# 任务：left18448 第 7501-7600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0076__5e6e5c2c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7501-7600 行

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
left18448 第 7501-7600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7501-7600_ktype_dimension_mapping_final.tsv
- left18448_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
JAC	E-Js4	EV	SUV	Frontantrieb	Elektro	Apr 2023	-	154496
JAC	Iev6e	EV	Schrägheck	Frontantrieb	Elektro	May 2017	-	127454
JAC	M3	EV	Kasten	Heckantrieb	Elektro	Apr 2024	-	801529
JAC	T8 pro	2	Pick-up	Allrad	Diesel	Oct 2025	-	802526
JAC	T8 pro	2.0 4WD	Pick-up	Allrad	Diesel	Oct 2025	-	802631
JAC	T8 pro	2.4 4WD	Pick-up	Allrad	Benzin	Nov 2023	-	157040
JAC	T8 pro	2.4 LPG 4WD	Pick-up	Allrad	Benzin/Autogas (LPG)	Nov 2023	-	157041
Jaecoo	5	1.5 Shs-h	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	163290
Jaecoo	5	1.6 T	SUV	Frontantrieb	Benzin	Jul 2025	-	162196
Jaecoo	5	1.6 T AWD	SUV	Allrad	Benzin	Jul 2025	-	162197
Jaecoo	5	EV	SUV	Frontantrieb	Elektro	Aug 2025	-	162364
Jaecoo	8	1.5 Shs-p AWD	SUV	Allrad	Benzin/Elektro	Apr 2026	-	164734
Jaecoo	J7	1.6	SUV	Frontantrieb	Benzin	Oct 2024	-	801213
Jaecoo	J7	1.6 AWD	SUV	Allrad	Benzin	Oct 2024	-	801214
Jaecoo	J7	Phev	SUV	Frontantrieb	Benzin/Elektro	Jan 2025	-	801266
Jaecoo	J7	Shs-h	SUV	Frontantrieb	Benzin/Elektro	Mar 2026	-	803323
Jaecoo	J7	Shs-p	SUV	Frontantrieb	Benzin/Elektro	Mar 2026	-	803322
Jaguar	E-Pace	1.5 P160 Mhev	SUV	Frontantrieb	Benzin/Elektro	Nov 2020	-	142718
Jaguar	E-Pace	1.5 P270e Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158498
Jaguar	E-Pace	1.5 P300e Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Nov 2020	-	142723
Jaguar	E-Pace	2.0 AWD	SUV	Allrad	Benzin	Sep 2017	-	127974
Jaguar	E-Pace	2.0 D150	SUV	Frontantrieb	Diesel	Sep 2017	-	127975
Jaguar	E-Pace	2.0 D150 AWD	SUV	Allrad	Diesel	Sep 2017	-	127976
Jaguar	E-Pace	2.0 D165	SUV	Frontantrieb	Diesel	Nov 2020	-	142715
Jaguar	E-Pace	2.0 D165 Mhev AWD	SUV	Allrad	Diesel/Elektro	Nov 2020	-	142716
Jaguar	E-Pace	2.0 D180 AWD	SUV	Allrad	Diesel	Sep 2017	-	127977
Jaguar	E-Pace	2.0 D200 Mhev AWD	SUV	Allrad	Diesel/Elektro	Nov 2020	-	142717
Jaguar	E-Pace	2.0 D240 AWD	SUV	Allrad	Diesel	Sep 2017	-	127978
Jaguar	E-Pace	2.0 Flexfuel AWD	SUV	Allrad	Benzin/Ethanol	Apr 2023	-	153717
Jaguar	E-Pace	2.0 P200 AWD	SUV	Allrad	Benzin	Sep 2017	-	127973
Jaguar	E-Pace	2.0 P200 Mhev AWD	SUV	Allrad	Benzin/Elektro	Nov 2020	-	142719
Jaguar	E-Pace	2.0 P200 Mhev Flex AWD	SUV	Allrad	Benzin/Ethanol/Elektro	Nov 2020	-	153259
Jaguar	E-Pace	2.0 P250 Mhev AWD	SUV	Allrad	Benzin/Elektro	Nov 2020	-	142720
Jaguar	E-Pace	2.0 P300 Mhev AWD	SUV	Allrad	Benzin/Elektro	Nov 2020	-	142721
Jaguar	F-Pace	2.0 D165 Mhev	SUV	Allrad	Diesel/Elektro	Oct 2020	-	142704
Jaguar	F-Pace	2.0 D200 Mhev	SUV	Allrad	Diesel/Elektro	Oct 2020	-	142705
Jaguar	F-Pace	2.0 P400e Plug-in Hybrid	SUV	Allrad	Benzin/Elektro	Oct 2020	-	142711
Jaguar	F-Pace	2.0 SD4 AWD	SUV	Allrad	Diesel	Feb 2017	-	126021
Jaguar	F-Pace	2.0 TD4	SUV	Heckantrieb	Diesel	Sep 2015	-	117715
Jaguar	F-Pace	2.0 TD4	SUV	Heckantrieb	Diesel	Feb 2017	-	126020
Jaguar	F-Pace	2.0 TD4 AWD	SUV	Allrad	Diesel	Sep 2015	-	117716
Jaguar	F-Pace	2.0 TI4 AWD	SUV	Allrad	Benzin	Feb 2017	-	126022
Jaguar	F-Pace	2.0 TI4 AWD	SUV	Allrad	Benzin	Jun 2017	-	127990
Jaguar	F-Pace	3.0 D300 AWD	SUV	Allrad	Diesel	Oct 2020	-	801121
Jaguar	F-Pace	3.0 D300 Mhev	SUV	Allrad	Diesel/Elektro	Oct 2020	-	142708
Jaguar	F-Pace	3.0 P400 Mhev	SUV	Allrad	Benzin/Elektro	Oct 2020	-	142709
Jaguar	F-Pace	3.0 Scv6 AWD	SUV	Allrad	Benzin	Sep 2015	-	117712
Jaguar	F-Pace	3.0 Scv6 AWD	SUV	Allrad	Benzin	Sep 2015	-	117713
Jaguar	F-Pace	3.0 Sdv6 AWD	SUV	Allrad	Diesel	Sep 2015	-	117714
Jaguar	F-Pace	5.0 SVR P550 Mhev	SUV	Allrad	Benzin/Elektro	Oct 2020	-	142710
Jaguar	F-Pace	5.0 SVR P575	SUV	Allrad	Benzin	Feb 2023	-	156548
Jaguar	F-Type	2.0 TI4	Coupe	Heckantrieb	Benzin	Jul 2017	-	126887
Jaguar	F-Type	2.0 TI4	Cabriolet	Heckantrieb	Benzin	Jul 2017	-	126888
Jaguar	F-Type	3.0 Scv6	Cabriolet	Heckantrieb	Benzin	Oct 2012	-	57131
Jaguar	F-Type	3.0 Scv6	Coupe	Heckantrieb	Benzin	Oct 2013	-	100686
Jaguar	F-Type	3.0 Scv6 400 Sport	Coupe	Heckantrieb	Benzin	Nov 2016	-	125815
Jaguar	F-Type	3.0 Scv6 400 Sport AWD	Coupe	Allrad	Benzin	Nov 2016	-	125817
Jaguar	F-Type	3.0 Scv6 S	Cabriolet	Heckantrieb	Benzin	Oct 2012	-	57133
Jaguar	F-Type	3.0 Scv6 S	Coupe	Heckantrieb	Benzin	Oct 2013	-	100687
Jaguar	F-Type	3.0 Scv6 S AWD	Cabriolet	Allrad	Benzin	Dec 2014	-	109349
Jaguar	F-Type	3.0 Scv6 S AWD	Coupe	Allrad	Benzin	Dec 2014	-	109350
Jaguar	F-Type	5.0 Scv8 R	Coupe	Heckantrieb	Benzin	Oct 2013	-	100688
Jaguar	F-Type	5.0 Scv8 R	Cabriolet	Heckantrieb	Benzin	Oct 2013	-	109352
Jaguar	F-Type	5.0 Scv8 R AWD	Coupe	Allrad	Benzin	Dec 2014	-	109351
Jaguar	F-Type	5.0 Scv8 R AWD	Cabriolet	Allrad	Benzin	Dec 2014	-	109353
Jaguar	F-Type	5.0 Scv8 S	Cabriolet	Heckantrieb	Benzin	Oct 2012	-	57134
Jaguar	F-Type	5.0 Scv8 SVR / Scv8 P575 R	Coupe	Allrad	Benzin	Dec 2015	-	118546
Jaguar	F-Type	5.0 Scv8 SVR / Scv8 P575 R AWD	Cabriolet	Allrad	Benzin	Dec 2015	-	117709
Jaguar	F-Type	Scv6 400 Sport	Cabriolet	Heckantrieb	Benzin	Nov 2016	-	125818
Jaguar	F-Type	Scv6 400 Sport AWD	Cabriolet	Allrad	Benzin	Nov 2016	-	125819
Jaguar	I-Pace	Ev320 AWD	SUV	Allrad	Elektro	Oct 2020	-	142696
Jaguar	Mk i	3.4	Stufenheck	Heckantrieb	Benzin	Sep 1955	Sep 1959	59960
Jaguar	Mk ii	240	Stufenheck	Heckantrieb	Benzin	Sep 1959	Oct 1969	58389
Jaguar	Mk ii	340	Stufenheck	Heckantrieb	Benzin	Sep 1955	Oct 1970	58390
Jaguar	Mk ii	3.8 S	Stufenheck	Heckantrieb	Benzin	Sep 1959	Sep 1966	58394
Jaguar	Mk vii	3.4	Stufenheck	Heckantrieb	Benzin	May 1950	Oct 1956	58410
Jaguar	Mk vii	3.4	Stufenheck	Heckantrieb	Benzin	Jul 1954	Oct 1956	58411
Jaguar	Mk viii	3.4	Stufenheck	Heckantrieb	Benzin	May 1956	Oct 1958	100929
Jaguar	Mk viii	3.4	Stufenheck	Heckantrieb	Benzin	May 1956	Oct 1958	100930
Jaguar	Mk x i	4.2	Stufenheck	Heckantrieb	Benzin	Sep 1961	Jul 1968	58419
Jaguar	Mk x i	420g	Stufenheck	Heckantrieb	Benzin	Sep 1966	Oct 1970	58392
Jaguar	S-Type i	3.4	Stufenheck	Heckantrieb	Benzin	May 1963	Aug 1968	58425
Jaguar	S-Type i	3.8	Stufenheck	Heckantrieb	Benzin	May 1963	Aug 1968	58433
Jaguar	S-Type ii	2.5 V6	Stufenheck	Heckantrieb	Benzin	Apr 2002	Oct 2007	16696
Jaguar	S-Type ii	2.7 D	Stufenheck	Heckantrieb	Diesel	Jun 2004	Oct 2007	18021
Jaguar	S-Type ii	3.0 V6	Stufenheck	Heckantrieb	Benzin	Jan 1999	Oct 2007	10279
Jaguar	S-Type ii	4.0 V8	Stufenheck	Heckantrieb	Benzin	Jan 1999	Apr 2002	10280
Jaguar	S-Type ii	4.2 V8	Stufenheck	Heckantrieb	Benzin	Apr 2002	Oct 2007	16697
Jaguar	S-Type ii	R 4,2 V8	Stufenheck	Heckantrieb	Benzin	Apr 2002	Oct 2007	16698
Jaguar	Xe	2	Stufenheck	Heckantrieb	Benzin	Mar 2015	-	108185
Jaguar	Xe	2	Stufenheck	Heckantrieb	Benzin	Mar 2015	-	108186
Jaguar	Xe	2	Stufenheck	Heckantrieb	Benzin	Feb 2017	-	126746
Jaguar	Xe	2.0 AWD	Stufenheck	Allrad	Benzin	Feb 2017	-	126747
Jaguar	Xe	2.0 AWD	Stufenheck	Allrad	Benzin	Jun 2017	-	127991
Jaguar	Xe	2.0 D	Stufenheck	Heckantrieb	Diesel	Mar 2015	-	108183
Jaguar	Xe	2.0 D	Stufenheck	Heckantrieb	Diesel	Mar 2015	-	108184
Jaguar	Xe	2.0 D AWD	Stufenheck	Allrad	Diesel	Oct 2015	-	117794
Jaguar	Xe	2.0 D AWD	Stufenheck	Allrad	Diesel	Feb 2017	-	126745
Jaguar	Xe	2.0 D200 Mhev	Stufenheck	Heckantrieb	Diesel/Elektro	Nov 2020	-	142688
Jaguar	Xe	2.0 D200 Mhev AWD	Stufenheck	Allrad	Diesel/Elektro	Nov 2020	-	142689


--- Round 1 / 首次发送 ---
## 更新点

已完成外廓聚类、尺寸组复用和机械终检。仅对有明确三维差异的分支进行拆分：

* F-PACE 区分改款前、普通改款后和 SVR；官方资料显示普通改款车型与 SVR 的车长不同。([汽车尺寸比较网][1])
* F-TYPE 的组合 Ktype `118546`、`117709` 按 SVR 与后期 P575 R 外廓拆分。([Jaguar][2])
* S-Type II 按 1999–2002、2002–2004、2004–2007 三套不同三维拆分。([CarsGuide][3])

## 进度

输入 Ktype：100/100
最终映射行：107
DIMENSION_GROUP：31
PENDING：0
映射引用闭合：通过
ID 唯一性：通过
三维、来源及直接链接非空：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154496	154496	SUV	First generation		5	EU-JAC-E-JS4-2023-SUV-STANDARD-01	HIGH		READY
127454	127454	Hatchback	First generation		5	EU-JAC-IEV6E-2017-HATCHBACK-STANDARD-01	MEDIUM		READY
801529	801529	Van	First generation			EU-JAC-M3-2024-VAN-STANDARD-01	HIGH		READY
802526	802526	Pickup	First generation		4	EU-JAC-T8-PRO-2023-PICKUP-DOUBLE-CAB-01	HIGH		READY
802631	802631	Pickup	First generation		4	EU-JAC-T8-PRO-2023-PICKUP-DOUBLE-CAB-01	HIGH		READY
157040	157040	Pickup	First generation		4	EU-JAC-T8-PRO-2023-PICKUP-DOUBLE-CAB-01	HIGH		READY
157041	157041	Pickup	First generation		4	EU-JAC-T8-PRO-2023-PICKUP-DOUBLE-CAB-01	HIGH		READY
163290	163290	SUV	First generation		5	EU-JAECOO-5-2025-SUV-STANDARD-01	HIGH		READY
162196	162196	SUV	First generation		5	EU-JAECOO-5-2025-SUV-STANDARD-01	HIGH		READY
162197	162197	SUV	First generation		5	EU-JAECOO-5-2025-SUV-STANDARD-01	HIGH		READY
162364	162364	SUV	First generation		5	EU-JAECOO-5-2025-SUV-STANDARD-01	HIGH		READY
164734	164734	SUV	First generation		5	EU-JAECOO-8-2026-SUV-STANDARD-01	HIGH		READY
801213	801213	SUV	First generation		5	EU-JAECOO-J7-2024-SUV-STANDARD-01	HIGH		READY
801214	801214	SUV	First generation		5	EU-JAECOO-J7-2024-SUV-STANDARD-01	HIGH		READY
801266	801266	SUV	First generation		5	EU-JAECOO-J7-2024-SUV-STANDARD-01	HIGH		READY
803323	803323	SUV	First generation		5	EU-JAECOO-J7-2024-SUV-STANDARD-01	HIGH		READY
803322	803322	SUV	First generation		5	EU-JAECOO-J7-2024-SUV-STANDARD-01	HIGH		READY
142718	142718	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
158498	158498	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142723	142723	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127974	127974	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127975	127975	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127976	127976	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142715	142715	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142716	142716	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127977	127977	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142717	142717	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127978	127978	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
153717	153717	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
127973	127973	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142719	142719	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
153259	153259	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142720	142720	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142721	142721	SUV	First generation	X540	5	EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	HIGH		READY
142704	142704	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
142705	142705	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
142711	142711	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
126021	126021	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
117715	117715	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
126020	126020	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
117716	117716	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
126022	126022	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
127990	127990	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
801121	801121	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
142708	142708	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
142709	142709	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	HIGH		READY
117712	117712	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
117713	117713	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
117714	117714	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	HIGH		READY
142710	142710	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-SVR-01	HIGH		READY
156548	156548	SUV	First generation	X761	5	EU-JAGUAR-F-PACE-X761-SUV-SVR-01	HIGH		READY
126887	126887	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
126888	126888	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
57131	57131	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
100686	100686	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
125815	125815	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
125817	125817	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
57133	57133	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
100687	100687	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
109349	109349	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
109350	109350	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
100688	100688	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
109352	109352	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
109351	109351	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH		READY
109353	109353	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
57134	57134	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
118546_svr	118546	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-SVR-01	HIGH	SVR exterior	READY
118546_p575r	118546	Coupe	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	HIGH	P575 R exterior	READY
117709_svr	117709	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	HIGH	SVR exterior	READY
117709_p575r	117709	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-P575R-01	HIGH	P575 R exterior	READY
125818	125818	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
125819	125819	Convertible	First generation	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	HIGH		READY
142696	142696	SUV	First generation	X590	5	EU-JAGUAR-I-PACE-X590-SUV-STANDARD-01	HIGH		READY
59960	59960	Sedan	Mark I		4	EU-JAGUAR-MK1-1955-SEDAN-STANDARD-01	HIGH		READY
58389	58389	Sedan	Mark II		4	EU-JAGUAR-MK2-1967-SEDAN-240-340-01	HIGH		READY
58390	58390	Sedan	Mark II		4	EU-JAGUAR-MK2-1967-SEDAN-240-340-01	HIGH		READY
58394	58394	Sedan	Mark II		4	EU-JAGUAR-MK2-1959-SEDAN-3-8-01	HIGH		READY
58410	58410	Sedan	Mark VII		4	EU-JAGUAR-MK7-1950-SEDAN-STANDARD-01	HIGH		READY
58411	58411	Sedan	Mark VII		4	EU-JAGUAR-MK7-1950-SEDAN-STANDARD-01	HIGH		READY
100929	100929	Sedan	Mark VIII		4	EU-JAGUAR-MK8-1956-SEDAN-STANDARD-01	HIGH		READY
100930	100930	Sedan	Mark VIII		4	EU-JAGUAR-MK8-1956-SEDAN-STANDARD-01	HIGH		READY
58419	58419	Sedan	Mark X/420G		4	EU-JAGUAR-MK10-420G-1961-SEDAN-STANDARD-01	HIGH		READY
58392	58392	Sedan	Mark X/420G		4	EU-JAGUAR-MK10-420G-1961-SEDAN-STANDARD-01	HIGH		READY
58425	58425	Sedan	1963 generation		4	EU-JAGUAR-S-TYPE-1963-SEDAN-STANDARD-01	HIGH		READY
58433	58433	Sedan	1963 generation		4	EU-JAGUAR-S-TYPE-1963-SEDAN-STANDARD-01	HIGH		READY
16696_phase2	16696	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE2-01	MEDIUM	2002-2004 exterior	READY
16696_phase3	16696	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	MEDIUM	2004-2007 exterior	READY
18021	18021	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	HIGH		READY
10279_phase1	10279	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE1-01	MEDIUM	1999-2002 exterior	READY
10279_phase2	10279	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE2-01	MEDIUM	2002-2004 exterior	READY
10279_phase3	10279	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	MEDIUM	2004-2007 exterior	READY
10280	10280	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE1-01	HIGH		READY
16697_phase2	16697	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE2-01	MEDIUM	2002-2004 exterior	READY
16697_phase3	16697	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	MEDIUM	2004-2007 exterior	READY
16698_phase2	16698	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE2-01	MEDIUM	2002-2004 exterior	READY
16698_phase3	16698	Sedan	Second generation	X200	4	EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	MEDIUM	2004-2007 exterior	READY
108185	108185	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
108186	108186	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
126746	126746	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
126747	126747	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	HIGH		READY
127991	127991	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	HIGH		READY
108183	108183	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
108184	108184	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	HIGH		READY
117794	117794	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	HIGH		READY
126745	126745	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	HIGH		READY
142688	142688	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-FACELIFT-RWD-01	HIGH		READY
142689	142689	Sedan	First generation	X760	4	EU-JAGUAR-XE-X760-SEDAN-FACELIFT-AWD-01	HIGH		READY
```

[下载 left18448_7501-7600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_7501-7600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAC-E-JS4-2023-SUV-STANDARD-01	4410	1800	1660	Auto-Data	https://www.auto-data.net/en/jac-js4-e-js4-55-kwh-150hp-50462
EU-JAC-IEV6E-2017-HATCHBACK-STANDARD-01	3630	1670	1475	CarNewsChina vehicle database	https://data.carnewschina.com/database/jac/jac-iev6e/2017/params
EU-JAC-M3-2024-VAN-STANDARD-01	5115	1765	1900	JAC Switzerland	https://jac-schweiz.ch/en/m3ev/
EU-JAC-T8-PRO-2023-PICKUP-DOUBLE-CAB-01	5325	1880	1830	JAC Motors	https://jacen.jac.com.cn/models/T8PRO/
EU-JAECOO-5-2025-SUV-STANDARD-01	4380	1860	1650	AutomobileDimensions	https://www.automobiledimension.com/model/jaecoo/5
EU-JAECOO-8-2026-SUV-STANDARD-01	4820	1930	1710	JAECOO Indonesia J8 SHS-P specification	https://jaecoo.id/uploads/Flyer_J8_SHS_P_ARDIS_compressed_2ba20e5472.pdf
EU-JAECOO-J7-2024-SUV-STANDARD-01	4500	1865	1680	Omoda Jaecoo Australia J7 specification sheet	https://www.omodajaecoo.com.au/sites/default/files/2025-09/153_24_Jaecoo_J7_Spec_Sheet_AU_ICE_v100.pdf
EU-JAGUAR-E-PACE-X540-SUV-STANDARD-01	4395	1900	1648	AutomobileDimensions	https://www.automobiledimension.com/model/jaguar/e-pace
EU-JAGUAR-F-PACE-X761-SUV-PREFACELIFT-01	4731	1936	1652	Jaguar F-PACE official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-FPAC17-PRT0520_F_PACE_17MY_MB_GEE%20UPDATE_V3.pdf
EU-JAGUAR-F-PACE-X761-SUV-FACELIFT-01	4747	1936	1664	AutomobileDimensions	https://www.automobiledimension.com/model/jaguar/f-pace
EU-JAGUAR-F-PACE-X761-SUV-SVR-01	4762	1936	1670	Jaguar F-PACE official technical specification	https://www.jaguar.com/content/dam/jdx/pdfs/uk/wltp/Jaguar-F-PACE-TD-Insert-1X7612550000GBEN01P.pdf
EU-JAGUAR-F-TYPE-X152-COUPE-STANDARD-01	4470	1923	1311	Jaguar F-TYPE 17MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-STANDARD-01	4470	1923	1308	Jaguar F-TYPE 17MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf
EU-JAGUAR-F-TYPE-X152-COUPE-SVR-01	4475	1923	1311	Jaguar F-TYPE 17MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	4475	1923	1308	Jaguar F-TYPE 17MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-P575R-01	4470	1923	1307	Jaguar F-TYPE official technical specification	https://www.jaguar.com/content/dam/jdx/pdfs/uk/wltp/Jaguar-F-TYPE-TD-Insert-1X1522400000GBEN01P.pdf
EU-JAGUAR-I-PACE-X590-SUV-STANDARD-01	4682	1895	1565	CarExpert	https://www.carexpert.com.au/jaguar/i-pace/2021/features-and-specs
EU-JAGUAR-MK1-1955-SEDAN-STANDARD-01	4591	1695	1461	Jaguar Enthusiasts' Club	https://jec.org.uk/models/compact-jaguar-saloons/mk-1/
EU-JAGUAR-MK2-1967-SEDAN-240-340-01	4591	1695	1467	Jaguar Enthusiasts' Club	https://jec.org.uk/models/compact-jaguar-saloons/240-saloon/
EU-JAGUAR-MK2-1959-SEDAN-3-8-01	4591	1689	1467	Jaguar Enthusiasts' Club	https://jec.org.uk/models/compact-jaguar-saloons/mk-2/
EU-JAGUAR-MK7-1950-SEDAN-STANDARD-01	4991	1854	1600	Jaguar Enthusiasts' Club	https://jec.org.uk/models/mark-vii-to-ix-saloons/mark-vii/
EU-JAGUAR-MK8-1956-SEDAN-STANDARD-01	4991	1854	1600	Jaguar Enthusiasts' Club	https://jec.org.uk/models/mark-vii-to-ix-saloons/mark-viii/
EU-JAGUAR-MK10-420G-1961-SEDAN-STANDARD-01	5131	1930	1391	Jaguar Enthusiasts' Club	https://jec.org.uk/models/mark-10-420g-ds420/420g/
EU-JAGUAR-S-TYPE-1963-SEDAN-STANDARD-01	4750	1683	1416	Jaguar Enthusiasts' Club	https://jec.org.uk/models/compact-jaguar-saloons/s-type/
EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE1-01	4861	1819	1444	CarsGuide	https://www.carsguide.com.au/jaguar/s-type/car-dimensions/1999
EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE2-01	4877	1818	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/1287965/jaguar_s-type_2_5_v6_automatic.html
EU-JAGUAR-S-TYPE-X200-SEDAN-PHASE3-01	4905	1818	1447	Jaguar USA S-TYPE 2006 brochure	https://www.auto-brochures.com/makes/Jaguar/S-Type/Jaguar_US%20S-Type_2006.pdf
EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-RWD-01	4672	1850	1416	Jaguar XE official brochure	https://i.i-sgcm.com/new_cars/cars/11783/brochures/brochure_20161128111517.pdf
EU-JAGUAR-XE-X760-SEDAN-PREFACELIFT-AWD-01	4672	1850	1425	Jaguar XE official brochure	https://i.i-sgcm.com/new_cars/cars/11783/brochures/brochure_20161128111517.pdf
EU-JAGUAR-XE-X760-SEDAN-FACELIFT-RWD-01	4678	1850	1416	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2976800/jaguar_xe_d200_mhev.html
EU-JAGUAR-XE-X760-SEDAN-FACELIFT-AWD-01	4678	1850	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2976815/jaguar_xe_d200_mhev_awd.html
```

[下载 left18448_7501-7600_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_7501-7600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobiledimension.com/model/jaguar/f-pace "https://www.automobiledimension.com/model/jaguar/f-pace"
[2]: https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf "https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL_FTYP17_PRT0022_F-TYPE_17MY_MB_GEE_FINAL.pdf"
[3]: https://www.carsguide.com.au/jaguar/s-type/car-dimensions/1999 "https://www.carsguide.com.au/jaguar/s-type/car-dimensions/1999"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5149 行）
- 累计尺寸组：dimension_groups_final.tsv（1373 行）

