# 任务：left18448 第 7801-7900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0079__dfb2bdcf


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7801-7900 行

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
left18448 第 7801-7900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7801-7900_ktype_dimension_mapping_final.tsv
- left18448_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-JEEP-PATRIOT-MK-SUV-01	4410	1756	1637

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Jeep	Patriot	2.0 CRD	Geländewagen geschlossen	Frontantrieb	Diesel	Feb 2007	Dec 2017	56233
Jeep	Patriot	2.2 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 2011	Dec 2017	10156
Jeep	Patriot	2.2 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	Jan 2011	Dec 2017	11465
Jeep	Renegade	1.4	SUV	Frontantrieb	Benzin	Jul 2014	Dec 2018	107046
Jeep	Renegade	1.6	SUV	Frontantrieb	Benzin	Jul 2014	Sep 2018	107045
Jeep	Renegade	1.0 T-gdi	SUV	Frontantrieb	Benzin	Aug 2021	-	149291
Jeep	Renegade	1.3 Phev 4XE	SUV	Allrad	Benzin/Elektro	Aug 2020	-	144113
Jeep	Renegade	1.4 4X4	SUV	Allrad	Benzin	Jul 2014	Dec 2018	107049
Jeep	Renegade	1.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2016	-	148241
Jeep	Renegade	1.5 T4 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147846
Jeep	Renegade	1.6 CRD	SUV	Frontantrieb	Diesel	Jul 2014	-	107050
Jeep	Renegade	1.6 CRD	SUV	Frontantrieb	Diesel	Jun 2017	-	802280
Jeep	Renegade	1.6 Multijet	SUV	Frontantrieb	Diesel	Feb 2020	-	144112
Jeep	Renegade	1.6 Multijet	SUV	Frontantrieb	Diesel	Aug 2022	-	149314
Jeep	Renegade	2.0 CRD 4X4	SUV	Allrad	Diesel	Jul 2014	-	107051
Jeep	Renegade	2.0 CRD 4X4	SUV	Allrad	Diesel	Jul 2014	-	107052
Jeep	Renegade	2.0 CRD 4X4	SUV	Allrad	Diesel	Jul 2014	-	116883
Jeep	Renegade van	1.4	Kasten/SUV	Frontantrieb	Benzin	Jul 2014	-	143117
Jeep	Renegade van	1.4 4X4	Kasten/SUV	Allrad	Benzin	Jul 2014	-	143118
Jeep	Renegade van	1.6 E-torq	Kasten/SUV	Frontantrieb	Benzin	Jul 2014	Sep 2018	143119
Jeep	Wrangler i	4.2	Geländewagen offen	Allrad	Benzin	Aug 1986	Aug 1989	18194
Jeep	Wrangler ii	2.4	Geländewagen offen	Allrad	Benzin	Nov 2002	Apr 2007	17259
Jeep	Wrangler ii	4	Geländewagen offen	Allrad	Benzin	Jun 1998	Apr 2007	14407
Jeep	Wrangler ii	4	Geländewagen offen	Allrad	Benzin	Aug 1996	Apr 2007	55969
Jeep	Wrangler ii	4.0 Rubicon	Geländewagen offen	Allrad	Benzin	Aug 2003	Apr 2007	17735
Jeep	Wrangler iii	3.6 V6	Geländewagen offen	Allrad	Benzin	Oct 2011	-	12487
Jeep	Wrangler iv	6.4	Geländewagen offen	Allrad	Benzin	Sep 2021	-	147732
Jeep	Wrangler iv	2.0 4XE Plug-in Hybrid	Geländewagen offen	Allrad	Benzin/Elektro	May 2021	-	145708
Karma	Gs-6	1.5 Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Sep 2021	-	146597
KG Mobility	Actyon	GDI	SUV	Frontantrieb	Benzin	Aug 2024	-	160358
KG Mobility	Actyon	GDI	SUV	Frontantrieb	Benzin	Aug 2024	-	801096
KG Mobility	Actyon	GDI 4X4	SUV	Allrad	Benzin	Aug 2024	-	160357
KG Mobility	Actyon	GDI 4X4	SUV	Allrad	Benzin	Aug 2024	-	801097
KG Mobility	Actyon	Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	163086
KG Mobility	Korando	1.5 T-gdi	SUV	Frontantrieb	Benzin	Nov 2023	-	157741
KG Mobility	Korando	1.5 T-gdi	SUV	Frontantrieb	Benzin	May 2025	-	801832
KG Mobility	Korando	1.5 T-gdi 4WD	SUV	Allrad	Benzin	Nov 2023	-	157743
KG Mobility	Korando	1.5 T-gdi 4WD	SUV	Allrad	Benzin	May 2025	-	801831
KG Mobility	Musso	2.2 E-xdi	Pick-up	Heckantrieb	Diesel	Nov 2023	-	157757
KG Mobility	Musso	2.2 E-xdi 4WD	Pick-up	Allrad	Diesel	Nov 2023	-	157756
KG Mobility	Musso	EV	Pick-up	Frontantrieb	Elektro	Mar 2025	-	802031
KG Mobility	Musso	EV 4WD	Pick-up	Allrad	Elektro	May 2025	-	802033
KG Mobility	Musso	EV 4WD	Pick-up	Allrad	Elektro	Jan 2026	-	803057
KG Mobility	Rexton	2.2 E-xdi	SUV	Heckantrieb	Diesel	Nov 2023	-	803439
KG Mobility	Rexton	2.2 E-xdi 4WD	SUV	Allrad	Diesel	Nov 2023	-	157754
KG Mobility	Tivoli	1.5 T-gdi	SUV	Frontantrieb	Benzin	Nov 2023	-	157748
KG Mobility	Tivoli	1.5 T-gdi	SUV	Frontantrieb	Benzin	Nov 2023	-	157750
KG Mobility	Tivoli	1.5 T-gdi	SUV	Frontantrieb	Benzin	Jun 2024	-	160680
KG Mobility	Tivoli	1.5 T-gdi	SUV	Frontantrieb	Benzin	Jun 2024	-	160682
KG Mobility	Tivoli	1.5 T-gdi 4WD	SUV	Allrad	Benzin	Nov 2023	-	157749
KG Mobility	Torres	1.5	SUV	Frontantrieb	Benzin	Nov 2023	-	157744
KG Mobility	Torres	1.5 4WD	SUV	Allrad	Benzin	Nov 2023	-	157745
KG Mobility	Torres	1.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jun 2025	-	802242
KG Mobility	Torres	EVX	SUV	Frontantrieb	Elektro	Jan 2024	-	157759
KG Mobility	Torres	EVX	Kasten/SUV	Frontantrieb	Elektro	Jan 2024	-	801659
KIA	Besta	2.2 D	Kasten	Heckantrieb	Diesel	Feb 1996	Dec 2003	10793
KIA	Besta	2.2 D	Bus	Heckantrieb	Diesel	Jul 1992	Dec 2003	57903
KIA	Cadenza i	3.5 Cvvt	Stufenheck	Frontantrieb	Benzin	Jan 2010	Dec 2015	55701
KIA	Cadenza ii	3.3 GDI	Stufenheck	Frontantrieb	Benzin	Jan 2016	-	122060
KIA	Cadenza ii	3.3 MPI	Stufenheck	Frontantrieb	Benzin	Jan 2016	-	122062
KIA	Carens i	1.6	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	Aug 2006	16936
KIA	Carens i	1.8 I	Großraumlimousine	Frontantrieb	Benzin	Nov 2000	Jul 2002	15580
KIA	Carens i	1.8 I	Großraumlimousine	Frontantrieb	Benzin	Mar 2000	Aug 2006	119084
KIA	Carens i	1.8 I 16V	Großraumlimousine	Frontantrieb	Benzin	Mar 2000	May 2002	101135
KIA	Carens i	2.0 Crdi	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	Apr 2006	16938
KIA	Carens i	2.0 Cvvt	Großraumlimousine	Frontantrieb	Benzin	Aug 2004	May 2007	18286
KIA	Carens ii	1.8	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	Aug 2006	16937
KIA	Carens iii	1.6 Crdi 110	Großraumlimousine	Frontantrieb	Diesel	Oct 2010	Mar 2013	59293
KIA	Carens iv	1.6 GDI	Großraumlimousine	Frontantrieb	Benzin	Mar 2013	Aug 2016	58619
KIA	Carens iv	1.7 Crdi	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Aug 2018	58621
KIA	Carens iv	1.7 Crdi	Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Aug 2016	58622
KIA	Carens iv	1.7 Crdi	Großraumlimousine	Frontantrieb	Diesel	Jul 2015	Sep 2018	118700
KIA	Carens iv	2.0 GDI	Großraumlimousine	Frontantrieb	Benzin	Mar 2013	-	58620
KIA	Carens iv	2.0 GDI	Großraumlimousine	Frontantrieb	Benzin	Mar 2013	Aug 2016	58894
KIA	Carens iv	2.0 GDI	Großraumlimousine	Frontantrieb	Benzin	Jun 2016	Aug 2016	151411
KIA	Carens iv van	Crdi	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	Aug 2016	142826
KIA	Carens iv van	Crdi	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	Aug 2016	142827
KIA	Carnival / grand iii	2.2 Crdi	Großraumlimousine	Frontantrieb	Diesel	Jan 2010	Jun 2015	5963
KIA	Carnival / grand iii	2.2 Crdi	Großraumlimousine	Frontantrieb	Diesel	Jan 2010	Jun 2015	5970
KIA	Carnival i	2.5 V6	Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Oct 2001	13140
KIA	Carnival i	2.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Aug 1999	Oct 2001	13141
KIA	Carnival ii	3.5	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	Apr 2006	16821
KIA	Carnival iv	2.2 Crdi VGT	Großraumlimousine	Frontantrieb	Diesel	Sep 2020	-	142670
KIA	Carnival iv	3.5 MPI	Großraumlimousine	Frontantrieb	Benzin	Sep 2021	-	145736
KIA	Ceed	1.0 T-gdi 100 Eco-dynamics+	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	147743
KIA	Ceed	1.0 T-gdi 100 Eco-dynamics+	Kombi	Frontantrieb	Benzin/Elektro	Apr 2022	-	147744
KIA	Ceed	1.0 T-gdi Eco-dynamics+	Kombi	Frontantrieb	Benzin/Elektro	Jul 2021	-	147705
KIA	Ceed	1.0 T-gdi Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2021	-	152735
KIA	Ceed	1.5 T-gdi	Schrägheck	Frontantrieb	Benzin	Jan 2021	-	143332
KIA	Ceed	1.5 T-gdi	Kombi	Frontantrieb	Benzin	Jan 2021	-	143333
KIA	Ceed	1.5 T-gdi	Schrägheck	Frontantrieb	Benzin	Feb 2024	-	158044
KIA	Ceed	1.5 T-gdi	Kombi	Frontantrieb	Benzin	Feb 2024	-	158046
KIA	Ceed	1.5 T-gdi Eco-dynamics+	Kombi	Frontantrieb	Benzin/Elektro	Jan 2021	-	145706
KIA	Ceed	1.5 T-gdi Eco-dynamics+	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	145707
KIA	Ceed	1.5 T-gdi Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2024	-	158045
KIA	Ceed	1.5 T-gdi Mhev	Kombi	Frontantrieb	Benzin/Elektro	Feb 2024	-	158047
KIA	Cee'd	1.6	Kombi	Frontantrieb	Benzin	Sep 2007	Nov 2012	5135
KIA	Cee'd	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jul 2015	Jul 2018	116489
KIA	Cee'd	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jul 2015	Jul 2018	116490
KIA	Cee'd	1.0 T-gdi	Kombi	Frontantrieb	Benzin	Jul 2015	Jul 2018	116492


--- Round 1 / 首次发送 ---
## 更新点

Patriot 直接复用累计尺寸组；Renegade 按标准、传统 4×4、4xe、e-Hybrid 四种实际外廓闭合；Wrangler 对 TJ Rubicon、JL 392、JL 4xe 等有明确尺寸([汽车数据网][1])([汽车数据网][1])

机械终检已通过：100 个输入 Ktype 全部为 `READY`，`PENDING=0`；共引用 34 个尺寸组，无重复 ID、断裂引用或孤立尺寸组。

## 进度

`TOTAL=100 | READY=100 | PENDING=0 | DIMENSION_GROUPS=34`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56233	56233	SUV	I	MK	5	EU-JEEP-PATRIOT-MK-SUV-01	HIGH		READY
10156	10156	SUV	I	MK	5	EU-JEEP-PATRIOT-MK-SUV-01	HIGH		READY
11465	11465	SUV	I	MK	5	EU-JEEP-PATRIOT-MK-SUV-01	HIGH		READY
107046	107046	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
107045	107045	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
149291	149291	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
144113	144113	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4XE-01	HIGH		READY
107049	107049	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4X4-01	HIGH		READY
148241	148241	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
147846	147846	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-EHYBRID-01	HIGH		READY
107050	107050	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
802280	802280	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
144112	144112	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
149314	149314	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	HIGH		READY
107051	107051	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4X4-01	HIGH		READY
107052	107052	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4X4-01	HIGH		READY
116883	116883	SUV	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4X4-01	HIGH		READY
143117	143117	Van	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	MEDIUM	Commercial conversion; exterior follows Renegade BU shell.	READY
143118	143118	Van	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-4X4-01	MEDIUM	Commercial conversion; exterior follows Renegade BU shell.	READY
143119	143119	Van	I	BU	5	EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	MEDIUM	Commercial conversion; exterior follows Renegade BU shell.	READY
18194	18194	Convertible	I	YJ	2	EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-02	MEDIUM	4.2 variant matched to YJ 2-door exterior.	READY
17259	17259	Convertible	II	TJ	2	EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-STANDARD-01	HIGH		READY
14407	14407	Convertible	II	TJ	2	EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-STANDARD-01	HIGH		READY
55969	55969	Convertible	II	TJ	2	EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-STANDARD-01	HIGH		READY
17735	17735	Convertible	II	TJ	2	EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-RUBICON-01	HIGH	Factory Rubicon exterior branch.	READY
12487	12487	Convertible	III	JK	2	EU-JEEP-WRANGLER-III-JK-CONVERTIBLE-2D-02	HIGH		READY
147732	147732	Convertible	IV	JL	4	EU-JEEP-WRANGLER-IV-JL-CONVERTIBLE-4D-392-01	HIGH	Factory 392 exterior branch.	READY
145708	145708	Convertible	IV	JL	4	EU-JEEP-WRANGLER-IV-JL-CONVERTIBLE-4D-4XE-01	HIGH	Factory 4xe exterior branch.	READY
146597	146597	Sedan	GS-6		4	EU-KARMA-GS6-2022-SEDAN-STANDARD-01	HIGH		READY
160358	160358	SUV	2024		5	EU-KGM-ACTYON-2024-SUV-STANDARD-01	HIGH		READY
801096	801096	SUV	2024		5	EU-KGM-ACTYON-2024-SUV-STANDARD-01	HIGH		READY
160357	160357	SUV	2024		5	EU-KGM-ACTYON-2024-SUV-STANDARD-01	HIGH		READY
801097	801097	SUV	2024		5	EU-KGM-ACTYON-2024-SUV-STANDARD-01	HIGH		READY
163086	163086	SUV	2024		5	EU-KGM-ACTYON-2024-SUV-STANDARD-01	HIGH		READY
157741	157741	SUV	2023		5	EU-KGM-KORANDO-2023-SUV-STANDARD-01	HIGH		READY
801832	801832	SUV	2023		5	EU-KGM-KORANDO-2023-SUV-STANDARD-01	HIGH		READY
157743	157743	SUV	2023		5	EU-KGM-KORANDO-2023-SUV-STANDARD-01	HIGH		READY
801831	801831	SUV	2023		5	EU-KGM-KORANDO-2023-SUV-STANDARD-01	HIGH		READY
157757	157757	Pickup	2023		4	EU-KGM-MUSSO-2023-PICKUP-STANDARD-01	HIGH		READY
157756	157756	Pickup	2023		4	EU-KGM-MUSSO-2023-PICKUP-STANDARD-01	HIGH		READY
802031	802031	Pickup	2025		4	EU-KGM-MUSSO-EV-2025-PICKUP-STANDARD-01	HIGH		READY
802033	802033	Pickup	2025		4	EU-KGM-MUSSO-EV-2025-PICKUP-STANDARD-01	HIGH		READY
803057	803057	Pickup	2025		4	EU-KGM-MUSSO-EV-2025-PICKUP-STANDARD-01	HIGH		READY
803439	803439	SUV	2023		5	EU-KGM-REXTON-2023-SUV-STANDARD-01	HIGH		READY
157754	157754	SUV	2023		5	EU-KGM-REXTON-2023-SUV-STANDARD-01	HIGH		READY
157748	157748	SUV	2023		5	EU-KGM-TIVOLI-2023-SUV-STANDARD-01	HIGH		READY
157750	157750	SUV	2023		5	EU-KGM-TIVOLI-2023-SUV-STANDARD-01	HIGH		READY
160680	160680	SUV	2023		5	EU-KGM-TIVOLI-2023-SUV-STANDARD-01	HIGH		READY
160682	160682	SUV	2023		5	EU-KGM-TIVOLI-2023-SUV-STANDARD-01	HIGH		READY
157749	157749	SUV	2023		5	EU-KGM-TIVOLI-2023-SUV-STANDARD-01	HIGH		READY
157744	157744	SUV	2023		5	EU-KGM-TORRES-2023-SUV-STANDARD-01	HIGH		READY
157745	157745	SUV	2023		5	EU-KGM-TORRES-2023-SUV-STANDARD-01	HIGH		READY
802242	802242	SUV	2023		5	EU-KGM-TORRES-2023-SUV-STANDARD-01	HIGH		READY
157759	157759	SUV	2023		5	EU-KGM-TORRES-2023-SUV-STANDARD-01	HIGH		READY
801659	801659	Van	2023		5	EU-KGM-TORRES-2023-SUV-STANDARD-01	MEDIUM	Commercial conversion; exterior follows Torres EVX shell.	READY
10793	10793	Van	I	TA		EU-KIA-BESTA-I-VAN-STANDARD-01	MEDIUM		READY
57903	57903	Van	I	TA		EU-KIA-BESTA-I-VAN-STANDARD-01	MEDIUM	Passenger and panel variants share sourced exterior envelope.	READY
55701	55701	Sedan	I		4	EU-KIA-CADENZA-I-SEDAN-STANDARD-01	HIGH		READY
122060	122060	Sedan	II		4	EU-KIA-CADENZA-II-SEDAN-STANDARD-01	HIGH		READY
122062	122062	Sedan	II		4	EU-KIA-CADENZA-II-SEDAN-STANDARD-01	HIGH		READY
16936	16936	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	HIGH		READY
15580	15580	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	HIGH		READY
119084	119084	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	HIGH		READY
101135	101135	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	HIGH		READY
16938	16938	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	HIGH		READY
18286	18286	MPV	I	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	MEDIUM	Late registration range matched to the same Carens I exterior.	READY
16937	16937	MPV	II	RS	5	EU-KIA-CARENS-I-MPV-STANDARD-01	MEDIUM	Input generation label retained; exterior matches Carens I production body.	READY
59293	59293	MPV	III	UN	5	EU-KIA-CARENS-III-MPV-STANDARD-01	MEDIUM	Input generation label matched to the UN exterior.	READY
58619	58619	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
58621	58621	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
58622	58622	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
118700	118700	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
58620	58620	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
58894	58894	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
151411	151411	MPV	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	HIGH		READY
142826	142826	Van	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	MEDIUM	Commercial conversion; exterior follows Carens IV RP shell.	READY
142827	142827	Van	IV	RP	5	EU-KIA-CARENS-IV-MPV-STANDARD-01	MEDIUM	Commercial conversion; exterior follows Carens IV RP shell.	READY
5963	5963	MPV	III	VQ	5	EU-KIA-CARNIVAL-III-VQ-MPV-STANDARD-01	MEDIUM	Combined aftermarket model label mapped to standard European VQ exterior.	READY
5970	5970	MPV	III	VQ	5	EU-KIA-CARNIVAL-III-VQ-MPV-STANDARD-01	MEDIUM	Combined aftermarket model label mapped to standard European VQ exterior.	READY
13140	13140	MPV	I	UP/GQ	5	EU-KIA-CARNIVAL-I-MPV-PREFL-01	HIGH		READY
13141	13141	MPV	I	UP/GQ	5	EU-KIA-CARNIVAL-I-MPV-PREFL-01	HIGH		READY
16821	16821	MPV	II	UP/GQ	5	EU-KIA-CARNIVAL-II-MPV-FACELIFT-01	HIGH		READY
142670	142670	MPV	IV	KA4	5	EU-KIA-CARNIVAL-IV-KA4-MPV-STANDARD-01	HIGH		READY
145736	145736	MPV	IV	KA4	5	EU-KIA-CARNIVAL-IV-KA4-MPV-STANDARD-01	HIGH		READY
147743	147743	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
147744	147744	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
147705	147705	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
152735	152735	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
143332	143332	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
143333	143333	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
158044	158044	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
158046	158046	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
145706	145706	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
145707	145707	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
158045	158045	Hatchback	III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	HIGH		READY
158047	158047	Wagon	III	CD	5	EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	HIGH		READY
5135	5135	Wagon	I	ED	5	EU-KIA-CEED-I-ED-WAGON-STANDARD-01	MEDIUM	Facelift and roof-rail height variation not split; standard body envelope used.	READY
116489	116489	Hatchback	II	JD	5	EU-KIA-CEED-II-JD-HATCHBACK-FACELIFT-01	HIGH		READY
116490	116490	Hatchback	II	JD	5	EU-KIA-CEED-II-JD-HATCHBACK-FACELIFT-01	HIGH		READY
116492	116492	Wagon	II	JD	5	EU-KIA-CEED-II-JD-WAGON-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射最终 TSV](sandbox:/mnt/data/left18448_7801-7900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-PATRIOT-MK-SUV-01	4410	1756	1637	Auto-Data	https://www.auto-data.net/en/jeep-patriot-model-160
EU-JEEP-RENEGADE-BU-SUV-STANDARD-01	4236	1805	1667	Auto-Data	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.0-t-gdi-120hp-35848
EU-JEEP-RENEGADE-BU-SUV-4XE-01	4236	1805	1692	Auto-Data	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.3-turbo-190hp-plug-in-hybrid-4xe-automatic-41418
EU-JEEP-RENEGADE-BU-SUV-4X4-01	4236	1805	1697	Auto-Data	https://www.auto-data.net/en/jeep-renegade-1.4-multiair2-170hp-4x4-automatic-start-stop-22112
EU-JEEP-RENEGADE-BU-SUV-EHYBRID-01	4236	1805	1702	Auto-Data	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.5-gse-t4-130hp-e-hybrid-dct-46356
EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-02	3879	1740	1765	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-i-yj-generation-341
EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-STANDARD-01	3883	1694	1750	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-ii-tj-2.4-i-16v-147hp-1179
EU-JEEP-WRANGLER-II-TJ-CONVERTIBLE-2D-RUBICON-01	3947	1693	1764	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-ii-tj-rubicon-4.0-i-193hp-automatic-31702
EU-JEEP-WRANGLER-III-JK-CONVERTIBLE-2D-02	4223	1873	1840	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sahara-3.6i-v6-24v-285hp-4x4-automatic-31688
EU-JEEP-WRANGLER-IV-JL-CONVERTIBLE-4D-392-01	4785	1875	1892	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-iv-unlimited-jl-rubicon-6.4-392-v8-470hp-4x4-selec-trac-automatic-43239
EU-JEEP-WRANGLER-IV-JL-CONVERTIBLE-4D-4XE-01	4786	1875	1868	Auto-Data	https://www.auto-data.net/en/jeep-wrangler-iv-unlimited-jl-rubicon-2.0-turbo-375hp-4xe-etorque-plug-in-hybrid-rock-trac-automatic-43238
EU-KARMA-GS6-2022-SEDAN-STANDARD-01	5065	1984	1331	Edmunds	https://www.edmunds.com/karma/gs-6/2022/features-specs/
EU-KGM-ACTYON-2024-SUV-STANDARD-01	4740	1910	1680	Auto-Data	https://www.auto-data.net/en/kgm-actyon-model-3516
EU-KGM-KORANDO-2023-SUV-STANDARD-01	4465	1870	1635	Auto-Data	https://www.auto-data.net/en/kgm-korando-model-3360
EU-KGM-MUSSO-2023-PICKUP-STANDARD-01	5095	1950	1870	Auto-Data	https://www.auto-data.net/en/kgm-musso-generation-10418
EU-KGM-MUSSO-EV-2025-PICKUP-STANDARD-01	5160	1920	1740	KGM official	https://en.kg-mobility.com/pr/model/show-room/200000300020003
EU-KGM-REXTON-2023-SUV-STANDARD-01	4850	1960	1825	Auto-Data	https://www.auto-data.net/en/kgm-rexton-model-3368
EU-KGM-TIVOLI-2023-SUV-STANDARD-01	4255	1810	1620	Auto-Data	https://www.auto-data.net/en/kgm-tivoli-model-3359
EU-KGM-TORRES-2023-SUV-STANDARD-01	4715	1890	1725	Auto-Data	https://www.auto-data.net/en/kgm-torres-generation-9752
EU-KIA-BESTA-I-VAN-STANDARD-01	4685	1695	1945	Engine in Detail	https://www.engineindetail.com/cars/kia/besta/besta-ta-1997-2000
EU-KIA-CADENZA-I-SEDAN-STANDARD-01	4965	1850	1475	Auto-Data	https://www.auto-data.net/en/kia-cadenza-model-2212
EU-KIA-CADENZA-II-SEDAN-STANDARD-01	4971	1869	1471	Auto-Data	https://www.auto-data.net/en/kia-cadenza-model-2212
EU-KIA-CARENS-I-MPV-STANDARD-01	4493	1748	1609	Auto-Data	https://www.auto-data.net/en/kia-carens-model-289
EU-KIA-CARENS-III-MPV-STANDARD-01	4545	1820	1650	Auto-Data	https://www.auto-data.net/en/kia-carens-model-289
EU-KIA-CARENS-IV-MPV-STANDARD-01	4525	1805	1610	Auto-Data	https://www.auto-data.net/en/kia-carens-model-289
EU-KIA-CARNIVAL-III-VQ-MPV-STANDARD-01	4810	1985	1760	Auto-Data	https://www.auto-data.net/en/kia-carnival-model-294
EU-KIA-CARNIVAL-I-MPV-PREFL-01	4890	1900	1730	Auto-Data	https://www.auto-data.net/en/kia-carnival-model-294
EU-KIA-CARNIVAL-II-MPV-FACELIFT-01	4925	1900	1735	Auto-Data	https://www.auto-data.net/en/kia-carnival-model-294
EU-KIA-CARNIVAL-IV-KA4-MPV-STANDARD-01	5155	1995	1740	Auto-Data	https://www.auto-data.net/en/kia-carnival-model-294
EU-KIA-CEED-III-CD-HATCHBACK-FACELIFT-01	4325	1800	1447	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-facelift-2021-generation-8610
EU-KIA-CEED-III-CD-WAGON-FACELIFT-01	4600	1800	1465	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-sportswagon-facelift-2021-1.0-t-gdi-120hp-44740
EU-KIA-CEED-I-ED-WAGON-STANDARD-01	4470	1790	1490	Auto-Data	https://www.auto-data.net/en/kia-ceed-sw-i-1.6-cvvt-122hp-42438
EU-KIA-CEED-II-JD-HATCHBACK-FACELIFT-01	4310	1780	1470	Auto-Data	https://www.auto-data.net/en/kia-ceed-ii-facelift-2015-generation-5965
EU-KIA-CEED-II-JD-WAGON-FACELIFT-01	4505	1780	1485	Auto-Data	https://www.auto-data.net/en/kia-ceed-sw-ii-facelift-2015-1.6-gdi-135hp-41653
```

[下载 DIMENSION_GROUP 最终 TSV](sandbox:/mnt/data/left18448_7801-7900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.5-gse-t4-130hp-e-hybrid-dct-46356?utm_source=chatgpt.com "Jeep Renegade (facelift 2018) 1.5 GSE T4 (130 Hp) e ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5452 行）
- 累计尺寸组：dimension_groups_final.tsv（1469 行）

