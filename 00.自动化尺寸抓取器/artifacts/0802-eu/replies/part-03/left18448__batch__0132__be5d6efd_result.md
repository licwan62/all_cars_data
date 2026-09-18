# 任务：left18448 第 13101-13200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0132__be5d6efd


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13101-13200 行

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
left18448 第 13101-13200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13101-13200_ktype_dimension_mapping_final.tsv
- left18448_13101-13200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Peugeot	3008 van	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2009	Aug 2016	142642
Peugeot	3008 van	HDI 110	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2009	Aug 2016	142640
Peugeot	3008 van	HDI 150	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2009	Aug 2016	142641
Peugeot	3008 van	Puretech 130	Kasten/SUV	Frontantrieb	Benzin	May 2016	-	142646
Peugeot	305 ii	1.6	Stufenheck	Frontantrieb	Benzin	Nov 1982	Dec 1988	113329
Peugeot	308 cc	1.6 HDI	Cabriolet	Frontantrieb	Diesel	Mar 2013	Dec 2014	58885
Peugeot	308 cc	2.0 Cvvt	Cabriolet	Frontantrieb	Benzin	Jul 2009	Dec 2014	118677
Peugeot	308 i	1.6 Bioflex	Schrägheck	Frontantrieb	Benzin/Ethanol	Apr 2008	Oct 2014	5975
Peugeot	308 i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Jul 2010	Oct 2014	33864
Peugeot	308 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Mar 2013	Oct 2014	58886
Peugeot	308 i	2.0 Bioflex	Schrägheck	Frontantrieb	Benzin/Ethanol	Jan 2008	Dec 2012	118675
Peugeot	308 i	2.0 HDI	Schrägheck	Frontantrieb	Diesel	Jul 2010	Dec 2012	33865
Peugeot	308 i	2.0 HDI	Schrägheck	Frontantrieb	Diesel	Oct 2011	Oct 2014	56201
Peugeot	308 i	2.0 HDI	Schrägheck	Frontantrieb	Diesel	Apr 2012	Oct 2014	58133
Peugeot	308 ii	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	Nov 2013	Jun 2021	100834
Peugeot	308 ii	1.2 THP 130	Schrägheck	Frontantrieb	Benzin	Nov 2013	Jun 2021	100835
Peugeot	308 ii	1.2 VTI 72	Schrägheck	Frontantrieb	Benzin	Sep 2013	Jun 2021	59726
Peugeot	308 ii	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Nov 2013	Jun 2021	100836
Peugeot	308 ii	1.6 GT 205	Schrägheck	Frontantrieb	Benzin	Jun 2014	Jun 2021	108171
Peugeot	308 ii	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Jun 2015	Jun 2021	115504
Peugeot	308 ii	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Aug 2015	Jun 2021	117761
Peugeot	308 ii	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Sep 2013	Jun 2021	59728
Peugeot	308 ii	1.6 HDI / Bluehdi 115	Schrägheck	Frontantrieb	Diesel	Sep 2013	Jun 2021	59730
Peugeot	308 ii	1.6 HDI 100	Schrägheck	Frontantrieb	Diesel	Apr 2014	Jun 2021	105880
Peugeot	308 ii	1.6 THP	Schrägheck	Frontantrieb	Benzin	Sep 2013	Jun 2021	59724
Peugeot	308 ii	1.6 THP 125	Schrägheck	Frontantrieb	Benzin	Sep 2013	Jun 2021	59725
Peugeot	308 ii	1.6 THP 150	Schrägheck	Frontantrieb	Benzin	Mar 2014	Jun 2021	110757
Peugeot	308 ii	1.6 THP 163	Schrägheck	Frontantrieb	Benzin	Jun 2014	Jun 2021	110760
Peugeot	308 ii	2.0 Bluehdi 150	Schrägheck	Frontantrieb	Diesel	Nov 2013	Jun 2021	100837
Peugeot	308 ii	2.0 GT Bluehdi 180	Schrägheck	Frontantrieb	Diesel	Jun 2014	Jun 2021	108172
Peugeot	308 iii	1.2 Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	-	801565
Peugeot	308 iii	1.6 Hybrid 195	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2025	-	801487
Peugeot	308 iii	Bluehdi 130	Schrägheck	Frontantrieb	Diesel	Jul 2021	-	144520
Peugeot	308 iii	E-308	Schrägheck	Frontantrieb	Elektro	Aug 2023	-	152826
Peugeot	308 iii	Hybrid 136	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2023	Mar 2025	154610
Peugeot	308 iii	Hybrid 180	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2021	-	144523
Peugeot	308 iii	Hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2021	-	144522
Peugeot	308 iii	Puretech 110	Schrägheck	Frontantrieb	Benzin	Jul 2021	-	144511
Peugeot	308 iii	Puretech 130	Schrägheck	Frontantrieb	Benzin	Jul 2021	-	144519
Peugeot	308 sw i	2	Kombi	Frontantrieb	Benzin	Jan 2008	Dec 2011	156215
Peugeot	308 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	Nov 2009	Oct 2014	11074
Peugeot	308 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	Mar 2013	Oct 2014	59020
Peugeot	308 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	Apr 2011	Oct 2014	56738
Peugeot	308 sw ii	1.2 THP 110	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	105876
Peugeot	308 sw ii	1.2 THP 130	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	100644
Peugeot	308 sw ii	1.6 Bluehdi 100	Kombi	Frontantrieb	Diesel	Apr 2014	Jun 2021	105882
Peugeot	308 sw ii	1.6 Bluehdi 120	Kombi	Frontantrieb	Diesel	Mar 2014	Jun 2021	105877
Peugeot	308 sw ii	1.6 GT 205	Kombi	Frontantrieb	Benzin	Feb 2015	Jun 2021	108173
Peugeot	308 sw ii	1.6 HDI / Bluehdi 115	Kombi	Frontantrieb	Diesel	Mar 2014	Jun 2021	100647
Peugeot	308 sw ii	1.6 HDI 92	Kombi	Frontantrieb	Diesel	Mar 2014	Jun 2021	100646
Peugeot	308 sw ii	1.6 THP 125	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	110749
Peugeot	308 sw ii	1.6 THP 150	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	110750
Peugeot	308 sw ii	1.6 THP 155	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	100645
Peugeot	308 sw ii	1.6 VTI	Kombi	Frontantrieb	Benzin	Mar 2014	Jun 2021	110748
Peugeot	308 sw ii	2.0 Bluehdi 150	Kombi	Frontantrieb	Diesel	Mar 2014	Jun 2021	100648
Peugeot	308 sw ii	2.0 GT HDI 180 / Bluehdi 180	Kombi	Frontantrieb	Diesel	Jun 2014	Jun 2021	108174
Peugeot	308 sw iii	1.2 Hybrid 145	Kombi	Frontantrieb	Benzin/Elektro	Mar 2025	-	801566
Peugeot	308 sw iii	Bluehdi 130	Kombi	Frontantrieb	Diesel	Jul 2021	-	145073
Peugeot	308 sw iii	E-308	Kombi	Frontantrieb	Elektro	Aug 2023	-	152829
Peugeot	308 sw iii	Hybrid 180	Kombi	Frontantrieb	Benzin/Elektro	Jul 2021	-	145075
Peugeot	308 sw iii	Hybrid 195	Kombi	Frontantrieb	Benzin/Elektro	Feb 2025	-	801488
Peugeot	308 sw iii	Hybrid 225	Kombi	Frontantrieb	Benzin/Elektro	Jul 2021	-	145077
Peugeot	308 sw iii	Puretech 110	Kombi	Frontantrieb	Benzin	Jul 2021	-	145072
Peugeot	308 sw iii	Puretech 130	Kombi	Frontantrieb	Benzin	Jul 2021	-	145071
Peugeot	308 sw iii	Puretech 136	Kombi	Frontantrieb	Benzin/Elektro	Aug 2023	Mar 2025	154612
Peugeot	309 ii	1.6	Schrägheck	Frontantrieb	Benzin	Jul 1989	Dec 1993	12621
Peugeot	309 ii	1.8 Diesel	Schrägheck	Frontantrieb	Diesel	Jul 1989	Dec 1993	12620
Peugeot	309 ii	1.9 GTI 16V	Schrägheck	Frontantrieb	Benzin	Aug 1989	Jul 1990	12619
Peugeot	405 ii	1.6	Stufenheck	Frontantrieb	Benzin	Aug 1992	May 1997	59941
Peugeot	405 ii	1.9	Stufenheck	Frontantrieb	Benzin	Jun 1992	Apr 1997	144387
Peugeot	408 ii	E-210	Schrägheck	Frontantrieb	Elektro	Nov 2024	-	800997
Peugeot	408 ii	Hybrid 136	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2023	-	155860
Peugeot	408 ii	Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	-	801567
Peugeot	408 ii	Hybrid 180	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2022	-	148309
Peugeot	408 ii	Hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2022	-	148310
Peugeot	408 ii	Hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2025	-	803434
Peugeot	408 ii	Hybrid 240	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2026	-	803191
Peugeot	408 ii	Puretech 130	Schrägheck	Frontantrieb	Benzin	Jul 2022	-	148306
Peugeot	508 i	1.6 Bluehdi 120	Stufenheck	Frontantrieb	Diesel	Mar 2014	Dec 2018	113670
Peugeot	508 i	1.6 HDI	Stufenheck	Frontantrieb	Diesel	Feb 2012	Dec 2018	12960
Peugeot	508 i	1.6 HDI	Stufenheck	Frontantrieb	Diesel	Sep 2014	Dec 2018	117327
Peugeot	508 i	1.6 THP	Stufenheck	Frontantrieb	Benzin	Nov 2010	Dec 2018	12769
Peugeot	508 i	1.6 THP	Stufenheck	Frontantrieb	Benzin	Jan 2012	Dec 2018	55284
Peugeot	508 i	1.6 THP	Stufenheck	Frontantrieb	Benzin	Sep 2011	Dec 2018	56438
Peugeot	508 i	1.6 VTI	Stufenheck	Frontantrieb	Benzin	Nov 2010	Dec 2018	12767
Peugeot	508 i	2.0 Bluehdi 150	Stufenheck	Frontantrieb	Diesel	Apr 2014	Dec 2018	105884
Peugeot	508 i	2.0 Bluehdi 180	Stufenheck	Frontantrieb	Diesel	Apr 2014	Dec 2018	105886
Peugeot	508 i	2.0 HDI	Stufenheck	Frontantrieb	Diesel	Nov 2010	Dec 2018	12772
Peugeot	508 i	2.0 HDI Hybrid4 AWC	Stufenheck	Allrad	Diesel/Elektro	Nov 2010	Dec 2018	58646
Peugeot	508 ii	Hybrid 180	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2023	-	154615
Peugeot	508 sw i	1.6	Kombi	Frontantrieb	Benzin	Feb 2012	Dec 2018	109335
Peugeot	508 sw i	1.6 Bluehdi 120	Kombi	Frontantrieb	Diesel	Mar 2014	Dec 2018	113671
Peugeot	508 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	Feb 2012	Dec 2018	12961
Peugeot	508 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	Sep 2014	Dec 2018	117329
Peugeot	508 sw i	1.6 THP	Kombi	Frontantrieb	Benzin	Nov 2010	Dec 2018	12778
Peugeot	508 sw i	1.6 VTI	Kombi	Frontantrieb	Benzin	Nov 2010	Dec 2018	12776
Peugeot	508 sw i	2.0 Bluehdi 150	Kombi	Frontantrieb	Diesel	Apr 2014	Dec 2018	105885
Peugeot	508 sw i	2.0 Bluehdi 180	Kombi	Frontantrieb	Diesel	Apr 2014	Dec 2018	105887
Peugeot	508 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	Nov 2010	Dec 2018	12783
Peugeot	508 sw i	2.0 HDI 180 RXH	Kombi	Frontantrieb	Diesel	Oct 2014	Dec 2018	108563


--- Round 1 / 首次发送 ---
## 更新点

已完成缓存复用、独立外廓建组及机械终检。Peugeot 508 I 的 2014 改款前后车长、车宽存在明确变化，因此对生产期跨越改款的 Ktype 建立 `_prefl` / `_facelift` 分支；508 RXH、308 GT/GTi、309 柴油及 GTI 16 等具有明确高度差异的工厂外廓单独建组。([CarsGuide][1])

## 进度

* 输入 Ktype：100
* 最终映射行：118
* DIMENSION_GROUP：23
* PENDING：0
* id 唯一、尺寸组唯一、映射引用闭合、尺寸及来源非空检查：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142642	142642	Van	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	Commercial derivative; passenger-body exterior reused.	READY
142640	142640	Van	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	Commercial derivative; passenger-body exterior reused.	READY
142641	142641	Van	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	Commercial derivative; passenger-body exterior reused.	READY
142646	142646	Van	Peugeot 3008 II		5	EU-PEUGEOT-3008-II-SUV-01	MEDIUM	Commercial derivative; passenger-body exterior reused.	READY
113329	113329	Sedan	Peugeot 305 II	581M	4	EU-PEUGEOT-305-II-SEDAN-01	MEDIUM	Standard 581M saloon exterior.	READY
58885	58885	Convertible	Peugeot 308 CC I	T7	2	EU-PEUGEOT-308-I-CONVERTIBLE-01	HIGH		READY
118677	118677	Convertible	Peugeot 308 CC I	T7	2	EU-PEUGEOT-308-I-CONVERTIBLE-01	HIGH		READY
5975	5975	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
33864	33864	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
58886	58886	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
118675	118675	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
33865	33865	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
56201	56201	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
58133	58133	Hatchback	Peugeot 308 I	T7		EU-PEUGEOT-308-I-HATCHBACK-01	HIGH		READY
100834	100834	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
100835	100835	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
59726	59726	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
100836	100836	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
108171	108171	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-PERFORMANCE-01	HIGH	Factory GT/GTi lowered exterior.	READY
115504	115504	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-PERFORMANCE-01	HIGH	Factory GT/GTi lowered exterior.	READY
117761	117761	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-PERFORMANCE-01	HIGH	Factory GT/GTi lowered exterior.	READY
59728	59728	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
59730	59730	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
105880	105880	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
59724	59724	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
59725	59725	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
110757	110757	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
110760	110760	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
100837	100837	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	HIGH		READY
108172	108172	Hatchback	Peugeot 308 II	T9	5	EU-PEUGEOT-308-II-HATCHBACK-PERFORMANCE-01	HIGH	Factory GT/GTi lowered exterior.	READY
801565	801565	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
801487	801487	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
144520	144520	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
152826	152826	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
154610	154610	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
144523	144523	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
144522	144522	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
144511	144511	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
144519	144519	Hatchback	Peugeot 308 III		5	EU-PEUGEOT-308-III-HATCHBACK-01	HIGH		READY
156215	156215	Wagon	Peugeot 308 SW I	T7	5	EU-PEUGEOT-308-I-SW-01	HIGH		READY
11074	11074	Wagon	Peugeot 308 SW I	T7	5	EU-PEUGEOT-308-I-SW-01	HIGH		READY
59020	59020	Wagon	Peugeot 308 SW I	T7	5	EU-PEUGEOT-308-I-SW-01	HIGH		READY
56738	56738	Wagon	Peugeot 308 SW I	T7	5	EU-PEUGEOT-308-I-SW-01	HIGH		READY
105876	105876	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
100644	100644	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
105882	105882	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
105877	105877	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
108173	108173	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-GT-01	HIGH	Factory GT lowered exterior.	READY
100647	100647	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
100646	100646	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
110749	110749	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
110750	110750	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
100645	100645	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
110748	110748	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
100648	100648	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-STANDARD-01	HIGH		READY
108174	108174	Wagon	Peugeot 308 SW II	T9	5	EU-PEUGEOT-308-II-SW-GT-01	HIGH	Factory GT lowered exterior.	READY
801566	801566	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
145073	145073	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
152829	152829	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
145075	145075	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
801488	801488	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
145077	145077	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
145072	145072	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
145071	145071	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
154612	154612	Wagon	Peugeot 308 SW III		5	EU-PEUGEOT-308-III-SW-01	HIGH		READY
12621	12621	Hatchback	Peugeot 309 II			EU-PEUGEOT-309-II-HATCHBACK-STANDARD-01	HIGH	Standard 1.6 ride height.	READY
12620	12620	Hatchback	Peugeot 309 II			EU-PEUGEOT-309-II-HATCHBACK-DIESEL-01	HIGH	Factory diesel ride height.	READY
12619	12619	Hatchback	Peugeot 309 II		3	EU-PEUGEOT-309-II-HATCHBACK-GTI16-01	HIGH	Factory GTI 16 ride height.	READY
59941	59941	Sedan	Peugeot 405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
144387	144387	Sedan	Peugeot 405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
800997	800997	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
155860	155860	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
801567	801567	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
148309	148309	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
148310	148310	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
803434	803434	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
803191	803191	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
148306	148306	Hatchback	Peugeot 408 II	P54	5	EU-PEUGEOT-408-II-HATCHBACK-01	HIGH		READY
113670_prefl	113670	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
113670_facelift	113670	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12960_prefl	12960	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12960_facelift	12960	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
117327	117327	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	HIGH		READY
12769_prefl	12769	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12769_facelift	12769	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
55284_prefl	55284	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
55284_facelift	55284	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
56438_prefl	56438	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
56438_facelift	56438	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12767_prefl	12767	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12767_facelift	12767	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105884_prefl	105884	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105884_facelift	105884	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105886_prefl	105886	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105886_facelift	105886	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12772_prefl	12772	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12772_facelift	12772	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
58646_prefl	58646	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
58646_facelift	58646	Sedan	Peugeot 508 I		4	EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
154615	154615	Hatchback	Peugeot 508 II	R8	5	EU-PEUGEOT-508-II-PHASE-I-HATCHBACK-01	HIGH		READY
109335_prefl	109335	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
109335_facelift	109335	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
113671_prefl	113671	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
113671_facelift	113671	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12961_prefl	12961	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12961_facelift	12961	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
117329	117329	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	HIGH		READY
12778_prefl	12778	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12778_facelift	12778	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12776_prefl	12776	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12776_facelift	12776	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105885_prefl	105885	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105885_facelift	105885	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105887_prefl	105887	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
105887_facelift	105887	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12783_prefl	12783	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-PREFACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
12783_facelift	12783	Wagon	Peugeot 508 SW I		5	EU-PEUGEOT-508-I-SW-FACELIFT-01	MEDIUM	Production span covers the dimension-changing 2014 facelift.	READY
108563	108563	Wagon	Peugeot 508 I		5	EU-PEUGEOT-508-I-RXH-FACELIFT-01	HIGH	Factory RXH crossover-wagon exterior.	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_13101-13200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-3008-I-MPV-01	4365	1837	1639	Auto-Data, Peugeot 3008 I Phase I 2.0 HDi 150	https://www.auto-data.net/en/peugeot-3008-i-phase-i-2009-2.0-hdi-fap-150hp-5422
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Automobile-Catalog, 2017 Peugeot 3008 1.2 PureTech 130	https://www.automobile-catalog.com/make/peugeot/3008_2/3008_2_1_2wd/2017.html
EU-PEUGEOT-305-II-SEDAN-01	4263	1630	1407	Automobile-Catalog, 1986 Peugeot 305 GL	https://www.automobile-catalog.com/car/1986/2568590/peugeot_305_gl.html
EU-PEUGEOT-308-I-CONVERTIBLE-01	4440	1817	1426	Automobile-Catalog, 2012 Peugeot 308 CC 1.6 THP 156	https://www.automobile-catalog.com/car/2012/2622875/peugeot_308_cc_1_6_thp_156_automatic.html
EU-PEUGEOT-308-I-HATCHBACK-01	4276	1815	1498	Auto-Data, Peugeot 308 I Phase I 1.6 VTi 120 5-door	https://www.auto-data.net/en/peugeot-308-i-phase-i-2007-1.6-16v-vti-120hp-5d-5372
EU-PEUGEOT-308-II-HATCHBACK-STANDARD-01	4253	1804	1457	Automobile-Catalog, 2016 Peugeot 308 1.2 PureTech 130	https://www.automobile-catalog.com/car/2016/2624285/peugeot_308_1_2_puretech_130.html
EU-PEUGEOT-308-II-HATCHBACK-PERFORMANCE-01	4253	1804	1446	Automobile-Catalog, 2016 Peugeot 308 GT 1.6 THP 205	https://www.automobile-catalog.com/car/2016/2624315/peugeot_308_gt_1_6_thp_205.html
EU-PEUGEOT-308-III-HATCHBACK-01	4367	1852	1441	Automobile-Catalog, 2022 Peugeot 308 Hybrid 180 PHEV	https://www.automobile-catalog.com/car/2022/3046730/peugeot_308_hybrid_180_phev.html
EU-PEUGEOT-308-I-SW-01	4500	1815	1555	Automobile-Catalog, 2012 Peugeot 308 SW 1.6 VTi 120	https://www.automobile-catalog.com/car/2012/2622725/peugeot_308_sw_1_6_vti_120.html
EU-PEUGEOT-308-II-SW-STANDARD-01	4585	1804	1461	Automobile-Catalog, 2016 Peugeot 308 SW 1.2 PureTech 130; body height excludes rails/antenna	https://www.automobile-catalog.com/car/2016/2624465/peugeot_308_sw_1_2_puretech_130.html
EU-PEUGEOT-308-II-SW-GT-01	4585	1804	1457	Automobile-Catalog, 2016 Peugeot 308 SW GT 1.6 THP 205	https://www.automobile-catalog.com/car/2016/2624615/peugeot_308_sw_gt_1_6_thp_205.html
EU-PEUGEOT-308-III-SW-01	4636	1852	1442	Automobile-Catalog, 2022 Peugeot 308 SW Hybrid 180 PHEV	https://www.automobile-catalog.com/car/2022/3046760/peugeot_308_sw_hybrid_180_phev.html
EU-PEUGEOT-309-II-HATCHBACK-STANDARD-01	4051	1628	1392	Automobile-Catalog, 1990 Peugeot 309 Automatic 1.6	https://www.automobile-catalog.com/car/1990/2578715/peugeot_309_automatic_1_6.html
EU-PEUGEOT-309-II-HATCHBACK-DIESEL-01	4051	1628	1380	Automobile-Catalog, 1990 Peugeot 309 SRDT 1.8	https://www.automobile-catalog.com/car/1990/2578805/peugeot_309_srdt.html
EU-PEUGEOT-309-II-HATCHBACK-GTI16-01	4051	1628	1384	Automobile-Catalog, 1990 Peugeot 309 GTI 16	https://www.automobile-catalog.com/car/1990/2578985/peugeot_309_gti_16.html
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406	Automobile-Catalog, 1993 Peugeot 405 Style 1.6	https://www.automobile-catalog.com/car/1993/2586605/peugeot_405_style_1_6.html
EU-PEUGEOT-408-II-HATCHBACK-01	4687	1848	1478	Automobile-Catalog, 2023 Peugeot 408 Hybrid 180 PHEV	https://www.automobile-catalog.com/car/2023/3210770/peugeot_408_hybrid_180_phev.html
EU-PEUGEOT-508-I-SEDAN-PREFACELIFT-01	4792	1853	1456	Automobile-Catalog, 2012 Peugeot 508 1.6 THP 156	https://www.automobile-catalog.com/car/2012/2625065/peugeot_508_1_6_thp_156_155.html
EU-PEUGEOT-508-I-SEDAN-FACELIFT-01	4830	1828	1456	Automobile-Catalog, 2015 Peugeot 508 1.6 BlueHDi 120	https://www.automobile-catalog.com/car/2015/2625800/peugeot_508_1_6_bluehdi_120.html
EU-PEUGEOT-508-II-PHASE-I-HATCHBACK-01	4750	1859	1403	Automobile-Catalog, 2023 Peugeot 508 Hybrid 180 PHEV	https://www.automobile-catalog.com/car/2023/3210740/peugeot_508_hybrid_180_phev.html
EU-PEUGEOT-508-I-SW-PREFACELIFT-01	4813	1853	1476	Automobile-Catalog, 2011 Peugeot 508 SW 2.0 HDi 163	https://www.automobile-catalog.com/car/2011/2625335/peugeot_508_sw_2_0_hdi_fap_163_165.html
EU-PEUGEOT-508-I-SW-FACELIFT-01	4829	1828	1476	Automobile-Catalog, 2015 Peugeot 508 SW 1.6 BlueHDi 120	https://www.automobile-catalog.com/car/2015/2625815/peugeot_508_sw_1_6_bluehdi_120.html
EU-PEUGEOT-508-I-RXH-FACELIFT-01	4828	1864	1525	Automobile-Catalog, 2015 Peugeot 508 RXH 2.0 BlueHDi 180	https://www.automobile-catalog.com/car/2015/2625920/peugeot_508_rxh_2_0_bluehdi_180.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_13101-13200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carsguide.com.au/peugeot/508/car-dimensions/2011?utm_source=chatgpt.com "Peugeot 508 Dimensions 2011 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4775 行）
- 累计尺寸组：dimension_groups_final.tsv（1301 行）

