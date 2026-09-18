# 任务：left18448 第 15901-16000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0160__73981dc1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15901-16000 行

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
left18448 第 15901-16000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15901-16000_ktype_dimension_mapping_final.tsv
- left18448_15901-16000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SUZUKI-WAGON-R-PLUS-I-HATCHBACK-01	3410	1575	1700
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3575	1620	1705

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Suzuki	Wagon r+	1.3 Ddis	Schrägheck	Frontantrieb	Diesel	Sep 2003	-	17765
Suzuki	X-90	1.6 I 16V	Geländewagen offen	Heckantrieb	Benzin	Sep 1995	Dec 1997	5681
Suzuki	Xl7	3.6	SUV	Frontantrieb	Benzin	Sep 2006	Dec 2009	54466
Suzuki	Xl7	3.6 Allrad	SUV	Allrad	Benzin	Sep 2006	Dec 2009	54465
SWM Motors	G01	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2023	-	156805
SWM Motors	G01	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2023	-	801363
SWM Motors	G01	1.5 T	SUV	Frontantrieb	Benzin	Jan 2023	-	154803
SWM Motors	G01	1.5 T	SUV	Frontantrieb	Benzin	Apr 2023	-	801362
SWM Motors	G01	1.5 T	SUV	Frontantrieb	Benzin	Apr 2025	-	801711
SWM Motors	G03f	1.5	SUV	Frontantrieb	Benzin	Nov 2025	-	800079
SWM Motors	G03f	1.5 EDI	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	803363
SWM Motors	G05	1.5	SUV	Frontantrieb	Benzin	Nov 2024	-	801262
Talbot	160	1.6	Stufenheck	Heckantrieb	Benzin	Jan 1973	Mar 1979	11839
Talbot	180	2	Stufenheck	Heckantrieb	Benzin	Feb 1973	Sep 1977	11840
Tata	Indigo	1.4	Stufenheck	Frontantrieb	Benzin	Jan 2003	-	18346
Tata	Indigo	1.4	Kombi	Frontantrieb	Benzin	Jan 2003	Dec 2010	18348
Tata	Indigo	1.4 D	Stufenheck	Frontantrieb	Diesel	Jan 2003	-	18347
Tata	Indigo	1.4 D	Kombi	Frontantrieb	Diesel	Jan 2003	Dec 2010	18349
Tata	Loadbeta	1.9 D	Pick-up	Heckantrieb	Diesel	Nov 1995	Dec 2006	18440
Tata	Loadbeta	1.9 D	Pick-up	Heckantrieb	Diesel	Aug 1994	Dec 2006	18441
Tata	Loadbeta	1.9 D Allrad	Pick-up	Allrad	Diesel	Nov 1995	Dec 2006	18439
Tata	Safari	2.1 EXI 4X4	SUV	Allrad	Benzin	Aug 2003	-	18350
Tata	Sierra	1.9 D	Geländewagen geschlossen	Heckantrieb	Diesel	Aug 1995	Feb 2000	18361
Tata	Sierra	2.0 TD	Geländewagen geschlossen	Heckantrieb	Diesel	Jun 1997	Dec 2002	18351
Tata	Telcoline	3.0 207 DI	Pick-up	Allrad	Diesel	Jun 1999	Dec 2007	18352
Tazzari	Zero	EM1	Stufenheck	Heckantrieb	Elektro	Jun 2012	Dec 2016	124748
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	Feb 2019	-	143475
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	Dec 2019	-	143476
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	Mar 2020	-	145757
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	Sep 2023	-	801182
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	May 2025	-	801834
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Dec 2020	-	143474
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Jun 2019	-	143477
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Feb 2019	-	143479
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Dec 2019	-	143480
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Jun 2019	-	144477
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Mar 2019	-	147387
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Mar 2022	-	153369
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	Feb 2024	-	157008
Tesla	Model 3	EV Perfomance AWD	Stufenheck	Allrad	Elektro	Feb 2022	-	154877
Tesla	Model 3	EV Performance AWD	Stufenheck	Allrad	Elektro	Dec 2019	-	143478
Tesla	Model 3	EV Performance AWD	Stufenheck	Allrad	Elektro	Apr 2024	-	158557
Tesla	Model 3	EV Performance AWD	Stufenheck	Allrad	Elektro	Apr 2024	-	158637
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	Nov 2013	Sep 2014	106770
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	Oct 2014	Apr 2026	111108
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	Nov 2013	Apr 2026	120800
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	Nov 2016	Apr 2026	123897
Tesla	Model s	70	Schrägheck	Heckantrieb	Elektro	Sep 2015	Apr 2026	117530
Tesla	Model s	70	Schrägheck	Heckantrieb	Elektro	Sep 2015	Apr 2026	118983
Tesla	Model s	75	Schrägheck	Heckantrieb	Elektro	Nov 2016	Apr 2026	120531
Tesla	Model s	75	Schrägheck	Heckantrieb	Elektro	Nov 2016	Apr 2026	123898
Tesla	Model s	85	Schrägheck	Heckantrieb	Elektro	Sep 2012	Feb 2016	58349
Tesla	Model s	85	Schrägheck	Heckantrieb	Elektro	Feb 2015	Feb 2016	111109
Tesla	Model s	85	Schrägheck	Heckantrieb	Elektro	Sep 2012	Feb 2016	117529
Tesla	Model s	90	Schrägheck	Heckantrieb	Elektro	Sep 2012	Feb 2016	154660
Tesla	Model s	60D AWD	Schrägheck	Allrad	Elektro	Oct 2014	Apr 2015	108502
Tesla	Model s	60D AWD	Schrägheck	Allrad	Elektro	Oct 2014	Apr 2026	120799
Tesla	Model s	60D AWD	Schrägheck	Allrad	Elektro	Jun 2016	Apr 2026	123896
Tesla	Model s	70D AWD	Schrägheck	Allrad	Elektro	Apr 2015	Apr 2026	113073
Tesla	Model s	70D AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	117515
Tesla	Model s	75D AWD	Schrägheck	Allrad	Elektro	Jun 2016	Apr 2026	120532
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	Oct 2014	Feb 2016	108501
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	Jan 2014	Feb 2016	113081
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	Oct 2014	Feb 2016	117518
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	Oct 2014	Jul 2015	126198
Tesla	Model s	90D AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	119786
Tesla	Model s	EV AWD	Schrägheck	Allrad	Elektro	Sep 2020	Apr 2026	143463
Tesla	Model s	EV AWD	Schrägheck	Allrad	Elektro	Jan 2021	Apr 2026	144729
Tesla	Model s	EV AWD	Schrägheck	Allrad	Elektro	Jan 2023	Apr 2026	154878
Tesla	Model s	P100d AWD	Schrägheck	Allrad	Elektro	Jan 2017	Dec 2019	151032
Tesla	Model s	P85	Schrägheck	Heckantrieb	Elektro	Nov 2013	Dec 2014	106768
Tesla	Model s	P85	Schrägheck	Heckantrieb	Elektro	May 2013	Dec 2014	126196
Tesla	Model s	P85d AWD	Schrägheck	Allrad	Elektro	Oct 2014	Feb 2016	109006
Tesla	Model s	P85d AWD	Schrägheck	Allrad	Elektro	Sep 2015	Feb 2016	117352
Tesla	Model s	P85d AWD	Schrägheck	Allrad	Elektro	Oct 2014	Oct 2015	126200
Tesla	Model s	P90d AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	119784
Tesla	Model s	P90d AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	119785
Tesla	Model s	P90d AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	154688
Tesla	Model s	Plaid AWD	Schrägheck	Allrad	Elektro	Jan 2021	Apr 2026	144730
Tesla	Model x	75D AWD	Schrägheck	Allrad	Elektro	Jun 2016	Apr 2026	120372
Tesla	Model x	90D AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	117531
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	Sep 2019	Apr 2026	143399
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	Sep 2020	Apr 2026	143400
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	Jan 2021	Apr 2026	144731
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	Feb 2023	Apr 2026	153625
Tesla	Model x	P90d AWD	Schrägheck	Allrad	Elektro	Sep 2015	Apr 2026	117532
Tesla	Model x	Plaid AWD	Schrägheck	Allrad	Elektro	Jan 2021	Apr 2026	144732
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	Jul 2021	Jan 2025	144817
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	Sep 2021	Jan 2025	145782
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	Feb 2023	Jan 2025	157997
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	Apr 2024	Jan 2025	158468
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	Jan 2025	-	160389
Tesla	Model y	EV	SUV	Allrad	Elektro	Jan 2025	-	161096
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	May 2023	Jan 2025	800779
Tesla	Model y	EV Allrad	SUV	Allrad	Elektro	Jul 2021	Jan 2025	144818
Tesla	Model y	EV Allrad	SUV	Allrad	Elektro	Sep 2021	Jan 2025	156980
Tesla	Model y	EV Heckantrieb	SUV	Heckantrieb	Elektro	Sep 2022	Jan 2025	800822
Tesla	Model y	EV Performance Allrad	SUV	Allrad	Elektro	Sep 2021	Jan 2025	145788
Tesla	Model y	EV Performance Allrad	SUV	Allrad	Elektro	Sep 2021	Jan 2025	157006
Tesla	Model y	EV Performance Allrad	SUV	Allrad	Elektro	Jan 2022	Jan 2025	802537


--- Round 1 / 首次发送 ---
## 更新点

* 当前 100 个输入 Ktype 已全部覆盖，动力、能源、功率、变速箱及驱动差异均优先复用相同物理外廓。
* 共闭合 22 个 DIMENSION_GROUP；复用了既有 `EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01`，其累计三维与规格页一致。([汽车数据][1])
* Tesla 仅在三维明确改变时拆组：Model 3 Highland、Model S 2016/2021 外廓、Model X 2021 外廓和 Model Y 2025 外廓。([汽车数据][2])
* Tata Telcoline/Loadbeta 按当前 Ktype 未提供 CAB/BED 分支证据的标准双门 Pickup 外廓合并；Tazzari Zero 三维由技术资料支持。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：22
* `id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用闭合、三维与来源非空、无孤立尺寸组。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17765	17765	Hatchback	II		5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
5681	5681	Convertible	I	LB11S	2	EU-SUZUKI-X-90-I-CONVERTIBLE-01	HIGH	Open two-door off-road body normalized as Convertible.	READY
54466	54466	SUV	II		5	EU-SUZUKI-XL7-II-SUV-01	HIGH		READY
54465	54465	SUV	II		5	EU-SUZUKI-XL7-II-SUV-01	HIGH		READY
156805	156805	SUV	I		5	EU-SWM-G01-I-SUV-01	HIGH		READY
801363	801363	SUV	I		5	EU-SWM-G01-I-SUV-01	HIGH		READY
154803	154803	SUV	I		5	EU-SWM-G01-I-SUV-01	HIGH		READY
801362	801362	SUV	I		5	EU-SWM-G01-I-SUV-01	HIGH		READY
801711	801711	SUV	I		5	EU-SWM-G01-I-SUV-01	HIGH		READY
800079	800079	SUV	I		5	EU-SWM-G03F-I-SUV-01	HIGH		READY
803363	803363	SUV	I		5	EU-SWM-G03F-I-SUV-01	MEDIUM	EDI powertrain does not establish a different exterior.	READY
801262	801262	SUV	I facelift		5	EU-SWM-G05-I-SUV-01	HIGH	G05 Pro/facelift exterior branch.	READY
11839	11839	Sedan	I		4	EU-TALBOT-160-180-I-SEDAN-SHARED-01	MEDIUM	Talbot 160 and 180 share the same production body shell.	READY
11840	11840	Sedan	I		4	EU-TALBOT-160-180-I-SEDAN-SHARED-01	MEDIUM	Talbot 160 and 180 share the same production body shell.	READY
18346	18346	Sedan	I		4	EU-TATA-INDIGO-I-SEDAN-01	HIGH		READY
18348	18348	Wagon	I		5	EU-TATA-INDIGO-MARINA-I-WAGON-01	HIGH	Marina estate body.	READY
18347	18347	Sedan	I		4	EU-TATA-INDIGO-I-SEDAN-01	HIGH		READY
18349	18349	Wagon	I		5	EU-TATA-INDIGO-MARINA-I-WAGON-01	HIGH	Marina estate body.	READY
18440	18440	Pickup	I		2	EU-TATA-TELCOLINE-I-PICKUP-STANDARD-01	MEDIUM	Loadbeta/Telcoline are first-generation export aliases; no Ktype-specific cab or bed branch is evidenced.	READY
18441	18441	Pickup	I		2	EU-TATA-TELCOLINE-I-PICKUP-STANDARD-01	MEDIUM	Loadbeta/Telcoline are first-generation export aliases; no Ktype-specific cab or bed branch is evidenced.	READY
18439	18439	Pickup	I		2	EU-TATA-TELCOLINE-I-PICKUP-STANDARD-01	MEDIUM	Loadbeta/Telcoline are first-generation export aliases; no Ktype-specific cab or bed branch is evidenced.	READY
18350	18350	SUV	I		5	EU-TATA-SAFARI-I-SUV-01	MEDIUM		READY
18361	18361	SUV	I		3	EU-TATA-SIERRA-I-SUV-01	HIGH	Closed three-door off-road body normalized as SUV.	READY
18351	18351	SUV	I		3	EU-TATA-SIERRA-I-SUV-01	HIGH	Closed three-door off-road body normalized as SUV.	READY
18352	18352	Pickup	I		2	EU-TATA-TELCOLINE-I-PICKUP-STANDARD-01	MEDIUM	Loadbeta/Telcoline are first-generation export aliases; no Ktype-specific cab or bed branch is evidenced.	READY
124748	124748	Sedan	I		2	EU-TAZZARI-ZERO-I-SEDAN-01	MEDIUM	Input Stufenheck normalized as Sedan under the body-style contract.	READY
143475	143475	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
143476	143476	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
145757	145757	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
801182	801182	Sedan	I Highland		4	EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	HIGH	Highland exterior dimensions differ from the earlier body.	READY
801834	801834	Sedan	I Highland		4	EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	HIGH	Highland exterior dimensions differ from the earlier body.	READY
143474	143474	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
143477	143477	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
143479	143479	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
143480	143480	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
144477	144477	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
147387	147387	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
153369	153369	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
157008	157008	Sedan	I Highland		4	EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	HIGH	Highland exterior dimensions differ from the earlier body.	READY
154877	154877	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
143478	143478	Sedan	I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
158557	158557	Sedan	I Highland		4	EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	HIGH	Highland exterior dimensions differ from the earlier body.	READY
158637	158637	Sedan	I Highland		4	EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	HIGH	Highland exterior dimensions differ from the earlier body.	READY
106770	106770	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
111108	111108	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
120800	120800	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
123897	123897	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
117530	117530	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
118983	118983	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
120531	120531	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
123898	123898	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
58349	58349	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
111109	111109	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
117529	117529	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
154660	154660	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
108502	108502	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
120799	120799	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
123896	123896	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
113073	113073	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
117515	117515	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
120532	120532	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
108501	108501	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
113081	113081	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
117518	117518	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
126198	126198	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
119786	119786	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
143463	143463	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
144729	144729	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2021-01	HIGH	Liftback normalized to Hatchback.	READY
154878	154878	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2021-01	HIGH	Liftback normalized to Hatchback.	READY
151032	151032	Hatchback	I facelift 2016		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	HIGH	Liftback normalized to Hatchback.	READY
106768	106768	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
126196	126196	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
109006	109006	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
117352	117352	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
126200	126200	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
119784	119784	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
119785	119785	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
154688	154688	Hatchback	I		5	EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	HIGH	Liftback normalized to Hatchback.	READY
144730	144730	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2021-01	HIGH	Liftback normalized to Hatchback.	READY
120372	120372	Hatchback	I		5	EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
117531	117531	Hatchback	I		5	EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
143399	143399	Hatchback	I		5	EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
143400	143400	Hatchback	I		5	EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
144731	144731	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-X-I-HATCHBACK-FACELIFT-2021-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
153625	153625	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-X-I-HATCHBACK-FACELIFT-2021-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
117532	117532	Hatchback	I		5	EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
144732	144732	Hatchback	I facelift 2021		5	EU-TESLA-MODEL-X-I-HATCHBACK-FACELIFT-2021-01	HIGH	Schrägheck normalized as Hatchback under the body-style contract.	READY
144817	144817	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
145782	145782	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
157997	157997	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
158468	158468	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
160389	160389	SUV	I facelift 2025		5	EU-TESLA-MODEL-Y-I-SUV-FACELIFT-2025-01	HIGH	2025 redesigned exterior branch.	READY
161096	161096	SUV	I facelift 2025		5	EU-TESLA-MODEL-Y-I-SUV-FACELIFT-2025-01	HIGH	2025 redesigned exterior branch.	READY
800779	800779	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
144818	144818	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
156980	156980	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
800822	800822	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
145788	145788	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
157006	157006	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
802537	802537	SUV	I		5	EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	HIGH		READY
```

[下载 left18448_15901-16000_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15901-16000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3575	1620	1705	Auto-Data generation page	https://www.auto-data.net/en/suzuki-wagon-r-ii-generation-3708
EU-SUZUKI-X-90-I-CONVERTIBLE-01	3710	1695	1550	Automobile-Catalog specification page	https://www.automobile-catalog.com/car/1995/3351485/suzuki_x-90_4wd_automatic.html
EU-SUZUKI-XL7-II-SUV-01	5009	1834	1750	Auto-Data model page	https://www.auto-data.net/en/suzuki-xl7-model-1912
EU-SWM-G01-I-SUV-01	4610	1855	1740	Auto-Data specification page	https://www.auto-data.net/en/swm-g01-1.5t-156hp-53917
EU-SWM-G03F-I-SUV-01	4605	1815	1825	Auto-Data specification page	https://www.auto-data.net/en/swm-g03f-1.5l-108hp-53965
EU-SWM-G05-I-SUV-01	4750	1860	1780	Auto-Data specification page	https://www.auto-data.net/en/swm-g05-pro-facelift-2021-1.5t-156hp-dct-53949
EU-TALBOT-160-180-I-SEDAN-SHARED-01	4527	1728	1430	Automobile-Catalog model-year page	https://www.automobile-catalog.com/make/chrysler_france/160-2_l/160-2_l/1973.html
EU-TATA-INDIGO-I-SEDAN-01	4150	1620	1540	Auto-Data model page	https://www.auto-data.net/en/tata-indigo-model-172
EU-TATA-INDIGO-MARINA-I-WAGON-01	4130	1625	1575	Auto-Data model page	https://www.auto-data.net/en/tata-indigo-model-172
EU-TATA-TELCOLINE-I-PICKUP-STANDARD-01	4585	1810	1590	CarsGuide variant specification page	https://www.carsguide.com.au/tata/telcoline/car-dimensions/2000
EU-TATA-SAFARI-I-SUV-01	4650	1918	1925	CarWale generation comparison page	https://www.carwale.com/compare-cars/tata-safari-1998-2005-vs-ford-endeavour-2003-2007/?c1=633&c2=417
EU-TATA-SIERRA-I-SUV-01	4410	1710	1770	Auto-Data model page	https://www.auto-data.net/en/tata-sierra-model-169
EU-TAZZARI-ZERO-I-SEDAN-01	2880	1560	1425	Tazzari Zero technical brochure reproduction	https://www.calameo.com/books/00235694440f4fe1ef349
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443	Auto-Data model page	https://www.auto-data.net/en/tesla-model-3-model-2355
EU-TESLA-MODEL-3-I-SEDAN-HIGHLAND-01	4720	1850	1441	Auto-Data generation page	https://www.auto-data.net/en/tesla-model-3-highland-facelift-2023-generation-9666
EU-TESLA-MODEL-S-I-HATCHBACK-ORIGINAL-01	4970	1964	1445	Auto-Data model page	https://www.auto-data.net/en/tesla-model-s-model-2013
EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2016-01	4979	1964	1445	Auto-Data model page	https://www.auto-data.net/en/tesla-model-s-model-2013
EU-TESLA-MODEL-S-I-HATCHBACK-FACELIFT-2021-01	5021	1987	1431	Auto-Data model page	https://www.auto-data.net/en/tesla-model-s-model-2013
EU-TESLA-MODEL-X-I-HATCHBACK-ORIGINAL-01	5052	1999	1684	Auto-Data generation page	https://www.auto-data.net/en/tesla-model-x-generation-4104
EU-TESLA-MODEL-X-I-HATCHBACK-FACELIFT-2021-01	5057	1999	1680	Auto-Data generation page	https://www.auto-data.net/en/tesla-model-x-facelift-2021-generation-8166
EU-TESLA-MODEL-Y-I-SUV-ORIGINAL-01	4751	1921	1624	Auto-Data generation page	https://www.auto-data.net/en/tesla-model-y-generation-8049
EU-TESLA-MODEL-Y-I-SUV-FACELIFT-2025-01	4790	1920	1624	Tesla Model Y owner manual	https://www.tesla.com/ownersmanual/modely/en_gb/GUID-1E76B638-7B12-4D9A-8767-94B7F1E92A0E.html
```

[下载 left18448_15901-16000_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15901-16000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/suzuki-wagon-r-model-1902?utm_source=chatgpt.com "Suzuki Wagon R+ | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/tesla-model-3-model-2355?utm_source=chatgpt.com "Tesla Model 3 | Technical Specs, Fuel consumption, Dimensions"
[3]: https://en.wikipedia.org/wiki/Tata_Telcoline?utm_source=chatgpt.com "Tata Telcoline"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2528 行）
- 累计尺寸组：dimension_groups_final.tsv（587 行）

