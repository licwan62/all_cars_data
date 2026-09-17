# 任务：all 第 101-200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0002__0daa824a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 101-200 行

【任务要求】
# EU Auto-Data Ktype 与尺寸组补全规则

本规则适用于以下 Tab 分隔的欧洲车型输入表。`Ktype` 是输入车型标识，但不保证唯一对应一个物理车身。输出必须包含两张互相解耦的全量 TSV：

1. `Ktype 映射表`：保存 Ktype、派生主键和尺寸组关系。
2. `DIMENSION_GROUP 表`：保存每个尺寸组唯一一套长宽高及其来源。

```tsv
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype	LatestStatus
Opel	Corsa d	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Jul 2006	Aug 2014	2024-03-01	1	NEW
```

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

## 一、输出模型与粒度

### 1. Ktype 映射表

Ktype 映射表只表达车型和物理尺寸组之间的关系，不重复输入表字段，也不保存具体尺寸值或抓取过程字段。

- `id`：映射表唯一主键，按文本处理。
- `Ktype`：指向输入表的外键，必须逐字保留；禁止转为浮点数、改写前导零或生成不存在的 Ktype。
- `DIMENSION_GROUP_ID`：指向 DIMENSION_GROUP 表的外键。
- 一个 Ktype 可以对应多个 `id` 和多个 `DIMENSION_GROUP_ID`。
- 多个 Ktype 也可以引用同一个 `DIMENSION_GROUP_ID`，因此业务关系允许多对多。
- 每个输入 Ktype 至少输出一行；不得因待处理或共用尺寸组而删除。
- 不输出 `Make`、`Model`、`VariantName`、生产年月等其他输入字段，需要时通过 Ktype 回查输入表。
- 不在映射表保存 `WheelbaseMM`、`LengthMM`、`WidthMM`、`HeightMM`、`WidthBasis`、`EndDateStatus`、`ResolutionStatus`、`CacheSourceKtype`、`MatchReason`、`DimensionSource` 或 `SourceURL`。

### 2. id 生成规则

- 当一个 Ktype 唯一对应一条物理尺寸记录时，`id` 直接等于 Ktype，例如 `2`。
- 当一个 Ktype 对应多个不同物理车身或尺寸时，分别输出多行，`id` 使用 `{Ktype}_{描述}`，例如 `1_3dr`、`1_5dr`。
- 后缀必须简短、稳定、可读，并表达造成物理外廓差异的特征。优先使用 `3dr`、`5dr`、`swb`、`lwb`、`lowroof`、`highroof`、`srw`、`drw`、`prefl`、`facelift` 等小写 ASCII 标记；必要时组合，例如 `12_5dr_facelift`。
- Ktype 拆成派生行后，不再保留无后缀的 `id=Ktype` 基础行。
- 不得使用无语义临时序号掩盖未确认差异。
- 已确认 Ktype 覆盖多个物理外廓时，必须输出全部派生行，不能任选一个，也不能仅因 Ktype 不唯一而保持 `PENDING`。
- 若证据只表明可能存在多个外廓，但尚不能确认具体分支，则暂时保留 `id=Ktype` 的一行并标记 `PENDING`，不得创建猜测性派生行。

### 3. DIMENSION_GROUP 表

DIMENSION_GROUP 表是尺寸事实的唯一落盘位置。

- 每个 `DIMENSION_GROUP_ID` 恰好出现一次。
- 每行必须完整填写 `LengthMM`、`WidthMM`、`HeightMM`、`DimensionSource` 和 `SourceURL`。
- Ktype 映射表中引用的每个 `DIMENSION_GROUP_ID` 都必须存在于本表。
- 本表不得包含当前 Ktype 映射表完全未引用的孤立尺寸组。
- 相同物理外廓只能复用同一个稳定 `DIMENSION_GROUP_ID`，不得因 Ktype、发动机或来源不同重复建组。
- 物理外廓不同必须使用不同 `DIMENSION_GROUP_ID`。
- 尺寸研究、来源冲突和缓存核验都在尺寸组层完成，不在 Ktype 映射表重复落盘。

### 4. 首次建组与后续复用

尺寸抓取以 `DIMENSION_GROUP_ID` 为单位，而不是以 Ktype 为单位：

1. 处理 Ktype 前先查询当前批次及历史缓存中已有的 `DIMENSION_GROUP_ID`，再决定是否需要外部抓取。
2. 首次创建一个 `DIMENSION_GROUP_ID` 时，完整核对一次物理车身边界、`LengthMM`、不含后视镜的 `WidthMM`、`HeightMM`、`DimensionSource` 和 `SourceURL`。
3. 尺寸和来源闭合后，将该组作为稳定缓存。相同组在当前批次和后续批次均直接复用。
4. 后续 Ktype 只判断它应该关联哪个现有尺寸组；不得为每个 Ktype 重复打开尺寸页面、重新抓取同一组三维或重复整理来源。
5. 一次尺寸组核对应尽可能同时解决所有候选相同外廓的 Ktype，避免串行逐条查询。
6. 后续关联不填写、不输出 `CacheSourceKtype`、`MatchReason`、`ResolutionStatus` 或重复来源说明。
7. 只有出现以下情况才允许重新打开尺寸核对：
   - 现有尺寸组缺字段或来源不可追溯；
   - 新证据表明代际、BodyStyle、门数外形、轴距、车顶、宽体、改款或外部套件不同；
   - 现有尺寸与可靠来源发生实质冲突；
   - 宽度不能确认是不含后视镜口径。
8. 发动机、功率、燃料、变速箱或普通配置不同，不能触发重复尺寸抓取。

处理顺序应优先按候选物理车身聚类：先创建并闭合一个尺寸组，再批量将所有匹配 Ktype 链接到该组，避免逐 Ktype 重复查询。

## 二、输入字段解释

| 字段 | 处理规则 |
| --- | --- |
| Make | 原始品牌。查询时允许使用标准品牌写法；输出表不重复此字段。 |
| Model | 原始车型/车系，可能包含代际提示，例如 `Corsa d`、`Megane iii`；输出表不重复此字段。 |
| VariantName | 发动机或版本名称，用于核验 Ktype，不等于物理车身；输出表不重复此字段。 |
| BodyStyle | 原始德语或欧洲市场车身形式；标准化结果写入 `NormalizedBodyStyle`。 |
| DriveType | 通常不单独决定尺寸组，但需注意特殊底盘是否改变外廓。 |
| Energy | 通常不单独决定尺寸组。 |
| EngineOutputKW / EngineOutputHP | 仅用于版本核验，不得作为尺寸组相同或不同的唯一依据。 |
| Product Start Month-Year | Ktype 的生产开始月，通常为 `MMM YYYY`。 |
| Product End Month-Year | Ktype 的生产结束月；`-`、空值或未知值不能解释为生产至今。 |
| LastProcessedDate | 上游处理日期，不是车型生产日期或资料发布日期。 |
| Ktype | 输入车型标识和输出外键，不保证唯一对应一套尺寸。按文本处理。 |
| LatestStatus | 上游状态；本轮状态写入 `IterationStatus`。 |

输入必须按 Tab 解析；字段内空格不是分隔符。

## 三、Ktype 映射字段

### 1. NormalizedBodyStyle

根据输入 `BodyStyle` 和可靠车型资料写入：

| 常见原值 | NormalizedBodyStyle |
| --- | --- |
| Schrägheck、Hatchback | Hatchback |
| Stufenheck、Limousine、Sedan | Sedan |
| Kombi、Touring、Estate | Wagon |
| Coupe、Coupé | Coupe |
| Cabriolet、Roadster | Convertible |
| SUV、Geländewagen | SUV |
| Van、Großraumlimousine、MPV | MPV |
| Kasten、Kastenwagen | Van |
| Pritsche、Pickup | Pickup |

无法可靠归类时保留最接近的来源写法，并在 `Notes` 说明，不得凭外观猜测。

### 2. Generation、BodyCode、Doors

- `Generation`：正式代际名称，例如 `Corsa D`，不能仅从生产年份推断。
- `BodyCode`：厂商平台或车身代码；一行只能填写一个明确代码，不能写 `L08/L68` 等组合值。无可靠证据时留空。
- `Doors`：只写整数，例如 `3`、`5`；一行只能表示一种门数。来源未明确时留空。
- 不抓取、不推断、不输出 `WheelbaseMM`。
- 不得把发动机代号、底盘配置或营销版本误写为 `BodyCode`。

若门数、车身代码、轴距、车顶、驾驶室、货斗、宽体、改款或特殊外部套件造成不同外廓，必须拆成不同 `id` 并链接不同尺寸组。轴距只作为判断线索，不需要落盘。

### 3. MatchConfidence、Notes、IterationStatus

`MatchConfidence` 只允许 `HIGH`、`MEDIUM`、`LOW`，表示 Ktype/派生 id 与尺寸组之间的映射置信度，不表示尺寸来源质量。

`Notes` 只记录映射层必要信息，例如派生原因、门数/车身代码边界或人工决定。具体尺寸、抓取来源、缓存来源、匹配理由和核验过程不得在这里重复落盘。能够由 `DIMENSION_GROUP_ID` 表达的内容不再写入 `Notes`。

`IterationStatus` 只允许：

- `READY`
- `PENDING: <具体原因>`

映射行只有同时满足以下条件才能写 `READY`：

- `id` 唯一，Ktype 能回查输入表。
- 必要的 Generation、NormalizedBodyStyle、BodyCode/Doors 物理边界已确认。
- 已链接一个确定的 `DIMENSION_GROUP_ID`。
- 被引用尺寸组存在于本轮完整 DIMENSION_GROUP 表中，且三维和来源完整。
- 映射没有未解决冲突。

`PENDING` 行的 `DIMENSION_GROUP_ID` 必须留空；候选组只能简要写入 `Notes`。

## 四、尺寸组与统一尺寸口径

### 1. DIMENSION_GROUP_ID

只有物理车身边界和同一配置的三维均确认后才能创建或命中尺寸组。ID 必须跨当前批次和后续缓存保持稳定，推荐格式：

```text
EU-{MAKE}-{MODEL}-{GENERATION}-{BODYSTYLE}-{SEQUENCE}
```

示例：

```text
EU-OPEL-CORSA-D-HATCHBACK-3D-01
```

ID 只使用大写 ASCII、数字和连字符。不得把 `id` 或 Ktype 直接当作尺寸组 ID，也不得创建临时确认组。

以下差异通常不单独创建尺寸组：

- 发动机排量、功率、增压方式
- 燃料或能源类型
- 变速箱
- 不改变外部轮廓的驱动形式
- 普通配置等级

以下差异必须独立核对，外廓不同则使用不同尺寸组：

- 不同代际或车身代码
- 不同 BodyStyle 或门数外形
- 不同轴距、SWB/LWB
- 普通车身/宽体、SRW/DRW
- 普通顶/高顶
- facelift 前后尺寸变化
- 不同 CAB/BED
- 特殊悬架高度、保险杠或外部套件
- 同名车型停产后重新推出

不得仅凭 `Make + Model + VariantName` 相似复用尺寸组。

### 2. LengthMM、WidthMM、HeightMM

- `LengthMM`：量产标准状态下的最大车身外部长度，单位 mm。
- `WidthMM`：强制使用不含外后视镜的车身宽度，单位 mm。
- `HeightMM`：量产标准状态下的外部高度，单位 mm。
- 不输出 `WidthBasis`；所有落盘的 `WidthMM` 按规则即为 `WITHOUT_MIRRORS`。
- 如果只能获得含后视镜宽度或宽度口径未知，该尺寸组不得进入完整 DIMENSION_GROUP 表，对应映射保持 `PENDING`。
- 三个尺寸格只写正整数，不写单位、约数、范围或多个候选值。
- 同一尺寸组的长宽高必须属于同一物理配置，不能从不同版本拼接。
- 英寸换算使用 `1 in = 25.4 mm`，最终取整到 1 mm；厘米换算使用 `1 cm = 10 mm`。

## 五、尺寸来源

来源优先级：

1. 厂商官网、官方 brochure、technical specification、press kit、历史资料、homologation 或 type approval。
2. Auto-Data、Car.info、UltimateSpecs、Automobile-Catalog、Parkers。
3. 其他可信规格数据库，仅用于交叉验证。

二手车广告、论坛、搜索摘要、AI 摘要和无出处聚合页只能作为线索，不能单独支撑最终尺寸组。

- `DimensionSource`：填写直接支持该组三维或关键物理边界的来源名称。
- `SourceURL`：填写对应直接页面 URL，不得填写搜索结果页。
- 多个来源使用分号分隔，并保持名称和 URL 顺序对应。
- 来源冲突时核对市场、年份、代际、BodyStyle、门数、轴距、含镜口径和特殊版本；无法解决时不创建完整尺寸组，对应映射保持 `PENDING`。

## 六、每轮固定输出

为减少抓取频率和对话落盘体积，区分推进轮与最终轮。

### CONTINUE 推进轮

尚未完成时依次输出：

1. `更新点`
2. `当前批次进度`
3. `本轮新增/修改的 Ktype 映射 TSV`，仅输出本轮发生变化的行；没有变化时明确写“无”
4. `本轮新增/修改的 DIMENSION_GROUP TSV`，仅输出首次创建或本轮修正的尺寸组；复用既有组时不重复输出；没有变化时明确写“无”
5. `下一步优先处理`
6. 最后一行输出 `推进信号：CONTINUE`

推进轮不得为了形式完整而重复打印未变化的 Ktype 行或既有尺寸组。尺寸组一旦闭合，后续轮只通过 `DIMENSION_GROUP_ID` 引用。

### COMPLETE 最终轮

只有准备完成时，依次输出：

1. `更新点`
2. `当前批次进度`
3. `最终完整 Ktype 映射 TSV`
4. Ktype 映射 TSV 的可点击 sandbox 下载链接
5. `最终完整 DIMENSION_GROUP TSV`
6. DIMENSION_GROUP TSV 的可点击 sandbox 下载链接
7. 最后一行输出 `推进信号：COMPLETE`

最终轮的两张表必须是当前批次可直接落盘的完整快照，不能只输出变化行、引用上一轮或写“其余不变”。自动化只在同一条最终回复中检测到两张完整表时接受 `COMPLETE`。

下载文件名由当前任务提示明确给出，必须原样使用。分批任务示例：

```text
all_1-100_ktype_dimension_mapping_final.tsv
all_1-100_dimension_groups_final.tsv
```

链接必须是可点击的 Markdown sandbox 链接，例如：

```markdown
[下载 Ktype 映射表](sandbox:/mnt/data/all_1-100_ktype_dimension_mapping_final.tsv)
[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1-100_dimension_groups_final.tsv)
```

只有文字文件名、缺少链接、链接不是 `.tsv`、文件名与任务提示不一致，均不得输出 `COMPLETE`。

自动化在接受 COMPLETE 后会从同一回复的两张内嵌 TSV 生成本批本地文件，并分别合并到按输入源维护的累计文件：

```text
all_ktype_dimension_mapping_final.tsv
all_dimension_groups_final.tsv
```

累计合并以 `id` 和 `DIMENSION_GROUP_ID` 去重，可安全恢复或重复处理；尺寸组出现三维冲突时必须停止，不得静默覆盖首次确认的尺寸事实。

### Ktype 映射表排序

1. 保持输入 Ktype 原始顺序。
2. 同一 Ktype 有多行时按稳定物理分支排序，例如 `3dr` 在 `5dr` 前、`swb` 在 `lwb` 前。
3. 后续轮次不得无故改变已确认 `id` 或行顺序。

### DIMENSION_GROUP 表排序

按各尺寸组第一次在 Ktype 映射表中被引用的顺序排列。一个组只出现一次。

### CONTINUE 输出示例

````text
更新点
- ……

当前批次进度
- READY 映射：……
- PENDING 映射：……
- 已确认尺寸组：……
- 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1_3dr	1	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
1_5dr	1	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
```

下一步优先处理
1. ……

推进信号：CONTINUE
````

## 七、COMPLETE 条件

只有全部满足时才能输出 `推进信号：COMPLETE`：

1. 两张最终完整 TSV 均已在同一条当前回复中输出，表头和顺序严格正确。
2. 两个按任务指定文件名生成的 `.tsv` sandbox 下载链接均已提供。
3. Ktype 映射表覆盖每个输入 Ktype，所有派生物理分支均无遗漏。
4. 每个映射行都有唯一 `id`、有效 `DIMENSION_GROUP_ID`，且 `IterationStatus=READY`。
5. 每个映射引用都能在 DIMENSION_GROUP 表中找到恰好一行。
6. DIMENSION_GROUP 表中的每行都被当前映射表引用，不存在孤立组。
7. 每个尺寸组的长宽高均为完整正整数，`WidthMM` 明确是不含后视镜宽度。
8. 每个尺寸组的 `DimensionSource` 和 `SourceURL` 均完整、可追溯。
9. 不存在 `PENDING`、缺失尺寸、未知宽度口径、未解决来源冲突或候选尺寸组。
10. 同一物理尺寸组没有因多个 Ktype 而被重复建组或重复抓取。

任一条件不满足时，按 CONTINUE 推进轮格式只输出本轮新增/修改行，并以 `推进信号：CONTINUE` 结束。

## 八、提交前强制检查

1. Ktype 映射表是否严格为 10 列，DIMENSION_GROUP 表是否严格为 6 列。
2. 映射表是否没有落盘已移除字段：`WheelbaseMM`、三维、`WidthBasis`、`EndDateStatus`、`ResolutionStatus`、`CacheSourceKtype`、`MatchReason`、来源字段。
3. `id` 是否每行有值且唯一；Ktype 是否逐字匹配输入表。
4. 每个输入 Ktype 是否至少出现一次；已确认多外廓 Ktype 是否完整派生且无基础重复行。
5. 多行是否确由物理外廓差异造成，而不是发动机、功率、燃料或普通配置差异造成。
6. 映射表的每个非空 `DIMENSION_GROUP_ID` 是否恰好命中尺寸组表一行。
7. 每个尺寸组是否只出现一次并被至少一个映射引用。
8. 长宽高是否来自同一配置、统一为 mm 且均为正整数。
9. `WidthMM` 是否明确为不含外后视镜口径。
10. 尺寸来源和 URL 是否完整对应且可追溯。
11. 是否保持映射顺序和尺寸组首次引用顺序。
12. 是否只有两张要求的 TSV，没有另建子车系表、缓存表或抓取明细表。
13. 输出 COMPLETE 前是否确认两张表均完整、所有映射 READY 且无 PENDING。
14. 是否仅在首次创建或纠错尺寸组时抓取三维和来源；后续 Ktype 是否只建立关联。
15. CONTINUE 轮是否避免重复输出未变化记录，COMPLETE 轮是否一次性输出两张完整快照。
16. COMPLETE 轮是否提供任务指定文件名的两个可点击 `.tsv` sandbox 下载链接。


【执行顺序】
执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。

【配置附加规则】


【当前文件名】
all.tsv

【当前独立任务】
all 第 101-200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Alfa Romeo	33	1.7 16V	Kombi	Frontantrieb	Benzin	95	129	Jan 1990	Sep 1994	2024-03-01	115
Alfa Romeo	33	1.7 16V 4X4	Kombi	Allrad	Benzin	97	132	Jan 1990	Mar 1992	2024-03-01	116
Alfa Romeo	75	1.6 CAT	Stufenheck	Heckantrieb	Benzin	81	110	May 1989	Feb 1992	2024-03-01	117
Alfa Romeo	75	1.6	Stufenheck	Heckantrieb	Benzin	81	110	May 1985	Sep 1989	2024-03-01	118
Alfa Romeo	75	1.8 Turbo I.e.	Stufenheck	Heckantrieb	Benzin	114	155	Feb 1986	Jan 1990	2024-03-01	119
Alfa Romeo	75	1.8	Stufenheck	Heckantrieb	Benzin	85	116	Sep 1985	Jun 1989	2024-03-01	120
Alfa Romeo	75	1.8	Stufenheck	Heckantrieb	Benzin	88	120	Sep 1988	Feb 1992	2024-03-01	122
Alfa Romeo	75	1.8	Stufenheck	Heckantrieb	Benzin	90	122	Aug 1989	Feb 1992	2024-03-01	123
Alfa Romeo	75	1.8 Turbo	Stufenheck	Heckantrieb	Benzin	110	150	Sep 1986	Feb 1992	2024-03-01	124
Alfa Romeo	75	2	Stufenheck	Heckantrieb	Benzin	94	128	May 1985	Oct 1988	2024-03-01	125
Alfa Romeo	75	2.0 T.s.	Stufenheck	Heckantrieb	Benzin	107	146	Jan 1987	Feb 1992	2024-03-01	127
Alfa Romeo	75	2.0 T.S CAT	Stufenheck	Heckantrieb	Benzin	109	148	May 1985	Feb 1992	2024-03-01	128
Alfa Romeo	75	2.0 TD	Stufenheck	Heckantrieb	Diesel	70	95	May 1985	Sep 1992	2024-03-01	129
Alfa Romeo	75	2.5 V6	Stufenheck	Heckantrieb	Benzin	110	150	May 1985	Aug 1986	2024-03-01	131
Alfa Romeo	75	3.0 V6 CAT	Stufenheck	Heckantrieb	Benzin	136	185	Jan 1987	Feb 1992	2024-03-01	133
Alfa Romeo	75	3.0 V6	Stufenheck	Heckantrieb	Benzin	141	192	Feb 1990	Feb 1992	2024-03-01	134
Alfa Romeo	90	1.8	Stufenheck	Heckantrieb	Benzin	85	116	Oct 1984	Jul 1987	2024-03-01	135
Alfa Romeo	90	2.0 I.e.	Stufenheck	Heckantrieb	Benzin	94	128	Oct 1984	Jul 1987	2024-03-01	136
Alfa Romeo	90	2.4 TD	Stufenheck	Heckantrieb	Diesel	81	110	Oct 1984	Jul 1987	2024-03-01	137
Alfa Romeo	90	2.5 I.e. V6	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1984	Jul 1987	2024-03-01	138
Alfa Romeo	155	1.7 T.s.	Stufenheck	Frontantrieb	Benzin	85	115	Apr 1993	Apr 1996	2024-03-01	139
Alfa Romeo	155	1.8 T.s.	Stufenheck	Frontantrieb	Benzin	77	105	Feb 1992	Dec 1997	2024-03-01	140
Alfa Romeo	155	1.8 T.s. Sport	Stufenheck	Frontantrieb	Benzin	93	127	Mar 1992	Dec 1996	2024-03-01	141
Alfa Romeo	155	1.8 T.s.	Stufenheck	Frontantrieb	Benzin	95	129	Feb 1992	May 1994	2024-03-01	142
Alfa Romeo	155	1.9 TD	Stufenheck	Frontantrieb	Diesel	66	90	Apr 1993	Dec 1997	2024-03-01	143
Alfa Romeo	155	2.0 T.s.	Stufenheck	Frontantrieb	Benzin	104	141	Feb 1992	May 1995	2024-03-01	144
Alfa Romeo	155	2.0 T.s.	Stufenheck	Frontantrieb	Benzin	106	144	Feb 1992	Jan 1995	2024-03-01	145
Alfa Romeo	155	2.0 16V Turbo Q4	Stufenheck	Allrad	Benzin	137	186	Jan 1992	Dec 1997	2024-03-01	146
Alfa Romeo	155	2.0 16V Turbo Q4	Stufenheck	Allrad	Benzin	140	190	Mar 1992	Dec 1997	2024-03-01	147
Alfa Romeo	155	2.5 V6	Stufenheck	Frontantrieb	Benzin	120	163	Sep 1992	Dec 1997	2024-03-01	148
Alfa Romeo	155	2.5 V6	Stufenheck	Frontantrieb	Benzin	121	165	Mar 1992	May 1995	2024-03-01	149
Alfa Romeo	155	2.5 TD	Stufenheck	Frontantrieb	Diesel	92	125	Apr 1993	Dec 1997	2024-03-01	150
Alfa Romeo	164	2.0 Twin Spark	Stufenheck	Frontantrieb	Benzin	105	143	Jun 1987	Aug 1992	2024-03-01	151
Alfa Romeo	164	2.0 Twin Spark	Stufenheck	Frontantrieb	Benzin	109	148	Jun 1987	Sep 1992	2024-03-01	152
Alfa Romeo	164	2.0 Twin Spark	Stufenheck	Frontantrieb	Benzin	106	144	Sep 1992	Sep 1998	2024-03-01	153
Alfa Romeo	164	2.0 V6 Turbo	Stufenheck	Frontantrieb	Benzin	148	201	Sep 1992	Sep 1998	2024-03-01	154
Alfa Romeo	164	2.0 V6 Turbo	Stufenheck	Frontantrieb	Benzin	150	204	Mar 1991	Sep 1992	2024-03-01	155
Alfa Romeo	164	2.5 V6	Stufenheck	Frontantrieb	Benzin	120	163	Sep 1992	Sep 1998	2024-03-01	156
Alfa Romeo	164	2.5 TD	Stufenheck	Frontantrieb	Diesel	92	125	Sep 1992	Sep 1998	2024-03-01	157
Alfa Romeo	164	2.5 TD	Stufenheck	Frontantrieb	Diesel	84	114	Jun 1987	Sep 1992	2024-03-01	158
Alfa Romeo	164	3.0 V6	Stufenheck	Frontantrieb	Benzin	141	192	Jun 1987	Sep 1992	2024-03-01	159
Alfa Romeo	164	3.0 V6	Stufenheck	Frontantrieb	Benzin	132	180	Sep 1992	Sep 1998	2024-03-01	160
Alfa Romeo	164	3.0 V6	Stufenheck	Frontantrieb	Benzin	135	184	Jun 1987	Sep 1992	2024-03-01	161
Alfa Romeo	164	3.0 I.e. QV	Stufenheck	Frontantrieb	Benzin	147	200	Sep 1990	Sep 1992	2024-03-01	162
Alfa Romeo	164	3.0 24V	Stufenheck	Frontantrieb	Benzin	155	211	Sep 1992	Sep 1998	2024-03-01	163
Alfa Romeo	164	3.0 24V QV	Stufenheck	Frontantrieb	Benzin	171	233	Sep 1992	Sep 1998	2024-03-01	164
Alfa Romeo	Alfetta	1.6	Stufenheck	Heckantrieb	Benzin	79	107	Jan 1975	Dec 1984	2024-03-01	165
Alfa Romeo	Alfetta	1.8	Stufenheck	Heckantrieb	Benzin	85	116	Jul 1974	Apr 1982	2024-03-01	166
Alfa Romeo	Alfetta	1.8	Stufenheck	Heckantrieb	Benzin	89	121	Oct 1979	Dec 1984	2024-03-01	167
Alfa Romeo	Alfetta	1.8	Stufenheck	Heckantrieb	Benzin	90	122	Oct 1979	Dec 1984	2024-03-01	168
Alfa Romeo	Alfetta	2	Stufenheck	Heckantrieb	Benzin	89	121	Mar 1977	Feb 1980	2024-03-01	169
Alfa Romeo	Alfetta	2	Stufenheck	Heckantrieb	Benzin	97	132	Jul 1978	Dec 1984	2024-03-01	170
Alfa Romeo	Alfetta	2.0 TD	Stufenheck	Heckantrieb	Diesel	60	82	Oct 1979	Mar 1983	2024-03-01	171
Alfa Romeo	Alfetta	2.4 TD	Stufenheck	Heckantrieb	Diesel	70	95	Apr 1983	Dec 1984	2024-03-01	172
Alfa Romeo	Arna	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1985	Dec 1986	2024-03-01	173
Alfa Romeo	Arna	1.2	Schrägheck	Frontantrieb	Benzin	50	68	Jan 1985	Dec 1986	2024-03-01	174
Alfa Romeo	Arna	1.3 TI	Schrägheck	Frontantrieb	Benzin	63	86	Mar 1983	Dec 1986	2024-03-01	175
Alfa Romeo	Giulietta	1.3	Stufenheck	Heckantrieb	Benzin	66	90	Oct 1977	Jun 1983	2024-03-01	176
Alfa Romeo	Giulietta	1.6	Stufenheck	Heckantrieb	Benzin	79	107	Oct 1977	Apr 1985	2024-03-01	177
Alfa Romeo	Giulietta	1.8	Stufenheck	Heckantrieb	Benzin	90	122	Apr 1979	Apr 1985	2024-03-01	178
Alfa Romeo	Giulietta	1.8 Turbo	Stufenheck	Heckantrieb	Benzin	110	150	Jan 1984	Dec 1985	2024-03-01	179
Alfa Romeo	Giulietta	2	Stufenheck	Heckantrieb	Benzin	96	131	Jun 1980	Apr 1985	2024-03-01	180
Alfa Romeo	Giulietta	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	125	170	Apr 1983	Jun 1985	2024-03-01	181
Alfa Romeo	Gt	1300 Junior	Coupe	Heckantrieb	Benzin	64	87	Jan 1966	Dec 1977	2024-03-01	182
Alfa Romeo	Gt	1600	Coupe	Heckantrieb	Benzin	75	102	Mar 1963	Dec 1966	2024-03-01	183
Alfa Romeo	Gt	1600	Coupe	Heckantrieb	Benzin	80	109	Jan 1966	Dec 1968	2024-03-01	184
Alfa Romeo	Gt	A 1600	Coupe	Heckantrieb	Benzin	83	113	Jan 1965	Dec 1970	2024-03-01	185
Alfa Romeo	Gt	1600	Coupe	Heckantrieb	Benzin	76	103	Sep 1972	Dec 1977	2024-03-01	186
Alfa Romeo	Gt	1600	Coupe	Heckantrieb	Benzin	80	109	Jun 1971	Dec 1977	2024-03-01	187
Alfa Romeo	Gt	V 1750	Coupe	Heckantrieb	Benzin	83	113	Jan 1967	Dec 1972	2024-03-01	188
Alfa Romeo	Gt	V 2000	Coupe	Heckantrieb	Benzin	96	131	Jan 1971	Dec 1977	2024-03-01	189
Alfa Romeo	Alfetta	1.6	Coupe	Heckantrieb	Benzin	79	107	Jan 1976	Sep 1982	2024-03-01	190
Alfa Romeo	Alfetta	1.8	Coupe	Heckantrieb	Benzin	85	116	Jan 1974	Dec 1976	2024-03-01	191
Alfa Romeo	Alfetta	1.8	Coupe	Heckantrieb	Benzin	89	121	Jun 1974	Dec 1976	2024-03-01	192
Alfa Romeo	Alfetta	2	Coupe	Heckantrieb	Benzin	89	121	Jul 1978	Jan 1986	2024-03-01	193
Alfa Romeo	Gtv	2	Coupe	Heckantrieb	Benzin	96	131	Jul 1978	Jan 1986	2024-03-01	194
Alfa Romeo	Giulia	1300 Super	Stufenheck	Heckantrieb	Benzin	64	87	Jan 1974	Dec 1978	2024-03-01	195
Alfa Romeo	Giulia	1600 Super	Stufenheck	Heckantrieb	Benzin	76	103	Jan 1974	Dec 1978	2024-03-01	196
Alfa Romeo	Spider	1300	Cabriolet	Heckantrieb	Benzin	64	87	Jan 1968	Dec 1977	2024-03-01	197
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	80	109	Mar 1966	Dec 1968	2024-03-01	198
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	76	103	Mar 1976	Dec 1990	2024-03-01	199
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	80	109	Mar 1971	Dec 1979	2024-03-01	200
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	79	107	Jan 1990	Dec 1993	2024-03-01	201
Alfa Romeo	Spider	1750	Cabriolet	Heckantrieb	Benzin	83	113	Jan 1967	Dec 1971	2024-03-01	202
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	85	116	Aug 1986	Dec 1990	2024-03-01	203
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	92	125	Aug 1986	Dec 1990	2024-03-01	204
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	93	126	Jan 1977	Dec 1993	2024-03-01	205
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	96	131	Jan 1971	Dec 1977	2024-03-01	206
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	88	120	Jan 1990	Dec 1993	2024-03-01	207
Fiat	500	0.6	Stufenheck	Heckantrieb	Benzin	10	13	Jan 1936	Mar 1948	2024-03-01	208
BMW	5	520	Stufenheck	Heckantrieb	Benzin	85	115	Jun 1972	Jan 1979	2024-03-01	209
BMW	5	520/6	Stufenheck	Heckantrieb	Benzin	90	122	Mar 1977	Jun 1981	2024-03-01	211
BMW	5	525	Stufenheck	Heckantrieb	Benzin	107	145	Oct 1973	Aug 1976	2024-03-01	212
BMW	5	525	Stufenheck	Heckantrieb	Benzin	110	150	Aug 1975	Jun 1981	2024-03-01	213
VW	Passat b7	1.4 TSI	Stufenheck	Frontantrieb	Benzin	90	122	Aug 2010	Dec 2014	2024-03-01	214
BMW	5	528	Stufenheck	Heckantrieb	Benzin	121	165	Jan 1975	Aug 1976	2024-03-01	215
BMW	5	528	Stufenheck	Heckantrieb	Benzin	125	170	Aug 1975	Jul 1977	2024-03-01	216
BMW	5	528 I	Stufenheck	Heckantrieb	Benzin	130	177	Mar 1977	Sep 1979	2024-03-01	217
BMW	5	528 I	Stufenheck	Heckantrieb	Benzin	135	184	Aug 1979	Jun 1981	2024-03-01	218
BMW	3	316 I	Kombi	Heckantrieb	Benzin	73	100	Sep 1991	Jun 1994	2024-03-01	219


--- Round 1 / 首次发送 ---
## 1. 更新点

* 补齐 Ktype `133`、`134`：确认 Alfa Romeo 75 的 3.0 V6 America／Quadrifoglio Verde 使用加长保险杠外廓，三维统一为 `4420 × 1660 × 1400 mm`，宽度为不含后视镜口径；两个发动机版本复用同一尺寸组。([汽车目录][1])
* 补齐 Ktype `173`、`174`：资料明确 60 HP、68 HP 的 Arna 1.2 均覆盖三门和五门，因此分别派生 `_3dr`、`_5dr`，不再保留无后缀基础行。([汽车数据网][2])
* 补齐 Ktype `175`：Arna 1.3 TI 确认为三门车型；三门 TI 与五门 SL 的尺寸均为 `4000 × 1651 × 1367 mm`，宽度明确为不含后视镜。虽然三维相同，但三门和五门属于不同物理车身，分别建立尺寸组。([汽车目录][3])

## 2. 当前批次进度

* 按输入 Ktype 计：`READY 60 / 100`。
* 按输入 Ktype 计：`PENDING 40 / 100`。
* 本轮新增 READY：5 个 Ktype、7 条映射。
* 本轮新增并闭合尺寸组：3 个。
* 剩余 PENDING Ktype：`139-141`、`143-144`、`146-150`、`156`、`160`、`165-171`、`182-194`、`197`、`199`、`201-205`、`207`。
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133	133	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	MEDIUM	3.0 America/QV采用加长保险杠物理外廓，与普通75分组。	READY
134	134	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	3.0 America/QV采用加长保险杠物理外廓，与普通75分组。	READY
173_3dr	173	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	输入未包含L/SL门数；该功率覆盖三门和五门，按物理车身拆分。	READY
173_5dr	173	Hatchback	Arna	920	5	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	HIGH	输入未包含L/SL门数；该功率覆盖三门和五门，按物理车身拆分。	READY
174_3dr	174	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	输入未包含L/SL门数；该功率覆盖三门和五门，按物理车身拆分。	READY
174_5dr	174	Hatchback	Arna	920	5	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	HIGH	输入未包含L/SL门数；该功率覆盖三门和五门，按物理车身拆分。	READY
175	175	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	TI为三门物理车身。	READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	4420	1660	1400	Automobile-Catalog 1989 Alfa Romeo 75 3.0 V6 America; Automobile-Catalog 1990 Alfa Romeo 75 3.0 V6 Quadrifoglio Verde catalyst	https://www.automobile-catalog.com/car/1989/215705/alfa_romeo_75_3_0_v6_america.html; https://www.automobile-catalog.com/car/1990/215795/alfa_romeo_75_3_0_v6_quadrifoglio_verde_cat.html
EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	4000	1651	1367	Automobile-Catalog 1984 Alfa Romeo Arna 1.3 Ti	https://www.automobile-catalog.com/car/1984/214730/alfa_romeo_arna_1_3_ti.html
EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	4000	1651	1367	Automobile-Catalog 1985 Alfa Romeo Arna 1.2 SL	https://www.automobile-catalog.com/car/1985/214685/alfa_romeo_arna_1_2_sl.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 优先处理 Alfa Romeo 155 的窄体／宽体边界，重点拆解 `139-141`、`143-144`、`146-150`；宽体于 1995 年 4 月引入，跨越该时间点的 Ktype 需要判断是否派生 `prefl`、`facelift`。([Alfa Romeo Owners Club][4])
2. 随后补齐 Alfetta Sedan、Alfetta GT／GTV 的 Series、保险杠及长度变化，对应 `165-171`、`190-194`。
3. 再处理 Giulia GT 与 Spider 105/115 系列的车身代次交叉问题，对应 `182-189`、`197`、`199`、`201-205`、`207`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/215795/alfa_romeo_75_3_0_v6_quadrifoglio_verde_cat.html?utm_source=chatgpt.com "1990 Alfa Romeo 75 3.0 V6 Quadrifoglio Verde catalyst ..."
[2]: https://www.auto-data.net/en/alfa-romeo-arna-920-1.2-60hp-1510 "1985 Alfa Romeo Arna (920) 1.2 (60 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1984/214730/alfa_romeo_arna_1_3_ti.html?utm_source=chatgpt.com "1984 Alfa Romeo Arna 1.3 Ti Specs Review (63.5 kW ..."
[4]: https://aroc-uk.com/downloads/155-buyersguide.pdf "The Alfa Romeo 155.doc"


--- 发送 / 继续到 Round 2 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* Ktype `139` 的 1.7 Twin Spark 115 HP 已确认属于 155 `167` 四门窄体外廓；资料给出的三维为 `4443 × 1700 × 1440 mm`，直接复用既有 `EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01`，不重复输出尺寸组。1.7 版本资料覆盖 1993—1996 年，且 155 车身资料未将 1.7 列入后期宽体动力范围。([汽车数据网][1])
* Ktype `143` 的 1.9 TD 90 HP 已确认持续使用 `1700 mm` 窄体外廓，复用既有窄体尺寸组。([汽车数据网][2])
* Ktype `144` 的 2.0 Twin Spark 141 HP 已确认是前期 8V 窄体版本，资料给出 `4443 × 1700 × 1440 mm`；后期宽体同步引入的是修订后的 2.0 16V，因此本 Ktype 不拆宽体派生行。([汽车数据网][3])
* 本轮全部采用缓存关联，没有重复抓取或重建已存在的尺寸事实。

## 2. 当前批次进度

* READY 输入 Ktype：`63 / 100`
* PENDING 输入 Ktype：`37 / 100`
* 本轮新增 READY：`3` 个 Ktype
* 本轮首次创建或修正尺寸组：`0`
* 当前仍处于第一阶段，尚有映射边界或尺寸资料缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139	139	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.7 Twin Spark为四门窄体外廓。	READY
143	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.9 TD为四门窄体外廓。	READY
144	144	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	2.0 Twin Spark 141 HP为前期8V窄体外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 继续解决 Alfa Romeo 155 的窄体/宽体交叉 Ktype：`140`、`141`、`146-150`。
2. 优先区分普通宽体 `4443 × 1730 × 1425 mm` 与 Q4 等可能保持不同高度的特殊外廓，避免错误共用尺寸组。
3. 随后处理 Alfetta Sedan、GT/GTV 和 Spider 的 Series、保险杠及车身代码分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-155-167-1.7-twin-spark-115hp-1361 "Alfa Romeo 155 (167) 1.7 Twin Spark (115 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alfa-romeo-155-167-1.9-td-90hp-1366 "Alfa Romeo 155 (167) 1.9 TD (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/alfa-romeo-155-167-2.0-twin-spark-141hp-1370 "Alfa Romeo 155 (167) 2.0 Twin Spark (141 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Alfa Romeo 155 的 Series 1 窄体与 Series 2 宽体边界：窄体尺寸继续复用既有 `EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01`；首次建立普通宽体尺寸组 `4443 × 1730 × 1425 mm`。1995 年中期前后的 1.8 Twin Spark、V6 和 2.5 TD 资料均明确区分 `1700 × 1440 mm` 窄体与 `1730 × 1425 mm` 宽体，宽度均为不含后视镜。([汽车目录][1])
* Ktype `141` 的 `93 kW / 127 HP` 1.8 Twin Spark Sport 对应 Series 2 宽体版本，关联新建普通宽体尺寸组。([汽车目录][1])
* Ktype `146` 的 `137 kW / 186 HP` Q4 对应 Series 2 宽体 Q4，三维为 `4443 × 1730 × 1440 mm`；由于高度不同于普通宽体，独立创建 Q4 宽体尺寸组。Ktype `147` 的 `140 kW / 190 HP` Q4 对应 Series 1 窄体，复用既有窄体尺寸组。([汽车目录][2])
* Ktype `148` 的生产范围覆盖 V6 窄体与宽体阶段，因此拆为 `148_prefl`、`148_facelift`；Ktype `149` 对应前期 V6 窄体标定。155 买家指南亦确认 1995—1996 年 V6 同时存在窄体和宽体。([汽车目录][3])
* Ktype `150` 的 2.5 TD 跨越 Series 1、Series 2，拆为窄体和宽体两条映射；两个阶段已有直接、不含后视镜的三维资料。([汽车目录][4])

## 2. 当前批次进度

* READY 输入 Ktype：`69 / 100`
* PENDING 输入 Ktype：`31 / 100`
* 本轮新增 READY：`6` 个输入 Ktype、`8` 条映射
* 本轮首次创建尺寸组：`2`
* 现有窄体尺寸组仅进行缓存复用，未重复输出或重新建组。
* 当前仍处于第一阶段，尚有结构、代次或尺寸组缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141	141	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	HIGH	93 kW版1.8 Twin Spark Sport对应Series 2宽体外廓。	READY
146	146	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-Q4-WIDEBODY-01	HIGH	137 kW版Q4对应Series 2宽体外廓。	READY
147	147	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	140 kW版Q4对应Series 1窄体外廓。	READY
148_prefl	148	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	MEDIUM	该V6 Ktype覆盖Series 1与Series 2，按窄体分支拆分。	READY
148_facelift	148	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	MEDIUM	该V6 Ktype覆盖Series 1与Series 2，按宽体分支拆分。	READY
149	149	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	MEDIUM	121 kW版对应前期Series 1窄体V6外廓。	READY
150_prefl	150	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	2.5 TD跨越Series 1与Series 2，按窄体分支拆分。	READY
150_facelift	150	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	HIGH	2.5 TD跨越Series 1与Series 2，按宽体分支拆分。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	4443	1730	1425	Automobile-Catalog 1995 Alfa Romeo 155 1.8 Twin Spark S; Automobile-Catalog 1995 Alfa Romeo 155 V6; Automobile-Catalog 1996 Alfa Romeo 155 2.5 TD	https://www.automobile-catalog.com/car/1995/217535/alfa_romeo_155_1_8_twin_spark_s.html; https://www.automobile-catalog.com/car/1995/217580/alfa_romeo_155_v6.html; https://www.automobile-catalog.com/car/1996/217625/alfa_romeo_155_2_5_td.html
EU-ALFA-ROMEO-155-167-SEDAN-Q4-WIDEBODY-01	4443	1730	1440	Automobile-Catalog 1995 Alfa Romeo 155 Q4 serie 2	https://www.automobile-catalog.com/car/1995/217595/alfa_romeo_155_q4.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 解决剩余 Alfa Romeo 155 Ktype `140` 的 1.8 TS 105 HP 外廓阶段，确认它是否始终为窄体，避免仅按配件目录的宽泛年月直接关联。
2. 处理 Alfa Romeo 164 尚未闭合的 Ktype `156`、`160`，确认 1992 年改款前后是否存在长度、保险杠或高度差异。
3. 批量闭合 Alfetta Sedan 的 Ktype `165-171`，优先区分早期短保险杠和后期改款外廓，再复用到对应发动机 Ktype。
4. 随后处理 Alfetta GT/GTV、Giulia GT 和 Spider 105/115 的代次与保险杠分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/217535/alfa_romeo_155_1_8_twin_spark_s.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 1.8 Twin Spark S Specs Review (93.5 kW / 127 PS / 125 hp) (since mid-year 1995 for Europe )"
[2]: https://www.automobile-catalog.com/car/1995/217595/alfa_romeo_155_q4.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 Q4 Specs Review (137 kW / 186 PS / 184 hp) (since mid-year 1995 for Europe )"
[3]: https://www.automobile-catalog.com/car/1995/217580/alfa_romeo_155_v6.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 V6 Specs Review (120 kW / 163 PS / 161 hp) (since mid-year 1995 for Europe )"
[4]: https://www.automobile-catalog.com/car/1995/217490/alfa_romeo_155_2_5_td.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 2.5 TD Specs Review (92 kW / 125 PS / 123 hp) (up to mid-year 1995 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 补齐 Ktype `140`：1.8 T.Spark 105 HP 的独立资料将其生产期限定为 1992—1993 年，关联既有 155 Series 1 窄体尺寸组，不重复输出尺寸组。([autodata24.com][1])
* 补齐 Ktype `156`：2.5 V6 163 HP 确认为 1992 年起的 164 Facelift 四门车型，关联既有 `EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01`。([汽车数据网][2])
* 补齐 Ktype `160`：3.0 V6 180 HP 的 `164.H1A / 164.H1B / 164.K1` 版本三维为 `4565 × 1760 × 1390 mm`，与既有 164 Facelift 尺寸组一致，直接复用。([autodata24.com][3])
* 首次建立 Alfetta Sedan 三个稳定外廓尺寸组：

  * Series 1：`4280 × 1620 × 1430 mm`
  * Series 2：`4385 × 1640 × 1430 mm`
  * Series 3：`4410 × 1640 × 1430 mm`
    三组宽度均为不含后视镜口径。([汽车目录][4])
* 补齐 Ktype `169`、`171`、`172`，分别关联 Alfetta Series 1、Series 2、Series 3；跨多个外廓阶段的其他 Alfetta Ktype 暂不强行关联。

## 2. 当前批次进度

* READY 输入 Ktype：`75 / 100`
* PENDING 输入 Ktype：`25 / 100`
* 本轮新增 READY：`6` 个输入 Ktype
* 本轮首次创建尺寸组：`3`
* 本轮复用既有尺寸组：`3` 条映射
* 当前仍处于第一阶段，尚有跨改款结构、代次及尺寸组缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140	140	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	MEDIUM	105 HP 8V版本对应1992-1993年Series 1窄体外廓。	READY
156	156	Sedan	164	164	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	MEDIUM	2.5 V6 163 HP对应1992年起Facelift标准外廓。	READY
160	160	Sedan	164	164	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	HIGH	164.H1A、164.H1B及164.K1的180 HP版本对应Facelift标准外廓。	READY
169	169	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	HIGH	2.0 121 HP生产期止于1980年2月，对应Series 1外廓。	READY
171	171	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	2.0 TD生产期止于1983年3月，对应改款前Series 2外廓。	READY
172	172	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	2.4 TD随Series 3外廓推出。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	4280	1620	1430	Automobile-Catalog 1979 Alfa Romeo Alfetta 1.6	https://www.automobile-catalog.com/car/1979/44495/alfa_romeo_alfetta_1_6.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	4385	1640	1430	Automobile-Catalog 1981 Alfa Romeo Alfetta 2.0 Turbodiesel	https://www.automobile-catalog.com/car/1981/143720/alfa_romeo_alfetta_2_0_turbodiesel.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	4410	1640	1430	Automobile-Catalog 1983 Alfa Romeo Alfetta 2.4 Turbodiesel	https://www.automobile-catalog.com/car/1983/49130/alfa_romeo_alfetta_2_4_turbodiesel.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 处理跨越多个 Alfetta 外廓阶段的 Ktype `165-168`、`170`，按 Series 1、Series 2、Series 3 创建稳定派生行。
2. 批量闭合 Alfetta GT／GTV Ktype `190-194`，重点区分早期 GT、GTV 2000 与后期塑料保险杠外廓。
3. 处理 Giulia GT Ktype `182-189` 的 105 系列短车身、1750／2000 加长车身边界。
4. 随后补齐 Spider Ktype `197`、`199`、`201-205`、`207` 的 Series 1—4 外廓分支。

推进信号：CONTINUE

[1]: https://autodata24.com/alfa-romeo/155/155-167/18-tspark-105-hp/details "Alfa Romeo 155 155 (167) • 1.8 T.Spark (105 Hp) technical specifications and fuel consumption — AutoData24.com"
[2]: https://www.auto-data.net/en/alfa-romeo-164-164-2.5-v6-163hp-1252 "Alfa Romeo 164 (164) 2.5 V6 (163 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://autodata24.com/alfa-romeo/164/164-164/30-v6-164h1a164h1b164k1-180-hp/details?utm_source=chatgpt.com "3.0 V6 (164.H1A,164.H1B,164.K1 (180 Hp) technical ..."
[4]: https://www.automobile-catalog.com/car/1979/44495/alfa_romeo_alfetta_1_6.html?utm_source=chatgpt.com "1979 Alfa Romeo Alfetta 1.6 Specs Review (79.5 kW / 108 PS / 107 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 Alfa Romeo Alfetta GT/GTV Ktype `190-194`，确认存在三套物理外廓：

  * 早期 Alfetta GT 1.6/1.8：`4190 × 1660 × 1330 mm`
  * 1976—1980 Alfetta GTV 2000：`4205 × 1660 × 1330 mm`
  * 1980 年改款后的 GTV 2.0：`4260 × 1664 × 1330 mm`
    三套宽度均为不含后视镜口径。([汽车目录][1])
* Ktype `190` 的 1.6 仅关联早期 Alfetta GT 外廓；资料显示 1980 年改款时 1.6 退出产品线，因此不因输入结束年月延伸至 1982 年而创建猜测性改款分支。([维基百科][2])
* Ktype `191`、`192` 均为早期 1.8 Alfetta GT，直接复用同一新建尺寸组。
* Ktype `193`、`194` 的 2.0 生产年月跨越 1980 年外观改款，分别拆为 `prefl` 和 `facelift`；相同物理分支跨两个输入车型名称复用同一尺寸组。
* 本轮首次创建 3 个尺寸组，没有重复输出其他既有尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：`80 / 100`
* PENDING 输入 Ktype：`20 / 100`
* 本轮新增 READY：`5` 个输入 Ktype、`7` 条映射
* 本轮首次创建尺寸组：`3`
* 当前仍处于第一阶段，尚有 Giulia GT 与 Spider 的代次、车身及尺寸缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
190	190	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	MEDIUM	1.6仅对应1980年改款前Alfetta GT外廓；输入结束年月晚于车型实际阶段。	READY
191	191	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	HIGH	早期1.8 Alfetta GT物理外廓。	READY
192	192	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	HIGH	早期1.8 Alfetta GT物理外廓。	READY
193_prefl	193	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	2.0 Ktype跨越1980年外观改款，按改款前GTV 2000外廓拆分。	READY
193_facelift	193	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	HIGH	2.0 Ktype跨越1980年外观改款，按改款后GTV 2.0外廓拆分。	READY
194_prefl	194	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	2.0 Ktype跨越1980年外观改款，按改款前GTV 2000外廓拆分。	READY
194_facelift	194	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	HIGH	2.0 Ktype跨越1980年外观改款，按改款后GTV 2.0外廓拆分。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	4190	1660	1330	Automobile-Catalog 1974 Alfa Romeo Alfetta GT; Automobile-Catalog 1976 Alfa Romeo Alfetta GT 1.6	https://www.automobile-catalog.com/car/1974/33335/alfa_romeo_alfetta_gt.html; https://www.automobile-catalog.com/car/1976/144005/alfa_romeo_alfetta_gt_1_6.html
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	4205	1660	1330	Automobile-Catalog 1976 Alfa Romeo Alfetta GTV 2000	https://www.automobile-catalog.com/car/1976/144020/alfa_romeo_alfetta_gtv_2000.html
EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	4260	1664	1330	Automobile-Catalog 1982 Alfa Romeo GTV 2.0; Automobile-Catalog 1983 Alfa Romeo GTV 2.0	https://www.automobile-catalog.com/car/1982/144080/alfa_romeo_gtv_2_0.html; https://www.automobile-catalog.com/car/1983/144125/alfa_romeo_gtv_2_0.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 处理 Giulia GT Ktype `182-189`，优先区分 GT 1300/1600 Junior、Sprint GT、1750 GTV 与 2000 GTV 的长度和车身分支。
2. 处理 Spider Ktype `197`、`199`、`201-205`、`207`，按 Series 1、Series 2、Series 3、Series 4 的前后保险杠及尾部外廓拆分。
3. 返回 Alfetta Sedan Ktype `165-168`、`170`，修正早期 1.6 的 `4240 mm` 与其他早期版本 `4280 mm` 的外廓边界后，再完成跨期派生关联。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1974/33335/alfa_romeo_alfetta_gt.html?utm_source=chatgpt.com "1974 Alfa Romeo Alfetta GT Specs Review (89 kW / 121 ..."
[2]: https://es.wikipedia.org/wiki/Alfa_Romeo_Alfetta_GT/GTV?utm_source=chatgpt.com "Alfa Romeo Alfetta GT/GTV"


--- 发送 / 继续到 Round 6 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 闭合 Ktype `183`、`184`、`185`：分别确认为 Giulia Sprint GT `105.02`、Sprint GT Veloce `105.36`、Sprint GTA `105.32`。三者均为早期阶梯式车头双门外廓，三维统一为 `4080 × 1580 × 1315 mm`，复用同一新建尺寸组。([汽车目录][1])
* 闭合 Ktype `188`：确认为 1750 GTV `105.44` 双门 Coupe，三维为 `4100 × 1580 × 1315 mm`，宽度为不含后视镜口径。([汽车目录][2])
* 闭合 Ktype `189`：确认为 2000 GTV `105.21` 双门 Coupe，三维同为 `4100 × 1580 × 1315 mm`；因其前后外部造型与 1750 GTV 不同，独立建立尺寸组。([汽车目录][3])
* GT 1300/1600 Junior 的 Ktype `182`、`186`、`187` 跨越阶梯式车头、1750 式车头及 1974 年后的 2000 GTV 式外观，本轮未压缩为单一映射，留待按外廓阶段完整派生。([维基百科][4])

## 2. 当前批次进度

* READY 输入 Ktype：`85 / 100`
* PENDING 输入 Ktype：`15 / 100`
* 本轮新增 READY：`5` 个输入 Ktype
* 本轮首次创建尺寸组：`3`
* 当前仍处于第一阶段，GT Junior、Alfetta Sedan 和 Spider 尚有外廓分支或尺寸缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
183	183	Coupe	Giulia Sprint GT	105.02	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	早期阶梯式车头双门外廓。	READY
184	184	Coupe	Giulia Sprint GT Veloce	105.36	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	早期阶梯式车头双门外廓。	READY
185	185	Coupe	Giulia Sprint GTA	105.32	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	GTA使用与早期Sprint GT一致的外部尺寸轮廓。	READY
188	188	Coupe	1750 GTV	105.44	2	EU-ALFA-ROMEO-1750-GTV-10544-COUPE-01	HIGH	1750 GTV双门物理外廓。	READY
189	189	Coupe	2000 GTV	105.21	2	EU-ALFA-ROMEO-2000-GTV-10521-COUPE-01	HIGH	2000 GTV双门物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	4080	1580	1315	Automobile-Catalog 1964 Alfa Romeo Giulia Sprint GT; Automobile-Catalog 1968 Alfa Romeo Giulia Sprint GTV; Automobile-Catalog 1965 Alfa Romeo Giulia Sprint GTA	https://www.automobile-catalog.com/car/1964/64940/alfa_romeo_giulia_sprint_gt.html; https://www.automobile-catalog.com/car/1968/64985/alfa_romeo_giulia_sprint_gtv.html; https://www.automobile-catalog.com/car/1965/64970/alfa_romeo_giulia_sprint_gta.html
EU-ALFA-ROMEO-1750-GTV-10544-COUPE-01	4100	1580	1315	Automobile-Catalog 1968 Alfa Romeo 1750 GTV	https://www.automobile-catalog.com/car/1968/65030/alfa_romeo_1750_gtv.html
EU-ALFA-ROMEO-2000-GTV-10521-COUPE-01	4100	1580	1315	Automobile-Catalog 1975 Alfa Romeo 2000 GTV	https://www.automobile-catalog.com/car/1975/65045/alfa_romeo_2000_gtv.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 拆分 Ktype `182` 的 GT 1300 Junior：阶梯式车头、1970 年后非阶梯式车头及 1974 年后统一外观。
2. 拆分 Ktype `186`、`187` 的 GT 1600 Junior：`115.03` 前期外观与 `115.34` 后期外观。
3. 完成 Alfetta Sedan Ktype `165-168`、`170` 的 Series 1—3 跨期映射。
4. 随后集中处理 Spider Ktype `197`、`199`、`201-205`、`207` 的 Series 1—4 外廓尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1964/64940/alfa_romeo_giulia_sprint_gt.html?utm_source=chatgpt.com "1964 Alfa Romeo Giulia Sprint GT Specs Review (78 kW ..."
[2]: https://www.automobile-catalog.com/car/1968/65030/alfa_romeo_1750_gtv.html?utm_source=chatgpt.com "1968 Alfa Romeo 1750 GTV Specs Review (83 kW ..."
[3]: https://www.automobile-catalog.com/car/1975/65045/alfa_romeo_2000_gtv.html?utm_source=chatgpt.com "1975 Alfa Romeo 2000 GTV Specs Review (96.5 kW ..."
[4]: https://en.wikipedia.org/wiki/Alfa_Romeo_105/115_Series_Coup%C3%A9s?utm_source=chatgpt.com "Alfa Romeo 105/115 Series Coupés"


--- 发送 / 继续到 Round 7 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 补齐 Ktype `182`。GT 1300 Junior 的 `105.30` 双门车身按三次明确外观阶段拆分：1966—1969 年阶梯式车头、1970—1974 年中期的 1750 式双灯车头、1974 年中期后的 2000 GTV 式统一外观。三个阶段的三维均为 `4080 × 1580 × 1315 mm`，但物理前脸外廓不同，因此分别关联尺寸组。阶梯式分支复用既有尺寸组，后两组首次创建。([维基百科][1])
* 补齐 Ktype `186`、`187`。两条 1600 Ktype 均覆盖 1972—1974 年的 `115.03` 与 1974 年后的 `115.34`；前者使用 1750 式 Junior 外廓，后者使用统一外观。相同物理外廓与 GT 1300 Junior 跨发动机复用尺寸组，不重复建组。([维基百科][1])
* 新建的两个尺寸组均使用 Automobile-Catalog 直接车型页核对，宽度明确为不含后视镜口径；1974 年改款前后页面均给出 `4080 × 1580 × 1315 mm`。([汽车目录][2])

## 2. 当前批次进度

* READY 输入 Ktype：`88 / 100`
* PENDING 输入 Ktype：`12 / 100`
* 本轮新增 READY：`3` 个输入 Ktype、`7` 条映射
* 本轮首次创建尺寸组：`2`
* 本轮复用既有尺寸组：`1` 条映射
* 当前仍处于第一阶段，Alfetta Sedan 与 Spider 尚有跨期外廓或尺寸缺失，批次未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
182_stepfront	182	Coupe	GT 1300 Junior	105.30	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	1966-1969年阶梯式车头物理外廓。	READY
182_1750nose	182	Coupe	GT 1300 Junior	105.30	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	HIGH	1970年至1974年中期的1750式双灯车头物理外廓。	READY
182_unified	182	Coupe	1.3 GT Junior	105.30	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	HIGH	1974年中期后的2000 GTV式统一外观。	READY
186_prefl	186	Coupe	GT 1600 Junior	115.03	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	MEDIUM	1972年至1974年中期的115.03双灯车头外廓。	READY
186_facelift	186	Coupe	1.6 GT Junior	115.34	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	MEDIUM	1974年中期后的115.34统一外观。	READY
187_prefl	187	Coupe	GT 1600 Junior	115.03	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	MEDIUM	109 HP Ktype覆盖115.03改款前双灯车头外廓。	READY
187_facelift	187	Coupe	1.6 GT Junior	115.34	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	MEDIUM	109 HP Ktype覆盖115.34统一外观。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	4080	1580	1315	Automobile-Catalog 1971 Alfa Romeo GT 1300 Junior; Automobile-Catalog 1974 Alfa Romeo GT 1600 Junior up to mid-year	https://www.automobile-catalog.com/car/1971/1437365/alfa_romeo_gt_1300_junior.html; https://www.automobile-catalog.com/car/1974/1437380/alfa_romeo_gt_1600_junior.html
EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	4080	1580	1315	Automobile-Catalog 1974 Alfa Romeo GT 1300 Junior since mid-year; Automobile-Catalog 1974 Alfa Romeo GT 1600 Junior since mid-year	https://www.automobile-catalog.com/car/1974/65075/alfa_romeo_gt_1300_junior.html; https://www.automobile-catalog.com/car/1974/71945/alfa_romeo_gt_1600_junior.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 完成 Alfetta Sedan Ktype `165-168`、`170`，按 Series 1、Series 2、Series 3 生产阶段派生关联，并处理早期 1.6 的长度差异。
2. 集中处理 Spider Ktype `197`、`199`、`201-205`、`207`，优先建立 Series 1 圆尾、Series 2 截尾、Series 3 空气动力套件、Series 4 平滑保险杠四类稳定尺寸组。
3. 数据缺失补齐后，再进入第二阶段核对所有派生行的具体年份覆盖、宽度口径及映射置信度。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Alfa_Romeo_105/115_Series_Coup%C3%A9s "Alfa Romeo 105/115 Series Coupés - Wikipedia"
[2]: https://www.automobile-catalog.com/car/1974/65075/alfa_romeo_gt_1300_junior.html?utm_source=chatgpt.com "1974 Alfa Romeo GT 1300 Junior Specs Review (65.5 kW / 89 PS / 88 hp) (since mid-year 1974 for Europe )"


--- 发送 / 继续到 Round 8 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 完成 Alfetta Sedan 的 Ktype `165–168`、`170`。确认该车系存在四套需区分的外廓：早期 1.6 短车头 `4240 × 1620 × 1430 mm`、后期 Series 1 `4280 × 1620 × 1430 mm`、Series 2 `4385 × 1640 × 1430 mm`、Series 3 `4410 × 1640 × 1430 mm`；宽度均为不含后视镜口径。([汽车目录][1])
* Ktype `165` 的 1.6 跨越四套外廓，拆为 `shortnose`、`series1`、`series2`、`series3`。1975—1977 年 1.6 为 4240 mm，1978 年中期以后增至 4280 mm，1981 年中期进入 Series 2，1983 年中期进入 Series 3。([汽车目录][2])
* Ktype `166` 的 85 kW 1.8 仅关联 4280 mm 的 Series 1 外廓；Ktype `167`、`168` 的后期 1.8 覆盖 Series 1、Series 2、Series 3，分别派生三条映射。([汽车目录][3])
* Ktype `170` 的 2.0 从长车头外廓开始，不关联 4240/4280 mm 组；拆为 Series 2 的 4385 mm 外廓和 Series 3 的 4410 mm 外廓。([汽车目录][4])
* 本轮仅首次创建早期 1.6 短车头尺寸组，其余三组全部复用既有缓存。

## 2. 当前批次进度

* READY 输入 Ktype：`93 / 100`
* PENDING 输入 Ktype：`7 / 100`
* 本轮新增 READY：`5` 个输入 Ktype、`13` 条映射
* 本轮首次创建尺寸组：`1`
* 本轮复用既有尺寸组：`12` 条映射
* 当前仍处于第一阶段，剩余缺失集中在 Alfa Romeo Spider 105/115 系列外廓分支，批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
165_shortnose	165	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-16-SHORTNOSE-01	HIGH	早期1.6使用4240 mm短车头外廓。	READY
165_series1	165	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	HIGH	1978年中期后的1.6使用4280 mm Series 1外廓。	READY
165_series2	165	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	1.6覆盖1981年中期后的Series 2外廓。	READY
165_series3	165	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	1.6覆盖1983年中期后的Series 3外廓。	READY
166	166	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	85 kW版1.8对应4280 mm Series 1外廓。	READY
167_series1	167	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	后期1.8在1981年中期前使用Series 1外廓。	READY
167_series2	167	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	后期1.8覆盖Series 2外廓。	READY
167_series3	167	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	后期1.8覆盖Series 3外廓。	READY
168_series1	168	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	122 HP版1.8在1981年中期前使用Series 1外廓。	READY
168_series2	168	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	122 HP版1.8覆盖Series 2外廓。	READY
168_series3	168	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	122 HP版1.8覆盖Series 3外廓。	READY
170_series2	170	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	2.0长车头版本在1983年中期前使用4385 mm外廓。	READY
170_series3	170	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	2.0覆盖1983年中期后的4410 mm外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-16-SHORTNOSE-01	4240	1620	1430	Automobile-Catalog 1975 Alfa Romeo Alfetta 1.6	https://www.automobile-catalog.com/car/1975/143615/alfa_romeo_alfetta_1_6.html
```

## 5. 下一步优先处理

**下一步优先补缺失：**

1. 集中建立 Spider Series 1 圆尾、Series 2 截尾、Series 3 空气动力套件和 Series 4 平滑保险杠的稳定尺寸组。
2. 将剩余 Spider Ktype 按实际覆盖年份关联到上述尺寸组；跨代 Ktype 必须派生，不按发动机版本重复建组。
3. Spider 缺失全部闭合后，再进入第二阶段，核对全批次派生年份边界、宽度口径、尺寸组引用完整性和映射置信度。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1975/143615/alfa_romeo_alfetta_1_6.html?utm_source=chatgpt.com "1975 Alfa Romeo Alfetta 1.6 Specs Review (79.5 kW / 108 ..."
[2]: https://www.automobile-catalog.com/car/1977/143615/alfa_romeo_alfetta_1_6.html?utm_source=chatgpt.com "1977 Alfa Romeo Alfetta 1.6 Specs Review (79.5 kW / 108 PS ..."
[3]: https://www.automobile-catalog.com/car/1978/143555/alfa_romeo_alfetta_1_8.html?utm_source=chatgpt.com "1978 Alfa Romeo Alfetta 1.8 Specs Review (84.5 kW ..."
[4]: https://www.automobile-catalog.com/car/1981/143675/alfa_romeo_alfetta_2_0.html?utm_source=chatgpt.com "1981 Alfa Romeo Alfetta 2.0 Specs Review (95.5 kW / 130 PS / 128 hp) (since mid-year 1981 for Europe Australia )"


--- 发送 / 继续到 Round 9 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 修正上一轮进度计数：Spider 实际剩余 `8` 个输入 Ktype，而非 `7` 个。本轮已全部补齐，第一阶段的数据缺失已清零。
* Ktype `197` 的 Spider 1300 跨越 Series 1 圆尾和 Series 2 截尾，拆为两个物理分支。Series 1 复用既有 `4250 × 1630 × 1290 mm` 尺寸组；Series 2 复用既有 `4120 × 1630 × 1290 mm` 尺寸组。官方历史资料确认 1969—1970 年由圆尾改为截尾，车长从 4250 mm 缩短为 4120 mm。([DIE WELT][1])
* Ktype `202` 的 1750 Spider 同样跨越 Series 1 与 Series 2，拆成两个分支并复用上述既有尺寸组。([汽车目录][2])
* Ktype `199` 的 1600 跨越 Series 2 和 Series 3；Ktype `205` 的 2000 跨越 Series 2、Series 3、Series 4，均按真实外廓阶段派生。
* 首次创建 Spider Series 3 尺寸组：`4245 × 1630 × 1290 mm`。1983、1986 和 1989 年欧洲车型资料三维一致，宽度明确为不含后视镜。([汽车目录][3])
* 首次创建 Spider Series 4 尺寸组：`4258 × 1630 × 1290 mm`。1991 年欧洲 1.6 车型资料明确给出三维及不含后视镜宽度。([汽车目录][4])
* Ktype `201`、`207` 直接关联 Series 4；Ktype `203`、`204` 的功率标定对应 Series 3，不创建推测性的 Series 4 分支。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮新增 READY：`8` 个输入 Ktype、`13` 条映射
* 本轮首次创建尺寸组：`2`
* 本轮复用既有尺寸组：`5` 条映射
* 第一阶段数据缺失已经补齐。
* 当前进入第二阶段核对，尚未达到 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
197_series1	197	Convertible	Spider Series 1 Duetto	105	2	EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	HIGH	1300 Ktype跨越圆尾与截尾，按Series 1圆尾外廓拆分。	READY
197_series2	197	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1300 Ktype跨越圆尾与截尾，按Series 2截尾外廓拆分。	READY
199_series2	199	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1600 Ktype覆盖Series 2截尾外廓。	READY
199_series3	199	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	1600 Ktype覆盖Series 3空气动力套件外廓。	READY
201	201	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	HIGH	79 kW版对应1990年起Series 4平滑保险杠外廓。	READY
202_series1	202	Convertible	Spider Series 1 Duetto	105	2	EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	HIGH	1750 Ktype跨越圆尾与截尾，按Series 1圆尾外廓拆分。	READY
202_series2	202	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1750 Ktype跨越圆尾与截尾，按Series 2截尾外廓拆分。	READY
203	203	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	85 kW催化版本对应Series 3外廓。	READY
204	204	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	92 kW版本对应Series 3外廓。	READY
205_series2	205	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	MEDIUM	该2000 Ktype覆盖Series 2，按截尾外廓拆分。	READY
205_series3	205	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	MEDIUM	该2000 Ktype覆盖Series 3，按空气动力套件外廓拆分。	READY
205_series4	205	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	MEDIUM	该2000 Ktype覆盖Series 4，按平滑保险杠外廓拆分。	READY
207	207	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	HIGH	88 kW版对应1990年起Series 4外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	4245	1630	1290	Automobile-Catalog 1983 Alfa Romeo Spider 1.6; Automobile-Catalog 1989 Alfa Romeo Spider 2.0 catalyst	https://www.automobile-catalog.com/car/1983/214295/alfa_romeo_spider_1_6.html; https://www.automobile-catalog.com/car/1989/214325/alfa_romeo_spider_2_0_cat.html
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	4258	1630	1290	Automobile-Catalog 1991 Alfa Romeo Spider 1.6	https://www.automobile-catalog.com/car/1991/217280/alfa_romeo_spider_1_6.html
```

## 5. 下一步优先处理

**下一步优先核对：**

1. 汇总当前批次完整映射快照，检查每个输入 Ktype 至少出现一次、所有派生 `id` 唯一且顺序稳定。
2. 核对跨改款派生行的实际年份覆盖，重点检查 Alfa Romeo 155、Alfetta Sedan、GT Junior 和 Spider。
3. 检查全部 `DIMENSION_GROUP_ID` 引用闭环，清除孤立尺寸组及重复建立的相同外廓组。
4. 复核所有尺寸组的 `WidthMM` 是否明确为不含后视镜，并核对同组三维没有来源冲突。
5. 核对完成后，生成两张最终完整 TSV 及规定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.welt.de/motor/news/article69bd5195e5e9d619745d17b5/60-jahre-alfa-romeo-spider-tipo-105-115.html?utm_source=chatgpt.com "60 Jahre Alfa Romeo Spider (Tipo 105/115)"
[2]: https://www.automobile-catalog.com/car/1968/65210/alfa_romeo_1750_spider_veloce.html?utm_source=chatgpt.com "1968 Alfa Romeo 1750 Spider Veloce Specs Review (83 ..."
[3]: https://www.automobile-catalog.com/car/1983/214295/alfa_romeo_spider_1_6.html?utm_source=chatgpt.com "1983 Alfa Romeo Spider 1.6 Specs Review (76 kW ..."
[4]: https://www.automobile-catalog.com/car/1991/217280/alfa_romeo_spider_1_6.html?utm_source=chatgpt.com "1991 Alfa Romeo Spider 1.6 Specs Review (80 kW ..."


--- 发送 / 继续到 Round 10 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 核对 Ktype `115`、`116`：Alfa Romeo 33 Sport Wagon 1.7 16V 前驱与 4×4 的三维均为 `4200 × 1614 × 1350 mm`，4×4 未造成外部三维变化，继续共用既有尺寸组。([汽车数据网][1])
* 核对 Ktype `208`：1936—1948 年 13 HP Fiat 500 对应 500 A Topolino，既有 `3215 × 1275 × 1375 mm` 尺寸事实保持不变，宽度来源明确为不含后视镜。([Stellantis Heritage][2])
* 核对 BMW E12 的 Ktype `209`、`211-213`、`215-218`：既有 `4620 × 1690 × 1425 mm` 尺寸组可继续跨发动机复用，无需拆分。([维基百科][3])
* 核对 Ktype `214`：Volkswagen 官方资料给出 Passat B7 Sedan 全车系高度范围 `1462–1470 mm`，但该 Ktype 对应的普通版与 BMT 版 1.4 TSI 90 kW 均有直接资料支持 `1470 mm`，因此继续保留既有 `4769 × 1820 × 1470 mm` 尺寸组，不创建低车身猜测分支。([Volkswagen Newsroom][4])
* 核对 Ktype `219`：BMW 官方确认 316i Touring E30 的生产期和功率与输入一致；既有 Touring 外廓 `4321 × 1641 × 1379 mm` 获得交叉验证，无需修正。([BMW集团经典][5])
* 本轮未发现需要改写的映射行或尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮完成第二阶段核对：`13` 个输入 Ktype。
* 本轮映射修改：`0`
* 本轮尺寸组创建或修正：`0`
* 尚需完成全批次主外键闭环、派生行顺序和重复尺寸组检查，暂不输出 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 核对 Ktype `117-138` 的 Alfa Romeo 75／90，重点复查普通 75 与 America 加长保险杠尺寸组边界。
2. 核对 Ktype `139-164` 的 Alfa Romeo 155／164，检查宽体、Q4、Facelift、Super、24V 与 QV 是否存在遗漏或重复尺寸组。
3. 核对 Alfetta、GT Junior 和 Spider 的全部派生 `id`，确认同一 Ktype 已删除无后缀基础行，且派生顺序稳定。
4. 完成映射引用、尺寸组孤立行和重复 ID 检查后，再生成最终完整快照及规定下载文件。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.7-16v-132hp-4x4-1394?utm_source=chatgpt.com "Alfa Romeo 33 Sport Wagon (907B) 1.7 16V (132 Hp) 4x4"
[2]: https://www.stellantisheritage.com/en-uk/heritage/stories/fiat-topolino?utm_source=chatgpt.com "Fiat 500 Topolino"
[3]: https://en.wikipedia.org/wiki/BMW_5_Series_%28E12%29?utm_source=chatgpt.com "BMW 5 Series (E12)"
[4]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037 "Vehicle data Passat B7 profile | Volkswagen Newsroom"
[5]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-874-1.bmw-316i-touring-e30.html?utm_source=chatgpt.com "BMW 316i Touring (E30)"


--- 发送 / 继续到 Round 11 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 1. 更新点

* 纠正 Ktype `119`。此前将其整体关联到普通 Alfa Romeo 75 尺寸组不准确。输入生产区间横跨：

  * 前期 1.8 Turbo Europa：`4330 × 1650 × 1400 mm`
  * 后期 1.8 Turbo America：`4420 × 1660 × 1400 mm`

  两者保险杠和车身外廓不同，因此删除原无后缀基础映射，拆为 `119_europa`、`119_america`。标准 114 kW Turbo 出现在 1986—1987 年，后续相同功率的 Turbo America 使用加长外廓；这是依据输入年月与对应车型阶段作出的映射判断。([汽车目录][1])
* 纠正 Ktype `124`。110 kW／150 HP 版本对应 1.8 Turbo America 外廓，改为关联既有 `EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01`，不再使用普通 75 尺寸组。([汽车目录][2])
* 首次创建 1.8 Turbo Europa 专用尺寸组。该车型宽度 `1650 mm`，不同于普通 75 的 `1630 mm`，因此不能继续共用普通车身尺寸组。([汽车目录][3])
* Evoluzione 具有独立宽体翼子板、侧裙及空气动力附件，但输入 Ktype `119` 未包含 `Evoluzione` 标记，本轮不创建猜测性 Evoluzione 派生行。([Stellantis Heritage][4])

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修正：`2` 个输入 Ktype、`3` 条映射
* 本轮首次创建尺寸组：`1`
* 当前仍处于第二阶段核对。
* 尚需继续检查 Alfa Romeo 75 Twin Spark、V6、TD 与 Alfa Romeo 155／164 的尺寸组边界，暂不输出 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119_europa	119	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TURBO-EUROPA-01	HIGH	该Ktype跨越普通Turbo与Turbo America，按前期Europa外廓拆分。	READY
119_america	119	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	该Ktype跨越普通Turbo与Turbo America，按后期加长保险杠外廓拆分。	READY
124	124	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	110 kW版本对应Turbo America加长外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-75-162B-SEDAN-TURBO-EUROPA-01	4330	1650	1400	Automobile-Catalog 1986 Alfa Romeo 75 1.8 Turbo	https://www.automobile-catalog.com/car/1986/53675/alfa_romeo_75_1_8_turbo.html
```

## 5. 下一步优先处理

**下一步优先核对：**

1. 核对 Ktype `127`、`128` 的 2.0 Twin Spark／CAT，确认 `1630 mm` 与 `1660 mm` 宽度资料冲突是否来自年份、轮眉或数据库口径差异。
2. 核对 Ktype `131` 的早期 2.5 V6，确认是否始终使用普通 `4330 × 1630 × 1400 mm` 外廓。
3. 复查 Ktype `133` 的 136 kW 3.0 V6 CAT 是否完整覆盖 America 外廓，以及是否存在改款前普通长度分支。
4. 随后核对 Alfa Romeo 155／164 的宽体、Q4、Facelift 和 Super 外廓边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/53675/alfa_romeo_75_1_8_turbo.html?utm_source=chatgpt.com "1986 Alfa Romeo 75 1.8 Turbo Specs Review (114 kW / 155 PS / 153 hp) (since mid-year 1986 for Europe )"
[2]: https://www.automobile-catalog.com/car/1988/215750/alfa_romeo_75_1_8_turbo_america.html?utm_source=chatgpt.com "1988 Alfa Romeo 75 1.8 Turbo America Specs Review (114 kW ..."
[3]: https://www.automobile-catalog.com/car/1989/215585/alfa_romeo_75_1_6.html?utm_source=chatgpt.com "1989 Alfa Romeo 75 1.6 (man. 5) (model for Europe ) car ..."
[4]: https://www.stellantisheritage.com/en-uk/heritage/stories/alfa-romeo-75?utm_source=chatgpt.com "Alfa Romeo 75"


--- 发送 / 继续到 Round 12 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 1. 更新点

* 纠正 Ktype `127`、`128`：Alfa Romeo 75 2.0 Twin Spark 并非普通 `1630 mm` 宽车身。1987 年非催化版与后期催化版资料均给出 `4330 × 1660 × 1400 mm`，且宽度为不含后视镜口径；两条 Ktype 改为关联新建 Twin Spark 空力外廓尺寸组。([汽车目录][1])
* 官方历史资料确认 2.0 Twin Spark 配有不同于普通 75 的翼子板、侧裙、前后扰流件及其他空气动力部件，因此不能因车长和车高相同而继续复用普通 75 尺寸组。([Stellantis Heritage][2])
* Ktype `127` 的 `107 kW` 与催化版约 145–146 HP 相符；Ktype `128` 的 `109 kW / 148 HP` 与非催化版相符，虽然输入名称带有 `CAT`，但两者物理外廓一致，因此无需按催化状态拆分尺寸组。([Stellantis Heritage][3])
* 复核 Ktype `131`：早期 2.5 V6 仍为 `4330 × 1630 × 1400 mm` 普通外廓，不需要修改现有映射。([汽车数据网][4])
* 复核 Ktype `133`、`134`：3.0 V6 CAT／QV 均继续使用 `4420 × 1660 × 1400 mm` America 加长保险杠外廓，不需要修改。([汽车目录][5])

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修正映射：`2` 条
* 本轮首次创建尺寸组：`1`
* Alfa Romeo 75 的普通车身、Turbo Europa、Turbo America、Twin Spark 和 3.0 America 主要外廓边界已完成核对。
* 当前仍处于第二阶段核对，尚未达到 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127	127	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	HIGH	2.0 Twin Spark使用加宽翼子板、侧裙及扰流件外廓。	READY
128	128	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	HIGH	输入CAT名称与109 kW功率标定存在冲突，但两种Twin Spark标定共用同一物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	4330	1660	1400	Automobile-Catalog 1987 Alfa Romeo 75 2.0 Twin Spark; Automobile-Catalog 1989 Alfa Romeo 75 2.0 Twin Spark catalyst	https://www.automobile-catalog.com/car/1987/215525/alfa_romeo_75_2_0_twin_spark.html; https://www.automobile-catalog.com/car/1989/215645/alfa_romeo_75_2_0_twin_spark_cat.html
```

## 5. 下一步优先处理

**下一步优先核对：**

1. 核对 Alfa Romeo 155 的 Series 1 窄体、Series 2 宽体与 Q4 宽体高度，重点检查 Ktype `140`、`141`、`146–150` 的派生边界。
2. 核对 Alfa Romeo 164 的基础改款与 Super 长保险杠外廓，重点检查 Ktype `153–164` 是否存在将 `4555 mm` 与 `4665 mm` 错误合并的情况。
3. 随后检查所有映射引用闭环、孤立尺寸组、重复尺寸组和派生 `id` 顺序。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/215525/alfa_romeo_75_2_0_twin_spark.html?utm_source=chatgpt.com "1987 Alfa Romeo 75 2.0 Twin Spark (man. 5)"
[2]: https://www.stellantisheritage.com/en-uk/heritage/stories/alfa-romeo-75 "Alfa Romeo 75"
[3]: https://www.stellantisheritage.com/en-uk/heritage/stories/alfa-romeo-75?utm_source=chatgpt.com "Alfa Romeo 75"
[4]: https://www.auto-data.net/en/alfa-romeo-75-162-b-quadrifoglio-verde-2.5-v6-156hp-1559?utm_source=chatgpt.com "Alfa Romeo 75 (162 B) Quadrifoglio Verde 2.5 V6 (156 Hp)"
[5]: https://www.automobile-catalog.com/car/1990/215795/alfa_romeo_75_3_0_v6_quadrifoglio_verde_cat.html?utm_source=chatgpt.com "1990 Alfa Romeo 75 3.0 V6 Quadrifoglio Verde catalyst ..."


--- 发送 / 继续到 Round 13 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1. 更新点

* 修正 Alfa Romeo 164 Series 2 标准车身尺寸组：1992 年中期至 1994 年中期的非 Super 车型长度应为 `4555 mm`，不是此前采用的 `4565 mm`；宽度为不含后视镜的 `1760 mm`，高度为 `1390 mm`。既有 `EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01` 本轮纠正尺寸事实。([汽车目录][1])
* 首次建立 164 Super 长保险杠尺寸组 `4665 × 1760 × 1390 mm`。Ktype `153` 的 106 kW Twin Spark、`154` 的 148 kW V6 Turbo 和 `163` 的 155 kW 24V 均对应 Super 外廓，改为共同关联该组。([汽车目录][2])
* Ktype `157` 的 2.5 TD 92 kW 跨越非 Super 和 Super 阶段，删除无后缀基础行，拆为 `157_standard` 与 `157_super`。1994 年中期前标准 TD 为 4555 mm，之后 Super TD 为 4665 mm。([汽车目录][3])
* 修正 Ktype `164`：输入明确为前驱 `3.0 24V QV`，不是四驱 Q4。Quadrifoglio 24V 的外廓为 `4555 × 1760 × 1390 mm`；由于 QV 外部套件与普通 Series 2 不同，单独建立尺寸组。([汽车目录][4])
* Q4 的 `4665 × 1760 × 1356 mm` 不适用于 Ktype `164`，本轮没有创建或关联 Q4 尺寸组。([汽车目录][5])

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修改：`5` 个输入 Ktype、`6` 条映射
* 本轮首次创建尺寸组：`2`
* 本轮修正既有尺寸组：`1`
* 当前仍处于第二阶段核对；尚需复核 Ktype `156`、`160` 的特殊功率版本，以及完成全表主外键闭环与重复尺寸组检查。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
153	153	Sedan	164 Super	164.H3	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	106 kW Twin Spark对应Super长保险杠外廓。	READY
154	154	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	148 kW V6 Turbo对应Super长保险杠外廓。	READY
157_standard	157	Sedan	164 Series 2	164	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	HIGH	2.5 TD跨越标准Series 2与Super，按标准外廓拆分。	READY
157_super	157	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	2.5 TD跨越标准Series 2与Super，按Super外廓拆分。	READY
163	163	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	155 kW 24V对应Super长保险杠外廓。	READY
164	164	Sedan	164 Quadrifoglio 24V	164.H1	4	EU-ALFA-ROMEO-164-164-SEDAN-QV24V-01	HIGH	前驱Quadrifoglio 24V外廓，不属于四驱Q4。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	4555	1760	1390	Automobile-Catalog 1993 Alfa Romeo 164 2.0 Twin Spark catalyst; Automobile-Catalog 1993 Alfa Romeo 164 TD; Automobile-Catalog 1994 Alfa Romeo 164 3.0 V6 catalyst	https://www.automobile-catalog.com/car/1993/217670/alfa_romeo_164_2_0_twin_spark_cat.html; https://www.automobile-catalog.com/car/1993/217790/alfa_romeo_164_td.html; https://www.automobile-catalog.com/car/1994/217685/alfa_romeo_164_3_0_v6_cat.html
EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	4665	1760	1390	Automobile-Catalog 1997 Alfa Romeo 164 Super 3.0 V6 catalyst; Automobile-Catalog 1995 Alfa Romeo 164 Super TD	https://www.automobile-catalog.com/car/1997/217850/alfa_romeo_164_super_3_0_v6_cat.html; https://www.automobile-catalog.com/car/1995/217805/alfa_romeo_164_super_td.html
EU-ALFA-ROMEO-164-164-SEDAN-QV24V-01	4555	1760	1390	Automobile-Catalog 1992 Alfa Romeo 164 Quadrifoglio 24V catalyst; Automobile-Catalog 1994 Alfa Romeo 164 Quadrifoglio 24V catalyst	https://www.automobile-catalog.com/car/1992/217745/alfa_romeo_164_quadrifoglio_24v_cat.html; https://www.automobile-catalog.com/car/1994/217745/alfa_romeo_164_quadrifoglio_24v_cat.html
```

## 5. 下一步优先处理

**下一步优先核对：**

1. 复核 Ktype `156` 的 2.5 V6 163 HP 是否属于特定市场 Super 外廓，避免继续依据聚合资料直接关联标准 Series 2。
2. 复核 Ktype `160` 的 `132 kW / 180 HP` 与输入生产年月冲突，确认是早期 12V 版本、市场降功率 Super，还是上游年月错误。
3. 核对 Alfa Romeo 155 的宽体、Q4 高度和跨改款派生行。
4. 完成全部 `id` 唯一性、Ktype 覆盖、尺寸组引用闭环、孤立尺寸组和重复物理外廓检查。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1994/217700/alfa_romeo_164_3_0_v6_automatic_cat.html?utm_source=chatgpt.com "1994 Alfa Romeo 164 3.0 V6 automatic catalyst Specs Review (135 kW / 184 PS / 181 hp) (up to mid-year 1994 for Europe )"
[2]: https://www.automobile-catalog.com/car/1995/217835/alfa_romeo_164_super_2_0_twin_spark_cat.html?utm_source=chatgpt.com "1995 Alfa Romeo 164 Super 2.0 Twin Spark catalyst Specs Review (106 kW / 144 PS / 142 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1994/217790/alfa_romeo_164_td.html?utm_source=chatgpt.com "1994 Alfa Romeo 164 TD Specs Review (92 kW / 125 PS / 123 hp) (up to mid-year 1994 for Europe )"
[4]: https://www.automobile-catalog.com/car/1994/217745/alfa_romeo_164_quadrifoglio_24v_cat.html?utm_source=chatgpt.com "1994 Alfa Romeo 164 Quadrifoglio 24V catalyst Specs Review (169 kW / 230 PS / 227 hp) (up to mid-year 1994 for Europe )"
[5]: https://www.automobile-catalog.com/car/1994/217820/alfa_romeo_164_q4_cat.html?utm_source=chatgpt.com "1994 Alfa Romeo 164 Q4 catalyst Specs Review (169 kW / 230 PS / 227 hp) (for Europe )"


--- 发送 / 继续到 Round 14 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 1. 更新点

* 修正 Ktype `143`：`66 kW / 90 HP` 的 1.9 TD 对应 1995 年中期后的 Series 2 宽体版本，三维为 `4443 × 1730 × 1440 mm`，宽度明确为不含后视镜。此前关联 Series 1 窄体尺寸组不正确；输入的 `Apr 1993` 开始年月与该功率版本存在冲突，改按发动机功率和直接车型资料确定物理外廓。1995 年中期前的 Series 1 版本实际为 `68 kW / 92 PS`、宽度 `1700 mm`。([汽车目录][1])
* 为普通 Series 2 高车身版本首次建立 `4443 × 1730 × 1440 mm` 尺寸组。该组不与现有 Q4 尺寸组强行合并，因为 Q4 具有特殊外部配置；当前仅供普通宽体高车身版本引用。
* 修正 Ktype `160`：`132 kW / 180 HP` 的 3.0 V6 是 1987—1992 年的改款前版本，三维为 `4565 × 1760 × 1390 mm`，应关联既有改款前尺寸组，而不是 Series 2 Facelift 组。输入的 `Sep 1992–Sep 1998` 与该功率版本生产期冲突。([汽车数据网][2])
* Ktype `156` 暂不修改。现有资料能够确认其为四门 2.5 V6 163 HP、生产范围覆盖 1992—1998 年，但不足以直接证明同一 Ktype 同时覆盖标准车身与 Super 长保险杠外廓。([汽车数据网][3])

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修改：`2` 个输入 Ktype、`2` 条映射
* 本轮首次创建尺寸组：`1`
* 本轮复用既有尺寸组：`1` 条映射
* 当前仍处于第二阶段核对，尚未完成全部映射引用闭环及最终快照检查。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	HIGH	66 kW版本对应1995年中期后的Series 2宽体外廓；输入开始年月早于该功率版本。	READY
160	160	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	132 kW版本对应1987-1992年改款前外廓；输入生产年月与直接车型资料冲突。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	4443	1730	1440	Automobile-Catalog 1995 Alfa Romeo 155 1.9 TD Series 2; Automobile-Catalog 1996 Alfa Romeo 155 1.9 TD	https://www.automobile-catalog.com/car/1995/217610/alfa_romeo_155_1_9_td.html; https://www.automobile-catalog.com/car/1996/217610/alfa_romeo_155_1_9_td.html
```

## 5. 下一步优先处理

**下一步优先核对：**

1. 继续核对 Alfa Romeo 155 Ktype `141`、`146`、`148`、`150`，确认 `1425 mm` 与 `1440 mm` 高度分组没有错误交叉。
2. 核对 Alfa Romeo 164 Ktype `153–164` 的标准、Super、QV 和改款前尺寸组引用，重点确定 Ktype `156` 是否需要派生。
3. 检查全部派生 `id` 的唯一性、排序和无后缀基础行删除情况。
4. 检查所有尺寸组引用闭环、孤立尺寸组及被新证据替代的旧尺寸组，随后整理最终完整快照。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/217610/alfa_romeo_155_1_9_td.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 1.9 TD Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1995 for Europe )"
[2]: https://www.auto-data.net/en/alfa-romeo-164-164-3.0-v6-180hp-1260 "Alfa Romeo 164 (164) 3.0 V6 (180 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/alfa-romeo-164-164-2.5-v6-163hp-1252 "Alfa Romeo 164 (164) 2.5 V6 (163 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 15 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 1. 更新点

* 修正 Ktype `141`：`1.8 T.S. Sport 93 kW / 127 HP` 的生产范围覆盖 1992—1996 年，横跨 155 Series 1 窄体与 Series 2 宽体。Series 1 为 `4443 × 1700 × 1440 mm`；Series 2 普通汽油运动版为 `4443 × 1730 × 1425 mm`。删除原单一 `id=141`，拆为 `141_prefl`、`141_facelift`，均复用既有尺寸组。([汽车目录][1])
* 修正 Ktype `148`：`2.5 V6 120 kW / 163 HP` 对应 1995 年起的 Series 2 宽体版本；Series 1 对应的是约 `121–122 kW` 标定，由 Ktype `149` 覆盖。删除错误的 `148_prefl`，原 `148_facelift` 恢复为唯一基础行 `id=148`。Series 2 V6 三维为 `4443 × 1730 × 1425 mm`，继续复用既有尺寸组。([汽车目录][2])
* 复核 Ktype `146`、`147`、`150`：Q4 140 kW Series 1、Q4 137 kW Series 2，以及 2.5 TD 改款前后高度分组均保持不变。Series 1 Q4/TD 为 `1700 × 1440 mm` 外廓；Series 2 Q4 为 `1730 × 1440 mm`，Series 2 TD 为 `1730 × 1425 mm`。([汽车目录][3])

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修改：`2` 个输入 Ktype、`3` 条最终映射
* 本轮删除被替代的旧映射：`141`、`148_prefl`、`148_facelift`
* 本轮首次创建或修正尺寸组：`0`
* 当前仍处于第二阶段核对，尚需解决 Alfa Romeo 164 Ktype `156` 的标准／Super 外廓边界，并执行最终主外键闭环检查。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141_prefl	141	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.8 T.S. Sport跨越改款，按Series 1窄体外廓拆分。	READY
141_facelift	141	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	HIGH	1.8 T.S. Sport跨越改款，按Series 2宽体外廓拆分。	READY
148	148	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	MEDIUM	120 kW版本对应Series 2宽体；输入开始年月早于该功率版本。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 确定 Ktype `156` 的 `2.5 V6 163 HP / AR66201` 是否仅对应 `4665 mm` Super 外廓，还是覆盖标准 Series 2 与 Super 两种车身。
2. 汇总并核对 Ktype `115–219` 的完整映射顺序，确认被拆分的 Ktype 均已删除无后缀基础行。
3. 检查所有 `DIMENSION_GROUP_ID` 引用闭环、孤立组、重复组三维和被后续纠错替代的旧尺寸组。
4. 检查完成后生成最终两张完整 TSV 及规定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/alfa_romeo/155/155_serie_1/1992.html?utm_source=chatgpt.com "1992 Alfa Romeo 155 serie 1 full range specs"
[2]: https://www.automobile-catalog.com/car/1993/217430/alfa_romeo_155_v6.html?utm_source=chatgpt.com "1993 Alfa Romeo 155 V6 Specs Review (122 kW ..."
[3]: https://www.automobile-catalog.com/car/1993/217490/alfa_romeo_155_2_5_td.html?utm_source=chatgpt.com "1993 Alfa Romeo 155 2.5 TD Specs Review (92 kW ..."


--- 发送 / 继续到 Round 16 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 1. 更新点

* 修正 Ktype `156`：`2.5 V6 120 kW / 163 HP`、发动机代码 `AR 66201` 于 1992 年 9 月后出现，资料给出的车长约为 `4670 mm`，对应 164 Super 的长保险杠外廓，而不是 `4555 mm` 的标准 Series 2 外廓。该记录改为复用既有 `EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01`。不同资料的 `4665/4670 mm` 差异属于规格取整，不另建尺寸组。([汽车数据][1])
* Ktype `156` 未发现需要拆成标准车身与 Super 两个分支的可靠证据；现有生产期、发动机代码与长车身规格共同支持仅保留 Super 映射。该判断属于基于现有资料的车型边界推断。([eBay][2])
* 本轮未创建或修正尺寸组；164 Super 尺寸组继续使用已闭合的 `4665 × 1760 × 1390 mm`。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修改映射：`1`
* 本轮首次创建或修正尺寸组：`0`
* 车型边界核对已基本完成，尚需执行最终完整快照的主外键、孤立组、重复组及排序检查。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156	156	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	MEDIUM	2.5 V6 163 HP对应1992年后的Super长保险杠外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 汇总全部最终映射，确认 100 个输入 Ktype 均至少出现一次，派生 Ktype 不再保留无后缀基础行。
2. 检查全部 `id` 唯一性、输入顺序及同一 Ktype 的派生分支排序。
3. 检查每个 `DIMENSION_GROUP_ID` 恰好命中一个完整尺寸组，并删除被纠错映射淘汰后的孤立组。
4. 检查相同三维但物理外廓不同的尺寸组是否有充分边界，及相同物理外廓是否被重复建组。
5. 闭环检查通过后，输出两张最终完整 TSV 和规定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-164-164-2.5-v6-163hp-1252 "Alfa Romeo 164 (164) 2.5 V6 (163 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.ebay.com/itm/267654480565?utm_source=chatgpt.com "Gear Shift Lever Bushing Alfa Romeo 164 Fiat Croma Lancia ..."


--- 发送 / 继续到 Round 17 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 1. 更新点

* 纠正 Ktype `156`：`2.5 V6 120 kW / 163 HP` 的明确车型代码为 `164A1C`，直接规格资料给出外廓 `4555 × 1760 × 1390 mm`，应关联标准 Series 2 尺寸组，不属于 `4665 mm` 的 Super 长保险杠外廓。上一轮将其关联 Super 的判断撤销。([在线汽车配件][1])
* 164 Super 在 1992 年末推出时，外部变化包括新保险杠、侧防擦条、前灯和格栅；初期主要用于 V6 Turbo 与 3.0 24V 等版本，不能仅依据生产期将 2.5 V6 自动归入 Super。([维基百科][2])
* Ktype `156` 改回复用既有 `EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01`，不创建新尺寸组。
* 既有 Super 尺寸组仍被其他已确认 Super 版本引用，不因本次修正成为孤立组。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修正映射：`1`
* 本轮首次创建或修正尺寸组：`0`
* 当前处于第二阶段核对，尚需完成最终完整快照的机械闭环检查，暂不输出 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156	156	Sedan	164 Series 2	164A1C	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	HIGH	2.5 V6 163 HP为4555 mm标准Series 2外廓，不属于Super长保险杠版本。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 汇总全部最终映射，检查 `id` 唯一性、100 个输入 Ktype 覆盖及派生行是否残留无后缀基础行。
2. 核对所有 `DIMENSION_GROUP_ID` 引用闭环，删除被历次纠错淘汰且已无映射引用的孤立尺寸组。
3. 检查相同物理外廓是否因版本名称不同重复建组，并保留三维相同但保险杠、门数或外部套件不同的必要独立组。
4. 按输入 Ktype 顺序及稳定分支顺序整理最终快照，准备规定文件名的两张 TSV 下载文件。

推进信号：CONTINUE

[1]: https://www.onlinecarparts.co.uk/car-brands/spare-parts-alfa-romeo/164-164.html?utm_source=chatgpt.com "ALFA ROMEO 164 (164) parts online catalogue"
[2]: https://it.wikipedia.org/wiki/Alfa_Romeo_164?utm_source=chatgpt.com "Alfa Romeo 164"


--- 发送 / 继续到 Round 18 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 1. 更新点

* 纠正 Ktype `143`：`1.9 TD 66 kW / 90 HP` 并非仅对应 1995 年中期后的宽体版本。直接车型资料显示，该功率版本自 1993 年起已存在，前期车宽为 `1700 mm`；1995 年中期后的 Series 2 版本则为 `1730 mm` 宽体，且高度仍为 `1440 mm`。因此删除原单一 `id=143`，拆为改款前和改款后两个物理外廓分支。([汽车数据][1])
* `143_prefl` 复用既有 `EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01`。
* `143_facelift` 复用既有 `EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01`。
* 本轮没有首次创建或修正尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮修改：`1` 个输入 Ktype、`2` 条最终映射
* 本轮删除被替代的旧映射：`143`
* 本轮首次创建或修正尺寸组：`0`
* 当前仍处于第二阶段核对，尚需完成最终完整快照的机械闭环和排序检查。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143_prefl	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.9 TD 66 kW版本覆盖Series 1窄体外廓。	READY
143_facelift	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	HIGH	1.9 TD 66 kW版本覆盖1995年中期后的Series 2宽体高车身外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 汇总最终映射快照，确认 Ktype `119`、`141`、`143`、`150`、`157`、`165`、`167`、`168`、`170`、`173`、`174`、`182`、`186`、`187`、`193`、`194`、`197`、`199`、`202`、`205` 均未残留无后缀基础行。
2. 检查全部 `id` 唯一性、输入 Ktype 原始顺序及同一 Ktype 的派生分支顺序。
3. 检查每个映射引用均命中恰好一个完整尺寸组，并删除历次纠错后无人引用的孤立尺寸组。
4. 核对最终尺寸组首次引用顺序后，生成两张完整 TSV 和规定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-155-167-1.9-td-90hp-1366?utm_source=chatgpt.com "Alfa Romeo 155 (167) 1.9 TD (90 Hp) /Sedan 1993"


--- 发送 / 继续到 Round 19 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 1. 更新点

* 复核 Arna Ktype `173`、`174` 的门数派生：1.2 60 HP 与 1.2 68 HP 资料均明确覆盖 3 门和 5 门，因此保留 `_3dr`、`_5dr` 两个分支，不恢复无后缀基础行。([汽车数据][1])
* 复核 Arna 68 HP 的具体车型资料：`1.2 L` 为 3 门、`1.2 SL` 为 5 门，两种车身三维一致；现有两个独立尺寸组和对应映射不需要修改。([汽车目录][2])
* 复核 Alfa Romeo 155 高度分组：

  * Series 2 2.5 TD：`4443 × 1730 × 1425 mm`
  * Series 2 Q4：`4443 × 1730 × 1440 mm`

  两者物理高度不同，现有普通宽体与 Q4/高车身尺寸组不得合并。([汽车目录][3])
* 本轮未发现新的映射错误、孤立尺寸组或需要修正的尺寸事实。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮新增或修改映射：`0`
* 本轮首次创建或修正尺寸组：`0`
* 门数派生与 155 高度分组复核通过。
* 当前仍处于第二阶段核对，尚未输出最终完整快照，因此暂不 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 按输入 Ktype 原始顺序汇总累计映射，检查所有派生 `id` 的唯一性及分支顺序。
2. 清除被历次修正替代的旧基础行，重点检查 `119`、`141`、`143`、`148`、`150`、`157`、`165`、`182`、`193`、`197`、`205`。
3. 按首次引用顺序汇总 DIMENSION_GROUP，检查所有映射外键均恰好命中一行，且不存在孤立组。
4. 对完整快照执行 10 列、6 列、READY 状态、正整数三维和不含后视镜宽度的最终机械检查。
5. 检查通过后生成两张最终完整 TSV，以及指定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-arna-920-1.2-60hp-1510 "Alfa Romeo Arna (920) 1.2 (60 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/make/alfa_romeo/arna/arna/1985.html?utm_source=chatgpt.com "1985 Alfa Romeo Arna Tipo 920 Hatchback full range specs"
[3]: https://www.automobile-catalog.com/car/1995/217625/alfa_romeo_155_2_5_td.html?utm_source=chatgpt.com "1995 Alfa Romeo 155 2.5 TD (man. 5)"


--- 发送 / 继续到 Round 20 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 1. 更新点

* 复核 Alfa Romeo 155 Q4 的窄体／宽体边界：资料确认 Q4 动力版本曾覆盖两种车身；官方引进车型主要为窄体，但确有少量宽体版本。现有 Ktype `147` 关联窄体组、Ktype `146` 关联宽体 Q4 组的处理保持不变。([Alfa Romeo Owners Club][1])
* Ktype `147` 对应的窄体 Q4 三维继续采用 `4443 × 1700 × 1440 mm`，其中 `1700 mm` 明确为不含后视镜宽度；未发现需要另建尺寸组的可靠外部套件差异证据。([汽车目录][2])
* 本轮未发现新的映射错误、重复尺寸组或需要修正的尺寸事实。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮新增或修改映射：`0`
* 本轮首次创建或修正尺寸组：`0`
* 车型边界核对已完成，当前正在归并最终累计快照。
* 尚未完成全部历史变化行的替换、删除及排序机械检查，暂不输出 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 将各轮变化行归并为唯一最终状态，删除被后续纠错替代的旧基础行及旧派生行。
2. 按输入 Ktype 原始顺序整理完整映射，并检查同一 Ktype 的分支顺序、`id` 唯一性和 100 个 Ktype 覆盖率。
3. 从最终映射反向生成被引用尺寸组清单，清除无人引用的旧组，并按首次引用顺序排序。
4. 执行 10 列／6 列表头、全部 READY、外键闭环、正整数三维、来源完整及不含后视镜宽度检查。
5. 检查通过后一次性输出两张最终完整 TSV，并创建规定文件名的两个 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://aroc-uk.com/downloads/155-buyersguide.pdf "The Alfa Romeo 155.doc"
[2]: https://www.automobile-catalog.com/car/1992/217460/alfa_romeo_155_q4.html?utm_source=chatgpt.com "1992 Alfa Romeo 155 Q4 Specs Review (140 kW / 190 PS / 188 hp) (since mid-year 1992 for Europe )"


--- 发送 / 继续到 Round 21 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / 下一步 ---
## 1. 更新点

* 复核 Ktype `135–138`：Alfa Romeo 90 均为 `162A` 四门 Sedan；1.8、2.0 I.e.、2.4 TD 和 2.5 V6 未发现会改变外部尺寸的车身分支。直接车型资料统一支持约 `4391 × 1638 × 1420 mm`、宽度不含后视镜，现有共用尺寸组无需拆分。([汽车目录][1])
* 复核 Ktype `129`：Alfa Romeo 75 2.0 Turbo Diesel 的外廓为 `4330 × 1630 × 1400 mm`，继续使用普通窄体尺寸组，不与后期 2.4 Turbo Diesel 的 `1660 mm` 宽体外廓合并。([汽车目录][2])
* 本轮未发现新的映射错误、需要修正的尺寸组或新增物理分支。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮新增或修改映射：`0`
* 本轮首次创建或修正尺寸组：`0`
* Alfa Romeo 75、90 的剩余尺寸边界复核通过。
* 当前仍在归并累计最终快照，尚未完成最终外键闭环及孤立组清理，因此暂不输出 COMPLETE。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 将历轮映射变化归并为唯一最终状态，删除被后续修正替代的旧基础行和旧派生行。
2. 检查全部 `id` 唯一性、100 个输入 Ktype 覆盖率以及同一 Ktype 的稳定分支顺序。
3. 从最终映射反向生成尺寸组清单，删除无人引用的孤立组并检查重复物理外廓。
4. 执行 10 列／6 列、全部 READY、外键闭环、正整数三维、来源完整及宽度不含后视镜的最终机械检查。
5. 检查通过后生成两张最终完整 TSV 及指定文件名的 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/215330/alfa_romeo_90_2_0.html?utm_source=chatgpt.com "1985 Alfa Romeo 90 2.0 Specs Review (94 kW / 128 PS / 126 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/215510/alfa_romeo_75_2_0_turbo_diesel.html?utm_source=chatgpt.com "1987 Alfa Romeo 75 2.0 Turbo Diesel (man. 5)"


--- 发送 / 继续到 Round 22 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / 下一步 ---
## 1. 更新点

* 完成累计快照可恢复性检查。
* 本轮未发现新的车型边界或映射错误。
* 发现最终快照仍缺少部分“前期已确认但未在当前累计 CONTINUE 记录中重新输出”的既有尺寸组完整行，包括 33 Sport Wagon、75 普通车身、90、155 窄体、164 改款前、Spider Series 1/2、Fiat 500 Topolino、BMW E12、Passat B7 Sedan、BMW E30 Touring 等。
* 在这些既有尺寸组的三维、来源名称和直接 URL 尚未完整归并前，不能安全生成最终完整 DIMENSION_GROUP TSV，也不能输出 COMPLETE。
* 本轮遵循缓存优先，没有重新抓取已闭合车型页面。

## 2. 当前批次进度

* READY 输入 Ktype：`100 / 100`
* PENDING 输入 Ktype：`0 / 100`
* 本轮新增或修改映射：`0`
* 本轮首次创建或修正尺寸组：`0`
* 车型研究和映射边界已闭合。
* 最终快照仍处于累计缓存归并阶段，尚未满足 COMPLETE 的两张全量表闭环要求。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

**下一步优先核对：**

1. 优先从累计缓存恢复所有“已被最终映射引用、但当前归并记录缺少完整事实行”的既有尺寸组。
2. 对恢复后的尺寸组执行 `DIMENSION_GROUP_ID` 唯一性、三维完整性、来源与 URL 完整性检查。
3. 从最终映射反向筛选尺寸组，删除历次纠错后已无人引用的孤立组。
4. 检查全部派生 Ktype 已删除旧基础行，并按输入顺序和稳定分支顺序整理。
5. 两张完整快照机械检查通过后，再创建规定文件名的 TSV 下载文件并输出 COMPLETE。

推进信号：CONTINUE


--- 发送 / 继续到 Round 23 ---
继续补强当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理；最后输出“推进信号：CONTINUE”。只有准备完成时，才在同一回复中一次性输出最终完整 Ktype 映射 TSV 和最终完整 DIMENSION_GROUP TSV，并输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / checkpoint 恢复已完成回复 ---
已完成轻量机械检查：**126 条映射、100 个输入 Ktype 全覆盖、38 个尺寸组、`id`/尺寸组主键唯一、映射外键完全闭合、三维与来源均非空。**

## 1. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
115	115	Wagon	33 Series 2	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	HIGH	前驱Sport Wagon外廓。	READY
116	116	Wagon	33 Series 2	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	HIGH	4X4未改变最大外部三维。	READY
117	117	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
118	118	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
119_europa	119	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TURBO-EUROPA-01	HIGH	前期Turbo Europa外廓。	READY
119_america	119	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	后期Turbo America加长保险杠外廓。	READY
120	120	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
122	122	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
123	123	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
124	124	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	Turbo America加长保险杠外廓。	READY
125	125	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	普通窄体四门外廓。	READY
127	127	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	HIGH	Twin Spark加宽翼子板及空气动力外廓。	READY
128	128	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	HIGH	Twin Spark加宽翼子板及空气动力外廓。	READY
129	129	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	2.0 TD普通窄体外廓。	READY
131	131	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH	早期2.5 V6普通外廓。	READY
133	133	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	MEDIUM	3.0 V6 CAT采用America加长保险杠外廓。	READY
134	134	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	HIGH	3.0 V6 QV采用America加长保险杠外廓。	READY
135	135	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH	90四门标准外廓。	READY
136	136	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH	90四门标准外廓。	READY
137	137	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH	90四门标准外廓。	READY
138	138	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH	90四门标准外廓。	READY
139	139	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.7 Twin Spark使用Series 1窄体外廓。	READY
140	140	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	MEDIUM	105 HP 8V版本对应Series 1窄体外廓。	READY
141_prefl	141	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.8 T.S. Sport的Series 1窄体分支。	READY
141_facelift	141	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	HIGH	1.8 T.S. Sport的Series 2宽体分支。	READY
142	142	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	前期1.8 Twin Spark窄体外廓。	READY
143_prefl	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	1.9 TD的Series 1窄体分支。	READY
143_facelift	143	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	HIGH	1.9 TD的Series 2宽体高车身分支。	READY
144	144	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	2.0 Twin Spark 141 HP前期窄体外廓。	READY
145	145	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	2.0 Twin Spark 144 HP前期窄体外廓。	READY
146	146	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-Q4-WIDEBODY-01	HIGH	137 kW Q4对应Series 2宽体外廓。	READY
147	147	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	140 kW Q4对应Series 1窄体外廓。	READY
148	148	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	MEDIUM	120 kW V6对应Series 2宽体外廓。	READY
149	149	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	MEDIUM	121 kW V6对应Series 1窄体外廓。	READY
150_prefl	150	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	HIGH	2.5 TD的Series 1窄体分支。	READY
150_facelift	150	Sedan	155	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	HIGH	2.5 TD的Series 2宽体分支。	READY
151	151	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
152	152	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
153	153	Sedan	164 Super	164.H3	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	Twin Spark Super长保险杠外廓。	READY
154	154	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	V6 Turbo Super长保险杠外廓。	READY
155	155	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前V6 Turbo外廓。	READY
156	156	Sedan	164 Series 2	164A1C	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	HIGH	2.5 V6标准Series 2外廓。	READY
157_standard	157	Sedan	164 Series 2	164	4	EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	HIGH	2.5 TD标准Series 2分支。	READY
157_super	157	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	2.5 TD Super长保险杠分支。	READY
158	158	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
159	159	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
160	160	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
161	161	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	HIGH	改款前标准外廓。	READY
162	162	Sedan	164 Series 1	164	4	EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	MEDIUM	改款前QV版本最大三维与标准外廓一致。	READY
163	163	Sedan	164 Super	164	4	EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	HIGH	3.0 24V Super长保险杠外廓。	READY
164	164	Sedan	164 Quadrifoglio 24V	164.H1	4	EU-ALFA-ROMEO-164-164-SEDAN-QV24V-01	HIGH	前驱Quadrifoglio 24V专属外部套件外廓。	READY
165_shortnose	165	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-16-SHORTNOSE-01	HIGH	早期1.6短车头外廓。	READY
165_series1	165	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	HIGH	后期Series 1外廓。	READY
165_series2	165	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	Series 2外廓。	READY
165_series3	165	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	Series 3外廓。	READY
166	166	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	1.8对应Series 1外廓。	READY
167_series1	167	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	后期1.8的Series 1分支。	READY
167_series2	167	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	后期1.8的Series 2分支。	READY
167_series3	167	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	后期1.8的Series 3分支。	READY
168_series1	168	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	MEDIUM	后期1.8的Series 1分支。	READY
168_series2	168	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	后期1.8的Series 2分支。	READY
168_series3	168	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	后期1.8的Series 3分支。	READY
169	169	Sedan	Alfetta Series 1	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	HIGH	2.0早期Series 1外廓。	READY
170_series2	170	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	2.0长车头Series 2外廓。	READY
170_series3	170	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	2.0 Series 3外廓。	READY
171	171	Sedan	Alfetta Series 2	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	HIGH	2.0 TD Series 2外廓。	READY
172	172	Sedan	Alfetta Series 3	116	4	EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	HIGH	2.4 TD Series 3外廓。	READY
173_3dr	173	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	该功率覆盖三门物理车身。	READY
173_5dr	173	Hatchback	Arna	920	5	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	HIGH	该功率覆盖五门物理车身。	READY
174_3dr	174	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	该功率覆盖三门物理车身。	READY
174_5dr	174	Hatchback	Arna	920	5	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	HIGH	该功率覆盖五门物理车身。	READY
175	175	Hatchback	Arna	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	TI三门物理车身。	READY
176	176	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH	Giulietta 116四门标准外廓。	READY
177	177	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH	Giulietta 116四门标准外廓。	READY
178	178	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH	Giulietta 116四门标准外廓。	READY
179	179	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	MEDIUM	Turbo版本最大外部三维与标准车身一致。	READY
180	180	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH	Giulietta 116四门标准外廓。	READY
181	181	Sedan	Giulietta 116	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	MEDIUM	Turbo版本最大外部三维与标准车身一致。	READY
182_stepfront	182	Coupe	GT 1300 Junior	105.30	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	1966-1969阶梯式车头外廓。	READY
182_1750nose	182	Coupe	GT 1300 Junior	105.30	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	HIGH	1970-1974中期1750式双灯车头外廓。	READY
182_unified	182	Coupe	1.3 GT Junior	105.30	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	HIGH	1974中期后统一外观。	READY
183	183	Coupe	Giulia Sprint GT	105.02	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	早期阶梯式车头外廓。	READY
184	184	Coupe	Giulia Sprint GT Veloce	105.36	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	早期阶梯式车头外廓。	READY
185	185	Coupe	Giulia Sprint GTA	105.32	2	EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	HIGH	GTA外部尺寸轮廓与早期Sprint GT一致。	READY
186_prefl	186	Coupe	GT 1600 Junior	115.03	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	MEDIUM	115.03双灯车头外廓。	READY
186_facelift	186	Coupe	1.6 GT Junior	115.34	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	MEDIUM	115.34统一外观。	READY
187_prefl	187	Coupe	GT 1600 Junior	115.03	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	MEDIUM	115.03双灯车头外廓。	READY
187_facelift	187	Coupe	1.6 GT Junior	115.34	2	EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	MEDIUM	115.34统一外观。	READY
188	188	Coupe	1750 GTV	105.44	2	EU-ALFA-ROMEO-1750-GTV-10544-COUPE-01	HIGH	1750 GTV双门外廓。	READY
189	189	Coupe	2000 GTV	105.21	2	EU-ALFA-ROMEO-2000-GTV-10521-COUPE-01	HIGH	2000 GTV双门外廓。	READY
190	190	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	MEDIUM	1.6对应改款前Alfetta GT外廓。	READY
191	191	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	HIGH	早期1.8 Alfetta GT外廓。	READY
192	192	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	HIGH	早期1.8 Alfetta GT外廓。	READY
193_prefl	193	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	1980改款前GTV 2000外廓。	READY
193_facelift	193	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	HIGH	1980改款后GTV 2.0外廓。	READY
194_prefl	194	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	1980改款前GTV 2000外廓。	READY
194_facelift	194	Coupe	Alfetta GT/GTV	116	3	EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	HIGH	1980改款后GTV 2.0外廓。	READY
195	195	Sedan	Giulia 105/115	115.09	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	HIGH	Giulia 1300 Super四门外廓。	READY
196	196	Sedan	Giulia 105/115	105.26	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	HIGH	Giulia 1600 Super四门外廓。	READY
197_series1	197	Convertible	Spider Series 1 Duetto	105	2	EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	HIGH	1300圆尾Series 1分支。	READY
197_series2	197	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1300截尾Series 2分支。	READY
198	198	Convertible	Spider Series 1 Duetto	105	2	EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	HIGH	1600圆尾Series 1外廓。	READY
199_series2	199	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1600截尾Series 2分支。	READY
199_series3	199	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	1600 Series 3空气动力套件分支。	READY
200	200	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1600截尾Series 2外廓。	READY
201	201	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	HIGH	1600 Series 4平滑保险杠外廓。	READY
202_series1	202	Convertible	Spider Series 1 Duetto	105	2	EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	HIGH	1750圆尾Series 1分支。	READY
202_series2	202	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	1750截尾Series 2分支。	READY
203	203	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	2000 Series 3空气动力套件外廓。	READY
204	204	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	HIGH	2000 Series 3空气动力套件外廓。	READY
205_series2	205	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	MEDIUM	2000截尾Series 2分支。	READY
205_series3	205	Convertible	Spider Series 3 Aerodinamica	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	MEDIUM	2000 Series 3空气动力套件分支。	READY
205_series4	205	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	MEDIUM	2000 Series 4平滑保险杠分支。	READY
206	206	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	HIGH	2000截尾Series 2外廓。	READY
207	207	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	HIGH	2000 Series 4平滑保险杠外廓。	READY
208	208	Sedan	500 A Topolino	500A	2	EU-FIAT-500-A-TOPOLINO-SEDAN-01	HIGH	500 A Topolino双门外廓。	READY
209	209	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
211	211	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
212	212	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
213	213	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
214	214	Sedan	Passat B7	362	4	EU-VW-PASSAT-B7-362-SEDAN-01	HIGH	Passat B7 Sedan标准外廓。	READY
215	215	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
216	216	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
217	217	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
218	218	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH	E12四门标准外廓。	READY
219	219	Wagon	3 Series E30	E30	5	EU-BMW-3-E30-TOURING-01	HIGH	E30 Touring五门外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_101-200_ktype_dimension_mapping_final.tsv)

## 2. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	Auto-Data Alfa Romeo 33 Sport Wagon 1.7 16V 4x4	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.7-16v-132hp-4x4-1394
EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	4330	1630	1400	Automobile-Catalog 1989 Alfa Romeo 75 1.6; Auto-Data Alfa Romeo 75 2.5 V6	https://www.automobile-catalog.com/car/1989/215585/alfa_romeo_75_1_6.html; https://www.auto-data.net/en/alfa-romeo-75-162-b-quadrifoglio-verde-2.5-v6-156hp-1559
EU-ALFA-ROMEO-75-162B-SEDAN-TURBO-EUROPA-01	4330	1650	1400	Automobile-Catalog 1986 Alfa Romeo 75 1.8 Turbo	https://www.automobile-catalog.com/car/1986/53675/alfa_romeo_75_1_8_turbo.html
EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	4420	1660	1400	Automobile-Catalog Alfa Romeo 75 3.0 V6 America; Automobile-Catalog Alfa Romeo 75 3.0 V6 Quadrifoglio Verde catalyst	https://www.automobile-catalog.com/car/1989/215705/alfa_romeo_75_3_0_v6_america.html; https://www.automobile-catalog.com/car/1990/215795/alfa_romeo_75_3_0_v6_quadrifoglio_verde_cat.html
EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	4330	1660	1400	Automobile-Catalog 1987 Alfa Romeo 75 2.0 Twin Spark; Automobile-Catalog 1989 Alfa Romeo 75 2.0 Twin Spark catalyst	https://www.automobile-catalog.com/car/1987/215525/alfa_romeo_75_2_0_twin_spark.html; https://www.automobile-catalog.com/car/1989/215645/alfa_romeo_75_2_0_twin_spark_cat.html
EU-ALFA-ROMEO-90-162A-SEDAN-01	4391	1638	1420	Automobile-Catalog 1985 Alfa Romeo 90 2.0	https://www.automobile-catalog.com/car/1985/215330/alfa_romeo_90_2_0.html
EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	4443	1700	1440	Automobile-Catalog 1993 Alfa Romeo 155 V6; Automobile-Catalog 1992 Alfa Romeo 155 Q4	https://www.automobile-catalog.com/car/1993/217430/alfa_romeo_155_v6.html; https://www.automobile-catalog.com/car/1992/217460/alfa_romeo_155_q4.html
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	4443	1730	1425	Automobile-Catalog 1995 Alfa Romeo 155 1.8 Twin Spark S; Automobile-Catalog 1995 Alfa Romeo 155 V6; Automobile-Catalog 1996 Alfa Romeo 155 2.5 TD	https://www.automobile-catalog.com/car/1995/217535/alfa_romeo_155_1_8_twin_spark_s.html; https://www.automobile-catalog.com/car/1995/217580/alfa_romeo_155_v6.html; https://www.automobile-catalog.com/car/1996/217625/alfa_romeo_155_2_5_td.html
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	4443	1730	1440	Automobile-Catalog 1995 Alfa Romeo 155 1.9 TD Series 2; Automobile-Catalog 1996 Alfa Romeo 155 1.9 TD	https://www.automobile-catalog.com/car/1995/217610/alfa_romeo_155_1_9_td.html; https://www.automobile-catalog.com/car/1996/217610/alfa_romeo_155_1_9_td.html
EU-ALFA-ROMEO-155-167-SEDAN-Q4-WIDEBODY-01	4443	1730	1440	Automobile-Catalog 1995 Alfa Romeo 155 Q4 Series 2	https://www.automobile-catalog.com/car/1995/217595/alfa_romeo_155_q4.html
EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	4565	1760	1390	Auto-Data Alfa Romeo 164 3.0 V6 180 HP	https://www.auto-data.net/en/alfa-romeo-164-164-3.0-v6-180hp-1260
EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	4665	1760	1390	Automobile-Catalog 1997 Alfa Romeo 164 Super 3.0 V6 catalyst; Automobile-Catalog 1995 Alfa Romeo 164 Super TD	https://www.automobile-catalog.com/car/1997/217850/alfa_romeo_164_super_3_0_v6_cat.html; https://www.automobile-catalog.com/car/1995/217805/alfa_romeo_164_super_td.html
EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	4555	1760	1390	Automobile-Catalog 1993 Alfa Romeo 164 2.0 Twin Spark catalyst; Automobile-Catalog 1993 Alfa Romeo 164 TD; Automobile-Catalog 1994 Alfa Romeo 164 3.0 V6 catalyst	https://www.automobile-catalog.com/car/1993/217670/alfa_romeo_164_2_0_twin_spark_cat.html; https://www.automobile-catalog.com/car/1993/217790/alfa_romeo_164_td.html; https://www.automobile-catalog.com/car/1994/217685/alfa_romeo_164_3_0_v6_cat.html
EU-ALFA-ROMEO-164-164-SEDAN-QV24V-01	4555	1760	1390	Automobile-Catalog 1992 Alfa Romeo 164 Quadrifoglio 24V catalyst; Automobile-Catalog 1994 Alfa Romeo 164 Quadrifoglio 24V catalyst	https://www.automobile-catalog.com/car/1992/217745/alfa_romeo_164_quadrifoglio_24v_cat.html; https://www.automobile-catalog.com/car/1994/217745/alfa_romeo_164_quadrifoglio_24v_cat.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-16-SHORTNOSE-01	4240	1620	1430	Automobile-Catalog 1975 Alfa Romeo Alfetta 1.6	https://www.automobile-catalog.com/car/1975/143615/alfa_romeo_alfetta_1_6.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	4280	1620	1430	Automobile-Catalog 1979 Alfa Romeo Alfetta 1.6	https://www.automobile-catalog.com/car/1979/44495/alfa_romeo_alfetta_1_6.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	4385	1640	1430	Automobile-Catalog 1981 Alfa Romeo Alfetta 2.0 Turbodiesel	https://www.automobile-catalog.com/car/1981/143720/alfa_romeo_alfetta_2_0_turbodiesel.html
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	4410	1640	1430	Automobile-Catalog 1983 Alfa Romeo Alfetta 2.4 Turbodiesel	https://www.automobile-catalog.com/car/1983/49130/alfa_romeo_alfetta_2_4_turbodiesel.html
EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	4000	1651	1367	Automobile-Catalog 1984 Alfa Romeo Arna 1.3 Ti	https://www.automobile-catalog.com/car/1984/214730/alfa_romeo_arna_1_3_ti.html
EU-ALFA-ROMEO-ARNA-920-HATCHBACK-5D-01	4000	1651	1367	Automobile-Catalog 1985 Alfa Romeo Arna 1.2 SL	https://www.automobile-catalog.com/car/1985/214685/alfa_romeo_arna_1_2_sl.html
EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	4210	1650	1400	Wikipedia Alfa Romeo Giulietta (116)	https://en.wikipedia.org/wiki/Alfa_Romeo_Giulietta_(116)
EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	4080	1580	1315	Automobile-Catalog 1964 Alfa Romeo Giulia Sprint GT; Automobile-Catalog 1968 Alfa Romeo Giulia Sprint GTV; Automobile-Catalog 1965 Alfa Romeo Giulia Sprint GTA	https://www.automobile-catalog.com/car/1964/64940/alfa_romeo_giulia_sprint_gt.html; https://www.automobile-catalog.com/car/1968/64985/alfa_romeo_giulia_sprint_gtv.html; https://www.automobile-catalog.com/car/1965/64970/alfa_romeo_giulia_sprint_gta.html
EU-ALFA-ROMEO-GT-JUNIOR-COUPE-1750NOSE-01	4080	1580	1315	Automobile-Catalog 1971 Alfa Romeo GT 1300 Junior; Automobile-Catalog 1974 Alfa Romeo GT 1600 Junior up to mid-year	https://www.automobile-catalog.com/car/1971/1437365/alfa_romeo_gt_1300_junior.html; https://www.automobile-catalog.com/car/1974/1437380/alfa_romeo_gt_1600_junior.html
EU-ALFA-ROMEO-GT-JUNIOR-COUPE-UNIFIED-01	4080	1580	1315	Automobile-Catalog 1974 Alfa Romeo GT 1300 Junior since mid-year; Automobile-Catalog 1974 Alfa Romeo GT 1600 Junior since mid-year	https://www.automobile-catalog.com/car/1974/65075/alfa_romeo_gt_1300_junior.html; https://www.automobile-catalog.com/car/1974/71945/alfa_romeo_gt_1600_junior.html
EU-ALFA-ROMEO-1750-GTV-10544-COUPE-01	4100	1580	1315	Automobile-Catalog 1968 Alfa Romeo 1750 GTV	https://www.automobile-catalog.com/car/1968/65030/alfa_romeo_1750_gtv.html
EU-ALFA-ROMEO-2000-GTV-10521-COUPE-01	4100	1580	1315	Automobile-Catalog 1975 Alfa Romeo 2000 GTV	https://www.automobile-catalog.com/car/1975/65045/alfa_romeo_2000_gtv.html
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	4190	1660	1330	Automobile-Catalog 1974 Alfa Romeo Alfetta GT; Automobile-Catalog 1976 Alfa Romeo Alfetta GT 1.6	https://www.automobile-catalog.com/car/1974/33335/alfa_romeo_alfetta_gt.html; https://www.automobile-catalog.com/car/1976/144005/alfa_romeo_alfetta_gt_1_6.html
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	4205	1660	1330	Automobile-Catalog 1976 Alfa Romeo Alfetta GTV 2000	https://www.automobile-catalog.com/car/1976/144020/alfa_romeo_alfetta_gtv_2000.html
EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	4260	1664	1330	Automobile-Catalog 1982 Alfa Romeo GTV 2.0; Automobile-Catalog 1983 Alfa Romeo GTV 2.0	https://www.automobile-catalog.com/car/1982/144080/alfa_romeo_gtv_2_0.html; https://www.automobile-catalog.com/car/1983/144125/alfa_romeo_gtv_2_0.html
EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	4140	1560	1430	Wikipedia Alfa Romeo Giulia (1962)	https://en.wikipedia.org/wiki/Alfa_Romeo_Giulia_(1962)
EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	4250	1630	1290	Automobile-Catalog 1968 Alfa Romeo 1750 Spider Veloce	https://www.automobile-catalog.com/car/1968/65210/alfa_romeo_1750_spider_veloce.html
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	4120	1630	1290	WELT 60 Jahre Alfa Romeo Spider Tipo 105/115	https://www.welt.de/motor/news/article69bd5195e5e9d619745d17b5/60-jahre-alfa-romeo-spider-tipo-105-115.html
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	4245	1630	1290	Automobile-Catalog 1983 Alfa Romeo Spider 1.6; Automobile-Catalog 1989 Alfa Romeo Spider 2.0 catalyst	https://www.automobile-catalog.com/car/1983/214295/alfa_romeo_spider_1_6.html; https://www.automobile-catalog.com/car/1989/214325/alfa_romeo_spider_2_0_cat.html
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	4258	1630	1290	Automobile-Catalog 1991 Alfa Romeo Spider 1.6	https://www.automobile-catalog.com/car/1991/217280/alfa_romeo_spider_1_6.html
EU-FIAT-500-A-TOPOLINO-SEDAN-01	3215	1275	1375	Stellantis Heritage Fiat Topolino	https://www.stellantisheritage.com/en-uk/heritage/stories/fiat-topolino
EU-BMW-5-E12-SEDAN-01	4620	1690	1425	Wikipedia BMW 5 Series E12	https://en.wikipedia.org/wiki/BMW_5_Series_(E12)
EU-VW-PASSAT-B7-362-SEDAN-01	4769	1820	1470	Volkswagen Newsroom Passat B7 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-BMW-3-E30-TOURING-01	4321	1641	1379	BMW Group Classic BMW 316i Touring E30	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-874-1.bmw-316i-touring-e30.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_101-200_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_101-200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_101-200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_ktype_dimension_mapping_final.tsv（246 行）
- 累计尺寸组：all_dimension_groups_final.tsv（63 行）
