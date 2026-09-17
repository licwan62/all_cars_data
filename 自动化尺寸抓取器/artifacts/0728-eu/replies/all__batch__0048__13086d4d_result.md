# 任务：all 第 4701-4800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0048__13086d4d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4701-4800 行

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
all 第 4701-4800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-BMW-6-F13-COUPE-01	4894	1894	1369
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Porsche	911	3.8 Carrera 4S / 4 GTS	Coupe	Allrad	Benzin	300	408	Jun 2009	Dec 2012	2024-03-01	4846
Mercedes-benz	124	200 E	Stufenheck	Heckantrieb	Benzin	100	136	Oct 1992	Jun 1993	2024-03-01	4847
Mercedes-benz	124	220 E	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1992	Jun 1993	2024-03-01	4848
Mercedes-benz	124	280 E	Stufenheck	Heckantrieb	Benzin	145	197	Oct 1992	Jun 1993	2024-03-01	4849
Mercedes-benz	124	400 E 4.2	Stufenheck	Heckantrieb	Benzin	205	279	Oct 1992	Jun 1993	2024-03-01	4850
KIA	Cee'd	1.4 Cvvt	Kombi	Frontantrieb	Benzin	66	90	Jul 2009	Dec 2012	2024-03-01	4851
KIA	Cee'd	1.6 Cvvt	Kombi	Frontantrieb	Benzin	92	125	Jun 2009	Dec 2012	2024-03-01	4852
Fiat	Grande punto	1.4 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	57	78	Jul 2008	-	2024-03-01	4853
Porsche	911	3.6 GT2 RS	Coupe	Heckantrieb	Benzin	456	620	May 2010	Dec 2012	2024-03-01	4854
Ferrari	208/308	308 GTB	Coupe	Heckantrieb	Benzin	188	255	Sep 1975	Jun 1980	2024-03-01	4855
Ferrari	208/308	308 GTS	Coupe	Heckantrieb	Benzin	188	255	Sep 1977	Jun 1980	2024-03-01	4856
Ferrari	456 gt/gta	5.5	Coupe	Heckantrieb	Benzin	325	442	Jan 1993	Jun 2004	2024-03-01	4857
Ferrari	512 tr	4.9	Coupe	Heckantrieb	Benzin	315	428	Jan 1992	Oct 1994	2024-03-01	4858
Ferrari	512 m	4.9	Coupe	Heckantrieb	Benzin	324	440	Nov 1994	Aug 1996	2024-03-01	4859
Ferrari	Testarossa	4.9	Coupe	Heckantrieb	Benzin	287	390	May 1984	Dec 1991	2024-03-01	4860
Ferrari	F40	3	Coupe	Heckantrieb	Benzin	352	478	Feb 1988	Jun 1992	2024-03-01	4861
Ferrari	208/308	208 Turbo	Coupe	Heckantrieb	Benzin	162	220	Jun 1982	Oct 1989	2024-03-01	4862
Ferrari	Testarossa	5	Coupe	Heckantrieb	Benzin	272	370	Aug 1986	Oct 1991	2024-03-01	4863
Ferrari	400	4.8	Coupe	Heckantrieb	Benzin	232	315	May 1979	Mar 1985	2024-03-01	4864
Ferrari	Mondial	8	Coupe	Heckantrieb	Benzin	158	214	Jul 1980	Sep 1983	2024-03-01	4865
Ferrari	Mondial	8 Quattrovalvole	Coupe	Heckantrieb	Benzin	177	240	Oct 1982	Jul 1987	2024-03-01	4866
Ferrari	Mondial	8 Quattrovalvole	Cabriolet	Heckantrieb	Benzin	177	240	Mar 1984	Jul 1987	2024-03-01	4867
Ferrari	Mondial	3.2 Quattrovalvole	Coupe	Heckantrieb	Benzin	199	270	Oct 1985	Dec 1988	2024-03-01	4868
Ferrari	Mondial	3.2 Quattrovalvole	Cabriolet	Heckantrieb	Benzin	199	270	Sep 1985	Dec 1988	2024-03-01	4869
Ferrari	Mondial	3.4 T	Coupe	Heckantrieb	Benzin	221	300	Mar 1989	Dec 1993	2024-03-01	4870
Ferrari	Mondial	3.4 T	Cabriolet	Heckantrieb	Benzin	221	300	Jan 1989	Dec 1993	2024-03-01	4871
Ferrari	328 gtb	3.2	Coupe	Heckantrieb	Benzin	199	270	Sep 1985	Sep 1989	2024-03-01	4872
Ferrari	328 gts	3.2	Targa	Heckantrieb	Benzin	199	270	Sep 1985	Sep 1989	2024-03-01	4873
Porsche	911	3.8 Turbo	Cabriolet	Allrad	Benzin	368	500	Sep 2009	Dec 2012	2024-03-01	4874
KIA	Cee'd	1.4	Kombi	Frontantrieb	Benzin	77	105	Oct 2010	Dec 2012	2024-03-01	4875
Ferrari	Dino gt	206 GT	Coupe	Heckantrieb	Benzin	132	180	Feb 1969	Oct 1969	2024-03-01	4876
Ferrari	Dino gt	246 GT	Coupe	Heckantrieb	Benzin	143	195	Oct 1969	Oct 1973	2024-03-01	4877
Ferrari	Dino gts	246 GTS	Cabriolet	Heckantrieb	Benzin	143	195	Apr 1972	Oct 1973	2024-03-01	4878
Ferrari	365 gtb/4 daytona	4.4	Coupe	Heckantrieb	Benzin	259	352	Feb 1969	Dec 1974	2024-03-01	4879
Ferrari	365 gts/4 daytona	4.4	Cabriolet	Heckantrieb	Benzin	259	352	May 1971	Dec 1974	2024-03-01	4880
Ferrari	F355 berlinetta	3.5	Coupe	Heckantrieb	Benzin	280	380	May 1994	Mar 1999	2024-03-01	4881
Porsche	911	3.8 Carrera S / GTS	Cabriolet	Heckantrieb	Benzin	300	408	Jun 2009	Dec 2011	2024-03-01	4882
Ferrari	F355 spider	3.5	Cabriolet	Heckantrieb	Benzin	280	380	Jul 1995	Dec 2000	2024-03-01	4883
Ferrari	348 tb/gtb	3.4	Coupe	Heckantrieb	Benzin	221	300	Feb 1990	Apr 1994	2024-03-01	4884
Ferrari	348 ts/gts	3.4	Targa	Heckantrieb	Benzin	221	300	Aug 1990	Oct 1993	2024-03-01	4885
Ferrari	348 tb/gtb	3.4	Coupe	Heckantrieb	Benzin	235	320	Oct 1993	Apr 1994	2024-03-01	4886
Ferrari	348 ts/gts	3.4	Targa	Heckantrieb	Benzin	235	320	Oct 1993	Dec 1995	2024-03-01	4887
Ferrari	412	4.9	Coupe	Heckantrieb	Benzin	250	340	Apr 1985	Dec 1988	2024-03-01	4888
Ferrari	365 gt 2+2	4.4	Coupe	Heckantrieb	Benzin	235	320	Jun 1967	Apr 1971	2024-03-01	4889
Ferrari	512 bb	4.9	Coupe	Heckantrieb	Benzin	250	340	Aug 1976	Jun 1981	2024-03-01	4890
Ferrari	512 bb	I 4.9	Coupe	Heckantrieb	Benzin	237	322	Jul 1981	Aug 1984	2024-03-01	4891
Ferrari	208/308	308 GTB QV	Coupe	Heckantrieb	Benzin	177	240	Sep 1982	Jun 1985	2024-03-01	4892
Ferrari	208/308	308 GTS QV	Coupe	Heckantrieb	Benzin	177	240	Sep 1982	Jun 1985	2024-03-01	4893
MG	Mgb	1.8	Cabriolet	Heckantrieb	Benzin	70	95	May 1962	Dec 1980	2024-03-01	4894
MG	Mgb	1.8	Cabriolet	Heckantrieb	Benzin	68	92	May 1962	Dec 1980	2024-03-01	4895
MG	Mgb gt	1.8	Coupe	Heckantrieb	Benzin	68	92	Jul 1965	Nov 1980	2024-03-01	4896
MG	Mgb gt	1.8	Coupe	Heckantrieb	Benzin	70	95	Jul 1965	Nov 1980	2024-03-01	4897
MG	Mgb gt	3.5	Coupe	Heckantrieb	Benzin	101	137	Oct 1972	Dec 1977	2024-03-01	4898
MG	Mgr v8	3.9	Cabriolet	Heckantrieb	Benzin	140	190	Sep 1992	Dec 1995	2024-03-01	4899
MG	Midget	1.3	Cabriolet	Heckantrieb	Benzin	48	65	Jan 1967	Sep 1974	2024-03-01	4900
MG	Midget	1.5	Cabriolet	Heckantrieb	Benzin	49	66	Sep 1974	Dec 1979	2024-03-01	4901
Maserati	228	2.8 I	Coupe	Heckantrieb	Benzin	184	250	Dec 1986	Dec 1990	2024-03-01	4903
Maserati	Biturbo	420	Stufenheck	Heckantrieb	Benzin	133	180	Mar 1985	Dec 1986	2024-03-01	4904
Maserati	Biturbo	420 I	Stufenheck	Heckantrieb	Benzin	138	187	Jan 1987	Dec 1988	2024-03-01	4905
Maserati	Biturbo	430	Stufenheck	Heckantrieb	Benzin	182	247	Feb 1988	Dec 1994	2024-03-01	4906
Maserati	Biturbo	222	Coupe	Heckantrieb	Benzin	162	220	Jan 1989	Dec 1992	2024-03-01	4907
Maserati	Biturbo	2.24v	Coupe	Heckantrieb	Benzin	180	245	Mar 1989	Jun 1993	2024-03-01	4908
Maserati	Biturbo	4.24v	Stufenheck	Heckantrieb	Benzin	180	245	Apr 1990	Dec 1994	2024-03-01	4909
Maserati	Biturbo	425	Stufenheck	Heckantrieb	Benzin	140	190	Jun 1984	Aug 1987	2024-03-01	4911
Maserati	Biturbo	425	Stufenheck	Heckantrieb	Benzin	147	200	Jun 1984	Aug 1987	2024-03-01	4912
Maserati	Biturbo	222 SE	Coupe	Heckantrieb	Benzin	184	250	Jan 1988	Dec 1990	2024-03-01	4913
Maserati	Biturbo	222 E	Coupe	Heckantrieb	Benzin	182	247	Jan 1989	Oct 1989	2024-03-01	4914
Maserati	Biturbo	I	Coupe	Heckantrieb	Benzin	136	184	Jul 1985	Apr 1987	2024-03-01	4915
Maserati	Biturbo	S 2.0	Coupe	Heckantrieb	Benzin	151	205	Dec 1981	Feb 1987	2024-03-01	4916
Maserati	Biturbo	SI 2.0	Coupe	Heckantrieb	Benzin	151	205	Sep 1987	Dec 1988	2024-03-01	4917
Maserati	Biturbo	ES	Coupe	Heckantrieb	Benzin	147	200	Sep 1983	Dec 1986	2024-03-01	4918
Maserati	Biturbo	2	Cabriolet	Heckantrieb	Benzin	136	184	Jul 1985	Apr 1987	2024-03-01	4919
Maserati	Biturbo	2.8	Cabriolet	Heckantrieb	Benzin	165	224	Jan 1989	Dec 1994	2024-03-01	4920
Maserati	Bora	4.7	Coupe	Heckantrieb	Benzin	228	310	Jan 1971	May 1980	2024-03-01	4921
Maserati	Bora	5	Coupe	Heckantrieb	Benzin	235	320	Jul 1976	May 1980	2024-03-01	4922
Maserati	Ghibli	4.7	Coupe	Heckantrieb	Benzin	228	310	Jan 1967	Dec 1973	2024-03-01	4923
Maserati	Ghibli	5	Coupe	Heckantrieb	Benzin	247	335	Jan 1970	Dec 1973	2024-03-01	4924
Maserati	Ghibli	4.7	Cabriolet	Heckantrieb	Benzin	228	310	Jun 1968	Dec 1973	2024-03-01	4925
Maserati	Ghibli	4.9	Cabriolet	Heckantrieb	Benzin	247	335	Jun 1968	Dec 1973	2024-03-01	4926
Maserati	Indy	4.2	Coupe	Heckantrieb	Benzin	191	260	Apr 1969	Dec 1974	2024-03-01	4927
Maserati	Indy	4.7	Coupe	Heckantrieb	Benzin	213	290	Jan 1972	Dec 1974	2024-03-01	4928
Maserati	Indy	4.9	Coupe	Heckantrieb	Benzin	235	320	Jan 1972	Dec 1974	2024-03-01	4929
Maserati	Karif	2.8	Coupe	Heckantrieb	Benzin	165	225	Apr 1988	Jan 1991	2024-03-01	4930
Maserati	Karif	2.8	Coupe	Heckantrieb	Benzin	182	247	Apr 1988	Dec 1992	2024-03-01	4931
Maserati	Khamsin	4.9	Coupe	Heckantrieb	Benzin	235	320	Jan 1974	Dec 1982	2024-03-01	4932
Maserati	Kyalami	4.2	Coupe	Heckantrieb	Benzin	188	255	Apr 1976	Dec 1985	2024-03-01	4933
Maserati	Kyalami	4.9	Coupe	Heckantrieb	Benzin	206	280	Apr 1976	Dec 1985	2024-03-01	4934
Maserati	Merak	2	Coupe	Heckantrieb	Benzin	125	170	Jan 1976	Dec 1983	2024-03-01	4935
Maserati	Merak	3.0 SS	Coupe	Heckantrieb	Benzin	162	220	May 1975	Dec 1983	2024-03-01	4936
Maserati	Mexico	4.2	Coupe	Heckantrieb	Benzin	191	260	Jan 1967	Dec 1972	2024-03-01	4937
Maserati	Mexico	4.7	Coupe	Heckantrieb	Benzin	213	290	Jan 1967	Dec 1972	2024-03-01	4938
Maserati	Quattroporte iii	4.7	Stufenheck	Heckantrieb	Benzin	188	255	Jun 1979	Oct 1985	2024-03-01	4939
Maserati	Quattroporte iii	4.9	Stufenheck	Heckantrieb	Benzin	206	280	Aug 1979	Dec 1989	2024-03-01	4940
Maserati	Quattroporte iv	2.0 Biturbo	Stufenheck	Heckantrieb	Benzin	211	287	Mar 1994	Sep 1998	2024-03-01	4941
Maserati	Quattroporte iv	2.8 Biturbo	Stufenheck	Heckantrieb	Benzin	209	284	Mar 1994	Sep 1998	2024-03-01	4942
Maserati	Shamal	3.2	Coupe	Heckantrieb	Benzin	240	326	Dec 1989	Nov 1995	2024-03-01	4943
Maserati	Ghibli	2.0 24V Biturbo	Coupe	Heckantrieb	Benzin	225	306	May 1992	Dec 1997	2024-03-01	4944
BMW	6	633 CSI	Coupe	Heckantrieb	Benzin	145	197	Sep 1978	Aug 1984	2024-03-01	4945
Chrysler	Vision	3.5 TSI	Stufenheck	Frontantrieb	Benzin	155	211	Sep 1993	Dec 1997	2024-03-01	4946
BMW	Isetta	250	Coupe	Heckantrieb	Benzin	9	12	Jan 1956	Dec 1962	2024-03-01	4947


--- Round 1 / 首次发送 ---
## 更新点

* 闭合 Porsche 911 997.2 的宽体 GTS/4S Coupé、GT2 RS、Turbo Cabriolet、GTS Cabriolet 分支；Ktype `4846` 复用已有尺寸组，其余新建尺寸组。([automobile-catalog.com][1])
* Mercedes-Benz W124 普通轿车与 400 E 分开建组：普通车型高度为 `1428 mm`，400 E 官方高度为 `1431 mm`。([marsClassic][2])
* Kia Cee’d ED 改款旅行车的三个 Ktype 合并到同一 `4490 × 1790 × 1525 mm` 尺寸组；Fiat Grande Punto Natural Power 因 CNG 车型高度为 `1514 mm`，单独建组。([automobile-catalog.com][3])
* 闭合 Ferrari 308 GTB/GTS、208 GTB Turbo、Testarossa、512 TR、F512 M；GTB Coupé 与 GTS Targa 即使三维相同，仍按不同车身形式分组。([法拉利][4])
* Ferrari F40 暂不建组：Ferrari 官方历史页给出 `4358 × 1970 × 1124 mm`，多个常用规格资料给出 `4430 × 1980 × 1130 mm`，属于阻塞性尺寸冲突。([法拉利][5])

## 当前批次进度

* 输入记录：100
* READY 映射：21
* PENDING 映射：79
* 本轮新增尺寸组：13
* 本轮复用已有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4846	4846	Coupe	911 997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GTS-01	HIGH	Carrera 4S与4 GTS均落入997.2宽体双门外廓。	READY
4847	4847	Sedan	W124	124.019	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4848	4848	Sedan	W124	124.022	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4849	4849	Sedan	W124	124.028	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4850	4850	Sedan	W124	124.034	4	EU-MERCEDES-BENZ-124-W124-SEDAN-400E-01	HIGH	400 E对应独立V8轿车尺寸边界。	READY
4851	4851	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4852	4852	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4853	4853	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power五门CNG车身。	READY
4854	4854	Coupe	911 997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	HIGH	GT2 RS专属宽体及外部套件。	READY
4855	4855	Coupe	308 GTB		2	EU-FERRARI-308-GTB-COUPE-01	HIGH	308 GTB固定顶Berlinetta。	READY
4856	4856	Targa	308 GTS		2	EU-FERRARI-308-GTS-TARGA-01	HIGH	308 GTS可拆顶Targa车身。	READY
4858	4858	Coupe	512 TR	F110	2	EU-FERRARI-512-TR-COUPE-01	HIGH	512 TR独立改款外廓。	READY
4859	4859	Coupe	F512 M	F110	2	EU-FERRARI-F512-M-COUPE-01	HIGH	F512 M最终改款外廓。	READY
4860	4860	Coupe	Testarossa	F110	2	EU-FERRARI-TESTAROSSA-F110-COUPE-01	HIGH	初期欧洲规格Testarossa双门车身。	READY
4861	4861	Coupe	F40		2		LOW	候选为量产F40标准Berlinetta车身。	PENDING: Ferrari官方历史页与常用规格资料的量产车三维存在实质冲突
4862	4862	Coupe	208 GTB Turbo		2	EU-FERRARI-208-GTB-TURBO-COUPE-01	HIGH	208 GTB Turbo固定顶车身。	READY
4863	4863	Coupe	Testarossa	F110	2	EU-FERRARI-TESTAROSSA-F110-COUPE-01	HIGH	欧洲催化版仍为同一Testarossa外廓。	READY
4874	4874	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	HIGH	997.2 Turbo Cabriolet宽体敞篷外廓。	READY
4875	4875	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4882	4882	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	HIGH	300 kW对应997.2 Carrera GTS宽体敞篷车身。	READY
4892	4892	Coupe	308 GTB Quattrovalvole		2	EU-FERRARI-308-GTB-COUPE-01	HIGH	Quattrovalvole继续使用308 GTB固定顶外廓。	READY
4893	4893	Targa	308 GTS Quattrovalvole		2	EU-FERRARI-308-GTS-TARGA-01	HIGH	车型名GTS QV，按可拆顶车身纠正输入Coupe。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-124-W124-SEDAN-01	4740	1740	1428	Mercedes-Benz Public Archive 200 E (M 111 engine); Mercedes-Benz Public Archive 280 E	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-E-M-111-engine.xhtml?oid=5301; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-E.xhtml?oid=5288
EU-MERCEDES-BENZ-124-W124-SEDAN-400E-01	4740	1740	1431	Mercedes-Benz Public Archive 400 E	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/400-E.xhtml?oid=5291
EU-KIA-CEED-ED-WAGON-FACELIFT-01	4490	1790	1525	Automobile-Catalog 2010 Kia CeeD SW 1.4 EcoDynamics Vision; Automobile-Catalog 2010 Kia CeeD SW 1.6 EcoDynamics Mind	https://www.automobile-catalog.com/car/2010/1361405/kia_cee_d_sw_1_4_cvvt_vision_isg.html; https://www.automobile-catalog.com/car/2010/1362005/kia_cee_d_sw_1_6_cvvt_mind_isg.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514	Automobile-Catalog 2010 Fiat Grande Punto 1.4 Natural Power	https://www.automobile-catalog.com/car/2010/728705/fiat_grande_punto_1_4_natural_power_petrol.html
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285	Automobile-Catalog 2011 Porsche 911 GT2 RS	https://www.automobile-catalog.com/car/2011/2868635/porsche_911_gt2_rs.html
EU-FERRARI-308-GTB-COUPE-01	4230	1720	1120	Ferrari 308 GTB official historical specifications	https://www.ferrari.com/en-EN/auto/308-gtb
EU-FERRARI-308-GTS-TARGA-01	4230	1720	1120	Ferrari 308 GTS official historical specifications	https://www.ferrari.com/en-EN/auto/308-gts
EU-FERRARI-512-TR-COUPE-01	4480	1976	1135	Ferrari 512 TR official historical specifications; Automobile-Catalog 1993 Ferrari 512 TR	https://www.ferrari.com/en-EN/auto/512-tr; https://www.automobile-catalog.com/car/1993/706775/ferrari_512_tr.html
EU-FERRARI-F512-M-COUPE-01	4480	1976	1135	Ferrari F512 M official historical specifications	https://www.ferrari.com/en-EN/auto/f512-m
EU-FERRARI-TESTAROSSA-F110-COUPE-01	4485	1976	1130	Ferrari Testarossa official historical specifications; Automobile-Catalog 1984 Ferrari Testarossa	https://www.ferrari.com/en-EN/auto/testarossa; https://www.automobile-catalog.com/car/1984/2065880/ferrari_testarossa.html
EU-FERRARI-208-GTB-TURBO-COUPE-01	4230	1720	1120	Ferrari 208 GTB Turbo official historical specifications; Automobile-Catalog 1983 Ferrari 208 GTB Turbo	https://www.ferrari.com/en-EN/auto/208-gtb-turbo; https://www.automobile-catalog.com/car/1983/706220/ferrari_208_gtb_turbo.html
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300	Automobile-Catalog 2011 Porsche 911 Turbo Cabriolet	https://www.automobile-catalog.com/car/2011/2868545/porsche_911_turbo_cabriolet.html
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300	Automobile-Catalog 2011 Porsche 911 Carrera GTS Cabriolet	https://www.automobile-catalog.com/car/2011/2868680/porsche_911_carrera_gts_cabriolet.html
```

## 下一步优先处理

1. 先解决 F40 官方历史页与常见量产规格之间的口径冲突，避免错误建组。
2. 按同车系聚类闭合 Ferrari Mondial、328、Dino、Daytona、F355、348、BB 系列。
3. 再批量处理 Maserati Biturbo 家族及其 Coupé、Sedan、Cabriolet 不同轴距/车身分支。
4. 最后处理 MG、BMW Isetta、Chrysler Vision 等剩余独立车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2011/2868635/porsche_911_gt2_rs.html?utm_source=chatgpt.com "2011 Porsche 911 GT2 RS (man. 6) (model up to mid-year ..."
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-E-M-111-engine.xhtml?oid=5301&utm_source=chatgpt.com "200 E (M 111 engine)"
[3]: https://www.automobile-catalog.com/car/2010/1361405/kia_cee_d_sw_1_4_cvvt_vision_isg.html?utm_source=chatgpt.com "2010 Kia CeeD SW 1.4 EcoDynamics Vision (man. 5)"
[4]: https://www.ferrari.com/en-EN/auto/308-gtb?utm_source=chatgpt.com "Ferrari 308 GTB (1975)"
[5]: https://www.ferrari.com/en-EN/auto/f40?utm_source=chatgpt.com "Ferrari F40 (1987) - Ferrari.com"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 闭合 Ferrari 456 GT、400、Mondial、328、Dino、Daytona、F355、348、412、365 GT 2+2、512 BB/BBi 一批高复用车身；同外廓 Ktype 直接关联已在本轮首次确认的尺寸组。
* Mondial 按普通 Mondial（8 / Quattrovalvole / 3.2）与 Mondial t 分组；Coupe 与 Cabriolet 分开建组。
* 348、328、Daytona、512 BB 系列按固定顶 / Targa / Spider 等物理车身分开建组；同组三维一致时仅复用组，不重复抓取。
* 当前仍有 Ferrari F40、MG、Maserati、BMW 6 E24、Chrysler Vision、BMW Isetta 等未闭合，批次尚未完成。

当前批次进度

* READY 映射：47
* PENDING 映射：53
* 已确认尺寸组：33
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4857	4857	Coupe	456 GT		2	EU-FERRARI-456-GT-COUPE-01	HIGH	456 GT 双门2+2固定顶外廓。	READY
4864	4864	Coupe	400		2	EU-FERRARI-400-COUPE-01	HIGH	400 系列双门2+2固定顶外廓。	READY
4865	4865	Coupe	Mondial 8		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4866	4866	Coupe	Mondial Quattrovalvole		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4867	4867	Convertible	Mondial Quattrovalvole		2	EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	HIGH	Mondial 普通敞篷外廓。	READY
4868	4868	Coupe	Mondial 3.2		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4869	4869	Convertible	Mondial 3.2		2	EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	HIGH	Mondial 普通敞篷外廓。	READY
4870	4870	Coupe	Mondial t		2	EU-FERRARI-MONDIAL-T-COUPE-01	HIGH	Mondial t 固定顶外廓。	READY
4871	4871	Convertible	Mondial t		2	EU-FERRARI-MONDIAL-T-CONVERTIBLE-01	HIGH	Mondial t 敞篷外廓。	READY
4872	4872	Coupe	328 GTB		2	EU-FERRARI-328-GTB-COUPE-01	HIGH	328 GTB 固定顶外廓。	READY
4873	4873	Targa	328 GTS		2	EU-FERRARI-328-GTS-TARGA-01	HIGH	328 GTS 可拆顶外廓。	READY
4876	4876	Coupe	Dino 206 GT		2	EU-FERRARI-DINO-206-GT-COUPE-01	HIGH	Dino 206 GT 固定顶外廓。	READY
4877	4877	Coupe	Dino 246 GT		2	EU-FERRARI-DINO-246-GT-COUPE-01	HIGH	Dino 246 GT 固定顶外廓。	READY
4878	4878	Convertible	Dino 246 GTS		2	EU-FERRARI-DINO-246-GTS-CONVERTIBLE-01	HIGH	Dino 246 GTS 开放式车身外廓。	READY
4879	4879	Coupe	365 GTB/4 Daytona		2	EU-FERRARI-365-GTB4-DAYTONA-COUPE-01	HIGH	Daytona 固定顶外廓。	READY
4880	4880	Convertible	365 GTS/4 Daytona		2	EU-FERRARI-365-GTS4-DAYTONA-CONVERTIBLE-01	HIGH	Daytona Spider 开放式车身外廓。	READY
4881	4881	Coupe	F355 Berlinetta		2	EU-FERRARI-F355-BERLINETTA-COUPE-01	HIGH	F355 Berlinetta 固定顶外廓。	READY
4883	4883	Convertible	F355 Spider		2	EU-FERRARI-F355-SPIDER-CONVERTIBLE-01	HIGH	F355 Spider 开放式车身外廓。	READY
4884	4884	Coupe	348 tb/gtb		2	EU-FERRARI-348-TB-GTB-COUPE-01	HIGH	348 固定顶外廓。	READY
4885	4885	Targa	348 ts/gts		2	EU-FERRARI-348-TS-GTS-TARGA-01	HIGH	348 Targa 外廓。	READY
4886	4886	Coupe	348 tb/gtb		2	EU-FERRARI-348-TB-GTB-COUPE-01	HIGH	后期348固定顶仍为同一外廓。	READY
4887	4887	Targa	348 ts/gts		2	EU-FERRARI-348-TS-GTS-TARGA-01	HIGH	后期348 Targa 仍为同一外廓。	READY
4888	4888	Coupe	412		2	EU-FERRARI-412-COUPE-01	HIGH	412 双门2+2固定顶外廓。	READY
4889	4889	Coupe	365 GT 2+2		2	EU-FERRARI-365-GT-2PLUS2-COUPE-01	HIGH	365 GT 2+2 固定顶外廓。	READY
4890	4890	Coupe	512 BB		2	EU-FERRARI-512-BB-BBI-COUPE-01	HIGH	512 Berlinetta Boxer 固定顶外廓。	READY
4891	4891	Coupe	512 BBi		2	EU-FERRARI-512-BB-BBI-COUPE-01	HIGH	512 BBi 与512 BB外廓复用同组。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FERRARI-456-GT-COUPE-01	4763	1920	1300	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/456-gt
EU-FERRARI-400-COUPE-01	4818	1798	1314	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/400
EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	4580	1790	1250	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-8
EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	4580	1790	1270	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-cabriolet
EU-FERRARI-MONDIAL-T-COUPE-01	4540	1790	1235	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-t
EU-FERRARI-MONDIAL-T-CONVERTIBLE-01	4540	1790	1280	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-t-cabriolet
EU-FERRARI-328-GTB-COUPE-01	4255	1730	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/328-gtb
EU-FERRARI-328-GTS-TARGA-01	4255	1730	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/328-gts
EU-FERRARI-DINO-206-GT-COUPE-01	4235	1700	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-206-gt
EU-FERRARI-DINO-246-GT-COUPE-01	4235	1700	1115	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-246-gt
EU-FERRARI-DINO-246-GTS-CONVERTIBLE-01	4235	1700	1135	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-246-gts
EU-FERRARI-365-GTB4-DAYTONA-COUPE-01	4425	1760	1245	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gtb4
EU-FERRARI-365-GTS4-DAYTONA-CONVERTIBLE-01	4425	1760	1245	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gts4
EU-FERRARI-F355-BERLINETTA-COUPE-01	4250	1900	1171	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/f355-berlinetta
EU-FERRARI-F355-SPIDER-CONVERTIBLE-01	4250	1900	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/f355-spider
EU-FERRARI-348-TB-GTB-COUPE-01	4230	1894	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/348-tb
EU-FERRARI-348-TS-GTS-TARGA-01	4230	1894	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/348-ts
EU-FERRARI-412-COUPE-01	4818	1798	1314	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/412
EU-FERRARI-365-GT-2PLUS2-COUPE-01	4970	1770	1340	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gt-2-plus-2
EU-FERRARI-512-BB-BBI-COUPE-01	4400	1830	1120	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/512-bb
```

下一步优先处理

1. 先闭合 Ferrari F40 的冲突尺寸，决定是否可入组。
2. 批量处理 MG（MGB、MGB GT、MGR V8、Midget）并优先复用同车身组。
3. 批量处理 Maserati Biturbo 家族与 Quattroporte / Ghibli / Indy / Bora / Merak 等独立车身。
4. 最后处理 BMW 6 E24、BMW Isetta、Chrysler Vision 等剩余独立车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 MG RV8、Midget 1.3 与 Midget 1.5；跨保险杠阶段的 MGB、MGB GT 暂不合并。([汽车目录][1])
* 闭合 29 个 Maserati Ktype，覆盖 Biturbo 早期车身、228、Bora、Indy、Karif、Khamsin、Kyalami、Merak、Quattroporte IV 和 Shamal。([汽车目录][2])
* BMW 633 CSI 复用已有 E24 早期尺寸组，不重复输出尺寸组。
* Chrysler Vision 按 1993–1994 与 1995–1997 高度差异拆成两个派生映射；BMW Isetta 250 按早期短车身与后期加长车身拆分。([汽车目录][3])

## 当前批次进度

* READY 输入 Ktype：82
* READY 映射行：84
* PENDING 输入 Ktype：18
* 已确认尺寸组：56
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4899	4899	Convertible	RV8		2	EU-MG-RV8-CONVERTIBLE-01	HIGH	RV8双门敞篷外廓。	READY
4900	4900	Convertible	Midget Mk III		2	EU-MG-MIDGET-MK3-CONVERTIBLE-01	HIGH	1275车型对应Mk III敞篷外廓。	READY
4901	4901	Convertible	Midget 1500		2	EU-MG-MIDGET-1500-CONVERTIBLE-01	HIGH	1500车型对应后期敞篷外廓。	READY
4903	4903	Coupe	228		2	EU-MASERATI-228-COUPE-01	HIGH	228长轴距双门外廓。	READY
4904	4904	Sedan	Biturbo 420		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4905	4905	Sedan	Biturbo 420 i		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4907	4907	Coupe	Biturbo 222		2	EU-MASERATI-BITURBO-222-COUPE-01	HIGH	222双门改款外廓。	READY
4911	4911	Sedan	Biturbo 425		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4912	4912	Sedan	Biturbo 425		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4913	4913	Coupe	Biturbo 222 SE		2	EU-MASERATI-BITURBO-222-SE-COUPE-01	HIGH	222 SE专属外部套件外廓。	READY
4914	4914	Coupe	Biturbo 222 E		2	EU-MASERATI-BITURBO-222-COUPE-01	HIGH	222 E双门改款外廓。	READY
4915	4915	Coupe	Biturbo i		2	EU-MASERATI-BITURBO-I-COUPE-01	HIGH	第二系列Biturbo i双门外廓。	READY
4916	4916	Coupe	Biturbo S		2	EU-MASERATI-BITURBO-S-ES-COUPE-01	HIGH	早期Biturbo S双门外廓。	READY
4917	4917	Coupe	Biturbo Si		2	EU-MASERATI-BITURBO-SI-COUPE-01	HIGH	Biturbo Si低车身外廓。	READY
4918	4918	Coupe	Biturbo ES		2	EU-MASERATI-BITURBO-S-ES-COUPE-01	MEDIUM	ES对应早期Biturbo双门外廓。	READY
4919	4919	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	短轴距Spyder敞篷外廓。	READY
4920	4920	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	2.8车型继续使用短轴距Spyder外廓。	READY
4921	4921	Coupe	Bora	AM117	2	EU-MASERATI-BORA-AM117-COUPE-01	HIGH	AM117中置双门外廓。	READY
4922	4922	Coupe	Bora	AM117	2	EU-MASERATI-BORA-AM117-COUPE-01	HIGH	5.0车型使用同一AM117外廓。	READY
4927	4927	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	AM116双门四座外廓。	READY
4928	4928	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	4.7车型使用同一AM116外廓。	READY
4929	4929	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	4.9车型使用同一AM116外廓。	READY
4930	4930	Coupe	Karif		2	EU-MASERATI-KARIF-COUPE-01	HIGH	Karif短轴距固定顶外廓。	READY
4931	4931	Coupe	Karif		2	EU-MASERATI-KARIF-COUPE-01	HIGH	功率差异不改变Karif外廓。	READY
4932	4932	Coupe	Khamsin	AM120	2	EU-MASERATI-KHAMSIN-AM120-COUPE-01	HIGH	欧洲规格AM120双门外廓。	READY
4933	4933	Coupe	Kyalami	AM129	2	EU-MASERATI-KYALAMI-AM129-COUPE-01	HIGH	AM129双门四座外廓。	READY
4934	4934	Coupe	Kyalami	AM129	2	EU-MASERATI-KYALAMI-AM129-COUPE-01	HIGH	4.9车型使用同一AM129外廓。	READY
4935	4935	Coupe	Merak	AM122	2	EU-MASERATI-MERAK-AM122-COUPE-01	HIGH	AM122中置双门外廓。	READY
4936	4936	Coupe	Merak SS	AM122	2	EU-MASERATI-MERAK-AM122-COUPE-01	HIGH	Merak SS使用同一AM122车身边界。	READY
4941	4941	Sedan	Quattroporte IV		4	EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	HIGH	第四代四门轿车外廓。	READY
4942	4942	Sedan	Quattroporte IV		4	EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	HIGH	2.8车型使用同一第四代轿车外廓。	READY
4943	4943	Coupe	Shamal		2	EU-MASERATI-SHAMAL-COUPE-01	HIGH	Shamal宽体双门外廓。	READY
4945	4945	Coupe	6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH	1978至1984年早期E24外廓。	READY
4946_early	4946	Sedan	Vision LH	LH	4	EU-CHRYSLER-VISION-LH-SEDAN-EARLY-01	HIGH	1993至1994车型高度分支。	READY
4946_late	4946	Sedan	Vision LH	LH	4	EU-CHRYSLER-VISION-LH-SEDAN-LATE-01	HIGH	1995至1997车型高度分支。	READY
4947_early	4947	Coupe	Isetta 250 early		1	EU-BMW-ISETTA-250-COUPE-EARLY-01	HIGH	早期短车身Isetta 250。	READY
4947_late	4947	Coupe	Isetta 250 second series		1	EU-BMW-ISETTA-250-COUPE-LATE-01	HIGH	第二系列加长车身Isetta 250。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MG-RV8-CONVERTIBLE-01	4010	1694	1320	Automobile-Catalog 1994 MG RV8	https://www.automobile-catalog.com/car/1994/1701830/mg_rv8.html
EU-MG-MIDGET-MK3-CONVERTIBLE-01	3496	1394	1235	Automobile-Catalog 1967 MG Midget Mk III	https://www.automobile-catalog.com/car/1967/1698575/mg_midget_mk_iii_low_compr.html
EU-MG-MIDGET-1500-CONVERTIBLE-01	3581	1411	1226	Automobile-Catalog 1975 MG Midget 1500	https://www.automobile-catalog.com/car/1975/1698740/mg_midget_1500.html
EU-MASERATI-228-COUPE-01	4460	1865	1330	Automobile-Catalog 1989 Maserati 228	https://www.automobile-catalog.com/car/1989/1445750/maserati_228.html
EU-MASERATI-BITURBO-420-425-SEDAN-01	4400	1730	1360	Automobile-Catalog Maserati 420; Automobile-Catalog Maserati 420 i; Automobile-Catalog Maserati Biturbo 425	https://www.automobile-catalog.com/car/1986/1445435/maserati_420.html; https://www.automobile-catalog.com/car/1987/1445570/maserati_420_i.html; https://www.automobile-catalog.com/car/1984/1445330/maserati_biturbo_425.html
EU-MASERATI-BITURBO-222-COUPE-01	4153	1714	1255	Automobile-Catalog Maserati 222; Automobile-Catalog Maserati 222 E	https://www.automobile-catalog.com/car/1988/1445855/maserati_222.html; https://www.automobile-catalog.com/car/1990/2606465/maserati_222_e.html
EU-MASERATI-BITURBO-222-SE-COUPE-01	4201	1714	1305	Automobile-Catalog 1990 Maserati 222 SE	https://www.automobile-catalog.com/car/1990/1446065/maserati_222_se.html
EU-MASERATI-BITURBO-I-COUPE-01	4155	1714	1305	Automobile-Catalog 1986 Maserati Biturbo i	https://www.automobile-catalog.com/car/1986/1445525/maserati_biturbo_i.html
EU-MASERATI-BITURBO-S-ES-COUPE-01	4153	1714	1305	Automobile-Catalog 1984 Maserati Biturbo S	https://www.automobile-catalog.com/car/1984/1445255/maserati_biturbo_s.html
EU-MASERATI-BITURBO-SI-COUPE-01	4153	1714	1255	Automobile-Catalog 1988 Maserati Biturbo Si	https://www.automobile-catalog.com/car/1988/1445375/maserati_biturbo_si.html
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog 1987 Maserati Biturbo Spyder	https://www.automobile-catalog.com/car/1987/1445300/maserati_biturbo_spyder.html
EU-MASERATI-BORA-AM117-COUPE-01	4335	1768	1134	Automobile-Catalog 1972 Maserati Bora	https://www.automobile-catalog.com/car/1972/1444640/maserati_bora.html
EU-MASERATI-INDY-AM116-COUPE-01	4740	1760	1220	Automobile-Catalog 1969 Maserati Indy 4200	https://www.automobile-catalog.com/car/1969/1444460/maserati_indy_4200.html
EU-MASERATI-KARIF-COUPE-01	4043	1714	1285	Automobile-Catalog 1989 Maserati Karif	https://www.automobile-catalog.com/car/1989/1445930/maserati_karif.html
EU-MASERATI-KHAMSIN-AM120-COUPE-01	4400	1804	1168	Automobile-Catalog 1977 Maserati Khamsin	https://www.automobile-catalog.com/car/1977/1444715/maserati_khamsin.html
EU-MASERATI-KYALAMI-AM129-COUPE-01	4580	1850	1270	Automobile-Catalog 1976 Maserati Kyalami 4200	https://www.automobile-catalog.com/car/1976/1445015/maserati_kyalami_4200.html
EU-MASERATI-MERAK-AM122-COUPE-01	4335	1760	1134	Automobile-Catalog 1978 Maserati Merak 2000	https://www.automobile-catalog.com/car/1978/1444910/maserati_merak_2000.html
EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	4550	1810	1380	Automobile-Catalog 1994 Maserati Quattroporte 2.8	https://www.automobile-catalog.com/car/1994/1446830/maserati_quattroporte_2_8.html
EU-MASERATI-SHAMAL-COUPE-01	4100	1850	1300	Automobile-Catalog 1994 Maserati Shamal	https://www.automobile-catalog.com/car/1994/1446500/maserati_shamal.html
EU-CHRYSLER-VISION-LH-SEDAN-EARLY-01	5121	1890	1417	Automobile-Catalog 1993 Eagle Vision TSi	https://www.automobile-catalog.com/car/1993/702080/eagle_vision_tsi.html
EU-CHRYSLER-VISION-LH-SEDAN-LATE-01	5121	1890	1430	Automobile-Catalog 1995 Eagle Vision TSi	https://www.automobile-catalog.com/car/1995/702260/eagle_vision_tsi.html
EU-BMW-ISETTA-250-COUPE-EARLY-01	2285	1380	1340	BMW Group PressClub 50 years of the BMW Isetta	https://www.press.bmwgroup.com/canada/article/attachment/T0023581EN/43468
EU-BMW-ISETTA-250-COUPE-LATE-01	2355	1380	1340	Automobile-Catalog 1962 BMW Isetta 250 second series	https://www.automobile-catalog.com/car/1962/1449050/bmw_isetta_250_2__serie.html
```

## 下一步优先处理

1. 拆分 MGB、MGB GT 与 MGB GT V8 的镀铬保险杠、橡胶保险杠物理分支。
2. 解决 Maserati 430、2.24v、4.24v、Quattroporte III 和 Ghibli II 跨改款高度变化。
3. 闭合经典 Ghibli Coupé/Spyder、Mexico 的来源冲突。
4. 最后解决 Ferrari F40 官方历史尺寸与常用量产规格冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1994/1701845/mg_rv8.html?utm_source=chatgpt.com "1994 MG RV8 (man. 5) (model since April 1994 for Japan ) car ..."
[2]: https://www.automobile-catalog.com/car/1989/1445750/maserati_228.html?utm_source=chatgpt.com "1989 Maserati 228 (man. 5) (model for Europe ) car ..."
[3]: https://www.automobile-catalog.com/car/1993/702080/eagle_vision_tsi.html?utm_source=chatgpt.com "1993 Eagle Vision TSi (aut. 4) (model since mid-year 1992 ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 剩余 18 个 PENDING 已全部闭合。
* F40 按来源优先级采用 Ferrari 官方量产公路版尺寸 `4358 × 1970 × 1124 mm`，Ferrari 官方历史页与官方认证二手车页面数据一致。([法拉利][1])
* MGB、MGB GT 与 MGB GT V8 已按镀铬保险杠和橡胶保险杠的物理外廓拆分。([汽车目录][2])
* Maserati 430、2.24v、4.24v 已按前后期尺寸变化拆分；经典 Ghibli、Mexico、Quattroporte III 与 Ghibli II 已闭合。([汽车目录][3])
* 已完成机械检查：表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，尺寸和来源字段非空。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：110
* PENDING：0
* DIMENSION_GROUP：76
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4846	4846	Coupe	911 997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GTS-01	HIGH	Carrera 4S与4 GTS均落入997.2宽体双门外廓。	READY
4847	4847	Sedan	W124	124.019	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4848	4848	Sedan	W124	124.022	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4849	4849	Sedan	W124	124.028	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	HIGH	标准轴距W124四门轿车。	READY
4850	4850	Sedan	W124	124.034	4	EU-MERCEDES-BENZ-124-W124-SEDAN-400E-01	HIGH	400 E对应独立V8轿车尺寸边界。	READY
4851	4851	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4852	4852	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4853	4853	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power五门CNG车身。	READY
4854	4854	Coupe	911 997.2	997	2	EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	HIGH	GT2 RS专属宽体及外部套件。	READY
4855	4855	Coupe	308 GTB		2	EU-FERRARI-308-GTB-COUPE-01	HIGH	308 GTB固定顶Berlinetta。	READY
4856	4856	Targa	308 GTS		2	EU-FERRARI-308-GTS-TARGA-01	HIGH	308 GTS可拆顶Targa车身。	READY
4857	4857	Coupe	456 GT		2	EU-FERRARI-456-GT-COUPE-01	HIGH	456 GT 双门2+2固定顶外廓。	READY
4858	4858	Coupe	512 TR	F110	2	EU-FERRARI-512-TR-COUPE-01	HIGH	512 TR独立改款外廓。	READY
4859	4859	Coupe	F512 M	F110	2	EU-FERRARI-F512-M-COUPE-01	HIGH	F512 M最终改款外廓。	READY
4860	4860	Coupe	Testarossa	F110	2	EU-FERRARI-TESTAROSSA-F110-COUPE-01	HIGH	初期欧洲规格Testarossa双门车身。	READY
4861	4861	Coupe	F40	F120	2	EU-FERRARI-F40-F120-COUPE-01	HIGH	量产公路版F40双门Berlinetta外廓。	READY
4862	4862	Coupe	208 GTB Turbo		2	EU-FERRARI-208-GTB-TURBO-COUPE-01	HIGH	208 GTB Turbo固定顶车身。	READY
4863	4863	Coupe	Testarossa	F110	2	EU-FERRARI-TESTAROSSA-F110-COUPE-01	HIGH	欧洲催化版仍为同一Testarossa外廓。	READY
4864	4864	Coupe	400		2	EU-FERRARI-400-COUPE-01	HIGH	400 系列双门2+2固定顶外廓。	READY
4865	4865	Coupe	Mondial 8		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4866	4866	Coupe	Mondial Quattrovalvole		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4867	4867	Convertible	Mondial Quattrovalvole		2	EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	HIGH	Mondial 普通敞篷外廓。	READY
4868	4868	Coupe	Mondial 3.2		2	EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	HIGH	Mondial 普通固定顶外廓。	READY
4869	4869	Convertible	Mondial 3.2		2	EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	HIGH	Mondial 普通敞篷外廓。	READY
4870	4870	Coupe	Mondial t		2	EU-FERRARI-MONDIAL-T-COUPE-01	HIGH	Mondial t 固定顶外廓。	READY
4871	4871	Convertible	Mondial t		2	EU-FERRARI-MONDIAL-T-CONVERTIBLE-01	HIGH	Mondial t 敞篷外廓。	READY
4872	4872	Coupe	328 GTB		2	EU-FERRARI-328-GTB-COUPE-01	HIGH	328 GTB 固定顶外廓。	READY
4873	4873	Targa	328 GTS		2	EU-FERRARI-328-GTS-TARGA-01	HIGH	328 GTS 可拆顶外廓。	READY
4874	4874	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	HIGH	997.2 Turbo Cabriolet宽体敞篷外廓。	READY
4875	4875	Wagon	Cee'd ED facelift	ED	5	EU-KIA-CEED-ED-WAGON-FACELIFT-01	HIGH	改款cee'd SW五门旅行车。	READY
4876	4876	Coupe	Dino 206 GT		2	EU-FERRARI-DINO-206-GT-COUPE-01	HIGH	Dino 206 GT 固定顶外廓。	READY
4877	4877	Coupe	Dino 246 GT		2	EU-FERRARI-DINO-246-GT-COUPE-01	HIGH	Dino 246 GT 固定顶外廓。	READY
4878	4878	Convertible	Dino 246 GTS		2	EU-FERRARI-DINO-246-GTS-CONVERTIBLE-01	HIGH	Dino 246 GTS 开放式车身外廓。	READY
4879	4879	Coupe	365 GTB/4 Daytona		2	EU-FERRARI-365-GTB4-DAYTONA-COUPE-01	HIGH	Daytona 固定顶外廓。	READY
4880	4880	Convertible	365 GTS/4 Daytona		2	EU-FERRARI-365-GTS4-DAYTONA-CONVERTIBLE-01	HIGH	Daytona Spider 开放式车身外廓。	READY
4881	4881	Coupe	F355 Berlinetta		2	EU-FERRARI-F355-BERLINETTA-COUPE-01	HIGH	F355 Berlinetta 固定顶外廓。	READY
4882	4882	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	HIGH	300 kW对应997.2 Carrera GTS宽体敞篷车身。	READY
4883	4883	Convertible	F355 Spider		2	EU-FERRARI-F355-SPIDER-CONVERTIBLE-01	HIGH	F355 Spider 开放式车身外廓。	READY
4884	4884	Coupe	348 tb/gtb		2	EU-FERRARI-348-TB-GTB-COUPE-01	HIGH	348 固定顶外廓。	READY
4885	4885	Targa	348 ts/gts		2	EU-FERRARI-348-TS-GTS-TARGA-01	HIGH	348 Targa 外廓。	READY
4886	4886	Coupe	348 tb/gtb		2	EU-FERRARI-348-TB-GTB-COUPE-01	HIGH	后期348固定顶仍为同一外廓。	READY
4887	4887	Targa	348 ts/gts		2	EU-FERRARI-348-TS-GTS-TARGA-01	HIGH	后期348 Targa 仍为同一外廓。	READY
4888	4888	Coupe	412		2	EU-FERRARI-412-COUPE-01	HIGH	412 双门2+2固定顶外廓。	READY
4889	4889	Coupe	365 GT 2+2		2	EU-FERRARI-365-GT-2PLUS2-COUPE-01	HIGH	365 GT 2+2 固定顶外廓。	READY
4890	4890	Coupe	512 BB		2	EU-FERRARI-512-BB-BBI-COUPE-01	HIGH	512 Berlinetta Boxer 固定顶外廓。	READY
4891	4891	Coupe	512 BBi		2	EU-FERRARI-512-BB-BBI-COUPE-01	HIGH	512 BBi 与512 BB外廓复用同组。	READY
4892	4892	Coupe	308 GTB Quattrovalvole		2	EU-FERRARI-308-GTB-COUPE-01	HIGH	Quattrovalvole继续使用308 GTB固定顶外廓。	READY
4893	4893	Targa	308 GTS Quattrovalvole		2	EU-FERRARI-308-GTS-TARGA-01	HIGH	车型名GTS QV，按可拆顶车身纠正输入Coupe。	READY
4894_chrome	4894	Convertible	MGB Mk I-III		2	EU-MG-MGB-ROADSTER-CHROME-01	HIGH	镀铬保险杠Roadster外廓。	READY
4894_rubber	4894	Convertible	MGB Mk IV		2	EU-MG-MGB-ROADSTER-RUBBER-01	HIGH	橡胶保险杠Roadster外廓。	READY
4895_chrome	4895	Convertible	MGB Mk I-III		2	EU-MG-MGB-ROADSTER-CHROME-01	HIGH	镀铬保险杠Roadster外廓。	READY
4895_rubber	4895	Convertible	MGB Mk IV		2	EU-MG-MGB-ROADSTER-RUBBER-01	HIGH	橡胶保险杠Roadster外廓。	READY
4896_chrome	4896	Coupe	MGB GT Mk I-III		3	EU-MG-MGB-GT-CHROME-01	HIGH	镀铬保险杠三门GT外廓。	READY
4896_rubber	4896	Coupe	MGB GT Mk IV		3	EU-MG-MGB-GT-RUBBER-01	HIGH	橡胶保险杠三门GT外廓。	READY
4897_chrome	4897	Coupe	MGB GT Mk I-III		3	EU-MG-MGB-GT-CHROME-01	HIGH	镀铬保险杠三门GT外廓。	READY
4897_rubber	4897	Coupe	MGB GT Mk IV		3	EU-MG-MGB-GT-RUBBER-01	HIGH	橡胶保险杠三门GT外廓。	READY
4898_chrome	4898	Coupe	MGB GT V8 chrome		3	EU-MG-MGB-GT-V8-CHROME-01	HIGH	镀铬保险杠GT V8外廓。	READY
4898_rubber	4898	Coupe	MGB GT V8 rubber		3	EU-MG-MGB-GT-V8-RUBBER-01	HIGH	橡胶保险杠GT V8外廓。	READY
4899	4899	Convertible	RV8		2	EU-MG-RV8-CONVERTIBLE-01	HIGH	RV8双门敞篷外廓。	READY
4900	4900	Convertible	Midget Mk III		2	EU-MG-MIDGET-MK3-CONVERTIBLE-01	HIGH	1275车型对应Mk III敞篷外廓。	READY
4901	4901	Convertible	Midget 1500		2	EU-MG-MIDGET-1500-CONVERTIBLE-01	HIGH	1500车型对应后期敞篷外廓。	READY
4903	4903	Coupe	228		2	EU-MASERATI-228-COUPE-01	HIGH	228长轴距双门外廓。	READY
4904	4904	Sedan	Biturbo 420		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4905	4905	Sedan	Biturbo 420 i		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4906_early	4906	Sedan	Biturbo 430 early		4	EU-MASERATI-BITURBO-430-SEDAN-EARLY-01	HIGH	430早期车身高度分支。	READY
4906_late	4906	Sedan	Biturbo 430 late		4	EU-MASERATI-BITURBO-430-SEDAN-LATE-01	HIGH	430后期车身高度分支。	READY
4907	4907	Coupe	Biturbo 222		2	EU-MASERATI-BITURBO-222-COUPE-01	HIGH	222双门改款外廓。	READY
4908_early	4908	Coupe	Biturbo 2.24v		2	EU-MASERATI-BITURBO-2-24V-COUPE-EARLY-01	HIGH	2.24v初期外廓。	READY
4908_late	4908	Coupe	Biturbo 2.24v II		2	EU-MASERATI-BITURBO-2-24V-COUPE-LATE-01	HIGH	2.24v II改款外廓。	READY
4909_early	4909	Sedan	Biturbo 4.24v		4	EU-MASERATI-BITURBO-4-24V-SEDAN-EARLY-01	HIGH	4.24v初期外廓。	READY
4909_late	4909	Sedan	Biturbo 4.24v II		4	EU-MASERATI-BITURBO-4-24V-SEDAN-LATE-01	HIGH	4.24v II改款外廓。	READY
4911	4911	Sedan	Biturbo 425		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4912	4912	Sedan	Biturbo 425		4	EU-MASERATI-BITURBO-420-425-SEDAN-01	HIGH	Biturbo四门长轴距外廓。	READY
4913	4913	Coupe	Biturbo 222 SE		2	EU-MASERATI-BITURBO-222-SE-COUPE-01	HIGH	222 SE专属外部套件外廓。	READY
4914	4914	Coupe	Biturbo 222 E		2	EU-MASERATI-BITURBO-222-COUPE-01	HIGH	222 E双门改款外廓。	READY
4915	4915	Coupe	Biturbo i		2	EU-MASERATI-BITURBO-I-COUPE-01	HIGH	第二系列Biturbo i双门外廓。	READY
4916	4916	Coupe	Biturbo S		2	EU-MASERATI-BITURBO-S-ES-COUPE-01	HIGH	早期Biturbo S双门外廓。	READY
4917	4917	Coupe	Biturbo Si		2	EU-MASERATI-BITURBO-SI-COUPE-01	HIGH	Biturbo Si低车身外廓。	READY
4918	4918	Coupe	Biturbo ES		2	EU-MASERATI-BITURBO-S-ES-COUPE-01	MEDIUM	ES对应早期Biturbo双门外廓。	READY
4919	4919	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	短轴距Spyder敞篷外廓。	READY
4920	4920	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	2.8车型继续使用短轴距Spyder外廓。	READY
4921	4921	Coupe	Bora	AM117	2	EU-MASERATI-BORA-AM117-COUPE-01	HIGH	AM117中置双门外廓。	READY
4922	4922	Coupe	Bora	AM117	2	EU-MASERATI-BORA-AM117-COUPE-01	HIGH	5.0车型使用同一AM117外廓。	READY
4923	4923	Coupe	Ghibli I	AM115	2	EU-MASERATI-GHIBLI-AM115-COUPE-01	HIGH	4.7升Ghibli固定顶外廓。	READY
4924	4924	Coupe	Ghibli I SS	AM115/49	2	EU-MASERATI-GHIBLI-AM115-COUPE-01	HIGH	5.0升SS沿用同一固定顶外廓。	READY
4925	4925	Convertible	Ghibli I Spyder	AM115/S	2	EU-MASERATI-GHIBLI-AM115-CONVERTIBLE-01	HIGH	4.7升Ghibli Spyder外廓。	READY
4926	4926	Convertible	Ghibli I Spyder SS	AM115/S49	2	EU-MASERATI-GHIBLI-AM115-CONVERTIBLE-01	HIGH	4.9升Spyder SS沿用同一敞篷外廓。	READY
4927	4927	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	AM116双门四座外廓。	READY
4928	4928	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	4.7车型使用同一AM116外廓。	READY
4929	4929	Coupe	Indy	AM116	2	EU-MASERATI-INDY-AM116-COUPE-01	HIGH	4.9车型使用同一AM116外廓。	READY
4930	4930	Coupe	Karif		2	EU-MASERATI-KARIF-COUPE-01	HIGH	Karif短轴距固定顶外廓。	READY
4931	4931	Coupe	Karif		2	EU-MASERATI-KARIF-COUPE-01	HIGH	功率差异不改变Karif外廓。	READY
4932	4932	Coupe	Khamsin	AM120	2	EU-MASERATI-KHAMSIN-AM120-COUPE-01	HIGH	欧洲规格AM120双门外廓。	READY
4933	4933	Coupe	Kyalami	AM129	2	EU-MASERATI-KYALAMI-AM129-COUPE-01	HIGH	AM129双门四座外廓。	READY
4934	4934	Coupe	Kyalami	AM129	2	EU-MASERATI-KYALAMI-AM129-COUPE-01	HIGH	4.9车型使用同一AM129外廓。	READY
4935	4935	Coupe	Merak	AM122	2	EU-MASERATI-MERAK-AM122-COUPE-01	HIGH	AM122中置双门外廓。	READY
4936	4936	Coupe	Merak SS	AM122	2	EU-MASERATI-MERAK-AM122-COUPE-01	HIGH	Merak SS使用同一AM122车身边界。	READY
4937	4937	Coupe	Mexico	AM112	2	EU-MASERATI-MEXICO-AM112-COUPE-01	HIGH	Mexico 4.2双门四座外廓。	READY
4938	4938	Coupe	Mexico	AM112/1	2	EU-MASERATI-MEXICO-AM112-COUPE-01	HIGH	Mexico 4.7沿用同一外廓。	READY
4939	4939	Sedan	Quattroporte III	AM330	4	EU-MASERATI-QUATTROPORTE-III-AM330-SEDAN-01	HIGH	第三代标准四门轿车外廓。	READY
4940	4940	Sedan	Quattroporte III	AM330	4	EU-MASERATI-QUATTROPORTE-III-AM330-SEDAN-01	HIGH	4.9车型沿用同一AM330外廓。	READY
4941	4941	Sedan	Quattroporte IV		4	EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	HIGH	第四代四门轿车外廓。	READY
4942	4942	Sedan	Quattroporte IV		4	EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	HIGH	2.8车型使用同一第四代轿车外廓。	READY
4943	4943	Coupe	Shamal		2	EU-MASERATI-SHAMAL-COUPE-01	HIGH	Shamal宽体双门外廓。	READY
4944	4944	Coupe	Ghibli II	AM336	2	EU-MASERATI-GHIBLI-II-AM336-COUPE-01	HIGH	第二代Ghibli双门外廓。	READY
4945	4945	Coupe	6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH	1978至1984年早期E24外廓。	READY
4946_early	4946	Sedan	Vision LH	LH	4	EU-CHRYSLER-VISION-LH-SEDAN-EARLY-01	HIGH	1993至1994车型高度分支。	READY
4946_late	4946	Sedan	Vision LH	LH	4	EU-CHRYSLER-VISION-LH-SEDAN-LATE-01	HIGH	1995至1997车型高度分支。	READY
4947_early	4947	Coupe	Isetta 250 early		1	EU-BMW-ISETTA-250-COUPE-EARLY-01	HIGH	早期短车身Isetta 250。	READY
4947_late	4947	Coupe	Isetta 250 second series		1	EU-BMW-ISETTA-250-COUPE-LATE-01	HIGH	第二系列加长车身Isetta 250。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4701-4800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300	Automobile-Catalog 2011 Porsche 911 Carrera GTS Coupe	https://www.automobile-catalog.com/car/2011/2868650/porsche_911_carrera_gts_coupe.html
EU-MERCEDES-BENZ-124-W124-SEDAN-01	4740	1740	1428	Mercedes-Benz Public Archive 200 E (M 111 engine); Mercedes-Benz Public Archive 280 E	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-E-M-111-engine.xhtml?oid=5301; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-E.xhtml?oid=5288
EU-MERCEDES-BENZ-124-W124-SEDAN-400E-01	4740	1740	1431	Mercedes-Benz Public Archive 400 E	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/400-E.xhtml?oid=5291
EU-KIA-CEED-ED-WAGON-FACELIFT-01	4490	1790	1525	Automobile-Catalog 2010 Kia CeeD SW 1.4 EcoDynamics Vision; Automobile-Catalog 2010 Kia CeeD SW 1.6 EcoDynamics Mind	https://www.automobile-catalog.com/car/2010/1361405/kia_cee_d_sw_1_4_cvvt_vision_isg.html; https://www.automobile-catalog.com/car/2010/1362005/kia_cee_d_sw_1_6_cvvt_mind_isg.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514	Automobile-Catalog 2010 Fiat Grande Punto 1.4 Natural Power	https://www.automobile-catalog.com/car/2010/728705/fiat_grande_punto_1_4_natural_power_petrol.html
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285	Automobile-Catalog 2011 Porsche 911 GT2 RS	https://www.automobile-catalog.com/car/2011/2868635/porsche_911_gt2_rs.html
EU-FERRARI-308-GTB-COUPE-01	4230	1720	1120	Ferrari 308 GTB official historical specifications	https://www.ferrari.com/en-EN/auto/308-gtb
EU-FERRARI-308-GTS-TARGA-01	4230	1720	1120	Ferrari 308 GTS official historical specifications	https://www.ferrari.com/en-EN/auto/308-gts
EU-FERRARI-456-GT-COUPE-01	4763	1920	1300	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/456-gt
EU-FERRARI-512-TR-COUPE-01	4480	1976	1135	Ferrari 512 TR official historical specifications; Automobile-Catalog 1993 Ferrari 512 TR	https://www.ferrari.com/en-EN/auto/512-tr; https://www.automobile-catalog.com/car/1993/706775/ferrari_512_tr.html
EU-FERRARI-F512-M-COUPE-01	4480	1976	1135	Ferrari F512 M official historical specifications	https://www.ferrari.com/en-EN/auto/f512-m
EU-FERRARI-TESTAROSSA-F110-COUPE-01	4485	1976	1130	Ferrari Testarossa official historical specifications; Automobile-Catalog 1984 Ferrari Testarossa	https://www.ferrari.com/en-EN/auto/testarossa; https://www.automobile-catalog.com/car/1984/2065880/ferrari_testarossa.html
EU-FERRARI-F40-F120-COUPE-01	4358	1970	1124	Ferrari F40 official historical specifications	https://www.ferrari.com/en-EN/auto/f40
EU-FERRARI-208-GTB-TURBO-COUPE-01	4230	1720	1120	Ferrari 208 GTB Turbo official historical specifications; Automobile-Catalog 1983 Ferrari 208 GTB Turbo	https://www.ferrari.com/en-EN/auto/208-gtb-turbo; https://www.automobile-catalog.com/car/1983/706220/ferrari_208_gtb_turbo.html
EU-FERRARI-400-COUPE-01	4818	1798	1314	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/400
EU-FERRARI-MONDIAL-8-QV-3-2-COUPE-01	4580	1790	1250	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-8
EU-FERRARI-MONDIAL-8-QV-3-2-CONVERTIBLE-01	4580	1790	1270	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-cabriolet
EU-FERRARI-MONDIAL-T-COUPE-01	4540	1790	1235	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-t
EU-FERRARI-MONDIAL-T-CONVERTIBLE-01	4540	1790	1280	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/mondial-t-cabriolet
EU-FERRARI-328-GTB-COUPE-01	4255	1730	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/328-gtb
EU-FERRARI-328-GTS-TARGA-01	4255	1730	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/328-gts
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300	Automobile-Catalog 2011 Porsche 911 Turbo Cabriolet	https://www.automobile-catalog.com/car/2011/2868545/porsche_911_turbo_cabriolet.html
EU-FERRARI-DINO-206-GT-COUPE-01	4235	1700	1130	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-206-gt
EU-FERRARI-DINO-246-GT-COUPE-01	4235	1700	1115	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-246-gt
EU-FERRARI-DINO-246-GTS-CONVERTIBLE-01	4235	1700	1135	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/dino-246-gts
EU-FERRARI-365-GTB4-DAYTONA-COUPE-01	4425	1760	1245	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gtb4
EU-FERRARI-365-GTS4-DAYTONA-CONVERTIBLE-01	4425	1760	1245	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gts4
EU-FERRARI-F355-BERLINETTA-COUPE-01	4250	1900	1171	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/f355-berlinetta
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300	Automobile-Catalog 2011 Porsche 911 Carrera GTS Cabriolet	https://www.automobile-catalog.com/car/2011/2868680/porsche_911_carrera_gts_cabriolet.html
EU-FERRARI-F355-SPIDER-CONVERTIBLE-01	4250	1900	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/f355-spider
EU-FERRARI-348-TB-GTB-COUPE-01	4230	1894	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/348-tb
EU-FERRARI-348-TS-GTS-TARGA-01	4230	1894	1170	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/348-ts
EU-FERRARI-412-COUPE-01	4818	1798	1314	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/412
EU-FERRARI-365-GT-2PLUS2-COUPE-01	4970	1770	1340	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/365-gt-2-plus-2
EU-FERRARI-512-BB-BBI-COUPE-01	4400	1830	1120	Ferrari official historical specifications	https://www.ferrari.com/en-EN/auto/512-bb
EU-MG-MGB-ROADSTER-CHROME-01	3891	1521	1255	Automobile-Catalog 1968 MG MGB	https://www.automobile-catalog.com/car/1968/1696925/mg_mgb.html
EU-MG-MGB-ROADSTER-RUBBER-01	4020	1524	1295	Automobile-Catalog 1975 MG MGB	https://www.automobile-catalog.com/car/1975/1698170/mg_mgb.html
EU-MG-MGB-GT-CHROME-01	3891	1521	1255	Automobile-Catalog 1968 MG MGB GT	https://www.automobile-catalog.com/car/1968/1696865/mg_mgb_gt.html
EU-MG-MGB-GT-RUBBER-01	4020	1524	1295	Automobile-Catalog 1975 MG MGB GT	https://www.automobile-catalog.com/car/1975/1698200/mg_mgb_gt.html
EU-MG-MGB-GT-V8-CHROME-01	3931	1521	1267	Automobile-Catalog 1973 MG MGB GT V8	https://www.automobile-catalog.com/car/1973/1698050/mg_mgb_gt_v8.html
EU-MG-MGB-GT-V8-RUBBER-01	4020	1524	1295	Automobile-Catalog 1975 MG MGB GT V8	https://www.automobile-catalog.com/car/1975/1698125/mg_mgb_gt_v8.html
EU-MG-RV8-CONVERTIBLE-01	4010	1694	1320	Automobile-Catalog 1994 MG RV8	https://www.automobile-catalog.com/car/1994/1701830/mg_rv8.html
EU-MG-MIDGET-MK3-CONVERTIBLE-01	3496	1394	1235	Automobile-Catalog 1967 MG Midget Mk III	https://www.automobile-catalog.com/car/1967/1698575/mg_midget_mk_iii_low_compr.html
EU-MG-MIDGET-1500-CONVERTIBLE-01	3581	1411	1226	Automobile-Catalog 1975 MG Midget 1500	https://www.automobile-catalog.com/car/1975/1698740/mg_midget_1500.html
EU-MASERATI-228-COUPE-01	4460	1865	1330	Automobile-Catalog 1989 Maserati 228	https://www.automobile-catalog.com/car/1989/1445750/maserati_228.html
EU-MASERATI-BITURBO-420-425-SEDAN-01	4400	1730	1360	Automobile-Catalog Maserati 420; Automobile-Catalog Maserati 420 i; Automobile-Catalog Maserati Biturbo 425	https://www.automobile-catalog.com/car/1986/1445435/maserati_420.html; https://www.automobile-catalog.com/car/1987/1445570/maserati_420_i.html; https://www.automobile-catalog.com/car/1984/1445330/maserati_biturbo_425.html
EU-MASERATI-BITURBO-430-SEDAN-EARLY-01	4400	1730	1360	Automobile-Catalog 1988 Maserati 430	https://www.automobile-catalog.com/car/1988/1445660/maserati_430.html
EU-MASERATI-BITURBO-430-SEDAN-LATE-01	4400	1730	1370	Automobile-Catalog 1993 Maserati 430	https://www.automobile-catalog.com/car/1993/1445720/maserati_430.html
EU-MASERATI-BITURBO-222-COUPE-01	4153	1714	1255	Automobile-Catalog Maserati 222; Automobile-Catalog Maserati 222 E	https://www.automobile-catalog.com/car/1988/1445855/maserati_222.html; https://www.automobile-catalog.com/car/1990/2606465/maserati_222_e.html
EU-MASERATI-BITURBO-2-24V-COUPE-EARLY-01	4190	1714	1305	Automobile-Catalog 1989 Maserati 2.24V	https://www.automobile-catalog.com/car/1989/1445915/maserati_2_24v.html
EU-MASERATI-BITURBO-2-24V-COUPE-LATE-01	4195	1714	1305	Automobile-Catalog 1992 Maserati 2.24V II	https://www.automobile-catalog.com/car/1992/1446155/maserati_2_24v_ii.html
EU-MASERATI-BITURBO-4-24V-SEDAN-EARLY-01	4400	1730	1370	Automobile-Catalog 1990 Maserati 4.24V	https://www.automobile-catalog.com/car/1990/1446095/maserati_4_24v.html
EU-MASERATI-BITURBO-4-24V-SEDAN-LATE-01	4410	1730	1378	Automobile-Catalog 1992 Maserati 4.24V II	https://www.automobile-catalog.com/car/1992/2606450/maserati_4_24v_ii.html
EU-MASERATI-BITURBO-222-SE-COUPE-01	4201	1714	1305	Automobile-Catalog 1990 Maserati 222 SE	https://www.automobile-catalog.com/car/1990/1446065/maserati_222_se.html
EU-MASERATI-BITURBO-I-COUPE-01	4155	1714	1305	Automobile-Catalog 1986 Maserati Biturbo i	https://www.automobile-catalog.com/car/1986/1445525/maserati_biturbo_i.html
EU-MASERATI-BITURBO-S-ES-COUPE-01	4153	1714	1305	Automobile-Catalog 1984 Maserati Biturbo S	https://www.automobile-catalog.com/car/1984/1445255/maserati_biturbo_s.html
EU-MASERATI-BITURBO-SI-COUPE-01	4153	1714	1255	Automobile-Catalog 1988 Maserati Biturbo Si	https://www.automobile-catalog.com/car/1988/1445375/maserati_biturbo_si.html
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog 1987 Maserati Biturbo Spyder	https://www.automobile-catalog.com/car/1987/1445300/maserati_biturbo_spyder.html
EU-MASERATI-BORA-AM117-COUPE-01	4335	1768	1134	Automobile-Catalog 1972 Maserati Bora	https://www.automobile-catalog.com/car/1972/1444640/maserati_bora.html
EU-MASERATI-GHIBLI-AM115-COUPE-01	4590	1790	1160	Automobile-Catalog 1970 Maserati Ghibli	https://www.automobile-catalog.com/car/1970/1444160/maserati_ghibli.html
EU-MASERATI-GHIBLI-AM115-CONVERTIBLE-01	4590	1790	1160	Automobile-Catalog 1970 Maserati Ghibli Spider	https://www.automobile-catalog.com/car/1970/1444190/maserati_ghibli_spider.html
EU-MASERATI-INDY-AM116-COUPE-01	4740	1760	1220	Automobile-Catalog 1969 Maserati Indy 4200	https://www.automobile-catalog.com/car/1969/1444460/maserati_indy_4200.html
EU-MASERATI-KARIF-COUPE-01	4043	1714	1285	Automobile-Catalog 1989 Maserati Karif	https://www.automobile-catalog.com/car/1989/1445930/maserati_karif.html
EU-MASERATI-KHAMSIN-AM120-COUPE-01	4400	1804	1168	Automobile-Catalog 1977 Maserati Khamsin	https://www.automobile-catalog.com/car/1977/1444715/maserati_khamsin.html
EU-MASERATI-KYALAMI-AM129-COUPE-01	4580	1850	1270	Automobile-Catalog 1976 Maserati Kyalami 4200	https://www.automobile-catalog.com/car/1976/1445015/maserati_kyalami_4200.html
EU-MASERATI-MERAK-AM122-COUPE-01	4335	1760	1134	Automobile-Catalog 1978 Maserati Merak 2000	https://www.automobile-catalog.com/car/1978/1444910/maserati_merak_2000.html
EU-MASERATI-MEXICO-AM112-COUPE-01	4760	1730	1340	Automobile-Catalog 1968 Maserati Mexico 4200	https://www.automobile-catalog.com/car/1968/1444025/maserati_mexico_4200.html
EU-MASERATI-QUATTROPORTE-III-AM330-SEDAN-01	4910	1890	1385	Automobile-Catalog 1980 Maserati Quattroporte 4900 manual	https://www.automobile-catalog.com/car/1980/1445135/maserati_quattroporte_4900_manual.html
EU-MASERATI-QUATTROPORTE-IV-SEDAN-01	4550	1810	1380	Automobile-Catalog 1994 Maserati Quattroporte 2.8	https://www.automobile-catalog.com/car/1994/1446830/maserati_quattroporte_2_8.html
EU-MASERATI-SHAMAL-COUPE-01	4100	1850	1300	Automobile-Catalog 1994 Maserati Shamal	https://www.automobile-catalog.com/car/1994/1446500/maserati_shamal.html
EU-MASERATI-GHIBLI-II-AM336-COUPE-01	4223	1775	1300	Automobile-Catalog 1994 Maserati Ghibli 2.0	https://www.automobile-catalog.com/car/1994/1446530/maserati_ghibli_2_0.html
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365	Automobile-Catalog 1979 BMW 633 CSi	https://www.automobile-catalog.com/car/1979/34565/bmw_633_csi.html
EU-CHRYSLER-VISION-LH-SEDAN-EARLY-01	5121	1890	1417	Automobile-Catalog 1993 Eagle Vision TSi	https://www.automobile-catalog.com/car/1993/702080/eagle_vision_tsi.html
EU-CHRYSLER-VISION-LH-SEDAN-LATE-01	5121	1890	1430	Automobile-Catalog 1995 Eagle Vision TSi	https://www.automobile-catalog.com/car/1995/702260/eagle_vision_tsi.html
EU-BMW-ISETTA-250-COUPE-EARLY-01	2285	1380	1340	BMW Group PressClub 50 years of the BMW Isetta	https://www.press.bmwgroup.com/canada/article/attachment/T0023581EN/43468
EU-BMW-ISETTA-250-COUPE-LATE-01	2355	1380	1340	Automobile-Catalog 1962 BMW Isetta 250 second series	https://www.automobile-catalog.com/car/1962/1449050/bmw_isetta_250_2__serie.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4701-4800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ferrari.com/en-EN/auto/f40?utm_source=chatgpt.com "Ferrari F40 (1987) - Ferrari.com"
[2]: https://www.automobile-catalog.com/car/1968/1696925/mg_mgb.html?utm_source=chatgpt.com "1968 MG MGB (man. 4) (model for North America ) car ..."
[3]: https://www.automobile-catalog.com/car/1988/1445660/maserati_430.html?utm_source=chatgpt.com "1988 Maserati 430 (man. 5) (model for Europe ) car ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4701-4800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4701-4800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6303 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1966 行）

