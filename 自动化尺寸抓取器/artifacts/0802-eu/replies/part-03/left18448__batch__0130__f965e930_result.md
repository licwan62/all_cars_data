# 任务：left18448 第 12901-13000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0130__f965e930


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 12901-13000 行

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
left18448 第 12901-13000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_12901-13000_ktype_dimension_mapping_final.tsv
- left18448_12901-13000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	4675	1811	1447
EU-PEUGEOT-407-I-SW-PHASE-I-01	4763	1811	1486

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Peugeot	407	2.2	Kombi	Frontantrieb	Benzin	May 2004	Jul 2005	18013
Peugeot	407	3	Stufenheck	Frontantrieb	Benzin	Mar 2004	Dec 2010	17851
Peugeot	407	3	Kombi	Frontantrieb	Benzin	May 2004	Dec 2010	18014
Peugeot	407	1.6 HDI 110	Stufenheck	Frontantrieb	Diesel	May 2004	Dec 2010	17986
Peugeot	407	1.6 HDI 110	Kombi	Frontantrieb	Diesel	May 2004	Dec 2010	18015
Peugeot	407	1.8 16V	Kombi	Frontantrieb	Benzin	Aug 2005	Dec 2010	18994
Peugeot	407	1.8 16V	Stufenheck	Frontantrieb	Benzin	Aug 2005	Dec 2010	18998
Peugeot	407	2.0 16V	Kombi	Frontantrieb	Benzin	Aug 2005	Dec 2010	18995
Peugeot	407	2.0 16V	Stufenheck	Frontantrieb	Benzin	Sep 2005	Dec 2010	19000
Peugeot	407	2.0 Bioflex	Stufenheck	Frontantrieb	Benzin/Ethanol	Sep 2007	Feb 2011	8795
Peugeot	407	2.0 Flex	Stufenheck	Frontantrieb	Benzin/Ethanol	Oct 2005	Feb 2011	39827
Peugeot	407	2.0 HDI 135	Stufenheck	Frontantrieb	Diesel	May 2004	Oct 2010	17852
Peugeot	407	2.0 HDI 135	Kombi	Frontantrieb	Diesel	Jul 2004	Dec 2010	18016
Peugeot	407	2.2 16V	Coupe	Frontantrieb	Benzin	Oct 2005	-	18990
Peugeot	407	2.2 16V	Kombi	Frontantrieb	Benzin	Aug 2005	Dec 2010	18996
Peugeot	407	2.2 16V	Stufenheck	Frontantrieb	Benzin	Aug 2005	Dec 2010	19001
Peugeot	407	2.7 HDI	Coupe	Frontantrieb	Diesel	Oct 2005	-	18992
Peugeot	407	3.0 V6	Coupe	Frontantrieb	Benzin	Oct 2005	-	18991
Peugeot	504	1.6	Pick-up	Heckantrieb	Benzin	Jan 1980	Jun 1987	14294
Peugeot	504	1.8	Pick-up	Heckantrieb	Benzin	Jul 1987	Dec 1989	14295
Peugeot	504	2	Coupe	Heckantrieb	Benzin	Oct 1974	Aug 1982	14289
Peugeot	504	2	Cabriolet	Heckantrieb	Benzin	Oct 1974	Aug 1982	14291
Peugeot	504	2	Cabriolet	Heckantrieb	Benzin	Aug 1982	Aug 1984	14292
Peugeot	504	2	Coupe	Heckantrieb	Benzin	Aug 1982	Aug 1984	14293
Peugeot	504	2	Coupe	Heckantrieb	Benzin	Jan 1971	Dec 1977	151043
Peugeot	504	2.7	Coupe	Heckantrieb	Benzin	Oct 1977	Aug 1984	14290
Peugeot	504	1.9 D	Pick-up	Heckantrieb	Diesel	Jan 1980	Dec 1989	14296
Peugeot	504	2.3 D	Pick-up	Heckantrieb	Diesel	Jan 1980	Dec 1989	14297
Peugeot	505	2	Stufenheck	Heckantrieb	Benzin	May 1979	Mar 1982	17629
Peugeot	505	2.2 Turbo Injection	Stufenheck	Heckantrieb	Benzin	Jun 1987	Dec 1988	14194
Peugeot	505	2.3 Diesel	Kombi	Heckantrieb	Diesel	Apr 1982	Jun 1986	13296
Peugeot	604	2.8	Stufenheck	Heckantrieb	Benzin	Jan 1977	Dec 1981	126065
Peugeot	605	2	Stufenheck	Frontantrieb	Benzin	Feb 1990	Sep 1999	15897
Peugeot	605	2.1 D	Stufenheck	Frontantrieb	Diesel	Jun 1989	Jul 1995	10920
Peugeot	605	2.1 TD 12V	Stufenheck	Frontantrieb	Diesel	Aug 1994	Sep 1999	10121
Peugeot	607	2	Stufenheck	Frontantrieb	Benzin	Feb 2000	Aug 2005	17911
Peugeot	607	2.0 HDI	Stufenheck	Frontantrieb	Diesel	May 2000	Sep 2005	18268
Peugeot	607	2.0 HDI	Stufenheck	Frontantrieb	Diesel	Sep 2005	Jul 2011	19003
Peugeot	607	2.2 16V	Stufenheck	Frontantrieb	Benzin	Feb 2000	Aug 2005	14533
Peugeot	607	2.2 16V	Stufenheck	Frontantrieb	Benzin	Sep 2005	Jun 2010	19002
Peugeot	607	2.2 HDI	Stufenheck	Frontantrieb	Diesel	Feb 2000	Feb 2006	13167
Peugeot	607	2.7 HDI 24V	Stufenheck	Frontantrieb	Diesel	Dec 2004	Jul 2011	18616
Peugeot	607	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Feb 2000	Jul 2004	13166
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 1998	Sep 2000	142611
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2000	Feb 2003	142612
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 1997	May 2000	142613
Peugeot	806	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	May 1997	Aug 2002	8705
Peugeot	806	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 1998	Sep 2000	11425
Peugeot	806	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Aug 2002	15814
Peugeot	806	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Aug 1999	Aug 2002	13165
Peugeot	806	2.0 HDI 16V	Großraumlimousine	Frontantrieb	Diesel	Aug 1999	Aug 2002	18276
Peugeot	806	DT	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 1997	May 2000	142610
Peugeot	806	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 1999	Feb 2003	142609
Peugeot	806	TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 1995	Aug 2002	142608
Peugeot	807	2	Großraumlimousine	Frontantrieb	Benzin	Jun 2002	-	16666
Peugeot	807	2.2	Großraumlimousine	Frontantrieb	Benzin	Jun 2002	-	16667
Peugeot	807	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	-	19004
Peugeot	807	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2002	May 2006	16669
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2004	May 2006	142524
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2002	May 2006	142624
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2010	-	142636
Peugeot	807	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2002	-	16670
Peugeot	807	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2006	-	59776
Peugeot	807	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	Apr 2004	May 2006	111402
Peugeot	807	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	Jun 2002	-	16668
Peugeot	807	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2004	May 2006	142626
Peugeot	1007	1.4	Schrägheck	Frontantrieb	Benzin	Apr 2005	-	18431
Peugeot	1007	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2005	-	18993
Peugeot	1007	1.4 HDI	Schrägheck	Frontantrieb	Diesel	Apr 2005	-	18433
Peugeot	1007	1.6 16V	Schrägheck	Frontantrieb	Benzin	Apr 2005	-	18432
Peugeot	4007	HDI 155	Kasten/SUV	Allrad	Diesel	Feb 2007	Mar 2013	142675
Peugeot	4008	1.6	SUV	Frontantrieb	Benzin	May 2012	-	110852
Peugeot	4008	1.6 HDI	SUV	Frontantrieb	Diesel	May 2012	-	110850
Peugeot	4008	1.6 HDI AWC	SUV	Allrad	Diesel	May 2012	-	55130
Peugeot	4008	1.8 HDI	SUV	Frontantrieb	Diesel	May 2012	-	110851
Peugeot	4008	1.8 HDI AWC	SUV	Allrad	Diesel	May 2012	-	55131
Peugeot	4008	2.0 AWC	SUV	Allrad	Benzin	May 2012	-	56084
Peugeot	5008	1.2	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Mar 2017	111986
Peugeot	5008	1.2 Hybrid 136	Großraumlimousine	Frontantrieb	Benzin/Elektro	Jun 2023	-	154732
Peugeot	5008	1.2 THP	Großraumlimousine	Frontantrieb	Benzin	Dec 2016	-	124945
Peugeot	5008	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	-	124949
Peugeot	5008	1.6 Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	Nov 2019	126190
Peugeot	5008	1.6 Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	Nov 2014	Mar 2017	144752
Peugeot	5008	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	May 2014	Mar 2017	108175
Peugeot	5008	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	Nov 2019	124950
Peugeot	5008	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Mar 2017	58878
Peugeot	5008	1.6 THP 150	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	Mar 2017	108055
Peugeot	5008	1.6 THP 163	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	Mar 2017	108056
Peugeot	5008	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	Mar 2017	117933
Peugeot	5008	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	Dec 2016	-	124951
Peugeot	5008	2.0 Bluehdi 136	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	-	126191
Peugeot	5008	2.0 Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	-	124952
Peugeot	5008	2.0 Bluehdi 180	Großraumlimousine	Frontantrieb	Diesel	Dec 2016	-	124953
Peugeot	5008	Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2018	-	142671
Peugeot	5008	Bluehdi 180	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2018	-	142673
Peugeot	5008	E-210	SUV	Frontantrieb	Elektro	Aug 2024	-	800012
Peugeot	5008	E-230 Long Range	SUV	Frontantrieb	Elektro	Nov 2024	-	800995
Peugeot	5008	E-325 AWD	SUV	Allrad	Elektro	Jul 2025	-	802057
Peugeot	5008	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Aug 2010	Mar 2017	142664
Peugeot	5008	HDI / E-hdi	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Mar 2017	142669


--- Round 1 / 首次发送 ---
## 更新点

407 Sedan/SW 复用跨批次已有尺寸组；新增 407 Coupe 等未覆盖外廓。605 的 Phase I/II 车长分别为 4723/4765 mm，607 的 Phase I/II 标准车身尺寸分别为 4877×1800×1437 mm 与 4902×1800×1442 mm，因此仅拆分实际跨越这些物理变化的 Ktype。([汽车目录][1])

## 进度

* 输入 Ktype：100
* 最终映射行：105
* 尺寸组：22（复用已有 2 个，新增 20 个）
* 拆分 Ktype：5
* PENDING：0
* 唯一性、引用闭合、三维与来源非空、下载文件名：全部通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18013	18013	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
17851	17851	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
18014	18014	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
17986	17986	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
18015	18015	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
18994	18994	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
18998	18998	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
18995	18995	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
19000	19000	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
8795	8795	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
39827	39827	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
17852	17852	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
18016	18016	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
18990	18990	Coupe	I		2	EU-PEUGEOT-407-I-COUPE-STANDARD-01	HIGH		READY
18996	18996	Wagon	I		5	EU-PEUGEOT-407-I-SW-PHASE-I-01	HIGH		READY
19001	19001	Sedan	I		4	EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	HIGH		READY
18992	18992	Coupe	I		2	EU-PEUGEOT-407-I-COUPE-STANDARD-01	HIGH		READY
18991	18991	Coupe	I		2	EU-PEUGEOT-407-I-COUPE-STANDARD-01	HIGH		READY
14294	14294	Pickup	I		2	EU-PEUGEOT-504-I-PICKUP-STANDARD-01	MEDIUM		READY
14295	14295	Pickup	I		2	EU-PEUGEOT-504-I-PICKUP-STANDARD-01	MEDIUM		READY
14289	14289	Coupe	I		2	EU-PEUGEOT-504-I-COUPE-STANDARD-01	HIGH		READY
14291	14291	Convertible	I		2	EU-PEUGEOT-504-I-CONVERTIBLE-STANDARD-01	MEDIUM		READY
14292	14292	Convertible	I		2	EU-PEUGEOT-504-I-CONVERTIBLE-STANDARD-01	MEDIUM		READY
14293	14293	Coupe	I		2	EU-PEUGEOT-504-I-COUPE-STANDARD-01	HIGH		READY
151043	151043	Coupe	I		2	EU-PEUGEOT-504-I-COUPE-STANDARD-01	HIGH		READY
14290	14290	Coupe	I		2	EU-PEUGEOT-504-I-COUPE-STANDARD-01	HIGH		READY
14296	14296	Pickup	I		2	EU-PEUGEOT-504-I-PICKUP-STANDARD-01	MEDIUM		READY
14297	14297	Pickup	I		2	EU-PEUGEOT-504-I-PICKUP-STANDARD-01	MEDIUM		READY
17629	17629	Sedan	I Phase I		4	EU-PEUGEOT-505-I-SEDAN-PHASE-I-01	HIGH		READY
14194	14194	Sedan	I Phase II		4	EU-PEUGEOT-505-I-SEDAN-PHASE-II-01	HIGH		READY
13296	13296	Wagon	I Phase I		5	EU-PEUGEOT-505-I-WAGON-PHASE-I-01	HIGH		READY
126065	126065	Sedan	I		4	EU-PEUGEOT-604-I-SEDAN-STANDARD-01	HIGH		READY
15897_phase1	15897	Sedan	I Phase I		4	EU-PEUGEOT-605-I-SEDAN-PHASE-I-01	HIGH	Ktype spans the 1994 Phase II exterior-length change.	READY
15897_phase2	15897	Sedan	I Phase II		4	EU-PEUGEOT-605-I-SEDAN-PHASE-II-01	HIGH	Ktype spans the 1994 Phase II exterior-length change.	READY
10920	10920	Sedan	I Phase I		4	EU-PEUGEOT-605-I-SEDAN-PHASE-I-01	HIGH		READY
10121	10121	Sedan	I Phase II		4	EU-PEUGEOT-605-I-SEDAN-PHASE-II-01	HIGH		READY
17911_phase1	17911	Sedan	I Phase I	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
17911_phase2	17911	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
18268_phase1	18268	Sedan	I Phase I	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
18268_phase2	18268	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
19003	19003	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH		READY
14533_phase1	14533	Sedan	I Phase I	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
14533_phase2	14533	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
19002	19002	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH		READY
13167_phase1	13167	Sedan	I Phase I	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
13167_phase2	13167	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH	Ktype spans the November 2004 facelift with changed exterior dimensions.	READY
18616	18616	Sedan	I Phase II	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	HIGH		READY
13166	13166	Sedan	I Phase I	Z8	4	EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	HIGH		READY
142611	142611	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
142612	142612	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
142613	142613	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
8705	8705	MPV	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
11425	11425	MPV	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
15814	15814	MPV	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
13165	13165	MPV	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
18276	18276	MPV	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
142610	142610	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
142609	142609	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
142608	142608	Van	I	221	5	EU-PEUGEOT-806-I-MPV-STANDARD-01	HIGH		READY
16666	16666	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
16667	16667	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
19004	19004	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
16669	16669	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
142524	142524	Van	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
142624	142624	Van	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
142636	142636	Van	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
16670	16670	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
59776	59776	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
111402	111402	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
16668	16668	MPV	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
142626	142626	Van	I		5	EU-PEUGEOT-807-I-MPV-STANDARD-01	HIGH		READY
18431	18431	Hatchback	I		3	EU-PEUGEOT-1007-I-HATCHBACK-STANDARD-01	HIGH		READY
18993	18993	Hatchback	I		3	EU-PEUGEOT-1007-I-HATCHBACK-STANDARD-01	HIGH		READY
18433	18433	Hatchback	I		3	EU-PEUGEOT-1007-I-HATCHBACK-STANDARD-01	HIGH		READY
18432	18432	Hatchback	I		3	EU-PEUGEOT-1007-I-HATCHBACK-STANDARD-01	HIGH		READY
142675	142675	Van	I		5	EU-PEUGEOT-4007-I-SUV-STANDARD-01	MEDIUM		READY
110852	110852	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
110850	110850	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
55130	55130	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
110851	110851	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
55131	55131	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
56084	56084	SUV	I		5	EU-PEUGEOT-4008-I-SUV-STANDARD-01	HIGH		READY
111986	111986	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
154732	154732	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
124945	124945	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
124949	124949	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
126190	126190	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
144752	144752	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
108175	108175	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
124950	124950	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
58878	58878	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
108055	108055	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
108056	108056	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
117933	117933	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
124951	124951	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
126191	126191	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
124952	124952	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
124953	124953	MPV	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
142671	142671	Van	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
142673	142673	Van	II		5	EU-PEUGEOT-5008-II-SUV-STANDARD-01	HIGH		READY
800012	800012	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
800995	800995	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
802057	802057	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
142664	142664	Van	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
142669	142669	Van	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_12901-13000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-407-I-SEDAN-PHASE-I-01	4675	1811	1447	Auto-Data	https://www.auto-data.net/en/peugeot-407-phase-i-2004-2.0-16v-136hp-5396
EU-PEUGEOT-407-I-SW-PHASE-I-01	4763	1811	1486	Auto-Data	https://www.auto-data.net/en/peugeot-407-sw-phase-i-2004-generation-1239
EU-PEUGEOT-407-I-COUPE-STANDARD-01	4815	1868	1399	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/2619350/peugeot_407_coupe_2_2_165.html
EU-PEUGEOT-504-I-PICKUP-STANDARD-01	4800	1694	1550	Drive.Place	https://peugeot.drive.place/504/i/group_pickup_2dr/228489
EU-PEUGEOT-504-I-COUPE-STANDARD-01	4360	1700	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2556605/peugeot_504_coupe.html
EU-PEUGEOT-504-I-CONVERTIBLE-STANDARD-01	4361	1699	1359	Autoevolution	https://www.autoevolution.com/cars/peugeot-504-cabriolet-1977.html
EU-PEUGEOT-505-I-SEDAN-PHASE-I-01	4579	1720	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/2569325/peugeot_505_sr.html
EU-PEUGEOT-505-I-SEDAN-PHASE-II-01	4579	1737	1424	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Peugeot/99/Peugeot-505-Turbo-Injection.html
EU-PEUGEOT-505-I-WAGON-PHASE-I-01	4898	1730	1540	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/2569790/peugeot_505_break_gld.html
EU-PEUGEOT-604-I-SEDAN-STANDARD-01	4721	1770	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/2567780/peugeot_604_ti_v6.html
EU-PEUGEOT-605-I-SEDAN-PHASE-I-01	4723	1799	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/2587475/peugeot_605_sri.html
EU-PEUGEOT-605-I-SEDAN-PHASE-II-01	4765	1799	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2587850/peugeot_605_sri.html
EU-PEUGEOT-607-I-SEDAN-PHASE-I-01	4877	1800	1437	Auto-Data	https://www.auto-data.net/en/peugeot-607-generation-1242
EU-PEUGEOT-607-I-SEDAN-PHASE-II-01	4902	1800	1442	Auto-Data	https://www.auto-data.net/en/peugeot-607-phase-ii-2004-generation-8889
EU-PEUGEOT-806-I-MPV-STANDARD-01	4454	1834	1714	Auto-Data	https://www.auto-data.net/en/peugeot-806-221-2.0-16v-136hp-5477
EU-PEUGEOT-807-I-MPV-STANDARD-01	4727	1850	1752	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/2618510/peugeot_807_2_0_16v_135_automatic.html
EU-PEUGEOT-1007-I-HATCHBACK-STANDARD-01	3731	1662	1620	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2619965/peugeot_1007_1_4_75.html
EU-PEUGEOT-4007-I-SUV-STANDARD-01	4635	1805	1670	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2623325/peugeot_4007_2_2_hdi_156_fap.html
EU-PEUGEOT-4008-I-SUV-STANDARD-01	4340	1768	1625	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/2627795/peugeot_4008_1_8_hdi_150_4wd.html
EU-PEUGEOT-5008-I-MPV-STANDARD-01	4529	1837	1639	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2626370/peugeot_5008_2_0_bluehdi_150.html
EU-PEUGEOT-5008-II-SUV-STANDARD-01	4641	1844	1646	ADAC	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/5008/2generation/268076/
EU-PEUGEOT-5008-III-SUV-STANDARD-01	4791	1895	1694	Peugeot UK	https://www.peugeot.co.uk/models/new-peugeot-5008/electric.html
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_12901-13000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1989/2587475/peugeot_605_sri.html?utm_source=chatgpt.com "1989 Peugeot 605 SRi Specs Review (94 kW / 128 PS / 126 hp) (since September 1989 for Europe )"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4553 行）
- 累计尺寸组：dimension_groups_final.tsv（1260 行）

