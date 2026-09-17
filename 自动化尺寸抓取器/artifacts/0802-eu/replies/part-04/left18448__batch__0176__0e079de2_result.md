# 任务：left18448 第 17501-17600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0176__0e079de2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17501-17600 行

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
left18448 第 17501-17600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17501-17600_ktype_dimension_mapping_final.tsv
- left18448_17501-17600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	4204	1759	1485

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Golf v	2.0 FSI	Schrägheck	Frontantrieb	Benzin	Jan 2004	Nov 2008	17281
VW	Golf v	2.0 FSI 4motion	Schrägheck	Allrad	Benzin	Aug 2004	Nov 2008	18386
VW	Golf v	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Oct 2004	Feb 2009	18387
VW	Golf v	2.0 SDI	Schrägheck	Frontantrieb	Diesel	Jan 2004	Nov 2008	17871
VW	Golf v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2005	Nov 2008	18919
VW	Golf v	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	Oct 2003	Nov 2008	17280
VW	Golf v	2.0 TDI 16V 4motion	Schrägheck	Allrad	Diesel	Aug 2004	Nov 2008	18385
VW	Golf v	3.2 R32 4motion	Schrägheck	Allrad	Benzin	Nov 2005	Nov 2008	18921
VW	Golf vi	2.5	Schrägheck	Frontantrieb	Benzin	Jul 2009	May 2013	58524
VW	Golf vi	1.2 TSI 16V	Cabriolet	Frontantrieb	Benzin	Nov 2013	May 2016	11973
VW	Golf vi	1.4 TSI	Cabriolet	Frontantrieb	Benzin	Nov 2013	May 2016	115171
VW	Golf vi	1.4 TSI	Cabriolet	Frontantrieb	Benzin	Nov 2013	May 2016	115173
VW	Golf vi	1.8 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2009	Jan 2011	34879
VW	Golf vi	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Jun 2009	Nov 2013	10431
VW	Golf vi	2.0 GTI	Schrägheck	Frontantrieb	Benzin	May 2011	Nov 2012	10524
VW	Golf vi	2.0 R	Cabriolet	Frontantrieb	Benzin	Jan 2013	May 2016	59290
VW	Golf vi	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Nov 2013	May 2016	115175
VW	Golf vi	Blue E-motion	Schrägheck	Frontantrieb	Elektro	Dec 2010	Nov 2013	53583
VW	Golf vi variant	1.2 TSI	Kombi	Frontantrieb	Benzin	Jul 2010	Jul 2013	34793
VW	Golf vi variant	1.6 Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	Jul 2010	Jul 2013	6055
VW	Golf vi variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Jul 2009	Jul 2013	34795
VW	Golf vi variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Jan 2010	Jul 2013	58749
VW	Golf vi variant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	Jul 2009	Jul 2013	58748
VW	Golf vii	1.6	Schrägheck	Frontantrieb	Benzin	May 2014	Jul 2017	107945
VW	Golf vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Aug 2020	115566
VW	Golf vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2016	Aug 2020	124239
VW	Golf vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2017	Jul 2019	125997
VW	Golf vii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2012	Mar 2017	56142
VW	Golf vii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Aug 2020	57456
VW	Golf vii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2014	Mar 2017	105901
VW	Golf vii	1.4 GTE Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	May 2014	Aug 2020	106227
VW	Golf vii	1.4 TGI CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jun 2013	Jul 2018	45814
VW	Golf vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2012	Aug 2020	56144
VW	Golf vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Mar 2017	57459
VW	Golf vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Aug 2020	105911
VW	Golf vii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Mar 2021	105912
VW	Golf vii	1.4 TSI Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	Nov 2012	Mar 2017	57462
VW	Golf vii	1.4 TSI Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	Dec 2013	Jul 2018	106414
VW	Golf vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Apr 2017	Aug 2020	126840
VW	Golf vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Aug 2020	128344
VW	Golf vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2012	Mar 2017	56145
VW	Golf vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2013	Jul 2018	59067
VW	Golf vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Jan 2013	Mar 2017	59068
VW	Golf vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2016	Aug 2020	124240
VW	Golf vii	1.6 TDI 4motion	Schrägheck	Allrad	Diesel	Nov 2012	Mar 2017	57460
VW	Golf vii	1.6 TDI 4motion	Schrägheck	Allrad	Diesel	Jan 2013	Mar 2017	59289
VW	Golf vii	2.0 GTD	Schrägheck	Frontantrieb	Diesel	Apr 2013	Aug 2020	59120
VW	Golf vii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Apr 2013	Aug 2020	59115
VW	Golf vii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Apr 2013	Aug 2020	59116
VW	Golf vii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Nov 2013	Jul 2017	106229
VW	Golf vii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Mar 2017	Aug 2020	126007
VW	Golf vii	2.0 GTI Clubsport	Schrägheck	Frontantrieb	Benzin	Feb 2016	Mar 2017	118645
VW	Golf vii	2.0 GTI Clubsport S	Schrägheck	Frontantrieb	Benzin	Sep 2016	Mar 2017	120193
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	Nov 2013	Mar 2017	100074
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	Nov 2013	Aug 2020	100075
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	Dec 2016	Aug 2020	125943
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	Dec 2016	Aug 2020	125995
VW	Golf vii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2012	Aug 2020	56147
VW	Golf vii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2012	Aug 2020	59070
VW	Golf vii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	Aug 2020	59071
VW	Golf vii	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	Nov 2012	Aug 2020	57461
VW	Golf vii	E-golf	Schrägheck	Frontantrieb	Elektro	Mar 2014	Feb 2017	101041
VW	Golf vii	E-golf	Schrägheck	Frontantrieb	Elektro	Dec 2016	Jan 2021	126625
VW	Golf vii van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	Nov 2016	Aug 2020	803187
VW	Golf vii variant	1.6	Kombi	Frontantrieb	Benzin	May 2014	Jul 2017	107946
VW	Golf vii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	May 2015	Aug 2020	115568
VW	Golf vii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	Nov 2016	Aug 2020	124242
VW	Golf vii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	Jan 2017	Jul 2019	125998
VW	Golf vii variant	1.2 TSI	Kombi	Frontantrieb	Benzin	May 2013	Mar 2017	58926
VW	Golf vii variant	1.2 TSI	Kombi	Frontantrieb	Benzin	Apr 2013	Aug 2020	58943
VW	Golf vii variant	1.2 TSI	Kombi	Frontantrieb	Benzin	Apr 2014	Mar 2017	105917
VW	Golf vii variant	1.4 TSI	Kombi	Frontantrieb	Benzin	May 2013	Mar 2017	58944
VW	Golf vii variant	1.4 TSI	Kombi	Frontantrieb	Benzin	May 2014	Aug 2020	105919
VW	Golf vii variant	1.4 TSI	Kombi	Frontantrieb	Benzin	May 2014	Mar 2021	106231
VW	Golf vii variant	1.4 TSI Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	Apr 2013	Mar 2017	100072
VW	Golf vii variant	1.4 TSI Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	May 2014	Mar 2017	106415
VW	Golf vii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	Apr 2017	Aug 2020	126844
VW	Golf vii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	Jul 2017	Aug 2020	128340
VW	Golf vii variant	1.6 TDI	Kombi	Frontantrieb	Diesel	May 2013	Mar 2017	58945
VW	Golf vii variant	1.6 TDI	Kombi	Frontantrieb	Diesel	Nov 2016	Aug 2020	124243
VW	Golf vii variant	1.6 TDI 4motion	Kombi	Allrad	Diesel	May 2013	Mar 2017	106416
VW	Golf vii variant	2.0 GTD	Kombi	Frontantrieb	Diesel	Jan 2015	Jul 2019	109842
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	Mar 2015	Aug 2020	112296
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	Mar 2015	Mar 2017	113320
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	Dec 2016	Aug 2020	125944
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	Dec 2016	Aug 2020	125996
VW	Golf vii variant	2.0 TDI	Kombi	Frontantrieb	Diesel	Apr 2013	Aug 2020	58946
VW	Golf viii	1.0 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2020	-	142889
VW	Golf viii	1.4 GTE Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2020	-	144084
VW	Golf viii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	144993
VW	Golf viii	1.4 TSI Ehybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2020	-	146214
VW	Golf viii	1.5 Ehybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	800298
VW	Golf viii	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2020	-	146184
VW	Golf viii	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2024	-	157955
VW	Golf viii	1.5 GTE Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	158703
VW	Golf viii	1.5 TGI	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Sep 2020	-	142908
VW	Golf viii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	157954
VW	Golf viii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Jun 2024	-	158710
VW	Golf viii	2.0 GTI 50	Schrägheck	Frontantrieb	Benzin	Oct 2025	-	802557
VW	Golf viii	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	Sep 2020	-	142910


--- Round 1 / 首次发送 ---
## 更新点

复用了既有 Golf V 标准尺寸组；经复核，Golf V GTI 与 R32 的保险杠、车高等外廓尺寸确实不同，因此分别建立独立尺寸组，没有错([汽车数据网][1])([auto-data.net][1])

Golf VII 仅对生产期实际跨越、且前后期三维明确变化的 Ktype 派生 `_prefl/_facelift`；Golf VII R Variant 依据 Volkswagen 车型资料保持单一尺寸组。Golf VIII 的 2024 改款、GTE、eHybrid、GTI 和 GTI Edition 50 按已确认的独立三维建组。([汽车数据网][2])
输入 Ktype：100/100
最终映射行：126
最终尺寸组：32
PENDING：0
机械终检：表头、列数、ID 唯一性、Ktype 覆盖、尺寸组引用闭合、三维正整数、来源及 URL 非空均已通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17281	17281	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18386	18386	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18387	18387	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-GTI-01	HIGH		READY
17871	17871	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18919	18919	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
17280	17280	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18385	18385	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	HIGH		READY
18921	18921	Hatchback	Golf V (A5)			EU-VW-GOLF-V-A5-HATCHBACK-R32-01	HIGH		READY
58524	58524	Hatchback	Golf VI (A6)			EU-VW-GOLF-VI-A6-HATCHBACK-25-01	HIGH		READY
11973	11973	Convertible	Golf VI (A6)			EU-VW-GOLF-VI-A6-CONVERTIBLE-STANDARD-01	HIGH		READY
115171	115171	Convertible	Golf VI (A6)			EU-VW-GOLF-VI-A6-CONVERTIBLE-STANDARD-01	HIGH		READY
115173	115173	Convertible	Golf VI (A6)			EU-VW-GOLF-VI-A6-CONVERTIBLE-STANDARD-01	HIGH		READY
34879	34879	Hatchback	Golf VI (A6)			EU-VW-GOLF-VI-A6-HATCHBACK-STANDARD-01	HIGH		READY
10431	10431	Hatchback	Golf VI (A6)			EU-VW-GOLF-VI-A6-HATCHBACK-GTI-01	HIGH		READY
10524	10524	Hatchback	Golf VI (A6)			EU-VW-GOLF-VI-A6-HATCHBACK-GTI-01	HIGH		READY
59290	59290	Convertible	Golf VI (A6)			EU-VW-GOLF-VI-A6-CONVERTIBLE-R-01	HIGH		READY
115175	115175	Convertible	Golf VI (A6)			EU-VW-GOLF-VI-A6-CONVERTIBLE-STANDARD-01	HIGH		READY
53583	53583	Hatchback	Golf VI (A6)			EU-VW-GOLF-VI-A6-HATCHBACK-STANDARD-01	HIGH		READY
34793	34793	Wagon	Golf VI (A6)			EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	HIGH		READY
6055	6055	Wagon	Golf VI (A6)			EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	HIGH		READY
34795	34795	Wagon	Golf VI (A6)			EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	HIGH		READY
58749	58749	Wagon	Golf VI (A6)			EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	HIGH		READY
58748	58748	Wagon	Golf VI (A6)			EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	HIGH		READY
107945_prefl	107945	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
107945_facelift	107945	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
115566_prefl	115566	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
115566_facelift	115566	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
124239	124239	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
125997	125997	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
56142	56142	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
57456_prefl	57456	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
57456_facelift	57456	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105901	105901	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
106227_prefl	106227	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTE-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106227_facelift	106227	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTE-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
45814_prefl	45814	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
45814_facelift	45814	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
56144_prefl	56144	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
56144_facelift	56144	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
57459	57459	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
105911_prefl	105911	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105911_facelift	105911	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105912_prefl	105912	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105912_facelift	105912	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
57462	57462	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
106414_prefl	106414	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106414_facelift	106414	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
126840	126840	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
128344	128344	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
56145	56145	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
59067_prefl	59067	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59067_facelift	59067	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59068	59068	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
124240	124240	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
57460	57460	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
59289	59289	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
59120_prefl	59120	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59120_facelift	59120	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59115_prefl	59115	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59115_facelift	59115	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTI-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59116_prefl	59116	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59116_facelift	59116	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTI-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106229_prefl	106229	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106229_facelift	106229	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTI-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
126007	126007	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-GTI-FACELIFT-01	HIGH		READY
118645	118645	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	HIGH		READY
120193	120193	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	HIGH		READY
100074	100074	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-R-PREFL-01	HIGH		READY
100075_prefl	100075	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-R-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
100075_facelift	100075	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-R-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
125943	125943	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-R-FACELIFT-01	HIGH		READY
125995	125995	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-R-FACELIFT-01	HIGH		READY
56147_prefl	56147	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
56147_facelift	56147	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59070_prefl	59070	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59070_facelift	59070	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59071_prefl	59071	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
59071_facelift	59071	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
57461_prefl	57461	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
57461_facelift	57461	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
101041	101041	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-EGOLF-PREFL-01	HIGH		READY
126625	126625	Hatchback	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-EGOLF-FACELIFT-01	HIGH		READY
803187	803187	Van	Golf VII (A7)			EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	HIGH	Commercial cargo conversion; exterior follows the corresponding hatchback phase.	READY
107946_prefl	107946	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
107946_facelift	107946	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
115568_prefl	115568	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
115568_facelift	115568	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
124242	124242	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	HIGH		READY
125998	125998	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	HIGH		READY
58926	58926	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
58943_prefl	58943	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
58943_facelift	58943	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105917	105917	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
58944	58944	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
105919_prefl	105919	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
105919_facelift	105919	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106231_prefl	106231	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
106231_facelift	106231	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
100072	100072	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
106415	106415	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
126844	126844	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	HIGH		READY
128340	128340	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	HIGH		READY
58945	58945	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
124243	124243	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	HIGH		READY
106416	106416	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	HIGH		READY
109842_prefl	109842	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-GTD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
109842_facelift	109842	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
112296	112296	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-R-STANDARD-01	HIGH		READY
113320	113320	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-R-STANDARD-01	HIGH		READY
125944	125944	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-R-STANDARD-01	HIGH		READY
125996	125996	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-R-STANDARD-01	HIGH		READY
58946_prefl	58946	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
58946_facelift	58946	Wagon	Golf VII (A7)			EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	MEDIUM	Ktype production period spans the confirmed 2017 exterior-dimension change.	READY
142889	142889	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-HIGH-PREFL-01	HIGH		READY
144084	144084	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-HYBRID-PREFL-01	HIGH		READY
144993	144993	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
146214	146214	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-HYBRID-PREFL-01	HIGH		READY
800298	800298	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-EHYBRID-FACELIFT-01	HIGH		READY
146184	146184	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
157955	157955	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
158703	158703	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-GTE-FACELIFT-01	HIGH		READY
142908	142908	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-HIGH-PREFL-01	HIGH		READY
157954	157954	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-FACELIFT-01	HIGH		READY
158710	158710	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-GTI-FACELIFT-01	HIGH		READY
802557	802557	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-GTI50-FACELIFT-01	HIGH		READY
142910	142910	Hatchback	Golf VIII (A8)			EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-PREFL-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_17501-17600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-V-A5-HATCHBACK-STANDARD-01	4204	1759	1485	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-5-door-2.0-fsi-150hp-4motion-51654
EU-VW-GOLF-V-A5-HATCHBACK-GTI-01	4216	1759	1469	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-5-door-gti-2.0-tfsi-200hp-51651
EU-VW-GOLF-V-A5-HATCHBACK-R32-01	4246	1759	1465	Volkswagen specification sheet (archived copy)	https://www.australiancar.reviews/_pdfs/Volkswagen_Golf-R32_Mk5_Specifications_200607.pdf
EU-VW-GOLF-VI-A6-HATCHBACK-25-01	4210	1786	1479	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-2.5-170hp-tiptronic-51975
EU-VW-GOLF-VI-A6-CONVERTIBLE-STANDARD-01	4246	1782	1423	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-1.4-tsi-122hp-20414
EU-VW-GOLF-VI-A6-HATCHBACK-STANDARD-01	4199	1786	1480	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-1.8-tsi-160hp-42837
EU-VW-GOLF-VI-A6-HATCHBACK-GTI-01	4213	1786	1469	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-gti-2.0-tsi-210hp-dsg-41229
EU-VW-GOLF-VI-A6-CONVERTIBLE-R-01	4266	1782	1405	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-r-2.0-tsi-265hp-dsg-41903
EU-VW-GOLF-VI-A6-WAGON-STANDARD-01	4534	1781	1504	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-6-variant-profile-19529
EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-PREFL-01	4255	1799	1452	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-1.2-tsi-105hp-17885
EU-VW-GOLF-VII-A7-HATCHBACK-STANDARD-FACELIFT-01	4258	1799	1492	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.6-tdi-115hp-27633
EU-VW-GOLF-VII-A7-HATCHBACK-GTE-PREFL-01	4270	1799	1457	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-gte-1.4-tsi-204hp-plug-in-hybrid-dsg-20418
EU-VW-GOLF-VII-A7-HATCHBACK-GTE-FACELIFT-01	4276	1799	1484	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-gte-1.4-tsi-204hp-plug-in-hybrid-dsg-52611
EU-VW-GOLF-VII-A7-HATCHBACK-PERFORMANCE-PREFL-01	4268	1799	1442	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-gti-2.0-tsi-220hp-18409
EU-VW-GOLF-VII-A7-HATCHBACK-GTD-FACELIFT-01	4268	1790	1482	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-gtd-2.0-tdi-184hp-28057
EU-VW-GOLF-VII-A7-HATCHBACK-GTI-FACELIFT-01	4268	1799	1482	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-gti-2.0-tsi-230hp-27832
EU-VW-GOLF-VII-A7-HATCHBACK-R-PREFL-01	4276	1799	1436	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-r-2.0-tsi-300hp-4motion-dsg-52617
EU-VW-GOLF-VII-A7-HATCHBACK-R-FACELIFT-01	4263	1799	1465	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-r-2.0-tsi-310hp-4motion-dsg-27651
EU-VW-GOLF-VII-A7-HATCHBACK-EGOLF-PREFL-01	4270	1799	1473	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-e-golf-24.2-kwh-115hp-44054
EU-VW-GOLF-VII-A7-HATCHBACK-EGOLF-FACELIFT-01	4270	1799	1482	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-e-golf-35.8-kwh-136hp-cvt-32179
EU-VW-GOLF-VII-A7-WAGON-STANDARD-PREFL-01	4562	1799	1481	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-variant-1.4-tsi-122hp-18425
EU-VW-GOLF-VII-A7-WAGON-STANDARD-FACELIFT-01	4567	1799	1515	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.0-tsi-116hp-36010
EU-VW-GOLF-VII-A7-WAGON-GTD-PREFL-01	4575	1799	1470	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vii-variant-gtd-2.0-tdi-184hp-23317
EU-VW-GOLF-VII-A7-WAGON-R-STANDARD-01	4586	1789	1495	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042
EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-HIGH-PREFL-01	4284	1789	1491	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-1.5-tgi-130hp-dsg-41967
EU-VW-GOLF-VIII-A8-HATCHBACK-HYBRID-PREFL-01	4287	1789	1484	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-gte-1.4-tsi-245hp-ehybrid-dsg-41337
EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-PREFL-01	4284	1789	1456	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-1.5-tsi-130hp-38151
EU-VW-GOLF-VIII-A8-HATCHBACK-EHYBRID-FACELIFT-01	4289	1789	1476	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-facelift-2024-1.5-tsi-204hp-ehybrid-dsg-51778
EU-VW-GOLF-VIII-A8-HATCHBACK-STANDARD-FACELIFT-01	4282	1789	1483	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-facelift-2024-1.5-tsi-150hp-51250
EU-VW-GOLF-VIII-A8-HATCHBACK-GTE-FACELIFT-01	4289	1789	1478	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-facelift-2024-gte-1.5-tsi-272hp-ehybrid-dsg-51779
EU-VW-GOLF-VIII-A8-HATCHBACK-GTI-FACELIFT-01	4289	1789	1471	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-facelift-2024-gti-2.0-tsi-265hp-dsg-51761
EU-VW-GOLF-VIII-A8-HATCHBACK-GTI50-FACELIFT-01	4292	1789	1463	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-viii-facelift-2024-gti-edition-50-2.0-tsi-325hp-dsg-55683
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_17501-17600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volkswagen-golf-v-5-door-gti-2.0-tfsi-200hp-51651?utm_source=chatgpt.com "Volkswagen Golf V (5-door) GTI 2.0 TFSI (200 Hp)"
[2]: https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.6-tdi-115hp-27633?utm_source=chatgpt.com "Volkswagen Golf VII (5-door, facelift 2017) 1.6 TDI (115 Hp)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4530 行）
- 累计尺寸组：dimension_groups_final.tsv（1089 行）

