# 任务：left18448 第 4501-4600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0046__8e98c739


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4501-4600 行

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
left18448 第 4501-4600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4501-4600_ktype_dimension_mapping_final.tsv
- left18448_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	3948	1715	1483
EU-DS-DS3-A55-HATCHBACK-STANDARD-01	3948	1715	1458
EU-DS-DS3-D34-HATCHBACK-STANDARD-01	4118	1791	1534

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
DS	Ds	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jul 2015	Jul 2019	118007
DS	Ds	1.6 Bluehdi 120	Cabriolet	Frontantrieb	Diesel	Jul 2015	Jul 2019	118011
DS	Ds	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jul 2015	Dec 2018	118015
DS	Ds	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jun 2015	Dec 2018	118606
DS	Ds	1.6 Bluehdi 75	Schrägheck	Frontantrieb	Diesel	Jul 2015	Jul 2019	118602
DS	Ds	1.6 E-hdi	Schrägheck	Frontantrieb	Diesel	Jun 2015	Dec 2018	802236
DS	Ds	1.6 E-tense 225	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2020	Jun 2022	144486
DS	Ds	1.6 E-tense 250	Stufenheck	Frontantrieb	Benzin/Elektro	Aug 2022	Aug 2024	149810
DS	Ds	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Jul 2015	Jul 2019	118005
DS	Ds	1.6 THP 165	Cabriolet	Frontantrieb	Benzin	Jul 2015	Jul 2019	118009
DS	Ds	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Jul 2015	Dec 2018	118013
DS	Ds	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Jul 2015	Dec 2018	118607
DS	Ds	1.6 THP 208	Schrägheck	Frontantrieb	Benzin	Sep 2015	Jul 2019	118603
DS	Ds	1.6 THP 208	Cabriolet	Frontantrieb	Benzin	Sep 2015	Jul 2019	118604
DS	Ds	1.6 THP 210	Schrägheck	Frontantrieb	Benzin	Jul 2015	Dec 2018	118014
DS	Ds	1.6 THP 210	Schrägheck	Frontantrieb	Benzin	Apr 2015	Dec 2018	118018
DS	Ds	2.0 Bluehdi 150	Schrägheck	Frontantrieb	Diesel	Jul 2015	Dec 2018	118016
DS	Ds	2.0 Bluehdi 150	Schrägheck	Frontantrieb	Diesel	Apr 2015	Dec 2018	118019
DS	Ds	2.0 Bluehdi 180	Schrägheck	Frontantrieb	Diesel	Jul 2015	Dec 2018	118017
DS	Ds	2.0 Bluehdi 180	Schrägheck	Frontantrieb	Diesel	Apr 2015	Dec 2018	118020
DS	Ds	Bluehdi 130	Schrägheck	Frontantrieb	Diesel	Oct 2021	Aug 2025	144481
DS	Ds	Bluehdi 130	SUV	Frontantrieb	Diesel	Sep 2022	-	149699
DS	Ds	E-tense	Schrägheck	Frontantrieb	Elektro	Jan 2023	-	151534
DS	Ds	E-tense 225	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2021	Aug 2025	144484
DS	Ds	E-tense 225	SUV	Frontantrieb	Benzin/Elektro	Sep 2020	-	145318
DS	Ds	E-tense 225	SUV	Frontantrieb	Benzin/Elektro	Sep 2022	-	149701
DS	Ds	E-tense 360 4X4	Stufenheck	Allrad	Benzin/Elektro	Jun 2021	Aug 2024	145080
DS	Ds	E-tense 4X4 300	SUV	Allrad	Benzin/Elektro	Sep 2022	-	149703
DS	Ds	E-tense 4X4 360	SUV	Allrad	Benzin/Elektro	Sep 2022	-	149707
DS	Ds	Hybrid 136	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	Apr 2025	158771
DS	Ds	Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	Aug 2025	801884
DS	Ds	Puretech 130	Schrägheck	Frontantrieb	Benzin	Oct 2021	Dec 2024	144480
DS	Ds	Puretech 180	Schrägheck	Frontantrieb	Benzin	Oct 2021	Oct 2022	144482
DS	Ds	Puretech 180	SUV	Frontantrieb	Benzin	Sep 2022	-	151266
DS	Ds	Puretech 225	Schrägheck	Frontantrieb	Benzin	Oct 2021	Aug 2022	144483
DS	Ds	Puretech 225	SUV	Frontantrieb	Benzin	Sep 2022	-	151267
DS	N°4	1.2 Hybrid 145	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2025	-	161783
DS	N°4	1.5 Bluehdi 130	Schrägheck	Frontantrieb	Diesel	Dec 2025	-	163101
DS	N°4	1.6 Plug-in-hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2025	-	161782
DS	N°4	1.6 Plug-in-hybrid 240	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2026	-	164015
DS	N°4	E-tense 213	Schrägheck	Frontantrieb	Elektro	Jun 2025	-	161779
DS	N°7	E-tense FWD	SUV	Frontantrieb	Elektro	Feb 2026	-	164728
DS	N°8	74	Coupe	Frontantrieb	Elektro	Feb 2025	-	160379
DS	N°8	97 Long Range	Coupe	Frontantrieb	Elektro	Feb 2025	-	160377
DS	N°8	97 Long Range 4X4	Coupe	Allrad	Elektro	Feb 2025	-	160378
DSK	Q51	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	May 2024	-	160127
DSK	Q51	1.6 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	May 2024	-	160131
DSK	Q51	1.6 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	May 2024	-	160130
E.go	E.wave x	Electric	Schrägheck	Heckantrieb	Elektro	Feb 2023	-	151938
Ebro	S400	1.5 HEV	SUV	Frontantrieb	Benzin/Elektro	Jun 2025	-	161970
Ebro	S700	1.5 T-gdi Phev	SUV	Frontantrieb	Benzin/Elektro	Jan 2026	-	163773
Elaris	Beo	EV	SUV	Frontantrieb	Elektro	Jul 2021	-	145683
Elaris	Caro	EV	Kasten	Heckantrieb	Elektro	Nov 2022	-	157418
Elaris	Dyo	EV	Schrägheck	Frontantrieb	Elektro	Mar 2023	-	152750
Elaris	Finn	EV	Schrägheck	Frontantrieb	Elektro	Jan 2020	-	144010
Elaris	Leo	EV	SUV	Frontantrieb	Elektro	Jan 2020	-	144149
Elaris	Pio	EV	Schrägheck	Frontantrieb	Elektro	Jul 2021	-	146574
EMC	4	1.5	SUV	Frontantrieb	Benzin	Nov 2024	-	161217
EMC	4	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2024	-	161223
EMC	6	1.5	SUV	Frontantrieb	Benzin	Nov 2024	-	161000
EMC	6	1.5	SUV	Frontantrieb	Benzin	Nov 2024	-	161003
EMC	6	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2024	-	160993
EMC	6	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2024	-	161001
EMC	7	1.5	SUV	Frontantrieb	Benzin	Nov 2024	-	161194
EMC	212	2.0 4X4	SUV	Allrad	Benzin	Aug 2025	-	162303
EMC	212	2.0 4X4	SUV	Allrad	Diesel	Mar 2026	-	164646
EMC	Wave 3	1.5	SUV	Frontantrieb	Benzin	Jul 2022	-	156018
EMC	Wave 3	1.5	SUV	Frontantrieb	Benzin	Jul 2022	-	156020
EMC	Wave 3	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2022	-	156019
EMC	Wave 3	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2022	-	156021
EMC	Yudo	EV	SUV	Frontantrieb	Elektro	May 2024	-	160989
EMW	340	340	Stufenheck	Heckantrieb	Benzin	Jul 1952	Dec 1955	155163
EON Motors	Weez	EV	Schrägheck	Allrad	Elektro	Oct 2022	-	160494
EVO	Cross 4	TDI 4WD	Pick-up	Allrad	Diesel	Dec 2022	-	154759
EVO	Cuatro	1.5	SUV	Frontantrieb	Benzin	Oct 2025	-	162708
EVO	Cuatro	1.5	SUV	Frontantrieb	Benzin	Jan 2026	-	164287
EVO	Cuatro	1.5	SUV	Frontantrieb	Benzin	Jan 2026	-	164520
EVO	Cuatro	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Oct 2025	-	162709
EVO	Cuatro	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2026	-	164289
EVO	Evo 3	1.5	Schrägheck	Frontantrieb	Benzin	Apr 2023	-	154750
EVO	Evo 3	1.5 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Apr 2023	-	154748
EVO	Evo 4	1.6	SUV	Frontantrieb	Benzin	Jul 2022	-	154752
EVO	Evo 4	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2022	-	154751
EVO	Evo 5	1.5	SUV	Frontantrieb	Benzin	Apr 2023	-	154758
EVO	Evo 5	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2023	-	154757
EVO	Evo 6	1.5 GPL Turbo	SUV	Frontantrieb	Benzin/Autogas (LPG)	Oct 2024	-	160244
EVO	Evo 6	1.5 Turbo	SUV	Frontantrieb	Benzin	Oct 2024	-	160245
EVO	Evo 7	1.5	SUV	Frontantrieb	Benzin	Oct 2023	-	156348
EVO	Evo 7	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Mar 2024	-	158114
EVO	Spazio	1.5	Großraumlimousine	Frontantrieb	Benzin	Sep 2025	-	164246
EVO	Spazio	1.5 GPL	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Sep 2025	-	164247
Evum Motors	Acar	Electric	Pritsche/Fahrgestell	Allrad	Elektro	Jun 2020	-	152857
Exlantix	Es	BEV	Stufenheck	Heckantrieb	Elektro	Jan 2026	-	163775
Exlantix	Es	BEV AWD	Stufenheck	Allrad	Elektro	Oct 2026	-	162614
Exlantix	Et	BEV	SUV	Heckantrieb	Elektro	Jan 2026	-	163776
Exlantix	Et	BEV AWD	SUV	Allrad	Elektro	Oct 2026	-	162615
Faam	Ecomile	CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Jan 2010	Dec 2012	801724
Faam	Ecomile	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2010	Dec 2012	801720
Faam	Ecomile	LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2010	Dec 2012	801723
Faam	Jolly 2000	CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Jan 2010	Dec 2012	801736


--- Round 1 / 首次发送 ---
## 更新点

本批次已完成。动力、能源及普通配置差异均按物理外廓合并；DS 4 II 与外廓相同的 N°4 复用同一尺寸组；DS 7 改款前后因三维变化分别建组。

## 进度

输入 Ktype：100
READY：100
PENDING：0
DIMENSION_GROUP：40
引用闭合：是
孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
118007	118007	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118011	118011	Convertible	DS 3 Cabrio I facelift	A55	2	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
118015	118015	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118606	118606	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118602	118602	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
802236	802236	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
144486	144486	Sedan	DS 9 I		4	EU-DS-DS9-GEN1-SEDAN-STANDARD-01	HIGH		READY
149810	149810	Sedan	DS 9 I		4	EU-DS-DS9-GEN1-SEDAN-STANDARD-01	HIGH		READY
118005	118005	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118009	118009	Convertible	DS 3 Cabrio I facelift	A55	2	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
118013	118013	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118607	118607	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118603	118603	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118604	118604	Convertible	DS 3 Cabrio I facelift	A55	2	EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	HIGH		READY
118014	118014	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118018	118018	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118016	118016	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118019	118019	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118017	118017	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
118020	118020	Hatchback	DS 3 I facelift	A55	3	EU-DS-DS3-A55-HATCHBACK-STANDARD-01	HIGH		READY
144481	144481	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
149699	149699	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
151534	151534	Hatchback	DS 3 II facelift	D34	5	EU-DS-DS3-D34-HATCHBACK-STANDARD-01	HIGH		READY
144484	144484	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
145318	145318	SUV	DS 7 I pre-facelift		5	EU-DS-DS7-GEN1-SUV-PREFACELIFT-01	HIGH		READY
149701	149701	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
145080	145080	Sedan	DS 9 I		4	EU-DS-DS9-GEN1-SEDAN-STANDARD-01	HIGH		READY
149703	149703	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
149707	149707	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
158771	158771	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
801884	801884	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
144480	144480	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
144482	144482	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
151266	151266	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
144483	144483	Hatchback	DS 4 II		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
151267	151267	SUV	DS 7 I facelift		5	EU-DS-DS7-GEN1-SUV-FACELIFT-01	HIGH		READY
161783	161783	Hatchback	DS 4 II facelift / N°4		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
163101	163101	Hatchback	DS 4 II facelift / N°4		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
161782	161782	Hatchback	DS 4 II facelift / N°4		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
164015	164015	Hatchback	DS 4 II facelift / N°4		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
161779	161779	Hatchback	DS 4 II facelift / N°4		5	EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	HIGH		READY
164728	164728	SUV	DS N°7 I		5	EU-DS-N7-GEN1-SUV-STANDARD-01	HIGH		READY
160379	160379	Coupe	DS N°8 I		5	EU-DS-N8-GEN1-COUPE-STANDARD-01	HIGH		READY
160377	160377	Coupe	DS N°8 I		5	EU-DS-N8-GEN1-COUPE-STANDARD-01	HIGH		READY
160378	160378	Coupe	DS N°8 I		5	EU-DS-N8-GEN1-COUPE-STANDARD-01	HIGH		READY
160127	160127	Pickup	Q51 I		2	EU-DSK-Q51-GEN1-PICKUP-STANDARD-01	MEDIUM		READY
160131	160131	Pickup	Q51 I		2	EU-DSK-Q51-GEN1-PICKUP-STANDARD-01	MEDIUM		READY
160130	160130	Pickup	Q51 I		2	EU-DSK-Q51-GEN1-PICKUP-STANDARD-01	MEDIUM		READY
151938	151938	Hatchback	e.wave X I		3	EU-EGO-EWAVEX-GEN1-HATCHBACK-STANDARD-01	MEDIUM		READY
161970	161970	SUV	S400 I		5	EU-EBRO-S400-GEN1-SUV-STANDARD-01	HIGH		READY
163773	163773	SUV	S700 I		5	EU-EBRO-S700-GEN1-SUV-STANDARD-01	HIGH		READY
145683	145683	SUV	Beo I		5	EU-ELARIS-BEO-GEN1-SUV-STANDARD-01	HIGH		READY
157418	157418	Van	Caro I			EU-ELARIS-CARO-GEN1-VAN-STANDARD-01	MEDIUM		READY
152750	152750	Hatchback	Dyo I		3	EU-ELARIS-DYO-GEN1-HATCHBACK-STANDARD-01	HIGH		READY
144010	144010	Hatchback	Finn I		3	EU-ELARIS-FINN-GEN1-HATCHBACK-STANDARD-01	HIGH		READY
144149	144149	SUV	Leo		5	EU-ELARIS-LEO-GEN1-SUV-STANDARD-01	MEDIUM		READY
146574	146574	Hatchback	Pio I		3	EU-ELARIS-PIO-GEN1-HATCHBACK-STANDARD-01	MEDIUM		READY
161217	161217	SUV	EMC 4 I		5	EU-EMC-4-GEN1-SUV-STANDARD-01	HIGH		READY
161223	161223	SUV	EMC 4 I		5	EU-EMC-4-GEN1-SUV-STANDARD-01	HIGH		READY
161000	161000	SUV	EMC 6 I (2024)		5	EU-EMC-6-GEN1-SUV-2024-01	MEDIUM	按2024版 EMC 6 SEI 外廓归组	READY
161003	161003	SUV	EMC 6 I (2024)		5	EU-EMC-6-GEN1-SUV-2024-01	MEDIUM	按2024版 EMC 6 SEI 外廓归组	READY
160993	160993	SUV	EMC 6 I (2024)		5	EU-EMC-6-GEN1-SUV-2024-01	MEDIUM	按2024版 EMC 6 SEI 外廓归组	READY
161001	161001	SUV	EMC 6 I (2024)		5	EU-EMC-6-GEN1-SUV-2024-01	MEDIUM	按2024版 EMC 6 SEI 外廓归组	READY
161194	161194	SUV	EMC 7 I		5	EU-EMC-7-GEN1-SUV-STANDARD-01	HIGH		READY
162303	162303	SUV	EMC 212 I		5	EU-EMC-212-GEN1-SUV-STANDARD-01	HIGH		READY
164646	164646	SUV	EMC 212 I		5	EU-EMC-212-GEN1-SUV-STANDARD-01	HIGH		READY
156018	156018	SUV	Wave 3 I		5	EU-EMC-WAVE3-GEN1-SUV-STANDARD-01	HIGH		READY
156020	156020	SUV	Wave 3 I		5	EU-EMC-WAVE3-GEN1-SUV-STANDARD-01	HIGH		READY
156019	156019	SUV	Wave 3 I		5	EU-EMC-WAVE3-GEN1-SUV-STANDARD-01	HIGH		READY
156021	156021	SUV	Wave 3 I		5	EU-EMC-WAVE3-GEN1-SUV-STANDARD-01	HIGH		READY
160989	160989	SUV	Yudo I		5	EU-EMC-YUDO-GEN1-SUV-STANDARD-01	HIGH		READY
155163	155163	Sedan	340 I		4	EU-EMW-340-GEN1-SEDAN-STANDARD-01	MEDIUM		READY
160494	160494	Hatchback	Weez I			EU-EON-WEEZ-GEN1-HATCHBACK-CITYPRO-01	MEDIUM		READY
154759	154759	Pickup	Cross 4 I		4	EU-EVO-CROSS4-GEN1-PICKUP-DOUBLECAB-01	HIGH		READY
162708	162708	SUV	Cuatro I		5	EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	HIGH		READY
164287	164287	SUV	Cuatro I		5	EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	HIGH		READY
164520	164520	SUV	Cuatro I		5	EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	HIGH		READY
162709	162709	SUV	Cuatro I		5	EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	HIGH		READY
164289	164289	SUV	Cuatro I		5	EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	HIGH		READY
154750	154750	Hatchback	Evo 3 I		5	EU-EVO-EVO3-GEN1-HATCHBACK-STANDARD-01	HIGH		READY
154748	154748	Hatchback	Evo 3 I		5	EU-EVO-EVO3-GEN1-HATCHBACK-STANDARD-01	HIGH		READY
154752	154752	SUV	Evo 4 I		5	EU-EVO-EVO4-GEN1-SUV-STANDARD-01	HIGH		READY
154751	154751	SUV	Evo 4 I		5	EU-EVO-EVO4-GEN1-SUV-STANDARD-01	HIGH		READY
154758	154758	SUV	Evo 5 I		5	EU-EVO-EVO5-GEN1-SUV-STANDARD-01	HIGH		READY
154757	154757	SUV	Evo 5 I		5	EU-EVO-EVO5-GEN1-SUV-STANDARD-01	HIGH		READY
160244	160244	SUV	Evo 6 I		5	EU-EVO-EVO6-GEN1-SUV-STANDARD-01	HIGH		READY
160245	160245	SUV	Evo 6 I		5	EU-EVO-EVO6-GEN1-SUV-STANDARD-01	HIGH		READY
156348	156348	SUV	Evo 7 I		5	EU-EVO-EVO7-GEN1-SUV-STANDARD-01	HIGH		READY
158114	158114	SUV	Evo 7 I		5	EU-EVO-EVO7-GEN1-SUV-STANDARD-01	HIGH		READY
164246	164246	MPV	Spazio I		5	EU-EVO-SPAZIO-GEN1-MPV-STANDARD-01	HIGH		READY
164247	164247	MPV	Spazio I		5	EU-EVO-SPAZIO-GEN1-MPV-STANDARD-01	HIGH		READY
152857	152857	Pickup	aCar I		2	EU-EVUM-ACAR-GEN1-PICKUP-STANDARD-01	MEDIUM	按2020首发标准平台外廓归组	READY
163775	163775	Sedan	Exlantix ES I		4	EU-EXLANTIX-ES-GEN1-SEDAN-STANDARD-01	MEDIUM		READY
162614	162614	Sedan	Exlantix ES I		4	EU-EXLANTIX-ES-GEN1-SEDAN-STANDARD-01	MEDIUM		READY
163776	163776	SUV	Exlantix ET I		5	EU-EXLANTIX-ET-GEN1-SUV-STANDARD-01	MEDIUM		READY
162615	162615	SUV	Exlantix ET I		5	EU-EXLANTIX-ET-GEN1-SUV-STANDARD-01	MEDIUM		READY
801724	801724	Pickup	Ecomile I		2	EU-FAAM-ECOMILE-GEN1-PICKUP-STANDARD-01	LOW	按 Ecomile 的 Daihatsu Zebra 标准皮卡车身归组	READY
801720	801720	Pickup	Ecomile I		2	EU-FAAM-ECOMILE-GEN1-PICKUP-STANDARD-01	LOW	按 Ecomile 的 Daihatsu Zebra 标准皮卡车身归组	READY
801723	801723	Pickup	Ecomile I		2	EU-FAAM-ECOMILE-GEN1-PICKUP-STANDARD-01	LOW	按 Ecomile 的 Daihatsu Zebra 标准皮卡车身归组	READY
801736	801736	Pickup	Jolly 2000 I		2	EU-FAAM-JOLLY2000-GEN1-PICKUP-STANDARD-01	LOW	采用标准底盘外廓；未采用可变上装最大高度	READY
```

[下载 left18448_4501-4600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_4501-4600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DS-DS3-A55-CONVERTIBLE-STANDARD-01	3948	1715	1483	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2227655/ds_3_cabrio_bluehdi_120.html
EU-DS-DS3-A55-HATCHBACK-STANDARD-01	3948	1715	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2227520/ds_3_thp_165.html
EU-DS-DS3-D34-HATCHBACK-STANDARD-01	4118	1791	1534	DS Automobiles / Stellantis official technical data	https://www.media.stellantis.com/uk-en/ds/press/ds-3-crossback-icon-of-high-tech-style
EU-DS-DS4-GEN2-HATCHBACK-STANDARD-01	4400	1830	1470	DS Automobiles official N°4 specifications	https://www.dsautomobiles.co.uk/models/dsn4/e-tense.html
EU-DS-DS9-GEN1-SEDAN-STANDARD-01	4930	1930	1460	DS Automobiles / Stellantis official technical data	https://www.media.stellantis.com/em-en/ds/press/ds-9-the-power-of-elegance-1632575108-1619424000
EU-DS-DS7-GEN1-SUV-PREFACELIFT-01	4570	1890	1620	DS Automobiles / Stellantis official technical data	https://www.media.stellantis.com/uk-en/ds/press/ds-7-crossback-the-first-new-generation-ds
EU-DS-DS7-GEN1-SUV-FACELIFT-01	4595	1906	1620	DS Automobiles / Stellantis official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds7priceandspecificationguidejuly2023-650ad2f64b001.pdf
EU-DS-N7-GEN1-SUV-STANDARD-01	4660	1900	1630	DS Automobiles / Stellantis official technical data	https://www.media.stellantis.com/uk-en/ds/press/ds-n07-first-class-suv
EU-DS-N8-GEN1-COUPE-STANDARD-01	4820	1900	1580	DS Automobiles / Stellantis official technical data	https://www.media.stellantis.com/em-en/ds/press/ds-n08-the-electric-journey-starts-now
EU-DSK-Q51-GEN1-PICKUP-STANDARD-01	5555	1830	2055	DFSK Q51 dealer technical sheet	https://grupomamsa.com/descubre-el-nuevo-q51-dfsk/
EU-EGO-EWAVEX-GEN1-HATCHBACK-STANDARD-01	3360	1814	1638	UltimateSpecs	https://www.ultimatespecs.com/car-specs/eGO-Mobile/133505/eGO-Mobile-ewave-X-30kWh.html
EU-EBRO-S400-GEN1-SUV-STANDARD-01	4320	1831	1646	EBRO official specifications	https://www.ebroauto.com/modelos/s400-hev/especificaciones
EU-EBRO-S700-GEN1-SUV-STANDARD-01	4553	1862	1696	Auto-Data	https://www.auto-data.net/en/ebro-s700-1.5-tgdi-279hp-plug-in-hybrid-dht-54949
EU-ELARIS-BEO-GEN1-SUV-STANDARD-01	4698	1908	1696	Auto-Data	https://www.auto-data.net/en/elaris-beo-86-kwh-204hp-50300
EU-ELARIS-CARO-GEN1-VAN-STANDARD-01	5915	2040	2632	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Elaris/138571/Elaris-Caro-Caro-875-kWh.html
EU-ELARIS-DYO-GEN1-HATCHBACK-STANDARD-01	2871	1563	1568	Auto-Data	https://www.auto-data.net/en/elaris-dyo-30-kwh-48hp-50308
EU-ELARIS-FINN-GEN1-HATCHBACK-STANDARD-01	2871	1563	1568	Auto-Data	https://www.auto-data.net/en/elaris-finn-31.5-kwh-48hp-50309
EU-ELARIS-LEO-GEN1-SUV-STANDARD-01	4602	1900	1645	Auto-Data	https://www.auto-data.net/en/elaris-leo-ii-64.6-kwh-184hp-50311
EU-ELARIS-PIO-GEN1-HATCHBACK-STANDARD-01	2811	1540	1555	EngineInDetail	https://www.engineindetail.com/pae/elaris-pio-2021
EU-EMC-4-GEN1-SUV-STANDARD-01	4005	1760	1575	EMC official specifications	https://emcauto.it/veicoli/emc-quattro/
EU-EMC-6-GEN1-SUV-2024-01	4440	1831	1665	Auto-Data	https://www.auto-data.net/en/emc-6-sei-1.5-113hp-55784
EU-EMC-7-GEN1-SUV-STANDARD-01	4535	1845	1725	EMC official specifications	https://emcauto.it/veicoli/emc-sette/
EU-EMC-212-GEN1-SUV-STANDARD-01	4705	1895	1936	EMC official specifications	https://emcauto.it/veicoli/emc-212/
EU-EMC-WAVE3-GEN1-SUV-STANDARD-01	4440	1831	1665	Jolly Auto Wave 3 technical data	https://www.jollyauto.com/wave3/
EU-EMC-YUDO-GEN1-SUV-STANDARD-01	4035	1736	1625	Auto-Data	https://www.auto-data.net/en/emc-yudo-41.7-kwh-95hp-55800
EU-EMW-340-GEN1-SEDAN-STANDARD-01	4600	1765	1630	Carfolio	https://www.carfolio.com/emw-340-360800
EU-EON-WEEZ-GEN1-HATCHBACK-CITYPRO-01	3000	1500	1660	L'Argus	https://www.largus.fr/actualite-automobile/essai-eon-weez-city-pro-le-livreur-urbain-avec-un-moteur-electrique-par-roue-30026112.html
EU-EVO-CROSS4-GEN1-PICKUP-DOUBLECAB-01	5315	1880	1830	EVO official specifications	https://www.auto-evo.com/modello/evo-cross-4/
EU-EVO-CUATRO-GEN1-SUV-STANDARD-01	4400	1831	1653	Auto-Data	https://www.auto-data.net/en/evo-cuatro-1.5l-117hp-55509
EU-EVO-EVO3-GEN1-HATCHBACK-STANDARD-01	4135	1750	1568	EVO official specifications	https://www.auto-evo.com/modello/evo3/
EU-EVO-EVO4-GEN1-SUV-STANDARD-01	4325	1765	1640	EVO official specifications	https://www.auto-evo.eu/modello/evo-4-4/
EU-EVO-EVO5-GEN1-SUV-STANDARD-01	4325	1815	1640	EVO official specifications	https://www.auto-evo.com/modello/evo-5-4/
EU-EVO-EVO6-GEN1-SUV-STANDARD-01	4565	1860	1690	EVO official specifications	https://www.auto-evo.com/modello/evo-6-benzina/
EU-EVO-EVO7-GEN1-SUV-STANDARD-01	4795	1870	1758	EVO official specifications	https://www.auto-evo.eu/modello/evo-7-3/
EU-EVO-SPAZIO-GEN1-MPV-STANDARD-01	4850	1900	1715	EVO official specifications	https://www.auto-evo.com/modello/evo-spazio-ita-bz/
EU-EVUM-ACAR-GEN1-PICKUP-STANDARD-01	4000	1500	2000	Engineering for Change product profile	https://www.engineeringforchange.org/solutions/product/evum-acar/
EU-EXLANTIX-ES-GEN1-SEDAN-STANDARD-01	4945	1978	1480	Segmenty automotive technical report	https://segmenty.com/GenerateNewsStaticJsps/Exeed_Exlantix_ES_enters_local_market.html
EU-EXLANTIX-ET-GEN1-SUV-STANDARD-01	4955	1975	1698	CarNewsChina technical report	https://carnewschina.com/2023/10/16/cherys-exeed-exlantix-et-is-li-auto-l7-for-the-overseas-markets/
EU-FAAM-ECOMILE-GEN1-PICKUP-STANDARD-01	3915	1560	1825	Daihatsu Zebra model reference (FAAM Ecomile rebadge)	https://en.wikipedia.org/wiki/Daihatsu_Zebra
EU-FAAM-JOLLY2000-GEN1-PICKUP-STANDARD-01	4770	1560	1950	FAAM / i-moving Jolly 2000 chassis technical brochure	https://asset.moto.it/pricelist/auto/74b79c45fa49eb0b32337db2fdabed63/brochure-2016.pdf
```

[下载 left18448_4501-4600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_4501-4600_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5336 行）
- 累计尺寸组：dimension_groups_final.tsv（1559 行）

