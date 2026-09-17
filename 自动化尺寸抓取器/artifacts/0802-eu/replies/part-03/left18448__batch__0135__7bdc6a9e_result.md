# 任务：left18448 第 13401-13500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0135__7bdc6a9e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13401-13500 行

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
left18448 第 13401-13500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13401-13500_ktype_dimension_mapping_final.tsv
- left18448_13401-13500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	3300	1400	1710
EU-PIAGGIO-PORTER-I-VAN-01	3370	1400	1870
EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	3420	1395	1705

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Piaggio	Porter	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	Nov 2015	-	117798
Piaggio	Porter	1.3	Kasten	Heckantrieb	Benzin	Jan 2016	-	119833
Piaggio	Porter	1.2 D	Kasten	Heckantrieb	Diesel	May 1995	-	14757
Piaggio	Porter	1.2 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 1995	-	18184
Piaggio	Porter	1.3 16V 4X4	Kasten	Allrad	Benzin	Jun 1998	Dec 2010	5074
Piaggio	Porter	1.3 16V 4X4	Pritsche/Fahrgestell	Allrad	Benzin	Jun 1998	Dec 2010	5108
Piaggio	Porter	1.3 4X4	Kasten	Allrad	Benzin	Jan 2011	-	118670
Piaggio	Porter	1.3 4X4	Pritsche/Fahrgestell	Allrad	Benzin	Jan 2011	-	118671
Piaggio	Porter	1.3 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Jan 2011	-	10571
Piaggio	Porter	1.3 CNG	Bus	Heckantrieb	Benzin/Erdgas (CNG)	Jul 2016	-	120591
Piaggio	Porter	1.3 CNG	Kasten	Heckantrieb	Benzin/Erdgas (CNG)	Jul 2016	-	120592
Piaggio	Porter	1.3 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Jul 2016	-	120594
Piaggio	Porter	1.3 I 16V	Kasten	Heckantrieb	Benzin	May 1998	-	14756
Piaggio	Porter	1.3 LPG	Kasten	Heckantrieb	Benzin/Autogas (LPG)	Jan 2016	-	119834
Piaggio	Porter	1.3 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2016	-	119835
Piaggio	Porter	1.3 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2016	-	119836
Piaggio	Porter	1.4 D	Kasten	Heckantrieb	Diesel	Apr 1998	-	18627
Piaggio	Porter	1.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 1998	-	18628
Piaggio	Porter	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jun 1998	-	5754
Piaggio	Porter	Electro	Kasten	Heckantrieb	Elektro	Jun 1998	-	5755
Piaggio	Porter np6	1.5 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Jan 2021	-	143697
Piaggio	Porter np6	1.5 CNG Allrad	Pritsche/Fahrgestell	Allrad	Benzin/Erdgas (CNG)	Feb 2023	-	157285
Piaggio	Porter np6	1.5 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2021	-	143695
Piaggio	Porter npe	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2025	-	801528
Plymouth	Voyager / grand	3	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16426
Plymouth	Voyager / grand	2.0 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16424
Plymouth	Voyager / grand	2.4 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16425
Plymouth	Voyager / grand	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	Jan 1995	Mar 2001	16432
Plymouth	Voyager / grand	3.3 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16427
Plymouth	Voyager / grand	3.8 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16428
Plymouth	Voyager / grand	3.8 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	16430
Plymouth	Voyager / grand	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	16429
Plymouth	Voyager / grand	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	16431
Polestar	Polestar 2	EV	Schrägheck	Frontantrieb	Elektro	Apr 2021	-	143879
Polestar	Polestar 2	EV	Schrägheck	Frontantrieb	Elektro	Apr 2021	Dec 2022	144835
Polestar	Polestar 2	EV	Schrägheck	Allrad	Elektro	Jan 2023	-	152005
Polestar	Polestar 2	EV	Schrägheck	Heckantrieb	Elektro	Mar 2023	-	152752
Polestar	Polestar 2	EV	Schrägheck	Heckantrieb	Elektro	Mar 2023	-	152753
Polestar	Polestar 2	EV	Schrägheck	Allrad	Elektro	Mar 2023	-	152754
Polestar	Polestar 3	EV	SUV	Allrad	Elektro	Oct 2023	-	150670
Polestar	Polestar 3	EV	SUV	Allrad	Elektro	Oct 2023	-	150671
Polestar	Polestar 3	EV	SUV	Heckantrieb	Elektro	Oct 2023	-	158768
Polestar	Polestar 3	EV	SUV	Heckantrieb	Elektro	Oct 2025	-	802522
Polestar	Polestar 3	EV	SUV	Allrad	Elektro	Oct 2025	-	802523
Polestar	Polestar 3	EV	SUV	Allrad	Elektro	Oct 2025	-	802524
Polestar	Polestar 4	EV	SUV	Heckantrieb	Elektro	Apr 2023	-	154015
Polestar	Polestar 4	EV Allrad	SUV	Allrad	Elektro	Apr 2023	-	154016
Polestar	Polestar 5	Dual Motor AWD	Stufenheck	Allrad	Elektro	Sep 2025	-	162481
Polestar	Polestar 5	Performance AWD	Stufenheck	Allrad	Elektro	Sep 2025	-	162482
Pontiac	Trans sport	3.4	Großraumlimousine	Frontantrieb	Benzin	Sep 1998	Dec 1999	11608
Pontiac	Trans sport	3.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 1996	Aug 1998	142525
Pontiac	Trans sport	3.8	Großraumlimousine	Frontantrieb	Benzin	Sep 1991	Dec 1995	48313
Pontiac	Trans sport mini cargo van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Sep 1991	Dec 1994	48311
Pontiac	Trans sport van	2.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 1993	Aug 1995	143213
Pontiac	Trans sport van	3.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 1989	Oct 1996	143214
Pontiac	Trans sport van	3.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 1989	Oct 1996	143215
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1989	Mar 1997	143216
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1989	Mar 1997	143217
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 1989	Mar 1997	143218
Porsche	911	2	Coupe	Heckantrieb	Benzin	Jan 1963	Jul 1967	144566
Porsche	911	2.0 E	Coupe	Heckantrieb	Benzin	Sep 1968	Dec 1969	58998
Porsche	911	2.0 S	Coupe	Heckantrieb	Benzin	Jul 1966	Nov 1968	58996
Porsche	911	2.0 S	Coupe	Heckantrieb	Benzin	Sep 1968	Dec 1969	58997
Porsche	911	2.2 E	Coupe	Heckantrieb	Benzin	Sep 1969	Dec 1971	58999
Porsche	911	2.2 S	Coupe	Heckantrieb	Benzin	Sep 1969	Dec 1971	59000
Porsche	911	2.3 T	Targa	Heckantrieb	Benzin	Sep 1971	Dec 1973	58915
Porsche	911	3.0 Carrera	Coupe	Heckantrieb	Benzin	Nov 2015	Dec 2019	117749
Porsche	911	3.0 Carrera	Cabriolet	Heckantrieb	Benzin	Nov 2015	Dec 2019	117750
Porsche	911	3.0 Carrera	Coupe	Heckantrieb	Benzin	Jan 2024	-	159166
Porsche	911	3.0 Carrera	Cabriolet	Heckantrieb	Benzin	Jan 2024	-	159167
Porsche	911	3.0 Carrera 4	Cabriolet	Allrad	Benzin	Nov 2015	Dec 2019	117751
Porsche	911	3.0 Carrera 4	Coupe	Allrad	Benzin	Nov 2015	Dec 2019	117752
Porsche	911	3.0 Carrera 4	Targa	Allrad	Benzin	Nov 2015	Dec 2019	117753
Porsche	911	3.0 Carrera 4 GTS	Coupe	Allrad	Benzin	Mar 2017	Dec 2019	125933
Porsche	911	3.0 Carrera 4 GTS	Cabriolet	Allrad	Benzin	Mar 2017	Dec 2019	125935
Porsche	911	3.0 Carrera 4 GTS	Targa	Allrad	Benzin	Mar 2017	Dec 2019	125936
Porsche	911	3.0 Carrera 4 GTS	Cabriolet	Allrad	Benzin	Jan 2021	Dec 2024	145113
Porsche	911	3.0 Carrera 4 GTS	Coupe	Allrad	Benzin	Jan 2021	Dec 2024	145115
Porsche	911	3.0 Carrera 4S	Cabriolet	Allrad	Benzin	Nov 2015	Dec 2019	117756
Porsche	911	3.0 Carrera 4S	Coupe	Allrad	Benzin	Nov 2015	Dec 2019	117757
Porsche	911	3.0 Carrera 4S	Targa	Allrad	Benzin	Nov 2015	Dec 2019	117758
Porsche	911	3.0 Carrera 4S	Coupe	Allrad	Benzin	Jan 2024	-	802680
Porsche	911	3.0 Carrera 4S	Cabriolet	Allrad	Benzin	Jan 2024	-	802681
Porsche	911	3.0 Carrera GTS	Coupe	Heckantrieb	Benzin	Mar 2017	Dec 2019	125932
Porsche	911	3.0 Carrera GTS	Cabriolet	Heckantrieb	Benzin	Mar 2017	Dec 2019	125934
Porsche	911	3.0 Carrera GTS	Cabriolet	Heckantrieb	Benzin	Jan 2021	May 2024	145114
Porsche	911	3.0 Carrera GTS	Coupe	Heckantrieb	Benzin	Jan 2021	Dec 2024	145116
Porsche	911	3.0 Carrera S	Coupe	Heckantrieb	Benzin	Nov 2015	Dec 2019	117754
Porsche	911	3.0 Carrera S	Cabriolet	Heckantrieb	Benzin	Nov 2015	Dec 2019	117755
Porsche	911	3.0 Carrera S	Coupe	Heckantrieb	Benzin	Jan 2024	-	801888
Porsche	911	3.0 Carrera S	Cabriolet	Heckantrieb	Benzin	Jan 2024	-	802104
Porsche	911	3.0 Carrera T	Coupe	Heckantrieb	Benzin	Apr 2022	Dec 2024	151471
Porsche	911	3.0 Carrera T	Coupe	Heckantrieb	Benzin	Jan 2024	-	801223
Porsche	911	3.0 Carrera T	Cabriolet	Heckantrieb	Benzin	Jan 2024	-	801278
Porsche	911	3.0 Dakar	Coupe	Allrad	Benzin	Jan 2023	Dec 2024	152277
Porsche	911	3.0 Turbo	Coupe	Heckantrieb	Benzin	Jan 1975	Dec 1977	11800
Porsche	911	3.3 Turbo	Cabriolet	Heckantrieb	Benzin	Sep 1986	Aug 1989	59491
Porsche	911	3.4 Carrera	Coupe	Heckantrieb	Benzin	Dec 2011	Dec 2019	11568
Porsche	911	3.4 Carrera	Coupe	Heckantrieb	Benzin	Aug 1997	Jul 1999	14428
Porsche	911	3.4 Carrera	Cabriolet	Heckantrieb	Benzin	Aug 1997	Jul 1999	14429


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 100 个输入 Ktype 的映射闭合。
* 复用 3 个跨批次 Piaggio 尺寸组，新建当前批次所需尺寸组。
* Polestar 5 按官方列出的 Dual Motor 与 Performance 高度差拆分；Porter NP6/NPE 的短轴底盘外廓复用；1972 年 911 T Targa 使用对应欧洲规格。([Polestar – Electric cars | Polestar SG][1])
* 已完成固定表头、唯一性、引用闭合、正整数尺寸、来源非空及孤立尺寸组检查。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：45
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117798	117798	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
119833	119833	Van	Porter II			EU-PIAGGIO-PORTER-II-VAN-01	HIGH		READY
14757	14757	Van	Porter I			EU-PIAGGIO-PORTER-I-VAN-01	HIGH		READY
18184	18184	Pickup	Porter I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	HIGH		READY
5074	5074	Van	Porter I			EU-PIAGGIO-PORTER-I-VAN-01	HIGH		READY
5108	5108	Pickup	Porter I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	HIGH		READY
118670	118670	Van	Porter II			EU-PIAGGIO-PORTER-II-VAN-01	HIGH		READY
118671	118671	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
10571	10571	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
120591	120591	MPV	Porter II			EU-PIAGGIO-PORTER-II-VAN-01	HIGH		READY
120592	120592	Van	Porter II			EU-PIAGGIO-PORTER-II-VAN-01	HIGH		READY
120594	120594	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
14756	14756	Van	Porter I			EU-PIAGGIO-PORTER-I-VAN-01	HIGH		READY
119834	119834	Van	Porter II			EU-PIAGGIO-PORTER-II-VAN-01	HIGH		READY
119835	119835	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
119836	119836	Pickup	Porter II			EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	HIGH		READY
18627	18627	Van	Porter I			EU-PIAGGIO-PORTER-I-VAN-01	HIGH		READY
18628	18628	Pickup	Porter I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	HIGH		READY
5754	5754	Pickup	Porter I			EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	HIGH		READY
5755	5755	Van	Porter I			EU-PIAGGIO-PORTER-I-VAN-01	HIGH		READY
143697	143697	Pickup	Porter NP6	NP6		EU-PIAGGIO-PORTER-NP6-PICKUP-SWB-01	MEDIUM	No wheelbase branch is stated; standard SWB cab/chassis selected.	READY
157285	157285	Pickup	Porter NP6	NP6		EU-PIAGGIO-PORTER-NP6-PICKUP-SWB-01	MEDIUM	No wheelbase branch is stated; standard SWB cab/chassis selected.	READY
143695	143695	Pickup	Porter NP6	NP6		EU-PIAGGIO-PORTER-NP6-PICKUP-SWB-01	MEDIUM	No wheelbase branch is stated; standard SWB cab/chassis selected.	READY
801528	801528	Pickup	Porter NPE	NP6		EU-PIAGGIO-PORTER-NP6-PICKUP-SWB-01	MEDIUM	NPE uses the NP6 SWB cab/chassis exterior; no wheelbase branch is stated.	READY
16426	16426	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16424	16424	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16425	16425	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16432	16432	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16427	16427	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16428	16428	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16430	16430	MPV	Voyager III	NS		EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	MEDIUM	Combined Voyager/Grand label has no Grand marker; standard-wheelbase Voyager selected.	READY
16429	16429	MPV	Voyager III	NS		EU-PLYMOUTH-GRAND-VOYAGER-III-MPV-LWB-01	HIGH	AWD offering mapped to the Grand Voyager LWB exterior.	READY
16431	16431	MPV	Voyager III	NS		EU-PLYMOUTH-GRAND-VOYAGER-III-MPV-LWB-01	HIGH	AWD offering mapped to the Grand Voyager LWB exterior.	READY
143879	143879	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
144835	144835	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
152005	152005	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
152752	152752	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
152753	152753	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
152754	152754	Hatchback	Polestar 2		5	EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	HIGH		READY
150670	150670	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
150671	150671	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
158768	158768	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
802522	802522	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
802523	802523	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
802524	802524	SUV	Polestar 3		5	EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	HIGH		READY
154015	154015	SUV	Polestar 4		5	EU-POLESTAR-POLESTAR-4-SUV-STANDARD-01	HIGH		READY
154016	154016	SUV	Polestar 4		5	EU-POLESTAR-POLESTAR-4-SUV-STANDARD-01	HIGH		READY
162481	162481	Sedan	Polestar 5			EU-POLESTAR-POLESTAR-5-SEDAN-DUAL-MOTOR-01	HIGH	Dual Motor factory height differs from the Performance version.	READY
162482	162482	Sedan	Polestar 5			EU-POLESTAR-POLESTAR-5-SEDAN-PERFORMANCE-01	HIGH	Performance factory height differs from the Dual Motor version.	READY
11608	11608	MPV	Trans Sport II	GMT200		EU-PONTIAC-TRANS-SPORT-II-MPV-SWB-01	MEDIUM	No Long designation is present; standard-wheelbase body selected.	READY
142525	142525	Van	Trans Sport II	GMT200		EU-PONTIAC-TRANS-SPORT-II-MPV-SWB-01	MEDIUM	No Long designation is present; standard-wheelbase body selected.	READY
48313	48313	MPV	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH		READY
48311	48311	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143213	143213	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143214	143214	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143215	143215	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143216	143216	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143217	143217	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
143218	143218	Van	Trans Sport I	GMT199		EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	HIGH	Cargo designation shares the passenger-body exterior.	READY
144566	144566	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
58998	58998	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
58996	58996	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
58997	58997	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
58999	58999	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
59000	59000	Coupe	911 901	901	2	EU-PORSCHE-911-901-COUPE-STANDARD-01	HIGH		READY
58915	58915	Targa	911 901	901	2	EU-PORSCHE-911-901-TARGA-STANDARD-01	HIGH		READY
117749	117749	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-01	HIGH		READY
117750	117750	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-01	HIGH		READY
159166	159166	Coupe	911 992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-01	HIGH		READY
159167	159167	Convertible	911 992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-01	HIGH		READY
117751	117751	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-01	HIGH		READY
117752	117752	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-4-01	HIGH		READY
117753	117753	Targa	911 991.2	991	2	EU-PORSCHE-911-991-2-TARGA-CARRERA-4-01	HIGH		READY
125933	125933	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-4-GTS-01	HIGH		READY
125935	125935	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-GTS-01	HIGH		READY
125936	125936	Targa	911 991.2	991	2	EU-PORSCHE-911-991-2-TARGA-CARRERA-4-GTS-01	HIGH		READY
145113	145113	Convertible	911 992.1	992	2	EU-PORSCHE-911-992-1-CONVERTIBLE-GTS-01	HIGH		READY
145115	145115	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-COUPE-GTS-01	HIGH		READY
117756	117756	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4S-01	HIGH		READY
117757	117757	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-4S-01	HIGH		READY
117758	117758	Targa	911 991.2	991	2	EU-PORSCHE-911-991-2-TARGA-CARRERA-4S-01	HIGH		READY
802680	802680	Coupe	911 992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-S-01	HIGH		READY
802681	802681	Convertible	911 992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-S-01	HIGH		READY
125932	125932	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-GTS-01	HIGH		READY
125934	125934	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-GTS-01	HIGH		READY
145114	145114	Convertible	911 992.1	992	2	EU-PORSCHE-911-992-1-CONVERTIBLE-GTS-01	HIGH		READY
145116	145116	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-COUPE-GTS-01	HIGH		READY
117754	117754	Coupe	911 991.2	991	2	EU-PORSCHE-911-991-2-COUPE-CARRERA-S-01	HIGH		READY
117755	117755	Convertible	911 991.2	991	2	EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-S-01	HIGH		READY
801888	801888	Coupe	911 992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-S-01	HIGH		READY
802104	802104	Convertible	911 992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-S-01	HIGH		READY
151471	151471	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-COUPE-CARRERA-T-01	HIGH		READY
801223	801223	Coupe	911 992.2	992	2	EU-PORSCHE-911-992-2-COUPE-CARRERA-T-01	HIGH		READY
801278	801278	Convertible	911 992.2	992	2	EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-01	HIGH	Carrera T Cabriolet shares the standard 992.2 cabriolet exterior dimensions.	READY
152277	152277	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-COUPE-DAKAR-01	HIGH		READY
11800	11800	Coupe	911 930	930	2	EU-PORSCHE-911-930-COUPE-TURBO-01	HIGH		READY
59491	59491	Convertible	911 930	930	2	EU-PORSCHE-911-930-CONVERTIBLE-TURBO-01	HIGH		READY
11568	11568	Coupe	911 991.1	991	2	EU-PORSCHE-911-991-1-COUPE-CARRERA-01	HIGH		READY
14428	14428	Coupe	911 996	996	2	EU-PORSCHE-911-996-COUPE-CARRERA-01	HIGH		READY
14429	14429	Convertible	911 996	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_13401-13500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PIAGGIO-PORTER-I-STANDARD-DECK-01	3300	1400	1710	Cross-batch closed Piaggio Porter I dimension record	https://www.caranddriving.com/cdwebsite/editorial-library-review.aspx?id=106622
EU-PIAGGIO-PORTER-I-VAN-01	3370	1400	1870	Cross-batch closed Piaggio Porter I dimension record	https://www.caranddriving.com/cdwebsite/editorial-library-review.aspx?id=106622
EU-PIAGGIO-PORTER-II-STANDARD-DECK-01	3420	1395	1705	Piaggio Porter Multitech Euro 5 workshop manual	https://www.manualslib.de/manual/777055/Piaggio-2010-Porter-Multitech-Euro-5.html
EU-PIAGGIO-PORTER-II-VAN-01	3400	1395	1870	Piaggio Porter brochure	https://piaggiocommercialuk.com/wp-content/uploads/2017/12/Porter-Brochure-pdf.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-SWB-01	4085	1640	1840	Piaggio Porter NP6 1.5 E6 2024 workshop manual	https://www.manualslib.de/manual/1436557/Piaggio-Porter-Np6-1-5-E6-2024.html
EU-PLYMOUTH-VOYAGER-III-MPV-SWB-01	4733	1950	1740	Auto-Data Chrysler Voyager III generation specifications	https://www.auto-data.net/en/chrysler-voyager-iii-generation-3279
EU-PLYMOUTH-GRAND-VOYAGER-III-MPV-LWB-01	5070	1950	1740	Auto-Data Chrysler Grand Voyager III generation specifications	https://www.auto-data.net/en/chrysler-grand-voyager-iii-generation-3258
EU-POLESTAR-POLESTAR-2-HATCHBACK-STANDARD-01	4606	1859	1479	Polestar 2 2024 official manual	https://www.polestar.com/en-ca/manual/polestar-2/2024/article/600bb602685314bdc0a80151151322eb/
EU-POLESTAR-POLESTAR-3-SUV-STANDARD-01	4900	1968	1627	Polestar 3 2025 official manual	https://www.polestar.com/us/manual/polestar-3/2025/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409
EU-POLESTAR-POLESTAR-4-SUV-STANDARD-01	4840	2008	1534	Polestar 4 2025 official manual	https://www.polestar.com/us/manual/polestar-4/2025/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-POLESTAR-POLESTAR-5-SEDAN-DUAL-MOTOR-01	5087	2015	1425	Polestar 5 official specifications	https://www.polestar.com/ie/polestar-5/specifications/
EU-POLESTAR-POLESTAR-5-SEDAN-PERFORMANCE-01	5087	2015	1419	Polestar 5 official specifications	https://www.polestar.com/ie/polestar-5/specifications/
EU-PONTIAC-TRANS-SPORT-I-MPV-STANDARD-01	4946	1886	1670	Auto-Data Pontiac Trans Sport 3.8 V6 specifications	https://www.auto-data.net/en/pontiac-trans-sport-3.8-i-v6-175hp-5988
EU-PONTIAC-TRANS-SPORT-II-MPV-SWB-01	4750	1845	1710	Auto-Data Pontiac Trans Sport II 3.4 V6 specifications	https://www.auto-data.net/en/pontiac-trans-sport-ii-3.4-i-v6-182hp-5984
EU-PORSCHE-911-901-COUPE-STANDARD-01	4163	1610	1320	Automobile-Catalog Porsche 911 specifications	https://www.automobile-catalog.com/car/1964/2588450/porsche_911.html
EU-PORSCHE-911-901-TARGA-STANDARD-01	4147	1610	1320	Automobile-Catalog 1972 Porsche 911 T Targa specifications	https://www.automobile-catalog.com/car/1972/2590490/porsche_911_t_coupe_5-speed.html
EU-PORSCHE-911-930-COUPE-TURBO-01	4291	1775	1320	Automobile-Catalog Porsche 911 Turbo specifications	https://www.automobile-catalog.com/car/1976/2650340/porsche_911_turbo.html
EU-PORSCHE-911-930-CONVERTIBLE-TURBO-01	4291	1775	1310	Auto-Data Porsche 911 Cabriolet Type 930 specifications	https://www.auto-data.net/en/porsche-911-cabriolet-type-930-3.3-turbo-300hp-6660
EU-PORSCHE-911-996-COUPE-CARRERA-01	4430	1765	1305	Auto-Data Porsche 911 996 Carrera specifications	https://www.auto-data.net/en/porsche-911-996-carrera-3.4-300hp-6591
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305	Auto-Data Porsche 911 Cabriolet 996 Carrera specifications	https://www.auto-data.net/en/porsche-911-cabriolet-996-carrera-3.4-300hp-6601
EU-PORSCHE-911-991-1-COUPE-CARRERA-01	4491	1808	1303	Porsche 911 Carrera Coupe official specifications	https://newsroom.porsche.com/dam/jcr%3A269452dc-fbc5-4684-8ae2-1bae59290fd7/Specifications_911_Carrera_Coupe.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-01	4499	1808	1294	Porsche 2017 911 Carrera official specifications	https://newsroom.porsche.com/dam/jcr%3A8a8a3990-34a8-4ae0-a11e-f4bb53abd5e0/2017_911_Carrera_and_Carrera_S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-01	4499	1808	1289	Porsche 2017 911 Carrera official specifications	https://newsroom.porsche.com/dam/jcr%3A8a8a3990-34a8-4ae0-a11e-f4bb53abd5e0/2017_911_Carrera_and_Carrera_S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-01	4499	1852	1289	Porsche 2017 911 Carrera 4 official specifications	https://newsroom.porsche.com/dam/jcr%3A60826685-395e-47f8-a50b-046abff854cb/2017_911_Carrera_4_and_Carrera_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-4-01	4499	1852	1294	Porsche 2017 911 Carrera 4 official specifications	https://newsroom.porsche.com/dam/jcr%3A60826685-395e-47f8-a50b-046abff854cb/2017_911_Carrera_4_and_Carrera_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-TARGA-CARRERA-4-01	4499	1852	1288	Porsche 2017 911 Targa 4 official specifications	https://newsroom.porsche.com/dam/jcr%3A455adda8-a3e6-4c88-a857-decd40900e74/2017_911_Targa_4_and_Targa_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-4-GTS-01	4528	1852	1299	Porsche 2018 911 GTS official specifications	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4-GTS-01	4528	1852	1293	Porsche 2018 911 GTS official specifications	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-TARGA-CARRERA-4-GTS-01	4528	1852	1291	Porsche 2018 911 GTS official specifications	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-4S-01	4499	1852	1291	Porsche 2017 911 Carrera 4S official specifications	https://newsroom.porsche.com/dam/jcr%3A60826685-395e-47f8-a50b-046abff854cb/2017_911_Carrera_4_and_Carrera_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-4S-01	4499	1852	1296	Porsche 2017 911 Carrera 4S official specifications	https://newsroom.porsche.com/dam/jcr%3A60826685-395e-47f8-a50b-046abff854cb/2017_911_Carrera_4_and_Carrera_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-TARGA-CARRERA-4S-01	4499	1852	1293	Porsche 2017 911 Targa 4S official specifications	https://newsroom.porsche.com/dam/jcr%3A455adda8-a3e6-4c88-a857-decd40900e74/2017_911_Targa_4_and_Targa_4S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-GTS-01	4528	1852	1297	Porsche 2018 911 GTS official specifications	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-GTS-01	4528	1852	1291	Porsche 2018 911 GTS official specifications	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-COUPE-CARRERA-S-01	4499	1808	1296	Porsche 2017 911 Carrera S official specifications	https://newsroom.porsche.com/dam/jcr%3A8a8a3990-34a8-4ae0-a11e-f4bb53abd5e0/2017_911_Carrera_and_Carrera_S_Technical_Specifications.pdf
EU-PORSCHE-911-991-2-CONVERTIBLE-CARRERA-S-01	4499	1808	1291	Porsche 2017 911 Carrera S official specifications	https://newsroom.porsche.com/dam/jcr%3A8a8a3990-34a8-4ae0-a11e-f4bb53abd5e0/2017_911_Carrera_and_Carrera_S_Technical_Specifications.pdf
EU-PORSCHE-911-992-1-COUPE-GTS-01	4533	1852	1301	Auto-Data Porsche 911 992 Carrera GTS specifications	https://www.auto-data.net/en/porsche-911-992-carrera-gts-3.0-480hp-pdk-43906
EU-PORSCHE-911-992-1-CONVERTIBLE-GTS-01	4533	1852	1300	Auto-Data Porsche 911 Cabriolet 992 Carrera GTS specifications	https://www.auto-data.net/en/porsche-911-cabriolet-992-carrera-gts-3.0-480hp-pdk-43918
EU-PORSCHE-911-992-1-COUPE-CARRERA-T-01	4530	1852	1293	Auto-Data Porsche 911 992 Carrera T specifications	https://www.auto-data.net/en/porsche-911-992-carrera-t-3.0-385hp-46702
EU-PORSCHE-911-992-1-COUPE-DAKAR-01	4530	1864	1338	Porsche 911 Dakar official technical data	https://newsroom.porsche.com/dam/jcr%3A5cac90b3-71ec-4021-b0fd-ec1e4bbfc087/pag-911-dakar-td-en.pdf
EU-PORSCHE-911-992-2-COUPE-CARRERA-01	4542	1852	1298	Porsche 992.2 911 Carrera official specifications	https://newsroom.porsche.com/dam/jcr%3A86fc9a9b-ece1-4cca-9930-39a78e89baf3/992.2%20911%20Carrera%20and%20Carrera%20Cabriolet%20Technical%20Specifications.pdf
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-01	4542	1852	1301	Porsche 992.2 911 Carrera official specifications	https://newsroom.porsche.com/dam/jcr%3A86fc9a9b-ece1-4cca-9930-39a78e89baf3/992.2%20911%20Carrera%20and%20Carrera%20Cabriolet%20Technical%20Specifications.pdf
EU-PORSCHE-911-992-2-COUPE-CARRERA-S-01	4542	1852	1303	Porsche 992.2 911 Carrera S official specifications	https://newsroom.porsche.com/dam/jcr%3Abfdc5085-68fd-4472-9a20-6ea1d0c8cf44/Type%20992.2%20911%20Carrera%20S%20and%20911%20Carrera%20S%20Cabriolet%20U.S.%20specifications.pdf
EU-PORSCHE-911-992-2-CONVERTIBLE-CARRERA-S-01	4542	1852	1302	Porsche 992.2 911 Carrera S official specifications	https://newsroom.porsche.com/dam/jcr%3Abfdc5085-68fd-4472-9a20-6ea1d0c8cf44/Type%20992.2%20911%20Carrera%20S%20and%20911%20Carrera%20S%20Cabriolet%20U.S.%20specifications.pdf
EU-PORSCHE-911-992-2-COUPE-CARRERA-T-01	4542	1852	1293	Porsche 992.2 911 Carrera T official specifications	https://newsroom.porsche.com/dam/jcr%3Af10cc150-9305-4c43-a2ed-58e80d098f9b/992.2%20911%20Carrera%20T%20and%20Carrera%20T%20Cabriolet%20Technical%20Specifications.pdf
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_13401-13500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.polestar.com/ie/polestar-5/specifications/ "https://www.polestar.com/ie/polestar-5/specifications/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5075 行）
- 累计尺寸组：dimension_groups_final.tsv（1385 行）

