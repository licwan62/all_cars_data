# 任务：left18448 第 15801-15900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0159__ec837699


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15801-15900 行

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
left18448 第 15801-15900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15801-15900_ktype_dimension_mapping_final.tsv
- left18448_15801-15900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Suzuki	Grand vitara i	2.0 4X4	Geländewagen geschlossen	Allrad	Benzin	Mar 1998	Jul 2003	11517
Suzuki	Grand vitara i	2.0 4X4	Geländewagen offen	Allrad	Benzin	Mar 1998	Jul 2003	115783
Suzuki	Grand vitara i	2.0 HDI 110 16V 4X4	Geländewagen geschlossen	Allrad	Diesel	Jul 2001	Sep 2005	15968
Suzuki	Grand vitara i	2.0 HDI 110 4X4	Geländewagen geschlossen	Allrad	Diesel	Feb 2001	Dec 2003	34976
Suzuki	Grand vitara i	2.0 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	Mar 1998	Jul 2003	11518
Suzuki	Grand vitara i	2.5 V6 24V 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 1998	Jul 2003	11239
Suzuki	Grand vitara i	2.5 V6 24V 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 2001	Jul 2003	18287
Suzuki	Grand vitara i	2.7 4X4	Geländewagen geschlossen	Allrad	Benzin	Sep 2001	Jul 2003	16550
Suzuki	Grand vitara i	2.7 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 2003	Jul 2003	17763
Suzuki	Grand vitara ii	2.7 Allrad	Geländewagen geschlossen	Allrad	Benzin	Jan 2007	Dec 2008	127378
Suzuki	Ignis i	1.3	Schrägheck	Frontantrieb	Benzin	Oct 2000	Sep 2003	15523
Suzuki	Ignis i	1.3 4WD	Schrägheck	Allrad	Benzin	Oct 2000	Sep 2003	15524
Suzuki	Ignis i	1.5 Sport	Schrägheck	Frontantrieb	Benzin	Dec 2003	Dec 2005	17870
Suzuki	Ignis ii	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2003	-	17698
Suzuki	Ignis ii	1.5	Schrägheck	Frontantrieb	Benzin	Sep 2003	-	17699
Suzuki	Ignis ii	1.3 Ddis	Schrägheck	Frontantrieb	Diesel	Sep 2003	-	17701
Suzuki	Ignis ii	1.5 4X4	Schrägheck	Allrad	Benzin	Sep 2003	-	17700
Suzuki	Jimny	1.3 16V	Geländewagen geschlossen	Heckantrieb	Benzin	Sep 1998	-	10319
Suzuki	Jimny	1.3 16V	Geländewagen geschlossen	Heckantrieb	Benzin	Feb 2001	-	16094
Suzuki	Jimny	1.3 16V 4WD	Geländewagen geschlossen	Allrad	Benzin	Sep 1998	-	10321
Suzuki	Jimny	1.3 16V 4WD	Geländewagen geschlossen	Allrad	Benzin	Feb 2001	-	16095
Suzuki	Jimny	1.3 4WD	Geländewagen geschlossen	Allrad	Benzin	May 2014	-	106326
Suzuki	Jimny	1.5 Ddis 4WD	Geländewagen geschlossen	Allrad	Diesel	Dec 2003	-	18141
Suzuki	Kizashi	2.4	Stufenheck	Frontantrieb	Benzin	Oct 2010	-	34970
Suzuki	Kizashi	2.4 4X4	Stufenheck	Allrad	Benzin	Oct 2010	-	34971
Suzuki	Liana	1.3	Schrägheck	Frontantrieb	Benzin	Jul 2001	Dec 2007	16074
Suzuki	Liana	1.3	Stufenheck	Frontantrieb	Benzin	Mar 2002	-	16635
Suzuki	Liana	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2001	Dec 2007	16075
Suzuki	Liana	1.6	Stufenheck	Frontantrieb	Benzin	Mar 2002	-	16646
Suzuki	Liana	1.4 Ddis	Stufenheck	Frontantrieb	Diesel	Apr 2004	-	18606
Suzuki	Liana	1.4 Ddis	Schrägheck	Frontantrieb	Diesel	Apr 2004	Dec 2007	18607
Suzuki	Liana	1.6 4WD	Schrägheck	Allrad	Benzin	Jul 2001	Dec 2007	16076
Suzuki	Liana	1.6 4WD	Stufenheck	Allrad	Benzin	Mar 2002	-	16647
Suzuki	Liana	1.6 4WD	Stufenheck	Allrad	Benzin	Apr 2002	-	17302
Suzuki	Liana	1.6 4WD	Schrägheck	Allrad	Benzin	Apr 2002	Dec 2007	17304
Suzuki	Liana	1.6 I	Stufenheck	Frontantrieb	Benzin	Apr 2002	-	17301
Suzuki	Liana	1.6 I	Schrägheck	Frontantrieb	Benzin	Apr 2002	Dec 2007	17303
Suzuki	Maruti	800	Schrägheck	Frontantrieb	Benzin	Feb 1988	Dec 1994	110770
Suzuki	Samurai	1.9 TD Allrad	Geländewagen geschlossen	Allrad	Diesel	Nov 1998	Dec 2004	11247
Suzuki	S-Cross	1.4 Smart Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2022	-	146488
Suzuki	S-Cross	1.4 Smart Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802158
Suzuki	S-Cross	1.4 Smart Hybrid Allgrip	SUV	Allrad	Benzin/Elektro	Jan 2022	-	146236
Suzuki	S-Cross	1.4 Smart Hybrid Allgrip	SUV	Allrad	Benzin/Elektro	Jul 2025	-	802159
Suzuki	S-Cross	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2022	-	148368
Suzuki	S-Cross	1.5 Hybrid Allgrip	SUV	Allrad	Benzin/Elektro	Jan 2022	-	148369
Suzuki	Splash	1	Schrägheck	Frontantrieb	Benzin	Jun 2011	-	12055
Suzuki	Splash	1.2 VVT	Schrägheck	Frontantrieb	Benzin	Jun 2011	-	12061
Suzuki	Swace	1.8 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Oct 2020	-	143239
Suzuki	Swace	1.8 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Mar 2023	-	152749
Suzuki	Swift ii	1	Stufenheck	Frontantrieb	Benzin	Jan 1994	May 2001	123758
Suzuki	Swift ii	1.3	Schrägheck	Frontantrieb	Benzin	Mar 1989	Dec 1997	49124
Suzuki	Swift ii	1.3	Stufenheck	Frontantrieb	Benzin	Sep 1989	Dec 1994	49129
Suzuki	Swift iii	1.3	Schrägheck	Frontantrieb	Benzin	Feb 2005	Jun 2012	19094
Suzuki	Swift iii	1.5	Schrägheck	Frontantrieb	Benzin	Feb 2005	Dec 2011	19093
Suzuki	Swift iv	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2012	Apr 2017	11746
Suzuki	Swift v	1	Schrägheck	Frontantrieb	Benzin	Apr 2017	-	126919
Suzuki	Swift v	1.2	Schrägheck	Frontantrieb	Benzin	Apr 2017	-	126921
Suzuki	Swift v	1.0 Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2017	-	126920
Suzuki	Swift v	1.2 Allgrip	Schrägheck	Allrad	Benzin	Apr 2017	-	126924
Suzuki	Swift v	1.2 Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2017	-	126922
Suzuki	Swift v	1.2 Shvs Allgrip	Schrägheck	Allrad	Benzin/Elektro	Apr 2017	-	126923
Suzuki	Swift vi	1.2 VVT Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Dec 2023	-	157116
Suzuki	Swift vi	1.2 VVT Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2024	-	802410
Suzuki	Swift vi	1.2 VVT Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	Dec 2023	-	157117
Suzuki	Swift vi	1.2 VVT Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	Nov 2024	-	802412
Suzuki	Sx4 / classic	1.5 VVT 4X4	Schrägheck	Allrad	Benzin	Jul 2010	-	108353
Suzuki	Sx4 / classic	1.5 Vvti	Schrägheck	Frontantrieb	Benzin	Jul 2007	Dec 2015	124432
Suzuki	Sx4 s-Cross	1	Schrägheck	Frontantrieb	Benzin	Aug 2016	Jun 2022	121781
Suzuki	Sx4 s-Cross	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2013	Jun 2022	100878
Suzuki	Sx4 s-Cross	1.0 Allgrip	Schrägheck	Allrad	Benzin	Aug 2016	Jun 2022	121970
Suzuki	Sx4 s-Cross	1.4 T	Schrägheck	Frontantrieb	Benzin	Aug 2016	Jun 2022	121586
Suzuki	Sx4 s-Cross	1.4 T Allgrip	Schrägheck	Allrad	Benzin	Aug 2016	Jun 2022	121587
Suzuki	Sx4 s-Cross	1.6 Allgrip	Schrägheck	Allrad	Benzin	Aug 2013	Jun 2022	12928
Suzuki	Sx4 s-Cross	1.6 Allgrip	Schrägheck	Allrad	Benzin	Dec 2013	Jun 2022	100880
Suzuki	Vitara	1.6	Geländewagen geschlossen	Allrad	Benzin	Feb 1991	Mar 1998	101074
Suzuki	Vitara	1.6	SUV	Frontantrieb	Benzin	Feb 2015	-	110038
Suzuki	Vitara	1.6	Geländewagen offen	Allrad	Benzin	Jan 1990	Dec 1993	117863
Suzuki	Vitara	1.4 Hybrid	SUV	Allrad	Benzin/Elektro/Biogas	Aug 2023	-	158254
Suzuki	Vitara	1.4 Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802160
Suzuki	Vitara	1.4 Mild Hybrid Allgrip	SUV	Allrad	Benzin/Elektro	Jul 2025	-	802161
Suzuki	Vitara	1.4 T	SUV	Frontantrieb	Benzin	Sep 2015	-	116537
Suzuki	Vitara	1.4 T Allgrip	SUV	Allrad	Benzin	Sep 2015	-	116538
Suzuki	Vitara	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2022	-	146491
Suzuki	Vitara	1.5 Hybrid Allgrip	SUV	Allrad	Benzin/Elektro	Jan 2022	-	146490
Suzuki	Vitara	1.5 Hybrid Allgrip	SUV	Allrad	Benzin/Elektro/Biogas	Aug 2023	-	158256
Suzuki	Vitara	1.6 Allgrip	SUV	Allrad	Benzin	Feb 2015	-	110039
Suzuki	Vitara	1.6 Allgrip	SUV	Allrad	Benzin	May 2015	-	121230
Suzuki	Vitara	1.6 Allrad	Geländewagen geschlossen	Allrad	Benzin	Oct 1988	Dec 1998	109831
Suzuki	Vitara	1.6 Ddis	SUV	Frontantrieb	Diesel	Feb 2015	-	110040
Suzuki	Vitara	1.6 Ddis Allgrip	SUV	Allrad	Diesel	Feb 2015	-	110041
Suzuki	Vitara	1.6 I 16V	Geländewagen geschlossen	Heckantrieb	Benzin	Jan 1990	Dec 1998	127412
Suzuki	Vitara	1.9 D	Geländewagen offen	Allrad	Diesel	Aug 1996	Mar 1999	7888
Suzuki	Vitara	1.9 D	Geländewagen offen	Allrad	Diesel	Jan 1995	Mar 1998	16115
Suzuki	Vitara	2.0 HDI	Geländewagen offen	Allrad	Diesel	Jan 2002	Dec 2005	54957
Suzuki	Vitara	2.0 TD Allrad	Geländewagen geschlossen	Allrad	Diesel	Dec 1994	Mar 1998	5680
Suzuki	Vitara	HDI	Geländewagen geschlossen	Allrad	Diesel	Dec 2003	Dec 2005	54956
Suzuki	Wagon r+	1.2	Schrägheck	Frontantrieb	Benzin	Feb 1998	May 2000	10171
Suzuki	Wagon r+	1.3	Schrägheck	Frontantrieb	Benzin	May 2000	Dec 2004	14791
Suzuki	Wagon r+	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2003	Aug 2006	17764
Suzuki	Wagon r+	1.2 4WD	Schrägheck	Allrad	Benzin	Feb 1998	May 2000	10170


--- Round 1 / 首次发送 ---
## 更新点

完成 Suzuki 批次物理外廓归并。老款 Vitara 的 Ktype `101074`、`109831`、`127412` 按已确认的 3 门短轴与 5 门长轴拆分；Jimny、## 更新点

完成 SuzukiLiana、SX4、Swift、现代 Vitara ([AUTODOC][1])urn706377search1

## 进度

* 输入 Ktype：100
* 最终映射：103 行
* DIMENSION_GROUP：42 个
* PENDING：0
* 映射引用闭合：通过
* `id`、`DIMENSION_GROUP_ID` 唯一性：通过
* 三维、来源、URL 非空检查：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11517	11517	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
115783	115783	Convertible	I	FT	3	EU-SUZUKI-GRAND-VITARA-I-CONVERTIBLE-3DR-01	HIGH		READY
15968	15968	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
34976	34976	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
11518	11518	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
11239	11239	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
18287	18287	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
16550	16550	SUV	I	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	HIGH	2.7 对应 XL-7 长轴外廓	READY
17763	17763	SUV	I	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	HIGH	2.7 对应 XL-7 长轴外廓	READY
127378	127378	SUV	II	JT	5	EU-SUZUKI-GRAND-VITARA-II-SUV-5DR-01	HIGH		READY
15523	15523	Hatchback	I	FH	5	EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	HIGH		READY
15524	15524	Hatchback	I	FH	5	EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	HIGH		READY
17870	17870	Hatchback	I	FH	3	EU-SUZUKI-IGNIS-I-HATCHBACK-SPORT-01	HIGH		READY
17698	17698	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17699	17699	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17701	17701	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17700	17700	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
10319	10319	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
16094	16094	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
10321	10321	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
16095	16095	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
106326	106326	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT2012-01	HIGH	2012 改款长度分支	READY
18141	18141	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
34970	34970	Sedan	I	FR	4	EU-SUZUKI-KIZASHI-I-SEDAN-01	HIGH		READY
34971	34971	Sedan	I	FR	4	EU-SUZUKI-KIZASHI-I-SEDAN-01	HIGH		READY
16074	16074	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16635	16635	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
16075	16075	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16646	16646	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
18606	18606	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
18607	18607	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-FACELIFT-01	HIGH	2004 改款两厢外廓	READY
16076	16076	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16647	16647	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17302	17302	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17304	17304	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
17301	17301	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17303	17303	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
110770	110770	Hatchback	I			EU-SUZUKI-MARUTI-800-HATCHBACK-01	MEDIUM		READY
11247	11247	SUV	I	SJ	3	EU-SUZUKI-SAMURAI-I-SUV-LWB-HARDTOP-01	HIGH	长轴硬顶外廓	READY
146488	146488	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
802158	802158	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
146236	146236	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
802159	802159	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
148368	148368	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
148369	148369	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
12055	12055	Hatchback	I	EX	5	EU-SUZUKI-SPLASH-I-HATCHBACK-01	HIGH		READY
12061	12061	Hatchback	I	EX	5	EU-SUZUKI-SPLASH-I-HATCHBACK-01	HIGH		READY
143239	143239	Wagon	I	E210	5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
152749	152749	Wagon	I	E210	5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
123758	123758	Sedan	II	AH/AJ	4	EU-SUZUKI-SWIFT-II-SEDAN-01	HIGH		READY
49124	49124	Hatchback	II	EA/MA		EU-SUZUKI-SWIFT-II-HATCHBACK-01	MEDIUM		READY
49129	49129	Sedan	II	AH/AJ	4	EU-SUZUKI-SWIFT-II-SEDAN-01	HIGH		READY
19094	19094	Hatchback	III	MZ/EZ	5	EU-SUZUKI-SWIFT-III-HATCHBACK-01	HIGH		READY
19093	19093	Hatchback	III	MZ/EZ	5	EU-SUZUKI-SWIFT-III-HATCHBACK-01	HIGH		READY
11746	11746	Hatchback	IV	FZ/NZ	5	EU-SUZUKI-SWIFT-IV-HATCHBACK-SPORT-01	HIGH		READY
126919	126919	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126921	126921	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126920	126920	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126924	126924	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
126922	126922	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126923	126923	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
157116	157116	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	HIGH		READY
802410	802410	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	HIGH		READY
157117	157117	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
802412	802412	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
108353	108353	Hatchback	I	EY/GY	5	EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	HIGH	2009 改款外廓	READY
124432	124432	Hatchback	I	EY/GY	5	EU-SUZUKI-SX4-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
121781	121781	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
100878	100878	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
121970	121970	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
121586	121586	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
121587	121587	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
12928	12928	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
100880	100880	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
101074_3dr	101074	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
101074_5dr	101074	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
110038	110038	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
117863	117863	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-3DR-01	HIGH		READY
158254	158254	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
802160	802160	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-FWD-01	HIGH	2024 改款前驱外廓	READY
802161	802161	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-ALLGRIP-01	HIGH	2024 改款 AllGrip 车高分支	READY
116537	116537	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
116538	116538	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
146491	146491	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
146490	146490	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
158256	158256	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
110039	110039	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
121230	121230	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
109831_3dr	109831	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
109831_5dr	109831	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
110040	110040	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
110041	110041	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
127412_3dr	127412	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
127412_5dr	127412	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
7888	7888	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	HIGH		READY
16115	16115	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	HIGH		READY
54957	54957	Convertible	I	ET	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-HDI-3DR-01	MEDIUM	HDi 敞篷短轴外廓	READY
5680	5680	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-WIDEBODY-01	HIGH	宽体五门外廓	READY
54956	54956	SUV	I	ET	3	EU-SUZUKI-VITARA-I-SUV-HDI-3DR-01	MEDIUM	HDi 封闭式短轴硬顶外廓	READY
10171	10171	Hatchback	I	EM	5	EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	HIGH		READY
14791	14791	Hatchback	II	MM	5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
17764	17764	Hatchback	II	MM	5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
10170	10170	Hatchback	I	EM	5	EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	HIGH		READY
```

[下载 left18448_15801-15900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15801-15900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	4215	1780	1740	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-generation-3734
EU-SUZUKI-GRAND-VITARA-I-CONVERTIBLE-3DR-01	3865	1710	1690	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-cabrio-generation-3735
EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	4700	1780	1740	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-xl-7-ht-generation-3736
EU-SUZUKI-GRAND-VITARA-II-SUV-5DR-01	4575	1810	1695	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-2.7-v6-185hp-4wd-45647
EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	3615	1595	1540	Auto-Data	https://www.auto-data.net/en/suzuki-ignis-i-fh-1.3-i-16v-5-dr-83hp-4wd-16416
EU-SUZUKI-IGNIS-I-HATCHBACK-SPORT-01	3620	1650	1525	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/3389120/suzuki_ignis_sport.html
EU-SUZUKI-IGNIS-II-HATCHBACK-01	3770	1605	1565	Auto-Data	https://www.auto-data.net/en/suzuki-ignis-i-mh-generation-5258
EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	3645	1600	1705	Auto-Data	https://www.auto-data.net/en/suzuki-jimny-iii-generation-3698
EU-SUZUKI-JIMNY-III-SUV-FACELIFT2012-01	3675	1600	1705	Auto-Data	https://www.auto-data.net/en/suzuki-jimny-iii-facelift-2012-generation-4518
EU-SUZUKI-KIZASHI-I-SEDAN-01	4650	1820	1470	Auto-Data	https://www.auto-data.net/en/suzuki-kizashi-2.4-178hp-21698
EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	4280	1720	1550	Auto-Data	https://www.auto-data.net/en/suzuki-liana-wagon-i-generation-3715
EU-SUZUKI-LIANA-I-HATCHBACK-FACELIFT-01	4230	1690	1550	Auto-Data	https://www.auto-data.net/en/suzuki-liana-wagon-i-facelift-2004-generation-3713
EU-SUZUKI-LIANA-I-SEDAN-01	4350	1690	1545	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/3390425/suzuki_liana_sedan_1_6.html
EU-SUZUKI-MARUTI-800-HATCHBACK-01	3300	1415	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3326870/suzuki_alto_gl_3-door_automatic.html
EU-SUZUKI-SAMURAI-I-SUV-LWB-HARDTOP-01	4040	1530	1690	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Suzuki/41701/Suzuki-Samurai-LWB-Hard-Top-19TD.html
EU-SUZUKI-S-CROSS-II-SUV-01	4305	1785	1585	Suzuki official	https://www.suzuki.com.au/vehicles/suv/s-cross/specifications/
EU-SUZUKI-SPLASH-I-HATCHBACK-01	3715	1680	1590	Auto-Data	https://www.auto-data.net/en/suzuki-splash-1.0-65hp-16488
EU-SUZUKI-SWACE-I-WAGON-01	4655	1790	1460	Auto-Data	https://www.auto-data.net/en/suzuki-swace-model-2824
EU-SUZUKI-SWIFT-II-SEDAN-01	4095	1590	1380	Drive.Place	https://suzuki.drive.place/swift/ii/group_sedan/271005
EU-SUZUKI-SWIFT-II-HATCHBACK-01	3745	1590	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3334535/suzuki_swift_1_3_gs_3-door.html
EU-SUZUKI-SWIFT-III-HATCHBACK-01	3695	1690	1500	Auto-Data	https://www.auto-data.net/en/suzuki-swift-iv-1.3i-92hp-4wd-16524
EU-SUZUKI-SWIFT-IV-HATCHBACK-SPORT-01	3890	1695	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3405950/suzuki_swift_sport.html
EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	3840	1735	1480	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-1.0-112hp-shvs-29940
EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	3840	1735	1505	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-1.2-dualjet-90hp-allgrip-29980
EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	3860	1735	1495	Suzuki official	https://www.globalsuzuki.com/pan-europeantestdrive2403/swift/presskit/pdf/swift_pressrelease_en.pdf
EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	3860	1735	1520	Suzuki official	https://www.globalsuzuki.com/pan-europeantestdrive2403/swift/presskit/pdf/swift_pressrelease_en.pdf
EU-SUZUKI-SX4-I-HATCHBACK-PREFACELIFT-01	4135	1755	1605	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-generation-3729
EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	4150	1755	1620	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-facelift-2009-generation-3834
EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	4300	1765	1575	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-generation-4185
EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	4300	1785	1580	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-facelift-2016-generation-5088
EU-SUZUKI-VITARA-I-SUV-3DR-01	3620	1630	1665	CarsGuide	https://www.carsguide.com.au/suzuki/vitara/car-dimensions/1995
EU-SUZUKI-VITARA-I-SUV-5DR-01	4030	1635	1700	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3349655/suzuki_vitara_1_6i_jlx_16v_5-door.html
EU-SUZUKI-VITARA-I-CONVERTIBLE-3DR-01	3620	1631	1669	Autoevolution	https://www.autoevolution.com/cars/suzuki-vitara-cabrio-1989.html
EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	3630	1670	1630	Auto-Data	https://www.auto-data.net/en/suzuki-vitara-cabrio-et-ta-1.9-d-et-75hp-16440
EU-SUZUKI-VITARA-I-CONVERTIBLE-HDI-3DR-01	3630	1635	1700	Autokoo	https://www.autokoo.com/fiche-technique/suzuki/vitara/cabriolet-20-hdi-jlx/30512720020201
EU-SUZUKI-VITARA-I-SUV-5DR-WIDEBODY-01	4120	1700	1700	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Suzuki/5895/Suzuki-Vitara-Wagon-20-Turbo-D.html
EU-SUZUKI-VITARA-I-SUV-HDI-3DR-01	3720	1635	1700	Autogidas	https://autogidas.lt/en/auto-katalogas/suzuki/vitara/2.0-hdi-2001-2003-k72673
EU-SUZUKI-VITARA-IV-SUV-2015-01	4175	1775	1610	CarsGuide	https://www.carsguide.com.au/suzuki/vitara/car-dimensions/2024
EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-FWD-01	4185	1775	1600	Suzuki official	https://www.suzuki.com.au/vehicles/suv/vitara-hybrid/specifications/
EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-ALLGRIP-01	4185	1775	1595	Suzuki official	https://www.suzuki.com.au/vehicles/suv/vitara-hybrid/specifications/
EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	3410	1575	1700	Auto-Data	https://www.auto-data.net/en/suzuki-wagon-r-model-1902
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3575	1620	1705	Auto-Data	https://www.auto-data.net/en/suzuki-wagon-r-model-1902
```

[下载 left18448_15801-15900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15801-15900_dimension_groups_final.ts)

推进信号：COMPLETE

[1]: https://www.autodoc.parts/car-parts/coil-springs-10213/suzuki/vitara/vitara-et-ta/101074-1-6-se-416?utm_source=chatgpt.com "Suzuki Vitara mk1 1.6 Springs (95 hp Petrol G16B)"


--- 发送 / 完成信号纠偏 / Round 2 ---
你刚才给了完成信号，但当前回复缺少完整 Ktype 映射 TSV、完整 DIMENSION_GROUP TSV，存在未引用/缺失/不完整的尺寸组，或仍有数据缺失。请补齐所有必需表；未完成时输出“推进信号：CONTINUE”，确认全部表完整且映射闭合后才输出“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15801-15900_ktype_dimension_mapping_final.tsv
- left18448_15801-15900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

已重新读取并机械校验两份最终文件，未重新展开车型研究。

## 进度

* 输入 Ktype：100 个
* 最终 Ktype 映射：103 行
* DIMENSION_GROUP：42 行
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 缺失引用：0
* 孤立尺寸组：0
* `PENDING`：0
* 三维、来源、URL 空值：0
* 两个指定文件：已创建

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11517	11517	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
115783	115783	Convertible	I	FT	3	EU-SUZUKI-GRAND-VITARA-I-CONVERTIBLE-3DR-01	HIGH		READY
15968	15968	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
34976	34976	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
11518	11518	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
11239	11239	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
18287	18287	SUV	I	FT/GT	5	EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	HIGH		READY
16550	16550	SUV	I	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	HIGH	2.7 对应 XL-7 长轴外廓	READY
17763	17763	SUV	I	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	HIGH	2.7 对应 XL-7 长轴外廓	READY
127378	127378	SUV	II	JT	5	EU-SUZUKI-GRAND-VITARA-II-SUV-5DR-01	HIGH		READY
15523	15523	Hatchback	I	FH	5	EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	HIGH		READY
15524	15524	Hatchback	I	FH	5	EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	HIGH		READY
17870	17870	Hatchback	I	FH	3	EU-SUZUKI-IGNIS-I-HATCHBACK-SPORT-01	HIGH		READY
17698	17698	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17699	17699	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17701	17701	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
17700	17700	Hatchback	II	MH	5	EU-SUZUKI-IGNIS-II-HATCHBACK-01	HIGH		READY
10319	10319	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
16094	16094	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
10321	10321	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
16095	16095	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
106326	106326	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT2012-01	HIGH	2012 改款长度分支	READY
18141	18141	SUV	III	FJ	3	EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	HIGH		READY
34970	34970	Sedan	I	FR	4	EU-SUZUKI-KIZASHI-I-SEDAN-01	HIGH		READY
34971	34971	Sedan	I	FR	4	EU-SUZUKI-KIZASHI-I-SEDAN-01	HIGH		READY
16074	16074	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16635	16635	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
16075	16075	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16646	16646	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
18606	18606	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
18607	18607	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-FACELIFT-01	HIGH	2004 改款两厢外廓	READY
16076	16076	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
16647	16647	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17302	17302	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17304	17304	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
17301	17301	Sedan	I	ER	4	EU-SUZUKI-LIANA-I-SEDAN-01	HIGH		READY
17303	17303	Hatchback	I	ER	5	EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
110770	110770	Hatchback	I			EU-SUZUKI-MARUTI-800-HATCHBACK-01	MEDIUM		READY
11247	11247	SUV	I	SJ	3	EU-SUZUKI-SAMURAI-I-SUV-LWB-HARDTOP-01	HIGH	长轴硬顶外廓	READY
146488	146488	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
802158	802158	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
146236	146236	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
802159	802159	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
148368	148368	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
148369	148369	SUV	II	JY	5	EU-SUZUKI-S-CROSS-II-SUV-01	HIGH		READY
12055	12055	Hatchback	I	EX	5	EU-SUZUKI-SPLASH-I-HATCHBACK-01	HIGH		READY
12061	12061	Hatchback	I	EX	5	EU-SUZUKI-SPLASH-I-HATCHBACK-01	HIGH		READY
143239	143239	Wagon	I	E210	5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
152749	152749	Wagon	I	E210	5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
123758	123758	Sedan	II	AH/AJ	4	EU-SUZUKI-SWIFT-II-SEDAN-01	HIGH		READY
49124	49124	Hatchback	II	EA/MA		EU-SUZUKI-SWIFT-II-HATCHBACK-01	MEDIUM		READY
49129	49129	Sedan	II	AH/AJ	4	EU-SUZUKI-SWIFT-II-SEDAN-01	HIGH		READY
19094	19094	Hatchback	III	MZ/EZ	5	EU-SUZUKI-SWIFT-III-HATCHBACK-01	HIGH		READY
19093	19093	Hatchback	III	MZ/EZ	5	EU-SUZUKI-SWIFT-III-HATCHBACK-01	HIGH		READY
11746	11746	Hatchback	IV	FZ/NZ	5	EU-SUZUKI-SWIFT-IV-HATCHBACK-SPORT-01	HIGH		READY
126919	126919	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126921	126921	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126920	126920	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126924	126924	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
126922	126922	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	HIGH		READY
126923	126923	Hatchback	V	AZ	5	EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
157116	157116	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	HIGH		READY
802410	802410	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	HIGH		READY
157117	157117	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
802412	802412	Hatchback	VI		5	EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	HIGH	AllGrip 标准车高分支	READY
108353	108353	Hatchback	I	EY/GY	5	EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	HIGH	2009 改款外廓	READY
124432	124432	Hatchback	I	EY/GY	5	EU-SUZUKI-SX4-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
121781	121781	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
100878	100878	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
121970	121970	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
121586	121586	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
121587	121587	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	HIGH	2016 改款宽度分支	READY
12928	12928	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
100880	100880	Hatchback	I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	HIGH		READY
101074_3dr	101074	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
101074_5dr	101074	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
110038	110038	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
117863	117863	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-3DR-01	HIGH		READY
158254	158254	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
802160	802160	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-FWD-01	HIGH	2024 改款前驱外廓	READY
802161	802161	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-ALLGRIP-01	HIGH	2024 改款 AllGrip 车高分支	READY
116537	116537	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
116538	116538	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
146491	146491	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
146490	146490	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
158256	158256	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
110039	110039	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
121230	121230	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
109831_3dr	109831	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
109831_5dr	109831	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
110040	110040	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
110041	110041	SUV	IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-2015-01	HIGH		READY
127412_3dr	127412	SUV	I	ET/TA	3	EU-SUZUKI-VITARA-I-SUV-3DR-01	MEDIUM	同一 Ktype 覆盖 3 门短轴外廓	READY
127412_5dr	127412	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-01	MEDIUM	同一 Ktype 覆盖 5 门长轴外廓	READY
7888	7888	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	HIGH		READY
16115	16115	Convertible	I	ET/TA	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	HIGH		READY
54957	54957	Convertible	I	ET	3	EU-SUZUKI-VITARA-I-CONVERTIBLE-HDI-3DR-01	MEDIUM	HDi 敞篷短轴外廓	READY
5680	5680	SUV	I	ET/TA	5	EU-SUZUKI-VITARA-I-SUV-5DR-WIDEBODY-01	HIGH	宽体五门外廓	READY
54956	54956	SUV	I	ET	3	EU-SUZUKI-VITARA-I-SUV-HDI-3DR-01	MEDIUM	HDi 封闭式短轴硬顶外廓	READY
10171	10171	Hatchback	I	EM	5	EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	HIGH		READY
14791	14791	Hatchback	II	MM	5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
17764	17764	Hatchback	II	MM	5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
10170	10170	Hatchback	I	EM	5	EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	HIGH		READY
```

[下载 left18448_15801-15900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15801-15900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-GRAND-VITARA-I-SUV-5DR-01	4215	1780	1740	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-generation-3734
EU-SUZUKI-GRAND-VITARA-I-CONVERTIBLE-3DR-01	3865	1710	1690	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-cabrio-generation-3735
EU-SUZUKI-GRAND-VITARA-I-XL7-SUV-5DR-01	4700	1780	1740	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-xl-7-ht-generation-3736
EU-SUZUKI-GRAND-VITARA-II-SUV-5DR-01	4575	1810	1695	Auto-Data	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-2.7-v6-185hp-4wd-45647
EU-SUZUKI-IGNIS-I-HATCHBACK-STANDARD-01	3615	1595	1540	Auto-Data	https://www.auto-data.net/en/suzuki-ignis-i-fh-1.3-i-16v-5-dr-83hp-4wd-16416
EU-SUZUKI-IGNIS-I-HATCHBACK-SPORT-01	3620	1650	1525	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/3389120/suzuki_ignis_sport.html
EU-SUZUKI-IGNIS-II-HATCHBACK-01	3770	1605	1565	Auto-Data	https://www.auto-data.net/en/suzuki-ignis-i-mh-generation-5258
EU-SUZUKI-JIMNY-III-SUV-PREFACELIFT-01	3645	1600	1705	Auto-Data	https://www.auto-data.net/en/suzuki-jimny-iii-generation-3698
EU-SUZUKI-JIMNY-III-SUV-FACELIFT2012-01	3675	1600	1705	Auto-Data	https://www.auto-data.net/en/suzuki-jimny-iii-facelift-2012-generation-4518
EU-SUZUKI-KIZASHI-I-SEDAN-01	4650	1820	1470	Auto-Data	https://www.auto-data.net/en/suzuki-kizashi-2.4-178hp-21698
EU-SUZUKI-LIANA-I-HATCHBACK-PREFACELIFT-01	4280	1720	1550	Auto-Data	https://www.auto-data.net/en/suzuki-liana-wagon-i-generation-3715
EU-SUZUKI-LIANA-I-HATCHBACK-FACELIFT-01	4230	1690	1550	Auto-Data	https://www.auto-data.net/en/suzuki-liana-wagon-i-facelift-2004-generation-3713
EU-SUZUKI-LIANA-I-SEDAN-01	4350	1690	1545	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/3390425/suzuki_liana_sedan_1_6.html
EU-SUZUKI-MARUTI-800-HATCHBACK-01	3300	1415	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3326870/suzuki_alto_gl_3-door_automatic.html
EU-SUZUKI-SAMURAI-I-SUV-LWB-HARDTOP-01	4040	1530	1690	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Suzuki/41701/Suzuki-Samurai-LWB-Hard-Top-19TD.html
EU-SUZUKI-S-CROSS-II-SUV-01	4305	1785	1585	Suzuki official	https://www.suzuki.com.au/vehicles/suv/s-cross/specifications/
EU-SUZUKI-SPLASH-I-HATCHBACK-01	3715	1680	1590	Auto-Data	https://www.auto-data.net/en/suzuki-splash-1.0-65hp-16488
EU-SUZUKI-SWACE-I-WAGON-01	4655	1790	1460	Auto-Data	https://www.auto-data.net/en/suzuki-swace-model-2824
EU-SUZUKI-SWIFT-II-SEDAN-01	4095	1590	1380	Drive.Place	https://suzuki.drive.place/swift/ii/group_sedan/271005
EU-SUZUKI-SWIFT-II-HATCHBACK-01	3745	1590	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3334535/suzuki_swift_1_3_gs_3-door.html
EU-SUZUKI-SWIFT-III-HATCHBACK-01	3695	1690	1500	Auto-Data	https://www.auto-data.net/en/suzuki-swift-iv-1.3i-92hp-4wd-16524
EU-SUZUKI-SWIFT-IV-HATCHBACK-SPORT-01	3890	1695	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3405950/suzuki_swift_sport.html
EU-SUZUKI-SWIFT-V-HATCHBACK-FWD-01	3840	1735	1480	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-1.0-112hp-shvs-29940
EU-SUZUKI-SWIFT-V-HATCHBACK-ALLGRIP-01	3840	1735	1505	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-1.2-dualjet-90hp-allgrip-29980
EU-SUZUKI-SWIFT-VI-HATCHBACK-FWD-01	3860	1735	1495	Suzuki official	https://www.globalsuzuki.com/pan-europeantestdrive2403/swift/presskit/pdf/swift_pressrelease_en.pdf
EU-SUZUKI-SWIFT-VI-HATCHBACK-ALLGRIP-01	3860	1735	1520	Suzuki official	https://www.globalsuzuki.com/pan-europeantestdrive2403/swift/presskit/pdf/swift_pressrelease_en.pdf
EU-SUZUKI-SX4-I-HATCHBACK-PREFACELIFT-01	4135	1755	1605	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-generation-3729
EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	4150	1755	1620	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-facelift-2009-generation-3834
EU-SUZUKI-SX4-S-CROSS-I-SUV-PREFACELIFT-01	4300	1765	1575	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-generation-4185
EU-SUZUKI-SX4-S-CROSS-I-SUV-FACELIFT-01	4300	1785	1580	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-facelift-2016-generation-5088
EU-SUZUKI-VITARA-I-SUV-3DR-01	3620	1630	1665	CarsGuide	https://www.carsguide.com.au/suzuki/vitara/car-dimensions/1995
EU-SUZUKI-VITARA-I-SUV-5DR-01	4030	1635	1700	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3349655/suzuki_vitara_1_6i_jlx_16v_5-door.html
EU-SUZUKI-VITARA-I-CONVERTIBLE-3DR-01	3620	1631	1669	Autoevolution	https://www.autoevolution.com/cars/suzuki-vitara-cabrio-1989.html
EU-SUZUKI-VITARA-I-CONVERTIBLE-DIESEL-3DR-01	3630	1670	1630	Auto-Data	https://www.auto-data.net/en/suzuki-vitara-cabrio-et-ta-1.9-d-et-75hp-16440
EU-SUZUKI-VITARA-I-CONVERTIBLE-HDI-3DR-01	3630	1635	1700	Autokoo	https://www.autokoo.com/fiche-technique/suzuki/vitara/cabriolet-20-hdi-jlx/30512720020201
EU-SUZUKI-VITARA-I-SUV-5DR-WIDEBODY-01	4120	1700	1700	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Suzuki/5895/Suzuki-Vitara-Wagon-20-Turbo-D.html
EU-SUZUKI-VITARA-I-SUV-HDI-3DR-01	3720	1635	1700	Autogidas	https://autogidas.lt/en/auto-katalogas/suzuki/vitara/2.0-hdi-2001-2003-k72673
EU-SUZUKI-VITARA-IV-SUV-2015-01	4175	1775	1610	CarsGuide	https://www.carsguide.com.au/suzuki/vitara/car-dimensions/2024
EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-FWD-01	4185	1775	1600	Suzuki official	https://www.suzuki.com.au/vehicles/suv/vitara-hybrid/specifications/
EU-SUZUKI-VITARA-IV-SUV-FACELIFT2024-ALLGRIP-01	4185	1775	1595	Suzuki official	https://www.suzuki.com.au/vehicles/suv/vitara-hybrid/specifications/
EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	3410	1575	1700	Auto-Data	https://www.auto-data.net/en/suzuki-wagon-r-model-1902
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3575	1620	1705	Auto-Data	https://www.auto-data.net/en/suzuki-wagon-r-model-1902
```

[下载 left18448_15801-15900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15801-15900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2428 行）
- 累计尺寸组：dimension_groups_final.tsv（566 行）

