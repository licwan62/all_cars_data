# 文件名：split_part_09.tsv


--- Round 1 / 首次发送 ---
更新点

修正 分类：原 SUV 统一改为 越野车；原 旅行车 按当前允许分类改为 两厢车。

补入本轮可确认尺寸：E-Class Sedan / All-Terrain / AMG E53 Sedan / AMG E53 Wagon、EQB、GLA gen1/gen2 普通版与部分 AMG 版尺寸。E-Class 官方页显示 2026 AMG E53 Sedan 为 194.9 / 74.9 / 57.9，AMG E53 Wagon 为 195.2 / 74.9 / 58.4；E450 All-Terrain 官方页显示 194.9 / 74.4 / 58.9。
梅赛德斯-奔驰
+2
梅赛德斯-奔驰
+2

EQB 2022-2023 与 2024-2026 尺寸补入 184.4 / 72.2 / 65.6，其中 2025 MBUSA 与 Edmunds 均给出 184.4 / 72.2 / 65.6；2024 Edmunds 高度为 65.3，因此本轮按覆盖区间取 max_height 65.6。
梅赛德斯-奔驰
+2
Edmunds
+2

GLA gen2 普通版 2021/2022/2023 已逐年覆盖为 173.6 / 72.2 / 63.5；AMG GLA45 2023 为 174.6 / 72.8 / 62.5，GLA gen1 普通版 2020 为 173.9 / 71.0 / 60.0。
梅赛德斯-奔驰媒体
+4
Edmunds
+4
Edmunds
+4

当前批次进度

已补尺寸：10/10

已按当前允许分类修正：10/10

已可入库：3/10

仍待终核：7/10，主要缺 2024/2025/2026 新款 E-Class 的逐年覆盖、GLA gen1 2015-2019、GLA AMG 中间年、EQB 2026 直接参考。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen6 executive	2024-2026			194.9	74.0	57.9	2026 Mercedes-Benz E-Class Sedan	W214 sedan；已补 2026 官方尺寸	待终核: 缺失 2024/2025 逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	All-Terrain	gen6 executive	2024-2026			194.9	74.4	58.9	2026 Mercedes-Benz E450 4MATIC All-Terrain Wagon	All-Terrain wagon 后部+高度不同；分类由旅行车修正为两厢车	待终核: 缺失 2024/2025 逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E53 Hybrid	gen6 executive	2025-2026			194.9	74.9	57.9	2026 Mercedes-AMG E53 Hybrid Sedan	AMG PHEV 包围/宽度不同；已补 2026 官方尺寸	待终核: 缺失 2025 逐年参考
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	AMG E53 Hybrid Wagon	gen6 executive	2026-2026			195.2	74.9	58.4	2026 Mercedes-AMG E53 Hybrid Wagon	AMG wagon 与 All-Terrain/普通 wagon 需拆；分类由旅行车修正为两厢车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV	gen1 compact electric SUV	2022-2023			184.4	72.2	65.6	2022/2023 Mercedes-Benz EQB	纯电 SUV；可选三排但外形同车身；分类由 SUV 修正为越野车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV facelift	gen1 facelift compact electric SUV	2024-2026			184.4	72.2	65.6	2024/2025 Mercedes-Benz EQB	2024 改款，已按 2024-2025 取最大高度；分类由 SUV 修正为越野车	待终核: 缺失 2026 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen1 subcompact SUV	2015-2020			173.9	71.0	60.0	2020 Mercedes-Benz GLA 250 SUV	X156 小型 SUV；高车身；分类由 SUV 修正为越野车	待终核: 缺失 2015/2016/2017/2018/2019 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA45	gen1 subcompact SUV	2015-2020			175.4	71.0	58.0	2019 Mercedes-AMG GLA45	AMG 包围/高度需核；已补 2019 AMG 尺寸；分类由 SUV 修正为越野车	待终核: 缺失 2015/2016/2017/2018/2020 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen2 subcompact SUV	2021-2023			173.6	72.2	63.5	2021/2022/2023 Mercedes-Benz GLA 250 SUV	H247 换代，高度明显变化；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA35/GLA45	gen2 subcompact SUV	2021-2023			174.6	72.8	62.5	2023 Mercedes-AMG GLA45	AMG 包围/高度需核；已补 2023 AMG 最大尺寸；分类由 SUV 修正为越野车	待终核: 缺失 2021/2022 逐年参考

下一步优先核对

优先补 Mercedes-Benz E-Class 2024/2025 Sedan、All-Terrain、AMG E53 Sedan 的逐年官方/Edmunds 尺寸。

其次补 GLA-Class gen1 2015-2019 普通版与 GLA45 2015-2018/2020。

最后补 EQB 2026 与 GLA AMG gen2 2021/2022，确认是否可压缩为完整区间。

下一步


--- Round 2 / 下一步 ---
更新点

本轮继续补强逐年覆盖，不新增当前 TSV 范围外记录。

Mercedes-Benz E-Class Sedan Std. 2024-2026：补齐 2024/2025/2026 尺寸覆盖，状态推进为可入库。2025 Edmunds 给出 194.9 / 74.0 / 57.9，2026 MBUSA 同尺寸；2024 W214 同代尺寸按 Edmunds/MBUSA 规格覆盖。
Edmunds
+2
Edmunds
+2

E-Class All-Terrain 2024-2026：补入 2024 官方 quick reference 的 194.9 / 74.4 / 58.9；2025/2026 仍缺完整逐年参考，暂不判可入库。
梅赛德斯-奔驰媒体
+1

AMG E53 Hybrid Sedan 2025-2026：补齐 2025/2026 官方/Edmunds 尺寸，状态推进为可入库；官方 quick reference 与 2026 MBUSA 均支持 194.9 / 74.9 / 57.9。
梅赛德斯-奔驰媒体
+1

EQB facelift 2024-2026：补强 2024/2025 逐年参考，仍缺 2026 美国市场直接尺寸参考。2024 Edmunds 为 184.4 / 72.2 / 65.3，2025 Edmunds/MBUSA 为 184.4 / 72.2 / 65.6，本行取最大高度 65.6。
Edmunds
+2
Edmunds
+2

GLA gen1 Std.：补强 2015/2016/2018/2019/2020 参考，仍缺 2017 直接参考；GLA gen1 AMG GLA45 补强 2016/2018/2019，仍缺 2015/2017/2020。
Edmunds
+5
Edmunds
+5
Edmunds
+5

GLA gen2 AMG GLA35/GLA45：补入 2022/2023 GLA45 参考，仍缺 2021，且当前版本混合 GLA35/GLA45 还需确认是否应拆。
Edmunds
+1

当前批次进度

当前记录：10 条

已补尺寸：10/10

已完成分类字段修正：10/10

本轮推进为可入库：E-Class Sedan Std. 2024-2026、AMG E53 Hybrid Sedan 2025-2026

当前可入库：5/10

当前待终核：5/10，集中在 All-Terrain 2025/2026、EQB 2026、GLA gen1 缺 2017、GLA AMG 缺年份与混合版本确认。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen6 executive	2024-2026			194.9	74.0	57.9	2024/2025/2026 Mercedes-Benz E-Class Sedan	W214 sedan；2024-2026 已按同代 Sedan 尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	All-Terrain	gen6 executive	2024-2026			194.9	74.4	58.9	2024 Mercedes-Benz E450 4MATIC All-Terrain Wagon	All-Terrain wagon 后部+高度不同；分类由旅行车修正为两厢车；已补 2024 官方尺寸	待终核: 缺失 2025/2026 逐年参考
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E53 Hybrid	gen6 executive	2025-2026			194.9	74.9	57.9	2025/2026 Mercedes-AMG E53 Hybrid Sedan	AMG PHEV 包围/宽度不同；2025-2026 已按 AMG E53 Hybrid Sedan 官方尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	AMG E53 Hybrid Wagon	gen6 executive	2026-2026			195.2	74.9	58.4	2026 Mercedes-AMG E53 Hybrid Wagon	AMG wagon 与 All-Terrain/普通 wagon 需拆；分类由旅行车修正为两厢车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV	gen1 compact electric SUV	2022-2023			184.4	72.2	65.6	2022/2023 Mercedes-Benz EQB	纯电 SUV；可选三排但外形同车身；分类由 SUV 修正为越野车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV facelift	gen1 facelift compact electric SUV	2024-2026			184.4	72.2	65.6	2024/2025 Mercedes-Benz EQB	2024 改款；2024 高度 65.3、2025 高度 65.6，本行取区间最大；分类由 SUV 修正为越野车	待终核: 缺失 2026 美国市场逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen1 subcompact SUV	2015-2020			173.9	71.0	60.0	2015/2016/2018/2019/2020 Mercedes-Benz GLA 250 SUV	X156 小型 SUV；高车身；分类由 SUV 修正为越野车；本轮补强 2015/2016/2018/2019	待终核: 缺失 2017 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA45	gen1 subcompact SUV	2015-2020			175.4	71.0	58.2	2016/2018/2019 Mercedes-AMG GLA45	AMG 包围/长度不同；按已核 2016/2018/2019 取最大长度 175.4、高度 58.2；分类由 SUV 修正为越野车	待终核: 缺失 2015/2017/2020 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen2 subcompact SUV	2021-2023			173.6	72.2	63.5	2021/2022/2023 Mercedes-Benz GLA 250 SUV	H247 换代，高度明显变化；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA35/GLA45	gen2 subcompact SUV	2021-2023			174.6	72.8	62.5	2022/2023 Mercedes-AMG GLA45	AMG 包围/高度需核；已补 2022/2023 GLA45 最大尺寸；分类由 SUV 修正为越野车	待终核: 缺失 2021 逐年参考，且 GLA35/GLA45 混合版本需确认是否拆行

下一步优先核对
优先核 E-Class All-Terrain 2025/2026 和 EQB 2026 美国市场尺寸，这两条完成后可直接推进入库；然后核 GLA gen1 Std. 2017、GLA45 2015/2017/2020；最后处理 GLA gen2 AMG GLA35/GLA45 是否需要拆成 AMG GLA35 与 AMG GLA45 两行。

下一步


--- Round 3 / 下一步 ---
更新点

E-Class All-Terrain 2024-2026：补齐 2024/2025/2026 参考，状态推进为可入库；2024/2026 官方高度 58.9，2025 Edmunds 高度 57.9，本行按区间最大取 58.9。
梅赛德斯-奔驰
+2
Edmunds
+2

GLA-Class Std. gen1 2015-2020：补入缺失的 2017 参考，普通版 2015/2017/2020 均为 173.9 / 71.0 / 60.0，结合上一轮已覆盖年份，推进为可入库。
Edmunds
+2
Edmunds
+2

GLA-Class AMG GLA45 gen1：补入 2015/2017 参考，并修正最大长度为 176.4；仍缺 2020 AMG GLA45 直接参考，暂不入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

GLA-Class AMG GLA35/GLA45 gen2 2021-2023：补齐 2021 AMG GLA35/GLA45 参考，确认 2021-2023 AMG 35/45 外廓尺寸一致为 174.6 / 72.8 / 62.5，状态推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

EQB facelift 2024-2026：仍保留 2026 直接参考缺口；2024/2025 已确认，2026 搜索到的经销商页仅能支撑长度，宽/高不足，不判可入库。
mercedesbenzofvirginiabeach.com
+2
Edmunds
+2

当前批次进度

当前记录：10 条

已补尺寸：10/10

当前可入库：8/10

当前待终核：2/10

剩余缺口：EQB facelift 2026 缺完整美国市场宽/高直接参考；GLA45 gen1 2020 缺直接尺寸参考。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen6 executive	2024-2026			194.9	74.0	57.9	2024/2025/2026 Mercedes-Benz E-Class Sedan	W214 sedan；2024-2026 已按同代 Sedan 尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	All-Terrain	gen6 executive	2024-2026			194.9	74.4	58.9	2024/2025/2026 Mercedes-Benz E450 4MATIC All-Terrain Wagon	All-Terrain wagon 后部+高度不同；2025 Edmunds 高度较低，本行按 2024/2026 官方高度取区间最大 58.9；分类由旅行车修正为两厢车	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E53 Hybrid	gen6 executive	2025-2026			194.9	74.9	57.9	2025/2026 Mercedes-AMG E53 Hybrid Sedan	AMG PHEV 包围/宽度不同；2025-2026 已按 AMG E53 Hybrid Sedan 官方尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	AMG E53 Hybrid Wagon	gen6 executive	2026-2026			195.2	74.9	58.4	2026 Mercedes-AMG E53 Hybrid Wagon	AMG wagon 与 All-Terrain/普通 wagon 需拆；分类由旅行车修正为两厢车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV	gen1 compact electric SUV	2022-2023			184.4	72.2	65.6	2022/2023 Mercedes-Benz EQB	纯电 SUV；可选三排但外形同车身；分类由 SUV 修正为越野车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV facelift	gen1 facelift compact electric SUV	2024-2026			184.4	72.2	65.6	2024/2025 Mercedes-Benz EQB	2024 改款；2024 高度 65.3、2025 高度 65.6，本行取区间最大；分类由 SUV 修正为越野车	待终核: 缺失 2026 美国市场完整宽度/高度直接参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen1 subcompact SUV	2015-2020			173.9	71.0	60.0	2015/2016/2017/2018/2019/2020 Mercedes-Benz GLA 250 SUV	X156 小型 SUV；高车身；分类由 SUV 修正为越野车；本轮补齐 2017 参考	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA45	gen1 subcompact SUV	2015-2020			176.4	71.0	58.2	2015/2016/2017/2018/2019 Mercedes-AMG GLA45	AMG 包围/长度不同；本轮补入 2015/2017，按已核年份取最大长度 176.4；分类由 SUV 修正为越野车	待终核: 缺失 2020 AMG GLA45 逐年参考
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen2 subcompact SUV	2021-2023			173.6	72.2	63.5	2021/2022/2023 Mercedes-Benz GLA 250 SUV	H247 换代，高度明显变化；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA35/GLA45	gen2 subcompact SUV	2021-2023			174.6	72.8	62.5	2021/2022/2023 Mercedes-AMG GLA35/GLA45	AMG 包围/宽度不同；已确认 2021-2023 AMG GLA35 与 GLA45 外廓尺寸一致，暂保留合并版本；分类由 SUV 修正为越野车	可入库

下一步优先核对

优先找 2026 Mercedes-Benz EQB 美国市场官方或 Edmunds 完整长宽高。

其次找 2020 Mercedes-AMG GLA45 美国市场直接尺寸；如果确认 2020 未在美国销售 AMG GLA45，则应把该行年份缩小为 2015-2019，并在备注说明 2020 无美国 AMG GLA45 覆盖。

下一步


--- Round 4 / 下一步 ---
更新点

Mercedes-Benz EQB EV facelift 2024-2026：补齐 2026 美国经销商规格页完整长宽高，2026 EQB 300 显示 length 184.4、body width 72.2、height 65.6；本行推进为可入库。
梅赛德斯-奔驰维吉尼亚海滩

Mercedes-Benz GLA-Class AMG GLA45 gen1：确认 2020 GLA-Class 美国规格页只有 GLA 250 / GLA 250 4MATIC，且 Edmunds 明确写 2020 AMG GLA45 discontinued；因此不强行保留 2020 AMG，年份区间缩小为 2015-2019，状态推进为可入库。
Edmunds
+1

当前批次 10 条已全部完成尺寸补强与状态收口。

当前批次进度

当前记录：10 条

已补尺寸：10/10

可入库：10/10

待终核：0/10

本轮没有新增当前 split 范围外车型、代际或年份；仅将原 2015-2020 AMG GLA45 缩小为实际美国市场覆盖的 2015-2019。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	Std.	gen6 executive	2024-2026			194.9	74.0	57.9	2024/2025/2026 Mercedes-Benz E-Class Sedan	W214 sedan；2024-2026 已按同代 Sedan 尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	All-Terrain	gen6 executive	2024-2026			194.9	74.4	58.9	2024/2025/2026 Mercedes-Benz E450 4MATIC All-Terrain Wagon	All-Terrain wagon 后部+高度不同；2025 Edmunds 高度较低，本行按 2024/2026 官方高度取区间最大 58.9；分类由旅行车修正为两厢车	可入库
Mercedes-Benz E-Class	三厢车	Mercedes-Benz	E-Class	Sedan	AMG E53 Hybrid	gen6 executive	2025-2026			194.9	74.9	57.9	2025/2026 Mercedes-AMG E53 Hybrid Sedan	AMG PHEV 包围/宽度不同；2025-2026 已按 AMG E53 Hybrid Sedan 官方尺寸补齐	可入库
Mercedes-Benz E-Class	两厢车	Mercedes-Benz	E-Class	Wagon	AMG E53 Hybrid Wagon	gen6 executive	2026-2026			195.2	74.9	58.4	2026 Mercedes-AMG E53 Hybrid Wagon	AMG wagon 与 All-Terrain/普通 wagon 需拆；分类由旅行车修正为两厢车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV	gen1 compact electric SUV	2022-2023			184.4	72.2	65.6	2022/2023 Mercedes-Benz EQB	纯电 SUV；可选三排但外形同车身；分类由 SUV 修正为越野车	可入库
Mercedes-Benz EQB	越野车	Mercedes-Benz	EQB	SUV	EV facelift	gen1 facelift compact electric SUV	2024-2026			184.4	72.2	65.6	2024/2025/2026 Mercedes-Benz EQB	2024 改款；2024 高度 65.3、2025/2026 高度 65.6，本行取区间最大；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen1 subcompact SUV	2015-2020			173.9	71.0	60.0	2015/2016/2017/2018/2019/2020 Mercedes-Benz GLA 250 SUV	X156 小型 SUV；高车身；分类由 SUV 修正为越野车；2015-2020 普通 GLA 250 已覆盖	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA45	gen1 subcompact SUV	2015-2019			176.4	71.0	58.2	2015/2016/2017/2018/2019 Mercedes-AMG GLA45	AMG 包围/长度不同；2020 美国市场 AMG GLA45 discontinued，原 2015-2020 缩小为 2015-2019；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	Std.	gen2 subcompact SUV	2021-2023			173.6	72.2	63.5	2021/2022/2023 Mercedes-Benz GLA 250 SUV	H247 换代，高度明显变化；分类由 SUV 修正为越野车	可入库
Mercedes-Benz GLA-Class	越野车	Mercedes-Benz	GLA-Class	SUV	AMG GLA35/GLA45	gen2 subcompact SUV	2021-2023			174.6	72.8	62.5	2021/2022/2023 Mercedes-AMG GLA35/GLA45	AMG 包围/宽度不同；已确认 2021-2023 AMG GLA35 与 GLA45 外廓尺寸一致，暂保留合并版本；分类由 SUV 修正为越野车	可入库

下一步优先核对
无。本批次剩余待终核已清零。

本批次完成。

