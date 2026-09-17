# 任务：left18448 第 15301-15400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0154__d5a822f0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15301-15400 行

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
left18448 第 15301-15400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15301-15400_ktype_dimension_mapping_final.tsv
- left18448_15301-15400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	4511	1731	1429
EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	4511	1731	1448
EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	4572	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Skoda	Octavia	1.4 TSI	Kombi	Frontantrieb	Benzin	Aug 2014	Oct 2020	115158
Skoda	Octavia	1.4 TSI	Kombi	Frontantrieb	Benzin	Jun 2020	-	144843
Skoda	Octavia	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	146987
Skoda	Octavia	1.4 TSI G-tec	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2013	Feb 2017	106544
Skoda	Octavia	1.4 TSI G-tec	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2012	Feb 2017	106545
Skoda	Octavia	1.4 TSI IV	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2020	-	145197
Skoda	Octavia	1.4 TSI IV	Kombi	Frontantrieb	Benzin/Elektro	Jun 2020	-	145198
Skoda	Octavia	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2024	-	158004
Skoda	Octavia	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	Apr 2024	-	158005
Skoda	Octavia	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Feb 2017	Oct 2020	128418
Skoda	Octavia	1.5 TSI	Kombi	Frontantrieb	Benzin	Feb 2017	Oct 2020	128420
Skoda	Octavia	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2024	-	158002
Skoda	Octavia	1.5 TSI	Kombi	Frontantrieb	Benzin	Apr 2024	-	158003
Skoda	Octavia	1.5 TSI E-tec	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2020	-	143425
Skoda	Octavia	1.5 TSI E-tec	Kombi	Frontantrieb	Benzin/Elektro	Nov 2020	-	143426
Skoda	Octavia	1.6 FSI	Schrägheck	Frontantrieb	Benzin	Feb 2004	Oct 2008	17974
Skoda	Octavia	1.6 FSI	Kombi	Frontantrieb	Benzin	Feb 2004	Oct 2008	18247
Skoda	Octavia	1.6 SRE	Kombi	Frontantrieb	Benzin	Jan 2014	Feb 2017	107944
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	May 2015	58760
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	Nov 2012	May 2015	58766
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	Oct 2020	59077
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	Nov 2012	Oct 2020	59078
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Feb 2017	100629
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	May 2013	Feb 2017	100630
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2017	Oct 2020	126000
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	Feb 2017	Oct 2020	126001
Skoda	Octavia	1.6 TDI 4X4	Kombi	Allrad	Diesel	Nov 2012	May 2015	59488
Skoda	Octavia	1.6 TDI 4X4	Schrägheck	Allrad	Diesel	May 2013	May 2015	108643
Skoda	Octavia	1.6 TDI 4X4	Schrägheck	Allrad	Diesel	May 2015	Feb 2017	115209
Skoda	Octavia	1.6 TDI 4X4	Kombi	Allrad	Diesel	May 2015	Feb 2017	115210
Skoda	Octavia	1.8 T	Kombi	Frontantrieb	Benzin	Jul 1998	Dec 2010	10270
Skoda	Octavia	1.8 T	Schrägheck	Frontantrieb	Benzin	Aug 1997	Dec 2010	11346
Skoda	Octavia	1.8 T 4X4	Schrägheck	Allrad	Benzin	May 2001	May 2006	16086
Skoda	Octavia	1.8 T 4X4	Kombi	Allrad	Benzin	May 2001	May 2006	16087
Skoda	Octavia	1.8 TSI	Schrägheck	Frontantrieb	Benzin	Mar 2009	Jun 2013	7867
Skoda	Octavia	1.8 TSI	Kombi	Frontantrieb	Benzin	Mar 2009	Jun 2013	7868
Skoda	Octavia	1.8 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Oct 2020	58759
Skoda	Octavia	1.8 TSI	Kombi	Frontantrieb	Benzin	Nov 2012	Oct 2020	58765
Skoda	Octavia	1.8 TSI 4X4	Kombi	Allrad	Benzin	Nov 2012	Feb 2017	59489
Skoda	Octavia	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	May 2014	Oct 2020	108644
Skoda	Octavia	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Jun 1997	Dec 2003	8704
Skoda	Octavia	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2002	Sep 2004	17475
Skoda	Octavia	1.9 TDI	Kombi	Frontantrieb	Diesel	Sep 2002	Sep 2004	17476
Skoda	Octavia	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Jun 2004	Dec 2010	17970
Skoda	Octavia	1.9 TDI	Kombi	Frontantrieb	Diesel	Sep 2004	Dec 2010	18248
Skoda	Octavia	1.9 TDI 4X4	Kombi	Allrad	Diesel	Nov 1999	Feb 2006	12243
Skoda	Octavia	1.9 TDI 4X4	Kombi	Allrad	Diesel	Sep 2000	Jan 2006	15294
Skoda	Octavia	1.9 TDI 4X4	Kombi	Allrad	Diesel	Nov 2004	Dec 2010	18481
Skoda	Octavia	2.0 4X4	Kombi	Allrad	Benzin	Aug 2000	Sep 2004	16088
Skoda	Octavia	2.0 FSI	Schrägheck	Frontantrieb	Benzin	Nov 2004	Oct 2008	18478
Skoda	Octavia	2.0 FSI	Kombi	Frontantrieb	Benzin	Nov 2004	Oct 2008	18479
Skoda	Octavia	2.0 FSI 4X4	Kombi	Allrad	Benzin	Nov 2004	Apr 2009	18480
Skoda	Octavia	2.0 RS	Kombi	Frontantrieb	Benzin	Aug 2024	-	800480
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	Oct 2020	58761
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2012	Oct 2020	58767
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	Feb 2017	59079
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2012	Feb 2017	59080
Skoda	Octavia	2.0 TDI / TDI RS 4X4	Kombi	Allrad	Diesel	May 2013	Oct 2020	108648
Skoda	Octavia	2.0 TDI / TDI RS 4X4	Schrägheck	Allrad	Diesel	May 2013	Oct 2020	108649
Skoda	Octavia	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	Feb 2004	Apr 2013	17971
Skoda	Octavia	2.0 TDI 16V	Kombi	Frontantrieb	Diesel	Feb 2004	May 2013	18249
Skoda	Octavia	2.0 TDI 16V 4X4	Kombi	Allrad	Diesel	May 2010	Feb 2013	6042
Skoda	Octavia	2.0 TDI 4X4	Kombi	Allrad	Diesel	Nov 2012	Oct 2020	59490
Skoda	Octavia	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	May 2013	Oct 2020	108645
Skoda	Octavia	2.0 TDI 4X4	Kombi	Allrad	Diesel	Sep 2020	-	143518
Skoda	Octavia	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	Sep 2020	-	144928
Skoda	Octavia	2.0 TDI RS	Schrägheck	Frontantrieb	Diesel	May 2013	Oct 2020	59676
Skoda	Octavia	2.0 TDI RS	Kombi	Frontantrieb	Diesel	May 2013	Oct 2020	59679
Skoda	Octavia	2.0 TSI 4X4	Kombi	Allrad	Benzin	Sep 2020	-	143519
Skoda	Octavia	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	Jul 2020	-	145013
Skoda	Octavia	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	Jan 2025	-	801352
Skoda	Octavia	2.0 TSI 4X4	Kombi	Allrad	Benzin	Jan 2025	-	801353
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	May 2013	Feb 2017	59677
Skoda	Octavia	2.0 TSI RS	Kombi	Frontantrieb	Benzin	Nov 2012	Feb 2017	59680
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	May 2015	Oct 2020	115160
Skoda	Octavia	2.0 TSI RS	Kombi	Frontantrieb	Benzin	May 2015	Oct 2020	115161
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	Feb 2017	Oct 2020	126002
Skoda	Octavia	2.0 TSI RS	Kombi	Frontantrieb	Benzin	Feb 2017	Oct 2020	126003
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	Aug 2024	-	800493
Skoda	Octavia	RS 1.8 T	Schrägheck	Frontantrieb	Benzin	May 2001	Jan 2006	15293
Skoda	Octavia	RS 1.8 T	Kombi	Frontantrieb	Benzin	Aug 2002	Jan 2006	16945
Skoda	Rapid	1.2	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	56161
Skoda	Rapid	1.2	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	107504
Skoda	Rapid	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	59064
Skoda	Rapid	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	105755
Skoda	Rapid	1.6	Schrägheck	Frontantrieb	Benzin	May 2015	Mar 2022	123729
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2017	Dec 2019	128465
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2017	Dec 2019	128467
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2017	Dec 2019	128469
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2017	Dec 2019	128470
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	May 2015	39229
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	May 2015	39231
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	May 2015	56162
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	May 2015	56165
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2019	115178
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2019	115179
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2019	115182
Skoda	Rapid	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2019	115183
Skoda	Rapid	1.3 S	Coupe	Heckantrieb	Benzin	Sep 1984	Dec 1990	5073
Skoda	Rapid	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2019	115181


--- Round 1 / 首次发送 ---
## 1）更新点

* 已复用 12 个跨批次 Octavia I–III 标准尺寸组，没有改写既有 ID 或三维。
* 新建 Octavia I/III RS、Octavia IV 改款前/后及 RS、Rapid Liftback/Spaceback/Coupe 等 15 个独立尺寸组。Octavia IV 数据采用 Škoda 官方技术资料，Rapid Liftback 与 Spaceback 采用官方技术资料。
* Rapid 重复动力行已根据 NH3/NK3/NK6 Liftback 与 NH1 Spaceback 的 Ktype 归属解耦，未按发动机重复创建尺寸组。([AIC德国][1])
* 对确实跨越且三维发生变化的改款 Ktype 使用 `_prefl`、`_facelift` 派生行；Ktype 108648、108649 输入明确同时包含标准 TDI 与 TDI RS，因此保留标准/RS及改款阶段的物理分支。
* 机械终检通过：表头、列数、ID 唯一性、100 个输入 Ktype 覆盖、引用闭合、正整数三维、来源、直接 URL 和下载文件均完整。

## 2）进度

输入 Ktype：100
最终映射行：131
READY：131
PENDING：0
DIMENSION_GROUP：27
孤立尺寸组：0

## 3）最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
115158_prefl	115158	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
115158_facelift	115158	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
144843	144843	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
146987	146987	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
106544	106544	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
106545	106545	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
145197	145197	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
145198	145198	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
158004	158004	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-FACELIFT-01	HIGH		READY
158005	158005	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-FACELIFT-01	HIGH		READY
128418	128418	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH		READY
128420	128420	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
158002	158002	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-FACELIFT-01	HIGH		READY
158003	158003	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-FACELIFT-01	HIGH		READY
143425	143425	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
143426	143426	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
17974	17974	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	HIGH		READY
18247	18247	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH		READY
107944	107944	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
58760	58760	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
58766	58766	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
59077_prefl	59077	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59077_facelift	59077	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59078_prefl	59078	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59078_facelift	59078	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
100629	100629	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
100630	100630	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
126000	126000	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH		READY
126001	126001	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
59488	59488	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
108643	108643	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
115209	115209	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
115210	115210	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
10270_prefl	10270	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
10270_facelift	10270	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
11346_prefl	11346	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
11346_facelift	11346	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
16086	16086	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH		READY
16087	16087	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH		READY
7867	7867	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	HIGH		READY
7868	7868	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH		READY
58759_prefl	58759	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58759_facelift	58759	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58765_prefl	58765	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58765_facelift	58765	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59489	59489	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
108644_prefl	108644	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
108644_facelift	108644	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
8704_prefl	8704	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
8704_facelift	8704	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
17475	17475	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH		READY
17476	17476	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH		READY
17970_prefl	17970	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
17970_facelift	17970	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18248_prefl	18248	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18248_facelift	18248	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
12243_prefl	12243	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
12243_facelift	12243	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
15294	15294	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH		READY
18481_prefl	18481	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18481_facelift	18481	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
16088_prefl	16088	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
16088_facelift	16088	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the Sep 2000 exterior facelift; dimensions require phase-specific branches.	READY
18478	18478	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	HIGH		READY
18479	18479	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH		READY
18480_prefl	18480	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18480_facelift	18480	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
800480	800480	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-RS-FACELIFT-01	HIGH		READY
58761_prefl	58761	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58761_facelift	58761	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58767_prefl	58767	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
58767_facelift	58767	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59079	59079	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
59080	59080	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
108648_std_prefl	108648	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108648_std_facelift	108648	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108648_rs_prefl	108648	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-PREFL-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108648_rs_facelift	108648	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-FACELIFT-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108649_std_prefl	108649	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108649_std_facelift	108649	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108649_rs_prefl	108649	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-PREFL-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
108649_rs_facelift	108649	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-FACELIFT-01	HIGH	Input Ktype explicitly covers both standard TDI and TDI RS 4x4 and spans the 2017 facelift; four evidence-backed physical branches are retained.	READY
17971_prefl	17971	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
17971_facelift	17971	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18249_prefl	18249	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
18249_facelift	18249	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2008/2009 exterior facelift; dimensions require phase-specific branches.	READY
6042	6042	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	HIGH		READY
59490_prefl	59490	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
59490_facelift	59490	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
108645_prefl	108645	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
108645_facelift	108645	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific branches.	READY
143518	143518	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
144928	144928	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
59676_prefl	59676	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-PREFL-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
59676_facelift	59676	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-FACELIFT-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
59679_prefl	59679	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-PREFL-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
59679_facelift	59679	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-FACELIFT-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
143519	143519	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
145013	145013	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
801352	801352	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-FACELIFT-01	HIGH		READY
801353	801353	Wagon	Octavia IV	NX5/PV5	5	EU-SKODA-OCTAVIA-IV-WAGON-FACELIFT-01	HIGH		READY
59677	59677	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-PREFL-01	HIGH		READY
59680	59680	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-PREFL-01	HIGH		READY
115160_prefl	115160	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-PREFL-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
115160_facelift	115160	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-FACELIFT-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
115161_prefl	115161	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-PREFL-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
115161_facelift	115161	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-FACELIFT-01	HIGH	RS Ktype production span crosses the 2017 exterior facelift; dimensions require phase-specific RS branches.	READY
126002	126002	Hatchback	Octavia III	5E3/NL3/NR3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-RS-FACELIFT-01	HIGH		READY
126003	126003	Wagon	Octavia III	5E5/5E6	5	EU-SKODA-OCTAVIA-III-WAGON-RS-FACELIFT-01	HIGH		READY
800493	800493	Hatchback	Octavia IV	NX3/NN3/PV3	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-RS-FACELIFT-01	HIGH		READY
15293	15293	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-HATCHBACK-RS-FACELIFT-01	HIGH		READY
16945	16945	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-WAGON-RS-FACELIFT-01	HIGH		READY
56161	56161	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
107504	107504	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
59064	59064	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
105755	105755	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
123729	123729	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
128465	128465	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
128467	128467	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
128469	128469	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
128470	128470	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
39229	39229	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
39231	39231	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
56162	56162	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
56165	56165	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
115178	115178	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
115179	115179	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
115182	115182	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
115183	115183	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolves to the shorter Rapid Spaceback body.	READY
5073	5073	Coupe	Garde/Rapid	743/747	2	EU-SKODA-RAPID-GARDE-RAPID-COUPE-STANDARD-01	MEDIUM	Ktype maps to the rear-engined Garde/Rapid two-door coupe family.	READY
115181	115181	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolves to the Rapid liftback body, not the shorter Spaceback.	READY
```

[下载 left18448_15301-15400_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15301-15400_ktype_dimension_mapping_final.tsv)

## 4）最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	4507	1731	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3135110/skoda_octavia_1_4_16v.html
EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	4511	1731	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3134480/skoda_octavia_1_8_20v.html
EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	4513	1731	1457	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/3135125/skoda_octavia_combi_1_4_16v.html
EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	4511	1731	1448	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/3134900/skoda_octavia_combi_1_8_20v_turbo_automatic.html
EU-SKODA-OCTAVIA-I-HATCHBACK-RS-FACELIFT-01	4507	1731	1413	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/3135500/skoda_octavia_rs.html
EU-SKODA-OCTAVIA-I-WAGON-RS-FACELIFT-01	4513	1731	1444	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/3135515/skoda_octavia_combi_rs.html
EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	4569	1769	1462	Auto-Data	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-2.0-tdi-pd-16v-140hp-55842
EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	4572	1769	1462	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/3137540/skoda_octavia_1_4_16v_75.html
EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	4569	1769	1468	Auto-Data	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-2.0-tdi-pd-16v-140hp-55849
EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	4572	1769	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3137810/skoda_octavia_combi_1_9_tdi_pd_105.html
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Automoli	https://www.automoli.com/en/vehicles/skoda/octavia/octavia-iii-facelift-2017-5261/
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/3145325/skoda_octavia_1_4_tsi_140_dsg.html
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Auto-Data	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-1.8-tsi-180hp-27415
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/3145580/skoda_octavia_combi_1_4_tsi_140.html
EU-SKODA-OCTAVIA-III-HATCHBACK-RS-PREFL-01	4685	1814	1449	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/3145850/skoda_octavia_rs_2_0_tdi_cr_184_dsg.html
EU-SKODA-OCTAVIA-III-HATCHBACK-RS-FACELIFT-01	4689	1814	1448	Škoda technical data	https://cdn.skoda-storyboard.com/2017/07/TD-OCTAVIA-RS-245-en.pdf
EU-SKODA-OCTAVIA-III-WAGON-RS-PREFL-01	4685	1814	1452	Škoda technical data	https://cdn.skoda-storyboard.com/2016/05/160530_TD_SKODA_Octavia_Combi_RS_en.pdf
EU-SKODA-OCTAVIA-III-WAGON-RS-FACELIFT-01	4689	1814	1452	Škoda technical data	https://cdn.skoda-storyboard.com/2016/05/TD-OCTAVIA-COMBI-RS-en.pdf
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470	Škoda technical data	https://cdn.skoda-storyboard.com/2020/11/TD-OCTAVIA-en.pdf
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468	Škoda technical data	https://cdn.skoda-storyboard.com/2020/11/TD-OCTAVIA-en.pdf
EU-SKODA-OCTAVIA-IV-HATCHBACK-FACELIFT-01	4698	1829	1470	Škoda technical data	https://cdn.skoda-storyboard.com/2024/07/TD-Octavia-en_b3a3bf09.pdf
EU-SKODA-OCTAVIA-IV-WAGON-FACELIFT-01	4698	1829	1468	Škoda technical data	https://cdn.skoda-storyboard.com/2024/07/TD-Octavia-en_b3a3bf09.pdf
EU-SKODA-OCTAVIA-IV-HATCHBACK-RS-FACELIFT-01	4709	1829	1455	Škoda technical data	https://cdn.skoda-storyboard.com/2024/07/TD-Octavia-en_b3a3bf09.pdf
EU-SKODA-OCTAVIA-IV-WAGON-RS-FACELIFT-01	4709	1829	1455	Škoda technical data	https://cdn.skoda-storyboard.com/2024/07/TD-Octavia-en_b3a3bf09.pdf
EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	4483	1706	1461	Škoda technical data	https://cdn.skoda-storyboard.com/2016/05/TD-RAPID-en.pdf
EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	4304	1706	1459	Škoda technical data	https://cdn.skoda-storyboard.com/2016/05/TD-RAPID-SPACEBACK-en-1.pdf
EU-SKODA-RAPID-GARDE-RAPID-COUPE-STANDARD-01	4200	1610	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/3131615/skoda_rapid_120.html
```

[下载 left18448_15301-15400_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15301-15400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://aic-germany.de/en/product-catalogue/5002?utm_source=chatgpt.com "Product catalogue from AIC Germany"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1884 行）
- 累计尺寸组：dimension_groups_final.tsv（376 行）

