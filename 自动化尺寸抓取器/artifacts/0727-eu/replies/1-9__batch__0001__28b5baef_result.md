# 任务：1-9 第 1-9 行
# 来源文件：1-9.tsv
# 任务 ID：1-9__batch__0001__28b5baef


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】1-9 第 1-9 行

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
1-9.tsv

【当前独立任务】
1-9 第 1-9 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- 1-9_1-9_ktype_dimension_mapping_final.tsv
- 1-9_1-9_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype	LatestStatus
Opel	Corsa d	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Jul 2006	Aug 2014	2024-03-01	1	NEW
BMW	1502-2002	1502	Stufenheck	Heckantrieb	Benzin	55	75	Jan 1975	Jul 1977	2024-03-01	2	NEW
Renault	Megane iii	2.0 TCE	Coupe	Frontantrieb	Benzin	184	250	May 2009	Aug 2015	2024-03-01	3	NEW
BMW	1502-2002	1602	Stufenheck	Heckantrieb	Benzin	63	85	Apr 1971	Jul 1975	2024-03-01	4	NEW
BMW	1502-2002	1802	Stufenheck	Heckantrieb	Benzin	66	90	May 1971	Jul 1975	2024-03-01	5	NEW
BMW	1502-2002	2002	Stufenheck	Heckantrieb	Benzin	74	100	Feb 1968	Jul 1975	2024-03-01	6	NEW
BMW	1502-2002	2002	Cabriolet	Heckantrieb	Benzin	74	100	May 1971	Jul 1975	2024-03-01	7	NEW
BMW	1502-2002	2002 TII	Stufenheck	Heckantrieb	Benzin	96	130	Apr 1971	Jun 1975	2024-03-01	8	NEW
BMW	1502-2002	2002 Turbo	Stufenheck	Heckantrieb	Benzin	125	170	Jan 1974	Jul 1975	2024-03-01	9	NEW 


--- Round 1 / 首次发送 ---
## 1）更新点

* Ktype `1`：Corsa D 1.4 90 hp 同时覆盖 3 门和 5 门车身，官方规格确认两者不含后视镜宽度分别为 1713 mm、1737 mm，因此拆分为两个物理分支。输入生产期超过已核对的 90 hp 车型生产期，映射置信度标记为 `MEDIUM`，但不阻塞闭合。 、1602、1802、2002、2002 TII 复用标准 E10 两门 Sedan 尺寸组。 ([汽车目录][1])type `3`：Megane III 250 hp 对应 Renault Sport 宽体 Coupe，采用明确标注不含后视镜宽度的 1848 mm 数据。 ([汽车目录][2])type `7`：输入生产期跨越全敞篷 Cabriolet 与 1971 年 7 月起的 Baur TopCabriolet，两个车身高度不同，拆分为两个分支。 ([汽车目录][3])type `9`：2002 Turbo 为独立 E20 宽体外廓，单独建立尺寸组。 ([汽车目录][4]) 2）进度

输入 Ktype：`9/9` 已覆盖
最终映射行：`11`
最终尺寸组：`7`
READY：`11`
PENDING：`0`
机械终检：表头、列数、ID 唯一性、引用闭合、正整数三维、来源及链接、孤立组检查均通过。

## 3）最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1_3dr	1	Hatchback	Corsa D		3	EU-OPEL-CORSA-D-HATCHBACK-3DR-01	MEDIUM	3-door branch; input lifespan extends beyond sourced 90 hp production.	READY
1_5dr	1	Hatchback	Corsa D		5	EU-OPEL-CORSA-D-HATCHBACK-5DR-01	MEDIUM	5-door branch; input lifespan extends beyond sourced 90 hp production.	READY
2	2	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-STANDARD-01	HIGH		READY
3	3	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-RS-01	HIGH	Renault Sport wide-body exterior.	READY
4	4	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-STANDARD-01	HIGH		READY
5	5	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-STANDARD-01	HIGH		READY
6	6	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-STANDARD-01	HIGH		READY
7_fullcab	7	Convertible	02 Series		2	EU-BMW-02-E10-CONVERTIBLE-FULLCAB-01	HIGH	Full Cabriolet branch through Jun 1971.	READY
7_topcab	7	Convertible	02 Series		2	EU-BMW-02-E10-CONVERTIBLE-TOPCAB-01	HIGH	Baur TopCabriolet branch from Jul 1971.	READY
8	8	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-STANDARD-01	HIGH		READY
9	9	Sedan	02 Series	E20	2	EU-BMW-02-E20-SEDAN-TURBO-01	HIGH	Factory Turbo wide-body exterior.	READY
```

[下载 1-9_1-9_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/1-9_1-9_ktype_dimension_mapping_final.tsv)

## 4）最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CORSA-D-HATCHBACK-3DR-01	3999	1713	1488	Vauxhall Corsa Price/Specification Guide (12 May 2014)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/corsa/price-guides/015_Corsa_Spec_PG_12_May_2014-1402308752.pdf
EU-OPEL-CORSA-D-HATCHBACK-5DR-01	3999	1737	1488	Vauxhall Corsa Price/Specification Guide (12 May 2014)	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/corsa/price-guides/015_Corsa_Spec_PG_12_May_2014-1402308752.pdf
EU-BMW-02-E10-SEDAN-STANDARD-01	4230	1590	1410	Automobile-Catalog (1975 BMW 1502)	https://www.automobile-catalog.com/car/1975/76940/bmw_1502.html
EU-RENAULT-MEGANE-III-COUPE-RS-01	4299	1848	1435	Automobile-Catalog (2010 Renault Megane RS)	https://www.automobile-catalog.com/car/2010/2959820/renault_megane_rs_renault_sport.html
EU-BMW-02-E10-CONVERTIBLE-FULLCAB-01	4230	1590	1360	Automobile-Catalog (1971 BMW 2002 Cabriolet, Jan-Jun)	https://www.automobile-catalog.com/car/1971/77165/bmw_2002_cabriolet.html
EU-BMW-02-E10-CONVERTIBLE-TOPCAB-01	4230	1590	1400	Automobile-Catalog (1971 BMW 2002 TopCabriolet, from Jul)	https://www.automobile-catalog.com/car/1971/36845/bmw_2002_cabriolet.html
EU-BMW-02-E20-SEDAN-TURBO-01	4220	1620	1410	Automobile-Catalog (1974 BMW 2002 Turbo)	https://www.automobile-catalog.com/car/1974/26645/bmw_2002_turbo.html
```

[下载 1-9_1-9_dimension_groups_final.tsv](sandbox:/mnt/data/1-9_1-9_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1975/76940/bmw_1502.html?utm_source=chatgpt.com "Detailed specs review of 1975 BMW 1502 model for Europe"
[2]: https://www.automobile-catalog.com/car/2010/2959820/renault_megane_rs_renault_sport.html?utm_source=chatgpt.com "2010 Renault Megane RS (Renault Sport) Specs Review (184 kW ..."
[3]: https://www.automobile-catalog.com/car/1971/77165/bmw_2002_cabriolet.html?utm_source=chatgpt.com "1971 BMW 2002 Cabriolet Specs Review (73.5 kW / 100 PS / 99 hp) (since January 1971 for Europe )"
[4]: https://www.automobile-catalog.com/car/1974/26645/bmw_2002_turbo.html?utm_source=chatgpt.com "1974 BMW 2002 Turbo Specs Review (125 kW / 170 PS ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（11 行）
- 累计尺寸组：dimension_groups_final.tsv（7 行）

