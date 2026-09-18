# 任务：left18448 第 7701-7800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0078__694c7a1f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7701-7800 行

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
left18448 第 7701-7800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7701-7800_ktype_dimension_mapping_final.tsv
- left18448_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Jaguar	X-Type i	2.2 D	Kombi	Frontantrieb	Diesel	Oct 2005	Dec 2009	18915
Jaguar	X-Type i	2.2 D	Stufenheck	Frontantrieb	Diesel	Oct 2005	Nov 2009	18916
Jaguar	X-Type i	2.5 V6 Allrad	Stufenheck	Allrad	Benzin	Jun 2001	Nov 2009	15607
Jaguar	X-Type i	3.0 V6 Allrad	Stufenheck	Allrad	Benzin	Jun 2001	Dec 2008	15608
Jeep	Avenger	1.2 GSE T3	SUV	Frontantrieb	Benzin	Dec 2022	-	151489
Jeep	Avenger	1.2 Hybrid 4XE	SUV	Allrad	Benzin/Elektro	Oct 2024	-	801000
Jeep	Avenger	1.2 T3 E-hybrid	SUV	Frontantrieb	Benzin/Elektro	Dec 2023	-	156939
Jeep	Avenger	Electric	SUV	Frontantrieb	Elektro	Dec 2022	-	151490
Jeep	Cherokee	2.4	SUV	Frontantrieb	Benzin	Nov 2013	-	106102
Jeep	Cherokee	2.5	Geländewagen geschlossen	Allrad	Benzin	Oct 1995	Sep 2001	5139
Jeep	Cherokee	2.0 CRD	SUV	Frontantrieb	Diesel	Apr 2014	Aug 2018	105892
Jeep	Cherokee	2.0 CRD	Kasten/SUV	Frontantrieb	Diesel	Apr 2014	Aug 2018	143100
Jeep	Cherokee	2.0 CRD 4X4	SUV	Allrad	Diesel	Apr 2014	Aug 2018	105875
Jeep	Cherokee	2.0 CRD 4X4	SUV	Allrad	Diesel	Apr 2014	Aug 2018	105894
Jeep	Cherokee	2.1 TD	Geländewagen geschlossen	Heckantrieb	Diesel	Jun 1989	Mar 1992	16038
Jeep	Cherokee	2.2 CRD	Kasten/SUV	Allrad	Diesel	Aug 2015	Aug 2018	143101
Jeep	Cherokee	2.2 CRD	Kasten/SUV	Allrad	Diesel	Aug 2015	Aug 2018	143102
Jeep	Cherokee	2.2 CRD 4X4	SUV	Allrad	Diesel	Aug 2015	Aug 2018	116214
Jeep	Cherokee	2.2 CRD 4X4	SUV	Allrad	Diesel	Aug 2015	Aug 2018	116215
Jeep	Cherokee	2.4 4X4	SUV	Allrad	Benzin	Nov 2013	-	100390
Jeep	Cherokee	2.4 4X4	SUV	Allrad	Benzin	Nov 2013	-	107324
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 1990	Sep 1996	121502
Jeep	Cherokee	2.8 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 2002	Jan 2008	17258
Jeep	Cherokee	2.8 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 2004	Jan 2008	18793
Jeep	Cherokee	2.8 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 2010	-	55928
Jeep	Cherokee	3.2 4X4	SUV	Allrad	Benzin	Jan 2014	-	128303
Jeep	Cherokee	3.2 4X4	Kasten/SUV	Allrad	Benzin	Aug 2015	-	143099
Jeep	Cherokee	3.2 V6	SUV	Frontantrieb	Benzin	Nov 2013	-	107322
Jeep	Cherokee	3.2 V6 4X4	SUV	Allrad	Benzin	Nov 2013	-	100391
Jeep	Cherokee	3.7 4X4	Geländewagen geschlossen	Allrad	Benzin	Aug 2003	Jan 2008	17737
Jeep	Cherokee	3.7 4X4	Geländewagen geschlossen	Allrad	Benzin	Sep 2001	Oct 2007	55917
Jeep	Cherokee	3.7 V6 Allrad	Geländewagen geschlossen	Allrad	Benzin	Jan 2008	Aug 2012	12567
Jeep	Cherokee	4.0 I	Geländewagen geschlossen	Allrad	Benzin	Jul 1998	Sep 2001	14432
Jeep	Cherokee	4.0 I	Geländewagen geschlossen	Allrad	Benzin	Feb 1999	Sep 2001	15426
Jeep	Cherokee	4.0 I	Geländewagen geschlossen	Allrad	Benzin	Oct 1990	Sep 2001	57509
Jeep	Cherokee	4.0 I 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 1995	Sep 2001	5138
Jeep	Cj5 - cj8	2	Geländewagen offen	Allrad	Benzin	Jan 1983	Dec 1987	14536
Jeep	Cj5 - cj8	2.5	Geländewagen offen	Allrad	Benzin	Jan 1984	Dec 1987	14537
Jeep	Cj5 - cj8	2.5	Geländewagen offen	Allrad	Benzin	Sep 1979	Dec 1983	14538
Jeep	Cj5 - cj8	3.7	Geländewagen offen	Allrad	Benzin	Jan 1966	Dec 1971	14539
Jeep	Cj5 - cj8	3.8	Geländewagen offen	Allrad	Benzin	Jan 1972	Dec 1978	14540
Jeep	Cj5 - cj8	4.2	Geländewagen offen	Allrad	Benzin	Jan 1972	Dec 1987	14541
Jeep	Cj5 - cj8	5	Geländewagen offen	Allrad	Benzin	Jan 1973	Dec 1981	14542
Jeep	Cj5 - cj8	2.1 D	Geländewagen offen	Allrad	Diesel	Jan 1983	Dec 1987	14543
Jeep	Cj5 - cj8	2.4 D	Geländewagen offen	Allrad	Diesel	Jan 1983	Dec 1987	14544
Jeep	Commander	3.0 CRD 4X4	Kasten/SUV	Allrad	Diesel	Sep 2005	Dec 2010	143108
Jeep	Commander	5.7 Hemi V8 4X4	Kasten/SUV	Allrad	Benzin	Sep 2005	Dec 2010	143107
Jeep	Compass	1.3	SUV	Frontantrieb	Benzin	Aug 2020	-	143535
Jeep	Compass	2	SUV	Frontantrieb	Benzin	May 2011	-	11437
Jeep	Compass	1.2 Hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2025	-	161686
Jeep	Compass	1.3 Hybrid 4X4	SUV	Allrad	Benzin/Elektro	Apr 2021	-	144209
Jeep	Compass	1.4 Multiair	SUV	Frontantrieb	Benzin	Mar 2017	-	127519
Jeep	Compass	1.4 Multiair 4X4	SUV	Allrad	Benzin	Mar 2017	-	127520
Jeep	Compass	1.5 T4 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147847
Jeep	Compass	1.6 CRD	SUV	Frontantrieb	Diesel	Mar 2017	-	127521
Jeep	Compass	1.6 Multijet	SUV	Frontantrieb	Diesel	Apr 2021	-	144208
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	Dec 2016	-	126318
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	Mar 2017	-	127522
Jeep	Compass	2.2 CRD	SUV	Frontantrieb	Diesel	May 2011	-	11453
Jeep	Compass	2.2 CRD 4X4	SUV	Allrad	Diesel	May 2011	-	108013
Jeep	Compass	E-hybrid Plug IN	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	163737
Jeep	Compass	EV	SUV	Frontantrieb	Elektro	May 2025	-	161687
Jeep	Gladiator	3.0 D 4WD	Pick-up	Allrad	Diesel	Apr 2021	-	144083
Jeep	Grand cherokee i	5.9 I 4X4	Geländewagen geschlossen	Allrad	Benzin	Aug 1997	Apr 1999	11029
Jeep	Grand cherokee ii	2.7 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Oct 2001	Sep 2005	16477
Jeep	Grand cherokee ii	3.1 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	Apr 1999	Dec 2001	10012
Jeep	Grand cherokee ii	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 1999	Sep 2005	10010
Jeep	Grand cherokee ii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 1999	Aug 2000	10011
Jeep	Grand cherokee ii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 1999	Sep 2005	15427
Jeep	Grand cherokee ii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 2001	Sep 2005	16478
Jeep	Grand cherokee ii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 2003	Sep 2005	17736
Jeep	Grand cherokee iii	5.7	Geländewagen geschlossen	Heckantrieb	Benzin	Jun 2005	Dec 2008	59986
Jeep	Grand cherokee iii	3.0 CRD	Geländewagen geschlossen	Heckantrieb	Diesel	Jun 2005	Dec 2010	12569
Jeep	Grand cherokee iii	3.0 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jun 2005	Dec 2010	18808
Jeep	Grand cherokee iii	3.7 V6 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 2004	Dec 2010	18805
Jeep	Grand cherokee iii	3.7 V6 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 2008	Dec 2010	57253
Jeep	Grand cherokee iii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 2005	Dec 2010	18806
Jeep	Grand cherokee iii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Sep 2007	Feb 2010	54929
Jeep	Grand cherokee iii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 2005	Dec 2010	56846
Jeep	Grand cherokee iii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 2007	May 2010	59987
Jeep	Grand cherokee iii	4.7 V8 Flex	Geländewagen geschlossen	Heckantrieb	Benzin/Ethanol	Oct 2004	May 2010	57252
Jeep	Grand cherokee iii	5.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 2005	Dec 2010	18807
Jeep	Grand cherokee iii	6.1 Srt8 RWD	Geländewagen geschlossen	Heckantrieb	Benzin	Mar 2006	May 2010	59985
Jeep	Grand cherokee iv	3.0 CRD V6 4X4	SUV	Allrad	Diesel	Feb 2011	-	11458
Jeep	Grand cherokee iv	3.0 CRD V6 4X4	SUV	Allrad	Diesel	Feb 2011	-	11461
Jeep	Grand cherokee iv	3.0 CRD V6 4X4	SUV	Allrad	Diesel	Jul 2013	-	106092
Jeep	Grand cherokee iv	3.6 V6	SUV	Heckantrieb	Benzin	Nov 2010	-	59988
Jeep	Grand cherokee iv	3.6 V6 Flexfuel 4X4	SUV	Allrad	Benzin/Ethanol	Nov 2010	-	17123
Jeep	Grand cherokee iv	3.6 VVT 4X4	SUV	Allrad	Benzin	Apr 2016	-	101099
Jeep	Grand cherokee iv	5.7 4X4	SUV	Allrad	Benzin	Jan 2011	-	126953
Jeep	Grand cherokee l v	2.0 4XE Plug-in Hybrid	SUV	Allrad	Benzin/Elektro	May 2021	-	146336
Jeep	Grand cherokee van	3.0 CRD	Kasten/SUV	Allrad	Diesel	Jan 2017	-	143113
Jeep	Grand cherokee van	3.0 CRD	Kasten/SUV	Allrad	Diesel	Jul 2013	-	143114
Jeep	Grand cherokee van	5.7 Hemi 4X4	Kasten/SUV	Allrad	Benzin	Jul 2013	-	143111
Jeep	Grand cherokee van	V6 VVT	Kasten/SUV	Allrad	Benzin	Jul 2013	-	143110
Jeep	Grand wagoneer	5.9 4WD	Geländewagen geschlossen	Allrad	Benzin	Sep 1983	Dec 1991	44942
Jeep	J10 standard cab pickup	5.9 4WD	Pick-up	Allrad	Benzin	Sep 1978	Dec 1988	44947
Jeep	J20 standard cab pickup	5.9 4WD	Pick-up	Allrad	Benzin	Sep 1978	Dec 1988	44957
Jeep	Patriot	2	Geländewagen geschlossen	Frontantrieb	Benzin	Jan 2011	Dec 2017	11466
Jeep	Patriot	2.4	Geländewagen geschlossen	Frontantrieb	Benzin	Jun 2009	Dec 2017	56234


--- Round 1 / 首次发送 ---
## 更新点

本批已按物理外廓聚类闭合：

* Jaguar X-Type 区分 Sedan 与 Wagon。
* Jeep Avenger 区分前驱燃油/轻混、4xe、纯电三种外廓。
* Cherokee 按 XJ、KJ、KK、KL 处理；`5139`、`57509`、`5([汽车目录][1])([汽车目录][1])e 按 ZJ、WJ、WK、WK2、WL 以及 SRT8 独立外廓归组。
* Kasten/SUV 商用认证行直接复用相同代际 SUV 外廓，没有创建重复尺寸组。

## 进度

* 输入 Ktype：100
* 最终映射行：103
* 独立 DIMENSION_GROUP：34
* PENDING：0
* 唯一 ID、尺寸组引用、正整数三维、来源及 URL、孤立组检查：全部通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18915	18915	Wagon	X-Type (X400)	X400	5	EU-JAGUAR-X-TYPE-X400-WAGON-01	HIGH		READY
18916	18916	Sedan	X-Type (X400)	X400	4	EU-JAGUAR-X-TYPE-X400-SEDAN-01	HIGH		READY
15607	15607	Sedan	X-Type (X400)	X400	4	EU-JAGUAR-X-TYPE-X400-SEDAN-01	HIGH		READY
15608	15608	Sedan	X-Type (X400)	X400	4	EU-JAGUAR-X-TYPE-X400-SEDAN-01	HIGH		READY
151489	151489	SUV	1	J2	5	EU-JEEP-AVENGER-J2-SUV-FWD-ICE-01	HIGH		READY
801000	801000	SUV	1	J2	5	EU-JEEP-AVENGER-J2-SUV-4XE-01	MEDIUM	4xe exterior differs from FWD and EV branches.	READY
156939	156939	SUV	1	J2	5	EU-JEEP-AVENGER-J2-SUV-FWD-ICE-01	HIGH		READY
151490	151490	SUV	1	J2	5	EU-JEEP-AVENGER-J2-SUV-EV-01	HIGH		READY
106102	106102	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
5139_prefl	5139	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-25-EARLY-01	MEDIUM	Ktype spans early and later XJ 2.5 exteriors.	READY
5139_facelift	5139	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-25-LATE-01	MEDIUM	Ktype spans early and later XJ 2.5 exteriors.	READY
105892	105892	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
143100	143100	Van	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	MEDIUM	Commercial homologation; exterior matches KL SUV.	READY
105875	105875	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
105894	105894	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
16038	16038	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	MEDIUM	Drivetrain label does not alter the matched XJ exterior.	READY
143101	143101	Van	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	MEDIUM	Commercial homologation; exterior matches KL SUV.	READY
143102	143102	Van	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	MEDIUM	Commercial homologation; exterior matches KL SUV.	READY
116214	116214	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
116215	116215	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
100390	100390	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
107324	107324	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
121502	121502	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-25-EARLY-01	HIGH		READY
17258	17258	SUV	3 (KJ)	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
18793	18793	SUV	3 (KJ)	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
55928	55928	SUV	4 (KK)	KK	5	EU-JEEP-CHEROKEE-KK-SUV-01	HIGH		READY
128303	128303	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
143099	143099	Van	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	MEDIUM	Commercial homologation; exterior matches KL SUV.	READY
107322	107322	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
100391	100391	SUV	5 (KL)	KL	5	EU-JEEP-CHEROKEE-KL-SUV-01	HIGH		READY
17737	17737	SUV	3 (KJ)	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
55917	55917	SUV	3 (KJ)	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
12567	12567	SUV	4 (KK)	KK	5	EU-JEEP-CHEROKEE-KK-SUV-01	HIGH		READY
14432	14432	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	HIGH		READY
15426	15426	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	HIGH		READY
57509_prefl	57509	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-EARLY-01	MEDIUM	Ktype spans early and later XJ 4.0 exteriors.	READY
57509_facelift	57509	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	MEDIUM	Ktype spans early and later XJ 4.0 exteriors.	READY
5138_prefl	5138	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-EARLY-01	MEDIUM	Ktype spans early and later XJ 4.0 exteriors.	READY
5138_facelift	5138	SUV	2 (XJ)	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	MEDIUM	Ktype spans early and later XJ 4.0 exteriors.	READY
14536	14536	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14537	14537	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14538	14538	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14539	14539	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14540	14540	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14541	14541	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14542	14542	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14543	14543	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
14544	14544	Convertible	CJ-5	CJ5	2	EU-JEEP-CJ-CJ5-CONVERTIBLE-01	MEDIUM	Input CJ5-CJ8 family label matched the CJ-5 engine/date listing.	READY
143108	143108	Van	1 (XK)	XK	5	EU-JEEP-COMMANDER-XK-VAN-01	MEDIUM	Commercial homologation; common Commander XK exterior.	READY
143107	143107	Van	1 (XK)	XK	5	EU-JEEP-COMMANDER-XK-VAN-01	MEDIUM	Commercial homologation; common Commander XK exterior.	READY
143535	143535	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-FWD-01	HIGH		READY
11437	11437	SUV	1 (MK)	MK	5	EU-JEEP-COMPASS-MK-SUV-01	HIGH		READY
161686	161686	SUV	3		5	EU-JEEP-COMPASS-III-SUV-01	MEDIUM		READY
144209	144209	SUV	2 facelift (MP)	MP	5	EU-JEEP-COMPASS-MP-FACELIFT-SUV-4XE-01	HIGH		READY
127519	127519	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-FWD-01	HIGH		READY
127520	127520	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-4X4-01	HIGH		READY
147847	147847	SUV	2 facelift (MP)	MP	5	EU-JEEP-COMPASS-MP-FACELIFT-SUV-FWD-01	HIGH		READY
127521	127521	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-FWD-01	HIGH		READY
144208	144208	SUV	2 facelift (MP)	MP	5	EU-JEEP-COMPASS-MP-FACELIFT-SUV-FWD-01	HIGH		READY
126318	126318	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-4X4-01	HIGH		READY
127522	127522	SUV	2 (MP)	MP	5	EU-JEEP-COMPASS-MP-SUV-4X4-01	HIGH		READY
11453	11453	SUV	1 (MK)	MK	5	EU-JEEP-COMPASS-MK-SUV-01	HIGH		READY
108013	108013	SUV	1 (MK)	MK	5	EU-JEEP-COMPASS-MK-SUV-01	HIGH		READY
163737	163737	SUV	3		5	EU-JEEP-COMPASS-III-SUV-01	MEDIUM		READY
161687	161687	SUV	3		5	EU-JEEP-COMPASS-III-SUV-01	MEDIUM		READY
144083	144083	Pickup	1 (JT)	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-01	MEDIUM	Standard production height selected; trim-specific raised versions excluded.	READY
11029	11029	SUV	1 (ZJ)	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-01	HIGH		READY
16477	16477	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
10012	10012	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
10010	10010	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
10011	10011	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
15427	15427	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
16478	16478	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
17736	17736	SUV	2 (WJ)	WJ	5	EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	HIGH		READY
59986	59986	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	MEDIUM	Production span crosses the facelift; standard early WK exterior retained.	READY
12569	12569	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	MEDIUM	Production span crosses the facelift; standard early WK exterior retained.	READY
18808	18808	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	HIGH		READY
18805	18805	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	HIGH		READY
57253	57253	SUV	3 facelift (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-LATE-01	HIGH		READY
18806	18806	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	HIGH		READY
54929	54929	SUV	3 facelift (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-LATE-01	HIGH		READY
56846	56846	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	HIGH		READY
59987	59987	SUV	3 facelift (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-LATE-01	HIGH		READY
57252	57252	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	MEDIUM	Production span crosses the facelift; standard early WK exterior retained.	READY
18807	18807	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	HIGH		READY
59985	59985	SUV	3 (WK)	WK	5	EU-JEEP-GRAND-CHEROKEE-WK-SRT8-SUV-01	HIGH	SRT8 has a distinct lower exterior.	READY
11458	11458	SUV	4 (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-SUV-4X4-01	HIGH		READY
11461	11461	SUV	4 (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-SUV-4X4-01	HIGH		READY
106092	106092	SUV	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	HIGH		READY
59988	59988	SUV	4 (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-SUV-36-01	HIGH		READY
17123	17123	SUV	4 (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-SUV-36-01	HIGH		READY
101099	101099	SUV	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	HIGH		READY
126953	126953	SUV	4 (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-SUV-4X4-01	HIGH		READY
146336	146336	SUV	5 (WL)	WL	5	EU-JEEP-GRAND-CHEROKEE-WL-SUV-01	MEDIUM	4xe is the two-row WL exterior, not the long-wheelbase L body.	READY
143113	143113	Van	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	MEDIUM	Commercial homologation; exterior matches WK2 facelift SUV.	READY
143114	143114	Van	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	MEDIUM	Commercial homologation; exterior matches WK2 facelift SUV.	READY
143111	143111	Van	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	MEDIUM	Commercial homologation; exterior matches WK2 facelift SUV.	READY
143110	143110	Van	4 facelift (WK2)	WK2	5	EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	MEDIUM	Commercial homologation; exterior matches WK2 facelift SUV.	READY
44942	44942	SUV	SJ	SJ	5	EU-JEEP-GRAND-WAGONEER-SJ-SUV-01	MEDIUM		READY
44947	44947	Pickup	SJ	SJ	2	EU-JEEP-J10-SJ-PICKUP-01	MEDIUM		READY
44957	44957	Pickup	SJ	SJ	2	EU-JEEP-J20-SJ-PICKUP-01	LOW	Complete dimensions rely on a traceable specialist specification.	READY
11466	11466	SUV	1 (MK74)	MK74	5	EU-JEEP-PATRIOT-MK-SUV-01	HIGH		READY
56234	56234	SUV	1 (MK74)	MK74	5	EU-JEEP-PATRIOT-MK-SUV-01	HIGH		READY
```

[下载 left18448_7701-7800_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_7701-7800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-X-TYPE-X400-WAGON-01	4716	1789	1483	Auto-Data — Jaguar X-Type Estate 2.0 TDI	https://www.auto-data.net/en/jaguar-x-type-estate-2.0-tdi-130hp-169
EU-JAGUAR-X-TYPE-X400-SEDAN-01	4672	1789	1430	Auto-Data — Jaguar X-Type X400 2.2 D	https://www.auto-data.net/en/jaguar-x-type-x400-2.2-d-155hp-166
EU-JEEP-AVENGER-J2-SUV-FWD-ICE-01	4084	1776	1534	Auto-Data — Jeep Avenger 1.2 GSE T3	https://www.auto-data.net/en/jeep-avenger-1.2-gse-t3-100hp-49064
EU-JEEP-AVENGER-J2-SUV-4XE-01	4088	1778	1541	Auto-Data — Jeep Avenger generation	https://www.auto-data.net/en/jeep-avenger-generation-9018
EU-JEEP-AVENGER-J2-SUV-EV-01	4080	1778	1528	Auto-Data — Jeep Avenger 54 kWh Electric	https://www.auto-data.net/en/jeep-avenger-54-kwh-156hp-electric-47331
EU-JEEP-CHEROKEE-KL-SUV-01	4624	1859	1670	Auto-Data — Jeep Cherokee V KL 2.0 4WD	https://www.auto-data.net/en/jeep-cherokee-v-kl-2.0-140hp-4wd-22136
EU-JEEP-CHEROKEE-XJ-SUV-25-EARLY-01	4288	1720	1621	Auto-Data — Jeep Cherokee II XJ 2.5 Jamboree	https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-2.5-i-jamboree-122hp-1133
EU-JEEP-CHEROKEE-XJ-SUV-25-LATE-01	4255	1725	1630	Auto-Data — Jeep Cherokee II XJ 2.5	https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-2.5-i-118hp-1132
EU-JEEP-CHEROKEE-XJ-SUV-WIDE-LATE-01	4240	1790	1630	Auto-Data — Jeep Cherokee II XJ 2.1 TD	https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-2.1-td-86hp-1131
EU-JEEP-CHEROKEE-KJ-SUV-01	4430	1820	1865	Auto-Data — Jeep Cherokee III KJ 2.8 CRDi	https://www.auto-data.net/en/jeep-cherokee-iii-kj-2.8-crdi-163hp-automatic-29488
EU-JEEP-CHEROKEE-KK-SUV-01	4493	1839	1797	Auto-Data — Jeep Cherokee IV KK 2.8 CRD	https://www.auto-data.net/en/jeep-cherokee-iv-kk-2.8-crd-177hp-1124
EU-JEEP-CHEROKEE-XJ-SUV-WIDE-EARLY-01	4288	1790	1630	Auto-Data — Jeep Cherokee II XJ 4.0	https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-4.0-i-184hp-1139
EU-JEEP-CJ-CJ5-CONVERTIBLE-01	3424	1521	1717	Auto-Data — Jeep CJ-5 4.2	https://www.auto-data.net/en/jeep-cj-5-4.2-103hp-1196
EU-JEEP-COMMANDER-XK-VAN-01	4787	1900	1826	Auto-Data — Jeep Commander XK generation	https://www.auto-data.net/en/jeep-commander-xk-generation-334
EU-JEEP-COMPASS-MP-SUV-FWD-01	4394	1819	1629	Auto-Data — Jeep Compass II MP 1.4 MultiAir	https://www.auto-data.net/en/jeep-compass-ii-mp-1.4-multiair-140hp-30066
EU-JEEP-COMPASS-MK-SUV-01	4448	1812	1718	Auto-Data — Jeep Compass I MK facelift 2.2 CRD	https://www.auto-data.net/en/jeep-compass-i-mk-facelift-2011-2.2-crd-136hp-30026
EU-JEEP-COMPASS-III-SUV-01	4552	1900	1675	Autoelectrique — Jeep Compass Electric dimensions	https://www.elektrischeauto.be/fr/voitures-electriques/detail/jeep-compass-electrique-170-kw
EU-JEEP-COMPASS-MP-FACELIFT-SUV-4XE-01	4404	1819	1649	Automobile-Catalog — 2021 Jeep Compass 4xe 190	https://www.automobile-catalog.com/car/2021/3008900/jeep_compass_4xe_1_3_t4_phev_190.html
EU-JEEP-COMPASS-MP-SUV-4X4-01	4394	1819	1644	Auto-Data — Jeep Compass II MP 1.4 MultiAir 4x4	https://www.auto-data.net/en/jeep-compass-ii-mp-1.4-multiair-170hp-4x4-automatic-30135
EU-JEEP-COMPASS-MP-FACELIFT-SUV-FWD-01	4404	1819	1629	Auto-Data — Jeep Compass II MP facelift 1.5 e-Hybrid	https://www.auto-data.net/en/jeep-compass-ii-mp-facelift-2021-1.5-gse-130hp-e-hybrid-dct-46374
EU-JEEP-GLADIATOR-JT-PICKUP-01	5591	1894	1843	Auto-Data — Jeep Gladiator JT 3.0 MultiJet V6	https://www.auto-data.net/en/jeep-gladiator-jt-3.0-multijet-v6-264hp-4wd-automatic-43243
EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-01	4500	1800	1720	Auto-Data — Jeep Grand Cherokee I ZJ 5.9 V8	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.9i-v8-241hp-4x4-automatic-1173
EU-JEEP-GRAND-CHEROKEE-WJ-SUV-01	4611	1858	1805	Auto-Data — Jeep Grand Cherokee II WJ 4.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-ii-wj-4.7-v8-220hp-4x4-automatic-1161
EU-JEEP-GRAND-CHEROKEE-WK-SUV-4X4-01	4750	1870	1740	Auto-Data — Jeep Grand Cherokee III WK 3.7 4x4	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-3.7i-v6-201hp-4x4-automatic-31156
EU-JEEP-GRAND-CHEROKEE-WK-SUV-LATE-01	4775	1861	1749	Auto-Data — Jeep Grand Cherokee III WK 4.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-4.7i-v8-309hp-automatic-31227
EU-JEEP-GRAND-CHEROKEE-WK-SRT8-SUV-01	4785	1870	1710	Auto-Data — Jeep Grand Cherokee III WK SRT8	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-srt8-6.1i-v8-426hp-4x4-automatic-1157
EU-JEEP-GRAND-CHEROKEE-WK2-SUV-4X4-01	4822	1943	1781	Auto-Data — Jeep Grand Cherokee IV WK2 3.0 CRD 4x4	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-3.0-crd-241hp-4x4-automatic-22120
EU-JEEP-GRAND-CHEROKEE-WK2-FACELIFT-SUV-01	4828	1943	1802	Auto-Data — Jeep Grand Cherokee IV WK2 facelift 3.0 CRD	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-facelift-2013-3.0-crd-250hp-4x4-automatic-22125
EU-JEEP-GRAND-CHEROKEE-WK2-SUV-36-01	4822	1938	1761	Auto-Data — Jeep Grand Cherokee IV WK2 3.6 V6	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-3.6-v6-294hp-automatic-31140
EU-JEEP-GRAND-CHEROKEE-WL-SUV-01	4915	1969	1799	Auto-Data — Jeep Grand Cherokee WL generation	https://www.auto-data.net/en/jeep-grand-cherokee-model-159
EU-JEEP-GRAND-WAGONEER-SJ-SUV-01	4735	1900	1687	Automobile-Catalog — 1991 Jeep Grand Wagoneer	https://www.automobile-catalog.com/car/1991/1308290/jeep_grand_wagoneer.html
EU-JEEP-J10-SJ-PICKUP-01	4970	1730	1830	CarsGuide — 1983 Jeep J10 dimensions	https://www.carsguide.com.au/jeep/j10/car-dimensions/1983
EU-JEEP-J20-SJ-PICKUP-01	5232	2004	1796	Off-Roading Pro — Jeep J20 dimensions	https://offroadingpro.com/jeep-j20/
EU-JEEP-PATRIOT-MK-SUV-01	4410	1756	1637	Auto-Data — Jeep Patriot generation	https://www.auto-data.net/en/jeep-patriot-generation-338
```

[下载 left18448_7701-7800_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_7701-7800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2021/3008900/jeep_compass_4xe_1_3_t4_phev_190.html "https://www.automobile-catalog.com/car/2021/3008900/jeep_compass_4xe_1_3_t4_phev_190.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5352 行）
- 累计尺寸组：dimension_groups_final.tsv（1436 行）

