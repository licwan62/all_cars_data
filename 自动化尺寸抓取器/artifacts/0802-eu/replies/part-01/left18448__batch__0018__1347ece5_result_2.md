# 任务：left18448 第 1701-1800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0018__1347ece5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1701-1800 行

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
left18448 第 1701-1800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1701-1800_ktype_dimension_mapping_final.tsv
- left18448_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-01	4360	1748	1423
EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421
EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430
EU-BMW-1-SERIES-E88-CONVERTIBLE-01	4360	1748	1411
EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421
EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421
EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	4361	1800	1459

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110051
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110075
BMW	1	120 D	Coupe	Heckantrieb	Diesel	Sep 2007	Oct 2013	122022
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Dec 2011	124739
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jun 2004	Feb 2007	124781
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	147590
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	147594
BMW	1	120 D Mild-hybrid	Schrägheck	Frontantrieb	Diesel/Elektro	Jul 2024	-	800020
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Nov 2012	Feb 2015	57466
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Feb 2012	Feb 2015	58374
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Nov 2012	Feb 2015	100887
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Jan 2012	Feb 2015	100888
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2019	110052
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2019	110078
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2019	147586
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2019	147588
BMW	1	120 I	Cabriolet	Heckantrieb	Benzin	Mar 2008	Dec 2013	55639
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Jun 2004	Feb 2007	58188
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Mar 2007	Jun 2011	58218
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Mar 2007	Jun 2011	58221
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Mar 2007	Jun 2011	58224
BMW	1	120 I	Coupe	Heckantrieb	Benzin	Sep 2009	Oct 2013	59307
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2019	110044
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2016	110062
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	Jun 2019	120226
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	Jun 2019	120240
BMW	1	120 Mild-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2024	-	800016
BMW	1	123 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Jun 2011	58304
BMW	1	123 Xdrive Mild-hybrid	Schrägheck	Allrad	Benzin/Elektro	Nov 2024	-	800868
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	Mar 2012	Feb 2015	16996
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	Dec 2011	May 2019	58375
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	Dec 2011	Feb 2015	58376
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	May 2019	110055
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110080
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	Dec 2011	Dec 2019	58356
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	Mar 2012	Nov 2017	100889
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	Mar 2013	Jun 2019	100892
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	Oct 2015	Jun 2019	120229
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	Jun 2019	120242
BMW	1	128 I	Cabriolet	Heckantrieb	Benzin	Dec 2007	Oct 2013	50120
BMW	1	130 I	Schrägheck	Heckantrieb	Benzin	Sep 2006	Dec 2011	18560
BMW	1	130 I	Schrägheck	Heckantrieb	Benzin	Mar 2007	Jun 2011	58233
BMW	1	130 I	Schrägheck	Heckantrieb	Benzin	Sep 2005	Feb 2007	58238
BMW	1	135 I	Cabriolet	Heckantrieb	Benzin	Mar 2008	Dec 2013	55640
BMW	1	M 135 I	Schrägheck	Heckantrieb	Benzin	Jul 2012	Feb 2015	56734
BMW	1	M 135 I	Schrägheck	Heckantrieb	Benzin	Dec 2011	Jun 2016	58358
BMW	1	M 135 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2016	110046
BMW	1	M 135 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2016	110066
BMW	1	M 135 I Xdrive	Schrägheck	Allrad	Benzin	Nov 2012	Feb 2015	56735
BMW	1	M 135 I Xdrive	Schrägheck	Allrad	Benzin	Feb 2012	Jun 2016	58361
BMW	1	M 135 I Xdrive	Schrägheck	Allrad	Benzin	Mar 2015	Jun 2016	110047
BMW	1	M 135 I Xdrive	Schrägheck	Allrad	Benzin	Mar 2015	Jun 2016	110070
BMW	1	M 135 Xdrive	Schrägheck	Allrad	Benzin	Jul 2024	-	800018
BMW	1	M 140 I	Schrägheck	Heckantrieb	Benzin	Oct 2015	Jun 2019	120235
BMW	1	M 140 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	Jun 2019	120244
BMW	1	M 140 I Xdrive	Schrägheck	Allrad	Benzin	Sep 2015	Jun 2019	120236
BMW	1	M 140 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2016	Jun 2019	120245
BMW	2	216	Coupe	Frontantrieb	Benzin	Mar 2025	-	160684
BMW	2	218	Coupe	Frontantrieb	Benzin	Nov 2024	-	161092
BMW	2	220	Coupe	Frontantrieb	Benzin/Elektro	Nov 2024	-	160034
BMW	2	214 D	Großraumlimousine	Frontantrieb	Diesel	Jul 2014	Feb 2018	110022
BMW	2	214 D	Großraumlimousine	Frontantrieb	Diesel	Jul 2015	Feb 2018	113400
BMW	2	216 D	Großraumlimousine	Frontantrieb	Diesel	Mar 2014	Oct 2021	107975
BMW	2	216 D	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	-	111075
BMW	2	216 I	Großraumlimousine	Frontantrieb	Benzin	Jul 2015	Feb 2018	113399
BMW	2	216 I	Großraumlimousine	Frontantrieb	Benzin	Feb 2015	Feb 2018	116775
BMW	2	216i	Großraumlimousine	Frontantrieb	Benzin	Nov 2022	-	150697
BMW	2	218 D	Coupe	Heckantrieb	Diesel	Mar 2014	Jun 2015	100823
BMW	2	218 D	Großraumlimousine	Frontantrieb	Diesel	Nov 2013	Oct 2021	107547
BMW	2	218 D	Großraumlimousine	Frontantrieb	Diesel	Jul 2014	-	111076
BMW	2	218 D	Coupe	Heckantrieb	Diesel	Jul 2015	Sep 2020	113347
BMW	2	218 D	Cabriolet	Heckantrieb	Diesel	Jul 2015	Sep 2020	113349
BMW	2	218 D	Großraumlimousine	Frontantrieb	Diesel	Nov 2013	Oct 2021	116624
BMW	2	218 D	Großraumlimousine	Frontantrieb	Diesel	Jul 2014	-	116629
BMW	2	218 D	Coupe	Heckantrieb	Diesel	Mar 2014	Sep 2020	116638
BMW	2	218 D	Cabriolet	Heckantrieb	Diesel	Jul 2015	Sep 2020	116642
BMW	2	218 D	Coupe	Frontantrieb	Diesel	Nov 2024	-	160040
BMW	2	218 D Xdrive	Großraumlimousine	Allrad	Diesel	Dec 2014	Oct 2021	117593
BMW	2	218 D Xdrive	Großraumlimousine	Allrad	Diesel	Dec 2014	Oct 2021	117596
BMW	2	218 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2015	-	118972
BMW	2	218 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2015	-	119028
BMW	2	218 I	Großraumlimousine	Frontantrieb	Benzin	Jul 2014	Oct 2021	105893
BMW	2	218 I	Coupe	Heckantrieb	Benzin	Mar 2015	Jun 2021	109511
BMW	2	218 I	Cabriolet	Heckantrieb	Benzin	Mar 2015	Jun 2021	109519
BMW	2	218 I	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	-	111073
BMW	2	218 I	Großraumlimousine	Frontantrieb	Benzin	Apr 2017	-	128113
BMW	2	218 I	Cabriolet	Heckantrieb	Benzin	Nov 2020	Jun 2021	147602
BMW	2	218 I	Coupe	Heckantrieb	Benzin	Jul 2022	-	148077
BMW	2	218 I	Coupe	Heckantrieb	Benzin	Nov 2020	Jun 2021	801700
BMW	2	218d	Großraumlimousine	Frontantrieb	Diesel	Nov 2021	-	145860
BMW	2	218d	Großraumlimousine	Frontantrieb	Diesel	Jun 2022	-	148030
BMW	2	218i	Großraumlimousine	Frontantrieb	Benzin	Nov 2021	-	145854
BMW	2	220 D	Coupe	Heckantrieb	Diesel	Oct 2013	Jun 2017	58284
BMW	2	220 D	Coupe	Heckantrieb	Diesel	Oct 2012	Nov 2014	100890
BMW	2	220 D	Coupe	Heckantrieb	Diesel	Mar 2014	Sep 2020	107961
BMW	2	220 D	Großraumlimousine	Frontantrieb	Diesel	Mar 2014	Oct 2021	107976
BMW	2	220 D	Cabriolet	Heckantrieb	Diesel	Mar 2014	Sep 2020	108001
BMW	2	220 D	Großraumlimousine	Frontantrieb	Diesel	Sep 2014	-	113402
BMW	2	220 D	Großraumlimousine	Frontantrieb	Diesel	Mar 2014	Oct 2021	116625
BMW	2	220 D	Großraumlimousine	Frontantrieb	Diesel	Sep 2014	-	116630


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖全部 **100 个输入 Ktype**；跨改款 Ktype 按物理外廓拆分，共生成 **123 条映射**。
* 复用已有尺寸组 10 个，首次建立 BMW 1 Series M Performance 与 BMW 2 Series 各车身尺寸组 13 个。
* F20/F21 M Performance 未复用普通 F20/F21 尺寸：BMW 官方技术数据表明其改款前、改款后外廓存在独立尺寸边界。([宝马集团新闻][1])
* 两表已通过列数、主键唯一、引用闭合、尺寸正整数、来源非空及孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：123
* PENDING 映射：0
* 当前引用尺寸组：23
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
110051	110051	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110075	110075	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
122022	122022	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-01	HIGH	E82双门Coupe外廓。	READY
124739	124739	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
124781	124781	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
147590	147590	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
147594	147594	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
800020	800020	Hatchback	1 Series IV	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
57466	57466	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58374	58374	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
100887	100887	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
100888	100888	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110052	110052	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110078	110078	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
147586	147586	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
147588	147588	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
55639	55639	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
58188	58188	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
58218	58218	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58221	58221	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58224	58224	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
59307	59307	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-01	HIGH	E82双门Coupe外廓。	READY
110044	110044	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110062	110062	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
120226	120226	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
120240	120240	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
800016	800016	Hatchback	1 Series IV	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
58304	58304	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
800868	800868	Hatchback	1 Series IV	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
16996	16996	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58375_prefl	58375	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨F21改款，改款前外廓。	READY
58375_facelift	58375	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨F21改款，改款后外廓。	READY
58376	58376	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110055	110055	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110080	110080	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
58356_prefl	58356	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨F21改款，改款前外廓。	READY
58356_facelift	58356	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨F21改款，改款后外廓。	READY
100889_prefl	100889	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨F20改款，改款前外廓。	READY
100889_facelift	100889	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨F20改款，改款后外廓。	READY
100892_prefl	100892	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨F21改款，改款前外廓。	READY
100892_facelift	100892	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨F21改款，改款后外廓。	READY
120229	120229	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
120242	120242	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
50120	50120	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
18560	18560	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58233	58233	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58238	58238	Hatchback	1 Series I	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
55640	55640	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
56734	56734	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-PREFL-01	HIGH	F20 M Performance五门改款前外廓。	READY
58358_prefl	58358	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-PREFL-01	HIGH	Ktype跨F21 M Performance改款，改款前外廓。	READY
58358_facelift	58358	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	Ktype跨F21 M Performance改款，改款后外廓。	READY
110046	110046	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	F21 M Performance三门改款外廓。	READY
110066	110066	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-FACELIFT-01	HIGH	F20 M Performance五门改款外廓。	READY
56735	56735	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-PREFL-01	HIGH	F20 M Performance五门改款前外廓。	READY
58361_prefl	58361	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-PREFL-01	HIGH	Ktype跨F21 M Performance改款，改款前外廓。	READY
58361_facelift	58361	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	Ktype跨F21 M Performance改款，改款后外廓。	READY
110047	110047	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	F21 M Performance三门改款外廓。	READY
110070	110070	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-FACELIFT-01	HIGH	F20 M Performance五门改款外廓。	READY
800018	800018	Hatchback	1 Series IV	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
120235	120235	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	F21 M Performance三门改款外廓。	READY
120244	120244	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-FACELIFT-01	HIGH	F20 M Performance五门改款外廓。	READY
120236	120236	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	HIGH	F21 M Performance三门改款外廓。	READY
120245	120245	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-FACELIFT-01	HIGH	F20 M Performance五门改款外廓。	READY
160684	160684	Coupe	2 Series Gran Coupé II	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	F74四门Gran Coupé外廓。	READY
161092	161092	Coupe	2 Series Gran Coupé II	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	F74四门Gran Coupé外廓。	READY
160034	160034	Coupe	2 Series Gran Coupé II	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	F74四门Gran Coupé外廓。	READY
110022	110022	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45五门Active Tourer改款前外廓。	READY
113400	113400	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46五门Gran Tourer改款前外廓。	READY
107975_prefl	107975	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
107975_facelift	107975	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
111075_prefl	111075	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
111075_facelift	111075	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
113399	113399	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46五门Gran Tourer改款前外廓。	READY
116775	116775	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45五门Active Tourer改款前外廓。	READY
150697	150697	MPV	2 Series Active Tourer II	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH	U06五门Active Tourer外廓。	READY
100823	100823	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
107547_prefl	107547	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
107547_facelift	107547	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
111076_prefl	111076	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
111076_facelift	111076	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
113347	113347	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
113349	113349	Convertible	2 Series I	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH	F23双门敞篷外廓。	READY
116624_prefl	116624	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
116624_facelift	116624	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
116629_prefl	116629	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
116629_facelift	116629	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
116638	116638	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
116642	116642	Convertible	2 Series I	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH	F23双门敞篷外廓。	READY
160040	160040	Coupe	2 Series Gran Coupé II	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	F74四门Gran Coupé外廓。	READY
117593_prefl	117593	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
117593_facelift	117593	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
117596_prefl	117596	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
117596_facelift	117596	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
118972_prefl	118972	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
118972_facelift	118972	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
119028_prefl	119028	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
119028_facelift	119028	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
105893_prefl	105893	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
105893_facelift	105893	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
109511	109511	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
109519	109519	Convertible	2 Series I	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH	F23双门敞篷外廓。	READY
111073_prefl	111073	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
111073_facelift	111073	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
128113_prefl	128113	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
128113_facelift	128113	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
147602	147602	Convertible	2 Series I	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH	F23双门敞篷外廓。	READY
148077	148077	Coupe	2 Series Coupé II	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH	G42双门Coupe外廓。	READY
801700	801700	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
145860	145860	MPV	2 Series Active Tourer II	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH	U06五门Active Tourer外廓。	READY
148030	148030	MPV	2 Series Active Tourer II	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH	U06五门Active Tourer外廓。	READY
145854	145854	MPV	2 Series Active Tourer II	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH	U06五门Active Tourer外廓。	READY
58284	58284	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
100890	100890	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
107961	107961	Coupe	2 Series I	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH	F22双门Coupe外廓。	READY
107976_prefl	107976	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
107976_facelift	107976	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
108001	108001	Convertible	2 Series I	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH	F23双门敞篷外廓。	READY
113402_prefl	113402	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
113402_facelift	113402	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
116625_prefl	116625	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	Ktype跨F45改款，改款前外廓。	READY
116625_facelift	116625	MPV	2 Series Active Tourer I	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	Ktype跨F45改款，改款后外廓。	READY
116630_prefl	116630	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	Ktype跨F46改款，改款前外廓。	READY
116630_facelift	116630	MPV	2 Series Gran Tourer I	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	Ktype跨F46改款，改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1701-1800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421	BMW Group PressClub — BMW UK 1 Series F20/F21 LCI technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395392
EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421	BMW Group PressClub — BMW UK 1 Series F20/F21 LCI technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395392
EU-BMW-1-SERIES-E82-COUPE-01	4360	1748	1423	BMW Group PressClub — Specifications BMW 1 Series Coupé	https://www.press.bmwgroup.com/global/article/attachment/T0095893EN/142801
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	BMW Group PressClub — Specifications BMW 1 Series 3 Door Hatch, 09/2009	https://www.press.bmwgroup.com/global/article/detail/T0039355EN/specifications-bmw-1-series-3-door-hatch?language=en
EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	BMW Group PressClub — BMW 1 Series specifications, 06/2004	https://www.press.bmwgroup.com/japan/article/attachment/T0015362JA/31726
EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	4361	1800	1459	BMW Group PressClub — The all-new BMW 1 Series	https://www.press.bmwgroup.com/global/article/detail/T0442625EN/the-all-new-bmw-1-series?language=en
EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	BMW Group PressClub — The all-new BMW 1 Series	https://www.press.bmwgroup.com/asia/article/detail/T0123074EN/the-all-new-bmw-1-series?language=en
EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	BMW Group PressClub — The new three-door BMW 1 Series	https://www.press.bmwgroup.com/asia/article/detail/T0137200EN/the-new-three-door-bmw-1-series?language=en
EU-BMW-1-SERIES-E88-CONVERTIBLE-01	4360	1748	1411	BMW Group PressClub — BMW 1 Series Convertible specifications	https://www.press.bmwgroup.com/global/article/attachment/T0095873EN/142796
EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421	BMW Group PressClub — Specifications BMW 1 Series 5 Door Hatch, 09/2009	https://www.press.bmwgroup.com/global/article/detail/T0039356EN/specifications-bmw-1-series-5-door-hatch-09/2009?language=en
EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-PREFL-01	4340	1765	1411	BMW Group PressClub — BMW M135i five-door technical data	https://www.press.bmwgroup.com/global/article/attachment/T0126696EN/207829
EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-PREFL-01	4340	1765	1411	BMW Group PressClub — BMW M135i three-door technical data	https://www.press.bmwgroup.com/greece/article/attachment/T0128334EL/192583
EU-BMW-1-SERIES-F21-HATCHBACK-3D-MPERFORMANCE-FACELIFT-01	4324	1765	1411	BMW Group PressClub — BMW UK 1 Series F20/F21 LCI technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395392
EU-BMW-1-SERIES-F20-HATCHBACK-5D-MPERFORMANCE-FACELIFT-01	4324	1765	1411	BMW Group PressClub — BMW UK 1 Series F20/F21 LCI technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395392
EU-BMW-2-SERIES-F74-GRAN-COUPE-01	4546	1800	1445	BMW Group PressClub — The new BMW 2 Series Gran Coupé	https://www.press.bmwgroup.com/ireland/article/detail/T0445719EN/the-new-bmw-2-series-gran-coup%C3%A9?language=en
EU-BMW-2-SERIES-F45-MPV-PREFL-01	4342	1800	1555	BMW Group PressClub — The new BMW 2 Series Active Tourer	https://www.press.bmwgroup.com/global/article/detail/T0186826EN/the-new-bmw-2-series-active-tourer?language=en
EU-BMW-2-SERIES-F46-MPV-PREFL-01	4556	1800	1612	BMW Group PressClub — The new BMW 216i Gran Tourer	https://www.press.bmwgroup.com/asia/article/detail/T0274133EN/the-new-bmw-216i-gran-tourer-now-available-in-singapore?language=en
EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	4354	1800	1555	BMW Group PressClub — Specifications BMW 2 Series Active Tourer, 09/2018	https://www.press.bmwgroup.com/global/article/detail/T0286423EN/specifications-of-the-bmw-2-series-active-tourer-valid-from-september-2018?language=en
EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	4568	1800	1612	BMW Group PressClub — Specifications BMW 2 Series Gran Tourer, 09/2018	https://www.press.bmwgroup.com/global/article/detail/T0286424EN/specifications-of-the-bmw-2-series-gran-tourer-valid-from-september-2018?language=en
EU-BMW-2-SERIES-U06-MPV-01	4386	1824	1576	BMW Group PressClub — The new BMW 2 Series Active Tourer	https://www.press.bmwgroup.com/czech/article/detail/T0347812CS/nov%C3%A9-bmw-%C5%99ady-2-active-tourer?language=cs
EU-BMW-2-SERIES-F22-COUPE-01	4432	1774	1418	BMW Group PressClub — A new dimension in dynamics: the BMW 2 Series Coupé	https://www.press.bmwgroup.com/global/article/detail/T0151285EN/a-new-dimension-in-dynamics-the-bmw-2-series-coupe?language=en
EU-BMW-2-SERIES-F23-CONVERTIBLE-01	4432	1774	1413	BMW Group PressClub — BMW 2 Series Convertible technical data	https://www.press.bmwgroup.com/global/article/attachment/T0192483EN/295142
EU-BMW-2-SERIES-G42-COUPE-01	4537	1838	1390	BMW Group PressClub — The all-new BMW 2 Series Coupé	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0337149EN_GB/the-all-new-bmw-2-series-coup%C3%A9?language=en_GB
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1701-1800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0126696EN/207829 "https://www.press.bmwgroup.com/global/article/attachment/T0126696EN/207829"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2092 行）
- 累计尺寸组：dimension_groups_final.tsv（640 行）

