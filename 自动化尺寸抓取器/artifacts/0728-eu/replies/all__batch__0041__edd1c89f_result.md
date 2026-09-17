# 任务：all 第 4001-4100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0041__edd1c89f


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
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Nissan	Sunny	1.4	Stufenheck	Heckantrieb	Benzin	49	67	Jun 1979	Feb 1982	2024-03-01	4136
Nissan	Sunny	1.5	Stufenheck	Heckantrieb	Benzin	51	69	Jun 1979	Feb 1982	2024-03-01	4137
Honda	Accord i	1.6 L/ex	Stufenheck	Frontantrieb	Benzin	59	80	Jan 1978	Sep 1983	2024-03-01	4138
Nissan	Sunny	1.4	Kombi	Heckantrieb	Benzin	48	65	Jun 1979	Feb 1982	2024-03-01	4139
Honda	Accord i hatchback	1.6 L/ex	Schrägheck	Frontantrieb	Benzin	59	80	Jan 1979	Sep 1983	2024-03-01	4140
Nissan	Sunny	1.5	Kombi	Heckantrieb	Benzin	51	69	Jun 1979	Feb 1982	2024-03-01	4141
Nissan	Sunny	1.5	Stufenheck	Frontantrieb	Benzin	55	75	Mar 1982	Oct 1986	2024-03-01	4142
Hyundai	I30	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	66	90	Dec 2011	Dec 2016	2024-03-01	4144
Nissan	Sunny	1.7 D	Stufenheck	Frontantrieb	Diesel	40	54	Mar 1982	Oct 1986	2024-03-01	4145
Nissan	Sunny	1.5	Coupe	Frontantrieb	Benzin	55	75	Mar 1982	Oct 1986	2024-03-01	4146
Honda	Accord ii hatchback	1.6 EX	Schrägheck	Frontantrieb	Benzin	65	88	Sep 1983	Oct 1985	2024-03-01	4147
Honda	Accord ii	1.6 EX	Stufenheck	Frontantrieb	Benzin	65	88	Sep 1983	Oct 1985	2024-03-01	4148
Honda	Accord ii hatchback	1.8 EX	Schrägheck	Frontantrieb	Benzin	74	101	Sep 1983	Oct 1985	2024-03-01	4149
Nissan	Sunny	1.5	Kombi	Frontantrieb	Benzin	55	75	Mar 1982	Oct 1986	2024-03-01	4150
Honda	Accord ii	1.8 EX	Stufenheck	Frontantrieb	Benzin	74	101	Sep 1983	Oct 1985	2024-03-01	4151
Nissan	Sunny	1.7 D	Kombi	Frontantrieb	Diesel	40	54	Mar 1982	Oct 1986	2024-03-01	4152
Honda	Accord iii	1.6 L	Stufenheck	Frontantrieb	Benzin	65	88	Nov 1985	Dec 1989	2024-03-01	4153
Honda	Accord iii	2.0 EX	Stufenheck	Frontantrieb	Benzin	75	102	Nov 1985	Dec 1989	2024-03-01	4154
Nissan	Sunny	1.4 LX	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1988	Aug 1991	2024-03-01	4155
Nissan	Sunny	1.6 I	Stufenheck	Frontantrieb	Benzin	54	73	Jun 1986	Oct 1990	2024-03-01	4156
Honda	Accord iii aerodeck	2.0 EX	Kombi	Frontantrieb	Benzin	75	102	Oct 1987	Dec 1989	2024-03-01	4157
Honda	Accord iii	2.0 EX	Stufenheck	Frontantrieb	Benzin	76	103	Nov 1985	Dec 1989	2024-03-01	4158
Nissan	Sunny	1.6 I 12V	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1986	Oct 1990	2024-03-01	4159
Honda	Accord iii	2.0 EX	Stufenheck	Frontantrieb	Benzin	78	106	Nov 1985	May 1989	2024-03-01	4160
Nissan	Sunny	1.6 I 4X4	Stufenheck	Allrad	Benzin	54	73	Jun 1986	Oct 1990	2024-03-01	4161
Honda	Accord iii aerodeck	2.0 EX	Kombi	Frontantrieb	Benzin	78	106	Nov 1985	May 1989	2024-03-01	4162
Honda	Accord iii	2.0 EXI	Stufenheck	Frontantrieb	Benzin	85	116	Jan 1986	Dec 1989	2024-03-01	4163
Nissan	Sunny	1.6 I 12V	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1988	Jun 1991	2024-03-01	4164
Honda	Accord iii aerodeck	2.0 EXI	Kombi	Frontantrieb	Benzin	85	116	Oct 1987	Dec 1989	2024-03-01	4165
Nissan	Sunny	1.7 D	Stufenheck	Frontantrieb	Diesel	40	54	Jun 1986	May 1989	2024-03-01	4166
Honda	Accord iii	2.0 EXI	Stufenheck	Frontantrieb	Benzin	90	122	Nov 1985	Dec 1987	2024-03-01	4167
Honda	Accord iii aerodeck	2.0 EXI	Kombi	Frontantrieb	Benzin	90	122	Nov 1985	Dec 1987	2024-03-01	4168
Honda	Accord iii	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	98	133	Oct 1987	Dec 1989	2024-03-01	4169
Honda	Accord iii	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	101	137	Jan 1987	Dec 1987	2024-03-01	4170
Mercedes-benz	G-Klasse	G 300 CDI	Geländewagen geschlossen	Allrad	Diesel	135	184	Apr 2010	Jul 2023	2024-03-01	4171
Nissan	Sunny	1.6 I	Schrägheck	Frontantrieb	Benzin	54	73	Jun 1986	Oct 1990	2024-03-01	4172
Nissan	Sunny	1.6 GTI 16V	Schrägheck	Frontantrieb	Benzin	81	110	Jun 1987	May 1989	2024-03-01	4173
Nissan	Sunny	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	92	125	Jan 1989	Jun 1991	2024-03-01	4174
Nissan	Sunny	1.7 D	Schrägheck	Frontantrieb	Diesel	40	54	Jun 1986	Jan 1991	2024-03-01	4175
Nissan	Sunny	1.6 I	Coupe	Frontantrieb	Benzin	54	73	Jun 1986	May 1989	2024-03-01	4176
Nissan	Sunny	1.6 I 12V	Coupe	Frontantrieb	Benzin	66	90	Oct 1988	Jun 1991	2024-03-01	4177
Nissan	Sunny	1.6 GTI 16V	Coupe	Frontantrieb	Benzin	81	110	May 1987	May 1989	2024-03-01	4178
Nissan	Sunny	1.8 GTI 16V	Coupe	Frontantrieb	Benzin	92	125	Jan 1989	Jun 1991	2024-03-01	4179
Nissan	Sunny	1.6 I	Kombi	Frontantrieb	Benzin	54	73	Aug 1986	May 1989	2024-03-01	4180
Nissan	Sunny	1.6 I 4X4	Kombi	Allrad	Benzin	54	73	Jun 1986	May 1989	2024-03-01	4181
Nissan	Sunny	1.6 I 12V	Kombi	Frontantrieb	Benzin	66	90	Oct 1988	Jun 1991	2024-03-01	4182
Nissan	Sunny	1.7 D	Kombi	Frontantrieb	Diesel	40	54	Jan 1986	Jun 1991	2024-03-01	4183
Nissan	Sunny	2.0 D	Stufenheck	Frontantrieb	Diesel	55	75	Oct 1990	May 1995	2024-03-01	4184
Nissan	Sunny	1.4 I	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1990	May 1995	2024-03-01	4185
Nissan	Sunny	1.6 I	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1990	May 1995	2024-03-01	4186
Nissan	Sunny	2.0 D	Schrägheck	Frontantrieb	Diesel	55	75	Oct 1990	May 1995	2024-03-01	4187
Nissan	Sunny	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1990	May 1995	2024-03-01	4188
Nissan	Sunny	1.6 I	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1990	May 1995	2024-03-01	4189
Nissan	Sunny	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1990	May 1995	2024-03-01	4190
Nissan	Sunny	2.0 GTI 16V	Schrägheck	Frontantrieb	Benzin	105	143	Oct 1990	May 1995	2024-03-01	4191
Nissan	Sunny	2.0 D	Schrägheck	Frontantrieb	Diesel	55	75	Oct 1990	May 1995	2024-03-01	4192
Nissan	Sunny	1.6 I	Kombi	Frontantrieb	Benzin	66	90	Jun 1991	Mar 2000	2024-03-01	4193
Nissan	Sunny	1.6 I 16V 4X4	Kombi	Allrad	Benzin	75	102	Oct 1992	Mar 2000	2024-03-01	4194
Nissan	Sunny	2.0 D	Kombi	Frontantrieb	Diesel	55	75	Jun 1991	Mar 2000	2024-03-01	4195
Nissan	Stanza	1.6	Stufenheck	Frontantrieb	Benzin	60	82	Aug 1981	Dec 1985	2024-03-01	4196
Nissan	Stanza	1.6	Schrägheck	Frontantrieb	Benzin	60	82	Aug 1981	Dec 1985	2024-03-01	4197
Nissan	Stanza	1.8	Schrägheck	Frontantrieb	Benzin	65	88	Aug 1981	Dec 1985	2024-03-01	4198
Nissan	Stanza	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1981	Dec 1985	2024-03-01	4199
Nissan	Bluebird	1.8	Stufenheck	Heckantrieb	Benzin	65	88	Jan 1980	Dec 1983	2024-03-01	4200
Nissan	Bluebird	2.0 D	Stufenheck	Heckantrieb	Diesel	44	60	Jan 1980	Dec 1983	2024-03-01	4201
Nissan	Bluebird	1.8	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1980	May 1984	2024-03-01	4202
Nissan	Bluebird	1.8	Kombi	Heckantrieb	Benzin	65	88	Jan 1980	May 1984	2024-03-01	4203
Nissan	Bluebird	2.0 D	Kombi	Heckantrieb	Diesel	44	60	Jan 1980	May 1984	2024-03-01	4204
Nissan	Bluebird	2.0 I	Stufenheck	Frontantrieb	Benzin	77	105	Apr 1984	Jan 1988	2024-03-01	4205
Nissan	Bluebird	2.0 D	Stufenheck	Frontantrieb	Diesel	43	58	Apr 1984	Jan 1988	2024-03-01	4206
Nissan	Bluebird	2	Kombi	Frontantrieb	Benzin	75	102	Apr 1986	Sep 1990	2024-03-01	4207
Nissan	Bluebird	2.0 I	Kombi	Frontantrieb	Benzin	77	105	Apr 1984	Dec 1990	2024-03-01	4208
Nissan	Bluebird	2.0 D	Kombi	Frontantrieb	Diesel	43	58	Apr 1984	Jan 1988	2024-03-01	4209
Nissan	Bluebird	2.0 D	Kombi	Frontantrieb	Diesel	49	67	Mar 1986	Dec 1990	2024-03-01	4210
Nissan	Bluebird	2	Stufenheck	Frontantrieb	Benzin	75	102	Dec 1985	Dec 1987	2024-03-01	4211
Honda	Legend i	2.5 I	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1986	Dec 1987	2024-03-01	4212
Nissan	Bluebird	2.0 I	Stufenheck	Frontantrieb	Benzin	77	105	Dec 1985	Dec 1990	2024-03-01	4213
Honda	Legend i	2.7 I 24V	Stufenheck	Frontantrieb	Benzin	124	169	Jan 1988	Dec 1990	2024-03-01	4214
Honda	Legend ii	3.2 I 24V	Stufenheck	Frontantrieb	Benzin	151	205	Jan 1991	Feb 1996	2024-03-01	4215
Honda	Legend i	2.7 I 24V	Coupe	Frontantrieb	Benzin	124	169	Oct 1987	Dec 1990	2024-03-01	4216
Honda	Legend ii	3.2 I 24V	Coupe	Frontantrieb	Benzin	151	205	Jan 1991	Feb 1996	2024-03-01	4217
Honda	Prelude	1.6	Coupe	Frontantrieb	Benzin	59	80	Nov 1978	Oct 1982	2026-01-01	4218
Nissan	Bluebird	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	95	129	Feb 1989	Dec 1990	2024-03-01	4219
Honda	Prelude	1.8 EX	Coupe	Frontantrieb	Benzin	74	101	Nov 1985	Apr 1987	2026-01-01	4220
Honda	Prelude	1.8 EX	Coupe	Frontantrieb	Benzin	77	105	Nov 1983	Apr 1987	2026-01-01	4221
Nissan	Bluebird	2.0 D	Stufenheck	Frontantrieb	Diesel	49	67	Mar 1986	Dec 1990	2024-03-01	4222
Honda	Crx i	1.5 I	Coupe	Frontantrieb	Benzin	74	101	Oct 1983	Nov 1986	2024-03-01	4223
Honda	Crx i	1.6 I 16V	Coupe	Frontantrieb	Benzin	92	125	Mar 1986	Oct 1987	2024-03-01	4224
Nissan	Bluebird	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	95	129	Feb 1989	Dec 1990	2024-03-01	4225
Honda	Crx ii	1.6 I 16V	Coupe	Frontantrieb	Benzin	96	131	Oct 1987	Dec 1989	2024-03-01	4226
Honda	Crx ii	1.6 I 16V	Coupe	Frontantrieb	Benzin	91	124	Oct 1987	Feb 1992	2024-03-01	4227
Nissan	Bluebird	2	Schrägheck	Frontantrieb	Benzin	75	102	Dec 1985	Dec 1987	2024-03-01	4228
Nissan	Bluebird	2.0 I	Schrägheck	Frontantrieb	Benzin	77	105	Dec 1985	Dec 1990	2024-03-01	4229
Honda	Crx ii	1.6 I 16V Vtec	Coupe	Frontantrieb	Benzin	110	150	Oct 1989	Feb 1992	2024-03-01	4230
Nissan	Bluebird	2.0 D	Schrägheck	Frontantrieb	Diesel	49	67	Mar 1986	Dec 1990	2024-03-01	4231
Honda	Crx iii	1.6 ESI	Targa	Frontantrieb	Benzin	92	125	Mar 1992	Dec 1998	2024-03-01	4232
Honda	Crx iii	1.6 I VTI	Targa	Frontantrieb	Benzin	118	160	Mar 1992	Dec 1998	2024-03-01	4233
Honda	Prelude	2.0 EX	Coupe	Frontantrieb	Benzin	80	109	Apr 1987	Jan 1992	2026-01-01	4234
Nissan	Maxima iii	3.0 I	Stufenheck	Frontantrieb	Benzin	125	170	Oct 1988	Jun 1994	2024-03-01	4235
Honda	Prelude	2.0 I EX 16V	Coupe	Frontantrieb	Benzin	101	137	Apr 1986	Dec 1987	2026-01-01	4236


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类闭合 **33 个 Ktype 映射**，覆盖 Honda Accord I/II/III、Nissan Sunny B11、Sunny B12 Coupe/Wagon，以及 Hyundai i30 II GD。
* 本轮首次创建 **11 个尺寸组**；Hyundai i30 复用跨批次既有尺寸组。
* 暂未复用既有 `EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01`：当前欧洲 B310 资料出现与历史组三维不同的版本，需先区分市场、改款及车身代码，禁止覆盖或错误复用。B310 Fastback Estate 也存在前后期长度差异。([汽车目录][1])
* 已闭合尺寸均采用资料明确标注的车身宽度，不含外后视镜。Accord 各代和 Sunny B11/B12 的车身形式、门数与三维已按同代欧洲规格归组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：33
* PENDING 映射：67
* 当前批次引用尺寸组：12

  * 本轮首次创建：11
  * 跨批次复用：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4138	4138	Sedan	Accord I		4	EU-HONDA-ACCORD-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4140	4140	Hatchback	Accord I		3	EU-HONDA-ACCORD-I-HATCHBACK-3D-01	HIGH	第一代三门掀背外廓。	READY
4142	4142	Sedan	Sunny B11	B11	4	EU-NISSAN-SUNNY-B11-SEDAN-4D-01	HIGH	B11四门轿车外廓。	READY
4144	4144	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	复用既有GD五门尺寸组。	READY
4145	4145	Sedan	Sunny B11	B11	4	EU-NISSAN-SUNNY-B11-SEDAN-4D-01	HIGH	B11四门轿车外廓。	READY
4146	4146	Coupe	Sunny B11	B11	3	EU-NISSAN-SUNNY-B11-COUPE-3D-01	HIGH	B11三门Coupe外廓。	READY
4147	4147	Hatchback	Accord II		3	EU-HONDA-ACCORD-II-HATCHBACK-3D-01	HIGH	第二代后期三门掀背外廓。	READY
4148	4148	Sedan	Accord II		4	EU-HONDA-ACCORD-II-SEDAN-4D-01	HIGH	第二代后期四门轿车外廓。	READY
4149	4149	Hatchback	Accord II		3	EU-HONDA-ACCORD-II-HATCHBACK-3D-01	HIGH	第二代后期三门掀背外廓。	READY
4150	4150	Wagon	Sunny B11	B11	5	EU-NISSAN-SUNNY-B11-WAGON-5D-01	HIGH	B11五门Traveller外廓。	READY
4151	4151	Sedan	Accord II		4	EU-HONDA-ACCORD-II-SEDAN-4D-01	HIGH	第二代后期四门轿车外廓。	READY
4152	4152	Wagon	Sunny B11	B11	5	EU-NISSAN-SUNNY-B11-WAGON-5D-01	HIGH	B11五门Traveller外廓。	READY
4153	4153	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4154	4154	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4157	4157	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4158	4158	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4160	4160	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4162	4162	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4163	4163	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4165	4165	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4167	4167	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4168	4168	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4169	4169	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4170	4170	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4176	4176	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4177	4177	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4178	4178	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4179	4179	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4180	4180	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4182	4182	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4183	4183	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4193	4193	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12 Estate延续生产外廓。	READY
4195	4195	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12 Estate延续生产外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-ACCORD-I-SEDAN-4D-01	4365	1620	1355	Automobile-Catalog - 1979 Honda Accord 4-Door Sedan	https://www.automobile-catalog.com/car/1979/1086770/honda_accord_sedan_hondamatic.html
EU-HONDA-ACCORD-I-HATCHBACK-3D-01	4125	1620	1335	Automobile-Catalog - 1980 Honda Accord Hatchback EX Europe	https://www.automobile-catalog.com/car/1980/2191355/honda_accord_coupe_ex.html
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385	Automobile-Catalog - Nissan Sunny B11 Sedan Europe	https://www.automobile-catalog.com/car/1985/24080/nissan_sunny_1_3.html
EU-NISSAN-SUNNY-B11-COUPE-3D-01	4135	1620	1355	Automobile-Catalog - 1983 Nissan Sunny 1.5 GL Coupe	https://www.automobile-catalog.com/car/1983/2210405/nissan_sunny_1_5_gl_coupe.html
EU-NISSAN-SUNNY-B11-WAGON-5D-01	4255	1620	1360	Automobile-Catalog - 1983 Nissan Sunny 1.5 GL Traveller	https://www.automobile-catalog.com/car/1983/2210390/nissan_sunny_1_5_gl_traveller.html
EU-HONDA-ACCORD-II-HATCHBACK-3D-01	4255	1665	1355	Automobile-Catalog - 1983 Honda Accord Hatchback 1.6 EX Europe	https://www.automobile-catalog.com/car/1983/1091465/honda_accord_coupe_1_6_ex.html
EU-HONDA-ACCORD-II-SEDAN-4D-01	4455	1665	1375	Automobile-Catalog - 1984 Honda Accord Limousine 1.6 EX Europe	https://www.automobile-catalog.com/car/1984/1091450/honda_accord_limousine_1_6_ex_hondamatic.html
EU-HONDA-ACCORD-III-SEDAN-4D-01	4535	1695	1355	Automobile-Catalog - 1986 Honda Accord EX 2.0 Europe	https://www.automobile-catalog.com/car/1986/1097270/honda_accord_ex_2_0.html
EU-HONDA-ACCORD-III-AERODECK-3D-01	4335	1695	1335	Automobile-Catalog - 1986 Honda Accord Aerodeck EX 2.0 Europe	https://www.automobile-catalog.com/car/1986/1097435/honda_accord_aerodeck_ex_2_0.html
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325	Automobile-Catalog - 1988 Nissan Sunny 1.6 GSX Coupe Europe	https://www.automobile-catalog.com/car/1988/2222465/nissan_sunny_1_6_gsx_coupe_automatic.html
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385	Automobile-Catalog - 1988 Nissan Sunny 1.6 LX Estate Europe	https://www.automobile-catalog.com/car/1988/2222660/nissan_sunny_1_6_lx_estate.html
```

## 下一步优先处理

1. 区分 Sunny B310 Sedan/Fastback Estate 的前期、改款后及市场尺寸，确认 Ktype `4136`、`4137`、`4139`、`4141` 是否需要派生。
2. 处理 Sunny N13：重点拆分前驱/四驱高度、前后期宽度，以及 Hatchback 的三门/五门边界。
3. 核对 Sunny B12 四驱 Estate `4181`、`4194`，避免错误复用前驱 Estate 高度。
4. 随后批量闭合 Sunny N14、Stanza T11、Bluebird 910/U11、Honda Legend、Prelude、CRX、Maxima J30 和 G-Klasse W463。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/2109665/datsun_sunny_1_4_saloon.html?utm_source=chatgpt.com "1980 Datsun Sunny 1.4 Saloon Specs Review (46.5 kW / 63 PS / 62 hp) (since April 1980 for Europe U.K.)"
[2]: https://www.automobile-catalog.com/car/1980/2191355/honda_accord_coupe_ex.html?utm_source=chatgpt.com "1980 Honda Accord Hatchback EX Specs Review (59 kW / 80 PS / 79 hp) (since mid-year 1980 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 新增闭合 **19 个 Ktype 映射**，本轮集中处理了 **Mercedes-Benz G-Klasse W463、Honda Legend I/II、Honda Prelude I/II/III、Honda CRX I/II/III、Nissan Maxima III**。
* 本轮首次创建 **12 个 DIMENSION_GROUP**。
* 继续采用缓存优先模式：已闭合车型后续只建立关联，不重复抓取或重复输出来源说明。

当前批次进度

* READY 映射：52
* PENDING 映射：48
* 已确认尺寸组：24
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4171	4171	SUV	G-Klasse W463		5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	HIGH	W463五门封闭式越野车外廓。	READY
4212	4212	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4214	4214	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4215	4215	Sedan	Legend II		4	EU-HONDA-LEGEND-II-SEDAN-4D-01	HIGH	第二代四门轿车外廓。	READY
4216	4216	Coupe	Legend I		2	EU-HONDA-LEGEND-I-COUPE-2D-01	HIGH	第一代双门Coupe外廓。	READY
4217	4217	Coupe	Legend II		2	EU-HONDA-LEGEND-II-COUPE-2D-01	HIGH	第二代双门Coupe外廓。	READY
4218	4218	Coupe	Prelude I		2	EU-HONDA-PRELUDE-I-COUPE-2D-01	HIGH	第一代双门Coupe外廓。	READY
4220	4220	Coupe	Prelude II		2	EU-HONDA-PRELUDE-II-COUPE-2D-01	HIGH	第二代双门Coupe外廓。	READY
4221	4221	Coupe	Prelude II		2	EU-HONDA-PRELUDE-II-COUPE-2D-01	HIGH	第二代双门Coupe外廓。	READY
4223	4223	Coupe	CRX I		2	EU-HONDA-CRX-I-COUPE-2D-01	HIGH	第一代双门CRX外廓。	READY
4224	4224	Coupe	CRX I		2	EU-HONDA-CRX-I-COUPE-2D-01	HIGH	第一代双门CRX外廓。	READY
4226	4226	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4227	4227	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4230	4230	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4232	4232	Convertible	CRX III		2	EU-HONDA-CRX-III-CONVERTIBLE-2D-01	HIGH	del Sol targa开放式车身外廓。	READY
4233	4233	Convertible	CRX III		2	EU-HONDA-CRX-III-CONVERTIBLE-2D-01	HIGH	del Sol targa开放式车身外廓。	READY
4234	4234	Coupe	Prelude III		2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	第三代双门Coupe外廓。	READY
4235	4235	Sedan	Maxima III		4	EU-NISSAN-MAXIMA-III-SEDAN-4D-01	HIGH	第三代四门轿车外廓。	READY
4236	4236	Coupe	Prelude III		2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	第三代双门Coupe外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951	Automobile-Catalog - Mercedes-Benz G 300 CDI Station Wagon LWB	https://www.automobile-catalog.com/car/2012/2567370/mercedes-benz_g_300_cdi_station_wagon_lwb.html
EU-HONDA-LEGEND-I-SEDAN-4D-01	4775	1745	1375	Automobile-Catalog - Honda Legend Sedan 2.5i	https://www.automobile-catalog.com/car/1986/1089455/honda_legend_2_5i.html
EU-HONDA-LEGEND-I-COUPE-2D-01	4770	1745	1320	Automobile-Catalog - Honda Legend Coupe 2.7i 24V	https://www.automobile-catalog.com/car/1988/1089665/honda_legend_coupe_2_7i_24v.html
EU-HONDA-LEGEND-II-SEDAN-4D-01	4955	1810	1405	Automobile-Catalog - Honda Legend Sedan 3.2i 24V	https://www.automobile-catalog.com/car/1991/1092385/honda_legend_3_2i_24v.html
EU-HONDA-LEGEND-II-COUPE-2D-01	4945	1810	1375	Automobile-Catalog - Honda Legend Coupe 3.2i 24V	https://www.automobile-catalog.com/car/1991/1092470/honda_legend_coupe_3_2i_24v.html
EU-HONDA-PRELUDE-I-COUPE-2D-01	4090	1635	1290	Automobile-Catalog - Honda Prelude 1.6	https://www.automobile-catalog.com/car/1979/1086765/honda_prelude_1_6.html
EU-HONDA-PRELUDE-II-COUPE-2D-01	4460	1690	1295	Automobile-Catalog - Honda Prelude 1.8 EX	https://www.automobile-catalog.com/car/1984/1091455/honda_prelude_1_8_ex.html
EU-HONDA-CRX-I-COUPE-2D-01	3675	1625	1270	Automobile-Catalog - Honda CR-X 1.5i	https://www.automobile-catalog.com/car/1984/1091625/honda_cr-x_1_5i.html
EU-HONDA-CRX-II-COUPE-2D-01	3800	1675	1270	Automobile-Catalog - Honda CR-X 1.6i-16V	https://www.automobile-catalog.com/car/1988/1098895/honda_cr-x_1_6i-16v.html
EU-HONDA-CRX-III-CONVERTIBLE-2D-01	3995	1695	1255	Automobile-Catalog - Honda CR-X del Sol ESi	https://www.automobile-catalog.com/car/1992/1102565/honda_cr-x_del_sol_esi.html
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295	Automobile-Catalog - Honda Prelude 2.0 EX	https://www.automobile-catalog.com/car/1988/1099040/honda_prelude_2_0_ex.html
EU-NISSAN-MAXIMA-III-SEDAN-4D-01	4780	1760	1395	Automobile-Catalog - Nissan Maxima 3.0i V6	https://www.automobile-catalog.com/car/1989/2227310/nissan_maxima_3_0i_v6.html
```

下一步优先处理

1. 继续优先消除 **Nissan Sunny B310 / N13 / N14** 的 PENDING，重点确认 B310 前后期与 N13 四驱/非四驱是否需独立尺寸组。
2. 批量闭合 **Nissan Stanza、Bluebird 910/U11、Sunny N14 hatch/sedan/wagon**。
3. 如上述完成后，再检查是否已达到 `PENDING=0`，若达到则下一条直接输出两张最终完整 TSV、两个指定 sandbox 下载链接并结束为 `COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Nissan Sunny N14 四门轿车与 Nissan Stanza T11 轿车/掀背车身簇。
* Stanza T11 掀背 Ktype 按三门、五门两个物理外廓拆分，不再保留无后缀基础行。
* 本轮新增 7 个 READY Ktype，首次创建 4 个尺寸组。N14 轿车及 Stanza T11 三种车身的尺寸边界已闭合。([汽车目录][1])

## 当前批次进度

* READY Ktype：59
* PENDING Ktype：41
* 已确认尺寸组：28
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4184	4184	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4185	4185	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4186	4186	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4196	4196	Sedan	Stanza T11	T11	4	EU-NISSAN-STANZA-T11-SEDAN-4D-01	HIGH	T11四门轿车外廓。	READY
4197_3dr	4197	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4197_5dr	4197	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
4198_3dr	4198	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4198_5dr	4198	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
4199_3dr	4199	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4199_5dr	4199	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395	Automobile-Catalog - 1991 Nissan Sunny 2.0 LX Diesel 4d	https://www.automobile-catalog.com/car/1991/2247500/nissan_sunny_2_0_lx_diesel_4d.html
EU-NISSAN-STANZA-T11-SEDAN-4D-01	4280	1665	1385	Automobile-Catalog - Nissan Stanza T11 Export Sedan	https://www.automobile-catalog.com/make/nissan/stanza_2gen_t11/stanza_t11_export_sedan/1983.html
EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	4225	1665	1370	Automobile-Catalog - 1982 Nissan Stanza 1.8 3d	https://www.automobile-catalog.com/car/1982/2215220/nissan_stanza_1_8_3d.html
EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	4280	1665	1390	Automobile-Catalog - 1982 Nissan Stanza 1.8 5d	https://www.automobile-catalog.com/car/1982/2215280/nissan_stanza_1_8_5d_automatic.html
```

## 下一步优先处理

1. 闭合 Sunny N14 掀背 Ktype `4187–4192` 的三门/五门边界。
2. 处理 Sunny B310 `4136、4137、4139、4141`，重点区分二门/四门轿车及前后期旅行车。
3. 批量闭合 Sunny N13 轿车、掀背及四驱分支。
4. 随后处理 Bluebird 910、U11 与 T12/T72 车身簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/2248025/nissan_sunny_2_0_lx_diesel_4d.html?utm_source=chatgpt.com "1995 Nissan Sunny 2.0 LX Diesel 4d Specs Review (55 kW / 75 ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Sunny N14 剩余 6 个掀背 Ktype：`4187–4189`、`4191` 对应五门 Liftback；`4190`、`4192` 对应三门 Hatchback。三门和五门外廓分别建组。([AUTODOC][1])
* N14 三门尺寸闭合为 `3975×1690×1395 mm`，五门尺寸闭合为 `4145×1690×1395 mm`，宽度均为不含后视镜口径。([汽车目录][2])
* 本轮新增 6 个 READY Ktype、2 个 DIMENSION_GROUP。

## 当前批次进度

* READY Ktype：65
* PENDING Ktype：35
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4187	4187	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4188	4188	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4189	4189	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4190	4190	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	N14三门掀背外廓。	READY
4191	4191	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门GTI掀背外廓。	READY
4192	4192	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	N14三门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395	Automobile-Catalog - 1991 Nissan Sunny 2.0 GTI 5d	https://www.automobile-catalog.com/car/1991/2247575/nissan_sunny_2_0_gti_5d.html
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395	Automobile-Catalog - 1992 Nissan Sunny 1.4 LX 3d	https://www.automobile-catalog.com/car/1992/2247695/nissan_sunny_1_4_lx_3d.html
```

## 下一步优先处理

1. 闭合 Sunny N13 四门轿车的前期、后期及四驱分支。
2. 拆分 Sunny N13 掀背的三门、五门及 GTI 门数边界。
3. 处理 Sunny B12 四驱 Estate 与 B310 前后期轿车/旅行车。
4. 最后批量闭合 Bluebird 910、U11、T12/T72 剩余 Ktype。

推进信号：CONTINUE

[1]: https://www.auto-doc.be/pieces-detachees/eclairage-des-instruments-et-des-commandes-10608/nissan/sunny/sunny-iii-liftback-n14/4187-2-0-d?utm_source=chatgpt.com "Eclairage des instruments Nissan Sunny III Liftback (N14) 2.0 D ..."
[2]: https://www.automobile-catalog.com/car/1992/2247695/nissan_sunny_1_4_lx_3d.html?utm_source=chatgpt.com "1992 Nissan Sunny 1.4 LX 3d Specs Review (60 kW / 82 PS / 80 hp) (up to December 1992 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Nissan Bluebird 剩余 **19 个输入 Ktype**，新增 **31 条 READY 映射行**。
* Bluebird 910 的轿车和旅行车均确认存在前后期外廓差异，跨期 Ktype 已拆分为 `prefl/facelift`。轿车由 `4350×1655×1400` 变为 `4395×1655×1400`，旅行车由 `4400×1655×1400` 变为 `4445×1655×1405`。([汽车目录][1])
* Bluebird U11 轿车复用同一外廓；旅行车后期由 `4405×1690×1455` 变为 `4445×1690×1475`，跨期 Ktype 已拆分。([汽车目录][2])
* Bluebird T12/T72 的轿车和五门掀背均按改款前后拆分：轿车 `4405→4460 mm`，掀背 `4365→4420 mm`；宽度和高度不变。([汽车目录][3])

## 当前批次进度

* READY 输入 Ktype：84 / 100
* READY 映射行：99
* PENDING 输入 Ktype：16
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4200_prefl	4200	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4200_facelift	4200	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4201_prefl	4201	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4201_facelift	4201	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4202_prefl	4202	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4202_facelift	4202	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4203_prefl	4203	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	HIGH	910旅行车改款前物理外廓。	READY
4203_facelift	4203	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	HIGH	910旅行车改款后物理外廓。	READY
4204_prefl	4204	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	HIGH	910旅行车改款前物理外廓。	READY
4204_facelift	4204	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	HIGH	910旅行车改款后物理外廓。	READY
4205	4205	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门轿车外廓。	READY
4206	4206	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门轿车外廓。	READY
4207_prefl	4207	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4207_facelift	4207	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4208_prefl	4208	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4208_facelift	4208	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4209	4209	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4210_prefl	4210	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4210_facelift	4210	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4211	4211	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4213_prefl	4213	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4213_facelift	4213	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4219	4219	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4222_prefl	4222	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4222_facelift	4222	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4225	4225	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
4228	4228	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4229_prefl	4229	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4229_facelift	4229	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
4231_prefl	4231	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4231_facelift	4231	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	4350	1655	1400	Automobile-Catalog - 1981 Datsun Bluebird 1.8 GL	https://www.automobile-catalog.com/car/1981/45245/datsun_bluebird_1_8.html
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	4395	1655	1400	Automobile-Catalog - 1983 Datsun Bluebird 1.8 GL	https://www.automobile-catalog.com/car/1983/2119295/datsun_bluebird_1_8_gl.html
EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	4400	1655	1400	Automobile-Catalog - 1980 Datsun Bluebird 1.8 GL Wagon	https://www.automobile-catalog.com/car/1980/2119145/datsun_bluebird_1_8_gl_wagon.html
EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	4445	1655	1405	Automobile-Catalog - 1982 Datsun Bluebird 1.8 GL Wagon	https://www.automobile-catalog.com/car/1982/2119340/datsun_bluebird_1_8_gl_wagon.html
EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	4360	1690	1400	Automobile-Catalog - 1985 Nissan Bluebird 2.0 SGL	https://www.automobile-catalog.com/car/1985/2240120/nissan_bluebird_2_0_sgl.html
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	4405	1690	1455	Automobile-Catalog - 1985 Nissan Bluebird 2.0 GL Estate	https://www.automobile-catalog.com/car/1985/2240165/nissan_bluebird_2_0_gl_estate.html
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	4445	1690	1475	Automobile-Catalog - 1988 Nissan Bluebird 2.0 GL Estate	https://www.automobile-catalog.com/car/1988/2236745/nissan_bluebird_2_0_gl_estate.html
EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	4405	1690	1395	Automobile-Catalog - 1987 Nissan Bluebird 2.0 SGX 4-door	https://www.automobile-catalog.com/car/1987/2237210/nissan_bluebird_2_0_sgx_4-d.html
EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	4460	1690	1395	Automobile-Catalog - 1989 Nissan Bluebird 2.0i Executive 4-door	https://www.automobile-catalog.com/car/1989/2236865/nissan_bluebird_2_0_gsx_4-d.html
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	4365	1690	1395	Automobile-Catalog - 1987 Nissan Bluebird 2.0 SGX 5-door	https://www.automobile-catalog.com/car/1987/2237240/nissan_bluebird_2_0_sgx_5-d.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	4420	1690	1395	Automobile-Catalog - 1989 Nissan Bluebird 2.0i Executive 5-door	https://www.automobile-catalog.com/car/1989/2236895/nissan_bluebird_2_0_gsx_5-d.html
```

## 下一步优先处理

1. 闭合 Sunny N13 的四门轿车、三门/五门掀背及四驱分支。
2. 闭合 Sunny B12 四驱旅行车 `4181`、`4194`。
3. 最后处理 Sunny B310 `4136`、`4137`、`4139`、`4141` 的欧洲市场前后期尺寸差异。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/45245/datsun_bluebird_1_8.html?utm_source=chatgpt.com "1981 Datsun Bluebird 1.8 GL Specs Review (65 kW / 88 PS / 87 hp) (for Europe export)"
[2]: https://www.automobile-catalog.com/car/1984/2240120/nissan_bluebird_2_0_sgl.html?utm_source=chatgpt.com "1984 Nissan Bluebird 2.0 SGL Specs Review (77 kW / 105 PS / 103 hp) (since May 1984 for Europe )"
[3]: https://www.automobile-catalog.com/car/1987/2237210/nissan_bluebird_2_0_sgx_4-d.html?utm_source=chatgpt.com "1987 Nissan Bluebird 2.0 SGX 4-d Specs Review (77 kW / 105 PS / 103 hp) (up to mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 14 个输入 Ktype。B310 轿车 `4136`、`4137` 直接复用跨批次既有官方尺寸组，不重复创建或输出尺寸组。Nissan 官方 Heritage Collection 对 HB310 记录为 `3995×1590×1370 mm`。([日产汽车公司全球网站][1])
* Sunny B12 四驱旅行车确认高度为 `1400 mm`，高于既有前驱旅行车组，已独立建组；Sunny Y10 四驱旅行车闭合为 `4175×1665×1525 mm`。([汽车目录][2])
* Sunny N13 已按四门轿车、四驱轿车、三门/五门掀背及不同外廓宽度分别建立稳定尺寸组。([汽车目录][3])

## 当前批次进度

* READY 输入 Ktype：98 / 100
* READY 映射行：117
* PENDING 输入 Ktype：2
* 当前批次已引用尺寸组：51
* 剩余 PENDING：`4139`、`4141`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4136	4136	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	HBL310轿车物理边界；资料未按门数拆分。	READY
4137	4137	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	HBL310轿车物理边界；资料未按门数拆分。	READY
4155	4155	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门轿车标准外廓。	READY
4156	4156	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门轿车标准外廓。	READY
4159_3dr	4159	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门掀背物理分支。	READY
4159_5dr	4159	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门掀背物理分支。	READY
4161	4161	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	HIGH	N13四驱四门轿车外廓。	READY
4164	4164	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-02	HIGH	N13后期四门轿车外廓。	READY
4166	4166	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门柴油轿车标准外廓。	READY
4172_3dr	4172	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门掀背物理分支。	READY
4172_5dr	4172	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门掀背物理分支。	READY
4173	4173	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	HIGH	N13前期三门GTI掀背外廓。	READY
4174_3dr	4174	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	MEDIUM	N13后期三门GTI掀背物理分支。	READY
4174_5dr	4174	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	MEDIUM	N13后期五门GTI掀背物理分支。	READY
4175_3dr	4175	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门柴油掀背物理分支。	READY
4175_5dr	4175	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门柴油掀背物理分支。	READY
4181	4181	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	HIGH	B12五门四驱旅行车外廓。	READY
4194	4194	Wagon	Sunny Y10	Y10	5	EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	HIGH	Y10五门四驱旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX 4d catalyst	https://www.automobile-catalog.com/car/1987/2219330/nissan_sunny_1_6_slx_4d_cat.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-02	4215	1645	1380	Automobile-Catalog - 1989 Nissan Sunny SLX 1.6 4d catalyst	https://www.automobile-catalog.com/car/1989/2219450/nissan_sunny_slx_1_6_4d_automatic_cat.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4215	1640	1395	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX 4WD catalyst	https://www.automobile-catalog.com/car/1987/2219345/nissan_sunny_1_6_slx_4wd_cat.html
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380	Automobile-Catalog - 1988 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1988/2219870/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380	Automobile-Catalog - 1987 Nissan Sunny 1.6 SGX	https://www.automobile-catalog.com/car/1987/2219075/nissan_sunny_1_6_sgx.html
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	4030	1645	1380	Automobile-Catalog - 1989 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1989/2219420/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	4030	1645	1380	Automobile-Catalog - 1989 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1989/2219420/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX Traveller 4WD catalyst	https://www.automobile-catalog.com/car/1987/2222630/nissan_sunny_1_6_slx_traveller_4wd_cat.html
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525	Automobile-Catalog - 1994 Nissan Sunny 1.6i SLX Wagon 4x4	https://www.automobile-catalog.com/car/1994/2248430/nissan_sunny_1_6i_slx_wagon_4x4.html
```

## 下一步优先处理

1. 仅处理 B310/HBL310 旅行车 Ktype `4139`、`4141`。
2. 确认欧洲 140Y/150Y Traveller 对应的统一三维，排除不同市场保险杠造成的长度差异。
3. 两行闭合并达到 `PENDING=0` 后，下一轮直接执行机械收尾，输出两张最终完整 TSV、两个指定 sandbox 下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Sunny_Sedan_1400SGL.html?utm_source=chatgpt.com "Nissan | Heritage Collection | DATSUN Sunny Sedan 1400SGL"
[2]: https://www.automobile-catalog.com/car/1987/2222630/nissan_sunny_1_6_slx_traveller_4wd_cat.html?utm_source=chatgpt.com "1987 Nissan Sunny 1.6 SLX Traveller 4WD catalyst Specs Review (54 kW / 73 PS / 72 hp) (since mid-year 1987 for Europe )"
[3]: https://www.automobile-catalog.com/car/1987/62420/nissan_sunny_4wd.html?utm_source=chatgpt.com "1987 Nissan Sunny 1.6 SLX 4WD Specs Review (62 kW / 84 PS / 83 hp) (since mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4001-4100_ktype_dimension_mapping_final.tsv
- all_4001-4100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合最后两个 PENDING：`4139`、`4141` 均关联 Sunny B310 五门 Fastback Estate 尺寸组，三维为 `4050×1590×1390 mm`，宽度为不含后视镜口径。([汽车目录][1])
* 机械收尾时修正 Prelude II 缓存冲突：1.8 车型尺寸组修正为 `4295×1690×1295 mm`；`4236` 改为 Prelude II 2.0i-16 后期外廓，并建立 `4375×1690×1295 mm` 的独立尺寸组。([汽车目录][2])
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100 / 100 READY
* 最终映射行：119
* PENDING：0
* 最终尺寸组：53
* `id` 与 `DIMENSION_GROUP_ID` 均唯一。
* 所有映射引用均已闭合，无孤立尺寸组。
* 两张表表头、字段数、正整数三维、来源与 URL 已通过机械检查。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4136	4136	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	HBL310轿车物理边界；资料未按门数拆分。	READY
4137	4137	Sedan	Sunny B310	HBL310		EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	MEDIUM	HBL310轿车物理边界；资料未按门数拆分。	READY
4138	4138	Sedan	Accord I		4	EU-HONDA-ACCORD-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4139	4139	Wagon	Sunny B310		5	EU-NISSAN-SUNNY-B310-WAGON-5D-01	HIGH	B310五门Fastback Estate外廓。	READY
4140	4140	Hatchback	Accord I		3	EU-HONDA-ACCORD-I-HATCHBACK-3D-01	HIGH	第一代三门掀背外廓。	READY
4141	4141	Wagon	Sunny B310		5	EU-NISSAN-SUNNY-B310-WAGON-5D-01	HIGH	B310五门Fastback Estate外廓。	READY
4142	4142	Sedan	Sunny B11	B11	4	EU-NISSAN-SUNNY-B11-SEDAN-4D-01	HIGH	B11四门轿车外廓。	READY
4144	4144	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
4145	4145	Sedan	Sunny B11	B11	4	EU-NISSAN-SUNNY-B11-SEDAN-4D-01	HIGH	B11四门轿车外廓。	READY
4146	4146	Coupe	Sunny B11	B11	3	EU-NISSAN-SUNNY-B11-COUPE-3D-01	HIGH	B11三门Coupe外廓。	READY
4147	4147	Hatchback	Accord II		3	EU-HONDA-ACCORD-II-HATCHBACK-3D-01	HIGH	第二代后期三门掀背外廓。	READY
4148	4148	Sedan	Accord II		4	EU-HONDA-ACCORD-II-SEDAN-4D-01	HIGH	第二代后期四门轿车外廓。	READY
4149	4149	Hatchback	Accord II		3	EU-HONDA-ACCORD-II-HATCHBACK-3D-01	HIGH	第二代后期三门掀背外廓。	READY
4150	4150	Wagon	Sunny B11	B11	5	EU-NISSAN-SUNNY-B11-WAGON-5D-01	HIGH	B11五门Traveller外廓。	READY
4151	4151	Sedan	Accord II		4	EU-HONDA-ACCORD-II-SEDAN-4D-01	HIGH	第二代后期四门轿车外廓。	READY
4152	4152	Wagon	Sunny B11	B11	5	EU-NISSAN-SUNNY-B11-WAGON-5D-01	HIGH	B11五门Traveller外廓。	READY
4153	4153	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4154	4154	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4155	4155	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门轿车标准外廓。	READY
4156	4156	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门轿车标准外廓。	READY
4157	4157	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4158	4158	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4159_3dr	4159	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门掀背物理分支。	READY
4159_5dr	4159	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门掀背物理分支。	READY
4160	4160	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4161	4161	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	HIGH	N13四驱四门轿车外廓。	READY
4162	4162	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4163	4163	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4164	4164	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-02	HIGH	N13后期四门轿车外廓。	READY
4165	4165	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4166	4166	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH	N13四门柴油轿车标准外廓。	READY
4167	4167	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4168	4168	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-3D-01	HIGH	Aerodeck三门车身外廓。	READY
4169	4169	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4170	4170	Sedan	Accord III		4	EU-HONDA-ACCORD-III-SEDAN-4D-01	HIGH	第三代欧洲四门轿车外廓。	READY
4171	4171	SUV	G-Klasse W463		5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	HIGH	W463五门封闭式越野车外廓。	READY
4172_3dr	4172	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门掀背物理分支。	READY
4172_5dr	4172	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门掀背物理分支。	READY
4173	4173	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	HIGH	N13前期三门GTI掀背外廓。	READY
4174_3dr	4174	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	MEDIUM	N13后期三门GTI掀背物理分支。	READY
4174_5dr	4174	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	MEDIUM	N13后期五门GTI掀背物理分支。	READY
4175_3dr	4175	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	N13三门柴油掀背物理分支。	READY
4175_5dr	4175	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	N13五门柴油掀背物理分支。	READY
4176	4176	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4177	4177	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4178	4178	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4179	4179	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH	B12三门Coupe外廓。	READY
4180	4180	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4181	4181	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	HIGH	B12五门四驱旅行车外廓。	READY
4182	4182	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4183	4183	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12五门Estate外廓。	READY
4184	4184	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4185	4185	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4186	4186	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH	N14四门轿车外廓。	READY
4187	4187	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4188	4188	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4189	4189	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门掀背外廓。	READY
4190	4190	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	N14三门掀背外廓。	READY
4191	4191	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	N14五门GTI掀背外廓。	READY
4192	4192	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	N14三门掀背外廓。	READY
4193	4193	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12 Estate延续生产外廓。	READY
4194	4194	Wagon	Sunny Y10	Y10	5	EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	HIGH	Y10五门四驱旅行车外廓。	READY
4195	4195	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH	B12 Estate延续生产外廓。	READY
4196	4196	Sedan	Stanza T11	T11	4	EU-NISSAN-STANZA-T11-SEDAN-4D-01	HIGH	T11四门轿车外廓。	READY
4197_3dr	4197	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4197_5dr	4197	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
4198_3dr	4198	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4198_5dr	4198	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
4199_3dr	4199	Hatchback	Stanza T11	T11	3	EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	MEDIUM	T11三门掀背物理分支。	READY
4199_5dr	4199	Hatchback	Stanza T11	T11	5	EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	MEDIUM	T11五门掀背物理分支。	READY
4200_prefl	4200	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4200_facelift	4200	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4201_prefl	4201	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4201_facelift	4201	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4202_prefl	4202	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	HIGH	910轿车改款前物理外廓。	READY
4202_facelift	4202	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910轿车改款后物理外廓。	READY
4203_prefl	4203	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	HIGH	910旅行车改款前物理外廓。	READY
4203_facelift	4203	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	HIGH	910旅行车改款后物理外廓。	READY
4204_prefl	4204	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	HIGH	910旅行车改款前物理外廓。	READY
4204_facelift	4204	Wagon	Bluebird 910	910	5	EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	HIGH	910旅行车改款后物理外廓。	READY
4205	4205	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门轿车外廓。	READY
4206	4206	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门轿车外廓。	READY
4207_prefl	4207	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4207_facelift	4207	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4208_prefl	4208	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4208_facelift	4208	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4209	4209	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4210_prefl	4210	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	HIGH	U11旅行车前期物理外廓。	READY
4210_facelift	4210	Wagon	Bluebird U11	U11	5	EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	HIGH	U11旅行车后期物理外廓。	READY
4211	4211	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4212	4212	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4213_prefl	4213	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4213_facelift	4213	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4214	4214	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
4215	4215	Sedan	Legend II		4	EU-HONDA-LEGEND-II-SEDAN-4D-01	HIGH	第二代四门轿车外廓。	READY
4216	4216	Coupe	Legend I		2	EU-HONDA-LEGEND-I-COUPE-2D-01	HIGH	第一代双门Coupe外廓。	READY
4217	4217	Coupe	Legend II		2	EU-HONDA-LEGEND-II-COUPE-2D-01	HIGH	第二代双门Coupe外廓。	READY
4218	4218	Coupe	Prelude I		2	EU-HONDA-PRELUDE-I-COUPE-2D-01	HIGH	第一代双门Coupe外廓。	READY
4219	4219	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4220	4220	Coupe	Prelude II		2	EU-HONDA-PRELUDE-II-COUPE-2D-01	HIGH	第二代1.8双门Coupe外廓。	READY
4221	4221	Coupe	Prelude II		2	EU-HONDA-PRELUDE-II-COUPE-2D-01	HIGH	第二代1.8双门Coupe外廓。	READY
4222_prefl	4222	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12改款前四门轿车外廓。	READY
4222_facelift	4222	Sedan	Bluebird T72	T72	4	EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	HIGH	T72改款后四门轿车外廓。	READY
4223	4223	Coupe	CRX I		2	EU-HONDA-CRX-I-COUPE-2D-01	HIGH	第一代双门CRX外廓。	READY
4224	4224	Coupe	CRX I		2	EU-HONDA-CRX-I-COUPE-2D-01	HIGH	第一代双门CRX外廓。	READY
4225	4225	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
4226	4226	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4227	4227	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4228	4228	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4229_prefl	4229	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4229_facelift	4229	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
4230	4230	Coupe	CRX II		2	EU-HONDA-CRX-II-COUPE-2D-01	HIGH	第二代双门CRX外廓。	READY
4231_prefl	4231	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	HIGH	T12改款前五门掀背外廓。	READY
4231_facelift	4231	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	HIGH	T72改款后五门掀背外廓。	READY
4232	4232	Convertible	CRX III		2	EU-HONDA-CRX-III-CONVERTIBLE-2D-01	HIGH	del Sol targa开放式车身外廓。	READY
4233	4233	Convertible	CRX III		2	EU-HONDA-CRX-III-CONVERTIBLE-2D-01	HIGH	del Sol targa开放式车身外廓。	READY
4234	4234	Coupe	Prelude III		2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	第三代双门Coupe外廓。	READY
4235	4235	Sedan	Maxima III		4	EU-NISSAN-MAXIMA-III-SEDAN-4D-01	HIGH	第三代四门轿车外廓。	READY
4236	4236	Coupe	Prelude II		2	EU-HONDA-PRELUDE-II-COUPE-2D-FACELIFT-01	HIGH	第二代2.0i-16后期双门Coupe外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4001-4100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370	Nissan Heritage Collection - Datsun Sunny Sedan 1400SGL	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/DATSUN_Sunny_Sedan_1400SGL.html
EU-HONDA-ACCORD-I-SEDAN-4D-01	4365	1620	1355	Automobile-Catalog - 1979 Honda Accord 4-Door Sedan	https://www.automobile-catalog.com/car/1979/1086770/honda_accord_sedan_hondamatic.html
EU-NISSAN-SUNNY-B310-WAGON-5D-01	4050	1590	1390	Automobile-Catalog - 1981 Datsun Sunny 1500 Station Wagon L	https://www.automobile-catalog.com/car/1981/2109620/datsun_sunny_1500_station_wagon_l.html
EU-HONDA-ACCORD-I-HATCHBACK-3D-01	4125	1620	1335	Automobile-Catalog - 1980 Honda Accord Hatchback EX Europe	https://www.automobile-catalog.com/car/1980/2191355/honda_accord_coupe_ex.html
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385	Automobile-Catalog - Nissan Sunny B11 Sedan Europe	https://www.automobile-catalog.com/car/1985/24080/nissan_sunny_1_3.html
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470	Automobile-Catalog - 2012 Hyundai i30 1.6 CRDi 128	https://www.automobile-catalog.com/car/2012/1607495/hyundai_i30_1_6_crdi_128.html
EU-NISSAN-SUNNY-B11-COUPE-3D-01	4135	1620	1355	Automobile-Catalog - 1983 Nissan Sunny 1.5 GL Coupe	https://www.automobile-catalog.com/car/1983/2210405/nissan_sunny_1_5_gl_coupe.html
EU-HONDA-ACCORD-II-HATCHBACK-3D-01	4255	1665	1355	Automobile-Catalog - 1983 Honda Accord Hatchback 1.6 EX Europe	https://www.automobile-catalog.com/car/1983/1091465/honda_accord_coupe_1_6_ex.html
EU-HONDA-ACCORD-II-SEDAN-4D-01	4455	1665	1375	Automobile-Catalog - 1984 Honda Accord Limousine 1.6 EX Europe	https://www.automobile-catalog.com/car/1984/1091450/honda_accord_limousine_1_6_ex_hondamatic.html
EU-NISSAN-SUNNY-B11-WAGON-5D-01	4255	1620	1360	Automobile-Catalog - 1983 Nissan Sunny 1.5 GL Traveller	https://www.automobile-catalog.com/car/1983/2210390/nissan_sunny_1_5_gl_traveller.html
EU-HONDA-ACCORD-III-SEDAN-4D-01	4535	1695	1355	Automobile-Catalog - 1986 Honda Accord EX 2.0 Europe	https://www.automobile-catalog.com/car/1986/1097270/honda_accord_ex_2_0.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX 4d catalyst	https://www.automobile-catalog.com/car/1987/2219330/nissan_sunny_1_6_slx_4d_cat.html
EU-HONDA-ACCORD-III-AERODECK-3D-01	4335	1695	1335	Automobile-Catalog - 1986 Honda Accord Aerodeck EX 2.0 Europe	https://www.automobile-catalog.com/car/1986/1097435/honda_accord_aerodeck_ex_2_0.html
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380	Automobile-Catalog - 1988 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1988/2219870/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380	Automobile-Catalog - 1987 Nissan Sunny 1.6 SGX	https://www.automobile-catalog.com/car/1987/2219075/nissan_sunny_1_6_sgx.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4215	1640	1395	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX 4WD catalyst	https://www.automobile-catalog.com/car/1987/2219345/nissan_sunny_1_6_slx_4wd_cat.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-02	4215	1645	1380	Automobile-Catalog - 1989 Nissan Sunny SLX 1.6 4d catalyst	https://www.automobile-catalog.com/car/1989/2219450/nissan_sunny_slx_1_6_4d_automatic_cat.html
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951	Automobile-Catalog - Mercedes-Benz G 300 CDI Station Wagon LWB	https://www.automobile-catalog.com/car/2012/2567370/mercedes-benz_g_300_cdi_station_wagon_lwb.html
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	4030	1645	1380	Automobile-Catalog - 1989 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1989/2219420/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	4030	1645	1380	Automobile-Catalog - 1989 Nissan Sunny GTI 16V catalyst	https://www.automobile-catalog.com/car/1989/2219420/nissan_sunny_gti_16v_cat.html
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325	Automobile-Catalog - 1988 Nissan Sunny 1.6 GSX Coupe Europe	https://www.automobile-catalog.com/car/1988/2222465/nissan_sunny_1_6_gsx_coupe_automatic.html
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385	Automobile-Catalog - 1988 Nissan Sunny 1.6 LX Estate Europe	https://www.automobile-catalog.com/car/1988/2222660/nissan_sunny_1_6_lx_estate.html
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400	Automobile-Catalog - 1987 Nissan Sunny 1.6 SLX Traveller 4WD catalyst	https://www.automobile-catalog.com/car/1987/2222630/nissan_sunny_1_6_slx_traveller_4wd_cat.html
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395	Automobile-Catalog - 1991 Nissan Sunny 2.0 LX Diesel 4d	https://www.automobile-catalog.com/car/1991/2247500/nissan_sunny_2_0_lx_diesel_4d.html
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395	Automobile-Catalog - 1991 Nissan Sunny 2.0 GTI 5d	https://www.automobile-catalog.com/car/1991/2247575/nissan_sunny_2_0_gti_5d.html
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395	Automobile-Catalog - 1992 Nissan Sunny 1.4 LX 3d	https://www.automobile-catalog.com/car/1992/2247695/nissan_sunny_1_4_lx_3d.html
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525	Automobile-Catalog - 1994 Nissan Sunny 1.6i SLX Wagon 4x4	https://www.automobile-catalog.com/car/1994/2248430/nissan_sunny_1_6i_slx_wagon_4x4.html
EU-NISSAN-STANZA-T11-SEDAN-4D-01	4280	1665	1385	Automobile-Catalog - Nissan Stanza T11 Export Sedan	https://www.automobile-catalog.com/make/nissan/stanza_2gen_t11/stanza_t11_export_sedan/1983.html
EU-NISSAN-STANZA-T11-HATCHBACK-3D-01	4225	1665	1370	Automobile-Catalog - 1982 Nissan Stanza 1.8 3d	https://www.automobile-catalog.com/car/1982/2215220/nissan_stanza_1_8_3d.html
EU-NISSAN-STANZA-T11-HATCHBACK-5D-01	4280	1665	1390	Automobile-Catalog - 1982 Nissan Stanza 1.8 5d	https://www.automobile-catalog.com/car/1982/2215280/nissan_stanza_1_8_5d_automatic.html
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	4350	1655	1400	Automobile-Catalog - 1981 Datsun Bluebird 1.8 GL	https://www.automobile-catalog.com/car/1981/45245/datsun_bluebird_1_8.html
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	4395	1655	1400	Automobile-Catalog - 1983 Datsun Bluebird 1.8 GL	https://www.automobile-catalog.com/car/1983/2119295/datsun_bluebird_1_8_gl.html
EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	4400	1655	1400	Automobile-Catalog - 1980 Datsun Bluebird 1.8 GL Wagon	https://www.automobile-catalog.com/car/1980/2119145/datsun_bluebird_1_8_gl_wagon.html
EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	4445	1655	1405	Automobile-Catalog - 1982 Datsun Bluebird 1.8 GL Wagon	https://www.automobile-catalog.com/car/1982/2119340/datsun_bluebird_1_8_gl_wagon.html
EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	4360	1690	1400	Automobile-Catalog - 1985 Nissan Bluebird 2.0 SGL	https://www.automobile-catalog.com/car/1985/2240120/nissan_bluebird_2_0_sgl.html
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	4405	1690	1455	Automobile-Catalog - 1985 Nissan Bluebird 2.0 GL Estate	https://www.automobile-catalog.com/car/1985/2240165/nissan_bluebird_2_0_gl_estate.html
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	4445	1690	1475	Automobile-Catalog - 1988 Nissan Bluebird 2.0 GL Estate	https://www.automobile-catalog.com/car/1988/2236745/nissan_bluebird_2_0_gl_estate.html
EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	4405	1690	1395	Automobile-Catalog - 1987 Nissan Bluebird 2.0 SGX 4-door	https://www.automobile-catalog.com/car/1987/2237210/nissan_bluebird_2_0_sgx_4-d.html
EU-HONDA-LEGEND-I-SEDAN-4D-01	4775	1745	1375	Automobile-Catalog - Honda Legend Sedan 2.5i	https://www.automobile-catalog.com/car/1986/1089455/honda_legend_2_5i.html
EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	4460	1690	1395	Automobile-Catalog - 1989 Nissan Bluebird 2.0i Executive 4-door	https://www.automobile-catalog.com/car/1989/2236865/nissan_bluebird_2_0_gsx_4-d.html
EU-HONDA-LEGEND-II-SEDAN-4D-01	4955	1810	1405	Automobile-Catalog - Honda Legend Sedan 3.2i 24V	https://www.automobile-catalog.com/car/1991/1092385/honda_legend_3_2i_24v.html
EU-HONDA-LEGEND-I-COUPE-2D-01	4770	1745	1320	Automobile-Catalog - Honda Legend Coupe 2.7i 24V	https://www.automobile-catalog.com/car/1988/1089665/honda_legend_coupe_2_7i_24v.html
EU-HONDA-LEGEND-II-COUPE-2D-01	4945	1810	1375	Automobile-Catalog - Honda Legend Coupe 3.2i 24V	https://www.automobile-catalog.com/car/1991/1092470/honda_legend_coupe_3_2i_24v.html
EU-HONDA-PRELUDE-I-COUPE-2D-01	4090	1635	1290	Automobile-Catalog - Honda Prelude 1.6	https://www.automobile-catalog.com/car/1979/1086765/honda_prelude_1_6.html
EU-HONDA-PRELUDE-II-COUPE-2D-01	4295	1690	1295	Automobile-Catalog - 1984 Honda Prelude EX 1.8 Europe	https://www.automobile-catalog.com/car/1984/1091885/honda_prelude_ex.html
EU-HONDA-CRX-I-COUPE-2D-01	3675	1625	1270	Automobile-Catalog - Honda CR-X 1.5i	https://www.automobile-catalog.com/car/1984/1091625/honda_cr-x_1_5i.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	4420	1690	1395	Automobile-Catalog - 1989 Nissan Bluebird 2.0i Executive 5-door	https://www.automobile-catalog.com/car/1989/2236895/nissan_bluebird_2_0_gsx_5-d.html
EU-HONDA-CRX-II-COUPE-2D-01	3800	1675	1270	Automobile-Catalog - Honda CR-X 1.6i-16V	https://www.automobile-catalog.com/car/1988/1098895/honda_cr-x_1_6i-16v.html
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	4365	1690	1395	Automobile-Catalog - 1987 Nissan Bluebird 2.0 SGX 5-door	https://www.automobile-catalog.com/car/1987/2237240/nissan_bluebird_2_0_sgx_5-d.html
EU-HONDA-CRX-III-CONVERTIBLE-2D-01	3995	1695	1255	Automobile-Catalog - Honda CR-X del Sol ESi	https://www.automobile-catalog.com/car/1992/1102565/honda_cr-x_del_sol_esi.html
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295	Automobile-Catalog - Honda Prelude 2.0 EX	https://www.automobile-catalog.com/car/1988/1099040/honda_prelude_2_0_ex.html
EU-NISSAN-MAXIMA-III-SEDAN-4D-01	4780	1760	1395	Automobile-Catalog - Nissan Maxima 3.0i V6	https://www.automobile-catalog.com/car/1989/2227310/nissan_maxima_3_0i_v6.html
EU-HONDA-PRELUDE-II-COUPE-2D-FACELIFT-01	4375	1690	1295	Automobile-Catalog - 1986 Honda Prelude EX 2.0i-16 Europe	https://www.automobile-catalog.com/car/1986/1092005/honda_prelude_ex_2_0i-16.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4001-4100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1981/2109620/datsun_sunny_1500_station_wagon_l.html?utm_source=chatgpt.com "1981 Datsun Sunny 1500 Station Wagon L Specs Review ..."
[2]: https://www.automobile-catalog.com/car/1984/1091885/honda_prelude_ex.html?utm_source=chatgpt.com "1984 Honda Prelude EX Specs Review (77 kW / 105 PS / 103 hp) (for Europe )"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4001-4100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4001-4100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5431 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1620 行）

