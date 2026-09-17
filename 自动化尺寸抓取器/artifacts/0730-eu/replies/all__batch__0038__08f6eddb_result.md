# 任务：all 第 3701-3800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0038__08f6eddb


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3701-3800 行

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
all 第 3701-3800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742
EU-DS-DS3-CROSSBACK-I-SUV-01	4118	1791	1534
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620
EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	3538	1589	1576
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-01	4668	1825	1459
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	4065	1760	1529
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449
EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	4035	1734	1474
EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	4115	1765	1600
EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	4100	1765	1600
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639
EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	4135	1765	1565
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435
EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	4653	1790	1445
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Honda	Hr-V	1.5 I-vtec	SUV	Frontantrieb	Benzin	134	182	Apr 2019	-	2024-03-01	135959
Land Rover	Range rover evoque	2.0 D150	SUV	Frontantrieb	Diesel	110	150	Dec 2018	-	2024-03-01	135975
Audi	A8 d5	60 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	338	460	May 2018	-	2024-03-01	135979
Mercedes-benz	Cla	CLA 200	Coupe	Frontantrieb	Benzin	110	150	Mar 2019	-	2024-03-01	135980
Volvo	Xc60 ii	T5 Polestar AWD	SUV	Allrad	Benzin	192	261	Mar 2017	Dec 2018	2024-03-01	135988
Audi	A8 d5	50 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	210	286	Jul 2018	-	2024-03-01	135995
Mercedes-benz	Sprinter 4-T	414 CDI Allrad	Kasten	Allrad	Diesel	105	143	Jan 2019	Dec 2021	2024-08-01	136000
Mercedes-benz	Sprinter 4-T	416 CDI Allrad	Kasten	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	136001
Mercedes-benz	Sprinter 4-T	419 CDI Allrad	Kasten	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	136002
Mercedes-benz	Vito	Evito	Kasten	Frontantrieb	Elektro	85	116	Mar 2019	-	2024-05-01	136003
Mercedes-benz	Vito tourer	114 CDI	Bus	Heckantrieb	Diesel	100	136	Mar 2019	-	2024-03-01	136004
Mercedes-benz	Vito tourer	114 CDI 4-matic	Bus	Allrad	Diesel	100	136	Mar 2019	-	2024-03-01	136005
Mercedes-benz	Vito tourer	116 CDI	Bus	Heckantrieb	Diesel	120	163	Mar 2019	-	2024-03-01	136006
Mercedes-benz	Vito tourer	116 CDI 4-matic	Bus	Allrad	Diesel	120	163	Mar 2019	-	2024-03-01	136007
Mercedes-benz	Vito tourer	119 CDI	Bus	Heckantrieb	Diesel	140	190	Mar 2019	-	2024-03-01	136008
Mercedes-benz	Vito tourer	119 CDI 4-matic	Bus	Allrad	Diesel	140	190	Mar 2019	-	2024-03-01	136009
Mercedes-benz	Vito mixto	114 CDI	Kasten	Heckantrieb	Diesel	100	136	Mar 2019	-	2024-03-01	136010
Mercedes-benz	Vito	114 CDI 4X4	Kasten	Allrad	Diesel	100	136	Apr 2020	-	2024-03-01	136011
Mercedes-benz	Vito mixto	116 CDI	Kasten	Heckantrieb	Diesel	120	163	Mar 2019	-	2024-03-01	136012
Mercedes-benz	Vito mixto	116 CDI 4-matic	Kasten	Allrad	Diesel	120	163	Mar 2019	-	2024-03-01	136013
Mercedes-benz	Vito mixto	119 CDI	Kasten	Heckantrieb	Diesel	140	190	Mar 2019	-	2024-03-01	136014
Mercedes-benz	Vito mixto	119 CDI 4-matic	Kasten	Allrad	Diesel	140	190	Mar 2019	-	2024-03-01	136015
Mitsubishi	Pajero ii	3.0 4WD	Geländewagen geschlossen	Allrad	Benzin	130	177	Nov 1997	Apr 2000	2024-03-01	136024
Mercedes-benz	V-Klasse	V 220 CDI / D	Bus	Heckantrieb	Diesel	120	163	Mar 2019	-	2024-03-01	136026
Mercedes-benz	V-Klasse	V 220 CDI / D 4-matic	Bus	Allrad	Diesel	120	163	Mar 2019	-	2024-03-01	136027
Mercedes-benz	V-Klasse	V 250 CDI / D	Bus	Heckantrieb	Diesel	140	190	Mar 2019	-	2024-03-01	136028
Mercedes-benz	V-Klasse	V 250 CDI / D 4-matic	Bus	Allrad	Diesel	140	190	Mar 2019	-	2024-03-01	136029
Mercedes-benz	V-Klasse	V 300 CDI / D	Bus	Heckantrieb	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	136030
Mercedes-benz	V-Klasse	V 300 CDI / D 4-matic	Bus	Allrad	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	136031
Mercedes-benz	Vito tourer	Evito	Bus	Frontantrieb	Elektro	85	116	Apr 2019	-	2024-05-01	136036
Audi	A8 d5	45 TDI Quattro	Stufenheck	Allrad	Diesel	183	249	Jan 2019	-	2024-03-01	136041
Mercedes-benz	Gls	350 D 4-matic	SUV	Allrad	Diesel	210	286	Apr 2019	-	2024-03-01	136066
Mercedes-benz	Gls	400 D 4-matic	SUV	Allrad	Diesel	243	330	Apr 2019	-	2024-03-01	136067
Volvo	Xc90 ii	T6 Polestar AWD	SUV	Allrad	Benzin	246	334	Jan 2017	Dec 2021	2024-05-01	136068
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	246	334	Mar 2017	Dec 2022	2024-05-01	136069
Volvo	Xc60 ii	T6 Polestar AWD	SUV	Allrad	Benzin	246	334	Mar 2017	Dec 2021	2024-05-01	136070
Nissan	X-Trail iii	1.7 DCI	SUV	Frontantrieb	Diesel	110	150	Apr 2019	-	2024-03-01	136072
Nissan	X-Trail iii	1.7 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	110	150	Apr 2019	-	2024-03-01	136073
Nissan	X-Trail iii	1.3 Dig-t	SUV	Frontantrieb	Benzin	118	160	Apr 2019	-	2024-03-01	136074
Mercedes-benz	A-Klasse	A 220	Stufenheck	Frontantrieb	Benzin	140	190	Jan 2019	-	2024-03-01	136075
Audi	A3	40 Tfsi	Schrägheck	Frontantrieb	Benzin	140	190	Jul 2018	Oct 2020	2024-03-01	136076
Audi	A3	35 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Jul 2018	Oct 2020	2024-03-01	136077
Audi	A3	35 TDI	Stufenheck	Frontantrieb	Diesel	110	150	Jul 2018	Oct 2020	2024-03-01	136078
Audi	A3	40 Tfsi	Stufenheck	Frontantrieb	Benzin	140	190	Jul 2018	Oct 2020	2024-03-01	136079
Audi	A3	40 Tfsi	Cabriolet	Frontantrieb	Benzin	140	190	Nov 2018	Oct 2020	2024-03-01	136080
Mercedes-benz	B-Klasse sports tourer	B 220	Schrägheck	Frontantrieb	Benzin	140	190	Apr 2019	-	2024-03-01	136081
Audi	Q2	35 TDI Quattro	SUV	Allrad	Diesel	110	150	Jan 2019	-	2025-04-01	136082
Mercedes-benz	A-Klasse	A 180	Stufenheck	Frontantrieb	Benzin	100	136	Apr 2019	-	2024-03-01	136083
Audi	A4 b9	35 TDI	Stufenheck	Frontantrieb	Diesel	110	150	Aug 2015	-	2024-03-01	136107
Audi	A4 b9	40 TDI	Stufenheck	Frontantrieb	Diesel	140	190	May 2015	-	2024-07-01	136108
Audi	A4 b9	40 TDI Quattro	Stufenheck	Allrad	Diesel	140	190	Sep 2015	Sep 2020	2026-07-01	136109
Audi	A4 b9 avant	35 TDI	Kombi	Frontantrieb	Diesel	110	150	Oct 2018	Oct 2019	2024-03-01	136110
Audi	A4 b9 avant	40 TDI	Kombi	Frontantrieb	Diesel	140	190	Oct 2018	Aug 2020	2025-06-01	136111
Audi	A4 b9 avant	40 TDI Quattro	Kombi	Allrad	Diesel	140	190	Oct 2018	Sep 2020	2024-03-01	136112
Audi	A5	40 TDI	Coupe	Frontantrieb	Diesel	140	190	Jun 2016	-	2024-07-01	136114
Audi	A5	40 TDI Quattro	Coupe	Allrad	Diesel	140	190	Oct 2016	-	2024-07-01	136115
Audi	A5	40 TDI	Cabriolet	Frontantrieb	Diesel	140	190	Nov 2016	-	2026-07-01	136118
Audi	A5	35 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2017	Feb 2020	2024-03-01	136119
Audi	A5	40 TDI	Schrägheck	Frontantrieb	Diesel	140	190	Sep 2016	-	2024-07-01	136121
Audi	A5	40 TDI Quattro	Schrägheck	Allrad	Diesel	140	190	Aug 2016	-	2024-07-01	136122
Mercedes-benz	Cla	CLA 200 D	Coupe	Frontantrieb	Diesel	110	150	Apr 2019	-	2024-03-01	136124
Mercedes-benz	Cla	CLA 220 D	Coupe	Frontantrieb	Diesel	140	190	Apr 2019	-	2024-03-01	136125
Mercedes-benz	B-Klasse sports tourer	B 160	Schrägheck	Frontantrieb	Benzin	80	109	Apr 2019	-	2024-03-01	136126
Mercedes-benz	Glc	200 D	SUV	Heckantrieb	Diesel	120	163	Apr 2019	Jun 2022	2024-03-01	136127
Mercedes-benz	Glc	200 D 4-matic	SUV	Allrad	Diesel	120	163	Apr 2019	Jun 2022	2024-03-01	136128
Mercedes-benz	Glc	220 D	SUV	Heckantrieb	Diesel	143	194	Apr 2019	Jun 2022	2024-03-01	136129
Mercedes-benz	Glc	220 D 4-matic	SUV	Allrad	Diesel	143	194	Apr 2019	Jun 2022	2024-03-01	136130
Mercedes-benz	Glc	200 D	SUV	Heckantrieb	Diesel	120	163	Apr 2019	Aug 2021	2024-03-01	136131
Mercedes-benz	Glc	200 D 4-matic	SUV	Allrad	Diesel	120	163	Apr 2019	Mar 2023	2024-03-01	136132
Mercedes-benz	Glc	220 D 4-matic	SUV	Allrad	Diesel	143	194	Apr 2019	Mar 2023	2024-03-01	136133
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	140	190	Sep 2018	-	2024-03-01	136134
Audi	A6 c8	35 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	120	163	Mar 2019	-	2024-03-01	136135
Audi	A6 c8 avant	35 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	120	163	Mar 2019	-	2024-03-01	136136
Audi	Q2	35 TDI	SUV	Frontantrieb	Diesel	110	150	Sep 2016	-	2024-03-01	136137
Nissan	Juke	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	80	109	Sep 2018	Dec 2019	2024-03-01	136138
Nissan	Micra v	0.9 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Mar 2019	-	2024-03-01	136140
DS	Ds	E-tense 4X4	SUV	Allrad	Benzin/Elektro	221	300	May 2019	-	2024-03-01	136141
DS	Ds	Hybrid4	Schrägheck	Allrad	Diesel/Elektro	147	200	Apr 2015	Dec 2018	2024-03-01	136142
Ford	Fiesta vii van	1.1 Ti-vct	Kasten/Schrägheck	Frontantrieb	Benzin	63	86	Apr 2019	-	2024-03-01	136143
DS	Ds	E-tense	Schrägheck	Frontantrieb	Elektro	100	136	May 2019	Dec 2022	2024-03-01	136144
Ford	Fiesta vii van	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	63	86	Apr 2019	-	2024-03-01	136145
Bentley	Bentayga	6	SUV	Allrad	Benzin	467	635	Mar 2019	-	2024-03-01	136146
Ferrari	F8	3.9	Coupe	Heckantrieb	Benzin	530	721	Mar 2019	-	2024-03-01	136147
Lada	Largus	1.6 CNG	Kasten/Kombi	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Nov 2018	-	2024-03-01	136148
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	100	136	Apr 2018	Apr 2023	2024-05-01	136149
Hyundai	Ix20	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	92	125	Nov 2010	Jul 2019	2024-03-01	136150
Hyundai	I20 ii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	55	75	Jan 2019	Sep 2020	2024-05-01	136151
Hyundai	Tucson	1.6 Crdi Hybrid 48V	SUV	Frontantrieb	Diesel/Elektro	85	116	Mar 2019	Dec 2020	2024-03-01	136152
Hyundai	Tucson	1.6 Crdi Hybrid 48V	SUV	Frontantrieb	Diesel/Elektro	100	136	Mar 2019	Dec 2020	2024-03-01	136153
Hyundai	Tucson	1.6 Crdi Hybrid 48V Allrad	SUV	Allrad	Diesel/Elektro	100	136	Mar 2019	Dec 2020	2024-03-01	136154
KIA	Sportage iv	1.6 Crdi Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	85	116	Mar 2019	Sep 2022	2024-03-01	136155
KIA	Sportage iv	1.6 Crdi Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	100	136	Mar 2019	Sep 2022	2024-03-01	136156
KIA	Sportage iv	1.6 Crdi Eco-dynamics+ AWD	SUV	Allrad	Diesel/Elektro	100	136	Mar 2019	Sep 2022	2024-03-01	136157
Chery	Tiggo 4	2	SUV	Frontantrieb	Benzin	90	122	Sep 2018	-	2026-04-01	136158
Skoda	Scala	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Feb 2019	-	2024-03-01	136159
Fiat	Panda	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	51	69	Mar 2019	-	2024-03-01	136160
Ford	Focus iv	2.0 ST Ecoblue	Schrägheck	Frontantrieb	Diesel	140	190	Apr 2019	Nov 2025	2026-02-01	136161
Toyota	Corolla	1.6 Vvti	Stufenheck	Frontantrieb	Benzin	90	122	Jan 2019	-	2024-03-01	136162
Ford	Focus iv turnier	2.0 ST Ecoblue	Kombi	Frontantrieb	Diesel	140	190	Apr 2019	Nov 2025	2026-02-01	136163
Ford	Focus iv	2.3 ST Ecoboost	Schrägheck	Frontantrieb	Benzin	206	280	Apr 2019	Nov 2025	2026-02-01	136164


--- Round 1 / 首次发送 ---
## 更新点

* 已按跨批次索引复用 **31 个既有尺寸组**，批量闭合 Audi、Mercedes-Benz、Volvo、DS、Hyundai、KIA 等车型映射。
* 首次闭合 3 个尺寸组：

  * Honda HR-V II facelift Sport：`4346 × 1790 × 1605 mm`
  * Mercedes-Benz B-Class W247：`4419 × 1796 × 1562 mm`
  * Ferrari F8 Tributo：`4611 × 1979 × 1206 mm`
    Honda 官方资料同时区分普通版与 182 hp Sport 的车身长度、宽度；B-Class 尺寸来自对应 W247 车型资料；F8 宽度按不含后视镜口径闭合。
* Ktype `136150` 跨越 Hyundai ix20 改款边界，已拆分为前期和 facelift 两条物理外廓映射。
* DS 的两个模糊车型名已按动力版本归位：`136141` 为 DS 7 Crossback E-Tense 4x4 300，`136144` 为 DS 3 Crossback E-Tense。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：55
* READY 映射：56
* PENDING Ktype：45
* 当前已引用尺寸组：34
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135959	135959	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-FACELIFT-SPORT-01	HIGH	Sport 外观件形成独立外廓。	READY
135975	135975	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
135979	135979	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
135980	135980	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
135988	135988	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
135995	135995	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
136041	136041	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
136068	136068	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136069	136069	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136070	136070	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136075	136075	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
136076	136076	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门外廓。	READY
136077	136077	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门外廓。	READY
136078	136078	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136079	136079	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136080	136080	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
136081	136081	MPV	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136082	136082	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
136083	136083	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
136110	136110	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	生产截止落在改款切换前，采用前期 Avant 外廓。	READY
136119	136119	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	Sportback 前期外廓。	READY
136124	136124	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
136125	136125	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
136126	136126	MPV	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136127	136127	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136128	136128	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136129	136129	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136130	136130	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136131	136131	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136132	136132	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136133	136133	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136134	136134	SUV	Tiguan II		5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH	四驱标准 SUV 外廓。	READY
136135	136135	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
136136	136136	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH	Avant 外廓。	READY
136137	136137	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
136138	136138	SUV	Juke I facelift	F15	5	EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	HIGH		READY
136140	136140	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
136141	136141	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	HIGH	E-Tense 4x4 300 对应 DS 7 Crossback。	READY
136142	136142	Hatchback	DS 5 facelift		5	EU-DS-DS5-FACELIFT-HATCHBACK-01	HIGH	Hybrid4 对应 DS 5 改款。	READY
136143	136143	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	MEDIUM	三门厢式车外廓。	READY
136144	136144	SUV	DS 3 Crossback I		5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH	E-Tense 对应 DS 3 Crossback，修正原始车身分类。	READY
136145	136145	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	MEDIUM	三门厢式车外廓。	READY
136146	136146	SUV	Bentayga I		5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
136147	136147	Coupe	F8 Tributo		2	EU-FERRARI-F8-TRIBUTO-COUPE-01	HIGH		READY
136149	136149	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	纯电外廓。	READY
136150_prefl	136150	MPV	ix20 I	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	HIGH	跨越改款边界，拆分前期外廓。	READY
136150_facelift	136150	MPV	ix20 I facelift	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	HIGH	跨越改款边界，拆分改款外廓。	READY
136151	136151	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	HIGH	五门外廓。	READY
136152	136152	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136153	136153	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136154	136154	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136155	136155	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136156	136156	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136157	136157	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136159	136159	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
136162	136162	Sedan	Corolla XII	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-HR-V-II-SUV-FACELIFT-SPORT-01	4346	1790	1605	Honda Motor Europe 2019 HR-V official brochure	https://www.honda.no/content/dam/local/norway/brochures/cars/HRV/HRV_NO_brochure.pdf
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Mercedes-Benz B-Class UK Range Guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2019/07/new-b-class.pdf
EU-FERRARI-F8-TRIBUTO-COUPE-01	4611	1979	1206	Auto-Data Ferrari F8 Tributo specifications;Car and Driver Ferrari F8 Tributo specifications	https://www.auto-data.net/en/ferrari-f8-tributo-generation-6969;https://www.caranddriver.com/ferrari/f8-tributo-spider/specs
```

## 下一步优先处理

1. 先闭合 Sprinter 4-T、Vito、eVito、V-Class 的长度、轴距和车顶派生分支。
2. 处理 Audi A4/A5 与 Ford Focus ST 跨 facelift 的物理外廓拆分。
3. 补齐 X-Trail III、GLS X167、Pajero II、Largus、Panda III、Tiggo 4 等尚未缓存尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 36 个 Ktype。Vito、Vito Mixto、Vito Tourer 与 V-Class 已按 Compact、Long、Extra-long 物理车长分支拆分；eVito 厢式车和早期 41 kWh eVito Tourer 按实际可用长度独立建组。([Dezo's Garage][1])
* Audi A4 B9、A5 F5 跨改款 Ktype 已拆分，并直接复用累计表中的改款前、facelift 尺寸组，未重复输出尺寸来源。
* 首次创建 GLS X167、X-Trail III facelift、Panda III Natural Power 等尺寸组；GLS 宽度采用不含后视镜的 1956 mm。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射：139
* PENDING Ktype：9
* 已确认且被引用尺寸组：55
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136003_long	136003	Van	eVito W447	W447		EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-LONG-01	HIGH	Long 纯电厢式车分支。	READY
136003_extra_long	136003	Van	eVito W447	W447		EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-EXTRA-LONG-01	HIGH	Extra-long 纯电厢式车分支。	READY
136004_compact	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136004_long	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136004_extra_long	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136005_compact	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136005_long	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136005_extra_long	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136006_compact	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136006_long	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136006_extra_long	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136007_compact	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136007_long	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136007_extra_long	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136008_compact	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136008_long	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136008_extra_long	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136009_compact	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136009_long	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136009_extra_long	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136010_compact	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136010_long	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136010_extra_long	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136011_long	136011	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136011_extra_long	136011	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136012_compact	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136012_long	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136012_extra_long	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136013_compact	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136013_long	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136013_extra_long	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136014_compact	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136014_long	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136014_extra_long	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136015_compact	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136015_long	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136015_extra_long	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136026_compact	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136026_long	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136026_extra_long	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136027_compact	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136027_long	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136027_extra_long	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136028_compact	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136028_long	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136028_extra_long	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136029_compact	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136029_long	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136029_extra_long	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136030_compact	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136030_long	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136030_extra_long	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136031_compact	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136031_long	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136031_extra_long	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136036_long	136036	MPV	eVito Tourer W447	W447		EU-MERCEDES-BENZ-EVITO-W447-TOURER-LONG-01	HIGH	Long 纯电乘用车分支。	READY
136036_extra_long	136036	MPV	eVito Tourer W447	W447		EU-MERCEDES-BENZ-EVITO-W447-TOURER-EXTRA-LONG-01	HIGH	Extra-long 纯电乘用车分支。	READY
136066	136066	SUV	GLS X167	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
136067	136067	SUV	GLS X167	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
136072	136072	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136073	136073	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136074	136074	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136107_prefl	136107	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136107_facelift	136107	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136108_prefl	136108	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136108_facelift	136108	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136109_prefl	136109	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136109_facelift	136109	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136111_prefl	136111	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	改款前外廓分支。	READY
136111_facelift	136111	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136112_prefl	136112	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	改款前外廓分支。	READY
136112_facelift	136112	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136114_prefl	136114	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	MEDIUM	改款前外廓分支。	READY
136114_facelift	136114	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136115_prefl	136115	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	MEDIUM	改款前外廓分支。	READY
136115_facelift	136115	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136118_prefl	136118	Convertible	A5 F5		2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	MEDIUM	改款前外廓分支。	READY
136118_facelift	136118	Convertible	A5 F5		2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136121_prefl	136121	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前外廓分支。	READY
136121_facelift	136121	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136122_prefl	136122	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前外廓分支。	READY
136122_facelift	136122	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136160	136160	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-NATURAL-POWER-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-LONG-01	5140	1928	1941	Auto-Data Mercedes-Benz eVito W447 Panel Van Long	https://www.auto-data.net/en/mercedes-benz-vito-w447-facelift-2020-panel-van-long-evito-41-kwh-116hp-36171
EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-EXTRA-LONG-01	5370	1928	1945	Auto-Data Mercedes-Benz eVito W447 Panel Van Extra Long	https://www.auto-data.net/en/mercedes-benz-vito-w447-facelift-2020-panel-van-extra-long-evito-41-kwh-116hp-55893
EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MERCEDES-BENZ-VITO-W447-LONG-01	5140	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	4895	1928	1907	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	5370	1928	1908	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-EVITO-W447-TOURER-LONG-01	5140	1928	1934	EV Database Mercedes-Benz eVito Tourer Long 41 kWh	https://ev-database.org/car/1613/Mercedes-Benz-eVito-Tourer-Long-41-kWh
EU-MERCEDES-BENZ-EVITO-W447-TOURER-EXTRA-LONG-01	5370	1928	1938	EV Database Mercedes-Benz eVito Tourer Extra-Long 41 kWh	https://ev-database.org/car/1614/Mercedes-Benz-eVito-Tourer-Extra-Long-41-kWh
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823	Auto-Data Mercedes-Benz GLS X167 GLS 350d	https://www.auto-data.net/en/mercedes-benz-gls-x167-gls-350d-286hp-4matic-g-tronic-36911
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Nissan X-Trail 2019 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/Nissan-X-Trail-2019-UK.pdf
EU-FIAT-PANDA-III-319-NATURAL-POWER-HATCHBACK-01	3653	1643	1605	Fiat Panda official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
```

## 下一步优先处理

1. 闭合 Ktype `136000`–`136002` 的 Sprinter VS30 四驱厢式车轴距和车顶组合。
2. 处理 Pajero II、Lada Largus、Chery Tiggo 4 三个独立车型。
3. 核对 Focus IV ST Hatchback/Turnier 的 ST 悬架高度及 facelift 分支，完成最后 3 个 Ktype。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2019-Mercedes-Benz-Vito-Tourer-UK.pdf "MB_brochures_a4-297x210_v4"
[2]: https://www.auto-data.net/en/mercedes-benz-gls-x167-gls-350d-286hp-4matic-g-tronic-36911 "Mercedes-Benz GLS (X167) GLS 350d (286 Hp) 4MATIC G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 9 个 Ktype 已全部闭合，本轮新增 18 条映射、11 个尺寸组。
* Sprinter 4-T 按 AWD 厢式车的 L2H2、L3H2、L3H3 三个物理分支拆分；官方规格分别支持对应车长、车宽和车高。([BlueSky][1])
* Pajero II 已拆分三门短轴与五门长轴；Largus CNG 已拆分 F90 厢式车与 R90 旅行车。([汽车数据][2])
* Tiggo 4 2.0 已闭合；Focus IV ST 已区分改款前两厢、改款前旅行车及 facelift 两厢外廓。([Chery в России][3])
* 已完成固定表头、唯一主键、外键闭合、尺寸与来源非空、下载文件名检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：157
* PENDING：0
* DIMENSION_GROUP：66
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 孤立尺寸组：0
* 缺失映射引用：0
* 机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135959	135959	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-FACELIFT-SPORT-01	HIGH	Sport 外观件形成独立外廓。	READY
135975	135975	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
135979	135979	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
135980	135980	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
135988	135988	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
135995	135995	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
136000_l2h2	136000	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L2H2-01	MEDIUM	L2H2 全轮驱动厢式车分支。	READY
136000_l3h2	136000	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H2-01	MEDIUM	L3H2 全轮驱动厢式车分支。	READY
136000_l3h3	136000	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H3-01	MEDIUM	L3H3 全轮驱动厢式车分支。	READY
136001_l2h2	136001	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L2H2-01	MEDIUM	L2H2 全轮驱动厢式车分支。	READY
136001_l3h2	136001	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H2-01	MEDIUM	L3H2 全轮驱动厢式车分支。	READY
136001_l3h3	136001	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H3-01	MEDIUM	L3H3 全轮驱动厢式车分支。	READY
136002_l2h2	136002	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L2H2-01	MEDIUM	L2H2 全轮驱动厢式车分支。	READY
136002_l3h2	136002	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H2-01	MEDIUM	L3H2 全轮驱动厢式车分支。	READY
136002_l3h3	136002	Van	Sprinter VS30	W907		EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H3-01	MEDIUM	L3H3 全轮驱动厢式车分支。	READY
136003_long	136003	Van	eVito W447	W447		EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-LONG-01	HIGH	Long 纯电厢式车分支。	READY
136003_extra_long	136003	Van	eVito W447	W447		EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-EXTRA-LONG-01	HIGH	Extra-long 纯电厢式车分支。	READY
136004_compact	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136004_long	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136004_extra_long	136004	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136005_compact	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136005_long	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136005_extra_long	136005	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136006_compact	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136006_long	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136006_extra_long	136006	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136007_compact	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136007_long	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136007_extra_long	136007	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136008_compact	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136008_long	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136008_extra_long	136008	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136009_compact	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136009_long	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136009_extra_long	136009	MPV	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136010_compact	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136010_long	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136010_extra_long	136010	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136011_long	136011	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136011_extra_long	136011	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136012_compact	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136012_long	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136012_extra_long	136012	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136013_compact	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136013_long	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136013_extra_long	136013	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136014_compact	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136014_long	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136014_extra_long	136014	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136015_compact	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact 车长分支。	READY
136015_long	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long 车长分支。	READY
136015_extra_long	136015	Van	Vito W447	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136024_3dr	136024	SUV	Pajero II		3	EU-MITSUBISHI-PAJERO-II-V20-SUV-3D-01	HIGH	三门短轴金属顶外廓。	READY
136024_5dr	136024	SUV	Pajero II		5	EU-MITSUBISHI-PAJERO-II-V20-SUV-5D-01	HIGH	五门长轴外廓。	READY
136026_compact	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136026_long	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136026_extra_long	136026	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136027_compact	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136027_long	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136027_extra_long	136027	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136028_compact	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136028_long	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136028_extra_long	136028	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136029_compact	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136029_long	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136029_extra_long	136029	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136030_compact	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136030_long	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136030_extra_long	136030	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136031_compact	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	HIGH	Compact 车长分支。	READY
136031_long	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	Long 车长分支。	READY
136031_extra_long	136031	MPV	V-Class W447 facelift	W447		EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	HIGH	Extra-long 车长分支。	READY
136036_long	136036	MPV	eVito Tourer W447	W447		EU-MERCEDES-BENZ-EVITO-W447-TOURER-LONG-01	HIGH	Long 纯电乘用车分支。	READY
136036_extra_long	136036	MPV	eVito Tourer W447	W447		EU-MERCEDES-BENZ-EVITO-W447-TOURER-EXTRA-LONG-01	HIGH	Extra-long 纯电乘用车分支。	READY
136041	136041	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
136066	136066	SUV	GLS X167	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
136067	136067	SUV	GLS X167	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
136068	136068	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136069	136069	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136070	136070	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136072	136072	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136073	136073	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136074	136074	SUV	X-Trail III facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
136075	136075	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
136076	136076	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门外廓。	READY
136077	136077	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门外廓。	READY
136078	136078	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136079	136079	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136080	136080	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
136081	136081	MPV	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136082	136082	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
136083	136083	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
136107_prefl	136107	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136107_facelift	136107	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136108_prefl	136108	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136108_facelift	136108	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136109_prefl	136109	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	MEDIUM	改款前外廓分支。	READY
136109_facelift	136109	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136110	136110	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	生产截止落在改款切换前，采用前期 Avant 外廓。	READY
136111_prefl	136111	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	改款前外廓分支。	READY
136111_facelift	136111	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136112_prefl	136112	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	MEDIUM	改款前外廓分支。	READY
136112_facelift	136112	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136114_prefl	136114	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	MEDIUM	改款前外廓分支。	READY
136114_facelift	136114	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136115_prefl	136115	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	MEDIUM	改款前外廓分支。	READY
136115_facelift	136115	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136118_prefl	136118	Convertible	A5 F5		2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	MEDIUM	改款前外廓分支。	READY
136118_facelift	136118	Convertible	A5 F5		2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136119	136119	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	Sportback 前期外廓。	READY
136121_prefl	136121	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前外廓分支。	READY
136121_facelift	136121	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136122_prefl	136122	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前外廓分支。	READY
136122_facelift	136122	Hatchback	A5 F5		5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	MEDIUM	Facelift 外廓分支。	READY
136124	136124	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
136125	136125	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	四门轿跑车物理外廓。	READY
136126	136126	MPV	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136127	136127	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136128	136128	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136129	136129	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136130	136130	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136131	136131	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136132	136132	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136133	136133	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136134	136134	SUV	Tiguan II		5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH	四驱标准 SUV 外廓。	READY
136135	136135	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
136136	136136	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH	Avant 外廓。	READY
136137	136137	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
136138	136138	SUV	Juke I facelift	F15	5	EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	HIGH		READY
136140	136140	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
136141	136141	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	HIGH	E-Tense 4x4 300 对应 DS 7 Crossback。	READY
136142	136142	Hatchback	DS 5 facelift		5	EU-DS-DS5-FACELIFT-HATCHBACK-01	HIGH	Hybrid4 对应 DS 5 改款。	READY
136143	136143	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	MEDIUM	三门厢式车外廓。	READY
136144	136144	SUV	DS 3 Crossback I		5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH	E-Tense 对应 DS 3 Crossback，修正原始车身分类。	READY
136145	136145	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	MEDIUM	三门厢式车外廓。	READY
136146	136146	SUV	Bentayga I		5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
136147	136147	Coupe	F8 Tributo		2	EU-FERRARI-F8-TRIBUTO-COUPE-01	HIGH		READY
136148_van	136148	Van	Largus I	F90	5	EU-LADA-LARGUS-I-F90-CNG-VAN-01	HIGH	CNG 厢式车外廓。	READY
136148_wagon	136148	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	CNG 五座旅行车外廓。	READY
136149	136149	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	纯电外廓。	READY
136150_prefl	136150	MPV	ix20 I	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	HIGH	跨越改款边界，拆分前期外廓。	READY
136150_facelift	136150	MPV	ix20 I facelift	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	HIGH	跨越改款边界，拆分改款外廓。	READY
136151	136151	Hatchback	i20 II	GB	5	EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	HIGH	五门外廓。	READY
136152	136152	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136153	136153	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136154	136154	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136155	136155	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136156	136156	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136157	136157	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
136158	136158	SUV	Tiggo 4 I	T1X	5	EU-CHERY-TIGGO-4-I-T1X-SUV-01	HIGH		READY
136159	136159	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
136160	136160	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-NATURAL-POWER-HATCHBACK-01	HIGH		READY
136161	136161	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-PREFL-01	HIGH	2.0 EcoBlue ST 仅对应改款前外廓。	READY
136162	136162	Sedan	Corolla XII	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH		READY
136163	136163	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-ST-WAGON-PREFL-01	HIGH	2.0 EcoBlue ST 仅对应改款前外廓。	READY
136164_prefl	136164	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-PREFL-01	HIGH	改款前 ST 外廓分支。	READY
136164_facelift	136164	Hatchback	Focus IV facelift	C519	5	EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-FACELIFT-01	HIGH	Facelift ST 外廓分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3701-3800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-HR-V-II-SUV-FACELIFT-SPORT-01	4346	1790	1605	Honda Motor Europe 2019 HR-V official brochure	https://www.honda.no/content/dam/local/norway/brochures/cars/HRV/HRV_NO_brochure.pdf
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Auto-Data Range Rover Evoque II specifications	https://www.auto-data.net/en/land-rover-range-rover-evoque-ii-2.0-td4-150hp-34876
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473	Auto-Data Audi A8 D5 specifications	https://www.auto-data.net/en/audi-a8-d5-generation-5850
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439	AutoWiki Mercedes-Benz CLA C118 specifications	https://auto-wiki.org/mercedes-benz/cla/c118/cla-coupe-200-progressive-120-kw-84176/
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars XC60 dimensions	https://www.volvocars.com/uk/support/car/xc60/20w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L2H2-01	5932	2020	2785	Mercedes-Benz Sprinter Panel/Crew Van AWD official price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H2-01	6967	2020	2778	Mercedes-Benz Sprinter Panel/Crew Van AWD official price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-W907-PANEL-VAN-AWD-L3H3-01	6967	2020	2995	Mercedes-Benz Sprinter Panel/Crew Van AWD official price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-LONG-01	5140	1928	1941	Auto-Data Mercedes-Benz eVito W447 Panel Van Long	https://www.auto-data.net/en/mercedes-benz-vito-w447-facelift-2020-panel-van-long-evito-41-kwh-116hp-36171
EU-MERCEDES-BENZ-EVITO-W447-PANEL-VAN-EXTRA-LONG-01	5370	1928	1945	Auto-Data Mercedes-Benz eVito W447 Panel Van Extra Long	https://www.auto-data.net/en/mercedes-benz-vito-w447-facelift-2020-panel-van-extra-long-evito-41-kwh-116hp-55893
EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MERCEDES-BENZ-VITO-W447-LONG-01	5140	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito 2019 official range guide	https://globalvans.co.uk/avm/images/vans/MEVD/Mercede_Vito_october_2019.pdf
EU-MITSUBISHI-PAJERO-II-V20-SUV-3D-01	4145	1785	1845	Auto-Data Mitsubishi Pajero II Metal Top 3.0 V6 24V specifications	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15522
EU-MITSUBISHI-PAJERO-II-V20-SUV-5D-01	4725	1775	1900	Auto-Data Mitsubishi Pajero II 3.0 V6 24V specifications	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15508
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-COMPACT-01	4895	1928	1907	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRA-LONG-01	5370	1928	1908	Mercedes-Benz V-Class 2019 official brochure	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_v-classandmarco_polo_2019_e.pdf
EU-MERCEDES-BENZ-EVITO-W447-TOURER-LONG-01	5140	1928	1934	EV Database Mercedes-Benz eVito Tourer Long 41 kWh	https://ev-database.org/car/1613/Mercedes-Benz-eVito-Tourer-Long-41-kWh
EU-MERCEDES-BENZ-EVITO-W447-TOURER-EXTRA-LONG-01	5370	1928	1938	EV Database Mercedes-Benz eVito Tourer Extra-Long 41 kWh	https://ev-database.org/car/1614/Mercedes-Benz-eVito-Tourer-Extra-Long-41-kWh
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823	Auto-Data Mercedes-Benz GLS X167 GLS 350d	https://www.auto-data.net/en/mercedes-benz-gls-x167-gls-350d-286hp-4matic-g-tronic-36911
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo Cars XC90 dimensions	https://www.volvocars.com/uk/support/car/xc90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Nissan X-Trail 2019 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/Nissan-X-Trail-2019-UK.pdf
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Auto-Data Mercedes-Benz A-Class Sedan V177 specifications	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-220-190hp-4matic-dct-34130
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Auto-Data Audi A3 Sportback 8V facelift specifications	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-40-tfsi-190hp-s-tronic-52331
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift specifications	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-40-tfsi-190hp-s-tronic-52330
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift specifications	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-40-tfsi-190hp-s-tronic-52332
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Mercedes-Benz B-Class UK Range Guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2019/07/new-b-class.pdf
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Automobile-Catalog Audi Q2 35 TDI specifications	https://www.automobile-catalog.com/car/2019/2913800/audi_q2_35_tdi.html
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	AutoWiki Audi A4 B9 specifications	https://www.autowiki.fi/index.php/Audi_A4_%28B9%29
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431	Audi A4 major upgrade official design data	https://www.audi.com/en/the-audi-a4-major-upgrade-for-the-bestseller-2019-11884/the-design-11889
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Auto-Data Audi A4 Avant B9 specifications	https://www.auto-data.net/en/audi-a4-avant-b9-8w-generation-4620
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460	Audi A4 major upgrade official design data	https://www.audi.com/en/the-audi-a4-major-upgrade-for-the-bestseller-2019-11884/the-design-11889
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Australian Car.Reviews Audi F5 A5 Coupe specifications	https://australiancar.reviews/review-audi-f5-a5-coupe-2017-on/
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Carsart Audi A5 Coupe F5 facelift specifications	https://carsart.net/details/2019-audi-a5-coupe-f5-facelift-2019-40-tdi-190-hp-quattro-ultra-s-tronic
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371	Automobile-Catalog Audi A5 Cabriolet F5 specifications	https://www.automobile-catalog.com/make/audi/a5_2/a5_2_cabriolet_2wd/2017.html
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Audi A5 Cabriolet official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a5-cabriolet-1394/download
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Auto-Data Audi A5 Sportback F5 specifications	https://www.auto-data.net/en/audi-a5-sportback-f5-generation-5188
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	VehicleSizes Audi A5 Sportback F5 facelift specifications	https://www.vehiclesizes.com/cars/audi/a5/a5-sportback-f5-facelift-2019-2020/
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639	Auto-Data Mercedes-Benz GLC X253 specifications	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-glc-300-241hp-9g-tronic-53040
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673	Auto-Data Volkswagen Tiguan II specifications	https://www.auto-data.net/en/volkswagen-tiguan-ii-generation-4678
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Automobile Dimension Audi A6 specifications	https://www.automobiledimension.com/model/audi/a6
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	ADAC Audi A6 Avant C8 specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a6/c8/291821/
EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	4135	1765	1565	Nissan Juke F15 official specifications	https://history.nissan.co.jp/JUKE/F15/1006/PDF/juke_spec_specification.pdf
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	Auto-Data Nissan Micra K14 specifications	https://www.auto-data.net/en/nissan-micra-k14-generation-5276
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620	Auto Express DS 7 Crossback specifications	https://www.autoexpress.co.uk/ds/7/prices-specs/87501/1.2-puretech-elegance-5dr
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504	AutoScout24 DS 5 Hybrid4 specifications	https://www.autoscout24.at/auto/technische-daten/ds-automobiles/ds-5/ds5-hybrid4-etg-limousine-diesel-20688/
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466	Automobile-Catalog Ford Fiesta VII specifications	https://www.automobile-catalog.com/car/2019/2563055/ford_fiesta_1_5_tdci_120_st-line.html
EU-DS-DS3-CROSSBACK-I-SUV-01	4118	1791	1534	Automobile Dimension DS 3 Crossback specifications	https://www.automobiledimension.com/model/ds/ds3-crossback
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742	CarsGuide Bentley Bentayga 2019 dimensions	https://www.carsguide.com.au/bentley/bentayga/car-dimensions/2019
EU-FERRARI-F8-TRIBUTO-COUPE-01	4611	1979	1206	Auto-Data Ferrari F8 Tributo specifications;Car and Driver Ferrari F8 Tributo specifications	https://www.auto-data.net/en/ferrari-f8-tributo-generation-6969;https://www.caranddriver.com/ferrari/f8-tributo-spider/specs
EU-LADA-LARGUS-I-F90-CNG-VAN-01	4470	1750	1650	LADA Largus CNG official brochure	https://static.lada.ru/files/brochures/models_pdf/Largus_cng-brochures.pdf
EU-LADA-LARGUS-I-R90-CNG-WAGON-01	4470	1750	1670	LADA Largus CNG official brochure	https://static.lada.ru/files/brochures/models_pdf/Largus_cng-brochures.pdf
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570	Hyundai Kona Electric official model history	https://www.hyundai.com/kr/ko/brand/brandstory/model/kona-history/2018-kona-electric
EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	4100	1765	1600	Hyundai ix20 owner manual dimensions	https://www.carmanualsonline.info/hyundai-ix20-2015-owners-manual/?srch=dimensions
EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	4115	1765	1600	Auto-Data Hyundai ix20 facelift specifications	https://www.auto-data.net/en/hyundai-ix20-facelift-2015-generation-4833
EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	4035	1734	1474	VehicleSizes Hyundai i20 II GB specifications	https://www.vehiclesizes.com/cars/hyundai/i20/i20-ii-gb-hatchback-2014/
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Auto-Data Hyundai Tucson III specifications	https://www.auto-data.net/en/hyundai-tucson-iii-1.6-t-gdi-177hp-4wd-22481
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Auto-Data Kia Sportage IV specifications	https://www.auto-data.net/en/kia-sportage-iv-1.6-gdi-132hp-22728
EU-CHERY-TIGGO-4-I-T1X-SUV-01	4318	1831	1662	Chery Russia Tiggo 4 official specifications	https://www.chery.ru/chery/about/news/382/
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471	Skoda Scala official technical data	https://cdn.skoda-storyboard.com/2019/03/TD-SCALA-en.pdf
EU-FIAT-PANDA-III-319-NATURAL-POWER-HATCHBACK-01	3653	1643	1605	Fiat Panda official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-PREFL-01	4388	1825	1458	Auto-Data Ford Focus IV Hatchback ST specifications	https://www.auto-data.net/en/ford-focus-iv-hatchback-st-2.0-ecoblue-190hp-37682
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435	Auto-Data Toyota Corolla XII E210 Sedan specifications	https://www.auto-data.net/en/toyota-corolla-xii-e210-1.6i-132hp-cvt-37774
EU-FORD-FOCUS-IV-C519-ST-WAGON-PREFL-01	4668	1825	1492	Auto-Data Ford Focus IV Wagon ST specifications	https://www.auto-data.net/en/ford-focus-iv-wagon-st-2.0-ecoblue-190hp-37685
EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-FACELIFT-01	4393	1825	1458	Ford Focus official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3701-3800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf "https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf"
[2]: https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15508 "https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15508"
[3]: https://www.chery.ru/chery/about/news/382/ "https://www.chery.ru/chery/about/news/382/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3322 行）
- 累计尺寸组：dimension_groups_final.tsv（1496 行）

