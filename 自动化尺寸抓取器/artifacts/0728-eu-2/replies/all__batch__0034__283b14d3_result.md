# 任务：all 第 3301-3400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0034__283b14d3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3301-3400 行

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
all 第 3301-3400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
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
EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	5400	1900	1515
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
EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	5629	2027	1869
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	4877	1849	1278
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278
EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	5164	1725	1580
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	5197	1725	1577
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	4793	1725	1577
EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	5164	1725	1621
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	5197	1725	1661
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	4793	1725	1621
EU-CHEVROLET-S10-I-PICKUP-4WD-EXTCAB-SHORT-01	4897	1646	1610
EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-LONG-01	4933	1646	1610
EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-SHORT-01	4526	1646	1610
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	4590	1830	1690
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	4590	1830	1710
EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	4273	1769	1456
EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	4288	1769	1456
EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	4275	1773	1458
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	6342	2029	1890
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	5784	2029	1890
EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	5834	2029	1875
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	6200	2014	1847
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	5695	2014	1847
EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	5692	2014	1848
EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	4689	2019	1787
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-BRAVO-II-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	5681	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	5681	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	5181	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	5181	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	4831	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	5980	2040	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	5980	2040	2125
EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	5998	2050	2524
EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	5413	2050	2524
EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	4963	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779
EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	5599	2024	2470
EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	5099	2024	2470
EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	5099	2024	2480
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104
EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-DUCATO-X230-TRUCK-LWB-01	5620	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-MWB-01	5120	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-SWB-01	4770	2000	2100
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100
EU-FIAT-SEDICI-I-SUV-4X4-01	4115	1755	1620
EU-FIAT-SEDICI-SUV-01	4115	1755	1620
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	4730	1829	1323
EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	5088	1847	1334
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675
EU-HONDA-LEGEND-IV-SEDAN-KB1-01	4957	1845	1450
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475
EU-JEEP-PATRIOT-I-MK74-SUV-01	4408	1785	1658
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281
EU-NISSAN-MURANO-II-Z51-SUV-5D-01	4860	1885	1720
EU-NISSAN-SKYLINE-R32-COUPE-2D-01	4530	1695	1325
EU-NISSAN-SKYLINE-R32-SEDAN-4D-01	4580	1695	1360
EU-NISSAN-SKYLINE-R33-GTS4-COUPE-2D-01	4640	1720	1355
EU-NISSAN-SKYLINE-R34-COUPE-2D-01	4580	1725	1340
EU-RENAULT-KANGOO-I-FACELIFT-MPV-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-TOYOTA-CORONA-T190-SEDAN-01	4520	1695	1410
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833
EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	4206	1759	1580
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592
EU-VW-GOLF-PLUS-V-MPV-PREFL-01	4206	1759	1592
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Chevrolet	S10	4.3	Pick-up	Heckantrieb	Benzin	142	193	Oct 1994	Dec 2004	2024-03-01	30146
Chevrolet	S10	4.3 4X4	Pick-up	Allrad	Benzin	142	193	Oct 1994	Aug 2002	2024-03-01	30147
Honda	Cr-V iii	2.4 I-vtec 4WD	SUV	Allrad	Benzin	118	160	Oct 2006	Oct 2012	2025-12-01	30149
Toyota	Corona	2	Stufenheck	Frontantrieb	Benzin	98	133	Oct 1993	Sep 1995	2024-03-01	30156
Dodge	Ram 1500	5.9	Pick-up	Heckantrieb	Benzin	184	250	Jan 1993	Sep 2001	2024-03-01	30166
Dodge	Ram 2500	5.9 DI	Pick-up	Heckantrieb	Diesel	118	160	Jan 1993	Sep 1996	2024-03-01	30167
Dodge	Ram 2500	5.9 DI 4X4	Pick-up	Allrad	Diesel	154	209	Oct 1996	May 2001	2024-03-01	30168
Dodge	Ram 1500	5.9 4X4	Pick-up	Allrad	Benzin	184	250	Jan 1993	Sep 2001	2024-03-01	30169
Dodge	Ram 1500	5.2	Pick-up	Heckantrieb	Benzin	172	234	Jan 1993	Sep 2001	2024-03-01	30170
Dodge	Ram 2500	8	Pick-up	Heckantrieb	Benzin	221	300	Jan 1993	May 2001	2024-03-01	30171
Dodge	Ram 1500	5.2 4X4	Pick-up	Allrad	Benzin	172	234	Jan 1993	May 2001	2024-03-01	30172
Dodge	Ram 1500	3.9	Pick-up	Heckantrieb	Benzin	128	174	Jan 1993	May 2001	2024-03-01	30173
Dodge	Ram 1500	5.2	Pick-up	Heckantrieb	Benzin	164	223	Jan 1993	Jun 1998	2024-03-01	30174
Dodge	Ram 2500	5.9 DI 4X4	Pick-up	Allrad	Diesel	118	160	Jan 1993	Sep 1996	2024-03-01	30175
Dodge	Ram 2500	8.0 4X4	Pick-up	Allrad	Benzin	221	300	Jan 1993	May 2001	2024-03-01	30176
Dodge	Ram 2500	8.0 4X4	Pick-up	Allrad	Benzin	228	310	Jan 2002	Dec 2009	2024-03-01	30177
Dodge	Ram 1500	3.7	Pick-up	Heckantrieb	Benzin	157	213	Jun 2001	Sep 2008	2024-03-01	30179
Dodge	Ram 1500	4.7 4X4	Pick-up	Allrad	Benzin	172	234	Jun 2001	Sep 2008	2024-03-01	30180
Dodge	Ram 2500	5.9 DI 4X4	Pick-up	Allrad	Diesel	180	245	Jan 2002	Dec 2009	2024-03-01	30181
Dodge	Ram 1500	4.7	Pick-up	Heckantrieb	Benzin	172	234	Jun 2001	Sep 2008	2024-03-01	30182
Dodge	Ram 1500	5.9 4X4	Pick-up	Allrad	Benzin	180	245	Jun 2001	Sep 2008	2024-03-01	30183
Dodge	Ram	5.2	Bus	Heckantrieb	Benzin	107	145	Oct 1985	Sep 1987	2024-03-01	30186
Dodge	Ram	5.9	Bus	Heckantrieb	Benzin	130	177	Oct 1985	Sep 1988	2024-03-01	30187
Dodge	Ram	5.2	Bus	Heckantrieb	Benzin	127	173	Oct 1987	Sep 1993	2024-03-01	30188
Dodge	Ram van	5.2 CNG	Kasten	Heckantrieb	Benzin/Erdgas (CNG)	165	224	Aug 1999	Sep 2003	2024-03-01	30190
Dodge	Ram van	5.9	Kasten	Heckantrieb	Benzin	184	250	Aug 1993	Sep 2003	2024-03-01	30191
Dodge	Ram van	3.9	Kasten	Heckantrieb	Benzin	128	174	Aug 1993	Sep 2003	2024-03-01	30192
Dodge	Ram van	5.2 Flexfuel	Kasten	Heckantrieb	Benzin/Ethanol	162	220	Aug 1999	Sep 2003	2024-03-01	30193
Dodge	Ram van	5.2	Kasten	Heckantrieb	Benzin	172	234	Aug 1993	Sep 2003	2024-03-01	30194
Ford USA	Thunderbird	4.6	Coupe	Heckantrieb	Benzin	151	205	Jan 1993	Dec 1997	2024-03-01	30212
Mercedes-benz	Slr	5.4	Cabriolet	Heckantrieb	Benzin	478	650	Oct 2006	-	2024-03-01	30213
Bentley	Arnage	6.8	Coupe	Heckantrieb	Benzin	336	457	Sep 2005	-	2024-03-01	30214
Hyundai	Tiburon	2.0 Cvvt	Coupe	Frontantrieb	Benzin	105	143	Oct 2006	Dec 2008	2024-03-01	30235
Chevrolet	Avalanche	5.3 AWD	Pick-up	Allrad	Benzin	235	320	May 2006	Dec 2013	2024-03-01	30246
Nissan	Trade	2.3 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	55	75	Jun 1996	Oct 2001	2024-03-01	30262
Chevrolet	Camaro	3.6	Coupe	Heckantrieb	Benzin	224	305	Sep 2009	Dec 2010	2024-03-01	30272
Nissan	Murano ii	3.5 4X4	SUV	Allrad	Benzin	195	265	Nov 2007	Sep 2014	2024-03-01	30282
Honda	Cr-V iii	2.4	SUV	Frontantrieb	Benzin	124	168	Jun 2006	Jun 2012	2025-12-01	30298
Ford USA	F-150	6.2 4X4	Pick-up	Allrad	Benzin	306	416	Jan 2010	-	2024-03-01	30301
Nissan	Skyline	2.6 Twin Turbo 4X4	Coupe	Allrad	Benzin	206	280	Apr 1989	Jun 1993	2024-03-01	30303
Nissan	Skyline	2.6 Twin Turbo 4X4	Coupe	Allrad	Benzin	206	280	Jul 1994	Sep 1999	2024-03-01	30304
BMW	3	330 CI	Coupe	Heckantrieb	Benzin	170	231	Jun 2000	May 2006	2024-03-01	30325
Fiat	Ducato	130 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	96	131	Aug 2006	-	2024-03-01	30326
Fiat	Bravo ii	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	66	90	Apr 2007	Dec 2008	2024-03-01	30327
Ford	S-Max	2.0 Flexifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	107	145	May 2006	Dec 2014	2024-03-01	30329
Ford	Mondeo iv turnier	2.0 Flexifuel	Kombi	Frontantrieb	Benzin/Ethanol	107	145	Mar 2009	Jan 2015	2024-03-01	30330
Ford	Mondeo iv	2.0 Flexifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	107	145	Mar 2009	Jan 2015	2024-03-01	30331
Suzuki	Liana	1.6	Stufenheck	Frontantrieb	Benzin	79	107	Jan 2005	-	2024-03-01	30332
Suzuki	Liana	1.6 4WD	Stufenheck	Allrad	Benzin	79	107	Jan 2005	Dec 2007	2024-03-01	30333
Suzuki	Liana	1.6 4WD	Schrägheck	Allrad	Benzin	79	107	Jan 2005	Dec 2007	2024-03-01	30334
Suzuki	Liana	1.6	Schrägheck	Frontantrieb	Benzin	79	107	Jan 2005	Aug 2007	2024-03-01	30335
Fiat	Sedici	1.6 16V	SUV	Frontantrieb	Benzin	79	107	Jun 2006	Oct 2014	2024-03-01	30338
Jeep	Comanche	2.5 4X4	Pick-up	Allrad	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	30341
Nissan	Skyline	2.5	Coupe	Heckantrieb	Benzin	184	250	Jan 1994	Jul 2000	2024-03-01	30350
Opel	Vectra b caravan	1.7 TD	Kombi	Frontantrieb	Diesel	60	82	Nov 1996	Dec 1997	2024-03-01	30351
VW	Golf plus v	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Nov 2007	Dec 2013	2024-03-01	30352
Subaru	Impreza	1.5 AWD	Schrägheck	Allrad	Benzin	79	107	Feb 2008	Mar 2012	2024-03-01	30355
Hyundai	Sonata v	3.3	Stufenheck	Frontantrieb	Benzin	173	235	Jun 2005	Dec 2010	2024-03-01	30356
Honda	Civic viii hatchback	1.4	Schrägheck	Frontantrieb	Benzin	73	100	Oct 2008	Dec 2011	2024-03-01	30357
Honda	Jazz iii	1.3 I	Schrägheck	Frontantrieb	Benzin	73	100	Jul 2008	Dec 2015	2025-12-01	30358
Honda	Jazz iii	1.2	Schrägheck	Frontantrieb	Benzin	66	90	Jul 2008	Dec 2015	2025-12-01	30359
Honda	Legend iv	3.7 Vtec V6 4WD	Stufenheck	Allrad	Benzin	217	295	Jul 2008	Dec 2012	2024-03-01	30360
Audi	A6 c6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	125	170	Nov 2008	Mar 2011	2024-03-01	30361
Audi	A6 c6	2.7 TDI	Stufenheck	Frontantrieb	Diesel	140	190	Oct 2008	Mar 2011	2024-03-01	30362
Audi	A6 c6	2.7 TDI Quattro	Stufenheck	Allrad	Diesel	140	190	Oct 2008	Mar 2011	2024-03-01	30363
Audi	A6 c6	2.8 FSI	Stufenheck	Frontantrieb	Benzin	140	190	Oct 2008	Mar 2011	2024-03-01	30364
Audi	A6 c6	2.8 FSI Quattro	Stufenheck	Allrad	Benzin	140	190	Oct 2008	Mar 2011	2024-03-01	30365
Audi	A6 c6	2.8 FSI Quattro	Stufenheck	Allrad	Benzin	162	220	Oct 2008	Mar 2011	2024-03-01	30366
Audi	A6 c6	2.8 FSI	Stufenheck	Frontantrieb	Benzin	162	220	Oct 2008	Mar 2011	2024-03-01	30367
Mercedes-benz	C-Klasse	C 180 Kompressor	Stufenheck	Heckantrieb	Benzin	115	156	Jan 2008	Jan 2014	2024-03-01	30368
Audi	A6 c6	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	176	240	Oct 2008	Mar 2011	2024-03-01	30369
Audi	A6 c6	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	213	290	Oct 2008	Mar 2011	2024-03-01	30370
Mercedes-benz	C-Klasse	C 350 CGI	Stufenheck	Heckantrieb	Benzin	215	292	Sep 2008	Jan 2014	2024-03-01	30371
Mercedes-benz	C-Klasse	C 180 Kompressor	Kombi	Heckantrieb	Benzin	115	156	Jan 2008	Aug 2014	2024-03-01	30372
Audi	A6 c6 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	125	170	Oct 2008	Aug 2011	2024-03-01	30373
Audi	A6 c6 avant	2.7 TDI	Kombi	Frontantrieb	Diesel	140	190	Oct 2008	Aug 2011	2024-03-01	30374
Audi	A6 c6 avant	2.7 TDI Quattro	Kombi	Allrad	Diesel	140	190	Oct 2008	Aug 2011	2024-03-01	30375
Audi	A6 c6 avant	2.8 FSI	Kombi	Frontantrieb	Benzin	140	190	Oct 2008	Aug 2011	2024-03-01	30376
Audi	A6 c6 avant	2.8 FSI	Kombi	Frontantrieb	Benzin	162	220	Oct 2008	Aug 2011	2024-03-01	30377
Audi	A6 c6 avant	2.8 FSI Quattro	Kombi	Allrad	Benzin	140	190	Oct 2008	Aug 2011	2024-03-01	30378
Audi	A6 c6 avant	2.8 FSI Quattro	Kombi	Allrad	Benzin	162	220	Oct 2008	Aug 2011	2024-03-01	30379
Audi	A6 c6 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	176	240	Oct 2008	Aug 2011	2024-03-01	30380
Audi	A6 c6 avant	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	213	290	Oct 2008	Aug 2011	2024-03-01	30381
Audi	A6 allroad c6	2.7 TDI Quattro	Kombi	Allrad	Diesel	140	190	Oct 2008	Aug 2011	2024-03-01	30382
Audi	A6 allroad c6	3.0 TDI Quattro	Kombi	Allrad	Diesel	176	240	Oct 2008	Aug 2011	2024-03-01	30383
Audi	A6 allroad c6	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	213	290	Oct 2008	Aug 2011	2024-03-01	30384
Citroën	C4 i	2.0 HDI	Schrägheck	Frontantrieb	Diesel	103	140	Jul 2008	Jul 2011	2024-03-01	30385
Citroën	C4	2.0 HDI	Coupe	Frontantrieb	Diesel	103	140	Jul 2008	Jul 2011	2024-03-01	30386
Ssangyong	Actyon	2.3	SUV	Heckantrieb	Benzin	110	150	Nov 2006	-	2025-12-01	30387
Renault	Kangoo	1.6 16V Flex	Großraumlimousine	Frontantrieb	Benzin/Ethanol	78	106	Feb 2008	-	2024-03-01	30388
Jeep	Patriot	2.4 ECO + 4X4	Geländewagen geschlossen	Allrad	Benzin/Autogas (LPG)	125	170	Jul 2008	Dec 2017	2024-03-01	30389
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	88	120	Jun 2008	Dec 2015	2024-03-01	30390
Hummer	Hummer h3	5.3 V8 AWD	Geländewagen geschlossen	Allrad	Benzin	224	305	Oct 2008	-	2024-03-01	30391
Renault	Megane ii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	77	105	May 2005	Jul 2009	2024-03-01	30392
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	100	136	Nov 2007	Jul 2018	2024-03-01	30397
VW	Touareg	3.0 TDI	SUV	Allrad	Diesel	155	211	Apr 2006	May 2010	2024-03-01	30398
Mercedes-benz	E-Klasse	E 230 T	Kombi	Heckantrieb	Benzin	150	204	May 2007	Jul 2009	2024-03-01	30399
VW	Caddy iii	1.9 TDI 4motion	Großraumlimousine	Allrad	Diesel	77	105	May 2008	Aug 2010	2024-03-01	30401
Mazda	Rx-7 ii	1.3 Turbo	Cabriolet	Heckantrieb	Benzin	147	200	Mar 1989	Dec 1991	2024-03-01	30402
Ford	C-Max	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Feb 2007	Sep 2010	2024-03-01	30403


--- Round 1 / 首次发送 ---
## 更新点

* 按现有尺寸组索引完成首轮缓存关联。
* 已处理 59 个输入 Ktype，生成 89 条 READY 映射。
* 其中 Chevrolet S10、Dodge Ram 2500、Fiat Ducato、Ford S-Max/Mondeo、Audi A4、VW Tiguan 等按已确认的驾驶室、货斗、车身长度、车顶或改款分支拆分。
* 本轮全部复用现有尺寸组，未重复抓取或新建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：59
* READY 映射行：89
* PENDING Ktype：41
* 本轮引用既有尺寸组：55
* 本轮新增或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30146_regcab_short	30146	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30146_regcab_long	30146	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30146_extcab_short	30146	Pickup	S10 II			EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30147_regcab_short	30147	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30147_regcab_long	30147	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30147_extcab_short	30147	Pickup	S10 II			EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30149	30149	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
30156	30156	Sedan	Corona T190	T190	4	EU-TOYOTA-CORONA-T190-SEDAN-01	HIGH		READY
30167_regcab_long	30167	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30167_extcab_short	30167	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30167_extcab_long	30167	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30168_regcab_long	30168	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30168_extcab_short	30168	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30168_extcab_long	30168	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30171_regcab_long	30171	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30171_extcab_short	30171	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30171_extcab_long	30171	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30175_regcab_long	30175	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30175_extcab_short	30175	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30175_extcab_long	30175	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30176_regcab_long	30176	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30176_extcab_short	30176	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30176_extcab_long	30176	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30177_regcab_long	30177	Pickup	Ram 2500 III		2	EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30177_quadcab_short	30177	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	MEDIUM	Quad Cab short-bed physical branch.	READY
30177_quadcab_long	30177	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	MEDIUM	Quad Cab long-bed physical branch.	READY
30181_regcab_long	30181	Pickup	Ram 2500 III		2	EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30181_quadcab_short	30181	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	MEDIUM	Quad Cab short-bed physical branch.	READY
30181_quadcab_long	30181	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	MEDIUM	Quad Cab long-bed physical branch.	READY
30212	30212	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	HIGH		READY
30213	30213	Convertible	SLR McLaren	R199	2	EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	HIGH		READY
30214	30214	Sedan	Arnage T		4	EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	MEDIUM	Input BodyStyle corrected from Coupe to the Arnage four-door sedan.	READY
30282	30282	SUV	Murano II	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-5D-01	HIGH		READY
30298	30298	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
30303	30303	Coupe	Skyline R32	R32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	HIGH		READY
30325	30325	Coupe	3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	HIGH		READY
30326_l1h1	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L1H1-01	MEDIUM	L1H1 physical branch.	READY
30326_l1h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L1H2-01	MEDIUM	L1H2 physical branch.	READY
30326_l2h1	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L2H1-01	MEDIUM	L2H1 physical branch.	READY
30326_l2h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L2H2-01	MEDIUM	L2H2 physical branch.	READY
30326_l3h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L3H2-01	MEDIUM	L3H2 physical branch.	READY
30326_l3h3	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L3H3-01	MEDIUM	L3H3 physical branch.	READY
30326_l4h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L4H2-01	MEDIUM	L4H2 physical branch.	READY
30326_l4h3	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L4H3-01	MEDIUM	L4H3 physical branch.	READY
30327	30327	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
30329_prefl	30329	MPV	S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30329_facelift	30329	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Facelift physical branch.	READY
30330_prefl	30330	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30330_facelift	30330	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30331_prefl	30331	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30331_facelift	30331	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30338	30338	SUV	Sedici I		5	EU-FIAT-SEDICI-SUV-01	HIGH		READY
30356	30356	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
30357	30357	Hatchback	Civic VIII		5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
30360	30360	Sedan	Legend IV	KB1	4	EU-HONDA-LEGEND-IV-SEDAN-KB1-01	HIGH		READY
30361	30361	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30362	30362	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30363	30363	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30364	30364	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30365	30365	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30366	30366	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30367	30367	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30369	30369	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30370	30370	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30373	30373	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30374	30374	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30375	30375	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30376	30376	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30377	30377	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30378	30378	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30379	30379	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30380	30380	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30381	30381	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30382	30382	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30383	30383	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30384	30384	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30385	30385	Hatchback	C4 I Phase II		5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
30386	30386	Coupe	C4 I Phase II		3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
30387	30387	SUV	Actyon I		5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
30388	30388	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
30389	30389	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
30390_prefl	30390	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	MEDIUM	Pre-facelift physical branch.	READY
30390_facelift	30390	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	MEDIUM	Facelift physical branch.	READY
30392	30392	Wagon	Megane II Grandtour Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
30397_prefl	30397	SUV	Tiguan 5N	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30397_facelift	30397	SUV	Tiguan 5N facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30398	30398	SUV	Touareg I facelift	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH		READY
30401	30401	MPV	Caddy III	2K	5	EU-VW-CADDY-III-MPV-PREFL-01	HIGH		READY
30403	30403	MPV	C-Max I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Dodge Ram 1500 II/III、Ram Bus、Ram Van、Ford F-150、Jeep Comanche、Chevrolet Avalanche II 等北美多驾驶室/货斗车型。
2. 批量建立 Hyundai Tiburon、Suzuki Liana、Honda Jazz III、Subaru Impreza GH、Mercedes-Benz W204/S204/W211、Hummer H3、Mazda RX-7 II 等乘用车尺寸组。
3. 单独解决 Nissan Skyline R33/R34 跨代、VW Golf Plus 既有高度冲突、Nissan Trade 底盘长度和其他边界不完整项目。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新完成 14 个 Ktype，新增 10 个尺寸组。
* 本轮闭合 Hyundai Tiburon、Suzuki Liana、Honda Jazz、Subaru Impreza、Mercedes-Benz C-Class、Hummer H3、Mazda RX-7 与 Opel Vectra B Caravan。([汽车数据][1])
* Mercedes-Benz W204/S204、Hummer H3、Mazda RX-7 FC3C 和 Vectra B Caravan 的车身边界及不含后视镜宽度已闭合。([汽车数据][2])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：73
* READY 映射行：103
* PENDING Ktype：27
* 已确认尺寸组：65
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30235	30235	Coupe	Tiburon II facelift	GK	3	EU-HYUNDAI-TIBURON-II-GK-FACELIFT-COUPE-3D-01	HIGH		READY
30332	30332	Sedan	Liana I facelift		4	EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	HIGH		READY
30333	30333	Sedan	Liana I facelift		4	EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	HIGH		READY
30334	30334	Hatchback	Liana I facelift		5	EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
30335	30335	Hatchback	Liana I facelift		5	EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
30351	30351	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-CARAVAN-WAGON-5D-PREFL-01	HIGH		READY
30355	30355	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	HIGH		READY
30358	30358	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	MEDIUM	European input generation label; GE five-door body.	READY
30359	30359	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	MEDIUM	European input generation label; GE five-door body.	READY
30368	30368	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	MEDIUM	156 hp Kompressor maps to the pre-facelift W204 body.	READY
30371	30371	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	HIGH	292 hp C 350 CGI pre-facelift body.	READY
30372	30372	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	MEDIUM	156 hp Kompressor maps to the pre-facelift S204 body.	READY
30391	30391	SUV	H3 I		5	EU-HUMMER-H3-I-SUV-5D-V8-01	HIGH	V8 SUV body; not H3T pickup.	READY
30402	30402	Convertible	RX-7 II facelift	FC3C	2	EU-MAZDA-RX-7-II-FC3C-CONVERTIBLE-2D-FACELIFT-01	HIGH	FC3C convertible physical body.	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-TIBURON-II-GK-FACELIFT-COUPE-3D-01	4395	1760	1330	Auto-Data Hyundai Tiburon II GK facelift 2.0	https://www.auto-data.net/en/hyundai-tiburon-ii-gk-facelift-2006-2.0-138hp-54985
EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	4350	1690	1454	Auto-Data Suzuki Liana Sedan I facelift 1.6i	https://www.auto-data.net/en/suzuki-liana-sedan-i-facelift-2004-1.6i-107hp-16511
EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	4230	1690	1550	Auto-Data Suzuki Liana Wagon I facelift	https://www.auto-data.net/en/suzuki-liana-wagon-i-facelift-2004-generation-3713
EU-OPEL-VECTRA-B-CARAVAN-WAGON-5D-PREFL-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan	https://www.auto-data.net/en/opel-vectra-b-caravan-generation-542
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475	Subaru official used-car catalog Impreza 1.5i	https://ucar.subaru.jp/php/catalog/grade.php?cat_id=10051272
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525	Auto-Data Honda Jazz II 1.4 100 Hp	https://www.auto-data.net/en/honda-jazz-ii-1.4-100hp-12138
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 180 Kompressor; Auto-Data Mercedes-Benz C-Class W204 C 350 CGI	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-180-1.8-kompressor-156hp-43161;https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-350-cgi-blueefficiency-v6-292hp-7g-tronic-44256
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	4596	1770	1459	Auto-Data Mercedes-Benz C-Class T-modell S204 C 180 Kompressor	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-c-180-1.8-kompressor-156hp-12550
EU-HUMMER-H3-I-SUV-5D-V8-01	4742	1897	1893	Auto-Data Hummer H3 5.3i V8	https://www.auto-data.net/en/hummer-h3-5.3i-v8-305hp-4x4-automatic-29832
EU-MAZDA-RX-7-II-FC3C-CONVERTIBLE-2D-FACELIFT-01	4335	1690	1270	GAZOO Mazda Savanna RX-7 Cabriolet catalog	https://gazoo.com/catalog/maker/MAZDA/SAVANNA_RX7/198904/2501614/
```

## 5. 下一步优先处理

1. 批量闭合 Dodge Ram 1500、Ram Bus、Ram Van 的驾驶室、货斗、轴距和车顶分支。
2. 处理 Chevrolet Avalanche II、Camaro V、Ford F-150、Jeep Comanche及 Nissan Trade。
3. 最后解决 Nissan Skyline R33/R34 跨代和 VW Golf Plus 高度冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/hyundai-tiburon-ii-gk-facelift-2006-2.0-138hp-54985 "Hyundai Tiburon II (GK, facelift 2006) 2.0 (138 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-180-1.8-kompressor-156hp-43161 "Mercedes-Benz C-class (W204) C 180 1.8 Kompressor (156 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 新完成 6 个 Ktype，新增 8 条 READY 映射；其中 Skyline Ktype `30304` 拆分为 R33 GT-R 与 R34 GT-R 两个物理车身，Golf Plus Ktype `30352` 拆分为改款前后两个分支。([日产汽车全球网站][1])
* 首次创建 6 个尺寸组，闭合 Chevrolet Avalanche II、Camaro V、Nissan Skyline R33/R34 与 Mercedes-Benz E-Class S211 Wagon。([Edmunds][2])
* Golf Plus 改款前后直接复用跨批次已有尺寸组，未重复输出尺寸事实。

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：79
* READY 映射行：111
* PENDING Ktype：21
* 已确认尺寸组：71
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30246	30246	Pickup	Avalanche II	GMT900	4	EU-CHEVROLET-AVALANCHE-II-GMT900-PICKUP-4D-01	HIGH		READY
30272	30272	Coupe	Camaro V		2	EU-CHEVROLET-CAMARO-V-COUPE-2D-01	HIGH		READY
30304_r33	30304	Coupe	Skyline GT-R R33	BCNR33	2	EU-NISSAN-SKYLINE-GT-R-R33-BCNR33-COUPE-2D-01	HIGH	Ktype覆盖R33与R34 GT-R两个物理车身。	READY
30304_r34	30304	Coupe	Skyline GT-R R34	BNR34	2	EU-NISSAN-SKYLINE-GT-R-R34-BNR34-COUPE-2D-01	HIGH	Ktype覆盖R33与R34 GT-R两个物理车身。	READY
30350	30350	Coupe	Skyline R33	ECR33	2	EU-NISSAN-SKYLINE-R33-ECR33-COUPE-2D-01	HIGH	250 hp版本对应R33 GTS25t Coupe物理车身。	READY
30352_prefl	30352	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	MEDIUM	改款前物理外廓。	READY
30352_facelift	30352	MPV	Golf Plus VI facelift		5	EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	MEDIUM	改款后物理外廓。	READY
30399	30399	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-5D-FACELIFT-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-AVALANCHE-II-GMT900-PICKUP-4D-01	5621	2009	1946	Edmunds 2013 Chevrolet Avalanche specifications; The Car Connection 2013 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/black-diamond-avalanche/2013/features-specs/;https://www.thecarconnection.com/specifications/chevrolet_avalanche_2013
EU-CHEVROLET-CAMARO-V-COUPE-2D-01	4836	1918	1377	Chevrolet 2010 Camaro brochure; Edmunds 2010 Chevrolet Camaro 1LT specifications	https://xr793.com/wp-content/uploads/2022/07/2010-Chevrolet-Camaro-CN.pdf;https://www.edmunds.com/chevrolet/camaro/2010/st-101110009/features-specs/
EU-NISSAN-SKYLINE-GT-R-R33-BCNR33-COUPE-2D-01	4675	1780	1360	Nissan Heritage Collection Skyline GT-R Nürburgring Time Attack	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/346_skyline_gt-r_nurburgring.html
EU-NISSAN-SKYLINE-GT-R-R34-BNR34-COUPE-2D-01	4600	1785	1360	Auto-Data Nissan Skyline GT-R X R34 2.6 Turbo 4WD; Automobile-Catalog 1999 Nissan Skyline GT-R R34	https://www.auto-data.net/en/nissan-skyline-gt-r-x-r34-2.6-i-24v-turbo-4wd-280hp-360;https://www.automobile-catalog.com/make/nissan/skyline_gtr_r34/skyline_gtr_r34/1999.html
EU-NISSAN-SKYLINE-R33-ECR33-COUPE-2D-01	4640	1720	1340	UltimateSpecs Nissan R33 Skyline GTS25t Coupe Type M	https://www.ultimatespecs.com/car-specs/Nissan/39596/Nissan-R33-Skyline-GTS25t-Coupe-Type-M.html
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-5D-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 230 station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-230-station-wagon.xhtml?oid=2461883
```

## 5. 下一步优先处理

1. 集中闭合 Dodge Ram 1500 II/III 的 Regular Cab、Extended Cab、Quad Cab 与货斗长度分支。
2. 集中处理 Dodge Ram Bus、Ram Van 的轴距、车身长度和车顶边界。
3. 最后处理 Nissan Trade、Ford F-150 与 Jeep Comanche 的驾驶室及货斗组合。

推进信号：CONTINUE

[1]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/346_skyline_gt-r_nurburgring.html?utm_source=chatgpt.com "Skyline GT-R Nürburgring Time Attack (1994: BCNR33)"
[2]: https://www.edmunds.com/chevrolet/black-diamond-avalanche/2013/features-specs/ "Used 2013 Chevrolet Black Diamond Avalanche Specs & Features | Edmunds"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 完成 6 个第二代 Dodge Ram 1500 Ktype，新增 22 条 READY 映射。
* 按 Regular Cab／Club Cab、短货斗／长货斗及 4×2／4×4 高度差异建立 8 个尺寸组。
* 长度采用官方尺寸表的**含后保险杠总长**；宽度采用车身外侧最大宽度，不含后视镜。官方 brochure 与对应规格页面能够闭合各分支三维。([汽车手册][1])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：85
* READY 映射行：133
* PENDING Ktype：15
* 已确认尺寸组：79
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30166_regcab_short	30166	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30166_regcab_long	30166	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30166_clubcab_short	30166	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed exterior branch.	READY
30166_clubcab_long	30166	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed exterior branch.	READY
30169_regcab_short	30169	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed 4x4 physical branch.	READY
30169_regcab_long	30169	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed 4x4 physical branch.	READY
30169_clubcab_short	30169	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed 4x4 exterior branch.	READY
30169_clubcab_long	30169	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed 4x4 exterior branch.	READY
30170_regcab_short	30170	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30170_regcab_long	30170	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30170_clubcab_short	30170	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed exterior branch.	READY
30170_clubcab_long	30170	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed exterior branch.	READY
30172_regcab_short	30172	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed 4x4 physical branch.	READY
30172_regcab_long	30172	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed 4x4 physical branch.	READY
30172_clubcab_short	30172	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed 4x4 exterior branch.	READY
30172_clubcab_long	30172	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed 4x4 exterior branch.	READY
30173_regcab_short	30173	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30173_regcab_long	30173	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30174_regcab_short	30174	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30174_regcab_long	30174	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30174_clubcab_short	30174	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club Cab short-bed physical branch.	READY
30174_clubcab_long	30174	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club Cab long-bed physical branch.	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	5184	2017	1826	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	5692	2017	1824	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	5690	2017	1819	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	6198	2017	1816	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	5184	2017	1897	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	5692	2017	1895	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	5690	2017	1895	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	6198	2017	1892	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
```

## 5. 下一步优先处理

1. 闭合第三代 Ram 1500 的 Regular Cab／Quad Cab、短／长货斗和驱动高度分支。
2. 集中处理 Ram Bus 与 Ram Van 的短轴、长轴车身。
3. 最后处理 Nissan Trade、Ford F-150 与 Jeep Comanche。

推进信号：CONTINUE

[1]: https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf?utm_source=chatgpt.com "ram pickup"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 完成 Jeep Comanche Ktype `30341`。
* 按四驱短货斗和四驱长货斗拆分为两个物理分支，首次创建 2 个尺寸组。
* 本轮未重新核对任何已确认尺寸组。Comanche MJ 的两种轴距对应不同车长和高度，不能合并为同一尺寸组。([Geocities][1])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：86
* READY 映射行：135
* PENDING Ktype：14
* 已确认尺寸组：81
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30341_shortbed	30341	Pickup	Comanche I	MJ	2	EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-SHORTBED-01	HIGH	四驱短货斗物理分支。	READY
30341_longbed	30341	Pickup	Comanche I	MJ	2	EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-LONGBED-01	HIGH	四驱长货斗物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-SHORTBED-01	4554	1821	1651	1988 Jeep Comanche official brochure scan; 1987 Jeep Comanche Dimensions & Specifications archive	https://autocatalogarchive.com/wp-content/uploads/2024/10/Jeep-Comanche-1988-USA-.pdf;https://www.geocities.ws/jeepcomanche8692/1987info.html
EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-LONGBED-01	4928	1821	1643	1988 Jeep Comanche official brochure scan; 1987 Jeep Comanche Dimensions & Specifications archive	https://autocatalogarchive.com/wp-content/uploads/2024/10/Jeep-Comanche-1988-USA-.pdf;https://www.geocities.ws/jeepcomanche8692/1987info.html
```

## 5. 下一步优先处理

1. 批量闭合第三代 Dodge Ram 1500 的驾驶室、货斗和驱动高度分支。
2. 集中处理 Dodge Ram Bus 与 Ram Van 的短轴、长轴及加长车身。
3. 最后处理 Nissan Trade 与 Ford F-150 的多车身边界。

推进信号：CONTINUE

[1]: https://www.geocities.ws/jeepcomanche8692/1987info.html "1987 Jeep Comanche Info -- The 1986-1992 Jeep Comanche Website"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 完成 Dodge Ram 1500 Ktype `30179`、`30182`，新增 13 条 READY 映射。
* 首次创建 8 个二驱尺寸组；相同驾驶室、货斗和改款边界由两个 Ktype 共用，不按发动机重复建组。
* 2002 与 2008 规格分别确认 Regular Cab／Quad Cab、短货斗／长货斗外廓；3.7 V6 仅派生 Regular Cab 及后期 Quad Cab短货斗，未创建不存在的 Quad Cab长货斗分支。([Edmunds][1])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：88
* READY 映射行：148
* PENDING Ktype：12
* 已确认尺寸组：89
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30179_regcab_short_prefl	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗物理分支。	READY
30179_regcab_long_prefl	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗物理分支。	READY
30179_regcab_short_facelift	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗物理分支。	READY
30179_regcab_long_facelift	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗物理分支。	READY
30179_quadcab_short_facelift	30179	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗物理分支。	READY
30182_regcab_short_prefl	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗物理分支。	READY
30182_regcab_long_prefl	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗物理分支。	READY
30182_quadcab_short_prefl	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	改款前Quad Cab短货斗物理分支。	READY
30182_quadcab_long_prefl	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	改款前Quad Cab长货斗物理分支。	READY
30182_regcab_short_facelift	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗物理分支。	READY
30182_regcab_long_facelift	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗物理分支。	READY
30182_quadcab_short_facelift	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗物理分支。	READY
30182_quadcab_long_facelift	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Quad Cab长货斗物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	5276	2029	1890	Edmunds 2002 Dodge Ram 1500 Regular Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002949/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	5834	2029	1882	Edmunds 2002 Dodge Ram 1500 Regular Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002948/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-PREFL-01	5784	2029	1897	Edmunds 2002 Dodge Ram 1500 Quad Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002963/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-PREFL-01	6342	2029	1892	Edmunds 2002 Dodge Ram 1500 Quad Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/quad-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	5276	2022	1869	Edmunds 2008 Dodge Ram 1500 Regular Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/regular-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	5834	2029	1882	Edmunds 2008 Dodge Ram 1500 Regular Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919581/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	5784	2022	1885	Edmunds 2008 Dodge Ram 1500 Quad Cab SLT 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919590/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-FACELIFT-01	6342	2022	1880	Edmunds 2008 Dodge Ram 1500 Quad Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/quad-cab/st-100919589/features-specs/
```

## 5. 下一步优先处理

1. 闭合 Ktype `30180`、`30183` 的四驱 Regular Cab／Quad Cab及短、长货斗分支。
2. 批量处理 Ktype `30186`–`30194` 的 Ram Bus与Ram Van轴距、车身长度边界。
3. 最后处理 Nissan Trade `30262` 与 Ford F-150 `30301`。

推进信号：CONTINUE

[1]: https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002948/features-specs/?utm_source=chatgpt.com "Used 2002 Dodge Ram Pickup 1500 ST Specs & Features | Edmunds"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 完成 Ktype `30180`、`30183`，新增 12 条 READY 映射。
* Ktype `30180` 按改款前后、Regular Cab／Quad Cab、短货斗／长货斗拆分为 8 个四驱物理分支。
* Ktype `30183` 的 5.9 版本关联改款前 4 个四驱分支，不创建不对应发动机生产阶段的改款后分支。
* 首次创建 8 个尺寸组；宽度均采用不含后视镜口径。([Edmunds][1])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：90
* READY 映射行：160
* PENDING Ktype：10
* 已确认尺寸组：97
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30180_regcab_short_prefl	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗四驱分支。	READY
30180_regcab_long_prefl	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗四驱分支。	READY
30180_quadcab_short_prefl	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	改款前Quad Cab短货斗四驱分支。	READY
30180_quadcab_long_prefl	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	改款前Quad Cab长货斗四驱分支。	READY
30180_regcab_short_facelift	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗四驱分支。	READY
30180_regcab_long_facelift	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗四驱分支。	READY
30180_quadcab_short_facelift	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗四驱分支。	READY
30180_quadcab_long_facelift	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Quad Cab长货斗四驱分支。	READY
30183_regcab_short_prefl	30183	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	5.9版本改款前Regular Cab短货斗分支。	READY
30183_regcab_long_prefl	30183	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	MEDIUM	5.9版本改款前Regular Cab长货斗分支。	READY
30183_quadcab_short_prefl	30183	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	5.9版本改款前Quad Cab短货斗分支。	READY
30183_quadcab_long_prefl	30183	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	5.9版本改款前Quad Cab长货斗分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	5276	2029	1946	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Regular Cab ST 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002951/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	5834	2029	1930	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Regular Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002950/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	5784	2029	1946	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Quad Cab ST 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/quad-cab/st-100002965/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	6342	2029	1941	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Quad Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002964/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-FACELIFT-01	5276	2022	1918	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Regular Cab SLT 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919586/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-FACELIFT-01	5834	2022	1913	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Regular Cab SLT 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/regular-cab/st-100919587/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-FACELIFT-01	5784	2022	1928	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Quad Cab 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/quad-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-FACELIFT-01	6342	2022	1923	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Quad Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919594/features-specs/
```

## 5. 下一步优先处理

1. 集中闭合 Ktype `30186`–`30194` 的 Dodge Ram Bus 与 Ram Van轴距、车身长度和车顶分支。
2. 处理 Nissan Trade Ktype `30262` 的底盘轴距及驾驶室边界。
3. 处理 Ford F-150 Ktype `30301` 的驾驶室和货斗组合。

推进信号：CONTINUE

[1]: https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002950/features-specs/ "Used 2002 Dodge Ram Pickup 1500 ST Specs & Features | Edmunds"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 完成 Dodge Ram Bus Ktype `30186`–`30188`，按短轴、长轴标准车身和 Maxi 加长车身拆分；5.9 L 发动机未建立短轴分支。官方资料中的三种车身长度和对应外廓已闭合。([Dezo's Garage][1])
* 完成 Dodge Ram Van 5.2 CNG Ktype `30190`，关联 Ram 2500 长轴标准长度货运车身。([Torque Brief][2])
* 本轮新增 9 条 READY 映射和 4 个尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：94
* READY 映射行：169
* PENDING Ktype：6
* 已确认尺寸组：101
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30186_swb	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
30186_lwb	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30186_maxi	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30187_lwb	30187	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30187_maxi	30187	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30188_swb	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
30188_lwb	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30188_maxi	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30190_lwb	30190	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	HIGH	B2500长轴标准长度货运车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-WAGON-III-MPV-SWB-01	4544	2027	2022	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-WAGON-III-MPV-LWB-01	5001	2027	2055	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	5662	2027	2047	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-VAN-III-VAN-LWB-01	5212	2027	2029	Edmunds 2001 Dodge Ram Cargo 2500 specifications; Dodge 1999 Ram Van official brochure	https://www.edmunds.com/dodge/ram-cargo/2001/st-100000858/features-specs/;https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf
```

## 5. 下一步优先处理

1. 批量关联 Ktype `30191`–`30194` 的 Ram Van 标准长轴与 Maxi 加长车身。
2. 闭合 Nissan Trade Ktype `30262` 的底盘轴距及驾驶室分支。
3. 闭合 Ford F-150 Ktype `30301` 的 Regular Cab、SuperCab、SuperCrew 与货斗组合。

推进信号：CONTINUE

[1]: https://xr793.com/dodge-1980-1989 "Dezo's Garage| 1980-1989 Dodge Car, CUV & SUV PDF Sales Brochure/Catalog/Flyer/Info Aspen, B100, B200, B300, Challenger, Colt, D150, D200, D300, D50, Diplomat, Mirada, Omni, Ramcharger, St Regis, Aries, B150, B250, B350, Ram 50, 400, Rampage, 600, Charger, Conquest, D100, Daytona, Mini Ram, Caravan, Lancer, Dakota, Raider, Shadow, Dynasty, Spirit | Dezo's Garage"
[2]: https://torquebrief.com/car-specs/dodge-ram-van-2500-2wd-cng-2001-technical-specs/?utm_source=chatgpt.com "2001 Dodge Ram Van 2500 2WD CNG Specs"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 完成 Dodge Ram Van Ktype `30191`–`30194`，按短轴、长轴标准车身和 Maxi 加长车身建立关联；发动机和燃料差异未重复建组。
* 完成 Ford F-150 Ktype `30301`，拆分为普通 SuperCrew 5.5-ft 货斗、SVT Raptor SuperCab 和 SVT Raptor SuperCrew 三个物理外廓。官方资料显示普通 6.2 L 车型对应 145 英寸轴距的 SuperCrew 5.5-ft 货斗；Raptor 宽体需单独建组。
* 本轮新增 13 条 READY 映射、5 个尺寸组；Ram Van 长轴标准车身复用既有尺寸组，未重复输出。Ram Van 的短轴、标准长轴和 Maxi 车身边界依据车型资料闭合。

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：99
* READY 映射行：182
* PENDING Ktype：1
* 已确认尺寸组：106
* 当前仅剩 Nissan Trade Ktype `30262` 未闭合。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30191_lwb	30191	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30191_maxi	30191	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30192_swb	30192	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30192_lwb	30192	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30193_swb	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30193_lwb	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30193_maxi	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30194_swb	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30194_lwb	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30194_maxi	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30301_supercrew_55	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-PICKUP-SUPERCREW-55-4X4-01	HIGH	普通车身SuperCrew 5.5-ft货斗四驱分支。	READY
30301_raptor_supercab	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCAB-55-01	HIGH	SVT Raptor SuperCab宽体分支。	READY
30301_raptor_supercrew	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCREW-55-01	HIGH	SVT Raptor SuperCrew宽体分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-VAN-III-VAN-SWB-01	4755	2027	2019	Dodge 1999 Ram Van official brochure; AutoDetective 1999 Dodge Ram Van 1500 SWB specifications	https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf;https://www.autodetective.com/directory/1999/dodge/ram-van/trim/1500-swb/
EU-DODGE-RAM-VAN-III-VAN-MAXI-01	5872	2027	2029	Dodge 1999 Ram Van official brochure; AutoDetective 2001 Dodge Ram Van 1500 Maxivan specifications	https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf;https://www.autodetective.com/directory/2001/dodge/ram-van/trim/1500-maxivan/
EU-FORD-USA-F150-XII-PICKUP-SUPERCREW-55-4X4-01	5889	2012	1927	Ford 2011 F-150 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_f150.pdf
EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCAB-55-01	5603	2192	1994	Edmunds 2011 Ford F-150 SuperCab SVT Raptor specifications	https://www.edmunds.com/ford/f-150/2011/supercab/st-101307095/features-specs/
EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCREW-55-01	5895	2192	1991	Edmunds 2011 Ford F-150 SuperCrew SVT Raptor specifications	https://www.edmunds.com/ford/f-150/2011/svt-raptor/features-specs/
```

## 5. 下一步优先处理

1. 仅处理 Nissan Trade Ktype `30262`。
2. 核对其底盘驾驶室的轴距分支、完整长宽高及不含后视镜宽度。
3. 闭合后立即进行一次机械检查，并输出两张最终完整 TSV、两个指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* Nissan Trade Ktype `30262` 已闭合为 Trade 75 单排底盘驾驶室，尺寸为 `4615 × 1800 × 2115 mm`，宽度采用不含后视镜口径。([DENSO][1])
* 已完成唯一一次机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸与来源字段完整、无孤立尺寸组。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：183
* PENDING：0
* DIMENSION_GROUP：109
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30146_regcab_short	30146	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30146_regcab_long	30146	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30146_extcab_short	30146	Pickup	S10 II			EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30147_regcab_short	30147	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30147_regcab_long	30147	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30147_extcab_short	30147	Pickup	S10 II			EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30149	30149	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
30156	30156	Sedan	Corona T190	T190	4	EU-TOYOTA-CORONA-T190-SEDAN-01	HIGH		READY
30166_regcab_short	30166	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30166_regcab_long	30166	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30166_clubcab_short	30166	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed exterior branch.	READY
30166_clubcab_long	30166	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed exterior branch.	READY
30167_regcab_long	30167	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30167_extcab_short	30167	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30167_extcab_long	30167	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30168_regcab_long	30168	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30168_extcab_short	30168	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30168_extcab_long	30168	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30169_regcab_short	30169	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed 4x4 physical branch.	READY
30169_regcab_long	30169	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed 4x4 physical branch.	READY
30169_clubcab_short	30169	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed 4x4 exterior branch.	READY
30169_clubcab_long	30169	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed 4x4 exterior branch.	READY
30170_regcab_short	30170	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30170_regcab_long	30170	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30170_clubcab_short	30170	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed exterior branch.	READY
30170_clubcab_long	30170	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed exterior branch.	READY
30171_regcab_long	30171	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30171_extcab_short	30171	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30171_extcab_long	30171	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30172_regcab_short	30172	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed 4x4 physical branch.	READY
30172_regcab_long	30172	Pickup	Ram 1500 II	BE	2	EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed 4x4 physical branch.	READY
30172_clubcab_short	30172	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club/Quad Cab short-bed 4x4 exterior branch.	READY
30172_clubcab_long	30172	Pickup	Ram 1500 II	BE		EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club/Quad Cab long-bed 4x4 exterior branch.	READY
30173_regcab_short	30173	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30173_regcab_long	30173	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30174_regcab_short	30174	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	MEDIUM	Regular Cab short-bed physical branch.	READY
30174_regcab_long	30174	Pickup	Ram 1500 II	BR	2	EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30174_clubcab_short	30174	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	MEDIUM	Club Cab short-bed physical branch.	READY
30174_clubcab_long	30174	Pickup	Ram 1500 II	BR		EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	MEDIUM	Club Cab long-bed physical branch.	READY
30175_regcab_long	30175	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30175_extcab_short	30175	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30175_extcab_long	30175	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30176_regcab_long	30176	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30176_extcab_short	30176	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Extended Cab short-bed physical branch.	READY
30176_extcab_long	30176	Pickup	Ram 2500 II			EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Extended Cab long-bed physical branch.	READY
30177_regcab_long	30177	Pickup	Ram 2500 III		2	EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30177_quadcab_short	30177	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	MEDIUM	Quad Cab short-bed physical branch.	READY
30177_quadcab_long	30177	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	MEDIUM	Quad Cab long-bed physical branch.	READY
30179_regcab_short_prefl	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗物理分支。	READY
30179_regcab_long_prefl	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗物理分支。	READY
30179_regcab_short_facelift	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗物理分支。	READY
30179_regcab_long_facelift	30179	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗物理分支。	READY
30179_quadcab_short_facelift	30179	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗物理分支。	READY
30180_regcab_short_prefl	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗四驱分支。	READY
30180_regcab_long_prefl	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗四驱分支。	READY
30180_quadcab_short_prefl	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	改款前Quad Cab短货斗四驱分支。	READY
30180_quadcab_long_prefl	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	改款前Quad Cab长货斗四驱分支。	READY
30180_regcab_short_facelift	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗四驱分支。	READY
30180_regcab_long_facelift	30180	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗四驱分支。	READY
30180_quadcab_short_facelift	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗四驱分支。	READY
30180_quadcab_long_facelift	30180	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Quad Cab长货斗四驱分支。	READY
30181_regcab_long	30181	Pickup	Ram 2500 III		2	EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab long-bed physical branch.	READY
30181_quadcab_short	30181	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	MEDIUM	Quad Cab short-bed physical branch.	READY
30181_quadcab_long	30181	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	MEDIUM	Quad Cab long-bed physical branch.	READY
30182_regcab_short_prefl	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	改款前Regular Cab短货斗物理分支。	READY
30182_regcab_long_prefl	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	MEDIUM	改款前Regular Cab长货斗物理分支。	READY
30182_quadcab_short_prefl	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	改款前Quad Cab短货斗物理分支。	READY
30182_quadcab_long_prefl	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	改款前Quad Cab长货斗物理分支。	READY
30182_regcab_short_facelift	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Regular Cab短货斗物理分支。	READY
30182_regcab_long_facelift	30182	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Regular Cab长货斗物理分支。	READY
30182_quadcab_short_facelift	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	MEDIUM	改款后Quad Cab短货斗物理分支。	READY
30182_quadcab_long_facelift	30182	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-FACELIFT-01	MEDIUM	改款后Quad Cab长货斗物理分支。	READY
30183_regcab_short_prefl	30183	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	MEDIUM	5.9版本改款前Regular Cab短货斗分支。	READY
30183_regcab_long_prefl	30183	Pickup	Ram 1500 III		2	EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	MEDIUM	5.9版本改款前Regular Cab长货斗分支。	READY
30183_quadcab_short_prefl	30183	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	MEDIUM	5.9版本改款前Quad Cab短货斗分支。	READY
30183_quadcab_long_prefl	30183	Pickup	Ram 1500 III		4	EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	MEDIUM	5.9版本改款前Quad Cab长货斗分支。	READY
30186_swb	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
30186_lwb	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30186_maxi	30186	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30187_lwb	30187	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30187_maxi	30187	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30188_swb	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
30188_lwb	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-LWB-01	MEDIUM	长轴标准长度乘用车身。	READY
30188_maxi	30188	MPV	Ram Wagon III			EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	MEDIUM	长轴Maxi加长乘用车身。	READY
30190_lwb	30190	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	HIGH	B2500长轴标准长度货运车身。	READY
30191_lwb	30191	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30191_maxi	30191	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30192_swb	30192	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30192_lwb	30192	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30193_swb	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30193_lwb	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30193_maxi	30193	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30194_swb	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-SWB-01	MEDIUM	短轴货运车身。	READY
30194_lwb	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-LWB-01	MEDIUM	长轴标准货运车身。	READY
30194_maxi	30194	Van	Ram Van III			EU-DODGE-RAM-VAN-III-VAN-MAXI-01	MEDIUM	Maxi加长货运车身。	READY
30212	30212	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	HIGH		READY
30213	30213	Convertible	SLR McLaren	R199	2	EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	HIGH		READY
30214	30214	Sedan	Arnage T		4	EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	MEDIUM	Input BodyStyle corrected from Coupe to the Arnage four-door sedan.	READY
30235	30235	Coupe	Tiburon II facelift	GK	3	EU-HYUNDAI-TIBURON-II-GK-FACELIFT-COUPE-3D-01	HIGH		READY
30246	30246	Pickup	Avalanche II	GMT900	4	EU-CHEVROLET-AVALANCHE-II-GMT900-PICKUP-4D-01	HIGH		READY
30262	30262	Pickup	Trade TC/TX		2	EU-NISSAN-TRADE-TC-TX-CHASSIS-CAB-2D-01	MEDIUM	Trade 75 single-cab chassis-cab; LD23 Model Year TX.	READY
30272	30272	Coupe	Camaro V		2	EU-CHEVROLET-CAMARO-V-COUPE-2D-01	HIGH		READY
30282	30282	SUV	Murano II	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-5D-01	HIGH		READY
30298	30298	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
30301_supercrew_55	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-PICKUP-SUPERCREW-55-4X4-01	HIGH	普通车身SuperCrew 5.5-ft货斗四驱分支。	READY
30301_raptor_supercab	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCAB-55-01	HIGH	SVT Raptor SuperCab宽体分支。	READY
30301_raptor_supercrew	30301	Pickup	F-150 XII		4	EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCREW-55-01	HIGH	SVT Raptor SuperCrew宽体分支。	READY
30303	30303	Coupe	Skyline R32	R32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	HIGH		READY
30304_r33	30304	Coupe	Skyline GT-R R33	BCNR33	2	EU-NISSAN-SKYLINE-GT-R-R33-BCNR33-COUPE-2D-01	HIGH	Ktype覆盖R33与R34 GT-R两个物理车身。	READY
30304_r34	30304	Coupe	Skyline GT-R R34	BNR34	2	EU-NISSAN-SKYLINE-GT-R-R34-BNR34-COUPE-2D-01	HIGH	Ktype覆盖R33与R34 GT-R两个物理车身。	READY
30325	30325	Coupe	3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	HIGH		READY
30326_l1h1	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L1H1-01	MEDIUM	L1H1 physical branch.	READY
30326_l1h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L1H2-01	MEDIUM	L1H2 physical branch.	READY
30326_l2h1	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L2H1-01	MEDIUM	L2H1 physical branch.	READY
30326_l2h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L2H2-01	MEDIUM	L2H2 physical branch.	READY
30326_l3h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L3H2-01	MEDIUM	L3H2 physical branch.	READY
30326_l3h3	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L3H3-01	MEDIUM	L3H3 physical branch.	READY
30326_l4h2	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L4H2-01	MEDIUM	L4H2 physical branch.	READY
30326_l4h3	30326	Van	Ducato III	X250		EU-FIAT-DUCATO-III-VAN-L4H3-01	MEDIUM	L4H3 physical branch.	READY
30327	30327	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
30329_prefl	30329	MPV	S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30329_facelift	30329	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Facelift physical branch.	READY
30330_prefl	30330	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30330_facelift	30330	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30331_prefl	30331	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30331_facelift	30331	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30332	30332	Sedan	Liana I facelift		4	EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	HIGH		READY
30333	30333	Sedan	Liana I facelift		4	EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	HIGH		READY
30334	30334	Hatchback	Liana I facelift		5	EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
30335	30335	Hatchback	Liana I facelift		5	EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
30338	30338	SUV	Sedici I		5	EU-FIAT-SEDICI-SUV-01	HIGH		READY
30341_shortbed	30341	Pickup	Comanche I	MJ	2	EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-SHORTBED-01	HIGH	四驱短货斗物理分支。	READY
30341_longbed	30341	Pickup	Comanche I	MJ	2	EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-LONGBED-01	HIGH	四驱长货斗物理分支。	READY
30350	30350	Coupe	Skyline R33	ECR33	2	EU-NISSAN-SKYLINE-R33-ECR33-COUPE-2D-01	HIGH	250 hp版本对应R33 GTS25t Coupe物理车身。	READY
30351	30351	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-CARAVAN-WAGON-5D-PREFL-01	HIGH		READY
30352_prefl	30352	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	MEDIUM	改款前物理外廓。	READY
30352_facelift	30352	MPV	Golf Plus VI facelift		5	EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	MEDIUM	改款后物理外廓。	READY
30355	30355	Hatchback	Impreza III	GH	5	EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	HIGH		READY
30356	30356	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
30357	30357	Hatchback	Civic VIII		5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
30358	30358	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	MEDIUM	European input generation label; GE five-door body.	READY
30359	30359	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	MEDIUM	European input generation label; GE five-door body.	READY
30360	30360	Sedan	Legend IV	KB1	4	EU-HONDA-LEGEND-IV-SEDAN-KB1-01	HIGH		READY
30361	30361	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30362	30362	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30363	30363	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30364	30364	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30365	30365	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30366	30366	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30367	30367	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30368	30368	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	MEDIUM	156 hp Kompressor maps to the pre-facelift W204 body.	READY
30369	30369	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30370	30370	Sedan	A6 C6 facelift	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH		READY
30371	30371	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	HIGH	292 hp C 350 CGI pre-facelift body.	READY
30372	30372	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	MEDIUM	156 hp Kompressor maps to the pre-facelift S204 body.	READY
30373	30373	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30374	30374	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30375	30375	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30376	30376	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30377	30377	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30378	30378	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30379	30379	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30380	30380	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30381	30381	Wagon	A6 C6 Avant facelift	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH		READY
30382	30382	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30383	30383	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30384	30384	Wagon	A6 C6 allroad facelift		5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH		READY
30385	30385	Hatchback	C4 I Phase II		5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
30386	30386	Coupe	C4 I Phase II		3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
30387	30387	SUV	Actyon I		5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
30388	30388	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
30389	30389	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
30390_prefl	30390	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	MEDIUM	Pre-facelift physical branch.	READY
30390_facelift	30390	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	MEDIUM	Facelift physical branch.	READY
30391	30391	SUV	H3 I		5	EU-HUMMER-H3-I-SUV-5D-V8-01	HIGH	V8 SUV body; not H3T pickup.	READY
30392	30392	Wagon	Megane II Grandtour Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
30397_prefl	30397	SUV	Tiguan 5N	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	Pre-facelift physical branch.	READY
30397_facelift	30397	SUV	Tiguan 5N facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	Facelift physical branch.	READY
30398	30398	SUV	Touareg I facelift	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH		READY
30399	30399	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-5D-FACELIFT-01	HIGH		READY
30401	30401	MPV	Caddy III	2K	5	EU-VW-CADDY-III-MPV-PREFL-01	HIGH		READY
30402	30402	Convertible	RX-7 II facelift	FC3C	2	EU-MAZDA-RX-7-II-FC3C-CONVERTIBLE-2D-FACELIFT-01	HIGH	FC3C convertible physical body.	READY
30403	30403	MPV	C-Max I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3301-3400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	4793	1725	1577	Edmunds Chevrolet S-10 Regular Cab specifications	https://www.edmunds.com/chevrolet/s-10/1998/regular-cab/features-specs/
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	5197	1725	1577	Edmunds Chevrolet S-10 Regular Cab specifications	https://www.edmunds.com/chevrolet/s-10/1998/regular-cab/features-specs/
EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	5164	1725	1580	Edmunds Chevrolet S-10 Extended Cab specifications	https://www.edmunds.com/chevrolet/s-10/1998/extended-cab/features-specs/
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	4793	1725	1621	Edmunds Chevrolet S-10 Regular Cab 4WD specifications	https://www.edmunds.com/chevrolet/s-10/1998/regular-cab/features-specs/
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	5197	1725	1661	Edmunds Chevrolet S-10 Regular Cab 4WD specifications	https://www.edmunds.com/chevrolet/s-10/1998/regular-cab/features-specs/
EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	5164	1725	1621	Edmunds Chevrolet S-10 Extended Cab 4WD specifications	https://www.edmunds.com/chevrolet/s-10/1998/extended-cab/features-specs/
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675	Auto-Data Honda CR-V III specifications	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-12335
EU-TOYOTA-CORONA-T190-SEDAN-01	4520	1695	1410	Toyota Global 75 Years Vehicle Lineage Corona	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008512A/
EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-SHORTBED-01	5184	2017	1826	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-REGCAB-LONGBED-01	5692	2017	1824	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-SHORTBED-01	5690	2017	1819	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BR-PICKUP-CLUBCAB-LONGBED-01	6198	2017	1816	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	5692	2014	1848	Dodge 1995 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	5695	2014	1847	Dodge 1995 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	6200	2014	1847	Dodge 1995 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-SHORTBED-01	5184	2017	1897	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-REGCAB-LONGBED-01	5692	2017	1895	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-SHORTBED-01	5690	2017	1895	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-1500-II-BE-PICKUP-CLUBCAB-LONGBED-01	6198	2017	1892	Dodge 1995 RAM Pickup official brochure - Dodge RAM Pickup Dimensions	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_1995.pdf
EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	5834	2029	1875	Dodge 2008 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	5784	2029	1890	Dodge 2008 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	6342	2029	1890	Dodge 2008 Ram Pickup official brochure	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-PREFL-01	5276	2029	1890	Edmunds 2002 Dodge Ram 1500 Regular Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002949/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-PREFL-01	5834	2029	1882	Edmunds 2002 Dodge Ram 1500 Regular Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002948/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-SHORTBED-FACELIFT-01	5276	2022	1869	Edmunds 2008 Dodge Ram 1500 Regular Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/regular-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-REGCAB-LONGBED-FACELIFT-01	5834	2029	1882	Edmunds 2008 Dodge Ram 1500 Regular Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919581/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-FACELIFT-01	5784	2022	1885	Edmunds 2008 Dodge Ram 1500 Quad Cab SLT 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919590/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-PREFL-01	5276	2029	1946	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Regular Cab ST 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002951/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-PREFL-01	5834	2029	1930	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Regular Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002950/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-PREFL-01	5784	2029	1946	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Quad Cab ST 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/quad-cab/st-100002965/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-PREFL-01	6342	2029	1941	Dodge 2002 Ram Pickup brochure; Edmunds 2002 Dodge Ram 1500 Quad Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2002.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002964/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-SHORTBED-FACELIFT-01	5276	2022	1918	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Regular Cab SLT 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919586/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-REGCAB-LONGBED-FACELIFT-01	5834	2022	1913	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Regular Cab SLT 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/regular-cab/st-100919587/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-SHORTBED-FACELIFT-01	5784	2022	1928	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Quad Cab 4WD Short Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/quad-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-4WD-QUADCAB-LONGBED-FACELIFT-01	6342	2022	1923	Dodge 2008 Ram Pickup brochure; Edmunds 2008 Dodge Ram 1500 Quad Cab ST 4WD Long Bed specifications	https://www.auto-brochures.com/makes/Dodge/Ram%20Pickup/Dodge_US%20RamPickup_2008.pdf;https://www.edmunds.com/dodge/ram-pickup-1500/2008/st-100919594/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-SHORTBED-PREFL-01	5784	2029	1897	Edmunds 2002 Dodge Ram 1500 Quad Cab ST 2WD Short Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/st-100002963/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-PREFL-01	6342	2029	1892	Edmunds 2002 Dodge Ram 1500 Quad Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2002/quad-cab/features-specs/
EU-DODGE-RAM-1500-III-PICKUP-2WD-QUADCAB-LONGBED-FACELIFT-01	6342	2022	1880	Edmunds 2008 Dodge Ram 1500 Quad Cab ST 2WD Long Bed specifications	https://www.edmunds.com/dodge/ram-pickup-1500/2008/quad-cab/st-100919589/features-specs/
EU-DODGE-RAM-WAGON-III-MPV-SWB-01	4544	2027	2022	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-WAGON-III-MPV-LWB-01	5001	2027	2055	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-WAGON-III-MPV-MAXI-01	5662	2027	2047	Dodge 1987 Ram Van official brochure; Dodge 1989 Ram Wagons official brochure	https://xr793.com/wp-content/uploads/2023/08/1987-Dodge-Van.pdf;https://xr793.com/wp-content/uploads/2019/08/1989-Dodge-Ram-Wagons.pdf
EU-DODGE-RAM-VAN-III-VAN-LWB-01	5212	2027	2029	Edmunds 2001 Dodge Ram Cargo 2500 specifications; Dodge 1999 Ram Van official brochure	https://www.edmunds.com/dodge/ram-cargo/2001/st-100000858/features-specs/;https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf
EU-DODGE-RAM-VAN-III-VAN-MAXI-01	5872	2027	2029	Dodge 1999 Ram Van official brochure; AutoDetective 2001 Dodge Ram Van 1500 Maxivan specifications	https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf;https://www.autodetective.com/directory/2001/dodge/ram-van/trim/1500-maxivan/
EU-DODGE-RAM-VAN-III-VAN-SWB-01	4755	2027	2019	Dodge 1999 Ram Van official brochure; AutoDetective 1999 Dodge Ram Van 1500 SWB specifications	https://xr793.com/wp-content/uploads/2018/09/1999-Dodge-Ram-Van.pdf;https://www.autodetective.com/directory/1999/dodge/ram-van/trim/1500-swb/
EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	5088	1847	1334	Edmunds 1997 Ford Thunderbird specifications	https://www.edmunds.com/ford/thunderbird/1997/features-specs/
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281	Mercedes-Benz Public Archive SLR McLaren Roadster	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLR-McLaren-Roadster.xhtml?oid=2461965
EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	5400	1900	1515	Automobile-Detail Bentley Arnage T specifications	https://www.automobile-detail.com/bentley-arnage-t-car-technical-specifications-2/
EU-HYUNDAI-TIBURON-II-GK-FACELIFT-COUPE-3D-01	4395	1760	1330	Auto-Data Hyundai Tiburon II GK facelift 2.0	https://www.auto-data.net/en/hyundai-tiburon-ii-gk-facelift-2006-2.0-138hp-54985
EU-CHEVROLET-AVALANCHE-II-GMT900-PICKUP-4D-01	5621	2009	1946	Edmunds 2013 Chevrolet Avalanche specifications; The Car Connection 2013 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/black-diamond-avalanche/2013/features-specs/;https://www.thecarconnection.com/specifications/chevrolet_avalanche_2013
EU-NISSAN-TRADE-TC-TX-CHASSIS-CAB-2D-01	4615	1800	2115	AutoCasion Nissan Trade 75 Chasis Cabina 1996	https://www.autocasion.com/marcas/nissan/trade-industrial/trade-75-chasis-cabina-2-puertas-18486
EU-CHEVROLET-CAMARO-V-COUPE-2D-01	4836	1918	1377	Chevrolet 2010 Camaro brochure; Edmunds 2010 Chevrolet Camaro 1LT specifications	https://xr793.com/wp-content/uploads/2022/07/2010-Chevrolet-Camaro-CN.pdf;https://www.edmunds.com/chevrolet/camaro/2010/st-101110009/features-specs/
EU-NISSAN-MURANO-II-Z51-SUV-5D-01	4860	1885	1720	Auto-Data Nissan Murano II Z51 specifications	https://www.auto-data.net/en/nissan-murano-ii-z51-generation-3814
EU-FORD-USA-F150-XII-PICKUP-SUPERCREW-55-4X4-01	5889	2012	1927	Ford 2011 F-150 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_f150.pdf
EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCAB-55-01	5603	2192	1994	Edmunds 2011 Ford F-150 SuperCab SVT Raptor specifications	https://www.edmunds.com/ford/f-150/2011/supercab/st-101307095/features-specs/
EU-FORD-USA-F150-XII-RAPTOR-PICKUP-SUPERCREW-55-01	5895	2192	1991	Edmunds 2011 Ford F-150 SuperCrew SVT Raptor specifications	https://www.edmunds.com/ford/f-150/2011/svt-raptor/features-specs/
EU-NISSAN-SKYLINE-R32-COUPE-2D-01	4530	1695	1325	GAZOO Nissan Skyline GT-R R32 catalog	https://gazoo.com/catalog/maker/NISSAN/SKYLINE/198905/1505826/
EU-NISSAN-SKYLINE-GT-R-R33-BCNR33-COUPE-2D-01	4675	1780	1360	Nissan Heritage Collection Skyline GT-R Nürburgring Time Attack	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/346_skyline_gt-r_nurburgring.html
EU-NISSAN-SKYLINE-GT-R-R34-BNR34-COUPE-2D-01	4600	1785	1360	Auto-Data Nissan Skyline GT-R X R34 2.6 Turbo 4WD; Automobile-Catalog 1999 Nissan Skyline GT-R R34	https://www.auto-data.net/en/nissan-skyline-gt-r-x-r34-2.6-i-24v-turbo-4wd-280hp-360;https://www.automobile-catalog.com/make/nissan/skyline_gtr_r34/skyline_gtr_r34/1999.html
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369	Auto-Data BMW 3 Series Coupe E46 facelift	https://www.auto-data.net/en/bmw-3-series-coupe-e46-facelift-2003-generation-8259
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779	Fiat Professional Ducato dimensions	https://www.fiatprofessional.com/ducato/van/dimensions
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data Fiat Bravo II 198 specifications	https://www.auto-data.net/en/fiat-bravo-ii-198-generation-1617
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658	Auto-Data Ford S-MAX 2006 specifications	https://www.auto-data.net/en/ford-s-max-2.0-i-16v-145hp-8113
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Automobile-Catalog 2010 Ford S-Max specifications	https://www.automobile-catalog.com/car/2010/1234850/ford_s-max_2_0_titanium.html
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Auto-Data Ford Mondeo III Wagon specifications	https://www.auto-data.net/en/ford-mondeo-iii-wagon-generation-1696
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Auto-Data Ford Mondeo III Wagon facelift specifications	https://www.auto-data.net/en/ford-mondeo-iii-wagon-facelift-2010-generation-4284
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Auto-Data Ford Mondeo III Hatchback specifications	https://www.auto-data.net/en/ford-mondeo-iii-hatchback-generation-1695
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Auto-Data Ford Mondeo III Hatchback facelift specifications	https://www.auto-data.net/en/ford-mondeo-iii-hatchback-facelift-2010-2.0-16v-145hp-duratec-20141
EU-SUZUKI-LIANA-I-FACELIFT-SEDAN-4D-01	4350	1690	1454	Auto-Data Suzuki Liana Sedan I facelift 1.6i	https://www.auto-data.net/en/suzuki-liana-sedan-i-facelift-2004-1.6i-107hp-16511
EU-SUZUKI-LIANA-I-FACELIFT-HATCHBACK-5D-01	4230	1690	1550	Auto-Data Suzuki Liana Wagon I facelift	https://www.auto-data.net/en/suzuki-liana-wagon-i-facelift-2004-generation-3713
EU-FIAT-SEDICI-SUV-01	4115	1755	1620	Auto-Data Fiat Sedici specifications	https://www.auto-data.net/en/fiat-sedici-1.6-i-16v-107hp-7221
EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-SHORTBED-01	4554	1821	1651	1988 Jeep Comanche official brochure scan; 1987 Jeep Comanche Dimensions & Specifications archive	https://autocatalogarchive.com/wp-content/uploads/2024/10/Jeep-Comanche-1988-USA-.pdf;https://www.geocities.ws/jeepcomanche8692/1987info.html
EU-JEEP-COMANCHE-I-MJ-PICKUP-4X4-LONGBED-01	4928	1821	1643	1988 Jeep Comanche official brochure scan; 1987 Jeep Comanche Dimensions & Specifications archive	https://autocatalogarchive.com/wp-content/uploads/2024/10/Jeep-Comanche-1988-USA-.pdf;https://www.geocities.ws/jeepcomanche8692/1987info.html
EU-NISSAN-SKYLINE-R33-ECR33-COUPE-2D-01	4640	1720	1340	UltimateSpecs Nissan R33 Skyline GTS25t Coupe Type M	https://www.ultimatespecs.com/car-specs/Nissan/39596/Nissan-R33-Skyline-GTS25t-Coupe-Type-M.html
EU-OPEL-VECTRA-B-CARAVAN-WAGON-5D-PREFL-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan	https://www.auto-data.net/en/opel-vectra-b-caravan-generation-542
EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 1.9 TDI specifications	https://www.auto-data.net/en/volkswagen-golf-v-plus-1.9-tdi-105hp-8656
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus specifications	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475	Subaru official used-car catalog Impreza 1.5i	https://ucar.subaru.jp/php/catalog/grade.php?cat_id=10051272
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475	Auto-Data Hyundai Sonata V NF 3.3 specifications	https://www.auto-data.net/en/hyundai-sonata-v-nf-3.3i-v6-24v-235hp-automatic-13822
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460	Auto-Data Honda Civic VIII Hatchback 5D 1.4 i-VTEC	https://www.auto-data.net/en/honda-civic-viii-hatchback-5d-1.4-i-vtec-100hp-41968
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525	Auto-Data Honda Jazz II 1.4 100 Hp	https://www.auto-data.net/en/honda-jazz-ii-1.4-100hp-12138
EU-HONDA-LEGEND-IV-SEDAN-KB1-01	4957	1845	1450	Auto-Data Honda Legend IV KB1 3.7 VTEC	https://www.auto-data.net/en/honda-legend-iv-kb1-facelift-2008-3.7-vtec-v6-295hp-sh-awd-12172
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459	Auto-Data Audi A6 C6 facelift specifications	https://www.auto-data.net/en/audi-a6-4f-c6-facelift-2008-3.0-tfsi-v6-290hp-quattro-tiptronic-4659
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 180 Kompressor; Auto-Data Mercedes-Benz C-Class W204 C 350 CGI	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-180-1.8-kompressor-156hp-43161;https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-350-cgi-blueefficiency-v6-292hp-7g-tronic-44256
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	4596	1770	1459	Auto-Data Mercedes-Benz C-Class T-modell S204 C 180 Kompressor	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-c-180-1.8-kompressor-156hp-12550
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463	Auto-Data Audi A6 Avant C6 facelift specifications	https://www.auto-data.net/en/audi-a6-avant-4f-c6-facelift-2008-generation-4368
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521	Auto-Data Audi A6 model specifications - C6 allroad facelift	https://www.auto-data.net/en/audi-a6-model-511
EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	4275	1773	1458	Auto-Data Citroen C4 I Hatchback Phase II specifications	https://www.auto-data.net/en/citroen-c4-i-hatchback-phase-ii-2008-2.0-hdi-140hp-fap-27969
EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	4288	1769	1456	Auto-Data Citroen C4 I Coupe Phase II specifications	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-ii-2008-2.0-hdi-16v-140hp-fap-27907
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740	Auto-Data SsangYong Actyon 2.3 specifications	https://www.auto-data.net/en/ssangyong-actyon-2.3-150hp-15988
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data Renault Kangoo II specifications	https://www.auto-data.net/en/renault-kangoo-ii-1.6-16v-106hp-33902
EU-JEEP-PATRIOT-I-MK74-SUV-01	4408	1785	1658	Auto-Data Jeep Patriot specifications	https://www.auto-data.net/en/jeep-patriot-2.4-i-16v-174hp-1174
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 8K specifications	https://www.auto-data.net/en/audi-a4-avant-b8-8k-generation-1085
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 model specifications - B8 Avant facelift	https://www.auto-data.net/en/audi-a4-model-501
EU-HUMMER-H3-I-SUV-5D-V8-01	4742	1897	1893	Auto-Data Hummer H3 5.3i V8	https://www.auto-data.net/en/hummer-h3-5.3i-v8-305hp-4x4-automatic-29832
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour specifications	https://www.auto-data.net/en/renault-megane-ii-grandtour-1.9-dci-110hp-fap-30328
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data Volkswagen Tiguan I specifications	https://www.auto-data.net/en/volkswagen-tiguan-2.0-tdi-140hp-44138
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data Volkswagen Tiguan I facelift specifications	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-2.0-tsi-180hp-4motion-44117
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726	Auto-Data Volkswagen Touareg I 7L specifications	https://www.auto-data.net/en/volkswagen-touareg-i-7l-3.0-tdi-224hp-4motion-tiptronic-8513
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-5D-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 230 station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-230-station-wagon.xhtml?oid=2461883
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833	Auto-Data Volkswagen Caddy III 4MOTION specifications	https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-105hp-dpf-4motion-50631
EU-MAZDA-RX-7-II-FC3C-CONVERTIBLE-2D-FACELIFT-01	4335	1690	1270	GAZOO Mazda Savanna RX-7 Cabriolet catalog	https://gazoo.com/catalog/maker/MAZDA/SAVANNA_RX7/198904/2501614/
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588	Honest John Ford C-MAX 1.8 TDCi specifications	https://www.honestjohn.co.uk/specs/detail/?v=MFORCMAX0034
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3301-3400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.denso-am.eu/catalog/pv/30262?utm_source=chatgpt.com "Car parts for NISSAN TRADE Platform/Chassis, 2.3 D, 55kW(75ps), LD23 | DENSO"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3301-3400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3301-3400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4141 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1968 行）

