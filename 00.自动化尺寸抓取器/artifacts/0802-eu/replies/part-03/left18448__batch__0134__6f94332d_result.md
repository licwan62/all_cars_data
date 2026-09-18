# 任务：left18448 第 13301-13400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0134__6f94332d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13301-13400 行

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
left18448 第 13301-13400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13301-13400_ktype_dimension_mapping_final.tsv
- left18448_13301-13400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940
EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	5016	1895	1942
EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	4813	1895	1942
EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	4959	1920	1899
EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	4959	1920	1940

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Peugeot	Expert	2.0 HDI 130 4X4	Bus	Allrad	Diesel	Mar 2011	Mar 2016	108627
Peugeot	Expert	2.0 HDI 130 4X4	Kasten	Allrad	Diesel	Jan 2012	Mar 2016	109725
Peugeot	Expert	2.0 HDI 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2009	-	119828
Peugeot	Expert	2.0 HDI 16V	Bus	Frontantrieb	Diesel	Jul 2000	Dec 2006	18278
Peugeot	Expert	2.2 Bluehdi 150	Kasten	Frontantrieb	Diesel	May 2025	-	802364
Peugeot	Expert	2.2 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2025	-	802368
Peugeot	Expert	2.2 Bluehdi 150	Bus	Frontantrieb	Diesel	May 2025	-	802875
Peugeot	Expert	2.2 Bluehdi 180	Kasten	Frontantrieb	Diesel	May 2025	-	802365
Peugeot	Expert	2.2 Bluehdi 180	Bus	Frontantrieb	Diesel	May 2025	-	802367
Peugeot	Expert	E-expert	Bus	Frontantrieb	Elektro	Sep 2020	Oct 2023	144863
Peugeot	Expert	E-expert	Kasten	Frontantrieb	Elektro	Nov 2023	-	158217
Peugeot	Expert	E-expert	Bus	Frontantrieb	Elektro	Nov 2023	-	158218
Peugeot	Expert	E-expert	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2023	-	158220
Peugeot	Expert	E-expert 4X4	Kasten	Allrad	Elektro	Jan 2025	-	802666
Peugeot	Expert	E-expert Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Jan 2023	Sep 2024	152624
Peugeot	Expert	E-expert Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Oct 2024	-	801169
Peugeot	Ion	Electric	Schrägheck	Heckantrieb	Elektro	Jan 2011	-	112396
Peugeot	J7	1.5	Kasten	Frontantrieb	Benzin	Aug 1968	Jul 1970	14345
Peugeot	J7	1.6	Kasten	Frontantrieb	Benzin	Aug 1968	Mar 1980	14298
Peugeot	J7	1.6	Bus	Frontantrieb	Benzin	Aug 1968	Jul 1970	14337
Peugeot	J7	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	Aug 1968	Jul 1970	14343
Peugeot	J7	1.6	Bus	Frontantrieb	Benzin	Jul 1970	Mar 1980	14346
Peugeot	J7	1.6	Kasten	Frontantrieb	Benzin	Aug 1968	Mar 1980	14347
Peugeot	J7	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 1970	Mar 1980	14348
Peugeot	J7	1.8	Kasten	Frontantrieb	Benzin	Jul 1970	Mar 1980	14299
Peugeot	J7	1.8	Bus	Frontantrieb	Benzin	Jul 1970	Mar 1980	14336
Peugeot	J7	1.8	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 1970	Mar 1980	14344
Peugeot	J7	1.9 D	Kasten	Frontantrieb	Diesel	Aug 1968	Jul 1978	14300
Peugeot	J7	1.9 D	Bus	Frontantrieb	Diesel	Aug 1968	Jul 1978	14341
Peugeot	J7	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 1968	Jul 1978	14342
Peugeot	J7	2.1 D	Kasten	Frontantrieb	Diesel	Aug 1968	Jul 1977	14301
Peugeot	J7	2.1 D	Bus	Frontantrieb	Diesel	Aug 1968	Jul 1977	14334
Peugeot	J7	2.1 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 1968	Jul 1977	14339
Peugeot	J7	2.3 D	Bus	Frontantrieb	Diesel	Jul 1977	Mar 1980	14335
Peugeot	J7	2.3 D	Kasten	Frontantrieb	Diesel	Jul 1977	Mar 1980	14338
Peugeot	J7	2.3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1977	Mar 1980	14340
Peugeot	J9	1.6	Kasten	Frontantrieb	Benzin	Mar 1980	Jun 1987	14305
Peugeot	J9	2	Kasten	Frontantrieb	Benzin	Mar 1980	Jun 1987	14302
Peugeot	J9	2	Bus	Frontantrieb	Benzin	Mar 1980	Jun 1987	14349
Peugeot	J9	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Mar 1980	Jun 1987	14352
Peugeot	J9	2.1 D	Kasten	Frontantrieb	Diesel	Mar 1980	Jun 1987	14304
Peugeot	J9	2.3 D	Kasten	Frontantrieb	Diesel	Mar 1980	Jul 1982	14306
Peugeot	J9	2.3 D	Bus	Frontantrieb	Diesel	Mar 1980	Jul 1982	14350
Peugeot	J9	2.3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1980	Jul 1982	14353
Peugeot	J9	2.5 D	Kasten	Frontantrieb	Diesel	Jul 1982	Jun 1987	14303
Peugeot	J9	2.5 D	Bus	Frontantrieb	Diesel	Aug 1982	Jun 1987	14351
Peugeot	J9	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1982	Jun 1987	14354
Peugeot	Partner	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Apr 2010	-	11047
Peugeot	Partner	1.8	Großraumlimousine	Frontantrieb	Benzin	May 1997	Dec 2002	8706
Peugeot	Partner	1.4 Bifuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Apr 2003	Oct 2006	156842
Peugeot	Partner	1.4 CNG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Apr 2003	Oct 2006	17576
Peugeot	Partner	1.6 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	-	112373
Peugeot	Partner	1.6 Bluehdi 100 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Apr 2015	-	147437
Peugeot	Partner	1.6 Bluehdi 120	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	-	112374
Peugeot	Partner	1.6 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2009	-	12148
Peugeot	Partner	1.6 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2013	-	58890
Peugeot	Partner	1.6 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2011	-	111989
Peugeot	Partner	1.6 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2013	-	111990
Peugeot	Partner	1.6 HDI / Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2011	-	113674
Peugeot	Partner	1.6 HDI 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2009	-	12149
Peugeot	Partner	1.6 HDI 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Jul 2012	-	150723
Peugeot	Partner	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2010	-	11045
Peugeot	Partner	1.9 D	Großraumlimousine	Frontantrieb	Diesel	Jan 1999	Jul 2008	14434
Peugeot	Partner	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 1996	Dec 2015	18835
Peugeot	Partner	1.9 D 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Apr 2004	Jul 2011	18497
Peugeot	Partner	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Feb 2000	Jul 2008	14766
Peugeot	Partner	2.0 HDI 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Apr 2004	Aug 2005	18498
Peugeot	Partner	Électrique	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jun 2013	-	53379
Peugeot	Partner	E-partner	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jul 2021	-	145280
Peugeot	Partner	E-partner	Kasten/Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157798
Peugeot	Partner	E-partner 4X4	Kasten/Großraumlimousine	Allrad	Elektro	Jan 2025	-	801366
Peugeot	Partner tepee	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Dec 2014	-	112330
Peugeot	Partner tepee	1.6 Bluehdi 100 4X4	Großraumlimousine	Allrad	Diesel	Apr 2015	-	126060
Peugeot	Partner tepee	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	Dec 2014	-	112331
Peugeot	Partner tepee	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Aug 2010	-	33871
Peugeot	Partner tepee	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	-	58889
Peugeot	Partner tepee	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	-	108555
Peugeot	Partner tepee	1.6 HDI / Bluehdi 75	Großraumlimousine	Frontantrieb	Diesel	Jun 2008	Dec 2018	113673
Peugeot	Partner tepee	1.6 HDI 4X4	Großraumlimousine	Allrad	Diesel	Jul 2012	-	150582
Peugeot	Partner tepee	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	Apr 2010	-	11044
Peugeot	Partner tepee	1.6 HDI 90 4X4	Großraumlimousine	Allrad	Diesel	Jul 2012	-	147435
Peugeot	Partner tepee	1.6 VTI	Großraumlimousine	Frontantrieb	Benzin	Aug 2010	-	33870
Peugeot	Rcz	1.6 THP 270	Coupe	Frontantrieb	Benzin	Jun 2013	Dec 2015	52427
Peugeot	Rifter	E-rifter	Großraumlimousine	Frontantrieb	Elektro	Jul 2021	Oct 2023	145515
Peugeot	Rifter	E-rifter	Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157799
Peugeot	Traveller	2.2 Bluehdi 150	Bus	Frontantrieb	Diesel	May 2025	-	802874
Peugeot	Traveller	2.2 Bluehdi 180	Bus	Frontantrieb	Diesel	May 2025	-	802366
Peugeot	Traveller	E-traveller	Bus	Frontantrieb	Elektro	Nov 2023	-	158219
Piaggio	Ape	0.2	Pritsche/Fahrgestell	Heckantrieb	Gemisch	Jan 1971	Nov 1981	14755
Piaggio	Ape	0.2	Cabriolet	Heckantrieb	Benzin	Jan 2013	-	114014
Piaggio	Ape	0.2	Pritsche/Fahrgestell	Heckantrieb	Gemisch	Jan 2012	-	124238
Piaggio	Ape	500	Pritsche/Fahrgestell	Heckantrieb	Gemisch	Jan 1968	Dec 1978	803059
Piaggio	Ape	550	Pritsche/Fahrgestell	Heckantrieb	Gemisch	Jan 1967	Dec 1972	803058
Piaggio	Ape	600	Pritsche/Fahrgestell	Heckantrieb	Gemisch	Jan 1969	Dec 1978	803060
Piaggio	Ape	0.4 D	Kasten	Heckantrieb	Diesel	Aug 1993	Dec 1996	14792
Piaggio	M500	0.5 D	Schrägheck	Frontantrieb	Diesel	Jan 2004	-	18056
Piaggio	Porter	1	Kasten	Heckantrieb	Benzin	Feb 1993	May 1998	14758
Piaggio	Porter	1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Feb 1993	Jun 1994	18151
Piaggio	Porter	1	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jul 1994	-	18152
Piaggio	Porter	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2015	-	117797


--- Round 1 / 首次发送 ---
## 更新点

* 已复用 5 个跨批次 Expert 尺寸组，并为 Expert/Traveller 改款外廓、Partner/Rifter、J7/J9、RCZ 和 Piag([manualzz.com][1])([汽车数据网][2])([汽车数据网][3])修手册中的标准货台与厢式车身分别建组。([manualzz.com][4])([manualzz.com][1])用的历史缓存尺寸组。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：32
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108627	108627	MPV	II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	HIGH	Ktype未标注长度，采用标准L1H1外廓。	READY
109725	109725	Van	II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	HIGH	Ktype未标注长度，采用标准L1H1外廓。	READY
119828	119828	Pickup	II			EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	HIGH		READY
18278	18278	MPV	I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	HIGH		READY
802364	802364	Van	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	HIGH	Ktype未标注长度，采用标准M外廓。	READY
802368	802368	Pickup	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-PLATFORM-CAB-M-01	MEDIUM	按标准M转换底盘外廓映射。	READY
802875	802875	MPV	III facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
802365	802365	Van	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	HIGH	Ktype未标注长度，采用标准M外廓。	READY
802367	802367	MPV	III facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
144863	144863	MPV	III	K0		EU-PEUGEOT-EXPERT-III-K0-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
158217	158217	Van	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	HIGH	Ktype未标注长度，采用标准M外廓。	READY
158218	158218	MPV	III facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
158220	158220	Pickup	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-PLATFORM-CAB-M-01	MEDIUM	按标准M转换底盘外廓映射。	READY
802666	802666	Van	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	HIGH	四驱不改变标准M车身外廓。	READY
152624	152624	Van	III	K0		EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	HIGH	改款前氢燃料版本复用标准M H1外廓。	READY
801169	801169	Van	III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	HIGH	改款后氢燃料版本复用标准M外廓。	READY
112396	112396	Hatchback	I		5	EU-PEUGEOT-ION-I-HATCHBACK-01	HIGH		READY
14345	14345	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14298	14298	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14337	14337	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14343	14343	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14346	14346	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14347	14347	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14348	14348	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14299	14299	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14336	14336	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14344	14344	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14300	14300	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14341	14341	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14342	14342	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14301	14301	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14334	14334	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14339	14339	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14335	14335	MPV	J7			EU-PEUGEOT-J7-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14338	14338	Van	J7			EU-PEUGEOT-J7-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14340	14340	Pickup	J7			EU-PEUGEOT-J7-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14305	14305	Van	J9			EU-PEUGEOT-J9-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14302	14302	Van	J9			EU-PEUGEOT-J9-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14349	14349	MPV	J9			EU-PEUGEOT-J9-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14352	14352	Pickup	J9			EU-PEUGEOT-J9-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14304	14304	Van	J9			EU-PEUGEOT-J9-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14306	14306	Van	J9			EU-PEUGEOT-J9-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14350	14350	MPV	J9			EU-PEUGEOT-J9-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14353	14353	Pickup	J9			EU-PEUGEOT-J9-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14303	14303	Van	J9			EU-PEUGEOT-J9-VAN-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14351	14351	MPV	J9			EU-PEUGEOT-J9-BUS-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
14354	14354	Pickup	J9			EU-PEUGEOT-J9-PICKUP-01	MEDIUM	历史车型按输入车身类型采用标准量产外廓。	READY
11047	11047	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
8706	8706	MPV	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	HIGH		READY
156842	156842	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
17576	17576	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
112373	112373	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
147437	147437	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
112374	112374	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
12148	12148	Pickup	II			EU-PEUGEOT-PARTNER-II-PLATFORM-CAB-L1-01	HIGH	Ktype未标注长度，采用标准L1平台驾驶室外廓。	READY
58890	58890	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
111989	111989	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
111990	111990	Pickup	II			EU-PEUGEOT-PARTNER-II-PLATFORM-CAB-L1-01	HIGH	Ktype未标注长度，采用标准L1平台驾驶室外廓。	READY
113674	113674	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
12149	12149	Pickup	II			EU-PEUGEOT-PARTNER-II-PLATFORM-CAB-L1-01	HIGH	Ktype未标注长度，采用标准L1平台驾驶室外廓。	READY
150723	150723	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
11045	11045	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
14434	14434	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
18835	18835	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
18497	18497	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
14766	14766	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
18498	18498	Van	I	M49/M59		EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	MEDIUM	输入为混合封闭车身标签时按标准短轴外廓映射。	READY
53379	53379	Van	II			EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	HIGH	Ktype未标注长度，采用标准L1封闭车身外廓。	READY
145280	145280	Van	III	K9		EU-PEUGEOT-PARTNER-III-K9-STANDARD-M-01	HIGH	Ktype未标注长度，采用标准M封闭车身外廓。	READY
157798	157798	Van	III	K9		EU-PEUGEOT-PARTNER-III-K9-STANDARD-M-01	HIGH	Ktype未标注长度，采用标准M封闭车身外廓。	READY
801366	801366	Van	III	K9		EU-PEUGEOT-PARTNER-III-K9-STANDARD-M-01	HIGH	四驱不改变标准M封闭车身外廓。	READY
112330	112330	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
126060	126060	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
112331	112331	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
33871	33871	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
58889	58889	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
108555	108555	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
113673	113673	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
150582	150582	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
11044	11044	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
147435	147435	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
33870	33870	MPV	II			EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	HIGH	动力或四驱标签不改变标准Tepee L1外廓。	READY
52427	52427	Coupe	I	T75	2	EU-PEUGEOT-RCZ-I-T75-COUPE-R-01	HIGH		READY
145515	145515	MPV	I	K9		EU-PEUGEOT-RIFTER-I-K9-STANDARD-M-01	HIGH	采用改款前标准M外廓。	READY
157799	157799	MPV	I facelift	K9		EU-PEUGEOT-RIFTER-I-K9-FACELIFT-M-01	HIGH	改款后三维变化，单独建组。	READY
802874	802874	MPV	I facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
802366	802366	MPV	I facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
158219	158219	MPV	I facelift	K0		EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	HIGH	Ktype未标注长度，采用标准M乘用外廓。	READY
14755	14755	Pickup	historic			EU-PIAGGIO-APE-400R-HISTORIC-PICKUP-01	LOW	历史0.2车型按标准短货台外廓映射。	READY
114014	114014	Convertible	Calessino			EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	HIGH		READY
124238	124238	Pickup	TM	P703		EU-PIAGGIO-APE-TM-P703-STANDARD-DECK-01	HIGH	Ktype未标注货台长度，采用标准货台外廓。	READY
803059	803059	Pickup	500/550/600 series			EU-PIAGGIO-APE-500-600-VINTAGE-PICKUP-01	MEDIUM	同系列历史货运车型复用标准量产外廓。	READY
803058	803058	Pickup	500/550/600 series			EU-PIAGGIO-APE-500-600-VINTAGE-PICKUP-01	MEDIUM	同系列历史货运车型复用标准量产外廓。	READY
803060	803060	Pickup	500/550/600 series			EU-PIAGGIO-APE-500-600-VINTAGE-PICKUP-01	MEDIUM	同系列历史货运车型复用标准量产外廓。	READY
14792	14792	Van	TM			EU-PIAGGIO-APE-TM-DIESEL-VAN-01	HIGH		READY
18056	18056	Hatchback	I		3	EU-PIAGGIO-M500-I-HATCHBACK-01	HIGH		READY
14758	14758	Van	I			EU-PIAGGIO-PORTER-I-VAN-01	MEDIUM	采用第一代标准厢式外廓。	READY
18151	18151	Pickup	I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	MEDIUM	生产期变化未发现标准货台三维改变。	READY
18152	18152	Pickup	I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	MEDIUM	生产期变化未发现标准货台三维改变。	READY
117797	117797	Pickup	II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH	Ktype未标注货台长度，采用标准短货台外廓。	READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_13301-13400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940	Drom Peugeot Expert I catalog specification	https://www.drom.ru/catalog/peugeot/expert/235598/
EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	5016	1895	1942	Auto-Selection Jumpy/Expert II L2 platform-cab specification	https://www.auto-selection.com/fiche-technique/citroen/jumpy-plancb/2012/29-l2-hdi-125-fap-confort-1088647.php
EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	4813	1895	1942	CarsGuide Peugeot Expert 2011 dimensions	https://www.carsguide.com.au/peugeot/expert/car-dimensions/2011
EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	4959	1920	1940	Peugeot Australia Expert specifications	https://www.peugeot.com.au/models/expert-van/specifications.html
EU-PEUGEOT-EXPERT-III-K0-BUS-M-01	4959	1920	1890	Auto-Data Peugeot Traveller/Expert passenger specification	https://www.auto-data.net/en/peugeot-traveller-model-2304
EU-PEUGEOT-EXPERT-III-K0-FACELIFT-VAN-M-01	4981	1920	1904	Peugeot Expert 2024 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2024/05/Peugeot-Expert-2024-UK.pdf
EU-PEUGEOT-EXPERT-III-K0-FACELIFT-PLATFORM-CAB-M-01	4981	1920	1904	Peugeot Expert 2024 UK brochure, medium conversion-base envelope	https://autocatalogarchive.com/wp-content/uploads/2024/05/Peugeot-Expert-2024-UK.pdf
EU-PEUGEOT-EXPERT-TRAVELLER-K0-FACELIFT-BUS-M-01	4981	1920	1890	Peugeot E-Traveller technical brochure	https://www.simonbailes.co.uk/pdfs/peugeot-brochures/new-models/oct-25/E-Traveller.pdf
EU-PEUGEOT-ION-I-HATCHBACK-01	3475	1475	1610	Auto-Data Peugeot iOn generation specification	https://www.auto-data.net/en/peugeot-ion-generation-4391
EU-PEUGEOT-J7-VAN-01	4740	2000	2350	Kfz-Tech Peugeot J7 historical technical data	https://www.kfz-tech.de/Engl/Hersteller/Peugeot/PeugeotJ71965.htm
EU-PEUGEOT-J7-BUS-01	4740	2000	2350	Kfz-Tech Peugeot J7 historical technical data	https://www.kfz-tech.de/Engl/Hersteller/Peugeot/PeugeotJ71965.htm
EU-PEUGEOT-J7-PICKUP-01	4740	2000	2350	Kfz-Tech Peugeot J7 historical technical data	https://www.kfz-tech.de/Engl/Hersteller/Peugeot/PeugeotJ71965.htm
EU-PEUGEOT-J9-VAN-01	4732	2034	2300	Peugeot J9 historical model specification	https://en.wikipedia.org/wiki/Peugeot_J9
EU-PEUGEOT-J9-BUS-01	4732	2034	2300	Peugeot J9 historical model specification	https://en.wikipedia.org/wiki/Peugeot_J9
EU-PEUGEOT-J9-PICKUP-01	4732	2034	2300	Peugeot J9 historical model specification	https://en.wikipedia.org/wiki/Peugeot_J9
EU-PEUGEOT-PARTNER-I-M49-M59-STANDARD-01	4137	1724	1810	Drive.Place Peugeot Partner first-generation specification	https://peugeot.drive.place/partner/ii/group_furgon/604107
EU-PEUGEOT-PARTNER-II-STANDARD-L1-01	4380	1810	1805	Peugeot Partner 2009 owner manual dimensions	https://www.carmanualsonline.info/peugeot-partner-2009-owner-s-manual/?srch=dimensions
EU-PEUGEOT-PARTNER-II-PLATFORM-CAB-L1-01	4237	1810	1821	Peugeot Partner 2009 owner manual platform-cab dimensions	https://www.carmanualsonline.info/peugeot-partner-2009-owner-s-manual/?srch=dimensions
EU-PEUGEOT-PARTNER-II-TEPEE-L1-01	4380	1810	1803	Auto-Data Peugeot Partner II Tepee generation specification	https://www.auto-data.net/en/peugeot-partner-ii-tepee-generation-1274
EU-PEUGEOT-PARTNER-III-K9-STANDARD-M-01	4403	1848	1796	Peugeot e-Partner standard-body specification	https://www.loadsofvans.com/new-vans/peugeot-e-partner-electric
EU-PEUGEOT-RIFTER-I-K9-STANDARD-M-01	4403	1848	1878	Auto-Data Peugeot Rifter L1 specification	https://www.auto-data.net/en/peugeot-rifter-model-2386
EU-PEUGEOT-RIFTER-I-K9-FACELIFT-M-01	4405	1848	1818	Auto-Data Peugeot Rifter L1 facelift specification	https://www.auto-data.net/en/peugeot-rifter-model-2386
EU-PEUGEOT-RCZ-I-T75-COUPE-R-01	4290	1845	1352	CarsGuide Peugeot RCZ 2015 dimensions	https://www.carsguide.com.au/peugeot/rcz/car-dimensions/2015
EU-PIAGGIO-APE-400R-HISTORIC-PICKUP-01	2490	1260	1550	Piaggio Ape historical standard-deck specification	https://en.wikipedia.org/wiki/Piaggio_Ape
EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	2700	1335	1780	Piaggio Ape Calessino technical specification	https://www.scribd.com/document/802161098/Ape-Calessino-07-2016
EU-PIAGGIO-APE-TM-P703-STANDARD-DECK-01	3175	1480	1630	Piaggio Ape TM P703 workshop manual	https://manualzz.com/doc/23404734/piaggio-ape-tm-2012-workshop-manual
EU-PIAGGIO-APE-500-600-VINTAGE-PICKUP-01	3300	1460	1650	Vintage Piaggio Ape 500/600 series specification	https://customtuktuk.com/vintage-piaggio-ape-500-600-series/
EU-PIAGGIO-APE-TM-DIESEL-VAN-01	3210	1480	1780	Piaggio Ape TM workshop manual van dimensions	https://manualzz.com/doc/23404734/piaggio-ape-tm-2012-workshop-manual
EU-PIAGGIO-M500-I-HATCHBACK-01	2500	1400	1480	Automoto Piaggio M500 specification	https://www.automoto.it/catalogo/piaggio/m500/confort/96724
EU-PIAGGIO-PORTER-I-VAN-01	3370	1400	1870	Quattroruote Piaggio Porter 1.2 minivan archive	https://www.quattroruote.it/listino-archivio-trasporti/piaggio/porter-12-serie/porter-12-serie-minifurgoni
EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	3300	1400	1710	Quattroruote Piaggio Porter chassis/deck archive	https://www.quattroruote.it/listino-archivio-trasporti/piaggio/porter-12-serie/porter-12-serie-autotelaio-con-cassone
EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	3420	1395	1705	Piaggio Porter 2019 international brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_13301-13400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://manualzz.com/doc/23404734/piaggio-ape-tm-2012-workshop-manual?utm_source=chatgpt.com "Ape TM Benzina, Ape TM KAT, Ape TM P703 FL2 Service Station Manual | Manualzz"
[2]: https://www.auto-data.net/en/peugeot-rifter-model-2386 "https://www.auto-data.net/en/peugeot-rifter-model-2386"
[3]: https://www.auto-data.net/en/peugeot-rifter-model-2386?utm_source=chatgpt.com "Peugeot Rifter | Technical Specs, Fuel consumption ..."
[4]: https://manualzz.com/doc/23404734/piaggio-ape-tm-2012-workshop-manual "https://manualzz.com/doc/23404734/piaggio-ape-tm-2012-workshop-manual"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4975 行）
- 累计尺寸组：dimension_groups_final.tsv（1343 行）

