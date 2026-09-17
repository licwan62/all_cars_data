# 任务：left18448 第 8701-8800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0088__7a342a00


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8701-8800 行

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
left18448 第 8701-8800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8701-8800_ktype_dimension_mapping_final.tsv
- left18448_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-LEXUS-RZ-I-EB10-SUV-STANDARD-01	4805	1895	1635

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Lexus	Rz	500e Direct4	SUV	Allrad	Elektro	Oct 2025	-	802512
Lexus	Rz	550e Direct4	SUV	Allrad	Elektro	Oct 2025	-	802513
Lexus	Sc	430	Cabriolet	Heckantrieb	Benzin	May 2001	Jul 2010	15860
Lexus	Ux	300h	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	157599
Lexus	Ux	300h E-four	SUV	Allrad	Benzin/Elektro	Feb 2024	-	157598
Ligier	Ambra	0.5	Schrägheck	Frontantrieb	Diesel	Aug 1999	Dec 2006	106238
Ligier	Be up	0.5	Schrägheck	Frontantrieb	Benzin	Aug 2002	Dec 2006	18055
Ligier	Be up	0.5	Schrägheck	Frontantrieb	Diesel	Apr 2004	Dec 2006	106239
Ligier	Js50	EV	Schrägheck	Frontantrieb	Elektro	Jan 2025	-	801871
Ligier	Js50	EV	Schrägheck	Frontantrieb	Elektro	May 2025	-	802067
Ligier	Js60	0.5	Schrägheck	Frontantrieb	Diesel	Sep 2020	-	159484
Ligier	Js60	0.5	Schrägheck	Frontantrieb	Diesel	Sep 2020	-	159491
Ligier	Myli	0.5	Schrägheck	Frontantrieb	Diesel	Apr 2024	-	160385
Ligier	Myli	0.5	Schrägheck	Frontantrieb	Diesel	Apr 2024	-	801112
Ligier	Myli	EV	Schrägheck	Frontantrieb	Elektro	May 2023	-	159525
Ligier	Nova	400	Schrägheck	Frontantrieb	Benzin	Aug 2002	Dec 2008	18053
Ligier	Nova	500	Schrägheck	Frontantrieb	Diesel	Aug 2002	-	18052
Ligier	Nova	650	Schrägheck	Frontantrieb	Benzin	Aug 2002	-	18054
Lincoln	Continental	4.6	Stufenheck	Frontantrieb	Benzin	Jan 1998	Dec 2002	57905
Lincoln	Mark viii	4.6	Coupe	Heckantrieb	Benzin	Oct 1992	Dec 1998	11295
Lincoln	Town car	4.6	Stufenheck	Heckantrieb	Benzin	Sep 1990	Dec 1995	45313
Lincoln	Town car	4.6	Stufenheck	Heckantrieb	Benzin	Sep 1993	Dec 1997	115001
Lincoln	Town car	5	Stufenheck	Heckantrieb	Benzin	Sep 1985	Dec 1989	53011
Lincoln	Town car ii	4.6	Stufenheck	Heckantrieb	Benzin	Oct 1990	Dec 1997	11296
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	Oct 1997	Dec 2003	11297
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	Sep 1998	Dec 2011	13855
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	Sep 1998	Dec 2003	51204
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	Sep 2003	Dec 2008	51207
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	Sep 1997	Dec 2000	53157
Livan Auto	X3	1.5 MPI	Schrägheck	Frontantrieb	Benzin	Sep 2023	-	160544
Lloyd	Alexander	0.6	Stufenheck	Frontantrieb	Benzin	Jan 1957	Dec 1961	107920
Lloyd	Alexander	0.6	Kombi	Frontantrieb	Benzin	Jan 1957	Dec 1961	107922
Lloyd	Alexander	0.6 TS	Stufenheck	Frontantrieb	Benzin	Jan 1958	Dec 1961	107921
Lloyd	Alexander	0.6 TS	Kombi	Frontantrieb	Benzin	Jan 1958	Dec 1961	107924
Lloyd	Lc	0.4	Cabriolet	Frontantrieb	Gemisch	Jan 1953	Dec 1957	107909
Lloyd	Lc	0.6	Cabriolet	Frontantrieb	Benzin	Jan 1955	Dec 1961	107910
Lloyd	Lk	0.4	Kasten	Frontantrieb	Gemisch	Jan 1953	Dec 1957	107911
Lloyd	Lk	0.6	Kasten	Frontantrieb	Benzin	Jan 1955	Dec 1961	107913
Lloyd	Lp	0.25	Stufenheck	Frontantrieb	Gemisch	Apr 1956	Dec 1957	107898
Lloyd	Lp	0.4	Stufenheck	Frontantrieb	Gemisch	Jan 1953	Dec 1957	107904
Lloyd	Lp	0.6	Stufenheck	Frontantrieb	Benzin	Jan 1955	Dec 1961	107905
Lloyd	Ls	0.4	Kombi	Frontantrieb	Gemisch	Jan 1953	Dec 1957	107906
Lloyd	Ls	0.6	Kombi	Frontantrieb	Benzin	Jan 1955	Dec 1961	107907
Lotus	2	1.8	Cabriolet	Heckantrieb	Benzin	Apr 2007	Jul 2011	34805
Lotus	2	1.8	Cabriolet	Heckantrieb	Benzin	Apr 2007	Jul 2011	106234
Lotus	3	3.5 Road	Cabriolet	Heckantrieb	Benzin	Feb 2016	-	128117
Lotus	Elan	1.6 I 16V Turbo	Cabriolet	Frontantrieb	Benzin	Sep 1991	Nov 1995	11999
Lotus	Eletre	EV Allrad	SUV	Allrad	Elektro	Oct 2022	-	150745
Lotus	Eletre	EV Allrad	SUV	Allrad	Elektro	Oct 2022	-	150746
Lotus	Elise	1.6	Cabriolet	Heckantrieb	Benzin	Jun 2007	-	34807
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Mar 2000	Feb 2001	14660
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Nov 2000	Aug 2005	15636
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	May 2002	-	16847
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Jan 2004	-	17860
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Jun 2007	-	34808
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Jan 2004	Oct 2013	56829
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Nov 1998	Jan 2001	106237
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Nov 1998	Jan 2001	108250
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	Mar 1999	Jan 2001	108251
Lotus	Elise	Sport 240	Cabriolet	Heckantrieb	Benzin	Jan 2021	-	145186
Lotus	Emeya	EV Allrad	Schrägheck	Allrad	Elektro	Jan 2024	-	157462
Lotus	Emeya	EV Allrad	Schrägheck	Allrad	Elektro	Jan 2024	-	157463
Lotus	Emira	2	Coupe	Heckantrieb	Benzin	Nov 2021	-	145900
Lotus	Emira	2	Coupe	Heckantrieb	Benzin	Nov 2021	-	150688
Lotus	Emira	3.5	Coupe	Heckantrieb	Benzin	Jul 2022	-	148227
Lotus	Europa	2.0 Turbo	Coupe	Heckantrieb	Benzin	Sep 2008	-	34819
Lotus	Evora	3.5 400	Coupe	Heckantrieb	Benzin	Sep 2015	-	117729
Lotus	Evora	3.5 430	Coupe	Heckantrieb	Benzin	Jun 2017	-	128430
Lotus	Evora	3.5 S	Coupe	Heckantrieb	Benzin	Dec 2010	Apr 2016	7843
Lotus	Exige	1.8 16V	Coupe	Heckantrieb	Benzin	May 2000	Jul 2008	16817
Lotus	Exige	1.8 16V	Coupe	Heckantrieb	Benzin	Sep 2001	Jul 2008	16818
Lotus	Exige	1.8 CUP 260	Coupe	Heckantrieb	Benzin	Apr 2006	Jun 2012	34815
Lotus	Exige	1.8 GT3	Coupe	Heckantrieb	Benzin	Aug 2006	Jun 2012	11127
Lotus	Exige	1.8 S	Coupe	Heckantrieb	Benzin	Jan 2008	Apr 2011	100897
Lotus	Exige	3.5 350 S	Coupe	Heckantrieb	Benzin	Jun 2012	-	55601
Lotus	Exige	3.5 380	Coupe	Heckantrieb	Benzin	Nov 2016	-	127092
Lotus	Exige	3.5 390	Coupe	Heckantrieb	Benzin	Mar 2021	-	145037
Lotus	Exige	3.5 420	Coupe	Heckantrieb	Benzin	Nov 2017	-	145039
LTI	Tx	2.7 TD	Schrägheck	Heckantrieb	Diesel	Jan 1997	-	12656
Lucid	Air	EV	Stufenheck	Heckantrieb	Elektro	Mar 2024	-	157987
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	147310
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	147311
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	147312
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	147313
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	147314
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Sep 2023	-	156519
Lucid	Air	EV AWD	Stufenheck	Allrad	Elektro	Aug 2023	-	156545
Lucid	Gravity	EV Allrad	SUV	Allrad	Elektro	Sep 2025	-	162480
Lynk & CO	1	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Sep 2024	-	801092
Lynk & CO	2	EV	SUV	Heckantrieb	Elektro	Dec 2024	-	160293
Lynk & CO	8	1.5 TD Phev	SUV	Frontantrieb	Benzin/Elektro	Jun 2025	-	801804
Lynk & CO	8	Phev Allrad	SUV	Allrad	Benzin/Elektro	Sep 2023	-	156150
Mahindra	Cj 3	2.2	Geländewagen offen	Allrad	Benzin	Oct 1988	Sep 1992	10425
Mahindra	Cj 3	2.1 D Allrad	Geländewagen offen	Allrad	Diesel	Oct 1988	Sep 1992	10422
Mahindra	Cj 3	2.3 D	Geländewagen offen	Allrad	Diesel	Oct 1988	Sep 1992	10423
Mahindra	Cj 3	2.5 D	Geländewagen offen	Allrad	Diesel	Oct 1988	Sep 1992	10424
Mahindra	Cj 3 wagon	2.2	Geländewagen geschlossen	Allrad	Benzin	Oct 1988	Sep 1992	13230
Mahindra	Cj 3 wagon	2.1 D	Geländewagen geschlossen	Allrad	Diesel	Oct 1988	Sep 1992	13231
Mahindra	Cj 3 wagon	2.3 D	Geländewagen geschlossen	Allrad	Diesel	Oct 1988	Sep 1992	13232
Mahindra	Cj 3 wagon	2.5 D	Geländewagen geschlossen	Allrad	Diesel	Oct 1988	Sep 1992	13233


--- Round 1 / 首次发送 ---
## 更新点

本批按物理外廓完成聚类，动力、能源和普通配置重复项均复用既有尺寸组。仅对存在明确尺寸边界的 3 个 Ktype 派生分支：Lexus SC 430、Lincoln Town Car Ktype 13855、Lotus Elise Ktype 56829。SC 430 初期官方尺寸为 4515×1825×1370 mm；Town Car 1998 与 2003 车型的长度、高度确有变化；Elise 2011 起记录到车长由 3785 mm 变为 3824 mm。([Lexus Media Site][1])

## 进度

输入 Ktype：100
最终映射行：103
最终尺寸组：51
READY：103
PENDING：0

固定表头、列数、主键唯一性、Ktype 覆盖、尺寸组引用闭合、正整数三维、来源链接和孤立组检查均已通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
802512	802512	SUV	I	EB10	5	EU-LEXUS-RZ-I-EB10-SUV-STANDARD-01	HIGH		READY
802513	802513	SUV	I	EB10	5	EU-LEXUS-RZ-I-EB10-SUV-STANDARD-01	HIGH		READY
15860_prefl	15860	Convertible	II	Z40	2	EU-LEXUS-SC-II-CONVERTIBLE-PREFL-01	HIGH	Production span covers documented 4515 mm pre-facelift and 4535 mm facelift bodies.	READY
15860_facelift	15860	Convertible	II	Z40	2	EU-LEXUS-SC-II-CONVERTIBLE-FACELIFT-01	HIGH	Production span covers documented 4515 mm pre-facelift and 4535 mm facelift bodies.	READY
157599	157599	SUV	I	ZA10	5	EU-LEXUS-UX-I-SUV-STANDARD-01	HIGH		READY
157598	157598	SUV	I	ZA10	5	EU-LEXUS-UX-I-SUV-STANDARD-01	HIGH		READY
106238	106238	Hatchback	I		3	EU-LIGIER-AMBRA-I-HATCHBACK-STANDARD-01	MEDIUM		READY
18055	18055	Hatchback	I		0	EU-LIGIER-BE-UP-I-HATCHBACK-STANDARD-01	MEDIUM		READY
106239	106239	Hatchback	I		0	EU-LIGIER-BE-UP-I-HATCHBACK-STANDARD-01	MEDIUM		READY
801871	801871	Hatchback	II		3	EU-LIGIER-JS50-II-HATCHBACK-STANDARD-01	HIGH		READY
802067	802067	Hatchback	II		3	EU-LIGIER-JS50-II-HATCHBACK-STANDARD-01	HIGH		READY
159484	159484	Hatchback	I		3	EU-LIGIER-JS60-I-HATCHBACK-STANDARD-01	HIGH		READY
159491	159491	Hatchback	I		3	EU-LIGIER-JS60-I-HATCHBACK-STANDARD-01	HIGH		READY
160385	160385	Hatchback	I		3	EU-LIGIER-MYLI-I-HATCHBACK-STANDARD-01	HIGH		READY
801112	801112	Hatchback	I		3	EU-LIGIER-MYLI-I-HATCHBACK-STANDARD-01	HIGH		READY
159525	159525	Hatchback	I		3	EU-LIGIER-MYLI-I-HATCHBACK-STANDARD-01	HIGH		READY
18053	18053	Hatchback	I		3	EU-LIGIER-NOVA-I-HATCHBACK-STANDARD-01	MEDIUM		READY
18052	18052	Hatchback	I		3	EU-LIGIER-NOVA-I-HATCHBACK-STANDARD-01	MEDIUM		READY
18054	18054	Hatchback	I		3	EU-LIGIER-NOVA-I-HATCHBACK-STANDARD-01	MEDIUM		READY
57905	57905	Sedan	IX	FN74	4	EU-LINCOLN-CONTINENTAL-IX-SEDAN-STANDARD-01	HIGH		READY
11295	11295	Coupe	I	FN10	2	EU-LINCOLN-MARK-VIII-I-COUPE-STANDARD-01	HIGH		READY
45313	45313	Sedan	II	Panther	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-STANDARD-01	MEDIUM		READY
115001	115001	Sedan	II	Panther	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-STANDARD-01	MEDIUM		READY
53011	53011	Sedan	I	Panther	4	EU-LINCOLN-TOWN-CAR-I-SEDAN-STANDARD-01	HIGH		READY
11296	11296	Sedan	II	Panther	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-STANDARD-01	MEDIUM		READY
11297	11297	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-PRE2003-01	HIGH		READY
13855_pre03	13855	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-PRE2003-01	HIGH	Ktype span crosses the documented 2003 exterior revision; pre-2003 and 2003-plus envelopes are retained separately.	READY
13855_03plus	13855	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-2003PLUS-01	HIGH	Ktype span crosses the documented 2003 exterior revision; pre-2003 and 2003-plus envelopes are retained separately.	READY
51204	51204	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-PRE2003-01	HIGH		READY
51207	51207	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-2003PLUS-01	HIGH		READY
53157	53157	Sedan	III	Panther	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-PRE2003-01	HIGH		READY
160544	160544	Hatchback	I		5	EU-LIVAN-X3-PRO-I-HATCHBACK-STANDARD-01	HIGH		READY
107920	107920	Sedan	Alexander		2	EU-LLOYD-600-I-SEDAN-STANDARD-01	MEDIUM		READY
107922	107922	Wagon	Alexander		3	EU-LLOYD-600-I-WAGON-STANDARD-01	MEDIUM		READY
107921	107921	Sedan	Alexander		2	EU-LLOYD-600-I-SEDAN-STANDARD-01	MEDIUM		READY
107924	107924	Wagon	Alexander		3	EU-LLOYD-600-I-WAGON-STANDARD-01	MEDIUM		READY
107909	107909	Convertible	400	LC400	2	EU-LLOYD-400-I-CONVERTIBLE-STANDARD-01	MEDIUM		READY
107910	107910	Convertible	600	LC600	2	EU-LLOYD-600-I-CONVERTIBLE-STANDARD-01	MEDIUM		READY
107911	107911	Van	400	LK400	3	EU-LLOYD-400-I-VAN-STANDARD-01	MEDIUM		READY
107913	107913	Van	600	LK600	3	EU-LLOYD-600-I-VAN-STANDARD-01	MEDIUM		READY
107898	107898	Sedan	250	LP250	2	EU-LLOYD-400-I-SEDAN-STANDARD-01	MEDIUM		READY
107904	107904	Sedan	400	LP400	2	EU-LLOYD-400-I-SEDAN-STANDARD-01	MEDIUM		READY
107905	107905	Sedan	600	LP600	2	EU-LLOYD-600-I-SEDAN-STANDARD-01	MEDIUM		READY
107906	107906	Wagon	400	LS400	3	EU-LLOYD-400-I-WAGON-STANDARD-01	MEDIUM		READY
107907	107907	Wagon	600	LS600	3	EU-LLOYD-600-I-WAGON-STANDARD-01	MEDIUM		READY
34805	34805	Convertible	I	Type 111	2	EU-LOTUS-2-ELEVEN-I-CONVERTIBLE-STANDARD-01	HIGH		READY
106234	106234	Convertible	I	Type 111	2	EU-LOTUS-2-ELEVEN-I-CONVERTIBLE-STANDARD-01	HIGH		READY
128117	128117	Convertible	I		2	EU-LOTUS-3-ELEVEN-I-CONVERTIBLE-ROAD-01	MEDIUM		READY
11999	11999	Convertible	M100	M100	2	EU-LOTUS-ELAN-M100-CONVERTIBLE-STANDARD-01	HIGH		READY
150745	150745	SUV	I	Type 132	5	EU-LOTUS-ELETRE-I-SUV-STANDARD-01	HIGH		READY
150746	150746	SUV	I	Type 132	5	EU-LOTUS-ELETRE-I-SUV-STANDARD-01	HIGH		READY
34807	34807	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH		READY
14660	14660	Convertible	S1	Type 111	2	EU-LOTUS-ELISE-S1-CONVERTIBLE-STANDARD-01	HIGH		READY
15636	15636	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH		READY
16847	16847	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH		READY
17860	17860	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH		READY
34808	34808	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH		READY
56829_pre2011	56829	Convertible	S2	Type 111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	HIGH	Ktype span crosses the documented 2011 exterior-length change from 3785 mm to 3824 mm.	READY
56829_2011plus	56829	Convertible	S3	Type 111	2	EU-LOTUS-ELISE-S3-CONVERTIBLE-STANDARD-01	HIGH	Ktype span crosses the documented 2011 exterior-length change from 3785 mm to 3824 mm.	READY
106237	106237	Convertible	S1	Type 111	2	EU-LOTUS-ELISE-S1-CONVERTIBLE-STANDARD-01	HIGH		READY
108250	108250	Convertible	S1	Type 111	2	EU-LOTUS-ELISE-S1-CONVERTIBLE-STANDARD-01	HIGH		READY
108251	108251	Convertible	S1	Type 111	2	EU-LOTUS-ELISE-S1-CONVERTIBLE-STANDARD-01	HIGH		READY
145186	145186	Convertible	S3	Type 111	2	EU-LOTUS-ELISE-S3-CONVERTIBLE-STANDARD-01	HIGH		READY
157462	157462	Hatchback	I	Type 133	5	EU-LOTUS-EMEYA-I-HATCHBACK-STANDARD-01	HIGH		READY
157463	157463	Hatchback	I	Type 133	5	EU-LOTUS-EMEYA-I-HATCHBACK-STANDARD-01	HIGH		READY
145900	145900	Coupe	I	Type 131	2	EU-LOTUS-EMIRA-I-COUPE-STANDARD-01	HIGH		READY
150688	150688	Coupe	I	Type 131	2	EU-LOTUS-EMIRA-I-COUPE-STANDARD-01	HIGH		READY
148227	148227	Coupe	I	Type 131	2	EU-LOTUS-EMIRA-I-COUPE-STANDARD-01	HIGH		READY
34819	34819	Coupe	Europa S	Type 121	2	EU-LOTUS-EUROPA-S-COUPE-STANDARD-01	HIGH		READY
117729	117729	Coupe	I	Type 122	2	EU-LOTUS-EVORA-I-COUPE-400-01	HIGH		READY
128430	128430	Coupe	I	Type 122	2	EU-LOTUS-EVORA-I-COUPE-430-01	MEDIUM		READY
7843	7843	Coupe	I	Type 122	2	EU-LOTUS-EVORA-I-COUPE-PREFL-01	HIGH		READY
16817	16817	Coupe	S1	Type 111	2	EU-LOTUS-EXIGE-S1-COUPE-STANDARD-01	HIGH		READY
16818	16818	Coupe	S2	Type 111	2	EU-LOTUS-EXIGE-S2-COUPE-STANDARD-01	HIGH		READY
34815	34815	Coupe	S2	Type 111	2	EU-LOTUS-EXIGE-S2-COUPE-STANDARD-01	HIGH		READY
11127	11127	Coupe	S2	Type 111	2	EU-LOTUS-EXIGE-S2-COUPE-STANDARD-01	HIGH		READY
100897	100897	Coupe	S2	Type 111	2	EU-LOTUS-EXIGE-S2-COUPE-STANDARD-01	HIGH		READY
55601	55601	Coupe	S3	Type 117	2	EU-LOTUS-EXIGE-S3-COUPE-EARLY-01	HIGH		READY
127092	127092	Coupe	S3	Type 117	2	EU-LOTUS-EXIGE-S3-COUPE-FINAL-01	HIGH		READY
145037	145037	Coupe	S3	Type 117	2	EU-LOTUS-EXIGE-S3-COUPE-FINAL-01	HIGH		READY
145039	145039	Coupe	S3	Type 117	2	EU-LOTUS-EXIGE-S3-COUPE-FINAL-01	HIGH		READY
12656	12656	Hatchback	TX1		4	EU-LTI-TX1-I-HATCHBACK-STANDARD-01	MEDIUM		READY
157987	157987	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
147310	147310	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
147311	147311	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
147312	147312	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
147313	147313	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
147314	147314	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
156519	156519	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
156545	156545	Sedan	I		4	EU-LUCID-AIR-I-SEDAN-STANDARD-01	HIGH		READY
162480	162480	SUV	I		5	EU-LUCID-GRAVITY-I-SUV-STANDARD-01	HIGH		READY
801092	801092	SUV	I facelift		5	EU-LYNK-CO-01-I-SUV-MY25-01	HIGH		READY
160293	160293	SUV	I		5	EU-LYNK-CO-02-I-SUV-STANDARD-01	HIGH		READY
801804	801804	SUV	I facelift		5	EU-LYNK-CO-08-I-SUV-FACELIFT-01	HIGH		READY
156150	156150	SUV	I		5	EU-LYNK-CO-08-I-SUV-PREFL-01	HIGH		READY
10425	10425	SUV	I	CJ3	2	EU-MAHINDRA-CJ3-I-SUV-OPEN-01	MEDIUM		READY
10422	10422	SUV	I	CJ3	2	EU-MAHINDRA-CJ3-I-SUV-OPEN-01	MEDIUM		READY
10423	10423	SUV	I	CJ3	2	EU-MAHINDRA-CJ3-I-SUV-OPEN-01	MEDIUM		READY
10424	10424	SUV	I	CJ3	2	EU-MAHINDRA-CJ3-I-SUV-OPEN-01	MEDIUM		READY
13230	13230	SUV	I	CJ3 Wagon	3	EU-MAHINDRA-CJ3-I-SUV-WAGON-01	MEDIUM	Closed wagon body is retained separately from the open CJ3 body.	READY
13231	13231	SUV	I	CJ3 Wagon	3	EU-MAHINDRA-CJ3-I-SUV-WAGON-01	MEDIUM	Closed wagon body is retained separately from the open CJ3 body.	READY
13232	13232	SUV	I	CJ3 Wagon	3	EU-MAHINDRA-CJ3-I-SUV-WAGON-01	MEDIUM	Closed wagon body is retained separately from the open CJ3 body.	READY
13233	13233	SUV	I	CJ3 Wagon	3	EU-MAHINDRA-CJ3-I-SUV-WAGON-01	MEDIUM	Closed wagon body is retained separately from the open CJ3 body.	READY
```

[下载 left18448_8701-8800_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_8701-8800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LEXUS-RZ-I-EB10-SUV-STANDARD-01	4805	1895	1635	Lexus Europe newsroom – all-new RZ dimensions	https://newsroom.lexus.eu/world-premiere-of-the-all-new-lexus-rz/
EU-LEXUS-SC-II-CONVERTIBLE-PREFL-01	4515	1825	1370	Lexus Media UK – SC 430 launch pack	https://media.lexus.co.uk/sc-430-launch-pack-july-2001/
EU-LEXUS-SC-II-CONVERTIBLE-FACELIFT-01	4535	1825	1370	Automobile-Catalog – 2006 Lexus SC 430	https://www.automobile-catalog.com/car/2006/1425830/lexus_sc_430.html
EU-LEXUS-UX-I-SUV-STANDARD-01	4495	1840	1520	Lexus Europe newsroom – UX technical dimensions	https://newsroom.lexus.eu/world-debut-of-the-lexus-ux-a-new-genre-of-crossover/
EU-LIGIER-AMBRA-I-HATCHBACK-STANDARD-01	2470	1400	1520	Auta5P – Ligier Ambra	https://auta5p.eu/lang/en/katalog/auto.php?idf=Ligier-Ambra-8468
EU-LIGIER-BE-UP-I-HATCHBACK-STANDARD-01	2680	1410	1560	Auta5P – Ligier Be Up	https://auta5p.eu/lang/en/katalog/auto.php?idf=Ligier-Be-Up-8469
EU-LIGIER-JS50-II-HATCHBACK-STANDARD-01	2972	1499	1503	Ligier Latvia – New JS50 specifications	https://www.ligier.lv/product/new-js50/
EU-LIGIER-JS60-I-HATCHBACK-STANDARD-01	2992	1500	1537	Ligier Latvia – JS60 specifications	https://www.ligier.lv/product/js60/
EU-LIGIER-MYLI-I-HATCHBACK-STANDARD-01	2958	1499	1541	Ligier Latvia – Myli specifications	https://www.ligier.lv/product/myli/
EU-LIGIER-NOVA-I-HATCHBACK-STANDARD-01	2670	1440	1540	AutoKatalog – Ligier Nova 650 generation	https://autokatalog.pl/ligier/nova-650/i
EU-LINCOLN-CONTINENTAL-IX-SEDAN-STANDARD-01	5258	1869	1422	Edmunds – 1998 Lincoln Continental specifications	https://www.edmunds.com/lincoln/continental/1998/features-specs/
EU-LINCOLN-MARK-VIII-I-COUPE-STANDARD-01	5255	1895	1361	Edmunds – 1993 Lincoln Mark VIII specifications	https://www.edmunds.com/lincoln/mark-viii/1993/features-specs/
EU-LINCOLN-TOWN-CAR-II-SEDAN-STANDARD-01	5593	1984	1440	Edmunds – 1990 Lincoln Town Car specifications	https://www.edmunds.com/lincoln/town-car/1990/features-specs/
EU-LINCOLN-TOWN-CAR-I-SEDAN-STANDARD-01	5563	1984	1420	Automobile-Catalog – 1985 Lincoln Town Car	https://www.automobile-catalog.com/car/1985/1413860/lincoln_town_car.html
EU-LINCOLN-TOWN-CAR-III-SEDAN-PRE2003-01	5469	1986	1473	Edmunds – 1998 Lincoln Town Car specifications	https://www.edmunds.com/lincoln/town-car/1998/features-specs/
EU-LINCOLN-TOWN-CAR-III-SEDAN-2003PLUS-01	5471	1986	1499	Edmunds – 2003 Lincoln Town Car specifications	https://www.edmunds.com/lincoln/town-car/2003/features-specs/
EU-LIVAN-X3-PRO-I-HATCHBACK-STANDARD-01	4005	1760	1575	Auto-Data – Livan X3 Pro 1.5	https://www.auto-data.net/en/livan-x3-pro-1.5-113hp-53957
EU-LLOYD-600-I-SEDAN-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd Alexander sedan dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/600-alexander/1generation/349488/
EU-LLOYD-600-I-WAGON-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd Alexander wagon dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/600-alexander/1generation/349489/
EU-LLOYD-400-I-CONVERTIBLE-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd LC 400 dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/400/1generation/349484/
EU-LLOYD-600-I-CONVERTIBLE-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd LC 600 dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/600-alexander/1generation/349487/
EU-LLOYD-400-I-VAN-STANDARD-01	3355	1410	1400	Lloyd 400 model overview and exterior dimensions	https://en.wikipedia.org/wiki/Lloyd_400
EU-LLOYD-600-I-VAN-STANDARD-01	3355	1410	1400	Lloyd 600 model overview and exterior dimensions	https://en.wikipedia.org/wiki/Lloyd_600
EU-LLOYD-400-I-SEDAN-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd LP 400 dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/400/1generation/349482/
EU-LLOYD-400-I-WAGON-STANDARD-01	3355	1410	1400	ADAC Autokatalog – Lloyd LS 400 dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/lloyd/400/1generation/349483/
EU-LOTUS-2-ELEVEN-I-CONVERTIBLE-STANDARD-01	3822	1709	1112	Lotus 2-Eleven service notes – dimensions excluding mirrors	https://manuals.plus/m/b2955df0d9cb6b5f95ab8fbe40cdfb959a2ec7c568388b386c047ac432df9655
EU-LOTUS-3-ELEVEN-I-CONVERTIBLE-ROAD-01	4120	1860	1200	Carsales – 2017 Lotus 3-Eleven dimensions	https://www.carsales.com.au/research/lotus/3-eleven/2017/
EU-LOTUS-ELAN-M100-CONVERTIBLE-STANDARD-01	3803	1734	1230	Automobile-Catalog – 1991 Lotus Elan SE	https://www.automobile-catalog.com/car/1991/1435595/lotus_elan_se.html
EU-LOTUS-ELETRE-I-SUV-STANDARD-01	5103	2019	1630	CarExpert New Zealand – Lotus Eletre exterior dimensions	https://www.carexpert.co.nz/lotus/eletre/base/exterior-and-dimensions
EU-LOTUS-ELISE-S2-CONVERTIBLE-STANDARD-01	3785	1719	1117	Toyota GAZOO catalog – Lotus Elise S	https://gazoo.com/catalog/maker/LOTUS/ELISE/199909/10035800/
EU-LOTUS-ELISE-S1-CONVERTIBLE-STANDARD-01	3726	1701	1148	Elises.co.uk – Lotus Elise S1 dimensions excluding mirrors	https://www.elises.co.uk/models/s1/index.html
EU-LOTUS-ELISE-S3-CONVERTIBLE-STANDARD-01	3824	1719	1117	Automobile-Catalog – 2011 Lotus Elise	https://www.automobile-catalog.com/car/2011/1436585/lotus_elise.html
EU-LOTUS-EMEYA-I-HATCHBACK-STANDARD-01	5139	2005	1459	Lotus Poland – Emeya dimensions	https://lotuspoland.com/en/emeya
EU-LOTUS-EMIRA-I-COUPE-STANDARD-01	4412	1895	1224	Car and Driver – Lotus Emira dimensions without mirrors	https://www.caranddriver.com/lotus/emira/specs
EU-LOTUS-EUROPA-S-COUPE-STANDARD-01	3900	1714	1120	Carsales – 2008 Lotus Europa dimensions	https://www.carsales.com.au/research/lotus/europa/2008/
EU-LOTUS-EVORA-I-COUPE-400-01	4384	1844	1229	Edmunds – 2017 Lotus Evora 400 specifications	https://www.edmunds.com/lotus/evora-400/2017/features-specs/
EU-LOTUS-EVORA-I-COUPE-430-01	4394	1844	1229	AutoEvolution – Lotus Evora GT430	https://www.autoevolution.com/cars/lotus-evora-gt430-2017.html
EU-LOTUS-EVORA-I-COUPE-PREFL-01	4342	1848	1223	VehicleScore – Lotus Evora dimensions	https://vehiclescore.co.uk/car-dimensions-check/lotus/evora
EU-LOTUS-EXIGE-S1-COUPE-STANDARD-01	3761	1730	1201	EncyCARpedia – Lotus Exige S1 dimensions	https://www.encycarpedia.com/lotus/00-exige-targa
EU-LOTUS-EXIGE-S2-COUPE-STANDARD-01	3785	1719	1117	CarsGuide – 2008 Lotus Exige dimensions	https://www.carsguide.com.au/lotus/exige/car-dimensions/2008
EU-LOTUS-EXIGE-S3-COUPE-EARLY-01	4052	1802	1153	NetCarShow – 2012 Lotus Exige S technical data	https://www.netcarshow.com/lotus/2012-exige_s/
EU-LOTUS-EXIGE-S3-COUPE-FINAL-01	4084	1802	1129	Lotus Antwerp – Exige Sport 420 Final Edition specifications	https://lotusantwerp.be/new-lotus-exige-sport-420-final-edition/
EU-LTI-TX1-I-HATCHBACK-STANDARD-01	4580	1800	1830	Automobile-Catalog – 2001 LTI TX1	https://www.automobile-catalog.com/car/2001/338690/lti_tx1_automatic.html
EU-LUCID-AIR-I-SEDAN-STANDARD-01	4976	1935	1407	Car and Driver – Lucid Air dimensions without mirrors	https://www.caranddriver.com/lucid-motors/air/specs
EU-LUCID-GRAVITY-I-SUV-STANDARD-01	5034	2004	1656	Car and Driver – Lucid Gravity dimensions without mirrors	https://www.caranddriver.com/lucid/gravity/specs
EU-LYNK-CO-01-I-SUV-MY25-01	4545	1860	1694	Lynk & Co – 01 features and dimensions	https://www.lynkco.com/fr-be/cars/01/features
EU-LYNK-CO-02-I-SUV-STANDARD-01	4460	1845	1573	Lynk & Co Philippines – 02 specifications	https://lynkco.ph/02-e-suv/
EU-LYNK-CO-08-I-SUV-FACELIFT-01	4825	1915	1660	Lynk & Co China – 08 specifications	https://www.lynkco.com.cn/cars/08
EU-LYNK-CO-08-I-SUV-PREFL-01	4820	1915	1685	Lynk & Co Vietnam – 08 comparison specifications	https://lynkco.com.vn/en/comparison?cars=21%2C23
EU-MAHINDRA-CJ3-I-SUV-OPEN-01	3299	1740	1720	Drive.Place – Mahindra CJ-3 open-body dimensions	https://mahindra.drive.place/cj_3/i/group_vezdehod/407372
EU-MAHINDRA-CJ3-I-SUV-WAGON-01	3299	1740	1720	Auto-Data – Mahindra CJ 3 Wagon generation	https://www.auto-data.net/en/mahindra-cj-3-wagon-generation-2058
```

[下载 left18448_8701-8800_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_8701-8800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.lexus.co.uk/sc-430-launch-pack-july-2001/ "https://media.lexus.co.uk/sc-430-launch-pack-july-2001/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6376 行）
- 累计尺寸组：dimension_groups_final.tsv（1811 行）

