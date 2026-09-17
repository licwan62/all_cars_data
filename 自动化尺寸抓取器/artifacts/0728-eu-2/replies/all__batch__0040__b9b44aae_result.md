# 任务：all 第 3901-4000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0040__b9b44aae


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
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	5143	1954	1750
EU-CITROEN-NEMO-I-AA-VAN-01	3864	1716	1721
EU-CITROEN-NEMO-I-AJ-MPV-01	3959	1716	1721
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	4107	1777	1296
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK300-01	4107	1788	1296
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	4107	1788	1298
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	4532	1827	1298
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	4562	1820	1317
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628
EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	4440	1817	1427
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564
EU-PEUGEOT-BIPPER-I-AA-VAN-01	3864	1716	1721
EU-PEUGEOT-BIPPER-I-AJ-MPV-01	3959	1716	1721
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-3D-02	3986	1719	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-02	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	4299	1785	1423
EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	4299	1848	1435
EU-RENAULT-MEGANE-III-COUPE-PREFL-01	4299	1804	1435
EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	4295	1808	1471
EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	4295	1808	1491
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695
EU-SUZUKI-GRAND-VITARA-II-3D-PREFL-SUV-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	4798	1898	1743
EU-VOLVO-XC90-I-SUV-5D-01	4798	1898	1784

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Suzuki	Grand vitara ii	2.4 Allrad	Geländewagen geschlossen	Allrad	Benzin	122	166	Jan 2009	-	2024-03-01	31383
Chrysler	Grand voyager v	3.8	Großraumlimousine	Frontantrieb	Benzin	142	193	Oct 2007	-	2024-03-01	31384
Subaru	Tribeca	3.6	SUV	Allrad	Benzin	190	258	Sep 2007	-	2024-03-01	31385
Nissan	370z	3.7	Coupe	Heckantrieb	Benzin	241	328	Jun 2009	-	2024-03-01	31387
Jaguar	Xk ii	5.0 XKR	Cabriolet	Heckantrieb	Benzin	375	510	Jan 2009	Jul 2014	2024-03-01	31401
Jaguar	Xk ii	5.0 XKR	Coupe	Heckantrieb	Benzin	375	510	Jan 2009	Jul 2014	2024-03-01	31403
Volvo	S80 ii	D3	Stufenheck	Frontantrieb	Diesel	100	136	May 2012	May 2014	2024-03-01	31406
Chevrolet	Corvette	6.2 ZR1	Coupe	Heckantrieb	Benzin	476	647	Sep 2008	Aug 2013	2024-03-01	31407
Mercedes-benz	Sl	65 AMG Black Series	Cabriolet	Heckantrieb	Benzin	493	670	Jul 2008	Jan 2012	2024-03-01	31408
Mercedes-benz	E-Klasse	E 36 AMG	Stufenheck	Heckantrieb	Benzin	200	272	Apr 1996	Jan 1998	2024-03-01	31412
Ferrari	Superamerica	575	Cabriolet	Heckantrieb	Benzin	397	540	Jan 2005	Apr 2006	2024-03-01	31418
Audi	Q7	4.2 TDI Quattro	SUV	Allrad	Diesel	250	340	May 2009	Aug 2015	2024-03-01	31430
Audi	Tt	2.5 RS Quattro	Coupe	Allrad	Benzin	250	340	Jul 2009	Jun 2014	2024-03-01	31438
Audi	Tt	2.5 RS Quattro	Cabriolet	Allrad	Benzin	250	340	Jul 2009	Jun 2014	2024-03-01	31439
Hyundai	Genesis	2.0 Cvvt	Coupe	Heckantrieb	Benzin	154	209	Jun 2008	Feb 2014	2024-03-01	31446
Chevrolet	Cruze	1.6	Stufenheck	Frontantrieb	Benzin	83	113	May 2009	-	2024-03-01	31469
Chevrolet	Cruze	1.8	Stufenheck	Frontantrieb	Benzin	104	141	May 2009	-	2024-03-01	31470
Chevrolet	Cruze	2.0 CDI	Stufenheck	Frontantrieb	Diesel	110	150	May 2009	-	2024-03-01	31471
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	81	110	Feb 2013	Dec 2016	2024-03-01	31476
Volvo	Xc90 i	D3 / D5	SUV	Frontantrieb	Diesel	120	163	Apr 2009	Dec 2014	2024-03-01	31478
Hyundai	H100	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	74	101	Nov 2006	-	2024-03-01	31489
Mercedes-benz	R-Klasse	R 300 CDI	Großraumlimousine	Heckantrieb	Diesel	140	190	Jul 2009	Dec 2012	2024-03-01	31493
Mercedes-benz	R-Klasse	R 300 CDI 4-matic	Großraumlimousine	Allrad	Diesel	140	190	Jul 2009	Dec 2012	2024-03-01	31494
Mercedes-benz	R-Klasse	R 350 CDI 4-matic	Großraumlimousine	Allrad	Diesel	165	224	Jul 2009	Dec 2012	2024-03-01	31495
Mercedes-benz	R-Klasse	R 350 CDI 4-matic	Großraumlimousine	Allrad	Diesel	155	211	Jan 2006	Dec 2014	2024-03-01	31496
Mercedes-benz	R-Klasse	R 300	Großraumlimousine	Heckantrieb	Benzin	170	231	Jul 2009	Dec 2014	2024-03-01	31497
Mercedes-benz	C-Klasse	C 350 CDI	Stufenheck	Heckantrieb	Diesel	165	224	Jul 2009	Jan 2014	2024-03-01	31499
Mercedes-benz	C-Klasse	C 350 CDI 4-matic	Stufenheck	Allrad	Diesel	165	224	Jul 2009	Jan 2014	2024-03-01	31500
Mercedes-benz	C-Klasse	C 250 CGI	Stufenheck	Heckantrieb	Benzin	150	204	Jul 2009	Jan 2014	2024-03-01	31501
Mercedes-benz	C-Klasse	C 300	Stufenheck	Heckantrieb	Benzin	170	231	Jul 2009	Jan 2014	2024-03-01	31502
Mercedes-benz	C-Klasse	C 300 4-matic	Stufenheck	Allrad	Benzin	170	231	Jul 2007	Jan 2014	2024-03-01	31503
Audi	A6 c6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Apr 2009	Mar 2011	2024-03-01	31513
Audi	A6 c6 avant	3	Kombi	Frontantrieb	Benzin	160	218	Mar 2005	May 2006	2024-03-01	31514
Audi	A6 c6 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	120	163	Apr 2009	Aug 2011	2024-03-01	31517
Citroën	Nemo	1.4 HDI	Großraumlimousine	Frontantrieb	Diesel	50	68	Apr 2009	-	2024-03-01	31518
Citroën	Nemo	1.4	Großraumlimousine	Frontantrieb	Benzin	54	73	Apr 2009	-	2024-03-01	31519
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	55	75	Jun 2008	Dec 2012	2024-03-01	31520
Peugeot	308 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	103	140	Sep 2007	Oct 2014	2024-03-01	31521
Peugeot	308 cc	1.6 16V	Cabriolet	Frontantrieb	Benzin	88	120	Jun 2009	Dec 2014	2024-03-01	31522
Peugeot	308 cc	1.6 HDI	Cabriolet	Frontantrieb	Diesel	82	112	Jun 2009	Dec 2014	2024-03-01	31523
Peugeot	3008 i	1.6 THP	Großraumlimousine	Frontantrieb	Benzin	115	156	Jun 2009	Aug 2016	2024-11-01	31524
Peugeot	Bipper	1.4	Großraumlimousine	Frontantrieb	Benzin	54	73	Apr 2008	-	2024-03-01	31525
Peugeot	Bipper	1.4 HDI	Großraumlimousine	Frontantrieb	Diesel	50	68	Apr 2008	-	2024-03-01	31526
Renault	Clio iii	2.0 16V Sport	Schrägheck	Frontantrieb	Benzin	148	200	Sep 2008	Dec 2014	2026-05-01	31527
Renault	Laguna iii	3.0 DCI	Schrägheck	Frontantrieb	Diesel	173	235	Sep 2008	Dec 2015	2024-03-01	31528
Renault	Laguna iii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	81	110	Oct 2007	Dec 2015	2024-03-01	31529
Renault	Laguna iii grandtour	3.0 DCI	Kombi	Frontantrieb	Diesel	173	235	Sep 2008	Dec 2015	2024-03-01	31530
Renault	Megane iii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	74	101	May 2009	Aug 2015	2024-03-01	31531
Renault	Megane iii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	81	110	May 2009	Aug 2015	2024-03-01	31532
Renault	Megane iii grandtour	2.0 CVT	Kombi	Frontantrieb	Benzin	103	140	May 2009	Aug 2015	2024-03-01	31533
Renault	Megane iii grandtour	1.4 TCE	Kombi	Frontantrieb	Benzin	96	130	May 2009	Aug 2015	2024-03-01	31534
Renault	Megane iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	66	90	May 2009	Aug 2015	2024-03-01	31535
Renault	Megane iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	81	110	Feb 2009	Aug 2015	2024-03-01	31536
Renault	Megane iii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	96	131	May 2009	Aug 2015	2024-03-01	31537
Renault	Megane iii	2.0 CVT	Coupe	Frontantrieb	Benzin	103	140	May 2009	Aug 2015	2024-03-01	31538
Renault	Megane iii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	118	160	Apr 2009	Aug 2015	2024-03-01	31541
Renault	Megane iii grandtour	2.0 TCE	Kombi	Frontantrieb	Benzin	132	180	Nov 2008	Aug 2015	2024-03-01	31542
Renault	Scénic iii	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	81	110	Feb 2009	Sep 2016	2024-05-01	31543
Renault	Scénic iii	1.4 16V	Großraumlimousine	Frontantrieb	Benzin	96	131	Feb 2009	Sep 2016	2024-05-01	31544
Renault	Scénic iii	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	103	140	Feb 2009	Sep 2016	2024-05-01	31545
Renault	Scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	78	106	Feb 2009	Sep 2016	2024-05-01	31546
Renault	Scénic iii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Feb 2009	Sep 2016	2024-05-01	31547
Renault	Scénic iii	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	96	131	Feb 2009	Sep 2016	2024-05-01	31548
Renault	Scénic iii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	118	160	Apr 2009	Sep 2016	2024-05-01	31549
Renault	Grand scénic iii	1.4 16V	Großraumlimousine	Frontantrieb	Benzin	96	131	Feb 2009	Sep 2016	2024-05-01	31550
Renault	Grand scénic iii	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	81	109	Feb 2009	Sep 2016	2024-05-01	31551
Renault	Grand scénic iii	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	103	140	Feb 2009	Sep 2016	2024-05-01	31552
Renault	Grand scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	78	106	Feb 2009	Sep 2016	2024-05-01	31553
Renault	Grand scénic iii	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	96	131	Feb 2009	Sep 2016	2024-05-01	31554
Renault	Grand scénic iii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Feb 2009	Sep 2016	2024-05-01	31555
Renault	Grand scénic iii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	118	160	Apr 2009	Sep 2016	2024-05-01	31556
Toyota	Verso	1.6	Großraumlimousine	Frontantrieb	Benzin	97	132	Apr 2009	Aug 2018	2024-03-01	31564
Toyota	Verso	1.8	Großraumlimousine	Frontantrieb	Benzin	108	147	Apr 2009	Aug 2018	2024-03-01	31565
Toyota	Verso	2.0 D-4d	Großraumlimousine	Frontantrieb	Diesel	93	126	Apr 2009	Aug 2018	2024-03-01	31566
Toyota	Verso	2.2 D-4d	Großraumlimousine	Frontantrieb	Diesel	110	150	Apr 2009	Aug 2018	2024-03-01	31567
Toyota	Verso	2.2 D-cat	Großraumlimousine	Frontantrieb	Diesel	130	177	Apr 2009	Aug 2018	2024-03-01	31568
Audi	A5	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	132	180	Sep 2009	Jun 2014	2024-03-01	31569
Audi	A5	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	155	211	Sep 2009	Jan 2017	2024-03-01	31570
Audi	A5	3.2 FSI Quattro	Schrägheck	Allrad	Benzin	195	265	Sep 2009	Mar 2012	2024-03-01	31571
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Sep 2009	Mar 2012	2024-03-01	31572
Audi	A5	2.7 TDI	Schrägheck	Frontantrieb	Diesel	140	190	Sep 2009	Mar 2012	2024-03-01	31573
Audi	A5	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	176	240	Sep 2009	Mar 2012	2024-03-01	31574
Mercedes-benz	E-Klasse	E 200 CDI / Bluetec	Kombi	Heckantrieb	Diesel	100	136	Nov 2009	Dec 2016	2024-03-01	31575
Mercedes-benz	E-Klasse	E 220 CDI / Bluetec	Kombi	Heckantrieb	Diesel	125	170	Nov 2009	Dec 2016	2024-03-01	31576
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec	Kombi	Heckantrieb	Diesel	150	204	Nov 2009	Dec 2016	2024-03-01	31577
Mercedes-benz	E-Klasse	E 350 CDI	Kombi	Heckantrieb	Diesel	170	231	Nov 2009	Dec 2011	2024-03-01	31578
Mercedes-benz	E-Klasse	E 350 CDI 4-matic	Kombi	Allrad	Diesel	170	231	Nov 2009	Dec 2011	2024-03-01	31579
Mercedes-benz	E-Klasse	E 200 CGI	Kombi	Heckantrieb	Benzin	135	184	Nov 2009	Dec 2016	2024-03-01	31580
Mercedes-benz	E-Klasse	E 250 CGI	Kombi	Heckantrieb	Benzin	150	204	Nov 2009	Dec 2013	2024-03-01	31581
Mercedes-benz	E-Klasse	E 350 4-matic	Kombi	Allrad	Benzin	200	272	Nov 2009	Dec 2011	2024-03-01	31582
Mercedes-benz	E-Klasse	E 350 CGI	Kombi	Heckantrieb	Benzin	215	292	Nov 2009	Dec 2011	2024-03-01	31583
Mercedes-benz	E-Klasse	E 500	Kombi	Heckantrieb	Benzin	285	388	Nov 2009	Dec 2011	2024-03-01	31584
Audi	A4 allroad b8	2.0 TDI Quattro	Kombi	Allrad	Diesel	105	143	Sep 2009	May 2016	2024-03-01	31585
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	155	211	Jun 2009	Dec 2012	2024-03-01	31586
Seat	Leon	2.0 Cupra R	Schrägheck	Frontantrieb	Benzin	195	265	Sep 2009	Dec 2012	2024-03-01	31587
Seat	Exeo	2.0 TDI	Stufenheck	Frontantrieb	Diesel	88	120	Dec 2008	May 2013	2024-03-01	31588
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jun 2009	Apr 2013	2024-03-01	31590
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Jun 2009	Apr 2013	2024-03-01	31591
Skoda	Octavia	1.4 TSI	Schrägheck	Frontantrieb	Benzin	90	122	Nov 2008	Jun 2013	2024-03-01	31592
Skoda	Octavia	1.4 TSI	Kombi	Frontantrieb	Benzin	90	122	Nov 2008	Jun 2013	2024-03-01	31593


--- Round 1 / 首次发送 ---
## 更新点

* 复用历史缓存尺寸组，新增闭合 26 个 Ktype 映射，未重复输出既有尺寸组。
* 新建 `EU-SEAT-EXEO-I-SEDAN-01`；SEAT Exeo 2009 车主手册明确给出车长 4661 mm、车宽 1772 mm、车高 1430 mm。([汽车手册在线][1])
* 本轮合计新增 27 个 READY 映射、1 个 DIMENSION_GROUP。

## 当前批次进度

* READY 映射：27
* PENDING／待闭合 Ktype：73
* 已确认尺寸组：21

  * 历史缓存复用：20
  * 本轮首次创建：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31384	31384	MPV	Grand Voyager V	RT	5	EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	HIGH		READY
31406	31406	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
31430	31430	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH		READY
31476	31476	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
31478	31478	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	HIGH		READY
31513	31513	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-FACELIFT-SEDAN-01	HIGH		READY
31514	31514	Wagon	A6 C6 pre-facelift	4F5	5	EU-AUDI-A6-C6-PREFL-WAGON-01	HIGH		READY
31517	31517	Wagon	A6 C6 facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
31518	31518	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	HIGH		READY
31519	31519	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	HIGH		READY
31520	31520	Hatchback	Fiesta VI (CB1)	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	三门与五门共用该外廓；输入未区分门数。	READY
31521	31521	Wagon	308 SW I Phase I		5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
31522	31522	Convertible	308 CC I Phase I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
31523	31523	Convertible	308 CC I Phase I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
31524	31524	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH		READY
31525	31525	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	HIGH		READY
31526	31526	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	HIGH		READY
31527	31527	Hatchback	Clio III RS		3	EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	HIGH		READY
31528	31528	Hatchback	Laguna III	BT	5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
31529	31529	Wagon	Laguna III Grandtour	KT	5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
31530	31530	Wagon	Laguna III Grandtour	KT	5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
31586	31586	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FR-01	HIGH		READY
31588	31588	Sedan	Exeo I		4	EU-SEAT-EXEO-I-SEDAN-01	HIGH		READY
31590	31590	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
31591	31591	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
31592	31592	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
31593	31593	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-EXEO-I-SEDAN-01	4661	1772	1430	SEAT Exeo 2009 Owner's Manual	https://www.carmanualsonline.info/seat-exeo-2009-owner-s-manual/?srch=width
```

## 下一步优先处理

1. 集中闭合 Scénic III 与 Grand Scénic III 两个 MPV 车身组，覆盖 Ktype `31543–31556`。
2. 核对 Megane III Grandtour、Coupe 跨 Phase I／改款边界，批量解决 `31531–31542`。
3. 处理 Toyota Verso、Audi A5 Sportback 和 Mercedes-Benz E-Class W212 Wagon 的改款前后外廓分支。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/seat-exeo-2009-owner-s-manual/?srch=width "width Seat Exeo 2009 Owner's manual (310 Pages)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 C-Class W204、Toyota Verso、Scénic III 和 Grand Scénic III 四个车型簇；对生产区间跨越且外廓尺寸发生变化的 Ktype，按 `prefl`／`facelift` 拆分。
* 新增 48 行 READY 映射，覆盖 24 个原始 Ktype。
* 首次创建 8 个尺寸组。W204 改款前后车长分别为 4581 mm、4591 mm；Verso 改款前后车长分别为 4440 mm、4460 mm。([汽车目录][1])
* Scénic III 使用 4344 mm 与 4366 mm 两套外廓；Grand Scénic III 使用 4560 mm 与 4573 mm 两套外廓。([autocatalogarchive.com][2])

## 当前批次进度

* 已闭合输入 Ktype：51 / 100
* READY 映射行：75
* PENDING Ktype：49
* 已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31499_prefl	31499	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31499_facelift	31499	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31500_prefl	31500	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31500_facelift	31500	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31501_prefl	31501	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31501_facelift	31501	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31502_prefl	31502	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31502_facelift	31502	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31503_prefl	31503	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31503_facelift	31503	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31543_prefl	31543	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31543_facelift	31543	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31544_prefl	31544	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31544_facelift	31544	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31545_prefl	31545	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31545_facelift	31545	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31546_prefl	31546	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31546_facelift	31546	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31547_prefl	31547	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31547_facelift	31547	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31548_prefl	31548	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31548_facelift	31548	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31549_prefl	31549	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31549_facelift	31549	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31550_prefl	31550	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31550_facelift	31550	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31551_prefl	31551	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31551_facelift	31551	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31552_prefl	31552	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31552_facelift	31552	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31553_prefl	31553	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31553_facelift	31553	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31554_prefl	31554	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31554_facelift	31554	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31555_prefl	31555	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31555_facelift	31555	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31556_prefl	31556	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31556_facelift	31556	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31564_prefl	31564	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31564_facelift	31564	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31565_prefl	31565	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31565_facelift	31565	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31566_prefl	31566	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31566_facelift	31566	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31567_prefl	31567	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31567_facelift	31567	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31568_prefl	31568	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31568_facelift	31568	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	4581	1770	1447	Automobile-Catalog Mercedes-Benz C-Class W204 Phase I	https://www.automobile-catalog.com/make/mercedes-benz/w-204_c_class/w204/2010.html
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	4591	1770	1447	Mercedes-Benz C-Class Saloon and Estate brochure	https://ragtop.org/mbbrochures/2012/ireland/20110511C-Class_WS204_0611_021.pdf
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637	Renault Grand Scenic and Scenic 2009 brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Scenic-Grand-Scenic-2009-UK.pdf
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640	Auto-Data Renault Scenic III Phase II	https://www.auto-data.net/en/renault-scenic-iii-phase-ii-collection-2012-generation-3874
EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	4560	1845	1645	Renault Grand Scenic and Scenic 2009 brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Scenic-Grand-Scenic-2009-UK.pdf
EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase II	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-ii-collection-2012-generation-3873
EU-TOYOTA-VERSO-I-MPV-PREFL-01	4440	1790	1620	Toyota New Verso UK brochure	https://xr793.com/wp-content/uploads/2022/12/2010-Toyota-Verso-UK.pdf
EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	4460	1790	1620	Toyota Verso official press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/1517399376180122MVersofullrelease.pdf
```

## 下一步优先处理

1. 闭合 Megane III Grandtour 与 Coupe，复用已有 Coupe 改款尺寸组并仅补建 Grandtour 组。
2. 处理 Audi A5 Sportback、Mercedes-Benz E-Class S212 Wagon 和 R-Class W251 的跨改款分支。
3. 随后处理 Cruze、370Z、Genesis Coupe、Tribeca 及其余单车型特殊外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/mercedes-benz/w-204_c_class/w204/2010.html?utm_source=chatgpt.com "2010 Mercedes-Benz C Sedan W204 phase-I RWD (2WD) ..."
[2]: https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Scenic-Grand-Scenic-2009-UK.pdf?utm_source=chatgpt.com "RENAULT GRAND SCENIC & SCENIC"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Megane III Grandtour／Coupe、Audi A5 Sportback、Mercedes-Benz E-Class S212 Wagon 和 Leon II Cupra R，共新增 49 行 READY 映射，覆盖 27 个 Ktype。
* 首次创建 6 个尺寸组；复用 Megane III Coupe 的 3 个既有组及 Leon II facelift 既有组，不重复输出。
* Megane Grandtour 按 4559 mm 与 4567 mm 两套外廓拆分；A5 Sportback 按 4711 mm 与 4712 mm 拆分；S212 Wagon 按改款前后 4895 mm 与 4905 mm 拆分。([汽车目录][1])

## 当前批次进度

* 已闭合输入 Ktype：78 / 100
* READY 映射行：124
* PENDING／待闭合 Ktype：22
* 当前映射已引用尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31531_phase12	31531	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31531_phase3	31531	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31532_phase12	31532	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31532_phase3	31532	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31533_phase12	31533	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31533_phase3	31533	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31534_phase12	31534	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31534_phase3	31534	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31535_phase12	31535	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31535_phase3	31535	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31536_phase12	31536	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31536_phase3	31536	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31537_phase12	31537	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31537_phase3	31537	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31538_prefl	31538	Coupe	Megane III Coupe pre-facelift		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	跨三阶段外廓变化拆分。	READY
31538_facelift1	31538	Coupe	Megane III Coupe facelift I		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	跨三阶段外廓变化拆分。	READY
31538_facelift2	31538	Coupe	Megane III Coupe facelift II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	跨三阶段外廓变化拆分。	READY
31541_phase12	31541	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31541_phase3	31541	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31542_phase12	31542	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31542_phase3	31542	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31569_prefl	31569	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31569_facelift	31569	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31570_prefl	31570	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31570_facelift	31570	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31571_prefl	31571	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31571_facelift	31571	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31572_prefl	31572	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31572_facelift	31572	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31573_prefl	31573	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31573_facelift	31573	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31574_prefl	31574	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31574_facelift	31574	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31575_prefl	31575	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31575_facelift	31575	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31576_prefl	31576	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31576_facelift	31576	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31577_prefl	31577	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31577_facelift	31577	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31578	31578	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31579	31579	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31580_prefl	31580	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31580_facelift	31580	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31581_prefl	31581	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31581_facelift	31581	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31582	31582	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31583	31583	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31584	31584	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31587	31587	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	4559	1804	1507	Automobile-Catalog 2009 Renault Megane Estate (Grandtour) 1.5 dCi 110 FAP	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	4567	1804	1507	Automobile-Catalog 2014 Renault Megane Estate (Grandtour) 1.6 Energy dCi 130	https://www.automobile-catalog.com/car/2014/2961185/renault_megane_estate_grandtour_1_6_energy_dci_130.html
EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	4711	1854	1391	Auto-Data Audi A5 Sportback (8TA)	https://www.auto-data.net/en/audi-a5-sportback-8ta-generation-1095
EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	4712	1854	1391	Auto-Data Audi A5 Sportback (8TA, facelift 2011)	https://www.auto-data.net/en/audi-a5-sportback-8ta-facelift-2011-generation-4153
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	4895	1854	1512	Auto-Data Mercedes-Benz E-class T-modell (S212) E 220 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-220-cdi-blueefficiency-170hp-17375
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	4905	1854	1507	Auto-Data Mercedes-Benz E-class T-modell (S212, facelift 2013) E 220 CDI	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-facelift-2013-e-220-cdi-170hp-18745
```

## 下一步优先处理

1. 闭合剩余 R-Class W251、Chevrolet Cruze Sedan 和 Audi A4 Allroad B8 聚类。
2. 处理 370Z、TT RS Coupe／Roadster、Jaguar XKR Coupe／Convertible 等双车身或特殊性能外廓。
3. 最后处理 Tribeca、Genesis Coupe、H100、E 36 AMG、Ferrari Superamerica 等单独车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html?utm_source=chatgpt.com "2009 Renault Megane Estate (Grandtour) 1.5 dCi 110 FAP ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 Tribeca、370Z、Corvette ZR1、SL 65 AMG Black Series 四个特殊车身；Black Series 按固定车顶宽体 Coupe 修正车身形式。([auto-data.net][1])
* 闭合 Jaguar XKR Coupe／Convertible；车宽采用官方资料明确标注的 excluding mirrors 口径。([media.jaguar.com][2])
* 闭合 TT RS Coupe／Roadster、Cruze Sedan 和 A4 Allroad B8；A4 Allroad 改款前后外廓三维一致，使用同一尺寸组。([auto-data.net][3])
* 新增 12 个 READY 映射、10 个尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：90 / 100
* READY 映射行：136
* PENDING／待闭合 Ktype：10
* 当前映射已引用尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31385	31385	SUV	Tribeca facelift 2007		5	EU-SUBARU-TRIBECA-FACELIFT-SUV-5D-01	HIGH		READY
31387	31387	Coupe	370Z	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-01	HIGH		READY
31401	31401	Convertible	XK II facelift	X150	2	EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	HIGH		READY
31403	31403	Coupe	XK II facelift	X150	2	EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	HIGH		READY
31407	31407	Coupe	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	HIGH		READY
31408	31408	Coupe	SL R230 facelift Black Series	R230	2	EU-MERCEDES-BENZ-SL-R230-BLACK-SERIES-COUPE-01	HIGH	Black Series为固定车顶宽体Coupe，修正输入车身形式。	READY
31438	31438	Coupe	TT RS 8J	8J	3	EU-AUDI-TT-8J-RS-COUPE-3D-01	HIGH		READY
31439	31439	Convertible	TT RS 8J	8J	2	EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	HIGH		READY
31469	31469	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31470	31470	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31471	31471	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31585	31585	Wagon	A4 allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-TRIBECA-FACELIFT-SUV-5D-01	4865	1880	1685	Auto-Data Subaru Tribeca facelift 2007 3.6R	https://www.auto-data.net/en/subaru-tribeca-facelift-2007-3.6r-258hp-automatic-16123
EU-NISSAN-370Z-Z34-COUPE-3D-01	4250	1845	1310	Auto-Data Nissan 370Z 3.7 328 Hp	https://www.auto-data.net/en/nissan-370z-3.7-328hp-664
EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	4794	1892	1329	Jaguar XK official brochure; Jaguar 2014 XK Media Newsroom	https://jaguarclubrussia.com/images/katalog/1990/JaguarXKX150/docXKX150/Jaguar_US-XK_2008.pdf;https://media.jaguar.com/en-us/news/2013/11/2014-jaguar-xk
EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	4794	1892	1322	Jaguar XK official brochure; Jaguar 2014 XK Media Newsroom	https://jaguarclubrussia.com/images/katalog/1990/JaguarXKX150/docXKX150/Jaguar_US-XK_2008.pdf;https://media.jaguar.com/en-us/news/2013/11/2014-jaguar-xk
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237	Auto-Data Chevrolet Corvette C6 ZR1	https://www.auto-data.net/en/chevrolet-corvette-coupe-c6-zr1-6.2i-v8-32v-638hp-14522
EU-MERCEDES-BENZ-SL-R230-BLACK-SERIES-COUPE-01	4589	1960	1310	Auto-Data Mercedes-Benz SL 65 AMG Black Series	https://www.auto-data.net/en/mercedes-benz-sl-coupe-r230-facelift-2008-amg-sl-65-black-series-v12-670hp-speedshift-41190
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342	Auto-Data Audi TT RS Coupe 8J	https://www.auto-data.net/en/audi-tt-rs-coupe-8j-2.5-tfsi-340hp-quattro-17882
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348	Auto-Data Audi TT RS Roadster 8J	https://www.auto-data.net/en/audi-tt-rs-roadster-8j-2.5-tfsi-340hp-17883
EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	4597	1788	1477	Auto-Data Chevrolet Cruze Sedan 1.6 113 Hp	https://www.auto-data.net/en/chevrolet-cruze-sedan-1.6-113hp-14575
EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	4721	1841	1495	Auto-Data Audi A4 Allroad B8 pre-facelift; Auto-Data Audi A4 Allroad B8 facelift	https://www.auto-data.net/en/audi-a4-allroad-b8-8k-2.0-tdi-143hp-quattro-4343;https://www.auto-data.net/en/audi-a4-allroad-b8-8k-facelift-2011-2.0-tdi-143hp-quattro-26639
```

## 下一步优先处理

1. 闭合 R-Class W251／V251 的 SWB、LWB及改款边界，覆盖 `31493–31497`。
2. 处理 Grand Vitara II 2.4 与 H100 Pritsche/Fahrgestell 的多外廓分支。
3. 最后闭合 E 36 AMG、Ferrari Superamerica 和 Genesis Coupe。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/subaru-tribeca-facelift-2007-3.6r-258hp-automatic-16123 "Subaru Tribeca (facelift 2007) 3.6R (258 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://media.jaguar.com/en-us/news/2013/11/2014-jaguar-xk "2014 Jaguar XK | Jaguar 2024 Media Newsroom"
[3]: https://www.auto-data.net/en/audi-tt-rs-coupe-8j-2.5-tfsi-340hp-quattro-17882 "Audi TT RS Coupe (8J) 2.5 TFSI (340 Hp) quattro | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Suzuki Grand Vitara II 2.4，依据官方规格将同一 Ktype 拆分为三门与五门两种外廓；现有缓存组三维不同，因此新建尺寸组，不覆盖历史记录。
* 闭合 Mercedes-Benz E 36 AMG、Ferrari 575M Superamerica 和 Hyundai Genesis Coupe。([Carsales][1])
* 闭合 Hyundai H100 Pritsche/Fahrgestell，映射到标准驾驶室底盘外廓。([AUTODOC][2])
* 本轮新增 6 行 READY 映射、6 个尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：95 / 100
* READY 映射行：142
* PENDING Ktype：5
* 当前映射已引用尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31383_3dr	31383	SUV	Grand Vitara II facelift 2008		3	EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-02	HIGH	三门与五门外廓不同，按三门分支拆分。	READY
31383_5dr	31383	SUV	Grand Vitara II facelift 2008		5	EU-SUZUKI-GRAND-VITARA-II-5D-FACELIFT-2008-SUV-01	HIGH	三门与五门外廓不同，按五门分支拆分。	READY
31412	31412	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-E36-AMG-SEDAN-01	HIGH		READY
31418	31418	Convertible	575M Superamerica		2	EU-FERRARI-575M-SUPERAMERICA-CONVERTIBLE-01	HIGH		READY
31446	31446	Coupe	Genesis Coupe I pre-facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-01	HIGH		READY
31489	31489	Pickup	H-100 Porter II		2	EU-HYUNDAI-H100-PORTER-II-CHASSIS-CAB-01	MEDIUM	标准驾驶室底盘分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-02	4060	1810	1695	Suzuki Grand Vitara January 2009 official specification and price list	https://media.prd.suzuki.nl/media/documents/Suzuki_GrandVitara-specprijslijst_jan2009.pdf
EU-SUZUKI-GRAND-VITARA-II-5D-FACELIFT-2008-SUV-01	4500	1810	1695	Suzuki Grand Vitara January 2009 official specification and price list	https://media.prd.suzuki.nl/media/documents/Suzuki_GrandVitara-specprijslijst_jan2009.pdf
EU-MERCEDES-BENZ-E-CLASS-W210-E36-AMG-SEDAN-01	4795	1799	1411	Carsales Mercedes-Benz E-Class E36 AMG 1996 specifications	https://www.carsales.com.au/research/mercedes-benz/e-class/1996/e36-amg/
EU-FERRARI-575M-SUPERAMERICA-CONVERTIBLE-01	4550	1935	1280	Auto-Data Ferrari 575M Superamerica	https://www.auto-data.net/en/ferrari-575m-maranello-575m-superamerica-540hp-6536
EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-01	4630	1864	1384	Hyundai 2010 Genesis Coupe official brochure	https://www.auto-brochures.com/makes/Hyundai/Genesis%20Coupe/Hyundai_US%20GenesisCoupe_2010.pdf
EU-HYUNDAI-H100-PORTER-II-CHASSIS-CAB-01	4850	1740	1970	Hyundai H-100 official flyer	https://www.hyundai.com/content/dam/hyundai/ph/en/data/marketing/brochure/product/h100/H-100_FLYERv2.pdf
```

## 下一步优先处理

1. 按已确认的 W251／V251 车身代码，完成 `31493–31497` 的标准轴距与长轴距派生映射。
2. 统一 R-Class 官方尺寸口径，闭合所需 SWB／LWB 尺寸组。
3. 达到 `PENDING=0` 后立即进行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.carsales.com.au/cars/details/1997-mercedes-benz-e-class-e36-amg-auto/SSE-AD-13678111/?utm_source=chatgpt.com "1997 Mercedes-Benz E-Class E36 AMG Auto"
[2]: https://www.autodoc.co.uk/spares/hyundai/h100/porter-platform-chassis/31489-2-5-td?utm_source=chatgpt.com "Parts Porter H100 2.5 TD 101 hp Diesel 2006 - 2026 4D56-T"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 剩余 `31493–31497` 已按 R-Class 标准轴距 `W251` 与长轴距 `V251` 两种物理外廓闭合。
* 本批 100 个输入 Ktype 已全部覆盖，共形成 152 行 READY 映射和 57 个尺寸组。
* 已完成机械检查：表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，无孤立尺寸组，三维及来源字段完整。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：152
* PENDING：0
* DIMENSION_GROUP：57
* 缺失尺寸组引用：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31383_3dr	31383	SUV	Grand Vitara II facelift 2008		3	EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-02	HIGH	三门与五门外廓不同，按三门分支拆分。	READY
31383_5dr	31383	SUV	Grand Vitara II facelift 2008		5	EU-SUZUKI-GRAND-VITARA-II-5D-FACELIFT-2008-SUV-01	HIGH	三门与五门外廓不同，按五门分支拆分。	READY
31384	31384	MPV	Grand Voyager V	RT	5	EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	HIGH		READY
31385	31385	SUV	Tribeca facelift 2007		5	EU-SUBARU-TRIBECA-FACELIFT-SUV-5D-01	HIGH		READY
31387	31387	Coupe	370Z	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-01	HIGH		READY
31401	31401	Convertible	XK II facelift	X150	2	EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	HIGH		READY
31403	31403	Coupe	XK II facelift	X150	2	EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	HIGH		READY
31406	31406	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
31407	31407	Coupe	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	HIGH		READY
31408	31408	Coupe	SL R230 facelift Black Series	R230	2	EU-MERCEDES-BENZ-SL-R230-BLACK-SERIES-COUPE-01	HIGH	Black Series为固定车顶宽体Coupe，修正输入车身形式。	READY
31412	31412	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-E36-AMG-SEDAN-01	HIGH		READY
31418	31418	Convertible	575M Superamerica		2	EU-FERRARI-575M-SUPERAMERICA-CONVERTIBLE-01	HIGH		READY
31430	31430	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH		READY
31438	31438	Coupe	TT RS 8J	8J	3	EU-AUDI-TT-8J-RS-COUPE-3D-01	HIGH		READY
31439	31439	Convertible	TT RS 8J	8J	2	EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	HIGH		READY
31446	31446	Coupe	Genesis Coupe I pre-facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-01	HIGH		READY
31469	31469	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31470	31470	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31471	31471	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	HIGH		READY
31476	31476	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
31478	31478	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	HIGH		READY
31489	31489	Pickup	H-100 Porter II		2	EU-HYUNDAI-H100-PORTER-II-CHASSIS-CAB-01	MEDIUM	标准驾驶室底盘分支。	READY
31493_swb	31493	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	HIGH	标准轴距W251外廓。	READY
31493_lwb	31493	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	HIGH	长轴距V251外廓。	READY
31494_swb	31494	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	HIGH	标准轴距W251外廓。	READY
31494_lwb	31494	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	HIGH	长轴距V251外廓。	READY
31495_swb	31495	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	HIGH	标准轴距W251外廓。	READY
31495_lwb	31495	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	HIGH	长轴距V251外廓。	READY
31496_swb	31496	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	HIGH	标准轴距W251外廓。	READY
31496_lwb	31496	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	HIGH	长轴距V251外廓。	READY
31497_swb	31497	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	HIGH	标准轴距W251外廓。	READY
31497_lwb	31497	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	HIGH	长轴距V251外廓。	READY
31499_prefl	31499	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31499_facelift	31499	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31500_prefl	31500	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31500_facelift	31500	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31501_prefl	31501	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31501_facelift	31501	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31502_prefl	31502	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31502_facelift	31502	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31503_prefl	31503	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	Ktype跨W204改款且车长变化，按改款前外廓拆分。	READY
31503_facelift	31503	Sedan	C-Class W204 facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨W204改款且车长变化，按改款后外廓拆分。	READY
31513	31513	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-FACELIFT-SEDAN-01	HIGH		READY
31514	31514	Wagon	A6 C6 pre-facelift	4F5	5	EU-AUDI-A6-C6-PREFL-WAGON-01	HIGH		READY
31517	31517	Wagon	A6 C6 facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
31518	31518	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	HIGH		READY
31519	31519	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	HIGH		READY
31520	31520	Hatchback	Fiesta VI (CB1)	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	三门与五门共用该外廓；输入未区分门数。	READY
31521	31521	Wagon	308 SW I Phase I		5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
31522	31522	Convertible	308 CC I Phase I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
31523	31523	Convertible	308 CC I Phase I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
31524	31524	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH		READY
31525	31525	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	HIGH		READY
31526	31526	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	HIGH		READY
31527	31527	Hatchback	Clio III RS		3	EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	HIGH		READY
31528	31528	Hatchback	Laguna III	BT	5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
31529	31529	Wagon	Laguna III Grandtour	KT	5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
31530	31530	Wagon	Laguna III Grandtour	KT	5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
31531_phase12	31531	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31531_phase3	31531	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31532_phase12	31532	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31532_phase3	31532	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31533_phase12	31533	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31533_phase3	31533	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31534_phase12	31534	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31534_phase3	31534	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31535_phase12	31535	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31535_phase3	31535	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31536_phase12	31536	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31536_phase3	31536	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31537_phase12	31537	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31537_phase3	31537	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31538_prefl	31538	Coupe	Megane III Coupe pre-facelift		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	跨三阶段外廓变化拆分。	READY
31538_facelift1	31538	Coupe	Megane III Coupe facelift I		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	跨三阶段外廓变化拆分。	READY
31538_facelift2	31538	Coupe	Megane III Coupe facelift II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	跨三阶段外廓变化拆分。	READY
31541_phase12	31541	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31541_phase3	31541	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31542_phase12	31542	Wagon	Megane III Grandtour Phase I/II		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	HIGH	跨Phase III外廓变化拆分。	READY
31542_phase3	31542	Wagon	Megane III Grandtour Phase III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	HIGH	跨Phase III外廓变化拆分。	READY
31543_prefl	31543	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31543_facelift	31543	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31544_prefl	31544	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31544_facelift	31544	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31545_prefl	31545	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31545_facelift	31545	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31546_prefl	31546	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31546_facelift	31546	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31547_prefl	31547	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31547_facelift	31547	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31548_prefl	31548	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31548_facelift	31548	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31549_prefl	31549	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款前外廓拆分。	READY
31549_facelift	31549	MPV	Scenic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Scenic III改款且车长变化，按改款后外廓拆分。	READY
31550_prefl	31550	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31550_facelift	31550	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31551_prefl	31551	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31551_facelift	31551	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31552_prefl	31552	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31552_facelift	31552	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31553_prefl	31553	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31553_facelift	31553	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31554_prefl	31554	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31554_facelift	31554	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31555_prefl	31555	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31555_facelift	31555	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31556_prefl	31556	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款前外廓拆分。	READY
31556_facelift	31556	MPV	Grand Scenic III Phase II/III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	HIGH	Ktype跨Grand Scenic III改款且车长变化，按改款后外廓拆分。	READY
31564_prefl	31564	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31564_facelift	31564	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31565_prefl	31565	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31565_facelift	31565	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31566_prefl	31566	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31566_facelift	31566	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31567_prefl	31567	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31567_facelift	31567	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31568_prefl	31568	MPV	Verso I pre-facelift		5	EU-TOYOTA-VERSO-I-MPV-PREFL-01	HIGH	Ktype跨Verso改款且车长变化，按改款前外廓拆分。	READY
31568_facelift	31568	MPV	Verso I facelift		5	EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	HIGH	Ktype跨Verso改款且车长变化，按改款后外廓拆分。	READY
31569_prefl	31569	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31569_facelift	31569	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31570_prefl	31570	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31570_facelift	31570	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31571_prefl	31571	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31571_facelift	31571	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31572_prefl	31572	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31572_facelift	31572	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31573_prefl	31573	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31573_facelift	31573	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31574_prefl	31574	Hatchback	A5 I Sportback pre-facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31574_facelift	31574	Hatchback	A5 I Sportback facelift	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31575_prefl	31575	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31575_facelift	31575	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31576_prefl	31576	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31576_facelift	31576	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31577_prefl	31577	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31577_facelift	31577	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31578	31578	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31579	31579	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31580_prefl	31580	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31580_facelift	31580	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31581_prefl	31581	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH	跨改款外廓变化拆分。	READY
31581_facelift	31581	Wagon	E-Class S212 facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	跨改款外廓变化拆分。	READY
31582	31582	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31583	31583	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31584	31584	Wagon	E-Class S212 pre-facelift	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
31585	31585	Wagon	A4 allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
31586	31586	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FR-01	HIGH		READY
31587	31587	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH		READY
31588	31588	Sedan	Exeo I		4	EU-SEAT-EXEO-I-SEDAN-01	HIGH		READY
31590	31590	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
31591	31591	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
31592	31592	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
31593	31593	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3901-4000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-02	4060	1810	1695	Suzuki Grand Vitara January 2009 official specification and price list	https://media.prd.suzuki.nl/media/documents/Suzuki_GrandVitara-specprijslijst_jan2009.pdf
EU-SUZUKI-GRAND-VITARA-II-5D-FACELIFT-2008-SUV-01	4500	1810	1695	Suzuki Grand Vitara January 2009 official specification and price list	https://media.prd.suzuki.nl/media/documents/Suzuki_GrandVitara-specprijslijst_jan2009.pdf
EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	5143	1954	1750	Auto-Data Chrysler Grand Voyager V 3.8i V6	https://www.auto-data.net/en/chrysler-grand-voyager-v-3.8i-v6-193hp-automatic-38765
EU-SUBARU-TRIBECA-FACELIFT-SUV-5D-01	4865	1880	1685	Auto-Data Subaru Tribeca facelift 2007 3.6R	https://www.auto-data.net/en/subaru-tribeca-facelift-2007-3.6r-258hp-automatic-16123
EU-NISSAN-370Z-Z34-COUPE-3D-01	4250	1845	1310	Auto-Data Nissan 370Z 3.7 328 Hp	https://www.auto-data.net/en/nissan-370z-3.7-328hp-664
EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	4794	1892	1329	Jaguar XK official brochure; Jaguar 2014 XK Media Newsroom	https://jaguarclubrussia.com/images/katalog/1990/JaguarXKX150/docXKX150/Jaguar_US-XK_2008.pdf;https://media.jaguar.com/en-us/news/2013/11/2014-jaguar-xk
EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	4794	1892	1322	Jaguar XK official brochure; Jaguar 2014 XK Media Newsroom	https://jaguarclubrussia.com/images/katalog/1990/JaguarXKX150/docXKX150/Jaguar_US-XK_2008.pdf;https://media.jaguar.com/en-us/news/2013/11/2014-jaguar-xk
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II 2.0 D	https://www.auto-data.net/en/volvo-s80-ii-2.0-d-136hp-46142
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237	Auto-Data Chevrolet Corvette C6 ZR1	https://www.auto-data.net/en/chevrolet-corvette-coupe-c6-zr1-6.2i-v8-32v-638hp-14522
EU-MERCEDES-BENZ-SL-R230-BLACK-SERIES-COUPE-01	4589	1960	1310	Auto-Data Mercedes-Benz SL 65 AMG Black Series	https://www.auto-data.net/en/mercedes-benz-sl-coupe-r230-facelift-2008-amg-sl-65-black-series-v12-670hp-speedshift-41190
EU-MERCEDES-BENZ-E-CLASS-W210-E36-AMG-SEDAN-01	4795	1799	1411	Carsales Mercedes-Benz E-Class E36 AMG 1996 specifications	https://www.carsales.com.au/research/mercedes-benz/e-class/1996/e36-amg/
EU-FERRARI-575M-SUPERAMERICA-CONVERTIBLE-01	4550	1935	1280	Auto-Data Ferrari 575M Superamerica	https://www.auto-data.net/en/ferrari-575m-maranello-575m-superamerica-540hp-6536
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737	Auto-Data Audi Q7 I facelift 4.2 TDI	https://www.auto-data.net/en/audi-q7-i-typ-4l-facelift-2009-4.2-tdi-v8-340hp-quattro-6-tiptronic-4859
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342	Auto-Data Audi TT RS Coupe 8J	https://www.auto-data.net/en/audi-tt-rs-coupe-8j-2.5-tfsi-340hp-quattro-17882
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348	Auto-Data Audi TT RS Roadster 8J	https://www.auto-data.net/en/audi-tt-rs-roadster-8j-2.5-tfsi-340hp-17883
EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-01	4630	1864	1384	Hyundai 2010 Genesis Coupe official brochure	https://www.auto-brochures.com/makes/Hyundai/Genesis%20Coupe/Hyundai_US%20GenesisCoupe_2010.pdf
EU-CHEVROLET-CRUZE-I-J300-SEDAN-4D-01	4597	1788	1477	Auto-Data Chevrolet Cruze Sedan 1.6 113 Hp	https://www.auto-data.net/en/chevrolet-cruze-sedan-1.6-113hp-14575
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data Seat Leon III ST	https://www.auto-data.net/en/seat-leon-iii-st-2.0-tdi-184hp-start-stop-19376
EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	4798	1898	1743	Auto-Data Volvo XC90 facelift 2.4 D3	https://www.auto-data.net/en/volvo-xc90-facelift-2007-2.4-d3-163hp-automatic-21818
EU-HYUNDAI-H100-PORTER-II-CHASSIS-CAB-01	4850	1740	1970	Hyundai H-100 official flyer	https://www.hyundai.com/content/dam/hyundai/ph/en/data/marketing/brochure/product/h100/H-100_FLYERv2.pdf
EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-02	4922	1922	1674	Mercedes-Benz R-Class official brochure	https://xr793.com/wp-content/uploads/2023/10/2011-Mercedes-Benz-R-Class-AUS.pdf
EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-02	5157	1922	1674	Mercedes-Benz R-Class official brochure	https://xr793.com/wp-content/uploads/2023/10/2011-Mercedes-Benz-R-Class-AUS.pdf
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	4581	1770	1447	Automobile-Catalog Mercedes-Benz C-Class W204 Phase I	https://www.automobile-catalog.com/make/mercedes-benz/w-204_c_class/w204/2010.html
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-FACELIFT-01	4591	1770	1447	Mercedes-Benz C-Class Saloon and Estate brochure	https://ragtop.org/mbbrochures/2012/ireland/20110511C-Class_WS204_0611_021.pdf
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459	Auto-Data Audi A6 C6 facelift 2.0 TDI	https://www.auto-data.net/en/audi-a6-4f-c6-facelift-2008-2.0-tdi-170hp-4636
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463	Auto-Data Audi A6 Avant C6 3.0	https://www.auto-data.net/en/audi-a6-avant-4f-c6-3.0-i-v6-30v-218hp-4683
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463	Auto-Data Audi A6 Avant C6 facelift 2.0 TDI	https://www.auto-data.net/en/audi-a6-avant-4f-c6-facelift-2008-2.0-tdi-170hp-dpf-4667
EU-CITROEN-NEMO-I-AJ-MPV-01	3959	1716	1721	Auto-Data Citroen Nemo Multispace 1.4 HDi	https://www.auto-data.net/en/citroen-nemo-multispace-1.4-hdi-70hp-54978
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481	Auto-Data Ford Fiesta VII Mk7 3-door 1.6 TDCi	https://www.auto-data.net/en/ford-fiesta-vii-mk7-3-door-1.6-tdci-75hp-8033
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564	Auto-Data Peugeot 308 SW I Phase I 2.0 HDi	https://www.auto-data.net/en/peugeot-308-sw-i-phase-i-2008-2.0-hdi-140hp-52711
EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	4440	1817	1427	Auto-Data Peugeot 308 CC I Phase I 1.6 VTi	https://www.auto-data.net/en/peugeot-308-cc-i-phase-i-2008-1.6-16v-vti-120hp-5361
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628	Auto-Data Peugeot 3008 I Phase I 1.6 THP	https://www.auto-data.net/en/peugeot-3008-i-phase-i-2009-1.6-thp-156hp-17630
EU-PEUGEOT-BIPPER-I-AJ-MPV-01	3959	1716	1721	Auto-Data Peugeot Bipper Tepee 1.4	https://www.auto-data.net/en/peugeot-bipper-tepee-1.4-75hp-17690
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477	Auto-Data Renault Clio III Phase I RS	https://www.auto-data.net/en/renault-clio-iii-phase-i-rs-2.0-i-16v-200hp-10400
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445	Auto-Data Renault Laguna III	https://www.auto-data.net/en/renault-laguna-iii-2.0-16v-140hp-10287
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445	Auto-Data Renault Laguna III Grandtour	https://www.auto-data.net/en/renault-laguna-iii-grandtour-2-0-16v-140hp-10296
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	4559	1804	1507	Automobile-Catalog 2009 Renault Megane Estate (Grandtour) 1.5 dCi 110 FAP	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	4567	1804	1507	Automobile-Catalog 2014 Renault Megane Estate (Grandtour) 1.6 Energy dCi 130	https://www.automobile-catalog.com/car/2014/2961185/renault_megane_estate_grandtour_1_6_energy_dci_130.html
EU-RENAULT-MEGANE-III-COUPE-PREFL-01	4299	1804	1435	Auto-Data Renault Megane III Coupe	https://www.auto-data.net/en/renault-megane-iii-coupe-generation-2146
EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	4299	1785	1423	Auto-Data Renault Megane III Coupe Phase II	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-ii-2012-generation-3875
EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	4299	1848	1435	Auto-Data Renault Megane III Coupe Phase III	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-iii-2014-generation-4288
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637	Renault Grand Scenic and Scenic 2009 brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Scenic-Grand-Scenic-2009-UK.pdf
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640	Auto-Data Renault Scenic III Phase II	https://www.auto-data.net/en/renault-scenic-iii-phase-ii-collection-2012-generation-3874
EU-RENAULT-GRAND-SCENIC-III-MPV-PREFL-01	4560	1845	1645	Renault Grand Scenic and Scenic 2009 brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Scenic-Grand-Scenic-2009-UK.pdf
EU-RENAULT-GRAND-SCENIC-III-MPV-FACELIFT-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase II	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-ii-collection-2012-generation-3873
EU-TOYOTA-VERSO-I-MPV-PREFL-01	4440	1790	1620	Toyota New Verso UK brochure	https://xr793.com/wp-content/uploads/2022/12/2010-Toyota-Verso-UK.pdf
EU-TOYOTA-VERSO-I-MPV-FACELIFT-01	4460	1790	1620	Toyota Verso official press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/1517399376180122MVersofullrelease.pdf
EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	4711	1854	1391	Auto-Data Audi A5 Sportback (8TA)	https://www.auto-data.net/en/audi-a5-sportback-8ta-generation-1095
EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	4712	1854	1391	Auto-Data Audi A5 Sportback (8TA, facelift 2011)	https://www.auto-data.net/en/audi-a5-sportback-8ta-facelift-2011-generation-4153
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	4895	1854	1512	Auto-Data Mercedes-Benz E-class T-modell (S212) E 220 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-220-cdi-blueefficiency-170hp-17375
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	4905	1854	1507	Auto-Data Mercedes-Benz E-class T-modell (S212, facelift 2013) E 220 CDI	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-facelift-2013-e-220-cdi-170hp-18745
EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	4721	1841	1495	Auto-Data Audi A4 Allroad B8 pre-facelift; Auto-Data Audi A4 Allroad B8 facelift	https://www.auto-data.net/en/audi-a4-allroad-b8-8k-2.0-tdi-143hp-quattro-4343;https://www.auto-data.net/en/audi-a4-allroad-b8-8k-facelift-2011-2.0-tdi-143hp-quattro-26639
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458	Auto-Data Seat Leon II facelift FR	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-fr-2.0-tfsi-211hp-46474
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data Seat Leon II facelift	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-generation-9017
EU-SEAT-EXEO-I-SEDAN-01	4661	1772	1430	SEAT Exeo 2009 Owner's Manual	https://www.carmanualsonline.info/seat-exeo-2009-owner-s-manual/?srch=width
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-1.6-tdi-cr-dpf-105hp-17434
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II Combi facelift	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-1.6-tdi-cr-dpf-105hp-17436
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3901-4000_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3901-4000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3901-4000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4691 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2121 行）

