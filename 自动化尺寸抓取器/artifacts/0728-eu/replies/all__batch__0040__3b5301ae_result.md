# 任务：all 第 3901-4000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0040__3b5301ae


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3901-4000 行

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
all 第 3901-4000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-AX-GT-HATCHBACK-3D-01	3495	1596	1340
EU-CITROEN-AX-PHASE-I-HATCHBACK-01	3495	1555	1355
EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	3495	1596	1340
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355
EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	3525	1555	1355
EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	3495	1596	1350
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-CITROEN-XM-Y3-HATCHBACK-01	4708	1794	1385
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1467
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	4260	1702	1451
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	4260	1705	1457
EU-CITROEN-ZX-N2-HATCHBACK-16V-01	4085	1718	1375
EU-CITROEN-ZX-N2-HATCHBACK-STD-01	4071	1702	1399
EU-CITROEN-ZX-N2-HATCHBACK-VOLCANE-01	4085	1707	1386
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ40-XJ81-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1377
EU-JAGUAR-XJ-SERIES-III-SEDAN-02	4959	1770	1372
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375
EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261
EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	5023	1798	1314
EU-JAGUAR-XJ-X306-XJR-SEDAN-SWB-01	5023	1798	1303
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457
EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	4972	1956	1865
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MAZDA-MX-3-EC-COUPE-3D-01	4220	1695	1310
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230
EU-MAZDA-MX-6-II-GE-COUPE-2D-01	4615	1750	1310
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395
EU-OPEL-CALIBRA-A-COUPE-3D-01	4492	1688	1320
EU-ROVER-100-XP-CONVERTIBLE-2D-01	3521	1550	1395
EU-ROVER-100-XP-HATCHBACK-3D-01	3521	1550	1377
EU-ROVER-100-XP-HATCHBACK-5D-01	3521	1550	1377
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390
EU-ROVER-200-SD3-SEDAN-FACELIFT-01	4160	1635	1393
EU-ROVER-200-SD3-SEDAN-PREFL-01	4156	1623	1378
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380
EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	3100	1440	1351
EU-ROVER-MINI-MK-VI-VII-HATCHBACK-2D-01	3054	1440	1340
EU-SKODA-FAVORIT-781-HATCHBACK-01	3815	1620	1415
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Citroën	Jumper i	1.9 TD	Bus	Frontantrieb	Diesel	68	92	Feb 1994	Apr 2002	2024-03-01	4035
Citroën	Jumper i	2.5 TD	Bus	Frontantrieb	Diesel	76	103	Aug 1994	Apr 2002	2024-03-01	4036
Citroën	Jumper i	2	Bus	Frontantrieb	Benzin	80	109	Feb 1994	Apr 2002	2024-03-01	4037
Citroën	Xm	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	97	132	May 1994	Oct 2000	2024-03-01	4038
Citroën	Xm	2.0 I 16V	Kombi	Frontantrieb	Benzin	97	132	May 1994	Oct 2000	2024-03-01	4039
Citroën	Xm	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	108	147	May 1994	Oct 2000	2024-03-01	4040
Mercedes-benz	G-Klasse	G 280 CDI	Geländewagen geschlossen	Allrad	Diesel	135	184	Apr 2009	-	2024-03-01	4041
Citroën	Xm	2.5 TD	Schrägheck	Frontantrieb	Diesel	95	129	May 1994	Oct 2000	2024-03-01	4042
Citroën	Xm	2.5 TD	Kombi	Frontantrieb	Diesel	95	129	May 1994	Oct 2000	2024-03-01	4043
Citroën	Xantia	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	110	150	Jun 1994	Jan 1998	2024-03-01	4044
Citroën	Xantia	1.9 D	Schrägheck	Frontantrieb	Diesel	50	68	Jun 1994	Jan 1998	2024-03-01	4045
Citroën	Xantia	1.9 D	Schrägheck	Frontantrieb	Diesel	51	69	Jun 1994	Jan 1998	2024-03-01	4046
Citroën	Zx	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	110	150	Jun 1994	Jun 1997	2024-03-01	4047
Citroën	Zx	1.9 D	Schrägheck	Frontantrieb	Diesel	50	68	Jul 1993	Jun 1997	2024-03-01	4048
Citroën	Zx	1.9 D	Kombi	Frontantrieb	Diesel	50	68	Jun 1994	Oct 1997	2024-03-01	4049
Citroën	Evasion	2.0 Turbo C.t.	Großraumlimousine	Frontantrieb	Benzin	108	147	Jun 1994	Jul 2002	2024-03-01	4050
Citroën	Evasion	2	Großraumlimousine	Frontantrieb	Benzin	89	121	Jun 1994	Jul 2002	2024-03-01	4051
Citroën	Jumper i	1.9 TD	Bus	Frontantrieb	Diesel	66	90	Aug 1994	Apr 2002	2024-03-01	4052
Citroën	Jumper i	2.5 D	Bus	Frontantrieb	Diesel	63	86	Aug 1994	Apr 2002	2024-03-01	4053
Citroën	Ax	15 D	Schrägheck	Frontantrieb	Diesel	40	54	Aug 1994	Dec 1997	2024-03-01	4054
Mazda	Xedos 9	2.0 24V	Stufenheck	Frontantrieb	Benzin	105	143	Aug 1993	Jan 2000	2024-03-01	4055
Mazda	Mx-5 i	1.8	Cabriolet	Heckantrieb	Benzin	96	130	Jan 1993	Apr 1998	2024-03-01	4056
Mazda	Mx-3	1.6 I	Coupe	Frontantrieb	Benzin	79	107	Nov 1993	Sep 1998	2024-03-01	4057
Mazda	Mx-3	1.8 I V6	Coupe	Frontantrieb	Benzin	95	129	Jan 1994	Oct 1997	2024-03-01	4058
Mazda	323 s v	1.3 16V	Stufenheck	Frontantrieb	Benzin	54	73	Aug 1994	Sep 1998	2024-03-01	4059
Mazda	323 c v	1.3 16V	Coupe	Frontantrieb	Benzin	54	73	Aug 1994	Sep 1998	2024-03-01	4060
Mazda	323 s v	1.5 16V	Stufenheck	Frontantrieb	Benzin	65	88	Aug 1994	Sep 1998	2024-03-01	4061
Mazda	323 c v	1.5 16V	Coupe	Frontantrieb	Benzin	65	88	Aug 1994	Sep 1998	2024-03-01	4062
Mazda	323 f v	2.0 24V	Schrägheck	Frontantrieb	Benzin	106	144	Aug 1994	Sep 1998	2024-03-01	4063
Mazda	323 f v	1.5 16V	Schrägheck	Frontantrieb	Benzin	65	88	Jul 1994	Sep 1998	2024-03-01	4064
Mazda	Xedos 6	1.6 16V	Stufenheck	Frontantrieb	Benzin	79	107	Apr 1994	Oct 1999	2024-03-01	4065
Mazda	Xedos 6	2.0 V6	Stufenheck	Frontantrieb	Benzin	103	140	Jun 1994	Oct 1999	2024-03-01	4066
Mazda	323 s v	1.8 16V	Stufenheck	Frontantrieb	Benzin	84	114	Aug 1994	Sep 1998	2024-03-01	4067
Mazda	323 c v	1.8 16V	Coupe	Frontantrieb	Benzin	84	114	Aug 1994	Sep 1998	2024-03-01	4068
Mazda	323 f v	1.8 16V	Schrägheck	Frontantrieb	Benzin	84	114	Aug 1994	Sep 1998	2024-03-01	4069
Mazda	626 iv	1.8 I	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1994	Apr 1997	2024-03-01	4070
Mazda	626 iv hatchback	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1994	Apr 1997	2024-03-01	4071
Mazda	626 iv hatchback	2.5 24V	Schrägheck	Frontantrieb	Benzin	120	163	Aug 1994	Apr 1997	2024-03-01	4072
Opel	Combo	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	33	45	Jul 1994	Oct 2001	2024-03-01	4073
Opel	Combo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Jul 1994	Oct 2001	2024-03-01	4074
Mazda	Mx-6	2.5 I 24V	Coupe	Frontantrieb	Benzin	120	163	Aug 1994	Feb 1997	2024-03-01	4075
Opel	Combo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	60	82	Jul 1994	Oct 2001	2024-03-01	4076
Opel	Combo	1.7 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	44	60	Jul 1994	Oct 2001	2024-03-01	4077
Opel	Tigra	1.4 16V	Coupe	Frontantrieb	Benzin	66	90	Jul 1994	Dec 2000	2024-03-01	4078
Opel	Tigra	1.6 16V	Coupe	Frontantrieb	Benzin	78	106	Jul 1994	Aug 1998	2024-03-01	4079
Rover	100	114	Cabriolet	Frontantrieb	Benzin	55	75	Apr 1994	Oct 1997	2024-03-01	4080
Rover	200	220 GSI	Coupe	Frontantrieb	Benzin	100	136	May 1994	Jun 1999	2024-03-01	4082
Rover	600	620 TI Vitesse	Stufenheck	Frontantrieb	Benzin	147	200	May 1994	Aug 1998	2024-03-01	4083
Land Rover	Range rover ii	2.5 D 4X4	Geländewagen geschlossen	Allrad	Diesel	100	136	Jul 1994	Mar 2002	2024-03-01	4084
Land Rover	Range rover ii	3.9 4X4	Geländewagen geschlossen	Allrad	Benzin	140	190	Jul 1994	Mar 2002	2024-03-01	4085
Land Rover	Range rover ii	4.6 4X4	Geländewagen geschlossen	Allrad	Benzin	165	224	Jul 1994	Mar 2002	2024-03-01	4086
Rover	Mini	1300	Cabriolet	Frontantrieb	Benzin	46	63	Sep 1992	Apr 1995	2024-03-01	4087
Skoda	Favorit	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Jan 1994	Sep 1994	2024-03-01	4088
Skoda	Favorit	1.3	Kombi	Frontantrieb	Benzin	50	68	Jan 1994	Jun 1995	2024-03-01	4089
Jaguar	Xj	4	Coupe	Heckantrieb	Benzin	171	233	Jul 1994	Mar 1996	2024-03-01	4090
Volvo	940	2.3	Kombi	Heckantrieb	Benzin	85	116	Aug 1992	Jul 1994	2024-03-01	4091
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	85	116	Aug 1992	Jul 1994	2024-03-01	4092
Opel	Astra f caravan	1.8 I 16V	Kombi	Frontantrieb	Benzin	85	116	Jul 1994	Jan 1998	2024-03-01	4093
Opel	Calibra a	2.0 I 16V 4X4	Coupe	Allrad	Benzin	100	136	Feb 1994	Jul 1997	2024-03-01	4094
Opel	Calibra a	2.0 I 16V	Coupe	Frontantrieb	Benzin	100	136	Feb 1994	Jul 1997	2024-03-01	4095
Honda	Jazz i	45 1.2	Schrägheck	Frontantrieb	Benzin	33	45	Feb 1984	Oct 1986	2024-03-01	4096
Honda	Jazz i	55 1.2	Schrägheck	Frontantrieb	Benzin	40	54	Sep 1984	Oct 1986	2024-03-01	4097
Honda	Jazz i	56 1.2	Schrägheck	Frontantrieb	Benzin	41	56	Oct 1983	Oct 1986	2024-03-01	4098
Honda	Quintet	1.6 EX	Schrägheck	Frontantrieb	Benzin	59	80	Feb 1980	Dec 1984	2024-03-01	4099
Honda	Civic i hatchback	1200	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1977	Dec 1980	2024-03-01	4100
Honda	Civic i	1300 L	Stufenheck	Frontantrieb	Benzin	33	45	Sep 1980	Sep 1983	2024-03-01	4101
Honda	Civic ii	1300 L	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1979	Sep 1983	2024-03-01	4102
Honda	Civic i	1300 L	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1980	Sep 1983	2024-03-01	4103
Honda	Civic i	1300 S	Stufenheck	Frontantrieb	Benzin	52	71	Oct 1979	Dec 1984	2024-03-01	4104
Nissan	Micra i	1	Schrägheck	Frontantrieb	Benzin	40	54	Dec 1982	May 1989	2024-03-01	4105
Honda	Civic ii	1300	Kombi	Frontantrieb	Benzin	44	60	Sep 1979	Sep 1983	2024-03-01	4106
Nissan	Micra i	1	Schrägheck	Frontantrieb	Benzin	37	50	Dec 1982	Dec 1989	2024-03-01	4107
Honda	Civic iii hatchback	1.2	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1984	Oct 1987	2024-03-01	4108
Nissan	Micra i	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1986	Jul 1992	2024-03-01	4109
Nissan	Micra i	1.2	Schrägheck	Frontantrieb	Benzin	40	54	Jul 1986	Jul 1992	2024-03-01	4110
Honda	Civic iii hatchback	1.3	Schrägheck	Frontantrieb	Benzin	52	71	Oct 1983	Oct 1987	2024-03-01	4111
Nissan	Micra ii	1.0 I 16V	Schrägheck	Frontantrieb	Benzin	40	54	Aug 1992	Jul 2000	2024-03-01	4112
Nissan	Cherry	1.2	Kombi	Frontantrieb	Benzin	38	52	Oct 1978	Jul 1981	2024-03-01	4113
Honda	Civic iv hatchback	1.4 L	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1987	Dec 1991	2024-03-01	4114
Honda	Civic iv	1.4 L	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1987	Dec 1989	2024-03-01	4115
Nissan	Cherry	1.3	Kombi	Frontantrieb	Benzin	44	60	Sep 1981	Dec 1983	2024-03-01	4116
Honda	Civic iii hatchback	1.5 GL	Schrägheck	Frontantrieb	Benzin	63	86	Oct 1983	Oct 1987	2024-03-01	4117
Nissan	Cherry	1.2	Schrägheck	Frontantrieb	Benzin	38	52	Aug 1978	Jul 1981	2024-03-01	4118
Nissan	Cherry	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1981	Sep 1982	2024-03-01	4119
Honda	Civic iii hatchback	1.5 GTI	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1986	Oct 1987	2024-03-01	4120
Nissan	Cherry	1.2	Coupe	Frontantrieb	Benzin	38	52	Aug 1978	Jul 1981	2024-03-01	4121
Honda	Civic iii hatchback	1.5 GT	Schrägheck	Frontantrieb	Benzin	74	101	Jan 1985	Oct 1987	2024-03-01	4122
Nissan	Cherry	1.3	Coupe	Frontantrieb	Benzin	44	60	Aug 1981	Sep 1982	2024-03-01	4123
Nissan	Cherry	1.3	Schrägheck	Frontantrieb	Benzin	44	60	May 1982	Oct 1986	2024-03-01	4124
Honda	Civic iv	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	80	109	Nov 1987	Sep 1991	2024-03-01	4125
Nissan	Cherry	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Nov 1983	Oct 1986	2024-03-01	4126
Nissan	Cherry	1.7 D	Schrägheck	Frontantrieb	Diesel	40	54	Oct 1982	Dec 1986	2024-03-01	4127
Honda	Civic iv hatchback	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	80	109	Oct 1987	Sep 1991	2024-03-01	4128
Honda	Civic iv hatchback	1.3 16V CAT	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1989	Sep 1991	2024-03-01	4129
Nissan	Sunny	1.4	Stufenheck	Heckantrieb	Benzin	48	65	Jan 1970	Feb 1982	2024-03-01	4130
Honda	Civic iv hatchback	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	69	94	Oct 1988	Sep 1991	2024-03-01	4131
Honda	Civic iv	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	69	94	Oct 1987	Sep 1991	2024-03-01	4132
Honda	Civic iv	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	81	110	Oct 1987	Sep 1991	2024-03-01	4133
Honda	Civic iv hatchback	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	81	110	Oct 1987	Sep 1991	2024-03-01	4134
Honda	Civic iv hatchback	1.6 I 16V Vtec	Schrägheck	Frontantrieb	Benzin	110	150	Oct 1989	Sep 1991	2024-03-01	4135


--- Round 1 / 首次发送 ---
## 更新点

* 复用历史缓存尺寸组完成 Citroën Xantia/ZX/AX、Mazda Xedos/MX/626、Rover、Jaguar、Volvo、Opel Calibra 等映射。
* 首次闭合 8 个尺寸组：Citroën XM Y4 两种车身、Mazda 323 BA 三种车身、Opel Combo B、Range Rover P38A、Škoda Favorit Forman。对应三维已按车身外廓集中核对。([汽车数据][1])
* 本轮新增 READY 映射 48 条，没有重复输出已存在尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：48
* PENDING 映射：52
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4038	4038	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4039	4039	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
4040	4040	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4042	4042	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4043	4043	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
4044	4044	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4045	4045	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4046	4046	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4047	4047	Hatchback	ZX N2	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-16V-01	HIGH		READY
4048	4048	Hatchback	ZX N2	N2		EU-CITROEN-ZX-N2-HATCHBACK-STD-01	MEDIUM	输入未区分三门或五门；复用标准外廓尺寸组。	READY
4049	4049	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	HIGH		READY
4054	4054	Hatchback	AX Phase II	ZA		EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	输入未区分三门或五门；复用Phase II标准外廓尺寸组。	READY
4055	4055	Sedan	Xedos 9	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH		READY
4056	4056	Convertible	MX-5 I	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH		READY
4057	4057	Coupe	MX-3	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH		READY
4058	4058	Coupe	MX-3	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH		READY
4059	4059	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4060	4060	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4061	4061	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4062	4062	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4063	4063	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4064	4064	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4065	4065	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4066	4066	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4067	4067	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4068	4068	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4069	4069	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4070	4070	Sedan	626 IV	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH		READY
4071	4071	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4072	4072	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4073	4073	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4074	4074	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4075	4075	Coupe	MX-6 II	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH		READY
4076	4076	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4077	4077	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4080	4080	Convertible	Rover 100	XP	2	EU-ROVER-100-XP-CONVERTIBLE-2D-01	HIGH		READY
4082	4082	Coupe	Rover 200 II	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
4083	4083	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4084	4084	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4085	4085	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4086	4086	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4088	4088	Hatchback	Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
4089	4089	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	HIGH		READY
4090	4090	Coupe	XJS Facelift	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
4091	4091	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
4092	4092	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
4094	4094	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH		READY
4095	4095	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396	Auto-Data Citroën XM Y4 2.0 i 16V	https://www.auto-data.net/en/citroen-xm-y4-2.0-i-16v-132hp-15037
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467	Auto-Data Citroën XM Break Y4 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xm-break-y4-2.1-turbo-d12-109hp-15046
EU-MAZDA-323-S-V-BA-SEDAN-4D-01	4340	1710	1420	Auto-Data Mazda 323 S V BA generation	https://www.auto-data.net/en/mazda-323-s-v-ba-generation-2351
EU-MAZDA-323-C-V-BA-COUPE-3D-01	4035	1710	1405	Auto-Data Mazda 323 C V BA generation	https://www.auto-data.net/en/mazda-323-c-v-ba-generation-2352
EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	4245	1695	1355	Auto-Data Mazda 323 F V BA generation	https://www.auto-data.net/en/mazda-323-f-v-ba-generation-2350
EU-OPEL-COMBO-B-VAN-01	4230	1686	1805	Auto-Data Opel Combo B generation	https://www.auto-data.net/en/opel-combo-b-generation-491
EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	4713	1889	1817	Automobile-Catalog 1995 Range Rover 2.5 DSE	https://www.automobile-catalog.com/car/1995/1398620/range_rover_2_5_dse_automatic.html
EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	4160	1620	1425	Auto-Data Škoda Favorit Forman 785 1.3	https://www.auto-data.net/en/skoda-favorit-forman-785-1.3-68hp-14294
```

## 下一步优先处理

1. 集中拆分 Citroën Jumper I Bus 的轴距和车顶外廓分支。
2. 解决 Citroën Evasion 两条 2.0 记录的三维差异，避免按发动机错误重复建组。
3. 核对 Opel Tigra A、Astra F Caravan、Rover Mini Cabriolet 和 Mercedes G 280 CDI。
4. 按代际集中处理 Honda Civic/Jazz/Quintet，以及 Nissan Micra/Cherry/Sunny。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-xm-y4-2.0-i-16v-132hp-15037?utm_source=chatgpt.com "Citroen XM (Y4) 2.0 i 16V (132 Hp) /Hatchback 1994"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 Citroën Evasion、Opel Tigra A、Rover Mini Cabriolet、Opel Astra F Caravan、Honda Jazz/Quintet/Civic、Nissan Micra/Cherry 共 13 个尺寸组。
* Nissan Micra K10 的 1.0 Ktype 跨越 1986 年外廓变化，按 `pre86` 与 `post86` 拆分；1.2 Ktype 直接关联改款后尺寸组。
* 本轮新增 READY 映射行 35 条，覆盖 33 个输入 Ktype。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：81
* READY 映射行：83
* PENDING 输入 Ktype：19
* 当前批次已确认尺寸组：41
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4050	4050	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4051	4051	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4078	4078	Coupe	Tigra A		3	EU-OPEL-TIGRA-A-COUPE-3D-01	HIGH		READY
4079	4079	Coupe	Tigra A		3	EU-OPEL-TIGRA-A-COUPE-3D-01	HIGH		READY
4087	4087	Convertible	Mini Cabrio		2	EU-ROVER-MINI-CABRIO-CONVERTIBLE-2D-01	HIGH		READY
4093	4093	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH	1994年款Caravan改款外廓。	READY
4096	4096	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4097	4097	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4098	4098	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4099	4099	Hatchback	Quintet	SU	5	EU-HONDA-QUINTET-SU-HATCHBACK-5D-01	HIGH		READY
4105_pre86	4105	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款前分支。	READY
4105_post86	4105	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款后分支。	READY
4107_pre86	4107	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款前分支。	READY
4107_post86	4107	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款后分支。	READY
4108	4108	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4109	4109	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	1986年7月起1.2版本对应改款后外廓。	READY
4110	4110	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	1986年7月起1.2版本对应改款后外廓。	READY
4111	4111	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4112	4112	Hatchback	Micra II	K11		EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4114	4114	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4115	4115	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4117	4117	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4120	4120	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4122	4122	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4124	4124	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4125	4125	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4126	4126	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4127	4127	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4128	4128	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4129	4129	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4131	4131	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4132	4132	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4133	4133	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4134	4134	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4135	4135	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714	Auto-Data Citroën Evasion 22	https://www.auto-data.net/en/citroen-evasion-22-generation-3297
EU-OPEL-TIGRA-A-COUPE-3D-01	3922	1604	1340	Automobile-Catalog 1994 Opel Tigra 1.4 16V	https://www.automobile-catalog.com/car/1994/2484575/opel_tigra_1_4_16v.html
EU-ROVER-MINI-CABRIO-CONVERTIBLE-2D-01	3100	1440	1350	Auto-Data Rover Mini MK I Cabrio	https://www.auto-data.net/en/rover-mini-mk-i-cabrio-generation-2448
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525	Auto-Data Opel Astra F Caravan facelift 1994	https://www.auto-data.net/en/opel-astra-f-caravan-facelift-1994-generation-6632
EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	3380	1570	1470	Auto-Data Honda Jazz AA	https://www.auto-data.net/en/honda-jazz-aa-generation-2589
EU-HONDA-QUINTET-SU-HATCHBACK-5D-01	4110	1615	1355	Automobile-Catalog 1980 Honda Quintet	https://www.automobile-catalog.com/car/1980/1087460/honda_quint_te.html
EU-HONDA-CIVIC-III-HATCHBACK-3D-01	3810	1635	1340	Auto-Data Honda Civic III Hatchback	https://www.auto-data.net/en/honda-civic-iii-hatchback-generation-2640
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330	Auto-Data Honda Civic IV Hatchback	https://www.auto-data.net/en/honda-civic-iv-hatchback-generation-2638
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360	Auto-Data Honda Civic IV Sedan	https://www.auto-data.net/en/honda-civic-iv-generation-2636
EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	3645	1560	1395	Automobile-Catalog 1982 Nissan Micra 1.0 DX	https://www.automobile-catalog.com/car/1982/2192765/nissan_micra_1_0_dx.html
EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	3760	1560	1395	Automobile-Catalog 1989 Nissan Micra 1.0 L	https://www.automobile-catalog.com/car/1989/2193215/nissan_micra_1_0_l.html
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440	Auto-Data Nissan Micra K11	https://www.auto-data.net/en/nissan-micra-k11-generation-208
EU-NISSAN-CHERRY-N12-HATCHBACK-01	3960	1620	1385	Auto-Data Nissan Cherry N12	https://www.auto-data.net/en/nissan-cherry-n12-generation-95
```

## 下一步优先处理

1. 拆分 Citroën Jumper I Bus 的轴距与车顶分支。
2. 确认 Mercedes-Benz G 280 CDI W461 的封闭车身边界。
3. 集中闭合 Honda Civic I、Civic II 的 Hatchback、Sedan、Wagon 外廓。
4. 集中处理 Nissan Cherry N10/VN10 的 Hatchback、Coupe、Wagon，以及跨年代范围异常的 Sunny Ktype 4130。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-evasion-22-generation-3297?utm_source=chatgpt.com "Citroen Evasion (22) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合早期 Honda Civic 4 个物理外廓、Nissan Cherry N10 六个改款前后外廓，以及 Nissan Sunny B310 轿车外廓，共新增 13 个 READY 输入 Ktype。
* Ktype `4113`、`4118`、`4121` 的生产区间覆盖 Cherry N10 Phase I 与 Phase II，且改款前后三维不同，已分别拆为 `prefl` 和 `facelift` 派生行。([汽车目录][1])
* Ktype `4130` 的输入生产区间异常，但 `1.4 / 65 hp / HBL310 / Sedan` 能锁定 Sunny B310 轿车；尺寸采用 Nissan 官方同代 HB310 轿车记录。([日产汽车官方网站][2])
* Jumper I Bus 五个 Ktype 与 G 280 CDI 暂未闭合，继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：94
* READY 映射行：99
* PENDING 输入 Ktype：6
* 已确认尺寸组：52
* 本轮首次创建尺寸组：11
* 剩余 PENDING：`4035`、`4036`、`4037`、`4041`、`4052`、`4053`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4100	4100	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-SB1-HATCHBACK-FACELIFT-01	MEDIUM	输入结束年月延伸至换代后；按1200三门SB1改款外廓。	READY
4101	4101	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入Model代际标注与生产期不一致；四门轿车对应Civic II SS。	READY
4102	4102	Hatchback	Civic II	SL	3	EU-HONDA-CIVIC-II-SL-HATCHBACK-3D-01	HIGH		READY
4103	4103	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入Model代际标注与生产期不一致；四门轿车对应Civic II SS。	READY
4104	4104	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入结束年月超出Civic II生产期；按1300四门SS外廓。	READY
4106	4106	Wagon	Civic II	ST	5	EU-HONDA-CIVIC-II-ST-WAGON-5D-01	HIGH		READY
4113_prefl	4113	Wagon	Cherry N10 Phase I	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4113_facelift	4113	Wagon	Cherry N10 Phase II	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4116	4116	Wagon	Cherry N10 Phase II	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	MEDIUM	输入结束年月晚于N10旅行车生产期；按1.3改款后外廓。	READY
4118_prefl	4118	Hatchback	Cherry N10 Phase I	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4118_facelift	4118	Hatchback	Cherry N10 Phase II	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4119	4119	Hatchback	Cherry N10 Phase II	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4121_prefl	4121	Coupe	Cherry N10 Phase I	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4121_facelift	4121	Coupe	Cherry N10 Phase II	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4123	4123	Coupe	Cherry N10 Phase II	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	HIGH		READY
4130	4130	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	输入生产年月异常；按明确的HBL310后驱轿车边界。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-I-SB1-HATCHBACK-FACELIFT-01	3560	1505	1325	Automobile-Catalog 1978 Honda Civic 1200 Hatchback Hondamatic	https://www.automobile-catalog.com/car/1978/1086110/honda_civic_1200_hatchback_hondamatic.html
EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	4090	1580	1350	Automobile-Catalog 1980 Honda Civic 4-Door Sedan EX	https://www.automobile-catalog.com/car/1980/1088735/honda_civic_4-door_sedan_ex.html
EU-HONDA-CIVIC-II-SL-HATCHBACK-3D-01	3760	1580	1350	Automobile-Catalog 1980 Honda Civic 1300 3-Door GL	https://www.automobile-catalog.com/car/1980/1088330/honda_civic_1300_3-door_gl.html
EU-HONDA-CIVIC-II-ST-WAGON-5D-01	3995	1580	1375	Automobile-Catalog 1981 Honda Civic GLS Wagon	https://www.automobile-catalog.com/car/1981/1089425/honda_civic_gls_wagon.html
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	3890	1600	1360	Automobile-Catalog 1979 Datsun Cherry 1.2 GL 3door	https://www.automobile-catalog.com/car/1979/24635/datsun_cherry_1_2.html
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	3960	1620	1360	Automobile-Catalog 1981 Datsun Cherry 1.3 GL 5door	https://www.automobile-catalog.com/car/1981/2105600/datsun_cherry_1_3_gl_5door_5-speed.html
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-I-01	3930	1600	1385	Automobile-Catalog 1979 Datsun Cherry 1.2 GL Wagon	https://www.automobile-catalog.com/car/1979/2105405/datsun_cherry_1_2_gl_wagon.html
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	3990	1620	1385	Automobile-Catalog 1981 Datsun Cherry 1.3 L Wagon	https://www.automobile-catalog.com/car/1981/2105675/datsun_cherry_1_3_l_wagon.html
EU-NISSAN-CHERRY-N10-COUPE-PHASE-I-01	3890	1620	1320	Automobile-Catalog 1979 Datsun Cherry 1.2 GL Coupe	https://www.automobile-catalog.com/car/1979/2105390/datsun_cherry_1_2_gl_coupe.html
EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	3960	1620	1320	Automobile-Catalog 1981 Datsun Cherry 1.3 Coupe	https://www.automobile-catalog.com/car/1981/2113595/datsun_cherry_1_3_coupe.html
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370	Nissan Heritage Collection DATSUN Sunny Sedan 1400SGL;Auto-Data Nissan Sunny 1.4 HBL310 65 Hp	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Sunny_Sedan_1400SGL.html;https://www.auto-data.net/en/nissan-sunny-140y-150y-1.4-hbl310-65hp-528
```

## 下一步优先处理

1. 按轴距、车顶高度和乘用 Bus 车身集中拆分 Jumper I 的 `4035`、`4036`、`4037`、`4052`、`4053`。
2. 确认 G 280 CDI `4041` 对应 W461 长轴五门 Station Wagon，还是同期三门封闭 Van；闭合其唯一物理分支或输出必要派生行。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/24635/datsun_cherry_1_2.html?utm_source=chatgpt.com "1979 Datsun Cherry 1.2 GL 3door Specs Review (38 kW / 52 PS / 51 hp) (since September 1979 for Europe )"
[2]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Sunny_Sedan_1400SGL.html "Nissan | Heritage Collection | DATSUN Sunny Sedan 1400SGL"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Citroën Jumper I Bus 已闭合短轴标准顶、中轴标准顶、中轴高顶三个稳定尺寸组；本轮仅首次核对并建组，后续 Ktype 直接复用。
* Ktype `4037` 的 2.0 80 kW Bus 已确认短轴与中轴两套不同外廓；31M 与资料中的标准高度 31MH 记录三维一致，因此共同引用中轴标准顶组。Ktype `4053` 的 2.5 D 63 kW 覆盖短轴标准顶、中轴标准顶和中轴高顶三套外廓。([gazoo.pl][1])
* Mercedes-Benz G 280 CDI 已锁定为 2009 年 W461 `Edition 30 PUR` 五门长轴车身，并闭合对应尺寸组。([marsClassic][2])
* Ktype `4035`、`4036` 已确认发动机和 230P 边界，但现有资料混合乘用 Bus 与封闭商用车配置，暂不猜测派生分支。([AUTODOC UK][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：98
* READY 映射行：106
* PENDING 输入 Ktype：2
* PENDING Ktype：`4035`、`4036`
* 已确认尺寸组：56
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4035	4035	MPV	Jumper I	230P	4		LOW	候选为短轴标准顶与中轴标准顶；现有记录尚未完全排除封闭商用车配置。	PENDING: 1.9 TD 68 kW乘用Bus物理分支未完全确认
4036	4036	MPV	Jumper I	230P	4		LOW	已确认2.5 TD 76 kW存在中轴车身，但乘用Bus的完整轴距和车顶分支尚未闭合。	PENDING: 2.5 TD 76 kW乘用Bus物理分支未完全确认
4037_swb_lowroof	4037	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	31C短轴标准顶物理外廓。	READY
4037_mwb_lowroof	4037	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	31M及相同三维的标准高度31MH物理外廓。	READY
4041	4041	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-EDITION-30-PUR-01	HIGH	2009年Edition 30 PUR五门长轴外廓。	READY
4052	4052	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	27C短轴标准顶物理外廓。	READY
4053_swb_lowroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	31C短轴标准顶物理外廓。	READY
4053_mwb_lowroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	31M及标准高度31MH物理外廓。	READY
4053_mwb_highroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	31MH中轴高顶物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-EDITION-30-PUR-01	4580	1700	2200	Mercedes-Benz Public Archive G 280 CDI Edition 30 PUR;Automobile-Catalog 2009 Mercedes-Benz G 280 CDI Edition 30 PUR	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/G-280-CDI-Edition-30-PUR-Off-Roader---W-461.xhtml?oid=1142062;https://www.automobile-catalog.com/car/2009/1567520/mercedes-benz_g_280_cdi_edition_30_pur.html
```

## 下一步优先处理

1. 核对 Ktype `4035` 的 1.9 TD 68 kW 在 230P 乘用 Bus 中是否同时覆盖 31C 与 31M，排除同发动机封闭商用车记录。
2. 核对 Ktype `4036` 的 2.5 TD 76 kW 乘用 Bus 是否只有中轴标准顶，或还覆盖短轴及高顶分支。
3. 两条映射闭合后立即执行一次机械检查，并输出两张完整 TSV、指定 sandbox 下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://gazoo.pl/samochody/citroen/citroen-jumper/ "Dane techniczne Citroen Jumper, wszystkie wersje, rodzaje, typy, generacje, silniki - gazoo.pl"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/G-280-CDI-Edition-30-PUR-Off-Roader---W-461.xhtml?oid=1142062 "G 280 CDI \"Edition 30 PUR\", Off-Roader - W 461"
[3]: https://www.autodoc.co.uk/car-parts/track-rod-end-10703/citroen/relay/jumper-bus-230p/4035-1-9-td?utm_source=chatgpt.com "Citroen Jumper 230 1.9 TD Track rod end - 92 hp Diesel 68 kW ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后两个 PENDING Ktype 已闭合：`4035` 关联既有短轴标准顶组；`4036` 拆分为短轴标准顶、中轴标准顶和中轴高顶三个物理分支。车型身份分别对应 Jumper I Bus 1.9 TD 68 kW 与 2.5 TD 76 kW。([ak24parts.com][1])
* 已完成一次机械收尾检查：表头正确、110 个 `id` 唯一、56 个尺寸组唯一、100 个输入 Ktype 全覆盖、映射引用全部闭合、无孤立尺寸组、三维及来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* 最终映射行：110
* PENDING：0
* 最终尺寸组：56
* 机械检查：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4035	4035	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	27C与31C乘用Bus共用短轴标准顶外廓。	READY
4036_swb_lowroof	4036	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	27C/31C短轴标准顶物理外廓。	READY
4036_mwb_lowroof	4036	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	31M中轴标准顶物理外廓。	READY
4036_mwb_highroof	4036	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	31MH中轴高顶物理外廓。	READY
4037_swb_lowroof	4037	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	31C短轴标准顶物理外廓。	READY
4037_mwb_lowroof	4037	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	31M中轴标准顶物理外廓。	READY
4038	4038	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4039	4039	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
4040	4040	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4041	4041	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-EDITION-30-PUR-01	HIGH	2009年Edition 30 PUR五门长轴外廓。	READY
4042	4042	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
4043	4043	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
4044	4044	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4045	4045	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4046	4046	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH		READY
4047	4047	Hatchback	ZX N2	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-16V-01	HIGH		READY
4048	4048	Hatchback	ZX N2	N2		EU-CITROEN-ZX-N2-HATCHBACK-STD-01	MEDIUM	输入未区分三门或五门；复用标准外廓尺寸组。	READY
4049	4049	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	HIGH		READY
4050	4050	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4051	4051	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4052	4052	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	27C短轴标准顶物理外廓。	READY
4053_swb_lowroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	31C短轴标准顶物理外廓。	READY
4053_mwb_lowroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	31M中轴标准顶物理外廓。	READY
4053_mwb_highroof	4053	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	31MH中轴高顶物理外廓。	READY
4054	4054	Hatchback	AX Phase II	ZA		EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	输入未区分三门或五门；复用Phase II标准外廓尺寸组。	READY
4055	4055	Sedan	Xedos 9	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH		READY
4056	4056	Convertible	MX-5 I	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH		READY
4057	4057	Coupe	MX-3	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH		READY
4058	4058	Coupe	MX-3	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH		READY
4059	4059	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4060	4060	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4061	4061	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4062	4062	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4063	4063	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4064	4064	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4065	4065	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4066	4066	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4067	4067	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4068	4068	Coupe	323 C V	BA	3	EU-MAZDA-323-C-V-BA-COUPE-3D-01	MEDIUM	323 C V三门车身按输入BodyStyle归类为Coupe。	READY
4069	4069	Hatchback	323 F V	BA	5	EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	HIGH		READY
4070	4070	Sedan	626 IV	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH		READY
4071	4071	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4072	4072	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4073	4073	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4074	4074	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4075	4075	Coupe	MX-6 II	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH		READY
4076	4076	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4077	4077	Van	Combo B			EU-OPEL-COMBO-B-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine写法；按Combo B统一封闭厢式外廓。	READY
4078	4078	Coupe	Tigra A		3	EU-OPEL-TIGRA-A-COUPE-3D-01	HIGH		READY
4079	4079	Coupe	Tigra A		3	EU-OPEL-TIGRA-A-COUPE-3D-01	HIGH		READY
4080	4080	Convertible	Rover 100	XP	2	EU-ROVER-100-XP-CONVERTIBLE-2D-01	HIGH		READY
4082	4082	Coupe	Rover 200 II	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
4083	4083	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4084	4084	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4085	4085	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4086	4086	SUV	Range Rover II	P38A	5	EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	HIGH		READY
4087	4087	Convertible	Mini Cabrio		2	EU-ROVER-MINI-CABRIO-CONVERTIBLE-2D-01	HIGH		READY
4088	4088	Hatchback	Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
4089	4089	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	HIGH		READY
4090	4090	Coupe	XJS Facelift	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
4091	4091	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
4092	4092	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
4093	4093	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH	1994年款Caravan改款外廓。	READY
4094	4094	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH		READY
4095	4095	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH		READY
4096	4096	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4097	4097	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4098	4098	Hatchback	Jazz AA	AA	3	EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	HIGH		READY
4099	4099	Hatchback	Quintet	SU	5	EU-HONDA-QUINTET-SU-HATCHBACK-5D-01	HIGH		READY
4100	4100	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-SB1-HATCHBACK-FACELIFT-01	MEDIUM	输入结束年月延伸至换代后；按1200三门SB1改款外廓。	READY
4101	4101	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入Model代际标注与生产期不一致；四门轿车对应Civic II SS。	READY
4102	4102	Hatchback	Civic II	SL	3	EU-HONDA-CIVIC-II-SL-HATCHBACK-3D-01	HIGH		READY
4103	4103	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入Model代际标注与生产期不一致；四门轿车对应Civic II SS。	READY
4104	4104	Sedan	Civic II	SS	4	EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	MEDIUM	输入结束年月超出Civic II生产期；按1300四门SS外廓。	READY
4105_pre86	4105	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款前分支。	READY
4105_post86	4105	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款后分支。	READY
4106	4106	Wagon	Civic II	ST	5	EU-HONDA-CIVIC-II-ST-WAGON-5D-01	HIGH		READY
4107_pre86	4107	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款前分支。	READY
4107_post86	4107	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	Ktype跨越1986年外廓变化；本行为改款后分支。	READY
4108	4108	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4109	4109	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	1986年7月起1.2版本对应改款后外廓。	READY
4110	4110	Hatchback	Micra I	K10		EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	HIGH	1986年7月起1.2版本对应改款后外廓。	READY
4111	4111	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4112	4112	Hatchback	Micra II	K11		EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4113_prefl	4113	Wagon	Cherry N10 Phase I	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4113_facelift	4113	Wagon	Cherry N10 Phase II	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4114	4114	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4115	4115	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4116	4116	Wagon	Cherry N10 Phase II	VN10	5	EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	MEDIUM	输入结束年月晚于N10旅行车生产期；按1.3改款后外廓。	READY
4117	4117	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4118_prefl	4118	Hatchback	Cherry N10 Phase I	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4118_facelift	4118	Hatchback	Cherry N10 Phase II	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4119	4119	Hatchback	Cherry N10 Phase II	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4120	4120	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4121_prefl	4121	Coupe	Cherry N10 Phase I	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-I-01	HIGH	Ktype跨越N10外廓改款；本行为改款前分支。	READY
4121_facelift	4121	Coupe	Cherry N10 Phase II	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	HIGH	Ktype跨越N10外廓改款；本行为改款后分支。	READY
4122	4122	Hatchback	Civic III		3	EU-HONDA-CIVIC-III-HATCHBACK-3D-01	HIGH		READY
4123	4123	Coupe	Cherry N10 Phase II	N10	3	EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	HIGH		READY
4124	4124	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4125	4125	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4126	4126	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4127	4127	Hatchback	Cherry N12	N12		EU-NISSAN-CHERRY-N12-HATCHBACK-01	HIGH	输入未区分三门或五门；两者使用同一外廓尺寸。	READY
4128	4128	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4129	4129	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4130	4130	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	输入生产年月异常；按明确的HBL310后驱轿车边界。	READY
4131	4131	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4132	4132	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4133	4133	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH		READY
4134	4134	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
4135	4135	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3901-4000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Gazoo Citroën Jumper I Kombi technical data	https://gazoo.pl/samochody/citroen/citroen-jumper/
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396	Auto-Data Citroën XM Y4 2.0 i 16V	https://www.auto-data.net/en/citroen-xm-y4-2.0-i-16v-132hp-15037
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467	Auto-Data Citroën XM Break Y4 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xm-break-y4-2.1-turbo-d12-109hp-15046
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-EDITION-30-PUR-01	4580	1700	2200	Mercedes-Benz Public Archive G 280 CDI Edition 30 PUR;Automobile-Catalog 2009 Mercedes-Benz G 280 CDI Edition 30 PUR	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/G-280-CDI-Edition-30-PUR-Off-Roader---W-461.xhtml?oid=1142062;https://www.automobile-catalog.com/car/2009/1567520/mercedes-benz_g_280_cdi_edition_30_pur.html
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387	Auto-Data Citroën Xantia X1 2.0i 16V	https://www.auto-data.net/en/citroen-xantia-x1-2.0i-16v-152hp-14965
EU-CITROEN-ZX-N2-HATCHBACK-16V-01	4085	1718	1375	Automobile-Catalog Citroën ZX 16V	https://www.automobile-catalog.com/car/1995/2031995/citroen_zx_16v.html
EU-CITROEN-ZX-N2-HATCHBACK-STD-01	4071	1702	1399	Automobile-Catalog Citroën ZX Avantage 1.9 D	https://www.automobile-catalog.com/car/1993/542525/citroen_zx_avantage_1_9_d_automatic.html
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	4260	1705	1457	Auto-Data Citroën ZX model data	https://www.auto-data.net/en/citroen-zx-model-1698
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714	Auto-Data Citroën Evasion 22	https://www.auto-data.net/en/citroen-evasion-22-generation-3297
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355	Automobile-Catalog Citroën AX Debut 1.5 Diesel	https://www.automobile-catalog.com/car/1995/1451165/citroen_ax_debut_1_5_diesel.html
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395	Automobile-Catalog Mazda Xedos 9 2.0i V6	https://www.automobile-catalog.com/car/1995/1653320/mazda_xedos_9_2_0i_v6.html
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230	Auto-Data Mazda MX-5 I NA 1.8	https://www.auto-data.net/en/mazda-mx-5-i-na-1.8-130hp-11263
EU-MAZDA-MX-3-EC-COUPE-3D-01	4220	1695	1310	Automobile-Catalog Mazda MX-3 16V	https://www.automobile-catalog.com/car/1996/1648595/mazda_mx-3_16v.html
EU-MAZDA-323-S-V-BA-SEDAN-4D-01	4340	1710	1420	Auto-Data Mazda 323 S V BA generation	https://www.auto-data.net/en/mazda-323-s-v-ba-generation-2351
EU-MAZDA-323-C-V-BA-COUPE-3D-01	4035	1710	1405	Auto-Data Mazda 323 C V BA generation	https://www.auto-data.net/en/mazda-323-c-v-ba-generation-2352
EU-MAZDA-323-F-V-BA-HATCHBACK-5D-01	4245	1695	1355	Auto-Data Mazda 323 F V BA generation	https://www.auto-data.net/en/mazda-323-f-v-ba-generation-2350
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355	Automobile-Catalog Mazda Xedos 6 2.0i V6	https://www.automobile-catalog.com/car/1997/1652825/mazda_xedos_6_2_0i_v6.html
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400	Auto-Data Mazda 626 IV GE 1.8 i	https://www.auto-data.net/en/mazda-626-iv-ge-1.8-i-105hp-11298
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390	Auto-Data Mazda 626 IV Hatchback GE 2.5 24V	https://www.auto-data.net/en/mazda-626-iv-hatchback-ge-2.5-24v-165hp-11287
EU-OPEL-COMBO-B-VAN-01	4230	1686	1805	Auto-Data Opel Combo B generation	https://www.auto-data.net/en/opel-combo-b-generation-491
EU-MAZDA-MX-6-II-GE-COUPE-2D-01	4615	1750	1310	Auto-Data Mazda MX-6 GE6 generation	https://www.auto-data.net/en/mazda-mx-6-ge6-generation-2395
EU-OPEL-TIGRA-A-COUPE-3D-01	3922	1604	1340	Automobile-Catalog 1994 Opel Tigra 1.4 16V	https://www.automobile-catalog.com/car/1994/2484575/opel_tigra_1_4_16v.html
EU-ROVER-100-XP-CONVERTIBLE-2D-01	3521	1550	1395	Auto-Data Rover 100 Cabrio XP 114	https://www.auto-data.net/en/rover-100-cabrio-xp-114-75hp-11496
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370	Auto-Data Rover 200 Coupe XW generation	https://www.auto-data.net/en/rover-200-coupe-xw-generation-2450
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380	Auto-Data Rover 600 RH 620 Ti Vitesse	https://www.auto-data.net/en/rover-600-rh-620-ti-vitesse-200hp-11593
EU-LAND-ROVER-RANGE-ROVER-II-P38A-SUV-01	4713	1889	1817	Automobile-Catalog 1995 Range Rover 2.5 DSE	https://www.automobile-catalog.com/car/1995/1398620/range_rover_2_5_dse_automatic.html
EU-ROVER-MINI-CABRIO-CONVERTIBLE-2D-01	3100	1440	1350	Auto-Data Rover Mini MK I Cabrio	https://www.auto-data.net/en/rover-mini-mk-i-cabrio-generation-2448
EU-SKODA-FAVORIT-781-HATCHBACK-01	3815	1620	1415	Auto-Data Škoda Favorit 781 1.3	https://www.auto-data.net/en/skoda-favorit-781-1.3-781-68hp-14284
EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	4160	1620	1425	Auto-Data Škoda Favorit Forman 785 1.3	https://www.auto-data.net/en/skoda-favorit-forman-785-1.3-68hp-14294
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254	Auto-Data Jaguar XJS Coupe 4.0	https://www.auto-data.net/en/jaguar-xjs-coupe-4.0-233hp-224
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435	Auto-Data Volvo 940 Combi 945 generation	https://www.auto-data.net/en/volvo-940-combi-945-generation-1938
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425	Auto-Data Volvo 940 944 generation	https://www.auto-data.net/en/volvo-940-944-generation-1937
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525	Auto-Data Opel Astra F Caravan facelift 1994	https://www.auto-data.net/en/opel-astra-f-caravan-facelift-1994-generation-6632
EU-OPEL-CALIBRA-A-COUPE-3D-01	4492	1688	1320	Auto-Data Opel Calibra facelift 1994 2.0 16V ECOTEC	https://www.auto-data.net/en/opel-calibra-facelift-1994-2.0-16v-ecotec-136hp-2545
EU-HONDA-JAZZ-AA-HATCHBACK-3D-01	3380	1570	1470	Auto-Data Honda Jazz AA generation	https://www.auto-data.net/en/honda-jazz-aa-generation-2589
EU-HONDA-QUINTET-SU-HATCHBACK-5D-01	4110	1615	1355	Automobile-Catalog 1980 Honda Quintet	https://www.automobile-catalog.com/car/1980/1087460/honda_quint_te.html
EU-HONDA-CIVIC-I-SB1-HATCHBACK-FACELIFT-01	3560	1505	1325	Automobile-Catalog 1978 Honda Civic 1200 Hatchback Hondamatic	https://www.automobile-catalog.com/car/1978/1086110/honda_civic_1200_hatchback_hondamatic.html
EU-HONDA-CIVIC-II-SS-SEDAN-4D-01	4090	1580	1350	Automobile-Catalog 1980 Honda Civic 4-Door Sedan EX	https://www.automobile-catalog.com/car/1980/1088735/honda_civic_4-door_sedan_ex.html
EU-HONDA-CIVIC-II-SL-HATCHBACK-3D-01	3760	1580	1350	Automobile-Catalog 1980 Honda Civic 1300 3-Door GL	https://www.automobile-catalog.com/car/1980/1088330/honda_civic_1300_3-door_gl.html
EU-NISSAN-MICRA-I-K10-HATCHBACK-PRE86-01	3645	1560	1395	Automobile-Catalog 1982 Nissan Micra 1.0 DX	https://www.automobile-catalog.com/car/1982/2192765/nissan_micra_1_0_dx.html
EU-NISSAN-MICRA-I-K10-HATCHBACK-POST86-01	3760	1560	1395	Automobile-Catalog 1989 Nissan Micra 1.0 L	https://www.automobile-catalog.com/car/1989/2193215/nissan_micra_1_0_l.html
EU-HONDA-CIVIC-II-ST-WAGON-5D-01	3995	1580	1375	Automobile-Catalog 1981 Honda Civic GLS Wagon	https://www.automobile-catalog.com/car/1981/1089425/honda_civic_gls_wagon.html
EU-HONDA-CIVIC-III-HATCHBACK-3D-01	3810	1635	1340	Auto-Data Honda Civic III Hatchback generation	https://www.auto-data.net/en/honda-civic-iii-hatchback-generation-2640
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440	Auto-Data Nissan Micra K11 generation	https://www.auto-data.net/en/nissan-micra-k11-generation-208
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-I-01	3930	1600	1385	Automobile-Catalog 1979 Datsun Cherry 1.2 GL Wagon	https://www.automobile-catalog.com/car/1979/2105405/datsun_cherry_1_2_gl_wagon.html
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	3990	1620	1385	Automobile-Catalog 1981 Datsun Cherry 1.3 L Wagon	https://www.automobile-catalog.com/car/1981/2105675/datsun_cherry_1_3_l_wagon.html
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330	Auto-Data Honda Civic IV Hatchback generation	https://www.auto-data.net/en/honda-civic-iv-hatchback-generation-2638
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360	Auto-Data Honda Civic IV Sedan generation	https://www.auto-data.net/en/honda-civic-iv-generation-2636
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	3890	1600	1360	Automobile-Catalog 1979 Datsun Cherry 1.2 GL 3-door	https://www.automobile-catalog.com/car/1979/24635/datsun_cherry_1_2.html
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	3960	1620	1360	Automobile-Catalog 1981 Datsun Cherry 1.3 GL 5-door	https://www.automobile-catalog.com/car/1981/2105600/datsun_cherry_1_3_gl_5door_5-speed.html
EU-NISSAN-CHERRY-N10-COUPE-PHASE-I-01	3890	1620	1320	Automobile-Catalog 1979 Datsun Cherry 1.2 GL Coupe	https://www.automobile-catalog.com/car/1979/2105390/datsun_cherry_1_2_gl_coupe.html
EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	3960	1620	1320	Automobile-Catalog 1981 Datsun Cherry 1.3 Coupe	https://www.automobile-catalog.com/car/1981/2113595/datsun_cherry_1_3_coupe.html
EU-NISSAN-CHERRY-N12-HATCHBACK-01	3960	1620	1385	Auto-Data Nissan Cherry N12 generation	https://www.auto-data.net/en/nissan-cherry-n12-generation-95
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370	Nissan Heritage Collection DATSUN Sunny Sedan 1400SGL;Auto-Data Nissan Sunny 1.4 HBL310	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Sunny_Sedan_1400SGL.html;https://www.auto-data.net/en/nissan-sunny-140y-150y-1.4-hbl310-65hp-528
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3901-4000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ak24parts.com/en/spareparts/4035/jumper-i-bus-230p-1-9-td?srsltid=AfmBOopzwbBSVHQchXnVTgcNe6f-b-k7m5qcOG5kgQ8MDgPK-YXOUBPB "https://www.ak24parts.com/en/spareparts/4035/jumper-i-bus-230p-1-9-td?srsltid=AfmBOopzwbBSVHQchXnVTgcNe6f-b-k7m5qcOG5kgQ8MDgPK-YXOUBPB"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3901-4000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3901-4000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5312 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1569 行）

