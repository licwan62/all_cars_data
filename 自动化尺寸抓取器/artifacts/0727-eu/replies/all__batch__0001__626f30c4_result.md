# 任务：all 第 1-100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0001__626f30c4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1-100 行

【任务要求】
# EU Auto-Data Ktype 与尺寸组补全规则

输入是 Tab 分隔的欧洲车型表。`Ktype` 是输入外键，但不保证唯一对应物理车身。输出两张解耦的 TSV：Ktype 映射表和 DIMENSION_GROUP 尺寸事实表。

<!-- fitment-data-contract
full_table:
  columns:
    - id
    - Ktype
    - NormalizedBodyStyle
    - Generation
    - BodyCode
    - Doors
    - DIMENSION_GROUP_ID
    - MatchConfidence
    - Notes
    - IterationStatus
  auto_empty_columns: []
dimension_group_table:
  enabled: true
  columns:
    - DIMENSION_GROUP_ID
    - LengthMM
    - WidthMM
    - HeightMM
    - DimensionSource
    - SourceURL
  auto_empty_columns: []
subseries_match:
  enabled: false
  columns: []
  auto_empty_columns: []
-->

## 一、最高优先级

目标是用最少的独立尺寸研究覆盖全部输入 Ktype，不是为每个 Ktype 重复建立研究记录。顺序固定为：

1. 优先复用已闭合的 DIMENSION_GROUP。
2. 合并不改变物理外廓的发动机、能源、功率、变速箱、普通配置和 facelift 标签。
3. 仅研究缓存未覆盖的独立物理外廓。
4. `PENDING=0` 后立即进入一次机械收尾并输出 `COMPLETE`。
5. 若所有剩余 `PENDING` 都已穷尽允许的可靠来源，仍无法在不猜测、不拼接不同配置且不降低证据标准的前提下推进，则进入 `ALMOST` 收尾，不再重复检索。

不存在明确冲突时，“已有可靠结果并停止”优先于“继续寻找更理想来源”。不得为补非必需字段、提高置信度、优化措辞、增加来源或枚举理论分支而增加轮次。

## 二、输出数据契约

### Ktype 映射表

- 严格使用契约中的 10 列；不输出输入原字段、三维、轴距、来源或抓取过程字段。
- `Ktype` 按文本逐字保留，不得转浮点、改前导零或生成不存在的 Ktype。每个输入 Ktype 至少一行。
- 单一物理外廓时 `id=Ktype`。确认存在多个不同物理外廓时才派生 `{Ktype}_{简短 ASCII 特征}`，如 `_3dr`、`_lwb`、`_facelift`；拆分后不保留无后缀基础行。
- 多行是例外，必须有明确物理证据；不得使用无语义序号或猜测性分支。
- `NormalizedBodyStyle`：Schrägheck/Hatchback→Hatchback，Stufenheck/Limousine/Sedan→Sedan，Kombi/Touring/Estate→Wagon，Cabriolet/Roadster→Convertible，Großraumlimousine→MPV，Kasten/Kastenwagen→Van，Pritsche→Pickup。
- `Generation`、`BodyCode`、`Doors` 是辅助字段。来源未明确时允许留空；若空值不影响外廓区分，不阻塞 `READY`。不得把发动机代号当作 `BodyCode`。
- `MatchConfidence` 只用 `HIGH|MEDIUM|LOW`，表示映射置信度；`MEDIUM/LOW` 不自动阻塞 `READY`。
- `Notes` 只记录必要的分支边界或人工决定，不重复尺寸、来源、缓存和核验过程。
- `IterationStatus` 只用 `READY` 或 `PENDING: <具体原因>`。`PENDING` 行的 `DIMENSION_GROUP_ID` 必须留空。

### DIMENSION_GROUP 表

- 严格使用契约中的 6 列。每个 `DIMENSION_GROUP_ID` 唯一，三维和来源完整，且必须被当前映射表引用。
- 同一物理外廓只使用一个稳定尺寸组；多个 Ktype 应直接复用，不得因发动机、来源或 Ktype 不同重复建组。
- 推荐 ID：`EU-{MAKE}-{MODEL}-{GENERATION}-{BODYSTYLE}-{BRANCH}-{SEQUENCE}`，只用大写 ASCII、数字和连字符。
- 若当前三维与累计表中同名 ID 冲突，不得覆盖；创建新序号 ID 并同步映射。
- `LengthMM/WidthMM/HeightMM` 是同一量产配置的正整数 mm。`WidthMM` 强制为不含外后视镜的车身宽度。不得拼接不同配置的三维。
- 只有含镜宽度或宽度口径无法确认时，该组不得落盘，映射保持 `PENDING`。

## 三、物理分支决策

### 可能需要拆分

只有可靠证据表明当前 Ktype 实际覆盖不同外廓时，才按 BodyStyle/门数外形、轴距 `SWB/LWB`、`L1/L2/L3`、车顶级别、`SRW/DRW`、CAB/BED、宽体或工厂独立特殊车身拆分。不同代际或车身代码需独立核对。

只输出当前 Ktype 有证据覆盖的分支，不得枚举该车系理论上的全部配置，不得将 prefl/facelift 与轴距、车顶、驾驶室或货斗做无证据的笛卡尔积。证据只确认一个分支时只输出该分支；无法确认是否多分支时，保留单行并使用最匹配输入的标准量产外廓。

### Facelift

facelift、LCI、Phase II、改款年份或外观名称本身不是拆分或新建尺寸组的充分条件。

1. 先判断改款是否改变 BodyStyle、门数、BodyCode、轴距/车顶/驾驶室/货斗级别或标准量产三维。
2. 无可靠证据证明上述差异，或资料明确显示三维相同时，视为同一物理外廓：不建 `_prefl/_facelift` 派生行，保留一行并复用同一尺寸组。
3. 只有可靠资料明确证明至少一个三维值或物理边界不同，才拆分并建立不同尺寸组。
4. Ktype 生产期跨越改款日期只是线索，不能单独触发拆分。

### 不拆分

发动机、功率、燃料/能源、变速箱、不改外廓的驱动形式和普通配置不触发拆分或重新抓取。

可拆卸车顶行李架/横杆、天线、普通轮胎轮毂、装饰包、非独立车身的保险杠/扰流板和其他非永久附件默认不拆分。`HeightMM` 优先使用不含可拆附件的标准车身高度；不得仅因资料同时列出含/不含行李架高度而创建 lowroof/highroof。只有工厂定义为独立量产车身且 Ktype 明确覆盖时才例外。

## 四、来源与停止条件

优先级：厂商官网/手册/技术资料/认证资料 > Auto-Data、Car.info、UltimateSpecs、Automobile-Catalog、Parkers > 其他可追溯规格数据库。搜索摘要、AI 摘要、论坛、二手车广告和无出处聚合页不能单独支撑尺寸组。`SourceURL` 必须是直接页面，不得是搜索结果页。

满足任一条后立即闭合，不再搜索：

1. 一个官方来源支持同一配置的完整三维，且宽度口径可确认；
2. 一个允许的可信规格数据库给出匹配车型的完整三维，且未发现具体冲突；
3. 最多两个可靠来源合计支持同一配置的完整三维。

官方来源不是 `READY` 的强制条件。已有可信二级来源且无冲突时，不得仅为寻找官方页面或提高 `MatchConfidence` 继续搜索。只有同市场、同阶段、同车身/配置、同测量口径下存在具体数值冲突，或宽度口径不明时，才增加核验。

`ALMOST` 只用于真正的证据穷尽：每个剩余 `PENDING` 都必须有具体阻塞原因，并且已无契约允许的可靠来源路径可继续验证。临时网络、浏览器、登录、页面或超时故障，单轮搜索无结果，或仅达到轮次/时间上限，都不是证据穷尽，不得触发 `ALMOST`。不得为了结束任务而降低来源标准、拼接不同配置的三维、猜测缺失值或把 `PENDING` 强行改成 `READY`。

## 五、每批执行流程

1. 一次读取当前批全部输入。
2. 按 Make + Model + Generation 候选 + BodyStyle + BodyCode 候选聚类，先消除只由动力和普通配置造成的重复。
3. 查询当前批及历史缓存，批量关联已有尺寸组。已闭合组不得重新打开来源页。
4. 只对缓存未命中的独立物理外廓抓取一次；一个组闭合后立即关联所有适用 Ktype。
5. 最后只处理无组可关联的 `PENDING`。不得按 Ktype 串行重复搜索同一外廓。
6. `PENDING=0` 后停止外部检索，最多执行一次表头、唯一性、引用闭合、非空和链接检查，然后立即 `COMPLETE`。
7. 若仍有 `PENDING`，但所有剩余项均满足证据穷尽条件，则停止重复搜索，输出当前全部可交付的 `READY` 数据并以 `ALMOST` 结束。

## 六、输出与终检

### CONTINUE

未完成时仅依次输出：更新点、当前批进度、本轮新增/修改的 Ktype TSV、本轮首次创建/修正的 DIMENSION_GROUP TSV、下一步优先处理，最后一行 `推进信号：CONTINUE`。无变化写“无”；不重复输出未变行或已闭合尺寸组。

### ALMOST

`ALMOST` 是证据穷尽时的任务级终态，但不是成功，也不是行级 `IterationStatus`。剩余记录必须继续使用 `PENDING: <具体原因>`；不得在 Ktype 映射行中写 `ALMOST`。任务以 `ALMOST` 结束后不再发送 `CONTINUE`，但正式完整性审计仍应把它视为未完整任务。

只有仍存在 `PENDING`，并且每个剩余项都满足第四节的证据穷尽条件时，才可输出 `ALMOST`。同一条 ALMOST 回复必须依次包含：

1. 证据穷尽说明和当前 `READY/PENDING` 计数；
2. 每个剩余 `PENDING` 的 Ktype 与具体阻塞原因；
3. 全部当前 `READY` 映射组成的完整 Ktype TSV，不得只给变化行、引用上轮或写“其余不变”；
4. 按任务指定精确文件名创建、内容与内嵌 READY 映射 TSV 一致的可点击 `.tsv` sandbox 链接；
5. 仅由这些 READY 映射引用、且覆盖其全部引用的完整 DIMENSION_GROUP TSV；每组必须包含完整正整数三维、`DimensionSource` 和非空直接 `SourceURL`，不得包含孤立组；
6. 按任务指定精确文件名创建、内容与内嵌 DIMENSION_GROUP TSV 一致的第二个可点击 `.tsv` sandbox 链接；
7. 最后一行单独输出 `推进信号：ALMOST`。

ALMOST 两张表只交付当前可可靠入库的 READY 记录及其尺寸组；PENDING 只在阻塞清单中保留，不得混入 READY 下载文件。缺少任一当前 READY 映射、任一被引用尺寸组、任一 `SourceURL`、任一精确 sandbox 链接或任一 PENDING 原因时，不得输出 `ALMOST`。若 `PENDING=0`，必须使用 `COMPLETE`，不得降级为 `ALMOST`。

### COMPLETE

`PENDING=0` 后的下一条回复必须在同一条消息中依次包含：更新点、进度、最终完整 Ktype TSV、按任务指定文件名创建的可点击 `.tsv` sandbox 链接、最终完整 DIMENSION_GROUP TSV、对应 sandbox 链接，最后一行 `推进信号：COMPLETE`。不得只给变化行、引用上轮或写“其余不变”。

终检只做以下机械项，不重新研究：

1. 两张表的固定表头和列数正确，`id` 与 `DIMENSION_GROUP_ID` 各自唯一。
2. 每个输入 Ktype 至少被覆盖一次；每个映射均为 `READY` 并引用恰好一个存在的尺寸组。
3. 尺寸组三维为正整数、宽度不含后视镜、来源和直接 URL 非空，且没有孤立组。
4. 不存在 `PENDING`、未解决冲突、重复物理组或无证据派生分支。
5. 两个任务指定文件名的可点击 sandbox 链接齐全。

任一机械项不满足时只修复该项，不得重新展开逐车型或逐来源研究；修复后立即输出两张完整表、两个链接和 `COMPLETE`。


【执行顺序】
执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。

【配置附加规则】


【当前文件名】
all.tsv

【当前独立任务】
all 第 1-100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	Ktype
AC	428	7	Cabriolet	Heckantrieb	Benzin	257	349	Jan 1965	Dec 1974	12424
AC	Ace	4.6	Cabriolet	Heckantrieb	Benzin	240	326	Oct 1998	-	12428
AC	Ace	4.9	Cabriolet	Heckantrieb	Benzin	179	243	Oct 1998	-	12430
AC	Ace	4.9	Cabriolet	Heckantrieb	Benzin	191	260	Jan 1995	Oct 1998	12426
AC	Ace	4.9 Super Charger	Cabriolet	Heckantrieb	Benzin	239	325	Oct 1998	-	12431
AC	Aceca	4.6	Coupe	Heckantrieb	Benzin	240	326	Oct 1998	Dec 2001	12434
AC	Aceca	4.9	Coupe	Heckantrieb	Benzin	179	243	Sep 1993	Dec 1997	12436
AC	Aceca	4.9 Super Charger	Coupe	Heckantrieb	Benzin	239	325	Oct 1998	Dec 2001	12437
AC	Cobra iv	4.9	Cabriolet	Heckantrieb	Benzin	184	250	Jan 1990	Oct 1997	12439
AC	Cobra iv	4.9	Cabriolet	Heckantrieb	Benzin	250	340	Jan 1990	Oct 1997	12442
AC	Cobra iv	4.9 Super Charger	Cabriolet	Heckantrieb	Benzin	239	325	Oct 1997	-	12440
AC	Cobra iv	5.8	Cabriolet	Heckantrieb	Benzin	412	560	Jan 1990	Oct 1997	12443
AC	Cobra iv	6.2	Cabriolet	Heckantrieb	Benzin	325	442	Apr 2009	Jun 2015	20772
AC	Cobra iv	6.2	Cabriolet	Heckantrieb	Benzin	410	558	Apr 2009	Jun 2013	20773
AMC	Eagle	4.2 4WD	Stufenheck	Allrad	Benzin	90	122	Oct 1979	Aug 1985	21981
AMC	Hornet	3.3	Schrägheck	Heckantrieb	Benzin	96	131	Oct 1969	Dec 1970	140546
AMC	Matador	3.8	Kombi	Heckantrieb	Benzin	99	135	Sep 1970	Dec 1974	140545
ARO	10	1.4 AWD	Geländewagen offen	Allrad	Benzin	46	63	Jun 1984	Oct 1999	151161
ARO	240-244	2.5	Geländewagen geschlossen	Allrad	Benzin	59	80	Apr 1978	Dec 1998	11221
ARO	240-244	2.7 D	Geländewagen geschlossen	Allrad	Diesel	50	68	Sep 1989	Dec 1998	11219
ARO	240-244	2.7 D	Geländewagen geschlossen	Allrad	Diesel	52	71	Apr 1985	Dec 1998	11220
ARO	Spartana pick up	1,2 AWD	Geländewagen offen	Allrad	Benzin	40	54	Jan 1997	Dec 2003	127222
Abarth	124	1.4	Cabriolet	Heckantrieb	Benzin	125	170	Mar 2016	-	119512
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	103	140	May 2010	-	58731
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	107	145	May 2016	-	120080
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	118	160	Aug 2008	-	33667
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Jun 2016	-	121446
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	121	165	May 2016	-	120081
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	132	180	Aug 2008	-	1052
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	140	190	Aug 2008	-	1053
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2008	-	28251
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	103	140	Sep 2009	-	1054
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	107	145	May 2016	-	122082
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	118	160	May 2011	-	20872
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	121	165	May 2016	-	121235
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	132	180	Jun 2010	-	59224
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	99	135	May 2008	-	59698
Abarth	500e	Scorpionissima	Cabriolet	Frontantrieb	Elektro	114	155	Feb 2023	-	152403
Abarth	500e	Scorpionissima	Schrägheck	Frontantrieb	Elektro	114	155	Feb 2023	-	152402
Abarth	600e	Scorpionissima	SUV	Frontantrieb	Elektro	207	282	Oct 2024	-	160058
Abarth	600e	Turismo	SUV	Frontantrieb	Elektro	175	238	Oct 2024	-	160053
Abarth	Grande punto	1.4	Schrägheck	Frontantrieb	Benzin	114	155	Jul 2007	Jun 2010	23484
Abarth	Grande punto	1.4 Esseesse / Supersport	Schrägheck	Frontantrieb	Benzin	132	180	May 2008	Jun 2010	33668
Abarth	Punto	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Oct 2009	Feb 2012	129101
Abarth	Punto	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Mar 2012	-	1060
Abarth	Punto	1.4 Supersport	Schrägheck	Frontantrieb	Benzin	132	180	Mar 2012	-	56931
Abarth	Ritmo	125 TC 2.0	Schrägheck	Frontantrieb	Benzin	92	125	Nov 1981	Dec 1987	14518
Abarth	Ritmo	130 TC 2.0	Schrägheck	Frontantrieb	Benzin	96	130	Apr 1983	Dec 1987	2589
Addax	Mt	Mt10 Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	8	11	Jan 2018	-	154955
Addax	Mt	Mt15 Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	9	12	Jan 2018	-	154956
Addax	Mtn	Mt15n Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	12	16	Jan 2020	-	154957
Addax	Mtn	Mt8n Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	12	16	Jan 2023	-	154960
Addax	Mtx	Mt15x Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	12	16	Jan 2023	-	154958
Aeolus	Yixuan	1.5	Stufenheck	Frontantrieb	Benzin	92	125	Aug 2022	-	149025
Aion	Hyptec ht	EV	SUV	Heckantrieb	Elektro	180	245	Dec 2025	-	163182
Aion	V	EV	SUV	Frontantrieb	Elektro	150	204	Sep 2025	-	163649
Aiways	U5	EV	SUV	Frontantrieb	Elektro	150	204	Sep 2020	-	141933
Aiways	U6	EV	SUV	Frontantrieb	Elektro	160	218	Oct 2022	-	150630
Aixam	500	0.5 D	Cabriolet	Frontantrieb	Diesel	10	14	Oct 1996	Jul 2007	132441
Aixam	500	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Dec 1997	Mar 2004	24427
Aixam	A.721	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	24428
Aixam	A.741	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	24429
Aixam	A.751	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Jan 2005	Mar 2010	24430
Aixam	City	0.4	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2012	Dec 2016	100175
Aixam	City	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Oct 2016	-	132955
Aixam	City	Electric	Schrägheck	Frontantrieb	Elektro	4	5	Jan 2012	Dec 2016	106507
Aixam	City	Electric	Schrägheck	Frontantrieb	Elektro	6	8	Mar 2018	-	132970
Aixam	Coupe	0.5	Coupe	Frontantrieb	Diesel	6	8	Oct 2016	-	132961
Aixam	Coupe	Electric	Coupe	Frontantrieb	Elektro	6	8	Mar 2018	-	132976
Aixam	Crossline	0.5	Schrägheck	Frontantrieb	Benzin	15	20	Jan 2012	Dec 2016	12773
Aixam	Crossline	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Oct 2016	-	132963
Aixam	Crossline	0.6	Schrägheck	Frontantrieb	Diesel	11	15	Jan 2012	Dec 2016	127221
Aixam	Crossover	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2018	-	140723
Aixam	Crossover	0.5 GTR	Schrägheck	Frontantrieb	Benzin	15	20	Jan 2012	Dec 2016	118699
Aixam	D-Truck	0.4	Kasten	Frontantrieb	Diesel	4	5	May 2014	-	106509
Aixam	D-Truck	0.4	Pick-up	Frontantrieb	Diesel	4	5	Jan 2012	-	106510
Aixam	D-Truck	0.4	Pritsche/Fahrgestell	Frontantrieb	Diesel	4	5	May 2014	-	106511
Aixam	D-Truck	0.5	Kasten	Frontantrieb	Diesel	6	8	Feb 2018	-	133369
Aixam	D-Truck	0.5	Pritsche/Fahrgestell	Frontantrieb	Diesel	6	8	Feb 2018	-	133370
Aixam	D-Truck	0.6	Kasten	Frontantrieb	Diesel	11	15	May 2015	-	118039
Aixam	D-Truck	0.6	Pick-up	Frontantrieb	Diesel	11	15	May 2015	-	118040
Aixam	D-Truck	0.6	Pritsche/Fahrgestell	Frontantrieb	Diesel	11	15	May 2015	-	118041
Aixam	D-Truck	Electric	Kasten	Frontantrieb	Elektro	6	8	Oct 2024	-	801824
Aixam	D-Truck	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	6	8	Oct 2024	-	801825
Aixam	Mega	0.4 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	4	5	Jan 2007	-	122693
Aixam	Mega	E-scouty	Schrägheck	Frontantrieb	Elektro	6	8	May 2024	-	163905
Aixam	Mega	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	4	5	Jan 2007	Dec 2011	122694
Aixam	Minauto	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Mar 2018	-	133210
Aixam	Minauto	Electric	Schrägheck	Frontantrieb	Elektro	6	8	Oct 2024	-	801819
Aixam	Roadline	0.4	Schrägheck	Frontantrieb	Diesel	4	5	Sep 2009	Jul 2012	140722
Aixam	Roadline	0.6	Schrägheck	Frontantrieb	Diesel	11	15	Sep 2009	Jul 2012	112213
Aixam	Scouty	0.4	Cabriolet	Frontantrieb	Diesel	4	5	Apr 2007	-	100181
Alfa Romeo	145	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1994	Dec 1996	3822
Alfa Romeo	145	1.4 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	76	103	Dec 1996	Jan 2001	7765
Alfa Romeo	145	1.6 16V T.s.	Schrägheck	Frontantrieb	Benzin	82	112	Sep 1997	Dec 2000	54968
Alfa Romeo	145	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	76	103	Oct 1994	Dec 1996	3821
Alfa Romeo	145	1.6 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	88	120	Dec 1996	Jan 2001	7769
Alfa Romeo	145	1.7 I.e. 16V	Schrägheck	Frontantrieb	Benzin	95	129	Oct 1994	Dec 1996	3820
Alfa Romeo	145	1.8 I.e. 16V	Schrägheck	Frontantrieb	Benzin	106	144	Mar 1998	Jan 2001	9503
Alfa Romeo	145	1.8 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	103	140	Dec 1996	Dec 1998	7770

