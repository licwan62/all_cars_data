# 文件名：split_part_02.tsv


--- Round 1 / 首次发送 ---
已


--- Round 2 / 下一步 ---
已思考 4s

已思考 4s


--- Round 3 / 下一步 ---
已思考 8s

已思考 8s


--- Round 4 / 下一步 ---
已思考 16s

已思考 16s


--- Round 5 / 下一步 ---
已思考 10s


--- Round 6 / 下一步 ---
已思考 10s


--- Round 7 / 下一步 ---
已思考 10s


--- Round 8 / 下一步 ---
已思考 12s


--- Round 9 / 下一步 ---
已思考 17s


--- Round 10 / 下一步 ---
已思考 11s


--- Round 11 / 下一步 ---
已思考 6s


--- Round 12 / 下一步 ---
已思考 13s


--- Round 13 / 下一步 ---
已思考 10s


--- Round 14 / 下一步 ---
已思考 10s


--- Round 15 / 下一步 ---
已思考 10s


--- Round 16 / 下一步 ---
更新点

本轮继续做了版本排除区间细化，不是重复上一轮：

Genesis G80 Sport 2018-2020 备注从 excl: Std. 改为 excl: Std. 2018-2020，把排除年份写完整。

Genesis G80 Std. 2025-2026 备注从 excl: Sport / EV 改为 excl: Sport 2025-2026 / EV，避免后续误解为排除其他年份 Sport。

Genesis G80 Sport 2025-2026 备注从 excl: Std./EV 改为 excl: Std. 2025-2026 / EV，排除边界更清楚。

Honda Ridgeline 2024-2026 备注补充 TrailSport 不单独加宽/加高，说明为什么可压缩进普通行。

当前批次进度

当前 split_part_02：11/11 条已处理。

可入库：11/11。

待终核：0/11。

本轮相比上一轮有实际更新：G80 Sport/Std. 的排除年份边界已细化，Ridgeline TrailSport 合并理由已补强。

本轮更新后的 TSV：

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Genesis G80	三厢车	Genesis	G80	Sedan	Sport	gen1 facelift midsize luxury	2018-2020			196.5	74.4	58.3	2018-2020 Genesis G80 3.3T Sport, Edmunds	Sport trim 独立保留；外观/轮胎不额外扩大入库三维；excl: Std. 2018-2020	可入库
Genesis G80	三厢车	Genesis	G80	Sedan	Std.	gen2 pre-facelift midsize luxury	2021-2024			196.7	75.8	57.7	2021-2024 Genesis G80 non-EV sedan, Edmunds	换代四门 sedan；2024 长度为 196.7，作为区间最大值；excl: EV 2023-2024	可入库
Genesis G80	三厢车	Genesis	G80	Sedan	EV	gen2 pre-facelift midsize luxury	2023-2024			197.0	75.8	57.9	2023-2024 Genesis Electrified G80, Edmunds	美国市场 Electrified G80 覆盖 2023-2024；版本字段按规则规范为 EV；2025 美国市场停售/不作为可入库覆盖年	可入库
Genesis G80	三厢车	Genesis	G80	Sedan	Std.	gen2 facelift midsize luxury	2025-2026			196.7	75.8	57.7	2025-2026 Genesis G80 2.5T standard / non-Sport sedan, Edmunds	2025 改款普通版；按常规 G80 sedan 三维入库，不吃 Sport 最大长度；excl: Sport 2025-2026 / EV	可入库
Genesis G80	三厢车	Genesis	G80	Sedan	Sport	gen2 facelift midsize luxury	2025-2026			197.0	75.8	57.7	2025-2026 Genesis G80 3.5T Sport Prestige / Sport, Edmunds	2025 改款 Sport 类配置最大长度 197.0，独立保留，避免并入 Std. 行导致普通版过度放大；excl: Std. 2025-2026 / EV	可入库
Honda Ridgeline	皮卡	Honda	Ridgeline	Pickup	Std.	gen1 midsize pickup	2006-2014	Crew Cab	5.0	206.9	77.8	71.2	2006-2014 Honda Ridgeline Crew Cab, Edmunds	一代货斗 60 in≈5.0 ft；2014 RTL 高度 71.2 作为区间最大值	可入库
Honda Ridgeline	皮卡	Honda	Ridgeline	Pickup	Std.	gen2 pre-facelift midsize pickup	2017-2020	Crew Cab	5.3	210.0	78.6	70.8	2017-2020 Honda Ridgeline Crew Cab, Edmunds	二代前期；货斗 64 in≈5.3 ft；AWD 高度 70.8 作为最大值	可入库
Honda Ridgeline	皮卡	Honda	Ridgeline	Pickup	Std.	gen2 facelift midsize pickup	2021-2023	Crew Cab	5.3	210.2	78.6	70.8	2021-2023 Honda Ridgeline Crew Cab, Edmunds	2021 前脸改款；货斗 64 in≈5.3 ft	可入库
Honda Ridgeline	皮卡	Honda	Ridgeline	Pickup	Std.	gen2 late facelift midsize pickup	2024-2026	Crew Cab	5.3	210.2	78.6	70.8	2024-2026 Honda Ridgeline Crew Cab / TrailSport, Edmunds / Honda official	2024-2026 普通款与 TrailSport 三维同值，TrailSport 不单独加宽/加高，压缩入同一行；货斗 64 in≈5.3 ft；inc: TrailSport 2024-2026	可入库
Hyundai Genesis	三厢车	Hyundai	Genesis	Sedan	Std.	gen1 pre-facelift midsize luxury	2009-2011			195.9	74.4	58.1	2009-2011 Hyundai Genesis Sedan, Edmunds	初代 Hyundai Genesis sedan 前期；与 2012 facelift 后尺寸不同，单独保留	可入库
Hyundai Genesis	三厢车	Hyundai	Genesis	Sedan	Std.	gen1 facelift midsize luxury	2012-2014			196.3	74.4	58.3	2012-2014 Hyundai Genesis Sedan, Edmunds / Car and Driver	2012 facelift 后长度/高度取最大值；facelift 后最大高度 58.3，不单独拆 R-Spec	可入库

下一步优先核对

当前批次无剩余待终核。

合并总表时优先检查：Genesis G80 2025-2026 Std. 与 Sport 不要被误合并；Honda Ridgeline 2024-2026 已包含 TrailSport，不要重复导入独立 TrailSport 行；Hyundai Genesis 2009-2011 与 2012-2014 保持拆分。

本批次完成。

