# 文件名：list.tsv


--- 恢复现场 / 已有回复 ---
更新点

* 将 S10 第一代原先覆盖 `1983-1992`、但三维全部为空的 6 个 CAB/BED/驱动组合拆为 `1983-1988` 与 `1989-1992` 两段，避免已补年份继续被空值阻塞。
* 已逐年读取 1983、1984、1985、1986、1987、1988 Chevrolet S-10 官方 Vehicle Information Kit；六个年度的 Regular 6.0、Regular 7.5、Extended 6.0 外廓尺寸保持一致。([通用汽车][1])
* 补齐 1983-1988 S10 Regular 6.0：2WD 为 `178.2 × 64.7 × 61.3 in`，4WD 为 `178.2 × 64.7 × 63.4 in`。
* 补齐 1983-1988 S10 Regular 7.5：2WD 为 `194.2 × 64.7 × 61.3 in`，4WD 为 `194.2 × 64.7 × 63.4 in`。
* 补齐 1983-1988 S10 Extended 6.0：2WD 为 `192.8 × 64.7 × 61.3 in`，4WD 为 `192.8 × 64.7 × 63.4 in`。
* 1983-1988 各组合的参考车型已改为完整连续年份覆盖；1989-1992 继续单独保留具体尺寸缺失状态，未直接套用前期数据。
* 当前仍处于第一阶段补缺失，没有把尚缺尺寸或参考车型的记录改为可入库。

当前批次进度

* 本轮实际完成：S10 第一代 1983-1988 六个 CAB/BED/驱动组合的年份、长度、宽度、高度和参考车型覆盖。
* S10 第一代剩余缺失：1989-1992 六个组合的逐年三维和参考车型。
* S10 第二代剩余缺失：1995-1997、1999-2000、2001-2003 多个 Regular/Extended 组合，以及 ZR2。
* Chevy Van 仍是当前最大的车型级缺失项：1965-1996 多数轴距与车身长度组合尚未展开。
* El Camino 仍缺 1959-1977、1979-1986 的逐年尺寸和参考车型。
* Astro 1985-1989、Lumina APV 1993 等记录仍有关键空值。
* 当前批次尚未完成。

本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
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
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Regular	6.0	178.2	64.7	61.3	1983-1988 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；六个年度官方尺寸一致；标准装备、空载状态	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.4	1983-1988 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Regular	7.5	194.2	64.7	61.3	1983-1988 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.4	1983-1988 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Extended	6.0	192.8	64.7	61.3	1983-1988 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.4	1983-1988 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1989-1992	Pickup		皮卡	Regular	6.0					2WD普通版；不得直接沿用1983-1988尺寸	待终核: 1989-1992 Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1989-1992	Pickup	4WD	皮卡	Regular	6.0					4WD高度需逐年确认；不得直接沿用1983-1988尺寸	待终核: 1989-1992 4WD Regular 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1989-1992	Pickup		皮卡	Regular	7.5					2WD长货斗版本；需确认各年实际存在性	待终核: 1989-1992 Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1989-1992	Pickup	4WD	皮卡	Regular	7.5					4WD长货斗版本；需确认各年实际存在性	待终核: 1989-1992 4WD Regular 7.5逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1989-1992	Pickup		皮卡	Extended	6.0					Extended驾驶室短货斗；需逐年确认	待终核: 1989-1992 Extended 6.0逐年长宽高与参考车型缺失
Chevrolet	S10	gen1	1989-1992	Pickup	4WD	皮卡	Extended	6.0					4WD Extended驾驶室短货斗；需逐年确认	待终核: 1989-1992 4WD Extended 6.0逐年长宽高与参考车型缺失
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

1. **下一步优先补缺失：**继续读取 1989、1990、1991、1992 S10 官方年度资料，补齐第一代剩余六个 CAB/BED/驱动组合。
2. 补齐 S10 第二代 1995-1997、1999-2000、2001-2003 的 Regular/Extended 三维，优先清除当前空白单元格。
3. 单独建立并补齐 S10 ZR2 的实际销售年份、CAB、BED、宽度和高度，不与普通4WD共用尺寸。
4. 随后处理 Chevy Van，按实际轴距和短轴/长轴车身拆分 1965-1996。
5. 补齐 El Camino 1959-1977、1979-1986 以及 Astro 1985-1989 的尺寸空值。

下一步

继续优先补齐 S10 1989-1992 六个 CAB/BED/驱动组合的逐年长宽高和参考车型。

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1983-Chevrolet-S-10.pdf "pages"


--- Round 1 / 存档续跑 ---
更新点

* 补齐 S10 第一代最后一组关键空值：1989–1992 的 Regular 6.0、Regular 7.5、Extended 6.0，以及对应 4WD，共 6 类组合已全部补入长宽高和参考车型。
* 1989–1990 官方资料显示六类基础车身的长度保持为 178.2、194.2、192.8 in，宽度为 64.8 in；2WD 高度为 61.3 in，4WD 高度为 63.4 in。([通用汽车][1])
* 1991 年不能与相邻年份强行合并：宽度变为 64.7 in；Regular 2WD 高度为 61.6 in，Extended 2WD 和基础 4WD 高度为 63.5 in。官方表同时列出 Baja 外挂灯架或前部附件后的更大长度、高度，本表采用无外挂附件的基础车身外廓。
* 1992 年宽度继续为 64.7 in，但基础高度恢复为 2WD 61.3 in、4WD 63.4 in，因此单独拆行，未与 1991 合并。([通用汽车][2])
* S10 gen1 的 1982–1993 主要 CAB/BED/驱动组合目前均已有尺寸，不再存在整段长宽高空白；后续只需转入宽度口径和第二来源核对。
* 当前仍处于第一阶段补缺失，S10 gen2、Chevy Van、El Camino、Astro 等仍有关键空值，本轮未扩大“可入库”范围。

当前批次进度

* 已完成主要尺寸补齐：Blazer EV、Silverado 1500HD、S10 gen1。
* S10 gen1：1982–1993 的 Regular 6.0、Regular 7.5、Extended 6.0 主要组合已补齐；剩余问题为 without-mirrors 宽度口径和部分配置第二来源。
* S10 gen2：1995–1997、1999–2000、2001–2003 的普通 Regular/Extended 组合仍有尺寸空值；ZR2 仍缺完整三维。
* Chevy Van：1965–1996 多数短轴、长轴车身仍未拆全并补入尺寸。
* El Camino：1959–1977、1979–1986 仍缺逐年三维和参考车型。
* Astro 1985–1989、Lumina APV 1993 仍有关键尺寸空值。
* 当前批次尚未完成。

本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
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
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Regular	6.0	178.2	64.7	61.3	1983-1988 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；六个年度官方尺寸一致；标准装备、空载状态	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.4	1983-1988 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Regular	7.5	194.2	64.7	61.3	1983-1988 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.4	1983-1988 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup		皮卡	Extended	6.0	192.8	64.7	61.3	1983-1988 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1983-1988	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.4	1983-1988 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；4WD高度独立；六个年度官方尺寸一致	待终核: 1983-1988 W-IN是否明确为without mirrors仍需终核
Chevrolet	S10	gen1	1989-1990	Pickup		皮卡	Regular	6.0	178.2	64.8	61.3	1989-1990 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；两年官方基础车身三维一致	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1989-1990	Pickup	4WD	皮卡	Regular	6.0	178.2	64.8	63.4	1989-1990 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；基础4WD，不含外挂灯架或越野附件	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1989-1990	Pickup		皮卡	Regular	7.5	194.2	64.8	61.3	1989-1990 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；两年官方基础车身三维一致	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1989-1990	Pickup	4WD	皮卡	Regular	7.5	194.2	64.8	63.4	1989-1990 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；基础4WD	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1989-1990	Pickup		皮卡	Extended	6.0	192.8	64.8	61.3	1989-1990 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；两年官方基础车身三维一致	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1989-1990	Pickup	4WD	皮卡	Extended	6.0	192.8	64.8	63.4	1989-1990 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；基础4WD	待终核: 1989-1990 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup		皮卡	Regular	6.0	178.2	64.7	61.6	1991 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；1991高度与1990/1992不同	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.5	1991 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	采用基础4WD车身；官方另列Baja附件后194.5-in长度和72.1-in灯架高度，不纳入本行	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup		皮卡	Regular	7.5	194.2	64.7	61.6	1991 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；1991高度独立	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.5	1991 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；基础4WD	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup		皮卡	Extended	6.0	192.8	64.7	63.5	1991 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；官方表列Extended 2WD高度63.5 in	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1991	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.5	1991 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	采用基础4WD车身；官方另列Baja附件后209.1-in长度和72.1-in灯架高度，不纳入本行	待终核: 1991 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup		皮卡	Regular	6.0	178.2	64.7	61.3	1992 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	73.1-in货斗；1992基础车身高度恢复为61.3 in	待终核: 1992 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup	4WD	皮卡	Regular	6.0	178.2	64.7	63.4	1992 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	73.1-in货斗；基础4WD	待终核: 1992 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup		皮卡	Regular	7.5	194.2	64.7	61.3	1992 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；1992基础车身高度61.3 in	待终核: 1992 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup	4WD	皮卡	Regular	7.5	194.2	64.7	63.4	1992 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	89.0-in货斗；基础4WD	待终核: 1992 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup		皮卡	Extended	6.0	192.8	64.7	61.3	1992 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	73.1-in货斗；1992 Extended 2WD高度61.3 in	待终核: 1992 W-IN未明确标注without mirrors
Chevrolet	S10	gen1	1992	Pickup	4WD	皮卡	Extended	6.0	192.8	64.7	63.4	1992 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	73.1-in货斗；基础4WD	待终核: 1992 W-IN未明确标注without mirrors
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

1. **下一步优先补缺失：**补齐 S10 gen2 1995–1997 的 Regular 6.0、Regular 7.5、Extended 6.0 及对应 4WD 三维和参考车型。
2. 补齐 S10 gen2 1999–2000、2001–2003 的普通 CAB/BED 组合，清除当前长宽高空白。
3. 单独核对并补入 S10 ZR2 的实际销售年份、Regular/Extended CAB、6.0-ft BED、宽体宽度和加高高度。
4. 补齐 Astro 1985–1989 的短轴三维和逐年参考车型。
5. 随后处理 Chevy Van 1965–1996 和 El Camino 1959–1977、1979–1986 的大段尺寸空值。

下一步

继续优先补齐 S10 gen2 1995–1997 的六个普通 CAB/BED/驱动组合。

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1989-Chevrolet-S-10.pdf "pages"
[2]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1992-Chevrolet-S-10.pdf "pages"


--- 脚本异常 ---
异常: Playwright browser 请求失败 (tab-new): {"ok":false,"error":"browserContext.newPage: Target page, context or browser has been closed\n    at activePage (D:\\Home\\Scripts\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:62:85)\n    at async runAction (D:\\Home\\Scripts\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:93:16)\n    at async Server. (D:\\Home\\Scripts\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:167:20)"}

