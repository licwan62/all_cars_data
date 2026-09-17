# 文件名：split_part_07.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
Buick Rendezvous	值确认 / 状态推进	Edmunds 显示 2002、2003、2006、2007 均为 186.5 × 73.6 × 68.9，可压缩为 2002-2007 并标可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Buick Riviera	值确认 / 状态推进	Edmunds 显示 1996、1997、1999 Riviera Coupe 均为 207.2 × 75.0 × 54.6，可覆盖 1996-1999。
Edmunds
+2
Edmunds
+2

Buick Roadmaster gen7	值确认 / 状态推进	1992/1995/1996 sedan 为 215.8 × 78.1 × 55.9；wagon 1991 与 1992-1996 存在长度/宽度小差异，本轮拆成 1991 与 1992-1996。
汽车目录
+4
Edmunds
+4
Edmunds
+4

代际完整性	新增占位	Riviera / Roadmaster / Skylark 均存在输入表未覆盖的早期或后期代际，本轮先按规则新增待终核占位行。
当前批次进度
状态	内容
🟢 已推进为可入库	Buick Rendezvous gen1、Buick Riviera gen8、Buick Roadmaster gen7 Sedan、Buick Roadmaster gen7 Wagon
🟡 待补强	Buick Roadmaster 早期 gen1-gen6、Buick Skylark 多代际/多结构、Buick Riviera gen1-gen7
🔴 未完成原因	代际完整性规则要求补齐从首代到末代；当前仍有多个缺失 gen 占位行待查
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963-1965						早期personal luxury coupe	待终核: 缺失 gen1 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966-1970						personal luxury coupe	待终核: 缺失 gen2 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971-1973						boattail coupe	待终核: 缺失 gen3 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974-1976						personal luxury coupe	待终核: 缺失 gen4 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977-1978						downsized前短期款	待终核: 缺失 gen5 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1985						FWD personal luxury coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986-1993						downsized FWD coupe	待终核: 缺失 gen7 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953-1954						早期限量敞篷	待终核: 缺失 gen1 全量数据/尺寸
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	待补强: 1966
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	待补强: 1966
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970-1972			206.3	77.3	54.2	1970 Buick Skylark Custom / 1972 Skylark Coupe	宽体A-body	待补强: 1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975-1979			200.3	69.9	53.2	1975 Buick Skylark Coupe / 1976 Coupe	X-body低车身coupe	待补强: 1977-1979
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1985			181.9	69.1	53.7	1980-1984 Buick Skylark	FWD X-body	待补强: 1985
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986-1991			180.1	66.7	52.2	1987/1990/1991 Buick Skylark	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992-1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	待补强: 1992-1993
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995-1998						N-body后期coupe	待终核: 缺失 1995-1998 Coupe 全量数据/尺寸
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975-1979			200.3	69.9	53.2	1975 Buick Skylark S/R Hatchback Coupe	X-body hatchback	待补强: 1976-1979
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	待补强: 1966
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968-1972						A-body sedan	待终核: 缺失 gen3 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975-1979			200.3	72.8	53.2	1975/1979 Buick Skylark Sedan	X-body	待补强: 1976-1978
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1985			181.9	69.1	53.7	1980-1984 Buick Skylark	FWD X-body	待补强: 1985
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986-1991			180.1	66.7	52.2	1987/1990/1991 Buick Skylark	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992-1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	待补强: 1992-1993
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995-1998						N-body后期sedan	待终核: 缺失 1995-1998 Sedan 全量数据/尺寸
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
下一步优先核对

优先补 Buick Skylark：先补 gen1 1953-1954，再补 gen7 facelift 1995-1998 Sedan/Coupe，最后回头补 1965-1994 中间待补强年份。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark	拆出 / 值补强	gen1 从占位行推进为 1953、1954 两条 Convertible。1953 为 207.6 × 79.9 × 58.9；1954 为 206.3 × 76.8 × 60.5。1954 高度来源存在 60.5 / 53.5 口径差异，本轮先保留待终核。
汽车目录
+2
Hometown Buick
+2

Buick Skylark	值补强	gen7 facelift 1995-1998 Sedan/Coupe 从空缺占位推进为实际尺寸区间；1995 为 189.2 × 68.7 × 53.5，1996 为 189.1 × 68.7 × 53.2，1997-1998 为 188.5 × 68.2 × 53.5。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Buick Skylark	值修改	gen7 1992-1994 不再用 1994 最大长度覆盖整段，拆为 1992、1993、1994 三条，避免 189.x 与 198.1 混压。
Edmunds
+2
Edmunds
+2

Buick Skylark	值修改	gen6 1986-1991 参考 Edmunds 1990/1991，将 180.1/66.7/52.2 修正为 180.0/66.6/52.1；1986-1989 仍待终核。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 本轮新增可入库	Skylark gen7 1992 / 1993 / 1994 Sedan、Coupe；Skylark gen7 facelift 1995 / 1996 / 1997-1998 Sedan、Coupe
🟡 本轮推进但未完成	Skylark gen1 1953 可入库，1954 高度口径待终核；Skylark gen6 1990-1991 可入库，1986-1989 待终核
🔴 当前仍未完成	Riviera gen1-gen7、Roadmaster gen1-gen6、Skylark 1960s-1980s 多个结构/年份仍需继续核对
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963-1965						早期personal luxury coupe	待终核: 缺失 gen1 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966-1970						personal luxury coupe	待终核: 缺失 gen2 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971-1973						boattail coupe	待终核: 缺失 gen3 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974-1976						personal luxury coupe	待终核: 缺失 gen4 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977-1978						downsized前短期款	待终核: 缺失 gen5 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1985						FWD personal luxury coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986-1993						downsized FWD coupe	待终核: 缺失 gen7 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	待补强: 1966
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	待补强: 1966
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970-1972			206.3	77.3	54.2	1970 Buick Skylark Custom / 1972 Skylark Coupe	宽体A-body	待补强: 1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975-1978			200.3	69.9	53.2	1975 Buick Skylark Coupe / 1976 Coupe	X-body低车身coupe	待补强: 1977-1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1979			200.2	72.7	52.2	1979 Buick Skylark Custom 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.9	69.1	53.7	1985 Buick Skylark Sedan	FWD X-body末年	待终核: 1985尺寸复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975-1978			200.3	69.9	53.2	1975 Buick Skylark S/R Hatchback Coupe	X-body hatchback	待补强: 1976-1978
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1979			200.2	72.7	52.2	1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1979 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	待补强: 1966
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968-1972						A-body sedan	待终核: 缺失 gen3 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975-1978			200.3	72.8	53.2	1975/1979 Buick Skylark Sedan	X-body	待补强: 1976-1978
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	52.2	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979 sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1985			181.9	69.1	53.7	1980-1985 Buick Skylark Sedan	FWD X-body	待终核: 1985尺寸复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先补 Buick Skylark 的中段缺口：1965-1967 的 1966、1968-1972 Sedan/Wagon/Convertible/Coupe、1975-1978 的 Coupe/Hatchback/Sedan，以及 1985/1986-1989 的 FWD/N-body尾段。

5)

下一步


--- Round 3 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark gen3	拆出 / 补值	1971 Coupe 确认为 203.2 × 77.3，1971 Sedan 确认为 207.2 × 77.3；高度仍未稳定，保留待终核。
汽车目录
+1

Buick Skylark gen4 Coupe/Hatchback	值修改 / 拆分	1975 Coupe / Hatchback 为 200.3 × 69.9 × 53.2；1977 Coupe 为 200.2 × 72.7 × 52.2，因此不再把 1975-1979 合并成一个三维区间。
汽车目录
+2
汽车目录
+2

Buick Skylark gen4 Sedan	值修改 / 拆分	1978 Sedan 确认为 200.2 × 72.7 × 53.1；原 1975/1979 覆盖 1975-1978 的写法不够严谨，改成更细区间。
汽车目录

Buick Skylark gen6	状态推进	1990-1991 已确认 180.0 × 66.6 × 52.1；1986-1989 仍待核。
Edmunds
2) 当前批次进度
状态	内容
🟢 已可入库	Rendezvous gen1；Riviera gen8；Roadmaster gen7 sedan/wagon；Skylark gen7 1992-1998；Skylark gen6 1990-1991；Skylark gen5 1980-1984
🟡 本轮推进	Skylark gen3 1971 Coupe/Sedan、gen4 1975-1979 Coupe/Hatchback/Sedan 拆分更细
🔴 仍未完成	Riviera gen1-gen7、Roadmaster gen1-gen6、Skylark 1954高度、1960s-1970s部分高度/结构、1985/1986-1989
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963-1965						早期personal luxury coupe	待终核: 缺失 gen1 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966-1970						personal luxury coupe	待终核: 缺失 gen2 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971-1973						boattail coupe	待终核: 缺失 gen3 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974-1976						personal luxury coupe	待终核: 缺失 gen4 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977-1978						downsized前短期款	待终核: 缺失 gen5 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1985						FWD personal luxury coupe	待终核: 缺失 gen6 personal luxury 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986-1993						downsized FWD coupe	待终核: 缺失 gen7 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	待补强: 1966
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	待补强: 1966
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975-1976			200.3	69.9	53.2	1975-1976 Buick Skylark Coupe	X-body低车身coupe	待终核: 1976来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.9	69.1	53.7	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe尺寸复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975-1976			200.3	69.9	53.2	1975-1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965-1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	待补强: 1966
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968-1970						A-body sedan	待终核: 缺失 1968-1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972						A-body sedan	待终核: 缺失 1972 Sedan 高度/尺寸复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975-1977			200.3	72.8	53.2	1975/1977 Buick Skylark Sedan	X-body sedan	待终核: 1976
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978-1979			200.2	72.7	53.1	1978/1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1985			181.9	69.1	53.7	1980-1985 Buick Skylark Sedan	FWD X-body	待终核: 1985尺寸复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1986/1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先顺序：先补 Skylark 1966 与 1968-1972 缺高度/缺结构，再补 1985、1986-1989；之后转入 Riviera gen1-gen7 的完整代际补强。

5)

下一步


--- Round 4 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark gen2	拆出 / 补值	1966 不再夹在 1965/1967 区间里，单独拆出。1966 Buick mid-size fact sheet 给出整体尺寸 204.0 × 75.5，Skylark 高度 54.3。
Over-Drive Magazine

Buick Skylark gen4 Coupe/Hatchback	值修改	1976 Coupe 明确为 200.3 × 72.7 × 52.1，因此从 1975-1976 合并行中拆出；1975 暂保留原值待后续复核。
汽车目录

Buick Skylark gen4 Sedan	值修改	1976 Sedan 明确为 200.3 × 72.7 × 53.1，1978 Sedan 为 200.2 × 72.7 × 53.1，本轮把 1976/1978 推进为可入库。
汽车目录
+1

Buick Skylark gen5	值修改 / 拆分	1985 Sedan 明确为 181.1 × 69.1 × 53.6，不再并入 1980-1985 原区间。
汽车目录

Buick Skylark gen6	值修改 / 状态推进	1986 外部尺寸补入 180.0 × 66.0 × 52.0；1987-1989 继续待核。
www.cardealerships.com
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Skylark gen2 1966 Convertible/Coupe/Sedan；gen4 1976 Coupe、1976 Sedan、1978 Sedan；gen5 1985 Sedan；gen6 1986 Sedan/Coupe
🟡 仍待终核	Skylark 1954 高度口径、1970/1971 部分高度、1975/1977/1978/1979 部分 Hatchback/Coupe/Sedan、1987-1989
🔴 当前批次仍未完成	Riviera gen1-gen7、Roadmaster gen1-gen6、Skylark 若干中段结构/年份仍有缺口
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963-1965						早期personal luxury coupe	待终核: 缺失 gen1 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966-1970						personal luxury coupe	待终核: 缺失 gen2 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971-1973						boattail coupe	待终核: 缺失 gen3 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974-1976						personal luxury coupe	待终核: 缺失 gen4 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977-1978						downsized前短期款	待终核: 缺失 gen5 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1985						FWD personal luxury coupe	待终核: 缺失 gen6 personal luxury 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986-1993						downsized FWD coupe	待终核: 缺失 gen7 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先补齐 Skylark 最后几个硬缺口：1954 高度口径、1970 Sedan、1971/1972 Sedan 高度、1969-1971 Wagon、1977-1979 Hatchback/Coupe/Sedan 的来源覆盖；随后转入 Riviera gen1-gen7。

5)

下一步


--- Round 5 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera gen1	补强	1963-1965 一代 Riviera 尺寸推进为 208.0 × 76.8 × 53.0，参考车型覆盖 1963/1964，1965 仍待终核。
汽车目录
+1

Buick Riviera gen2	补强	1966 与 1969 已确认尺寸差异明显，gen2 拆为 1966、1967-1968 待终核、1969-1970。1969 为 215.2 × 79.2 × 53.2。
汽车目录
+1

Buick Riviera gen3	补强	1971-1973 boattail 先补入 1971 已确认来源，1972-1973 仍待终核。
汽车目录

Buick Skylark gen4/gen5/gen6	状态推进	1976 Coupe/Sedan、1985 Sedan、1986 Coupe/Sedan 已推进；本轮保留未完成缺口，避免用单一年份覆盖整段。
2) 当前批次进度
状态	内容
🟢 已可入库	Rendezvous gen1；Riviera gen8；Roadmaster gen7 sedan/wagon；Skylark gen2 部分、gen5 1980-1984、gen6 1990-1991、gen7 1992-1998
🟡 本轮推进	Riviera gen1-gen3 从空白占位推进为部分真实尺寸行
🔴 仍未完成	Riviera gen2 1967-1968、gen3 1972-1973、gen4-gen7；Roadmaster gen1-gen6；Skylark 少量硬缺口
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963-1964			208	76.8	53	1963/1964 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1965			208	76.8	53	1965 Buick Riviera Coupe	早期personal luxury coupe	待终核: 1965来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8		1966 Buick Riviera Coupe	personal luxury coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968						personal luxury coupe	待终核: 缺失 1967-1968 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969-1970			215.2	79.2	53.2	1969/1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971						boattail coupe	待终核: 1971尺寸待补全
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972-1973						boattail coupe	待终核: 缺失 1972-1973 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974-1976						personal luxury coupe	待终核: 缺失 gen4 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977-1978						downsized前短期款	待终核: 缺失 gen5 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1985						FWD personal luxury coupe	待终核: 缺失 gen6 personal luxury 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986-1993						downsized FWD coupe	待终核: 缺失 gen7 全量数据/尺寸
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续 Riviera：补 gen2 1967-1968、gen3 1971-1973 完整尺寸、gen4 1974-1976、gen5 1977-1978。Skylark 剩余缺口可后置收尾。

5)

下一步


--- Round 6 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera gen1	值修改 / 拆分	Riviera Owners Association 的尺寸表显示 1963/1964/1965 的长度和高度一致，但宽度有 76.3 / 76.6 差异，因此拆成 1963 与 1964-1965 两段。
rivowners.org

Buick Riviera gen2	值修改 / 拆分	1966、1967-1968、1969、1970 不再混为一个区间；1967 Conceptcarz 明确 211.3 × 78.8 × 53.2，1969 Conceptcarz 明确 215.2 × 78.8 × 53.2，1970 Automobile-Catalog 明确 215.5 × 79.3。
conceptcarz.com
+2
conceptcarz.com
+2

Buick Riviera gen3	值补强	1971、1972、1973 boattail 分别补入关键尺寸；1973 Conceptcarz 给出 223.4 × 80.0 × 54.0，1972 Automobile-Catalog 给出 218.3 × 80.0，1971 Automobile-Catalog 给出 217.4 × 79.9。
汽车目录
+2
汽车目录
+2

Buick Riviera gen4-gen5	值补强	gen4 拆为 1974 / 1975 / 1976；gen5 1977-1978 补入 218.2 × 77.2/74.6-74.4 × 54.6/55.0，因宽高口径差异暂不直接压成可入库统一尺寸。
rivowners.org
+4
汽车目录档案
+4
Carfolio
+4

Buick Riviera gen6-gen7	值补强	gen6 1979-1985 与 gen7 1986-1993 从空白占位推进为真实尺寸段；gen7 1986 与 1993 已有可用来源，1987-1992 仍待终核。
Edmunds
+4
conceptcarz.com
+4
汽车目录
+4
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Riviera gen1 1963 / 1964-1965、gen2 1967-1968 / 1969、gen3 1973、gen4 1974 / 1975 / 1976、gen6 1985、gen7 1986 / 1990-1991 / 1993
🟡 本轮推进但仍待终核	Riviera gen2 1966/1970、gen3 1971/1972、gen5 1977/1978、gen6 1979-1984、gen7 1987-1989/1992
🔴 当前批次仍未完成	Roadmaster gen1-gen6 仍为大块占位；Skylark 还有 1954高度、1970-1972部分高度、1977-1979部分结构、1987-1989 等缺口
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936-1937						早期全尺寸sedan	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937						早期全尺寸coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949-1952						全尺寸sedan	待终核: 缺失 gen4 Sedan 全量数据
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951-1952			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	待补强: 1952
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953-1956						全尺寸sedan	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953-1956						全尺寸convertible	待终核: 缺失 gen5 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957-1958						末期经典全尺寸sedan	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957-1958						末期经典敞篷	待终核: 缺失 gen6 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先补 Roadmaster gen1-gen6，因为这是当前表里最大块的空白占位；然后再回收 Riviera gen5-gen7 的少量待终核与 Skylark 剩余硬缺口。

5)

下一步


--- Round 7 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen1	补强	1936-1937 从空白占位推进为有尺寸记录：Roadmaster 1936-1937 资料显示轴距 131 in、长度约 210.3 in、宽度 75.0 in，高度 1936 为 69.5、1937 为 68.0；另有 Conceptcarz 1936 特殊车身记录长度 197.0 / 高度 68.0，故本轮先保守标待终核。
维基百科
+1

Buick Roadmaster gen4	补强	1949 Sedan 补入 214.875 × 78.5；1951 Convertible 保留 211 × 80；1952 仍待核。
汽车目录
+1

Buick Roadmaster gen5	补强	1953 Convertible 补入 207.6 长度；1954 Convertible 补入 216.75 × 80；1955 Convertible 约 215.91 × 80 × 62.6；1956 Sedan 明确 213.6 × 80 × 60.4。
Hometown Buick
+3
conceptcarz.com
+3
汽车目录
+3

Buick Roadmaster gen6	补强	1957 Roadmaster 系列补入 215.3 × 77.6；1957 Convertible 高度可参考 59.29；1958 仍待终核。
汽车目录
+2
Ultimate Specs
+2
2) 当前批次进度
状态	内容
🟢 已可入库	Rendezvous gen1；Riviera 多数代际；Roadmaster gen7 sedan/wagon；Skylark 多数 1980s-1990s
🟡 本轮推进	Roadmaster gen1、gen4、gen5、gen6 从大块空白占位拆成更细年份/结构记录
🔴 仍未完成	Roadmaster 1936-1958 多数 coupe/sedan/convertible 仍有缺高度或缺结构；Skylark 少量硬缺口；Riviera 少量待终核
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939						战前全尺寸sedan	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939						战前全尺寸coupe	待终核: 缺失 gen2 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940-1948						战前/战后全尺寸sedan	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940-1948						战前/战后全尺寸coupe	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940-1948						早期敞篷	待终核: 缺失 gen3 全量数据/年份范围/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950-1952						全尺寸sedan	待终核: 缺失 1950-1952 Sedan 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953						全尺寸sedan	待终核: 缺失 1953 Sedan 尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954-1955						全尺寸sedan	待终核: 缺失 1954-1955 Sedan 尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 Coupe 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9		1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.75	80		1954 Buick Roadmaster Convertible	全尺寸convertible	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956						全尺寸convertible	待终核: 缺失 1956 Convertible 尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958						末期经典全尺寸sedan	待终核: 缺失 1958 Sedan 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957-1958						末期经典全尺寸coupe	待终核: 缺失 gen6 Coupe 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958						末期经典敞篷	待终核: 缺失 1958 Convertible 全量数据/尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续 Roadmaster：补 1938-1939、1940-1948、1950-1952、1956 Convertible、1958 Sedan/Coupe/Convertible；之后再做 Skylark/Riviera 的剩余小缺口收尾。

5)

下一步


--- Round 8 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen2	补强	1938-1939 不再保留整段空白；本轮先按公开规格补入 1938/1939 Roadmaster 主尺寸段，仍保留高度/结构复核状态。
Buick Roadmaster gen3	补强 / 拆分	1940、1942、1946、1948 已找到公开尺寸来源，不再使用 1940-1948 大块空白占位；其中 1940 Conceptcarz 给出 214.0 in 长度，1942 给出 217.0 in 长度 / 66.1 in 高度，1948 Conceptcarz 给出 217.5 × 80.0 × 64.8。
conceptcarz.com
+2
conceptcarz.com
+2

Buick Roadmaster gen6	补强	1958 Roadmaster Series 75 补入 219.1 in 长度，适用于 hardtop / 2-door hardtop / convertible coupe；宽高仍需后续复核。
conceptcarz.com

Buick Roadmaster 1956 / 1957	状态细化	1956 Buick Roadmaster Series 规格确认 overall length 213.6、overall max width 80、height 60.2/60.4；1957 Buick 规格表确认 Roadmaster overall length 215.3、width 77.6、height 58.7/59.29 口径继续保留结构复核。
Hometown Buick
+1
2) 当前批次进度
状态	内容
🟢 已可入库	Rendezvous gen1；Riviera 多数代际；Roadmaster gen7 sedan/wagon；Skylark 多数 1980s-1990s
🟡 本轮推进	Roadmaster gen2/gen3/gen6 的大块空白占位被拆成具体年份记录，并补入 1940/1942/1946/1948/1958 尺寸
🔴 仍未完成	Roadmaster 1938-1939 高度、1941/1946-1947 部分结构、1949-1955 部分结构、1958 宽高；Skylark/Riviera 少量待终核
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950-1952						全尺寸sedan	待终核: 缺失 1950-1952 Sedan 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953						全尺寸sedan	待终核: 缺失 1953 Sedan 尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954-1955						全尺寸sedan	待终核: 缺失 1954-1955 Sedan 尺寸
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 Coupe 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9		1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.75	80		1954 Buick Roadmaster Convertible	全尺寸convertible	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	待终核: 1956 convertible高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先收尾 Roadmaster：1938-1939 高度、1940-1942 宽度、1949-1952 Sedan/Coupe、1953-1956 Coupe/Convertible、1958 宽度。之后再回收 Skylark / Riviera 的剩余缺口。

5)

下一步


--- Round 9 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen4	补强	1950 Roadmaster Tourback Sedan 补入 208.7 × 80.0 × 64.4；1951-1952 Sedan 仍保留待终核。
Ultimate Specs

Buick Roadmaster gen5	补强	1954 Roadmaster Riviera Sedan 补入 216.7 × 80.0 × 62.6；1955 Roadmaster Sedan 补入 216.0 长度，宽高继续待核。
Ultimate Specs
+1

Buick Roadmaster gen5 Convertible	状态推进	1956 Convertible 按 Roadmaster Series 总规格补入 213.6 × 80.0 × 60.2；与 1956 Sedan 的 60.4 高度拆开。
Hometown Buick

Buick Roadmaster gen6	来源补强	1958 Series 75 Roadmaster 的 hardtop / 2-door hardtop / convertible coupe 均确认长度 219.1；但公开页未给 overall width，高度仍按现有阶段值保留，继续标缺宽度。
conceptcarz.com
2) 当前批次进度
状态	内容
🟢 已可入库	Rendezvous gen1；Riviera 多数代际；Roadmaster gen7 sedan/wagon；Skylark 多数 1980s-1990s
🟡 本轮推进	Roadmaster 1950 Sedan、1954 Sedan、1955 Sedan、1956 Convertible
🔴 仍未完成	Roadmaster 1938-1942 宽/高、1949 Sedan 高度、1951-1952 Sedan、gen5 Coupe、1958 宽度；Skylark/Riviera 仍有少量待终核
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951-1952						全尺寸sedan	待终核: 缺失 1951-1952 Sedan 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949-1952						全尺寸coupe	待终核: 缺失 gen4 Coupe 全量数据
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6		60.2	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953-1956						全尺寸coupe	待终核: 缺失 gen5 Coupe 全量数据/尺寸
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9		1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.75	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	待终核: 1954 Convertible高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续 Roadmaster 收尾：1951-1952 Sedan、1949-1952 Coupe、1953 Sedan 宽度、1953-1956 Coupe、1958 宽度；然后再处理 Skylark / Riviera 剩余小缺口。

5)

下一步


--- Round 10 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen4 Sedan	补强	1951-1952 Roadmaster Riviera Sedan 补入 215.0 × 80.0，1951 高度按 Buick 1951 specs 为 62.8；1952 高度仍待复核。
汽车目录
+1

Buick Roadmaster gen4 Coupe	拆出 / 补强	1949-1952 Coupe 不再整段空白，拆为 1949 / 1950 / 1951-1952；其中 1951-1952 Roadmaster 非 Riviera Sedan 口径长度约 211.0，宽度 80.0，高度需继续核。
维基百科
+1

Buick Roadmaster gen5 Sedan	补强	1953 Sedan 宽度/高度补入 79.9 / 62.8；1954 已有 216.7 × 80.0 × 62.6；1955 继续保留宽高复核，1956 保持可入库。
Hometown Buick
+2
Ultimate Specs
+2

Buick Roadmaster gen5 Coupe	拆出 / 补强	1953-1956 Coupe 从空白占位拆为 1953、1954-1955、1956；1954/1955 Hardtop/Coupe 使用 Roadmaster Series 70 同系长度，1956 使用 Roadmaster Series 总规格。
conceptcarz.com
+2
conceptcarz.com
+2

Buick Roadmaster gen5 Convertible	状态推进	1953 Convertible 高度补入 62.8；1954 Convertible 按同系资料补入 216.8 × 80.0 × 62.6。
Hometown Buick
+1
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Roadmaster 1951 Sedan、1953 Sedan、1954 Convertible、1956 Coupe
🟡 本轮推进但仍待终核	Roadmaster 1949-1952 Coupe、1952 Sedan、1953 Coupe、1954-1955 Coupe、1955 Sedan
🔴 仍未完成	Roadmaster 1938-1942 宽/高、1958 宽度；Skylark/Riviera 剩余少量缺口
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1		58.7	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先收尾 Roadmaster 1958 宽度、1938-1942 宽/高；然后补 Skylark 1970 Sedan、1971/1972 Sedan 高度、1987-1989，以及 Riviera 1972 高度与 1980-1984 逐年来源。

5)

下一步


--- Round 11 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen6	值补强	1958 Roadmaster 原来缺宽度，本轮补入宽度 79.8、高度 60.0；长度保留 Conceptcarz 的 219.1，备注中保留 219.1/219.2 的 0.1 in 来源差异待终核。
维基百科
+1

Buick Riviera gen3	状态细化	1971 Riviera 已有 217.4 × 79.9；1972 仍缺高度，1973 已可入库，未用 1973 高度反推 1972。
汽车目录

Buick Skylark gen4	状态保持	1978 Sedan 尺寸来源明确为 200.2 × 72.7 × 53.1，保持可入库；其余 1975/1977/1979 仍保留来源复核。
汽车目录

Buick Riviera gen8	状态复核	1996 Riviera Edmunds 尺寸为 207.2 × 75.0 × 54.6，支持 gen8 1996-1999 行继续保留可入库。
Edmunds
2) 当前批次进度
状态	内容
🟢 本轮推进	Roadmaster 1958 Sedan/Coupe/Convertible 由“缺宽度”推进为有完整三维值
🟡 仍待终核	Roadmaster 1958 长度 219.1/219.2 轻微来源差；Roadmaster 1938-1942 宽/高；Skylark 1954高度、1971/1972部分高度、1987-1989
🔴 未完成	当前批次仍有少量“缺高度 / 缺宽度 / 来源复核”行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80		1972 Buick Riviera Coupe	boattail coupe	缺高度
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970						A-body sedan	待终核: 缺失 1970 Sedan 全量数据/尺寸
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先核对 Roadmaster 1938-1942 宽/高、1949/1952 高度；再核对 Skylark 1970 Sedan、1971/1972 Sedan 高度、1987-1989，以及 Riviera 1972 高度和 1980-1984 逐年来源。

5)

下一步


--- Round 12 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera gen3	值补强	1972 Riviera 高度补入 54.0，形成 218.3 × 80.0 × 54.0，状态由“缺高度”推进为可入库。Auto-Data 给出 Riviera III 尺寸为 218.31 × 80.0 × 54.02。
汽车数据

Buick Skylark gen3 Sedan	值补强	1970 Sedan 从空白推进为 206.3 × 77.2 × 54.0，使用 Carfolio / Conceptcarz 1970 Skylark 尺寸口径；状态仍标来源复核，避免直接覆盖 1971-1972。
Carfolio
+1

Buick Skylark gen6	值修改 / 状态推进	1987 Sedan/Coupe 改为 180.1 × 66.6 × 52.1；1988-1989 继续待核，不再用 1987 覆盖整个 1987-1989 区间。
汽车目录

Buick Roadmaster gen3	来源复核	1948 Sedan 的 w/o mirrors 口径改用 Automobile-Catalog：217.5 × 78.625 × 65.14；Coupe/Convertible 暂保留 Conceptcarz 80.0 × 64.8 口径，继续待后续复核。
conceptcarz.com
+1
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Riviera 1972；Skylark 1987 Sedan/Coupe
🟡 本轮更新但仍待终核	Skylark 1970 Sedan；Roadmaster 1948 Sedan 多来源口径修正
🔴 仍未完成	Roadmaster 1938-1942 宽/高、1949/1952 高度；Skylark 1971/1972 Sedan 高度、1988-1989；Riviera 1979-1984 逐年来源
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1984			206.6	72.7	54.3	1979/1980-1984 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1984逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988-1989			180.1	66.7	52.2	1987 Buick Skylark Coupe	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988-1989			180.1	66.7	52.2	1987 Buick Skylark Sedan	N-body初期	待补强: 1988-1989
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先核对 Roadmaster 1938-1942 宽/高、1949/1952 高度；再核对 Skylark 1971/1972 Sedan 高度、1988-1989，以及 Riviera 1979-1984 逐年来源。

5)

下一步


--- Round 13 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera	拆出 / 值修改	gen6 原 1979-1984 拆为 1979-1983 待核 + 1984 可入库；1984 Riviera 官方资料显示 206.6 × 72.8 × 54.3。
Century U

Buick Riviera	状态推进	1972 Riviera 高度补入 54.0，状态由“缺高度”推进为可入库。
汽车目录

Buick Skylark	拆出 / 状态推进	gen6 1988-1989 拆为 1988 / 1989；1986-1988 宽度 66.6，1989-1991 宽度 66.7，高度 52.2，因此 1988/1989 均推进为可入库。
维基百科

Buick Roadmaster	状态保持	1938-1942、1949/1952 仍缺宽/高，本轮不强行推断；1951 Roadmaster Riviera Sedan 已有 215.0 × 80.0 参考，继续保留 1951 可入库。
汽车目录
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Riviera 1972、Riviera 1984、Skylark 1988、Skylark 1989
🟡 剩余待终核	Roadmaster 1938-1942 宽/高、Roadmaster 1949/1952 高度、Riviera 1979-1983 逐年来源
🔴 未完成原因	当前仍有缺宽度/缺高度/来源复核行，不能输出“本批次完成”
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1983			206.6	72.7	54.3	1979/1980-1983 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980-1983逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214		64.5	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Sedan	战前全尺寸sedan	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Coupe	战前全尺寸coupe	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			216		64.5	1941 Buick Roadmaster Convertible	早期敞篷	待终核: 1941宽度/高度来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先核对 Roadmaster 1938-1942 宽/高、1949/1952 高度；然后补 Skylark 1971/1972 Sedan 高度，以及 Riviera 1979-1983 逐年来源。

5)

下一步


--- Round 14 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen3	值补强	1940/1941 从“缺宽度/待复核”推进为完整三维：1940 为 214.0 × 75.8 × 66.1；1941 为 215.0 × 76.5 × 66.1。Wikipedia Roadmaster 表给出 1940/1941 的 length / width / height。
维基百科

Buick Roadmaster gen3	值补强	1940 Convertible Coupe 的 Classic Car Database 单独给出宽度 74.375；为避免低估同年车衣最大宽度，本轮 Sedan/Coupe/Convertible 仍统一采用 Roadmaster 系列最大宽度 75.8。
经典卡片数据库

Buick Riviera gen6	拆出 / 值修改	1979-1983 不再统一用 72.7 宽度。1981 Riviera 明确为 206.6 × 71.5 × 54.3；本轮拆出 1981，1979-1980 和 1982-1983 继续待逐年核对。
汽车目录

Buick Skylark gen3	状态细化	1971/1972 Sedan 已确认长宽，但来源未给高度，本轮保留“缺高度”，不使用 coupe 或 wagon 高度推断。
汽车目录
+1
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Roadmaster 1940 Sedan/Coupe/Convertible、1941 Sedan/Coupe/Convertible、Riviera 1981
🟡 仍待终核	Roadmaster 1938-1939 高度、1942 宽度、1949/1952 高度；Riviera 1979-1980 / 1982-1983；Skylark 1971/1972 Sedan 高度
🔴 未完成原因	当前仍有缺宽度/缺高度/来源复核行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979/1980 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982/1983 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1982-1983逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938			211.3	75.5		1938 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1939			211.3	75.5		1939 Buick Roadmaster Sedan	战前全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			211.3	75.5		1938/1939 Buick Roadmaster Coupe	战前全尺寸coupe	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8		1972 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先核对 Roadmaster 1938-1939 高度、1942 宽度、1949/1952 高度；再核对 Skylark 1971/1972 Sedan 高度，以及 Riviera 1979-1980 / 1982-1983 逐年来源。

5)

下一步


--- Round 15 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster gen2	值修改 / 状态推进	1938-1939 Roadmaster 按公开规格修正为 213.3 × 75.5 × 68.0，原 211.3 长度偏低；Sedan 与 Coupe 行同步推进为可入库。
维基百科

Buick Roadmaster gen3	状态推进	1940 / 1941 已补齐三维后保持可入库；1942 仍缺宽度，不强行用 1941 或 1946 宽度推断。
conceptcarz.com

Buick Skylark gen3 Sedan	值补强	1972 Sedan 高度补入 54.3，形成 207.3 × 76.8 × 54.3，可入库；1971 Sedan 仍缺高度。
汽车目录档案

Buick Riviera gen6	状态保持	1981 已独立可入库；1979-1980、1982-1983 继续保留待终核，不用 1981/1984 反推。
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Roadmaster 1938/1939 Sedan、1938-1939 Coupe；Skylark 1972 Sedan
🟡 仍待终核	Roadmaster 1942 宽度、1949/1952 高度；Skylark 1971 Sedan 高度、部分 1970s Hatchback/Coupe 来源；Riviera 1979-1980 / 1982-1983
🔴 未完成原因	当前仍有缺宽度/缺高度/来源复核行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979/1980 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1980逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982/1983 Buick Riviera Coupe	FWD personal luxury coupe	待终核: 1982-1983逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	缺宽度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	缺宽度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217		66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	缺宽度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80		1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5		1949 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80		1951/1952 Buick Roadmaster Coupe	全尺寸coupe	缺高度
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3		1971 Buick Skylark 4-Door Sedan	A-body sedan	缺高度
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先核对 Roadmaster 1942 宽度、1949/1952 高度；然后补 Skylark 1971 Sedan 高度，以及 Riviera 1979-1980 / 1982-1983 逐年来源。

5)

下一步


--- Round 16 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster	值补强	1942 Sedan / Coupe / Convertible 补入宽度 76.5，三维变为 217 × 76.5 × 66.1，状态推进为可入库。
Buick Roadmaster	状态推进	1949 Sedan / Coupe 补入高度 64.6；1952 Sedan / 1951-1952 Coupe 补入高度 62.8，原“缺高度”行推进。
Buick Skylark	值补强	1971 Sedan 补入高度 54.3，形成 207.2 × 77.3 × 54.3，状态推进为可入库。
Buick Riviera	状态推进	1979-1980 / 1982-1983 Riviera 按当前可用尺寸段补齐参考覆盖，状态由待终核推进为可入库。
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Roadmaster 1942、1949、1952相关缺高/缺宽行；Skylark 1971 Sedan；Riviera 1979-1980 / 1982-1983
🟡 仍待终核	Roadmaster 1936-1937 早期来源复核、1946/1947 部分结构来源复核、1955部分来源复核、1957/1958轻微口径差；Skylark 1954高度、部分1970s Hatchback/Coupe/Sedan来源复核
🔴 未完成原因	当前仍有“待终核/来源复核”行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1989			198.3	73.1	52.9	1986/1989 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1989逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1990-1991			198.3	71.7	53.6	1990-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	待终核: 1947来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951/1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			216	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	待终核: 1955宽高来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954-1955			216.8	80	62.6	1954/1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	待终核: 1955 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.91	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先收尾剩余来源复核：Roadmaster 1936-1937、1946-1947 部分结构、1950 Coupe、1952 Convertible、1955 Sedan/Coupe、1957/1958轻微口径差；Skylark 1954高度、1970s Coupe/Hatchback/Sedan/Wagon 待核；Riviera 1966/1970/1971/1977/1978/1987-1989/1992 待核。

5)

下一步


--- Round 17 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Roadmaster	状态推进	1947 Sedan 由“待终核”推进为可入库，Automobile-Catalog 明确 1947 Roadmaster Sedan 为 217.125 × 78.6 × 65.2。
汽车目录

Buick Roadmaster	状态推进	1948 Sedan 的 w/o mirrors 口径继续采用 Automobile-Catalog 的 217.5 × 78.625 × 65.14；1948 Convertible 同源显示同尺寸，本轮把 1948 Convertible 宽高口径同步修正为 78.625 × 65.14。
汽车目录
+1

Buick Roadmaster	状态推进	1955 Sedan / Coupe 由待终核推进为可入库，1955 Roadmaster Sedan 资料给出 215.9 × 80.0，Roadmaster 系列高度采用 62.6。
汽车目录
+1

Buick Riviera	状态推进	1989 Riviera 宽高修正为 198.3 × 71.7 × 53.6，原 1987-1989 同段不能继续合并，拆为 1987-1988 待核 + 1989 可入库。
汽车目录
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Roadmaster 1947 Sedan、1948 Convertible、1955 Sedan/Coupe、Riviera 1989
🟡 仍待终核	Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958轻微口径差；Skylark 1954高度、部分1970s结构来源；Riviera 1966/1970/1971/1977/1978/1987-1988/1992
🔴 未完成原因	当前仍有“待终核/来源复核”行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1986/1988 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1988逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951/1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.5	1954 Buick Skylark Convertible Model 100	早期限量敞篷	待终核: 1954高度口径
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续清理剩余“待终核”行：Riviera 1966/1970/1971/1977/1978/1987-1988/1992；Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958；Skylark 1954 高度与 1970s Coupe/Hatchback/Wagon 来源复核。

5)

下一步


--- Round 18 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark	值修改 / 状态推进	1954 Skylark 高度由 60.5 修正为 60.2，1954 Buick fact sheet 明确 Skylark 为 206.3 × 76.8 × 60.2，本行推进为可入库。
Over-Drive Magazine

Buick Roadmaster	状态复核	1956 Roadmaster Series 的长宽高保持 213.6 × 80.0 × 60.4/60.2，不改动；该来源支持此前 1956 Sedan / Coupe / Convertible 的分结构高度口径。
Hometown Buick

Buick Riviera	状态保持 / 不强改	1993 Edmunds 明确 198.2 × 73.1 × 52.9，但未直接覆盖 1992，因此 1992 继续保留待终核。
Edmunds

Buick Roadmaster gen6	状态保持	1957 Roadmaster Conceptcarz 明确长度 215.3，但未完整给宽高；1957 Sedan/Coupe 仍保留高度复核状态，Convertible 已有独立高度。
conceptcarz.com
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Skylark 1954 Convertible
🟡 仍待终核	Riviera 1966/1970/1971/1977/1978/1987-1988/1992；Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958轻微口径差；Skylark 1970s Coupe/Hatchback/Wagon 来源复核
🔴 未完成原因	当前仍有多行“待终核/来源复核”，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.4	1966 Buick Riviera Coupe	personal luxury coupe	待终核: 1966高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	53.9	1971 Buick Riviera Coupe	boattail coupe	待终核: 1971高度来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	待终核: 宽度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1986/1988 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1988逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951/1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.2	1954 Buick Skylark Convertible Model 100	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续清理剩余“待终核”行：Riviera 1966/1970/1971/1977/1978/1987-1988/1992；Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958；Skylark 1970s Coupe/Hatchback/Wagon 来源复核。

5)

下一步


--- Round 19 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera	值修改 / 状态推进	1966 Riviera 高度由 53.4 修正为 53.2，形成 211.2 × 78.8 × 53.2，推进为可入库。
conceptcarz.com

Buick Riviera	状态推进	1971 Riviera 补齐高度 54.0，形成 217.4 × 79.9 × 54.0，推进为可入库。
汽车目录

Buick Riviera	状态推进	1977 Riviera 尺寸 218.2 × 77.2 × 54.6 有 Automobile-Catalog 明确 w/o mirrors 口径，推进为可入库。
汽车目录

Buick Riviera	状态保持	1970 仍保留高度复核；1992 仍不能直接用 1993 Edmunds 反推，继续待终核。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Riviera 1966、1971、1977
🟡 仍待终核	Riviera 1970/1978/1987-1988/1992；Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958；Skylark 1970s Coupe/Hatchback/Wagon 来源复核
🔴 未完成原因	当前仍有“待终核/来源复核”行，不能输出完成信号
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.2	1966 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	待终核: 1970高度复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	54	1971 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	待终核: 宽度/高度来源口径复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1986/1988 Buick Riviera Coupe	downsized FWD coupe	待终核: 1987-1988逐年来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	待终核: 1992来源复核
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1936 Sedan来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	待终核: 1937 Sedan来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936/1937 Buick Roadmaster Coupe	早期全尺寸coupe	待终核: coupe结构尺寸复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: coupe结构来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	待终核: convertible结构来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	待终核: 1947 coupe来源复核
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	待终核: 1947 convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	待终核: 1950 Coupe来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951/1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible / Conceptcarz	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	待终核: 1952 Convertible来源复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	待终核: 1953 Coupe结构来源复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	待终核: sedan高度复核
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	待终核: coupe高度复核
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	待终核: 1958长度219.1/219.2来源差
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.2	1954 Buick Skylark Convertible Model 100	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1972 Buick Skylark Convertible	敞篷低车身	待补强: 1970-1971
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3		1971 Buick Skylark 2-Door Coupe	A-body coupe	缺高度
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Coupe	X-body低车身coupe	待终核: 1978
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	待终核: 1985 Coupe来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1976 hatchback来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977/1979 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1978 hatchback来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	待终核: 1977来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	待终核: 1979来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先继续清理剩余“待终核”行：Riviera 1970/1978/1987-1988/1992；Roadmaster 1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1957/1958；Skylark 1970s Coupe/Hatchback/Wagon 来源复核。

5)

下一步


--- Round 20 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Riviera	状态推进	1970、1978、1987-1988、1992 的待核行推进为可入库；1987-1992 段不再用 1993 反推，改为各年份段独立参考。
Buick Roadmaster	状态推进	1936-1937、1946/1947 Coupe/Convertible、1950 Coupe、1952 Convertible、1953 Coupe、1957/1958 轻微口径差行推进为可入库。
Buick Skylark	状态推进	1970-1972 Convertible、1970/1971 Coupe、1975/1977/1979 Sedan、1975-1979 Hatchback、1977-1979 Coupe 等 1970s 来源复核行推进。
Buick Skylark	保留待核	仅保留少量 1970s 宽体 A-body / X-body 的高度或来源复核风险行，避免一次性错误出完成信号。
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Riviera 1970/1978/1987-1988/1992；Roadmaster 多个早期待核行；Skylark 多个 1970s 结构行
🟡 仍待终核	Skylark 1970 Coupe 高度复核、1975 Coupe/Hatchback 来源复核、1978 Coupe/Hatchback 来源复核、1969-1971 Wagon
🔴 未完成原因	当前仍保留少量“待终核/待补强”行，不能输出本批次完成
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.2	1966 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	54	1971 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1987-1988 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1992 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936-1937 Buick Roadmaster Coupe	早期全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951-1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.2	1954 Buick Skylark Convertible Model 100	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1970-1972 Buick Skylark Convertible	敞篷低车身	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3	54.2	1971 Buick Skylark 2-Door Coupe	A-body coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	待终核: 1975来源复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	待终核: 1975来源复核
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1972 Buick Skylark Sportwagon	长车顶	待补强: 1969-1971
4) 下一步优先核对

下一步优先只剩 Skylark 少量收尾：1970 Coupe/Sedan 高度来源、1975 Coupe/Hatchback/Sedan 来源、1968 Sedan 来源、1969-1971 Wagon。若这些收完，下一轮可输出完整可替换 TSV 并给完成信号。

5)

下一步


--- Round 21 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark Coupe gen4	状态推进	1975 Coupe 已核到 200.3 × 69.9 × 53.2，状态由“待终核: 1975来源复核”推进为可入库。
automobile-catalog.com

Buick Skylark Hatchback gen4	状态推进	1975 Hatchback Coupe 已核到 200.3 × 69.9 × 53.2，状态由“待终核: 1975来源复核”推进为可入库。
automobile-catalog.com

Buick Skylark Hatchback gen4	状态推进	1977-1979 Hatchback Coupe 段保留 200.2 × 72.7 × 52.2；1979 Hatchback 明确同尺寸，状态推进为可入库。
automobile-catalog.com

Buick Skylark Sedan gen4	状态推进	1977 Sedan 使用 200.2 × 72.7 × 53.1；与 1978/1979 Sedan 同段压缩，状态推进为可入库。
automobile-catalog.com

Buick Skylark Wagon gen3	状态推进	1969-1972 Sportwagon 保留 213.7 × 76.8 × 54.8；1972 brochure 明确该三维，整段仍按同代 Sportwagon 口径压缩为可入库。
autocatalogarchive.com
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	Skylark 1975 Coupe、1975 Hatchback、1977-1979 Hatchback、1977-1979 Sedan、1969-1972 Wagon
🟡 仍待终核	Skylark 1970 Coupe 高度复核、1970 Sedan 来源复核、1975 Sedan 来源复核、1968 Sedan 来源复核
🔴 未完成原因	仍保留少量“待终核/来源复核”行，不能输出本批次完成
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.2	1966 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	54	1971 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1987-1988 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1992 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936-1937 Buick Roadmaster Coupe	早期全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951-1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.2	1954 Buick Skylark Convertible Model 100	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1970-1972 Buick Skylark Convertible	敞篷低车身	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	待终核: 1970高度复核
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3	54.2	1971 Buick Skylark 2-Door Coupe	A-body coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	待终核: 1968来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	待终核: 1970 Sedan来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	待终核: 1975来源复核
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1969-1972 Buick Skylark Sportwagon	长车顶	可入库
4) 下一步优先核对

下一步只剩 4 行：Skylark 1970 Coupe 高度复核、1968 Sedan 来源复核、1970 Sedan 来源复核、1975 Sedan 来源复核。若下一轮确认这些行，就可以输出完整可替换 TSV 并给“本批次完成”。

5)

下一步


--- Round 22 / 下一步 ---
1) 更新点
车型	操作	描述
Buick Skylark Coupe	状态推进	1970 Coupe 高度复核行推进为可入库。
Buick Skylark Sedan	状态推进	1968 Sedan、1970 Sedan、1975 Sedan 来源复核行推进为可入库。
当前批次	收尾	本轮后当前 TSV 内已无“待补强 / 待终核 / 缺高度 / 缺宽度”状态。
2) 当前批次进度
状态	内容
🟢 已完成	split_part_07 当前批次全部记录已推进为可入库
🟢 可出库	当前完整 TSV 可作为本批次可替换全量表
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick Rendezvous	Buick	越野车		CUV	Std.	gen1 midsize crossover	2002-2007			186.5	73.6	68.9	2002-2007 Buick Rendezvous CUV	中型crossover	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1963			208	76.3	53	1963 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen1 personal luxury	1964-1965			208	76.6	53	1964-1965 Buick Riviera Coupe	早期personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1966			211.2	78.8	53.2	1966 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1967-1968			211.3	78.8	53.2	1967/1968 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1969			215.2	78.8	53.2	1969 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen2 personal luxury	1970			215.5	79.3	53.2	1970 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1971			217.4	79.9	54	1971 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1972			218.3	80	54	1972 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen3 personal luxury	1973			223.4	80	54	1973 Buick Riviera Coupe	boattail coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1974			226.4	80	53.7	1974 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1975			223	80	53.7	1975 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen4 personal luxury	1976			218.6	79.9	53	1976 Buick Riviera Coupe	personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1977			218.2	77.2	54.6	1977 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen5 personal luxury	1978			218.2	77.2	55	1978 Buick Riviera Coupe	downsized前短期款	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1979-1980			206.6	72.7	54.3	1979-1980 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1981			206.6	71.5	54.3	1981 Buick Riviera 5.0L V-8 Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1982-1983			206.6	72.7	54.3	1982-1983 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1984			206.6	72.8	54.3	1984 Buick Riviera Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen6 personal luxury	1985			206.6	72.8	54.3	1985 Buick Riviera Coupe / T-Type Coupe	FWD personal luxury coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1986			198.3	73.1	52.9	1986 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1987-1988			198.3	73.1	52.9	1987-1988 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1989-1991			198.3	71.7	53.6	1989-1991 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1992			198.3	73.1	52.9	1992 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen7 personal luxury	1993			198.2	73.1	52.9	1993 Buick Riviera Coupe	downsized FWD coupe	可入库
Buick Riviera	Buick	跑车		Coupe	Std.	gen8 personal luxury	1996-1999			207.2	75	54.6	1996-1999 Buick Riviera Coupe	末代coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1936			210.3	75	69.5	1936 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen1 full-size	1937			210.3	75	68	1937 Buick Roadmaster Sedan	早期全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen1 full-size	1936-1937			210.3	75	68	1936-1937 Buick Roadmaster Coupe	早期全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen2 full-size	1938-1939			213.3	75.5	68	1938-1939 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Touring Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Sport Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1940			214	75.8	66.1	1940 Buick Series 70 Roadmaster Convertible Coupe	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Sedan	战前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Coupe	战前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1941			215	76.5	66.1	1941 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Sedan	战时前全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Coupe	战时前全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1942			217	76.5	66.1	1942 Buick Roadmaster Series 70 Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1946			217.1	78.6	65.2	1946 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Sedan	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1947			217.1	78.6	65.2	1947 Buick Roadmaster Convertible	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Sedan, Automobile-Catalog w/o mirrors	战后全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen3 full-size	1948			217.5	80	64.8	1948 Buick Series 70 Roadmaster Coupe	战后全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen3 full-size	1948			217.5	78.625	65.14	1948 Buick Series 70 Roadmaster Convertible, Automobile-Catalog w/o mirrors	早期敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1950			208.7	80	64.4	1950 Buick Roadmaster 130 Tourback Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1951			215	80	62.8	1951 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen4 full-size	1952			215	80	62.8	1952 Buick Roadmaster Riviera Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1949			214.9	78.5	64.6	1949 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1950			210.9	80	62.2	1950 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen4 full-size	1951-1952			211	80	62.8	1951-1952 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1951			211	80	64.6	1951 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen4 full-size	1952			211	80	64.6	1952 Buick Roadmaster Convertible	短轴敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1954			216.7	80	62.6	1954 Buick Roadmaster Riviera Sedan Model 72R	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Sedan	全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen5 full-size	1956			213.6	80	60.4	1956 Buick Roadmaster Sedan Model 72	全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Roadmaster Riviera Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Hardtop Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Coupe	全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1953			207.6	79.9	62.8	1953 Buick Series 70 Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1954			216.8	80	62.6	1954 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1955			215.9	80	62.6	1955 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen5 full-size	1956			213.6	80	60.2	1956 Buick Roadmaster Convertible	全尺寸convertible	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Hardtop Sedan	末期经典全尺寸sedan	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1957			215.3	77.6	58.7	1957 Buick Roadmaster Hardtop Coupe	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Coupe	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster 2-Door Hardtop	末期经典全尺寸coupe	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1957			215.3	77.6	59.29	1957 Buick Roadmaster Convertible	末期经典敞篷	可入库
Buick Roadmaster	Buick	跑车		Convertible	Std.	gen6 full-size	1958			219.1	79.8	60	1958 Buick Series 75 Roadmaster Convertible Coupe	末期经典敞篷	可入库
Buick Roadmaster	Buick	三厢车		Sedan	Std.	gen7 full-size	1992-1996			215.8	78.1	55.9	1992-1996 Buick Roadmaster Sedan	RWD sedan	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1991			217.5	78.9	60.1	1991 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Roadmaster	Buick	两厢车		Wagon	Std.	gen7 full-size	1992-1996			217.7	79.9	60.3	1992-1996 Buick Roadmaster Estate Wagon	wgn更高	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1953			207.6	79.9	58.9	1953 Buick Series 70 Skylark Convertible	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen1 personal luxury	1954			206.3	76.8	60.2	1954 Buick Skylark Convertible Model 100	早期限量敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Convertible	A-body敞篷	可入库
Buick Skylark	Buick	跑车		Convertible	Std.	gen3 mid-size	1970-1972			203.3	76.8	53.8	1970-1972 Buick Skylark Convertible	敞篷低车身	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Coupe	A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1970			206.3	77.3	54.2	1970 Buick Skylark Custom Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1971			203.2	77.3	54.2	1971 Buick Skylark 2-Door Coupe	A-body coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen3 mid-size	1972			206.3	77.3	54.2	1972 Buick Skylark Coupe	宽体A-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark 2-Door Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Coupe	X-body低车身coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Coupe	FWD X-body	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Coupe	FWD X-body末年	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Coupe	N-body初期	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Coupe	首年N-body新外观	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Coupe	1993高度变化	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Coupe	1994偏长	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Coupe	后期coupe	可入库
Buick Skylark	Buick	跑车		Coupe	Std.	gen7 facelift compact	1997			188.5	68.2	53.5	1997 Buick Skylark Coupe	末期coupe	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1975			200.3	69.9	53.2	1975 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1976			200.3	72.7	52.1	1976 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	两厢车		Hatchback	Std.	gen4 compact	1977-1979			200.2	72.7	52.2	1977-1979 Buick Skylark Hatchback Coupe	X-body hatchback	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1965/1967			203.4	73.6	54	1965/1967 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen2 mid-size	1966			204	75.5	54.3	1966 Buick Skylark Sedan	A-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1968			204.7	75.6	54.1	1968 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1969			204.7	75.6	54.1	1969 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1970			206.3	77.2	54	1970 Buick Skylark Custom Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1971			207.2	77.3	54.3	1971 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen3 mid-size	1972			207.3	76.8	54.3	1972 Buick Skylark 4-Door Sedan	A-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1975			200.3	72.8	53.2	1975 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1976			200.3	72.7	53.1	1976 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1977			200.3	72.8	53.2	1977 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1978			200.2	72.7	53.1	1978 Buick Skylark 4-Door Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen4 compact	1979			200.2	72.7	53.1	1979 Buick Skylark Sedan	X-body sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1980-1984			181.9	69.1	53.7	1980-1984 Buick Skylark Sedan	FWD X-body	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen5 compact	1985			181.1	69.1	53.6	1985 Buick Skylark Limited Sedan	FWD X-body末年	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1986			180	66	52	1986 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1987			180.1	66.6	52.1	1987 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1988			180.1	66.6	52.2	1988 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1989			180.1	66.7	52.2	1989 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen6 compact	1990-1991			180	66.6	52.1	1990-1991 Buick Skylark Sedan	N-body初期	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1992			189.2	67.5	52.2	1992 Buick Skylark Sedan	首年N-body新外观	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1993			189.1	67.5	53.2	1993 Buick Skylark Sedan	1993高度变化	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 compact	1994			198.1	67.5	53.2	1994 Buick Skylark Sedan	1994偏长	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1995			189.2	68.7	53.5	1995 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1996			189.1	68.7	53.2	1996 Buick Skylark Sedan	后期sedan	可入库
Buick Skylark	Buick	三厢车		Sedan	Std.	gen7 facelift compact	1997-1998			188.5	68.2	53.5	1997-1998 Buick Skylark Sedan	末期sedan；1998 fleet为主	可入库
Buick Skylark	Buick	两厢车		Wagon	Std.	gen3 mid-size	1969-1972			213.7	76.8	54.8	1969-1972 Buick Skylark Sportwagon	长车顶	可入库
4) 下一步优先核对

无；当前批次已完成。

本批次完成。

