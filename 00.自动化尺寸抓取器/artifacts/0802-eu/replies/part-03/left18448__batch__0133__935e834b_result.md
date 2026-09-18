# 任务：left18448 第 13201-13300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0133__935e834b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13201-13300 行

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
left18448 第 13201-13300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13201-13300_ktype_dimension_mapping_final.tsv
- left18448_13201-13300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Peugeot	508 sw i	2.0 HDI RXH Hybrid4	Kombi	Allrad	Diesel/Elektro	Nov 2010	Dec 2018	106512
Peugeot	508 sw ii	Hybrid 180	Kombi	Frontantrieb	Benzin/Elektro	Mar 2023	-	154617
Peugeot	Bipper	1.3 HDI 80	Großraumlimousine	Frontantrieb	Diesel	Dec 2015	-	118702
Peugeot	Boxer	2	Bus	Frontantrieb	Benzin	Dec 2001	Jun 2006	16642
Peugeot	Boxer	2	Kasten	Frontantrieb	Benzin	Dec 2001	Jun 2006	16755
Peugeot	Boxer	1.9 D	Kasten	Frontantrieb	Diesel	Jul 1999	Apr 2002	14753
Peugeot	Boxer	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Apr 2002	118853
Peugeot	Boxer	1.9 TD	Kasten	Frontantrieb	Diesel	Jul 1999	Apr 2002	14754
Peugeot	Boxer	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1994	Apr 2002	14866
Peugeot	Boxer	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 1994	Apr 2002	14867
Peugeot	Boxer	2.0 Bluehdi 110	Bus	Frontantrieb	Diesel	Jul 2015	Sep 2019	116453
Peugeot	Boxer	2.0 Bluehdi 110	Kasten	Frontantrieb	Diesel	Mar 2016	Sep 2019	120718
Peugeot	Boxer	2.0 Bluehdi 110	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2016	Sep 2019	120845
Peugeot	Boxer	2.0 Bluehdi 130	Bus	Frontantrieb	Diesel	Jul 2015	Sep 2019	116454
Peugeot	Boxer	2.0 Bluehdi 130	Kasten	Frontantrieb	Diesel	Mar 2016	Sep 2019	120719
Peugeot	Boxer	2.0 Bluehdi 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2016	Sep 2019	120846
Peugeot	Boxer	2.0 Bluehdi 160	Bus	Frontantrieb	Diesel	Jul 2015	Sep 2019	116508
Peugeot	Boxer	2.0 Bluehdi 160	Kasten	Frontantrieb	Diesel	Mar 2016	Dec 2023	120720
Peugeot	Boxer	2.0 Bluehdi 160	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2016	Dec 2023	120847
Peugeot	Boxer	2.0 HDI	Bus	Frontantrieb	Diesel	Dec 2001	Jun 2006	16643
Peugeot	Boxer	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2001	Jun 2006	16748
Peugeot	Boxer	2.0 HDI	Kasten	Frontantrieb	Diesel	Apr 2002	Jun 2006	16752
Peugeot	Boxer	2.0 HDI	Kasten	Frontantrieb	Diesel	Aug 2001	Apr 2002	17923
Peugeot	Boxer	2.0 I	Kasten	Frontantrieb	Benzin	Jun 1994	Apr 2002	11083
Peugeot	Boxer	2.0 I	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jun 1994	Apr 2002	11086
Peugeot	Boxer	2.0 I 4X4	Bus	Allrad	Benzin	Aug 1996	Apr 2002	7875
Peugeot	Boxer	2.2 Bluehdi 120	Kasten	Frontantrieb	Diesel	Nov 2023	-	157466
Peugeot	Boxer	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	157469
Peugeot	Boxer	2.2 Bluehdi 140	Kasten	Frontantrieb	Diesel	Nov 2023	-	157467
Peugeot	Boxer	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	157470
Peugeot	Boxer	2.2 Bluehdi 180	Kasten	Frontantrieb	Diesel	Nov 2023	-	157468
Peugeot	Boxer	2.2 Bluehdi 180	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2023	-	157471
Peugeot	Boxer	2.2 HDI	Bus	Frontantrieb	Diesel	Dec 2001	Jun 2006	16644
Peugeot	Boxer	2.2 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2001	Jun 2006	16750
Peugeot	Boxer	2.2 HDI	Kasten	Frontantrieb	Diesel	Dec 2001	Jun 2006	16754
Peugeot	Boxer	2.2 HDI 110	Bus	Frontantrieb	Diesel	Mar 2011	Dec 2020	11107
Peugeot	Boxer	2.2 HDI 110	Kasten	Frontantrieb	Diesel	Mar 2011	Dec 2020	11112
Peugeot	Boxer	2.2 HDI 110	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2011	Dec 2020	11115
Peugeot	Boxer	2.2 HDI 130	Bus	Frontantrieb	Diesel	Mar 2011	-	11108
Peugeot	Boxer	2.2 HDI 130	Kasten	Frontantrieb	Diesel	Mar 2011	-	11113
Peugeot	Boxer	2.2 HDI 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2006	-	11116
Peugeot	Boxer	2.2 HDI 130	Pritsche/Fahrgestell	Allrad	Diesel	Mar 2011	-	150604
Peugeot	Boxer	2.2 HDI 150	Bus	Frontantrieb	Diesel	Mar 2011	-	11109
Peugeot	Boxer	2.2 HDI 150	Kasten	Frontantrieb	Diesel	Mar 2011	-	11114
Peugeot	Boxer	2.2 HDI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2011	-	11117
Peugeot	Boxer	2.2 HDI 150	Pritsche/Fahrgestell	Allrad	Diesel	Mar 2011	-	150605
Peugeot	Boxer	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Apr 2002	11084
Peugeot	Boxer	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 1999	Apr 2002	14869
Peugeot	Boxer	2.5 D 4X4	Kasten	Allrad	Diesel	Jul 1999	Apr 2002	14871
Peugeot	Boxer	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Dec 1997	11085
Peugeot	Boxer	2.5 TDI	Kasten	Frontantrieb	Diesel	Jan 1997	Apr 2002	10692
Peugeot	Boxer	2.5 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 1997	Apr 2002	11087
Peugeot	Boxer	2.5 TDI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 1999	Apr 2002	14868
Peugeot	Boxer	2.5 TDI 4X4	Kasten	Allrad	Diesel	Jul 1999	Apr 2002	14870
Peugeot	Boxer	2.8 HDI	Bus	Frontantrieb	Diesel	Nov 2000	Apr 2002	15696
Peugeot	Boxer	2.8 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2000	Apr 2002	15697
Peugeot	Boxer	2.8 HDI	Kasten	Frontantrieb	Diesel	Nov 2000	Apr 2002	15698
Peugeot	Boxer	2.8 HDI	Bus	Frontantrieb	Diesel	Dec 2001	Jun 2006	16645
Peugeot	Boxer	2.8 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2001	Jun 2006	16749
Peugeot	Boxer	2.8 HDI	Kasten	Frontantrieb	Diesel	Dec 2001	Jun 2006	16753
Peugeot	Boxer	2.8 HDI 4X4	Bus	Allrad	Diesel	Dec 2001	Jun 2006	16756
Peugeot	Boxer	2.8 HDI 4X4	Kasten	Allrad	Diesel	Dec 2001	Jun 2006	16757
Peugeot	Boxer	2.8 HDI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Dec 2001	Jun 2006	16758
Peugeot	Boxer	3.0 HDI 175	Bus	Frontantrieb	Diesel	Mar 2011	-	11110
Peugeot	Boxer	3.0 HDI 175	Kasten	Frontantrieb	Diesel	Mar 2011	-	11111
Peugeot	Boxer	3.0 HDI 175	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2011	-	11118
Peugeot	Boxer	E-boxer	Kasten	Frontantrieb	Elektro	Jul 2021	Oct 2023	145321
Peugeot	Boxer	E-boxer	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2021	Oct 2023	151716
Peugeot	Boxer	E-boxer	Kasten	Frontantrieb	Elektro	Nov 2023	-	157472
Peugeot	Boxer	E-boxer	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2023	-	157473
Peugeot	Boxer	E-boxer Hydrogen	Kasten	Frontantrieb	Wasserstoff/Elektro	Apr 2025	-	802129
Peugeot	Expert	2	Bus	Frontantrieb	Benzin	Jul 2000	Dec 2006	15115
Peugeot	Expert	2	Kasten	Frontantrieb	Benzin	Sep 2002	Dec 2006	17505
Peugeot	Expert	1.6 Bluehdi 115	Kasten	Frontantrieb	Diesel	Apr 2016	Dec 2019	120076
Peugeot	Expert	1.6 Bluehdi 95	Kasten	Frontantrieb	Diesel	Apr 2016	Dec 2019	120075
Peugeot	Expert	1.6 Bluehdi 95	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Dec 2019	125133
Peugeot	Expert	1.6 HDI 90 8V	Bus	Frontantrieb	Diesel	Jan 2007	Mar 2016	107957
Peugeot	Expert	1.6 HDI 90 8V	Kasten	Frontantrieb	Diesel	Jan 2007	-	107958
Peugeot	Expert	1.6 HDI 90 8V	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2007	-	119825
Peugeot	Expert	1.9 D 70	Kasten	Frontantrieb	Diesel	Dec 1998	Dec 2006	18310
Peugeot	Expert	2.0 16V	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jan 2007	Mar 2016	144167
Peugeot	Expert	2.0 Bluehdi 120	Kasten	Frontantrieb	Diesel	Apr 2016	Dec 2022	120077
Peugeot	Expert	2.0 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Dec 2022	125134
Peugeot	Expert	2.0 Bluehdi 145	Bus	Frontantrieb	Diesel	Jul 2021	Apr 2025	144861
Peugeot	Expert	2.0 Bluehdi 145	Kasten	Frontantrieb	Diesel	Aug 2021	Apr 2025	145137
Peugeot	Expert	2.0 Bluehdi 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2023	Apr 2025	152623
Peugeot	Expert	2.0 Bluehdi 150	Kasten	Frontantrieb	Diesel	Apr 2016	Dec 2022	120078
Peugeot	Expert	2.0 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2016	Dec 2022	125135
Peugeot	Expert	2.0 Bluehdi 180	Kasten	Frontantrieb	Diesel	Apr 2016	Apr 2025	120079
Peugeot	Expert	2.0 HDI	Bus	Frontantrieb	Diesel	Jul 2000	Dec 2006	15116
Peugeot	Expert	2.0 HDI	Kasten	Frontantrieb	Diesel	Jul 2000	Dec 2006	15117
Peugeot	Expert	2.0 HDI	Kasten	Frontantrieb	Diesel	Jul 2000	Dec 2006	17226
Peugeot	Expert	2.0 HDI	Kasten	Frontantrieb	Diesel	Jul 2000	Dec 2006	18279
Peugeot	Expert	2.0 HDI 100	Bus	Frontantrieb	Diesel	Mar 2011	Mar 2016	11125
Peugeot	Expert	2.0 HDI 100	Kasten	Frontantrieb	Diesel	Mar 2011	-	11128
Peugeot	Expert	2.0 HDI 120 4X4	Bus	Allrad	Diesel	Jan 2007	Mar 2016	5983
Peugeot	Expert	2.0 HDI 120 4X4	Kasten	Allrad	Diesel	Jan 2010	-	109724
Peugeot	Expert	2.0 HDI 130	Bus	Frontantrieb	Diesel	Mar 2011	-	11126
Peugeot	Expert	2.0 HDI 130	Kasten	Frontantrieb	Diesel	Mar 2011	-	11130
Peugeot	Expert	2.0 HDI 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2011	-	119826


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成 Peugeot 508、Bipper、Boxer、Expert 的聚类、尺寸建组及复用。
* 发动机、能源、驱动形式和未改变物理外廓的改款标签未重复建组。
* 商用车未提供轴距、车顶或平台级别时，统一采用该代标准量产外廓，没有展开无证据分支。
* 508、Boxer 和 Expert 的关键三维已由 ADAC、Peugeot 官方规格页、车主手册及可追溯规格资料闭合。([ADAC][1])

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：14
* 机械终检：固定表头、列数、ID 唯一性、引用闭合、正整数三维、来源非空及无孤立组均通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106512	106512	Wagon	508 I RXH		5	EU-PEUGEOT-508-I-RXH-WAGON-01	HIGH		READY
154617	154617	Wagon	508 II Facelift		5	EU-PEUGEOT-508-II-FACELIFT-WAGON-01	HIGH		READY
118702	118702	MPV	Bipper I		5	EU-PEUGEOT-BIPPER-I-MPV-01	HIGH		READY
16642	16642	MPV	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16755	16755	Van	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
14753	14753	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
118853	118853	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14754	14754	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
14866	14866	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14867	14867	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
116453	116453	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120718	120718	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120845	120845	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
116454	116454	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120719	120719	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120846	120846	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
116508	116508	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120720	120720	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
120847	120847	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
16643	16643	MPV	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16748	16748	Pickup	Boxer II	244		EU-PEUGEOT-BOXER-II-244-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
16752	16752	Van	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
17923	17923	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11083	11083	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11086	11086	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
7875	7875	MPV	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
157466	157466	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
157469	157469	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
157467	157467	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
157470	157470	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
157468	157468	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
157471	157471	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
16644	16644	MPV	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16750	16750	Pickup	Boxer II	244		EU-PEUGEOT-BOXER-II-244-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
16754	16754	Van	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11107	11107	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11112	11112	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11115	11115	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
11108	11108	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11113	11113	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11116	11116	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
150604	150604	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
11109	11109	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11114	11114	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11117	11117	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
150605	150605	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
11084	11084	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14869	14869	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14871	14871	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11085	11085	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
10692	10692	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11087	11087	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14868	14868	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
14870	14870	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
15696	15696	MPV	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
15697	15697	Pickup	Boxer I	230		EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
15698	15698	Van	Boxer I	230		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16645	16645	MPV	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16749	16749	Pickup	Boxer II	244		EU-PEUGEOT-BOXER-II-244-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
16753	16753	Van	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16756	16756	MPV	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16757	16757	Van	Boxer II	244		EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
16758	16758	Pickup	Boxer II	244		EU-PEUGEOT-BOXER-II-244-CHASSIS-SCAB-SWB-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
11110	11110	MPV	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11111	11111	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
11118	11118	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
145321	145321	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
151716	151716	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
157472	157472	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
157473	157473	Pickup	Boxer III	250		EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	MEDIUM	未提供轴距/驾驶室级别，采用该代标准单排底盘驾驶室外廓。	READY
802129	802129	Van	Boxer III	250		EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	MEDIUM	未提供轴距/车顶级别，采用该代标准量产外廓。	READY
15115	15115	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
17505	17505	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
120076	120076	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
120075	120075	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
125133	125133	Pickup	Expert III			EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
107957	107957	MPV	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
107958	107958	Van	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
119825	119825	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
18310	18310	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
144167	144167	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
120077	120077	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
125134	125134	Pickup	Expert III			EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
144861	144861	MPV	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
145137	145137	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
152623	152623	Pickup	Expert III			EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
120078	120078	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
125135	125135	Pickup	Expert III			EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
120079	120079	Van	Expert III			EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
15116	15116	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
15117	15117	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
17226	17226	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
18279	18279	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
11125	11125	MPV	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
11128	11128	Van	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
5983	5983	MPV	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
109724	109724	Van	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
11126	11126	MPV	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
11130	11130	Van	Expert II			EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	MEDIUM	未提供轴距/车身长度级别，采用该代标准量产外廓。	READY
119826	119826	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	MEDIUM	未提供轴距/平台级别，采用该代标准平台驾驶室外廓。	READY
```

[下载 left18448_13201-13300_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_13201-13300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-508-I-RXH-WAGON-01	4823	1864	1525	ADAC vehicle catalogue	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/508/1generation/231406/
EU-PEUGEOT-508-II-FACELIFT-WAGON-01	4778	1859	1420	Peugeot UK official 508 SW specifications	https://www.peugeot.co.uk/content/peugeot/worldwide/uk/en/index/models/508-sw.html
EU-PEUGEOT-BIPPER-I-MPV-01	3959	1716	1721	ADAC vehicle catalogue	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/bipper/1generation/214385/
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	AutoGidas vehicle catalogue	https://autogidas.lt/en/auto-katalogas/peugeot/boxer/1000-td-270c-1994-1998-k37737
EU-PEUGEOT-BOXER-I-230-CHASSIS-SCAB-SWB-01	4655	1998	2150	ParuVendu technical specifications	https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot-boxer/310-c-2-5-td-8-cv-diesel/3057505/
EU-PEUGEOT-BOXER-II-244-STANDARD-SWB-H1-01	4749	2024	2150	Peugeot Boxer 2002 owner manual	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-II-244-CHASSIS-SCAB-SWB-01	4831	2024	2100	Peugeot Boxer 2002 owner manual; standard value from listed 2100-2125 mm cab range	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-III-250-STANDARD-L1H1-01	4963	2050	2254	Honest John Vans specifications	https://vans.honestjohn.co.uk/specs/detail/?v=PEUBOX0114
EU-PEUGEOT-BOXER-III-250-CHASSIS-SCAB-L1-01	4908	2050	2254	Peugeot Boxer 2021 owner manual	https://www.carmanualsonline.info/peugeot-boxer-2021-owners-manual/16
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940	VinDecoderz vehicle specifications	https://www.vindecoderz.com/EN/Peugeot/Expert/2000/2.0%20MT/specs-features/25913
EU-PEUGEOT-EXPERT-II-STANDARD-L1H1-01	4813	1895	1942	CarsGuide vehicle dimensions	https://www.carsguide.com.au/peugeot/expert/car-dimensions/2009
EU-PEUGEOT-EXPERT-II-PLATFORM-CAB-L2-01	5016	1895	1942	Citroen Dispatch brochure; shared Expert/Dispatch platform cab	https://citroen.manymanuals.com/cars/dispatch-crew-van/brochure-16949/12
EU-PEUGEOT-EXPERT-III-K0-STANDARD-M-H1-01	4959	1920	1940	Peugeot Australia official Expert specifications	https://www.peugeot.com.au/models/expert-van/specifications.html
EU-PEUGEOT-EXPERT-III-K0-PLATFORM-CAB-M-01	4959	1920	1899	Auto Express vehicle specifications	https://www.autoexpress.co.uk/peugeot/expert/355958/peugeot-e-expert-review/prices-specs/39602/1200-1.6-bluehdi-95-platform-cab
```

[下载 left18448_13201-13300_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_13201-13300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/508/1generation/231406/?utm_source=chatgpt.com "Peugeot 508 RXH HYbrid4 Automatik (04/12 - 07/14): Technische Daten, Bilder, Preise | ADAC"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4875 行）
- 累计尺寸组：dimension_groups_final.tsv（1315 行）

