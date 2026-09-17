# 文件名：list.tsv


--- Round 1 / 首次发送 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 2 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 3 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 4 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 5 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 6 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 7 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 8 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 9 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 10 / 下一步 ---
ChatGPT 说：更新点

按原始 12 个 MODEL 的顺序建立了 41 条拆分记录，先补入可确认的年份、代际、结构、特殊版本、轴距车身和皮卡组合骨架。

Astro 已按两代以及短轴/LWB 拆分；Avalanche 已按两代、1500/2500 和 Crew 5.3 货斗拆分。当前仅把已有代表年份尺寸写入，未覆盖年份继续保留具体待终核状态。 Edmunds+5维基百科+5Edmunds+5

Blazer EV 已拆分普通版与 SS；2026 年普通版为约 192.2 × 78.0 × 65.1 in，SS 为约 192.7 × 78.0 × 64.8 in，宽度均采用 without mirrors。 Edmunds+2雪佛兰+2

HHR 已拆分普通版、Panel、SS 和单年 Panel SS；Metro 已拆分 Hatchback 与 Sedan；Lumina APV 已单独保留存在尺寸来源冲突的 1993 年。 Edmunds+4Edmunds+4维基百科+4

Silverado 1500HD 已识别 2004 年车型名称中断，并按 2001–2003、2005、2006、2007 Classic 拆分；Venture 已按短轴和长轴拆分，2005 年仅保留长轴。 Cars.com+4Edmunds+4Edmunds+4

Chevy Van、El Camino、S10 已完成代际和主要特殊版本骨架，但 CAB/BED、不同车身长度及逐年尺寸仍存在大量缺失，未进入集中核对阶段。

当前批次进度

已基本补齐结构骨架：Astro、Avalanche、Blazer EV、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture。

当前唯一暂列可入库记录：2025–2026 Blazer EV SS。

部分完成：Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture，主要缺少区间内逐年参考车型覆盖。

缺失较多：Chevy Van、El Camino、S10，尚缺不同轴距或 CAB/BED 组合及对应三维。

Blazer EV 普通版仍需统一 65.0/65.1 in 的高度显示精度。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964-1966	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1964-1966车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							全尺寸van；存在客运/货运及不同轴距车身；按Wagon/两厢车业务口径暂归类	待终核: 1967-1970车身长度拆分、三维和参考车型全部缺失
Chevrolet	Chevy Van	gen3	1971-1996	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴、客运/货运及可能的加高车顶	待终核: 1971-1996车身版本、逐年三维和参考车型全部缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978-1987	Pickup		皮卡	Regular						轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1978-1987名义BED、逐年三维和参考车型缺失
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982-1993	Pickup		皮卡							第一代紧凑型皮卡；存在Regular/Extended及多种货斗	待终核: 1982-1993 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1994-1997	Pickup		皮卡							第二代改款前；存在Regular/Extended及短/长货斗	待终核: 1994-1997 CAB/BED真实组合、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1998-2004	Pickup		皮卡							1998 facelift，代际不变；需另核ZR2宽体/加高差异	待终核: 1998-2004 CAB/BED组合、ZR2拆分、逐年三维和参考车型全部缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular		188.9	67.8	62.4	1997 Chevrolet S10 EV	纯电Regular单排版本	待终核: 1997 EV名义BED及第二可靠规格源缺失
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular		190.8	68.3	62.4	1998 Chevrolet S10 EV	纯电Regular单排版本；1998外形更新	待终核: 1998 EV名义BED及第二可靠规格源缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

下一步优先补缺失：首先补齐 S10 两代各年份的 Regular/Extended/Crew CAB、名义 BED 及真实组合，再单独核对 ZR2 和 EV。

补齐 Chevy Van 三代的短轴/长轴、客运/货运车身及对应三维。

补齐 El Camino 五代的名义货斗长度和各尺寸变化年份。

解决 Lumina APV 1993 年长度、高度来源冲突。

完成上述缺失后，再开始集中逐年补齐 Astro、Avalanche、HHR、Metro、Uplander 和 Venture 的参考车型覆盖。

下一步
继续优先补齐 S10、Chevy Van 和 El Camino 的车身组合、CAB/BED、三维及参考车型，不提前转入全批次尺寸口径核对。


--- Round 11 / 下一步 ---
ChatGPT 说：更新点

S10 不再保留“整代 CAB/BED 全空”的占位行：已按 Regular 6.0、Regular 7.5、Extended 6.0 和 Crew 4.5 建立组合骨架，并把 2WD、4WD 因高度不同而拆开。

补入 1982 S10 官方尺寸：Regular 6.0 为 178.2 × 64.7 × 61.2 in，Regular 7.5 为 194.1 × 64.7 × 61.2 in。GM Heritage Archive 提供对应年度官方 Vehicle Information Kit。通用汽车+1

补入 1993 S10 六个 CAB/BED/驱动尺寸组合。官方技术资料明确列出 2WD 高度 61.3 in、4WD 高度 63.4 in，并列出 73.1/89.0 in 货斗长度。通用汽车+1

补入 1994 和 1998 S10 的六组尺寸框架；1998 官方表还明确注明最大宽度为不含后视镜口径。通用汽车+1

补入 2001–2004 S10 Crew 4.5-ft Bed，尺寸为 205.3 × 67.9 × 63.4 in，实际货斗约 55.2 in。Edmunds+2Edmunds+2

S10 新增 ZR2 待补尺寸行，避免后续将宽体、加高越野版本强行并入普通 4WD。

Chevy Van 已补入 1964 年官方参考车型、167.6 in 长度和约 77.3 in 标准整备高度；W-IN 仍缺少可确认的 without-mirrors 数值。通用汽车+1

El Camino 已将 gen5 的 1978、1987 两个官方年度端点补齐为 201.6 × 71.9 × 53.8 in，并补入名义 6.5-ft 货斗；1979–1986 暂不直接套用端点尺寸。通用汽车+1

当前批次进度

数据缺失阶段继续推进，尚未转入集中逐年核对阶段。

S10：CAB/BED 和驱动高度拆分骨架已明显补强；已完成 1982、1993、1994、1998 和 Crew 2001–2004 的代表配置回填。

S10 仍缺失：1983–1992、1995–1997、1999–2000、2001–2003 Regular/Extended，以及 ZR2 的逐年尺寸。

Chevy Van：1964 年已部分补齐；1965–1996 的轴距、车身长度、宽度和高度仍是主要缺失项。

El Camino：1978 和 1987 已补齐；1959–1977、1979–1986 仍缺逐年三维和货斗口径。

其他车型继续保留上一轮已形成的拆分结构，尚缺的逐年参考车型和尺寸没有提前标记为可入库。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964	Wagon		两厢车			167.6		77.3	1964 Chevrolet G Van	90.0-in wheelbase；标准整备高度约77.28 in；官方资料未在同一尺寸表明确列出车身最大宽度	待终核: 1964缺少without mirrors宽度
Chevrolet	Chevy Van	gen1	1965-1966	Wagon		两厢车							第一代forward-control van；需确认是否延续90-in轴距和1964外廓	待终核: 1965-1966长宽高与参考车型缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							第二代van；存在不同载重级别和车身用途	待终核: 1967-1970轴距、车身长度、without mirrors宽度、高度和参考车型缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴及客运/货运车身	待终核: 1971-1982车身长度组合、三维和参考车型缺失
Chevrolet	Chevy Van	gen3	1983-1996	Wagon		两厢车							后期市场同时使用Chevy Van/G Van/Vandura等名称；需拆短轴/长轴及客运/货运车身	待终核: 1983-1996车型名称边界、车身长度组合、三维和参考车型缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular							轿车式coupe utility；需检查1973-1977保险杠变化导致的长度差异	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿约79.5 in、底部约78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5					未直接套用1978/1987端点尺寸；需逐年检查前后保险杠及外饰变化	待终核: 1979-1986逐年长宽高与参考车型缺失
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿约79.5 in、底部约78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982	Pickup		皮卡	Regular	6.0	178.2	64.7	61.2	1982 Chevrolet S-10 Regular Cab 6.0-ft Bed	73.1-in货斗按名义6.0填写；官方尺寸为标准装备、空载状态	待终核: 1982尺寸缺少第二可靠规格源
Chevrolet	S10	gen1	1982	Pickup		皮卡	Regular	7.5	194.1	64.7	61.2	1982 Chevrolet S-10 Regular Cab 7.5-ft Bed	89.0-in货斗按名义7.5填写；官方尺寸为标准装备、空载状态	待终核: 1982尺寸缺少第二可靠规格源
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Regular	6.0					2WD普通版；73-in级短货斗	待终核: 1983-1992 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Regular	6.0					4WD高度与2WD不同，独立保留	待终核: 1983-1992 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Regular	7.5					2WD长货斗版本；89-in级货斗	待终核: 1983-1992 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Regular	7.5					4WD长货斗版本	待终核: 1983-1992 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Extended	6.0					Extended驾驶室配短货斗	待终核: 1983-1992 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Extended	6.0					4WD Extended驾驶室配短货斗	待终核: 1983-1992 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1993	Pickup		皮卡	Regular	6.0	178.2	64.7	61.3	1993 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；2WD；W-IN按官方maximum width	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.4	1993 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup		皮卡	Regular	7.5	194.2	64.7	61.3	1993 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；2WD	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.4	1993 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup		皮卡	Extended	6.0	192.8	64.7	61.3	1993 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；2WD	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.4	1993 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen2	1994	Pickup		皮卡	Regular	6.0	188.7	67.9	63.0	1994 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；第二代首年；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	64.5	1994 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup		皮卡	Regular	7.5	204.6	67.9	63.7	1994 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	64.6	1994 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup		皮卡	Extended	6.0	203.3	67.9	61.9	1994 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	64.6	1994 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Regular	6.0					2WD普通短货斗版本	待终核: 1995-1997 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Regular	6.0					4WD普通短货斗版本	待终核: 1995-1997 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Regular	7.5					2WD长货斗版本	待终核: 1995-1997 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Regular	7.5					4WD长货斗版本	待终核: 1995-1997 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Extended	6.0					2WD Extended短货斗版本	待终核: 1995-1997 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Extended	6.0					4WD Extended短货斗版本	待终核: 1995-1997 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Regular	6.0					普通2WD短货斗	待终核: 1999-2000 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Regular	6.0					普通4WD短货斗	待终核: 1999-2000 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Regular	7.5					普通2WD长货斗	待终核: 1999-2000 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Regular	7.5					普通4WD长货斗	待终核: 1999-2000 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Extended	6.0					普通2WD Extended短货斗	待终核: 1999-2000 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Extended	6.0					普通4WD Extended短货斗	待终核: 1999-2000 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Regular	6.0					普通2WD短货斗	待终核: 2001-2003 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Regular	6.0					普通4WD短货斗	待终核: 2001-2003 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Regular	7.5					普通2WD长货斗	待终核: 2001-2003 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Regular	7.5					普通4WD长货斗	待终核: 2001-2003 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Extended	6.0					普通2WD Extended短货斗	待终核: 2001-2003 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Extended	6.0	205.3	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；当前三维仅由2003参考覆盖	待终核: 2001-2002逐年尺寸与参考车型缺失
Chevrolet	S10	gen2	2001-2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2002 Chevrolet S-10 Crew Cab 4.5-ft Bed; 2003 Chevrolet S-10 Crew Cab 4.5-ft Bed; 2004 Chevrolet S-10 Crew Cab 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD；W-IN按without mirrors	待终核: 2001 Crew逐年参考车型及2001配置尺寸缺失
Chevrolet	S10	gen2	1994-2003	Pickup	ZR2	皮卡	Regular	6.0					宽轮距、加高越野版本；不得并入普通4WD	待终核: 1994-2003 ZR2 Regular逐年存在性、长宽高和参考车型缺失
Chevrolet	S10	gen2	1994-2003	Pickup	ZR2	皮卡	Extended	6.0					宽轮距、加高越野版本；不得并入普通4WD	待终核: 1994-2003 ZR2 Extended逐年存在性、长宽高和参考车型缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

**下一步优先补缺失：**补齐 S10 1983–1992、1995–1997、1999–2000 和 2001–2003 Regular/Extended 的逐年三维与参考车型。

补齐 S10 ZR2 Regular/Extended 的实际宽度、高度、销售年份和对应 CAB/BED；确认是否还需独立保留 Xtreme。

按 90/108/108–125 in 等实际轴距和车身长度，继续拆分 Chevy Van 1965–1996。

补齐 El Camino 1959–1977 和 1979–1986 的逐年外廓尺寸及名义 BED。

上述尺寸空值清除后，再进入第二阶段，集中核对逐年覆盖、without-mirrors 口径和迭代状态。

下一步
继续优先补齐 S10 尚为空的普通版和 ZR2 三维，并同步补充 Chevy Van 的短轴、长轴车身尺寸。


--- Round 12 / 下一步 ---
ChatGPT 说：更新点

S10 不再保留“整代 CAB/BED 全空”的占位行：已按 Regular 6.0、Regular 7.5、Extended 6.0 和 Crew 4.5 建立组合骨架，并把 2WD、4WD 因高度不同而拆开。

补入 1982 S10 官方尺寸：Regular 6.0 为 178.2 × 64.7 × 61.2 in，Regular 7.5 为 194.1 × 64.7 × 61.2 in。GM Heritage Archive 提供对应年度官方 Vehicle Information Kit。通用汽车+1

补入 1993 S10 六个 CAB/BED/驱动尺寸组合。官方技术资料明确列出 2WD 高度 61.3 in、4WD 高度 63.4 in，并列出 73.1/89.0 in 货斗长度。通用汽车+1

补入 1994 和 1998 S10 的六组尺寸框架；1998 官方表还明确注明最大宽度为不含后视镜口径。通用汽车+1

补入 2001–2004 S10 Crew 4.5-ft Bed，尺寸为 205.3 × 67.9 × 63.4 in，实际货斗约 55.2 in。Edmunds+2Edmunds+2

S10 新增 ZR2 待补尺寸行，避免后续将宽体、加高越野版本强行并入普通 4WD。

Chevy Van 已补入 1964 年官方参考车型、167.6 in 长度和约 77.3 in 标准整备高度；W-IN 仍缺少可确认的 without-mirrors 数值。通用汽车+1

El Camino 已将 gen5 的 1978、1987 两个官方年度端点补齐为 201.6 × 71.9 × 53.8 in，并补入名义 6.5-ft 货斗；1979–1986 暂不直接套用端点尺寸。通用汽车+1

当前批次进度

数据缺失阶段继续推进，尚未转入集中逐年核对阶段。

S10：CAB/BED 和驱动高度拆分骨架已明显补强；已完成 1982、1993、1994、1998 和 Crew 2001–2004 的代表配置回填。

S10 仍缺失：1983–1992、1995–1997、1999–2000、2001–2003 Regular/Extended，以及 ZR2 的逐年尺寸。

Chevy Van：1964 年已部分补齐；1965–1996 的轴距、车身长度、宽度和高度仍是主要缺失项。

El Camino：1978 和 1987 已补齐；1959–1977、1979–1986 仍缺逐年三维和货斗口径。

其他车型继续保留上一轮已形成的拆分结构，尚缺的逐年参考车型和尺寸没有提前标记为可入库。

当前批次尚未完成。

本轮更新后的全量 TSV
tsvMAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1989	Wagon		两厢车							minivan/van轮廓；短轴车身；按Wagon/两厢车业务口径暂归类	待终核: 1985-1989短轴逐年三维与参考车型缺失
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro	短轴车身；客运/货运外壳共用关系待逐年确认；W-IN按without mirrors	待终核: 1991-1994逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro EXT	加长车身；EXT市场名称写入参考车型；W-IN按without mirrors	待终核: 1991-1994 LWB逐年尺寸与参考车型未补齐
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro	1995起取消短轴车身；客运/货运外壳关系待核；W-IN按without mirrors	待终核: 1996-2005逐年尺寸与参考车型未补齐
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；W-IN按without mirrors	待终核: 2004-2006逐年三维与参考车型未补齐
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；W-IN按without mirrors	待终核: 2008-2013逐年三维与参考车型未补齐
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964	Wagon		两厢车			167.6		77.3	1964 Chevrolet G Van	90.0-in wheelbase；标准整备高度约77.28 in；官方资料未在同一尺寸表明确列出车身最大宽度	待终核: 1964缺少without mirrors宽度
Chevrolet	Chevy Van	gen1	1965-1966	Wagon		两厢车							第一代forward-control van；需确认是否延续90-in轴距和1964外廓	待终核: 1965-1966长宽高与参考车型缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon		两厢车							第二代van；存在不同载重级别和车身用途	待终核: 1967-1970轴距、车身长度、without mirrors宽度、高度和参考车型缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon		两厢车							G-Series全尺寸van；需拆短轴/长轴及客运/货运车身	待终核: 1971-1982车身长度组合、三维和参考车型缺失
Chevrolet	Chevy Van	gen3	1983-1996	Wagon		两厢车							后期市场同时使用Chevy Van/G Van/Vandura等名称；需拆短轴/长轴及客运/货运车身	待终核: 1983-1996车型名称边界、车身长度组合、三维和参考车型缺失
Chevrolet	El Camino	gen1	1959-1960	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1959-1960名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen2	1964-1967	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1964-1967名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen3	1968-1972	Pickup		皮卡	Regular							轿车式coupe utility；一体式单排驾驶室和货斗	待终核: 1968-1972名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen4	1973-1977	Pickup		皮卡	Regular							轿车式coupe utility；需检查1973-1977保险杠变化导致的长度差异	待终核: 1973-1977名义BED、逐年三维和参考车型缺失
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿约79.5 in、底部约78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5					未直接套用1978/1987端点尺寸；需逐年检查前后保险杠及外饰变化	待终核: 1979-1986逐年长宽高与参考车型缺失
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿约79.5 in、底部约78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV	minivan轮廓；W-IN按车身宽度口径	待终核: 1991-1992逐年三维与参考车型未补齐
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车				73.9			1993为前后尺寸记录交界年，聚合资料同时列入两组长度/高度	待终核: 1993 L-IN与H-IN来源冲突，参考车型缺失
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina Minivan	1994起市场名称常简化为Lumina Minivan；代际不变	待终核: 1995-1996逐年三维与参考车型未补齐
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback	Chevrolet品牌Metro仅覆盖1998-2001；W-IN按without mirrors	待终核: 1999-2000 Hatchback逐年尺寸与参考车型未补齐
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；W-IN按without mirrors	待终核: 1999-2000 Sedan逐年尺寸与参考车型未补齐
Chevrolet	S10	gen1	1982	Pickup		皮卡	Regular	6.0	178.2	64.7	61.2	1982 Chevrolet S-10 Regular Cab 6.0-ft Bed	73.1-in货斗按名义6.0填写；官方尺寸为标准装备、空载状态	待终核: 1982尺寸缺少第二可靠规格源
Chevrolet	S10	gen1	1982	Pickup		皮卡	Regular	7.5	194.1	64.7	61.2	1982 Chevrolet S-10 Regular Cab 7.5-ft Bed	89.0-in货斗按名义7.5填写；官方尺寸为标准装备、空载状态	待终核: 1982尺寸缺少第二可靠规格源
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Regular	6.0					2WD普通版；73-in级短货斗	待终核: 1983-1992 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Regular	6.0					4WD高度与2WD不同，独立保留	待终核: 1983-1992 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Regular	7.5					2WD长货斗版本；89-in级货斗	待终核: 1983-1992 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Regular	7.5					4WD长货斗版本	待终核: 1983-1992 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup		皮卡	Extended	6.0					Extended驾驶室配短货斗	待终核: 1983-1992 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1983-1992	Pickup	4WD	皮卡	Extended	6.0					4WD Extended驾驶室配短货斗	待终核: 1983-1992 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1993	Pickup		皮卡	Regular	6.0	178.2	64.7	61.3	1993 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；2WD；W-IN按官方maximum width	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.4	1993 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup		皮卡	Regular	7.5	194.2	64.7	61.3	1993 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；2WD	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.4	1993 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup		皮卡	Extended	6.0	192.8	64.7	61.3	1993 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；2WD	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen1	1993	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.4	1993 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立	待终核: 1993配置存在性需第二来源交叉确认
Chevrolet	S10	gen2	1994	Pickup		皮卡	Regular	6.0	188.7	67.9	63.0	1994 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；第二代首年；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	64.5	1994 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup		皮卡	Regular	7.5	204.6	67.9	63.7	1994 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	64.6	1994 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup		皮卡	Extended	6.0	203.3	67.9	61.9	1994 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1994	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	64.6	1994 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1994尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Regular	6.0					2WD普通短货斗版本	待终核: 1995-1997 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Regular	6.0					4WD普通短货斗版本	待终核: 1995-1997 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Regular	7.5					2WD长货斗版本	待终核: 1995-1997 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Regular	7.5					4WD长货斗版本	待终核: 1995-1997 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup		皮卡	Extended	6.0					2WD Extended短货斗版本	待终核: 1995-1997 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1995-1997	Pickup	4WD	皮卡	Extended	6.0					4WD Extended短货斗版本	待终核: 1995-1997 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Regular	6.0					普通2WD短货斗	待终核: 1999-2000 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Regular	6.0					普通4WD短货斗	待终核: 1999-2000 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Regular	7.5					普通2WD长货斗	待终核: 1999-2000 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Regular	7.5					普通4WD长货斗	待终核: 1999-2000 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup		皮卡	Extended	6.0					普通2WD Extended短货斗	待终核: 1999-2000 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	1999-2000	Pickup	4WD	皮卡	Extended	6.0					普通4WD Extended短货斗	待终核: 1999-2000 4WD Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Regular	6.0					普通2WD短货斗	待终核: 2001-2003 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Regular	6.0					普通4WD短货斗	待终核: 2001-2003 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Regular	7.5					普通2WD长货斗	待终核: 2001-2003 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Regular	7.5					普通4WD长货斗	待终核: 2001-2003 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup		皮卡	Extended	6.0					普通2WD Extended短货斗	待终核: 2001-2003 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen2	2001-2003	Pickup	4WD	皮卡	Extended	6.0	205.3	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；当前三维仅由2003参考覆盖	待终核: 2001-2002逐年尺寸与参考车型缺失
Chevrolet	S10	gen2	2001-2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2002 Chevrolet S-10 Crew Cab 4.5-ft Bed; 2003 Chevrolet S-10 Crew Cab 4.5-ft Bed; 2004 Chevrolet S-10 Crew Cab 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD；W-IN按without mirrors	待终核: 2001 Crew逐年参考车型及2001配置尺寸缺失
Chevrolet	S10	gen2	1994-2003	Pickup	ZR2	皮卡	Regular	6.0					宽轮距、加高越野版本；不得并入普通4WD	待终核: 1994-2003 ZR2 Regular逐年存在性、长宽高和参考车型缺失
Chevrolet	S10	gen2	1994-2003	Pickup	ZR2	皮卡	Extended	6.0					宽轮距、加高越野版本；不得并入普通4WD	待终核: 1994-2003 ZR2 Extended逐年存在性、长宽高和参考车型缺失
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```
下一步优先处理

**下一步优先补缺失：**补齐 S10 1983–1992、1995–1997、1999–2000 和 2001–2003 Regular/Extended 的逐年三维与参考车型。

补齐 S10 ZR2 Regular/Extended 的实际宽度、高度、销售年份和对应 CAB/BED；确认是否还需独立保留 Xtreme。

按 90/108/108–125 in 等实际轴距和车身长度，继续拆分 Chevy Van 1965–1996。

补齐 El Camino 1959–1977 和 1979–1986 的逐年外廓尺寸及名义 BED。

上述尺寸空值清除后，再进入第二阶段，集中核对逐年覆盖、without-mirrors 口径和迭代状态。

下一步
继续优先补齐 S10 尚为空的普通版和 ZR2 三维，并同步补充 Chevy Van 的短轴、长轴车身尺寸。

