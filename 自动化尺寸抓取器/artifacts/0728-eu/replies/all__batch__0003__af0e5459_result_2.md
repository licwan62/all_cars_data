# 任务：all 第 201-300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0003__af0e5459


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 201-300 行

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

建议按各尺寸组第一次在 Ktype 映射表中被引用的顺序排列。一个组只出现一次。尺寸组顺序仅用于稳定输出，不得因非阻塞的排序差异延迟 `COMPLETE`。

### 第二阶段轻量收尾

1. 第一阶段只负责消除数据缺失；当进度达到 `PENDING=0`、`READY=全部输入行` 时，数据阶段结束。
2. 第二阶段最多只允许一轮轻量机械检查：两张表表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、每个映射引用闭合、长宽高和来源非空、两个任务指定下载链接存在。
3. 第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复抓取，也不得重新验证已经首次确认并缓存的尺寸组。
4. `PENDING=0` 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以 `推进信号：COMPLETE` 结束；不得再输出 `CONTINUE`。
5. 非阻塞的排序、措辞、置信度微调或来源偏好不影响完成。只要既有尺寸组已按首次创建规则确认且映射闭合，应优先完成并给出链接。

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

`PENDING=0` 后立即按以下机械条件组装最终产物；全部满足即可输出 `推进信号：COMPLETE`，无需再做第二轮外部核对：

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

任一机械条件不满足时，只修复该具体产物问题；不得重新展开逐车型研究。修复后立即输出两张完整 TSV、下载链接和 `COMPLETE`。

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
执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。

【配置附加规则】


【当前文件名】
all.tsv

【当前独立任务】
all 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Alfa Romeo	33	1.5 4X4	Schrägheck	Allrad	Benzin	62	84	Nov 1983	Dec 1984	2024-03-01	220
BMW	5	518	Stufenheck	Heckantrieb	Benzin	66	90	Jun 1981	Sep 1984	2024-03-01	221
Alfa Romeo	33	1.5 4X4	Schrägheck	Allrad	Benzin	66	90	Jan 1985	Sep 1986	2024-03-01	222
BMW	5	518 I	Stufenheck	Heckantrieb	Benzin	77	105	May 1981	Dec 1987	2024-03-01	223
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	92	125	Jun 1981	Dec 1987	2024-03-01	224
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	95	129	Aug 1985	Dec 1987	2024-03-01	225
BMW	5	524 D	Stufenheck	Heckantrieb	Diesel	63	86	Mar 1986	Dec 1987	2024-03-01	226
BMW	5	524 TD	Stufenheck	Heckantrieb	Diesel	85	115	Sep 1983	Dec 1987	2024-03-01	227
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	110	150	Jun 1981	Dec 1987	2024-03-01	228
BMW	5	525 E	Stufenheck	Heckantrieb	Benzin	90	122	Sep 1981	Dec 1987	2024-03-01	229
BMW	5	525 E	Stufenheck	Heckantrieb	Benzin	92	125	Mar 1983	Dec 1987	2024-03-01	230
BMW	5	525 E	Stufenheck	Heckantrieb	Benzin	95	129	Sep 1985	Dec 1987	2024-03-01	231
BMW	5	528 I	Stufenheck	Heckantrieb	Benzin	135	184	Jun 1981	Dec 1987	2024-03-01	232
BMW	5	535 I, M 535 I	Stufenheck	Heckantrieb	Benzin	136	185	Jan 1985	Dec 1987	2024-03-01	233
BMW	5	535 I, M 535 I	Stufenheck	Heckantrieb	Benzin	141	192	Jan 1985	Dec 1987	2024-03-01	234
BMW	5	535 I	Stufenheck	Heckantrieb	Benzin	162	220	Jan 1985	Dec 1987	2024-03-01	235
Alfa Romeo	33	1.5 4X4	Schrägheck	Allrad	Benzin	77	105	Sep 1986	Dec 1989	2024-03-01	236
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	95	129	Jun 1987	Sep 1990	2024-03-01	237
BMW	5	520 I 24V	Stufenheck	Heckantrieb	Benzin	110	150	Apr 1990	Aug 1995	2024-03-01	238
BMW	5	524 TD	Stufenheck	Heckantrieb	Diesel	85	115	Mar 1988	Aug 1991	2024-03-01	239
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	125	170	Feb 1988	Aug 1990	2024-03-01	240
BMW	5	525 I 24V	Stufenheck	Heckantrieb	Benzin	141	192	Mar 1990	Aug 1995	2024-03-01	241
BMW	5	525 IX 24V	Stufenheck	Allrad	Benzin	141	192	Oct 1991	Aug 1995	2024-03-01	242
BMW	5	525 TDS	Stufenheck	Heckantrieb	Diesel	105	143	Sep 1991	Aug 1995	2024-03-01	243
BMW	5	530 I	Stufenheck	Heckantrieb	Benzin	138	188	Jan 1988	Apr 1990	2024-03-01	244
BMW	5	530 I V8	Stufenheck	Heckantrieb	Benzin	160	218	Sep 1992	Dec 1995	2024-03-01	245
BMW	5	535 I	Stufenheck	Heckantrieb	Benzin	155	211	Nov 1987	Feb 1993	2024-03-01	246
BMW	5	M5	Stufenheck	Heckantrieb	Benzin	232	315	Sep 1988	Mar 1992	2024-03-01	247
BMW	5	M5	Stufenheck	Heckantrieb	Benzin	250	340	Jan 1992	Jul 1995	2024-03-01	249
BMW	5	540 I V8	Stufenheck	Heckantrieb	Benzin	210	286	Sep 1992	Dec 1995	2024-03-01	250
BMW	5	520 I	Kombi	Heckantrieb	Benzin	110	150	Jul 1991	Jul 1996	2024-03-01	251
BMW	5	525 I	Kombi	Heckantrieb	Benzin	141	192	Jul 1991	Jul 1996	2024-03-01	252
BMW	5	525 IX	Kombi	Allrad	Benzin	141	192	Jan 1992	Mar 1996	2024-03-01	253
BMW	5	525 TDS	Kombi	Heckantrieb	Diesel	105	143	Dec 1991	Jul 1996	2024-03-01	254
BMW	5	530 I	Kombi	Heckantrieb	Benzin	160	218	Sep 1992	Jul 1996	2024-03-01	255
BMW	2500-3.3	2500	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1968	Apr 1977	2024-03-01	256
BMW	2500-3.3	2.8 L	Stufenheck	Heckantrieb	Benzin	125	170	Feb 1975	Apr 1977	2024-03-01	257
BMW	2500-3.3	2800	Stufenheck	Heckantrieb	Benzin	125	170	Oct 1968	Jul 1975	2024-03-01	258
BMW	2500-3.3	3.0 S	Stufenheck	Heckantrieb	Benzin	132	180	May 1971	Apr 1977	2024-03-01	259
BMW	2500-3.3	3.0 L	Stufenheck	Heckantrieb	Benzin	132	180	Feb 1975	Apr 1977	2024-03-01	260
BMW	2500-3.3	3.0 SI	Stufenheck	Heckantrieb	Benzin	143	194	Oct 1975	Apr 1977	2024-03-01	261
BMW	2500-3.3	3.0 SI	Stufenheck	Heckantrieb	Benzin	147	200	Jul 1971	Sep 1975	2024-03-01	262
BMW	2500-3.3	3.2 LI	Stufenheck	Heckantrieb	Benzin	147	200	Oct 1975	Apr 1977	2024-03-01	263
BMW	2500-3.3	3.3 L	Stufenheck	Heckantrieb	Benzin	140	190	Jan 1974	Sep 1976	2024-03-01	264
BMW	2.5-3.2	2.5 CS	Coupe	Heckantrieb	Benzin	110	150	Sep 1974	Mar 1976	2024-03-01	265
BMW	2.5-3.2	2800 CS	Coupe	Heckantrieb	Benzin	125	170	Jan 1969	Apr 1971	2024-03-01	266
BMW	2.5-3.2	3.0 CS	Coupe	Heckantrieb	Benzin	132	180	May 1971	Mar 1976	2024-03-01	267
BMW	2.5-3.2	3.0 CSI	Coupe	Heckantrieb	Benzin	147	200	Jul 1971	Mar 1976	2024-03-01	268
VW	Passat b7	1.8 TSI	Stufenheck	Frontantrieb	Benzin	118	160	Aug 2010	Dec 2014	2024-03-01	269
BMW	6	628 CSI	Coupe	Heckantrieb	Benzin	135	184	Sep 1979	Aug 1987	2024-03-01	270
BMW	6	630 CS	Coupe	Heckantrieb	Benzin	136	185	Apr 1976	Aug 1979	2024-03-01	271
BMW	6	633 CSI	Coupe	Heckantrieb	Benzin	147	200	Oct 1975	Dec 1981	2024-03-01	272
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	160	218	Jun 1978	Apr 1982	2024-03-01	273
BMW	6	M 635 CSI	Coupe	Heckantrieb	Benzin	210	286	Apr 1984	Dec 1988	2024-03-01	274
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	155	211	Jul 1987	Apr 1989	2024-03-01	275
VW	Passat b7	2.0 TSI	Stufenheck	Frontantrieb	Benzin	155	210	Nov 2010	Dec 2014	2024-03-01	276
BMW	7	728	Stufenheck	Heckantrieb	Benzin	125	170	May 1977	Aug 1979	2024-03-01	277
BMW	7	728 I	Stufenheck	Heckantrieb	Benzin	135	184	Sep 1977	Aug 1986	2024-03-01	278
BMW	7	730	Stufenheck	Heckantrieb	Benzin	135	184	May 1977	Aug 1979	2024-03-01	279
BMW	7	733 I	Stufenheck	Heckantrieb	Benzin	145	197	May 1977	Aug 1986	2024-03-01	280
BMW	7	745 I	Stufenheck	Heckantrieb	Benzin	185	252	Apr 1980	Apr 1983	2024-03-01	281
BMW	7	735 I	Stufenheck	Heckantrieb	Benzin	136	185	May 1984	Sep 1986	2024-03-01	282
BMW	7	735 I	Stufenheck	Heckantrieb	Benzin	160	218	Sep 1982	Sep 1986	2024-03-01	283
BMW	7	745 I	Stufenheck	Heckantrieb	Benzin	185	252	May 1983	Aug 1986	2024-03-01	284
BMW	7	730 I, IL	Stufenheck	Heckantrieb	Benzin	145	197	Mar 1985	Jan 1989	2024-03-01	285
BMW	7	730 I, IL	Stufenheck	Heckantrieb	Benzin	138	188	Mar 1987	Mar 1994	2024-03-01	286
BMW	7	730 I, IL V8	Stufenheck	Heckantrieb	Benzin	160	218	Apr 1992	Sep 1994	2024-03-01	287
BMW	7	735 I, IL	Stufenheck	Heckantrieb	Benzin	155	211	Jun 1986	Jul 1992	2024-03-01	288
BMW	7	735 I, IL	Stufenheck	Heckantrieb	Benzin	162	220	Jul 1986	Jan 1989	2024-03-01	289
BMW	7	740 I, IL V8	Stufenheck	Heckantrieb	Benzin	210	286	May 1992	Mar 1994	2024-03-01	290
BMW	7	750 I, IL V12	Stufenheck	Heckantrieb	Benzin	220	300	Sep 1987	Sep 1994	2024-03-01	291
BMW	8	850 I, CI	Coupe	Heckantrieb	Benzin	220	300	Jan 1990	Aug 1994	2024-03-01	292
VW	Passat b7	1.6 TDI	Stufenheck	Frontantrieb	Diesel	77	105	Aug 2010	Dec 2014	2024-03-01	293
VW	Passat b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Aug 2010	Dec 2014	2024-03-01	294
VW	Passat b7	2.0 TDI 4motion	Stufenheck	Allrad	Diesel	103	140	Aug 2010	Dec 2014	2024-03-01	295
VW	Passat b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	125	170	Aug 2010	Dec 2014	2024-03-01	296
BMW	Z1 roadster	2.5	Cabriolet	Heckantrieb	Benzin	125	170	Jun 1988	Jun 1991	2024-03-01	297
BMW	3	318 I	Cabriolet	Heckantrieb	Benzin	83	113	Sep 1990	Oct 1993	2024-03-01	298
BMW	3	320 I	Cabriolet	Heckantrieb	Benzin	95	129	May 1986	Nov 1993	2024-03-01	299
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	125	170	Aug 1987	Nov 1993	2024-03-01	300
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	126	171	Dec 1985	Dec 1987	2024-03-01	301
BMW	3	320 I	Cabriolet	Heckantrieb	Benzin	110	150	Dec 1993	Nov 1999	2024-03-01	302
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	141	192	Mar 1993	Aug 1995	2024-03-01	303
Mercedes-benz	Ponton	180 D	Stufenheck	Heckantrieb	Diesel	32	44	Jan 1953	Jul 1959	2024-03-01	304
Mercedes-benz	Ponton	180	Stufenheck	Heckantrieb	Benzin	48	65	Jul 1953	Dec 1962	2024-03-01	305
Mercedes-benz	Ponton	220	Stufenheck	Heckantrieb	Benzin	63	86	Jan 1954	Dec 1956	2024-03-01	306
Mercedes-benz	Ponton	220 S	Stufenheck	Heckantrieb	Benzin	78	106	Jan 1956	Dec 1959	2024-03-01	307
Mercedes-benz	Ponton	220 SE	Stufenheck	Heckantrieb	Benzin	88	120	Jan 1958	Aug 1959	2024-03-01	308
Mercedes-benz	190	E 1.8	Stufenheck	Heckantrieb	Benzin	80	109	Apr 1990	Aug 1993	2024-03-01	309
Mercedes-benz	190	2	Stufenheck	Heckantrieb	Benzin	66	90	Oct 1982	Oct 1984	2024-03-01	310
Mercedes-benz	190	E 2.0	Stufenheck	Heckantrieb	Benzin	83	113	Feb 1985	Dec 1986	2024-03-01	311
Mercedes-benz	190	E 2.0	Stufenheck	Heckantrieb	Benzin	85	116	Feb 1985	Dec 1986	2024-03-01	312
Mercedes-benz	190	2	Stufenheck	Heckantrieb	Benzin	75	102	Jan 1986	May 1990	2024-03-01	313
VW	Passat b7	2.0 TDI 4motion	Stufenheck	Allrad	Diesel	125	170	Aug 2010	Jan 2013	2024-03-01	314
VW	Passat b7	1.4 TSI Ecofuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	110	150	Aug 2010	Dec 2014	2024-03-01	315
Mercedes-benz	190	2	Stufenheck	Heckantrieb	Benzin	77	105	Aug 1983	May 1990	2024-03-01	316
VW	Passat b7 variant	1.4 TSI	Kombi	Frontantrieb	Benzin	90	122	Aug 2010	Dec 2014	2024-03-01	317
Mercedes-benz	190	E 2.0	Stufenheck	Heckantrieb	Benzin	87	118	Jan 1985	Aug 1993	2024-03-01	318
Mercedes-benz	190	E 2.0	Stufenheck	Heckantrieb	Benzin	90	122	Oct 1982	Jun 1993	2024-03-01	319
Ford	Fiesta i	0.9	Schrägheck	Frontantrieb	Benzin	29	40	May 1976	Aug 1983	2024-03-01	320


--- Round 1 / checkpoint 续跑 ---
## 更新点

* 已按物理外廓聚类完成 BMW E28、E34、E3、E9、E23、E32、E31、Z1，以及部分 E24、E30、E36 的映射；发动机、燃料和功率差异均直接复用尺寸组。
* E28 的 `535 I, M 535 I` 已拆分为标准 535i 与 M535i 两个外廓；E34 的普通 Sedan、525iX、M5、普通 Touring、525iX Touring 分别建组。相关来源明确给出了不含后视镜宽度。([汽车目录][1])
* E32 输入中的 `I, IL` 已全部拆分为 SWB/LWB；750i 的短轴 V12 低车身单独建组，长轴车型复用已确认的 LWB 外廓。([汽车目录][2])
* Passat B7 Sedan 的本批发动机版本已闭合到 `4769×1820×1470`；Variant 采用 Volkswagen 官方档案的 `4771×1820×1508`，厂内代码为 `3C`。([汽车数据网][3])
* Mercedes-Benz W201 当前只落盘生产阶段边界明确的 Ktype；跨越多次车身尺寸变化的 Ktype 暂不强行绑定。([汽车目录][4])

## 当前批次进度

* 已覆盖输入 Ktype：82/100
* READY 映射：91 行
* PENDING 输入 Ktype：18/100
* 已确认尺寸组：24
* 待处理 Ktype：`220、222、236、270、274、275、299、301、304–308、310、313、316、318、319`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
221	221	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
223	223	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
224	224	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
225	225	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
226	226	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
227	227	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
228	228	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
229	229	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
230	230	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
231	231	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
232	232	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
233_535i	233	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH	535i标准外廓。	READY
233_m535i	233	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-M535I-01	HIGH	M535i运动外廓。	READY
234_535i	234	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH	535i标准外廓。	READY
234_m535i	234	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-M535I-01	HIGH	M535i运动外廓。	READY
235	235	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
237	237	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
238	238	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
239	239	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
240	240	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
241	241	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
242	242	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-IX-01	HIGH	525iX增高外廓。	READY
243	243	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
244	244	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
245	245	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
246	246	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
247	247	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-M5-01	HIGH	M5低车身外廓。	READY
249	249	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-M5-01	HIGH	M5低车身外廓。	READY
250	250	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
251	251	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
252	252	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
253	253	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-IX-01	HIGH	525iX Touring增高外廓。	READY
254	254	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
255	255	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
256	256	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
257	257	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
258	258	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
259	259	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
260	260	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
261	261	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
262	262	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
263	263	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
264	264	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
265	265	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
266	266	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
267	267	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
268	268	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
269	269	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
271	271	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
272	272	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
273	273	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
276	276	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
277	277	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
278	278	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
279	279	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
280	280	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
281	281	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
282	282	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
283	283	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
284	284	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
285_swb	285	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
285_lwb	285	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
286_swb	286	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
286_lwb	286	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
287_swb	287	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
287_lwb	287	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
288_swb	288	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
288_lwb	288	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
289_swb	289	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
289_lwb	289	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
290_swb	290	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
290_lwb	290	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
291_swb	291	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-V12-01	HIGH	750i短轴V12低车身外廓。	READY
291_lwb	291	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	750iL长轴外廓。	READY
292	292	Coupe	BMW 8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850-01	HIGH		READY
293	293	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
294	294	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
295	295	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
296	296	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
297	297	Convertible	BMW Z1	E30Z	2	EU-BMW-Z1-ROADSTER-01	HIGH		READY
298	298	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH		READY
300	300	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH		READY
302	302	Convertible	BMW 3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH		READY
303	303	Convertible	BMW 3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH		READY
309	309	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	第二阶段车身外廓。	READY
311	311	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	第一阶段车身外廓。	READY
312	312	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	第一阶段车身外廓。	READY
314	314	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
315	315	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
317	317	Wagon	Volkswagen Passat B7	3C	5	EU-VW-PASSAT-B7-WAGON-01	HIGH		READY
320	320	Hatchback	Ford Fiesta Mk1		3	EU-FORD-FIESTA-MK1-HATCHBACK-3D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-E28-SEDAN-01	4620	1700	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1448555/bmw_520i_a.html
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/263360/bmw_m_535i_a.html
EU-BMW-5-E34-SEDAN-01	4720	1751	1412	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/58550/bmw_520i.html
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/268475/bmw_525ix_automatic_cat.html
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/268775/bmw_m5.html
EU-BMW-5-E34-WAGON-01	4720	1751	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/268190/bmw_525i_touring_cat.html
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/268220/bmw_525ix_touring_cat.html
EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	4700	1750	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/77690/bmw_3_0_s.html
EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	4800	1750	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/77735/bmw_3_0_l.html
EU-BMW-E9-COUPE-01	4660	1670	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/78335/bmw_3_0_cs.html
EU-VW-PASSAT-B7-SEDAN-01	4769	1820	1470	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b7-1.8-tsi-160hp-16821
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/171335/bmw_635_csi.html
EU-BMW-7-E23-SEDAN-01	4860	1800	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/264500/bmw_735i_a.html
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267380/bmw_735i_automatic.html
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267665/bmw_735il_automatic.html
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267455/bmw_750i.html
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/269090/bmw_850i_automatic.html
EU-BMW-Z1-ROADSTER-01	3921	1690	1277	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267290/bmw_z1.html
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/266105/bmw_325i_cabrio.html
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/270170/bmw_320i_cabrio.html
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	4448	1690	1375	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/1478765/mercedes-benz_190_e_2_0_5-speed.html
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	4420	1678	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1477265/mercedes-benz_190_e_5-speed_ece-version.html
EU-VW-PASSAT-B7-WAGON-01	4771	1820	1508	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-FORD-FIESTA-MK1-HATCHBACK-3D-01	3565	1567	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/922595/ford_fiesta_1_1_l.html
```

## 下一步优先处理

1. 优先闭合 Alfa Romeo 33 4X4 的早期与 1986 后期外廓。
2. 确认 E24 Ktype `270、274、275` 是否跨越 1987 年保险杠或车身长度变化，并按已确认分支派生。
3. 闭合 E30 Cabriolet Ktype `299、301` 的早期 1380 mm 与后期 1370 mm 高度边界。
4. 批量处理 Mercedes-Benz Ponton 的 W120/W180 长度阶段，以及跨阶段 W201 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/1448555/bmw_520i_a.html "https://www.automobile-catalog.com/car/1985/1448555/bmw_520i_a.html"
[2]: https://www.automobile-catalog.com/car/1989/267380/bmw_735i_automatic.html?utm_source=chatgpt.com "1989 BMW 735i automatic (aut. 4) (model up to mid-year ..."
[3]: https://www.auto-data.net/en/volkswagen-passat-b7-2.0-tsi-211hp-16823?utm_source=chatgpt.com "Volkswagen Passat (B7) 2.0 TSI (211 Hp) /Sedan 2010"
[4]: https://www.automobile-catalog.com/car/1986/1477265/mercedes-benz_190_e_5-speed_ece-version.html?utm_source=chatgpt.com "1986 Mercedes-Benz 190 E 5-speed (ECE-Version) (man. 5)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 已闭合 Alfa Romeo 33 4X4 的早期与改款后外廓，三个 Ktype 分别关联两个稳定尺寸组。([汽车目录][1])
* BMW E24 已按 1987 年中期前后长度变化拆分；M635 CSi 同时保留其独立低车身高度。E30 Cabriolet 已按 1987 年 9 月前后的高度变化完成派生映射。([汽车目录][2])
* Mercedes-Benz Ponton 已按 W120、W180、W128 的实际生产型和长度阶段闭合；相同外廓复用尺寸组。([marsClassic][3])
* Mercedes-Benz W201 已使用早期、第一阶段及 1988 年 9 月后改款三个现有或新建尺寸组，跨期 Ktype 已全部派生。([汽车目录][4])
* 已完成轻量机械检查：固定列数、`id` 和 `DIMENSION_GROUP_ID` 唯一、100 个输入 Ktype 全覆盖、映射外键闭合、所有三维及来源非空。

## 当前批次进度

* 输入 Ktype：100/100
* READY 映射：124
* PENDING：0
* DIMENSION_GROUP：36
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
220	220	Hatchback	Alfa Romeo 33 Tipo 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-PREFL-01	HIGH	早期4×4外廓。	READY
221	221	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
222	222	Hatchback	Alfa Romeo 33 Tipo 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-PREFL-01	HIGH	早期4×4外廓。	READY
223	223	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
224	224	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
225	225	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
226	226	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
227	227	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
228	228	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
229	229	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
230	230	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
231	231	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
232	232	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
233_535i	233	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH	535i标准外廓。	READY
233_m535i	233	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-M535I-01	HIGH	M535i运动外廓。	READY
234_535i	234	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH	535i标准外廓。	READY
234_m535i	234	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-M535I-01	HIGH	M535i运动外廓。	READY
235	235	Sedan	BMW 5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
236	236	Hatchback	Alfa Romeo 33 Tipo 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-FACELIFT-01	HIGH	改款后增高外廓。	READY
237	237	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
238	238	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
239	239	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
240	240	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
241	241	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
242	242	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-IX-01	HIGH	525iX增高外廓。	READY
243	243	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
244	244	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
245	245	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
246	246	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
247	247	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-M5-01	HIGH	M5低车身外廓。	READY
249	249	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-M5-01	HIGH	M5低车身外廓。	READY
250	250	Sedan	BMW 5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
251	251	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
252	252	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
253	253	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-IX-01	HIGH	525iX Touring增高外廓。	READY
254	254	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
255	255	Wagon	BMW 5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
256	256	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
257	257	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
258	258	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
259	259	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
260	260	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
261	261	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
262	262	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	HIGH		READY
263	263	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
264	264	Sedan	BMW New Six E3	E3	4	EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	HIGH	L/LI长轴外廓。	READY
265	265	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
266	266	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
267	267	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
268	268	Coupe	BMW E9	E9	2	EU-BMW-E9-COUPE-01	HIGH		READY
269	269	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
270_prefl	270	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH	1987年中期前标准外廓。	READY
270_facelift	270	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-LATE-01	HIGH	1987年中期后加长外廓。	READY
271	271	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
272	272	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
273	273	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH		READY
274_prefl	274	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-M635I-EARLY-01	HIGH	M635 CSi早期低车身外廓。	READY
274_facelift	274	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-M635I-LATE-01	HIGH	M635 CSi后期加长外廓。	READY
275	275	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-LATE-01	HIGH	1987年中期后标准外廓。	READY
276	276	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
277	277	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
278	278	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
279	279	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
280	280	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
281	281	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
282	282	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
283	283	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
284	284	Sedan	BMW 7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
285_swb	285	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
285_lwb	285	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
286_swb	286	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
286_lwb	286	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
287_swb	287	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
287_lwb	287	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
288_swb	288	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
288_lwb	288	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
289_swb	289	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
289_lwb	289	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
290_swb	290	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-01	HIGH	i短轴外廓。	READY
290_lwb	290	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	iL长轴外廓。	READY
291_swb	291	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-SWB-V12-01	HIGH	750i短轴V12低车身外廓。	READY
291_lwb	291	Sedan	BMW 7 Series E32	E32	4	EU-BMW-7-E32-SEDAN-LWB-01	HIGH	750iL长轴外廓。	READY
292	292	Coupe	BMW 8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850-01	HIGH		READY
293	293	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
294	294	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
295	295	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
296	296	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
297	297	Convertible	BMW Z1	E30Z	2	EU-BMW-Z1-ROADSTER-01	HIGH		READY
298	298	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH		READY
299_prefl	299	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-PREFL-01	HIGH	1987年9月前较高外廓。	READY
299_facelift	299	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH	1987年9月后较低外廓。	READY
300_prefl	300	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-PREFL-01	HIGH	1987年9月前较高外廓。	READY
300_facelift	300	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH	1987年9月后较低外廓。	READY
301_prefl	301	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-PREFL-01	HIGH	1987年9月前较高外廓。	READY
301_facelift	301	Convertible	BMW 3 Series E30	E30	2	EU-BMW-3-E30-CONVERTIBLE-01	HIGH	1987年9月后较低外廓。	READY
302	302	Convertible	BMW 3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH		READY
303	303	Convertible	BMW 3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH		READY
304	304	Sedan	Mercedes-Benz Ponton	W120 D I	4	EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4460-01	HIGH	180 D早期W120外廓。	READY
305_w120bi	305	Sedan	Mercedes-Benz Ponton	W120 B I	4	EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4460-01	HIGH	180第一生产型。	READY
305_w120bii	305	Sedan	Mercedes-Benz Ponton	W120 B II	4	EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4485-01	HIGH	180 a加长外廓。	READY
305_w120biii	305	Sedan	Mercedes-Benz Ponton	W120 B III	4	EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4500-01	HIGH	180 b外廓。	READY
305_w120biv	305	Sedan	Mercedes-Benz Ponton	W120 B IV	4	EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4500-01	HIGH	180 c与180 b共用外廓。	READY
306	306	Sedan	Mercedes-Benz Ponton	W180 I	4	EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4715-01	HIGH	220 a六缸早期外廓。	READY
307_preaug57	307	Sedan	Mercedes-Benz Ponton	W180 II	4	EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4715-01	HIGH	220 S至1957年8月前外廓。	READY
307_postaug57	307	Sedan	Mercedes-Benz Ponton	W180 II	4	EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4750-01	HIGH	220 S自1957年8月起加长外廓。	READY
308	308	Sedan	Mercedes-Benz Ponton	W128	4	EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4750-01	HIGH	220 SE后期六缸外廓。	READY
309	309	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	第二阶段车身外廓。	READY
310	310	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EARLY-01	HIGH	1982–1984早期外廓。	READY
311	311	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	第一阶段车身外廓。	READY
312	312	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	第一阶段车身外廓。	READY
313_prefl	313	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	1985年至1988年8月外廓。	READY
313_facelift	313	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	1988年9月后改款外廓。	READY
314	314	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
315	315	Sedan	Volkswagen Passat B7	3C	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH		READY
316_early	316	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EARLY-01	HIGH	1982–1984早期外廓。	READY
316_prefl	316	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	1985年至1988年8月外廓。	READY
316_facelift	316	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	1988年9月后改款外廓。	READY
317	317	Wagon	Volkswagen Passat B7	3C	5	EU-VW-PASSAT-B7-WAGON-01	HIGH		READY
318_prefl	318	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	1985年至1988年8月外廓。	READY
318_facelift	318	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	1988年9月后改款外廓。	READY
319_early	319	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EARLY-01	HIGH	1982–1984早期外廓。	READY
319_prefl	319	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	HIGH	1985年至1988年8月外廓。	READY
319_facelift	319	Sedan	Mercedes-Benz 190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	HIGH	1988年9月后改款外廓。	READY
320	320	Hatchback	Ford Fiesta Mk1		3	EU-FORD-FIESTA-MK1-HATCHBACK-3D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_201-300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-PREFL-01	4015	1612	1325	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/214790/alfa_romeo_33_1_5_4x4.html
EU-BMW-5-E28-SEDAN-01	4620	1700	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1448555/bmw_520i_a.html
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/263360/bmw_m_535i_a.html
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-FACELIFT-01	4015	1612	1345	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/215045/alfa_romeo_33_1_5_4x4.html
EU-BMW-5-E34-SEDAN-01	4720	1751	1412	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/58550/bmw_520i.html
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/268475/bmw_525ix_automatic_cat.html
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/268775/bmw_m5.html
EU-BMW-5-E34-WAGON-01	4720	1751	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/268190/bmw_525i_touring_cat.html
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/268220/bmw_525ix_touring_cat.html
EU-BMW-NEW-SIX-E3-SEDAN-SWB-01	4700	1750	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/77690/bmw_3_0_s.html
EU-BMW-NEW-SIX-E3-SEDAN-LWB-01	4800	1750	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/77735/bmw_3_0_l.html
EU-BMW-E9-COUPE-01	4660	1670	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/78335/bmw_3_0_cs.html
EU-VW-PASSAT-B7-SEDAN-01	4769	1820	1470	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b7-1.8-tsi-160hp-16821
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/171335/bmw_635_csi.html
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/264185/bmw_635_csi.html
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/50165/bmw_m_635_csi.html
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/264245/bmw_m_635_csi.html
EU-BMW-7-E23-SEDAN-01	4860	1800	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/264500/bmw_735i_a.html
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267380/bmw_735i_automatic.html
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267665/bmw_735il_automatic.html
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267455/bmw_750i.html
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/269090/bmw_850i_automatic.html
EU-BMW-Z1-ROADSTER-01	3921	1690	1277	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/267290/bmw_z1.html
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/266105/bmw_325i_cabrio.html
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/53555/bmw_325i_cabrio.html
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/270170/bmw_320i_cabrio.html
EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4460-01	4460	1740	1560	Mercedes-Benz Public Archive — 180 D	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/180-D.xhtml?oid=5137
EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4485-01	4485	1740	1560	Mercedes-Benz Public Archive — 180 a	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/180-a.xhtml?oid=5144
EU-MERCEDES-BENZ-PONTON-W120-SEDAN-4500-01	4500	1740	1560	Mercedes-Benz Public Archive — 180 b;Mercedes-Benz Public Archive — 180 c	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/180-b.xhtml?oid=5228;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/180-c.xhtml?oid=5226
EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4715-01	4715	1740	1560	Mercedes-Benz Public Archive — 220 a;Mercedes-Benz Public Archive — 220 S	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-a.xhtml?oid=4886;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-S.xhtml?oid=4884
EU-MERCEDES-BENZ-PONTON-6CYL-SEDAN-4750-01	4750	1740	1560	Mercedes-Benz Public Archive — 220 S;Mercedes-Benz Public Archive — 220 SE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-S.xhtml?oid=4884;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-SE.xhtml?oid=4887
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	4448	1690	1375	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/1478765/mercedes-benz_190_e_2_0_5-speed.html
EU-MERCEDES-BENZ-190-W201-SEDAN-EARLY-01	4420	1678	1383	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/28025/mercedes-benz_190_automatic.html
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	4420	1678	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1477265/mercedes-benz_190_e_5-speed_ece-version.html
EU-VW-PASSAT-B7-WAGON-01	4771	1820	1508	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-FORD-FIESTA-MK1-HATCHBACK-3D-01	3565	1567	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/922595/ford_fiesta_1_1_l.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_201-300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1984/214790/alfa_romeo_33_1_5_4x4.html?utm_source=chatgpt.com "1984 Alfa Romeo 33 1.5 4x4 Specs Review (62.5 kW / 85 PS / 84 hp) (up to mid-year 1984 for Europe )"
[2]: https://www.automobile-catalog.com/car/1986/263975/bmw_628_csi_5-speed.html?utm_source=chatgpt.com "1986 BMW 628 CSi 5-speed Specs Review (135 kW / 184 PS / 181 hp) (for Europe )"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/180-D.xhtml?oid=5137 "180 D"
[4]: https://www.automobile-catalog.com/car/1982/28025/mercedes-benz_190_automatic.html?utm_source=chatgpt.com "1982 Mercedes-Benz 190 automatic Specs Review (66 kW ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_201-300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_201-300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（370 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（99 行）
