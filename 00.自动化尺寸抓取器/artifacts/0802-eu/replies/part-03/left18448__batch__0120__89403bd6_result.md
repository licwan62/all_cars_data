# 任务：left18448 第 11901-12000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0120__89403bd6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11901-12000 行

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
left18448 第 11901-12000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11901-12000_ktype_dimension_mapping_final.tsv
- left18448_11901-12000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Nissan	Qashqai +2 van	2.0 Allrad	Kasten/SUV	Allrad	Benzin	Aug 2008	Apr 2014	801396
Nissan	Qashqai +2 van	2.0 DCI Allrad	Kasten/SUV	Allrad	Diesel	Mar 2013	Nov 2013	801401
Nissan	Qashqai i	1.6	SUV	Frontantrieb	Benzin	Nov 2010	Dec 2013	11137
Nissan	Qashqai i	2	SUV	Frontantrieb	Benzin	Feb 2007	Dec 2013	11138
Nissan	Qashqai i	1.5 DCI	SUV	Frontantrieb	Diesel	Jan 2010	Dec 2013	11136
Nissan	Qashqai i	1.6 DCI	SUV	Frontantrieb	Diesel	Oct 2011	Dec 2013	11758
Nissan	Qashqai i	1.6 DCI Allrad	SUV	Allrad	Diesel	Oct 2011	Dec 2013	11757
Nissan	Qashqai i	2.0 Allrad	SUV	Allrad	Benzin	Feb 2007	Dec 2013	11140
Nissan	Qashqai i van	2	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Apr 2014	143136
Nissan	Qashqai i van	1.5 DCI	Kasten/SUV	Frontantrieb	Diesel	Mar 2013	Apr 2014	143138
Nissan	Qashqai i van	1.6 Cvtc	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Apr 2014	143135
Nissan	Qashqai i van	1.6 DCI	Kasten/SUV	Frontantrieb	Diesel	Mar 2013	Apr 2014	143139
Nissan	Qashqai i van	1.6 DCI Allrad	Kasten/SUV	Allrad	Diesel	Mar 2013	Apr 2014	143140
Nissan	Qashqai i van	2.0 Allrad	Kasten/SUV	Allrad	Benzin	Mar 2013	Apr 2014	143137
Nissan	Qashqai i van	2.0 DCI Allrad	Kasten/SUV	Allrad	Diesel	Mar 2013	Apr 2014	143141
Nissan	Qashqai ii	1.2 Dig-t	SUV	Frontantrieb	Benzin	Nov 2013	Aug 2018	100506
Nissan	Qashqai ii	1.3 Dig-t	SUV	Frontantrieb	Benzin	Oct 2020	Apr 2021	143002
Nissan	Qashqai ii	1.5 DCI	SUV	Frontantrieb	Diesel	Nov 2013	Aug 2018	100507
Nissan	Qashqai ii	1.6 DCI	SUV	Frontantrieb	Diesel	Nov 2013	Aug 2018	100508
Nissan	Qashqai ii	1.6 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	Nov 2013	Aug 2018	100509
Nissan	Qashqai ii	1.6 Dig-t	SUV	Frontantrieb	Benzin	Feb 2014	Aug 2018	108463
Nissan	Qashqai ii	2.0 ALL Mode 4x4-i	SUV	Allrad	Benzin	Dec 2013	Apr 2021	120309
Nissan	Qashqai iii	1.3 Dig-t	SUV	Frontantrieb	Benzin/Elektro	Apr 2021	-	144424
Nissan	Qashqai iii	1.3 Dig-t	SUV	Frontantrieb	Benzin/Elektro	Apr 2021	-	144425
Nissan	Qashqai iii	1.3 Dig-t Allrad	SUV	Allrad	Benzin/Elektro	Apr 2021	-	144426
Nissan	Qashqai iii	1.5 Vc-t E-power	SUV	Frontantrieb	Benzin/Elektro	Sep 2022	Jul 2025	148229
Nissan	Qashqai iii	1.5 Vc-t E-power	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	802533
Nissan	Quest	3.3	Großraumlimousine	Frontantrieb	Benzin	Sep 1998	Dec 2002	46425
Nissan	Quest	3.5 V6	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	-	57233
Nissan	Rogue	2.5	SUV	Frontantrieb	Benzin	Jan 2007	Dec 2015	59991
Nissan	Rogue	2.5 AWD	SUV	Allrad	Benzin	Jan 2007	Dec 2013	55276
Nissan	Sentra vi	2	Stufenheck	Frontantrieb	Benzin	Oct 2006	Dec 2012	47360
Nissan	Sentra vii	1.6	Stufenheck	Frontantrieb	Benzin	Aug 2014	-	114374
Nissan	Serena	1.6	Kasten/Großraumlimousine	Heckantrieb	Benzin	Feb 1993	Jun 2001	143190
Nissan	Serena	1.6	Kasten/Großraumlimousine	Heckantrieb	Benzin	Sep 1994	Jun 1999	143191
Nissan	Serena	2	Kasten/Großraumlimousine	Heckantrieb	Diesel	Jul 1992	Sep 1994	143192
Nissan	Serena	2.3	Kasten/Großraumlimousine	Heckantrieb	Diesel	Oct 1994	Sep 2001	143193
Nissan	Silvia	1.8	Coupe	Heckantrieb	Benzin	Jan 1979	May 1983	14267
Nissan	Silvia	2000 Turbo	Coupe	Heckantrieb	Benzin	Sep 1999	Dec 2003	121954
Nissan	Silvia	2000 Turbo	Coupe	Heckantrieb	Benzin	Sep 1999	Dec 2003	121955
Nissan	Skyline	2.5 Turbo	Coupe	Heckantrieb	Benzin	May 1998	Jan 2006	34617
Nissan	Skyline	2.6 Turbo 4X4	Coupe	Allrad	Benzin	Jan 1999	Feb 2008	34619
Nissan	Skyline	2.6 Turbo 4X4	Coupe	Allrad	Benzin	Oct 1999	Aug 2002	56822
Nissan	Skyline	370gt	Stufenheck	Heckantrieb	Benzin	Dec 2008	Dec 2014	124286
Nissan	Stanza	1.8 SGL	Stufenheck	Frontantrieb	Benzin	Mar 1983	Dec 1985	5055
Nissan	Sunny	1.3	Kombi	Frontantrieb	Benzin	Aug 1982	Aug 1990	17927
Nissan	Sunny	1.4 I 16V	Stufenheck	Frontantrieb	Benzin	Oct 1990	Jun 1995	17891
Nissan	Sunny	1.6 I 16V	Kasten/Kombi	Frontantrieb	Benzin	Oct 1992	Mar 2000	10646
Nissan	Sunny	1.6 I 16V 4WD	Stufenheck	Allrad	Benzin	Oct 1990	May 1995	10659
Nissan	Sunny	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	Nov 1990	Mar 2000	10639
Nissan	Sunny	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1990	May 1995	10645
Nissan	Teana ii	2.5 Four Allrad	Stufenheck	Allrad	Benzin	Jun 2008	Dec 2012	124551
Nissan	Teana iii	2.5	Stufenheck	Frontantrieb	Benzin	Sep 2013	-	107403
Nissan	Terrano	2.4 4WD	Geländewagen geschlossen	Allrad	Benzin	May 1996	Jan 2002	5988
Nissan	Terrano	2.4 4WD	Geländewagen geschlossen	Allrad	Benzin	May 1996	Sep 2007	5989
Nissan	Terrano	2.7 TDI 4WD	Geländewagen geschlossen	Allrad	Diesel	May 1996	Sep 2007	5990
Nissan	Terrano	2.7 TDI 4WD	Kasten	Allrad	Diesel	Jun 1998	Sep 2007	12495
Nissan	Terrano	3.0 DI 4WD	Kasten	Allrad	Diesel	Apr 2003	Sep 2007	12496
Nissan	Terrano	3.0 DI 4WD	Geländewagen geschlossen	Allrad	Diesel	May 2002	Sep 2007	16773
Nissan	Terrano	3.5 4WD	Geländewagen geschlossen	Allrad	Benzin	Jul 2000	Jun 2003	148307
Nissan	Townstar	1.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2021	-	146448
Nissan	Townstar	1.3	Großraumlimousine	Frontantrieb	Benzin	Dec 2021	-	146449
Nissan	Townstar	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Mar 2022	-	148295
Nissan	Townstar	Electric	Großraumlimousine	Frontantrieb	Elektro	Sep 2022	-	150815
Nissan	Townstar evalia	1.3	Großraumlimousine	Frontantrieb	Benzin	May 2024	-	800234
Nissan	Townstar evalia	Electric	Großraumlimousine	Frontantrieb	Elektro	May 2024	-	800233
Nissan	Trade	75	Kasten	Heckantrieb	Diesel	May 1997	Dec 2000	34269
Nissan	Trade	100	Kasten	Heckantrieb	Diesel	Jan 1996	Dec 1998	34267
Nissan	Trade	3.0 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1996	Dec 1998	34266
Nissan	Trade	3.0 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1994	Dec 1998	34268
Nissan	Urvan	2	Kasten	Heckantrieb	Benzin	May 1987	May 1997	10648
Nissan	Urvan	2.3 D	Kasten	Heckantrieb	Diesel	Jan 1988	May 1997	10649
Nissan	Urvan	2.5 D	Kasten	Heckantrieb	Diesel	Dec 1988	May 1997	10720
Nissan	Vanette	1.5	Bus	Heckantrieb	Benzin	Oct 1986	Dec 1995	18493
Nissan	Vanette	1.5	Kasten	Heckantrieb	Benzin	Oct 1986	Dec 1995	18494
Nissan	Vanette	2.0 D	Kasten	Heckantrieb	Diesel	Jul 1991	Jan 1995	10819
Nissan	X-Trail i	2	SUV	Frontantrieb	Benzin	Jul 2001	Jan 2013	19069
Nissan	X-Trail i	2.0 4X4	SUV	Allrad	Benzin	Jul 2001	Jan 2013	15969
Nissan	X-Trail i	2.2 DCI	SUV	Frontantrieb	Diesel	Dec 2003	Jan 2013	19070
Nissan	X-Trail i	2.2 DCI 4X4	SUV	Allrad	Diesel	Jun 2001	Dec 2008	17887
Nissan	X-Trail i	2.2 DI 4X4	SUV	Allrad	Diesel	Jul 2001	Oct 2005	15970
Nissan	X-Trail i	2.5 4X4	SUV	Allrad	Benzin	Sep 2002	Jan 2013	17194
Nissan	X-Trail ii	2.0 DCI 4X4	SUV	Allrad	Diesel	Oct 2009	Nov 2013	57658
Nissan	X-Trail iii	1.3 Dig-t	SUV	Frontantrieb	Benzin	Jun 2021	-	145046
Nissan	X-Trail iii	1.6 DCI	SUV	Frontantrieb	Diesel	Apr 2014	-	106464
Nissan	X-Trail iii	1.6 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	Apr 2014	-	106465
Nissan	X-Trail iii	1.6 Dig-t	SUV	Frontantrieb	Benzin	Jun 2015	-	116533
Nissan	X-Trail iii	2.0 DCI	SUV	Frontantrieb	Diesel	Oct 2016	-	125349
Nissan	X-Trail iii	2.0 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	Oct 2016	-	125350
Nissan	X-Trail iv	1.5 E-power	SUV	Frontantrieb	Benzin/Elektro	Oct 2024	-	801206
Nissan	X-Trail iv	1.5 E-power E-4orce	SUV	Allrad	Benzin/Elektro	Oct 2024	-	801207
Nissan	X-Trail iv	1.5 Vc-t E-power	SUV	Frontantrieb	Benzin/Elektro	Sep 2022	-	149408
Nissan	X-Trail iv	1.5 Vc-t E-power E-4orce	SUV	Allrad	Benzin/Elektro	Sep 2022	-	149407
Nissan	X-Trail iv	1.5 Vc-t Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Sep 2022	-	148371
Nissan	X-Trail van	DCI	Kasten/SUV	Frontantrieb	Diesel	Jan 2011	Feb 2014	142932
Nissan	X-Trail van	DCI 4X4	Kasten/SUV	Allrad	Diesel	Jan 2013	Feb 2014	142933
Nissan	X-Trail van	DCI 4X4	Kasten/SUV	Allrad	Diesel	Mar 2013	Feb 2014	142934
NSU	Prinz	1	Stufenheck	Heckantrieb	Benzin	Jan 1964	Dec 1967	122018
NSU	Ro 80	1	Stufenheck	Frontantrieb	Benzin	Oct 1967	Jul 1977	11123
NSU	Sportprinz	0.6	Coupe	Heckantrieb	Benzin	Apr 1959	Dec 1967	122017


--- Round 1 / 首次发送 ---
## 更新点

已完成车型聚类、尺寸组复用及机械终检。仅 `5990`、`16773` 因明确覆盖 Terrano 3 门短轴与 5 门长轴外廓而拆分；动力、驱动及普通配置均复用对应尺寸组。

## 进度

* 输入 Ktype：100
* Ktype 映射：102 行
* DIMENSION_GROUP：46 组
* READY：102
* PENDING：0
* 引用闭合、固定列数、ID 唯一、三维与来源非空检查：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801396	801396	Van	Qashqai +2 I	NJ10	5	EU-NISSAN-QASHQAI-NJ10-VAN-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
801401	801401	Van	Qashqai +2 I facelift	NJ10	5	EU-NISSAN-QASHQAI-NJ10-VAN-FACELIFT-001	HIGH		READY
11137	11137	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH		READY
11138	11138	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-J10-SUV-PREFL-001	HIGH		READY
11136	11136	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-J10-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
11758	11758	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH		READY
11757	11757	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH		READY
11140	11140	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-J10-SUV-PREFL-001	HIGH		READY
143136	143136	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143138	143138	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143135	143135	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143139	143139	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143140	143140	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143137	143137	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
143141	143141	Van	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
100506	100506	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
143002	143002	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-J11-SUV-FACELIFT-001	HIGH		READY
100507	100507	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
100508	100508	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
100509	100509	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
108463	108463	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
120309	120309	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
144424	144424	SUV	Qashqai III	J12	5	EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	HIGH		READY
144425	144425	SUV	Qashqai III	J12	5	EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	HIGH		READY
144426	144426	SUV	Qashqai III	J12	5	EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	HIGH		READY
148229	148229	SUV	Qashqai III	J12	5	EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	HIGH		READY
802533	802533	SUV	Qashqai III	J12	5	EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	HIGH	改款未形成独立外廓，复用同一尺寸组	READY
46425	46425	MPV	Quest II	V41	5	EU-NISSAN-QUEST-V41-MPV-STANDARD-001	HIGH		READY
57233	57233	MPV	Quest IV	RE52	5	EU-NISSAN-QUEST-RE52-MPV-STANDARD-001	HIGH		READY
59991	59991	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-S35-SUV-STANDARD-001	HIGH		READY
55276	55276	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-S35-SUV-STANDARD-001	HIGH		READY
47360	47360	Sedan	Sentra VI	B16	4	EU-NISSAN-SENTRA-B16-SEDAN-STANDARD-001	HIGH		READY
114374	114374	Sedan	Sentra VII	B17	4	EU-NISSAN-SENTRA-B17-SEDAN-STANDARD-001	HIGH		READY
143190	143190	MPV	Serena C23	C23	5	EU-NISSAN-SERENA-C23-MPV-STANDARD-001	MEDIUM	动力版本标称高度小幅差异不构成独立车身	READY
143191	143191	MPV	Serena C23	C23	5	EU-NISSAN-SERENA-C23-MPV-STANDARD-001	MEDIUM	动力版本标称高度小幅差异不构成独立车身	READY
143192	143192	MPV	Serena C23	C23	5	EU-NISSAN-SERENA-C23-MPV-STANDARD-001	MEDIUM	动力版本标称高度小幅差异不构成独立车身	READY
143193	143193	MPV	Serena C23	C23	5	EU-NISSAN-SERENA-C23-MPV-STANDARD-001	MEDIUM	动力版本标称高度小幅差异不构成独立车身	READY
14267	14267	Coupe	Silvia III	S110	2	EU-NISSAN-SILVIA-S110-COUPE-STANDARD-001	HIGH		READY
121954	121954	Coupe	Silvia VII	S15	2	EU-NISSAN-SILVIA-S15-COUPE-STANDARD-001	HIGH		READY
121955	121955	Coupe	Silvia VII	S15	2	EU-NISSAN-SILVIA-S15-COUPE-STANDARD-001	HIGH		READY
34617	34617	Coupe	Skyline X	R34	2	EU-NISSAN-SKYLINE-R34-COUPE-GTT-001	HIGH		READY
34619	34619	Coupe	Skyline GT-R X	R34	2	EU-NISSAN-SKYLINE-R34-COUPE-GTR-001	HIGH		READY
56822	56822	Coupe	Skyline GT-R X	R34	2	EU-NISSAN-SKYLINE-R34-COUPE-GTR-001	HIGH		READY
124286	124286	Sedan	Skyline XII	V36	4	EU-NISSAN-SKYLINE-V36-SEDAN-370GT-001	HIGH		READY
5055	5055	Sedan	Stanza T11	T11	4	EU-NISSAN-STANZA-T11-SEDAN-STANDARD-001	MEDIUM		READY
17927	17927	Wagon	Sunny I Wagon	B11	5	EU-NISSAN-SUNNY-B11-WAGON-STANDARD-001	MEDIUM		READY
17891	17891	Sedan	Sunny III	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-STANDARD-001	HIGH		READY
10646	10646	Van	Sunny III Wagon	Y10		EU-NISSAN-SUNNY-Y10-VAN-STANDARD-001	HIGH	商用改装未改变旅行车车身外廓	READY
10659	10659	Sedan	Sunny III	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-STANDARD-001	HIGH		READY
10639	10639	Van	Sunny III Wagon	Y10		EU-NISSAN-SUNNY-Y10-VAN-STANDARD-001	HIGH	商用改装未改变旅行车车身外廓	READY
10645	10645	Hatchback	Sunny III Hatch	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5DR-001	HIGH		READY
124551	124551	Sedan	Teana II	J32	4	EU-NISSAN-TEANA-J32-SEDAN-4WD-001	HIGH		READY
107403	107403	Sedan	Teana III	L33	4	EU-NISSAN-TEANA-L33-SEDAN-STANDARD-001	HIGH		READY
5988	5988	SUV	Terrano II	R20	3	EU-NISSAN-TERRANO-R20-SUV-3DR-PREFL-001	HIGH		READY
5989	5989	SUV	Terrano II	R20	5	EU-NISSAN-TERRANO-R20-SUV-5DR-PREFL-001	HIGH		READY
5990_3dr	5990	SUV	Terrano II	R20	3	EU-NISSAN-TERRANO-R20-SUV-3DR-PREFL-001	HIGH	Ktype覆盖3门短轴分支	READY
5990_5dr	5990	SUV	Terrano II	R20	5	EU-NISSAN-TERRANO-R20-SUV-5DR-PREFL-001	HIGH	Ktype覆盖5门长轴分支	READY
12495	12495	Van	Terrano II	R20	3	EU-NISSAN-TERRANO-R20-SUV-3DR-PREFL-001	HIGH	商用改装未改变3门短轴外廓	READY
12496	12496	Van	Terrano II facelift	R20	3	EU-NISSAN-TERRANO-R20-SUV-3DR-FACELIFT-001	HIGH	商用改装未改变3门短轴外廓	READY
16773_3dr	16773	SUV	Terrano II facelift	R20	3	EU-NISSAN-TERRANO-R20-SUV-3DR-FACELIFT-001	HIGH	Ktype覆盖3门短轴分支	READY
16773_5dr	16773	SUV	Terrano II facelift	R20	5	EU-NISSAN-TERRANO-R20-SUV-5DR-FACELIFT-001	HIGH	Ktype覆盖5门长轴分支	READY
148307	148307	SUV	Terrano R50	R50	5	EU-NISSAN-TERRANO-R50-SUV-STANDARD-001	MEDIUM	按R50同车身Pathfinder/Terrano外廓匹配	READY
146448	146448	Van	Townstar I	NFK		EU-NISSAN-TOWNSTAR-NFK-VAN-L1-001	HIGH	组合车身条目按L1厢式外廓匹配	READY
146449	146449	MPV	Townstar I	NFK	5	EU-NISSAN-TOWNSTAR-NFK-MPV-L1-001	HIGH		READY
148295	148295	Van	Townstar I	NFK		EU-NISSAN-TOWNSTAR-NFK-VAN-L1-001	HIGH	组合车身条目按L1厢式外廓匹配	READY
150815	150815	MPV	Townstar I	NFK	5	EU-NISSAN-TOWNSTAR-NFK-MPV-L1-001	HIGH		READY
800234	800234	MPV	Townstar I Evalia	NFK	5	EU-NISSAN-TOWNSTAR-NFK-MPV-L2-EVALIA-001	HIGH	Evalia按L2乘用外廓匹配	READY
800233	800233	MPV	Townstar I Evalia	NFK	5	EU-NISSAN-TOWNSTAR-NFK-MPV-L2-EVALIA-001	HIGH	Evalia按L2乘用外廓匹配	READY
34269	34269	Van	Trade	PF		EU-NISSAN-TRADE-PF-VAN-STANDARD-001	LOW	无轴距级别字段，采用标准量产厢式外廓	READY
34267	34267	Van	Trade	PF		EU-NISSAN-TRADE-PF-VAN-STANDARD-001	LOW	无轴距级别字段，采用标准量产厢式外廓	READY
34266	34266	Pickup	Trade	PF		EU-NISSAN-TRADE-PF-PICKUP-STANDARD-001	LOW	无轴距级别字段，采用标准量产卡车外廓	READY
34268	34268	Pickup	Trade	PF		EU-NISSAN-TRADE-PF-PICKUP-STANDARD-001	LOW	无轴距级别字段，采用标准量产卡车外廓	READY
10648	10648	Van	Urvan E24	E24		EU-NISSAN-URVAN-E24-VAN-LWB-001	MEDIUM	输入未给轴距级别，采用欧洲常见长轴厢式外廓	READY
10649	10649	Van	Urvan E24	E24		EU-NISSAN-URVAN-E24-VAN-LWB-001	MEDIUM	输入未给轴距级别，采用欧洲常见长轴厢式外廓	READY
10720	10720	Van	Urvan E24	E24		EU-NISSAN-URVAN-E24-VAN-LWB-001	MEDIUM	输入未给轴距级别，采用欧洲常见长轴厢式外廓	READY
18493	18493	MPV	Vanette C22	C22		EU-NISSAN-VANETTE-C22-STANDARD-001	MEDIUM		READY
18494	18494	Van	Vanette C22	C22		EU-NISSAN-VANETTE-C22-STANDARD-001	MEDIUM		READY
10819	10819	Van	Vanette C22	C22		EU-NISSAN-VANETTE-C22-STANDARD-001	MEDIUM		READY
19069	19069	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
15969	15969	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
19070	19070	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
17887	17887	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
15970	15970	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
17194	17194	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	HIGH	动力与驱动版本共用同一车身外廓	READY
57658	57658	SUV	X-Trail II	T31	5	EU-NISSAN-XTRAIL-T31-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
145046	145046	SUV	X-Trail III facelift	T32	5	EU-NISSAN-XTRAIL-T32-SUV-FACELIFT-001	HIGH		READY
106464	106464	SUV	X-Trail III	T32	5	EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
106465	106465	SUV	X-Trail III	T32	5	EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
116533	116533	SUV	X-Trail III	T32	5	EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
125349	125349	SUV	X-Trail III	T32	5	EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
125350	125350	SUV	X-Trail III	T32	5	EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	MEDIUM	按投产起始阶段匹配；跨改款不派生分支	READY
801206	801206	SUV	X-Trail IV	T33	5	EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	HIGH		READY
801207	801207	SUV	X-Trail IV	T33	5	EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	HIGH		READY
149408	149408	SUV	X-Trail IV	T33	5	EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	HIGH		READY
149407	149407	SUV	X-Trail IV	T33	5	EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	HIGH		READY
148371	148371	SUV	X-Trail IV	T33	5	EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	HIGH		READY
142932	142932	Van	X-Trail II facelift	T31	5	EU-NISSAN-XTRAIL-T31-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
142933	142933	Van	X-Trail II facelift	T31	5	EU-NISSAN-XTRAIL-T31-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
142934	142934	Van	X-Trail II facelift	T31	5	EU-NISSAN-XTRAIL-T31-SUV-FACELIFT-001	HIGH	商用改装未改变车身外廓	READY
122018	122018	Sedan	Prinz 4		2	EU-NSU-PRINZ4-GEN1-SEDAN-STANDARD-001	HIGH		READY
11123	11123	Sedan	Ro 80		4	EU-NSU-RO80-GEN1-SEDAN-STANDARD-001	HIGH		READY
122017	122017	Coupe	Sportprinz		2	EU-NSU-SPORTPRINZ-GEN1-COUPE-STANDARD-001	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_11901-12000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-QASHQAI-NJ10-VAN-PREFL-001	4525	1780	1645	Automobile-Catalog, 2008 Nissan Qashqai+2 phase-I 4WD specifications	https://www.automobile-catalog.com/make/nissan/qashqai_1gen/qashqai_j10_plus_1_4wd/2008.html
EU-NISSAN-QASHQAI-NJ10-VAN-FACELIFT-001	4541	1780	1645	Auto-Data, Nissan Qashqai+2 I NJ10 facelift generation specifications	https://www.auto-data.net/en/nissan-qashqai-2-i-nj10-facelift-2010-generation-3813
EU-NISSAN-QASHQAI-J10-SUV-PREFL-001	4315	1780	1615	Auto-Data, Nissan Qashqai I J10 2.0 specifications	https://www.auto-data.net/en/nissan-qashqai-i-j10-2.0-141hp-731
EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-001	4330	1780	1615	Auto-Data, Nissan Qashqai I J10 facelift generation specifications	https://www.auto-data.net/en/nissan-qashqai-i-j10-facelift-2010-generation-3812
EU-NISSAN-QASHQAI-J11-SUV-PREFL-001	4377	1806	1590	Auto-Data, Nissan Qashqai II J11 1.5 dCi specifications	https://www.auto-data.net/en/nissan-qashqai-ii-j11-1.5-dci-110hp-19093
EU-NISSAN-QASHQAI-J11-SUV-FACELIFT-001	4394	1806	1590	Auto-Data, Nissan Qashqai II J11 facelift 1.3 DIG-T specifications	https://www.auto-data.net/en/nissan-qashqai-ii-j11-facelift-2017-1.3i-160hp-dct-34522
EU-NISSAN-QASHQAI-J12-SUV-STANDARD-001	4425	1835	1625	Auto-Data, Nissan Qashqai III J12 e-Power specifications	https://www.auto-data.net/en/nissan-qashqai-iii-j12-e-power-1.5-vc-t-190hp-full-hybrid-automatic-46241
EU-NISSAN-QUEST-V41-MPV-STANDARD-001	4948	1902	1709	Automobile-Catalog, 2000 Nissan Quest GXE specifications	https://www.automobile-catalog.com/car/2000/2324630/nissan_quest_gxe.html
EU-NISSAN-QUEST-RE52-MPV-STANDARD-001	5100	1971	1816	Edmunds, 2012 Nissan Quest S features and specifications	https://www.edmunds.com/nissan/quest/2012/st-101413894/features-specs/
EU-NISSAN-ROGUE-S35-SUV-STANDARD-001	4646	1801	1659	Auto-Data, Nissan Rogue I S35 2.5i specifications	https://www.auto-data.net/en/nissan-rogue-i-s35-2.5i-170hp-cvt-831
EU-NISSAN-SENTRA-B16-SEDAN-STANDARD-001	4567	1790	1512	Auto-Data, Nissan Sentra VI generation specifications	https://www.auto-data.net/en/nissan-sentra-vi-generation-269
EU-NISSAN-SENTRA-B17-SEDAN-STANDARD-001	4610	1760	1495	Auto-Data, Nissan Sentra VII B17 1.8 specifications	https://www.auto-data.net/en/nissan-sentra-vii-b17-1.8-130hp-46999
EU-NISSAN-SERENA-C23-MPV-STANDARD-001	4315	1710	1840	Auto-Data, Nissan Serena C23M 1.6 16V specifications	https://www.auto-data.net/en/nissan-serena-c23m-1.6-16v-97hp-936
EU-NISSAN-SILVIA-S110-COUPE-STANDARD-001	4400	1680	1310	Nissan Global Heritage Collection, Silvia S110 specifications	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/silvia093.html
EU-NISSAN-SILVIA-S15-COUPE-STANDARD-001	4445	1695	1285	Auto-Data, Nissan Silvia S15 generation specifications	https://www.auto-data.net/en/nissan-silvia-s15-generation-89
EU-NISSAN-SKYLINE-R34-COUPE-GTT-001	4580	1725	1340	Auto-Data, Nissan Skyline R34 2.5 turbo specifications	https://www.auto-data.net/en/nissan-skyline-x-r34-2.5-i-24v-turbo-280hp-automatic-359
EU-NISSAN-SKYLINE-R34-COUPE-GTR-001	4600	1785	1360	Auto-Data, Nissan Skyline GT-R R34 specifications	https://www.auto-data.net/en/nissan-skyline-gt-r-x-r34-2.6-i-24v-turbo-4wd-280hp-360
EU-NISSAN-SKYLINE-V36-SEDAN-370GT-001	4755	1770	1450	Carfolio, Nissan Skyline 370GT specifications	https://www.carfolio.com/nissan-skyline-370gt-207086
EU-NISSAN-STANZA-T11-SEDAN-STANDARD-001	4280	1665	1390	Automobile-Catalog, 1984 Nissan Stanza 1.8 SGL 4-door specifications	https://www.automobile-catalog.com/car/1984/2215400/nissan_stanza_1_8_sgl_4d.html
EU-NISSAN-SUNNY-B11-WAGON-STANDARD-001	4255	1620	1390	Drive.Place, Nissan Sunny B11 wagon specifications	https://nissan.drive.place/sunny/b11/group_wagon_5/197857
EU-NISSAN-SUNNY-N14-SEDAN-STANDARD-001	4230	1690	1395	Auto-Data, Nissan Sunny III N14 generation specifications	https://www.auto-data.net/en/nissan-sunny-iii-n14-generation-140
EU-NISSAN-SUNNY-Y10-VAN-STANDARD-001	4175	1665	1520	Auto-Data, Nissan Sunny III Wagon Y10 generation specifications	https://www.auto-data.net/en/nissan-sunny-iii-wagon-y10-generation-142
EU-NISSAN-SUNNY-N14-HATCHBACK-5DR-001	4145	1690	1395	Auto-Data, Nissan Sunny III Hatch N14 5-door generation specifications	https://www.auto-data.net/en/nissan-sunny-iii-hatch-n14-5-doors-generation-141
EU-NISSAN-TEANA-J32-SEDAN-4WD-001	4850	1795	1500	Automobile-Catalog, Nissan Teana 250XE Four specifications	https://www.automobile-catalog.com/car/2010/2282510/nissan_teana_250xe_four.html
EU-NISSAN-TEANA-L33-SEDAN-STANDARD-001	4863	1830	1482	Auto.ru catalog, Nissan Teana L33 specifications	https://auto.ru/catalog/cars/nissan/teana/20098974/20098977/specifications/
EU-NISSAN-TERRANO-R20-SUV-3DR-PREFL-001	4185	1755	1830	Auto-Data, Nissan Terrano II R20 3-door specifications	https://www.auto-data.net/en/nissan-terrano-ii-r20-2.4-i-12v-3-dr-116hp-651
EU-NISSAN-TERRANO-R20-SUV-5DR-PREFL-001	4665	1755	1850	Auto-Data, Nissan Terrano II R20 5-door specifications	https://www.auto-data.net/en/nissan-terrano-ii-r20-2.4-i-12v-5-dr-118hp-652
EU-NISSAN-TERRANO-R20-SUV-3DR-FACELIFT-001	4217	1755	1830	Auto-Data, Nissan Terrano II R20 facelift 3-door specifications	https://www.auto-data.net/en/nissan-terrano-ii-r20-3.0-tdi-16v-3-dr-154hp-automatic-24962
EU-NISSAN-TERRANO-R20-SUV-5DR-FACELIFT-001	4697	1755	1850	Auto-Data, Nissan Terrano II R20 facelift 5-door specifications	https://www.auto-data.net/en/nissan-terrano-ii-r20-3.0-tdi-16v-5-dr-154hp-660
EU-NISSAN-TERRANO-R50-SUV-STANDARD-001	4640	1820	1750	Automobile-Catalog, Nissan Pathfinder/Terrano R50 3.5 V6 4x4 specifications	https://www.automobile-catalog.com/car/2000/2305085/nissan_pathfinder_3_5_v6_4x4.html
EU-NISSAN-TOWNSTAR-NFK-VAN-L1-001	4488	1860	1864	Auto-Data, Nissan Townstar Van generation specifications	https://www.auto-data.net/en/nissan-townstar-van-generation-8776
EU-NISSAN-TOWNSTAR-NFK-MPV-L1-001	4486	1860	1848	Automobile Dimension, Nissan Townstar dimensions without mirrors	https://www.automobiledimension.com/model/nissan/townstar
EU-NISSAN-TOWNSTAR-NFK-MPV-L2-EVALIA-001	4911	1860	1815	Nissan official, Townstar Combi L2 dimensions	https://www.nissan.com.mt/vehicles/new-vehicles/townstar-combi-2025/dimensions.html
EU-NISSAN-TRADE-PF-VAN-STANDARD-001	5050	1890	2150	ArabWheels, Nissan Trade specifications	https://www.arabwheels.ae/new-cars/nissan/trade/specifications/
EU-NISSAN-TRADE-PF-PICKUP-STANDARD-001	5050	1890	2150	ArabWheels, Nissan Trade truck specifications	https://www.arabwheels.ae/new-cars/nissan/trade/specifications/
EU-NISSAN-URVAN-E24-VAN-LWB-001	4860	1690	1950	CarsGuide, 1987 Nissan Urvan dimensions	https://www.carsguide.com.au/nissan/urvan/car-dimensions/1987
EU-NISSAN-VANETTE-C22-STANDARD-001	4365	1690	1900	Auto-Data, Nissan Vanette C22 2.0 D specifications	https://www.auto-data.net/en/nissan-vanette-2.0-d-67hp-793
EU-NISSAN-XTRAIL-T30-SUV-STANDARD-001	4455	1765	1675	Auto-Data, Nissan X-Trail I T30 facelift specifications	https://www.auto-data.net/en/nissan-x-trail-i-t30-facelift-2003-2.0-140hp-29886
EU-NISSAN-XTRAIL-T31-SUV-PREFL-001	4630	1785	1685	Auto-Data, Nissan X-Trail II T31 2.0 dCi 4x4 specifications	https://www.auto-data.net/en/nissan-x-trail-ii-t31-2.0-dci-150hp-4x4-906
EU-NISSAN-XTRAIL-T31-SUV-FACELIFT-001	4635	1790	1700	Auto-Data, Nissan X-Trail II T31 facelift specifications	https://www.auto-data.net/en/nissan-x-trail-ii-t31-facelift-2010-2.0-dci-150hp-4x4-17039
EU-NISSAN-XTRAIL-T32-SUV-PREFL-001	4640	1820	1715	Auto-Data, Nissan X-Trail III T32 1.6 dCi specifications	https://www.auto-data.net/en/nissan-x-trail-iii-t32-1.6-dci-130hp-22219
EU-NISSAN-XTRAIL-T32-SUV-FACELIFT-001	4690	1820	1740	Auto-Data, Nissan X-Trail III T32 facelift generation specifications	https://www.auto-data.net/en/nissan-x-trail-iii-t32-facelift-2017-generation-5996
EU-NISSAN-XTRAIL-T33-SUV-STANDARD-001	4680	1840	1720	Auto-Data, Nissan X-Trail IV T33 e-Power specifications	https://www.auto-data.net/en/nissan-x-trail-iv-t33-1.5-vc-t-204hp-e-power-automatic-46451
EU-NSU-PRINZ4-GEN1-SEDAN-STANDARD-001	3440	1490	1360	Auta5P, NSU Prinz 4 L specifications	https://auta5p.eu/lang/en/katalog/auto.php?idf=NSU-Prinz-4-L-23079
EU-NSU-RO80-GEN1-SEDAN-STANDARD-001	4780	1760	1410	Auto-Data, NSU Ro 80 specifications	https://www.auto-data.net/en/audi-nsu-ro-80-1.0-115hp-4529
EU-NSU-SPORTPRINZ-GEN1-COUPE-STANDARD-001	3560	1520	1235	Engine in Detail, NSU Sport-Prinz specifications	https://www.engineindetail.com/cars/nsu/prinz/sport-prinz-1959-1967
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_11901-12000_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3342 行）
- 累计尺寸组：dimension_groups_final.tsv（1039 行）

