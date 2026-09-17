# 任务：left18448 第 16201-16300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0163__917565df


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16201-16300 行

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
left18448 第 16201-16300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16201-16300_ktype_dimension_mapping_final.tsv
- left18448_16201-16300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-TOYOTA-COROLLA-AE86-COUPE-STANDARD-01	4205	1625	1335
EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	4370	1770	1620
EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	4360	1770	1620
EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	4460	1825	1620
EU-TOYOTA-COROLLA-E100-HATCHBACK-COMPACT-01	4095	1685	1380
EU-TOYOTA-COROLLA-E100-HATCHBACK-LIFTBACK-01	4295	1685	1375
EU-TOYOTA-COROLLA-E100-SEDAN-STANDARD-01	4270	1685	1380
EU-TOYOTA-COROLLA-E100-WAGON-STANDARD-01	4260	1685	1460
EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	4270	1690	1385
EU-TOYOTA-COROLLA-E110-SEDAN-STANDARD-01	4295	1690	1385
EU-TOYOTA-COROLLA-E110-WAGON-STANDARD-01	4320	1690	1445
EU-TOYOTA-COROLLA-E120-E130-HATCHBACK-STANDARD-01	4180	1710	1475
EU-TOYOTA-COROLLA-E120-E130-SEDAN-STANDARD-01	4375	1710	1470
EU-TOYOTA-COROLLA-E120-E130-WAGON-STANDARD-01	4410	1710	1520
EU-TOYOTA-COROLLA-E140-E150-SEDAN-STANDARD-01	4540	1760	1470
EU-TOYOTA-COROLLA-E170-SEDAN-STANDARD-01	4620	1775	1465
EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	4370	1790	1435
EU-TOYOTA-COROLLA-E210-SEDAN-STANDARD-01	4630	1780	1435
EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	4650	1790	1435
EU-TOYOTA-COROLLA-E70-HATCHBACK-STANDARD-01	4050	1610	1385
EU-TOYOTA-COROLLA-E70-WAGON-HIGHROOF-01	4215	1610	1450
EU-TOYOTA-COROLLA-E80-HATCHBACK-STANDARD-01	3970	1635	1380
EU-TOYOTA-COROLLA-E80-SEDAN-STANDARD-01	4140	1610	1385
EU-TOYOTA-COROLLA-E90-SEDAN-STANDARD-01	4195	1655	1365
EU-TOYOTA-COROLLA-E90-WAGON-STANDARD-01	4205	1655	1425
EU-TOYOTA-COROLLA-VERSO-E120-MPV-STANDARD-01	4240	1710	1610

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Toyota	Corolla	1.9 D	Schrägheck	Frontantrieb	Diesel	Feb 2000	Jan 2002	15718
Toyota	Corolla	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	Sep 2000	Jan 2002	15565
Toyota	Corolla	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	Sep 2000	Jan 2002	15566
Toyota	Corolla	2.0 D-4d	Kombi	Frontantrieb	Diesel	Sep 2000	Oct 2001	15567
Toyota	Corolla	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	Sep 2000	Nov 2001	16033
Toyota	Corolla	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	May 2003	Feb 2007	17439
Toyota	Corolla	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	Jan 2002	Dec 2006	17856
Toyota	Corolla	2.0 D-4d	Großraumlimousine	Frontantrieb	Diesel	Apr 2004	Mar 2009	18041
Toyota	Corolla	2.0 D-4d	Kombi	Frontantrieb	Diesel	Apr 2004	Feb 2007	18220
Toyota	Corolla	2.0 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	May 2021	-	144564
Toyota	Corolla	2.0 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	May 2021	-	144565
Toyota	Corolla	2.0 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2023	-	151825
Toyota	Corolla	2.0 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Jan 2023	-	151826
Toyota	Corolla	2.0 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Feb 2025	-	801665
Toyota	Corolla	2.0 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2025	-	801666
Toyota	Corolla	2.0 Vvti Hybrid	SUV	Frontantrieb	Benzin/Elektro	Aug 2022	-	149658
Toyota	Corolla	2.0 Vvti Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jun 2025	-	802015
Toyota	Corolla	2.0 Vvti Hybrid 4X4	SUV	Allrad	Benzin/Elektro	Jun 2025	-	802818
Toyota	Corolla	2.0 Vvti Hybrid AWD	SUV	Allrad	Benzin/Elektro	Aug 2022	-	149659
Toyota	Corolla	2.2 D-4d	Großraumlimousine	Frontantrieb	Diesel	Oct 2005	Mar 2009	19068
Toyota	Corona	2	Kombi	Heckantrieb	Benzin	Sep 1975	May 1979	10741
Toyota	Cressida	2.2 D	Stufenheck	Heckantrieb	Diesel	Sep 1980	Apr 1985	5058
Toyota	Cressida	2.4 TD	Stufenheck	Heckantrieb	Diesel	Jan 1985	Oct 1988	59447
Toyota	Cressida station wagon	2	Kombi	Heckantrieb	Benzin	Dec 1977	Mar 1981	110599
Toyota	Dyna	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1977	Aug 1984	18850
Toyota	Dyna	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Sep 1984	Aug 1987	18851
Toyota	Dyna	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1984	Aug 1987	18852
Toyota	Dyna	2.4 D	Bus	Heckantrieb	Diesel	Aug 1977	Feb 1979	18854
Toyota	Dyna	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1985	May 1995	55605
Toyota	Dyna	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1987	Apr 1995	125328
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	-	10664
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Oct 2009	-	13887
Toyota	Dyna	3.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1984	Aug 1987	18853
Toyota	Dyna	3.4 D	Bus	Heckantrieb	Diesel	Aug 1977	Aug 1987	18855
Toyota	Dyna	4.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Oct 2006	-	11251
Toyota	Dyna	4.0 D4D 4WD	Pritsche/Fahrgestell	Allrad	Diesel	May 2011	-	13888
Toyota	Dyna 100	1.8	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1987	Apr 1995	59388
Toyota	Dyna 100	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 1995	Jul 2001	121636
Toyota	Dyna 150	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Aug 1985	Sep 1987	59460
Toyota	Dyna 150	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1985	Aug 1987	59458
Toyota	Fj cruiser	4.0 4WD	SUV	Allrad	Benzin	Jan 2006	Jan 2018	12252
Toyota	Fortuner	2.8 D 4X4	SUV	Allrad	Diesel	May 2015	-	116366
Toyota	Gr 86	2.4	Coupe	Heckantrieb	Benzin	Apr 2022	-	147244
Toyota	Gt	2	Coupe	Heckantrieb	Benzin	Mar 2012	-	15977
Toyota	Hiace / commuter v	2.5 D-4d	Bus	Heckantrieb	Diesel	Sep 2006	-	11805
Toyota	Hiace ii	1.6	Kasten	Heckantrieb	Benzin	Feb 1977	Mar 1983	10764
Toyota	Hiace ii	2	Kasten	Heckantrieb	Benzin	Feb 1977	Mar 1983	10742
Toyota	Hiace ii	2.2 D	Kasten	Heckantrieb	Diesel	Jan 1979	Mar 1983	10743
Toyota	Hiace iii	2	Kasten	Heckantrieb	Benzin	Dec 1982	Aug 1989	10765
Toyota	Hiace iv	2.4	Kasten	Heckantrieb	Benzin	Aug 1995	Nov 2003	10766
Toyota	Hiace iv	2.4	Kasten	Heckantrieb	Benzin	Aug 1995	Aug 2004	34712
Toyota	Hiace iv	2.7	Bus	Heckantrieb	Benzin	Apr 1998	Nov 2001	14326
Toyota	Hiace iv	2.7	Kasten	Heckantrieb	Benzin	Apr 1998	Jun 2005	14327
Toyota	Hiace iv	2.7	Bus	Heckantrieb	Benzin	Jul 1998	Dec 2006	16556
Toyota	Hiace iv	2.4 4WD	Kasten	Allrad	Benzin	Aug 1995	Apr 1998	14324
Toyota	Hiace iv	2.4 4WD	Bus	Allrad	Benzin	Aug 1995	Apr 1998	14325
Toyota	Hiace iv	2.4 D	Kasten	Heckantrieb	Diesel	Aug 1995	Aug 2001	10768
Toyota	Hiace iv	2.4 D	Bus	Heckantrieb	Diesel	Aug 1995	Aug 2001	14436
Toyota	Hiace iv	2.4 D 4WD	Bus	Allrad	Diesel	Aug 1987	Aug 1995	18553
Toyota	Hiace iv	2.4 D 4WD	Kasten	Allrad	Diesel	Aug 1989	Jul 1999	18554
Toyota	Hiace iv	2.4 TD	Kasten	Heckantrieb	Diesel	Aug 1995	Aug 2001	10779
Toyota	Hiace iv	2.4 TD 4WD	Kasten	Allrad	Diesel	Aug 1995	Aug 2001	14328
Toyota	Hiace iv	2.4 TD 4WD	Bus	Allrad	Diesel	Aug 1995	Aug 2001	14329
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	Aug 2001	Aug 2006	16546
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	Aug 2001	Aug 2006	16547
Toyota	Hiace iv	2.5 D-4d	Kasten	Heckantrieb	Diesel	Aug 2001	Aug 2006	16557
Toyota	Hiace iv	2.5 D-4d	Kasten	Heckantrieb	Diesel	Aug 2001	Aug 2006	16558
Toyota	Hiace iv	2.5 D-4d 4WD	Bus	Allrad	Diesel	Nov 2001	Aug 2006	59373
Toyota	Hiace iv	2.7 4WD	Bus	Allrad	Benzin	Apr 1998	Aug 2006	14330
Toyota	Hiace iv	2.7 4WD	Kasten	Allrad	Benzin	Jul 1998	Jun 2005	14331
Toyota	Hiace iv	2.7 4WD	Bus	Allrad	Benzin	Jul 1998	Jun 2005	58716
Toyota	Hiace v	2.5 D-4d	Kasten	Heckantrieb	Diesel	Jun 2004	-	11806
Toyota	Hiace v	2.5 D-4d	Kasten	Heckantrieb	Diesel	Sep 2006	-	55939
Toyota	Hiace v	3.0 D	Kasten	Heckantrieb	Diesel	Nov 2008	-	12163
Toyota	Hilux iv	2	Pick-up	Heckantrieb	Benzin	Aug 1983	Jul 1988	8715
Toyota	Hilux iv	2.4 D	Pick-up	Heckantrieb	Diesel	Sep 1984	Jul 1988	127891
Toyota	Hilux v	1.8	Pick-up	Heckantrieb	Benzin	Sep 1988	Jun 1998	10473
Toyota	Hilux v	2.4 D	Pick-up	Heckantrieb	Diesel	Mar 1995	Aug 1997	10479
Toyota	Hilux v	2.4 D	Pick-up	Heckantrieb	Diesel	Sep 1988	Aug 1997	10759
Toyota	Hilux v	2.4 D 4WD	Pick-up	Allrad	Diesel	Jan 1994	Dec 1997	8714
Toyota	Hilux v	2.4 D 4WD	Pick-up	Allrad	Diesel	Sep 1988	Aug 1997	10760
Toyota	Hilux v	2.4 EFI 4WD	Pick-up	Allrad	Benzin	Jan 1989	Jul 1997	8712
Toyota	Hilux vi	2.4 D	Pick-up	Heckantrieb	Diesel	Aug 1997	Apr 2005	14473
Toyota	Hilux vi	2.4 D	Pick-up	Heckantrieb	Diesel	Aug 1997	Jul 2005	124036
Toyota	Hilux vi	2.4 TD 4WD	Pick-up	Allrad	Diesel	Aug 1998	Jan 2002	10079
Toyota	Hilux vi	2.5 D-4d	Pick-up	Heckantrieb	Diesel	Nov 2001	Jul 2005	16548
Toyota	Hilux vi	2.5 D-4d 4WD	Pick-up	Allrad	Diesel	Nov 2001	Jul 2005	16549
Toyota	Hilux vii	2.5 D-4d 4WD	Pick-up	Allrad	Diesel	Dec 2007	May 2015	34943
Toyota	Hilux vii	2.5 D-4d 4WD	Pick-up	Allrad	Diesel	Nov 2004	Dec 2005	110594
Toyota	Hilux vii	3.0 D-4d 4WD	Pick-up	Allrad	Diesel	Mar 2005	May 2015	34581
Toyota	Hilux vii	3.0 D-4d 4WD	Pick-up	Allrad	Diesel	May 2008	Dec 2012	116996
Toyota	Hilux viii	2.4 D	Pick-up	Heckantrieb	Diesel	May 2015	-	115114
Toyota	Hilux viii	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2015	-	117640
Toyota	Hilux viii	2.4 D 4WD	Pick-up	Allrad	Diesel	May 2015	-	115118
Toyota	Hilux viii	2.8 D-4d	Pick-up	Heckantrieb	Diesel	May 2015	Feb 2021	115123
Toyota	Hilux viii	2.8 D-4d 48V Mhev 4WD	Pick-up	Allrad	Diesel/Elektro	Mar 2024	-	158032
Toyota	Hilux viii	2.8 D-4d 4WD	Pick-up	Allrad	Diesel	May 2015	Feb 2021	115124
Toyota	Hilux viii	2.8 D-4d 4WD	Pick-up	Allrad	Diesel	Nov 2024	-	801232
Toyota	Hilux viii	2.8 D-4d Mhev 4WD	Pick-up	Allrad	Diesel/Elektro	Nov 2024	-	801233
Toyota	Land cruiser	3.9	Geländewagen geschlossen	Allrad	Benzin	Mar 1969	Jan 1975	15743


--- Round 1 / 首次发送 ---
## 1）更新点

已完成 Corolla 既有尺寸组复用，并将跨越不同车长的 Corolla Verso Ktype 18041、19068 分拆为改款前与改款后物理分支。乘用车部分已闭合 Corona、Cressida、FJ Cruiser、Fortuner、GT86、GR86 与 Land Cruiser J40。商用车按家族缓存完成了大部分 Dyna、Hiace、Hilux 的标准量产外廓关联；官方资料明确列出多种驾驶室、轴距或车顶而输入无法定位的项目继续保留 PENDING。 ([CarsGuide][1])

## 2）当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：100
* READY Ktype：90
* PENDING Ktype：10
* 当前映射行：102，其中 Corolla Verso 两个 Ktype 各拆分为两行
* 本轮首次建立尺寸组：24
* 剩余阻塞：Dyna 5 个、Hiace 1 个、Hilux 4 个

## 3）本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15718	15718	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15565	15565	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15566	15566	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15567	15567	Wagon	E110	E110	5	EU-TOYOTA-COROLLA-E110-WAGON-STANDARD-01	HIGH		READY
16033	16033	Sedan	E110	E110	4	EU-TOYOTA-COROLLA-E110-SEDAN-STANDARD-01	HIGH		READY
17439	17439	Hatchback	E120/E130	E120/E130	5	EU-TOYOTA-COROLLA-E120-E130-HATCHBACK-STANDARD-01	HIGH		READY
17856	17856	Sedan	E120/E130	E120/E130	4	EU-TOYOTA-COROLLA-E120-E130-SEDAN-STANDARD-01	HIGH		READY
18041_prefl	18041	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
18041_facelift	18041	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
18220	18220	Wagon	E120/E130	E120/E130	5	EU-TOYOTA-COROLLA-E120-E130-WAGON-STANDARD-01	HIGH		READY
144564	144564	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
151825	151825	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
801666	801666	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
144565	144565	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
151826	151826	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
801665	801665	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
149658	149658	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
802015	802015	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
802818	802818	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
149659	149659	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
19068_prefl	19068	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
19068_facelift	19068	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
10741	10741	Wagon	T100/T120	RT118	5	EU-TOYOTA-CORONA-T100-WAGON-STANDARD-01	MEDIUM	Generic 2.0 wagon mapped to the standard 1977 wagon envelope.	READY
5058	5058	Sedan	X60	LX60	4	EU-TOYOTA-CRESSIDA-X60-SEDAN-STANDARD-01	HIGH		READY
59447	59447	Sedan	X70	LX71	4	EU-TOYOTA-CRESSIDA-X70-SEDAN-STANDARD-01	HIGH		READY
110599	110599	Wagon	X30	RX30	5	EU-TOYOTA-CRESSIDA-X30-WAGON-STANDARD-01	HIGH		READY
18850	18850	Pickup	IV			EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
18851	18851	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
18852	18852	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
18853	18853	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
55605	55605	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Input does not identify bed/cab detail; official just-low representative envelope selected.	READY
125328	125328	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Input does not identify bed/cab detail; official just-low representative envelope selected.	READY
59388	59388	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Input does not identify bed/cab detail; official just-low representative envelope selected.	READY
59460	59460	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Input does not identify bed/cab detail; official just-low representative envelope selected.	READY
59458	59458	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Input does not identify bed/cab detail; official just-low representative envelope selected.	READY
10664	10664	Pickup	U300/U400			EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
13887	13887	Pickup	U300/U400			EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	MEDIUM	Input does not identify cab or wheelbase; standard narrow-cab representative envelope selected.	READY
18854	18854	MPV					LOW		PENDING: Dyna bus body dimensions not yet closed
18855	18855	MPV					LOW		PENDING: Dyna bus body dimensions not yet closed
11251	11251	Pickup					LOW		PENDING: 4.0 D-4D cab and wheelbase branch not yet closed
13888	13888	Pickup					LOW		PENDING: 4WD 4.0 D-4D cab and wheelbase branch not yet closed
121636	121636	Pickup					LOW		PENDING: 1995-2001 Dyna 100 outer envelope not yet closed
12252	12252	SUV	XJ10	GSJ15	5	EU-TOYOTA-FJ-CRUISER-XJ10-SUV-STANDARD-01	HIGH		READY
116366	116366	SUV	II	AN160	5	EU-TOYOTA-FORTUNER-II-SUV-STANDARD-01	HIGH		READY
147244	147244	Coupe	II	ZN8	2	EU-TOYOTA-GR86-ZN8-COUPE-STANDARD-01	HIGH		READY
15977	15977	Coupe	I	ZN6	2	EU-TOYOTA-GT86-ZN6-COUPE-STANDARD-01	HIGH		READY
11805	11805	MPV	V	H200		EU-TOYOTA-HIACE-H200-MPV-COMMUTER-01	HIGH	Commuter name identifies the super-long high-roof passenger branch.	READY
10764	10764	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Input does not identify body length; standard van envelope selected.	READY
10742	10742	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Input does not identify body length; standard van envelope selected.	READY
10743	10743	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Input does not identify body length; standard van envelope selected.	READY
10765	10765	Van	III	H50/H60/H70		EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	MEDIUM	Input does not identify body length; standard van envelope selected.	READY
10766	10766	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
34712	34712	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14326	14326	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14327	14327	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
16556	16556	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14324	14324	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14325	14325	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
10768	10768	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14436	14436	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
18554	18554	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
10779	10779	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14328	14328	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14329	14329	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
16546	16546	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
16547	16547	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
16557	16557	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
16558	16558	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
59373	59373	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14330	14330	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
14331	14331	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
58716	58716	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Input does not identify wheelbase or roof; standard H100 one-box envelope selected.	READY
18553	18553	MPV	III/IV				LOW		PENDING: pre-H100 4WD bus height and body length not yet closed
11806	11806	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Input does not identify roof or body length; standard-roof van envelope selected.	READY
55939	55939	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Input does not identify roof or body length; standard-roof van envelope selected.	READY
12163	12163	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Input does not identify roof or body length; standard-roof van envelope selected.	READY
8715	8715	Pickup	IV	N50/N60		EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	MEDIUM	Input does not identify cab/bed length; long-body representative envelope selected.	READY
127891	127891	Pickup	IV	N50/N60		EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	MEDIUM	Input does not identify cab/bed length; long-body representative envelope selected.	READY
10473	10473	Pickup	V	N80/N90/N100/N110			LOW		PENDING: RWD cab/bed branch and matching height not yet closed
10479	10479	Pickup	V	N80/N90/N100/N110			LOW		PENDING: RWD cab/bed branch and matching height not yet closed
10759	10759	Pickup	V	N80/N90/N100/N110			LOW		PENDING: RWD cab/bed branch and matching height not yet closed
8714	8714	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	Input does not identify cab/bed length; 4WD long-body representative envelope selected.	READY
10760	10760	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	Input does not identify cab/bed length; 4WD long-body representative envelope selected.	READY
8712	8712	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	Input does not identify cab/bed length; 4WD long-body representative envelope selected.	READY
14473	14473	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Input does not identify cab; official 2WD double-cab representative envelope selected.	READY
124036	124036	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Input does not identify cab; official 2WD double-cab representative envelope selected.	READY
16548	16548	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Input does not identify cab; official 2WD double-cab representative envelope selected.	READY
10079	10079	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	MEDIUM	Input does not identify cab; official 4WD standard-cab representative envelope selected.	READY
16549	16549	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	MEDIUM	Input does not identify cab; official 4WD standard-cab representative envelope selected.	READY
34943	34943	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	Input does not identify cab; European 4WD double-cab representative envelope selected.	READY
110594	110594	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	Input does not identify cab; European 4WD double-cab representative envelope selected.	READY
34581	34581	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	Input does not identify cab; European 4WD double-cab representative envelope selected.	READY
116996	116996	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	Input does not identify cab; European 4WD double-cab representative envelope selected.	READY
115114	115114	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
115118	115118	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
115123	115123	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
158032	158032	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
115124	115124	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
801232	801232	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
801233	801233	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Input does not identify cab; standard-width double-cab envelope selected.	READY
117640	117640	Pickup	VIII	AN120/AN130			LOW		PENDING: chassis-cab has no closed complete outer envelope without body specification
15743	15743	SUV	J40	FJ40	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	HIGH		READY
```

## 4）本轮首次创建/修正的 DIMENSION_GROUP TSV

复用的 Corolla 历史组未重复输出。

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CORONA-T100-WAGON-STANDARD-01	4280	1610	1420	CarsGuide	https://www.carsguide.com.au/toyota/corona/car-dimensions/1977
EU-TOYOTA-CRESSIDA-X60-SEDAN-STANDARD-01	4500	1680	1450	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Toyota/5313/Toyota-Cressida-II-22-Diesel.html
EU-TOYOTA-CRESSIDA-X70-SEDAN-STANDARD-01	4690	1690	1420	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Toyota/5316/Toyota-Cressida-III-24-TD.html
EU-TOYOTA-CRESSIDA-X30-WAGON-STANDARD-01	4530	1680	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/3474080/toyota_cressida_2000_wagon.html
EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	4690	1690	1990	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014348/index.html
EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	4690	1695	1990	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60016639/index.html
EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	4430	1695	1940	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001680/
EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	4690	1695	1985	Goo-net catalog	https://www.goo-net.com/catalog/TOYOTA/DYNA/834935/
EU-TOYOTA-FJ-CRUISER-XJ10-SUV-STANDARD-01	4671	1905	1830	Auto-Data	https://www.auto-data.net/en/toyota-fj-cruiser-model-467
EU-TOYOTA-FORTUNER-II-SUV-STANDARD-01	4795	1855	1835	Auto-Data	https://www.auto-data.net/en/toyota-fortuner-ii-2.8-d-4d-177hp-4wd-automatic-33584
EU-TOYOTA-GR86-ZN8-COUPE-STANDARD-01	4265	1775	1310	Auto-Data	https://www.auto-data.net/en/toyota-86-ii-gr-2.4-d-4s-235hp-43105
EU-TOYOTA-GT86-ZN6-COUPE-STANDARD-01	4240	1775	1285	Auto-Data	https://www.auto-data.net/en/toyota-86-i-2.0-d-4s-200hp-18501
EU-TOYOTA-HIACE-H200-MPV-COMMUTER-01	5380	1880	2285	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015464/
EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	4340	1690	1925	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/
EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	4425	1690	1950	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	4615	1690	1980	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html
EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	4695	1695	1980	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015495/index.html
EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	4690	1610	1560	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015530/index.html
EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	4690	1690	1765	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015538/index.html
EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	4690	1690	1640	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015606/index.html
EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	4690	1690	1760	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015606/index.html
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	5255	1835	1810	Toyota Europe	https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	5325	1855	1810	Toyota Europe technical data	https://newsroom.toyota.eu/download/939287/19.10.20newhiluxdpl-technicaldatafinal.doc
EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	3870	1665	1950	Auta5P	https://auta5p.eu/lang/en/katalog/auto.php?idf=Toyota-Land-Cruiser-FJ40-3.9-26770
```

## 5）下一步优先处理

优先按共享外廓一次闭合剩余分支：

1. Dyna 1977–1987 Bus：18854、18855。
2. Dyna 4.0 D-4D 与 Dyna 100：11251、13888、121636。
3. Hiace 1987–1995 4WD Bus：18553。
4. Hilux V 后驱标准车身：10473、10479、10759。
5. Hilux VIII chassis-cab：117640；只在找到完整出厂外廓时落盘，不把无车斗底盘长度当成完整 Pickup 外廓。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/toyota/corona/car-dimensions/1977 "https://www.carsguide.com.au/toyota/corona/car-dimensions/1977"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16201-16300_ktype_dimension_mapping_final.tsv
- left18448_16201-16300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1）更新点

缓存优先闭合 8 个 PENDING：

* 18854、18855 分别关联既有 Dyna IV、Dyna V 标准窄体尺寸组。
* 18553 按其 LH51/LH61/LH66/LH71 车身代码关联既有 Hiace H50 标准尺寸组，不扩展 H100 理论分支。([丰田官网][1])
* 121636 建立 Dyna 100 / LY100 标准货台尺寸组。([丰田官网][2])
* 10473、10479、10759 共用 Hilux V 后驱标准单排尺寸组。([CarsGuide][3])
* 117640 建立 Hilux VIII 2.4D 后驱单排底盘尺寸组。([丰田澳大利亚][4])
* 剩余 PENDING 仅为 Dyna 4.0 D-4D 的 11251、13888。

## 2）当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* PENDING Ktype：2
* 当前映射行：102
* READY 映射行：100
* PENDING 映射行：2
* 当前引用 DIMENSION_GROUP：38
* 本轮新建 DIMENSION_GROUP：3

## 3）本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18854	18854	MPV	IV	JU20		EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	MEDIUM	JU20 standard single-tire outer envelope selected.	READY
18855	18855	MPV	V	BU82		EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	HIGH		READY
121636	121636	Pickup	Dyna 100	LY100/LY100R		EU-TOYOTA-DYNA-100-LY100-PICKUP-STANDARD-01	MEDIUM	Standard-deck branch selected.	READY
18553	18553	MPV	III	LH51/LH61/LH66/LH71		EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	MEDIUM	Standard H50/H60/H70 outer envelope selected.	READY
10473	10473	Pickup	V			EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
10479	10479	Pickup	V			EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
10759	10759	Pickup	V			EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
117640	117640	Pickup	VIII	GUN112/GUN122/GUN135		EU-TOYOTA-HILUX-VIII-PICKUP-SINGLECAB-CHASSIS-01	HIGH	Standard 4x2 single-cab chassis branch selected.	READY
```

## 4）本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-DYNA-100-LY100-PICKUP-STANDARD-01	4430	1695	1940	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015363/index.html
EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	4725	1650	1555	CarsGuide	https://www.carsguide.com.au/toyota/hilux/car-dimensions/1989
EU-TOYOTA-HILUX-VIII-PICKUP-SINGLECAB-CHASSIS-01	5265	1800	1855	Toyota Australia	https://www.toyota.com.au/hilux/gr-sport
```

## 5）下一步优先处理

只处理剩余两个阻塞项：

1. 11251：Dyna 4.0 D-4D 后驱，按已确认的 XZU417/XZU423/XZU425/XZU427/XZU435 物理边界确定最匹配标准分支。
2. 13888：Dyna 4.0 D-4D 4WD，按 XZU675/XZU685/XZU695/XZU775 确认标准四驱外廓；不与后驱组强行合并。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014348/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015363/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[3]: https://www.carsguide.com.au/toyota/hilux/car-dimensions/1989 "Toyota HiLux Dimensions 1989 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[4]: https://www.toyota.com.au/hilux/gr-sport?srsltid=AfmBOoor-0TjO2qCgIyZ9w5okIpXFd76I04m3vFHv2yhUlo4dHKFu3ZS "HiLux GR Sport 2024 | 4x4 Utes | Toyota Australia"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16201-16300_ktype_dimension_mapping_final.tsv
- left18448_16201-16300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1）更新点

剩余 Ktype 11251、13888 已闭合，分别关联标准短轴后驱和标准单排四驱 Dyna 尺寸组。复用的 Corolla 尺寸组已补齐完整来源字段；机械终检确认无缺失引用、孤立尺寸组或 PENDING。([Mattaki][1])

## 2）进度

* 输入 Ktype：100
* 最终映射行：102
* READY 映射行：102
* PENDING：0
* DIMENSION_GROUP：40
* `id` 与 `DIMENSION_GROUP_ID`：各自唯一
* 映射引用：全部闭合
* 三维、来源及 URL：全部非空

## 3）最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15718	15718	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15565	15565	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15566	15566	Hatchback	E110	E110	5	EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	HIGH		READY
15567	15567	Wagon	E110	E110	5	EU-TOYOTA-COROLLA-E110-WAGON-STANDARD-01	HIGH		READY
16033	16033	Sedan	E110	E110	4	EU-TOYOTA-COROLLA-E110-SEDAN-STANDARD-01	HIGH		READY
17439	17439	Hatchback	E120/E130	E120/E130	5	EU-TOYOTA-COROLLA-E120-E130-HATCHBACK-STANDARD-01	HIGH		READY
17856	17856	Sedan	E120/E130	E120/E130	4	EU-TOYOTA-COROLLA-E120-E130-SEDAN-STANDARD-01	HIGH		READY
18041_prefl	18041	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
18041_facelift	18041	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
18220	18220	Wagon	E120/E130	E120/E130	5	EU-TOYOTA-COROLLA-E120-E130-WAGON-STANDARD-01	HIGH		READY
144564	144564	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
144565	144565	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
151825	151825	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
151826	151826	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
801665	801665	Wagon	E210	E210	5	EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	HIGH		READY
801666	801666	Hatchback	E210	E210	5	EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	HIGH		READY
149658	149658	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
802015	802015	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
802818	802818	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
149659	149659	SUV	Corolla Cross I	XG10	5	EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	HIGH		READY
19068_prefl	19068	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
19068_facelift	19068	MPV	Corolla Verso AR10	AR10	5	EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	HIGH	Ktype spans Corolla Verso pre-facelift and facelift outer lengths; split by physical length.	READY
10741	10741	Wagon	T100/T120	RT118	5	EU-TOYOTA-CORONA-T100-WAGON-STANDARD-01	MEDIUM	Generic 2.0 wagon mapped to the standard 1977 wagon envelope.	READY
5058	5058	Sedan	X60	LX60	4	EU-TOYOTA-CRESSIDA-X60-SEDAN-STANDARD-01	HIGH		READY
59447	59447	Sedan	X70	LX71	4	EU-TOYOTA-CRESSIDA-X70-SEDAN-STANDARD-01	HIGH		READY
110599	110599	Wagon	X30	RX30	5	EU-TOYOTA-CRESSIDA-X30-WAGON-STANDARD-01	HIGH		READY
18850	18850	Pickup	IV			EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
18851	18851	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
18852	18852	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
18854	18854	MPV	IV	JU20		EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	MEDIUM	JU20 standard single-tire outer envelope selected.	READY
55605	55605	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Standard just-low representative envelope selected.	READY
125328	125328	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Standard just-low representative envelope selected.	READY
10664	10664	Pickup	U300/U400			EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
13887	13887	Pickup	U300/U400			EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
18853	18853	Pickup	V			EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	MEDIUM	Standard narrow-cab representative envelope selected.	READY
18855	18855	MPV	V	BU82		EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	HIGH		READY
11251	11251	Pickup	U400	XZU417/XZU423/XZU425/XZU427/XZU435	2	EU-TOYOTA-DYNA-U400-PICKUP-STANDARD-2WD-01	MEDIUM	Standard short-wheelbase cab-chassis branch selected.	READY
13888	13888	Pickup	U700	XZU675/XZU685/XZU695/XZU775	2	EU-TOYOTA-DYNA-U700-PICKUP-STANDARD-4WD-01	MEDIUM	Standard single-cab 4WD branch selected.	READY
59388	59388	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Standard just-low representative envelope selected.	READY
121636	121636	Pickup	Dyna 100	LY100/LY100R		EU-TOYOTA-DYNA-100-LY100-PICKUP-STANDARD-01	MEDIUM	Standard-deck branch selected.	READY
59460	59460	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Standard just-low representative envelope selected.	READY
59458	59458	Pickup	Y50			EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	MEDIUM	Standard just-low representative envelope selected.	READY
12252	12252	SUV	XJ10	GSJ15	5	EU-TOYOTA-FJ-CRUISER-XJ10-SUV-STANDARD-01	HIGH		READY
116366	116366	SUV	II	AN160	5	EU-TOYOTA-FORTUNER-II-SUV-STANDARD-01	HIGH		READY
147244	147244	Coupe	II	ZN8	2	EU-TOYOTA-GR86-ZN8-COUPE-STANDARD-01	HIGH		READY
15977	15977	Coupe	I	ZN6	2	EU-TOYOTA-GT86-ZN6-COUPE-STANDARD-01	HIGH		READY
11805	11805	MPV	V	H200		EU-TOYOTA-HIACE-H200-MPV-COMMUTER-01	HIGH	Commuter name identifies the super-long high-roof passenger branch.	READY
10764	10764	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Standard van envelope selected.	READY
10742	10742	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Standard van envelope selected.	READY
10743	10743	Van	II	H20/H30		EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	MEDIUM	Standard van envelope selected.	READY
10765	10765	Van	III	H50/H60/H70		EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	MEDIUM	Standard van envelope selected.	READY
10766	10766	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
34712	34712	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14326	14326	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14327	14327	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
16556	16556	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14324	14324	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14325	14325	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
10768	10768	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14436	14436	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
18553	18553	MPV	III	LH51/LH61/LH66/LH71		EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	MEDIUM	Standard H50/H60/H70 outer envelope selected.	READY
18554	18554	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
10779	10779	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14328	14328	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14329	14329	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
16546	16546	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
16547	16547	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
16557	16557	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
16558	16558	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
59373	59373	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14330	14330	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
14331	14331	Van	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
58716	58716	MPV	IV	H100		EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	MEDIUM	Standard H100 one-box envelope selected.	READY
11806	11806	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Standard-roof van envelope selected.	READY
55939	55939	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Standard-roof van envelope selected.	READY
12163	12163	Van	V	H200		EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	MEDIUM	Standard-roof van envelope selected.	READY
8715	8715	Pickup	IV	N50/N60		EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	MEDIUM	Long-body representative envelope selected.	READY
127891	127891	Pickup	IV	N50/N60		EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	MEDIUM	Long-body representative envelope selected.	READY
10473	10473	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
10479	10479	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
10759	10759	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	MEDIUM	Standard 2WD single-cab outer envelope selected.	READY
8714	8714	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	4WD long-body representative envelope selected.	READY
10760	10760	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	4WD long-body representative envelope selected.	READY
8712	8712	Pickup	V	N80/N90/N100/N110		EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	MEDIUM	4WD long-body representative envelope selected.	READY
14473	14473	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Official 2WD double-cab representative envelope selected.	READY
124036	124036	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Official 2WD double-cab representative envelope selected.	READY
10079	10079	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	MEDIUM	Official 4WD standard-cab representative envelope selected.	READY
16548	16548	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	MEDIUM	Official 2WD double-cab representative envelope selected.	READY
16549	16549	Pickup	VI	N140/N150/N160/N170		EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	MEDIUM	Official 4WD standard-cab representative envelope selected.	READY
34943	34943	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	European 4WD double-cab representative envelope selected.	READY
110594	110594	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	European 4WD double-cab representative envelope selected.	READY
34581	34581	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	European 4WD double-cab representative envelope selected.	READY
116996	116996	Pickup	VII	AN10/AN20/AN30		EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	MEDIUM	European 4WD double-cab representative envelope selected.	READY
115114	115114	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
117640	117640	Pickup	VIII	GUN112/GUN122/GUN135		EU-TOYOTA-HILUX-VIII-PICKUP-SINGLECAB-CHASSIS-01	HIGH	Standard 4x2 single-cab chassis branch selected.	READY
115118	115118	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
115123	115123	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
158032	158032	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
115124	115124	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
801232	801232	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
801233	801233	Pickup	VIII	AN120/AN130		EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Standard-width double-cab envelope selected.	READY
15743	15743	SUV	J40	FJ40	2	EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	HIGH		READY
```

[下载 left18448_16201-16300_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_16201-16300_ktype_dimension_mapping_final.tsv)

## 4）最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-E110-HATCHBACK-LIFTBACK-01	4270	1690	1385	Auto-Data	https://www.auto-data.net/en/toyota-corolla-hatch-viii-e110-generation-827
EU-TOYOTA-COROLLA-E110-WAGON-STANDARD-01	4320	1690	1445	Auto-Data	https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-2.0-d-72hp-3346
EU-TOYOTA-COROLLA-E110-SEDAN-STANDARD-01	4295	1690	1385	Auto-Data	https://www.auto-data.net/en/toyota-corolla-viii-e110-generation-825
EU-TOYOTA-COROLLA-E120-E130-HATCHBACK-STANDARD-01	4180	1710	1475	Auto-Data	https://www.auto-data.net/en/toyota-corolla-hatch-ix-e120-e130-generation-819
EU-TOYOTA-COROLLA-E120-E130-SEDAN-STANDARD-01	4375	1710	1470	Auto-Data	https://www.auto-data.net/en/toyota-corolla-ix-e120-e130-2.0-d-4d-90hp-3312
EU-TOYOTA-COROLLA-E120-E130-WAGON-STANDARD-01	4410	1710	1520	Auto-Data	https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-generation-820
EU-TOYOTA-COROLLA-AR10-MPV-PREFACELIFT-01	4360	1770	1620	Auto-Data	https://www.auto-data.net/en/toyota-corolla-verso-ii-ar10-1.6-vvt-i-110hp-42295
EU-TOYOTA-COROLLA-AR10-MPV-FACELIFT-01	4370	1770	1620	Auto-Data	https://www.auto-data.net/en/toyota-corolla-verso-ii-ar10-facelift-2007-2.2-d-4d-136hp-17126
EU-TOYOTA-COROLLA-E210-HATCHBACK-STANDARD-01	4370	1790	1435	Auto-Data	https://www.auto-data.net/en/toyota-corolla-hatchback-xii-e210-2.0-180hp-hybrid-e-cvt-34627
EU-TOYOTA-COROLLA-E210-WAGON-STANDARD-01	4650	1790	1435	Auto-Data	https://www.auto-data.net/en/toyota-corolla-touring-sports-xii-e210-generation-6607
EU-TOYOTA-COROLLA-CROSS-I-SUV-STANDARD-01	4460	1825	1620	Auto-Data	https://www.auto-data.net/en/toyota-corolla-cross-2.0-197hp-hybrid-e-four-e-cvt-45158
EU-TOYOTA-CORONA-T100-WAGON-STANDARD-01	4280	1610	1420	CarsGuide	https://www.carsguide.com.au/toyota/corona/car-dimensions/1977
EU-TOYOTA-CRESSIDA-X60-SEDAN-STANDARD-01	4500	1680	1450	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Toyota/5313/Toyota-Cressida-II-22-Diesel.html
EU-TOYOTA-CRESSIDA-X70-SEDAN-STANDARD-01	4690	1690	1420	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Toyota/5316/Toyota-Cressida-III-24-TD.html
EU-TOYOTA-CRESSIDA-X30-WAGON-STANDARD-01	4530	1680	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/3474080/toyota_cressida_2000_wagon.html
EU-TOYOTA-DYNA-IV-PICKUP-NARROW-STANDARD-01	4690	1690	1990	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014348/index.html
EU-TOYOTA-DYNA-V-PICKUP-NARROW-STANDARD-01	4690	1695	1990	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60016639/index.html
EU-TOYOTA-DYNA-Y50-PICKUP-JUSTLOW-01	4430	1695	1940	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001680/
EU-TOYOTA-DYNA-U300-PICKUP-NARROW-STANDARD-01	4690	1695	1985	Goo-net catalog	https://www.goo-net.com/catalog/TOYOTA/DYNA/834935/
EU-TOYOTA-DYNA-100-LY100-PICKUP-STANDARD-01	4430	1695	1940	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015363/index.html
EU-TOYOTA-DYNA-U400-PICKUP-STANDARD-2WD-01	4710	1850	2100	Hino 616 official specification	https://cdn.mattaki.com/hino/static-assets/vehicles/specifications/300-Series/616-STD-AT.pdf
EU-TOYOTA-DYNA-U700-PICKUP-STANDARD-4WD-01	4685	1695	1990	Nextage Toyota catalog	https://www.nextage.jp/carcatalog/toyota/dyna/tkg-xzu675/
EU-TOYOTA-FJ-CRUISER-XJ10-SUV-STANDARD-01	4671	1905	1830	Auto-Data	https://www.auto-data.net/en/toyota-fj-cruiser-model-467
EU-TOYOTA-FORTUNER-II-SUV-STANDARD-01	4795	1855	1835	Auto-Data	https://www.auto-data.net/en/toyota-fortuner-ii-2.8-d-4d-177hp-4wd-automatic-33584
EU-TOYOTA-GR86-ZN8-COUPE-STANDARD-01	4265	1775	1310	Auto-Data	https://www.auto-data.net/en/toyota-86-ii-gr-2.4-d-4s-235hp-43105
EU-TOYOTA-GT86-ZN6-COUPE-STANDARD-01	4240	1775	1285	Auto-Data	https://www.auto-data.net/en/toyota-86-i-2.0-d-4s-200hp-18501
EU-TOYOTA-HIACE-H200-MPV-COMMUTER-01	5380	1880	2285	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015464/
EU-TOYOTA-HIACE-H20-VAN-STANDARD-01	4340	1690	1925	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/
EU-TOYOTA-HIACE-H50-VAN-STANDARD-01	4425	1690	1950	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-HIACE-H100-ONEBOX-STANDARD-01	4615	1690	1980	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html
EU-TOYOTA-HIACE-H200-VAN-STANDARD-01	4695	1695	1980	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015495/index.html
EU-TOYOTA-HILUX-IV-PICKUP-LONG-STANDARD-01	4690	1610	1560	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015530/index.html
EU-TOYOTA-HILUX-V-PICKUP-LONG-4WD-01	4690	1690	1765	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015538/index.html
EU-TOYOTA-HILUX-V-PICKUP-RWD-STANDARD-01	4725	1650	1555	CarsGuide	https://www.carsguide.com.au/toyota/hilux/car-dimensions/1989
EU-TOYOTA-HILUX-VI-PICKUP-DOUBLECAB-2WD-01	4690	1690	1640	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015606/index.html
EU-TOYOTA-HILUX-VI-PICKUP-STANDARDCAB-4WD-01	4690	1690	1760	Toyota official vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015606/index.html
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLECAB-4WD-01	5255	1835	1810	Toyota Europe	https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VIII-PICKUP-DOUBLECAB-STANDARD-01	5325	1855	1810	Toyota Europe technical data	https://newsroom.toyota.eu/download/939287/19.10.20newhiluxdpl-technicaldatafinal.doc
EU-TOYOTA-HILUX-VIII-PICKUP-SINGLECAB-CHASSIS-01	5265	1800	1855	Toyota Australia	https://www.toyota.com.au/hilux/gr-sport
EU-TOYOTA-LAND-CRUISER-J40-SUV-SWB-HARDTOP-01	3870	1665	1950	Auta5P	https://auta5p.eu/lang/en/katalog/auto.php?idf=Toyota-Land-Cruiser-FJ40-3.9-26770
```

[下载 left18448_16201-16300_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_16201-16300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://cdn.mattaki.com/hino/static-assets/vehicles/specifications/300-Series/616-STD-AT.pdf?utm_source=chatgpt.com "616 STD Cab - Mattaki"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3088 行）
- 累计尺寸组：dimension_groups_final.tsv（782 行）

