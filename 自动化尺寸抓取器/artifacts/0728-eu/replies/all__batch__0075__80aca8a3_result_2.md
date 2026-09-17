# 任务：all 第 7401-7500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0075__80aca8a3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7401-7500 行

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
all 第 7401-7500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	4605	1820	1685
EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	4570	1820	1685
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	5182	1904	1958
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	4542	1905	2037
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037
EU-ROVER-200-III-RF-HATCHBACK-01	3973	1688	1419
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390
EU-SEAT-ALHAMBRA-II-7N-MPV-01	4854	1904	1720
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424
EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	4142	1640	1424
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390
EU-SEAT-MARBELLA-028A-VAN-3D-01	3475	1500	1445
EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	3475	1500	1445
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675
EU-SSANGYONG-MUSSO-I-FJ-SUV-01	4640	1905	1735
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	4935	1864	1760
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	3870	1680	1395
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-02	4500	1710	1400
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422
EU-VOLVO-S70-I-SEDAN-4D-01	4720	1760	1400
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430
EU-VW-CADDY-II-9K9-VAN-01	4207	1696	1836
EU-VW-CADDY-III-2K-VAN-01	4405	1794	1833
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Seat	Ibiza ii	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	110	150	Aug 1996	Aug 1999	2024-03-01	7891
Seat	Ibiza ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Aug 1996	Feb 2002	2024-03-01	7892
Seat	Alhambra	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	81	110	Aug 1996	Jun 2000	2024-03-01	7893
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Mar 2010	Jun 2013	2024-03-01	7894
Seat	Arosa	1	Schrägheck	Frontantrieb	Benzin	37	50	May 1997	Jun 2004	2024-03-01	7895
Seat	Arosa	1.4	Schrägheck	Frontantrieb	Benzin	44	60	May 1997	Jun 2004	2024-03-01	7896
Seat	Ibiza ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Feb 1997	Feb 2002	2024-03-01	7897
Seat	Ibiza ii	1.4 I 16V	Schrägheck	Frontantrieb	Benzin	74	101	Jun 1997	Feb 2002	2024-03-01	7898
Seat	Ibiza ii	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Apr 1993	Jun 1999	2024-03-01	7899
Seat	Cordoba	1.9 D	Stufenheck	Frontantrieb	Diesel	47	64	Jan 1996	Aug 1996	2024-03-01	7901
Seat	Cordoba	1.4 I 16V	Stufenheck	Frontantrieb	Benzin	74	101	Sep 1996	Oct 2002	2024-03-01	7902
Seat	Toledo	1.6 I	Schrägheck	Frontantrieb	Benzin	74	101	Nov 1996	Mar 1999	2024-03-01	7903
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	81	110	Mar 2010	Jun 2013	2024-03-01	7904
Seat	Toledo	1.9 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Nov 1996	Mar 1999	2024-03-01	7905
Seat	Marbella	0.9 CAT	Schrägheck	Frontantrieb	Benzin	30	41	Nov 1996	Oct 1998	2024-03-01	7906
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1996	Sep 2004	2024-03-01	7907
Skoda	Octavia	1.8	Schrägheck	Frontantrieb	Benzin	92	125	Sep 1996	Jul 2000	2024-03-01	7908
Skoda	Octavia	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Sep 1996	Mar 2010	2024-03-01	7909
Ssangyong	Korando	2.9 D	Geländewagen geschlossen	Allrad	Diesel	72	98	Dec 1996	Oct 2000	2024-03-01	7910
Ssangyong	Korando	2.3 D	Geländewagen geschlossen	Allrad	Diesel	58	79	Dec 1996	Jun 1998	2024-03-01	7911
Ssangyong	Korando	3.2	Geländewagen geschlossen	Allrad	Benzin	154	209	Dec 1996	Nov 2002	2024-03-01	7912
Ssangyong	Musso	2	Geländewagen geschlossen	Allrad	Benzin	93	126	Oct 1996	May 2005	2024-03-01	7913
Ssangyong	Musso	2.3	Geländewagen geschlossen	Allrad	Benzin	103	140	Oct 1996	Nov 2002	2024-03-01	7914
Suzuki	Baleno	1.3	Schrägheck	Frontantrieb	Benzin	52	71	Sep 1996	May 2002	2024-03-01	7915
Suzuki	Baleno	1.3	Stufenheck	Frontantrieb	Benzin	52	71	Sep 1996	May 2002	2024-03-01	7916
Toyota	Camry	3.0 24V	Stufenheck	Frontantrieb	Benzin	140	190	Aug 1996	Nov 2001	2024-03-01	7917
Toyota	Camry	2.2	Stufenheck	Frontantrieb	Benzin	96	131	Aug 1996	Nov 2001	2024-03-01	7918
Toyota	Picnic	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	94	128	Aug 1996	Sep 2000	2024-03-01	7919
Volvo	S40 i	1.6	Stufenheck	Frontantrieb	Benzin	77	105	Sep 1995	Aug 1999	2024-03-01	7920
Volvo	V40	1.6	Kombi	Frontantrieb	Benzin	77	105	Dec 1995	Aug 1999	2024-03-01	7921
Volvo	S70	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	166	226	Jan 1997	Nov 2000	2024-03-01	7922
Audi	A6 c7	2.8 FSI	Stufenheck	Frontantrieb	Benzin	150	204	Nov 2010	Apr 2015	2024-03-01	7923
Volvo	S70	2	Stufenheck	Frontantrieb	Benzin	132	180	Jan 1997	Nov 2000	2024-03-01	7924
Volvo	V70 i	2.0 Turbo	Kombi	Frontantrieb	Benzin	166	226	Nov 1996	Dec 2000	2024-03-01	7925
Volvo	V70 i	2	Kombi	Frontantrieb	Benzin	132	180	Nov 1996	Mar 2000	2024-03-01	7926
Volvo	V70 i	2.0 Turbo AWD	Kombi	Allrad	Benzin	166	226	Nov 1996	Dec 2000	2024-03-01	7927
Audi	A6 c7	2.8 FSI Quattro	Stufenheck	Allrad	Benzin	150	204	Nov 2010	Apr 2015	2024-03-01	7928
VW	Transporter / multivan t4	2.5 Syncro	Bus	Allrad	Benzin	85	115	Jul 1996	Apr 2003	2025-11-01	7929
Audi	A6 c7	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	220	300	Nov 2010	May 2012	2024-03-01	7930
VW	Transporter / multivan t4	2.5	Bus	Frontantrieb	Benzin	85	115	Aug 1996	Apr 2003	2025-11-01	7931
VW	Passat b5 variant	1.6	Kombi	Frontantrieb	Benzin	74	101	Jun 1997	Nov 2000	2024-03-01	7932
VW	Passat b5 variant	1.8	Kombi	Frontantrieb	Benzin	92	125	Jun 1997	Nov 2000	2024-03-01	7933
VW	Passat b5 variant	1.8 T	Kombi	Frontantrieb	Benzin	110	150	May 1997	Nov 2000	2024-03-01	7934
VW	Passat b5 variant	2.3 VR5	Kombi	Frontantrieb	Benzin	110	150	Jun 1997	Nov 2000	2024-03-01	7935
VW	Passat b5 variant	2.8 V6	Kombi	Frontantrieb	Benzin	142	193	Jun 1997	Nov 2000	2024-03-01	7936
VW	Passat b5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Jun 1997	Nov 2000	2024-03-01	7937
Audi	A6 c7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	130	177	Mar 2011	Sep 2018	2024-03-01	7938
VW	Passat b5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	81	110	Jun 1997	Nov 2000	2024-03-01	7939
VW	Caddy ii	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Sep 1996	Jan 2004	2024-03-01	7940
VW	Passat b5	2.8 V6	Stufenheck	Frontantrieb	Benzin	142	193	Aug 1996	Nov 2000	2024-03-01	7941
Renault	Trafic	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	63	86	Mar 1980	Dec 1986	2024-03-01	7942
Audi	A6 c7	3.0 TDI	Stufenheck	Frontantrieb	Diesel	150	204	Nov 2010	Sep 2018	2024-03-01	7943
Audi	A6 c7	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	150	204	Mar 2011	Sep 2018	2024-03-01	7944
Renault	Trafic	1.6	Kasten	Frontantrieb	Benzin	48	65	Jan 1983	Jun 1986	2024-03-01	7945
Renault	Trafic	1.7	Bus	Frontantrieb	Benzin	50	68	Jun 1986	Apr 1989	2024-03-01	7946
Renault	Trafic	1.7	Kasten	Frontantrieb	Benzin	50	68	Jun 1986	Apr 1989	2024-03-01	7947
Renault	Trafic	1.7	Kasten	Frontantrieb	Benzin	50	68	Aug 1992	Aug 1994	2024-03-01	7948
Renault	Trafic	2	Bus	Frontantrieb	Benzin	59	80	Jun 1986	Apr 1989	2024-03-01	7949
Renault	Trafic	2	Kasten	Frontantrieb	Benzin	59	80	May 1989	Aug 1990	2024-03-01	7950
Renault	Trafic	2	Bus	Frontantrieb	Benzin	59	80	May 1989	Aug 1990	2024-03-01	7951
Renault	Trafic	2.2	Kasten	Frontantrieb	Benzin	70	95	May 1989	Jun 1994	2024-03-01	7952
Renault	Trafic	2.1 D	Kasten	Frontantrieb	Diesel	43	58	May 1989	Jun 1994	2024-03-01	7953
Renault	Trafic	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	51	69	Mar 1980	Apr 1989	2024-03-01	7954
Renault	Trafic	2.5 D	Kasten	Frontantrieb	Diesel	55	75	May 1989	Mar 2001	2024-03-01	7955
Renault	Trafic	2.1 D	Kasten	Frontantrieb	Diesel	47	64	Jun 1994	Oct 1997	2024-03-01	7956
Renault	Trafic	2.2	Kasten	Frontantrieb	Benzin	74	101	Jun 1994	Oct 1997	2024-03-01	7957
Renault	Trafic	1.4	Bus	Frontantrieb	Benzin	35	48	Mar 1980	Apr 1989	2024-03-01	7958
Renault	Trafic	1.4	Kasten	Frontantrieb	Benzin	35	48	Mar 1980	Apr 1989	2024-03-01	7959
Audi	A6 c7	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	180	245	Mar 2011	Sep 2018	2024-03-01	7960
Peugeot	Boxer	1.9 D	Kasten	Frontantrieb	Diesel	51	69	Mar 1994	Apr 2002	2024-03-01	7961
Peugeot	Boxer	1.9 TD	Kasten	Frontantrieb	Diesel	68	92	Mar 1994	Apr 2002	2024-03-01	7962
Peugeot	Boxer	2.5 D	Kasten	Frontantrieb	Diesel	63	86	Mar 1994	Apr 2002	2024-03-01	7963
Peugeot	Boxer	2.5 TD	Kasten	Frontantrieb	Diesel	76	103	Mar 1994	Dec 1997	2024-03-01	7964
Ford	Focus iii	1.6 TI	Stufenheck	Frontantrieb	Benzin	77	105	Jul 2010	Feb 2020	2024-03-01	7965
Ford	Focus iii	1.6 TI	Stufenheck	Frontantrieb	Benzin	92	125	Jul 2010	Feb 2020	2024-03-01	7966
Ford	Focus iii	1.6 Flexifuel	Stufenheck	Frontantrieb	Benzin/Ethanol	88	120	Jul 2010	Feb 2020	2024-03-01	7967
Renault	Super 5	1.4 CAT	Schrägheck	Frontantrieb	Benzin	43	58	Oct 1985	Dec 1996	2024-03-01	7968
Ford	Focus iii	1.6 Ecoboost	Stufenheck	Frontantrieb	Benzin	110	150	Jul 2010	Jun 2014	2024-03-01	7969
Ford	Focus iii	1.6 Ecoboost	Stufenheck	Frontantrieb	Benzin	134	182	Jul 2010	Jun 2014	2024-03-01	7970
Fiat	1500-2300	1500 L	Stufenheck	Heckantrieb	Benzin	55	75	Oct 1963	Dec 1970	2024-03-01	7972
Ssangyong	Musso	2.3 D	Geländewagen geschlossen	Allrad	Diesel	59	80	Oct 1995	Apr 1999	2024-03-01	7973
VW	Polo	90 1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Sep 1996	Sep 2001	2024-03-01	7974
Rover	200 ii	216 1.6i 16V	Cabriolet	Frontantrieb	Benzin	82	111	Jan 1996	Nov 1999	2024-03-01	7975
Peugeot	Partner	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Jun 1996	Sep 2005	2024-03-01	7976
Peugeot	Partner	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Jun 1996	Dec 2015	2024-03-01	7977
Peugeot	Partner	1.8 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	43	58	Jun 1996	Dec 2002	2024-03-01	7978
Peugeot	Partner	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	51	69	Jun 1996	Dec 2002	2024-03-01	7979
Honda	Cr-V iv	2.4 AWD	SUV	Allrad	Benzin	140	190	Jan 2012	Dec 2018	2025-12-01	7980
Asia Motors	Rocsta	1.8 I 4X4	Geländewagen offen	Allrad	Benzin	57	77	Jun 1993	Dec 1999	2024-03-01	7981
Volvo	850	T5	Stufenheck	Frontantrieb	Benzin	166	226	Aug 1993	Jul 1996	2024-03-01	7982
Asia Motors	Rocsta	2.2 D 4X4	Geländewagen offen	Allrad	Diesel	45	61	Jun 1993	Dec 1999	2024-03-01	7983
Volvo	850	T5-r	Stufenheck	Frontantrieb	Benzin	184	250	Aug 1995	Dec 1996	2024-03-01	7984
Volvo	850	T5	Kombi	Frontantrieb	Benzin	166	226	Feb 1993	Dec 1996	2024-03-01	7985
Volvo	850	T5-r	Kombi	Frontantrieb	Benzin	184	250	Aug 1995	Dec 1996	2024-03-01	7986
Pontiac	Trans sport	3.8	Großraumlimousine	Frontantrieb	Benzin	127	172	Jul 1989	Mar 1997	2024-03-01	7989
Ford	Focus iii	1.6 Tdci	Stufenheck	Frontantrieb	Diesel	70	95	Jul 2010	Feb 2020	2024-03-01	7991
Pontiac	Trans sport	3.4	Großraumlimousine	Frontantrieb	Benzin	134	182	Mar 1997	Sep 1998	2024-03-01	7992
Ford	Focus iii	1.6 Tdci	Stufenheck	Frontantrieb	Diesel	85	115	Jul 2010	Feb 2020	2024-03-01	7993
Chevrolet	Trans sport	3.4	Großraumlimousine	Frontantrieb	Benzin	137	186	Aug 1996	Sep 2005	2024-03-01	7995
Chevrolet	Lumina apv	3.1	Großraumlimousine	Frontantrieb	Benzin	119	162	Jan 1994	Jul 1996	2024-03-01	7996


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类处理全部 100 个输入 Ktype，并保留尚未闭合 Ktype 的基础映射行。
* 本轮完成 74 个 Ktype，共形成 94 条 `READY` 派生映射；复用 30 个已有尺寸组，首次创建并闭合 15 个尺寸组。
* 新闭合范围包括 Alhambra I、Arosa 改款前后、Octavia I 改款前后、Korando II 两个高度分支、Camry XV20、Picnic、Passat B5 三厢/旅行版、Focus III 三厢、Fiat 1500 L，以及两代 Pontiac Trans Sport。([Auto Data][1])
* 其余 26 个 Ktype 已写入具体 `PENDING` 原因，未建立猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* READY 映射行：94
* PENDING Ktype／映射行：26
* 当前已引用尺寸组：45
* 本轮新建尺寸组：15
* 复用已有尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7891	7891	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	HIGH	2.0 16V GT/Cupra三门外廓。	READY
7892_3dr_prefl	7892	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_5dr_prefl	7892	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_3dr_facelift	7892	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_5dr_facelift	7892	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7893	7893	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	HIGH		READY
7894	7894	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	HIGH		READY
7895_prefl	7895	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	HIGH	Ktype跨2000年改款，拆分改款前外廓。	READY
7895_facelift	7895	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2000年改款，拆分改款后外廓。	READY
7896_prefl	7896	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	HIGH	Ktype跨2000年改款，拆分改款前外廓。	READY
7896_facelift	7896	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2000年改款，拆分改款后外廓。	READY
7897_3dr_prefl	7897	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_5dr_prefl	7897	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_3dr_facelift	7897	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_5dr_facelift	7897	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_3dr_prefl	7898	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_5dr_prefl	7898	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_3dr_facelift	7898	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_5dr_facelift	7898	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7899_3dr_6k	7899	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_5dr_6k	7899	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_3dr_6k1	7899	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_5dr_6k1	7899	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7901	7901	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
7902_prefl	7902	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	Ktype跨1999年外观改款，拆分改款前。	READY
7902_facelift	7902	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	Ktype跨1999年外观改款，拆分改款后。	READY
7903	7903	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
7904	7904	Wagon	Octavia II	1Z	5		MEDIUM	候选为1Z旅行版改款后外廓；前驱与既有4×4尺寸组边界待闭合。	PENDING: 旅行版前驱尺寸组尚未闭合
7905	7905	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
7906	7906	Hatchback	Marbella	28	3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH		READY
7907_prefl	7907	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	Ktype跨2000年改款，拆分改款前外廓。	READY
7907_facelift	7907	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨2000年改款，拆分改款后外廓。	READY
7908	7908	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	HIGH		READY
7909_prefl	7909	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	Ktype跨2000年改款，拆分改款前外廓。	READY
7909_facelift	7909	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨2000年改款，拆分改款后外廓。	READY
7910	7910	SUV	Korando II	KJ	3		LOW	2.9 D存在1840/1940 mm高度候选。	PENDING: 2.9 D车身高度冲突未解决
7911	7911	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	MEDIUM	2.3 D闭合车身高度分支。	READY
7912	7912	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH	3.2汽油闭合车身高度分支。	READY
7913	7913	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7914	7914	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7915	7915	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	HIGH		READY
7916	7916	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
7917	7917	Sedan	Camry IV	XV20	4	EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	HIGH		READY
7918	7918	Sedan	Camry IV	XV20	4	EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	HIGH		READY
7919	7919	MPV	Picnic I	XM1	5	EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	HIGH		READY
7920	7920	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
7921	7921	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
7922	7922	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7923	7923	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7924	7924	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7925	7925	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7926	7926	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7927	7927	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7928	7928	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7929	7929	MPV	Transporter T4				LOW	Bus Ktype可能覆盖SWB/LWB及不同车顶。	PENDING: T4轴距与车顶物理分支未确认
7930	7930	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7931	7931	MPV	Transporter T4				LOW	Bus Ktype可能覆盖SWB/LWB及不同车顶。	PENDING: T4轴距与车顶物理分支未确认
7932	7932	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7933	7933	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7934	7934	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7935	7935	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7936	7936	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7937	7937	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7938	7938	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7939	7939	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7940	7940	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	HIGH	原始车身为Kasten/Großraumlimousine；外廓按9K9统一。	READY
7941	7941	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
7942	7942	Pickup	Trafic I Phase 1				LOW	Pritsche/Fahrgestell可能覆盖不同轴距和驾驶室。	PENDING: 底盘车轴距与驾驶室分支未确认
7943	7943	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7944	7944	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7945	7945	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH		READY
7946	7946	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH		READY
7947	7947	Van	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	厢式与客车外部尺寸一致，复用已闭合Phase 2短轴低顶组。	READY
7948	7948	Van	Trafic I Phase 3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7949	7949	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH		READY
7950	7950	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7951	7951	MPV	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	HIGH		READY
7952	7952	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7953	7953	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7954	7954	Pickup	Trafic I Phase 1/2				LOW	Pritsche/Fahrgestell跨车身更新且可能覆盖多轴距。	PENDING: 底盘车物理分支未确认
7955	7955	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7956	7956	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7957	7957	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7958_pre86	7958	MPV	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分早期外廓。	READY
7958_post86	7958	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分后期外廓。	READY
7959_pre86	7959	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分早期外廓。	READY
7959_post86	7959	Van	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	Ktype跨1986年车身更新；后期厢式复用同外廓客车尺寸组。	READY
7960	7960	Sedan	A6 C7	4G2	4		MEDIUM	候选需按2014/2015改款前后边界拆分。	PENDING: A6 C7改款前后尺寸组尚未闭合
7961	7961	Van	Boxer I	230			LOW	Kasten Ktype可能覆盖SWB/MWB及不同车顶高度。	PENDING: Boxer厢式车轴距与车顶分支未确认
7962	7962	Van	Boxer I	230			LOW	Kasten Ktype可能覆盖SWB/MWB及不同车顶高度。	PENDING: Boxer厢式车轴距与车顶分支未确认
7963	7963	Van	Boxer I	230			LOW	Kasten Ktype可能覆盖SWB/MWB及不同车顶高度。	PENDING: Boxer厢式车轴距与车顶分支未确认
7964	7964	Van	Boxer I	230			LOW	Kasten Ktype可能覆盖SWB/MWB及不同车顶高度。	PENDING: Boxer厢式车轴距与车顶分支未确认
7965	7965	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7966	7966	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7967	7967	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7968	7968	Hatchback	Super 5				LOW	生产范围覆盖门数与后期车型边界，候选外廓未闭合。	PENDING: 门数与尺寸组尚未确认
7969	7969	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7970	7970	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7972	7972	Sedan	1500 L		4	EU-FIAT-1500L-SEDAN-4D-01	HIGH		READY
7973	7973	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7974	7974	Sedan	Polo III	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH		READY
7975	7975	Convertible	200 II	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
7976	7976	Van	Partner I	M49/M59			LOW	原始结构混合Kasten/Großraumlimousine，且生产范围可能跨改款。	PENDING: 车身用途与改款物理分支未确认
7977	7977	Van	Partner I	M49/M59			LOW	原始结构混合Kasten/Großraumlimousine，且生产范围可能跨改款。	PENDING: 车身用途与改款物理分支未确认
7978	7978	Van	Partner I	M49/M59			LOW	原始结构混合Kasten/Großraumlimousine，且生产范围可能跨改款。	PENDING: 车身用途与改款物理分支未确认
7979	7979	Van	Partner I	M49/M59			LOW	原始结构混合Kasten/Großraumlimousine，且生产范围可能跨改款。	PENDING: 车身用途与改款物理分支未确认
7980_prefl	7980	SUV	CR-V IV	RM	5	EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	MEDIUM	Ktype跨2015年改款，拆分改款前外廓。	READY
7980_facelift	7980	SUV	CR-V IV	RM	5	EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	MEDIUM	Ktype跨2015年改款，拆分改款后外廓。	READY
7981	7981	SUV	Rocsta		2		LOW	开放式越野车三维与不含后视镜宽度尚未闭合。	PENDING: Rocsta尺寸来源尚未闭合
7982	7982	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
7983	7983	SUV	Rocsta		2		LOW	开放式越野车三维与不含后视镜宽度尚未闭合。	PENDING: Rocsta尺寸来源尚未闭合
7984	7984	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
7985	7985	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
7986	7986	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
7989	7989	MPV	Trans Sport I	GMT199	3	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
7991	7991	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7992	7992	MPV	Trans Sport II	GMT200	3	EU-PONTIAC-TRANS-SPORT-II-GMT200-MPV-SWB-01	HIGH	标准轴距车身。	READY
7993	7993	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7995	7995	MPV	Trans Sport II	GMT200	3		LOW	欧洲Chevrolet长/短轴边界与三维尚未闭合。	PENDING: Chevrolet Trans Sport尺寸组未确认
7996	7996	MPV	Lumina APV I	GMT199	3		LOW	第一代APV三维及不含后视镜宽度尚未闭合。	PENDING: Lumina APV尺寸组未确认
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	4620	1810	1730	Auto-Data	https://www.auto-data.net/en/seat-alhambra-model-1452
EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	3536	1639	1480	Auto-Data	https://www.auto-data.net/en/seat-arosa-model-1448
EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	3551	1639	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3071015/seat_arosa_1_0.html
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/3134390/skoda_octavia_1_6_75.html
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3135425/skoda_octavia_1_9_tdi_90.html
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940	Auto-Data	https://www.auto-data.net/en/ssangyong-korando-ii-kj-2.3-d-80hp-15993
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3160850/ssangyong_korando_e32.html
EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	4765	1785	1430	Auto-Data	https://www.auto-data.net/en/toyota-camry-iv-xv20-generation-1014
EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	4530	1695	1620	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/3486080/toyota_picnic_2_0_automatic.html
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496	EncyCARpedia	https://www.encycarpedia.com/volkswagen/97-passat-variant-1-8-5v-turbo-estate
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	Drive.Place	https://volkswagen.drive.place/passat/b5/group_sedan/323104
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1592975/ford_focus_4-dr_1_6_ti-vct_125_titanium.html
EU-FIAT-1500L-SEDAN-4D-01	4485	1620	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/709430/fiat_1500l.html
EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	4946	1886	1670	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2855810/pontiac_trans_sport_3_8_v6.html
EU-PONTIAC-TRANS-SPORT-II-GMT200-MPV-SWB-01	4757	1847	1712	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2859170/pontiac_trans_sport_standard.html
```

## 下一步优先处理

1. 优先闭合 Peugeot Boxer I 厢式车 Ktype `7961–7964` 的 SWB/MWB、低顶/高顶物理分支，并判断能否复用已有 Boxer I Bus 尺寸事实。
2. 批量解决 Audi A6 C7 的 7 个 Ktype，以及 Octavia II Wagon `7904` 的改款和驱动边界。
3. 继续处理 Transporter T4、Trafic 底盘车、Partner I、Super 5、Rocsta、Chevrolet Trans Sport 和 Lumina APV。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-alhambra-model-1452?utm_source=chatgpt.com "Seat Alhambra | Technical Specs, Fuel consumption, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮将 16 个 Ktype 从 `PENDING` 转为 `READY`，新增 19 条确定映射。
* Octavia II 旅行版改款后前驱外廓与已有 4×4 尺寸组完全一致，直接复用；Korando 2.9 D 复用既有低高度尺寸组，不重复建组。([汽车目录][1])
* 首次闭合 A6 C7 改款前三厢、T4 改款后短轴/长轴客车、Super 5 三门/五门和两种 Rocsta 外廓。([汽车目录][2])
* 首次闭合 Chevrolet Trans Sport 186 HP 与 Lumina APV 第一代尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：113
* PENDING Ktype／映射行：10
* 当前已引用尺寸组：55
* 本轮首次创建尺寸组：9
* 本轮复用既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7904	7904	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH		READY
7910	7910	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH		READY
7923	7923	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7928	7928	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7929_swb	7929	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7929_lwb	7929	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7930	7930	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7931_swb	7931	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7931_lwb	7931	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7938	7938	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7943	7943	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7944	7944	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7960	7960	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7968_3dr	7968	Hatchback	Super 5		3	EU-RENAULT-SUPER5-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门物理分支。	READY
7968_5dr	7968	Hatchback	Super 5		5	EU-RENAULT-SUPER5-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门物理分支。	READY
7981	7981	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-SWB-01	HIGH		READY
7983	7983	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-LWB-01	HIGH		READY
7995	7995	MPV	Trans Sport II	U	5	EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	HIGH		READY
7996	7996	MPV	Lumina APV I	GMT199	4	EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	MEDIUM	输入功率与规格资料标注不一致；物理车身边界已确认。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1588355/audi_a6_2_8_fsi.html
EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	4789	1840	1940	Auto-Data	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-115hp-49355
EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	5189	1840	1940	Auto-Data	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.5-115hp-49366
EU-RENAULT-SUPER5-HATCHBACK-3D-01	3591	1584	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/50105/renault_5_1_4_gtl.html
EU-RENAULT-SUPER5-HATCHBACK-5D-01	3651	1584	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/2938490/renault_5_gtl_1_4_5-door.html
EU-ASIA-MOTORS-ROCSTA-SUV-SWB-01	3585	1690	1820	Auto-Data	https://www.auto-data.net/en/asia-rocsta-1.8-i-4x4-86hp-2878
EU-ASIA-MOTORS-ROCSTA-SUV-LWB-01	3720	1630	1800	Auto-Data	https://www.auto-data.net/en/asia-rocsta-2.2-d-4x4-61hp-2879
EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	5113	1850	1730	Auto-Data	https://www.auto-data.net/en/chevrolet-trans-sport-u-3.4-i-v6-186hp-14448
EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	4844	1877	1669	Auto-Data	https://www.auto-data.net/en/chevrolet-lumina-apv-3.1-i-122hp-14475
```

## 下一步优先处理

1. 闭合 Peugeot Boxer I 厢式车 Ktype `7961–7964` 的轴距与车顶分支，优先匹配已有 Boxer I 尺寸组。
2. 集中处理 Partner I `7976–7979` 的改款前后和 Van／MPV共同外廓边界。
3. 最后处理 Trafic I 底盘车 `7942、7954` 的轴距与驾驶室分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2010/3138755/skoda_octavia_combi_2_0_tdi_pd_140.html?utm_source=chatgpt.com "2010 Skoda Octavia Combi 2.0 TDI PD (140) Specs Review (103 kW / 140 PS / 138 hp) (up to May 2010 for Europe )"
[2]: https://www.automobile-catalog.com/car/2011/1588355/audi_a6_2_8_fsi.html?utm_source=chatgpt.com "2011 Audi A6 2.8 FSI Specs Review (150 kW / 204 PS / 201 hp) (since April 2011 for Europe )"
[3]: https://www.auto-data.net/en/chevrolet-trans-sport-u-3.4-i-v6-186hp-14448 "Chevrolet Trans Sport (U) 3.4 i V6 (186 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮未强行创建尺寸组。Partner 官方乘用版资料为 `4137 × 1724 × 1810 mm`，而改款前乘用版及厢式版资料分别出现 `4110 × 1720 × 1870 mm` 与 `4110 × 1720 × 1800 mm`；原始 Ktype 又混合 `Kasten/Großraumlimousine`，因此暂不拼接或任选尺寸。
* Boxer `7961–7964` 已进一步确认属于 `230L` 厢式车条目，但现有跨年度资料同时覆盖 1994–2006 年及 2002 年改款，所列车长与已有改款前缓存不一致，且没有闭合各发动机对应的轴距和车顶分支，因此仅修正映射边界，不建立新组。([KMotorShop][1])
* Trafic 后驱底盘车仍存在多轴距及底盘衍生边界；现有 Bus/Van 缓存不能直接复用。本轮将剩余 10 行的 `Notes`、`BodyCode` 和具体 PENDING 原因机械修正。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：113
* PENDING Ktype／映射行：10
* 当前已引用尺寸组：55
* 本轮首次创建／修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7942	7942	Pickup	Trafic I Phase 1				LOW	后驱底盘车可能包含不同轴距及驾驶室外廓；现有Bus/Van尺寸组不可直接复用。	PENDING: Trafic底盘车轴距与驾驶室分支未闭合
7954	7954	Pickup	Trafic I Phase 1/2				LOW	生产范围跨车身阶段，且后驱底盘车可能包含不同轴距及驾驶室外廓。	PENDING: Trafic底盘车阶段与物理分支未闭合
7961	7961	Van	Boxer I	230L			LOW	已确认230L厢式车；改款前尺寸与跨改款资料冲突，轴距及车顶分支未闭合。	PENDING: Boxer改款前轴距与车顶分支未闭合
7962	7962	Van	Boxer I	230L			LOW	已确认230L厢式车；改款前尺寸与跨改款资料冲突，轴距及车顶分支未闭合。	PENDING: Boxer改款前轴距与车顶分支未闭合
7963	7963	Van	Boxer I	230L			LOW	已确认230L厢式车；改款前尺寸与跨改款资料冲突，轴距及车顶分支未闭合。	PENDING: Boxer改款前轴距与车顶分支未闭合
7964	7964	Van	Boxer I	230L			LOW	已确认230L厢式车；改款前尺寸与跨改款资料冲突，轴距及车顶分支未闭合。	PENDING: Boxer改款前轴距与车顶分支未闭合
7976	7976	Van	Partner I				LOW	原始Kasten/Großraumlimousine混合商用与乘用外廓；车身代码及市场尺寸边界未闭合。	PENDING: Partner车身用途与改款尺寸冲突未解决
7977	7977	Van	Partner I				LOW	原始Kasten/Großraumlimousine混合商用与乘用外廓；车身代码及市场尺寸边界未闭合。	PENDING: Partner车身用途与改款尺寸冲突未解决
7978	7978	Van	Partner I				LOW	原始Kasten/Großraumlimousine混合商用与乘用外廓；车身代码及市场尺寸边界未闭合。	PENDING: Partner车身用途与改款尺寸冲突未解决
7979	7979	Van	Partner I				LOW	原始Kasten/Großraumlimousine混合商用与乘用外廓；车身代码及市场尺寸边界未闭合。	PENDING: Partner车身用途与改款尺寸冲突未解决
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 寻找 Boxer I `230L` 改款前官方规格或型式核准资料，一次性闭合发动机对应的 SWB/MWB 与低顶/高顶分支。
2. 分别闭合 Partner I 改款前后 `Kasten` 与 `Großraumlimousine` 外廓，解决长度和高度的市场口径冲突。
3. 最后闭合 Trafic I 后驱底盘车的轴距、驾驶室及改款阶段分支。

[1]: https://www.kmotorshop.com/en/device/car-list/1909?utm_source=chatgpt.com "Cars PEUGEOT BOXER Van (230L)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已确认 `7976–7979` 均为 Peugeot Partner **Kastenwagen 厢式车**，不再按乘用 MPV 与商用 Van 混合处理。([Alufelgen Sportfahrwerke und mehr][1])
* `7976、7977` 的生产范围跨越 2002 年改款，拆为 M49 改款前与 M59 改款后两个物理外廓；`7978、7979` 仅关联改款前尺寸组。
* 首次闭合 Partner I 改款前厢式车 `4110 × 1720 × 1800 mm`，以及改款后厢式车 `4137 × 1724 × 1810 mm`。([标致驾驭][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射行：119
* PENDING Ktype／映射行：6
* 当前已引用尺寸组：57
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7976_prefl	7976	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	Ktype跨2002年改款，拆分改款前厢式车外廓。	READY
7976_facelift	7976	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	Ktype跨2002年改款，拆分改款后厢式车外廓。	READY
7977_prefl	7977	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	Ktype跨2002年改款，拆分改款前厢式车外廓。	READY
7977_facelift	7977	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	Ktype跨2002年改款，拆分改款后厢式车外廓。	READY
7978	7978	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH		READY
7979	7979	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800	Drive.Place	https://peugeot.drive.place/partner/i/group_furgon/604252
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810	Peugeot UK official Partner brochure; Drive.Place	https://xr793.com/wp-content/uploads/2022/12/2003-Peugeot-Partner-Combi-UK.pdf;https://peugeot.drive.place/partner/ii/group_furgon/604107
```

## 下一步优先处理

1. 闭合 Boxer I `7961、7962` 的 `270C/270CS` 以及 1.9 TD 可用车顶分支。
2. 闭合 Boxer I `7963、7964` 的 `310C/310CS/320M/320MH` 等轴距、载重和车顶分支。
3. 最后处理 Trafic I P6 后驱底盘车 `7942、7954` 的轴距与驾驶室外廓。

推进信号：CONTINUE

[1]: https://www.jms-fahrzeugteile.com/en/brake-technology/ebc-brake-discsbrake-pads/ebc-standard-bremsbelaege-fuer/peugeot/partner/vavornefront/1177960/ebc-blackstuff-pads-dp1104-30080-fits-for-peugeot-partner-5?utm_source=chatgpt.com "EBC Blackstuff pads DP1104(30080) fits for Peugeot Partner 5 | JMS ..."
[2]: https://peugeot.drive.place/partner/i/group_furgon/604252?utm_source=chatgpt.com "Peugeot Partner I 1.8 MT 58 hp Van — specifications"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Peugeot Boxer I 的 4 个待处理 Ktype。`7961–7964` 按 `270C/270CS/310C/310CS/320M/320MH/350MH/320LH/350LH` 的实际轴距与车顶外廓拆分，共新增 21 条 `READY` 映射。车型目录确认了各发动机可用的车身分支，尺寸目录提供了对应的完整三维。([La Centrale][1])
* 其中 4 个尺寸组与跨批次缓存三维完全一致，直接复用；本轮仅首次创建其余 5 个尺寸组。
* 当前仅剩 Renault Trafic I 后驱底盘车 `7942、7954` 尚未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：140
* PENDING Ktype／映射行：2
* 当前映射已引用尺寸组：66
* 本轮首次创建尺寸组：5
* 本轮复用已有尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7961_270c	7961	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	270C短轴低顶外廓。	READY
7961_270cs	7961	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	270CS短轴高顶外廓。	READY
7962_270c	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	270C短轴低顶外廓。	READY
7962_270cs	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	270CS短轴高顶外廓。	READY
7962_310c	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7962_310cs	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7962_320m	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7963_310c	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7963_310cs	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7963_320m	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7963_320mh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	320MH中轴高顶外廓。	READY
7963_350mh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	MEDIUM	350MH中轴高顶外廓。	READY
7963_320lh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	320LH长轴高顶外廓。	READY
7963_350lh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	350LH长轴高顶外廓。	READY
7964_310c	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7964_310cs	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7964_320m	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7964_320mh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	320MH中轴高顶外廓。	READY
7964_350mh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	MEDIUM	350MH中轴高顶外廓。	READY
7964_320lh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	320LH长轴高顶外廓。	READY
7964_350lh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	350LH长轴高顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
```

## 下一步优先处理

1. 闭合 `7942` 的 Trafic I Phase 1 后驱 2.0 底盘车轴距及驾驶室分支。
2. 闭合 `7954` 的 Trafic I 2.5 D 后驱底盘车改款阶段、轴距及驾驶室分支。
3. 两项完成且 `PENDING=0` 后，仅执行一次机械闭合检查并直接输出最终完整两张 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html "Fiche Technique Peugeot Boxer Année 1994 - La Centrale"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7401-7500_ktype_dimension_mapping_final.tsv
- all_7401-7500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后两个 Renault Trafic I Phase 1 P6 后驱底盘车 Ktype 已闭合：汽油平台为 `4535 × 1996 × 2070 mm`，柴油平台为 `4535 × 1996 × 2067 mm`。([Transit Center Ford Transit Spare Parts][1])
* 当前批次已达到 `PENDING=0`。
* 已完成机械收尾检查：固定表头正确、142 个 `id` 唯一、68 个 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸和来源字段完整、无孤立尺寸组。
* 两个任务指定 TSV 文件均已创建并校验。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：142
* PENDING：0
* 当前引用尺寸组：68
* 映射引用闭合：68/68
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7891	7891	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	HIGH	2.0 16V GT/Cupra三门外廓。	READY
7892_3dr_prefl	7892	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_5dr_prefl	7892	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_3dr_facelift	7892	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7892_5dr_facelift	7892	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7893	7893	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	HIGH		READY
7894	7894	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	HIGH		READY
7895_prefl	7895	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	HIGH	Ktype跨2000年改款，拆分改款前外廓。	READY
7895_facelift	7895	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2000年改款，拆分改款后外廓。	READY
7896_prefl	7896	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	HIGH	Ktype跨2000年改款，拆分改款前外廓。	READY
7896_facelift	7896	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2000年改款，拆分改款后外廓。	READY
7897_3dr_prefl	7897	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_5dr_prefl	7897	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_3dr_facelift	7897	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7897_5dr_facelift	7897	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_3dr_prefl	7898	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_5dr_prefl	7898	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_3dr_facelift	7898	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7898_5dr_facelift	7898	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨6K1/6K2及3/5门，按物理分支拆分。	READY
7899_3dr_6k	7899	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_5dr_6k	7899	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_3dr_6k1	7899	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7899_5dr_6k1	7899	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨早期6K与6K1且覆盖3/5门。	READY
7901	7901	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
7902_prefl	7902	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	Ktype跨1999年外观改款，拆分改款前。	READY
7902_facelift	7902	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	Ktype跨1999年外观改款，拆分改款后。	READY
7903	7903	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
7904	7904	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH		READY
7905	7905	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
7906	7906	Hatchback	Marbella	28	3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH		READY
7907_prefl	7907	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	Ktype跨2000年改款，拆分改款前外廓。	READY
7907_facelift	7907	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨2000年改款，拆分改款后外廓。	READY
7908	7908	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	HIGH		READY
7909_prefl	7909	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	Ktype跨2000年改款，拆分改款前外廓。	READY
7909_facelift	7909	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨2000年改款，拆分改款后外廓。	READY
7910	7910	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH		READY
7911	7911	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	MEDIUM	2.3 D闭合车身高度分支。	READY
7912	7912	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH	3.2汽油闭合车身高度分支。	READY
7913	7913	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7914	7914	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7915	7915	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	HIGH		READY
7916	7916	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
7917	7917	Sedan	Camry IV	XV20	4	EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	HIGH		READY
7918	7918	Sedan	Camry IV	XV20	4	EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	HIGH		READY
7919	7919	MPV	Picnic I	XM1	5	EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	HIGH		READY
7920	7920	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
7921	7921	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
7922	7922	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7923	7923	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7924	7924	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7925	7925	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7926	7926	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7927	7927	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7928	7928	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7929_swb	7929	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7929_lwb	7929	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7930	7930	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7931_swb	7931	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7931_lwb	7931	MPV	Transporter T4 facelift			EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	MEDIUM	Ktype覆盖短轴与长轴客车外廓。	READY
7932	7932	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7933	7933	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7934	7934	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7935	7935	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7936	7936	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7937	7937	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7938	7938	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7939	7939	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
7940	7940	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	HIGH	原始车身为Kasten/Großraumlimousine；外廓按9K9统一。	READY
7941	7941	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
7942	7942	Pickup	Trafic I Phase 1	P6	2	EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-PETROL-01	HIGH	2.0汽油P6标准平台/底盘外廓。	READY
7943	7943	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7944	7944	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7945	7945	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH		READY
7946	7946	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH		READY
7947	7947	Van	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	厢式与客车外部尺寸一致，复用已闭合Phase 2短轴低顶组。	READY
7948	7948	Van	Trafic I Phase 3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7949	7949	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH		READY
7950	7950	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7951	7951	MPV	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	HIGH		READY
7952	7952	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7953	7953	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7954	7954	Pickup	Trafic I Phase 1	P6	2	EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-DIESEL-01	HIGH	2.5 D P6标准平台/底盘外廓。	READY
7955	7955	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7956	7956	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7957	7957	Van	Trafic I Phase 2/3			EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	复用已闭合Phase 2/3短轴低顶外廓。	READY
7958_pre86	7958	MPV	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分早期外廓。	READY
7958_post86	7958	MPV	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分后期外廓。	READY
7959_pre86	7959	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH	Ktype跨1986年车身更新，拆分早期外廓。	READY
7959_post86	7959	Van	Trafic I Phase 2			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	Ktype跨1986年车身更新；后期厢式复用同外廓客车尺寸组。	READY
7960	7960	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH		READY
7961_270c	7961	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	270C短轴低顶外廓。	READY
7961_270cs	7961	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	270CS短轴高顶外廓。	READY
7962_270c	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	270C短轴低顶外廓。	READY
7962_270cs	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	270CS短轴高顶外廓。	READY
7962_310c	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7962_310cs	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7962_320m	7962	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7963_310c	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7963_310cs	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7963_320m	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7963_320mh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	320MH中轴高顶外廓。	READY
7963_350mh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	MEDIUM	350MH中轴高顶外廓。	READY
7963_320lh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	320LH长轴高顶外廓。	READY
7963_350lh	7963	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	350LH长轴高顶外廓。	READY
7964_310c	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	310C短轴低顶外廓。	READY
7964_310cs	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	310CS短轴高顶外廓。	READY
7964_320m	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	320M中轴低顶外廓。	READY
7964_320mh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	320MH中轴高顶外廓。	READY
7964_350mh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	MEDIUM	350MH中轴高顶外廓。	READY
7964_320lh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	320LH长轴高顶外廓。	READY
7964_350lh	7964	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	350LH长轴高顶外廓。	READY
7965	7965	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7966	7966	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7967	7967	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7968_3dr	7968	Hatchback	Super 5		3	EU-RENAULT-SUPER5-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门物理分支。	READY
7968_5dr	7968	Hatchback	Super 5		5	EU-RENAULT-SUPER5-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门物理分支。	READY
7969	7969	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7970	7970	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7972	7972	Sedan	1500 L		4	EU-FIAT-1500L-SEDAN-4D-01	HIGH		READY
7973	7973	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
7974	7974	Sedan	Polo III	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH		READY
7975	7975	Convertible	200 II	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
7976_prefl	7976	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	Ktype跨2002年改款，拆分改款前厢式车外廓。	READY
7976_facelift	7976	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	Ktype跨2002年改款，拆分改款后厢式车外廓。	READY
7977_prefl	7977	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	Ktype跨2002年改款，拆分改款前厢式车外廓。	READY
7977_facelift	7977	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	Ktype跨2002年改款，拆分改款后厢式车外廓。	READY
7978	7978	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH		READY
7979	7979	Van	Partner I	M49		EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH		READY
7980_prefl	7980	SUV	CR-V IV	RM	5	EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	MEDIUM	Ktype跨2015年改款，拆分改款前外廓。	READY
7980_facelift	7980	SUV	CR-V IV	RM	5	EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	MEDIUM	Ktype跨2015年改款，拆分改款后外廓。	READY
7981	7981	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-SWB-01	HIGH		READY
7982	7982	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
7983	7983	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-LWB-01	HIGH		READY
7984	7984	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
7985	7985	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
7986	7986	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
7989	7989	MPV	Trans Sport I	GMT199	3	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
7991	7991	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7992	7992	MPV	Trans Sport II	GMT200	3	EU-PONTIAC-TRANS-SPORT-II-GMT200-MPV-SWB-01	HIGH	标准轴距车身。	READY
7993	7993	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7995	7995	MPV	Trans Sport II	U	5	EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	HIGH		READY
7996	7996	MPV	Lumina APV I	GMT199	4	EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	MEDIUM	输入功率与规格资料标注不一致；物理车身边界已确认。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7401-7500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3066545/seat_ibiza_gti_cupra_2_0_16v.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Auto-Data	https://www.auto-data.net/en/seat-ibiza-ii-1.4-i-16v-101hp-13500
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Auto-Data	https://www.auto-data.net/en/seat-ibiza-ii-1.4-i-16v-101hp-13500
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422	Auto-Data	https://www.auto-data.net/en/seat-ibiza-ii-facelift-1999-generation-2907
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422	Auto-Data	https://www.auto-data.net/en/seat-ibiza-ii-facelift-1999-generation-2907
EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	4620	1810	1730	Auto-Data	https://www.auto-data.net/en/seat-alhambra-model-1452
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462	Auto-Data	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-1.9-tdi-105hp-14187
EU-SEAT-AROSA-I-6H-HATCHBACK-PREFL-01	3536	1639	1480	Auto-Data	https://www.auto-data.net/en/seat-arosa-model-1448
EU-SEAT-AROSA-I-6H-HATCHBACK-FACELIFT-01	3551	1639	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3071015/seat_arosa_1_0.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3065780/seat_ibiza_1_6i.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3065780/seat_ibiza_1_6i.html
EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	4142	1640	1424	EncyCARpedia	https://www.encycarpedia.com/seat/97-cordoba-1-6-se-saloon
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424	Auto-Data	https://www.auto-data.net/en/seat-cordoba-i-facelift-1999-1.6-101hp-13420
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424	Auto-Data	https://www.auto-data.net/en/seat-toledo-i-1l-facelift-1995-generation-8912
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468	Auto-Data	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-2.0-tdi-cr-140hp-4x4-14207
EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	3475	1500	1445	Auto-Data	https://www.auto-data.net/en/seat-marbella-28-generation-2910
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/3134390/skoda_octavia_1_6_75.html
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3135425/skoda_octavia_1_9_tdi_90.html
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3160850/ssangyong_korando_e32.html
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940	Auto-Data	https://www.auto-data.net/en/ssangyong-korando-ii-kj-2.3-d-80hp-15993
EU-SSANGYONG-MUSSO-I-FJ-SUV-01	4640	1905	1735	Auto-Data	https://www.auto-data.net/en/ssangyong-musso-i-generation-3570
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390	Auto-Data	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.3-i-16v-85hp-16481
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390	Auto-Data	https://www.auto-data.net/en/suzuki-baleno-eg-1995-1.3-i-16v-85hp-16470
EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	4765	1785	1430	Auto-Data	https://www.auto-data.net/en/toyota-camry-iv-xv20-generation-1014
EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	4530	1695	1620	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/3486080/toyota_picnic_2_0_automatic.html
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Auto-Data	https://www.auto-data.net/en/volvo-s40-vs-generation-1972
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425	Auto-Data	https://www.auto-data.net/en/volvo-v40-combi-vw-generation-1967
EU-VOLVO-S70-I-SEDAN-4D-01	4720	1760	1400	Auto-Data	https://www.auto-data.net/en/volvo-s70-generation-1939
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1588355/audi_a6_2_8_fsi.html
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430	Auto-Data	https://www.auto-data.net/en/volvo-v70-i-2.0-20v-turbo-226hp-awd-9259
EU-VW-TRANSPORTER-T4-FACELIFT-BUS-SWB-LOWROOF-01	4789	1840	1940	Auto-Data	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-115hp-49355
EU-VW-TRANSPORTER-T4-FACELIFT-BUS-LWB-LOWROOF-01	5189	1840	1940	Auto-Data	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.5-115hp-49366
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496	EncyCARpedia	https://www.encycarpedia.com/volkswagen/97-passat-variant-1-8-5v-turbo-estate
EU-VW-CADDY-II-9K9-VAN-01	4207	1696	1836	IKZ vehicle specification archive	https://www.ikz.de/ikz-archiv/1999/22/9922056.php
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	Drive.Place	https://volkswagen.drive.place/passat/b5/group_sedan/323104
EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-PETROL-01	4535	1996	2070	Renault Trafic I technical dimension drawing (Transit Center scan)	https://www.transitcenter.uk/blog/1985traficwymiard.webp
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037	Transit Center Renault Trafic I specifications	https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037	Transit Center Renault Trafic I specifications	https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html
EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	4542	1905	2037	Transit Center Renault Trafic I specifications	https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html
EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-DIESEL-01	4535	1996	2067	Renault Trafic I technical dimension drawing (Transit Center scan)	https://www.transitcenter.uk/blog/1985traficwymiard.webp
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037	Transit Center Renault Trafic I specifications	https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Drom;La Centrale	https://www.drom.ru/catalog/lcv/peugeot/boxer/specs/dimensions/;https://www.lacentrale.fr/fiches-techniques-voiture-peugeot-boxer--1994-.html
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1592975/ford_focus_4-dr_1_6_ti-vct_125_titanium.html
EU-RENAULT-SUPER5-HATCHBACK-3D-01	3591	1584	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/50105/renault_5_1_4_gtl.html
EU-RENAULT-SUPER5-HATCHBACK-5D-01	3651	1584	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/2938490/renault_5_gtl_1_4_5-door.html
EU-FIAT-1500L-SEDAN-4D-01	4485	1620	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/709430/fiat_1500l.html
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-generation-1857
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390	Auto-Data	https://www.auto-data.net/en/rover-200-cabrio-xw-generation-2452
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800	Drive.Place	https://peugeot.drive.place/partner/i/group_furgon/604252
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810	Peugeot UK official Partner brochure;Drive.Place	https://xr793.com/wp-content/uploads/2022/12/2003-Peugeot-Partner-Combi-UK.pdf;https://peugeot.drive.place/partner/ii/group_furgon/604107
EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	4570	1820	1685	Auto-Data	https://www.auto-data.net/en/honda-cr-v-iv-2.0-i-vtec-155hp-awd-18010
EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	4605	1820	1685	Auto-Data	https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-2.0-i-vtec-155hp-automatic-awd-21493
EU-ASIA-MOTORS-ROCSTA-SUV-SWB-01	3585	1690	1820	Auto-Data	https://www.auto-data.net/en/asia-rocsta-1.8-i-4x4-86hp-2878
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415	Auto-Data	https://www.auto-data.net/en/volvo-850-ls-generation-1928
EU-ASIA-MOTORS-ROCSTA-SUV-LWB-01	3720	1630	1800	Auto-Data	https://www.auto-data.net/en/asia-rocsta-2.2-d-4x4-61hp-2879
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Auto-Data	https://www.auto-data.net/en/volvo-850-combi-lw-generation-1927
EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	4946	1886	1670	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2855810/pontiac_trans_sport_3_8_v6.html
EU-PONTIAC-TRANS-SPORT-II-GMT200-MPV-SWB-01	4757	1847	1712	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2859170/pontiac_trans_sport_standard.html
EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	5113	1850	1730	Auto-Data	https://www.auto-data.net/en/chevrolet-trans-sport-u-3.4-i-v6-186hp-14448
EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	4844	1877	1669	Auto-Data	https://www.auto-data.net/en/chevrolet-lumina-apv-3.1-i-122hp-14475
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7401-7500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html "https://www.transitcenter.uk/renault-trafic-i-specification-t-76.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7401-7500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7401-7500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9445 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2889 行）

