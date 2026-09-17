# 任务：left18448 第 13001-13100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0131__d1cc98e0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13001-13100 行

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
left18448 第 13001-13100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13001-13100_ktype_dimension_mapping_final.tsv
- left18448_13001-13100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PEUGEOT-206-I-HATCHBACK-RC-01	3835	1673	1425
EU-PEUGEOT-206-I-HATCHBACK-S16-01	3835	1673	1433
EU-PEUGEOT-206-I-HATCHBACK-STANDARD-FACELIFT-02	3822	1652	1425
EU-PEUGEOT-206-I-HATCHBACK-STANDARD-PREFL-02	3835	1652	1432
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	3962	1739	1460
EU-PEUGEOT-5008-I-MPV-STANDARD-01	4529	1837	1639
EU-PEUGEOT-5008-II-SUV-STANDARD-01	4641	1844	1646
EU-PEUGEOT-5008-III-SUV-STANDARD-01	4791	1895	1694

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Peugeot	5008	HDI 136	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2012	Mar 2017	142668
Peugeot	5008	HDI 150	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2009	Mar 2017	142665
Peugeot	5008	HDI 165	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2009	Mar 2017	142666
Peugeot	5008	Hybrid 136	SUV	Frontantrieb	Benzin/Elektro	Aug 2024	-	800011
Peugeot	5008	Hybrid 145	SUV	Frontantrieb	Benzin/Elektro	Mar 2025	-	801560
Peugeot	5008	Plug-in Hybrid 195	SUV	Frontantrieb	Benzin/Elektro	Aug 2024	-	800448
Peugeot	5008	Plug-in Hybrid 225	SUV	Frontantrieb	Benzin/Elektro	Feb 2026	-	803192
Peugeot	106 ii	1.5 D	Schrägheck	Frontantrieb	Diesel	Apr 1998	Jul 2004	16156
Peugeot	106 van ii	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	Apr 1996	Mar 2001	13514
Peugeot	2008 i	1.2 THP 110 / Puretech 110	SUV	Frontantrieb	Benzin	Jan 2015	-	111916
Peugeot	2008 i	1.2 THP 130 / Puretech 130	SUV	Frontantrieb	Benzin	Jan 2015	Nov 2019	111917
Peugeot	2008 i	1.2 VTI	SUV	Frontantrieb	Benzin	Mar 2013	Dec 2018	58874
Peugeot	2008 i	1.4 HDI	SUV	Frontantrieb	Diesel	Jun 2013	-	59316
Peugeot	2008 i	1.6 Bluehdi	SUV	Frontantrieb	Diesel	Jul 2014	-	117333
Peugeot	2008 i	1.6 Bluehdi 100	SUV	Frontantrieb	Diesel	Jan 2015	Nov 2019	111920
Peugeot	2008 i	1.6 Bluehdi 120	SUV	Frontantrieb	Diesel	Jul 2014	Apr 2018	109331
Peugeot	2008 i	1.6 Bluehdi 75	SUV	Frontantrieb	Diesel	Jan 2015	Nov 2019	113672
Peugeot	2008 i	1.6 HDI	SUV	Frontantrieb	Diesel	Mar 2013	-	58876
Peugeot	2008 i	1.6 HDI	SUV	Frontantrieb	Diesel	Mar 2013	-	58877
Peugeot	2008 i	1.6 VTI	SUV	Frontantrieb	Benzin	Mar 2013	-	58875
Peugeot	2008 i van	Bluehdi 100	Kasten/SUV	Frontantrieb	Diesel	May 2018	-	142638
Peugeot	2008 i van	Bluehdi 120	Kasten/SUV	Frontantrieb	Diesel	May 2018	-	142639
Peugeot	2008 i van	Puretech 130	Kasten/SUV	Frontantrieb	Benzin	Jan 2018	Nov 2019	142637
Peugeot	2008 ii	1.2 Hybrid 110	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	802715
Peugeot	2008 ii	1.2 Hybrid 136	SUV	Frontantrieb	Benzin/Elektro	Nov 2023	-	156997
Peugeot	2008 ii	1.2 Hybrid 145	SUV	Frontantrieb	Benzin/Elektro	Mar 2025	-	801563
Peugeot	2008 ii	1.5 Bluehdi 110	SUV	Frontantrieb	Diesel	Jan 2021	-	143254
Peugeot	2008 ii	E-2008	SUV	Frontantrieb	Elektro	Apr 2023	-	154661
Peugeot	205 ii	1.6 GTX	Schrägheck	Frontantrieb	Benzin	Jan 1987	Oct 1991	17621
Peugeot	206 cc	1.6 16V	Cabriolet	Frontantrieb	Benzin	Sep 2000	Dec 2007	15704
Peugeot	206 cc	1.6 HDI 110	Cabriolet	Frontantrieb	Diesel	Apr 2005	Feb 2007	18477
Peugeot	206 cc	2.0 S16	Cabriolet	Frontantrieb	Benzin	Sep 2000	Dec 2007	14399
Peugeot	206 sw	1.1	Kombi	Frontantrieb	Benzin	Jul 2002	Feb 2007	16674
Peugeot	206 sw	1.4	Kombi	Frontantrieb	Benzin	Jul 2002	Feb 2007	16675
Peugeot	206 sw	1.4 16V	Kombi	Frontantrieb	Benzin	Oct 2003	-	17746
Peugeot	206 sw	1.4 HDI	Kombi	Frontantrieb	Diesel	Jul 2002	Feb 2007	16678
Peugeot	206 sw	1.6 16V	Kombi	Frontantrieb	Benzin	Jul 2002	-	16676
Peugeot	206 sw	1.6 HDI 110	Kombi	Frontantrieb	Diesel	May 2004	-	18107
Peugeot	206 sw	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Jul 2002	Feb 2007	56080
Peugeot	206 sw	2.0 16V	Kombi	Frontantrieb	Benzin	Jul 2002	Feb 2007	16677
Peugeot	206 sw	2.0 HDI	Kombi	Frontantrieb	Diesel	Jul 2002	Feb 2007	16836
Peugeot	206 van	1.4 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	Sep 2001	Mar 2009	12492
Peugeot	206+	1.1	Schrägheck	Frontantrieb	Benzin	Jan 2009	Jun 2013	33837
Peugeot	206+	1.4 HDI ECO 70	Schrägheck	Frontantrieb	Diesel	Jan 2009	Jun 2013	33839
Peugeot	206+	1.4 I	Schrägheck	Frontantrieb	Benzin	Jan 2009	Aug 2013	33838
Peugeot	207 sw	1.4 16V	Kombi	Frontantrieb	Benzin	Nov 2009	Dec 2012	52008
Peugeot	207 sw	1.6 16V Turbo	Kombi	Frontantrieb	Benzin	Feb 2007	Dec 2012	110730
Peugeot	207/207+	1.4	Schrägheck	Frontantrieb	Benzin	Aug 2008	Dec 2015	13008
Peugeot	207/207+	1.4	Schrägheck	Frontantrieb	Benzin	Apr 2006	Oct 2013	58565
Peugeot	207/207+	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2009	Dec 2012	58571
Peugeot	208 i	1.0 VTI	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2019	33804
Peugeot	208 i	1.2 GPL	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2015	Dec 2019	122065
Peugeot	208 i	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	Jan 2013	Dec 2019	107418
Peugeot	208 i	1.2 VTI 68 / Puretech 68	Schrägheck	Frontantrieb	Benzin	Aug 2016	Dec 2019	126685
Peugeot	208 i	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2019	33807
Peugeot	208 i	1.4 GPL	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Oct 2013	Dec 2019	117338
Peugeot	208 i	1.4 VTI	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2019	33823
Peugeot	208 i	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Jan 2015	Dec 2019	111924
Peugeot	208 i	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jan 2015	Dec 2019	109333
Peugeot	208 i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Aug 2012	Dec 2019	58650
Peugeot	208 i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	Oct 2014	Dec 2019	108642
Peugeot	208 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Jan 2015	Dec 2019	117336
Peugeot	208 i	1.6 HDI / Bluehdi 75	Schrägheck	Frontantrieb	Diesel	Jan 2013	Dec 2019	107419
Peugeot	208 i	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Mar 2015	Dec 2019	112328
Peugeot	208 i	1.6 VTI	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2019	33929
Peugeot	208 ii	1.2 Hybrid 100	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2023	-	155683
Peugeot	208 ii	1.2 Hybrid 136	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2023	-	156286
Peugeot	208 ii	1.2 Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	-	801859
Peugeot	208 ii	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Jun 2019	-	144436
Peugeot	208 ii	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	Oct 2019	-	144371
Peugeot	208 ii	1.6 VTI 115	Schrägheck	Frontantrieb	Benzin	Nov 2019	-	144434
Peugeot	208 ii	E-208	Schrägheck	Frontantrieb	Elektro	Jan 2023	-	151535
Peugeot	208 ii	E-208 GTI	Schrägheck	Frontantrieb	Elektro	Oct 2025	-	802032
Peugeot	208 ii	Hybrid 110	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	-	801562
Peugeot	3008 i	1.2	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Aug 2016	111987
Peugeot	3008 i	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	May 2014	Aug 2016	107941
Peugeot	3008 i	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Dec 2009	Aug 2016	33866
Peugeot	3008 i	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Aug 2016	58880
Peugeot	3008 i	1.6 Turbo	Großraumlimousine	Frontantrieb	Benzin	May 2014	Aug 2016	106340
Peugeot	3008 i	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Sep 2011	Aug 2016	59322
Peugeot	3008 i	2.0 HDI Hybrid4	Großraumlimousine	Allrad	Diesel/Elektro	Feb 2011	Aug 2016	53215
Peugeot	3008 ii	1.2 Hybrid 136	SUV	Frontantrieb	Benzin/Elektro	May 2023	Nov 2023	154451
Peugeot	3008 ii	1.2 Thp/ Puretech 130	SUV	Frontantrieb	Benzin	May 2016	-	121650
Peugeot	3008 ii	1.6 Bluehdi 100	SUV	Frontantrieb	Diesel	Nov 2016	Dec 2019	126187
Peugeot	3008 ii	1.6 Bluehdi 115	SUV	Frontantrieb	Diesel	Nov 2016	Dec 2019	126188
Peugeot	3008 ii	1.6 Bluehdi 120	SUV	Frontantrieb	Diesel	May 2016	Dec 2019	121646
Peugeot	3008 ii	1.6 THP 165	SUV	Frontantrieb	Benzin	May 2016	-	121649
Peugeot	3008 ii	2.0 Bluehdi 136	SUV	Frontantrieb	Diesel	Nov 2016	-	126189
Peugeot	3008 ii	2.0 Bluehdi 150	SUV	Frontantrieb	Diesel	May 2016	Sep 2020	121648
Peugeot	3008 ii	2.0 Bluehdi 180	SUV	Frontantrieb	Diesel	May 2016	-	121173
Peugeot	3008 ii	Hybrid 180	SUV	Frontantrieb	Benzin/Elektro	Nov 2022	-	151468
Peugeot	3008 iii	E-210	SUV	Frontantrieb	Elektro	Nov 2023	-	156879
Peugeot	3008 iii	E-230 Long Range	SUV	Frontantrieb	Elektro	Oct 2024	-	800996
Peugeot	3008 iii	E-325 AWD	SUV	Allrad	Elektro	Jul 2025	-	802056
Peugeot	3008 iii	Hybrid 136	SUV	Frontantrieb	Benzin/Elektro	Nov 2023	-	156880
Peugeot	3008 iii	Hybrid 145	SUV	Frontantrieb	Benzin/Elektro	Mar 2025	-	801561
Peugeot	3008 iii	Plug-in Hybrid 195	SUV	Frontantrieb	Benzin/Elektro	May 2024	-	800059
Peugeot	3008 iii	Plug-in Hybrid 225	SUV	Frontantrieb	Benzin/Elektro	Mar 2026	-	803433
Peugeot	3008 van	Bluehdi 130	Kasten/SUV	Frontantrieb	Diesel	Feb 2018	-	142647
Peugeot	3008 van	Bluehdi 180	Kasten/SUV	Frontantrieb	Diesel	Jan 2018	-	142648


--- Round 1 / 首次发送 ---
## 更新点

已按物理外廓聚类并复用既有 5008 I、5008 III、206 标准 Hatchback 和 208 I 5D 尺寸组。仅对有明确尺寸变化且 Ktype 跨越边界的 206 Van、207 Hatchback、207 SW 建立派生映射；207 改款前后长度分别为 Hatchback 4030→4045 mm、SW 4156→4164 mm。([汽车目录][1])

新一代 3008、5008 的尺寸采用 Peugeot 官方资料，宽度口径为不含外后视镜。([标致阿曼][2])

## 进度

* 输入 Ktype：100
* 最终映射行：104
* 最终尺寸组：24
* PENDING：0
* id、尺寸组 ID、引用闭合、正整数尺寸、来源及链接检查：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142668	142668	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
142665	142665	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
142666	142666	MPV	I		5	EU-PEUGEOT-5008-I-MPV-STANDARD-01	HIGH		READY
800011	800011	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
801560	801560	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
800448	800448	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
803192	803192	SUV	III		5	EU-PEUGEOT-5008-III-SUV-STANDARD-01	HIGH		READY
16156	16156	Hatchback	II			EU-PEUGEOT-106-II-HATCHBACK-STANDARD-01	HIGH		READY
13514	13514	Van	II		3	EU-PEUGEOT-106-II-VAN-ELECTRIC-01	MEDIUM	Electric panel-van derivative; dedicated exterior dimensions used.	READY
111916	111916	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
111917	111917	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
58874	58874	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
59316	59316	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
117333	117333	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
111920	111920	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
109331	109331	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
113672	113672	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
58876	58876	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
58877	58877	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
58875	58875	SUV	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	HIGH		READY
142638	142638	Van	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	MEDIUM	Commercial conversion retains the 2008 I SUV exterior envelope.	READY
142639	142639	Van	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	MEDIUM	Commercial conversion retains the 2008 I SUV exterior envelope.	READY
142637	142637	Van	I		5	EU-PEUGEOT-2008-I-SUV-STANDARD-01	MEDIUM	Commercial conversion retains the 2008 I SUV exterior envelope.	READY
802715	802715	SUV	II		5	EU-PEUGEOT-2008-II-SUV-FACELIFT-01	HIGH		READY
156997	156997	SUV	II		5	EU-PEUGEOT-2008-II-SUV-FACELIFT-01	HIGH		READY
801563	801563	SUV	II		5	EU-PEUGEOT-2008-II-SUV-FACELIFT-01	HIGH		READY
143254	143254	SUV	II		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH		READY
154661	154661	SUV	II		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH		READY
17621	17621	Hatchback	II	20A/C	3	EU-PEUGEOT-205-II-HATCHBACK-GTX-01	MEDIUM	Spanish-market GTX mapped to the matching three-door facelift body envelope.	READY
15704	15704	Convertible	I		2	EU-PEUGEOT-206-I-CONVERTIBLE-CC-01	HIGH		READY
18477	18477	Convertible	I		2	EU-PEUGEOT-206-I-CONVERTIBLE-CC-01	HIGH		READY
14399	14399	Convertible	I		2	EU-PEUGEOT-206-I-CONVERTIBLE-CC-01	HIGH		READY
16674	16674	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
16675	16675	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
17746	17746	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
16678	16678	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
16676	16676	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
18107	18107	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
56080	56080	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
16677	16677	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
16836	16836	Wagon	I		5	EU-PEUGEOT-206-I-WAGON-STANDARD-01	HIGH		READY
12492_prefl	12492	Van	I		3	EU-PEUGEOT-206-I-HATCHBACK-STANDARD-PREFL-02	MEDIUM	Pre-facelift exterior branch; this Ktype also covers the facelift branch.	READY
12492_facelift	12492	Van	I		3	EU-PEUGEOT-206-I-HATCHBACK-STANDARD-FACELIFT-02	MEDIUM	Facelift exterior branch; this Ktype also covers the pre-facelift branch.	READY
33837	33837	Hatchback	206+			EU-PEUGEOT-206-PLUS-HATCHBACK-STANDARD-01	HIGH		READY
33839	33839	Hatchback	206+			EU-PEUGEOT-206-PLUS-HATCHBACK-STANDARD-01	HIGH		READY
33838	33838	Hatchback	206+			EU-PEUGEOT-206-PLUS-HATCHBACK-STANDARD-01	HIGH		READY
52008	52008	Wagon	I		5	EU-PEUGEOT-207-I-WAGON-FACELIFT-01	HIGH		READY
110730_prefl	110730	Wagon	I		5	EU-PEUGEOT-207-I-WAGON-PREFL-01	MEDIUM	Pre-facelift exterior branch; this Ktype also covers the facelift branch.	READY
110730_facelift	110730	Wagon	I		5	EU-PEUGEOT-207-I-WAGON-FACELIFT-01	MEDIUM	Facelift exterior branch; this Ktype also covers the pre-facelift branch.	READY
13008_prefl	13008	Hatchback	I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift exterior branch; this Ktype also covers the facelift branch.	READY
13008_facelift	13008	Hatchback	I			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	Facelift exterior branch; this Ktype also covers the pre-facelift branch.	READY
58565_prefl	58565	Hatchback	I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift exterior branch; this Ktype also covers the facelift branch.	READY
58565_facelift	58565	Hatchback	I			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	Facelift exterior branch; this Ktype also covers the pre-facelift branch.	READY
58571	58571	Hatchback	I			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	HIGH		READY
33804	33804	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
107418	107418	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
33807	33807	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
117338	117338	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
33823	33823	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
111924	111924	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
109333	109333	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
117336	117336	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
107419	107419	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
33929	33929	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	HIGH		READY
122065	122065	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	MEDIUM	Assigned to the facelift envelope at the 2015 model transition.	READY
126685	126685	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH		READY
112328	112328	Hatchback	I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	MEDIUM	THP 165 variant assigned to the facelift envelope.	READY
58650	58650	Hatchback	I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-PREFL-01	HIGH		READY
108642	108642	Hatchback	I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-PREFL-01	HIGH		READY
155683	155683	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
156286	156286	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
801859	801859	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
144436	144436	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
144371	144371	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
144434	144434	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
151535	151535	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
802032	802032	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
801562	801562	Hatchback	II	P21	5	EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	HIGH		READY
111987	111987	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
107941	107941	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
33866	33866	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
58880	58880	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
106340	106340	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
59322	59322	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
53215	53215	MPV	I		5	EU-PEUGEOT-3008-I-MPV-STANDARD-01	HIGH		READY
154451	154451	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
121650	121650	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
126187	126187	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
126188	126188	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
121646	121646	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
121649	121649	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
126189	126189	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
121648	121648	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
121173	121173	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
151468	151468	SUV	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	HIGH		READY
156879	156879	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
800996	800996	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
802056	802056	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
156880	156880	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
801561	801561	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
800059	800059	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
803433	803433	SUV	III		5	EU-PEUGEOT-3008-III-SUV-STANDARD-01	HIGH		READY
142647	142647	Van	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	MEDIUM	Commercial conversion retains the 3008 II SUV exterior envelope.	READY
142648	142648	Van	II		5	EU-PEUGEOT-3008-II-SUV-STANDARD-01	MEDIUM	Commercial conversion retains the 3008 II SUV exterior envelope.	READY
```

[Ktype 映射表下载](sandbox:/mnt/data/left18448_13001-13100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-5008-I-MPV-STANDARD-01	4529	1837	1639	Automobile-Catalog (2013 Peugeot 5008 1.6 HDi 115)	https://www.automobile-catalog.com/car/2013/2626250/peugeot_5008_1_6_hdi_115.html
EU-PEUGEOT-5008-III-SUV-STANDARD-01	4791	1895	1694	Peugeot official (New Peugeot 5008 Hybrid exterior dimensions)	https://www.peugeot.ie/our-models/new-peugeot-5008/hybrid.html
EU-PEUGEOT-106-II-HATCHBACK-STANDARD-01	3678	1588	1376	Automobile-Catalog (2000 Peugeot 106 1.5 D Style)	https://www.automobile-catalog.com/car/2000/2609930/peugeot_106_1_5_d_style.html
EU-PEUGEOT-106-II-VAN-ELECTRIC-01	3678	1594	1380	Automobile-Catalog (1998 Peugeot 106 Electric)	https://www.automobile-catalog.com/car/1998/2609645/peugeot_106_electric_electrique.html
EU-PEUGEOT-2008-I-SUV-STANDARD-01	4159	1739	1556	Automobile-Catalog (2014 Peugeot 2008 1.2 VTi 82)	https://www.automobile-catalog.com/car/2014/2627210/peugeot_2008_1_2_vti_82.html
EU-PEUGEOT-2008-II-SUV-PREFL-01	4300	1770	1550	Peugeot UK technical specification (December 2020, mirrored transcription)	https://www.readkong.com/page/all-new-peugeot-2008-equipment-and-technical-specifications-7295933
EU-PEUGEOT-2008-II-SUV-FACELIFT-01	4304	1770	1550	AutomobileDimension (Peugeot 2008 2023)	https://www.automobiledimension.com/model/peugeot/2008
EU-PEUGEOT-205-II-HATCHBACK-GTX-01	3705	1572	1365	Automobile-Catalog (1987 Peugeot 205 XT/GT three-door body)	https://www.automobile-catalog.com/car/1987/2574875/peugeot_205_xt_gt.html
EU-PEUGEOT-206-I-CONVERTIBLE-CC-01	3835	1673	1373	Automobile-Catalog (2006 Peugeot 206 CC 2.0 16V 135)	https://www.automobile-catalog.com/car/2006/2616275/peugeot_206_cc_2_0_16v_135.html
EU-PEUGEOT-206-I-WAGON-STANDARD-01	4028	1652	1460	Automobile-Catalog (2002 Peugeot 206 SW 1.4 75)	https://www.automobile-catalog.com/car/2002/2615675/peugeot_206_sw_1_4_75.html
EU-PEUGEOT-206-I-HATCHBACK-STANDARD-PREFL-02	3835	1652	1432	Auto-Data (Peugeot 206 1.6i 88)	https://www.auto-data.net/en/peugeot-206-1.6i-88hp-5252
EU-PEUGEOT-206-I-HATCHBACK-STANDARD-FACELIFT-02	3822	1652	1425	Automobile-Catalog (2004 Peugeot 206 1.4 75)	https://www.automobile-catalog.com/car/2004/2615915/peugeot_206_1_4_75.html
EU-PEUGEOT-206-PLUS-HATCHBACK-STANDARD-01	3872	1655	1446	Automobile-Catalog (2009 Peugeot 206+ 1.4 HDi 70)	https://www.automobile-catalog.com/car/2009/2616365/peugeot_206_1_4_hdi_70.html
EU-PEUGEOT-207-I-WAGON-PREFL-01	4156	1748	1510	Automobile-Catalog (2009 Peugeot 207 SW 1.4 75, up to June 2009)	https://www.automobile-catalog.com/car/2009/2620505/peugeot_207_sw_1_4_75.html
EU-PEUGEOT-207-I-WAGON-FACELIFT-01	4164	1748	1510	Automobile-Catalog (2009 Peugeot 207 SW 1.4 75, since July 2009)	https://www.automobile-catalog.com/car/2009/2620820/peugeot_207_sw_1_4_75.html
EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	4030	1748	1472	Automobile-Catalog (2009 Peugeot 207 1.4 75, up to June 2009)	https://www.automobile-catalog.com/car/2009/2620310/peugeot_207_1_4_75.html
EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	4045	1748	1472	Automobile-Catalog (2009 Peugeot 207 1.4 75, since July 2009)	https://www.automobile-catalog.com/car/2009/2620670/peugeot_207_1_4_75.html
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-PREFL-01	3962	1739	1460	Automobile-Catalog (2012 Peugeot 208 1.2 VTi 82)	https://www.automobile-catalog.com/car/2012/2623505/peugeot_208_1_2_vti_82.html
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460	Automobile-Catalog (2015 Peugeot 208 1.2 PureTech 110)	https://www.automobile-catalog.com/car/2015/2623805/peugeot_208_1_2_puretech_110.html
EU-PEUGEOT-208-I-A9-HATCHBACK-3D-PREFL-01	3962	1739	1460	Automobile-Catalog (2013 Peugeot 208 GTi)	https://www.automobile-catalog.com/car/2013/2623670/peugeot_208_gti.html
EU-PEUGEOT-208-II-P21-HATCHBACK-5D-STANDARD-01	4055	1745	1430	Peugeot official 208 technical specification PDF	https://ksa.peugeot.com/content/dam/peugeot/master/b2c/our-range/e-208---208/document/208-21C.pdf
EU-PEUGEOT-3008-I-MPV-STANDARD-01	4365	1837	1639	Auto-Data (Peugeot 3008 I 1.6 HDi 112)	https://www.auto-data.net/en/peugeot-3008-i-phase-i-2009-1.6-hdi-112hp-16700
EU-PEUGEOT-3008-II-SUV-STANDARD-01	4447	1841	1624	Auto-Data (Peugeot 3008 II phase I generation)	https://www.auto-data.net/en/peugeot-3008-ii-phase-i-2016-generation-4862
EU-PEUGEOT-3008-III-SUV-STANDARD-01	4542	1895	1641	Peugeot official (All-new 3008 exterior dimensions)	https://oman.peugeot.com/en/our-models/peugeot-3008/all-new.html
```

[DIMENSION_GROUP 尺寸表下载](sandbox:/mnt/data/left18448_13001-13100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2009/2620670/peugeot_207_1_4_75.html?utm_source=chatgpt.com "2009 Peugeot 207 1.4 75 Specs Review (54 kW / 73 PS / 72 hp) (since July 2009 for Europe )"
[2]: https://oman.peugeot.com/en/our-models/peugeot-3008/all-new.html "Peugeot 3008 (2025): Explore the New Modern SUV and Specs"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4657 行）
- 累计尺寸组：dimension_groups_final.tsv（1278 行）

