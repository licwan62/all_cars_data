# 文件名：split_part_06.tsv


--- Round 1 / 首次发送 ---
ChatGPT 说：1) 更新点


本轮新增可入库记录数量：1


本轮新增完成三维口径数量：1


Nissan Frontier 原记录只覆盖 2005-2007，本轮清理掉参考车型中混入的 2010/2011/2012/2013/2018/2019/2020/2021；并将驾驶室类型由 extended 规范为 King Cab。


Nissan Frontier 2005/2006/2007 King Cab 6ft 已逐年核对：2005 为 205.5/72.8/68.7，2006 为 205.5/72.8/69.7，2007 为 205.5/72.8/69.7，因此压缩行取最大高度 69.7，可入库。Edmunds+2Edmunds+2


Ford F-350 DRW 行继续保留待终核：公开 Edmunds 可核到 2017 Regular Cab 8ft 的 231.8/80.0/80.9，但这是非 DRW 宽度口径；2018 Edmunds 可核到 266.2/96.0/81.1 的 DRW Crew Cab 8ft，不对应 Regular Cab 行。Edmunds+1


2) 当前批次进度


当前批次共 7 条记录。


本轮已推进 1 条为可入库：Nissan Frontier 2005-2007 King Cab 6ft。


F-350 Super Duty DRW 共 6 条仍待终核，主要缺口是 DRW + 指定 cab/bed 的完整官方或 Edmunds/KBB 三维口径。


因本轮已有新增可入库记录与新增完成三维口径记录，暂不额外扩展到谨慎来源落表；下一轮优先继续查 Ford 官方 brochure / order guide、KBB 分 trim specs、J.D. Power/NADA 交叉验证。


3) 本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen3 Super Duty pickup	2016	Crew Cab	8	263	96	79.8	2016 F-350 Crew Cab DRW 8 ft	宽体后双轮; 单年拆分; Edmunds可核263.0长度但公开页宽度79.9/高度80.8疑似非DRW口径，暂不直接替代DRW行	待终核: 缺少2016 Crew Cab DRW 8 ft完整三维口径来源Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2017	Regular Cab	8	231.8	96	81.2	2017 F-350 DRW Regular Cab 8 ft	宽体后双轮; Edmunds Regular Cab公开页为231.8/80.0/80.9，宽度为非DRW口径; 当前96宽体需继续复核	待终核: 缺少2017 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2018	Regular Cab	8	231.8	96	81.2	2018 F-350 DRW Regular Cab 8 ft	宽体后双轮; 已核到2018 Crew Cab DRW 8ft为266.2/96.0/81.1但不对应Regular Cab; Regular Cab DRW仍缺口	待终核: 缺少2018 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2019	Regular Cab	8	231.8	96	81.2	2019 F-350 DRW Regular Cab 8 ft	宽体后双轮; Regular Cab公开页多为非DRW宽体口径; 不采用普通80.0宽度页直接入库	待终核: 缺少2019 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Regular Cab	8	231.8	96	81.3	2025 F-350 DRW Regular Cab 8 ft	宽体后双轮; Edmunds 2025公开页为250.0/80.0/81.4等非本行DRW Regular 8ft口径; 当前按2026保守控制	待终核: 已核公开页非本行口径，缺2025 DRW Regular Cab 8 ft最大高度口径Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Crew Cab	8	266.2	96	81.5	2025 F-350 Crew Cab DRW 8 ft	宽体后双轮; 4x2 DRW已核266.2/96/79.5; Ford官方2025页含F-350 DRW尾门高度分项但未直接给本行完整三维; 当前按全配置最大高度81.5保守控制	待终核: 已核2025 4x2 DRW，缺2025 4x4 DRW或全配置最大高度口径Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6	205.5	72.8	69.7	2005-2007 Nissan Frontier King Cab 6 ft	6ft斗; 2005-2007逐年核对完成; 2005高度68.7，2006/2007高度69.7，压缩行取最大高度69.7; 已移除当前年份范围外的2010+参考	可入库
4) 下一步优先核对


Ford 2016 F-350 Crew Cab DRW 8ft：优先查 Ford 官方 brochure/order guide、KBB Crew Cab DRW 分 trim、J.D. Power/NADA。


Ford 2017/2018/2019 F-350 Regular Cab DRW 8ft：优先查 Ford towing guide / fleet order guide / KBB Regular Cab DRW 分 trim。


Ford 2025 F-350 DRW Regular Cab 与 Crew Cab 8ft：优先查 Ford 官方 specs、commercial/fleet order guide、KBB 2025 specs。


下一步


--- Round 2 / 下一步 ---
ChatGPT 说：1) 更新点


本轮新增可入库记录数量：2


本轮新增完成三维口径数量：2


已用 Ford 2025 官方 Super Duty 外部尺寸页/PDF 闭合 2025 F-350 DRW Regular Cab 8ft 与 Crew Cab 8ft：官方表给出 Regular Cab 8ft 长度 231.8，Crew Cab LWB 8ft 长度 266.2；F-350 DRW 高度分别为 Regular Cab 4x2/4x4 = 79.4/81.3，Crew Cab LWB 4x2/4x4 = 79.5/81.5；DRW 不含镜宽度为 96。https://www.ford.com/+1


2016 F-350 Crew Cab DRW 8ft 继续不强行入库：Edmunds 当前可见页对应 Crew Cab 4WD LB 的 263.0/79.9/80.8，更像 SRW 或非 DRW 宽体口径，不能替代 DRW 96 宽记录。Edmunds


2017-2019 Regular Cab DRW 8ft 继续待终核：2017 Edmunds Regular Cab 8ft 可见 231.8/80.0/80.9，仍是非 DRW 宽度；2018/2019 当前可见 DRW 96 宽样本更多落在 Crew Cab 8ft，不能直接套 Regular Cab。Edmunds+2Edmunds+2


2) 当前批次进度


当前批次共 7 条记录。


已可入库：3 条


2025 F-350 DRW Regular Cab 8ft


2025 F-350 DRW Crew Cab 8ft


2005-2007 Nissan Frontier King Cab 6ft




仍待终核：4 条


2016 F-350 Crew Cab DRW 8ft


2017 F-350 Regular Cab DRW 8ft


2018 F-350 Regular Cab DRW 8ft


2019 F-350 Regular Cab DRW 8ft




3) 本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen3 Super Duty pickup	2016	Crew Cab	8	263	96	79.8	2016 F-350 Crew Cab DRW 8 ft	宽体后双轮; 单年拆分; Edmunds当前可见Crew Cab 4WD LB为263.0/79.9/80.8，宽度非DRW口径，不能替代本行96宽体记录; 原79.8高度暂保留	待终核: 缺少2016 Crew Cab DRW 8 ft完整三维口径来源Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2017	Regular Cab	8	231.8	96	81.2	2017 F-350 DRW Regular Cab 8 ft	宽体后双轮; Edmunds Regular Cab公开页为231.8/80.0/80.9，宽度为非DRW口径; 当前96宽体需继续复核; 高度81.2暂按原保守值	待终核: 缺少2017 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2018	Regular Cab	8	231.8	96	81.2	2018 F-350 DRW Regular Cab 8 ft	宽体后双轮; 已核到2018 Crew Cab DRW 8ft为266.2/96.0/81.1但不对应Regular Cab; Regular Cab DRW仍缺口; 高度81.2暂按原保守值	待终核: 缺少2018 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2019	Regular Cab	8	231.8	96	81.2	2019 F-350 DRW Regular Cab 8 ft	宽体后双轮; 已核到2019 Crew Cab DRW 8ft为266.2/96.0/81.1但不对应Regular Cab; Regular Cab公开页多为非DRW宽体口径	待终核: 缺少2019 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Regular Cab	8	231.8	96	81.3	2025 F-350 DRW Regular Cab 8 ft	宽体后双轮; Ford官方2025 Super Duty外部尺寸表已核Regular Cab 8ft: 4x2/4x4长度231.8，F-350 DRW高度79.4/81.3，DRW宽度96; 压缩行取4x4最大高度81.3	可入库Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Crew Cab	8	266.2	96	81.5	2025 F-350 Crew Cab DRW 8 ft	宽体后双轮; Ford官方2025 Super Duty外部尺寸表已核Crew Cab LWB 8ft: 4x2/4x4长度266.2，F-350 DRW高度79.5/81.5，DRW宽度96; 压缩行取4x4最大高度81.5	可入库Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6	205.5	72.8	69.7	2005-2007 Nissan Frontier King Cab 6 ft	6ft斗; 2005-2007逐年核对完成; 2005高度68.7，2006/2007高度69.7，压缩行取最大高度69.7; 已移除当前年份范围外的2010+参考	可入库
4) 下一步优先核对


2016 F-350 Crew Cab DRW 8ft：追加查 Ford 2016 Super Duty brochure / fleet order guide / body builder layout book、KBB 分 trim specs、J.D. Power/NADA。


2017/2018/2019 F-350 Regular Cab DRW 8ft：追加查 Ford 官方 towing guide、fleet order guide、body builder layout book；如果官方表只给 SRW 宽度，再用 KBB/NADA 交叉验证 DRW 宽度与 4x4 最大高度。


下一步


--- Round 3 / 下一步 ---
ChatGPT 说：1) 更新点


本轮新增可入库记录数量：1


本轮新增完成三维口径数量：1


本轮闭合 2019 Ford F-350 Super Duty DRW Regular Cab 8 ft：2019 Ford Super Duty 官方 brochure 规格表给出 Regular Cab 8' Box 长度 231.8、DRW 不含镜宽度 96.0、F-350 DRW 高度 78.8/81.6，因此本行取最大高度 81.6，推进为可入库。Dealereprocess+1


2017/2018 Regular Cab DRW 仍不强行入库：2017 Edmunds Regular Cab 页为 231.8/80.0/80.9，是非 DRW 宽度口径；2018 当前能核到 DRW 宽度/高度线索，但缺少同年官方完整 Regular Cab DRW 8ft 三维表。Edmunds+1


2) 当前批次进度


当前批次共 7 条记录。


已可入库：4 条


2019 F-350 DRW Regular Cab 8ft


2025 F-350 DRW Regular Cab 8ft


2025 F-350 DRW Crew Cab 8ft


2005-2007 Nissan Frontier King Cab 6ft




仍待终核：3 条


2016 F-350 Crew Cab DRW 8ft


2017 F-350 Regular Cab DRW 8ft


2018 F-350 Regular Cab DRW 8ft




3) 本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen3 Super Duty pickup	2016	Crew Cab	8	263	96	79.8	2016 F-350 Crew Cab DRW 8 ft	宽体后双轮; 单年拆分; Edmunds当前可见Crew Cab 4WD LB为263.0/79.9/80.8，宽度非DRW口径，不能替代本行96宽体记录; 原79.8高度暂保留	待终核: 缺少2016 Crew Cab DRW 8 ft完整三维口径来源Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2017	Regular Cab	8	231.8	96	81.2	2017 F-350 DRW Regular Cab 8 ft	宽体后双轮; Edmunds Regular Cab公开页为231.8/80.0/80.9，宽度为非DRW口径; 已追加查2017 towing/product sheet线索但缺官方完整三维表; 高度81.2暂按原保守值	待终核: 缺少2017 DRW Regular Cab 8 ft完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2018	Regular Cab	8	231.8	96	81.2	2018 F-350 DRW Regular Cab 8 ft	宽体后双轮; 当前可查到2018 F-350 DRW宽度96/高度约81线索，但缺同年官方Regular Cab DRW 8ft完整长宽高表; 不直接用dealer线索入库	待终核: 缺少2018 DRW Regular Cab 8 ft官方或KBB完整口径复核Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2019	Regular Cab	8	231.8	96	81.6	2019 F-350 DRW Regular Cab 8 ft	Ford 2019 Super Duty官方brochure规格表已核Regular Cab 8ft长度231.8，DRW不含镜宽度96.0，F-350 DRW高度78.8/81.6; 压缩行取4x4最大高度81.6	可入库Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Regular Cab	8	231.8	96	81.3	2025 F-350 DRW Regular Cab 8 ft	宽体后双轮; Ford官方2025 Super Duty外部尺寸表已核Regular Cab 8ft: 4x2/4x4长度231.8，F-350 DRW高度79.4/81.3，DRW宽度96; 压缩行取4x4最大高度81.3	可入库Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Crew Cab	8	266.2	96	81.5	2025 F-350 Crew Cab DRW 8 ft	宽体后双轮; Ford官方2025 Super Duty外部尺寸表已核Crew Cab LWB 8ft: 4x2/4x4长度266.2，F-350 DRW高度79.5/81.5，DRW宽度96; 压缩行取4x4最大高度81.5	可入库Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6	205.5	72.8	69.7	2005-2007 Nissan Frontier King Cab 6 ft	6ft斗; 2005-2007逐年核对完成; 2005高度68.7，2006/2007高度69.7，压缩行取最大高度69.7; 已移除当前年份范围外的2010+参考	可入库
4) 下一步优先核对


2016 F-350 Crew Cab DRW 8ft：继续查 Ford 2016 Super Duty brochure / fleet order guide / body builder layout book、KBB、J.D. Power/NADA。


2017 F-350 Regular Cab DRW 8ft：继续查 2017 Ford Super Duty product sheet 可打开版本、KBB Regular Cab DRW、NADA。


2018 F-350 Regular Cab DRW 8ft：继续查 2018 Ford Super Duty USA brochure 可解析版本、KBB Regular Cab DRW、J.D. Power/NADA；dealer/listing 仅作线索，不直接落表。


下一步


--- Round 4 / 下一步 ---
ChatGPT 说：1) 更新点


本轮新增可入库记录数量：3


本轮新增完成三维口径数量：3


2016 F-350 Crew Cab DRW 8ft 已用 Ford 2016 官方 brochure 技术规格闭合：Crew Cab LWB 长度 263.0，DRW 不含镜宽度 96.0，F-350 DRW 高度 77.3/79.9，取最大高度 79.9。Dealereprocess+1


2017 F-350 Regular Cab DRW 8ft 已用 Ford 2017 官方 brochure 技术规格闭合：Regular Cab LWB 长度 231.8，DRW 不含镜宽度 96.0，F-350 DRW 高度 78.1/80.6，取最大高度 80.6。Dealereprocess+1


2018 F-350 Regular Cab DRW 8ft 已用 Ford 2018 官方 brochure 技术规格闭合：Regular Cab 8ft 长度 231.8，DRW 不含镜宽度 96.0，F-350 DRW 高度 78.1/80.6，取最大高度 80.6。Dealereprocess+1


至此当前 split_part_06 共 7 条全部闭合为可入库。


2) 当前批次进度


当前批次共 7 条记录。


已可入库：7 条。


待终核：0 条。


本轮修正了 3 条 F-350 的高度口径：


2016 Crew Cab DRW 8ft：79.8 → 79.9


2017 Regular Cab DRW 8ft：81.2 → 80.6


2018 Regular Cab DRW 8ft：81.2 → 80.6




3) 本轮更新后的 TSV

`tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen3 Super Duty pickup	2016	Crew Cab	8	263	96	79.9	2016 Ford F-350 Crew Cab DRW 8 ft	Ford 2016 Super Duty官方brochure技术规格已核Crew Cab LWB 8ft: 长度263.0，DRW不含镜宽度96.0，F-350 DRW高度77.3/79.9; 压缩行取4x4最大高度79.9	可入库
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2017	Regular Cab	8	231.8	96	80.6	2017 Ford F-350 Regular Cab DRW 8 ft	Ford 2017 Super Duty官方brochure技术规格已核Regular Cab LWB 8ft: 长度231.8，DRW不含镜宽度96.0，F-350 DRW高度78.1/80.6; 压缩行取4x4最大高度80.6	可入库
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2018	Regular Cab	8	231.8	96	80.6	2018 Ford F-350 Regular Cab DRW 8 ft	Ford 2018 Super Duty官方brochure技术规格已核Regular Cab 8ft: 长度231.8，DRW不含镜宽度96.0，F-350 DRW高度78.1/80.6; 压缩行取4x4最大高度80.6	可入库
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen4 Super Duty pickup	2019	Regular Cab	8	231.8	96	81.6	2019 Ford F-350 Regular Cab DRW 8 ft	Ford 2019 Super Duty官方brochure规格表已核Regular Cab 8ft长度231.8，DRW不含镜宽度96.0，F-350 DRW高度78.8/81.6; 压缩行取4x4最大高度81.6	可入库
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Regular Cab	8	231.8	96	81.3	2025 Ford F-350 Regular Cab DRW 8 ft	Ford官方2025 Super Duty外部尺寸表已核Regular Cab 8ft: 4x2/4x4长度231.8，F-350 DRW高度79.4/81.3，DRW宽度96; 压缩行取4x4最大高度81.3	可入库
Ford F-350 Super Duty	皮卡	Ford	F-350 Super Duty	Pickup	DRW	gen5 Super Duty pickup	2025	Crew Cab	8	266.2	96	81.5	2025 Ford F-350 Crew Cab DRW 8 ft	Ford官方2025 Super Duty外部尺寸表已核Crew Cab LWB 8ft: 4x2/4x4长度266.2，F-350 DRW高度79.5/81.5，DRW宽度96; 压缩行取4x4最大高度81.5	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6	205.5	72.8	69.7	2005-2007 Nissan Frontier King Cab 6 ft	6ft斗; 2005-2007逐年核对完成; 2005高度68.7，2006/2007高度69.7，压缩行取最大高度69.7; 已移除当前年份范围外的2010+参考	可入库
`
4) 下一步优先核对
无。当前 split_part_06 已全部可入库。
本批次完成。

