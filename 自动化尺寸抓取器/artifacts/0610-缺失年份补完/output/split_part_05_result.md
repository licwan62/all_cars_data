# 文件名：split_part_05.tsv


--- Round 1 / 首次发送 ---
ChatGPT 说：更新点：


遍历参考车型核对年份区间，拆分部分结构/版本以确保逐年覆盖。


本轮新增可入库记录数量：5（1970 Dodge Challenger、1978 Dodge Challenger、1966 Dodge Charger、1968 Dodge Charger、1971 Dodge Charger部分年份拆分完成）。


本轮新增完成三维口径数量：0（缺乏尺寸数据，需要后续来源补充）。


TSV（当前批次完整可替换）：
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Dodge Challenger	跑车	Dodge	Challenger	Coupe		gen1	E-body pony car	1970-1972					191.3	76.3	50.9	1970 Dodge Challenger Hardtop	1975-1977 断年无 Challenger；1970-1972 按早期 E-body 候选尺寸，未逐年终核	待终核: 缺失 1971/1972 逐年参考
Dodge Challenger	跑车	Dodge	Challenger	Coupe		gen1	E-body pony car	1973-1974					198.6	77.4	50.9	1973 Dodge Challenger Hardtop	1973-1974 保险杠外廓加长，候选尺寸，未逐年终核	待终核: 缺失 1974 逐年参考
Dodge Challenger	跑车	Dodge	Challenger	Coupe		gen2	Mitsubishi-based compact coupe	1978-1983					183.1	65.9	51.8	1978 Dodge Challenger Coupe	三菱 Galant Lambda / Sapporo 系紧凑 Coupe 候选尺寸，未逐年终核	待终核: 缺失 1979/1980/1981/1982/1983 逐年参考
Dodge Charger	跑车	Dodge	Charger	Coupe		gen1	B-body fastback coupe	1966-1967					203.6	75.3	53.0	1966 Dodge Charger		待终核: 缺失 1967 逐年参考
Dodge Charger	跑车	Dodge	Charger	Coupe		gen2	B-body muscle coupe	1968-1970					208.0	76.6	53.2	1968 Dodge Charger		待终核: 缺失 1969/1970 逐年参考
Dodge Charger	跑车	Dodge	Charger	Coupe		gen3	B-body coke-bottle coupe	1971-1972					205.4	79.1	52.2	1971 Dodge Charger		待终核: 缺失 1972 逐年参考
Dodge Charger	跑车	Dodge	Charger	Coupe		gen3	B-body coke-bottle coupe	1973-1974					214.0	77.0	52.6	1973 Dodge Charger	1973-1974 外廓加长，候选尺寸，未逐年终核	待终核: 缺失 1974 逐年参考
Dodge Charger	跑车	Dodge	Charger	Coupe		gen4	personal luxury B-body coupe	1975-1978					215.3	77.7	52.6	1975 Dodge Charger	1979-1981 断年需留痕；1975-1978 候选尺寸，未逐年终核	待终核: 缺失 1976/1977/1978 逐年参考
Dodge Charger	两厢车	Dodge	Charger	Hatchback		gen5	L-body compact hatchback	1982-1987					174.0	66.7	50.8	1982 Dodge Charger Hatchback	候选尺寸，未逐年终核	待终核: 缺失 1983/1984/1985/1986/1987 逐年参考
Dodge Durango	越野车	Dodge	Durango	SUV		gen1	Dakota-based midsize SUV	1998					193.2	71.5	72.6	1998 Dodge Durango SUV	候选尺寸	待终核: 需复核 1998 尺寸口径与 w/o mirrors
Dodge Durango	越野车	Dodge	Durango	SUV		gen1	Dakota-based midsize SUV	1999-2001					193.3	71.5	72.9	1999 Dodge Durango SUV	候选尺寸，未逐年终核	待终核: 缺失 2000/2001 逐年参考
Dodge Durango	越野车	Dodge	Durango	SUV		gen1	Dakota-based midsize SUV	2002-2003					193.5	71.3	72.0	2002 Dodge Durango SUV	候选尺寸，未逐年终核	待终核: 缺失 2003 逐年参考
Ford Thunderbird	跑车	Ford	Thunderbird	Convertible		gen1	two-seat personal car	1955					175.3	70.3	52.4	1955 Ford Thunderbird Convertible	1955 two-seat removable hardtop roadster，结构按 Convertible 处理；候选尺寸	待终核: 需复核 1955 Convertible 尺寸口径
Ford Thunderbird	跑车	Ford	Thunderbird	Convertible		gen1	two-seat personal car	1956					185.2	71.3	52.4	1956 Ford Thunderbird Convertible	1956 后备胎外置导致车长变化；候选尺寸	待终核: 需复核 1956 Convertible 尺寸口径
Ford Thunderbird	跑车	Ford	Thunderbird	Convertible		gen1	two-seat personal car	1957					181.4	72.8	51.8	1957 Ford Thunderbird Convertible	1957 车身修订；候选尺寸	待终核: 需复核 1957 Convertible 尺寸口径
Ford Thunderbird	跑车	Ford	Thunderbird	Coupe		gen2	four-seat squarebird personal luxury	1958					205.4	77.0	52.5	1958 Ford Thunderbird Hardtop	候选尺寸	待终核: 需复核 1958 Coupe/Hardtop 尺寸口径
Ford Thunderbird	跑车	Ford	Thunderbird	Convertible		gen2	four-seat squarebird personal luxury	1958					205.4	77.0	53.1	1958 Ford Thunderbird Convertible	Convertible 高度候选值，未终核	待终核: 需复核 1958 Convertible 尺寸口径
Ford Thunderbird	跑车	Ford	Thunderbird	Coupe		gen2	four-seat squarebird personal luxury	1959-1960					205.4	77.0	52.5	1959 Ford Thunderbird Hardtop	候选尺寸，未逐年终核	待终核: 缺失 1960 Coupe/Hardtop 逐年参考
Ford Thunderbird	跑车	Ford	Thunderbird	Convertible		gen2	four-seat squarebird personal luxury	1959-1960					205.4	77.0	53.1	1959 Ford Thunderbird Convertible	Convertible 高度候选值，未逐年终核	待终核: 缺失 1960 Convertible 逐年参考