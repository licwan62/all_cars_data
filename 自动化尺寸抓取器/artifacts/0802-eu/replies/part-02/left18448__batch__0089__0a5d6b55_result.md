# 任务：left18448 第 8801-8900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0089__0a5d6b55


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 8801-8900 行

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
left18448 第 8801-8900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_8801-8900_ktype_dimension_mapping_final.tsv
- left18448_8801-8900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mahindra	Goa	2.2 Crde AWD	Geländewagen geschlossen	Allrad	Diesel	Jan 2010	-	126179
Mahindra	Kuv100	1.2 VVT LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2020	-	154491
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	Feb 2017	Jun 2024	126571
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	Feb 2017	-	126572
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	Feb 2017	-	126573
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	Jun 2024	126581
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	-	126582
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2016	-	126583
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	Nov 2022	-	151828
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2022	-	151862
MAN	Tge	2.0 TDI AWD	Kasten	Allrad	Diesel	Apr 2017	-	126577
MAN	Tge	2.0 TDI AWD	Kasten	Allrad	Diesel	Mar 2017	-	126578
MAN	Tge	2.0 TDI AWD	Kasten	Allrad	Diesel	Nov 2022	-	151830
MAN	Tge	2.0 TDI AWD	Pritsche/Fahrgestell	Allrad	Diesel	Nov 2022	-	151863
MAN	Tge	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	Mar 2023	-	150629
MAN	Tge	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2023	-	150720
Maserati	228	2.8	Coupe	Heckantrieb	Benzin	Aug 1986	Jun 1993	57264
Maserati	3200 gt	3.2 Biturbo V8 32V	Coupe	Heckantrieb	Benzin	Oct 1998	Mar 2002	10301
Maserati	4200 gt /	4.2	Coupe	Heckantrieb	Benzin	Mar 2002	Dec 2007	16566
Maserati	4200 gt /	4.2	Coupe	Heckantrieb	Benzin	May 2002	Nov 2007	116191
Maserati	Ghibli	3	Stufenheck	Heckantrieb	Benzin	Aug 2013	-	38888
Maserati	Ghibli	3	Stufenheck	Heckantrieb	Benzin	Aug 2013	-	107361
Maserati	Ghibli	2.0 24V Biturbo	Coupe	Heckantrieb	Benzin	Jan 1996	Dec 1997	122015
Maserati	Ghibli	2.8 24V Biturbo	Coupe	Heckantrieb	Benzin	Jun 1992	Dec 1997	14889
Maserati	Ghibli	3.0 D	Stufenheck	Heckantrieb	Diesel	Aug 2013	-	38882
Maserati	Ghibli	3.0 D	Stufenheck	Heckantrieb	Diesel	Aug 2013	-	39221
Maserati	Ghibli	3.0 S	Stufenheck	Heckantrieb	Benzin	Aug 2013	-	38893
Maserati	Ghibli	3.0 S Q4	Stufenheck	Allrad	Benzin	Aug 2013	-	18237
Maserati	Ghibli	3.8 V8	Stufenheck	Heckantrieb	Benzin	Oct 2020	-	143003
Maserati	Gran turismo i	4.2	Coupe	Heckantrieb	Benzin	Jan 2013	-	59478
Maserati	Gran turismo i	4.7	Coupe	Heckantrieb	Benzin	Sep 2010	-	56221
Maserati	Gran turismo i	4.7	Coupe	Heckantrieb	Benzin	May 2012	-	59479
Maserati	Gran turismo ii	Folgore Q4	Coupe	Allrad	Elektro	Dec 2023	-	157197
Maserati	Gran turismo ii	Modena	Coupe	Allrad	Benzin	Jan 2023	-	152619
Maserati	Gran turismo ii	Trofeo	Coupe	Allrad	Benzin	Jan 2023	-	152620
Maserati	Grancabrio	4.7	Cabriolet	Heckantrieb	Benzin	Jun 2010	Jan 2013	54954
Maserati	Grancabrio	4.7	Cabriolet	Heckantrieb	Benzin	Jan 2011	Jun 2017	56218
Maserati	Grancabrio	4.7	Cabriolet	Heckantrieb	Benzin	Feb 2013	Nov 2019	59480
Maserati	Grancabrio	Folgore	Cabriolet	Allrad	Elektro	Oct 2023	-	158769
Maserati	Grancabrio	Modena	Cabriolet	Allrad	Benzin	Mar 2024	-	801494
Maserati	Grancabrio	Trofeo	Cabriolet	Allrad	Benzin	Mar 2024	-	158124
Maserati	Grecale	Folgore Q4	SUV	Allrad	Elektro	Jul 2023	-	155924
Maserati	Grecale	Folgore Q4	SUV	Allrad	Elektro	Dec 2023	-	157195
Maserati	Grecale	GT Mild Hybrid Q4	SUV	Allrad	Benzin/Elektro	Apr 2022	-	147474
Maserati	Grecale	GT Mild Hybrid Q4	SUV	Allrad	Benzin/Elektro	Apr 2025	-	801805
Maserati	Grecale	Modena Mild Hybrid Q4	SUV	Allrad	Benzin/Elektro	Apr 2022	-	147475
Maserati	Grecale	Trofeo Q4	SUV	Allrad	Benzin	Apr 2022	-	147476
Maserati	Levante	2.0 GT Mild Hybrid Q4	SUV	Allrad	Benzin/Elektro	Aug 2021	-	145291
Maserati	Levante	3.0 D Q4	SUV	Allrad	Diesel	Jun 2016	-	120566
Maserati	Mc 12	6	Coupe	Heckantrieb	Benzin	Aug 2004	-	18266
Maserati	Mc 20	3	Coupe	Heckantrieb	Benzin	Sep 2020	-	145033
Maserati	Mc 20	3.0 GT2 Stradale	Coupe	Heckantrieb	Benzin	Sep 2024	-	801065
Maserati	Mc 20	Cielo	Cabriolet	Heckantrieb	Benzin	May 2022	-	147795
Maserati	Mcpura	3	Coupe	Heckantrieb	Benzin	Jul 2025	-	162326
Maserati	Mcpura	Cielo	Cabriolet	Heckantrieb	Benzin	Jul 2025	-	162327
Maserati	Mistral	3.7	Coupe	Heckantrieb	Benzin	Sep 1963	Dec 1970	45414
Maserati	Mistral	4	Coupe	Heckantrieb	Benzin	Sep 1966	Dec 1970	45415
Maserati	Quattroporte i	4.1	Stufenheck	Heckantrieb	Benzin	Sep 1962	Dec 1970	108018
Maserati	Quattroporte ii	3	Stufenheck	Frontantrieb	Benzin	Oct 1974	Dec 1978	108017
Maserati	Quattroporte iv	3.2 V8 32V	Stufenheck	Heckantrieb	Benzin	Dec 1995	May 2001	14727
Maserati	Quattroporte v	4.2	Stufenheck	Heckantrieb	Benzin	Mar 2004	-	17882
Maserati	Quattroporte v	4.2	Stufenheck	Heckantrieb	Benzin	Sep 2004	Dec 2012	124175
Maserati	Quattroporte v	4.7 GT S	Stufenheck	Heckantrieb	Benzin	Nov 2011	-	53160
Maserati	Quattroporte vi	3	Stufenheck	Heckantrieb	Benzin	Mar 2013	-	100091
Maserati	Quattroporte vi	3	Stufenheck	Heckantrieb	Benzin	Oct 2016	-	126475
Maserati	Quattroporte vi	3.0 D	Stufenheck	Heckantrieb	Diesel	Sep 2013	-	53262
Maserati	Quattroporte vi	3.0 D	Stufenheck	Heckantrieb	Diesel	Sep 2013	-	53270
Maserati	Quattroporte vi	3.0 S	Stufenheck	Heckantrieb	Benzin	May 2013	-	52450
Maserati	Quattroporte vi	3.0 S	Stufenheck	Heckantrieb	Benzin	Nov 2016	-	123925
Maserati	Quattroporte vi	3.0 S Q4	Stufenheck	Allrad	Benzin	May 2013	-	52434
Maserati	Quattroporte vi	3.8 GT S	Stufenheck	Heckantrieb	Benzin	Jan 2013	-	59796
Maserati	Quattroporte vi	3.8 V8	Stufenheck	Heckantrieb	Benzin	Oct 2020	-	143010
Maxus	Deliver 7	2	Kasten	Frontantrieb	Diesel	Oct 2024	-	801058
Maxus	Deliver 7	2	Kasten	Frontantrieb	Diesel	Jan 2026	-	803436
Maxus	Deliver 9	2.0 D	Kasten	Heckantrieb	Diesel	Jan 2022	-	147446
Maxus	Deliver 9	2.0 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2022	-	147447
Maxus	Deliver 9	2.0 D FWD	Kasten	Frontantrieb	Diesel	Jul 2020	-	147610
Maxus	Deliver 9	2.0 D FWD	Kasten	Frontantrieb	Diesel	Jan 2022	-	152748
Maxus	Edeliver 3	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Oct 2022	-	150910
Maxus	Edeliver 3	Electric	Kasten	Frontantrieb	Elektro	Jun 2024	-	801123
Maxus	Edeliver 3	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jun 2024	-	801124
Maxus	Edeliver 5	EV	Kasten	Frontantrieb	Elektro	Jul 2024	-	157297
Maxus	Edeliver 7	Electric	Kasten	Frontantrieb	Elektro	Dec 2023	-	156890
Maxus	Edeliver 7	Electric 4X4	Kasten	Allrad	Elektro	Oct 2024	-	158794
Maxus	Edeliver 9	Electric	Kasten	Frontantrieb	Elektro	Jul 2020	-	143649
Maxus	Edeliver 9	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Oct 2022	-	150926
Maxus	Eterron 9	EV 102	Pick-up	Allrad	Elektro	Nov 2024	-	160052
Maxus	Euniq 5 van	EV	Kasten/Großraumlimousine	Frontantrieb	Elektro	May 2020	-	150845
Maxus	Mifa 7	EV	Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	156078
Maxus	Mifa 9	EV	Großraumlimousine	Frontantrieb	Elektro	Mar 2023	-	145981
Maxus	T60 max	2.0 D 4X4	Pick-up	Allrad	Diesel	Oct 2024	-	801299
Maxus	T90	EV	Pick-up	Heckantrieb	Elektro	Mar 2021	-	143943
Maxus	V80	Ev80	Bus	Frontantrieb	Elektro	Jan 2017	-	149896
Maybach	57	5.5	Stufenheck	Heckantrieb	Benzin	Sep 2002	Dec 2012	16803
Maybach	57	6	Stufenheck	Heckantrieb	Benzin	Jun 2009	Dec 2012	10873
Maybach	57	6	Stufenheck	Heckantrieb	Benzin	Jan 2011	Dec 2012	56202
Maybach	57	S 6.0	Stufenheck	Heckantrieb	Benzin	Sep 2005	Dec 2012	18978
Mazda	2	1.2	Schrägheck	Frontantrieb	Benzin	Apr 2003	Jun 2007	17317
Mazda	2	1.4	Schrägheck	Frontantrieb	Benzin	Apr 2003	Jun 2007	17104
Mazda	2	1.5	Schrägheck	Frontantrieb	Benzin	Aug 2014	-	109546


--- Round 1 / 首次发送 ---
## 更新点

完成全部映射与尺寸组闭合。MAN TGE 标准厢式/底盘尺寸采用官方技术资料；MAXUS eDeliver 3、eDeliver 9 使用对应规格表，并确认车身宽度口径。([MAN Global][1])

仅对存在明确外廓变化的 5 个跨改款 Ktype 派生分支：Maserati Quattroporte V 的 `17882`、`124175`，以及 Maybach 57 的 `16803`、`10873`、`18978`。

## 进度

* 输入 Ktype：100
* 最终映射行：105
* DIMENSION_GROUP：54
* READY：105
* PENDING：0
* 映射引用闭合：通过
* ID 唯一性：通过
* 三维、来源和 URL 非空检查：通过
* 孤立尺寸组：0

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126179	126179	SUV	I	SCORPIO	5	EU-MAHINDRA-GOA-I-SUV-STD-01	MEDIUM		READY
154491	154491	SUV	I	KUV100 NXT	5	EU-MAHINDRA-KUV100-I-SUV-NXT-01	HIGH		READY
126571	126571	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
126572	126572	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
126573	126573	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
126581	126581	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
126582	126582	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
126583	126583	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
151828	151828	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
151862	151862	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
126577	126577	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
126578	126578	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
151830	151830	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
151863	151863	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
150629	150629	Van	I			EU-MAN-TGE-I-VAN-STD-01	MEDIUM	输入未标轴距/车顶，采用标准量产厢式外廓	READY
150720	150720	Pickup	I			EU-MAN-TGE-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准量产底盘驾驶室外廓	READY
57264	57264	Coupe	I	AM334	2	EU-MASERATI-228-I-COUPE-STD-01	HIGH		READY
10301	10301	Coupe	I	AM338	2	EU-MASERATI-3200GT-I-COUPE-STD-01	HIGH		READY
16566	16566	Coupe	I	M138	2	EU-MASERATI-4200GT-I-COUPE-STD-01	HIGH		READY
116191	116191	Coupe	I	M138	2	EU-MASERATI-4200GT-I-COUPE-STD-01	HIGH		READY
38888	38888	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
107361	107361	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
122015	122015	Coupe	II	AM336	2	EU-MASERATI-GHIBLI-II-COUPE-20-01	HIGH	同代动力版本资料显示标准车高不同，分别建组	READY
14889	14889	Coupe	II	AM336	2	EU-MASERATI-GHIBLI-II-COUPE-28-01	HIGH	同代动力版本资料显示标准车高不同，分别建组	READY
38882	38882	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
39221	39221	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
38893	38893	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
18237	18237	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
143003	143003	Sedan	III	M157	4	EU-MASERATI-GHIBLI-III-SEDAN-STD-01	HIGH		READY
59478	59478	Coupe	I	M145	2	EU-MASERATI-GRANTURISMO-I-COUPE-STD-01	HIGH		READY
56221	56221	Coupe	I	M145	2	EU-MASERATI-GRANTURISMO-I-COUPE-STD-01	HIGH		READY
59479	59479	Coupe	I	M145	2	EU-MASERATI-GRANTURISMO-I-COUPE-STD-01	HIGH		READY
157197	157197	Coupe	II	M189	2	EU-MASERATI-GRANTURISMO-II-COUPE-MODENA-FOLGORE-01	HIGH		READY
152619	152619	Coupe	II	M189	2	EU-MASERATI-GRANTURISMO-II-COUPE-MODENA-FOLGORE-01	HIGH		READY
152620	152620	Coupe	II	M189	2	EU-MASERATI-GRANTURISMO-II-COUPE-TROFEO-01	HIGH	官方规格显示 Trofeo 车长与 Modena/Folgore 不同	READY
54954	54954	Convertible	I	M145	2	EU-MASERATI-GRANCABRIO-I-CONVERTIBLE-STD-01	HIGH		READY
56218	56218	Convertible	I	M145	2	EU-MASERATI-GRANCABRIO-I-CONVERTIBLE-STD-01	HIGH		READY
59480	59480	Convertible	I	M145	2	EU-MASERATI-GRANCABRIO-I-CONVERTIBLE-STD-01	HIGH		READY
158769	158769	Convertible	II	M189	2	EU-MASERATI-GRANCABRIO-II-CONVERTIBLE-STD-01	HIGH		READY
801494	801494	Convertible	II	M189	2	EU-MASERATI-GRANCABRIO-II-CONVERTIBLE-STD-01	HIGH		READY
158124	158124	Convertible	II	M189	2	EU-MASERATI-GRANCABRIO-II-CONVERTIBLE-STD-01	HIGH		READY
155924	155924	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-FOLGORE-01	HIGH		READY
157195	157195	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-FOLGORE-01	HIGH		READY
147474	147474	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-GT-01	HIGH		READY
801805	801805	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-GT-01	HIGH		READY
147475	147475	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-MODENA-01	HIGH		READY
147476	147476	SUV	I	M182	5	EU-MASERATI-GRECALE-I-SUV-TROFEO-01	HIGH		READY
145291	145291	SUV	I	M161	5	EU-MASERATI-LEVANTE-I-SUV-STD-01	MEDIUM		READY
120566	120566	SUV	I	M161	5	EU-MASERATI-LEVANTE-I-SUV-STD-01	MEDIUM		READY
18266	18266	Coupe	I	M144S	2	EU-MASERATI-MC12-I-COUPE-STD-01	HIGH		READY
145033	145033	Coupe	I	M240	2	EU-MASERATI-MC20-I-COUPE-STD-01	HIGH		READY
801065	801065	Coupe	I	M240	2	EU-MASERATI-MC20-I-COUPE-GT2-01	HIGH		READY
147795	147795	Convertible	I	M240	2	EU-MASERATI-MC20-I-CONVERTIBLE-CIELO-01	HIGH		READY
162326	162326	Coupe	I	M240	2	EU-MASERATI-MCPURA-I-COUPE-STD-01	HIGH		READY
162327	162327	Convertible	I	M240	2	EU-MASERATI-MCPURA-I-CONVERTIBLE-CIELO-01	HIGH		READY
45414	45414	Coupe	I	AM109	2	EU-MASERATI-MISTRAL-I-COUPE-STD-01	HIGH		READY
45415	45415	Coupe	I	AM109	2	EU-MASERATI-MISTRAL-I-COUPE-STD-01	HIGH		READY
108018	108018	Sedan	I	AM107	4	EU-MASERATI-QUATTROPORTE-I-SEDAN-STD-01	HIGH		READY
108017	108017	Sedan	II	AM123	4	EU-MASERATI-QUATTROPORTE-II-SEDAN-STD-01	HIGH		READY
14727	14727	Sedan	IV	AM337	4	EU-MASERATI-QUATTROPORTE-IV-SEDAN-STD-01	HIGH		READY
17882_prefl	17882	Sedan	V	M139	4	EU-MASERATI-QUATTROPORTE-V-SEDAN-PREFL-01	HIGH	Ktype 跨越改款且车长有明确变化；本行为改款前外廓	READY
17882_facelift	17882	Sedan	V	M139	4	EU-MASERATI-QUATTROPORTE-V-SEDAN-FACELIFT-01	HIGH	Ktype 跨越改款且车长有明确变化；本行为改款后外廓	READY
124175_prefl	124175	Sedan	V	M139	4	EU-MASERATI-QUATTROPORTE-V-SEDAN-PREFL-01	HIGH	Ktype 跨越改款且车长有明确变化；本行为改款前外廓	READY
124175_facelift	124175	Sedan	V	M139	4	EU-MASERATI-QUATTROPORTE-V-SEDAN-FACELIFT-01	HIGH	Ktype 跨越改款且车长有明确变化；本行为改款后外廓	READY
53160	53160	Sedan	V	M139	4	EU-MASERATI-QUATTROPORTE-V-SEDAN-GTS-01	HIGH		READY
100091	100091	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
126475	126475	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
53262	53262	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
53270	53270	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
52450	52450	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
123925	123925	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
52434	52434	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
59796	59796	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
143010	143010	Sedan	VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	HIGH		READY
801058	801058	Van	I			EU-MAXUS-DELIVER7-I-VAN-L2H1-01	MEDIUM	输入未标轴距/车顶，采用标准 L2H1 厢式外廓	READY
803436	803436	Van	I			EU-MAXUS-DELIVER7-I-VAN-L2H1-01	MEDIUM	输入未标轴距/车顶，采用标准 L2H1 厢式外廓	READY
147446	147446	Van	I			EU-MAXUS-DELIVER9-I-VAN-L3H2-01	MEDIUM	输入未标轴距/车顶，采用标准 L3H2 厢式外廓	READY
147447	147447	Pickup	I			EU-MAXUS-DELIVER9-I-PICKUP-CHASSIS-L3-01	MEDIUM	输入未标轴距，采用标准 L3 底盘驾驶室外廓	READY
147610	147610	Van	I			EU-MAXUS-DELIVER9-I-VAN-L3H2-01	MEDIUM	输入未标轴距/车顶，采用标准 L3H2 厢式外廓	READY
152748	152748	Van	I			EU-MAXUS-DELIVER9-I-VAN-L3H2-01	MEDIUM	输入未标轴距/车顶，采用标准 L3H2 厢式外廓	READY
150910	150910	Pickup	I			EU-MAXUS-EDELIVER3-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准底盘驾驶室外廓	READY
801123	801123	Van	I			EU-MAXUS-EDELIVER3-I-VAN-SWB-01	MEDIUM	输入未标轴距，采用标准短轴厢式外廓	READY
801124	801124	Pickup	I			EU-MAXUS-EDELIVER3-I-PICKUP-CHASSIS-01	MEDIUM	输入未标轴距，采用标准底盘驾驶室外廓	READY
157297	157297	Van	I			EU-MAXUS-EDELIVER5-I-VAN-L1H1-01	MEDIUM	输入未标轴距/车顶，采用标准 L1H1 厢式外廓	READY
156890	156890	Van	I			EU-MAXUS-EDELIVER7-I-VAN-L1H1-01	MEDIUM	输入未标轴距/车顶，采用标准 L1H1 厢式外廓	READY
158794	158794	Van	I			EU-MAXUS-EDELIVER7-I-VAN-L1H1-01	MEDIUM	输入未标轴距/车顶，采用标准 L1H1 厢式外廓	READY
143649	143649	Van	I			EU-MAXUS-EDELIVER9-I-VAN-L3H2-01	MEDIUM	输入未标轴距/车顶，采用标准 L3H2 厢式外廓	READY
150926	150926	Pickup	I			EU-MAXUS-EDELIVER9-I-PICKUP-CHASSIS-L3-01	MEDIUM	输入未标轴距，采用标准 L3 底盘驾驶室外廓	READY
160052	160052	Pickup	I		4	EU-MAXUS-ETERRON9-I-PICKUP-STD-01	HIGH		READY
150845	150845	Van	I		5	EU-MAXUS-EUNIQ5-I-VAN-STD-01	HIGH		READY
156078	156078	MPV	I		5	EU-MAXUS-MIFA7-I-MPV-STD-01	HIGH		READY
145981	145981	MPV	I		5	EU-MAXUS-MIFA9-I-MPV-STD-01	HIGH		READY
801299	801299	Pickup	I		4	EU-MAXUS-T60MAX-I-PICKUP-STD-01	HIGH		READY
143943	143943	Pickup	I		4	EU-MAXUS-T90-I-PICKUP-EV-01	HIGH		READY
149896	149896	MPV	I			EU-MAXUS-V80-I-MPV-EV80-01	MEDIUM	输入未标轴距/车顶，采用标准 EV80 客车外廓	READY
16803_prefl	16803	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-PREFL-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款前外廓	READY
16803_facelift	16803	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-FACELIFT-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款后外廓	READY
10873_prefl	10873	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-PREFL-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款前外廓	READY
10873_facelift	10873	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-FACELIFT-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款后外廓	READY
56202	56202	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-FACELIFT-01	HIGH	生产期仅覆盖 2010 改款后外廓	READY
18978_prefl	18978	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-PREFL-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款前外廓	READY
18978_facelift	18978	Sedan	I	W240	4	EU-MAYBACH-57-I-SEDAN-FACELIFT-01	HIGH	Ktype 跨越 2010 改款且车长有明确变化；本行为改款后外廓	READY
17317	17317	Hatchback	I	DY	5	EU-MAZDA-2-I-HATCHBACK-STD-01	HIGH		READY
17104	17104	Hatchback	I	DY	5	EU-MAZDA-2-I-HATCHBACK-STD-01	HIGH		READY
109546	109546	Hatchback	III	DJ	5	EU-MAZDA-2-III-HATCHBACK-STD-01	HIGH		READY
```

[下载 left18448_8801-8900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_8801-8900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAHINDRA-GOA-I-SUV-STD-01	4482	1775	1975	Auto-Data	https://www.auto-data.net/en/mahindra-goa-model-2684
EU-MAHINDRA-KUV100-I-SUV-NXT-01	3700	1735	1655	Mahindra official	https://www.mahindra.es/modelos/kuv100-k6-nxt/
EU-MAN-TGE-I-VAN-STD-01	5986	2040	2355	MAN official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-PICKUP-CHASSIS-01	5996	2033	2312	MAN official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MASERATI-228-I-COUPE-STD-01	4460	1865	1330	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/1445750/maserati_228.html
EU-MASERATI-3200GT-I-COUPE-STD-01	4510	1822	1305	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/1447070/maserati_3200_gt.html
EU-MASERATI-4200GT-I-COUPE-STD-01	4523	1822	1305	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1447280/maserati_coupe_gt.html
EU-MASERATI-GHIBLI-II-COUPE-20-01	4223	1775	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/1446605/maserati_ghibli_2_0.html
EU-MASERATI-GHIBLI-II-COUPE-28-01	4223	1775	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/1446590/maserati_ghibli_2_8.html
EU-MASERATI-GHIBLI-III-SEDAN-STD-01	4971	1945	1461	Automobile-Catalog	https://www.automobile-catalog.com/make/maserati/ghibli_3gen/ghibli_3gen/2014.html
EU-MASERATI-GRANTURISMO-I-COUPE-STD-01	4881	1847	1353	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1447985/maserati_granturismo.html
EU-MASERATI-GRANTURISMO-II-COUPE-MODENA-FOLGORE-01	4959	1957	1353	Maserati official brochure	https://www.maserati.com/content/dam/maserati/international/Brochures/my23/granturismo/Maserati_Granturismo_Digital_Flyer_EN.pdf
EU-MASERATI-GRANTURISMO-II-COUPE-TROFEO-01	4966	1957	1353	Maserati official brochure	https://www.maserati.com/content/dam/maserati/international/Brochures/my23/granturismo/Maserati_Granturismo_Digital_Flyer_EN.pdf
EU-MASERATI-GRANCABRIO-I-CONVERTIBLE-STD-01	4881	1847	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1448045/maserati_grancabrio.html
EU-MASERATI-GRANCABRIO-II-CONVERTIBLE-STD-01	4966	1957	1365	Maserati official	https://www.maserati.com/az/en/models/grancabrio/grancabrio-folgore
EU-MASERATI-GRECALE-I-SUV-GT-01	4846	1948	1670	Maserati official	https://www.maserati.com/cn/zh/news/new-maserati-grecale-global-premiere
EU-MASERATI-GRECALE-I-SUV-MODENA-01	4847	1979	1667	Maserati official	https://www.maserati.com/tw/zh/shopping-tools/grecale-digital-event-
EU-MASERATI-GRECALE-I-SUV-TROFEO-01	4859	1979	1659	Maserati official	https://www.maserati.com/gb/en/models/explore-grecale
EU-MASERATI-GRECALE-I-SUV-FOLGORE-01	4865	1948	1651	Maserati official	https://www.maserati.com/au/en/dealers/barbagallo/models/grecale
EU-MASERATI-LEVANTE-I-SUV-STD-01	5005	1981	1693	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2408285/maserati_levante_diesel_275.html
EU-MASERATI-MC12-I-COUPE-STD-01	5143	2096	1205	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1447955/maserati_mc12_stradale.html
EU-MASERATI-MC20-I-COUPE-STD-01	4669	1965	1224	Maserati official	https://www.maserati.com/global/en/models/mc20
EU-MASERATI-MC20-I-COUPE-GT2-01	4669	1965	1222	Maserati official	https://www.maserati.com/global/en/models/gt2-stradale
EU-MASERATI-MC20-I-CONVERTIBLE-CIELO-01	4669	1965	1224	Maserati official	https://www.maserati.com/qa/en/models/mc20-cielo
EU-MASERATI-MCPURA-I-COUPE-STD-01	4667	1965	1226	Maserati official catalogue	https://www.maserati.com/global/en/shopping-tools/catalogues/mcpura-catalogues
EU-MASERATI-MCPURA-I-CONVERTIBLE-CIELO-01	4667	1965	1214	Maserati official	https://www.maserati.com/global/en/models/mcpura-cielo
EU-MASERATI-MISTRAL-I-COUPE-STD-01	4500	1650	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/1443500/maserati_mistral_3700.html
EU-MASERATI-QUATTROPORTE-I-SEDAN-STD-01	5000	1720	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/1443845/maserati_quattroporte.html
EU-MASERATI-QUATTROPORTE-II-SEDAN-STD-01	5130	1870	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/1444865/maserati_quattroporte_ii.html
EU-MASERATI-QUATTROPORTE-IV-SEDAN-STD-01	4550	1810	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/1446920/maserati_quattroporte_3_2.html
EU-MASERATI-QUATTROPORTE-V-SEDAN-PREFL-01	5052	1895	1438	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1447355/maserati_quattroporte.html
EU-MASERATI-QUATTROPORTE-V-SEDAN-FACELIFT-01	5097	1895	1438	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1447475/maserati_quattroporte.html
EU-MASERATI-QUATTROPORTE-V-SEDAN-GTS-01	5097	1895	1423	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1447505/maserati_quattroporte_sport_gt_s.html
EU-MASERATI-QUATTROPORTE-VI-SEDAN-STD-01	5262	1948	1481	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2606585/maserati_quattroporte.html
EU-MAXUS-DELIVER7-I-VAN-L2H1-01	5372	2030	1999	MAXUS official brochure	https://saicmaxus.co.uk/wp-content/uploads/2024/12/HM_DELIVER7_DIESEL_SPEC_BROCHURE_MY2024_130924-1.pdf
EU-MAXUS-DELIVER9-I-VAN-L3H2-01	5940	2062	2535	MAXUS official	https://www.saicmaxus.co.uk/our-range/new-vans/deliver-9/
EU-MAXUS-DELIVER9-I-PICKUP-CHASSIS-L3-01	6200	2052	2320	MAXUS official brochure	https://bluesky-cogcms-prodb.cdn.imgeng.in/media/zucnonwm/902287-harris-maxus-deliver-9-a4-print-latest.pdf
EU-MAXUS-EDELIVER3-I-VAN-SWB-01	4555	1780	1895	MAXUS specification sheet	https://maxusdonegal.ie/wp-content/uploads/2023/04/MAXUS_eDELIVER3_SpecSheet_PDF_HM_25062021_012.pdf
EU-MAXUS-EDELIVER3-I-PICKUP-CHASSIS-01	5090	1780	1885	MAXUS specification sheet	https://maxusdonegal.ie/wp-content/uploads/2023/04/MAXUS_eDELIVER3_SpecSheet_PDF_HM_25062021_012.pdf
EU-MAXUS-EDELIVER5-I-VAN-L1H1-01	4800	1874	1960	MAXUS official brochure	https://saicmaxus.co.uk/wp-content/uploads/2024/07/MAXUS_eDELIVER5_Spec_Brochure_2024_MY24_050624.pdf
EU-MAXUS-EDELIVER7-I-VAN-L1H1-01	4998	2030	1990	MAXUS official brochure	https://saicmaxus.co.uk/wp-content/uploads/2023/09/MAXUS_Brochure_eDELIVER7_HM_31082023_083.pdf
EU-MAXUS-EDELIVER9-I-VAN-L3H2-01	5940	2062	2525	MAXUS specification sheet	https://maxusdonegal.ie/wp-content/uploads/2023/04/MAXUS_eDELIVER9_SpecSheet_PDF_HM_29062021_013.pdf
EU-MAXUS-EDELIVER9-I-PICKUP-CHASSIS-L3-01	6200	2052	2290	MAXUS specification sheet	https://maxusdonegal.ie/wp-content/uploads/2023/04/MAXUS_eDELIVER9_SpecSheet_PDF_HM_29062021_013.pdf
EU-MAXUS-ETERRON9-I-PICKUP-STD-01	5500	1997	1860	MAXUS official	https://www.saicmaxus.co.uk/our-range/new-vans/eterron-9/
EU-MAXUS-EUNIQ5-I-VAN-STD-01	4825	1825	1778	MAXUS official brochure	https://www.maxusmall.com/uploads/month_2108/2021081704493845955.pdf
EU-MAXUS-MIFA7-I-MPV-STD-01	4907	1885	1756	MAXUS official brochure	https://saicmaxus.co.uk/wp-content/uploads/2024/04/MIFA-7-MPV-90kWh-V3-1.pdf
EU-MAXUS-MIFA9-I-MPV-STD-01	5270	2000	1840	MAXUS official brochure	https://saicmaxus.co.uk/wp-content/uploads/2023/03/MAXUS_MIFA9_Spec_Brochure_2024_MY24_050624.pdf
EU-MAXUS-T60MAX-I-PICKUP-STD-01	5395	1960	1870	MAXUS official brochure	https://i0.motionx.ie/wp-content/uploads/sites/39/2025/10/06160442/t60-max-brochure.pdf
EU-MAXUS-T90-I-PICKUP-EV-01	5365	1900	1809	MAXUS official brochure	https://maxus.co.za/T90EV.pdf
EU-MAXUS-V80-I-MPV-EV80-01	5700	1998	2345	MAXUS official brochure	https://maxuskw.com/wp-content/uploads/2021/05/Maxus-V80-Brochure.pdf
EU-MAYBACH-57-I-SEDAN-PREFL-01	5728	1980	1572	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1570385/maybach_57.html
EU-MAYBACH-57-I-SEDAN-FACELIFT-01	5734	1980	1572	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1570460/maybach_57.html
EU-MAZDA-2-I-HATCHBACK-STD-01	3925	1680	1545	Auto-Data	https://www.auto-data.net/en/mazda-2-i-dy-generation-2426
EU-MAZDA-2-III-HATCHBACK-STD-01	4060	1695	1495	Auto-Data	https://www.auto-data.net/en/mazda-2-iii-dj-1.5-skyactiv-g-115hp-22025
```

[下载 left18448_8801-8900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_8801-8900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf?utm_source=chatgpt.com "man-tge-technical-data-en.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6481 行）
- 累计尺寸组：dimension_groups_final.tsv（1865 行）

