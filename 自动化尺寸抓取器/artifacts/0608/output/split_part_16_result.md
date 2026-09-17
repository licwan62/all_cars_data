# 文件名：split_part_16.tsv


--- Round 1 / 首次发送 ---
1) 更新点

修正分类：敞篷车/掀背车 不符合本批规则，911 统一改为 跑车，Panamera 改为 两厢车。

911 Turbo / GT / Dakar 已拆为 Turbo、GT3/GT3 RS、Dakar，避免宽体/加高车型混写。

Panamera 2010-2013 原尺寸偏长，按逐年结果缩小为 195.6/76.0/55.8，并保留高度最大值。2014-2016 facelift Std. 保留 197.4/76.0/55.8；Executive LWB 独立 203.4/76.0/56.1。

关键尺寸来源核对到 Edmunds / Car and Driver：911 Cabriolet/Targa 标准 992 为 177.9/72.9/51.1，Turbo 为 178.6/74.9/51.3，Dakar 为 178.6/73.4/52.7，992.2 标准 Carrera/Targa 为 178.8-179.3/72.9/约51.3，Panamera 2014-2016 与 Executive LWB 也已匹配 Edmunds。
Edmunds
+9
Car and Driver
+9
Car and Driver
+9

2) 当前批次进度

当前批次 10 条原始记录已补强为 12 条可替换记录；仍有 911 992.2 的 2026 部分 Turbo/GT 年款、以及 2020-2021 Panamera 早期部分年份参考需要继续终核，所以本轮不判定本批次完成。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Cabriolet	992 Cabriolet 结构不同，标准宽体未并入	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen8 992	2021-2024			177.9	72.9	51.2	2021/2022/2023/2024 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，2024 Targa 4S 高度取 51.2	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo	gen8 992	2021-2024			178.6	74.9	51.3	2021/2022/2023/2024 Porsche 911 Turbo/Turbo S Coupe	Turbo 宽体，区别于 Carrera/GT3/Dakar	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS	gen8 992	2021-2024			180.0	74.8	52.1	2023/2024 Porsche 911 GT3 RS; 2024 Porsche 911 S/T; 2024 Porsche 911 GT3 reference	GT/RS 空气套件高风险，长度/高度取 GT3 RS/S-T 最大	待终核: 缺失 2021/2022 GT3 逐年参考，2024 GT3 RS 宽度需终核
Porsche 911	跑车	Porsche	911	Coupe	Dakar	gen8 992	2023-2024			178.6	73.4	52.7	2023/2024 Porsche 911 Dakar	Dakar 加高，原 2021-2024 范围内仅保留实际 Dakar 年份	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std. facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/Carrera GTS Coupe	992.2 普通 coupe，长度取 GTS 最大	可入库
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/GTS Cabriolet	Cabriolet 改款，取 992.2 Cabriolet/GTS 最大包络	待终核: 2026 Cabriolet 全版本逐年参考需补齐
Porsche 911	跑车	Porsche	911	Targa	Std. facelift	gen8 facelift 992.2	2026-2026			179.3	72.9	51.3	2026 Porsche 911 Targa 4S/Targa 4 GTS	Targa 4S/GTS 2026 扩展，取 GTS 长度最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo facelift	gen8 facelift 992.2	2025-2026			179.2	74.8	51.3	2025/2026 Porsche 911 Turbo S Coupe	Turbo S 宽体，区别于 GT3	待终核: 2026 Turbo/Turbo S Coupe 全版本参考需补齐
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS facelift	gen8 facelift 992.2	2025-2026			180.0	74.8	52.0	2025 Porsche 911 GT3/GT3 RS; 2026 Porsche 911 GT3	GT3/GT3 RS 空气套件高风险	待终核: 缺失 2026 GT3 RS 参考
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std.	gen1 full-size luxury	2010-2013			195.6	76.0	55.8	2010/2011/2012/2013 Porsche Panamera Liftback	一代标准轴，长度修正为 195.6，取高度最大值	待终核: 缺失 2010/2011 Edmunds 逐年参考
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std. facelift	gen1 facelift full-size luxury	2014-2016			197.4	76.0	55.8	2014/2015/2016 Porsche Panamera Liftback	改款标准轴，2015 低高但取区间最大高度	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Executive LWB	gen1 facelift full-size luxury	2014-2016			203.4	76.0	56.1	2014/2015/2016 Porsche Panamera Executive LWB	Executive 长轴，必须拆	待终核: 缺失 2014 Executive LWB 逐年参考
4) 下一步优先核对

优先补齐 4 个待终核点：911 992 GT3 2021/2022、911 992.2 2026 Turbo/GT3 RS、2026 Cabriolet 全版本、Panamera 2010/2011 与 2014 Executive LWB 的逐年权威参考。

下一步


--- Round 2 / 下一步 ---
1) 更新点

将 Porsche Panamera Executive LWB 2014-2016 补齐为逐年覆盖，2014/2015/2016 Executive LWB 均可支撑 203.4 / 76.0 / 56.1，状态由待终核改为可入库。
Edmunds
+2
Edmunds
+2

将 Porsche 911 GT3/GT3 RS gen8 992 从 2021-2024 收窄为 2022-2024，因为 2021 不作为当前 GT3/GT3 RS 覆盖年；尺寸按 2022 GT3 与 2024 GT3 RS 最大包络修正为 180.0 / 74.8 / 52.1。
Car and Driver
+1

Porsche 911 Cabriolet facelift 2025-2026 宽度由 72.9 调整为 74.8，用于覆盖 2026 GTS/宽体 Cabriolet 风险，仍保留待终核。
Edmunds
+1

Panamera 2010-2013 Std. 已补到 2010 权威尺寸，但 2011/2012/2013 仍缺逐年完整来源，所以仍不能判可入库。
Edmunds
+1

2) 当前批次进度

当前批次由原始 10 条拆分/补强为 13 条。
本轮新增 2 条从待终核推进：Panamera Executive LWB 2014-2016 已可入库；911 GT3/GT3 RS gen8 992 年份边界已修正并可入库。
仍有 4 条待终核：911 Cabriolet facelift、911 Turbo facelift、911 GT3/GT3 RS facelift、Panamera Std. 2010-2013。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Cabriolet	992 Cabriolet 结构不同，标准宽体未并入	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen8 992	2021-2024			177.9	72.9	51.2	2021/2022/2023/2024 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，2024 Targa 4S 高度取 51.2	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo	gen8 992	2021-2024			178.6	74.9	51.3	2021/2022/2023/2024 Porsche 911 Turbo/Turbo S Coupe	Turbo 宽体，区别于 Carrera/GT3/Dakar	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS	gen8 992	2022-2024			180.0	74.8	52.1	2022/2023/2024 Porsche 911 GT3/GT3 RS Coupe	GT/RS 空气套件高风险；原范围内 2021 不作为 GT3/GT3 RS 覆盖年	可入库
Porsche 911	跑车	Porsche	911	Coupe	Dakar	gen8 992	2023-2024			178.6	73.4	52.7	2023/2024 Porsche 911 Dakar	Dakar 加高，原 2021-2024 范围内仅保留实际 Dakar 年份	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std. facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/Carrera GTS Coupe	992.2 普通 coupe，长度取 GTS 最大	可入库
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet facelift	gen8 facelift 992.2	2025-2026			179.3	74.8	51.3	2025/2026 Porsche 911 Carrera/GTS Cabriolet	Cabriolet 改款，宽度按 2026 GTS/宽体 Cabriolet 风险上调	待终核: 2025/2026 Cabriolet 各驱动版本宽度需逐年终核
Porsche 911	跑车	Porsche	911	Targa	Std. facelift	gen8 facelift 992.2	2026-2026			179.3	72.9	51.3	2026 Porsche 911 Targa 4S/Targa 4 GTS	Targa 4S/GTS 2026 扩展，取 GTS 长度最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo facelift	gen8 facelift 992.2	2025-2026			179.2	74.8	51.3	2025/2026 Porsche 911 Turbo S Coupe	Turbo S 宽体，区别于 GT3	待终核: 2026 Turbo/Turbo S Coupe 长度/高度需终核
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS facelift	gen8 facelift 992.2	2025-2026			180.0	74.8	52.0	2025 Porsche 911 GT3/GT3 RS; 2026 Porsche 911 GT3	GT3/GT3 RS 空气套件高风险	待终核: 缺失 2026 GT3 RS 参考，且 2025 GT3 RS 是否属于 facelift 需终核
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std.	gen1 full-size luxury	2010-2013			195.6	76.0	55.8	2010 Porsche Panamera Liftback; 2011/2012/2013 pending year-by-year source	一代标准轴，长度修正为 195.6，取高度最大值	待终核: 缺失 2011/2012/2013 逐年参考
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std. facelift	gen1 facelift full-size luxury	2014-2016			197.4	76.0	55.8	2014/2015/2016 Porsche Panamera Liftback	改款标准轴，2015 低高但取区间最大高度	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Executive LWB	gen1 facelift full-size luxury	2014-2016			203.4	76.0	56.1	2014/2015/2016 Porsche Panamera 4S/Turbo Executive LWB	Executive 长轴，必须拆	可入库
4) 下一步优先核对

优先核对剩余 4 条：
Panamera Std. 2011/2012/2013、911 Cabriolet facelift 2025/2026 宽度差异、911 Turbo facelift 2026、911 GT3 RS facelift 2026。

5) 下一步

下一步


--- Round 3 / 下一步 ---
1) 更新点

Panamera Std. 2010-2013 已补齐 2011/2012/2013 逐年尺寸，195.6 / 76.0 / 55.8 可覆盖整段，状态改为 可入库。Edmunds 显示 2011、2012、2013 Panamera 均为 length 195.6、width without mirrors 76.0、height 55.8。
Edmunds
+2
Edmunds
+2

911 Cabriolet facelift 2025-2026 宽度从上一轮临时上调的 74.8 修正回 72.9；74.8 属于 Turbo/宽体风险，不应并入标准 Cabriolet facelift 行。2026 Carrera GTS / Carrera 4 GTS 宽度 without mirrors 均为 72.9。
Edmunds
+1

911 GT3/GT3 RS facelift 拆得更干净：2026 已确认 GT3 尺寸 179.9 / 72.9 / 50.4；GT3 RS facelift 仍缺 2026 逐年参考，因此保留待终核。
Edmunds
+1

2) 当前批次进度

当前批次由原始 10 条补强为 13 条。
本轮后可入库记录增加到 10 条，仍有 3 条待终核：911 Turbo facelift 2025-2026、911 GT3 RS facelift、911 Cabriolet facelift 是否需要覆盖 AWD/GTS 全变体继续终核。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Cabriolet	992 Cabriolet 结构不同，标准宽体未并入	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen8 992	2021-2024			177.9	72.9	51.2	2021/2022/2023/2024 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，2024 Targa 4S 高度取 51.2	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo	gen8 992	2021-2024			178.6	74.9	51.3	2021/2022/2023/2024 Porsche 911 Turbo/Turbo S Coupe	Turbo 宽体，区别于 Carrera/GT3/Dakar	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS	gen8 992	2022-2024			180.0	74.8	52.1	2022/2023/2024 Porsche 911 GT3/GT3 RS Coupe	GT/RS 空气套件高风险；原范围内 2021 不作为 GT3/GT3 RS 覆盖年	可入库
Porsche 911	跑车	Porsche	911	Coupe	Dakar	gen8 992	2023-2024			178.6	73.4	52.7	2023/2024 Porsche 911 Dakar	Dakar 加高，原 2021-2024 范围内仅保留实际 Dakar 年份	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std. facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/Carrera GTS Coupe	992.2 普通 coupe，长度取 GTS 最大	可入库
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/GTS Cabriolet	Cabriolet 改款，标准/GTS Cabriolet 不并入 Turbo Cabriolet 宽体	待终核: 2025/2026 Cabriolet AWD/GTS 全变体需最终确认
Porsche 911	跑车	Porsche	911	Targa	Std. facelift	gen8 facelift 992.2	2026-2026			179.3	72.9	51.3	2026 Porsche 911 Targa 4S/Targa 4 GTS	Targa 4S/GTS 2026 扩展，取 GTS 长度最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo facelift	gen8 facelift 992.2	2025-2026			179.2	74.8	51.3	2025/2026 Porsche 911 Turbo S Coupe	Turbo S 宽体，区别于 GT3	待终核: 2026 Turbo/Turbo S Coupe 长度/高度需终核
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS facelift	gen8 facelift 992.2	2025-2026			180.0	74.8	52.0	2025 Porsche 911 GT3/GT3 RS; 2026 Porsche 911 GT3	GT3/GT3 RS 空气套件高风险	待终核: 缺失 2026 GT3 RS 参考，且 2025 GT3 RS 是否属于 facelift 需终核
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std.	gen1 full-size luxury	2010-2013			195.6	76.0	55.8	2010/2011/2012/2013 Porsche Panamera Liftback	一代标准轴，长度修正为 195.6，取高度最大值	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std. facelift	gen1 facelift full-size luxury	2014-2016			197.4	76.0	55.8	2014/2015/2016 Porsche Panamera Liftback	改款标准轴，2015 低高但取区间最大高度	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Executive LWB	gen1 facelift full-size luxury	2014-2016			203.4	76.0	56.1	2014/2015/2016 Porsche Panamera 4S/Turbo Executive LWB	Executive 长轴，必须拆	可入库
4) 下一步优先核对

优先只剩 3 个点：2026 911 Turbo S Coupe 官方长宽高、2026 911 GT3 RS 是否已覆盖/是否可缩小年份、2025-2026 Cabriolet facelift 是否需要按 Carrera / GTS / AWD 再拆。

5) 下一步

下一步


--- Round 4 / 下一步 ---
1) 更新点

911 Cabriolet facelift 2025-2026 已进一步核对，标准 Carrera/GTS Cabriolet 宽度不应按 Turbo 宽体处理，继续保持 179.3 / 72.9 / 51.3；参考车型已覆盖 2025/2026，状态改为 可入库。2026 Carrera GTS/Carrera 4 GTS 的宽度 without mirrors 为 72.9，长度 179.3；2026 Carrera S Cabriolet 实测规格也显示 178.8 / 72.9 / 50.9，可被该行包络。
Edmunds
+2
MotorTrend
+2

911 GT3/GT3 RS facelift 2025-2026 拆分为 GT3 facelift 2026-2026 与 GT3 RS facelift 2025-2026。2026 GT3 已有明确尺寸，改为可入库；GT3 RS facelift 仍缺 2026 逐年尺寸，保留待终核。
保时捷
+1

911 Turbo facelift 2025-2026 仍保留待终核：目前可确认 Turbo S 新款官方车型存在，但本轮未能形成 2025/2026 两年完整长宽高逐年覆盖，所以不强行判可入库。
保时捷
+1

2) 当前批次进度

当前批次由原始 10 条补强为 14 条。
本轮后 可入库 记录为 12 条，剩余 2 条待终核：911 Turbo facelift 2025-2026、911 GT3 RS facelift 2025-2026。
Panamera 三条已全部完成；911 992 标准 Cabriolet/Targa/Turbo/GT3/Dakar 已完成；911 992.2 标准 Coupe/Cabriolet/Targa/GT3 已完成。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Cabriolet	992 Cabriolet 结构不同，标准宽体未并入	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen8 992	2021-2024			177.9	72.9	51.2	2021/2022/2023/2024 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，2024 Targa 4S 高度取 51.2	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo	gen8 992	2021-2024			178.6	74.9	51.3	2021/2022/2023/2024 Porsche 911 Turbo/Turbo S Coupe	Turbo 宽体，区别于 Carrera/GT3/Dakar	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS	gen8 992	2022-2024			180.0	74.8	52.1	2022/2023/2024 Porsche 911 GT3/GT3 RS Coupe	GT/RS 空气套件高风险；原范围内 2021 不作为 GT3/GT3 RS 覆盖年	可入库
Porsche 911	跑车	Porsche	911	Coupe	Dakar	gen8 992	2023-2024			178.6	73.4	52.7	2023/2024 Porsche 911 Dakar	Dakar 加高，原 2021-2024 范围内仅保留实际 Dakar 年份	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std. facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/Carrera GTS Coupe	992.2 普通 coupe，长度取 GTS 最大	可入库
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/GTS Cabriolet	Cabriolet 改款，标准/GTS Cabriolet 不并入 Turbo Cabriolet 宽体	可入库
Porsche 911	跑车	Porsche	911	Targa	Std. facelift	gen8 facelift 992.2	2026-2026			179.3	72.9	51.3	2026 Porsche 911 Targa 4S/Targa 4 GTS	Targa 4S/GTS 2026 扩展，取 GTS 长度最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo facelift	gen8 facelift 992.2	2025-2026			179.2	74.8	51.3	2025/2026 Porsche 911 Turbo S Coupe	Turbo S 宽体，区别于 GT3	待终核: 缺失 2025/2026 Turbo S Coupe 完整逐年长宽高参考
Porsche 911	跑车	Porsche	911	Coupe	GT3 facelift	gen8 facelift 992.2	2026-2026			179.9	72.9	50.4	2026 Porsche 911 GT3 Coupe	992.2 GT3，低车身，区别于 GT3 RS 大尾翼版本	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS facelift	gen8 facelift 992.2	2025-2026			180.0	74.8	52.0	2025 Porsche 911 GT3 RS; 2026 Porsche 911 GT3 RS pending	GT3 RS 空气套件高风险，需与普通 GT3 拆开	待终核: 缺失 2026 GT3 RS 逐年参考，2025 是否属于 992.2 facelift 仍需终核
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std.	gen1 full-size luxury	2010-2013			195.6	76.0	55.8	2010/2011/2012/2013 Porsche Panamera Liftback	一代标准轴，长度修正为 195.6，取高度最大值	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std. facelift	gen1 facelift full-size luxury	2014-2016			197.4	76.0	55.8	2014/2015/2016 Porsche Panamera Liftback	改款标准轴，2015 低高但取区间最大高度	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Executive LWB	gen1 facelift full-size luxury	2014-2016			203.4	76.0	56.1	2014/2015/2016 Porsche Panamera 4S/Turbo Executive LWB	Executive 长轴，必须拆	可入库
4) 下一步优先核对

下一步只剩 2 个点：2025/2026 Porsche 911 Turbo S Coupe 的完整逐年长宽高，以及 2026 Porsche 911 GT3 RS 是否存在可用尺寸并确认 2025 GT3 RS 是否应归入 992.2 facelift。

5) 下一步

下一步


--- Round 5 / 下一步 ---
1) 更新点

911 Turbo facelift 2025-2026 已补齐 2025/2026：2025 Edmunds 为 178.5 / 74.8 / 51.3，2026 Car and Driver 为 179.2 / 74.8 / 51.3，因此本行取最大包络 179.2 / 74.8 / 51.3，状态改为 可入库。
Edmunds
+1

911 GT3 facelift 从上一轮 2026-2026 扩回 2025-2026，因为 2025/2026 GT3 均有 179.9 / 72.9 / 50.4 尺寸参考，状态改为 可入库。
Edmunds
+1

911 GT3 RS facelift 2025-2026 修正为 GT3 RS 2025-2025：2025 GT3 RS 可核为 180.0 / 74.8 / 52.0；2026 GT3 RS 当前未形成可用逐年参考，且不应强行覆盖到 2026，所以缩小年份并改为可入库。
Edmunds

2) 当前批次进度

当前批次由原始 10 条补强为 14 条。
本轮后全部记录均为 可入库。
本批次当前已完成。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet	gen8 992	2020-2024			177.9	72.9	51.1	2020/2021/2022/2023/2024 Porsche 911 Carrera Cabriolet	992 Cabriolet 结构不同，标准宽体未并入	可入库
Porsche 911	跑车	Porsche	911	Targa	Std.	gen8 992	2021-2024			177.9	72.9	51.2	2021/2022/2023/2024 Porsche 911 Targa 4/Targa 4S	Targa 结构不同，2024 Targa 4S 高度取 51.2	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo	gen8 992	2021-2024			178.6	74.9	51.3	2021/2022/2023/2024 Porsche 911 Turbo/Turbo S Coupe	Turbo 宽体，区别于 Carrera/GT3/Dakar	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3/GT3 RS	gen8 992	2022-2024			180.0	74.8	52.1	2022/2023/2024 Porsche 911 GT3/GT3 RS Coupe	GT/RS 空气套件高风险；原范围内 2021 不作为 GT3/GT3 RS 覆盖年	可入库
Porsche 911	跑车	Porsche	911	Coupe	Dakar	gen8 992	2023-2024			178.6	73.4	52.7	2023/2024 Porsche 911 Dakar	Dakar 加高，原 2021-2024 范围内仅保留实际 Dakar 年份	可入库
Porsche 911	跑车	Porsche	911	Coupe	Std. facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/Carrera GTS Coupe	992.2 普通 coupe，长度取 GTS 最大	可入库
Porsche 911	跑车	Porsche	911	Convertible	Cabriolet facelift	gen8 facelift 992.2	2025-2026			179.3	72.9	51.3	2025/2026 Porsche 911 Carrera/GTS Cabriolet	Cabriolet 改款，标准/GTS Cabriolet 不并入 Turbo Cabriolet 宽体	可入库
Porsche 911	跑车	Porsche	911	Targa	Std. facelift	gen8 facelift 992.2	2026-2026			179.3	72.9	51.3	2026 Porsche 911 Targa 4S/Targa 4 GTS	Targa 4S/GTS 2026 扩展，取 GTS 长度最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	Turbo facelift	gen8 facelift 992.2	2025-2026			179.2	74.8	51.3	2025/2026 Porsche 911 Turbo/Turbo S Coupe	Turbo/Turbo S 宽体，区别于 GT3；2026 长度取最大	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 facelift	gen8 facelift 992.2	2025-2026			179.9	72.9	50.4	2025/2026 Porsche 911 GT3 Coupe	992.2 GT3，低车身，区别于 GT3 RS 大尾翼版本	可入库
Porsche 911	跑车	Porsche	911	Coupe	GT3 RS	gen8 992	2025-2025			180.0	74.8	52.0	2025 Porsche 911 GT3 RS	GT3 RS 空气套件高风险；2026 未确认不覆盖	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std.	gen1 full-size luxury	2010-2013			195.6	76.0	55.8	2010/2011/2012/2013 Porsche Panamera Liftback	一代标准轴，长度修正为 195.6，取高度最大值	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Std. facelift	gen1 facelift full-size luxury	2014-2016			197.4	76.0	55.8	2014/2015/2016 Porsche Panamera Liftback	改款标准轴，2015 低高但取区间最大高度	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Liftback	Executive LWB	gen1 facelift full-size luxury	2014-2016			203.4	76.0	56.1	2014/2015/2016 Porsche Panamera 4S/Turbo Executive LWB	Executive 长轴，必须拆	可入库
4) 下一步优先核对

无。当前批次所有记录已补强到可入库；未保留 2026 GT3 RS，因为当前 split 原范围内未能形成可用逐年参考，且不能强行扩展或假设覆盖。

本批次完成。

