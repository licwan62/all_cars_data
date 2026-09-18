# 任务：left18448 第 18401-18448 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0185__af591c1f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 18401-18448 行

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
left18448 第 18401-18448 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_18401-18448_ktype_dimension_mapping_final.tsv
- left18448_18401-18448_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Wiesmann	Mf3 roadster	3.2	Cabriolet	Heckantrieb	Benzin	Jan 1996	Aug 2001	13368
Wiesmann	Mf3 roadster	3.2	Cabriolet	Heckantrieb	Benzin	Jul 2003	-	17888
Wiesmann	Mf3 roadster	3.2	Cabriolet	Heckantrieb	Benzin	May 2001	Aug 2003	124747
Wiesmann	Mf4 roadster	4.4	Cabriolet	Heckantrieb	Benzin	Nov 2010	-	10074
Wiesmann	Mf5 roadster	4.4	Cabriolet	Heckantrieb	Benzin	Nov 2010	-	10076
Wiesmann	Mf5 roadster	4.4	Cabriolet	Heckantrieb	Benzin	Feb 2012	-	110276
Xbus	X	Electric	Bus	Allrad	Elektro	Jan 2022	-	146228
Xbus	Xbus	Electric	Pritsche/Fahrgestell	Allrad	Elektro	Jan 2022	-	146226
Xbus	Xbus	Electric	Kasten	Allrad	Elektro	Jan 2022	-	146227
XEV	Yoyo	EV	Schrägheck	Heckantrieb	Elektro	Jul 2022	-	148107
Xpeng	G3i	EV	SUV	Frontantrieb	Elektro	Jul 2021	-	146029
Xpeng	G6	EV	SUV	Heckantrieb	Elektro	Jun 2023	-	800228
Xpeng	G6	EV	SUV	Heckantrieb	Elektro	Jul 2024	-	800259
Xpeng	G6	EV	SUV	Heckantrieb	Elektro	Jun 2023	-	800260
Xpeng	G6	EV Allrad	SUV	Allrad	Elektro	Jun 2023	-	155404
Xpeng	G6	EV Allrad	SUV	Allrad	Elektro	May 2024	-	800715
Xpeng	G9	EV	SUV	Heckantrieb	Elektro	Sep 2022	-	150157
Xpeng	G9	EV	SUV	Heckantrieb	Elektro	Mar 2025	-	801587
Xpeng	G9	EV Allrad	SUV	Allrad	Elektro	Sep 2022	-	150158
Xpeng	G9	EV Allrad	SUV	Allrad	Elektro	Mar 2025	-	801588
Xpeng	P7	EV	Stufenheck	Heckantrieb	Elektro	Mar 2023	-	152822
Xpeng	P7	EV Allrad	Stufenheck	Allrad	Elektro	Mar 2023	-	152823
Xpeng	P7+	EV AWD	Schrägheck	Allrad	Elektro	Mar 2026	-	164016
Yudo	1	EV	Schrägheck	Heckantrieb	Elektro	Apr 2026	-	164518
Yudo	2	1.5	SUV	Frontantrieb	Benzin	Dec 2024	-	161664
Yudo	2	1.5	SUV	Frontantrieb	Benzin	Dec 2024	-	161665
Yudo	2	1.5	SUV	Frontantrieb	Benzin	Apr 2026	-	164512
Yudo	3	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Apr 2026	-	164516
Yudo	4	EV	Stufenheck	Frontantrieb	Elektro	Dec 2024	-	161669
Yudo	6	2.0 Allrad	SUV	Allrad	Benzin	Mar 2026	-	164417
Yudo	Yuntu	EV	SUV	Frontantrieb	Elektro	Feb 2023	-	152687
Zastava	Koral	1.1	Schrägheck	Frontantrieb	Benzin	Oct 2002	Nov 2008	50850
Zastava	Koral	1.1	Schrägheck	Frontantrieb	Benzin	Oct 2002	Nov 2008	50852
ZAZ	Tavria	1.2 S	Schrägheck	Frontantrieb	Benzin	Feb 1987	Dec 2007	11129
ZD	D2s	Electric	Schrägheck	Frontantrieb	Elektro	Aug 2021	-	123577
ZD	D2s	Electric	Schrägheck	Frontantrieb	Elektro	Nov 2019	-	154987
ZD	D2s	Electric	Schrägheck	Frontantrieb	Elektro	Nov 2019	-	154989
Zeekr	1	EV	Schrägheck	Heckantrieb	Elektro	Apr 2021	-	144844
Zeekr	1	EV Allrad	Schrägheck	Allrad	Elektro	Apr 2021	-	144846
Zeekr	7gt	EV	Kombi	Heckantrieb	Elektro	Apr 2025	-	161373
Zeekr	7gt	EV Allrad	Kombi	Allrad	Elektro	Apr 2025	-	161374
Zeekr	7x	EV	SUV	Heckantrieb	Elektro	Sep 2024	-	159812
Zeekr	7x	EV	SUV	Allrad	Elektro	Sep 2024	-	159813
Zeekr	7x	EV	SUV	Allrad	Elektro	Sep 2024	-	160480
Zeekr	X	EV	SUV	Heckantrieb	Elektro	Apr 2023	-	153586
Zeekr	X	EV Allrad	SUV	Allrad	Elektro	Apr 2023	-	153587
Zenvo	St1	7	Coupe	Heckantrieb	Benzin	Mar 2009	-	801849
Zuendapp	Janus	0.25	Schrägheck	Heckantrieb	Gemisch	Sep 1957	Dec 1958	115525


--- Round 1 / 首次发送 ---
## 更新点

本批 48 个 Ktype 已全部闭合，共复用或建立 28 个尺寸组。动力类型与生产日期造成的重复已合并；XPeng G9 按官方规格保留 RWD 1680 mm、AWD 1670 mm 两个实际高度分支；Yudo 6 在 Ktype 未指定 Navigator 的情况下采用基础 Adventurer 外廓；Zeekr 001、7X 未对 Ktype 未明确覆盖的低车高悬架配置进行猜测性拆分。([XPeng Inc.][1])

## 进度

`READY=48`
`PENDING=0`
`DIMENSION_GROUP=28`

机械终检通过：固定表头正确、ID 唯一、48 个输入 Ktype 全覆盖、映射引用闭合、尺寸为正整数、来源及 URL 非空、无孤立尺寸组。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13368	13368	Convertible	MF3		2	EU-WIESMANN-MF3-GEN1-CONVERTIBLE-STD-01	HIGH		READY
17888	17888	Convertible	MF3		2	EU-WIESMANN-MF3-GEN1-CONVERTIBLE-STD-01	HIGH		READY
124747	124747	Convertible	MF3		2	EU-WIESMANN-MF3-GEN1-CONVERTIBLE-STD-01	HIGH		READY
10074	10074	Convertible	MF4		2	EU-WIESMANN-MF4-GEN1-CONVERTIBLE-STD-01	HIGH		READY
10076	10076	Convertible	MF5		2	EU-WIESMANN-MF5-GEN1-CONVERTIBLE-STD-01	HIGH		READY
110276	110276	Convertible	MF5		2	EU-WIESMANN-MF5-GEN1-CONVERTIBLE-STD-01	HIGH		READY
146228	146228	MPV	XBUS			EU-XBUS-XBUS-GEN1-MPV-PASSENGER-01	MEDIUM	Passenger module selected from input BodyStyle.	READY
146226	146226	Pickup	XBUS			EU-XBUS-XBUS-GEN1-PICKUP-FLATBED-01	MEDIUM	Flatbed/chassis module selected from input BodyStyle.	READY
146227	146227	Van	XBUS			EU-XBUS-XBUS-GEN1-VAN-CARGO-01	MEDIUM	Cargo van module selected from input BodyStyle.	READY
148107	148107	Hatchback	YOYO		2	EU-XEV-YOYO-GEN1-HATCHBACK-STD-01	HIGH		READY
146029	146029	SUV	G3i 2021		5	EU-XPENG-G3I-2021-SUV-STD-01	HIGH		READY
800228	800228	SUV	G6		5	EU-XPENG-G6-GEN1-SUV-STD-01	HIGH		READY
800259	800259	SUV	G6		5	EU-XPENG-G6-GEN1-SUV-STD-01	HIGH		READY
800260	800260	SUV	G6		5	EU-XPENG-G6-GEN1-SUV-STD-01	HIGH		READY
155404	155404	SUV	G6		5	EU-XPENG-G6-GEN1-SUV-STD-01	HIGH		READY
800715	800715	SUV	G6		5	EU-XPENG-G6-GEN1-SUV-STD-01	HIGH		READY
150157	150157	SUV	G9		5	EU-XPENG-G9-GEN1-SUV-RWD-01	HIGH		READY
801587	801587	SUV	G9		5	EU-XPENG-G9-GEN1-SUV-RWD-01	HIGH		READY
150158	150158	SUV	G9		5	EU-XPENG-G9-GEN1-SUV-AWD-01	HIGH		READY
801588	801588	SUV	G9		5	EU-XPENG-G9-GEN1-SUV-AWD-01	HIGH		READY
152822	152822	Sedan	P7 2023		4	EU-XPENG-P7-2023-SEDAN-STD-01	HIGH		READY
152823	152823	Sedan	P7 2023		4	EU-XPENG-P7-2023-SEDAN-STD-01	HIGH		READY
164016	164016	Hatchback	P7+		5	EU-XPENG-P7PLUS-GEN1-HATCHBACK-STD-01	HIGH		READY
164518	164518	Hatchback	YOOUDOOO 1			EU-YUDO-1-GEN1-HATCHBACK-STD-01	MEDIUM		READY
161664	161664	SUV	YOOUDOOO 2		5	EU-YUDO-2-GEN1-SUV-STD-01	MEDIUM		READY
161665	161665	SUV	YOOUDOOO 2		5	EU-YUDO-2-GEN1-SUV-STD-01	MEDIUM		READY
164512	164512	SUV	YOOUDOOO 2		5	EU-YUDO-2-GEN1-SUV-STD-01	MEDIUM		READY
164516	164516	SUV	YOOUDOOO 3 MAX		5	EU-YUDO-3MAX-GEN1-SUV-STD-01	MEDIUM		READY
161669	161669	Sedan	YOOUDOOO 4		4	EU-YUDO-4-GEN1-SEDAN-STD-01	MEDIUM		READY
164417	164417	SUV	YOOUDOOO 6 (BAW 212)		5	EU-YUDO-6-BAW212-SUV-ADVENTURER-01	MEDIUM	Standard Adventurer body selected; Navigator trim not asserted for this Ktype.	READY
152687	152687	SUV	Yuntu		5	EU-YUDO-YUNTU-GEN1-SUV-STD-01	HIGH		READY
50850	50850	Hatchback	Yugo Koral		3	EU-ZASTAVA-KORAL-GEN1-HATCHBACK-STD-01	HIGH		READY
50852	50852	Hatchback	Yugo Koral		3	EU-ZASTAVA-KORAL-GEN1-HATCHBACK-STD-01	HIGH		READY
11129	11129	Hatchback	1102 Tavria	1102	3	EU-ZAZ-TAVRIA-1102-HATCHBACK-STD-01	HIGH		READY
123577	123577	Hatchback	D2S		3	EU-ZD-D2S-GEN1-HATCHBACK-STD-01	MEDIUM	Minor published length variance treated as one homologated body.	READY
154987	154987	Hatchback	D2S		3	EU-ZD-D2S-GEN1-HATCHBACK-STD-01	MEDIUM	Minor published length variance treated as one homologated body.	READY
154989	154989	Hatchback	D2S		3	EU-ZD-D2S-GEN1-HATCHBACK-STD-01	MEDIUM	Minor published length variance treated as one homologated body.	READY
144844	144844	Hatchback	001		5	EU-ZEEKR-001-GEN1-HATCHBACK-STD-01	HIGH		READY
144846	144846	Hatchback	001		5	EU-ZEEKR-001-GEN1-HATCHBACK-STD-01	MEDIUM	Standard-height body used; air-suspension trim not asserted for this Ktype.	READY
161373	161373	Wagon	007 GT		5	EU-ZEEKR-7GT-GEN1-WAGON-STD-01	HIGH		READY
161374	161374	Wagon	007 GT		5	EU-ZEEKR-7GT-GEN1-WAGON-STD-01	HIGH		READY
159812	159812	SUV	7X		5	EU-ZEEKR-7X-GEN1-SUV-STD-01	MEDIUM	Standard-height body used; lower-height trim not asserted for this Ktype.	READY
159813	159813	SUV	7X		5	EU-ZEEKR-7X-GEN1-SUV-STD-01	MEDIUM	Standard-height body used; lower-height trim not asserted for this Ktype.	READY
160480	160480	SUV	7X		5	EU-ZEEKR-7X-GEN1-SUV-STD-01	MEDIUM	Standard-height body used; lower-height trim not asserted for this Ktype.	READY
153586	153586	SUV	X		5	EU-ZEEKR-X-GEN1-SUV-STD-01	HIGH		READY
153587	153587	SUV	X		5	EU-ZEEKR-X-GEN1-SUV-STD-01	HIGH		READY
801849	801849	Coupe	ST1		2	EU-ZENVO-ST1-GEN1-COUPE-STD-01	HIGH		READY
115525	115525	Hatchback	Janus 250		2	EU-ZUENDAPP-JANUS-250-HATCHBACK-STD-01	MEDIUM		READY
```

[下载 left18448_18401-18448_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_18401-18448_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-WIESMANN-MF3-GEN1-CONVERTIBLE-STD-01	3860	1750	1160	Auto-Data	https://www.auto-data.net/en/wiesmann-roadster-mf3-3.2i-24v-325hp-10855
EU-WIESMANN-MF4-GEN1-CONVERTIBLE-STD-01	4230	1880	1190	Auto-Data	https://www.auto-data.net/en/wiesmann-roadster-mf4-generation-5062
EU-WIESMANN-MF5-GEN1-CONVERTIBLE-STD-01	4220	1950	1180	Auto-Data	https://www.auto-data.net/en/wiesmann-roadster-mf5-generation-5063
EU-XBUS-XBUS-GEN1-MPV-PASSENGER-01	3960	1640	1960	Dan Seaman Motors	https://www.danseamanmotors.ie/blog?id=190
EU-XBUS-XBUS-GEN1-PICKUP-FLATBED-01	3960	1640	1960	Dan Seaman Motors	https://www.danseamanmotors.ie/blog?id=190
EU-XBUS-XBUS-GEN1-VAN-CARGO-01	3960	1640	1960	Dan Seaman Motors	https://www.danseamanmotors.ie/blog?id=190
EU-XEV-YOYO-GEN1-HATCHBACK-STD-01	2530	1500	1560	Carfolio	https://www.carfolio.com/xev-yoyo-798171
EU-XPENG-G3I-2021-SUV-STD-01	4495	1820	1610	XPeng official specifications	https://www.xiaopeng.com/g3i/configuration.html
EU-XPENG-G6-GEN1-SUV-STD-01	4753	1920	1650	XPeng official specifications	https://www.xpeng.com/ae/g6specs.html
EU-XPENG-G9-GEN1-SUV-RWD-01	4891	1937	1680	XPeng official specifications	https://www.xpeng.com/ae/g9specs.html
EU-XPENG-G9-GEN1-SUV-AWD-01	4891	1937	1670	XPeng official specifications	https://www.xpeng.com/ae/g9specs.html
EU-XPENG-P7-2023-SEDAN-STD-01	4888	1896	1450	XPeng official specifications	https://www.xpeng.com/ae/p7.html
EU-XPENG-P7PLUS-GEN1-HATCHBACK-STD-01	5056	1937	1512	XPeng official specifications	https://www.xpeng.com/fi/test-4
EU-YUDO-1-GEN1-HATCHBACK-STD-01	3000	1510	1630	Diariomotor	https://www.diariomotor.com/noticia/yooudooo-1-detalles/
EU-YUDO-2-GEN1-SUV-STD-01	4380	1810	1615	Qué coche me compro	https://www.quecochemecompro.com/precios/yudo-2/yudo-2-pro-15t-dct/
EU-YUDO-3MAX-GEN1-SUV-STD-01	4590	1880	1608	Cimosa Motor	https://cimosamotor.es/YOOUDOOO-3-MAX/
EU-YUDO-4-GEN1-SEDAN-STD-01	4675	1835	1480	Qué coche me compro	https://www.quecochemecompro.com/precios/yudo-4-electrico/
EU-YUDO-6-BAW212-SUV-ADVENTURER-01	4705	1895	1936	Coches.net	https://www.coches.net/noticias/yooudooo-6-todoterreno-gasolina
EU-YUDO-YUNTU-GEN1-SUV-STD-01	4035	1736	1625	Yudo official specifications	https://www.yudoauto.com.tr/en/teknik-ozellikler.php
EU-ZASTAVA-KORAL-GEN1-HATCHBACK-STD-01	3552	1548	1345	Auto-Data	https://www.auto-data.net/en/zastava-yugo-koral-1.1-60hp-11668
EU-ZAZ-TAVRIA-1102-HATCHBACK-STD-01	3708	1554	1410	Auto-Data	https://www.auto-data.net/en/zaz-1102-1.1-53hp-13942
EU-ZD-D2S-GEN1-HATCHBACK-STD-01	2811	1499	1555	Coches.net / JATO Dynamics	https://www.coches.net/fichas_tecnicas/zhidou/d2s/berlina/3-puertas/17kw_23cv_electrico/108904/822931120210101/
EU-ZEEKR-001-GEN1-HATCHBACK-STD-01	4970	1999	1560	Auto-Data	https://www.auto-data.net/en/zeekr-001-model-3263
EU-ZEEKR-7GT-GEN1-WAGON-STD-01	4864	1900	1460	Zeekr Group official launch	https://www.zeekrgroup.com/en/news/202504151
EU-ZEEKR-7X-GEN1-SUV-STD-01	4825	1930	1666	CarNewsChina / MIIT specifications	https://carnewschina.com/2025/09/10/new-zeekr-7x-ev-outputs-784hp-and-has-up-to-802km-range/
EU-ZEEKR-X-GEN1-SUV-STD-01	4450	1836	1572	BorderlessCar specifications	https://www.borderlesscar.com/product/zeekr-x/
EU-ZENVO-ST1-GEN1-COUPE-STD-01	4665	2041	1198	Auto-Data	https://www.auto-data.net/en/zenvo-st1-generation-5920
EU-ZUENDAPP-JANUS-250-HATCHBACK-STD-01	2890	1410	1400	Auta5P catalog	https://auta5p.eu/lang/en/katalog/auto.php?idf=Zundapp-Janus-250-17514
```

[下载 left18448_18401-18448_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_18401-18448_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://ir.xiaopeng.com/news-releases/news-release-details/xpeng-launches-g9-flagship-suv?utm_source=chatgpt.com "XPENG Launches G9 Flagship SUV | XPeng Inc."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5456 行）
- 累计尺寸组：dimension_groups_final.tsv（1276 行）

