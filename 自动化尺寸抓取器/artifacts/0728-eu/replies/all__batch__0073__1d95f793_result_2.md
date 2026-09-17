# 任务：all 第 7201-7300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0073__1d95f793


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7201-7300 行

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
all 第 7201-7300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425
EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330
EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	4260	1664	1330
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318
EU-AUDI-A8-D2-SEDAN-FACELIFT-01	5034	1880	1438
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	4910	1860	1454
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-BMW-6-F13-COUPE-01	4894	1894	1369
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420
EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	4256	1662	1393
EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	4482	1662	1393
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	3780	1620	1390
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-GTI-01	3750	1620	1390
EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	4085	1620	1390
EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	3295	1395	1435
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	3864	1716	1721
EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	3959	1716	1721
EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	3957	1716	1721
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904
EU-FIAT-FIORINO-I-VAN-01	3635	1690	1810
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460
EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	4200	1790	1624
EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	4251	1790	1625
EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	4240	1790	1623
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385
EU-LANCIA-THEMA-I-8-32-SEDAN-01	4590	1733	1420
EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	4590	1752	1433
EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	4590	1758	1435
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435
EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	4590	1755	1440
EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	4605	1752	1435
EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	3995	1670	1400
EU-MERCEDES-BENZ-VITO-W638-BUS-01	4660	1880	1875
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	4763	1901	1902
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	5238	1901	1900
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	5008	1901	2329
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	5008	1901	1902
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-RENAULT-12-BREAK-WAGON-5D-01	4404	1616	1455
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417
EU-RENAULT-19-II-L53-CHAMADE-SEDAN-01	4248	1696	1412
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417
EU-RENAULT-9-L42-SEDAN-PHASE1-01	4070	1650	1405
EU-RENAULT-9-L42-SEDAN-PHASE2-01	4132	1666	1410
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425
EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	4370	1660	1400
EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	4410	1660	1450
EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	4410	1660	1490
EU-SUZUKI-VITARA-I-SUV-CLOSED-01	3620	1630	1665
EU-SUZUKI-VITARA-I-SUV-OPEN-01	3620	1630	1665
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-VW-GOLF-PLUS-V-MPV-01	4204	1759	1592

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Lancia	Prisma	1.9 Diesel	Stufenheck	Frontantrieb	Diesel	48	65	Jan 1983	Feb 1992	2024-03-01	7675
Lancia	Thema	8.32	Stufenheck	Frontantrieb	Benzin	158	215	Sep 1987	May 1989	2024-03-01	7676
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	120	163	Jul 2010	-	2024-03-01	7677
Mercedes-benz	Viano	CDI 3.0	Bus	Heckantrieb	Diesel	165	224	Jul 2010	-	2024-03-01	7678
Subaru	Leone iii	1800 CAT 4WD	Stufenheck	Allrad	Benzin	70	95	Jul 1986	Sep 1991	2024-03-01	7679
Subaru	Leone iii station wagon	1800 Super Catalytic-conv 4WD	Kombi	Allrad	Benzin	70	95	Jul 1986	Feb 1992	2024-03-01	7680
Renault	16	1.6 TS	Schrägheck	Frontantrieb	Benzin	61	83	Sep 1968	Aug 1980	2024-03-01	7681
Renault	16	1.6 TX	Schrägheck	Frontantrieb	Benzin	68	93	Jun 1974	Aug 1980	2024-03-01	7682
Mercedes-benz	Viano	CDI 2.2 4-matic	Bus	Allrad	Diesel	100	136	Jul 2010	-	2024-03-01	7683
Renault	16	1.5	Schrägheck	Frontantrieb	Benzin	40	55	Sep 1965	Oct 1975	2024-03-01	7684
Mercedes-benz	Viano	CDI 2.2 4-matic	Bus	Allrad	Diesel	120	163	Jul 2010	-	2024-03-01	7685
Mercedes-benz	Vito	116 CDI 4X4	Bus	Allrad	Diesel	120	163	Sep 2010	Aug 2014	2024-03-01	7686
Daihatsu	Charade iv	1.3 16V	Schrägheck	Frontantrieb	Benzin	55	75	May 1996	Nov 1999	2024-03-01	7687
Toyota	Corolla	1.6 XLI	Kombi	Frontantrieb	Benzin	77	105	Nov 1989	Jun 1992	2024-03-01	7689
Renault	14	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Dec 1981	Dec 1983	2024-03-01	7690
Suzuki	Vitara	2.0 16V	Geländewagen offen	Allrad	Benzin	97	132	Dec 1996	Mar 1999	2024-03-01	7691
Suzuki	Vitara	2.0 16V Allrad	Geländewagen geschlossen	Allrad	Benzin	97	132	Dec 1996	Mar 1998	2024-03-01	7692
Renault	12	1.3	Kombi	Frontantrieb	Benzin	37	50	Jul 1975	Apr 1980	2024-03-01	7693
Renault	12	1.3	Stufenheck	Frontantrieb	Benzin	37	50	Jul 1975	Apr 1980	2024-03-01	7694
Mercedes-benz	Vito	113 CDI 4X4	Bus	Allrad	Diesel	100	136	Sep 2010	Aug 2014	2024-03-01	7695
Suzuki	Vitara	1.9 D Allrad	Geländewagen geschlossen	Allrad	Diesel	50	68	Jan 1995	Mar 1998	2024-03-01	7696
Suzuki	Vitara	2.5 V6 24V Allrad	Geländewagen geschlossen	Allrad	Benzin	118	160	Dec 1995	Mar 1998	2024-03-01	7697
Suzuki	Vitara	2.0 TD Intercooler Allrad	Geländewagen geschlossen	Allrad	Diesel	64	87	Dec 1995	Mar 1998	2024-03-01	7698
Suzuki	Vitara	1.9 D Allrad	Geländewagen geschlossen	Allrad	Diesel	55	75	Aug 1996	Mar 1998	2024-03-01	7699
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	69	94	Jun 1987	Dec 1988	2024-03-01	7700
Mazda	323 c iv	1.8 16V 4WD	Schrägheck	Allrad	Benzin	76	103	Nov 1991	Dec 1993	2024-03-01	7701
Mazda	323 c iv	1.8 16V Turbo 4WD	Schrägheck	Allrad	Benzin	120	163	Sep 1990	Dec 1992	2024-03-01	7702
Opel	Campo	2.3	Pick-up	Heckantrieb	Benzin	69	94	Aug 1991	Aug 1994	2024-03-01	7703
Opel	Campo	2.5 D	Pick-up	Heckantrieb	Diesel	56	76	Aug 1991	Jun 1994	2024-03-01	7704
Opel	Campo	2.3 4X4	Pick-up	Allrad	Benzin	69	94	Aug 1991	Aug 1994	2024-03-01	7705
Opel	Campo	2.5 D 4X4	Pick-up	Allrad	Diesel	56	76	Aug 1991	Jun 1994	2024-03-01	7706
Opel	Campo	3.1 TD 4X4	Pick-up	Allrad	Diesel	80	109	Dec 1992	Jun 2001	2024-03-01	7707
Opel	Campo	3.1 TD	Pick-up	Heckantrieb	Diesel	80	109	Dec 1992	Jun 2001	2024-03-01	7708
Opel	Campo	2.3 4X4	Pick-up	Allrad	Benzin	72	98	Aug 1994	Sep 1996	2024-03-01	7709
Opel	Campo	2.3	Pick-up	Heckantrieb	Benzin	72	98	Aug 1994	Sep 1996	2024-03-01	7710
Mazda	323 s iv	1.8 16V Turbo 4WD	Stufenheck	Allrad	Benzin	120	163	Jan 1991	Jul 1994	2024-03-01	7711
Mazda	323 f iv	1.8 4WD	Schrägheck	Allrad	Benzin	76	103	Jan 1991	Apr 1994	2024-03-01	7712
Opel	Vivaro a	1.9 DI	Pritsche/Fahrgestell	Frontantrieb	Diesel	60	82	Aug 2001	Jul 2014	2024-03-01	7713
Daihatsu	Charade iv	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1996	Nov 1999	2024-03-01	7716
BMW	6	640 D Xdrive	Cabriolet	Allrad	Diesel	230	313	Mar 2012	Jun 2018	2024-03-01	7717
Daihatsu	Charade iv	1.5 16V	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1994	Jan 2001	2024-03-01	7718
Daihatsu	Gran move	1.5 16V	Großraumlimousine	Frontantrieb	Benzin	66	90	Oct 1996	Jul 1998	2024-03-01	7719
Opel	Vivaro a	2.5 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	99	135	Apr 2003	Mar 2010	2024-03-01	7720
Cadillac	Bls	2.0 T AWD	Stufenheck	Allrad	Benzin	154	210	Apr 2006	Dec 2010	2024-03-01	7721
Daihatsu	Move	0.8	Großraumlimousine	Frontantrieb	Benzin	31	42	Jan 1997	Nov 1999	2024-03-01	7722
Cadillac	Xlr	4.4	Cabriolet	Heckantrieb	Benzin	331	450	Mar 2004	Sep 2009	2024-03-01	7723
Daihatsu	Cuore iv	0.8	Schrägheck	Frontantrieb	Benzin	31	42	Nov 1996	Oct 1998	2024-03-01	7724
Daihatsu	Charade iv	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1997	Nov 1999	2024-03-01	7727
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	69	94	Jun 1987	Dec 1988	2024-03-01	7729
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	65	88	Oct 1986	Dec 1988	2024-03-01	7730
Renault	9	1.4 Turbo	Stufenheck	Frontantrieb	Benzin	77	105	Apr 1984	Dec 1986	2024-03-01	7731
Porsche	911	2.0 L	Coupe	Heckantrieb	Benzin	96	130	Aug 1967	Dec 1968	2024-03-01	7732
Porsche	911	2.0 S	Targa	Heckantrieb	Benzin	125	170	Jul 1966	Feb 1972	2024-03-01	7735
Porsche	911	2.3 T	Coupe	Heckantrieb	Benzin	103	140	Aug 1971	Dec 1973	2024-03-01	7736
Fiat	Ducato	1.9 D	Kasten	Frontantrieb	Diesel	51	69	Mar 1994	Apr 2002	2024-03-01	7738
Fiat	Ducato	2.5 TDI	Kasten	Frontantrieb	Diesel	80	109	Mar 1994	Apr 2002	2024-03-01	7739
Fiat	Ducato	2.5 D	Kasten	Frontantrieb	Diesel	62	84	Mar 1994	Apr 2002	2024-03-01	7740
Audi	A6 c5	1.8 T	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1997	Jan 2005	2024-03-01	7741
Audi	A8 d2	2.5 TDI	Stufenheck	Frontantrieb	Diesel	110	150	Jan 1997	Apr 2000	2024-03-01	7742
Audi	b3	1.8	Cabriolet	Frontantrieb	Benzin	92	125	Jan 1997	Aug 2000	2024-03-01	7743
Renault	19 ii	1.8	Cabriolet	Frontantrieb	Benzin	66	90	Sep 1993	Jun 1996	2024-03-01	7744
BMW	5	520 I	Kombi	Heckantrieb	Benzin	110	150	Mar 1997	Aug 2001	2024-03-01	7745
BMW	Z3 roadster	2.8 I	Cabriolet	Heckantrieb	Benzin	142	193	Nov 1996	May 2000	2024-03-01	7746
BMW	5	523 I	Kombi	Heckantrieb	Benzin	125	170	Mar 1997	Aug 2000	2024-03-01	7747
BMW	5	540 I	Kombi	Heckantrieb	Benzin	210	286	Apr 1997	Dec 2003	2024-03-01	7748
Opel	Mokka	1.8 4X4	SUV	Allrad	Benzin	103	140	Jan 2013	Dec 2019	2025-06-01	7749
BMW	Z3 roadster	M 3.2	Cabriolet	Heckantrieb	Benzin	236	321	Jan 1997	Jun 2000	2024-03-01	7750
Chrysler	Voyager / grand iii	2.0 I	Großraumlimousine	Frontantrieb	Benzin	98	133	Jan 1995	Mar 2001	2024-03-01	7751
VW	Golf plus v	1.2 TSI	Schrägheck	Frontantrieb	Benzin	63	86	May 2010	Dec 2013	2024-03-01	7752
Jeep	Cherokee	2.5 I 4X4	Geländewagen geschlossen	Allrad	Benzin	87	118	Oct 1984	Sep 2001	2024-03-01	7753
Citroën	Xantia	3.0 I 24V	Schrägheck	Frontantrieb	Benzin	140	190	Jan 1997	Apr 2003	2024-03-01	7754
Citroën	Jumper i	2.5 TDI	Bus	Frontantrieb	Diesel	79	107	Dec 1996	Nov 2000	2024-03-01	7755
Citroën	Jumper i	2.5 TDI 4X4	Bus	Allrad	Diesel	79	107	Dec 1996	Nov 2000	2024-03-01	7756
Daewoo	Nexia	1.5	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1996	Aug 1997	2024-03-01	7757
Daewoo	Nexia	1.5	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1996	Aug 1997	2024-03-01	7758
Fiat	Coupe	2.0 20V	Coupe	Frontantrieb	Benzin	108	147	Aug 1996	Sep 1998	2024-03-01	7759
Fiat	Coupe	2.0 20V Turbo	Coupe	Frontantrieb	Benzin	162	220	Aug 1996	Aug 2000	2024-03-01	7760
Fiat	Punto	1.4 GT Turbo	Schrägheck	Frontantrieb	Benzin	96	131	Sep 1996	Jul 1999	2024-03-01	7762
Fiat	Punto	1.7 TD	Schrägheck	Frontantrieb	Diesel	46	63	Sep 1996	Sep 1999	2024-03-01	7763
Alfa Romeo	Gtv	3.0 V6 24V	Coupe	Frontantrieb	Benzin	162	220	Oct 1996	Oct 2000	2024-03-01	7764
Alfa Romeo	145	1.4 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	76	103	Dec 1996	Jan 2001	2024-03-01	7765
Alfa Romeo	146	1.4 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	76	103	Nov 1996	Jan 2001	2024-03-01	7766
Alfa Romeo	146	1.6 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	88	120	Nov 1996	Oct 2001	2024-03-01	7767
Alfa Romeo	146	1.8 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	103	140	Nov 1996	Jan 2001	2024-03-01	7768
Alfa Romeo	145	1.6 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	88	120	Dec 1996	Jan 2001	2024-03-01	7769
Alfa Romeo	145	1.8 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	103	140	Dec 1996	Dec 1998	2024-03-01	7770
Fiat	Fiorino	65 1.7 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	46	63	Jan 1997	May 2001	2024-03-01	7771
Fiat	Ducato panorama	1.9 TD	Bus	Frontantrieb	Diesel	60	82	Mar 1989	Aug 1990	2024-03-01	7773
Fiat	Ducato panorama	2	Bus	Frontantrieb	Benzin	62	84	Sep 1988	Aug 1990	2024-03-01	7774
Fiat	Ducato panorama	2.5 D 4X4	Bus	Allrad	Diesel	55	75	Jan 1987	Aug 1990	2024-03-01	7775
Fiat	Ducato panorama	2.5 TD	Bus	Frontantrieb	Diesel	68	92	Jan 1987	Aug 1990	2024-03-01	7776
Fiat	Ducato panorama	2.5 TD 4X4	Bus	Allrad	Diesel	68	92	Jan 1986	Aug 1990	2024-03-01	7778
Fiat	Ducato	1.8	Kasten	Frontantrieb	Benzin	49	67	Jan 1982	Oct 1988	2024-03-01	7779
Fiat	Ducato	1.9 D	Kasten	Frontantrieb	Diesel	52	71	Jan 1988	Aug 1990	2024-03-01	7780
Fiat	Ducato	1.9 TD	Kasten	Frontantrieb	Diesel	60	82	Mar 1989	Aug 1990	2024-03-01	7781
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	55	75	Jul 1985	Aug 1990	2024-03-01	7782
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	58	79	Jan 1982	Aug 1990	2024-03-01	7783
Fiat	Ducato	2.5 D	Kasten	Frontantrieb	Diesel	55	75	Jan 1982	Aug 1990	2024-03-01	7784
Fiat	Ducato	2.4 D	Kasten	Frontantrieb	Diesel	53	72	Jan 1982	Aug 1990	2024-03-01	7785
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	62	84	Mar 1989	Aug 1990	2024-03-01	7786


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 **58 个输入 Ktype** 的映射，生成 **68 条 READY 映射行**。
* 直接复用累计表中已确认的 **32 个尺寸组**，未重复输出其三维和来源。
* 首次闭合 **13 个 DIMENSION_GROUP**，包括 Renault 14、Renault 12 Sedan、BMW F12 Convertible、Audi A6 C5 Sedan、Audi Cabriolet、BMW E39 Touring、BMW Z3/Z3 M、Cadillac BLS/XLR-V 等。新建尺寸组均采用不含后视镜宽度。([汽车目录][1])
* 已拆分 Porsche 911 Ktype `7736` 的 1972 年 8 月前后外廓；两阶段长度分别为 4147 mm 和 4127 mm。([汽车目录][2])
* 已拆分 Jeep Cherokee XJ、Citroën Xantia、Fiat Punto、Alfa Romeo GTV 以及 Ducato Panorama 的明确物理分支。

## 当前批次进度

* 输入 Ktype 总数：100
* 已 READY 输入 Ktype：58
* READY 映射行：68
* 尚待处理输入 Ktype：42
* 本轮首次创建尺寸组：13
* 本轮复用既有尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7675	7675	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7676	7676	Sedan	Thema I	834	4	EU-LANCIA-THEMA-I-8-32-SEDAN-01	HIGH	8.32专属外廓。	READY
7679	7679	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
7680	7680	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	Super 4WD加高外廓。	READY
7687	7687	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7689	7689	Wagon	Corolla VI E90	E90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH		READY
7690	7690	Hatchback	Renault 14	R1210	5	EU-RENAULT-14-HATCHBACK-5D-01	HIGH		READY
7691	7691	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴外廓。	READY
7693	7693	Wagon	Renault 12		5	EU-RENAULT-12-BREAK-WAGON-5D-01	HIGH		READY
7694	7694	Sedan	Renault 12		4	EU-RENAULT-12-SEDAN-4D-01	HIGH		READY
7701	7701	Hatchback	323 IV BG	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
7702	7702	Hatchback	323 IV BG	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
7716	7716	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7717	7717	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
7718	7718	Sedan	Charade IV	G200	4	EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	HIGH		READY
7719	7719	MPV	Gran Move I		5	EU-DAIHATSU-GRAN-MOVE-I-MPV-01	MEDIUM		READY
7721	7721	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-4D-01	HIGH		READY
7722	7722	MPV	Move I	L601	5	EU-DAIHATSU-MOVE-I-L601-MPV-01	HIGH		READY
7723	7723	Convertible	XLR	X215	2	EU-CADILLAC-XLR-V-CONVERTIBLE-01	HIGH	XLR-V增压版外廓。	READY
7724	7724	Hatchback	Cuore IV	L501		EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	HIGH		READY
7727	7727	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7729	7729	Sedan	Renault 9 Phase 2	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE2-01	HIGH		READY
7730	7730	Sedan	Renault 9 Phase 2	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE2-01	HIGH		READY
7731	7731	Sedan	Renault 9 Phase 1	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE1-01	HIGH		READY
7732	7732	Coupe	911 F Series	901	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	HIGH	2.0 L短轴Coupe。	READY
7735	7735	Targa	911 F Series	901	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	Targa车身保留来源名称。	READY
7736_preaug72	7736	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	HIGH	1972年8月前外廓。	READY
7736_postaug72	7736	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	HIGH	1972年8月后外廓。	READY
7741	7741	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH	改款前后长宽高一致，复用同一尺寸组。	READY
7742	7742	Sedan	A8 D2	4D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
7743	7743	Convertible	Audi Cabriolet B3	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-FACELIFT-01	HIGH		READY
7744	7744	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH		READY
7745	7745	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7746	7746	Convertible	Z3	E36/7	2	EU-BMW-Z3-E36-7-ROADSTER-2-8-01	HIGH	2.8宽体Roadster。	READY
7747	7747	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7748	7748	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7750	7750	Convertible	Z3 M	E36/7	2	EU-BMW-Z3-M-E36-7-ROADSTER-01	HIGH	M Roadster低车身外廓。	READY
7752	7752	MPV	Golf Plus V	5M	5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
7753_early	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	MEDIUM	早期短车身分支。	READY
7753_prefl	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	MEDIUM	改款前长车身分支。	READY
7753_facelift	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	MEDIUM	1997年改款外廓。	READY
7754_x1	7754	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	X1阶段。	READY
7754_x2	7754	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	X2改款阶段。	READY
7757	7757	Sedan	Nexia	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
7758	7758	Hatchback	Nexia	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH		READY
7759	7759	Coupe	Fiat Coupe	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
7760	7760	Coupe	Fiat Coupe	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
7762	7762	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	HIGH	GT三门外廓。	READY
7763_3dr	7763	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	HIGH	三门分支。	READY
7763_5dr	7763	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	HIGH	五门分支。	READY
7764_prefl	7764	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前外廓。	READY
7764_facelift	7764	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
7765	7765	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7766	7766	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7767	7767	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7768	7768	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7769	7769	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7770	7770	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7771	7771	Van	Fiorino II			EU-FIAT-FIORINO-II-VAN-01	MEDIUM	货运/乘用混合标注按共同封闭车身落组。	READY
7773	7773	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH		READY
7774_prefl	7774	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7774_facelift	7774	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7775_prefl	7775	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7775_facelift	7775	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7776_prefl	7776	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7776_facelift	7776	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7778_prefl	7778	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7778_facelift	7778	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-14-HATCHBACK-5D-01	4025	1624	1405	Automobile-Catalog 1981 Renault 14 TS Regency	https://www.automobile-catalog.com/car/1981/2929745/renault_14_ts_regency.html
EU-RENAULT-12-SEDAN-4D-01	4348	1616	1435	Automobile-Catalog 1976 Renault 12 L	https://www.automobile-catalog.com/car/1976/2926670/renault_12_l.html
EU-BMW-6-F12-CONVERTIBLE-01	4894	1894	1365	BMW Group PressClub 640d xDrive Convertible specifications	https://www.press.bmwgroup.com/global/article/detail/T0124398EN/specifications-bmw-6-series-convertible-640d-xdrive-03/2012?language=en
EU-DAIHATSU-GRAN-MOVE-I-MPV-01	4059	1641	1600	AutoEvolution Daihatsu Gran Move 1.5 90 HP	https://www.autoevolution.com/cars/daihatsu-gran-move-1996.html
EU-CADILLAC-BLS-SEDAN-4D-01	4680	1752	1471	Auto-Data Cadillac BLS 2.0 T 210 Hp	https://www.auto-data.net/en/cadillac-bls-2.0-t-210hp-11691
EU-DAIHATSU-MOVE-I-L601-MPV-01	3310	1400	1699	AutoEvolution Daihatsu Move 0.8 42 HP	https://www.autoevolution.com/cars/daihatsu-move-1997.html
EU-CADILLAC-XLR-V-CONVERTIBLE-01	4514	1836	1280	Edmunds 2006 Cadillac XLR-V specifications	https://www.edmunds.com/cadillac/xlr-v/2006/features-specs/
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320	Automobile-Catalog 1968 Porsche 911 L Coupe	https://www.automobile-catalog.com/car/1968/2588870/porsche_911_l_coupe.html
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453	Auto-Data Audi A6 4B C5 1.8 T; Auto-Data Audi A6 4B C5 facelift 1.8 T	https://www.auto-data.net/en/audi-a6-4b-c5-1.8-t-150hp-4693;https://www.auto-data.net/en/audi-a6-4b-c5-facelift-2001-1.8-t-150hp-27079
EU-AUDI-CABRIOLET-8G-CONVERTIBLE-FACELIFT-01	4366	1716	1379	Auto-Data Audi Cabriolet B3 8G facelift 1.8 20V	https://www.auto-data.net/en/audi-cabriolet-b3-8g-facelift-1997-1.8-20v-125hp-4247
EU-BMW-5-E39-WAGON-01	4805	1800	1440	Auto-Data BMW 5 Series Touring E39 520i	https://www.auto-data.net/en/bmw-5-series-touring-e39-520i-150hp-9645
EU-BMW-Z3-E36-7-ROADSTER-2-8-01	4025	1740	1293	Auto-Data BMW Z3 E36/7 2.8	https://www.auto-data.net/en/bmw-z3-e36-7-2.8-192hp-9916
EU-BMW-Z3-M-E36-7-ROADSTER-01	4025	1740	1266	BMW M Z3 M Roadster technical data	https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-z3-m-roadster.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz Viano/Vito W639 的 Compact、Long、Extra-long 车长分支及 4MATIC 高度边界。
2. 区分 Suzuki Vitara 封闭式三门短轴与五门长轴，处理 Ktype `7692`、`7696`—`7699`。
3. 核对 Opel Campo 的 Single Cab、Extended Cab、Double Cab 以及短/长货斗分支。
4. 处理 Opel Vivaro A 平板/底盘车的轴距和驾驶室分支。
5. 集中闭合 Fiat Ducato 230、280、290 Kasten 的 SWB/LWB 与低顶/高顶组合。
6. 补齐 Renault 16、Renault 11、Mazda 323 S/F、Opel Mokka、Chrysler Voyager/Grand Voyager 等剩余乘用车外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/2929745/renault_14_ts_regency.html?utm_source=chatgpt.com "1981 Renault 14 TS Regency Specs Review (51.5 kW / 70 ..."
[2]: https://www.automobile-catalog.com/car/1972/2590220/porsche_911_t_coupe.html?utm_source=chatgpt.com "1972 Porsche 911 T Coupe Specs Review (95.5 kW / 130 PS / 128 hp) (up to August 1972 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Viano W639 Facelift 的 4 个 Ktype，按照官方确认的 Compact、Long、Extra Long 三种车长拆分；三种车身长度分别为 4763、5008、5238 mm。([marsClassic][1])
* 完成 Opel Campo 的 8 个 Ktype，统一拆分为 Single Cab、Half Cab、Double Cab；三种驾驶室均有对应输入发动机版本，Single Cab 高 1595 mm，Half/Double Cab 高 1710 mm。([汽车数据网][2])
* 完成 Renault 11、Mazda 323 F IV、Opel Mokka I 和 Chrysler Voyager III 映射。Mazda 323 F 为五门 4260×1680×1340 mm；Mokka 官方宽度采用不含后视镜的 1777 mm；Voyager 2.0 I 仅映射短轴四门 Voyager III。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* READY 映射行：108
* PENDING 输入 Ktype：26
* 当前批次已确认尺寸组：55
* 本轮新增 READY 输入 Ktype：16
* 本轮新增映射行：40
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7677_compact	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7677_long	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7677_extralong	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7678_compact	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7678_long	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7678_extralong	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7683_compact	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7683_long	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7683_extralong	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7685_compact	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7685_long	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7685_extralong	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7700	7700	Hatchback	Renault 11 Phase 2	C37E	3	EU-RENAULT-11-PHASE2-C37E-HATCHBACK-3D-01	HIGH	GTE三门外廓。	READY
7703_singlecab	7703	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7703_halfcab	7703	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7703_doublecab	7703	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7704_singlecab	7704	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7704_halfcab	7704	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7704_doublecab	7704	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7705_singlecab	7705	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7705_halfcab	7705	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7705_doublecab	7705	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7706_singlecab	7706	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7706_halfcab	7706	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7706_doublecab	7706	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7707_singlecab	7707	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7707_halfcab	7707	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7707_doublecab	7707	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7708_singlecab	7708	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7708_halfcab	7708	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7708_doublecab	7708	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7709_singlecab	7709	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7709_halfcab	7709	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7709_doublecab	7709	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7710_singlecab	7710	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7710_halfcab	7710	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7710_doublecab	7710	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7712	7712	Hatchback	323 F IV BG	BG	5	EU-MAZDA-323-F-IV-BG-HATCHBACK-5D-01	HIGH		READY
7749	7749	SUV	Mokka I		5	EU-OPEL-MOKKA-I-SUV-01	HIGH		READY
7751	7751	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	HIGH	2.0 I对应短轴Voyager III。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	4763	1901	1875	Mercedes-Benz Public Archive Viano 639 overview; Auto-Data Mercedes-Benz Viano W639 Facelift CDI 2.2	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://www.auto-data.net/en/mercedes-benz-viano-w639-facelift-2010-cdi-2.2-163hp-automatic-18950
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	5008	1901	1875	Mercedes-Benz Public Archive Viano 639 overview; Mercedes-Benz Public Archive Viano CDI 2.2 long	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2010---2014.xhtml?oid=193897441
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	5238	1901	1872	Mercedes-Benz Public Archive Viano 639 overview; Mercedes-Benz Public Archive Viano CDI 3.0 extra long	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-extra-long-2010---2014.xhtml?oid=193897450
EU-RENAULT-11-PHASE2-C37E-HATCHBACK-3D-01	4047	1666	1380	Automobile-Catalog 1987 Renault 11 GTE	https://www.automobile-catalog.com/car/1987/2935100/renault_11_gte.html
EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	4980	1690	1595	Auto-Data Opel Campo Single Cab	https://www.auto-data.net/en/opel-campo-single-cab-generation-5140
EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	4980	1690	1710	Auto-Data Opel Campo model overview	https://www.auto-data.net/en/opel-campo-model-233
EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	4980	1690	1710	Auto-Data Opel Campo Double Cab	https://www.auto-data.net/en/opel-campo-double-cab-generation-5141
EU-MAZDA-323-F-IV-BG-HATCHBACK-5D-01	4260	1680	1340	Auto-Data Mazda 323 F IV BG 1.8 4WD	https://www.auto-data.net/en/mazda-323-f-iv-bg-1.8-4wd-103hp-11180
EU-OPEL-MOKKA-I-SUV-01	4278	1777	1658	Opel Mokka 2013 official specification	https://opel.psc-zagreb.com/getImage?path=Downloads%2Fcountry_1332918467480%2Fdoc_1365706479747_hr_mokka_2013_04_11.pdf
EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	4733	1950	1740	Auto-Data Chrysler Voyager III 2.0 I	https://www.auto-data.net/en/chrysler-voyager-iii-2.0-i-133hp-14833
```

## 下一步优先处理

1. 闭合 Vito W639 4X4 的 Compact、Long、Extra Long 分支及对应车高：`7686`、`7695`。
2. 处理 Vitara I 封闭式三门短轴、五门长轴和 V6/柴油外廓：`7692`、`7696`—`7699`。
3. 处理 Renault 16 各阶段、Mazda 323 S IV，以及 Vivaro A 平板/底盘车：`7681`、`7682`、`7684`、`7711`、`7713`、`7720`。
4. 集中闭合 Jumper/Ducato 230、280、290 的轴距与车顶组合：`7738`—`7740`、`7755`—`7756`、`7779`—`7786`。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058 "639 series Viano Multi Purpose Vehicles, 2010 - 2014"
[2]: https://www.auto-data.net/en/opel-campo-single-cab-generation-5140 "Opel Campo Single Cab | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1987/2935100/renault_11_gte.html?utm_source=chatgpt.com "1987 Renault 11 GTE Specs Review (70 kW / 95 PS / 94 hp) (for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 **11 个 Ktype**，新增 **15 条 READY 映射**及 **7 个尺寸组**。
* Vito W639 4X4 按 Compact、Long、Extra Long 三种车长拆分；官方资料确认车长与 1901 mm 不含镜车宽，4X4 对应车高为 1942/1942/1939 mm。
* Vitara 2.0 16V 三门宽体闭合为 3745×1695×1660 mm；五门柴油及 V6 外廓闭合为 4125×1695×1695 mm。官方历史规格页同时确认三门与五门分支边界。
* Renault 16 三个 Ktype 复用同一五门车身；Mazda 323 S IV Turbo 4WD 闭合四门 Sedan 外廓。([Renault][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：85
* READY 映射行：123
* PENDING 输入 Ktype：15
* 已确认尺寸组：62
* 本轮新增 READY 输入 Ktype：11
* 本轮新增映射行：15
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7686_compact	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	MEDIUM	Compact四驱车身分支。	READY
7686_long	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	MEDIUM	Long轴四驱车身分支。	READY
7686_extralong	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	MEDIUM	Extra Long四驱车身分支。	READY
7681	7681	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7682	7682	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7684	7684	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7692	7692	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-3D-WIDEBODY-01	HIGH	2.0 16V三门宽体封闭式外廓。	READY
7695_compact	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	MEDIUM	Compact四驱车身分支。	READY
7695_long	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	MEDIUM	Long轴四驱车身分支。	READY
7695_extralong	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	MEDIUM	Extra Long四驱车身分支。	READY
7696	7696	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门柴油封闭式外廓。	READY
7697	7697	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门V6封闭式外廓。	READY
7698	7698	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门涡轮柴油封闭式外廓。	READY
7699	7699	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	MEDIUM	五门柴油封闭式外廓。	READY
7711	7711	Sedan	323 IV BG	BG8R	4	EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	4763	1901	1942	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	5008	1901	1942	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	5238	1901	1939	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-RENAULT-16-HATCHBACK-5D-01	4240	1650	1450	Renault The Originals R16 TX	https://theoriginals.renault.com/en/r16-tx
EU-SUZUKI-VITARA-I-SUV-CLOSED-3D-WIDEBODY-01	3745	1695	1660	Suzuki Vitara 2.0 16V official specification brochure	https://www.autoweek.nl/autobrochures/download/483/
EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	4125	1695	1695	Suzuki Vitara Villager V6 official brochure; Suzuki Vitara 5-door Wagon 2.0 Diesel official specification	https://www.autoweek.nl/autobrochures/download/476/;https://www.autoweek.nl/autobrochures/download/485/
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375	Tunel.az Mazda 323 S IV BG 163 hp specifications	https://tunel.az/catalog/mazda/323/mazda-323-s-iv-bg/3f6679a3-9421-49bb-9b1a-ab50f0fd13b4
```

## 下一步优先处理

1. 闭合 Opel Vivaro A 平板/底盘车的轴距、驾驶室和车高分支：`7713`、`7720`。
2. 集中处理 Fiat Ducato II 230 Kasten 的 SWB/MWB/LWB 与低顶/高顶分支：`7738`—`7740`。
3. 处理 Citroën Jumper I Bus 普通前驱与 Dangel 4X4 的外廓边界：`7755`、`7756`。
4. 最后闭合 Fiat Ducato I 280/290 Kasten 的改款阶段、轴距与车顶组合：`7779`—`7786`。

推进信号：CONTINUE

[1]: https://theoriginals.renault.com/en/r16-tx "R16 TX - The Originals Museum"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Opel Vivaro A 平板/底盘车型 `7713`、`7720`。官方改装车型资料确认单排栏板车外廓为 **5350 × 1990 × 2000 mm**，其中宽度为不含后视镜口径。
* 闭合 Citroën Jumper I 前驱 Bus `7755`，按已有缓存直接关联 SWB 低顶、MWB 低顶和 MWB 高顶三个尺寸组；未重复抓取或输出既有尺寸组。
* Jumper 4X4 `7756` 暂未关联普通前驱缓存组，仍需确认 Dangel 四驱改装是否改变整车高度。现有车型资料仅能确认该代 Bus 覆盖 4655–5005 mm 车长和前驱/四驱配置，尚不足以闭合具体四驱高度。([引擎细节][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：88
* READY 映射行：128
* PENDING 输入 Ktype：12
* 已确认尺寸组：63
* 本轮新增 READY 输入 Ktype：3
* 本轮新增映射行：5
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7713	7713	Pickup	Vivaro A	X83	2	EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	MEDIUM	单排栏板车物理外廓。	READY
7720	7720	Pickup	Vivaro A	X83	2	EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	MEDIUM	单排栏板车物理外廓。	READY
7755_swb_lowroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	短轴低顶客车分支。	READY
7755_mwb_lowroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	中轴低顶客车分支。	READY
7755_mwb_highroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	中轴高顶客车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	5350	1990	2000	Vauxhall Vivaro and Movano 2008 Chassis Cabs and Core Conversions	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_ChassisCabConv_August_2007.pdf
```

## 下一步优先处理

1. 确认 `7756` Jumper I Dangel 4X4 Bus 的 SWB/MWB、车顶及四驱悬架高度边界。
2. 根据 Ducato 230 官方手册闭合 `7738`—`7740` 的 10/14/MAXI、SWB/MWB/LWB 与低顶/高顶组合。
3. 闭合 `7779`—`7786` 的 Ducato I 280/290 改款阶段及 Van 轴距、车顶分支。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002?utm_source=chatgpt.com "Citroen Jumper (I) Estate/Wagon (1997 - 2002)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 `7756`：Jumper I 2.5 TDI 4X4 Bus 关联既有短轴低顶客车尺寸组。瑞士型式批准记录确认该乘用车身为 4655 × 1998 × 2150 mm。([Motoro][1])
* 闭合 `7781`、`7786`：两者均属于 Ducato I 290 Kasten，按 SWB/LWB、低顶/高顶四个既有物理分支完成映射。
* 本轮全部复用既有尺寸组，未重新抓取或重复输出尺寸来源。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：91
* READY 映射行：137
* PENDING 输入 Ktype：9
* 已确认尺寸组：63
* 本轮新增 READY 输入 Ktype：3
* 本轮新增映射行：9
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7756	7756	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	四驱短轴低顶客车外廓。	READY
7781_swb_lowroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶分支。	READY
7781_swb_highroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶分支。	READY
7781_lwb_lowroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶分支。	READY
7781_lwb_highroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶分支。	READY
7786_swb_lowroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶分支。	READY
7786_swb_highroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶分支。	READY
7786_lwb_lowroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶分支。	READY
7786_lwb_highroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `7738`—`7740` 的 Ducato II 230 Kasten：按 4655、5005、5505 mm 车长及对应车顶组合建立稳定尺寸组。
2. 创建 Ducato I 280 Kasten 的首次尺寸组，处理 `7779`、`7780`、`7782`—`7785`。
3. 对跨越 280/290 改款时间的 Ktype 拆分 `prefl`、`facelift` 分支，并将 290 分支直接关联既有缓存组。

推进信号：CONTINUE

[1]: https://motoro.ch/en/fiche-technique/citroen/jumper-2-5tdi-4x4 "motoro.ch"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 Fiat Ducato II 230 Kasten 的 `7738`—`7740`，按短轴低顶、短轴高顶、中轴低顶、中轴高顶和长轴高顶拆分。确认车宽均为不含后视镜的 1998 mm，车长覆盖 4655、5005、5505 mm。([使用手册][1])
* 已闭合仅覆盖 280 车身阶段的 `7779`，创建短轴低顶、短轴高顶和长轴高顶三个稳定尺寸组；对应三维由同一瑞士型式批准记录确认。([Astra Open Data][2])
* `7780`、`7782`—`7785` 跨越 Ducato 280/290 改款阶段，保留为最后一组待拆分映射；既有 290 尺寸组不重复输出。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：95
* READY 映射行：155
* PENDING 输入 Ktype：5
* 当前映射引用的已确认尺寸组：83
* 本轮新增 READY 输入 Ktype：4
* 本轮新增映射行：18
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7738_swb_lowroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7738_swb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7738_mwb_lowroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7738_mwb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7738_lwb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7739_swb_lowroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7739_swb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7739_mwb_lowroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7739_mwb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7739_lwb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7740_swb_lowroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7740_swb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7740_mwb_lowroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7740_mwb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7740_lwb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7779_swb_lowroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	HIGH	280短轴低顶封闭货厢分支。	READY
7779_swb_highroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	HIGH	280短轴高顶封闭货厢分支。	READY
7779_lwb_highroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	HIGH	280长轴高顶封闭货厢分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150	Swiss type approval Fiat Ducato 230/14 1.9 TDS CH3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470	Swiss type approval Fiat Ducato 230/14 1.9 TDS CH3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150	Swiss type approval Fiat Ducato 230/14 2.5 TD CH3F2207	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2207_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470	Swiss type approval Fiat Ducato 230/14 2.0 CH3F2208	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2208_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480	Swiss type approval Fiat Ducato 230/18 2.5 TD CH3F2235	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2235_F.pdf
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4759	1965	2100	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	4759	1965	2400	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	5489	1965	2400	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
```

## 下一步优先处理

1. 将 `7780`、`7782`、`7783`、`7784`、`7785` 拆分为 280 改款前分支和 290 改款后分支。
2. 280 分支关联本轮新建尺寸组；290 分支直接关联既有四个缓存尺寸组，不再重复输出来源。
3. PENDING 清零后立即执行一次机械校验并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.gebruikershandleiding.com/Fiat-Ducato-230/preview-handleiding-573899.html?page=0169 "Handleiding Fiat Ducato 230 (pagina 169 van 206) (Nederlands)"
[2]: https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf "BSY1/EVPS/T754S.E517PROD.STC09130.D0002094.?"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7201-7300_ktype_dimension_mapping_final.tsv
- all_7201-7300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 完成剩余 Ktype `7780`、`7782`、`7783`、`7784`、`7785` 的 Ducato I 280/290 物理分支拆分。
* 280 分支关联短轴低顶、短轴高顶、长轴高顶尺寸组；290 分支关联短轴低顶、短轴高顶、长轴低顶、长轴高顶尺寸组。
* 已完成机械校验：映射表严格为 10 列，尺寸组表严格为 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；所有引用闭合；无孤立尺寸组；尺寸、来源及 URL 均非空。
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* 最终映射行：190
* PENDING：0
* 最终 DIMENSION_GROUP：83
* 所有映射均为 `READY`，当前批次完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7675	7675	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7676	7676	Sedan	Thema I	834	4	EU-LANCIA-THEMA-I-8-32-SEDAN-01	HIGH	8.32专属外廓。	READY
7677_compact	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7677_long	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7677_extralong	7677	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7678_compact	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7678_long	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7678_extralong	7678	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7679	7679	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
7680	7680	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	Super 4WD加高外廓。	READY
7681	7681	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7682	7682	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7683_compact	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7683_long	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7683_extralong	7683	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7684	7684	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-01	HIGH		READY
7685_compact	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	HIGH	Compact车身分支。	READY
7685_long	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	HIGH	Long车身分支。	READY
7685_extralong	7685	MPV	Viano W639 Facelift	W639		EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
7686_compact	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	MEDIUM	Compact四驱车身分支。	READY
7686_long	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	MEDIUM	Long轴四驱车身分支。	READY
7686_extralong	7686	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	MEDIUM	Extra Long四驱车身分支。	READY
7687	7687	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7689	7689	Wagon	Corolla VI E90	E90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH		READY
7690	7690	Hatchback	Renault 14	R1210	5	EU-RENAULT-14-HATCHBACK-5D-01	HIGH		READY
7691	7691	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴外廓。	READY
7692	7692	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-3D-WIDEBODY-01	HIGH	2.0 16V三门宽体封闭式外廓。	READY
7693	7693	Wagon	Renault 12		5	EU-RENAULT-12-BREAK-WAGON-5D-01	HIGH		READY
7694	7694	Sedan	Renault 12		4	EU-RENAULT-12-SEDAN-4D-01	HIGH		READY
7695_compact	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	MEDIUM	Compact四驱车身分支。	READY
7695_long	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	MEDIUM	Long轴四驱车身分支。	READY
7695_extralong	7695	MPV	Vito W639 Facelift	W639		EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	MEDIUM	Extra Long四驱车身分支。	READY
7696	7696	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门柴油封闭式外廓。	READY
7697	7697	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门V6封闭式外廓。	READY
7698	7698	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	HIGH	五门涡轮柴油封闭式外廓。	READY
7699	7699	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	MEDIUM	五门柴油封闭式外廓。	READY
7700	7700	Hatchback	Renault 11 Phase 2	C37E	3	EU-RENAULT-11-PHASE2-C37E-HATCHBACK-3D-01	HIGH	GTE三门外廓。	READY
7701	7701	Hatchback	323 IV BG	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
7702	7702	Hatchback	323 IV BG	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
7703_singlecab	7703	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7703_halfcab	7703	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7703_doublecab	7703	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7704_singlecab	7704	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7704_halfcab	7704	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7704_doublecab	7704	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7705_singlecab	7705	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7705_halfcab	7705	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7705_doublecab	7705	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7706_singlecab	7706	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7706_halfcab	7706	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7706_doublecab	7706	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7707_singlecab	7707	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7707_halfcab	7707	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7707_doublecab	7707	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7708_singlecab	7708	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7708_halfcab	7708	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7708_doublecab	7708	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7709_singlecab	7709	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7709_halfcab	7709	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7709_doublecab	7709	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7710_singlecab	7710	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	MEDIUM	单排驾驶室分支。	READY
7710_halfcab	7710	Pickup	Campo I		2	EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	MEDIUM	加长驾驶室分支。	READY
7710_doublecab	7710	Pickup	Campo I		4	EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	MEDIUM	双排驾驶室分支。	READY
7711	7711	Sedan	323 IV BG	BG8R	4	EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
7712	7712	Hatchback	323 F IV BG	BG	5	EU-MAZDA-323-F-IV-BG-HATCHBACK-5D-01	HIGH		READY
7713	7713	Pickup	Vivaro A	X83	2	EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	MEDIUM	单排栏板车物理外廓。	READY
7716	7716	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7717	7717	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
7718	7718	Sedan	Charade IV	G200	4	EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	HIGH		READY
7719	7719	MPV	Gran Move I		5	EU-DAIHATSU-GRAN-MOVE-I-MPV-01	MEDIUM		READY
7720	7720	Pickup	Vivaro A	X83	2	EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	MEDIUM	单排栏板车物理外廓。	READY
7721	7721	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-4D-01	HIGH		READY
7722	7722	MPV	Move I	L601	5	EU-DAIHATSU-MOVE-I-L601-MPV-01	HIGH		READY
7723	7723	Convertible	XLR	X215	2	EU-CADILLAC-XLR-V-CONVERTIBLE-01	HIGH	XLR-V增压版外廓。	READY
7724	7724	Hatchback	Cuore IV	L501		EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	HIGH		READY
7727	7727	Hatchback	Charade IV	G200		EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	HIGH		READY
7729	7729	Sedan	Renault 9 Phase 2	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE2-01	HIGH		READY
7730	7730	Sedan	Renault 9 Phase 2	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE2-01	HIGH		READY
7731	7731	Sedan	Renault 9 Phase 1	L42	4	EU-RENAULT-9-L42-SEDAN-PHASE1-01	HIGH		READY
7732	7732	Coupe	911 F Series	901	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	HIGH	2.0 L短轴Coupe。	READY
7735	7735	Targa	911 F Series	901	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	Targa车身保留来源名称。	READY
7736_preaug72	7736	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	HIGH	1972年8月前外廓。	READY
7736_postaug72	7736	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	HIGH	1972年8月后外廓。	READY
7738_swb_lowroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7738_swb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7738_mwb_lowroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7738_mwb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7738_lwb_highroof	7738	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7739_swb_lowroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7739_swb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7739_mwb_lowroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7739_mwb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7739_lwb_highroof	7739	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7740_swb_lowroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭货厢分支。	READY
7740_swb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭货厢分支。	READY
7740_mwb_lowroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	MEDIUM	中轴低顶封闭货厢分支。	READY
7740_mwb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶封闭货厢分支。	READY
7740_lwb_highroof	7740	Van	Ducato II	230		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭货厢分支。	READY
7741	7741	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH	改款前后长宽高一致，复用同一尺寸组。	READY
7742	7742	Sedan	A8 D2	4D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
7743	7743	Convertible	Audi Cabriolet B3	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-FACELIFT-01	HIGH		READY
7744	7744	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH		READY
7745	7745	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7746	7746	Convertible	Z3	E36/7	2	EU-BMW-Z3-E36-7-ROADSTER-2-8-01	HIGH	2.8宽体Roadster。	READY
7747	7747	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7748	7748	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
7749	7749	SUV	Mokka I		5	EU-OPEL-MOKKA-I-SUV-01	HIGH		READY
7750	7750	Convertible	Z3 M	E36/7	2	EU-BMW-Z3-M-E36-7-ROADSTER-01	HIGH	M Roadster低车身外廓。	READY
7751	7751	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	HIGH	2.0 I对应短轴Voyager III。	READY
7752	7752	MPV	Golf Plus V	5M	5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
7753_early	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	MEDIUM	早期短车身分支。	READY
7753_prefl	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	MEDIUM	改款前长车身分支。	READY
7753_facelift	7753	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	MEDIUM	1997年改款外廓。	READY
7754_x1	7754	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	X1阶段。	READY
7754_x2	7754	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	X2改款阶段。	READY
7755_swb_lowroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	短轴低顶客车分支。	READY
7755_mwb_lowroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	中轴低顶客车分支。	READY
7755_mwb_highroof	7755	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	中轴高顶客车分支。	READY
7756	7756	MPV	Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	四驱短轴低顶客车外廓。	READY
7757	7757	Sedan	Nexia	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
7758	7758	Hatchback	Nexia	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH		READY
7759	7759	Coupe	Fiat Coupe	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
7760	7760	Coupe	Fiat Coupe	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
7762	7762	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	HIGH	GT三门外廓。	READY
7763_3dr	7763	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	HIGH	三门分支。	READY
7763_5dr	7763	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	HIGH	五门分支。	READY
7764_prefl	7764	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前外廓。	READY
7764_facelift	7764	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
7765	7765	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7766	7766	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7767	7767	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7768	7768	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
7769	7769	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7770	7770	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
7771	7771	Van	Fiorino II			EU-FIAT-FIORINO-II-VAN-01	MEDIUM	货运/乘用混合标注按共同封闭车身落组。	READY
7773	7773	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH		READY
7774_prefl	7774	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7774_facelift	7774	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7775_prefl	7775	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7775_facelift	7775	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7776_prefl	7776	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7776_facelift	7776	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7778_prefl	7778	MPV	Ducato I 280	280		EU-FIAT-DUCATO-I-PANORAMA-280-01	HIGH	280前期车身。	READY
7778_facelift	7778	MPV	Ducato I 290	290		EU-FIAT-DUCATO-I-PANORAMA-290-01	HIGH	290改款车身。	READY
7779_swb_lowroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	HIGH	280短轴低顶封闭货厢分支。	READY
7779_swb_highroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	HIGH	280短轴高顶封闭货厢分支。	READY
7779_lwb_highroof	7779	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	HIGH	280长轴高顶封闭货厢分支。	READY
7780_prefl_swb_lowroof	7780	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	MEDIUM	280改款前短轴低顶分支。	READY
7780_prefl_swb_highroof	7780	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	MEDIUM	280改款前短轴高顶分支。	READY
7780_prefl_lwb_highroof	7780	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	MEDIUM	280改款前长轴高顶分支。	READY
7780_facelift_swb_lowroof	7780	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	290改款后短轴低顶分支。	READY
7780_facelift_swb_highroof	7780	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	290改款后短轴高顶分支。	READY
7780_facelift_lwb_lowroof	7780	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	290改款后长轴低顶分支。	READY
7780_facelift_lwb_highroof	7780	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	290改款后长轴高顶分支。	READY
7781_swb_lowroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶分支。	READY
7781_swb_highroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶分支。	READY
7781_lwb_lowroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶分支。	READY
7781_lwb_highroof	7781	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶分支。	READY
7782_prefl_swb_lowroof	7782	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	MEDIUM	280改款前短轴低顶分支。	READY
7782_prefl_swb_highroof	7782	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	MEDIUM	280改款前短轴高顶分支。	READY
7782_prefl_lwb_highroof	7782	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	MEDIUM	280改款前长轴高顶分支。	READY
7782_facelift_swb_lowroof	7782	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	290改款后短轴低顶分支。	READY
7782_facelift_swb_highroof	7782	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	290改款后短轴高顶分支。	READY
7782_facelift_lwb_lowroof	7782	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	290改款后长轴低顶分支。	READY
7782_facelift_lwb_highroof	7782	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	290改款后长轴高顶分支。	READY
7783_prefl_swb_lowroof	7783	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	MEDIUM	280改款前短轴低顶分支。	READY
7783_prefl_swb_highroof	7783	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	MEDIUM	280改款前短轴高顶分支。	READY
7783_prefl_lwb_highroof	7783	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	MEDIUM	280改款前长轴高顶分支。	READY
7783_facelift_swb_lowroof	7783	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	290改款后短轴低顶分支。	READY
7783_facelift_swb_highroof	7783	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	290改款后短轴高顶分支。	READY
7783_facelift_lwb_lowroof	7783	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	290改款后长轴低顶分支。	READY
7783_facelift_lwb_highroof	7783	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	290改款后长轴高顶分支。	READY
7784_prefl_swb_lowroof	7784	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	MEDIUM	280改款前短轴低顶分支。	READY
7784_prefl_swb_highroof	7784	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	MEDIUM	280改款前短轴高顶分支。	READY
7784_prefl_lwb_highroof	7784	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	MEDIUM	280改款前长轴高顶分支。	READY
7784_facelift_swb_lowroof	7784	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	290改款后短轴低顶分支。	READY
7784_facelift_swb_highroof	7784	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	290改款后短轴高顶分支。	READY
7784_facelift_lwb_lowroof	7784	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	290改款后长轴低顶分支。	READY
7784_facelift_lwb_highroof	7784	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	290改款后长轴高顶分支。	READY
7785_prefl_swb_lowroof	7785	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	MEDIUM	280改款前短轴低顶分支。	READY
7785_prefl_swb_highroof	7785	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	MEDIUM	280改款前短轴高顶分支。	READY
7785_prefl_lwb_highroof	7785	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	MEDIUM	280改款前长轴高顶分支。	READY
7785_facelift_swb_lowroof	7785	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	290改款后短轴低顶分支。	READY
7785_facelift_swb_highroof	7785	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	290改款后短轴高顶分支。	READY
7785_facelift_lwb_lowroof	7785	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	290改款后长轴低顶分支。	READY
7785_facelift_lwb_highroof	7785	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	290改款后长轴高顶分支。	READY
7786_swb_lowroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶分支。	READY
7786_swb_highroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶分支。	READY
7786_lwb_lowroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶分支。	READY
7786_lwb_highroof	7786	Van	Ducato I	290		EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7201-7300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385	Cumulative DIMENSION_GROUP cache; Lancia Prisma specifications	https://de.wikipedia.org/wiki/Lancia_Prisma
EU-LANCIA-THEMA-I-8-32-SEDAN-01	4590	1733	1420	Automobile-Catalog 1988 Lancia Thema 8.32	https://www.automobile-catalog.com/car/1988/54410/lancia_thema_8_32.html
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-01	4763	1901	1875	Mercedes-Benz Public Archive Viano 639 overview; Auto-Data Mercedes-Benz Viano W639 Facelift CDI 2.2	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://www.auto-data.net/en/mercedes-benz-viano-w639-facelift-2010-cdi-2.2-163hp-automatic-18950
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-01	5008	1901	1875	Mercedes-Benz Public Archive Viano 639 overview; Mercedes-Benz Public Archive Viano CDI 2.2 long	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2010---2014.xhtml?oid=193897441
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRA-LONG-01	5238	1901	1872	Mercedes-Benz Public Archive Viano 639 overview; Mercedes-Benz Public Archive Viano CDI 3.0 extra long	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/639-series-Viano-Multi-Purpose-Vehicles-2010---2014.xhtml?oid=6017058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-extra-long-2010---2014.xhtml?oid=193897450
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425	Automobile-Catalog Subaru Leone 4WD four-door sedan	https://www.automobile-catalog.com/car/1987/3212840/subaru_leone_4wd_4door_sedan_1_6_sg.html
EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	4410	1660	1490	Automobile-Catalog Subaru 4WD station wagon	https://www.automobile-catalog.com/car/1986/3215690/subaru_4wd_1_8_gl_station_wagon_dual_range.html
EU-RENAULT-16-HATCHBACK-5D-01	4240	1650	1450	Renault The Originals R16 TX	https://theoriginals.renault.com/en/r16-tx
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-COMPACT-01	4763	1901	1942	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-LONG-01	5008	1901	1942	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-MERCEDES-BENZ-VITO-W639-BUS-4X4-EXTRA-LONG-01	5238	1901	1939	Mercedes-Benz The Vito official brochure; Drom Mercedes-Benz Vito W639 4X4 dimensions	https://cms.my.na/assets/documents/p18v4tdkgq1b4j1c3qdlc18sg1s122.pdf;https://www.drom.ru/catalog/mercedes-benz/vito/specs/dimensions/
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	3780	1620	1390	Auto-Data Daihatsu Charade IV G200 1.3 i	https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.3-i-ts-75hp-126
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425	Cumulative DIMENSION_GROUP cache; Toyota Corolla E90 wagon specifications	https://www.drom.ru/catalog/toyota/corolla/g_1987_7805/
EU-RENAULT-14-HATCHBACK-5D-01	4025	1624	1405	Automobile-Catalog 1981 Renault 14 TS Regency	https://www.automobile-catalog.com/car/1981/2929745/renault_14_ts_regency.html
EU-SUZUKI-VITARA-I-SUV-OPEN-01	3620	1630	1665	Automobile-Catalog Suzuki Vitara 1.6i Cabrio	https://www.automobile-catalog.com/car/1992/3349355/suzuki_vitara_1_6i_cabrio_automatic.html
EU-SUZUKI-VITARA-I-SUV-CLOSED-3D-WIDEBODY-01	3745	1695	1660	Suzuki Vitara 2.0 16V official specification brochure	https://www.autoweek.nl/autobrochures/download/483/
EU-RENAULT-12-BREAK-WAGON-5D-01	4404	1616	1455	Automobile-Catalog Renault 12 TN Break	https://www.automobile-catalog.com/car/1974/2926640/renault_12_tn_break.html
EU-RENAULT-12-SEDAN-4D-01	4348	1616	1435	Automobile-Catalog 1976 Renault 12 L	https://www.automobile-catalog.com/car/1976/2926670/renault_12_l.html
EU-SUZUKI-VITARA-I-SUV-CLOSED-5D-WIDEBODY-01	4125	1695	1695	Suzuki Vitara Villager V6 official brochure; Suzuki Vitara 5-door Wagon 2.0 Diesel official specification	https://www.autoweek.nl/autobrochures/download/476/;https://www.autoweek.nl/autobrochures/download/485/
EU-RENAULT-11-PHASE2-C37E-HATCHBACK-3D-01	4047	1666	1380	Automobile-Catalog 1987 Renault 11 GTE	https://www.automobile-catalog.com/car/1987/2935100/renault_11_gte.html
EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	3995	1670	1400	Cumulative DIMENSION_GROUP cache; Mazda 323 C IV BG 1.8 16V 4WD specifications	https://carmanuals.ru/tech/tehnicheskie-dannye-mazda-323-c-iv-bg-18-16v-4wd
EU-OPEL-CAMPO-I-PICKUP-SINGLECAB-01	4980	1690	1595	Auto-Data Opel Campo Single Cab	https://www.auto-data.net/en/opel-campo-single-cab-generation-5140
EU-OPEL-CAMPO-I-PICKUP-HALFCAB-01	4980	1690	1710	Auto-Data Opel Campo model overview	https://www.auto-data.net/en/opel-campo-model-233
EU-OPEL-CAMPO-I-PICKUP-DOUBLECAB-01	4980	1690	1710	Auto-Data Opel Campo Double Cab	https://www.auto-data.net/en/opel-campo-double-cab-generation-5141
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375	Tunel.az Mazda 323 S IV BG 163 hp specifications	https://tunel.az/catalog/mazda/323/mazda-323-s-iv-bg/3f6679a3-9421-49bb-9b1a-ab50f0fd13b4
EU-MAZDA-323-F-IV-BG-HATCHBACK-5D-01	4260	1680	1340	Auto-Data Mazda 323 F IV BG 1.8 4WD	https://www.auto-data.net/en/mazda-323-f-iv-bg-1.8-4wd-103hp-11180
EU-OPEL-VIVARO-A-X83-PICKUP-DROPSIDE-01	5350	1990	2000	Vauxhall Vivaro and Movano 2008 Chassis Cabs and Core Conversions	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_ChassisCabConv_August_2007.pdf
EU-BMW-6-F12-CONVERTIBLE-01	4894	1894	1365	BMW Group PressClub 640d xDrive Convertible specifications	https://www.press.bmwgroup.com/global/article/detail/T0124398EN/specifications-bmw-6-series-convertible-640d-xdrive-03/2012?language=en
EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	4085	1620	1390	Auto-Data Daihatsu Charade IV G200 1.5 i 16V	https://www.auto-data.net/en/daihatsu-charade-iv-g200-1.5-i-16v-sx-75hp-122
EU-DAIHATSU-GRAN-MOVE-I-MPV-01	4059	1641	1600	AutoEvolution Daihatsu Gran Move 1.5 90 HP	https://www.autoevolution.com/cars/daihatsu-gran-move-1996.html
EU-CADILLAC-BLS-SEDAN-4D-01	4680	1752	1471	Auto-Data Cadillac BLS 2.0 T 210 Hp	https://www.auto-data.net/en/cadillac-bls-2.0-t-210hp-11691
EU-DAIHATSU-MOVE-I-L601-MPV-01	3310	1400	1699	AutoEvolution Daihatsu Move 0.8 42 HP	https://www.autoevolution.com/cars/daihatsu-move-1997.html
EU-CADILLAC-XLR-V-CONVERTIBLE-01	4514	1836	1280	Edmunds 2006 Cadillac XLR-V specifications	https://www.edmunds.com/cadillac/xlr-v/2006/features-specs/
EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	3295	1395	1435	Cumulative DIMENSION_GROUP cache; Daihatsu Cuore IV L501 specifications	https://www.auto-data.net/en/daihatsu-cuore-model-15
EU-RENAULT-9-L42-SEDAN-PHASE2-01	4132	1666	1410	Auto.ru Renault 9 phase 2 specifications	https://auto.ru/catalog/cars/renault/9/24080821/24080833/specifications/
EU-RENAULT-9-L42-SEDAN-PHASE1-01	4070	1650	1405	Cumulative DIMENSION_GROUP cache; Renault 9 L42 phase 1 specifications	https://www.automobile-catalog.com/model/renault/renault_9.html
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320	Automobile-Catalog 1968 Porsche 911 L Coupe	https://www.automobile-catalog.com/car/1968/2588870/porsche_911_l_coupe.html
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320	Automobile-Catalog 1968 Porsche 911 S Targa	https://www.automobile-catalog.com/car/1968/2589020/porsche_911_s_targa.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog 1972 Porsche 911 T Coupe pre-August	https://www.automobile-catalog.com/car/1972/2590220/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320	Automobile-Catalog 1972 Porsche 911 T Coupe post-August	https://www.automobile-catalog.com/car/1972/2590745/porsche_911_t_coupe.html
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150	Swiss type approval Fiat Ducato 230/14 1.9 TDS CH3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470	Swiss type approval Fiat Ducato 230/14 1.9 TDS CH3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150	Swiss type approval Fiat Ducato 230/14 2.5 TD CH3F2207	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2207_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470	Swiss type approval Fiat Ducato 230/14 2.0 CH3F2208	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2208_F.pdf
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480	Swiss type approval Fiat Ducato 230/18 2.5 TD CH3F2235	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2235_F.pdf
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453	Auto-Data Audi A6 4B C5 1.8 T; Auto-Data Audi A6 4B C5 facelift 1.8 T	https://www.auto-data.net/en/audi-a6-4b-c5-1.8-t-150hp-4693;https://www.auto-data.net/en/audi-a6-4b-c5-facelift-2001-1.8-t-150hp-27079
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440	Cumulative DIMENSION_GROUP cache; Audi A8 D2 specifications	https://catalog.aw.by/49235/
EU-AUDI-CABRIOLET-8G-CONVERTIBLE-FACELIFT-01	4366	1716	1379	Auto-Data Audi Cabriolet B3 8G facelift 1.8 20V	https://www.auto-data.net/en/audi-cabriolet-b3-8g-facelift-1997-1.8-20v-125hp-4247
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410	Cumulative DIMENSION_GROUP cache; Renault 19 II Cabriolet specifications	https://catalog.aw.by/58286/
EU-BMW-5-E39-WAGON-01	4805	1800	1440	Auto-Data BMW 5 Series Touring E39 520i	https://www.auto-data.net/en/bmw-5-series-touring-e39-520i-150hp-9645
EU-BMW-Z3-E36-7-ROADSTER-2-8-01	4025	1740	1293	Auto-Data BMW Z3 E36/7 2.8	https://www.auto-data.net/en/bmw-z3-e36-7-2.8-192hp-9916
EU-OPEL-MOKKA-I-SUV-01	4278	1777	1658	Opel Mokka 2013 official specification	https://opel.psc-zagreb.com/getImage?path=Downloads%2Fcountry_1332918467480%2Fdoc_1365706479747_hr_mokka_2013_04_11.pdf
EU-BMW-Z3-M-E36-7-ROADSTER-01	4025	1740	1266	BMW M Z3 M Roadster technical data	https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-z3-m-roadster.html
EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	4733	1950	1740	Auto-Data Chrysler Voyager III 2.0 I	https://www.auto-data.net/en/chrysler-voyager-iii-2.0-i-133hp-14833
EU-VW-GOLF-PLUS-V-MPV-01	4204	1759	1592	Cumulative DIMENSION_GROUP cache; Volkswagen Golf Plus specifications	https://www.cars-directory.net/gallery/volkswagen/golf_plus/2012/
EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	4200	1790	1624	Automobile-Catalog Jeep Cherokee XJ early specifications	https://www.automobile-catalog.com/car/1990/1312925/jeep_cherokee_limited_4wd_4-door_4_0l_automatic.html
EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	4240	1790	1623	Automobile-Catalog Jeep Cherokee XJ pre-facelift specifications	https://www.automobile-catalog.com/car/1993/1313270/jeep_cherokee_limited_4_0_high_output.html
EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	4251	1790	1625	Automobile-Catalog Jeep Cherokee XJ facelift specifications	https://www.automobile-catalog.com/make/jeep/cherokee_2gen/cherokee_2gen_2_4d/1999.html
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387	Cumulative DIMENSION_GROUP cache; Citroën Xantia X1 specifications	https://www.auto-motor-und-sport.de/marken-modelle/citroen/xantia/technische-daten/
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400	Auto-Data Citroën Xantia X2 2.0 i 16V	https://www.auto-data.net/en/citroen-xantia-x2-2.0-i-16v-132hp-14945
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Cumulative DIMENSION_GROUP cache; Citroën Jumper I passenger-body specifications	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Cumulative DIMENSION_GROUP cache; Citroën Jumper I passenger-body specifications	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Cumulative DIMENSION_GROUP cache; Citroën Jumper I passenger-body specifications	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	4482	1662	1393	Automobile-Catalog Daewoo Nexia GL sedan	https://www.automobile-catalog.com/car/1995/555155/daewoo_nexia_gl_sedan.html
EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	4256	1662	1393	Automobile-Catalog Daewoo Nexia GL hatchback	https://www.automobile-catalog.com/car/1995/555095/daewoo_nexia_gl_hatchback.html
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340	Cumulative DIMENSION_GROUP cache; Fiat Coupé 175 specifications	https://en.wikipedia.org/wiki/Fiat_Coup%C3%A9
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450	Auto-Data Fiat Punto I 176 GT 1.4 Turbo	https://www.auto-data.net/en/fiat-punto-i-176-gt-1.4-turbo-133hp-6993
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460	Cumulative DIMENSION_GROUP cache; Fiat Punto I 176 specifications	https://en.wikipedia.org/wiki/Fiat_Punto
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460	Cumulative DIMENSION_GROUP cache; Fiat Punto I 176 specifications	https://en.wikipedia.org/wiki/Fiat_Punto
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318	Cumulative DIMENSION_GROUP cache; Alfa Romeo GTV 916 pre-facelift specifications	https://en.wikipedia.org/wiki/Alfa_Romeo_GTV_and_Spider
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318	Cumulative DIMENSION_GROUP cache; Alfa Romeo GTV 916 facelift specifications	https://en.wikipedia.org/wiki/Alfa_Romeo_GTV_and_Spider
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427	Cumulative DIMENSION_GROUP cache; Alfa Romeo 145 930 specifications	https://en.wikipedia.org/wiki/Alfa_Romeo_145_and_146
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425	Cumulative DIMENSION_GROUP cache; Alfa Romeo 146 930 specifications	https://en.wikipedia.org/wiki/Alfa_Romeo_145_and_146
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904	Cumulative DIMENSION_GROUP cache; Fiat Fiorino II specifications	https://en.wikipedia.org/wiki/Fiat_Fiorino
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 290 Panorama specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 280 Panorama specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4759	1965	2100	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	4759	1965	2400	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	5489	1965	2400	Swiss type approval Fiat Ducato 280/14 CH3F2017	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2017_F.pdf
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 290 van specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 290 van specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 290 van specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450	Cumulative DIMENSION_GROUP cache; Fiat Ducato I 290 van specifications	https://en.wikipedia.org/wiki/Fiat_Ducato
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7201-7300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7201-7300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7201-7300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9303 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2856 行）

