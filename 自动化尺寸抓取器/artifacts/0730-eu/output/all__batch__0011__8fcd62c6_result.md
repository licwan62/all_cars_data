# 任务：all 第 1001-1100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0011__8fcd62c6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1001-1100 行

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
all 第 1001-1100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-AUDI-TT-8S-RS-COUPE-01	4191	1832	1344
EU-AUDI-TT-8S-RS-ROADSTER-01	4191	1832	1346
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	6505	2024	1935
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	6025	2024	1935
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	6264	2024	1935
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	5784	2024	1935
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	5641	2024	2024
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-RWD-01	5641	2024	1935
EU-FIAT-500-312-FACELIFT-HATCHBACK-3D-01	3571	1627	1488
EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	4800	1890	1685
EU-KIA-SORENTO-III-UM-SUV-PREFL-01	4780	1890	1685
EU-KIA-SPORTAGE-IV-QL-SUV-01	4480	1855	1635
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448
EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	4267	1732	1445
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	4295	1690	1385
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465
EU-TOYOTA-DYNA-100-LY100-PICKUP-01	4415	1695	1830
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
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	5008	2.0 Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Dec 2016	-	2024-03-01	124952
Peugeot	5008	2.0 Bluehdi 180	Großraumlimousine	Frontantrieb	Diesel	133	181	Dec 2016	-	2024-03-01	124953
Citroën	Jumpy iii	2.0 Bluehdi 180	Bus	Frontantrieb	Diesel	130	177	Apr 2016	Apr 2025	2025-12-01	124959
Renault	Clio iii	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Nov 2005	Dec 2014	2026-05-01	124975
Renault	Clio iii	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Nov 2007	Dec 2011	2026-05-01	124977
BMW	5	525 I	Kombi	Heckantrieb	Benzin	155	211	Jan 2007	Dec 2010	2024-03-01	124994
Ferrari	Gtc4 lusso / t	3.9 T	Coupe	Heckantrieb	Benzin	449	610	Oct 2016	-	2024-03-01	124998
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	100	136	Jul 2013	Jun 2014	2024-03-01	125041
Mazda	Mx-5 rf	2	Targa	Heckantrieb	Benzin	118	160	Dec 2016	-	2024-03-01	125056
BMW	5	518 D	Kombi	Heckantrieb	Diesel	120	163	Jul 2014	Feb 2017	2024-03-01	125059
BMW	5	530 I	Kombi	Heckantrieb	Benzin	190	258	Mar 2010	May 2013	2024-03-01	125091
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	75	102	Oct 2016	Jun 2024	2025-04-01	125092
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	103	140	Sep 2016	-	2025-04-01	125093
VW	Crafter	2.0 TDI FWD	Bus	Frontantrieb	Diesel	130	177	Sep 2016	-	2025-04-01	125094
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	155	211	Jan 2010	Aug 2011	2024-03-01	125098
BMW	5	530 I	Stufenheck	Heckantrieb	Benzin	190	258	Mar 2010	Jun 2013	2024-03-01	125102
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	120	163	Oct 2013	Oct 2016	2024-03-01	125105
Aston Martin	Rapide	6.0 S	Schrägheck	Heckantrieb	Benzin	412	560	Aug 2014	-	2024-03-01	125126
BMW	5	520 D	Schrägheck	Heckantrieb	Diesel	100	136	Jul 2013	Feb 2017	2024-03-01	125128
Peugeot	Expert	1.6 Bluehdi 95	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Sep 2016	Dec 2019	2025-12-01	125133
Peugeot	Expert	2.0 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	90	122	Sep 2016	Dec 2022	2025-12-01	125134
Peugeot	Expert	2.0 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	110	150	Sep 2016	Dec 2022	2025-12-01	125135
Audi	A5	3.0 TDI Quattro	Coupe	Allrad	Diesel	200	272	Feb 2017	Dec 2017	2024-03-01	125153
Audi	A5	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	200	272	Feb 2017	Dec 2017	2024-03-01	125154
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	206	280	Dec 2016	-	2024-03-01	125157
Mercedes-benz	E-Klasse	E 200 4-matic	Kombi	Allrad	Benzin	135	184	Jan 2017	Jun 2019	2024-03-01	125163
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel	143	194	Jan 2017	Oct 2023	2024-03-01	125164
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel	143	194	Jan 2017	Oct 2023	2024-03-01	125165
Mercedes-benz	E-Klasse	AMG E 63 4-matic+	Stufenheck	Allrad	Benzin	420	571	Jan 2017	Nov 2021	2024-03-01	125169
Mercedes-benz	E-Klasse	AMG E 63 S 4-matic+	Stufenheck	Allrad	Benzin	450	612	Jan 2017	Oct 2023	2024-03-01	125170
BMW	3	320 I	Kombi	Heckantrieb	Benzin	120	163	Nov 2012	Jun 2015	2024-03-01	125171
BMW	3	320 I Xdrive	Kombi	Allrad	Benzin	120	163	Mar 2013	Jun 2015	2024-03-01	125172
Audi	Q5	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Jan 2017	Nov 2020	2024-03-01	125183
Audi	Q5	SQ5 Tfsi Quattro	SUV	Allrad	Benzin	260	354	Nov 2016	-	2024-03-01	125184
Audi	Q5	2.0 TDI	SUV	Frontantrieb	Diesel	100	136	Jan 2017	Nov 2020	2024-03-01	125199
Citroën	Jumpy iii	1.6 Bluehdi 95	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Sep 2016	Apr 2020	2025-02-03	125208
Toyota	Corolla	1.6	Coupe	Heckantrieb	Benzin	91	124	May 1987	Apr 1992	2024-03-01	125212
Citroën	Jumpy iii	2.0 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	90	122	Sep 2016	Dec 2022	2025-12-01	125213
Citroën	Jumpy iii	2.0 Bluehdi 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	110	150	Sep 2016	Dec 2022	2025-12-01	125214
Hyundai	Ix35	2.0 4WD	SUV	Allrad	Benzin	116	158	Sep 2014	Jun 2015	2024-03-01	125220
VW	Jetta iv	1.2 TSI 16V	Stufenheck	Frontantrieb	Benzin	77	105	Aug 2014	Dec 2017	2024-03-01	125249
Honda	Cr-V v	1.5 AWD	SUV	Allrad	Benzin	142	193	Dec 2016	-	2024-03-01	125265
Fiat	500	0.9	Cabriolet	Frontantrieb	Benzin	44	60	Dec 2013	-	2024-03-01	125291
VW	Polo	1.9 TDI	Stufenheck	Frontantrieb	Diesel	74	101	Jul 2003	Dec 2010	2024-03-01	125292
Citroën	Xm	3.0 V6 24V	Kombi	Frontantrieb	Benzin	147	200	Jan 1990	Jul 1994	2024-03-01	125303
Renault	Clio iv	1.2 LPG 16V	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	54	73	Nov 2012	Jun 2015	2026-05-01	125321
Toyota	Dyna	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	55	75	Aug 1987	Apr 1995	2024-03-01	125328
BMW	5	530 I	Kombi	Heckantrieb	Benzin	185	252	Mar 2017	Jun 2020	2024-03-01	125336
BMW	5	540 I Xdrive	Kombi	Allrad	Benzin	250	340	Mar 2017	Jun 2020	2024-03-01	125337
BMW	5	540 I Xdrive	Kombi	Allrad	Benzin	265	360	Mar 2017	Jun 2020	2024-03-01	125338
BMW	5	520 D	Kombi	Heckantrieb	Diesel	140	190	Mar 2017	-	2024-03-01	125339
BMW	5	530 D	Kombi	Heckantrieb	Diesel	195	265	Mar 2017	Jun 2020	2024-03-01	125340
BMW	5	530 D Xdrive	Kombi	Allrad	Diesel	195	265	Mar 2017	Jun 2020	2024-03-01	125341
BMW	5	530 E Plug-in Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	185	252	Mar 2017	Jun 2020	2025-06-01	125343
BMW	5	530 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	185	252	Mar 2017	Jun 2023	2024-03-01	125345
Mini	Mini	Cooper SE All4	Kombi	Allrad	Benzin/Elektro	165	224	Jan 2017	-	2024-03-01	125347
Mini	Mini	John Cooper Works All4	Kombi	Allrad	Benzin	170	231	Mar 2017	Jun 2019	2024-03-01	125348
Nissan	X-Trail iii	2.0 DCI	SUV	Frontantrieb	Diesel	130	177	Oct 2016	-	2024-03-01	125349
Nissan	X-Trail iii	2.0 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	130	177	Oct 2016	-	2024-03-01	125350
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	135	184	Jan 2017	-	2024-03-01	125351
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	135	184	Jan 2017	-	2024-03-01	125352
Mitsubishi	3000 gt	3.0 4WD	Coupe	Allrad	Benzin	165	224	Jun 1989	Aug 1999	2024-03-01	125427
Mitsubishi	3000 gt	3	Coupe	Frontantrieb	Benzin	165	224	Dec 1990	May 1993	2024-03-01	125430
Chevrolet	Silverado 2500	8.1 AWD	Pick-up	Allrad	Benzin	254	345	Oct 2001	Aug 2006	2024-03-01	125438
Mitsubishi	Galant viii	3	Stufenheck	Frontantrieb	Benzin	152	207	Jan 1999	Dec 2003	2024-03-01	125440
Toyota	Mr2 ii	2.2	Coupe	Heckantrieb	Benzin	100	136	Jan 1992	May 1995	2024-03-01	125446
Fiat	Scudo	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	58	79	Sep 1996	Dec 2006	2024-03-01	125474
Chevrolet	Tahoe	6.2 4WD	SUV	Allrad	Benzin	301	409	Oct 2015	-	2024-03-01	125493
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	123	167	Sep 1974	Dec 1975	2024-03-01	125500
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	186	253	Sep 1989	Dec 1990	2024-03-01	125504
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	287	390	Sep 1989	Dec 1990	2024-03-01	125505
Chevrolet	Caprice	5.7	Stufenheck	Heckantrieb	Benzin	116	158	Sep 1974	Dec 1975	2024-03-01	125527
Mitsubishi	Lancer iv	EVO IV	Stufenheck	Allrad	Benzin	206	280	Aug 1996	Dec 1997	2024-03-01	125528
Chevrolet	Malibu	5	Stufenheck	Heckantrieb	Benzin	108	147	Sep 1977	Dec 1979	2024-03-01	125554
Chevrolet	Malibu	5	Coupe	Heckantrieb	Benzin	115	156	Sep 1979	Dec 1983	2024-03-01	125565
Mitsubishi	Lancer vii	EVO VII	Stufenheck	Allrad	Benzin	206	280	Jan 2001	Jan 2003	2024-03-01	125584
KIA	Sorento iii	3.3 4WD	SUV	Allrad	Benzin	199	271	Apr 2015	Dec 2018	2024-05-01	125588
KIA	Sportage iv	2.0 AWD	SUV	Allrad	Benzin	114	155	Dec 2015	Sep 2022	2024-03-01	125591
Mitsubishi	Lancer vii	EVO Viii	Stufenheck	Allrad	Benzin	206	280	Apr 2003	Mar 2005	2024-03-01	125592
Mitsubishi	Lancer vii	EVO Viii - Fq-300	Stufenheck	Allrad	Benzin	225	305	Apr 2003	Apr 2004	2024-03-01	125593
Mitsubishi	Lancer vii	EVO Viii - Fq-300	Stufenheck	Allrad	Benzin	227	309	Apr 2003	Apr 2004	2024-03-01	125594
Mitsubishi	Lancer vii	EVO Viii - Fq-330	Stufenheck	Allrad	Benzin	246	334	Oct 2003	Aug 2006	2026-06-01	125596
Mitsubishi	Lancer vii	EVO Viii - Fq-340	Stufenheck	Allrad	Benzin	255	347	Apr 2004	Mar 2005	2024-03-01	125600
Mitsubishi	Lancer vii	EVO Viii - Fq-400	Stufenheck	Allrad	Benzin	302	411	Oct 2004	Aug 2006	2024-03-01	125602
Mitsubishi	Lancer vii	EVO IX - Fq-360	Stufenheck	Allrad	Benzin	273	371	Jul 2006	Dec 2007	2024-03-01	125608
Lancia	Thema	2000 I.e. Turbo	Kombi	Frontantrieb	Benzin	122	166	Jun 1987	Jul 1994	2024-03-01	125609
Microcar	F8	0.5	Schrägheck	Frontantrieb	Diesel	4	5	Feb 2013	-	2024-03-01	125693
Microcar	F8	0.5	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2014	-	2024-03-01	125694
Seat	Leon	2.0 Cupra	Schrägheck	Frontantrieb	Benzin	221	300	Jan 2017	Aug 2018	2024-03-01	125703
Seat	Leon	2.0 Cupra	Coupe	Frontantrieb	Benzin	221	300	Jan 2017	Aug 2018	2024-03-01	125718
Seat	Leon	2.0 Cupra	Kombi	Frontantrieb	Benzin	221	300	Nov 2016	Aug 2018	2024-03-01	125719
Seat	Leon	2.0 Cupra 4drive	Kombi	Allrad	Benzin	221	300	Nov 2016	Aug 2020	2024-03-01	125720
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	131	178	Jan 2010	Dec 2015	2024-03-01	125748
Isuzu	Gemini	1.5	Schrägheck	Frontantrieb	Benzin	56	76	Jan 1985	Dec 1987	2024-03-01	125793
Isuzu	Gemini	1.6 GTI 16V	Schrägheck	Frontantrieb	Benzin	92	125	Mar 1988	Jun 1990	2024-03-01	125799
Isuzu	Piazza	2	Coupe	Heckantrieb	Benzin	75	102	Jun 1981	Aug 1985	2024-03-01	125804
Ford	Maverick	2.0 16V FWD	SUV	Frontantrieb	Benzin	91	124	Feb 2001	-	2024-03-01	125811
Ford	Maverick	3.0 V6 24V FWD	SUV	Frontantrieb	Benzin	145	197	Feb 2001	-	2024-03-01	125812
Ford	Escort ii	1.6	Stufenheck	Heckantrieb	Benzin	64	87	Jan 1979	Dec 1980	2024-03-01	125814
Jaguar	F-Type	3.0 Scv6 400 Sport	Coupe	Heckantrieb	Benzin	294	400	Nov 2016	-	2024-03-01	125815


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 12 个历史尺寸组的直接复用，不重复输出其三维和来源。
* 新建并闭合 4 个 BMW 尺寸组。BMW 官方 2013 年资料确认 F10 Sedan 为 4907×1860×1464 mm、F11 Touring 为 4907×1860×1462 mm、F07 Gran Turismo 为 5004×1901×1559 mm。
* BMW 官方 2017 年 G31 规格表确认普通 G31 Touring 外廓为 4943×1868×1498 mm。
* 对跨越已确认尺寸变化改款的 Ktype `125345`、`125588` 分别建立改款前后派生映射。
* F10/F11 前期车型及结束时间未知的 G31 520d 暂不猜测复用，保持 PENDING。

## 当前批次进度

* 已闭合输入 Ktype：23 / 100
* READY 映射：25
* 已明确进入 PENDING：4
* 尚未闭合输入 Ktype：77
* 本轮复用历史尺寸组：12
* 本轮首次创建尺寸组：4
* 当前已引用并闭合尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124952	124952	SUV	5008 II		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	MEDIUM	输入Großraumlimousine，按第二代5008五门SUV外廓归类。	READY
124953	124953	SUV	5008 II		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	MEDIUM	输入Großraumlimousine，按第二代5008五门SUV外廓归类。	READY
125041	125041	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11改款旅行车物理外廓。	READY
125059	125059	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11改款旅行车物理外廓。	READY
125091	125091	Wagon	5 Series VI	F11	5		MEDIUM	候选F11前期旅行车；需确认前期三维是否与2013改款组完全一致。	PENDING: F11前期三维与改款组复用边界未确认
125098	125098	Sedan	5 Series VI	F10	4		MEDIUM	候选F10前期三厢；需补官方前期尺寸。	PENDING: F10前期三维尚未闭合
125102	125102	Sedan	5 Series VI	F10	4		MEDIUM	候选F10前期三厢；需补官方前期尺寸。	PENDING: F10前期三维尚未闭合
125105	125105	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	F10改款三厢物理外廓。	READY
125128	125128	Hatchback	5 Series VI	F07	5	EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	HIGH	F07 Gran Turismo五门掀背物理外廓。	READY
125153	125153	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH	F5双门Coupe物理外廓。	READY
125154	125154	Hatchback	A5 II (F5)	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback五门掀背物理外廓。	READY
125183	125183	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
125199	125199	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
125336	125336	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125337	125337	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125338	125338	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125339	125339	Wagon	5 Series VII	G31	5		MEDIUM	结束时间未知，140kW 520d版本可能跨越G31外廓变化改款。	PENDING: 结束时间未知且可能跨G31改款尺寸变化
125340	125340	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125341	125341	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125343	125343	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	G30改款前三厢物理外廓。	READY
125345_prefl	125345	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125345_facelift	125345	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125588_prefl	125588	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-PREFL-01	HIGH	同一Ktype覆盖Sorento III改款前外廓。	READY
125588_facelift	125588	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	HIGH	同一Ktype覆盖Sorento III改款后外廓。	READY
125591	125591	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-QL-SUV-01	HIGH		READY
125703	125703	Hatchback	Leon III	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Leon 5F改款五门掀背外廓。	READY
125718	125718	Coupe	Leon III	5F	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	HIGH	Leon SC改款三门外廓。	READY
125719	125719	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH	Leon ST改款旅行车外廓。	READY
125720	125720	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH	Leon ST改款旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498	BMW Group PressClub 2017 BMW 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0267496EN/384763
```

## 下一步优先处理

1. 以共平台车身簇批量处理 Peugeot Expert、Citroën Jumpy III 和 Fiat Scudo，并先拆清 Bus、Chassis Cab、长度及车顶分支。
2. 闭合 BMW F10/F11 前期尺寸组，并判断 `125339` 是否需要拆分 G31 改款前后分支。
3. 批量处理 Mercedes-Benz W213/S213、Audi SQ5 FY、Alfa Romeo Stelvio、Honda CR-V V 和 Nissan X-Trail III 等现代车型。
4. 后续集中处理 Corvette、Lancer Evolution、3000 GT、Galant、Malibu、Caprice 等历史车型簇。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 已消除上一轮 4 条 PENDING：F11 前期三维与现有组一致；F10 前期单独建组；无结束时间的 G31 520d 按改款前后尺寸差异拆分。BMW 官方资料同时确认 F31 后驱与 xDrive 高度分别为 1429 mm、1434 mm，因此建立两个尺寸组。
* 首次闭合 Ferrari GTC4Lusso T、Mazda MX-5 RF 和 Audi SQ5 FY 尺寸组。([法拉利官网][1])
* 首次闭合 Mercedes-Benz S213 改款前旅行车，以及 Audi TT 8S Coupe、Roadster 两种外廓。([汽车数据网][2])
* Renault Clio IV、Toyota Dyna 100、MINI F54 直接复用已有尺寸组，本轮不重复输出尺寸和来源。

## 2. 当前批次进度

* READY 输入 Ktype：39 / 100
* READY 映射：42
* 待闭合输入 Ktype：61
* 当前已引用并闭合尺寸组：29
* 本轮首次创建尺寸组：10
* 本轮新增复用历史尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124998	124998	Coupe	GTC4Lusso			EU-FERRARI-GTC4LUSSO-T-COUPE-01	HIGH	GTC4Lusso T三门掀背式Coupe外廓。	READY
125056	125056	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX-5-ND-RF-01	HIGH	RF电动硬顶车身外廓。	READY
125091	125091	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11前期与现有尺寸组外廓三维一致。	READY
125098	125098	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	F10改款前三厢外廓。	READY
125102	125102	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	F10改款前三厢外廓。	READY
125163	125163	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	S213改款前旅行车外廓。	READY
125171	125171	Wagon	3 Series VI	F31	5	EU-BMW-3-F31-WAGON-PREFL-RWD-01	HIGH	F31改款前后驱旅行车外廓。	READY
125172	125172	Wagon	3 Series VI	F31	5	EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	HIGH	xDrive车身高度与后驱版本不同。	READY
125184	125184	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-01	HIGH	SQ5专属外廓高度。	READY
125321	125321	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	改款前后外廓三维一致，复用稳定尺寸组。	READY
125328	125328	Pickup	Dyna 100	LY100	2	EU-TOYOTA-DYNA-100-LY100-PICKUP-01	HIGH	LY100单排底盘车外廓。	READY
125339_prefl	125339	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125339_facelift	125339	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125347	125347	Wagon	MINI III	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman外廓。	READY
125348	125348	Wagon	MINI III	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman外廓。	READY
125351	125351	Coupe	TT III	8S	3	EU-AUDI-TT-8S-COUPE-01	HIGH	8S三门Coupe外廓。	READY
125352	125352	Convertible	TT III	8S	2	EU-AUDI-TT-8S-ROADSTER-01	HIGH	8S双门Roadster外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FERRARI-GTC4LUSSO-T-COUPE-01	4922	1980	1383	Ferrari GTC4Lusso T official reveal press release	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/cs_ferrari_gtc4lusso_t_reveal_gbr.pdf
EU-MAZDA-MX-5-ND-RF-01	3915	1735	1235	Mazda Motor Europe MX-5 official press material	https://at.mazda-press.com/api/assets/download/b8bde554-f284-41d2-bc9c-b544e1d9abe7_Default?isDownload=false
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	BMW Group PressClub ActiveHybrid 5 specifications	https://www.press.bmwgroup.com/global/article/attachment/T0121796EN/190364
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E 220d 4MATIC S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-220d-194hp-4matic-9g-tronic-30787
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429	BMW Group PressClub BMW 320i Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0132112EN/207745/Specifications_BMW_3_Series_Touring_320i_11_2012.pdf
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434	BMW Group PressClub BMW 320i xDrive Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208685/Specifications_BMW_3_Series_Touring_320i_xDrive_03_2013.pdf
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635	Audi UK SQ5 TFSI technical data	https://press.audi.co.uk/assets/documents/original/21087-AudiUK00017568AudiSQ5TFSIQ520TDI.pdf
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub BMW 530e Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0317776EN/461553
EU-AUDI-TT-8S-COUPE-01	4177	1832	1353	Auto-Data Audi TT Coupe 8S 2.0 TDI quattro	https://www.auto-data.net/se/audi-tt-coupe-8s-2.0-tdi-184hp-quattro-s-tronic-31768
EU-AUDI-TT-8S-ROADSTER-01	4177	1832	1355	Auto-Data Audi TT Roadster 8S 2.0 TDI quattro	https://www.auto-data.net/en/audi-tt-roadster-8s-2.0-tdi-184hp-quattro-s-tronic-30307
```

## 5. 下一步优先处理

1. 批量闭合 Peugeot Expert、Citroën Jumpy III、Fiat Scudo 的 Bus、Chassis Cab、长度和车顶分支。
2. 处理 Mercedes-Benz W213 AMG E63、S213 跨改款 Ktype，并避免把普通车身与 AMG 宽体混组。
3. 闭合 Alfa Romeo Stelvio、Honda CR-V V、Nissan X-Trail III、Hyundai ix35 等 SUV。
4. 按代际集中处理 Corvette、Lancer Evolution、3000 GT、Galant、Malibu、Caprice 等历史车型。

推进信号：CONTINUE

[1]: https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/cs_ferrari_gtc4lusso_t_reveal_gbr.pdf?utm_source=chatgpt.com "Ferrari GTC4Lusso T revealed First four-seater in Prancing ..."
[2]: https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-220d-194hp-4matic-g-tronic-30787 "Mercedes-Benz E-class T-modell (S213) E 220d (194 Hp) 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Mercedes-Benz S213 普通旅行车改款后尺寸组；`125164`、`125165` 均跨越尺寸变化改款，分别拆为改款前、改款后分支。另闭合 W213 AMG E 63 改款前三厢外廓。([汽车数据网][1])
* 闭合 Aston Martin Rapide S、Alfa Romeo Stelvio、Hyundai ix35、Volkswagen Jetta VI、Honda CR-V V、Fiat 500 C 和 Jaguar F-Type 400 Sport。([汽车数据网][2])
* 闭合 Chevrolet Tahoe IV 与 Ford Maverick II；两个 Maverick Ktype 复用同一五门 SUV 尺寸组。([汽车数据网][3])
* 本轮新增 READY 输入 Ktype 13 个、新建尺寸组 11 个；未重复输出既有 S213 改款前尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：52 / 100
* READY 映射：57
* 尚未闭合输入 Ktype：48
* 已引用并闭合尺寸组：40
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125126	125126	Hatchback	Rapide S		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S五门掀背外廓。	READY
125157	125157	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
125164_prefl	125164	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125164_facelift	125164	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125165_prefl	125165	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125165_facelift	125165	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125169	125169	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63-SEDAN-PREFL-01	HIGH	W213 AMG E 63改款前宽体三厢外廓。	READY
125220	125220	SUV	ix35 I facelift		5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	MEDIUM	ix35改款后五门SUV外廓。	READY
125249	125249	Sedan	Jetta VI facelift		4	EU-VW-JETTA-VI-SEDAN-FACELIFT-01	HIGH	输入代际标签与生产期不一致，按Jetta VI改款车型归类。	READY
125265	125265	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-01	MEDIUM	CR-V第五代五门SUV外廓。	READY
125291	125291	Convertible	500	312	3	EU-FIAT-500-312-CABRIOLET-PREFL-01	MEDIUM	500 C改款前软顶车身外廓。	READY
125493	125493	SUV	Tahoe IV	K2UC	5	EU-CHEVROLET-TAHOE-IV-K2UC-SUV-01	MEDIUM	K2UC五门SUV外廓。	READY
125811	125811	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-01	HIGH		READY
125812	125812	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-01	MEDIUM	输入驱动信息与常见3.0 V6配置不一致；不影响五门车身外廓边界。	READY
125815	125815	Coupe	F-Type facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH	400 Sport改款双门Coupe外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	5020	1929	1360	Auto-Data Aston Martin Rapide S	https://www.auto-data.net/en/aston-martin-rapide-s-generation-4935
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Auto-Data Alfa Romeo Stelvio 2.0 280 AWD	https://www.auto-data.net/en/alfa-romeo-stelvio-949-2.0-280hp-awd-automatic-28578
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Auto-Data Mercedes-Benz E 220d S213 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-194hp-9g-tronic-40982
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63-SEDAN-PREFL-01	4988	1907	1468	Auto-Data Mercedes-AMG E 63 W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-v8-571hp-4matic-mct-29710
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655	Auto-Data Hyundai ix35 facelift 2.0 GDI 4x4	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-2.0-gdi-166hp-4x4-automatic-18560
EU-VW-JETTA-VI-SEDAN-FACELIFT-01	4659	1778	1482	Autodata1 Volkswagen Jetta VI facelift 1.2 TSI	https://www.autodata1.com/en/car/volkswagen/jetta/jetta-vi-facelift-2014-12-tsi-105-hp
EU-HONDA-CR-V-V-SUV-01	4587	1854	1689	Auto-Data Honda CR-V V 1.5 AWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-190hp-awd-automatic-33228
EU-FIAT-500-312-CABRIOLET-PREFL-01	3546	1627	1488	Auto-Data Fiat 500 C 0.9 TwinAir	https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354
EU-CHEVROLET-TAHOE-IV-K2UC-SUV-01	5179	2045	1890	Auto-Data Chevrolet Tahoe 6.2 AWD	https://www.auto-data.net/en/chevrolet-tahoe-gmtk2uc-g-6.2-v8-420hp-awd-automatic-33466
EU-FORD-MAVERICK-II-SUV-01	4394	1781	1722	Auto-Data Ford Maverick II 2.0	https://www.auto-data.net/en/ford-maverick-ii-2.0-i-16v-124hp-7544
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311	Auto-Data Jaguar F-Type 400 Sport Coupe	https://www.auto-data.net/en/jaguar-f-type-coupe-facelift-2017-3.0-v6-400hp-automatic-27595
```

## 5. 下一步优先处理

1. 处理 Peugeot Expert、Citroën Jumpy III、Fiat Scudo 的 Bus 与 Chassis Cab 长度、车顶和轴距分支。
2. 闭合 Mercedes-AMG E 63 S 改款前后尺寸冲突及 Nissan X-Trail III 精确高度分支。
3. 集中处理 Mitsubishi Lancer Evolution、3000 GT、Galant、L200 等共享代际车型。
4. 最后处理 Corvette、Malibu、Caprice、MR2、Isuzu Gemini/Piazza 等历史车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-194hp-9g-tronic-40982?utm_source=chatgpt.com "Mercedes-Benz E-class T-modell (S213, facelift 2020 ..."
[2]: https://www.auto-data.net/en/aston-martin-rapide-s-generation-4935 "Aston Martin Rapide S | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/chevrolet-tahoe-gmtk2uc-g-6.2-v8-420hp-awd-automatic-33466 "Chevrolet Tahoe (GMTK2UC/G) 6.2 V8 (420 Hp) AWD Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 完成 Mercedes-AMG E 63 S W213 跨改款拆分：改款前后长度、宽度及高度均发生变化，分别建立独立尺寸组；不复用上一轮普通 E 63 的尺寸组。([汽车数据网][1])
* 完成 Nissan X-Trail III 2.0 dCi 前驱、四驱 Ktype 的改款前后拆分；同一时期前驱和四驱复用相同车身尺寸组。改款后采用官方 Nissan 基础车身口径，不含选装 19 英寸轮胎造成的额外宽度，也不含车顶行李架高度。([汽车数据网][2])
* 批量闭合 Mitsubishi Lancer Evolution IV、VII、VIII 和 IX FQ-360。Evolution VIII 各 FQ-300/FQ-330/FQ-340/FQ-400 版本复用同一外廓尺寸组。([汽车数据网][3])

## 2. 当前批次进度

* READY 输入 Ktype：64 / 100
* READY 映射：72
* 尚未闭合输入 Ktype：36
* 已引用并闭合尺寸组：48
* 本轮新增 READY 输入 Ktype：12
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125170_prefl	125170	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125170_facelift	125170	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125349_prefl	125349	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125349_facelift	125349	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125350_prefl	125350	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125350_facelift	125350	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125528	125528	Sedan	Lancer Evolution IV	CN9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IV-CN9A-SEDAN-01	HIGH		READY
125584	125584	Sedan	Lancer Evolution VII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VII-CT9A-SEDAN-01	HIGH		READY
125592	125592	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII。	READY
125593	125593	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-300。	READY
125594	125594	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-300。	READY
125596	125596	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-330。	READY
125600	125600	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-340。	READY
125602	125602	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-400。	READY
125608	125608	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-CT9A-FQ360-SEDAN-01	HIGH	按VariantName识别为Evolution IX FQ-360。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-PREFL-01	4988	1907	1463	Auto-Data Mercedes-AMG E 63 S W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-s-v8-612hp-4matic-mct-29924
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-FACELIFT-01	4940	1852	1460	Auto-Data Mercedes-AMG E 63 S W213 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-amg-e-63-s-612hp-4matic-amg-speedshift-mct-40870
EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	4640	1820	1715	Auto-Data Nissan X-Trail III T32 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-iii-t32-2.0-dci-177hp-xtronic-29978
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Nissan X-Trail 2017 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/X-Trail%20Brochure%202017.10.pdf
EU-MITSUBISHI-LANCER-EVOLUTION-IV-CN9A-SEDAN-01	4330	1690	1415	Auto-Data Mitsubishi Lancer Evolution IV	https://www.auto-data.net/en/mitsubishi-lancer-evolution-iv-2.0-280hp-4wd-42185
EU-MITSUBISHI-LANCER-EVOLUTION-VII-CT9A-SEDAN-01	4455	1770	1450	Auto-Data Mitsubishi Lancer Evolution VII	https://www.auto-data.net/en/mitsubishi-lancer-evolution-vii-generation-3443
EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	4490	1770	1450	Automobile-Catalog Mitsubishi Lancer Evolution VIII 2004 full range	https://www.automobile-catalog.com/make/mitsubishi/lancer_evolution_3/lancer_evolution_viii/2004.html
EU-MITSUBISHI-LANCER-EVOLUTION-IX-CT9A-FQ360-SEDAN-01	4490	1770	1450	Automobile-Catalog Mitsubishi Lancer Evo IX MR FQ-360	https://www.automobile-catalog.com/car/2007/1998110/mitsubishi_lancer_evo_ix_mr_fq-360.html
```

## 5. 下一步优先处理

1. 闭合 Mitsubishi 3000 GT、Galant VIII、L200 和 Toyota MR2 II。
2. 处理 Corvette C3/C4、Chevrolet Caprice、Malibu 及 Silverado 2500 多 CAB/BED 分支。
3. 集中处理 Peugeot Expert、Citroën Jumpy III、Fiat Scudo 和 VW Crafter 的长度、车顶及底盘车分支。
4. 最后处理 Renault Clio III、VW Polo Sedan、Citroën XM Wagon、Lancia Thema Wagon、Microcar F8、Isuzu Gemini/Piazza 和 Ford Escort II。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-amg-e-63-s-612hp-4matic-amg-speedshift-mct-40870 "Mercedes-Benz E-class (W213, facelift 2020) AMG E 63 S (612 Hp) 4MATIC+ AMG SPEEDSHIFT MCT | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/nissan-x-trail-iii-t32-2.0-dci-177hp-xtronic-29978 "Nissan X-Trail III (T32) 2.0 dCi (177 Hp) Xtronic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mitsubishi-lancer-evolution-iv-2.0-280hp-4wd-42185?utm_source=chatgpt.com "Mitsubishi Lancer Evolution IV 2.0 (280 Hp) 4WD"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 BMW E61 Touring、Toyota Corolla AE92 Coupe、Citroën XM Y3 Break、Mitsubishi 3000GT 和 Galant VIII 等历史车型；`125427` 因 3000GT 前后期长度变化拆分为两个物理分支。([汽车目录][1])
* 闭合 Toyota MR2 II、Corvette C3、Corvette C4 普通版与 ZR-1、Caprice II 和 Malibu III；C4 ZR-1 因宽体外廓独立建组，`125565` 因 Malibu Coupe 生产期跨越尺寸变化拆分为前后期。([Edmunds][2])
* 闭合 Lancia Thema Wagon、Isuzu Gemini 两种外廓及 Isuzu Piazza；Ford Escort II 的欧洲规格边界尚未闭合，本轮未创建猜测性尺寸组。([汽车目录][3])

## 2. 当前批次进度

* READY 输入 Ktype：81 / 100
* READY 映射：91
* PENDING／尚未闭合输入 Ktype：19
* 已引用并闭合尺寸组：66
* 本轮新增 READY 输入 Ktype：17
* 本轮首次创建尺寸组：18
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124994	124994	Wagon	5 Series V	E61	5	EU-BMW-5-E61-WAGON-01	HIGH	E61 Touring物理外廓。	READY
125212	125212	Coupe	Corolla VI	AE92	2	EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	MEDIUM	生产期与功率对应AE92自然吸气双门Coupe；输入驱动字段与该车身资料不一致。	READY
125303	125303	Wagon	XM I	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH	Y3 Break物理外廓。	READY
125427_prefl	125427	Coupe	3000GT I	Z16A	3	EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125427_facelift	125427	Coupe	3000GT I	Z16A	3	EU-MITSUBISHI-3000GT-I-COUPE-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125430	125430	Coupe	3000GT I	Z15A	3	EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	MEDIUM	前驱自然吸气早期车身外廓。	READY
125440	125440	Sedan	Galant VIII		4	EU-MITSUBISHI-GALANT-VIII-SEDAN-3.0-01	MEDIUM	3.0升前驱四门车身；输入功率与直接规格页标注存在小幅差异。	READY
125446	125446	Coupe	MR2 II	SW21	2	EU-TOYOTA-MR2-II-SW21-COUPE-01	HIGH	2.2升SW21双门车身外廓。	READY
125500	125500	Coupe	Corvette C3	C3	2	EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	HIGH	1975年C3 Coupe外廓。	READY
125504	125504	Coupe	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-COUPE-BASE-1990-01	HIGH	1990年普通版C4 Coupe外廓。	READY
125505	125505	Coupe	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-ZR1-COUPE-1990-01	HIGH	ZR-1宽体外廓。	READY
125527	125527	Sedan	Caprice II		4	EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	HIGH	1975年四门Sedan外廓。	READY
125554	125554	Sedan	Malibu III		4	EU-CHEVROLET-MALIBU-III-SEDAN-PHASE-I-01	HIGH	第三代前期四门Sedan外廓。	READY
125565_prefl	125565	Coupe	Malibu III		2	EU-CHEVROLET-MALIBU-III-COUPE-PHASE-I-01	HIGH	同一Ktype跨越外廓尺寸变化，拆分前期Coupe分支。	READY
125565_facelift	125565	Coupe	Malibu III		2	EU-CHEVROLET-MALIBU-III-COUPE-PHASE-II-01	HIGH	同一Ktype跨越外廓尺寸变化，拆分后期Coupe分支。	READY
125609	125609	Wagon	Thema I	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH	Thema Station Wagon物理外廓。	READY
125793	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	HIGH	第二代前期三门Hatchback外廓。	READY
125799	125799	Hatchback	Gemini II	JT190	3	EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	HIGH	GTI 16V改款三门Hatchback外廓。	READY
125804	125804	Coupe	Piazza I	JR120	3	EU-ISUZU-PIAZZA-I-JR120-COUPE-01	HIGH	JR120三门Coupe外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-E61-WAGON-01	4843	1846	1491	Automobile-Catalog BMW 525i Touring	https://www.automobile-catalog.com/car/2007/280055/bmw_525i_touring.html
EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	4245	1665	1300	Toyota 75 Years Corolla Levin AE92 vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003784/index.html
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1464	Automobile-Catalog Citroën XM Break V6	https://www.automobile-catalog.com/car/1991/541625/citroen_xm_break_v6.html
EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	4555	1840	1285	Automobile-Catalog Mitsubishi GTO	https://www.automobile-catalog.com/car/1991/1966805/mitsubishi_gto.html
EU-MITSUBISHI-3000GT-I-COUPE-FACELIFT-01	4570	1840	1285	Automobile-Catalog Mitsubishi 3000 GT	https://www.automobile-catalog.com/car/1994/1967795/mitsubishi_3000_gt.html
EU-MITSUBISHI-GALANT-VIII-SEDAN-3.0-01	4770	1740	1415	Auto-Data Mitsubishi Galant VIII 3.0 GTZ	https://www.auto-data.net/en/mitsubishi-galant-viii-3.0-i-v6-24v-gtz-197hp-15364
EU-TOYOTA-MR2-II-SW21-COUPE-01	4171	1699	1240	Edmunds 1992 Toyota MR2 specifications	https://www.edmunds.com/toyota/mr2/1992/st-11626/features-specs/
EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	4704	1753	1222	Corvette Action Center 1975 specifications	https://www.corvetteactioncenter.com/specs/c3/1975/75specs.html
EU-CHEVROLET-CORVETTE-C4-COUPE-BASE-1990-01	4483	1803	1186	Automobile-Catalog 1990 Chevrolet Corvette	https://www.automobile-catalog.com/car/1990/463625/chevrolet_corvette.html
EU-CHEVROLET-CORVETTE-C4-ZR1-COUPE-1990-01	4506	1880	1186	Automobile-Catalog 1990 Corvette ZR-1; Edmunds 1990 Corvette ZR1 specifications	https://www.automobile-catalog.com/make/chevrolet_usa/corvette_c4/corvette_c4_coupe_zr-1/1990.html;https://www.edmunds.com/chevrolet/corvette/1990/zr1/features-specs/
EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	5659	2019	1384	Automobile-Catalog 1975 Chevrolet Caprice Sedan	https://www.automobile-catalog.com/car/1975/117695/chevrolet_caprice_4-door_sedan_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-MALIBU-III-SEDAN-PHASE-I-01	4895	1816	1377	Automobile-Catalog 1979 Chevrolet Malibu Sedan 5.0	https://www.automobile-catalog.com/car/1979/202010/chevrolet_malibu_sedan_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-I-01	4895	1816	1354	Automobile-Catalog 1979 Chevrolet Malibu Classic Sport Coupe 5.0	https://www.automobile-catalog.com/car/1979/201785/chevrolet_malibu_classic_sport_coupe_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-II-01	4895	1836	1415	Automobile-Catalog 1981 Chevrolet Malibu Classic Sport Coupe 5.0	https://www.automobile-catalog.com/car/1981/203330/chevrolet_malibu_classic_sport_coupe_5_0l_v-8_automatic.html
EU-LANCIA-THEMA-834-WAGON-01	4590	1755	1440	Automobile-Catalog Lancia Thema Station Wagon i.e. Turbo	https://www.automobile-catalog.com/car/1987/31355/lancia_thema_station_wagon_i_e__turbo.html
EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	3960	1600	1380	Automobile-Catalog 1985 Isuzu Gemini 1.5 Hatchback	https://www.automobile-catalog.com/car/1985/1258265/isuzu_gemini_1_5_hatchback.html
EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	4010	1615	1365	Automobile-Catalog 1988 Isuzu Gemini GTI 16V Hatchback	https://www.automobile-catalog.com/car/1988/1259030/isuzu_gemini_gti_16v_hatchback.html
EU-ISUZU-PIAZZA-I-JR120-COUPE-01	4310	1655	1300	Automobile-Catalog 1981 Isuzu Piazza	https://www.automobile-catalog.com/car/1981/58640/isuzu_piazza.html
```

## 5. 下一步优先处理

1. 集中拆分 Peugeot Expert、Citroën Jumpy III、Fiat Scudo 和 VW Crafter 的长度、轴距、车顶与 Bus／Chassis Cab 外廓。
2. 闭合 Renault Clio III Kasten 两条 Ktype 和 Volkswagen Polo Sedan。
3. 处理 Chevrolet Silverado 2500 的 CAB、货斗及驱动分支。
4. 最后闭合 Microcar F8、Mitsubishi L200 与 Ford Escort II。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/280055/bmw_525i_touring.html?utm_source=chatgpt.com "2007 BMW 525i Touring Specs Review (160 kW / 218 PS / 215 hp) (since mid-year 2007 for Europe )"
[2]: https://www.edmunds.com/toyota/mr2/1992/st-11626/features-specs/?utm_source=chatgpt.com "Used 1992 Toyota MR2 Base Specs & Features | Edmunds"
[3]: https://www.automobile-catalog.com/car/1987/31355/lancia_thema_station_wagon_i_e__turbo.html?utm_source=chatgpt.com "1987 Lancia Thema Station Wagon i.e. Turbo Specs Review (121.5 kW / 165 PS / 163 hp) (for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* Renault Clio III 三门商用版按 2009 年改款拆分：改款前为 `3986×1719×1495`，改款后为 `4032×1720×1497`；两条 Ktype 均覆盖前后期。([汽车数据网][1])
* Chevrolet Silverado 2500HD 8.1 4WD 按 Regular Cab、Extended Cab、Crew Cab及长短货斗拆为五个物理分支，全部直接引用已有缓存尺寸组，本轮不重复输出尺寸来源。
* Mitsubishi L200 178 HP 对应第四代改款 Double Cab，闭合为 `5185×1750×1775`。([汽车数据网][2])
* Ford Escort Mk II 1.6 Sedan 覆盖两门、四门车身，两者外廓三维相同，建立两个映射并共用一个尺寸组。([汽车目录][3])
* 两条 Microcar F8 Ktype 命中相同 F8C 三门外廓。([microcar.drive.place][4])

## 2. 当前批次进度

* READY 输入 Ktype：88 / 100
* READY 映射：105
* PENDING／尚未闭合输入 Ktype：12
* 已引用并闭合尺寸组：76
* 本轮新增 READY 输入 Ktype：7
* 本轮首次创建尺寸组：5
* 本轮新增复用历史尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124975_prefl	124975	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	HIGH	三门商用版改款前物理外廓。	READY
124975_facelift	124975	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	HIGH	同一Ktype跨越2009年外廓变化改款。	READY
124977_prefl	124977	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	HIGH	三门商用版改款前物理外廓。	READY
124977_facelift	124977	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	HIGH	同一Ktype跨越2009年外廓变化改款。	READY
125438_regularcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	MEDIUM	Regular Cab Long Bed 4WD物理分支。	READY
125438_extendedcab_shortbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	MEDIUM	Extended Cab Short Bed 4WD物理分支。	READY
125438_extendedcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	MEDIUM	Extended Cab Long Bed 4WD物理分支。	READY
125438_crewcab_shortbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	MEDIUM	Crew Cab Short Bed 4WD物理分支。	READY
125438_crewcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	MEDIUM	Crew Cab Long Bed 4WD物理分支。	READY
125693	125693	Hatchback	F8C	F8C	3	EU-MICROCAR-F8C-HATCHBACK-01	MEDIUM	F8C三门微型车外廓。	READY
125694	125694	Hatchback	F8C	F8C	3	EU-MICROCAR-F8C-HATCHBACK-01	MEDIUM	F8C三门微型车外廓。	READY
125748	125748	Pickup	L200 IV facelift		4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLECAB-FACELIFT-01	HIGH	178 HP Double Cab改款车身。	READY
125814_2dr	125814	Sedan	Escort II		2	EU-FORD-ESCORT-II-SEDAN-1.6-01	MEDIUM	两门Sedan物理分支。	READY
125814_4dr	125814	Sedan	Escort II		4	EU-FORD-ESCORT-II-SEDAN-1.6-01	MEDIUM	四门Sedan外廓三维与两门分支一致。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 1.2 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-75hp-25673
EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 3-door 1.2 16V	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-1.2-16v-75hp-10402
EU-MICROCAR-F8C-HATCHBACK-01	3003	1505	1465	Drive.Place Microcar F8C specifications	https://microcar.drive.place/f8c/i/group_coupe/410997
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLECAB-FACELIFT-01	5185	1750	1775	Auto-Data Mitsubishi L200 IV Double Cab facelift 2.5 HP DI-D	https://www.auto-data.net/en/mitsubishi-l200-iv-double-cab-facelift-2010-2.5-hp-di-d-178hp-18119
EU-FORD-ESCORT-II-SEDAN-1.6-01	3978	1596	1398	Automobile-Catalog 1979 Ford Escort 1600 L	https://www.automobile-catalog.com/car/1979/38075/ford_escort_1600_l.html
```

## 5. 下一步优先处理

1. 闭合 Peugeot Expert III 与 Citroën Jumpy III 的 Platform/Chassis Cab 外廓，并批量关联 6 条 Ktype。
2. 拆分 Volkswagen Crafter II Bus 的长度和车顶组合，并优先复用三维完全一致的既有 Crafter 尺寸组。
3. 闭合 Citroën Jumpy III Bus 和 Fiat Scudo I Chassis Cab。
4. 最后解决 Volkswagen Polo Sedan 生产期及代际边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-75hp-25673?utm_source=chatgpt.com "Renault Clio III (Phase I) 3-door 1.2 16V (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-l200-iv-double-cab-facelift-2010-2.5-hp-di-d-178hp-18119 "Mitsubishi L200 IV Double Cab (facelift 2010) 2.5 HP DI-D (178 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1979/38075/ford_escort_1600_l.html?utm_source=chatgpt.com "1979 Ford Escort 1600 L Specs Review (63.5 kW / 86 PS / 85 hp) (since mid-year 1979 for Europe U.K.)"
[4]: https://microcar.drive.place/f8c/i/group_coupe/410997?utm_source=chatgpt.com "Microcar F8C I 0.5 CVT 6 hp Coupe — specifications"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* Citroën Jumpy III Bus 的 BlueHDi 180 同时覆盖 XS、M、XL 三种车长，已拆分为三个物理外廓；官方资料明确宽度为不含后视镜口径。
* Peugeot Expert III 与 Citroën Jumpy III 的 Platform Cab 均为同一 K0 平台中轴距底盘车，六条 Ktype 共用一个尺寸组。
* 三条 Volkswagen Crafter II Bus Ktype 均按 L3H2、L3H3、L4H3、L4H4、L5H3、L5H4 六种既有物理外廓展开，直接引用已有 Crafter 尺寸组，不重复输出尺寸来源。
* Volkswagen Polo 1.9 TDI Sedan 已闭合为 Polo IV `9N2` 四门三厢外廓。Volkswagen 官方资料确认该代 74 kW 1.9 TDI 的生产边界。([volkswagen-newsroom.com][1])
* Fiat Scudo I Platform/Chassis 的现有资料能确认 `220` 底盘及动力版本，但尚未取得能够明确对应第一代底盘车完整三维且确认宽度口径的可靠来源，暂不猜测建组。

## 2. 当前批次进度

* READY 输入 Ktype：99 / 100
* PENDING 输入 Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已引用并闭合尺寸组：87
* 本轮首次创建尺寸组：5
* 本轮新增复用既有尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124959_xs	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-XS-01	HIGH	XS乘用Bus物理分支。	READY
124959_m	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-M-01	HIGH	M乘用Bus物理分支。	READY
124959_xl	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-XL-01	HIGH	XL乘用Bus物理分支。	READY
125092_l3h2	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125092_l3h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125092_l4h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125092_l4h4	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125092_l5h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125092_l5h4	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125093_l3h2	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125093_l3h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125093_l4h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125093_l4h4	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125093_l5h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125093_l5h4	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125094_l3h2	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125094_l3h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125094_l4h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125094_l4h4	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125094_l5h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125094_l5h4	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125133	125133	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125134	125134	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125135	125135	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125208	125208	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125213	125213	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125214	125214	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125292	125292	Sedan	Polo IV	9N2	4	EU-VW-POLO-IV-9N2-SEDAN-01	MEDIUM	输入结束期晚于欧洲官方生产资料，按9N2四门Sedan外廓。	READY
125474	125474	Pickup	Scudo I	220	2		LOW	候选第一代220 Platform/Chassis；完整三维及不含后视镜宽度尚未闭合。	PENDING: 第一代Scudo底盘车三维和宽度口径未闭合
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-III-BUS-XS-01	4609	1920	1905	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-CITROEN-JUMPY-III-BUS-M-01	4959	1920	1890	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-CITROEN-JUMPY-III-BUS-XL-01	5309	1920	1890	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	4814	1920	1881	Citroën Jumpy official technical sheet;Peugeot Expert official price list	https://asset.moto.it/pricelist/auto/e6e36c081fd635a25a70c043553fb310/scheda-tecnica-2016.pdf;https://professional.peugeot.it/content/dam/peugeot/italy/b2c/our-range/expert/listino/Listino_eExpert_Expert_Giugno.pdf
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465	Volkswagen Newsroom Polo IV vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
```

## 5. 下一步优先处理

1. 仅处理 `125474` Fiat Scudo I `220` Platform/Chassis：查找能够直接支持完整长宽高并明确不含后视镜宽度的第一代技术资料。
2. 该记录闭合后立即进行一次机械检查，并输出两张最终完整 TSV、两个指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152?utm_source=chatgpt.com "Vehicle data Polo IV profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 最后一条 `125474` 已闭合：确认为 Fiat Scudo I、`220` 底盘代码、双门 Platform/Chassis，尺寸组为 `4430 × 1810 × 1927 mm`。瑞士 ASTRA 型式批准资料明确标注车身形式为底盘车，并给出三维及两门信息。
* 当前批次已消除全部 PENDING。
* 已完成机械收尾检查：两张表表头正确，134 个映射 `id` 唯一，88 个 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，无孤立尺寸组，三维与来源字段均非空。

## 当前批次进度

* 输入 Ktype：100 / 100 READY
* READY 映射：134
* PENDING 映射：0
* DIMENSION_GROUP：88
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124952	124952	SUV	5008 II		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	MEDIUM	输入Großraumlimousine，按第二代5008五门SUV外廓归类。	READY
124953	124953	SUV	5008 II		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	MEDIUM	输入Großraumlimousine，按第二代5008五门SUV外廓归类。	READY
124959_xs	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-XS-01	HIGH	XS乘用Bus物理分支。	READY
124959_m	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-M-01	HIGH	M乘用Bus物理分支。	READY
124959_xl	124959	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-BUS-XL-01	HIGH	XL乘用Bus物理分支。	READY
124975_prefl	124975	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	HIGH	三门商用版改款前物理外廓。	READY
124975_facelift	124975	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	HIGH	同一Ktype跨越2009年外廓变化改款。	READY
124977_prefl	124977	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	HIGH	三门商用版改款前物理外廓。	READY
124977_facelift	124977	Van	Clio III		3	EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	HIGH	同一Ktype跨越2009年外廓变化改款。	READY
124994	124994	Wagon	5 Series V	E61	5	EU-BMW-5-E61-WAGON-01	HIGH	E61 Touring物理外廓。	READY
124998	124998	Coupe	GTC4Lusso			EU-FERRARI-GTC4LUSSO-T-COUPE-01	HIGH	GTC4Lusso T三门掀背式Coupe外廓。	READY
125041	125041	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11改款旅行车物理外廓。	READY
125056	125056	Convertible	MX-5 IV	ND	2	EU-MAZDA-MX-5-ND-RF-01	HIGH	RF电动硬顶车身外廓。	READY
125059	125059	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11改款旅行车物理外廓。	READY
125091	125091	Wagon	5 Series VI	F11	5	EU-BMW-5-F11-WAGON-FACELIFT-01	HIGH	F11前期与现有尺寸组外廓三维一致。	READY
125092_l3h2	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125092_l3h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125092_l4h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125092_l4h4	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125092_l5h3	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125092_l5h4	125092	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125093_l3h2	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125093_l3h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125093_l4h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125093_l4h4	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125093_l5h3	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125093_l5h4	125093	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125094_l3h2	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2 Bus物理分支。	READY
125094_l3h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3 Bus物理分支。	READY
125094_l4h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3 Bus物理分支。	READY
125094_l4h4	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4 Bus物理分支。	READY
125094_l5h3	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3 Bus物理分支。	READY
125094_l5h4	125094	MPV	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4 Bus物理分支。	READY
125098	125098	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	F10改款前三厢外廓。	READY
125102	125102	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	F10改款前三厢外廓。	READY
125105	125105	Sedan	5 Series VI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	F10改款三厢物理外廓。	READY
125126	125126	Hatchback	Rapide S		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S五门掀背外廓。	READY
125128	125128	Hatchback	5 Series VI	F07	5	EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	HIGH	F07 Gran Turismo五门掀背物理外廓。	READY
125133	125133	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125134	125134	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125135	125135	Pickup	Expert III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125153	125153	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH	F5双门Coupe物理外廓。	READY
125154	125154	Hatchback	A5 II (F5)	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback五门掀背物理外廓。	READY
125157	125157	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
125163	125163	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	S213改款前旅行车外廓。	READY
125164_prefl	125164	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125164_facelift	125164	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125165_prefl	125165	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125165_facelift	125165	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125169	125169	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63-SEDAN-PREFL-01	HIGH	W213 AMG E 63改款前宽体三厢外廓。	READY
125170_prefl	125170	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125170_facelift	125170	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125171	125171	Wagon	3 Series VI	F31	5	EU-BMW-3-F31-WAGON-PREFL-RWD-01	HIGH	F31改款前后驱旅行车外廓。	READY
125172	125172	Wagon	3 Series VI	F31	5	EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	HIGH	xDrive车身高度与后驱版本不同。	READY
125183	125183	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
125184	125184	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-01	HIGH	SQ5专属外廓高度。	READY
125199	125199	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
125208	125208	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125212	125212	Coupe	Corolla VI	AE92	2	EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	MEDIUM	生产期与功率对应AE92自然吸气双门Coupe；输入驱动字段与该车身资料不一致。	READY
125213	125213	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125214	125214	Pickup	Jumpy III	K0	2	EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	HIGH	中轴距Platform Cab物理外廓。	READY
125220	125220	SUV	ix35 I facelift		5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	MEDIUM	ix35改款后五门SUV外廓。	READY
125249	125249	Sedan	Jetta VI facelift		4	EU-VW-JETTA-VI-SEDAN-FACELIFT-01	HIGH	输入代际标签与生产期不一致，按Jetta VI改款车型归类。	READY
125265	125265	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-01	MEDIUM	CR-V第五代五门SUV外廓。	READY
125291	125291	Convertible	500	312	3	EU-FIAT-500-312-CABRIOLET-PREFL-01	MEDIUM	500 C改款前软顶车身外廓。	READY
125292	125292	Sedan	Polo IV	9N2	4	EU-VW-POLO-IV-9N2-SEDAN-01	MEDIUM	输入结束期晚于欧洲官方生产资料，按9N2四门Sedan外廓。	READY
125303	125303	Wagon	XM I	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH	Y3 Break物理外廓。	READY
125321	125321	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	改款前后外廓三维一致，复用稳定尺寸组。	READY
125328	125328	Pickup	Dyna 100	LY100	2	EU-TOYOTA-DYNA-100-LY100-PICKUP-01	HIGH	LY100单排底盘车外廓。	READY
125336	125336	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125337	125337	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125338	125338	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125339_prefl	125339	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125339_facelift	125339	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125340	125340	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125341	125341	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31改款前旅行车物理外廓。	READY
125343	125343	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	G30改款前三厢物理外廓。	READY
125345_prefl	125345	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125345_facelift	125345	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125347	125347	Wagon	MINI III	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman外廓。	READY
125348	125348	Wagon	MINI III	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman外廓。	READY
125349_prefl	125349	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125349_facelift	125349	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125350_prefl	125350	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125350_facelift	125350	SUV	X-Trail III	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125351	125351	Coupe	TT III	8S	3	EU-AUDI-TT-8S-COUPE-01	HIGH	8S三门Coupe外廓。	READY
125352	125352	Convertible	TT III	8S	2	EU-AUDI-TT-8S-ROADSTER-01	HIGH	8S双门Roadster外廓。	READY
125427_prefl	125427	Coupe	3000GT I	Z16A	3	EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款前分支。	READY
125427_facelift	125427	Coupe	3000GT I	Z16A	3	EU-MITSUBISHI-3000GT-I-COUPE-FACELIFT-01	HIGH	同一Ktype跨越外廓尺寸变化改款，拆分改款后分支。	READY
125430	125430	Coupe	3000GT I	Z15A	3	EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	MEDIUM	前驱自然吸气早期车身外廓。	READY
125438_regularcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	MEDIUM	Regular Cab Long Bed 4WD物理分支。	READY
125438_extendedcab_shortbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	MEDIUM	Extended Cab Short Bed 4WD物理分支。	READY
125438_extendedcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	MEDIUM	Extended Cab Long Bed 4WD物理分支。	READY
125438_crewcab_shortbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	MEDIUM	Crew Cab Short Bed 4WD物理分支。	READY
125438_crewcab_longbed	125438	Pickup	Silverado 2500HD	GMT800		EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	MEDIUM	Crew Cab Long Bed 4WD物理分支。	READY
125440	125440	Sedan	Galant VIII		4	EU-MITSUBISHI-GALANT-VIII-SEDAN-3.0-01	MEDIUM	3.0升前驱四门车身；输入功率与直接规格页标注存在小幅差异。	READY
125446	125446	Coupe	MR2 II	SW21	2	EU-TOYOTA-MR2-II-SW21-COUPE-01	HIGH	2.2升SW21双门车身外廓。	READY
125474	125474	Pickup	Scudo I	220	2	EU-FIAT-SCUDO-I-220-PLATFORM-CHASSIS-01	HIGH	第一代220短轴Platform/Chassis双门外廓。	READY
125493	125493	SUV	Tahoe IV	K2UC	5	EU-CHEVROLET-TAHOE-IV-K2UC-SUV-01	MEDIUM	K2UC五门SUV外廓。	READY
125500	125500	Coupe	Corvette C3	C3	2	EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	HIGH	1975年C3 Coupe外廓。	READY
125504	125504	Coupe	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-COUPE-BASE-1990-01	HIGH	1990年普通版C4 Coupe外廓。	READY
125505	125505	Coupe	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-ZR1-COUPE-1990-01	HIGH	ZR-1宽体外廓。	READY
125527	125527	Sedan	Caprice II		4	EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	HIGH	1975年四门Sedan外廓。	READY
125528	125528	Sedan	Lancer Evolution IV	CN9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IV-CN9A-SEDAN-01	HIGH		READY
125554	125554	Sedan	Malibu III		4	EU-CHEVROLET-MALIBU-III-SEDAN-PHASE-I-01	HIGH	第三代前期四门Sedan外廓。	READY
125565_prefl	125565	Coupe	Malibu III		2	EU-CHEVROLET-MALIBU-III-COUPE-PHASE-I-01	HIGH	同一Ktype跨越外廓尺寸变化，拆分前期Coupe分支。	READY
125565_facelift	125565	Coupe	Malibu III		2	EU-CHEVROLET-MALIBU-III-COUPE-PHASE-II-01	HIGH	同一Ktype跨越外廓尺寸变化，拆分后期Coupe分支。	READY
125584	125584	Sedan	Lancer Evolution VII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VII-CT9A-SEDAN-01	HIGH		READY
125588_prefl	125588	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-PREFL-01	HIGH	同一Ktype覆盖Sorento III改款前外廓。	READY
125588_facelift	125588	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	HIGH	同一Ktype覆盖Sorento III改款后外廓。	READY
125591	125591	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-QL-SUV-01	HIGH		READY
125592	125592	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII。	READY
125593	125593	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-300。	READY
125594	125594	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-300。	READY
125596	125596	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-330。	READY
125600	125600	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-340。	READY
125602	125602	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	HIGH	按VariantName识别为Evolution VIII FQ-400。	READY
125608	125608	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-CT9A-FQ360-SEDAN-01	HIGH	按VariantName识别为Evolution IX FQ-360。	READY
125609	125609	Wagon	Thema I	834	5	EU-LANCIA-THEMA-834-WAGON-01	HIGH	Thema Station Wagon物理外廓。	READY
125693	125693	Hatchback	F8C	F8C	3	EU-MICROCAR-F8C-HATCHBACK-01	MEDIUM	F8C三门微型车外廓。	READY
125694	125694	Hatchback	F8C	F8C	3	EU-MICROCAR-F8C-HATCHBACK-01	MEDIUM	F8C三门微型车外廓。	READY
125703	125703	Hatchback	Leon III	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Leon 5F改款五门掀背外廓。	READY
125718	125718	Coupe	Leon III	5F	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	HIGH	Leon SC改款三门外廓。	READY
125719	125719	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH	Leon ST改款旅行车外廓。	READY
125720	125720	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH	Leon ST改款旅行车外廓。	READY
125748	125748	Pickup	L200 IV facelift		4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLECAB-FACELIFT-01	HIGH	178 HP Double Cab改款车身。	READY
125793	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	HIGH	第二代前期三门Hatchback外廓。	READY
125799	125799	Hatchback	Gemini II	JT190	3	EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	HIGH	GTI 16V改款三门Hatchback外廓。	READY
125804	125804	Coupe	Piazza I	JR120	3	EU-ISUZU-PIAZZA-I-JR120-COUPE-01	HIGH	JR120三门Coupe外廓。	READY
125811	125811	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-01	HIGH		READY
125812	125812	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-01	MEDIUM	输入驱动信息与常见3.0 V6配置不一致；不影响五门车身外廓边界。	READY
125814_2dr	125814	Sedan	Escort II		2	EU-FORD-ESCORT-II-SEDAN-1.6-01	MEDIUM	两门Sedan物理分支。	READY
125814_4dr	125814	Sedan	Escort II		4	EU-FORD-ESCORT-II-SEDAN-1.6-01	MEDIUM	四门Sedan外廓三维与两门分支一致。	READY
125815	125815	Coupe	F-Type facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH	400 Sport改款双门Coupe外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1001-1100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646	Auto-Data Peugeot 5008 II Phase I 2.0 BlueHDi 150	https://www.auto-data.net/en/peugeot-5008-ii-phase-i-2017-2.0-bluehdi-150hp-27389
EU-CITROEN-JUMPY-III-BUS-XS-01	4609	1920	1905	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-CITROEN-JUMPY-III-BUS-M-01	4959	1920	1890	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-CITROEN-JUMPY-III-BUS-XL-01	5309	1920	1890	Citroën Jumpy Atlante official technical sheet July 2016	https://asset.moto.it/pricelist/auto/73f825b68452f43eb322d418ed4e8094/-scheda-tecnica-2016.pdf
EU-RENAULT-CLIO-III-VAN-3D-PREFL-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 1.2 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-75hp-25673
EU-RENAULT-CLIO-III-VAN-3D-FACELIFT-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 3-door 1.2 16V	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-1.2-16v-75hp-10402
EU-BMW-5-E61-WAGON-01	4843	1846	1491	Automobile-Catalog BMW 525i Touring	https://www.automobile-catalog.com/car/2007/280055/bmw_525i_touring.html
EU-FERRARI-GTC4LUSSO-T-COUPE-01	4922	1980	1383	Ferrari GTC4Lusso T official reveal press release	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/cs_ferrari_gtc4lusso_t_reveal_gbr.pdf
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-MAZDA-MX-5-ND-RF-01	3915	1735	1235	Mazda Motor Europe MX-5 official press material	https://at.mazda-press.com/api/assets/download/b8bde554-f284-41d2-bc9c-b544e1d9abe7_Default?isDownload=false
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Commercial Vehicles Crafter Van official tariff and technical data	https://www.volkswagen-utilitaires.fr/idhub/content/dam/onehub_nfz/importers/fr/documentation/2024/Tarif-Crafter-Van-MY2025.pdf
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	BMW Group PressClub ActiveHybrid 5 specifications	https://www.press.bmwgroup.com/global/article/attachment/T0121796EN/190364
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	5020	1929	1360	Auto-Data Aston Martin Rapide S	https://www.auto-data.net/en/aston-martin-rapide-s-generation-4935
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559	BMW Group PressClub 2013 BMW 5 Series press kit	https://www.press.bmwgroup.com/global/article/attachment/T0141378EN/264133
EU-PSA-EXPERT-JUMPY-III-K0-PLATFORM-CAB-01	4814	1920	1881	Citroën Jumpy official technical sheet;Peugeot Expert official price list	https://asset.moto.it/pricelist/auto/e6e36c081fd635a25a70c043553fb310/scheda-tecnica-2016.pdf;https://professional.peugeot.it/content/dam/peugeot/italy/b2c/our-range/expert/listino/Listino_eExpert_Expert_Giugno.pdf
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Audi A5 Coupe official technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1080/file_en/7408d27a32c7f357b5a8b1993d75e0d804b6c3c4/eTD-Audi-A5-Coupe-35-TFSI-110kW-MHEV_240502.pdf?1714662679=
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi A5 Sportback official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a5-sportback-1393/download
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Auto-Data Alfa Romeo Stelvio 2.0 280 AWD	https://www.auto-data.net/en/alfa-romeo-stelvio-949-2.0-280hp-awd-automatic-28578
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E 220d 4MATIC S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-220d-194hp-4matic-9g-tronic-30787
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Auto-Data Mercedes-Benz E 220d S213 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-194hp-9g-tronic-40982
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63-SEDAN-PREFL-01	4988	1907	1468	Auto-Data Mercedes-AMG E 63 W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-v8-571hp-4matic-mct-29710
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-PREFL-01	4988	1907	1463	Auto-Data Mercedes-AMG E 63 S W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-s-v8-612hp-4matic-mct-29924
EU-MERCEDES-BENZ-E-CLASS-W213-AMG-E63S-SEDAN-FACELIFT-01	4940	1852	1460	Auto-Data Mercedes-AMG E 63 S W213 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-amg-e-63-s-612hp-4matic-amg-speedshift-mct-40870
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429	BMW Group PressClub BMW 320i Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0132112EN/207745/Specifications_BMW_3_Series_Touring_320i_11_2012.pdf
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434	BMW Group PressClub BMW 320i xDrive Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208685/Specifications_BMW_3_Series_Touring_320i_xDrive_03_2013.pdf
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659	Audi Q5 2017 dimension drawing	https://dt16c8g6jis9k.cloudfront.net/audi/q5/2017/dimensions
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635	Audi UK SQ5 TFSI technical data	https://press.audi.co.uk/assets/documents/original/21087-AudiUK00017568AudiSQ5TFSIQ520TDI.pdf
EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	4245	1665	1300	Toyota 75 Years Corolla Levin AE92 vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003784/index.html
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655	Auto-Data Hyundai ix35 facelift 2.0 GDI 4x4	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-2.0-gdi-166hp-4x4-automatic-18560
EU-VW-JETTA-VI-SEDAN-FACELIFT-01	4659	1778	1482	Autodata1 Volkswagen Jetta VI facelift 1.2 TSI	https://www.autodata1.com/en/car/volkswagen/jetta/jetta-vi-facelift-2014-12-tsi-105-hp
EU-HONDA-CR-V-V-SUV-01	4587	1854	1689	Auto-Data Honda CR-V V 1.5 AWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-190hp-awd-automatic-33228
EU-FIAT-500-312-CABRIOLET-PREFL-01	3546	1627	1488	Auto-Data Fiat 500 C 0.9 TwinAir	https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465	Volkswagen Newsroom Polo IV vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1464	Automobile-Catalog Citroën XM Break V6	https://www.automobile-catalog.com/car/1991/541625/citroen_xm_break_v6.html
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448	Auto-Data Renault Clio IV Phase II	https://www.auto-data.net/en/renault-clio-iv-phase-ii-2016-0.9-tce-75hp-35441
EU-TOYOTA-DYNA-100-LY100-PICKUP-01	4415	1695	1830	Carlist.my Toyota Dyna LY100R specifications	https://www.carlist.my/used-cars/1997-toyota-dyna-2-5-lorry/8290360
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498	BMW Group PressClub 2017 BMW 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0267496EN/384763
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub BMW 530e Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0317776EN/461553
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub BMW 5 Series Sedan specifications valid from September 2018	https://www.press.bmwgroup.com/global/article/detail/T0286565EN/specifications-of-the-bmw-5-series-sedan-valid-from-09/2018
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group PressClub BMW 5 Series Sedan specifications valid from May 2020	https://www.press.bmwgroup.com/global/article/detail/T0314291EN/specifications-of-the-bmw-5-series-sedan-valid-from-05/2020
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441	BMW Group PressClub MINI Clubman specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252423EN/353092
EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	4640	1820	1715	Auto-Data Nissan X-Trail III T32 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-iii-t32-2.0-dci-177hp-xtronic-29978
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Nissan X-Trail 2017 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/X-Trail%20Brochure%202017.10.pdf
EU-AUDI-TT-8S-COUPE-01	4177	1832	1353	Auto-Data Audi TT Coupe 8S 2.0 TDI quattro	https://www.auto-data.net/se/audi-tt-coupe-8s-2.0-tdi-184hp-quattro-s-tronic-31768
EU-AUDI-TT-8S-ROADSTER-01	4177	1832	1355	Auto-Data Audi TT Roadster 8S 2.0 TDI quattro	https://www.auto-data.net/en/audi-tt-roadster-8s-2.0-tdi-184hp-quattro-s-tronic-30307
EU-MITSUBISHI-3000GT-I-COUPE-PREFL-01	4555	1840	1285	Automobile-Catalog Mitsubishi GTO	https://www.automobile-catalog.com/car/1991/1966805/mitsubishi_gto.html
EU-MITSUBISHI-3000GT-I-COUPE-FACELIFT-01	4570	1840	1285	Automobile-Catalog Mitsubishi 3000 GT	https://www.automobile-catalog.com/car/1994/1967795/mitsubishi_3000_gt.html
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	5641	2024	2024	Chevrolet 2005 Silverado 2500HD official vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Silverado-2500HD.pdf
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	5784	2024	1935	Chevrolet 2005 Silverado 2500HD official vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Silverado-2500HD.pdf
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	6264	2024	1935	Chevrolet 2005 Silverado 2500HD official vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Silverado-2500HD.pdf
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	6025	2024	1935	Chevrolet 2005 Silverado 2500HD official vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Silverado-2500HD.pdf
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	6505	2024	1935	Chevrolet 2005 Silverado 2500HD official vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Silverado-2500HD.pdf
EU-MITSUBISHI-GALANT-VIII-SEDAN-3.0-01	4770	1740	1415	Auto-Data Mitsubishi Galant VIII 3.0 GTZ	https://www.auto-data.net/en/mitsubishi-galant-viii-3.0-i-v6-24v-gtz-197hp-15364
EU-TOYOTA-MR2-II-SW21-COUPE-01	4171	1699	1240	Edmunds 1992 Toyota MR2 specifications	https://www.edmunds.com/toyota/mr2/1992/st-11626/features-specs/
EU-FIAT-SCUDO-I-220-PLATFORM-CHASSIS-01	4430	1810	1927	Swiss ASTRA type approval extract Fiat Scudo chassis 3FA107	https://typenscheinschweiz.ch/pdf/auto/3FA107
EU-CHEVROLET-TAHOE-IV-K2UC-SUV-01	5179	2045	1890	Auto-Data Chevrolet Tahoe 6.2 AWD	https://www.auto-data.net/en/chevrolet-tahoe-gmtk2uc-g-6.2-v8-420hp-awd-automatic-33466
EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	4704	1753	1222	Corvette Action Center 1975 specifications	https://www.corvetteactioncenter.com/specs/c3/1975/75specs.html
EU-CHEVROLET-CORVETTE-C4-COUPE-BASE-1990-01	4483	1803	1186	Automobile-Catalog 1990 Chevrolet Corvette	https://www.automobile-catalog.com/car/1990/463625/chevrolet_corvette.html
EU-CHEVROLET-CORVETTE-C4-ZR1-COUPE-1990-01	4506	1880	1186	Automobile-Catalog 1990 Corvette ZR-1;Edmunds 1990 Corvette ZR1 specifications	https://www.automobile-catalog.com/make/chevrolet_usa/corvette_c4/corvette_c4_coupe_zr-1/1990.html;https://www.edmunds.com/chevrolet/corvette/1990/zr1/features-specs/
EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	5659	2019	1384	Automobile-Catalog 1975 Chevrolet Caprice Sedan	https://www.automobile-catalog.com/car/1975/117695/chevrolet_caprice_4-door_sedan_350_v-8_turbo-fire_hydra-matic.html
EU-MITSUBISHI-LANCER-EVOLUTION-IV-CN9A-SEDAN-01	4330	1690	1415	Auto-Data Mitsubishi Lancer Evolution IV	https://www.auto-data.net/en/mitsubishi-lancer-evolution-iv-2.0-280hp-4wd-42185
EU-CHEVROLET-MALIBU-III-SEDAN-PHASE-I-01	4895	1816	1377	Automobile-Catalog 1979 Chevrolet Malibu Sedan 5.0	https://www.automobile-catalog.com/car/1979/202010/chevrolet_malibu_sedan_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-I-01	4895	1816	1354	Automobile-Catalog 1979 Chevrolet Malibu Classic Sport Coupe 5.0	https://www.automobile-catalog.com/car/1979/201785/chevrolet_malibu_classic_sport_coupe_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-II-01	4895	1836	1415	Automobile-Catalog 1981 Chevrolet Malibu Classic Sport Coupe 5.0	https://www.automobile-catalog.com/car/1981/203330/chevrolet_malibu_classic_sport_coupe_5_0l_v-8_automatic.html
EU-MITSUBISHI-LANCER-EVOLUTION-VII-CT9A-SEDAN-01	4455	1770	1450	Auto-Data Mitsubishi Lancer Evolution VII	https://www.auto-data.net/en/mitsubishi-lancer-evolution-vii-generation-3443
EU-KIA-SORENTO-III-UM-SUV-PREFL-01	4780	1890	1685	Auto-Data Kia Sorento III 2.2 CRDi	https://www.auto-data.net/en/kia-sorento-iii-2.2-crdi-200hp-23790
EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	4800	1890	1685	Auto-Data Kia Sorento III facelift 2.2 CRDi	https://www.auto-data.net/en/kia-sorento-iii-facelift-2018-2.2-crdi-200hp-automatic-32158
EU-KIA-SPORTAGE-IV-QL-SUV-01	4480	1855	1635	Auto-Data Kia Sportage IV 2.0 MPI	https://www.auto-data.net/en/kia-sportage-iv-2.0-mpi-155hp-sportmatic-54522
EU-MITSUBISHI-LANCER-EVOLUTION-VIII-CT9A-SEDAN-01	4490	1770	1450	Automobile-Catalog Mitsubishi Lancer Evolution VIII 2004 full range	https://www.automobile-catalog.com/make/mitsubishi/lancer_evolution_3/lancer_evolution_viii/2004.html
EU-MITSUBISHI-LANCER-EVOLUTION-IX-CT9A-FQ360-SEDAN-01	4490	1770	1450	Automobile-Catalog Mitsubishi Lancer Evo IX MR FQ-360	https://www.automobile-catalog.com/car/2007/1998110/mitsubishi_lancer_evo_ix_mr_fq-360.html
EU-LANCIA-THEMA-834-WAGON-01	4590	1755	1440	Automobile-Catalog Lancia Thema Station Wagon i.e. Turbo	https://www.automobile-catalog.com/car/1987/31355/lancia_thema_station_wagon_i_e__turbo.html
EU-MICROCAR-F8C-HATCHBACK-01	3003	1505	1465	Drive.Place Microcar F8C specifications	https://microcar.drive.place/f8c/i/group_coupe/410997
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	Auto-Data Seat Leon III facelift 1.8 TSI	https://www.auto-data.net/en/seat-leon-iii-facelift-2016-1.8-tsi-180hp-dsg-26904
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446	Auto-Data Seat Leon III SC facelift generation	https://www.auto-data.net/en/seat-leon-iii-sc-facelift-2016-generation-5214
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454	Auto-Data Seat Leon III ST facelift specifications	https://www.auto-data.net/en/seat-leon-model-1459
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLECAB-FACELIFT-01	5185	1750	1775	Auto-Data Mitsubishi L200 IV Double Cab facelift 2.5 HP DI-D	https://www.auto-data.net/en/mitsubishi-l200-iv-double-cab-facelift-2010-2.5-hp-di-d-178hp-18119
EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	3960	1600	1380	Automobile-Catalog 1985 Isuzu Gemini 1.5 Hatchback	https://www.automobile-catalog.com/car/1985/1258265/isuzu_gemini_1_5_hatchback.html
EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	4010	1615	1365	Automobile-Catalog 1988 Isuzu Gemini GTI 16V Hatchback	https://www.automobile-catalog.com/car/1988/1259030/isuzu_gemini_gti_16v_hatchback.html
EU-ISUZU-PIAZZA-I-JR120-COUPE-01	4310	1655	1300	Automobile-Catalog 1981 Isuzu Piazza	https://www.automobile-catalog.com/car/1981/58640/isuzu_piazza.html
EU-FORD-MAVERICK-II-SUV-01	4394	1781	1722	Auto-Data Ford Maverick II 2.0	https://www.auto-data.net/en/ford-maverick-ii-2.0-i-16v-124hp-7544
EU-FORD-ESCORT-II-SEDAN-1.6-01	3978	1596	1398	Automobile-Catalog 1979 Ford Escort 1600 L	https://www.automobile-catalog.com/car/1979/38075/ford_escort_1600_l.html
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311	Auto-Data Jaguar F-Type 400 Sport Coupe	https://www.auto-data.net/en/jaguar-f-type-coupe-facelift-2017-3.0-v6-400hp-automatic-27595
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1001-1100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1001-1100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1001-1100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1049 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（539 行）

