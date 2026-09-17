# 任务：all 第 2801-2900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0029__1229325b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2801-2900 行

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
- 如果当前批次得到的三维与累计表中同名 `DIMENSION_GROUP_ID` 不同，禁止覆盖已有组；应使用同系列下一个可用序号创建新尺寸组，并将当前批次所有相关 Ktype 映射同步指向新组。
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

自动化在接受 COMPLETE 后会从同一回复的两张内嵌 TSV 生成本批本地文件。分批模式固定使用首批文件名维护两张累计总表：

```text
all_1-100_ktype_dimension_mapping_final.tsv
all_1-100_dimension_groups_final.tsv
```

第一批成功时创建这两张总表；此后每个批次成功都立即追加。累计合并以 `id` 和 `DIMENSION_GROUP_ID` 去重，可安全恢复或重复处理；尺寸组出现三维冲突时必须停止，不得静默覆盖首次确认的尺寸事实。首批文件名从第二批开始代表累计总表，不再是冻结的第一批快照。

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
all 第 2801-2900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AIXAM-CITY-2016-HATCHBACK-01	2758	1500	1470
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-RENAULT-GRAND-SCENIC-IV-MPV-01	4635	1866	1660
EU-RENAULT-SCENIC-IV-MPV-01	4406	1866	1653
EU-RUF-CTR-ANNIVERSARY-COUPE-01	4207	1819	1265
EU-SEAT-IBIZA-IV-ST-FACELIFT-WAGON-01	4236	1693	1445
EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	3992	1732	1452
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Aixam	Coupe	0.5	Coupe	Frontantrieb	Diesel	6	8	Oct 2016	-	2024-03-01	132961
RUF	Turbo florio	3.8	Targa	Heckantrieb	Benzin	474	644	Mar 2015	-	2024-03-01	132962
Aixam	Crossline	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Oct 2016	-	2024-03-01	132963
RUF	Ctr	3.8	Coupe	Heckantrieb	Benzin	515	700	Mar 2007	Dec 2009	2024-03-01	132967
Aixam	City	Electric	Schrägheck	Frontantrieb	Elektro	6	8	Mar 2018	-	2024-03-01	132970
Gumpert	Apollo	4.2	Coupe	Heckantrieb	Benzin	478	650	Aug 2009	Dec 2013	2024-03-01	132971
Mitsubishi	Lancer v	1.8 GTI	Stufenheck	Frontantrieb	Benzin	100	136	Jul 1991	Jul 1993	2024-03-01	132974
Aixam	Coupe	Electric	Coupe	Frontantrieb	Elektro	6	8	Mar 2018	-	2024-03-01	132976
Rolls-royce	Silver spirit mk i	6.75	Stufenheck	Heckantrieb	Benzin	191	260	Oct 1980	Jun 1984	2024-03-01	132978
Gumpert	Apollo	4.2	Coupe	Heckantrieb	Benzin	515	700	Aug 2009	Dec 2013	2024-03-01	132983
Apollo	Apollo n	4.2	Coupe	Heckantrieb	Benzin	515	700	Mar 2016	-	2024-03-01	132987
Apollo	Arrow	4	Coupe	Heckantrieb	Benzin	735	999	Mar 2016	-	2024-03-01	132989
Peugeot	Partner	1.5 Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Sep 2018	-	2024-03-01	132995
Peugeot	Partner	1.6 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2018	-	2024-03-01	132997
Peugeot	Partner	1.6 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	73	99	Sep 2018	-	2024-03-01	132998
Audi	A8 d3	3.0 Quattro	Stufenheck	Allrad	Benzin	162	220	Jul 2003	May 2005	2024-03-01	133001
Ford USA	Edge	2.0 Ecoblue AWD	SUV	Allrad	Diesel	140	190	Aug 2018	-	2024-03-01	133002
Ford USA	Edge	2.0 Ecoblue AWD	SUV	Allrad	Diesel	175	238	Aug 2018	-	2024-03-01	133004
Porsche	Boxster	2.9	Cabriolet	Heckantrieb	Benzin	155	211	Feb 2009	Mar 2012	2024-03-01	133007
Porsche	Cayman	2.9	Coupe	Heckantrieb	Benzin	155	211	Feb 2009	Jun 2013	2024-03-01	133008
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	155	211	Apr 2012	May 2016	2024-03-01	133009
Porsche	Cayman	2.7	Coupe	Heckantrieb	Benzin	155	211	Mar 2013	May 2016	2024-03-01	133011
Apollo	Ie	6.3	Coupe	Heckantrieb	Benzin	582	791	Oct 2017	-	2024-03-01	133013
Ford	Kuga ii	1.5 Ecoboost 4X4	SUV	Allrad	Benzin	129	176	Aug 2018	Jun 2019	2024-03-01	133018
Mazda	121 iii	1.8 TD	Schrägheck	Frontantrieb	Diesel	55	75	Feb 2000	Oct 2002	2024-03-01	133019
Lancia	Zeta	2.0 JTD 16V	Großraumlimousine	Frontantrieb	Diesel	81	110	Apr 2001	Oct 2003	2024-03-01	133025
Lancia	Voyager	3.6 V6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	208	283	Jan 2014	Dec 2014	2024-03-01	133029
Audi	Q3	35 Tfsi	SUV	Frontantrieb	Benzin	110	150	Aug 2018	-	2024-03-01	133035
Audi	Q3	35 TDI	SUV	Frontantrieb	Diesel	110	150	Sep 2018	-	2024-03-01	133038
Audi	Q3	35 TDI Quattro	SUV	Allrad	Diesel	110	150	Sep 2018	-	2024-03-01	133039
Audi	Q3	40 TDI Quattro	SUV	Allrad	Diesel	140	190	Oct 2018	-	2024-03-01	133041
Audi	Q3	45 Tfsi Quattro	SUV	Allrad	Benzin	169	230	Jul 2018	-	2024-03-01	133042
Nissan	Juke	1.6	SUV	Frontantrieb	Benzin	83	113	Jul 2018	Dec 2019	2024-03-01	133043
Mercedes-benz	C-Klasse	C 250	Kombi	Heckantrieb	Benzin	150	204	Feb 2008	Dec 2012	2024-03-01	133044
RUF	Rtr	3.8	Coupe	Heckantrieb	Benzin	590	802	Jan 2015	-	2024-03-01	133056
Alfa Romeo	147	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	88	120	Mar 2001	Dec 2009	2024-03-01	133059
Alfa Romeo	147	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	77	105	Jan 2009	Mar 2010	2024-03-01	133063
RUF	Turbo r	3.6	Coupe	Allrad	Benzin	360	490	Jan 1998	-	2024-03-01	133064
RUF	Rct	3.6 EVO	Coupe	Heckantrieb	Benzin	313	425	Jan 1994	Jan 2016	2024-03-01	133067
Alfa Romeo	Giulietta	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Apr 2011	Feb 2016	2024-03-01	133069
Volvo	V60 ii	D3 AWD	Kombi	Allrad	Diesel	110	150	Sep 2018	Dec 2021	2024-05-01	133070
RUF	Ultimate	3.6	Coupe	Heckantrieb	Benzin	434	590	Feb 2016	-	2024-03-01	133071
Seat	Ibiza iv	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	May 2009	May 2015	2024-03-01	133072
Seat	Ibiza iv	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	70	Mar 2008	May 2011	2024-03-01	133073
Volvo	V60 ii	D4 AWD	Kombi	Allrad	Diesel	140	190	Sep 2018	Dec 2021	2024-05-01	133074
Seat	Ibiza iv	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	63	85	Mar 2008	May 2011	2024-03-01	133075
Seat	Ibiza iv sc	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	63	85	Jul 2008	May 2011	2025-06-01	133076
Seat	Ibiza iv	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Apr 2008	May 2015	2024-03-01	133078
Seat	Cordoba	1.4	Kombi	Frontantrieb	Benzin	74	101	Feb 2000	Jul 2000	2024-03-01	133082
Seat	Cordoba	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	81	110	Aug 2000	Dec 2002	2024-03-01	133083
Alfa Romeo	Giulietta	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	125	170	Apr 2011	Dec 2020	2024-03-01	133085
Mitsubishi	Asx	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	86	117	Jun 2010	-	2024-03-01	133090
Alfa Romeo	Giulietta	2.0 Jtdm	Kasten/Schrägheck	Frontantrieb	Diesel	129	175	May 2015	Dec 2020	2024-03-01	133092
Mazda	Mx-5 iv	1.5	Cabriolet	Heckantrieb	Benzin	97	132	May 2018	-	2024-03-01	133097
Fiat	Doblo cargo	1.6 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Mar 2015	Dec 2023	2025-02-03	133098
RUF	Rgt mk i	3.6	Coupe	Heckantrieb	Benzin	283	385	Jan 2000	Dec 2003	2024-03-01	133099
RUF	Rgt mk i	3.6 RS	Coupe	Heckantrieb	Benzin	290	395	Jan 2004	Dec 2004	2024-03-01	133100
RUF	Rgt mk ii	3.8	Coupe	Heckantrieb	Benzin	332	451	Jan 2005	Dec 2009	2024-03-01	133101
RUF	Rgt mk ii	4.5	Coupe	Heckantrieb	Benzin	410	557	Jan 2010	Dec 2011	2024-03-01	133102
RUF	Rgt mk iii	4.5	Coupe	Heckantrieb	Benzin	405	551	Jan 2012	-	2024-03-01	133103
RUF	Rgt mk iii	4.2	Coupe	Heckantrieb	Benzin	386	525	Jan 2017	-	2024-03-01	133104
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	100	136	Dec 2017	Jan 2022	2025-06-01	133105
Hyundai	Tucson	1.6 Crdi	SUV	Frontantrieb	Diesel	85	116	Aug 2018	Sep 2020	2024-03-01	133106
Hyundai	Tucson	1.6 Crdi	SUV	Frontantrieb	Diesel	100	136	Aug 2018	Dec 2020	2024-03-01	133107
Hyundai	Tucson	1.6 Crdi Allrad	SUV	Allrad	Diesel	100	136	Aug 2018	Dec 2020	2024-03-01	133108
Daihatsu	Terios	1.5 LPG 4X4	Geländewagen geschlossen	Allrad	Benzin/Autogas (LPG)	77	105	Jun 2009	-	2024-03-01	133115
Hyundai	Santa fe iv	2.4 GDI AWD	SUV	Allrad	Benzin	136	185	Jul 2018	Jul 2020	2024-03-01	133116
Hyundai	Santa fe iv	2.0 Crdi	SUV	Frontantrieb	Diesel	110	150	Jul 2018	Jul 2020	2024-03-01	133117
Mazda	Mx-5 iv	2	Cabriolet	Heckantrieb	Benzin	135	184	May 2018	-	2024-03-01	133119
Mazda	Mx-5 rf	1.5	Targa	Heckantrieb	Benzin	97	132	May 2018	-	2024-03-01	133120
Mazda	Mx-5 rf	2	Targa	Heckantrieb	Benzin	135	184	May 2018	-	2024-03-01	133121
Skoda	Octavia	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Aug 2000	Mar 2010	2024-03-01	133122
Skoda	Octavia	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	50	68	Aug 2000	Dec 2003	2024-03-01	133123
KIA	Optima	2.0 T-gdi GT	Kombi	Frontantrieb	Benzin	175	238	Jan 2018	Dec 2019	2024-03-01	133124
Skoda	Fabia i praktik	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	74	101	Jan 2000	Dec 2007	2024-03-01	133125
KIA	Optima	1.6 T-gdi	Kombi	Frontantrieb	Benzin	132	179	Jan 2018	Dec 2019	2024-03-01	133126
KIA	Optima	1.6 Crdi	Kombi	Frontantrieb	Diesel	100	136	Jan 2018	Dec 2019	2024-03-01	133128
Skoda	Fabia i praktik	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	55	75	Aug 2004	Oct 2005	2024-03-01	133129
Skoda	Roomster	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	63	86	Mar 2010	May 2015	2024-03-01	133130
KIA	Stinger	2.0 T-gdi	Schrägheck	Heckantrieb	Benzin	180	245	Jul 2018	Dec 2023	2026-04-01	133131
KIA	Stinger	3.3 T-gdi 4WD	Schrägheck	Allrad	Benzin	269	366	Jul 2018	Dec 2023	2026-04-01	133132
Skoda	Roomster	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	77	105	Jun 2006	Jul 2010	2024-03-01	133133
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	120	163	Aug 2010	Oct 2016	2024-03-01	133134
Skoda	Fabia ii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	69	Jul 2007	Nov 2014	2024-03-01	133135
Skoda	Fabia ii combi	1.2 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	51	69	Oct 2007	Nov 2014	2024-03-01	133139
Mini	Mini	Cooper S	Coupe	Frontantrieb	Benzin	120	163	Jan 2014	Sep 2016	2026-04-01	133143
Mitsubishi	Outlander iii	2.0 Bifuel	SUV	Frontantrieb	Benzin/Autogas (LPG)	107	146	Oct 2012	Dec 2022	2025-06-01	133145
Mitsubishi	Lancer viii	2.0 EVO X	Stufenheck	Allrad	Benzin	296	402	Jun 2009	-	2024-03-01	133147
Skoda	Fabia ii	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	63	86	Jan 2007	Nov 2014	2024-03-01	133148
Renault	Scénic iv	1.3 TCE 160	Großraumlimousine	Frontantrieb	Benzin	117	159	Sep 2018	Jul 2022	2024-05-01	133155
Renault	Grand scénic iv	1.3 TCE 160	Großraumlimousine	Frontantrieb	Benzin	117	159	Sep 2018	Mar 2023	2024-05-01	133156
Renault	Scénic iv	1.7 Blue DCI 120	Großraumlimousine	Frontantrieb	Diesel	88	120	Aug 2018	Jul 2022	2024-05-01	133157
Fiat	Punto	1.2 Bipower	Schrägheck	Frontantrieb	Benzin/Ethanol	44	60	Aug 2001	May 2003	2024-03-01	133158
Renault	Grand scénic iv	1.7 Blue DCI 120	Großraumlimousine	Frontantrieb	Diesel	88	120	Aug 2018	Mar 2023	2024-05-01	133159
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	85	116	Oct 2001	Aug 2005	2024-03-01	133160
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	59	80	Oct 2001	Aug 2005	2024-03-01	133161
Renault	Scénic iv	1.7 Blue DCI 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Aug 2018	Jul 2022	2024-05-01	133162
Renault	Grand scénic iv	1.7 Blue DCI 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Aug 2018	Mar 2023	2024-05-01	133164
Skoda	Fabia ii combi	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	63	86	Oct 2007	Nov 2014	2024-03-01	133165
Alpina	Xd3	Biturbo Allrad	SUV	Allrad	Diesel	285	388	Jul 2018	Jun 2024	2026-06-01	133167


--- Round 1 / 首次发送 ---
## 更新点

* 复用 9 个跨批次既有尺寸组，完成 Aixam City、Ford Kuga II facelift、Volvo V60 II、Hyundai i30/Tucson/Santa Fe、KIA Stinger、Renault Scénic/Grand Scénic 共 18 个 Ktype 的映射。
* 首次闭合 12 个尺寸组，完成 Porsche 987.2/981、Audi Q3 F3、Nissan Juke F15 facelift、Alfa Romeo Giulietta 940、Mazda MX-5 ND/RF、KIA Optima Sportswagon 共 20 个 Ktype。
* Audi Q3、Nissan Juke 和 KIA Optima Sportswagon 使用厂商尺寸资料；Mazda MX-5 按官方手册中软顶/RF及标准轮径对应高度拆分。
* Porsche 981 使用官方技术规格并由规格数据库补齐公制不含后视镜宽度；Giulietta 使用官方车主手册尺寸。
* 本轮未修改任何已有 DIMENSION_GROUP 的三维事实。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：38
* PENDING Ktype：62
* 当前已引用尺寸组：21

  * 复用既有尺寸组：9
  * 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132970	132970	Hatchback	Sensation		3	EU-AIXAM-CITY-2016-HATCHBACK-01	HIGH		READY
133007	133007	Convertible	Boxster 987.2	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
133008	133008	Coupe	Cayman 987.2	987C	3	EU-PORSCHE-CAYMAN-9872-COUPE-01	HIGH		READY
133009	133009	Convertible	Boxster 981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-01	HIGH		READY
133011	133011	Coupe	Cayman 981	981C	3	EU-PORSCHE-CAYMAN-981-COUPE-01	HIGH		READY
133018	133018	SUV	Kuga II facelift	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
133035	133035	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133038	133038	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133039	133039	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133041	133041	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133042	133042	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133043	133043	SUV	Juke I facelift	F15	5	EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	HIGH		READY
133069	133069	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133070	133070	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
133074	133074	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
133085	133085	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133092	133092	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133097	133097	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-CONVERTIBLE-16IN-01	MEDIUM	欧洲标准16英寸轮径软顶外廓。	READY
133105	133105	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
133106	133106	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133107	133107	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133108	133108	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133116	133116	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133117	133117	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133119	133119	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-CONVERTIBLE-17IN-01	MEDIUM	欧洲标准17英寸轮径软顶外廓。	READY
133120	133120	Targa	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-RF-16IN-01	MEDIUM	欧洲标准16英寸轮径RF外廓。	READY
133121	133121	Targa	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-RF-17IN-01	MEDIUM	欧洲标准17英寸轮径RF外廓。	READY
133124	133124	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133126	133126	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133128	133128	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133131	133131	Liftback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
133132	133132	Liftback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
133155	133155	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133156	133156	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
133157	133157	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133159	133159	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
133162	133162	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133164	133164	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1292	Auto-Data	https://www.auto-data.net/en/porsche-boxster-987-facelift-2009-2.9-255hp-40880
EU-PORSCHE-CAYMAN-9872-COUPE-01	4347	1801	1304	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-facelift-2009-2.9-265hp-40905
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-01	4374	1801	1282	Porsche 2013 Boxster official technical specifications;Automobile-Catalog	https://newsroom.porsche.com/dam/jcr%3A4d1913a9-97f9-4ade-8bc4-fc2cc32caeb9/2013_Boxster_Technical_Specifications.pdf;https://www.automobile-catalog.com/car/2013/2871725/porsche_boxster.html
EU-PORSCHE-CAYMAN-981-COUPE-01	4380	1801	1294	Porsche 2014 Cayman official technical specifications;Automobile-Catalog	https://newsroom.porsche.com/dam/jcr%3A0036dadf-873b-46b8-86b2-841009f188af/2014_Cayman_Technical_Specifications.pdf;https://www.automobile-catalog.com/car/2014/2871785/porsche_cayman.html
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Audi Q3 official dimensions sheet (07/18)	https://www.audi.com/en/publications/dimensions/dimensions-q3-1413/download
EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	4135	1765	1565	Nissan JUKE official brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Files/Brochures/Models/Juke/JUK0139r02_Nissan_JUKE_Brochure%20PDF.pdf
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	4351	1798	1465	Alfa Romeo Giulietta official owner handbook	https://aftersales.fiat.com/eLumData/EN/83/191_GIULIETTA/83_191_GIULIETTA_604.38.862_EN_03_09.16_L_LG/83_191_GIULIETTA_604.38.862_EN_03_09.16_L_LG.pdf
EU-MAZDA-MX5-IV-ND-CONVERTIBLE-16IN-01	3915	1735	1225	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-MAZDA-MX5-IV-ND-CONVERTIBLE-17IN-01	3915	1735	1230	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-MAZDA-MX5-IV-ND-RF-16IN-01	3915	1735	1230	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-MAZDA-MX5-IV-ND-RF-17IN-01	3915	1735	1235	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470	Kia Optima Sportswagon official press kit	https://prod2-press.kia.com/eu/en/home/models/optima-sportswagon/optima-sportswagon.html
```

## 下一步优先处理

1. 集中闭合 Peugeot Partner K9 三个动力 Ktype，并确认 Van/乘用车及标准轴距、长轴距物理分支。
2. 批量处理 Aixam Coupe/Crossline，以及 Gumpert/Apollo/RUF 小众跑车集群。
3. 处理 Seat Ibiza/Cordoba、Skoda Fabia/Roomster/Octavia、Fiat Punto/Stilo/Doblò 等高复用车型组。
4. 再处理 Mitsubishi、Lancia、Audi A8、Ford Edge、Alpina XD3 等剩余独立车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新增 26 个 Ktype、36 条 READY 映射，首次创建 19 个尺寸组。
* Peugeot Partner III 按官方 L1/L2 短轴、长轴外廓拆分，宽度均采用不含后视镜口径。
* Ford Edge II facelift 两个动力 Ktype 共用官方确认的五门 SUV 外廓。
* Ibiza IV、Fabia II、Roomster I 中跨越改款且外廓长度变化的 Ktype 已拆成 `prefl`、`facelift` 派生行。([汽车目录档案][1])
* MINI R58 Cooper S 未复用已有普通 Cooper 尺寸组，单独创建 Cooper S 尺寸组；XD3 依据 285 kW/388 PS 锁定 G01 改款前外廓。([汽车档案][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射行：74
* PENDING Ktype：36
* 已确认并被引用尺寸组：40
* 本轮首次创建尺寸组：19
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132995_l1	132995	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132995_l2	132995	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
132997_l1	132997	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132997_l2	132997	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
132998_l1	132998	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132998_l2	132998	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
133002	133002	SUV	Edge II facelift	CD539	5	EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	HIGH		READY
133004	133004	SUV	Edge II facelift	CD539	5	EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	HIGH		READY
133072_prefl	133072	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133072_facelift	133072	Hatchback	Ibiza IV facelift	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133073	133073	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH		READY
133075	133075	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH		READY
133076	133076	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-SC-HATCHBACK-PREFL-01	HIGH	SC三门物理外廓。	READY
133078_prefl	133078	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133078_facelift	133078	Hatchback	Ibiza IV facelift	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133082	133082	Wagon	Córdoba I facelift	6K5	5	EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	HIGH	Vario旅行车外廓。	READY
133083	133083	Wagon	Córdoba I facelift	6K5	5	EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	HIGH	N1/Kasten用途不改变Vario外廓。	READY
133122	133122	Wagon	Octavia I facelift/Tour	1U5	5	EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	HIGH	N1/Kasten用途不改变Combi外廓。	READY
133123	133123	Wagon	Octavia I facelift/Tour	1U5	5	EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	HIGH	N1/Kasten用途不改变Combi外廓。	READY
133130	133130	MPV	Roomster I facelift	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH		READY
133133_prefl	133133	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133133_facelift	133133	MPV	Roomster I facelift	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH	Ktype跨2010改款拆分。	READY
133134	133134	Wagon	MINI Clubman I	R55	5	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	HIGH	Cooper S Clubman外廓。	READY
133135_prefl	133135	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133135_facelift	133135	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133139_prefl	133139	Wagon	Fabia II Combi	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133139_facelift	133139	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133143	133143	Coupe	MINI Coupé I	R58	2	EU-MINI-MINI-R58-COUPE-COOPER-S-01	HIGH	Cooper S专属外廓。	READY
133148_prefl	133148	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133148_facelift	133148	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133158	133158	Hatchback	Punto II	188	5	EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	HIGH	Bipower五门外廓。	READY
133160	133160	Wagon	Stilo I Multi Wagon	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH	N1/Kasten用途不改变Multi Wagon外廓。	READY
133161	133161	Wagon	Stilo I Multi Wagon	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH	N1/Kasten用途不改变Multi Wagon外廓。	READY
133165_prefl	133165	Wagon	Fabia II Combi	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133165_facelift	133165	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133167	133167	SUV	XD3 II	G01	5	EU-ALPINA-XD3-II-G01-SUV-PREFL-01	HIGH	285 kW/388 PS对应G01改款前外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	Peugeot LCV Catalogue 2020	https://kwt.peugeot.com/content/dam/peugeot/saudi_arabia/brochure/Peugeot_LCV_Catalogue_2020.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	Peugeot LCV Catalogue 2020	https://kwt.peugeot.com/content/dam/peugeot/saudi_arabia/brochure/Peugeot_LCV_Catalogue_2020.pdf
EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	4834	1928	1732	Ford Edge official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-edge.pdf
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	4052	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3094550/seat_ibiza_1_2_12v_70.html
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	4061	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3095600/seat_ibiza_1_2_tdi_cr_75.html
EU-SEAT-IBIZA-IV-6J1-SC-HATCHBACK-PREFL-01	4034	1693	1428	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3094670/seat_ibiza_sc_1_6_16v_105.html
EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	4163	1640	1433	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3070925/seat_cordoba_vario_1_9_tdi_110.html
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3135395/skoda_octavia_combi_1_9_tdi_90.html
EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	4214	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3143090/skoda_roomster_1_6_tdi_cr_90.html
EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	4205	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/3142835/skoda_roomster_1_4_tdi_pd_80.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1753625/mini_cooper_s_clubman.html
EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	3992	1642	1498	Škoda Drive Place	https://skoda.drive.place/fabia/ii/group_hatchback_5d/249719
EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	4000	1642	1498	Automoli	https://www.automoli.com/en/vehicles/skoda/fabia/fabia-ii-facelift-2010-4316/
EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	4239	1642	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/3140615/skoda_fabia_combi_1_4_tdi_80.html
EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	4247	1642	1498	Automoli	https://www.automoli.com/en/vehicles/skoda/fabia/fabia-ii-combi-facelift-2010-4315/
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384	Carfolio	https://www.carfolio.com/mini-cooper-s-coupe-247445
EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	3835	1660	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/723875/fiat_punto_5-porte_1_2_16v_elx.html
EU-FIAT-STILO-I-192-MULTIWAGON-01	4516	1756	1570	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/724925/fiat_stilo_multi_wagon_1_9_jtd_115_active.html
EU-ALPINA-XD3-II-G01-SUV-PREFL-01	4718	1897	1655	Auto-Data	https://www.auto-data.net/en/alpina-xd3-g01-generation-6138
```

## 5. 下一步优先处理

1. Aixam Coupe/Crossline 及电动、柴油共用外廓边界。
2. Gumpert Apollo、Apollo N/Arrow/IE 与 RUF 各 911 衍生跑车。
3. Mitsubishi Lancer、ASX、Outlander、Daihatsu Terios。
4. Audi A8 D3、Mercedes-Benz C-Klasse S204、Lancia Zeta/Voyager。
5. Fiat Doblò Cargo 多轴距、Alfa Romeo 147 多门数及剩余独立车型。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2017/05/Seat-Ibiza-2012-UK.pdf?utm_source=chatgpt.com "Seat-Ibiza-2012-UK.pdf"
[2]: https://www.carfolio.com/mini-cooper-s-coupe-247445?utm_source=chatgpt.com "2011 MINI Cooper S Coupé R58"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Lancia Voyager 3.6 V6 LPG 的 RT 代 MPV 外廓，官方资料确认三维为 5218 × 1998 × 1750 mm。([Stellantis Media][1])
* Alfa Romeo 147 的 120 PS Ktype 按改款前后及 3/5 门物理分支拆分；官方资料确认改款前为 4170 × 1729 × 1442 mm、改款后为 4223 × 1729 × 1442 mm。([Stellantis Media][2])
* Alfa Romeo 147 的 105 PS、2009–2010 Ktype 关联改款后五门尺寸组；2009 年官方车型范围仅保留五门车身，并同时包含 105 PS 与 120 PS 1.6 发动机。([Stellantis Media][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* READY 映射行：80
* PENDING Ktype：33
* 已确认并被引用尺寸组：45
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133029	133029	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-01	HIGH		READY
133059_3dr_prefl	133059	Hatchback	147 I pre-facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_5dr_prefl	133059	Hatchback	147 I pre-facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_3dr_facelift	133059	Hatchback	147 I facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_5dr_facelift	133059	Hatchback	147 I facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133063	133063	Hatchback	147 I facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	HIGH	2009年车型范围为五门车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-VOYAGER-RT-MPV-01	5218	1998	1750	Lancia Voyager official specifications	https://www.media.stellantis.com/uploads/fr/FR/2013/LANCIA/TARIFS/130201_FT_VOYAGER178.pdf
EU-ALFA-ROMEO-147-937-HATCHBACK-3D-PREFL-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-5D-PREFL-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-3D-FACELIFT-01	4223	1729	1442	Alfa Romeo new 147 range official specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	4223	1729	1442	Alfa Romeo new 147 range official specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
```

## 5. 下一步优先处理

1. Audi A8 D3、Mercedes-Benz C-Klasse S204、Mazda 121 III 与 Lancia Zeta。
2. Mitsubishi Lancer V、Lancer Evolution X、ASX、Outlander III。
3. Daihatsu Terios、Skoda Fabia I Praktik 与 Fiat Doblò Cargo 的轴距/车顶分支。
4. 最后集中闭合 Aixam Coupe/Crossline、Gumpert/Apollo 与 RUF 小众跑车。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/fr/FR/2013/LANCIA/TARIFS/130201_FT_VOYAGER178.pdf?utm_source=chatgpt.com "30075 LANCIA FICHE TARIFS VOYAGER.indd"
[2]: https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147?utm_source=chatgpt.com "La nuova gamma di Alfa 147 | Alfa Romeo | Stellantis Media"
[3]: https://www.media.stellantis.com/it-it/alfa-romeo/press/moving-la-nuova-serie-speciale-di-alfa-romeo-147?utm_source=chatgpt.com "“Moving”: la nuova Serie Speciale di Alfa Romeo 147 | Alfa Romeo | Stellantis Media"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合 Aixam Coupé、Crossline 柴油及电动 Ktype；同代 Coupé 柴油/电动复用同一外廓，Crossline 独立建组。官方手册确认均为两门车身，并分别给出完整三维。
* 闭合 Audi A8 D3、Mazda 121 III、Lancia Zeta、Rolls-Royce Silver Spirit Mk I、Daihatsu Terios II、Mitsubishi Lancer IV GTI 与 Evolution X。([汽车目录][1])
* Škoda Fabia I Praktik 按 2004 年长度变化拆分为两个物理分支；2004 年后的 1.4 TDI 直接关联后期尺寸组。
* 本轮新增 12 个 READY Ktype、13 条映射和 11 个尺寸组；未修改既有尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射行：93
* PENDING Ktype：21
* 已确认并被引用尺寸组：56
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132961	132961	Coupe	Sensation		2	EU-AIXAM-COUPE-SENSATION-COUPE-01	HIGH		READY
132963	132963	Hatchback	Sensation		2	EU-AIXAM-CROSSLINE-SENSATION-HATCHBACK-01	HIGH		READY
132974	132974	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-GTI-01	MEDIUM	输入代际写法与明确的1.8 GTI四门车型资料不一致。	READY
132976	132976	Coupe	Sensation		2	EU-AIXAM-COUPE-SENSATION-COUPE-01	MEDIUM	电动版与同代Coupé共用物理外廓。	READY
132978	132978	Sedan	Silver Spirit Mk I	SZ	4	EU-ROLLS-ROYCE-SILVER-SPIRIT-MK-I-SEDAN-01	HIGH		READY
133001	133001	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH		READY
133019	133019	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	MEDIUM	1.8 TD资料明确对应五门车身。	READY
133025	133025	MPV	Zeta I		5	EU-LANCIA-ZETA-I-MPV-01	MEDIUM	输入终止月晚于公开车型生产期，物理外廓对应Zeta量产车身。	READY
133115	133115	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH		READY
133125_pre04	133125	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-PRE04-01	MEDIUM	Ktype跨2004年外廓长度变更拆分。	READY
133125_post04	133125	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-POST04-01	MEDIUM	Ktype跨2004年外廓长度变更拆分。	READY
133129	133129	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-POST04-01	MEDIUM		READY
133147	133147	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AIXAM-COUPE-SENSATION-COUPE-01	2762	1500	1480	AIXAM official user manual	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-AIXAM-CROSSLINE-SENSATION-HATCHBACK-01	3000	1500	1540	AIXAM official user manual	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-MITSUBISHI-LANCER-IV-SEDAN-GTI-01	4235	1670	1405	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-iv-gti-1.8-16v-136hp-15676
EU-ROLLS-ROYCE-SILVER-SPIRIT-MK-I-SEDAN-01	5270	1890	1480	Rolls-Royce Silver Spirit Register	https://www.rrsilverspirit.com/models/1980Spirit.htm
EU-AUDI-A8-D3-4E-SEDAN-01	5051	1894	1444	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/252665/audi_a8_4_2_quattro.html
EU-MAZDA-121-III-HATCHBACK-5D-01	3830	1630	1320	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mazda/7477/Mazda-121-III-18-TD.html
EU-LANCIA-ZETA-I-MPV-01	4470	1834	1714	Auto-Data	https://www.auto-data.net/en/lancia-zeta-generation-1174
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4095	1695	1730	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1223510/daihatsu_terios_1_5_top_4wd_automatic.html
EU-SKODA-FABIA-I-PRAKTIK-PRE04-01	4222	1646	1452	Škoda Fabia Praktik historical specification	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-PRAKTIK-POST04-01	4232	1646	1452	Škoda Fabia Praktik historical specification	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	4495	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1997780/mitsubishi_lancer_rs_evolution_x.html
```

## 5. 下一步优先处理

1. Mercedes-Benz C-Klasse S204、Mitsubishi ASX、Outlander III 与 Fiat Doblò Cargo 多外廓分支。
2. Gumpert Apollo、Apollo N、Arrow、IE。
3. 集中闭合 RUF Turbo Florio、CTR、RTR、Turbo R、RCT、Ultimate 与 RGT Mk I–III。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2003/252665/audi_a8_4_2_quattro.html?utm_source=chatgpt.com "2003 Audi A8 4.2 Quattro (aut. 6) (model for Europe ) car ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 RUF Turbo Florio 与 CTR3。Turbo Florio 对应 474 kW 版本及 4491 × 1860 × 1295 mm 外廓；CTR 输入的 515 kW/700 PS 对应 CTR3，按 4445 × 1944 × 1200 mm 建组。([RUF][1])
* Gumpert Apollo 的 650 PS、700 PS Ktype 共用同一物理车身，首次创建 4460 × 1998 × 1114 mm 尺寸组。([汽车档案][2])
* Fiat Doblò 70 kW/95 PS 在官方德国价目中对应 M1 Kombi Maxi；按官方 Maxi 车身尺寸 4756 × 1832 × 1880 mm 建组，不扩展为没有证据支持的其他轴距或高顶分支。
* 本轮新增 5 个 READY Ktype、5 条映射和 4 个尺寸组；未修改既有尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射行：98
* PENDING Ktype：16
* 已确认并被引用尺寸组：60
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132962	132962	Targa	Turbo Florio		2	EU-RUF-TURBO-FLORIO-TARGA-01	HIGH	固定式防滚架Targa车身。	READY
132967	132967	Coupe	CTR3		2	EU-RUF-CTR3-COUPE-01	MEDIUM	输入排量写法与CTR3资料存在差异，700 PS物理外廓已确认。	READY
132971	132971	Coupe	Apollo		2	EU-GUMPERT-APOLLO-COUPE-01	HIGH		READY
132983	132983	Coupe	Apollo		2	EU-GUMPERT-APOLLO-COUPE-01	HIGH		READY
133098	133098	MPV	Doblò II facelift	263	5	EU-FIAT-DOBLO-II-263-COMBI-MAXI-01	MEDIUM	70 kW/95 PS对应M1 Kombi Maxi物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RUF-TURBO-FLORIO-TARGA-01	4491	1860	1295	RUF Japan Turbo Florio technical data	https://www.ruf-web.co.jp/com/turboflorio/
EU-RUF-CTR3-COUPE-01	4445	1944	1200	Auto-Data	https://www.auto-data.net/en/ruf-ctr-3-3.7-700hp-31957
EU-GUMPERT-APOLLO-COUPE-01	4460	1998	1114	Carfolio	https://www.carfolio.com/gumpert-apollo-s-235191
EU-FIAT-DOBLO-II-263-COMBI-MAXI-01	4756	1832	1880	Fiat Professional Doblò Cargo official technical specifications;Fiat Professional Doblò Cargo official German price list	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf;https://www.media.stellantis.com/uploads/de/DE/2019/Fiat_Prof/Preislisten/190404_FP_DobloCargo_PL.pdf
```

## 5. 下一步优先处理

1. Mercedes-Benz C-Klasse S204 改款前后的高度及物理分支。
2. Mitsubishi ASX、Outlander III 跨改款外廓边界。
3. Apollo N、Arrow、IE。
4. RUF RTR、Turbo R、RCT、Ultimate 及 RGT Mk I–III。

推进信号：CONTINUE

[1]: https://www.ruf-web.co.jp/com/turboflorio/?utm_source=chatgpt.com "RTC - RUF Turbo Florio -"
[2]: https://www.carfolio.com/gumpert-apollo-s-235191?utm_source=chatgpt.com "2009 Gumpert apollo s: detailed specifications ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后 16 个 Ktype 已闭合，新增 Apollo Arrow/IE、Mercedes-Benz S204 改款分支、Mitsubishi ASX/Outlander 分支及 RUF 各代尺寸组。RUF RtR 与 RGT 4.2 采用 RUF 技术数据，Apollo Arrow、RGT-8 等使用对应车型规格资料。([RUF][1])
* 已完成机械检查：映射表 116 行且 `id` 唯一；尺寸组表 75 行且 `DIMENSION_GROUP_ID` 唯一；全部引用闭合，无孤立尺寸组、无 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：116
* PENDING：0
* 最终尺寸组：75
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132961	132961	Coupe	Sensation		2	EU-AIXAM-COUPE-SENSATION-COUPE-01	HIGH		READY
132962	132962	Targa	Turbo Florio		2	EU-RUF-TURBO-FLORIO-TARGA-01	HIGH	固定式防滚架Targa车身。	READY
132963	132963	Hatchback	Sensation		2	EU-AIXAM-CROSSLINE-SENSATION-HATCHBACK-01	HIGH		READY
132967	132967	Coupe	CTR3		2	EU-RUF-CTR3-COUPE-01	MEDIUM	输入排量写法与CTR3资料存在差异，700 PS物理外廓已确认。	READY
132970	132970	Hatchback	Sensation		3	EU-AIXAM-CITY-2016-HATCHBACK-01	HIGH		READY
132971	132971	Coupe	Apollo		2	EU-GUMPERT-APOLLO-COUPE-01	HIGH		READY
132974	132974	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-GTI-01	MEDIUM	输入代际写法与明确的1.8 GTI四门车型资料不一致。	READY
132976	132976	Coupe	Sensation		2	EU-AIXAM-COUPE-SENSATION-COUPE-01	MEDIUM	电动版与同代Coupé共用物理外廓。	READY
132978	132978	Sedan	Silver Spirit Mk I	SZ	4	EU-ROLLS-ROYCE-SILVER-SPIRIT-MK-I-SEDAN-01	HIGH		READY
132983	132983	Coupe	Apollo		2	EU-GUMPERT-APOLLO-COUPE-01	HIGH		READY
132987	132987	Coupe	Apollo N		2	EU-GUMPERT-APOLLO-COUPE-01	MEDIUM	Apollo N延续原Gumpert Apollo物理外廓。	READY
132989	132989	Coupe	Arrow		2	EU-APOLLO-ARROW-COUPE-01	HIGH		READY
132995_l1	132995	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132995_l2	132995	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
132997_l1	132997	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132997_l2	132997	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
132998_l1	132998	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1短轴物理外廓。	READY
132998_l2	132998	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴物理外廓。	READY
133001	133001	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH		READY
133002	133002	SUV	Edge II facelift	CD539	5	EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	HIGH		READY
133004	133004	SUV	Edge II facelift	CD539	5	EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	HIGH		READY
133007	133007	Convertible	Boxster 987.2	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
133008	133008	Coupe	Cayman 987.2	987C	3	EU-PORSCHE-CAYMAN-9872-COUPE-01	HIGH		READY
133009	133009	Convertible	Boxster 981	981	2	EU-PORSCHE-BOXSTER-981-CONVERTIBLE-01	HIGH		READY
133011	133011	Coupe	Cayman 981	981C	3	EU-PORSCHE-CAYMAN-981-COUPE-01	HIGH		READY
133013	133013	Coupe	Intensa Emozione		2	EU-APOLLO-INTENSA-EMOZIONE-COUPE-01	HIGH		READY
133018	133018	SUV	Kuga II facelift	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
133019	133019	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	MEDIUM	1.8 TD资料明确对应五门车身。	READY
133025	133025	MPV	Zeta I		5	EU-LANCIA-ZETA-I-MPV-01	MEDIUM	输入终止月晚于公开车型生产期，物理外廓对应Zeta量产车身。	READY
133029	133029	MPV	Voyager	RT	5	EU-LANCIA-VOYAGER-RT-MPV-01	HIGH		READY
133035	133035	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133038	133038	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133039	133039	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133041	133041	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133042	133042	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
133043	133043	SUV	Juke I facelift	F15	5	EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	HIGH		READY
133044_prefl	133044	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	Ktype跨2011改款拆分。	READY
133044_facelift	133044	Wagon	C-Class S204 facelift	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	Ktype跨2011改款拆分。	READY
133056	133056	Coupe	RtR		2	EU-RUF-RTR-COUPE-01	HIGH		READY
133059_3dr_prefl	133059	Hatchback	147 I pre-facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_5dr_prefl	133059	Hatchback	147 I pre-facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_3dr_facelift	133059	Hatchback	147 I facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133059_5dr_facelift	133059	Hatchback	147 I facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖改款前后三门及五门外廓。	READY
133063	133063	Hatchback	147 I facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	HIGH	2009年车型范围为五门车身。	READY
133064	133064	Coupe	Turbo R	993	2	EU-RUF-TURBO-R-993-COUPE-01	HIGH		READY
133067	133067	Coupe	RCT EVO	964	2	EU-RUF-RCT-EVO-964-COUPE-01	MEDIUM	按标准窄体Coupé物理外廓落盘。	READY
133069	133069	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133070	133070	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
133071	133071	Coupe	Ultimate	964	2	EU-RUF-ULTIMATE-964-COUPE-01	HIGH		READY
133072_prefl	133072	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133072_facelift	133072	Hatchback	Ibiza IV facelift	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133073	133073	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH		READY
133074	133074	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
133075	133075	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH		READY
133076	133076	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-SC-HATCHBACK-PREFL-01	HIGH	SC三门物理外廓。	READY
133078_prefl	133078	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133078_facelift	133078	Hatchback	Ibiza IV facelift	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	HIGH	N1/Kasten用途；Ktype跨2012改款拆分。	READY
133082	133082	Wagon	Córdoba I facelift	6K5	5	EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	HIGH	Vario旅行车外廓。	READY
133083	133083	Wagon	Córdoba I facelift	6K5	5	EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	HIGH	N1/Kasten用途不改变Vario外廓。	READY
133085	133085	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133090	133090	SUV	ASX I	GA0	5	EU-MITSUBISHI-ASX-I-GA0-SUV-01	HIGH		READY
133092	133092	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH	N1/Kasten用途不改变五门外廓。	READY
133097	133097	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-CONVERTIBLE-16IN-01	MEDIUM	欧洲标准16英寸轮径软顶外廓。	READY
133098	133098	MPV	Doblò II facelift	263	5	EU-FIAT-DOBLO-II-263-COMBI-MAXI-01	MEDIUM	70 kW/95 PS对应M1 Kombi Maxi物理外廓。	READY
133099	133099	Coupe	RGT Mk I	996	2	EU-RUF-RGT-MK-I-996-COUPE-01	HIGH		READY
133100	133100	Coupe	RGT Mk I	996	2	EU-RUF-RGT-MK-I-996-COUPE-01	HIGH		READY
133101	133101	Coupe	RGT Mk II	997	2	EU-RUF-RGT-MK-II-997-COUPE-01	HIGH		READY
133102	133102	Coupe	RGT Mk II RGT-8	997	2	EU-RUF-RGT-MK-II-997-COUPE-01	MEDIUM	V8动力不改变同代RGT物理外廓。	READY
133103	133103	Coupe	RGT Mk III RGT-8	991	2	EU-RUF-RGT-MK-III-991-RGT8-COUPE-01	HIGH		READY
133104	133104	Coupe	RGT Mk III 4.2	991	2	EU-RUF-RGT-MK-III-991-42-WIDEBODY-COUPE-01	HIGH		READY
133105	133105	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
133106	133106	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133107	133107	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133108	133108	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133115	133115	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH		READY
133116	133116	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133117	133117	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133119	133119	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-CONVERTIBLE-17IN-01	MEDIUM	欧洲标准17英寸轮径软顶外廓。	READY
133120	133120	Targa	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-RF-16IN-01	MEDIUM	欧洲标准16英寸轮径RF外廓。	READY
133121	133121	Targa	MX-5 IV	ND	2	EU-MAZDA-MX5-IV-ND-RF-17IN-01	MEDIUM	欧洲标准17英寸轮径RF外廓。	READY
133122	133122	Wagon	Octavia I facelift/Tour	1U5	5	EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	HIGH	N1/Kasten用途不改变Combi外廓。	READY
133123	133123	Wagon	Octavia I facelift/Tour	1U5	5	EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	HIGH	N1/Kasten用途不改变Combi外廓。	READY
133124	133124	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133125_pre04	133125	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-PRE04-01	MEDIUM	Ktype跨2004年外廓长度变更拆分。	READY
133125_post04	133125	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-POST04-01	MEDIUM	Ktype跨2004年外廓长度变更拆分。	READY
133126	133126	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133128	133128	Wagon	Optima JF	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
133129	133129	Wagon	Fabia I Praktik		5	EU-SKODA-FABIA-I-PRAKTIK-POST04-01	MEDIUM		READY
133130	133130	MPV	Roomster I facelift	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH		READY
133131	133131	Liftback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
133132	133132	Liftback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
133133_prefl	133133	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133133_facelift	133133	MPV	Roomster I facelift	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH	Ktype跨2010改款拆分。	READY
133134	133134	Wagon	MINI Clubman I	R55	5	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	HIGH	Cooper S Clubman外廓。	READY
133135_prefl	133135	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133135_facelift	133135	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133139_prefl	133139	Wagon	Fabia II Combi	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133139_facelift	133139	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133143	133143	Coupe	MINI Coupé I	R58	2	EU-MINI-MINI-R58-COUPE-COOPER-S-01	HIGH	Cooper S专属外廓。	READY
133145_prefl	133145	SUV	Outlander III	GF0W	5	EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-PREFL-01	HIGH	Ktype跨2015改款拆分。	READY
133145_facelift	133145	SUV	Outlander III facelift	GF0W	5	EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	HIGH	Ktype跨2015改款拆分。	READY
133147	133147	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	HIGH		READY
133148_prefl	133148	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133148_facelift	133148	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133155	133155	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133156	133156	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
133157	133157	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133158	133158	Hatchback	Punto II	188	5	EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	HIGH	Bipower五门外廓。	READY
133159	133159	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
133160	133160	Wagon	Stilo I Multi Wagon	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH	N1/Kasten用途不改变Multi Wagon外廓。	READY
133161	133161	Wagon	Stilo I Multi Wagon	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH	N1/Kasten用途不改变Multi Wagon外廓。	READY
133162	133162	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
133164	133164	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
133165_prefl	133165	Wagon	Fabia II Combi	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	Ktype跨2010改款拆分。	READY
133165_facelift	133165	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	Ktype跨2010改款拆分。	READY
133167	133167	SUV	XD3 II	G01	5	EU-ALPINA-XD3-II-G01-SUV-PREFL-01	HIGH	285 kW/388 PS对应G01改款前外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2801-2900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AIXAM-COUPE-SENSATION-COUPE-01	2762	1500	1480	AIXAM official user manual	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-RUF-TURBO-FLORIO-TARGA-01	4491	1860	1295	RUF Japan Turbo Florio technical data	https://www.ruf-web.co.jp/com/turboflorio/
EU-AIXAM-CROSSLINE-SENSATION-HATCHBACK-01	3000	1500	1540	AIXAM official user manual	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-RUF-CTR3-COUPE-01	4445	1944	1200	Auto-Data	https://www.auto-data.net/en/ruf-ctr-3-3.7-700hp-31957
EU-AIXAM-CITY-2016-HATCHBACK-01	2758	1500	1470	AIXAM official user manual	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-GUMPERT-APOLLO-COUPE-01	4460	1998	1114	Carfolio	https://www.carfolio.com/gumpert-apollo-s-235191
EU-MITSUBISHI-LANCER-IV-SEDAN-GTI-01	4235	1670	1405	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-iv-gti-1.8-16v-136hp-15676
EU-ROLLS-ROYCE-SILVER-SPIRIT-MK-I-SEDAN-01	5270	1890	1480	Rolls-Royce Silver Spirit Register	https://www.rrsilverspirit.com/models/1980Spirit.htm
EU-APOLLO-ARROW-COUPE-01	4890	1992	1224	Apollo Arrow debut technical specifications	https://paultan.org/2016/03/02/apollo-arrow-debuts-in-geneva-1000-hp-1000-nm/
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	Peugeot LCV Catalogue 2020	https://kwt.peugeot.com/content/dam/peugeot/saudi_arabia/brochure/Peugeot_LCV_Catalogue_2020.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	Peugeot LCV Catalogue 2020	https://kwt.peugeot.com/content/dam/peugeot/saudi_arabia/brochure/Peugeot_LCV_Catalogue_2020.pdf
EU-AUDI-A8-D3-4E-SEDAN-01	5051	1894	1444	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/252665/audi_a8_4_2_quattro.html
EU-FORD-EDGE-II-CD539-FACELIFT-SUV-01	4834	1928	1732	Ford Edge official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-edge.pdf
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1292	Auto-Data	https://www.auto-data.net/en/porsche-boxster-987-facelift-2009-2.9-255hp-40880
EU-PORSCHE-CAYMAN-9872-COUPE-01	4347	1801	1304	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-facelift-2009-2.9-265hp-40905
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-01	4374	1801	1282	Porsche 2013 Boxster official technical specifications;Automobile-Catalog	https://newsroom.porsche.com/dam/jcr%3A4d1913a9-97f9-4ade-8bc4-fc2cc32caeb9/2013_Boxster_Technical_Specifications.pdf;https://www.automobile-catalog.com/car/2013/2871725/porsche_boxster.html
EU-PORSCHE-CAYMAN-981-COUPE-01	4380	1801	1294	Porsche 2014 Cayman official technical specifications;Automobile-Catalog	https://newsroom.porsche.com/dam/jcr%3A0036dadf-873b-46b8-86b2-841009f188af/2014_Cayman_Technical_Specifications.pdf;https://www.automobile-catalog.com/car/2014/2871785/porsche_cayman.html
EU-APOLLO-INTENSA-EMOZIONE-COUPE-01	5066	1995	1130	Apollo Intensa Emozione official technical specifications	https://www.allcarindex.com/blog/apollo-intensa-emozione-officialy-revealed-wvideo
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2455610/ford_kuga_2_0_tdci_150_2x4.html
EU-MAZDA-121-III-HATCHBACK-5D-01	3830	1630	1320	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mazda/7477/Mazda-121-III-18-TD.html
EU-LANCIA-ZETA-I-MPV-01	4470	1834	1714	Auto-Data	https://www.auto-data.net/en/lancia-zeta-generation-1174
EU-LANCIA-VOYAGER-RT-MPV-01	5218	1998	1750	Lancia Voyager official specifications	https://www.media.stellantis.com/uploads/fr/FR/2013/LANCIA/TARIFS/130201_FT_VOYAGER178.pdf
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Audi Q3 official dimensions sheet (07/18)	https://www.audi.com/en/publications/dimensions/dimensions-q3-1413/download
EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	4135	1765	1565	Nissan JUKE official brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Files/Brochures/Models/Juke/JUK0139r02_Nissan_JUKE_Brochure%20PDF.pdf
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-c-250-cgi-blueefficiency-204hp-5g-tronic-44296
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-facelift-2011-c-250-cdi-blueefficiency-204hp-7g-tronic-plus-18859
EU-RUF-RTR-COUPE-01	4491	1860	1295	RUF Japan RtR technical data	https://www.ruf-web.co.jp/com/RtR/
EU-ALFA-ROMEO-147-937-HATCHBACK-3D-PREFL-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-5D-PREFL-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-3D-FACELIFT-01	4223	1729	1442	Alfa Romeo new 147 range official specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
EU-ALFA-ROMEO-147-937-HATCHBACK-5D-FACELIFT-01	4223	1729	1442	Alfa Romeo new 147 range official specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
EU-RUF-TURBO-R-993-COUPE-01	4290	1735	1300	Conceptcarz	https://www.conceptcarz.com/s29281/ruf-turbo-r.aspx
EU-RUF-RCT-EVO-964-COUPE-01	4250	1652	1310	RUF RCT technical dimensions	https://en.wikipedia.org/wiki/Ruf_RCT
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	4351	1798	1465	Alfa Romeo Giulietta official owner handbook	https://aftersales.fiat.com/eLumData/EN/83/191_GIULIETTA/83_191_GIULIETTA_604.38.862_EN_03_09.16_L_LG/83_191_GIULIETTA_604.38.862_EN_03_09.16_L_LG.pdf
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Cars V60 dimensions	https://www.volvocars.com/en-ae/support/car/v60/article/766ee075f0e03896c0a8015109ee0749/
EU-RUF-ULTIMATE-964-COUPE-01	4250	1652	1250	RUF Ultimate official sales brochure	https://i.i-sgcm.com/new_cars/cars/11915/brochures/brochure_20160927104917.pdf
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	4052	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3094550/seat_ibiza_1_2_12v_70.html
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	4061	1693	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3095600/seat_ibiza_1_2_tdi_cr_75.html
EU-SEAT-IBIZA-IV-6J1-SC-HATCHBACK-PREFL-01	4034	1693	1428	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3094670/seat_ibiza_sc_1_6_16v_105.html
EU-SEAT-CORDOBA-I-6K5-VARIO-FACELIFT-01	4163	1640	1433	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3070925/seat_cordoba_vario_1_9_tdi_110.html
EU-MITSUBISHI-ASX-I-GA0-SUV-01	4295	1770	1615	Mitsubishi ASX official brochure	https://ingressmotors.com/wp-content/uploads/2015/11/2015-mitsubshi-ASX-leaflet-brochure.pdf
EU-MAZDA-MX5-IV-ND-CONVERTIBLE-16IN-01	3915	1735	1225	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-FIAT-DOBLO-II-263-COMBI-MAXI-01	4756	1832	1880	Fiat Professional Doblò Cargo official technical specifications;Fiat Professional Doblò Cargo official German price list	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf;https://www.media.stellantis.com/uploads/de/DE/2019/Fiat_Prof/Preislisten/190404_FP_DobloCargo_PL.pdf
EU-RUF-RGT-MK-I-996-COUPE-01	4430	1765	1305	Gran Turismo RUF RGT model specifications	https://gran-turismo.fandom.com/wiki/RUF_RGT_%2700
EU-RUF-RGT-MK-II-997-COUPE-01	4468	1872	1290	Road & Track RUF RGT test specifications	https://www.roadandtrack.com/car-culture/a20748/ruf-rgt-1/
EU-RUF-RGT-MK-III-991-RGT8-COUPE-01	4491	1808	1295	Supercars.net RUF RGT-8 specifications	https://www.supercars.net/blog/?p=251824
EU-RUF-RGT-MK-III-991-42-WIDEBODY-COUPE-01	4491	2012	1295	RUF Japan RGT 4.2 technical data	https://www.ruf-web.co.jp/com/RGT4.2/
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-facelift-2019-1.6-crdi-136hp-dct-35989
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Auto-Data	https://www.auto-data.net/en/hyundai-tucson-iii-facelift-2018-1.6-crdi-115hp-37666
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4095	1695	1730	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1223510/daihatsu_terios_1_5_top_4wd_automatic.html
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-iv-tm-2.4-gdi-185hp-4wd-automatic-32849
EU-MAZDA-MX5-IV-ND-CONVERTIBLE-17IN-01	3915	1735	1230	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-MAZDA-MX5-IV-ND-RF-16IN-01	3915	1735	1230	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-MAZDA-MX5-IV-ND-RF-17IN-01	3915	1735	1235	Mazda MX-5 official owner manual	https://owners-manual.mazda.com/gen/en/mx-5/mx-5_8fl9ee16j/contents/10020103.html
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3135395/skoda_octavia_combi_1_9_tdi_90.html
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470	Kia Optima Sportswagon official press kit	https://prod2-press.kia.com/eu/en/home/models/optima-sportswagon/optima-sportswagon.html
EU-SKODA-FABIA-I-PRAKTIK-PRE04-01	4222	1646	1452	Škoda Fabia Praktik historical specification	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-PRAKTIK-POST04-01	4232	1646	1452	Škoda Fabia Praktik historical specification	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	4214	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3143090/skoda_roomster_1_6_tdi_cr_90.html
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400	Kia Stinger official brochure	https://www.kia.com/content/dam/kwcms/sg/en/pdf/Brochure/Brochure_Specs/StingerBrochureSpecsSheet_Oct2021.pdf
EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	4205	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/3142835/skoda_roomster_1_4_tdi_pd_80.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1753625/mini_cooper_s_clubman.html
EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	3992	1642	1498	Škoda Drive Place	https://skoda.drive.place/fabia/ii/group_hatchback_5d/249719
EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	4000	1642	1498	Automoli	https://www.automoli.com/en/vehicles/skoda/fabia/fabia-ii-facelift-2010-4316/
EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	4239	1642	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/3140615/skoda_fabia_combi_1_4_tdi_80.html
EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	4247	1642	1498	Automoli	https://www.automoli.com/en/vehicles/skoda/fabia/fabia-ii-combi-facelift-2010-4315/
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384	Carfolio	https://www.carfolio.com/mini-cooper-s-coupe-247445
EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-PREFL-01	4655	1800	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2012405/mitsubishi_outlander_2_0_2wd_cleartec_inform.html
EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	4695	1810	1680	Auto-Data	https://www.auto-data.net/en/mitsubishi-outlander-iii-facelift-2015-2.0-mivec-150hp-4wd-automatic-22198
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	4495	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1997780/mitsubishi_lancer_rs_evolution_x.html
EU-RENAULT-SCENIC-IV-MPV-01	4406	1866	1653	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2986100/renault_scenic_blue_dci_150.html
EU-RENAULT-GRAND-SCENIC-IV-MPV-01	4635	1866	1660	Renault Grand Scenic official price list	https://www.uniqehorn.eu/carmanager/res/files/PL_Scenic_E6d_Temp_01_21.pdf
EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	3835	1660	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/723875/fiat_punto_5-porte_1_2_16v_elx.html
EU-FIAT-STILO-I-192-MULTIWAGON-01	4516	1756	1570	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/724925/fiat_stilo_multi_wagon_1_9_jtd_115_active.html
EU-ALPINA-XD3-II-G01-SUV-PREFL-01	4718	1897	1655	Auto-Data	https://www.auto-data.net/en/alpina-xd3-g01-generation-6138
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2801-2900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ruf-web.co.jp/com/RtR/ "https://www.ruf-web.co.jp/com/RtR/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2151 行）
- 累计尺寸组：dimension_groups_final.tsv（1086 行）

