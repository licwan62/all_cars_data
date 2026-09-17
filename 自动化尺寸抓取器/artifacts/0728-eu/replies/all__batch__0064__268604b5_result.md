# 任务：all 第 6301-6400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0064__268604b5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6301-6400 行

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
all 第 6301-6400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764
EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	4820	1884	1723
EU-FORD-GRAND-C-MAX-II-MPV-01	4520	1828	1684
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658
EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	3970	1560	1400
EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	3970	1570	1400
EU-PEUGEOT-204-CONVERTIBLE-2D-01	3740	1560	1320
EU-PEUGEOT-204-COUPE-3D-01	3740	1560	1300
EU-PEUGEOT-204-EARLY-SEDAN-01	3990	1560	1400
EU-PEUGEOT-204-LATE-SEDAN-01	3980	1570	1400
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380
EU-PEUGEOT-404-I-SEDAN-POST69-01	4445	1626	1450
EU-PEUGEOT-404-I-SEDAN-PRE69-01	4420	1626	1450
EU-PEUGEOT-504-SEDAN-01	4496	1689	1461
EU-PEUGEOT-505-I-BREAK-01	4898	1730	1540
EU-PEUGEOT-505-II-BREAK-01	4901	1730	1540
EU-PEUGEOT-505-II-SEDAN-STANDARD-01	4579	1737	1432
EU-PEUGEOT-505-II-SEDAN-V6-01	4579	1737	1430
EU-PEUGEOT-505-I-SEDAN-STANDARD-01	4579	1720	1450
EU-PEUGEOT-505-I-SEDAN-TURBO-01	4579	1737	1424
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714
EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	5489	1965	1900
EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	4712	1965	1900
EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	4765	1965	2100
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-TOYOTA-CORONA-VI-T130-LIFTBACK-5D-01	4290	1645	1385
EU-TOYOTA-CROWN-VI-S110-SEDAN-4D-01	4860	1715	1430
EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	4425	1690	1890
EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	4690	1690	1890
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-FACELIFT2012-01	4950	1970	1865
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	4750	1800	1845
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-TURBODIESEL-01	4750	1800	1830
EU-TOYOTA-LAND-CRUISER-70-CONVERTIBLE-2D-SWB-HARDTOP-01	4040	1690	1890
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	4405	1790	1950
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	3975	1690	1870
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900
EU-TOYOTA-LAND-CRUISER-PRADO-70-SUV-5D-LWB-01	4585	1690	1890
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-01	4485	1885	1875
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-01	4760	1885	1890
EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	3995	1650	1900
EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	4000	1650	1910
EU-TOYOTA-LITEACE-II-M20-VAN-4D-01	3900	1625	1765
EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	4750	1800	1780

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Toyota	Corolla	1.2	Stufenheck	Heckantrieb	Benzin	43	58	Oct 1972	Jul 1979	2024-03-01	6721
Dacia	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	65	88	May 2010	-	2024-03-01	6722
Toyota	Corolla	1.2	Coupe	Heckantrieb	Benzin	40	54	Jul 1975	Jan 1980	2024-03-01	6723
Toyota	Corolla	1.2	Kombi	Heckantrieb	Benzin	40	54	Jul 1975	Jul 1979	2024-03-01	6724
Toyota	Corolla	1.2	Schrägheck	Heckantrieb	Benzin	40	54	Sep 1976	Jan 1980	2024-03-01	6725
Toyota	Corolla	1.6	Schrägheck	Heckantrieb	Benzin	54	73	Sep 1976	Jan 1980	2024-03-01	6726
Toyota	Corolla	1.6	Schrägheck	Heckantrieb	Benzin	62	84	Sep 1976	Jan 1980	2024-03-01	6727
Peugeot	404	1.6	Stufenheck	Heckantrieb	Benzin	54	73	Nov 1967	Dec 1971	2024-03-01	6728
Peugeot	404	1.6 GT	Stufenheck	Heckantrieb	Benzin	50	68	Jul 1971	Dec 1971	2024-03-01	6729
Peugeot	404	1.6	Cabriolet	Heckantrieb	Benzin	59	80	Apr 1963	Dec 1968	2024-03-01	6730
Peugeot	204	1.1	Cabriolet	Frontantrieb	Benzin	39	53	Jan 1967	May 1969	2024-03-01	6731
Toyota	Corolla	1.6 GT	Schrägheck	Heckantrieb	Benzin	81	110	May 1980	Sep 1983	2024-03-01	6732
Toyota	Corolla	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Oct 1982	Sep 1983	2024-03-01	6733
Toyota	Corolla	1.8 D	Stufenheck	Heckantrieb	Diesel	43	58	Jan 1983	Sep 1983	2024-03-01	6734
Peugeot	309 ii	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Jul 1990	Dec 1993	2024-03-01	6735
Peugeot	309 ii	1.9 GTI 16V	Schrägheck	Frontantrieb	Benzin	108	147	Oct 1990	Dec 1993	2024-03-01	6736
Toyota	Corolla	1.8 D	Stufenheck	Frontantrieb	Diesel	43	58	Jun 1983	May 1988	2024-03-01	6737
Toyota	Corolla	1.8 D	Stufenheck	Frontantrieb	Diesel	47	64	Jun 1983	Jun 1989	2024-03-01	6738
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Dec 1985	May 1988	2024-03-01	6739
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	43	58	Jun 1983	May 1988	2024-03-01	6740
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	63	86	Jul 1985	May 1988	2024-03-01	6741
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	43	58	Jan 1985	May 1988	2024-03-01	6742
Toyota	Corolla	1.6 16V	Coupe	Heckantrieb	Benzin	85	115	Dec 1985	Apr 1987	2024-03-01	6743
Toyota	Corolla	1.8 D	Stufenheck	Frontantrieb	Diesel	47	64	Jul 1987	Jun 1993	2024-03-01	6744
Toyota	Corolla	1.6 GTI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 1987	Jun 1993	2024-03-01	6745
Toyota	Corona	1.8	Stufenheck	Heckantrieb	Benzin	63	86	Oct 1979	Jan 1981	2024-03-01	6746
Toyota	Corona	2.0 Mark II	Stufenheck	Heckantrieb	Benzin	65	88	Dec 1975	Oct 1977	2024-03-01	6748
Toyota	Corona	2	Stufenheck	Heckantrieb	Benzin	65	88	Jan 1976	May 1979	2024-03-01	6749
Toyota	Cressida station wagon	2	Kombi	Heckantrieb	Benzin	77	105	Feb 1981	Mar 1985	2024-03-01	6750
Toyota	Cressida station wagon	2.2 D	Kombi	Heckantrieb	Diesel	49	67	Sep 1980	Apr 1985	2024-03-01	6751
Toyota	Crown	2.8	Kombi	Heckantrieb	Benzin	107	146	Sep 1980	Sep 1983	2024-03-01	6752
Toyota	Crown	2.8 I Super Saloon	Stufenheck	Heckantrieb	Benzin	125	170	Feb 1984	Mar 1985	2024-03-01	6753
Toyota	Hiace iii	2.2 D	Bus	Heckantrieb	Diesel	49	67	Dec 1982	Nov 1989	2024-03-01	6754
Toyota	Hiace iii	1.8	Bus	Heckantrieb	Benzin	58	79	Mar 1983	Jul 1989	2024-03-01	6755
Toyota	Hiace iii	2.4 D 4WD	Bus	Allrad	Diesel	54	73	Jan 1987	Aug 1989	2024-03-01	6756
Toyota	Hiace iii	1.8	Kasten	Heckantrieb	Benzin	58	79	Dec 1982	Jul 1989	2024-03-01	6757
Toyota	Hiace iii	2.2 D	Kasten	Heckantrieb	Diesel	49	67	Dec 1982	Nov 1989	2024-03-01	6758
Toyota	Hiace iii	2.4 D	Kasten	Heckantrieb	Diesel	55	75	Dec 1982	Nov 1989	2024-03-01	6759
Toyota	Hiace iv	2.4 D	Kasten	Heckantrieb	Diesel	55	75	Aug 1989	Aug 2004	2024-03-01	6760
Toyota	Hiace iv	2	Kasten	Heckantrieb	Benzin	74	101	Feb 1990	Aug 2004	2024-03-01	6761
BMW	5	M 550 D Xdrive	Kombi	Allrad	Diesel	280	381	Mar 2012	Feb 2017	2024-03-01	6762
Toyota	Liteace	1.5	Kasten	Heckantrieb	Benzin	51	69	May 1986	Sep 1991	2024-03-01	6763
Toyota	Liteace	1.5	Bus	Heckantrieb	Benzin	52	71	Jul 1989	Jan 1992	2024-03-01	6764
Toyota	Land cruiser	4.2	Geländewagen geschlossen	Allrad	Benzin	88	120	Oct 1981	Jan 1988	2024-03-01	6765
Toyota	Land cruiser	4.0 D	Geländewagen geschlossen	Allrad	Diesel	77	105	Oct 1981	Jan 1988	2024-03-01	6766
Toyota	Land cruiser	3.4 D	Geländewagen geschlossen	Allrad	Diesel	70	95	Nov 1984	Dec 1996	2024-03-01	6767
Toyota	Previa i	2.4 4WD	Großraumlimousine	Allrad	Benzin	97	132	Jan 1990	Aug 2000	2024-03-01	6768
Peugeot	504	1.8	Stufenheck	Heckantrieb	Benzin	60	82	Jul 1968	Feb 1971	2024-03-01	6769
Peugeot	504	1.8 Injection	Stufenheck	Heckantrieb	Benzin	71	97	Jul 1968	Feb 1971	2024-03-01	6770
Peugeot	504	1.9 D	Stufenheck	Heckantrieb	Diesel	40	54	Mar 1973	Jul 1986	2024-03-01	6771
Peugeot	504	2.1 D	Stufenheck	Heckantrieb	Diesel	48	65	Feb 1971	Jul 1986	2024-03-01	6772
Peugeot	504	2.3 D	Stufenheck	Heckantrieb	Diesel	51	69	Jul 1975	Dec 1983	2024-03-01	6773
Peugeot	504	1.8	Kombi	Heckantrieb	Benzin	54	73	Apr 1971	Jul 1986	2024-03-01	6774
Peugeot	504	2	Kombi	Heckantrieb	Benzin	68	92	Apr 1971	Jul 1986	2024-03-01	6775
Peugeot	504	2.1 D	Kombi	Heckantrieb	Diesel	48	65	Apr 1971	Jul 1986	2024-03-01	6776
Peugeot	504	2.3 D	Kombi	Heckantrieb	Diesel	51	69	Jul 1975	Jul 1986	2024-03-01	6777
Peugeot	505	1.8	Stufenheck	Heckantrieb	Benzin	62	84	Sep 1985	Oct 1986	2024-03-01	6778
Peugeot	505	2.2 Turbo Injection	Stufenheck	Heckantrieb	Benzin	110	150	Jan 1986	Dec 1987	2024-03-01	6779
Peugeot	505	2	Kombi	Heckantrieb	Benzin	60	82	Apr 1982	Nov 1987	2024-03-01	6780
Peugeot	505	2.2 GTI	Kombi	Heckantrieb	Benzin	90	122	Sep 1985	Dec 1986	2024-03-01	6781
Peugeot	505	2.5 Turbo Diesel	Kombi	Heckantrieb	Diesel	66	90	Oct 1985	Nov 1987	2024-03-01	6782
Peugeot	505	2.5 Turbo Diesel	Kombi	Heckantrieb	Diesel	77	105	Oct 1986	Dec 1993	2024-03-01	6783
Peugeot	604	2.7 SL	Stufenheck	Heckantrieb	Benzin	100	136	Aug 1977	May 1983	2024-03-01	6784
Peugeot	604	2.3 TD	Stufenheck	Heckantrieb	Diesel	59	80	Sep 1979	May 1983	2024-03-01	6785
Peugeot	604	2.8 GTI	Stufenheck	Heckantrieb	Benzin	110	150	Sep 1983	Jul 1987	2024-03-01	6786
Peugeot	604	2.5 TD	Stufenheck	Heckantrieb	Diesel	66	90	Aug 1983	Dec 1986	2024-03-01	6787
Peugeot	806	1.8	Großraumlimousine	Frontantrieb	Benzin	73	99	Jul 1995	Aug 2002	2024-03-01	6788
Peugeot	J5	2	Bus	Frontantrieb	Benzin	62	84	Oct 1990	Feb 1994	2024-03-01	6789
Peugeot	J5	2	Bus	Frontantrieb	Benzin	58	79	Jan 1983	Sep 1990	2024-03-01	6790
Peugeot	J5	2.5 D 4X4	Bus	Allrad	Diesel	54	73	Oct 1990	Feb 1994	2024-03-01	6791
Peugeot	J5	2.5 TD 4X4	Bus	Allrad	Diesel	70	95	Oct 1990	Feb 1994	2024-03-01	6792
Peugeot	J5	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	58	79	Jan 1983	Nov 1988	2024-03-01	6793
Peugeot	J5	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	55	75	Jan 1986	Nov 1988	2024-03-01	6794
Peugeot	J5	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Oct 1990	Feb 1994	2024-03-01	6795
Peugeot	J5	2.5 D 4X4	Kasten	Allrad	Diesel	54	73	Oct 1990	Mar 1994	2024-03-01	6796
Peugeot	J5	2.5 TD 4X4	Kasten	Allrad	Diesel	70	95	Oct 1990	Mar 1994	2024-03-01	6797
Peugeot	J5	2.5 TD 4X4	Pritsche/Fahrgestell	Allrad	Diesel	70	95	Oct 1990	Feb 1994	2024-03-01	6798
Skoda	Octavia	1.4	Kombi	Frontantrieb	Benzin	55	75	May 2004	May 2006	2024-03-01	6799
Skoda	Octavia	1.8 TSI 4X4	Kombi	Allrad	Benzin	112	152	Mar 2009	Feb 2013	2024-03-01	6800
Trabant	P 601	0.6	Kasten	Frontantrieb	Benzin	19	26	Jul 1966	Apr 1990	2024-03-01	6801
Ford	Galaxy ii	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Feb 2011	Jun 2015	2024-03-01	6802
Ford	S-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Feb 2011	Dec 2014	2024-03-01	6803
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Feb 2011	Jun 2019	2024-03-01	6804
Daimler	2.8 - 5.3	Sovereign 2.8	Stufenheck	Heckantrieb	Benzin	110	149	Oct 1969	May 1975	2024-03-01	6805
Daimler	2.8 - 5.3	Sovereign 3.4	Stufenheck	Heckantrieb	Benzin	120	163	May 1975	Dec 1978	2024-03-01	6806
Daimler	Xj	Sovereign 3.6	Stufenheck	Heckantrieb	Benzin	136	185	Oct 1986	Sep 1989	2024-03-01	6807
Daimler	Xj	Sovereign 3.6	Stufenheck	Heckantrieb	Benzin	145	197	Oct 1986	Jul 1989	2024-03-01	6808
Daimler	Xj	Sovereign 4.0	Stufenheck	Heckantrieb	Benzin	163	222	Sep 1989	Sep 1994	2024-03-01	6809
Daimler	Daimler xj	SIX 4.0	Stufenheck	Heckantrieb	Benzin	177	241	Oct 1994	Jun 2003	2024-03-01	6810
Daimler	2.8 - 5.3	Sovereign 4.2	Stufenheck	Heckantrieb	Benzin	137	186	Oct 1969	Sep 1973	2024-03-01	6811
Daimler	2.8 - 5.3	Sovereign 4.2	Stufenheck	Heckantrieb	Benzin	124	169	Jun 1976	Mar 1979	2024-03-01	6812
Daimler	2.8 - 5.3	Sovereign 4.2	Stufenheck	Heckantrieb	Benzin	127	173	Sep 1973	Mar 1979	2024-03-01	6813
Daimler	2.8 - 5.3	Sovereign 4.2	Stufenheck	Heckantrieb	Benzin	151	205	Mar 1979	Oct 1986	2024-03-01	6814
Daimler	2.8 - 5.3	Double SIX / Vanden 5.3	Stufenheck	Heckantrieb	Benzin	198	269	Jul 1972	Sep 1973	2024-03-01	6815
Daimler	2.8 - 5.3	Double SIX / Vanden 5.3	Stufenheck	Heckantrieb	Benzin	186	253	Sep 1973	May 1975	2024-03-01	6816
Daimler	2.8 - 5.3	Double SIX 5.3	Stufenheck	Heckantrieb	Benzin	211	287	May 1975	Jul 1981	2024-03-01	6817
Daimler	2.8 - 5.3	Double SIX H.e. 5.3	Stufenheck	Heckantrieb	Benzin	217	295	Jul 1981	Oct 1986	2024-03-01	6818
Daimler	2.8 - 5.3	Double SIX 5.3	Stufenheck	Heckantrieb	Benzin	194	264	Oct 1986	Feb 1993	2024-03-01	6819
Daimler	2.8 - 5.3	Double SIX 5.3	Stufenheck	Heckantrieb	Benzin	197	268	Jul 1981	Feb 1993	2024-03-01	6820
Daimler	Xj	Double SIX 6.0	Stufenheck	Heckantrieb	Benzin	229	311	Feb 1993	Sep 1994	2024-03-01	6821


--- Round 1 / checkpoint 续跑 ---
## 更新点

* 缓存优先完成 51 个输入 Ktype，共形成 62 条 READY 映射；涉及 31 个既有尺寸组直接复用。
* 首次闭合 4 个新尺寸组：BMW M550d xDrive Touring F11、Peugeot 504 Break、Škoda Octavia II 前期 Combi、Trabant P601 Universal/Kasten。
* BMW 官方技术表确认 M550d xDrive Touring 为五门 F11，三维为 4910 × 1860 × 1462 mm。([宝马集团新闻][1])
* Octavia II 前期 Combi 使用 4572 × 1769 × 1468 mm，其中宽度明确为不含后视镜。([automobile-catalog.com][2])
* Peugeot 504 Break 按 4800 × 1690 × 1550 mm 建组；Trabant 601 Universal/Kasten 同壳体按 3560 × 1510 × 1440 mm 建组。([ultimatespecs.com][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：51
* READY 映射行：62
* PENDING Ktype：49
* 已引用尺寸组：35
* 本轮新建尺寸组：4
* 复用既有尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6722	6722	Wagon	Logan I facelift	KS	5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	MCV五门改款外廓。	READY
6728_pre69	6728	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-PRE69-01	MEDIUM	生产期跨越1969年外廓变更，拆分前期。	READY
6728_post69	6728	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	MEDIUM	生产期跨越1969年外廓变更，拆分后期。	READY
6729	6729	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	HIGH	1971年后期四门外廓。	READY
6731	6731	Convertible	204		2	EU-PEUGEOT-204-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
6732	6732	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门GT掀背外廓。	READY
6733	6733	Sedan	Corolla IV (E70)		4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	E70四门轿车外廓。	READY
6734	6734	Sedan	Corolla IV (E70)		4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	E70四门轿车外廓。	READY
6735_3dr	6735	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分三门。	READY
6735_5dr	6735	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分五门。	READY
6736_3dr	6736	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分三门。	READY
6736_5dr	6736	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分五门。	READY
6737	6737	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6738	6738	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6739	6739	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6740_3dr	6740	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6740_5dr	6740	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6741_3dr	6741	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6741_5dr	6741	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6742_3dr	6742	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6742_5dr	6742	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6743	6743	Coupe	Corolla V (E80)	AE86	2	EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	HIGH	AE86双门后驱轿跑外廓。	READY
6744	6744	Sedan	Corolla VI (E90)	CE90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门柴油轿车外廓。	READY
6745	6745	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	HIGH	AE92三门GTI紧凑掀背外廓。	READY
6762	6762	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	HIGH	F11五门M550d xDrive Touring外廓。	READY
6763_prefl	6763	Van	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	MEDIUM	生产期跨越外廓改款，拆分前期；厢式车复用同壳体组。	READY
6763_facelift	6763	Van	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	MEDIUM	生产期跨越外廓改款，拆分后期；厢式车复用同壳体组。	READY
6764	6764	MPV	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	HIGH	后期四门客车外廓。	READY
6766	6766	SUV	Land Cruiser 60	HJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	HIGH	60系五门自然吸气柴油外廓。	READY
6769	6769	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6770	6770	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6771	6771	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6772	6772	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6773	6773	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6774	6774	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6775	6775	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6776	6776	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6777	6777	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6778	6778	Sedan	505 II		4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH	505 II标准四门轿车外廓。	READY
6780_prefl	6780	Wagon	505 I		5	EU-PEUGEOT-505-I-BREAK-01	MEDIUM	生产期跨越代际改款，拆分505 I Break。	READY
6780_facelift	6780	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	MEDIUM	生产期跨越代际改款，拆分505 II Break。	READY
6781	6781	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6782	6782	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6783	6783	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6784	6784	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6785	6785	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6786	6786	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6787	6787	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6788	6788	MPV	806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221平台五门MPV外廓。	READY
6789	6789	MPV	J5	280P	4	EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM	标准轴距客车外廓。	READY
6790	6790	MPV	J5	280P	4	EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM	标准轴距客车外廓。	READY
6793_swb	6793	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6793_lwb	6793	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
6794_swb	6794	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6794_lwb	6794	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
6799	6799	Wagon	Octavia II (1Z)	1Z5	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	HIGH	1Z5前期五门旅行车外廓。	READY
6800	6800	Wagon	Octavia II (1Z)	1Z5	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH	1Z5改款四驱旅行车外廓。	READY
6801	6801	Van	P 601	P601	3	EU-TRABANT-P601-UNIVERSAL-VAN-3D-01	MEDIUM	Kasten采用P601 Universal三门封闭式车身外廓。	READY
6802	6802	MPV	Galaxy II facelift	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6改款五门MPV外廓。	READY
6803	6803	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH	WA6五门MPV外廓。	READY
6804_prefl	6804	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	MEDIUM	生产期跨越改款尺寸变化，拆分前期。	READY
6804_facelift	6804	MPV	Grand C-Max II facelift		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	MEDIUM	生产期跨越改款尺寸变化，拆分后期。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462	BMW Group PressClub technical data: BMW M550d xDrive Touring (03/2012)	https://www.press.bmwgroup.com/deutschland/article/attachment/T0124400DE/183778
EU-PEUGEOT-504-BREAK-WAGON-5D-01	4800	1690	1550	UltimateSpecs Peugeot 504 Break specifications	https://www.ultimatespecs.com/car-specs/Peugeot/M458/504-Break
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468	Automobile-Catalog 2007 Skoda Octavia Combi 1.4 16V specifications	https://www.automobile-catalog.com/car/2007/3137930/skoda_octavia_combi_1_4_16v_80.html
EU-TRABANT-P601-UNIVERSAL-VAN-3D-01	3560	1510	1440	Sachsenring Trabant 601 operating manual technical data (reproduced with citation)	https://en.wikipedia.org/wiki/Trabant_601#Technical_data
```

## 下一步优先处理

1. Toyota 早期 Corolla、Corona、Cressida、Crown 的代际跨界及 Coupe/Wagon/Liftback 外廓。
2. Hiace III/IV 的轴距、车顶及 4WD 分支；Land Cruiser 60/70 和 Previa 4WD。
3. Peugeot 404 Cabriolet、505 Turbo Sedan，以及 J5 4×4、Van、后期底盘驾驶室。
4. Daimler Sovereign、Double Six 和 XJ 的 Series I/II/III、XJ40、X300/X308 分段。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/deutschland/article/attachment/T0124400DE/183778 "BMW"
[2]: https://www.automobile-catalog.com/car/2007/3137930/skoda_octavia_combi_1_4_16v_80.html?utm_source=chatgpt.com "2007 Skoda Octavia Combi 1.4 16V (80) Specs Review (59 ..."
[3]: https://www.ultimatespecs.com/car-specs/Peugeot/M458/504-Break?utm_source=chatgpt.com "Specs for all Peugeot 504 Break versions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 新增完成 15 个 Ktype、19 条映射，首次创建 9 个尺寸组。
* Peugeot 404 Cabriolet、Toyota Corona T130 Sedan 与 Cressida X60 Wagon 的欧洲规格已闭合；Cressida 汽油与柴油旅行车高度不同，分别建组。([汽车目录][1])
* Crown VII MS123、HiAce III Van 短轴/长轴及 Land Cruiser FJ60 使用 Toyota 官方资料建组。([丰田官方全球网站][2])
* HiAce III Bus 短轴/长轴、Previa I 4WD 与 Peugeot 505 Turbo Injection 直接关联既有尺寸组，不重复输出尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：66
* READY 映射行：81
* PENDING Ktype：34
* 当前已引用尺寸组：48
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6730	6730	Convertible	404		2	EU-PEUGEOT-404-CABRIOLET-2D-01	MEDIUM	双门敞篷外廓。	READY
6746	6746	Sedan	Corona VI (T130)		4	EU-TOYOTA-CORONA-VI-T130-SEDAN-4D-01	HIGH	T130四门轿车外廓。	READY
6750	6750	Wagon	Cressida II (X60)		5	EU-TOYOTA-CRESSIDA-II-X60-WAGON-PETROL-01	HIGH	汽油版五门旅行车外廓。	READY
6751	6751	Wagon	Cressida II (X60)		5	EU-TOYOTA-CRESSIDA-II-X60-WAGON-DIESEL-01	HIGH	柴油版五门旅行车外廓。	READY
6752	6752	Wagon	Crown VI (S110)		5	EU-TOYOTA-CROWN-VI-S110-WAGON-5D-01	HIGH	S110五门旅行车外廓。	READY
6753	6753	Sedan	Crown VII (S120)	MS123	4	EU-TOYOTA-CROWN-VII-S120-SEDAN-MS123-01	HIGH	MS123四门轿车外廓。	READY
6754_swb	6754	MPV	HiAce III (H50/H60)	LH50	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分短轴。	READY
6754_lwb	6754	MPV	HiAce III (H50/H60)	LH60	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分长轴。	READY
6755_swb	6755	MPV	HiAce III (H50/H60)	YH50	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分短轴。	READY
6755_lwb	6755	MPV	HiAce III (H50/H60)	YH60	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分长轴。	READY
6757_swb	6757	Van	HiAce III (H50/H60)	YH50	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6757_lwb	6757	Van	HiAce III (H50/H60)	YH60	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6758_swb	6758	Van	HiAce III (H50/H60)	LH50	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6758_lwb	6758	Van	HiAce III (H50/H60)	LH60	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6759_swb	6759	Van	HiAce III (H50/H60)	LH51	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6759_lwb	6759	Van	HiAce III (H50/H60)	LH61	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6765	6765	SUV	Land Cruiser 60	FJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	HIGH	FJ60五门汽油车型外廓。	READY
6768	6768	MPV	Previa I (XR10/XR20)		4	EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	MEDIUM	四驱车型外廓。	READY
6779	6779	Sedan	505 II		4	EU-PEUGEOT-505-I-SEDAN-TURBO-01	HIGH	四门Turbo Injection外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-404-CABRIOLET-2D-01	4490	1680	1430	Automobile-Catalog 1967 Peugeot 404 Cabriolet Super Luxe specifications	https://www.automobile-catalog.com/car/1967/2554910/peugeot_404_cabriolet_super_luxe.html
EU-TOYOTA-CORONA-VI-T130-SEDAN-4D-01	4290	1645	1410	Automobile-Catalog 1980 Toyota Corona Sedan 1.8 GL specifications	https://www.automobile-catalog.com/car/1980/3497225/toyota_corona_sedan_1_8_gl_automatic.html
EU-TOYOTA-CRESSIDA-II-X60-WAGON-PETROL-01	4645	1690	1470	Automobile-Catalog 1981 Toyota Cressida 2.0 DX Wagon specifications	https://www.automobile-catalog.com/car/1981/3477215/toyota_cressida_2_0_dx_wagon.html
EU-TOYOTA-CRESSIDA-II-X60-WAGON-DIESEL-01	4645	1690	1475	Automobile-Catalog 1981 Toyota Cressida 2.2 DX Wagon specifications	https://www.automobile-catalog.com/car/1981/3477260/toyota_cressida_2_2_dx_wagon.html
EU-TOYOTA-CROWN-VI-S110-WAGON-5D-01	4690	1690	1475	Automobile-Catalog 1981 Toyota Crown 2.8 Custom Wagon specifications	https://www.automobile-catalog.com/car/1981/3501200/toyota_crown_2_8_custom_wagon_automatic.html
EU-TOYOTA-CROWN-VII-S120-SEDAN-MS123-01	4860	1720	1435	Toyota 75 Years Vehicle Lineage seventh-generation Crown specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60005311A/
EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	4425	1690	1950	Toyota 75 Years Vehicle Lineage third-generation Hiace Van specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	4690	1690	1950	Toyota 75 Years Vehicle Lineage third-generation Hiace Van specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	4750	1800	1815	Toyota 75 Years Vehicle Lineage Land Cruiser 60 specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60013889/
```

## 下一步优先处理

1. 处理 Corolla III/IV 的早期 Sedan、Coupe、Wagon 与 Liftback 分支，以及 Corona Mark II。
2. 闭合 HiAce III 4WD Bus、HiAce IV Van 与 Land Cruiser 70 的 BJ70/BJ73/BJ75 分支。
3. 处理 Peugeot J5 后期 Bus、4×4 Van、底盘驾驶室的轴距与车顶组合。
4. 最后集中处理 Daimler Sovereign、Double Six、XJ40、X300/X308 的代际边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1967/2554910/peugeot_404_cabriolet_super_luxe.html?utm_source=chatgpt.com "1967 Peugeot 404 Cabriolet Super Luxe Specs Review (54.5 kW / 74 PS / 73 hp) (since September 1967 for Europe )"
[2]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60005311A/ "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* 新增完成 7 个 Ktype、7 条 READY 映射，首次创建 5 个尺寸组。
* Corolla III 的 KE35 双门硬顶车身确认为 3995 × 1570 × 1350 mm；E50 三门 Liftback 确认为 4120 × 1600 × 1320 mm。([丰田官方全球网站][1])
* Corolla KE36 Wagon 复用第三代 Corolla Van/Wagon 同一外廓，三维为 4050 × 1570 × 1390 mm。([丰田官方全球网站][2])
* Corona Mark II RX22 四门 Sedan 与 Corona RT104 四门 Sedan 分别闭合为 4325 × 1625 × 1390 mm、4250 × 1610 × 1390 mm。([丰田官方全球网站][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射行：88
* PENDING Ktype：27
* 当前已引用尺寸组：53
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6723	6723	Coupe	Corolla III (E30)	KE35	2	EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	HIGH	KE35双门硬顶轿跑外廓。	READY
6724	6724	Wagon	Corolla III (E30)	KE36	5	EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	HIGH	KE36五门旅行车外廓。	READY
6725	6725	Hatchback	Corolla III (E50)		3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	MEDIUM	三门Liftback外廓。	READY
6726	6726	Hatchback	Corolla III (E50)	TE51	3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	HIGH	TE51三门Liftback外廓。	READY
6727	6727	Hatchback	Corolla III (E50)	TE51	3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	HIGH	TE51三门Liftback外廓。	READY
6748	6748	Sedan	Corona Mark II II	RX22	4	EU-TOYOTA-CORONA-MARK-II-II-RX22-SEDAN-4D-01	HIGH	RX22四门轿车外廓。	READY
6749	6749	Sedan	Corona V	RT104	4	EU-TOYOTA-CORONA-V-RT104-SEDAN-4D-01	HIGH	RT104四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350	Toyota 75 Years Vehicle Lineage third-generation Corolla Hardtop specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003407/
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390	Toyota 75 Years Vehicle Lineage third-generation Corolla Van specifications; Bendix Toyota Corolla Wagon KE36 catalogue	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003414/index.html; https://www.bendix.com.au/catalogue/toyota/corolla/corolla-wagon-te72/12-ke36-ke30
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320	Toyota 75 Years Vehicle Lineage third-generation Corolla Liftback specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003472/index.html
EU-TOYOTA-CORONA-MARK-II-II-RX22-SEDAN-4D-01	4325	1625	1390	Toyota 75 Years Vehicle Lineage second-generation Toyopet Corona Mark II Sedan specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012964/
EU-TOYOTA-CORONA-V-RT104-SEDAN-4D-01	4250	1610	1390	Toyota 75 Years Vehicle Lineage fifth-generation Toyopet Corona Sedan specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60007675A/
```

## 下一步优先处理

1. 闭合 Ktype 6721 跨 Corolla E20/E30 的 Sedan 门数与物理分支。
2. 处理 HiAce III 4WD Bus、HiAce IV Van 和 Land Cruiser 70 柴油封闭车身。
3. 批量解决 Peugeot J5 后期 Bus、4×4 Van 与底盘驾驶室组合。
4. 集中处理剩余 Daimler Series I/II/III、XJ40、X300/X308 代际分支。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003407/ "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003414/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[3]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012964/?utm_source=chatgpt.com "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
## 更新点

* 新增完成 7 个 Ktype、7 条 READY 映射；首次创建 4 个 Daimler 尺寸组。
* Ktype 6767 确认为 Land Cruiser 70 系 BJ70 三门短轴封闭车身，直接复用既有尺寸组，不重复输出尺寸事实。
* Daimler XJ40 的 3.6、4.0 车型因标准车高不同，分别建组；XJ81 6.0 V12 的不含后视镜宽度为 1793 mm，单独建组。([汽车目录][1])
* 6819、6820 均确认属于 XJ Series III Double Six 5.3，复用同一外廓尺寸组。([汽车目录][2])
* 按原始 100 个 Ktype 重新机械计数，上一轮实际为 READY 72、PENDING 28；本轮更新后为 READY 79、PENDING 21。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射行：95
* PENDING Ktype：21
* 当前已引用尺寸组：58
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6767	6767	SUV	Land Cruiser 70	BJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	HIGH	BJ70三门短轴封闭车身。	READY
6807	6807	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-3-6-01	HIGH	XJ40四门3.6车型外廓。	READY
6808	6808	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-3-6-01	HIGH	XJ40四门3.6车型外廓。	READY
6809	6809	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-4-0-01	HIGH	XJ40四门4.0车型外廓。	READY
6819	6819	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-DOUBLE-SIX-SEDAN-01	HIGH	Series III四门Double Six外廓。	READY
6820	6820	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-DOUBLE-SIX-SEDAN-01	HIGH	Series III四门Double Six外廓。	READY
6821	6821	Sedan	Daimler XJ81	XJ81	4	EU-DAIMLER-XJ81-DOUBLE-SIX-SEDAN-01	HIGH	XJ81四门6.0 Double Six外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIMLER-XJ40-SEDAN-3-6-01	4988	1798	1380	Automobile-Catalog 1989 Daimler 3.6 specifications	https://www.automobile-catalog.com/car/1989/57920/daimler_3_6.html
EU-DAIMLER-XJ40-SEDAN-4-0-01	4988	1798	1358	Automobile-Catalog 1990 Daimler 4.0 catalyst specifications	https://www.automobile-catalog.com/car/1990/1283570/daimler_4_0_cat.html
EU-DAIMLER-XJ-SERIES-III-DOUBLE-SIX-SEDAN-01	4959	1770	1377	Automobile-Catalog 1992 Daimler Double Six catalyst specifications	https://www.automobile-catalog.com/car/1992/1281710/daimler_double_six_cat.html
EU-DAIMLER-XJ81-DOUBLE-SIX-SEDAN-01	4988	1793	1358	Auto-Data Daimler XJ40/XJ81 Double Six 6.0 specifications; Automobile-Catalog 1993 Daimler Double Six specifications	https://www.auto-data.net/en/daimler-xj-40-81-double-six-6.0-311hp-1116; https://www.automobile-catalog.com/car/1993/1284035/daimler_double_six.html
```

## 下一步优先处理

1. 处理 Daimler Sovereign 与 Double Six 的 Series I、Series II、Series III 跨代记录，以及 Ktype 6810 的 X300/X308 分支。
2. 闭合 Peugeot J5 后期 290P/290L Bus、Van、4×4 与底盘驾驶室外廓。
3. 处理 HiAce III 4WD Bus、HiAce IV Van，以及 Corolla Ktype 6721 的 E20/E30 跨代分支。
4. 完成剩余映射后立即执行一次机械闭合检查。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/57920/daimler_3_6.html?utm_source=chatgpt.com "1989 Daimler 3.6 Specs Review (165 kW / 224 PS / 221 hp) (up to mid-year 1989 for Europe )"
[2]: https://www.automobile-catalog.com/car/1992/1281710/daimler_double_six_cat.html?utm_source=chatgpt.com "1992 Daimler Double Six catalyst Specs Review (194 kW ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
## 更新点

* 完成 6 个 Ktype，共新增 7 条 READY 映射；剩余 PENDING 降至 15 个。
* Daimler XJ Series I、Series II 长轴和 Series III 三种外廓已闭合。Series II 四门轿车自 1974 年起统一采用长轴车身，Series II 长轴三维为 4945 × 1770 × 1375 mm。([jaguarheritage.com][1])
* Ktype 6817 的生产期跨越 Series II 与 Series III，按两种物理外廓拆分；Ktype 6818 直接复用既有 Series III Double Six 尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射行：102
* PENDING Ktype：15
* 当前已引用尺寸组：62
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6806	6806	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SOVEREIGN-SEDAN-LWB-01	HIGH	Series II长轴四门Sovereign外廓。	READY
6811	6811	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	MEDIUM	Series I四门Sovereign外廓。	READY
6812	6812	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SOVEREIGN-SEDAN-LWB-01	HIGH	Series II长轴四门Sovereign外廓。	READY
6814	6814	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SOVEREIGN-SEDAN-01	HIGH	Series III四门Sovereign外廓。	READY
6817_s2	6817	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-DOUBLE-SIX-SEDAN-LWB-01	HIGH	生产期跨越Series II与Series III，拆分Series II长轴外廓。	READY
6817_s3	6817	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-DOUBLE-SIX-SEDAN-01	HIGH	生产期跨越Series II与Series III，拆分Series III外廓。	READY
6818	6818	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-DOUBLE-SIX-SEDAN-01	HIGH	Series III四门Double Six H.E.外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	4813	1768	1341	Automobile-Catalog 1970 Daimler Sovereign 2.8 specifications	https://www.automobile-catalog.com/car/1970/1280660/daimler_sovereign_2_8.html
EU-DAIMLER-XJ-SERIES-II-SOVEREIGN-SEDAN-LWB-01	4945	1770	1375	Automobile-Catalog 1976 Daimler Sovereign 3.4 specifications; Jaguar Daimler Heritage Trust 1975 Daimler Sovereign Series 2	https://www.automobile-catalog.com/car/1976/1281050/daimler_sovereign_3_4.html; https://www.jaguarheritage.com/vehicle-collection/1975-daimler-sovereign-s2-4-2-litre-saloon-uev-34n/
EU-DAIMLER-XJ-SERIES-III-SOVEREIGN-SEDAN-01	4959	1770	1377	Automobile-Catalog 1979 Daimler Sovereign 4.2 specifications	https://www.automobile-catalog.com/car/1979/1281395/daimler_sovereign_4_2.html
EU-DAIMLER-XJ-SERIES-II-DOUBLE-SIX-SEDAN-LWB-01	4945	1770	1375	Automobile-Catalog 1977 Daimler Double Six specifications	https://www.automobile-catalog.com/car/1977/1281245/daimler_double_six.html
```

## 下一步优先处理

1. Daimler Ktype 6805、6813、6815、6816 的 Series I/II、标准轴距与 Vanden Plas 长轴分支。
2. Peugeot J5 Ktype 6791、6792、6795—6798 的第二期 4×4 Bus、Van 和底盘驾驶室。
3. Toyota HiAce Ktype 6756、6760、6761 的 4WD、轴距和车顶分支。
4. 最后处理 Corolla Ktype 6721 与 Daimler Ktype 6810 的跨代边界。

推进信号：CONTINUE

[1]: https://www.jaguarheritage.com/vehicle-collection/1975-daimler-sovereign-s2-4-2-litre-saloon-uev-34n/?utm_source=chatgpt.com "Jaguar Daimler Heritage Trust"
[2]: https://www.automobile-catalog.com/car/1977/1281245/daimler_double_six.html?utm_source=chatgpt.com "1977 Daimler Double Six Specs Review (212.5 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 续跑 ---
## 更新点

* 新增完成 6 个 Ktype、12 条 READY 映射；剩余 PENDING 降至 9 个。
* Ktype 6721 按 Corolla E20 与 E30 两代轿车外廓拆分；两代三维分别为 3945 × 1505 × 1375 mm、3995 × 1570 × 1375 mm。([丰田官方全球网站][1])
* Ktype 6805、6813、6815、6816 已按 Daimler XJ Series I/II 的标准轴距、长轴和 Vanden Plas 外廓拆分。Series II 标准轴距与长轴分别为 4843 × 1770 × 1375 mm、4945 × 1770 × 1375 mm。([汽车目录][2])
* Ktype 6810 确认为 X300 Daimler Six 4.0，使用 5024 × 1799 × 1314 mm 外廓。([汽车目录][3])
* 同一物理外廓的 Series II Sovereign/Double Six 和 Series III Sovereign/Double Six 已合并为通用尺寸组，替换此前按配置等级重复建立的尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：114
* PENDING Ktype：9
* 当前已引用尺寸组：65
* 本轮首次创建或修正尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6721_e20	6721	Sedan	Corolla II (E20)	KE20	4	EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	HIGH	生产期跨越E20与E30，拆分E20四门轿车外廓。	READY
6721_e30	6721	Sedan	Corolla III (E30)	KE30	4	EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	HIGH	生产期跨越E20与E30，拆分E30四门轿车外廓。	READY
6805_s1	6805	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	HIGH	生产期跨代，拆分Series I外廓。	READY
6805_s2_swb	6805	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	MEDIUM	生产期覆盖Series II早期标准轴距外廓。	READY
6805_s2_lwb	6805	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	MEDIUM	生产期覆盖Series II后期长轴外廓。	READY
6806	6806	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Series II长轴四门外廓。	READY
6810	6810	Sedan	Daimler X300	X300	4	EU-DAIMLER-X300-SEDAN-01	HIGH	Daimler Six 4.0对应X300四门标准轴距外廓。	READY
6812	6812	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Series II长轴四门外廓。	READY
6813_s2_swb	6813	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	HIGH	生产期覆盖Series II早期标准轴距外廓。	READY
6813_s2_lwb	6813	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	生产期覆盖Series II长轴外廓。	READY
6814	6814	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6815_standard	6815	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-SEDAN-SWB-01	HIGH	Double Six标准轴距外廓。	READY
6815_vdp	6815	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-VANDEN-PLAS-LWB-01	HIGH	Vanden Plas长轴外廓。	READY
6816_standard	6816	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Double Six标准轴距外廓。	READY
6816_vdp	6816	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Vanden Plas长轴外廓。	READY
6817_s2	6817	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	生产期跨代，Series II长轴外廓。	READY
6817_s3	6817	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	生产期跨代，Series III外廓。	READY
6818	6818	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6819	6819	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6820	6820	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375	Toyota 75 Years Vehicle Lineage second-generation Corolla Sedan specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003253/index.html
EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	4843	1770	1375	Automobile-Catalog 1974 Daimler Sovereign 4.2 specifications	https://www.automobile-catalog.com/car/1974/1280975/daimler_sovereign_4_2_automatic.html
EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375	Automobile-Catalog 1974 Daimler Sovereign 4.2 LWB specifications; Jaguar Daimler Heritage Trust Series II Sovereign	https://www.automobile-catalog.com/car/1974/1281005/daimler_sovereign_4_2_lwb_automatic.html; https://www.jaguarheritage.com/vehicle-collection/1975-daimler-sovereign-s2-4-2-litre-saloon-uev-34n/
EU-DAIMLER-XJ-SERIES-III-SEDAN-01	4959	1770	1377	Automobile-Catalog 1979 Daimler Sovereign 4.2 specifications	https://www.automobile-catalog.com/car/1979/1281395/daimler_sovereign_4_2.html
EU-DAIMLER-X300-SEDAN-01	5024	1799	1314	Automobile-Catalog 1995 Daimler Six automatic specifications	https://www.automobile-catalog.com/car/1995/1285730/daimler_six_automatic.html
EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-SEDAN-SWB-01	4814	1768	1343	Automobile-Catalog 1972 Daimler Double Six specifications	https://www.automobile-catalog.com/car/1972/1280930/daimler_double_six.html
EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-VANDEN-PLAS-LWB-01	4916	1768	1343	Automobile-Catalog 1972 Daimler Double Six Vanden Plas Saloon specifications	https://www.automobile-catalog.com/car/1972/1280945/daimler_double_six_vanden_plas_saloon.html
```

## 下一步优先处理

1. Toyota HiAce III 4WD Bus：Ktype 6756。
2. Toyota HiAce IV H100 Van：Ktype 6760、6761。
3. Peugeot J5 290P 4×4 Bus：Ktype 6791、6792。
4. Peugeot J5 290L 底盘驾驶室与 4×4 Van：Ktype 6795—6798。
5. 剩余 9 个 Ktype 闭合后立即生成两张最终完整 TSV 和指定下载文件。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003253/index.html?utm_source=chatgpt.com "Corolla - Toyota Motor Corporation Official Global Website"
[2]: https://www.automobile-catalog.com/car/1974/1280975/daimler_sovereign_4_2_automatic.html?utm_source=chatgpt.com "1974 Daimler Sovereign 4.2 automatic (aut. 3)"
[3]: https://www.automobile-catalog.com/car/1995/1285730/daimler_six_automatic.html?utm_source=chatgpt.com "1995 Daimler Six automatic Specs Review (177 kW ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 续跑 ---
## 更新点

* 闭合 Toyota HiAce III 4WD Bus、HiAce IV H100 Van，以及 Peugeot J5 290L 前驱底盘驾驶室，共完成 4 个 Ktype、5 条映射。
* HiAce III 4WD Bus 的 1987 年外廓为 4425 × 1690 × 1920 mm，与既有两驱 H50 MPV 高度 1890 mm 不同，因此新增独立 4WD 尺寸组，不覆盖既有组。([CarsGuide][1])
* HiAce IV 两个 Van Ktype 关联既有 H100 标准外廓组，不重复输出尺寸组。
* J5 290L 前驱底盘驾驶室继续沿用既有 SWB/LWB 外廓；J5 290P/290L 的 Dangel 4×4 车型仍需确认因离地间隙提升造成的整车高度及 Kasten 车长/车顶分支。资料已确认这些 Ktype 分别属于 290P Bus、290L Van 和 290L Chassis，但现有页面没有给出完整三维。([AUTODOC CLUB][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：119
* PENDING Ktype：5
* 已确认尺寸组：66
* 本轮首次创建尺寸组：1
* 剩余 PENDING：6791、6792、6796、6797、6798
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6756	6756	MPV	HiAce III (H50/H60)		4	EU-TOYOTA-HIACE-III-H50-MPV-4D-4WD-01	MEDIUM	四驱短轴四门客车外廓。	READY
6760	6760	Van	HiAce IV (H100)	H100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100四门厢式车标准外廓。	READY
6761	6761	Van	HiAce IV (H100)	H100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100四门厢式车标准外廓。	READY
6795_swb	6795	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6795_lwb	6795	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIACE-III-H50-MPV-4D-4WD-01	4425	1690	1920	CarsGuide 1987 Toyota HiAce dimensions	https://www.carsguide.com.au/toyota/hiace/car-dimensions/1987
```

## 下一步优先处理

1. 核对 J5 290P 的 2.5 D 4×4 与 2.5 TD 4×4 是否因轮胎、悬架和 Dangel 离地间隙形成不同整车高度。
2. 确认 J5 290L 4×4 Kasten 的短轴、长轴、普通顶及高顶实际覆盖分支。
3. 确认 J5 290L 4×4 底盘驾驶室的 SWB/LWB 整车高度；闭合剩余 5 个 Ktype 后立即生成最终完整 TSV。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/toyota/hiace/car-dimensions/1987?utm_source=chatgpt.com "Toyota HiAce Dimensions 1987 - Length, Width, Height ..."
[2]: https://club.autodoc.co.uk/tyres/peugeot/j5/j5-bus-290p "PEUGEOT J5 Minibus (290) tyre sizes and rim dimensions – recommended tyre and rim combination"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6301-6400_ktype_dimension_mapping_final.tsv
- all_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* 剩余 Ktype `6791`、`6792`、`6796`、`6797`、`6798` 已闭合，新增 12 条 READY 映射和 5 个尺寸组；底盘驾驶室分支复用既有 SWB/LWB 尺寸组。
* J5 290P Bus 和 290L Van/Platform 的 4×4 车型边界已确认；标准客车和普通顶车身尺寸分别按 4765 × 1965 × 2100 mm、4759 × 1965 × 2100 mm 闭合。([KMotorShop][1])
* 已完成机械检查：固定表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、三维和来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：131
* PENDING Ktype：0
* DIMENSION_GROUP：73
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6721_e20	6721	Sedan	Corolla II (E20)	KE20	4	EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	HIGH	生产期跨越E20与E30，拆分E20四门轿车外廓。	READY
6721_e30	6721	Sedan	Corolla III (E30)	KE30	4	EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	HIGH	生产期跨越E20与E30，拆分E30四门轿车外廓。	READY
6722	6722	Wagon	Logan I facelift	KS	5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	MCV五门改款外廓。	READY
6723	6723	Coupe	Corolla III (E30)	KE35	2	EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	HIGH	KE35双门硬顶轿跑外廓。	READY
6724	6724	Wagon	Corolla III (E30)	KE36	5	EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	HIGH	KE36五门旅行车外廓。	READY
6725	6725	Hatchback	Corolla III (E50)		3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	MEDIUM	三门Liftback外廓。	READY
6726	6726	Hatchback	Corolla III (E50)	TE51	3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	HIGH	TE51三门Liftback外廓。	READY
6727	6727	Hatchback	Corolla III (E50)	TE51	3	EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	HIGH	TE51三门Liftback外廓。	READY
6728_pre69	6728	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-PRE69-01	MEDIUM	生产期跨越1969年外廓变更，拆分前期。	READY
6728_post69	6728	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	MEDIUM	生产期跨越1969年外廓变更，拆分后期。	READY
6729	6729	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	HIGH	1971年后期四门外廓。	READY
6730	6730	Convertible	404		2	EU-PEUGEOT-404-CABRIOLET-2D-01	MEDIUM	双门敞篷外廓。	READY
6731	6731	Convertible	204		2	EU-PEUGEOT-204-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
6732	6732	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门GT掀背外廓。	READY
6733	6733	Sedan	Corolla IV (E70)		4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	E70四门轿车外廓。	READY
6734	6734	Sedan	Corolla IV (E70)		4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	E70四门轿车外廓。	READY
6735_3dr	6735	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分三门。	READY
6735_5dr	6735	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分五门。	READY
6736_3dr	6736	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分三门。	READY
6736_5dr	6736	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	原Ktype覆盖三门与五门车身，拆分五门。	READY
6737	6737	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6738	6738	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6739	6739	Sedan	Corolla V (E80)		4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	E80四门轿车外廓。	READY
6740_3dr	6740	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6740_5dr	6740	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6741_3dr	6741	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6741_5dr	6741	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6742_3dr	6742	Hatchback	Corolla V (E80)		3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	MEDIUM	原Ktype未限定门数，拆分三门紧凑掀背。	READY
6742_5dr	6742	Hatchback	Corolla V (E80)		5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	MEDIUM	原Ktype未限定门数，拆分五门掀背。	READY
6743	6743	Coupe	Corolla V (E80)	AE86	2	EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	HIGH	AE86双门后驱轿跑外廓。	READY
6744	6744	Sedan	Corolla VI (E90)	CE90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门柴油轿车外廓。	READY
6745	6745	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	HIGH	AE92三门GTI紧凑掀背外廓。	READY
6746	6746	Sedan	Corona VI (T130)		4	EU-TOYOTA-CORONA-VI-T130-SEDAN-4D-01	HIGH	T130四门轿车外廓。	READY
6748	6748	Sedan	Corona Mark II II	RX22	4	EU-TOYOTA-CORONA-MARK-II-II-RX22-SEDAN-4D-01	HIGH	RX22四门轿车外廓。	READY
6749	6749	Sedan	Corona V	RT104	4	EU-TOYOTA-CORONA-V-RT104-SEDAN-4D-01	HIGH	RT104四门轿车外廓。	READY
6750	6750	Wagon	Cressida II (X60)		5	EU-TOYOTA-CRESSIDA-II-X60-WAGON-PETROL-01	HIGH	汽油版五门旅行车外廓。	READY
6751	6751	Wagon	Cressida II (X60)		5	EU-TOYOTA-CRESSIDA-II-X60-WAGON-DIESEL-01	HIGH	柴油版五门旅行车外廓。	READY
6752	6752	Wagon	Crown VI (S110)		5	EU-TOYOTA-CROWN-VI-S110-WAGON-5D-01	HIGH	S110五门旅行车外廓。	READY
6753	6753	Sedan	Crown VII (S120)	MS123	4	EU-TOYOTA-CROWN-VII-S120-SEDAN-MS123-01	HIGH	MS123四门轿车外廓。	READY
6754_swb	6754	MPV	HiAce III (H50/H60)	LH50	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分短轴。	READY
6754_lwb	6754	MPV	HiAce III (H50/H60)	LH60	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分长轴。	READY
6755_swb	6755	MPV	HiAce III (H50/H60)	YH50	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分短轴。	READY
6755_lwb	6755	MPV	HiAce III (H50/H60)	YH60	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴客车，拆分长轴。	READY
6756	6756	MPV	HiAce III (H50/H60)		4	EU-TOYOTA-HIACE-III-H50-MPV-4D-4WD-01	MEDIUM	四驱短轴四门客车外廓。	READY
6757_swb	6757	Van	HiAce III (H50/H60)	YH50	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6757_lwb	6757	Van	HiAce III (H50/H60)	YH60	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6758_swb	6758	Van	HiAce III (H50/H60)	LH50	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6758_lwb	6758	Van	HiAce III (H50/H60)	LH60	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	HIGH	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6759_swb	6759	Van	HiAce III (H50/H60)	LH51	4	EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴厢式车，拆分短轴。	READY
6759_lwb	6759	Van	HiAce III (H50/H60)	LH61	4	EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴厢式车，拆分长轴。	READY
6760	6760	Van	HiAce IV (H100)	H100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100四门厢式车标准外廓。	READY
6761	6761	Van	HiAce IV (H100)	H100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100四门厢式车标准外廓。	READY
6762	6762	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	HIGH	F11五门M550d xDrive Touring外廓。	READY
6763_prefl	6763	Van	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	MEDIUM	生产期跨越外廓改款，拆分前期；厢式车复用同壳体组。	READY
6763_facelift	6763	Van	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	MEDIUM	生产期跨越外廓改款，拆分后期；厢式车复用同壳体组。	READY
6764	6764	MPV	LiteAce III (M30)	M30	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	HIGH	后期四门客车外廓。	READY
6765	6765	SUV	Land Cruiser 60	FJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	HIGH	FJ60五门汽油车型外廓。	READY
6766	6766	SUV	Land Cruiser 60	HJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	HIGH	60系五门自然吸气柴油外廓。	READY
6767	6767	SUV	Land Cruiser 70	BJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	HIGH	BJ70三门短轴封闭车身。	READY
6768	6768	MPV	Previa I (XR10/XR20)		4	EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	MEDIUM	四驱车型外廓。	READY
6769	6769	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6770	6770	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6771	6771	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6772	6772	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6773	6773	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH	504四门轿车外廓。	READY
6774	6774	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6775	6775	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6776	6776	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6777	6777	Wagon	504 Break		5	EU-PEUGEOT-504-BREAK-WAGON-5D-01	HIGH	504 Break五门旅行车外廓。	READY
6778	6778	Sedan	505 II		4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH	505 II标准四门轿车外廓。	READY
6779	6779	Sedan	505 II		4	EU-PEUGEOT-505-I-SEDAN-TURBO-01	HIGH	四门Turbo Injection外廓。	READY
6780_prefl	6780	Wagon	505 I		5	EU-PEUGEOT-505-I-BREAK-01	MEDIUM	生产期跨越代际改款，拆分505 I Break。	READY
6780_facelift	6780	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	MEDIUM	生产期跨越代际改款，拆分505 II Break。	READY
6781	6781	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6782	6782	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6783	6783	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH	505 II五门Break外廓。	READY
6784	6784	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6785	6785	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6786	6786	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6787	6787	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH	604四门轿车外廓。	READY
6788	6788	MPV	806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221平台五门MPV外廓。	READY
6789	6789	MPV	J5	280P	4	EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM	标准轴距客车外廓。	READY
6790	6790	MPV	J5	280P	4	EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM	标准轴距客车外廓。	READY
6791	6791	MPV	J5 II	290P	4	EU-PEUGEOT-J5-290P-MINIBUS-4X4-STANDARD-01	MEDIUM	290P四驱标准客车外廓。	READY
6792	6792	MPV	J5 II	290P	4	EU-PEUGEOT-J5-290P-MINIBUS-4X4-STANDARD-01	MEDIUM	290P四驱标准客车外廓。	READY
6793_swb	6793	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6793_lwb	6793	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
6794_swb	6794	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6794_lwb	6794	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
6795_swb	6795	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分短轴。	READY
6795_lwb	6795	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	原Ktype覆盖短轴与长轴底盘驾驶室，拆分长轴。	READY
6796_swb_lowroof	6796	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	原Ktype覆盖短轴普通顶外廓。	READY
6796_swb_highroof	6796	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	原Ktype覆盖短轴高顶外廓。	READY
6796_lwb_lowroof	6796	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	原Ktype覆盖长轴普通顶外廓。	READY
6796_lwb_highroof	6796	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	原Ktype覆盖长轴高顶外廓。	READY
6797_swb_lowroof	6797	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	原Ktype覆盖短轴普通顶外廓。	READY
6797_swb_highroof	6797	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	原Ktype覆盖短轴高顶外廓。	READY
6797_lwb_lowroof	6797	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	原Ktype覆盖长轴普通顶外廓。	READY
6797_lwb_highroof	6797	Van	J5 II	290L	4	EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	原Ktype覆盖长轴高顶外廓。	READY
6798_swb	6798	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	四驱底盘驾驶室覆盖短轴外廓。	READY
6798_lwb	6798	Pickup	J5 II	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	四驱底盘驾驶室覆盖长轴外廓。	READY
6799	6799	Wagon	Octavia II (1Z)	1Z5	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	HIGH	1Z5前期五门旅行车外廓。	READY
6800	6800	Wagon	Octavia II (1Z)	1Z5	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH	1Z5改款四驱旅行车外廓。	READY
6801	6801	Van	P 601	P601	3	EU-TRABANT-P601-UNIVERSAL-VAN-3D-01	MEDIUM	Kasten采用P601 Universal三门封闭式车身外廓。	READY
6802	6802	MPV	Galaxy II facelift	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6改款五门MPV外廓。	READY
6803	6803	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH	WA6五门MPV外廓。	READY
6804_prefl	6804	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	MEDIUM	生产期跨越改款尺寸变化，拆分前期。	READY
6804_facelift	6804	MPV	Grand C-Max II facelift		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	MEDIUM	生产期跨越改款尺寸变化，拆分后期。	READY
6805_s1	6805	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	HIGH	生产期跨代，拆分Series I外廓。	READY
6805_s2_swb	6805	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	MEDIUM	生产期覆盖Series II早期标准轴距外廓。	READY
6805_s2_lwb	6805	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	MEDIUM	生产期覆盖Series II后期长轴外廓。	READY
6806	6806	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Series II长轴四门外廓。	READY
6807	6807	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-3-6-01	HIGH	XJ40四门3.6车型外廓。	READY
6808	6808	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-3-6-01	HIGH	XJ40四门3.6车型外廓。	READY
6809	6809	Sedan	Daimler XJ40	XJ40	4	EU-DAIMLER-XJ40-SEDAN-4-0-01	HIGH	XJ40四门4.0车型外廓。	READY
6810	6810	Sedan	Daimler X300	X300	4	EU-DAIMLER-X300-SEDAN-01	HIGH	Daimler Six 4.0对应X300四门标准轴距外廓。	READY
6811	6811	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	MEDIUM	Series I四门Sovereign外廓。	READY
6812	6812	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Series II长轴四门外廓。	READY
6813_s2_swb	6813	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	HIGH	生产期覆盖Series II早期标准轴距外廓。	READY
6813_s2_lwb	6813	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	生产期覆盖Series II长轴外廓。	READY
6814	6814	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6815_standard	6815	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-SEDAN-SWB-01	HIGH	Double Six标准轴距外廓。	READY
6815_vdp	6815	Sedan	Daimler XJ Series I		4	EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-VANDEN-PLAS-LWB-01	HIGH	Vanden Plas长轴外廓。	READY
6816_standard	6816	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Double Six标准轴距外廓。	READY
6816_vdp	6816	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	Vanden Plas长轴外廓。	READY
6817_s2	6817	Sedan	Daimler XJ Series II		4	EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	HIGH	生产期跨代，Series II长轴外廓。	READY
6817_s3	6817	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	生产期跨代，Series III外廓。	READY
6818	6818	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6819	6819	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6820	6820	Sedan	Daimler XJ Series III		4	EU-DAIMLER-XJ-SERIES-III-SEDAN-01	HIGH	Series III四门外廓。	READY
6821	6821	Sedan	Daimler XJ81	XJ81	4	EU-DAIMLER-XJ81-DOUBLE-SIX-SEDAN-01	HIGH	XJ81四门6.0 Double Six外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6301-6400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375	Toyota 75 Years Vehicle Lineage second-generation Corolla Sedan; Auto-Data Toyota Corolla catalog	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003253/index.html; https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift generation	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-generation-8968
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350	Toyota 75 Years Vehicle Lineage third-generation Corolla Hardtop	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003407/
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390	Toyota 75 Years Vehicle Lineage third-generation Corolla Van; Bendix KE36 catalog	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003414/index.html; https://www.bendix.com.au/catalogue/toyota/corolla/corolla-wagon-te72/12-ke36-ke30
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320	Toyota 75 Years Vehicle Lineage third-generation Corolla Liftback	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003472/index.html
EU-PEUGEOT-404-I-SEDAN-PRE69-01	4420	1626	1450	Auto-Data Peugeot 404 Berline generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-404-berline-generation-8180
EU-PEUGEOT-404-I-SEDAN-POST69-01	4445	1626	1450	Auto-Data Peugeot 404 Berline generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-404-berline-generation-8180
EU-PEUGEOT-404-CABRIOLET-2D-01	4490	1680	1430	Automobile-Catalog 1967 Peugeot 404 Cabriolet Super Luxe	https://www.automobile-catalog.com/car/1967/2554910/peugeot_404_cabriolet_super_luxe.html
EU-PEUGEOT-204-CONVERTIBLE-2D-01	3740	1560	1320	Peugeot 204 model specifications; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-204-model-586
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380	Auto-Data Peugeot 309 facelift generation	https://www.auto-data.net/en/peugeot-309-model-578
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380	Auto-Data Peugeot 309 facelift generation	https://www.auto-data.net/en/peugeot-309-model-578
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360	Auto-Data Toyota Corolla generation catalog; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-corolla-model-407
EU-TOYOTA-CORONA-VI-T130-SEDAN-4D-01	4290	1645	1410	Automobile-Catalog 1980 Toyota Corona Sedan 1.8 GL	https://www.automobile-catalog.com/car/1980/3497225/toyota_corona_sedan_1_8_gl_automatic.html
EU-TOYOTA-CORONA-MARK-II-II-RX22-SEDAN-4D-01	4325	1625	1390	Toyota 75 Years Vehicle Lineage second-generation Corona Mark II Sedan	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012964/
EU-TOYOTA-CORONA-V-RT104-SEDAN-4D-01	4250	1610	1390	Toyota 75 Years Vehicle Lineage fifth-generation Corona Sedan	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60007675A/
EU-TOYOTA-CRESSIDA-II-X60-WAGON-PETROL-01	4645	1690	1470	Automobile-Catalog 1981 Toyota Cressida 2.0 DX Wagon	https://www.automobile-catalog.com/car/1981/3477215/toyota_cressida_2_0_dx_wagon.html
EU-TOYOTA-CRESSIDA-II-X60-WAGON-DIESEL-01	4645	1690	1475	Automobile-Catalog 1981 Toyota Cressida 2.2 DX Wagon	https://www.automobile-catalog.com/car/1981/3477260/toyota_cressida_2_2_dx_wagon.html
EU-TOYOTA-CROWN-VI-S110-WAGON-5D-01	4690	1690	1475	Automobile-Catalog 1981 Toyota Crown 2.8 Custom Wagon	https://www.automobile-catalog.com/car/1981/3501200/toyota_crown_2_8_custom_wagon_automatic.html
EU-TOYOTA-CROWN-VII-S120-SEDAN-MS123-01	4860	1720	1435	Toyota 75 Years Vehicle Lineage seventh-generation Crown	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60005311A/
EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	4425	1690	1890	Toyota HiAce generation specifications; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-hiace-model-393
EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	4690	1690	1890	Toyota HiAce generation specifications; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-hiace-model-393
EU-TOYOTA-HIACE-III-H50-MPV-4D-4WD-01	4425	1690	1920	CarsGuide 1987 Toyota HiAce dimensions	https://www.carsguide.com.au/toyota/hiace/car-dimensions/1987
EU-TOYOTA-HIACE-III-H50-VAN-4D-SWB-01	4425	1690	1950	Toyota 75 Years Vehicle Lineage third-generation HiAce Van	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-HIACE-III-H60-VAN-4D-LWB-01	4690	1690	1950	Toyota 75 Years Vehicle Lineage third-generation HiAce Van	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980	Auto-Data Toyota HiAce IV H100 generation	https://www.auto-data.net/en/toyota-hiace-iv-h100-generation-784
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462	BMW Group PressClub technical data: BMW M550d xDrive Touring	https://www.press.bmwgroup.com/deutschland/article/attachment/T0124400DE/183778
EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	4000	1650	1910	Auto-Data Toyota Lite Ace model; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-lite-ace-model-443
EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	3995	1650	1900	Auto-Data Toyota Lite Ace model; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-lite-ace-model-443
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	4750	1800	1815	Toyota 75 Years Vehicle Lineage Land Cruiser 60; cumulative DIMENSION_GROUP cache	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60013889/
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	4750	1800	1845	Toyota Land Cruiser J60 specifications; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-land-cruiser-model-438
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	3975	1690	1870	Auto-Data Toyota Land Cruiser J70/J73 generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-generation-939
EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	4750	1800	1780	Toyota Previa I specifications; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/toyota-previa-model-424
EU-PEUGEOT-504-SEDAN-01	4496	1689	1461	Auto-Data Peugeot 504 generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-504-generation-1251
EU-PEUGEOT-504-BREAK-WAGON-5D-01	4800	1690	1550	UltimateSpecs Peugeot 504 Break specifications	https://www.ultimatespecs.com/car-specs/Peugeot/M458/504-Break
EU-PEUGEOT-505-II-SEDAN-STANDARD-01	4579	1737	1432	Auto-Data Peugeot 505 model; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-505-model-584
EU-PEUGEOT-505-I-SEDAN-TURBO-01	4579	1737	1424	Auto-Data Peugeot 505 model; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-505-model-584
EU-PEUGEOT-505-I-BREAK-01	4898	1730	1540	Auto-Data Peugeot 505 Break 551D generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-505-break-551d-generation-1261
EU-PEUGEOT-505-II-BREAK-01	4901	1730	1540	Auto-Data Peugeot 505 Break 551D generation; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-505-break-551d-generation-1261
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430	Auto-Data Peugeot 604 generation	https://www.auto-data.net/en/peugeot-604-generation-1273
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Auto-Data Peugeot 806 model; cumulative DIMENSION_GROUP cache	https://www.auto-data.net/en/peugeot-806-model-580
EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	4765	1965	2100	Truck1 Peugeot J5 minibus technical specifications; cumulative DIMENSION_GROUP cache	https://www.truck1.eu/blog/peugeot-j5-minibus-2-5-d-73-hp-tech-specs-t30521
EU-PEUGEOT-J5-290P-MINIBUS-4X4-STANDARD-01	4765	1965	2100	Truck1 Peugeot J5 minibus dimensions; Spareto J5 290P 4x4 application	https://www.truck1.eu/blog/peugeot-j5-minibus-2-5-d-73-hp-tech-specs-t30521; https://spareto.com/products/hutchinson-mounting-manual-transmission/594265
EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	4712	1965	1900	Cumulative J5 chassis-cab DIMENSION_GROUP cache; Autocity J5 290L application	https://www.autocity.eu/en/types/2/1/12091/0/peugeot-j5-pianale-piatto-telaio-%28290l%29
EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	5489	1965	1900	Cumulative J5 chassis-cab DIMENSION_GROUP cache; Autocity J5 290L application	https://www.autocity.eu/en/types/2/1/12091/0/peugeot-j5-pianale-piatto-telaio-%28290l%29
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	4759	1965	2100	AutoCentrum Peugeot J5 body dimensions; Spareto J5 290L Van 4x4 application	https://www.autocentrum.pl/dane-techniczne/peugeot/j-5/; https://spareto.com/products/hutchinson-mounting-manual-transmission/594265
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	4759	1965	2420	WheelsAge Peugeot J5 high-roof dimensions; Spareto J5 290L Van 4x4 application	https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof/diesel/specifications; https://spareto.com/products/hutchinson-mounting-manual-transmission/594265
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	5489	1965	2100	AutoCentrum Peugeot J5 standard-roof dimensions; WheelsAge Peugeot J5 long-body specifications; Spareto J5 290L Van 4x4 application	https://www.autocentrum.pl/dane-techniczne/peugeot/j-5/; https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof_long/specifications; https://spareto.com/products/hutchinson-mounting-manual-transmission/594265
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	5489	1965	2420	WheelsAge Peugeot J5 high-roof long dimensions; Spareto J5 290L Van 4x4 application	https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof_long/specifications; https://spareto.com/products/hutchinson-mounting-manual-transmission/594265
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi specifications	https://www.auto-data.net/en/skoda-octavia-ii-combi-2.0-tdi-140hp-14230
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468	Auto-Data Skoda Octavia II Combi facelift 4x4 specifications	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-1.9-tdi-105hp-4x4-14204
EU-TRABANT-P601-UNIVERSAL-VAN-3D-01	3560	1510	1440	Auto-Data Trabant P 601 Universal generation	https://www.auto-data.net/en/trabant-p-601-universal-generation-1189
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764	Auto-Data Ford Galaxy II facelift generation	https://www.auto-data.net/en/ford-galaxy-ii-facelift-2010-generation-10039
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658	Auto-Data Ford S-MAX first generation	https://www.auto-data.net/en/ford-s-max-generation-1780
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Auto-Data Ford Grand C-MAX II specifications	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratec-ti-vct-105hp-19814
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642	Auto-Data Ford Grand C-MAX II facelift generation	https://www.auto-data.net/en/ford-grand-c-max-ii-facelift-2015-generation-4479
EU-DAIMLER-XJ-SERIES-I-SOVEREIGN-SEDAN-01	4813	1768	1341	Automobile-Catalog 1970 Daimler Sovereign 2.8	https://www.automobile-catalog.com/car/1970/1280660/daimler_sovereign_2_8.html
EU-DAIMLER-XJ-SERIES-II-SEDAN-SWB-01	4843	1770	1375	Automobile-Catalog 1974 Daimler Sovereign 4.2	https://www.automobile-catalog.com/car/1974/1280975/daimler_sovereign_4_2_automatic.html
EU-DAIMLER-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375	Automobile-Catalog 1974 Daimler Sovereign 4.2 LWB; Jaguar Daimler Heritage Trust Series II Sovereign	https://www.automobile-catalog.com/car/1974/1281005/daimler_sovereign_4_2_lwb_automatic.html; https://www.jaguarheritage.com/vehicle-collection/1975-daimler-sovereign-s2-4-2-litre-saloon-uev-34n/
EU-DAIMLER-XJ40-SEDAN-3-6-01	4988	1798	1380	Automobile-Catalog 1989 Daimler 3.6	https://www.automobile-catalog.com/car/1989/57920/daimler_3_6.html
EU-DAIMLER-XJ40-SEDAN-4-0-01	4988	1798	1358	Automobile-Catalog 1990 Daimler 4.0 catalyst	https://www.automobile-catalog.com/car/1990/1283570/daimler_4_0_cat.html
EU-DAIMLER-X300-SEDAN-01	5024	1799	1314	Automobile-Catalog 1995 Daimler Six automatic	https://www.automobile-catalog.com/car/1995/1285730/daimler_six_automatic.html
EU-DAIMLER-XJ-SERIES-III-SEDAN-01	4959	1770	1377	Automobile-Catalog 1979 Daimler Sovereign 4.2	https://www.automobile-catalog.com/car/1979/1281395/daimler_sovereign_4_2.html
EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-SEDAN-SWB-01	4814	1768	1343	Automobile-Catalog 1972 Daimler Double Six	https://www.automobile-catalog.com/car/1972/1280930/daimler_double_six.html
EU-DAIMLER-XJ-SERIES-I-DOUBLE-SIX-VANDEN-PLAS-LWB-01	4916	1768	1343	Automobile-Catalog 1972 Daimler Double Six Vanden Plas Saloon	https://www.automobile-catalog.com/car/1972/1280945/daimler_double_six_vanden_plas_saloon.html
EU-DAIMLER-XJ81-DOUBLE-SIX-SEDAN-01	4988	1793	1358	Auto-Data Daimler XJ40/XJ81 Double Six 6.0; Automobile-Catalog 1993 Daimler Double Six	https://www.auto-data.net/en/daimler-xj-40-81-double-six-6.0-311hp-1116; https://www.automobile-catalog.com/car/1993/1284035/daimler_double_six.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6301-6400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.kmotorshop.com/en/device/car-list/1703?utm_source=chatgpt.com "Cars PEUGEOT J5 Platform/Chassis (290L) | K MOTORSHOP s.r.o."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6301-6400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6301-6400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8047 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2468 行）

