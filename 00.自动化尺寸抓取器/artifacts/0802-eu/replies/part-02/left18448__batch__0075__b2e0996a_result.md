# 任务：left18448 第 7401-7500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0075__b2e0996a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7401-7500 行

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
left18448 第 7401-7500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7401-7500_ktype_dimension_mapping_final.tsv
- left18448_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-IVECO-DAILY-IV-CHASSISCAB-29L-3000-01	5014	1996	2225
EU-IVECO-DAILY-IV-CHASSISCAB-29L-3450-01	5899	1996	2220
EU-IVECO-DAILY-IV-CHASSISCAB-35C-3000-01	5334	1996	2285
EU-IVECO-DAILY-IV-CHASSISCAB-35C-3450-01	5899	1996	2280
EU-IVECO-DAILY-IV-CHASSISCAB-35C-3750-01	6509	1996	2275
EU-IVECO-DAILY-IV-CHASSISCAB-35C-4100-01	6909	1996	2270
EU-IVECO-DAILY-IV-CHASSISCAB-35S-3000-01	5014	1996	2245
EU-IVECO-DAILY-IV-CHASSISCAB-35S-3450-01	5899	1996	2240
EU-IVECO-DAILY-IV-CHASSISCAB-35S-3750-01	6509	1996	2225
EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3450-01	5928	1996	2280
EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	6538	1996	2275
EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-4350-01	7358	1996	2270
EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-4750-01	8223	1996	2280
EU-IVECO-DAILY-IV-CHASSISCAB-4X4-3050-01	4921	2016	2606
EU-IVECO-DAILY-IV-CHASSISCAB-4X4-3400-01	5432	2016	2597
EU-IVECO-DAILY-IV-CHASSISCAB-60C-3450-01	5905	2060	2340
EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	6515	2060	2335
EU-IVECO-DAILY-IV-CHASSISCAB-60C-4350-01	7340	2060	2330
EU-IVECO-DAILY-IV-CHASSISCAB-60C-4750-01	8200	2060	2325
EU-IVECO-DAILY-IV-CREWCAB-35C-3450-01	5899	1996	2300
EU-IVECO-DAILY-IV-CREWCAB-35C-3750-01	6509	1996	2300
EU-IVECO-DAILY-IV-CREWCAB-35C-4100-01	6909	1996	2290
EU-IVECO-DAILY-IV-CREWCAB-35S-3450-01	5014	1996	2245
EU-IVECO-DAILY-IV-CREWCAB-45C50C-3450-01	5928	1996	2295
EU-IVECO-DAILY-IV-CREWCAB-45C50C-3750-01	6538	1996	2290
EU-IVECO-DAILY-IV-CREWCAB-45C50C-4350-01	7358	1996	2280
EU-IVECO-DAILY-IV-CREWCAB-4X4-3400-01	5432	2016	2629
EU-IVECO-DAILY-IV-CREWCAB-60C-3750-01	6515	2060	2275
EU-IVECO-DAILY-IV-CREWCAB-60C-4350-01	7340	2060	2270
EU-IVECO-DAILY-IV-VAN-29L-5077-LOWROOF-01	5077	1996	2260
EU-IVECO-DAILY-IV-VAN-29L-5077-MIDROOF-01	5077	1996	2635
EU-IVECO-DAILY-IV-VAN-29L-5477-LOWROOF-01	5477	1996	2260
EU-IVECO-DAILY-IV-VAN-29L-5477-MIDROOF-01	5477	1996	2635
EU-IVECO-DAILY-IV-VAN-29L-5997-MIDROOF-01	5997	1996	2630
EU-IVECO-DAILY-IV-VAN-35C-5997-HIGHROOF-01	5997	1996	2815
EU-IVECO-DAILY-IV-VAN-35C-5997-MIDROOF-01	5997	1996	2760
EU-IVECO-DAILY-IV-VAN-35C-7012-HIGHROOF-01	7012	1996	2820
EU-IVECO-DAILY-IV-VAN-35C-7012-MIDROOF-01	7012	1996	2750
EU-IVECO-DAILY-IV-VAN-35S-5077-LOWROOF-01	5077	1996	2270
EU-IVECO-DAILY-IV-VAN-35S-5077-MIDROOF-01	5077	1996	2645
EU-IVECO-DAILY-IV-VAN-35S-5477-LOWROOF-01	5477	1996	2270
EU-IVECO-DAILY-IV-VAN-35S-5477-MIDROOF-01	5477	1996	2645
EU-IVECO-DAILY-IV-VAN-35S-5997-HIGHROOF-01	5997	1996	2825
EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	5997	1996	2640
EU-IVECO-DAILY-IV-VAN-35S-7012-HIGHROOF-01	7012	1996	2860
EU-IVECO-DAILY-IV-VAN-35S-7012-MIDROOF-01	7012	1996	2670
EU-IVECO-DAILY-IV-VAN-50C-5477-LOWROOF-01	5477	1996	2270
EU-IVECO-DAILY-IV-VAN-50C-5997-MIDROOF-01	5997	1996	2745
EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	7012	1996	2930
EU-IVECO-DAILY-IV-VAN-50C-7012-MIDROOF-01	7012	1996	2745
EU-IVECO-DAILY-IV-VAN-60C-7012-HIGHROOF-01	7012	2080	3025

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Iveco	Daily iv	60c17 V, 60c17 V/P	Kasten	Heckantrieb	Diesel	Jul 2007	Aug 2011	34458
Iveco	Daily iv	60c17, 60c17 /P	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2007	Aug 2011	34501
Iveco	Daily iv	60c18	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2006	Aug 2011	34285
Iveco	Daily iv	60c18	Kasten	Heckantrieb	Diesel	May 2006	Aug 2011	34320
Iveco	Daily iv	65c14 G, 65c14 G/p, 65c14 GD, 65c14 Gd/p	Pritsche/Fahrgestell	Heckantrieb	CNG	Jul 2007	Aug 2011	34490
Iveco	Daily iv	65c14 V, 65c14 V/P	Kasten	Heckantrieb	Diesel	Sep 2009	Aug 2011	34464
Iveco	Daily iv	65c14, 65c14 /P	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2009	Aug 2011	34494
Iveco	Daily iv	65c15	Kasten	Heckantrieb	Diesel	May 2006	Aug 2011	34321
Iveco	Daily iv	65c15, 65c15 /P, 65c15 D, 65c15 D/P	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2006	Aug 2011	34302
Iveco	Daily iv	65c17 V, 65c17 V/P	Kasten	Heckantrieb	Diesel	Jul 2007	Aug 2011	34463
Iveco	Daily iv	65c17, 65c17 /P	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2007	Aug 2011	34492
Iveco	Daily iv	65c18	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2006	Aug 2011	34286
Iveco	Daily iv	65c18	Kasten	Heckantrieb	Diesel	May 2006	Aug 2011	34322
Iveco	Daily iv	70c14 V, 70c14 V/P	Kasten	Heckantrieb	Diesel	Sep 2009	Aug 2011	34467
Iveco	Daily iv	70c14, 70c14 /P	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2009	Aug 2011	34486
Iveco	Daily iv	70c15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2008	Aug 2011	59784
Iveco	Daily iv	70c17, 70c17p	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2009	Aug 2011	34487
Iveco	Daily iv	70c17v, 70c17 V/P	Kasten	Heckantrieb	Diesel	Jul 2007	Aug 2011	34468
Iveco	Daily v	26l11, 29l11, 29s11, 35c11d, 35s11, 40c11	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	56431
Iveco	Daily v	29l15 V, 35s15 V, 35c15l V, 40c15l V, 50c15l V	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	57763
Iveco	Daily v	29l15, 35s15, 35c15, 40c15, 50c15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	108241
Iveco	Daily v	29s11, 29l11, 35c11, 35s11, 40c11	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	57760
Iveco	Daily v	29s13, 29l13, 29l13d, 35s13, 35c13d, 40c13	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	56433
Iveco	Daily v	29s13, 29l13, 35c13, 35s13, 40c13, 40s13	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	57761
Iveco	Daily v	35c15 V, 40c15 V, 45c15 V, 50c15 V, 60c15 V,65c15 V	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	57779
Iveco	Daily v	35c15, 35s15, 40c15, 45c15, 50c15, 60c15, 65c15, 70c15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	56556
Iveco	Daily v	35c17, 35s17, 40c17, 45c17, 50c17, 60c17, 65c17, 70c17	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	56557
Iveco	Daily v	35c17, 35s17, 40c17, 45c17, 50c17, 60c17, 65c17, 70c17	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	56697
Iveco	Daily v	35c21 V, 35s21 V, 40c21 V, 45c21 V, 50c21 V	Kasten	Heckantrieb	Diesel	Sep 2011	Feb 2014	57775
Iveco	Daily v	35c21, 35s21, 40c21, 45c21, 50c21, 60c21, 65c21, 70c21	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Feb 2014	56586
Iveco	Daily v	35s17, 40c17, 45c17, 50c17	Bus	Heckantrieb	Diesel	Sep 2011	Feb 2014	146505
Iveco	Daily v	35s60e Electric	Kasten	Heckantrieb	Elektro	Sep 2011	Feb 2014	111528
Iveco	Daily v	50c15	Bus	Heckantrieb	Diesel	Sep 2011	Feb 2014	146507
Iveco	Daily v	50c80e Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Sep 2011	Feb 2014	106485
Iveco	Daily v	Naturalpower 50c14	Bus	Heckantrieb	CNG	Sep 2011	Feb 2014	146506
Iveco	Daily vi	33s11, 35s11, 35c11	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	Jul 2021	107420
Iveco	Daily vi	33s11, 35s11, 35c11	Kasten	Heckantrieb	Diesel	Mar 2014	Jul 2021	107440
Iveco	Daily vi	33s12, 35s12, 35c12	Kasten	Heckantrieb	Diesel	Apr 2016	-	119876
Iveco	Daily vi	33s12, 35s12, 35c12	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2016	-	119889
Iveco	Daily vi	33s13, 35s13, 35c13	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	-	107421
Iveco	Daily vi	33s13, 35s13, 35c13	Kasten	Heckantrieb	Diesel	Mar 2014	-	107441
Iveco	Daily vi	33s14, 35s14, 35c14, 38s14	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2016	-	119890
Iveco	Daily vi	33s14, 35s14, 35c14, 42s14	Kasten	Heckantrieb	Diesel	Apr 2016	-	119877
Iveco	Daily vi	33s15, 35s15, 35c15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	-	107438
Iveco	Daily vi	33s15, 35s15, 35c15	Kasten	Heckantrieb	Diesel	Mar 2014	-	107442
Iveco	Daily vi	33s16, 35s16, 35c16, 38s16, 40c16, 42s16, 50c16	Kasten	Heckantrieb	Diesel	Apr 2016	-	119878
Iveco	Daily vi	33s16, 35s16, 35c16, 40c16, 42s16, 50c16	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2016	-	119891
Iveco	Daily vi	35c21, 35s21, 40c21, 42s21, 50c21, 60c21, 65c21, 70c21	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2021	-	151066
Iveco	Daily vi	35c21, 35s21, 40c21, 50c21, 60c21, 65c21, 70c21	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2019	-	146291
Iveco	Daily vi	35s14, 35s15, 35c15, 40s14, 40c15, 50c15, 60c5, 65c15,...	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	-	107422
Iveco	Daily vi	35s15, 35c15, 40c15, 45c15, 50c15, 65c15, 70c15	Kasten	Heckantrieb	Diesel	Mar 2014	-	107444
Iveco	Daily vi	35s15, 35c15, 40c15, 50c15, 60c15, 65c15, 70c15	Kasten	Heckantrieb	Diesel	Apr 2016	-	119880
Iveco	Daily vi	35s15, 35c15, 40c15, 50c15, 60c15, 65c15, 70c15	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2016	-	119892
Iveco	Daily vi	35s15, 55s15, 70s15, 70c15	Pritsche/Fahrgestell	Allrad	Diesel	Mar 2014	-	146292
Iveco	Daily vi	35s16, 35c16, 40c16, 42s16, 50c16, 60c16, 65c16, 70c16	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2019	-	146293
Iveco	Daily vi	35s16, 35c16, 40c16, 50c16, 70c16	Kasten	Heckantrieb	Diesel	Jul 2021	-	151064
Iveco	Daily vi	35s17, 35c17, 40c17, 45s17,45c17, 50c17, 60c17, 65c17,...	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	-	107424
Iveco	Daily vi	35s17, 35c17, 40c17, 50c17, 55c17, 60c17, 65c17, 70c17	Kasten	Heckantrieb	Diesel	Mar 2014	-	107445
Iveco	Daily vi	35s17, 55s17 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Mar 2014	-	116128
Iveco	Daily vi	35s18, 35c18, 40c18, 42s18, 50c18, 60c18, 65c18, 70c18	Kasten	Heckantrieb	Diesel	Jul 2021	-	151068
Iveco	Daily vi	35s18, 35c18, 40c18, 45c18, 50c18, 60c18, 65c18, 70c18	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2016	-	119893
Iveco	Daily vi	35s18, 35c18, 40c18, 50c18, 60c18, 65c18, 70c18	Kasten	Heckantrieb	Diesel	Apr 2016	-	119881
Iveco	Daily vi	35s18, 35c18, 55c18, 55s18, 70c18, 70s18	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2022	-	153735
Iveco	Daily vi	35s18, 42s18, 35c18, 38s18, 40c18, 50c18, 60c18, 65c18,...	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2021	-	151069
Iveco	Daily vi	35s18, 55s18, 55c18, 70s18, 70c18 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Apr 2016	-	126004
Iveco	Daily vi	35s21, 35c21, 40c21, 42s21, 50c21, 60c21, 65c21, 70c21	Kasten	Heckantrieb	Diesel	Jul 2021	-	151065
Iveco	Daily vi	35s21, 35c21, 40c21, 45c21, 50c21, 60c21, 65c21, 70c21	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2014	-	107426
Iveco	Daily vi	35s21, 35c21, 40c21, 50c21	Kasten	Heckantrieb	Diesel	Mar 2014	-	107446
Iveco	Daily vi	35s21, 35c21, 40c21, 50c21, 60c21, 65c21, 70c21	Kasten	Heckantrieb	Diesel	Apr 2019	-	146290
Iveco	Daily vi	35s60e	Kasten	Heckantrieb	Elektro	Oct 2015	-	127609
Iveco	Daily vi	35s60e, 35c60e	Pritsche/Fahrgestell	Heckantrieb	Elektro	Oct 2015	-	127615
Iveco	Daily vi	40c15, 50c15, 60c15	Bus	Heckantrieb	Diesel	Mar 2014	-	114562
Iveco	Daily vi	40c15, 50c15, 60c15	Bus	Heckantrieb	Diesel	Apr 2016	-	127646
Iveco	Daily vi	40c17, 50c17, 60c17	Bus	Heckantrieb	Diesel	Mar 2014	-	114563
Iveco	Daily vi	40c18, 50c18, 60c18	Bus	Heckantrieb	Diesel	Apr 2016	-	127648
Iveco	Daily vi	45c80e, 50c80e	Pritsche/Fahrgestell	Heckantrieb	Elektro	Oct 2015	-	127618
Iveco	Daily vi	50c16	Bus	Heckantrieb	Diesel	Apr 2019	-	146294
Iveco	Daily vi	50c18, 60c18	Bus	Heckantrieb	Diesel	Jul 2021	-	151070
Iveco	Daily vi	50c21, 60c21	Bus	Heckantrieb	Diesel	Apr 2019	-	146296
Iveco	Daily vi	50c21, 60c21	Bus	Heckantrieb	Diesel	Jul 2021	-	151067
Iveco	Daily vi	50c80e	Bus	Heckantrieb	Elektro	Apr 2016	-	119901
Iveco	Daily vi	50c80e	Kasten	Heckantrieb	Elektro	Oct 2015	-	127611
Iveco	Daily vi	55s18, 55c18, 70s18, 70c18	Kasten	Allrad	Diesel	Jan 2018	-	146289
Iveco	Daily vi	55s18, 55c18, 70s18, 70c18	Kasten	Allrad	Diesel	Jun 2022	-	153734
Iveco	Daily vi	Edaily 35s10e, 38s10e, 42s10e	Kasten	Heckantrieb	Elektro	Dec 2022	-	153919
Iveco	Daily vi	Edaily 35s10e, 42s10e	Pritsche/Fahrgestell	Heckantrieb	Elektro	Dec 2022	-	153918
Iveco	Daily vi	Edaily 35s14e, 38s, 42s, 42c, 50c, 60c, 72C	Kasten	Heckantrieb	Elektro	Dec 2022	-	153897
Iveco	Daily vi	Edaily 35s14e, 38s, 42s, 42c, 50c, 60c, 72C	Pritsche/Fahrgestell	Heckantrieb	Elektro	Dec 2022	-	153901
Iveco	Daily vi	Edaily 72c14e	Bus	Heckantrieb	Elektro	Dec 2022	-	800835
Iveco	Daily vi	Naturalpower 35s14, 35c, 38s, 40c, 50c, 60c, 65c, 70C	Pritsche/Fahrgestell	Heckantrieb	CNG	Mar 2014	-	107431
Iveco	Daily vi	Naturalpower 35s14, 35c, 38s, 40c, 50c, 60c, 65c, 70C	Kasten	Heckantrieb	CNG	Mar 2014	-	107447
Iveco	Daily vi	Naturalpower 40c14, 50c14, 60c14	Bus	Heckantrieb	CNG	Mar 2014	-	119900
Iveco	Ejolly	J31f10le	Kasten	Frontantrieb	Elektro	Feb 2026	-	164137
Iveco	Ejolly	J31f10se	Kasten	Frontantrieb	Elektro	Feb 2026	-	164136
Iveco	Emoovy	35f16e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jul 2025	-	164271
Iveco	Esuperjolly	J35f20e	Kasten	Frontantrieb	Elektro	Nov 2025	-	164105
Iveco	Esuperjolly	J42f20e	Kasten	Frontantrieb	Elektro	Nov 2025	-	164106
Iveco	Power daily	39.15, 42.15, 50.15	Kasten	Heckantrieb	Diesel	Dec 2007	-	145566
Iveco	Power daily	A39.15, A42.15, A50.15	Bus	Heckantrieb	Diesel	Dec 2007	-	145567
JAC	E30x	EV	Schrägheck	Frontantrieb	Elektro	Mar 2025	-	801444


--- Round 1 / 首次发送 ---
## 更新点

* 完成当前 100 个 Ktype 的聚类、尺寸组复用和映射闭合。
* Daily IV/V 对三维完全一致的历史尺寸组直接复用；Daily IV 重型厢式车查得 `7012×1996×3025 mm`，与累计表中宽度为 `2080 mm` 的组冲突，因此未覆盖旧组，创建了序号为 `02` 的新尺寸组。
* Daily VI 的标准厢式车、重型厢式车、底盘驾驶室、Minibus 和 4×4 分支已分别闭合。([CarsGuide][1])
* eJolly、eMoovy、eSuperJolly、Power Daily 和 JAC E30X 的新增外廓已闭合。([IVECO][2])

## 当前批次进度

* 输入 Ktype：100
* `READY`：100
* `PENDING`：0
* 被引用尺寸组：18
* 孤立尺寸组：0
* 固定表头、列数、`id` 唯一性、尺寸组唯一性、引用闭合、正整数三维、来源和文件链接检查均已通过。

## 最终完整 Ktype 映射表

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34458	34458	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34501	34501	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34285	34285	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34320	34320	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34490	34490	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34464	34464	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34494	34494	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34321	34321	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34302	34302	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34463	34463	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34492	34492	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34286	34286	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34322	34322	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34467	34467	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
34486	34486	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
59784	59784	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34487	34487	Pickup	Daily IV			EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	MEDIUM	Ktype omits wheelbase; standard 3750 mm chassis-cab exterior selected.	READY
34468	34468	Van	Daily IV			EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	MEDIUM	Ktype omits roof/body length; standard 7012 mm H3 heavy-van exterior selected; 1996 mm body-width branch used.	READY
56431	56431	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-35C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
57763	57763	Van	Daily V			EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
108241	108241	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-35C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
57760	57760	Van	Daily V			EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
56433	56433	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-35C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
57761	57761	Van	Daily V			EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
57779	57779	Van	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
56556	56556	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
56557	56557	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
56697	56697	Van	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
57775	57775	Van	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
56586	56586	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
146505	146505	Bus	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
111528	111528	Van	Daily V			EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
146507	146507	Bus	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
106485	106485	Pickup	Daily V			EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	MEDIUM	2011 facelift retained the same outer body; standard 3750 mm chassis branch selected.	READY
146506	146506	Bus	Daily V			EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	MEDIUM	2011 facelift retained the same outer body; standard production van exterior selected.	READY
107420	107420	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107440	107440	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
119876	119876	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
119889	119889	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107421	107421	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107441	107441	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
119890	119890	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
119877	119877	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
107438	107438	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107442	107442	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
119878	119878	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
119891	119891	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
151066	151066	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
146291	146291	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107422	107422	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107444	107444	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
119880	119880	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
119892	119892	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
146292	146292	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-4X4-3780-01	MEDIUM	Standard 3780 mm single-cab 4x4 exterior selected.	READY
146293	146293	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
151064	151064	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
107424	107424	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107445	107445	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
116128	116128	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-4X4-3780-01	MEDIUM	Standard 3780 mm single-cab 4x4 exterior selected.	READY
151068	151068	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
119893	119893	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
119881	119881	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
153735	153735	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-4X4-3780-01	MEDIUM	Standard 3780 mm single-cab 4x4 exterior selected.	READY
151069	151069	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
126004	126004	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-4X4-3780-01	MEDIUM	Standard 3780 mm single-cab 4x4 exterior selected.	READY
151065	151065	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
107426	107426	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107446	107446	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
146290	146290	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
127609	127609	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
127615	127615	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
114562	114562	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
127646	127646	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
114563	114563	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
127648	127648	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
127618	127618	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
146294	146294	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
151070	151070	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
146296	146296	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
151067	151067	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
119901	119901	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
127611	127611	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
146289	146289	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-4X4-4100-H3-01	LOW	Ktype omits body length; standard 4100 mm H3 heavy-van exterior used as the 4x4 representative.	READY
153734	153734	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-4X4-4100-H3-01	LOW	Ktype omits body length; standard 4100 mm H3 heavy-van exterior used as the 4x4 representative.	READY
153919	153919	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 van exterior selected.	READY
153918	153918	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
153897	153897	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
153901	153901	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
800835	800835	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
107431	107431	Pickup	Daily VI			EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	MEDIUM	Ktype omits wheelbase/cab; standard 3750 mm single-cab chassis exterior selected.	READY
107447	107447	Van	Daily VI			EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	MEDIUM	Ktype omits wheelbase/roof; standard 3520L H2 heavy-van exterior selected.	READY
119900	119900	Bus	Daily VI			EU-IVECO-DAILY-VI-BUS-4100L-H2-01	MEDIUM	Powertrain does not change the outer shell; standard 4100 mm minibus exterior selected.	READY
164137	164137	Van	eJolly I			EU-IVECO-EJOLLY-I-VAN-LONG-01	HIGH	LE suffix mapped to the official long-body line.	READY
164136	164136	Van	eJolly I			EU-IVECO-EJOLLY-I-VAN-SHORT-01	HIGH	SE suffix mapped to the official short-body line.	READY
164271	164271	Pickup	eMoovy I			EU-IVECO-EMOOVY-I-CHASSISCAB-STANDARD-01	HIGH	Official chassis-cab exterior.	READY
164105	164105	Van	eSuperJolly I			EU-IVECO-ESUPERJOLLY-I-VAN-5998-H1-01	MEDIUM	GVW code does not change the body; standard 13 m3 configuration selected.	READY
164106	164106	Van	eSuperJolly I			EU-IVECO-ESUPERJOLLY-I-VAN-5998-H1-01	MEDIUM	GVW code does not change the body; standard 13 m3 configuration selected.	READY
145566	145566	Van	Power Daily I			EU-IVECO-POWER-DAILY-I-VANBUS-LWB-HIGHROOF-01	LOW	Aggregated 39/42/50 codes; A50 LWB high-roof production exterior selected.	READY
145567	145567	Bus	Power Daily I			EU-IVECO-POWER-DAILY-I-VANBUS-LWB-HIGHROOF-01	LOW	Aggregated 39/42/50 codes; A50 LWB high-roof production exterior selected.	READY
801444	801444	Hatchback	E30X I		5	EU-JAC-E30X-I-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载 left18448_7401-7500_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_7401-7500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP 表

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-IV-CHASSISCAB-60C-3750-01	6515	2060	2335	IVECO 70C15/E4 technical specification	https://aaa-iveco.com/images/products/daily/Iveco-70C15-E4.pdf
EU-IVECO-DAILY-IV-VAN-65C70C-7012-HIGHROOF-02	7012	1996	3025	CarsGuide Iveco Daily 2010 dimensions	https://www.carsguide.com.au/iveco/daily/car-dimensions/2010
EU-IVECO-DAILY-IV-CHASSISCAB-35C-3750-01	6509	1996	2275	IVECO Daily official price list and dimensions	https://www.iv-service.ru/uploads/Price%20IVECO%20Daily.pdf
EU-IVECO-DAILY-IV-CHASSISCAB-45C50C-3750-01	6538	1996	2275	IVECO Daily official price list and dimensions	https://www.iv-service.ru/uploads/Price%20IVECO%20Daily.pdf
EU-IVECO-DAILY-IV-VAN-35S-5997-MIDROOF-01	5997	1996	2640	CarsGuide Iveco Daily 2012 dimensions	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012
EU-IVECO-DAILY-IV-VAN-50C-7012-HIGHROOF-01	7012	1996	2930	CarsGuide Iveco Daily 2012 dimensions	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012
EU-IVECO-DAILY-VI-VAN-35S-3520L-H2-01	6087	2052	2660	IVECO Daily E6 Van specification	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/E6-Daily-Van-Spec-Sheet.pdf?rev=81436cbddcd64654b968cad8f4a35e23
EU-IVECO-DAILY-VI-VAN-50C-3520L-H2-01	6109	2052	2748	IVECO Daily E6 Van specification	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/E6-Daily-Van-Spec-Sheet.pdf?rev=81436cbddcd64654b968cad8f4a35e23
EU-IVECO-DAILY-VI-CHASSISCAB-50C-3750-01	6593	2052	2264	IVECO Daily E6 Cab Chassis specification	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/E6-Daily-Cab-Chassis-Spec-Sheet.pdf?rev=c8ef861a2d4e4331b74f8d8958731418
EU-IVECO-DAILY-VI-BUS-4100L-H2-01	7618	2052	2831	IVECO Bus eDaily Minibus technical datasheet	https://www.ivecobus.com/czech/-/media/IvecoBus/International/pdf/schede-tecniche/daily/eDaily-Line.pdf?rev=-1
EU-IVECO-DAILY-VI-CHASSISCAB-4X4-3780-01	5853	2056	2506	IVECO Daily 4x4 specification	https://www.iveco.com/au/-/media/IVECOdotcom/Australia/Products/Daily/July-24/Daily-4x4-Spec-Sheet---Web-Version.pdf?rev=1add957e98ed4b84b89376713d864d92
EU-IVECO-DAILY-VI-VAN-4X4-4100-H3-01	7264	2052	3041	Van Reviewer Iveco Daily 70C dimensions	https://vanreviewer.co.uk/iveco/daily/70c/dimensions/10348/
EU-IVECO-EJOLLY-I-VAN-SHORT-01	4980	1920	1895	IVECO eJolly official product page and brochure	https://www.iveco.com/uk/eJolly/eJolly
EU-IVECO-EJOLLY-I-VAN-LONG-01	5330	1920	1935	IVECO eJolly official product page and brochure	https://www.iveco.com/uk/eJolly/eJolly
EU-IVECO-EMOOVY-I-CHASSISCAB-STANDARD-01	5320	1995	2005	IVECO eMoovy official brochure	https://www.iveco.com/uk/-/media/IVECOdotcom/Content/Products/eMoovy/Brochure/BTS-L2434701MASTER_Brochure_IVECO_eMoovy_Digital_RGB.pdf?rev=-1
EU-IVECO-ESUPERJOLLY-I-VAN-5998-H1-01	5998	2050	2612	IVECO eSuperJolly brochure + Van Reviewer body width	https://www.iveco.com/uk/-/media/IVECOdotcom/Content/Products/eJolly/brochure/brochure_eSuperJolly_en.pdf?rev=-1 ; https://vanreviewer.co.uk/iveco/esuperjolly/dimensions/8121/
EU-IVECO-POWER-DAILY-I-VANBUS-LWB-HIGHROOF-01	7133	2000	2875	IVECO Power Daily A50.13 technical documentation	https://www.scribd.com/document/585599401/Power-Daily-MINIBUS-A50-13-ENGLISH
EU-JAC-E30X-I-HATCHBACK-STANDARD-01	4025	1770	1560	JAC E30X official specification	https://jacen.jac.com.cn/pdf/E30X.pdf
```

[下载 left18448_7401-7500_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_7401-7500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carsguide.com.au/iveco/daily/car-dimensions/2010 "https://www.carsguide.com.au/iveco/daily/car-dimensions/2010"
[2]: https://www.iveco.com/uk/-/media/IVECOdotcom/Content/Products/eJolly/brochure/brochure_eJolly_en.pdf?rev=-1 "https://www.iveco.com/uk/-/media/IVECOdotcom/Content/Products/eJolly/brochure/brochure_eJolly_en.pdf?rev=-1"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5042 行）
- 累计尺寸组：dimension_groups_final.tsv（1342 行）

