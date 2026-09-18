# 任务：left18448 第 15001-15100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0151__a99a6789


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 15001-15100 行

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
left18448 第 15001-15100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_15001-15100_ktype_dimension_mapping_final.tsv
- left18448_15001-15100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	4315	1768	1458
EU-SEAT-LEON-III-COUPE-FACELIFT17-01	4247	1810	1446
EU-SEAT-LEON-III-COUPE-PREFL-01	4228	1810	1446
EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	4282	1816	1459
EU-SEAT-LEON-III-HATCHBACK-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-WAGON-FACELIFT17-01	4549	1816	1451
EU-SEAT-LEON-III-WAGON-PREFL-01	4535	1816	1451
EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	4368	1799	1456
EU-SEAT-LEON-IV-WAGON-STANDARD-01	4642	1799	1450

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Seat	Leon	1.4 TSI	Schrägheck	Frontantrieb	Benzin	Sep 2012	Aug 2020	57590
Seat	Leon	1.4 TSI	Coupe	Frontantrieb	Benzin	Feb 2013	Jun 2015	59598
Seat	Leon	1.4 TSI	Coupe	Frontantrieb	Benzin	Feb 2013	Nov 2016	59599
Seat	Leon	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Aug 2020	106385
Seat	Leon	1.4 TSI	Schrägheck	Frontantrieb	Benzin	May 2014	Aug 2020	106386
Seat	Leon	1.4 TSI	Coupe	Frontantrieb	Benzin	May 2014	Aug 2018	106388
Seat	Leon	1.4 TSI	Coupe	Frontantrieb	Benzin	May 2014	Aug 2018	106389
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	May 2014	Aug 2018	106393
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	May 2014	Aug 2020	106395
Seat	Leon	1.5 Ehybrid	Kombi	Frontantrieb	Benzin/Elektro	Jun 2024	-	801094
Seat	Leon	1.5 E-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2024	-	801050
Seat	Leon	1.5 E-hybrid	Kombi	Frontantrieb	Benzin/Elektro	Oct 2024	-	801051
Seat	Leon	1.5 E-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	801095
Seat	Leon	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	May 2024	-	800144
Seat	Leon	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	May 2024	-	800145
Seat	Leon	1.5 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	May 2021	-	144672
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	May 2024	-	158770
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	May 2024	-	159071
Seat	Leon	1.6 16 V	Schrägheck	Frontantrieb	Benzin	Sep 2000	Jun 2006	15640
Seat	Leon	1.6 SRE	Schrägheck	Frontantrieb	Benzin	Nov 2020	-	157067
Seat	Leon	1.6 SRE	Kombi	Frontantrieb	Benzin	Mar 2021	-	157068
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2012	Aug 2020	56777
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2012	Aug 2018	56778
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2013	Aug 2020	59057
Seat	Leon	1.6 TDI	Coupe	Frontantrieb	Diesel	Feb 2013	Aug 2018	59603
Seat	Leon	1.6 TDI	Coupe	Frontantrieb	Diesel	Feb 2013	Aug 2018	59605
Seat	Leon	1.6 TDI	Coupe	Frontantrieb	Diesel	Sep 2013	Nov 2016	59606
Seat	Leon	1.6 TDI	Kombi	Frontantrieb	Diesel	Sep 2013	Aug 2020	100793
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2016	Aug 2020	124050
Seat	Leon	1.6 TDI	Kombi	Frontantrieb	Diesel	Nov 2016	Aug 2020	124051
Seat	Leon	1.6 TDI	Coupe	Frontantrieb	Diesel	Nov 2016	Aug 2018	124860
Seat	Leon	1.6 TDI 4drive	Kombi	Allrad	Diesel	Apr 2014	Aug 2020	101002
Seat	Leon	1.6 TDI 4drive	Kombi	Allrad	Diesel	Nov 2014	Aug 2020	108633
Seat	Leon	1.8 20V	Schrägheck	Frontantrieb	Benzin	Nov 1999	Jun 2006	13160
Seat	Leon	1.8 20V T	Schrägheck	Frontantrieb	Benzin	Nov 1999	Jun 2006	14413
Seat	Leon	1.8 20V T 4	Schrägheck	Allrad	Benzin	Nov 1999	Jun 2006	14416
Seat	Leon	1.8 T Cupra R	Schrägheck	Frontantrieb	Benzin	Feb 2002	Jun 2006	16692
Seat	Leon	1.8 T Cupra R	Schrägheck	Frontantrieb	Benzin	Jul 2003	Jun 2006	17297
Seat	Leon	1.8 TSI	Schrägheck	Frontantrieb	Benzin	Feb 2013	Aug 2018	57592
Seat	Leon	1.8 TSI	Coupe	Frontantrieb	Benzin	Feb 2013	Aug 2018	59601
Seat	Leon	1.8 TSI 4drive	Kombi	Allrad	Benzin	Nov 2014	Aug 2018	108635
Seat	Leon	1.9 SDI	Schrägheck	Frontantrieb	Diesel	Nov 1999	Jun 2006	14414
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Nov 1999	Jun 2006	13161
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Nov 1999	Jun 2006	13162
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2000	Jun 2006	15725
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	May 2003	Jun 2006	17515
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2005	Dec 2010	18769
Seat	Leon	1.9 TDI Syncro	Schrägheck	Allrad	Diesel	May 2002	Jun 2006	17300
Seat	Leon	2.0 Cupra	Schrägheck	Frontantrieb	Benzin	Oct 2013	Aug 2020	100787
Seat	Leon	2.0 Cupra	Schrägheck	Frontantrieb	Benzin	Oct 2013	Aug 2020	100788
Seat	Leon	2.0 Cupra	Coupe	Frontantrieb	Benzin	Oct 2013	Nov 2016	100790
Seat	Leon	2.0 Cupra	Coupe	Frontantrieb	Benzin	Oct 2013	Nov 2016	100791
Seat	Leon	2.0 Cupra	Kombi	Frontantrieb	Benzin	Oct 2013	Aug 2020	108636
Seat	Leon	2.0 Cupra	Kombi	Frontantrieb	Benzin	Oct 2013	Aug 2020	108637
Seat	Leon	2.0 Cupra	Schrägheck	Frontantrieb	Benzin	Oct 2015	Aug 2020	118000
Seat	Leon	2.0 Cupra	Coupe	Frontantrieb	Benzin	Oct 2015	Nov 2016	118001
Seat	Leon	2.0 Cupra	Kombi	Frontantrieb	Benzin	Oct 2015	Aug 2020	118002
Seat	Leon	2.0 Cupra	Schrägheck	Frontantrieb	Benzin	Jan 2017	Aug 2018	125703
Seat	Leon	2.0 Cupra	Coupe	Frontantrieb	Benzin	Jan 2017	Aug 2018	125718
Seat	Leon	2.0 Cupra	Kombi	Frontantrieb	Benzin	Nov 2016	Aug 2018	125719
Seat	Leon	2.0 Cupra 4drive	Kombi	Allrad	Benzin	Nov 2016	Aug 2020	125720
Seat	Leon	2.0 FSI	Schrägheck	Frontantrieb	Benzin	Jul 2005	May 2010	18767
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Oct 2012	Aug 2020	57594
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2012	Aug 2020	57597
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Aug 2020	59060
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Aug 2020	59061
Seat	Leon	2.0 TDI	Coupe	Frontantrieb	Diesel	May 2013	Aug 2018	59609
Seat	Leon	2.0 TDI	Coupe	Frontantrieb	Diesel	Feb 2013	Aug 2018	59610
Seat	Leon	2.0 TDI	Coupe	Frontantrieb	Diesel	Mar 2013	Aug 2018	59611
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2020	-	143681
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Jun 2021	-	157069
Seat	Leon	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	Jul 2005	Dec 2012	18770
Seat	Leon	2.0 TDI 4drive	Kombi	Allrad	Diesel	Apr 2014	Aug 2020	106226
Seat	Leon	2.0 TDI 4drive	Kombi	Allrad	Diesel	Nov 2014	Aug 2018	108634
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Sep 2005	May 2006	18768
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Mar 2021	-	143678
Seat	Leon	2.0 Tfsi	Kombi	Frontantrieb	Benzin	Mar 2021	-	144218
Seat	Leon	2.8 Cupra 4	Schrägheck	Allrad	Benzin	Feb 2001	Jun 2006	15724
Seat	Leon	TDI 4drive	Kombi	Allrad	Diesel	Nov 2020	-	144219
Seat	Marbella	0.9	Schrägheck	Frontantrieb	Benzin	Jul 1997	Oct 1998	16116
Seat	Mii	1	Schrägheck	Frontantrieb	Benzin	Oct 2011	Jul 2019	15893
Seat	Mii	1	Schrägheck	Frontantrieb	Benzin	Oct 2011	Jul 2019	15944
Seat	Mii	1.0 Ecofuel	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Oct 2012	Jul 2019	57621
Seat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	Oct 1980	Dec 1986	17498
Seat	Ritmo	1.4	Schrägheck	Frontantrieb	Benzin	Jul 1978	Sep 1983	17510
Seat	Tarraco	2.0 Tfsi 4drive	SUV	Allrad	Benzin	Jan 2021	May 2024	143551
Seat	Tarraco	2.0 TSI 4drive	SUV	Allrad	Benzin	Nov 2020	May 2024	801663
Seat	Tarraco	TSI E-hybrid	SUV	Frontantrieb	Benzin/Elektro	Feb 2021	May 2024	144223
Seat	Terra	0.9 CAT	Kombi	Frontantrieb	Benzin	Feb 1992	Dec 1994	8176
Seat	Terra	0.9 CAT	Kasten/Kombi	Frontantrieb	Benzin	Jan 1990	Dec 1995	8177
Seat	Toledo	1.2	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	57522
Seat	Toledo	1.6	Stufenheck	Frontantrieb	Benzin	Oct 1998	Jul 2004	10046
Seat	Toledo	1.6	Großraumlimousine	Frontantrieb	Benzin	Oct 2004	May 2009	18380
Seat	Toledo	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2013	Jun 2015	59063
Seat	Toledo	1.6	Schrägheck	Frontantrieb	Benzin	May 2015	Apr 2019	117374
Seat	Toledo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Apr 2019	128156
Seat	Toledo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Apr 2019	128157
Seat	Toledo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	57523
Seat	Toledo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2012	Jun 2015	57524
Seat	Toledo	1.2 TSI	Schrägheck	Frontantrieb	Benzin	May 2015	May 2017	115144


--- Round 1 / 首次发送 ---
## 更新点

复用 10 个既有 Leon 尺寸组；Leon III 的 Hatchback、Coupe、Wagon 在 2017 改款前后均存在明确长度差异，因此 33 个跨越改款周期的 Ktype 分拆为 `_prefl` 与 `_facelift`。([汽车目录][1])

Leon IV 的 PHEV Hatchback 和 Wagon 高度分别为 1460 mm、1456 mm，与既有标准组不同，因此新增两个 `PHEV-02` 尺寸组；Mii Ecofuel 与普通燃油版继续合并为同一外廓。([汽车目录][2])

## 进度

* 输入 Ktype：100
* 最终映射行：133
* DIMENSION_GROUP：21
* PENDING：0
* 引用闭合、唯一性、正整数尺寸、来源及下载文件检查：全部通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57590_prefl	57590	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
57590_facelift	57590	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59598	59598	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
59599	59599	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
106385_prefl	106385	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
106385_facelift	106385	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
106386_prefl	106386	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
106386_facelift	106386	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
106388_prefl	106388	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
106388_facelift	106388	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
106389_prefl	106389	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
106389_facelift	106389	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
106393_prefl	106393	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
106393_facelift	106393	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
106395_prefl	106395	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
106395_facelift	106395	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
801094	801094	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-PHEV-02	HIGH	PHEV-specific body height.	READY
801050	801050	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-PHEV-02	HIGH	PHEV-specific body height.	READY
801051	801051	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-PHEV-02	HIGH	PHEV-specific body height.	READY
801095	801095	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-PHEV-02	HIGH	PHEV-specific body height.	READY
800144	800144	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
800145	800145	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
144672	144672	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
158770	158770	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
159071	159071	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
15640	15640	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
157067	157067	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
157068	157068	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
56777_prefl	56777	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
56777_facelift	56777	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
56778_prefl	56778	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
56778_facelift	56778	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59057_prefl	59057	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
59057_facelift	59057	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59603_prefl	59603	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59603_facelift	59603	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59605_prefl	59605	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59605_facelift	59605	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59606	59606	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
100793_prefl	100793	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
100793_facelift	100793	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
124050	124050	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH		READY
124051	124051	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH		READY
124860	124860	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH		READY
101002_prefl	101002	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
101002_facelift	101002	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
108633_prefl	108633	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
108633_facelift	108633	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
13160	13160	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
14413	14413	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
14416	14416	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
16692	16692	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
17297	17297	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
57592_prefl	57592	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
57592_facelift	57592	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59601_prefl	59601	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59601_facelift	59601	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
108635_prefl	108635	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
108635_facelift	108635	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
14414	14414	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
13161	13161	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
13162	13162	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
15725	15725	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
17515	17515	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
18769	18769	Hatchback	II	1P	5	EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	HIGH		READY
17300	17300	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
100787_prefl	100787	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
100787_facelift	100787	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
100788_prefl	100788	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
100788_facelift	100788	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
100790	100790	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
100791	100791	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
108636_prefl	108636	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
108636_facelift	108636	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
108637_prefl	108637	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
108637_facelift	108637	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
118000_prefl	118000	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
118000_facelift	118000	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
118001	118001	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH		READY
118002_prefl	118002	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
118002_facelift	118002	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
125703	125703	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH		READY
125718	125718	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH		READY
125719	125719	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH		READY
125720	125720	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH		READY
18767	18767	Hatchback	II	1P	5	EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	HIGH		READY
57594_prefl	57594	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
57594_facelift	57594	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
57597_prefl	57597	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
57597_facelift	57597	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59060_prefl	59060	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
59060_facelift	59060	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59061_prefl	59061	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-PREFL-01	HIGH	Pre-facelift exterior.	READY
59061_facelift	59061	Hatchback	III	5F	5	EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59609_prefl	59609	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59609_facelift	59609	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59610_prefl	59610	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59610_facelift	59610	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
59611_prefl	59611	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-PREFL-01	HIGH	Pre-facelift exterior.	READY
59611_facelift	59611	Coupe	III	5F	3	EU-SEAT-LEON-III-COUPE-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
143681	143681	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
157069	157069	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
18770	18770	Hatchback	II	1P	5	EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	HIGH		READY
106226_prefl	106226	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
106226_facelift	106226	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
108634_prefl	108634	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-PREFL-01	HIGH	Pre-facelift exterior.	READY
108634_facelift	108634	Wagon	III	5F	5	EU-SEAT-LEON-III-WAGON-FACELIFT17-01	HIGH	2017 facelift exterior.	READY
18768	18768	Hatchback	II	1P	5	EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	HIGH		READY
143678	143678	Hatchback	IV	KL	5	EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	HIGH		READY
144218	144218	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
15724	15724	Hatchback	I	1M	5	EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	HIGH		READY
144219	144219	Wagon	IV	KL	5	EU-SEAT-LEON-IV-WAGON-STANDARD-01	HIGH		READY
16116	16116	Hatchback	I		3	EU-SEAT-MARBELLA-I-HATCHBACK-STANDARD-01	HIGH		READY
15893	15893	Hatchback	I			EU-SEAT-MII-I-HATCHBACK-STANDARD-01	HIGH		READY
15944	15944	Hatchback	I			EU-SEAT-MII-I-HATCHBACK-STANDARD-01	HIGH		READY
57621	57621	Hatchback	I			EU-SEAT-MII-I-HATCHBACK-STANDARD-01	HIGH		READY
17498	17498	Hatchback	I		3	EU-SEAT-PANDA-I-HATCHBACK-STANDARD-01	HIGH		READY
17510	17510	Hatchback	I		5	EU-SEAT-RITMO-I-HATCHBACK-STANDARD-01	MEDIUM	Input start date predates documented SEAT production; exterior maps to Ritmo I.	READY
143551	143551	SUV	I		5	EU-SEAT-TARRACO-I-SUV-STANDARD-01	HIGH		READY
801663	801663	SUV	I		5	EU-SEAT-TARRACO-I-SUV-STANDARD-01	HIGH		READY
144223	144223	SUV	I		5	EU-SEAT-TARRACO-I-SUV-STANDARD-01	HIGH		READY
8176	8176	Wagon	I			EU-SEAT-TERRA-I-STANDARD-01	HIGH		READY
8177	8177	Van	I			EU-SEAT-TERRA-I-STANDARD-01	HIGH		READY
57522	57522	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
10046	10046	Sedan	II	1M2	4	EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	HIGH		READY
18380	18380	MPV	III	5P2	5	EU-SEAT-TOLEDO-III-MPV-STANDARD-01	HIGH		READY
59063	59063	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
117374	117374	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
128156	128156	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
128157	128157	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
57523	57523	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
57524	57524	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
115144	115144	Hatchback	IV	KG3	5	EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载 left18448_15001-15100_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_15001-15100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-LEON-III-HATCHBACK-PREFL-01	4263	1816	1459	Automobile-Catalog (2016 Seat Leon 1.4 TSI)	https://www.automobile-catalog.com/car/2016/3097175/seat_leon_1_4_tsi_125.html
EU-SEAT-LEON-III-HATCHBACK-FACELIFT17-01	4282	1816	1459	Automobile-Catalog (2017 Seat Leon 1.4 TSI)	https://www.automobile-catalog.com/car/2017/3098045/seat_leon_1_4_tsi_125.html
EU-SEAT-LEON-III-COUPE-PREFL-01	4228	1810	1446	Auto-Data (Seat Leon III SC 1.6 TDI)	https://www.auto-data.net/en/seat-leon-iii-sc-1.6-tdi-105hp-dsg-start-stop-19500
EU-SEAT-LEON-III-COUPE-FACELIFT17-01	4247	1810	1446	Automobile-Catalog (2017 Seat Leon SC 1.4 TSI)	https://www.automobile-catalog.com/car/2017/3098180/seat_leon_sc_1_4_tsi_125.html
EU-SEAT-LEON-III-WAGON-PREFL-01	4535	1816	1451	Automobile-Catalog (2016 Seat Leon ST 1.4 TSI)	https://www.automobile-catalog.com/car/2016/3097205/seat_leon_st_1_4_tsi_125.html
EU-SEAT-LEON-III-WAGON-FACELIFT17-01	4549	1816	1451	Automobile-Catalog (2017 Seat Leon ST 2.0 TDI)	https://www.automobile-catalog.com/car/2017/3098465/seat_leon_st_2_0_tdi_cr_150.html
EU-SEAT-LEON-IV-WAGON-PHEV-02	4642	1799	1456	Automobile-Catalog (2025 Seat Leon Sportstourer 1.5 e-Hybrid)	https://www.automobile-catalog.com/car/2025/3382160/seat_leon_sportstourer_1_5_e-hybrid_204.html
EU-SEAT-LEON-IV-HATCHBACK-PHEV-02	4368	1799	1460	Automobile-Catalog (2025 Seat Leon 1.5 e-Hybrid)	https://www.automobile-catalog.com/car/2025/3382145/seat_leon_1_5_e-hybrid_204.html
EU-SEAT-LEON-IV-WAGON-STANDARD-01	4642	1799	1450	Automobile-Catalog (2024 Seat Leon Sportstourer 1.5 eTSI)	https://www.automobile-catalog.com/car/2024/3099980/seat_leon_sportstourer_1_5_etsi_150_dsg.html
EU-SEAT-LEON-IV-HATCHBACK-STANDARD-01	4368	1799	1456	Automobile-Catalog (2024 Seat Leon 1.5 eTSI)	https://www.automobile-catalog.com/car/2024/3099725/seat_leon_1_5_etsi_150_dsg.html
EU-SEAT-LEON-I-HATCHBACK-STANDARD-01	4184	1742	1439	Auto-Data (Seat Leon I 1.8 20V)	https://www.auto-data.net/en/seat-leon-i-1m-1.8-20v-125hp-automatic-29349
EU-SEAT-LEON-II-HATCHBACK-STANDARD-01	4315	1768	1458	Auto-Data (Seat Leon II 2.0 TDI)	https://www.auto-data.net/en/seat-leon-ii-1p-2.0-tdi-16v-140hp-automatic-46460
EU-SEAT-MARBELLA-I-HATCHBACK-STANDARD-01	3475	1500	1445	Automobile-Catalog (1997 Seat Marbella)	https://www.automobile-catalog.com/car/1997/3065375/seat_marbella_base.html
EU-SEAT-MII-I-HATCHBACK-STANDARD-01	3557	1641	1478	Auto-Data (Seat Mii 2011-2019)	https://www.auto-data.net/en/seat-mii-model-2030
EU-SEAT-PANDA-I-HATCHBACK-STANDARD-01	3380	1460	1440	UltimateSpecs (Seat Panda 45)	https://www.ultimatespecs.com/car-specs/Seat/357/Seat-Panda-45.html
EU-SEAT-RITMO-I-HATCHBACK-STANDARD-01	3940	1650	1400	SEAT Historic Cars (Ritmo)	https://www.seatcocheshistoricos.es/SEATHistoricos/1980/ritmo.php
EU-SEAT-TARRACO-I-SUV-STANDARD-01	4735	1839	1658	Auto-Data (Seat Tarraco e-Hybrid)	https://www.auto-data.net/en/seat-tarraco-1.4-tsi-245hp-e-hybrid-dsg-42062
EU-SEAT-TERRA-I-STANDARD-01	3869	1490	1895	SEAT Historic Cars (Terra)	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1980/Terra.php
EU-SEAT-TOLEDO-IV-HATCHBACK-STANDARD-01	4482	1706	1461	Auto-Data (Seat Toledo IV 1.2 TSI)	https://www.auto-data.net/en/seat-toledo-iv-nh-1.2-tsi-105hp-start-stop-19362
EU-SEAT-TOLEDO-II-SEDAN-STANDARD-01	4439	1742	1436	Auto-Data (Seat Toledo II 1.6)	https://www.auto-data.net/en/seat-toledo-ii-1m2-1.6-100hp-13539
EU-SEAT-TOLEDO-III-MPV-STANDARD-01	4458	1768	1568	UltimateSpecs (Seat Toledo III 1.6 8V)	https://www.ultimatespecs.com/car-specs/Seat/1209/Seat-Toledo-III-16-8v.html
```

[下载 left18448_15001-15100_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_15001-15100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2016/3097175/seat_leon_1_4_tsi_125.html?utm_source=chatgpt.com "2016 Seat Leon 1.4 TSI (125) Specs Review (92 kW / ..."
[2]: https://www.automobile-catalog.com/car/2025/3382160/seat_leon_sportstourer_1_5_e-hybrid_204.html?utm_source=chatgpt.com "2025 Seat Leon Sportstourer 1.5 e-HYBRID (204) Specs ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1533 行）
- 累计尺寸组：dimension_groups_final.tsv（301 行）

