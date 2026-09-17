# 任务：all 第 12801-12900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0129__3f1888d1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 12801-12900 行

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
all 第 12801-12900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12801-12900_ktype_dimension_mapping_final.tsv
- all_12801-12900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453
EU-AUDI-A6-C5-4B5-WAGON-5D-01	4796	1810	1479
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-2D-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-2D-01	4488	1757	1369
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415
EU-BMW-3-E46-TOURING-5D-01	4478	1739	1409
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-CITROEN-C8-MPV-FACELIFT-01	4727	1854	1752
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1832
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-LOWROOF-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-LWB-LOWROOF-01	4633	1722	1817
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	4253	1722	2086
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	4253	1722	1831
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	4253	1722	2073
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	4253	1722	1818
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	4740	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	4390	1832	2100
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	4577	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	4561	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	4227	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	4211	1789	1845
EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	4406	1832	1899
EU-FIAT-DOBLO-II-263-MPV-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-FACELIFT-01	4406	1832	2125
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-II-CARGO-MAXI-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-II-CARGO-MAXI-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-II-CARGO-SWB-FACELIFT-01	4406	1832	1845
EU-FIAT-DOBLO-II-CARGO-SWB-PREFL-01	4390	1832	1845
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	5489	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	4759	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4759	1965	2100
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	4908	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	5358	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X250-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-X250-VAN-L1H2-01	4963	2050	2524
EU-FIAT-DUCATO-X250-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-X250-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-X250-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-X250-VAN-L4H2-01	6363	2050	2524
EU-FIAT-DUCATO-X250-VAN-L4H3-01	6363	2050	2764
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490
EU-FORD-SCORPIO-I-GGE-WAGON-5D-4X4-01	4744	1760	1490
EU-FORD-SCORPIO-I-HATCHBACK-01	4669	1760	1440
EU-FORD-SCORPIO-I-HATCHBACK-5D-01	4669	1760	1490
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1402
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442
EU-FORD-SCORPIO-I-SEDAN-01	4744	1766	1450
EU-FORD-SCORPIO-I-SEDAN-02	4744	1766	1440
EU-FORD-SCORPIO-I-SEDAN-4D-01	4744	1766	1450
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430
EU-MAZDA-626-III-GV-WAGON-5D-02	4660	1755	1440
EU-MAZDA-626-III-GV-WAGON-5D-4WD-01	4610	1690	1450
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	4680	1750	1400
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MAZDA-626-V-GF-HATCHBACK-5D-01	4575	1710	1430
EU-MAZDA-626-V-GF-HATCHBACK-5D-02	4574	1710	1430
EU-MAZDA-626-V-GF-HATCHBACK-PREFL-01	4575	1710	1430
EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	4590	1710	1430
EU-MAZDA-626-V-GF-SEDAN-PREFL-01	4575	1710	1430
EU-MAZDA-626-V-GW-WAGON-5D-01	4660	1710	1515
EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	4755	1795	1440
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420
EU-PEUGEOT-406-COUPE-2D-01	4615	1780	1352
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410
EU-PEUGEOT-406-WAGON-FACELIFT-01	4736	1760	1460
EU-PEUGEOT-807-I-E-MPV-01	4727	1854	1752
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465
EU-PEUGEOT-BOXER-I-230-PICKUP-14-LWB-01	5620	2000	2096
EU-PEUGEOT-BOXER-I-230-PICKUP-14-MWB-01	5120	2000	2093
EU-PEUGEOT-BOXER-I-230-PICKUP-14-SWB-01	4770	2000	2093
EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-LWB-01	5620	2000	2130
EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-MWB-01	5120	2000	2124
EU-PORSCHE-CAYENNE-II-SUV-DIESEL-01	4846	1939	1705
EU-PORSCHE-CAYENNE-II-SUV-TURBO-01	4846	1939	1702
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492
EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	4315	1768	1459
EU-VW-BORA-1J6-WAGON-5D-01	4409	1735	1485
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Saab	9-5	2.2 TID	Stufenheck	Frontantrieb	Diesel	88	120	Mar 2002	Dec 2009	2024-03-01	16636
Saab	9-5	2.2 TID	Kombi	Frontantrieb	Diesel	88	120	Mar 2002	Dec 2009	2024-03-01	16637
Opel	Corsa b	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	74	100	Aug 1997	Sep 2000	2024-03-01	16641
Peugeot	Boxer	2	Bus	Frontantrieb	Benzin	81	110	Dec 2001	Jun 2006	2024-03-01	16642
Peugeot	Boxer	2.0 HDI	Bus	Frontantrieb	Diesel	62	84	Dec 2001	Jun 2006	2024-03-01	16643
Peugeot	Boxer	2.2 HDI	Bus	Frontantrieb	Diesel	74	101	Dec 2001	Jun 2006	2024-03-01	16644
Peugeot	Boxer	2.8 HDI	Bus	Frontantrieb	Diesel	94	128	Dec 2001	Jun 2006	2024-03-01	16645
Suzuki	Liana	1.6	Stufenheck	Frontantrieb	Benzin	76	103	Mar 2002	-	2024-03-01	16646
Suzuki	Liana	1.6 4WD	Stufenheck	Allrad	Benzin	76	103	Mar 2002	-	2024-03-01	16647
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	81	110	Dec 2001	Jul 2006	2024-03-01	16648
Fiat	Ducato	2.0 JTD	Kasten	Frontantrieb	Diesel	62	84	Dec 2001	Jul 2006	2024-03-01	16649
Fiat	Ducato	2.3 JTD	Kasten	Frontantrieb	Diesel	81	110	Dec 2001	Jul 2006	2024-03-01	16650
Fiat	Ducato	2.8 JTD	Kasten	Frontantrieb	Diesel	94	128	Dec 2001	Dec 2011	2024-03-01	16651
Fiat	Ducato	2	Bus	Frontantrieb	Benzin	81	110	Dec 2001	Jul 2006	2024-03-01	16652
Fiat	Ducato	2.0 JTD	Bus	Frontantrieb	Diesel	62	84	Dec 2001	Jul 2006	2024-03-01	16653
Fiat	Ducato	2.3 JTD	Bus	Frontantrieb	Diesel	81	110	Dec 2001	Jul 2006	2024-03-01	16654
Fiat	Ducato	2.8 JTD	Bus	Frontantrieb	Diesel	94	128	Dec 2001	-	2024-03-01	16655
Ferrari	5__ maranello	575 M	Coupe	Heckantrieb	Benzin	380	517	Apr 2002	Dec 2006	2024-03-01	16656
Mercedes-benz	Clk	CLK 240	Coupe	Heckantrieb	Benzin	125	170	Jun 2002	May 2009	2024-03-01	16657
Mercedes-benz	Clk	CLK 200 Kompressor	Coupe	Heckantrieb	Benzin	120	163	Sep 2002	May 2009	2024-03-01	16658
Mercedes-benz	Clk	CLK 200 CGI	Coupe	Heckantrieb	Benzin	125	170	Jul 2003	May 2009	2024-03-01	16659
Fiat	Doblo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	76	103	Oct 2001	-	2024-03-01	16660
Fiat	Doblo	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	100	Oct 2001	-	2024-03-01	16661
Citroën	Jumper ii	2	Bus	Frontantrieb	Benzin	81	110	Apr 2002	Jun 2006	2025-12-01	16662
Citroën	Jumper ii	2.0 HDI	Bus	Frontantrieb	Diesel	62	84	Apr 2002	Jun 2006	2025-12-01	16663
Citroën	Jumper ii	2.2 HDI	Bus	Frontantrieb	Diesel	74	101	Apr 2002	Jun 2006	2025-12-01	16664
Citroën	Jumper ii	2.8 HDI	Bus	Frontantrieb	Diesel	94	128	Apr 2002	Jun 2006	2025-12-01	16665
Peugeot	807	2	Großraumlimousine	Frontantrieb	Benzin	100	136	Jun 2002	-	2024-03-01	16666
Peugeot	807	2.2	Großraumlimousine	Frontantrieb	Benzin	116	158	Jun 2002	-	2024-03-01	16667
Peugeot	807	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	150	204	Jun 2002	-	2024-03-01	16668
Peugeot	807	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	79	107	Jun 2002	May 2006	2024-03-01	16669
Peugeot	807	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	94	128	Jun 2002	-	2024-03-01	16670
Chevrolet	Alero	2.2	Stufenheck	Frontantrieb	Benzin	104	141	Dec 2001	Sep 2004	2024-03-01	16671
VW	Polo	1.7 SDI	Schrägheck	Frontantrieb	Diesel	42	57	Apr 1997	Oct 1999	2024-03-01	16672
Fiat	Punto	1.9 JTD	Schrägheck	Frontantrieb	Diesel	63	86	Oct 2001	Mar 2012	2024-03-01	16673
Peugeot	206 sw	1.1	Kombi	Frontantrieb	Benzin	44	60	Jul 2002	Feb 2007	2024-03-01	16674
Peugeot	206 sw	1.4	Kombi	Frontantrieb	Benzin	55	75	Jul 2002	Feb 2007	2024-03-01	16675
Peugeot	206 sw	1.6 16V	Kombi	Frontantrieb	Benzin	80	109	Jul 2002	-	2024-03-01	16676
Peugeot	206 sw	2.0 16V	Kombi	Frontantrieb	Benzin	100	136	Jul 2002	Feb 2007	2024-03-01	16677
Peugeot	206 sw	1.4 HDI	Kombi	Frontantrieb	Diesel	50	68	Jul 2002	Feb 2007	2024-03-01	16678
Audi	A2	1.6 FSI	Schrägheck	Frontantrieb	Benzin	81	110	May 2002	Aug 2005	2024-03-01	16679
Mazda	6	1.8	Schrägheck	Frontantrieb	Benzin	88	120	Aug 2002	Aug 2007	2024-03-01	16680
Mazda	6	2	Schrägheck	Frontantrieb	Benzin	104	141	Aug 2002	Aug 2007	2024-03-01	16681
Mazda	6	2.3	Schrägheck	Frontantrieb	Benzin	122	166	Aug 2002	Aug 2007	2024-03-01	16682
Mazda	6	2.0 DI	Schrägheck	Frontantrieb	Diesel	100	136	Aug 2002	Aug 2007	2024-03-01	16683
Mazda	6	1.8	Stufenheck	Frontantrieb	Benzin	88	120	Aug 2002	Aug 2007	2024-03-01	16684
Mazda	6	2	Stufenheck	Frontantrieb	Benzin	104	141	Jun 2002	Aug 2007	2024-03-01	16685
Mazda	6	2.3	Stufenheck	Frontantrieb	Benzin	122	166	Jun 2002	Aug 2007	2024-03-01	16686
Mazda	6	2.0 DI	Stufenheck	Frontantrieb	Diesel	100	136	Jun 2002	Aug 2007	2024-03-01	16687
Mazda	6	1.8	Kombi	Frontantrieb	Benzin	88	120	Aug 2002	Aug 2007	2024-03-01	16688
Mazda	6	2	Kombi	Frontantrieb	Benzin	104	141	Aug 2002	Aug 2007	2024-03-01	16689
Mazda	6	2.3	Kombi	Frontantrieb	Benzin	122	166	Jan 2002	Feb 2008	2024-03-01	16690
Mazda	6	2.0 DI	Kombi	Frontantrieb	Diesel	100	136	Aug 2002	Feb 2005	2024-03-01	16691
Seat	Leon	1.8 T Cupra R	Schrägheck	Frontantrieb	Benzin	154	209	Feb 2002	Jun 2006	2024-03-01	16692
VW	Phaeton	3.2 V6	Stufenheck	Frontantrieb	Benzin	177	241	Apr 2002	May 2005	2024-03-01	16693
Peugeot	406	2.2	Coupe	Frontantrieb	Benzin	116	158	Mar 2002	Dec 2004	2024-03-01	16694
Porsche	Cayenne	S 4.5	SUV	Allrad	Benzin	250	340	Sep 2002	Sep 2007	2024-03-01	16695
Jaguar	S-Type ii	2.5 V6	Stufenheck	Heckantrieb	Benzin	147	200	Apr 2002	Oct 2007	2024-03-01	16696
Jaguar	S-Type ii	4.2 V8	Stufenheck	Heckantrieb	Benzin	219	298	Apr 2002	Oct 2007	2024-03-01	16697
Jaguar	S-Type ii	R 4,2 V8	Stufenheck	Heckantrieb	Benzin	291	396	Apr 2002	Oct 2007	2024-03-01	16698
Mercedes-benz	Clk	CLK 270 CDI	Coupe	Heckantrieb	Diesel	125	170	Oct 2002	May 2009	2024-03-01	16699
VW	Bora	1.8 T	Stufenheck	Frontantrieb	Benzin	132	180	Mar 2002	May 2005	2024-03-01	16700
Alpina	Roadster	4.8 V8	Cabriolet	Heckantrieb	Benzin	280	381	Jun 2002	Oct 2003	2024-03-01	16701
VW	Passat b5.5	1.8 T	Stufenheck	Frontantrieb	Benzin	125	170	Feb 2001	Nov 2005	2024-03-01	16703
Audi	A4 b5	2.4	Stufenheck	Frontantrieb	Benzin	120	163	Aug 1997	Nov 2000	2024-03-01	16705
Audi	A4 b5	2.4 Quattro	Stufenheck	Allrad	Benzin	120	163	Aug 1997	Nov 2000	2024-03-01	16706
Audi	A4 b5 avant	2.4	Kombi	Frontantrieb	Benzin	120	163	Aug 1997	Sep 2001	2024-03-01	16707
Audi	A4 b5 avant	2.4 Quattro	Kombi	Allrad	Benzin	120	163	Aug 1997	Sep 2001	2024-03-01	16708
Audi	A6 c5	2.4	Stufenheck	Frontantrieb	Benzin	120	163	Feb 1997	Jan 2005	2024-03-01	16709
Audi	A6 c5	2.4 Quattro	Stufenheck	Allrad	Benzin	120	163	Feb 1997	Jan 2005	2024-03-01	16710
Audi	A6 c5 avant	2.4	Kombi	Frontantrieb	Benzin	120	163	Dec 1997	Jan 2005	2024-03-01	16711
Audi	A6 c5 avant	2.4 Quattro	Kombi	Allrad	Benzin	120	163	Dec 1997	Jan 2005	2024-03-01	16712
Suzuki	Alto vi	1.1	Schrägheck	Frontantrieb	Benzin	46	63	Jun 2002	Dec 2008	2025-06-01	16713
Mercedes-benz	C-Klasse	C 180 Kompressor	Stufenheck	Heckantrieb	Benzin	105	143	May 2002	Feb 2007	2024-03-01	16714
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	120	163	May 2002	Feb 2007	2024-03-01	16715
Mercedes-benz	C-Klasse	C 180 Kompressor	Kombi	Heckantrieb	Benzin	105	143	May 2002	Aug 2007	2024-03-01	16716
Mercedes-benz	C-Klasse	C 200 Kompressor	Kombi	Heckantrieb	Benzin	120	163	May 2002	Aug 2007	2024-03-01	16717
Mercedes-benz	C-Klasse	C 180 Kompressor	Coupe	Heckantrieb	Benzin	105	143	May 2002	May 2008	2024-03-01	16718
Mercedes-benz	C-Klasse	C 200 Kompressor	Coupe	Heckantrieb	Benzin	120	163	May 2002	May 2008	2024-03-01	16719
Mercedes-benz	C-Klasse	C 230 Kompressor	Coupe	Heckantrieb	Benzin	141	192	May 2002	May 2008	2024-03-01	16720
Hyundai	Accent ii	1.5	Stufenheck	Frontantrieb	Benzin	66	90	Jan 2000	Nov 2005	2024-03-01	16721
Citroën	C8	2	Großraumlimousine	Frontantrieb	Benzin	100	136	Jul 2002	-	2024-03-01	16726
Citroën	C8	2.2	Großraumlimousine	Frontantrieb	Benzin	116	158	Jul 2002	-	2024-03-01	16727
Citroën	C8	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	150	204	Jul 2002	-	2024-03-01	16728
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	79	107	Jul 2002	-	2024-03-01	16729
Citroën	C8	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	94	128	Jul 2002	-	2024-03-01	16730
Alpina	B10	V8 S 4.8	Stufenheck	Heckantrieb	Benzin	276	375	Jan 2002	May 2004	2024-03-01	16731
VW	Polo	1.4 FSI	Schrägheck	Frontantrieb	Benzin	63	86	Feb 2002	Jul 2006	2024-03-01	16732
Audi	Allroad c5	4.2 V8 Quattro	Kombi	Allrad	Benzin	220	299	Jul 2002	Aug 2005	2024-03-01	16733
Opel	Astra g caravan	2.0 OPC	Kombi	Frontantrieb	Benzin	141	192	Sep 2002	Jul 2004	2024-03-01	16736
Ford	Scorpio i	2.5 D	Stufenheck	Heckantrieb	Diesel	51	69	Dec 1989	Dec 1994	2024-03-01	16737
Fiat	Ducato	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	62	84	Dec 2001	Jul 2006	2024-03-01	16738
Fiat	Ducato	2.3 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	81	110	Dec 2001	Jul 2006	2024-03-01	16739
Fiat	Ducato	2.8 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	94	128	Dec 2001	Jul 2006	2024-03-01	16740
BMW	3	316 I	Kombi	Heckantrieb	Benzin	85	115	Mar 2002	Feb 2005	2024-03-01	16741
BMW	3	318 D	Kombi	Heckantrieb	Diesel	85	115	Oct 2002	Mar 2003	2024-03-01	16742
Opel	Vectra c cc	1.8 16V	Schrägheck	Frontantrieb	Benzin	90	122	Aug 2002	Sep 2008	2024-03-01	16743
Opel	Vectra c cc	2.2 16V	Schrägheck	Frontantrieb	Benzin	108	147	Aug 2002	Aug 2008	2024-03-01	16744
Opel	Vectra c cc	2.0 DTI 16V	Schrägheck	Frontantrieb	Diesel	74	101	Aug 2002	Aug 2005	2024-03-01	16745
Opel	Vectra c cc	2.2 DTI 16V	Schrägheck	Frontantrieb	Diesel	92	125	Aug 2002	Jul 2006	2024-03-01	16746

