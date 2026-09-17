# 任务：left18448 第 8901-9000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0090__f3cc1935


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8901-9000 行

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
left18448 第 8901-9000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8901-9000_ktype_dimension_mapping_final.tsv
- left18448_8901-9000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MAZDA-2-I-HATCHBACK-STD-01	3925	1680	1545
EU-MAZDA-2-III-HATCHBACK-STD-01	4060	1695	1495

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mazda	2	1.6	Schrägheck	Frontantrieb	Benzin	Apr 2003	Jun 2007	17105
Mazda	2	1.3 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	Nov 2014	119035
Mazda	2	1.3 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2011	Nov 2014	119099
Mazda	2	1.3 MZR	Schrägheck	Frontantrieb	Benzin	Jan 2010	Jun 2015	54913
Mazda	2	1.4 CD	Schrägheck	Frontantrieb	Diesel	Apr 2003	Jun 2007	17318
Mazda	2	1.5 D	Schrägheck	Frontantrieb	Diesel	Jun 2015	-	108280
Mazda	2	1.5 E-skyactiv G	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2021	-	146106
Mazda	2	1.5 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2022	-	146857
Mazda	2	1.5 MZR	Schrägheck	Frontantrieb	Benzin	Jun 2011	Jun 2015	54912
Mazda	2	1.5 Skyactiv-g	Schrägheck	Frontantrieb	Benzin	Aug 2014	-	108282
Mazda	2	1.5 Skyactiv-g	Schrägheck	Frontantrieb	Benzin	Aug 2014	-	109547
Mazda	2	1.6 Mz-cd	Schrägheck	Frontantrieb	Diesel	Jun 2011	Jun 2015	54910
Mazda	3	1.3	Schrägheck	Frontantrieb	Benzin	Oct 2003	Jun 2009	18099
Mazda	3	1.5	Stufenheck	Frontantrieb	Benzin	Oct 2014	May 2019	108445
Mazda	3	1.5	Stufenheck	Frontantrieb	Benzin	Oct 2013	May 2019	111907
Mazda	3	1.6	Schrägheck	Frontantrieb	Benzin	Oct 2003	Jun 2009	17669
Mazda	3	1.6	Stufenheck	Frontantrieb	Benzin	Feb 2004	Jun 2009	17671
Mazda	3	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2013	May 2019	111906
Mazda	3	1.6	Schrägheck	Frontantrieb	Benzin	Sep 2013	May 2019	111911
Mazda	3	2	Schrägheck	Frontantrieb	Benzin	Oct 2003	Dec 2009	17670
Mazda	3	2	Stufenheck	Frontantrieb	Benzin	Oct 2003	Dec 2009	17672
Mazda	3	2	Stufenheck	Frontantrieb	Benzin	Nov 2014	May 2019	108289
Mazda	3	2	Schrägheck	Frontantrieb	Benzin	Nov 2013	May 2016	111915
Mazda	3	1.5 D	Schrägheck	Frontantrieb	Diesel	Feb 2016	May 2019	118542
Mazda	3	1.5 D	Stufenheck	Frontantrieb	Diesel	Jun 2016	May 2019	118543
Mazda	3	1.6 DI Turbo	Stufenheck	Frontantrieb	Diesel	Jun 2004	Jun 2009	17875
Mazda	3	1.6 DI Turbo	Schrägheck	Frontantrieb	Diesel	Jun 2004	Jun 2009	17876
Mazda	3	1.6 Mz-cd	Schrägheck	Frontantrieb	Diesel	Jun 2006	Dec 2009	107549
Mazda	3	1.6 MZR CD	Stufenheck	Frontantrieb	Diesel	Sep 2010	May 2013	6538
Mazda	3	1.6 MZR CD	Schrägheck	Frontantrieb	Diesel	Sep 2010	May 2013	6612
Mazda	3	1.6 MZR CD	Stufenheck	Frontantrieb	Diesel	Dec 2008	May 2013	58605
Mazda	3	2.0 AWD	Stufenheck	Allrad	Benzin	May 2019	-	800387
Mazda	3	2.0 Skyactiv-x M Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Feb 2021	-	144530
Mazda	3	2.5 E-skyactiv-g	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	800085
Mazda	3	2.5 E-skyactiv-g	Stufenheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	800086
Mazda	3	Skyactiv-x M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2021	-	144528
Mazda	3	Skyactiv-x M Hybrid AWD	Schrägheck	Allrad	Benzin/Elektro	Feb 2021	-	144529
Mazda	5	1.8	Großraumlimousine	Frontantrieb	Benzin	Feb 2005	May 2010	18541
Mazda	5	2	Großraumlimousine	Frontantrieb	Benzin	Jun 2010	-	12477
Mazda	5	2	Großraumlimousine	Frontantrieb	Benzin	Feb 2005	May 2010	18543
Mazda	5	1.8 MZR	Großraumlimousine	Frontantrieb	Benzin	Sep 2010	-	58902
Mazda	5	2.0 CD	Großraumlimousine	Frontantrieb	Diesel	Feb 2005	May 2010	18545
Mazda	5	2.0 CD	Großraumlimousine	Frontantrieb	Diesel	Feb 2005	May 2010	18830
Mazda	6	1.8	Schrägheck	Frontantrieb	Benzin	Aug 2002	Aug 2007	16680
Mazda	6	1.8	Stufenheck	Frontantrieb	Benzin	Aug 2002	Aug 2007	16684
Mazda	6	1.8	Kombi	Frontantrieb	Benzin	Aug 2002	Aug 2007	16688
Mazda	6	2	Schrägheck	Frontantrieb	Benzin	Aug 2002	Aug 2007	16681
Mazda	6	2	Stufenheck	Frontantrieb	Benzin	Jun 2002	Aug 2007	16685
Mazda	6	2	Kombi	Frontantrieb	Benzin	Aug 2002	Aug 2007	16689
Mazda	6	2	Schrägheck	Frontantrieb	Benzin	Mar 2005	Aug 2007	19107
Mazda	6	2	Stufenheck	Frontantrieb	Benzin	Mar 2005	Aug 2007	19108
Mazda	6	2	Kombi	Frontantrieb	Benzin	Mar 2005	Aug 2007	19109
Mazda	6	2	Stufenheck	Frontantrieb	Benzin	Jan 2013	-	58504
Mazda	6	2	Stufenheck	Frontantrieb	Benzin	Jan 2013	-	58507
Mazda	6	2	Kombi	Frontantrieb	Benzin	Jan 2013	-	58538
Mazda	6	2	Kombi	Frontantrieb	Benzin	Jan 2013	-	58542
Mazda	6	2.3	Schrägheck	Frontantrieb	Benzin	Aug 2002	Aug 2007	16682
Mazda	6	2.3	Stufenheck	Frontantrieb	Benzin	Jun 2002	Aug 2007	16686
Mazda	6	2.3	Kombi	Frontantrieb	Benzin	Jan 2002	Feb 2008	16690
Mazda	6	2.5	Stufenheck	Frontantrieb	Benzin	Jan 2013	-	58508
Mazda	6	2.5	Kombi	Frontantrieb	Benzin	Dec 2012	-	59414
Mazda	6	2.0 DI	Schrägheck	Frontantrieb	Diesel	Aug 2002	Aug 2007	16683
Mazda	6	2.0 DI	Stufenheck	Frontantrieb	Diesel	Jun 2002	Aug 2007	16687
Mazda	6	2.0 DI	Kombi	Frontantrieb	Diesel	Aug 2002	Feb 2005	16691
Mazda	6	2.0 DI	Schrägheck	Frontantrieb	Diesel	Aug 2002	Aug 2007	16844
Mazda	6	2.0 DI	Kombi	Frontantrieb	Diesel	Aug 2002	Aug 2007	16864
Mazda	6	2.0 DI	Stufenheck	Frontantrieb	Diesel	Aug 2002	Aug 2007	16865
Mazda	6	2.0 DI	Schrägheck	Frontantrieb	Diesel	Jun 2005	Aug 2007	18827
Mazda	6	2.0 DI	Stufenheck	Frontantrieb	Diesel	Jun 2005	Aug 2007	18828
Mazda	6	2.0 DI	Kombi	Frontantrieb	Diesel	Jun 2005	Aug 2007	18829
Mazda	6	2.0 MZR	Stufenheck	Frontantrieb	Benzin	Jan 2010	Dec 2012	34860
Mazda	6	2.2 D	Stufenheck	Frontantrieb	Diesel	Jan 2010	Dec 2012	34861
Mazda	6	2.2 D	Stufenheck	Frontantrieb	Diesel	Jan 2010	Jul 2013	34862
Mazda	6	2.2 D	Stufenheck	Frontantrieb	Diesel	Dec 2012	-	57598
Mazda	6	2.2 D	Kombi	Frontantrieb	Diesel	Aug 2012	Feb 2018	57607
Mazda	6	2.2 D	Stufenheck	Frontantrieb	Diesel	Dec 2012	Nov 2020	58509
Mazda	6	2.2 D	Kombi	Frontantrieb	Diesel	Oct 2012	Dec 2020	59412
Mazda	6	2.2 D 4WD	Stufenheck	Allrad	Diesel	Jul 2014	-	111842
Mazda	6	2.2 D AWD	Kombi	Allrad	Diesel	Feb 2015	-	111366
Mazda	6	2.2 D AWD	Kombi	Allrad	Diesel	Dec 2012	Dec 2020	111890
Mazda	6	2.3 AWD	Kombi	Allrad	Benzin	Nov 2002	Aug 2007	17160
Mazda	616	1.6	Stufenheck	Heckantrieb	Benzin	Jun 1973	Feb 1978	10799
Mazda	818	1.3	Kombi	Heckantrieb	Benzin	Jan 1974	Oct 1978	10800
Mazda	818	1.3	Coupe	Heckantrieb	Benzin	Oct 1972	Dec 1978	125898
Mazda	818	1.6	Kombi	Heckantrieb	Benzin	Jan 1977	Oct 1978	10801
Mazda	1000	1	Stufenheck	Heckantrieb	Benzin	Jan 1975	Jan 1977	10794
Mazda	1300	1.3	Stufenheck	Heckantrieb	Benzin	Feb 1971	Jan 1977	10795
Mazda	1300	1.3	Stufenheck	Heckantrieb	Benzin	Jan 1975	Jan 1977	118687
Mazda	1800	1.8	Stufenheck	Heckantrieb	Benzin	Oct 1968	Mar 1973	151025
Mazda	323 c iv	1.3 16V	Schrägheck	Frontantrieb	Benzin	Sep 1989	Jul 1994	8796
Mazda	323 c iv	1.8 16V	Schrägheck	Frontantrieb	Benzin	Sep 1989	Mar 1993	18838
Mazda	323 f iv	1.8 16V	Schrägheck	Frontantrieb	Benzin	Sep 1989	Mar 1993	18861
Mazda	323 f vi	1.4	Schrägheck	Frontantrieb	Benzin	Jan 2001	May 2004	15789
Mazda	323 f vi	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2001	May 2004	15790
Mazda	323 f vi	1.6	Schrägheck	Frontantrieb	Benzin	Jan 2001	May 2004	15791
Mazda	323 f vi	2	Schrägheck	Frontantrieb	Benzin	Jan 2001	May 2004	15792
Mazda	323 f vi	2.0 TD	Schrägheck	Frontantrieb	Diesel	Jan 2001	May 2004	15793
Mazda	323 i station wagon	1.3	Kombi	Heckantrieb	Benzin	May 1978	May 1986	10796
Mazda	323 ii	1.1	Stufenheck	Frontantrieb	Benzin	Nov 1980	Oct 1985	14072
Mazda	323 ii	1.5	Stufenheck	Frontantrieb	Benzin	May 1981	Dec 1985	14071


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓完成聚类，动力、能源、驱动和普通配置版本均复用相同尺寸组。
* 复用累计尺寸组 `EU-MAZDA-2-I-HATCHBACK-STD-01` 和 `EU-MAZDA-2-III-HATCHBACK-STD-01`，未改写已([汽车数据网][1])
* Ktype `118542` 有对应 1.5D 改款前后完整尺寸证据，且三维由 `4460×1795×1450` 变为 `4470×1795×1465`，因此保留 `_prefl`、`_facelift` 两个物理分支；其余跨改款日期的 Ktype 未作推测性拆分。 ([auto-data.net][2])([汽车数据网][2])h10
* 已完成固定表头、唯一 ID、Ktype 覆盖、尺寸组引用闭合、正整数三维、来源与文件链接检查。

## 进度

* 输入 Ktype：100
* 已覆盖 Ktype：100
* 最终映射行：101
* 最终尺寸组：35
* PENDING：0
* IterationStatus：全部 `READY`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17105	17105	Hatchback	I	DY	5	EU-MAZDA-2-I-HATCHBACK-STD-01	HIGH		READY
119035	119035	Hatchback	II	DE	5	EU-MAZDA-2-II-HATCHBACK-STD-01	HIGH		READY
119099	119099	Hatchback	II	DE	5	EU-MAZDA-2-II-HATCHBACK-STD-01	HIGH		READY
54913	54913	Hatchback	II	DE	5	EU-MAZDA-2-II-HATCHBACK-STD-01	HIGH		READY
17318	17318	Hatchback	I	DY	5	EU-MAZDA-2-I-HATCHBACK-STD-01	HIGH		READY
108280	108280	Hatchback	III	DJ	5	EU-MAZDA-2-III-HATCHBACK-STD-01	HIGH		READY
146106	146106	Hatchback	III	DJ	5	EU-MAZDA-2-III-HATCHBACK-STD-01	HIGH		READY
146857	146857	Hatchback	IV	XP21	5	EU-MAZDA-2-IV-HATCHBACK-STD-01	HIGH		READY
54912	54912	Hatchback	II	DE	5	EU-MAZDA-2-II-HATCHBACK-STD-01	HIGH		READY
108282	108282	Hatchback	III	DJ	5	EU-MAZDA-2-III-HATCHBACK-STD-01	HIGH		READY
109547	109547	Hatchback	III	DJ	5	EU-MAZDA-2-III-HATCHBACK-STD-01	HIGH		READY
54910	54910	Hatchback	II	DE	5	EU-MAZDA-2-II-HATCHBACK-STD-01	HIGH		READY
18099	18099	Hatchback	I	BK	5	EU-MAZDA-3-I-HATCHBACK-STD-01	HIGH		READY
108445	108445	Sedan	III	BM	4	EU-MAZDA-3-III-SEDAN-STD-01	HIGH		READY
111907	111907	Sedan	III	BM	4	EU-MAZDA-3-III-SEDAN-STD-01	HIGH		READY
17669	17669	Hatchback	I	BK	5	EU-MAZDA-3-I-HATCHBACK-STD-01	HIGH		READY
17671	17671	Sedan	I	BK	4	EU-MAZDA-3-I-SEDAN-STD-01	HIGH		READY
111906	111906	Sedan	III	BM	4	EU-MAZDA-3-III-SEDAN-STD-01	HIGH		READY
111911	111911	Hatchback	III	BM	5	EU-MAZDA-3-III-HATCHBACK-PREFL-01	HIGH		READY
17670	17670	Hatchback	I	BK	5	EU-MAZDA-3-I-HATCHBACK-STD-01	HIGH		READY
17672	17672	Sedan	I	BK	4	EU-MAZDA-3-I-SEDAN-STD-01	HIGH		READY
108289	108289	Sedan	III	BM	4	EU-MAZDA-3-III-SEDAN-STD-01	HIGH		READY
111915	111915	Hatchback	III	BM	5	EU-MAZDA-3-III-HATCHBACK-PREFL-01	HIGH		READY
118542_prefl	118542	Hatchback	III	BM	5	EU-MAZDA-3-III-HATCHBACK-PREFL-01	HIGH	1.5D Ktype spans verified 2016 pre-facelift body.	READY
118542_facelift	118542	Hatchback	III	BM	5	EU-MAZDA-3-III-HATCHBACK-FACELIFT-01	HIGH	1.5D Ktype spans verified 2017 facelift body with changed dimensions.	READY
118543	118543	Sedan	III	BM	4	EU-MAZDA-3-III-SEDAN-STD-01	HIGH		READY
17875	17875	Sedan	I	BK	4	EU-MAZDA-3-I-SEDAN-STD-01	HIGH		READY
17876	17876	Hatchback	I	BK	5	EU-MAZDA-3-I-HATCHBACK-STD-01	HIGH		READY
107549	107549	Hatchback	I	BK	5	EU-MAZDA-3-I-HATCHBACK-STD-01	HIGH		READY
6538	6538	Sedan	II	BL	4	EU-MAZDA-3-II-SEDAN-STD-01	HIGH		READY
6612	6612	Hatchback	II	BL	5	EU-MAZDA-3-II-HATCHBACK-STD-01	HIGH		READY
58605	58605	Sedan	II	BL	4	EU-MAZDA-3-II-SEDAN-STD-01	HIGH		READY
800387	800387	Sedan	IV	BP	4	EU-MAZDA-3-IV-SEDAN-STD-01	HIGH		READY
144530	144530	Sedan	IV	BP	4	EU-MAZDA-3-IV-SEDAN-STD-01	HIGH		READY
800085	800085	Hatchback	IV	BP	5	EU-MAZDA-3-IV-HATCHBACK-STD-01	HIGH		READY
800086	800086	Sedan	IV	BP	4	EU-MAZDA-3-IV-SEDAN-STD-01	HIGH		READY
144528	144528	Hatchback	IV	BP	5	EU-MAZDA-3-IV-HATCHBACK-STD-01	HIGH		READY
144529	144529	Hatchback	IV	BP	5	EU-MAZDA-3-IV-HATCHBACK-STD-01	HIGH		READY
18541	18541	MPV	I	CR	5	EU-MAZDA-5-I-MPV-STD-01	HIGH		READY
12477	12477	MPV	II	CW	5	EU-MAZDA-5-II-MPV-STD-01	HIGH		READY
18543	18543	MPV	I	CR	5	EU-MAZDA-5-I-MPV-STD-01	HIGH		READY
58902	58902	MPV	II	CW	5	EU-MAZDA-5-II-MPV-STD-01	HIGH		READY
18545	18545	MPV	I	CR	5	EU-MAZDA-5-I-MPV-STD-01	HIGH		READY
18830	18830	MPV	I	CR	5	EU-MAZDA-5-I-MPV-STD-01	HIGH		READY
16680	16680	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-PREFL-01	HIGH		READY
16684	16684	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-PREFL-01	HIGH		READY
16688	16688	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
16681	16681	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-PREFL-01	HIGH		READY
16685	16685	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-PREFL-01	HIGH		READY
16689	16689	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
19107	19107	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-FACELIFT-01	HIGH		READY
19108	19108	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-FACELIFT-01	HIGH		READY
19109	19109	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-FACELIFT-01	HIGH		READY
58504	58504	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
58507	58507	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
58538	58538	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
58542	58542	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
16682	16682	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-PREFL-01	HIGH		READY
16686	16686	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-PREFL-01	HIGH		READY
16690	16690	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
58508	58508	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
59414	59414	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
16683	16683	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-PREFL-01	HIGH		READY
16687	16687	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-PREFL-01	HIGH		READY
16691	16691	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
16844	16844	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-PREFL-01	HIGH		READY
16864	16864	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
16865	16865	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-PREFL-01	HIGH		READY
18827	18827	Hatchback	I	GG	5	EU-MAZDA-6-I-HATCHBACK-FACELIFT-01	HIGH		READY
18828	18828	Sedan	I	GG	4	EU-MAZDA-6-I-SEDAN-FACELIFT-01	HIGH		READY
18829	18829	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-FACELIFT-01	HIGH		READY
34860	34860	Sedan	II	GH	4	EU-MAZDA-6-II-SEDAN-STD-01	HIGH		READY
34861	34861	Sedan	II	GH	4	EU-MAZDA-6-II-SEDAN-STD-01	HIGH		READY
34862	34862	Sedan	II	GH	4	EU-MAZDA-6-II-SEDAN-STD-01	HIGH		READY
57598	57598	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
57607	57607	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
58509	58509	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
59412	59412	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
111842	111842	Sedan	III	GJ	4	EU-MAZDA-6-III-SEDAN-STD-01	HIGH		READY
111366	111366	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
111890	111890	Wagon	III	GJ	5	EU-MAZDA-6-III-WAGON-STD-01	HIGH		READY
17160	17160	Wagon	I	GY	5	EU-MAZDA-6-I-WAGON-PREFL-01	HIGH		READY
10799	10799	Sedan	I		4	EU-MAZDA-616-I-SEDAN-STD-01	MEDIUM		READY
10800	10800	Wagon	I		5	EU-MAZDA-818-I-WAGON-STD-01	MEDIUM		READY
125898	125898	Coupe	I		2	EU-MAZDA-818-I-COUPE-STD-01	MEDIUM		READY
10801	10801	Wagon	I		5	EU-MAZDA-818-I-WAGON-STD-01	MEDIUM		READY
10794	10794	Sedan	I		4	EU-MAZDA-1000-I-SEDAN-STD-01	MEDIUM		READY
10795	10795	Sedan	I		4	EU-MAZDA-1300-I-SEDAN-STD-01	MEDIUM		READY
118687	118687	Sedan	I		4	EU-MAZDA-1300-I-SEDAN-STD-01	MEDIUM		READY
151025	151025	Sedan	I		4	EU-MAZDA-1800-I-SEDAN-STD-01	MEDIUM		READY
8796	8796	Hatchback	IV	BG	3	EU-MAZDA-323-IV-HATCHBACK-3DR-01	HIGH		READY
18838	18838	Hatchback	IV	BG	3	EU-MAZDA-323-IV-HATCHBACK-3DR-01	HIGH		READY
18861	18861	Hatchback	IV	BG	5	EU-MAZDA-323-IV-HATCHBACK-5DR-01	HIGH		READY
15789	15789	Hatchback	VI	BJ	5	EU-MAZDA-323-VI-HATCHBACK-STD-01	HIGH		READY
15790	15790	Hatchback	VI	BJ	5	EU-MAZDA-323-VI-HATCHBACK-STD-01	HIGH		READY
15791	15791	Hatchback	VI	BJ	5	EU-MAZDA-323-VI-HATCHBACK-STD-01	HIGH		READY
15792	15792	Hatchback	VI	BJ	5	EU-MAZDA-323-VI-HATCHBACK-STD-01	HIGH		READY
15793	15793	Hatchback	VI	BJ	5	EU-MAZDA-323-VI-HATCHBACK-STD-01	HIGH		READY
10796	10796	Wagon	I	FA	5	EU-MAZDA-323-I-WAGON-STD-01	MEDIUM		READY
14072	14072	Sedan	II	BD	4	EU-MAZDA-323-II-SEDAN-STD-01	HIGH		READY
14071	14071	Sedan	II	BD	4	EU-MAZDA-323-II-SEDAN-STD-01	HIGH		READY
```

[下载 left18448_8901-9000_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_8901-9000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-2-I-HATCHBACK-STD-01	3925	1680	1545	Auto-Data.net	https://www.auto-data.net/en/mazda-2-i-dy-generation-2426
EU-MAZDA-2-II-HATCHBACK-STD-01	3920	1695	1475	Auto-Data.net	https://www.auto-data.net/en/mazda-2-ii-de-facelift-2010-1.3i-84hp-17494
EU-MAZDA-2-III-HATCHBACK-STD-01	4060	1695	1495	Auto-Data.net	https://www.auto-data.net/en/mazda-2-iii-dj-generation-4559
EU-MAZDA-2-IV-HATCHBACK-STD-01	3940	1745	1500	Auto-Data.net	https://www.auto-data.net/en/mazda-2-iv-xp21-1.5-116hp-hybrid-cvt-45447
EU-MAZDA-3-I-HATCHBACK-STD-01	4420	1755	1465	Auto-Data.net	https://www.auto-data.net/en/mazda-3-i-hatchback-bk-1.6i-105hp-11477
EU-MAZDA-3-III-SEDAN-STD-01	4580	1795	1455	Auto-Data.net	https://www.auto-data.net/en/mazda-3-iii-sedan-bm-2.0-skyactiv-g-120hp-22024
EU-MAZDA-3-I-SEDAN-STD-01	4490	1755	1465	Auto-Data.net	https://www.auto-data.net/en/mazda-3-i-sedan-bk-1.6i-105hp-automatic-31196
EU-MAZDA-3-III-HATCHBACK-PREFL-01	4460	1795	1450	Auto-Data.net	https://www.auto-data.net/en/mazda-3-iii-hatchback-bm-1.5-skyactiv-g-100hp-22023
EU-MAZDA-3-III-HATCHBACK-FACELIFT-01	4470	1795	1465	Auto-Data.net	https://www.auto-data.net/en/mazda-3-iii-hatchback-bm-facelift-2017-1.5-skyactiv-d-105hp-28173
EU-MAZDA-3-II-SEDAN-STD-01	4580	1755	1470	Auto-Data.net	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-1.6-cd-109hp-31204
EU-MAZDA-3-II-HATCHBACK-STD-01	4460	1755	1470	Auto-Data.net	https://www.auto-data.net/en/mazda-3-ii-hatchback-bl-facelift-2011-1.6i-105hp-17501
EU-MAZDA-3-IV-SEDAN-STD-01	4660	1795	1440	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mazda/135526/Mazda-3-%28BP%29-Sedan-20-e-SkyActiv-X-186.html
EU-MAZDA-3-IV-HATCHBACK-STD-01	4460	1795	1440	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mazda/125644/Mazda-3-%28BP%29-20-e-SkyActiv-X-186.html
EU-MAZDA-5-I-MPV-STD-01	4505	1755	1615	Auto-Data.net	https://www.auto-data.net/en/mazda-5-i-2.0-cd-110hp-11071
EU-MAZDA-5-II-MPV-STD-01	4585	1750	1615	Auto-Data.net	https://www.auto-data.net/en/mazda-5-ii-1.6-cd-115hp-17508
EU-MAZDA-6-I-HATCHBACK-PREFL-01	4680	1780	1435	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-hatchback-typ-gg-gy-gg1-1.8-120hp-31720
EU-MAZDA-6-I-SEDAN-PREFL-01	4680	1780	1435	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-sedan-typ-gg-gy-gg1-1.8-120hp-31716
EU-MAZDA-6-I-WAGON-PREFL-01	4700	1780	1480	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-combi-typ-gg-gy-gg1-1.8-120hp-31722
EU-MAZDA-6-I-HATCHBACK-FACELIFT-01	4690	1780	1435	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-hatchback-typ-gg-gy-gg1-facelift-2005-2.0-147hp-31951
EU-MAZDA-6-I-SEDAN-FACELIFT-01	4690	1780	1435	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-sedan-typ-gg-gy-gg1-facelift-2005-2.0-147hp-31727
EU-MAZDA-6-I-WAGON-FACELIFT-01	4710	1780	1480	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-combi-typ-gg-gy-gg1-facelift-2005-2.0-cd-143hp-30794
EU-MAZDA-6-III-SEDAN-STD-01	4865	1840	1450	Auto-Data.net	https://www.auto-data.net/en/mazda-6-iii-sedan-gj-2.0-skyactiv-g-165hp-i-eloop-18090
EU-MAZDA-6-III-WAGON-STD-01	4800	1840	1480	Auto-Data.net	https://www.auto-data.net/en/mazda-6-iii-sport-combi-gj-2.0-skyactiv-g-165hp-i-eloop-18293
EU-MAZDA-6-II-SEDAN-STD-01	4755	1795	1440	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-sedan-gh-facelift-2010-2.0-155hp-16773
EU-MAZDA-616-I-SEDAN-STD-01	4140	1575	1422	Drive.Place	https://mazda.drive.place/616/i/group_sedan/132916
EU-MAZDA-818-I-WAGON-STD-01	4095	1595	1405	CarsGuide	https://www.carsguide.com.au/mazda/808/1972
EU-MAZDA-818-I-COUPE-STD-01	4075	1595	1355	CarsGuide	https://www.carsguide.com.au/mazda/808/1972
EU-MAZDA-1000-I-SEDAN-STD-01	3855	1540	1385	Auto-Data.net	https://www.auto-data.net/en/mazda-1000-1.0-45hp-11059
EU-MAZDA-1300-I-SEDAN-STD-01	3855	1540	1380	CarsGuide	https://www.carsguide.com.au/mazda/1300/car-dimensions/1971
EU-MAZDA-1800-I-SEDAN-STD-01	4375	1632	1429	Carfolio	https://www.carfolio.com/mazda-1800-sva-62051
EU-MAZDA-323-IV-HATCHBACK-3DR-01	3996	1675	1379	Auto-Data.net	https://www.auto-data.net/en/mazda-323-c-iv-bg-1.3-16v-73hp-11168
EU-MAZDA-323-IV-HATCHBACK-5DR-01	4260	1680	1340	Auto-Data.net	https://www.auto-data.net/en/mazda-323-f-iv-bg-1.6-84hp-11176
EU-MAZDA-323-VI-HATCHBACK-STD-01	4200	1705	1410	Auto-Data.net	https://www.auto-data.net/en/mazda-323-f-vi-bj-1.5-i-16v-88hp-11136
EU-MAZDA-323-I-WAGON-STD-01	4010	1605	1425	CarsGuide	https://www.carsguide.com.au/mazda/323/car-dimensions/1978
EU-MAZDA-323-II-SEDAN-STD-01	3955	1630	1375	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mazda/547/Mazda-323-II-1100.html
```

[下载 left18448_8901-9000_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_8901-9000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/mazda-2-i-dy-generation-2426?utm_source=chatgpt.com "Mazda 2 I (DY) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mazda-3-iii-hatchback-bm-1.5-skyactiv-g-100hp-22023?utm_source=chatgpt.com "Mazda 3 III Hatchback (BM) 1.5 SkyActiv-G (100 Hp)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6582 行）
- 累计尺寸组：dimension_groups_final.tsv（1898 行）

