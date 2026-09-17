# 文件名：list.tsv


--- 恢复现场 / 已有回复 ---
## 1. 更新点

* 将原来两条笼统的 `1994-2003 ZR2` 空白占位行，拆为按年份与 CAB 实际变化排列的 11 条记录。
* ZR2 的 CAB 边界已明确：1994 年先用于 Regular，1995 年扩展到 Extended；Regular 延续至 1999 年，2000–2003 年仅保留 Extended。2001 官方资料也明确 ZR2 仅用于 LS Extended Cab。([维基百科][1])
* 补入 1994、1995、1996–1997 ZR2 的基础车身长度和对应参考车型；宽体最大宽度及加高后高度暂不引用普通 4WD 数据，继续留作具体缺失。
* 1998 ZR2 已拆为 Regular 与 Extended；Extended 已补入 `204.8 in` 长度和 `63.4 in` 聚合高度，但其 `67.9 in` 数据与 ZR2 宽轮距、轮眉外扩特征存在口径冲突，因此 W-IN 暂留空。
* 1999 ZR2 已完整拆分：

  * Regular：`190.1 × 71.9 × 64.3 in`
  * Extended：`204.7 × 71.9 × 64.3 in`
    两个 style-specific 规格页均将宽度标为 without mirrors。([Edmunds][2])
* 2000 ZR2 仅保留 Extended，补入 `204.7 × 71.9 × 63.4 in`；未继续生成 Regular ZR2。([Edmunds][3])
* 2001 ZR2 已确认仅为 Extended 6.0，但 Cars.com 页面内部同时出现相互矛盾的车长、宽度和高度数据，因此本轮只补 CAB、BED 和参考车型，不拼接冲突三维。([Cars.com][4])
* 2002–2003 ZR2 已补入 `205.3 in` 长度和 `66.4 in` 高度；来源所列 `67.9 in` 宽度与 1999–2000 Wide Stance 的 `71.9 in` 冲突，因此 W-IN 继续留空，避免错误入库。([Edmunds][5])
* 同步修改 1999–2003 普通 4WD 行的状态，不再写“ZR2 尚未拆分”，改为普通版自身的来源或口径待核事项。

## 2. 当前批次进度

* S10 普通版：1982–2003 的主要实际 CAB/BED 组合均已有三维；2004 仅保留 Crew 4WD。
* S10 ZR2：

  * 已补齐完整三维：1999 Regular、1999 Extended、2000 Extended。
  * 部分补齐：1994–1998、2001–2003。
  * 主要剩余缺失：1994–1998 的 ZR2 最大车身宽度和高度、2001 的一致三维、2002–2003 的最大宽体宽度。
* S10 Xtreme/ZQ8 仍未建立独立尺寸行。
* Astro 1985–1989、Lumina APV 1993 仍有关键尺寸空值。
* Chevy Van 仍有大段轴距、车身长度和三维缺失。
* El Camino 1959–1977、1979–1986 仍缺逐年尺寸和参考车型。
* 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3. 本轮更新后的全量 TSV

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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999 Xtreme等特殊低悬架版本尚未独立补齐
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999特殊外观和悬架版本尚未独立补齐
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999 Xtreme Extended尺寸尚未独立补齐
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐；Xtreme尚未拆分
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取；Xtreme Extended尚未拆分
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；官方基础车身尺寸	待终核: 2001 Xtreme/ZQ8特殊悬架尺寸尚未独立补齐
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通版尺寸已补齐，特殊低悬架版本边界未确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；W-IN按官方车身宽度	待终核: 2001 Xtreme/ZQ8 Extended尺寸尚未独立补齐
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；当年取消Regular长货斗	待终核: 2002 Xtreme/ZQ8特殊悬架尺寸尚未独立补齐
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；2WD Extended采用117.9-in轴距，长度与4WD Extended不同	待终核: 2002 Xtreme/ZQ8 Extended尺寸尚未独立补齐
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD	待终核: 2003 Xtreme/ZQ8特殊悬架尺寸尚未独立补齐
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；122.9-in轴距	待终核: 2003 Xtreme/ZQ8 Extended尺寸尚未独立补齐
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；Cars.com同一页面内部三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5. 下一步优先处理

1. **下一步优先补缺失：**补齐 S10 Xtreme/ZQ8 1999–2003 的 Regular/Extended CAB、长度和降低悬架后的高度，确认是否需要独立版本行。
2. 继续解决 S10 ZR2 1994–1998、2001–2003 的宽体 without-mirrors 宽度，优先查官方 order guide、brochure 和年度技术表。
3. 补齐 Astro 1985–1989 的短轴三维和逐年参考车型。
4. 解决 Lumina APV 1993 的长度、高度和参考车型空值。
5. 按轴距及短轴/长轴车身拆分 Chevy Van 1965–1996，并补齐三维。
6. 补齐 El Camino 1959–1977、1979–1986 的 BED、长宽高和参考车型。

下一步

继续优先补齐 S10 Xtreme/ZQ8 的实际年份、CAB、BED、长度和降低悬架后的高度。

[1]: https://en.wikipedia.org/wiki/RPO_ZR2 "https://en.wikipedia.org/wiki/RPO_ZR2"
[2]: https://www.edmunds.com/chevrolet/s-10/1999/st-14654/features-specs/ "Used 1999 Chevrolet S-10 LS Wide Stance Specs & Features | Edmunds"
[3]: https://www.edmunds.com/chevrolet/s-10/2000/st-1699/features-specs/?utm_source=chatgpt.com "Used 2000 Chevrolet S-10 LS Wide Stance Specs & Features | Edmunds"
[4]: https://www.cars.com/research/chevrolet-s_10-2001/specs/5690/ "https://www.cars.com/research/chevrolet-s_10-2001/specs/5690/"
[5]: https://www.edmunds.com/chevrolet/s-10/2002/st-100002838/features-specs/?utm_source=chatgpt.com "Used 2002 Chevrolet S-10 LS ZR2 Specs & Features"


--- Round 1 / 存档续跑 ---
## 1. 更新点

* S10 Xtreme 已从普通版待核事项中独立拆出。确认 1999–2003 年均同时存在 Regular 与 Extended、2WD、短货斗组合；2004 年因美国市场只保留 Crew Cab，不再保留 Xtreme。([汽车频道][1])
* 补齐 1999–2000 Xtreme：

  * Regular：190.1 × 67.9 × 62.0 in
  * Extended：204.7 × 67.9 × 62.7 in
    两者宽度均为 without mirrors。([Edmunds][2])
* 补齐 2001 Xtreme：

  * Regular：190.1 × 67.9 × 62.1 in
  * Extended：205.3 × 67.9 × 62.7 in
    2001 Regular 的高度与普通年度表 62.0 in 存在 0.1 in 来源差异，继续具体标记待终核。([Cars.com][3])
* 补齐 2002–2003 Xtreme：

  * Regular：190.0 × 67.9 × 62.0 in
  * Extended：205.3 × 67.9 × 62.7 in。([Edmunds][4])
* 已核对 ZQ8：2002–2003 的 Regular/Extended ZQ8 公开外廓尺寸与对应普通 2WD 短货斗一致。ZQ8 属运动悬架配置，但没有形成独立长宽高边界，因此本轮不单独新增版本行，只在备注中记录合并处理。这是基于规格表作出的业务适配判断。([Edmunds][5])
* 修正上一轮 S10 区域重复记录：删除重复出现的 1997 S10 EV 行。
* 普通版 1999–2003 的状态已移除“Xtreme/ZQ8 尚未拆分”，改为其自身仍待解决的尺寸来源或口径问题。

## 2. 当前批次进度

* 已完成主要数据补齐：Blazer EV、S10 gen1、S10 gen2 普通版、S10 Xtreme、Silverado 1500HD。
* S10 ZQ8：已完成是否拆行判断，不独立拆分。
* S10 ZR2：1999–2000 已有完整三维；1994–1998、2001–2003 仍缺部分宽体宽度或存在来源冲突。
* Astro 1985–1989 仍缺三维，是下一项优先补缺失对象。
* Lumina APV 1993 仍缺 L-IN、H-IN 和参考车型。
* Chevy Van 1964–1996 仍存在大量轴距、短轴/长轴车身和三维缺失。
* El Camino 1959–1977、1979–1986 仍缺 BED、逐年三维和参考车型。
* 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3. 本轮更新后的全量 TSV

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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；Cars.com style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5. 下一步优先处理

1. **下一步优先补缺失：**补齐 Astro 1985–1989 短轴版本的逐年长宽高和参考车型。
2. 解决 Lumina APV 1993 的 L-IN、H-IN 与参考车型空值。
3. 继续补齐 S10 ZR2 1994–1998、2001–2003 的最大宽体 without-mirrors 宽度。
4. 按实际轴距和短轴/长轴车身拆分 Chevy Van 1965–1996，并优先补齐长宽高。
5. 补齐 El Camino 1959–1977、1979–1986 的名义 BED、逐年三维和参考车型。
6. 数据空值全部清除后，再进入第二阶段，集中核对逐年参考车型覆盖、宽度口径与迭代状态。

推进信号：CONTINUE

[1]: https://www.theautochannel.com/vehicles/new/reviews/1999/russ9927.html?utm_source=chatgpt.com "Chevrolet S-10 LS Xtreme (1999)"
[2]: https://www.edmunds.com/chevrolet/s-10/1999/regular-cab/st-12987/features-specs/ "Used 1999 Chevrolet S-10 Regular Cab LS Xtreme Specs & Features | Edmunds"
[3]: https://www.cars.com/research/chevrolet-s_10-2001/specs/ "2001 Chevrolet S-10 Specs, Dimensions & Colors | Cars.com"
[4]: https://www.edmunds.com/chevrolet/s-10/2002/regular-cab/st-100072175/features-specs/ "Used 2002 Chevrolet S-10 Regular Cab LS Xtreme Specs & Features | Edmunds"
[5]: https://www.edmunds.com/chevrolet/s-10/2002/st-100002836/features-specs/?utm_source=chatgpt.com "Used 2002 Chevrolet S-10 LS ZQ8 Specs & Features"


--- Round 2 / 下一步 ---
## 1. 更新点

* 将原 `1985-1989 Astro` 空白占位行拆为 `1985-1988` 与 `1989`，因为乘用版整车高度在 1989 年由 73.7 in 变为 74.1 in，不能继续合并。
* 补齐 1985–1988 Astro 短轴乘用版三维：`176.8 × 77.0 × 73.7 in`。1985、1987 和 1988 官方资料中的乘用版尺寸一致；1986 暂按同一阶段尺寸补入，但仍保留“缺少独立官方乘用版尺寸页”的待终核状态。([通用汽车][1])
* 补齐 1989 Astro 短轴乘用版三维：`176.8 × 77.0 × 74.1 in`。1989 官方规格表明确列出 111.0-in 轴距、176.8-in 长度、74.1-in 高度和 77.0-in 宽度。([通用汽车][2])
* 确认同期 Cargo Van 的高度为 74.5 in，与乘用版存在外廓高度差异。当前先完成原乘用版空值，Cargo 是否需要作为独立版本扩展到 1985–1994，将在后续补缺失阶段统一处理。([通用汽车][1])
* Astro 1985–1989 已不再存在 L-IN、W-IN、H-IN 和参考车型全空的问题；当前 Astro 的缺失重点转为 Cargo 版本边界及后续年份逐年参考覆盖。

## 2. 当前批次进度

* 已基本清除关键尺寸空值：Blazer EV、S10 普通版、S10 Xtreme、S10 gen1、Silverado 1500HD、Astro 1985–1989 乘用版。
* Astro 1985–1989：乘用版已补齐；Cargo 高度与乘用版不同，尚未完成独立拆分。
* S10 ZR2：1994–1998、2001–2003 仍缺部分最大宽体宽度或存在来源冲突。
* Lumina APV 1993 仍缺 L-IN、H-IN 与参考车型。
* Chevy Van 1964–1996 仍有大量轴距、车身长度、宽度和高度缺失。
* El Camino 1959–1977、1979–1986 仍缺 BED、逐年三维和参考车型。
* 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3. 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985-1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1986缺少独立官方乘用版尺寸页；1985-1988 Cargo是否需按74.5-in高度独立拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989 Cargo高度74.5 in，是否需要独立版本行尚未处理
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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5. 下一步优先处理

1. **下一步优先补缺失：**解决 Lumina APV 1993 的 L-IN、H-IN 和参考车型空值，优先读取官方 MVMA 外部尺寸页。
2. 按实际轴距、短轴/长轴和客运/货运车身拆分 Chevy Van 1964–1996，优先清除 L-IN、W-IN、H-IN 空白。
3. 补齐 El Camino 1959–1977、1979–1986 的名义 BED、逐年三维和参考车型。
4. 继续补齐 S10 ZR2 1994–1998、2001–2003 的最大宽体 without-mirrors 宽度。
5. 补充 Astro 1990–2005 的逐年参考车型覆盖，并判断 Cargo 是否需要按高度独立拆行。
6. 所有关键尺寸空值清除后，再进入第二阶段，集中核对宽度口径、逐年覆盖和迭代状态。

推进信号：CONTINUE

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1985-Chevrolet-Astro-Van.pdf "pages"
[2]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1989-Chevrolet-Astro-Van.pdf "pages"


--- Round 3 / 下一步 ---
## 1. 更新点

* 补齐 1993 Chevrolet Lumina APV 的关键空值，不再保留长度、高度和参考车型为空的记录。
* 1993 官方 MVMA 外部尺寸页列出：

  * `L103 Vehicle length：194.2 in`
  * `W103 Vehicle width：73.9 in`
  * `W410 Outside mirror width：83.3 in`
  * `H101 Vehicle height：65.7 in`
* 因此本表采用 `194.2 × 73.9 × 65.7 in`，W-IN 明确取不含后视镜的车身宽度 73.9 in，而不是 83.3 in 的外后视镜总宽。公开车型资料也将 1993 年列在 194.2-in 长度与 65.7-in 高度的交界范围内。([维基百科][1])
* 1993 Lumina APV 已补入对应参考车型；原先“存在两组聚合尺寸冲突”的备注已替换为官方尺寸口径说明。
* 当前主要缺失对象转为 Chevy Van、El Camino，以及 S10 ZR2 若干年份的宽体宽度和高度。

## 2. 当前批次进度

* 已清除关键尺寸空值：Astro 乘用版、Blazer EV、Lumina APV 1993、S10 普通版、S10 Xtreme、S10 gen1、Silverado 1500HD。
* Lumina APV 1993 已补齐 L-IN、W-IN、H-IN 和参考车型；仍需在第二阶段核对第二来源及 1993/1994 长度变化边界。
* Chevy Van 1964–1996 仍存在大量轴距、短轴/长轴车身和三维缺失。
* El Camino 1959–1977、1979–1986 仍缺 BED、逐年三维和参考车型。
* S10 ZR2 1994–1998、2001–2003 仍缺部分可靠的最大宽体宽度或存在来源冲突。
* 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3. 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985-1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1986缺少独立官方乘用版尺寸页；1985-1988 Cargo是否需按74.5-in高度独立拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989 Cargo高度74.5 in，是否需要独立版本行尚未处理
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
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5. 下一步优先处理

1. **下一步优先补缺失：**按真实轴距及短轴/长轴车身拆分 Chevy Van 1964–1996，优先补齐 L-IN、W-IN、H-IN 和参考车型。
2. 补齐 El Camino 1959–1977、1979–1986 的名义 BED、逐年三维和参考车型。
3. 继续解决 S10 ZR2 1994–1998、2001–2003 的最大宽体 without-mirrors 宽度和缺失高度。
4. 补充 Astro 1990–2005 的逐年参考车型覆盖，并判断 Cargo 是否因高度差异需要独立拆行。
5. 补齐 HHR、Metro、Uplander、Venture 尚未覆盖的逐年参考车型。
6. 所有关键空值清除后，再进入第二阶段核对尺寸口径、参考覆盖和迭代状态。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Chevrolet_Lumina_APV?utm_source=chatgpt.com "Chevrolet Lumina APV"


--- Round 4 / 下一步 ---
## 1. 更新点

* 将原先覆盖 `1983-1996`、结构和尺寸均未拆开的 Chevy Van 占位行，按第三代真实车身轴距拆为 Short 110 in、Regular 125 in、Extended 146 in 三类。146-in Extended 成品厢式车从 1990 年开始提供，之前主要用于 cutaway chassis。([维基百科][1])
* 新增并补齐 1995 Chevy Van 三种车身：

  * Short：`180.1 × 79.5 × 80.0 in`
  * Regular：`204.1 × 79.5 × 79.7 in`
  * Extended：`225.1 × 79.5 × 82.3 in`
* 1995 GM 官方尺寸表确认三种轴距分别为 110、125、146 in，三种长度分别为 180.1、204.1、225.1 in，官方 Maximum Width 统一列为 79.5 in。
* 1995 Short 的聚合规格页另列 79.1-in without-mirrors 宽度，与 GM 官方技术表 79.5 in 不同；当前以官方技术表为主，并在迭代状态中保留冲突。Regular 的 204.1 × 79.5 × 79.7 in 可由独立规格页交叉覆盖。([Edmunds][2])
* 1995 Extended 高度补入 82.3 in；其 225.1-in 长度、79.5-in 宽度与官方尺寸表一致。([autodetective.com][3])
* 1996 不再与 1983–1995 混在一条记录中：已单独拆出 G-Classic Regular 和 Extended。1996 仅保留高于 8,500 lb GVWR 的 G30/G-Classic 范围，但三维仍待官方尺寸页补入。([维基百科][1])
* 1971–1982、1983–1989、1990–1992 的车身轴距组合骨架已补齐，不再只保留无法成表的整代空白行；本轮没有把 1995 尺寸反向套用到早期年份。

## 2. 当前批次进度

* Chevy Van 的主要车身结构已由 4 条笼统记录扩展为按代际、轴距和车身长度区分的记录。
* Chevy Van 已完整补齐：1995 Short、Regular、Extended 的 CAB/BED 非适用字段、长宽高和参考车型。
* Chevy Van 仍缺：1964 宽度；1965–1970 三维；1971–1994 各轴距车身三维；1996 G-Classic 三维。
* El Camino 1959–1977、1979–1986 仍存在 BED、三维和参考车型缺失。
* S10 ZR2 1994–1998、2001–2003 仍有部分宽度或高度空值。
* 当前仍处于第一阶段补缺失，尚未转入集中核对阶段。

## 3. 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985-1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1986缺少独立官方乘用版尺寸页；1985-1988 Cargo是否需按74.5-in高度独立拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989 Cargo高度74.5 in，是否需要独立版本行尚未处理
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
Chevrolet	Chevy Van	gen1	1964	Wagon	Short	两厢车			167.6		77.3	1964 Chevrolet G Van 90-in Wheelbase	90.0-in wheelbase；标准整备高度约77.3 in	待终核: 1964缺少without-mirrors最大车身宽度
Chevrolet	Chevy Van	gen1	1965-1966	Wagon	Short	两厢车						1965-1966 Chevrolet G10 Chevy Van 90-in Wheelbase	第一代forward-control短轴车身；未直接沿用1964尺寸	待终核: 1965-1966 L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon	Short	两厢车						1967-1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代短轴forward-control车身；90-in wheelbase	待终核: 1967-1970 Short L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen2	1967-1970	Wagon	Regular	两厢车						1967-1970 Chevrolet G10/G20 Chevy Van 108-in Wheelbase	第二代长轴车身；G20仅提供108-in wheelbase	待终核: 1967-1970 Regular L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Short	两厢车						1971-1982 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	第三代短轴车身；110-in wheelbase	待终核: 1971-1982 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Regular	两厢车						1971-1982 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	第三代标准长轴车身；125-in wheelbase	待终核: 1971-1982 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Short	两厢车						1983-1989 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴cargo van；146-in轴距同期主要为cutaway，不作为完整厢式车纳入	待终核: 1983-1989 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Regular	两厢车						1983-1989 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴cargo van	待终核: 1983-1989 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Short	两厢车						1990-1992 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴完整厢式车	待终核: 1990-1992 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Regular	两厢车						1990-1992 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴完整厢式车	待终核: 1990-1992 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Extended	两厢车						1990-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	1990起146-in轴距提供单后轮完整加长厢式车	待终核: 1990-1992 Extended逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993 Chevrolet Chevy Van G10 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short逐年尺寸及1993/1994宽度口径覆盖未补齐
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车						1993-1994 Chevrolet Chevy Van Regular Wheelbase	125-in wheelbase	待终核: 1993-1994 Regular L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车						1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车	待终核: 1993-1994 Extended L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车						1996 Chevrolet G30 G-Classic Regular Wheelbase	1996仅保留GVWR高于8500 lb的G30/G-Classic范围；125-in wheelbase	待终核: 1996 Regular L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车						1996 Chevrolet G30 G-Classic Extended Wheelbase	1996末年加长G-Classic；146-in wheelbase	待终核: 1996 Extended L-IN、W-IN、H-IN缺失
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
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5. 下一步优先处理

1. **下一步优先补缺失：**继续补 Chevy Van，优先处理 1965–1970 的 90/108-in 轴距外廓，以及 1993–1994、1996 三种车身的长宽高。
2. 补齐 El Camino 1959–1977、1979–1986 的名义 BED、逐年长宽高和参考车型。
3. 解决 S10 ZR2 1994–1998、2001–2003 的最大宽体 without-mirrors 宽度与缺失高度。
4. 补充 Astro 1990–2005 的逐年参考车型覆盖，并确定 Cargo 是否因高度差异独立拆行。
5. 清除上述关键尺寸空值后，再进入第二阶段核对尺寸口径、逐年覆盖和迭代状态。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Chevrolet_van?utm_source=chatgpt.com "Chevrolet van"
[2]: https://www.edmunds.com/chevrolet/chevy-van/1995/st-11924/features-specs/?utm_source=chatgpt.com "Used 1995 Chevrolet Chevy Van G10 Specs & Features"
[3]: https://www.autodetective.com/directory/1995/chevrolet/g-series-van/trim/g30-extended/?utm_source=chatgpt.com "1995 Chevrolet G-Series Van G30 Extended Review"


--- Round 5 / 下一步 ---
## 1) 更新点

* 补齐 Chevy Van 第一代全部外廓空值：

  * 1964：`167.6 × 72.7 × 77.3 in`
  * 1965：`167.5 × 72.8 × 77.3 in`
  * 1966：`168.3 × 72.7 × 77.3 in`

  其中 W-IN 采用官方车身/后保险杠最大宽度，不含外后视镜；1965 与 1966 因整车长度不同，已拆为独立年份行。([gm.com][1])

* 将原来笼统的 `1967-1970 Short/Regular` 拆为 G10 Short、G10 Regular 和 G20 Regular。G20 的车高为 79.0 in，明显高于 G10 的 77.3 in，不能继续混在同一 Regular 记录中。([gm.com][2])

* 补齐 1967–1969 第二代三种主体外廓：

  * G10 Short：`171.0 × 75.0 × 77.3 in`
  * G10 Regular：`189.0 × 75.0 × 77.3 in`
  * G20 Regular：`189.0 × 75.0 × 79.0 in`

* 1970 未发现独立 G-Van 技术包；作为同代末年，暂按 1969 同车身外廓补入，并单独保留待官方直接资料终核状态，没有与 1967–1969 直接合并。

* 补齐 1993–1994 Regular 和 Extended：

  * Regular：`204.1 × 79.5 × 79.7 in`
  * Extended：`225.0 × 79.5 × 82.3 in`

  1993–1994 Short 继续保留已取得的 `180.0 × 79.1 × 80.0 in`。([Kbb.com][3])

* 补齐 1996 G-Classic：

  * Regular：`204.1 × 79.5 × 79.7 in`
  * Extended：`225.0 × 79.1 × 82.3 in`

  1996 新平台 135/155-in 轴距规格属于同期 Chevrolet Express/GMT600，不并入本批次的 Chevy Van G-Classic 行。([Edmunds][4])

* 本轮没有转入第二阶段集中核对；Chevy Van 1971–1992 仍有大段外廓空值。

## 2) 当前批次进度

* Chevy Van 1964–1970：结构、轴距版本、长宽高和参考车型均已补齐。
* Chevy Van 1993–1996：Short、Regular、Extended/G-Classic 主体尺寸已补齐。
* Chevy Van 主要剩余缺失：1971–1982、1983–1989、1990–1992 的 Short、Regular、Extended 外廓。
* El Camino 1959–1977、1979–1986 仍缺 BED、三维和参考车型。
* S10 ZR2 1994–1998、2001–2003 仍有部分 W-IN/H-IN 空值。
* 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3) 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985-1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1986缺少独立官方乘用版尺寸页；1985-1988 Cargo是否需按74.5-in高度独立拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989 Cargo高度74.5 in，是否需要独立版本行尚未处理
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
Chevrolet	Chevy Van	gen1	1964	Wagon	G10 Short	两厢车			167.6	72.7	77.3	1964 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 167.56 in、maximum body/rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 官方尺寸已补齐；需第二规格源确认四舍五入口径
Chevrolet	Chevy Van	gen1	1965	Wagon	G10 Short	两厢车			167.5	72.8	77.3	1965 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方图示maximum width 72.75 in、unloaded height 77.25 in	待终核: 1965尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen1	1966	Wagon	G10 Short	两厢车			168.3	72.7	77.3	1966 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 168.30 in、across-rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 1966尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1970未包含在本合并段；1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Short	两厢车						1971-1982 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	第三代短轴车身；110-in wheelbase	待终核: 1971-1982 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Regular	两厢车						1971-1982 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	第三代标准长轴车身；125-in wheelbase	待终核: 1971-1982 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Short	两厢车						1983-1989 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴cargo van；146-in轴距同期主要为cutaway，不作为完整厢式车纳入	待终核: 1983-1989 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Regular	两厢车						1983-1989 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴cargo van	待终核: 1983-1989 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Short	两厢车						1990-1992 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴完整厢式车	待终核: 1990-1992 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Regular	两厢车						1990-1992 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴完整厢式车	待终核: 1990-1992 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Extended	两厢车						1990-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	1990起146-in轴距提供单后轮完整加长厢式车	待终核: 1990-1992 Extended逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
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
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5) 下一步优先处理

1. **下一步优先补缺失：**继续补齐 Chevy Van 1971–1982 的 110/125-in 车身三维，按 G10/G20/G30 高度差异拆分。
2. 补齐 Chevy Van 1983–1989 Short/Regular，以及 1990–1992 Short/Regular/Extended 的长宽高。
3. 补齐 El Camino 1959–1977、1979–1986 的 BED、长宽高和参考车型。
4. 解决 S10 ZR2 1994–1998、2001–2003 的 W-IN/H-IN 空值。
5. 所有关键空值清除后，再进入第二阶段逐年核对参考车型、without-mirrors 口径及迭代状态。

推进信号：CONTINUE

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1964-Chevrolet-G-Van.pdf "pages"
[2]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1967-Chevrolet-G-Van.pdf "pages"
[3]: https://www.kbb.com/chevrolet/g-series-g30/1993/van/?utm_source=chatgpt.com "1993 Chevy G-Series G30 Van Price, Listings & Reviews | Kelley Blue Book"
[4]: https://www.edmunds.com/chevrolet/chevy-van-classic/1996/st-13262/features-specs/?utm_source=chatgpt.com "Used 1996 Chevrolet Chevy Van Classic G30 Specs & ..."


--- Round 6 / 下一步 ---
## 1) 更新点

- 补齐 Chevy Van 第一代全部外廓空值：
- 1964：`167.6 × 72.7 × 77.3 in`
- 1965：`167.5 × 72.8 × 77.3 in`
- 1966：`168.3 × 72.7 × 77.3 in`
其中 W-IN 采用官方车身/后保险杠最大宽度，不含外后视镜；1965 与 1966 因整车长度不同，已拆为独立年份行。gm.com+2gm.com+2
- 将原来笼统的 `1967-1970 Short/Regular` 拆为 G10 Short、G10 Regular 和 G20 Regular。G20 的车高为 79.0 in，明显高于 G10 的 77.3 in，不能继续混在同一 Regular 记录中。gm.com+1
- 补齐 1967–1969 第二代三种主体外廓：
- G10 Short：`171.0 × 75.0 × 77.3 in`
- G10 Regular：`189.0 × 75.0 × 77.3 in`
- G20 Regular：`189.0 × 75.0 × 79.0 in`
- 1970 未发现独立 G-Van 技术包；作为同代末年，暂按 1969 同车身外廓补入，并单独保留待官方直接资料终核状态，没有与 1967–1969 直接合并。
- 补齐 1993–1994 Regular 和 Extended：
- Regular：`204.1 × 79.5 × 79.7 in`
- Extended：`225.0 × 79.5 × 82.3 in`
1993–1994 Short 继续保留已取得的 `180.0 × 79.1 × 80.0 in`。Kbb.com+2autodetective.com+2
- 补齐 1996 G-Classic：
- Regular：`204.1 × 79.5 × 79.7 in`
- Extended：`225.0 × 79.1 × 82.3 in`
1996 新平台 135/155-in 轴距规格属于同期 Chevrolet Express/GMT600，不并入本批次的 Chevy Van G-Classic 行。Edmunds+2维基百科+2
- 本轮没有转入第二阶段集中核对；Chevy Van 1971–1992 仍有大段外廓空值。

## 2) 当前批次进度

- Chevy Van 1964–1970：结构、轴距版本、长宽高和参考车型均已补齐。
- Chevy Van 1993–1996：Short、Regular、Extended/G-Classic 主体尺寸已补齐。
- Chevy Van 主要剩余缺失：1971–1982、1983–1989、1990–1992 的 Short、Regular、Extended 外廓。
- El Camino 1959–1977、1979–1986 仍缺 BED、三维和参考车型。
- S10 ZR2 1994–1998、2001–2003 仍有部分 W-IN/H-IN 空值。
- 当前仍处于第一阶段补缺失，当前批次尚未完成。

## 3) 本轮更新后的全量 TSV

```
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985-1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1986缺少独立官方乘用版尺寸页；1985-1988 Cargo是否需按74.5-in高度独立拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989 Cargo高度74.5 in，是否需要独立版本行尚未处理
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
Chevrolet	Chevy Van	gen1	1964	Wagon	G10 Short	两厢车			167.6	72.7	77.3	1964 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 167.56 in、maximum body/rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 官方尺寸已补齐；需第二规格源确认四舍五入口径
Chevrolet	Chevy Van	gen1	1965	Wagon	G10 Short	两厢车			167.5	72.8	77.3	1965 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方图示maximum width 72.75 in、unloaded height 77.25 in	待终核: 1965尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen1	1966	Wagon	G10 Short	两厢车			168.3	72.7	77.3	1966 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 168.30 in、across-rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 1966尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1970未包含在本合并段；1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Short	两厢车						1971-1982 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	第三代短轴车身；110-in wheelbase	待终核: 1971-1982 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1971-1982	Wagon	Regular	两厢车						1971-1982 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	第三代标准长轴车身；125-in wheelbase	待终核: 1971-1982 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Short	两厢车						1983-1989 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴cargo van；146-in轴距同期主要为cutaway，不作为完整厢式车纳入	待终核: 1983-1989 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1983-1989	Wagon	Regular	两厢车						1983-1989 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴cargo van	待终核: 1983-1989 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Short	两厢车						1990-1992 Chevrolet G10/G20 Chevy Van 110-in Wheelbase	短轴完整厢式车	待终核: 1990-1992 Short逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Regular	两厢车						1990-1992 Chevrolet G10/G20/G30 Chevy Van 125-in Wheelbase	标准长轴完整厢式车	待终核: 1990-1992 Regular逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1990-1992	Wagon	Extended	两厢车						1990-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	1990起146-in轴距提供单后轮完整加长厢式车	待终核: 1990-1992 Extended逐年L-IN、W-IN、H-IN缺失
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
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
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
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
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	6.0	188.7	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方技术表基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1995 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；基础2WD长货斗	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1995 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1995 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；Extended基础2WD车身	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1995	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1995 W-IN虽为官方maximum width但未明确标注without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	6.0	188.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；两年4WD基础高度一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Regular	7.5	204.6	67.9	62.1	1996-1997 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；两年官方三维一致	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.4	1996-1997 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD长货斗高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup		皮卡	Extended	6.0	203.3	67.9	62.2	1996-1997 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；1996起Extended可配第三侧门，基础外廓不变	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1996-1997	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD Extended高度独立	待终核: 1996-1997 W-IN未在表下注明without mirrors
Chevrolet	S10	gen2	1997	Pickup	EV	皮卡	Regular	6.0	188.9	67.8	62.4	1997 Chevrolet S-10 EV Regular Cab	纯电Regular单排；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1997 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	6.0	188.6	67.9	63.2	1998 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；官方资料注明maximum width shown without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	6.0	188.6	67.9	63.9	1998 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Regular	7.5	204.6	67.9	63.3	1998 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Regular	7.5	204.6	67.9	65.0	1998 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup		皮卡	Extended	6.0	203.3	67.9	63.3	1998 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	4WD	皮卡	Extended	6.0	203.3	67.9	63.9	1998 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；4WD高度独立	待终核: 1998尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1998	Pickup	EV	皮卡	Regular	6.0	190.8	68.3	62.4	1998 Chevrolet S-10 EV Regular Cab	纯电Regular单排；1998外形更新；名义6.0-ft货斗暂按同轴距燃油车归类	待终核: 1998 EV货斗实际长度及without mirrors宽度需官方资料确认
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	1999 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；facelift后长度增加；W-IN由官方明确标注without mirrors	待终核: 1999普通2WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	1999 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD高度，不含ZR2宽轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	1999 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；W-IN按without mirrors	待终核: 1999普通长货斗尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Regular	7.5	206.1	67.9	64.4	1999 Chevrolet S-10 Regular Cab 4WD 7.5-ft Bed	88.8-in货斗；该4WD长货斗组合见于1999官方尺寸表	待终核: 1999普通4WD长货斗尺寸缺少第二来源
Chevrolet	S10	gen2	1999	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	1999 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 1999普通Extended 2WD尺寸缺少第二可靠来源
Chevrolet	S10	gen2	1999	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	1999 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；基础4WD Extended，不含ZR2轮眉	待终核: 1999普通4WD尺寸缺少第二可靠规格源
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2000 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Regular	6.0	190.1	67.9	63.4	2000 Chevrolet S-10 Regular Cab 4WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2000	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2000 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in货斗；2000配置列表未发现4WD长货斗，因此仅保留2WD	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup		皮卡	Extended	6.0	204.7	67.9	62.7	2000 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in货斗；W-IN按without mirrors	待终核: 2000官方技术PDF未成功读取，当前由Edmunds配置页补齐
Chevrolet	S10	gen2	2000	Pickup	4WD	皮卡	Extended	6.0	204.7	67.9	63.4	2000 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in货斗；普通4WD，不含ZR2宽体	待终核: 2000普通4WD三维缺少官方年度尺寸表确认
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2001 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab当年仅2WD；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通版尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2001 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	88.8-in长货斗；Regular Cab当年仅2WD	待终核: 2001普通长货斗尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2001 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2001普通Extended尺寸缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2001 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2宽轮眉	待终核: 2001普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2001	Pickup	4WD	皮卡	Crew	4.5	204.8	67.9	63.4	2001 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2001 Crew官方宽度口径需与第二来源交叉确认
Chevrolet	S10	gen2	2002	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2002 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2002普通版三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup		皮卡	Extended	6.0	206.1	67.9	62.7	2002 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；当前官方表长度与style-specific聚合205.3存在差异；ZQ8不单独拆分	待终核: 2002普通Extended L-IN存在206.1/205.3来源冲突
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2002 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2002普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2002	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2002 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；Crew仅4WD	待终核: 2002 Crew 67.8-in官方宽度需确认without mirrors表述
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	6.0	190.1	67.9	62.0	2003 Chevrolet S-10 Regular Cab 2WD 6.0-ft Bed	72.8-in短货斗；Regular Cab仅2WD；ZQ8外廓相同，不单独拆分	待终核: 2003官方190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2003	Pickup		皮卡	Regular	7.5	206.1	67.9	62.9	2003 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	长货斗在2003年重新列入官方尺寸表	待终核: 官方货斗表未列长货斗floor length，BED名义值需终核
Chevrolet	S10	gen2	2003	Pickup		皮卡	Extended	6.0	204.8	67.9	62.7	2003 Chevrolet S-10 Extended Cab 2WD 6.0-ft Bed	72.8-in短货斗；ZQ8公开外廓相同，不单独拆分	待终核: 2003官方204.8与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Extended	6.0	204.8	67.9	63.4	2003 Chevrolet S-10 Extended Cab 4WD 6.0-ft Bed	72.8-in短货斗；基础4WD，不含ZR2外扩轮眉	待终核: 2003普通4WD三维缺少第二可靠来源
Chevrolet	S10	gen2	2003	Pickup	4WD	皮卡	Crew	4.5	204.8	67.8	63.4	2003 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	55.2-in实际货斗按名义4.5填写；采用GM官方年度尺寸	待终核: Edmunds列205.3/67.9，与GM官方204.8/67.8存在来源冲突
Chevrolet	S10	gen2	2004	Pickup	4WD	皮卡	Crew	4.5	205.3	67.9	63.4	2004 Chevrolet S-10 Crew Cab 4WD 4.5-ft Bed	美国市场2004仅保留Crew Cab；55.2-in货斗按名义4.5填写	待终核: 2004三维目前依赖单一主要聚合来源
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.0	1999-2000 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD街道运动版；270-degree ground effects；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	1999-2000	Pickup	Xtreme	皮卡	Extended	6.0	204.7	67.9	62.7	1999-2000 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD街道运动版；Extended短货斗；W-IN按without mirrors	待终核: 1999-2000 Xtreme逐年官方order guide参考覆盖未补齐
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Regular	6.0	190.1	67.9	62.1	2001 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；style数据高度62.1 in，普通年度表为62.0 in	待终核: 2001 Xtreme H-IN存在62.0/62.1来源差异
Chevrolet	S10	gen2	2001	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2001 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；W-IN按without mirrors；ground-effects车身	待终核: 2001 Xtreme Extended L-IN与GM基础车身204.8存在0.5-in差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Regular	6.0	190.0	67.9	62.0	2002-2003 Chevrolet S-10 LS Xtreme Regular Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: 官方年度表190.1与style-specific 190.0存在舍入差异
Chevrolet	S10	gen2	2002-2003	Pickup	Xtreme	皮卡	Extended	6.0	205.3	67.9	62.7	2002-2003 Chevrolet S-10 LS Xtreme Extended Cab 6.0-ft Bed	2WD Xtreme；两年style-specific三维一致；W-IN按without mirrors	待终核: GM基础车身204.8/206.1与style-specific 205.3存在来源差异
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7			1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；长度按同轴距基础车身，宽体轮眉宽度及加高后高度不得套用普通4WD	待终核: 1994 ZR2缺少without mirrors最大宽度和官方整车高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7			1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；长度按基础短轴车身	待终核: 1995 Regular ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3			1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗	待终核: 1995 Extended ZR2缺少without mirrors最大宽度和高度
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6			1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；基础长度两年一致	待终核: 1996-1997 Regular ZR2宽度、高度及逐年官方尺寸表缺失
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3			1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box	待终核: 1996-1997 Extended ZR2宽度和高度缺失
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6			1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	1999为Regular ZR2最后一年，因此1998保留Regular组合；facelift后前脸	待终核: 1998 Regular ZR2缺少style-specific宽度和高度
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8		63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	style-specific聚合资料确认Extended ZR2；67.9-in宽度与宽轮距轮眉外廓存在口径疑点，暂不写入	待终核: 1998 Extended ZR2缺少可靠without mirrors最大宽体宽度
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0				2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	官方资料确认ZR2仅用于LS Extended Cab；同一规格页面三维相互冲突，暂不拼接	待终核: 2001 ZR2 L-IN、without mirrors W-IN和H-IN存在来源内冲突
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3		66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	两年均仅Extended ZR2；72.8-in短货斗；高度明显高于普通4WD	待终核: 2002-2003 ZR2宽度来源列67.9 in，与1999-2000 Wide Stance 71.9 in冲突，缺少可靠最大宽体without mirrors口径
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5) 下一步优先处理

- **下一步优先补缺失：**继续补齐 Chevy Van 1971–1982 的 110/125-in 车身三维，按 G10/G20/G30 高度差异拆分。
- 补齐 Chevy Van 1983–1989 Short/Regular，以及 1990–1992 Short/Regular/Extended 的长宽高。
- 补齐 El Camino 1959–1977、1979–1986 的 BED、长宽高和参考车型。
- 解决 S10 ZR2 1994–1998、2001–2003 的 W-IN/H-IN 空值。
- 所有关键空值清除后，再进入第二阶段逐年核对参考车型、without-mirrors 口径及迭代状态。

推进信号：CONTINUE

