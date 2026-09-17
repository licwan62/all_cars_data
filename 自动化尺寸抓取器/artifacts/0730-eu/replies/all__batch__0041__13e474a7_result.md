# 任务：all 第 4001-4100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0041__13e474a7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4001-4100 行

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
all 第 4001-4100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-BMW-X6-F16-SUV-01	4909	1989	1702
EU-CITROEN-C3-AIRCROSS-II-VAN-01	4154	1756	1597
EU-FORD-KUGA-II-VAN-FACELIFT-01	4531	1838	1689
EU-FORD-KUGA-II-VAN-PREFL-01	4524	1838	1702
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
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
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305
EU-MAN-TGE-I-VAN-L1H1-RWD-01	5986	2040	2355
EU-MAN-TGE-I-VAN-L1H2-RWD-01	5986	2040	2590
EU-MAN-TGE-I-VAN-L2H2-RWD-01	6836	2040	2590
EU-MAN-TGE-I-VAN-L2H3-RWD-01	6836	2040	2798
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355
EU-MAN-TGE-I-VAN-L3H2-AWD-01	5986	2040	2390
EU-MAN-TGE-I-VAN-L3H2-RWD-01	7391	2040	2590
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590
EU-MAN-TGE-I-VAN-L3H3-AWD-01	5986	2040	2625
EU-MAN-TGE-I-VAN-L3H3-RWD-01	7391	2040	2798
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590
EU-MAN-TGE-I-VAN-L4H3-AWD-01	6836	2040	2625
EU-MAN-TGE-I-VAN-L4H4-01	6836	2040	2798
EU-MAN-TGE-I-VAN-L5H3-01	7391	2040	2590
EU-MAN-TGE-I-VAN-L5H4-01	7391	2040	2798
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442
EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	4145	1700	2000
EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	4185	1690	1967
EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	4825	1931	1969
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	5115	1800	1780
EU-MITSUBISHI-L200-V-CLUB-CAB-PICKUP-01	5195	1785	1775
EU-MITSUBISHI-L200-V-DOUBLE-CAB-PICKUP-01	5205	1785	1775
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430
EU-PEUGEOT-308-CC-I-T7-CONVERTIBLE-01	4400	1817	1426
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	3615	1646	1541
EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	3595	1646	1554
EU-TOYOTA-SUPRA-V-A90-COUPE-01	4380	1865	1290
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Citroën	C3 aircross ii van	1.5 Bluehdi 120	Kasten/SUV	Frontantrieb	Diesel	88	120	May 2019	-	2024-03-01	136625
Peugeot	308 sw ii	1.5 Bluehdi 130	Kasten/Kombi	Frontantrieb	Diesel	96	131	Jun 2017	Jun 2021	2024-03-01	136628
Peugeot	308	1.5 Bluehdi 130	Kasten/Schrägheck	Frontantrieb	Diesel	96	131	Jun 2017	Jun 2021	2024-03-01	136629
Citroën	C4 cactus van	Puretech 82	Kasten/Schrägheck	Frontantrieb	Benzin	60	82	May 2019	-	2024-03-01	136631
Ford	Galaxy mk iii van	2.0 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	110	150	Mar 2019	Apr 2023	2026-03-01	136633
Ford	Galaxy mk iii van	2.0 Ecoblue AWD	Kasten/Großraumlimousine	Allrad	Diesel	140	190	Mar 2019	Apr 2023	2026-03-01	136634
Peugeot	208	1.5 Bluehdi 100	Kasten/Schrägheck	Frontantrieb	Diesel	75	102	May 2018	Dec 2019	2024-03-01	136635
Citroën	C4 cactus van	Puretech 110	Kasten/Schrägheck	Frontantrieb	Benzin	81	110	May 2019	-	2024-03-01	136636
Citroën	C4 cactus van	Puretech 130	Kasten/Schrägheck	Frontantrieb	Benzin	96	131	May 2019	-	2024-03-01	136637
Citroën	C4 cactus van	Bluehdi 100	Kasten/Schrägheck	Frontantrieb	Diesel	73	99	May 2019	-	2024-03-01	136639
Citroën	C4 cactus van	Bluehdi 100	Kasten/Schrägheck	Frontantrieb	Diesel	73	99	May 2019	-	2024-03-01	136640
Toyota	Yaris	1.0 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	53	72	Jun 2018	Jun 2020	2024-05-01	136641
Toyota	Yaris	1.5 Hybrid	Kasten/Schrägheck	Frontantrieb	Benzin/Elektro	74	101	Apr 2015	Jun 2020	2024-05-01	136643
BMW	X6	Xdrive 40 I	SUV	Allrad	Benzin	250	340	Aug 2019	Mar 2023	2024-03-01	136645
BMW	X6	Xdrive M50 I	SUV	Allrad	Benzin	390	530	Aug 2019	Mar 2023	2024-03-01	136646
BMW	X5	Xdrive M50 I	SUV	Allrad	Benzin	390	530	Aug 2019	Mar 2023	2024-03-01	136647
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	195	265	Aug 2019	Jul 2020	2024-03-01	136648
BMW	X6	Xdrive M 50 D	SUV	Allrad	Diesel	294	400	Aug 2019	Mar 2023	2024-03-01	136649
Nissan	X-Trail iii	1.7 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	96	131	Apr 2019	-	2024-03-01	136651
Nissan	X-Trail iii	1.7 DCI	SUV	Frontantrieb	Diesel	120	163	Apr 2019	-	2024-03-01	136652
Nissan	X-Trail iii	1.7 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	120	163	Apr 2019	-	2024-03-01	136653
Porsche	Cayenne	3.0 AWD	SUV	Allrad	Benzin	250	340	Jan 2019	-	2024-03-01	136654
Porsche	Cayenne	2.9 S AWD	SUV	Allrad	Benzin	324	440	Jan 2019	-	2024-03-01	136655
Porsche	Cayenne	4.0 Turbo AWD	SUV	Allrad	Benzin	404	550	Jan 2019	-	2024-03-01	136656
Toyota	Supra	2	Coupe	Heckantrieb	Benzin	190	258	Jun 2019	-	2024-03-01	136657
Toyota	Supra	2	Coupe	Heckantrieb	Benzin	145	197	Jun 2019	-	2024-03-01	136658
Citroën	C4 spacetourer van	Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	May 2019	-	2024-03-01	136660
Citroën	C4 spacetourer van	Bluehdi 120	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	May 2019	-	2024-03-01	136661
Citroën	C4 spacetourer van	Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	May 2019	-	2024-03-01	136662
Citroën	Grand c4 spacetourer van	Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	May 2019	-	2024-03-01	136663
Citroën	Grand c4 spacetourer van	Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	May 2019	-	2024-03-01	136664
Citroën	Grand c4 spacetourer van	Bluehdi 160	Kasten/Großraumlimousine	Frontantrieb	Diesel	120	163	May 2019	-	2024-03-01	136665
Hyundai	Tucson	1.6 Crdi Allrad	SUV	Allrad	Diesel	85	116	Aug 2018	Sep 2020	2024-03-01	136666
Mercedes-benz	A-Klasse	AMG A 45 4-matic+	Schrägheck	Allrad	Benzin	285	387	Jul 2019	-	2024-03-01	136670
Mercedes-benz	A-Klasse	AMG A 45 S 4-matic+	Schrägheck	Allrad	Benzin	310	421	Jul 2019	-	2024-03-01	136671
Mercedes-benz	Cla	AMG CLA 45 4-matic+	Coupe	Allrad	Benzin	285	387	Jul 2019	-	2024-03-01	136675
Mercedes-benz	Cla	AMG CLA 45 S 4-matic+	Coupe	Allrad	Benzin	310	421	Jul 2019	-	2024-03-01	136676
KIA	Rio iv hatchback van	1.0 T-gdi 100	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Jan 2017	-	2024-03-01	136687
KIA	Rio iv hatchback van	1.0 T-gdi 120	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Jan 2017	-	2024-03-01	136688
KIA	Ceed	T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Mar 2018	-	2024-03-01	136690
KIA	Ceed	1.4 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	103	140	Mar 2018	Dec 2020	2024-08-01	136694
KIA	Ceed	T-gdi GT	Kasten/Schrägheck	Frontantrieb	Benzin	150	204	Oct 2018	-	2024-03-01	136695
KIA	Ceed	Crdi 115	Kasten/Schrägheck	Frontantrieb	Diesel	85	116	Mar 2018	-	2024-03-01	136696
KIA	Ceed	Crdi 136	Kasten/Schrägheck	Frontantrieb	Diesel	100	136	Mar 2018	-	2024-03-01	136697
Mitsubishi	L200	2.2 Di-d 4WD	Pick-up	Allrad	Diesel	110	150	Jul 2019	-	2024-03-01	136698
Peugeot	208 ii	1.2 Puretech 75	Schrägheck	Frontantrieb	Benzin	55	75	Jun 2019	-	2024-03-01	136701
KIA	Ceed	T-gdi	Kasten/Kombi	Frontantrieb	Benzin	88	120	May 2018	-	2024-03-01	136703
KIA	Ceed	1.4 T-gdi	Kasten/Kombi	Frontantrieb	Benzin	103	140	Apr 2018	Dec 2020	2024-08-01	136704
KIA	Ceed	Crdi 115	Kasten/Kombi	Frontantrieb	Diesel	85	116	May 2018	-	2024-03-01	136705
KIA	Ceed	Crdi 136	Kasten/Kombi	Frontantrieb	Diesel	100	136	May 2018	-	2024-03-01	136706
KIA	Niro van	GDI Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	104	141	Sep 2016	-	2024-03-01	136708
KIA	Stonic	1.0 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Aug 2018	-	2024-03-01	136709
KIA	Stonic	1.0 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Jul 2017	-	2024-03-01	136710
KIA	Stonic	1.6 Crdi	Kasten/Schrägheck	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	136711
Peugeot	Partner	1.2 THP	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Feb 2016	-	2024-03-01	136712
KIA	Stinger	2.0 T-gdi	Kasten/Schrägheck	Heckantrieb	Benzin	180	245	Jul 2018	Dec 2023	2026-04-01	136713
KIA	Stinger	3.3 T-gdi	Kasten/Schrägheck	Heckantrieb	Benzin	269	366	Jul 2018	Dec 2023	2026-04-01	136714
KIA	Stinger	2.2 Crdi VGT	Kasten/Schrägheck	Heckantrieb	Diesel	147	200	Jul 2018	Dec 2023	2026-04-01	136715
KIA	Stinger	2.2 Crdi VGT 4WD	Kasten/Schrägheck	Allrad	Diesel	147	200	Jun 2017	Dec 2023	2026-04-01	136716
Hyundai	I20 ii hatchback van	1.0 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Jan 2016	Sep 2021	2025-06-01	136718
Hyundai	I20 ii hatchback van	1.2 MPI	Kasten/Schrägheck	Frontantrieb	Benzin	62	84	May 2015	Sep 2021	2025-06-01	136719
Hyundai	I20 ii hatchback van	1.2 MPI	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	May 2015	Sep 2021	2025-06-01	136720
Ford	Kuga ii van	1.5 Tdci	Kasten/SUV	Frontantrieb	Diesel	88	120	Jan 2019	Dec 2019	2024-05-01	136721
Volvo	Xc40	T5 Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	193	262	Jun 2019	-	2024-03-01	136722
Hyundai	I30	1.0 T-gdi	Kasten/Kombi	Frontantrieb	Benzin	88	120	Mar 2017	-	2024-03-01	136723
Hyundai	I30	1.4 T-gdi	Kasten/Kombi	Frontantrieb	Benzin	103	140	Mar 2017	Dec 2020	2025-02-03	136724
Hyundai	I30	1.6 Crdi VGT	Kasten/Kombi	Frontantrieb	Diesel	100	136	Mar 2017	-	2024-03-01	136726
Mini	Mini	Cooper SE / Electric	Schrägheck	Frontantrieb	Elektro	135	184	Nov 2019	-	2024-03-01	136727
Ford	Transit connect v408	1.5 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	101	May 2018	-	2024-03-01	136728
Renault	Twingo	0.9 TCE 95	Schrägheck	Heckantrieb	Benzin	68	92	Mar 2019	Jan 2021	2026-05-01	136729
Mazda	3	Skyactiv-x M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	132	179	Jun 2019	-	2024-03-01	136738
Mazda	3	Skyactiv-x M Hybrid AWD	Schrägheck	Allrad	Benzin/Elektro	132	179	Jun 2019	-	2024-03-01	136739
Mazda	3	2.0 Skyactiv-x M Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	132	179	Jun 2019	-	2024-03-01	136740
Volvo	Xc60 ii	T5 Polestar AWD	SUV	Allrad	Benzin	186	253	May 2019	Dec 2020	2025-06-01	136754
Volvo	V60 ii	T5 Polestar	Kombi	Frontantrieb	Benzin	186	253	Jul 2019	Dec 2021	2024-05-01	136756
Volvo	V60 ii	T5 Polestar AWD	Kombi	Allrad	Benzin	186	253	Jul 2019	-	2024-03-01	136757
Volvo	V60 ii	T4 Polestar	Kombi	Frontantrieb	Benzin	155	210	Jul 2019	Dec 2021	2024-05-01	136758
Volvo	Xc60 ii	T5 Polestar	SUV	Frontantrieb	Benzin	186	253	May 2019	Dec 2020	2024-05-01	136759
Volvo	S60 iii	T5 Polestar	Stufenheck	Frontantrieb	Benzin	186	253	Jul 2019	Dec 2021	2024-05-01	136760
Volvo	Xc60 ii	T6 Polestar AWD	SUV	Allrad	Benzin	240	326	Dec 2018	Aug 2019	2025-06-01	136761
Volvo	Xc60 ii	T4 Polestar	SUV	Frontantrieb	Benzin	155	210	Jul 2019	Dec 2021	2024-05-01	136762
Volvo	S60 iii	T4 Polestar	Stufenheck	Frontantrieb	Benzin	155	210	Jul 2019	Dec 2021	2024-05-01	136763
Volvo	Xc90 ii	T6 Polestar AWD	SUV	Allrad	Benzin	240	326	Oct 2017	Dec 2021	2024-05-01	136764
Volvo	Xc90 ii	T5 Polestar AWD	SUV	Allrad	Benzin	186	253	Jul 2019	Dec 2020	2024-05-01	136765
Renault	Kadjar	1.7 Blue DCI 150	SUV	Frontantrieb	Diesel	110	150	Aug 2018	-	2024-03-01	136766
Mercedes-benz	C-Klasse	C 160	Stufenheck	Heckantrieb	Benzin	95	129	Jun 2019	May 2021	2024-03-01	136778
Mercedes-benz	C-Klasse	C 180	Stufenheck	Heckantrieb	Benzin	115	156	Jun 2019	May 2021	2024-03-01	136779
Volvo	Xc90 ii	T8 Twin Engine AWD	SUV	Allrad	Benzin/Elektro	287	390	Nov 2018	Dec 2022	2025-06-01	136781
Mercedes-benz	C-Klasse	C 160	Kombi	Heckantrieb	Benzin	95	129	Jun 2019	Nov 2019	2024-03-01	136784
Mercedes-benz	C-Klasse	C 180	Kombi	Heckantrieb	Benzin	115	156	Jun 2019	Feb 2021	2024-03-01	136785
Mercedes-benz	C-Klasse	C 180	Coupe	Heckantrieb	Benzin	115	156	Jun 2019	Apr 2023	2024-03-01	136787
Mercedes-benz	C-Klasse	C 180	Cabriolet	Heckantrieb	Benzin	115	156	Jun 2019	Apr 2023	2024-03-01	136789
Mercedes-benz	G-Klasse	G 400 D 4-matic	Geländewagen geschlossen	Allrad	Diesel	243	330	Jul 2019	-	2024-03-01	136790
Nissan	Silvia	2	Coupe	Heckantrieb	Benzin	103	140	Jan 1991	Sep 1993	2024-03-01	136812
Mclaren	720s	4	Cabriolet	Heckantrieb	Benzin	530	720	Feb 2019	-	2024-03-01	136813
Volvo	Xc40	T2	SUV	Frontantrieb	Benzin	95	129	Jun 2019	-	2024-03-01	136833
Mercedes-benz	Cla	AMG CLA 45 4-matic+	Kombi	Allrad	Benzin	285	387	Jul 2019	-	2024-03-01	136839
Mercedes-benz	Cla	AMG CLA 45 S 4-matic+	Kombi	Allrad	Benzin	310	421	Jul 2019	-	2024-03-01	136840
MAN	Tge	2.0 TDI RWD	Bus	Heckantrieb	Diesel	90	122	Jan 2019	Dec 2021	2025-11-01	136843
MAN	Tge	2.0 TDI RWD	Bus	Heckantrieb	Diesel	130	177	Feb 2017	Jun 2024	2024-05-01	136867


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 100 个 Ktype 的首轮物理车身聚类：96 行转为 `READY`，仅余 4 行因驾驶室、轴距或车顶分支不明确而保持 `PENDING`。
* 本轮复用跨批次既有尺寸组 33 个，首次闭合并创建尺寸组 14 个。Ford Galaxy 官方资料明确区分含镜与不含镜宽度；BMW X6、Kia Rio/Niro、MINI Cooper SE、Nissan Silvia 等新组也已由官方资料或直接规格页闭合。
* 尚未闭合的 Ktype：`136698`、`136728`、`136843`、`136867`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：96
* PENDING 映射：4
* 当前已引用尺寸组：47
* 其中复用既有尺寸组：33
* 本轮首次创建尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136625	136625	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136628	136628	Wagon	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136629	136629	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136631	136631	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136633	136633	MPV	Galaxy III facelift	CD390	5	EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	HIGH	前驱与四驱版本共用同一五门 MPV 外廓。	READY
136634	136634	MPV	Galaxy III facelift	CD390	5	EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	HIGH	前驱与四驱版本共用同一五门 MPV 外廓。	READY
136635	136635	Hatchback	208 I facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH	商用化版本对应五门掀背车外廓。	READY
136636	136636	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136637	136637	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136639	136639	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136640	136640	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136641	136641	Hatchback	Yaris III facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH	三门 Van 物理外廓。	READY
136643	136643	Hatchback	Yaris III facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH	三门 Van 物理外廓。	READY
136645	136645	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136646	136646	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136647	136647	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
136648	136648	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136649	136649	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136651	136651	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136652	136652	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136653	136653	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136654	136654	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136655	136655	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136656	136656	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136657	136657	Coupe	Supra V	A90	2	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
136658	136658	Coupe	Supra V	A90	2	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
136660	136660	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136661	136661	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136662	136662	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136663	136663	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136664	136664	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136665	136665	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136666	136666	SUV	Tucson III facelift	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136670	136670	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	HIGH	A 45 与 A 45 S 共用同一 AMG 五门外廓。	READY
136671	136671	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	HIGH	A 45 与 A 45 S 共用同一 AMG 五门外廓。	READY
136675	136675	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	HIGH	四门 Coupe；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136676	136676	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	HIGH	四门 Coupe；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136687	136687	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136688	136688	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136690	136690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136694	136694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136695	136695	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-GT-01	HIGH	GT 外部套件对应独立外廓组。	READY
136696	136696	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136697	136697	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136698	136698	Pickup	L200 V facelift				LOW	候选为 Club Cab 或 Double Cab；驾驶室物理分支尚未确认。	PENDING: 未确认 Club Cab / Double Cab 物理分支
136701	136701	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136703	136703	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136704	136704	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136705	136705	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136706	136706	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136708	136708	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-SUV-PREFL-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136709	136709	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136710	136710	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136711	136711	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136712	136712	MPV	Partner II facelift	B9	5	EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	HIGH		READY
136713	136713	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136714	136714	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136715	136715	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136716	136716	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136718	136718	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136719	136719	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136720	136720	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136721	136721	SUV	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136722	136722	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136723	136723	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136724	136724	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136726	136726	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136727	136727	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	HIGH		READY
136728	136728	MPV	Transit Connect II facelift	V408	5		LOW	候选为短轴或长轴乘用版；车身长度分支尚未确认。	PENDING: 未确认短轴 / 长轴物理分支
136729	136729	Hatchback	Twingo III facelift	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136738	136738	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136739	136739	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136740	136740	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH		READY
136754	136754	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136756	136756	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136757	136757	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136758	136758	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136759	136759	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136760	136760	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136761	136761	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136762	136762	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136763	136763	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136764	136764	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136765	136765	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136766	136766	SUV	Kadjar I facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
136778	136778	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136779	136779	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136781	136781	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136784	136784	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136785	136785	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136787	136787	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
136789	136789	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
136790	136790	SUV	G-Class W463 II	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	HIGH		READY
136812	136812	Coupe	Silvia S13	S13	2	EU-NISSAN-SILVIA-S13-COUPE-01	HIGH		READY
136813	136813	Convertible	720S Spider		2	EU-MCLAREN-720S-I-SPIDER-CONVERTIBLE-01	MEDIUM	Spider 可折叠硬顶双门外廓。	READY
136833	136833	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136839	136839	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	HIGH	Shooting Brake；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136840	136840	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	HIGH	Shooting Brake；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136843	136843	MPV	TGE I				LOW	Bus 存在多个车长与车顶高度组合，输入未给出 L/H 分支。	PENDING: 未确认车长与车顶高度分支
136867	136867	MPV	TGE I				LOW	Bus 存在多个车长与车顶高度组合，输入未给出 L/H 分支。	PENDING: 未确认车长与车顶高度分支
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	4170	1714	1480	Auto-Data; Citroën/Stellantis official model information	https://www.auto-data.net/en/citroen-c4-cactus-phase-ii-2018-1.2-puretech-130hp-31707;https://www.media.stellantis.com/uk-en/citroen/press/new-citroen-c4-cactus-the-ultra-comfortable-hatchback-with-a-unique-personality
EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	4848	1916	1747	Ford Galaxy official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Galaxy.pdf
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW Group PressClub official model information	https://www.press.bmwgroup.com/ireland/article/detail/T0300671EN/the-all-new-bmw-x6?language=en
EU-CITROEN-C4-SPACETOURER-I-MPV-01	4438	1826	1638	Auto-Data	https://www.auto-data.net/en/citroen-c4-spacetourer-phase-i-2018-generation-6609
EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	4602	1826	1638	Auto-Data	https://www.auto-data.net/en/citroen-grand-c4-spacetourer-phase-i-2018-generation-6610
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2908145/mercedes-amg_a_45_s_4matic.html
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2908160/mercedes-amg_cla_45_4matic_coupe.html
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450	Kia Europe official technical specification	https://press.kia.com/content/dam/kiapress/EU/download-files/New-Rio/Kia-Rio-Technical-Specification-3-Feb-2017.doc
EU-KIA-NIRO-I-DE-SUV-PREFL-01	4355	1800	1535	Kia Europe official press information	https://press.kia.com/ie/en/home/media-resouces/press-releases/2016/16_03_01_kia-niro-european-debut---geneva-2016.html
EU-HYUNDAI-I20-II-GB-HATCHBACK-01	4035	1734	1474	Auto-Data	https://www.auto-data.net/en/hyundai-i20-model-1503
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432	BMW Group PressClub MINI Cooper SE official specification	https://www.press.bmwgroup.com/global/article/attachment/T0325441EN/471414
EU-NISSAN-SILVIA-S13-COUPE-01	4470	1690	1290	Nissan Heritage Collection official vehicle data	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/silvia_qs.html
EU-MCLAREN-720S-I-SPIDER-CONVERTIBLE-01	4543	1930	1196	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2795555/mclaren_720s_spider.html
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2908205/mercedes-amg_cla_45_s_4matic_shooting_brake.html
```

## 下一步优先处理

1. 核定 `136698` 的 L200 是 Club Cab 还是 Double Cab，并仅创建实际覆盖的驾驶室分支。
2. 核定 `136728` Transit Connect V408 是短轴还是长轴乘用版。
3. 将 `136843`、`136867` 作为同一 MAN TGE Bus 聚类一次性核定，确认其 L3/L4/L5 车长及车顶高度组合。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 剩余 4 个 PENDING Ktype 已全部闭合。
* `136698` 按 L200 Club Cab、Double Cab 标准后保险杠、Double Cab 踏步后保险杠拆分为 3 个物理外廓。
* `136728` 按 Transit Connect SWB、LWB 拆分为 2 个物理外廓。
* `136843`、`136867` 各按 TGE Bus 的 L3H2、L3H3、L4H3 拆分，并复用既有尺寸组。
* 已完成固定表头、唯一主键、映射引用闭合、尺寸与来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：107
* PENDING 映射：0
* DIMENSION_GROUP：55
* 唯一 `id`：107 / 107
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136625	136625	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136628	136628	Wagon	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136629	136629	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136631	136631	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136633	136633	MPV	Galaxy III facelift	CD390	5	EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	HIGH	前驱与四驱版本共用同一五门 MPV 外廓。	READY
136634	136634	MPV	Galaxy III facelift	CD390	5	EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	HIGH	前驱与四驱版本共用同一五门 MPV 外廓。	READY
136635	136635	Hatchback	208 I facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH	商用化版本对应五门掀背车外廓。	READY
136636	136636	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136637	136637	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136639	136639	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136640	136640	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136641	136641	Hatchback	Yaris III facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH	三门 Van 物理外廓。	READY
136643	136643	Hatchback	Yaris III facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH	三门 Van 物理外廓。	READY
136645	136645	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136646	136646	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136647	136647	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
136648	136648	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136649	136649	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH		READY
136651	136651	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136652	136652	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136653	136653	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136654	136654	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136655	136655	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136656	136656	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
136657	136657	Coupe	Supra V	A90	2	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
136658	136658	Coupe	Supra V	A90	2	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
136660	136660	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136661	136661	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136662	136662	MPV	C4 SpaceTourer I		5	EU-CITROEN-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变短轴五门 MPV 外廓。	READY
136663	136663	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136664	136664	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136665	136665	MPV	Grand C4 SpaceTourer I		5	EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	HIGH	商用化版本不改变长车身五门 MPV 外廓。	READY
136666	136666	SUV	Tucson III facelift	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136670	136670	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	HIGH	A 45 与 A 45 S 共用同一 AMG 五门外廓。	READY
136671	136671	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	HIGH	A 45 与 A 45 S 共用同一 AMG 五门外廓。	READY
136675	136675	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	HIGH	四门 Coupe；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136676	136676	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	HIGH	四门 Coupe；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136687	136687	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136688	136688	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136690	136690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136694	136694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136695	136695	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-GT-01	HIGH	GT 外部套件对应独立外廓组。	READY
136696	136696	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136697	136697	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	商用化版本不改变标准五门掀背车外廓。	READY
136698_clubcab	136698	Pickup	L200 V facelift		4	EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	MEDIUM	Club Cab 四门物理外廓。	READY
136698_doublecab_standard	136698	Pickup	L200 V facelift		4	EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	MEDIUM	Double Cab 标准后保险杠物理外廓。	READY
136698_doublecab_stepbumper	136698	Pickup	L200 V facelift		4	EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	MEDIUM	Double Cab 带后踏步保险杠物理外廓。	READY
136701	136701	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136703	136703	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136704	136704	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136705	136705	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136706	136706	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136708	136708	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-SUV-PREFL-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136709	136709	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136710	136710	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136711	136711	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入为 Kasten/Schrägheck，物理外廓按五门跨界 SUV 归类。	READY
136712	136712	MPV	Partner II facelift	B9	5	EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	HIGH		READY
136713	136713	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136714	136714	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136715	136715	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136716	136716	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	五门 liftback 物理外廓。	READY
136718	136718	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136719	136719	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136720	136720	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-01	HIGH	商用化版本不改变五门掀背车外廓。	READY
136721	136721	SUV	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH	商用化版本不改变五门 SUV 外廓。	READY
136722	136722	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136723	136723	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136724	136724	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136726	136726	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	商用化版本不改变五门旅行车外廓。	READY
136727	136727	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	HIGH		READY
136728_swb	136728	MPV	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	L1/SWB 物理外廓。	READY
136728_lwb	136728	MPV	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	L2/LWB 物理外廓。	READY
136729	136729	Hatchback	Twingo III facelift	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136738	136738	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136739	136739	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136740	136740	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH		READY
136754	136754	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136756	136756	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136757	136757	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136758	136758	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136759	136759	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136760	136760	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136761	136761	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136762	136762	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136763	136763	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136764	136764	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136765	136765	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136766	136766	SUV	Kadjar I facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
136778	136778	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136779	136779	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136781	136781	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136784	136784	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136785	136785	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136787	136787	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
136789	136789	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
136790	136790	SUV	G-Class W463 II	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	HIGH		READY
136812	136812	Coupe	Silvia S13	S13	2	EU-NISSAN-SILVIA-S13-COUPE-01	HIGH		READY
136813	136813	Convertible	720S Spider		2	EU-MCLAREN-720S-I-SPIDER-CONVERTIBLE-01	MEDIUM	Spider 可折叠硬顶双门外廓。	READY
136833	136833	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136839	136839	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	HIGH	Shooting Brake；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136840	136840	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	HIGH	Shooting Brake；CLA 45 与 CLA 45 S 共用同一外廓。	READY
136843_l3h2	136843	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	标准车长普通顶物理外廓。	READY
136843_l3h3	136843	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	标准车长高顶物理外廓。	READY
136843_l4h3	136843	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	长车身高顶物理外廓。	READY
136867_l3h2	136867	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	标准车长普通顶物理外廓。	READY
136867_l3h3	136867	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	标准车长高顶物理外廓。	READY
136867_l4h3	136867	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	长车身高顶物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4001-4100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C3-AIRCROSS-II-VAN-01	4154	1756	1597	Auto-Data	https://www.auto-data.net/en/citroen-c3-aircross-i-phase-i-2017-1.2-puretech-110hp-automatic-30775
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-sw-ii-phase-ii-2017-1.2-puretech-130hp-automatic-36344
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-ii-phase-ii-2017-1.2-puretech-130hp-automatic-36339
EU-CITROEN-C4-CACTUS-I-HATCHBACK-FACELIFT-01	4170	1714	1480	Auto-Data; Citroën/Stellantis official model information	https://www.auto-data.net/en/citroen-c4-cactus-phase-ii-2018-1.2-puretech-130hp-31707;https://www.media.stellantis.com/uk-en/citroen/press/new-citroen-c4-cactus-the-ultra-comfortable-hatchback-with-a-unique-personality
EU-FORD-GALAXY-III-CD390-MPV-FACELIFT-01	4848	1916	1747	Ford Galaxy official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Galaxy.pdf
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460	Auto-Data	https://www.auto-data.net/en/peugeot-208-i-phase-ii-2015-1.5-bluehdi-102hp-36638
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510	Auto-Data	https://www.auto-data.net/en/toyota-yaris-model-490
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW Group PressClub official model information	https://www.press.bmwgroup.com/ireland/article/detail/T0300671EN/the-all-new-bmw-x6?language=en
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	Auto-Data	https://www.auto-data.net/en/bmw-x5-g05-40i-340hp-xdrive-steptronic-33264
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Nissan X-Trail T32 official specification	https://history.nissan.co.jp/ARCHIVES/PDF/X-TRAIL/T32/20190111/x-trail_specsheet.pdf
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-3.0-v6-340hp-tiptronic-s-31653
EU-TOYOTA-SUPRA-V-A90-COUPE-01	4380	1865	1290	Toyota GR Supra official brochure	https://www.toyota.com.cy/content/dam/toyota/nmsc/cyprus/cross-model/toyota-brochures/tcy-brochures/Supra.pdf
EU-CITROEN-C4-SPACETOURER-I-MPV-01	4438	1826	1638	Auto-Data	https://www.auto-data.net/en/citroen-c4-spacetourer-phase-i-2018-generation-6609
EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	4602	1826	1638	Auto-Data	https://www.auto-data.net/en/citroen-grand-c4-spacetourer-phase-i-2018-generation-6610
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Auto-Data	https://www.auto-data.net/en/hyundai-tucson-iii-facelift-2018-1.6-t-gdi-177hp-awd-35032
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2908145/mercedes-amg_a_45_s_4matic.html
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2908160/mercedes-amg_cla_45_4matic_coupe.html
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450	Kia Europe official technical specification	https://press.kia.com/content/dam/kiapress/EU/download-files/New-Rio/Kia-Rio-Technical-Specification-3-Feb-2017.doc
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-1.4-t-gdi-140hp-34224
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-gt-1.6-t-gdi-204hp-dct-44392
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	5215	1815	1780	Mitsubishi L200 20MY official UK brochure	https://nd-mediagallery2-public-production.s3.amazonaws.com/95f341bba36c69e83a339b8640a1ba33/20my_l200_series_6_brochure.pdf
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	5225	1815	1780	Mitsubishi L200 20MY official UK brochure	https://nd-mediagallery2-public-production.s3.amazonaws.com/95f341bba36c69e83a339b8640a1ba33/20my_l200_series_6_brochure.pdf
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	5305	1815	1780	Mitsubishi L200 20MY official UK brochure	https://nd-mediagallery2-public-production.s3.amazonaws.com/95f341bba36c69e83a339b8640a1ba33/20my_l200_series_6_brochure.pdf
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430	Auto-Data	https://www.auto-data.net/en/peugeot-208-ii-phase-i-2019-generation-7026
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-sportswagon-1.4-t-gdi-140hp-32822
EU-KIA-NIRO-I-DE-SUV-PREFL-01	4355	1800	1535	Kia Europe official press information	https://press.kia.com/ie/en/home/media-resouces/press-releases/2016/16_03_01_kia-niro-european-debut---geneva-2016.html
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Auto-Data	https://www.auto-data.net/en/kia-stonic-1.4i-100hp-31118
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801	Peugeot Partner Tepee official owner manual	https://www.carmanualsonline.info/peugeot-partner-tepee-2016-owner-s-manual/?srch=wheelbase
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400	Auto-Data	https://www.auto-data.net/en/kia-stinger-generation-5624
EU-HYUNDAI-I20-II-GB-HATCHBACK-01	4035	1734	1474	Auto-Data	https://www.auto-data.net/en/hyundai-i20-model-1503
EU-FORD-KUGA-II-VAN-FACELIFT-01	4531	1838	1689	Auto-Data	https://www.auto-data.net/en/ford-kuga-ii-facelift-2016-2.0-tdci-180hp-4x4-powershift-25791
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Auto-Data	https://www.auto-data.net/en/volvo-xc40-2.0-d3-150hp-32773
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-cw-generation-5497
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432	BMW Group PressClub MINI Cooper SE official specification	https://www.press.bmwgroup.com/global/article/attachment/T0325441EN/471414
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	4418	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	4818	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	3615	1646	1541	Auto-Data	https://www.auto-data.net/en/renault-twingo-iii-facelift-2019-0.9-tce-92hp-35667
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Auto-Data	https://www.auto-data.net/en/mazda-3-iv-hatchback-2.0-skyactiv-g-162hp-skyactiv-drive-38128
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440	Auto-Data	https://www.auto-data.net/en/mazda-3-iv-sedan-2.0-skyactiv-g-162hp-skyactiv-drive-38129
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data	https://www.auto-data.net/en/volvo-xc60-ii-generation-5397
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Support official dimensions	https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Auto-Data	https://www.auto-data.net/en/volvo-s60-iii-2.0-t5-250hp-automatic-35050
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Auto-Data	https://www.auto-data.net/en/volvo-xc90-ii-generation-4274
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613	Auto-Data	https://www.auto-data.net/en/renault-kadjar-facelift-2018-1.7-blue-dci-150hp-4wd-34197
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-160-129hp-52482
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-160-129hp-52484
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-180-1.6-156hp-44014
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-180-1.6-156hp-52493
EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	4825	1931	1969	Auto-Data	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2018-g-400d-330hp-4matic-9g-tronic-42383
EU-NISSAN-SILVIA-S13-COUPE-01	4470	1690	1290	Nissan Heritage Collection official vehicle data	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/silvia_qs.html
EU-MCLAREN-720S-I-SPIDER-CONVERTIBLE-01	4543	1930	1196	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2795555/mclaren_720s_spider.html
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2908205/mercedes-amg_cla_45_s_4matic_shooting_brake.html
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355	MAN TGE Combi Van official brochure	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/broschueren/tge/minibus/man-tge-minibus-en.pdf/_jcr_content/renditions/original./man-tge-minibus-en.pdf
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590	MAN TGE Combi Van official brochure	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/broschueren/tge/minibus/man-tge-minibus-en.pdf/_jcr_content/renditions/original./man-tge-minibus-en.pdf
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590	MAN TGE Combi Van official brochure	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/broschueren/tge/minibus/man-tge-minibus-en.pdf/_jcr_content/renditions/original./man-tge-minibus-en.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4001-4100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3663 行）
- 累计尺寸组：dimension_groups_final.tsv（1572 行）

