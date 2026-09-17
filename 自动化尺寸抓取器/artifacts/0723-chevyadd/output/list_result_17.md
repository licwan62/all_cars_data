# 文件名：list.tsv


--- 恢复现场 / 已有回复 ---
## 1) 更新点

* 将 El Camino 原有 5 条存在空值的聚合记录，替换为按实际外廓变化拆分的 15 条完整记录；1959–1977、1979–1986 的 BED、L-IN、W-IN、H-IN 和参考车型均已补齐。GM Heritage Archive 当前收录了 1959–1960、1964–1987 各年度 El Camino Vehicle Information Kit。([gm.com][1])
* 第一代拆为 1959、1960：

  * 1959：`210.9 × 79.9 × 58.8 in`
  * 1960：`210.8 × 80.8 × 58.4 in`

  两年货斗内部长度均为 76.25 in，BED 按名义 `6.5` 归类。1959 官方车型页明确给出 210⅞-in 车长、58¾-in 高度和 76¼-in 货斗；因该页没有单列整车总宽，W-IN 采用同平台当年 full-size Chevrolet 的 79.9-in 外宽，并保留口径说明。([news.chevrolet.com][2])
* 第二代拆为 1964、1965、1966、1967，分别补入：

  * 1964：`198.8 × 73.2 × 54.1 in`
  * 1965：`201.5 × 74.5 × 53.3 in`
  * 1966：`197.5 × 75.0 × 54.5 in`
  * 1967：`197.5 × 75.0 × 56.5 in`

  货斗地板长度为 78.5 in，均归入 `6.5` BED。
* 第三代按车身尺寸节点拆为 1968–1969、1970、1971–1972。1970 因车长、宽度和高度均与前后年份不同，单独保留为 `206.5 × 75.4 × 54.4 in`。([carfolio.com][3])
* 第四代拆为 1973、1974–1975、1976、1977：

  * 1973：`213.2 × 76.6 × 53.8 in`
  * 1974–1975：`215.2 × 76.6 × 53.9 in`
  * 1976：`213.3 × 76.9 × 54.2 in`
  * 1977：`213.3 × 77.3 × 54.2 in`

  官方资料列出的货斗地板有效长度约 80.8 in，继续按名义 `6.5` 处理；1975 的官方资料检索结果也显示 215.2-in 长度、76.6-in 宽度和 53.9-in 高度。([hdpaintcode.com][4])
* 第五代 `1979-1986` 已补为 `201.6 × 71.9 × 53.8 in`。1979、1983、1985、1986 官方年度资料均显示相同外廓及 79.5/78.5-in 货斗长度，因此本轮合并为连续尺寸段；1985 官方尺寸页可直接确认该组数值。([gm.com][5])

## 2) 当前批次进度

* El Camino 1959–1987：当前记录均已具备 CAB、BED、三维和参考车型，不再存在阻塞成表的字段空值。
* Chevy Van 1964–1996：现有拆分行均已有三维和参考车型。
* 当前主要尺寸缺失集中在 S10 ZR2：

  * 1994–1998 仍缺部分 W-IN、H-IN。
  * 2001 仍缺完整三维。
  * 2002–2003 仍缺可靠的最大宽体 W-IN。
* Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture 仍有部分逐年参考车型覆盖缺失。
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
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in短轴；1972官方表为177×79.5×79.0 in；1971先按同代首期同结构补入	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in标准长轴；1972官方表为201×79.5×79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in短轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in标准长轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G30 Regular	两厢车			201.0	79.5	80.3	1971-1972 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1972官方高度80.25 in按一位小数记为80.3	待终核: 1971缺少独立G-Van尺寸页；1972宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 110-in Wheelbase	官方OH 78.75 in，按一位小数记为78.8	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.75 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Short	两厢车			177.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Regular	两厢车			201.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Short	两厢车			177.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Regular	两厢车			201.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1974 Chevrolet G30 Chevy Van 125-in Wheelbase	年度尺寸表仅列125-in完整G30车身	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1975 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in G30完整车身	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Short	两厢车			177.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Regular	两厢车			201.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Short	两厢车			177.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Regular	两厢车			201.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1977 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in完整G30车身	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 110-in Wheelbase	前后保险杠变化后Short总长增至178.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 125-in Wheelbase	Regular总长增至202.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1978 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Short	两厢车			178.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Regular	两厢车			202.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Short	两厢车			178.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Regular	两厢车			202.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Short	两厢车			178.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Regular	两厢车			202.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1980 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1981-1982 Chevrolet G10 Chevy Van 110-in Wheelbase	1981官方尺寸；1982按相邻年度同结构连续值补入	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1981-1982 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；1981官方OH 79.2 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1981-1982 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；1981官方OH 79.8 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1981-1982 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；1981官方OH 79.5 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版表未单列该组合，Cargo配置覆盖需第二阶段核对
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1983-1988 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	125-in G20；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1983-1988 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	125-in G30重载完整厢式车	待终核: 发动机和GVWR造成的细微高度差待第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1989 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	1989年度Short G10外廓	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1989 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	1989 G10 Regular高度降至79.1 in	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1989 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	1989年度尺寸表未列G20 Short，因此仅保留Regular	待终核: 1989 Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1989 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	汽油版高度81.8 in、HD/柴油版81.9 in；本行取最大值81.9	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Short	两厢车			178.2	79.5	80.0	1990 Chevrolet G10 Chevy Van 110-in Wheelbase	1990年度Short G10高度80.0 in	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Regular	两厢车			202.2	79.5	79.7	1990 Chevrolet G10 Chevy Van 125-in Wheelbase	1990年度Regular G10外廓	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Short	两厢车			178.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 110-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Regular	两厢车			202.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 125-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Regular	两厢车			202.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30重载车身	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；1990起正式列入整车尺寸表	待终核: 1990 Extended缺少第二可靠规格源
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1991-1992 Chevrolet G10 Chevy Van 125-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1991-1992 Chevrolet G20 Chevy Van 125-in Wheelbase	年度表未列G20 Short，因此仅保留Regular	待终核: Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1991-1992 Chevrolet G30 Chevy Van 125-in Wheelbase	汽油版高度81.8 in、HD版本81.9 in；本行取最大值	待终核: 不同GVWR高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1991-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；两年外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
Chevrolet	El Camino	gen1	1959	Pickup		皮卡	Regular	6.5	210.9	79.9	58.8	1959 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类；L-IN和H-IN来自官方车型图	待终核: 官方El Camino车型页未单列整车总宽，W-IN采用同年同平台full-size Chevrolet 79.9-in外宽
Chevrolet	El Camino	gen1	1960	Pickup		皮卡	Regular	6.5	210.8	80.8	58.4	1960 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类	待终核: 1960尺寸缺少第二可靠规格源
Chevrolet	El Camino	gen2	1964	Pickup		皮卡	Regular	6.5	198.8	73.2	54.1	1964 Chevrolet El Camino	115-in wheelbase；官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1964官方高度为loaded口径，需与其他年份design/unloaded高度统一
Chevrolet	El Camino	gen2	1965	Pickup		皮卡	Regular	6.5	201.5	74.5	53.3	1965 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1965三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1966	Pickup		皮卡	Regular	6.5	197.5	75.0	54.5	1966 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；前后外形变化使车长较1965缩短	待终核: 1966三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1967	Pickup		皮卡	Regular	6.5	197.5	75.0	56.5	1967 Chevrolet El Camino	与1966车长、宽度相同，但官方高度增加至56.5 in	待终核: 1967高度变化需第二可靠来源确认
Chevrolet	El Camino	gen3	1968-1969	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1968-1969 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: 1968-1969 W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen3	1970	Pickup		皮卡	Regular	6.5	206.5	75.4	54.4	1970 Chevrolet El Camino	1970年度官方外廓与1968-1969及1971-1972不同，单独拆分	待终核: 1970货斗实际长度需在年度货斗尺寸页再次确认
Chevrolet	El Camino	gen3	1971-1972	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1971-1972 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen4	1973	Pickup		皮卡	Regular	6.5	213.2	76.6	53.8	1973 Chevrolet El Camino	第四代首年；官方货斗有效地板长度约80.8 in，BED按名义6.5填写	待终核: 1973货斗上沿与地板长度代码需再次统一
Chevrolet	El Camino	gen4	1974-1975	Pickup		皮卡	Regular	6.5	215.2	76.6	53.9	1974-1975 Chevrolet El Camino	保险杠变化使总长增至215.2 in；两年官方外廓一致；货斗有效地板长度约80.8 in	待终核: 1975需补直接年度尺寸页截图交叉确认
Chevrolet	El Camino	gen4	1976	Pickup		皮卡	Regular	6.5	213.3	76.9	54.2	1976 Chevrolet El Camino	标准车长213.3 in；带可选impact strips时可达214.3 in，本行采用标准装备尺寸	待终核: W-IN采用官方maximum body/overall car width 76.9 in，需统一W103/W116代码口径
Chevrolet	El Camino	gen4	1977	Pickup		皮卡	Regular	6.5	213.3	77.3	54.2	1977 Chevrolet El Camino	标准车长213.3 in；官方maximum overall width of car增至77.3 in	待终核: 1977最大车宽与body width 76.9 in的字段口径需终核
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1979-1986 Chevrolet El Camino	1979/1983/1985/1986官方年度图示均为201.6×71.9×53.8 in；货斗上沿79.5 in、地板78.5 in	待终核: 1980-1982及1984需补各自年度直接尺寸页，当前按同代连续官方外廓合并
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
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

1. **下一步优先补缺失：**解决 S10 ZR2 1994–1998 的 W-IN、H-IN，优先读取年度 MVMA、order guide 和具体 style 规格页。
2. 补齐 2001 S10 ZR2 的 L-IN、W-IN、H-IN，避免继续保留整组三维空值。
3. 补齐 2002–2003 S10 ZR2 的可靠最大宽体 W-IN，并判断 67.9 与 71.9 in 分别代表基础车身还是外扩轮眉最大宽度。
4. 补充 Astro、Avalanche、HHR、Lumina APV、Metro、Silverado 1500HD、Uplander、Venture 尚未覆盖的逐年参考车型。
5. 上述缺失全部清除后，再进入第二阶段，集中核对邻年延续值、宽度口径、来源冲突和迭代状态。

推进信号：CONTINUE

[1]: https://www.gm.com/heritage/archive/vehicle-information-kits "https://www.gm.com/heritage/archive/vehicle-information-kits"
[2]: https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1959-Chevrolet-El-Camino.pdf "https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1959-Chevrolet-El-Camino.pdf"
[3]: https://www.carfolio.com/chevrolet-el-camino-318868?utm_source=chatgpt.com "1970 Chevrolet El Camino"
[4]: https://hdpaintcode.com/files/1975-chevrolet-corvette-paint-codes-and-body_ocred.pdf?utm_source=chatgpt.com "||
ee"
[5]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-El-Camino.pdf "https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-El-Camino.pdf"


--- Round 1 / 存档续跑 ---
## 1) 更新点

* 已清除 S10 ZR2 区域剩余的全部 L-IN、W-IN、H-IN 空值。
* 1994–1997 ZR2 没有在 GM 年度外廓表中单独列出轮眉最大包络尺寸。本轮先采用对应年度、驾驶室和轴距的官方 4WD 车身尺寸补齐：

  * 1994 Regular：`188.7 × 67.9 × 64.5 in`
  * 1995 Regular：`188.7 × 67.9 × 63.8 in`
  * 1995 Extended：`203.3 × 67.9 × 63.8 in`
  * 1996–1997 Regular：`188.6 × 67.9 × 63.8 in`
  * 1996–1997 Extended：`203.3 × 67.9 × 63.8 in`

  这些数值能够补齐成表字段，但 ZR2 轮眉、宽轮距和悬架升高后的最大实体包络仍保留待终核，不将“宽 4 in 的轮距”直接等同为车身宽度增加 4 in。([gm.com][1])
* 1998 Regular ZR2 补入 `71.9 × 64.3 in`；具体配置资料将其列为 ZR2 4WD，并提供 71.9-in 宽度和 64.3-in 高度。其 190.1-in 配置页车长与 GM 年度外廓表的 188.6 in 存在冲突，本轮仍保留官方年度表的 188.6 in，不在补缺失阶段强行改口径。([cargurus.com][2])
* 1998 Extended ZR2 补入 W-IN `67.9 in`，形成 `204.8 × 67.9 × 63.4 in`；该数据来自具体 Extended Cab ZR2 配置，而不是由 Regular Cab 推算。
* 2001 Extended ZR2 补入 `205.0 × 68.0 × 63.0 in`。Cars.com 的具体 `Ext Cab 123" WB 4WD LS w/ZR2` 测量表列出 205-in 不含后保险杠车长、68-in 最大无后视镜宽度和 63-in 高度；页面顶部摘要误显示 190.1 × 62.1 in，因此已在迭代状态中保留页面内部冲突。([Cars.com][3])
* 2002–2003 Extended ZR2 补入 W-IN `67.9 in`，完整尺寸为 `205.3 × 67.9 × 66.4 in`。具体 LS ZR2 配置页明确标注该宽度为 without mirrors，并同时确认 72.8-in 货斗。([Edmunds][4])
* 当前全量 TSV 已不存在 L-IN、W-IN、H-IN 或参考车型整格为空的阻塞行；但部分年份段的参考车型仍只覆盖首年或代表年，因此仍按第一阶段“补缺失覆盖”继续，不宣布完成。

## 2) 当前批次进度

* Chevy Van、El Camino、S10 普通版、S10 Xtreme 和 S10 ZR2 的结构、CAB/BED、三维与参考车型字段均已形成完整记录。
* S10 ZR2 的数值空白已经清除；其剩余事项主要是第二阶段的轮眉最大外廓、年度表与配置表冲突及取值口径核对。
* 当前第一阶段剩余缺失主要是**逐年参考车型覆盖**：

  * Astro 1990–2005；
  * Avalanche 2003–2013；
  * HHR 部分年份与 Panel/SS；
  * Lumina APV 1991–1992、1995–1996；
  * Metro 1999–2000；
  * Silverado 1500HD 2002–2003；
  * Uplander、Venture 的部分年份。
* 因上述年份覆盖尚未补齐，当前批次仍未完成，下一步优先补缺失。

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
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in短轴；1972官方表为177×79.5×79.0 in；1971先按同代首期同结构补入	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in标准长轴；1972官方表为201×79.5×79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in短轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in标准长轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G30 Regular	两厢车			201.0	79.5	80.3	1971-1972 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1972官方高度80.25 in按一位小数记为80.3	待终核: 1971缺少独立G-Van尺寸页；1972宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 110-in Wheelbase	官方OH 78.75 in，按一位小数记为78.8	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.75 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Short	两厢车			177.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Regular	两厢车			201.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Short	两厢车			177.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Regular	两厢车			201.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1974 Chevrolet G30 Chevy Van 125-in Wheelbase	年度尺寸表仅列125-in完整G30车身	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1975 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in G30完整车身	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Short	两厢车			177.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Regular	两厢车			201.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Short	两厢车			177.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Regular	两厢车			201.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1977 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in完整G30车身	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 110-in Wheelbase	前后保险杠变化后Short总长增至178.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 125-in Wheelbase	Regular总长增至202.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1978 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Short	两厢车			178.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Regular	两厢车			202.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Short	两厢车			178.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Regular	两厢车			202.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Short	两厢车			178.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Regular	两厢车			202.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1980 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1981-1982 Chevrolet G10 Chevy Van 110-in Wheelbase	1981官方尺寸；1982按相邻年度同结构连续值补入	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1981-1982 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；1981官方OH 79.2 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1981-1982 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；1981官方OH 79.8 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1981-1982 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；1981官方OH 79.5 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版表未单列该组合，Cargo配置覆盖需第二阶段核对
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1983-1988 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	125-in G20；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1983-1988 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	125-in G30重载完整厢式车	待终核: 发动机和GVWR造成的细微高度差待第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1989 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	1989年度Short G10外廓	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1989 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	1989 G10 Regular高度降至79.1 in	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1989 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	1989年度尺寸表未列G20 Short，因此仅保留立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版Regular	待终核: 1989 Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1989 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	汽油版高度81.8 in、HD/柴油版81.9 in；本行取最大值81.9	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Short	两厢车			178.2	79.5	80.0	1990 Chevrolet G10 Chevy Van 110-in Wheelbase	1990年度Short G10高度80.0 in	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Regular	两厢车			202.2	79.5	79.7	1990 Chevrolet G10 Chevy Van 125-in Wheelbase	1990年度Regular G10外廓	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Short	两厢车			178.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 110-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Regular	两厢车			202.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 125-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Regular	两厢车			202.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30重载车身	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；1990起正式列入整车尺寸表	待终核: 1990 Extended缺少第二可靠规格源
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1991-1992 Chevrolet G10 Chevy Van 125-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1991-1992 Chevrolet G20 Chevy Van 125-in Wheelbase	年度表未列G20 Short，因此仅保留Regular	待终核: Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1991-1992 Chevrolet G30 Chevy Van 125-in Wheelbase	汽油版高度81.8 in、HD版本81.9 in；本行取最大值	待终核: 不同GVWR高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1991-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；两年外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
Chevrolet	El Camino	gen1	1959	Pickup		皮卡	Regular	6.5	210.9	79.9	58.8	1959 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类；L-IN和H-IN来自官方车型图	待终核: 官方El Camino车型页未单列整车总宽，W-IN采用同年同平台full-size Chevrolet 79.9-in外宽
Chevrolet	El Camino	gen1	1960	Pickup		皮卡	Regular	6.5	210.8	80.8	58.4	1960 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类	待终核: 1960尺寸缺少第二可靠规格源
Chevrolet	El Camino	gen2	1964	Pickup		皮卡	Regular	6.5	198.8	73.2	54.1	1964 Chevrolet El Camino	115-in wheelbase；官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1964官方高度为loaded口径，需与其他年份design/unloaded高度统一
Chevrolet	El Camino	gen2	1965	Pickup		皮卡	Regular	6.5	201.5	74.5	53.3	1965 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1965三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1966	Pickup		皮卡	Regular	6.5	197.5	75.0	54.5	1966 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；前后外形变化使车长较1965缩短	待终核: 1966三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1967	Pickup		皮卡	Regular	6.5	197.5	75.0	56.5	1967 Chevrolet El Camino	与1966车长、宽度相同，但官方高度增加至56.5 in	待终核: 1967高度变化需第二可靠来源确认
Chevrolet	El Camino	gen3	1968-1969	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1968-1969 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: 1968-1969 W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen3	1970	Pickup		皮卡	Regular	6.5	206.5	75.4	54.4	1970 Chevrolet El Camino	1970年度官方外廓与1968-1969及1971-1972不同，单独拆分	待终核: 1970货斗实际长度需在年度货斗尺寸页再次确认
Chevrolet	El Camino	gen3	1971-1972	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1971-1972 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen4	1973	Pickup		皮卡	Regular	6.5	213.2	76.6	53.8	1973 Chevrolet El Camino	第四代首年；官方货斗有效地板长度约80.8 in，BED按名义6.5填写	待终核: 1973货斗上沿与地板长度代码需再次统一
Chevrolet	El Camino	gen4	1974-1975	Pickup		皮卡	Regular	6.5	215.2	76.6	53.9	1974-1975 Chevrolet El Camino	保险杠变化使总长增至215.2 in；两年官方外廓一致；货斗有效地板长度约80.8 in	待终核: 1975需补直接年度尺寸页截图交叉确认
Chevrolet	El Camino	gen4	1976	Pickup		皮卡	Regular	6.5	213.3	76.9	54.2	1976 Chevrolet El Camino	标准车长213.3 in；带可选impact strips时可达214.3 in，本行采用标准装备尺寸	待终核: W-IN采用官方maximum body/overall car width 76.9 in，需统一W103/W116代码口径
Chevrolet	El Camino	gen4	1977	Pickup		皮卡	Regular	6.5	213.3	77.3	54.2	1977 Chevrolet El Camino	标准车长213.3 in；官方maximum overall width of car增至77.3 in	待终核: 1977最大车宽与body width 76.9 in的字段口径需终核
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1979-1986 Chevrolet El Camino	1979/1983/1985/1986官方年度图示均为201.6×71.9×53.8 in；货斗上沿79.5 in、地板78.5 in	待终核: 1980-1982及1984需补各自年度直接尺寸页，当前按同代连续官方外廓合并
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
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
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	64.5	1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；官方年度表未单列ZR2轮眉最大包络，本行采用同年度4WD Regular官方车身三维	待终核: 1994 ZR2专属轮眉最大外廓和升高悬架后的配置高度未独立发布
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；采用同年度4WD Regular官方车身三维补齐	待终核: 1995 Regular ZR2轮眉最大外廓与车身宽度是否相同
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗；采用对应4WD Extended官方车身三维	待终核: 1995 Extended ZR2轮眉最大外廓和配置专属高度未单列
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；采用两年对应4WD Regular官方车身三维	待终核: ZR2宽轮距不直接等同于车身增宽；轮眉最大包络仍需专属来源
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box；三维采用对应4WD Extended年度表	待终核: 1996-1997 Extended ZR2配置专属轮眉宽度和高度未单列
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6	71.9	64.3	1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	具体ZR2配置资料列71.9-in宽度、64.3-in高度；L-IN继续采用GM年度表188.6 in	待终核: ZR2配置页另列190.1-in车长，与GM年度尺寸表188.6 in冲突
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8	67.9	63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	具体Extended ZR2配置为204.8×67.9×63.4 in；W-IN按without mirrors	待终核: 同年度Regular ZR2资料列71.9-in宽度，Regular与Extended宽度口径存在冲突
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0	205.0	68.0	63.0	2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	Cars.com具体Ext Cab 123-in WB 4WD LS w/ZR2测量表列205-in车长、68-in最大无镜宽度和63-in高度	待终核: 同页面顶部摘要误列190.1×62.1 in；测量表为整数精度，需补GM年度配置表
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3	67.9	66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	具体LS ZR2配置页明确列205.3×67.9×66.4 in；W-IN标注without mirrors；72.8-in短货斗	待终核: 67.9-in配置宽度与1999-2000 Wide Stance 71.9-in宽度口径需第二阶段统一
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴	待终核: 1998-2003 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	2003 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴	待终核: 1997-2002/2004 LWB逐年三维与参考车型未补齐；货运版年份来源冲突
```

## 5) 下一步优先处理

1. **下一步优先补缺失：**补齐 Astro 1990–2005 的逐年参考车型，并按 Short、EXT/LWB 及 Passenger/Cargo 的真实年份边界完善覆盖。
2. 补齐 Avalanche 2003–2013 的逐年参考车型，确认 1500、2500 和第二代各年份均有对应参考。
3. 补齐 HHR、Lumina APV、Metro 的缺失年份参考车型。
4. 补齐 Silverado 1500HD 2002–2003、Uplander、Venture 的逐年参考车型覆盖。
5. 逐年参考车型全部补齐后，再进入第二阶段，集中核对 S10 ZR2 宽体包络、without-mirrors 口径、邻年延续值和迭代状态。

推进信号：CONTINUE

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-S-10.pdf "pages"
[2]: https://www.cargurus.com/Cars/1998-Chevrolet-S-10-Trims-c3905 "https://www.cargurus.com/Cars/1998-Chevrolet-S-10-Trims-c3905"
[3]: https://www.cars.com/research/chevrolet-s_10-2001/specs/5690/ "https://www.cars.com/research/chevrolet-s_10-2001/specs/5690/"
[4]: https://www.edmunds.com/chevrolet/s-10/2002/extended-cab/st-100002838/features-specs/ "https://www.edmunds.com/chevrolet/s-10/2002/extended-cab/st-100002838/features-specs/"


--- Round 2 / 下一步 ---
## 1) 更新点

* 补齐 **Chevrolet Astro 1985–2005** 的逐年参考车型覆盖。GM Heritage Archive 对 1985 至 2005 每个 Astro 车型年均提供独立年度资料入口，因此原先仅写首年车型的 1990–1994 Short、1990–1994 EXT/LWB 和 1995–2005 LWB 记录，现已改为列出范围内全部年份。([通用汽车][1])
* 补齐 **Chevrolet Lumina APV 1990–1996** 的逐年参考车型覆盖。1990、1991、1992、1993、1994、1995、1996 均可在 GM 档案目录中找到对应年度车型资料。([通用汽车][1])
* 补齐 **Chevrolet Venture 1997–2005** 的逐年参考车型覆盖。SWB 行覆盖 1997–2004，LWB 行覆盖 1997–2005，并保持原有年份边界不变。([通用汽车][1])
* 本轮只更新参考车型字段及对应迭代状态，没有调整上述车型的三维数据，也没有新增原年份范围以外的记录。
* Astro、Lumina APV、Venture 不再因“参考车型仅覆盖首年”阻塞成表；Passenger/Cargo、Short/LWB 的尺寸差异与货运版年份问题仍留待第二阶段核对。

## 2) 当前批次进度

* 结构、CAB、BED、L-IN、W-IN、H-IN 和参考车型存在整格空白的记录已经清除。
* 已完成逐年参考车型覆盖：

  * Astro 1985–2005；
  * Blazer EV 2024–2026；
  * Chevy Van 1964–1996；
  * El Camino 1959–1987；
  * Lumina APV 1990–1996；
  * S10 普通版、EV、Xtreme、ZR2；
  * Venture 1997–2005。
* 第一阶段仍有参考车型覆盖缺失：

  * Avalanche 2003–2013；
  * HHR 普通版、Panel 和 SS 的部分年份；
  * Metro 1999–2000；
  * Silverado 1500HD 2002–2003；
  * Uplander 2006–2008。
* 因仍存在逐年参考车型覆盖缺失，当前批次尚未完成，仍执行“下一步优先补缺失”。

## 3) 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985 Chevrolet Astro Van; 1986 Chevrolet Astro Van; 1987 Chevrolet Astro Van; 1988 Chevrolet Astro Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1985-1988逐年参考车型已覆盖；1986缺少独立官方乘用版尺寸页；Passenger/Cargo是否需按高度差异拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989参考车型已覆盖；Cargo高度74.5 in，是否需要独立版本行尚未处理
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro Van; 1991 Chevrolet Astro Van; 1992 Chevrolet Astro Van; 1993 Chevrolet Astro Van; 1994 Chevrolet Astro Van	短轴车身；各年度车型资料入口均已覆盖；客运/货运外壳尺寸关系待逐年确认；W-IN按without mirrors	待终核: 1990-1994逐年参考车型已补齐；Short Passenger/Cargo高度和配置边界待核
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro Van EXT; 1991 Chevrolet Astro Van EXT; 1992 Chevrolet Astro Van EXT; 1993 Chevrolet Astro Van EXT; 1994 Chevrolet Astro Van EXT	加长车身；EXT/LWB覆盖1990-1994；W-IN按without mirrors	待终核: 1990-1994逐年参考车型已补齐；EXT Passenger/Cargo高度和配置边界待核
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro Van; 1996 Chevrolet Astro Van; 1997 Chevrolet Astro Van; 1998 Chevrolet Astro Van; 1999 Chevrolet Astro Van; 2000 Chevrolet Astro Van; 2001 Chevrolet Astro Van; 2002 Chevrolet Astro Van; 2003 Chevrolet Astro Van; 2004 Chevrolet Astro Van; 2005 Chevrolet Astro Van	1995起取消短轴车身；1995-2005全部车型年均已补入参考车型；W-IN按without mirrors	待终核: 逐年参考车型已补齐；Passenger/Cargo、RWD/AWD高度和外廓差异待核
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
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in短轴；1972官方表为177×79.5×79.0 in；1971先按同代首期同结构补入	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in标准长轴；1972官方表为201×79.5×79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in短轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in标准长轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G30 Regular	两厢车			201.0	79.5	80.3	1971-1972 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1972官方高度80.25 in按一位小数记为80.3	待终核: 1971缺少独立G-Van尺寸页；1972宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 110-in Wheelbase	官方OH 78.75 in，按一位小数记为78.8	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.75 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Short	两厢车			177.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Regular	两厢车			201.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Short	两厢车			177.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Regular	两厢车			201.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1974 Chevrolet G30 Chevy Van 125-in Wheelbase	年度尺寸表仅列125-in完整G30车身	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1975 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in G30完整车身	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Short	两厢车			177.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Regular	两厢车			201.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Short	两厢车			177.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Regular	两厢车			201.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1977 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in完整G30车身	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 110-in Wheelbase	前后保险杠变化后Short总长增至178.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 125-in Wheelbase	Regular总长增至202.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1978 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Short	两厢车			178.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Regular	两厢车			202.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Short	两厢车			178.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Regular	两厢车			202.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Short	两厢车			178.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Regular	两厢车			202.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1980 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1981-1982 Chevrolet G10 Chevy Van 110-in Wheelbase	1981官方尺寸；1982按相邻年度同结构连续值补入	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1981-1982 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；1981官方OH 79.2 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1981-1982 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；1981官方OH 79.8 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1981-1982 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；1981官方OH 79.5 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版表未单列该组合，Cargo配置覆盖需第二阶段核对
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1983-1988 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	125-in G20；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1983-1988 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	125-in G30重载完整厢式车	待终核: 发动机和GVWR造成的细微高度差待第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1989 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	1989年度Short G10外廓	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1989 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	1989 G10 Regular高度降至79.1 in	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1989 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	1989年度尺寸表未列G20 Short，因此仅保留Regular	待终核: 1989 Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1989 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	汽油版高度81.8 in、HD/柴油版81.9 in；本行取最大值81.9	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Short	两厢车			178.2	79.5	80.0	1990 Chevrolet G10 Chevy Van 110-in Wheelbase	1990年度Short G10高度80.0 in	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Regular	两厢车			202.2	79.5	79.7	1990 Chevrolet G10 Chevy Van 125-in Wheelbase	1990年度Regular G10外廓	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Short	两厢车			178.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 110-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Regular	两厢车			202.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 125-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Regular	两厢车			202.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30重载车身	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；1990起正式列入整车尺寸表	待终核: 1990 Extended缺少第二可靠规格源
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1991-1992 Chevrolet G10 Chevy Van 125-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1991-1992 Chevrolet G20 Chevy Van 125-in Wheelbase	年度表未列G20 Short，因此仅保留Regular	待终核: Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1991-1992 Chevrolet G30 Chevy Van 125-in Wheelbase	汽油版高度81.8 in、HD版本81.9 in；本行取最大值	待终核: 不同GVWR高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1991-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；两年外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
Chevrolet	El Camino	gen1	1959	Pickup		皮卡	Regular	6.5	210.9	79.9	58.8	1959 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类；L-IN和H-IN来自官方车型图	待终核: 官方El Camino车型页未单列整车总宽，W-IN采用同年同平台full-size Chevrolet 79.9-in外宽
Chevrolet	El Camino	gen1	1960	Pickup		皮卡	Regular	6.5	210.8	80.8	58.4	1960 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类	待终核: 1960尺寸缺少第二可靠规格源
Chevrolet	El Camino	gen2	1964	Pickup		皮卡	Regular	6.5	198.8	73.2	54.1	1964 Chevrolet El Camino	115-in wheelbase；官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1964官方高度为loaded口径，需与其他年份design/unloaded高度统一
Chevrolet	El Camino	gen2	1965	Pickup		皮卡	Regular	6.5	201.5	74.5	53.3	1965 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1965三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1966	Pickup		皮卡	Regular	6.5	197.5	75.0	54.5	1966 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；前后外形变化使车长较1965缩短	待终核: 1966三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1967	Pickup		皮卡	Regular	6.5	197.5	75.0	56.5	1967 Chevrolet El Camino	与1966车长、宽度相同，但官方高度增加至56.5 in	待终核: 1967高度变化需第二可靠来源确认
Chevrolet	El Camino	gen3	1968-1969	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1968-1969 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: 1968-1969 W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen3	1970	Pickup		皮卡	Regular	6.5	206.5	75.4	54.4	1970 Chevrolet El Camino	1970年度官方外廓与1968-1969及1971-1972不同，单独拆分	待终核: 1970货斗实际长度需在年度货斗尺寸页再次确认
Chevrolet	El Camino	gen3	1971-1972	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1971-1972 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen4	1973	Pickup		皮卡	Regular	6.5	213.2	76.6	53.8	1973 Chevrolet El Camino	第四代首年；官方货斗有效地板长度约80.8 in，BED按名义6.5填写	待终核: 1973货斗上沿与地板长度代码需再次统一
Chevrolet	El Camino	gen4	1974-1975	Pickup		皮卡	Regular	6.5	215.2	76.6	53.9	1974-1975 Chevrolet El Camino	保险杠变化使总长增至215.2 in；两年官方外廓一致；货斗有效地板长度约80.8 in	待终核: 1975需补直接年度尺寸页截图交叉确认
Chevrolet	El Camino	gen4	1976	Pickup		皮卡	Regular	6.5	213.3	76.9	54.2	1976 Chevrolet El Camino	标准车长213.3 in；带可选impact strips时可达214.3 in，本行采用标准装备尺寸	待终核: W-IN采用官方maximum body/overall car width 76.9 in，需统一W103/W116代码口径
Chevrolet	El Camino	gen4	1977	Pickup		皮卡	Regular	6.5	213.3	77.3	54.2	1977 Chevrolet El Camino	标准车长213.3 in；官方maximum overall width of car增至77.3 in	待终核: 1977最大车宽与body width 76.9 in的字段口径需终核
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1979-1986 Chevrolet El Camino	1979/1983/1985/1986官方年度图示均为201.6×71.9×53.8 in；货斗上沿79.5 in、地板78.5 in	待终核: 1980-1982及1984需补各自年度直接尺寸页，当前按同代连续官方外廓合并
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2009 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；W-IN按without mirrors	待终核: 2007-2008/2010-2011逐年参考车型未补齐
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身	待终核: 2008-2011 Panel逐年尺寸与参考车型未补齐
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；W-IN按without mirrors	待终核: 2010 SS三维与参考车型未补齐
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV; 1991 Chevrolet Lumina APV; 1992 Chevrolet Lumina APV	minivan轮廓；1990-1992全部年度参考车型已补齐；W-IN按车身宽度口径	待终核: 逐年参考车型已覆盖；1990-1992高度、配置和车身外廓需逐年终核
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993参考车型及三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina APV; 1995 Chevrolet Lumina APV; 1996 Chevrolet Lumina APV	1994起市场名称常简化为Lumina Minivan；1994-1996全部年度参考车型已补齐	待终核: 逐年参考车型已覆盖；1994-1996市场名称、尺寸及配置口径待终核
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
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	64.5	1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；官方年度表未单列ZR2轮眉最大包络，本行采用同年度4WD Regular官方车身三维	待终核: 1994 ZR2专属轮眉最大外廓和升高悬架后的配置高度未独立发布
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；采用同年度4WD Regular官方车身三维补齐	待终核: 1995 Regular ZR2轮眉最大外廓与车身宽度是否相同
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗；采用对应4WD Extended官方车身三维	待终核: 1995 Extended ZR2轮眉最大外廓和配置专属高度未单列
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；采用两年对应4WD Regular官方车身三维	待终核: ZR2宽轮距不直接等同于车身增宽；轮眉最大包络仍需专属来源
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box；三维采用对应4WD Extended年度表	待终核: 1996-1997 Extended ZR2配置专属轮眉宽度和高度未单列
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6	71.9	64.3	1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	具体ZR2配置资料列71.9-in宽度、64.3-in高度；L-IN继续采用GM年度表188.6 in	待终核: ZR2配置页另列190.1-in车长，与GM年度尺寸表188.6 in冲突
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8	67.9	63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	具体Extended ZR2配置为204.8×67.9×63.4 in；W-IN按without mirrors	待终核: 同年度Regular ZR2资料列71.9-in宽度，Regular与Extended宽度口径存在冲突
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0	205.0	68.0	63.0	2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	Cars.com具体Ext Cab 123-in WB 4WD LS w/ZR2测量表列205-in车长、68-in最大无镜宽度和63-in高度	待终核: 同页面顶部摘要误列190.1×62.1 in；测量表为整数精度，需补GM年度配置表
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3	67.9	66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	具体LS ZR2配置页明确列205.3×67.9×66.4 in；W-IN标注without mirrors；72.8-in短货斗	待终核: 67.9-in配置宽度与1999-2000 Wide Stance 71.9-in宽度口径需第二阶段统一
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；W-IN按without mirrors	待终核: 2002-2003逐年参考覆盖及2003高度76.1/76.2差异未确认
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB	美国市场止于2008；长轴minivan；W-IN按车身宽度	待终核: 2006-2008 LWB逐年三维与参考车型未补齐
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB	短轴版本主要面向fleet；标准短轴版本留空	待终核: 2007-2008 SWB逐年三维与参考车型未补齐
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 1998 Chevrolet Venture SWB; 1999 Chevrolet Venture SWB; 2000 Chevrolet Venture SWB; 2001 Chevrolet Venture SWB; 2002 Chevrolet Venture SWB; 2003 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴；1997-2004逐年参考车型已补齐	待终核: SWB逐年参考覆盖已补齐；各年度配置与三维是否完全一致待第二阶段核对
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	1997 Chevrolet Venture LWB; 1998 Chevrolet Venture LWB; 1999 Chevrolet Venture LWB; 2000 Chevrolet Venture LWB; 2001 Chevrolet Venture LWB; 2002 Chevrolet Venture LWB; 2003 Chevrolet Venture LWB; 2004 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴；1997-2005逐年参考车型已补齐	待终核: LWB逐年参考覆盖已补齐；货运版年份来源冲突和逐年尺寸口径待核
```

## 5) 下一步优先处理

1. **下一步优先补缺失：**补齐 Avalanche 2003–2006 的 1500/2500 逐年参考车型，以及 2007–2013 第二代逐年参考车型。
2. 补齐 HHR 2006–2011 普通版、2007–2011 Panel、2008–2010 SS 的缺失年份参考车型。
3. 补齐 Metro 1999–2000 Hatchback/Sedan 参考车型。
4. 补齐 Silverado 1500HD 2002–2003 与 Uplander 2006–2008 的逐年参考车型。
5. 第一阶段参考车型覆盖全部补齐后，再进入第二阶段，集中核对三维口径、Passenger/Cargo 边界、without-mirrors 宽度及迭代状态。

推进信号：CONTINUE

[1]: https://www.gm.com/heritage/archive/vehicle-information-kits "GM Heritage Archive: Vehicle Info Kits | General Motors"


--- Round 3 / 下一步 ---
## 1) 更新点

* 补齐 **Avalanche 2003–2013** 的逐年参考车型：

  * 2003–2006 的 1500、2500 分别覆盖四个车型年；
  * 2007–2013 第二代覆盖七个车型年，2013 年按实际市场名称补充为 Black Diamond Avalanche。现有资料可确认 2004 年同时存在 1500/2500，2006 年仍有 2500，2013 年存在 Black Diamond Avalanche 各配置。([Edmunds][1])
* 补齐 **HHR** 的逐年参考车型：

  * 普通版覆盖 2006–2011；
  * Panel 覆盖 2007–2011；
  * SS 覆盖 2008–2010；
  * Panel SS 保持仅 2009 年。资料分别确认 2007 Panel、2008/2010 SS、2011 普通版及 Panel。([Edmunds][2])
* 补齐 **Metro** 的逐年参考车型：Hatchback 覆盖 1998–2000，Sedan 覆盖 1998–2001；1999、2000 年两种结构以及 2001 Sedan 均有对应规格记录。([Edmunds][3])
* 补齐 **Silverado 1500HD 2001–2003** 的逐年 Crew Cab 6.6-ft Bed 参考车型。2002、2003 年规格页均确认 Crew Cab 车身，2002 年资料同时说明 1500HD 仅提供 Crew Cab、short box。([Edmunds][4])
* 补齐 **Uplander**：

  * LWB 覆盖 2005–2008；
  * SWB 覆盖 2006–2008。

  2006 年新增短轴版本，2008 年资料仍同时列出 113.0-in regular wheelbase 与 121.1-in extended wheelbase。([Edmunds][5])
* 本轮完成后，当前 TSV 已不再存在结构、版本、CAB、BED、三维或参考车型字段的阻塞性空值；第一阶段补缺失结束，后续转入第二阶段逐年核对。

## 2) 当前批次进度

* **第一阶段：已完成。**

  * 所有现有记录均已有结构、版本、分类、CAB/BED（适用车型）、L-IN、W-IN、H-IN 和参考车型。
  * 聚合年份范围内的逐年参考车型已覆盖。
* **第二阶段：尚未完成。**

  * 仍需核对 Passenger/Cargo、2WD/4WD、不同 GVWR 和动力配置是否造成需拆行的高度差异。
  * 仍需统一 `maximum width`、`body width`、`overall width without mirrors` 等宽度口径。
  * 仍需解决 S10 ZR2、Chevy Van、El Camino 等来源间的尺寸冲突和邻年延续值。
  * 仍需逐行更新最终迭代状态，因此当前批次不能标记完成。

## 3) 本轮更新后的全量 TSV

```tsv
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon		两厢车			176.8	77.0	73.7	1985 Chevrolet Astro Van; 1986 Chevrolet Astro Van; 1987 Chevrolet Astro Van; 1988 Chevrolet Astro Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段乘用版外廓补入；Cargo同期高度为74.5 in	待终核: 1985-1988逐年参考车型已覆盖；1986缺少独立官方乘用版尺寸页；Passenger/Cargo是否需按高度差异拆分
Chevrolet	Astro	gen1	1989	Wagon		两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Van	111.0-in短轴乘用版；1989官方规格表高度升至74.1 in；W-IN为官方overall width	待终核: 1989参考车型已覆盖；Cargo高度74.5 in，是否需要独立版本行尚未处理
Chevrolet	Astro	gen1	1990-1994	Wagon		两厢车			176.8	77.0	74.1	1990 Chevrolet Astro Van; 1991 Chevrolet Astro Van; 1992 Chevrolet Astro Van; 1993 Chevrolet Astro Van; 1994 Chevrolet Astro Van	短轴车身；各年度车型资料入口均已覆盖；客运/货运外壳尺寸关系待逐年确认；W-IN按without mirrors	待终核: 1990-1994逐年参考车型已补齐；Short Passenger/Cargo高度和配置边界待核
Chevrolet	Astro	gen1	1990-1994	Wagon	LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro Van EXT; 1991 Chevrolet Astro Van EXT; 1992 Chevrolet Astro Van EXT; 1993 Chevrolet Astro Van EXT; 1994 Chevrolet Astro Van EXT	加长车身；EXT/LWB覆盖1990-1994；W-IN按without mirrors	待终核: 1990-1994逐年参考车型已补齐；EXT Passenger/Cargo高度和配置边界待核
Chevrolet	Astro	gen2	1995-2005	Wagon	LWB	两厢车			189.8	75.9	76.2	1995 Chevrolet Astro Van; 1996 Chevrolet Astro Van; 1997 Chevrolet Astro Van; 1998 Chevrolet Astro Van; 1999 Chevrolet Astro Van; 2000 Chevrolet Astro Van; 2001 Chevrolet Astro Van; 2002 Chevrolet Astro Van; 2003 Chevrolet Astro Van; 2004 Chevrolet Astro Van; 2005 Chevrolet Astro Van	1995起取消短轴车身；1995-2005全部车型年均已补入参考车型；W-IN按without mirrors	待终核: 逐年参考车型已补齐；Passenger/Cargo、RWD/AWD高度和外廓差异待核
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab; 2004 Chevrolet Avalanche 1500 Crew Cab; 2005 Chevrolet Avalanche 1500 Crew Cab; 2006 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；2003-2006逐年1500参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；各年度2WD/4WD高度及三维一致性待核
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab; 2004 Chevrolet Avalanche 2500 Crew Cab; 2005 Chevrolet Avalanche 2500 Crew Cab; 2006 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；2003-2006逐年2500参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；各年度高度、GVWR和外廓一致性待核
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab; 2008 Chevrolet Avalanche Crew Cab; 2009 Chevrolet Avalanche Crew Cab; 2010 Chevrolet Avalanche Crew Cab; 2011 Chevrolet Avalanche Crew Cab; 2012 Chevrolet Avalanche Crew Cab; 2013 Chevrolet Black Diamond Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；2007-2013逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；2WD/4WD及配置高度差异和2013 Black Diamond命名口径待核
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964	Wagon	G10 Short	两厢车			167.6	72.7	77.3	1964 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 167.56 in、maximum body/rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 官方尺寸已补齐；需第二规格源确认四舍五入口径
Chevrolet	Chevy Van	gen1	1965	Wagon	G10 Short	两厢车			167.5	72.8	77.3	1965 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方图示maximum width 72.75 in、unloaded height 77.25 in	待终核: 1965尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen1	1966	Wagon	G10 Short	两厢车			168.3	72.7	77.3	1966 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 168.30 in、across-rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 1966尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in短轴；1972官方表为177×79.5×79.0 in；1971先按同代首期同结构补入	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in标准长轴；1972官方表为201×79.5×79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in短轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in标准长轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G30 Regular	两厢车			201.0	79.5	80.3	1971-1972 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1972官方高度80.25 in按一位小数记为80.3	待终核: 1971缺少独立G-Van尺寸页；1972宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 110-in Wheelbase	官方OH 78.75 in，按一位小数记为78.8	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.75 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Short	两厢车			177.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Regular	两厢车			201.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Short	两厢车			177.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Regular	两厢车			201.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1974 Chevrolet G30 Chevy Van 125-in Wheelbase	年度尺寸表仅列125-in完整G30车身	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1975 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in G30完整车身	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Short	两厢车			177.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Regular	两厢车			201.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Short	两厢车			177.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Regular	两厢车			201.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1977 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in完整G30车身	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 110-in Wheelbase	前后保险杠变化后Short总长增至178.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 125-in Wheelbase	Regular总长增至202.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1978 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Short	两厢车			178.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Regular	两厢车			202.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Short	两厢车			178.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Regular	两厢车			202.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Short	两厢车			178.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Regular	两厢车			202.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1980 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1981-1982 Chevrolet G10 Chevy Van 110-in Wheelbase	1981官方尺寸；1982按相邻年度同结构连续值补入	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1981-1982 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；1981官方OH 79.2 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1981-1982 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；1981官方OH 79.8 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1981-1982 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；1981官方OH 79.5 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版表未单列该组合，Cargo配置覆盖需第二阶段核对
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1983-1988 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	125-in G20；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1983-1988 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	125-in G30重载完整厢式车	待终核: 发动机和GVWR造成的细微高度差待第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1989 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	1989年度Short G10外廓	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1989 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	1989 G10 Regular高度降至79.1 in	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1989 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	1989年度尺寸表未列G20 Short，因此仅保留Regular	待终核: 1989 Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1989 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	汽油版高度81.8 in、HD/柴油版81.9 in；本行取最大值81.9	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Short	两厢车			178.2	79.5	80.0	1990 Chevrolet G10 Chevy Van 110-in Wheelbase	1990年度Short G10高度80.0 in	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Regular	两厢车			202.2	79.5	79.7	1990 Chevrolet G10 Chevy Van 125-in Wheelbase	1990年度Regular G10外廓	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Short	两厢车			178.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 110-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Regular	两厢车			202.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 125-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Regular	两厢车			202.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30重载车身	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；1990起正式列入整车尺寸表	待终核: 1990 Extended缺少第二可靠规格源
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1991-1992 Chevrolet G10 Chevy Van 125-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1991-1992 Chevrolet G20 Chevy Van 125-in Wheelbase	年度表未列G20 Short，因此仅保留Regular	待终核: Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1991-1992 Chevrolet G30 Chevy Van 125-in Wheelbase	汽油版高度81.8 in、HD版本81.9 in；本行取最大值	待终核: 不同GVWR高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1991-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；两年外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
Chevrolet	El Camino	gen1	1959	Pickup		皮卡	Regular	6.5	210.9	79.9	58.8	1959 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类；L-IN和H-IN来自官方车型图	待终核: 官方El Camino车型页未单列整车总宽，W-IN采用同年同平台full-size Chevrolet 79.9-in外宽
Chevrolet	El Camino	gen1	1960	Pickup		皮卡	Regular	6.5	210.8	80.8	58.4	1960 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类	待终核: 1960尺寸缺少第二可靠规格源
Chevrolet	El Camino	gen2	1964	Pickup		皮卡	Regular	6.5	198.8	73.2	54.1	1964 Chevrolet El Camino	115-in wheelbase；官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1964官方高度为loaded口径，需与其他年份design/unloaded高度统一
Chevrolet	El Camino	gen2	1965	Pickup		皮卡	Regular	6.5	201.5	74.5	53.3	1965 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1965三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1966	Pickup		皮卡	Regular	6.5	197.5	75.0	54.5	1966 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；前后外形变化使车长较1965缩短	待终核: 1966三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1967	Pickup		皮卡	Regular	6.5	197.5	75.0	56.5	1967 Chevrolet El Camino	与1966车长、宽度相同，但官方高度增加至56.5 in	待终核: 1967高度变化需第二可靠来源确认
Chevrolet	El Camino	gen3	1968-1969	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1968-1969 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: 1968-1969 W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen3	1970	Pickup		皮卡	Regular	6.5	206.5	75.4	54.4	1970 Chevrolet El Camino	1970年度官方外廓与1968-1969及1971-1972不同，单独拆分	待终核: 1970货斗实际长度需在年度货斗尺寸页再次确认
Chevrolet	El Camino	gen3	1971-1972	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1971-1972 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen4	1973	Pickup		皮卡	Regular	6.5	213.2	76.6	53.8	1973 Chevrolet El Camino	第四代首年；官方货斗有效地板长度约80.8 in，BED按名义6.5填写	待终核: 1973货斗上沿与地板长度代码需再次统一
Chevrolet	El Camino	gen4	1974-1975	Pickup		皮卡	Regular	6.5	215.2	76.6	53.9	1974-1975 Chevrolet El Camino	保险杠变化使总长增至215.2 in；两年官方外廓一致；货斗有效地板长度约80.8 in	待终核: 1975需补直接年度尺寸页截图交叉确认
Chevrolet	El Camino	gen4	1976	Pickup		皮卡	Regular	6.5	213.3	76.9	54.2	1976 Chevrolet El Camino	标准车长213.3 in；带可选impact strips时可达214.3 in，本行采用标准装备尺寸	待终核: W-IN采用官方maximum body/overall car width 76.9 in，需统一W103/W116代码口径
Chevrolet	El Camino	gen4	1977	Pickup		皮卡	Regular	6.5	213.3	77.3	54.2	1977 Chevrolet El Camino	标准车长213.3 in；官方maximum overall width of car增至77.3 in	待终核: 1977最大车宽与body width 76.9 in的字段口径需终核
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1979-1986 Chevrolet El Camino	1979/1983/1985/1986官方年度图示均为201.6×71.9×53.8 in；货斗上沿79.5 in、地板78.5 in	待终核: 1980-1982及1984需补各自年度直接尺寸页，当前按同代连续官方外廓合并
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2007 Chevrolet HHR; 2008 Chevrolet HHR; 2009 Chevrolet HHR; 2010 Chevrolet HHR; 2011 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；2006-2011逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；普通版逐年尺寸、悬架与配置差异待核
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel; 2008 Chevrolet HHR Panel; 2009 Chevrolet HHR Panel; 2010 Chevrolet HHR Panel; 2011 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身；2007-2011逐年参考车型已覆盖	待终核: 逐年参考车型已补齐；Panel与普通版外廓是否完全一致待核
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS; 2010 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；2008-2010逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；手动/自动及年度悬架高度差待核
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV; 1991 Chevrolet Lumina APV; 1992 Chevrolet Lumina APV	minivan轮廓；1990-1992全部年度参考车型已补齐；W-IN按车身宽度口径	待终核: 逐年参考车型已覆盖；1990-1992高度、配置和车身外廓需逐年终核
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993参考车型及三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina APV; 1995 Chevrolet Lumina APV; 1996 Chevrolet Lumina APV	1994起市场名称常简化为Lumina Minivan；1994-1996全部年度参考车型已补齐	待终核: 逐年参考车型已覆盖；1994-1996市场名称、尺寸及配置口径待终核
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback; 1999 Chevrolet Metro Hatchback; 2000 Chevrolet Metro Hatchback	Chevrolet品牌Metro Hatchback覆盖1998-2000；逐年参考车型已补齐；W-IN按without mirrors	待终核: 逐年参考车型已补齐；发动机及配置是否导致外廓差异待核
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 1999 Chevrolet Metro Sedan; 2000 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；1998-2001逐年参考车型已补齐；W-IN按without mirrors	待终核: 逐年参考车型已补齐；1998-2001三维及配置一致性待核
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
Chevrolet	S10	gen2	1994	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	64.5	1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	ZR2首年仅Regular；官方年度表未单列ZR2轮眉最大包络，本行采用同年度4WD Regular官方车身三维	待终核: 1994 ZR2专属轮眉最大外廓和升高悬架后的配置高度未独立发布
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Regular	6.0	188.7	67.9	63.8	1995 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular ZR2继续销售；采用同年度4WD Regular官方车身三维补齐	待终核: 1995 Regular ZR2轮眉最大外廓与车身宽度是否相同
Chevrolet	S10	gen2	1995	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1995 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1995起ZR2扩展到Extended Cab；72.8-in短货斗；采用对应4WD Extended官方车身三维	待终核: 1995 Extended ZR2轮眉最大外廓和配置专属高度未单列
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Regular	6.0	188.6	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	Regular宽轮距越野版；采用两年对应4WD Regular官方车身三维	待终核: ZR2宽轮距不直接等同于车身增宽；轮眉最大包络仍需专属来源
Chevrolet	S10	gen2	1996-1997	Pickup	ZR2	皮卡	Extended	6.0	203.3	67.9	63.8	1996-1997 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	1997官方宣传资料确认4x4 ZR2 LS Extended-Cab Short-Box；三维采用对应4WD Extended年度表	待终核: 1996-1997 Extended ZR2配置专属轮眉宽度和高度未单列
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Regular	6.0	188.6	71.9	64.3	1998 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed	具体ZR2配置资料列71.9-in宽度、64.3-in高度；L-IN继续采用GM年度表188.6 in	待终核: ZR2配置页另列190.1-in车长，与GM年度尺寸表188.6 in冲突
Chevrolet	S10	gen2	1998	Pickup	ZR2	皮卡	Extended	6.0	204.8	67.9	63.4	1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed	具体Extended ZR2配置为204.8×67.9×63.4 in；W-IN按without mirrors	待终核: 同年度Regular ZR2资料列71.9-in宽度，Regular与Extended宽度口径存在冲突
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Regular	6.0	190.1	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Regular Cab 6.0-ft Bed	ZR2/Wide Stance；Regular ZR2最后一年；W-IN按without mirrors	待终核: 1999 Regular ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	1999	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	64.3	1999 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	ZR2/Wide Stance；72.8-in短货斗；W-IN按without mirrors	待终核: 1999 Extended ZR2需补官方年度尺寸表交叉确认
Chevrolet	S10	gen2	2000	Pickup	ZR2	皮卡	Extended	6.0	204.7	71.9	63.4	2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed	2000起ZR2仅Extended；W-IN按without mirrors	待终核: 2000 ZR2高度较1999低0.9 in，需官方资料确认是否为口径差
Chevrolet	S10	gen2	2001	Pickup	ZR2	皮卡	Extended	6.0	205.0	68.0	63.0	2001 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	Cars.com具体Ext Cab 123-in WB 4WD LS w/ZR2测量表列205-in车长、68-in最大无镜宽度和63-in高度	待终核: 同页面顶部摘要误列190.1×62.1 in；测量表为整数精度，需补GM年度配置表
Chevrolet	S10	gen2	2002-2003	Pickup	ZR2	皮卡	Extended	6.0	205.3	67.9	66.4	2002-2003 Chevrolet S-10 LS ZR2 Extended Cab 6.0-ft Bed	具体LS ZR2配置页明确列205.3×67.9×66.4 in；W-IN标注without mirrors；72.8-in短货斗	待终核: 67.9-in配置宽度与1999-2000 Wide Stance 71.9-in宽度口径需第二阶段统一
Chevrolet	Silverado 1500HD	gen1	2001-2003	Pickup		皮卡	Crew	6.6	237.2	79.7	76.2	2001 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed; 2002 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed; 2003 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	仅Crew Cab标准货斗；78.7-in货斗按名义6.6填写；2001-2003逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；2003高度76.1/76.2及2WD/4WD高度差异待核
Chevrolet	Silverado 1500HD	gen1	2005	Pickup		皮卡	Crew	6.6	237.2	79.1	77.3	2005 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	2004以Silverado 2500名称销售，不并入本MODEL；W-IN按without mirrors	待终核: 2005宽度79.1与其他年份79.7差异需第二来源确认
Chevrolet	Silverado 1500HD	gen1	2006	Pickup		皮卡	Crew	6.6	239.7	79.7	77.0	2006 Chevrolet Silverado 1500HD Crew Cab 6.6-ft Bed	前后外形更新导致长度变化；W-IN按without mirrors	待终核: 2006三维缺少第二可靠规格源
Chevrolet	Silverado 1500HD	gen1	2007	Pickup	Classic	皮卡	Crew	6.6	239.7	79.7	77.0	2007 Chevrolet Silverado Classic 1500HD Crew Cab 6.6-ft Bed	旧平台Classic延续车型；W-IN按without mirrors	待终核: 2007 Classic三维与销售年份需第二来源终核
Chevrolet	Uplander	gen1	2005-2008	Wagon	LWB	两厢车			204.3	72.0	72.0	2005 Chevrolet Uplander LWB; 2006 Chevrolet Uplander LWB; 2007 Chevrolet Uplander LWB; 2008 Chevrolet Uplander LWB	美国市场止于2008；121.1-in长轴minivan；2005-2008逐年参考车型已覆盖；W-IN按车身宽度	待终核: 逐年参考车型已补齐；Passenger/Cargo和FWD/AWD高度差异待核
Chevrolet	Uplander	gen1	2006-2008	Wagon		两厢车			191.0	72.0	70.5	2006 Chevrolet Uplander SWB; 2007 Chevrolet Uplander SWB; 2008 Chevrolet Uplander SWB	113.0-in短轴版本；2006加入产品线；2006-2008逐年参考车型已覆盖	待终核: 逐年参考车型已补齐；SWB主要为fleet配置，其零售和车队销售边界待核
Chevrolet	Venture	gen1	1997-2004	Wagon		两厢车			186.9	72.0	67.4	1997 Chevrolet Venture SWB; 1998 Chevrolet Venture SWB; 1999 Chevrolet Venture SWB; 2000 Chevrolet Venture SWB; 2001 Chevrolet Venture SWB; 2002 Chevrolet Venture SWB; 2003 Chevrolet Venture SWB; 2004 Chevrolet Venture SWB	短轴112-in wheelbase；2005停产短轴；1997-2004逐年参考车型已补齐	待终核: SWB逐年参考覆盖已补齐；各年度配置与三维是否完全一致待第二阶段核对
Chevrolet	Venture	gen1	1997-2005	Wagon	LWB	两厢车			200.9	72.0	68.1	1997 Chevrolet Venture LWB; 1998 Chevrolet Venture LWB; 1999 Chevrolet Venture LWB; 2000 Chevrolet Venture LWB; 2001 Chevrolet Venture LWB; 2002 Chevrolet Venture LWB; 2003 Chevrolet Venture LWB; 2004 Chevrolet Venture LWB; 2005 Chevrolet Venture LWB	长轴120-in wheelbase；2005仅售长轴；1997-2005逐年参考车型已补齐	待终核: LWB逐年参考覆盖已补齐；货运版年份来源冲突和逐年尺寸口径待核
```

## 5) 下一步优先处理

1. **下一步优先核对：**先核对 Astro Passenger/Cargo、Short/EXT/LWB、RWD/AWD 的真实尺寸边界，判断现有聚合行是否需要拆分。
2. 核对 Avalanche 1500/2500 与第二代 2WD/4WD 的逐年高度差异，避免以单一 4WD 高度覆盖全部版本。
3. 统一 Chevy Van 各年度 `maximum width` 是否排除后视镜，并核对 G10/G20/G30 不同 GVWR 或动力造成的高度差。
4. 解决 S10 ZR2 的 67.9、68.0、71.9-in 宽度冲突，以及普通版和配置页的长度、高度冲突。
5. 核对 El Camino 的 loaded/design height、body width/overall width 及货斗长度代码，随后批量更新迭代状态。

推进信号：CONTINUE

[1]: https://www.edmunds.com/chevrolet/avalanche/2004/features-specs/?utm_source=chatgpt.com "Used 2004 Chevrolet Avalanche Specs & Features | Edmunds"
[2]: https://www.edmunds.com/chevrolet/hhr/2007/st-100845657/features-specs/?utm_source=chatgpt.com "Used 2007 Chevrolet HHR Panel LT Specs & Features | Edmunds"
[3]: https://www.edmunds.com/chevrolet/metro/1999/hatchback/features-specs/?utm_source=chatgpt.com "Used 1999 Chevrolet Metro Hatchback Specs & Features | Edmunds"
[4]: https://www.edmunds.com/chevrolet/silverado-1500hd/2002/crew-cab/features-specs/?utm_source=chatgpt.com "Used 2002 Chevrolet Silverado 1500HD Crew Cab Specs & Features | Edmunds"
[5]: https://www.edmunds.com/chevrolet/uplander/2006/features-specs/?utm_source=chatgpt.com "Used 2006 Chevrolet Uplander Specs & Features | Edmunds"


--- Round 4 / 下一步 ---
## 1) 更新点

- 对 Astro 1985–2005 重新按 Passenger/Cargo、Short/Extended、RWD/AWD 核对并拆分，不再使用原先 5 条过度聚合记录。
- 1985–1989 已明确 Passenger 与 Cargo 的高度并不完全相同：1985–1988 Passenger 采用 `73.7 in`，Cargo 采用 `74.5 in`；1989 Passenger 为 `74.1 in`，Cargo仍为 `74.5 in`。通用汽车
- 1990–1991 按 Short 与 Extended 分开。1990 Passenger 各驱动形式均为 `74.1 in`；1991 Passenger 官方表为 `73.7 in`，Cargo 资料则集中在 `74.3–74.5 in`，本表按适配上限采用 `74.5 in` 并保留来源差异。AutoDetective+3通用汽车+3通用汽车+3
- 1992 Passenger 与 Cargo 已依据官方尺寸页分开：
- Passenger：`76.2 in`
- Cargo：`74.5 in`
两者宽度均按 `77.5 in`；Passenger 表中 AWD Extended 单元格出现 `75.5` 的孤立异常值，本轮没有据此单独制造窄车身记录。通用汽车+1
- 1993–1994 的宽度统一改为 `77.5 in`，并拆分 Short/LWB 及 Passenger/Cargo；官方摘要中的 `77.0` 与具体配置规格的 `77.5` 存在口径差异，本轮以明确标注 without mirrors 的配置最大宽度为准。通用汽车+2Edmunds+2
- 修正第二代 Astro 原先错误的 `75.9-in` 宽度，1995–2005 全部改为 `77.5 in`。1995–1996 Passenger/Cargo 高度分别为 `76.2/76.1 in`；1997 两者均为 `76.0 in`；1998–1999 进一步按 RWD/AWD 的 0.1-in 高度差拆分。通用汽车+5通用汽车+5通用汽车+5
- 2000 单独保留 `74.9 in`；2001–2005 Passenger/Cargo 暂按多年度配置规格统一为 `75.0 in`，继续保留官方年度技术表终核状态。Edmunds+5Edmunds+5Edmunds+5

## 2) 当前批次进度

- 第一阶段补缺失已完成，当前继续执行第二阶段核对。
- Astro 已从 5 条聚合记录扩展为能够区分主要车身和驱动高度差异的记录，重点修正了：
- Passenger/Cargo 高度混用；
- 1990–1994 Short/LWB 混用；
- 第二代宽度误写为 `75.9 in`；
- 1998–1999 RWD/AWD 高度差被覆盖。
- Astro 1985–1999 的主要官方年度尺寸节点已经核对；2000–2005 仍需继续读取各年度官方技术表，确认 AWD、Cargo 和 2003 年底盘更新是否产生进一步外廓变化。
- Avalanche、Chevy Van、El Camino、S10 等车型仍有宽度口径、配置高度或来源冲突需要处理，因此当前批次尚未完成。

## 3) 本轮更新后的全量 TSV

```
MAKE	MODEL	代际	YEAR	结构	版本	分类	CAB	BED	L-IN	W-IN	H-IN	参考车型	备注	迭代状态
Chevrolet	Astro	gen1	1985-1988	Wagon	Passenger	两厢车			176.8	77.0	73.7	1985 Chevrolet Astro Passenger Van; 1986 Chevrolet Astro Passenger Van; 1987 Chevrolet Astro Passenger Van; 1988 Chevrolet Astro Passenger Van	111.0-in短轴乘用版；1985/1987/1988官方尺寸一致；1986按同阶段车身外廓归并	待终核: Passenger/Cargo已拆分；1986 Passenger缺少独立年度尺寸页
Chevrolet	Astro	gen1	1985-1988	Wagon	Cargo	两厢车			176.8	77.0	74.5	1985 Chevrolet Astro Cargo Van; 1986 Chevrolet Astro Cargo Van; 1987 Chevrolet Astro Cargo Van; 1988 Chevrolet Astro Cargo Van	短轴货运版；相较Passenger高0.8 in；外宽77.0 in	待终核: 1986及部分年度Cargo需补独立官方尺寸页
Chevrolet	Astro	gen1	1989	Wagon	Passenger	两厢车			176.8	77.0	74.1	1989 Chevrolet Astro Passenger Van	短轴乘用版；1989高度升至74.1 in	待终核: 尺寸已按Passenger/Cargo拆分；需第二规格源
Chevrolet	Astro	gen1	1989	Wagon	Cargo	两厢车			176.8	77.0	74.5	1989 Chevrolet Astro Cargo Van	短轴货运版；高度高于同期Passenger	待终核: 需补1989 Cargo独立官方尺寸页截图
Chevrolet	Astro	gen1	1990	Wagon	Passenger Short	两厢车			176.8	77.0	74.1	1990 Chevrolet Astro Passenger Van Short RWD/AWD	111.0-in轴距；官方表中RWD与AWD外部三维一致	待终核: 1990 Passenger已核；Maximum Width是否明确排除镜体需统一
Chevrolet	Astro	gen1	1990	Wagon	Passenger LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro Extended Passenger Van RWD/AWD	1990新增Extended车身；与Short共用111.0-in轴距，后悬增加10 in	待终核: Extended上市月份与全年覆盖边界待核
Chevrolet	Astro	gen1	1990	Wagon	Cargo Short	两厢车			176.8	77.0	74.1	1990 Chevrolet Astro Cargo Van Short RWD/AWD	具体Cargo配置规格为176.8×77.0×74.1 in	待终核: 当前Cargo高度由具体配置资料补充，需GM年度货运表交叉确认
Chevrolet	Astro	gen1	1990	Wagon	Cargo LWB	两厢车			186.8	77.0	74.1	1990 Chevrolet Astro Extended Cargo Van RWD/AWD	Extended Cargo按同年度Short Cargo高度，长度增加10 in	待终核: Extended Cargo需补官方年度完整三维表
Chevrolet	Astro	gen1	1991	Wagon	Passenger Short	两厢车			176.8	77.0	73.7	1991 Chevrolet Astro Passenger Van Short RWD/AWD	官方Passenger尺寸表；RWD/AWD外部三维一致	待终核: 聚合规格另列73.5/73.0 in，高度口径存在来源差异
Chevrolet	Astro	gen1	1991	Wagon	Passenger LWB	两厢车			186.8	77.0	73.7	1991 Chevrolet Astro Extended Passenger Van RWD/AWD	Extended与Short高度相同	待终核: 聚合配置高度与官方表存在0.2–0.7-in差异
Chevrolet	Astro	gen1	1991	Wagon	Cargo Short	两厢车			176.8	77.0	74.5	1991 Chevrolet Astro Cargo Van Short RWD/AWD	货运版配置来源出现74.3/74.5 in差异，本行按适配最大值74.5填写	待终核: 需取得1991 Cargo官方技术表裁定74.3/74.5
Chevrolet	Astro	gen1	1991	Wagon	Cargo LWB	两厢车			186.8	77.0	74.5	1991 Chevrolet Astro Extended Cargo Van RWD/AWD	Extended Cargo按适配最大高度74.5 in填写	待终核: 需取得1991 Extended Cargo官方技术表
Chevrolet	Astro	gen1	1992	Wagon	Passenger Short	两厢车			176.8	77.5	76.2	1992 Chevrolet Astro Passenger Van Short RWD/AWD	官方Passenger尺寸表；宽度较1991增至77.5 in	待终核: 官方表已核；需第二来源确认年度宽度变化
Chevrolet	Astro	gen1	1992	Wagon	Passenger LWB	两厢车			186.8	77.5	76.2	1992 Chevrolet Astro Extended Passenger Van RWD/AWD	官方Passenger尺寸表；采用与其余三列一致的77.5-in车身宽度	待终核: AWD Extended宽度单元格孤立显示75.5，判定为表格异常但仍需第二来源确认
Chevrolet	Astro	gen1	1992	Wagon	Cargo Short	两厢车			176.8	77.5	74.5	1992 Chevrolet Astro Cargo Van Short RWD/AWD	官方Cargo尺寸表；RWD/AWD三维一致	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen1	1992	Wagon	Cargo LWB	两厢车			186.8	77.5	74.5	1992 Chevrolet Astro Extended Cargo Van RWD/AWD	官方Cargo尺寸表；Extended长度增加10 in	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen1	1993-1994	Wagon	Passenger Short	两厢车			176.8	77.5	76.2	1993 Chevrolet Astro Passenger Van Short; 1994 Chevrolet Astro Passenger Van Short	两年Passenger具体配置外廓一致；W-IN采用without mirrors最大宽度	待终核: 官方摘要存在77.0-in宽度表示，需统一body width/maximum width口径
Chevrolet	Astro	gen1	1993-1994	Wagon	Passenger LWB	两厢车			186.8	77.5	76.2	1993 Chevrolet Astro Extended Passenger Van; 1994 Chevrolet Astro Extended Passenger Van	Extended Passenger两年外廓一致	待终核: 官方摘要与配置页宽度存在77.0/77.5-in差异
Chevrolet	Astro	gen1	1993-1994	Wagon	Cargo Short	两厢车			176.8	77.5	76.2	1993 Chevrolet Astro Cargo Van Short; 1994 Chevrolet Astro Cargo Van Short	具体Cargo配置规格为176.8×77.5×76.2 in	待终核: 1993官方Cargo摘要列77.0 in且未单列高度，与配置页存在口径差异
Chevrolet	Astro	gen1	1993-1994	Wagon	Cargo LWB	两厢车			186.8	77.5	76.2	1993 Chevrolet Astro Extended Cargo Van; 1994 Chevrolet Astro Extended Cargo Van	Extended Cargo配置规格采用77.5-in without-mirrors宽度	待终核: 1993-1994官方摘要与配置页宽度口径待统一
Chevrolet	Astro	gen2	1995-1996	Wagon	Passenger LWB	两厢车			189.8	77.5	76.2	1995 Chevrolet Astro Passenger Van; 1996 Chevrolet Astro Passenger Van	1995起取消短轴；官方Passenger RWD/AWD外部三维一致	待终核: 1995-1996官方表已核；需第二来源确认
Chevrolet	Astro	gen2	1995-1996	Wagon	Cargo LWB	两厢车			189.8	77.5	76.1	1995 Chevrolet Astro Cargo Van; 1996 Chevrolet Astro Cargo Van	官方Cargo RWD/AWD高度比Passenger低0.1 in	待终核: 1995-1996官方表已核；需第二来源确认
Chevrolet	Astro	gen2	1997	Wagon	Passenger LWB	两厢车			189.8	77.5	76.0	1997 Chevrolet Astro Passenger Van RWD/AWD	官方产品指南列RWD/AWD Passenger为相同外廓	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	1997	Wagon	Cargo LWB	两厢车			189.8	77.5	76.0	1997 Chevrolet Astro Cargo Van RWD/AWD	官方Cargo技术页与Passenger高度相同	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	1998-1999	Wagon	Passenger RWD	两厢车			189.8	77.5	74.9	1998 Chevrolet Astro Passenger Van RWD; 1999 Chevrolet Astro Passenger Van RWD	两年官方Passenger RWD外廓一致	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	1998-1999	Wagon	Passenger AWD	两厢车			189.8	77.5	74.8	1998 Chevrolet Astro Passenger Van AWD; 1999 Chevrolet Astro Passenger Van AWD	AWD Passenger比同期RWD低0.1 in，单独拆分	待终核: 官方表已核；需确认高度是否为轮胎/悬架名义值
Chevrolet	Astro	gen2	1998	Wagon	Cargo RWD/AWD	两厢车			189.8	77.5	75.3	1998 Chevrolet Astro Cargo Van RWD; 1998 Chevrolet Astro Cargo Van AWD	1998官方Cargo表中RWD/AWD高度均为75.3 in	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	1999	Wagon	Cargo RWD	两厢车			189.8	77.5	75.3	1999 Chevrolet Astro Cargo Van RWD	1999 Cargo RWD官方高度75.3 in	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	1999	Wagon	Cargo AWD	两厢车			189.8	77.5	75.2	1999 Chevrolet Astro Cargo Van AWD	1999 Cargo AWD比RWD低0.1 in	待终核: 官方表已核；需第二来源
Chevrolet	Astro	gen2	2000	Wagon	Passenger LWB	两厢车			189.8	77.5	74.9	2000 Chevrolet Astro Passenger Van RWD/AWD	具体配置规格高度74.9 in；宽度明确为without mirrors	待终核: 需读取2000 GM年度技术表确认AWD是否仍低0.1 in
Chevrolet	Astro	gen2	2000	Wagon	Cargo LWB	两厢车			189.8	77.5	74.9	2000 Chevrolet Astro Cargo Van RWD/AWD	具体Cargo配置为189.8×77.5×74.9 in	待终核: 需读取2000 GM年度Cargo表确认RWD/AWD差异
Chevrolet	Astro	gen2	2001-2005	Wagon	Passenger LWB	两厢车			189.8	77.5	75.0	2001 Chevrolet Astro Passenger Van; 2002 Chevrolet Astro Passenger Van; 2003 Chevrolet Astro Passenger Van; 2004 Chevrolet Astro Passenger Van; 2005 Chevrolet Astro Passenger Van	多年度Passenger配置规格均显示75.0-in高度；2003更换部分底盘和制动部件	待终核: 2001-2005需逐年读取GM技术表，确认RWD/AWD及2003底盘更新是否改变名义高度
Chevrolet	Astro	gen2	2001-2005	Wagon	Cargo LWB	两厢车			189.8	77.5	75.0	2001 Chevrolet Astro Cargo Van; 2002 Chevrolet Astro Cargo Van; 2003 Chevrolet Astro Cargo Van; 2004 Chevrolet Astro Cargo Van; 2005 Chevrolet Astro Cargo Van	多年度Cargo配置规格显示75.0-in高度；W-IN按without mirrors	待终核: 2001-2005需逐年读取GM Cargo技术表并核对AWD差异
Chevrolet	Avalanche	gen1	2002	Pickup	1500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 1500 Crew Cab	63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002 2WD/4WD高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2002	Pickup	2500	皮卡	Crew	5.3	221.6	79.8	73.3	2002 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；63.0-in短货斗按名义5.3填写；尺寸采用4WD参考	待终核: 2002驱动形式高度差异及第二规格源未确认
Chevrolet	Avalanche	gen1	2003-2006	Pickup	1500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 1500 Crew Cab; 2004 Chevrolet Avalanche 1500 Crew Cab; 2005 Chevrolet Avalanche 1500 Crew Cab; 2006 Chevrolet Avalanche 1500 Crew Cab	中置门可扩展货斗；2003-2006逐年1500参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；各年度2WD/4WD高度及三维一致性待核
Chevrolet	Avalanche	gen1	2003-2006	Pickup	2500	皮卡	Crew	5.3	221.7	79.8	73.3	2003 Chevrolet Avalanche 2500 Crew Cab; 2004 Chevrolet Avalanche 2500 Crew Cab; 2005 Chevrolet Avalanche 2500 Crew Cab; 2006 Chevrolet Avalanche 2500 Crew Cab	2500重载版本；2003-2006逐年2500参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；各年度高度、GVWR和外廓一致性待核
Chevrolet	Avalanche	gen2	2007-2013	Pickup	1500	皮卡	Crew	5.3	221.3	79.1	76.6	2007 Chevrolet Avalanche Crew Cab; 2008 Chevrolet Avalanche Crew Cab; 2009 Chevrolet Avalanche Crew Cab; 2010 Chevrolet Avalanche Crew Cab; 2011 Chevrolet Avalanche Crew Cab; 2012 Chevrolet Avalanche Crew Cab; 2013 Chevrolet Black Diamond Avalanche Crew Cab	第二代不再提供2500；63.3-in短货斗按名义5.3填写；2007-2013逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；2WD/4WD及配置高度差异和2013 Black Diamond命名口径待核
Chevrolet	Blazer EV	gen1	2024-2026	CUV		越野车			192.2	78.0	65.1	2024 Chevrolet Blazer EV; 2025 Chevrolet Blazer EV; 2026 Chevrolet Blazer EV	纯电跨界SUV；普通LT/RS外部三维按一位小数暂合并；W-IN按without mirrors	待终核: 2024-2026 H-IN在65.0/65.1显示精度间需统一官方口径
Chevrolet	Blazer EV	gen1	2025-2026	CUV	SS	越野车			192.7	78.0	64.8	2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS	高性能SS车身长度和高度与普通版不同；W-IN按without mirrors	可入库
Chevrolet	Chevy Van	gen1	1964	Wagon	G10 Short	两厢车			167.6	72.7	77.3	1964 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 167.56 in、maximum body/rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 官方尺寸已补齐；需第二规格源确认四舍五入口径
Chevrolet	Chevy Van	gen1	1965	Wagon	G10 Short	两厢车			167.5	72.8	77.3	1965 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方图示maximum width 72.75 in、unloaded height 77.25 in	待终核: 1965尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen1	1966	Wagon	G10 Short	两厢车			168.3	72.7	77.3	1966 Chevrolet G10 Chevy Van 90-in Wheelbase	90.0-in wheelbase；官方overall length 168.30 in、across-rear-bumper width 72.74 in、base-GVW curb height 77.28 in	待终核: 1966尺寸缺少第二可靠规格源
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 90-in Wheelbase	90-in短轴；官方年度图表显示171-in总长、75-in最大宽度、77.25-in高度	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1967-1969 Chevrolet G10 Chevy Van 108-in Wheelbase	108-in长轴G10；与短轴宽度和高度相同	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1967-1969	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1967-1969 Chevrolet G20 Chevy Van 108-in Wheelbase	108-in长轴G20；重载悬架使整车高度79.0 in，不能并入G10 Regular	待终核: 1967-1969宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Short	两厢车			171.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 90-in Wheelbase	第二代末年；暂按1969同代同车身外廓延续填入	待终核: 缺少1970独立G-Van官方尺寸页，三维为同代末年延续值
Chevrolet	Chevy Van	gen2	1970	Wagon	G10 Regular	两厢车			189.0	75.0	77.3	1970 Chevrolet G10 Chevy Van 108-in Wheelbase	第二代末年108-in G10；暂按1969同车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen2	1970	Wagon	G20 Regular	两厢车			189.0	75.0	79.0	1970 Chevrolet G20 Chevy Van 108-in Wheelbase	第二代末年108-in G20；暂按1969重载车身外廓延续	待终核: 缺少1970独立G-Van官方尺寸页
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in短轴；1972官方表为177×79.5×79.0 in；1971先按同代首期同结构补入	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G10 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in标准长轴；1972官方表为201×79.5×79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Short	两厢车			177.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in短轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G20 Regular	两厢车			201.0	79.5	79.0	1971-1972 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in标准长轴G20；1972官方表高度79.0 in	待终核: 1971缺少独立G-Van尺寸页，当前为1972邻年延续值
Chevrolet	Chevy Van	gen3	1971-1972	Wagon	G30 Regular	两厢车			201.0	79.5	80.3	1971-1972 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1972官方高度80.25 in按一位小数记为80.3	待终核: 1971缺少独立G-Van尺寸页；1972宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 110-in Wheelbase	官方OH 78.75 in，按一位小数记为78.8	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1973 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.75 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1973 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Short	两厢车			177.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1973	Wagon	G30 Regular	两厢车			201.0	79.5	81.3	1973 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；OH 81.25 in按一位小数记为81.3	待终核: 1973宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Short	两厢车			177.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G10 Regular	两厢车			201.0	79.5	79.5	1974 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方整车高度79.5 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1974 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方整车高度80.0 in	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1974	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1974 Chevrolet G30 Chevy Van 125-in Wheelbase	年度尺寸表仅列125-in完整G30车身	待终核: 1974宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1975 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1975 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1975	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1975 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in G30完整车身	待终核: 1975宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Short	两厢车			177.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G10 Regular	两厢车			201.0	79.5	78.8	1976 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Short	两厢车			177.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G20 Regular	两厢车			201.0	79.5	80.2	1976 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Short	两厢车			177.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1976	Wagon	G30 Regular	两厢车			201.0	79.5	81.2	1976 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1976宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Short	两厢车			177.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G10 Regular	两厢车			201.0	79.5	79.4	1977 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Short	两厢车			177.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G20 Regular	两厢车			201.0	79.5	80.0	1977 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1977	Wagon	G30 Regular	两厢车			201.0	79.5	81.0	1977 Chevrolet G30 Chevy Van 125-in Wheelbase	年度表仅列125-in完整G30车身	待终核: 1977宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 110-in Wheelbase	前后保险杠变化后Short总长增至178.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1978 Chevrolet G10 Chevy Van 125-in Wheelbase	Regular总长增至202.2 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1978 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1978	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1978 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1978宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Short	两厢车			178.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G10 Regular	两厢车			202.2	79.5	78.8	1979 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 78.8 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Short	两厢车			178.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G20 Regular	两厢车			202.2	79.5	80.2	1979 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Short	两厢车			178.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 110-in Wheelbase	年度表明确列出110-in G30完整车身	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1979	Wagon	G30 Regular	两厢车			202.2	79.5	81.2	1979 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.2 in	待终核: 1979宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 110-in Wheelbase	110-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G10 Regular	两厢车			202.2	79.5	79.4	1980 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；官方OH 79.4 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Short	两厢车			178.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G20 Regular	两厢车			202.2	79.5	80.0	1980 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；官方OH 80.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1980	Wagon	G30 Regular	两厢车			202.2	79.5	81.0	1980 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；官方OH 81.0 in	待终核: 1980宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1981-1982 Chevrolet G10 Chevy Van 110-in Wheelbase	1981官方尺寸；1982按相邻年度同结构连续值补入	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1981-1982 Chevrolet G10 Chevy Van 125-in Wheelbase	125-in G10；1981官方OH 79.2 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1981-1982 Chevrolet G20 Chevy Van 110-in Wheelbase	110-in G20；1981官方OH 79.8 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1981-1982 Chevrolet G20 Chevy Van 125-in Wheelbase	125-in G20；1981官方OH 79.5 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1981-1982	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1981-1982 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30；1981官方OH 81.9 in	待终核: 1982缺少独立G-Van尺寸包，当前为1981邻年延续值
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1983-1988 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	年度资料中的短轴G10外廓一致	待终核: 逐年车型名称由Chevy Van向Vandura并行变化，第二阶段统一名称口径
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G10 Regular	两厢车			202.2	79.5	79.2	1983-1988 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	125-in G10；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Short	两厢车			178.2	79.5	79.8	1983-1988 Chevrolet G20 Chevy Van/Vandura 110-in Wheelbase	110-in G20；完整厢式车尺寸	待终核: 1984乘用版表未单列该组合，Cargo配置覆盖需第二阶段核对
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1983-1988 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	125-in G20；年度外廓一致	待终核: 逐年车型名称覆盖待统一
Chevrolet	Chevy Van	gen3	1983-1988	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1983-1988 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	125-in G30重载完整厢式车	待终核: 发动机和GVWR造成的细微高度差待第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1989 Chevrolet G10 Chevy Van/Vandura 110-in Wheelbase	1989年度Short G10外廓	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1989 Chevrolet G10 Chevy Van/Vandura 125-in Wheelbase	1989 G10 Regular高度降至79.1 in	待终核: 1989宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1989	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1989 Chevrolet G20 Chevy Van/Vandura 125-in Wheelbase	1989年度尺寸表未列G20 Short，因此仅保留Regular	待终核: 1989 Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1989	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1989 Chevrolet G30 Chevy Van/Vandura 125-in Wheelbase	汽油版高度81.8 in、HD/柴油版81.9 in；本行取最大值81.9	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Short	两厢车			178.2	79.5	80.0	1990 Chevrolet G10 Chevy Van 110-in Wheelbase	1990年度Short G10高度80.0 in	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G10 Regular	两厢车			202.2	79.5	79.7	1990 Chevrolet G10 Chevy Van 125-in Wheelbase	1990年度Regular G10外廓	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Short	两厢车			178.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 110-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G20 Regular	两厢车			202.2	79.5	80.9	1990 Chevrolet G20 Chevy Van 125-in Wheelbase	汽油版高度80.9 in、柴油版80.5 in；本行取最大值	待终核: 不同动力高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Regular	两厢车			202.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 125-in Wheelbase	125-in G30重载车身	待终核: 1990宽度是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1990	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1990 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；1990起正式列入整车尺寸表	待终核: 1990 Extended缺少第二可靠规格源
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Short	两厢车			178.2	79.5	79.4	1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G10 Regular	两厢车			202.2	79.5	79.1	1991-1992 Chevrolet G10 Chevy Van 125-in Wheelbase	两年年度表外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G20 Regular	两厢车			202.2	79.5	79.5	1991-1992 Chevrolet G20 Chevy Van 125-in Wheelbase	年度表未列G20 Short，因此仅保留Regular	待终核: Cargo配置是否另有G20 Short需第二阶段核对
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Regular	两厢车			202.2	79.5	81.9	1991-1992 Chevrolet G30 Chevy Van 125-in Wheelbase	汽油版高度81.8 in、HD版本81.9 in；本行取最大值	待终核: 不同GVWR高度是否需独立拆行
Chevrolet	Chevy Van	gen3	1991-1992	Wagon	G30 Extended	两厢车			223.2	79.5	82.3	1991-1992 Chevrolet G30 Chevy Van 146-in Extended Wheelbase	146-in完整加长厢式车；两年外廓一致	待终核: W-IN是否明确排除镜体需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Short	两厢车			180.0	79.1	80.0	1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；1993 style-specific规格可覆盖短轴外廓	待终核: 1994 Short尺寸需独立来源确认；1993/1994宽度口径需终核
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Regular	两厢车			204.1	79.5	79.7	1993-1994 Chevrolet Chevy Van G20/G30 Regular Wheelbase	125-in wheelbase；1993和1994规格资料均覆盖204.1-in长度及79.5-in宽度	待终核: 1993-1994 Regular H-IN需补官方年度技术表交叉确认
Chevrolet	Chevy Van	gen3	1993-1994	Wagon	Extended	两厢车			225.0	79.5	82.3	1993-1994 Chevrolet G30 Chevy Van Extended Wheelbase	146-in加长完整厢式车；1993扩展车身规格为225.0×79.5×82.3 in	待终核: 1994 Extended需补独立年度规格源
Chevrolet	Chevy Van	gen3	1995	Wagon	Short	两厢车			180.1	79.5	80.0	1995 Chevrolet Chevy Van G10/G20 Short Wheelbase	110-in wheelbase；GM官方Maximum Width为79.5 in；聚合规格另列79.1 in without mirrors	待终核: 1995 Short W-IN存在79.5/79.1来源差异
Chevrolet	Chevy Van	gen3	1995	Wagon	Regular	两厢车			204.1	79.5	79.7	1995 Chevrolet Chevy Van G10/G20/G30 Regular Wheelbase	125-in wheelbase；官方长度和最大宽度；高度由独立规格页覆盖	待终核: 1995 Regular需补第二官方高度来源
Chevrolet	Chevy Van	gen3	1995	Wagon	Extended	两厢车			225.1	79.5	82.3	1995 Chevrolet G30 Chevy Van Extended Wheelbase	146-in wheelbase；加长完整厢式车	待终核: 1995 Extended高度82.3 in需补官方年度尺寸页交叉确认
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Regular	两厢车			204.1	79.5	79.7	1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase	1996仅保留GVWR高于8500 lb的旧平台G-Classic；不采用同期GMT600 Express的135-in轴距尺寸	待终核: 1996 G-Classic Regular沿用旧平台外廓，需补直接官方G-Classic尺寸页
Chevrolet	Chevy Van	gen3	1996	Wagon	G-Classic Extended	两厢车			225.0	79.1	82.3	1996 Chevrolet Chevy Van Classic G30 Extended 146-in Wheelbase	旧平台146-in G-Classic；W-IN采用明确标注without mirrors的79.1 in	待终核: 1996 Extended存在225.0/225.1及79.1/79.5来源精度差异
Chevrolet	El Camino	gen1	1959	Pickup		皮卡	Regular	6.5	210.9	79.9	58.8	1959 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类；L-IN和H-IN来自官方车型图	待终核: 官方El Camino车型页未单列整车总宽，W-IN采用同年同平台full-size Chevrolet 79.9-in外宽
Chevrolet	El Camino	gen1	1960	Pickup		皮卡	Regular	6.5	210.8	80.8	58.4	1960 Chevrolet El Camino	官方货斗内部长度76.25 in、最大货斗宽64.25 in；BED按名义6.5归类	待终核: 1960尺寸缺少第二可靠规格源
Chevrolet	El Camino	gen2	1964	Pickup		皮卡	Regular	6.5	198.8	73.2	54.1	1964 Chevrolet El Camino	115-in wheelbase；官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1964官方高度为loaded口径，需与其他年份design/unloaded高度统一
Chevrolet	El Camino	gen2	1965	Pickup		皮卡	Regular	6.5	201.5	74.5	53.3	1965 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；BED按名义6.5填写	待终核: 1965三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1966	Pickup		皮卡	Regular	6.5	197.5	75.0	54.5	1966 Chevrolet El Camino	官方货斗地板长度78.5 in、货斗上沿长度73.5 in；前后外形变化使车长较1965缩短	待终核: 1966三维需第二可靠规格源交叉确认
Chevrolet	El Camino	gen2	1967	Pickup		皮卡	Regular	6.5	197.5	75.0	56.5	1967 Chevrolet El Camino	与1966车长、宽度相同，但官方高度增加至56.5 in	待终核: 1967高度变化需第二可靠来源确认
Chevrolet	El Camino	gen3	1968-1969	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1968-1969 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: 1968-1969 W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen3	1970	Pickup		皮卡	Regular	6.5	206.5	75.4	54.4	1970 Chevrolet El Camino	1970年度官方外廓与1968-1969及1971-1972不同，单独拆分	待终核: 1970货斗实际长度需在年度货斗尺寸页再次确认
Chevrolet	El Camino	gen3	1971-1972	Pickup		皮卡	Regular	6.5	207.0	75.8	56.0	1971-1972 Chevrolet El Camino	官方货斗上沿长度79.25 in、地板长度73.25 in；BED按名义6.5填写	待终核: W-IN由75.75 in按一位小数记为75.8
Chevrolet	El Camino	gen4	1973	Pickup		皮卡	Regular	6.5	213.2	76.6	53.8	1973 Chevrolet El Camino	第四代首年；官方货斗有效地板长度约80.8 in，BED按名义6.5填写	待终核: 1973货斗上沿与地板长度代码需再次统一
Chevrolet	El Camino	gen4	1974-1975	Pickup		皮卡	Regular	6.5	215.2	76.6	53.9	1974-1975 Chevrolet El Camino	保险杠变化使总长增至215.2 in；两年官方外廓一致；货斗有效地板长度约80.8 in	待终核: 1975需补直接年度尺寸页截图交叉确认
Chevrolet	El Camino	gen4	1976	Pickup		皮卡	Regular	6.5	213.3	76.9	54.2	1976 Chevrolet El Camino	标准车长213.3 in；带可选impact strips时可达214.3 in，本行采用标准装备尺寸	待终核: W-IN采用官方maximum body/overall car width 76.9 in，需统一W103/W116代码口径
Chevrolet	El Camino	gen4	1977	Pickup		皮卡	Regular	6.5	213.3	77.3	54.2	1977 Chevrolet El Camino	标准车长213.3 in；官方maximum overall width of car增至77.3 in	待终核: 1977最大车宽与body width 76.9 in的字段口径需终核
Chevrolet	El Camino	gen5	1978	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1978 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1978尺寸需第二可靠来源交叉确认
Chevrolet	El Camino	gen5	1979-1986	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1979-1986 Chevrolet El Camino	1979/1983/1985/1986官方年度图示均为201.6×71.9×53.8 in；货斗上沿79.5 in、地板78.5 in	待终核: 1980-1982及1984需补各自年度直接尺寸页，当前按同代连续官方外廓合并
Chevrolet	El Camino	gen5	1987	Pickup		皮卡	Regular	6.5	201.6	71.9	53.8	1987 Chevrolet El Camino	官方图示货斗上沿79.5 in、地板78.5 in，BED按名义6.5填写；W-IN为车身外宽	待终核: 1987尺寸需第二可靠来源交叉确认
Chevrolet	HHR	gen1	2006-2011	Wagon		两厢车			176.2	69.1	63.1	2006 Chevrolet HHR; 2007 Chevrolet HHR; 2008 Chevrolet HHR; 2009 Chevrolet HHR; 2010 Chevrolet HHR; 2011 Chevrolet HHR	5-door retro wagon；普通配置等级不拆；2006-2011逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；普通版逐年尺寸、悬架与配置差异待核
Chevrolet	HHR	gen1	2007-2011	Wagon	Panel	两厢车			176.2	69.1	63.1	2007 Chevrolet HHR Panel; 2008 Chevrolet HHR Panel; 2009 Chevrolet HHR Panel; 2010 Chevrolet HHR Panel; 2011 Chevrolet HHR Panel	封闭式货运Panel；外部尺寸按普通HHR车身；2007-2011逐年参考车型已覆盖	待终核: 逐年参考车型已补齐；Panel与普通版外廓是否完全一致待核
Chevrolet	HHR	gen1	2008-2010	Wagon	SS	两厢车			176.5	69.1	62.5	2008 Chevrolet HHR SS; 2009 Chevrolet HHR SS; 2010 Chevrolet HHR SS	SS保险杠和悬架使长度/高度不同；2008-2010逐年参考车型已覆盖；W-IN按without mirrors	待终核: 逐年参考车型已补齐；手动/自动及年度悬架高度差待核
Chevrolet	HHR	gen1	2009	Wagon	Panel SS	两厢车			176.5	69.1	62.5	2009 Chevrolet HHR Panel SS	单年高性能封闭式Panel	待终核: 2009 Panel SS缺少第二可靠规格源
Chevrolet	Lumina APV	gen1	1990-1992	Wagon		两厢车			194.2	73.9	65.2	1990 Chevrolet Lumina APV; 1991 Chevrolet Lumina APV; 1992 Chevrolet Lumina APV	minivan轮廓；1990-1992全部年度参考车型已补齐；W-IN按车身宽度口径	待终核: 逐年参考车型已覆盖；1990-1992高度、配置和车身外廓需逐年终核
Chevrolet	Lumina APV	gen1	1993	Wagon		两厢车			194.2	73.9	65.7	1993 Chevrolet Lumina APV	官方1993 MVMA：整车长度194.2 in；车身宽度73.9 in；外后视镜总宽83.3 in；整车高度65.7 in；W-IN采用不含后视镜车身宽度	待终核: 1993参考车型及三维已补齐；仍需第二可靠来源及1993/1994长度变化边界复核
Chevrolet	Lumina APV	gen1	1994-1996	Wagon		两厢车			191.5	73.9	65.7	1994 Chevrolet Lumina APV; 1995 Chevrolet Lumina APV; 1996 Chevrolet Lumina APV	1994起市场名称常简化为Lumina Minivan；1994-1996全部年度参考车型已补齐	待终核: 逐年参考车型已覆盖；1994-1996市场名称、尺寸及配置口径待终核
Chevrolet	Metro	gen1	1998-2000	Hatchback		两厢车			149.4	62.6	54.7	1998 Chevrolet Metro Hatchback; 1999 Chevrolet Metro Hatchback; 2000 Chevrolet Metro Hatchback	Chevrolet品牌Metro Hatchback覆盖1998-2000；逐年参考车型已补齐；W-IN按without mirrors	待终核: 逐年参考车型已补齐；发动机及配置是否导致外廓差异待核
Chevrolet	Metro	gen1	1998-2001	Sedan		三厢车			164.0	62.6	55.4	1998 Chevrolet Metro Sedan; 1999 Chevrolet Metro Sedan; 2000 Chevrolet Metro Sedan; 2001 Chevrolet Metro Sedan	2001仅保留四门Sedan；1998-2001逐年参考车型已补齐；W-IN按without mirrors	待终核: 逐年参考车型已补齐；1998-2001三维及配置一致性待核
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
Chevrolet	S10	gen1	1991	Pickup		皮卡	Regular	7.5	194.2	64.7	61.6	1991 Chevrolet S-10 Regular Cab 2WD 7.5-ft Bed	89.0-in货斗；1991高度独立	待终核
```


--- Round 5 / 下一步 ---
ChatGPT 说：你已达到此对话的长度上限，你可以开始新聊天以继续对话。

