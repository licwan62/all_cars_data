# 任务：left18448 第 15401-15500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0155__571ba389


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15401-15500 行

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
left18448 第 15401-15500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15401-15500_ktype_dimension_mapping_final.tsv
- left18448_15401-15500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SKODA-RAPID-GARDE-RAPID-COUPE-STANDARD-01	4200	1610	1380
EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	4483	1706	1461
EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	4304	1706	1459

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Skoda	Rapid	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2019	115185
Skoda	Rapid	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	52392
Skoda	Rapid	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	56167
Skoda	Rapid	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Mar 2022	115180
Skoda	Rapid	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Dec 2019	115184
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2012	Dec 2019	39271
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2013	May 2015	52395
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2012	Dec 2019	56170
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2013	May 2015	59062
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2019	115186
Skoda	Rapid	1.6 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Dec 2019	115187
Skoda	Roomster	1.2 TDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2010	May 2015	5950
Skoda	Roomster	1.6 TDI	Kasten/Kombi	Frontantrieb	Diesel	Mar 2010	May 2015	10998
Skoda	Roomster	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2006	May 2006	10996
Skoda	Scala	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2019	-	144116
Skoda	Superb i	1.9 TDI	Stufenheck	Frontantrieb	Diesel	Aug 2002	Oct 2005	17008
Skoda	Superb i	2.5 TDI	Stufenheck	Frontantrieb	Diesel	Jun 2003	Mar 2008	18005
Skoda	Superb i	2.8 V6	Stufenheck	Frontantrieb	Benzin	Jun 2002	Mar 2008	57689
Skoda	Superb ii	1.9 TDI	Kombi	Frontantrieb	Diesel	Oct 2009	Nov 2010	11006
Skoda	Superb ii	2.0 TDI 16V 4X4	Kombi	Allrad	Diesel	Nov 2010	May 2015	10573
Skoda	Superb ii	2.0 TDI 16V 4X4	Schrägheck	Allrad	Diesel	Nov 2010	May 2015	10574
Skoda	Superb iii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Mar 2015	Jun 2024	112398
Skoda	Superb iii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Mar 2015	Jun 2024	113304
Skoda	Superb iii	1.4 TSI	Kombi	Frontantrieb	Benzin	Mar 2015	Jun 2024	115163
Skoda	Superb iii	1.4 TSI	Kombi	Frontantrieb	Benzin	Mar 2015	Jun 2024	115164
Skoda	Superb iii	1.4 TSI 4X4	Kombi	Allrad	Benzin	Mar 2015	Jun 2024	115232
Skoda	Superb iii	1.4 TSI 4X4	Schrägheck	Allrad	Benzin	Mar 2015	Jun 2024	115233
Skoda	Superb iii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2015	Jun 2024	113310
Skoda	Superb iii	1.6 TDI	Kombi	Frontantrieb	Diesel	Mar 2015	Jun 2024	115166
Skoda	Superb iii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	Mar 2015	Jun 2024	115235
Skoda	Superb iii	1.8 TSI	Kombi	Frontantrieb	Benzin	Mar 2015	Jun 2024	115236
Skoda	Superb iii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2015	Jun 2024	112394
Skoda	Superb iii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2015	Jun 2024	112397
Skoda	Superb iii	2.0 TDI	Kombi	Frontantrieb	Diesel	Mar 2015	Jun 2024	115167
Skoda	Superb iii	2.0 TDI	Kombi	Frontantrieb	Diesel	Mar 2015	Jun 2024	115168
Skoda	Superb iii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2020	Jun 2024	142870
Skoda	Superb iii	2.0 TDI	Kombi	Frontantrieb	Diesel	Jul 2020	Jun 2024	142871
Skoda	Superb iii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2024	113313
Skoda	Superb iii	2.0 TDI 4X4	Kombi	Allrad	Diesel	Mar 2015	Jun 2024	115169
Skoda	Superb iii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2024	115237
Skoda	Superb iii	2.0 TDI 4X4	Kombi	Allrad	Diesel	Mar 2015	Jun 2024	115238
Skoda	Superb iii	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Mar 2015	Jun 2024	113308
Skoda	Superb iii	2.0 Tfsi 4X4	Schrägheck	Allrad	Benzin	Mar 2015	Jun 2024	112399
Skoda	Superb iii	2.0 TSI	Kombi	Frontantrieb	Benzin	Mar 2015	Jun 2024	115165
Skoda	Superb iii	2.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2020	Jun 2024	801674
Skoda	Superb iii	2.0 TSI	Kombi	Frontantrieb	Benzin	Nov 2020	Jun 2024	801681
Skoda	Superb iii	2.0 TSI 4X4	Kombi	Allrad	Benzin	Mar 2015	Jun 2024	115239
Skoda	Superb iv	1.5 TSI IV	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2025	-	801378
Skoda	Superb iv	1.5 TSI IV	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2025	-	803388
Skoda	Superb iv	1.5 TSI IV Phev	Kombi	Frontantrieb	Benzin/Elektro	Apr 2024	-	158499
Skoda	Superb iv	1.5 TSI Mhev	Kombi	Frontantrieb	Benzin/Elektro	Nov 2023	-	156862
Skoda	Superb iv	1.5 TSI Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2023	-	157413
Skoda	Superb iv	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2023	-	156864
Skoda	Superb iv	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2023	-	157414
Skoda	Superb iv	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	Mar 2024	-	158105
Skoda	Superb iv	2.0 TDI 4X4	Kombi	Allrad	Diesel	Feb 2024	-	158106
Skoda	Superb iv	2.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2024	-	801044
Skoda	Superb iv	2.0 TSI	Kombi	Frontantrieb	Benzin	Nov 2024	-	801045
Skoda	Superb iv	2.0 TSI 4X4	Kombi	Allrad	Benzin	May 2024	-	158342
Skoda	Superb iv	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	Feb 2024	-	158530
Skoda	Yeti	1.6	SUV	Frontantrieb	Benzin	Apr 2014	Dec 2017	107942
Skoda	Yeti	1.2 TSI	SUV	Frontantrieb	Benzin	May 2015	Dec 2017	115188
Skoda	Yeti	1.4 TSI	SUV	Frontantrieb	Benzin	May 2015	Dec 2017	115189
Skoda	Yeti	1.4 TSI 4X4	SUV	Allrad	Benzin	May 2015	Dec 2017	115190
Skoda	Yeti	2.0 TDI	SUV	Frontantrieb	Diesel	Nov 2011	Dec 2017	10974
Skoda	Yeti	2.0 TDI	SUV	Frontantrieb	Diesel	May 2015	Dec 2017	115191
Skoda	Yeti	2.0 TDI 4X4	SUV	Allrad	Diesel	May 2015	Dec 2017	115192
Skywell	Et5/be11	EV	SUV	Frontantrieb	Elektro	Oct 2022	-	152615
Smart	#1	EV	SUV	Heckantrieb	Elektro	Jun 2022	-	148313
Smart	#1	EV Allrad	SUV	Allrad	Elektro	Aug 2022	-	149094
Smart	#3	EV	SUV	Heckantrieb	Elektro	Jun 2023	-	155186
Smart	#3	EV Allrad	SUV	Allrad	Elektro	Jun 2023	-	155187
Smart	#5	Brabus	SUV	Allrad	Elektro	Oct 2024	-	160048
Smart	#5	Premium	SUV	Heckantrieb	Elektro	Oct 2024	-	160047
Smart	#5	PRO	SUV	Heckantrieb	Elektro	Oct 2024	-	160046
Smart	#5	Pulse Allrad	SUV	Allrad	Elektro	Oct 2024	-	161529
Smart	Cabrio	0.6	Cabriolet	Heckantrieb	Benzin	Mar 2000	Jan 2004	14661
Smart	Cabrio	0.6	Cabriolet	Heckantrieb	Benzin	Jan 2001	Jan 2004	15670
Smart	Cabrio	0.6	Cabriolet	Heckantrieb	Benzin	Jun 2002	Jan 2004	17563
Smart	Cabrio	0.7	Cabriolet	Heckantrieb	Benzin	Jan 2003	Jan 2004	17200
Smart	Cabrio	0.7	Cabriolet	Heckantrieb	Benzin	Jan 2003	Jan 2004	17201
Smart	Cabrio	0.8 CDI	Cabriolet	Heckantrieb	Diesel	Mar 2001	Jan 2004	15668
Smart	City-	0.6	Coupe	Heckantrieb	Benzin	Jan 2001	Jan 2004	15669
Smart	City-	0.6	Coupe	Heckantrieb	Benzin	Jun 2002	Jan 2004	17564
Smart	City-	0.7	Coupe	Heckantrieb	Benzin	Jan 2003	Jan 2004	17197
Smart	City-	0.7	Coupe	Heckantrieb	Benzin	Jan 2003	Jan 2004	17198
Smart	City-	0.7	Coupe	Heckantrieb	Benzin	Jan 2003	Jan 2004	17199
Smart	City-	0.8 CDI	Coupe	Heckantrieb	Diesel	Nov 1999	Jan 2004	12180
Smart	Crossblade	0.6	Cabriolet	Heckantrieb	Benzin	Jun 2002	Dec 2003	16616
Smart	Forfour	0.9	Schrägheck	Heckantrieb	Benzin	Nov 2014	-	108764
Smart	Forfour	1	Schrägheck	Heckantrieb	Benzin	Jul 2014	-	107341
Smart	Forfour	1	Schrägheck	Heckantrieb	Benzin	Nov 2014	-	108763
Smart	Forfour	1.1	Schrägheck	Frontantrieb	Benzin	Jan 2004	Jun 2006	17747
Smart	Forfour	1.3	Schrägheck	Frontantrieb	Benzin	Jan 2004	Jun 2006	17748
Smart	Forfour	1.5	Schrägheck	Frontantrieb	Benzin	Jan 2004	Jun 2006	17749
Smart	Forfour	0.9 Brabus	Schrägheck	Heckantrieb	Benzin	Jul 2016	-	119983
Smart	Forfour	1.5 Brabus	Schrägheck	Frontantrieb	Benzin	May 2005	Jun 2006	18576
Smart	Forfour	1.5 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2006	17800
Smart	Forfour	1.5 CDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Jun 2006	17801
Smart	Forfour	Electric Drive	Schrägheck	Heckantrieb	Elektro	May 2017	-	127353


--- Round 1 / 首次发送 ---
## 更新点

已完成本批 100 个输入 Ktype 的物理外廓归并：

* Rapid 复用累计表中的 Liftback、Spaceback 两个尺寸组；Ktype 按 NH1 Spaceback 与 Rapid Liftback 分流，未因发动机或改款重复建组。官方资料确认两种车身分别为 4304×1706×1459 mm 和 4483×1706×1461 mm。([Allegro][1])
* Superb III 有 22 个 Ktype 的适用期覆盖 2019 改款前后；官方资料确认 Hatchback、Wagon 改款后长度发生变化，因此分别建立 `_prefl`、`_facelift` 映射，不保留无后缀基础行。([AIC德国][2])
* Superb IV 的 Hatchback、Wagon、PHEV 外廓分别闭合；Combi PHEV 的官方尺寸为 4902×1849×1483 mm。
* 完成固定表头、唯一性、引用闭合、正整数尺寸、来源与链接非空、孤立尺寸组检查。

## 进度

输入 Ktype：100
最终映射行：122
DIMENSION_GROUP：27（复用已有组 2 个，新建组 25 个）
READY：122
PENDING：0
孤立尺寸组：0
未闭合引用：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
115185	115185	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
52392	52392	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
56167	56167	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolved to Rapid liftback.	READY
115180	115180	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolved to Rapid liftback.	READY
115184	115184	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
39271	39271	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
52395	52395	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
56170	56170	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolved to Rapid liftback.	READY
59062	59062	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolved to Rapid liftback.	READY
115186	115186	Hatchback	Rapid I	NH3/NK3/NK6	5	EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	HIGH	Ktype resolved to Rapid liftback.	READY
115187	115187	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	HIGH	Ktype resolved to Rapid Spaceback (NH1).	READY
5950	5950	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
10998	10998	Van	Roomster I	5J Praktik	5	EU-SKODA-ROOMSTER-I-VAN-PRAKTIK-01	HIGH	Kasten/Kombi input resolved to factory Roomster Praktik van.	READY
10996	10996	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-MPV-PREFACELIFT-01	HIGH		READY
144116	144116	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-HATCHBACK-STANDARD-01	HIGH		READY
17008	17008	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-SEDAN-STANDARD-01	HIGH		READY
18005	18005	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-SEDAN-STANDARD-01	HIGH		READY
57689	57689	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-SEDAN-STANDARD-01	HIGH		READY
11006	11006	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-WAGON-STANDARD-01	HIGH		READY
10573	10573	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-WAGON-STANDARD-01	HIGH		READY
10574	10574	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-HATCHBACK-LIFTBACK-01	HIGH		READY
112398_prefl	112398	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112398_facelift	112398	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113304_prefl	113304	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113304_facelift	113304	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115163_prefl	115163	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115163_facelift	115163	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115164_prefl	115164	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115164_facelift	115164	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115232_prefl	115232	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115232_facelift	115232	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115233_prefl	115233	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115233_facelift	115233	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113310_prefl	113310	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113310_facelift	113310	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115166_prefl	115166	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115166_facelift	115166	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115235_prefl	115235	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115235_facelift	115235	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115236_prefl	115236	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115236_facelift	115236	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112394_prefl	112394	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112394_facelift	112394	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112397_prefl	112397	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112397_facelift	112397	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115167_prefl	115167	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115167_facelift	115167	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115168_prefl	115168	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115168_facelift	115168	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
142870	142870	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH		READY
142871	142871	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH		READY
113313_prefl	113313	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113313_facelift	113313	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115169_prefl	115169	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115169_facelift	115169	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115237_prefl	115237	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115237_facelift	115237	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115238_prefl	115238	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115238_facelift	115238	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113308_prefl	113308	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
113308_facelift	113308	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112399_prefl	112399	Hatchback	Superb III pre-facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
112399_facelift	112399	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115165_prefl	115165	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115165_facelift	115165	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
801674	801674	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	HIGH		READY
801681	801681	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH		READY
115239_prefl	115239	Wagon	Superb III pre-facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
115239_facelift	115239	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	HIGH	Ktype spans the 2019 facelift; official standard outer dimensions differ by stage.	READY
801378	801378	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-PHEV-01	MEDIUM	PHEV hatch uses the higher production body-height specification.	READY
803388	803388	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-PHEV-01	MEDIUM	PHEV hatch uses the higher production body-height specification.	READY
158499	158499	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-PHEV-01	HIGH		READY
156862	156862	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	HIGH		READY
157413	157413	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	HIGH		READY
156864	156864	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	HIGH		READY
157414	157414	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	HIGH		READY
158105	158105	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	HIGH		READY
158106	158106	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	HIGH		READY
801044	801044	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	HIGH		READY
801045	801045	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	HIGH		READY
158342	158342	Wagon	Superb IV		5	EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	HIGH		READY
158530	158530	Hatchback	Superb IV		5	EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	HIGH		READY
107942	107942	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
115188	115188	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
115189	115189	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
115190	115190	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
10974	10974	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
115191	115191	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
115192	115192	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-SUV-STANDARD-01	HIGH		READY
152615	152615	SUV	ET5/BE11 I		5	EU-SKYWELL-ET5-I-SUV-STANDARD-01	MEDIUM	ET5/BE11 alias resolved to the 2021-on production body.	READY
148313	148313	SUV	smart #1 I		5	EU-SMART-1-I-SUV-STANDARD-01	HIGH		READY
149094	149094	SUV	smart #1 I		5	EU-SMART-1-I-SUV-STANDARD-01	HIGH		READY
155186	155186	SUV	smart #3 I		5	EU-SMART-3-I-SUV-STANDARD-01	HIGH		READY
155187	155187	SUV	smart #3 I		5	EU-SMART-3-I-SUV-STANDARD-01	HIGH		READY
160048	160048	SUV	smart #5 I		5	EU-SMART-5-I-SUV-STANDARD-01	HIGH		READY
160047	160047	SUV	smart #5 I		5	EU-SMART-5-I-SUV-STANDARD-01	HIGH		READY
160046	160046	SUV	smart #5 I		5	EU-SMART-5-I-SUV-STANDARD-01	HIGH		READY
161529	161529	SUV	smart #5 I		5	EU-SMART-5-I-SUV-STANDARD-01	HIGH		READY
14661	14661	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
15670	15670	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
17563	17563	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
17200	17200	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
17201	17201	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
15668	15668	Convertible	fortwo I	A450	2	EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	HIGH		READY
15669	15669	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
17564	17564	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
17197	17197	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
17198	17198	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
17199	17199	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
12180	12180	Coupe	fortwo I	C450	2	EU-SMART-FORTWO-I-COUPE-CITY-01	HIGH	City- input resolved to first-generation smart city-coupé.	READY
16616	16616	Convertible	Crossblade I	450	2	EU-SMART-CROSSBLADE-I-CONVERTIBLE-STANDARD-01	MEDIUM		READY
108764	108764	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
107341	107341	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
108763	108763	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
17747	17747	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
17748	17748	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
17749	17749	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
119983	119983	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
18576	18576	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
17800	17800	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
17801	17801	Hatchback	Forfour I	W454	5	EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	HIGH		READY
127353	127353	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载 left18448_15401-15500_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15401-15500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-RAPID-I-HATCHBACK-LIFTBACK-01	4483	1706	1461	Škoda official technical data	https://cdn.skoda-storyboard.com/2016/05/TD-RAPID-en.pdf
EU-SKODA-RAPID-I-HATCHBACK-SPACEBACK-01	4304	1706	1459	Škoda official technical data	https://cdn.skoda-storyboard.com/2016/05/TD-RAPID-SPACEBACK-en-1.pdf
EU-SKODA-ROOMSTER-I-MPV-PREFACELIFT-01	4205	1684	1607	Auto-Data	https://www.auto-data.net/en/skoda-roomster-model-1561
EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	4214	1684	1607	Auto-Data	https://www.auto-data.net/en/skoda-roomster-facelift-2010-generation-4187
EU-SKODA-ROOMSTER-I-VAN-PRAKTIK-01	4213	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/3143165/skoda_praktik_1_2_tdi_cr_75.html
EU-SKODA-SCALA-I-HATCHBACK-STANDARD-01	4362	1793	1471	Škoda official technical data	https://cdn.skoda-storyboard.com/2019/04/TD-SCALA-petrol-diesel-en.pdf
EU-SKODA-SUPERB-I-SEDAN-STANDARD-01	4803	1765	1469	Auto-Data	https://www.auto-data.net/en/skoda-superb-i-1.9-tdi-131hp-14115
EU-SKODA-SUPERB-II-WAGON-STANDARD-01	4838	1817	1510	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-combi-1.8-tsi-160hp-17427
EU-SKODA-SUPERB-II-HATCHBACK-LIFTBACK-01	4838	1817	1462	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-1.8-tsi-160hp-14106
EU-SKODA-SUPERB-III-HATCHBACK-PREFACELIFT-01	4861	1864	1468	Škoda official technical data	https://cdn.skoda-storyboard.com/2016/05/TD-SUPERB-en.pdf
EU-SKODA-SUPERB-III-WAGON-PREFACELIFT-01	4856	1864	1477	Škoda official technical data	https://cdn.skoda-storyboard.com/2016/05/TD-SUPERB-COMBI-en-1.pdf
EU-SKODA-SUPERB-III-HATCHBACK-FACELIFT-01	4869	1864	1469	Škoda official technical data	https://cdn.skoda-storyboard.com/2019/07/TD-SUPERB-en.pdf
EU-SKODA-SUPERB-III-WAGON-FACELIFT-01	4862	1864	1477	Škoda official technical data	https://cdn.skoda-storyboard.com/2016/05/TD-SUPERB-COMBI-en-2.pdf
EU-SKODA-SUPERB-IV-HATCHBACK-STANDARD-01	4912	1849	1481	Škoda official technical data	https://cdn.skoda-storyboard.com/2024/03/TD-Superb-en_87b42ad4.pdf
EU-SKODA-SUPERB-IV-HATCHBACK-PHEV-01	4912	1849	1496	Auto-Data	https://www.auto-data.net/en/skoda-superb-iv-iv-1.5-tsi-204hp-plug-in-hybrid-dsg-53760
EU-SKODA-SUPERB-IV-WAGON-STANDARD-01	4902	1849	1482	Škoda official technical data	https://cdn.skoda-storyboard.com/2024/03/TD-Superb-en_87b42ad4.pdf
EU-SKODA-SUPERB-IV-WAGON-PHEV-01	4902	1849	1483	Škoda official technical data	https://cdn.skoda-storyboard.com/2024/03/TD-Superb-en_87b42ad4.pdf
EU-SKODA-YETI-I-SUV-STANDARD-01	4223	1793	1691	Škoda technical specifications	https://www.australiancar.reviews/_pdfs/Skoda_Yeti_5LII_Technicalspecifications_201405.pdf
EU-SKYWELL-ET5-I-SUV-STANDARD-01	4698	1908	1696	Skywell ET5 brochure	https://autocatalogarchive.com/wp-content/uploads/2023/09/Skywell-ET5-2023-UAE.pdf
EU-SMART-1-I-SUV-STANDARD-01	4270	1822	1636	smart official specification sheet	https://nz.smart.com/app/uploads/2025/02/smart-1-spec-sheet.pdf
EU-SMART-3-I-SUV-STANDARD-01	4400	1844	1556	smart official specification sheet	https://nz.smart.com/app/uploads/2025/02/smart-3-spec-sheet.pdf
EU-SMART-5-I-SUV-STANDARD-01	4695	1920	1705	AutomobileDimensions	https://www.automobiledimension.com/model/smart/hashtag5
EU-SMART-FORTWO-I-CONVERTIBLE-CABRIO-01	2500	1515	1549	Auto-Data	https://www.auto-data.net/en/smart-fortwo-cabrio-a450-generation-3289
EU-SMART-FORTWO-I-COUPE-CITY-01	2500	1515	1549	Auto-Data	https://www.auto-data.net/en/smart-fortwo-coupe-c450-generation-3290
EU-SMART-CROSSBLADE-I-CONVERTIBLE-STANDARD-01	2622	1618	1508	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/3154490/smart_crossblade.html
EU-SMART-FORFOUR-I-HATCHBACK-STANDARD-01	3752	1684	1450	Auto-Data	https://www.auto-data.net/en/smart-forfour-w454-generation-3286
EU-SMART-FORFOUR-II-HATCHBACK-STANDARD-01	3495	1665	1554	Auto-Data	https://www.auto-data.net/en/smart-forfour-ii-w453-1.0-71hp-24116
```

[下载 left18448_15401-15500_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15401-15500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://allegro.pl/produkt/dpa-11211294902-wspornik-kratka-chlodnicy-823e2967-9932-47db-b733-c82bd61688d7?utm_source=chatgpt.com "DPA 11211294902 Wspornik, kratka chłodnicy • Cena, Opinie - Allegro"
[2]: https://aic-germany.de/en/product-catalogue/3056?utm_source=chatgpt.com "Product catalogue from AIC Germany"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2006 行）
- 累计尺寸组：dimension_groups_final.tsv（401 行）

