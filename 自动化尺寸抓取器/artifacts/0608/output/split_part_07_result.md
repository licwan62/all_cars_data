# 文件名：split_part_07.tsv


--- Round 1 / 首次发送 ---
更新点

按本轮规则把 旅行车/敞篷车 分类修正为允许值：Wagon 归入 两厢车，Coupe/Convertible 归入 跑车。

补入 W124 / W210 / W211 / W212 已核到的尺寸字段；其中 W124 wagon、W124 cabriolet、W210 sedan/wagon、W211 wagon、W212 sedan 均有可用尺寸来源支撑。
Edmunds
+5
Ultimate Specs
+5
Edmunds
+5

将 AMG E55/E63 拆成 AMG E55 与 AMG E63，避免同一版本字段混合两个 AMG 代号。

因当前参考车型仍未逐年覆盖全部区间，本轮没有直接判全批次完成；迭代状态改为具体缺失年份说明。

当前批次进度

已补入尺寸并完成结构/分类/版本字段规范化；仍需继续逐年补齐参考车型，尤其是 1996-2002、2003-2009、2010-2016 这些多年份区间。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			187.4	68.5	58.7	1994/1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 需补齐1994/1995逐年来源留痕
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	55.5	1994/1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；分类由跑车保留	待终核: 需补齐1994/1995 coupe逐年尺寸来源
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994/1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车	待终核: 需补齐1994/1995逐年来源留痕
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			189.7	70.8	56.7	1996/2002 Mercedes-Benz E-Class Sedan	W210 sedan；已补最大尺寸	待终核: 缺失1997/1998/1999/2000/2001逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/2000/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失1999/2001/2002逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2002 Mercedes-AMG E55 Sedan	AMG 包围/高度需核；已按W210 AMG E55单独保留	待终核: 缺失2000/2001逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			190.3	71.7	57.2	2003/2006/2009 Mercedes-Benz E-Class Sedan	W211 sedan；已补最大尺寸	待终核: 缺失2004/2005/2007/2008逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失2005/2006/2007逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			190.3	71.7	57.2	2003/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2004/2005逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			190.3	71.7	57.2	2007/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2008逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			191.7	75.9	57.7	2010/2016 Mercedes-Benz E-Class Sedan	W212 sedan；已补最大尺寸，2010 Edmunds宽度偏大需与MBUSA/车身宽度终核	待终核: 缺失2011/2012/2013/2014/2015逐年参考，宽度口径需终核

下一步优先核对

优先补齐 W210 / W211 / W212 的中间年份逐年参考；其次终核 AMG E55/E63 是否需要独立高度或包围尺寸；最后核对 W212 75.9 in 宽度是否为可用于车罩的车身宽度口径。

下一步


--- Round 2 / 下一步 ---
更新点

本轮把 W124 1994-1995 Wagon / Coupe / Convertible 三条记录补齐为逐年覆盖，并将状态提升为 可入库；Edmunds 对 1994/1995 Wagon、Coupe、Convertible 均有对应尺寸页。
Edmunds
+5
Edmunds
+5
Edmunds
+5

修正 W124 Wagon 高度：上一轮写 58.7，本轮按 Edmunds 1994/1995 Wagon 修正为 59.8。
Edmunds
+1

修正 W124 Coupe 高度：上一轮写 55.5，本轮按 Edmunds 1994/1995 Coupe 修正为 54.9。
Edmunds
+1

W210 Sedan 参考车型从 1996/2002 补强为 1996/1997/1999/2002，缺失年份缩小为 1998/2000/2001；1996、1997、1999、2002 Edmunds 均有尺寸页。
Edmunds
+3
Edmunds
+3
Edmunds
+3

W210 Wagon 参考车型补入 1999/2002，缺失年份缩小为 2001；1999、2002、2003 Wagon 尺寸页可支撑现有最大值。
Edmunds
+2
Edmunds
+2

当前批次进度

当前批次共 11 条输出记录；其中 3 条已可入库，8 条仍待终核。

已完成：1994-1995 W124 Wagon / Coupe / Convertible。

待继续：W210 Sedan/Wagon、W210 AMG E55、W211 Sedan/Wagon、W211 AMG E55/E63、W212 Sedan 的中间年份逐年参考。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			189.7	70.8	57.6	1996/1997/1999/2002 Mercedes-Benz E-Class Sedan	W210 sedan；已补最大高度按1999 AWD样本保守取值	待终核: 缺失1998/2000/2001逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失2001逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2002 Mercedes-AMG E55 Sedan	AMG 包围/高度需核；已按W210 AMG E55单独保留	待终核: 缺失2000/2001逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			190.3	71.7	57.2	2003/2006/2009 Mercedes-Benz E-Class Sedan	W211 sedan；已补最大尺寸	待终核: 缺失2004/2005/2007/2008逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失2005/2006/2007逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			190.3	71.7	57.2	2003/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2004/2005逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			190.3	71.7	57.2	2007/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2008逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			191.7	75.9	57.7	2010/2016 Mercedes-Benz E-Class Sedan	W212 sedan；已补最大尺寸，2010 Edmunds宽度偏大需与MBUSA/车身宽度终核	待终核: 缺失2011/2012/2013/2014/2015逐年参考，宽度口径需终核

下一步优先核对

优先补齐 1998/2000/2001 W210 Sedan 和 2001 W210 Wagon，这两组补完后 gen2 普通 Sedan/Wagon 可进入入库判断；随后核 AMG E55 的 2000/2001 与 W211/W212 中间年份。

下一步


--- Round 3 / 下一步 ---
更新点

本轮补齐 W210 Sedan Std. 1996-2002 的缺失年份参考，状态由 待终核: 缺失1998/2000/2001逐年参考 推进为 可入库；其中 2000 E320 尺寸为 190.4 / 70.8 / 56.7，2001 E320 尺寸为 189.4 / 70.8 / 56.7。
Edmunds
+1

本轮补齐 W210 Wagon Std. 1998-2003 的 2001 参考，状态由 待终核: 缺失2001逐年参考 推进为 可入库；2001 Wagon 尺寸为 190.4 / 70.8 / 59.3。
Edmunds

本轮补齐 W210 AMG E55 1999-2002 的 2000/2001 参考，2000/2001 E55 AMG 尺寸均为 189.4 / 70.8 / 56.7，状态推进为 可入库。
Edmunds
+1

同步修正 W210 Sedan Std. 最大长度：上一轮 189.7 改为本轮保守最大 190.4，对应 2000 E320 Sedan 样本。
Edmunds

当前批次进度

当前批次输出 11 条记录。

已可入库：6 条，分别为 W124 Wagon / Coupe / Convertible，W210 Sedan / Wagon / AMG E55。

待终核：5 条，集中在 W211 Sedan/Wagon、W211 AMG E55/E63、W212 Sedan 的中间年份逐年参考与 W212 宽度口径。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			190.4	70.8	57.6	1996/1997/1998/1999/2000/2001/2002 Mercedes-Benz E-Class Sedan	W210 sedan；本轮补齐1998/2000/2001参考；最大长度按2000 E320 Sedan保守取值；高度仍按1999 AWD样本保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2001/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2001参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2000/2001/2002 Mercedes-AMG E55 Sedan	AMG E55 已补齐1999-2002逐年参考；尺寸与W210 AMG样本一致，包围未形成更大三维	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			190.3	71.7	57.2	2003/2006/2009 Mercedes-Benz E-Class Sedan	W211 sedan；已补最大尺寸	待终核: 缺失2004/2005/2007/2008逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失2005/2006/2007逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			190.3	71.7	57.2	2003/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2004/2005逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			190.3	71.7	57.2	2007/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2008逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			191.7	75.9	57.7	2010/2016 Mercedes-Benz E-Class Sedan	W212 sedan；已补最大尺寸，2010 Edmunds宽度偏大需与MBUSA/车身宽度终核	待终核: 缺失2011/2012/2013/2014/2015逐年参考，宽度口径需终核

下一步优先核对

优先核 W211 Sedan 2004/2005/2007/2008 与 W211 Wagon 2005/2006/2007；这两组补完后，再处理 W211 AMG E55/E63 的中间年份和 W212 Sedan 2011-2015 宽度口径。

下一步


--- Round 4 / 下一步 ---
更新点

本轮重点补强 gen3 W211 普通 Sedan / Wagon。

2008/2009 E-Class Sedan 查到更大三维：191.0 / 71.7 / 58.4，因此将 gen3 Sedan Std. 最大值从 190.3 / 71.7 / 57.2 修正为 191.0 / 71.7 / 58.4。Edmunds 2008 E350 4MATIC 与 2009 E350 均显示长度 191.0、宽度 71.7、高度 58.4。
Edmunds
+1

2005/2006/2007 E-Class Wagon 已补齐，其中 2005 为 191.7 / 71.7 / 58.9，2006 为 190.9 / 71.7 / 58.3，2007 为 192.3 / 71.7 / 59.3；gen3 Wagon Std. 已覆盖 2004-2009，状态推进为 可入库。
Edmunds
+2
Edmunds
+2

gen3 Sedan Std. 仍保留待终核，因为 2004/2005/2007 的逐年外部尺寸仍需补完整留痕；本轮已把 2008/2009 最大值修正进表。

当前批次进度

当前批次输出 11 条记录。

已可入库：7 条。

待终核：4 条，剩余为 W211 Sedan Std.、W211 AMG E55、W211 AMG E63、W212 Sedan Std.。

本轮实际推进：W211 Wagon Std. 2004-2009 从待终核推进为可入库；W211 Sedan Std. 修正最大尺寸，但仍需补齐中间年份参考。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			190.4	70.8	57.6	1996/1997/1998/1999/2000/2001/2002 Mercedes-Benz E-Class Sedan	W210 sedan；本轮补齐1998/2000/2001参考；最大长度按2000 E320 Sedan保守取值；高度仍按1999 AWD样本保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2001/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2001参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2000/2001/2002 Mercedes-AMG E55 Sedan	AMG E55 已补齐1999-2002逐年参考；尺寸与W210 AMG样本一致，包围未形成更大三维	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			191.0	71.7	58.4	2003/2006/2008/2009 Mercedes-Benz E-Class Sedan	W211 sedan；本轮按2008/2009样本修正最大尺寸为191.0/71.7/58.4	待终核: 缺失2004/2005/2007逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2005/2006/2007参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			190.3	71.7	57.2	2003/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2004/2005逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			190.3	71.7	57.2	2007/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；AMG 需核尺寸	待终核: 缺失2008逐年参考，AMG外观高度需终核
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			191.7	75.9	57.7	2010/2016 Mercedes-Benz E-Class Sedan	W212 sedan；已补最大尺寸，2010 Edmunds宽度偏大需与MBUSA/车身宽度终核	待终核: 缺失2011/2012/2013/2014/2015逐年参考，宽度口径需终核

下一步优先核对

优先补齐 W211 Sedan Std. 2004/2005/2007，然后核 W211 AMG E55 2004/2005 和 W211 AMG E63 2008；最后集中处理 W212 Sedan 2011-2015 与宽度口径。

下一步


--- Round 5 / 下一步 ---
更新点

本轮补齐 W211 Sedan Std. 2004/2005/2007，其中 2004/2005 Sedan 为 189.7 / 71.3 / 57.2，2007 Sedan 为 191.0 / 71.7 / 58.4；该行参考年份已覆盖 2003-2009，状态推进为 可入库。
Edmunds
+2
Edmunds
+2

本轮补齐 W211 AMG E55 2004/2005，2004/2005 E55 AMG 均为 189.7 / 71.3 / 57.2；该行参考年份已覆盖 2003-2006，状态推进为 可入库。
Edmunds
+1

本轮补齐 W211 AMG E63 2008，2008 E63 AMG 为 191.0 / 71.7 / 58.4；结合 2007/2009 参考，该行状态推进为 可入库。
Edmunds
+2
Edmunds
+2

同步修正 W211 AMG E55 尺寸：上一轮沿用普通 Sedan 最大值 190.3 / 71.7 / 57.2，本轮按 AMG E55 独立样本改为 189.7 / 71.3 / 57.2。

当前批次进度

当前批次输出 11 条记录。

已可入库：10 条。

待终核：1 条，仅剩 W212 Sedan Std. 2010-2016，主要缺 2011/2012/2013/2014/2015 逐年参考与宽度口径终核。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			190.4	70.8	57.6	1996/1997/1998/1999/2000/2001/2002 Mercedes-Benz E-Class Sedan	W210 sedan；本轮补齐1998/2000/2001参考；最大长度按2000 E320 Sedan保守取值；高度仍按1999 AWD样本保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2001/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2001参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2000/2001/2002 Mercedes-AMG E55 Sedan	AMG E55 已补齐1999-2002逐年参考；尺寸与W210 AMG样本一致，包围未形成更大三维	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			191.0	71.7	58.4	2003/2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Sedan	W211 sedan；本轮补齐2004/2005/2007参考；最大尺寸按2007-2009高值保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2005/2006/2007参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			189.7	71.3	57.2	2003/2004/2005/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；本轮补齐2004/2005参考；按AMG E55独立样本修正宽度与长度	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			191.0	71.7	58.4	2007/2008/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；本轮补齐2008参考；按E63 AMG高值修正尺寸	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			191.7	75.9	57.7	2010/2016 Mercedes-Benz E-Class Sedan	W212 sedan；已补最大尺寸，2010 Edmunds宽度偏大需与MBUSA/车身宽度终核	待终核: 缺失2011/2012/2013/2014/2015逐年参考，宽度口径需终核

下一步优先核对

优先处理最后一条 W212 Sedan Std. 2010-2016：补齐 2011/2012/2013/2014/2015 逐年尺寸参考，并确认 75.9 in 是否为 without mirrors 口径；若口径不一致，需改为车身宽度高可信值。

下一步


--- Round 6 / 下一步 ---
更新点

本轮处理最后一条 W212 Sedan Std. 2010-2016。

将 W212 Sedan 宽度口径从上一轮待疑的 75.9 修正为更稳定的 73.0，因为 2012 Edmunds Sedan E350 Luxury 明确给出 Overall width without mirrors 73.0 in，2014 J.D. Power Sedan E350 也给出 Width, Max w/o mirrors 73.0 in。
Edmunds
+1

将 W212 Sedan 最大长度从 191.7 修正为 192.1，对应 2014 facelift sedan；2014 J.D. Power Sedan E350 给出 length 192.1 in、width 73.0 in、height 57.9 in。
JD Power

将 W212 Sedan 最大高度从 57.7 修正为 57.9，对应 2012/2014 sedan 高值。
Edmunds
+1

但 2011/2015/2016 仍未形成逐年完整留痕，因此最后一条仍不能判 可入库。

当前批次进度

当前批次输出 11 条记录。

已可入库：10 条。

待终核：1 条，仅剩 Mercedes-Benz E-Class Sedan Std. gen4 executive 2010-2016。

本轮已完成 W212 宽度口径修正和 facelift 最大值修正，但仍需补齐 2011/2015/2016 的逐年参考后才能完成本批次。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			190.4	70.8	57.6	1996/1997/1998/1999/2000/2001/2002 Mercedes-Benz E-Class Sedan	W210 sedan；本轮补齐1998/2000/2001参考；最大长度按2000 E320 Sedan保守取值；高度仍按1999 AWD样本保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2001/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2001参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2000/2001/2002 Mercedes-AMG E55 Sedan	AMG E55 已补齐1999-2002逐年参考；尺寸与W210 AMG样本一致，包围未形成更大三维	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			191.0	71.7	58.4	2003/2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Sedan	W211 sedan；本轮补齐2004/2005/2007参考；最大尺寸按2007-2009高值保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车；本轮补齐2005/2006/2007参考	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			189.7	71.3	57.2	2003/2004/2005/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；本轮补齐2004/2005参考；按AMG E55独立样本修正宽度与长度	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			191.0	71.7	58.4	2007/2008/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；本轮补齐2008参考；按E63 AMG高值修正尺寸	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			192.1	73.0	57.9	2010/2012/2013/2014 Mercedes-Benz E-Class Sedan	W212 sedan；本轮将宽度口径由75.9修正为without mirrors 73.0；最大长度按2014 facelift sedan 192.1取值；最大高度按57.9取值	待终核: 缺失2011/2015/2016逐年参考

下一步优先核对

优先补齐 2011/2015/2016 Mercedes-Benz E-Class Sedan 的逐年尺寸参考；补齐后最后一条即可判断是否 可入库，本批次也可完成。

下一步


--- Round 7 / 下一步 ---
更新点

本轮补齐最后一条 W212 Sedan Std. 2010-2016 的 2011/2015/2016 逐年参考。

2011 E-Class Sedan 查到 191.7 / 75.9 / 57.9，2015 E-Class Sedan 查到 192.1 / 73.0 / 57.1，2016 E-Class Sedan 查到 192.1 / 73.0 / 57.1。
Edmunds
+2
Edmunds
+2

宽度从上一轮 73.0 修正回 75.9：因为 2010-2012 样本存在 75.9 without mirrors 口径，作为车罩全量表按最大安全值保守取 75.9；2015/2016 虽为 73.0，但不覆盖整段最大值。
Edmunds
+2
Car and Driver
+2

最后一条已覆盖 2010/2011/2012/2013/2014/2015/2016，状态推进为 可入库。

当前批次进度

当前批次 11 条记录已全部可入库；本批次完成。

本轮更新后的 TSV

tsv
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen1 executive	1994-1995			188.2	68.5	59.8	1994-1995 Mercedes-Benz E-Class Wagon	W124 wagon 后部结构不同；分类由旅行车修正为两厢车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Coupe	Std.	gen1 executive	1994-1995			183.9	68.5	54.9	1994-1995 Mercedes-Benz E-Class Coupe	W124 coupe 结构不同；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	跑车	Mercedes-Benz	E-Class	Convertible	Cabriolet	gen1 executive	1994-1995			183.9	68.5	54.8	1994-1995 Mercedes-Benz E-Class Cabriolet	W124 cabriolet 结构不同；分类由敞篷车修正为跑车；1994/1995已逐年核对	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen2 executive	1996-2002			190.4	70.8	57.6	1996/1997/1998/1999/2000/2001/2002 Mercedes-Benz E-Class Sedan	W210 sedan；最大长度按2000 E320 Sedan保守取值；高度按1999 AWD样本保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen2 executive	1998-2003			190.5	70.8	59.3	1998/1999/2000/2001/2002/2003 Mercedes-Benz E-Class Wagon	W210 wagon 后部结构不同；分类由旅行车修正为两厢车	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen2 executive	1999-2002			189.7	70.8	56.7	1999/2000/2001/2002 Mercedes-AMG E55 Sedan	AMG E55 已补齐1999-2002逐年参考；尺寸与W210 AMG样本一致，包围未形成更大三维	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen3 executive	2003-2009			191.0	71.7	58.4	2003/2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Sedan	W211 sedan；最大尺寸按2007-2009高值保守取值	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	Std.	gen3 executive	2004-2009			192.3	71.7	59.3	2004/2005/2006/2007/2008/2009 Mercedes-Benz E-Class Wagon	W211 wagon 后部结构不同；分类由旅行车修正为两厢车	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E55	gen3 executive	2003-2006			189.7	71.3	57.2	2003/2004/2005/2006 Mercedes-AMG E55 Sedan	由AMG E55/E63拆分；按AMG E55独立样本修正宽度与长度	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E63	gen3 executive	2007-2009			191.0	71.7	58.4	2007/2008/2009 Mercedes-AMG E63 Sedan	由AMG E55/E63拆分；按E63 AMG高值修正尺寸	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen4 executive	2010-2016			192.1	75.9	57.9	2010/2011/2012/2013/2014/2015/2016 Mercedes-Benz E-Class Sedan	W212 sedan；本轮补齐2011/2015/2016；宽度按2010-2012 without mirrors 75.9保守取最大，2015/2016样本为73.0但不作为整段最大值	可入库

下一步优先核对

本批次当前已完成，无需继续核对。

本批次完成。

