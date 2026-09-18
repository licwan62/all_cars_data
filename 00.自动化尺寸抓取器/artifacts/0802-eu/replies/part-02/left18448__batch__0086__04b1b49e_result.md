# 任务：left18448 第 8501-8600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0086__04b1b49e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8501-8600 行

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
left18448 第 8501-8600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8501-8600_ktype_dimension_mapping_final.tsv
- left18448_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	4956	2000	1846
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	4970	2000	1846

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Land Rover	Discovery v	D300 Mhev 4X4	SUV	Allrad	Diesel/Elektro	Dec 2020	-	142742
Land Rover	Discovery v	D350 Mhev 4X4	SUV	Allrad	Diesel/Elektro	May 2024	-	158738
Land Rover	Discovery v	P360 Mhev 4X4	SUV	Allrad	Benzin/Elektro	Dec 2020	-	142743
Land Rover	Discovery v van	2.0 SD4 4X4	Kasten/SUV	Allrad	Diesel	Sep 2016	-	142752
Land Rover	Discovery v van	2.0 SI4 4X4	Kasten/SUV	Allrad	Benzin	Sep 2017	-	142757
Land Rover	Discovery v van	2.0 TD4 4X4	Kasten/SUV	Allrad	Diesel	Sep 2016	Dec 2018	142747
Land Rover	Discovery v van	3.0 D350 Mhev 4X4	Kasten/SUV	Allrad	Diesel/Elektro	May 2024	-	802670
Land Rover	Discovery v van	3.0 Scv6 4X4	Kasten/SUV	Allrad	Benzin	Sep 2016	-	142758
Land Rover	Discovery v van	3.0 Sdv6 4X4	Kasten/SUV	Allrad	Diesel	Sep 2018	-	142754
Land Rover	Discovery v van	3.0 TD6 4X4	Kasten/SUV	Allrad	Diesel	Sep 2016	-	142753
Land Rover	Freelander 2	2.0 SI4 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 2011	Oct 2014	15945
Land Rover	Freelander i	1.8 16V 4X4	Geländewagen geschlossen	Allrad	Benzin	Apr 1998	Oct 2006	15591
Land Rover	Freelander i	2.0 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	Nov 2000	Oct 2006	15429
Land Rover	Freelander i	2.0 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	Mar 2001	Oct 2006	17313
Land Rover	Freelander i	2.5 V6 4X4	Geländewagen geschlossen	Allrad	Benzin	Nov 2000	Oct 2006	15428
Land Rover	Freelander i soft top	1.8 4X4	Geländewagen offen	Allrad	Benzin	Oct 2000	Oct 2006	55967
Land Rover	Freelander i soft top	1.8 I 16V 4X4	Geländewagen offen	Allrad	Benzin	Feb 1998	Oct 2006	10539
Land Rover	Freelander i soft top	2.0 DI 4X4	Geländewagen offen	Allrad	Diesel	Feb 1998	Oct 2006	10541
Land Rover	Freelander i soft top	2.0 TD4 4X4	Geländewagen offen	Allrad	Diesel	Oct 2000	Oct 2006	55968
Land Rover	Range rover evoque	1.5 P270e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158659
Land Rover	Range rover evoque	1.5 P300e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	Feb 2020	-	158630
Land Rover	Range rover evoque	2.0 4X4	SUV	Allrad	Benzin	Sep 2011	Dec 2019	100976
Land Rover	Range rover evoque	2.0 4X4	SUV	Allrad	Benzin	Aug 2017	Dec 2019	115023
Land Rover	Range rover evoque	2.0 4X4	Cabriolet	Allrad	Benzin	Nov 2015	Dec 2019	117555
Land Rover	Range rover evoque	2.0 4X4	SUV	Allrad	Benzin	Aug 2017	Dec 2019	128221
Land Rover	Range rover evoque	2.0 4X4	Cabriolet	Allrad	Benzin	Aug 2017	Dec 2019	128231
Land Rover	Range rover evoque	2.0 D	SUV	Frontantrieb	Diesel	Jun 2015	Dec 2019	115147
Land Rover	Range rover evoque	2.0 D 4X4	SUV	Allrad	Diesel	Jun 2015	Dec 2019	115148
Land Rover	Range rover evoque	2.0 D 4X4	SUV	Allrad	Diesel	May 2015	Dec 2019	115150
Land Rover	Range rover evoque	2.0 D 4X4	Cabriolet	Allrad	Diesel	Nov 2015	Dec 2019	117553
Land Rover	Range rover evoque	2.0 D 4X4	Cabriolet	Allrad	Diesel	Nov 2015	Dec 2019	117554
Land Rover	Range rover evoque	2.0 D 4X4	SUV	Allrad	Diesel	Aug 2017	Dec 2019	127386
Land Rover	Range rover evoque	2.0 D 4X4	Cabriolet	Allrad	Diesel	Aug 2017	Dec 2019	128145
Land Rover	Range rover evoque van	SD4 4X4	Kasten/SUV	Allrad	Diesel	May 2015	Dec 2019	142926
Land Rover	Range rover evoque van	SI4 4X4	Kasten/SUV	Allrad	Benzin	Sep 2013	Dec 2019	142922
Land Rover	Range rover evoque van	TD4	Kasten/SUV	Frontantrieb	Diesel	May 2015	Dec 2019	142924
Land Rover	Range rover evoque van	TD4 4X4	Kasten/SUV	Allrad	Diesel	May 2015	Dec 2019	142925
Land Rover	Range rover i	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	Jul 1970	Aug 1981	14264
Land Rover	Range rover i	3.9 4X4	Geländewagen geschlossen	Allrad	Benzin	Oct 1989	Dec 1994	45175
Land Rover	Range rover i	3.9 4X4	Geländewagen geschlossen	Allrad	Benzin	Nov 1988	Dec 1992	106051
Land Rover	Range rover ii	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	Jan 1995	Mar 2002	11627
Land Rover	Range rover ii	4.6 4X4	Geländewagen geschlossen	Allrad	Benzin	Jun 1998	Mar 2002	11628
Land Rover	Range rover iii	3.0 D 4X4	Geländewagen geschlossen	Allrad	Diesel	Mar 2002	Aug 2012	16520
Land Rover	Range rover iii	4.2 4X4	Geländewagen geschlossen	Allrad	Benzin	May 2005	Aug 2012	18572
Land Rover	Range rover iii	4.4 4X4	Geländewagen geschlossen	Allrad	Benzin	Aug 2004	Aug 2012	14235
Land Rover	Range rover iii	4.4 4X4	Geländewagen geschlossen	Allrad	Benzin	Mar 2002	Aug 2005	16519
Land Rover	Range rover iii	4.4 4X4	Geländewagen geschlossen	Allrad	Benzin	May 2005	Aug 2012	18573
Land Rover	Range rover iv	3.0 Scv6 4X4	SUV	Allrad	Benzin	Oct 2013	Sep 2021	100015
Land Rover	Range rover iv	3.0 Scv6 4X4	SUV	Allrad	Benzin	Jun 2015	Sep 2021	115843
Land Rover	Range rover iv	3.0 Sdv6 4X4	SUV	Allrad	Diesel	Aug 2012	Jan 2016	56762
Land Rover	Range rover iv	3.0 Sdv6 Hybrid 4X4	SUV	Allrad	Diesel/Elektro	Oct 2013	Sep 2021	100017
Land Rover	Range rover iv	3.0 Sdv6 Hybrid 4X4	SUV	Allrad	Diesel/Elektro	Jun 2015	Sep 2021	116829
Land Rover	Range rover iv	3.0 Tdv6 4X4	SUV	Allrad	Diesel	Aug 2012	Sep 2021	56775
Land Rover	Range rover iv	3.0 Tdv6 4X4	SUV	Allrad	Diesel	Oct 2013	Jan 2016	100016
Land Rover	Range rover iv	4.4 Sdv8 4X4	SUV	Allrad	Diesel	Aug 2012	Sep 2021	56776
Land Rover	Range rover iv	4.4 Sdv8 4X4	SUV	Allrad	Diesel	Aug 2013	Sep 2021	105800
Land Rover	Range rover iv	5.0 Scv8 4X4	SUV	Allrad	Benzin	Aug 2012	Sep 2021	57067
Land Rover	Range rover iv	5.0 Scv8 4X4	SUV	Allrad	Benzin	Jun 2015	Sep 2021	115836
Land Rover	Range rover iv	5.0 V8 4X4	SUV	Allrad	Benzin	Dec 2013	Jan 2016	100503
Land Rover	Range rover sport i	2.7 D 4X4	SUV	Allrad	Diesel	Feb 2005	Mar 2013	18804
Land Rover	Range rover sport i	3.0 D 4X4	SUV	Allrad	Diesel	Jun 2011	Mar 2013	12009
Land Rover	Range rover sport i	3.0 D 4X4	SUV	Allrad	Diesel	Aug 2012	Mar 2013	56766
Land Rover	Range rover sport i	4.2 4X4	SUV	Allrad	Benzin	Feb 2005	Mar 2013	18802
Land Rover	Range rover sport i	4.4 4X4	SUV	Allrad	Benzin	Feb 2005	Mar 2013	18803
Land Rover	Range rover sport ii	3.0 Scv6 4X4	SUV	Allrad	Benzin	Apr 2013	Dec 2019	58991
Land Rover	Range rover sport ii	3.0 Scv6 4X4	SUV	Allrad	Benzin	Jun 2015	Dec 2018	115828
Land Rover	Range rover sport ii	3.0 Sdv6 4X4	SUV	Allrad	Diesel	Apr 2013	Dec 2016	58992
Land Rover	Range rover sport ii	3.0 Sdv6 4X4	SUV	Allrad	Diesel	Apr 2013	Mar 2022	58995
Land Rover	Range rover sport ii	3.0 Sdv6 4X4	SUV	Allrad	Diesel	Sep 2014	Mar 2022	108825
Land Rover	Range rover sport ii	3.0 Sdv6 Hybrid 4X4	SUV	Allrad	Diesel/Elektro	Oct 2013	Mar 2022	100338
Land Rover	Range rover sport ii	3.0 Sdv6 Hybrid 4X4	SUV	Allrad	Diesel/Elektro	Jun 2015	Dec 2017	116835
Land Rover	Range rover sport ii	3.0 Tdv6 4X4	SUV	Allrad	Diesel	Apr 2013	Mar 2022	58993
Land Rover	Range rover sport ii	3.0 Tdv6 4X4	SUV	Allrad	Diesel	Apr 2013	Dec 2018	58994
Land Rover	Range rover sport ii	4.4 Sdv8 4X4	SUV	Allrad	Diesel	Oct 2013	Mar 2022	100337
Land Rover	Range rover sport ii	5.0 Scv8 4X4	SUV	Allrad	Benzin	Apr 2013	Dec 2018	58987
Land Rover	Range rover sport ii	5.0 Scv8 4X4	SUV	Allrad	Benzin	Jan 2014	Dec 2018	108805
Land Rover	Range rover sport iii	1.5 P 270e Phev 4X4	SUV	Allrad	Benzin/Elektro	May 2024	-	158739
Land Rover	Range rover sport iii	3.0 D250 Mhev AWD	SUV	Allrad	Diesel/Elektro	Apr 2022	-	147571
Land Rover	Range rover sport iii	3.0 D300 Mhev AWD	SUV	Allrad	Diesel/Elektro	Apr 2022	-	147572
Land Rover	Range rover sport iii	3.0 D350 Mhev AWD	SUV	Allrad	Diesel/Elektro	Apr 2022	-	148074
Land Rover	Range rover sport iii	P400 Mhev AWD	SUV	Allrad	Benzin/Elektro	Apr 2022	-	147574
Land Rover	Range rover sport iii	P440e Phev AWD	SUV	Allrad	Benzin/Elektro	Apr 2022	-	147576
Land Rover	Range rover sport iii	P460e Phev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154566
Land Rover	Range rover sport iii	P510e Phev AWD	SUV	Allrad	Benzin/Elektro	Apr 2022	-	147578
Land Rover	Range rover sport iii	P530 AWD	SUV	Allrad	Benzin	Apr 2022	-	147579
Land Rover	Range rover sport iii	P530 Mhev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	157552
Land Rover	Range rover sport iii	P550e Phev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154567
Land Rover	Range rover sport iii	P635 Mhev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154838
Land Rover	Range rover v	D250 Mhev AWD	SUV	Allrad	Diesel/Elektro	Oct 2021	-	145841
Land Rover	Range rover v	D300 Mhev AWD	SUV	Allrad	Diesel/Elektro	Oct 2021	-	145839
Land Rover	Range rover v	D350 Mhev AWD	SUV	Allrad	Diesel/Elektro	Oct 2021	-	145840
Land Rover	Range rover v	P400 Mhev AWD	SUV	Allrad	Benzin/Elektro	Oct 2021	-	145837
Land Rover	Range rover v	P440e Phev AWD	SUV	Allrad	Benzin/Elektro	Feb 2022	-	147221
Land Rover	Range rover v	P460e Phev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154564
Land Rover	Range rover v	P510e Phev AWD	SUV	Allrad	Benzin/Elektro	Feb 2022	-	147223
Land Rover	Range rover v	P530 AWD	SUV	Allrad	Benzin	Oct 2021	-	145838
Land Rover	Range rover v	P530 Mhev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	155606
Land Rover	Range rover v	P550e Phev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154565
Land Rover	Range rover v	P615 Mhev AWD	SUV	Allrad	Benzin/Elektro	May 2023	-	154755
Land Rover	Range rover velar	2.0 D165 Mhev 4X4	SUV	Allrad	Diesel/Elektro	Feb 2021	-	148139


--- Round 1 / 首次发送 ---
## 更新点

已完成本批 100 个 Ktype 的物理外廓归并与尺寸组闭合：

* 复用 Discovery V L462 已有的改款前、改款后尺寸组。
* 将 `158630/158659` 正确归入 Range Rover Evoque II L551，未误并入 Evoque I L538。
* 对 Freelander II、Evoque II、Range Rover Sport III、Range Rover V、Velar 等车型采用不含后视镜的车身宽度口径。([汽车目录][1])
* Range Rover III L322 未因发动机或资料取整差异制造无证据分支。
* Range Rover IV、Range Rover V 输入未带 LWB 标识，统一映射至标准轴距外廓。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：20
* 唯一 Ktype：100
* 唯一映射 id：100
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射表

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142742	142742	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	HIGH		READY
158738	158738	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	HIGH		READY
142743	142743	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	HIGH		READY
142752	142752	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
142757	142757	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
142747	142747	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
802670	802670	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
142758	142758	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
142754	142754	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
142753	142753	Van	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Discovery V exterior shell.	READY
15945	15945	SUV	Freelander II	L359	5	EU-LAND-ROVER-FREELANDER-II-L359-SUV-STANDARD-01	HIGH		READY
15591	15591	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-STANDARD-01	HIGH		READY
15429	15429	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-STANDARD-01	HIGH		READY
17313	17313	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-STANDARD-01	HIGH		READY
15428	15428	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-STANDARD-01	HIGH		READY
55967	55967	Convertible	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-CONVERTIBLE-STANDARD-01	HIGH		READY
10539	10539	Convertible	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-CONVERTIBLE-STANDARD-01	HIGH		READY
10541	10541	Convertible	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-CONVERTIBLE-STANDARD-01	HIGH		READY
55968	55968	Convertible	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-CONVERTIBLE-STANDARD-01	HIGH		READY
158659	158659	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-STANDARD-01	HIGH		READY
158630	158630	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-STANDARD-01	HIGH		READY
100976	100976	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-PREFL-01	HIGH		READY
115023	115023	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
117555	117555	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	HIGH		READY
128221	128221	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
128231	128231	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	HIGH		READY
115147	115147	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
115148	115148	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
115150	115150	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
117553	117553	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	HIGH		READY
117554	117554	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	HIGH		READY
127386	127386	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	HIGH		READY
128145	128145	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	HIGH		READY
142926	142926	Van	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	MEDIUM	Commercial variant shares the phase-matched Evoque I five-door exterior shell.	READY
142922	142922	Van	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-PREFL-01	MEDIUM	Commercial variant shares the phase-matched Evoque I five-door exterior shell.	READY
142924	142924	Van	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	MEDIUM	Commercial variant shares the phase-matched Evoque I five-door exterior shell.	READY
142925	142925	Van	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	MEDIUM	Commercial variant shares the phase-matched Evoque I five-door exterior shell.	READY
14264	14264	SUV	Range Rover I		3	EU-LAND-ROVER-RANGE-ROVER-I-CLASSIC-SUV-3DR-EARLY-01	HIGH		READY
45175	45175	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-CLASSIC-SUV-5DR-LATE-01	HIGH		READY
106051	106051	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-CLASSIC-SUV-5DR-LATE-01	HIGH		READY
11627	11627	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-STANDARD-01	HIGH		READY
11628	11628	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-STANDARD-01	HIGH		READY
16520	16520	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	HIGH		READY
18572	18572	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	HIGH		READY
14235	14235	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	HIGH		READY
16519	16519	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	HIGH		READY
18573	18573	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	HIGH		READY
100015	100015	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
115843	115843	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
56762	56762	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
100017	100017	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
116829	116829	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
56775	56775	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
100016	100016	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
56776	56776	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
105800	105800	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
57067	57067	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
115836	115836	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
100503	100503	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
18804	18804	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	HIGH		READY
12009	12009	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	HIGH		READY
56766	56766	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	HIGH		READY
18802	18802	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	HIGH		READY
18803	18803	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	HIGH		READY
58991	58991	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
115828	115828	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
58992	58992	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
58995	58995	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
108825	108825	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
100338	100338	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
116835	116835	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
58993	58993	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
58994	58994	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
100337	100337	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
58987	58987	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
108805	108805	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	Date span alone was not used to infer a facelift split.	READY
158739	158739	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147571	147571	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147572	147572	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
148074	148074	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147574	147574	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147576	147576	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
154566	154566	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147578	147578	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
147579	147579	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
157552	157552	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
154567	154567	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
154838	154838	SUV	Range Rover Sport III	L461	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	HIGH		READY
145841	145841	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
145839	145839	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
145840	145840	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
145837	145837	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
147221	147221	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
154564	154564	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
147223	147223	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
145838	145838	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
155606	155606	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
154565	154565	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
154755	154755	SUV	Range Rover V	L460	5	EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	HIGH	No LWB marker; mapped to the standard-wheelbase exterior.	READY
148139	148139	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-I-L560-SUV-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射表](sandbox:/mnt/data/left18448_8501-8600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP 表

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-FACELIFT-01	4956	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2976110/land-rover_discovery_2_0_p300_awd.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-PREFL-01	4970	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html
EU-LAND-ROVER-FREELANDER-II-L359-SUV-STANDARD-01	4500	1910	1740	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1406750/land_rover_freelander_2_sd4_hse.html
EU-LAND-ROVER-FREELANDER-I-LN-SUV-STANDARD-01	4445	1809	1760	Auto-Data.net	https://www.auto-data.net/en/land-rover-freelander-i-ln-generation-1207
EU-LAND-ROVER-FREELANDER-I-LN-CONVERTIBLE-STANDARD-01	4433	1809	1760	Auto-Data.net	https://www.auto-data.net/en/land-rover-freelander-i-soft-top-generation-1208
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-PREFL-01	4365	1900	1635	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1615805/range_rover_evoque_td4_pure.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-FACELIFT-01	4370	1900	1635	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2327045/range_rover_evoque_5-door_si4_awd.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-STANDARD-01	4370	1900	1609	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2564900/range_rover_evoque_convertible_si4_240_awd.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-STANDARD-01	4371	1904	1649	Automobile-Catalog	https://www.automobile-catalog.com/car/2022/2976515/range_rover_evoque_p300e_phev_awd.html
EU-LAND-ROVER-RANGE-ROVER-I-CLASSIC-SUV-3DR-EARLY-01	4470	1778	1778	Automobile-Catalog	https://www.automobile-catalog.com/car/1970/36350/range_rover.html
EU-LAND-ROVER-RANGE-ROVER-I-CLASSIC-SUV-5DR-LATE-01	4449	1818	1790	Auto-Data.net	https://www.auto-data.net/en/land-rover-range-rover-i-3.9-v8-188hp-5215
EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-STANDARD-01	4713	1853	1817	Auto-Data.net	https://www.auto-data.net/en/land-rover-range-rover-ii-4.6-218hp-5207
EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-STANDARD-01	4950	1956	1863	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1404035/range_rover_v8_se.html
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	4999	1983	1835	Auto-Data.net	https://www.auto-data.net/en/land-rover-range-rover-iv-5.0-v8-510hp-awd-automatic-23034
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	4788	1928	1784	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1404875/range_rover_sport_tdv6_hse.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1405085/range_rover_sport_3_0_tdv6_se.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780	Auto-Data.net	https://www.auto-data.net/en/land-rover-range-rover-sport-ii-4.4-v8-339hp-awd-automatic-22946
EU-LAND-ROVER-RANGE-ROVER-SPORT-III-L461-SUV-STANDARD-01	4946	1990	1820	Automobile Dimension	https://www.automobiledimension.com/model/land-rover/range-rover-sport
EU-LAND-ROVER-RANGE-ROVER-V-L460-SUV-SWB-01	5052	1990	1870	Automobile Dimension	https://www.automobiledimension.com/model/land-rover/range-rover
EU-LAND-ROVER-RANGE-ROVER-VELAR-I-L560-SUV-STANDARD-01	4797	1930	1683	CarExpert	https://www.carexpert.com.au/land-rover/range-rover-velar
```

[下载完整 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_8501-8600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html "https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6159 行）
- 累计尺寸组：dimension_groups_final.tsv（1708 行）

