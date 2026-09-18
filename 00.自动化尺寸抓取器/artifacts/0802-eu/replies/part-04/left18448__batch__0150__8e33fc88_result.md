# 任务：left18448 第 14901-15000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0150__8e33fc88


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 14901-15000 行

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
left18448 第 14901-15000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14901-15000_ktype_dimension_mapping_final.tsv
- left18448_14901-15000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	4163	1640	1424
EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	4142	1640	1409
EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	4163	1640	1433
EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	4280	1698	1441

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Seat	Cordoba	1.6 I	Kombi	Frontantrieb	Benzin	May 1997	Jun 1999	18574
Seat	Cordoba	1.8 T 20V Cupra	Stufenheck	Frontantrieb	Benzin	Jul 2000	Oct 2002	13202
Seat	Cordoba	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Aug 1996	Jun 1999	5673
Seat	Cordoba	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Jun 1999	Oct 2002	12894
Seat	Cordoba	1.9 SDI	Kombi	Frontantrieb	Diesel	Jun 1999	Dec 2002	12895
Seat	Cordoba	1.9 SDI	Stufenheck	Frontantrieb	Diesel	Sep 2002	Nov 2009	17154
Seat	Cordoba	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Aug 1996	Oct 2002	7890
Seat	Cordoba	1.9 TDI	Kombi	Frontantrieb	Diesel	Jul 1997	Dec 2002	8831
Seat	Cordoba	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Oct 2002	Nov 2009	17118
Seat	Cordoba	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Sep 2002	Nov 2009	17153
Seat	Cordoba	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	Aug 1996	Jun 1999	7889
Seat	Exeo	1.8 TSI	Stufenheck	Frontantrieb	Benzin	Sep 2010	May 2013	34806
Seat	Exeo	1.8 TSI	Stufenheck	Frontantrieb	Benzin	May 2010	May 2013	34809
Seat	Exeo	1.8 TSI	Kombi	Frontantrieb	Benzin	Sep 2010	May 2013	34811
Seat	Exeo	1.8 TSI	Kombi	Frontantrieb	Benzin	May 2010	May 2013	34814
Seat	Exeo	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	May 2010	May 2013	34810
Seat	Exeo	2.0 Tfsi	Kombi	Frontantrieb	Benzin	May 2010	May 2013	34818
Seat	Fura	0.9	Schrägheck	Frontantrieb	Benzin	Jan 1982	Jun 1986	8114
Seat	Fura	1.4 Crono	Schrägheck	Frontantrieb	Benzin	Jan 1982	Jun 1986	8115
Seat	Ibiza ii	1.0 16V	Schrägheck	Frontantrieb	Benzin	Oct 1999	May 2002	17090
Seat	Ibiza ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	May 2000	Feb 2002	13198
Seat	Ibiza ii	1.6 I	Schrägheck	Frontantrieb	Benzin	Apr 1996	Feb 2002	5677
Seat	Ibiza ii	1.6 I	Schrägheck	Frontantrieb	Benzin	Sep 1994	Jun 1999	18580
Seat	Ibiza ii	1.8 T 20V Cupra	Schrägheck	Frontantrieb	Benzin	Jul 2000	Feb 2002	13199
Seat	Ibiza ii	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Aug 1999	Feb 2002	13194
Seat	Ibiza iii	1.2	Schrägheck	Frontantrieb	Benzin	Feb 2002	Jun 2006	16523
Seat	Ibiza iii	1.6	Schrägheck	Frontantrieb	Benzin	Feb 2003	Nov 2009	17924
Seat	Ibiza iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Feb 2002	Nov 2009	16524
Seat	Ibiza iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Feb 2002	Dec 2007	16809
Seat	Ibiza iii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2002	Dec 2005	17079
Seat	Ibiza iii	1.8 T Cupra R	Schrägheck	Frontantrieb	Benzin	Jan 2004	Feb 2008	17298
Seat	Ibiza iii	1.8 T FR	Schrägheck	Frontantrieb	Benzin	Dec 2003	May 2008	17836
Seat	Ibiza iii	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Feb 2002	Dec 2005	16810
Seat	Ibiza iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2002	Nov 2009	16525
Seat	Ibiza iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2002	Nov 2009	16526
Seat	Ibiza iii	1.9 TDI Cupra R	Schrägheck	Frontantrieb	Diesel	Mar 2004	Feb 2008	18243
Seat	Ibiza iv	1	Schrägheck	Frontantrieb	Benzin	May 2015	Jun 2017	113863
Seat	Ibiza iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Jun 2017	113866
Seat	Ibiza iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Jun 2017	113867
Seat	Ibiza iv	1.2 TDI	Schrägheck	Frontantrieb	Diesel	Jun 2010	May 2015	33875
Seat	Ibiza iv	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2012	May 2015	57425
Seat	Ibiza iv	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Jun 2017	113864
Seat	Ibiza iv	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Sep 2015	Jun 2017	116635
Seat	Ibiza iv	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Jun 2017	113868
Seat	Ibiza iv	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Jun 2017	113871
Seat	Ibiza iv	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Jun 2017	113872
Seat	Ibiza iv	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Oct 2013	May 2015	100092
Seat	Ibiza iv	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2015	Jun 2017	117375
Seat	Ibiza iv	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	May 2015	10643
Seat	Ibiza iv sc	1	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2016	113886
Seat	Ibiza iv sc	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2016	113894
Seat	Ibiza iv sc	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2016	113895
Seat	Ibiza iv sc	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2012	May 2015	100024
Seat	Ibiza iv sc	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2016	113893
Seat	Ibiza iv sc	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Sep 2015	Dec 2016	116636
Seat	Ibiza iv sc	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2016	113896
Seat	Ibiza iv sc	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2016	113898
Seat	Ibiza iv sc	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2016	113899
Seat	Ibiza iv sc	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Oct 2013	May 2015	100094
Seat	Ibiza iv sc	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2015	Dec 2016	117379
Seat	Ibiza iv sc	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	May 2015	10637
Seat	Ibiza iv sc	1.8 TSI Cupra	Schrägheck	Frontantrieb	Benzin	Nov 2015	Dec 2016	117382
Seat	Ibiza iv st	1	Kombi	Frontantrieb	Benzin	May 2015	Jul 2016	113900
Seat	Ibiza iv st	1.0 TSI	Kombi	Frontantrieb	Benzin	May 2015	Jul 2016	113902
Seat	Ibiza iv st	1.0 TSI	Kombi	Frontantrieb	Benzin	May 2015	Jul 2016	113903
Seat	Ibiza iv st	1.2 TSI	Kombi	Frontantrieb	Benzin	Sep 2012	May 2015	57427
Seat	Ibiza iv st	1.2 TSI	Kombi	Frontantrieb	Benzin	May 2015	Jul 2016	113901
Seat	Ibiza iv st	1.2 TSI	Kombi	Frontantrieb	Benzin	Sep 2015	Jul 2016	116637
Seat	Ibiza iv st	1.4 TDI	Kombi	Frontantrieb	Diesel	May 2015	Jul 2016	113904
Seat	Ibiza iv st	1.4 TDI	Kombi	Frontantrieb	Diesel	May 2015	Jul 2016	113905
Seat	Ibiza iv st	1.4 TDI	Kombi	Frontantrieb	Diesel	May 2015	Jul 2016	113906
Seat	Ibiza iv st	1.4 TSI	Kombi	Frontantrieb	Benzin	Oct 2013	May 2015	100095
Seat	Ibiza iv st	1.4 TSI	Kombi	Frontantrieb	Benzin	Nov 2015	Jul 2016	117380
Seat	Ibiza v	1.0 MPI	Schrägheck	Frontantrieb	Benzin	Jan 2017	-	127208
Seat	Ibiza v	1.0 MPI	Schrägheck	Frontantrieb	Benzin	Jul 2017	-	128304
Seat	Ibiza v	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2017	-	127209
Seat	Ibiza v	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2017	-	127210
Seat	Ibiza v	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2017	-	128305
Seat	Ibiza v	1.6 SRE	Schrägheck	Frontantrieb	Benzin	May 2017	-	127213
Seat	Inca	1.4 16V	Kasten/Kombi	Frontantrieb	Benzin	Apr 2000	Jun 2003	15803
Seat	Inca	1.6 I	Kasten/Kombi	Frontantrieb	Benzin	Jun 1997	Sep 2000	18157
Seat	Inca	1.9 SDI	Kasten/Kombi	Frontantrieb	Diesel	Nov 1995	Jun 2003	8097
Seat	Leon	1.6	Schrägheck	Frontantrieb	Benzin	Nov 1999	Jun 2006	13159
Seat	Leon	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2005	Dec 2012	18766
Seat	Leon	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Aug 2020	115140
Seat	Leon	1.0 TSI	Coupe	Frontantrieb	Benzin	May 2015	Aug 2018	115142
Seat	Leon	1.0 TSI	Kombi	Frontantrieb	Benzin	May 2015	Aug 2020	115143
Seat	Leon	1.0 TSI Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2020	-	143677
Seat	Leon	1.0 TSI Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Aug 2020	-	143680
Seat	Leon	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Dec 2012	Aug 2018	57587
Seat	Leon	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2013	Aug 2020	57589
Seat	Leon	1.2 TSI	Coupe	Frontantrieb	Benzin	Jan 2013	Aug 2018	59596
Seat	Leon	1.2 TSI	Coupe	Frontantrieb	Benzin	Feb 2013	Apr 2014	59597
Seat	Leon	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2014	Aug 2020	101004
Seat	Leon	1.2 TSI	Coupe	Frontantrieb	Benzin	May 2014	Aug 2018	106387
Seat	Leon	1.2 TSI	Kombi	Frontantrieb	Benzin	May 2014	Aug 2020	106392
Seat	Leon	1.4 16V	Schrägheck	Frontantrieb	Benzin	Nov 1999	Jun 2006	14268
Seat	Leon	1.4 TGI	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Feb 2013	Aug 2018	100789
Seat	Leon	1.4 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	Oct 2013	Aug 2018	100794
Seat	Leon	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Oct 2016	56779


--- Round 1 / 首次发送 ---
## 更新点

已完成全部 100 个输入 Ktype 的物理外廓归并。仅对跨越已证实尺寸变化节点的 Ktype 派生阶段行，包括 Cordoba 1999 改款、Exeo ST 2011 改款、Ibiza II 1996/1999 改款、Ibiza IV 2012 改款和 Leon III 2016 年末改款；动力、燃料和普通配置均直接复用尺寸组。Ibiza IV 2015 改款因三维不变未重复建组。关键阶段尺寸及不含后视镜宽度已由对应车型规格页闭合。([汽车目录][1])

## 当前批进度

输入 Ktype：100
最终映射行：122
DIMENSION_GROUP：31
READY：122
PENDING：0
机械终检：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18574	18574	Wagon	Cordoba I	6K	5	EU-SEAT-CORDOBA-I-WAGON-PREFL-01	HIGH		READY
13202	13202	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	HIGH		READY
5673	5673	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	HIGH		READY
12894	12894	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	HIGH		READY
12895	12895	Wagon	Cordoba I	6K	5	EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	HIGH		READY
17154	17154	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
7890_prefl	7890	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	HIGH	1999改款改变外廓，按阶段拆分	READY
7890_facelift	7890	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	HIGH	1999改款改变外廓，按阶段拆分	READY
8831_prefl	8831	Wagon	Cordoba I	6K	5	EU-SEAT-CORDOBA-I-WAGON-PREFL-01	HIGH	1999改款改变外廓，按阶段拆分	READY
8831_facelift	8831	Wagon	Cordoba I	6K	5	EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	HIGH	1999改款改变外廓，按阶段拆分	READY
17118	17118	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
17153	17153	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	HIGH		READY
7889	7889	Sedan	Cordoba I	6K		EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	HIGH		READY
34806	34806	Sedan	Exeo I	3R2	4	EU-SEAT-EXEO-I-SEDAN-STANDARD-01	HIGH		READY
34809	34809	Sedan	Exeo I	3R2	4	EU-SEAT-EXEO-I-SEDAN-STANDARD-01	HIGH		READY
34811_prefl	34811	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-PREFL-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
34811_facelift	34811	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-FACELIFT11-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
34814_prefl	34814	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-PREFL-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
34814_facelift	34814	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-FACELIFT11-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
34810	34810	Sedan	Exeo I	3R2	4	EU-SEAT-EXEO-I-SEDAN-STANDARD-01	HIGH		READY
34818_prefl	34818	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-PREFL-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
34818_facelift	34818	Wagon	Exeo I	3R5	5	EU-SEAT-EXEO-I-WAGON-FACELIFT11-01	HIGH	2011改款改变旅行版长度，按阶段拆分	READY
8114	8114	Hatchback	Fura I	025A	3	EU-SEAT-FURA-I-HATCHBACK-STANDARD-01	HIGH		READY
8115	8115	Hatchback	Fura I	025A	3	EU-SEAT-FURA-I-HATCHBACK-CRONO-01	HIGH	Crono为独立外廓	READY
17090	17090	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	HIGH		READY
13198	13198	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	HIGH		READY
5677_early	5677	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-EARLY-01	HIGH	1996及1999改款改变外廓，按阶段拆分	READY
5677_facelift96	5677	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT96-01	HIGH	1996及1999改款改变外廓，按阶段拆分	READY
5677_facelift99	5677	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	HIGH	1996及1999改款改变外廓，按阶段拆分	READY
18580_early	18580	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-EARLY-01	HIGH	1996及1999改款改变外廓，按阶段拆分	READY
18580_facelift96	18580	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT96-01	HIGH	1996及1999改款改变外廓，按阶段拆分	READY
13199	13199	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	HIGH		READY
13194	13194	Hatchback	Ibiza II	6K		EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	HIGH		READY
16523	16523	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
17924	17924	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
16524	16524	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
16809	16809	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
17079	17079	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
17298	17298	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
17836	17836	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
16810	16810	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
16525	16525	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
16526	16526	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
18243	18243	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	HIGH		READY
113863	113863	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113866	113866	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113867	113867	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
33875_phase1	33875	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE1-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
33875_phase2	33875	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
57425	57425	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113864	113864	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
116635	116635	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113868	113868	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113871	113871	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
113872	113872	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
100092	100092	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
117375	117375	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH		READY
10643_phase1	10643	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE1-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
10643_phase2	10643	Hatchback	Ibiza IV	6J5/6P1	5	EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
113886	113886	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113894	113894	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113895	113895	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
100024	100024	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113893	113893	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
116636	116636	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113896	113896	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113898	113898	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113899	113899	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
100094	100094	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
117379	117379	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
10637_phase1	10637	Hatchback	Ibiza IV	6J1	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE1-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
10637_phase2	10637	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH	2012改款改变长度，按阶段拆分；2015改款三维不变	READY
117382	117382	Hatchback	Ibiza IV	6J1/6P5	3	EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	HIGH		READY
113900	113900	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113902	113902	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113903	113903	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
57427	57427	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113901	113901	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
116637	116637	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113904	113904	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113905	113905	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
113906	113906	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
100095	100095	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
117380	117380	Wagon	Ibiza IV	6J8/6P8	5	EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	HIGH		READY
127208	127208	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
128304	128304	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
127209	127209	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
127210	127210	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
128305	128305	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
127213	127213	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	HIGH		READY
15803	15803	Van	Inca I	9K		EU-SEAT-INCA-I-VAN-STANDARD-01	HIGH		READY
18157	18157	Van	Inca I	9K		EU-SEAT-INCA-I-VAN-STANDARD-01	HIGH		READY
8097	8097	Van	Inca I	9K		EU-SEAT-INCA-I-VAN-STANDARD-01	HIGH		READY
13159	13159	Hatchback	Leon I	1M1	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
18766	18766	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	HIGH		READY
115140_prefl	115140	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
115140_facelift	115140	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
115142_prefl	115142	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
115142_facelift	115142	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
115143_prefl	115143	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
115143_facelift	115143	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
143677	143677	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
143680	143680	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
57587_prefl	57587	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
57587_facelift	57587	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
57589_prefl	57589	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
57589_facelift	57589	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
59596_prefl	59596	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
59596_facelift	59596	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
59597	59597	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
101004_prefl	101004	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
101004_facelift	101004	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
106387_prefl	106387	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
106387_facelift	106387	Coupe	Leon III	5F5	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
106392_prefl	106392	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
106392_facelift	106392	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
14268	14268	Hatchback	Leon I	1M1	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
100789_prefl	100789	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
100789_facelift	100789	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
100794_prefl	100794	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
100794_facelift	100794	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2016年末改款改变长度，按阶段拆分	READY
56779	56779	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH		READY
```

[下载 left18448_14901-15000_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_14901-15000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-CORDOBA-I-WAGON-PREFL-01	4142	1640	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3066530/seat_cordoba_vario_1_4.html
EU-SEAT-CORDOBA-I-SEDAN-FACELIFT99-01	4163	1640	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3070730/seat_cordoba_1_9_sdi.html
EU-SEAT-CORDOBA-I-SEDAN-PREFL-01	4142	1640	1409	Auto-Data.net	https://www.auto-data.net/en/seat-cordoba-i-1.6-i-101hp-13448
EU-SEAT-CORDOBA-I-WAGON-FACELIFT99-01	4163	1640	1433	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3070895/seat_cordoba_vario_1_9_sdi.html
EU-SEAT-CORDOBA-II-SEDAN-STANDARD-01	4280	1698	1441	Auto-Data.net	https://www.auto-data.net/en/seat-cordoba-ii-1.4-tdi-75hp-13412
EU-SEAT-EXEO-I-SEDAN-STANDARD-01	4661	1772	1430	Auto-Data.net	https://www.auto-data.net/en/seat-exeo-2.0-tsi-211hp-16910
EU-SEAT-EXEO-I-WAGON-PREFL-01	4670	1772	1454	Auto-Data.net	https://www.auto-data.net/en/seat-exeo-st-generation-2918
EU-SEAT-EXEO-I-WAGON-FACELIFT11-01	4666	1772	1454	Auto-Data.net	https://www.auto-data.net/en/seat-exeo-st-1.8-tsi-160hp-16913
EU-SEAT-FURA-I-HATCHBACK-STANDARD-01	3711	1536	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/3062960/seat_fura_dos_l_3_puertas.html
EU-SEAT-FURA-I-HATCHBACK-CRONO-01	3718	1552	1383	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/41150/seat_fura_crono.html
EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT99-01	3876	1640	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3070505/seat_ibiza_1_6_100.html
EU-SEAT-IBIZA-II-HATCHBACK-EARLY-01	3813	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/3065780/seat_ibiza_1_6i.html
EU-SEAT-IBIZA-II-HATCHBACK-FACELIFT96-01	3853	1640	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3067160/seat_ibiza_1_6_75.html
EU-SEAT-IBIZA-III-HATCHBACK-STANDARD-01	3955	1700	1440	Auto-Data.net	https://www.auto-data.net/en/seat-ibiza-iii-1.4-16v-75hp-13479
EU-SEAT-IBIZA-IV-HATCHBACK-PHASE2-01	4061	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/3095540/seat_ibiza_1_2_tsi_85.html
EU-SEAT-IBIZA-IV-HATCHBACK-PHASE1-01	4052	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3095270/seat_ibiza_1_6_lpg.html
EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE2-01	4043	1693	1428	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3095360/seat_ibiza_sc_1_2_tsi_105_dsg.html
EU-SEAT-IBIZA-IV-HATCHBACK-3D-PHASE1-01	4034	1693	1428	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3095285/seat_ibiza_sc_1_6_lpg.html
EU-SEAT-IBIZA-IV-WAGON-PHASE2-01	4236	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/3095720/seat_ibiza_st_1_2_tsi_105.html
EU-SEAT-IBIZA-V-HATCHBACK-STANDARD-01	4059	1780	1444	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/3101300/seat_ibiza_1_0_ecotsi_95.html
EU-SEAT-INCA-I-VAN-STANDARD-01	4207	1696	1836	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3071210/seat_inca_van_1_9_sdi.html
EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	4184	1742	1439	Auto-Data.net	https://www.auto-data.net/en/seat-leon-i-1m-1.4-16v-75hp-13615
EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	4315	1768	1458	Auto-Data.net	https://www.auto-data.net/en/seat-leon-ii-1p-1.6-mpi-102hp-13601
EU-SEAT-LEON-III-HATCHBACK-PREFL-01	4263	1816	1459	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/3097055/seat_leon_1_2_tsi_110.html
EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	4282	1816	1459	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/3098615/seat_leon_1_0_tsi_115_ecomotive.html
EU-SEAT-LEON-III-COUPE-PREFL-01	4228	1810	1446	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/3097085/seat_leon_sc_1_2_tsi_110.html
EU-SEAT-LEON-III-COUPE-FACELIFT17-01	4247	1810	1446	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/3098645/seat_leon_sc_1_0_tsi_115_ecomotive.html
EU-SEAT-LEON-III-WAGON-PREFL-01	4535	1816	1451	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/3097115/seat_leon_st_1_2_tsi_110.html
EU-SEAT-LEON-III-WAGON-FACELIFT17-01	4549	1816	1451	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/3098675/seat_leon_st_1_0_tsi_115_ecomotive.html
EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	4368	1799	1456	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/3099665/seat_leon_1_0_etsi_110_dsg.html
EU-SEAT-LEON-IV-WAGON-STANDARD-01	4642	1799	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/3099920/seat_leon_sportstourer_1_0_etsi_110_dsg.html
```

[下载 left18448_14901-15000_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_14901-15000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1998/3066530/seat_cordoba_vario_1_4.html?utm_source=chatgpt.com "1998 Seat Cordoba Vario 1.4 Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1400 行）
- 累计尺寸组：dimension_groups_final.tsv（290 行）

