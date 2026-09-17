# 任务：all 第 2901-3000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0030__904454f2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-RENAULT-TRAFIC-II-BUS-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-BUS-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	5036	1904	1973
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967
EU-RENAULT-TRAFIC-II-VAN-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-VAN-L1H2-01	4782	1904	2465
EU-RENAULT-TRAFIC-II-VAN-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-VAN-L2H2-01	5182	1904	2464
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	5260	1760	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	5260	1835	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	5255	1760	1695
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	5130	1760	1810
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	5255	1835	1810
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	5260	1760	1835
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	5255	1835	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	5255	1760	1795
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	81	110	Jul 2008	Mar 2017	2024-03-01	28225
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	96	131	Jul 2008	Mar 2017	2024-03-01	28226
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	118	160	Jul 2008	Mar 2017	2024-03-01	28227
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	210	286	May 2008	Dec 2010	2024-03-01	28228
Volvo	Xc60 i	2.4 D / D3 / D4 AWD	SUV	Allrad	Diesel	120	163	May 2008	Feb 2017	2024-03-01	28229
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	136	185	May 2008	Dec 2009	2024-03-01	28230
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	118	160	May 2008	Nov 2017	2024-03-01	28231
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	90	122	Aug 2008	Nov 2017	2024-03-01	28232
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Aug 2008	Nov 2017	2024-03-01	28233
VW	Scirocco	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	May 2008	Nov 2009	2024-03-01	28234
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2008	Apr 2017	2024-03-01	28235
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	60	82	Jun 2008	Apr 2017	2024-03-01	28236
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2008	Dec 2012	2024-03-01	28237
Ford	Fiesta vi	1.4	Schrägheck	Frontantrieb	Benzin	71	97	Oct 2008	Dec 2017	2024-03-01	28238
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2008	Sep 2012	2024-03-01	28239
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28240
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28241
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28242
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28243
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	254	345	Oct 2008	Dec 2012	2024-03-01	28244
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	283	385	Oct 2008	Dec 2012	2024-03-01	28245
Porsche	Cayman	S 3,4 Sport	Coupe	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2012	2024-03-01	28246
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2009	2024-03-01	28247
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	70	95	Sep 2008	Aug 2013	2024-03-01	28248
Alfa Romeo	Mito	1.4 Tjet	Schrägheck	Frontantrieb	Benzin	114	155	Aug 2008	Jun 2011	2024-03-01	28249
Alfa Romeo	Mito	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	88	120	Aug 2008	Aug 2015	2024-03-01	28250
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2008	-	2024-03-01	28251
Skoda	Superb ii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 2008	May 2015	2024-03-01	28252
Skoda	Superb ii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Mar 2008	May 2015	2024-03-01	28253
Skoda	Superb ii	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	118	160	Nov 2008	May 2015	2024-03-01	28254
Skoda	Superb ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Nov 2010	2024-03-01	28255
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Mar 2008	May 2010	2024-03-01	28256
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Jul 2008	May 2015	2024-03-01	28257
Skoda	Superb ii	3.6 FSI 4X4	Schrägheck	Allrad	Benzin	191	260	Nov 2008	May 2015	2024-03-01	28258
Ferrari	California	4.3	Cabriolet	Heckantrieb	Benzin	338	460	Jul 2008	-	2024-03-01	28259
Bentley	Continental	6.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	449	610	Sep 2008	Feb 2013	2024-03-01	28260
Seat	Ibiza iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Jun 2010	2024-03-01	28261
Seat	Ibiza iv sc	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jul 2008	Jun 2010	2025-06-01	28262
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	283	385	Jun 2008	Dec 2012	2024-03-01	28263
Ford	Transit tourneo	2	Bus	Heckantrieb	Benzin	84	114	Nov 1994	Dec 2000	2024-03-01	28264
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	51	69	Nov 1994	Dec 2000	2024-03-01	28265
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	56	76	Nov 1994	Dec 2000	2024-03-01	28266
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Nov 1994	Dec 2000	2024-03-01	28267
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Apr 1998	Dec 2000	2024-03-01	28268
Subaru	Impreza	1.5 F	Schrägheck	Frontantrieb	Benzin	79	107	Sep 2007	Mar 2012	2024-03-01	28273
Audi	A4 b8 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	132	180	Jun 2008	Dec 2015	2024-03-01	28276
Audi	A4 b8 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	155	211	Jun 2008	Dec 2015	2024-03-01	28277
Audi	Tt	1.8 Tfsi	Coupe	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28278
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28279
Audi	Tt	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28280
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28281
Skoda	Superb ii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	125	170	Sep 2008	May 2015	2024-03-01	28282
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	125	170	Jun 2008	Jan 2012	2024-03-01	28283
VW	Passat cc b6	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Jun 2008	Jan 2012	2024-03-01	28284
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	100	136	Jun 2008	May 2011	2024-03-01	28285
VW	Touareg	2.5 R5 TDI	SUV	Allrad	Diesel	120	163	Aug 2003	May 2010	2024-03-01	28286
Rover	800	2	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1987	Sep 1988	2024-03-01	28291
Nissan	Primera	2.0 4X4	Stufenheck	Allrad	Benzin	110	150	Mar 1991	Apr 1993	2024-03-01	28308
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	115	156	Nov 1994	Aug 1996	2024-03-01	28332
Fiat	Multipla	1.6	Großraumlimousine	Frontantrieb	Benzin	76	103	Sep 2000	Jun 2010	2024-03-01	28345
Land Rover	110/127	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Jun 1984	Aug 1987	2024-03-01	28359
Land Rover	90	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	52	71	Jan 1984	Aug 1987	2024-03-01	28360
Mini	Mini	John Cooper Works	Schrägheck	Frontantrieb	Benzin	160	218	Mar 2006	Sep 2006	2024-03-01	28363
Fiat	Stilo	1.6	Schrägheck	Frontantrieb	Benzin	100	136	Apr 2005	Nov 2006	2025-11-01	28364
Renault	Vel satis	3.5	Schrägheck	Frontantrieb	Benzin	170	231	Oct 2004	Aug 2009	2025-12-01	28369
Mercedes-benz	Clk	CLK 63 AMG	Coupe	Heckantrieb	Benzin	373	507	May 2007	May 2009	2024-03-01	28372
Mercedes-benz	E-Klasse	350 CGI	Kombi	Heckantrieb	Benzin	215	292	May 2006	Jul 2009	2024-03-01	28374
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	177	241	Nov 2003	Jun 2012	2024-03-01	28376
Renault	Scénic ii	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Jun 2006	Nov 2008	2024-03-01	28380
Subaru	Legacy iv	2.0 AWD	Stufenheck	Allrad	Benzin	121	165	Jun 2005	Apr 2009	2024-03-01	28382
Mitsubishi	Grandis	2.4 Mivec	Großraumlimousine	Frontantrieb	Benzin	130	177	Apr 2004	Dec 2011	2024-03-01	28393
Hummer	Hummer h3	3.7 4WD	Geländewagen geschlossen	Allrad	Benzin	180	245	Sep 2006	-	2024-03-01	28398
Jaguar	Xk ii	3.6	Cabriolet	Heckantrieb	Benzin	190	258	Oct 2007	Jul 2014	2024-03-01	28400
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	195	265	May 2008	Jun 2014	2024-03-01	28404
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	28405
Jaguar	S-Type ii	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	298	405	Nov 2001	Dec 2008	2024-03-01	28427
Honda	Cr-V iii	2.4	SUV	Frontantrieb	Benzin	125	170	Apr 2007	Dec 2012	2025-12-01	28439
Jaguar	Mk ix	3.8	Stufenheck	Heckantrieb	Benzin	164	223	Oct 1958	Jul 1961	2024-03-01	28444
Dodge	Charger	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Sep 2005	Dec 2010	2024-03-01	28454
Dodge	Charger	2.7	Stufenheck	Heckantrieb	Benzin	141	192	Apr 2006	Dec 2010	2024-03-01	28455
Dodge	Durango	4.7 AWD	SUV	Allrad	Benzin	172	234	Nov 2003	Dec 2009	2024-03-01	28460
VW	Golf vi	2.0 TSI	Cabriolet	Frontantrieb	Benzin	162	220	Nov 2013	May 2016	2024-03-01	28480
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1993	Sep 1997	2024-03-01	28494
Mitsubishi	Gto	3.0 AWD	Coupe	Allrad	Benzin	210	286	Jan 1994	Dec 2000	2024-03-01	28497
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	85	116	Aug 2005	-	2025-06-01	28506
Mercedes-benz	Vito / mixto	109 CDI	Kasten	Heckantrieb	Diesel	70	95	Aug 2006	Aug 2014	2025-12-01	28507
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Sep 2006	-	2024-03-01	28514
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	75	102	Mar 2005	May 2015	2024-03-01	28515
Renault	Trafic ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2007	-	2024-03-01	28516
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	28517
Jaguar	Mk x i	3.8	Stufenheck	Heckantrieb	Benzin	197	268	Oct 1961	Oct 1964	2024-05-01	28522
Fiat	Doblo	1.3 JTD	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2005	-	2024-03-01	28536
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28543
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Aug 1991	Jul 1992	2024-03-01	28544
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	68	92	Aug 1988	Jul 1991	2024-03-01	28547
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28548
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Dec 1982	Jul 1992	2024-03-01	28549
Ford	Focus i	1.8 Turbo DI / Tddi	Stufenheck	Frontantrieb	Diesel	55	75	Aug 2001	Mar 2005	2024-03-01	28562
VW	Lt 28-35 ii	2.8 TDI	Bus	Heckantrieb	Diesel	92	125	Jul 1997	May 2003	2024-03-01	28565
Volvo	V50	2.4 TDI	Kombi	Frontantrieb	Diesel	120	163	May 2007	Dec 2010	2024-03-01	28567


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **42 个输入 Ktype、48 条 READY 映射行**；其中首次创建 7 个尺寸组，另复用跨批次既有尺寸组 26 个。
* Scirocco 官方资料明确为 `4256 × 1810 × 1404 mm`，其中 1810 mm 明确是不含后视镜宽度；MiTo 官方技术资料同时确认三门车身及 `4063 × 1720 × 1446 mm`。([volkswagen.co.uk][1])
* Abarth 500 的 135 hp 普通版与 160 hp Esseesse 高度不同。本批 Ktype 28251 为 135 hp，因此采用官方普通版高度 **1480 mm**，没有误用 Esseesse 的 1485 mm。([Stellantis Media][2])
* Fiesta 组采用 3950 × 1722 × 1481 mm；资料明确 1722 mm 为不含后视镜宽度。Superb II 前期组采用 4838 × 1817 × 1462 mm。([jims-garage.co.uk][3])
* Insignia、跨改款 XC60/Fiesta/Superb、特殊版 Porsche、商用车轴距及车顶分支暂不强行映射，继续保持待闭合。

## 当前批次进度

* 输入 Ktype 总数：100
* 已处理输入 Ktype：42
* READY 映射行：48
* 剩余待闭合输入 Ktype：58
* 当前已引用尺寸组：33

  * 本轮首次创建：7
  * 复用既有缓存：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28228	28228	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	HIGH	前期标准SUV外廓。	READY
28230	28230	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	HIGH	前期标准SUV外廓。	READY
28231	28231	Coupe	Scirocco III		3	EU-VW-SCIROCCO-III-COUPE-3D-PREFL-01	HIGH	前期三门Scirocco外廓；动力差异不拆组。	READY
28232	28232	Coupe	Scirocco III		3	EU-VW-SCIROCCO-III-COUPE-3D-PREFL-01	HIGH	前期三门Scirocco外廓；动力差异不拆组。	READY
28233	28233	Coupe	Scirocco III		3	EU-VW-SCIROCCO-III-COUPE-3D-PREFL-01	HIGH	前期三门Scirocco外廓；动力差异不拆组。	READY
28234	28234	Coupe	Scirocco III		3	EU-VW-SCIROCCO-III-COUPE-3D-PREFL-01	HIGH	前期三门Scirocco外廓；动力差异不拆组。	READY
28237	28237	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	MEDIUM	三门与五门三维一致，共用前期外廓组。	READY
28239	28239	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	MEDIUM	三门与五门三维一致，共用前期外廓组。	READY
28240	28240	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	997.2后驱标准车身。	READY
28241	28241	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	997.2后驱标准车身。	READY
28248	28248	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	Type 955三门掀背外廓。	READY
28249	28249	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	Type 955三门掀背外廓。	READY
28250	28250	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	Type 955三门掀背外廓。	READY
28251	28251	Hatchback	500 (312)	312	3	EU-ABARTH-500-312-HATCHBACK-3D-01	HIGH	312三门硬顶外廓；不与500C共组。	READY
28255	28255	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	前期四门TwinDoor掀背外廓。	READY
28256	28256	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	前期四门TwinDoor掀背外廓。	READY
28262	28262	Hatchback	Ibiza IV	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	SC三门前期外廓。	READY
28263	28263	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	HIGH	997.2四驱宽体双门外廓。	READY
28276_prefl	28276	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	Ktype生产期跨越改款，按前期分支拆分。	READY
28276_facelift	28276	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	Ktype生产期跨越改款，按改款分支拆分。	READY
28277_prefl	28277	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	Ktype生产期跨越改款，按前期分支拆分。	READY
28277_facelift	28277	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	Ktype生产期跨越改款，按改款分支拆分。	READY
28278	28278	Coupe	TT II (8J)	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J Coupe统一外廓组。	READY
28279	28279	Coupe	TT II (8J)	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J Coupe统一外廓组。	READY
28283	28283	Coupe	Passat CC B6		4	EU-VW-PASSAT-CC-B6-COUPE-4D-PREFL-01	HIGH	前期四门轿跑外廓。	READY
28284	28284	Coupe	Passat CC B6		4	EU-VW-PASSAT-CC-B6-COUPE-4D-PREFL-01	HIGH	前期四门轿跑外廓。	READY
28285	28285	Coupe	Passat CC B6		4	EU-VW-PASSAT-CC-B6-COUPE-4D-PREFL-01	HIGH	前期四门轿跑外廓。	READY
28308	28308	Sedan	Primera P10	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门轿车外廓。	READY
28345_prefl	28345	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	Ktype生产期跨越改款，按前期外廓拆分。	READY
28345_facelift	28345	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	Ktype生产期跨越改款，按改款外廓拆分。	READY
28363	28363	Hatchback	MINI R53	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	JCW三门外廓。	READY
28364_3dr	28364	Hatchback	Stilo I	192	3	EU-FIAT-STILO-I-HATCHBACK-3D-01	HIGH	输入未区分门数，按三门物理外廓派生。	READY
28364_5dr	28364	Hatchback	Stilo I	192	5	EU-FIAT-STILO-I-HATCHBACK-5D-01	HIGH	输入未区分门数，按五门物理外廓派生。	READY
28369	28369	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款五门外廓。	READY
28380	28380	MPV	Scénic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV外廓。	READY
28393	28393	MPV	Grandis I		5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH	五门MPV标准外廓。	READY
28405	28405	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV外廓。	READY
28439	28439	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
28454	28454	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	MEDIUM	SRT8沿用已确认LX四门外廓组。	READY
28455	28455	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	LX四门轿车外廓。	READY
28460	28460	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	HB五门SUV外廓。	READY
28480	28480	Convertible	Golf VI Cabriolet		2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	双门敞篷外廓。	READY
28494	28494	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门轿车外廓。	READY
28506_compact	28506	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	MEDIUM	输入未区分车长，按Compact标准顶乘用外廓派生。	READY
28506_long	28506	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	MEDIUM	输入未区分车长，按Long标准顶乘用外廓派生。	READY
28506_extralong	28506	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	MEDIUM	输入未区分车长，按Extra-long标准顶乘用外廓派生。	READY
28536	28536	MPV	Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH	改款短轴乘用外廓。	READY
28567	28567	Wagon	V50 facelift	MW	5	EU-VOLVO-V50-MW-WAGON-FACELIFT-01	HIGH	MW改款五门旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-XC60-I-SUV-PREFL-01	4628	1891	1713	Volvo XC60 2009 owner's manual; Volvo Car UK technical specification	https://www.carmanualsonline.info/volvo-xc60-2009-owner/29; https://news.cision.com/volvo-car-uk/r/volvo-announces-full-technical-specification-for-the-new-xc60%2Cc4198924
EU-VW-SCIROCCO-III-COUPE-3D-PREFL-01	4256	1810	1404	Volkswagen Scirocco brochure July 2009	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/scirocco/scirocco-brochure-july-2009.pdf
EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	3950	1722	1481	Ford New Fiesta brochure; Cataloge.eu Ford Fiesta 2008 B299	https://www.jims-garage.co.uk/fd/new_ford/ebrochures/New_Fiesta_eBrochure.pdf; https://www.cataloge.eu/ford/fiesta-2008-b299
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4063	1720	1446	Alfa Romeo MiTo Technical Data 2008	https://www.alfaromeobr.com.br/assets/catalogos/Alfa-MiT-TechSpecs-2008-UK.pdf
EU-ABARTH-500-312-HATCHBACK-3D-01	3657	1627	1480	Abarth 500 Rebirth of a Legend press pack	https://www.media.stellantis.com/uk-en/abarth/press/abarth-500-rebirth-of-a-legend-press-pack
EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	4838	1817	1462	Auto-Data Skoda Superb II 2.0 TDI PD 140	https://www.auto-data.net/en/skoda-superb-ii-2.0-tdi-pd-140hp-dpf-17424
EU-VW-PASSAT-CC-B6-COUPE-4D-PREFL-01	4799	1855	1417	Volkswagen UK Passat CC press kit	https://www.vwpress.co.uk/press-kits/273
```

## 下一步优先处理

1. 先处理改款跨期与缓存冲突：Insignia A、XC60 Ktype 28229、Fiesta 长生产期行、Superb II 长生产期行、TT 敞篷和 Touareg。
2. 再闭合特殊外廓：911 Cabriolet/Targa、Cayman S Sport、Boxster 303 hp、Ferrari California、CLK 63 AMG、Jaguar及 Hummer。
3. 最后集中处理多轴距、多车顶和底盘车：Transit Tourneo、Land Rover 90/110/127、Vito、Dyna、Hilux、Trafic、L200及 VW LT。

推进信号：CONTINUE

[1]: https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/scirocco/scirocco-brochure-july-2009.pdf "https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/scirocco/scirocco-brochure-july-2009.pdf"
[2]: https://www.media.stellantis.com/uk-en/abarth/press/abarth-500-rebirth-of-a-legend-press-pack "https://www.media.stellantis.com/uk-en/abarth/press/abarth-500-rebirth-of-a-legend-press-pack"
[3]: https://www.jims-garage.co.uk/fd/new_ford/ebrochures/New_Fiesta_eBrochure.pdf "https://www.jims-garage.co.uk/fd/new_ford/ebrochures/New_Fiesta_eBrochure.pdf"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **46 条 READY 映射**，闭合 **29 个输入 Ktype**。
* Insignia A、XC60 I、Fiesta VI、Superb II、Audi TT Roadster、Touareg I 和 Mazda RX-8 的生产期跨越不同外廓，已按 `prefl` / `facelift` 拆分。
* Porsche 997.2 Carrera 与 Carrera S Cabriolet、Targa 4 与 Targa 4S 存在高度差异，分别建立尺寸组，没有按相同车身名称合并。([汽车数据网][1])
* 本轮首次建立 **17 个尺寸组**；Cayman 987、Boxster 987、TT 8J Roadster 前期、Touareg 7L 改款等直接复用已有组，没有重复输出尺寸记录。
* XC60 改款、Fiesta 改款、TT Roadster 改款及 RX-8 前后期的三维和不含后视镜宽度已闭合。([沃尔沃汽车][2])

## 当前批次进度

* 输入 Ktype 总数：100
* READY 输入 Ktype：71
* PENDING 输入 Ktype：29
* READY 映射行：94
* 当前批次累计引用尺寸组：56
* 本轮首次创建尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28225_prefl	28225	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28225_facelift	28225	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28226_prefl	28226	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28226_facelift	28226	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28227_prefl	28227	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28227_facelift	28227	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28229_prefl	28229	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	HIGH	生产期跨越改款，按前期SUV外廓拆分。	READY
28229_facelift	28229	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	生产期跨越改款，按改款SUV外廓拆分。	READY
28235_prefl	28235	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	MEDIUM	生产期跨越改款，按前期外廓拆分。	READY
28235_facelift	28235	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	MEDIUM	生产期跨越改款，按改款外廓拆分。	READY
28236_prefl	28236	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	MEDIUM	生产期跨越改款，按前期外廓拆分。	READY
28236_facelift	28236	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	MEDIUM	生产期跨越改款，按改款外廓拆分。	READY
28238_prefl	28238	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	MEDIUM	生产期跨越改款，按前期外廓拆分。	READY
28238_facelift	28238	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	MEDIUM	生产期跨越改款，按改款外廓拆分。	READY
28242	28242	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-RWD-01	HIGH	后驱Carrera敞篷外廓。	READY
28243	28243	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-RWD-01	HIGH	Carrera S敞篷高度不同，独立建组。	READY
28244	28244	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4-AWD-01	HIGH	Targa 4独立车身边界。	READY
28245	28245	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4S-AWD-01	HIGH	Targa 4S高度不同，独立建组。	READY
28246	28246	Coupe	Cayman 987.1	987C	2	EU-PORSCHE-CAYMAN-987C-COUPE-01	HIGH	S Sport沿用987C双门硬顶外廓。	READY
28247	28247	Convertible	Boxster 987.1	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	HIGH	987双门敞篷外廓。	READY
28252_prefl	28252	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28252_facelift	28252	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28253_prefl	28253	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28253_facelift	28253	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28254_prefl	28254	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28254_facelift	28254	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28257_prefl	28257	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28257_facelift	28257	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28258_prefl	28258	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28258_facelift	28258	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28259	28259	Convertible	California I		2	EU-FERRARI-CALIFORNIA-I-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
28261	28261	Hatchback	Ibiza IV	6J	5	EU-SEAT-IBIZA-IV-6J-HATCHBACK-5D-PREFL-01	HIGH	五门前期掀背外廓。	READY
28273	28273	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	MEDIUM	GH五门标准掀背外廓。	READY
28280_prefl	28280	Convertible	TT II (8J)	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	生产期跨越改款，按前期Roadster外廓拆分。	READY
28280_facelift	28280	Convertible	TT II (8J) facelift	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	生产期跨越改款，按改款Roadster外廓拆分。	READY
28281_prefl	28281	Convertible	TT II (8J)	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	生产期跨越改款，按前期Roadster外廓拆分。	READY
28281_facelift	28281	Convertible	TT II (8J) facelift	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	生产期跨越改款，按改款Roadster外廓拆分。	READY
28282_prefl	28282	Hatchback	Superb II		4	EU-SKODA-SUPERB-II-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期TwinDoor外廓拆分。	READY
28282_facelift	28282	Hatchback	Superb II facelift		4	EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款TwinDoor外廓拆分。	READY
28286_prefl	28286	SUV	Touareg I (7L)	7L	5	EU-VW-TOUAREG-I-7L-SUV-PREFL-01	HIGH	生产期跨越改款，按前期SUV外廓拆分。	READY
28286_facelift	28286	SUV	Touareg I (7L) facelift	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	生产期跨越改款，按改款SUV外廓拆分。	READY
28374	28374	Wagon	E-Class W211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款旅行车外廓。	READY
28376_prefl	28376	Coupe	RX-8	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-PREFL-01	MEDIUM	生产期跨越改款，按前期四门轿跑外廓拆分。	READY
28376_facelift	28376	Coupe	RX-8 facelift	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	MEDIUM	生产期跨越改款，按改款四门轿跑外廓拆分。	READY
28382	28382	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-SEDAN-4D-01	MEDIUM	BL四门轿车外廓。	READY
28398	28398	SUV	H3		5	EU-HUMMER-H3-SUV-5D-01	HIGH	五门SUV标准外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Volvo XC60 Dimensions official support	https://www.volvocars.com/bg/support/car/xc60/14w46/article/18f77489f78f457dc0a801e800a04016/
EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	3969	1722	1495	Automobile-Catalog 2013 Ford Fiesta 1.25 Ambiente	https://www.automobile-catalog.com/car/2013/1817075/ford_fiesta_1_25_60_ambiente.html
EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-RWD-01	4435	1808	1310	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-3.6-345hp-36725
EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-RWD-01	4435	1808	1300	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera S	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-s-3.8-385hp-36728
EU-PORSCHE-911-997-FACELIFT-TARGA-4-AWD-01	4435	1852	1310	Auto-Data Porsche 911 Targa 997 facelift Targa 4	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4-3.6-345hp-36793
EU-PORSCHE-911-997-FACELIFT-TARGA-4S-AWD-01	4435	1852	1300	Auto-Data Porsche 911 Targa 997 facelift Targa 4S	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4s-3.8-385hp-36797
EU-SKODA-SUPERB-II-HATCHBACK-FACELIFT-01	4833	1817	1462	Automobile-Catalog Skoda Superb 2.0 TDI CR 140 2013	https://www.automobile-catalog.com/car/2013/3142370/skoda_superb_2_0_tdi_cr_140.html
EU-FERRARI-CALIFORNIA-I-CONVERTIBLE-01	4562	1909	1322	Auto-Data Ferrari California 4.3 V8 460	https://www.auto-data.net/en/ferrari-california-4.3-i-v8-32v-460hp-6523
EU-SEAT-IBIZA-IV-6J-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data Seat Ibiza IV 1.9 TDI 105	https://www.auto-data.net/en/seat-ibiza-iv-1.9-tdi-105hp-dpf-13471
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475	Auto-Data Subaru Impreza III Hatchback RF 1.5	https://www.auto-data.net/en/subaru-impreza-iii-hatchback-rf-1.5-107hp-awd-automatic-16063
EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	4198	1842	1358	Auto-Data Audi TT Roadster 8J facelift 1.8 TFSI	https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-1.8-tfsi-160hp-27343
EU-VW-TOUAREG-I-7L-SUV-PREFL-01	4754	1928	1726	Auto-Data Volkswagen Touareg I 7L 2.5 TDI	https://www.auto-data.net/en/volkswagen-touareg-i-7l-2.5-tdi-174hp-4motion-tiptronic-8511
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	4888	1822	1506	Auto-Data Mercedes-Benz E-class T-modell S211 facelift E 350 CGI	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-350-cgi-292hp-7g-tronic-12931
EU-MAZDA-RX-8-SE3P-COUPE-PREFL-01	4427	1770	1341	Automobile-Catalog Mazda RX-8 2005	https://www.automobile-catalog.com/car/2005/1678910/mazda_rx-8.html
EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	4460	1770	1340	Automobile-Catalog Mazda RX-8 Sport 2009	https://www.automobile-catalog.com/car/2009/1679225/mazda_rx-8_sport_automatic.html
EU-SUBARU-LEGACY-IV-SEDAN-4D-01	4665	1730	1425	Auto-Data Subaru Legacy IV 2.0R 165	https://www.auto-data.net/en/subaru-legacy-iv-2.0r-165hp-awd-16162
EU-HUMMER-H3-SUV-5D-01	4742	1897	1872	Auto-Data Hummer H3 3.7i 245	https://www.auto-data.net/en/hummer-h3-3.7i-20v-245hp-4x4-29804
```

## 下一步优先处理

1. 闭合剩余乘用车：Bentley Continental Flying Spur、Rover 800、Explorer、CLK 63 AMG、Jaguar XK/S-Type/Mk IX/Mk X、Mitsubishi GTO及 Focus I Sedan。
2. 单独处理 Land Rover 90、110/127 的轴距和车顶物理边界。
3. 最后集中拆分商用车：Transit Tourneo、Vito/Mixto、Dyna、Hilux、Trafic、L200及 VW LT 的轴距、车顶、驾驶室和底盘分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-3.6-345hp-36725 "Porsche 911 Cabriolet (997, facelift 2008) Carrera 3.6 (345 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.volvocars.com/bg/support/car/xc60/14w46/article/18f77489f78f457dc0a801e800a04016/?utm_source=chatgpt.com "XC60 Dimensions | Volvo Support BG"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 8 个输入 Ktype，新增 19 条 READY 映射。
* Bentley Continental Flying Spur、Explorer II、Audi TTS 8J、Jaguar Mark IX 和 Focus I Sedan 首次建立尺寸组；TTS 因改款高度变化拆为前期与改款组。
* Toyota Dyna、Hilux VII 与 Renault Trafic II 直接复用跨批次既有尺寸组，未重复输出尺寸及来源。
* 剩余 21 个 Ktype 继续保持待闭合，主要集中在商用车多轴距、车顶和特殊车身版本。

## 当前批次进度

* 输入 Ktype 总数：100
* READY 输入 Ktype：79
* PENDING 输入 Ktype：21
* READY 映射行：113
* 当前批次累计引用尺寸组：75
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28260	28260	Sedan	Continental Flying Spur I	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
28332	28332	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-01	HIGH	第二代五门SUV外廓。	READY
28404_prefl	28404	Coupe	TTS 8J	8J3	3	EU-AUDI-TTS-8J-COUPE-PREFL-01	HIGH	生产期跨越改款，按前期外廓拆分。	READY
28404_facelift	28404	Coupe	TTS 8J facelift	8J3	3	EU-AUDI-TTS-8J-COUPE-FACELIFT-01	HIGH	生产期跨越改款，按改款外廓拆分。	READY
28444	28444	Sedan	Mark IX		4	EU-JAGUAR-MARK-IX-SEDAN-4D-01	HIGH	Mark IX四门轿车外廓。	READY
28514_swb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	MEDIUM	输入未区分轴距及底盘驾驶室分支。	READY
28514_swb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	MEDIUM	输入未区分轴距及栏板货箱分支。	READY
28514_mwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	MEDIUM	输入未区分轴距及底盘驾驶室分支。	READY
28514_mwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	MEDIUM	输入未区分轴距及栏板货箱分支。	READY
28514_lwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	MEDIUM	输入未区分轴距及底盘驾驶室分支。	READY
28514_lwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	MEDIUM	输入未区分轴距及栏板货箱分支。	READY
28515_single_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	输入未区分驾驶室，按前期单排两驱外廓拆分。	READY
28515_extra_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	MEDIUM	输入未区分驾驶室，按前期加长驾驶室两驱外廓拆分。	READY
28515_double_prefl	28515	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	MEDIUM	输入未区分驾驶室，按前期双排两驱外廓拆分。	READY
28515_single_facelift	28515	Pickup	Hilux VII facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	MEDIUM	生产期跨越2012改款，按单排外廓拆分。	READY
28515_extra_facelift	28515	Pickup	Hilux VII facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	MEDIUM	生产期跨越2012改款，按加长驾驶室外廓拆分。	READY
28515_double_facelift	28515	Pickup	Hilux VII facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	生产期跨越2012改款，按窄体双排两驱外廓拆分。	READY
28516	28516	Pickup	Trafic II Phase II	X83	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	MEDIUM	L2平台驾驶室外廓。	READY
28562	28562	Sedan	Focus I	DFW	4	EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	HIGH	DFW四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-4D-01	5307	1916	1479	Bentley Continental Flying Spur 2008 official brochure	https://brochureshub.com/wp-content/uploads/2020/04/Bentley_int-ContinentalFlyingSpur_2008.pdf
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-01	4788	1783	1702	Ford 1995 Explorer official brochure	https://xr793.com/wp-content/uploads/2022/12/1995-Ford-Explorer.pdf
EU-AUDI-TTS-8J-COUPE-PREFL-01	4198	1842	1352	Auto-Data Audi TTS Coupe 8J generation	https://www.auto-data.net/en/audi-tts-coupe-8j-generation-1137
EU-AUDI-TTS-8J-COUPE-FACELIFT-01	4198	1842	1345	Auto-Data Audi TTS Coupe 8J facelift generation	https://www.auto-data.net/en/audi-tts-coupe-8j-facelift-2010-generation-5254
EU-JAGUAR-MARK-IX-SEDAN-4D-01	4991	1854	1600	Automobile-Catalog 1959 Jaguar Mark IX	https://www.automobile-catalog.com/car/1959/1276190/jaguar_mark_ix.html
EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	4369	1702	1481	Auto-Data Ford Focus I Sedan generation	https://www.auto-data.net/en/ford-focus-i-sedan-generation-1649
```

## 下一步优先处理

1. 闭合剩余特殊乘用车：Rover 800、CLK 63 AMG Black Series、Jaguar XK/S-Type/Mark X、Mitsubishi GTO。
2. 处理 Land Rover 90 与 110/127 的轴距和车身边界。
3. 集中处理 Transit Tourneo、Vito/Mixto、L200及 VW LT I/II 的轴距、车顶、驾驶室和底盘分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 12 个输入 Ktype，新增 17 条 READY 映射和 13 个尺寸组。
* Transit Tourneo VE83 的 5 个动力版本共用短轴低顶乘用外廓；Vito W639 Kasten 按 Compact、Long、Extra-long及高顶分支拆分。([fordbook.ru][1])
* Rover 800 Fastback、CLK 63 AMG Black Series、Jaguar XK/S-Type R及 Mitsubishi GTO 已按实际车身或改款长度差异独立建组。([汽车目录][2])
* 剩余 9 个 Ktype，集中在 Land Rover 110/127、Jaguar Mark X、L200及 VW LT 多车身分支。

## 当前批次进度

* 输入 Ktype 总数：100
* READY 输入 Ktype：91
* PENDING 输入 Ktype：9
* READY 映射行：130
* 当前批次累计引用尺寸组：88
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28264	28264	MPV	Transit Tourneo VE83	VE83		EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo乘用外廓。	READY
28265	28265	MPV	Transit Tourneo VE83	VE83		EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo乘用外廓。	READY
28266	28266	MPV	Transit Tourneo VE83	VE83		EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo乘用外廓。	READY
28267	28267	MPV	Transit Tourneo VE83	VE83		EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo乘用外廓。	READY
28268	28268	MPV	Transit Tourneo VE83	VE83		EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo乘用外廓。	READY
28291	28291	Hatchback	800 Mk1	XX	5	EU-ROVER-800-MK1-FASTBACK-5D-01	HIGH	五门Fastback物理外廓。	READY
28360	28360	SUV	Land Rover Ninety		3	EU-LAND-ROVER-90-HARDTOP-3D-01	MEDIUM	Ninety三门硬顶封闭车身。	READY
28372	28372	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-BLACK-SERIES-COUPE-2D-01	HIGH	507 hp版本为Black Series宽体双门外廓。	READY
28400_prefl	28400	Convertible	XK II (X150)	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-PREFL-01	HIGH	生产期跨越改款，按前期敞篷外廓拆分。	READY
28400_facelift	28400	Convertible	XK II (X150) facelift	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-FACELIFT-01	HIGH	生产期跨越改款，按改款敞篷外廓拆分。	READY
28427	28427	Sedan	S-Type II		4	EU-JAGUAR-S-TYPE-II-R-SEDAN-4D-01	HIGH	S-Type R四门高性能外廓。	READY
28497_prefl	28497	Coupe	GTO	Z16A	3	EU-MITSUBISHI-GTO-Z16A-COUPE-PREFL-01	HIGH	生产期覆盖前期车身长度，按前期外廓拆分。	READY
28497_facelift	28497	Coupe	GTO facelift	Z16A	3	EU-MITSUBISHI-GTO-Z16A-COUPE-FACELIFT-01	HIGH	生产期覆盖改款车身长度，按改款外廓拆分。	READY
28507_compact_lowroof	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	MEDIUM	输入未区分车长及车顶，按Compact标准顶派生。	READY
28507_long_lowroof	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	MEDIUM	输入未区分车长及车顶，按Long标准顶派生。	READY
28507_long_highroof	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	MEDIUM	输入未区分车长及车顶，按Long高顶派生。	READY
28507_extralong_lowroof	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	MEDIUM	输入未区分车长及车顶，按Extra-long标准顶派生。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-TOURNEO-VE83-BUS-SWB-LOWROOF-01	4616	1972	1968	Ford Transit II owner manual dimensions; EngineInDetail Ford Tourneo 1994-2001	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya; https://www.engineindetail.com/cars/ford/transit/tourneo-tourneo-1994-2001
EU-ROVER-800-MK1-FASTBACK-5D-01	4693	1730	1398	Automobile-Catalog 1988 Rover 820 Fastback	https://www.automobile-catalog.com/car/1988/2997530/rover_820_fastback.html
EU-LAND-ROVER-90-HARDTOP-3D-01	3858	1790	1972	Automobile-Catalog Land-Rover 90 Hard Top 2.25; Automobile-Catalog Land-Rover 90 Hard Top V8	https://www.automobile-catalog.com/car/1985/1393700/land-rover_90_hard_top_2_25-litre.html; https://www.automobile-catalog.com/car/1985/1393745/land-rover_90_hard_top_v8.html
EU-MERCEDES-BENZ-CLK-C209-BLACK-SERIES-COUPE-2D-01	4657	1833	1365	Mercedes-Benz Public Archive CLK 63 AMG Black Series; Automobile-Catalog CLK 63 AMG Black Series	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-63-AMG-Black-Series--C-209-E-62-AMG-2007---2008.xhtml?oid=2462059; https://www.automobile-catalog.com/car/2007/1543910/mercedes-benz_clk_63_amg_black_series.html
EU-JAGUAR-XK-X150-CONVERTIBLE-PREFL-01	4791	1892	1329	Jaguar XK 2008 official brochure	https://jaguarrules.ru/wp-content/uploads/2021/12/Jaguar-XK-X150-Brochure-2008.pdf
EU-JAGUAR-XK-X150-CONVERTIBLE-FACELIFT-01	4794	1892	1329	Automobile-Catalog 2010 Jaguar XK Convertible Europe	https://www.automobile-catalog.com/car/2010/1293125/jaguar_xk_convertible.html
EU-JAGUAR-S-TYPE-II-R-SEDAN-4D-01	4905	1818	1447	Jaguar S-Type 2006 official brochure	https://directechs.blob.core.windows.net/directwirebrochures/brochure4264_0.pdf
EU-MITSUBISHI-GTO-Z16A-COUPE-PREFL-01	4560	1840	1285	Automobile-Catalog 1994 Mitsubishi 3000 GT Europe Series 1	https://www.automobile-catalog.com/car/1994/1967780/mitsubishi_3000_gt.html
EU-MITSUBISHI-GTO-Z16A-COUPE-FACELIFT-01	4570	1840	1285	Automobile-Catalog 1994 Mitsubishi 3000 GT Europe Series 2	https://www.automobile-catalog.com/car/1994/1967795/mitsubishi_3000_gt.html
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	4748	1901	1902	Mercedes-Benz Vito Panel Van Specification Sheet April 2005	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	4993	1901	1902	Mercedes-Benz Vito Panel Van Specification Sheet April 2005	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2328	Mercedes-Benz Vito Panel Van Specification Sheet April 2005	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	5223	1901	1900	Mercedes-Benz Vito Panel Van Specification Sheet April 2005	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
```

## 下一步优先处理

1. 闭合 Land Rover 110/127 与 Jaguar Mark X。
2. 拆分 Mitsubishi L200 IV 的驾驶室和改款外廓。
3. 集中处理 VW LT I/II 的载重级别、轴距、驾驶室、底盘及 Bus 分支。

推进信号：CONTINUE

[1]: https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya?utm_source=chatgpt.com "Dimensions of the car (General information / User manual / Ford Transit 2 1986-2000)"
[2]: https://www.automobile-catalog.com/car/1988/2997530/rover_820_fastback.html?utm_source=chatgpt.com "1988 Rover 820 Fastback Specs Review (73.5 kW / 100 PS ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Ktype `28359` 和 `28522`，新增 3 条 READY 映射及 3 个尺寸组。
* `28359` 按封闭车身拆为 One Ten Hard Top 与 Station Wagon；未建立 127 分支，因为同期标准 127 为四门 Crew Cab Pickup，不符合输入的封闭越野车车身边界。([汽车目录][1])
* Jaguar Mark X 3.8 已闭合为四门 Sedan，尺寸为 `5131 × 1930 × 1384 mm`，宽度明确不含后视镜。([汽车目录][2])

## 当前批次进度

* 输入 Ktype 总数：100
* READY 输入 Ktype：93
* PENDING 输入 Ktype：7
* READY 映射行：133
* 当前批次累计引用尺寸组：91
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28359_hardtop	28359	SUV	Land Rover One Ten		3	EU-LAND-ROVER-110-HARDTOP-3D-01	MEDIUM	封闭三门Hard Top物理外廓。	READY
28359_stationwagon	28359	SUV	Land Rover One Ten		5	EU-LAND-ROVER-110-STATION-WAGON-5D-01	MEDIUM	封闭五门Station Wagon物理外廓。	READY
28522	28522	Sedan	Mark X		4	EU-JAGUAR-MARK-X-SEDAN-4D-01	HIGH	Mark X 3.8四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-110-HARDTOP-3D-01	4445	1790	2035	Automobile-Catalog 1987 Land-Rover 110 Hard Top 2.5 Diesel	https://www.automobile-catalog.com/car/1987/1393910/land-rover_110_hard_top_2_5_diesel.html
EU-LAND-ROVER-110-STATION-WAGON-5D-01	4580	1790	2035	Automobile-Catalog 1985 Land-Rover 110 Station Wagon 2.5 Diesel	https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html
EU-JAGUAR-MARK-X-SEDAN-4D-01	5131	1930	1384	Automobile-Catalog 1962 Jaguar Mark X Sedan Overdrive	https://www.automobile-catalog.com/car/1962/1277795/jaguar_mark_x_sedan_overdrive.html
```

## 下一步优先处理

1. 闭合 Ktype `28517` 的 L200 IV 后驱 Single Cab，并解决 1655/1775 mm 高度与宽度口径边界。
2. 集中处理 Ktype `28543`、`28544`、`28547`、`28548`、`28549` 的 VW LT I Syncro、载重级别、轴距和平台/底盘分支。
3. 最后闭合 Ktype `28565` 的 VW LT II Bus 轴距及车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/1393910/land-rover_110_hard_top_2_5_diesel.html?utm_source=chatgpt.com "1987 Land-Rover 110 Hard Top 2.5 Diesel (man. 5)"
[2]: https://www.automobile-catalog.com/car/1962/1277810/jaguar_mark_x_sedan_automatic.html?utm_source=chatgpt.com "1962 Jaguar Mark X Sedan automatic Specs Review (198 kW / 269 PS / 265 hp) (since mid-year 1961 for North America U.S.)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Ktype `28548`、`28549`，新增 8 条 READY 映射及 4 个尺寸组。
* 两个 Ktype 均按同期 LT I 4x4 的单排栏板、双排栏板、单排底盘驾驶室和双排底盘驾驶室拆分；相同物理分支跨 Ktype 复用同一尺寸组。
* 1991 年 Volkswagen LT 4x4 官方资料确认该系列采用 2950 mm 轴距，并分别给出上述四种车身的完整外廓尺寸。
* `28517`、`28543`、`28544`、`28547`、`28565` 尚有车身边界或尺寸口径冲突，未强行建立尺寸组。

## 当前批次进度

* 输入 Ktype 总数：100
* READY 输入 Ktype：95
* PENDING 输入 Ktype：5
* READY 映射行：141
* 当前批次累计引用尺寸组：95
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28548_pickup_singlecab	28548	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	输入未区分驾驶室，按单排栏板外廓拆分。	READY
28548_pickup_doublecab	28548	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	输入未区分驾驶室，按双排栏板外廓拆分。	READY
28548_chassis_singlecab	28548	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	MEDIUM	输入未区分车身，按单排底盘驾驶室外廓拆分。	READY
28548_chassis_doublecab	28548	Pickup	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	MEDIUM	输入未区分车身，按双排底盘驾驶室外廓拆分。	READY
28549_pickup_singlecab	28549	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	输入未区分驾驶室，按单排栏板外廓拆分。	READY
28549_pickup_doublecab	28549	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	输入未区分驾驶室，按双排栏板外廓拆分。	READY
28549_chassis_singlecab	28549	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	MEDIUM	输入未区分车身，按单排底盘驾驶室外廓拆分。	READY
28549_chassis_doublecab	28549	Pickup	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	MEDIUM	输入未区分车身，按双排底盘驾驶室外廓拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	5630	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	5330	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
```

## 下一步优先处理

1. 闭合 `28517` 的 L200 IV 后驱单排车身，解决改款前后长度及 2WD 高度口径。
2. 解决 `28543`、`28544` 的输入车型级别与同期 LT 4x4 官方 LT40/45 范围冲突。
3. 闭合 `28547` 的 LT I 后驱栏板/底盘轴距分支，以及 `28565` 的 LT II Bus 轴距与车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 9 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	4063	1720	1446
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342
EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	4198	1842	1350
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	4174	1702	1430
EU-FORD-FOCUS-I-DNW-WAGON-5D-FACELIFT-01	4454	1702	1467
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800
EU-FORD-USA-EXPLORER-IV-U251-SUV-5D-01	4912	1872	1834
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675
EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	4794	1892	1329
EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	4794	1892	1322
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	3961	1683	1432
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	3958	1683	1432
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	3961	1683	1426
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	3937	1683	1426
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	3723	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	3729	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	3714	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	3723	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655
EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	5010	1695	1755
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-WAGON-FACELIFT-01	4913	1856	1520
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	4435	1830	1295
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-S-TARGA-2D-01	4147	1610	1320
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-FACELIFT-01	4342	1801	1292
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-BASE-01	4347	1801	1304
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-S-01	4347	1801	1306
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-RENAULT-TRAFIC-II-BUS-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-BUS-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	5036	1904	1973
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967
EU-RENAULT-TRAFIC-II-VAN-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-VAN-L1H2-01	4782	1904	2465
EU-RENAULT-TRAFIC-II-VAN-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-VAN-L2H2-01	5182	1904	2464
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	4088	1693	1441
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	4061	1693	1445
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	4082	1693	1441
EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	4066	1693	1424
EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510
EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	4340	1690	1405
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	5260	1760	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	5260	1835	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	5255	1760	1695
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	5130	1760	1810
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	5255	1835	1810
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	5260	1760	1835
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	5255	1835	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	5255	1760	1795
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504
EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	4799	1855	1417
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	81	110	Jul 2008	Mar 2017	2024-03-01	28225
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	96	131	Jul 2008	Mar 2017	2024-03-01	28226
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	118	160	Jul 2008	Mar 2017	2024-03-01	28227
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	210	286	May 2008	Dec 2010	2024-03-01	28228
Volvo	Xc60 i	2.4 D / D3 / D4 AWD	SUV	Allrad	Diesel	120	163	May 2008	Feb 2017	2024-03-01	28229
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	136	185	May 2008	Dec 2009	2024-03-01	28230
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	118	160	May 2008	Nov 2017	2024-03-01	28231
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	90	122	Aug 2008	Nov 2017	2024-03-01	28232
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Aug 2008	Nov 2017	2024-03-01	28233
VW	Scirocco	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	May 2008	Nov 2009	2024-03-01	28234
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2008	Apr 2017	2024-03-01	28235
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	60	82	Jun 2008	Apr 2017	2024-03-01	28236
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2008	Dec 2012	2024-03-01	28237
Ford	Fiesta vi	1.4	Schrägheck	Frontantrieb	Benzin	71	97	Oct 2008	Dec 2017	2024-03-01	28238
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2008	Sep 2012	2024-03-01	28239
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28240
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28241
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28242
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28243
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	254	345	Oct 2008	Dec 2012	2024-03-01	28244
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	283	385	Oct 2008	Dec 2012	2024-03-01	28245
Porsche	Cayman	S 3,4 Sport	Coupe	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2012	2024-03-01	28246
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2009	2024-03-01	28247
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	70	95	Sep 2008	Aug 2013	2024-03-01	28248
Alfa Romeo	Mito	1.4 Tjet	Schrägheck	Frontantrieb	Benzin	114	155	Aug 2008	Jun 2011	2024-03-01	28249
Alfa Romeo	Mito	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	88	120	Aug 2008	Aug 2015	2024-03-01	28250
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2008	-	2024-03-01	28251
Skoda	Superb ii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 2008	May 2015	2024-03-01	28252
Skoda	Superb ii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Mar 2008	May 2015	2024-03-01	28253
Skoda	Superb ii	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	118	160	Nov 2008	May 2015	2024-03-01	28254
Skoda	Superb ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Nov 2010	2024-03-01	28255
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Mar 2008	May 2010	2024-03-01	28256
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Jul 2008	May 2015	2024-03-01	28257
Skoda	Superb ii	3.6 FSI 4X4	Schrägheck	Allrad	Benzin	191	260	Nov 2008	May 2015	2024-03-01	28258
Ferrari	California	4.3	Cabriolet	Heckantrieb	Benzin	338	460	Jul 2008	-	2024-03-01	28259
Bentley	Continental	6.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	449	610	Sep 2008	Feb 2013	2024-03-01	28260
Seat	Ibiza iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Jun 2010	2024-03-01	28261
Seat	Ibiza iv sc	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jul 2008	Jun 2010	2025-06-01	28262
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	283	385	Jun 2008	Dec 2012	2024-03-01	28263
Ford	Transit tourneo	2	Bus	Heckantrieb	Benzin	84	114	Nov 1994	Dec 2000	2024-03-01	28264
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	51	69	Nov 1994	Dec 2000	2024-03-01	28265
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	56	76	Nov 1994	Dec 2000	2024-03-01	28266
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Nov 1994	Dec 2000	2024-03-01	28267
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Apr 1998	Dec 2000	2024-03-01	28268
Subaru	Impreza	1.5 F	Schrägheck	Frontantrieb	Benzin	79	107	Sep 2007	Mar 2012	2024-03-01	28273
Audi	A4 b8 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	132	180	Jun 2008	Dec 2015	2024-03-01	28276
Audi	A4 b8 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	155	211	Jun 2008	Dec 2015	2024-03-01	28277
Audi	Tt	1.8 Tfsi	Coupe	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28278
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28279
Audi	Tt	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28280
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28281
Skoda	Superb ii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	125	170	Sep 2008	May 2015	2024-03-01	28282
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	125	170	Jun 2008	Jan 2012	2024-03-01	28283
VW	Passat cc b6	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Jun 2008	Jan 2012	2024-03-01	28284
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	100	136	Jun 2008	May 2011	2024-03-01	28285
VW	Touareg	2.5 R5 TDI	SUV	Allrad	Diesel	120	163	Aug 2003	May 2010	2024-03-01	28286
Rover	800	2	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1987	Sep 1988	2024-03-01	28291
Nissan	Primera	2.0 4X4	Stufenheck	Allrad	Benzin	110	150	Mar 1991	Apr 1993	2024-03-01	28308
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	115	156	Nov 1994	Aug 1996	2024-03-01	28332
Fiat	Multipla	1.6	Großraumlimousine	Frontantrieb	Benzin	76	103	Sep 2000	Jun 2010	2024-03-01	28345
Land Rover	110/127	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Jun 1984	Aug 1987	2024-03-01	28359
Land Rover	90	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	52	71	Jan 1984	Aug 1987	2024-03-01	28360
Mini	Mini	John Cooper Works	Schrägheck	Frontantrieb	Benzin	160	218	Mar 2006	Sep 2006	2024-03-01	28363
Fiat	Stilo	1.6	Schrägheck	Frontantrieb	Benzin	100	136	Apr 2005	Nov 2006	2025-11-01	28364
Renault	Vel satis	3.5	Schrägheck	Frontantrieb	Benzin	170	231	Oct 2004	Aug 2009	2025-12-01	28369
Mercedes-benz	Clk	CLK 63 AMG	Coupe	Heckantrieb	Benzin	373	507	May 2007	May 2009	2024-03-01	28372
Mercedes-benz	E-Klasse	350 CGI	Kombi	Heckantrieb	Benzin	215	292	May 2006	Jul 2009	2024-03-01	28374
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	177	241	Nov 2003	Jun 2012	2024-03-01	28376
Renault	Scénic ii	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Jun 2006	Nov 2008	2024-03-01	28380
Subaru	Legacy iv	2.0 AWD	Stufenheck	Allrad	Benzin	121	165	Jun 2005	Apr 2009	2024-03-01	28382
Mitsubishi	Grandis	2.4 Mivec	Großraumlimousine	Frontantrieb	Benzin	130	177	Apr 2004	Dec 2011	2024-03-01	28393
Hummer	Hummer h3	3.7 4WD	Geländewagen geschlossen	Allrad	Benzin	180	245	Sep 2006	-	2024-03-01	28398
Jaguar	Xk ii	3.6	Cabriolet	Heckantrieb	Benzin	190	258	Oct 2007	Jul 2014	2024-03-01	28400
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	195	265	May 2008	Jun 2014	2024-03-01	28404
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	28405
Jaguar	S-Type ii	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	298	405	Nov 2001	Dec 2008	2024-03-01	28427
Honda	Cr-V iii	2.4	SUV	Frontantrieb	Benzin	125	170	Apr 2007	Dec 2012	2025-12-01	28439
Jaguar	Mk ix	3.8	Stufenheck	Heckantrieb	Benzin	164	223	Oct 1958	Jul 1961	2024-03-01	28444
Dodge	Charger	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Sep 2005	Dec 2010	2024-03-01	28454
Dodge	Charger	2.7	Stufenheck	Heckantrieb	Benzin	141	192	Apr 2006	Dec 2010	2024-03-01	28455
Dodge	Durango	4.7 AWD	SUV	Allrad	Benzin	172	234	Nov 2003	Dec 2009	2024-03-01	28460
VW	Golf vi	2.0 TSI	Cabriolet	Frontantrieb	Benzin	162	220	Nov 2013	May 2016	2024-03-01	28480
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1993	Sep 1997	2024-03-01	28494
Mitsubishi	Gto	3.0 AWD	Coupe	Allrad	Benzin	210	286	Jan 1994	Dec 2000	2024-03-01	28497
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	85	116	Aug 2005	-	2025-06-01	28506
Mercedes-benz	Vito / mixto	109 CDI	Kasten	Heckantrieb	Diesel	70	95	Aug 2006	Aug 2014	2025-12-01	28507
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Sep 2006	-	2024-03-01	28514
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	75	102	Mar 2005	May 2015	2024-03-01	28515
Renault	Trafic ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2007	-	2024-03-01	28516
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	28517
Jaguar	Mk x i	3.8	Stufenheck	Heckantrieb	Benzin	197	268	Oct 1961	Oct 1964	2024-05-01	28522
Fiat	Doblo	1.3 JTD	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2005	-	2024-03-01	28536
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28543
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Aug 1991	Jul 1992	2024-03-01	28544
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	68	92	Aug 1988	Jul 1991	2024-03-01	28547
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28548
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Dec 1982	Jul 1992	2024-03-01	28549
Ford	Focus i	1.8 Turbo DI / Tddi	Stufenheck	Frontantrieb	Diesel	55	75	Aug 2001	Mar 2005	2024-03-01	28562
VW	Lt 28-35 ii	2.8 TDI	Bus	Heckantrieb	Diesel	92	125	Jul 1997	May 2003	2024-03-01	28565
Volvo	V50	2.4 TDI	Kombi	Frontantrieb	Diesel	120	163	May 2007	Dec 2010	2024-03-01	28567


--- 新建对话（分支降级） / Round 9 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6b7773-eefc-83ea-8189-cda9f1e508ee
新对话：https://chatgpt.com/c/6a6d9b21-0724-83ea-8486-d8e9b454a8cb

--- Round 9 / checkpoint 续跑 ---
## 更新点

* 闭合 Ktype `28360`：Land Rover Ninety 90 的封闭式车身包含 Hard Top 与 Station Wagon，两者长宽一致但高度分别为 1972 mm、1963 mm，拆为两个物理分支。宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Ktype `28517`：确认为第四代 L200 `KA4T`、后驱、单排驾驶室、2 门；尺寸采用 5040×1750×1655 mm。Mitsubishi 资料明确 `KA4T` 对应 2WD Single Cab，两个规格数据库给出的三维一致。([PartSouq][2])
* 本轮新增 3 条 READY 映射、3 个尺寸组。
* 剩余阻塞仅为 VW LT：`28543`、`28544`、`28547`。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：97
* PENDING Ktype：3
* READY 映射行：144
* 已确认尺寸组：98
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28360_hardtop	28360	SUV	Land Rover Ninety		3	EU-LAND-ROVER-NINETY-HARDTOP-3D-01	HIGH	Ninety 90三门Hard Top封闭式车身。	READY
28360_stationwagon	28360	SUV	Land Rover Ninety		3	EU-LAND-ROVER-NINETY-STATION-WAGON-3D-01	HIGH	Ninety 90三门Station Wagon，车高与Hard Top不同。	READY
28517	28517	Pickup	Mitsubishi L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-PICKUP-01	HIGH	KA4T后驱单排驾驶室外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-NINETY-HARDTOP-3D-01	3858	1790	1972	Automobile-Catalog 1985 Land-Rover 90 Hard Top 2.25-Litre	https://www.automobile-catalog.com/car/1985/1393700/land-rover_90_hard_top_2_25-litre.html
EU-LAND-ROVER-NINETY-STATION-WAGON-3D-01	3858	1790	1963	Automobile-Catalog 1984 Land-Rover 90 Station Wagon 2.25-Litre	https://www.automobile-catalog.com/car/1984/1393370/land-rover_90_station_wagon_2_25-litre.html
EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-PICKUP-01	5040	1750	1655	Autoboom Mitsubishi L200 IV Single Cab 2.5 MT diesel; Drive.Place Mitsubishi L200 IV Single Cab 136	https://autoboom.co.il/en/catalog/cars/mitsubishi/l200/4-generation/pickup-single-cab/32917; https://mitsubishi.drive.place/l200/iv/group_pickup_2dr/170719
```

## 下一步优先处理

1. 对 `28543`、`28544` 核定 LT 28–35 Syncro 是否应复用已闭合的 LT I 4×4 长轴单排、双排及底盘驾驶室尺寸组。
2. 对 `28547` 按官方 LT 技术资料拆分 LT 40–55 后驱的单排/双排、Pickup/Chassis-cab 与轴距分支，避免把 2950 mm 和 3650 mm 轴距外廓混为一组。官方资料已显示这些分支存在明显的长度、宽度和高度差异。([大众巴士网][3])

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/1393700/land-rover_90_hard_top_2_25-litre.html?utm_source=chatgpt.com "1985 Land-Rover 90 Hard Top 2.25-Litre Specs Review (55.2 kW / 75 PS / 74 hp) (up to mid-year 1985 for Europe )"
[2]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MN134131XB&ssd=%24%2AKwHS5vfc2aCFkbDVua7B2Iqevrmn1tnU1cfBzoihncWJw9yKzNvHzMOFxdrDpdyJhOfQ0dOjws3EiZuNiaug0rPCzcSH1ZWRwqmjqa27tNybygAAAADX7_cq%24&utm_source=chatgpt.com "Body | Mitsubishi L200,L200 SPORTERO General (EXPORT) KA4T | Parts Catalogs | PartSouq"
[3]: https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf "https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / checkpoint 续跑 ---
## 更新点

* Ktype `28543`、`28544` 已闭合。
* 两者覆盖的四个物理分支与当前批次既有 LT I 4×4 尺寸组完全重合，直接复用，不重复创建尺寸组。
* 本轮新增 8 条 READY 映射。
* 剩余 PENDING：Ktype `28547`。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：99
* PENDING Ktype：1
* READY 映射：152
* 已确认尺寸组：98
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28543_pickup_singlecab	28543	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	长轴单排驾驶室平板车分支。	READY
28543_pickup_doublecab	28543	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	长轴双排驾驶室平板车分支。	READY
28543_chassis_singlecab	28543	Chassis Cab	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	HIGH	长轴单排驾驶室底盘分支。	READY
28543_chassis_doublecab	28543	Chassis Cab	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
28544_pickup_singlecab	28544	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	长轴单排驾驶室平板车分支。	READY
28544_pickup_doublecab	28544	Pickup	LT I 4x4			EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	长轴双排驾驶室平板车分支。	READY
28544_chassis_singlecab	28544	Chassis Cab	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	HIGH	长轴单排驾驶室底盘分支。	READY
28544_chassis_doublecab	28544	Chassis Cab	LT I 4x4			EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

* 闭合 Ktype `28547`：按 LT 40–55 I 后驱的平板车、底盘驾驶室、单排/双排及 2950 mm、3650 mm 轴距边界完成派生映射和尺寸组建档。
* PENDING 清零后立即进行一次机械检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 11 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	4063	1720	1446
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342
EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	4198	1842	1350
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	4174	1702	1430
EU-FORD-FOCUS-I-DNW-WAGON-5D-FACELIFT-01	4454	1702	1467
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800
EU-FORD-USA-EXPLORER-IV-U251-SUV-5D-01	4912	1872	1834
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675
EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	4794	1892	1329
EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	4794	1892	1322
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	3961	1683	1432
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	3958	1683	1432
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	3961	1683	1426
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	3937	1683	1426
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	3723	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	3729	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	3714	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	3723	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655
EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	5010	1695	1755
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-WAGON-FACELIFT-01	4913	1856	1520
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	4435	1830	1295
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-S-TARGA-2D-01	4147	1610	1320
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-FACELIFT-01	4342	1801	1292
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-BASE-01	4347	1801	1304
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-S-01	4347	1801	1306
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-RENAULT-TRAFIC-II-BUS-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-BUS-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	5036	1904	1973
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967
EU-RENAULT-TRAFIC-II-VAN-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-VAN-L1H2-01	4782	1904	2465
EU-RENAULT-TRAFIC-II-VAN-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-VAN-L2H2-01	5182	1904	2464
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	4088	1693	1441
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	4061	1693	1445
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	4082	1693	1441
EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	4066	1693	1424
EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510
EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	4340	1690	1405
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	5260	1760	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	5260	1835	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	5255	1760	1695
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	5130	1760	1810
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	5255	1835	1810
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	5260	1760	1835
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	5255	1835	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	5255	1760	1795
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504
EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	4799	1855	1417
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	81	110	Jul 2008	Mar 2017	2024-03-01	28225
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	96	131	Jul 2008	Mar 2017	2024-03-01	28226
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	118	160	Jul 2008	Mar 2017	2024-03-01	28227
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	210	286	May 2008	Dec 2010	2024-03-01	28228
Volvo	Xc60 i	2.4 D / D3 / D4 AWD	SUV	Allrad	Diesel	120	163	May 2008	Feb 2017	2024-03-01	28229
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	136	185	May 2008	Dec 2009	2024-03-01	28230
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	118	160	May 2008	Nov 2017	2024-03-01	28231
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	90	122	Aug 2008	Nov 2017	2024-03-01	28232
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Aug 2008	Nov 2017	2024-03-01	28233
VW	Scirocco	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	May 2008	Nov 2009	2024-03-01	28234
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2008	Apr 2017	2024-03-01	28235
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	60	82	Jun 2008	Apr 2017	2024-03-01	28236
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2008	Dec 2012	2024-03-01	28237
Ford	Fiesta vi	1.4	Schrägheck	Frontantrieb	Benzin	71	97	Oct 2008	Dec 2017	2024-03-01	28238
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2008	Sep 2012	2024-03-01	28239
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28240
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28241
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28242
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28243
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	254	345	Oct 2008	Dec 2012	2024-03-01	28244
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	283	385	Oct 2008	Dec 2012	2024-03-01	28245
Porsche	Cayman	S 3,4 Sport	Coupe	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2012	2024-03-01	28246
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2009	2024-03-01	28247
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	70	95	Sep 2008	Aug 2013	2024-03-01	28248
Alfa Romeo	Mito	1.4 Tjet	Schrägheck	Frontantrieb	Benzin	114	155	Aug 2008	Jun 2011	2024-03-01	28249
Alfa Romeo	Mito	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	88	120	Aug 2008	Aug 2015	2024-03-01	28250
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2008	-	2024-03-01	28251
Skoda	Superb ii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 2008	May 2015	2024-03-01	28252
Skoda	Superb ii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Mar 2008	May 2015	2024-03-01	28253
Skoda	Superb ii	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	118	160	Nov 2008	May 2015	2024-03-01	28254
Skoda	Superb ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Nov 2010	2024-03-01	28255
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Mar 2008	May 2010	2024-03-01	28256
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Jul 2008	May 2015	2024-03-01	28257
Skoda	Superb ii	3.6 FSI 4X4	Schrägheck	Allrad	Benzin	191	260	Nov 2008	May 2015	2024-03-01	28258
Ferrari	California	4.3	Cabriolet	Heckantrieb	Benzin	338	460	Jul 2008	-	2024-03-01	28259
Bentley	Continental	6.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	449	610	Sep 2008	Feb 2013	2024-03-01	28260
Seat	Ibiza iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Jun 2010	2024-03-01	28261
Seat	Ibiza iv sc	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jul 2008	Jun 2010	2025-06-01	28262
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	283	385	Jun 2008	Dec 2012	2024-03-01	28263
Ford	Transit tourneo	2	Bus	Heckantrieb	Benzin	84	114	Nov 1994	Dec 2000	2024-03-01	28264
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	51	69	Nov 1994	Dec 2000	2024-03-01	28265
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	56	76	Nov 1994	Dec 2000	2024-03-01	28266
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Nov 1994	Dec 2000	2024-03-01	28267
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Apr 1998	Dec 2000	2024-03-01	28268
Subaru	Impreza	1.5 F	Schrägheck	Frontantrieb	Benzin	79	107	Sep 2007	Mar 2012	2024-03-01	28273
Audi	A4 b8 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	132	180	Jun 2008	Dec 2015	2024-03-01	28276
Audi	A4 b8 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	155	211	Jun 2008	Dec 2015	2024-03-01	28277
Audi	Tt	1.8 Tfsi	Coupe	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28278
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28279
Audi	Tt	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28280
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28281
Skoda	Superb ii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	125	170	Sep 2008	May 2015	2024-03-01	28282
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	125	170	Jun 2008	Jan 2012	2024-03-01	28283
VW	Passat cc b6	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Jun 2008	Jan 2012	2024-03-01	28284
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	100	136	Jun 2008	May 2011	2024-03-01	28285
VW	Touareg	2.5 R5 TDI	SUV	Allrad	Diesel	120	163	Aug 2003	May 2010	2024-03-01	28286
Rover	800	2	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1987	Sep 1988	2024-03-01	28291
Nissan	Primera	2.0 4X4	Stufenheck	Allrad	Benzin	110	150	Mar 1991	Apr 1993	2024-03-01	28308
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	115	156	Nov 1994	Aug 1996	2024-03-01	28332
Fiat	Multipla	1.6	Großraumlimousine	Frontantrieb	Benzin	76	103	Sep 2000	Jun 2010	2024-03-01	28345
Land Rover	110/127	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Jun 1984	Aug 1987	2024-03-01	28359
Land Rover	90	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	52	71	Jan 1984	Aug 1987	2024-03-01	28360
Mini	Mini	John Cooper Works	Schrägheck	Frontantrieb	Benzin	160	218	Mar 2006	Sep 2006	2024-03-01	28363
Fiat	Stilo	1.6	Schrägheck	Frontantrieb	Benzin	100	136	Apr 2005	Nov 2006	2025-11-01	28364
Renault	Vel satis	3.5	Schrägheck	Frontantrieb	Benzin	170	231	Oct 2004	Aug 2009	2025-12-01	28369
Mercedes-benz	Clk	CLK 63 AMG	Coupe	Heckantrieb	Benzin	373	507	May 2007	May 2009	2024-03-01	28372
Mercedes-benz	E-Klasse	350 CGI	Kombi	Heckantrieb	Benzin	215	292	May 2006	Jul 2009	2024-03-01	28374
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	177	241	Nov 2003	Jun 2012	2024-03-01	28376
Renault	Scénic ii	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Jun 2006	Nov 2008	2024-03-01	28380
Subaru	Legacy iv	2.0 AWD	Stufenheck	Allrad	Benzin	121	165	Jun 2005	Apr 2009	2024-03-01	28382
Mitsubishi	Grandis	2.4 Mivec	Großraumlimousine	Frontantrieb	Benzin	130	177	Apr 2004	Dec 2011	2024-03-01	28393
Hummer	Hummer h3	3.7 4WD	Geländewagen geschlossen	Allrad	Benzin	180	245	Sep 2006	-	2024-03-01	28398
Jaguar	Xk ii	3.6	Cabriolet	Heckantrieb	Benzin	190	258	Oct 2007	Jul 2014	2024-03-01	28400
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	195	265	May 2008	Jun 2014	2024-03-01	28404
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	28405
Jaguar	S-Type ii	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	298	405	Nov 2001	Dec 2008	2024-03-01	28427
Honda	Cr-V iii	2.4	SUV	Frontantrieb	Benzin	125	170	Apr 2007	Dec 2012	2025-12-01	28439
Jaguar	Mk ix	3.8	Stufenheck	Heckantrieb	Benzin	164	223	Oct 1958	Jul 1961	2024-03-01	28444
Dodge	Charger	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Sep 2005	Dec 2010	2024-03-01	28454
Dodge	Charger	2.7	Stufenheck	Heckantrieb	Benzin	141	192	Apr 2006	Dec 2010	2024-03-01	28455
Dodge	Durango	4.7 AWD	SUV	Allrad	Benzin	172	234	Nov 2003	Dec 2009	2024-03-01	28460
VW	Golf vi	2.0 TSI	Cabriolet	Frontantrieb	Benzin	162	220	Nov 2013	May 2016	2024-03-01	28480
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1993	Sep 1997	2024-03-01	28494
Mitsubishi	Gto	3.0 AWD	Coupe	Allrad	Benzin	210	286	Jan 1994	Dec 2000	2024-03-01	28497
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	85	116	Aug 2005	-	2025-06-01	28506
Mercedes-benz	Vito / mixto	109 CDI	Kasten	Heckantrieb	Diesel	70	95	Aug 2006	Aug 2014	2025-12-01	28507
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Sep 2006	-	2024-03-01	28514
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	75	102	Mar 2005	May 2015	2024-03-01	28515
Renault	Trafic ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2007	-	2024-03-01	28516
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	28517
Jaguar	Mk x i	3.8	Stufenheck	Heckantrieb	Benzin	197	268	Oct 1961	Oct 1964	2024-05-01	28522
Fiat	Doblo	1.3 JTD	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2005	-	2024-03-01	28536
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28543
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Aug 1991	Jul 1992	2024-03-01	28544
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	68	92	Aug 1988	Jul 1991	2024-03-01	28547
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28548
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Dec 1982	Jul 1992	2024-03-01	28549
Ford	Focus i	1.8 Turbo DI / Tddi	Stufenheck	Frontantrieb	Diesel	55	75	Aug 2001	Mar 2005	2024-03-01	28562
VW	Lt 28-35 ii	2.8 TDI	Bus	Heckantrieb	Diesel	92	125	Jul 1997	May 2003	2024-03-01	28565
Volvo	V50	2.4 TDI	Kombi	Frontantrieb	Diesel	120	163	May 2007	Dec 2010	2024-03-01	28567


--- 新建对话（分支降级） / Round 11 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6d9b21-0724-83ea-8486-d8e9b454a8cb
新对话：https://chatgpt.com/c/6a6d9fc4-e0a0-83ea-9516-5111e4043604

--- Round 11 / checkpoint 续跑 ---
## 更新点

- 已闭合最后一项 `Ktype 28547`。该 Ktype 对应 VW LT 40–55 I 2.4 TD 平台/底盘车型，依据单排/双排、栏板/底盘、2950/3650 mm 轴距及 LT40–LT55 高度差异，拆分为 16 个物理外廓分支。大众巴士网+4Brembo Parts+4大众巴士网+4
- 已完成固定表头、主键唯一性、尺寸组引用闭合、正整数尺寸、来源字段及下载文件检查。

## 当前批次进度

- 输入 Ktype：100
- READY 映射：168
- PENDING 映射：0
- 已确认尺寸组：113
- Ktype 映射表：严格 10 列
- DIMENSION_GROUP 表：严格 6 列
- `id` 与 `DIMENSION_GROUP_ID` 均唯一
- 映射引用与尺寸组集合完全闭合
- 无孤立尺寸组
- 两个指定 TSV 文件已生成

## 最终完整 Ktype 映射 TSV

```
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28225_prefl	28225	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28225_facelift	28225	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28226_prefl	28226	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28226_facelift	28226	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28227_prefl	28227	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	生产期跨越改款，按前期轿车外廓拆分。	READY
28227_facelift	28227	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	生产期跨越改款，按改款轿车外廓拆分。	READY
28228	28228	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
28229	28229	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
28230	28230	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
28231	28231	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	三门前期轿跑外廓。	READY
28232	28232	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	三门前期轿跑外廓。	READY
28233	28233	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	三门前期轿跑外廓。	READY
28234	28234	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	三门前期轿跑外廓。	READY
28235_prefl	28235	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，前期三/五门外廓共组。	READY
28235_facelift	28235	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，改款三/五门外廓共组。	READY
28236_prefl	28236	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，前期三/五门外廓共组。	READY
28236_facelift	28236	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，改款三/五门外廓共组。	READY
28237	28237	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	HIGH	生产期止于改款前，三/五门外廓共组。	READY
28238_prefl	28238	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，前期三/五门外廓共组。	READY
28238_facelift	28238	Hatchback	Fiesta VI facelift			EU-FORD-FIESTA-VI-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，改款三/五门外廓共组。	READY
28239	28239	Hatchback	Fiesta VI			EU-FORD-FIESTA-VI-HATCHBACK-PREFL-01	HIGH	生产期止于改款前，三/五门外廓共组。	READY
28240	28240	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	后驱Carrera轿跑外廓。	READY
28241	28241	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	后驱Carrera轿跑外廓。	READY
28242	28242	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-RWD-01	HIGH	后驱Carrera敞篷外廓。	READY
28243	28243	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-RWD-01	HIGH	后驱Carrera S敞篷外廓。	READY
28244	28244	Coupe	911 Targa (997.2)	997	2	EU-PORSCHE-911-997-TARGA-4-01	HIGH	四驱宽体Targa 4外廓。	READY
28245	28245	Coupe	911 Targa (997.2)	997	2	EU-PORSCHE-911-997-TARGA-4S-01	HIGH	四驱宽体Targa 4S外廓。	READY
28246	28246	Coupe	Cayman 987C	987C	3	EU-PORSCHE-CAYMAN-987C-COUPE-01	HIGH	Cayman S Sport三门轿跑外廓。	READY
28247	28247	Convertible	Boxster 987	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	HIGH	Boxster S前期敞篷外廓。	READY
28248	28248	Hatchback	MiTo 955	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	三门掀背外廓。	READY
28249	28249	Hatchback	MiTo 955	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	三门掀背外廓。	READY
28250	28250	Hatchback	MiTo 955	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	三门掀背外廓。	READY
28251	28251	Hatchback	500 (312)	312	3	EU-ABARTH-500-312-HATCHBACK-3D-01	HIGH	Abarth 500三门掀背外廓。	READY
28252_prefl	28252	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28252_facelift	28252	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28253_prefl	28253	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28253_facelift	28253	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28254_prefl	28254	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28254_facelift	28254	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28255	28255	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期止于前期车型。	READY
28256	28256	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期止于前期车型。	READY
28257_prefl	28257	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28257_facelift	28257	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28258_prefl	28258	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28258_facelift	28258	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28259	28259	Convertible	California F149	F149	2	EU-FERRARI-CALIFORNIA-F149-CONVERTIBLE-2D-01	HIGH	硬顶敞篷外廓。	READY
28260	28260	Sedan	Continental Flying Spur	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-SPEED-SEDAN-4D-01	HIGH	Flying Spur Speed四门轿车外廓。	READY
28261	28261	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	五门掀背前期外廓。	READY
28262	28262	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	SC三门掀背前期外廓。	READY
28263	28263	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	HIGH	Carrera 4S四驱宽体轿跑外廓。	READY
28264	28264	MPV	Transit Mk4 Tourneo		4	EU-FORD-TRANSIT-MK4-TOURNEO-BUS-SWB-01	MEDIUM	Tourneo短轴乘用客车外廓。	READY
28265	28265	MPV	Transit Mk4 Tourneo		4	EU-FORD-TRANSIT-MK4-TOURNEO-BUS-SWB-01	MEDIUM	Tourneo短轴乘用客车外廓。	READY
28266	28266	MPV	Transit Mk4 Tourneo		4	EU-FORD-TRANSIT-MK4-TOURNEO-BUS-SWB-01	MEDIUM	Tourneo短轴乘用客车外廓。	READY
28267	28267	MPV	Transit Mk4 Tourneo		4	EU-FORD-TRANSIT-MK4-TOURNEO-BUS-SWB-01	MEDIUM	Tourneo短轴乘用客车外廓。	READY
28268	28268	MPV	Transit Mk4 Tourneo		4	EU-FORD-TRANSIT-MK4-TOURNEO-BUS-SWB-01	MEDIUM	Tourneo短轴乘用客车外廓。	READY
28273	28273	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	HIGH	GH五门掀背外廓。	READY
28276_prefl	28276	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨越改款，按前期旅行车外廓拆分。	READY
28276_facelift	28276	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨越改款，改款外廓三维相同但代际边界独立。	READY
28277_prefl	28277	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨越改款，按前期旅行车外廓拆分。	READY
28277_facelift	28277	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨越改款，改款外廓三维相同但代际边界独立。	READY
28278	28278	Coupe	TT 8J	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	TT 8J三门轿跑外廓。	READY
28279	28279	Coupe	TT 8J	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	TT 8J三门轿跑外廓。	READY
28280	28280	Convertible	TT 8J	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	TT 8J两门敞篷外廓。	READY
28281	28281	Convertible	TT 8J	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	TT 8J两门敞篷外廓。	READY
28282_prefl	28282	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-PREFL-01	HIGH	生产期跨越改款，按前期双段式尾门外廓拆分。	READY
28282_facelift	28282	Hatchback	Superb II facelift	3T4	5	EU-SKODA-SUPERB-II-3T4-HATCHBACK-FACELIFT-01	HIGH	生产期跨越改款，按改款双段式尾门外廓拆分。	READY
28283	28283	Coupe	Passat CC I	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门轿跑外廓。	READY
28284	28284	Coupe	Passat CC I	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门轿跑外廓。	READY
28285	28285	Coupe	Passat CC I	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门轿跑外廓。	READY
28286	28286	SUV	Touareg I facelift	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	第一代改款五门SUV外廓。	READY
28291	28291	Hatchback	800 I		5	EU-ROVER-800-I-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
28308	28308	Sedan	Primera P10	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门轿车外廓。	READY
28332	28332	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	MEDIUM	第二代五门SUV外廓。	READY
28345_prefl	28345	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	生产期跨越改款，按前期外廓拆分。	READY
28345_facelift	28345	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	生产期跨越改款，按改款外廓拆分。	READY
28359_110	28359	SUV	Land Rover 110		3	EU-LAND-ROVER-110-HARDTOP-SUV-3D-01	MEDIUM	输入车系覆盖110，按短车身硬顶分支。	READY
28359_127	28359	SUV	Land Rover 127		3	EU-LAND-ROVER-127-HARDTOP-SUV-3D-01	MEDIUM	输入车系覆盖127，按长车身硬顶分支。	READY
28360_hardtop	28360	SUV	Land Rover 90		3	EU-LAND-ROVER-90-HARDTOP-SUV-3D-01	MEDIUM	硬顶封闭车身分支。	READY
28360_stationwagon	28360	SUV	Land Rover 90		3	EU-LAND-ROVER-90-STATION-WAGON-SUV-3D-01	MEDIUM	Station Wagon封闭车身分支。	READY
28363	28363	Hatchback	MINI R53	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	John Cooper Works三门掀背外廓。	READY
28364_3dr	28364	Hatchback	Stilo 192	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	HIGH	三门掀背物理外廓。	READY
28364_5dr	28364	Hatchback	Stilo 192	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	HIGH	五门掀背物理外廓。	READY
28369	28369	Hatchback	Vel Satis I facelift	BJ0	5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款五门掀背外廓。	READY
28372	28372	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH	CLK 63 AMG两门轿跑外廓。	READY
28374	28374	Wagon	E-Class W211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-5D-01	HIGH	S211改款旅行车外廓。	READY
28376_prefl	28376	Coupe	RX-8	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-4D-PREFL-01	HIGH	生产期跨越改款，按前期四门轿跑外廓拆分。	READY
28376_facelift	28376	Coupe	RX-8 facelift	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-4D-FACELIFT-01	HIGH	生产期跨越改款，按改款四门轿跑外廓拆分。	READY
28380	28380	MPV	Scénic II Phase II	JM	5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV外廓。	READY
28382	28382	Sedan	Legacy IV facelift	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL改款四门轿车外廓。	READY
28393	28393	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH	五门MPV外廓。	READY
28398	28398	SUV	Hummer H3	GMT345	5	EU-HUMMER-H3-GMT345-SUV-5D-01	HIGH	五门SUV外廓。	READY
28400	28400	Convertible	XK II	X150	2	EU-JAGUAR-XK-II-X150-CONVERTIBLE-2D-01	HIGH	X150两门敞篷外廓。	READY
28404	28404	Coupe	TTS 8J	8J3	3	EU-AUDI-TT-8J-TTS-COUPE-3D-01	HIGH	TTS三门轿跑专属保险杠外廓。	READY
28405	28405	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	第一代五门SUV外廓。	READY
28427	28427	Sedan	S-Type II	X200	4	EU-JAGUAR-S-TYPE-II-X200-SEDAN-4D-01	HIGH	四门高性能轿车外廓。	READY
28439	28439	SUV	CR-V III	RE	5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
28444	28444	Sedan	Mark IX		4	EU-JAGUAR-MK-IX-SEDAN-4D-01	MEDIUM	Mark IX四门轿车外廓。	READY
28454	28454	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	LX四门轿车外廓。	READY
28455	28455	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	LX四门轿车外廓。	READY
28460	28460	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	第二代五门SUV外廓。	READY
28480	28480	Convertible	Golf VI Cabriolet	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	两门软顶敞篷外廓。	READY
28494	28494	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门轿车外廓。	READY
28497	28497	Coupe	GTO II	Z16A	3	EU-MITSUBISHI-GTO-II-Z16A-COUPE-3D-01	HIGH	改款三门轿跑外廓。	READY
28506_compact	28506	MPV	Viano W639	W639	5	EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	HIGH	Compact乘用客车外廓。	READY
28506_long	28506	MPV	Viano W639	W639	5	EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	HIGH	Long乘用客车外廓。	READY
28506_extralong	28506	MPV	Viano W639	W639	5	EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	HIGH	Extra-long乘用客车外廓。	READY
28507_van_compact	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	MEDIUM	Compact低顶厢式车。	READY
28507_van_long	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	MEDIUM	Long低顶厢式车。	READY
28507_van_long_highroof	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	MEDIUM	Long高顶厢式车。	READY
28507_van_extralong	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	MEDIUM	Extra-long低顶厢式车。	READY
28507_mixto_compact	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	MEDIUM	Compact Mixto与同长度厢式车外廓一致。	READY
28507_mixto_extralong	28507	Van	Vito W639	W639		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	MEDIUM	Extra-long Mixto与同长度厢式车外廓一致。	READY
28514_swb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	MEDIUM	短轴单排底盘驾驶室。	READY
28514_swb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	MEDIUM	短轴单排栏板货厢。	READY
28514_mwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	MEDIUM	中轴单排底盘驾驶室。	READY
28514_mwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	MEDIUM	中轴单排栏板货厢。	READY
28514_lwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	MEDIUM	长轴单排底盘驾驶室。	READY
28514_lwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	MEDIUM	长轴单排栏板货厢。	READY
28515_singlecab_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	前期单排2WD外廓。	READY
28515_extracab_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	MEDIUM	前期加长排2WD外廓。	READY
28515_doublecab_prefl	28515	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	MEDIUM	前期双排2WD外廓。	READY
28515_singlecab_facelift	28515	Pickup	Hilux VII facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	MEDIUM	2012改款单排外廓。	READY
28515_extracab_facelift	28515	Pickup	Hilux VII facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	MEDIUM	2012改款加长排外廓。	READY
28515_doublecab_facelift	28515	Pickup	Hilux VII facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	2012改款双排窄体外廓。	READY
28516_l2	28516	Pickup	Trafic II Phase II		2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	MEDIUM	L2平台驾驶室外廓。	READY
28516_lwb	28516	Pickup	Trafic II Phase II		2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	长轴平台驾驶室外廓。	READY
28517	28517	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-KB4T-CLUB-CAB-2WD-PICKUP-01	MEDIUM	Club Cab 2WD物理外廓。	READY
28522	28522	Sedan	Mark X I		4	EU-JAGUAR-MK-X-I-SEDAN-4D-01	MEDIUM	Mark X第一期四门轿车外廓。	READY
28536	28536	MPV	Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH	短轴改款乘用MPV外廓。	READY
28543_pickup_singlecab	28543	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	四驱单排栏板货厢。	READY
28543_pickup_doublecab	28543	Pickup	LT I 4x4		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	四驱双排栏板货厢。	READY
28543_chassis_singlecab	28543	Pickup	LT I 4x4		2	EU-VW-LT-I-4X4-CHASSIS-CAB-SINGLE-CAB-01	MEDIUM	四驱单排底盘驾驶室。	READY
28543_chassis_doublecab	28543	Pickup	LT I 4x4		4	EU-VW-LT-I-4X4-CHASSIS-CAB-DOUBLE-CAB-01	MEDIUM	四驱双排底盘驾驶室。	READY
28544_pickup_singlecab	28544	Pickup	LT I 4x4		2	EU-VW-LT-I-4
```


--- 发送 / 推进信号纠偏 / Round 12 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 12 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	4063	1720	1446
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342
EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	4198	1842	1350
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	4174	1702	1430
EU-FORD-FOCUS-I-DNW-WAGON-5D-FACELIFT-01	4454	1702	1467
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800
EU-FORD-USA-EXPLORER-IV-U251-SUV-5D-01	4912	1872	1834
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675
EU-JAGUAR-XK-II-X150-XKR-CONVERTIBLE-2D-01	4794	1892	1329
EU-JAGUAR-XK-II-X150-XKR-COUPE-2D-01	4794	1892	1322
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	3961	1683	1432
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	3958	1683	1432
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	3961	1683	1426
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	3937	1683	1426
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	3723	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	3729	1683	1407
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	3714	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	3723	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655
EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	5010	1695	1755
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-INSIGNIA-A-SPORTS-TOURER-WAGON-FACELIFT-01	4913	1856	1520
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	4435	1830	1295
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-S-TARGA-2D-01	4147	1610	1320
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-FACELIFT-01	4342	1801	1292
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-BASE-01	4347	1801	1304
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-S-01	4347	1801	1306
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-RENAULT-TRAFIC-II-BUS-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-BUS-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	5036	1904	1973
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967
EU-RENAULT-TRAFIC-II-VAN-L1H1-01	4782	1904	1955
EU-RENAULT-TRAFIC-II-VAN-L1H2-01	4782	1904	2465
EU-RENAULT-TRAFIC-II-VAN-L2H1-01	5182	1904	1962
EU-RENAULT-TRAFIC-II-VAN-L2H2-01	5182	1904	2464
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	4088	1693	1441
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	4061	1693	1445
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	4082	1693	1441
EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	4066	1693	1424
EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510
EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	4340	1690	1405
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	5260	1760	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	5260	1835	1850
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	5255	1760	1695
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	5130	1760	1810
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	5255	1835	1810
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	5260	1760	1835
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	5255	1835	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	5255	1760	1795
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504
EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	4799	1855	1417
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	81	110	Jul 2008	Mar 2017	2024-03-01	28225
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	96	131	Jul 2008	Mar 2017	2024-03-01	28226
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	118	160	Jul 2008	Mar 2017	2024-03-01	28227
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	210	286	May 2008	Dec 2010	2024-03-01	28228
Volvo	Xc60 i	2.4 D / D3 / D4 AWD	SUV	Allrad	Diesel	120	163	May 2008	Feb 2017	2024-03-01	28229
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	136	185	May 2008	Dec 2009	2024-03-01	28230
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	118	160	May 2008	Nov 2017	2024-03-01	28231
VW	Scirocco	1.4 TSI	Coupe	Frontantrieb	Benzin	90	122	Aug 2008	Nov 2017	2024-03-01	28232
VW	Scirocco	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Aug 2008	Nov 2017	2024-03-01	28233
VW	Scirocco	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	May 2008	Nov 2009	2024-03-01	28234
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2008	Apr 2017	2024-03-01	28235
Ford	Fiesta vi	1.25	Schrägheck	Frontantrieb	Benzin	60	82	Jun 2008	Apr 2017	2024-03-01	28236
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2008	Dec 2012	2024-03-01	28237
Ford	Fiesta vi	1.4	Schrägheck	Frontantrieb	Benzin	71	97	Oct 2008	Dec 2017	2024-03-01	28238
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2008	Sep 2012	2024-03-01	28239
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28240
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28241
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	254	345	Jun 2008	Dec 2011	2024-03-01	28242
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	283	385	Jun 2008	Dec 2011	2024-03-01	28243
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	254	345	Oct 2008	Dec 2012	2024-03-01	28244
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	283	385	Oct 2008	Dec 2012	2024-03-01	28245
Porsche	Cayman	S 3,4 Sport	Coupe	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2012	2024-03-01	28246
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	223	303	Aug 2008	Dec 2009	2024-03-01	28247
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	70	95	Sep 2008	Aug 2013	2024-03-01	28248
Alfa Romeo	Mito	1.4 Tjet	Schrägheck	Frontantrieb	Benzin	114	155	Aug 2008	Jun 2011	2024-03-01	28249
Alfa Romeo	Mito	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	88	120	Aug 2008	Aug 2015	2024-03-01	28250
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2008	-	2024-03-01	28251
Skoda	Superb ii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 2008	May 2015	2024-03-01	28252
Skoda	Superb ii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Mar 2008	May 2015	2024-03-01	28253
Skoda	Superb ii	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	118	160	Nov 2008	May 2015	2024-03-01	28254
Skoda	Superb ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Nov 2010	2024-03-01	28255
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Mar 2008	May 2010	2024-03-01	28256
Skoda	Superb ii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Jul 2008	May 2015	2024-03-01	28257
Skoda	Superb ii	3.6 FSI 4X4	Schrägheck	Allrad	Benzin	191	260	Nov 2008	May 2015	2024-03-01	28258
Ferrari	California	4.3	Cabriolet	Heckantrieb	Benzin	338	460	Jul 2008	-	2024-03-01	28259
Bentley	Continental	6.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	449	610	Sep 2008	Feb 2013	2024-03-01	28260
Seat	Ibiza iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Jun 2010	2024-03-01	28261
Seat	Ibiza iv sc	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jul 2008	Jun 2010	2025-06-01	28262
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	283	385	Jun 2008	Dec 2012	2024-03-01	28263
Ford	Transit tourneo	2	Bus	Heckantrieb	Benzin	84	114	Nov 1994	Dec 2000	2024-03-01	28264
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	51	69	Nov 1994	Dec 2000	2024-03-01	28265
Ford	Transit tourneo	2.5 DI	Bus	Heckantrieb	Diesel	56	76	Nov 1994	Dec 2000	2024-03-01	28266
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Nov 1994	Dec 2000	2024-03-01	28267
Ford	Transit tourneo	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Apr 1998	Dec 2000	2024-03-01	28268
Subaru	Impreza	1.5 F	Schrägheck	Frontantrieb	Benzin	79	107	Sep 2007	Mar 2012	2024-03-01	28273
Audi	A4 b8 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	132	180	Jun 2008	Dec 2015	2024-03-01	28276
Audi	A4 b8 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	155	211	Jun 2008	Dec 2015	2024-03-01	28277
Audi	Tt	1.8 Tfsi	Coupe	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28278
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28279
Audi	Tt	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Jun 2008	Jun 2014	2024-03-01	28280
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	125	170	Jun 2008	Jun 2014	2024-03-01	28281
Skoda	Superb ii	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	125	170	Sep 2008	May 2015	2024-03-01	28282
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	125	170	Jun 2008	Jan 2012	2024-03-01	28283
VW	Passat cc b6	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Jun 2008	Jan 2012	2024-03-01	28284
VW	Passat cc b6	2.0 TDI	Coupe	Frontantrieb	Diesel	100	136	Jun 2008	May 2011	2024-03-01	28285
VW	Touareg	2.5 R5 TDI	SUV	Allrad	Diesel	120	163	Aug 2003	May 2010	2024-03-01	28286
Rover	800	2	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1987	Sep 1988	2024-03-01	28291
Nissan	Primera	2.0 4X4	Stufenheck	Allrad	Benzin	110	150	Mar 1991	Apr 1993	2024-03-01	28308
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	115	156	Nov 1994	Aug 1996	2024-03-01	28332
Fiat	Multipla	1.6	Großraumlimousine	Frontantrieb	Benzin	76	103	Sep 2000	Jun 2010	2024-03-01	28345
Land Rover	110/127	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Jun 1984	Aug 1987	2024-03-01	28359
Land Rover	90	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	52	71	Jan 1984	Aug 1987	2024-03-01	28360
Mini	Mini	John Cooper Works	Schrägheck	Frontantrieb	Benzin	160	218	Mar 2006	Sep 2006	2024-03-01	28363
Fiat	Stilo	1.6	Schrägheck	Frontantrieb	Benzin	100	136	Apr 2005	Nov 2006	2025-11-01	28364
Renault	Vel satis	3.5	Schrägheck	Frontantrieb	Benzin	170	231	Oct 2004	Aug 2009	2025-12-01	28369
Mercedes-benz	Clk	CLK 63 AMG	Coupe	Heckantrieb	Benzin	373	507	May 2007	May 2009	2024-03-01	28372
Mercedes-benz	E-Klasse	350 CGI	Kombi	Heckantrieb	Benzin	215	292	May 2006	Jul 2009	2024-03-01	28374
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	177	241	Nov 2003	Jun 2012	2024-03-01	28376
Renault	Scénic ii	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Jun 2006	Nov 2008	2024-03-01	28380
Subaru	Legacy iv	2.0 AWD	Stufenheck	Allrad	Benzin	121	165	Jun 2005	Apr 2009	2024-03-01	28382
Mitsubishi	Grandis	2.4 Mivec	Großraumlimousine	Frontantrieb	Benzin	130	177	Apr 2004	Dec 2011	2024-03-01	28393
Hummer	Hummer h3	3.7 4WD	Geländewagen geschlossen	Allrad	Benzin	180	245	Sep 2006	-	2024-03-01	28398
Jaguar	Xk ii	3.6	Cabriolet	Heckantrieb	Benzin	190	258	Oct 2007	Jul 2014	2024-03-01	28400
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	195	265	May 2008	Jun 2014	2024-03-01	28404
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	28405
Jaguar	S-Type ii	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	298	405	Nov 2001	Dec 2008	2024-03-01	28427
Honda	Cr-V iii	2.4	SUV	Frontantrieb	Benzin	125	170	Apr 2007	Dec 2012	2025-12-01	28439
Jaguar	Mk ix	3.8	Stufenheck	Heckantrieb	Benzin	164	223	Oct 1958	Jul 1961	2024-03-01	28444
Dodge	Charger	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Sep 2005	Dec 2010	2024-03-01	28454
Dodge	Charger	2.7	Stufenheck	Heckantrieb	Benzin	141	192	Apr 2006	Dec 2010	2024-03-01	28455
Dodge	Durango	4.7 AWD	SUV	Allrad	Benzin	172	234	Nov 2003	Dec 2009	2024-03-01	28460
VW	Golf vi	2.0 TSI	Cabriolet	Frontantrieb	Benzin	162	220	Nov 2013	May 2016	2024-03-01	28480
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1993	Sep 1997	2024-03-01	28494
Mitsubishi	Gto	3.0 AWD	Coupe	Allrad	Benzin	210	286	Jan 1994	Dec 2000	2024-03-01	28497
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	85	116	Aug 2005	-	2025-06-01	28506
Mercedes-benz	Vito / mixto	109 CDI	Kasten	Heckantrieb	Diesel	70	95	Aug 2006	Aug 2014	2025-12-01	28507
Toyota	Dyna	3.0 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Sep 2006	-	2024-03-01	28514
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	75	102	Mar 2005	May 2015	2024-03-01	28515
Renault	Trafic ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2007	-	2024-03-01	28516
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	28517
Jaguar	Mk x i	3.8	Stufenheck	Heckantrieb	Benzin	197	268	Oct 1961	Oct 1964	2024-05-01	28522
Fiat	Doblo	1.3 JTD	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2005	-	2024-03-01	28536
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28543
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Aug 1991	Jul 1992	2024-03-01	28544
VW	Lt 40-55 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	68	92	Aug 1988	Jul 1991	2024-03-01	28547
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	68	92	Aug 1991	Jul 1992	2024-03-01	28548
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Dec 1982	Jul 1992	2024-03-01	28549
Ford	Focus i	1.8 Turbo DI / Tddi	Stufenheck	Frontantrieb	Diesel	55	75	Aug 2001	Mar 2005	2024-03-01	28562
VW	Lt 28-35 ii	2.8 TDI	Bus	Heckantrieb	Diesel	92	125	Jul 1997	May 2003	2024-03-01	28565
Volvo	V50	2.4 TDI	Kombi	Frontantrieb	Diesel	120	163	May 2007	Dec 2010	2024-03-01	28567


--- 新建对话（分支降级） / Round 12 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6d9fc4-e0a0-83ea-9516-5111e4043604
新对话：https://chatgpt.com/c/6a6da8d2-64ac-83ea-bdfa-dbe6d4ae0ea6

--- Round 12 / checkpoint 续跑 ---
## 更新点

* 已完成 100 个输入 Ktype 的首轮建档与缓存匹配，所有输入 Ktype 均至少保留一条映射。
* 已批量复用 46 个历史尺寸组，不重复输出其三维和来源。
* 已确认 Fiesta VI、Superb II 3T4、Scirocco 137/138、Transit Tourneo 等 Ktype 的车型簇；门数、改款或商用车轴距仍未闭合的记录保持 PENDING。([meyermotoren.de][1])
* Toyota Hilux 28515、Renault Trafic 28516、Mitsubishi L200 28517 已确认到对应车型系列，但现有 Ktype 资料不足以单独锁定 CAB、轴距和车身分支，因此未猜测创建派生行。([market-auto.fr][2])

## 当前批次进度

* 输入 Ktype：100
* 已建立映射行：121
* READY 映射：63
* PENDING 映射：58
* 已命中尺寸组：46
* 本轮新建尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28225_prefl	28225	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28225_facelift	28225	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28226_prefl	28226	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28226_facelift	28226	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28227_prefl	28227	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28227_facelift	28227	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28228	28228	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28229	28229	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28230	28230	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28231_prefl	28231	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28231_facelift	28231	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28232_prefl	28232	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28232_facelift	28232	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28233_prefl	28233	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28233_facelift	28233	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28234	28234	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28235	28235	Hatchback	Fiesta VI				LOW	3门/5门覆盖及改款边界待确认。	PENDING: 门数与改款物理分支未闭合
28236	28236	Hatchback	Fiesta VI				LOW	3门/5门覆盖及改款边界待确认。	PENDING: 门数与改款物理分支未闭合
28237	28237	Hatchback	Fiesta VI				LOW	3门/5门覆盖及改款边界待确认。	PENDING: 门数与改款物理分支未闭合
28238	28238	Hatchback	Fiesta VI				LOW	3门/5门覆盖及改款边界待确认。	PENDING: 门数与改款物理分支未闭合
28239	28239	Hatchback	Fiesta VI				LOW	3门/5门覆盖及改款边界待确认。	PENDING: 门数与改款物理分支未闭合
28240	28240	Coupe	911 (997.2)	997	2		LOW	997.2 Carrera后驱Coupe尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28241	28241	Coupe	911 (997.2)	997	2		LOW	997.2 Carrera S后驱Coupe尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28242	28242	Convertible	911 (997.2)	997	2		LOW	997.2 Carrera后驱Cabriolet尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28243	28243	Convertible	911 (997.2)	997	2		LOW	997.2 Carrera S后驱Cabriolet尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28244	28244	Targa	911 (997.2)	997	2		LOW	997.2 Targa 4尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28245	28245	Targa	911 (997.2)	997	2		LOW	997.2 Targa 4S尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28246	28246	Coupe	Cayman I	987C	3	EU-PORSCHE-CAYMAN-987C-COUPE-01	MEDIUM	S Sport沿用987C Coupe外廓。	READY
28247	28247	Convertible	Boxster II	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	MEDIUM	987前期敞篷外廓。	READY
28248	28248	Hatchback	MiTo	955	3		LOW	现有两组同代三维冲突，需锁定本Ktype对应组。	PENDING: MiTo同代缓存组存在尺寸冲突
28249	28249	Hatchback	MiTo	955	3		LOW	现有两组同代三维冲突，需锁定本Ktype对应组。	PENDING: MiTo同代缓存组存在尺寸冲突
28250	28250	Hatchback	MiTo	955	3		LOW	现有两组同代三维冲突，需锁定本Ktype对应组。	PENDING: MiTo同代缓存组存在尺寸冲突
28251	28251	Hatchback	500	312	3		LOW	Abarth 500硬顶尺寸组待建。	PENDING: 硬顶Hatchback尺寸组尚未闭合
28252	28252	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28253	28253	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28254	28254	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28255	28255	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28256	28256	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28257	28257	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28258	28258	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28259	28259	Convertible	California	F149	2		LOW	California初代硬顶敞篷尺寸组待建。	PENDING: 新尺寸组尚未闭合
28260	28260	Sedan	Continental Flying Spur I	3W	4		LOW	6.0 Flex四门车型边界与尺寸待核。	PENDING: 车型命名与尺寸组尚未闭合
28261	28261	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	改款前五门标准外廓。	READY
28262	28262	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门SC标准外廓。	READY
28263	28263	Coupe	911 (997.2)	997	2		LOW	997.2 Carrera 4S Coupe尺寸组待建。	PENDING: 对应997.2物理尺寸组尚未闭合
28264	28264	MPV	Transit Tourneo				LOW	Tourneo客车轴距/车顶版本待确认。	PENDING: 轴距与车顶物理分支未闭合
28265	28265	MPV	Transit Tourneo				LOW	Tourneo客车轴距/车顶版本待确认。	PENDING: 轴距与车顶物理分支未闭合
28266	28266	MPV	Transit Tourneo				LOW	Tourneo客车轴距/车顶版本待确认。	PENDING: 轴距与车顶物理分支未闭合
28267	28267	MPV	Transit Tourneo				LOW	Tourneo客车轴距/车顶版本待确认。	PENDING: 轴距与车顶物理分支未闭合
28268	28268	MPV	Transit Tourneo				LOW	Tourneo客车轴距/车顶版本待确认。	PENDING: 轴距与车顶物理分支未闭合
28273	28273	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	HIGH	GH五门Hatchback。	READY
28276_prefl	28276	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前Avant。	READY
28276_facelift	28276	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后Avant。	READY
28277_prefl	28277	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前Avant。	READY
28277_facelift	28277	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后Avant。	READY
28278	28278	Coupe	TT II	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J三门Coupe。	READY
28279	28279	Coupe	TT II	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J三门Coupe。	READY
28280_prefl	28280	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	改款前Roadster。	READY
28280_facelift	28280	Convertible	TT II	8J9	2		LOW	改款后Roadster尺寸组待建。	PENDING: 改款后Convertible尺寸组未闭合
28281_prefl	28281	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	改款前Roadster。	READY
28281_facelift	28281	Convertible	TT II	8J9	2		LOW	改款后Roadster尺寸组待建。	PENDING: 改款后Convertible尺寸组未闭合
28282	28282	Hatchback	Superb II	3T4	5		LOW	3T4前后期Liftback尺寸组待建。	PENDING: Superb II Liftback改款前后尺寸组未闭合
28283	28283	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28284	28284	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28285	28285	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28286_prefl	28286	SUV	Touareg I	7L	5		LOW	改款前7L尺寸组待建。	PENDING: 改款前SUV尺寸组未闭合
28286_facelift	28286	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	改款后7L。	READY
28291	28291	Hatchback	800 I	XX	5		LOW	1987-1988 Fastback尺寸组待建。	PENDING: 新尺寸组尚未闭合
28308	28308	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门Sedan。	READY
28332	28332	SUV	Explorer II	U2	5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	MEDIUM	第二代五门SUV。	READY
28345_prefl	28345	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前MPV。	READY
28345_facelift	28345	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后MPV。	READY
28359	28359	SUV	Defender 110/127				LOW	110与127轴距及封闭车身分支未拆分。	PENDING: 多轴距物理分支未闭合
28360	28360	SUV	Defender 90		3		LOW	90封闭车身外廓与车顶高度待确认。	PENDING: 新尺寸组尚未闭合
28363	28363	Hatchback	MINI I	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	R53 JCW三门。	READY
28364_3dr	28364	Hatchback	Stilo I	192	3	EU-FIAT-STILO-I-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
28364_5dr	28364	Hatchback	Stilo I	192	5	EU-FIAT-STILO-I-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
28369	28369	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门Hatchback。	READY
28372	28372	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH	C209改款后Coupe。	READY
28374	28374	Wagon	E-Class III	S211	5		LOW	S211改款后Wagon尺寸组待建。	PENDING: 新尺寸组尚未闭合
28376	28376	Coupe	RX-8 I	SE3P	4		LOW	生产期跨改款，前后期外廓待拆分。	PENDING: 改款前后尺寸组未闭合
28380	28380	MPV	Scénic II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV。	READY
28382_prefl	28382	Sedan	Legacy IV	BL	4		LOW	改款前BL Sedan尺寸组待建。	PENDING: 改款前尺寸组未闭合
28382_facelift	28382	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	改款后BL Sedan。	READY
28393	28393	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH	五门MPV。	READY
28398	28398	SUV	H3	GMT345	5		LOW	H3标准SUV尺寸组待建。	PENDING: 新尺寸组尚未闭合
28400	28400	Convertible	XK II	X150	2		LOW	标准XK与XKR外廓不可直接等同。	PENDING: 标准XK Convertible尺寸组未闭合
28404	28404	Coupe	TT II TTS	8J3	3	EU-AUDI-TT-8J-TTS-COUPE-3D-01	HIGH	TTS三门Coupe。	READY
28405	28405	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV。	READY
28427	28427	Sedan	S-Type II	X200	4		LOW	Supercharged/S-Type R外廓尺寸组待建。	PENDING: 新尺寸组尚未闭合
28439	28439	SUV	CR-V III	RE	5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV。	READY
28444	28444	Sedan	Mark IX		4		LOW	Mark IX三维与宽度口径待核。	PENDING: 新尺寸组尚未闭合
28454	28454	Sedan	Charger VI	LX	4		LOW	SRT8外部套件尺寸需独立核对。	PENDING: SRT8尺寸组尚未闭合
28455	28455	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	标准LX四门Sedan。	READY
28460	28460	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	HB五门SUV。	READY
28480	28480	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	Golf VI Cabriolet。	READY
28494	28494	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门Sedan。	READY
28497	28497	Coupe	GTO II	Z16A	3		LOW	1994-2000改款/尾翼外廓待核。	PENDING: 物理分支与尺寸组未闭合
28506_compact	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	MEDIUM	Compact车长分支。	READY
28506_long	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	MEDIUM	Long车长分支。	READY
28506_extralong	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	MEDIUM	Extra-long车长分支。	READY
28507	28507	Van	Vito II	W639			LOW	Mixto/Van长度与车顶组合待拆分。	PENDING: 轴距与车顶物理分支未闭合
28514_swb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	MEDIUM	SWB chassis-cab。	READY
28514_swb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	MEDIUM	SWB dropside。	READY
28514_mwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	MEDIUM	MWB chassis-cab。	READY
28514_mwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	MEDIUM	MWB dropside。	READY
28514_lwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	MEDIUM	LWB chassis-cab。	READY
28514_lwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	MEDIUM	LWB dropside。	READY
28515	28515	Pickup	Hilux VII				LOW	Ktype覆盖多个Cab及改款分支，需按2WD可用车身闭合。	PENDING: CAB与改款物理分支未闭合
28516	28516	Pickup	Trafic II	EL			LOW	Platform/Chassis轴距分支待确认。	PENDING: 轴距物理分支未闭合
28517	28517	Pickup	L200 IV				LOW	Ktype未锁定Single/Club/Double Cab。	PENDING: CAB物理分支未闭合
28522	28522	Sedan	Mark X I		4		LOW	Mark X 3.8三维与宽度口径待核。	PENDING: 新尺寸组尚未闭合
28536	28536	MPV	Doblò I		5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH	改款后标准轴距MPV。	READY
28543	28543	Pickup	LT I				LOW	LT 28-35 Syncro平台车轴距/驾驶室分支待拆分。	PENDING: 轴距与驾驶室物理分支未闭合
28544	28544	Pickup	LT I				LOW	LT 28-35 Syncro平台车轴距/驾驶室分支待拆分。	PENDING: 轴距与驾驶室物理分支未闭合
28547	28547	Pickup	LT I				LOW	LT 40-55平台车轴距/驾驶室分支待拆分。	PENDING: 轴距与驾驶室物理分支未闭合
28548	28548	Pickup	LT I				LOW	LT 40-55平台车轴距/驾驶室分支待拆分。	PENDING: 轴距与驾驶室物理分支未闭合
28549	28549	Pickup	LT I				LOW	LT 40-55平台车轴距/驾驶室分支待拆分。	PENDING: 轴距与驾驶室物理分支未闭合
28562	28562	Sedan	Focus I	DFW	4		LOW	Focus I改款后Sedan尺寸组待建。	PENDING: 新尺寸组尚未闭合
28565	28565	MPV	LT II				LOW	Bus轴距与车顶组合待拆分。	PENDING: 轴距与车顶物理分支未闭合
28567	28567	Wagon	V50 I	MW	5	EU-VOLVO-V50-MW-WAGON-FACELIFT-01	HIGH	MW改款后Wagon。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Porsche 911 997.2、Skoda Superb II Liftback、Abarth 500、Ferrari California 等乘用车新尺寸组。
2. 解决 Fiesta VI、MiTo、Audi TT Roadster、Touareg I、Legacy IV 的门数、改款或缓存冲突。
3. 最后集中拆分 Transit Tourneo、Vito、Hilux、Trafic、L200、VW LT 等轴距、车顶和 CAB 分支。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/28235/ford/fiesta_6_cb1_ccn_/1_25_28235?utm_source=chatgpt.com "1.25 | Fiesta 6 (CB1, CCN) | Ford | Manufacturers | Meyer Motoren"
[2]: https://market-auto.fr/producto/denckermann-186-d110213?utm_source=chatgpt.com "Toyota HILUX VII Pickup 43310 09015 suspension/load rota ..."


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / checkpoint 续跑 ---
## 更新点

* 本轮关闭 26 条原 PENDING 映射；因 Superb II 跨改款拆分，新增 6 条派生映射行。
* 完成 Porsche 911 997.2 七个外廓分支，以及 Superb II Liftback 改款前后两个尺寸组。
* 首次建立 Abarth 500、Ferrari California、Audi TT Roadster facelift、Mercedes-Benz S211、Hummer H3、Jaguar S-Type R 尺寸组。
* Alfa Romeo MiTo 三个 Ktype 和 Dodge Charger SRT8 直接复用已有尺寸组，未重复输出尺寸事实。

## 当前批次进度

* 映射总行数：127
* READY 映射：95
* PENDING 映射：32
* 已确认尺寸组：61
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28240	28240	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-COUPE-01	HIGH	997.2 Carrera后驱Coupe。	READY
28241	28241	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-COUPE-01	HIGH	997.2 Carrera S后驱Coupe。	READY
28242	28242	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-01	HIGH	997.2 Carrera后驱Cabriolet。	READY
28243	28243	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-01	HIGH	997.2 Carrera S后驱Cabriolet。	READY
28244	28244	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4-01	HIGH	997.2 Targa 4宽体。	READY
28245	28245	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4S-01	HIGH	997.2 Targa 4S宽体。	READY
28248	28248	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28249	28249	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28250	28250	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28251	28251	Hatchback	500	312	3	EU-ABARTH-500-312-HATCHBACK-01	HIGH	312三门硬顶Hatchback。	READY
28252_prefl	28252	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28252_facelift	28252	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28253_prefl	28253	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28253_facelift	28253	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28254_prefl	28254	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28254_facelift	28254	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28255	28255	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28256	28256	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28257_prefl	28257	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28257_facelift	28257	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28258_prefl	28258	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28258_facelift	28258	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28259	28259	Convertible	California	F149	2	EU-FERRARI-CALIFORNIA-F149-CONVERTIBLE-01	MEDIUM	F149折叠硬顶Convertible。	READY
28263	28263	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-COUPE-01	HIGH	997.2 Carrera 4S宽体Coupe。	READY
28280_facelift	28280	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	改款后8J9 Roadster。	READY
28281_facelift	28281	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	改款后8J9 Roadster。	READY
28374	28374	Wagon	E-Class III	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门Wagon。	READY
28398	28398	SUV	H3	GMT345	5	EU-HUMMER-H3-GMT345-SUV-5D-01	HIGH	GMT345五门SUV。	READY
28427	28427	Sedan	S-Type	CCX	4	EU-JAGUAR-S-TYPE-CCX-R-SEDAN-4D-01	MEDIUM	CCX Type R四门Sedan。	READY
28454	28454	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	LX四门SRT8。	READY
28282_prefl	28282	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28282_facelift	28282	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-997-FACELIFT-CARRERA-COUPE-01	4435	1808	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-3.6-345hp-6571
EU-PORSCHE-911-997-FACELIFT-CARRERA-S-COUPE-01	4435	1808	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-s-3.8-385hp-36757
EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-01	4435	1808	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-3.6-345hp-36725
EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-01	4435	1808	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-s-3.8-385hp-36728
EU-PORSCHE-911-997-FACELIFT-TARGA-4-01	4435	1852	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4-3.6-345hp-36793
EU-PORSCHE-911-997-FACELIFT-TARGA-4S-01	4435	1852	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4s-3.8-385hp-36797
EU-ABARTH-500-312-HATCHBACK-01	3657	1627	1485	Auto-Data	https://www.auto-data.net/en/abarth-500-1.4-t-jet-135hp-42423
EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	4838	1817	1462	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-generation-3085
EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	4833	1817	1462	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-facelift-2013-generation-4191
EU-FERRARI-CALIFORNIA-F149-CONVERTIBLE-01	4562	1909	1322	Auto-Data	https://www.auto-data.net/en/ferrari-california-4.3-i-v8-32v-460hp-6523
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-COUPE-01	4435	1852	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2868410/porsche_911_carrera_4s_coupe.html
EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	4198	1842	1358	Auto-Data	https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-1.8-tfsi-160hp-27343
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	4888	1822	1506	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-350-cgi-292hp-7g-tronic-12931
EU-HUMMER-H3-GMT345-SUV-5D-01	4742	1897	1872	Auto-Data	https://www.auto-data.net/en/hummer-h3-3.7i-20v-245hp-4x4-29804
EU-JAGUAR-S-TYPE-CCX-R-SEDAN-4D-01	4861	1819	1441	Auto-Data	https://www.auto-data.net/en/jaguar-s-type-ccx-4.2-i-v8-32v-type-r-395hp-247
```

## 下一步优先处理

1. 闭合 Fiesta VI 的三门、五门及改款前后分支。
2. 集中处理 Transit Tourneo、Vito、Hilux、Trafic、L200 和 VW LT 的轴距、车顶及驾驶室分支。
3. 补齐 Touareg 改款前、Rover 800、Defender、RX-8、Jaguar Mark IX/Mark X、Mitsubishi GTO、Focus I 等剩余独立乘用车尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / checkpoint 续跑 ---
## 更新点

* 已闭合 Fiesta VI 的改款前/后、3 门/5 门物理分支；改款前 3 门复用现有尺寸组，其余三个分支首次建组。尺寸口径分别为 3950/3969 mm 车长，1709/1722 mm 不含后视镜车宽。([carwow.co.uk][1])
* 已闭合 Bentley Continental Flying Spur Speed、Touareg I 改款前、Rover 800 Fastback、Legacy IV 改款前、RX-8 高功率前期版、Jaguar XK Convertible、Mark IX、Mark X 及 Focus I Sedan。([汽车目录][2])
* 本轮首次创建 12 个尺寸组；其余已命中尺寸组继续复用，不重复输出。

## 当前批次进度

* 映射总行数：138
* READY 映射：120
* PENDING 映射：18
* 已确认尺寸组：73
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28235_prefl_3dr	28235	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28235_prefl_5dr	28235	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28235_facelift_3dr	28235	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28235_facelift_5dr	28235	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28236_prefl_3dr	28236	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28236_prefl_5dr	28236	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28236_facelift_3dr	28236	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28236_facelift_5dr	28236	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28237_3dr	28237	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28237_5dr	28237	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28238_prefl_3dr	28238	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28238_prefl_5dr	28238	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28238_facelift_3dr	28238	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28238_facelift_5dr	28238	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28239_3dr	28239	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28239_5dr	28239	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28260	28260	Sedan	Continental Flying Spur I	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-3W-SEDAN-SPEED-FACELIFT-01	HIGH	610 HP Speed改款后四门外廓。	READY
28286_prefl	28286	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-PREFL-01	HIGH	改款前7L五门SUV。	READY
28291	28291	Hatchback	800 I		5	EU-ROVER-800-I-FASTBACK-5D-01	MEDIUM	第一代五门Fastback。	READY
28376	28376	Coupe	RX-8 I	SE3P	4	EU-MAZDA-RX-8-I-SE3P-COUPE-PREFL-01	HIGH	241 HP对应前期高功率外廓。	READY
28382_prefl	28382	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-PREFL-4D-01	HIGH	改款前BL四门Sedan。	READY
28400	28400	Convertible	XK II	X150	2	EU-JAGUAR-XK-II-X150-CONVERTIBLE-2D-01	HIGH	自然吸气XK双门Convertible。	READY
28444	28444	Sedan	Mark IX		4	EU-JAGUAR-MARK-IX-SEDAN-4D-01	MEDIUM	Mark IX四门Sedan。	READY
28522	28522	Sedan	Mark X I		4	EU-JAGUAR-MARK-X-I-SEDAN-4D-01	MEDIUM	初期3.8升Mark X四门Sedan。	READY
28562	28562	Sedan	Focus I	DFW	4	EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	HIGH	DFW四门Sedan。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	3950	1722	1481	Auto-Data	https://www.auto-data.net/en/ford-fiesta-vii-mk7-5-door-1.25-60hp-8022
EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	3969	1709	1495	Automoli	https://www.automoli.com/en/vehicles/ford/fiesta/fiesta-vii-mk7-facelift-2013-3-door-9124/
EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	3969	1722	1495	Automoli	https://www.automoli.com/gb/vehicles/ford/fiesta/fiesta-vii-mk7-facelift-2013-5-door-4227/
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-3W-SEDAN-SPEED-FACELIFT-01	5290	1916	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1373495/bentley_continental_flying_spur_speed.html
EU-VW-TOUAREG-I-7L-SUV-PREFL-01	4754	1928	1726	Auto-Data	https://www.auto-data.net/en/volkswagen-touareg-i-7l-2.5-tdi-174hp-4motion-8512
EU-ROVER-800-I-FASTBACK-5D-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2997530/rover_820_fastback.html
EU-MAZDA-RX-8-I-SE3P-COUPE-PREFL-01	4425	1770	1340	Auto-Data	https://www.auto-data.net/en/mazda-rx-8-1.3-wankel-240hp-11245
EU-SUBARU-LEGACY-IV-BL-SEDAN-PREFL-4D-01	4665	1730	1425	Auto-Data	https://www.auto-data.net/en/subaru-legacy-iv-2.0r-165hp-awd-16162
EU-JAGUAR-XK-II-X150-CONVERTIBLE-2D-01	4791	1892	1329	Auto-Data	https://www.auto-data.net/en/jaguar-xk-convertible-x150-4.2-v8-298hp-automatic-41483
EU-JAGUAR-MARK-IX-SEDAN-4D-01	4991	1854	1600	Carfolio	https://www.carfolio.com/jaguar-mark-ix-3.8-141152
EU-JAGUAR-MARK-X-I-SEDAN-4D-01	5144	1943	1391	Carfolio	https://www.carfolio.com/jaguar-mk-x-3.8-58784
EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	4362	1698	1430	Auto-Data	https://www.auto-data.net/en/ford-focus-i-sedan-1.8-turbo-di-90hp-7358
```

## 下一步优先处理

1. 集中拆分 Transit Tourneo、Vito/Mixto 和 VW LT II Bus 的轴距及车顶组合。
2. 闭合 Defender 90、Defender 110/127、Hilux VII、Trafic II Platform、L200 IV 的轴距和驾驶室分支。
3. 最后处理 Mitsubishi GTO 以及 VW LT I 平台车的来源冲突和多轴距边界。

推进信号：CONTINUE

[1]: https://www.carwow.co.uk/blog/ford-fiesta-dimensions-919?utm_source=chatgpt.com "Ford Fiesta Dimensions – UK Exterior and Interior Stats"
[2]: https://www.automobile-catalog.com/car/2010/1373495/bentley_continental_flying_spur_speed.html?utm_source=chatgpt.com "2010 Bentley Continental Flying Spur Speed Specs Review (448.5 kW / 610 PS / 601 hp) (since mid-year 2009 for Europe North America worldwide)"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / checkpoint 续跑 ---
## 更新点

* 已闭合 Mercedes-Benz Vito/Mixto 109 CDI 的 Compact、Long 高顶和 Extra-long 三个 W639 车身分支，分别对应 `639.601`、`639.603`、`639.605`。([Auto Doc][1])
* 已确认 Toyota Hilux VII Ktype `28515` 为 KUN10/KUN15 单排座后驱车型，并按 2012 年改款前后拆分，直接复用两个已有尺寸组。([Autodoc][2])
* 已将 Renault Trafic II Ktype `28516` 锁定为 `EL` 长轴平台驾驶室，复用已有 LWB 尺寸组。([AUTODOC][3])

## 当前批次进度

* 映射总行数：141
* READY 映射：126
* PENDING 映射：15
* 已确认尺寸组：79
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28507_compact_lowroof	28507	Van	Vito II	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	HIGH	Compact低顶车身。	READY
28507_long_highroof	28507	Van	Vito II	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶车身。	READY
28507_extralong_lowroof	28507	Van	Vito II	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	HIGH	Extra-long低顶车身。	READY
28515_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	HIGH	单排座后驱改款前外廓。	READY
28515_facelift	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	HIGH	单排座后驱2012改款外廓。	READY
28516	28516	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	EL长轴平台驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	4748	1901	1902	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	5223	1901	1900	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
```

## 下一步优先处理

1. 解决 Mitsubishi L200 `KA4T` 单排座尺寸来源冲突。
2. 闭合 Ford Transit Tourneo 与 Land Rover 90、110/127 的轴距和车身分支。
3. 最后处理 VW LT I/II 多轴距、车顶组合及 Mitsubishi GTO 改款分支。

推进信号：CONTINUE

[1]: https://www.auto-doc.ie/car-parts/injector-nozzle-nozzle-holder-pde-12899/mercedes-benz/vito/vito-mixto-box-w639/28507-109-cdi-639-601-639-603-639-605?srsltid=AfmBOooE_7lG2iZFjFO3ebGFmKSdj81OpXhuJQKlcFanOfmgksefoYsH&utm_source=chatgpt.com "Mercedes Vito Mixto W639 109 CDI Injectors"
[2]: https://www.autodoc24.fr/car-parts/camshaft-seal-10621/toyota/hilux-pick-up/hilux-iii-pickup-tgn1-ggn2-ggn1-kun2-kun1/28515-2-5-d-4d-kun15-kun10?utm_source=chatgpt.com "Camshaft seal Toyota Hilux III 2.5 D-4D Diesel 2KD-FTV 102 hp"
[3]: https://www.autodoc.co.uk/car-parts/body/renault/trafic/trafic-ii-platform-chassis-el/28516-2-5-dci?utm_source=chatgpt.com "Body Renault Trafic II Platform 2.5 dCi 114hp Diesel 2007"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / checkpoint 续跑 ---
## 更新点

* Ktype `28517` 已闭合为 `KA4T` 后驱单排座车身。该代码对应欧洲市场 2WD Single Cab，首次建立独立尺寸组。([PartSouq][1])
* Ktype `28497` 已锁定为欧洲规格 `Z16A`、210 kW 的 3000 GT/GTO。1994 后期至 1999 年欧洲规格的三维均为 `4570 × 1840 × 1285 mm`，首次建立稳定尺寸组。
* 其余 13 条仍涉及 Tourneo、Defender 和 VW LT 的轴距、车顶、驾驶室或封闭车身分支，未创建猜测性派生行。

## 当前批次进度

* 映射总行数：141
* READY 映射：128
* PENDING 映射：13
* 已确认尺寸组：81
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28497	28497	Coupe	GTO II	Z16A	3	EU-MITSUBISHI-GTO-Z16A-COUPE-01	HIGH	Z16A欧洲规格双涡轮四驱Coupe。	READY
28517	28517	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-2WD-PICKUP-01	HIGH	KA4T后驱单排座。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-GTO-Z16A-COUPE-01	4570	1840	1285	Automobile-Catalog 1994 Europe;Automobile-Catalog 1999 Europe	https://www.automobile-catalog.com/car/1994/1967795/mitsubishi_3000_gt.html;https://www.automobile-catalog.com/car/1999/1967810/mitsubishi_3000_gt.html
EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-2WD-PICKUP-01	5029	1750	1656	AutoEvolution	https://www.autoevolution.com/cars/mitsubishi-l-200triton-single-cab-2005.html
```

## 下一步优先处理

1. 闭合 Ford Transit Tourneo 五个 Ktype 的统一短轴客车外廓与高度。
2. 拆分 Land Rover 90、110/127 的 Hard Top、Station Wagon 和轴距边界。
3. 最后集中处理 VW LT I 平台驾驶室与 LT II Bus 的轴距、车顶组合。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MN179425XA&ssd=%24%2AKwH8yNnquqWOhIa4mIjv8qSwkJeJ-Pf6--nv4KaPs-un7fKk4vXp4u2r6_Tti_ynqsn-__2N7OPqp7Wjp4WO_J3s4-qp-7u_7IGNh4OVhPy15AAAAADgVBY8%24 "Body | Mitsubishi L200 Europe (EUROPE) KA4T | Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / checkpoint 续跑 ---
## 更新点

* Ford Transit Tourneo 五个 Ktype 已统一闭合到 VE83 短轴客车外廓；历史规格表给出的三维为 4616 × 1974 × 2174 mm。([Timarit][1])
* Land Rover 两个 Ktype 按 Hard Top 与 Station Wagon 的实际外廓差异拆分，不再保留无后缀基础行。110 两种车身长度不同；90 两种车身高度不同。([汽车目录][2])
* 本轮关闭 7 条原 PENDING，新增 9 条 READY 派生映射和 5 个尺寸组。

## 当前批次进度

* 映射总行数：143
* READY 映射：137
* PENDING 映射：6
* 已确认尺寸组：86
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28264	28264	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28265	28265	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28266	28266	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28267	28267	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28268	28268	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28359_110_hardtop	28359	SUV	Land Rover 110	LDH	3	EU-LAND-ROVER-110-LDH-SUV-HARDTOP-3D-01	MEDIUM	LDH封闭式110三门Hard Top。	READY
28359_110_stationwagon	28359	SUV	Land Rover 110	LDH	5	EU-LAND-ROVER-110-LDH-SUV-STATION-WAGON-5D-01	MEDIUM	LDH封闭式110五门Station Wagon。	READY
28360_hardtop	28360	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-LDV-SUV-HARDTOP-3D-01	HIGH	LDV三门Hard Top。	READY
28360_stationwagon	28360	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-LDV-SUV-STATION-WAGON-3D-01	HIGH	LDV三门Station Wagon。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	4616	1974	2174	Ford Transit 1995 UK official brochure;Dagblaðið Vísir Ford specification table	https://autocatalogarchive.com/wp-content/uploads/2026/06/Ford-Transit-1995-UK.pdf;https://timarit.is/page/2937053
EU-LAND-ROVER-110-LDH-SUV-HARDTOP-3D-01	4445	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393655/land-rover_110_hard_top_2_5_diesel.html
EU-LAND-ROVER-110-LDH-SUV-STATION-WAGON-5D-01	4580	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393355/land-rover_110_station_wagon_diesel.html
EU-LAND-ROVER-90-LDV-SUV-HARDTOP-3D-01	3858	1790	1972	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393700/land-rover_90_hard_top_2_25-litre.html
EU-LAND-ROVER-90-LDV-SUV-STATION-WAGON-3D-01	3858	1790	1963	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393370/land-rover_90_station_wagon_2_25-litre.html
```

## 下一步优先处理

1. 闭合 VW LT 28–35 I Syncro 平台驾驶室 Ktype `28543`、`28544` 的轴距分支。
2. 闭合 VW LT 40–55 I 平台驾驶室 Ktype `28547`、`28548`、`28549` 的轴距和驾驶室分支。
3. 最后拆分 VW LT 28–35 II Bus Ktype `28565` 的轴距与车顶组合。

推进信号：CONTINUE

[1]: https://timarit.is/page/2937053?utm_source=chatgpt.com "Dagblaðið Vísir - DV - DV - Bílar (14.02.1996)"
[2]: https://www.automobile-catalog.com/car/1984/1393655/land-rover_110_hard_top_2_5_diesel.html?utm_source=chatgpt.com "1984 Land-Rover 110 Hard Top 2.5 Diesel (man. 5)"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / checkpoint 续跑 ---
## 更新点

* 已闭合 Ktype `28543`、`28544`、`28548`、`28549` 的 Syncro 物理分支。1991 年官方 4×4 资料将该底盘限定为 2950 mm 轴距，并明确列出单排/双排 Pritsche 与单排/双排 Fahrgestell 四种外廓。
* 已将 Ktype `28565` 拆分为 `2DB`、`2DE`、`2DK` 三个 Bus 车身代码，对应 3000、3550、4025 mm 轴距及三套外廓。([易趣][1])
* Ktype `28547` 仍覆盖多轴距、单/双排座、Pritsche/Fahrgestell 及不同载重级高度。官方尺寸表显示这些分支存在实质外廓差异，暂不创建猜测性映射。

## 当前批次进度

* 映射总行数：157
* READY 映射：156
* PENDING 映射：1
* 已确认尺寸组：93
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28543_pickup_singlecab	28543	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Pritsche。	READY
28543_pickup_doublecab	28543	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Pritsche。	READY
28543_chassis_singlecab	28543	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Fahrgestell。	READY
28543_chassis_doublecab	28543	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Fahrgestell。	READY
28544_pickup_singlecab	28544	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Pritsche。	READY
28544_pickup_doublecab	28544	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Pritsche。	READY
28544_chassis_singlecab	28544	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Fahrgestell。	READY
28544_chassis_doublecab	28544	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Fahrgestell。	READY
28547	28547	Pickup	LT I				LOW	候选覆盖2950/3650 mm轴距、单/双排座及Pritsche/Fahrgestell；载重级高度差尚未锁定。	PENDING: 载重级与车身分支未闭合
28548_pickup_singlecab	28548	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Pritsche。	READY
28548_pickup_doublecab	28548	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Pritsche。	READY
28548_chassis_singlecab	28548	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Fahrgestell。	READY
28548_chassis_doublecab	28548	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Fahrgestell。	READY
28549_pickup_singlecab	28549	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Pritsche。	READY
28549_pickup_doublecab	28549	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Pritsche。	READY
28549_chassis_singlecab	28549	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Fahrgestell。	READY
28549_chassis_doublecab	28549	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Fahrgestell。	READY
28565_swb	28565	MPV	LT II	2DB		EU-VW-LT-II-2DB-BUS-SWB-LOWROOF-01	HIGH	3000 mm轴距短轴Bus。	READY
28565_mwb	28565	MPV	LT II	2DE		EU-VW-LT-II-2DE-BUS-MWB-HIGHROOF-01	HIGH	3550 mm轴距中轴Bus。	READY
28565_lwb	28565	MPV	LT II	2DK		EU-VW-LT-II-2DK-BUS-LWB-HIGHROOF-01	HIGH	4025 mm轴距长轴Bus。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	5630	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	5330	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-II-2DB-BUS-SWB-LOWROOF-01	4835	1933	2350	VehicleScore Volkswagen LT dimensions;L'Argus Volkswagen LT 35 2.8 TDI 3000 Court	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt;https://www.largus.fr/fiche-technique/Volkswagen/Lt/II%2BTyp%2B2D/1997/Fourgon%2B4%2BPortes/35%2B28%2BTDI%2B125ch%2B3000%2BCourt-5653.html
EU-VW-LT-II-2DE-BUS-MWB-HIGHROOF-01	5585	1933	2570	VehicleScore Volkswagen LT dimensions	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
EU-VW-LT-II-2DK-BUS-LWB-HIGHROOF-01	6535	1933	2570	VehicleScore Volkswagen LT dimensions;L'Argus Volkswagen LT 35 2.8 TDI 4025 Long	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt;https://www.largus.fr/fiche-technique/Volkswagen/Lt/II%2BTyp%2B2D/1997/Fourgon%2B4%2BPortes/35%2B28%2BTDI%2B125ch%2B4025%2BLong-5655.html
```

## 下一步优先处理

1. 仅处理 Ktype `28547`：按 2950/3650 mm 轴距、单/双排座、Pritsche/Fahrgestell 和 LT40–55 载重级高度拆分，闭合后立即进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.ebay.de/itm/287242778914?utm_source=chatgpt.com "WALKER Abgasrohr 02973 für VW LT 28 35 2 Bus 2DB 2DE 2DK 46 2DC 2DF 2DG 2DL 2DM | eBay.de"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / checkpoint 续跑 ---
## 更新点

* 最后一个 PENDING Ktype `28547` 已按 2950/3650 mm 轴距、单排/双排驾驶室、Pritsche/Fahrgestell 及 LT40/45/50/55 外廓差异，拆分为 16 个确定物理分支。([TheSamba][1])
* 当前批次全部映射闭合，未重新核对已缓存尺寸组。
* 已完成固定表头、主键唯一、引用闭合、尺寸和来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：172
* PENDING 映射：0
* DIMENSION_GROUP：111
* 唯一 `id`：172
* 缺失引用：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28225_prefl	28225	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28225_facelift	28225	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28226_prefl	28226	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28226_facelift	28226	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28227_prefl	28227	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	改款前四门轿车。	READY
28227_facelift	28227	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	改款后四门轿车。	READY
28228	28228	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28229	28229	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28230	28230	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	第一代五门SUV。	READY
28231_prefl	28231	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28231_facelift	28231	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28232_prefl	28232	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28232_facelift	28232	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28233_prefl	28233	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28233_facelift	28233	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	改款后三门轿跑。	READY
28234	28234	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	改款前三门轿跑。	READY
28235_prefl_3dr	28235	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28235_prefl_5dr	28235	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28235_facelift_3dr	28235	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28235_facelift_5dr	28235	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28236_prefl_3dr	28236	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28236_prefl_5dr	28236	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28236_facelift_3dr	28236	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28236_facelift_5dr	28236	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28237_3dr	28237	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28237_5dr	28237	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28238_prefl_3dr	28238	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28238_prefl_5dr	28238	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28238_facelift_3dr	28238	Hatchback	Fiesta VI	CCN	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
28238_facelift_5dr	28238	Hatchback	Fiesta VI	CCN	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
28239_3dr	28239	Hatchback	Fiesta VI	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	改款前三门外廓。	READY
28239_5dr	28239	Hatchback	Fiesta VI	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
28240	28240	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-COUPE-01	HIGH	997.2 Carrera后驱Coupe。	READY
28241	28241	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-COUPE-01	HIGH	997.2 Carrera S后驱Coupe。	READY
28242	28242	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-01	HIGH	997.2 Carrera后驱Cabriolet。	READY
28243	28243	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-01	HIGH	997.2 Carrera S后驱Cabriolet。	READY
28244	28244	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4-01	HIGH	997.2 Targa 4宽体。	READY
28245	28245	Targa	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-TARGA-4S-01	HIGH	997.2 Targa 4S宽体。	READY
28246	28246	Coupe	Cayman I	987C	3	EU-PORSCHE-CAYMAN-987C-COUPE-01	MEDIUM	S Sport沿用987C Coupe外廓。	READY
28247	28247	Convertible	Boxster II	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	MEDIUM	987前期敞篷外廓。	READY
28248	28248	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28249	28249	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28250	28250	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	955三门Hatchback。	READY
28251	28251	Hatchback	500	312	3	EU-ABARTH-500-312-HATCHBACK-01	HIGH	312三门硬顶Hatchback。	READY
28252_prefl	28252	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28252_facelift	28252	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28253_prefl	28253	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28253_facelift	28253	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28254_prefl	28254	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28254_facelift	28254	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28255	28255	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28256	28256	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28257_prefl	28257	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28257_facelift	28257	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28258_prefl	28258	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28258_facelift	28258	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28259	28259	Convertible	California	F149	2	EU-FERRARI-CALIFORNIA-F149-CONVERTIBLE-01	MEDIUM	F149折叠硬顶Convertible。	READY
28260	28260	Sedan	Continental Flying Spur I	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-3W-SEDAN-SPEED-FACELIFT-01	HIGH	610 HP Speed改款后四门外廓。	READY
28261	28261	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	改款前五门标准外廓。	READY
28262	28262	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门SC标准外廓。	READY
28263	28263	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-COUPE-01	HIGH	997.2 Carrera 4S宽体Coupe。	READY
28264	28264	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28265	28265	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28266	28266	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28267	28267	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28268	28268	MPV	Transit Tourneo I	VE83		EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	HIGH	VE83短轴Tourneo客车外廓。	READY
28273	28273	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	HIGH	GH五门Hatchback。	READY
28276_prefl	28276	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前Avant。	READY
28276_facelift	28276	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后Avant。	READY
28277_prefl	28277	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前Avant。	READY
28277_facelift	28277	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后Avant。	READY
28278	28278	Coupe	TT II	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J三门Coupe。	READY
28279	28279	Coupe	TT II	8J3	3	EU-AUDI-TT-8J-COUPE-01	HIGH	8J三门Coupe。	READY
28280_prefl	28280	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	改款前Roadster。	READY
28280_facelift	28280	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	改款后8J9 Roadster。	READY
28281_prefl	28281	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	改款前Roadster。	READY
28281_facelift	28281	Convertible	TT II	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	HIGH	改款后8J9 Roadster。	READY
28282_prefl	28282	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	HIGH	改款前3T4五门Liftback。	READY
28282_facelift	28282	Hatchback	Superb II	3T4	5	EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	HIGH	改款后3T4五门Liftback。	READY
28283	28283	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28284	28284	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28285	28285	Coupe	Passat CC B6	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe外廓。	READY
28286_prefl	28286	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-PREFL-01	HIGH	改款前7L五门SUV。	READY
28286_facelift	28286	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	改款后7L。	READY
28291	28291	Hatchback	800 I		5	EU-ROVER-800-I-FASTBACK-5D-01	MEDIUM	第一代五门Fastback。	READY
28308	28308	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门Sedan。	READY
28332	28332	SUV	Explorer II	U2	5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	MEDIUM	第二代五门SUV。	READY
28345_prefl	28345	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前MPV。	READY
28345_facelift	28345	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后MPV。	READY
28359_110_hardtop	28359	SUV	Land Rover 110	LDH	3	EU-LAND-ROVER-110-LDH-SUV-HARDTOP-3D-01	MEDIUM	LDH封闭式110三门Hard Top。	READY
28359_110_stationwagon	28359	SUV	Land Rover 110	LDH	5	EU-LAND-ROVER-110-LDH-SUV-STATION-WAGON-5D-01	MEDIUM	LDH封闭式110五门Station Wagon。	READY
28360_hardtop	28360	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-LDV-SUV-HARDTOP-3D-01	HIGH	LDV三门Hard Top。	READY
28360_stationwagon	28360	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-LDV-SUV-STATION-WAGON-3D-01	HIGH	LDV三门Station Wagon。	READY
28363	28363	Hatchback	MINI I	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	R53 JCW三门。	READY
28364_3dr	28364	Hatchback	Stilo I	192	3	EU-FIAT-STILO-I-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
28364_5dr	28364	Hatchback	Stilo I	192	5	EU-FIAT-STILO-I-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
28369	28369	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门Hatchback。	READY
28372	28372	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH	C209改款后Coupe。	READY
28374	28374	Wagon	E-Class III	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门Wagon。	READY
28376	28376	Coupe	RX-8 I	SE3P	4	EU-MAZDA-RX-8-I-SE3P-COUPE-PREFL-01	HIGH	241 HP对应前期高功率外廓。	READY
28380	28380	MPV	Scénic II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV。	READY
28382_prefl	28382	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-PREFL-4D-01	HIGH	改款前BL四门Sedan。	READY
28382_facelift	28382	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	改款后BL Sedan。	READY
28393	28393	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH	五门MPV。	READY
28398	28398	SUV	H3	GMT345	5	EU-HUMMER-H3-GMT345-SUV-5D-01	HIGH	GMT345五门SUV。	READY
28400	28400	Convertible	XK II	X150	2	EU-JAGUAR-XK-II-X150-CONVERTIBLE-2D-01	HIGH	自然吸气XK双门Convertible。	READY
28404	28404	Coupe	TT II TTS	8J3	3	EU-AUDI-TT-8J-TTS-COUPE-3D-01	HIGH	TTS三门Coupe。	READY
28405	28405	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV。	READY
28427	28427	Sedan	S-Type	CCX	4	EU-JAGUAR-S-TYPE-CCX-R-SEDAN-4D-01	MEDIUM	CCX Type R四门Sedan。	READY
28439	28439	SUV	CR-V III	RE	5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV。	READY
28444	28444	Sedan	Mark IX		4	EU-JAGUAR-MARK-IX-SEDAN-4D-01	MEDIUM	Mark IX四门Sedan。	READY
28454	28454	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	LX四门SRT8。	READY
28455	28455	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH	标准LX四门Sedan。	READY
28460	28460	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	HB五门SUV。	READY
28480	28480	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	Golf VI Cabriolet。	READY
28494	28494	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门Sedan。	READY
28497	28497	Coupe	GTO II	Z16A	3	EU-MITSUBISHI-GTO-Z16A-COUPE-01	HIGH	Z16A欧洲规格双涡轮四驱Coupe。	READY
28506_compact	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	MEDIUM	Compact车长分支。	READY
28506_long	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	MEDIUM	Long车长分支。	READY
28506_extralong	28506	MPV	Viano I	W639	5	EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	MEDIUM	Extra-long车长分支。	READY
28507_compact_lowroof	28507	Van	Vito II	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	HIGH	Compact低顶车身。	READY
28507_long_highroof	28507	Van	Vito II	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶车身。	READY
28507_extralong_lowroof	28507	Van	Vito II	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	HIGH	Extra-long低顶车身。	READY
28514_swb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	MEDIUM	SWB chassis-cab。	READY
28514_swb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	MEDIUM	SWB dropside。	READY
28514_mwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	MEDIUM	MWB chassis-cab。	READY
28514_mwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	MEDIUM	MWB dropside。	READY
28514_lwb_chassis	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	MEDIUM	LWB chassis-cab。	READY
28514_lwb_dropside	28514	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	MEDIUM	LWB dropside。	READY
28515_prefl	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	HIGH	单排座后驱改款前外廓。	READY
28515_facelift	28515	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	HIGH	单排座后驱2012改款外廓。	READY
28516	28516	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	EL长轴平台驾驶室。	READY
28517	28517	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-2WD-PICKUP-01	HIGH	KA4T后驱单排座。	READY
28522	28522	Sedan	Mark X I		4	EU-JAGUAR-MARK-X-I-SEDAN-4D-01	MEDIUM	初期3.8升Mark X四门Sedan。	READY
28536	28536	MPV	Doblò I		5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH	改款后标准轴距MPV。	READY
28543_pickup_singlecab	28543	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Pritsche。	READY
28543_pickup_doublecab	28543	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Pritsche。	READY
28543_chassis_singlecab	28543	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Fahrgestell。	READY
28543_chassis_doublecab	28543	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Fahrgestell。	READY
28544_pickup_singlecab	28544	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Pritsche。	READY
28544_pickup_doublecab	28544	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Pritsche。	READY
28544_chassis_singlecab	28544	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Fahrgestell。	READY
28544_chassis_doublecab	28544	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Fahrgestell。	READY
28547_swb_singlecab_pickup_lt40_45	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT40-45-01	MEDIUM	2950 mm轴距单排座Pritsche；LT40/45外廓。	READY
28547_swb_singlecab_pickup_lt50	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT50-01	MEDIUM	2950 mm轴距单排座Pritsche；LT50高度分支。	READY
28547_swb_singlecab_pickup_lt55	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT55-01	MEDIUM	2950 mm轴距单排座Pritsche；LT55高度分支。	READY
28547_lwb_singlecab_pickup_lt40_50	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-PICKUP-LWB-SINGLE-CAB-LT40-50-01	MEDIUM	3650 mm轴距单排座Pritsche；LT40/45/50外廓。	READY
28547_lwb_singlecab_pickup_lt55	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-PICKUP-LWB-SINGLE-CAB-LT55-01	MEDIUM	3650 mm轴距单排座Pritsche；LT55高度分支。	READY
28547_swb_doublecab_pickup_lt40_50	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-PICKUP-SWB-DOUBLE-CAB-LT40-50-01	MEDIUM	2950 mm轴距双排座Pritsche；LT40/45/50外廓。	READY
28547_lwb_doublecab_pickup_lt40_50	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-PICKUP-LWB-DOUBLE-CAB-LT40-50-01	MEDIUM	3650 mm轴距双排座Pritsche；LT40/45/50外廓。	READY
28547_lwb_doublecab_pickup_lt55	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-PICKUP-LWB-DOUBLE-CAB-LT55-01	MEDIUM	3650 mm轴距双排座Pritsche；LT55高度分支。	READY
28547_swb_singlecab_chassis_lt40_50	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-CHASSIS-SWB-SINGLE-CAB-LT40-50-01	MEDIUM	2950 mm轴距单排座Fahrgestell；LT40/45/50外廓。	READY
28547_swb_singlecab_chassis_lt55	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-CHASSIS-SWB-SINGLE-CAB-LT55-01	MEDIUM	2950 mm轴距单排座Fahrgestell；LT55高度分支。	READY
28547_lwb_singlecab_chassis_lt40_50	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-CHASSIS-LWB-SINGLE-CAB-LT40-50-01	MEDIUM	3650 mm轴距单排座Fahrgestell；LT40/45/50外廓。	READY
28547_lwb_singlecab_chassis_lt55	28547	Pickup	LT I	293-909	2	EU-VW-LT-I-293-909-CHASSIS-LWB-SINGLE-CAB-LT55-01	MEDIUM	3650 mm轴距单排座Fahrgestell；LT55高度分支。	READY
28547_swb_doublecab_chassis_lt40	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-CHASSIS-SWB-DOUBLE-CAB-LT40-01	MEDIUM	2950 mm轴距双排座Fahrgestell；LT40高度分支。	READY
28547_swb_doublecab_chassis_lt45_50	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-CHASSIS-SWB-DOUBLE-CAB-LT45-50-01	MEDIUM	2950 mm轴距双排座Fahrgestell；LT45/50外廓。	READY
28547_lwb_doublecab_chassis_lt40_50	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-CHASSIS-LWB-DOUBLE-CAB-LT40-50-01	MEDIUM	3650 mm轴距双排座Fahrgestell；LT40/45/50外廓。	READY
28547_lwb_doublecab_chassis_lt55	28547	Pickup	LT I	293-909	4	EU-VW-LT-I-293-909-CHASSIS-LWB-DOUBLE-CAB-LT55-01	MEDIUM	3650 mm轴距双排座Fahrgestell；LT55高度分支。	READY
28548_pickup_singlecab	28548	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Pritsche。	READY
28548_pickup_doublecab	28548	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Pritsche。	READY
28548_chassis_singlecab	28548	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	MEDIUM	2950 mm轴距单排座Fahrgestell。	READY
28548_chassis_doublecab	28548	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	MEDIUM	2950 mm轴距双排座Fahrgestell。	READY
28549_pickup_singlecab	28549	Pickup	LT I		2	EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Pritsche。	READY
28549_pickup_doublecab	28549	Pickup	LT I		4	EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Pritsche。	READY
28549_chassis_singlecab	28549	Pickup	LT I		2	EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	HIGH	2950 mm轴距单排座Fahrgestell。	READY
28549_chassis_doublecab	28549	Pickup	LT I		4	EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	HIGH	2950 mm轴距双排座Fahrgestell。	READY
28562	28562	Sedan	Focus I	DFW	4	EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	HIGH	DFW四门Sedan。	READY
28565_swb	28565	MPV	LT II	2DB		EU-VW-LT-II-2DB-BUS-SWB-LOWROOF-01	HIGH	3000 mm轴距短轴Bus。	READY
28565_mwb	28565	MPV	LT II	2DE		EU-VW-LT-II-2DE-BUS-MWB-HIGHROOF-01	HIGH	3550 mm轴距中轴Bus。	READY
28565_lwb	28565	MPV	LT II	2DK		EU-VW-LT-II-2DK-BUS-LWB-HIGHROOF-01	HIGH	4025 mm轴距长轴Bus。	READY
28567	28567	Wagon	V50 I	MW	5	EU-VOLVO-V50-MW-WAGON-FACELIFT-01	HIGH	MW改款后Wagon。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2901-3000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-sedan-a-2.0-turbo-220hp-1802
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-sedan-a-facelift-2013-generation-4215
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713	Auto-Data	https://www.auto-data.net/en/volvo-xc60-i-3.0-t6-285hp-awd-17165
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404	Auto-Data	https://www.auto-data.net/en/volkswagen-scirocco-iii-1.4-tsi-160hp-8814
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406	Auto-Data	https://www.auto-data.net/en/volkswagen-scirocco-iii-facelift-2014-generation-4327
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481	Auto-Data	https://www.auto-data.net/en/ford-fiesta-vii-mk7-3-door-generation-9122
EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-01	3950	1722	1481	Auto-Data	https://www.auto-data.net/en/ford-fiesta-vii-mk7-5-door-1.25-60hp-8022
EU-FORD-FIESTA-VII-CB1-HATCHBACK-3D-FACELIFT-01	3969	1709	1495	Auto-Data	https://www.auto-data.net/en/ford-fiesta-vii-mk7-facelift-2012-3-door-1.0-65hp-46878
EU-FORD-FIESTA-VII-CB1-HATCHBACK-5D-FACELIFT-01	3969	1722	1495	Auto-Data	https://www.auto-data.net/en/ford-fiesta-vii-mk7-facelift-2012-5-door-1.0-65hp-46867
EU-PORSCHE-911-997-FACELIFT-CARRERA-COUPE-01	4435	1808	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-3.6-345hp-6571
EU-PORSCHE-911-997-FACELIFT-CARRERA-S-COUPE-01	4435	1808	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-s-3.8-385hp-36757
EU-PORSCHE-911-997-FACELIFT-CARRERA-CONVERTIBLE-01	4435	1808	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-3.6-345hp-36725
EU-PORSCHE-911-997-FACELIFT-CARRERA-S-CONVERTIBLE-01	4435	1808	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-s-3.8-385hp-36728
EU-PORSCHE-911-997-FACELIFT-TARGA-4-01	4435	1852	1310	Auto-Data	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4-3.6-345hp-36793
EU-PORSCHE-911-997-FACELIFT-TARGA-4S-01	4435	1852	1300	Auto-Data	https://www.auto-data.net/en/porsche-911-targa-997-facelift-2008-targa-4s-3.8-385hp-36797
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-generation-1532
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292	Auto-Data	https://www.auto-data.net/en/porsche-boxster-987-s-3.4-295hp-tiptronic-6706
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	4063	1720	1446	Auto-Data	https://www.auto-data.net/en/alfa-romeo-mito-generation-363
EU-ABARTH-500-312-HATCHBACK-01	3657	1627	1485	Auto-Data	https://www.auto-data.net/en/abarth-500-1.4-t-jet-135hp-42423
EU-SKODA-SUPERB-II-3T4-LIFTBACK-PREFL-01	4838	1817	1462	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-generation-3085
EU-SKODA-SUPERB-II-3T4-LIFTBACK-FACELIFT-01	4833	1817	1462	Auto-Data	https://www.auto-data.net/en/skoda-superb-ii-facelift-2013-generation-4191
EU-FERRARI-CALIFORNIA-F149-CONVERTIBLE-01	4562	1909	1322	Auto-Data	https://www.auto-data.net/en/ferrari-california-4.3-i-v8-32v-460hp-6523
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-3W-SEDAN-SPEED-FACELIFT-01	5290	1916	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1373495/bentley_continental_flying_spur_speed.html
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data	https://www.auto-data.net/en/seat-ibiza-iv-1.4-tdi-80hp-44358
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428	Auto-Data	https://www.auto-data.net/en/seat-ibiza-iv-sc-1.4-85hp-44348
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-COUPE-01	4435	1852	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2868410/porsche_911_carrera_4s_coupe.html
EU-FORD-TRANSIT-TOURNEO-I-VE83-MPV-SWB-01	4616	1974	2174	Ford Transit 1995 UK official brochure;Dagblaðið Vísir Ford specification table	https://autocatalogarchive.com/wp-content/uploads/2026/06/Ford-Transit-1995-UK.pdf;https://timarit.is/page/2937053
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475	Auto-Data	https://www.auto-data.net/en/subaru-impreza-iii-hatchback-generation-3589
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data	https://www.auto-data.net/en/audi-a4-avant-b8-8k-generation-1085
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-1.8-tfsi-170hp-multitronic-18923
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352	Auto-Data	https://www.auto-data.net/en/audi-tt-coupe-8j-2.0-tfsi-200hp-4877
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358	Auto-Data	https://www.auto-data.net/en/audi-tt-roadster-8j-generation-1087
EU-AUDI-TT-8J-CONVERTIBLE-2D-FACELIFT-01	4198	1842	1358	Auto-Data	https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-1.8-tfsi-160hp-27343
EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	4799	1855	1417	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-cc-i-generation-1894
EU-VW-TOUAREG-I-7L-SUV-PREFL-01	4754	1928	1726	Auto-Data	https://www.auto-data.net/en/volkswagen-touareg-i-7l-2.5-tdi-174hp-4motion-tiptronic-8511
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726	Auto-Data	https://www.auto-data.net/en/volkswagen-touareg-i-7l-facelift-2006-3.0-tdi-v6-240hp-4motion-tiptronic-8514
EU-ROVER-800-I-FASTBACK-5D-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2997530/rover_820_fastback.html
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-p10-generation-186
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800	Auto-Data	https://www.auto-data.net/en/ford-explorer-ii-4.0-xlt-162hp-7871
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695	Auto-Data	https://www.auto-data.net/en/fiat-multipla-186-generation-1626
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690	Auto-Data	https://www.auto-data.net/en/fiat-multipla-186-facelift-2004-generation-7330
EU-LAND-ROVER-110-LDH-SUV-HARDTOP-3D-01	4445	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393655/land-rover_110_hard_top_2_5_diesel.html
EU-LAND-ROVER-110-LDH-SUV-STATION-WAGON-5D-01	4580	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393355/land-rover_110_station_wagon_diesel.html
EU-LAND-ROVER-90-LDV-SUV-HARDTOP-3D-01	3858	1790	1972	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393700/land-rover_90_hard_top_2_25-litre.html
EU-LAND-ROVER-90-LDV-SUV-STATION-WAGON-3D-01	3858	1790	1963	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1393370/land-rover_90_station_wagon_2_25-litre.html
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427	Auto-Data	https://www.auto-data.net/en/mini-hatch-r50-r53-cooper-s-1.6-i-16v-170hp-15332
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475	Auto-Data	https://www.auto-data.net/en/fiat-stilo-192-3-door-generation-3404
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525	Auto-Data	https://www.auto-data.net/en/fiat-stilo-192-5-door-generation-3405
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577	Auto-Data	https://www.auto-data.net/en/renault-vel-satis-facelift-2005-generation-3755
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413	Auto-Data	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-clk-200-kompressor-163hp-23415
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	4888	1822	1506	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-350-cgi-292hp-7g-tronic-12931
EU-MAZDA-RX-8-I-SE3P-COUPE-PREFL-01	4425	1770	1340	Auto-Data	https://www.auto-data.net/en/mazda-rx-8-1.3-wankel-240hp-11245
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620	Auto-Data	https://www.auto-data.net/en/renault-scenic-ii-phase-ii-generation-7615
EU-SUBARU-LEGACY-IV-BL-SEDAN-PREFL-4D-01	4665	1730	1425	Auto-Data	https://www.auto-data.net/en/subaru-legacy-iv-2.0r-165hp-awd-16162
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425	Auto-Data	https://www.auto-data.net/en/subaru-legacy-iv-facelift-2006-generation-3598
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655	Auto-Data	https://www.auto-data.net/en/mitsubishi-grandis-2.4-i-16v-mivec-165hp-15449
EU-HUMMER-H3-GMT345-SUV-5D-01	4742	1897	1872	Auto-Data	https://www.auto-data.net/en/hummer-h3-3.7i-20v-245hp-4x4-29804
EU-JAGUAR-XK-II-X150-CONVERTIBLE-2D-01	4791	1892	1329	Auto-Data	https://www.auto-data.net/en/jaguar-xk-convertible-x150-4.2-v8-298hp-automatic-41483
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345	Auto-Data	https://www.auto-data.net/en/audi-tts-coupe-8j-generation-1137
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Auto-Data	https://www.auto-data.net/en/chevrolet-captiva-i-generation-3206
EU-JAGUAR-S-TYPE-CCX-R-SEDAN-4D-01	4861	1819	1441	Auto-Data	https://www.auto-data.net/en/jaguar-s-type-ccx-4.2-i-v8-32v-type-r-395hp-247
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675	Auto-Data	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-automatic-12336
EU-JAGUAR-MARK-IX-SEDAN-4D-01	4991	1854	1600	Carfolio	https://www.carfolio.com/jaguar-mark-ix-3.8-141152
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479	Auto-Data	https://www.auto-data.net/en/dodge-charger-vi-lx-generation-3180
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887	Auto-Data	https://www.auto-data.net/en/dodge-durango-ii-generation-3182
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-generation-4124
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351	Auto-Data	https://www.auto-data.net/en/cadillac-seville-iv-generation-3163
EU-MITSUBISHI-GTO-Z16A-COUPE-01	4570	1840	1285	Automobile-Catalog 1994 Europe;Automobile-Catalog 1999 Europe	https://www.automobile-catalog.com/car/1994/1967795/mitsubishi_3000_gt.html;https://www.automobile-catalog.com/car/1999/1967810/mitsubishi_3000_gt.html
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875	Mercedes-Benz Viano/Vito W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875	Mercedes-Benz Viano/Vito W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872	Mercedes-Benz Viano/Vito W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-LOWROOF-01	4748	1901	1902	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-LOWROOF-01	5223	1901	1900	Mercedes-Benz Vito Van/CrewCab W639 specifications	https://www.scribd.com/document/725303882/Mercedes-Benz-Vito-Van-CrewCab-W639-I-Specifications-201001
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235	Toyota Dyna official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/DynaGen7UKLaunchPack.pdf
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680	Auto-Data;Toyota Hilux official specifications	https://www.auto-data.net/en/toyota-hilux-single-cab-vii-facelift-2008-generation-8431;https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/HiluxGen7UKLaunchPack.pdf
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795	Toyota Hilux official specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/HiluxGen7UKLaunchPack.pdf
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967	Renault Trafic II platform-cab specifications	https://www.auto-data.net/en/renault-trafic-ii-platform-chassis-generation-3770
EU-MITSUBISHI-L200-IV-KA4T-SINGLE-CAB-2WD-PICKUP-01	5029	1750	1656	AutoEvolution	https://www.autoevolution.com/cars/mitsubishi-l-200triton-single-cab-2005.html
EU-JAGUAR-MARK-X-I-SEDAN-4D-01	5144	1943	1391	Carfolio	https://www.carfolio.com/jaguar-mk-x-3.8-58784
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818	Auto-Data	https://www.auto-data.net/en/fiat-doblo-i-facelift-2005-generation-3401
EU-VW-LT-I-4X4-PICKUP-SINGLE-CAB-01	5630	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-PICKUP-DOUBLE-CAB-01	5330	2140	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-SINGLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-4X4-CHASSIS-DOUBLE-CAB-01	5265	2085	2315	Volkswagen LT 4x4 official brochure June 1991	https://www.lt-forum.de/dokuwiki/lib/exe/fetch.php?media=startseite%3Aprospekte%3Avolkswagen%3Avw_lt_4x4_prospekt_1991%3Avw_lt_4x4_prospekt_1991.pdf
EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT40-45-01	5630	2140	2110	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT50-01	5630	2140	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-SWB-SINGLE-CAB-LT55-01	5630	2140	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-LWB-SINGLE-CAB-LT40-50-01	6545	2370	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-LWB-SINGLE-CAB-LT55-01	6545	2370	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-SWB-DOUBLE-CAB-LT40-50-01	5330	2140	2100	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-LWB-DOUBLE-CAB-LT40-50-01	6560	2140	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-PICKUP-LWB-DOUBLE-CAB-LT55-01	6560	2140	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-SWB-SINGLE-CAB-LT40-50-01	5245	2050	2120	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-SWB-SINGLE-CAB-LT55-01	5245	2050	2145	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-LWB-SINGLE-CAB-LT40-50-01	6240	2050	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-LWB-SINGLE-CAB-LT55-01	6240	2050	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-SWB-DOUBLE-CAB-LT40-01	5245	2050	2100	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-SWB-DOUBLE-CAB-LT45-50-01	5245	2050	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-LWB-DOUBLE-CAB-LT40-50-01	6180	2050	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-293-909-CHASSIS-LWB-DOUBLE-CAB-LT55-01	6180	2050	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-FORD-FOCUS-I-DFW-SEDAN-4D-01	4362	1698	1430	Auto-Data	https://www.auto-data.net/en/ford-focus-i-sedan-1.8-turbo-di-90hp-7358
EU-VW-LT-II-2DB-BUS-SWB-LOWROOF-01	4835	1933	2350	VehicleScore Volkswagen LT dimensions;L'Argus Volkswagen LT 35 2.8 TDI 3000 Court	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt;https://www.largus.fr/fiche-technique/Volkswagen/Lt/II%2BTyp%2B2D/1997/Fourgon%2B4%2BPortes/35%2B28%2BTDI%2B125ch%2B3000%2BCourt-5653.html
EU-VW-LT-II-2DE-BUS-MWB-HIGHROOF-01	5585	1933	2570	VehicleScore Volkswagen LT dimensions	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
EU-VW-LT-II-2DK-BUS-LWB-HIGHROOF-01	6535	1933	2570	VehicleScore Volkswagen LT dimensions;L'Argus Volkswagen LT 35 2.8 TDI 4025 Long	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt;https://www.largus.fr/fiche-technique/Volkswagen/Lt/II%2BTyp%2B2D/1997/Fourgon%2B4%2BPortes/35%2B28%2BTDI%2B125ch%2B4025%2BLong-5655.html
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457	Auto-Data	https://www.auto-data.net/en/volvo-v50-facelift-2007-2.4-d5-180hp-17178
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2901-3000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf "https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6216 行）
- 累计尺寸组：dimension_groups_final.tsv（2620 行）

- 尺寸冲突协调：
  - EU-HUMMER-H3-GMT345-SUV-5D-01 -> EU-HUMMER-H3-GMT345-SUV-5D-02：4742x1897x1893 与 4742x1897x1872，创建新尺寸组
