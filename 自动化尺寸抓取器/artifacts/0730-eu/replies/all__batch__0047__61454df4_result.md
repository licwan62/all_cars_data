# 任务：all 第 4601-4700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0047__61454df4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4601-4700 行

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
all 第 4601-4700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473
EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	4506	1851	1602
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705
EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	5299	1976	1488
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-F95-M-COMPETITION-SUV-01	4953	2015	1749
EU-BMW-X5-F95-M-SUV-01	4953	2015	1751
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-DODGE-CALIBER-I-PM-HATCHBACK-01	4415	1800	1535
EU-FERRARI-F8-TRIBUTO-COUPE-01	4611	1979	1206
EU-FIAT-500-I-312-HATCHBACK-PREFL-01	3546	1627	1488
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650
EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	4320	1722	1489
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1466
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-FACELIFT-01	4091	1735	1487
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-FACELIFT-01	4091	1735	1487
EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	3995	1710	1490
EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	3940	1710	1490
EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	4065	1760	1529
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449
EU-HYUNDAI-I20-II-GB-HATCHBACK-01	4035	1734	1474
EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	4035	1734	1474
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	4459	1924	1180
EU-LAMBORGHINI-HURACAN-PERFORMANTE-SPYDER-CONVERTIBLE-01	4506	1924	1180
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB3700-01	6060	2206	2410
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4250-01	6940	2206	2410
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4800-01	7485	2206	2410
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB3700-01	6060	2206	2405
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4250-01	6940	2206	2405
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4800-01	7485	2206	2405
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971
EU-NISSAN-NV300-I-L1H2-01	4999	1956	2493
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971
EU-NISSAN-NV300-I-L2H2-01	5399	1956	2490
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-PEUGEOT-2008-II-SUV-PREFL-01	4300	1770	1550
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	4137	1724	1810
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	4696	1923	1624
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-TURBO-01	4684	1926	1624
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-SEAT-IBIZA-IV-6J1-SC-HATCHBACK-PREFL-01	4034	1693	1428
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	4061	1693	1445
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-ST-FACELIFT-WAGON-01	4236	1693	1445
EU-SUBARU-XV-I-GP-SUV-01	4450	1780	1570
EU-SUBARU-XV-II-SUV-01	4465	1805	1615
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V40-II-HATCHBACK-01	4369	1802	1420
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798
EU-VW-T-ROC-I-SUV-01	4234	1819	1573

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Nissan	Nv300	2.0 DCI 170	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138786
Nissan	Nv300	2.0 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138787
Nissan	Nv300 kombi	2.0 DCI 145	Bus	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138788
Nissan	Nv300 kombi	2.0 DCI 120	Bus	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138789
Nissan	Nv300 kombi	2.0 DCI 170	Bus	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138790
Hyundai	Tucson	2.0 LPG Allrad	SUV	Allrad	Benzin/Autogas (LPG)	104	141	Jun 2009	Mar 2010	2024-03-01	138796
Hyundai	I20 i	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	75	102	Dec 2008	Dec 2012	2024-03-01	138797
Volvo	V60 ii	D4 Polestar AWD	Kombi	Allrad	Diesel	147	200	Feb 2018	Dec 2021	2024-05-01	138805
Dodge	Caliber	2.0 CRD	Schrägheck	Frontantrieb	Diesel	88	120	Jun 2006	Nov 2011	2024-03-01	138806
Volvo	V40	D4 Polestar	Schrägheck	Frontantrieb	Diesel	147	200	May 2014	Aug 2019	2024-03-01	138807
Volvo	V40 cross country	T5 Polestar AWD	Schrägheck	Allrad	Benzin	186	253	Jan 2015	Aug 2019	2024-03-01	138808
Volvo	V40	T5 Drive-e Polestar	Schrägheck	Frontantrieb	Benzin	186	253	May 2014	Aug 2019	2024-03-01	138809
Volvo	V60 i cross country	D4 Drive-e Polestar	Kombi	Frontantrieb	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138811
Volvo	V60 i cross country	D4 Polestar AWD	Kombi	Allrad	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138812
Volvo	V60 i cross country	T5 Drive-e Polestar	Kombi	Frontantrieb	Benzin	186	253	Mar 2015	Jul 2018	2024-03-01	138814
Volvo	V60 i cross country	T5 Drive-e Polestar AWD	Kombi	Allrad	Benzin	186	253	Mar 2015	Jul 2018	2024-03-01	138816
Volvo	S90 ii	T8 Plug-in Hybrid Polestar AWD	Stufenheck	Allrad	Benzin/Elektro	246	334	Oct 2017	Dec 2022	2024-05-01	138819
Volvo	S90 ii	T6 Drive-e Polestar AWD	Stufenheck	Allrad	Benzin	246	334	Mar 2016	Dec 2021	2024-05-01	138820
Volvo	S90 ii	T5 Drive-e Polestar	Stufenheck	Frontantrieb	Benzin	192	261	Mar 2016	Dec 2021	2024-05-01	138821
Volvo	S60 ii	D4 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138823
Volvo	S60 ii	D5 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	171	232	Mar 2015	May 2018	2024-03-01	138824
Volvo	S60 ii cross country	D4 Polestar AWD	Stufenheck	Allrad	Diesel	162	220	Mar 2015	Jul 2018	2024-03-01	138825
Volvo	S60 ii cross country	T5 Drive-e Polestar AWD	Stufenheck	Allrad	Benzin	186	253	Jun 2016	May 2018	2024-03-01	138826
Isuzu	D-Max i	2.5 Ditd 4X4	Pritsche/Fahrgestell	Allrad	Diesel	100	136	Oct 2006	Oct 2012	2024-03-01	138829
Volvo	S90 ii	D4 Drive-e Polestar AWD	Stufenheck	Allrad	Diesel	147	200	Mar 2016	Dec 2021	2024-05-01	138830
Audi	Q8	RS FSI Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	441	600	Sep 2019	-	2025-11-01	138832
Audi	A6 c8	55 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	270	367	Nov 2019	-	2024-03-01	138834
Volvo	Xc90 ii	T8 Plug-in Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	246	334	Jun 2015	Dec 2022	2024-05-01	138837
Volvo	V90 ii	T8 Plug-in Hybrid Polestar AWD	Kombi	Allrad	Benzin/Elektro	246	334	Mar 2016	Dec 2018	2024-05-01	138839
Renault	Trafic iii	2.0 DCI 120	Bus	Frontantrieb	Diesel	88	120	Jun 2019	-	2024-03-01	138844
Renault	Trafic iii	2.0 DCI 145	Bus	Frontantrieb	Diesel	107	145	Jun 2019	-	2024-03-01	138845
Audi	A7 sportback	50 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	220	299	Nov 2019	-	2024-03-01	138846
Renault	Trafic iii	2.0 DCI 170	Bus	Frontantrieb	Diesel	125	170	Jun 2019	-	2024-03-01	138847
Audi	Q7	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	280	381	Nov 2019	-	2024-03-01	138851
Audi	Q7	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	335	455	Nov 2019	-	2024-03-01	138853
VW	Crafter	2.0 TDI 4motion	Bus	Allrad	Diesel	103	140	Apr 2017	-	2024-03-01	138856
Audi	Q5	35 TDI Mild Hybrid	SUV	Frontantrieb	Diesel/Elektro	120	163	Sep 2019	-	2024-03-01	138857
Audi	Q5	40 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	150	204	Sep 2019	-	2024-03-01	138858
Peugeot	2008 ii	1.2 Puretech 100	SUV	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	138869
Audi	A8 d5	S8 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	420	571	Feb 2019	-	2025-11-01	138873
Audi	Q3	35 Tfsi Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	138876
Audi	Q3	35 Tfsi Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	138877
Nissan	Nv250	DCI 80	Kasten	Frontantrieb	Diesel	59	80	Jul 2019	-	2024-03-01	138879
Nissan	Nv250	DCI 95	Kasten	Frontantrieb	Diesel	70	95	Jul 2019	-	2024-03-01	138880
Nissan	Nv250	DCI 115	Kasten	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	138881
Nissan	Nv250	DCI 80	Bus	Frontantrieb	Diesel	59	80	Jul 2019	-	2024-03-01	138882
Nissan	Nv250	DCI 95	Bus	Frontantrieb	Diesel	70	95	Jul 2019	-	2024-03-01	138883
Nissan	Nv250	DCI 115	Bus	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	138884
Mercedes-benz	Glc	300 4-matic	SUV	Allrad	Benzin	190	258	Nov 2019	Mar 2023	2024-03-01	138888
Ferrari	812 gts spider	6.5	Cabriolet	Heckantrieb	Benzin	585	795	Oct 2019	-	2024-03-01	138892
Peugeot	Partner	1.5 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Jul 2019	-	2024-03-01	138894
VW	T-Roc	1.0 TSI	Cabriolet	Frontantrieb	Benzin	85	116	Dec 2019	-	2025-02-03	138897
VW	T-Roc	1.5 TSI	Cabriolet	Frontantrieb	Benzin	110	150	Dec 2019	-	2024-03-01	138898
Peugeot	Partner	1.2 Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jan 2019	-	2025-12-01	138902
Peugeot	Partner	1.2 Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	138903
Bentley	Flying spur	6.0 W12 TSI 4WD	Stufenheck	Allrad	Benzin	467	635	Apr 2019	-	2024-03-01	138905
Mercedes-benz	Sprinter 4,6-T	416 CDI 4X4	Kasten	Allrad	Diesel	120	163	Nov 2013	Dec 2018	2024-03-01	138913
Subaru	Xv	2.0 I E-boxer AWD	SUV	Allrad	Benzin/Elektro	110	150	Oct 2019	-	2024-03-01	138918
Audi	Q5	50 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	220	299	Apr 2019	-	2024-03-01	138940
Citroën	Jumpy iii	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	138950
Peugeot	Partner	1.5 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jul 2019	-	2024-03-01	138957
Citroën	Berlingo	1.5 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2019	-	2024-03-01	138959
Land Rover	Range rover iv	P360 Mhev 4X4	SUV	Allrad	Benzin/Elektro	265	360	Dec 2019	Sep 2021	2025-02-03	138972
Dodge	Challenger	6.2 SRT Hellcat Redeye	Coupe	Heckantrieb	Benzin	586	797	Sep 2019	-	2024-03-01	138974
Mercedes-benz	Marco polo camper	300 CDI	Bus	Heckantrieb	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	138980
Mercedes-benz	Marco polo camper	300 CDI 4-matic	Bus	Allrad	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	138981
Mercedes-benz	Marco polo camper	200 CDI	Bus	Heckantrieb	Diesel	100	136	Mar 2015	-	2024-03-01	138982
Mercedes-benz	Marco polo camper	200 CDI 4-matic	Bus	Allrad	Diesel	100	136	Mar 2015	-	2024-03-01	138984
Mercedes-benz	Marco polo camper	220 CDI	Bus	Heckantrieb	Diesel	120	163	Mar 2015	-	2024-03-01	138985
Mercedes-benz	Marco polo camper	220 CDI 4-matic	Bus	Allrad	Diesel	120	163	Mar 2015	-	2024-03-01	138986
Mercedes-benz	Marco polo camper	250 CDI	Bus	Heckantrieb	Diesel	140	190	Mar 2015	-	2024-03-01	138987
Mercedes-benz	Marco polo camper	250 CDI 4-matic	Bus	Allrad	Diesel	140	190	Mar 2015	-	2024-03-01	138989
Porsche	Macan	2.9 GTS	SUV	Allrad	Benzin	280	380	May 2019	-	2024-05-01	139008
Mercedes-benz	E-Klasse	E 300	Cabriolet	Heckantrieb	Benzin	190	258	Mar 2019	-	2024-03-01	139012
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	190	258	Apr 2019	Oct 2023	2025-02-03	139015
Hyundai	I10 iii	1.2 MPI	Schrägheck	Frontantrieb	Benzin	62	84	Sep 2019	-	2024-03-01	139017
Hyundai	I10 iii	1.0 MPI	Schrägheck	Frontantrieb	Benzin	49	67	Sep 2019	-	2024-03-01	139021
NIO	Es8	EV	SUV	Allrad	Elektro	400	544	Jan 2023	Jun 2023	2026-01-01	139022
Mercedes-benz	E-Klasse	E 300	Coupe	Heckantrieb	Benzin	190	258	Aug 2018	-	2024-03-01	139027
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	70	95	Dec 2019	-	2024-03-01	139031
Opel	Grandland	1.6 Turbo Hybrid	SUV	Frontantrieb	Benzin/Elektro	165	224	Dec 2019	-	2025-02-03	139036
Seat	Ibiza iv	1.2 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	May 2010	May 2015	2024-03-01	139037
Mercedes-benz	Vario	O 815	Bus	Heckantrieb	Diesel	110	150	Aug 1996	Dec 2010	2024-03-01	139039
VW	Caddy alltrack iv	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jun 2019	Sep 2020	2025-06-01	139045
Mclaren	Gt	4	Coupe	Heckantrieb	Benzin	456	620	Aug 2019	-	2024-03-01	139047
Lamborghini	Huracán	5.2 LP 610-2	Coupe	Heckantrieb	Benzin	449	610	Jan 2020	-	2024-03-01	139073
Renault	Trafic iii	2.0 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jun 2019	-	2024-03-01	139077
Renault	Trafic iii	2.0 DCI 170	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jun 2019	-	2024-03-01	139078
KIA	Ceed	1.6 GDI Hybrid	Kombi	Frontantrieb	Benzin/Elektro	104	141	Dec 2019	-	2024-03-01	139095
Ferrari	F8	3.9	Cabriolet	Heckantrieb	Benzin	530	720	Dec 2019	-	2024-03-01	139129
VW	Caddy alltrack iv	2.0 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	103	140	May 2015	Sep 2020	2025-06-01	139133
VW	Caddy alltrack iv	2.0 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	81	110	May 2015	Sep 2020	2025-06-01	139134
VW	Caddy alltrack iv	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	May 2015	Sep 2020	2025-06-01	139135
VW	Caddy alltrack iv	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	May 2015	Nov 2017	2025-06-01	139136
VW	Caddy alltrack iv	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	May 2015	Sep 2020	2025-06-01	139137
Ferrari	812 gts spider	6.5	Cabriolet	Heckantrieb	Benzin	588	799	Jan 2020	-	2025-12-01	139151
Ford	Fiesta vii	1.1 Ti-vct	Schrägheck	Frontantrieb	Benzin	55	75	Oct 2019	-	2024-03-01	139153
BMW	X5	Xdrive 45 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	235	320	Jun 2019	Mar 2023	2024-03-01	139154
Ford	Ecosport	1.5 Tdci Ecoblue	SUV	Frontantrieb	Diesel	88	120	Nov 2019	-	2024-03-01	139156
Fiat	500	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	51	69	Jan 2020	-	2024-03-01	139160


--- Round 1 / 首次发送 ---
## 更新点

* 已完成首轮缓存匹配与物理分支拆分：46 个输入 Ktype 已闭合，对应 51 条 `READY` 映射。
* 复用既有尺寸组 27 个；首次闭合 8 个尺寸组，包括 Volvo V40 Cross Country、V60 Cross Country、Audi RS Q8、A7 Sportback、S8。Volvo 页面分别列出车身宽度与含后视镜宽度；Audi 技术资料明确给出不含后视镜宽度。([沃尔沃汽车][1])
* 新建 Ferrari 812 GTS、Ferrari F8 Spider 和 Hyundai i10 III 尺寸组。([汽车数据网][2])
* 已拆分 Citroën Jumpy III 的 XS/M/XL、Mercedes-Benz W213 的改款前后，以及 Ford Fiesta Mk8 的三门/五门分支。
* McLaren GT 当前找到的 2045 mm 宽度是“后视镜折叠”口径，不满足车身不含后视镜要求，暂不建组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：105
* READY 映射：51
* PENDING 映射：54
* 已引用尺寸组：35
* 复用既有尺寸组：27
* 本轮新建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138786	138786	Pickup	NV300 I				MEDIUM	候选为多轴距底盘驾驶室；尚未确认分支。	PENDING: 底盘驾驶室轴距/驾驶室分支未闭合
138787	138787	Pickup	NV300 I				MEDIUM	候选为多轴距底盘驾驶室；尚未确认分支。	PENDING: 底盘驾驶室轴距/驾驶室分支未闭合
138788	138788	MPV	NV300 I				MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: 客运车身 L1/L2 分支未闭合
138789	138789	MPV	NV300 I				MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: 客运车身 L1/L2 分支未闭合
138790	138790	MPV	NV300 I				MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: 客运车身 L1/L2 分支未闭合
138796	138796	SUV	Tucson I	JM	5		MEDIUM	现有缓存仅锁定 2WD；AWD 外廓需独立闭合。	PENDING: AWD 外廓与既有 2WD 尺寸组边界未闭合
138797	138797	Hatchback	i20 I	PB	5		MEDIUM	生产区间跨改款前后，候选为两个既有尺寸组。	PENDING: 改款前/改款后物理分支未闭合
138805	138805	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	V60 II 五门旅行车外廓。	READY
138806	138806	Hatchback	Caliber I	PM	5	EU-DODGE-CALIBER-I-PM-HATCHBACK-01	HIGH	PM 五门掀背车外廓。	READY
138807	138807	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40 II 五门掀背车外廓。	READY
138808	138808	Hatchback	V40 II Cross Country		5	EU-VOLVO-V40-II-CROSS-COUNTRY-HATCHBACK-01	HIGH	Cross Country 五门外廓。	READY
138809	138809	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40 II 五门掀背车外廓。	READY
138811	138811	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
138812	138812	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
138814	138814	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
138816	138816	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
138819	138819	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
138820	138820	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
138821	138821	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
138823	138823	Sedan	S60 II		4		MEDIUM	S60 II 标准轿车尺寸组尚未闭合。	PENDING: 标准轿车三维与不含镜宽度未闭合
138824	138824	Sedan	S60 II		4		MEDIUM	S60 II 标准轿车尺寸组尚未闭合。	PENDING: 标准轿车三维与不含镜宽度未闭合
138825	138825	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country 四门轿车外廓。	READY
138826	138826	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country 四门轿车外廓。	READY
138829	138829	Pickup	D-Max I				MEDIUM	候选为多驾驶室/轴距底盘分支；尚未确认。	PENDING: 底盘驾驶室物理分支未闭合
138830	138830	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
138832	138832	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	HIGH	RS Q8 专属外廓。	READY
138834	138834	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	4A2 四门轿车外廓。	READY
138837	138837	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90 II 五门 SUV 外廓。	READY
138839	138839	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II 五门旅行车外廓。	READY
138844	138844	MPV	Trafic III	X82			MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: Trafic 客运车身 L1/L2 分支未闭合
138845	138845	MPV	Trafic III	X82			MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: Trafic 客运车身 L1/L2 分支未闭合
138846	138846	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	4KA 五门 Sportback 外廓。	READY
138847	138847	MPV	Trafic III	X82			MEDIUM	候选为 L1H1、L2H1 客运车身；尚未确认分支。	PENDING: Trafic 客运车身 L1/L2 分支未闭合
138851	138851	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M 改款五门 SUV 外廓。	READY
138853	138853	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M 改款五门 SUV 外廓。	READY
138856	138856	MPV	Crafter II				MEDIUM	候选为多轴距、多车顶 Bus 分支。	PENDING: Crafter Bus 轴距/车顶分支未闭合
138857	138857	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY 改款前五门 SUV 外廓。	READY
138858	138858	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY 改款前五门 SUV 外廓。	READY
138869	138869	SUV	2008 II	P24	5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	2008 II 改款前五门 SUV 外廓。	READY
138873	138873	Sedan	A8 D5	4N	4	EU-AUDI-A8-D5-S8-SEDAN-01	HIGH	D5 S8 四门轿车外廓。	READY
138876	138876	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3 五门 SUV 外廓。	READY
138877	138877	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3 五门 SUV 外廓。	READY
138879	138879	Van	NV250 I				MEDIUM	候选为标准/长轴 Van 分支。	PENDING: NV250 Van 长度分支未闭合
138880	138880	Van	NV250 I				MEDIUM	候选为标准/长轴 Van 分支。	PENDING: NV250 Van 长度分支未闭合
138881	138881	Van	NV250 I				MEDIUM	候选为标准/长轴 Van 分支。	PENDING: NV250 Van 长度分支未闭合
138882	138882	MPV	NV250 I				MEDIUM	候选为标准/长轴客运分支。	PENDING: NV250 客运长度分支未闭合
138883	138883	MPV	NV250 I				MEDIUM	候选为标准/长轴客运分支。	PENDING: NV250 客运长度分支未闭合
138884	138884	MPV	NV250 I				MEDIUM	候选为标准/长轴客运分支。	PENDING: NV250 客运长度分支未闭合
138888	138888	SUV	GLC I	X253	5		MEDIUM	2019 改款外廓与无后缀缓存组存在尺寸边界疑点。	PENDING: GLC 改款外廓尺寸冲突未解决
138892	138892	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS 双门敞篷外廓。	READY
138894	138894	Van/MPV	Partner III	K9			MEDIUM	输入混合 Van/MPV，且可能覆盖 M/XL。	PENDING: Partner 车身形式与长度分支未闭合
138897	138897	Convertible	T-Roc I	AC7	2		MEDIUM	T-Roc Cabriolet 为独立双门外廓。	PENDING: Cabriolet 三维与不含镜宽度未闭合
138898	138898	Convertible	T-Roc I	AC7	2		MEDIUM	T-Roc Cabriolet 为独立双门外廓。	PENDING: Cabriolet 三维与不含镜宽度未闭合
138902	138902	Van/MPV	Partner III	K9			MEDIUM	输入混合 Van/MPV，且可能覆盖 M/XL。	PENDING: Partner 车身形式与长度分支未闭合
138903	138903	Van/MPV	Partner III	K9			MEDIUM	输入混合 Van/MPV，且可能覆盖 M/XL。	PENDING: Partner 车身形式与长度分支未闭合
138905	138905	Sedan	Flying Spur III		4		MEDIUM	第三代 Flying Spur 已确认代际，车身不含镜宽度仍待闭合。	PENDING: 不含后视镜宽度未闭合
138913	138913	Van	Sprinter II	W906			MEDIUM	候选为多轴距、多车顶 4x4 Van 分支。	PENDING: Sprinter 4x4 轴距/车顶分支未闭合
138918	138918	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH	XV II 五门 SUV 外廓。	READY
138940	138940	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY 改款前五门 SUV 外廓。	READY
138950_xs	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-XS-01	MEDIUM	XS 短车身客运分支。	READY
138950_m	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-M-01	MEDIUM	M 中车身客运分支。	READY
138950_xl	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-XL-01	MEDIUM	XL 长车身客运分支。	READY
138957	138957	Van/MPV	Partner III	K9			MEDIUM	输入混合 Van/MPV，且可能覆盖 M/XL。	PENDING: Partner 车身形式与长度分支未闭合
138959	138959	Van/MPV	Berlingo III	K9			MEDIUM	输入混合 Van/MPV，且可能覆盖 M/XL。	PENDING: Berlingo 车身形式与长度分支未闭合
138972	138972	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	MEDIUM	L405 改款标准轴距五门外廓。	READY
138974	138974	Coupe	Challenger III	LC	2		MEDIUM	Redeye 外部套件/车高需独立确认。	PENDING: Redeye 专属外廓三维未闭合
138980	138980	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138981	138981	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138982	138982	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138984	138984	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138985	138985	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138986	138986	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138987	138987	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
138989	138989	MPV	Marco Polo W447	W447			MEDIUM	Marco Polo Camper 的升顶状态与整车高度边界尚未确认。	PENDING: Camper 车顶状态与高度未闭合
139008	139008	SUV	Macan I	95B	5		MEDIUM	GTS 改款外部套件与车高需独立闭合。	PENDING: Macan GTS 改款三维未闭合
139012	139012	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	A238 改款前双门敞篷外廓。	READY
139015_prefl	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	MEDIUM	W213 改款前四门轿车分支。	READY
139015_facelift	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	MEDIUM	W213 改款后四门轿车分支。	READY
139017	139017	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	i10 III 五门掀背车外廓。	READY
139021	139021	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	i10 III 五门掀背车外廓。	READY
139022	139022	SUV	ES8 I		5		MEDIUM	2023 欧洲 Ktype 对应的 ES8 代际/市场版本尚未锁定。	PENDING: ES8 代际与市场版本边界未闭合
139027	139027	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	C238 改款前双门轿跑外廓。	READY
139031_3dr	139031	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	MEDIUM	Mk8 三门掀背车分支。	READY
139031_5dr	139031	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	MEDIUM	Mk8 五门掀背车分支。	READY
139036	139036	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18 五门 SUV 外廓。	READY
139037	139037	Van/Hatchback	Ibiza IV	6J			MEDIUM	输入混合 Van/Hatchback，门数与外廓分支未确认。	PENDING: Ibiza Van/Hatchback 分支未闭合
139039	139039	MPV	Vario	W670			MEDIUM	O 815 Bus 可能覆盖多轴距及车身制造商外廓。	PENDING: Vario Bus 轴距/整车外廓未闭合
139045	139045	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139047	139047	Coupe	McLaren GT		2		MEDIUM	已找到的宽度为折叠后视镜口径，不能落盘。	PENDING: 不含后视镜车身宽度未确认
139073	139073	Coupe	Huracán I		2		MEDIUM	“LP 610-2”命名与已知驱动/功率分支不一致。	PENDING: Huracán 具体物理版本未确认
139077	139077	Pickup	Trafic III	X82			MEDIUM	候选为多轴距底盘驾驶室。	PENDING: Trafic 底盘驾驶室轴距分支未闭合
139078	139078	Pickup	Trafic III	X82			MEDIUM	候选为多轴距底盘驾驶室。	PENDING: Trafic 底盘驾驶室轴距分支未闭合
139095	139095	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD 五门旅行车外廓。	READY
139129	139129	Convertible	F8 Spider		2	EU-FERRARI-F8-SPIDER-CONVERTIBLE-01	HIGH	F8 Spider 双门敞篷外廓。	READY
139133	139133	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139134	139134	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139135	139135	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139136	139136	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139137	139137	Van/MPV	Caddy Alltrack IV	2K			MEDIUM	输入混合 Van/MPV，可能覆盖标准轴距/Maxi。	PENDING: Caddy Alltrack 车身与长度分支未闭合
139151	139151	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS 双门敞篷外廓。	READY
139153_3dr	139153	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	MEDIUM	Mk8 三门掀背车分支。	READY
139153_5dr	139153	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	MEDIUM	Mk8 五门掀背车分支。	READY
139154	139154	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05 改款前五门 SUV 外廓。	READY
139156	139156	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	EcoSport II 五门 SUV 外廓。	READY
139160	139160	Hatchback	500 I	312	3		MEDIUM	2020 Mild Hybrid 属改款后车身，既有缓存为改款前。	PENDING: 500 改款后三维未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V40-II-CROSS-COUNTRY-HATCHBACK-01	4370	1802	1458	Volvo Support V40 Cross Country dimensions	https://www.volvocars.com/en-th/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	4637	1866	1545	Volvo Support V60 Cross Country dimensions	https://www.volvocars.com/en-bh/support/car/v60-cross-country/article/18f77489f78f457dc0a801e800a04016/
EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	5012	1998	1694	Audi UK RS Q8 Technical Data	https://press.audi.co.uk/assets/documents/original/33583-AudiRSQ8UKTechDataMay2023.pdf
EU-AUDI-A7-C8-4KA-SPORTBACK-01	4969	1908	1422	Audi A7 Sportback facts and figures	https://www.audi.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835
EU-AUDI-A8-D5-S8-SEDAN-01	5179	1945	1474	Audi UK S8 Technical Data	https://press.audi.co.uk/assets/documents/original/16981-AudiS8TFSIquattrotiptronicUKTechnicalDataJuly2021.pdf
EU-FERRARI-812-GTS-CONVERTIBLE-01	4693	1971	1278	Auto-Data Ferrari 812 GTS	https://www.auto-data.net/en/ferrari-812-gts-generation-7574
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	Auto-Data Hyundai i10 III 1.2 MPi	https://www.auto-data.net/en/hyundai-i10-iii-1.2-mpi-84hp-37589
EU-FERRARI-F8-SPIDER-CONVERTIBLE-01	4611	1979	1206	Auto-Data Ferrari F8 Spider	https://www.auto-data.net/en/ferrari-f8-spider-3.9-v8-720hp-f1-dct-39252
```

## 下一步优先处理

1. 批量闭合共平台商用车：NV300/Trafic、NV250/Partner/Berlingo、Caddy Alltrack。
2. 处理可整簇消除多个 PENDING 的 Marco Polo、Crafter、Sprinter 和 Vario 轴距/车顶分支。
3. 补齐乘用车独立尺寸组：S60 II、T-Roc Cabriolet、GLC facelift、Macan GTS、Challenger Redeye、Fiat 500 facelift。
4. 单独解决 Bentley Flying Spur III、McLaren GT 的不含后视镜宽度，以及 Huracán 版本命名冲突。

推进信号：CONTINUE

[1]: https://www.volvocars.com/en-th/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/?utm_source=chatgpt.com "V40 Cross Country Dimensions | Volvo Support Thailand"
[2]: https://www.auto-data.net/en/ferrari-812-gts-generation-7574?utm_source=chatgpt.com "Ferrari 812 GTS | Technical Specs, Fuel consumption, ..."
[3]: https://www.auto-data.net/en/mclaren-gt-4.0-v8-620hp-ssg-37110 "McLaren GT 4.0 V8 (620 Hp) SSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 NV300 底盘驾驶室 L2，以及 NV300 Combi、Renault Trafic 客运版的 L1/L2 分支；客运版复用已有相同外廓尺寸组，不重复建组。官方资料确认两种车长及 1956 mm 不含后视镜宽度。
* 已闭合 NV250 Van：DCI 80 仅关联 L1；DCI 95、115 分拆为 L1/L2，并首次创建两个尺寸组。
* 已闭合 Tucson I LPG 4WD、S60 II 改款轿车和 Fiat 500 改款后三个尺寸组；i20 I 跨改款 Ktype 拆分后直接复用两个既有组。([engineindetail.com][1])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：114
* READY 映射：76
* PENDING 映射：38
* 已引用尺寸组：47
* 复用既有尺寸组：33
* 累计首次创建尺寸组：14
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138786	138786	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	HIGH	L2底盘驾驶室外廓。	READY
138787	138787	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	HIGH	L2底盘驾驶室外廓。	READY
138788_l1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138788_l2	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138789_l1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138789_l2	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138790_l1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138790_l2	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138796	138796	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	HIGH	LPG 4WD五门外廓。	READY
138797_prefl	138797	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	MEDIUM	改款前五门外廓分支。	READY
138797_facelift	138797	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	MEDIUM	改款后五门外廓分支。	READY
138823	138823	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
138824	138824	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
138844_l1	138844	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138844_l2	138844	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138845_l1	138845	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138845_l2	138845	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138847_l1	138847	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138847_l2	138847	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138879	138879	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	DCI 80的L1厢式车外廓。	READY
138880_l1	138880	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	L1厢式车分支。	READY
138880_l2	138880	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L2-01	HIGH	L2厢式车分支。	READY
138881_l1	138881	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	L1厢式车分支。	READY
138881_l2	138881	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L2-01	HIGH	L2厢式车分支。	READY
139160	139160	Hatchback	500 I	312	3	EU-FIAT-500-I-312-HATCHBACK-FACELIFT-01	HIGH	312改款后三门掀背车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	5399	1956	1951	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/fr/brochures/Brochures-vehicules/Brochure_NV300.pdf
EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	4325	1795	1720	Engine in Detail Hyundai Tucson 2.0 LPG GLS 4WD	https://www.engineindetail.com/pa/hyundai-tucson-2-0-lpg-gls-4wd-lpg-operation-2009
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data Volvo S60 II facelift 2.0 D4	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-2.0-d4-190hp-geartronic-31824
EU-NISSAN-NV250-I-VAN-L1-01	4282	1829	1844	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-VAN-L2-01	4666	1829	1836	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-FIAT-500-I-312-HATCHBACK-FACELIFT-01	3571	1627	1488	Fiat 500 official price and specification guide	https://www.fiat.co.uk/content/dam/fiat2023/uk/price-and-specification-guides/fiat-500/fiat-500.pdf
```

## 下一步优先处理

1. 闭合 Partner/Berlingo K9 的 Van、MPV 与 M/XL 分支，并处理剩余 NV250 客运 Ktype。
2. 批量处理 Caddy Alltrack IV 的标准轴距/Maxi 与 Van/MPV 分支。
3. 处理 Marco Polo、Sprinter、Crafter、Vario 的轴距及车顶高度分支。
4. 补齐 T-Roc Cabriolet、GLC facelift、Macan GTS、Challenger Redeye 等独立乘用车尺寸组。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/hyundai-tucson-2-0-lpg-gls-4wd-lpg-operation-2009?utm_source=chatgpt.com "Hyundai Tucson 2.0 LPG GLS 4WD (LPG operation) 2009 - Specs, Review & Tests"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 NV250 客运双排座 L2 分支：DCI 95、DCI 115 关联同一新尺寸组；DCI 80 的输入车身与官方动力配置仍存在冲突，继续保留待处理。
* Partner III 的 4 个 Ktype 已按 L1/L2 商用厢式车拆分，直接复用既有 K9 Van 尺寸组，不重复输出尺寸事实。([Charters Peugeot][1])
* 已闭合 Caddy Alltrack IV SWB 与 T-Roc Cabriolet；两组均使用官方资料中的不含后视镜宽度。
* 已闭合 Flying Spur III、Macan GTS、GLC facelift、Challenger Redeye 与 Huracán EVO RWD。([宾利汽车][2])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：118
* READY 映射：99
* PENDING 映射：19
* 已引用尺寸组：57
* 复用既有尺寸组：35
* 累计首次创建尺寸组：22
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138883	138883	MPV	NV250 I			EU-NISSAN-NV250-I-CREW-VAN-L2-01	MEDIUM	L2双排座客运外廓。	READY
138884	138884	MPV	NV250 I			EU-NISSAN-NV250-I-CREW-VAN-L2-01	MEDIUM	L2双排座客运外廓。	READY
138888	138888	SUV	GLC I facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	MEDIUM	X253改款五门SUV外廓。	READY
138894_l1	138894	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138894_l2	138894	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138897	138897	Convertible	T-Roc I	AC7	2	EU-VW-T-ROC-I-CABRIOLET-01	HIGH	双门敞篷外廓。	READY
138898	138898	Convertible	T-Roc I	AC7	2	EU-VW-T-ROC-I-CABRIOLET-01	HIGH	双门敞篷外廓。	READY
138902_l1	138902	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138902_l2	138902	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138903_l1	138903	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138903_l2	138903	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138905	138905	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代四门轿车外廓。	READY
138957_l1	138957	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138957_l2	138957	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138974	138974	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-III-LC-HELLCAT-REDEYE-COUPE-01	MEDIUM	Hellcat Redeye标准车身外廓。	READY
139008	139008	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-GTS-01	HIGH	GTS改款五门SUV外廓。	READY
139045	139045	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139073	139073	Coupe	Huracán EVO		2	EU-LAMBORGHINI-HURACAN-EVO-RWD-COUPE-01	MEDIUM	EVO RWD双门轿跑外廓。	READY
139133	139133	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139134	139134	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139135	139135	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139136	139136	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139137	139137	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV250-I-CREW-VAN-L2-01	4666	1829	1826	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	4655	1890	1644	AutoMoli Mercedes-Benz GLC SUV X253 facelift	https://www.automoli.com/en/vehicles/mercedes-benz/glc/glc-suv-x253-facelift-2019-7063/
EU-VW-T-ROC-I-CABRIOLET-01	4271	1811	1527	Volkswagen T-Roc Cabriolet official dimensions	https://www.vwpress.co.uk/assets/documents/original/32837-TRocCabrioletdimensions.pdf
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1988	1483	Bentley New Flying Spur official brochure	https://cdn.bentleymotors.com/downloads/en/brochure/global/flying-spur/BEN-FS-20-007_NewFlyingSpurCustomerBook_EU_v47_AW%28Digital%29.pdf
EU-DODGE-CHALLENGER-III-LC-HELLCAT-REDEYE-COUPE-01	5017	1923	1453	Edmunds 2020 Dodge Challenger SRT Hellcat Redeye specifications	https://www.edmunds.com/dodge/challenger/2020/srt-hellcat-redeye/features-specs/
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-GTS-01	4686	1935	1600	Porsche 2020 Macan official technical data	https://newsroom.porsche.com/dam/jcr%3A345230e8-84c0-47c8-9c9f-864353db1751/2020_Macan_Technical_Data.pdf
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4430	1793	1861	Volkswagen Caddy Trendline and Alltrack official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-LAMBORGHINI-HURACAN-EVO-RWD-COUPE-01	4520	1933	1165	Lamborghini Huracán EVO RWD official model page; Canadian Auto Review Huracán EVO RWD specifications	https://www.lamborghini.com/en-en/history/huracan-evo-rwd;https://canadianautoreview.ca/review-2020-lamborghini-huracan-evo-rwd
```

## 下一步优先处理

1. 批量闭合 8 个 Marco Polo Camper Ktype 的车顶及标准行驶高度。
2. 处理 Trafic 底盘驾驶室、Sprinter 4x4、Crafter Bus 和 Vario Bus 的轴距及车顶分支。
3. 处理 D-Max 底盘驾驶室、Berlingo K9、NV250 DCI 80 Bus 与 Ibiza Van/Hatchback。
4. 最后处理 NIO ES8 市场代际和 McLaren GT 不含后视镜宽度。

推进信号：CONTINUE

[1]: https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf?utm_source=chatgpt.com "ALL-NEW PEUGEOT PARTNER VAN"
[2]: https://cdn.bentleymotors.com/downloads/en/brochure/global/flying-spur/BEN-FS-20-007_NewFlyingSpurCustomerBook_EU_v47_AW%28Digital%29.pdf?utm_source=chatgpt.com "THE FLYING SPUR RANGE - Bentley Motors"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 6 个改款前 Marco Polo W447 Ktype。后驱和 4MATIC 均关联同一长轴露营车尺寸组；资料分别覆盖 200 CDI 后驱与 250 d 4MATIC，三维一致，宽度口径可由含镜宽度单独列示确认。([Engine In Detail][1])
* 已闭合 NIO ES8 544 hp 欧洲输入版本，对应第一代改款车型；官方手册明确区分车身宽度与含后视镜宽度。([蔚来][2])
* 已闭合 Renault Trafic III 145/170 hp 的 L2H1 平台式底盘驾驶室。官方资料同时列出该车身的三维及对应发动机版本。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：118
* READY 映射：108
* PENDING 映射：10
* 已引用尺寸组：60
* 复用既有尺寸组：35
* 累计首次创建尺寸组：25
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138982	138982	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138984	138984	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138985	138985	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138986	138986	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138987	138987	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138989	138989	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
139022	139022	SUV	ES8 I facelift		5	EU-NIO-ES8-I-FACELIFT-SUV-01	HIGH	第一代改款五门SUV外廓。	READY
139077	139077	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1平台式底盘驾驶室外廓。	READY
139078	139078	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1平台式底盘驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	5140	1928	1980	Engine in Detail Mercedes-Benz Marco Polo 200 CDI 2015;Engine in Detail Mercedes-Benz Marco Polo 250 d 4MATIC 2018	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-200-cdi-2015;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-250-d-4matic-7g-tronic-plus-2018
EU-NIO-ES8-I-FACELIFT-SUV-01	5022	1962	1756	NIO ES8 User Manual	https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	5248	1956	1953	Renault Nouveau Trafic official brochure	https://cdn.group.renault.com/ren/fr/product-plans/brochures/nouveau-trafic-vu/Brochure-Nouveau-Trafic-VU.pdf
```

## 下一步优先处理

1. 闭合 Marco Polo 300 CDI 改款车型与 McLaren GT 的不含后视镜宽度。
2. 处理 Crafter Bus、Sprinter 4x4、Vario Bus 的轴距和车顶分支。
3. 处理 NV250 DCI 80 Bus、Berlingo K9、D-Max I 底盘驾驶室与 Ibiza IV Van/Hatchback。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/mercedes-benz-marco-polo-200-cdi-2015 "Mercedes-Benz Marco Polo 200 CDI 2015 - Specs, Review & Tests"
[2]: https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html?utm_source=chatgpt.com "ES8 User Manual"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 已闭合 Marco Polo 300 CDI 后驱及 4MATIC 改款车型，共用 W447 改款露营车尺寸组。([Engine In Detail][1])
* 已将 Berlingo III BlueHDi 75 按 M、XL 厢式车分支拆分；官方资料明确列出两种车长、车高及 1848 mm 不含后视镜宽度。([雪铁龙新货车销售][2])
* 已闭合 McLaren GT；官方资料提供含镜及折叠镜宽度，另一个规格来源提供 1925 mm 车身宽度。([Di Uploads][3])

## 2. 当前批次进度

* 输入 Ktype：100
* 当前映射行：119
* READY 映射：113
* PENDING 映射：6
* 已引用尺寸组：64
* 复用既有尺寸组：35
* 累计首次创建尺寸组：29
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138959_m	138959	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-01	MEDIUM	M规格厢式车分支。	READY
138959_xl	138959	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	MEDIUM	XL规格厢式车分支。	READY
138980	138980	MPV	Marco Polo W447 facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	HIGH	改款长轴露营车外廓。	READY
138981	138981	MPV	Marco Polo W447 facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	HIGH	改款长轴露营车外廓。	READY
139047	139047	Coupe	McLaren GT		2	EU-MCLAREN-GT-I-COUPE-01	MEDIUM	双门轿跑外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1840	Citroën Berlingo Van official brochure	https://www.citroenvansales.com/wp-content/uploads/2024/05/Citroen-Berlingo-2019-Brochure-PV.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	4753	1848	1849	Citroën Berlingo Van official brochure	https://www.citroenvansales.com/wp-content/uploads/2024/05/Citroen-Berlingo-2019-Brochure-PV.pdf
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	5140	1928	1980	Engine in Detail Mercedes-Benz Marco Polo 300 d 4MATIC 2019	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2019
EU-MCLAREN-GT-I-COUPE-01	4683	1925	1213	McLaren GT official product brochure;CarsGuide McLaren GT 2019 dimensions	https://di-uploads-pod31.s3.us-east-1.amazonaws.com/mclarenpalmbeach/uploads/2021/03/gt-product-brochure-2020_en.pdf;https://www.carsguide.com.au/mclaren/gt/car-dimensions/2019
```

## 5. 下一步优先处理

1. 闭合 NV250 DCI 80 Bus 与 Ibiza IV 1.2 TDI 的车身和改款分支。
2. 处理 Crafter II 4MOTION Bus 与 Sprinter W906 4x4 的轴距、车顶组合。
3. 最后处理 D-Max I 底盘驾驶室及 Vario O 815 客车车身边界。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2019?utm_source=chatgpt.com "Mercedes-Benz Marco Polo 300 d 4MATIC 9G-TRONIC 2019 - Specs, Review & Tests"
[2]: https://www.citroenvansales.com/wp-content/uploads/2024/05/Citroen-Berlingo-2019-Brochure-PV.pdf "BERL_VAN_1911_GB_WEB.indd"
[3]: https://di-uploads-pod31.s3.us-east-1.amazonaws.com/mclarenpalmbeach/uploads/2021/03/gt-product-brochure-2020_en.pdf?utm_source=chatgpt.com "Scroll to explore"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* NV250 DCI 80 的官方配置仅对应 L1 Van；L2 Van 和 Crew Van 均不提供 80 dCi，因此将 Ktype `138882` 从候选客运分支修正为 L1 厢式车并复用既有尺寸组。
* D-Max I 2.5 TD 136 hp 四驱已拆分为 Space Cab 与 Double Cab 两个物理分支，分别闭合门数和三维。([汽车数据网][1])
* Ibiza IV 1.2 TDI 商用掀背车生产区间跨越改款节点，已按 6J5 改款前、改款后拆分并复用两个已有尺寸组。
* 本轮新增尺寸组 2 个；其余变化均为既有组关联。

## 2. 当前批次进度

* 输入 Ktype：100
* 当前映射行：121
* READY 映射：118
* PENDING 映射：3
* 已引用尺寸组：68
* 复用既有尺寸组：37
* 累计首次创建尺寸组：31
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138882	138882	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	MEDIUM	80 dCi仅对应L1厢式车；修正输入Bus边界。	READY
138829_spacecab	138829	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SPACE-CAB-4X4-01	MEDIUM	Space Cab四驱物理分支。	READY
138829_doublecab	138829	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-DOUBLE-CAB-4X4-01	MEDIUM	Double Cab四驱物理分支。	READY
139037_prefl	139037	Van	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	MEDIUM	6J5五门商用掀背改款前分支。	READY
139037_facelift	139037	Van	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	MEDIUM	6J5五门商用掀背改款后分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-I-SPACE-CAB-4X4-01	5030	1800	1715	Auto-Data Isuzu D-Max I 2.5 TD Space Cab 136 Hp	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-DOUBLE-CAB-4X4-01	5035	1800	1735	Auto-Data Isuzu D-Max I 2.5 TD Double Cab 136 Hp	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974
```

## 5. 下一步优先处理

1. Crafter II 4MOTION Bus：按实际提供的车长和车顶组合拆分并关联已有 Crafter 外廓组。
2. Sprinter W906 416 CDI 4x4 Van：闭合轴距、车长和车顶组合。
3. Vario O 815 Bus：确认原厂底盘与客车改装外廓边界；若 Ktype 覆盖多个客车车身，完整拆分对应物理分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974 "Isuzu D-Max I 2.5 TD Double Cab (136 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合最后 3 个阻塞项：

  * Crafter II 4MOTION Bus 按 L3H2、L3H3 两个客运外廓分支关联既有尺寸组。([大众汽车][1])
  * Sprinter W906 416 CDI 4x4 按长轴/超长轴及高顶/超高顶拆分为 4 个物理分支。([Dezo's Garage][2])
  * Vario O 815 采用完成整车外廓的 670.373、WB4250、U02 高顶全玻璃客车分支；670.374 Windlauf 为未完成底盘，不作为独立整车尺寸分支。([suw.cz][3])
* 已完成轻量机械收尾：两张表表头正确，125 个映射 `id` 唯一，75 个尺寸组唯一，所有引用闭合，三维、来源及 URL 均非空。
* 两个指定 TSV 文件已创建。

## 当前批次进度

* 输入 Ktype：100
* 最终 Ktype 映射：125
* READY 映射：125
* PENDING 映射：0
* 最终 DIMENSION_GROUP：75
* 孤立尺寸组：0
* 缺失映射引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138786	138786	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	HIGH	L2底盘驾驶室外廓。	READY
138787	138787	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	HIGH	L2底盘驾驶室外廓。	READY
138788_l1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138788_l2	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138789_l1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138789_l2	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138790_l1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L1H1-01	MEDIUM	L1客运车身分支。	READY
138790_l2	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-L2H1-01	MEDIUM	L2客运车身分支。	READY
138796	138796	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	HIGH	LPG 4WD五门外廓。	READY
138797_prefl	138797	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	MEDIUM	改款前五门外廓分支。	READY
138797_facelift	138797	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	MEDIUM	改款后五门外廓分支。	READY
138805	138805	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	V60 II五门旅行车外廓。	READY
138806	138806	Hatchback	Caliber I	PM	5	EU-DODGE-CALIBER-I-PM-HATCHBACK-01	HIGH	PM五门掀背车外廓。	READY
138807	138807	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40 II五门掀背车外廓。	READY
138808	138808	Hatchback	V40 II Cross Country		5	EU-VOLVO-V40-II-CROSS-COUNTRY-HATCHBACK-01	HIGH	Cross Country五门外廓。	READY
138809	138809	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40 II五门掀背车外廓。	READY
138811	138811	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country五门旅行车外廓。	READY
138812	138812	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country五门旅行车外廓。	READY
138814	138814	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country五门旅行车外廓。	READY
138816	138816	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country五门旅行车外廓。	READY
138819	138819	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车外廓。	READY
138820	138820	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车外廓。	READY
138821	138821	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车外廓。	READY
138823	138823	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
138824	138824	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
138825	138825	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country四门轿车外廓。	READY
138826	138826	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country四门轿车外廓。	READY
138829_spacecab	138829	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SPACE-CAB-4X4-01	MEDIUM	Space Cab四驱物理分支。	READY
138829_doublecab	138829	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-DOUBLE-CAB-4X4-01	MEDIUM	Double Cab四驱物理分支。	READY
138830	138830	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车外廓。	READY
138832	138832	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	HIGH	RS Q8专属外廓。	READY
138834	138834	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	4A2四门轿车外廓。	READY
138837	138837	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90 II五门SUV外廓。	READY
138839	138839	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II五门旅行车外廓。	READY
138844_l1	138844	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138844_l2	138844	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138845_l1	138845	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138845_l2	138845	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138846	138846	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	4KA五门Sportback外廓。	READY
138847_l1	138847	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	MEDIUM	L1客运车身分支。	READY
138847_l2	138847	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	MEDIUM	L2客运车身分支。	READY
138851	138851	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款五门SUV外廓。	READY
138853	138853	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款五门SUV外廓。	READY
138856_l3h2	138856	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2客运车身分支。	READY
138856_l3h3	138856	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3客运车身分支。	READY
138857	138857	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY改款前五门SUV外廓。	READY
138858	138858	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY改款前五门SUV外廓。	READY
138869	138869	SUV	2008 II	P24	5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	2008 II改款前五门SUV外廓。	READY
138873	138873	Sedan	A8 D5	4N	4	EU-AUDI-A8-D5-S8-SEDAN-01	HIGH	D5 S8四门轿车外廓。	READY
138876	138876	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
138877	138877	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
138879	138879	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	DCI 80的L1厢式车外廓。	READY
138880_l1	138880	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	L1厢式车分支。	READY
138880_l2	138880	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L2-01	HIGH	L2厢式车分支。	READY
138881_l1	138881	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	HIGH	L1厢式车分支。	READY
138881_l2	138881	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L2-01	HIGH	L2厢式车分支。	READY
138882	138882	Van	NV250 I			EU-NISSAN-NV250-I-VAN-L1-01	MEDIUM	80 dCi仅对应L1厢式车；修正输入Bus边界。	READY
138883	138883	MPV	NV250 I			EU-NISSAN-NV250-I-CREW-VAN-L2-01	MEDIUM	L2双排座客运外廓。	READY
138884	138884	MPV	NV250 I			EU-NISSAN-NV250-I-CREW-VAN-L2-01	MEDIUM	L2双排座客运外廓。	READY
138888	138888	SUV	GLC I facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	MEDIUM	X253改款五门SUV外廓。	READY
138892	138892	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS双门敞篷外廓。	READY
138894_l1	138894	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138894_l2	138894	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138897	138897	Convertible	T-Roc I	AC7	2	EU-VW-T-ROC-I-CABRIOLET-01	HIGH	双门敞篷外廓。	READY
138898	138898	Convertible	T-Roc I	AC7	2	EU-VW-T-ROC-I-CABRIOLET-01	HIGH	双门敞篷外廓。	READY
138902_l1	138902	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138902_l2	138902	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138903_l1	138903	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138903_l2	138903	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138905	138905	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代四门轿车外廓。	READY
138913_long_highroof	138913	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-LONG-HIGHROOF-4X4-01	HIGH	长轴高顶4x4分支。	READY
138913_long_superhighroof	138913	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-LONG-SUPERHIGHROOF-4X4-01	HIGH	长轴超高顶4x4分支。	READY
138913_extralong_highroof	138913	Van	Sprinter II	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-EXTRALONG-HIGHROOF-4X4-01	HIGH	超长轴高顶4x4分支。	READY
138913_extralong_superhighroof	138913	Van	Sprinter II	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-EXTRALONG-SUPERHIGHROOF-4X4-01	HIGH	超长轴超高顶4x4分支。	READY
138918	138918	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH	XV II五门SUV外廓。	READY
138940	138940	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY改款前五门SUV外廓。	READY
138950_xs	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-XS-01	MEDIUM	XS短车身客运分支。	READY
138950_m	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-M-01	MEDIUM	M中车身客运分支。	READY
138950_xl	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-COMBI-XL-01	MEDIUM	XL长车身客运分支。	READY
138957_l1	138957	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1厢式车分支。	READY
138957_l2	138957	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2厢式车分支。	READY
138959_m	138959	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-01	MEDIUM	M规格厢式车分支。	READY
138959_xl	138959	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	MEDIUM	XL规格厢式车分支。	READY
138972	138972	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	MEDIUM	L405改款标准轴距五门外廓。	READY
138974	138974	Coupe	Challenger III	LC	2	EU-DODGE-CHALLENGER-III-LC-HELLCAT-REDEYE-COUPE-01	MEDIUM	Hellcat Redeye标准车身外廓。	READY
138980	138980	MPV	Marco Polo W447 facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	HIGH	改款长轴露营车外廓。	READY
138981	138981	MPV	Marco Polo W447 facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	HIGH	改款长轴露营车外廓。	READY
138982	138982	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138984	138984	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138985	138985	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138986	138986	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138987	138987	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
138989	138989	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	HIGH	改款前长轴露营车外廓。	READY
139008	139008	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-GTS-01	HIGH	GTS改款五门SUV外廓。	READY
139012	139012	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	A238改款前双门敞篷外廓。	READY
139015_prefl	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	MEDIUM	W213改款前四门轿车分支。	READY
139015_facelift	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	MEDIUM	W213改款后四门轿车分支。	READY
139017	139017	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	i10 III五门掀背车外廓。	READY
139021	139021	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	i10 III五门掀背车外廓。	READY
139022	139022	SUV	ES8 I facelift		5	EU-NIO-ES8-I-FACELIFT-SUV-01	HIGH	第一代改款五门SUV外廓。	READY
139027	139027	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	C238改款前双门轿跑外廓。	READY
139031_3dr	139031	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	MEDIUM	Mk8三门掀背车分支。	READY
139031_5dr	139031	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	MEDIUM	Mk8五门掀背车分支。	READY
139036	139036	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18五门SUV外廓。	READY
139037_prefl	139037	Van	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	MEDIUM	6J5五门商用掀背改款前分支。	READY
139037_facelift	139037	Van	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	MEDIUM	6J5五门商用掀背改款后分支。	READY
139039	139039	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-U02-WB4250-01	MEDIUM	U02高顶全玻璃客车车身；670.374为未完成Windlauf底盘。	READY
139045	139045	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139047	139047	Coupe	McLaren GT		2	EU-MCLAREN-GT-I-COUPE-01	MEDIUM	双门轿跑外廓。	READY
139073	139073	Coupe	Huracán EVO		2	EU-LAMBORGHINI-HURACAN-EVO-RWD-COUPE-01	MEDIUM	EVO RWD双门轿跑外廓。	READY
139077	139077	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1平台式底盘驾驶室外廓。	READY
139078	139078	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1平台式底盘驾驶室外廓。	READY
139095	139095	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD五门旅行车外廓。	READY
139129	139129	Convertible	F8 Spider		2	EU-FERRARI-F8-SPIDER-CONVERTIBLE-01	HIGH	F8 Spider双门敞篷外廓。	READY
139133	139133	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139134	139134	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139135	139135	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139136	139136	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139137	139137	MPV	Caddy Alltrack IV	2K	5	EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	SWB五门Alltrack外廓。	READY
139151	139151	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS双门敞篷外廓。	READY
139153_3dr	139153	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	MEDIUM	Mk8三门掀背车分支。	READY
139153_5dr	139153	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	MEDIUM	Mk8五门掀背车分支。	READY
139154	139154	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前五门SUV外廓。	READY
139156	139156	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	EcoSport II五门SUV外廓。	READY
139160	139160	Hatchback	500 I	312	3	EU-FIAT-500-I-312-HATCHBACK-FACELIFT-01	HIGH	312改款后三门掀背车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4601-4700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV300-I-PLATFORM-CAB-L2-01	5399	1956	1951	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/fr/brochures/Brochures-vehicules/Brochure_NV300.pdf
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/fr/brochures/Brochures-vehicules/Brochure_NV300.pdf
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/fr/brochures/Brochures-vehicules/Brochure_NV300.pdf
EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	4325	1795	1720	Engine in Detail Hyundai Tucson 2.0 LPG GLS 4WD	https://www.engineindetail.com/pa/hyundai-tucson-2-0-lpg-gls-4wd-lpg-operation-2009
EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	3940	1710	1490	Auto-Data Hyundai i20 I (PB)	https://www.auto-data.net/en/hyundai-i20-model-1503
EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	3995	1710	1490	Auto-Data Hyundai i20 I (PB) facelift	https://www.auto-data.net/en/hyundai-i20-i-pb-facelift-2012-generation-4089
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Support V60 dimensions	https://www.volvocars.com/lb/support/car/v60/19w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-DODGE-CALIBER-I-PM-HATCHBACK-01	4415	1800	1535	Auto-Data Dodge Caliber 2.0 CRD	https://www.auto-data.net/en/dodge-caliber-2.0-16v-crd-140hp-2906
EU-VOLVO-V40-II-HATCHBACK-01	4369	1802	1420	Volvo Support V40 dimensions	https://www.volvocars.com/ie/support/car/v40/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V40-II-CROSS-COUNTRY-HATCHBACK-01	4370	1802	1458	Volvo Support V40 Cross Country dimensions	https://www.volvocars.com/en-th/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	4637	1866	1545	Volvo Support V60 Cross Country dimensions	https://www.volvocars.com/en-bh/support/car/v60-cross-country/article/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Support S90 dimensions	https://www.volvocars.com/en-bh/support/car/s90/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/871e942e897ca77dc0a801511788660a/
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data Volvo S60 II facelift 2.0 D4	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-2.0-d4-190hp-geartronic-31824
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539	Volvo Support S60 Cross Country dimensions	https://www.volvocars.com/de/support/car/s60-cross-country/article/18f77489f78f457dc0a801e800a04016/
EU-ISUZU-D-MAX-I-SPACE-CAB-4X4-01	5030	1800	1715	Auto-Data Isuzu D-Max I 2.5 TD Space Cab 136 Hp	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-DOUBLE-CAB-4X4-01	5035	1800	1735	Auto-Data Isuzu D-Max I 2.5 TD Double Cab 136 Hp	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974
EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	5012	1998	1694	Audi UK RS Q8 Technical Data	https://press.audi.co.uk/assets/documents/original/33583-AudiRSQ8UKTechDataMay2023.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Auto-Data Audi A6 C8 55 TFSI e quattro	https://www.auto-data.net/en/audi-a6-limousine-c8-55-tfsi-e-367hp-plug-in-hybrid-quattro-ultra-s-tronic-37900
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo Support XC90 dimensions	https://www.volvocars.com/en-bh/support/car/xc90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Support V90 dimensions	https://www.volvocars.com/lb/support/car/v90/2019/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/b39b95973dfe4ddcc0a80151496eb499/
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault Trafic official brochure	https://cdn.group.renault.com/ren/fr/product-plans/brochures/nouveau-trafic-vu/Brochure-Nouveau-Trafic-VU.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault Trafic official brochure	https://cdn.group.renault.com/ren/fr/product-plans/brochures/nouveau-trafic-vu/Brochure-Nouveau-Trafic-VU.pdf
EU-AUDI-A7-C8-4KA-SPORTBACK-01	4969	1908	1422	Audi A7 Sportback facts and figures	https://www.audi.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741	Auto-Data Audi Q7 II facelift	https://www.auto-data.net/en/audi-q7-ii-typ-4m-facelift-2019-generation-7195
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2021/july/crafter-online-brochure.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2021/july/crafter-online-brochure.pdf
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Auto-Data Audi Q5 II (FY)	https://www.auto-data.net/en/audi-q5-ii-fy-generation-5140
EU-PEUGEOT-2008-II-SUV-PREFL-01	4300	1770	1550	Auto-Data Peugeot 2008 II	https://www.auto-data.net/en/peugeot-2008-ii-generation-7149
EU-AUDI-A8-D5-S8-SEDAN-01	5179	1945	1474	Audi UK S8 Technical Data	https://press.audi.co.uk/assets/documents/original/16981-AudiS8TFSIquattrotiptronicUKTechnicalDataJuly2021.pdf
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Auto-Data Audi Q3 II (F3)	https://www.auto-data.net/en/audi-q3-ii-f3-generation-6577
EU-NISSAN-NV250-I-VAN-L1-01	4282	1829	1844	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-VAN-L2-01	4666	1829	1836	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-CREW-VAN-L2-01	4666	1829	1826	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	4655	1890	1644	AutoMoli Mercedes-Benz GLC SUV X253 facelift	https://www.automoli.com/en/vehicles/mercedes-benz/glc/glc-suv-x253-facelift-2019-7063/
EU-FERRARI-812-GTS-CONVERTIBLE-01	4693	1971	1278	Auto-Data Ferrari 812 GTS	https://www.auto-data.net/en/ferrari-812-gts-generation-7574
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	Peugeot Partner official brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	Peugeot Partner official brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-VW-T-ROC-I-CABRIOLET-01	4271	1811	1527	Volkswagen T-Roc Cabriolet official dimensions	https://www.vwpress.co.uk/assets/documents/original/32837-TRocCabrioletdimensions.pdf
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1988	1483	Bentley New Flying Spur official brochure	https://cdn.bentleymotors.com/downloads/en/brochure/global/flying-spur/BEN-FS-20-007_NewFlyingSpurCustomerBook_EU_v47_AW%28Digital%29.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-LONG-HIGHROOF-4X4-01	6961	1993	2910	Mercedes-Benz Sprinter official UK brochure	https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-LONG-SUPERHIGHROOF-4X4-01	6961	1993	3140	Mercedes-Benz Sprinter official UK brochure	https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-EXTRALONG-HIGHROOF-4X4-01	7361	1993	2900	Mercedes-Benz Sprinter official UK brochure	https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-EXTRALONG-SUPERHIGHROOF-4X4-01	7361	1993	3135	Mercedes-Benz Sprinter official UK brochure	https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf
EU-SUBARU-XV-II-SUV-01	4465	1805	1615	Auto-Data Subaru XV II	https://www.auto-data.net/en/subaru-xv-ii-generation-5442
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905	Auto-Data Citroën Jumpy III	https://www.auto-data.net/en/citroen-jumpy-iii-generation-4762
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890	Auto-Data Citroën Jumpy III	https://www.auto-data.net/en/citroen-jumpy-iii-generation-4762
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890	Auto-Data Citroën Jumpy III	https://www.auto-data.net/en/citroen-jumpy-iii-generation-4762
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1840	Citroën Berlingo Van official brochure	https://www.citroenvansales.com/wp-content/uploads/2024/05/Citroen-Berlingo-2019-Brochure-PV.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	4753	1848	1849	Citroën Berlingo Van official brochure	https://www.citroenvansales.com/wp-content/uploads/2024/05/Citroen-Berlingo-2019-Brochure-PV.pdf
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836	Auto-Data Range Rover IV facelift	https://www.auto-data.net/en/land-rover-range-rover-iv-facelift-2017-generation-5698
EU-DODGE-CHALLENGER-III-LC-HELLCAT-REDEYE-COUPE-01	5017	1923	1453	Edmunds 2020 Dodge Challenger SRT Hellcat Redeye specifications	https://www.edmunds.com/dodge/challenger/2020/srt-hellcat-redeye/features-specs/
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-FACELIFT-01	5140	1928	1980	Engine in Detail Mercedes-Benz Marco Polo 300 d 4MATIC 2019	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2019
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-PREFL-01	5140	1928	1980	Engine in Detail Mercedes-Benz Marco Polo 200 CDI 2015;Engine in Detail Mercedes-Benz Marco Polo 250 d 4MATIC 2018	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-200-cdi-2015;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-250-d-4matic-7g-tronic-plus-2018
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-GTS-01	4686	1935	1600	Porsche 2020 Macan official technical data	https://newsroom.porsche.com/dam/jcr%3A345230e8-84c0-47c8-9c9f-864353db1751/2020_Macan_Technical_Data.pdf
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabriolet A238 E 300 d	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300d-245hp-9g-tronic-33169
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-300-258hp-eq-boost-9g-tronic-38269
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300-258hp-eq-boost-9g-tronic-40876
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	Auto-Data Hyundai i10 III 1.2 MPi	https://www.auto-data.net/en/hyundai-i10-iii-1.2-mpi-84hp-37589
EU-NIO-ES8-I-FACELIFT-SUV-01	5022	1962	1756	NIO ES8 User Manual	https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 300 d	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-300d-245hp-9g-tronic-33166
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	4040	1735	1476	AutoData1 Ford Fiesta VIII dimensions	https://www.autodata1.com/en/car/ford/fiesta/fiesta-viii-10-ecoboost-95-hp-3d
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	4040	1735	1476	Auto-Data Ford Fiesta VIII (Mk8)	https://www.auto-data.net/en/ford-fiesta-viii-mk8-generation-5429
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Auto-Data Opel Grandland X	https://www.auto-data.net/en/opel-grandland-x-generation-5308
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-PREFL-01	4052	1693	1445	Auto-Data SEAT Ibiza IV 6J5	https://www.auto-data.net/en/seat-ibiza-iv-6j5-generation-2813
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-FACELIFT-01	4061	1693	1445	Auto-Data SEAT Ibiza IV facelift	https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-1.2-tsi-105hp-16880
EU-MERCEDES-BENZ-VARIO-W670-BUS-U02-WB4250-01	7210	2205	2820	Mercedes-Benz Vario official brochure;Mercedes-Benz Vario official price list	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://www.suw.cz/administrace/soubory_katalog/1334819026_cz_vario_cenik.pdf
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4430	1793	1861	Volkswagen Caddy Trendline and Alltrack official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-MCLAREN-GT-I-COUPE-01	4683	1925	1213	McLaren GT official product brochure;CarsGuide McLaren GT 2019 dimensions	https://di-uploads-pod31.s3.us-east-1.amazonaws.com/mclarenpalmbeach/uploads/2021/03/gt-product-brochure-2020_en.pdf;https://www.carsguide.com.au/mclaren/gt/car-dimensions/2019
EU-LAMBORGHINI-HURACAN-EVO-RWD-COUPE-01	4520	1933	1165	Lamborghini Huracán EVO RWD official model page;Canadian Auto Review Huracán EVO RWD specifications	https://www.lamborghini.com/en-en/history/huracan-evo-rwd;https://canadianautoreview.ca/review-2020-lamborghini-huracan-evo-rwd
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2H1-01	5248	1956	1953	Renault Nouveau Trafic official brochure	https://cdn.group.renault.com/ren/fr/product-plans/brochures/nouveau-trafic-vu/Brochure-Nouveau-Trafic-VU.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Auto-Data Kia Ceed III Sportswagon	https://www.auto-data.net/en/kia-ceed-iii-sportswagon-generation-6619
EU-FERRARI-F8-SPIDER-CONVERTIBLE-01	4611	1979	1206	Auto-Data Ferrari F8 Spider	https://www.auto-data.net/en/ferrari-f8-spider-3.9-v8-720hp-f1-dct-39252
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	Auto-Data BMW X5 G05	https://www.auto-data.net/en/bmw-x5-g05-generation-6555
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Auto-Data Ford EcoSport II	https://www.auto-data.net/en/ford-ecosport-ii-generation-4102
EU-FIAT-500-I-312-HATCHBACK-FACELIFT-01	3571	1627	1488	Fiat 500 official price and specification guide	https://www.fiat.co.uk/content/dam/fiat2023/uk/price-and-specification-guides/fiat-500/fiat-500.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4601-4700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2021/july/crafter-online-brochure.pdf "https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2021/july/crafter-online-brochure.pdf"
[2]: https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf "https://xr793.com/wp-content/uploads/2022/12/2014-Mercedes-Benz-Sprinter-Van-UK.pdf"
[3]: https://www.suw.cz/administrace/soubory_katalog/1334819026_cz_vario_cenik.pdf "https://www.suw.cz/administrace/soubory_katalog/1334819026_cz_vario_cenik.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4726 行）
- 累计尺寸组：dimension_groups_final.tsv（1810 行）

