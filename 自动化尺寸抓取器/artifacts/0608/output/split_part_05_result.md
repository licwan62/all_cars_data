# 文件名：split_part_05.tsv


--- Round 1 / 首次发送 ---
更新点

已补入本轮查到的尺寸值。

Mercedes-Benz C-Class Convertible 分类从 敞篷车 修正为允许范围内的 跑车。

CLA-Class 的 4-door coupe 从版本字段移除，普通版统一改为 Std.。

AMG / PHEV 拆为 AMG 与 PHEV。

AMG C43 / C63 S E Performance 拆为 AMG C43 与 AMG C63 S E Performance。

参考车型未逐年覆盖的记录，本轮不判定为可入库，全部写明缺失年份。

当前批次进度

当前批次已完成一轮结构修正和尺寸补强，但仍未达到全部逐年覆盖核对要求，继续保留“待终核”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			180.8	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；已补入已查样本尺寸	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015-2021			184.5	71.3	57.0	2015/2021 Mercedes-Benz C-Class Sedan	W205 sedan；已按标准 sedan 补入最大外廓	待终核: 缺失 2016/2017/2018/2019/2020 年份参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.4	2017/2023 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接	待终核: 缺失 2018/2019/2020/2021/2022 年份参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.4	2022 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载	待终核: 缺失 2017/2018/2019/2020/2021/2023 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；AMG 包围和轮拱宽度按更大样本保守取值	待终核: 缺失 2017/2018/2019/2020 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	71.3	56.9	2016/2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；PHEV 美国覆盖缩小到已知 C350e 年份	待终核: 缺失 2017 年份参考；2019-2021 PHEV 当前 split 原行范围内未确认美国在售
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022/2025/2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库	待终核: 缺失 2023/2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023/2025/2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；AMG C43 独立尺寸	待终核: 缺失 2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024/2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2023 未确认美国 C63 S E Performance sedan	待终核: 缺失 2025 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG 包围/高度需核；暂按同代 CLA 外廓保守保留	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2026			184.6	72.0	56.7	2020/2024/2026 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake	待终核: 缺失 2021/2022/2023/2025 年份参考

下一步优先核对

优先逐年补齐 C-Class W205 Sedan 2016-2020、C-Class Coupe/Convertible 2018-2022、CLA gen1 2015-2018、CLA gen2 2021-2023/2025 的参考车型覆盖；其次确认 W205 AMG 与 PHEV 是否需要进一步按 C43/C63/C350e 拆细。

下一步


--- Round 2 / 下一步 ---
更新点

本轮把 Mercedes-Benz C-Class Sedan Std. gen4 拆为 2015 与 2016-2021：2016-2021 已补齐逐年参考覆盖，可入库；2015 仍缺完整尺寸参考，继续待终核。Edmunds 已显示 2016/2017/2018/2019 C-Class Sedan 均为 184.5 × 71.3 × 56.8 in，2020 为 184.5 × 71.3 × 56.3 in，2021 为 184.5 × 71.3 × 56.8 in，本行按区间最大值保守入表。
Edmunds
+5
Edmunds
+5
Edmunds
+5

本轮修正 C-Class Coupe Std. 宽度为 71.3，已由 2019 Edmunds coupe 样本确认，不再沿用上一轮 71.6。
Edmunds

本轮修正 C-Class Convertible Std. 宽度为 71.3，并把已覆盖参考扩展为 2019/2020/2022。2019/2020 Edmunds convertible 样本显示宽度 without mirrors 为 71.3。
Edmunds
+1

本轮补强 CLA-Class gen2 Std.：2025 CLA 250 已确认 184.6 × 72.0 × 56.7 in；仍缺 2021/2022/2023/2026 年份参考，继续待终核。
Edmunds
+1

本轮把 CLA-Class gen1 AMG CLA45 的长度修正为 184.7，参考 2019 AMG CLA45；该行仍缺 2015-2018 年份参考。
Edmunds

当前批次进度

原始 10 条记录已完成第二轮补强，当前拆分为 13 条。
其中 1 条已达到“参考车型逐年覆盖 + 尺寸对应”的可入库条件；其余 12 条仍有具体年份缺口或结构/版本待终核，不能判为完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			180.8	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；已补入已查样本尺寸	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.3	55.4	2019 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；宽度修正为 without mirrors 71.3	待终核: 缺失 2017/2018/2020/2021/2022/2023 年份参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.3	55.5	2019/2020/2022 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；按已查样本最大高度保守取值	待终核: 缺失 2017/2018/2021/2023 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；AMG 包围和轮拱宽度按更大样本保守取值	待终核: 缺失 2017/2018/2019/2020 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	71.3	56.9	2016/2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；PHEV 美国覆盖缩小到已知 C350e 年份	待终核: 缺失 2017 年份参考；2019-2021 PHEV 当前 split 原行范围内未确认美国在售
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022/2025/2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库	待终核: 缺失 2023/2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023/2025/2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；AMG C43 独立尺寸	待终核: 缺失 2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024/2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2023 未确认美国 C63 S E Performance sedan	待终核: 缺失 2025 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG CLA45 长度按 2019 已查样本修正为 184.7；高度仍需逐年核对	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2026			184.6	72.0	56.7	2020/2024/2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2025 尺寸已补强	待终核: 缺失 2021/2022/2023/2026 年份参考

下一步优先核对

优先补齐 C-Class Coupe 2017/2018/2020/2021/2022/2023 与 C-Class Convertible 2017/2018/2021/2023，这两组会直接决定 coupe/cabriolet 是否能整体入库；然后补 CLA gen1 2015-2018 和 CLA gen2 2021-2023/2026。

下一步


--- Round 3 / 下一步 ---
更新点

本轮继续补强 C-Class Coupe Std.：新增 2017/2018/2020/2021/2022 coupe 参考覆盖，其中 2017 为 184.5 × 71.3 × 55.5，2018/2020 为 184.5 × 71.3 × 55.3，2021/2022 为 184.5 × 71.6 × 55.3；因此该行宽度回调为区间最大 71.6，高度保留区间最大 55.5。
Edmunds
+4
Edmunds
+4
Edmunds
+4

本轮继续补强 C-Class Convertible Std.：新增 2017/2018/2023 convertible 参考覆盖，2023 宽度为 71.6，因此该行宽度由 71.3 修正为 71.6；当前只剩 2021 未覆盖。
Edmunds
+4
Edmunds
+4
Edmunds
+4

本轮补强 C-Class PHEV：2018 C350e 已确认 184.5 × 72.1 × 56.8，因此 PHEV 宽度由 71.3 修正为 72.1；当前仍缺 2017 参考。
Edmunds

本轮没有新增当前 split 范围外车型、代际或年份；拆分后的年份合集仍未超出原记录范围。

当前批次进度

当前由原始 10 条记录拆分/修正为 13 条记录。
本轮后仍只有 C-Class Sedan Std. gen4 2016-2021 达到可入库；C-Class Convertible Std. 已接近完成，仅缺 2021；C-Class Coupe Std. 仍缺 2019/2023；其余 AMG、PHEV、CLA 行仍需继续逐年补齐。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；长度按 2013 AMG C63 Coupe 已查样本修正	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017/2018/2020/2021/2022 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2021/2022 样本宽度为 71.6，按区间最大值回调	待终核: 缺失 2019/2023 年份参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017/2018/2019/2020/2022/2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2023 样本宽度为 71.6，按区间最大值修正	待终核: 缺失 2021 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；AMG 包围和轮拱宽度按更大样本保守取值	待终核: 缺失 2017/2018/2019/2020 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016/2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2018 C350e without mirrors 宽度 72.1，按 PHEV 已查最大值修正	待终核: 缺失 2017 年份参考；2019-2021 PHEV 当前 split 原行范围内未确认美国在售
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022/2025/2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库	待终核: 缺失 2023/2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023/2025/2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；AMG C43 独立尺寸	待终核: 缺失 2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024/2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2023 未确认美国 C63 S E Performance sedan	待终核: 缺失 2025 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG CLA45 长度按 2019 已查样本修正为 184.7；高度仍需逐年核对	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2026			184.6	72.0	56.7	2020/2024/2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2025 尺寸已补强	待终核: 缺失 2021/2022/2023/2026 年份参考

下一步优先核对

优先补 C-Class Convertible 2021，补上即可判断整段 2017-2023 是否可入库；其次补 C-Class Coupe 2019/2023，再处理 C-Class PHEV 2017 与 C-Class gen5 Sedan 2023/2024。

下一步


--- Round 4 / 下一步 ---
更新点

C-Class Convertible Std. 2017-2023 本轮补齐 2021 参考，2017-2023 已逐年覆盖，状态改为 可入库；2021 Edmunds 给出 184.5 × 71.6 × 55.5 in。
Edmunds

C-Class PHEV 2016-2018 本轮补齐 2017 C350e，2016/2017/2018 已覆盖，状态改为 可入库；2017 C350e 为 184.5 × 72.1 × 56.8 in。
Edmunds

C-Class Coupe Std. 2017-2023 本轮补入 2019 Coupe，2019 为 184.5 × 71.3 × 55.3 in；但 2023 Edmunds 页面可确认车型存在，未给完整外廓尺寸，因此继续待终核。
Edmunds
+1

C-Class Sedan Std. gen5 2022-2026 本轮补入 2023/2024 标准 Sedan 尺寸，2023/2024 均为 187.0 × 74.4 × 56.6 in；结合已查 2022/2025/2026，参考车型改为 2022-2026。
Edmunds
+1

未新增当前 TSV 范围外车型、代际或年份；仅在原记录年份范围内补强与状态更新。

当前批次进度

当前批次由原始 10 条拆分/修正为 13 条。
本轮后 可入库 从 1 条增加到 4 条：C-Class Sedan Std. gen4 2016-2021、C-Class Convertible Std. gen4 2017-2023、C-Class PHEV 2016-2018、C-Class Sedan Std. gen5 2022-2026。
其余 9 条仍有具体年份或完整尺寸参考缺口，继续待终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；长度按 2013 AMG C63 Coupe 已查样本修正	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017/2018/2019/2020/2021/2022 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2019 已补齐，2023 页面仅确认车型存在但缺完整外廓尺寸	待终核: 2023 缺少完整长宽高参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2019/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；已补 2019 AMG C63 S 页面，但 AMG C43/C63 仍需逐年核对	待终核: 缺失 2017/2018/2020 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016-2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2016/2017/2018 C350e 已覆盖，按 PHEV 最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022-2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库；2023/2024 已补齐	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023/2025/2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；AMG C43 独立尺寸	待终核: 缺失 2024 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024/2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2023 未确认美国 C63 S E Performance sedan	待终核: 缺失 2025 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG CLA45 长度按 2019 已查样本修正为 184.7；高度仍需逐年核对	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2026			184.6	72.0	56.7	2020/2024/2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2025 尺寸已补强	待终核: 缺失 2021/2022/2023/2026 年份参考

下一步优先核对

优先补 C-Class Coupe 2023 完整长宽高；然后补 C-Class gen5 AMG C43 2024、C-Class AMG C63 S E Performance 2025；之后集中处理 CLA gen1 2015-2018 与 CLA gen2 2021/2022/2023/2026。

下一步


--- Round 5 / 下一步 ---
更新点

C-Class Sedan AMG C43 gen5 2023-2026 本轮补齐 2024 参考，2023-2026 已逐年覆盖，状态改为 可入库；2024 AMG C43 与 2026 AMG C43 外廓均为 188.6 × 74.4 × 57.1 in。
Edmunds
+1

C-Class Sedan AMG C63 S E Performance gen5 2024-2026 本轮补齐 2025 参考，2024-2026 已逐年覆盖，状态改为 可入库；2025 Edmunds 给出 190.6 × 74.4 × 57.4 in。
Edmunds

CLA-Class Sedan Std. gen2 本轮确认 2026 已进入新一代 CLA EV，不能继续并入 2020-2025 C118 gas sedan；因此把原 2020-2026 拆为 2020-2025 Std. gen2 与 2026 EV gen3，年份合集仍在原记录范围内。2025 CLA-Class 为 184.6 × 72.0 × 56.7 in；2026 CLA 250+ EV 为 185.9 × 73.0 × 57.8 in。
Edmunds
+1

CLA-Class Sedan Std. gen2 2020-2025 本轮补入 2021/2022/2024/2025 样本；2022 为 184.6 × 72.0 × 56.3 in，2024 为 184.6 × 72.0 × 56.3 in，2025 为 184.6 × 72.0 × 56.7 in；仍缺 2023。
Edmunds
+2
Edmunds
+2

CLA-Class Sedan Std. gen1 2014-2019 本轮补入 2015 样本；2015 CLA250 为 182.3 × 70.0 × 56.6 in，仍缺 2016/2017/2018。
Edmunds

当前批次进度

当前批次由原始 10 条记录拆分/修正为 14 条记录。
本轮后 可入库 从 4 条增加到 6 条：新增 C-Class AMG C43 gen5 2023-2026 与 C-Class AMG C63 S E Performance gen5 2024-2026。
仍有 8 条待终核，主要集中在 C-Class Coupe 2023、C-Class gen3 AMG C63 Coupe 2012/2015、C-Class 2015 Sedan、W205 AMG 2017/2018/2020、CLA gen1 2016-2018、CLA gen2 2023、CLA 2026 EV 单年外廓确认。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；长度按 2013 AMG C63 Coupe 已查样本修正	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017/2018/2019/2020/2021/2022 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2019 已补齐，2023 页面仅确认车型存在但缺完整外廓尺寸	待终核: 2023 缺少完整长宽高参考
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2019/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；已补 2019 AMG C63 S 页面，但 AMG C43/C63 仍需逐年核对	待终核: 缺失 2017/2018/2020 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016-2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2016/2017/2018 C350e 已覆盖，按 PHEV 最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022-2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库；2023/2024 已补齐	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023-2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；2023-2026 已逐年覆盖，AMG C43 独立尺寸	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024-2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2024-2026 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014/2015/2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述；2015 样本已补入	待终核: 缺失 2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG CLA45 长度按 2019 已查样本修正为 184.7；高度仍需逐年核对	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2025			184.6	72.0	56.7	2020/2021/2022/2024/2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2026 已拆出为新一代 EV	待终核: 缺失 2023 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV	gen3 compact luxury EV	2026			185.9	73.0	57.8	2026 Mercedes-Benz CLA250+ EV Sedan	由原 2020-2026 CLA 行内拆出；2026 为新一代 CLA EV，不能并入 C118 gas sedan	待终核: 2026 EV 单年需继续确认美国量产/销售配置外廓

下一步优先核对

优先补 CLA gen2 2023，补齐后 2020-2025 CLA250 Sedan 可判断是否入库；其次补 CLA gen1 Std. 2016/2017/2018 与 CLA AMG CLA45 2015-2018；再回头处理 C-Class Coupe 2023 和 W205 AMG 2017/2018/2020。

下一步


--- Round 6 / 下一步 ---
更新点

C-Class Coupe Std. gen4 2017-2023 本轮补齐 2023 完整尺寸参考，2017-2023 已逐年覆盖，状态改为 可入库；2023 C 300 Coupe 尺寸为 184.5 × 71.3/71.6 × 55.3/55.4 in，不超过本行已取最大值。
Car and Driver
+1

CLA-Class Sedan Std. gen2 2020-2025 本轮补齐 2023，2020-2025 已逐年覆盖，状态改为 可入库；2023 CLA250 为 184.6 × 72.0 × 56.3 in。
Edmunds
+1

CLA-Class Sedan Std. gen1 2014-2019 本轮补齐 2016/2017/2018，2014-2019 已逐年覆盖，状态改为 可入库；2016/2017/2018 CLA250 均为 182.3 × 70.0 × 56.6 in。
Edmunds
+2
Edmunds
+2

C-Class Sedan AMG gen4 2016-2021 本轮补入 2020 AMG C43 尺寸，2020 AMG C43 为 185.0 × 71.3 × 56.3 in；但 2017/2018 仍缺，继续待终核。
Edmunds
+1

CLA-Class 2026 EV 本轮改回 2026 Mercedes-Benz CLA250+ EV Sedan，保留待终核；该行只在原 2020-2026 范围内拆出，不扩展范围。2026 CLA Electric CLA 250+ 尺寸为 185.9 × 73.0 × 57.8 in。
Edmunds

当前批次进度

当前批次由原始 10 条记录拆分/修正为 14 条记录。
本轮后 可入库 从 6 条增加到 9 条。仍有 5 条待终核：C-Class AMG C63 Coupe 2012/2015、C-Class Sedan Std. 2015、C-Class AMG gen4 2017/2018、CLA AMG CLA45 2015-2018、CLA 2026 EV 单年销售配置确认。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；长度按 2013 AMG C63 Coupe 已查样本修正	待终核: 缺失 2012/2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016/2019/2020/2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；已补 2020 AMG C43，但 2017/2018 AMG C43/C63 仍需逐年核对	待终核: 缺失 2017/2018 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016-2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2016/2017/2018 C350e 已覆盖，按 PHEV 最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022-2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库；2023/2024 已补齐	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023-2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；2023-2026 已逐年覆盖，AMG C43 独立尺寸	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024-2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2024-2026 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014-2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述；2014-2019 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014/2019 Mercedes-AMG CLA45 Sedan	AMG CLA45 长度按 2019 已查样本修正为 184.7；高度仍需逐年核对	待终核: 缺失 2015/2016/2017/2018 年份参考
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2025			184.6	72.0	56.7	2020-2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2026 已拆出为新一代 EV；2020-2025 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV	gen3 compact luxury EV	2026			185.9	73.0	57.8	2026 Mercedes-Benz CLA250+ EV Sedan	由原 2020-2026 CLA 行内拆出；2026 为新一代 CLA EV，不能并入 C118 gas sedan	待终核: 2026 EV 单年需继续确认美国量产/销售配置外廓

下一步优先核对

优先补 CLA AMG CLA45 2015/2016/2017/2018，补齐后 CLA 部分只剩 2026 EV 单年确认；其次补 C-Class AMG gen4 2017/2018，再处理 C-Class AMG C63 Coupe 2012/2015 与 C-Class Sedan Std. 2015。

下一步


--- Round 7 / 下一步 ---
更新点

CLA-Class AMG CLA45 gen1 2014-2019 本轮补齐 2015/2016/2017/2018：2016 Edmunds 为 184.7 × 70.0 × 55.7，2017/2018 MBUSA/Edmunds 为 183.8 × 70.0 × 55.7；结合 2014/2019，整段已逐年覆盖，状态改为 可入库。
Edmunds
+2
media.mbusa.com
+2

C-Class AMG gen4 2016-2021 本轮补齐 2017/2018 AMG C43：2017 为 185.1 × 71.3 × 56.3，2018 为 185.0 × 71.3 × 56.3；结合 2016/2019/2020/2021 已覆盖，状态改为 可入库。
Edmunds
+1

C-Class AMG C63 Coupe gen3 2012-2015 本轮补入 2012 C63 AMG Coupe：185.3 × 69.7 × 54.6；但 2015 仍缺，因此继续待终核。
Edmunds
+1

CLA-Class 2026 EV 本轮进一步确认 2026 CLA 250+ EV 单年尺寸仍按 185.9 × 73.0 × 57.8 保留；状态仍为待终核，因为美国最终销售配置需要继续确认。

未新增当前 TSV 范围外年代、车型或代际；仅补强、修正和更新状态。

当前批次进度

当前批次由原始 10 条记录拆分/修正为 14 条记录。
本轮后 可入库 从 9 条增加到 11 条。仍有 3 条待终核：C-Class AMG C63 Coupe 2015、C-Class Sedan Std. 2015、CLA 2026 EV 单年美国销售配置确认。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2012/2013/2014 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；2012 已补入，2015 仍缺完整参考	待终核: 缺失 2015 年份参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 已单独拆出，尺寸仍需复核到具体外廓来源	待终核: 2015 缺少完整长宽高参考
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016-2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；2016-2021 已逐年覆盖；按 AMG C43/C63 已查最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016-2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2016/2017/2018 C350e 已覆盖，按 PHEV 最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022-2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库；2023/2024 已补齐	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023-2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；2023-2026 已逐年覆盖，AMG C43 独立尺寸	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024-2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2024-2026 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014-2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述；2014-2019 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014-2019 Mercedes-AMG CLA45 Sedan	2014-2019 已逐年覆盖；按 AMG CLA45 已查最大外廓入表	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2025			184.6	72.0	56.7	2020-2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2026 已拆出为新一代 EV；2020-2025 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV	gen3 compact luxury EV	2026			185.9	73.0	57.8	2026 Mercedes-Benz CLA250+ EV Sedan	由原 2020-2026 CLA 行内拆出；2026 为新一代 CLA EV，不能并入 C118 gas sedan	待终核: 2026 EV 单年需继续确认美国最终销售配置外廓

下一步优先核对

优先补 2015 Mercedes-AMG C63 Coupe，然后终核 2015 Mercedes-Benz C-Class Sedan 的完整外廓来源；最后确认 2026 CLA250+ EV 是否按美国最终销售配置入库。

下一步


--- Round 8 / 下一步 ---
更新点

C-Class AMG C63 Coupe gen3 2012-2015 本轮补齐 2015：2015 C 63 AMG Coupe 为 185.3 × 69.7 × 54.6 in；结合 2012/2013/2014，整段 2012-2015 可入库。
Edmunds

C-Class Sedan Std. gen4 2015 本轮确认完整外廓：2015 C 300 Sedan 为 184.5 × 71.3 × 56.8 in，状态改为 可入库。
Edmunds

CLA-Class Sedan EV gen3 2026 本轮用 MBUSA 官方 2026 CLA 250+ 页面确认外廓：185.9 × 73.0 × 57.8 in，状态改为 可入库。
梅赛德斯-奔驰

当前批次剩余待终核项已清零；未新增当前 split 范围外车型、年代或代际。

当前批次进度

当前批次由原始 10 条记录拆分/修正为 14 条记录。
本轮后 14 条全部达到 可入库，当前批次已完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	AMG C63	gen3 compact executive	2012-2015			185.3	69.7	56.3	2012-2015 Mercedes-AMG C63 Coupe	AMG coupe 独立核对；2012-2015 已逐年覆盖，按区间最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2015			184.5	71.3	56.8	2015 Mercedes-Benz C-Class Sedan	W205 sedan；2015 单年完整外廓已确认	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen4 compact executive	2016-2021			184.5	71.3	56.8	2016-2021 Mercedes-Benz C-Class Sedan	W205 sedan；2016-2021 已逐年覆盖，按区间最大高度保守取值	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Coupe	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Coupe	Coupe 后部结构不同；2024 起由 CLE 承接；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	跑车	Mercedes-Benz	C-Class	Convertible	Std.	gen4 compact executive	2017-2023			184.5	71.6	55.5	2017-2023 Mercedes-Benz C-Class Cabriolet	分类由敞篷车修正为跑车；Cabriolet 信息已由结构字段承载；2017-2023 已逐年覆盖，按区间最大值入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG	gen4 compact executive	2016-2021			187.0	72.4	56.5	2016-2021 Mercedes-AMG C-Class Sedan	由 AMG / PHEV 拆出；2016-2021 已逐年覆盖；按 AMG C43/C63 已查最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	PHEV	gen4 compact executive	2016-2018			184.5	72.1	56.9	2016-2018 Mercedes-Benz C350e Sedan	由 AMG / PHEV 拆出；2016/2017/2018 C350e 已覆盖，按 PHEV 最大外廓入表	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	Std.	gen5 compact executive	2022-2026			187.0	74.4	56.6	2022-2026 Mercedes-Benz C300 Sedan	W206 sedan；Coupe/Cabrio 不再挂 C-Class 入库；2023/2024 已补齐	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C43	gen5 compact executive	2023-2026			188.6	74.4	57.1	2023-2026 Mercedes-AMG C43 Sedan	由 AMG C43 / C63 S E Performance 拆出；2023-2026 已逐年覆盖，AMG C43 独立尺寸	可入库
Mercedes-Benz C-Class	三厢车	Mercedes-Benz	C-Class	Sedan	AMG C63 S E Performance	gen5 compact executive	2024-2026			190.6	74.4	57.4	2024-2026 Mercedes-AMG C63 S E Performance Sedan	由 AMG C43 / C63 S E Performance 拆出；2024-2026 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen1 subcompact luxury	2014-2019			182.3	70.0	56.6	2014-2019 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；四门 coupe 仅作营销描述；2014-2019 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	AMG CLA45	gen1 subcompact luxury	2014-2019			184.7	70.0	56.6	2014-2019 Mercedes-AMG CLA45 Sedan	2014-2019 已逐年覆盖；按 AMG CLA45 已查最大外廓入表	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	Std.	gen2 subcompact luxury	2020-2025			184.6	72.0	56.7	2020-2025 Mercedes-Benz CLA250 Sedan	版本由 4-door coupe 修正为 Std.；C118 CLA；不保留欧洲 Shooting Brake；2026 已拆出为新一代 EV；2020-2025 已逐年覆盖	可入库
Mercedes-Benz CLA-Class	三厢车	Mercedes-Benz	CLA-Class	Sedan	EV	gen3 compact luxury EV	2026			185.9	73.0	57.8	2026 Mercedes-Benz CLA250+ EV Sedan	由原 2020-2026 CLA 行内拆出；2026 为新一代 CLA EV，MBUSA 官方外廓已确认	可入库

下一步优先核对

无。当前 split_part_05 已完成，可作为完整可替换 TSV 入库。

本批次完成。

