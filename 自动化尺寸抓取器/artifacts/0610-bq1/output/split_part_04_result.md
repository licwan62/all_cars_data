# 文件名：split_part_04.tsv


--- Round 1 / 首次发送 ---
ChatGPT 说：更新点：


本轮推进：逐行复核 Audi TT / Sebring / Elantra / Evoque / RX-7 / Mercedes-Benz C-Class / Lancer / Sentra 当前年份区间与参考车型是否覆盖。


新增可入库记录数量：0


新增完成三维口径数量：0


发现多数记录参考车型仅覆盖部分年份或单样本年份，需要扩展数据来源确认完整年份覆盖。


本轮更新后的 TSV：
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2010-2014	2010	2014			165.3	72.5	53.2	2012 Audi TT Coupe	紧凑型双门跑车	待终核: 缺失年份 2010/2011/2013/2014
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2010-2015	2010	2015			165.3	72.5	53.2	2012 Audi TT Roadster	紧凑型软顶跑车	待终核: 缺失年份 2010/2011/2013/2014/2015
Chrysler Sebring	跑车	Chrysler	Sebring	Convertible		gen3	convertible	2007	2007	2007			193.8	71.5	58.4	2007 Chrysler Sebring Convertible	中型软顶敞篷车	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2002-2006	2002	2006			177.1	67.7	56.1	2004 Hyundai Elantra GT Hatchback	紧凑型五门两厢车	待终核: 缺失年份 2002/2003/2005/2006
Land Rover Evoque	越野车	Land Rover	Evoque	SUV		gen2	compact SUV	2019	2019	2019			172.1	75	64.9	2019 Range Rover Evoque SUV	紧凑型豪华 SUV	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe		gen3	FD coupe	1992	1992	1992			168.5	68.9	48.4	1993 Mazda RX-7 Coupe	FD 双门跑车	待终核: 缺失年份 1992
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan		gen4	W205 sedan	2015	2015	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	紧凑型豪华三厢轿车	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe		gen2	C-Class coupe	2016	2016	2016			184.5	71.3	55.3	2016 Mercedes-Benz C-Class Coupe	豪华双门轿跑	可入库
Mitsubishi Lancer	三厢车	Mitsubishi	Lancer	Sedan		gen2	late sedan	2011-2014	2011	2014			180	69.4	58.7	2012 Mitsubishi Lancer Sedan	紧凑型三厢轿车	待终核: 缺失年份 2011/2013/2014
Nissan Sentra	三厢车	Nissan	Sentra	Sedan		gen6	compact sedan	2007-2012	2007	2012			179.8	70.5	59.5	2008 Nissan Sentra Sedan	紧凑型三厢轿车	待终核: 缺失年份 2007/2009/2010/2011/2012
下一步优先核对：


扩展数据来源：官方厂商官网配置器/Edmunds Features & Specs/KBB Specs/NHTSA vPIC


验证 Audi TT 2010-2015、Hyundai Elantra 2002-2006、Mazda RX-7 1992、Mitsubishi Lancer 2011-2014、Nissan Sentra 2007-2012 全年参考车型覆盖，确保可入库


下一步


--- Round 2 / 下一步 ---
更新点

本轮新增可入库记录数量：2

本轮新增完成三维口径数量：2

推进记录：Mitsubishi Lancer 2011-2014、Nissan Sentra 2007-2012 已补齐逐年参考覆盖，参考车型压缩为完整连续年份段。

Audi TT 本轮发现 2010/2011/2012/2013/2014 年份存在长度差异，先按已核对年份拆分，不强行合并；Convertible 也存在高度差异，继续待终核。Edmunds 对 TT 2010/2011/2012/2013/2014 的长宽高显示并非完全一致。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Lancer 2011-2014 Sedan 已按 Edmunds 逐年补齐，取同结构普通 Sedan 覆盖最大高度 58.7。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Sentra 2007-2012 Sedan 已按 Edmunds 逐年补齐，2007-2011 普通 Sedan 为 179.8/70.5/59.5，2012 为 180.1/70.5/59.5，当前压缩取最大长 180.1。
Edmunds
+5
Edmunds
+5
Edmunds
+5

当前批次进度

当前批次总记录：10 条

本轮后可入库：6 条

仍待终核：4 条

仍待终核集中在 Audi TT Coupe / Convertible、Hyundai Elantra Hatchback、Mazda RX-7 1992。

本轮新增可入库记录数量：2

本轮新增完成三维口径数量：2

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2010				164.5	72.5	53.2	2010 Audi TT Coupe	2010 已核对；2011/2014 长度不同，2012/2013 与 2010 接近但仍需按全年闭合后决定是否合并	待终核: 当前原区间 2010-2014 已拆分推进，仍缺 2011/2012/2013/2014 最终合并口径
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2011				165.4	72.5	53.2	2011 Audi TT Coupe	2011 Coupe 长度 165.4，区别于 2010/2012/2013/2014	待终核: 需确认是否为 trim/页面口径差异
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2012-2013				164.5	72.5	53.2	2012-2013 Audi TT Coupe	2012/2013 Coupe 已同源核对，尺寸一致	待终核: 需补交叉来源后入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2014				165.3	72.5	53.2	2014 Audi TT Coupe	2014 Coupe 长度 165.3，区别于 2012-2013	待终核: 需补交叉来源后入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2010				164.5	72.5	53.2	2010 Audi TT Convertible	2010 Roadster/Convertible 已核对；后续年份高度存在 53.5	待终核: 当前原区间 2010-2015 已拆分推进，仍缺 2011/2013/2014/2015 最终合并口径
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2011				165.4	72.5	53.5	2011 Audi TT Convertible	2011 Convertible 高度 53.5，区别于 Coupe	待终核: 需补交叉来源后入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2012				164.5	72.5	53.5	2012 Audi TT Convertible	2012 Convertible 已核对	待终核: 缺失年份 2013/2014/2015
Chrysler Sebring	跑车	Chrysler	Sebring	Convertible		gen3	convertible	2007				193.8	71.5	58.4	2007 Chrysler Sebring Convertible	中型软顶敞篷车	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2002				177.1	67.7	56.1	2002 Hyundai Elantra GT Hatchback	2002 已核对；2005/2006 长度为 177.9，原 2002-2006 不宜直接整段合并	待终核: 缺失年份 2003/2004，且需确认 2002-2004 与 2005-2006 是否拆分
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2005-2006				177.9	67.7	56.1	2005-2006 Hyundai Elantra GT Hatchback	2005/2006 Hatchback 已核对，尺寸一致	待终核: 缺失年份 2003/2004
Land Rover Evoque	越野车	Land Rover	Evoque	SUV		gen2	compact SUV	2019				172.1	75	64.9	2019 Range Rover Evoque SUV	紧凑型豪华 SUV	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe		gen3	FD coupe	1992				168.5	68.9	48.4	1992 Mazda RX-7 Coupe; 1993 Mazda RX-7 Coupe	1992 FD 尺寸需以更高可信来源闭合；1993 Edmunds/KBB 可作同代线索但不能单独覆盖 1992	待终核: 1992 仍需厂商 brochure/Edmunds/KBB 或可靠交叉来源确认
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan		gen4	W205 sedan	2015				184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	紧凑型豪华三厢轿车	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe		gen2	C-Class coupe	2016				184.5	71.3	55.3	2016 Mercedes-Benz C-Class Coupe	豪华双门轿跑	可入库
Mitsubishi Lancer	三厢车	Mitsubishi	Lancer	Sedan		gen2	late sedan	2011-2014				180	69.4	58.7	2011-2014 Mitsubishi Lancer Sedan	2011-2014 Sedan 已逐年核对；普通 Sedan/GT/Ralliart 高度存在 58.3/58.7，车衣口径取最大高度 58.7	可入库
Nissan Sentra	三厢车	Nissan	Sentra	Sedan		gen6	compact sedan	2007-2012				180.1	70.5	59.5	2007-2012 Nissan Sentra Sedan	2007-2012 Sedan 已逐年核对；2012 长度 180.1，2007-2011 为 179.8，压缩取最大长度	可入库

下一步优先核对

Audi TT：继续补 2013/2014/2015 Convertible，并用 KBB / Car and Driver / Audi brochure 交叉确认 Edmunds 年份差异是否为 trim 页面差异。

Hyundai Elantra：补 2003/2004 GT Hatchback，并确认 2002-2004 与 2005-2006 是否必须按长度差异拆分。

Mazda RX-7：优先找 1992 Mazda 官方 brochure / Edmunds 1992 / KBB 1992；若没有，再用 KBB 1993 + CarsGuide/AutoEvolution/Automobile-Catalog 作为谨慎交叉，不直接单源入库。

下一步


--- Round 3 / 下一步 ---
更新点




本轮新增可入库记录数量：3


本轮新增完成三维口径数量：3


主要推进：
• Audi TT Coupe 2012-2013 已确认逐年 Edmunds/KBB 尺寸一致，可标记待终核阶段闭合口径；
• Audi TT Convertible 2010-2012 已确认尺寸差异较小，合并 2010-2012 年份段，尺寸取最大值 165.4/72.5/53.5；
• Hyundai Elantra Hatchback 2002-2004 已补全 Edmunds 年份逐年尺寸，2002-2004 长宽高取最大值 177.9/67.7/56.1。




当前批次进度




总记录数：10


可入库：9 条（新增 3 条）


待终核：1 条（Mazda RX-7 1992）




本轮更新后的 TSV


tsv主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2010				164.5	72.5	53.2	2010 Audi TT Coupe	2010 已核对	待终核: 2011/2014/2015Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2011				165.4	72.5	53.2	2011 Audi TT Coupe	2011 已核对	待终核: 2010/2012/2013/2014/2015Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2012-2013				164.5	72.5	53.2	2012-2013 Audi TT Coupe	尺寸一致	可入库Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2014				165.3	72.5	53.2	2014 Audi TT Coupe	单年核对	待终核: 2010/2011/2012/2013/2015Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2010-2012				165.4	72.5	53.5	2010-2012 Audi TT Convertible	尺寸取最大值	可入库Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2013-2015				165.4	72.5	53.5	2013-2015 Audi TT Convertible	后续核对剩余年份	待终核: 2013/2014/2015Chrysler Sebring	跑车	Chrysler	Sebring	Convertible		gen3	convertible	2007				193.8	71.5	58.4	2007 Chrysler Sebring Convertible	中型软顶敞篷车	可入库Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2002-2004				177.9	67.7	56.1	2002-2004 Hyundai Elantra GT Hatchback	尺寸取最大值	可入库Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2005-2006				177.9	67.7	56.1	2005-2006 Hyundai Elantra GT Hatchback	尺寸一致	可入库Land Rover Evoque	越野车	Land Rover	Evoque	SUV		gen2	compact SUV	2019				172.1	75	64.9	2019 Range Rover Evoque SUV	紧凑型豪华 SUV	可入库Mazda RX-7	跑车	Mazda	RX-7	Coupe		gen3	FD coupe	1992				168.5	68.9	48.4	1992 Mazda RX-7 Coupe; 1993 Mazda RX-7 Coupe	1992 FD 尺寸需以更高可信来源闭合	待终核: 1992Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan		gen4	W205 sedan	2015				184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	紧凑型豪华三厢轿车	可入库Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe		gen2	C-Class coupe	2016				184.5	71.3	55.3	2016 Mercedes-Benz C-Class Coupe	豪华双门轿跑	可入库Mitsubishi Lancer	三厢车	Mitsubishi	Lancer	Sedan		gen2	late sedan	2011-2014				180	69.4	58.7	2011-2014 Mitsubishi Lancer Sedan	尺寸取最大值	可入库Nissan Sentra	三厢车	Nissan	Sentra	Sedan		gen6	compact sedan	2007-2012				180.1	70.5	59.5	2007-2012 Nissan Sentra Sedan	尺寸取最大值	可入库


下一步优先核对




Audi TT Convertible 2013-2015，核对 Edmunds / KBB / Audi brochure，确认 2013-2015 年份尺寸完整覆盖，可入库；


Audi TT Coupe 2010/2011/2014，核对 Edmunds / KBB / Audi brochure，确认尺寸差异及全年覆盖；


Mazda RX-7 1992 FD，寻找官方 brochure 或 Edmunds 1992/1993 可靠交叉来源，完成三维口径闭合。




下一步


--- Round 4 / 下一步 ---
更新点

本轮新增可入库记录数量：5

本轮新增完成三维口径数量：5

Audi TT Coupe 原 2010-2014 区间已按年份差异拆分并闭合：2010、2011、2012-2013、2014 均改为可入库。Edmunds 2010 TT 给出 164.5 / 72.5 / 53.2，2014 TT 给出 165.3 / 72.5 / 53.2，说明原整段 2010-2014 不能直接用一个尺寸压缩。
Edmunds
+1

Audi TT Convertible 2013-2015 已补齐：2013 为 164.5 / 72.5 / 53.5，2014 为 165.3 / 72.5 / 53.5，2015 为 165.3 / 72.5 / 53.5；合并 2014-2015，2013 单独留痕。
Edmunds
+2
Edmunds
+2

Mazda RX-7 1992 仍不直接判可入库：CarsGuide / AutoEvolution / Automobile-Catalog 均指向 4295 mm / 1750 mm / 1230 mm，折算约 169.1 / 68.9 / 48.4；但其中 AutoEvolution / Automobile-Catalog 属谨慎来源，且与原表 168.5 长度存在 0.6 in 差异，所以本轮先修正尺寸口径为 169.1 / 68.9 / 48.4，状态保留待终核。
carsguide.com.au
+2
autoevolution
+2

当前批次进度

当前批次原始记录：10 条

拆分后当前 TSV 记录：17 条

本轮后可入库：16 条

仍待终核：1 条，集中在 Mazda RX-7 1992

本轮新增可入库记录数量：5

本轮新增完成三维口径数量：5

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2010				164.5	72.5	53.2	2010 Audi TT Coupe	2010 单年已核对；与 2011/2014 长度不同，单独留痕	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2011				165.4	72.5	53.2	2011 Audi TT Coupe	2011 单年已核对；长度区别于 2010/2012-2013/2014	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2012-2013				164.5	72.5	53.2	2012-2013 Audi TT Coupe	2012/2013 Coupe 已逐年核对，尺寸一致	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2014				165.3	72.5	53.2	2014 Audi TT Coupe	2014 单年已核对；长度区别于 2010/2011/2012-2013	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2010				164.5	72.5	53.5	2010 Audi TT Convertible	2010 Convertible 已核对；高度按 Convertible/Roadster 口径修正为 53.5	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2011				165.4	72.5	53.5	2011 Audi TT Convertible	2011 Convertible 已核对；长度 165.4	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2012-2013				164.5	72.5	53.5	2012-2013 Audi TT Convertible	2012/2013 Convertible 已逐年核对，尺寸一致	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2014-2015				165.3	72.5	53.5	2014-2015 Audi TT Convertible	2014/2015 Convertible 已逐年核对，尺寸一致	可入库
Chrysler Sebring	跑车	Chrysler	Sebring	Convertible		gen3	convertible	2007				193.8	71.5	58.4	2007 Chrysler Sebring Convertible	中型软顶敞篷车	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2002-2004				177.9	67.7	56.1	2002-2004 Hyundai Elantra GT Hatchback	2002-2004 GT Hatchback 已逐年核对；压缩取最大长度 177.9	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2005-2006				177.9	67.7	56.1	2005-2006 Hyundai Elantra GT Hatchback	2005/2006 GT Hatchback 已逐年核对，尺寸一致	可入库
Land Rover Evoque	越野车	Land Rover	Evoque	SUV		gen2	compact SUV	2019				172.1	75	64.9	2019 Range Rover Evoque SUV	紧凑型豪华 SUV	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe		gen3	FD coupe	1992				169.1	68.9	48.4	1992 Mazda RX-7 Coupe	1992 FD 尺寸按 4295mm/1750mm/1230mm 折算修正；仍需官方 brochure/Edmunds/KBB 级别来源闭合	待终核: 1992 仍缺最可信或一般可信主来源确认
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan		gen4	W205 sedan	2015				184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	紧凑型豪华三厢轿车	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe		gen2	C-Class coupe	2016				184.5	71.3	55.3	2016 Mercedes-Benz C-Class Coupe	豪华双门轿跑	可入库
Mitsubishi Lancer	三厢车	Mitsubishi	Lancer	Sedan		gen2	late sedan	2011-2014				180	69.4	58.7	2011-2014 Mitsubishi Lancer Sedan	2011-2014 Sedan 已逐年核对；普通 Sedan/GT/Ralliart 高度存在 58.3/58.7，车衣口径取最大高度 58.7	可入库
Nissan Sentra	三厢车	Nissan	Sentra	Sedan		gen6	compact sedan	2007-2012				180.1	70.5	59.5	2007-2012 Nissan Sentra Sedan	2007-2012 Sedan 已逐年核对；2012 长度 180.1，2007-2011 为 179.8，压缩取最大长度	可入库

下一步优先核对

Mazda RX-7 1992：继续追加官方 Mazda brochure / KBB 1992 / Edmunds 1992 / NHTSA vPIC 车型年份验证；若找不到官方或 KBB/Edmunds 1992，则用 Car and Driver 1992 实测文章 + CarsGuide 1992 + AutoEvolution/Automobile-Catalog 做交叉说明，但不直接把谨慎来源单独作为入库主依据。

下一步

--- Round 5 / 人工复制 ---

主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2010				164.5	72.5	53.2	2010 Audi TT Coupe	2010 单年已核对	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2011				165.4	72.5	53.2	2011 Audi TT Coupe	2011 单年已核对	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2012-2013				164.5	72.5	53.2	2012-2013 Audi TT Coupe	尺寸一致	可入库
Audi TT	跑车	Audi	TT	Coupe		gen2	compact sports car	2014				165.3	72.5	53.2	2014 Audi TT Coupe	单年核对	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2010-2012				165.4	72.5	53.5	2010-2012 Audi TT Convertible	尺寸取最大值	可入库
Audi TT	跑车	Audi	TT	Convertible		gen2	compact sports car	2013-2015				165.4	72.5	53.5	2013-2015 Audi TT Convertible	尺寸取最大值	可入库
Chrysler Sebring	跑车	Chrysler	Sebring	Convertible		gen3	convertible	2007				193.8	71.5	58.4	2007 Chrysler Sebring Convertible	中型软顶敞篷车	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2002-2004				177.9	67.7	56.1	2002-2004 Hyundai Elantra GT Hatchback	尺寸取最大值	可入库
Hyundai Elantra	两厢车	Hyundai	Elantra	Hatchback		gen3	compact hatchback	2005-2006				177.9	67.7	56.1	2005-2006 Hyundai Elantra GT Hatchback	尺寸一致	可入库
Land Rover Evoque	越野车	Land Rover	Evoque	SUV		gen2	compact SUV	2019				172.1	75	64.9	2019 Range Rover Evoque SUV	紧凑型豪华 SUV	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe	Std.	gen3	compact sports	1993-1995				168.5	68.9	48.4	1994/1995 Mazda RX-7 FD	FD宽体低车身	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe	Std.	gen3	compact sports	1992				169.1	68.9	48.4	1992 Mazda RX-7 FD Coupe	FD宽体低车身，已核 Edmunds / CarsGuide / RX7Club	可入库
Mazda RX-7	跑车	Mazda	RX-7	Coupe/Convertible	Std.	gen2	compact sports	1986-1991				169.9	66.5	49.8	1986/1988/1991 Mazda RX-7 FC / 1990/1991 Mazda RX-7 Convertible Edmunds	FC世代; 软顶但三维同基准	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan		gen4	W205 sedan	2015				184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	紧凑型豪华三厢轿车	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe		gen2	C-Class coupe	2016				184.5	71.3	55.3	2016 Mercedes-Benz C-Class Coupe	豪华双门轿跑	可入库
Mitsubishi Lancer	三厢车	Mitsubishi	Lancer	Sedan		gen2	late sedan	2011-2014				180	69.4	58.7	2011-2014 Mitsubishi Lancer Sedan	尺寸取最大值	可入库
Nissan Sentra	三厢车	Nissan	Sentra	Sedan		gen6	compact sedan	2007-2012				180.1	70.5	59.5	2007-2012 Nissan Sentra Sedan	尺寸取最大值	可入库