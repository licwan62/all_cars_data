# 任务：left18448 第 8401-8500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0085__6d53cb53


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8401-8500 行

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
left18448 第 8401-8500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8401-8500_ktype_dimension_mapping_final.tsv
- left18448_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-LANCIA-THEMA-834-SEDAN-01	4590	1750	1435
EU-LANCIA-THEMA-834-WAGON-01	4590	1755	1440
EU-LANCIA-THEMA-LX-SEDAN-01	5066	1906	1488

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Lancia	Thema	3.0 D	Stufenheck	Heckantrieb	Diesel	Sep 2011	Oct 2014	11807
Lancia	Thema	3.0 D	Stufenheck	Heckantrieb	Diesel	Sep 2011	Oct 2014	11808
Lancia	Thema	3.6 4WD	Stufenheck	Allrad	Benzin	Sep 2011	Oct 2014	108293
Lancia	Thesis	2.4	Stufenheck	Frontantrieb	Benzin	Jul 2002	Jul 2009	16528
Lancia	Thesis	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	Jul 2002	Jul 2009	16527
Lancia	Thesis	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Jul 2002	Jul 2009	16529
Lancia	Thesis	2.4 JTD	Stufenheck	Frontantrieb	Diesel	May 2003	Jul 2009	17609
Lancia	Thesis	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Sep 2003	Jul 2009	58713
Lancia	Thesis	3.0 V6	Stufenheck	Frontantrieb	Benzin	Jul 2002	Jul 2009	16505
Lancia	Thesis	3.2 V6	Stufenheck	Frontantrieb	Benzin	May 2003	Jul 2009	17610
Lancia	Trevi	1600	Stufenheck	Frontantrieb	Benzin	May 1980	Jan 1987	15140
Lancia	Voyager	2.8 CRD	Großraumlimousine	Frontantrieb	Diesel	Sep 2011	Dec 2014	11812
Lancia	Voyager	2.8 CRD	Großraumlimousine	Frontantrieb	Diesel	Aug 2013	Dec 2014	52437
Lancia	Voyager	2.8 CRD	Großraumlimousine	Frontantrieb	Diesel	Jul 2012	Dec 2014	58714
Lancia	Voyager	3.6 V6	Großraumlimousine	Frontantrieb	Benzin	Sep 2011	Dec 2014	11810
Lancia	Y	1.2 16V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Sep 2003	15606
Lancia	Y	1.4 12V	Schrägheck	Frontantrieb	Benzin	Oct 1996	Sep 2003	7808
Lancia	Y10	1	Schrägheck	Frontantrieb	Benzin	Mar 1985	Jul 1989	13284
Lancia	Y10	1.0 Fire	Schrägheck	Frontantrieb	Benzin	Mar 1985	Jun 1989	15045
Lancia	Y10	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	Mar 1985	Feb 1989	5069
Lancia	Y10	1.1 I.E Fire	Schrägheck	Frontantrieb	Benzin	Aug 1989	Jun 1992	15043
Lancia	Y10	1.1 I.E Fire Allrad	Schrägheck	Allrad	Benzin	Aug 1989	Jun 1992	15044
Lancia	Ypsilon	1.2	Schrägheck	Frontantrieb	Benzin	May 2011	Dec 2021	10276
Lancia	Ypsilon	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2003	Dec 2011	17449
Lancia	Ypsilon	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2003	Dec 2011	17450
Lancia	Ypsilon	0.9 CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	May 2011	-	59317
Lancia	Ypsilon	0.9 Twinair	Schrägheck	Frontantrieb	Benzin	May 2011	Dec 2018	10212
Lancia	Ypsilon	0.9 Twinair	Schrägheck	Frontantrieb	Benzin	Dec 2013	Dec 2018	100769
Lancia	Ypsilon	1.2 Bi-fuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	-	10283
Lancia	Ypsilon	1.2 Bi-fuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	-	114586
Lancia	Ypsilon	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	May 2011	Aug 2018	10271
Lancia	Ypsilon	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Mar 2017	-	802281
Lancia	Ypsilon	1.3 JTD	Schrägheck	Frontantrieb	Diesel	Oct 2003	Dec 2011	17452
Lancia	Ypsilon	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2003	Dec 2011	17451
Lancia	Ypsilon	EV	Schrägheck	Frontantrieb	Elektro	Feb 2024	-	157785
Lancia	Ypsilon	EV	Schrägheck	Frontantrieb	Elektro	Sep 2025	-	802290
Lancia	Ypsilon	Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2024	-	158402
Lancia	Ypsilon	Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2025	-	803056
Lancia	Zeta	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 1998	Jul 2000	11371
Lancia	Zeta	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Jul 2000	Sep 2002	15065
Lancia	Zeta	2.1 TD	Großraumlimousine	Frontantrieb	Diesel	May 1996	Sep 1999	5734
Land Rover	90	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 1984	Jul 1990	59361
Land Rover	110/127	2.3	Geländewagen offen	Allrad	Benzin	Jun 1984	Aug 1987	150538
Land Rover	110/127	2.3	Geländewagen offen	Allrad	Diesel	Jun 1984	Aug 1987	150539
Land Rover	110/127	2.5	Geländewagen offen	Allrad	Diesel	Jun 1984	Dec 1990	150536
Land Rover	110/127	2.5	Geländewagen offen	Allrad	Benzin	Oct 1985	Aug 1990	150541
Land Rover	110/127	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 1985	Jul 1990	59864
Land Rover	110/127	2.5 TD	Geländewagen offen	Allrad	Diesel	Sep 1986	Aug 1990	150543
Land Rover	110/127	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 1985	Jul 1990	126015
Land Rover	Defender	2.2 TD4 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Aug 2011	Feb 2016	56210
Land Rover	Defender	2.4 TD4 4X4	Pritsche/Fahrgestell	Allrad	Diesel	May 2007	Feb 2016	59758
Land Rover	Defender cabrio	2.2 TD4 4X4	Geländewagen offen	Allrad	Diesel	Aug 2011	Feb 2016	13972
Land Rover	Defender cabrio	2.5 TD5 4X4	Geländewagen offen	Allrad	Diesel	Jun 1998	Feb 2016	17474
Land Rover	Defender pick up	2.2 TD4 4X4	Geländewagen offen	Allrad	Diesel	Aug 2011	Feb 2016	13973
Land Rover	Defender pick up	2.5 TD5 4X4	Geländewagen offen	Allrad	Diesel	Jun 1998	Feb 2016	17473
Land Rover	Defender station wagon	2.2 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	Aug 2011	Feb 2016	13971
Land Rover	Defender station wagon	2.2 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	Feb 2015	Feb 2016	112181
Land Rover	Defender station wagon	2.5 TD5 4X4	Geländewagen geschlossen	Allrad	Diesel	Jun 1998	Feb 2016	11626
Land Rover	Defender station wagon	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Sep 1990	Jul 1994	126014
Land Rover	Defender station wagon	3.9 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Nov 1998	Feb 2016	11244
Land Rover	Defender station wagon	D350 Mhev 4X4	Geländewagen geschlossen	Allrad	Diesel/Elektro	May 2024	-	158737
Land Rover	Defender station wagon	P300 Mhev 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	May 2022	-	148046
Land Rover	Defender station wagon	P300 Mhev 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	Jul 2023	-	155250
Land Rover	Defender station wagon	P300e Hybrid 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	Jun 2024	-	800481
Land Rover	Defender station wagon	P425 4X4	Geländewagen geschlossen	Allrad	Benzin	May 2024	-	158736
Land Rover	Defender station wagon	P500 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 2023	-	154512
Land Rover	Defender station wagon	P525 4X4	Geländewagen geschlossen	Allrad	Benzin	May 2021	-	144996
Land Rover	Defender station wagon	P635 Octa Mhev 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	May 2024	-	800296
Land Rover	Defender van	3.0 D350 Mhev 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel/Elektro	May 2024	-	800277
Land Rover	Discovery i	2.0 16 V 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 1989	Oct 1998	14307
Land Rover	Discovery i	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	Sep 1993	Oct 1998	14308
Land Rover	Discovery ii	2.5 TD5 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 1998	Jun 2004	10139
Land Rover	Discovery ii	2.5 TD5 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 1998	Jun 2004	105799
Land Rover	Discovery ii	4.0 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Nov 1998	Jun 2004	10943
Land Rover	Discovery iii	2.7 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jul 2004	Sep 2009	18239
Land Rover	Discovery iii	4.4 4X4	Geländewagen geschlossen	Allrad	Benzin	Jul 2004	Sep 2009	18238
Land Rover	Discovery iv	3.0 Sdv6 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 2009	Dec 2018	11891
Land Rover	Discovery iv	3.0 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jul 2012	Dec 2018	56756
Land Rover	Discovery sport	1.5 P 270e Phev 4X4	SUV	Allrad	Benzin/Elektro	May 2024	-	800227
Land Rover	Discovery sport	2.0 4X4	SUV	Allrad	Benzin	Nov 2014	-	107643
Land Rover	Discovery sport	2.0 4X4	SUV	Allrad	Benzin	Aug 2017	-	127384
Land Rover	Discovery sport	2.0 D	SUV	Frontantrieb	Diesel	Aug 2015	-	117411
Land Rover	Discovery sport	2.0 D 4X4	SUV	Allrad	Diesel	Dec 2014	-	107640
Land Rover	Discovery sport	2.0 D 4X4	SUV	Allrad	Diesel	Jun 2015	-	115141
Land Rover	Discovery sport	2.0 D 4X4	SUV	Allrad	Diesel	Aug 2017	-	127390
Land Rover	Discovery sport	2.0 D165 Mhev	SUV	Frontantrieb	Diesel/Elektro	Mar 2021	-	148138
Land Rover	Discovery sport	2.0 P200 Flex 4X4	SUV	Allrad	Benzin/Ethanol	May 2022	-	152766
Land Rover	Discovery sport	2.0 SI4 4X4	SUV	Allrad	Benzin	Dec 2017	-	150609
Land Rover	Discovery sport	2.2 D 4X4	SUV	Allrad	Diesel	Sep 2014	-	107641
Land Rover	Discovery sport	2.2 D 4X4	SUV	Allrad	Diesel	Sep 2014	-	107642
Land Rover	Discovery sport van	ED4 E-capability	Kasten/SUV	Frontantrieb	Diesel	Aug 2015	-	142915
Land Rover	Discovery sport van	SD4 4X4	Kasten/SUV	Allrad	Diesel	Aug 2017	-	142919
Land Rover	Discovery sport van	SI4 4X4	Kasten/SUV	Allrad	Benzin	Dec 2017	-	142896
Land Rover	Discovery sport van	SI4 4X4	Kasten/SUV	Allrad	Benzin	Aug 2017	-	142897
Land Rover	Discovery sport van	SI4 4X4	Kasten/SUV	Allrad	Benzin	Jan 2017	-	142898
Land Rover	Discovery sport van	TD4 4X4	Kasten/SUV	Allrad	Diesel	Dec 2014	-	142916
Land Rover	Discovery sport van	TD4 4X4	Kasten/SUV	Allrad	Diesel	Jun 2015	-	142918
Land Rover	Discovery v	2.0 SD4 4X4	SUV	Allrad	Diesel	Sep 2016	-	124201
Land Rover	Discovery v	2.0 TD4 4X4	SUV	Allrad	Diesel	Sep 2016	-	124200
Land Rover	Discovery v	D250 Mhev 4X4	SUV	Allrad	Diesel/Elektro	Dec 2020	-	142741


--- Round 1 / 首次发送 ---
## 更新点

* 已完成全部 100 个输入 Ktype 的首轮聚类和映射，当前闭合 70 个、待处理 30 个。
* 已复用现有 `EU-LANCIA-THEMA-LX-SEDAN-01`，没有重复建立 Thema 尺寸组。
* 本轮新建 21 个尺寸组，覆盖 Thesis、Trevi、Voyager、Y/Y10/Ypsilon、Zeta，以及 Discovery II—V。
* Trevi、Y、Ypsilon 等跨改款生产期没有仅凭日期强行派生多行；按 Ktype 起始阶段的标准外廓保留单行。Trevi 的前后期车长及 Discovery Sport 改款前后外廓已有明确差异。([汽车目录][1])
* Defender 和早期 Land Rover 90/110/127 暂不硬合并。官方资料明确存在 90、110、130，以及 Hard Top、Station Wagon、Pickup、底盘驾驶室等不同长度和高度分支，当前 Ktype 尚未闭合到具体物理分支。

## 当前批次进度

* 输入 Ktype：100
* READY：70
* PENDING：30
* 新建 DIMENSION_GROUP：21
* 复用历史 DIMENSION_GROUP：1
* 当前映射行：100
* PENDING 主要集中于：Land Rover 90/110/127、经典 Defender、L663 Defender、Discovery I。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11807	11807	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
11808	11808	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
108293	108293	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
16528	16528	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16527	16527	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16529	16529	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
17609	17609	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
58713	58713	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16505	16505	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
17610	17610	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
15140	15140	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-EARLY-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联前期标准外廓。	READY
11812	11812	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
52437	52437	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
58714	58714	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
11810	11810	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
15606	15606	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-FACELIFT-01	HIGH		READY
7808	7808	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
13284	13284	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
15045	15045	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
5069	5069	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
15043	15043	Hatchback	Y10 II	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE2-FWD-01	HIGH		READY
15044	15044	Hatchback	Y10 II	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE2-4WD-01	HIGH	工厂四驱外廓独立。	READY
10276	10276	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
59317	59317	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10212	10212	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
100769	100769	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10283	10283	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
114586	114586	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10271	10271	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
802281	802281	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-FACELIFT-01	HIGH		READY
17449	17449	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17450	17450	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17452	17452	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17451	17451	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
157785	157785	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
802290	802290	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
158402	158402	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
803056	803056	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
11371	11371	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-LATE-01	HIGH		READY
15065	15065	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-LATE-01	HIGH		READY
5734	5734	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-EARLY-01	HIGH		READY
59361	59361	SUV	Land Rover 90				LOW		PENDING: Ktype未闭合到90 Hard Top或County封闭车身，标准高度不同
150538	150538	Convertible	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距开放车身分支
150539	150539	Convertible	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距开放车身分支
150536	150536	Convertible	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距开放车身分支
150541	150541	Convertible	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距开放车身分支
150543	150543	Convertible	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距开放车身分支
59864	59864	SUV	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距封闭车身分支
126015	126015	SUV	Land Rover 110/127				LOW		PENDING: Ktype未闭合到110或127轴距封闭车身分支
56210	56210	Pickup	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到110/130轴距及底盘驾驶室分支
59758	59758	Pickup	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到110/130轴距及底盘驾驶室分支
13972	13972	Convertible	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距软顶分支
17474	17474	Convertible	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距软顶分支
13973	13973	Pickup	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110/130轴距及Pickup外廓分支
17473	17473	Pickup	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110/130轴距及Pickup外廓分支
13971	13971	SUV	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距Station Wagon分支
112181	112181	SUV	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距Station Wagon分支
11626	11626	SUV	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距Station Wagon分支
126014	126014	SUV	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距Station Wagon分支
11244	11244	SUV	Defender I	L316/L317			LOW		PENDING: Ktype未闭合到90/110轴距Station Wagon分支
158737	158737	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
148046	148046	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
155250	155250	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
800481	800481	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
158736	158736	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
154512	154512	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
144996	144996	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
800296	800296	SUV	Defender II	L663	5		LOW		PENDING: Ktype未闭合到90/110/130车长分支
800277	800277	Van	Defender II	L663	3		LOW		PENDING: Ktype未闭合到90/110 Hard Top车长分支
14307	14307	SUV	Discovery I	LJ/LG			LOW		PENDING: Ktype生产期覆盖门数及前后期外廓差异，物理边界未闭合
14308	14308	SUV	Discovery I	LJ/LG			LOW		PENDING: Ktype生产期覆盖门数及前后期外廓差异，物理边界未闭合
10139	10139	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
105799	105799	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
10943	10943	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
18239	18239	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	HIGH		READY
18238	18238	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	HIGH		READY
11891	11891	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	HIGH		READY
56756	56756	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	HIGH		READY
800227	800227	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
107643	107643	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
127384	127384	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
117411	117411	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107640	107640	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
115141	115141	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
127390	127390	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
150609	150609	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107641	107641	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107642	107642	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
148138	148138	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
152766	152766	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
142915	142915	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142919	142919	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142896	142896	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142897	142897	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142898	142898	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142916	142916	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142918	142918	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
124201	124201	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	HIGH		READY
124200	124200	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	HIGH		READY
142741	142741	SUV	Discovery V facelift	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

历史已有的 `EU-LANCIA-THEMA-LX-SEDAN-01` 为直接复用，本轮不重复输出。

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	4888	1830	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/1385075/lancia_thesis_2_4_jtd_executive.html
EU-LANCIA-TREVI-828-SEDAN-EARLY-01	4355	1706	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/1376915/lancia_beta_trevi_1600.html
EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	5218	1998	1750	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1577165/lancia_voyager_2_8_d_gold.html
EU-LANCIA-Y-840-HATCHBACK-PREFL-01	3723	1690	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1384085/lancia_ypsilon_1_2_16v_ls.html
EU-LANCIA-Y-840-HATCHBACK-FACELIFT-01	3741	1690	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/1384190/lancia_ypsilon_1_2_16v_lx_2a_serie.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	3392	1507	1423	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1380905/lancia_y10_fire.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE2-FWD-01	3392	1507	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1381115/lancia_y10_fire_lx_i_e_.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE2-4WD-01	3392	1537	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1381160/lancia_y10_4wd_i_e_.html
EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	3778	1704	1530	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1385735/lancia_ypsilon_1_2.html
EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	3842	1676	1517	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1576745/lancia_ypsilon_1_2_fire_evo_ii_69.html
EU-LANCIA-YPSILON-846-HATCHBACK-FACELIFT-01	3837	1676	1518	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2326760/lancia_ypsilon_twinair_turbo_80_metano.html
EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	4080	1755	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2025/3380915/lancia_ypsilon_ibrido_100.html
EU-LANCIA-ZETA-220-MPV-EARLY-01	4454	1834	1714	Auto-Data	https://www.auto-data.net/en/lancia-zeta-2.1-td-109hp-5044
EU-LANCIA-ZETA-220-MPV-LATE-01	4470	1834	1714	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1383920/lancia_zeta_2_0_16v_lx.html
EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	4705	1885	1900	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1400810/land-rover_discovery_td5_gs.html
EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	4848	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1405430/land-rover_discovery_3_tdv6_s.html
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	4829	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2045495/land-rover_discovery_4_3_0_sdv6.html
EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	4599	2000	1724	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2327360/land-rover_discovery_sport_td4_150_awd_automatic.html
EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	4597	2000	1727	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2976185/land-rover_discovery_sport_d165_mhev_awd.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	4970	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	4956	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2023/2976155/land-rover_discovery_3_0_d300_mhev_awd.html
```

## 下一步优先处理

集中消除剩余 30 个 PENDING，顺序为：先用 Ktype 适用目录闭合现代 Defender L663 的 90/110/130 分支；再处理经典 Defender 的 90/110/130、Station Wagon、Soft Top、Pickup 和底盘驾驶室；最后闭合 Land Rover 90/110/127 与 Discovery I 的门数及前后期边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/1377110/lancia_trevi_1600.html?utm_source=chatgpt.com "1981 Lancia Trevi 1600 Specs Review (73.6 kW / 100 PS / 99 hp) (since mid-year 1981 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8401-8500_ktype_dimension_mapping_final.tsv
- left18448_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 剩余 30 个 `PENDING` 已全部闭合。本轮新增 15 个独立尺寸组，完成早期 Land Rover、经典 Defender、L663 Defender 与 Discovery I 的映射。
* L663 已按实际 Ktype 落到 90、110、130 和 110 OCTA；经典 Defender 按 90 Soft Top、110 Pickup、110 Station Wagon、130 Chassis Cab 区分。([Starter Motors & Alternators][1])
* 历史 Thema LX 尺寸组保持累计表给定的 `5066×1906×1488`，来源字段机械修正为支持该组三维的 Auto-Data 页面。([汽车数据][2])
* 机械终检通过：固定表头和列数正确；100 个 `id`、Ktype 唯一；37 个尺寸组唯一；全部映射引用闭合；无 `PENDING`、无孤立尺寸组；三维、来源和直接 URL 均完整。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：37
* 映射引用闭合：100/100

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11807	11807	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
11808	11808	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
108293	108293	Sedan	Thema LX	LX	4	EU-LANCIA-THEMA-LX-SEDAN-01	HIGH		READY
16528	16528	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16527	16527	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16529	16529	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
17609	17609	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
58713	58713	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
16505	16505	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
17610	17610	Sedan	Thesis	841	4	EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	HIGH		READY
15140	15140	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-EARLY-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联前期标准外廓。	READY
11812	11812	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
52437	52437	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
58714	58714	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
11810	11810	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	HIGH		READY
15606	15606	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-FACELIFT-01	HIGH		READY
7808	7808	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
13284	13284	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
15045	15045	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
5069	5069	Hatchback	Y10 I	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	HIGH		READY
15043	15043	Hatchback	Y10 II	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE2-FWD-01	HIGH		READY
15044	15044	Hatchback	Y10 II	156	3	EU-LANCIA-Y10-156-HATCHBACK-PHASE2-4WD-01	HIGH	工厂四驱外廓独立。	READY
10276	10276	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
59317	59317	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10212	10212	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
100769	100769	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10283	10283	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
114586	114586	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
10271	10271	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
802281	802281	Hatchback	Ypsilon III	846	5	EU-LANCIA-YPSILON-846-HATCHBACK-FACELIFT-01	HIGH		READY
17449	17449	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17450	17450	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17452	17452	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
17451	17451	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	MEDIUM	跨期日期不单独触发拆分；按Ktype起始阶段关联改款前外廓。	READY
157785	157785	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
802290	802290	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
158402	158402	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
803056	803056	Hatchback	Ypsilon IV	L21	5	EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	HIGH		READY
11371	11371	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-LATE-01	HIGH		READY
15065	15065	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-LATE-01	HIGH		READY
5734	5734	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-EARLY-01	HIGH		READY
59361	59361	SUV	Land Rover 90		3	EU-LAND-ROVER-90-LDV-SUV-COUNTY-01	MEDIUM	封闭车身按标准90 County外廓关联。	READY
150538	150538	Pickup	Land Rover 110/127	LDH	2	EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	MEDIUM	开放式系列按有证据的标准110 Pickup外廓关联；无127专属证据。	READY
150539	150539	Pickup	Land Rover 110/127	LDH	2	EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	MEDIUM	开放式系列按有证据的标准110 Pickup外廓关联；无127专属证据。	READY
150536	150536	Pickup	Land Rover 110/127	LDH	2	EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	MEDIUM	开放式系列按有证据的标准110 Pickup外廓关联；无127专属证据。	READY
150541	150541	Pickup	Land Rover 110/127	LDH	2	EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	MEDIUM	开放式系列按有证据的标准110 Pickup外廓关联；无127专属证据。	READY
150543	150543	Pickup	Land Rover 110/127	LDH	2	EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	MEDIUM	开放式系列按有证据的标准110 Pickup外廓关联；无127专属证据。	READY
59864	59864	SUV	Land Rover 110/127	LDH	5	EU-LAND-ROVER-110-127-LDH-SUV-110-01	MEDIUM	封闭系列按标准110 Station Wagon外廓关联；无127专属证据。	READY
126015	126015	SUV	Land Rover 110/127	LDH	5	EU-LAND-ROVER-110-127-LDH-SUV-110-01	MEDIUM	封闭系列按标准110 Station Wagon外廓关联；无127专属证据。	READY
56210	56210	Pickup	Defender I	L316/L317	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-CHASSIS-01	MEDIUM	Pritsche/Fahrgestell按标准130 Chassis Cab外廓关联。	READY
59758	59758	Pickup	Defender I	L316/L317	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-CHASSIS-01	MEDIUM	Pritsche/Fahrgestell按标准130 Chassis Cab外廓关联。	READY
13972	13972	Convertible	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-LATE-01	HIGH		READY
17474	17474	Convertible	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-EARLY-01	MEDIUM	跨期Ktype按起始阶段的90 Soft Top外廓关联。	READY
13973	13973	Pickup	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-LATE-01	MEDIUM	按标准110 Pickup外廓关联。	READY
17473	17473	Pickup	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-EARLY-01	MEDIUM	跨期Ktype按起始阶段的110 High Capacity Pickup外廓关联。	READY
13971	13971	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-LATE-01	HIGH		READY
112181	112181	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-LATE-01	HIGH		READY
11626	11626	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-EARLY-01	MEDIUM	跨期Ktype按起始阶段的110 Station Wagon外廓关联。	READY
126014	126014	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-EARLY-01	HIGH		READY
11244	11244	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-EARLY-01	MEDIUM	跨期Ktype按起始阶段的110 Station Wagon外廓关联。	READY
158737	158737	SUV	Defender II 90	L663	3	EU-LAND-ROVER-DEFENDER-L663-SUV-90-01	HIGH		READY
148046	148046	SUV	Defender II 130	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-130-01	HIGH		READY
155250	155250	SUV	Defender II 110	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-110-01	HIGH		READY
800481	800481	SUV	Defender II 110	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-110-01	HIGH		READY
158736	158736	SUV	Defender II 90	L663	3	EU-LAND-ROVER-DEFENDER-L663-SUV-90-01	HIGH		READY
154512	154512	SUV	Defender II 130	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-130-01	HIGH		READY
144996	144996	SUV	Defender II 110	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-110-01	HIGH		READY
800296	800296	SUV	Defender II 110 OCTA	L663	5	EU-LAND-ROVER-DEFENDER-L663-SUV-110-OCTA-01	HIGH	OCTA宽体为独立工厂外廓。	READY
800277	800277	Van	Defender II 90 Hard Top	L663	3	EU-LAND-ROVER-DEFENDER-L663-SUV-90-01	HIGH	Hard Top商用转换不改变90标准外廓。	READY
14307	14307	SUV	Discovery I	LJ	5	EU-LAND-ROVER-DISCOVERY-I-LJ-SUV-5D-01	MEDIUM	生产期跨越更新；按标准5门量产外廓关联。	READY
14308	14308	SUV	Discovery I	LJ	5	EU-LAND-ROVER-DISCOVERY-I-LJ-SUV-5D-01	MEDIUM	生产期跨越更新；按标准5门量产外廓关联。	READY
10139	10139	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
105799	105799	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
10943	10943	SUV	Discovery II	L318	5	EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	HIGH		READY
18239	18239	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	HIGH		READY
18238	18238	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	HIGH		READY
11891	11891	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	HIGH		READY
56756	56756	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	HIGH		READY
800227	800227	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
107643	107643	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
127384	127384	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
117411	117411	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107640	107640	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
115141	115141	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
127390	127390	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
150609	150609	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107641	107641	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
107642	107642	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH		READY
148138	148138	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
152766	152766	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	HIGH		READY
142915	142915	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142919	142919	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142896	142896	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142897	142897	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142898	142898	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142916	142916	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
142918	142918	Van	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	HIGH	商用Van转换不改变标准外廓。	READY
124201	124201	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	HIGH		READY
124200	124200	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	HIGH		READY
142741	142741	SUV	Discovery V facelift	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	HIGH		READY
```

[下载 left18448_8401-8500_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_8401-8500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-THEMA-LX-SEDAN-01	5066	1906	1488	Auto-Data	https://www.auto-data.net/en/lancia-thema-lx-generation-8532
EU-LANCIA-THESIS-841-SEDAN-STANDARD-01	4888	1830	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/1385075/lancia_thesis_2_4_jtd_executive.html
EU-LANCIA-TREVI-828-SEDAN-EARLY-01	4355	1706	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/1376915/lancia_beta_trevi_1600.html
EU-LANCIA-VOYAGER-RT-MPV-STANDARD-01	5218	1998	1750	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1577165/lancia_voyager_2_8_d_gold.html
EU-LANCIA-Y-840-HATCHBACK-PREFL-01	3723	1690	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1384085/lancia_ypsilon_1_2_16v_ls.html
EU-LANCIA-Y-840-HATCHBACK-FACELIFT-01	3741	1690	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/1384190/lancia_ypsilon_1_2_16v_lx_2a_serie.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE1-FWD-01	3392	1507	1423	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1380905/lancia_y10_fire.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE2-FWD-01	3392	1507	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1381115/lancia_y10_fire_lx_i_e_.html
EU-LANCIA-Y10-156-HATCHBACK-PHASE2-4WD-01	3392	1537	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1381160/lancia_y10_4wd_i_e_.html
EU-LANCIA-YPSILON-843-HATCHBACK-PREFL-01	3778	1704	1530	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1385735/lancia_ypsilon_1_2.html
EU-LANCIA-YPSILON-846-HATCHBACK-PREFL-01	3842	1676	1517	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1576745/lancia_ypsilon_1_2_fire_evo_ii_69.html
EU-LANCIA-YPSILON-846-HATCHBACK-FACELIFT-01	3837	1676	1518	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2326760/lancia_ypsilon_twinair_turbo_80_metano.html
EU-LANCIA-YPSILON-L21-HATCHBACK-STANDARD-01	4080	1755	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2025/3380915/lancia_ypsilon_ibrido_100.html
EU-LANCIA-ZETA-220-MPV-EARLY-01	4454	1834	1714	Auto-Data	https://www.auto-data.net/en/lancia-zeta-2.1-td-109hp-5044
EU-LANCIA-ZETA-220-MPV-LATE-01	4470	1834	1714	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1383920/lancia_zeta_2_0_16v_lx.html
EU-LAND-ROVER-DISCOVERY-II-L318-SUV-STANDARD-01	4705	1885	1900	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1400810/land-rover_discovery_td5_gs.html
EU-LAND-ROVER-DISCOVERY-III-L319-SUV-STANDARD-01	4848	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1405430/land-rover_discovery_3_tdv6_s.html
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-STANDARD-01	4829	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2045495/land-rover_discovery_4_3_0_sdv6.html
EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-PREFL-01	4599	2000	1724	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2327360/land-rover_discovery_sport_td4_150_awd_automatic.html
EU-LAND-ROVER-DISCOVERY-SPORT-L550-SUV-FACELIFT-01	4597	2000	1727	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2976185/land-rover_discovery_sport_d165_mhev_awd.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	4970	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	4956	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2023/2976155/land-rover_discovery_3_0_d300_mhev_awd.html
EU-LAND-ROVER-90-LDV-SUV-COUNTY-01	3858	1790	1991	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/1394465/land-rover_90_county_v8.html
EU-LAND-ROVER-110-127-LDH-PICKUP-110-01	4445	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1393820/land-rover_110_pick-up_v8.html
EU-LAND-ROVER-110-127-LDH-SUV-110-01	4580	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html
EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-CHASSIS-01	5170	1790	2021	CarExpert	https://www.carexpert.com.au/land-rover/defender/2011-2-4l-cab-chassis-4x4-diesel-manual-jookfg5o20101118
EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-EARLY-01	3722	1790	1965	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1395950/land-rover_defender_90_soft_top_300tdi.html
EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-LATE-01	3722	1790	1997	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1615565/land-rover_defender_90_soft_top.html
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-EARLY-01	4631	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1395560/land-rover_defender_110_pick-up_high_capacity_td5.html
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-LATE-01	4370	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1615445/land-rover_defender_110_pick-up.html
EU-LAND-ROVER-DEFENDER-L316-SUV-110-EARLY-01	4599	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/1396730/land-rover_defender_110_station_wagon_td5.html
EU-LAND-ROVER-DEFENDER-L316-SUV-110-LATE-01	4639	1790	2181	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1396910/land-rover_defender_110_station_wagon.html
EU-LAND-ROVER-DEFENDER-L663-SUV-90-01	4583	1996	1974	CarExpert	https://www.carexpert.com.au/land-rover/defender/2026-s-3l-suv-4x4-diesel-automatic-jsa8w5gg20250613
EU-LAND-ROVER-DEFENDER-L663-SUV-110-01	5018	1996	1967	CarExpert	https://www.carexpert.com.au/land-rover/defender/2025-x-3l-suv-4x4-diesel-automatic-jsa5ggaa20241007
EU-LAND-ROVER-DEFENDER-L663-SUV-130-01	5358	1996	1970	CarExpert	https://www.carexpert.com.au/land-rover/defender/2023-se-3l-suv-4x4-diesel-automatic-jgfasfm520230719
EU-LAND-ROVER-DEFENDER-L663-SUV-110-OCTA-01	5003	2064	1995	Yahoo Autos Taiwan	https://autos.yahoo.com.tw/new-cars/trim/land-rover-defender-2025-110-v8-octa-edition-one/spec
EU-LAND-ROVER-DISCOVERY-I-LJ-SUV-5D-01	4521	1793	1928	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/1399805/land_rover_discovery_300tdi_5-door.html
```

[下载 left18448_8401-8500_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_8401-8500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://starters-alternators.co.uk/products/starter-land-rover-2-2-kw-4?variant=50387152208200 "https://starters-alternators.co.uk/products/starter-land-rover-2-2-kw-4?variant=50387152208200"
[2]: https://www.auto-data.net/en/lancia-thema-lx-generation-8532 "https://www.auto-data.net/en/lancia-thema-lx-generation-8532"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6059 行）
- 累计尺寸组：dimension_groups_final.tsv（1690 行）

