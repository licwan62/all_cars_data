# 任务：left18448 第 15201-15300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0153__c8d3e4e8


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15201-15300 行

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
left18448 第 15201-15300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15201-15300_ktype_dimension_mapping_final.tsv
- left18448_15201-15300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	3992	1732	1467
EU-SKODA-FABIA-III-WAGON-STANDARD-01	4257	1732	1467

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Skoda	Fabia iii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	127941
Skoda	Fabia iii	1.0 TSI	Kombi	Frontantrieb	Benzin	Aug 2014	Dec 2022	127942
Skoda	Fabia iii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	128141
Skoda	Fabia iii	1.0 TSI	Kombi	Frontantrieb	Benzin	Aug 2014	Dec 2022	128142
Skoda	Fabia iii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	108657
Skoda	Fabia iii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2014	Jun 2021	108658
Skoda	Fabia iii	1.2 TSI	Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	108662
Skoda	Fabia iii	1.2 TSI	Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	108663
Skoda	Fabia iii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2014	Jun 2021	108659
Skoda	Fabia iii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Aug 2014	Jun 2021	108660
Skoda	Fabia iii	1.4 TDI	Kombi	Frontantrieb	Diesel	Oct 2014	Dec 2022	108664
Skoda	Fabia iii	1.4 TDI	Kombi	Frontantrieb	Diesel	Oct 2014	Dec 2022	108665
Skoda	Fabia iii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	May 2015	Jun 2021	117784
Skoda	Fabia iii	1.4 TDI	Kombi	Frontantrieb	Diesel	May 2015	Dec 2022	117785
Skoda	Fabia iii praktik	1	Kasten/Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	154627
Skoda	Fabia iii praktik	1	Kasten/Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	154628
Skoda	Fabia iii praktik	1.2 TSI	Kasten/Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	154637
Skoda	Fabia iii praktik	1.2 TSI	Kasten/Kombi	Frontantrieb	Benzin	Oct 2014	Dec 2022	154638
Skoda	Fabia iii praktik	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	Oct 2014	Dec 2022	154639
Skoda	Fabia iii praktik	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	Oct 2014	Dec 2022	154640
Skoda	Fabia iii praktik	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	May 2015	Dec 2022	154641
Skoda	Fabia iv	1.0 MPI	Schrägheck	Frontantrieb	Benzin	Jun 2021	-	145019
Skoda	Fabia iv	1.0 MPI	Schrägheck	Frontantrieb	Benzin	Aug 2021	-	145238
Skoda	Fabia iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2021	-	145017
Skoda	Fabia iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jun 2021	-	145018
Skoda	Fabia iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	Jan 2024	-	157377
Skoda	Fabia iv	1.5 Rally2	Schrägheck	Frontantrieb	Benzin	Nov 2024	-	801036
Skoda	Fabia iv	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2021	-	146489
Skoda	Fabia iv	1.5 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2025	-	802660
Skoda	Favorit	1.3	Pick-up	Frontantrieb	Benzin	Dec 1992	Jun 1997	11189
Skoda	Favorit	1.3	Pick-up	Frontantrieb	Benzin	Dec 1992	Jun 1997	11190
Skoda	Favorit	1.3	Pick-up	Frontantrieb	Benzin	Dec 1992	Jun 1997	11191
Skoda	Favorit	1.3	Kasten/Kombi	Frontantrieb	Benzin	Oct 1990	Dec 1992	143317
Skoda	Favorit	1.3	Kasten/Kombi	Frontantrieb	Benzin	Jan 1989	Aug 1995	143318
Skoda	Felicia i	1.3	Pick-up	Frontantrieb	Benzin	Jun 1997	Apr 2002	11187
Skoda	Felicia i	1.3	Pick-up	Frontantrieb	Benzin	Jun 1997	Apr 2002	11188
Skoda	Felicia i	1.3	Schrägheck	Frontantrieb	Benzin	Oct 1994	Mar 1998	14741
Skoda	Felicia i	1.3	Kombi	Frontantrieb	Benzin	Aug 1995	Mar 1998	14744
Skoda	Felicia i	1.9 D	Schrägheck	Frontantrieb	Diesel	Oct 1995	Mar 1998	5678
Skoda	Felicia i	1.9 D	Kombi	Frontantrieb	Diesel	Oct 1995	Mar 1998	5679
Skoda	Felicia i	1.9 D	Pick-up	Frontantrieb	Diesel	Jun 1997	Apr 2002	8703
Skoda	Felicia ii	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1998	Jun 2001	11192
Skoda	Felicia ii	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1998	Jun 2001	11193
Skoda	Felicia ii	1.3	Kombi	Frontantrieb	Benzin	Aug 1996	Jun 2001	11196
Skoda	Felicia ii	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1998	Jun 2001	14745
Skoda	Felicia ii	1.6	Schrägheck	Frontantrieb	Benzin	Jan 1998	Jun 2001	11194
Skoda	Felicia ii	1.6	Kombi	Frontantrieb	Benzin	Jan 1998	Jun 2001	11197
Skoda	Felicia ii	1.9 D	Schrägheck	Frontantrieb	Diesel	Jan 1998	Jun 2001	11195
Skoda	Felicia ii	1.9 D	Kombi	Frontantrieb	Diesel	Jan 1998	Jun 2001	11198
Skoda	Kamiq	1.6 TDI	SUV	Frontantrieb	Diesel	Sep 2019	-	146729
Skoda	Karoq	1.0 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128286
Skoda	Karoq	1.0 TSI	SUV	Frontantrieb	Benzin	Sep 2020	-	142867
Skoda	Karoq	1.5 TSI	SUV	Frontantrieb	Benzin	Jul 2017	-	128287
Skoda	Karoq	1.6 TDI	SUV	Frontantrieb	Diesel	Jul 2017	-	128288
Skoda	Karoq	2.0 TDI	SUV	Frontantrieb	Diesel	Nov 2020	-	144747
Skoda	Karoq	2.0 TDI 4X4	SUV	Allrad	Diesel	Jul 2017	-	128289
Skoda	Karoq	2.0 TDI 4X4	SUV	Allrad	Diesel	Jul 2017	-	128471
Skoda	Karoq	2.0 TSI 4X4	SUV	Allrad	Benzin	Nov 2020	-	801672
Skoda	Kodiaq i	1.4 TSI	SUV	Frontantrieb	Benzin	Oct 2016	-	123422
Skoda	Kodiaq i	1.4 TSI	SUV	Frontantrieb	Benzin	Oct 2016	-	123933
Skoda	Kodiaq i	1.4 TSI 4X4	SUV	Allrad	Benzin	Oct 2016	-	123424
Skoda	Kodiaq i	2.0 RS 4X4	SUV	Allrad	Benzin	Jun 2021	-	145016
Skoda	Kodiaq i	2.0 TDI	SUV	Frontantrieb	Diesel	Oct 2016	-	123934
Skoda	Kodiaq i	2.0 TDI	SUV	Frontantrieb	Diesel	Jul 2018	-	154693
Skoda	Kodiaq i	2.0 TDI 4X4	SUV	Allrad	Diesel	Oct 2016	-	123426
Skoda	Kodiaq i	2.0 TDI 4X4	SUV	Allrad	Diesel	Oct 2016	-	123427
Skoda	Kodiaq i	2.0 TSI 4X4	SUV	Allrad	Benzin	Oct 2016	-	123425
Skoda	Kodiaq i	2.0 TSI 4X4	SUV	Allrad	Benzin	Nov 2020	-	801673
Skoda	Kodiaq ii	1.4 TSI	SUV	Frontantrieb	Benzin	Apr 2024	-	801829
Skoda	Kodiaq ii	1.5 TSI IV Phev	SUV	Frontantrieb	Benzin/Elektro	Apr 2024	-	158377
Skoda	Kodiaq ii	1.5 TSI Mhev	SUV	Frontantrieb	Benzin/Elektro	Jan 2024	-	157549
Skoda	Kodiaq ii	2.0 TDI	SUV	Frontantrieb	Diesel	Jan 2024	-	157362
Skoda	Kodiaq ii	2.0 TDI 4X4	SUV	Allrad	Diesel	Jan 2024	-	157363
Skoda	Kodiaq ii	2.0 TDI 4X4	SUV	Allrad	Diesel	Aug 2024	-	801830
Skoda	Kodiaq ii	2.0 TSI 4X4	SUV	Allrad	Benzin	Nov 2024	-	801026
Skoda	Kodiaq ii	2.0 TSI 4X4	SUV	Allrad	Benzin	Jan 2025	-	801222
Skoda	Octavia	1.4	Schrägheck	Frontantrieb	Benzin	Apr 1999	Mar 2001	14748
Skoda	Octavia	1.4	Schrägheck	Frontantrieb	Benzin	May 2004	May 2006	17972
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	Feb 1997	Dec 2007	8009
Skoda	Octavia	1.6	Kombi	Frontantrieb	Benzin	Jul 1998	Sep 2004	11629
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	Nov 2000	Dec 2010	15910
Skoda	Octavia	1.6	Kombi	Frontantrieb	Benzin	Sep 2000	Dec 2010	15918
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2004	Jun 2013	17973
Skoda	Octavia	1.6	Kombi	Frontantrieb	Benzin	Sep 2004	Jun 2013	18246
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2014	Oct 2020	107943
Skoda	Octavia	2	Schrägheck	Frontantrieb	Benzin	Apr 1999	May 2007	13085
Skoda	Octavia	2	Kombi	Frontantrieb	Benzin	Apr 1999	May 2007	13086
Skoda	Octavia	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2016	Oct 2020	120206
Skoda	Octavia	1.0 TSI	Kombi	Frontantrieb	Benzin	May 2016	Oct 2020	120207
Skoda	Octavia	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Feb 2017	58757
Skoda	Octavia	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Feb 2017	58758
Skoda	Octavia	1.2 TSI	Kombi	Frontantrieb	Benzin	Nov 2012	Feb 2017	58762
Skoda	Octavia	1.2 TSI	Kombi	Frontantrieb	Benzin	Nov 2012	Feb 2017	58763
Skoda	Octavia	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	Feb 2017	115152
Skoda	Octavia	1.2 TSI	Kombi	Frontantrieb	Benzin	May 2015	Feb 2017	115154
Skoda	Octavia	1.4 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Dec 2010	15292
Skoda	Octavia	1.4 16V	Kombi	Frontantrieb	Benzin	Aug 2000	Dec 2010	15917
Skoda	Octavia	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2012	Feb 2017	58750
Skoda	Octavia	1.4 TSI	Kombi	Frontantrieb	Benzin	Nov 2012	Feb 2017	58764
Skoda	Octavia	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Aug 2014	Oct 2020	115156


--- Round 1 / 首次发送 ---
## 更新点

复用跨批次已闭合的 2 个 Fabia III 尺寸组；新增 31 个尺寸组。发动机、燃料和功率差异已合并，Fabia III Praktik 复用 Combi 外廓。仅对有明确三维变化且当前 Ktype 覆盖前后阶段的 Karoq、Kodiaq I 和 Octavia 派生 `_prefl`、`_facelift` 行。尺寸优先采用 Škoda 官方技术资料，其余老款车型采用 Auto-Data 或 Automobile-Catalog 的直接规格页。([斯柯达故事板][1])

## 进度

* 输入 Ktype：100
* 最终映射行：120
* DIMENSION_GROUP：33
* 跨物理阶段拆分 Ktype：20
* PENDING：0
* 表头、唯一性、Ktype 覆盖、引用闭合、正整数三维、来源和 URL：全部通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127941	127941	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
127942	127942	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
128141	128141	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
128142	128142	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
108657	108657	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108658	108658	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108662	108662	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
108663	108663	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
108659	108659	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108660	108660	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
108664	108664	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
108665	108665	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
117784	117784	Hatchback	III		5	EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	HIGH		READY
117785	117785	Wagon	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	HIGH		READY
154627	154627	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154628	154628	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154637	154637	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154638	154638	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154639	154639	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154640	154640	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
154641	154641	Van	III		5	EU-SKODA-FABIA-III-WAGON-STANDARD-01	MEDIUM	Commercial derivative uses the Fabia III Combi outer envelope.	READY
145019	145019	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
145238	145238	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
145017	145017	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
145018	145018	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
157377	157377	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
801036	801036	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH	Road-going PJ3 Rally2 power variant; standard hatch outer body.	READY
146489	146489	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
802660	802660	Hatchback	IV		5	EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	HIGH		READY
11189	11189	Pickup	I		2	EU-SKODA-FAVORIT-I-PICKUP-STANDARD-01	HIGH		READY
11190	11190	Pickup	I		2	EU-SKODA-FAVORIT-I-PICKUP-STANDARD-01	HIGH		READY
11191	11191	Pickup	I		2	EU-SKODA-FAVORIT-I-PICKUP-STANDARD-01	HIGH		READY
143317	143317	Wagon	I		5	EU-SKODA-FAVORIT-I-WAGON-STANDARD-01	MEDIUM	Kasten/Kombi listing assigned the Forman estate outer envelope.	READY
143318	143318	Wagon	I		5	EU-SKODA-FAVORIT-I-WAGON-STANDARD-01	MEDIUM	Kasten/Kombi listing assigned the Forman estate outer envelope.	READY
11187	11187	Pickup	I		2	EU-SKODA-FELICIA-I-PICKUP-STANDARD-01	HIGH		READY
11188	11188	Pickup	I		2	EU-SKODA-FELICIA-I-PICKUP-STANDARD-01	HIGH		READY
14741	14741	Hatchback	I		5	EU-SKODA-FELICIA-I-HATCHBACK-STANDARD-01	HIGH		READY
14744	14744	Wagon	I		5	EU-SKODA-FELICIA-I-WAGON-STANDARD-01	HIGH		READY
5678	5678	Hatchback	I		5	EU-SKODA-FELICIA-I-HATCHBACK-STANDARD-01	HIGH		READY
5679	5679	Wagon	I		5	EU-SKODA-FELICIA-I-WAGON-STANDARD-01	HIGH		READY
8703	8703	Pickup	I		2	EU-SKODA-FELICIA-I-PICKUP-STANDARD-01	HIGH		READY
11192	11192	Hatchback	II		5	EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	HIGH		READY
11193	11193	Hatchback	II		5	EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	HIGH		READY
11196	11196	Wagon	II		5	EU-SKODA-FELICIA-II-WAGON-STANDARD-01	HIGH		READY
14745	14745	Hatchback	II		5	EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	HIGH		READY
11194	11194	Hatchback	II		5	EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	HIGH		READY
11197	11197	Wagon	II		5	EU-SKODA-FELICIA-II-WAGON-STANDARD-01	HIGH		READY
11195	11195	Hatchback	II		5	EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	HIGH		READY
11198	11198	Wagon	II		5	EU-SKODA-FELICIA-II-WAGON-STANDARD-01	HIGH		READY
146729	146729	SUV	I		5	EU-SKODA-KAMIQ-I-SUV-STANDARD-01	HIGH		READY
128286_prefl	128286	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	MEDIUM	Pre-facelift outer envelope.	READY
128286_facelift	128286	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-FWD-01	MEDIUM	Facelift outer envelope.	READY
142867_prefl	142867	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	MEDIUM	Pre-facelift outer envelope.	READY
142867_facelift	142867	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-FWD-01	MEDIUM	Facelift outer envelope.	READY
128287_prefl	128287	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	MEDIUM	Pre-facelift outer envelope.	READY
128287_facelift	128287	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-FWD-01	MEDIUM	Facelift outer envelope.	READY
128288	128288	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	HIGH		READY
144747_prefl	144747	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	MEDIUM	Pre-facelift outer envelope.	READY
144747_facelift	144747	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-FWD-01	MEDIUM	Facelift outer envelope.	READY
128289_prefl	128289	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-AWD-01	MEDIUM	Pre-facelift outer envelope.	READY
128289_facelift	128289	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-AWD-01	MEDIUM	Facelift outer envelope.	READY
128471	128471	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-AWD-01	HIGH		READY
801672_prefl	801672	SUV	I		5	EU-SKODA-KAROQ-I-SUV-PREFL-AWD-01	MEDIUM	Pre-facelift outer envelope.	READY
801672_facelift	801672	SUV	I		5	EU-SKODA-KAROQ-I-SUV-FACELIFT-AWD-01	MEDIUM	Facelift outer envelope.	READY
123422	123422	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
123933	123933	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
123424	123424	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
145016	145016	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-RS-01	HIGH		READY
123934_prefl	123934	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	MEDIUM	Pre-facelift outer envelope.	READY
123934_facelift	123934	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-STANDARD-01	MEDIUM	Facelift outer envelope.	READY
154693	154693	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
123426_prefl	123426	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	MEDIUM	Pre-facelift outer envelope.	READY
123426_facelift	123426	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-STANDARD-01	MEDIUM	Facelift outer envelope.	READY
123427	123427	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
123425	123425	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	HIGH		READY
801673_prefl	801673	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	MEDIUM	Pre-facelift outer envelope.	READY
801673_facelift	801673	SUV	I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-STANDARD-01	MEDIUM	Facelift outer envelope.	READY
801829	801829	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-FWD-STANDARD-01	MEDIUM	Input engine label is not listed in the EU technical sheet; standard FWD body envelope assigned.	READY
158377	158377	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-PHEV-STANDARD-01	HIGH		READY
157549	157549	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-FWD-STANDARD-01	HIGH		READY
157362	157362	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-FWD-STANDARD-01	HIGH		READY
157363	157363	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-AWD-STANDARD-01	HIGH		READY
801830	801830	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-AWD-STANDARD-01	HIGH		READY
801026	801026	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-AWD-STANDARD-01	HIGH		READY
801222	801222	SUV	II		5	EU-SKODA-KODIAQ-II-SUV-AWD-STANDARD-01	HIGH		READY
14748_prefl	14748	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
14748_facelift	14748	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
17972	17972	Hatchback	II		5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	HIGH		READY
8009_prefl	8009	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
8009_facelift	8009	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
11629_prefl	11629	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
11629_facelift	11629	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
15910	15910	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH		READY
15918	15918	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH		READY
17973_prefl	17973	Hatchback	II		5	EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
17973_facelift	17973	Hatchback	II		5	EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
18246_prefl	18246	Wagon	II		5	EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
18246_facelift	18246	Wagon	II		5	EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
107943_prefl	107943	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
107943_facelift	107943	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
13085_prefl	13085	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
13085_facelift	13085	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
13086_prefl	13086	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
13086_facelift	13086	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
120206_prefl	120206	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
120206_facelift	120206	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
120207_prefl	120207	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
120207_facelift	120207	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
58757	58757	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
58758	58758	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
58762	58762	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
58763	58763	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
115152	115152	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
115154	115154	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
15292	15292	Hatchback	I		5	EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	HIGH		READY
15917	15917	Wagon	I		5	EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	HIGH		READY
58750	58750	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH		READY
58764	58764	Wagon	III		5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH		READY
115156_prefl	115156	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift outer envelope.	READY
115156_facelift	115156	Hatchback	III		5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	MEDIUM	Facelift outer envelope.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_15201-15300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FABIA-III-HATCHBACK-STANDARD-01	3992	1732	1467	Auto-Data — Skoda Fabia III hatchback 1.2 TSI	https://www.auto-data.net/en/skoda-fabia-iii-1.2-tsi-110hp-20329
EU-SKODA-FABIA-III-WAGON-STANDARD-01	4257	1732	1467	Auto-Data — Skoda Fabia III Combi	https://www.auto-data.net/en/skoda-fabia-iii-combi-generation-4318
EU-SKODA-FABIA-IV-HATCHBACK-STANDARD-01	4108	1780	1459	Škoda Auto technical data — Fabia IV petrol	https://cdn.skoda-storyboard.com/2021/06/TD-2-FABIA-petrol-en.pdf
EU-SKODA-FAVORIT-I-PICKUP-STANDARD-01	4065	1620	1430	Automobile-Catalog — 1994 Skoda Pick-up LX	https://www.automobile-catalog.com/car/1994/3133250/skoda_pick-up_lx.html
EU-SKODA-FAVORIT-I-WAGON-STANDARD-01	4160	1620	1415	Automobile-Catalog — 1993 Skoda Forman LX/Favorit Estate	https://www.automobile-catalog.com/car/1993/3133220/skoda_forman_lx_favorit_estate_lxi.html
EU-SKODA-FELICIA-I-PICKUP-STANDARD-01	4115	1635	1440	Automobile-Catalog — 1998 Skoda Felicia Pickup 1.3	https://www.automobile-catalog.com/car/1998/3134120/skoda_felicia_pickup_1_3_54.html
EU-SKODA-FELICIA-I-HATCHBACK-STANDARD-01	3855	1635	1415	Automobile-Catalog — 1996 Skoda Felicia 1.3	https://www.automobile-catalog.com/car/1996/3133760/skoda_felicia_1_3_68.html
EU-SKODA-FELICIA-I-WAGON-STANDARD-01	4205	1635	1420	Automobile-Catalog — 1996 Skoda Felicia Estate 1.3	https://www.automobile-catalog.com/car/1996/3133685/skoda_felicia_estate_1_3_68.html
EU-SKODA-FELICIA-II-HATCHBACK-STANDARD-01	3883	1635	1415	Automobile-Catalog — 1999 Skoda Felicia 1.6	https://www.automobile-catalog.com/car/1999/3133940/skoda_felicia_1_6.html
EU-SKODA-FELICIA-II-WAGON-STANDARD-01	4237	1635	1420	Automobile-Catalog — 1999 Skoda Felicia Estate 1.9 D	https://www.automobile-catalog.com/car/1999/3134000/skoda_felicia_estate_1_9_d.html
EU-SKODA-KAMIQ-I-SUV-STANDARD-01	4241	1793	1553	Škoda Auto press kit — Kamiq overview	https://cdn.skoda-storyboard.com/2019/08/01_Press_Kit_SKODA_KAMIQ_Overview.pdf
EU-SKODA-KAROQ-I-SUV-PREFL-FWD-01	4382	1841	1603	Škoda Auto technical data — Karoq pre-facelift FWD	https://cdn.skoda-storyboard.com/2020/03/TD-KAROQ-en.pdf
EU-SKODA-KAROQ-I-SUV-FACELIFT-FWD-01	4390	1841	1603	Škoda Auto technical data — Karoq facelift FWD	https://cdn.skoda-storyboard.com/2020/11/TD-KAROQ-en.pdf
EU-SKODA-KAROQ-I-SUV-PREFL-AWD-01	4382	1841	1607	Škoda Auto technical data — Karoq pre-facelift AWD	https://cdn.skoda-storyboard.com/2020/03/TD-KAROQ-en.pdf
EU-SKODA-KAROQ-I-SUV-FACELIFT-AWD-01	4390	1841	1608	Škoda Auto technical data — Karoq facelift AWD	https://cdn.skoda-storyboard.com/2020/11/TD-KAROQ-en.pdf
EU-SKODA-KODIAQ-I-SUV-PREFL-STANDARD-01	4697	1882	1655	Škoda Auto technical data — Kodiaq I pre-facelift	https://cdn.skoda-storyboard.com/2018/02/TD-KODIAQ_en.pdf
EU-SKODA-KODIAQ-I-SUV-FACELIFT-RS-01	4699	1882	1666	Škoda Auto technical data — Kodiaq I RS	https://cdn.skoda-storyboard.com/2022/10/td_kodiaq_rs_en_26829012.pdf
EU-SKODA-KODIAQ-I-SUV-FACELIFT-STANDARD-01	4697	1882	1661	Škoda Auto technical data — Kodiaq I facelift	https://cdn.skoda-storyboard.com/2021/06/TD_KODIAQ_en.pdf
EU-SKODA-KODIAQ-II-SUV-FWD-STANDARD-01	4758	1864	1659	Škoda Auto technical data — Kodiaq II petrol/diesel FWD	https://cdn.skoda-storyboard.com/2024/04/TD_Kodiaq_Petrol_EN_9b580c72.pdf
EU-SKODA-KODIAQ-II-SUV-PHEV-STANDARD-01	4758	1864	1656	Škoda Auto technical data — Kodiaq II PHEV	https://cdn.skoda-storyboard.com/2024/04/TD_Kodiaq_PHEV_EN_ca44c6d3.pdf
EU-SKODA-KODIAQ-II-SUV-AWD-STANDARD-01	4758	1864	1657	Škoda Auto technical data — Kodiaq II petrol/diesel AWD	https://cdn.skoda-storyboard.com/2024/04/TD_Kodiaq_Diesel_EN_c6f3e8ba.pdf
EU-SKODA-OCTAVIA-I-HATCHBACK-PREFL-01	4511	1731	1429	Automobile-Catalog — 1998 Skoda Octavia hatchback	https://www.automobile-catalog.com/car/1998/3134450/skoda_octavia_1_6_100.html
EU-SKODA-OCTAVIA-I-HATCHBACK-FACELIFT-01	4507	1731	1431	Automobile-Catalog — 2001 Skoda Octavia hatchback	https://www.automobile-catalog.com/car/2001/3135200/skoda_octavia_2_0.html
EU-SKODA-OCTAVIA-II-HATCHBACK-PREFL-01	4572	1769	1462	Automobile-Catalog — Skoda Octavia II phase-I hatchback range	https://www.automobile-catalog.com/make/skoda/octavia_2gen/octavia_2_1_hatch/2008.html
EU-SKODA-OCTAVIA-I-WAGON-PREFL-01	4511	1731	1448	Automobile-Catalog — 1999 Skoda Octavia Combi	https://www.automobile-catalog.com/car/1999/3134840/skoda_octavia_combi_2_0_automatic.html
EU-SKODA-OCTAVIA-I-WAGON-FACELIFT-01	4513	1731	1457	Automobile-Catalog — 2001 Skoda Octavia Combi	https://www.automobile-catalog.com/car/2001/3135125/skoda_octavia_combi_1_4_16v.html
EU-SKODA-OCTAVIA-II-HATCHBACK-FACELIFT-01	4569	1769	1462	Automobile-Catalog — 2009 Skoda Octavia II hatchback	https://www.automobile-catalog.com/car/2009/3138080/skoda_octavia_1_6_mpi_102.html
EU-SKODA-OCTAVIA-II-WAGON-PREFL-01	4572	1769	1468	Automobile-Catalog — 2008 Skoda Octavia II Combi	https://www.automobile-catalog.com/car/2008/3137930/skoda_octavia_combi_1_4_16v_80.html
EU-SKODA-OCTAVIA-II-WAGON-FACELIFT-01	4569	1769	1468	Automobile-Catalog — 2009 Skoda Octavia II Combi	https://www.automobile-catalog.com/car/2009/3138170/skoda_octavia_combi_1_4_16v_80.html
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461	Auto-Data — Skoda Octavia III hatchback 1.8 TSI	https://www.auto-data.net/en/skoda-octavia-iii-1.8-tsi-180hp-19283
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Škoda Auto technical data — Octavia III facelift hatchback	https://cdn.skoda-storyboard.com/2019/08/TD-OCTAVIA-cz.pdf
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465	Auto-Data — Skoda Octavia III Combi 1.4 TSI	https://www.auto-data.net/en/skoda-octavia-iii-combi-1.4-tsi-140hp-19288
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Škoda Auto press kit — Octavia III facelift Combi	https://cdn.skoda-storyboard.com/2017/02/170207-%C5%A0KODA-OCTAVIA-Press-Kit.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_15201-15300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://cdn.skoda-storyboard.com/2021/06/TD-2-FABIA-petrol-en.pdf "https://cdn.skoda-storyboard.com/2021/06/TD-2-FABIA-petrol-en.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1753 行）
- 累计尺寸组：dimension_groups_final.tsv（361 行）

