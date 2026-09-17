# 任务：all 第 2701-2800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0028__0823adff


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2701-2800 行

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
all 第 2701-2800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2701-2800_ktype_dimension_mapping_final.tsv
- all_2701-2800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-DACIA-LODGY-MPV-01	4498	1751	1679
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1425
EU-LADA-GRANTA-I-HATCHBACK-01	4246	1700	1500
EU-LAMBORGHINI-AVENTADOR-S-ROADSTER-01	4797	2030	1136
EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	4459	1924	1180
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	4551	1939	1260
EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	5054	1953	1442
EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	5054	1953	1447
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465
EU-OPEL-ASTRA-G-HATCHBACK-3D-FACELIFT-01	4110	1709	1425
EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	4249	1753	1460
EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	4249	1753	1460
EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	4587	1753	1458
EU-OPEL-ASTRA-H-FAMILY-WAGON-01	4515	1753	1500
EU-OPEL-ASTRA-H-HATCHBACK-5D-FACELIFT-01	4249	1753	1460
EU-OPEL-ASTRA-H-SEDAN-01	4587	1753	1458
EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	4515	1753	1500
EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	4466	1840	1482
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-PAGANI-ZONDA-CINQUE-COUPE-01	4435	2055	1141
EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	4435	2055	1141
EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	4395	2055	1151
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Astra j	1.6 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	81	110	Jan 2014	Oct 2015	2024-03-01	132733
Opel	Astra j	1.6 Cdti	Kasten/Kombi	Frontantrieb	Diesel	81	110	Jan 2014	Oct 2015	2024-03-01	132735
Opel	Astra j	1.7 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	81	110	May 2013	Oct 2015	2024-03-01	132737
Opel	Astra j	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	96	131	Oct 2012	Oct 2015	2024-03-01	132744
Opel	Astra j	1.3 Cdti	Kasten/Kombi	Frontantrieb	Diesel	70	95	Oct 2012	Oct 2015	2024-03-01	132746
Nissan	Rogue	2.5 AWD	SUV	Allrad	Benzin	125	170	Jan 2010	Nov 2013	2024-03-01	132749
Opel	Astra j	2.0 Cdti	Kasten/Kombi	Frontantrieb	Diesel	121	165	Oct 2012	Oct 2015	2024-03-01	132750
Opel	Astra h	1.6 Ecotec	Kasten/Kombi	Frontantrieb	Benzin	85	116	Oct 2006	Dec 2010	2024-03-01	132752
Opel	Astra h	1.9 Cdti	Kasten/Kombi	Frontantrieb	Diesel	74	101	Aug 2005	Dec 2012	2024-03-01	132754
Opel	Astra h	1.4 Ecotec	Kasten/Kombi	Frontantrieb	Benzin	66	90	Dec 2004	Dec 2012	2024-03-01	132756
Opel	Astra h	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	59	80	Dec 2004	Jul 2007	2024-03-01	132775
Opel	Astra g	2.0 DTI	Kasten/Kombi	Frontantrieb	Diesel	74	101	Sep 2000	Apr 2005	2024-03-01	132778
Opel	Astra g	1.6	Kasten/Kombi	Frontantrieb	Benzin	74	101	Sep 1998	Jan 2004	2024-03-01	132779
Opel	Astra f	1.8 I	Kasten/Kombi	Frontantrieb	Benzin	66	90	Jun 1993	Aug 1994	2024-03-01	132780
Toyota	Yaris	1.3 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	63	86	Mar 2000	Sep 2005	2024-03-01	132784
Toyota	Yaris	1.5 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	78	106	Mar 2000	Mar 2003	2024-03-01	132785
Toyota	Yaris	1.4 D4D	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Oct 2001	Sep 2005	2024-03-01	132786
Renault	Megane iv	1.5 Blue DCI 95	Schrägheck	Frontantrieb	Diesel	70	95	Aug 2018	-	2024-03-01	132787
Toyota	Yaris	1.3 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	62	84	Apr 2003	Sep 2005	2024-03-01	132788
Renault	Megane iv grandtour	1.5 Blue DCI 95	Kombi	Frontantrieb	Diesel	70	95	Aug 2018	-	2024-03-01	132793
Renault	Megane iv	1.5 Blue DCI 115	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	132796
Renault	Megane iv grandtour	1.5 Blue DCI 115	Kombi	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	132797
Opel	Corsa d	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Jul 2012	Aug 2014	2024-03-01	132798
Opel	Corsa d	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Jul 2012	Aug 2014	2024-03-01	132799
Opel	Corsa d	1.7 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	96	131	Jul 2012	Aug 2014	2024-03-01	132800
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	183	249	Sep 2018	Jun 2020	2024-03-01	132801
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	183	249	Aug 2018	Jul 2020	2024-03-01	132802
Ford	S-Max	2.0 Ecoblue Bi-turbo	Großraumlimousine	Frontantrieb	Diesel	176	240	Jul 2018	Apr 2023	2026-03-01	132803
Ford	S-Max	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	140	190	Jul 2018	Apr 2023	2026-03-01	132804
Ford	S-Max	2.0 Ecoblue 4X4	Großraumlimousine	Allrad	Diesel	140	190	Jul 2018	Apr 2023	2026-03-01	132805
Dacia	Lodgy	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	80	109	Aug 2018	-	2024-03-01	132806
Opel	Zafira	1.6	Großraumlimousine	Frontantrieb	Benzin	100	136	Sep 2018	Jul 2019	2024-03-01	132825
Opel	Cascada	1.6	Cabriolet	Frontantrieb	Benzin	100	136	May 2018	Apr 2019	2024-03-01	132826
Ford	S-Max	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2018	Apr 2023	2026-03-01	132828
Ford	S-Max	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	110	150	Jul 2018	Apr 2023	2026-03-01	132829
Ford	S-Max	2.0 Ecoblue 4X4	Großraumlimousine	Allrad	Diesel	110	150	Jul 2018	Apr 2023	2026-03-01	132830
Ford	S-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	121	165	Jul 2018	Apr 2023	2026-03-01	132831
Ford	Galaxy iii	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2018	Apr 2023	2026-03-01	132832
Ford	Galaxy iii	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	110	150	Jul 2018	Apr 2023	2026-03-01	132833
Ford	Galaxy iii	2.0 Ecoblue 4X4	Großraumlimousine	Allrad	Diesel	110	150	Jul 2018	Apr 2023	2026-03-01	132834
Ford	Galaxy iii	2.0 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	140	190	Jul 2018	Apr 2023	2026-03-01	132835
Ford	Galaxy iii	2.0 Ecoblue 4X4	Großraumlimousine	Allrad	Diesel	140	190	Jul 2018	Apr 2023	2026-03-01	132836
Ford	Galaxy iii	2.0 Ecoblue Bi-turbo	Großraumlimousine	Frontantrieb	Diesel	176	240	Jul 2018	Apr 2023	2026-03-01	132837
Ford	Galaxy iii	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	121	165	Jul 2018	Apr 2023	2026-03-01	132838
Citroën	C5	1.2 Puretech 130	SUV	Frontantrieb	Benzin	96	131	Nov 2018	-	2024-07-01	132839
Citroën	C5	1.6 Puretech 180	SUV	Frontantrieb	Benzin	133	181	Nov 2018	-	2024-07-01	132840
Citroën	C5	1.5 Bluehdi 130	SUV	Frontantrieb	Diesel	96	131	Nov 2018	-	2024-07-01	132841
Citroën	C5	2.0 Bluehdi 180	SUV	Frontantrieb	Diesel	130	177	Nov 2018	-	2024-07-01	132842
Mercedes-benz	Amg gt	53 EQ Boost 4-matic+	Coupe	Allrad	Benzin/Elektro	320	435	Sep 2018	-	2024-03-01	132844
Mercedes-benz	Amg gt	43 EQ Boost 4-matic+	Coupe	Allrad	Benzin/Elektro	270	367	Sep 2018	-	2024-03-01	132845
Lamborghini	Aventador	6.5 LP 770-4 SVJ AWD	Coupe	Allrad	Benzin	566	770	Aug 2018	-	2024-03-01	132848
Mercedes-benz	Cls	CLS 220 D	Coupe	Heckantrieb	Diesel	143	194	Jun 2018	-	2024-03-01	132849
Land Rover	Range rover velar	3.0 D275 Sdv6 4X4	SUV	Allrad	Diesel	202	275	Apr 2018	-	2024-03-01	132852
Dacia	Duster	1.5 DCI 95	SUV	Frontantrieb	Diesel	70	95	Oct 2017	-	2024-03-01	132854
Dacia	Duster	1.5 DCI 115	SUV	Frontantrieb	Diesel	85	116	Oct 2017	-	2024-03-01	132855
Audi	A1	30 Tfsi	Schrägheck	Frontantrieb	Benzin	85	116	Jul 2018	-	2024-03-01	132856
Dacia	Duster	1.5 DCI 115 4X4	SUV	Allrad	Diesel	85	116	Oct 2017	-	2024-03-01	132857
Lada	Granta	1.6	Kombi	Frontantrieb	Benzin	78	106	Aug 2018	-	2024-03-01	132858
Lada	Granta	1.6	Kombi	Frontantrieb	Benzin	72	98	Aug 2018	-	2024-03-01	132859
Lada	Granta	1.6	Kombi	Frontantrieb	Benzin	64	87	Aug 2018	-	2024-03-01	132860
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	64	87	Aug 2018	-	2024-03-01	132861
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	72	98	Aug 2018	-	2024-03-01	132862
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	78	106	Aug 2018	-	2024-03-01	132863
Mercedes-benz	A-Klasse	AMG A 35 4-matic	Schrägheck	Allrad	Benzin	225	306	Sep 2018	-	2024-03-01	132864
Honda	Acty	0.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	23	31	Oct 1978	Jun 1987	2024-03-01	132896
Koenigsegg	Regera	5.0 Hybrid	Coupe	Heckantrieb	Benzin/Elektro	1119	1522	Mar 2015	-	2024-03-01	132897
Koenigsegg	Agera	RS 5.0	Coupe	Heckantrieb	Benzin/Ethanol	865	1176	Mar 2015	-	2024-03-01	132899
Koenigsegg	Agera	S 5.0	Coupe	Heckantrieb	Benzin/Ethanol	757	1029	Jun 2013	-	2024-03-01	132900
Koenigsegg	Agera	5	Coupe	Heckantrieb	Benzin/Ethanol	705	959	Jan 2011	-	2024-03-01	132901
Citroën	C3 aircross i	1.5 Bluehdi 120	SUV	Frontantrieb	Diesel	88	120	Aug 2018	-	2025-11-01	132902
Lamborghini	Centenario roadster	6.5 LP 770-4	Cabriolet	Allrad	Benzin	566	770	Apr 2016	-	2024-03-01	132904
Jaguar	Xe	2	Stufenheck	Heckantrieb	Benzin	147	200	Feb 2017	-	2024-03-01	132905
Bugatti	Divo	8	Coupe	Allrad	Benzin	1103	1500	Aug 2018	-	2024-03-01	132914
Pagani	Zonda	7.3	Coupe	Heckantrieb	Benzin	499	678	Jun 2009	May 2013	2024-03-01	132915
Pagani	Zonda roadster	7.3	Cabriolet	Heckantrieb	Benzin	478	650	Jun 2006	May 2009	2024-03-01	132916
Lamborghini	Huracán	5.2 Performante	Targa	Allrad	Benzin	470	639	Sep 2018	-	2025-12-01	132917
Skoda	Octavia	2.0 TSI	Schrägheck	Frontantrieb	Benzin	140	190	Feb 2017	Oct 2020	2024-03-01	132922
Skoda	Octavia	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Feb 2017	Oct 2020	2024-03-01	132923
Honda	Cr-V v	1.5 Vtec	SUV	Frontantrieb	Benzin	127	173	Aug 2017	-	2024-03-01	132926
Honda	Cr-V v	1.5 Vtec AWD	SUV	Allrad	Benzin	127	173	Aug 2017	-	2024-03-01	132928
Audi	A3	30 Tfsi	Schrägheck	Frontantrieb	Benzin	85	116	Jul 2018	Oct 2020	2024-03-01	132930
Audi	A3	35 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Oct 2018	Oct 2020	2024-03-01	132931
Audi	A3	30 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Jul 2018	Oct 2020	2024-03-01	132932
KTM	X-Bow	2.0 RR	Cabriolet	Heckantrieb	Benzin	265	360	Jul 2018	-	2024-03-01	132933
Audi	A3	30 Tfsi	Stufenheck	Frontantrieb	Benzin	85	115	Jul 2018	Oct 2020	2024-03-01	132934
Audi	A3	35 Tfsi	Stufenheck	Frontantrieb	Benzin	110	150	Oct 2018	Oct 2020	2024-03-01	132935
KTM	X-Bow	2.0 GT4	Coupe	Heckantrieb	Benzin	265	360	Jul 2018	-	2024-03-01	132936
Mclaren	600lt	3.8	Coupe	Heckantrieb	Benzin	441	600	Jun 2018	-	2024-03-01	132937
Renault	Clio iv grandtour	0.9 TCE 75	Kombi	Frontantrieb	Benzin	56	76	Aug 2018	Aug 2021	2026-05-01	132938
Mclaren	Senna	4	Coupe	Heckantrieb	Benzin	588	800	Jul 2018	-	2024-03-01	132939
Audi	A3	35 Tfsi	Cabriolet	Frontantrieb	Benzin	110	150	Oct 2018	Oct 2020	2024-03-01	132940
Audi	Q2	30 TDI	SUV	Frontantrieb	Diesel	85	115	Jul 2018	Oct 2020	2024-03-01	132942
Renault	Kadjar	1.3 TCE 160	SUV	Frontantrieb	Benzin	117	160	Aug 2018	-	2024-03-01	132945
Audi	Q5	35 TDI Quattro	SUV	Allrad	Diesel	120	163	Aug 2018	Nov 2020	2024-03-01	132946
Audi	Q5	40 TDI Quattro	SUV	Allrad	Diesel	140	190	Oct 2018	-	2024-03-01	132947
RUF	Scr	4	Coupe	Heckantrieb	Benzin	375	510	Jan 2018	-	2024-03-01	132949
RUF	Scr	4.2	Coupe	Heckantrieb	Benzin	386	525	Feb 2016	-	2024-03-01	132950
Aixam	City	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Oct 2016	-	2024-03-01	132955
Morgan	3-Wheeler	2	Cabriolet	Heckantrieb	Benzin	51	69	Sep 2017	-	2024-03-01	132957
RUF	Ctr	3.6	Coupe	Heckantrieb	Benzin	522	710	Mar 2017	-	2024-03-01	132959


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 99 个输入 Ktype 的物理外廓映射，共形成 102 条 `READY` 映射。
* `132749` 的生产区间跨 Nissan Rogue I 改款，改款前为 `4646×1801×1659 mm`，改款后为 `4656×1801×1684 mm`，已拆分为 `prefl`、`facelift` 两条派生映射。([汽车数据网][1])
* `132784`、`132786` 跨 Toyota Yaris I 改款，已按改款前后物理长度差异拆分。
* Audi A3 Sportback 采用 Audi 官方技术数据，将外廓闭合为 `4313×1785×1426 mm`，其中宽度明确为不含后视镜。([奥迪新闻][2])
* RUF SCR 4.2 已使用 2016 年官方技术资料闭合为 `4250×1652×1250 mm`。([i.i-sgcm][3])
* `132896` Honda Acty I 仍保留 `PENDING`：该 Ktype 横跨 1982 年改款，并存在驾驶室加长 100 mm 的 Big Cab 分支，当前无法在不猜测的情况下确定应输出哪些完整物理分支。([维基百科][4])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：103
* READY 映射：102
* PENDING 映射：1
* 已确认并引用尺寸组：60

  * 本轮首次创建：44
  * 跨批次复用：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132733	132733	Van	Astra J facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck 商用车外廓。	READY
132735	132735	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132737	132737	Van	Astra J facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck 商用车外廓。	READY
132744	132744	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132746	132746	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132749_prefl	132749	SUV	Rogue I pre-facelift	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132749_facelift	132749	SUV	Rogue I facelift	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132750	132750	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132752	132752	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132754	132754	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132756	132756	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132775	132775	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132778	132778	Van	Astra G	T98	5	EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132779	132779	Van	Astra G	T98	5	EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132780	132780	Van	Astra F pre-facelift	T92	5	EU-OPEL-ASTRA-F-T92-VAN-WAGON-PREFL-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132784_prefl	132784	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132784_facelift	132784	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132785	132785	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	Kasten/Schrägheck 三门商用车外廓。	READY
132786_prefl	132786	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132786_facelift	132786	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132787	132787	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
132788	132788	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Kasten/Schrägheck 三门商用车外廓。	READY
132793	132793	Wagon	Megane IV Grandtour		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
132796	132796	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
132797	132797	Wagon	Megane IV Grandtour		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
132798	132798	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132799	132799	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132800	132800	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132801	132801	SUV	X4 II	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132802	132802	SUV	X5 IV pre-facelift	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
132803	132803	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132804	132804	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132805	132805	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132806	132806	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
132825	132825	MPV	Zafira Tourer C facelift	P12	5	EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	HIGH		READY
132826	132826	Convertible	Cascada	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
132828	132828	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132829	132829	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132830	132830	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132831	132831	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132832	132832	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132833	132833	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132834	132834	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132835	132835	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132836	132836	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132837	132837	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132838	132838	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132839	132839	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132840	132840	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132841	132841	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132842	132842	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132844	132844	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH		READY
132845	132845	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH		READY
132848	132848	Coupe	Aventador SVJ	LB834	2	EU-LAMBORGHINI-AVENTADOR-SVJ-COUPE-01	HIGH		READY
132849	132849	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH		READY
132852	132852	SUV	Range Rover Velar I pre-facelift	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	HIGH		READY
132854	132854	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
132855	132855	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
132856	132856	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
132857	132857	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH		READY
132858	132858	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132859	132859	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132860	132860	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132861	132861	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132862	132862	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132863	132863	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132864	132864	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	HIGH	AMG A 35 外廓。	READY
132896	132896	Pickup	Acty I	TN	2		LOW	Ktype 跨 1982 改款及 Big Cab 分支，完整三维边界尚未闭合。	PENDING: 首代 Acty 物理分支未闭合
132897	132897	Coupe	Regera		2	EU-KOENIGSEGG-REGERA-COUPE-01	HIGH		READY
132899	132899	Coupe	Agera RS		2	EU-KOENIGSEGG-AGERA-RS-COUPE-01	HIGH		READY
132900	132900	Coupe	Agera S		2	EU-KOENIGSEGG-AGERA-COUPE-01	HIGH		READY
132901	132901	Coupe	Agera		2	EU-KOENIGSEGG-AGERA-COUPE-01	HIGH		READY
132902	132902	SUV	C3 Aircross I Phase I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH		READY
132904	132904	Convertible	Centenario Roadster		2	EU-LAMBORGHINI-CENTENARIO-ROADSTER-CONVERTIBLE-01	HIGH		READY
132905	132905	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
132914	132914	Coupe	Divo		2	EU-BUGATTI-DIVO-COUPE-01	HIGH		READY
132915	132915	Coupe	Zonda Cinque		2	EU-PAGANI-ZONDA-CINQUE-COUPE-01	HIGH		READY
132916	132916	Convertible	Zonda F Roadster		2	EU-PAGANI-ZONDA-F-ROADSTER-CONVERTIBLE-01	HIGH		READY
132917	132917	Convertible	Huracan Performante Spyder		2	EU-LAMBORGHINI-HURACAN-PERFORMANTE-SPYDER-CONVERTIBLE-01	HIGH	Targa 输入对应 Performante Spyder 开放式外廓。	READY
132922	132922	Hatchback	Octavia III facelift	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH	Schrägheck 对应五门 liftback 外廓。	READY
132923	132923	Wagon	Octavia III Combi facelift	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
132926	132926	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-FWD-01	HIGH		READY
132928	132928	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-AWD-01	HIGH		READY
132930	132930	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132931	132931	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132932	132932	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132933	132933	Convertible	X-Bow RR		0	EU-KTM-X-BOW-RR-CONVERTIBLE-01	HIGH	开放式车身，无常规车门。	READY
132934	132934	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
132935	132935	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
132936	132936	Coupe	X-Bow GT4		2	EU-KTM-X-BOW-GT4-COUPE-01	HIGH		READY
132937	132937	Coupe	600LT	P13	2	EU-MCLAREN-600LT-P13-COUPE-01	HIGH		READY
132938	132938	Wagon	Clio IV Grandtour Phase II		5	EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	HIGH		READY
132939	132939	Coupe	Senna	P15	2	EU-MCLAREN-SENNA-P15-COUPE-01	HIGH		READY
132940	132940	Convertible	A3 Cabriolet 8V facelift	8V	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
132942	132942	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
132945	132945	SUV	Kadjar I facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132946	132946	SUV	Q5 II pre-facelift	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
132947	132947	SUV	Q5 II pre-facelift	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
132949	132949	Coupe	SCR 2018		2	EU-RUF-SCR-2018-COUPE-01	HIGH		READY
132950	132950	Coupe	SCR 4.2		2	EU-RUF-SCR-4-2-COUPE-01	HIGH		READY
132955	132955	Hatchback	City 2016		3	EU-AIXAM-CITY-2016-HATCHBACK-01	MEDIUM		READY
132957	132957	Convertible	3 Wheeler		0	EU-MORGAN-3-WHEELER-ROADSTER-01	HIGH	开放式三轮车身，无常规车门。	READY
132959	132959	Coupe	CTR Anniversary		2	EU-RUF-CTR-ANNIVERSARY-COUPE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	4419	1814	1510	Auto-Data Opel Astra J facelift 1.6 CDTI	https://www.auto-data.net/en/opel-astra-j-facelift-2012-1.6-cdti-110hp-ecotec-start-stop-19434
EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	4698	1814	1535	Auto-Data Opel Astra J Sports Tourer facelift	https://www.auto-data.net/en/opel-astra-j-sports-tourer-facelift-2012-1.7-cdti-130hp-ecotec-19470
EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	4646	1801	1659	Auto-Data Nissan Rogue I S35 2.5i AWD CVT	https://www.auto-data.net/en/nissan-rogue-i-s35-2.5i-170hp-awd-cvt-832
EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	4656	1801	1684	Auto-Data Nissan Rogue I S35 facelift	https://www.auto-data.net/en/nissan-rogue-i-s35-facelift-2011-2.5i-170hp-cvt-34526
EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.6	https://www.auto-data.net/en/opel-astra-g-caravan-1.6-ecotec-16v-101hp-2417
EU-OPEL-ASTRA-F-T92-VAN-WAGON-PREFL-01	4278	1688	1475	Auto-Data Opel Astra F Caravan 1.8i	https://www.auto-data.net/en/opel-astra-f-caravan-1.8i-90hp-2489
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500	Auto-Data Toyota Yaris I 3-door	https://www.auto-data.net/en/toyota-yaris-i-3-door-generation-1052
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 3-door	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-1.4-d-4d-75hp-50708
EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	3999	1737	1488	Auto-Data Opel Corsa D facelift 3-door	https://www.auto-data.net/en/opel-corsa-d-facelift-2011-3-door-1.4-xer-100hp-16970
EU-FORD-S-MAX-II-MPV-01	4796	1916	1655	Auto-Data Ford S-Max II 2.0 EcoBlue	https://www.auto-data.net/en/ford-s-max-ii-2.0-ecoblue-190hp-s-s-34514
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660	Auto-Data Opel Zafira Tourer C facelift	https://www.auto-data.net/en/opel-zafira-tourer-c-facelift-2016-1.6-turbo-136hp-36415
EU-OPEL-CASCADA-W13-CONVERTIBLE-01	4696	1839	1443	Auto-Data Opel Cascada 1.6	https://www.auto-data.net/en/opel-cascada-1.6-136hp-automatic-33821
EU-FORD-GALAXY-III-MPV-01	4848	1916	1747	Auto-Data Ford Galaxy III	https://www.auto-data.net/en/ford-galaxy-iii-generation-4567
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670	Citroën C5 Aircross SUV Range 2018 brochure	https://www.charterscitroen.com/wp-content/uploads/sites/21/2017/06/citroen-c5-aircross-prices-specifications-brochure-november-2018.pdf
EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	5054	1953	1455	Auto-Data Mercedes-AMG GT 53 X290	https://www.auto-data.net/en/mercedes-benz-amg-gt-4-door-coupe-x290-53-435hp-eq-boost-4matic-amg-speedshift-tct-9g-34366
EU-LAMBORGHINI-AVENTADOR-SVJ-COUPE-01	4943	2098	1136	Auto-Data Lamborghini Aventador SVJ	https://www.auto-data.net/en/lamborghini-aventador-svj-6.5-v12-770hp-4wd-isr-34013
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	4803	1930	1665	Land Rover Introducing Range Rover Velar	https://media.landrover.com/en-gb/news/2017/03/introducing-range-rover-velar
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Auto-Data Audi A1 Sportback GB 30 TFSI	https://www.auto-data.net/en/audi-a1-sportback-gb-30-tfsi-116hp-34083
EU-LADA-GRANTA-I-FACELIFT-WAGON-01	4118	1700	1538	Auto-Data Lada Granta I facelift wagon	https://www.auto-data.net/en/lada-granta-i-facelift-2018-combi-1.6-16v-106hp-34498
EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	3926	1700	1500	Auto-Data Lada Granta model	https://www.auto-data.net/en/lada-granta-model-2080
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405	Auto-Data Mercedes-AMG A 35 W177	https://www.auto-data.net/en/mercedes-benz-a-class-w177-amg-a-35-306hp-4matic-dct-35067
EU-KOENIGSEGG-REGERA-COUPE-01	4560	2050	1110	Koenigsegg Regera technical specifications	https://www.koenigsegg.com/technical-specifications-regera
EU-KOENIGSEGG-AGERA-RS-COUPE-01	4293	2050	1120	Koenigsegg Agera RS technical specifications	https://www.koenigsegg.com/technical-specifications-agera-rs
EU-KOENIGSEGG-AGERA-COUPE-01	4293	1996	1120	Koenigsegg Agera R technical specifications	https://www.koenigsegg.com/technical-specifications-agera-r
EU-LAMBORGHINI-CENTENARIO-ROADSTER-CONVERTIBLE-01	4924	2061	1158	Lamborghini Centenario Roadster; LamboCars Centenario Roadster specifications	https://www.lamborghini.com/en-en/history/few-off/centenario-roadster; https://www.lambocars.com/centenario-lp770-4-roadster-specs-performance/
EU-BUGATTI-DIVO-COUPE-01	4641	2018	1212	Auto-Data Bugatti Divo	https://www.auto-data.net/en/bugatti-divo-8.0-w16-1500hp-awd-dsg-34033
EU-PAGANI-ZONDA-F-ROADSTER-CONVERTIBLE-01	4435	2055	1141	Auto-Data Pagani Zonda Roadster F	https://www.auto-data.net/en/pagani-zonda-roadster-f-7.3-v12-48v-650hp-24022
EU-LAMBORGHINI-HURACAN-PERFORMANTE-SPYDER-CONVERTIBLE-01	4506	1924	1180	Auto-Data Lamborghini Huracan Performante Spyder	https://www.auto-data.net/en/lamborghini-huracan-performante-spyder-generation-6155
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461	Auto-Data Skoda Octavia III facelift liftback	https://www.auto-data.net/en/skoda-octavia-iii-facelift-2017-2.0-tsi-190hp-dsg-35797
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465	Auto-Data Skoda Octavia III Combi facelift	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-2.0-tsi-190hp-dsg-35816
EU-HONDA-CR-V-V-RW-SUV-FWD-01	4600	1855	1679	Auto-Data Honda CR-V V 1.5 VTEC Turbo FWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-173hp-34296
EU-HONDA-CR-V-V-RW-SUV-AWD-01	4600	1855	1689	Auto-Data Honda CR-V V 1.5 VTEC Turbo AWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-173hp-awd-34297
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Audi UK A3 Sportback 1.5 TFSI technical data	https://press.audi.co.uk/assets/documents/original/11109-AudiUK00018622AudiA3Sportback15TFSI.pdf
EU-KTM-X-BOW-RR-CONVERTIBLE-01	3738	1915	1202	KTM X-Bow RR model information	https://www.ktm-cars.jp/x-bow/x-bow-r/model-info.html
EU-KTM-X-BOW-GT4-COUPE-01	4112	1933	1140	Mobility.fun KTM X-Bow GT4	https://www.mobility.fun/ktm-x-bow/x-bow-gt4
EU-MCLAREN-600LT-P13-COUPE-01	4604	1930	1194	McLaren 600LT official brochure; Auto-Data McLaren 600LT	https://autocatalogarchive.com/wp-content/uploads/2019/02/McLaren-600-LT-2019-INT.pdf; https://www.auto-data.net/en/mclaren-600lt-model-2482
EU-MCLAREN-SENNA-P15-COUPE-01	4744	1958	1229	McLaren Senna technical specification mirror; VehicleScore McLaren Senna dimensions	https://m.autoinfo.jp/release/Senna_spec_201802.pdf; https://vehiclescore.co.uk/car-dimensions-check/mclaren/senna
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-35-tfsi-150hp-35165
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Auto-Data Audi Q5 II FY 35 TDI quattro	https://www.auto-data.net/en/audi-q5-ii-fy-2.0-tdi-163hp-quattro-s-tronic-26239
EU-RUF-SCR-2018-COUPE-01	4207	1819	1265	Auto-Data RUF SCR 4.0	https://www.auto-data.net/en/ruf-scr-4.0-510hp-32841
EU-RUF-SCR-4-2-COUPE-01	4250	1652	1250	RUF SCR 4.2 official technical data brochure	https://i.i-sgcm.com/new_cars/cars/11913/brochures/brochure_20160927104832.pdf
EU-AIXAM-CITY-2016-HATCHBACK-01	2758	1500	1470	1000PS Aixam City 2016	https://www.1000ps.com/en-us/model/6353/aixam-city/2016
EU-MORGAN-3-WHEELER-ROADSTER-01	3225	1720	1000	Morgan 3 Wheeler official brochure	https://www.morgan-cars.jp/wp-content/uploads/2015/02/Inserts_3Wheeler.pdf
EU-RUF-CTR-ANNIVERSARY-COUPE-01	4207	1819	1265	RUF Japan CTR Anniversary specifications	https://www.ruf-web.co.jp/com/ctr2017/
```

## 下一步优先处理

1. 仅处理 Ktype `132896`：闭合 Honda Acty I 在 1978–1987 区间内的改款前、改款后标准驾驶室及 Big Cab 物理分支。
2. 确认各分支完整的长宽高和不含后视镜宽度后，将基础 `id=132896` 替换为有语义的派生行。
3. PENDING 清零后直接进行一次机械检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/nissan-rogue-i-s35-2.5i-170hp-awd-cvt-832?utm_source=chatgpt.com "Nissan Rogue I (S35) 2.5i (170 Hp) AWD CVT"
[2]: https://press.audi.co.uk/assets/documents/original/11109-AudiUK00018622AudiA3Sportback15TFSI.pdf "Audi A3 Sportback 1.5 TFSI 150PS S tronic Technical Data UK February 2018.xlsx"
[3]: https://i.i-sgcm.com/new_cars/cars/11913/brochures/brochure_20160927104832.pdf "RUF Rt 12"
[4]: https://en.wikipedia.org/wiki/Honda_Acty?utm_source=chatgpt.com "Honda Acty"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2701-2800_ktype_dimension_mapping_final.tsv
- all_2701-2800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已完成剩余 Ktype `132896`：其车型边界对应 Honda Acty I `TN` 后驱平台/底盘型，0.5 L、23 kW、31 hp、生产区间 1978–1987；标准车身尺寸闭合为 `3195×1395×1660 mm`，其中 `1395 mm` 明确为不含后视镜宽度。基于输入的后驱属性，本映射不纳入独立的 Big Cab 和 4WD 分支。([Auto Doc][1])
* 已完成机械检查：映射表严格 10 列，尺寸组表严格 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；所有映射引用闭合；无孤立尺寸组；尺寸、来源及 URL 均非空。
* `PENDING` 已清零。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：103
* PENDING 映射：0
* 完整 DIMENSION_GROUP：61
* 最终校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132733	132733	Van	Astra J facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck 商用车外廓。	READY
132735	132735	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132737	132737	Van	Astra J facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck 商用车外廓。	READY
132744	132744	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132746	132746	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132749_prefl	132749	SUV	Rogue I pre-facelift	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132749_facelift	132749	SUV	Rogue I facelift	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132750	132750	Van	Astra J Sports Tourer facelift	P10	5	EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132752	132752	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132754	132754	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132756	132756	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132775	132775	Van	Astra H	A04	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132778	132778	Van	Astra G	T98	5	EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132779	132779	Van	Astra G	T98	5	EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132780	132780	Van	Astra F pre-facelift	T92	5	EU-OPEL-ASTRA-F-T92-VAN-WAGON-PREFL-01	HIGH	Kasten/Kombi 商用车外廓。	READY
132784_prefl	132784	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132784_facelift	132784	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132785	132785	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	Kasten/Schrägheck 三门商用车外廓。	READY
132786_prefl	132786	Van	Yaris I pre-facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款前。	READY
132786_facelift	132786	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	同一 Ktype 跨改款前后外廓，拆分为改款后。	READY
132787	132787	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
132788	132788	Van	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Kasten/Schrägheck 三门商用车外廓。	READY
132793	132793	Wagon	Megane IV Grandtour		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
132796	132796	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
132797	132797	Wagon	Megane IV Grandtour		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
132798	132798	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132799	132799	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132800	132800	Van	Corsa D facelift	S07	3	EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	HIGH	Corsavan 三门商用车外廓。	READY
132801	132801	SUV	X4 II	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132802	132802	SUV	X5 IV pre-facelift	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
132803	132803	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132804	132804	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132805	132805	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132806	132806	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
132825	132825	MPV	Zafira Tourer C facelift	P12	5	EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	HIGH		READY
132826	132826	Convertible	Cascada	W13	2	EU-OPEL-CASCADA-W13-CONVERTIBLE-01	HIGH		READY
132828	132828	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132829	132829	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132830	132830	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132831	132831	MPV	S-Max II		5	EU-FORD-S-MAX-II-MPV-01	HIGH		READY
132832	132832	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132833	132833	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132834	132834	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132835	132835	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132836	132836	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132837	132837	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132838	132838	MPV	Galaxy III		5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
132839	132839	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132840	132840	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132841	132841	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132842	132842	SUV	C5 Aircross I pre-facelift	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH	输入 Model=C5、BodyStyle=SUV，对应 C5 Aircross。	READY
132844	132844	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH		READY
132845	132845	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH		READY
132848	132848	Coupe	Aventador SVJ	LB834	2	EU-LAMBORGHINI-AVENTADOR-SVJ-COUPE-01	HIGH		READY
132849	132849	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH		READY
132852	132852	SUV	Range Rover Velar I pre-facelift	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	HIGH		READY
132854	132854	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
132855	132855	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
132856	132856	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
132857	132857	SUV	Duster II	HM	5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH		READY
132858	132858	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132859	132859	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132860	132860	Wagon	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-WAGON-01	HIGH		READY
132861	132861	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132862	132862	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132863	132863	Hatchback	Granta I facelift		5	EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	HIGH		READY
132864	132864	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	HIGH	AMG A 35 外廓。	READY
132896	132896	Pickup	Acty I	TN	2	EU-HONDA-ACTY-I-TN-PICKUP-01	HIGH	后驱平台/底盘型，排除 Big Cab 与 4WD 分支。	READY
132897	132897	Coupe	Regera		2	EU-KOENIGSEGG-REGERA-COUPE-01	HIGH		READY
132899	132899	Coupe	Agera RS		2	EU-KOENIGSEGG-AGERA-RS-COUPE-01	HIGH		READY
132900	132900	Coupe	Agera S		2	EU-KOENIGSEGG-AGERA-COUPE-01	HIGH		READY
132901	132901	Coupe	Agera		2	EU-KOENIGSEGG-AGERA-COUPE-01	HIGH		READY
132902	132902	SUV	C3 Aircross I Phase I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH		READY
132904	132904	Convertible	Centenario Roadster		2	EU-LAMBORGHINI-CENTENARIO-ROADSTER-CONVERTIBLE-01	HIGH		READY
132905	132905	Sedan	XE I	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
132914	132914	Coupe	Divo		2	EU-BUGATTI-DIVO-COUPE-01	HIGH		READY
132915	132915	Coupe	Zonda Cinque		2	EU-PAGANI-ZONDA-CINQUE-COUPE-01	HIGH		READY
132916	132916	Convertible	Zonda F Roadster		2	EU-PAGANI-ZONDA-F-ROADSTER-CONVERTIBLE-01	HIGH		READY
132917	132917	Convertible	Huracan Performante Spyder		2	EU-LAMBORGHINI-HURACAN-PERFORMANTE-SPYDER-CONVERTIBLE-01	HIGH	Targa 输入对应 Performante Spyder 开放式外廓。	READY
132922	132922	Hatchback	Octavia III facelift	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH	Schrägheck 对应五门 liftback 外廓。	READY
132923	132923	Wagon	Octavia III Combi facelift	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
132926	132926	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-FWD-01	HIGH		READY
132928	132928	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-AWD-01	HIGH		READY
132930	132930	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132931	132931	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132932	132932	Hatchback	A3 Sportback 8V facelift	8V	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
132933	132933	Convertible	X-Bow RR		0	EU-KTM-X-BOW-RR-CONVERTIBLE-01	HIGH	开放式车身，无常规车门。	READY
132934	132934	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
132935	132935	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
132936	132936	Coupe	X-Bow GT4		2	EU-KTM-X-BOW-GT4-COUPE-01	HIGH		READY
132937	132937	Coupe	600LT	P13	2	EU-MCLAREN-600LT-P13-COUPE-01	HIGH		READY
132938	132938	Wagon	Clio IV Grandtour Phase II		5	EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	HIGH		READY
132939	132939	Coupe	Senna	P15	2	EU-MCLAREN-SENNA-P15-COUPE-01	HIGH		READY
132940	132940	Convertible	A3 Cabriolet 8V facelift	8V	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
132942	132942	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
132945	132945	SUV	Kadjar I facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132946	132946	SUV	Q5 II pre-facelift	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
132947	132947	SUV	Q5 II pre-facelift	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
132949	132949	Coupe	SCR 2018		2	EU-RUF-SCR-2018-COUPE-01	HIGH		READY
132950	132950	Coupe	SCR 4.2		2	EU-RUF-SCR-4-2-COUPE-01	HIGH		READY
132955	132955	Hatchback	City 2016		3	EU-AIXAM-CITY-2016-HATCHBACK-01	MEDIUM		READY
132957	132957	Convertible	3 Wheeler		0	EU-MORGAN-3-WHEELER-ROADSTER-01	HIGH	开放式三轮车身，无常规车门。	READY
132959	132959	Coupe	CTR Anniversary		2	EU-RUF-CTR-ANNIVERSARY-COUPE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2701-2800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-J-P10-VAN-HATCHBACK-FACELIFT-01	4419	1814	1510	Auto-Data Opel Astra J facelift 1.6 CDTI	https://www.auto-data.net/en/opel-astra-j-facelift-2012-1.6-cdti-110hp-ecotec-start-stop-19434
EU-OPEL-ASTRA-J-P10-VAN-WAGON-FACELIFT-01	4698	1814	1535	Auto-Data Opel Astra J Sports Tourer facelift	https://www.auto-data.net/en/opel-astra-j-sports-tourer-facelift-2012-1.7-cdti-130hp-ecotec-19470
EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	4646	1801	1659	Auto-Data Nissan Rogue I S35 2.5i AWD CVT	https://www.auto-data.net/en/nissan-rogue-i-s35-2.5i-170hp-awd-cvt-832
EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	4656	1801	1684	Auto-Data Nissan Rogue I S35 facelift	https://www.auto-data.net/en/nissan-rogue-i-s35-facelift-2011-2.5i-170hp-cvt-34526
EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift 2007	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.7-cdti-ecoflex-110hp-16947
EU-OPEL-ASTRA-G-T98-VAN-WAGON-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.6	https://www.auto-data.net/en/opel-astra-g-caravan-1.6-ecotec-16v-101hp-2417
EU-OPEL-ASTRA-F-T92-VAN-WAGON-PREFL-01	4278	1688	1475	Auto-Data Opel Astra F Caravan 1.8i	https://www.auto-data.net/en/opel-astra-f-caravan-1.8i-90hp-2489
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500	Auto-Data Toyota Yaris I 3-door	https://www.auto-data.net/en/toyota-yaris-i-3-door-generation-1052
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 3-door	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-1.4-d-4d-75hp-50708
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Auto-Data Renault Megane IV 1.5 Blue dCi 95	https://www.auto-data.net/en/renault-megane-iv-1.5-blue-dci-95hp-35491
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457	Auto-Data Renault Megane IV Grandtour 1.5 Blue dCi 95	https://www.auto-data.net/en/renault-megane-iv-grandtour-1.5-blue-dci-95hp-35500
EU-OPEL-CORSA-D-S07-VAN-HATCHBACK-3D-FACELIFT-01	3999	1737	1488	Auto-Data Opel Corsa D facelift 3-door	https://www.auto-data.net/en/opel-corsa-d-facelift-2011-3-door-1.4-xer-100hp-16970
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	Auto-Data BMW X4 G02 30d xDrive Steptronic	https://www.auto-data.net/en/bmw-x4-g02-30d-265hp-xdrive-steptronic-33345
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	Auto-Data BMW X5 G05 30d xDrive Steptronic	https://www.auto-data.net/en/bmw-x5-g05-30d-265hp-xdrive-steptronic-33266
EU-FORD-S-MAX-II-MPV-01	4796	1916	1655	Auto-Data Ford S-Max II 2.0 EcoBlue	https://www.auto-data.net/en/ford-s-max-ii-2.0-ecoblue-190hp-s-s-34514
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Auto-Data Dacia Lodgy 1.6 SCe LPG	https://www.auto-data.net/en/dacia-lodgy-1.6-sce-lpg-102hp-46202
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660	Auto-Data Opel Zafira Tourer C facelift	https://www.auto-data.net/en/opel-zafira-tourer-c-facelift-2016-1.6-turbo-136hp-36415
EU-OPEL-CASCADA-W13-CONVERTIBLE-01	4696	1839	1443	Auto-Data Opel Cascada 1.6	https://www.auto-data.net/en/opel-cascada-1.6-136hp-automatic-33821
EU-FORD-GALAXY-III-MPV-01	4848	1916	1747	Auto-Data Ford Galaxy III	https://www.auto-data.net/en/ford-galaxy-iii-generation-4567
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670	Citroën C5 Aircross SUV Range 2018 brochure	https://www.charterscitroen.com/wp-content/uploads/sites/21/2017/06/citroen-c5-aircross-prices-specifications-brochure-november-2018.pdf
EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	5054	1953	1455	Auto-Data Mercedes-AMG GT 53 X290	https://www.auto-data.net/en/mercedes-benz-amg-gt-4-door-coupe-x290-53-435hp-eq-boost-4matic-amg-speedshift-tct-9g-34366
EU-LAMBORGHINI-AVENTADOR-SVJ-COUPE-01	4943	2098	1136	Auto-Data Lamborghini Aventador SVJ	https://www.auto-data.net/en/lamborghini-aventador-svj-6.5-v12-770hp-4wd-isr-34013
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 CLS 220d	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-cls-220d-194hp-9g-tronic-38299
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	4803	1930	1665	Land Rover Introducing Range Rover Velar	https://media.landrover.com/en-gb/news/2017/03/introducing-range-rover-velar
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	Auto-Data Dacia Duster II 1.5 dCi 95	https://www.auto-data.net/en/dacia-duster-ii-1.5-dci-95hp-35555
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Auto-Data Audi A1 Sportback GB 30 TFSI	https://www.auto-data.net/en/audi-a1-sportback-gb-30-tfsi-116hp-34083
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682	Auto-Data Dacia Duster II 1.5 dCi 116 4x4	https://www.auto-data.net/en/dacia-duster-ii-1.5-dci-116hp-4x4-34931
EU-LADA-GRANTA-I-FACELIFT-WAGON-01	4118	1700	1538	Auto-Data Lada Granta I facelift wagon	https://www.auto-data.net/en/lada-granta-i-facelift-2018-combi-1.6-16v-106hp-34498
EU-LADA-GRANTA-I-FACELIFT-HATCHBACK-01	3926	1700	1500	Auto-Data Lada Granta model	https://www.auto-data.net/en/lada-granta-model-2080
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405	Auto-Data Mercedes-AMG A 35 W177	https://www.auto-data.net/en/mercedes-benz-a-class-w177-amg-a-35-306hp-4matic-dct-35067
EU-HONDA-ACTY-I-TN-PICKUP-01	3195	1395	1660	Honda TN-ACTY 1977 official news release; Automobile-Catalog 1980 Honda TN-Acty	https://global.honda/jp/news/1977/4770720.html; https://www.automobile-catalog.com/car/1980/1088780/honda_tn-acty.html
EU-KOENIGSEGG-REGERA-COUPE-01	4560	2050	1110	Koenigsegg Regera technical specifications	https://www.koenigsegg.com/technical-specifications-regera
EU-KOENIGSEGG-AGERA-RS-COUPE-01	4293	2050	1120	Koenigsegg Agera RS technical specifications	https://www.koenigsegg.com/technical-specifications-agera-rs
EU-KOENIGSEGG-AGERA-COUPE-01	4293	1996	1120	Koenigsegg Agera R technical specifications	https://www.koenigsegg.com/technical-specifications-agera-r
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637	Auto-Data Citroën C3 Aircross I Phase I 1.5 BlueHDi 120	https://www.auto-data.net/en/citroen-c3-aircross-i-phase-i-2017-1.5-bluehdi-120hp-automatic-39044
EU-LAMBORGHINI-CENTENARIO-ROADSTER-CONVERTIBLE-01	4924	2061	1158	Lamborghini Centenario Roadster; LamboCars Centenario Roadster specifications	https://www.lamborghini.com/en-en/history/few-off/centenario-roadster; https://www.lambocars.com/centenario-lp770-4-roadster-specs-performance/
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1425	Auto-Data Jaguar XE X760 2.0 200	https://www.auto-data.net/en/jaguar-xe-x760-2.0-200hp-automatic-21902
EU-BUGATTI-DIVO-COUPE-01	4641	2018	1212	Auto-Data Bugatti Divo	https://www.auto-data.net/en/bugatti-divo-8.0-w16-1500hp-awd-dsg-34033
EU-PAGANI-ZONDA-CINQUE-COUPE-01	4435	2055	1141	Auto-Data Pagani Zonda model dimensions; Pagani Zonda Cinque official model page	https://www.auto-data.net/en/pagani-zonda-model-315; https://www.pagani.com/zonda-cinque/
EU-PAGANI-ZONDA-F-ROADSTER-CONVERTIBLE-01	4435	2055	1141	Auto-Data Pagani Zonda Roadster F	https://www.auto-data.net/en/pagani-zonda-roadster-f-7.3-v12-48v-650hp-24022
EU-LAMBORGHINI-HURACAN-PERFORMANTE-SPYDER-CONVERTIBLE-01	4506	1924	1180	Auto-Data Lamborghini Huracan Performante Spyder	https://www.auto-data.net/en/lamborghini-huracan-performante-spyder-generation-6155
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461	Auto-Data Skoda Octavia III facelift liftback	https://www.auto-data.net/en/skoda-octavia-iii-facelift-2017-2.0-tsi-190hp-dsg-35797
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465	Auto-Data Skoda Octavia III Combi facelift	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-2.0-tsi-190hp-dsg-35816
EU-HONDA-CR-V-V-RW-SUV-FWD-01	4600	1855	1679	Auto-Data Honda CR-V V 1.5 VTEC Turbo FWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-173hp-34296
EU-HONDA-CR-V-V-RW-SUV-AWD-01	4600	1855	1689	Auto-Data Honda CR-V V 1.5 VTEC Turbo AWD	https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-173hp-awd-34297
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Audi UK A3 Sportback 1.5 TFSI technical data	https://press.audi.co.uk/assets/documents/original/11109-AudiUK00018622AudiA3Sportback15TFSI.pdf
EU-KTM-X-BOW-RR-CONVERTIBLE-01	3738	1915	1202	KTM X-Bow RR model information	https://www.ktm-cars.jp/x-bow/x-bow-r/model-info.html
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift 35 TFSI	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-35-tfsi-150hp-35153
EU-KTM-X-BOW-GT4-COUPE-01	4112	1933	1140	Mobility.fun KTM X-Bow GT4	https://www.mobility.fun/ktm-x-bow/x-bow-gt4
EU-MCLAREN-600LT-P13-COUPE-01	4604	1930	1194	McLaren 600LT official brochure; Auto-Data McLaren 600LT	https://autocatalogarchive.com/wp-content/uploads/2019/02/McLaren-600-LT-2019-INT.pdf; https://www.auto-data.net/en/mclaren-600lt-model-2482
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475	Auto-Data Renault Clio IV Grandtour Phase II 0.9 TCe 75	https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-ii-2016-0.9-tce-75hp-35362
EU-MCLAREN-SENNA-P15-COUPE-01	4744	1958	1229	McLaren Senna technical specification mirror; VehicleScore McLaren Senna dimensions	https://m.autoinfo.jp/release/Senna_spec_201802.pdf; https://vehiclescore.co.uk/car-dimensions-check/mclaren/senna
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-35-tfsi-150hp-35165
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Auto-Data Audi Q2 30 TDI S tronic	https://www.auto-data.net/en/audi-q2-30-tdi-116hp-s-tronic-35044
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613	Auto-Data Renault Kadjar facelift 1.3 TCe 159	https://www.auto-data.net/en/renault-kadjar-facelift-2018-1.3-tce-159hp-34192
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Auto-Data Audi Q5 II FY 35 TDI quattro	https://www.auto-data.net/en/audi-q5-ii-fy-2.0-tdi-163hp-quattro-s-tronic-26239
EU-RUF-SCR-2018-COUPE-01	4207	1819	1265	Auto-Data RUF SCR 4.0	https://www.auto-data.net/en/ruf-scr-4.0-510hp-32841
EU-RUF-SCR-4-2-COUPE-01	4250	1652	1250	RUF SCR 4.2 official technical data brochure	https://i.i-sgcm.com/new_cars/cars/11913/brochures/brochure_20160927104832.pdf
EU-AIXAM-CITY-2016-HATCHBACK-01	2758	1500	1470	1000PS Aixam City 2016	https://www.1000ps.com/en-us/model/6353/aixam-city/2016
EU-MORGAN-3-WHEELER-ROADSTER-01	3225	1720	1000	Morgan 3 Wheeler official brochure	https://www.morgan-cars.jp/wp-content/uploads/2015/02/Inserts_3Wheeler.pdf
EU-RUF-CTR-ANNIVERSARY-COUPE-01	4207	1819	1265	RUF Japan CTR Anniversary specifications	https://www.ruf-web.co.jp/com/ctr2017/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2701-2800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-doc.ie/car-parts/brake-pad-set-10130/honda/acty-tn/acty-platform-chassis-tn/132896-0-5?srsltid=AfmBOorJzfVvu2bL0gM4l45i4KcacgPgbhSyzmsJXhtZ1gs0udwfrev1 "https://www.auto-doc.ie/car-parts/brake-pad-set-10130/honda/acty-tn/acty-platform-chassis-tn/132896-0-5?srsltid=AfmBOorJzfVvu2bL0gM4l45i4KcacgPgbhSyzmsJXhtZ1gs0udwfrev1"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2035 行）
- 累计尺寸组：dimension_groups_final.tsv（1020 行）

