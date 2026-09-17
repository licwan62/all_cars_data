# 任务：all 第 6901-7000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0070__e716ddf7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6901-7000 行

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
all 第 6901-7000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6901-7000_ktype_dimension_mapping_final.tsv
- all_6901-7000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8L-HATCHBACK-3D-01	4152	1735	1427
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150
EU-DACIA-1300-SEDAN-4D-01	4340	1636	1434
EU-DACIA-1310-SEDAN-EARLY-4D-01	4340	1636	1430
EU-DACIA-1310-SEDAN-LATE-4D-01	4351	1660	1435
EU-DACIA-1310-SEDAN-MID-4D-01	4390	1615	1440
EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	3971	1613	1250
EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	3971	1613	1250
EU-FIAT-128-3P-BERLINETTA-COUPE-01	3826	1560	1310
EU-FIAT-128-S1-SEDAN-2D-01	3840	1590	1420
EU-FIAT-128-S1-SEDAN-4D-01	3840	1590	1420
EU-FIAT-128-S2-SEDAN-2D-01	3860	1590	1420
EU-FIAT-128-S2-SEDAN-4D-01	3860	1590	1420
EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	4264	1650	1400
EU-FIAT-131-S1-MIRAFIORI-SEDAN-2D-STD-01	4238	1632	1400
EU-FIAT-131-S1-MIRAFIORI-SEDAN-4D-STD-01	4238	1632	1400
EU-FIAT-131-S2-MIRAFIORI-SEDAN-2D-STD-01	4264	1651	1381
EU-FIAT-131-S2-MIRAFIORI-SEDAN-4D-STD-01	4264	1651	1381
EU-FIAT-131-S2-SEDAN-2D-RACING-01	4231	1663	1400
EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	4231	1651	1381
EU-FIAT-131-S3-MIRAFIORI-CL-SEDAN-4D-01	4264	1645	1411
EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	4264	1650	1400
EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	4231	1645	1405
EU-FIAT-132-S3-SEDAN-4D-2000-01	4404	1641	1425
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410
EU-FIAT-REGATA-WEEKEND-WAGON-01	4267	1650	1450
EU-FIAT-RITMO-138A-CABRIOLET-01	4014	1650	1400
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	3937	1688	1390
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	3937	1650	1400
EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	3937	1650	1400
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	4014	1663	1390
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	4014	1663	1363
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	4014	1650	1405
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	4014	1650	1405
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	4014	1650	1407
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	3993	1663	1390
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	3993	1650	1410
EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	4630	1864	1379
EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	4448	1702	1393
EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	4420	1700	1393
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457
EU-LADA-NOVA-2104-WAGON-5D-01	4115	1620	1443
EU-LADA-NOVA-2105-SEDAN-4D-01	4130	1620	1446
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402
EU-LADA-SAMARA-I-HATCHBACK-5D-01	4006	1650	1402
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	4680	1750	1400
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486
EU-MINI-MINI-R53-HATCHBACK-3D-01	3655	1688	1416
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-NISSAN-TERRANO-II-R20-SUV-3D-01	4105	1735	1805
EU-NISSAN-TERRANO-II-R20-SUV-5D-01	4585	1735	1810
EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	4365	1690	1680
EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	4365	1690	1680
EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	4520	1732	1435
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435
EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	4500	1732	1431
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431
EU-SAAB-900-I-CONVERTIBLE-01	4680	1690	1420
EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	4687	1690	1420
EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	4687	1690	1420
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-3D-01	4687	1693	1420
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-5D-01	4687	1693	1420
EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	4687	1695	1405
EU-SAAB-900-II-CONVERTIBLE-2D-01	4637	1711	1435
EU-SAAB-900-II-HATCHBACK-3D-01	4637	1711	1436
EU-SAAB-900-II-HATCHBACK-5D-01	4637	1711	1436
EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	4740	1690	1420
EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-SEDAN-4D-01	4740	1690	1420
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-3D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-5D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-TURBO16S-HATCHBACK-3D-01	4740	1690	1425
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	4360	1630	1395
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	4230	1630	1390
EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	4370	1630	1400
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	4360	1670	1365
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	4330	1670	1365
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	4370	1670	1365
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	4350	1670	1365
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	4390	1670	1365
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	4360	1670	1365
EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	4390	1670	1365
EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	4440	1690	1370
EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	4440	1690	1370
EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	4435	1690	1400
EU-VOLVO-760-SEDAN-FACELIFT-01	4790	1760	1410
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410
EU-VOLVO-760-WAGON-FACELIFT-01	4790	1760	1435
EU-VOLVO-760-WAGON-FACELIFT-02	4785	1761	1435
EU-VOLVO-760-WAGON-PREFL-01	4800	1750	1435
EU-VOLVO-S70-I-SEDAN-4D-01	4720	1760	1400
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Saab	900 i combi coupe	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	110	150	Jan 1986	Dec 1988	2024-03-01	7356
Saab	900 i	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1986	Dec 1988	2024-03-01	7357
Saab	900 i	2.0 EMS	Stufenheck	Frontantrieb	Benzin	87	118	Jan 1979	Dec 1980	2024-03-01	7358
Saab	96	1.5 V4	Schrägheck	Frontantrieb	Benzin	48	65	Oct 1965	Oct 1975	2024-03-01	7359
Volvo	340-360	2	Stufenheck	Heckantrieb	Benzin	83	113	Aug 1983	Jul 1984	2024-03-01	7360
Volvo	760	2.8	Stufenheck	Heckantrieb	Benzin	95	130	Jan 1982	Dec 1987	2024-03-01	7361
Saab	900 ii	2.0 I	Coupe	Frontantrieb	Benzin	96	131	Aug 1994	Feb 1998	2024-03-01	7363
Saab	900 ii	2.0 -16 Turbo	Coupe	Frontantrieb	Benzin	136	185	Dec 1993	Feb 1998	2024-03-01	7364
Saab	900 ii	2.3 -16	Coupe	Frontantrieb	Benzin	110	150	Dec 1993	Feb 1998	2024-03-01	7365
Saab	900 ii	2.5 -24 V6	Coupe	Frontantrieb	Benzin	125	170	Dec 1993	Feb 1998	2024-03-01	7366
Saab	96	1.5 V4	Schrägheck	Frontantrieb	Benzin	46	63	Nov 1975	Jul 1977	2024-03-01	7367
Saab	96	1.5 V4	Schrägheck	Frontantrieb	Benzin	50	68	Aug 1977	Aug 1980	2024-03-01	7368
Saab	95 station wagon	1.5 V4	Kombi	Frontantrieb	Benzin	48	65	Oct 1965	Dec 1975	2024-03-01	7369
Saab	95 station wagon	1.5 V4	Kombi	Frontantrieb	Benzin	46	63	Jan 1976	Aug 1977	2024-03-01	7370
Saab	95 station wagon	1.5 V4	Kombi	Frontantrieb	Benzin	50	68	Sep 1977	Dec 1978	2024-03-01	7371
Volvo	V70 i	2.0 Turbo	Kombi	Frontantrieb	Benzin	155	211	Dec 1995	Mar 2000	2024-03-01	7372
Volvo	S70	2	Stufenheck	Frontantrieb	Benzin	105	143	Jan 1997	Nov 2000	2024-03-01	7373
Volvo	S70	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	155	210	Jan 1997	Nov 2000	2024-03-01	7374
Volvo	S70	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	184	250	Jan 1997	Nov 2000	2024-03-01	7375
Volvo	V70 i	2	Kombi	Frontantrieb	Benzin	105	143	Dec 1995	Mar 2000	2024-03-01	7376
Volvo	V70 i	2.3 Turbo	Kombi	Frontantrieb	Benzin	184	250	Dec 1995	Mar 2000	2024-03-01	7377
Audi	A3	1.9 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Aug 1997	Jul 2001	2024-03-01	7378
Citroën	Jumper i	2.5 D 4X4	Bus	Allrad	Diesel	63	86	Aug 1996	Apr 2002	2024-03-01	7379
Citroën	Jumper i	1.9 TD 4X4	Bus	Allrad	Diesel	68	92	Aug 1996	Apr 2002	2024-03-01	7380
Citroën	Jumper i	2.5 TD 4X4	Bus	Allrad	Diesel	76	103	Aug 1996	Apr 2002	2024-03-01	7381
Citroën	Jumper i	2.0 4X4	Bus	Allrad	Benzin	80	109	Aug 1996	Apr 2002	2024-03-01	7382
Fiat	124	1800 Rally Abarth	Cabriolet	Heckantrieb	Benzin	94	128	Sep 1972	Jul 1975	2024-03-01	7383
Fiat	124	1800 Sport	Cabriolet	Heckantrieb	Benzin	82	112	Jan 1973	Jul 1975	2024-03-01	7384
Fiat	124	1200	Kombi	Heckantrieb	Benzin	44	60	Apr 1967	May 1973	2024-03-01	7385
Fiat	124	1400 Sport	Coupe	Heckantrieb	Benzin	66	90	Jun 1967	Oct 1972	2024-03-01	7386
Fiat	124	1600	Coupe	Heckantrieb	Benzin	81	110	Apr 1970	Oct 1973	2024-03-01	7387
Fiat	124	1600	Coupe	Heckantrieb	Benzin	74	100	Nov 1971	Oct 1973	2024-03-01	7388
Fiat	124	1800 Sport	Coupe	Heckantrieb	Benzin	87	118	Jan 1973	Feb 1976	2024-03-01	7389
Fiat	124	1200	Stufenheck	Heckantrieb	Benzin	48	65	Sep 1967	Jul 1975	2024-03-01	7390
Fiat	124	1500 Special T	Stufenheck	Heckantrieb	Benzin	59	80	Jan 1971	Jul 1975	2024-03-01	7391
Fiat	124	1400 Special	Stufenheck	Heckantrieb	Benzin	55	75	Jan 1971	Jul 1975	2024-03-01	7392
Fiat	124	1400 Special	Stufenheck	Heckantrieb	Benzin	51	70	Dec 1968	Dec 1972	2024-03-01	7393
Fiat	124	1600 Special T	Stufenheck	Heckantrieb	Benzin	70	95	Jan 1973	Jul 1975	2024-03-01	7395
Fiat	128	1.3 Rally	Stufenheck	Frontantrieb	Benzin	49	67	Jul 1971	Feb 1976	2024-03-01	7398
Fiat	128	1.3	Coupe	Frontantrieb	Benzin	55	75	Mar 1972	Dec 1979	2024-03-01	7399
Fiat	128	1.1	Coupe	Frontantrieb	Benzin	47	64	Mar 1972	Feb 1981	2024-03-01	7400
Fiat	128	1.1	Coupe	Frontantrieb	Benzin	48	65	Aug 1975	Feb 1981	2024-03-01	7401
Fiat	128	1.1	Kombi	Frontantrieb	Benzin	33	45	Feb 1975	Feb 1981	2024-03-01	7402
Fiat	128	1.3	Kombi	Frontantrieb	Benzin	44	60	Dec 1974	Oct 1982	2024-03-01	7403
Fiat	128	1.1	Kombi	Frontantrieb	Benzin	40	55	Oct 1969	Oct 1982	2024-03-01	7404
Hyundai	Genesis	3.8 V6	Coupe	Heckantrieb	Benzin	223	303	Jan 2008	Feb 2014	2024-03-01	7405
Fiat	130	3.2	Stufenheck	Heckantrieb	Benzin	121	165	Dec 1971	Mar 1978	2024-03-01	7406
Fiat	130	3.2	Coupe	Heckantrieb	Benzin	121	165	Oct 1971	Mar 1978	2024-03-01	7407
Hyundai	Lantra ii	1.8 16V	Kombi	Frontantrieb	Benzin	94	128	Feb 1996	Oct 2000	2024-03-01	7408
Renault	20	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1975	May 1977	2024-03-01	7409
Renault	30	2.6	Schrägheck	Frontantrieb	Benzin	92	125	Aug 1976	Aug 1978	2024-03-01	7410
Renault	12	1.3	Kombi	Frontantrieb	Benzin	44	60	Aug 1973	Aug 1980	2024-03-01	7411
Dacia	1300	1.3	Kombi	Frontantrieb	Benzin	40	54	Dec 1972	May 1983	2024-03-01	7413
Dacia	1310	1.3	Kombi	Frontantrieb	Benzin	40	54	May 1983	Jul 2004	2024-03-01	7414
Mazda	626 iv	2.0 I 4WD	Stufenheck	Allrad	Benzin	85	116	Apr 1992	Apr 1997	2024-03-01	7415
Mazda	626 iii station wagon	2.2 12V 4WD	Kombi	Allrad	Benzin	85	116	May 1991	Nov 1992	2024-03-01	7416
Mazda	626 iv hatchback	2.0 I 4WD	Schrägheck	Allrad	Benzin	85	116	Apr 1992	Apr 1997	2024-03-01	7417
Fiat	131	1.6 Super Mirafiori	Stufenheck	Heckantrieb	Benzin	72	98	Mar 1979	Mar 1982	2024-03-01	7419
Hyundai	Equus / centennial	4.6 V8	Stufenheck	Heckantrieb	Benzin	274	373	Mar 2009	Dec 2016	2024-05-01	7421
Fiat	131	2.5 Super Diesel	Kombi	Heckantrieb	Diesel	53	72	Mar 1979	Dec 1984	2024-03-01	7422
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	147	200	Aug 2010	Oct 2016	2024-03-01	7423
Fiat	Argenta	2000	Stufenheck	Heckantrieb	Benzin	83	113	Jun 1978	Dec 1985	2024-03-01	7425
Fiat	Argenta	1600	Stufenheck	Heckantrieb	Benzin	72	98	Apr 1981	Dec 1985	2024-03-01	7426
Fiat	Argenta	2500 Turbodiesel	Stufenheck	Heckantrieb	Diesel	66	90	Jul 1983	Aug 1985	2024-03-01	7427
Fiat	132	1.6	Stufenheck	Heckantrieb	Benzin	65	88	May 1977	Sep 1982	2024-03-01	7428
Fiat	132	1.7 GLS	Stufenheck	Heckantrieb	Benzin	79	107	Apr 1974	Dec 1975	2024-03-01	7429
Fiat	132	1.7 Special	Stufenheck	Heckantrieb	Benzin	77	105	Apr 1972	Jan 1974	2024-03-01	7430
Fiat	132	1.6	Stufenheck	Heckantrieb	Benzin	72	98	Jan 1976	Dec 1982	2024-03-01	7431
Fiat	132	1.6	Stufenheck	Heckantrieb	Benzin	72	98	Apr 1972	Jan 1976	2024-03-01	7432
Fiat	132	1.6	Stufenheck	Heckantrieb	Benzin	66	90	Mar 1977	Dec 1981	2024-03-01	7433
Fiat	132	1.7 GLS	Stufenheck	Heckantrieb	Benzin	82	112	Nov 1975	Jan 1977	2024-03-01	7434
Fiat	132	2.0 I.e.	Stufenheck	Heckantrieb	Benzin	90	122	Jan 1980	Dec 1982	2024-03-01	7435
Nissan	Terrano	3.0 I 4WD	Geländewagen geschlossen	Allrad	Benzin	109	148	Jan 1990	Dec 1995	2024-03-01	7436
Toyota	Carina ii	1.8	Stufenheck	Heckantrieb	Benzin	57	78	Jan 1978	May 1983	2024-03-01	7437
Toyota	Carina iii	1.8	Kombi	Heckantrieb	Benzin	57	78	Aug 1982	Dec 1982	2024-03-01	7438
Fiat	Croma	2500 V6	Schrägheck	Frontantrieb	Benzin	119	162	Jun 1993	Aug 1996	2024-03-01	7439
Fiat	Croma	2000 I.e. Turbo	Schrägheck	Frontantrieb	Benzin	111	151	Nov 1986	Nov 1988	2024-03-01	7440
Fiat	Regata	75 1.5	Stufenheck	Frontantrieb	Benzin	55	75	Dec 1983	Jul 1989	2024-03-01	7441
Lada	Samara	1300	Stufenheck	Frontantrieb	Benzin	45	61	Jul 1991	Aug 1999	2024-03-01	7442
Lada	Samara	1500	Stufenheck	Frontantrieb	Benzin	50	68	Jul 1991	Dec 1996	2024-03-01	7443
Fiat	Regata	100 1.6	Kombi	Frontantrieb	Benzin	74	101	Sep 1984	Dec 1990	2024-03-01	7444
Lada	Samara	1100	Schrägheck	Frontantrieb	Benzin	43	58	Feb 1996	Aug 1999	2024-03-01	7445
Fiat	Regata	85 1.6	Stufenheck	Frontantrieb	Benzin	60	82	Oct 1983	Jun 1990	2024-03-01	7446
Lada	Nova	1600	Stufenheck	Heckantrieb	Benzin	56	76	Jan 1988	Oct 2001	2024-03-01	7447
Lada	Samara	1100	Stufenheck	Frontantrieb	Benzin	39	53	Jul 1991	Aug 1999	2024-03-01	7448
Lada	Samara	1300	Stufenheck	Frontantrieb	Benzin	50	68	Jun 1995	Dec 2006	2024-03-01	7449
Mini	Mini	Cooper S JCW	Coupe	Frontantrieb	Benzin	147	200	Dec 2010	Apr 2015	2024-03-01	7450
Fiat	Ritmo	1.5	Schrägheck	Frontantrieb	Benzin	58	79	Aug 1985	May 1987	2024-03-01	7452
Moskvich	403	E 1.4	Stufenheck	Heckantrieb	Benzin	33	45	Mar 1962	Sep 1968	2024-03-01	7453
Moskvich	403	I E 1.4	Stufenheck	Heckantrieb	Benzin	33	45	Feb 1964	Sep 1968	2024-03-01	7454
Moskvich	423	1.4	Kombi	Heckantrieb	Benzin	33	45	Aug 1959	Sep 1965	2024-03-01	7455
Mercedes-benz	S-Klasse	S 63 AMG	Stufenheck	Heckantrieb	Benzin	420	571	Feb 2012	Dec 2013	2024-03-01	7456
Moskvich	407	1.4	Stufenheck	Heckantrieb	Benzin	33	45	Aug 1958	Sep 1969	2024-03-01	7457
Fiat	Ritmo	100 1.6	Cabriolet	Frontantrieb	Benzin	74	100	Oct 1985	Dec 1987	2024-03-01	7458
Mercedes-benz	M-Klasse	ML 500 4-matic	SUV	Allrad	Benzin	300	408	Feb 2012	Feb 2015	2024-03-01	7459
Moskvich	427	1.5	Kombi	Heckantrieb	Benzin	55	75	Jan 1975	Sep 1979	2024-03-01	7460
Moskvich	412	1.5	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1971	Oct 1988	2024-03-01	7461
Moskvich	Aslk 2140	1.5	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1976	Oct 1988	2024-03-01	7462
Moskvich	Aslk 2137	1.5	Kombi	Heckantrieb	Benzin	55	75	Jul 1976	Aug 1987	2024-03-01	7463
Moskvich	2141	1.5	Schrägheck	Frontantrieb	Benzin	51	69	May 1989	Dec 2001	2024-03-01	7464


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类处理全部 100 个输入 Ktype，形成 136 条映射：127 条 `READY`、9 条 `PENDING`。
* 本轮首次闭合 49 个尺寸组，另有 38 个尺寸组直接复用跨批次缓存，不在本轮 DIMENSION_GROUP 增量表中重复输出。
* MINI Clubman R55 官方技术表确认 Cooper S Clubman 为 5 门，三维为 3961 × 1683 × 1432 mm；MINI Coupé 官方资料明确列出 JCW Coupé 为 3758 × 1683 × 1384 mm，并将含后视镜宽度单列为 1892 mm。([BMW Group PressClub][1])
* Mercedes-Benz ML 500 W166 采用 4804 × 1926 × 1796 mm，来源明确将 1926 mm 标记为不含后视镜宽度；Fiat 130 Coupé 的来源同样明确标记不含后视镜宽度。([汽车目录][2])
* 剩余阻塞项集中于 Jumper I 4X4 改装底盘、Dacia 1310 长生产区间、后驱 Carina A60 Wagon、Lada Nova 1600，以及 Moskvich 427/412 的跨期车身边界。

## 当前批次进度

* 输入 Ktype：100
* 已输出映射：136
* READY 映射：127
* PENDING 映射：9
* READY Ktype：91
* PENDING Ktype：9
* 当前映射引用的已确认尺寸组：87
* 本轮首次创建尺寸组：49
* 本轮复用既有尺寸组：38
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7356_3dr_prefl	7356	Hatchback	Saab 900 I		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与改款前分支。	READY
7356_5dr_prefl	7356	Hatchback	Saab 900 I		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype未区分五门与改款前分支。	READY
7356_3dr_facelift	7356	Hatchback	Saab 900 I		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与改款后分支。	READY
7356_5dr_facelift	7356	Hatchback	Saab 900 I		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype未区分五门与改款后分支。	READY
7357_prefl	7357	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	HIGH	生产区间跨改款，保留改款前分支。	READY
7357_facelift	7357	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，保留改款后分支。	READY
7358	7358	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-PRE83-01	HIGH		READY
7359_early	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7359_mid	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-MID-01	MEDIUM	输入区间覆盖中期车身。	READY
7359_late	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-LATE-01	MEDIUM	输入区间覆盖后期窄保险杠车身。	READY
7360	7360	Sedan	Volvo 300 Series	344	4	EU-VOLVO-360-344-SEDAN-4D-01	HIGH		READY
7361	7361	Sedan	Volvo 760	704	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH		READY
7363	7363	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7364	7364	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7365	7365	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7366	7366	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7367	7367	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	HIGH	后期大型保险杠车身。	READY
7368	7368	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	HIGH	后期大型保险杠车身。	READY
7369_early	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7369_mid	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-MID-01	MEDIUM	输入区间覆盖中期车身。	READY
7369_late	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	MEDIUM	输入区间覆盖后期车身。	READY
7370	7370	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	HIGH		READY
7371	7371	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	HIGH		READY
7372	7372	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7373	7373	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7374	7374	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7375	7375	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7376	7376	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7377	7377	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7378	7378	Hatchback	Audi A3 8L	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
7379	7379	MPV	Citroën Jumper I	230P			LOW	候选为230P的SWB/MWB与低顶/高顶分支。	PENDING: 4X4改装底盘的总高及轴距/车顶分支尚未与既有普通底盘尺寸组闭合
7380	7380	MPV	Citroën Jumper I	230P			LOW	候选为230P的SWB/MWB与低顶/高顶分支。	PENDING: 4X4改装底盘的总高及轴距/车顶分支尚未与既有普通底盘尺寸组闭合
7381	7381	MPV	Citroën Jumper I	230P			LOW	候选为230P的SWB/MWB与低顶/高顶分支。	PENDING: 4X4改装底盘的总高及轴距/车顶分支尚未与既有普通底盘尺寸组闭合
7382	7382	MPV	Citroën Jumper I	230P			LOW	候选为230P的SWB/MWB与低顶/高顶分支。	PENDING: 4X4改装底盘的总高及轴距/车顶分支尚未与既有普通底盘尺寸组闭合
7383	7383	Convertible	Fiat 124 Sport Spider		2	EU-FIAT-124-RALLY-ABARTH-CONVERTIBLE-2D-01	HIGH		READY
7384	7384	Convertible	Fiat 124 Sport Spider I		2	EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	HIGH		READY
7385_early	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-EARLY-01	MEDIUM	生产区间覆盖早期车身。	READY
7385_mid	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-MID-01	MEDIUM	生产区间覆盖中期车身。	READY
7385_late	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-LATE-01	MEDIUM	生产区间覆盖后期车身。	READY
7386_ac	7386	Coupe	Fiat 124 Sport Coupé	AC	2	EU-FIAT-124-COUPE-AC-2D-01	MEDIUM	生产区间覆盖AC车身。	READY
7386_bc	7386	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7387_bc	7387	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7387_cc	7387	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	MEDIUM	生产区间覆盖CC车身。	READY
7388_bc	7388	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7388_cc	7388	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	MEDIUM	生产区间覆盖CC车身。	READY
7389	7389	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	HIGH		READY
7390_early	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-EARLY-01	MEDIUM	生产区间覆盖早期标准车身。	READY
7390_mid	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-MID-01	MEDIUM	生产区间覆盖中期标准车身。	READY
7390_late	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-LATE-01	MEDIUM	生产区间覆盖后期标准车身。	READY
7391	7391	Sedan	Fiat 124 Special T		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7392	7392	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7393_early	7393	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-EARLY-01	MEDIUM	生产区间覆盖早期Special车身。	READY
7393_late	7393	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	MEDIUM	生产区间覆盖后期Special车身。	READY
7395	7395	Sedan	Fiat 124 Special T		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7398	7398	Sedan	Fiat 128 Series 1		2	EU-FIAT-128-RALLY-S1-SEDAN-2D-01	HIGH		READY
7399_sport_early	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	MEDIUM	生产区间覆盖早期Sport Coupé车身。	READY
7399_sport_mid	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-MID-01	MEDIUM	生产区间覆盖中期Sport Coupé车身。	READY
7399_sport_late	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-LATE-01	MEDIUM	生产区间覆盖后期Sport Coupé车身。	READY
7399_3p	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-3P-BERLINETTA-COUPE-01	MEDIUM	生产区间覆盖3P Berlinetta车身。	READY
7400_sport_early	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	MEDIUM	生产区间覆盖早期Sport Coupé车身。	READY
7400_sport_mid	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-MID-01	MEDIUM	生产区间覆盖中期Sport Coupé车身。	READY
7400_sport_late	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-LATE-01	MEDIUM	生产区间覆盖后期Sport Coupé车身。	READY
7400_3p	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-3P-BERLINETTA-COUPE-01	MEDIUM	生产区间覆盖3P Berlinetta车身。	READY
7401	7401	Coupe	Fiat 128 3P Berlinetta		3	EU-FIAT-128-3P-BERLINETTA-COUPE-01	HIGH		READY
7402_familiare	7402	Wagon	Fiat 128 Familiare		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7402_panorama	7402	Wagon	Fiat 128 Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7403_familiare	7403	Wagon	Fiat 128 Familiare		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7403_panorama	7403	Wagon	Fiat 128 Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7404_familiare_early	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-EARLY-01	MEDIUM	生产区间覆盖早期Familiare车身。	READY
7404_familiare_late	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7404_panorama	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7405	7405	Coupe	Hyundai Genesis Coupe	BK	2	EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	HIGH		READY
7406	7406	Sedan	Fiat 130	130B	4	EU-FIAT-130-SEDAN-4D-3200-01	HIGH		READY
7407	7407	Coupe	Fiat 130 Coupé	BC	2	EU-FIAT-130-COUPE-2D-3200-01	HIGH		READY
7408	7408	Wagon	Hyundai Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
7409	7409	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-PREFL-01	HIGH		READY
7410	7410	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	HIGH		READY
7411	7411	Wagon	Renault 12		5	EU-RENAULT-12-BREAK-WAGON-5D-01	HIGH		READY
7413	7413	Wagon	Dacia 1300		5	EU-DACIA-1300-UNIVERSAL-WAGON-5D-01	HIGH		READY
7414	7414	Wagon	Dacia 1310		5		LOW	候选为1310 Universal早期、中期与后期车身。	PENDING: 1983-2004生产区间跨多次车身改款，尚未闭合各外廓分支
7415	7415	Sedan	Mazda 626 IV	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH		READY
7416	7416	Wagon	Mazda 626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-4WD-01	HIGH		READY
7417	7417	Hatchback	Mazda 626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	MEDIUM	4WD五门车身关联至GE后期五门尺寸组。	READY
7419	7419	Sedan	Fiat 131 Series 2		4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH		READY
7421	7421	Sedan	Hyundai Equus II	VI	4	EU-HYUNDAI-EQUUS-VI-SEDAN-4D-01	HIGH		READY
7422	7422	Wagon	Fiat 131 Series 3		5	EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	HIGH		READY
7423	7423	Wagon	MINI Clubman	R55	5	EU-MINI-CLUBMAN-R55-FACELIFT-WAGON-5D-COOPER-S-01	HIGH		READY
7425	7425	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7426	7426	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7427	7427	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7428	7428	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	HIGH		READY
7429	7429	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	HIGH		READY
7430	7430	Sedan	Fiat 132 Series 1		4	EU-FIAT-132-S1-SEDAN-4D-01	HIGH		READY
7431_s2	7431	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7431_s3	7431	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	MEDIUM	生产区间覆盖Series 3车身。	READY
7432_s1	7432	Sedan	Fiat 132 Series 1		4	EU-FIAT-132-S1-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 1车身。	READY
7432_s2	7432	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7433_s2	7433	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7433_s3	7433	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	MEDIUM	生产区间覆盖Series 3车身。	READY
7434	7434	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	HIGH		READY
7435	7435	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-2000-01	HIGH		READY
7436_3dr	7436	SUV	Nissan Terrano I	WD21	3	EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7436_5dr	7436	SUV	Nissan Terrano I	WD21	5	EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7437_prefl	7437	Sedan	Toyota Carina II	A40	4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
7437_facelift	7437	Sedan	Toyota Carina II	A40	4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
7438	7438	Wagon	Toyota Carina III	A60	5		LOW	不能复用前驱T170旅行车尺寸组。	PENDING: 后驱A60旅行车的欧洲市场三维与不含镜宽度尚未闭合
7439	7439	Hatchback	Fiat Croma I		5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH		READY
7440	7440	Hatchback	Fiat Croma I		5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH		READY
7441	7441	Sedan	Fiat Regata	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH		READY
7442	7442	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7443	7443	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7444	7444	Wagon	Fiat Regata Weekend		5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH		READY
7445_3dr	7445	Hatchback	Lada Samara I	2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7445_5dr	7445	Hatchback	Lada Samara I	2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7446	7446	Sedan	Fiat Regata	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH		READY
7447	7447	Sedan	Lada Nova		4		LOW	不得直接复用2105尺寸组。	PENDING: 1600版本对应2105或2107车身边界及不含镜宽度尚未闭合
7448	7448	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7449	7449	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7450	7450	Coupe	MINI Coupé	R58	2	EU-MINI-COUPE-R58-COUPE-2D-JCW-01	HIGH		READY
7452_3dr	7452	Hatchback	Fiat Ritmo Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7452_5dr	7452	Hatchback	Fiat Ritmo Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7453	7453	Sedan	Moskvich 403		4	EU-MOSKVICH-403-SEDAN-4D-01	HIGH		READY
7454	7454	Sedan	Moskvich 403		4	EU-MOSKVICH-403-SEDAN-4D-01	HIGH		READY
7455_early	7455	Wagon	Moskvich 423N		5	EU-MOSKVICH-423N-WAGON-5D-EARLY-01	MEDIUM	生产区间覆盖早期车身。	READY
7455_late	7455	Wagon	Moskvich 423N		5	EU-MOSKVICH-423N-WAGON-5D-LATE-01	MEDIUM	生产区间覆盖后期车身。	READY
7456_swb	7456	Sedan	Mercedes-Benz S-Class W221	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	MEDIUM	Ktype未区分标准轴距与长轴距。	READY
7456_lwb	7456	Sedan	Mercedes-Benz S-Class W221	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	MEDIUM	Ktype未区分标准轴距与长轴距。	READY
7457_early	7457	Sedan	Moskvich 407		4	EU-MOSKVICH-407-SEDAN-4D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7457_late	7457	Sedan	Moskvich 407		4	EU-MOSKVICH-407-SEDAN-4D-LATE-01	MEDIUM	输入区间覆盖后期车身。	READY
7458	7458	Convertible	Fiat Ritmo Cabriolet	138A	2	EU-FIAT-RITMO-138A-CABRIOLET-01	HIGH		READY
7459	7459	SUV	Mercedes-Benz M-Class	W166	5	EU-MERCEDES-BENZ-M-KLASSE-W166-SUV-5D-ML500-01	HIGH		READY
7460	7460	Wagon	Moskvich 427		5		LOW	候选为早期427与后期427 IE车身。	PENDING: 1975年前后车身改动的分界及早期宽度口径尚未闭合
7461	7461	Sedan	Moskvich 412		4		LOW	不能仅按发动机版本选择单一尺寸组。	PENDING: 1971-1988区间跨AZLK与Izh后期车身，具体外廓分支尚未闭合
7462	7462	Sedan	Moskvich 2140		4	EU-MOSKVICH-2140-SEDAN-4D-01	HIGH		READY
7463	7463	Wagon	Moskvich 2137		5	EU-MOSKVICH-2137-WAGON-5D-01	HIGH		READY
7464	7464	Hatchback	Moskvich 2141		5	EU-MOSKVICH-2141-HATCHBACK-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-96-V4-SEDAN-2D-EARLY-01	4165	1580	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/38180/saab_96_v4_sedan.html
EU-SAAB-96-V4-SEDAN-2D-MID-01	4200	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/3017105/saab_96_v4_standard_sedan.html
EU-SAAB-96-V4-SEDAN-2D-LATE-01	4200	1590	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/3017600/saab_96_v4.html
EU-VOLVO-360-344-SEDAN-4D-01	4415	1660	1392	Volvo Cars Legacy;Automobile-Catalog	https://www.volvocars.com/sg/cars/legacy-models/360-sedan/;https://www.automobile-catalog.com/car/1984/49685/volvo_360_gle.html
EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	4300	1590	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/3017525/saab_96_l.html
EU-SAAB-95-V4-WAGON-3D-EARLY-01	4270	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/3016880/saab_95_station_wagon.html
EU-SAAB-95-V4-WAGON-3D-MID-01	4300	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/3017495/saab_95_v4.html
EU-SAAB-95-V4-WAGON-3D-LATE-01	4300	1590	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/3017570/saab_95_v4.html
EU-FIAT-124-RALLY-ABARTH-CONVERTIBLE-2D-01	3914	1630	1240	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710510/fiat_124_rally_abarth.html
EU-FIAT-124-FAMILIARE-WAGON-5D-EARLY-01	4030	1625	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/709775/fiat_124_familiare_station_wagon.html
EU-FIAT-124-FAMILIARE-WAGON-5D-MID-01	4045	1625	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1970/710075/fiat_124_familiare.html
EU-FIAT-124-FAMILIARE-WAGON-5D-LATE-01	4045	1610	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710240/fiat_124_familiare.html
EU-FIAT-124-COUPE-AC-2D-01	4115	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/2066675/fiat_124_sport_coupe_5-speed.html
EU-FIAT-124-COUPE-BC-2D-01	4125	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/709925/fiat_124_sport_coupe_1600.html
EU-FIAT-124-COUPE-CC-2D-01	4175	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/710450/fiat_124_sport_coupe_1800.html
EU-FIAT-124-BERLINA-SEDAN-4D-EARLY-01	4030	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709760/fiat_124.html
EU-FIAT-124-BERLINA-SEDAN-4D-MID-01	4042	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/710060/fiat_124.html
EU-FIAT-124-BERLINA-SEDAN-4D-LATE-01	4045	1610	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/710225/fiat_124.html
EU-FIAT-124-SPECIAL-SEDAN-4D-EARLY-01	4050	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709835/fiat_124_special.html
EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	4059	1610	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/710180/fiat_124_special_t.html
EU-FIAT-128-RALLY-S1-SEDAN-2D-01	3886	1590	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/24695/fiat_128_rally.html
EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	3808	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710825/fiat_128_coupe_1300_sl.html
EU-FIAT-128-SPORT-COUPE-2D-MID-01	3856	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/711020/fiat_128_coupe_sl_1300.html
EU-FIAT-128-SPORT-COUPE-2D-LATE-01	3924	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/711035/fiat_128_coupe_sl.html
EU-FIAT-128-S1-FAMILIARE-WAGON-3D-EARLY-01	3863	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710780/fiat_128_familiare.html
EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	3845	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/711200/fiat_128_familiare.html
EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	3860	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/711785/fiat_128_panorama_1100_cl.html
EU-FIAT-130-SEDAN-4D-3200-01	4750	1805	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/713810/fiat_130_3200_automatic.html
EU-FIAT-130-COUPE-2D-3200-01	4842	1760	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/27395/fiat_130_coupe.html
EU-RENAULT-12-BREAK-WAGON-5D-01	4404	1616	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2926625/renault_12_ln_break.html
EU-DACIA-1300-UNIVERSAL-WAGON-5D-01	4400	1636	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/38690/dacia_1300_universal.html
EU-MAZDA-626-III-GV-WAGON-5D-4WD-01	4610	1690	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1637090/mazda_626_2_2i_glx_4wd_kombi_cat.html
EU-HYUNDAI-EQUUS-VI-SEDAN-4D-01	5160	1900	1495	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1608500/hyundai_centennial_4_6.html
EU-MINI-CLUBMAN-R55-FACELIFT-WAGON-5D-COOPER-S-01	3961	1683	1432	BMW Group PressClub MINI Clubman R55 technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0081768ES/123481
EU-FIAT-132-S3-SEDAN-4D-1600-01	4425	1650	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/33845/fiat_132_1600.html
EU-FIAT-132-S2-SEDAN-4D-01	4405	1640	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/713615/fiat_132_gls_1600.html
EU-FIAT-132-S1-SEDAN-4D-01	4376	1640	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/713210/fiat_132_1600.html
EU-MINI-COUPE-R58-COUPE-2D-JCW-01	3758	1683	1384	MINI Coupé UK press kit	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0121814EN_GB/mini-coup%C3%A9-uk-press-kit?language=en_GB
EU-MOSKVICH-403-SEDAN-4D-01	4040	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/2046365/moskvich_403.html
EU-MOSKVICH-423N-WAGON-5D-EARLY-01	4055	1540	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/2046290/moskvich_423n.html
EU-MOSKVICH-423N-WAGON-5D-LATE-01	4040	1540	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/2046410/moskvich_423n.html
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1556315/mercedes-benz_s_63_amg_performance_package.html
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1556330/mercedes-benz_s_63_amg_lwb_performance_package.html
EU-MOSKVICH-407-SEDAN-4D-EARLY-01	4055	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1958/2046305/moskvich_407.html
EU-MOSKVICH-407-SEDAN-4D-LATE-01	4040	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/2046395/moskvich_407.html
EU-MERCEDES-BENZ-M-KLASSE-W166-SUV-5D-ML500-01	4804	1926	1796	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/1940690/mercedes-benz_ml_500_4matic_lang.html
EU-MOSKVICH-2140-SEDAN-4D-01	4250	1550	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/27290/moskwicz_2140.html
EU-MOSKVICH-2137-WAGON-5D-01	4210	1550	1525	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/39125/moskwicz_2137.html
EU-MOSKVICH-2141-HATCHBACK-5D-01	4350	1690	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/53405/moskwicz_2141_1_5.html
```

## 下一步优先处理

1. 优先确认 Ktype 7379–7382 的 Jumper I 230P 4X4 是否改变整车高度，并闭合 SWB/MWB、低顶/高顶分支。
2. 按物理外廓分阶段闭合 Dacia 1310 Universal、Toyota Carina A60 Wagon 和 Lada Nova 1600。
3. 最后处理 Moskvich 427 与 412 的生产分界、AZLK/Izh 归属和不含后视镜宽度口径。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/spain/article/attachment/T0081768ES/123481 "https://www.press.bmwgroup.com/spain/article/attachment/T0081768ES/123481"
[2]: https://www.automobile-catalog.com/car/2015/1940690/mercedes-benz_ml_500_4matic_lang.html?utm_source=chatgpt.com "2015 Mercedes-Benz ML 500 4MATIC Specs Review ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6901-7000_ktype_dimension_mapping_final.tsv
- all_6901-7000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: Playwright browser bridge 启动超时


--- 发送 / checkpoint 续跑到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6901-7000_ktype_dimension_mapping_final.tsv
- all_6901-7000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* 上一轮 9 条 `PENDING` 已全部闭合。
* 已完成固定表头、唯一性、引用闭合、尺寸及来源非空检查。
* 最终结果覆盖 100 个输入 Ktype，共 139 条映射、96 个尺寸组，无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：139
* PENDING 映射：0
* 已确认尺寸组：96
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 最终状态：完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7356_3dr_prefl	7356	Hatchback	Saab 900 I		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与改款前分支。	READY
7356_5dr_prefl	7356	Hatchback	Saab 900 I		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype未区分五门与改款前分支。	READY
7356_3dr_facelift	7356	Hatchback	Saab 900 I		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与改款后分支。	READY
7356_5dr_facelift	7356	Hatchback	Saab 900 I		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype未区分五门与改款后分支。	READY
7357_prefl	7357	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	HIGH	生产区间跨改款，保留改款前分支。	READY
7357_facelift	7357	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，保留改款后分支。	READY
7358	7358	Sedan	Saab 900 I		4	EU-SAAB-900-I-SEDAN-PRE83-01	HIGH		READY
7359_early	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7359_mid	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-MID-01	MEDIUM	输入区间覆盖中期车身。	READY
7359_late	7359	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-LATE-01	MEDIUM	输入区间覆盖后期窄保险杠车身。	READY
7360	7360	Sedan	Volvo 300 Series	344	4	EU-VOLVO-360-344-SEDAN-4D-01	HIGH		READY
7361	7361	Sedan	Volvo 760	704	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH		READY
7363	7363	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7364	7364	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7365	7365	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7366	7366	Coupe	Saab 900 II	YS3D	3	EU-SAAB-900-II-HATCHBACK-3D-01	HIGH	三门车型在部分资料中归为 hatchback/coupé。	READY
7367	7367	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	HIGH	后期大型保险杠车身。	READY
7368	7368	Sedan	Saab 96 V4		2	EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	HIGH	后期大型保险杠车身。	READY
7369_early	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7369_mid	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-MID-01	MEDIUM	输入区间覆盖中期车身。	READY
7369_late	7369	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	MEDIUM	输入区间覆盖后期车身。	READY
7370	7370	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	HIGH		READY
7371	7371	Wagon	Saab 95 V4		3	EU-SAAB-95-V4-WAGON-3D-LATE-01	HIGH		READY
7372	7372	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7373	7373	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7374	7374	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7375	7375	Sedan	Volvo S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7376	7376	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7377	7377	Wagon	Volvo V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7378	7378	Hatchback	Audi A3 8L	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
7379	7379	MPV	Citroën Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	乘用Bus短轴低顶车身。	READY
7380	7380	MPV	Citroën Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	乘用Bus短轴低顶车身。	READY
7381	7381	MPV	Citroën Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	乘用Bus短轴低顶车身。	READY
7382	7382	MPV	Citroën Jumper I	230P	4	EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	乘用Bus短轴低顶车身。	READY
7383	7383	Convertible	Fiat 124 Sport Spider		2	EU-FIAT-124-RALLY-ABARTH-CONVERTIBLE-2D-01	HIGH		READY
7384	7384	Convertible	Fiat 124 Sport Spider I		2	EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	HIGH		READY
7385_early	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-EARLY-01	MEDIUM	生产区间覆盖早期车身。	READY
7385_mid	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-MID-01	MEDIUM	生产区间覆盖中期车身。	READY
7385_late	7385	Wagon	Fiat 124 Familiare		5	EU-FIAT-124-FAMILIARE-WAGON-5D-LATE-01	MEDIUM	生产区间覆盖后期车身。	READY
7386_ac	7386	Coupe	Fiat 124 Sport Coupé	AC	2	EU-FIAT-124-COUPE-AC-2D-01	MEDIUM	生产区间覆盖AC车身。	READY
7386_bc	7386	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7387_bc	7387	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7387_cc	7387	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	MEDIUM	生产区间覆盖CC车身。	READY
7388_bc	7388	Coupe	Fiat 124 Sport Coupé	BC	2	EU-FIAT-124-COUPE-BC-2D-01	MEDIUM	生产区间覆盖BC车身。	READY
7388_cc	7388	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	MEDIUM	生产区间覆盖CC车身。	READY
7389	7389	Coupe	Fiat 124 Sport Coupé	CC	2	EU-FIAT-124-COUPE-CC-2D-01	HIGH		READY
7390_early	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-EARLY-01	MEDIUM	生产区间覆盖早期标准车身。	READY
7390_mid	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-MID-01	MEDIUM	生产区间覆盖中期标准车身。	READY
7390_late	7390	Sedan	Fiat 124 Berlina		4	EU-FIAT-124-BERLINA-SEDAN-4D-LATE-01	MEDIUM	生产区间覆盖后期标准车身。	READY
7391	7391	Sedan	Fiat 124 Special T		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7392	7392	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7393_early	7393	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-EARLY-01	MEDIUM	生产区间覆盖早期Special车身。	READY
7393_late	7393	Sedan	Fiat 124 Special		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	MEDIUM	生产区间覆盖后期Special车身。	READY
7395	7395	Sedan	Fiat 124 Special T		4	EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	HIGH		READY
7398	7398	Sedan	Fiat 128 Series 1		2	EU-FIAT-128-RALLY-S1-SEDAN-2D-01	HIGH		READY
7399_sport_early	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	MEDIUM	生产区间覆盖早期Sport Coupé车身。	READY
7399_sport_mid	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-MID-01	MEDIUM	生产区间覆盖中期Sport Coupé车身。	READY
7399_sport_late	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-LATE-01	MEDIUM	生产区间覆盖后期Sport Coupé车身。	READY
7399_3p	7399	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-3P-BERLINETTA-COUPE-01	MEDIUM	生产区间覆盖3P Berlinetta车身。	READY
7400_sport_early	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	MEDIUM	生产区间覆盖早期Sport Coupé车身。	READY
7400_sport_mid	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-MID-01	MEDIUM	生产区间覆盖中期Sport Coupé车身。	READY
7400_sport_late	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-SPORT-COUPE-2D-LATE-01	MEDIUM	生产区间覆盖后期Sport Coupé车身。	READY
7400_3p	7400	Coupe	Fiat 128 Coupé / 3P		2	EU-FIAT-128-3P-BERLINETTA-COUPE-01	MEDIUM	生产区间覆盖3P Berlinetta车身。	READY
7401	7401	Coupe	Fiat 128 3P Berlinetta		3	EU-FIAT-128-3P-BERLINETTA-COUPE-01	HIGH		READY
7402_familiare	7402	Wagon	Fiat 128 Familiare		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7402_panorama	7402	Wagon	Fiat 128 Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7403_familiare	7403	Wagon	Fiat 128 Familiare		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7403_panorama	7403	Wagon	Fiat 128 Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7404_familiare_early	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-EARLY-01	MEDIUM	生产区间覆盖早期Familiare车身。	READY
7404_familiare_late	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	MEDIUM	生产区间覆盖后期Familiare车身。	READY
7404_panorama	7404	Wagon	Fiat 128 Familiare / Panorama		3	EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	MEDIUM	生产区间覆盖Panorama车身。	READY
7405	7405	Coupe	Hyundai Genesis Coupe	BK	2	EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	HIGH		READY
7406	7406	Sedan	Fiat 130	130B	4	EU-FIAT-130-SEDAN-4D-3200-01	HIGH		READY
7407	7407	Coupe	Fiat 130 Coupé	BC	2	EU-FIAT-130-COUPE-2D-3200-01	HIGH		READY
7408	7408	Wagon	Hyundai Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
7409	7409	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-PREFL-01	HIGH		READY
7410	7410	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	HIGH		READY
7411	7411	Wagon	Renault 12		5	EU-RENAULT-12-BREAK-WAGON-5D-01	HIGH		READY
7413	7413	Wagon	Dacia 1300		5	EU-DACIA-1300-UNIVERSAL-WAGON-5D-01	HIGH		READY
7414_early	7414	Wagon	Dacia 1310		5	EU-DACIA-1310-BREAK-WAGON-5D-EARLY-01	MEDIUM	生产区间覆盖早期车身。	READY
7414_mid	7414	Wagon	Dacia 1310		5	EU-DACIA-1310-BREAK-WAGON-5D-MID-01	MEDIUM	生产区间覆盖中期车身。	READY
7414_late	7414	Wagon	Dacia 1310		5	EU-DACIA-1310-BREAK-WAGON-5D-LATE-01	MEDIUM	生产区间覆盖后期车身。	READY
7415	7415	Sedan	Mazda 626 IV	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH		READY
7416	7416	Wagon	Mazda 626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-4WD-01	HIGH		READY
7417	7417	Hatchback	Mazda 626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	MEDIUM	4WD五门车身关联至GE后期五门尺寸组。	READY
7419	7419	Sedan	Fiat 131 Series 2		4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH		READY
7421	7421	Sedan	Hyundai Equus II	VI	4	EU-HYUNDAI-EQUUS-VI-SEDAN-4D-01	HIGH		READY
7422	7422	Wagon	Fiat 131 Series 3		5	EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	HIGH		READY
7423	7423	Wagon	MINI Clubman	R55	5	EU-MINI-CLUBMAN-R55-FACELIFT-WAGON-5D-COOPER-S-01	HIGH		READY
7425	7425	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7426	7426	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7427	7427	Sedan	Fiat Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH		READY
7428	7428	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	HIGH		READY
7429	7429	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	HIGH		READY
7430	7430	Sedan	Fiat 132 Series 1		4	EU-FIAT-132-S1-SEDAN-4D-01	HIGH		READY
7431_s2	7431	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7431_s3	7431	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	MEDIUM	生产区间覆盖Series 3车身。	READY
7432_s1	7432	Sedan	Fiat 132 Series 1		4	EU-FIAT-132-S1-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 1车身。	READY
7432_s2	7432	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7433_s2	7433	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	MEDIUM	生产区间覆盖Series 2车身。	READY
7433_s3	7433	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-1600-01	MEDIUM	生产区间覆盖Series 3车身。	READY
7434	7434	Sedan	Fiat 132 Series 2		4	EU-FIAT-132-S2-SEDAN-4D-01	HIGH		READY
7435	7435	Sedan	Fiat 132 Series 3		4	EU-FIAT-132-S3-SEDAN-4D-2000-01	HIGH		READY
7436_3dr	7436	SUV	Nissan Terrano I	WD21	3	EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7436_5dr	7436	SUV	Nissan Terrano I	WD21	5	EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7437_prefl	7437	Sedan	Toyota Carina II	A40	4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
7437_facelift	7437	Sedan	Toyota Carina II	A40	4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
7438	7438	Wagon	Toyota Carina III	A60	5	EU-TOYOTA-CARINA-III-A60-WAGON-5D-01	HIGH		READY
7439	7439	Hatchback	Fiat Croma I		5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH		READY
7440	7440	Hatchback	Fiat Croma I		5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH		READY
7441	7441	Sedan	Fiat Regata	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH		READY
7442	7442	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7443	7443	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7444	7444	Wagon	Fiat Regata Weekend		5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH		READY
7445_3dr	7445	Hatchback	Lada Samara I	2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7445_5dr	7445	Hatchback	Lada Samara I	2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7446	7446	Sedan	Fiat Regata	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH		READY
7447	7447	Sedan	Lada Nova	2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	HIGH		READY
7448	7448	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7449	7449	Sedan	Lada Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
7450	7450	Coupe	MINI Coupé	R58	2	EU-MINI-COUPE-R58-COUPE-2D-JCW-01	HIGH		READY
7452_3dr	7452	Hatchback	Fiat Ritmo Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7452_5dr	7452	Hatchback	Fiat Ritmo Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	Ktype未区分三门与五门车身。	READY
7453	7453	Sedan	Moskvich 403		4	EU-MOSKVICH-403-SEDAN-4D-01	HIGH		READY
7454	7454	Sedan	Moskvich 403		4	EU-MOSKVICH-403-SEDAN-4D-01	HIGH		READY
7455_early	7455	Wagon	Moskvich 423N		5	EU-MOSKVICH-423N-WAGON-5D-EARLY-01	MEDIUM	生产区间覆盖早期车身。	READY
7455_late	7455	Wagon	Moskvich 423N		5	EU-MOSKVICH-423N-WAGON-5D-LATE-01	MEDIUM	生产区间覆盖后期车身。	READY
7456_swb	7456	Sedan	Mercedes-Benz S-Class W221	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	MEDIUM	Ktype未区分标准轴距与长轴距。	READY
7456_lwb	7456	Sedan	Mercedes-Benz S-Class W221	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	MEDIUM	Ktype未区分标准轴距与长轴距。	READY
7457_early	7457	Sedan	Moskvich 407		4	EU-MOSKVICH-407-SEDAN-4D-EARLY-01	MEDIUM	输入区间覆盖早期车身。	READY
7457_late	7457	Sedan	Moskvich 407		4	EU-MOSKVICH-407-SEDAN-4D-LATE-01	MEDIUM	输入区间覆盖后期车身。	READY
7458	7458	Convertible	Fiat Ritmo Cabriolet	138A	2	EU-FIAT-RITMO-138A-CABRIOLET-01	HIGH		READY
7459	7459	SUV	Mercedes-Benz M-Class	W166	5	EU-MERCEDES-BENZ-M-KLASSE-W166-SUV-5D-ML500-01	HIGH		READY
7460	7460	Wagon	Moskvich 427		5	EU-MOSKVICH-427-WAGON-5D-LATE-01	HIGH	1975年起后期车身。	READY
7461_pre82	7461	Sedan	Moskvich 412	412 IE	4	EU-MOSKVICH-412-SEDAN-4D-PRE82-01	MEDIUM	生产区间覆盖1982年前车身。	READY
7461_post82	7461	Sedan	Moskvich 412	028-412 IE	4	EU-MOSKVICH-412-028-SEDAN-4D-POST82-01	MEDIUM	生产区间覆盖1982年后Izh车身。	READY
7462	7462	Sedan	Moskvich 2140		4	EU-MOSKVICH-2140-SEDAN-4D-01	HIGH		READY
7463	7463	Wagon	Moskvich 2137		5	EU-MOSKVICH-2137-WAGON-5D-01	HIGH		READY
7464	7464	Hatchback	Moskvich 2141		5	EU-MOSKVICH-2141-HATCHBACK-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6901-7000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	4740	1690	1420	Automobile-Catalog Saab 900 I 3-door model data	https://www.automobile-catalog.com/make/saab/900_1gen/900_1_1_3d/1986.html
EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	4740	1690	1425	Automobile-Catalog Saab 900 I 5-door model data	https://www.automobile-catalog.com/make/saab/900_1gen/900_1gen/1986.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	4687	1690	1420	Automobile-Catalog 1988 Saab 900 i 3-door	https://www.automobile-catalog.com/car/1988/3024860/saab_900_i_3-door.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	4687	1690	1420	Automobile-Catalog 1988 Saab 900 i 5-door	https://www.automobile-catalog.com/car/1988/3024980/saab_900_i_5-door.html
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425	Automobile-Catalog 1984 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1984/3022820/saab_900_turbo_4-door.html
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420	Automobile-Catalog 1988 Saab 900 i 4-door	https://www.automobile-catalog.com/car/1988/3024920/saab_900_i_4-door.html
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420	Automobile-Catalog 1980 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1980/3020825/saab_900_turbo_4-door.html
EU-SAAB-96-V4-SEDAN-2D-EARLY-01	4165	1580	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/38180/saab_96_v4_sedan.html
EU-SAAB-96-V4-SEDAN-2D-MID-01	4200	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/3017105/saab_96_v4_standard_sedan.html
EU-SAAB-96-V4-SEDAN-2D-LATE-01	4200	1590	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/3017600/saab_96_v4.html
EU-VOLVO-360-344-SEDAN-4D-01	4415	1660	1392	Volvo Cars Legacy;Automobile-Catalog	https://www.volvocars.com/sg/cars/legacy-models/360-sedan/;https://www.automobile-catalog.com/car/1984/49685/volvo_360_gle.html
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410	Volvo 760 model data	https://de.wikipedia.org/wiki/Volvo_760
EU-SAAB-900-II-HATCHBACK-3D-01	4637	1711	1436	Auto-Data Saab 900 II Combi Coupe	https://www.auto-data.net/en/saab-900-ii-combi-coupe-generation-2546
EU-SAAB-96-V4-SEDAN-2D-IMPACTBUMPER-01	4300	1590	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/3017525/saab_96_l.html
EU-SAAB-95-V4-WAGON-3D-EARLY-01	4270	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/3016880/saab_95_station_wagon.html
EU-SAAB-95-V4-WAGON-3D-MID-01	4300	1580	1475	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/3017495/saab_95_v4.html
EU-SAAB-95-V4-WAGON-3D-LATE-01	4300	1590	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/3017570/saab_95_v4.html
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430	Auto-Data Volvo V70 I	https://www.auto-data.net/en/volvo-v70-i-generation-1934
EU-VOLVO-S70-I-SEDAN-4D-01	4720	1760	1400	Auto-Data Volvo S70	https://www.auto-data.net/en/volvo-s70-model-922
EU-AUDI-A3-8L-HATCHBACK-3D-01	4152	1735	1427	Auto-Data Audi A3 8L	https://www.auto-data.net/en/audi-a3-model-496
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Swiss FEDRO type approval via Motoro	https://motoro.ch/en/fiche-technique/citroen/jumper-2-5dt-4x4
EU-FIAT-124-RALLY-ABARTH-CONVERTIBLE-2D-01	3914	1630	1240	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710510/fiat_124_rally_abarth.html
EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	3971	1613	1250	Automobile-Catalog 1973 Fiat 124 Sport Spider 1600	https://www.automobile-catalog.com/car/1973/710435/fiat_124_sport_spider_1600_5-speed.html
EU-FIAT-124-FAMILIARE-WAGON-5D-EARLY-01	4030	1625	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/709775/fiat_124_familiare_station_wagon.html
EU-FIAT-124-FAMILIARE-WAGON-5D-MID-01	4045	1625	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1970/710075/fiat_124_familiare.html
EU-FIAT-124-FAMILIARE-WAGON-5D-LATE-01	4045	1610	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710240/fiat_124_familiare.html
EU-FIAT-124-COUPE-AC-2D-01	4115	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/2066675/fiat_124_sport_coupe_5-speed.html
EU-FIAT-124-COUPE-BC-2D-01	4125	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/709925/fiat_124_sport_coupe_1600.html
EU-FIAT-124-COUPE-CC-2D-01	4175	1670	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/710450/fiat_124_sport_coupe_1800.html
EU-FIAT-124-BERLINA-SEDAN-4D-EARLY-01	4030	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709760/fiat_124.html
EU-FIAT-124-BERLINA-SEDAN-4D-MID-01	4042	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/710060/fiat_124.html
EU-FIAT-124-BERLINA-SEDAN-4D-LATE-01	4045	1610	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/710225/fiat_124.html
EU-FIAT-124-SPECIAL-SEDAN-4D-LATE-01	4059	1610	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/710180/fiat_124_special_t.html
EU-FIAT-124-SPECIAL-SEDAN-4D-EARLY-01	4050	1625	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709835/fiat_124_special.html
EU-FIAT-128-RALLY-S1-SEDAN-2D-01	3886	1590	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/24695/fiat_128_rally.html
EU-FIAT-128-SPORT-COUPE-2D-EARLY-01	3808	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710825/fiat_128_coupe_1300_sl.html
EU-FIAT-128-SPORT-COUPE-2D-MID-01	3856	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/711020/fiat_128_coupe_sl_1300.html
EU-FIAT-128-SPORT-COUPE-2D-LATE-01	3924	1560	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/711035/fiat_128_coupe_sl.html
EU-FIAT-128-3P-BERLINETTA-COUPE-01	3826	1560	1310	Automobile-Catalog 1976 Fiat 128 3P Berlinetta	https://www.automobile-catalog.com/car/1976/26270/fiat_128_3p_berlinetta_1300.html
EU-FIAT-128-S1-FAMILIARE-WAGON-3D-LATE-01	3845	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/711200/fiat_128_familiare.html
EU-FIAT-128-S2-PANORAMA-WAGON-3D-01	3860	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/711785/fiat_128_panorama_1100_cl.html
EU-FIAT-128-S1-FAMILIARE-WAGON-3D-EARLY-01	3863	1590	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/710780/fiat_128_familiare.html
EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	4630	1864	1379	Auto-Data Hyundai Genesis Coupe	https://www.auto-data.net/en/hyundai-genesis-coupe-generation-2968
EU-FIAT-130-SEDAN-4D-3200-01	4750	1805	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/713810/fiat_130_3200_automatic.html
EU-FIAT-130-COUPE-2D-3200-01	4842	1760	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/27395/fiat_130_coupe.html
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457	Auto-Data Hyundai Elantra II Wagon 1.8 16V	https://www.auto-data.net/en/hyundai-elantra-ii-wagon-1.8-16v-128hp-13919
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435	Automobile-Catalog 1978 Renault 20 GTL	https://www.automobile-catalog.com/car/1978/32690/renault_20_gtl.html
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431	Automobile-Catalog 1976 Renault 30 TS	https://www.automobile-catalog.com/car/1976/32720/renault_30_ts.html
EU-RENAULT-12-BREAK-WAGON-5D-01	4404	1616	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2926625/renault_12_ln_break.html
EU-DACIA-1300-UNIVERSAL-WAGON-5D-01	4400	1636	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/38690/dacia_1300_universal.html
EU-DACIA-1310-BREAK-WAGON-5D-EARLY-01	4404	1636	1455	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/554150/dacia_1310_break.html
EU-DACIA-1310-BREAK-WAGON-5D-MID-01	4410	1615	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/554315/dacia_1310_break_1_6.html
EU-DACIA-1310-BREAK-WAGON-5D-LATE-01	4391	1660	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/554420/dacia_1310_break_1_6.html
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400	Automobile-Catalog 1992 Mazda 626 1.9i LX	https://www.automobile-catalog.com/car/1992/1651100/mazda_626_1_9i_lx.html
EU-MAZDA-626-III-GV-WAGON-5D-4WD-01	4610	1690	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1637090/mazda_626_2_2i_glx_4wd_kombi_cat.html
EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	4680	1750	1400	Automobile-Catalog Mazda 626 GE 4WD hatchback model data	https://www.automobile-catalog.com/car/1992/1651085/mazda_626_2_0i_glx_4wd_5-d.html
EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	4231	1651	1381	Automobile-Catalog 1979 Fiat 131 Supermirafiori 1600	https://www.automobile-catalog.com/car/1979/32870/fiat_131_supermirafiori_1600.html
EU-HYUNDAI-EQUUS-VI-SEDAN-4D-01	5160	1900	1495	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1608500/hyundai_centennial_4_6.html
EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	4264	1650	1400	Automobile-Catalog Fiat 131 Series 3 Panorama model data	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_iii_mirafiori_wagon/1983.html
EU-MINI-CLUBMAN-R55-FACELIFT-WAGON-5D-COOPER-S-01	3961	1683	1432	BMW Group PressClub MINI Clubman R55 technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0081768ES/123481
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420	Automobile-Catalog 1982 Fiat Argenta 2000 Iniezione	https://www.automobile-catalog.com/car/1982/716645/fiat_argenta_2000_iniezione.html
EU-FIAT-132-S3-SEDAN-4D-1600-01	4425	1650	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/33845/fiat_132_1600.html
EU-FIAT-132-S2-SEDAN-4D-01	4405	1640	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/713615/fiat_132_gls_1600.html
EU-FIAT-132-S1-SEDAN-4D-01	4376	1640	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/713210/fiat_132_1600.html
EU-FIAT-132-S3-SEDAN-4D-2000-01	4404	1641	1425	Automobile-Catalog Fiat 132 Series 3 model data	https://www.automobile-catalog.com/make/fiat/132/132_series_iii/1980.html
EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	4365	1690	1680	Auto-Data Nissan Terrano I WD21	https://www.auto-data.net/en/nissan-terrano-i-wd21-generation-190
EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	4365	1690	1680	Auto-Data Nissan Terrano I WD21	https://www.auto-data.net/en/nissan-terrano-i-wd21-generation-190
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	4230	1630	1390	Automobile-Catalog 1978 Toyota Carina 1.6	https://www.automobile-catalog.com/car/1978/35825/toyota_carina_1600.html
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	4360	1630	1395	Automobile-Catalog 1980 Toyota Carina 1.6	https://www.automobile-catalog.com/car/1980/37835/toyota_carina_1_6.html
EU-TOYOTA-CARINA-III-A60-WAGON-5D-01	4470	1650	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/3502430/toyota_carina_surf_1800_st_5speed.html
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433	Auto-Data Fiat Croma model data	https://www.auto-data.net/en/fiat-croma-model-745
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433	Auto-Data Fiat Croma model data	https://www.auto-data.net/en/fiat-croma-model-745
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410	Auto-Data Fiat Regata 138	https://www.auto-data.net/en/fiat-regata-138-generation-1604
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402	Auto-Data Lada 21099	https://www.auto-data.net/en/lada-21099-generation-2833
EU-FIAT-REGATA-WEEKEND-WAGON-01	4267	1650	1450	Auto-Data Fiat Regata Weekend	https://www.auto-data.net/en/fiat-regata-weekend-generation-1605
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402	Lada Samara model data	https://en.wikipedia.org/wiki/Lada_Samara
EU-LADA-SAMARA-I-HATCHBACK-5D-01	4006	1650	1402	Lada Samara model data	https://en.wikipedia.org/wiki/Lada_Samara
EU-LADA-NOVA-2105-SEDAN-4D-01	4130	1620	1446	Lada Riva / VAZ-2105 model data	https://en.wikipedia.org/wiki/Lada_Riva
EU-MINI-COUPE-R58-COUPE-2D-JCW-01	3758	1683	1384	MINI Coupé UK press kit	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0121814EN_GB/mini-coup%C3%A9-uk-press-kit?language=en_GB
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418	Fiat Ritmo model data	https://en.wikipedia.org/wiki/Fiat_Ritmo
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418	Fiat Ritmo model data	https://en.wikipedia.org/wiki/Fiat_Ritmo
EU-MOSKVICH-403-SEDAN-4D-01	4040	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/2046365/moskvich_403.html
EU-MOSKVICH-423N-WAGON-5D-EARLY-01	4055	1540	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/2046290/moskvich_423n.html
EU-MOSKVICH-423N-WAGON-5D-LATE-01	4040	1540	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/2046410/moskvich_423n.html
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1556315/mercedes-benz_s_63_amg_performance_package.html
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/1556330/mercedes-benz_s_63_amg_lwb_performance_package.html
EU-MOSKVICH-407-SEDAN-4D-EARLY-01	4055	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1958/2046305/moskvich_407.html
EU-MOSKVICH-407-SEDAN-4D-LATE-01	4040	1540	1560	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/2046395/moskvich_407.html
EU-FIAT-RITMO-138A-CABRIOLET-01	4014	1650	1400	Fiat Ritmo model data	https://en.wikipedia.org/wiki/Fiat_Ritmo
EU-MERCEDES-BENZ-M-KLASSE-W166-SUV-5D-ML500-01	4804	1926	1796	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/1940690/mercedes-benz_ml_500_4matic_lang.html
EU-MOSKVICH-427-WAGON-5D-LATE-01	4120	1550	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/2046695/moskvich_427_ie.html
EU-MOSKVICH-412-SEDAN-4D-PRE82-01	4090	1550	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/2046725/moskvich_412_ie.html
EU-MOSKVICH-412-028-SEDAN-4D-POST82-01	4120	1550	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1293860/izh_412_ie.html
EU-MOSKVICH-2140-SEDAN-4D-01	4250	1550	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/27290/moskwicz_2140.html
EU-MOSKVICH-2137-WAGON-5D-01	4210	1550	1525	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/39125/moskwicz_2137.html
EU-MOSKVICH-2141-HATCHBACK-5D-01	4350	1690	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/53405/moskwicz_2141_1_5.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6901-7000_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6901-7000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6901-7000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8799 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2745 行）

