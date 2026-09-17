# 任务：left18448 第 15101-15200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0152__577e10e8


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15101-15200 行

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
left18448 第 15101-15200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15101-15200_ktype_dimension_mapping_final.tsv
- left18448_15101-15200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	4439	1742	1436
EU-SEAT-TOLEDO-III-MPV-STANDARD-01	4458	1768	1568
EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	4482	1706	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Seat	Toledo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	May 2017	115145
Seat	Toledo	1.4 16V	Stufenheck	Frontantrieb	Benzin	Jan 2000	May 2002	14571
Seat	Toledo	1.4 16V	Großraumlimousine	Frontantrieb	Benzin	May 2006	May 2009	100020
Seat	Toledo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Apr 2019	115149
Seat	Toledo	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	57525
Seat	Toledo	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Apr 2019	115146
Seat	Toledo	1.6 16V	Stufenheck	Frontantrieb	Benzin	Jun 2000	May 2006	15802
Seat	Toledo	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2012	Jun 2015	57526
Seat	Toledo	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Jun 2013	Jun 2015	100023
Seat	Toledo	1.6 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Apr 2019	115151
Seat	Toledo	1.8 20V	Stufenheck	Frontantrieb	Benzin	Oct 1998	Jul 2004	10047
Seat	Toledo	1.8 20vt	Stufenheck	Frontantrieb	Benzin	Sep 2000	Jul 2004	17926
Seat	Toledo	1.9 D	Schrägheck	Frontantrieb	Diesel	Dec 1995	Mar 1999	8095
Seat	Toledo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Mar 1999	Jul 2004	10049
Seat	Toledo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 1998	Jul 2004	10050
Seat	Toledo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 2000	Jul 2004	16180
Seat	Toledo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	May 2003	May 2006	17514
Seat	Toledo	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Oct 2004	May 2009	18382
Seat	Toledo	2.0 FSI	Großraumlimousine	Frontantrieb	Benzin	Oct 2004	May 2009	18381
Seat	Toledo	2.0 TDI 16V	Großraumlimousine	Frontantrieb	Diesel	Apr 2004	May 2009	18383
Seat	Toledo	2.3 V5	Stufenheck	Frontantrieb	Benzin	Oct 1998	Nov 2000	10048
Seat	Toledo	2.3 V5 20V	Stufenheck	Frontantrieb	Benzin	Sep 2000	Nov 2003	16071
Seres	3	Electric	SUV	Frontantrieb	Elektro	Dec 2020	-	145624
Seres	5	BEV Allrad	SUV	Allrad	Elektro	Jun 2023	-	155099
Seres	5	EV Allrad	SUV	Allrad	Elektro	Jun 2023	-	155102
Seres	5	EV AWD	SUV	Allrad	Elektro	Feb 2026	-	802902
Seres	5	EV Heckantrieb	SUV	Heckantrieb	Elektro	Feb 2026	-	802901
Seres	5	EVR Allrad	SUV	Allrad	Benzin/Elektro	Jun 2023	-	155101
Sevic	S70	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2020	-	144608
Sevic	V500	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2020	-	144229
Shineray	X30	EV	Kasten	Heckantrieb	Elektro	May 2023	-	154972
Silence	S04	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160367
Silence	S04	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160372
Silence	S04	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160375
Silence	S04	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160376
Skoda	105120	1.2 120 L	Stufenheck	Heckantrieb	Benzin	Aug 1987	Dec 1990	5070
Skoda	Citigo	1	Schrägheck	Frontantrieb	Benzin	Oct 2011	Aug 2019	15989
Skoda	Citigo	1	Schrägheck	Frontantrieb	Benzin	Oct 2011	Aug 2019	15995
Skoda	Citigo	1.0 CNG	Schrägheck	Frontantrieb	CNG	Nov 2012	Aug 2019	58802
Skoda	Elroq	50	SUV	Heckantrieb	Elektro	Nov 2024	-	159345
Skoda	Elroq	60	SUV	Heckantrieb	Elektro	Nov 2024	-	159346
Skoda	Elroq	85	SUV	Heckantrieb	Elektro	Nov 2024	-	159344
Skoda	Elroq	85X 4motion	SUV	Allrad	Elektro	Nov 2024	-	159347
Skoda	Elroq	RS 4motion	SUV	Allrad	Elektro	Apr 2025	-	161794
Skoda	Enyaq iv	50	SUV	Heckantrieb	Elektro	Jul 2024	-	800212
Skoda	Enyaq iv	60	SUV	Heckantrieb	Elektro	Jan 2025	-	801922
Skoda	Enyaq iv	85	SUV	Heckantrieb	Elektro	Oct 2023	-	156287
Skoda	Enyaq iv	80X 4X4	SUV	Allrad	Elektro	Oct 2021	-	145613
Skoda	Enyaq iv	85X	SUV	Allrad	Elektro	Oct 2023	-	156288
Skoda	Enyaq iv	RS	SUV	Allrad	Elektro	Jul 2023	-	155565
Skoda	Enyaq iv	RS	SUV	Allrad	Elektro	Oct 2023	-	156807
Skoda	Enyaq iv coupe	60	SUV	Heckantrieb	Elektro	Jul 2021	-	147493
Skoda	Enyaq iv coupe	60	SUV	Heckantrieb	Elektro	Jan 2025	-	801923
Skoda	Enyaq iv coupe	80	SUV	Heckantrieb	Elektro	Jul 2021	-	147494
Skoda	Enyaq iv coupe	85	SUV	Heckantrieb	Elektro	Oct 2023	-	156516
Skoda	Enyaq iv coupe	80X 4X4	SUV	Allrad	Elektro	Jul 2021	-	147495
Skoda	Enyaq iv coupe	85X Allrad	SUV	Allrad	Elektro	Oct 2023	-	156517
Skoda	Enyaq iv coupe	RS	SUV	Allrad	Elektro	Jul 2021	-	146691
Skoda	Enyaq iv coupe	RS	SUV	Allrad	Elektro	Oct 2021	-	156809
Skoda	Fabia i	1	Schrägheck	Frontantrieb	Benzin	Dec 1999	Aug 2002	14277
Skoda	Fabia i	1.2	Schrägheck	Frontantrieb	Benzin	Jul 2001	Apr 2007	16944
Skoda	Fabia i	1.2	Schrägheck	Frontantrieb	Benzin	Jan 2003	Mar 2008	17393
Skoda	Fabia i	1.2	Stufenheck	Frontantrieb	Benzin	Jan 2003	Dec 2007	17394
Skoda	Fabia i	1.2	Stufenheck	Frontantrieb	Benzin	Jul 2001	Dec 2007	18149
Skoda	Fabia i	1.4	Schrägheck	Frontantrieb	Benzin	Aug 1999	May 2003	13363
Skoda	Fabia i	1.4	Schrägheck	Frontantrieb	Benzin	Aug 2000	Aug 2002	15106
Skoda	Fabia i	1.4	Stufenheck	Frontantrieb	Benzin	Jul 2001	May 2003	16059
Skoda	Fabia i	1.4	Stufenheck	Frontantrieb	Benzin	Apr 2000	Aug 2002	18150
Skoda	Fabia i	2	Schrägheck	Frontantrieb	Benzin	Dec 1999	Mar 2008	15586
Skoda	Fabia i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Dec 1999	Mar 2008	13362
Skoda	Fabia i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Dec 1999	Mar 2008	15107
Skoda	Fabia i	1.4 16V	Stufenheck	Frontantrieb	Benzin	Oct 1999	Dec 2007	15938
Skoda	Fabia i	1.4 16V	Stufenheck	Frontantrieb	Benzin	Dec 1999	Dec 2007	16060
Skoda	Fabia i	1.4 TDI	Stufenheck	Frontantrieb	Diesel	Apr 2003	Dec 2007	17517
Skoda	Fabia i	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2003	Mar 2008	17519
Skoda	Fabia i	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Dec 1999	Mar 2008	13364
Skoda	Fabia i	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Nov 1999	Dec 2007	16058
Skoda	Fabia i	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Jan 2000	Mar 2008	14278
Skoda	Fabia i	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Jan 2000	Dec 2007	15937
Skoda	Fabia i	1.9 TDI RS	Schrägheck	Frontantrieb	Diesel	Jun 2003	Mar 2008	17456
Skoda	Fabia i combi	1.2	Kombi	Frontantrieb	Benzin	Jan 2003	Dec 2007	17395
Skoda	Fabia i combi	1.4	Kombi	Frontantrieb	Benzin	Apr 2000	May 2003	15503
Skoda	Fabia i combi	1.4	Kombi	Frontantrieb	Benzin	Apr 2000	Mar 2003	17321
Skoda	Fabia i combi	2	Kombi	Frontantrieb	Benzin	Apr 2000	Dec 2007	15585
Skoda	Fabia i combi	1.4 16V	Kombi	Frontantrieb	Benzin	May 2000	Dec 2007	15582
Skoda	Fabia i combi	1.4 16V	Kombi	Frontantrieb	Benzin	Apr 2000	Dec 2007	15583
Skoda	Fabia i combi	1.4 TDI	Kombi	Frontantrieb	Diesel	Apr 2003	Dec 2007	17518
Skoda	Fabia i combi	1.9 SDI	Kombi	Frontantrieb	Diesel	Apr 2000	Dec 2007	15504
Skoda	Fabia i combi	1.9 TDI	Kombi	Frontantrieb	Diesel	Apr 2000	Dec 2007	15584
Skoda	Fabia i praktik	1.2	Kasten/Kombi	Frontantrieb	Benzin	Jan 2003	Dec 2007	17396
Skoda	Fabia i praktik	1.9 SDI	Kasten/Kombi	Frontantrieb	Diesel	Jul 2001	Dec 2007	17397
Skoda	Fabia ii	1.2 TDI	Schrägheck	Frontantrieb	Diesel	May 2010	Dec 2014	33876
Skoda	Fabia ii combi	1.2 TDI	Kombi	Frontantrieb	Diesel	May 2010	Dec 2014	33877
Skoda	Fabia ii praktik	TDI	Kasten/Kombi	Frontantrieb	Diesel	Oct 2013	Nov 2014	154623
Skoda	Fabia iii	1	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	108655
Skoda	Fabia iii	1	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	108656
Skoda	Fabia iii	1	Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	108661
Skoda	Fabia iii	1	Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	108666
Skoda	Fabia iii	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2015	Jun 2021	117788
Skoda	Fabia iii	1.6	Kombi	Frontantrieb	Benzin	Jan 2015	Dec 2022	117789


--- Round 1 / 首次发送 ---
## 更新点

已完成本批 100 个 Ktype 的物理外廓归并。复用 3 个既有 Toledo 尺寸组，新增 29 个尺寸组；Citigo 按输入未编码门数时映射至 5 门车身，Fabia Praktik 复用对应 Combi 外廓，Enyaq 与 Elroq 仅在三维明确不同的版本间建立独立尺寸组。Toledo II、III、IV 的累计尺寸与复核结果一致。([汽车数据网][1])

机械终检已通过：100 个输入 Ktype 全部覆盖，`READY=100`、`PENDING=0`；映射 ID 唯一，32 个尺寸组全部被引用，三维均为正整数，来源和直接 URL 完整。

## 当前批进度

`总数=100｜READY=100｜PENDING=0｜DIMENSION_GROUP=32｜孤立尺寸组=0`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
115145	115145	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
14571	14571	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
100020	100020	MPV	III	5P	5	EU-SEAT-TOLEDO-III-MPV-STANDARD-01	HIGH		READY
115149	115149	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
57525	57525	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
115146	115146	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
15802	15802	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
57526	57526	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
100023	100023	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
115151	115151	Hatchback	IV	NH	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
10047	10047	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
17926	17926	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
8095	8095	Hatchback	I	1L	5	EU-SEAT-TOLEDO-I-HATCHBACK-STANDARD-01	HIGH		READY
10049	10049	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
10050	10050	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
16180	16180	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
17514	17514	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
18382	18382	MPV	III	5P	5	EU-SEAT-TOLEDO-III-MPV-STANDARD-01	HIGH		READY
18381	18381	MPV	III	5P	5	EU-SEAT-TOLEDO-III-MPV-STANDARD-01	HIGH		READY
18383	18383	MPV	III	5P	5	EU-SEAT-TOLEDO-III-MPV-STANDARD-01	HIGH		READY
10048	10048	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
16071	16071	Sedan	II	1M	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
145624	145624	SUV	I		5	EU-SERES-3-I-SUV-STANDARD-01	HIGH		READY
155099	155099	SUV	I		5	EU-SERES-5-I-SUV-STANDARD-01	HIGH		READY
155102	155102	SUV	I		5	EU-SERES-5-I-SUV-STANDARD-01	HIGH		READY
802902	802902	SUV	I		5	EU-SERES-5-I-SUV-STANDARD-01	HIGH		READY
802901	802901	SUV	I		5	EU-SERES-5-I-SUV-STANDARD-01	HIGH		READY
155101	155101	SUV	I		5	EU-SERES-5-I-SUV-STANDARD-01	HIGH		READY
144608	144608	Pickup	I			EU-SEVIC-S70-I-PICKUP-STANDARD-01	HIGH		READY
144229	144229	Pickup	I			EU-SEVIC-V500-I-PICKUP-STANDARD-01	MEDIUM	Mapped to the 2021 V500e standard platform.	READY
154972	154972	Van	I		5	EU-SHINERAY-X30-I-VAN-STANDARD-01	MEDIUM	Mapped to the X30LEV long-body electric van.	READY
160367	160367	Hatchback	I		3	EU-SILENCE-S04-I-HATCHBACK-MY25-01	HIGH		READY
160372	160372	Hatchback	I		3	EU-SILENCE-S04-I-HATCHBACK-MY25-01	HIGH		READY
160375	160375	Hatchback	I		3	EU-SILENCE-S04-I-HATCHBACK-MY25-01	HIGH		READY
160376	160376	Hatchback	I		3	EU-SILENCE-S04-I-HATCHBACK-MY25-01	HIGH		READY
5070	5070	Sedan	742	742	4	EU-SKODA-105120-742-SEDAN-STANDARD-01	HIGH		READY
15989	15989	Hatchback	I	NF1	5	EU-SKODA-CITIGO-I-HATCHBACK-PETROL-01	MEDIUM	Door variant not encoded; mapped to the 5-door body.	READY
15995	15995	Hatchback	I	NF1	5	EU-SKODA-CITIGO-I-HATCHBACK-PETROL-01	MEDIUM	Door variant not encoded; mapped to the 5-door body.	READY
58802	58802	Hatchback	I	NF1	5	EU-SKODA-CITIGO-I-HATCHBACK-CNG-01	MEDIUM	Door variant not encoded; mapped to the 5-door body.	READY
159345	159345	SUV	I	NY	5	EU-SKODA-ELROQ-I-SUV-50-60-85-01	HIGH		READY
159346	159346	SUV	I	NY	5	EU-SKODA-ELROQ-I-SUV-50-60-85-01	HIGH		READY
159344	159344	SUV	I	NY	5	EU-SKODA-ELROQ-I-SUV-50-60-85-01	HIGH		READY
159347	159347	SUV	I	NY	5	EU-SKODA-ELROQ-I-SUV-85X-01	HIGH		READY
161794	161794	SUV	I	NY	5	EU-SKODA-ELROQ-I-SUV-RS-01	HIGH		READY
800212	800212	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-50-01	HIGH		READY
801922	801922	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-FACELIFT-60-01	HIGH		READY
156287	156287	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-85-01	HIGH		READY
145613	145613	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-80X-85X-01	HIGH		READY
156288	156288	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-80X-85X-01	HIGH		READY
155565	155565	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-RS-01	HIGH		READY
156807	156807	SUV	I	5A	5	EU-SKODA-ENYAQ-I-SUV-RS-01	HIGH		READY
147493	147493	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-60-85-85X-01	HIGH		READY
801923	801923	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-FACELIFT-60-01	HIGH		READY
147494	147494	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-80-80X-01	HIGH		READY
156516	156516	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-60-85-85X-01	HIGH		READY
147495	147495	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-80-80X-01	HIGH		READY
156517	156517	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-60-85-85X-01	HIGH		READY
146691	146691	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-RS-01	HIGH		READY
156809	156809	SUV	I	5A	5	EU-SKODA-ENYAQ-I-COUPE-RS-01	HIGH		READY
14277	14277	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
16944	16944	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
17393	17393	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
17394	17394	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
18149	18149	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
13363	13363	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
15106	15106	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
16059	16059	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
18150	18150	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
15586	15586	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
13362	13362	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
15107	15107	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
15938	15938	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
16060	16060	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
17517	17517	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
17519	17519	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
13364	13364	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
16058	16058	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
14278	14278	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
15937	15937	Sedan	I	6Y3	4	EU-SKODA-FABIA-I-SEDAN-STANDARD-01	HIGH		READY
17456	17456	Hatchback	I	6Y2	5	EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	HIGH		READY
17395	17395	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15503	15503	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
17321	17321	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15585	15585	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15582	15582	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15583	15583	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
17518	17518	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15504	15504	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
15584	15584	Wagon	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	HIGH		READY
17396	17396	Van	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	MEDIUM	Praktik uses the Fabia I Combi exterior shell.	READY
17397	17397	Van	I	6Y5	5	EU-SKODA-FABIA-I-WAGON-STANDARD-01	MEDIUM	Praktik uses the Fabia I Combi exterior shell.	READY
33876	33876	Hatchback	II	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-STANDARD-01	HIGH		READY
33877	33877	Wagon	II	5J5	5	EU-SKODA-FABIA-II-WAGON-STANDARD-01	HIGH		READY
154623	154623	Van	II	5J5	5	EU-SKODA-FABIA-II-WAGON-STANDARD-01	MEDIUM	Praktik uses the Fabia II Combi exterior shell.	READY
108655	108655	Hatchback	III	6V2	5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108656	108656	Hatchback	III	6V2	5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108661	108661	Wagon	III	6V5	5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
108666	108666	Wagon	III	6V5	5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
117788	117788	Hatchback	III	6V2	5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
117789	117789	Wagon	III	6V5	5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射表](sandbox:/mnt/data/left18448_15101-15200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	4482	1706	1461	Auto-Data	https://www.auto-data.net/en/seat-toledo-iv-nh-generation-4194
EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	4439	1742	1436	Auto-Data	https://www.auto-data.net/en/seat-toledo-ii-1m2-generation-2912
EU-SEAT-TOLEDO-III-MPV-STANDARD-01	4458	1768	1568	Auto-Data	https://www.auto-data.net/en/seat-toledo-iii-5p-generation-2911
EU-SEAT-TOLEDO-I-HATCHBACK-STANDARD-01	4321	1662	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/3065705/seat_toledo_1_6i.html
EU-SERES-3-I-SUV-STANDARD-01	4385	1850	1650	EV Database	https://ev-database.org/car/1357/Seres-3
EU-SERES-5-I-SUV-STANDARD-01	4710	1930	1620	Auto-Data	https://www.auto-data.net/en/seres-5-generation-9100
EU-SEVIC-S70-I-PICKUP-STANDARD-01	1995	735	1245	SEVIC technical specifications	https://sevic.com/data/fms/Files/placeholder/documents/technical_specifications_S70_EN_upd2021.pdf
EU-SEVIC-V500-I-PICKUP-STANDARD-01	3701	1366	1965	SEVIC V500e brochure	https://autorings.lv/PDF/EN-SEVIC-V500E-BROCHURE-ONLINE.pdf
EU-SHINERAY-X30-I-VAN-STANDARD-01	4495	1680	1990	Shineray official specifications	https://www.shineray.com/page/list-28.html
EU-SILENCE-S04-I-HATCHBACK-MY25-01	2282	1268	1573	Silence S04 MY25 user manual	https://www.silence.eco/global/user-manual/UM_S04-MY25_ENG_V1.2-User-Manual-S04-MY25.pdf
EU-SKODA-105120-742-SEDAN-STANDARD-01	4200	1610	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/41735/skoda_120_l.html
EU-SKODA-CITIGO-I-HATCHBACK-PETROL-01	3597	1645	1478	Skoda Citigo technical data	https://cdn.skoda-storyboard.com/2016/05/TD-CITIGO-en.pdf
EU-SKODA-CITIGO-I-HATCHBACK-CNG-01	3597	1645	1480	Skoda Citigo technical data	https://cdn.skoda-storyboard.com/2016/05/TD-CITIGO-en.pdf
EU-SKODA-ELROQ-I-SUV-50-60-85-01	4488	1884	1625	Skoda Elroq technical data	https://cdn.skoda-storyboard.com/2024/10/TD-Elroq-en_f8cdb684.pdf
EU-SKODA-ELROQ-I-SUV-85X-01	4488	1884	1620	Skoda Elroq technical data	https://cdn.skoda-storyboard.com/2024/10/TD-Elroq-en_f8cdb684.pdf
EU-SKODA-ELROQ-I-SUV-RS-01	4488	1884	1608	Skoda Elroq technical data	https://cdn.skoda-storyboard.com/2024/10/TD-Elroq-en_f8cdb684.pdf
EU-SKODA-ENYAQ-I-SUV-50-01	4649	1879	1619	Skoda Enyaq iV technical data	https://cdn.skoda-storyboard.com/2020/08/TD-ENYAQ-iV-en.pdf
EU-SKODA-ENYAQ-I-SUV-FACELIFT-60-01	4658	1879	1622	Skoda Enyaq technical data	https://cdn.skoda-storyboard.com/2025/01/TD-Enyaq-en_1fba4bab.pdf
EU-SKODA-ENYAQ-I-SUV-85-01	4649	1879	1621	Auto-Data	https://www.auto-data.net/en/skoda-enyaq-iv-85-82-kwh-286hp-52179
EU-SKODA-ENYAQ-I-SUV-80X-85X-01	4649	1879	1620	Auto-Data	https://www.auto-data.net/en/skoda-enyaq-iv-85x-82-kwh-286hp-awd-52180
EU-SKODA-ENYAQ-I-SUV-RS-01	4653	1879	1605	Skoda Enyaq iV technical data	https://cdn.skoda-storyboard.com/2024/02/TD-Enyaq-iV-en_9ed3112d_7065b055.pdf
EU-SKODA-ENYAQ-I-COUPE-60-85-85X-01	4653	1879	1621	Auto-Data	https://www.auto-data.net/en/skoda-enyaq-coupe-iv-85-82-kwh-286hp-52176
EU-SKODA-ENYAQ-I-COUPE-FACELIFT-60-01	4658	1879	1623	Skoda Enyaq Coupe technical data	https://cdn.skoda-storyboard.com/2025/05/TD-Enyaq-Coupe-en_d0e93c99.pdf
EU-SKODA-ENYAQ-I-COUPE-80-80X-01	4653	1879	1622	Auto-Data	https://www.auto-data.net/en/skoda-enyaq-coupe-iv-80x-82-kwh-265hp-awd-45373
EU-SKODA-ENYAQ-I-COUPE-RS-01	4653	1879	1607	Skoda Enyaq Coupe RS iV technical data	https://cdn.skoda-storyboard.com/2022/03/TD-ENYAQ-COUPE-RS-iV-en.pdf
EU-SKODA-FABIA-I-HATCHBACK-STANDARD-01	3960	1646	1451	Auto-Data	https://www.auto-data.net/en/skoda-fabia-i-6y-1.4-60hp-14150
EU-SKODA-FABIA-I-SEDAN-STANDARD-01	4222	1646	1449	Auto-Data	https://www.auto-data.net/en/skoda-fabia-sedan-i-6y-generation-3093
EU-SKODA-FABIA-I-WAGON-STANDARD-01	4222	1646	1452	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3135995/skoda_fabia_combi_1_4_mpi_68.html
EU-SKODA-FABIA-II-HATCHBACK-STANDARD-01	3992	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-generation-3089
EU-SKODA-FABIA-II-WAGON-STANDARD-01	4239	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-combi-generation-3090
EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	3992	1732	1467	Auto-Data	https://www.auto-data.net/en/skoda-fabia-iii-generation-4317
EU-SKODA-FABIA-III-WAGON-STANDARD-01	4257	1732	1467	Auto-Data	https://www.auto-data.net/en/skoda-fabia-iii-combi-generation-4318
```

[下载完整 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_15101-15200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/seat-toledo-ii-1m2-generation-2912?utm_source=chatgpt.com "Seat Toledo II (1M2) | Technical Specs, Fuel consumption ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1633 行）
- 累计尺寸组：dimension_groups_final.tsv（330 行）

