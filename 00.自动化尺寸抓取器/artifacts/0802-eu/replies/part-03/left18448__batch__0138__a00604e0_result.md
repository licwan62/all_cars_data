# 任务：left18448 第 13701-13800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0138__a00604e0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13701-13800 行

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
left18448 第 13701-13800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13701-13800_ktype_dimension_mapping_final.tsv
- left18448_13701-13800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	4963	1966	1379
EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	4974	1967	1409
EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	4974	1966	1409
EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	4963	1966	1390

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Porsche	Taycan	4S Performance Battery Plus	Kombi	Allrad	Elektro	Nov 2023	-	157972
Porsche	Taycan	4S Performance Battery Plus	Stufenheck	Allrad	Elektro	Nov 2023	-	157978
Porsche	Taycan	Electric	Kombi	Heckantrieb	Elektro	Aug 2021	Dec 2023	153383
Porsche	Taycan	GTS	Kombi	Allrad	Elektro	Aug 2021	Dec 2023	146969
Porsche	Taycan	GTS	Stufenheck	Allrad	Elektro	May 2019	Dec 2023	147377
Porsche	Taycan	GTS	Stufenheck	Allrad	Elektro	Nov 2024	-	801106
Porsche	Taycan	GTS	Kombi	Allrad	Elektro	Nov 2024	-	801107
Porsche	Taycan	Performance Battery Plus	Kombi	Heckantrieb	Elektro	Aug 2021	Dec 2023	146964
Porsche	Taycan	Performance Battery Plus	Stufenheck	Heckantrieb	Elektro	May 2020	Dec 2023	153378
Porsche	Taycan	Performance Battery Plus	Stufenheck	Heckantrieb	Elektro	Nov 2023	-	157979
Porsche	Taycan	Performance Battery Plus	Kombi	Heckantrieb	Elektro	Nov 2023	-	157980
Porsche	Taycan	Turbo	Kombi	Allrad	Elektro	May 2020	Dec 2023	145140
Porsche	Taycan	Turbo	Kombi	Allrad	Elektro	Aug 2021	Dec 2023	146971
Porsche	Taycan	Turbo	Kombi	Allrad	Elektro	Nov 2023	-	157973
Porsche	Taycan	Turbo	Stufenheck	Allrad	Elektro	Nov 2023	-	157975
Porsche	Taycan	Turbo	Kombi	Allrad	Elektro	Nov 2023	-	157981
Porsche	Taycan	Turbo GT	Stufenheck	Allrad	Elektro	Nov 2023	-	158104
Porsche	Taycan	Turbo S	Kombi	Allrad	Elektro	May 2020	Dec 2023	145141
Porsche	Taycan	Turbo S	Kombi	Allrad	Elektro	Aug 2021	Dec 2023	146973
Porsche	Taycan	Turbo S	Kombi	Allrad	Elektro	Nov 2023	-	157974
Porsche	Taycan	Turbo S	Stufenheck	Allrad	Elektro	Nov 2023	-	157976
Porsche	Taycan	Turbo S	Kombi	Allrad	Elektro	Nov 2023	-	157982
Proton	Impian	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2001	Jun 2007	18318
Proton	Persona	1.6	Stufenheck	Frontantrieb	Benzin	Mar 2008	Jul 2016	33789
Proton	Persona 300	316	Schrägheck	Frontantrieb	Benzin	Mar 1996	Jul 2004	15986
Proton	Persona 300	318 16V GTI	Schrägheck	Frontantrieb	Benzin	Mar 1996	Jul 2000	15985
Proton	Persona 400	418	Stufenheck	Frontantrieb	Benzin	May 1996	Jul 2000	15987
Proton	Persona 400	416 I	Schrägheck	Frontantrieb	Benzin	Dec 1995	Jul 2000	10914
Proton	Persona 400	420 D	Schrägheck	Frontantrieb	Diesel	Sep 1996	Jul 2000	7886
Proton	Persona 400	420 TD	Stufenheck	Frontantrieb	Diesel	Sep 1996	Jul 2000	7885
Proton	Satria	1.5	Schrägheck	Frontantrieb	Benzin	Jul 2000	May 2006	18323
Proton	Wira	1.3	Stufenheck	Frontantrieb	Benzin	Aug 2000	-	18320
Proton	Wira	1.3	Schrägheck	Frontantrieb	Benzin	Aug 2000	Jun 2007	18321
Proton	Wira	1.5	Stufenheck	Frontantrieb	Benzin	Aug 2000	-	18319
Proton	Wira	1.5	Schrägheck	Frontantrieb	Benzin	Aug 2000	Jun 2007	18322
Proton	Wira	2.0 D	Stufenheck	Frontantrieb	Diesel	Jan 2000	-	14999
Proton	Wira	2.0 D	Schrägheck	Frontantrieb	Diesel	Jan 2000	Jun 2007	15020
Puch	G-Modell	230 G	Geländewagen geschlossen	Allrad	Benzin	Mar 1979	Aug 1985	13487
Puch	G-Modell	230 GE	Geländewagen geschlossen	Allrad	Benzin	Jul 1989	Aug 1993	13479
Puch	G-Modell	230 GE	Geländewagen geschlossen	Allrad	Benzin	Mar 1979	Dec 1991	13488
Puch	G-Modell	240 GD	Geländewagen geschlossen	Allrad	Diesel	Mar 1979	Sep 1987	13489
Puch	G-Modell	250 GD	Geländewagen geschlossen	Allrad	Diesel	Oct 1987	Dec 1991	13490
Puch	G-Modell	280 GE	Geländewagen geschlossen	Allrad	Benzin	Jan 1986	Dec 1991	13491
Puch	G-Modell	290 GD	Geländewagen geschlossen	Allrad	Diesel	Oct 1991	Dec 1997	13463
Puch	G-Modell	290 GD Turbodiesel	Geländewagen geschlossen	Allrad	Diesel	Apr 1997	Dec 2001	13464
Puch	G-Modell	300 GD	Geländewagen geschlossen	Allrad	Diesel	Jun 1989	Aug 1993	13481
Puch	G-Modell	300 GD	Geländewagen geschlossen	Allrad	Diesel	Sep 1979	Dec 1991	13492
Puch	G-Modell	300 GE	Geländewagen geschlossen	Allrad	Benzin	Jun 1989	Aug 1993	13480
Puch	G-Modell	350 GD Turbo	Geländewagen geschlossen	Allrad	Diesel	Aug 1991	Aug 1993	13484
Puch	G-Modell	G 300 Turbodiesel	Geländewagen geschlossen	Allrad	Diesel	Jan 1996	Nov 2000	13482
Puch	G-Modell	G 320	Geländewagen geschlossen	Allrad	Benzin	Feb 1994	Dec 1997	13483
Puch	G-Modell	G 36 AMG	Geländewagen geschlossen	Allrad	Benzin	Jan 1995	Apr 1998	13485
Puch	G-Modell	G 500	Geländewagen geschlossen	Allrad	Benzin	Dec 1997	Nov 2000	13486
Puch	G-Modell	G 55 AMG	Geländewagen geschlossen	Allrad	Benzin	Apr 1999	Mar 2001	14614
RAM	2500	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2010	Dec 2018	54616
RAM	2500	6.4 4WD	Pick-up	Allrad	Benzin	Sep 2013	-	106939
RAM	2500	6.7 D 4WD	Pick-up	Allrad	Diesel	Sep 2012	-	59532
RAM	1500 crew cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2012	Dec 2018	54507
RAM	1500 crew cab pickup	3.0 4X4	Pick-up	Allrad	Benzin	Apr 2024	-	800046
RAM	1500 crew cab pickup	3.0 4X4	Pick-up	Allrad	Benzin	Apr 2024	-	800050
RAM	1500 crew cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2012	Dec 2018	54506
RAM	1500 crew cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2010	Dec 2018	106204
RAM	1500 crew cab pickup	6.2 TRX	Pick-up	Allrad	Benzin	Sep 2020	-	145125
RAM	1500 extended cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2012	Dec 2018	54497
RAM	1500 extended cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2012	Dec 2018	54496
RAM	1500 extended cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2010	Dec 2012	106206
RAM	1500 standard cab pickup	5.7	Pick-up	Heckantrieb	Benzin	Sep 2012	Dec 2018	105960
RAM	1500 standard cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2012	Dec 2018	105961
RAM	1500 standard cab pickup	5.7 4WD	Pick-up	Allrad	Benzin	Sep 2010	Dec 2012	106202
RAM	Rampage	2.0 4X4	Pick-up	Allrad	Benzin	Jul 2023	-	156025
RAM	Rampage	2.2 4X4	Pick-up	Allrad	Diesel	Jan 2025	-	801493
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	Oct 1962	Sep 1983	1968
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	Oct 1983	Oct 1988	1969
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	Sep 1971	Dec 1988	1970
Renault	4	0.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Apr 1983	Jul 1989	1972
Renault	4	1.1	Schrägheck	Frontantrieb	Benzin	Jun 1978	Jun 1990	1971
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 1976	Jul 1989	1974
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1982	May 1989	1975
Renault	4	E-tech 120	SUV	Frontantrieb	Elektro	Jan 2025	-	160527
Renault	4	E-tech 150	SUV	Frontantrieb	Elektro	Jan 2025	-	160528
Renault	4	E-tech 150	Kasten/SUV	Frontantrieb	Elektro	Oct 2025	-	162731
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	Oct 1972	Aug 1984	1976
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	Jan 1982	Dec 1984	1977
Renault	5	1	Schrägheck	Frontantrieb	Benzin	Jan 1972	Dec 1985	1979
Renault	5	1.1	Schrägheck	Frontantrieb	Benzin	Sep 1980	Dec 1985	1980
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	Sep 1976	Sep 1979	1981
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	Jun 1979	Sep 1984	1982
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	Sep 1975	Sep 1984	1984
Renault	5	1.4	Schrägheck	Frontantrieb	Benzin	Jan 1982	Dec 1985	1986
Renault	5	1.3 Automatik	Schrägheck	Frontantrieb	Benzin	Jun 1979	Sep 1984	1983
Renault	5	1.4 Alpine A5	Schrägheck	Frontantrieb	Benzin	Sep 1977	Sep 1981	1987
Renault	5	1.4 Alpine Turbo	Schrägheck	Frontantrieb	Benzin	Oct 1981	Jan 1985	1988
Renault	5	1.4 Automatik	Schrägheck	Frontantrieb	Benzin	Jun 1982	Sep 1984	1985
Renault	5	E-tech 120	Schrägheck	Frontantrieb	Elektro	Nov 2024	-	801153
Renault	5	E-tech 150	Schrägheck	Frontantrieb	Elektro	Jun 2024	-	800148
Renault	5	E-tech 95	Schrägheck	Frontantrieb	Elektro	Nov 2024	-	801864
Renault	5	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160631
Renault	5	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160632
Renault	5	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	160633
Renault	5	Turbo 3E	Schrägheck	Heckantrieb	Elektro	May 2025	-	801870


--- Round 1 / 首次发送 ---
## 更新点

已完成 100 个输入 Ktype 的聚类与映射，共闭合 **31 个 DIMENSION_GROUP**：

* 复用 4 个既有 Taycan 尺寸组；Turbo GT 因官方三维为 4968 × 1998 × 1378 mm，建立独立宽体尺寸组。([njcar][1])标准外廓。
* RAM 1500 根据官方规格中明确存在的 Crew、Quad、Regular Cab 以及 4×2/4×4 高度差异闭合。([Ram Canada][2]) 厢式车已将 2370/210B 对应 F6 长车身、239B 对应 F4 短车身；现代 Renault 5 使用 1774 mm 不含后视镜宽度，Turbo 3E 独立宽体建组。([Renault 4][3])pe 总数：**100**
  READY：**100**
  PENDING：**0**
  尺寸组：**31**
  引用缺失：**0**
  孤立尺寸组：**0**

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
157972	157972	Wagon	Y1B facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	MEDIUM	Kombi按Cross Turismo分支。	READY
157978	157978	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
153383	153383	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
146969	146969	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
147377	147377	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
801106	801106	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
801107	801107	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
146964	146964	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
153378	153378	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
157979	157979	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
157980	157980	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
145140	145140	Wagon	Y1B	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	MEDIUM	Kombi按Cross Turismo分支。	READY
146971	146971	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
157973	157973	Wagon	Y1B facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	MEDIUM	Kombi按Cross Turismo分支。	READY
157975	157975	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
157981	157981	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
158104	158104	Sedan	Y1A facelift	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-TURBO-GT-01	HIGH	Turbo GT独立宽体外廓。	READY
145141	145141	Wagon	Y1B	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	MEDIUM	Kombi按Cross Turismo分支。	READY
146973	146973	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
157974	157974	Wagon	Y1B facelift	Y1B	5	EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	MEDIUM	Kombi按Cross Turismo分支。	READY
157976	157976	Sedan	Y1A	Y1A	4	EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	HIGH		READY
157982	157982	Wagon	Y1C	Y1C	5	EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	HIGH	Kombi按Sport Turismo分支。	READY
18318	18318	Sedan	Waja		4	EU-PROTON-IMPIAN-WAJA-SEDAN-STANDARD-01	HIGH		READY
33789	33789	Sedan	Persona CM	CM	4	EU-PROTON-PERSONA-CM-SEDAN-STANDARD-01	HIGH		READY
15986	15986	Hatchback	Persona I Compact		3	EU-PROTON-PERSONA-I-HATCHBACK-COMPACT-01	HIGH		READY
15985	15985	Hatchback	Persona I Compact		3	EU-PROTON-PERSONA-I-HATCHBACK-COMPACT-01	HIGH		READY
15987	15987	Sedan	Persona/Wira I		4	EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	HIGH		READY
10914	10914	Hatchback	Persona/Wira I		5	EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	HIGH		READY
7886	7886	Hatchback	Persona/Wira I		5	EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	HIGH		READY
7885	7885	Sedan	Persona/Wira I		4	EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	HIGH		READY
18323	18323	Hatchback	Satria I		3	EU-PROTON-SATRIA-I-HATCHBACK-STANDARD-01	HIGH		READY
18320	18320	Sedan	Persona/Wira I		4	EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	HIGH		READY
18321	18321	Hatchback	Persona/Wira I		5	EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	HIGH		READY
18319	18319	Sedan	Persona/Wira I		4	EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	HIGH		READY
18322	18322	Hatchback	Persona/Wira I		5	EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	HIGH		READY
14999	14999	Sedan	Persona/Wira I		4	EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	HIGH		READY
15020	15020	Hatchback	Persona/Wira I		5	EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	HIGH		READY
13487	13487	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13479	13479	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13488	13488	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13489	13489	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13490	13490	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13491	13491	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13463	13463	SUV	W461	W461	5	EU-PUCH-G-MODELL-W461-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13464	13464	SUV	W461	W461	5	EU-PUCH-G-MODELL-W461-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13481	13481	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13492	13492	SUV	W460	W460	5	EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13480	13480	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13484	13484	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13482	13482	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13483	13483	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13485	13485	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
13486	13486	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
14614	14614	SUV	W463	W463	5	EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	MEDIUM	输入未给轴距/门数；采用五门长轴标准外廓。	READY
54616	54616	Pickup	4th gen	DJ	4	EU-RAM-2500-DJ-PICKUP-CREW-64-4WD-01	MEDIUM	输入未给驾驶室/货斗；采用Crew Cab 6 ft 4 in外廓。	READY
106939	106939	Pickup	4th gen	DJ	4	EU-RAM-2500-DJ-PICKUP-CREW-64-4WD-01	MEDIUM	输入未给驾驶室/货斗；采用Crew Cab 6 ft 4 in外廓。	READY
59532	59532	Pickup	4th gen	DJ	4	EU-RAM-2500-DJ-PICKUP-CREW-64-4WD-01	MEDIUM	输入未给驾驶室/货斗；采用Crew Cab 6 ft 4 in外廓。	READY
54507	54507	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-CREW-57-2WD-01	MEDIUM	输入未给货斗；采用Crew Cab 5 ft 7 in短货斗。	READY
800046	800046	Pickup	5th gen facelift	DT	4	EU-RAM-1500-DT-PICKUP-CREW-57-4WD-01	MEDIUM	输入未给货斗；采用Crew Cab 5 ft 7 in短货斗。	READY
800050	800050	Pickup	5th gen facelift	DT	4	EU-RAM-1500-DT-PICKUP-CREW-57-4WD-01	MEDIUM	输入未给货斗；采用Crew Cab 5 ft 7 in短货斗。	READY
54506	54506	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-CREW-57-4WD-01	MEDIUM	输入未给货斗；采用Crew Cab 5 ft 7 in短货斗。	READY
106204	106204	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-CREW-57-4WD-01	MEDIUM	输入未给货斗；采用Crew Cab 5 ft 7 in短货斗。	READY
145125	145125	Pickup	5th gen	DT	4	EU-RAM-1500-DT-PICKUP-TRX-CREW-57-01	HIGH	TRX工厂宽体Crew Cab短货斗。	READY
54497	54497	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-QUAD-64-2WD-01	HIGH	Extended Cab对应Quad Cab 6 ft 4 in货斗。	READY
54496	54496	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-QUAD-64-4WD-01	HIGH	Extended Cab对应Quad Cab 6 ft 4 in货斗。	READY
106206	106206	Pickup	4th gen	DS	4	EU-RAM-1500-DS-PICKUP-QUAD-64-4WD-01	HIGH	Extended Cab对应Quad Cab 6 ft 4 in货斗。	READY
105960	105960	Pickup	4th gen	DS	2	EU-RAM-1500-DS-PICKUP-REGULAR-64-2WD-01	MEDIUM	输入未给货斗；采用Regular Cab 6 ft 4 in货斗。	READY
105961	105961	Pickup	4th gen	DS	2	EU-RAM-1500-DS-PICKUP-REGULAR-64-4WD-01	MEDIUM	输入未给货斗；采用Regular Cab 6 ft 4 in货斗。	READY
106202	106202	Pickup	4th gen	DS	2	EU-RAM-1500-DS-PICKUP-REGULAR-64-4WD-01	MEDIUM	输入未给货斗；采用Regular Cab 6 ft 4 in货斗。	READY
156025	156025	Pickup	Rampage	KM	4	EU-RAM-RAMPAGE-KM-PICKUP-CREW-STANDARD-01	HIGH		READY
801493	801493	Pickup	Rampage	KM	4	EU-RAM-RAMPAGE-KM-PICKUP-CREW-STANDARD-01	HIGH		READY
1968	1968	Hatchback	I	112	5	EU-RENAULT-4-I-HATCHBACK-STANDARD-01	HIGH		READY
1969	1969	Hatchback	I	112	5	EU-RENAULT-4-I-HATCHBACK-STANDARD-01	HIGH		READY
1970	1970	Hatchback	I	112	5	EU-RENAULT-4-I-HATCHBACK-STANDARD-01	HIGH		READY
1972	1972	Van	I	R21/R23	3	EU-RENAULT-4-I-VAN-F4-01	HIGH	0.8厢式采用F4短车身。	READY
1971	1971	Hatchback	I	112	5	EU-RENAULT-4-I-HATCHBACK-STANDARD-01	HIGH		READY
1974	1974	Van	I	2370/210B	3	EU-RENAULT-4-I-VAN-F6-01	HIGH	2370/210B对应F6长车身。	READY
1975	1975	Van	I	239B	3	EU-RENAULT-4-I-VAN-F4-01	HIGH	239B对应F4短车身。	READY
160527	160527	SUV	E-Tech	R4	5	EU-RENAULT-4-E-TECH-SUV-STANDARD-01	HIGH		READY
160528	160528	SUV	E-Tech	R4	5	EU-RENAULT-4-E-TECH-SUV-STANDARD-01	HIGH		READY
162731	162731	Van	E-Tech	R4	5	EU-RENAULT-4-E-TECH-SUV-STANDARD-01	HIGH	商用厢式与乘用版共用外廓。	READY
1976	1976	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1977	1977	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1979	1979	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1980	1980	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1981	1981	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1982	1982	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1984	1984	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1986	1986	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1983	1983	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1987	1987	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1988	1988	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
1985	1985	Hatchback	I	122		EU-RENAULT-5-I-HATCHBACK-STANDARD-01	MEDIUM	输入未给门数；采用第一代标准量产外廓。	READY
801153	801153	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
800148	800148	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
801864	801864	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
160631	160631	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
160632	160632	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
160633	160633	Hatchback	E-Tech	R5	5	EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	HIGH		READY
801870	801870	Hatchback	Turbo 3E	R5T3E	2	EU-RENAULT-5-TURBO-3E-HATCHBACK-WIDEBODY-01	HIGH	Turbo 3E为独立双门宽体外廓。	READY
```

[下载 Ktype 映射最终 TSV](sandbox:/mnt/data/left18448_13701-13800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-TAYCAN-Y1A-SEDAN-STANDARD-01	4963	1966	1379	Porsche Newsroom technical data	https://newsroom.porsche.com/dam/jcr%3A84336058-7f26-45da-8162-7de8b60a24e2/PAG_TD_Taycan4S_withPerformancebattery_EN.pdf
EU-PORSCHE-TAYCAN-Y1B-FACELIFT-WAGON-CROSS-TURISMO-01	4974	1967	1409	Porsche Newsroom technical data	https://newsroom.porsche.com/dam/jcr%3A8ee6f537-4ff9-435f-b3b4-7142d8972324/pag-taycan-4-cross-turismo-td-en.pdf
EU-PORSCHE-TAYCAN-Y1B-WAGON-CROSS-TURISMO-01	4974	1966	1409	Porsche MY23 technical specifications	https://download.newsroom.porsche.com/dam/jcr%3A0bf91231-daa1-4cf0-b4bd-51c665034a1f/MY23%20Porsche%20Taycan%20Technical%20Specifications.pdf
EU-PORSCHE-TAYCAN-Y1C-WAGON-SPORT-TURISMO-01	4963	1966	1390	Porsche MY23 technical specifications	https://download.newsroom.porsche.com/dam/jcr%3A0bf91231-daa1-4cf0-b4bd-51c665034a1f/MY23%20Porsche%20Taycan%20Technical%20Specifications.pdf
EU-PORSCHE-TAYCAN-Y1A-SEDAN-TURBO-GT-01	4968	1998	1378	Porsche Newsroom Turbo GT technical data	https://newsroom.porsche.com/dam/jcr%3Adb7be217-7b2a-44a6-b2b3-3493b5baf1c1/pag-taycan-turbo-gt-td-en.pdf.PDF
EU-PROTON-IMPIAN-WAJA-SEDAN-STANDARD-01	4465	1740	1420	Auto-Data Proton Waja 1.6	https://www.auto-data.net/en/proton-waja-1.6-i-16v-103hp-8243
EU-PROTON-PERSONA-CM-SEDAN-STANDARD-01	4477	1725	1438	CarsGuide 2008 Proton Persona dimensions	https://www.carsguide.com.au/proton/persona/car-dimensions/2008
EU-PROTON-PERSONA-I-HATCHBACK-COMPACT-01	3990	1698	1365	Auto-Data Proton Persona Compact	https://www.auto-data.net/en/proton-persona-i-compact-1.6-i-316-glsi-95hp-8235
EU-PROTON-PERSONA-WIRA-SEDAN-STANDARD-01	4360	1690	1385	Auto-Data Proton Persona I sedan	https://www.auto-data.net/en/proton-persona-i-generation-1816
EU-PROTON-PERSONA-WIRA-HATCHBACK-STANDARD-01	4270	1690	1385	Auto-Data Proton Persona I hatchback	https://www.auto-data.net/en/proton-persona-i-hatchback-1.6-i-16v-416-gli-95hp-8251
EU-PROTON-SATRIA-I-HATCHBACK-STANDARD-01	3990	1690	1360	CarsGuide 2000 Proton Satria dimensions	https://www.carsguide.com.au/proton/satria/car-dimensions/2000
EU-PUCH-G-MODELL-W460-SUV-LWB-5D-01	4404	1699	1920	NJCar Puch G-Modell dimensions	https://www.njcar.ru/dimensions/PUCH/Gmodell/
EU-PUCH-G-MODELL-W461-SUV-LWB-5D-01	4404	1700	1920	NJCar Puch G-Modell dimensions	https://www.njcar.ru/dimensions/PUCH/Gmodell/
EU-PUCH-G-MODELL-W463-SUV-LWB-5D-01	4680	1760	1940	NJCar Puch G-Modell dimensions	https://www.njcar.ru/dimensions/PUCH/Gmodell/
EU-RAM-2500-DJ-PICKUP-CREW-64-4WD-01	6030	2009	1974	Edmunds 2018 Ram 2500 Crew Cab	https://www.edmunds.com/ram/2500/2018/crew-cab/features-specs/
EU-RAM-1500-DS-PICKUP-CREW-57-2WD-01	5817	2018	1954	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-1500-DS-PICKUP-CREW-57-4WD-01	5817	2018	1968	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-1500-DT-PICKUP-CREW-57-4WD-01	5916	2085	1971	Edmunds 2025 Ram 1500 Crew Cab	https://www.edmunds.com/ram/1500/2025/crew-cab/features-specs/
EU-RAM-1500-DT-PICKUP-TRX-CREW-57-01	5916	2235	2055	MotorTrend 2021 Ram 1500 TRX specifications	https://www.motortrend.com/news/2021-ram-1500-trx-first-look
EU-RAM-1500-DS-PICKUP-QUAD-64-2WD-01	5817	2017	1960	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-1500-DS-PICKUP-QUAD-64-4WD-01	5817	2017	1975	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-1500-DS-PICKUP-REGULAR-64-2WD-01	5309	2017	1894	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-1500-DS-PICKUP-REGULAR-64-4WD-01	5309	2017	1910	Ram Canada 2018 1500 specifications chart	https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf
EU-RAM-RAMPAGE-KM-PICKUP-CREW-STANDARD-01	5028	1886	1780	Stellantis Media Ram Rampage technical data	https://www.media.stellantis.com/br-pt/ram/press/rampage-uma-legitima-ram-criada-sob-medida-para-o-brasil
EU-RENAULT-4-I-HATCHBACK-STANDARD-01	3670	1485	1550	Auto-Data Renault 4 generation	https://www.auto-data.net/en/renault-4-generation-2164
EU-RENAULT-4-I-VAN-F4-01	3653	1500	1710	AutoCentrum Renault 4 I Van 1.1	https://www.autocentrum.pl/dane-techniczne/renault/4/i/van/silnik-benzynowy-1.1-34km-1978-1991/
EU-RENAULT-4-I-VAN-F6-01	3853	1532	1720	La 4L de Sylvie Renault 4 F6 dimensions	https://www.la4ldesylvie.fr/dimensions-des-renault-4
EU-RENAULT-4-E-TECH-SUV-STANDARD-01	4143	1796	1552	Renault user manual dimensions	https://www.user-manual.renault.com/en/content/renault-4-e-tech-electric/technical-specifications/information-about-vehicle/dimensions
EU-RENAULT-5-I-HATCHBACK-STANDARD-01	3506	1525	1400	Automobile-Catalog 1978 Renault 5 TS	https://www.automobile-catalog.com/car/1978/2927870/renault_5_ts.html
EU-RENAULT-5-E-TECH-HATCHBACK-STANDARD-01	3922	1774	1498	Renault user manual dimensions	https://www.user-manual.renault.com/en/content/renault-5-e-tech-electric-0/technical-specifications/information-about-vehicle/dimensions
EU-RENAULT-5-TURBO-3E-HATCHBACK-WIDEBODY-01	4080	2030	1380	Renault Global Media Turbo 3E technical data	https://media.renault.com/renault-5-turbo-3e-the-legend-returns-in-the-form-of-the-very-first-electric-mini-supercar/?lang=eng
```

[下载 DIMENSION_GROUP 最终 TSV](sandbox:/mnt/data/left18448_13701-13800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.njcar.ru/dimensions/PUCH/Gmodell/?utm_source=chatgpt.com "Размеры автомобилей PUCH G-modell"
[2]: https://www.ramtruck.ca/documents/ramtruck/specifications/2018-ramtruck-1500ds-specifications-en.pdf?utm_source=chatgpt.com "2018 RAM 1500 Specifications Chart"
[3]: https://www.renault4.co.uk/forum/threads/r4-vans.6986/?utm_source=chatgpt.com "R4 vans | Renault 4 Forum"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5383 行）
- 累计尺寸组：dimension_groups_final.tsv（1530 行）

