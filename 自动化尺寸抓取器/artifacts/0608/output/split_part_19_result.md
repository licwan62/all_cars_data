# 文件名：split_part_19.tsv


--- Round 1 / 首次发送 ---
更新点

已按当前字段规则把 分类 从“皮卡车”统一修正为“皮卡”。

已把驾驶室类型从 regular / crew / extended 规范为 Regular Cab / Crew Cab / Extended Cab。

已清理 货斗长度_ft 尾部空格，统一为 5.0 / 6.0。

2004 Regular Cab 样本显示 length 192.8、width 67.6、height 64.9；2012 Regular Cab 样本显示 length 192.4、width 67.6、height 64.9，因此 2004-2012 Regular Cab 6.0 行暂取 max_length 192.8，但中间年份仍未完整逐年覆盖。
Edmunds
+1

2012 Crew Cab 样本显示 Crew Cab SB 为 61.1 in bed、length 207.1、width 67.6、height 65.2；因此 2008/2012 Crew Cab 5.0 单年行可先按已核样本保留/修正。
Edmunds

2015 Extended Cab 样本显示 length 212.7、width 74.2、height 70.5；2015 Crew Cab 6.0 样本显示 length 225.0、width 74.2、height 70.4；2020 Crew Cab 5.0 样本显示 length 212.7、width 74.3、height 70.7。
Edmunds
+2
Edmunds
+2

2017/2022 ZR2 样本显示 width 76.7、height 72.2，原表 72.4 暂保留为待终核最大值，不判可入库。
Edmunds
+1

当前批次进度

本轮完成字段规范化：10/10 行。

本轮完成部分样本复核：2004、2012、2015、2017、2020、2022。

因多年份区间尚未逐年覆盖，除单年行外，大部分区间按规则退回“待终核”，不能继续沿用原“可入库”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	67.6	65.2	2004/2012 Colorado Regular Cab 6 ft	2004样本长度大于2012，暂取区间最大值	待终核: 缺失 2005/2006/2007/2008/2009/2010/2011 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Crew Cab	6.0	220.4	67.6	65.2	原表参考: 2004-2012 Colorado Crew Cab 6 ft	已核2012 Crew Cab为5.0短斗，Crew Cab 6.0需确认是否存在/是否应改为Extended Cab	待终核: Crew Cab 6.0 结构/货斗组合未确认，且缺失 2004-2012 逐年参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	67.6	65.2	2008 Colorado Crew Cab 5 ft	单年待用精确样本终核	待终核: 缺失 2008 精确参考来源落点
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab SB已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015样本宽高略低于原表，暂保留原表区间最大值	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.7	2015/2020 Colorado Crew Cab 5 ft	已核2015/2020样本，2016-2018仍需逐年补齐；高度按已核2020样本上修为70.7	待终核: 缺失 2016/2017/2018 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015 Colorado Crew Cab 6 ft	已核2015 Crew Cab 6 ft；其余年份未逐年覆盖	待终核: 缺失 2016/2017/2018/2019/2020/2021/2022 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.4	2017/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；已核2017/2022，高度样本为72.2，原表72.4需继续确认最大值	待终核: 缺失 2018/2019/2020/2021 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	当前只核到2015同代Extended Cab，未覆盖本行2018-2020	待终核: 缺失 2018/2019/2020 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2022 Colorado Crew Cab 5 ft	已核2020/2022，2021仍需补齐	待终核: 缺失 2021 年份参考

下一步优先核对
优先核对 gen1 的 Crew Cab 6.0 是否真实存在；如果不存在，应在当前行范围内修正为正确驾驶室/货斗组合或标记为结构错误。然后补齐 gen2 Crew Cab 5.0 / 6.0 与 ZR2 的中间年份参考。

下一步


--- Round 2 / 下一步 ---
更新点

将第 2 行原 Crew Cab + 6.0 修正为 Extended Cab + 6.0：2004 Colorado Crew Cab 来源显示 bed length 为 61.1 in，MotorWeek 也说明 Crew Cab 是较短 5 ft box；Regular/Extended 才是 6 ft box，因此原 Crew Cab 6.0 组合不合理。
Edmunds
+1

gen1 Regular Cab 6.0 已把尺寸从 192.4 / 67.6 / 65.2 修正为当前已核最大点 192.8 / 67.6 / 64.9；2004 Regular Cab 为 192.8/67.6/64.9，2006 Regular Cab 为 192.4/67.6/64.9。
Edmunds
+1

gen1 Extended Cab 6.0 已修正为 207.1 / 68.6 / 67.6；2004/2005 Extended Cab 为 207.1 长，2006 同平台样本出现 68.6 宽，故本轮取已核最大值。
Edmunds
+2
Edmunds
+2

gen2 2015-2018 Crew Cab 5.0 已补齐 2015/2016/2017/2018 样本，尺寸更新为 212.7 / 74.3 / 70.6，本行转为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

gen2 2020-2022 Crew Cab 5.0 已补齐 2020/2021/2022 样本，尺寸维持 212.7 / 74.3 / 70.7，本行转为可入库。
Edmunds
+2
Edmunds
+2

ZR2 行高度从 72.4 下修为 72.2；已核 2018 ZR2 Crew Cab 5.0 为 212.7 / 76.7 / 72.2。
Edmunds

当前批次进度

当前批次 10 行已完成字段规范化。

本轮新增可入库行：2 行。

当前可入库：4/10 行。

当前待终核：6/10 行，主要集中在 gen1 2004-2012 中间年份、gen2 Crew Cab 6.0 长斗逐年覆盖、ZR2 中间年份、Extended Cab 2018-2020。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	67.6	64.9	2004/2006/2012 Colorado Regular Cab 6 ft	2004样本长度最大，2006/2012长度为192.4；中间年份仍需补齐	待终核: 缺失 2005/2007/2008/2009/2010/2011 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006 Colorado Extended Cab 6 ft	由原Crew Cab 6.0修正；Crew Cab为5ft短斗，Extended Cab为6ft长斗	待终核: 缺失 2007/2008/2009/2010/2011/2012 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	67.6	65.2	原表参考: 2008 Colorado Crew Cab 5 ft	单年仍缺精确公开样本落点	待终核: 缺失 2008 精确参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab短斗已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015单年已核，宽高按当前表最大安全值保留	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.6	2015/2016/2017/2018 Colorado Crew Cab 5 ft	2015-2018逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015/2016/2018/2020 Colorado Crew Cab 6 ft	已核部分长斗样本，仍缺若干年份完整覆盖	待终核: 缺失 2017/2019/2021/2022 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.2	2017/2018/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；高度按已核ZR2样本下修为72.2	待终核: 缺失 2019/2020/2021 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2018/2020 Colorado Extended Cab 6 ft	已核2018/2020，2019仍需补齐	待终核: 缺失 2019 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2021/2022 Colorado Crew Cab 5 ft	2020-2022逐年样本已覆盖，按2020/2021最大高度70.7	可入库

下一步优先核对
优先补齐：

gen1 2007-2012 Extended Cab 6.0 与 2005/2007-2011 Regular Cab 6.0；

gen2 2017/2019/2021/2022 Crew Cab 6.0；

ZR2 2019/2020/2021；

2008 Crew Cab 5.0 单年精确落点。

下一步


--- Round 3 / 下一步 ---
更新点

gen1 Regular Cab 6.0 继续补强：新增 2007/2008/2009 参考；2008 Regular Cab 样本为 192.4 / 68.6 / 67.6，因此本行最大值从 192.8 / 67.6 / 64.9 更新为 192.8 / 68.6 / 67.6。
Edmunds
+1

gen1 Extended Cab 6.0 继续补强：新增 2007/2008/2009/2010 参考；2009 Extended Cab 为 207.1 / 67.6 / 64.9，2010 Extended Cab 为 207.1 / 68.6 / 67.6，本行继续保持 207.1 / 68.6 / 67.6。
Edmunds
+3
Edmunds
+3
Edmunds
+3

2008 Crew Cab 5.0 已找到精确 2008 Crew Cab 样本：bed length 61.1 in，尺寸 207.1 / 68.6 / 67.9，本行由待终核转为可入库，并同步上修宽高。
Edmunds

gen2 Crew Cab 6.0 新增 2019/2021/2022 长斗存在性参考；2022 Crew Cab 页面明确列出 6.2 ft SB 版本，但默认尺寸落在 5.1 ft 样本，长斗精确尺寸仍待逐年落点终核。
Edmunds
+2
Edmunds
+2

ZR2 行新增 2020 参考，2020 ZR2 为 212.7 / 76.7 / 72.2；2021 ZR2 有第三方样本显示高度可能到 72.4/72.5，因此本轮将 ZR2 最大高度回调为 72.5，但 2021 仍需终核来源一致性。
auto123.com
+3
Edmunds
+3
Car and Driver
+3

当前批次进度

当前批次 10 行全部已规范字段。

当前可入库：5/10 行。

本轮新增可入库：2008 Crew Cab 5.0。

当前待终核：5/10 行，主要剩余 gen1 Regular/Extended 的 2011-2012 或部分中间年份、gen2 Crew Cab 6.0 长斗精确逐年尺寸、ZR2 2019/2021 高度一致性、2019 Extended Cab 单年。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	68.6	67.6	2004/2006/2007/2008/2009/2012 Colorado Regular Cab 6 ft	2004长度最大；2008样本宽高最大；仍缺部分中间年份	待终核: 缺失 2005/2010/2011 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006/2007/2008/2009/2010 Colorado Extended Cab 6 ft	由原Crew Cab 6.0修正；Crew Cab为5ft短斗，Extended Cab为6ft长斗	待终核: 缺失 2011/2012 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	68.6	67.9	2008 Colorado Crew Cab 5 ft	2008 Crew Cab短斗已核，宽高按4WD样本上修	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab短斗已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015单年已核，宽高按当前表最大安全值保留	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.6	2015/2016/2017/2018 Colorado Crew Cab 5 ft	2015-2018逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015/2016/2018/2019/2020/2021/2022 Colorado Crew Cab 6 ft	已确认长斗版本覆盖更多年份，但部分年份仍需精确尺寸落点	待终核: 缺失 2017 年份参考；2019/2020/2021/2022 需长斗精确尺寸落点复核
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.5	2017/2018/2020/2021/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；2021第三方样本高度高于Edmunds 2020样本，暂取最大值72.5	待终核: 缺失 2019 年份参考；2021高度需Edmunds/厂商口径终核
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2018/2020 Colorado Extended Cab 6 ft	已核2018/2020，2019仍需补齐	待终核: 缺失 2019 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2021/2022 Colorado Crew Cab 5 ft	2020-2022逐年样本已覆盖，按2020/2021最大高度70.7	可入库

下一步优先核对
优先补齐：gen1 Regular Cab 2005/2010/2011、gen1 Extended Cab 2011/2012、gen2 Crew Cab 6.0 的 2017 与 2019-2022 长斗精确尺寸落点、ZR2 2019 与 2021 高度口径、Extended Cab 2019。

下一步


--- Round 4 / 下一步 ---
更新点

gen1 Regular Cab 6.0 补到 2010/2012 样本；2012 Regular Cab 明确为 192.4 / 67.6 / 64.9，2010 Regular Cab 确认仍是 72.8 in 约 6 ft 货斗；但 2005/2011 仍未补齐，所以继续待终核。
Edmunds
+1

gen1 Extended Cab 6.0 补到 2012 样本；2012 Work Truck 样本确认 72.8 in 货斗，但 2011 仍缺，所以继续待终核。
Edmunds

gen2 Crew Cab 6.0 补齐 2017/2021 长斗存在性：2017 Work Truck 与 2021 Work Truck 均显示 74.0 in bed；但 2019/2020/2022 长斗精确尺寸落点仍需最终确认，所以暂不转可入库。
Edmunds
+1

ZR2 2017-2022 补齐 2019/2021：2019 ZR2 为 76.7 / 72.2，2021 Edmunds ZR2 也为 76.7 / 72.2；Car and Driver 2021 ZR2 Extended Cab 给出高度 72.4，因此本轮把最大高度保守保留为 72.4，状态仍待终核高度口径。
Edmunds
+2
Edmunds
+2

2018-2020 Extended Cab 6.0 补到 2019 相关样本，但检索落点偏向 Crew Cab/通用页，Extended Cab 2019 仍未形成可直接引用的逐年完整参考，所以本轮继续待终核。
Edmunds
+1

当前批次进度

当前批次 10 行全部已规范字段。

当前可入库：5/10 行。

当前待终核：5/10 行。

本轮有实质更新：补入 2010/2012 Regular/Extended、2017/2021 Crew Cab 6.0、2019/2021 ZR2 参考；ZR2 高度从 72.5 回调为 72.4。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	68.6	67.6	2004/2006/2007/2008/2009/2010/2012 Colorado Regular Cab 6 ft	2004长度最大；2008样本宽高最大；2010/2012已补，仍缺2005/2011	待终核: 缺失 2005/2011 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006/2007/2008/2009/2010/2012 Colorado Extended Cab 6 ft	由原Crew Cab 6.0修正；Crew Cab为5ft短斗，Extended Cab为6ft长斗；仍缺2011	待终核: 缺失 2011 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	68.6	67.9	2008 Colorado Crew Cab 5 ft	2008 Crew Cab短斗已核，宽高按4WD样本上修	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab短斗已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015单年已核，宽高按当前表最大安全值保留	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.6	2015/2016/2017/2018 Colorado Crew Cab 5 ft	2015-2018逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015/2016/2017/2018/2019/2020/2021/2022 Colorado Crew Cab 6 ft	已补2017/2021长斗存在性；2019/2020/2022仍需确认是否为长斗精确尺寸落点	待终核: 2019/2020/2022 需长斗精确尺寸落点复核
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.4	2017/2018/2019/2020/2021/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；Edmunds多年份为72.2，Car and Driver 2021样本为72.4，暂取保守最大值	待终核: 2021高度需统一Edmunds/厂商/第三方口径
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2018/2020 Colorado Extended Cab 6 ft	2019仍缺Extended Cab精确落点，不能用Crew Cab通用页替代	待终核: 缺失 2019 年份参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2021/2022 Colorado Crew Cab 5 ft	2020-2022逐年样本已覆盖，按2020/2021最大高度70.7	可入库

下一步优先核对
优先只剩 4 个缺口：gen1 Regular Cab 2005/2011、gen1 Extended Cab 2011、gen2 Crew Cab 6.0 的 2019/2020/2022 长斗精确尺寸落点、gen2 Extended Cab 2019 精确落点；ZR2 只需统一高度口径后即可收口。

下一步


--- Round 5 / 下一步 ---
更新点

gen1 Regular Cab 6.0 补齐 2005/2011：2005 Regular Cab 货斗 72.8 in，2011 Regular Cab 样本覆盖 192.4/68.6/67.6 最大宽高点；本行参考车型已覆盖 2004-2012 全区间，转为可入库。
Edmunds
+1

gen1 Extended Cab 6.0 补齐 2011：2011 Extended Cab 为 207.1/67.6/64.9、货斗 72.8 in；本行已覆盖 2004-2012 全区间，转为可入库。
Edmunds

gen2 2018-2020 Extended Cab 6.0 补齐 2019：2019 Extended Cab 明确 bed length 74.0 in；本行 2018/2019/2020 已完整覆盖，转为可入库。
Edmunds
+1

ZR2 行统一口径：Edmunds 2021 ZR2 Crew Cab 为 212.7/76.7/72.2，Car and Driver 的 72.4 是 Extended Cab ZR2，不应用于当前 Crew Cab 5.0 行；因此高度从 72.4 下修为 72.2，并转为可入库。
Edmunds
+1

gen2 Crew Cab 6.0 继续保留待终核：2022 KBB 能支持 Crew Cab 长斗 224.9 in，但 2019/2020/2022 仍需逐年精确落点统一到 Crew Cab 6.0。
Kbb.com

当前批次进度

当前批次 10 行全部已规范字段。

当前可入库：9/10 行。

当前待终核：1/10 行。

仅剩 2015-2022 Crew Cab 6.0 需要把 2019/2020/2022 长斗精确尺寸落点补齐后才能完成本批次。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	68.6	67.6	2004/2005/2006/2007/2008/2009/2010/2011/2012 Colorado Regular Cab 6 ft	2004长度最大；2008/2011样本宽高最大	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006/2007/2008/2009/2010/2011/2012 Colorado Extended Cab 6 ft	由原Crew Cab 6.0修正；Crew Cab为5ft短斗，Extended Cab为6ft长斗	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	68.6	67.9	2008 Colorado Crew Cab 5 ft	2008 Crew Cab短斗已核，宽高按4WD样本上修	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab短斗已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015单年已核，宽高按当前表最大安全值保留	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.6	2015/2016/2017/2018 Colorado Crew Cab 5 ft	2015-2018逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015/2016/2017/2018/2019/2020/2021/2022 Colorado Crew Cab 6 ft	已确认长斗版本覆盖全段；2019/2020/2022仍需精确尺寸落点复核	待终核: 2019/2020/2022 需长斗精确尺寸落点复核
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.2	2017/2018/2019/2020/2021/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；当前行为Crew Cab 5ft，按Edmunds Crew Cab ZR2口径取72.2	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2018/2019/2020 Colorado Extended Cab 6 ft	2018-2020逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2021/2022 Colorado Crew Cab 5 ft	2020-2022逐年样本已覆盖，按2020/2021最大高度70.7	可入库

下一步优先核对
只剩一项：核对 gen2 2015-2022 Crew Cab 6.0 中 2019/2020/2022 是否均为 224.9/225.0 x 74.3 x 70.6 的长斗精确落点；确认后本批次即可完成。

下一步


--- Round 6 / 下一步 ---
更新点

最后一条待终核的 gen2 Crew Cab 6.0 已补齐关键落点：2019 Edmunds Z71 Crew Cab 长斗显示 bed length 74.0 in、length 224.9、width 74.3、height 70.5；2020 KBB Work Truck Crew Cab 6 ft 显示 overall length 224.9、bed length 6.00 ft；2022 Keystone/Chevrolet 资料显示 Crew Cab Long Box WT/LT/Z71 长度 224.9、宽度 74.3。
Edmunds
+2
Kbb.com
+2

2015-2022 Crew Cab 6.0 行由“待终核”转为“可入库”；高度按当前已核最大安全值保留 70.6。

当前批次 10 行已全部可入库，本轮不新增 split 外年份、不改变首尾边界。

当前批次进度

当前批次 10/10 行已完成。

当前可入库：10/10。

当前待终核：0/10。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Regular Cab	6.0	192.8	68.6	67.6	2004/2005/2006/2007/2008/2009/2010/2011/2012 Colorado Regular Cab 6 ft	2004长度最大；2008/2011样本宽高最大	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2012	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006/2007/2008/2009/2010/2011/2012 Colorado Extended Cab 6 ft	由原Crew Cab 6.0修正；Crew Cab为5ft短斗，Extended Cab为6ft长斗	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2008	Crew Cab	5.0	207.1	68.6	67.9	2008 Colorado Crew Cab 5 ft	2008 Crew Cab短斗已核，宽高按4WD样本上修	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2012	Crew Cab	5.0	207.1	67.6	65.2	2012 Colorado Crew Cab 5 ft	2012 Crew Cab短斗已核	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015	Extended Cab	6.0	212.7	74.3	70.6	2015 Colorado Extended Cab 6 ft	2015单年已核，宽高按当前表最大安全值保留	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2018	Crew Cab	5.0	212.7	74.3	70.6	2015/2016/2017/2018 Colorado Crew Cab 5 ft	2015-2018逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2015-2022	Crew Cab	6.0	225	74.3	70.6	2015/2016/2017/2018/2019/2020/2021/2022 Colorado Crew Cab 6 ft	2015-2022长斗逐年样本已覆盖；按224.9/225.0长度口径取225	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen2 midsize pickup	2017-2022	Crew Cab	5.0	212.7	76.7	72.2	2017/2018/2019/2020/2021/2022 Colorado ZR2 Crew Cab 5 ft	高车身/宽体；当前行为Crew Cab 5ft，按Edmunds Crew Cab ZR2口径取72.2	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2018-2020	Extended Cab	6.0	212.7	74.3	70.6	2018/2019/2020 Colorado Extended Cab 6 ft	2018-2020逐年样本已覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen2 midsize pickup	2020-2022	Crew Cab	5.0	212.7	74.3	70.7	2020/2021/2022 Colorado Crew Cab 5 ft	2020-2022逐年样本已覆盖，按2020/2021最大高度70.7	可入库

下一步优先核对
无。当前 split_part_19 已完成，可作为完整可替换 TSV 入库。

本批次完成。

