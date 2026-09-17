# 文件名：split_part_15.tsv


--- Round 1 / 首次发送 ---
更新点

补齐 Porsche 911 当前批次三维尺寸。

将原“敞篷车”分类统一修正为本批次允许的“跑车”，结构保留 Convertible / Targa。

对 997 / 991 按中期尺寸风险拆分年份段。

992 Std. Coupe 2020-2024 已有连续区间尺寸依据，可入库；部分 996/997/991 宽体与特殊版本仍需逐年终核。参考依据包含 Edmunds / Car and Driver / Excellence Magazine 的 911 尺寸页。
Car and Driver
+4
Edmunds
+4
Edmunds
+4

当前批次进度

已补强：Porsche 911 gen5 996 / gen6 997 / gen7 991 / gen8 992。

已修正：分类、结构、版本、尺寸、参考车型覆盖表达。

未完成：996/997/991 的 Turbo / GT / Speedster 宽体组合仍需逐年逐版本终核，不能最终判为全部可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2/GT3	996 Turbo/GT2/GT3/GT3 RS 宽体或大尾翼，按车衣安全取宽体最大值	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2/GT3/GT3 RS 是否全部覆盖
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			174.6	71.2	51.2	2005/2006/2007/2008 Porsche 911 Carrera Coupe	997.1 普通 coupe，未并入 Turbo/GT 宽体	待终核: 需补齐 2006/2007/2008 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			175.8	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera Coupe	997.2 普通 coupe，中期改款后长度/宽度风险单独拆段	待终核: 需补齐 2009/2010/2011 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			174.6	71.2	51.6	2005/2006/2007/2008 Porsche 911 Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留	待终核: 需补齐 2006/2007/2008 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			175.8	72.9	51.6	2009/2010/2011/2012 Porsche 911 Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段	待终核: 需补齐 2009/2010/2011 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			174.6	71.2	51.6	2007/2008 Porsche 911 Targa	Targa 结构不同，玻璃顶车身单独保留	待终核: 需补齐 2008 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			175.8	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa	Targa 结构不同，997.2 改款后单独拆段	待终核: 需补齐 2009/2010/2011 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT widebody	gen6 997	2007-2012			175.8	72.9	51.6	2007/2008/2009/2010/2011/2012 Porsche 911 Turbo/GT2/GT3/GT3 RS	Turbo/GT2/GT3/GT3 RS 宽体或大尾翼，必须独立于普通 Carrera	待终核: 需逐年复核 2007-2012 Turbo/GT2/GT3/GT3 RS 版本覆盖
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	71.2	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera Coupe	991.1 普通 coupe，未并入 Turbo/GT 宽体	待终核: 需补齐 2013/2014/2015 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	71.5	51.0	2017/2018/2019 Porsche 911 Carrera Coupe	991.2 普通 coupe，facelift 后长度略增	待终核: 需补齐 2017/2018 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	71.2	51.2	2012/2013/2014/2015/2016 Porsche 911 Cabriolet	Cabriolet 结构不同，991.1 单独保留	待终核: 需补齐 2013/2014/2015 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	71.5	51.2	2017/2018/2019 Porsche 911 Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段	待终核: 需补齐 2017/2018 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa	Targa 结构不同，AWD/宽体风险高于普通 Carrera	待终核: 需补齐 2015/2016 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa	Targa 结构不同，991.2 facelift 后单独拆段	待终核: 需补齐 2017/2018 独立年份参考后确认可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT / Speedster	gen7 991	2014-2019			179.6	74.0	51.3	2014/2015/2016/2017/2018/2019 Porsche 911 Turbo/GT3/GT3 RS/Speedster	Turbo/GT3/GT3 RS/Speedster 属宽体、大尾翼或特殊车身，按车衣安全取最大包络	待终核: 需逐年复核 2014-2019 Turbo/GT/Speedster 各版本最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

先核 991 Turbo / GT / Speedster 2014-2019，因为该行混合了宽体、大尾翼、Speedster，最容易影响车衣尺寸。

再核 997 Turbo / GT widebody 2007-2012。

最后补齐 997/991 普通 Coupe / Cabriolet / Targa 的中间年份独立参考。

下一步


--- Round 2 / 下一步 ---
更新点

本轮继续补强 997 / 991 普通 Coupe、Cabriolet、Targa 的中间年份覆盖，把参考车型从“首尾/泛区间”改为逐年覆盖表达。

修正 997.1 / 997.2 普通 Coupe 的最大包络：Std. 行保留 Carrera / Carrera S / Carrera 4 / Carrera 4S 的安全最大值，宽体 Turbo / GT 仍单独保留。

991 Targa 按 Carrera 4/4S 宽体逻辑保留 72.9 in 宽度，不再和普通 Carrera Coupe 混用。

公开规格页显示 2005 911 Carrera S Coupe 长 175.6 / 宽 71.2 / 高 51.2，2011 911 Coupe 可到长 176.3 / 宽 72.9 / 高 51.2，2014 911 Cabriolet 为长 176.8 / 宽 71.2 / 高 51.3，2015 Targa 4S 为长 176.8 / 宽 72.9 / 高 50.8，2023 992 Carrera 基础尺寸约 4519×1852×1298 mm，本轮按车衣安全口径取最大包络。
汽车指南
+4
Edmunds
+4
Edmunds
+4

当前批次进度

已推进到：Porsche 911 当前 split 内 gen5 996 / gen6 997 / gen7 991 / gen8 992 全部行均已补尺寸。

本轮新增可入库：997 普通 Coupe / Convertible / Targa、991 普通 Coupe / Convertible / Targa、992 普通 Coupe。

仍待终核：996 Turbo/GT 宽体、997 Turbo/GT 宽体、991 Turbo/GT/Speedster 特殊包络，因为这些行混合多个高风险版本，仍需逐年逐版本确认最大长宽高。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2/GT3/GT3 RS	996 Turbo/GT2/GT3/GT3 RS 宽体或大尾翼，按车衣安全取宽体最大值	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2/GT3/GT3 RS 是否全部覆盖
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT widebody	gen6 997	2007-2012			176.3	72.9	51.6	2007/2008/2009/2010/2011/2012 Porsche 911 Turbo/GT2/GT3/GT3 RS	Turbo/GT2/GT3/GT3 RS 宽体或大尾翼，必须独立于普通 Carrera	待终核: 需逐年复核 2007/2008/2009/2010/2011/2012 Turbo/GT2/GT3/GT3 RS 版本覆盖
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT / Speedster	gen7 991	2014-2019			179.6	74.0	51.3	2014/2015/2016/2017/2018/2019 Porsche 911 Turbo/GT3/GT3 RS/Speedster	Turbo/GT3/GT3 RS/Speedster 属宽体、大尾翼或特殊车身，按车衣安全取最大包络	待终核: 需逐年复核 2014/2015/2016/2017/2018/2019 Turbo/GT/Speedster 各版本最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 991 Turbo / GT / Speedster 2014-2019：确认 GT3 RS、GT2 RS、Speedster 是否需要再从同一行拆出。

其次核 997 Turbo / GT widebody 2007-2012：确认 GT3 与 Turbo/GT2 是否同宽同高，是否应拆普通 GT3 与 RS/GT2。

最后核 996 Turbo / GT widebody 2001-2005：确认 GT3、GT2、Turbo 是否可共用最大包络。

下一步


--- Round 3 / 下一步 ---
更新点

本轮继续补强 3 条未完成的宽体 / GT / Speedster 高风险行。

将 996 Turbo / GT widebody 拆为 Turbo / GT2 widebody 与 GT3 / GT3 RS，因为 996 GT3 宽度约 69.7 in，而 Turbo/GT2 属宽体，不能继续混用同一宽体包络。
Excellence
+1

将 997 Turbo / GT widebody 拆为 Turbo / GT2 / GT3 RS widebody 与 GT3，因为 997 GT3 约 176.4 × 71.2 × 50.4 in，而 997 GT3 RS 宽度约 72.9 in，尺寸风险不同。
Excellence
+2
Excellence
+2

将 991 Turbo / GT / Speedster 拆为 Turbo / GT2 RS / GT3 RS widebody、GT3、Speedster，其中 2016 GT3 RS 为 178.9 × 74.0 × 50.8 in，2018 GT2 RS 为 179.1 × 74.0 × 51.1 in，2019 Speedster 为 179.6 × 73.0 × 49.3 in，Speedster 长度最大但宽高不是最大。
Edmunds
+2
Edmunds
+2

当前批次进度

已完成普通 997 / 991 / 992 Coupe、Convertible、Targa 行。

本轮已把 996 / 997 / 991 的混合高风险版本拆细到更安全的版本粒度。

仍待终核：996 Turbo/GT2 每个年份、997 Turbo/GT2/GT3 RS 每个年份、991 Turbo/GT2 RS/GT3 RS/Speedster 每个年份/版本覆盖。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 / GT3 RS widebody	gen6 997	2007-2012			176.9	72.9	51.6	2007/2008/2009/2010/2011/2012 Porsche 911 Turbo/GT2/GT3 RS	Turbo/GT2/GT3 RS 属宽体或大尾翼版本，独立于普通 Carrera 与普通 GT3	待终核: 需逐年复核 2007/2008/2009/2010/2011/2012 Turbo/GT2/GT3 RS 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997	2007-2011			176.4	71.2	50.4	2007/2008/2009/2010/2011 Porsche 911 GT3	997 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出	待终核: 需补齐 2008/2009/2011 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 RS / GT3 RS widebody	gen7 991	2014-2019			179.4	74.0	51.1	2014/2015/2016/2017/2018/2019 Porsche 911 Turbo/GT2 RS/GT3 RS	Turbo/GT2 RS/GT3 RS 属宽体、大尾翼或高空气动力版本，按最大宽高包络	待终核: 需逐年复核 2014/2015/2016/2017/2018/2019 Turbo/GT2 RS/GT3 RS 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991	2014-2019			179.4	72.9	51.1	2014/2015/2016/2017/2018/2019 Porsche 911 GT3	GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出	待终核: 需逐年复核 2014/2015/2016/2017/2018/2019 GT3 最大尺寸
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 991 Turbo / GT2 RS / GT3 RS widebody：确认 2014-2019 内 Turbo、Turbo S、GT3 RS、GT2 RS 是否需要继续拆成不同最大包络。

其次核 997 Turbo / GT2 / GT3 RS widebody：确认 2007-2012 GT2、GT2 RS、GT3 RS 与 Turbo 是否可共用 176.9 × 72.9 × 51.6。

最后核 996 Turbo / GT2 widebody 与 GT3 / GT3 RS：确认 2001-2005 各年份是否都有对应美国市场参考。

下一步


--- Round 4 / 下一步 ---
更新点

本轮继续推进 991 特殊版本行，不再把 Turbo、GT2 RS、GT3 RS 混在同一条记录里。

将 gen7 991 Turbo / GT2 RS / GT3 RS widebody 拆为 3 条：Turbo / Turbo S widebody、GT3 RS widebody、GT2 RS widebody。

保留 GT3 独立行；2018 GT3 Edmunds 规格为 179.6 × 72.9 × 50.0 in，明显不能和 74.0 in 宽体 GT3 RS / GT2 RS 混用。
Edmunds

GT3 RS / GT2 RS 宽体尺寸已进一步落点：2019 GT3 RS 为 179.4 × 74.0 × 51.1 in，2018 GT2 RS 为 179.1 × 74.0 × 51.1 in。
Edmunds
+1

当前批次进度

普通 997 / 991 / 992 Coupe、Convertible、Targa：已可入库。

991 Speedster：已可入库。

本轮进一步推进：991 特殊宽体版本已拆细。

仍待终核：996 Turbo/GT2、996 GT3/GT3 RS、997 Turbo/GT2/GT3 RS、997 GT3、991 Turbo/Turbo S、991 GT3 RS、991 GT2 RS、991 GT3。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 / GT3 RS widebody	gen6 997	2007-2012			176.9	72.9	51.6	2007/2008/2009/2010/2011/2012 Porsche 911 Turbo/GT2/GT3 RS	Turbo/GT2/GT3 RS 属宽体或大尾翼版本，独立于普通 Carrera 与普通 GT3	待终核: 需逐年复核 2007/2008/2009/2010/2011/2012 Turbo/GT2/GT3 RS 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997	2007-2011			176.5	71.2	50.4	2007/2008/2009/2010/2011 Porsche 911 GT3	997 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；本轮按 2007 GT3 已核尺寸修正长度	待终核: 需补齐 2008/2009/2010/2011 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991	2014-2019			177.4	74.0	51.0	2014/2015/2016/2017/2018/2019 Porsche 911 Turbo/Turbo S	991 Turbo/Turbo S 为宽体版本，但不同于 GT3 RS/GT2 RS 大尾翼包络，本轮从混合宽体行拆出	待终核: 需逐年复核 2014/2015/2016/2017/2018/2019 Turbo/Turbo S 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	待终核: 需确认当前 split 内 GT3 RS 是否仅覆盖 2016/2019 美国年款
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991	2014-2019			179.6	72.9	50.0	2014/2015/2016/2017/2018/2019 Porsche 911 GT3	GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；本轮按 2018 GT3 已核尺寸修正高度	待终核: 需确认 2016/2017 是否存在美国年款 GT3，若无销售需缩小为实际年份
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 991 Turbo / Turbo S 2014-2019：确认 991.1 与 991.2 是否需要按 facelift 拆成 2014-2016 / 2017-2019。

其次核 991 GT3：确认美国市场实际覆盖年份，尤其 2016/2017 是否应从 2014-2019 中切除。

再核 996 与 997 的 GT / Turbo 行：确认能否继续拆出 GT3 RS / GT2 / Turbo 的单独最大包络。

下一步


--- Round 5 / 下一步 ---
更新点

本轮继续补强 991 特殊版年份颗粒度。

将 991 Turbo / Turbo S widebody 2014-2019 拆为 991.1 2014-2016 和 991.2 2017-2019，保持年份合集不超出原 2014-2019。

将 991 GT3 2014-2019 修正为 2014-2016 与 2018-2019 两段，移除 2017 这个不稳定覆盖点，避免把无明确美国年款覆盖的年份混入。

将 991 GT3 RS 2016/2019 判为可入库；GT2 RS 2018、Speedster 2019 继续可入库。

2014 Turbo 尺寸为 177.4 × 74.0 × 51.0 in；Edmunds 2017 Turbo S 页面确认同属 2017 911 Turbo S Coupe 规格页；2014 Carrera 4S 页面显示普通 AWD 宽体为 176.8 × 72.9 × 51.0 in，说明 Turbo / GT RS 宽体不应与普通 Carrera 4S 混用。
Edmunds
+2
Edmunds
+2

当前批次进度

已可入库：997 普通 Coupe / Convertible / Targa；991 普通 Coupe / Convertible / Targa；991 Turbo/Turbo S；991 GT3；991 GT3 RS；991 GT2 RS；991 Speedster；992 普通 Coupe。

仍待终核：996 Turbo/GT2、996 GT3/GT3 RS、997 Turbo/GT2/GT3 RS、997 GT3。

当前批次仍未完成，因为 996 / 997 的 GT 与 Turbo 高风险行还需要继续核对。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 / GT3 RS widebody	gen6 997	2007-2012			176.9	72.9	51.6	2007/2008/2009/2010/2011/2012 Porsche 911 Turbo/GT2/GT3 RS	Turbo/GT2/GT3 RS 属宽体或大尾翼版本，独立于普通 Carrera 与普通 GT3	待终核: 需逐年复核 2007/2008/2009/2010/2011/2012 Turbo/GT2/GT3 RS 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997	2007-2011			176.5	71.2	50.4	2007/2008/2009/2010/2011 Porsche 911 GT3	997 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；按 GT3 最大包络	待终核: 需补齐 2008/2009/2010/2011 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 997 Turbo / GT2 / GT3 RS widebody，确认 2007-2012 是否需要继续拆成 Turbo / GT2 / GT3 RS 三条。

其次核 997 GT3，补齐 2008/2009/2010/2011 独立年份参考。

最后核 996 Turbo / GT2 widebody 与 GT3 / GT3 RS，确认 2001-2005 各版本美国市场覆盖和最大包络。

下一步


--- Round 6 / 下一步 ---
更新点

本轮继续补强 997 高风险版本行。

将原 997 Turbo / GT2 / GT3 RS widebody 2007-2012 进一步拆为：Turbo / Turbo S widebody、GT2 widebody、GT2 RS widebody、GT3 RS widebody，避免 Turbo、GT2、GT3 RS 混用同一条版本。

997 Turbo 2007 Edmunds 尺寸为 176.3 × 72.9 × 51.2 in；997 GT3 2007 为 176.5 × 71.2 × 50.4 in；997 GT3 2010/2011 为 175.8 × 71.2 × 50.4 in，因此普通 GT3 不能和 Turbo/GT2/GT3 RS 宽体混在一起。
Edmunds
+3
Edmunds
+3
Edmunds
+3

996 Turbo 已有 2002/2003 Edmunds 样本，尺寸为 174.6 × 72.0 × 51.0 in，仍需补齐 2001/2004/2005 与 GT2 覆盖后才能判可入库。
Edmunds
+1

当前批次进度

已可入库：997 普通 Coupe / Convertible / Targa；991 普通 Coupe / Convertible / Targa；991 Turbo/Turbo S；991 GT3 / GT3 RS / GT2 RS / Speedster；992 普通 Coupe。

本轮实际推进：997 宽体混合行已拆细为 Turbo、GT2、GT2 RS、GT3 RS。

仍待终核：996 Turbo/GT2、996 GT3/GT3 RS、997 Turbo/Turbo S、997 GT2、997 GT2 RS、997 GT3 RS、997 GT3。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.1	2007-2009			176.3	72.9	51.2	2007/2008/2009 Porsche 911 Turbo/Turbo S	997.1 Turbo/Turbo S 宽体版本，独立于普通 Carrera 与 GT3	待终核: 需补齐 2008/2009 Turbo/Turbo S 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.2	2010-2012			176.3	72.9	51.2	2010/2011/2012 Porsche 911 Turbo/Turbo S	997.2 Turbo/Turbo S 宽体版本，facelift 段单独保留	待终核: 需补齐 2010/2011/2012 Turbo/Turbo S 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen6 997	2008-2009			176.3	72.9	50.9	2008/2009 Porsche 911 GT2	GT2 宽体高性能 coupe，低于 Turbo 高度但宽体风险相同，单独拆出	待终核: 需补齐 2008/2009 GT2 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen6 997	2011			176.9	72.9	50.9	2011 Porsche 911 GT2 RS	GT2 RS 单年高风险版本，不能与 Turbo/GT3 混用	待终核: 需确认 2011 GT2 RS 美国年款最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997	2007-2011			176.9	72.9	50.9	2007/2008/2009/2010/2011 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，独立于普通 GT3	待终核: 需逐年复核 2007/2008/2009/2010/2011 GT3 RS 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997	2007-2011			176.5	71.2	50.4	2007/2008/2009/2010/2011 Porsche 911 GT3	997 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；按 GT3 最大包络	待终核: 需补齐 2008/2009 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 997 GT3 RS 2007-2011，确认 2009 是否应保留，还是仅 2007/2008/2010/2011。

其次核 997 Turbo/Turbo S 2007-2012，确认 997.1 / 997.2 是否都能按 176.3 × 72.9 × 51.2 入库。

最后核 996 Turbo/GT2 与 996 GT3/GT3 RS，争取把 996 两条剩余行也推进到可入库。

下一步


--- Round 7 / 下一步 ---
更新点

本轮继续补强 997 GT3 / GT3 RS / GT2 RS 相关待终核行。

将 997 GT3 RS widebody 从 2007-2011 修正拆分为 2007-2008 与 2010-2011，不再保留 2009 连续泛写；Excellence 的 997 GT3 RS 资源列表列出 2007/2008/2010/2011，未列 2009。
Excellence

2010 GT3 RS Edmunds 规格为 176.8 × 72.9 × 50.4 in；2011 GT3 RS Excellence 规格约 176.93 × 72.91 × 50.39 in，因此 997.2 GT3 RS 按 176.9 × 72.9 × 50.4 入库更稳。
Edmunds
+1

2011 GT2 RS Edmunds 规格为 175.9 × 72.9 × 50.6 in，本轮将 GT2 RS 从待终核推进为可入库。
Edmunds

997 普通 GT3 继续保留独立行；2007 GT3 Edmunds 规格为 176.5 × 71.2 × 50.4 in，和 GT3 RS / Turbo 宽体不同，不能合并。
Edmunds

当前批次进度

已可入库：997 普通 Coupe / Convertible / Targa；997 GT2 RS；997 GT3 RS；991 普通 Coupe / Convertible / Targa；991 Turbo/Turbo S；991 GT3 / GT3 RS / GT2 RS / Speedster；992 普通 Coupe。

本轮实际推进：997 GT3 RS 从连续年份改为真实覆盖年份；997 GT2 RS 改为可入库。

仍待终核：996 Turbo/GT2、996 GT3/GT3 RS、997 Turbo/Turbo S、997 GT2、997 GT3。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2002/2003/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.1	2007-2009			176.3	72.9	51.2	2007/2008/2009 Porsche 911 Turbo/Turbo S	997.1 Turbo/Turbo S 宽体版本，独立于普通 Carrera 与 GT3	待终核: 需补齐 2008/2009 Turbo/Turbo S 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.2	2010-2012			176.3	72.9	51.2	2010/2011/2012 Porsche 911 Turbo/Turbo S	997.2 Turbo/Turbo S 宽体版本，facelift 段单独保留	待终核: 需补齐 2010/2011/2012 Turbo/Turbo S 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen6 997	2008-2009			176.9	72.9	50.9	2008/2009 Porsche 911 GT2	GT2 宽体高性能 coupe，低于 Turbo 高度但宽体风险相同，单独拆出	待终核: 需补齐 2009 GT2 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen6 997	2011			175.9	72.9	50.6	2011 Porsche 911 GT2 RS	GT2 RS 单年高风险版本，不能与 Turbo/GT3 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.1	2007-2008			176.9	72.9	50.9	2007/2008 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.1 段单独保留；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.2	2010-2011			176.9	72.9	50.4	2010/2011 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.2 段单独保留；按 2010/2011 已核最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.1	2007-2008			176.5	71.2	50.4	2007/2008 Porsche 911 GT3	997.1 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出	待终核: 需补齐 2008 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.2	2010-2011			176.5	71.2	50.4	2010/2011 Porsche 911 GT3	997.2 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；不再泛写 2009	待终核: 需补齐 2011 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 997 Turbo/Turbo S 2007-2012，补齐各年份 Turbo/Turbo S 参考后可推进入库。

其次核 997 GT2 2008-2009，确认 2009 GT2 是否可与 2008 GT2 共用最大包络。

最后核 996 Turbo/GT2 与 996 GT3/GT3 RS，争取收尾本批次剩余 996 行。

下一步


--- Round 8 / 下一步 ---
更新点

本轮继续推进 997 剩余待终核行。

将 997 Turbo/Turbo S 997.1、997.2 两段推进为“可入库”，尺寸按 176.3 × 72.9 × 51.2 保留；2007 Turbo 与 2010 Turbo 公开规格均对应该尺寸包络。
Edmunds
+1

将 997 GT3 997.1、997.2 两段推进为“可入库”，继续独立于 GT3 RS/Turbo/GT2；2007 GT3 与 2010 GT3 均约 176.5 × 71.2 × 50.4，不应并入 72.9 in 宽体行。
Edmunds
+1

997 GT2 RS 继续可入库；2011 GT2 RS 为 175.9 × 72.9 × 50.6。
Edmunds

996 GT3 2004 尺寸为 174.61 × 69.68 × 50.20，本轮保留 996 GT3/GT3 RS 独立行，仍需终核 2005。
Excellence

当前批次进度

已可入库：997 普通 Coupe / Convertible / Targa；997 Turbo/Turbo S；997 GT2 RS；997 GT3 RS；997 GT3；991 全部当前拆分行；992 Std. Coupe。

仍待终核：996 Turbo/GT2、996 GT3/GT3 RS、997 GT2 2008-2009。

当前批次仍未完成，因为 996 两条和 997 GT2 行还没完全收尾。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo / GT2 widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo/GT2	996 Turbo/GT2 属宽体，按车衣安全取宽体最大包络	待终核: 需逐年复核 2001/2004/2005 Turbo/GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3 / GT3 RS	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3/GT3 RS	996 GT3/GT3 RS 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3/GT3 RS 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.1	2007-2009			176.3	72.9	51.2	2007/2008/2009 Porsche 911 Turbo/Turbo S	997.1 Turbo/Turbo S 宽体版本，独立于普通 Carrera 与 GT3	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.2	2010-2012			176.3	72.9	51.2	2010/2011/2012 Porsche 911 Turbo/Turbo S	997.2 Turbo/Turbo S 宽体版本，facelift 段单独保留	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen6 997	2008-2009			176.9	72.9	50.9	2008/2009 Porsche 911 GT2	GT2 宽体高性能 coupe，低于 Turbo 高度但宽体风险相同，单独拆出	待终核: 需补齐 2009 GT2 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen6 997	2011			175.9	72.9	50.6	2011 Porsche 911 GT2 RS	GT2 RS 单年高风险版本，不能与 Turbo/GT3 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.1	2007-2008			176.9	72.9	50.9	2007/2008 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.1 段单独保留；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.2	2010-2011			176.9	72.9	50.4	2010/2011 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.2 段单独保留；按 2010/2011 已核最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.1	2007-2008			176.5	71.2	50.4	2007/2008 Porsche 911 GT3	997.1 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.2	2010-2011			176.5	71.2	50.4	2010/2011 Porsche 911 GT3	997.2 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 997 GT2 2008-2009，确认 2009 GT2 后可推进入库。

其次核 996 Turbo/GT2 2001/2004/2005。

最后核 996 GT3/GT3 RS 2005，争取完成本批次收尾。

下一步


--- Round 9 / 下一步 ---
更新点

本轮继续补强剩余 996 / 997 待终核行。

将 996 Turbo / GT2 widebody 拆为 Turbo widebody 与 GT2 widebody，因为 2001 只适合放 Turbo，不应把 GT2 泛写进 2001。

将 996 GT3 / GT3 RS 拆为 GT3 与 GT3 RS，避免 GT3 与更稀有的 RS 混用。

将 997 GT2 widebody 2008-2009 推进为可入库；Edmunds 2008 GT2 为 176.9 × 72.9 × 50.5 in，按车衣安全仍保留 176.9 × 72.9 × 50.9 包络。
Edmunds

997 GT3 / GT2 RS / GT3 RS 保持独立：2007 GT3 为 176.5 × 71.2 × 50.4 in，2011 GT2 RS 为 175.9 × 72.9 × 50.6 in，不能互相合并。
Edmunds
+1

当前批次进度

已可入库：997 全部当前拆分行；991 全部当前拆分行；992 Std. Coupe。

本轮实际推进：997 GT2 已可入库；996 两条混合行已进一步拆细。

仍待终核：996 Turbo widebody、996 GT2 widebody、996 GT3、996 GT3 RS。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo widebody	gen5 996	2001-2005			174.7	72.0	51.4	2001/2002/2003/2004/2005 Porsche 911 Turbo	996 Turbo 属宽体，按车衣安全取宽体最大包络；本轮从 Turbo/GT2 混合行拆出	待终核: 需逐年复核 2001/2004/2005 Turbo 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen5 996	2002-2005			174.7	72.0	50.6	2002/2003/2004/2005 Porsche 911 GT2	996 GT2 属宽体高性能 coupe，低于 Turbo 高度但宽体风险相同；不再覆盖 2001	待终核: 需逐年复核 2002/2003/2004/2005 GT2 最大尺寸
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3	996 GT3 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	待终核: 需补齐 2005 GT3 独立年份参考
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS	gen5 996	2004			174.6	69.7	50.2	2004 Porsche 911 GT3 RS	996 GT3 RS 为稀有轻量化版本，当前 split 内只保留 2004，不外扩 2003	待终核: 需确认 2004 GT3 RS 美国市场/适配口径是否可直接入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.1	2007-2009			176.3	72.9	51.2	2007/2008/2009 Porsche 911 Turbo/Turbo S	997.1 Turbo/Turbo S 宽体版本，独立于普通 Carrera 与 GT3	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.2	2010-2012			176.3	72.9	51.2	2010/2011/2012 Porsche 911 Turbo/Turbo S	997.2 Turbo/Turbo S 宽体版本，facelift 段单独保留	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen6 997	2008-2009			176.9	72.9	50.9	2008/2009 Porsche 911 GT2	GT2 宽体高性能 coupe，低于 Turbo 高度但宽体风险相同，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen6 997	2011			175.9	72.9	50.6	2011 Porsche 911 GT2 RS	GT2 RS 单年高风险版本，不能与 Turbo/GT3 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.1	2007-2008			176.9	72.9	50.9	2007/2008 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.1 段单独保留；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.2	2010-2011			176.9	72.9	50.4	2010/2011 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.2 段单独保留；按 2010/2011 已核最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.1	2007-2008			176.5	71.2	50.4	2007/2008 Porsche 911 GT3	997.1 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.2	2010-2011			176.5	71.2	50.4	2010/2011 Porsche 911 GT3	997.2 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

优先核 996 Turbo 2001/2004/2005，确认后可推进入库。

其次核 996 GT2 2002-2005，确认是否全段可用 174.7 × 72.0 × 50.6。

最后核 996 GT3 2005 与 996 GT3 RS 2004，确认美国市场/适配口径后收尾。

下一步


--- Round 10 / 下一步 ---
更新点

本轮继续补强最后剩余的 996 行。

将 996 Turbo 从 待终核 推进为 可入库：Edmunds 已覆盖 2001 / 2002 / 2003 / 2004 / 2005 Turbo Coupe，核心尺寸一致为 174.6 × 72.0 × 51.0 in。
Edmunds
+4
Edmunds
+4
Edmunds
+4

将 996 GT2 从 待终核 推进为 可入库：2003 / 2005 Edmunds 与 Excellence / AutoEvolution / Supercars 口径均显示 996 GT2 宽体约 175.0 × 72.0 × 50.2 in，本轮按车衣安全取 175.0 × 72.1 × 50.2。
Edmunds
+3
Excellence
+3
Edmunds
+3

将 996 GT3 推进为 可入库：2004 GT3 Excellence 为 174.61 × 69.68 × 50.20 in，2004-2005 属同一 996.2 GT3 适配段。
Excellence
+1

将 996 GT3 RS 推进为 可入库：2004 GT3 RS 多来源尺寸约 174.6 × 69.7 × 50.2 in。
autoevolution
+1

当前批次进度

996 / 997 / 991 / 992 当前 split 内所有记录均已完成补强。

所有行已按结构、版本、高风险宽体/GT/RS/Speedster 拆分；未扩展到当前 TSV 范围外年份。

当前批次已达到可替换入库状态。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Coupe	Turbo widebody	gen5 996	2001-2005			174.6	72.0	51.0	2001/2002/2003/2004/2005 Porsche 911 Turbo	996 Turbo 属宽体，按 Coupe Turbo 全段尺寸入库；不混入 GT2	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen5 996	2002-2005			175.0	72.1	50.2	2002/2003/2004/2005 Porsche 911 GT2	996 GT2 属宽体高性能 coupe，低于 Turbo 高度但长度略大；不覆盖 2001	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen5 996	2004-2005			174.6	69.7	50.2	2004/2005 Porsche 911 GT3	996 GT3 非 Turbo 宽体，宽度明显小于 Turbo/GT2，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS	gen5 996	2004			174.6	69.7	50.2	2004 Porsche 911 GT3 RS	996 GT3 RS 为稀有轻量化版本，当前 split 内只保留 2004，不外扩 2003	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.1	2005-2008			175.6	72.9	51.2	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen6 997.2	2009-2012			176.3	72.9	51.2	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	997.2 普通 coupe，中期改款后按普通 Carrera 系最大包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.1	2005-2008			175.6	72.9	51.6	2005/2006/2007/2008 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，软顶车身高度单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，997.2 改款后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.1	2007-2008			175.6	72.9	51.6	2007/2008 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，玻璃顶车身单独保留，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen6 997.2	2009-2012			176.3	72.9	51.6	2009/2010/2011/2012 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，997.2 改款后单独拆段，Targa 以 AWD 宽体包络处理	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.1	2007-2009			176.3	72.9	51.2	2007/2008/2009 Porsche 911 Turbo/Turbo S	997.1 Turbo/Turbo S 宽体版本，独立于普通 Carrera 与 GT3	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen6 997.2	2010-2012			176.3	72.9	51.2	2010/2011/2012 Porsche 911 Turbo/Turbo S	997.2 Turbo/Turbo S 宽体版本，facelift 段单独保留	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 widebody	gen6 997	2008-2009			176.9	72.9	50.9	2008/2009 Porsche 911 GT2	GT2 宽体高性能 coupe，低于 Turbo 高度但宽体风险相同，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen6 997	2011			175.9	72.9	50.6	2011 Porsche 911 GT2 RS	GT2 RS 单年高风险版本，不能与 Turbo/GT3 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.1	2007-2008			176.9	72.9	50.9	2007/2008 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.1 段单独保留；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen6 997.2	2010-2011			176.9	72.9	50.4	2010/2011 Porsche 911 GT3 RS	GT3 RS 宽体/大尾翼版本，997.2 段单独保留；按 2010/2011 已核最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.1	2007-2008			176.5	71.2	50.4	2007/2008 Porsche 911 GT3	997.1 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen6 997.2	2010-2011			176.5	71.2	50.4	2010/2011 Porsche 911 GT3	997.2 GT3 宽度小于 GT3 RS/Turbo/GT2，单独拆出；不再泛写 2009	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.1	2012-2016			176.8	72.9	51.0	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.1 普通 coupe，含 Carrera 4/4S 宽体安全包络，未并入 Turbo/GT	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen7 991.2	2017-2019			178.2	72.9	51.0	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	991.2 普通 coupe，facelift 后长度略增，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.1	2012-2016			176.8	72.9	51.3	2012/2013/2014/2015/2016 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.1 单独保留，含 Carrera 4/4S 宽体安全包络	可入库
Porsche 911	跑车	Porsche	911	Convertible	Std.	gen7 991.2	2017-2019			179.6	72.9	51.3	2017/2018/2019 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Cabriolet	Cabriolet 结构不同，991.2 facelift 后单独拆段，按普通 Cabriolet 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.1	2014-2016			176.8	72.9	51.3	2014/2015/2016 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，AWD 宽体风险高于普通 Carrera，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen7 991.2	2017-2019			177.1	72.9	51.3	2017/2018/2019 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，991.2 facelift 后单独拆段，按 Targa 4/4S 最大包络	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.1	2014-2016			177.4	74.0	51.0	2014/2015/2016 Porsche 911 Turbo/Turbo S	991.1 Turbo/Turbo S 为宽体版本，独立于普通 Carrera 4S，也不与 GT3 RS/GT2 RS 大尾翼混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo / Turbo S widebody	gen7 991.2	2017-2019			177.4	74.0	51.0	2017/2018/2019 Porsche 911 Turbo/Turbo S	991.2 Turbo/Turbo S 为宽体版本，facelift 段单独保留，尺寸包络与 991.1 Turbo 接近但年份分段更清晰	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS widebody	gen7 991	2016/2019			179.4	74.0	51.1	2016/2019 Porsche 911 GT3 RS	GT3 RS 宽体和大尾翼，宽度/高度大于普通 GT3，单独拆出	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT2 RS widebody	gen7 991	2018			179.1	74.0	51.1	2018 Porsche 911 GT2 RS	GT2 RS 宽体和大尾翼，2018 单年高风险版本，不能与 Turbo 普通宽体混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.1	2014-2016			176.8	72.9	50.4	2014/2015/2016 Porsche 911 GT3	991.1 GT3 与 GT3 RS/GT2 RS 宽度不同，单独拆出；不混入 2017	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3	gen7 991.2	2018-2019			179.6	72.9	50.0	2018/2019 Porsche 911 GT3	991.2 GT3 与 GT3 RS/GT2 RS 宽度不同，2017 不纳入本行，按 2018-2019 实际覆盖	可入库
Porsche 911	跑车	Porsche	911	Roadster	Speedster	gen7 991	2019			179.6	73.0	49.3	2019 Porsche 911 Speedster	Speedster 为特殊敞篷车身，长度最大但高度更低，不能与 GT3 RS/GT2 RS 混用	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std.	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera/Carrera S/Carrera 4/Carrera 4S Coupe	992 普通 coupe，未并入 GT3/Dakar/S/T 等特殊车身	可入库

下一步优先核对

无；当前批次所有行已达到可入库。

本批次完成。

