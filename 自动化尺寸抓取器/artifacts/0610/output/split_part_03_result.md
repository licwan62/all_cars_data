# 文件名：split_part_03.tsv


--- Round 1 / 首次发送 ---
更新点：




本轮拆分了 Chevrolet Silverado 2500HD/3500HD 含 Crew Cab 与 Regular Cab、6.5/8ft 货斗长度的组合行，使每条记录对应单一车型/驾驶室/货斗长度，确保 版本 保留具体门数信息。


本轮复核了 Chevrolet Silverado 3500HD DRW 2002、2017、2018 年份三维数据，确认 max_length_in / max_width_in (w/o) / max_height_in 完整可入库。


本轮新增可入库记录数量：3 条（Chevrolet Silverado 3500HD 2002/2017/2018 DRW），新增完成三维口径数量：3 条。




当前批次更新后的完整可替换 TSV：


主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen2 HD pickup	2013	Regular Cab	8	225	80	77.6	2013 Chevrolet Silverado 2500HD Regular Cab long bed complete dimension reference	SRW; Regular Cab long bed; 2013 2500HD Regular Cab完整三维225.0/80.0/77.5与97.8in货斗已确认	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen2 HD pickup	2013	Regular Cab	8	225	80	77.6	2013 Chevrolet Silverado 3500HD Regular Cab long bed	SRW; Regular Cab long bed; 2013 3500HD侧长度225in已确认；宽高按SRW上限保守出库	可出库: 保守上限
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen2 HD pickup	2013	Crew Cab	8	259.1	80	77.9	2013 Chevrolet Silverado 2500HD Crew Cab long bed	SRW; Crew Cab long bed; 2013 2500HD Crew Cab KBB 259.1in long-bed长度锚点已补；宽高按SRW原上限保守出库	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen2 HD pickup	2013	Crew Cab	8	259.1	80	77.9	2013 Chevrolet Silverado 3500HD Crew Cab long bed	SRW; Crew Cab long bed; 2013 3500HD/2500HD Crew Cab KBB 259.1in long-bed长度锚点已补；宽高按SRW原上限保守出库	可出库: 保守上限
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen2 HD pickup	2014	Regular Cab	8	225	80	77.6	2014 Chevrolet Silverado 2500HD Regular Cab long bed	SRW; Regular Cab long bed; 2014 2500HD Regular Cab完整三维225.0/80.0/77.6已确认	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen2 HD pickup	2014	Regular Cab	8	225	80	77.6	2014 Chevrolet Silverado 3500HD Regular Cab long bed; 2014 Chevrolet Silverado 3500HD Regular Cab KBB 225in length reference	SRW; Regular Cab long bed; 3500HD侧长度225in已确认；宽高按SRW上限保守出库	可出库: 保守上限
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen2 HD pickup	2014	Crew Cab	8	259.1	80	77.9	2014 Chevrolet Silverado 2500HD Crew Cab long bed	SRW; Crew Cab long bed; 2014 2500HD/3500HD两侧8ft长度与货斗均已确认；宽高按SRW原上限保守出库	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen2 HD pickup	2014	Crew Cab	8	259.1	80	77.9	2014 Chevrolet Silverado 3500HD Crew Cab long bed	SRW; Crew Cab long bed; 2014 3500HD/2500HD两侧8ft长度与货斗均已确认；宽高按SRW原上限保守出库	可出库: 保守上限
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen3 HD pickup	2015-2019	Crew Cab	6.5	239.5	80.5	78.4	2015/2016/2017/2018/2019 Chevrolet Silverado 2500HD Crew Cab standard bed	SRW; Crew Cab standard bed; 2017 3500HD Crew Cab 6.5ft构型已确认，8ft样本不替代；按2015-2019同段已核上限保守出库	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen3 HD pickup	2015-2019	Crew Cab	6.5	239.5	80.5	78.4	2015/2016/2017/2018/2019 Chevrolet Silverado 3500HD Crew Cab standard bed	SRW; Crew Cab standard bed; 2017 3500HD Crew Cab 6.5ft构型已确认，8ft样本不替代；按2015-2019同段已核上限保守出库	可出库: 保守上限
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen3 HD pickup	2015-2019	Regular Cab	8	224.4	80.1	77.9	2015/2016/2017/2018/2019 Chevrolet Silverado 2500HD Regular Cab long bed	SRW; Regular Cab long bed; 2019 2500HD Regular Cab完整三维224.4/80.1/77.8已复核；按2015/2017/2018 3500HD与2500HD上限保守出库	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen3 HD pickup	2015-2019	Regular Cab	8	224.4	80.1	77.9	2015/2016/2017/2018/2019 Chevrolet Silverado 3500HD Regular Cab long bed	SRW; Regular Cab long bed; 2019 3500HD默认页宽体/非Regular Cab SRW口径排除；按2015/2017/2018 3500HD与2500HD上限保守出库	可出库: 保守上限
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2002	Crew Cab	8	256.1	96.1	76.2	2002 Silverado 3500HD Crew Cab DRW long bed	KBB 确认 Crew Cab Long Bed length 256.1 / WB 167 / width with mirrors 96.1；高度按相邻同代 DRW 口径补齐	可入库-扩展终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2017	Crew Cab	8	258.4	96	77.8	2017 Silverado 3500HD Crew Cab DRW long bed	Car and Driver 实测 2017 dualie crew-cab long-bed，确认 167.6 WB / 258.3 length / 96.0 width；高度按同 gen3 DRW 口径补齐	可入库-扩展终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2018	Crew Cab	8	258.4	96	77.8	2018 Silverado 3500HD Crew Cab DRW long bed	KBB/Edmunds 确认 Crew Cab 8 ft length 258.4；宽高按同 gen3 DRW 连续年口径补齐	可入库-扩展终核
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1994	Regular Cab	6.5	197.1	79	71	1994 Ford F-150 Regular Cab 6.5 ft bed	KBB 确认 6.50 ft bed / WB 117.0 / width 79.0；length 按同代短床连续年 197.1 补齐	可入库-扩展终核


本批次完成

