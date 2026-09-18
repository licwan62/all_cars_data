# 任务：left18448 第 11701-11800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0118__245e4db5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11701-11800 行

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
left18448 第 11701-11800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11701-11800_ktype_dimension_mapping_final.tsv
- left18448_11701-11800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Nissan	Kubistar	1.5 DCI 70	Kasten	Frontantrieb	Diesel	Sep 2005	Oct 2009	106786
Nissan	Leaf	EV	SUV	Frontantrieb	Elektro	Jul 2025	-	162066
Nissan	Leaf	EV	SUV	Frontantrieb	Elektro	Jul 2025	-	162067
Nissan	Maxima / qx v	2.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Mar 2000	Nov 2003	14716
Nissan	Maxima / qx v	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Mar 2000	Nov 2003	14717
Nissan	Maxima / qx v	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Mar 2000	Nov 2003	14718
Nissan	Maxima vi	3.5	Stufenheck	Frontantrieb	Benzin	Sep 2006	Dec 2008	59989
Nissan	Micra c+c iii	1.4 16V	Cabriolet	Frontantrieb	Benzin	Aug 2005	Jan 2009	18970
Nissan	Micra c+c iii	1.6 160 SR	Cabriolet	Frontantrieb	Benzin	Aug 2005	Jun 2010	18972
Nissan	Micra ii	1.0 I 16V	Schrägheck	Frontantrieb	Benzin	Jul 2000	Feb 2003	15470
Nissan	Micra ii	1.4 I 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Feb 2003	15471
Nissan	Micra iii	1.0 16V	Schrägheck	Frontantrieb	Benzin	Jan 2003	Jun 2010	18475
Nissan	Micra iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jan 2003	Jun 2010	17158
Nissan	Micra iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jan 2003	Jun 2010	17180
Nissan	Micra iii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Oct 2002	Jun 2010	123958
Nissan	Micra iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Jan 2003	Jun 2010	17159
Nissan	Micra iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jan 2003	Jun 2010	17181
Nissan	Micra iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Sep 2003	Jun 2010	17327
Nissan	Micra iii	160 SR	Schrägheck	Frontantrieb	Benzin	May 2005	Jun 2010	18973
Nissan	Micra iv	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2015	-	144315
Nissan	Micra iv	1.2 Dig-s	Schrägheck	Frontantrieb	Benzin	Mar 2011	-	144408
Nissan	Micra mk vi	EV	Schrägheck	Frontantrieb	Elektro	Jul 2025	-	162064
Nissan	Micra mk vi	EV	Schrägheck	Frontantrieb	Elektro	Jul 2025	-	162065
Nissan	Micra v	1	Schrägheck	Frontantrieb	Benzin	Dec 2016	-	123835
Nissan	Micra v	1	Schrägheck	Frontantrieb	Benzin	Dec 2016	-	126960
Nissan	Micra v	0.9 Ig-t	Schrägheck	Frontantrieb	Benzin	Dec 2016	-	123826
Nissan	Micra v	1.0 Ig-t	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	144220
Nissan	Micra v	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Dec 2016	-	123836
Nissan	Murano i	3.5 4X4	SUV	Allrad	Benzin	Aug 2003	Sep 2008	18430
Nissan	Murano i	3.5 4X4	SUV	Allrad	Benzin	Nov 2004	Jun 2008	57877
Nissan	Murano ii	2.5 DCI 4X4	SUV	Allrad	Diesel	Jan 2010	Sep 2014	10309
Nissan	Murano ii van	2.5 DCI 4X4	Kasten/SUV	Allrad	Diesel	Mar 2013	Sep 2014	143184
Nissan	Murano ii van	3.5 Cvtc 4X4	Kasten/SUV	Allrad	Benzin	Mar 2013	Sep 2014	143183
Nissan	Navara	2.3 DCI	Pick-up	Heckantrieb	Diesel	Oct 2015	-	115877
Nissan	Navara	2.3 DCI 4X4	Pick-up	Allrad	Diesel	Oct 2015	-	115879
Nissan	Navara	2.3 DCI 4X4	Pick-up	Allrad	Diesel	Oct 2015	-	117805
Nissan	Navara	2.3 DCI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jan 2015	-	118818
Nissan	Navara	2.5 D 4X4	Pick-up	Allrad	Diesel	Nov 2001	-	57648
Nissan	Navara	2.5 DCI	Pick-up	Heckantrieb	Diesel	Jul 2005	-	18794
Nissan	Navara	2.5 DCI	Pick-up	Heckantrieb	Diesel	Oct 2006	-	56223
Nissan	Navara	2.5 DCI 4WD	Pick-up	Allrad	Diesel	Jul 2005	-	18795
Nissan	Navara	2.5 DCI 4WD	Pick-up	Allrad	Diesel	Jan 2007	-	59303
Nissan	Navara	2.5 DCI 4X4	Pick-up	Allrad	Diesel	Jul 2014	-	108566
Nissan	Note	1.2	Großraumlimousine	Frontantrieb	Benzin	Aug 2012	Dec 2016	58980
Nissan	Note	1.2 Dig-s	Großraumlimousine	Frontantrieb	Benzin	Aug 2012	-	58981
Nissan	Note	1.2 LPG	Großraumlimousine	Frontantrieb	LPG	Mar 2015	Dec 2016	111983
Nissan	Note	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	Sep 2010	Jun 2012	11178
Nissan	Note	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	Jun 2013	Dec 2016	35456
Nissan	Np300 pickup	2.5 DCI	Pick-up	Heckantrieb	Diesel	Apr 2008	-	12494
Nissan	Nt400 cabstar	28.12, 32.12, 35.12	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2014	-	119699
Nissan	Nt400 cabstar	35.14, 45.14	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2014	-	119703
Nissan	Nt400 cabstar	35.15, 45.15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2014	-	119704
Nissan	Nv200	1.5 DCI 105	Kasten	Frontantrieb	Diesel	Jul 2010	Oct 2013	157726
Nissan	Nv200	1.5 DCI 110	Kasten	Frontantrieb	Diesel	Apr 2011	-	10937
Nissan	Nv200	1.5 DCI 90	Kasten	Frontantrieb	Diesel	Apr 2011	-	10933
Nissan	Nv200	E-nv	Kasten	Frontantrieb	Elektro	May 2014	-	108646
Nissan	Nv200 / evalia	1.5 DCI 110	Bus	Frontantrieb	Diesel	Apr 2011	-	10934
Nissan	Nv200 / evalia	1.5 DCI 90	Bus	Frontantrieb	Diesel	Apr 2011	-	10930
Nissan	Nv200 / evalia	E-nv	Bus	Frontantrieb	Elektro	Jul 2014	-	108894
Nissan	Nv300	1.6 DCI 125	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	-	126641
Nissan	Nv300	1.6 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	-	126643
Nissan	Nv300	2.0 DCI 110	Kasten	Frontantrieb	Diesel	May 2021	-	145677
Nissan	Nv300	2.0 DCI 150	Kasten	Frontantrieb	Diesel	May 2021	-	145678
Nissan	Nv300 kombi	1.6 DCI 95	Bus	Frontantrieb	Diesel	Sep 2016	-	123799
Nissan	Nv300 kombi	2.0 DCI 110	Bus	Frontantrieb	Diesel	May 2021	-	144946
Nissan	Nv300 kombi	2.0 DCI 150	Bus	Frontantrieb	Diesel	May 2021	-	144947
Nissan	Nv400	DCI 100	Bus	Frontantrieb	Diesel	Nov 2011	Sep 2016	12512
Nissan	Nv400	DCI 100	Kasten	Frontantrieb	Diesel	Nov 2011	Sep 2016	12513
Nissan	Nv400	DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2011	Sep 2016	12540
Nissan	Nv400	DCI 110	Bus	Frontantrieb	Diesel	Jun 2014	Dec 2022	107557
Nissan	Nv400	DCI 110	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2022	107558
Nissan	Nv400	DCI 110	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2014	Dec 2022	107563
Nissan	Nv400	DCI 125	Bus	Frontantrieb	Diesel	Nov 2011	Sep 2016	12514
Nissan	Nv400	DCI 125	Kasten	Frontantrieb	Diesel	Nov 2011	Sep 2016	12516
Nissan	Nv400	DCI 125	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2011	Sep 2016	12550
Nissan	Nv400	DCI 125 RWD	Kasten	Heckantrieb	Diesel	Nov 2011	Sep 2016	12538
Nissan	Nv400	DCI 125 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2011	Sep 2016	12551
Nissan	Nv400	DCI 135	Bus	Frontantrieb	Diesel	Jun 2014	Sep 2016	107559
Nissan	Nv400	DCI 135	Kasten	Frontantrieb	Diesel	Jun 2014	Dec 2022	107560
Nissan	Nv400	DCI 135	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2014	Dec 2022	107564
Nissan	Nv400	DCI 135 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jun 2014	Jun 2016	107567
Nissan	Nv400	DCI 135 RWD	Kasten	Heckantrieb	Diesel	Jun 2014	Sep 2016	107568
Nissan	Nv400	DCI 145	Bus	Frontantrieb	Diesel	Nov 2011	Dec 2022	12518
Nissan	Nv400	DCI 145	Kasten	Frontantrieb	Diesel	Nov 2011	Dec 2022	12524
Nissan	Nv400	DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2011	Dec 2022	12552
Nissan	Nv400	DCI 145 RWD	Kasten	Heckantrieb	Diesel	Nov 2011	Dec 2022	12539
Nissan	Nv400	DCI 145 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2011	Dec 2022	12553
Nissan	Nv400	DCI 150	Bus	Frontantrieb	Diesel	Feb 2014	Dec 2022	108455
Nissan	Nv400	DCI 150	Kasten	Frontantrieb	Diesel	Feb 2014	Dec 2022	108460
Nissan	Nv400	DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2014	Dec 2022	108461
Nissan	Nv400	DCI 150 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 2014	Jun 2016	108457
Nissan	Nv400	DCI 150 RWD	Kasten	Heckantrieb	Diesel	Feb 2014	Sep 2016	108459
Nissan	Nv400	DCI 160	Bus	Frontantrieb	Diesel	Jun 2014	Sep 2016	107561
Nissan	Nv400	DCI 165	Kasten	Frontantrieb	Diesel	Jun 2014	Sep 2016	107562
Nissan	Nv400	DCI 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2014	Jun 2016	107565
Nissan	Nv400	DCI 165 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jun 2014	Dec 2022	107566
Nissan	Nv400	DCI 165 RWD	Kasten	Heckantrieb	Diesel	Jun 2014	Dec 2022	111895
Nissan	Nv400	DCI 170	Bus	Frontantrieb	Diesel	Jul 2015	Dec 2022	116209
Nissan	Pathfinder ii	3.3 V6 4WD	Geländewagen geschlossen	Allrad	Benzin	Mar 1998	Oct 2000	17642
Nissan	Pathfinder ii	3.5 V6 4WD	Geländewagen geschlossen	Allrad	Benzin	Nov 2000	Dec 2004	15703


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个 Ktype 已完成聚类映射，共形成 32 个独立尺寸组。动力、能源和普通配置差异均复用既有物理外廓；Micra IV 因改款前后车长明确变化，保留两个尺寸组。Navara D23、NV200、NV300、NV400 等商用车型优先采用 Nissan 技术手册中的标准车身分支；历史乘用车型采用可追溯规格数据库闭合。([日产][1])

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：32
* 映射引用：全部闭合
* 孤立尺寸组：0
* 固定表头、列数、ID 唯一性、正整数三维、来源及 URL：检查通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106786	106786	Van	I	X76		EU-NISSAN-KUBISTAR-I-VAN-STD-01	MEDIUM		READY
162066	162066	SUV	III		5	EU-NISSAN-LEAF-III-SUV-STD-01	HIGH		READY
162067	162067	SUV	III		5	EU-NISSAN-LEAF-III-SUV-STD-01	HIGH		READY
14716	14716	Sedan	V	A33	4	EU-NISSAN-MAXIMA-QX-V-SEDAN-STD-01	HIGH		READY
14717	14717	Sedan	V	A33	4	EU-NISSAN-MAXIMA-QX-V-SEDAN-STD-01	HIGH		READY
14718	14718	Sedan	V	A33	4	EU-NISSAN-MAXIMA-QX-V-SEDAN-STD-01	HIGH		READY
59989	59989	Sedan	VI	A34	4	EU-NISSAN-MAXIMA-VI-SEDAN-FACELIFT-01	HIGH	Post-Jun-2006 facelift envelope matched to Sep 2006 start.	READY
18970	18970	Convertible	III	K12	2	EU-NISSAN-MICRA-III-CONVERTIBLE-CC-01	HIGH		READY
18972	18972	Convertible	III	K12	2	EU-NISSAN-MICRA-III-CONVERTIBLE-CC-01	HIGH		READY
15470	15470	Hatchback	II	K11	3/5	EU-NISSAN-MICRA-II-HATCHBACK-FACELIFT-01	MEDIUM	2000 facelift envelope used; no Ktype-level pre-facelift split evidence.	READY
15471	15471	Hatchback	II	K11	3/5	EU-NISSAN-MICRA-II-HATCHBACK-FACELIFT-01	MEDIUM	2000 facelift envelope used; no Ktype-level pre-facelift split evidence.	READY
18475	18475	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
17158	17158	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
17180	17180	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
123958	123958	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
17159	17159	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
17181	17181	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
17327	17327	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
18973	18973	Hatchback	III	K12	3/5	EU-NISSAN-MICRA-III-HATCHBACK-STD-01	HIGH		READY
144315	144315	Hatchback	IV	K13	5	EU-NISSAN-MICRA-IV-HATCHBACK-FL-01	HIGH	2013 facelift envelope; length changed.	READY
144408	144408	Hatchback	IV	K13	5	EU-NISSAN-MICRA-IV-HATCHBACK-PREFL-01	HIGH	Pre-facelift K13 envelope.	READY
162064	162064	Hatchback	VI		5	EU-NISSAN-MICRA-VI-HATCHBACK-EV-01	HIGH		READY
162065	162065	Hatchback	VI		5	EU-NISSAN-MICRA-VI-HATCHBACK-EV-01	HIGH		READY
123835	123835	Hatchback	V	K14	5	EU-NISSAN-MICRA-V-HATCHBACK-STD-01	HIGH		READY
126960	126960	Hatchback	V	K14	5	EU-NISSAN-MICRA-V-HATCHBACK-STD-01	HIGH		READY
123826	123826	Hatchback	V	K14	5	EU-NISSAN-MICRA-V-HATCHBACK-STD-01	HIGH		READY
144220	144220	Hatchback	V	K14	5	EU-NISSAN-MICRA-V-HATCHBACK-STD-01	HIGH		READY
123836	123836	Hatchback	V	K14	5	EU-NISSAN-MICRA-V-HATCHBACK-STD-01	HIGH		READY
18430	18430	SUV	I	Z50	5	EU-NISSAN-MURANO-I-SUV-STD-01	HIGH		READY
57877	57877	SUV	I	Z50	5	EU-NISSAN-MURANO-I-SUV-STD-01	HIGH		READY
10309	10309	SUV	II	Z51	5	EU-NISSAN-MURANO-II-SUV-FACELIFT-01	HIGH		READY
143184	143184	Van	II	Z51	5	EU-NISSAN-MURANO-II-SUV-FACELIFT-01	MEDIUM	Commercial conversion; exterior envelope matches Z51 SUV.	READY
143183	143183	Van	II	Z51	5	EU-NISSAN-MURANO-II-SUV-FACELIFT-01	MEDIUM	Commercial conversion; exterior envelope matches Z51 SUV.	READY
115877	115877	Pickup	IV	D23	4	EU-NISSAN-NAVARA-IV-PICKUP-DOUBLECAB-01	HIGH	Standard Double Cab envelope; no Ktype-level cab split evidence.	READY
115879	115879	Pickup	IV	D23	4	EU-NISSAN-NAVARA-IV-PICKUP-DOUBLECAB-01	HIGH	Standard Double Cab envelope; no Ktype-level cab split evidence.	READY
117805	117805	Pickup	IV	D23	4	EU-NISSAN-NAVARA-IV-PICKUP-DOUBLECAB-01	HIGH	Standard Double Cab envelope; no Ktype-level cab split evidence.	READY
118818	118818	Pickup	IV	D23		EU-NISSAN-NAVARA-IV-PICKUP-CHASSIS-KINGCAB-01	HIGH	Standard Chassis King Cab envelope.	READY
57648	57648	Pickup	II	D22	4	EU-NISSAN-NAVARA-II-PICKUP-DOUBLECAB-01	HIGH	Double Cab exterior selected for 2.5 Di 4WD.	READY
18794	18794	Pickup	III	D40	4	EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	Pre-facelift Double Cab envelope.	READY
56223	56223	Pickup	III	D40	4	EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	Pre-facelift Double Cab envelope.	READY
18795	18795	Pickup	III	D40	4	EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	Pre-facelift Double Cab envelope.	READY
59303	59303	Pickup	III	D40	4	EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	Pre-facelift Double Cab envelope.	READY
108566	108566	Pickup	III	D40	4	EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-FL-01	MEDIUM	2014-start Ktype mapped to facelift Double Cab envelope.	READY
58980	58980	MPV	II	E12	5	EU-NISSAN-NOTE-II-MPV-STD-01	HIGH		READY
58981	58981	MPV	II	E12	5	EU-NISSAN-NOTE-II-MPV-STD-01	HIGH		READY
111983	111983	MPV	II	E12	5	EU-NISSAN-NOTE-II-MPV-STD-01	HIGH		READY
11178	11178	MPV	I	E11	5	EU-NISSAN-NOTE-I-MPV-FACELIFT-01	HIGH		READY
35456	35456	MPV	II	E12	5	EU-NISSAN-NOTE-II-MPV-STD-01	HIGH		READY
12494	12494	Pickup	D22	D22	4	EU-NISSAN-NP300-D22-PICKUP-DOUBLECAB-01	MEDIUM	Standard Double Cab envelope; cab subtype not encoded by Ktype.	READY
119699	119699	Pickup	I	F24	2	EU-NISSAN-NT400-I-PICKUP-SWB-01	MEDIUM	Standard completed SWB dropside representative.	READY
119703	119703	Pickup	I	F24	2	EU-NISSAN-NT400-I-PICKUP-MWB-01	MEDIUM	Standard completed MWB dropside representative.	READY
119704	119704	Pickup	I	F24	2	EU-NISSAN-NT400-I-PICKUP-MWB-01	MEDIUM	Standard completed MWB dropside representative.	READY
157726	157726	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
10937	10937	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
10933	10933	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
108646	108646	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
10934	10934	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
10930	10930	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
108894	108894	Van	I	M20		EU-NISSAN-NV200-I-VAN-STD-01	HIGH		READY
126641	126641	Pickup	I	X82		EU-NISSAN-NV300-I-PICKUP-PLATFORM-L2H1-01	MEDIUM	Standard L2H1 platform-cab envelope.	READY
126643	126643	Pickup	I	X82		EU-NISSAN-NV300-I-PICKUP-PLATFORM-L2H1-01	MEDIUM	Standard L2H1 platform-cab envelope.	READY
145677	145677	Van	I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	MEDIUM	Standard L1H1 envelope; no Ktype-level length/roof split evidence.	READY
145678	145678	Van	I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	MEDIUM	Standard L1H1 envelope; no Ktype-level length/roof split evidence.	READY
123799	123799	Van	I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	MEDIUM	Standard L1H1 envelope; no Ktype-level length/roof split evidence.	READY
144946	144946	Van	I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	MEDIUM	Standard L1H1 envelope; no Ktype-level length/roof split evidence.	READY
144947	144947	Van	I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	MEDIUM	Standard L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12512	12512	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12513	12513	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12540	12540	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
107557	107557	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107558	107558	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107563	107563	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
12514	12514	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12516	12516	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12550	12550	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
12538	12538	Van	I	X62		EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	MEDIUM	Standard RWD L3H2 SRW envelope.	READY
12551	12551	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	MEDIUM	Standard RWD L3H1 single-cab TRW chassis envelope.	READY
107559	107559	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107560	107560	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107564	107564	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
107567	107567	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	MEDIUM	Standard RWD L3H1 single-cab TRW chassis envelope.	READY
107568	107568	Van	I	X62		EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	MEDIUM	Standard RWD L3H2 SRW envelope.	READY
12518	12518	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12524	12524	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
12552	12552	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
12539	12539	Van	I	X62		EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	MEDIUM	Standard RWD L3H2 SRW envelope.	READY
12553	12553	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	MEDIUM	Standard RWD L3H1 single-cab TRW chassis envelope.	READY
108455	108455	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
108460	108460	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
108461	108461	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
108457	108457	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	MEDIUM	Standard RWD L3H1 single-cab TRW chassis envelope.	READY
108459	108459	Van	I	X62		EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	MEDIUM	Standard RWD L3H2 SRW envelope.	READY
107561	107561	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107562	107562	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
107565	107565	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	MEDIUM	Standard FWD L2H1 single-cab chassis envelope.	READY
107566	107566	Pickup	I	X62		EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	MEDIUM	Standard RWD L3H1 single-cab TRW chassis envelope.	READY
111895	111895	Van	I	X62		EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	MEDIUM	Standard RWD L3H2 SRW envelope.	READY
116209	116209	Van	I	X62		EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	MEDIUM	Standard FWD L1H1 envelope; no Ktype-level length/roof split evidence.	READY
17642	17642	SUV	II	R50	5	EU-NISSAN-PATHFINDER-II-SUV-PREFL-01	HIGH		READY
15703	15703	SUV	II	R50	5	EU-NISSAN-PATHFINDER-II-SUV-FL-01	HIGH		READY
```

[下载 left18448_11701-11800_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_11701-11800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-KUBISTAR-I-VAN-STD-01	4035	1672	1800	VehicleScore	https://vehiclescore.co.uk/car-dimensions-check/nissan/kubistar
EU-NISSAN-LEAF-III-SUV-STD-01	4350	1810	1550	Nissan official dimensions	https://leaf.nissan.co.uk/dimensions
EU-NISSAN-MAXIMA-QX-V-SEDAN-STD-01	4920	1780	1435	Auto-Data	https://www.auto-data.net/en/nissan-maxima-qx-v-a33-2.5-v6-24v-209hp-671
EU-NISSAN-MAXIMA-VI-SEDAN-FACELIFT-01	4938	1821	1481	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2282390/nissan_maxima_3_5_se.html
EU-NISSAN-MICRA-III-CONVERTIBLE-CC-01	3806	1668	1441	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2199500/nissan_micra_cc_1_6.html
EU-NISSAN-MICRA-II-HATCHBACK-FACELIFT-01	3746	1595	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/2197730/nissan_micra_1_0_comfort_cvt.html
EU-NISSAN-MICRA-III-HATCHBACK-STD-01	3719	1660	1540	Auto-Data	https://www.auto-data.net/en/nissan-micra-k12-160-sr-110hp-712
EU-NISSAN-MICRA-IV-HATCHBACK-PREFL-01	3780	1665	1525	Auto-Data	https://www.auto-data.net/en/nissan-micra-k13-generation-3809
EU-NISSAN-MICRA-IV-HATCHBACK-FL-01	3825	1665	1520	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2200205/nissan_micra_1_2_dig-s.html
EU-NISSAN-MICRA-VI-HATCHBACK-EV-01	3974	1774	1498	Nissan official dimensions	https://micra.nissan.co.uk/dimensions
EU-NISSAN-MICRA-V-HATCHBACK-STD-01	3999	1743	1455	Auto-Data	https://www.auto-data.net/en/nissan-micra-k14-1.5-dci-90hp-27420
EU-NISSAN-MURANO-I-SUV-STD-01	4765	1880	1690	Auto-Data	https://www.auto-data.net/en/nissan-murano-i-z50-3.5-i-v6-248hp-4wd-808
EU-NISSAN-MURANO-II-SUV-FACELIFT-01	4860	1885	1720	Auto-Data	https://www.auto-data.net/en/nissan-murano-ii-z51-facelift-2010-2.5-dci-190hp-4wd-automatic-19089
EU-NISSAN-NAVARA-IV-PICKUP-DOUBLECAB-01	5330	1850	1805	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Navara_UK.pdf
EU-NISSAN-NAVARA-IV-PICKUP-CHASSIS-KINGCAB-01	5225	1790	1790	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Navara_UK.pdf
EU-NISSAN-NAVARA-II-PICKUP-DOUBLECAB-01	5080	1825	1705	Auto-Data	https://www.auto-data.net/en/nissan-pick-up-d22-2.5-di-103hp-4wd-double-cab-17107
EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-PREFL-01	5220	1850	1774	Auto-Data	https://www.auto-data.net/en/nissan-navara-iii-d40-generation-244
EU-NISSAN-NAVARA-III-PICKUP-DOUBLECAB-FL-01	5296	1848	1795	CarExpert	https://www.carexpert.com.au/nissan/navara/2012-st-2-5l-utility-4x4-diesel-manual-jmsmkff520150416
EU-NISSAN-NOTE-II-MPV-STD-01	4100	1695	1535	Auto-Data	https://www.auto-data.net/en/nissan-note-ii-e12-generation-4161
EU-NISSAN-NOTE-I-MPV-FACELIFT-01	4100	1690	1550	Auto-Data	https://www.auto-data.net/en/nissan-note-i-e11-facelift-2010-1.5-dci-90hp-17019
EU-NISSAN-NP300-D22-PICKUP-DOUBLECAB-01	5020	1825	1710	Auto-Data	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-pickup-double-cab-899
EU-NISSAN-NT400-I-PICKUP-SWB-01	5188	1870	2093	VehicleScore	https://vehiclescore.co.uk/car-dimensions-check/nissan/nt400%20cabstar
EU-NISSAN-NT400-I-PICKUP-MWB-01	5848	1870	2093	VehicleScore	https://vehiclescore.co.uk/car-dimensions-check/nissan/nt400%20cabstar
EU-NISSAN-NV200-I-VAN-STD-01	4400	1695	1860	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV200_combi_UK.pdf
EU-NISSAN-NV300-I-PICKUP-PLATFORM-L2H1-01	5399	1956	1971	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-VAN-L1H1-01	4999	1956	1971	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	5048	2070	2303	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-VAN-RWD-L3H2-01	6198	2070	2527	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-PICKUP-FWD-L2H1-01	5643	2070	2265	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-PICKUP-RWD-L3H1-01	6193	2070	2283	Nissan official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-PATHFINDER-II-SUV-PREFL-01	4530	1840	1750	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930
EU-NISSAN-PATHFINDER-II-SUV-FL-01	4640	1820	1750	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-ii-3.5-i-v6-24v-220hp-4wd-931
```

[下载 left18448_11701-11800_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_11701-11800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Navara_UK.pdf "https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Navara_UK.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3131 行）
- 累计尺寸组：dimension_groups_final.tsv（970 行）

