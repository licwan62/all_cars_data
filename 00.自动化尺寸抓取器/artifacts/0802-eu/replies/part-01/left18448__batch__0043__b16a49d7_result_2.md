# 任务：left18448 第 4201-4300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0043__b16a49d7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4201-4300 行

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
left18448 第 4201-4300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4201-4300_ktype_dimension_mapping_final.tsv
- left18448_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-DACIA-LOGAN-III-SEDAN-01	4396	1784	1501
EU-DACIA-LOGAN-II-SEDAN-FL-01	4358	1733	1517
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4347	1733	1517
EU-DACIA-LOGAN-II-WAGON-FL-01	4501	1733	1552
EU-DACIA-LOGAN-II-WAGON-PREFL-01	4492	1733	1550
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554
EU-DACIA-LOGAN-I-SEDAN-FL-01	4290	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525
EU-DACIA-LOGAN-I-VAN-01	4450	1740	1640
EU-DACIA-LOGAN-I-WAGON-FL-01	4473	1740	1662

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Dacia	Logan	TCE 90	Stufenheck	Frontantrieb	Benzin	Oct 2012	-	58612
Dacia	Logan	TCE 90	Kombi	Frontantrieb	Benzin	Feb 2013	-	59716
Dacia	Logan	TCE 90 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Sep 2015	-	118703
Dacia	Logan	TCE 90 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Sep 2015	-	124914
Dacia	Sandero	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2012	-	58134
Dacia	Sandero	1.2	Schrägheck	Frontantrieb	Benzin	May 2015	-	114214
Dacia	Sandero	1.0 SCE 65	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	145025
Dacia	Sandero	1.0 SCE 75	Schrägheck	Frontantrieb	Benzin	Dec 2016	Sep 2020	126214
Dacia	Sandero	1.0 TCE 100	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	145026
Dacia	Sandero	1.0 TCE 100 Eco-g	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2021	-	145027
Dacia	Sandero	1.0 TCE 110	Schrägheck	Frontantrieb	Benzin	Jul 2022	-	148078
Dacia	Sandero	1.0 TCE 90	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	145028
Dacia	Sandero	1.0 TCE LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2021	-	145029
Dacia	Sandero	1.2 16V LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2008	Jun 2013	11131
Dacia	Sandero	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Oct 2012	-	58142
Dacia	Sandero	1.2 TCE 120 Eco-g	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Dec 2025	-	802714
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Oct 2012	-	58144
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Nov 2008	Dec 2012	124722
Dacia	Sandero	1.5 DCI 75 / Blue DCI 75	Schrägheck	Frontantrieb	Diesel	Oct 2012	-	35269
Dacia	Sandero	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jul 2011	Dec 2012	59314
Dacia	Sandero	1.6 16V Bifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	Jan 2011	Dec 2012	12506
Dacia	Sandero	1.6 Hi-flex	Schrägheck	Frontantrieb	Benzin/Ethanol	Jun 2008	Dec 2012	124918
Dacia	Sandero	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2011	Dec 2012	119048
Dacia	Sandero	TCE 90	Schrägheck	Frontantrieb	Benzin	Oct 2012	-	58143
Dacia	Sandero	TCE 90 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Sep 2015	-	118704
Dacia	Spring	EV	Kasten/Schrägheck	Frontantrieb	Elektro	Dec 2024	-	801238
Dacia	Spring	EV	Schrägheck	Frontantrieb	Elektro	Oct 2025	-	802528
Dacia	Spring	Extreme	Schrägheck	Frontantrieb	Elektro	Dec 2022	-	152893
Dacia	Spring	Extreme	Schrägheck	Frontantrieb	Elektro	Oct 2025	-	802529
Daewoo	Espero	2	Stufenheck	Frontantrieb	Benzin	Oct 1991	Sep 1993	15652
Daewoo	Espero	2	Stufenheck	Frontantrieb	Benzin	Oct 1993	Sep 1994	15654
Daewoo	Espero	1.5 16V	Stufenheck	Frontantrieb	Benzin	Oct 1993	Sep 1994	15653
Daewoo	Evanda	2	Stufenheck	Frontantrieb	Benzin	Aug 2002	-	17168
Daewoo	Kalos	1.2	Schrägheck	Frontantrieb	Benzin	Apr 2003	-	17235
Daewoo	Kalos	1.4	Schrägheck	Frontantrieb	Benzin	Sep 2002	-	16986
Daewoo	Kalos	1.4 16V	Schrägheck	Frontantrieb	Benzin	Apr 2003	-	17236
Daewoo	Korando	2.3	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	-	11279
Daewoo	Korando	2.3	Geländewagen offen	Allrad	Benzin	Feb 1999	-	11285
Daewoo	Korando	2.0 16V	Geländewagen offen	Allrad	Benzin	Feb 1999	-	11882
Daewoo	Korando	2.9 D	Geländewagen geschlossen	Allrad	Diesel	Jan 1999	-	11281
Daewoo	Korando	2.9 TD	Geländewagen offen	Allrad	Diesel	Feb 1999	-	10169
Daewoo	Korando	2.9 TD	Geländewagen geschlossen	Allrad	Diesel	Jan 1999	-	11880
Daewoo	Korando	3.2 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	-	11280
Daewoo	Lacetti	1.4	Schrägheck	Frontantrieb	Benzin	Feb 2004	-	17580
Daewoo	Lacetti	1.4	Schrägheck	Frontantrieb	Benzin	Jun 2002	Dec 2004	122175
Daewoo	Lacetti	1.6	Schrägheck	Frontantrieb	Benzin	Feb 2004	-	17962
Daewoo	Lacetti	1.8	Schrägheck	Frontantrieb	Benzin	Feb 2004	-	17963
Daewoo	Lanos	1.5	Stufenheck	Frontantrieb	Benzin	Oct 1997	Jun 1999	54950
Daewoo	Lanos	1.6 16V	Stufenheck	Frontantrieb	Benzin	Feb 1997	-	14138
Daewoo	Leganza	2.2 16V	Stufenheck	Frontantrieb	Benzin	Apr 1999	Dec 2002	18629
Daewoo	Matiz	0.8	Schrägheck	Frontantrieb	Benzin	Sep 1998	-	10005
Daewoo	Matiz	1	Schrägheck	Frontantrieb	Benzin	Jan 2003	-	17234
Daewoo	Musso	2.3	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	-	11282
Daewoo	Musso	2.2 TD	Geländewagen geschlossen	Allrad	Diesel	Sep 1999	-	14508
Daewoo	Musso	2.9 D 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 1999	Sep 1999	11284
Daewoo	Musso	2.9 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 1999	-	14437
Daewoo	Musso	3.2 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 1999	-	11283
Daewoo	Nexia	1.8	Stufenheck	Frontantrieb	Benzin	Feb 1995	Jun 2008	110767
Daewoo	Nubira	1.6	Stufenheck	Frontantrieb	Benzin	Jul 2003	-	17237
Daewoo	Nubira	1.8	Stufenheck	Frontantrieb	Benzin	Jul 2003	-	17238
Daewoo	Nubira	1.6 16V	Schrägheck	Frontantrieb	Benzin	May 1997	May 1999	10781
Daewoo	Racer	1.5	Schrägheck	Frontantrieb	Benzin	Mar 1995	Dec 1997	110768
Daewoo	Rexton	2.9 TD	SUV	Allrad	Diesel	Apr 2002	-	16839
Daewoo	Rexton	3.2 V6	SUV	Allrad	Benzin	Apr 2002	-	16838
Daewoo	Rezzo	1.6	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	-	16517
Daewoo	Rezzo	1.8	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	-	14857
Daewoo	Rezzo	1.8	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	-	16515
Daewoo	Rezzo	2	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	-	14858
Daewoo	Rezzo	2	Großraumlimousine	Frontantrieb	Benzin	Sep 2001	Dec 2004	16518
DAF	400-Serie	428-435 2.5 D	Kasten	Heckantrieb	Diesel	Apr 1989	Aug 1993	14117
DAF	400-Serie	428-435 2.5 TD	Kasten	Heckantrieb	Diesel	Apr 1989	Aug 1993	14118
Daihatsu	Applause ii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jul 1997	May 2000	11862
Daihatsu	Charade iii	1.3	Stufenheck	Frontantrieb	Benzin	Nov 1990	Feb 1993	17423
Daihatsu	Charade iv	1	Schrägheck	Frontantrieb	Benzin	Sep 1994	Mar 1996	17425
Daihatsu	Charade viii	1.33 16V	Schrägheck	Frontantrieb	Benzin	May 2011	-	11732
Daihatsu	Copen	0.7	Cabriolet	Frontantrieb	Benzin	Sep 2003	Dec 2007	17468
Daihatsu	Copen	0.7	Cabriolet	Frontantrieb	Benzin	Sep 2003	Sep 2012	34827
Daihatsu	Cuore vi	1	Schrägheck	Frontantrieb	Benzin	May 2003	-	17325
Daihatsu	Extol	1.3	Bus	Heckantrieb	Benzin	Jul 2000	Nov 2011	18158
Daihatsu	Gran move	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	May 1998	-	10141
Daihatsu	Hijet	0.8	Kasten	Heckantrieb	Benzin	Jun 1986	Dec 1989	14126
Daihatsu	Hijet	0.8	Bus	Heckantrieb	Benzin	Jun 1986	Dec 1989	14129
Daihatsu	Hijet	1	Kasten	Heckantrieb	Benzin	Dec 1992	May 1998	10880
Daihatsu	Hijet	1	Kasten	Heckantrieb	Benzin	Jun 1986	Dec 1989	14127
Daihatsu	Hijet	1	Bus	Heckantrieb	Benzin	Jun 1986	Dec 1989	14128
Daihatsu	Hijet	1.0 I	Kasten	Heckantrieb	Benzin	Jul 1994	May 1998	10879
Daihatsu	Hijet	1.3 I 16V	Kasten	Heckantrieb	Benzin	May 1998	Oct 2005	14104
Daihatsu	Hijet	1.4 D	Kasten	Heckantrieb	Diesel	Mar 1998	Dec 2000	12500
Daihatsu	Move	1.0 I	Großraumlimousine	Frontantrieb	Benzin	Oct 1998	Sep 2002	11498
Daihatsu	Rocky hard top	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	May 1993	Dec 1998	5731
Daihatsu	Sirion	1	Schrägheck	Frontantrieb	Benzin	Jan 2005	Jun 2013	18482
Daihatsu	Sirion	1.3	Schrägheck	Frontantrieb	Benzin	Jan 2005	-	18483
Daihatsu	Sirion	1.0 I	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jan 2005	15537
Daihatsu	Sirion	1.0 I 4WD	Schrägheck	Allrad	Benzin	Apr 1999	Sep 2000	14412
Daihatsu	Sirion	1.0 I 4WD	Schrägheck	Allrad	Benzin	Sep 2000	Jan 2005	15538
Daihatsu	Sirion	1.3 Sport	Schrägheck	Frontantrieb	Benzin	Aug 2000	Jan 2005	15361
Daihatsu	Sirion	1.3 Sport 4WD	Schrägheck	Allrad	Benzin	Aug 2000	Mar 2005	15362
Daihatsu	Sparcar	0.8	Bus	Heckantrieb	Benzin	Sep 1983	May 1986	14122
Daihatsu	Sparcar	0.8	Kasten	Heckantrieb	Benzin	Sep 1983	May 1986	14124
Daihatsu	Sparcar	1	Bus	Heckantrieb	Benzin	Sep 1983	May 1986	14123


--- Round 1 / 首次发送 ---
## 更新点

已完成动力重复合并、历史尺寸组复用及独立外廓建组。Logan 复用既有尺寸组；Sandero、Spring、Matiz 按实际外廓变化分组；Korando 保留硬顶与敞篷边界；Hijet、Sparcar 按标准厢式车身闭合。老款厢式车型采用输入能够识别的标准量产外廓，不枚举无证据的轴距和车顶组合。([Auto Data][1])

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：42
* 已通过固定表头、唯一性、输入覆盖、映射引用闭合、正整数三维、来源非空和孤立组检查。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58612	58612	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-SEDAN-PREFL-01	HIGH		READY
59716	59716	Wagon	Logan II MCV	K8	5	EU-DACIA-LOGAN-II-WAGON-PREFL-01	HIGH		READY
118703	118703	Wagon	Logan II MCV	K8	5	EU-DACIA-LOGAN-II-WAGON-PREFL-01	HIGH		READY
124914	124914	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-SEDAN-PREFL-01	HIGH		READY
58134	58134	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
114214	114214	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
145025	145025	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
126214	126214	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
145026	145026	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145027	145027	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
148078	148078	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145028	145028	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145029	145029	Hatchback	Sandero III	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
11131	11131	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
58142	58142	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
802714	802714	Hatchback	Sandero III facelift 2025	BJI	5	EU-DACIA-SANDERO-III-HATCHBACK-FL2025-01	HIGH		READY
58144	58144	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
124722	124722	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
35269	35269	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
59314	59314	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
12506	12506	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
124918	124918	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
119048	119048	Hatchback	Sandero I	B90	5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
58143	58143	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
118704	118704	Hatchback	Sandero II	B52	5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH		READY
801238	801238	Van	Spring I facelift 2024		5	EU-DACIA-SPRING-I-HATCHBACK-FL2024-01	MEDIUM	Cargo classification; exterior envelope shared with the 2024 passenger body.	READY
802528	802528	Hatchback	Spring I facelift 2024		5	EU-DACIA-SPRING-I-HATCHBACK-FL2024-01	HIGH		READY
152893	152893	Hatchback	Spring I facelift 2022		5	EU-DACIA-SPRING-I-HATCHBACK-FL2022-01	HIGH		READY
802529	802529	Hatchback	Spring I facelift 2024		5	EU-DACIA-SPRING-I-HATCHBACK-FL2024-01	HIGH		READY
15652	15652	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-01	HIGH		READY
15654	15654	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-01	HIGH		READY
15653	15653	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-01	HIGH		READY
17168	17168	Sedan	Evanda		4	EU-DAEWOO-EVANDA-SEDAN-01	HIGH		READY
17235	17235	Hatchback	Kalos	T200	5	EU-DAEWOO-KALOS-T200-HATCHBACK-01	HIGH		READY
16986	16986	Hatchback	Kalos	T200	5	EU-DAEWOO-KALOS-T200-HATCHBACK-01	HIGH		READY
17236	17236	Hatchback	Kalos	T200	5	EU-DAEWOO-KALOS-T200-HATCHBACK-01	HIGH		READY
11279	11279	SUV	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-SUV-01	HIGH		READY
11285	11285	Convertible	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-01	HIGH		READY
11882	11882	Convertible	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-01	HIGH		READY
11281	11281	SUV	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-SUV-01	HIGH		READY
10169	10169	Convertible	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-01	HIGH		READY
11880	11880	SUV	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-SUV-01	HIGH		READY
11280	11280	SUV	Korando	KJ	3	EU-DAEWOO-KORANDO-KJ-SUV-01	HIGH		READY
17580	17580	Hatchback	Lacetti	J200	5	EU-DAEWOO-LACETTI-J200-HATCHBACK-01	HIGH		READY
122175	122175	Hatchback	Lacetti	J200	5	EU-DAEWOO-LACETTI-J200-HATCHBACK-01	HIGH		READY
17962	17962	Hatchback	Lacetti	J200	5	EU-DAEWOO-LACETTI-J200-HATCHBACK-01	HIGH		READY
17963	17963	Hatchback	Lacetti	J200	5	EU-DAEWOO-LACETTI-J200-HATCHBACK-01	HIGH		READY
54950	54950	Sedan	Lanos	KLAT	4	EU-DAEWOO-LANOS-KLAT-SEDAN-01	HIGH		READY
14138	14138	Sedan	Lanos	KLAT	4	EU-DAEWOO-LANOS-KLAT-SEDAN-01	HIGH		READY
18629	18629	Sedan	Leganza	KLAV	4	EU-DAEWOO-LEGANZA-KLAV-SEDAN-01	HIGH		READY
10005	10005	Hatchback	Matiz I	M100	5	EU-DAEWOO-MATIZ-M100-HATCHBACK-01	HIGH		READY
17234	17234	Hatchback	Matiz I facelift 2000	M150	5	EU-DAEWOO-MATIZ-M150-HATCHBACK-01	HIGH		READY
11282	11282	SUV	Musso	FJ	5	EU-DAEWOO-MUSSO-FJ-SUV-01	HIGH		READY
14508	14508	SUV	Musso	FJ	5	EU-DAEWOO-MUSSO-FJ-SUV-01	HIGH		READY
11284	11284	SUV	Musso	FJ	5	EU-DAEWOO-MUSSO-FJ-SUV-01	HIGH		READY
14437	14437	SUV	Musso	FJ	5	EU-DAEWOO-MUSSO-FJ-SUV-01	HIGH		READY
11283	11283	SUV	Musso	FJ	5	EU-DAEWOO-MUSSO-FJ-SUV-01	HIGH		READY
110767	110767	Sedan	Nexia	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-01	HIGH		READY
17237	17237	Sedan	Nubira III	J200	4	EU-DAEWOO-NUBIRA-III-SEDAN-01	HIGH		READY
17238	17238	Sedan	Nubira III	J200	4	EU-DAEWOO-NUBIRA-III-SEDAN-01	HIGH		READY
10781	10781	Hatchback	Nubira I	KLAJ	5	EU-DAEWOO-NUBIRA-KLAJ-HATCHBACK-01	HIGH		READY
110768	110768	Hatchback	Racer		5	EU-DAEWOO-RACER-HATCHBACK-01	HIGH		READY
16839	16839	SUV	Rexton I	Y200	5	EU-DAEWOO-REXTON-I-SUV-01	MEDIUM	Daewoo-badged Rexton uses the shared first-generation SsangYong exterior.	READY
16838	16838	SUV	Rexton I	Y200	5	EU-DAEWOO-REXTON-I-SUV-01	MEDIUM	Daewoo-badged Rexton uses the shared first-generation SsangYong exterior.	READY
16517	16517	MPV	Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
14857	14857	MPV	Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
16515	16515	MPV	Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
14858	14858	MPV	Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
16518	16518	MPV	Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
14117	14117	Van	400 Series			EU-DAF-400-SERIES-VAN-01	LOW	Generic 428-435 panel-van envelope; the Ktype does not identify wheelbase or roof branch.	READY
14118	14118	Van	400 Series			EU-DAF-400-SERIES-VAN-01	LOW	Generic 428-435 panel-van envelope; the Ktype does not identify wheelbase or roof branch.	READY
11862	11862	Hatchback	Applause II	A101	5	EU-DAIHATSU-APPLAUSE-II-HATCHBACK-01	HIGH		READY
17423	17423	Sedan	Charade III	G102	4	EU-DAIHATSU-CHARADE-III-SEDAN-01	HIGH		READY
17425	17425	Hatchback	Charade IV	G200	5	EU-DAIHATSU-CHARADE-IV-HATCHBACK-01	HIGH		READY
11732	11732	Hatchback	Charade VIII	XP9	5	EU-DAIHATSU-CHARADE-VIII-HATCHBACK-01	MEDIUM	European Charade VIII is the rebadged XP9 Toyota Yaris exterior.	READY
17468	17468	Convertible	Copen	L8	2	EU-DAIHATSU-COPEN-L8-CONVERTIBLE-01	HIGH		READY
34827	34827	Convertible	Copen	L8	2	EU-DAIHATSU-COPEN-L8-CONVERTIBLE-01	HIGH		READY
17325	17325	Hatchback	Cuore VI	L251	5	EU-DAIHATSU-CUORE-VI-L251-HATCHBACK-01	HIGH		READY
18158	18158	Van	Extol		5	EU-DAIHATSU-EXTOL-VAN-01	HIGH		READY
10141	10141	MPV	Gran Move I		5	EU-DAIHATSU-GRAN-MOVE-I-MPV-01	HIGH		READY
14126	14126	Van	Hijet S80	S80		EU-DAIHATSU-HIJET-S80-VAN-01	MEDIUM	Standard van roof selected; the Ktype has no low-roof marker.	READY
14129	14129	Van	Hijet S80	S80		EU-DAIHATSU-HIJET-S80-VAN-01	MEDIUM	Standard van roof selected; the Ktype has no low-roof marker.	READY
10880	10880	Van	Hijet S82/S85	S82/S85		EU-DAIHATSU-HIJET-S82-S85-VAN-01	MEDIUM	Standard van body selected; the Ktype has no wheelbase or roof branch.	READY
14127	14127	Van	Hijet S80	S80		EU-DAIHATSU-HIJET-S80-VAN-01	MEDIUM	Standard van roof selected; the Ktype has no low-roof marker.	READY
14128	14128	Van	Hijet S80	S80		EU-DAIHATSU-HIJET-S80-VAN-01	MEDIUM	Standard van roof selected; the Ktype has no low-roof marker.	READY
10879	10879	Van	Hijet S82/S85	S82/S85		EU-DAIHATSU-HIJET-S82-S85-VAN-01	MEDIUM	Standard van body selected; the Ktype has no wheelbase or roof branch.	READY
14104	14104	Van	Hijet / Porter			EU-DAIHATSU-HIJET-PORTER-VAN-01	MEDIUM		READY
12500	12500	Van	Hijet / Porter			EU-DAIHATSU-HIJET-PORTER-VAN-01	MEDIUM		READY
11498	11498	MPV	Move	L9	5	EU-DAIHATSU-MOVE-L9-MPV-01	HIGH		READY
5731	5731	SUV	Rocky	F7/F8	3	EU-DAIHATSU-ROCKY-F7-F8-SUV-01	HIGH		READY
18482	18482	Hatchback	Sirion II	M3	5	EU-DAIHATSU-SIRION-M2-HATCHBACK-01	HIGH		READY
18483	18483	Hatchback	Sirion II	M3	5	EU-DAIHATSU-SIRION-M2-HATCHBACK-01	HIGH		READY
15537	15537	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH		READY
14412	14412	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH		READY
15538	15538	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH		READY
15361	15361	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH		READY
15362	15362	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH		READY
14122	14122	Van	Sparcar / Hijet S70	S70		EU-DAIHATSU-SPARCAR-S70-VAN-01	MEDIUM	Standard van/minibus envelope; no separate roof branch is identified by the Ktype.	READY
14124	14124	Van	Sparcar / Hijet S70	S70		EU-DAIHATSU-SPARCAR-S70-VAN-01	MEDIUM	Standard van/minibus envelope; no separate roof branch is identified by the Ktype.	READY
14123	14123	Van	Sparcar / Hijet S70	S70		EU-DAIHATSU-SPARCAR-S70-VAN-01	MEDIUM	Standard van/minibus envelope; no separate roof branch is identified by the Ktype.	READY
```

[下载 left18448_4201-4300_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_4201-4300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4347	1733	1517	Auto-Data	https://www.auto-data.net/en/dacia-logan-ii-generation-3956
EU-DACIA-LOGAN-II-WAGON-PREFL-01	4492	1733	1550	Auto-Data	https://www.auto-data.net/en/dacia-logan-ii-mcv-generation-3958
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534	Auto-Data	https://www.auto-data.net/en/dacia-sandero-i-generation-3953
EU-DACIA-SANDERO-II-HATCHBACK-01	4057	1733	1523	Auto-Data	https://www.auto-data.net/en/dacia-sandero-ii-generation-3954
EU-DACIA-SANDERO-III-HATCHBACK-01	4088	1784	1499	Dacia technical specifications	https://media.dacia.com/wp-content/uploads/2022/07/08f707cf52f86dc7ae62ab61ff61071c-keeexed.pdf
EU-DACIA-SANDERO-III-HATCHBACK-FL2025-01	4102	1784	1496	Automobile-Catalog	https://www.automobile-catalog.com/car/2026/3569165/dacia_sandero_tce_100.html
EU-DACIA-SPRING-I-HATCHBACK-FL2022-01	3734	1579	1516	Auto-Data	https://www.auto-data.net/en/dacia-spring-facelift-2022-generation-9085
EU-DACIA-SPRING-I-HATCHBACK-FL2024-01	3701	1583	1519	Auto-Data	https://www.auto-data.net/en/dacia-spring-model-2829
EU-DAEWOO-ESPERO-KLEJ-SEDAN-01	4615	1718	1388	Auto-Data	https://www.auto-data.net/en/daewoo-espero-klej-2.0-i-105hp-16343
EU-DAEWOO-EVANDA-SEDAN-01	4770	1815	1440	Auto-Data	https://www.auto-data.net/en/daewoo-evanda-2.0-i-16v-131hp-16367
EU-DAEWOO-KALOS-T200-HATCHBACK-01	3880	1670	1495	Auto-Data	https://www.auto-data.net/en/daewoo-kalos-1.4-i-16v-94hp-16312
EU-DAEWOO-KORANDO-KJ-SUV-01	4330	1841	1840	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/3161570/ssangyong_daewoo_korando_e32.html
EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-01	4330	1841	1840	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/3161600/ssangyong_daewoo_korando_soft-top_2_9_turbo_diesel.html
EU-DAEWOO-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data	https://www.auto-data.net/en/daewoo-lacetti-generation-3672
EU-DAEWOO-LANOS-KLAT-SEDAN-01	4237	1678	1432	Auto-Data	https://www.auto-data.net/en/daewoo-lanos-klat-1.6-16v-106hp-17470
EU-DAEWOO-LEGANZA-KLAV-SEDAN-01	4671	1779	1437	Auto-Data	https://www.auto-data.net/en/daewoo-leganza-klav-2.2-133hp-16322
EU-DAEWOO-MATIZ-M100-HATCHBACK-01	3495	1495	1480	Auto-Data	https://www.auto-data.net/en/daewoo-matiz-i-0.8-i-52hp-16373
EU-DAEWOO-MATIZ-M150-HATCHBACK-01	3495	1495	1485	Auto-Data	https://www.auto-data.net/en/daewoo-matiz-i-facelift-2000-1.0-i-64hp-16372
EU-DAEWOO-MUSSO-FJ-SUV-01	4640	1864	1735	Auto-Data	https://www.auto-data.net/en/daewoo-musso-fj-generation-3643
EU-DAEWOO-NEXIA-KLETN-SEDAN-01	4482	1662	1394	Auto-Data	https://www.auto-data.net/en/daewoo-nexia-kletn-generation-3649
EU-DAEWOO-NUBIRA-III-SEDAN-01	4500	1725	1445	Auto-Data	https://www.auto-data.net/en/daewoo-nubira-iii-1.6-i-16v-110hp-16323
EU-DAEWOO-NUBIRA-KLAJ-HATCHBACK-01	4250	1700	1430	Auto-Data	https://www.auto-data.net/en/daewoo-nubira-hatchback-klaj-1.6-i-16v-106hp-16335
EU-DAEWOO-RACER-HATCHBACK-01	4158	1663	1360	Auto-Data	https://www.auto-data.net/en/daewoo-racer-hatchback-1.5-89hp-16375
EU-DAEWOO-REXTON-I-SUV-01	4720	1870	1760	Auto-Data	https://www.auto-data.net/en/ssangyong-rexton-i-rx-320-220hp-16029
EU-DAEWOO-REZZO-KLAU-MPV-01	4350	1755	1580	Auto-Data	https://www.auto-data.net/en/daewoo-rezzo-klau-generation-3644
EU-DAF-400-SERIES-VAN-01	4770	2260	2320	DAF 400 / LDV Convoy specifications	https://all-andorra.com/daf-400-ldv-convoy/
EU-DAIHATSU-APPLAUSE-II-HATCHBACK-01	4350	1660	1385	Auto-Data	https://www.auto-data.net/en/daihatsu-applause-ii-generation-9
EU-DAIHATSU-CHARADE-III-SEDAN-01	3995	1615	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/563720/daihatsu_charade_1_3_sg_sedan.html
EU-DAIHATSU-CHARADE-IV-HATCHBACK-01	3750	1620	1390	Automobile-Catalog	https://www.automobile-catalog.com/make/daihatsu/charade_4gen/charade_4gen_series_i_hatchback/1994.html
EU-DAIHATSU-CHARADE-VIII-HATCHBACK-01	3785	1695	1530	Engine in Detail	https://www.engineindetail.com/pa/daihatsu-charade-1-33-top-2011
EU-DAIHATSU-COPEN-L8-CONVERTIBLE-01	3395	1475	1245	Auto-Data	https://www.auto-data.net/en/daihatsu-copen-l8-generation-11
EU-DAIHATSU-CUORE-VI-L251-HATCHBACK-01	3410	1475	1500	Auto-Data	https://www.auto-data.net/en/daihatsu-cuore-l251-1.0-i-58hp-50
EU-DAIHATSU-EXTOL-VAN-01	3765	1515	1895	Auto-Data	https://www.auto-data.net/en/daihatsu-atrai-extol-generation-17
EU-DAIHATSU-GRAN-MOVE-I-MPV-01	4100	1640	1600	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Daihatsu/4839/Daihatsu-Grand-Move-16i.html
EU-DAIHATSU-HIJET-S80-VAN-01	3265	1395	1870	CarsGuide	https://www.carsguide.com.au/daihatsu/hi-jet/car-dimensions/1988
EU-DAIHATSU-HIJET-S82-S85-VAN-01	3295	1395	1870	Drive.Place	https://daihatsu.drive.place/hijet/viii/group_furgon/625461
EU-DAIHATSU-HIJET-PORTER-VAN-01	3370	1395	1870	VehicleScore	https://vehiclescore.co.uk/car-dimensions-check/daihatsu/hi%20jet
EU-DAIHATSU-MOVE-L9-MPV-01	3410	1475	1695	Auto-Data	https://www.auto-data.net/en/daihatsu-move-l9-1.0-i-12v-56hp-automatic-24534
EU-DAIHATSU-ROCKY-F7-F8-SUV-01	3840	1690	1850	Auto-Data	https://www.auto-data.net/en/daihatsu-rocky-hard-top-f7-f8-2.8-td-98hp-65
EU-DAIHATSU-SIRION-M2-HATCHBACK-01	3600	1665	1550	Auto-Data	https://www.auto-data.net/en/daihatsu-sirion-model-22
EU-DAIHATSU-SIRION-M1-HATCHBACK-01	3675	1595	1450	Auto-Data	https://www.auto-data.net/en/daihatsu-sirion-m1-generation-33
EU-DAIHATSU-SPARCAR-S70-VAN-01	3195	1395	1885	CarsGuide	https://www.carsguide.com.au/daihatsu/hi-jet/car-dimensions/1983
```

[下载 left18448_4201-4300_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_4201-4300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/daewoo-matiz-i-0.8-i-52hp-16373 "https://www.auto-data.net/en/daewoo-matiz-i-0.8-i-52hp-16373"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5016 行）
- 累计尺寸组：dimension_groups_final.tsv（1420 行）

