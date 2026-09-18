# 任务：left18448 第 4601-4700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0047__e0cbf046


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4601-4700 行

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
left18448 第 4601-4700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4601-4700_ktype_dimension_mapping_final.tsv
- left18448_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Faam	Jolly 2000	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2010	Dec 2012	801735
Faam	Smile	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2010	Dec 2011	801734
Farizon Auto	Supervan	EV	Kasten	Frontantrieb	Elektro	Dec 2024	-	160238
Farizon Auto	Supervan	EV	Kasten	Frontantrieb	Elektro	Feb 2025	-	160720
Farizon Auto	V6e	EV	Kasten	Heckantrieb	Elektro	Feb 2025	-	801885
Feidi	3mx	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Oct 2024	-	160182
Feidi	Enter	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Nov 2024	-	153995
Feidi	Enter	EV	Kasten	Heckantrieb	Elektro	Nov 2024	-	801131
Fengon	Glory 600	1.5 GDI	SUV	Frontantrieb	Benzin	Apr 2024	-	159722
Ferrari	12	V12	Coupe	Heckantrieb	Benzin	Mar 2024	-	159234
Ferrari	12	V12	Cabriolet	Heckantrieb	Benzin	Mar 2024	-	159235
Ferrari	360	3.6	Cabriolet	Heckantrieb	Benzin	Feb 2000	Aug 2005	14683
Ferrari	360	3.6 Challenge	Coupe	Heckantrieb	Benzin	May 2001	Mar 2005	54923
Ferrari	360	3.6 Challenge Stradale	Coupe	Heckantrieb	Benzin	May 2003	Mar 2005	17343
Ferrari	360	3.6 Modena	Coupe	Heckantrieb	Benzin	Mar 1999	Mar 2005	11979
Ferrari	360	3.6 Modena	Coupe	Heckantrieb	Benzin	Jan 2002	Mar 2005	56106
Ferrari	400	S I	Coupe	Heckantrieb	Benzin	Jan 1959	Dec 1964	144609
Ferrari	400	S I	Cabriolet	Heckantrieb	Benzin	Jan 1959	Dec 1964	144611
Ferrari	400	S II	Coupe	Heckantrieb	Benzin	Jan 1961	Dec 1964	144610
Ferrari	400	S II	Cabriolet	Heckantrieb	Benzin	Jan 1961	Dec 1964	144612
Ferrari	458	4.5	Cabriolet	Heckantrieb	Benzin	Sep 2011	-	18619
Ferrari	458	4.5	Coupe	Heckantrieb	Benzin	Sep 2013	-	100096
Ferrari	458	4.5	Coupe	Heckantrieb	Benzin	Sep 2013	-	101035
Ferrari	458	4.5	Cabriolet	Heckantrieb	Benzin	Dec 2014	-	108936
Ferrari	458	4.5	Cabriolet	Heckantrieb	Benzin	Sep 2014	-	110605
Ferrari	208/308	2.0 208 GTB	Coupe	Heckantrieb	Benzin	Jan 1980	Jul 1982	108191
Ferrari	208/308	2.9 308 GTS	Targa	Heckantrieb	Benzin	Jun 1976	Sep 1979	150403
Ferrari	208/308	308 Gtbi	Coupe	Heckantrieb	Benzin	Oct 1980	Dec 1982	127271
Ferrari	208/308	308 Gtsi	Targa	Heckantrieb	Benzin	Oct 1980	Dec 1982	127270
Ferrari	275 gtb	3.3	Coupe	Heckantrieb	Benzin	Sep 1963	Sep 1965	144563
Ferrari	275 gts	3.3	Cabriolet	Heckantrieb	Benzin	Jan 1964	Dec 1966	144654
Ferrari	296 gtb	Phev	Coupe	Heckantrieb	Benzin/Elektro	Oct 2021	-	145695
Ferrari	296 gtb	Speciale	Coupe	Heckantrieb	Benzin/Elektro	Jul 2025	-	802251
Ferrari	296 gts	Phev	Cabriolet	Heckantrieb	Benzin/Elektro	Oct 2021	-	147821
Ferrari	488 gtb	3.9	Coupe	Heckantrieb	Benzin	Apr 2015	-	113142
Ferrari	488 spider	3.9	Cabriolet	Heckantrieb	Benzin	Oct 2015	-	117780
Ferrari	5__ maranello	550	Coupe	Heckantrieb	Benzin	Apr 1996	Dec 2001	5732
Ferrari	5__ maranello	550	Coupe	Heckantrieb	Benzin	Sep 1998	Dec 2002	105963
Ferrari	5__ maranello	575 M	Coupe	Heckantrieb	Benzin	Apr 2002	Dec 2006	16656
Ferrari	550 barchetta	5.5	Cabriolet	Heckantrieb	Benzin	Oct 2000	Jan 2005	15497
Ferrari	599 gtb/gto	6.0 GTO	Coupe	Heckantrieb	Benzin	Apr 2010	-	14622
Ferrari	599 gtb/gto	6.0 GTO	Coupe	Heckantrieb	Benzin	Apr 2010	-	54917
Ferrari	599 sa	6	Cabriolet	Heckantrieb	Benzin	Sep 2010	-	52956
Ferrari	612 scaglietti	5.7	Coupe	Heckantrieb	Benzin	Apr 2004	Jun 2011	17853
Ferrari	812 superfast	6.5	Coupe	Heckantrieb	Benzin	Mar 2017	-	128158
Ferrari	812 superfast	Competizione	Coupe	Heckantrieb	Benzin	May 2021	-	145257
Ferrari	812 superfast	Competizione A	Targa	Heckantrieb	Benzin	Jul 2021	-	152629
Ferrari	849 testarossa	Hybrid	Coupe	Allrad	Benzin/Elektro	Mar 2026	-	162576
Ferrari	849 testarossa spider	Hybrid	Cabriolet	Allrad	Benzin/Elektro	Mar 2026	-	162577
Ferrari	Amalfi	3.9	Coupe	Heckantrieb	Benzin	Jan 2026	-	162205
Ferrari	California	3.9 T	Cabriolet	Heckantrieb	Benzin	Jun 2014	-	106306
Ferrari	Daytona sp3	V12	Targa	Heckantrieb	Benzin	Dec 2022	-	154851
Ferrari	Enzo ferrari	6	Coupe	Heckantrieb	Benzin	Oct 2002	Dec 2003	18065
Ferrari	F12 berlinetta	6.3	Coupe	Heckantrieb	Benzin	Oct 2012	-	56039
Ferrari	F12 berlinetta	6.3 TDF	Coupe	Heckantrieb	Benzin	Nov 2015	-	117781
Ferrari	F355 gts	3.5	Targa	Heckantrieb	Benzin	Jul 1994	Mar 1999	123772
Ferrari	F430	4.3 F430	Cabriolet	Heckantrieb	Benzin	May 2005	Dec 2009	18525
Ferrari	F430	F430	Coupe	Heckantrieb	Benzin	Mar 2005	Dec 2009	18306
Ferrari	F430	Scuderia 16M	Cabriolet	Heckantrieb	Benzin	Sep 2007	Dec 2009	10328
Ferrari	F80	3.0 Dual Mild Hybrid	Coupe	Allrad	Benzin/Elektro	Oct 2024	-	159820
Ferrari	Ff	6.3	Coupe	Allrad	Benzin	Jun 2011	Feb 2016	19058
Ferrari	Ff	6.3	Coupe	Allrad	Benzin	Jun 2011	Dec 2016	58475
Ferrari	Gtc4 lusso / t	6.3	Coupe	Allrad	Benzin	Apr 2016	-	119787
Ferrari	Gtc4 lusso / t	3.9 T	Coupe	Heckantrieb	Benzin	Oct 2016	-	124998
Ferrari	Laferrari	6.3 Hybrid	Coupe	Heckantrieb	Benzin/Elektro	Jun 2013	Dec 2015	113735
Ferrari	Mondial	3	Cabriolet	Heckantrieb	Benzin	May 1986	Sep 1987	127274
Ferrari	Mondial	3	Coupe	Heckantrieb	Benzin	May 1986	Sep 1987	127275
Ferrari	Portofino	3.9	Cabriolet	Heckantrieb	Benzin	Feb 2021	-	143610
Ferrari	Purosangue fuv	V12 Allrad	SUV	Allrad	Benzin	Oct 2022	-	150755
Ferrari	Roma	3.9	Cabriolet	Heckantrieb	Benzin	Apr 2023	-	154561
Ferrari	Sf90	Spider Phev 4WD	Cabriolet	Allrad	Benzin/Elektro	Mar 2021	-	144791
Ferrari	Sf90	XX Spider Phev 4WD	Cabriolet	Allrad	Benzin/Elektro	Jul 2023	-	156425
Ferrari	Sf90	XX Stradale Phev 4WD	Coupe	Allrad	Benzin/Elektro	Jul 2023	-	156042
Fest	E-Box m	Electric	Kasten	Heckantrieb	Elektro	Aug 2023	-	156206
Fiat	124	1200	Stufenheck	Heckantrieb	Benzin	Jul 1966	Oct 1973	6001
Fiat	124	1200	Kombi	Heckantrieb	Benzin	May 1973	Mar 1975	14418
Fiat	124	1600	Cabriolet	Heckantrieb	Benzin	Jan 1973	Jul 1975	116153
Fiat	124	1600	Coupe	Heckantrieb	Benzin	Jan 1973	Feb 1976	116421
Fiat	124	1600 Sport	Cabriolet	Heckantrieb	Benzin	Nov 1969	Aug 1973	14419
Fiat	124	1600 Sport	Coupe	Heckantrieb	Benzin	Aug 1972	Feb 1976	14420
Fiat	124	1600 Sport	Coupe	Heckantrieb	Benzin	Aug 1972	Dec 1975	14603
Fiat	124	1600 Sport	Cabriolet	Heckantrieb	Benzin	Jan 1969	Dec 1974	14605
Fiat	124	1800 Sport	Coupe	Heckantrieb	Benzin	Jan 1973	Feb 1976	14604
Fiat	126	650	Schrägheck	Heckantrieb	Benzin	Jul 1981	Sep 2000	11939
Fiat	130	2.9	Stufenheck	Heckantrieb	Benzin	Jun 1969	Dec 1971	14611
Fiat	130	2.9	Stufenheck	Heckantrieb	Benzin	Oct 1970	Dec 1971	14612
Fiat	131	1.3 Mirafiori	Stufenheck	Heckantrieb	Benzin	Oct 1974	Dec 1982	14422
Fiat	131	1.3 Mirafiori	Kombi	Heckantrieb	Benzin	Mar 1975	Mar 1982	14424
Fiat	131	1.4 Mirafiori	Kombi	Heckantrieb	Benzin	Nov 1981	Jan 1984	14444
Fiat	131	1.4 Super Mirafiori	Stufenheck	Heckantrieb	Benzin	Apr 1981	Dec 1983	13493
Fiat	131	1.6 Super	Kombi	Heckantrieb	Benzin	Dec 1979	Dec 1981	14494
Fiat	131	2.0 Abarth Rally	Stufenheck	Heckantrieb	Benzin	Jan 1976	Jul 1980	14423
Fiat	131	2.0 D	Kombi	Heckantrieb	Diesel	Jul 1978	Aug 1984	13281
Fiat	131	2.0 D	Stufenheck	Heckantrieb	Diesel	Mar 1978	Mar 1987	13282
Fiat	132	2.0 D	Stufenheck	Heckantrieb	Diesel	Jul 1978	Jul 1982	14449
Fiat	132	2.5 D	Stufenheck	Heckantrieb	Diesel	Jul 1978	Jul 1982	14450
Fiat	238	1.4	Bus	Frontantrieb	Benzin	Sep 1966	Jun 1976	14195
Fiat	238	1.4	Bus	Frontantrieb	Benzin	Oct 1967	Jun 1982	14196
Fiat	242	1.6	Kasten	Frontantrieb	Benzin	Oct 1975	Jul 1982	14197
Fiat	242	1.6	Bus	Frontantrieb	Benzin	Oct 1975	Jul 1982	14202


--- Round 1 / 首次发送 ---
## 更新点

已完成缓存优先聚类、尺寸组复用和未覆盖外廓补全。商用车宽度口径已按车身宽度处理；无证据的动力、配置和改款分支未拆分。

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：77
* 映射引用缺失：0
* 孤立尺寸组：0
* 固定表头、唯一性、正整数、来源非空检查：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801735	801735	Pickup	I			EU-FAAM-JOLLY-2000-I-PICKUP-01	MEDIUM	Pritsche/Fahrgestell无具体上装，按官方允许的最大完整车身外廓闭合	READY
801734	801734	Pickup	I			EU-FAAM-SMILE-I-PICKUP-01	HIGH		READY
160238	160238	Van	I			EU-FARIZON-SUPERVAN-I-VAN-SWB-LR-01	MEDIUM	无轴距或车顶分支证据，采用标准SWB低顶量产外廓	READY
160720	160720	Van	I			EU-FARIZON-SUPERVAN-I-VAN-SWB-LR-01	MEDIUM	无轴距或车顶分支证据，采用标准SWB低顶量产外廓	READY
801885	801885	Van	I			EU-FARIZON-V6E-I-VAN-01	HIGH		READY
160182	160182	Pickup	I			EU-FEIDI-3MX-I-PICKUP-01	HIGH		READY
153995	153995	Pickup	I			EU-FEIDI-ENTER-I-PICKUP-01	HIGH	Pritsche/Fahrgestell按工厂Truck量产外廓映射	READY
801131	801131	Van	I			EU-FEIDI-ENTER-I-VAN-01	HIGH		READY
159722	159722	SUV	I		5	EU-FENGON-GLORY-600-I-SUV-01	HIGH		READY
159234	159234	Coupe	12Cilindri		2	EU-FERRARI-12CILINDRI-I-COUPE-01	HIGH		READY
159235	159235	Convertible	12Cilindri		2	EU-FERRARI-12CILINDRI-I-CONVERTIBLE-01	HIGH		READY
14683	14683	Convertible	360		2	EU-FERRARI-360-I-CONVERTIBLE-01	HIGH		READY
54923	54923	Coupe	360 Challenge		2	EU-FERRARI-360-CHALLENGE-COUPE-01	HIGH		READY
17343	17343	Coupe	360 Challenge Stradale		2	EU-FERRARI-360-CHALLENGE-STRADALE-COUPE-01	HIGH		READY
11979	11979	Coupe	360		2	EU-FERRARI-360-I-COUPE-01	HIGH		READY
56106	56106	Coupe	360		2	EU-FERRARI-360-I-COUPE-01	HIGH		READY
144609	144609	Coupe	400 Series I		2	EU-FERRARI-400-SERIES-I-COUPE-01	HIGH		READY
144611	144611	Convertible	400 Series I		2	EU-FERRARI-400-SERIES-I-CONVERTIBLE-01	HIGH		READY
144610	144610	Coupe	400 Series II		2	EU-FERRARI-400-SERIES-II-COUPE-01	MEDIUM		READY
144612	144612	Convertible	400 Series II		2	EU-FERRARI-400-SERIES-II-CONVERTIBLE-01	MEDIUM		READY
18619	18619	Convertible	458		2	EU-FERRARI-458-I-CONVERTIBLE-01	HIGH		READY
100096	100096	Coupe	458		2	EU-FERRARI-458-I-COUPE-01	HIGH		READY
101035	101035	Coupe	458		2	EU-FERRARI-458-I-COUPE-01	HIGH		READY
108936	108936	Convertible	458		2	EU-FERRARI-458-I-CONVERTIBLE-01	HIGH		READY
110605	110605	Convertible	458		2	EU-FERRARI-458-I-CONVERTIBLE-01	HIGH		READY
108191	108191	Coupe	208/308		2	EU-FERRARI-208-308-I-COUPE-01	HIGH		READY
150403	150403	Convertible	208/308		2	EU-FERRARI-208-308-I-CONVERTIBLE-01	HIGH		READY
127271	127271	Coupe	208/308		2	EU-FERRARI-208-308-I-COUPE-01	HIGH		READY
127270	127270	Convertible	208/308		2	EU-FERRARI-208-308-I-CONVERTIBLE-01	HIGH		READY
144563	144563	Coupe	275		2	EU-FERRARI-275-I-COUPE-01	HIGH		READY
144654	144654	Convertible	275		2	EU-FERRARI-275-I-CONVERTIBLE-01	HIGH		READY
145695	145695	Coupe	296		2	EU-FERRARI-296-I-COUPE-01	HIGH		READY
802251	802251	Coupe	296 Speciale		2	EU-FERRARI-296-SPECIALE-COUPE-01	HIGH		READY
147821	147821	Convertible	296		2	EU-FERRARI-296-I-CONVERTIBLE-01	HIGH		READY
113142	113142	Coupe	488		2	EU-FERRARI-488-I-COUPE-01	HIGH		READY
117780	117780	Convertible	488		2	EU-FERRARI-488-I-CONVERTIBLE-01	HIGH		READY
5732	5732	Coupe	550/575 Maranello		2	EU-FERRARI-550-575-MARANELLO-COUPE-01	HIGH		READY
105963	105963	Coupe	550/575 Maranello		2	EU-FERRARI-550-575-MARANELLO-COUPE-01	HIGH		READY
16656	16656	Coupe	550/575 Maranello		2	EU-FERRARI-550-575-MARANELLO-COUPE-01	HIGH		READY
15497	15497	Convertible	550 Barchetta		2	EU-FERRARI-550-BARCHETTA-CONVERTIBLE-01	HIGH		READY
14622	14622	Coupe	599 GTO		2	EU-FERRARI-599-GTO-COUPE-01	HIGH		READY
54917	54917	Coupe	599 GTO		2	EU-FERRARI-599-GTO-COUPE-01	HIGH		READY
52956	52956	Convertible	599 SA Aperta		2	EU-FERRARI-599-SA-APERTA-CONVERTIBLE-01	HIGH		READY
17853	17853	Coupe	612		2	EU-FERRARI-612-I-COUPE-01	HIGH		READY
128158	128158	Coupe	812 Superfast		2	EU-FERRARI-812-SUPERFAST-COUPE-01	HIGH		READY
145257	145257	Coupe	812 Competizione		2	EU-FERRARI-812-COMPETIZIONE-COUPE-01	HIGH		READY
152629	152629	Convertible	812 Competizione A		2	EU-FERRARI-812-COMPETIZIONE-A-CONVERTIBLE-01	HIGH		READY
162576	162576	Coupe	849 Testarossa		2	EU-FERRARI-849-TESTAROSSA-COUPE-01	MEDIUM	厂商发布宽度2304口径疑含后视镜，采用可追溯数据库不含镜车身宽度1999	READY
162577	162577	Convertible	849 Testarossa		2	EU-FERRARI-849-TESTAROSSA-CONVERTIBLE-01	MEDIUM	厂商发布宽度2304口径疑含后视镜，采用可追溯数据库不含镜车身宽度1999	READY
162205	162205	Coupe	Amalfi		2	EU-FERRARI-AMALFI-I-COUPE-01	HIGH		READY
106306	106306	Convertible	California T		2	EU-FERRARI-CALIFORNIA-T-CONVERTIBLE-01	HIGH		READY
154851	154851	Convertible	Daytona SP3		2	EU-FERRARI-DAYTONA-SP3-CONVERTIBLE-01	HIGH		READY
18065	18065	Coupe	Enzo		2	EU-FERRARI-ENZO-I-COUPE-01	HIGH		READY
56039	56039	Coupe	F12		2	EU-FERRARI-F12-I-COUPE-01	HIGH		READY
117781	117781	Coupe	F12tdf		2	EU-FERRARI-F12-TDF-COUPE-01	HIGH		READY
123772	123772	Convertible	F355 GTS		2	EU-FERRARI-F355-GTS-CONVERTIBLE-01	HIGH		READY
18525	18525	Convertible	F430		2	EU-FERRARI-F430-I-CONVERTIBLE-01	HIGH		READY
18306	18306	Coupe	F430		2	EU-FERRARI-F430-I-COUPE-01	HIGH		READY
10328	10328	Convertible	F430		2	EU-FERRARI-F430-I-CONVERTIBLE-01	HIGH		READY
159820	159820	Coupe	F80		2	EU-FERRARI-F80-I-COUPE-01	HIGH		READY
19058	19058	Coupe	FF		3	EU-FERRARI-FF-I-COUPE-01	HIGH		READY
58475	58475	Coupe	FF		3	EU-FERRARI-FF-I-COUPE-01	HIGH		READY
119787	119787	Coupe	GTC4Lusso		3	EU-FERRARI-GTC4LUSSO-I-COUPE-01	HIGH		READY
124998	124998	Coupe	GTC4Lusso		3	EU-FERRARI-GTC4LUSSO-I-COUPE-01	HIGH		READY
113735	113735	Coupe	LaFerrari		2	EU-FERRARI-LAFERRARI-I-COUPE-01	HIGH		READY
127274	127274	Convertible	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	HIGH		READY
127275	127275	Coupe	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-COUPE-01	HIGH		READY
143610	143610	Convertible	Portofino M		2	EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	HIGH		READY
150755	150755	SUV	Purosangue		5	EU-FERRARI-PUROSANGUE-I-SUV-01	HIGH		READY
154561	154561	Convertible	Roma Spider		2	EU-FERRARI-ROMA-SPIDER-CONVERTIBLE-01	HIGH		READY
144791	144791	Convertible	SF90		2	EU-FERRARI-SF90-I-CONVERTIBLE-01	HIGH		READY
156425	156425	Convertible	SF90 XX		2	EU-FERRARI-SF90-XX-CONVERTIBLE-01	HIGH		READY
156042	156042	Coupe	SF90 XX		2	EU-FERRARI-SF90-XX-COUPE-01	HIGH		READY
156206	156206	Van	I			EU-FEST-E-BOX-M-I-VAN-01	HIGH		READY
6001	6001	Sedan	I		4	EU-FIAT-124-I-SEDAN-01	HIGH		READY
14418	14418	Wagon	I		5	EU-FIAT-124-I-WAGON-01	HIGH		READY
116153	116153	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-01	HIGH		READY
116421	116421	Coupe	124 Sport Coupe CC		2	EU-FIAT-124-SPORT-COUPE-CC-01	HIGH		READY
14419	14419	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-01	HIGH		READY
14420	14420	Coupe	124 Sport Coupe CC		2	EU-FIAT-124-SPORT-COUPE-CC-01	HIGH		READY
14603	14603	Coupe	124 Sport Coupe CC		2	EU-FIAT-124-SPORT-COUPE-CC-01	HIGH		READY
14605	14605	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-01	HIGH		READY
14604	14604	Coupe	124 Sport Coupe CC		2	EU-FIAT-124-SPORT-COUPE-CC-01	HIGH		READY
11939	11939	Hatchback	I		2	EU-FIAT-126-I-HATCHBACK-01	HIGH		READY
14611	14611	Sedan	I		4	EU-FIAT-130-I-SEDAN-01	HIGH		READY
14612	14612	Sedan	I		4	EU-FIAT-130-I-SEDAN-01	HIGH		READY
14422	14422	Sedan	Series I		4	EU-FIAT-131-SERIES-I-SEDAN-01	MEDIUM	生产期跨改款但无单一Ktype多外廓证据，采用最匹配标准Mirafiori外廓	READY
14424	14424	Wagon	Series I		5	EU-FIAT-131-SERIES-I-WAGON-01	HIGH		READY
14444	14444	Wagon	Series III		5	EU-FIAT-131-SERIES-III-WAGON-01	MEDIUM		READY
13493	13493	Sedan	Series II/III		4	EU-FIAT-131-SERIES-II-III-SEDAN-01	MEDIUM		READY
14494	14494	Wagon	Series II		5	EU-FIAT-131-SERIES-II-WAGON-01	HIGH		READY
14423	14423	Sedan	Abarth Rally		2	EU-FIAT-131-ABARTH-RALLY-SEDAN-01	HIGH		READY
13281	13281	Wagon	Series II		5	EU-FIAT-131-SERIES-II-WAGON-01	HIGH		READY
13282	13282	Sedan	Series II/III		4	EU-FIAT-131-SERIES-II-III-SEDAN-01	MEDIUM	生产期跨阶段但动力差异不触发拆分，采用Super/Diesel标准轿车外廓	READY
14449	14449	Sedan	Series III		4	EU-FIAT-132-SERIES-III-SEDAN-01	HIGH		READY
14450	14450	Sedan	Series III		4	EU-FIAT-132-SERIES-III-SEDAN-01	HIGH		READY
14195	14195	MPV	I			EU-FIAT-238-I-MPV-01	MEDIUM		READY
14196	14196	MPV	I			EU-FIAT-238-I-MPV-01	MEDIUM		READY
14197	14197	Van	I			EU-FIAT-242-I-VAN-01	MEDIUM		READY
14202	14202	MPV	I			EU-FIAT-242-I-MPV-01	MEDIUM		READY
```

[下载 left18448_4601-4700_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_4601-4700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FAAM-JOLLY-2000-I-PICKUP-01	4770	2000	4000	FAAM technical sheet	https://www.electricmotornews.com/wp-content/uploads/2013/02/SCHEDA-TECNICA-FAAM-JOLLY-2000.pdf
EU-FAAM-SMILE-I-PICKUP-01	2900	1240	1775	FAAM technical sheet	https://www.electricmotornews.com/wp-content/uploads/2013/02/CARATTERISTICHE-TECNICHE-SMILE.pdf
EU-FARIZON-SUPERVAN-I-VAN-SWB-LR-01	4990	1980	1980	CarsGuide specifications	https://www.carsguide.com.au/farizon/supervan/car-dimensions/2025
EU-FARIZON-V6E-I-VAN-01	4845	1730	1985	Farizon V6E owner manual	https://www.farizonauto.si/uploads/source/farizonsn-documentum/Farizon_V6E_user_manual/V6E_OM_EN_20241105.pdf
EU-FEIDI-3MX-I-PICKUP-01	3980	1830	1970	Wuzheng official specifications	https://www.wuzheng.com/business/3-wheel-vehicles/3mx-ev
EU-FEIDI-ENTER-I-PICKUP-01	4900	1710	2010	Feidi Enter customer care manual	https://www.wuzheng.com/services/images/download/FEIDI-Enter-CustomerCare-Manual.pdf
EU-FEIDI-ENTER-I-VAN-01	4460	1640	1980	Feidi Enter customer care manual	https://www.wuzheng.com/services/images/download/FEIDI-Enter-CustomerCare-Manual.pdf
EU-FENGON-GLORY-600-I-SUV-01	4720	1865	1710	DFSK Finland official distributor	https://dfskfinland.com/products/dfsk-600/
EU-FERRARI-12CILINDRI-I-COUPE-01	4733	2000	1292	Automobile-Catalog	https://www.automobile-catalog.com/car/2024/3377210/ferrari_12cilindri.html
EU-FERRARI-12CILINDRI-I-CONVERTIBLE-01	4733	2000	1292	Automobile-Catalog	https://www.automobile-catalog.com/car/2024/3377225/ferrari_12cilindri_spider.html
EU-FERRARI-360-I-CONVERTIBLE-01	4477	1922	1235	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/707135/ferrari_360_spider_f1.html
EU-FERRARI-360-CHALLENGE-COUPE-01	4477	1992	1184	Ferrari official model archive	https://www.ferrari.com/en-EN/auto/360-challenge
EU-FERRARI-360-CHALLENGE-STRADALE-COUPE-01	4477	1922	1199	Ferrari official model archive	https://www.ferrari.com/en-EN/auto/challenge-stradale
EU-FERRARI-360-I-COUPE-01	4477	1922	1214	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/707075/ferrari_360_modena.html
EU-FERRARI-400-SERIES-I-COUPE-01	4300	1680	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/705260/ferrari_400_superamerica_series_i.html
EU-FERRARI-400-SERIES-I-CONVERTIBLE-01	4300	1680	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/705260/ferrari_400_superamerica_series_i.html
EU-FERRARI-400-SERIES-II-COUPE-01	4670	1770	1300	Wikipedia technical specifications	https://de.wikipedia.org/wiki/Ferrari_400_Superamerica
EU-FERRARI-400-SERIES-II-CONVERTIBLE-01	4670	1770	1300	Wikipedia technical specifications	https://de.wikipedia.org/wiki/Ferrari_400_Superamerica
EU-FERRARI-458-I-CONVERTIBLE-01	4527	1937	1211	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Ferrari/138040/Ferrari-458-Italia-Spider.html
EU-FERRARI-458-I-COUPE-01	4527	1937	1213	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Ferrari/35710/Ferrari-458-Italia-.html
EU-FERRARI-208-308-I-COUPE-01	4230	1720	1120	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/705995/ferrari_308_gtbi.html
EU-FERRARI-208-308-I-CONVERTIBLE-01	4230	1720	1120	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/705995/ferrari_308_gtbi.html
EU-FERRARI-275-I-COUPE-01	4325	1725	1245	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/28085/ferrari_275_gtb.html
EU-FERRARI-275-I-CONVERTIBLE-01	4350	1675	1250	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/705470/ferrari_275_gts.html
EU-FERRARI-296-I-COUPE-01	4565	1958	1187	Automobile-Catalog	https://www.automobile-catalog.com/car/2024/3008810/ferrari_296_gtb.html
EU-FERRARI-296-SPECIALE-COUPE-01	4625	1968	1181	AutoTijd dimensions	https://autotijd.be/en/dimensions/ferrari/296-speciale
EU-FERRARI-296-I-CONVERTIBLE-01	4565	1958	1191	Automobile-Catalog	https://www.automobile-catalog.com/car/2023/3085940/ferrari_296_gts.html
EU-FERRARI-488-I-COUPE-01	4568	1952	1213	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2232020/ferrari_488_gtb.html
EU-FERRARI-488-I-CONVERTIBLE-01	4568	1952	1211	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2232035/ferrari_488_spider.html
EU-FERRARI-550-575-MARANELLO-COUPE-01	4550	1935	1277	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/707015/ferrari_550_maranello.html
EU-FERRARI-550-BARCHETTA-CONVERTIBLE-01	4550	1935	1258	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/707165/ferrari_550_barchetta.html
EU-FERRARI-599-GTO-COUPE-01	4710	1962	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1372805/ferrari_599_gto.html
EU-FERRARI-599-SA-APERTA-CONVERTIBLE-01	4700	1962	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1455395/ferrari_sa_aperta_pininfarina.html
EU-FERRARI-612-I-COUPE-01	4902	1957	1344	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1221050/ferrari_612_scaglietti.html
EU-FERRARI-812-SUPERFAST-COUPE-01	4657	1971	1276	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2746265/ferrari_812_superfast.html
EU-FERRARI-812-COMPETIZIONE-COUPE-01	4696	1971	1276	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/3008825/ferrari_812_competizione.html
EU-FERRARI-812-COMPETIZIONE-A-CONVERTIBLE-01	4696	1971	1276	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/3008825/ferrari_812_competizione.html
EU-FERRARI-849-TESTAROSSA-COUPE-01	4718	1999	1225	CarWale dimensions	https://www.carwale.com/compare-cars/ferrari-849-testarossa-vs-aston-martin-dbx-vs-ferrari-purosangue-suv/
EU-FERRARI-849-TESTAROSSA-CONVERTIBLE-01	4718	1999	1186	CarWale dimensions	https://www.carwale.com/compare-cars/ferrari-849-testarossa-vs-aston-martin-dbx-vs-ferrari-purosangue-suv/
EU-FERRARI-AMALFI-I-COUPE-01	4660	1974	1301	Automobile-Catalog	https://www.automobile-catalog.com/car/2026/3460685/ferrari_amalfi.html
EU-FERRARI-CALIFORNIA-T-CONVERTIBLE-01	4570	1910	1322	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2044070/ferrari_california_t.html
EU-FERRARI-DAYTONA-SP3-CONVERTIBLE-01	4686	2050	1142	Ferrari official article	https://www.ferrari.com/en-EN/corporate/articles/ferrari-unveils-an-exclusive-tailor-made-daytona-sp3
EU-FERRARI-ENZO-I-COUPE-01	4702	2035	1147	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/707255/ferrari_enzo.html
EU-FERRARI-F12-I-COUPE-01	4618	1942	1273	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/1613015/ferrari_f12_berlinetta.html
EU-FERRARI-F12-TDF-COUPE-01	4656	1961	1273	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2232050/ferrari_f12tdf.html
EU-FERRARI-F355-GTS-CONVERTIBLE-01	4250	1900	1170	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/706925/ferrari_f355_gts.html
EU-FERRARI-F430-I-CONVERTIBLE-01	4512	1923	1234	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/707390/ferrari_f430_spider_f1.html
EU-FERRARI-F430-I-COUPE-01	4512	1923	1214	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/707345/ferrari_f430_berlinetta.html
EU-FERRARI-F80-I-COUPE-01	4840	2060	1138	Automobile-Catalog	https://www.automobile-catalog.com/car/2025/3377195/ferrari_f80.html
EU-FERRARI-FF-I-COUPE-01	4907	1953	1379	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/1455380/ferrari_ff.html
EU-FERRARI-GTC4LUSSO-I-COUPE-01	4922	1980	1383	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2513720/ferrari_gtc4lusso.html
EU-FERRARI-LAFERRARI-I-COUPE-01	4702	1992	1116	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/1842590/laferrari.html
EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	4535	1795	1265	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/706385/ferrari_mondial_3_2_cabriolet.html
EU-FERRARI-MONDIAL-3-2-COUPE-01	4535	1795	1235	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/706370/ferrari_mondial_3_2.html
EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	4594	1938	1318	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2975525/ferrari_portofino_m.html
EU-FERRARI-PUROSANGUE-I-SUV-01	4973	2028	1589	AutoTijd dimensions	https://autotijd.be/en/dimensions/ferrari/purosangue
EU-FERRARI-ROMA-SPIDER-CONVERTIBLE-01	4656	1974	1306	AutoTijd dimensions	https://autotijd.be/en/dimensions/ferrari/roma-spider
EU-FERRARI-SF90-I-CONVERTIBLE-01	4704	1973	1191	Automobile-Catalog	https://www.automobile-catalog.com/car/2023/2975540/ferrari_sf90_spider.html
EU-FERRARI-SF90-XX-CONVERTIBLE-01	4850	2014	1225	Automobile-Catalog	https://www.automobile-catalog.com/car/2026/3570665/ferrari_sf90_xx_spider.html
EU-FERRARI-SF90-XX-COUPE-01	4850	2014	1225	Automobile-Catalog	https://www.automobile-catalog.com/car/2026/3570665/ferrari_sf90_xx_spider.html
EU-FEST-E-BOX-M-I-VAN-01	4525	1610	1900	Fest official specifications	https://fest-auto-en.webflow.io/e-box-m
EU-FIAT-124-I-SEDAN-01	4030	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/709760/fiat_124.html
EU-FIAT-124-I-WAGON-01	4045	1625	1440	Wikipedia technical specifications	https://en.wikipedia.org/wiki/Fiat_124
EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-01	3970	1613	1250	AutoEvolution	https://www.autoevolution.com/cars/fiat-124-sport-spider-1969.html
EU-FIAT-124-SPORT-COUPE-CC-01	4176	1669	1341	AutoEvolution	https://www.autoevolution.com/cars/fiat-124-sport-coupe-cc-1972.html
EU-FIAT-126-I-HATCHBACK-01	3054	1377	1335	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/40415/polski_fiat_126p_650.html
EU-FIAT-130-I-SEDAN-01	4750	1805	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/713720/fiat_130.html
EU-FIAT-131-SERIES-I-SEDAN-01	4265	1651	1382	AutoEvolution	https://www.autoevolution.com/cars/fiat-131-mirafiori-4-doors-1978.html
EU-FIAT-131-SERIES-I-WAGON-01	4264	1650	1400	Automoli specifications	https://www.automoli.com/us/vehicles/fiat/131/131-familiarepanorama-1608/
EU-FIAT-131-SERIES-III-WAGON-01	4231	1645	1420	Autotecnica historical specifications	https://www.autotecnica.org/fiat-131-terza-serie-indimenticabile/
EU-FIAT-131-SERIES-II-III-SEDAN-01	4231	1651	1381	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/36710/fiat_131_diesel_2500_super.html
EU-FIAT-131-SERIES-II-WAGON-01	4264	1651	1389	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/712550/fiat_131_panorama_l_1300.html
EU-FIAT-131-ABARTH-RALLY-SEDAN-01	4190	1720	1360	AutoZine historical specifications	https://www.autozine.org/Archive/Fiat/classic/131.html
EU-FIAT-132-SERIES-III-SEDAN-01	4390	1640	1430	Carfolio specifications	https://www.carfolio.com/fiat-132-diesel-2500-37906
EU-FIAT-238-I-MPV-01	4600	1835	1980	Drive.Place specifications	https://fiat.drive.place/238/i/group_minivan/380686
EU-FIAT-242-I-VAN-01	4961	1990	2356	KFZ-Tech historical specifications	https://www.kfz-tech.de/Engl/Hersteller/Fiat/Fiat2421975.htm
EU-FIAT-242-I-MPV-01	4961	1990	2356	KFZ-Tech historical specifications	https://www.kfz-tech.de/Engl/Hersteller/Fiat/Fiat2421975.htm
```

[下载 left18448_4601-4700_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_4601-4700_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5436 行）
- 累计尺寸组：dimension_groups_final.tsv（1636 行）

