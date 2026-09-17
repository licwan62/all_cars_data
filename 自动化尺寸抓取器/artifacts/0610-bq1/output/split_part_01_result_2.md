# 文件名：split_part_01.tsv


--- Round 1 / 首次发送 ---
更新点

本轮新增可入库记录数量：13。

本轮新增完成三维口径数量：13。

已把空白 版本 统一补为 Std.。

已按新字段口径移除旧字段 代际说明 / 区间最小年份 / 区间最大年份。

A5 2017 与 2018 跨代且尺寸不同，已在原 2017-2018 范围内拆成单年。2017 A5 Coupe/Cabriolet 参考 Car and Driver、Autoweb；2018 A5 Coupe/Cabriolet 参考 Edmunds、J.D. Power、Audi USA media kit。
奥迪
+4
Car and Driver
+4
Autoweb
+4

A8 2004-2006 LWB 原宽度 79.8 为疑似含镜宽，已按 w/o mirrors 修正为 74.6；同时 2004 与 2005-2006 长度差 0.4 in，已拆分。
The Car Connection
+2
Edmunds
+2

A4/A6/A8/A3 等按 Edmunds/KBB/交叉来源补齐逐年参考链。
Edmunds
+5
Edmunds
+5
Edmunds
+5

当前批次进度

当前批次原 10 行，拆分后 13 行。

13/13 行三维完整，13/13 行本轮判定为可入库。

暂无剩余待终核行。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Audi A3	两厢车	Audi	A3	Hatchback	Std.	gen2	2007-2009			169	69.5	56	2007/2008/2009 Audi A3 Hatchback	紧凑型五门两厢车；2009 长度取同代最大值；w/o mirrors 口径按 69.5 交叉校正	可入库
Audi A3	三厢车	Audi	A3	Sedan	Std.	gen4 facelift	2025			177.3	71.5	56.2	2025 Audi A3 Sedan	紧凑型豪华三厢轿车	可入库
Audi A4	三厢车	Audi	A4	Sedan	Std.	gen5 B9	2017-2019			186.1	72.5	56.2	2017-2019 Audi A4 Sedan	紧凑型豪华三厢轿车；逐年尺寸一致	可入库
Audi A5	跑车	Audi	A5	Coupe	Std.	gen1 B8.5	2017			182.1	73	54	2017 Audi A5 Coupe	双门豪华轿跑；2017 仍为上一代 B8.5，不能与 2018 B9 合并	可入库
Audi A5	跑车	Audi	A5	Coupe	Std.	gen2 B9	2018			184	72.7	54	2018 Audi A5 Coupe	双门豪华轿跑；2018 换代 B9	可入库
Audi A5	跑车	Audi	A5	Convertible	Std.	gen1 B8.5	2017			182.1	73	54.4	2017 Audi A5 Cabriolet	软顶豪华敞篷车；2017 仍为上一代 B8.5，不能与 2018 B9 合并	可入库
Audi A5	跑车	Audi	A5	Convertible	Std.	gen2 B9	2018			184	72.7	54.4	2018 Audi A5 Cabriolet	软顶豪华敞篷车；2018 换代 B9	可入库
Audi A6	三厢车	Audi	A6	Sedan	Std.	gen4 C7	2013-2015			193.9	73.8	57.8	2013/2014/2015 Audi A6 Sedan	中大型豪华三厢轿车；2013 宽度 73.7、2015 宽度 73.8，取最大 w/o mirrors	可入库
Audi A8	三厢车	Audi	A8	Sedan	LWB	gen2 D3	2004			204	74.6	57.3	2004 Audi A8 L Sedan	长轴距全尺寸豪华轿车；原 79.8 为含镜宽口径，已修正为 w/o mirrors 74.6	可入库
Audi A8	三厢车	Audi	A8	Sedan	LWB	gen2 D3	2005-2006			204.4	74.6	57.3	2005/2006 Audi A8 L Sedan	长轴距全尺寸豪华轿车；2005-2006 长度 204.4，与 2004 的 204.0 差异超过 0.1，已拆分	可入库
Audi A8	三厢车	Audi	A8	Sedan	LWB	gen3 D4 facelift	2015-2018			207.4	76.7	57.9	2015/2016/2017/2018 Audi A8 L Sedan	长轴距全尺寸豪华轿车；逐年尺寸一致	可入库
Audi A8	三厢车	Audi	A8	Sedan	LWB	gen4 D5	2019			208.7	76.6	58.5	2019 Audi A8 L Sedan	长轴距全尺寸豪华轿车	可入库
Audi A8	三厢车	Audi	A8	Sedan	LWB	gen4 D5 facelift	2022-2023			209.5	76.6	58.3	2022/2023 Audi A8 L Sedan	长轴距全尺寸豪华轿车；逐年覆盖 2022 与 2023	可入库

下一步优先核对

当前 split_part_01 已无待终核行。

若继续下一批，优先核对同样容易出错的跨代单年、含镜宽误填为 w/o mirrors、以及 Coupe/Convertible 同年不同结构尺寸。

本批次完成。

