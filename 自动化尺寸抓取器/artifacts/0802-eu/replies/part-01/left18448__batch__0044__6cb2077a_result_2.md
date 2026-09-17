# 任务：left18448 第 4301-4400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0044__6cb2077a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4301-4400 行

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

## 五、每批执行流程

1. 一次读取当前批全部输入。
2. 按 Make + Model + Generation 候选 + BodyStyle + BodyCode 候选聚类，先消除只由动力和普通配置造成的重复。
3. 查询当前批及历史缓存，批量关联已有尺寸组。已闭合组不得重新打开来源页。
4. 只对缓存未命中的独立物理外廓抓取一次；一个组闭合后立即关联所有适用 Ktype。
5. 最后只处理无组可关联的 `PENDING`。不得按 Ktype 串行重复搜索同一外廓。
6. `PENDING=0` 后停止外部检索，最多执行一次表头、唯一性、引用闭合、非空和链接检查，然后立即 `COMPLETE`。

## 六、输出与终检

### CONTINUE

未完成时仅依次输出：更新点、当前批进度、本轮新增/修改的 Ktype TSV、本轮首次创建/修正的 DIMENSION_GROUP TSV、下一步优先处理，最后一行 `推进信号：CONTINUE`。无变化写“无”；不重复输出未变行或已闭合尺寸组。

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
left18448.tsv

【当前独立任务】
left18448 第 4301-4400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4301-4400_ktype_dimension_mapping_final.tsv
- left18448_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-DAIHATSU-SPARCAR-S70-VAN-01	3195	1395	1885

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Daihatsu	Sparcar	1	Kasten	Heckantrieb	Benzin	Sep 1983	May 1986	14125
Daihatsu	Terios	1.3 4WD	Geländewagen geschlossen	Allrad	Benzin	Oct 1997	Oct 2000	8786
Daihatsu	Terios	1.3 4WD	Geländewagen geschlossen	Allrad	Benzin	Oct 2000	Oct 2005	15551
Daihatsu	Terios	1.5 Vvt-i RWD	Geländewagen geschlossen	Heckantrieb	Benzin	Sep 2010	-	116155
Daihatsu	Yrv	1	Großraumlimousine	Frontantrieb	Benzin	Feb 2001	-	16823
Daihatsu	Yrv	1.3	Großraumlimousine	Frontantrieb	Benzin	Feb 2001	-	15614
Daihatsu	Yrv	1.3 4WD	Großraumlimousine	Allrad	Benzin	Feb 2001	-	15953
Daihatsu	Yrv	1.3 Gtti	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	-	16926
Daimler	Daimler xj	SIX 4.0	Stufenheck	Heckantrieb	Benzin	Jul 1997	Dec 2002	14332
Daimler	Daimler xj	V8 Super 4.0	Stufenheck	Heckantrieb	Benzin	Jul 1997	Jun 2003	14333
DE Lorean	Dmc-12	2.9	Coupe	Heckantrieb	Benzin	Jan 1981	Dec 1983	12685
DE Tomaso	Deauville	5.8	Stufenheck	Heckantrieb	Benzin	Jan 1974	Dec 1978	124160
Deepal	S05	EV	SUV	Heckantrieb	Elektro	Aug 2025	-	162152
Deepal	S05	EV 4WD	SUV	Allrad	Elektro	Sep 2025	-	162788
Deepal	S07	EV	SUV	Heckantrieb	Elektro	Jul 2024	-	159370
Dfsk	580	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2021	-	154488
Dfsk	C31	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	Feb 2018	-	142555
Dfsk	C31	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	Apr 2025	-	802957
Dfsk	C31	1.5 4WD	Pritsche/Fahrgestell	Allrad	Benzin	Feb 2018	-	142556
Dfsk	C32	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	Feb 2018	-	142557
Dfsk	C32	1.5 4WD	Pritsche/Fahrgestell	Allrad	Benzin	Feb 2018	-	142558
Dfsk	C35	1.5	Kasten	Heckantrieb	Benzin	Feb 2018	-	142553
Dfsk	C35	1.5 4WD	Kasten	Allrad	Benzin	Feb 2018	-	142554
Dfsk	E5	1.5 Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	-	160295
Dfsk	E5	1.5 Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	-	160883
Dfsk	Ec75	Electric	Kasten	Frontantrieb	Elektro	Jan 2024	-	160006
Dfsk	Fengon 5	1.5	SUV	Frontantrieb	Benzin	Jan 2020	-	154831
Dfsk	Fengon 5	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Sep 2024	-	801302
Dfsk	Fengon 500	1.5	SUV	Frontantrieb	Benzin	Sep 2021	-	154753
Dfsk	Fengon 500	1.5	SUV	Frontantrieb	Benzin	Nov 2022	-	803185
Dfsk	Fengon 500	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Sep 2021	-	154754
Dfsk	Fengon 500	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2023	-	803186
Dfsk	Fengon 6	GDI	SUV	Frontantrieb	Benzin	Apr 2024	-	159311
Dfsk	Fengon 6	LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2024	-	161905
Dfsk	Fengon 7	2.0 4WD	SUV	Allrad	Benzin	Sep 2021	-	154832
Dfsk	Fengon 7	2.0 LPG 4WD	SUV	Allrad	Benzin/Autogas (LPG)	Sep 2021	-	157582
Dfsk	Forthing 9	1.5 HEV	Großraumlimousine	Frontantrieb	Benzin/Elektro	Oct 2025	-	162784
Dfsk	Glory 600	1.5 GDI	SUV	Frontantrieb	Benzin	Apr 2024	-	159721
Dfsk	K series	1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2011	-	110887
Dfsk	K series	1	Kasten	Heckantrieb	Benzin	Nov 2011	-	110893
Dfsk	K series	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2011	-	110883
Dfsk	K series	1.3	Kasten	Heckantrieb	Benzin	Nov 2011	-	110895
Dfsk	K series	1.2 K01h	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 2020	-	154830
Dfsk	K series	1.3 Allrad	Kasten	Allrad	Benzin	Nov 2011	-	110898
Dfsk	K series	1.3 Allrad	Pritsche/Fahrgestell	Allrad	Benzin	Nov 2011	-	110901
Dfsk	K series	K01he Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2021	-	154834
Dfsk	V	1.3 V21	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2011	-	110909
Dfsk	V	1.3 V21 Allrad	Pritsche/Fahrgestell	Allrad	Benzin	Nov 2011	-	110912
Dfsk	V	1.3 V22	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2011	-	801984
Dfsk	V	1.3 V22 Allrad	Pritsche/Fahrgestell	Allrad	Benzin	Nov 2011	-	801985
Dfsk	V	1.3 V25	Kasten	Heckantrieb	Benzin	Nov 2011	-	110914
Dfsk	V	1.3 V25 Allrad	Kasten	Allrad	Benzin	Nov 2011	-	110918
Dodge	Aspen	5.2	Coupe	Heckantrieb	Benzin	Sep 1975	Dec 1980	38897
Dodge	Avenger	3.6	Stufenheck	Frontantrieb	Benzin	Jan 2012	Dec 2014	55144
Dodge	Caliber	2.4 AWD	Schrägheck	Allrad	Benzin	Oct 2006	-	57238
Dodge	Caravan	2.4	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2007	16440
Dodge	Caravan	3.3	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2007	16436
Dodge	Caravan	3.8	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2007	16438
Dodge	Caravan	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 1995	Jun 2000	143071
Dodge	Caravan	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 1995	Jun 2000	143072
Dodge	Caravan	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	Jan 1995	Mar 2001	16417
Dodge	Caravan	3.3 AWD	Großraumlimousine	Allrad	Benzin	Feb 2000	Dec 2007	16437
Dodge	Caravan	3.3 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16414
Dodge	Caravan	3.8 AWD	Großraumlimousine	Allrad	Benzin	Feb 2000	Dec 2007	16439
Dodge	Caravan	3.8 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16420
Dodge	Caravan	3.8 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16421
Dodge	Caravan	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	16415
Dodge	Caravan	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	16416
Dodge	Challenger	3.5	Coupe	Heckantrieb	Benzin	Sep 2008	Dec 2010	55149
Dodge	Challenger	3.6	Coupe	Heckantrieb	Benzin	Jan 2011	-	55153
Dodge	Challenger	5.7	Coupe	Heckantrieb	Benzin	Sep 2008	Dec 2023	55150
Dodge	Challenger	5.7	Coupe	Heckantrieb	Benzin	Jan 2010	Dec 2023	55152
Dodge	Challenger	6.4	Coupe	Heckantrieb	Benzin	Sep 2014	-	108086
Dodge	Challenger	6.1 Srt8	Coupe	Heckantrieb	Benzin	Sep 2007	-	55151
Dodge	Challenger	6.2 SRT Hellcat	Coupe	Heckantrieb	Benzin	Sep 2014	-	108087
Dodge	Challenger	6.4 Srt8	Coupe	Heckantrieb	Benzin	Jan 2011	-	58481
Dodge	Challenger	6.4 Srt8	Coupe	Heckantrieb	Benzin	Aug 2011	-	59398
Dodge	Charger	3.6	Stufenheck	Heckantrieb	Benzin	Jan 2011	-	55145
Dodge	Charger	3.7	Coupe	Heckantrieb	Benzin	Sep 1969	Dec 1970	113517
Dodge	Charger	5.7 R/T	Stufenheck	Heckantrieb	Benzin	Sep 2010	-	55146
Dodge	Charger	5.7 R/T AWD	Stufenheck	Allrad	Benzin	Sep 2010	-	55147
Dodge	Charger	6.2 SRT Hellcat	Stufenheck	Heckantrieb	Benzin	Sep 2014	-	112983
Dodge	Charger	6.2 SRT Hellcat Redeye	Stufenheck	Heckantrieb	Benzin	Sep 2020	-	144308
Dodge	Charger	6.4 Srt8	Stufenheck	Heckantrieb	Benzin	Sep 2011	-	55148
Dodge	Charger	6.4 Srt8	Stufenheck	Heckantrieb	Benzin	Sep 2014	-	112982
Dodge	Durango	3.6	SUV	Heckantrieb	Benzin	Jan 2011	-	55161
Dodge	Durango	4.7	SUV	Heckantrieb	Benzin	Sep 1997	Dec 2003	39587
Dodge	Durango	5.2	SUV	Heckantrieb	Benzin	Sep 1998	Dec 2000	39585
Dodge	Durango	5.7	SUV	Heckantrieb	Benzin	Jan 2011	-	55163
Dodge	Durango	3.6 AWD	SUV	Allrad	Benzin	Jan 2011	-	55162
Dodge	Durango	4.7 4WD	SUV	Allrad	Benzin	Sep 1997	Dec 2003	39588
Dodge	Durango	5.2 4WD	SUV	Allrad	Benzin	Dec 1997	Dec 2000	57802
Dodge	Durango	5.7 AWD	SUV	Allrad	Benzin	Jan 2011	-	55164
Dodge	Durango	6.2 SRT Hellcat	SUV	Allrad	Benzin	Sep 2020	-	144310
Dodge	Grand caravan	3.6	Großraumlimousine	Frontantrieb	Benzin	Sep 2010	-	59500
Dodge	Journey	2.4	Großraumlimousine	Frontantrieb	Benzin	Sep 2008	-	55168
Dodge	Journey	3.6	Großraumlimousine	Frontantrieb	Benzin	Jun 2012	Dec 2015	55156
Dodge	Journey	3.6	Großraumlimousine	Frontantrieb	Benzin	Jan 2012	-	55169
Dodge	Journey	2.0 CRD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2008	Dec 2011	143073
Dodge	Journey	2.4 VVT	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jan 2009	Dec 2012	143074


--- Round 1 / 首次发送 ---
## 更新点

已完成当前批次聚类、尺寸组复用和必要的物理分支拆分。Challenger、Charger、Durango 与 Journey 仅在量产三维确有变化的阶段拆分；发动机、能源和驱动形式未改变外廓的记录均复用同一尺寸组。([汽车数据][1])

## 进度

100/100 个输入 Ktype 已覆盖；最终包含 **120 条映射记录、52 个尺寸组、PENDING=0**。固定表头、唯一性、尺寸组引用闭合、正整数三维、来源非空及指定文件名均已通过机械终检。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14125	14125	Van	S70	S70		EU-DAIHATSU-SPARCAR-S70-VAN-01	HIGH		READY
8786	8786	SUV	Terios I	J100	5	EU-DAIHATSU-TERIOS-J100-SUV-01	HIGH		READY
15551	15551	SUV	Terios I	J100	5	EU-DAIHATSU-TERIOS-J100-SUV-01	HIGH		READY
116155	116155	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-J200-SUV-RWD-01	HIGH		READY
16823	16823	MPV	YRV	M200	5	EU-DAIHATSU-YRV-M200-MPV-01	HIGH		READY
15614	15614	MPV	YRV	M200	5	EU-DAIHATSU-YRV-M200-MPV-01	HIGH		READY
15953	15953	MPV	YRV	M200	5	EU-DAIHATSU-YRV-M200-MPV-01	HIGH		READY
16926	16926	MPV	YRV	M200	5	EU-DAIHATSU-YRV-M200-MPV-01	HIGH		READY
14332	14332	Sedan	X300	X300	4	EU-DAIMLER-XJ-X300-SEDAN-SIX-01	MEDIUM	Variant name SIX mapped to the X300 standard-wheelbase body.	READY
14333	14333	Sedan	X308	X308	4	EU-DAIMLER-XJ-X308-SEDAN-SUPER-V8-01	HIGH		READY
12685	12685	Coupe	DMC-12		2	EU-DELOREAN-DMC12-COUPE-01	HIGH		READY
124160	124160	Sedan	Deauville Series I		4	EU-DETOMASO-DEAUVILLE-SERIES1-SEDAN-01	MEDIUM		READY
162152	162152	SUV	S05 I		5	EU-DEEPAL-S05-1-SUV-01	HIGH		READY
162788	162788	SUV	S05 I		5	EU-DEEPAL-S05-1-SUV-01	HIGH		READY
159370	159370	SUV	S07 I		5	EU-DEEPAL-S07-1-SUV-01	HIGH		READY
154488	154488	SUV	580 I		5	EU-DFSK-580-1-SUV-01	HIGH		READY
142555	142555	Pickup	C31 I	C31	2	EU-DFSK-C31-1-PICKUP-01	HIGH		READY
802957	802957	Pickup	C31 I	C31	2	EU-DFSK-C31-1-PICKUP-01	HIGH		READY
142556	142556	Pickup	C31 I	C31	2	EU-DFSK-C31-1-PICKUP-01	HIGH		READY
142557	142557	Pickup	C32 I	C32	4	EU-DFSK-C32-1-PICKUP-01	HIGH		READY
142558	142558	Pickup	C32 I	C32	4	EU-DFSK-C32-1-PICKUP-01	HIGH		READY
142553	142553	Van	C35 I	C35	5	EU-DFSK-C35-1-VAN-01	HIGH		READY
142554	142554	Van	C35 I	C35	5	EU-DFSK-C35-1-VAN-01	HIGH		READY
160295	160295	SUV	E5 I		5	EU-DFSK-E5-1-SUV-01	HIGH		READY
160883	160883	SUV	E5 I		5	EU-DFSK-E5-1-SUV-01	HIGH		READY
160006	160006	Van	EC75 I	EC75	5	EU-DFSK-EC75-1-VAN-01	HIGH		READY
154831	154831	SUV	Fengon 5 I		5	EU-DFSK-FENGON5-1-SUV-01	HIGH		READY
801302	801302	SUV	Fengon 5 I		5	EU-DFSK-FENGON5-1-SUV-01	HIGH		READY
154753	154753	SUV	Fengon 500 I		5	EU-DFSK-FENGON500-1-SUV-01	HIGH		READY
803185	803185	SUV	Fengon 500 I		5	EU-DFSK-FENGON500-1-SUV-01	HIGH		READY
154754	154754	SUV	Fengon 500 I		5	EU-DFSK-FENGON500-1-SUV-01	HIGH		READY
803186	803186	SUV	Fengon 500 I		5	EU-DFSK-FENGON500-1-SUV-01	HIGH		READY
159311	159311	SUV	Fengon 6 / Glory 600 I		5	EU-DFSK-FENGON6-1-SUV-01	HIGH		READY
161905	161905	SUV	Fengon 6 / Glory 600 I		5	EU-DFSK-FENGON6-1-SUV-01	HIGH		READY
154832	154832	SUV	Fengon 7 I		5	EU-DFSK-FENGON7-1-SUV-01	HIGH		READY
157582	157582	SUV	Fengon 7 I		5	EU-DFSK-FENGON7-1-SUV-01	HIGH		READY
162784	162784	MPV	Forthing 9 / V9 I		5	EU-DFSK-FORTHING9-1-MPV-01	HIGH		READY
159721	159721	SUV	Fengon 6 / Glory 600 I		5	EU-DFSK-FENGON6-1-SUV-01	HIGH		READY
110887	110887	Pickup	K-Series I	K01	2	EU-DFSK-KSERIES-K01-PICKUP-01	MEDIUM		READY
110893	110893	Van	K-Series I	K05/K07	5	EU-DFSK-KSERIES-K05-VAN-01	MEDIUM		READY
110883	110883	Pickup	K-Series I	K01	2	EU-DFSK-KSERIES-K01-PICKUP-01	MEDIUM		READY
110895	110895	Van	K-Series I	K05/K07	5	EU-DFSK-KSERIES-K05-VAN-01	MEDIUM		READY
154830	154830	Pickup	K-Series II	K01H	2	EU-DFSK-KSERIES-K01H-PICKUP-01	MEDIUM		READY
110898	110898	Van	K-Series I	K05/K07	5	EU-DFSK-KSERIES-K05-VAN-01	MEDIUM		READY
110901	110901	Pickup	K-Series I	K01	2	EU-DFSK-KSERIES-K01-PICKUP-01	MEDIUM		READY
154834	154834	Pickup	K-Series electric	K01HE	2	EU-DFSK-KSERIES-K01HE-PICKUP-01	MEDIUM		READY
110909	110909	Pickup	V-Series	V21	2	EU-DFSK-VSERIES-V21-PICKUP-01	MEDIUM		READY
110912	110912	Pickup	V-Series	V21	2	EU-DFSK-VSERIES-V21-PICKUP-01	MEDIUM		READY
801984	801984	Pickup	V-Series	V22	4	EU-DFSK-VSERIES-V22-PICKUP-01	MEDIUM		READY
801985	801985	Pickup	V-Series	V22	4	EU-DFSK-VSERIES-V22-PICKUP-01	MEDIUM		READY
110914	110914	Van	V-Series	V25	5	EU-DFSK-VSERIES-V25-VAN-01	MEDIUM		READY
110918	110918	Van	V-Series	V25	5	EU-DFSK-VSERIES-V25-VAN-01	MEDIUM		READY
38897	38897	Coupe	Aspen	F	2	EU-DODGE-ASPEN-F-COUPE-01	HIGH		READY
55144	55144	Sedan	Avenger facelift	JS	4	EU-DODGE-AVENGER-JS-FACELIFT-SEDAN-01	HIGH		READY
57238	57238	Hatchback	Caliber	PM	5	EU-DODGE-CALIBER-PM-HATCHBACK-AWD-01	HIGH		READY
16440	16440	MPV	Caravan IV SWB	RS	4	EU-DODGE-CARAVAN-RS-MPV-SWB-01	HIGH		READY
16436	16436	MPV	Caravan IV SWB	RS	4	EU-DODGE-CARAVAN-RS-MPV-SWB-01	HIGH		READY
16438	16438	MPV	Caravan IV SWB	RS	4	EU-DODGE-CARAVAN-RS-MPV-SWB-01	HIGH		READY
143071	143071	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH	Kasten/Großraumlimousine entries use the same production SWB minivan exterior.	READY
143072	143072	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH	Kasten/Großraumlimousine entries use the same production SWB minivan exterior.	READY
16417	16417	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
16437	16437	MPV	Caravan IV SWB	RS	4	EU-DODGE-CARAVAN-RS-MPV-SWB-01	HIGH		READY
16414	16414	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
16439	16439	MPV	Caravan IV SWB	RS	4	EU-DODGE-CARAVAN-RS-MPV-SWB-01	HIGH		READY
16420	16420	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
16421	16421	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
16415	16415	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
16416	16416	MPV	Caravan III SWB	NS	4	EU-DODGE-CARAVAN-NS-MPV-SWB-01	HIGH		READY
55149	55149	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH		READY
55153_prefl	55153	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH	2011-2014 standard body before the dimensional facelift.	READY
55153_facelift	55153	Coupe	Challenger III facelift	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-FACELIFT-01	HIGH	2014-2023 standard body after the dimensional facelift.	READY
55150_prefl	55150	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH	Pre-facelift standard body.	READY
55150_facelift	55150	Coupe	Challenger III facelift	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-FACELIFT-01	HIGH	Facelift standard body.	READY
55152_prefl	55152	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH	Pre-facelift standard body.	READY
55152_facelift	55152	Coupe	Challenger III facelift	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-FACELIFT-01	HIGH	Facelift standard body.	READY
108086	108086	Coupe	Challenger III facelift	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-FACELIFT-01	HIGH		READY
55151	55151	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH		READY
108087	108087	Coupe	Challenger III facelift	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-HELLCAT-01	MEDIUM	Generic Hellcat entry mapped to the standard-width factory body; no widebody branch asserted.	READY
58481	58481	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH		READY
59398	59398	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	HIGH		READY
55145_prefl	55145	Sedan	Charger VII	LD	4	EU-DODGE-CHARGER-LD-SEDAN-PREFL-01	HIGH	2011-2014 body.	READY
55145_facelift	55145	Sedan	Charger VII facelift 2015	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-01	HIGH	2015-2018 body.	READY
55145_facelift2019	55145	Sedan	Charger VII facelift 2019	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT2019-01	HIGH	2019-2023 standard-width body.	READY
113517	113517	Coupe	Charger II	B	2	EU-DODGE-CHARGER-B-COUPE-01	HIGH		READY
55146_prefl	55146	Sedan	Charger VII	LD	4	EU-DODGE-CHARGER-LD-SEDAN-PREFL-01	HIGH	2011-2014 body.	READY
55146_facelift	55146	Sedan	Charger VII facelift 2015	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-01	HIGH	2015-2018 body.	READY
55146_facelift2019	55146	Sedan	Charger VII facelift 2019	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT2019-01	HIGH	2019-2023 standard-width body.	READY
55147_prefl	55147	Sedan	Charger VII	LD	4	EU-DODGE-CHARGER-LD-SEDAN-PREFL-01	HIGH	2011-2014 body.	READY
55147_facelift	55147	Sedan	Charger VII facelift 2015	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-01	HIGH	2015-2018 body.	READY
55147_facelift2019	55147	Sedan	Charger VII facelift 2019	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT2019-01	HIGH	2019-2023 standard-width body.	READY
112983_narrow	112983	Sedan	Charger VII facelift 2015	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-SRT-01	HIGH	2015-2019 Hellcat standard-width body.	READY
112983_widebody	112983	Sedan	Charger VII facelift 2019	LD	4	EU-DODGE-CHARGER-LD-SEDAN-WIDEBODY-01	HIGH	2020-2023 Hellcat factory widebody.	READY
144308	144308	Sedan	Charger VII facelift 2019	LD	4	EU-DODGE-CHARGER-LD-SEDAN-WIDEBODY-01	HIGH		READY
55148	55148	Sedan	Charger VII	LD	4	EU-DODGE-CHARGER-LD-SEDAN-PREFL-SRT-01	HIGH		READY
112982	112982	Sedan	Charger VII facelift 2015	LD	4	EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-SRT-01	HIGH		READY
55161_prefl	55161	SUV	Durango III	WD	5	EU-DODGE-DURANGO-WD-SUV-PREFL-01	HIGH	2011-2013 body.	READY
55161_facelift	55161	SUV	Durango III facelift 2014	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT-01	HIGH	2014-2020 body.	READY
55161_facelift2021	55161	SUV	Durango III facelift 2021	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-RWD-01	HIGH	2021-on RWD body.	READY
39587	39587	SUV	Durango I	DN	5	EU-DODGE-DURANGO-DN-SUV-01	HIGH		READY
39585	39585	SUV	Durango I	DN	5	EU-DODGE-DURANGO-DN-SUV-01	HIGH		READY
55163_prefl	55163	SUV	Durango III	WD	5	EU-DODGE-DURANGO-WD-SUV-PREFL-01	HIGH	2011-2013 body.	READY
55163_facelift	55163	SUV	Durango III facelift 2014	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT-01	HIGH	2014-2020 body.	READY
55163_facelift2021	55163	SUV	Durango III facelift 2021	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-RWD-01	HIGH	2021-on RWD body.	READY
55162_prefl	55162	SUV	Durango III	WD	5	EU-DODGE-DURANGO-WD-SUV-PREFL-01	HIGH	2011-2013 body.	READY
55162_facelift	55162	SUV	Durango III facelift 2014	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT-01	HIGH	2014-2020 body.	READY
55162_facelift2021	55162	SUV	Durango III facelift 2021	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-AWD-01	HIGH	2021-on AWD body.	READY
39588	39588	SUV	Durango I	DN	5	EU-DODGE-DURANGO-DN-SUV-01	HIGH		READY
57802	57802	SUV	Durango I	DN	5	EU-DODGE-DURANGO-DN-SUV-01	HIGH		READY
55164_prefl	55164	SUV	Durango III	WD	5	EU-DODGE-DURANGO-WD-SUV-PREFL-01	HIGH	2011-2013 body.	READY
55164_facelift	55164	SUV	Durango III facelift 2014	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT-01	HIGH	2014-2020 body.	READY
55164_facelift2021	55164	SUV	Durango III facelift 2021	WD	5	EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-AWD-01	HIGH	2021-on AWD body.	READY
144310	144310	SUV	Durango III facelift 2021	WD	5	EU-DODGE-DURANGO-WD-SUV-HELLCAT-01	HIGH		READY
59500	59500	MPV	Grand Caravan V facelift	RT	5	EU-DODGE-GRANDCARAVAN-RT-MPV-FACELIFT-01	HIGH		READY
55168_prefl	55168	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-JC-MPV-PREFL-01	HIGH	2008-2010 pre-facelift body.	READY
55168_facelift	55168	MPV	Journey I facelift	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH	2010-on facelift body.	READY
55156	55156	MPV	Journey I facelift	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH		READY
55169	55169	MPV	Journey I facelift	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH		READY
143073	143073	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-JC-MPV-PREFL-01	HIGH	Kasten/Großraumlimousine mapped to the same production crossover-MPV exterior.	READY
143074_prefl	143074	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-JC-MPV-PREFL-01	HIGH	2009-2010 pre-facelift body.	READY
143074_facelift	143074	MPV	Journey I facelift	JC	5	EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	HIGH	2010-2012 facelift body.	READY
```

[下载 left18448_4301-4400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_4301-4400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-SPARCAR-S70-VAN-01	3195	1395	1885	Cross-batch closed group; CarsGuide 1984 Daihatsu Hi-Jet dimensions table	https://www.carsguide.com.au/daihatsu/hi-jet/car-dimensions/1984
EU-DAIHATSU-TERIOS-J100-SUV-01	3845	1555	1695	Auto-Data: Daihatsu Terios I (J100) 1.3 4WD	https://www.auto-data.net/en/daihatsu-terios-i-j100-1.3-i-16v-4wd-86hp-43
EU-DAIHATSU-TERIOS-J200-SUV-RWD-01	4055	1695	1740	Auto-Data: Daihatsu Terios II (J200) 1.5 RWD	https://www.auto-data.net/en/daihatsu-terios-ii-j200-1.5-i-16v-105hp-41
EU-DAIHATSU-YRV-M200-MPV-01	3765	1625	1550	Auto-Data: Daihatsu YRV 1.3 Turbo	https://www.auto-data.net/en/daihatsu-yrv-1.3-i-16v-turbo-140hp-120
EU-DAIMLER-XJ-X300-SEDAN-SIX-01	5024	1799	1314	Automobile-Catalog: Daimler Six 4.0	https://www.automobile-catalog.com/car/1995/1285715/daimler_six.html
EU-DAIMLER-XJ-X308-SEDAN-SUPER-V8-01	5148	1798	1380	Auto-Data: Daimler 4.0 V8 Super	https://www.auto-data.net/en/daimler-daimler-x300-4.0-i-v8-32v-super-363hp-1113
EU-DELOREAN-DMC12-COUPE-01	4267	1989	1140	Automobile-Catalog: 1982 De Lorean DMC-12; width without mirrors	https://www.automobile-catalog.com/car/1982/587540/de_lorean_dmc-12.html
EU-DETOMASO-DEAUVILLE-SERIES1-SEDAN-01	4851	1880	1372	Carfolio: De Tomaso Deauville	https://www.carfolio.com/de-tomaso-deauville-46475
EU-DEEPAL-S05-1-SUV-01	4620	1900	1600	Changan Singapore official: Deepal S05 specifications	https://www.changan.sg/s05/
EU-DEEPAL-S07-1-SUV-01	4750	1930	1625	Changan Europe official: Deepal S07 specifications	https://www.changaneurope.com/gr/en/Models/Changan-Deepal-S07/Specifications
EU-DFSK-580-1-SUV-01	4680	1845	1715	Auto-Data: DFSK 580 generation	https://www.auto-data.net/en/dfsk-580-generation-8609
EU-DFSK-C31-1-PICKUP-01	4730	1655	1890	DFSK Morocco official: C31 specifications	https://www.dfsk.ma/v%C3%A9hicules/c31
EU-DFSK-C32-1-PICKUP-01	4940	1655	1910	DFSK Tunisia: C32 specifications	https://dfsk.tn/dfsk-c32/
EU-DFSK-C35-1-VAN-01	4500	1680	2000	DFSK Morocco official: C35 specifications	https://www.dfsk.ma/ar/node/20
EU-DFSK-E5-1-SUV-01	4760	1865	1710	Auto-Data: DFSK E5 generation	https://www.auto-data.net/en/dfsk-e5-generation-11038
EU-DFSK-EC75-1-VAN-01	5130	1860	2020	DFSK Sweden official: EC75 specifications	https://dfsksweden.com/products/dfsk-ec75/
EU-DFSK-FENGON5-1-SUV-01	4685	1865	1645	Auto-Data: DFSK F5/Fengon 5 generation	https://www.auto-data.net/en/dfsk-f5-generation-8605
EU-DFSK-FENGON500-1-SUV-01	4385	1850	1645	DFSK Estonia official distributor: DFSK 500 specifications	https://dfskestonia.com/products/dfsk-500/
EU-DFSK-FENGON6-1-SUV-01	4720	1865	1710	DFSK Sweden official: DFSK 600 specifications	https://dfsksweden.com/products/dfsk-600/
EU-DFSK-FENGON7-1-SUV-01	4930	1935	1765	ADAC vehicle catalogue: DFSK Fengon 7	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/dfsk/fengon-7/1generation/345123/
EU-DFSK-FORTHING9-1-MPV-01	5251	1920	1820	Forthing official: V9/Forthing 9 specifications	https://www.forthingmotor.com/v9-product/
EU-DFSK-KSERIES-K01-PICKUP-01	3960	1560	1825	DFSK Motor product specification: K01 mini truck	https://www.dfsk-motor.com/truck/mini-truck/dfsk-k01-mini-truck-2-seater.html
EU-DFSK-KSERIES-K05-VAN-01	3795	1560	1925	DFSK specification sheet: K05/K07 van	https://dfsk.motordeal.co.za/wp-content/uploads/2012/10/dfsk.pdf
EU-DFSK-KSERIES-K01H-PICKUP-01	4035	1560	1825	DFSK Morocco official: K01H specifications	https://www.dfsk.ma/ar/node/22
EU-DFSK-KSERIES-K01HE-PICKUP-01	4280	1560	1825	Autocasion specification: DFSK K01HE electric pickup	https://www.autocasion.com/marcas/dfsk/serie-k-industrial/serie-k-pick-up-k01he-2-puertas-74118
EU-DFSK-VSERIES-V21-PICKUP-01	4625	1635	1890	RIM3 commercial catalogue: DFSK V21 single-cab	https://rim3.ru/comauto/catalog/dongfeng/
EU-DFSK-VSERIES-V22-PICKUP-01	4640	1635	1920	RIM3 commercial catalogue: DFSK V22 double-cab	https://rim3.ru/comauto/catalog/dongfeng/
EU-DFSK-VSERIES-V25-VAN-01	3905	1634	1960	RIM3 commercial catalogue: DFSK V25 van	https://rim3.ru/comauto/catalog/dongfeng/
EU-DODGE-ASPEN-F-COUPE-01	5016	1849	1349	Automobile-Catalog: 1976 Dodge Aspen R/T Coupe 318 V8	https://www.automobile-catalog.com/car/1976/661805/dodge_aspen_rt_coupe_318_v-8.html
EU-DODGE-AVENGER-JS-FACELIFT-SEDAN-01	4892	1850	1483	Auto-Data: Dodge Avenger facelift 3.6	https://www.auto-data.net/en/dodge-avenger-sedan-facelift-2010-3.6-v6-283hp-autostick-51164
EU-DODGE-CALIBER-PM-HATCHBACK-AWD-01	4415	1800	1535	CarsGuide: 2007 Dodge Caliber R/T 2.4 dimensions	https://www.carsguide.com.au/dodge/caliber/car-dimensions/2007
EU-DODGE-CARAVAN-RS-MPV-SWB-01	4803	1996	1750	Auto-Data: Dodge Caravan IV SWB generation	https://www.auto-data.net/en/dodge-caravan-iv-swb-generation-690
EU-DODGE-CARAVAN-NS-MPV-SWB-01	4733	1920	1740	Auto-Data: Dodge Caravan III SWB generation	https://www.auto-data.net/en/dodge-caravan-iii-swb-generation-691
EU-DODGE-CHALLENGER-LC-COUPE-PREFL-01	5023	1923	1449	Auto-Data: Dodge Challenger III 3.6/5.7 standard body	https://www.auto-data.net/en/dodge-challenger-iii-3.6-pentastar-v6-305hp-automatic-46099
EU-DODGE-CHALLENGER-LC-COUPE-FACELIFT-01	5027	1923	1460	Auto-Data: Dodge Challenger III facelift R/T 5.7	https://www.auto-data.net/en/dodge-challenger-iii-facelift-2014-r-t-5.7-hemi-v8-375hp-32893
EU-DODGE-CHALLENGER-LC-COUPE-HELLCAT-01	5018	1923	1454	Automobile-Catalog: 2019 Challenger Hellcat Redeye standard body; width without mirrors	https://www.automobile-catalog.com/car/2019/2760260/dodge_challenger_srt_hellcat_redeye.html
EU-DODGE-CHARGER-LD-SEDAN-PREFL-01	5077	1905	1482	Auto-Data: Dodge Charger VII LD SE 3.6	https://www.auto-data.net/en/dodge-charger-vii-ld-se-3.6-296hp-automatic-2884
EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-01	5040	1905	1479	Auto-Data: Dodge Charger VII facelift 2015 SE 3.6	https://www.auto-data.net/en/dodge-charger-vii-ld-facelift-2015-se-3.6-pentastar-v6-292hp-automatic-35143
EU-DODGE-CHARGER-LD-SEDAN-FACELIFT2019-01	5040	1905	1467	Auto-Data: Dodge Charger VII facelift 2019 SXT 3.6	https://www.auto-data.net/en/dodge-charger-vii-ld-facelift-2019-sxt-3.6-pentastar-v6-292hp-automatic-38967
EU-DODGE-CHARGER-B-COUPE-01	5283	1946	1351	1969 Dodge Charger factory brochure specifications	https://xr793.com/wp-content/uploads/2017/01/1969-Dodge-Charger.pdf
EU-DODGE-CHARGER-LD-SEDAN-FACELIFT-SRT-01	5100	1905	1480	Auto-Data: Dodge Charger VII facelift 2015 SRT Hellcat	https://www.auto-data.net/en/dodge-charger-vii-ld-facelift-2015-srt-hellcat-6.2-hemi-v8-707hp-automatic-35140
EU-DODGE-CHARGER-LD-SEDAN-WIDEBODY-01	5105	1989	1462	Auto-Data: Dodge Charger Hellcat Redeye Widebody	https://www.auto-data.net/en/dodge-charger-vii-ld-facelift-2019-srt-hellcat-redeye-6.2-v8-797hp-widebody-automatic-45690
EU-DODGE-CHARGER-LD-SEDAN-PREFL-SRT-01	5088	1886	1480	Auto-Data: Dodge Charger VII LD SRT8 6.4	https://www.auto-data.net/en/dodge-charger-vii-ld-srt8-6.4-477hp-automatic-35125
EU-DODGE-DURANGO-WD-SUV-PREFL-01	5075	1925	1801	Auto-Data: Dodge Durango III WD 3.6	https://www.auto-data.net/en/dodge-durango-iii-wd-3.6-v6-290hp-36153
EU-DODGE-DURANGO-WD-SUV-FACELIFT-01	5110	1925	1801	Auto-Data: Dodge Durango III facelift 2014 3.6	https://www.auto-data.net/en/dodge-durango-iii-wd-facelift-2014-3.6-v6-293hp-36202
EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-RWD-01	5101	1924	1831	Auto-Data: Dodge Durango facelift 2021 3.6 RWD	https://www.auto-data.net/en/dodge-durango-iii-wd-facelift-2021-3.6-pentastar-v6-295hp-torqueflite-43651
EU-DODGE-DURANGO-DN-SUV-01	4910	1810	1804	Auto-Data: Dodge Durango I DN 5.2 AWD	https://www.auto-data.net/en/dodge-durango-i-dn-5.2-awd-236hp-3015
EU-DODGE-DURANGO-WD-SUV-FACELIFT2021-AWD-01	5101	1924	1851	Auto-Data: Dodge Durango facelift 2021 3.6 AWD	https://www.auto-data.net/en/dodge-durango-iii-wd-facelift-2021-3.6-pentastar-v6-295hp-awd-torqueflite-43654
EU-DODGE-DURANGO-WD-SUV-HELLCAT-01	5104	1940	1831	Auto-Data: Dodge Durango facelift 2021 Hellcat	https://www.auto-data.net/en/dodge-durango-iii-wd-facelift-2021-hellcat-6.2-hemi-v8-710hp-awd-torqueflite-43657
EU-DODGE-GRANDCARAVAN-RT-MPV-FACELIFT-01	5151	1998	1725	Auto-Data: Dodge Caravan V facelift 2011 3.6	https://www.auto-data.net/en/dodge-caravan-v-facelift-2011-3.6-v6-287hp-automatic-30987
EU-DODGE-JOURNEY-JC-MPV-PREFL-01	4888	1878	1691	Auto-Data: Dodge Journey 2.4 pre-facelift	https://www.auto-data.net/en/dodge-journey-2.4-i-16v-170hp-2928
EU-DODGE-JOURNEY-JC-MPV-FACELIFT-01	4887	1834	1692	Auto-Data: Dodge Journey facelift 2010 2.4	https://www.auto-data.net/en/dodge-journey-facelift-2010-2.4-173hp-automatic-47968
```

[下载 left18448_4301-4400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_4301-4400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/dodge-challenger-iii-facelift-2014-r-t-5.7-hemi-v8-375hp-32893 "https://www.auto-data.net/en/dodge-challenger-iii-facelift-2014-r-t-5.7-hemi-v8-375hp-32893"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5136 行）
- 累计尺寸组：dimension_groups_final.tsv（1471 行）

