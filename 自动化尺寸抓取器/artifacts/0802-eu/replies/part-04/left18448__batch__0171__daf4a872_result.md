# 任务：left18448 第 17001-17100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0171__daf4a872


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 17001-17100 行

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
left18448 第 17001-17100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_17001-17100_ktype_dimension_mapping_final.tsv
- left18448_17001-17100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VOLVO-XC60-II-SUV-FACELIFT-01	4708	1902	1655

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Volvo	Xc60 ii	B4 Mild-hybrid	SUV	Frontantrieb	Diesel/Elektro	May 2019	-	144949
Volvo	Xc60 ii	B5 Mild-hybrid Polestar AWD	SUV	Allrad	Diesel/Elektro	Jan 2021	-	800184
Volvo	Xc60 ii	D4 AWD	SUV	Allrad	Diesel	Mar 2017	Dec 2021	126478
Volvo	Xc60 ii	D5 AWD	SUV	Allrad	Diesel	Mar 2017	Dec 2022	126479
Volvo	Xc60 ii	T5	SUV	Frontantrieb	Benzin	Mar 2017	-	128114
Volvo	Xc60 ii	T5 AWD	SUV	Allrad	Benzin	Mar 2017	Dec 2021	126480
Volvo	Xc60 ii	T6 AWD	SUV	Allrad	Benzin	Mar 2017	Dec 2021	126481
Volvo	Xc60 ii	T6 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Apr 2021	-	145081
Volvo	Xc60 ii	T6 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jan 2022	-	151835
Volvo	Xc60 ii	T6 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Apr 2022	-	801159
Volvo	Xc60 ii	T6 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	May 2026	-	803459
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	Mar 2017	Dec 2022	126482
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jan 2022	-	146619
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	Sep 2017	Dec 2022	146749
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	May 2026	-	803458
Volvo	Xc60 ii	T8 Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	May 2021	Dec 2022	143450
Volvo	Xc70 i cross country	2.4 T XC AWD	Kombi	Allrad	Benzin	Mar 2000	Sep 2002	14616
Volvo	Xc70 i cross country	2.5 T XC AWD	Kombi	Allrad	Benzin	Sep 2002	Aug 2007	16995
Volvo	Xc70 i cross country	D5 XC AWD	Kombi	Allrad	Diesel	Sep 2002	Aug 2007	16845
Volvo	Xc70 ii	2.4 D	Kombi	Frontantrieb	Diesel	Jun 2009	Dec 2010	33817
Volvo	Xc70 ii	D3	Kombi	Frontantrieb	Diesel	Apr 2010	Dec 2015	11508
Volvo	Xc70 ii	D4	Kombi	Frontantrieb	Diesel	Oct 2013	Apr 2016	100393
Volvo	Xc70 ii	D4 AWD	Kombi	Allrad	Diesel	Oct 2013	Apr 2016	100283
Volvo	Xc70 ii	D5 AWD	Kombi	Allrad	Diesel	Apr 2011	Dec 2015	10295
Volvo	Xc70 ii	D5 AWD	Kombi	Allrad	Diesel	Mar 2015	Apr 2016	113294
Volvo	Xc70 ii	T5	Kombi	Frontantrieb	Benzin	Oct 2013	Dec 2016	100394
Volvo	Xc70 ii	T5 AWD	Kombi	Allrad	Benzin	Aug 2015	Dec 2016	115626
Volvo	Xc70 ii van	2.0 D4	Kasten/Kombi	Frontantrieb	Diesel	Sep 2013	Dec 2016	143205
Volvo	Xc70 ii van	2.4 D4 AWD	Kasten/Kombi	Allrad	Diesel	Sep 2013	Apr 2016	143206
Volvo	Xc70 ii van	2.4 D5 AWD	Kasten/Kombi	Allrad	Diesel	Sep 2013	Dec 2016	143207
Volvo	Xc90 i	3.2	SUV	Frontantrieb	Benzin	Sep 2011	Sep 2014	106045
Volvo	Xc90 i	2.5 T AWD	SUV	Allrad	Benzin	Oct 2002	Sep 2014	16570
Volvo	Xc90 i	2.5 T AWD	SUV	Allrad	Benzin	Oct 2012	Sep 2014	108870
Volvo	Xc90 i	3.2 AWD	SUV	Allrad	Benzin	Apr 2010	Sep 2014	12490
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	Oct 2002	Dec 2006	16572
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	Oct 2007	Dec 2010	109449
Volvo	Xc90 i	T6 AWD	SUV	Allrad	Benzin	Oct 2002	Dec 2006	16571
Volvo	Xc90 i	V8 AWD	SUV	Allrad	Benzin	Jan 2005	Dec 2010	18291
Volvo	Xc90 i	V8 AWD	SUV	Allrad	Benzin	Sep 2004	Dec 2005	108617
Volvo	Xc90 i van	2.4 D4	Kasten/SUV	Frontantrieb	Diesel	Sep 2013	Dec 2014	143066
Volvo	Xc90 i van	2.4 D5 AWD	Kasten/SUV	Allrad	Diesel	Sep 2013	Dec 2014	143065
Volvo	Xc90 ii	B5 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147179
Volvo	Xc90 ii	B5 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2022	-	147210
Volvo	Xc90 ii	B5 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	Mar 2022	-	147178
Volvo	Xc90 ii	B5 Mild-hybrid Polestar AWD	SUV	Allrad	Diesel/Elektro	Jan 2021	-	800185
Volvo	Xc90 ii	D4	SUV	Frontantrieb	Diesel	Jun 2015	Dec 2018	111885
Volvo	Xc90 ii	D4 AWD	SUV	Allrad	Diesel	Oct 2015	Dec 2018	111886
Volvo	Xc90 ii	D5 AWD	SUV	Allrad	Diesel	Sep 2014	Dec 2016	107556
Volvo	Xc90 ii	D5 AWD	SUV	Allrad	Diesel	Mar 2016	Dec 2019	119842
Volvo	Xc90 ii	T5 AWD	SUV	Allrad	Benzin	Jun 2015	Dec 2021	111887
Volvo	Xc90 ii	T5 AWD	SUV	Allrad	Benzin	Feb 2016	Dec 2018	120522
Volvo	Xc90 ii	T6 AWD	SUV	Allrad	Benzin	Sep 2014	Dec 2018	107555
Volvo	Xc90 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	Jun 2015	Dec 2018	111864
Volvo	Xc90 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	May 2026	-	803457
Volvo	Xc90 ii	T8 Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	Feb 2020	Dec 2022	153020
Volvo	Xc90 ii	T8 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	May 2022	-	146643
Voyah	Courage	EV	SUV	Heckantrieb	Elektro	Oct 2024	-	159942
Voyah	Courage	EV	SUV	Allrad	Elektro	Oct 2024	-	159944
Voyah	Dream	EV Allrad	Großraumlimousine	Allrad	Elektro	Oct 2024	-	147538
Voyah	Free	EV Allrad	SUV	Allrad	Elektro	Sep 2022	-	150130
VW	166	1.1	Geländewagen offen	Allrad	Benzin	Feb 1942	Dec 1945	14881
VW	181	1.5	Geländewagen offen	Heckantrieb	Benzin	Sep 1969	Jul 1970	8911
VW	Amarok	2.0 Bitdi	Pick-up	Heckantrieb	Diesel	Nov 2011	May 2022	56028
VW	Amarok	2.0 Bitdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2012	Oct 2016	113222
VW	Amarok	2.0 Bitdi 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Sep 2011	Jul 2019	113223
VW	Amarok	2.0 TDI	Pick-up	Heckantrieb	Diesel	Sep 2010	Oct 2013	34980
VW	Amarok	2.0 TDI	Pick-up	Heckantrieb	Diesel	Jul 2012	May 2022	56896
VW	Amarok	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Oct 2013	113218
VW	Amarok	2.0 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2011	Oct 2016	113219
VW	Amarok	2.0 TDI 4motion	Pick-up	Allrad	Diesel	Sep 2010	Oct 2013	34979
VW	Amarok	2.0 TDI 4motion	Pick-up	Allrad	Diesel	Jun 2012	May 2022	56897
VW	Amarok	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	Sep 2011	Oct 2016	117767
VW	Amarok	2.0 TDI 4motion	Pick-up	Allrad	Diesel	Sep 2022	-	152399
VW	Amarok	2.0 TDI 4motion	Pick-up	Allrad	Diesel	Sep 2022	-	152400
VW	Amarok	2.0 TSI	Pick-up	Heckantrieb	Benzin	Dec 2010	Oct 2016	12071
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	Jun 2016	May 2022	120195
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	Sep 2022	-	152401
VW	Arteon	1.4 Ehybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2020	-	143835
VW	Arteon	1.4 Ehybrid	Kombi	Frontantrieb	Benzin/Elektro	Nov 2020	-	143838
VW	Arteon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2017	-	127056
VW	Arteon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2017	-	128180
VW	Arteon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2020	-	142914
VW	Arteon	2.0 TDI	Kombi	Frontantrieb	Diesel	Sep 2020	-	142920
VW	Arteon	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	Mar 2017	Jul 2020	126831
VW	Arteon	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	May 2017	-	128179
VW	Arteon	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	Sep 2020	-	142913
VW	Arteon	2.0 TDI 4motion	Kombi	Allrad	Diesel	Feb 2024	-	157935
VW	Arteon	2.0 TSI	Schrägheck	Frontantrieb	Benzin	May 2017	Jun 2021	128181
VW	Arteon	2.0 TSI	Kombi	Frontantrieb	Benzin	Sep 2020	Jun 2021	144801
VW	Arteon	2.0 TSI	Schrägheck	Frontantrieb	Benzin	Nov 2020	Dec 2024	801682
VW	Arteon	2.0 TSI	Kombi	Frontantrieb	Benzin	Jun 2020	Dec 2024	801683
VW	Arteon	2.0 TSI 4motion	Schrägheck	Allrad	Benzin	Apr 2017	-	126829
VW	Arteon	2.0 TSI 4motion	Kombi	Allrad	Benzin	Jun 2020	-	142921
VW	Arteon	2.0 TSI R 4motion	Schrägheck	Allrad	Benzin	Nov 2020	-	143836
VW	Arteon	2.0 TSI R 4motion	Kombi	Allrad	Benzin	Nov 2020	-	143837
VW	Atlas	3.6 FSI 4motion	SUV	Allrad	Benzin	Dec 2016	-	128511
VW	Beetle	2.5	Schrägheck	Frontantrieb	Benzin	Apr 2011	Jul 2019	58101
VW	Beetle	2.5	Cabriolet	Frontantrieb	Benzin	Dec 2011	Jul 2016	116818
VW	Beetle	1.2 TSI	Schrägheck	Frontantrieb	Benzin	Jul 2011	Jul 2019	11293
VW	Beetle	1.2 TSI	Cabriolet	Frontantrieb	Benzin	Dec 2011	Jul 2019	56783


--- Round 1 / 首次发送 ---
## 更新点

已完成全部物理外廓聚类与尺寸组闭合。XC60 II 已复用跨批次既有尺寸组；XC90 II、Amarok、Beetle 仅对有明确外廓差异的 Ktype 派生分支；Voyah Dream、Arteon eHybrid 和 Amarok II 的配置差异已按直接规格页分别落组。([Voyah][1])

## 进度

输入 Ktype：100
最终映射行：110
READY：110
PENDING：0
DIMENSION_GROUP：32
机械终检：通过

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144949	144949	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
800184	800184	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-01	HIGH		READY
126478	126478	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
126479	126479	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
128114	128114	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
126480	126480	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
126481	126481	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
145081	145081	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	HIGH		READY
151835	151835	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	HIGH		READY
801159	801159	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	HIGH		READY
803459	803459	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-02	HIGH		READY
126482	126482	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
146619	146619	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	HIGH		READY
146749	146749	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	HIGH		READY
803458	803458	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-02	HIGH		READY
143450	143450	SUV	XC60 II facelift		5	EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	HIGH		READY
14616	14616	Wagon	XC70 I		5	EU-VOLVO-XC70-I-WAGON-01	HIGH		READY
16995	16995	Wagon	XC70 I		5	EU-VOLVO-XC70-I-WAGON-01	HIGH		READY
16845	16845	Wagon	XC70 I		5	EU-VOLVO-XC70-I-WAGON-01	HIGH		READY
33817	33817	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
11508	11508	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
100393	100393	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
100283	100283	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
10295	10295	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
113294	113294	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
100394	100394	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
115626	115626	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH		READY
143205	143205	Van	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	Commercial classification; exterior matches the XC70 II wagon body.	READY
143206	143206	Van	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	Commercial classification; exterior matches the XC70 II wagon body.	READY
143207	143207	Van	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	Commercial classification; exterior matches the XC70 II wagon body.	READY
106045	106045	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
16570	16570	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
108870	108870	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
12490	12490	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
16572	16572	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
109449	109449	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
16571	16571	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
18291	18291	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
108617	108617	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH		READY
143066	143066	Van	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH	Commercial classification; exterior matches the XC90 I SUV body.	READY
143065	143065	Van	XC90 I		5	EU-VOLVO-XC90-I-SUV-01	HIGH	Commercial classification; exterior matches the XC90 I SUV body.	READY
147179	147179	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
147210	147210	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
147178	147178	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
800185	800185	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
111885	111885	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
111886	111886	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
107556	107556	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
119842_facelift	119842	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH	Ktype production range covers both exterior stages.	READY
119842_prefl	119842	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH	Ktype production range covers both exterior stages.	READY
111887_facelift	111887	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH	Ktype production range covers both exterior stages.	READY
111887_prefl	111887	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH	Ktype production range covers both exterior stages.	READY
120522	120522	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
107555	107555	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
111864	111864	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	HIGH		READY
803457	803457	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-02	HIGH		READY
153020	153020	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
146643	146643	SUV	XC90 II facelift		5	EU-VOLVO-XC90-II-SUV-FACELIFT-01	HIGH		READY
159942	159942	SUV	Courage I		5	EU-VOYAH-COURAGE-I-SUV-RWD-01	HIGH		READY
159944	159944	SUV	Courage I		5	EU-VOYAH-COURAGE-I-SUV-AWD-01	HIGH		READY
147538	147538	MPV	Dream I		5	EU-VOYAH-DREAM-I-MPV-AWD-01	HIGH		READY
150130	150130	SUV	Free I		5	EU-VOYAH-FREE-I-SUV-AWD-01	HIGH		READY
14881	14881	Convertible	Type 166	166		EU-VW-TYPE-166-CONVERTIBLE-01	MEDIUM	Open amphibious body; door count is not used as a branch.	READY
8911	8911	Convertible	Type 181	181	4	EU-VW-TYPE-181-CONVERTIBLE-01	HIGH		READY
56028_doublecab	56028	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
56028_singlecab	56028	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
113222	113222	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-CHASSIS-01	HIGH	Factory platform/chassis branch; no cargo bed body is assumed.	READY
113223	113223	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-CHASSIS-01	HIGH	Factory platform/chassis branch; no cargo bed body is assumed.	READY
34980_doublecab	34980	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
34980_singlecab	34980	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
56896_doublecab	56896	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
56896_singlecab	56896	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
113218	113218	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-CHASSIS-01	HIGH	Factory platform/chassis branch; no cargo bed body is assumed.	READY
113219	113219	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-CHASSIS-01	HIGH	Factory platform/chassis branch; no cargo bed body is assumed.	READY
34979_doublecab	34979	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
34979_singlecab	34979	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
56897_doublecab	56897	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
56897_singlecab	56897	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
117767	117767	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-CHASSIS-01	HIGH	Factory platform/chassis branch; no cargo bed body is assumed.	READY
152399	152399	Pickup	Amarok II	T1A/T1B	4	EU-VW-AMAROK-II-PICKUP-DOUBLECAB-LOW-01	HIGH		READY
152400	152400	Pickup	Amarok II	T1A/T1B	4	EU-VW-AMAROK-II-PICKUP-DOUBLECAB-01	HIGH		READY
12071_doublecab	12071	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
12071_singlecab	12071	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	Ktype covers both single-cab and double-cab pickup bodies.	READY
120195	120195	Pickup	Amarok I facelift	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-FACELIFT-01	HIGH		READY
152401	152401	Pickup	Amarok II	T1A/T1B	4	EU-VW-AMAROK-II-PICKUP-DOUBLECAB-01	HIGH		READY
143835	143835	Hatchback	Arteon I facelift		5	EU-VW-ARTEON-I-HATCHBACK-FACELIFT-PHEV-01	HIGH		READY
143838	143838	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-PHEV-01	HIGH		READY
127056	127056	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
128180	128180	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
142914	142914	Hatchback	Arteon I facelift		5	EU-VW-ARTEON-I-HATCHBACK-FACELIFT-01	HIGH		READY
142920	142920	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
126831	126831	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
128179	128179	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
142913	142913	Hatchback	Arteon I facelift		5	EU-VW-ARTEON-I-HATCHBACK-FACELIFT-01	HIGH		READY
157935	157935	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
128181	128181	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
144801	144801	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
801682	801682	Hatchback	Arteon I facelift		5	EU-VW-ARTEON-I-HATCHBACK-FACELIFT-01	HIGH		READY
801683	801683	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
126829	126829	Hatchback	Arteon I		5	EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	HIGH		READY
142921	142921	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
143836	143836	Hatchback	Arteon I facelift		5	EU-VW-ARTEON-I-HATCHBACK-FACELIFT-01	HIGH		READY
143837	143837	Wagon	Arteon I facelift		5	EU-VW-ARTEON-I-WAGON-FACELIFT-01	HIGH		READY
128511	128511	SUV	Atlas I		5	EU-VW-ATLAS-I-SUV-01	HIGH		READY
58101	58101	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH		READY
116818	116818	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH		READY
11293_facelift	11293	Hatchback	Beetle A5 facelift	5C	3	EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	HIGH	Ktype production range covers the 2016 exterior-dimension change.	READY
11293_prefl	11293	Hatchback	Beetle A5	5C	3	EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	HIGH	Ktype production range covers the 2016 exterior-dimension change.	READY
56783_facelift	56783	Convertible	Beetle A5 facelift	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	HIGH	Ktype production range covers the 2016 exterior-dimension change.	READY
56783_prefl	56783	Convertible	Beetle A5	5C	2	EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	HIGH	Ktype production range covers the 2016 exterior-dimension change.	READY
```

[下载 left18448_17001-17100_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_17001-17100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-XC60-II-SUV-PREFACELIFT-01	4688	1902	1658	Auto-Data.net	https://www.auto-data.net/en/volvo-xc60-ii-generation-5397
EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-01	4708	1902	1653	Auto-Data.net	https://www.auto-data.net/en/volvo-xc60-ii-facelift-2021-recharge-t6-2.0-253hp-plug-in-hybrid-awd-geartronic-45585
EU-VOLVO-XC60-II-SUV-FACELIFT-01	4708	1902	1655	Volvo Cars support	https://www.volvocars.com/en-om/support/car/xc60/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-XC60-II-SUV-FACELIFT-PHEV-02	4708	1902	1651	Volvo Cars support	https://www.volvocars.com/us/support/car/xc60-plug-in-hybrid/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-XC70-I-WAGON-01	4733	1860	1562	Auto-Data.net	https://www.auto-data.net/en/volvo-xc70-i-generation-1959
EU-VOLVO-XC70-II-WAGON-01	4838	1870	1604	Auto-Data.net	https://www.auto-data.net/en/volvo-xc70-model-933
EU-VOLVO-XC90-I-SUV-01	4807	1936	1784	Auto-Data.net	https://www.auto-data.net/en/volvo-xc90-generation-1968
EU-VOLVO-XC90-II-SUV-PREFACELIFT-01	4950	1923	1776	Auto-Data.net	https://www.auto-data.net/en/volvo-xc90-ii-generation-4274
EU-VOLVO-XC90-II-SUV-FACELIFT-01	4953	1923	1776	Auto-Data.net	https://www.auto-data.net/en/volvo-xc90-ii-facelift-2019-generation-7427
EU-VOLVO-XC90-II-SUV-FACELIFT-02	4953	1923	1767	Auto-Data.net	https://www.auto-data.net/en/volvo-xc90-model-938
EU-VOYAH-COURAGE-I-SUV-RWD-01	4725	1900	1636	Data.CarNewsChina	https://data.carnewschina.com/database/voyah/aratu-knowles/2024/params
EU-VOYAH-COURAGE-I-SUV-AWD-01	4725	1900	1653	Data.CarNewsChina	https://data.carnewschina.com/database/voyah/aratu-knowles/2024/params
EU-VOYAH-DREAM-I-MPV-AWD-01	5315	1985	1800	VOYAH Norway	https://www.voyah.no/voyah-dream/spesifikasjoner
EU-VOYAH-FREE-I-SUV-AWD-01	4905	1950	1645	VOYAH Finland	https://www.voyah.fi/voyah-free
EU-VW-TYPE-166-CONVERTIBLE-01	3825	1480	1615	Wikipedia	https://en.wikipedia.org/wiki/Volkswagen_Schwimmwagen
EU-VW-TYPE-181-CONVERTIBLE-01	3780	1640	1620	Conceptcarz	https://www.conceptcarz.com/s10439/volkswagen-type-181-thing.aspx
EU-VW-AMAROK-I-PICKUP-SINGLECAB-01	5181	1944	1820	Auto-Data.net	https://www.auto-data.net/en/volkswagen-amarok-i-single-cab-2.0-tdi-140hp-20553
EU-VW-AMAROK-I-PICKUP-DOUBLECAB-01	5254	1944	1834	Auto-Data.net	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-generation-4342
EU-VW-AMAROK-I-PICKUP-DOUBLECAB-FACELIFT-01	5254	1954	1834	Auto-Data.net	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-generation-5211
EU-VW-AMAROK-I-PICKUP-CHASSIS-01	5181	1944	1820	CarExpert specifications	https://www.carexpert.com.au/volkswagen/amarok/2015-2l-utility-4x4-diesel-automatic-jog5ak5m20150106
EU-VW-AMAROK-II-PICKUP-DOUBLECAB-LOW-01	5390	1910	1871	Auto-Data.net	https://www.auto-data.net/en/volkswagen-amarok-ii-2.0-tdi-170hp-4motion-48657
EU-VW-AMAROK-II-PICKUP-DOUBLECAB-01	5390	1910	1884	Auto-Data.net	https://www.auto-data.net/en/volkswagen-amarok-ii-2.0-tdi-205hp-4motion-48658
EU-VW-ARTEON-I-HATCHBACK-PREFACELIFT-01	4862	1871	1450	Auto-Data.net	https://www.auto-data.net/en/volkswagen-arteon-generation-5396
EU-VW-ARTEON-I-HATCHBACK-FACELIFT-01	4866	1871	1460	Auto-Data.net	https://www.auto-data.net/en/volkswagen-arteon-facelift-2020-generation-7833
EU-VW-ARTEON-I-HATCHBACK-FACELIFT-PHEV-01	4866	1871	1449	Auto-Data.net	https://www.auto-data.net/en/volkswagen-arteon-facelift-2020-1.4-tsi-218hp-ehybrid-dsg-41794
EU-VW-ARTEON-I-WAGON-FACELIFT-01	4866	1871	1462	Auto-Data.net	https://www.auto-data.net/en/volkswagen-arteon-shooting-brake-facelift-2020-generation-7832
EU-VW-ARTEON-I-WAGON-FACELIFT-PHEV-01	4866	1871	1450	Auto-Data.net	https://www.auto-data.net/en/volkswagen-arteon-shooting-brake-facelift-2020-1.4-tsi-218hp-ehybrid-dsg-41796
EU-VW-ATLAS-I-SUV-01	5036	1989	1778	Auto-Data.net	https://www.auto-data.net/en/volkswagen-atlas-3.6-v6-276hp-4motion-automatic-30408
EU-VW-BEETLE-A5-HATCHBACK-PREFACELIFT-01	4278	1808	1486	Auto-Data.net	https://www.auto-data.net/en/volkswagen-beetle-a5-generation-3785
EU-VW-BEETLE-A5-CONVERTIBLE-PREFACELIFT-01	4278	1808	1473	Auto-Data.net	https://www.auto-data.net/en/volkswagen-beetle-convertible-a5-1.2-tsi-105hp-dsg-20569
EU-VW-BEETLE-A5-HATCHBACK-FACELIFT-01	4288	1825	1488	Auto-Data.net	https://www.auto-data.net/en/volkswagen-beetle-model-897
EU-VW-BEETLE-A5-CONVERTIBLE-FACELIFT-01	4288	1825	1473	Auto-Data.net	https://www.auto-data.net/en/volkswagen-beetle-model-897
```

[下载 left18448_17001-17100_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_17001-17100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.voyah.no/voyah-dream/spesifikasjoner "https://www.voyah.no/voyah-dream/spesifikasjoner"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3962 行）
- 累计尺寸组：dimension_groups_final.tsv（1015 行）

