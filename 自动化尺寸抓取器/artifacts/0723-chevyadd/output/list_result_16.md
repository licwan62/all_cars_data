# 文件名：list.tsv


--- 恢复现场 / 已有回复 ---



--- Round 1 / 存档续跑 ---
## 1) 更新点

- 将 Chevy Van 原先仍为空的 `1971-1982`、`1983-1989`、`1990-1992` 三段，替换为按 G10/G20/G30、110/125/146-in 轴距、Short/Regular/Extended 拆分的实际车身记录。
- 1971–1977 的标准长度为 Short `177.0 in`、Regular `201.0 in`，宽度统一为 `79.5 in`；不同年度和载重系列的高度存在明显变化，因此没有整段共用一个高度。1973 和 1976 的官方表还明确列出 G30 Short，其他部分年份仅列 G30 Regular。通用汽车+5通用汽车+5通用汽车+5
- 1978 年起车长调整为 Short `178.2 in`、Regular `202.2 in`；1979 年再次出现 G30 Short。1981 年的 G10、G20、G30 高度分别进一步细分，不能继续只保留 Short/Regular 两条笼统记录。通用汽车+3通用汽车+3通用汽车+3
- 1983–1988 已补成五种主要车身：G10 Short、G10 Regular、G20 Short、G20 Regular、G30 Regular；1989 年官方表未列 G20 Short，因此单独拆年，没有错误延续该组合。通用汽车+3通用汽车+3通用汽车+3
- 1990 年补入首批完整 G30 Extended，尺寸为 `223.2 × 79.5 × 82.3 in`；1991–1992 继续保留 Extended，同时取消未在年度尺寸表出现的 G20 Short。通用汽车+2通用汽车+2
- GM 当前公开目录没有单独列出 1971 与 1982 G-Van 技术包，因此这两个年份分别按相邻的 1972、1981/1983 同结构连续尺寸先行补入，并在迭代状态中明确保留“邻年延续值”，未伪装成已直接取得的年度原始值。通用汽车

## 2) 当前批次进度

- Chevy Van 1964–1996：现有拆分行均已具备版本、长宽高和参考车型，不再存在整行尺寸空白。
- Chevy Van 第一阶段剩余事项仅为 1971、1982 的独立年度资料，以及少量车宽是否明确排除镜体的口径问题；这些属于第二阶段核对，不再阻塞成表。
- 当前最大缺失区转为 El Camino 1959–1977、1979–1986，其 BED、三维和参考车型仍未补齐。
- S10 ZR2 1994–1998、2001–2003 仍有 W-IN、H-IN 或整组三维空值。
- Astro、HHR、Metro、Uplander、Venture 仍有部分逐年参考车型覆盖缺失。
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

- **下一步优先补缺失：**补齐 El Camino 1959–1977、1979–1986 的名义 BED、长宽高和参考车型，先处理每代首末年及发生保险杠变化的年份。
- 继续解决 S10 ZR2 1994–1998 的 W-IN、H-IN，以及 2001 整组三维空值。
- 补齐 S10 ZR2 2002–2003 的可靠最大宽体宽度。
- 补充 Astro 1990–2005、HHR、Metro、Uplander、Venture 尚未覆盖的逐年参考车型。
- 只有上述缺失全部清除后，再进入第二阶段，集中核对邻年延续值、without-mirrors 口径、来源冲突与迭代状态。

推进信号：CONTINUE

