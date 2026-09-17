# 任务：all 第 2301-2400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0024__d390c9cc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2301-2400 行

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
all 第 2301-2400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4413	1830	1372
EU-ALFA-ROMEO-BRERA-COUPE-3D-01	4410	1830	1341
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391
EU-AUDI-A4-B7-CONVERTIBLE-02	4570	1780	1390
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453
EU-AUDI-A4-B7-WAGON-5D-02	4586	1772	1427
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474
EU-CITROEN-C8-I-MPV-01	4726	1854	1752
EU-CITROEN-C8-PHASE-I-MPV-5D-01	4727	1854	1752
EU-DAIHATSU-SIRION-M1-HATCHBACK-01	3675	1595	1450
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-BRAVO-II-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522
EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	4719	1863	1759
EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	4719	1863	1752
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430
EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	4435	1765	1465
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	4532	1827	1298
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	4640	1800	1720
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486
EU-PEUGEOT-807-MPV-01	4730	1850	1750
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
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	3600	1654	1470
EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	3699	1688	1470
EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	3602	1665	1470
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568
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

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	89	121	Sep 2005	Jun 2006	2024-03-01	26550
Seat	Altea	1.4 16V	Großraumlimousine	Frontantrieb	Benzin	63	86	May 2006	May 2011	2024-05-01	26551
Seat	Leon	1.4 16V	Schrägheck	Frontantrieb	Benzin	63	86	Jun 2006	Dec 2012	2024-03-01	26552
Audi	A4 b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	26553
Audi	A4 b7	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	26554
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	26555
Audi	A4 b7 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	26556
Seat	Toledo	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Jan 2006	May 2009	2024-03-01	26557
Seat	Toledo	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	147	200	Nov 2005	May 2009	2024-03-01	26558
VW	Jetta iii	2.5	Stufenheck	Frontantrieb	Benzin	110	150	Jan 2006	Oct 2010	2024-03-01	26559
Citroën	Berlingo	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Jul 2005	Dec 2011	2024-03-01	26560
Seat	Toledo	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Nov 2005	May 2009	2024-03-01	26561
Renault	Grand scénic ii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Sep 2005	Nov 2008	2024-03-01	26562
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	176	240	Nov 2007	Aug 2015	2024-03-01	26563
Mercedes-benz	Clc-Klasse	CLC 180 Kompressor	Coupe	Heckantrieb	Benzin	105	143	May 2008	Jun 2011	2024-03-01	26564
Mercedes-benz	Clc-Klasse	CLC 200 Kompressor	Coupe	Heckantrieb	Benzin	135	184	May 2008	Jun 2011	2024-03-01	26565
Mercedes-benz	Clc-Klasse	CLC 230	Coupe	Heckantrieb	Benzin	150	204	May 2008	Jun 2011	2024-03-01	26566
Mercedes-benz	Clc-Klasse	CLC 350	Coupe	Heckantrieb	Benzin	200	272	May 2008	Jun 2011	2024-03-01	26567
Mercedes-benz	Clc-Klasse	CLC 200 CDI	Coupe	Heckantrieb	Diesel	90	122	May 2008	Jun 2011	2024-03-01	26568
Mercedes-benz	Clc-Klasse	CLC 220 CDI	Coupe	Heckantrieb	Diesel	110	150	May 2008	Jun 2011	2024-03-01	26569
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	81	110	Feb 2008	Sep 2010	2024-03-01	26570
Mercedes-benz	C-Klasse	C 63 AMG	Stufenheck	Heckantrieb	Benzin	336	457	Feb 2008	Jan 2014	2024-03-01	26571
Mercedes-benz	C-Klasse	C 63 AMG	Kombi	Heckantrieb	Benzin	336	457	Feb 2008	Aug 2014	2024-03-01	26572
Mercedes-benz	M-Klasse	ML 500 4-matic	SUV	Allrad	Benzin	285	388	Dec 2007	Dec 2011	2024-03-01	26573
Mercedes-benz	Slr	5.4	Cabriolet	Heckantrieb	Benzin	460	626	Apr 2007	-	2024-03-01	26574
Mercedes-benz	S-Klasse	S 350 4-matic	Stufenheck	Allrad	Benzin	200	272	Feb 2008	Dec 2013	2024-03-01	26575
Mercedes-benz	Sl	350	Cabriolet	Heckantrieb	Benzin	232	316	Apr 2008	Jan 2012	2024-03-01	26576
Ford	Kuga i	2.0 Tdci	SUV	Frontantrieb	Diesel	100	136	Mar 2008	Nov 2012	2024-03-01	26577
Ford	Kuga i	2.0 Tdci 4X4	SUV	Allrad	Diesel	100	136	Mar 2008	Nov 2012	2024-03-01	26578
Mercedes-benz	Sl	63 AMG	Cabriolet	Heckantrieb	Benzin	386	525	Mar 2008	Jan 2012	2024-03-01	26579
Mercedes-benz	Sl	280	Cabriolet	Heckantrieb	Benzin	170	231	Mar 2008	Jan 2012	2024-03-01	26580
Audi	A3	1.4 Tfsi	Schrägheck	Frontantrieb	Benzin	92	125	Sep 2007	Aug 2012	2024-03-01	26581
Audi	A3	1.4 Tfsi	Schrägheck	Frontantrieb	Benzin	92	125	Sep 2007	Mar 2013	2024-03-01	26582
Mazda	2	1.4 Mzr-cd	Schrägheck	Frontantrieb	Diesel	50	68	Oct 2007	Dec 2010	2025-06-01	26583
Hyundai	I10 i	1.1	Schrägheck	Frontantrieb	Benzin	49	67	Jan 2008	Dec 2013	2024-03-01	26584
Hyundai	I10 i	1.1 Crdi	Schrägheck	Frontantrieb	Diesel	55	75	Jan 2008	Dec 2011	2024-03-01	26585
Mazda	3	2.0 Mzr-cd	Schrägheck	Frontantrieb	Diesel	105	143	Jul 2006	Jun 2009	2024-03-01	26586
Mazda	3	2.0 Mzr-cd	Stufenheck	Frontantrieb	Diesel	105	143	Dec 2006	Jun 2009	2024-03-01	26587
Honda	Civic viii hatchback	Type R	Schrägheck	Frontantrieb	Benzin	148	201	Sep 2006	Jan 2012	2024-03-01	26588
BMW	3	M3	Stufenheck	Heckantrieb	Benzin	309	420	Dec 2007	Oct 2011	2024-03-01	26589
BMW	3	M3	Cabriolet	Heckantrieb	Benzin	309	420	Mar 2008	Oct 2013	2024-03-01	26590
Saab	9-3	2.8 Turbo V6	Cabriolet	Frontantrieb	Benzin	188	256	Dec 2007	Feb 2015	2024-03-01	26591
Saab	9-3	2.8 Turbo V6	Stufenheck	Frontantrieb	Benzin	188	256	Dec 2007	Feb 2015	2024-03-01	26592
Saab	9-3	2.8 Turbo V6	Kombi	Frontantrieb	Benzin	188	256	Dec 2007	Feb 2015	2024-03-01	26593
Saab	9-3	1.9 Ttid	Stufenheck	Frontantrieb	Diesel	132	180	Dec 2007	Feb 2015	2024-03-01	26594
Saab	9-3	1.9 Ttid	Cabriolet	Frontantrieb	Diesel	132	180	Dec 2007	Feb 2015	2024-03-01	26595
Saab	9-3	1.9 Ttid	Kombi	Frontantrieb	Diesel	132	180	Dec 2007	Feb 2015	2024-03-01	26596
Mercedes-benz	E-Klasse	E 200 CDI	Kombi	Heckantrieb	Diesel	100	136	Apr 2006	Jul 2009	2024-03-01	26597
Smart	Fortwo cabrio	1.0 Brabus	Cabriolet	Heckantrieb	Benzin	72	98	Jan 2008	-	2024-03-01	26598
Alfa Romeo	Brera	3.2 JTS	Schrägheck	Frontantrieb	Benzin	191	260	Mar 2008	Jun 2010	2024-03-01	26599
Alfa Romeo	Spider	2.4 Jtdm	Cabriolet	Frontantrieb	Diesel	154	210	Mar 2008	Mar 2011	2024-03-01	26600
Alfa Romeo	Spider	3.2 JTS	Cabriolet	Frontantrieb	Benzin	191	260	Mar 2008	Mar 2011	2024-03-01	26601
Fiat	Bravo ii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	77	105	Sep 2007	Dec 2014	2024-03-01	26602
Fiat	Bravo ii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	88	120	Mar 2008	Dec 2014	2024-03-01	26603
Chevrolet	Aveo / kalos	1.4	Schrägheck	Frontantrieb	Benzin	74	101	Apr 2008	-	2024-03-01	26604
Chevrolet	Aveo / kalos	1.2	Schrägheck	Frontantrieb	Benzin	62	84	Apr 2008	-	2024-03-01	26605
Peugeot	308 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	128	174	Mar 2008	Oct 2014	2024-03-01	26606
VW	Passat cc b6	1.8 TSI	Coupe	Frontantrieb	Benzin	118	160	Jun 2008	Jan 2012	2024-03-01	26607
VW	Passat cc b6	3.6 FSI 4motion	Coupe	Allrad	Benzin	220	300	Feb 2008	Dec 2011	2024-03-01	26608
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Jun 2008	Jan 2012	2024-03-01	26609
Peugeot	308 sw i	1.4 16V	Kombi	Frontantrieb	Benzin	70	95	Sep 2007	Oct 2014	2024-03-01	26610
Peugeot	308 sw i	1.6 16V	Kombi	Frontantrieb	Benzin	88	120	Sep 2007	Oct 2014	2024-03-01	26611
Peugeot	308 sw i	1.6 16V	Kombi	Frontantrieb	Benzin	110	150	Sep 2007	Oct 2014	2024-03-01	26612
Peugeot	308 sw i	1.6 16V	Kombi	Frontantrieb	Benzin	128	174	Mar 2008	Oct 2014	2024-03-01	26613
Peugeot	308 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	66	90	Sep 2007	Oct 2014	2024-03-01	26614
Peugeot	308 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	80	109	Sep 2007	Oct 2014	2024-03-01	26615
Peugeot	308 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	100	136	Sep 2007	Dec 2012	2024-03-01	26616
Hyundai	H-1 cargo	2.5 Crdi	Kasten	Heckantrieb	Diesel	125	170	Feb 2008	-	2024-03-01	26617
Daihatsu	Sirion	1.3	Schrägheck	Frontantrieb	Benzin	67	91	Mar 2008	-	2024-03-01	26618
Daihatsu	Sirion	1.3 4WD	Schrägheck	Allrad	Benzin	67	91	Mar 2008	-	2024-03-01	26619
Daihatsu	Sirion	1.5	Schrägheck	Frontantrieb	Benzin	76	103	Mar 2008	-	2024-03-01	26620
Fiat	Panda	1.2 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	44	60	Jan 2007	Dec 2011	2024-03-01	26621
Fiat	Ulysse	2.2 D Multijet	Großraumlimousine	Frontantrieb	Diesel	125	170	Mar 2008	Jun 2011	2024-03-01	26622
Skoda	Octavia	2.0 TDI RS	Schrägheck	Frontantrieb	Diesel	125	170	Apr 2006	Feb 2013	2024-03-01	26623
Skoda	Octavia	2.0 TDI RS	Kombi	Frontantrieb	Diesel	125	170	Apr 2006	Feb 2013	2024-03-01	26624
Citroën	C2	1.6 HDI	Schrägheck	Frontantrieb	Diesel	80	109	Sep 2005	Dec 2009	2024-03-01	26625
Citroën	C8	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Jun 2006	Dec 2012	2024-03-01	26626
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	47	64	Jun 2005	Dec 2012	2026-05-01	26627
Renault	Modus / grand	1.2	Schrägheck	Frontantrieb	Benzin	58	78	Dec 2004	Dec 2013	2025-12-01	26628
Renault	Modus / grand	1.5 DCI	Schrägheck	Frontantrieb	Diesel	48	65	Dec 2004	Dec 2013	2025-12-01	26629
Peugeot	207/207+	1.4 16V	Schrägheck	Frontantrieb	Benzin	70	95	Jun 2007	Oct 2013	2024-03-01	26630
Peugeot	407	2.0 HDI	Coupe	Frontantrieb	Diesel	100	136	Oct 2005	-	2024-03-01	26631
Peugeot	807	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Jun 2006	Jun 2010	2024-03-01	26632
Mitsubishi	Outlander ii	2.2 Di-d 4WD	SUV	Allrad	Diesel	115	156	Aug 2007	Nov 2012	2024-03-01	26633
Mitsubishi	Grandis	2.0 Di-d	Großraumlimousine	Frontantrieb	Diesel	103	140	Feb 2007	Mar 2010	2024-03-01	26634
KIA	Pro cee'd	1.6	Schrägheck	Frontantrieb	Benzin	93	126	Feb 2008	Sep 2012	2024-03-01	26635
KIA	Cee'd	1.6	Kombi	Frontantrieb	Benzin	93	126	Sep 2007	Dec 2012	2024-03-01	26636
KIA	Cee'd	1.6	Schrägheck	Frontantrieb	Benzin	93	126	Feb 2008	Dec 2012	2024-03-01	26637
Lancia	Ypsilon	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	77	105	May 2007	Dec 2011	2024-03-01	26638
Mitsubishi	Lancer viii	EVO X	Stufenheck	Allrad	Benzin	217	295	Jun 2008	Dec 2015	2024-03-01	26643
Audi	A5	3.2 FSI Quattro	Coupe	Allrad	Benzin	195	265	Jun 2007	Mar 2012	2024-03-01	26644
Mitsubishi	Lancer viii sportback	1.8	Schrägheck	Frontantrieb	Benzin	105	143	Jun 2008	-	2024-03-01	26645
Mitsubishi	Lancer viii sportback	2.0 Di-d	Schrägheck	Frontantrieb	Diesel	103	140	Jun 2008	-	2024-03-01	26646
Mitsubishi	Lancer viii sportback	1.5	Schrägheck	Frontantrieb	Benzin	80	109	Jun 2008	-	2024-03-01	26647
Renault	Laguna iii	2.0 GT	Schrägheck	Frontantrieb	Benzin	150	204	Mar 2008	Dec 2015	2024-03-01	26648
Renault	Laguna iii	2.0 DCI GT	Schrägheck	Frontantrieb	Diesel	131	178	Mar 2008	Dec 2015	2024-03-01	26649
Renault	Laguna iii grandtour	2.0 GT	Kombi	Frontantrieb	Benzin	150	204	Mar 2008	Dec 2015	2024-03-01	26650
Renault	Laguna iii grandtour	2.0 DCI GT	Kombi	Frontantrieb	Diesel	131	178	Mar 2008	Dec 2015	2024-03-01	26651
Renault	Twingo	1.6 RS	Schrägheck	Frontantrieb	Benzin	98	133	May 2008	Sep 2014	2026-05-01	26652
Renault	Koleos i	2.0 DCI	SUV	Frontantrieb	Diesel	110	150	Sep 2008	-	2024-03-01	26653


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 100 个输入 Ktype 的映射占位覆盖，确认 81 条 READY 映射；因改款、门数和物理外廓拆分，共形成 116 条映射记录。
* 新闭合 BMW M3 E90/E93、Saab 9-3 改款轿车与旅行车、Smart Fortwo Brabus Cabrio、Mercedes-Benz E-Class S211 旅行版尺寸组。BMW M3 的改款前后尺寸一致，因此各自复用单一尺寸组。([汽车数据网][1])
* Saab 9-3 Sedan 与 Sport Combi 分别建组；Smart A451 Brabus Cabrio 和 S211 facelift Wagon 已闭合。([汽车数据网][2])
* Peugeot 308 SW、Ford Kuga、Mercedes-Benz CLC 等仍存在三维口径或物理分支冲突，未强行创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：81
* PENDING 映射：35
* 完全闭合 Ktype：65 / 100
* 当前批次引用的已确认尺寸组：65
* 本轮首次创建或因冲突新建的尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26550	26550	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	HIGH		READY
26551_prefl	26551	MPV	Altea I pre-facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26551_facelift	26551	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26552_prefl	26552	Hatchback	Leon II pre-facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26552_facelift	26552	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26553	26553	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26554	26554	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26555	26555	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
26556	26556	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
26557	26557	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26558	26558	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26559	26559	Sedan	Jetta V	1K2	4	EU-VOLKSWAGEN-JETTA-V-SEDAN-4D-01	HIGH	输入“Jetta iii”对应欧洲第五代Jetta轿车外廓。	READY
26560	26560	Kasten/Großraumlimousine	Berlingo I M59	M59			LOW	输入同时覆盖厢式与乘用车身，物理分支尚未闭合。	PENDING: 需确认Kasten与MPV物理分支及对应尺寸组
26561	26561	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26562_prefl	26562	MPV	Grand Scenic II Phase I	R84	5	EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	HIGH	同一Ktype跨Phase I/II且车长变化，拆分Phase I外廓。	READY
26562_facelift	26562	MPV	Grand Scenic II Phase II	R84	5	EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	同一Ktype跨Phase I/II且车长变化，拆分Phase II外廓。	READY
26563_prefl	26563	SUV	Q7 I pre-facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26563_facelift	26563	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26564	26564	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26565	26565	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26566	26566	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26567	26567	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26568	26568	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26569	26569	Coupe	CLC-Class	C203	3		MEDIUM	同一CLC三门车身；可靠来源车长存在冲突。	PENDING: 可靠来源车长冲突尚未解决
26570	26570	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
26571	26571	Sedan	C-Class W204 AMG	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-AMG-SEDAN-4D-01	HIGH	W204四门AMG轿车外廓。	READY
26572	26572	Wagon	C-Class S204 AMG	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-AMG-WAGON-5D-01	HIGH	S204五门AMG旅行车外廓。	READY
26573_prefl	26573	SUV	M-Class W164 pre-facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	HIGH	同一Ktype跨改款且长高变化，拆分改款前外廓。	READY
26573_facelift	26573	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH	同一Ktype跨改款且长高变化，拆分改款后外廓。	READY
26574	26574	Convertible	SLR McLaren R199 Roadster	R199	2	EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	HIGH	R199双门Roadster外廓。	READY
26575_prefl	26575	Sedan	S-Class W221 pre-facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-01	HIGH	同一Ktype跨2009改款且三维变化，拆分改款前外廓。	READY
26575_facelift	26575	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2009改款且三维变化，拆分改款后外廓。	READY
26576	26576	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26577	26577	SUV	Kuga I	C394	5		MEDIUM	前驱与四驱不单独分组；可靠来源高度口径冲突。	PENDING: 外部高度来源冲突尚未解决
26578	26578	SUV	Kuga I	C394	5		MEDIUM	前驱与四驱不单独分组；可靠来源高度口径冲突。	PENDING: 外部高度来源冲突尚未解决
26579	26579	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26580	26580	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26581_3dr_prefl	26581	Hatchback	A3 II pre-facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	三门Ktype跨改款，拆分改款前外廓。	READY
26581_3dr_facelift	26581	Hatchback	A3 II facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	三门Ktype跨改款，拆分改款后外廓。	READY
26582_5dr_prefl	26582	Hatchback	A3 II Sportback pre-facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	五门Sportback Ktype跨改款，拆分改款前外廓。	READY
26582_5dr_facelift	26582	Hatchback	A3 II Sportback facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	五门Sportback Ktype跨改款，拆分改款后外廓。	READY
26583	26583	Hatchback	Mazda2 II pre-facelift	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	HIGH		READY
26584_prefl	26584	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26584_facelift	26584	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26585	26585	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH		READY
26586	26586	Hatchback	Mazda3 I facelift	BK	5	EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	HIGH		READY
26587	26587	Sedan	Mazda3 I facelift	BK	4	EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	HIGH		READY
26588	26588	Hatchback	Civic Type R FN2	FN2	3	EU-HONDA-CIVIC-TYPE-R-FN2-HATCHBACK-3D-01	HIGH	FN2三门Type R宽体外廓，不复用普通Civic五门组。	READY
26589	26589	Sedan	M3 E90	E90	4	EU-BMW-M3-E90-SEDAN-4D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26590	26590	Convertible	M3 E93	E93	2	EU-BMW-M3-E93-CONVERTIBLE-2D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26591	26591	Convertible	9-3 II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH		READY
26592	26592	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	2007改款四门轿车外廓。	READY
26593	26593	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	2007改款五门Sport Combi外廓。	READY
26594	26594	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	2007改款四门轿车外廓。	READY
26595	26595	Convertible	9-3 II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH		READY
26596	26596	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	2007改款五门Sport Combi外廓。	READY
26597	26597	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-5D-01	HIGH	S211改款五门旅行车外廓。	READY
26598	26598	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-A451-CONVERTIBLE-2D-BRABUS-01	HIGH	A451双门Brabus敞篷外廓。	READY
26599	26599	Coupe	Brera 939	939	3	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	输入Schrägheck按Brera三门双门轿跑物理车身标准化为Coupe。	READY
26600	26600	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
26601	26601	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
26602	26602	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
26603	26603	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
26604	26604	Hatchback	Aveo T250/T255				LOW	Ktype门数及改款边界尚未确认。	PENDING: 需确认3门/5门及改款外廓分支
26605	26605	Hatchback	Aveo T250/T255				LOW	Ktype门数及改款边界尚未确认。	PENDING: 需确认3门/5门及改款外廓分支
26606	26606	Hatchback	308 I		5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
26607	26607	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26608	26608	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26609	26609	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26610	26610	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26611	26611	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26612	26612	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26613	26613	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26614	26614	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26615	26615	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26616	26616	Wagon	308 SW I	T7	5		MEDIUM	同一SW车身；可靠来源高度存在冲突。	PENDING: 外部高度来源冲突尚未解决
26617	26617	Van	H-1 II Cargo	TQ			LOW	货运车身的轴距与车顶分支尚未闭合。	PENDING: 需确认Cargo轴距与车顶外廓
26618	26618	Hatchback	Sirion II	M3	5		MEDIUM	前驱与四驱通常同外廓，当前尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26619	26619	Hatchback	Sirion II	M3	5		MEDIUM	前驱与四驱通常同外廓，当前尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26620	26620	Hatchback	Sirion II	M3	5		MEDIUM	同代五门外廓，当前尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26621	26621	Hatchback	Panda II	169	5		MEDIUM	Natural Power版本外部高度需独立核对。	PENDING: Natural Power外廓尺寸尚未闭合
26622	26622	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	HIGH		READY
26623_prefl	26623	Hatchback	Octavia II RS pre-facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	HIGH	同一Ktype跨改款，拆分RS改款前外廓。	READY
26623_facelift	26623	Hatchback	Octavia II RS facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	HIGH	同一Ktype跨改款，拆分RS改款后外廓。	READY
26624_prefl	26624	Wagon	Octavia II RS pre-facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	HIGH	同一Ktype跨改款，拆分RS改款前外廓。	READY
26624_facelift	26624	Wagon	Octavia II RS facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	HIGH	同一Ktype跨改款，拆分RS改款后外廓。	READY
26625	26625	Hatchback	C2 I	JM	3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
26626	26626	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH		READY
26627_3dr_prefl	26627	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入未区分门数且跨改款；保留已确认三门改款前分支。	READY
26627_3dr_facelift	26627	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数且跨改款；保留已确认三门改款后分支。	READY
26627_5dr_prefl	26627	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入未区分门数且跨改款；保留已确认五门改款前分支。	READY
26627_5dr_facelift	26627	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数且跨改款；保留已确认五门改款后分支。	READY
26628	26628	Hatchback	Modus / Grand Modus		5		LOW	输入合并短轴Modus与Grand Modus，需确认全部外廓分支。	PENDING: 需拆分Modus与Grand Modus物理外廓
26629	26629	Hatchback	Modus / Grand Modus		5		LOW	输入合并短轴Modus与Grand Modus，需确认全部外廓分支。	PENDING: 需拆分Modus与Grand Modus物理外廓
26630	26630	Hatchback	207 / 207+	A7			LOW	Ktype跨207与207+且门数边界未闭合。	PENDING: 需确认门数及207+改款外廓
26631	26631	Coupe	407 Coupe		2		MEDIUM	Coupe为独立外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26632	26632	MPV	807 I		5	EU-PEUGEOT-807-MPV-01	HIGH		READY
26633_prefl	26633	SUV	Outlander II pre-facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	MEDIUM	Ktype跨改款；本轮先闭合改款前分支，改款后分支待首次建组。	READY
26633_facelift	26633	SUV	Outlander II facelift	CW0	5		MEDIUM	同一Ktype跨改款，改款后外廓尚未闭合。	PENDING: 改款后尺寸组及来源尚未闭合
26634	26634	MPV	Grandis	NA4W	5		MEDIUM	同代五门MPV外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26635	26635	Hatchback	Pro Cee'd I	ED	3	EU-KIA-PRO-CEED-I-HATCHBACK-3D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26636_prefl	26636	Wagon	Cee'd SW I pre-facelift	ED	5	EU-KIA-CEED-I-SW-WAGON-5D-PREFL-01	HIGH	同一Ktype跨改款，旅行版高度变化，拆分改款前外廓。	READY
26636_facelift	26636	Wagon	Cee'd SW I facelift	ED	5	EU-KIA-CEED-I-SW-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨改款，旅行版高度变化，拆分改款后外廓。	READY
26637	26637	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26638	26638	Hatchback	Ypsilon I facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
26643	26643	Sedan	Lancer Evolution X	CZ4A	4		MEDIUM	EVO X宽体外廓需独立建组。	PENDING: EVO X尺寸组来源尚未闭合
26644	26644	Coupe	A5 I pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
26645	26645	Hatchback	Lancer VIII Sportback	CX0	5		MEDIUM	Sportback五门外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26646	26646	Hatchback	Lancer VIII Sportback	CX0	5		MEDIUM	Sportback五门外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26647	26647	Hatchback	Lancer VIII Sportback	CX0	5		MEDIUM	Sportback五门外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
26648	26648	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
26649	26649	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
26650	26650	Wagon	Laguna III Grandtour		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
26651	26651	Wagon	Laguna III Grandtour		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
26652	26652	Hatchback	Twingo II RS	CN0	3		MEDIUM	RS外部套件与普通车身不同，需独立闭合。	PENDING: RS尺寸组来源尚未闭合
26653	26653	SUV	Koleos I	HY	5		MEDIUM	同代五门SUV外廓，尺寸组尚未闭合。	PENDING: 尺寸组来源尚未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLKSWAGEN-JETTA-V-SEDAN-4D-01	4554	1781	1459	Auto-Data Volkswagen Jetta V 2.5i	https://www.auto-data.net/en/volkswagen-jetta-v-2.5i-150hp-9085
EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	4493	1810	1636	Auto-Data Renault Grand Scenic II Phase I 2.0 dCi	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-i-2.0-dci-150hp-39489
EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	4496	1810	1636	Auto-Data Renault Grand Scenic II Phase II 2.0 dCi	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-ii-2.0-dci-150hp-39505
EU-MERCEDES-BENZ-C-CLASS-W204-AMG-SEDAN-4D-01	4725	1795	1438	Auto-Data Mercedes-Benz C-class W204 AMG C 63 V8	https://www.auto-data.net/en/mercedes-benz-c-class-w204-amg-c-63-v8-457hp-7g-tronic-amg-speedshift-plus-12549
EU-MERCEDES-BENZ-C-CLASS-S204-AMG-WAGON-5D-01	4726	1795	1442	Auto-Data Mercedes-Benz C-class T-modell S204 AMG C 63 V8	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-amg-c-63-v8-457hp-7g-tronic-amg-speedshift-plus-12564
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	4788	1911	1840	Auto-Data Mercedes-Benz M-class W164 ML 500 V8	https://www.auto-data.net/en/mercedes-benz-m-class-w164-ml-500-v8-388hp-4matic-7g-tronic-12764
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	4781	1911	1815	Auto-Data Mercedes-Benz M-class W164 facelift ML 500 V8	https://www.auto-data.net/en/mercedes-benz-m-class-w164-facelift-2008-ml-500-v8-388hp-4matic-7g-tronic-43632
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281	Auto-Data Mercedes-Benz SLR McLaren R199 Roadster	https://www.auto-data.net/en/mercedes-benz-slr-mclaren-r199-roadster-5.5-v8-kompressor-626hp-amg-speedshift-r-12726
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-01	5079	1871	1473	Auto-Data Mercedes-Benz S-class W221 S 350 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-w221-s-350-272hp-4matic-7g-tronic-13036
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-class W221 facelift S 350 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-350-272hp-4matic-g-tronic-36914
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	4562	1820	1317	Auto-Data Mercedes-Benz SL R230 facelift 2008 SL 350; Auto-Data Mercedes-Benz SL R230 facelift 2008 AMG SL 63	https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2008-sl-350-v6-316hp-7g-tronic-41267;https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2008-amg-sl-63-v8-525hp-speedshift-mct-7g-tronic-41271
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.1 CRDi; Automobile-Catalog Hyundai i10 1.1	https://www.auto-data.net/en/hyundai-i10-i-1.1-crdi-75hp-13880;https://www.automobile-catalog.com/car/2008/1180925/hyundai_i10_1_1_style.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I facelift generation; Automobile-Catalog Hyundai i10 1.1	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787;https://www.automobile-catalog.com/car/2011/1606325/hyundai_i10_1_1_style.html
EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	4415	1755	1465	Auto-Data Mazda 3 I Hatchback BK facelift 2.0 CD	https://www.auto-data.net/en/mazda-3-i-hatchback-bk-facelift-2006-2.0-cd-143hp-16771
EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	4580	1755	1465	Auto-Data Mazda 3 I Sedan BK facelift 2.0 CD	https://www.auto-data.net/en/mazda-3-i-sedan-bk-facelift-2006-2.0-cd-143hp-16770
EU-HONDA-CIVIC-TYPE-R-FN2-HATCHBACK-3D-01	4276	1785	1445	Auto-Data Honda Civic Type R FN2 2.0	https://www.auto-data.net/en/honda-civic-type-r-fn2-2.0-201hp-12221
EU-BMW-M3-E90-SEDAN-4D-01	4580	1817	1447	Auto-Data BMW M3 E90; Auto-Data BMW M3 E90 LCI	https://www.auto-data.net/en/bmw-m3-e90-4.0-v8-420hp-52640;https://www.auto-data.net/en/bmw-m3-e90-lci-facelift-2008-4.0-v8-420hp-9865
EU-BMW-M3-E93-CONVERTIBLE-2D-01	4615	1804	1392	Auto-Data BMW M3 E93; Auto-Data BMW M3 E93 LCI	https://www.auto-data.net/en/bmw-m3-convertible-e93-4.0-v8-420hp-52646;https://www.auto-data.net/en/bmw-m3-convertible-e93-lci-facelift-2010-4.0-v8-420hp-9866
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450	Auto-Data Saab 9-3 Sedan II facelift	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-1.9-ttid-180hp-11908
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496	Auto-Data Saab 9-3 Sport Combi II facelift	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-1.9-ttid-180hp-11932
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-5D-01	4888	1822	1506	Auto-Data Mercedes-Benz E-Class T-Modell S211 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-200-cdi-136hp-12907
EU-SMART-FORTWO-II-A451-CONVERTIBLE-2D-BRABUS-01	2695	1559	1542	Auto-Data Smart Fortwo II Cabrio Brabus	https://www.auto-data.net/en/smart-fortwo-ii-cabrio-a451-brabus-1.0i-turbo-98hp-14870
EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	4799	1855	1417	Auto-Data Volkswagen Passat CC I generation	https://www.auto-data.net/en/volkswagen-passat-cc-i-generation-1894
EU-KIA-PRO-CEED-I-HATCHBACK-3D-01	4250	1790	1450	Automobile-Catalog Kia Pro Cee'd; Auto-Data Kia Pro Cee'd I facelift	https://www.automobile-catalog.com/car/2008/1360760/kia_pro_cee_d_2_0_crdi_sport.html;https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.6-16v-126hp-17080
EU-KIA-CEED-I-SW-WAGON-5D-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I generation	https://www.auto-data.net/en/kia-ceed-sw-i-generation-8041
EU-KIA-CEED-I-SW-WAGON-5D-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift 1.6 16V	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.6-16v-126hp-17072
EU-KIA-CEED-I-HATCHBACK-5D-01	4235	1790	1480	Auto-Data Kia Cee'd I; Auto-Data Kia Cee'd I facelift	https://www.auto-data.net/en/kia-ceed-i-2.0-crdi-140hp-42284;https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.6-16v-126hp-17065
```

## 下一步优先处理

1. 优先解决 Peugeot 308 SW 的 7 个 Ktype 和 Mercedes-Benz CLC 的 6 个 Ktype，单次核对可消除最多 PENDING。
2. 闭合 Modus/Grand Modus、Aveo、Berlingo 与 H-1 Cargo 的多物理车身分支。
3. 批量完成 Kuga、Sirion、Panda Natural Power、407 Coupe、Grandis、Lancer、Twingo RS、Koleos 及 Outlander facelift。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-m3-e90-4.0-v8-420hp-52640 "https://www.auto-data.net/en/bmw-m3-e90-4.0-v8-420hp-52640"
[2]: https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-1.9-ttid-180hp-11908 "https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-1.9-ttid-180hp-11908"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 原 `26560` 基础 PENDING 行已删除，按输入同时覆盖的厢式与乘用车身拆为 `26560_van`、`26560_mpv`，直接复用跨批次既有尺寸组。
* `26564–26569` 共用 Mercedes-Benz CLC CL203 三门外廓，首次创建尺寸组；官方资料确认三维为 `4448 × 1728 × 1405 mm`，宽度不含后视镜。
* `26577–26578` 共用 Ford Kuga I C394 五门外廓，首次创建尺寸组；官方车型资料确认三维为 `4443 × 1842 × 1710 mm`，其中 1842 mm 明确为不含后视镜宽度。
* `26631` Peugeot 407 Coupé 已闭合；官方规格表确认三维为 `4815 × 1868 × 1399 mm`，宽度明确不含车门后视镜。([全车中心][1])

## 当前批次进度

* 输入 Ktype：100
* 完全闭合 Ktype：75 / 100
* READY 映射：92
* PENDING 映射：25
* 当前映射总行数：117
* 当前批次引用的已确认尺寸组：70
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26560_van	26560	Van	Berlingo I M59	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	输入同时覆盖厢式与乘用车身，拆分厢式外廓。	READY
26560_mpv	26560	MPV	Berlingo I M59	M59	5	EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	输入同时覆盖厢式与乘用车身，拆分乘用外廓。	READY
26564	26564	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26565	26565	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26566	26566	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26567	26567	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26568	26568	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26569	26569	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26577	26577	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
26578	26578	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
26631	26631	Coupe	407 Coupe		2	EU-PEUGEOT-407-COUPE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	4448	1728	1405	Mercedes-Benz CLC-Class official brochure	https://ragtop.org/mbbrochures/2010/international/CLC-Class_CLC_1209_02.pdf
EU-FORD-KUGA-I-C394-SUV-5D-01	4443	1842	1710	Ford Kuga official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Kuga-UK.pdf
EU-PEUGEOT-407-COUPE-2D-01	4815	1868	1399	Peugeot 407 Coupe official specification and pricing	https://www.allcarcentral.com/peugeot_UK_pdf/Peugeot_407_Coupe_2008.pdf
```

## 下一步优先处理

1. 集中闭合 `26610–26616` Peugeot 308 SW，共用尺寸组后可一次消除 7 条 PENDING。
2. 批量处理 `26645–26647` Lancer Sportback、`26618–26620` Sirion。
3. 拆分并闭合 Modus／Grand Modus、Aveo 三门／五门，以及剩余独立车型尺寸组。

推进信号：CONTINUE

[1]: https://www.allcarcentral.com/peugeot_UK_pdf/Peugeot_407_Coupe_2008.pdf "407 Coupe_Current.xls"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 Peugeot 308 SW、Hyundai H-1 Cargo、Daihatsu Sirion、Renault Modus／Grand Modus、Peugeot 207、Mitsubishi Outlander 改款版、Grandis、Lancer Evolution X、Lancer Sportback、Renault Twingo RS 与 Koleos。
* `26628`、`26629` 分别拆分为 Modus 改款前、Modus 改款后和 Grand Modus 三种物理外廓。
* `26630` 按三门／五门及改款前／改款后拆分为四种物理外廓。
* `26633_facelift` 按手动挡与 TC-SST 对应的不同车身高度拆分为两个尺寸组。
* 本轮消除 22 条 PENDING；剩余阻塞项为 `26604`、`26605` 和 `26621`。

## 当前批次进度

* 输入 Ktype：100
* 完全闭合 Ktype：97 / 100
* READY 映射：124
* PENDING 映射：3
* 当前映射总行数：127
* 当前批次引用的已确认尺寸组：90
* 本轮首次创建尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26610	26610	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26611	26611	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26612	26612	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26613	26613	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26614	26614	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26615	26615	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26616	26616	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26617	26617	Van	H-1 II Cargo	TQ		EU-HYUNDAI-H-1-II-TQ-CARGO-VAN-01	HIGH		READY
26618	26618	Hatchback	Sirion II facelift	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	HIGH		READY
26619	26619	Hatchback	Sirion II facelift	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	MEDIUM		READY
26620	26620	Hatchback	Sirion II Sport	M3	5	EU-DAIHATSU-SIRION-II-M3-SPORT-HATCHBACK-5D-01	HIGH	SPORT外部套件对应较长外廓。	READY
26628_modus_prefl	26628	Hatchback	Modus I pre-facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	MEDIUM	短轴Modus改款前外廓。	READY
26628_modus_facelift	26628	Hatchback	Modus I facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	短轴Modus改款后外廓。	READY
26628_grand	26628	Hatchback	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	MEDIUM	长轴Grand Modus外廓。	READY
26629_modus_prefl	26629	Hatchback	Modus I pre-facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	MEDIUM	短轴Modus改款前外廓。	READY
26629_modus_facelift	26629	Hatchback	Modus I facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	短轴Modus改款后外廓。	READY
26629_grand	26629	Hatchback	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	MEDIUM	长轴Grand Modus外廓。	READY
26630_3dr_prefl	26630	Hatchback	207 I pre-facelift	A7	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前外廓。	READY
26630_5dr_prefl	26630	Hatchback	207 I pre-facelift	A7	5	EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前外廓。	READY
26630_3dr_facelift	26630	Hatchback	207 I facelift	A7	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后外廓。	READY
26630_5dr_facelift	26630	Hatchback	207 I facelift	A7	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
26633_facelift_manual	26633	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-MANUAL-01	HIGH	改款手动挡较高外廓。	READY
26633_facelift_tcsst	26633	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-TCSST-01	HIGH	改款TC-SST较低外廓。	READY
26634	26634	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
26643	26643	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-4D-01	HIGH	Evolution X宽体轿车外廓。	READY
26645	26645	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26646	26646	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26647	26647	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26652	26652	Hatchback	Twingo II RS	CN0	3	EU-RENAULT-TWINGO-II-RS-HATCHBACK-3D-01	HIGH	RS外部套件独立外廓。	READY
26653_phase1	26653	SUV	Koleos I Phase I	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	MEDIUM	Phase I外廓。	READY
26653_phase2	26653	SUV	Koleos I Phase II	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	MEDIUM	Phase II外廓。	READY
26653_phase3	26653	SUV	Koleos I Phase III	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	MEDIUM	Phase III外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564	Auto-Data Peugeot 308 SW I Phase I 1.6 HDi	https://www.auto-data.net/en/peugeot-308-sw-i-phase-i-2008-1.6-hdi-112hp-52713
EU-HYUNDAI-H-1-II-TQ-CARGO-VAN-01	5150	1920	1925	Auto-Data Hyundai H-1 II Cargo 2.5 CRDi	https://www.auto-data.net/en/hyundai-h-1-ii-cargo-2.5-crdi-170hp-automatic-25116
EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	3605	1665	1550	UltimateSpecs Daihatsu Sirion II 1.3 16V HIRO	https://www.ultimatespecs.com/car-specs/Daihatsu/13473/Daihatsu-Sirion-II-13-16V-HIRO-Aut.html
EU-DAIHATSU-SIRION-II-M3-SPORT-HATCHBACK-5D-01	3630	1665	1550	UltimateSpecs Daihatsu Sirion II 1.5 16V SPORT	https://www.ultimatespecs.com/car-specs/Daihatsu/13475/Daihatsu-Sirion-II-15-16V-SPORT.html
EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	3792	1695	1589	Auto-Data Renault Modus 1.2i 16V	https://www.auto-data.net/en/renault-modus-1.2i-16v-75hp-10624
EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	3874	1709	1589	Auto-Data Renault Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-modus-phase-ii-1.2-16v-75hp-29869
EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	4034	1709	1589	Auto-Data Renault Grand Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-16v-75hp-29949
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.4 VTi	https://www.auto-data.net/en/peugeot-207-1.4-vti-95hp-33967
EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.4 VTi	https://www.auto-data.net/en/peugeot-207-1.4-vti-95hp-33967
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 VTi	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-vti-95hp-33970
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 VTi	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-vti-95hp-33970
EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-MANUAL-01	4665	1800	1720	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-156hp-4wd-51287
EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-TCSST-01	4665	1800	1680	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D TC-SST 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-156hp-tc-sst-4wd-42195
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655	Auto-Data Mitsubishi Grandis 2.0 DI-D	https://www.auto-data.net/en/mitsubishi-grandis-2.0-di-d-136hp-15448
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-4D-01	4505	1810	1480	Auto-Data Mitsubishi Lancer Evolution X 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-lancer-evolution-x-2.0-mivec-295hp-s-awc-15647
EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	4585	1760	1515	Auto-Data Mitsubishi Lancer Sportback IX 1.8 MPI	https://www.auto-data.net/en/mitsubishi-lancer-sportback-ix-gs44s-1.8-mpi-143hp-15643
EU-RENAULT-TWINGO-II-RS-HATCHBACK-3D-01	3607	1688	1460	Auto-Data Renault Twingo II RS 1.6 16V	https://www.auto-data.net/en/renault-twingo-ii-rs-1.6-16v-133hp-35198
EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	4520	1855	1695	Auto-Data Renault Koleos 2.0 dCi 4x2	https://www.auto-data.net/en/renault-koleos-2.0-dci-fap-150hp-4x2-10808
EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	4520	1855	1695	Auto-Data Renault Koleos Phase II 2.0	https://www.auto-data.net/en/renault-koleos-phase-ii-2.0-150hp-20211
EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	4520	1865	1695	Automobile-Catalog Renault Koleos Phase III 2.0 dCi 150 4x2	https://www.automobile-catalog.com/car/2014/2959325/renault_koleos_2_0_dci_150_4x2.html
```

## 下一步优先处理

1. 解决 `26604`、`26605` Chevrolet Aveo Hatchback 的同车身宽度冲突，并确认是否需要按发动机对应的实际车身阶段拆分。
2. 获取 `26621` Fiat Panda Natural Power 未经十毫米取整的精确三维，并确认不含后视镜宽度。
3. 三条 PENDING 闭合后，立即进行一次机械检查并输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 最后 3 条 PENDING 已闭合：`26604`、`26605` 按 Aveo T255 三门和五门拆分；`26621` 建立 Panda II Natural Power 独立高车身尺寸组。([汽车档案库][1])
* 已完成机械检查：固定表头正确，所有 `id` 与 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，无孤立尺寸组，三维和来源字段完整。
* 当前批次达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* 完整映射行：129
* READY：129
* PENDING：0
* DIMENSION_GROUP：93
* 未闭合映射引用：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26550	26550	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	HIGH		READY
26551_prefl	26551	MPV	Altea I pre-facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26551_facelift	26551	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26552_prefl	26552	Hatchback	Leon II pre-facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26552_facelift	26552	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26553	26553	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26554	26554	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26555	26555	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
26556	26556	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
26557	26557	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26558	26558	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26559	26559	Sedan	Jetta V	1K2	4	EU-VOLKSWAGEN-JETTA-V-SEDAN-4D-01	HIGH	输入“Jetta iii”对应欧洲第五代Jetta轿车外廓。	READY
26560_van	26560	Van	Berlingo I M59	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	输入同时覆盖厢式与乘用车身，拆分厢式外廓。	READY
26560_mpv	26560	MPV	Berlingo I M59	M59	5	EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	输入同时覆盖厢式与乘用车身，拆分乘用外廓。	READY
26561	26561	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
26562_prefl	26562	MPV	Grand Scenic II Phase I	R84	5	EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	HIGH	同一Ktype跨Phase I/II且车长变化，拆分Phase I外廓。	READY
26562_facelift	26562	MPV	Grand Scenic II Phase II	R84	5	EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	同一Ktype跨Phase I/II且车长变化，拆分Phase II外廓。	READY
26563_prefl	26563	SUV	Q7 I pre-facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26563_facelift	26563	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26564	26564	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26565	26565	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26566	26566	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26567	26567	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26568	26568	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26569	26569	Coupe	CLC-Class	CL203	3	EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	HIGH		READY
26570	26570	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
26571	26571	Sedan	C-Class W204 AMG	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-AMG-SEDAN-4D-01	HIGH	W204四门AMG轿车外廓。	READY
26572	26572	Wagon	C-Class S204 AMG	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-AMG-WAGON-5D-01	HIGH	S204五门AMG旅行车外廓。	READY
26573_prefl	26573	SUV	M-Class W164 pre-facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	HIGH	同一Ktype跨改款且长高变化，拆分改款前外廓。	READY
26573_facelift	26573	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH	同一Ktype跨改款且长高变化，拆分改款后外廓。	READY
26574	26574	Convertible	SLR McLaren R199 Roadster	R199	2	EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	HIGH	R199双门Roadster外廓。	READY
26575_prefl	26575	Sedan	S-Class W221 pre-facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-01	HIGH	同一Ktype跨2009改款且三维变化，拆分改款前外廓。	READY
26575_facelift	26575	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2009改款且三维变化，拆分改款后外廓。	READY
26576	26576	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26577	26577	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
26578	26578	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
26579	26579	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26580	26580	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008改款R230双门Roadster外廓；当前三维与既有01不一致，按规则新建02。	READY
26581_3dr_prefl	26581	Hatchback	A3 II pre-facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	三门Ktype跨改款，拆分改款前外廓。	READY
26581_3dr_facelift	26581	Hatchback	A3 II facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	三门Ktype跨改款，拆分改款后外廓。	READY
26582_5dr_prefl	26582	Hatchback	A3 II Sportback pre-facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	五门Sportback Ktype跨改款，拆分改款前外廓。	READY
26582_5dr_facelift	26582	Hatchback	A3 II Sportback facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	五门Sportback Ktype跨改款，拆分改款后外廓。	READY
26583	26583	Hatchback	Mazda2 II pre-facelift	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	HIGH		READY
26584_prefl	26584	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨改款，拆分改款前外廓。	READY
26584_facelift	26584	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨改款，拆分改款后外廓。	READY
26585	26585	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH		READY
26586	26586	Hatchback	Mazda3 I facelift	BK	5	EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	HIGH		READY
26587	26587	Sedan	Mazda3 I facelift	BK	4	EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	HIGH		READY
26588	26588	Hatchback	Civic Type R FN2	FN2	3	EU-HONDA-CIVIC-TYPE-R-FN2-HATCHBACK-3D-01	HIGH	FN2三门Type R宽体外廓，不复用普通Civic五门组。	READY
26589	26589	Sedan	M3 E90	E90	4	EU-BMW-M3-E90-SEDAN-4D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26590	26590	Convertible	M3 E93	E93	2	EU-BMW-M3-E93-CONVERTIBLE-2D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26591	26591	Convertible	9-3 II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH		READY
26592	26592	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	2007改款四门轿车外廓。	READY
26593	26593	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	2007改款五门Sport Combi外廓。	READY
26594	26594	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	2007改款四门轿车外廓。	READY
26595	26595	Convertible	9-3 II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH		READY
26596	26596	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	2007改款五门Sport Combi外廓。	READY
26597	26597	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-5D-01	HIGH	S211改款五门旅行车外廓。	READY
26598	26598	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-A451-CONVERTIBLE-2D-BRABUS-01	HIGH	A451双门Brabus敞篷外廓。	READY
26599	26599	Coupe	Brera 939	939	3	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	输入Schrägheck按Brera三门双门轿跑物理车身标准化为Coupe。	READY
26600	26600	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
26601	26601	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
26602	26602	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
26603	26603	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
26604_3dr	26604	Hatchback	Aveo T255 facelift	T255	3	EU-CHEVROLET-AVEO-T255-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
26604_5dr	26604	Hatchback	Aveo T255 facelift	T255	5	EU-CHEVROLET-AVEO-T255-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
26605_3dr	26605	Hatchback	Aveo T255 facelift	T255	3	EU-CHEVROLET-AVEO-T255-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
26605_5dr	26605	Hatchback	Aveo T255 facelift	T255	5	EU-CHEVROLET-AVEO-T255-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
26606	26606	Hatchback	308 I		5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
26607	26607	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26608	26608	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26609	26609	Coupe	Passat CC I	3C8	4	EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	HIGH		READY
26610	26610	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26611	26611	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26612	26612	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26613	26613	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26614	26614	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26615	26615	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26616	26616	Wagon	308 SW I Phase I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
26617	26617	Van	H-1 II Cargo	TQ		EU-HYUNDAI-H-1-II-TQ-CARGO-VAN-01	HIGH		READY
26618	26618	Hatchback	Sirion II facelift	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	HIGH		READY
26619	26619	Hatchback	Sirion II facelift	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	MEDIUM		READY
26620	26620	Hatchback	Sirion II Sport	M3	5	EU-DAIHATSU-SIRION-II-M3-SPORT-HATCHBACK-5D-01	HIGH	SPORT外部套件对应较长外廓。	READY
26621	26621	Hatchback	Panda II Natural Power	169	5	EU-FIAT-PANDA-II-169-NATURAL-POWER-HATCHBACK-5D-01	HIGH	Natural Power高车身外廓。	READY
26622	26622	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	HIGH		READY
26623_prefl	26623	Hatchback	Octavia II RS pre-facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	HIGH	同一Ktype跨改款，拆分RS改款前外廓。	READY
26623_facelift	26623	Hatchback	Octavia II RS facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	HIGH	同一Ktype跨改款，拆分RS改款后外廓。	READY
26624_prefl	26624	Wagon	Octavia II RS pre-facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	HIGH	同一Ktype跨改款，拆分RS改款前外廓。	READY
26624_facelift	26624	Wagon	Octavia II RS facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	HIGH	同一Ktype跨改款，拆分RS改款后外廓。	READY
26625	26625	Hatchback	C2 I	JM	3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
26626	26626	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH		READY
26627_3dr_prefl	26627	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入未区分门数且跨改款；保留已确认三门改款前分支。	READY
26627_3dr_facelift	26627	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数且跨改款；保留已确认三门改款后分支。	READY
26627_5dr_prefl	26627	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入未区分门数且跨改款；保留已确认五门改款前分支。	READY
26627_5dr_facelift	26627	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数且跨改款；保留已确认五门改款后分支。	READY
26628_modus_prefl	26628	Hatchback	Modus I pre-facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	MEDIUM	短轴Modus改款前外廓。	READY
26628_modus_facelift	26628	Hatchback	Modus I facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	短轴Modus改款后外廓。	READY
26628_grand	26628	Hatchback	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	MEDIUM	长轴Grand Modus外廓。	READY
26629_modus_prefl	26629	Hatchback	Modus I pre-facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	MEDIUM	短轴Modus改款前外廓。	READY
26629_modus_facelift	26629	Hatchback	Modus I facelift		5	EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	短轴Modus改款后外廓。	READY
26629_grand	26629	Hatchback	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	MEDIUM	长轴Grand Modus外廓。	READY
26630_3dr_prefl	26630	Hatchback	207 I pre-facelift	A7	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前外廓。	READY
26630_5dr_prefl	26630	Hatchback	207 I pre-facelift	A7	5	EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前外廓。	READY
26630_3dr_facelift	26630	Hatchback	207 I facelift	A7	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后外廓。	READY
26630_5dr_facelift	26630	Hatchback	207 I facelift	A7	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
26631	26631	Coupe	407 Coupe		2	EU-PEUGEOT-407-COUPE-2D-01	HIGH		READY
26632	26632	MPV	807 I		5	EU-PEUGEOT-807-MPV-01	HIGH		READY
26633_prefl	26633	SUV	Outlander II pre-facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	MEDIUM	Ktype跨改款；本轮先闭合改款前分支，改款后分支待首次建组。	READY
26633_facelift_manual	26633	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-MANUAL-01	HIGH	改款手动挡较高外廓。	READY
26633_facelift_tcsst	26633	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-TCSST-01	HIGH	改款TC-SST较低外廓。	READY
26634	26634	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
26635	26635	Hatchback	Pro Cee'd I	ED	3	EU-KIA-PRO-CEED-I-HATCHBACK-3D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26636_prefl	26636	Wagon	Cee'd SW I pre-facelift	ED	5	EU-KIA-CEED-I-SW-WAGON-5D-PREFL-01	HIGH	同一Ktype跨改款，旅行版高度变化，拆分改款前外廓。	READY
26636_facelift	26636	Wagon	Cee'd SW I facelift	ED	5	EU-KIA-CEED-I-SW-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨改款，旅行版高度变化，拆分改款后外廓。	READY
26637	26637	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH	改款前后外廓三维一致，复用同一尺寸组。	READY
26638	26638	Hatchback	Ypsilon I facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
26643	26643	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-4D-01	HIGH	Evolution X宽体轿车外廓。	READY
26644	26644	Coupe	A5 I pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
26645	26645	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26646	26646	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26647	26647	Hatchback	Lancer IX Sportback	GS44S	5	EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	HIGH		READY
26648	26648	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
26649	26649	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
26650	26650	Wagon	Laguna III Grandtour		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
26651	26651	Wagon	Laguna III Grandtour		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
26652	26652	Hatchback	Twingo II RS	CN0	3	EU-RENAULT-TWINGO-II-RS-HATCHBACK-3D-01	HIGH	RS外部套件独立外廓。	READY
26653_phase1	26653	SUV	Koleos I Phase I	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	MEDIUM	Phase I外廓。	READY
26653_phase2	26653	SUV	Koleos I Phase II	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	MEDIUM	Phase II外廓。	READY
26653_phase3	26653	SUV	Koleos I Phase III	HY	5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	MEDIUM	Phase III外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2301-2400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463	Auto-Data Audi A6 Avant 4F C6 2.0 TDI	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.0-tdi-140hp-4665
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	Auto-Data Seat Altea 5P 1.4 MPI	https://www.auto-data.net/en/seat-altea-5p-1.4-mpi-85hp-13577
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data Seat Altea facelift 2009	https://www.auto-data.net/en/seat-altea-facelift-2009-generation-4202
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data Seat Leon II 1P	https://www.auto-data.net/en/seat-leon-ii-1p-1.8-tsi-160hp-46446
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data Seat Leon II facelift FR	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-fr-2.0-tdi-cr-170hp-dpf-46487
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data Audi A4 B7 2.0 TDI quattro	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-140hp-quattro-dpf-26496
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453	Auto-Data Audi A4 Avant B7 8E	https://www.auto-data.net/en/audi-a4-avant-b7-8e-generation-5202
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data Seat Toledo III 5P	https://www.auto-data.net/en/seat-toledo-iii-5p-generation-2911
EU-VOLKSWAGEN-JETTA-V-SEDAN-4D-01	4554	1781	1459	Auto-Data Volkswagen Jetta V 2.5i	https://www.auto-data.net/en/volkswagen-jetta-v-2.5i-150hp-9085
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819	Automobile-Catalog Citroen Berlingo First HDi 75 X	https://www.automobile-catalog.com/car/2009/1213775/citroen_berlingo_first_hdi_75_x.html
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810	Automobile-Catalog Citroen Berlingo Multispace 1.9 D	https://www.automobile-catalog.com/car/2002/550205/citroen_berlingo_multispace_1_9_d.html
EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	4493	1810	1636	Auto-Data Renault Grand Scenic II Phase I 2.0 dCi	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-i-2.0-dci-150hp-39489
EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	4496	1810	1636	Auto-Data Renault Grand Scenic II Phase II 2.0 dCi	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-ii-2.0-dci-150hp-39505
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737	Auto-Data Audi Q7 I 4L	https://www.auto-data.net/en/audi-q7-model-517
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737	Auto-Data Audi Q7 I 4L facelift 2009	https://www.auto-data.net/en/audi-q7-i-typ-4l-facelift-2009-generation-4178
EU-MERCEDES-BENZ-CLC-CL203-COUPE-3D-01	4448	1728	1405	Mercedes-Benz CLC-Class official brochure	https://ragtop.org/mbbrochures/2010/international/CLC-Class_CLC_1209_02.pdf
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588	Automobile-Catalog Ford Europe C-Max 2008	https://www.automobile-catalog.com/make/ford_europe/c-max_1gen/c-max_1gen__ii/2008.html
EU-MERCEDES-BENZ-C-CLASS-W204-AMG-SEDAN-4D-01	4725	1795	1438	Auto-Data Mercedes-Benz C-class W204 AMG C 63 V8	https://www.auto-data.net/en/mercedes-benz-c-class-w204-amg-c-63-v8-457hp-7g-tronic-amg-speedshift-plus-12549
EU-MERCEDES-BENZ-C-CLASS-S204-AMG-WAGON-5D-01	4726	1795	1442	Auto-Data Mercedes-Benz C-class T-modell S204 AMG C 63 V8	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-amg-c-63-v8-457hp-7g-tronic-amg-speedshift-plus-12564
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	4788	1911	1840	Auto-Data Mercedes-Benz M-class W164 ML 500 V8	https://www.auto-data.net/en/mercedes-benz-m-class-w164-ml-500-v8-388hp-4matic-7g-tronic-12764
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	4781	1911	1815	Auto-Data Mercedes-Benz M-class W164 facelift ML 500 V8	https://www.auto-data.net/en/mercedes-benz-m-class-w164-facelift-2008-ml-500-v8-388hp-4matic-7g-tronic-43632
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281	Auto-Data Mercedes-Benz SLR McLaren R199 Roadster	https://www.auto-data.net/en/mercedes-benz-slr-mclaren-r199-roadster-5.5-v8-kompressor-626hp-amg-speedshift-r-12726
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-01	5079	1871	1473	Auto-Data Mercedes-Benz S-class W221 S 350 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-w221-s-350-272hp-4matic-7g-tronic-13036
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-class W221 facelift S 350 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-350-272hp-4matic-g-tronic-36914
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	4562	1820	1317	Auto-Data Mercedes-Benz SL R230 facelift 2008 SL 350; Auto-Data Mercedes-Benz SL R230 facelift 2008 AMG SL 63	https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2008-sl-350-v6-316hp-7g-tronic-41267;https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2008-amg-sl-63-v8-525hp-speedshift-mct-7g-tronic-41271
EU-FORD-KUGA-I-C394-SUV-5D-01	4443	1842	1710	Ford Kuga official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Kuga-UK.pdf
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-generation-8936
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-2.0-tdi-140hp-quattro-55462
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA	https://www.auto-data.net/en/audi-a3-sportback-8pa-generation-1067
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423	Auto-Data Audi A3 Sportback 8PA facelift 2008	https://www.auto-data.net/en/audi-a3-sportback-8pa-facelift-2008-1.6-tdi-105hp-s-tronic-55461
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475	Auto-Data Mazda 2 II DE 1.4 CD	https://www.auto-data.net/en/mazda-2-ii-de-1.4-cd-68hp-11448
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.1 CRDi; Automobile-Catalog Hyundai i10 1.1	https://www.auto-data.net/en/hyundai-i10-i-1.1-crdi-75hp-13880;https://www.automobile-catalog.com/car/2008/1180925/hyundai_i10_1_1_style.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I facelift generation; Automobile-Catalog Hyundai i10 1.1	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787;https://www.automobile-catalog.com/car/2011/1606325/hyundai_i10_1_1_style.html
EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	4415	1755	1465	Auto-Data Mazda 3 I Hatchback BK facelift 2.0 CD	https://www.auto-data.net/en/mazda-3-i-hatchback-bk-facelift-2006-2.0-cd-143hp-16771
EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	4580	1755	1465	Auto-Data Mazda 3 I Sedan BK facelift 2.0 CD	https://www.auto-data.net/en/mazda-3-i-sedan-bk-facelift-2006-2.0-cd-143hp-16770
EU-HONDA-CIVIC-TYPE-R-FN2-HATCHBACK-3D-01	4276	1785	1445	Auto-Data Honda Civic Type R FN2 2.0	https://www.auto-data.net/en/honda-civic-type-r-fn2-2.0-201hp-12221
EU-BMW-M3-E90-SEDAN-4D-01	4580	1817	1447	Auto-Data BMW M3 E90; Auto-Data BMW M3 E90 LCI	https://www.auto-data.net/en/bmw-m3-e90-4.0-v8-420hp-52640;https://www.auto-data.net/en/bmw-m3-e90-lci-facelift-2008-4.0-v8-420hp-9865
EU-BMW-M3-E93-CONVERTIBLE-2D-01	4615	1804	1392	Auto-Data BMW M3 E93; Auto-Data BMW M3 E93 LCI	https://www.auto-data.net/en/bmw-m3-convertible-e93-4.0-v8-420hp-52646;https://www.auto-data.net/en/bmw-m3-convertible-e93-lci-facelift-2010-4.0-v8-420hp-9866
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437	Auto-Data Saab 9-3 Convertible II facelift	https://www.auto-data.net/en/saab-9-3-convertible-ii-facelift-2007-1.9-ttid-180hp-54587
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450	Auto-Data Saab 9-3 Sedan II facelift	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-1.9-ttid-180hp-11908
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496	Auto-Data Saab 9-3 Sport Combi II facelift	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-1.9-ttid-180hp-11932
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-5D-01	4888	1822	1506	Auto-Data Mercedes-Benz E-Class T-Modell S211 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-200-cdi-136hp-12907
EU-SMART-FORTWO-II-A451-CONVERTIBLE-2D-BRABUS-01	2695	1559	1542	Auto-Data Smart Fortwo II Cabrio Brabus	https://www.auto-data.net/en/smart-fortwo-ii-cabrio-a451-brabus-1.0i-turbo-98hp-14870
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4413	1830	1372	Auto-Data Alfa Romeo Brera	https://www.auto-data.net/en/alfa-romeo-brera-generation-406
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Auto-Data Alfa Romeo Spider 939	https://www.auto-data.net/en/alfa-romeo-spider-939-generation-387
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data Fiat Bravo II 198	https://www.auto-data.net/en/fiat-bravo-ii-198-generation-1617
EU-CHEVROLET-AVEO-T255-HATCHBACK-3D-01	3920	1680	1505	Chevrolet Aveo 2008 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/04/Chevrolet-Aveo-2008-UK.pdf
EU-CHEVROLET-AVEO-T255-HATCHBACK-5D-01	3920	1680	1505	Chevrolet Aveo 2008 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/04/Chevrolet-Aveo-2008-UK.pdf
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498	Auto-Data Peugeot 308 I Phase I	https://www.auto-data.net/en/peugeot-308-i-phase-i-2007-generation-1237
EU-VOLKSWAGEN-PASSAT-CC-I-COUPE-4D-01	4799	1855	1417	Auto-Data Volkswagen Passat CC I generation	https://www.auto-data.net/en/volkswagen-passat-cc-i-generation-1894
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564	Auto-Data Peugeot 308 SW I Phase I 1.6 HDi	https://www.auto-data.net/en/peugeot-308-sw-i-phase-i-2008-1.6-hdi-112hp-52713
EU-HYUNDAI-H-1-II-TQ-CARGO-VAN-01	5150	1920	1925	Auto-Data Hyundai H-1 II Cargo 2.5 CRDi	https://www.auto-data.net/en/hyundai-h-1-ii-cargo-2.5-crdi-170hp-automatic-25116
EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	3605	1665	1550	UltimateSpecs Daihatsu Sirion II 1.3 16V HIRO	https://www.ultimatespecs.com/car-specs/Daihatsu/13473/Daihatsu-Sirion-II-13-16V-HIRO-Aut.html
EU-DAIHATSU-SIRION-II-M3-SPORT-HATCHBACK-5D-01	3630	1665	1550	UltimateSpecs Daihatsu Sirion II 1.5 16V SPORT	https://www.ultimatespecs.com/car-specs/Daihatsu/13475/Daihatsu-Sirion-II-15-16V-SPORT.html
EU-FIAT-PANDA-II-169-NATURAL-POWER-HATCHBACK-5D-01	3538	1589	1576	Automobile-Catalog Fiat Panda 1.2 Natural Power	https://www.automobile-catalog.com/car/2007/726770/fiat_panda_1_2_natural_power_petrol.html
EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	4719	1863	1759	Auto-Data Fiat Ulysse II 179 facelift	https://www.auto-data.net/en/fiat-ulysse-ii-179-facelift-2008-generation-10247
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462	Auto-Data Skoda Octavia II RS 2.0 TDI	https://www.auto-data.net/en/skoda-octavia-ii-rs-2.0-tdi-170hp-14216
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift RS 2.0 TDI	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-rs-2.0-tdi-170hp-14191
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi RS 2.0 TDI	https://www.auto-data.net/en/skoda-octavia-ii-combi-rs-2.0-tdi-170hp-14234
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451	Auto-Data Skoda Octavia II Combi facelift RS 2.0 TDI	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-rs-2.0-tdi-170hp-55853
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474	Auto-Data Citroen C2 I Phase II	https://www.auto-data.net/en/citroen-c2-i-phase-ii-2008-1.4i-8v-73hp-27413
EU-CITROEN-C8-I-MPV-01	4726	1854	1752	EngineInDetail Citroen C8 2008-2012	https://www.engineindetail.com/cars/citroen/c8/c8-2008-2012
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.5-dci-106hp-25100
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II	https://www.auto-data.net/en/renault-clio-model-1020
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 5-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-generation-11029
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II	https://www.auto-data.net/en/renault-clio-model-1020
EU-RENAULT-MODUS-I-HATCHBACK-5D-PREFL-01	3792	1695	1589	Auto-Data Renault Modus 1.2i 16V	https://www.auto-data.net/en/renault-modus-1.2i-16v-75hp-10624
EU-RENAULT-MODUS-I-HATCHBACK-5D-FACELIFT-01	3874	1709	1589	Auto-Data Renault Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-modus-phase-ii-1.2-16v-75hp-29869
EU-RENAULT-GRAND-MODUS-I-HATCHBACK-5D-01	4034	1709	1589	Auto-Data Renault Grand Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-16v-75hp-29949
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.4 VTi	https://www.auto-data.net/en/peugeot-207-1.4-vti-95hp-33967
EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.4 VTi	https://www.auto-data.net/en/peugeot-207-1.4-vti-95hp-33967
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 VTi	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-vti-95hp-33970
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 VTi	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-vti-95hp-33970
EU-PEUGEOT-407-COUPE-2D-01	4815	1868	1399	Peugeot 407 Coupe official specification and pricing	https://www.allcarcentral.com/peugeot_UK_pdf/Peugeot_407_Coupe_2008.pdf
EU-PEUGEOT-807-MPV-01	4730	1850	1750	Auto-Data Peugeot 807 2.2 HDi	https://www.auto-data.net/en/peugeot-807-2.2-hdi-128hp-5527
EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	4640	1800	1720	Auto-Data Mitsubishi Outlander II	https://www.auto-data.net/en/mitsubishi-outlander-ii-generation-3392
EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-MANUAL-01	4665	1800	1720	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-156hp-4wd-51287
EU-MITSUBISHI-OUTLANDER-II-SUV-FACELIFT-TCSST-01	4665	1800	1680	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D TC-SST 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-156hp-tc-sst-4wd-42195
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655	Auto-Data Mitsubishi Grandis 2.0 DI-D	https://www.auto-data.net/en/mitsubishi-grandis-2.0-di-d-136hp-15448
EU-KIA-PRO-CEED-I-HATCHBACK-3D-01	4250	1790	1450	Automobile-Catalog Kia Pro Cee'd; Auto-Data Kia Pro Cee'd I facelift	https://www.automobile-catalog.com/car/2008/1360760/kia_pro_cee_d_2_0_crdi_sport.html;https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.6-16v-126hp-17080
EU-KIA-CEED-I-SW-WAGON-5D-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I generation	https://www.auto-data.net/en/kia-ceed-sw-i-generation-8041
EU-KIA-CEED-I-SW-WAGON-5D-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift 1.6 16V	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.6-16v-126hp-17072
EU-KIA-CEED-I-HATCHBACK-5D-01	4235	1790	1480	Auto-Data Kia Cee'd I; Auto-Data Kia Cee'd I facelift	https://www.auto-data.net/en/kia-ceed-i-2.0-crdi-140hp-42284;https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.6-16v-126hp-17065
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Auto-Data Lancia Ypsilon 843 facelift	https://www.auto-data.net/en/lancia-ypsilon-843-facelift-2006-generation-9189
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-4D-01	4505	1810	1480	Auto-Data Mitsubishi Lancer Evolution X 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-lancer-evolution-x-2.0-mivec-295hp-s-awc-15647
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372	Auto-Data Audi A5 Coupe 8T3	https://www.auto-data.net/en/audi-a5-coupe-8t3-2.0-tfsi-180hp-multitronic-4510
EU-MITSUBISHI-LANCER-IX-GS44S-SPORTBACK-5D-01	4585	1760	1515	Auto-Data Mitsubishi Lancer Sportback IX 1.8 MPI	https://www.auto-data.net/en/mitsubishi-lancer-sportback-ix-gs44s-1.8-mpi-143hp-15643
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445	Auto-Data Renault Laguna III	https://www.auto-data.net/en/renault-laguna-iii-2.0-16v-140hp-10287
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445	Auto-Data Renault Laguna III Grandtour	https://www.auto-data.net/en/renault-laguna-iii-grandtour-generation-2118
EU-RENAULT-TWINGO-II-RS-HATCHBACK-3D-01	3607	1688	1460	Auto-Data Renault Twingo II RS 1.6 16V	https://www.auto-data.net/en/renault-twingo-ii-rs-1.6-16v-133hp-35198
EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	4520	1855	1695	Auto-Data Renault Koleos 2.0 dCi 4x2	https://www.auto-data.net/en/renault-koleos-2.0-dci-fap-150hp-4x2-10808
EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	4520	1855	1695	Auto-Data Renault Koleos Phase II 2.0	https://www.auto-data.net/en/renault-koleos-phase-ii-2.0-150hp-20211
EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	4520	1865	1695	Automobile-Catalog Renault Koleos Phase III 2.0 dCi 150 4x2	https://www.automobile-catalog.com/car/2014/2959325/renault_koleos_2_0_dci_150_4x2.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2301-2400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://autocatalogarchive.com/wp-content/uploads/2025/04/Chevrolet-Aveo-2008-UK.pdf?utm_source=chatgpt.com "Chevrolet-Aveo-2008-UK.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2301-2400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2301-2400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3366 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1677 行）

- 尺寸冲突协调：
  - EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01 -> EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-02：4788x1910x1815 与 4788x1911x1840，创建新尺寸组
