# 任务：left18448 第 5301-5400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0054__3369c6d6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5301-5400 行

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
left18448 第 5301-5400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Capri	1.3	Coupe	Heckantrieb	Benzin	Feb 1974	Aug 1977	11162
Ford	Capri	1.3	Coupe	Heckantrieb	Benzin	Jan 1978	Jun 1985	14257
Ford	Capri	1.3	Coupe	Heckantrieb	Benzin	Feb 1974	Aug 1977	14948
Ford	Capri	1.6	Coupe	Heckantrieb	Benzin	Feb 1974	Dec 1977	11027
Ford	Capri	2	Coupe	Heckantrieb	Benzin	Jan 1978	Dec 1985	14949
Ford	Capri	2	Coupe	Heckantrieb	Benzin	Jan 1978	Dec 1982	15164
Ford	Capri	3	Coupe	Heckantrieb	Benzin	Jan 1978	Dec 1981	14947
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	Jan 1971	Dec 1972	15152
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	Oct 1972	Dec 1973	15153
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	Jan 1973	Dec 1973	15154
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1970	15155
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	Jan 1971	Dec 1973	15159
Ford	Capri	1600	Coupe	Heckantrieb	Benzin	Aug 1972	Feb 1974	11025
Ford	Capri	1600	Coupe	Heckantrieb	Benzin	Aug 1972	Feb 1974	14942
Ford	Capri	3000	Coupe	Heckantrieb	Benzin	Aug 1972	Feb 1974	11026
Ford	Capri	2.8 I Turbo	Coupe	Heckantrieb	Benzin	Jan 1982	Apr 1987	15165
Ford	Capri	2600 RS	Coupe	Heckantrieb	Benzin	Aug 1970	Feb 1974	11024
Ford	Capri	EV	SUV	Heckantrieb	Elektro	Oct 2024	-	159788
Ford	Capri	EV	SUV	Heckantrieb	Elektro	Oct 2024	-	159790
Ford	Capri	EV	SUV	Heckantrieb	Elektro	Mar 2026	-	164017
Ford	Capri	EV 4X4	SUV	Allrad	Elektro	Oct 2024	-	159789
Ford	C-Max	1.6	Großraumlimousine	Frontantrieb	Benzin	Apr 2007	Sep 2010	113250
Ford	C-Max	1.8	Großraumlimousine	Frontantrieb	Benzin	Feb 2007	Sep 2010	10288
Ford	C-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	56757
Ford	C-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	56760
Ford	C-Max	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	108790
Ford	C-Max	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	108791
Ford	C-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2018	Jun 2019	145790
Ford	C-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2018	Jun 2019	145827
Ford	C-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	111749
Ford	C-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	111753
Ford	C-Max	1.5 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	113252
Ford	C-Max	1.5 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	113253
Ford	C-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111755
Ford	C-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111765
Ford	C-Max	1.5 Tdci Econetic	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111764
Ford	C-Max	1.5 Tdci Econetic	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113264
Ford	C-Max	1.6 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Jun 2019	108792
Ford	C-Max	1.6 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Jun 2019	142731
Ford	C-Max	1.6 Flexifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	Feb 2011	Jun 2019	11922
Ford	C-Max	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Feb 2012	Jun 2019	55512
Ford	C-Max	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Feb 2012	Jun 2019	106025
Ford	C-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2007	Sep 2010	11895
Ford	C-Max	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108814
Ford	C-Max	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108815
Ford	C-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Jun 2019	14793
Ford	C-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	Feb 2012	Jun 2019	113147
Ford	C-Max	1.6 TI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2010	Jun 2019	142729
Ford	C-Max	2.0 Energi	Großraumlimousine	Frontantrieb	Benzin/Elektro	Jan 2015	Jun 2019	118794
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2011	Jun 2019	10196
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2007	Sep 2010	11894
Ford	C-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2011	Jun 2019	108816
Ford	C-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2011	Jun 2019	108817
Ford	C-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108818
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111766
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111767
Ford	C-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113287
Ford	C-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113292
Ford	Consul	1700	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1975	6592
Ford	Consul	1700	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1975	6596
Ford	Consul	1700	Kombi	Heckantrieb	Benzin	Jan 1972	Dec 1975	6599
Ford	Consul	1700	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1975	14950
Ford	Consul	1700	Kombi	Heckantrieb	Benzin	Jan 1972	Dec 1975	14951
Ford	Consul	1700	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1975	14952
Ford	Consul	2000	Stufenheck	Heckantrieb	Benzin	Sep 1974	Dec 1975	6593
Ford	Consul	2000	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1975	6594
Ford	Consul	2000	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1975	6597
Ford	Consul	2000	Kombi	Heckantrieb	Benzin	Jan 1972	Dec 1975	6600
Ford	Consul	2300	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1975	6595
Ford	Consul	2300	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1975	6598
Ford	Consul	2300	Kombi	Heckantrieb	Benzin	Jan 1972	Dec 1975	6601
Ford	Consul	3000	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1974	15169
Ford	Consul	3000	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1974	15170
Ford	Consul	3000	Kombi	Heckantrieb	Benzin	Jan 1972	Dec 1975	15172
Ford	Cougar	2.5 ST 200	Coupe	Frontantrieb	Benzin	Jan 2000	Dec 2001	14592
Ford	Cougar	2.5 V6 24V	Coupe	Frontantrieb	Benzin	Jun 2000	Dec 2001	15441
Ford	Courier	1.6	Pick-up	Frontantrieb	Benzin	Aug 2001	Dec 2011	121499
Ford	Courier	1.4 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	Apr 1996	Oct 1999	5742
Ford	Courier	1.8 DI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2000	Aug 2003	15829
Ford	Econovan	1.4	Kasten	Heckantrieb	Benzin	Mar 1986	Mar 1992	11095
Ford	Econovan	2.0 D	Kasten	Heckantrieb	Diesel	Mar 1986	Mar 1992	11096
Ford	Ecosport	1.0 Ecoboost	SUV	Frontantrieb	Benzin	Oct 2013	-	38703
Ford	Ecosport	1.0 Ecoboost	SUV	Frontantrieb	Benzin	Mar 2016	-	118620
Ford	Ecosport	1.5 Ecoblue Tdci	SUV	Frontantrieb	Diesel	May 2015	-	113168
Ford	Ecosport	1.5 Tdci	SUV	Frontantrieb	Diesel	Oct 2013	-	39881
Ford	Ecosport	1.5 Tdci	SUV	Frontantrieb	Diesel	May 2015	-	119943
Ford	Ecosport	1.5 TI	SUV	Frontantrieb	Benzin	Oct 2013	-	39840
Ford	Escort classic	1.6 16V	Schrägheck	Frontantrieb	Benzin	Oct 1998	Jul 2000	15373
Ford	Escort classic	1.8 TD	Schrägheck	Frontantrieb	Diesel	Oct 1998	Jul 2000	15372
Ford	Escort classic turnier	1.6 16V	Kombi	Frontantrieb	Benzin	Feb 1999	Jul 2000	15374
Ford	Escort classic turnier	1.8 TD	Kombi	Frontantrieb	Diesel	Feb 1999	Jul 2000	15375
Ford	Escort i	950	Stufenheck	Heckantrieb	Benzin	Aug 1968	Aug 1974	15244
Ford	Escort i	950	Stufenheck	Heckantrieb	Benzin	Aug 1968	Aug 1974	15245
Ford	Escort ii	1.6	Stufenheck	Heckantrieb	Benzin	Jan 1979	Dec 1980	125814
Ford	Escort ii turnier	1.1	Kombi	Heckantrieb	Benzin	Apr 1975	Aug 1980	15252
Ford	Escort ii turnier	1.1	Kombi	Heckantrieb	Benzin	Apr 1975	Aug 1980	15253
Ford	Escort ii turnier	1.3	Kombi	Heckantrieb	Benzin	Apr 1975	Aug 1980	14954
Ford	Escort iii	1.6 I	Schrägheck	Frontantrieb	Benzin	Jul 1985	Dec 1985	10223
Ford	Escort iii	RS 1600i	Schrägheck	Frontantrieb	Benzin	May 1982	Dec 1985	14953
Ford	Escort iv	1.6	Schrägheck	Frontantrieb	Benzin	Apr 1989	Jul 1990	6050


--- Round 1 / 首次发送 ---
## 更新点

* 闭合现代 **Ford Capri EV 五门 SUV** 尺寸组；后驱与四驱版本共用 `4634 × 1872 × 1626 mm` 官方外廓。
* 闭合 **C-MAX I 2007 改款五门 MPV** 尺寸组：`4372 × 1825 × 1588 mm`，宽度采用官方不含后视镜口径。
* 闭合 **C-MAX II 2015 改款五门 MPV** 尺寸组：`4379 × 1828 × 1610 mm`；同外壳的 `Kasten/Großraumlimousine` 登记版本复用该组。

## 当前批次进度

* READY 映射：22
* PENDING 输入 Ktype：78
* 已确认尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
159788	159788	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
159790	159790	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
164017	164017	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
159789	159789	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
113250	113250	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
10288	10288	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
145790	145790	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
145827	145827	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111749	111749	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111753	111753	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113252	113252	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
113253	113253	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
111755	111755	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111765	111765	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111764	111764	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113264	113264	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
11895	11895	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
11894	11894	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
111766	111766	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111767	111767	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113287	113287	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
113292	113292	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-CAPRI-EV-SUV-01	4634	1872	1626	Ford Capri detailed specification	https://www.fordpers.be/content/documents/news/2024/2024fordcapri_factsheet_eu.pdf
EU-FORD-C-MAX-I-FACELIFT-MPV-01	4372	1825	1588	Ford C-MAX UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf
EU-FORD-C-MAX-II-FACELIFT-MPV-01	4379	1828	1610	Ford C-MAX + Grand C-MAX brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf
```

## 下一步优先处理

1. 闭合 C-MAX II 改款前尺寸组，并拆分跨越 2015 改款且外廓变化的 Ktype。
2. 按 Capri Mk I、Mk II、Mk III、RS 及 Turbo 外部套件边界聚类。
3. 批量核对 Consul Sedan、Coupe、Wagon 三种车身尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新建 C-MAX II 改款前五门 MPV 尺寸组 `4380 × 1828 × 1626 mm`；对覆盖 2015 年改款前后的 18 个 Ktype 拆分 `prefl` 与 `facelift` 映射，改款后直接复用既有缓存组。改款前车型截至 2015 年 3 月，改款后车型自 2015 年 4 月起，两个外廓尺寸不同。([汽车数据][1])
* 新建北美版 C-MAX Energi 五门 MPV 独立尺寸组 `4409 × 1828 × 1623 mm`；不与欧洲普通 C-MAX II 或其改款组混用。([汽车目录][2])

## 当前批次进度

* READY 输入 Ktype：41 / 100
* READY 映射行：59
* PENDING 输入 Ktype：59
* 已确认尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56757_prefl	56757	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
56757_facelift	56757	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
56760_prefl	56760	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
56760_facelift	56760	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
108790_prefl	108790	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108790_facelift	108790	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108791_prefl	108791	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108791_facelift	108791	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108792_prefl	108792	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108792_facelift	108792	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
142731_prefl	142731	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
142731_facelift	142731	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
11922_prefl	11922	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
11922_facelift	11922	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
55512_prefl	55512	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
55512_facelift	55512	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
106025_prefl	106025	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
106025_facelift	106025	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
108814_prefl	108814	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108814_facelift	108814	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108815_prefl	108815	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108815_facelift	108815	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
14793_prefl	14793	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
14793_facelift	14793	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
113147_prefl	113147	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
113147_facelift	113147	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
142729_prefl	142729	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
142729_facelift	142729	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
118794	118794	MPV	C-MAX II Energi		5	EU-FORD-C-MAX-II-ENERGI-MPV-01	HIGH	北美版插电混动车身外廓。	READY
10196_prefl	10196	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
10196_facelift	10196	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
108816_prefl	108816	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108816_facelift	108816	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108817_prefl	108817	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108817_facelift	108817	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108818_prefl	108818	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108818_facelift	108818	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	4380	1828	1626	Auto-Data Ford C-MAX II 2.0 Duratorq TDCi specifications	https://www.auto-data.net/en/ford-c-max-ii-2.0-duratorq-tdci-140hp-dpf-19811
EU-FORD-C-MAX-II-ENERGI-MPV-01	4409	1828	1623	Automobile-Catalog 2015 Ford C-Max Energi specifications	https://www.automobile-catalog.com/car/2015/1596710/ford_c-max_energi.html
```

## 下一步优先处理

1. 按 Capri Mk I、Mk II、Mk III 聚类，单独核对 RS 2600 与 2.8 I Turbo 是否因宽体或外部套件建立独立尺寸组。
2. 随后一次闭合 Consul Sedan、Coupe、Wagon 三种车身，并批量复用到对应 Ktype。
3. 再处理 Cougar、Courier、Econovan 与 Ecosport 车型组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-c-max-ii-2.0-duratorq-tdci-140hp-dpf-19811?utm_source=chatgpt.com "Ford C-MAX II 2.0 Duratorq TDCi (140 Hp) DPF | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2015/1596710/ford_c-max_energi.html?utm_source=chatgpt.com "2015 Ford C-Max Energi Specs Review (140.2 kW / 191 PS / 188 hp) (for North America )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Consul Mk I 的 Sedan、Coupe、Wagon 三个尺寸组，并关联本批全部 16 个 Consul Ktype。三种车身共用 1791 mm 不含后视镜宽度，但长度和高度不同。([汽车目录][1])
* 首次闭合欧洲版 Cougar 三门 Coupe 尺寸组，并关联 2 个 Ktype。([汽车目录][2])
* 首次闭合 Escort Classic 五门 Hatchback 和 Classic Turnier 五门 Wagon 两个尺寸组，并关联 4 个 Ktype。([汽车目录][3])

## 当前批次进度

* READY 输入 Ktype：63 / 100
* READY 映射行：81
* PENDING 输入 Ktype：37
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6592	6592	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6596	6596	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6599	6599	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14950	14950	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
14951	14951	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14952	14952	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6593	6593	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6594	6594	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6597	6597	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6600	6600	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
6595	6595	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6598	6598	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6601	6601	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
15169	15169	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
15170	15170	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
15172	15172	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14592	14592	Coupe	Cougar I		3	EU-FORD-COUGAR-I-COUPE-01	HIGH	欧洲版三门掀背轿跑车身。	READY
15441	15441	Coupe	Cougar I		3	EU-FORD-COUGAR-I-COUPE-01	HIGH	欧洲版三门掀背轿跑车身。	READY
15373	15373	Hatchback	Escort Mk VI Classic		5	EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	HIGH	五门Classic掀背车身。	READY
15372	15372	Hatchback	Escort Mk VI Classic		5	EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	HIGH	五门Classic掀背车身。	READY
15374	15374	Wagon	Escort Mk VI Classic	ANL	5	EU-FORD-ESCORT-CLASSIC-WAGON-01	HIGH	Classic Turnier五门旅行车身。	READY
15375	15375	Wagon	Escort Mk VI Classic	ANL	5	EU-FORD-ESCORT-CLASSIC-WAGON-01	HIGH	Classic Turnier五门旅行车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-CONSUL-MK-I-SEDAN-01	4572	1791	1369	Automobile-Catalog 1972 Ford Consul 2500 L specifications	https://www.automobile-catalog.com/car/1972/916970/ford_consul_2500_l.html
EU-FORD-CONSUL-MK-I-COUPE-01	4572	1791	1341	Automobile-Catalog 1972 Ford Consul 1700 L Coupe specifications	https://www.automobile-catalog.com/car/1972/915140/ford_consul_1700_l_2tur_.html
EU-FORD-CONSUL-MK-I-WAGON-01	4674	1791	1410	Automobile-Catalog 1972 Ford Consul Estate 2500 L specifications	https://www.automobile-catalog.com/car/1972/917570/ford_consul_estate_2500_l.html
EU-FORD-COUGAR-I-COUPE-01	4699	1780	1346	Automobile-Catalog 1999 Ford Cougar 24V V6 Europe specifications	https://www.automobile-catalog.com/car/1999/958235/ford_cougar_24v_v6.html
EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	4136	1691	1398	Automobile-Catalog 1998 Ford Escort 1.8 TD Classic specifications	https://www.automobile-catalog.com/car/1998/953525/ford_escort_1_8_td_classic.html
EU-FORD-ESCORT-CLASSIC-WAGON-01	4300	1700	1416	Automobile-Catalog 1998 Ford Escort Turnier 1.8 TD Classic specifications	https://www.automobile-catalog.com/car/1998/953540/ford_escort_turnier_1_8_td_classic.html
```

## 下一步优先处理

1. 闭合 Capri Mk I、Mk II、Mk III，并单独处理 RS 2600、Turbo及跨改款 Ktype。
2. 批量处理 Courier、Econovan和 EcoSport。
3. 最后闭合 Escort I至IV剩余 Sedan、Wagon及 Hatchback 门数分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/916970/ford_consul_2500_l.html?utm_source=chatgpt.com "1972 Ford Consul 2500 L Specs Review (88 kW / 120 PS / 118 hp) (since mid-year 1972 for Europe )"
[2]: https://www.automobile-catalog.com/car/1999/958235/ford_cougar_24v_v6.html?utm_source=chatgpt.com "1999 Ford Cougar 24V (V6) Specs Review (125 kW / 170 PS / 168 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1998/953525/ford_escort_1_8_td_classic.html?utm_source=chatgpt.com "1998 Ford Escort 1.8 TD Classic Specs Review (66 kW ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 首次闭合 Escort Mk I 标准轿车与 Escort Mk II Turnier 旅行车尺寸组，并关联 5 个 Ktype。对应外廓分别为 `3978 × 1572 × 1402 mm` 和 `4056 × 1564 × 1414 mm`。([汽车目录][1])
* 首次闭合 Escort Mk III RS 1600i 三门车身与 Escort Mk IV 标准掀背车身尺寸组，并关联 2 个 Ktype。对应外廓分别为 `4052 × 1640 × 1350 mm` 和 `4022 × 1640 × 1385 mm`。([汽车目录][2])
* Courier、Econovan、Capri 与 EcoSport 本轮未创建猜测性尺寸组，继续保留待处理。

## 当前批次进度

* READY 输入 Ktype：70 / 100
* READY 映射行：88
* PENDING 输入 Ktype：30
* 已确认尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15244	15244	Sedan	Escort Mk I			EU-FORD-ESCORT-MK-I-SEDAN-01	MEDIUM	输入未区分两门或四门；使用标准轿车外廓。	READY
15245	15245	Sedan	Escort Mk I			EU-FORD-ESCORT-MK-I-SEDAN-01	MEDIUM	输入未区分两门或四门；使用标准轿车外廓。	READY
15252	15252	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
15253	15253	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
14954	14954	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
14953	14953	Hatchback	Escort Mk III	GAA	3	EU-FORD-ESCORT-MK-III-RS-HATCHBACK-01	HIGH	RS 1600i三门外廓。	READY
6050	6050	Hatchback	Escort Mk IV			EU-FORD-ESCORT-MK-IV-HATCHBACK-01	MEDIUM	标准三门与五门掀背外廓一致；输入未区分门数。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-MK-I-SEDAN-01	3978	1572	1402	Automobile-Catalog 1969 Ford Escort 1300 specifications	https://www.automobile-catalog.com/car/1969/909560/ford_escort_1300.html
EU-FORD-ESCORT-MK-II-WAGON-01	4056	1564	1414	Automobile-Catalog 1976 Ford Escort Turnier 1300 L specifications	https://www.automobile-catalog.com/car/1976/919865/ford_escort_turnier_1300_l.html
EU-FORD-ESCORT-MK-III-RS-HATCHBACK-01	4052	1640	1350	Automobile-Catalog 1983 Ford Escort RS 1600i specifications	https://www.automobile-catalog.com/car/1983/928955/ford_escort_rs_1600i.html
EU-FORD-ESCORT-MK-IV-HATCHBACK-01	4022	1640	1385	Automobile-Catalog 1989 Ford Escort 1.6 GL specifications	https://www.automobile-catalog.com/car/1989/942230/ford_escort_1_6_gl.html
```

## 下一步优先处理

1. 集中拆分 Capri Mk I、Mk II、Mk III，以及 RS 2600、Turbo 和跨代 Ktype。
2. 闭合 Courier Van、Courier Pickup 与 Econovan 的独立物理车身。
3. 最后处理 EcoSport 改款前后外廓和剩余 Escort III 普通掀背车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1969/909560/ford_escort_1300.html?utm_source=chatgpt.com "1969 Ford Escort 1300 Specs Review (38 kW / 52 PS ..."
[2]: https://www.automobile-catalog.com/car/1983/928955/ford_escort_rs_1600i.html?utm_source=chatgpt.com "1983 Ford Escort RS 1600i (man. 5) (model up to mid-year ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 首次闭合 **Capri Mk I 改款前、Mk I 改款后、Capri II 改款前、Capri II 改款后** 四个标准车身尺寸组。
* 对跨越改款周期的 Ktype 拆分 `prefl` 和 `facelift` 派生行；同阶段发动机版本直接复用对应尺寸组。
* Capri Mk I 改款前标准车身为 `4262 × 1645 × 1330 mm`，改款后为 `4313 × 1646 × 1352 mm`。Capri II 早期车身为 `4288 × 1698 × 1357 mm`，后期车身为 `4305 × 1698 × 1357 mm`。([汽车目录][1])
* RS 2600、Capri III 标准版本及 2.8 I Turbo 尚未在本轮建组，避免混用宽体、扰流套件或不同保险杠外廓。

## 当前批次进度

* READY 输入 Ktype：81 / 100
* READY 映射行：104
* PENDING 输入 Ktype：19
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11162_prefl	11162	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
11162_facelift	11162	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
14948_prefl	14948	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
14948_facelift	14948	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
11027_prefl	11027	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
11027_facelift	11027	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
15152_prefl	15152	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款前外廓。	READY
15152_facelift	15152	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款后外廓。	READY
15153	15153	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
15154	15154	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
15155	15155	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	Mk I改款前双门快背车身。	READY
15159_prefl	15159	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款前外廓。	READY
15159_facelift	15159	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款后外廓。	READY
11025	11025	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
14942	14942	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
11026	11026	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	4288	1698	1357	Automobile-Catalog 1974 Ford Capri II 1300 XL specifications	https://www.automobile-catalog.com/car/1974/918890/ford_capri_ii_1300_xl.html
EU-FORD-CAPRI-II-FACELIFT-COUPE-01	4305	1698	1357	Automobile-Catalog 1976 Ford Capri II 1300 L specifications	https://www.automobile-catalog.com/car/1976/918965/ford_capri_ii_1300_l.html
EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	4262	1645	1330	Automobile-Catalog 1970 Ford Capri 1300 specifications	https://www.automobile-catalog.com/car/1970/910145/ford_capri_1300.html
EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	4313	1646	1352	Automobile-Catalog 1973 Ford Capri 1600 XL specifications	https://www.automobile-catalog.com/car/1973/910460/ford_capri_1600_xl.html
```

## 下一步优先处理

1. 独立闭合 Capri III 普通车身、S/扰流外廓与宽体 2.8 I Turbo。
2. 拆分 RS 2600 改款前后低悬架及轮拱外廓。
3. 闭合 Courier Van、Courier Pickup、Econovan 和 EcoSport；最后处理剩余 Escort II、Escort III。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1969/910145/ford_capri_1300.html?utm_source=chatgpt.com "1969 Ford Capri 1300 Specs Review (37 kW / 50 PS / ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5301-5400_ktype_dimension_mapping_final.tsv
- left18448_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 Capri III 标准车身、Turbo 宽体及 RS 2600 改款前后尺寸组，并完成相关派生映射。([汽车目录][1])
* 已闭合 Courier Pickup、Courier Van 与 Econovan KAA 尺寸组。([Fichas Completas][2])
* 已闭合 EcoSport II 改款前后，以及剩余 Escort II、Escort III 尺寸组。([汽车目录][3])
* 已完成机械检查：表头固定、129 个 `id` 唯一、30 个尺寸组唯一、全部映射引用闭合，无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射行：129
* PENDING：0
* DIMENSION_GROUP：30
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11162_prefl	11162	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
11162_facelift	11162	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
14257	14257	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH	1.3标准三门车身。	READY
14948_prefl	14948	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
14948_facelift	14948	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
11027_prefl	11027	Coupe	Capri II pre-facelift		3	EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款前外廓。	READY
11027_facelift	11027	Coupe	Capri II facelift		3	EU-FORD-CAPRI-II-FACELIFT-COUPE-01	HIGH	跨越Capri II改款，改款后外廓。	READY
14949	14949	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH	2.0标准三门车身。	READY
15164	15164	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH	2.0标准三门车身。	READY
14947	14947	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH	3.0 S工厂配置；最大三维与标准车身一致。	READY
15152_prefl	15152	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款前外廓。	READY
15152_facelift	15152	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款后外廓。	READY
15153	15153	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
15154	15154	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
15155	15155	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	Mk I改款前双门快背车身。	READY
15159_prefl	15159	Coupe	Capri Mk I pre-facelift		2	EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款前外廓。	READY
15159_facelift	15159	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	跨越Mk I改款，改款后外廓。	READY
11025	11025	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
14942	14942	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
11026	11026	Coupe	Capri Mk I facelift		2	EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	HIGH	Mk I改款后双门快背车身。	READY
15165	15165	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-TURBO-WIDEBODY-COUPE-01	HIGH	2.8 i Turbo宽体外廓。	READY
11024_prefl	11024	Coupe	Capri RS 2600 pre-facelift		2	EU-FORD-CAPRI-RS2600-PREFACELIFT-COUPE-01	HIGH	跨越Mk I改款，RS 2600改款前低车身外廓。	READY
11024_facelift	11024	Coupe	Capri RS 2600 facelift		2	EU-FORD-CAPRI-RS2600-FACELIFT-COUPE-01	HIGH	跨越Mk I改款，RS 2600改款后低车身外廓。	READY
159788	159788	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
159790	159790	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
164017	164017	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
159789	159789	SUV	Capri EV		5	EU-FORD-CAPRI-EV-SUV-01	HIGH	五门SUV车身；后驱与四驱外廓一致。	READY
113250	113250	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
10288	10288	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
56757_prefl	56757	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
56757_facelift	56757	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
56760_prefl	56760	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
56760_facelift	56760	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
108790_prefl	108790	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108790_facelift	108790	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108791_prefl	108791	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108791_facelift	108791	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
145790	145790	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
145827	145827	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111749	111749	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111753	111753	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113252	113252	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
113253	113253	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
111755	111755	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111765	111765	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111764	111764	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113264	113264	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
108792_prefl	108792	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108792_facelift	108792	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
142731_prefl	142731	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
142731_facelift	142731	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
11922_prefl	11922	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
11922_facelift	11922	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
55512_prefl	55512	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
55512_facelift	55512	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
106025_prefl	106025	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
106025_facelift	106025	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
11895	11895	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
108814_prefl	108814	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108814_facelift	108814	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108815_prefl	108815	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108815_facelift	108815	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
14793_prefl	14793	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
14793_facelift	14793	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
113147_prefl	113147	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
113147_facelift	113147	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
142729_prefl	142729	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
142729_facelift	142729	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
118794	118794	MPV	C-MAX II Energi		5	EU-FORD-C-MAX-II-ENERGI-MPV-01	HIGH	北美版插电混动车身外廓。	READY
10196_prefl	10196	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	跨越2015改款，改款前外廓。	READY
10196_facelift	10196	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	跨越2015改款，改款后外廓。	READY
11894	11894	MPV	C-MAX I facelift		5	EU-FORD-C-MAX-I-FACELIFT-MPV-01	HIGH	2007改款五门MPV。	READY
108816_prefl	108816	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108816_facelift	108816	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108817_prefl	108817	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108817_facelift	108817	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
108818_prefl	108818	MPV	C-MAX II pre-facelift		5	EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款前外廓。	READY
108818_facelift	108818	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记；跨越2015改款，改款后外廓。	READY
111766	111766	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
111767	111767	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	2015改款五门MPV。	READY
113287	113287	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
113292	113292	MPV	C-MAX II facelift		5	EU-FORD-C-MAX-II-FACELIFT-MPV-01	HIGH	货运登记不改变五门车身外廓。	READY
6592	6592	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6596	6596	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6599	6599	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14950	14950	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
14951	14951	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14952	14952	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6593	6593	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6594	6594	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6597	6597	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6600	6600	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
6595	6595	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
6598	6598	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
6601	6601	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
15169	15169	Sedan	Consul Mk I			EU-FORD-CONSUL-MK-I-SEDAN-01	HIGH	两门与四门轿车共用外廓；输入未区分门数。	READY
15170	15170	Coupe	Consul Mk I		2	EU-FORD-CONSUL-MK-I-COUPE-01	HIGH	双门快背轿跑车身。	READY
15172	15172	Wagon	Consul Mk I		5	EU-FORD-CONSUL-MK-I-WAGON-01	HIGH	五门旅行车车身。	READY
14592	14592	Coupe	Cougar I		3	EU-FORD-COUGAR-I-COUPE-01	HIGH	欧洲版三门掀背轿跑车身。	READY
15441	15441	Coupe	Cougar I		3	EU-FORD-COUGAR-I-COUPE-01	HIGH	欧洲版三门掀背轿跑车身。	READY
121499	121499	Pickup	Courier Brazil		2	EU-FORD-COURIER-BRAZIL-PICKUP-01	HIGH	巴西版双门单排小型皮卡外廓。	READY
5742	5742	Van	Courier Europe			EU-FORD-COURIER-EUROPE-VAN-01	HIGH	Fiesta平台厢式车外廓。	READY
15829	15829	Van	Courier Europe			EU-FORD-COURIER-EUROPE-VAN-01	HIGH	Fiesta平台厢式车外廓。	READY
11095	11095	Van	Econovan KAA	KAA		EU-FORD-ECONOVAN-KAA-VAN-01	HIGH	KAA厢式车身；发动机差异不改变外廓。	READY
11096	11096	Van	Econovan KAA	KAA		EU-FORD-ECONOVAN-KAA-VAN-01	HIGH	KAA厢式车身；发动机差异不改变外廓。	READY
38703_prefl	38703	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	跨越2017改款，改款前外廓。	READY
38703_facelift	38703	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	跨越2017改款，改款后外廓。	READY
118620_prefl	118620	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	跨越2017改款，改款前外廓。	READY
118620_facelift	118620	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	跨越2017改款，改款后外廓。	READY
113168_prefl	113168	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	跨越2017改款，改款前外廓。	READY
113168_facelift	113168	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	跨越2017改款，改款后外廓。	READY
39881	39881	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	90 PS版本止于2017改款前外廓。	READY
119943_prefl	119943	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	跨越2017改款，改款前外廓。	READY
119943_facelift	119943	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	跨越2017改款，改款后外廓。	READY
39840_prefl	39840	SUV	EcoSport II pre-facelift		5	EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	HIGH	跨越2017改款，改款前外廓。	READY
39840_facelift	39840	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	跨越2017改款，改款后外廓。	READY
15373	15373	Hatchback	Escort Mk VI Classic		5	EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	HIGH	五门Classic掀背车身。	READY
15372	15372	Hatchback	Escort Mk VI Classic		5	EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	HIGH	五门Classic掀背车身。	READY
15374	15374	Wagon	Escort Mk VI Classic	ANL	5	EU-FORD-ESCORT-CLASSIC-WAGON-01	HIGH	Classic Turnier五门旅行车身。	READY
15375	15375	Wagon	Escort Mk VI Classic	ANL	5	EU-FORD-ESCORT-CLASSIC-WAGON-01	HIGH	Classic Turnier五门旅行车身。	READY
15244	15244	Sedan	Escort Mk I			EU-FORD-ESCORT-MK-I-SEDAN-01	MEDIUM	输入未区分两门或四门；使用标准轿车外廓。	READY
15245	15245	Sedan	Escort Mk I			EU-FORD-ESCORT-MK-I-SEDAN-01	MEDIUM	输入未区分两门或四门；使用标准轿车外廓。	READY
125814	125814	Sedan	Escort Mk II	ATH		EU-FORD-ESCORT-MK-II-SEDAN-01	HIGH	ATH轿车；两门与四门共用外廓，输入未区分门数。	READY
15252	15252	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
15253	15253	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
14954	14954	Wagon	Escort Mk II		3	EU-FORD-ESCORT-MK-II-WAGON-01	HIGH	三门Turnier旅行车身。	READY
10223	10223	Hatchback	Escort Mk III	GAA		EU-FORD-ESCORT-MK-III-HATCHBACK-01	HIGH	GAA标准掀背车身；输入未区分门数。	READY
14953	14953	Hatchback	Escort Mk III	GAA	3	EU-FORD-ESCORT-MK-III-RS-HATCHBACK-01	HIGH	RS 1600i三门外廓。	READY
6050	6050	Hatchback	Escort Mk IV			EU-FORD-ESCORT-MK-IV-HATCHBACK-01	MEDIUM	标准三门与五门掀背外廓一致；输入未区分门数。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5301-5400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-CAPRI-II-PREFACELIFT-COUPE-01	4288	1698	1357	Automobile-Catalog 1974 Ford Capri II 1300 XL specifications	https://www.automobile-catalog.com/car/1974/918890/ford_capri_ii_1300_xl.html
EU-FORD-CAPRI-II-FACELIFT-COUPE-01	4305	1698	1357	Automobile-Catalog 1976 Ford Capri II 1300 L specifications	https://www.automobile-catalog.com/car/1976/918965/ford_capri_ii_1300_l.html
EU-FORD-CAPRI-III-COUPE-01	4376	1698	1323	Automobile-Catalog 1983 Ford Capri 1.6 L specifications	https://www.automobile-catalog.com/car/1983/927380/ford_capri_1_6_l.html
EU-FORD-CAPRI-MK-I-PREFACELIFT-COUPE-01	4262	1645	1330	Automobile-Catalog 1970 Ford Capri 1300 specifications	https://www.automobile-catalog.com/car/1970/910145/ford_capri_1300.html
EU-FORD-CAPRI-MK-I-FACELIFT-COUPE-01	4313	1646	1352	Automobile-Catalog 1973 Ford Capri 1600 XL specifications	https://www.automobile-catalog.com/car/1973/910460/ford_capri_1600_xl.html
EU-FORD-CAPRI-III-TURBO-WIDEBODY-COUPE-01	4439	1780	1323	Automobile-Catalog 1981 Ford Capri Turbo specifications	https://www.automobile-catalog.com/car/1981/41870/ford_capri_turbo.html
EU-FORD-CAPRI-RS2600-PREFACELIFT-COUPE-01	4186	1646	1263	Automobile-Catalog 1971 Ford Capri RS 2600 specifications	https://www.automobile-catalog.com/car/1971/910385/ford_capri_rs_2600.html
EU-FORD-CAPRI-RS2600-FACELIFT-COUPE-01	4240	1672	1283	Automobile-Catalog 1972 Ford Capri RS 2600 specifications	https://www.automobile-catalog.com/car/1972/910565/ford_capri_rs_2600.html
EU-FORD-CAPRI-EV-SUV-01	4634	1872	1626	Ford Capri detailed specification	https://www.fordpers.be/content/documents/news/2024/2024fordcapri_factsheet_eu.pdf
EU-FORD-C-MAX-I-FACELIFT-MPV-01	4372	1825	1588	Ford C-MAX UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf
EU-FORD-C-MAX-II-PREFACELIFT-MPV-01	4380	1828	1626	Auto-Data Ford C-MAX II 2.0 Duratorq TDCi specifications	https://www.auto-data.net/en/ford-c-max-ii-2.0-duratorq-tdci-140hp-dpf-19811
EU-FORD-C-MAX-II-FACELIFT-MPV-01	4379	1828	1610	Ford C-MAX + Grand C-MAX brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf
EU-FORD-C-MAX-II-ENERGI-MPV-01	4409	1828	1623	Automobile-Catalog 2015 Ford C-Max Energi specifications	https://www.automobile-catalog.com/car/2015/1596710/ford_c-max_energi.html
EU-FORD-CONSUL-MK-I-SEDAN-01	4572	1791	1369	Automobile-Catalog 1972 Ford Consul 2500 L specifications	https://www.automobile-catalog.com/car/1972/916970/ford_consul_2500_l.html
EU-FORD-CONSUL-MK-I-COUPE-01	4572	1791	1341	Automobile-Catalog 1972 Ford Consul 1700 L Coupe specifications	https://www.automobile-catalog.com/car/1972/915140/ford_consul_1700_l_2tur_.html
EU-FORD-CONSUL-MK-I-WAGON-01	4674	1791	1410	Automobile-Catalog 1972 Ford Consul Estate 2500 L specifications	https://www.automobile-catalog.com/car/1972/917570/ford_consul_estate_2500_l.html
EU-FORD-COUGAR-I-COUPE-01	4699	1780	1346	Automobile-Catalog 1999 Ford Cougar 24V V6 Europe specifications	https://www.automobile-catalog.com/car/1999/958235/ford_cougar_24v_v6.html
EU-FORD-COURIER-BRAZIL-PICKUP-01	4457	1685	1477	Ficha Completa 2008 Ford Courier XL 1.6 specifications	https://www.fichacompleta.com.br/en/carros/ford/courier-xl-1-6-2008
EU-FORD-COURIER-EUROPE-VAN-01	4115	1650	1835	IKZ Haustechnik Ford Courier exterior dimensions	https://www.ikz.de/ikz-archiv/1999/22/9922056.php
EU-FORD-ECONOVAN-KAA-VAN-01	4030	1630	1820	Drive.Place Ford Econovan II 1.4 specifications	https://ford.drive.place/econovan/ii/group_minivan/722249
EU-FORD-ECOSPORT-II-PREFACELIFT-SUV-01	4273	1765	1648	Automobile-Catalog 2014 Ford EcoSport 1.5 TDCi specifications	https://www.automobile-catalog.com/car/2014/2044130/ford_ecosport_1_5_tdci_90.html
EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	4096	1765	1653	Automoli Ford EcoSport II facelift technical data	https://www.automoli.com/us/vehicles/ford/ecosport/ecosport-ii-facelift-2017-5825/
EU-FORD-ESCORT-CLASSIC-HATCHBACK-01	4136	1691	1398	Automobile-Catalog 1998 Ford Escort 1.8 TD Classic specifications	https://www.automobile-catalog.com/car/1998/953525/ford_escort_1_8_td_classic.html
EU-FORD-ESCORT-CLASSIC-WAGON-01	4300	1700	1416	Automobile-Catalog 1998 Ford Escort Turnier 1.8 TD Classic specifications	https://www.automobile-catalog.com/car/1998/953540/ford_escort_turnier_1_8_td_classic.html
EU-FORD-ESCORT-MK-I-SEDAN-01	3978	1572	1402	Automobile-Catalog 1969 Ford Escort 1300 specifications	https://www.automobile-catalog.com/car/1969/909560/ford_escort_1300.html
EU-FORD-ESCORT-MK-II-SEDAN-01	3978	1596	1398	Automobile-Catalog 1979 Ford Escort 1600 GL specifications	https://www.automobile-catalog.com/car/1979/941015/ford_escort_1600_gl.html
EU-FORD-ESCORT-MK-II-WAGON-01	4056	1564	1414	Automobile-Catalog 1976 Ford Escort Turnier 1300 L specifications	https://www.automobile-catalog.com/car/1976/919865/ford_escort_turnier_1300_l.html
EU-FORD-ESCORT-MK-III-HATCHBACK-01	3970	1640	1384	Automobile-Catalog 1985 Ford Escort 1.6 L specifications	https://www.automobile-catalog.com/car/1985/928700/ford_escort_1_6_l.html
EU-FORD-ESCORT-MK-III-RS-HATCHBACK-01	4052	1640	1350	Automobile-Catalog 1983 Ford Escort RS 1600i specifications	https://www.automobile-catalog.com/car/1983/928955/ford_escort_rs_1600i.html
EU-FORD-ESCORT-MK-IV-HATCHBACK-01	4022	1640	1385	Automobile-Catalog 1989 Ford Escort 1.6 GL specifications	https://www.automobile-catalog.com/car/1989/942230/ford_escort_1_6_gl.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5301-5400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1983/927380/ford_capri_1_6_l.html "https://www.automobile-catalog.com/car/1983/927380/ford_capri_1_6_l.html"
[2]: https://www.fichacompleta.com.br/en/carros/ford/courier-xl-1-6-2008 "https://www.fichacompleta.com.br/en/carros/ford/courier-xl-1-6-2008"
[3]: https://www.automobile-catalog.com/car/2014/2044130/ford_ecosport_1_5_tdci_90.html "https://www.automobile-catalog.com/car/2014/2044130/ford_ecosport_1_5_tdci_90.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1240 行）
- 累计尺寸组：dimension_groups_final.tsv（319 行）

