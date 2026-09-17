# 任务：left18448 第 13601-13700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0137__4d25da4c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13601-13700 行

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
left18448 第 13601-13700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13601-13700_ktype_dimension_mapping_final.tsv
- left18448_13601-13700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	4782	1928	1699
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-STANDARD-01	4930	1983	1698

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Porsche	Cayenne	3.0 AWD	SUV	Allrad	Benzin	Apr 2023	-	153721
Porsche	Cayenne	3.0 Diesel	SUV	Allrad	Diesel	Jun 2011	May 2018	11585
Porsche	Cayenne	3.0 Diesel	SUV	Allrad	Diesel	Jun 2010	May 2018	11814
Porsche	Cayenne	3.0 Diesel	SUV	Allrad	Diesel	Oct 2014	May 2018	107542
Porsche	Cayenne	3.0 Diesel	SUV	Allrad	Diesel	Aug 2014	May 2018	109320
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Jun 2023	-	154808
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Jun 2023	-	154809
Porsche	Cayenne	3.6 GTS	SUV	Allrad	Benzin	Feb 2015	May 2018	110624
Porsche	Cayenne	3.6 S	SUV	Allrad	Benzin	Oct 2014	May 2018	107544
Porsche	Cayenne	4.0 GTS	SUV	Allrad	Benzin	May 2024	-	158532
Porsche	Cayenne	4.0 GTS	SUV	Allrad	Benzin	May 2024	-	158696
Porsche	Cayenne	4.0 S AWD	SUV	Allrad	Benzin	Jun 2023	-	154769
Porsche	Cayenne	4.0 S AWD	SUV	Allrad	Benzin	Jun 2023	-	154770
Porsche	Cayenne	4.0 Turbo GT AWD	SUV	Allrad	Benzin	Oct 2020	May 2023	144667
Porsche	Cayenne	4.0 Turbo S E-hybrid AWD	SUV	Allrad	Benzin/Elektro	May 2017	May 2023	145106
Porsche	Cayenne	4.2 S Diesel	SUV	Allrad	Diesel	Oct 2012	May 2014	56877
Porsche	Cayenne	4.2 S Diesel	SUV	Allrad	Diesel	Oct 2014	May 2018	107543
Porsche	Cayenne	4.8 GTS	SUV	Allrad	Benzin	Jun 2012	May 2018	56026
Porsche	Cayenne	4.8 Turbo	SUV	Allrad	Benzin	Jun 2010	May 2014	11656
Porsche	Cayenne	4.8 Turbo	SUV	Allrad	Benzin	Oct 2014	May 2018	107545
Porsche	Cayenne	4.8 Turbo S	SUV	Allrad	Benzin	Oct 2012	May 2014	56878
Porsche	Cayenne	4.8 Turbo S	SUV	Allrad	Benzin	Jan 2015	May 2018	111985
Porsche	Cayenne	Electric	SUV	Allrad	Elektro	Feb 2026	-	163562
Porsche	Cayenne	S 4.5	SUV	Allrad	Benzin	Sep 2002	Sep 2007	16695
Porsche	Cayenne	S E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Oct 2023	-	156240
Porsche	Cayenne	S E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Oct 2023	-	156241
Porsche	Cayenne	S Electric	SUV	Allrad	Elektro	Feb 2026	-	164509
Porsche	Cayenne	Turbo 4.5	SUV	Allrad	Benzin	Sep 2002	Sep 2007	16848
Porsche	Cayenne	Turbo E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Aug 2023	-	156111
Porsche	Cayenne	Turbo E-hybrid AWD	SUV	Allrad	Benzin/Elektro	Aug 2023	-	156112
Porsche	Cayenne	Turbo Electric	SUV	Allrad	Elektro	Feb 2026	-	163563
Porsche	Cayenne	Turbo S 4.5	SUV	Allrad	Benzin	Jan 2004	Sep 2007	18918
Porsche	Cayman	2.7	Coupe	Heckantrieb	Benzin	Mar 2013	May 2016	57364
Porsche	Cayman	3.8 GT4	Coupe	Heckantrieb	Benzin	Jan 2015	May 2016	111984
Porsche	Cayman	GTS 3.4	Coupe	Heckantrieb	Benzin	Feb 2014	May 2016	101142
Porsche	Cayman	R 3.4	Coupe	Heckantrieb	Benzin	Nov 2010	Dec 2012	11323
Porsche	Cayman	S 3.4	Coupe	Heckantrieb	Benzin	Nov 2005	Dec 2009	18917
Porsche	Cayman	S 3.4	Coupe	Heckantrieb	Benzin	Mar 2013	May 2016	57365
Porsche	Macan	2	SUV	Allrad	Benzin	May 2014	Sep 2018	107478
Porsche	Macan	2	SUV	Allrad	Benzin	May 2015	-	117979
Porsche	Macan	2	SUV	Allrad	Benzin	May 2018	-	145236
Porsche	Macan	2.9 GTS AWD	SUV	Allrad	Benzin	May 2021	-	154487
Porsche	Macan	2.9 S	SUV	Allrad	Benzin	May 2021	-	154486
Porsche	Macan	3.0 GTS	SUV	Allrad	Benzin	Oct 2015	Sep 2018	117977
Porsche	Macan	3.0 S	SUV	Allrad	Benzin	Feb 2014	Sep 2018	100638
Porsche	Macan	3.0 S Diesel	SUV	Allrad	Diesel	Feb 2014	Sep 2018	100640
Porsche	Macan	3.0 S Diesel	SUV	Allrad	Diesel	Feb 2014	Sep 2018	105798
Porsche	Macan	3.0 S Diesel	SUV	Allrad	Diesel	Feb 2014	Sep 2018	105802
Porsche	Macan	3.0 S Diesel	SUV	Allrad	Diesel	Feb 2014	Sep 2018	107684
Porsche	Macan	3.6 Turbo	SUV	Allrad	Benzin	Feb 2014	Sep 2018	100639
Porsche	Macan	4 Electric 4	SUV	Allrad	Elektro	Feb 2024	-	157639
Porsche	Macan	4S Electric 4	SUV	Allrad	Elektro	Sep 2024	-	800552
Porsche	Macan	Electric	SUV	Heckantrieb	Elektro	Sep 2024	-	800553
Porsche	Macan	GTS Electric 4	SUV	Allrad	Elektro	Nov 2025	-	802752
Porsche	Macan	Turbo Electric 4	SUV	Allrad	Elektro	Feb 2024	-	157641
Porsche	Panamera	2.9	Schrägheck	Heckantrieb	Benzin	Jun 2023	-	156875
Porsche	Panamera	3	Schrägheck	Heckantrieb	Benzin	May 2016	Dec 2020	124806
Porsche	Panamera	3.6	Schrägheck	Heckantrieb	Benzin	Jul 2013	Oct 2016	59591
Porsche	Panamera	2.9 4	Schrägheck	Allrad	Benzin	Jun 2023	-	156876
Porsche	Panamera	2.9 4 E-hybrid	Kombi	Allrad	Benzin/Elektro	May 2017	Dec 2023	126896
Porsche	Panamera	2.9 4 E-hybrid	Schrägheck	Allrad	Benzin/Elektro	Jun 2023	-	158093
Porsche	Panamera	2.9 4S	Kombi	Allrad	Benzin	May 2017	Dec 2023	126897
Porsche	Panamera	2.9 4S E-hybrid	Kombi	Allrad	Benzin/Elektro	Aug 2020	Dec 2023	144319
Porsche	Panamera	2.9 4S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	Aug 2020	Dec 2023	144472
Porsche	Panamera	2.9 4S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	Feb 2024	-	158094
Porsche	Panamera	3.0 4	Schrägheck	Allrad	Benzin	May 2016	Dec 2020	124807
Porsche	Panamera	3.0 4	Kombi	Allrad	Benzin	May 2017	Dec 2020	126894
Porsche	Panamera	3.0 4S	Schrägheck	Allrad	Benzin	Jul 2013	Oct 2016	59590
Porsche	Panamera	3.0 D	Schrägheck	Heckantrieb	Diesel	Aug 2011	Jul 2013	11691
Porsche	Panamera	3.0 D	Schrägheck	Heckantrieb	Diesel	Aug 2011	Jul 2013	15981
Porsche	Panamera	3.0 D	Schrägheck	Heckantrieb	Diesel	Jul 2013	Oct 2016	100636
Porsche	Panamera	3.0 S	Schrägheck	Heckantrieb	Benzin	Jul 2013	Oct 2016	59589
Porsche	Panamera	3.0 S E-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	Mar 2011	Jul 2013	59585
Porsche	Panamera	3.0 S E-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	Jul 2013	Oct 2016	59587
Porsche	Panamera	3.6 4	Schrägheck	Allrad	Benzin	Jul 2013	Oct 2016	59592
Porsche	Panamera	4.0 GTS	Schrägheck	Allrad	Benzin	Jul 2024	-	800207
Porsche	Panamera	4.0 S 4 Diesel	Kombi	Allrad	Diesel	May 2017	Dec 2023	126899
Porsche	Panamera	4.0 Turbo	Kombi	Allrad	Benzin	May 2017	Dec 2023	126898
Porsche	Panamera	4.0 Turbo E-hybrid	Schrägheck	Allrad	Benzin/Elektro	Feb 2024	-	157717
Porsche	Panamera	4.0 Turbo S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	May 2017	Dec 2023	126908
Porsche	Panamera	4.0 Turbo S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	May 2020	Dec 2023	146731
Porsche	Panamera	4.0 Turbo S E-hybrid	Kombi	Allrad	Benzin/Elektro	May 2020	Dec 2023	146732
Porsche	Panamera	4.0 Turbo S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	Jul 2024	-	800281
Porsche	Panamera	4.8 GTS	Schrägheck	Allrad	Benzin	Jul 2013	Oct 2016	59594
Porsche	Panamera	4.8 Turbo	Schrägheck	Allrad	Benzin	Aug 2010	Jul 2013	11703
Porsche	Panamera	4.8 Turbo	Schrägheck	Allrad	Benzin	Jul 2013	Oct 2016	59593
Porsche	Panamera	4.8 Turbo S	Schrägheck	Allrad	Benzin	Jul 2013	Oct 2016	100637
Porsche	Taycan	4	Kombi	Allrad	Elektro	May 2020	Dec 2023	145130
Porsche	Taycan	4	Kombi	Allrad	Elektro	Nov 2023	-	157964
Porsche	Taycan	4	Stufenheck	Allrad	Elektro	Apr 2024	-	158556
Porsche	Taycan	4 Performance Battery Plus	Stufenheck	Allrad	Elektro	Nov 2024	-	801122
Porsche	Taycan	4 Performance Battery Plus	Kombi	Allrad	Elektro	Sep 2021	-	802695
Porsche	Taycan	4S	Kombi	Allrad	Elektro	May 2020	Dec 2023	153385
Porsche	Taycan	4S	Kombi	Allrad	Elektro	Aug 2021	Dec 2023	153386
Porsche	Taycan	4S	Kombi	Allrad	Elektro	Nov 2023	-	157971
Porsche	Taycan	4S	Stufenheck	Allrad	Elektro	Nov 2023	-	157977
Porsche	Taycan	4S	Kombi	Allrad	Elektro	Nov 2023	-	158033
Porsche	Taycan	4S Performance Battery Plus	Kombi	Allrad	Elektro	May 2020	Dec 2023	145139
Porsche	Taycan	4S Performance Battery Plus	Stufenheck	Allrad	Elektro	May 2019	Dec 2023	145147
Porsche	Taycan	4S Performance Battery Plus	Kombi	Allrad	Elektro	Aug 2021	Dec 2023	146967


--- Round 1 / 首次发送 ---
## 更新点

已复用累计表中的 2 个 Cayenne 尺寸组。Ktype `11585`、`11814` 跨越 2014 年改款，且改款前后车长由 4846 mm 变为 4855 mm，因此分别拆分为 `_prefl` 与 `_facelift`。全部宽度采用不含后视镜的车身宽度；相关规格页将车身宽度与含后视镜宽度分列，Macan Electric 与 Cayenne Electric 的新尺寸也采用保时捷官方资料。([汽车数据网][1])

## 进度

* 输入 Ktype：100
* 最终映射行：102
* DIMENSION_GROUP：46
* PENDING：0
* 固定表头、列数、ID 唯一性、引用闭合、正整数三维、来源及 URL 非空均已通过机械校验。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
153721	153721	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-STANDARD-01	HIGH		READY
11585_prefl	11585	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH	Ktype spans the 2014 facelift boundary with changed exterior dimensions.	READY
11585_facelift	11585	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH	Ktype spans the 2014 facelift boundary with changed exterior dimensions.	READY
11814_prefl	11814	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH	Ktype spans the 2014 facelift boundary with changed exterior dimensions.	READY
11814_facelift	11814	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH	Ktype spans the 2014 facelift boundary with changed exterior dimensions.	READY
107542	107542	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH		READY
109320	109320	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH		READY
154808	154808	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-EHYBRID-01	HIGH		READY
154809	154809	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-EHYBRID-01	HIGH		READY
110624	110624	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-GTS-01	HIGH		READY
107544	107544	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH		READY
158532	158532	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-GTS-01	HIGH		READY
158696	158696	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-GTS-01	HIGH		READY
154769	154769	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-01	HIGH		READY
154770	154770	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-01	HIGH		READY
144667	144667	Coupe	9Y0	9YB	5	EU-PORSCHE-CAYENNE-9Y0-COUPE-TURBO-GT-01	HIGH	Factory Cayenne Coupe/Turbo GT body despite SUV input.	READY
145106	145106	SUV	9Y0	9YA	5	EU-PORSCHE-CAYENNE-9Y0-SUV-TURBO-S-EHYBRID-01	HIGH		READY
56877	56877	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH		READY
107543	107543	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	HIGH		READY
56026	56026	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH		READY
11656	11656	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH		READY
107545	107545	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-TURBO-01	HIGH		READY
56878	56878	SUV	958	92A	5	EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	HIGH		READY
111985	111985	SUV	958 facelift	92A	5	EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-TURBO-S-01	HIGH		READY
163562	163562	SUV	Cayenne Electric		5	EU-PORSCHE-CAYENNE-ELECTRIC-SUV-STANDARD-01	HIGH		READY
16695	16695	SUV	955	9PA	5	EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	HIGH		READY
156240	156240	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-EHYBRID-01	HIGH		READY
156241	156241	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-EHYBRID-01	HIGH		READY
164509	164509	SUV	Cayenne Electric		5	EU-PORSCHE-CAYENNE-ELECTRIC-SUV-STANDARD-01	HIGH		READY
16848	16848	SUV	955	9PA	5	EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	HIGH		READY
156111	156111	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-TURBO-EHYBRID-01	HIGH		READY
156112	156112	SUV	9Y0 facelift	9YA	5	EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-TURBO-EHYBRID-01	HIGH		READY
163563	163563	SUV	Cayenne Electric		5	EU-PORSCHE-CAYENNE-ELECTRIC-SUV-STANDARD-01	HIGH		READY
18918	18918	SUV	955	9PA	5	EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	HIGH		READY
57364	57364	Coupe	981	981C	2	EU-PORSCHE-CAYMAN-981-COUPE-STANDARD-01	HIGH		READY
111984	111984	Coupe	981	981C	2	EU-PORSCHE-CAYMAN-981-COUPE-GT4-01	HIGH		READY
101142	101142	Coupe	981	981C	2	EU-PORSCHE-CAYMAN-981-COUPE-GTS-01	HIGH		READY
11323	11323	Coupe	987 facelift	987C	2	EU-PORSCHE-CAYMAN-987-FACELIFT-COUPE-R-01	HIGH		READY
18917	18917	Coupe	987	987C	2	EU-PORSCHE-CAYMAN-987-COUPE-S-01	HIGH		READY
57365	57365	Coupe	981	981C	2	EU-PORSCHE-CAYMAN-981-COUPE-S-01	HIGH		READY
107478	107478	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	HIGH		READY
117979	117979	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-02	HIGH		READY
145236	145236	SUV	95B facelift 2018	95B	5	EU-PORSCHE-MACAN-95B-FACELIFT-2018-SUV-STANDARD-01	HIGH		READY
154487	154487	SUV	95B facelift 2021	95B	5	EU-PORSCHE-MACAN-95B-FACELIFT-2021-SUV-GTS-01	HIGH		READY
154486	154486	SUV	95B facelift 2021	95B	5	EU-PORSCHE-MACAN-95B-FACELIFT-2021-SUV-S-01	HIGH		READY
117977	117977	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-GTS-01	HIGH		READY
100638	100638	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	HIGH		READY
100640	100640	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	HIGH		READY
105798	105798	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	HIGH		READY
105802	105802	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-02	HIGH		READY
107684	107684	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	MEDIUM		READY
100639	100639	SUV	95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-TURBO-01	HIGH		READY
157639	157639	SUV	Macan Electric	XAB	5	EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-STANDARD-01	HIGH		READY
800552	800552	SUV	Macan Electric	XAB	5	EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-STANDARD-01	HIGH		READY
800553	800553	SUV	Macan Electric	XAB	5	EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-STANDARD-01	HIGH		READY
802752	802752	SUV	Macan Electric	XAB	5	EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-GTS-01	HIGH		READY
157641	157641	SUV	Macan Electric	XAB	5	EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-STANDARD-01	HIGH		READY
156875	156875	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-STANDARD-01	HIGH		READY
124806	124806	Hatchback	971	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-STANDARD-01	HIGH		READY
59591	59591	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
156876	156876	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-STANDARD-01	HIGH		READY
126896	126896	Wagon	971	971	5	EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	HIGH		READY
158093	158093	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-STANDARD-01	HIGH		READY
126897	126897	Wagon	971	971	5	EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	HIGH		READY
144319	144319	Wagon	971 facelift	971	5	EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	HIGH		READY
144472	144472	Hatchback	971 facelift	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-STANDARD-01	HIGH		READY
158094	158094	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-STANDARD-01	HIGH		READY
124807	124807	Hatchback	971	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-EXECUTIVE-01	HIGH	TecDoc Ktype identifies Executive long-wheelbase body.	READY
126894	126894	Wagon	971	971	5	EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	HIGH		READY
59590	59590	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
11691	11691	Hatchback	970	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-STANDARD-01	HIGH		READY
15981	15981	Hatchback	970	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-STANDARD-01	HIGH		READY
100636	100636	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
59589	59589	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
59585	59585	Hatchback	970	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-STANDARD-01	HIGH		READY
59587	59587	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
59592	59592	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
800207	800207	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-GTS-01	HIGH		READY
126899	126899	Wagon	971	971	5	EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	HIGH		READY
126898	126898	Wagon	971	971	5	EU-PORSCHE-PANAMERA-971-WAGON-TURBO-01	HIGH		READY
157717	157717	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-TURBO-EHYBRID-01	HIGH		READY
126908	126908	Hatchback	971	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-EXECUTIVE-TURBO-S-EHYBRID-01	HIGH	TecDoc Ktype identifies Executive long-wheelbase body.	READY
146731	146731	Hatchback	971 facelift	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-TURBO-S-EHYBRID-01	HIGH		READY
146732	146732	Wagon	971 facelift	971	5	EU-PORSCHE-PANAMERA-971-WAGON-TURBO-01	HIGH		READY
800281	800281	Hatchback	976	976	5	EU-PORSCHE-PANAMERA-976-HATCHBACK-TURBO-EHYBRID-01	HIGH		READY
59594	59594	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-GTS-01	HIGH		READY
11703	11703	Hatchback	970	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-STANDARD-01	HIGH		READY
59593	59593	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
100637	100637	Hatchback	970 facelift	970	5	EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	HIGH		READY
145130	145130	Wagon	Y1	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	HIGH		READY
157964	157964	Wagon	Y1 facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	HIGH		READY
158556	158556	Sedan	Y1 facelift	Y1A	5	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
801122	801122	Sedan	Y1 facelift	Y1A	5	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
802695	802695	Wagon	Y1 facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	MEDIUM		READY
153385	153385	Wagon	Y1	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	HIGH		READY
153386	153386	Wagon	Y1	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH		READY
157971	157971	Wagon	Y1 facelift	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH		READY
157977	157977	Sedan	Y1 facelift	Y1A	5	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
158033	158033	Wagon	Y1 facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	HIGH		READY
145139	145139	Wagon	Y1	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	HIGH		READY
145147	145147	Sedan	Y1	Y1A	5	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
146967	146967	Wagon	Y1	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH		READY
```

[下载 left18448_13601-13700_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_13601-13700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	4782	1928	1699	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-955-s-4.5-v8-340hp-6724
EU-PORSCHE-CAYENNE-958-SUV-STANDARD-01	4846	1939	1705	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-ii-diesel-3.0-v6-245hp-tiptronic-31431
EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-STANDARD-01	4855	1939	1705	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-ii-facelift-2014-3.6-v6-300hp-tiptronic-21433
EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-GTS-01	4855	1954	1688	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-ii-facelift-2014-gts-3.6-v6-440hp-tiptronic-21438
EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-TURBO-01	4855	1939	1702	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-ii-facelift-2014-turbo-4.8-v8-520hp-tiptronic-21439
EU-PORSCHE-CAYENNE-958-FACELIFT-SUV-TURBO-S-01	4855	1954	1702	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-ii-facelift-2014-turbo-s-4.8-v8-570hp-tiptronic-21440
EU-PORSCHE-CAYENNE-9Y0-SUV-TURBO-S-EHYBRID-01	4926	1983	1673	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-turbo-s-4.0-v8-680hp-e-hybrid-tiptronic-s-37479
EU-PORSCHE-CAYENNE-9Y0-COUPE-TURBO-GT-01	4942	1995	1636	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-coupe-turbo-gt-4.0-v8-640hp-tiptronic-s-43791
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-STANDARD-01	4930	1983	1698	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-3.0-v6-353hp-tiptronic-s-48443
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-01	4930	1983	1697	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-s-4.0-v8-474hp-tiptronic-s-48444
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-EHYBRID-01	4930	1983	1696	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-3.0-v6-470hp-e-hybrid-tiptronic-s-48445
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-S-EHYBRID-01	4930	1983	1678	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-s-3.0-v6-519hp-e-hybrid-tiptronic-s-49734
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-TURBO-EHYBRID-01	4930	1983	1685	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-turbo-4.0-v8-739hp-e-hybrid-tiptronic-s-49735
EU-PORSCHE-CAYENNE-9Y0-FACELIFT-SUV-GTS-01	4930	1983	1674	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-gts-4.0-v8-500hp-tiptronic-s-51610
EU-PORSCHE-CAYENNE-ELECTRIC-SUV-STANDARD-01	4985	1980	1674	Porsche Newsroom	https://newsroom.porsche.com/en_PME/2025/products/porsche-cayenne-electric-technological-milestone-41129.html
EU-PORSCHE-CAYMAN-987-COUPE-S-01	4341	1801	1305	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-s-3.4-295hp-6693
EU-PORSCHE-CAYMAN-987-FACELIFT-COUPE-R-01	4347	1801	1285	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-facelift-2009-r-3.4-330hp-40907
EU-PORSCHE-CAYMAN-981-COUPE-STANDARD-01	4380	1801	1294	Auto-Data	https://www.auto-data.net/en/porsche-cayman-981c-2.7-275hp-21379
EU-PORSCHE-CAYMAN-981-COUPE-S-01	4380	1801	1295	Auto-Data	https://www.auto-data.net/en/porsche-cayman-981c-s-3.4-325hp-21384
EU-PORSCHE-CAYMAN-981-COUPE-GTS-01	4404	1801	1284	Auto-Data	https://www.auto-data.net/en/porsche-cayman-981c-gts-3.4-340hp-21386
EU-PORSCHE-CAYMAN-981-COUPE-GT4-01	4438	1817	1266	Auto-Data	https://www.auto-data.net/en/porsche-cayman-981c-gt4-3.8-385hp-21388
EU-PORSCHE-MACAN-95B-SUV-STANDARD-01	4681	1923	1624	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-s-3.0-v6-340hp-pdk-21420
EU-PORSCHE-MACAN-95B-SUV-STANDARD-02	4697	1923	1624	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-s-3.0-diesel-v6-250hp-pdk-52047
EU-PORSCHE-MACAN-95B-SUV-TURBO-01	4699	1923	1624	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-turbo-3.6-v6-400hp-pdk-21422
EU-PORSCHE-MACAN-95B-SUV-GTS-01	4692	1926	1609	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-gts-3.0-v6-360hp-dct-23182
EU-PORSCHE-MACAN-95B-FACELIFT-2018-SUV-STANDARD-01	4696	1923	1624	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2018-2.0-245hp-pdk-34454
EU-PORSCHE-MACAN-95B-FACELIFT-2021-SUV-S-01	4726	1927	1621	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2021-s-2.9-v6-380hp-pdk-44009
EU-PORSCHE-MACAN-95B-FACELIFT-2021-SUV-GTS-01	4726	1927	1596	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2021-gts-2.9-v6-440hp-pdk-44010
EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-STANDARD-01	4784	1938	1622	Porsche Newsroom	https://newsroom.porsche.com/en/press-kits/the-new-porsche-macan/Alltagstauglichkeit-und-Komfort.html
EU-PORSCHE-MACAN-XAB-ELECTRIC-SUV-GTS-01	4805	1952	1613	ADAC	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/porsche/macan/xab/345953/
EU-PORSCHE-PANAMERA-970-HATCHBACK-STANDARD-01	4970	1931	1418	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-3.6-v6-300hp-37938
EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-STANDARD-01	5015	1931	1418	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-ii-3.6-v6-310hp-pdk-21423
EU-PORSCHE-PANAMERA-970-FACELIFT-HATCHBACK-GTS-01	5015	1931	1408	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-ii-gts-4.8-v8-440hp-pdk-21430
EU-PORSCHE-PANAMERA-971-HATCHBACK-STANDARD-01	5049	1937	1423	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-3.0-v6-330hp-pdk-26984
EU-PORSCHE-PANAMERA-971-HATCHBACK-TURBO-S-EHYBRID-01	5049	1937	1427	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-ii-turbo-s-4.0-v8-700hp-e-hybrid-pdk-42320
EU-PORSCHE-PANAMERA-971-HATCHBACK-EXECUTIVE-01	5199	1937	1428	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-executive-4-3.0-v6-330hp-pdk-26986
EU-PORSCHE-PANAMERA-971-HATCHBACK-EXECUTIVE-TURBO-S-EHYBRID-01	5199	1937	1432	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-executive-turbo-s-4.0-v8-680hp-e-hybrid-pdk-31920
EU-PORSCHE-PANAMERA-971-WAGON-STANDARD-01	5049	1937	1428	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-4-3.0-v6-330hp-pdk-30548
EU-PORSCHE-PANAMERA-971-WAGON-TURBO-01	5049	1937	1432	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-turbo-4.0-v8-550hp-pdk-30430
EU-PORSCHE-PANAMERA-976-HATCHBACK-STANDARD-01	5052	1937	1423	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g3-4s-2.9-v6-544hp-e-hybrid-pdk-51285
EU-PORSCHE-PANAMERA-976-HATCHBACK-TURBO-EHYBRID-01	5054	1937	1423	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g3-turbo-4.0-v8-680hp-e-hybrid-pdk-50564
EU-PORSCHE-PANAMERA-976-HATCHBACK-GTS-01	5052	1937	1415	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g3-gts-4.0-v8-500hp-pdk-52291
EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	4963	1966	1379	Auto-Data	https://www.auto-data.net/en/porsche-taycan-y1a-4s-performance-plus-93.4-kwh-571hp-37877
EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	4974	1966	1409	Auto-Data	https://www.auto-data.net/en/porsche-taycan-cross-turismo-y1a-4-93.4-kwh-476hp-42445
EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	4974	1967	1409	Auto-Data	https://www.auto-data.net/en/porsche-taycan-cross-turismo-y1a-facelift-2024-4-105-kwh-435hp-51173
EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	4963	1966	1390	Auto-Data	https://www.auto-data.net/en/porsche-taycan-sport-turismo-y1a-4s-performance-plus-93.4-kwh-571hp-45725
```

[下载 left18448_13601-13700_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_13601-13700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/porsche-cayenne-iii-facelift-2023-gts-4.0-v8-500hp-tiptronic-s-51610 "Porsche Cayenne III (facelift 2023) GTS 4.0 V8 (500 Hp) Tiptronic S | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5283 行）
- 累计尺寸组：dimension_groups_final.tsv（1503 行）

