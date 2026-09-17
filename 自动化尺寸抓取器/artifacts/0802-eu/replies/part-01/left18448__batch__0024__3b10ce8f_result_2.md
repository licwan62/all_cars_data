# 任务：left18448 第 2301-2400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0024__3b10ce8f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2301-2400 行

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
left18448.tsv

【当前独立任务】
left18448 第 2301-2400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2301-2400_ktype_dimension_mapping_final.tsv
- left18448_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-4-3-0-CSL-COUPE-01	4794	1921	1386
EU-BMW-4-F32-COUPE-RWD-01	4638	1825	1362
EU-BMW-4-F32-COUPE-XDRIVE-01	4638	1825	1377
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384
EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	4638	1825	1399
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390
EU-BMW-4-G22-M440I-COUPE-RWD-01	4770	1852	1386
EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	4770	1852	1393
EU-BMW-4-G23-CONVERTIBLE-01	4768	1852	1384
EU-BMW-4-G23-CONVERTIBLE-XDRIVE-01	4768	1852	1391
EU-BMW-4-G23-M440I-CONVERTIBLE-RWD-01	4770	1852	1387
EU-BMW-4-G23-M440I-CONVERTIBLE-XDRIVE-01	4770	1852	1394

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	4	M4 CS Xdrive	Coupe	Allrad	Benzin	Jul 2024	-	800023
BMW	4	M4 CSL	Coupe	Heckantrieb	Benzin	May 2022	Feb 2023	147718
BMW	4	M4 GTS	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2019	118195
BMW	4	M440 I Mild-hybrid	Coupe	Heckantrieb	Benzin/Elektro	Sep 2022	-	150814
BMW	4	M440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	Jul 2021	-	144694
BMW	4	M440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	Jul 2024	-	801022
BMW	5	518 D	Kombi	Heckantrieb	Diesel	Jul 2013	Jun 2014	59794
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	Jul 2013	Jun 2014	59795
BMW	5	518 D	Kombi	Heckantrieb	Diesel	Jul 2014	Feb 2017	106271
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	Jul 2014	Oct 2016	106457
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	Jul 2013	Oct 2016	116690
BMW	5	518 D	Kombi	Heckantrieb	Diesel	Jul 2013	Feb 2017	116691
BMW	5	518 D	Kombi	Heckantrieb	Diesel	Jul 2014	Feb 2017	125059
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	Oct 2013	Oct 2016	125105
BMW	5	518 I	Kombi	Heckantrieb	Benzin	May 1994	Jul 1996	15597
BMW	5	518 I	Stufenheck	Heckantrieb	Benzin	Jun 1979	Jun 1981	17036
BMW	5	518 I	Stufenheck	Heckantrieb	Benzin	May 1981	Dec 1987	17037
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Feb 2000	Jun 2003	14599
BMW	5	520 D	Kombi	Heckantrieb	Diesel	Feb 2000	Sep 2003	14600
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Sep 2005	Dec 2009	19023
BMW	5	520 D	Schrägheck	Heckantrieb	Diesel	Apr 2011	Feb 2017	57270
BMW	5	520 D	Kombi	Heckantrieb	Diesel	Jul 2014	Feb 2017	106274
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Jul 2014	Oct 2016	106458
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Jun 2010	Oct 2016	116680
BMW	5	520 D	Kombi	Heckantrieb	Diesel	Jun 2010	Feb 2017	116681
BMW	5	520 D	Schrägheck	Heckantrieb	Diesel	Jul 2012	Jun 2013	116682
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Sep 2016	Jun 2023	123345
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	Sep 2016	Jun 2023	123822
BMW	5	520 D	Schrägheck	Heckantrieb	Diesel	Jul 2013	Feb 2017	125128
BMW	5	520 D	Kombi	Heckantrieb	Diesel	Mar 2017	-	125339
BMW	5	520 D	Kombi	Heckantrieb	Diesel	Mar 2017	-	126185
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Jul 2023	-	154720
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Jul 2023	-	155892
BMW	5	520 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	Mar 2024	-	157753
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	Jul 2013	Jun 2014	59780
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2013	Jun 2014	59782
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	Jul 2014	Feb 2017	106275
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2014	Oct 2016	106459
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	Jul 2013	Feb 2017	116692
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2013	Oct 2016	116693
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	Sep 2016	Jun 2023	123346
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	Sep 2016	Jun 2023	123823
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	Jul 2013	Jun 2014	125041
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	Jul 2017	-	127986
BMW	5	520 D Xdrive Mild-hybrid	Stufenheck	Allrad	Diesel/Elektro	Jul 2023	-	154721
BMW	5	520 D Xdrive Mild-hybrid	Kombi	Allrad	Diesel/Elektro	Mar 2024	-	157755
BMW	5	520 E Plug-in-hybrid	Kombi	Heckantrieb	Benzin/Elektro	Mar 2021	May 2022	143459
BMW	5	520 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Mar 2021	May 2022	143607
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jan 1996	Jun 2003	5052
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Sep 2011	Oct 2016	11832
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Oct 2010	Feb 2017	11857
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jan 1996	Jun 2003	14186
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Mar 1997	Aug 2001	14427
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Sep 2000	Jun 2003	15266
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Sep 2000	Dec 2003	15269
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jul 2003	Mar 2010	17290
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Sep 2007	Feb 2010	59410
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Jul 2007	Aug 2010	59411
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Sep 2011	Feb 2017	116679
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jul 2013	Oct 2016	117598
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Sep 2000	Dec 2003	126077
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Sep 2000	Jun 2003	126078
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Jul 2017	Jun 2020	128020
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jul 2017	-	128091
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jul 2017	Jun 2023	128146
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	Jul 2017	Jun 2020	128151
BMW	5	520 I	Kombi	Heckantrieb	Benzin	Jul 2017	Jun 2020	128152
BMW	5	520 I Mhev	Kombi	Heckantrieb	Benzin/Elektro	Nov 2024	-	801133
BMW	5	520 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2023	-	154722
BMW	5	520 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2023	-	155891
BMW	5	520 I Mild-hybrid 1.6	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2024	-	800099
BMW	5	523 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Jul 2023	-	156203
BMW	5	523 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	Jul 2023	-	156204
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	Sep 1995	Aug 2000	5093
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	Jan 2010	Aug 2011	14030
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	Oct 2004	Feb 2007	19013
BMW	5	523 I	Kombi	Heckantrieb	Benzin	Oct 2004	Feb 2007	19015
BMW	5	523 I	Kombi	Heckantrieb	Benzin	Nov 2009	Aug 2011	46024
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	Mar 2007	Dec 2009	118554
BMW	5	523 I	Kombi	Heckantrieb	Benzin	Jan 2007	Dec 2010	118557
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	Jan 2010	Aug 2011	125098
BMW	5	523 I	Kombi	Heckantrieb	Benzin	Sep 1998	Aug 2000	126080
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	Sep 2011	Oct 2016	11836
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Sep 2011	Feb 2017	11877
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	Feb 2000	Jun 2003	14679
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Feb 2000	May 2004	14680
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	Jun 2004	Mar 2010	17968
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Mar 2004	Mar 2007	17969
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Sep 2011	Feb 2017	116694
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Jul 2017	Jun 2019	127985
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	Jul 2017	Jun 2019	128026
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	Jul 2017	Jun 2019	128153
BMW	5	525 D	Kombi	Heckantrieb	Diesel	Jul 2017	Jun 2019	128154
BMW	5	525 D Xdrive	Stufenheck	Allrad	Diesel	Sep 2011	Oct 2016	11837
BMW	5	525 D Xdrive	Kombi	Allrad	Diesel	Sep 2011	Feb 2017	11878
BMW	5	525 D Xdrive	Kombi	Allrad	Diesel	Jul 2013	Feb 2017	116695
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	Sep 2000	Jun 2003	15270
BMW	5	525 I	Kombi	Heckantrieb	Benzin	Sep 2000	May 2004	15272
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	Sep 2003	Feb 2005	17293
BMW	5	525 I	Kombi	Heckantrieb	Benzin	Jun 2004	Dec 2010	17775


--- Round 1 / 首次发送 ---
## 更新点

* 已完成当前批次首个车型簇：6 条 BMW 4 系映射全部闭合。
* 新建两个特殊性能车尺寸组：

  * 2024 BMW M4 CS：官方规格为 `4801 × 1918 × 1399 mm`。
  * BMW M4 GTS：官方规格为 `4689 × 1870 × 1383 mm`；其可调前分流器和后翼造成的特殊外廓与普通 F82 M4 分组处理。
* M4 CSL 及 M440i Coupé 直接复用任务给出的跨批次稳定尺寸组，没有重复创建或重新抓取。
* `801022` 虽从 2024 年 7 月开始，但现有缓存中的 M440i xDrive Coupé 三维没有发生变化，因此继续复用既有 G22 xDrive 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：6
* PENDING 映射：94
* 已闭合并引用的尺寸组：5
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800023	800023	Coupe	M4 G82	G82	2	EU-BMW-4-G82-M4-CS-COUPE-01	HIGH	2024 M4 CS专属外部套件和物理外廓。	READY
147718	147718	Coupe	M4 G82	G82	2	EU-BMW-4-3-0-CSL-COUPE-01	HIGH	M4 CSL双座特殊性能版物理外廓。	READY
118195	118195	Coupe	M4 F82	F82	2	EU-BMW-4-F82-M4-GTS-COUPE-01	HIGH	M4 GTS专属可调空气动力套件物理外廓。	READY
150814	150814	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-RWD-01	HIGH	M440i后驱双门轿跑。	READY
144694	144694	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH	M440i xDrive双门轿跑。	READY
801022	801022	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH	2024款M440i xDrive继续沿用已确认G22外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-G82-M4-CS-COUPE-01	4801	1918	1399	BMW Group PressClub BMW M4 CS official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0441542EN/615500
EU-BMW-4-F82-M4-GTS-COUPE-01	4689	1870	1383	BMW Group PressClub BMW M4 GTS official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0236962EN/385978
```

## 下一步优先处理

优先闭合 BMW 5 系高复用车型簇：

1. F10/F11 的 518d、520d、520i、525d及 xDrive，分清改款前后长度和驱动高度差异。
2. G30/G31 跨 2020 年改款的 Ktype，确认是否需要拆分 `prefl`、`facelift` 派生行。
3. G60/G61 的 520d、520i、523d，包括 Sedan 与 Touring。
4. 最后处理 E12、E28、E34、E39、E60/E61 以及 F07 Gran Turismo 历史车身。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2301-2400_ktype_dimension_mapping_final.tsv
- left18448_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 BMW 5 系 F10/F11 车型簇，共新增 **32 个 READY Ktype、36 条映射行**。
* F10 改款前 Sedan 建组为 `4899 × 1860 × 1464 mm`；F10 LCI Sedan 建组为 `4907 × 1860 × 1464 mm`。跨越 2013 年改款且长度发生变化的 4 个 Ktype 已拆为 `prefl`、`facelift` 两个物理分支。
* F11 Touring 改款前后均为 `4907 × 1860 × 1462 mm`，因此没有因发动机、xDrive 或改款重复建组。官方资料也显示 Sedan 与 Touring 的 xDrive 版本未产生新的三维外廓。([BMW Group PressClub][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：38
* READY 映射行：42
* PENDING Ktype：62
* 已确认并被引用尺寸组：8
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59794	59794	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
59795	59795	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
106271	106271	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106457	106457	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116690	116690	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116691	116691	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
125059	125059	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
125105	125105	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
106274	106274	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106458	106458	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116680_prefl	116680	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
116680_facelift	116680	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
116681	116681	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
59780	59780	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
59782	59782	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
106275	106275	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106459	106459	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116692	116692	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116693	116693	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
125041	125041	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
11832_prefl	11832	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11832_facelift	11832	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11857	11857	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116679	116679	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
117598	117598	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
14030	14030	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH		READY
46024	46024	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
125098	125098	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH		READY
11836_prefl	11836	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11836_facelift	11836	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11877	11877	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116694	116694	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
11837_prefl	11837	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11837_facelift	11837	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11878	11878	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116695	116695	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	BMW Group PressClub The New BMW 5 Series Sedan official press kit	https://www.press.bmwgroup.com/global/article/attachment/T0076602EN/132811
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	BMW Group PressClub Specifications of the BMW 5 Series Sedan valid from July 2013	https://www.press.bmwgroup.com/global/article/attachment/T0143206EN/224272
EU-BMW-5-F11-WAGON-01	4907	1860	1462	BMW Group PressClub The New BMW 5 Series Touring official press kit; BMW Group PressClub BMW 518d and 520d official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0078341EN/132719;https://www.press.bmwgroup.com/global/article/attachment/T0193460EN/281508
```

## 下一步优先处理

优先闭合剩余高复用的新一代车型簇：

1. G30/G31 的 520d、520i、525d、520e，集中处理 2020 年 LCI 边界。
2. G60/G61 的 520d、520i、523d及 xDrive。
3. F07 5 Series Gran Turismo 改款前后尺寸组。
4. 最后处理 E12、E28、E34、E39、E60/E61 历史车身。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0078341EN/132719 "Microsoft Word - BMW 5 Series Touring EN.docx"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2301-2400_ktype_dimension_mapping_final.tsv
- left18448_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 G30/G31 中生产区间明确的 Sedan、Touring、xDrive 与 520e 插电混动分支；跨 2020 年改款且外廓长度变化的 Ktype 已拆分为 `prefl`、`facelift`。G30 LCI 普通 Sedan 与 520e Sedan 高度不同，分别建组；G31 520e Touring 与普通 LCI Touring 三维一致，复用同一尺寸组。
* 已闭合 G60 Sedan 与 G61 Touring 当前输入分支；两种 BodyStyle 虽三维相同，仍按不同物理车身分别建组。([BMW Group PressClub][1])
* `125339`、`126185`、`127986`、`128091` 的结束年月为 `-`，暂不将其解释为跨越 G30/G31 改款，留待下一轮补齐边界。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：63
* READY 映射行：72
* PENDING Ktype：37
* 已确认并被引用尺寸组：15
* 本轮新增 READY Ktype：25
* 本轮新增映射行：30
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123345_prefl	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123345_facelift	123345	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
123822_prefl	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123822_facelift	123822	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
154720	154720	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
155892	155892	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
157753	157753	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
123346_prefl	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123346_facelift	123346	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
123823_prefl	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123823_facelift	123823	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
154721	154721	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
157755	157755	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
143459	143459	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH		READY
143607	143607	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-PHEV-FACELIFT-01	HIGH		READY
128020	128020	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128146_prefl	128146	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
128146_facelift	128146	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
128151	128151	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128152	128152	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
801133	801133	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
154722	154722	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
155891	155891	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
800099	800099	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
156203	156203	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
156204	156204	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
127985	127985	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128026	128026	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128153	128153	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128154	128154	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub BMW 520i Sedan official specifications valid from 07/2017	https://www.press.bmwgroup.com/global/article/attachment/T0270585EN/384942
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group PressClub BMW 5 Series Sedan official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325537EN/471546
EU-BMW-5-G30-SEDAN-PHEV-FACELIFT-01	4963	1868	1483	BMW Group PressClub BMW 520e Sedan official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325537EN/471546
EU-BMW-5-G31-WAGON-PREFL-01	4942	1868	1498	BMW Group PressClub BMW 520i Touring official specifications valid from 07/2017	https://www.press.bmwgroup.com/global/article/attachment/T0270513EN/385112
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub BMW 5 Series Touring official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325535EN/471544
EU-BMW-5-G60-SEDAN-01	5060	1900	1515	BMW Group PressClub The new BMW 5 Series Sedan official press release	https://www.press.bmwgroup.com/global/article/detail/T0416261EN/the-new-bmw-5-series-sedan?language=en
EU-BMW-5-G61-WAGON-01	5060	1900	1515	BMW Group PressClub The new BMW 5 Series Touring official press release	https://www.press.bmwgroup.com/global/article/detail/T0439374EN/the-new-bmw-5-series-touring?language=en
```

## 下一步优先处理

1. 补齐 `125339`、`126185`、`127986`、`128091` 的 G30/G31 改款覆盖边界。
2. 集中闭合 F07 5 Series Gran Turismo 的改款前后分支。
3. 批量处理 E39 Sedan/Touring，随后处理 E60/E61。
4. 最后处理 E12、E28、E34 历史车型。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0416261EN/the-new-bmw-5-series-sedan?language=en "The new BMW 5 Series Sedan."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2301-2400_ktype_dimension_mapping_final.tsv
- left18448_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 基于既有 BMW 5 系桥接缓存，批量闭合 E34、E39、E60 和 E61 相同物理外廓的 Ktype，未逐 Ktype 重复抓取。
* `17036` 已按 75 kW、1979–1981 的 E12 518i 边界闭合为 `4620 × 1690 × 1425 mm`。([汽车目录][1])
* F07 改款使车长由 4998 mm 变为 5004 mm；`57270` 拆分为改款前、改款后两个分支，`116682` 和 `125128` 分别关联对应尺寸组。([BMW Group PressClub][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：106
* PENDING Ktype：4
* 已确认并被引用尺寸组：24
* 本轮新增 READY Ktype：33
* 本轮新增映射行：34
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15597	15597	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
17036	17036	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	MEDIUM	1981年换代边界已按75kW E12 518i确认。	READY
17037	17037	Sedan	5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
14599	14599	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14600	14600	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
19023	19023	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
57270_prefl	57270	Hatchback	5 Series F07	F07	5	EU-BMW-5-F07-HATCHBACK-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
57270_facelift	57270	Hatchback	5 Series F07 LCI	F07	5	EU-BMW-5-F07-HATCHBACK-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
116682	116682	Hatchback	5 Series F07	F07	5	EU-BMW-5-F07-HATCHBACK-PREFL-01	HIGH		READY
125128	125128	Hatchback	5 Series F07 LCI	F07	5	EU-BMW-5-F07-HATCHBACK-FACELIFT-01	HIGH		READY
5052	5052	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14186	14186	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14427	14427	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
15266	15266	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
15269	15269	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17290	17290	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
59410	59410	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
59411	59411	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
126077	126077	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
126078	126078	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
5093	5093	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
19013	19013	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
19015	19015	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
118554	118554	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
118557	118557	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
126080	126080	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
14679	14679	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14680	14680	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17968	17968	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
17969	17969	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
15270	15270	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
15272	15272	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17293	17293	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
17775	17775	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-E34-WAGON-01	4720	1751	1417	ADAC BMW 518i Touring E34 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e34-e34s-e345s/285746/
EU-BMW-5-E12-SEDAN-01	4620	1690	1425	Automobile-Catalog 1979 BMW 518i technical specifications	https://www.automobile-catalog.com/car/1979/170480/bmw_518i.html
EU-BMW-5-E28-SEDAN-01	4620	1700	1415	ADAC BMW 518i E28 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e28-e28s/254414/
EU-BMW-5-E39-SEDAN-01	4775	1800	1435	ADAC BMW 520d E39 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e39-e39s-facelift/112777/
EU-BMW-5-E39-WAGON-01	4805	1800	1445	ADAC BMW 520d Touring E39 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e39-e39s-facelift/108048/
EU-BMW-5-E60-SEDAN-01	4841	1846	1468	ADAC BMW 520d E60 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e60-e61-facelift/221929/
EU-BMW-5-E61-WAGON-01	4843	1846	1491	ADAC BMW 520d Touring E61 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e60-e61-facelift/221931/
EU-BMW-5-F07-HATCHBACK-PREFL-01	4998	1901	1559	BMW Group PressClub BMW 520d Gran Turismo official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0126736EN/207765
EU-BMW-5-F07-HATCHBACK-FACELIFT-01	5004	1901	1559	BMW Group PressClub BMW 5 Series Gran Turismo official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0143207EN/219005
```

## 下一步优先处理

优先解决最后 4 个结束年月为 `-` 的 G30/G31 Ktype：

1. `125339`、`126185`：520d G31 Touring。
2. `127986`：520d xDrive G31 Touring。
3. `128091`：520i G30 Sedan。
4. 仅确认其 Ktype 是否止于 2020 LCI 边界或同时覆盖改款前后；已建 G30/G31 尺寸组直接复用，不重新抓取三维。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/170480/bmw_518i.html?utm_source=chatgpt.com "1979 BMW 518i Specs Review (75 kW / 102 PS / 101 hp) (since mid-year 1979 for Europe Sweden)"
[2]: https://www.press.bmwgroup.com/global/article/attachment/T0126736EN/207764?utm_source=chatgpt.com "Specifications BMW 5 Series Gran Turismo."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2301-2400_ktype_dimension_mapping_final.tsv
- left18448_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后 4 个待处理 Ktype 已完成边界闭合；`125339`、`126185`、`127986`、`128091` 均拆分为 G30/G31 改款前和改款后分支，直接复用已确认尺寸组，未新增或重复抓取尺寸。桥接缓存明确显示这些开放结束日期记录同时命中改款前后两套外廓。
* 已完成固定表头、唯一主键、映射引用闭合、尺寸与来源非空、孤立尺寸组检查。
* 当前批次达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：114
* PENDING Ktype：0
* DIMENSION_GROUP：24
* 机械校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800023	800023	Coupe	M4 G82	G82	2	EU-BMW-4-G82-M4-CS-COUPE-01	HIGH	2024 M4 CS专属外部套件和物理外廓。	READY
147718	147718	Coupe	M4 G82	G82	2	EU-BMW-4-3-0-CSL-COUPE-01	HIGH	M4 CSL双座特殊性能版物理外廓。	READY
118195	118195	Coupe	M4 F82	F82	2	EU-BMW-4-F82-M4-GTS-COUPE-01	HIGH	M4 GTS专属可调空气动力套件物理外廓。	READY
150814	150814	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-RWD-01	HIGH		READY
144694	144694	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH		READY
801022	801022	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH		READY
59794	59794	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
59795	59795	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
106271	106271	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106457	106457	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116690	116690	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116691	116691	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
125059	125059	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
125105	125105	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
15597	15597	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
17036	17036	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	MEDIUM	1981年换代边界已按75kW E12 518i确认。	READY
17037	17037	Sedan	5 Series E28	E28	4	EU-BMW-5-E28-SEDAN-01	HIGH		READY
14599	14599	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14600	14600	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
19023	19023	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
57270_prefl	57270	Hatchback	5 Series F07	F07	5	EU-BMW-5-F07-HATCHBACK-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
57270_facelift	57270	Hatchback	5 Series F07 LCI	F07	5	EU-BMW-5-F07-HATCHBACK-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
106274	106274	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106458	106458	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116680_prefl	116680	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
116680_facelift	116680	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
116681	116681	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116682	116682	Hatchback	5 Series F07	F07	5	EU-BMW-5-F07-HATCHBACK-PREFL-01	HIGH		READY
123345_prefl	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123345_facelift	123345	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
123822_prefl	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123822_facelift	123822	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
125128	125128	Hatchback	5 Series F07 LCI	F07	5	EU-BMW-5-F07-HATCHBACK-FACELIFT-01	HIGH		READY
125339_prefl	125339	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	同一Ktype覆盖G31改款前后；改款前分支。	READY
125339_facelift	125339	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖G31改款前后；改款后分支。	READY
126185_prefl	126185	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	同一Ktype覆盖G31改款前后；改款前分支。	READY
126185_facelift	126185	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖G31改款前后；改款后分支。	READY
154720	154720	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
155892	155892	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
157753	157753	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
59780	59780	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
59782	59782	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
106275	106275	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
106459	106459	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
116692	116692	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116693	116693	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
123346_prefl	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123346_facelift	123346	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
123823_prefl	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
123823_facelift	123823	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
125041	125041	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
127986_prefl	127986	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	同一Ktype覆盖G31改款前后；改款前分支。	READY
127986_facelift	127986	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖G31改款前后；改款后分支。	READY
154721	154721	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
157755	157755	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
143459	143459	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH		READY
143607	143607	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-PHEV-FACELIFT-01	HIGH		READY
5052	5052	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
11832_prefl	11832	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11832_facelift	11832	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11857	11857	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
14186	14186	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14427	14427	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
15266	15266	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
15269	15269	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17290	17290	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
59410	59410	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
59411	59411	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
116679	116679	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
117598	117598	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
126077	126077	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
126078	126078	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
128020	128020	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128091_prefl	128091	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后；改款前分支。	READY
128091_facelift	128091	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后；改款后分支。	READY
128146_prefl	128146	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype跨2020年改款；改款前分支。	READY
128146_facelift	128146	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2020年改款；改款后分支。	READY
128151	128151	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128152	128152	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
801133	801133	Wagon	5 Series G61	G61	5	EU-BMW-5-G61-WAGON-01	HIGH		READY
154722	154722	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
155891	155891	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
800099	800099	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
156203	156203	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
156204	156204	Sedan	5 Series G60	G60	4	EU-BMW-5-G60-SEDAN-01	HIGH		READY
5093	5093	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14030	14030	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH		READY
19013	19013	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
19015	19015	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
46024	46024	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
118554	118554	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
118557	118557	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
125098	125098	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH		READY
126080	126080	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
11836_prefl	11836	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11836_facelift	11836	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11877	11877	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
14679	14679	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
14680	14680	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17968	17968	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
17969	17969	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
116694	116694	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
127985	127985	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128026	128026	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128153	128153	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128154	128154	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
11837_prefl	11837	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	同一Ktype跨2013改款；改款前分支。	READY
11837_facelift	11837	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	同一Ktype跨2013改款；改款后分支。	READY
11878	11878	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
116695	116695	Wagon	5 Series F11 LCI	F11	5	EU-BMW-5-F11-WAGON-01	HIGH		READY
15270	15270	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
15272	15272	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH		READY
17293	17293	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-01	HIGH		READY
17775	17775	Wagon	5 Series E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2301-2400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-G82-M4-CS-COUPE-01	4801	1918	1399	BMW Group PressClub BMW M4 CS official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0441542EN/615500
EU-BMW-4-3-0-CSL-COUPE-01	4794	1921	1386	BMW Group PressClub BMW M4 CSL official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0386533EN/613138
EU-BMW-4-F82-M4-GTS-COUPE-01	4689	1870	1383	BMW Group PressClub BMW M4 GTS official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0236962EN/385978
EU-BMW-4-G22-M440I-COUPE-RWD-01	4770	1852	1386	BMW Group PressClub BMW M440i Coupe official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0333558EN/480212
EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	4770	1852	1393	BMW Group PressClub BMW M440i xDrive Coupe official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326318EN/472221
EU-BMW-5-F11-WAGON-01	4907	1860	1462	BMW Group PressClub The New BMW 5 Series Touring official press kit; BMW Group PressClub BMW 518d and 520d official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0078341EN/132719;https://www.press.bmwgroup.com/global/article/attachment/T0193460EN/281508
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	BMW Group PressClub Specifications of the BMW 5 Series Sedan valid from July 2013	https://www.press.bmwgroup.com/global/article/attachment/T0143206EN/224272
EU-BMW-5-E34-WAGON-01	4720	1751	1417	ADAC BMW 518i Touring E34 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e34-e34s-e345s/285746/
EU-BMW-5-E12-SEDAN-01	4620	1690	1425	Automobile-Catalog 1979 BMW 518i technical specifications	https://www.automobile-catalog.com/car/1979/170480/bmw_518i.html
EU-BMW-5-E28-SEDAN-01	4620	1700	1415	ADAC BMW 518i E28 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e28-e28s/254414/
EU-BMW-5-E39-SEDAN-01	4775	1800	1435	ADAC BMW 520d E39 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e39-e39s-facelift/112777/
EU-BMW-5-E39-WAGON-01	4805	1800	1445	ADAC BMW 520d Touring E39 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e39-e39s-facelift/108048/
EU-BMW-5-E60-SEDAN-01	4841	1846	1468	ADAC BMW 520d E60 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e60-e61-facelift/221929/
EU-BMW-5-F07-HATCHBACK-PREFL-01	4998	1901	1559	BMW Group PressClub BMW 520d Gran Turismo official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0126736EN/207765
EU-BMW-5-F07-HATCHBACK-FACELIFT-01	5004	1901	1559	BMW Group PressClub BMW 5 Series Gran Turismo official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0143207EN/219005
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	BMW Group PressClub The New BMW 5 Series Sedan official press kit	https://www.press.bmwgroup.com/global/article/attachment/T0076602EN/132811
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub BMW 520i Sedan official specifications valid from 07/2017	https://www.press.bmwgroup.com/global/article/attachment/T0270585EN/384942
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group PressClub BMW 5 Series Sedan official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325537EN/471546
EU-BMW-5-G31-WAGON-PREFL-01	4942	1868	1498	BMW Group PressClub BMW 520i Touring official specifications valid from 07/2017	https://www.press.bmwgroup.com/global/article/attachment/T0270513EN/385112
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub BMW 5 Series Touring official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325535EN/471544
EU-BMW-5-G60-SEDAN-01	5060	1900	1515	BMW Group PressClub The new BMW 5 Series Sedan official press release	https://www.press.bmwgroup.com/global/article/detail/T0416261EN/the-new-bmw-5-series-sedan?language=en
EU-BMW-5-G61-WAGON-01	5060	1900	1515	BMW Group PressClub The new BMW 5 Series Touring official press release	https://www.press.bmwgroup.com/global/article/detail/T0439374EN/the-new-bmw-5-series-touring?language=en
EU-BMW-5-G30-SEDAN-PHEV-FACELIFT-01	4963	1868	1483	BMW Group PressClub BMW 520e Sedan official specifications valid from 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0325537EN/471546
EU-BMW-5-E61-WAGON-01	4843	1846	1491	ADAC BMW 520d Touring E61 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/e60-e61-facelift/221931/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2301-2400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2792 行）
- 累计尺寸组：dimension_groups_final.tsv（744 行）

