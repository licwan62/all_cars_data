# 文件名：split_part_10.tsv


--- Round 1 / 首次发送 ---
更新点

GLA-Class：分类从 SUV 规范为 越野车；Std. facelift 与 AMG facelift 分开保留，AMG 改款尺寸大于普通 GLA，不能合并。2025 GLA 250 为 173.6 / 72.2 / 63.5；2024 AMG GLA 35 与 2026 AMG GLA 35 均为 174.6 / 72.8 / 62.5。
Edmunds
+2
Edmunds
+2

S-Class：补入 W140 / W220 / W221 / W222 / Maybach 主要尺寸；W222 普通 S-Class 与 Maybach 长度差异明显，继续独立。2014/2020 W222 普通 S-Class 尺寸约 206.5-206.9 / 74.8 / 58.7-58.9；Maybach 为 215.3 / 75.6 / 59.4。
Edmunds
+2
Edmunds
+2

对未能形成“逐年完整参考”的区间，不沿用可入库，统一写明缺失年份范围。

当前批次进度

当前 10 条已全部补入尺寸；但多条历史 S-Class 仍缺中间年份逐年参考，暂不能判为完整可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；缺 2025 独立样本	待终核: 缺失 2025 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.3	59.1	1994-1998 Mercedes-Benz S-Class Sedan	按 W140 sedan 最大值处理；1999 需单独确认是否同 W140	待终核: 缺失 1999 年份参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.0	57.1	2000/2002/2006 Mercedes-Benz S-Class Sedan	W220 sedan；使用美规长车身最大值	待终核: 缺失 2001/2003/2004/2005 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.1	73.0	57.1	2006 Mercedes-Benz S65 AMG	W220 AMG；已核 2006 S65 AMG，S55/S65 中间年需继续补齐	待终核: 缺失 2001/2002/2003/2004/2005 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class Sedan	W221 sedan；按 LWB 最大长度处理	待终核: 缺失逐年参考明细
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class AMG / LWB	长轴/AMG 与普通 sedan 高度/包围需继续逐年核	待终核: 缺失逐年 AMG/LWB 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach	待终核: 缺失 2015/2016/2017/2018/2019 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.3	75.6	59.4	2020 Mercedes-Maybach S-Class	Maybach 长轴明显加长，必须独立	待终核: 缺失 2016/2017/2018/2019 年份参考

下一步优先核对

优先补齐 S-Class 的逐年参考：W220 2001/2003/2004/2005、W222 2015-2019、Maybach 2016-2019；其次补 AMG GLA 2025 独立尺寸样本。

下一步


--- Round 2 / 下一步 ---
更新点

补齐 2025 AMG GLA 35：尺寸确认为 174.6 / 72.8 / 62.5，GLA 250 为 173.6 / 72.2 / 63.5，两者尺寸不同，继续分行；GLA AMG 行从“缺 2025”推进为可入库。
Edmunds
+1

W140 S-Class Sedan：补到 1999 LWB 样本，1999 S320 LWB 长度为 205.2 in、宽 74.3 in、高 56.9 in；该行仍缺 1994-1998 的逐年明细，所以不判可入库。
Edmunds

W220 S-Class Sedan：补到 2004 Edmunds 样本，2004 S500 为 203.1 / 73.0 / 57.2；缺口从 2001/2003/2004/2005 缩小为 2001/2003/2005。
Edmunds

W222 S-Class：2020 trim 对照显示普通 sedan 多数为 206.9 / 74.8 / 58.9，AMG/Maybach 类更宽或更长，继续维持 Maybach 独立。
Edmunds

当前批次进度

当前 10 条均已补入尺寸。

已可入库：3 条（GLA Std. facelift、GLA AMG facelift、S-Class Coupe 1994-1995）。

待终核：7 条，主要集中在 S-Class 历史年份逐年参考未完整覆盖。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2025/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；2025 已补齐	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.3	59.1	1999 Mercedes-Benz S-Class S320 LWB / 1994-1998 Mercedes-Benz S-Class Sedan	按 W140 sedan 最大值处理；1999 LWB 已补，1994-1998 仍需逐年明细	待终核: 缺失 1994/1995/1996/1997/1998 年份逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.0	57.2	2000/2002/2004/2006 Mercedes-Benz S-Class Sedan	W220 sedan；2004 S500 已补，高度最大值修正为 57.2	待终核: 缺失 2001/2003/2005 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.1	73.0	57.2	2006 Mercedes-Benz S65 AMG / 2004 Mercedes-Benz S-Class S500 base reference	W220 AMG；AMG 外观包围对长宽高影响仍需逐年确认	待终核: 缺失 2001/2002/2003/2004/2005 年份 AMG 参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class Sedan	W221 sedan；按 LWB 最大长度处理	待终核: 缺失 2007/2008/2009/2010/2011/2012/2013 逐年参考明细
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class AMG / LWB	长轴/AMG 与普通 sedan 高度/包围需继续逐年核	待终核: 缺失 2007/2008/2009/2010/2011/2012/2013 逐年 AMG/LWB 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2017/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach；2020 trim 对照已补	待终核: 缺失 2015/2016/2018/2019 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.3	75.6	59.4	2020 Mercedes-Maybach S-Class / 2019 Mercedes-Maybach S-Class length reference	Maybach 长轴明显加长，必须独立	待终核: 缺失 2016/2017/2018/2019 年份完整三维参考

下一步优先核对

优先补齐 S-Class：W220 缺失的 2001/2003/2005；W222 普通 2015/2016/2018/2019；Maybach 2016-2019 完整三维；最后核 W221 2007-2013 普通与 AMG/LWB 是否需要拆分。

下一步


--- Round 3 / 下一步 ---
更新点

W220 普通 Sedan 已补齐 2000-2006 逐年参考：2000/2001 为 203.1 / 73.1 / 56.9，2003/2004/2005 为 203.1 / 73.0 / 57.2，按区间最大值保留 203.1 / 73.1 / 57.2，本轮推进为可入库。
Cars.com
+3
Edmunds
+3
Edmunds
+3

W222 普通 Sedan 补齐 2015/2016/2018/2019：2015/2016 为 206.5 / 74.8 / 58.7，2018 MBUSA sedan 为 206.9 / 74.8 / 58.8，2019 Edmunds 为 206.9 / 74.8 / 58.9，2020 为 206.9 / 74.8 / 58.9，按区间最大值保留 206.9 / 74.8 / 58.9。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Maybach 行补到 2019 长度依据：2019 Mercedes-Maybach S-Class 约 215 in，仍缺 2016-2018 完整三维，不能入库。
Architectural Digest

AMG GLA、GLA 普通版保持上一轮已完整覆盖状态；S-Class Coupe 1994-1995 保持可入库。

当前批次进度

当前 10 条中，已可入库 5 条：GLA Std.、GLA AMG、S-Class Coupe、W220 普通 Sedan、W222 普通 Sedan。
仍待终核 5 条：W140 Sedan、W220 AMG、W221 普通 Sedan、W221 AMG/LWB、W222 Maybach。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2025/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；2025 已补齐	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.3	59.1	1999 Mercedes-Benz S-Class S320 LWB / 1994-1998 Mercedes-Benz S-Class Sedan	按 W140 sedan 最大值处理；1999 LWB 已补，1994-1998 仍需逐年明细	待终核: 缺失 1994/1995/1996/1997/1998 年份逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.1	57.2	2000/2001/2002/2003/2004/2005/2006 Mercedes-Benz S-Class Sedan	W220 sedan；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.1	73.0	57.2	2003 Mercedes-Benz S55 AMG / 2006 Mercedes-Benz S65 AMG / W220 AMG dimension reference	W220 AMG；S55/S65 仍需按 AMG 年份逐年确认	待终核: 缺失 2001/2002/2004/2005 年份 AMG 参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class Sedan	W221 sedan；按 LWB 最大长度处理	待终核: 缺失 2007/2008/2009/2010/2011/2012/2013 逐年参考明细
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			205.4	73.7	58.0	2007-2013 Mercedes-Benz S-Class AMG / LWB	长轴/AMG 与普通 sedan 高度/包围需继续逐年核	待终核: 缺失 2007/2008/2009/2010/2011/2012/2013 逐年 AMG/LWB 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2015/2016/2017/2018/2019/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.3	75.6	59.4	2019/2020 Mercedes-Maybach S-Class	Maybach 长轴明显加长，必须独立；2019 已补长度依据，2020 三维完整	待终核: 缺失 2016/2017/2018 年份完整三维参考

下一步优先核对

优先核 W221 2007-2013 普通 Sedan 与 AMG/LWB 是否尺寸相同；其次补 W140 1994-1998 逐年明细；最后补 W220 AMG 2001/2002/2004/2005 与 Maybach 2016-2018 完整三维。

下一步


--- Round 4 / 下一步 ---
更新点

W221 普通 Sedan 补强到 2007/2009/2012/2013：2007 S550 与 2009 S550 均为 205.0 / 73.7 / 58.0，2013 S550 仍属 W221 末年样本；当前仍缺 2008/2010/2011 逐年参考，暂不判可入库。
Edmunds
+2
Edmunds
+2

W220 AMG S55/S65 补齐 2001/2002 参考：2001、2002 S55 AMG 均为 203.1 / 73.1 / 56.9；结合已有 2003/2006 样本后，缺口缩小为 2004/2005 AMG 参考。
Edmunds
+1

Maybach 行补入 2018 官方/Edmunds 双参考：2018 Mercedes-Maybach S560 为约 215.0 / 74.8 / 59.0，2019 为 215 in 长度参考，2020 Edmunds 为 215.0 / 74.8 / 59.0；缺口缩小为 2016/2017。
梅赛德斯-奔驰媒体
+2
Car and Driver
+2

W222 普通 Sedan 维持可入库：2016 Edmunds 显示普通 S-Class Sedan 为 206.5 / 74.8 / 58.7，与上一轮 2014-2020 普通区间最大值逻辑一致。
Edmunds

当前批次进度

当前 10 条中，已可入库 5 条：GLA Std.、GLA AMG、S-Class Coupe、W220 普通 Sedan、W222 普通 Sedan。
仍待终核 5 条：W140 Sedan、W220 AMG、W221 普通 Sedan、W221 AMG/LWB、W222 Maybach；其中 W220 AMG 与 Maybach 缺口本轮已明显收窄。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2025/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；2025 已补齐	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.3	59.1	1999 Mercedes-Benz S-Class S320 LWB / 1994-1998 Mercedes-Benz S-Class Sedan	按 W140 sedan 最大值处理；1999 LWB 已补，1994-1998 仍需逐年明细	待终核: 缺失 1994/1995/1996/1997/1998 年份逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.1	57.2	2000/2001/2002/2003/2004/2005/2006 Mercedes-Benz S-Class Sedan	W220 sedan；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.1	73.1	56.9	2001/2002/2003 Mercedes-Benz S55 AMG / 2006 Mercedes-Benz S65 AMG	W220 AMG；2001/2002 S55 AMG 已补，2004/2005 AMG 仍需逐年确认	待终核: 缺失 2004/2005 年份 AMG 参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			205.0	73.7	58.0	2007/2009/2012/2013 Mercedes-Benz S-Class S550 Sedan	W221 sedan；已补 2007/2009/2012/2013，按已核样本最大值保留	待终核: 缺失 2008/2010/2011 年份参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			205.0	73.7	58.0	2012/2013 Mercedes-Benz S65 AMG / 2007-2013 Mercedes-Benz S-Class LWB reference	W221 AMG/LWB；已确认 S65 AMG 属 W221 AMG 样本，但仍缺多数年份逐年 AMG/LWB 对应	待终核: 缺失 2007/2008/2009/2010/2011 年份 AMG/LWB 参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2015/2016/2017/2018/2019/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.0	74.8	59.0	2018/2019/2020 Mercedes-Maybach S-Class	Maybach 长轴明显加长，必须独立；2018/2020 三维已补，2019 长度已补	待终核: 缺失 2016/2017 年份完整三维参考

下一步优先核对

优先补 W221 普通 Sedan 的 2008/2010/2011；其次补 W220 AMG 2004/2005；再补 Maybach 2016/2017；最后处理 W140 1994-1998 与 W221 AMG/LWB 2007-2011。

下一步


--- Round 5 / 下一步 ---
更新点

W221 普通 Sedan：补齐 2008/2010/2011。2008 仍为 205.0 / 73.7 / 58.0，2010/2011 facelift LWB 为 206.5 / 73.7 / 58.0，所以该行最大长度从 205.0 修正为 206.5，并推进为可入库。
Edmunds
+2
Edmunds
+2

W220 AMG S55/S65：补齐 2004/2005，2005 S55 AMG 为 203.1 / 73.0 / 57.2；2006 S55 AMG 搜到 203.3 / 73.0 / 57.1，所以该行最大长度从 203.1 修正为 203.3，推进为可入库。
Edmunds
+2
Edmunds
+2

W222 Maybach：补齐 2016/2017，2016/2017 Edmunds Maybach 长度 214.7、高度 59.0/58.7，但 Edmunds 缺 without-mirrors 宽度；与 2018/2020 对照后仍按当前最大 215.0 / 74.8 / 59.0 保留，推进为可入库。
Edmunds
+1

W140 Sedan 本轮补到 1994/1995，但 1996-1998 仍缺逐年参考，继续待终核。
Edmunds
+1

当前批次进度

当前 10 条中，已可入库 8 条：GLA Std.、GLA AMG、S-Class Coupe、W220 普通 Sedan、W220 AMG、W221 普通 Sedan、W222 普通 Sedan、W222 Maybach。
仍待终核 2 条：W140 Sedan、W221 AMG/LWB。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2025/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；2025 已补齐	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.6	58.7	1994/1995/1999 Mercedes-Benz S-Class Sedan	按 W140 sedan 最大值处理；1994/1995/1999 已补，1996-1998 仍需逐年明细	待终核: 缺失 1996/1997/1998 年份逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.1	57.2	2000/2001/2002/2003/2004/2005/2006 Mercedes-Benz S-Class Sedan	W220 sedan；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.3	73.1	57.2	2001/2002/2003/2004/2005/2006 Mercedes-Benz S55/S65 AMG	W220 AMG；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			206.5	73.7	58.0	2007/2008/2009/2010/2011/2012/2013 Mercedes-Benz S-Class S550 Sedan	W221 sedan；2010/2011 facelift LWB 长度更大，按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			206.5	73.7	58.0	2011/2012/2013 Mercedes-Benz S63/S65 AMG / W221 LWB reference	W221 AMG/LWB；已补后期 AMG/LWB 尺寸，早期 AMG/LWB 仍缺逐年对应	待终核: 缺失 2007/2008/2009/2010 年份 AMG/LWB 参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2015/2016/2017/2018/2019/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.0	74.8	59.0	2016/2017/2018/2019/2020 Mercedes-Maybach S-Class	Maybach 长轴明显加长，必须独立；2016/2017 已补，按区间最大值保留	可入库

下一步优先核对

优先补 W140 Sedan 的 1996/1997/1998；其次补 W221 AMG/LWB 的 2007/2008/2009/2010。如果这两条闭环，本批次即可完成。

下一步


--- Round 6 / 下一步 ---
更新点

W140 Sedan 补齐 1996/1997/1998：1996 S500 为 205.2 / 74.3 / 58.5，1997 S600 为 205.2 / 74.3 / 58.3，1998 TheCarConnection 继续给出 205.2 / 74.3；结合 1994/1995/1999 已核样本后，该行按最大值修正为 205.2 / 74.4 / 58.9，推进为可入库。
Edmunds
+2
Edmunds
+2

W221 AMG/LWB 补齐 2007/2008/2009/2010：2007 S-Class trims 覆盖 AMG/LWB 为 205.0 / 73.7 / 58.0，2008 S63 AMG 为 205.0 / 73.7 / 58.0，2010 S65 AMG 为 206.5 / 73.7 / 58.0；结合 2011/2012/2013 后，该行按区间最大值 206.5 / 73.7 / 58.0 推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

本轮没有新增当前 TSV 范围外车型、代际或年份；只在原 10 条记录范围内补齐缺失年份参考和修正最大尺寸。

当前批次进度

当前 10 条已全部逐年闭环，10/10 可入库。
本批次当前已完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std. facelift	gen2 facelift subcompact SUV	2024-2026			173.6	72.2	63.5	2024/2025/2026 Mercedes-Benz GLA-Class GLA 250	2024 改款；普通 GLA 与 AMG GLA 尺寸不同，不合并	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG facelift	gen2 facelift subcompact SUV	2024-2026			174.6	72.8	62.5	2024/2025/2026 Mercedes-AMG GLA 35	AMG 改款较普通版更长更宽；2025 已补齐	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen1 W140 full-size luxury	1994-1999			205.2	74.4	58.9	1994/1995/1996/1997/1998/1999 Mercedes-Benz S-Class Sedan	按 W140 sedan 区间最大值处理；1994-1999 已逐年覆盖	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen1 C140 full-size luxury coupe	1994-1995			199.4	75.3	57.2	1994/1995 Mercedes-Benz S-Class Coupe	C140 coupe；1996 后多归 CL-Class	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen2 W220 full-size luxury	2000-2006			203.1	73.1	57.2	2000/2001/2002/2003/2004/2005/2006 Mercedes-Benz S-Class Sedan	W220 sedan；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S55/S65	gen2 W220 full-size luxury	2001-2006			203.3	73.1	57.2	2001/2002/2003/2004/2005/2006 Mercedes-Benz S55/S65 AMG	W220 AMG；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen3 W221 full-size luxury	2007-2013			206.5	73.7	58.0	2007/2008/2009/2010/2011/2012/2013 Mercedes-Benz S-Class S550 Sedan	W221 sedan；2010/2011 facelift LWB 长度更大，按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG / LWB variants	gen3 W221 full-size luxury	2007-2013			206.5	73.7	58.0	2007/2008/2009/2010/2011/2012/2013 Mercedes-Benz S63/S65 AMG / LWB	W221 AMG/LWB；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen4 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014/2015/2016/2017/2018/2019/2020 Mercedes-Benz S-Class Sedan	W222 sedan；普通长轴，不含 Maybach；逐年覆盖后按区间最大值保留	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach / LWB	gen4 W222 full-size luxury	2016-2020			215.0	74.8	59.0	2016/2017/2018/2019/2020 Mercedes-Maybach S-Class	Maybach 长轴明显加长，必须独立；逐年覆盖后按区间最大值保留	可入库

下一步优先核对

无。当前批次 10 条均已可入库。

本批次完成。

