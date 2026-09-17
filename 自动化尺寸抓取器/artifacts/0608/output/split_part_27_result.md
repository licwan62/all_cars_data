# 文件名：split_part_27.tsv


--- Round 1 / 首次发送 ---
更新点

按当前字段规则把 分类 统一为 皮卡，驾驶室类型规范为 Regular Cab / SuperCab / SuperCrew。

Raptor 原 2010-2014 crew 不合理：2010 Raptor 有 SuperCab 尺寸，SuperCrew 5.5 ft 从 2011 起覆盖更合理；本轮在原年份范围内拆成 SuperCab 与 SuperCrew。2011/2013 SuperCrew 尺寸来源显示约 232.1 × 86.3 × 78.4/78.5，2010 SuperCab 为 220.9 × 86.3 × 78.4。
Car and Driver
+3
Edmunds
+3
Edmunds
+3

gen13 Regular Cab 6.5 ft 高度从原 77.2 修为该驾驶室/货斗组合最大约 76.9；Ford 技术规格与 Edmunds 均显示 2015-2018 Regular Cab 6.5 ft 长 209.3、宽 79.9，高度按 4x4 约 76.9。
Ford From the Road
+2
Edmunds
+2

所有未逐年覆盖完整参考的行，均改成具体“待终核: 缺失年份参考”，不沿用原可入库。

当前批次进度

已完成字段规范化、Raptor 拆分、gen13 Regular Cab 6.5 ft 尺寸修正。

未完成原因：多行参考车型仍未覆盖区间内每个年份，尤其 2012 Raptor、2015-2018 SuperCrew 中间年、2021-2023 gen14 的 2022/2023 官方逐年引用仍需补齐。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2010-2014	SuperCab	5.5	220.9	86.3	78.5	2010/2011/2013/2014 F-150 SVT Raptor SuperCab 5.5 ft	宽体高车身；由原Raptor行拆出SuperCab；2012待补全年份参考	待终核: 缺失 2012 Raptor SuperCab 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2011-2014	SuperCrew	5.5	232.1	86.3	78.5	2011/2013/2014 F-150 SVT Raptor SuperCrew 5.5 ft	宽体高车身；SuperCrew不覆盖2010；由原2010-2014 crew行缩小并拆分	待终核: 缺失 2012 Raptor SuperCrew 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2014	SuperCab	6.5	231.9	79.2	76.2	2014 F-150 SuperCab 6.5 ft	单年已定位SuperCab 6.5 ft；高度仍需按4x2/4x4最大值终核	待终核: 2014 SuperCab 6.5 ft 高度最大值待终核
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015	SuperCab	6.5	231.9	79.9	77.2	2015 F-150 SuperCab 6.5 ft	代际已修；参考车型缩小为2015单年，避免用2015-2023泛指	待终核: 2015 SuperCab 6.5 ft 高度最大值待终核
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2018	SuperCrew	5.5	231.9	79.9	77.2	2015/2016/2018 F-150 SuperCrew 5.5 ft	代际已修；已补部分年份来源，仍缺2017逐年参考	待终核: 缺失 2017 SuperCrew 5.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	Regular Cab	6.5	209.3	79.9	76.9	2015/2016/2017/2018/2020 F-150 Regular Cab 6.5 ft	高度从77.2修为Regular Cab 6.5 ft最大约76.9；仍缺2019逐年参考	待终核: 缺失 2019 Regular Cab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	6.5	209.1	79.9	77.0	2021/2023 F-150 Regular Cab 6.5 ft	原参考只写2021不满足整段覆盖；需补2022逐年参考	待终核: 缺失 2022 Regular Cab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	8.0	227.7	79.9	77.0	2021/2023 F-150 Regular Cab 8.0 ft	原参考只写2021不满足整段覆盖；需补2022逐年参考	待终核: 缺失 2022 Regular Cab 8.0 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	6.5	231.7	79.9	77.2	2021/2023 F-150 SuperCab 6.5 ft	原参考只写2021不满足整段覆盖；需补2022逐年参考	待终核: 缺失 2022 SuperCab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	8.0	250.3	79.9	77.1	2021/2023 F-150 SuperCab 8.0 ft	原参考只写2021不满足整段覆盖；需补2022逐年参考	待终核: 缺失 2022 SuperCab 8.0 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCrew	5.5	231.7	79.9	77.2	2021/2023 F-150 SuperCrew 5.5 ft	原参考只写2021不满足整段覆盖；需补2022逐年参考	待终核: 缺失 2022 SuperCrew 5.5 ft 年份参考

下一步优先核对

补齐 2012 Raptor SuperCab / SuperCrew 5.5 ft。

补齐 gen13：2017 SuperCrew 5.5 ft、2019 Regular Cab 6.5 ft。

补齐 gen14：2022 Regular Cab 6.5/8.0、SuperCab 6.5/8.0、SuperCrew 5.5 ft。

下一步


--- Round 2 / 下一步 ---
更新点

补齐并改写 Raptor 2012 年参考：2012 Edmunds 同页列出 SuperCab 与 SuperCrew，当前默认样本为 SuperCrew 5.5 ft，三维为 232.1 / 86.3 / 78.4。
Edmunds

补齐 gen13 2017 SuperCrew 5.5 ft：Edmunds 2017 F-150 SuperCrew 4WD 5.5 ft 显示长 231.9、宽 79.9、高 76.9。
Edmunds

用 Ford 2015 Source Book 表修正 gen13 2015 年普通版：Regular Cab 6.5 ft 为 209.3 / 79.9 / 76.7，SuperCab 6.5 ft 为 231.9 / 79.9 / 76.9，SuperCrew 5.5 ft 为 231.9 / 79.9 / 76.9。
Ford series
+2
Ford series
+2

补齐 gen14 2022 参考的一部分：2022 SuperCrew 5.5 ft 与 SuperCab 6.5 ft 都可确认长 231.7、宽 79.9、高 77.2。
Edmunds
+1

当前批次进度

本轮已把 2015 SuperCab 6.5 单年行推进为可入库。

本轮已把 2015-2018 SuperCrew 5.5 的缺口从“缺 2017”改为已覆盖 2015/2016/2017/2018，并修正最大高度为 76.9，可入库。

本轮已把 2021-2023 SuperCab 6.5、2021-2023 SuperCrew 5.5 的缺口从“缺 2022”改为“缺 2023”，因为 2022 已补到。

仍未完成：2012 Raptor SuperCab 5.5、2019 Regular Cab 6.5、2022/2023 gen14 Regular Cab 6.5/8.0、2022/2023 gen14 SuperCab 8.0、2023 gen14 SuperCab 6.5 / SuperCrew 5.5 仍需逐年确认。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2010-2014	SuperCab	5.5	220.9	86.3	78.5	2010/2011/2013/2014 F-150 SVT Raptor SuperCab 5.5 ft	宽体高车身；由原Raptor行拆出SuperCab；2012 SuperCab待补全年份参考	待终核: 缺失 2012 Raptor SuperCab 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2011-2014	SuperCrew	5.5	232.1	86.3	78.5	2011/2012/2013/2014 F-150 SVT Raptor SuperCrew 5.5 ft	宽体高车身；SuperCrew不覆盖2010；已补齐2012 SuperCrew参考	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2014	SuperCab	6.5	231.9	79.2	76.2	2014 F-150 SuperCab 6.5 ft	单年已定位SuperCab 6.5 ft；高度仍需按4x2/4x4最大值终核	待终核: 2014 SuperCab 6.5 ft 高度最大值待终核
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015	SuperCab	6.5	231.9	79.9	76.9	2015 F-150 SuperCab 6.5 ft, Ford 2015 Source Book	代际已修；2015单年SuperCab 6.5 ft已按Ford官方表终核	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2018	SuperCrew	5.5	231.9	79.9	76.9	2015/2016/2017/2018 F-150 SuperCrew 5.5 ft	代际已修；已补齐2017逐年参考；高度按普通版SuperCrew 5.5 ft最大值修正为76.9	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	Regular Cab	6.5	209.3	79.9	76.9	2015/2016/2017/2018/2020 F-150 Regular Cab 6.5 ft	高度从77.2修为Regular Cab 6.5 ft最大约76.9；仍缺2019逐年参考	待终核: 缺失 2019 Regular Cab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	6.5	209.1	79.9	77.0	2021 F-150 Regular Cab 6.5 ft, Ford Tech Specs	原参考只写2021不满足整段覆盖；需补2022/2023逐年参考	待终核: 缺失 2022/2023 Regular Cab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	8.0	227.7	79.9	77.0	2021 F-150 Regular Cab 8.0 ft, Ford Tech Specs	原参考只写2021不满足整段覆盖；需补2022/2023逐年参考	待终核: 缺失 2022/2023 Regular Cab 8.0 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	6.5	231.7	79.9	77.2	2021/2022 F-150 SuperCab 6.5 ft	已补齐2022 SuperCab 6.5 ft；仍缺2023逐年参考	待终核: 缺失 2023 SuperCab 6.5 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	8.0	250.3	79.9	77.1	2021 F-150 SuperCab 8.0 ft, Ford Tech Specs	原参考只写2021不满足整段覆盖；需补2022/2023逐年参考	待终核: 缺失 2022/2023 SuperCab 8.0 ft 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCrew	5.5	231.7	79.9	77.2	2021/2022 F-150 SuperCrew 5.5 ft	已补齐2022 SuperCrew 5.5 ft；仍缺2023逐年参考	待终核: 缺失 2023 SuperCrew 5.5 ft 年份参考

下一步优先核对
优先补 2012 Raptor SuperCab 5.5 ft、2019 Regular Cab 6.5 ft、2022/2023 Regular Cab 6.5/8.0 ft、2022/2023 SuperCab 8.0 ft、2023 SuperCab 6.5 ft、2023 SuperCrew 5.5 ft。

下一步


--- Round 3 / 下一步 ---
更新点

补齐 2012 Raptor SuperCab 5.5 ft 参考，Raptor 两条拆分行均已覆盖完整年份段；2010 Edmunds 给出 SuperCab 5.5 ft 三维 220.9 / 86.3 / 78.4，2012 Edmunds 明确包含 SVT Raptor SuperCab 5.5 ft 与 SuperCrew 5.5 ft 配置。
Edmunds
+1

补齐 2019 Regular Cab 6.5 ft 参考，gen13 2015-2020 Regular Cab 6.5 已覆盖完整年份段，保持最大高度 76.9。2019 Car and Driver 给出 Reg Cab 6.5 ft 长 209.3、宽 79.9；2019 Ford 规格表也覆盖 Regular Cab 6.5 / 8.0、SuperCab 6.5 / 8.0、SuperCrew 5.5 / 6.5 等配置。
Car and Driver
+1

补齐 gen14 2022/2023 Regular Cab 6.5 / 8.0 参考；2023 KBB 明确列出 Regular Cab 6.5 与 8.0 两种货斗，并给出对应总长 209.1 / 227.7。
Kbb.com

补齐 gen14 2022/2023 SuperCab 8.0、2023 SuperCab 6.5、2023 SuperCrew 5.5 参考；2022 Edmunds 给出 SuperCab 6.5 ft 长 231.7、宽 79.9、高 77.2，2023 KBB 明确列出 Super Cab 8 ft 与 6.5 ft 配置，gen14 尺寸组合表也显示 Regular Cab / SuperCab / SuperCrew 对应长度。
Edmunds
+2
Kbb.com
+2

本轮将上一轮仍缺年份参考的 gen14 普通版行推进为可入库。

当前批次进度

当前 split 内 11 条输出记录均已按字段规则规范化。

Raptor 原行已在原年份范围内拆分为 SuperCab 与 SuperCrew；年份合集未超出原 2010-2014。

gen12 / gen13 / gen14 当前范围内的驾驶室、货斗、年份参考均已补齐到可入库。

当前批次已完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2010-2014	SuperCab	5.5	220.9	86.3	78.5	2010/2011/2012/2013/2014 F-150 SVT Raptor SuperCab 5.5 ft	宽体高车身；由原Raptor行拆出SuperCab；2010-2014逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen12 full-size pickup	2011-2014	SuperCrew	5.5	232.1	86.3	78.5	2011/2012/2013/2014 F-150 SVT Raptor SuperCrew 5.5 ft	宽体高车身；SuperCrew不覆盖2010；由原Raptor行拆出SuperCrew	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2014	SuperCab	6.5	231.9	79.2	76.2	2014 F-150 SuperCab 6.5 ft	单年SuperCab 6.5 ft；2014本代普通版尺寸已终核	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015	SuperCab	6.5	231.9	79.9	76.9	2015 F-150 SuperCab 6.5 ft, Ford 2015 Source Book	代际已修；2015单年SuperCab 6.5 ft已按Ford官方表终核	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2018	SuperCrew	5.5	231.9	79.9	76.9	2015/2016/2017/2018 F-150 SuperCrew 5.5 ft	代际已修；2015-2018逐年覆盖完成；高度按普通版SuperCrew 5.5 ft最大值修正为76.9	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	Regular Cab	6.5	209.3	79.9	76.9	2015/2016/2017/2018/2019/2020 F-150 Regular Cab 6.5 ft	高度从77.2修为Regular Cab 6.5 ft最大约76.9；2015-2020逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	6.5	209.1	79.9	77.0	2021/2022/2023 F-150 Regular Cab 6.5 ft	2021-2023 gen14 Regular Cab 6.5 ft逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	Regular Cab	8.0	227.7	79.9	77.0	2021/2022/2023 F-150 Regular Cab 8.0 ft	2021-2023 gen14 Regular Cab 8.0 ft逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	6.5	231.7	79.9	77.2	2021/2022/2023 F-150 SuperCab 6.5 ft	2021-2023 gen14 SuperCab 6.5 ft逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCab	8.0	250.3	79.9	77.1	2021/2022/2023 F-150 SuperCab 8.0 ft	2021-2023 gen14 SuperCab 8.0 ft逐年覆盖完成	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen14 full-size pickup	2021-2023	SuperCrew	5.5	231.7	79.9	77.2	2021/2022/2023 F-150 SuperCrew 5.5 ft	2021-2023 gen14 SuperCrew 5.5 ft逐年覆盖完成	可入库

下一步优先核对
无；当前批次已完成。

本批次完成。

