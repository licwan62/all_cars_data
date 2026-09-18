# 任务：left18448 第 11801-11900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0119__d39f8807


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11801-11900 行

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
left18448 第 11801-11900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11801-11900_ktype_dimension_mapping_final.tsv
- left18448_11801-11900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Nissan	Pathfinder iii	2.5 DCI 4WD	SUV	Allrad	Diesel	Jan 2005	Jan 2010	18506
Nissan	Pathfinder iii	2.5 DCI 4WD	SUV	Allrad	Diesel	Aug 2010	-	34757
Nissan	Pathfinder iii	2.5 DCI 4WD	SUV	Allrad	Diesel	Jan 2005	-	53614
Nissan	Pathfinder iii	3.0 DCI	SUV	Allrad	Diesel	Aug 2010	-	34758
Nissan	Pathfinder iii van	2.5 DCI 4X4	Kasten/SUV	Allrad	Diesel	Mar 2013	Aug 2014	143186
Nissan	Pathfinder iii van	3.0 DCI 4X4	Kasten/SUV	Allrad	Diesel	Mar 2013	Aug 2014	143187
Nissan	Pathfinder iv	3.5	SUV	Frontantrieb	Benzin	Oct 2013	-	108312
Nissan	Pathfinder iv	3.5 4WD	SUV	Allrad	Benzin	Sep 2012	-	58335
Nissan	Patrol gr iv	4.2 CAT	Geländewagen geschlossen	Allrad	Benzin	Nov 1988	Feb 1998	10739
Nissan	Patrol gr v wagon	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	Jun 1997	May 2000	9994
Nissan	Patrol gr v wagon	3.0 DTI	Geländewagen geschlossen	Allrad	Diesel	May 2000	-	14902
Nissan	Patrol iii/2 hardtop	2.8	Geländewagen geschlossen	Allrad	Benzin	May 1986	Jun 1990	10923
Nissan	Patrol iii/2 hardtop	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	May 1986	Jun 1990	11441
Nissan	Patrol iii/2 hardtop	3.3 D	Geländewagen geschlossen	Allrad	Diesel	Aug 1988	Jun 1990	8726
Nissan	Patrol vi	5.6	Geländewagen geschlossen	Allrad	Benzin	Apr 2010	-	34895
Nissan	Pick up	1.8	Pick-up	Heckantrieb	Benzin	Jan 1983	Mar 1986	10640
Nissan	Pick up	2.2 4WD	Pick-up	Allrad	Benzin	Apr 1983	Mar 1986	10641
Nissan	Pick up	2.3 D	Pick-up	Heckantrieb	Diesel	Apr 1983	Mar 1986	10642
Nissan	Pick up	2.4 I	Pick-up	Heckantrieb	Benzin	Feb 1998	Apr 2005	10016
Nissan	Pick up	2.4 I 4WD	Pick-up	Allrad	Benzin	Feb 1998	Nov 2001	10013
Nissan	Pick up	2.4 I 4WD	Pick-up	Allrad	Benzin	Mar 2002	Apr 2005	16775
Nissan	Pick up	2.5 D	Pick-up	Heckantrieb	Diesel	Feb 1998	Oct 2002	10014
Nissan	Pick up	2.5 D	Pick-up	Heckantrieb	Diesel	Aug 1992	Feb 1998	10021
Nissan	Pick up	2.5 D 4WD	Pick-up	Allrad	Diesel	Mar 1996	Feb 1998	10018
Nissan	Pick up	2.5 D 4WD	Pick-up	Allrad	Diesel	Aug 1987	Feb 1998	10022
Nissan	Pick up	2.5 D 4WD	Pick-up	Allrad	Diesel	Mar 1986	Aug 1991	10023
Nissan	Pick up	2.5 D 4WD	Pick-up	Allrad	Diesel	Apr 1983	Mar 1986	10644
Nissan	Pick up	2.5 DI	Pick-up	Heckantrieb	Diesel	Mar 2002	Dec 2012	17717
Nissan	Pick up	2.5 TD 4WD	Pick-up	Allrad	Diesel	May 1998	Nov 2001	10015
Nissan	Primastar	2	Bus	Frontantrieb	Benzin	Mar 2001	Aug 2006	16979
Nissan	Primastar	2	Kasten	Frontantrieb	Benzin	Feb 2003	-	17688
Nissan	Primastar	2	Kasten	Frontantrieb	Benzin	Apr 2006	-	126218
Nissan	Primastar	2	Bus	Frontantrieb	Benzin	Apr 2006	-	126219
Nissan	Primastar	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 2002	Aug 2006	126220
Nissan	Primastar	1.9 DCI 100	Kasten	Frontantrieb	Diesel	Sep 2002	-	17141
Nissan	Primastar	1.9 DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2002	Aug 2006	56196
Nissan	Primastar	1.9 DCI 80	Kasten	Frontantrieb	Diesel	Sep 2002	-	17140
Nissan	Primastar	2.0 DCI 110	Kasten	Frontantrieb	Diesel	Nov 2021	-	145773
Nissan	Primastar	2.0 DCI 110	Bus	Frontantrieb	Diesel	Nov 2021	-	148374
Nissan	Primastar	2.0 DCI 130	Kasten	Frontantrieb	Diesel	Nov 2021	-	145772
Nissan	Primastar	2.0 DCI 150	Kasten	Frontantrieb	Diesel	Nov 2021	-	145768
Nissan	Primastar	2.0 DCI 150	Bus	Frontantrieb	Diesel	Nov 2021	-	148375
Nissan	Primastar	2.0 DCI 170	Kasten	Frontantrieb	Diesel	Nov 2021	-	145770
Nissan	Primastar	2.0 DCI 170	Bus	Frontantrieb	Diesel	Nov 2021	-	148376
Nissan	Primastar	2.5 DCI 140	Kasten	Frontantrieb	Diesel	Jul 2003	-	17687
Nissan	Primastar	2.5 DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2006	-	126221
Nissan	Primastar	DCI 100	Bus	Frontantrieb	Diesel	Mar 2001	-	16981
Nissan	Primastar	DCI 140	Bus	Frontantrieb	Diesel	Jul 2003	-	17689
Nissan	Primastar	DCI 80	Bus	Frontantrieb	Diesel	Mar 2001	-	16980
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	Mar 2002	Aug 2008	16591
Nissan	Primera	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2002	Aug 2008	16921
Nissan	Primera	1.8	Schrägheck	Frontantrieb	Benzin	Jul 2002	Oct 2008	16922
Nissan	Primera	2	Schrägheck	Frontantrieb	Benzin	Jul 2002	Oct 2008	16923
Nissan	Primera	1.6 16V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Oct 2000	7851
Nissan	Primera	1.6 16V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Dec 2001	7852
Nissan	Primera	1.6 16V	Schrägheck	Frontantrieb	Benzin	Sep 1996	Jul 2002	7857
Nissan	Primera	1.6 16V	Schrägheck	Frontantrieb	Benzin	Sep 1996	Jul 2002	7858
Nissan	Primera	1.6 16V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jul 2002	16106
Nissan	Primera	1.6 16V	Stufenheck	Frontantrieb	Benzin	Jun 1996	Dec 2001	16107
Nissan	Primera	1.8 16V	Stufenheck	Frontantrieb	Benzin	Aug 1999	Dec 2001	13670
Nissan	Primera	1.8 16V	Schrägheck	Frontantrieb	Benzin	Aug 1999	Jul 2002	13671
Nissan	Primera	1.8 16V	Kombi	Frontantrieb	Benzin	Aug 1999	Dec 2001	13672
Nissan	Primera	1.8 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Aug 1999	Dec 2001	148233
Nissan	Primera	1.9 DCI	Stufenheck	Frontantrieb	Diesel	Apr 2003	Oct 2007	17536
Nissan	Primera	1.9 DCI	Schrägheck	Frontantrieb	Diesel	Apr 2003	Oct 2007	17538
Nissan	Primera	1.9 DCI	Kombi	Frontantrieb	Diesel	Apr 2003	-	17539
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Dec 2001	7853
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Dec 2001	7854
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Dec 2001	7855
Nissan	Primera	2.0 16V	Schrägheck	Frontantrieb	Benzin	Sep 1996	Jul 2002	7859
Nissan	Primera	2.0 16V	Schrägheck	Frontantrieb	Benzin	Sep 1996	Jul 2002	7860
Nissan	Primera	2.0 16V	Schrägheck	Frontantrieb	Benzin	Sep 1996	Jul 2002	7861
Nissan	Primera	2.0 16V	Schrägheck	Frontantrieb	Benzin	Aug 1999	Jul 2002	13739
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	Aug 1999	Dec 2001	13740
Nissan	Primera	2.0 16V	Kombi	Frontantrieb	Benzin	Aug 1999	Dec 2001	13741
Nissan	Primera	2.0 TD	Stufenheck	Frontantrieb	Diesel	Sep 1996	Dec 2001	7856
Nissan	Primera	2.0 TD	Schrägheck	Frontantrieb	Diesel	Sep 1996	Jul 2002	7862
Nissan	Primera	2.2 DCI	Kombi	Frontantrieb	Diesel	Apr 2003	-	17540
Nissan	Primera	2.2 DCI	Stufenheck	Frontantrieb	Diesel	Apr 2003	Apr 2006	17541
Nissan	Primera	2.2 DCI	Schrägheck	Frontantrieb	Diesel	Apr 2003	-	17543
Nissan	Primera	2.2 DI	Schrägheck	Frontantrieb	Diesel	Jul 2002	May 2007	16924
Nissan	Pulsar	1.2 Dig-t	Schrägheck	Frontantrieb	Benzin	Oct 2014	-	107484
Nissan	Pulsar	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Oct 2014	-	107485
Nissan	Pulsar	1.6 Dig-t	Schrägheck	Frontantrieb	Benzin	Feb 2015	-	109967
Nissan	Qashqai +2	1.6	SUV	Frontantrieb	Benzin	Feb 2007	Dec 2013	801368
Nissan	Qashqai +2	1.6	SUV	Frontantrieb	Benzin	Feb 2010	Nov 2013	801369
Nissan	Qashqai +2	2	SUV	Frontantrieb	Benzin	Aug 2008	Apr 2014	801384
Nissan	Qashqai +2	1.5 DCI	SUV	Frontantrieb	Diesel	Aug 2008	Jan 2010	801385
Nissan	Qashqai +2	1.5 DCI	SUV	Frontantrieb	Diesel	Aug 2008	Nov 2013	801387
Nissan	Qashqai +2	1.5 DCI	SUV	Frontantrieb	Diesel	Feb 2010	Nov 2013	801388
Nissan	Qashqai +2	1.6 DCI	SUV	Frontantrieb	Diesel	Jul 2011	Nov 2013	801389
Nissan	Qashqai +2	1.6 DCI Allrad	SUV	Allrad	Diesel	Jul 2011	Nov 2013	801390
Nissan	Qashqai +2	2.0 Allrad	SUV	Allrad	Benzin	Aug 2008	Apr 2014	801381
Nissan	Qashqai +2	2.0 DCI	SUV	Frontantrieb	Diesel	Aug 2008	Nov 2013	801392
Nissan	Qashqai +2	2.0 DCI Allrad	SUV	Allrad	Diesel	Aug 2008	Nov 2013	801391
Nissan	Qashqai +2 van	2	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Nov 2013	801395
Nissan	Qashqai +2 van	1.5 DCI	Kasten/SUV	Frontantrieb	Diesel	Mar 2013	Nov 2013	801397
Nissan	Qashqai +2 van	1.6 Cvtc	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Nov 2013	801394
Nissan	Qashqai +2 van	1.6 DCI	Kasten/SUV	Frontantrieb	Diesel	Mar 2013	Nov 2013	801398
Nissan	Qashqai +2 van	1.6 DCI Allrad	Kasten/SUV	Allrad	Diesel	Mar 2013	Nov 2013	801400


--- Round 1 / 首次发送 ---
## 更新点

已完成 100 个输入 Ktype 的聚类、尺寸组复用及机械终检。对 9 个明确跨越且三维发生变化的改款 Ktype 使用 `_prefl/_facelift` 拆分，包括 Pathfinder R51、Patrol Y61/Y62 和 Qashqai+2 NJ10；未因发动机、能源或驱动形式重复建组。相关代际资料确认这些改款存在实际外廓变化。([汽车数据][1])

Primastar X83 采用 Nissan UK 资料中的 SWB Low 标准外廓；2021 年起 X82 使用 Nissan UK L1H1 数据，其中车身宽 1956 mm、含镜宽 2283 mm，尺寸表采用不含镜宽度。([Dezo's Garage][2])

## 进度

输入 Ktype：**100/100**
最终映射行：**109**
DIMENSION_GROUP：**23**
READY：**109**
PENDING：**0**
引用闭合、ID 唯一、三维及来源非空检查：**通过**

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18506	18506	SUV	Pathfinder III	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-PREFL-01	HIGH		READY
34757	34757	SUV	Pathfinder III facelift	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	HIGH		READY
53614_prefl	53614	SUV	Pathfinder III	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
53614_facelift	53614	SUV	Pathfinder III facelift	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
34758	34758	SUV	Pathfinder III facelift	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	HIGH		READY
143186	143186	Van	Pathfinder III facelift	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	HIGH	Commercial conversion retains the R51 exterior envelope.	READY
143187	143187	Van	Pathfinder III facelift	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	HIGH	Commercial conversion retains the R51 exterior envelope.	READY
108312	108312	SUV	Pathfinder IV	R52	5	EU-NISSAN-PATHFINDER-R52-SUV-STANDARD-01	HIGH		READY
58335	58335	SUV	Pathfinder IV	R52	5	EU-NISSAN-PATHFINDER-R52-SUV-STANDARD-01	HIGH		READY
10739	10739	SUV	Patrol IV	Y60	5	EU-NISSAN-PATROL-Y60-SUV-5DR-01	MEDIUM	Body variant is not stated; the standard five-door wagon exterior is used.	READY
9994	9994	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-Y61-SUV-PREFL-01	HIGH		READY
14902_prefl	14902	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-Y61-SUV-PREFL-01	MEDIUM	Catalog span crosses the wider 2004 facelift; split by physical exterior.	READY
14902_facelift	14902	SUV	Patrol V facelift	Y61	5	EU-NISSAN-PATROL-Y61-SUV-FACELIFT-01	MEDIUM	Catalog span crosses the wider 2004 facelift; split by physical exterior.	READY
10923	10923	SUV	Patrol III/2 Hardtop	K260	3	EU-NISSAN-PATROL-K260-SUV-HARDTOP-01	HIGH		READY
11441	11441	SUV	Patrol III/2 Hardtop	K260	3	EU-NISSAN-PATROL-K260-SUV-HARDTOP-01	HIGH		READY
8726	8726	SUV	Patrol III/2 Hardtop	K260	3	EU-NISSAN-PATROL-K260-SUV-HARDTOP-01	HIGH		READY
34895_prefl	34895	SUV	Patrol VI	Y62	5	EU-NISSAN-PATROL-Y62-SUV-PREFL-01	MEDIUM	Catalog span crosses the dimension-changing 2014 facelift; split by physical exterior.	READY
34895_facelift	34895	SUV	Patrol VI facelift	Y62	5	EU-NISSAN-PATROL-Y62-SUV-FACELIFT-01	MEDIUM	Catalog span crosses the dimension-changing 2014 facelift; split by physical exterior.	READY
10640	10640	Pickup	Pick Up 720	720		EU-NISSAN-PICKUP-720-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10641	10641	Pickup	Pick Up 720	720		EU-NISSAN-PICKUP-720-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10642	10642	Pickup	Pick Up 720	720		EU-NISSAN-PICKUP-720-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10016	10016	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10013	10013	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
16775	16775	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10014	10014	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10021	10021	Pickup	Pick Up D21	D21		EU-NISSAN-PICKUP-D21-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10018	10018	Pickup	Pick Up D21	D21		EU-NISSAN-PICKUP-D21-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10022	10022	Pickup	Pick Up D21	D21		EU-NISSAN-PICKUP-D21-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10023	10023	Pickup	Pick Up D21	D21		EU-NISSAN-PICKUP-D21-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10644	10644	Pickup	Pick Up 720	720		EU-NISSAN-PICKUP-720-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
17717	17717	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
10015	10015	Pickup	Pick Up D22	D22		EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	LOW	Cab and bed branch are not identified; a standard production exterior is retained.	READY
16979	16979	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
17688	17688	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
126218	126218	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
126219	126219	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
126220	126220	Pickup	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	LOW	No chassis or bed branch is identified; the X83 SWB low-roof standard envelope is used.	READY
17141	17141	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
56196	56196	Pickup	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	LOW	No chassis or bed branch is identified; the X83 SWB low-roof standard envelope is used.	READY
17140	17140	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
145773	145773	Van	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
148374	148374	MPV	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
145772	145772	Van	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
145768	145768	Van	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
148375	148375	MPV	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
145770	145770	Van	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
148376	148376	MPV	Primastar II	X82		EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	MEDIUM	No L1/L2 branch is identified; the L1H1 standard exterior is used.	READY
17687	17687	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
126221	126221	Pickup	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	LOW	No chassis or bed branch is identified; the X83 SWB low-roof standard envelope is used.	READY
16981	16981	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
17689	17689	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
16980	16980	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	MEDIUM	No wheelbase or roof branch is identified; the X83 SWB low-roof standard exterior is used.	READY
16591	16591	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-STANDARD-01	HIGH		READY
16921	16921	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
16922	16922	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
16923	16923	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
7851	7851	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7852	7852	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7857	7857	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
7858	7858	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
16106	16106	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
16107	16107	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
13670	13670	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
13671	13671	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
13672	13672	Wagon	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-WAGON-STANDARD-01	HIGH		READY
148233	148233	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
17536	17536	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-STANDARD-01	HIGH		READY
17538	17538	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
17539	17539	Wagon	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-WAGON-STANDARD-01	HIGH		READY
7853	7853	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7854	7854	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7855	7855	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7859	7859	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
7860	7860	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
7861	7861	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
13739	13739	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
13740	13740	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
13741	13741	Wagon	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-WAGON-STANDARD-01	HIGH		READY
7856	7856	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	HIGH		READY
7862	7862	Hatchback	Primera P11	P11	5	EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	HIGH		READY
17540	17540	Wagon	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-WAGON-STANDARD-01	HIGH		READY
17541	17541	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-STANDARD-01	HIGH		READY
17543	17543	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
16924	16924	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	HIGH		READY
107484	107484	Hatchback	Pulsar C13	C13	5	EU-NISSAN-PULSAR-C13-HATCHBACK-STANDARD-01	HIGH		READY
107485	107485	Hatchback	Pulsar C13	C13	5	EU-NISSAN-PULSAR-C13-HATCHBACK-STANDARD-01	HIGH		READY
109967	109967	Hatchback	Pulsar C13	C13	5	EU-NISSAN-PULSAR-C13-HATCHBACK-STANDARD-01	HIGH		READY
801368_prefl	801368	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801368_facelift	801368	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801369	801369	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH		READY
801384_prefl	801384	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801384_facelift	801384	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801385	801385	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	HIGH		READY
801387_prefl	801387	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801387_facelift	801387	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801388	801388	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH		READY
801389	801389	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH		READY
801390	801390	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH		READY
801381_prefl	801381	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801381_facelift	801381	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801392_prefl	801392	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801392_facelift	801392	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801391_prefl	801391	SUV	Qashqai+2 I	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801391_facelift	801391	SUV	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	MEDIUM	Catalog span crosses a dimension-changing facelift; split by physical exterior.	READY
801395	801395	Van	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH	Commercial conversion retains the NJ10 exterior envelope.	READY
801397	801397	Van	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH	Commercial conversion retains the NJ10 exterior envelope.	READY
801394	801394	Van	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH	Commercial conversion retains the NJ10 exterior envelope.	READY
801398	801398	Van	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH	Commercial conversion retains the NJ10 exterior envelope.	READY
801400	801400	Van	Qashqai+2 I facelift	NJ10	5	EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	HIGH	Commercial conversion retains the NJ10 exterior envelope.	READY
```

[下载 left18448_11801-11900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_11801-11900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-PATHFINDER-R51-SUV-PREFL-01	4877	1854	1879	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-iii-generation-278
EU-NISSAN-PATHFINDER-R51-SUV-FACELIFT-01	4813	1848	1858	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-iii-facelift-2010-generation-3815
EU-NISSAN-PATHFINDER-R52-SUV-STANDARD-01	5009	1961	1768	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-iv-generation-7235
EU-NISSAN-PATROL-Y60-SUV-5DR-01	4920	1930	1790	Auto-Data	https://www.auto-data.net/en/nissan-patrol-iv-5-door-y60-generation-8355
EU-NISSAN-PATROL-Y61-SUV-PREFL-01	4965	1840	1855	Auto-Data	https://www.auto-data.net/en/nissan-patrol-v-5-door-y61-generation-83
EU-NISSAN-PATROL-Y61-SUV-FACELIFT-01	5080	1940	1855	Auto-Data	https://www.auto-data.net/en/nissan-patrol-v-5-door-y61-facelift-2004-generation-8287
EU-NISSAN-PATROL-K260-SUV-HARDTOP-01	4105	1690	1840	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/2307185/nissan_patrol_hardtop_2800_diesel_ebro.html
EU-NISSAN-PATROL-Y62-SUV-PREFL-01	5140	1995	1940	Auto-Data	https://www.auto-data.net/en/nissan-patrol-vi-y62-generation-8285
EU-NISSAN-PATROL-Y62-SUV-FACELIFT-01	5165	1995	1940	Auto-Data	https://www.auto-data.net/en/nissan-patrol-vi-y62-facelift-2014-generation-6313
EU-NISSAN-PICKUP-720-PICKUP-STANDARD-01	4690	1660	1530	Nissan Heritage Collection	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Pickup_Long_Body_Deluxe.html
EU-NISSAN-PICKUP-D21-PICKUP-STANDARD-01	4690	1690	1725	Auto-Data	https://www.auto-data.net/en/nissan-datsun-d21-2.0-4wd-91hp-540
EU-NISSAN-PICKUP-D22-PICKUP-STANDARD-01	5180	1825	1715	Auto-Data	https://www.auto-data.net/en/nissan-pick-up-d22-generation-101
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOW-01	4782	1904	1955	Nissan UK brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X82-VAN-L1H1-01	5080	1956	1971	Nissan UK technical information	https://www.nissan.co.uk/vehicles/new-vehicles/primastar/technical-information.html
EU-NISSAN-PRIMERA-P11-SEDAN-STANDARD-01	4522	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-p11-generation-183
EU-NISSAN-PRIMERA-P11-HATCHBACK-STANDARD-01	4522	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-hatch-p11-generation-184
EU-NISSAN-PRIMERA-P11-WAGON-STANDARD-01	4579	1715	1450	Auto-Data	https://www.auto-data.net/en/nissan-primera-wagon-p11-generation-185
EU-NISSAN-PRIMERA-P12-SEDAN-STANDARD-01	4567	1760	1480	Auto-Data	https://www.auto-data.net/en/nissan-primera-p12-generation-180
EU-NISSAN-PRIMERA-P12-HATCHBACK-STANDARD-01	4565	1760	1480	Auto-Data	https://www.auto-data.net/en/nissan-primera-hatch-p12-generation-181
EU-NISSAN-PRIMERA-P12-WAGON-STANDARD-01	4675	1760	1480	Auto-Data	https://www.auto-data.net/en/nissan-primera-wagon-p12-generation-182
EU-NISSAN-PULSAR-C13-HATCHBACK-STANDARD-01	4387	1768	1520	Auto-Data	https://www.auto-data.net/en/nissan-pulsar-c13-generation-4592
EU-NISSAN-QASHQAI2-NJ10-SUV-PREFL-01	4530	1780	1645	Auto-Data	https://www.auto-data.net/en/nissan-qashqai-2-i-nj10-generation-210
EU-NISSAN-QASHQAI2-NJ10-SUV-FACELIFT-01	4541	1780	1645	Auto-Data	https://www.auto-data.net/en/nissan-qashqai-2-i-nj10-facelift-2010-generation-3813
```

[下载 left18448_11801-11900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_11801-11900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/nissan-pathfinder-iii-generation-278?utm_source=chatgpt.com "Nissan Pathfinder III | Technical Specs, Fuel consumption, Dimensions"
[2]: https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf "Primastar_PT.indd"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3240 行）
- 累计尺寸组：dimension_groups_final.tsv（993 行）

