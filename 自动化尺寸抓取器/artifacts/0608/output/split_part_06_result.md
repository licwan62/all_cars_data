# 文件名：split_part_06.tsv


--- Round 1 / 首次发送 ---
更新点

CLA AMG 行补入二代 AMG 最大尺寸边界；但 2026 CLA45 S Final Edition 未完成逐年尺寸闭环，仍保留待终核。2025 AMG CLA35 的 Edmunds 尺寸为 184.8 / 73.1 / 55.3，可作为本轮二代 AMG 边界参考之一。
Edmunds

CLA EV / EQ Technology 行补入新一代 CLA EV 官方/Edmunds 已公开尺寸边界；但输入年份为 2027，当前可查到美国页更偏 2026 CLA 250+，所以不能判可入库。MBUSA/Edmunds 均显示新一代 CLA EV 尺寸约 185.9 / 73.0 / 57.8。
梅赛德斯-奔驰
+1

CLS gen1 标准版与 AMG 版拆开尺寸：标准 CLS500/CLS550 取 193.3 长，AMG 取 194.0 长；2006 Edmunds 可支持这一差异。
Edmunds
+1

CLC 行保持别名/不入库，不强行补尺寸，不并入当前可入库表。

当前批次进度

本轮已补强尺寸：CLA AMG、CLA EV、CLS gen1/gen2/gen3、E-Class W124。

仍未完成：CLA 2026 AMG、CLA 2027 美国年款确认、CLS 2012-2018/2019-2023 逐年参考闭环、E-Class 1994-1995 逐年来源闭环。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45	AMG 包围需核；2026 CLA45 S Final Edition 仍属二代末期	待终核: 缺失 2026 AMG CLA35/CLA45/CLA45 S Final Edition 年款尺寸参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2026 Mercedes-Benz CLA 250+ EV / 2027 Mercedes-Benz CLA EV-Hybrid preview	新一代 CLA EV/Hybrid 美国上市节奏待确认；不并入 2026 二代	待终核: 输入为 2027，但美国公开尺寸主要对应 2026 CLA 250+，需确认 2027 美国销售年款
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.7	2012/2013/2014/2015/2016/2017/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	待终核: 需继续复核 2015/2016/2017/2018 是否与 2012-2014 尺寸完全一致
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			194.5	74.1	55.7	2012/2013/2014 Mercedes-AMG CLS63	AMG 需核尺寸边界	待终核: 缺失 2015/2016/2017/2018 AMG CLS63 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			196.4	74.1	56.3	2019/2020/2021/2022/2023 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产	待终核: 需继续复核 2020/2021/2022/2023 是否与 2019 尺寸完全一致
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2023			196.4	74.1	56.3	2019 Mercedes-AMG CLS53	AMG 53 包围/高度需核	待终核: 缺失 2020/2021/2022/2023 AMG CLS53 年款尺寸参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	待终核: 需继续复核 1994/1995 E-Class Sedan 美国规格尺寸来源闭环

下一步优先核对
优先补 CLS gen2/gen3 中间年份闭环，再核 CLA 2026 AMG 与 2027 CLA 美国年款，最后核 W124 E-Class 1994/1995 官方或权威尺寸来源。

下一步


--- Round 2 / 下一步 ---
更新点

补齐 2026 AMG CLA35 / CLA45 S 官方与 Edmunds 尺寸，CLA AMG 行由“缺失 2026”推进为可入库；2026 AMG CLA35/CLA45 S 均为 184.8 in 长、73.1 in 不含镜宽，CLA45 S 高 55.4 in。
Edmunds
+3
梅赛德斯-奔驰
+3
梅赛德斯-奔驰
+3

修正 CLS gen2 AMG CLS63：2015 AMG CLS63 长度为 196.7 in，高于标准版 194.5 in，因此 AMG gen2 最大长度上调到 196.7。
Edmunds

修正 CLS gen3 标准版 / AMG CLS53：2019/2020/2022 数据显示 gen3 不能继续用 196.4 作为最大长度，标准版最大长度上调到 199.1；AMG CLS53 按 AMG 尺寸上调到 199.1 / 74.6 / 56.0。
梅赛德斯-奔驰媒体
+3
Edmunds
+3
Edmunds
+3

E-Class 1994-1995 Sedan 已补齐 1994/1995 sedan 逐年参考，尺寸保持 187.2 / 68.5 / 56.3，可入库。
Edmunds
+1

当前批次进度

已推进为可入库：CLA AMG、CLS gen1 标准版、CLS gen1 AMG、E-Class 1994-1995 Sedan。

仍待终核：CLA 2027 EV 美国年款、CLS gen2 标准版中间年份闭环、CLS gen2 AMG 2016-2018、CLS gen3 标准版 2021/2023、CLS gen3 AMG 2021-2023。

CLC 保持“别名/不入库”，不强行补尺寸。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45; 2026 Mercedes-AMG CLA35/CLA45 S	AMG 包围已按 CLA45 S 高度边界取值；2026 CLA45 S Final Edition 属二代末期	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2026 Mercedes-Benz CLA 250+ EV / 2027 Mercedes-Benz CLA EV-Hybrid preview	新一代 CLA EV/Hybrid 美国上市节奏待确认；不并入 2026 二代	待终核: 输入为 2027，但美国公开尺寸主要对应 2026 CLA 250+，需确认 2027 美国销售年款
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.8	2012/2013/2014/2015/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	待终核: 缺失 2016/2017 标准 CLS 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			196.7	74.1	55.7	2012/2013/2014/2015 Mercedes-AMG CLS63	AMG 2015 长度高于标准版，已按 AMG 边界取值	待终核: 缺失 2016/2017/2018 AMG CLS63 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			199.1	74.4	56.6	2019/2020/2022 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产	待终核: 缺失 2021/2023 标准 CLS 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2023			199.1	74.6	56.0	2019/2020 Mercedes-AMG CLS53	AMG 53 包围/高度已按官方 AMG CLS53 边界取值	待终核: 缺失 2021/2022/2023 AMG CLS53 年款尺寸参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	可入库

下一步优先核对
优先补 CLS gen2 标准版 2016/2017、CLS gen2 AMG 2016/2017/2018，再补 CLS gen3 2021/2023 标准版 与 2021/2022/2023 AMG CLS53，最后确认 2027 CLA EV / EQ Technology 是否已有美国销售年款尺寸。

下一步


--- Round 3 / 下一步 ---
更新点

CLS gen2 标准版 2016/2017 已补入逐年参考，2016/2017 Edmunds 均显示长度 194.5、高度 55.8；结合前后年份，标准版 2012-2018 可闭环。
Edmunds
+2
Edmunds
+2

CLS gen2 AMG CLS63 2018 已补入，2018 AMG CLS63 S 长度 196.7、高度 55.4；AMG 行仍缺 2016/2017 的 AMG 尺寸闭环，所以不能可入库。
Edmunds

CLS gen3 标准版 2021/2022/2023 已补入；2021 标准页为 196.4 / 73.9 / 56.3，2022/2023 为 198.8 / 73.8 / 56.6，结合 2019 最大长度 199.1，整段标准版最大值保持 199.1 / 74.4 / 56.6。
Edmunds
+3
Edmunds
+3
Edmunds
+3

CLS gen3 AMG CLS53 2021 已补入，2021 AMG CLS53 为 199.1 / 74.6 / 56.0；仍缺 2022/2023 AMG 年款尺寸或销售确认。
Edmunds

当前批次进度

已可入库：CLA AMG、CLS gen1 标准版、CLS gen1 AMG、CLS gen2 标准版、CLS gen3 标准版、E-Class 1994-1995 Sedan。

仍待终核：CLA 2027 EV 美国年款、CLS gen2 AMG 2016/2017、CLS gen3 AMG 2022/2023。

CLC 保持“别名/不入库”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45; 2026 Mercedes-AMG CLA35/CLA45 S	AMG 包围已按 CLA45 S 高度边界取值；2026 CLA45 S Final Edition 属二代末期	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2026 Mercedes-Benz CLA 250+ EV / 2027 Mercedes-Benz CLA EV-Hybrid preview	新一代 CLA EV/Hybrid 美国上市节奏待确认；不并入 2026 二代	待终核: 输入为 2027，但美国公开尺寸主要对应 2026 CLA 250+，需确认 2027 美国销售年款
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.8	2012/2013/2014/2015/2016/2017/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			196.7	74.1	55.7	2012/2013/2014/2015/2018 Mercedes-AMG CLS63	AMG 2015/2018 长度高于标准版，已按 AMG 边界取值	待终核: 缺失 2016/2017 AMG CLS63 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			199.1	74.4	56.6	2019/2020/2021/2022/2023 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产；已按 2019 长度与 2022-2023 高度边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2023			199.1	74.6	56.0	2019/2020/2021 Mercedes-AMG CLS53	AMG 53 包围/高度已按官方 AMG CLS53 边界取值	待终核: 缺失 2022/2023 AMG CLS53 年款尺寸参考或停售信息确认
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	可入库

下一步优先核对
优先补 2016/2017 AMG CLS63，再确认 2022/2023 AMG CLS53 是否美国继续销售或应缩短年份，最后确认 2027 CLA EV / EQ Technology 美国销售年款。

下一步


--- Round 4 / 下一步 ---
更新点

CLS gen2 AMG CLS63 补入 2017 与 2018 AMG CLS63 S 尺寸，均为 196.7 长、55.4 高；2016 仍未找到独立 AMG CLS63 年款尺寸页，所以该行继续待终核，但参考车型已从 2012/2013/2014/2015/2018 推进到 2012/2013/2014/2015/2017/2018。
Edmunds
+1

CLS gen3 AMG CLS53 核到北美 2022 model year 起 AMG CLS53 不再提供，输入原行 2019-2023 的 AMG 年份范围明显过宽；因此本轮按当前行原范围内“缩小年份”规则，将 AMG CLS53 行缩小为 2019-2021。
Mercedes-Benz of Washington
+2
Edmunds
+2

CLS gen3 AMG CLS53 缩短为 2019-2021 后，参考年份已覆盖 2019/2020/2021，状态推进为可入库。

CLA EV / EQ Technology 仍不能按 2027 可入库：当前公开美国页主要对应新一代 CLA 250+ EV，而输入年份为 2027，仍需后续确认 2027 美国销售年款。

当前批次进度

已可入库：CLA AMG、CLS gen1 标准版、CLS gen1 AMG、CLS gen2 标准版、CLS gen3 标准版、CLS gen3 AMG 2019-2021、E-Class 1994-1995 Sedan。

仍待终核：CLA 2027 EV 美国年款、CLS gen2 AMG 2016。

CLC 保持“别名/不入库”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45; 2026 Mercedes-AMG CLA35/CLA45 S	AMG 包围已按 CLA45 S 高度边界取值；2026 CLA45 S Final Edition 属二代末期	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2026 Mercedes-Benz CLA 250+ EV / 2027 Mercedes-Benz CLA EV-Hybrid preview	新一代 CLA EV/Hybrid 美国上市节奏待确认；不并入 2026 二代	待终核: 输入为 2027，但美国公开尺寸主要对应 2026 CLA 250+，需确认 2027 美国销售年款
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.8	2012/2013/2014/2015/2016/2017/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			196.7	74.1	55.7	2012/2013/2014/2015/2017/2018 Mercedes-AMG CLS63	AMG 2015/2017/2018 长度高于标准版，已按 AMG 边界取值	待终核: 缺失 2016 AMG CLS63 年款尺寸参考
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			199.1	74.4	56.6	2019/2020/2021/2022/2023 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产；已按 2019 长度与 2022-2023 高度边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2021			199.1	74.6	56.0	2019/2020/2021 Mercedes-AMG CLS53	AMG CLS53 北美 2022 起不再提供，当前 split 原 2019-2023 范围内缩小为 2019-2021	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	可入库

下一步优先核对
优先补 2016 AMG CLS63 独立年款尺寸页；若无法找到独立来源，可用 Mercedes-Benz 2016 CLS-Class 官方规格页交叉确认 AMG/非 AMG 宽高差异。之后再确认 2027 CLA EV / EQ Technology 是否已有美国销售年款页。

下一步


--- Round 5 / 下一步 ---
更新点

CLS gen2 AMG CLS63 补齐 2016 独立年款尺寸页；2016 Edmunds AMG CLS63 S 显示 Length 196.7、Height 55.4，至此 2012/2013/2014/2015/2016/2017/2018 全段参考闭环，可入库。
Edmunds

CLS gen2 AMG CLS63 高度最大值从 55.7 修正为 55.4；前轮/包围不影响车衣三维边界，长度仍取 196.7。

CLA EV / EQ Technology 行仍不能按 2027 可入库；当前可确认的是 2026 CLA 250+ EV / 新一代 CLA 预告信息，输入年份 2027 仍缺美国年款闭环。

本轮后只剩 CLA 2027 EV / EQ Technology 待终核；其他可入库或不入库状态已明确。

当前批次进度

可入库：8 行。

别名/不入库：1 行。

待终核：1 行，仅 Mercedes-Benz CLA-Class EV / EQ Technology 2027。

当前批次尚未全部完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45; 2026 Mercedes-AMG CLA35/CLA45 S	AMG 包围已按 CLA45 S 高度边界取值；2026 CLA45 S Final Edition 属二代末期	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2026 Mercedes-Benz CLA 250+ EV / 2027 Mercedes-Benz CLA EV-Hybrid preview	新一代 CLA EV/Hybrid 美国上市节奏待确认；不并入 2026 二代	待终核: 输入为 2027，但美国公开尺寸主要对应 2026 CLA 250+，需确认 2027 美国销售年款
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.8	2012/2013/2014/2015/2016/2017/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			196.7	74.1	55.4	2012/2013/2014/2015/2016/2017/2018 Mercedes-AMG CLS63	AMG 2015-2018 长度高于标准版，已按 AMG 边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			199.1	74.4	56.6	2019/2020/2021/2022/2023 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产；已按 2019 长度与 2022-2023 高度边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2021			199.1	74.6	56.0	2019/2020/2021 Mercedes-AMG CLS53	AMG CLS53 北美 2022 起不再提供，当前 split 原 2019-2023 范围内缩小为 2019-2021	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	可入库

下一步优先核对
只剩 Mercedes-Benz CLA-Class EV / EQ Technology 2027-2027：需要确认美国 2027 model year 是否正式销售，以及 2027 年款尺寸是否沿用 2026 CLA 250+ EV 的 185.9 / 73.0 / 57.8。

下一步


--- Round 6 / 下一步 ---
更新点

Mercedes-Benz CLA-Class EV / EQ Technology 已找到 MBUSA 2027 build 页面，车型名称为 2027 CLA 350 4MATIC ELECTRIC Sedan，说明 2027 美国年款已进入官方配置页；因此该行不再按“美国销售年款待确认”处理。
梅赛德斯-奔驰

尺寸仍采用 MBUSA / MBUSA media / Edmunds 对新一代 CLA Electric 已公开的 185.9 / 73.0 / 57.8；MBUSA 2026 CLA 250+ 与 CLA 350 4MATIC Electric 均显示同一套外部尺寸，MBUSA media quick reference 也给出 185.9 长、73 without mirrors、57.8 高。
梅赛德斯-奔驰
+2
梅赛德斯-奔驰
+2

CLA EV / EQ Technology 行参考车型改为 2027 Mercedes-Benz CLA 350 4MATIC ELECTRIC Sedan; 2026 CLA 250+ EV / CLA 350 4MATIC EV dimensions，状态推进为可入库。

当前批次剩余普通记录均已明确为“可入库”或“别名/不入库”，没有继续待终核项。

当前批次进度

可入库：9 行。

别名/不入库：1 行。

待终核：0 行。

本批次当前已完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA35/CLA45	gen2 subcompact luxury	2020-2026			184.8	73.1	55.4	2020/2021/2022/2023/2024/2025 Mercedes-AMG CLA35/CLA45; 2026 Mercedes-AMG CLA35/CLA45 S	AMG 包围已按 CLA45 S 高度边界取值；2026 CLA45 S Final Edition 属二代末期	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV / EQ Technology	gen3 compact luxury	2027-2027			185.9	73.0	57.8	2027 Mercedes-Benz CLA 350 4MATIC ELECTRIC Sedan; 2026 CLA 250+ EV / CLA 350 4MATIC EV dimensions	2027 美国官方配置页已出现；尺寸按新一代 CLA Electric 已公开规格取值	可入库
Mercedes-Benz CLC-Class	跑车	Mercedes-Benz	C-Class	Coupe	CLC alias / not US regular	gen2 compact executive	2008-2011					Mercedes-Benz CLC-Class	CLC 非美国常规销售名；不单独建主车型	别名/不入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen1 executive fastback	2006-2011			193.3	73.7	54.7	2006/2007/2008/2009/2010/2011 Mercedes-Benz CLS-Class	C219 fastback，不能按 E-Class sedan 合并	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS55/CLS63	gen1 executive fastback	2006-2011			194.0	73.7	54.7	2006/2007/2008 Mercedes-AMG CLS55; 2009/2010/2011 Mercedes-AMG CLS63	AMG 包围/轮胎已按更长车身边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen2 executive fastback	2012-2018			194.5	74.1	55.8	2012/2013/2014/2015/2016/2017/2018 Mercedes-Benz CLS-Class	C218 fastback；不保留欧洲 Shooting Brake	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS63	gen2 executive fastback	2012-2018			196.7	74.1	55.4	2012/2013/2014/2015/2016/2017/2018 Mercedes-AMG CLS63	AMG 2015-2018 长度高于标准版，已按 AMG 边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	4-door coupe	gen3 executive fastback	2019-2023			199.1	74.4	56.6	2019/2020/2021/2022/2023 Mercedes-Benz CLS-Class	C257 fastback；2023 后停产；已按 2019 长度与 2022-2023 高度边界取值	可入库
Mercedes-Benz CLS-Class	三厢车	Mercedes-Benz	CLS-Class	Sedan	AMG CLS53	gen3 executive fastback	2019-2021			199.1	74.6	56.0	2019/2020/2021 Mercedes-AMG CLS53	AMG CLS53 北美 2022 起不再提供，当前 split 原 2019-2023 范围内缩小为 2019-2021	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen1 executive	1994-1995			187.2	68.5	56.3	1994/1995 Mercedes-Benz E-Class Sedan	W124 E-Class sedan	可入库

下一步优先核对
无。当前批次已完成，可进入下一个 split 或合并前总表复核。

本批次完成。

