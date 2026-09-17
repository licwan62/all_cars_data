# 任务：all 第 3501-3600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0036__1d94af8b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3501-3600 行

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
all 第 3501-3600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390
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

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Toyota	Hiace iv	2	Bus	Heckantrieb	Benzin	74	101	Aug 1989	Apr 1998	2024-03-01	3620
Toyota	Hiace iv	2.4 D	Bus	Heckantrieb	Diesel	55	75	Aug 1989	Aug 1995	2024-03-01	3621
Toyota	Hiace iv	2.4	Bus	Heckantrieb	Benzin	88	120	Aug 1989	Aug 2003	2024-03-01	3622
Lexus	Ls	400	Stufenheck	Heckantrieb	Benzin	180	245	Dec 1989	Dec 1995	2024-03-01	3623
Toyota	Previa i	2.4	Großraumlimousine	Heckantrieb	Benzin	97	132	May 1990	Aug 2000	2024-03-01	3624
Toyota	Carina e vi	1.6	Stufenheck	Frontantrieb	Benzin	79	107	Jan 1993	Sep 1997	2024-03-01	3625
Toyota	Carina e vi	1.6 GLI	Schrägheck	Frontantrieb	Benzin	79	107	Apr 1992	Sep 1997	2024-03-01	3627
Toyota	Carina e vi	2	Stufenheck	Frontantrieb	Benzin	98	133	Jan 1993	Sep 1997	2024-03-01	3628
Toyota	Carina e vi	2.0 GLI	Schrägheck	Frontantrieb	Benzin	98	133	Apr 1992	Sep 1997	2024-03-01	3630
Toyota	Carina e vi	2.0 GTI	Schrägheck	Frontantrieb	Benzin	116	158	Apr 1992	Feb 1994	2024-03-01	3631
Toyota	Carina e vi sportswagon	1.6 GLI	Kombi	Frontantrieb	Benzin	79	107	Jan 1993	Sep 1997	2024-03-01	3632
Toyota	Carina e vi sportswagon	2.0 GLI	Kombi	Frontantrieb	Benzin	98	133	Jan 1993	Sep 1997	2024-03-01	3633
Toyota	Corolla	1.3 XLI 16V	Stufenheck	Frontantrieb	Benzin	65	88	Jul 1992	Sep 1995	2024-03-01	3634
Toyota	Corolla	1.3 XLI 16V	Schrägheck	Frontantrieb	Benzin	65	88	Jul 1992	Sep 1995	2024-03-01	3635
Toyota	Corolla	1.3 XLI	Schrägheck	Frontantrieb	Benzin	65	88	Jul 1992	Apr 1997	2024-03-01	3636
Toyota	Corolla	1.6 SI	Schrägheck	Frontantrieb	Benzin	84	114	Jul 1992	Apr 1997	2024-03-01	3637
Toyota	Corolla	1.6 GLI	Schrägheck	Frontantrieb	Benzin	84	114	Jul 1992	Apr 1997	2024-03-01	3638
Toyota	Corolla	1.3 XLI 16V	Kombi	Frontantrieb	Benzin	65	88	Jul 1992	Sep 1995	2024-03-01	3639
Mazda	323 iii	1.5	Stufenheck	Frontantrieb	Benzin	54	73	Sep 1987	Oct 1989	2024-03-01	3640
Mazda	323 iii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	54	73	Sep 1987	Oct 1989	2024-03-01	3641
Mazda	323 iii	1.6 GT	Stufenheck	Frontantrieb	Benzin	63	85	Nov 1986	Oct 1989	2024-03-01	3642
Mazda	323 iii hatchback	1.6 GT	Schrägheck	Frontantrieb	Benzin	63	86	Sep 1987	Oct 1989	2024-03-01	3643
Mazda	323 iii hatchback	1.6 GT	Schrägheck	Frontantrieb	Benzin	77	105	Aug 1985	Aug 1993	2024-03-01	3644
Mazda	323 iii hatchback	1.7 D	Schrägheck	Frontantrieb	Diesel	40	54	Apr 1986	May 1989	2024-03-01	3645
Mazda	323 iii	1.7 D	Stufenheck	Frontantrieb	Diesel	40	54	Sep 1986	May 1989	2024-03-01	3646
Mazda	323 iii hatchback	1.7 D	Schrägheck	Frontantrieb	Diesel	42	57	Jan 1987	May 1989	2024-03-01	3647
Mazda	323 iii station wagon	1.5	Kombi	Frontantrieb	Benzin	55	75	May 1986	May 1989	2024-03-01	3648
Mazda	323 iii station wagon	1.5	Kombi	Frontantrieb	Benzin	54	73	Jan 1987	May 1989	2024-03-01	3649
Mazda	323 iii station wagon	1.6	Kombi	Frontantrieb	Benzin	63	86	Sep 1986	Oct 1995	2024-03-01	3650
Mazda	323 iii station wagon	1.7 D	Kombi	Frontantrieb	Diesel	40	54	Nov 1986	Aug 1987	2024-03-01	3651
Mazda	323 iii station wagon	1.7 D	Kombi	Frontantrieb	Diesel	42	57	Nov 1986	Oct 1989	2024-03-01	3652
Mazda	323 iii station wagon	1.7 D	Kombi	Frontantrieb	Diesel	41	56	Oct 1989	Mar 1993	2024-03-01	3653
Mazda	323 iii station wagon	1.6 4X4	Kombi	Allrad	Benzin	63	86	May 1990	Mar 1993	2024-03-01	3654
Mazda	626 i	1.6	Stufenheck	Heckantrieb	Benzin	55	75	May 1979	May 1982	2024-03-01	3655
Mazda	626 i	2	Stufenheck	Heckantrieb	Benzin	66	90	Mar 1979	May 1982	2024-03-01	3656
Mazda	626 ii	1.6	Stufenheck	Frontantrieb	Benzin	59	80	Nov 1982	Jun 1987	2024-03-01	3657
Mazda	626 ii hatchback	1.6	Schrägheck	Frontantrieb	Benzin	59	80	Mar 1983	Sep 1987	2024-03-01	3658
Mazda	626 ii	2	Stufenheck	Frontantrieb	Benzin	74	101	Mar 1983	Sep 1987	2024-03-01	3659
Mazda	626 ii hatchback	2	Schrägheck	Frontantrieb	Benzin	74	101	Mar 1983	Sep 1987	2024-03-01	3660
Mazda	626 ii	2	Stufenheck	Frontantrieb	Benzin	88	120	Jan 1986	Sep 1987	2024-03-01	3661
Mazda	626 ii hatchback	2	Schrägheck	Frontantrieb	Benzin	88	120	Jan 1986	Sep 1987	2024-03-01	3662
Mazda	626 ii	2.0 D	Stufenheck	Frontantrieb	Diesel	46	63	Jan 1983	Jun 1987	2024-03-01	3663
Mazda	626 ii hatchback	2.0 D	Schrägheck	Frontantrieb	Diesel	46	63	Mar 1984	Jun 1987	2024-03-01	3664
Mazda	626 iii	2	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1987	Oct 1990	2024-03-01	3665
Mazda	626 iii	2.2 12V	Stufenheck	Frontantrieb	Benzin	85	115	Nov 1987	Jul 1991	2024-03-01	3666
Mazda	626 iii	2.0 D	Stufenheck	Frontantrieb	Diesel	44	60	Jul 1987	Jul 1991	2024-03-01	3667
Mazda	626 iii hatchback	2	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1987	Oct 1990	2024-03-01	3668
Mazda	626 iii hatchback	2.0 16V	Schrägheck	Frontantrieb	Benzin	103	140	Nov 1987	Oct 1990	2024-03-01	3669
Mazda	626 iii hatchback	2.2 12V	Schrägheck	Frontantrieb	Benzin	85	115	Jun 1988	Apr 1992	2024-03-01	3670
Mazda	626 iii hatchback	2.0 D	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1987	Jul 1991	2024-03-01	3671
Mazda	626 iii	2	Coupe	Frontantrieb	Benzin	66	90	Sep 1987	Oct 1990	2024-03-01	3672
Mazda	626 iii	2.0 16V	Coupe	Frontantrieb	Benzin	103	140	Dec 1987	Oct 1990	2024-03-01	3673
Mazda	626 iii	2.2 12V	Coupe	Frontantrieb	Benzin	85	115	Apr 1988	Dec 1991	2024-03-01	3674
Mazda	626 iii station wagon	2	Kombi	Frontantrieb	Benzin	66	90	Oct 1988	Sep 1997	2024-03-01	3675
Mazda	626 iii station wagon	2.2 12V	Kombi	Frontantrieb	Benzin	85	115	Mar 1989	Nov 1996	2024-03-01	3676
Mazda	929 i	2	Stufenheck	Heckantrieb	Benzin	66	90	May 1979	Jul 1986	2024-03-01	3677
Mazda	929 ii	2	Stufenheck	Heckantrieb	Benzin	66	90	May 1982	Mar 1984	2024-03-01	3679
Mazda	929 ii	2	Stufenheck	Heckantrieb	Benzin	74	101	Mar 1984	Jul 1987	2024-03-01	3680
Mazda	929 ii	2	Coupe	Heckantrieb	Benzin	66	90	May 1982	Mar 1984	2024-03-01	3681
Mazda	929 ii	2	Coupe	Heckantrieb	Benzin	74	101	Mar 1984	Jul 1987	2024-03-01	3682
Mazda	929 ii	2.0 I Turbo	Coupe	Heckantrieb	Benzin	88	120	Oct 1984	Jul 1987	2024-03-01	3684
Mazda	929 ii	2	Kombi	Heckantrieb	Benzin	66	90	Jan 1983	Dec 1987	2024-03-01	3685
Mazda	929 iii	2.2 12V	Stufenheck	Heckantrieb	Benzin	85	115	Jan 1988	Apr 1989	2024-03-01	3686
Mazda	929 iii	2.2 I	Stufenheck	Heckantrieb	Benzin	100	136	May 1987	Dec 1988	2024-03-01	3687
Mazda	929 iii	3	Stufenheck	Heckantrieb	Benzin	125	170	Jan 1988	Dec 1989	2024-03-01	3688
Mazda	E	E2200 D	Kasten	Heckantrieb	Diesel	46	63	May 1985	Feb 1988	2024-03-01	3689
Mazda	E	E2000	Bus	Heckantrieb	Benzin	63	86	Nov 1984	May 1994	2024-03-01	3690
Mazda	E	E2200 D	Bus	Heckantrieb	Diesel	46	63	Jan 1984	Feb 1988	2024-03-01	3691
Ssangyong	Kyron	2.7 XDI 4X4	SUV	Allrad	Diesel	120	163	Mar 2006	Dec 2014	2024-03-01	3692
Mazda	Rx-7 i	1	Coupe	Heckantrieb	Benzin	77	105	May 1979	May 1981	2024-03-01	3694
Mazda	Rx-7 i	1.1	Coupe	Heckantrieb	Benzin	85	115	Jan 1981	Mar 1984	2024-03-01	3695
Mazda	323 s iv	1.3	Stufenheck	Frontantrieb	Benzin	49	67	Sep 1989	Jun 1991	2024-03-01	3696
Mazda	323 s iv	1.3 16V	Stufenheck	Frontantrieb	Benzin	54	73	Apr 1991	Jul 1994	2024-03-01	3697
Mazda	323 s iv	1.6	Stufenheck	Frontantrieb	Benzin	62	84	Sep 1989	Jun 1991	2024-03-01	3698
Mazda	323 s iv	1.6 16V	Stufenheck	Frontantrieb	Benzin	65	88	Aug 1989	Oct 1996	2024-03-01	3699
Mazda	323 s iv	1.8 16V	Stufenheck	Frontantrieb	Benzin	76	103	Aug 1989	Jul 1994	2024-03-01	3700
Mazda	323 c iv	1.3	Schrägheck	Frontantrieb	Benzin	49	67	Sep 1989	Jul 1994	2024-03-01	3701
Mazda	323 c iv	1.6	Schrägheck	Frontantrieb	Benzin	62	84	Sep 1989	Jun 1991	2024-03-01	3703
Mazda	323 c iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	65	88	Mar 1991	Oct 1994	2024-03-01	3704
Mazda	323 c iv	1.8 16V GT	Schrägheck	Frontantrieb	Benzin	94	128	Sep 1989	Mar 1993	2024-03-01	3705
Mazda	323 f iv	1.6	Schrägheck	Frontantrieb	Benzin	62	84	Sep 1989	Jun 1991	2024-03-01	3706
Mazda	323 f iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	65	88	Mar 1991	Oct 1994	2024-03-01	3707
Mazda	323 f iv	1.8 16V	Schrägheck	Frontantrieb	Benzin	76	103	Aug 1989	Jul 1994	2024-03-01	3708
Mazda	323 f iv	1.8 16V GT	Schrägheck	Frontantrieb	Benzin	94	128	Aug 1989	Jul 1994	2024-03-01	3709
Mazda	Rx-7 ii	1.3	Coupe	Heckantrieb	Benzin	110	150	Nov 1985	Apr 1989	2024-03-01	3710
Mazda	Rx-7 ii	1.3 Turbo	Coupe	Heckantrieb	Benzin	147	200	Mar 1989	Dec 1991	2024-03-01	3711
Mazda	Mx-5 i	1.6	Cabriolet	Heckantrieb	Benzin	85	115	May 1990	Jan 1994	2024-03-01	3712
Mazda	121 ii	1.3 16V	Stufenheck	Frontantrieb	Benzin	39	53	Nov 1990	Mar 1996	2024-03-01	3713
Mazda	121 ii	1.3 I 16V	Stufenheck	Frontantrieb	Benzin	53	72	Nov 1990	Mar 1996	2024-03-01	3714
Mazda	Mx-3	1.6	Coupe	Frontantrieb	Benzin	66	90	May 1991	Oct 1993	2024-03-01	3715
Mazda	Mx-3	1.8 I V6	Coupe	Frontantrieb	Benzin	98	133	Jan 1992	Jan 1994	2024-03-01	3716
Mazda	Mx-6	2	Coupe	Frontantrieb	Benzin	85	115	Feb 1992	Feb 1997	2024-03-01	3717
Mazda	Mx-6	2.5 24V	Coupe	Frontantrieb	Benzin	121	165	Feb 1992	Sep 1997	2024-03-01	3718
Mazda	626 iv	1.8 I	Stufenheck	Frontantrieb	Benzin	77	105	Aug 1991	Apr 1997	2024-03-01	3719
Mazda	626 iv	2.0 I	Stufenheck	Frontantrieb	Benzin	85	115	Jan 1992	Apr 1997	2024-03-01	3720
Mazda	626 iv hatchback	1.8	Schrägheck	Frontantrieb	Benzin	77	105	Aug 1991	Apr 1997	2024-03-01	3721
Mazda	626 iv hatchback	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	Aug 1991	Apr 1997	2024-03-01	3722
Mazda	626 iv hatchback	2.5 24V	Schrägheck	Frontantrieb	Benzin	121	165	Jan 1992	Apr 1997	2024-03-01	3723
Mazda	Xedos 6	2.0 V6	Stufenheck	Frontantrieb	Benzin	106	144	Jan 1992	May 1994	2024-03-01	3724
Mazda	Xedos 9	2.5 24V	Stufenheck	Frontantrieb	Benzin	123	167	Jul 1993	Jul 2000	2024-03-01	3725


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Toyota Carina E VI（T19）** 的 Sedan、Liftback、Wagon 三类物理外廓，同类发动机 Ktype 直接批量关联。三种车身尺寸均采用不含后视镜宽度。([汽车目录][1])
* 已区分 **Toyota Corolla VII（E100）** 的四门 Sedan、三门 Compact、五门 Liftback 和五门 Wagon，避免将输入中的多个“Schrägheck”错误合并为一个尺寸组。([jms-fahrzeugteile.de][2])
* 已将 Mazda 323 III BF 的三个 Sedan Ktype 关联到跨批次既有尺寸组，不重复输出该尺寸组。
* 已闭合 Mazda 323 III BW Station Wagon 前期、后期两套外廓；Ktype `3650` 的生产期横跨车长变化边界，因此拆分为 `prefl` 和 `facelift` 两行。([jms-fahrzeugteile.de][3])

## 当前批次进度

* 输入 Ktype：100 个
* READY 映射：24 行
* 已覆盖输入 Ktype：23 个
* PENDING/尚待处理输入 Ktype：77 个
* 当前已引用尺寸组：10 个

  * 本轮新建：9 个
  * 复用跨批次既有组：1 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3625	3625	Sedan	Carina E VI (T19)	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH	T19四门轿车外廓。	READY
3627	3627	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3628	3628	Sedan	Carina E VI (T19)	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH	T19四门轿车外廓。	READY
3630	3630	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3631	3631	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3632	3632	Wagon	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	HIGH	T19五门旅行车外廓。	READY
3633	3633	Wagon	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	HIGH	T19五门旅行车外廓。	READY
3634	3634	Sedan	Corolla VII (E100)	EE101	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	EE101四门轿车外廓。	READY
3635	3635	Hatchback	Corolla VII (E100)	EE101	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH	EE101三门Compact外廓。	READY
3636	3636	Hatchback	Corolla VII (E100)	EE101	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH	EE101五门Liftback外廓。	READY
3637	3637	Hatchback	Corolla VII (E100)	AE101	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH	AE101三门Compact外廓。	READY
3638	3638	Hatchback	Corolla VII (E100)	AE101	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH	AE101五门Liftback外廓。	READY
3639	3639	Wagon	Corolla VII (E100)	EE101	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	EE101五门旅行车外廓。	READY
3640	3640	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3642	3642	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3646	3646	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3648	3648	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3649	3649	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3650_prefl	3650	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	MEDIUM	Ktype生产期跨越BW前后期外廓，前期分支。	READY
3650_facelift	3650	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	MEDIUM	Ktype生产期跨越BW前后期外廓，后期分支。	READY
3651	3651	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3652	3652	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3653	3653	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	HIGH	BW后期五门旅行车外廓。	READY
3654	3654	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	MEDIUM	BW后期四驱五门旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410	Automobile-Catalog 1992 Toyota Carina E 4Door 1.6i	https://www.automobile-catalog.com/car/1992/3602465/toyota_carina_e_4door_1_6i.html
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410	Automobile-Catalog 1992 Toyota Carina E 5Door Liftback 2.0i	https://www.automobile-catalog.com/car/1992/3602540/toyota_carina_e_5door_liftback_2_0i.html
EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	4545	1695	1425	Automobile-Catalog 1993 Toyota Carina E Estate Wagon 2.0i	https://www.automobile-catalog.com/car/1993/3602645/toyota_carina_e_estate_wagon_2_0i.html
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380	Automobile-Catalog 1992 Toyota Corolla Sedan 1.6 GLi	https://www.automobile-catalog.com/car/1992/3583415/toyota_corolla_sedan_1_6_gli.html
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380	Automobile-Catalog 1993 Toyota Corolla Compact 1.3 XLi	https://www.automobile-catalog.com/car/1993/3583445/toyota_corolla_compact_1_3_xli.html
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375	Automobile-Catalog 1992 Toyota Corolla Liftback 1.3 XLi	https://www.automobile-catalog.com/car/1992/3583340/toyota_corolla_liftback_1_3_xli.html
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460	Auto-Data Toyota Corolla Wagon VII E100 1.3 i XLI 16V;Automobile-Catalog 1993 Toyota Corolla Wagon 1500 G-Touring	https://www.auto-data.net/en/toyota-corolla-wagon-vii-e100-1.3-i-xli-16v-88hp-3361;https://www.automobile-catalog.com/car/1993/3580505/toyota_corolla_wagon_1500_g-touring_automatic.html
EU-MAZDA-323-III-BW-WAGON-PREFL-01	4220	1645	1430	Automobile-Catalog 1986 Mazda 323 Station Wagon 1.5 GLX	https://www.automobile-catalog.com/car/1986/55835/mazda_323_station_wagon_1_5_glx.html
EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	4235	1645	1430	Automobile-Catalog 1993 Mazda 323 Station Wagon 1.6i GLX Catalyst	https://www.automobile-catalog.com/car/1993/1631675/mazda_323_station_wagon_1_6i_glx_cat.html
```

## 下一步优先处理

1. 核对 Toyota Hiace IV H100 的 SWB/LWB、车顶高度及 Bus 外廓分支。
2. 解决 Mazda 323 III BF Hatchback 各 Ktype 的三门、五门边界，并关联现有 3D/5D 尺寸组。
3. 闭合 Lexus LS 400、Toyota Previa I，以及 Mazda 626 I–IV 的 Sedan、Hatchback、Coupe、Wagon 聚类。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1992/3602465/toyota_carina_e_4door_1_6i.html?utm_source=chatgpt.com "1992 Toyota Carina E 4Door 1.6i Specs Review (84.5 kW / 115 PS / 113 hp) (since April 1992 for Europe )"
[2]: https://www.jms-fahrzeugteile.de/Bremsentechnik/EBC-Bremscheiben-Belaege/EBC-Standardbremsscheiben-fuer/Toyota/Corolla-6/VA-vorne-front/EBC-Premium-Disc-Bremsscheibe-passend-fuer-Toyota-Corolla-6-E10%3A%3A1203541.html?utm_source=chatgpt.com "EBC Premium Disc Bremsscheibe passend für Toyota Corolla 6 E10"
[3]: https://www.jms-fahrzeugteile.de/Bremsentechnik/EBC-Bremscheiben-Belaege/EBC-Standardbremsscheiben-fuer/Mazda/323-3/VA-vorne-front/EBC-Premium-Disc-Bremsscheibe-passend-fuer-Mazda-323-3-BF%3A%3A1184755.html?utm_source=chatgpt.com "EBC Premium Disc Bremsscheibe passend für Mazda 323 (3) BF"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Lexus LS 400 第一代欧洲版单一四门外廓，输入功率与欧洲 UCF10 规格一致。([汽车目录][1])
* 已闭合 Toyota Previa I 后驱 MPV 外廓，采用 Toyota 官方第一代 4750 × 1800 × 1780 mm 规格。([Toyota UK Magazine][2])
* 已创建 Mazda 323 III BF 改款后的 3 门、5 门尺寸组；改款后车长为 4000 mm，宽度明确为不含后视镜。Ktype `3644` 同时覆盖改款前后，拆为两个物理分支；改款前分支直接复用既有 3 门尺寸组。([汽车目录][3])

## 当前批次进度

* READY 映射：32 行
* 已覆盖输入 Ktype：28 个
* PENDING／尚待处理输入 Ktype：72 个
* 当前批次已引用尺寸组：15 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3623	3623	Sedan	LS I (XF10)	UCF10	4	EU-LEXUS-LS-I-XF10-SEDAN-4D-01	HIGH	UCF10欧洲版四门轿车外廓。	READY
3624	3624	MPV	Previa I (XR10/XR20)		4	EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	HIGH	第一代后驱欧洲版MPV外廓。	READY
3641_3dr	3641	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门外廓。	READY
3641_5dr	3641	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门外廓。	READY
3644_prefl	3644	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	Ktype生产区间跨越BF改款边界，改款前三门分支。	READY
3644_facelift	3644	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	MEDIUM	Ktype生产区间跨越BF改款边界，改款后三门分支。	READY
3647_3dr	3647	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门柴油外廓。	READY
3647_5dr	3647	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门柴油外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LEXUS-LS-I-XF10-SEDAN-4D-01	5005	1820	1425	Automobile-Catalog 1990 Lexus LS 400 Europe	https://www.automobile-catalog.com/car/1990/1423475/lexus_ls_400.html
EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	4750	1800	1780	Toyota UK Previa history	https://mag.toyota.co.uk/history-of-the-toyota-previa/
EU-MAZDA-323-III-BF-HATCHBACK-3D-02	4000	1645	1390	Automobile-Catalog 1989 Mazda 323 1.6i GT 3-Door	https://www.automobile-catalog.com/car/1989/1631300/mazda_323_1_6i.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-02	4000	1645	1390	Automobile-Catalog 1989 Mazda 323 1.5 GLX 5-Door	https://www.automobile-catalog.com/car/1989/1631270/mazda_323_1_5_glx.html
```

## 下一步优先处理

1. 闭合剩余 Mazda 323 III BF Hatchback Ktype `3643`、`3645` 的门数及改款边界。
2. 批量处理 Mazda 626 II GC Sedan 与 Hatchback，并区分确有外廓变化的前后期配置。
3. 随后处理 Mazda 626 III GD 的 Sedan、Hatchback、Coupe 和 Wagon 四个车身簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/1423475/lexus_ls_400.html?utm_source=chatgpt.com "1990 Lexus LS 400 Specs Review (180 kW / 245 PS / 241 hp) (since early-year 1990 for Europe )"
[2]: https://mag.toyota.co.uk/history-of-the-toyota-previa/?utm_source=chatgpt.com "Toyota Previa history - revolutionary people carrier"
[3]: https://www.automobile-catalog.com/car/1987/51620/mazda_323_1_6i_gtx.html?utm_source=chatgpt.com "1987 Mazda 323 1.6i GTX (man. 5) (model up to mid-year ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 补齐 Mazda 323 III BF 剩余 Hatchback Ktype：`3643` 按三门、五门拆分；`3645` 按三门/五门及改款前后拆分，全部复用既有 BF Hatchback 尺寸组，不重复建组。([汽车目录][1])
* 闭合 Mazda 626 II GC 的 Sedan 与 Hatchback 簇。因实际车高存在 1395/1410 mm 和 1350/1365 mm 两组外廓，分别建立独立尺寸组。([汽车目录][2])
* 闭合 Mazda 626 III GD/GV 的 Sedan、Hatchback、Coupe、Wagon 四个车身簇，批量关联 12 个 Ktype。([汽车目录][3])

## 2. 当前批次进度

* READY 映射：58 行
* 已覆盖输入 Ktype：50 个
* PENDING／尚待处理输入 Ktype：50 个
* 当前已引用尺寸组：23 个
* 本轮首次创建尺寸组：8 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3643_3dr	3643	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门外廓。	READY
3643_5dr	3643	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门外廓。	READY
3645_3dr_prefl	3645	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门改款前外廓。	READY
3645_3dr_facelift	3645	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	MEDIUM	Ktype覆盖三门改款后外廓。	READY
3645_5dr_prefl	3645	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门改款前外廓。	READY
3645_5dr_facelift	3645	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	MEDIUM	Ktype覆盖五门改款后外廓。	READY
3657	3657	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-01	HIGH	GC四门轿车外廓。	READY
3658	3658	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-01	HIGH	GC五门1.6掀背外廓。	READY
3659	3659	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-02	HIGH	GC四门2.0外廓。	READY
3660	3660	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	HIGH	GC五门2.0掀背外廓。	READY
3661	3661	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-02	HIGH	GC四门2.0 GT外廓。	READY
3662	3662	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	HIGH	GC五门2.0 GT掀背外廓。	READY
3663	3663	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-01	HIGH	GC四门柴油外廓。	READY
3664	3664	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	MEDIUM	GC五门柴油掀背外廓。	READY
3665	3665	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门轿车外廓。	READY
3666	3666	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门轿车外廓。	READY
3667	3667	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门柴油轿车外廓。	READY
3668	3668	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3669	3669	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门16V掀背外廓。	READY
3670	3670	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3671	3671	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门柴油掀背外廓。	READY
3672	3672	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe外廓。	READY
3673	3673	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门16V Coupe外廓。	READY
3674	3674	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe外廓。	READY
3675	3675	Wagon	626 III (GV)	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行车外廓。	READY
3676	3676	Wagon	626 III (GV)	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395	Automobile-Catalog 1983 Mazda 626 1.6 LX	https://www.automobile-catalog.com/car/1983/1626035/mazda_626_1_6_lx.html
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350	Automobile-Catalog 1983 Mazda 626 1.6 LX 5-Door	https://www.automobile-catalog.com/car/1983/1626080/mazda_626_1_6_lx_5-door.html
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410	Automobile-Catalog 1983 Mazda 626 2.0 GLX	https://www.automobile-catalog.com/car/1983/1626350/mazda_626_2_0_glx.html
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365	Automobile-Catalog 1983 Mazda 626 2.0 GLX 5-Door	https://www.automobile-catalog.com/car/1983/1626110/mazda_626_2_0_glx_5-door.html
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410	Automobile-Catalog 1988 Mazda 626 2.0 LX Catalyst	https://www.automobile-catalog.com/car/1988/1633955/mazda_626_2_0_lx_cat.html
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375	Automobile-Catalog 1988 Mazda 626 2.0i GLX 5-Door Automatic Catalyst	https://www.automobile-catalog.com/car/1988/1634030/mazda_626_2_0i_glx_5-d_automatic_cat.html
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360	Automobile-Catalog 1988 Mazda 626 2.0i 16V GT Coupe	https://www.automobile-catalog.com/car/1988/1633940/mazda_626_2_0i_16v_gt_coupe.html
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430	Automobile-Catalog 1988 Mazda 626 2.0 12V GLX Estate	https://www.automobile-catalog.com/car/1988/1634480/mazda_626_2_0_12v_glx_estate.html
```

## 5. 下一步优先处理

1. Mazda 626 I CB、929 I/II/III 的 Sedan、Coupe、Wagon 车身簇。
2. Mazda 323 IV BG 的 S、C、F 三种独立车身外廓。
3. Mazda RX-7 I/II、MX-5 I、MX-3、MX-6 等 Coupe/Convertible 簇。
4. Toyota Hiace IV H100 的轴距和车顶分支，以及 Mazda E 系列 Van/Bus 外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/1631315/mazda_323_1_6i_cat.html?utm_source=chatgpt.com "1988 Mazda 323 1.6i catalyst (man. 5) (LX, GLX)."
[2]: https://www.automobile-catalog.com/car/1983/1626035/mazda_626_1_6_lx.html?utm_source=chatgpt.com "1983 Mazda 626 1.6 LX Specs Review (59 kW / 80 PS / 79 hp) (since early-year 1983 for Europe Germany)"
[3]: https://www.automobile-catalog.com/car/1988/1633955/mazda_626_2_0_lx_cat.html?utm_source=chatgpt.com "1988 Mazda 626 2.0 LX catalyst Specs Review (66 kW / 90 ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合 Mazda 626 I（CB）四门 Sedan 外廓，两个发动机 Ktype 共用同一尺寸组。
* 闭合 Mazda 929 的 HB Sedan、HB Coupe、LA4 Wagon 和 HC Sedan 四个车身簇。929 HB Sedan、Coupe 与 LA4 Wagon 的三维分别为 4670×1690×1420、4640×1690×1355、4650×1715×1445 mm；HC Sedan 为 4885×1705×1425 mm，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Mazda 323 IV（BG）的 S Sedan、C 三门 Hatchback 和 F 五门 Hatchback 三类外廓。
* 323 C 的普通版本为 3995×1675×1380 mm；GT 外部套件版本长度增加至 4030 mm，因此 Ktype `3705` 使用独立尺寸组。323 F 为 4260×1675×1335 mm。([汽车目录][2])

## 2. 当前批次进度

* READY 映射：82 行
* 已覆盖输入 Ktype：74 个
* PENDING／尚待处理输入 Ktype：26 个
* 当前已引用尺寸组：32 个
* 本轮首次创建尺寸组：9 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3655	3655	Sedan	626 I (CB)	CB	4	EU-MAZDA-626-I-CB-SEDAN-4D-01	HIGH	CB四门轿车外廓。	READY
3656	3656	Sedan	626 I (CB)	CB	4	EU-MAZDA-626-I-CB-SEDAN-4D-01	HIGH	CB四门轿车外廓。	READY
3679	3679	Sedan	929 III (HB)	HB	4	EU-MAZDA-929-III-HB-SEDAN-4D-01	HIGH	HB四门轿车外廓。	READY
3680	3680	Sedan	929 III (HB)	HB	4	EU-MAZDA-929-III-HB-SEDAN-4D-01	HIGH	HB四门轿车外廓。	READY
3681	3681	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Hardtop Coupe外廓。	READY
3682	3682	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Hardtop Coupe外廓。	READY
3684	3684	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Turbo Coupe外廓。	READY
3685	3685	Wagon	929 II Wagon (LA4)	LA4	5	EU-MAZDA-929-II-LA4-WAGON-5D-01	HIGH	LA4五门旅行车外廓。	READY
3686	3686	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3687	3687	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3688	3688	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3696	3696	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3697	3697	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3698	3698	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3699	3699	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3700	3700	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3701	3701	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3703	3703	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3704	3704	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3705	3705	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-GT-3D-01	HIGH	BG C三门GT外部套件外廓。	READY
3706	3706	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3707	3707	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3708	3708	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3709	3709	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门GT Hatchback外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370	Automobile-Catalog 1979 Mazda 626 1.6 Europe	https://www.automobile-catalog.com/car/1979/35270/mazda_626_1600.html
EU-MAZDA-929-III-HB-SEDAN-4D-01	4670	1690	1420	Automobile-Catalog 1982 Mazda 929 Europe	https://www.automobile-catalog.com/car/1982/25775/mazda_929.html
EU-MAZDA-929-III-HB-COUPE-2D-01	4640	1690	1355	Automobile-Catalog 1982 Mazda 929 Hardtop Europe	https://www.automobile-catalog.com/car/1982/1628945/mazda_929_hardtop.html
EU-MAZDA-929-II-LA4-WAGON-5D-01	4650	1715	1445	Automobile-Catalog 1982 Mazda 929 Station Wagon Europe	https://www.automobile-catalog.com/car/1982/1628900/mazda_929_station_wagon.html
EU-MAZDA-929-IV-HC-SEDAN-4D-01	4885	1705	1425	Automobile-Catalog 1988 Mazda 929 2.2i GLX Europe	https://www.automobile-catalog.com/car/1988/60350/mazda_929_2_2i_glx.html
EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	4215	1675	1375	Automobile-Catalog 1990 Mazda 323 1.3 16V LX Sedan Europe	https://www.automobile-catalog.com/car/1990/1645625/mazda_323_1_3_16v_lx_sedan.html
EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	3995	1675	1380	Automobile-Catalog 1990 Mazda 323 1.3 16V LX Hatchback Europe	https://www.automobile-catalog.com/car/1990/1645610/mazda_323_1_3_16v_lx_hatchback.html
EU-MAZDA-323-IV-BG-C-HATCHBACK-GT-3D-01	4030	1675	1380	Automobile-Catalog 1990 Mazda 323 1.9i 16V GT Hatchback catalyst Europe	https://www.automobile-catalog.com/car/1990/64385/mazda_323_1_9i_16v_gt_hatchback_cat.html
EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	4260	1675	1335	Automobile-Catalog 1990 Mazda 323F 1.6 16V GLX Europe	https://www.automobile-catalog.com/car/1990/1645640/mazda_323f_1_6_16v_glx.html
```

## 5. 下一步优先处理

1. 闭合 Mazda RX-7 I/II、MX-5 I、MX-3 和 MX-6 的 Coupe／Convertible 簇。
2. 闭合 Mazda 121 II、626 IV、Xedos 6 和 Xedos 9。
3. 最后处理 Toyota Hiace IV、Mazda E Van/Bus、Mazda 929 I 与 SsangYong Kyron 等可能存在轴距、车顶或改款分支的车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1982/25775/mazda_929.html?utm_source=chatgpt.com "1982 Mazda 929 Specs Review (66 kW / 90 PS / 89 hp) (since April 1982 for Europe )"
[2]: https://www.automobile-catalog.com/car/1990/1645610/mazda_323_1_3_16v_lx_hatchback.html?utm_source=chatgpt.com "1990 Mazda 323 1.3 16V LX Hatchback Specs Review (54 kW / 73 PS / 72 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 已闭合 Mazda RX-7 I、RX-7 II 的改款前后物理外廓：第一代由 4285×1675×1260 mm 变为 4320×1670×1260 mm；第二代由 4310×1690×1270 mm 变为 4335×1690×1265 mm。([汽车目录][1])
* 已批量闭合 Mazda MX-5 I、121 II、MX-3、MX-6，发动机差异均直接复用同一物理尺寸组。([汽车目录][2])
* 已闭合 Mazda 626 IV 的 Sedan、Hatchback 两套外廓，以及 Xedos 6、Xedos 9 的 Sedan 外廓。([汽车目录][3])

## 2. 当前批次进度

* READY 映射：100 行
* 已覆盖输入 Ktype：92 个
* PENDING／尚待处理输入 Ktype：8 个
* 当前已引用尺寸组：44 个
* 本轮首次创建尺寸组：12 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3694	3694	Coupe	RX-7 I (SA/FB)	SA22C	3	EU-MAZDA-RX-7-I-SA22C-COUPE-PREFL-01	HIGH	第一代改款前三门Coupe外廓。	READY
3695	3695	Coupe	RX-7 I (SA/FB)	SA22C	3	EU-MAZDA-RX-7-I-SA22C-COUPE-FACELIFT-01	HIGH	第一代改款后三门Coupe外廓。	READY
3710	3710	Coupe	RX-7 II (FC)	FC	3	EU-MAZDA-RX-7-II-FC-COUPE-PREFL-01	HIGH	FC改款前三门Coupe外廓。	READY
3711	3711	Coupe	RX-7 II (FC)	FC	3	EU-MAZDA-RX-7-II-FC-COUPE-FACELIFT-01	HIGH	FC改款后三门Turbo Coupe外廓。	READY
3712	3712	Convertible	MX-5 I (NA)	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH	NA双门Roadster外廓。	READY
3713	3713	Sedan	121 II (DB)	DB	4	EU-MAZDA-121-II-DB-SEDAN-4D-01	HIGH	DB四门轿车外廓。	READY
3714	3714	Sedan	121 II (DB)	DB	4	EU-MAZDA-121-II-DB-SEDAN-4D-01	HIGH	DB四门轿车外廓。	READY
3715	3715	Coupe	MX-3 (EC)	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH	EC三门Hatchback Coupe外廓。	READY
3716	3716	Coupe	MX-3 (EC)	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH	EC三门V6 Hatchback Coupe外廓。	READY
3717	3717	Coupe	MX-6 II (GE)	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH	GE双门Coupe外廓。	READY
3718	3718	Coupe	MX-6 II (GE)	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH	GE双门V6 Coupe外廓。	READY
3719	3719	Sedan	626 IV (GE)	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH	GE四门轿车外廓。	READY
3720	3720	Sedan	626 IV (GE)	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH	GE四门轿车外廓。	READY
3721	3721	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门Hatchback外廓。	READY
3722	3722	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门Hatchback外廓。	READY
3723	3723	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门V6 Hatchback外廓。	READY
3724	3724	Sedan	Xedos 6 (CA)	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH	CA四门轿车外廓。	READY
3725	3725	Sedan	Xedos 9 (TA)	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH	TA四门轿车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-RX-7-I-SA22C-COUPE-PREFL-01	4285	1675	1260	Automobile-Catalog 1979 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1979/37265/mazda_rx-7.html
EU-MAZDA-RX-7-I-SA22C-COUPE-FACELIFT-01	4320	1670	1260	Automobile-Catalog 1981 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1981/26795/mazda_rx-7.html
EU-MAZDA-RX-7-II-FC-COUPE-PREFL-01	4310	1690	1270	Automobile-Catalog 1986 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1986/54140/mazda_rx-7.html
EU-MAZDA-RX-7-II-FC-COUPE-FACELIFT-01	4335	1690	1265	Automobile-Catalog 1990 Mazda RX-7 Turbo II Europe	https://www.automobile-catalog.com/car/1990/1639205/mazda_rx-7_turbo_ii.html
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230	Automobile-Catalog 1990 Mazda MX-5 Europe	https://www.automobile-catalog.com/car/1990/1640945/mazda_mx-5.html
EU-MAZDA-121-II-DB-SEDAN-4D-01	3800	1655	1470	Automobile-Catalog 1991 Mazda 121 1.3 GLX Europe	https://www.automobile-catalog.com/car/1991/1647830/mazda_121_1_3_glx.html
EU-MAZDA-MX-3-EC-COUPE-3D-01	4220	1695	1310	Automobile-Catalog 1992 Mazda MX-3 16V Europe	https://www.automobile-catalog.com/car/1992/1648550/mazda_mx-3_16v.html
EU-MAZDA-MX-6-II-GE-COUPE-2D-01	4615	1750	1310	Automobile-Catalog 1992 Mazda MX-6 2.0i 16V Europe	https://www.automobile-catalog.com/car/1992/1655285/mazda_mx-6_2_0i_16v.html
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400	Automobile-Catalog 1992 Mazda 626 1.9i LX Sedan Europe	https://www.automobile-catalog.com/car/1992/1651100/mazda_626_1_9i_lx.html
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390	Automobile-Catalog 1992 Mazda 626 1.9i LX 5-door Europe	https://www.automobile-catalog.com/car/1992/1650995/mazda_626_1_9i_lx_5-d.html
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355	Auto-Data Mazda Xedos 6 CA	https://www.auto-data.net/en/mazda-xedos-6-model-1210
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395	Automobile-Catalog 1993 Mazda Xedos 9 2.5i V6 4WS Europe	https://www.automobile-catalog.com/car/1993/1653365/mazda_xedos_9_2_5i_v6_4ws.html
```

## 5. 下一步优先处理

1. Toyota Hiace IV H100：确认 Bus 在各发动机 Ktype 下覆盖的标准轴距、长轴距及车顶分支。
2. Mazda E 系：确认 E2200 Kasten、E2000 Bus、E2200 Bus 的短车身/长车身边界。
3. Mazda 929 I：闭合早期 LA 系四门 Sedan 外廓。
4. SsangYong Kyron：核对改款前后长度和标准车高口径。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/37265/mazda_rx-7.html?utm_source=chatgpt.com "1979 Mazda RX-7 Specs Review (77 kW / 105 PS / 103 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1990/1640945/mazda_mx-5.html?utm_source=chatgpt.com "1990 Mazda MX-5 Specs Review (84.5 kW / 115 PS / 113 hp) (since mid-year 1990 for Europe )"
[3]: https://www.automobile-catalog.com/car/1992/1651100/mazda_626_1_9i_lx.html?utm_source=chatgpt.com "1992 Mazda 626 1.9i LX Specs Review (77 kW / 105 PS / 103 hp) (since January 1992 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 已闭合剩余 8 个 Ktype：Toyota Hiace IV H100、Mazda 929 I LA4、Mazda E-Series SR1/SR2 及 SsangYong Kyron I；其中 929 I 按改款前后拆分为两套外廓。([丰田汽车官网][1])
* 已补齐跨批次复用的 Mazda 323 III BF 三个尺寸组来源，未改写已有三维。([汽车目录][2])
* 已完成固定表头、唯一主键、映射引用闭合、正整数三维、来源非空和下载文件检查。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 映射：109 行
* PENDING 映射：0
* DIMENSION_GROUP：51 个
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 当前批次已完成。

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3620	3620	MPV	Hiace IV (H100)	RZH100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100标准轴距四门Bus外廓。	READY
3621	3621	MPV	Hiace IV (H100)	LH100	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100标准轴距四门柴油Bus外廓。	READY
3622	3622	MPV	Hiace IV (H100)	RZH101	4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	H100标准轴距四门Bus外廓。	READY
3623	3623	Sedan	LS I (XF10)	UCF10	4	EU-LEXUS-LS-I-XF10-SEDAN-4D-01	HIGH	UCF10欧洲版四门轿车外廓。	READY
3624	3624	MPV	Previa I (XR10/XR20)		4	EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	HIGH	第一代后驱欧洲版MPV外廓。	READY
3625	3625	Sedan	Carina E VI (T19)	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH	T19四门轿车外廓。	READY
3627	3627	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3628	3628	Sedan	Carina E VI (T19)	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH	T19四门轿车外廓。	READY
3630	3630	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3631	3631	Hatchback	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	T19五门Liftback外廓。	READY
3632	3632	Wagon	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	HIGH	T19五门旅行车外廓。	READY
3633	3633	Wagon	Carina E VI (T19)	T19	5	EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	HIGH	T19五门旅行车外廓。	READY
3634	3634	Sedan	Corolla VII (E100)	EE101	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	EE101四门轿车外廓。	READY
3635	3635	Hatchback	Corolla VII (E100)	EE101	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH	EE101三门Compact外廓。	READY
3636	3636	Hatchback	Corolla VII (E100)	EE101	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH	EE101五门Liftback外廓。	READY
3637	3637	Hatchback	Corolla VII (E100)	AE101	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH	AE101三门Compact外廓。	READY
3638	3638	Hatchback	Corolla VII (E100)	AE101	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH	AE101五门Liftback外廓。	READY
3639	3639	Wagon	Corolla VII (E100)	EE101	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	EE101五门旅行车外廓。	READY
3640	3640	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3641_3dr	3641	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门外廓。	READY
3641_5dr	3641	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门外廓。	READY
3642	3642	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3643_3dr	3643	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门外廓。	READY
3643_5dr	3643	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门外廓。	READY
3644_prefl	3644	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	Ktype生产区间跨越BF改款边界，改款前三门分支。	READY
3644_facelift	3644	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	MEDIUM	Ktype生产区间跨越BF改款边界，改款后三门分支。	READY
3645_3dr_prefl	3645	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门改款前外廓。	READY
3645_3dr_facelift	3645	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	MEDIUM	Ktype覆盖三门改款后外廓。	READY
3645_5dr_prefl	3645	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门改款前外廓。	READY
3645_5dr_facelift	3645	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	MEDIUM	Ktype覆盖五门改款后外廓。	READY
3646	3646	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
3647_3dr	3647	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-02	HIGH	BF改款后三门柴油外廓。	READY
3647_5dr	3647	Hatchback	323 III (BF)	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-02	HIGH	BF改款后五门柴油外廓。	READY
3648	3648	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3649	3649	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3650_prefl	3650	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	MEDIUM	Ktype生产期跨越BW前后期外廓，前期分支。	READY
3650_facelift	3650	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	MEDIUM	Ktype生产期跨越BW前后期外廓，后期分支。	READY
3651	3651	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3652	3652	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-PREFL-01	HIGH	BW前期五门旅行车外廓。	READY
3653	3653	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	HIGH	BW后期五门旅行车外廓。	READY
3654	3654	Wagon	323 III (BW)	BW	5	EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	MEDIUM	BW后期四驱五门旅行车外廓。	READY
3655	3655	Sedan	626 I (CB)	CB	4	EU-MAZDA-626-I-CB-SEDAN-4D-01	HIGH	CB四门轿车外廓。	READY
3656	3656	Sedan	626 I (CB)	CB	4	EU-MAZDA-626-I-CB-SEDAN-4D-01	HIGH	CB四门轿车外廓。	READY
3657	3657	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-01	HIGH	GC四门轿车外廓。	READY
3658	3658	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-01	HIGH	GC五门1.6掀背外廓。	READY
3659	3659	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-02	HIGH	GC四门2.0外廓。	READY
3660	3660	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	HIGH	GC五门2.0掀背外廓。	READY
3661	3661	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-02	HIGH	GC四门2.0 GT外廓。	READY
3662	3662	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	HIGH	GC五门2.0 GT掀背外廓。	READY
3663	3663	Sedan	626 II (GC)	GC	4	EU-MAZDA-626-II-GC-SEDAN-4D-01	HIGH	GC四门柴油外廓。	READY
3664	3664	Hatchback	626 II (GC)	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-02	MEDIUM	GC五门柴油掀背外廓。	READY
3665	3665	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门轿车外廓。	READY
3666	3666	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门轿车外廓。	READY
3667	3667	Sedan	626 III (GD)	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-01	HIGH	GD四门柴油轿车外廓。	READY
3668	3668	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3669	3669	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门16V掀背外廓。	READY
3670	3670	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3671	3671	Hatchback	626 III (GD)	GD	5	EU-MAZDA-626-III-GD-HATCHBACK-5D-01	HIGH	GD五门柴油掀背外廓。	READY
3672	3672	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe外廓。	READY
3673	3673	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门16V Coupe外廓。	READY
3674	3674	Coupe	626 III (GD)	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe外廓。	READY
3675	3675	Wagon	626 III (GV)	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行车外廓。	READY
3676	3676	Wagon	626 III (GV)	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行车外廓。	READY
3677_prefl	3677	Sedan	929 I (LA4)	LA4	4	EU-MAZDA-929-I-LA4-SEDAN-4D-PREFL-01	MEDIUM	Ktype生产区间覆盖LA4改款前四门外廓。	READY
3677_facelift	3677	Sedan	929 I (LA4)	LA4	4	EU-MAZDA-929-I-LA4-SEDAN-4D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖LA4改款后四门外廓。	READY
3679	3679	Sedan	929 III (HB)	HB	4	EU-MAZDA-929-III-HB-SEDAN-4D-01	HIGH	HB四门轿车外廓。	READY
3680	3680	Sedan	929 III (HB)	HB	4	EU-MAZDA-929-III-HB-SEDAN-4D-01	HIGH	HB四门轿车外廓。	READY
3681	3681	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Hardtop Coupe外廓。	READY
3682	3682	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Hardtop Coupe外廓。	READY
3684	3684	Coupe	929 III (HB)	HB	2	EU-MAZDA-929-III-HB-COUPE-2D-01	HIGH	HB双门Turbo Coupe外廓。	READY
3685	3685	Wagon	929 II Wagon (LA4)	LA4	5	EU-MAZDA-929-II-LA4-WAGON-5D-01	HIGH	LA4五门旅行车外廓。	READY
3686	3686	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3687	3687	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3688	3688	Sedan	929 IV (HC)	HC	4	EU-MAZDA-929-IV-HC-SEDAN-4D-01	HIGH	HC四门轿车外廓。	READY
3689	3689	Van	E-Series III (SR2)	SR2	5	EU-MAZDA-E-SERIES-III-SR2-VAN-01	MEDIUM	SR2五门厢式车外廓。	READY
3690	3690	MPV	E-Series III (SR1)	SR1	4	EU-MAZDA-E-SERIES-III-SR1-MPV-01	MEDIUM	SR1四门Bus外廓。	READY
3691	3691	MPV	E-Series III (SR1)	SR1	4	EU-MAZDA-E-SERIES-III-SR1-MPV-01	MEDIUM	SR1四门柴油Bus外廓。	READY
3692	3692	SUV	Kyron I		5	EU-SSANGYONG-KYRON-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
3694	3694	Coupe	RX-7 I (SA/FB)	SA22C	3	EU-MAZDA-RX-7-I-SA22C-COUPE-PREFL-01	HIGH	第一代改款前三门Coupe外廓。	READY
3695	3695	Coupe	RX-7 I (SA/FB)	SA22C	3	EU-MAZDA-RX-7-I-SA22C-COUPE-FACELIFT-01	HIGH	第一代改款后三门Coupe外廓。	READY
3696	3696	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3697	3697	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3698	3698	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3699	3699	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3700	3700	Sedan	323 IV (BG)	BG	4	EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	HIGH	BG S四门轿车外廓。	READY
3701	3701	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3703	3703	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3704	3704	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	HIGH	BG C三门Hatchback外廓。	READY
3705	3705	Hatchback	323 IV (BG)	BG	3	EU-MAZDA-323-IV-BG-C-HATCHBACK-GT-3D-01	HIGH	BG C三门GT外部套件外廓。	READY
3706	3706	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3707	3707	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3708	3708	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门Hatchback外廓。	READY
3709	3709	Hatchback	323 IV (BG)	BG	5	EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	HIGH	BG F五门GT Hatchback外廓。	READY
3710	3710	Coupe	RX-7 II (FC)	FC	3	EU-MAZDA-RX-7-II-FC-COUPE-PREFL-01	HIGH	FC改款前三门Coupe外廓。	READY
3711	3711	Coupe	RX-7 II (FC)	FC	3	EU-MAZDA-RX-7-II-FC-COUPE-FACELIFT-01	HIGH	FC改款后三门Turbo Coupe外廓。	READY
3712	3712	Convertible	MX-5 I (NA)	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH	NA双门Roadster外廓。	READY
3713	3713	Sedan	121 II (DB)	DB	4	EU-MAZDA-121-II-DB-SEDAN-4D-01	HIGH	DB四门轿车外廓。	READY
3714	3714	Sedan	121 II (DB)	DB	4	EU-MAZDA-121-II-DB-SEDAN-4D-01	HIGH	DB四门轿车外廓。	READY
3715	3715	Coupe	MX-3 (EC)	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH	EC三门Hatchback Coupe外廓。	READY
3716	3716	Coupe	MX-3 (EC)	EC	3	EU-MAZDA-MX-3-EC-COUPE-3D-01	HIGH	EC三门V6 Hatchback Coupe外廓。	READY
3717	3717	Coupe	MX-6 II (GE)	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH	GE双门Coupe外廓。	READY
3718	3718	Coupe	MX-6 II (GE)	GE	2	EU-MAZDA-MX-6-II-GE-COUPE-2D-01	HIGH	GE双门V6 Coupe外廓。	READY
3719	3719	Sedan	626 IV (GE)	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH	GE四门轿车外廓。	READY
3720	3720	Sedan	626 IV (GE)	GE	4	EU-MAZDA-626-IV-GE-SEDAN-4D-01	HIGH	GE四门轿车外廓。	READY
3721	3721	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门Hatchback外廓。	READY
3722	3722	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门Hatchback外廓。	READY
3723	3723	Hatchback	626 IV (GE)	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH	GE五门V6 Hatchback外廓。	READY
3724	3724	Sedan	Xedos 6 (CA)	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH	CA四门轿车外廓。	READY
3725	3725	Sedan	Xedos 9 (TA)	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH	TA四门轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3501-3600_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980	Toyota 75 Years Vehicle Lineage – 1989 Hiace	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html
EU-LEXUS-LS-I-XF10-SEDAN-4D-01	5005	1820	1425	Automobile-Catalog 1990 Lexus LS 400 Europe	https://www.automobile-catalog.com/car/1990/1423475/lexus_ls_400.html
EU-TOYOTA-PREVIA-I-XR10-MPV-2WD-01	4750	1800	1780	Toyota UK Previa history	https://mag.toyota.co.uk/history-of-the-toyota-previa/
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410	Automobile-Catalog 1992 Toyota Carina E 4Door 1.6i	https://www.automobile-catalog.com/car/1992/3602465/toyota_carina_e_4door_1_6i.html
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410	Automobile-Catalog 1992 Toyota Carina E 5Door Liftback 2.0i	https://www.automobile-catalog.com/car/1992/3602540/toyota_carina_e_5door_liftback_2_0i.html
EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	4545	1695	1425	Automobile-Catalog 1993 Toyota Carina E Estate Wagon 2.0i	https://www.automobile-catalog.com/car/1993/3602645/toyota_carina_e_estate_wagon_2_0i.html
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380	Automobile-Catalog 1992 Toyota Corolla Sedan 1.6 GLi	https://www.automobile-catalog.com/car/1992/3583415/toyota_corolla_sedan_1_6_gli.html
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380	Automobile-Catalog 1993 Toyota Corolla Compact 1.3 XLi	https://www.automobile-catalog.com/car/1993/3583445/toyota_corolla_compact_1_3_xli.html
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375	Automobile-Catalog 1992 Toyota Corolla Liftback 1.3 XLi	https://www.automobile-catalog.com/car/1992/3583340/toyota_corolla_liftback_1_3_xli.html
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460	Auto-Data Toyota Corolla Wagon VII E100 1.3 i XLI 16V;Automobile-Catalog 1993 Toyota Corolla Wagon 1500 G-Touring	https://www.auto-data.net/en/toyota-corolla-wagon-vii-e100-1.3-i-xli-16v-88hp-3361;https://www.automobile-catalog.com/car/1993/3580505/toyota_corolla_wagon_1500_g-touring_automatic.html
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390	Automobile-Catalog 1987 Mazda 323 1.5 GLX Sedan	https://www.automobile-catalog.com/car/1987/1630220/mazda_323_1_5_glx_sedan.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-02	4000	1645	1390	Automobile-Catalog 1989 Mazda 323 1.6i GT 3-Door	https://www.automobile-catalog.com/car/1989/1631300/mazda_323_1_6i.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-02	4000	1645	1390	Automobile-Catalog 1989 Mazda 323 1.5 GLX 5-Door	https://www.automobile-catalog.com/car/1989/1631270/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.5 GLX Europe	https://www.automobile-catalog.com/car/1986/1629980/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.5 GLX Europe	https://www.automobile-catalog.com/car/1986/1630010/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BW-WAGON-PREFL-01	4220	1645	1430	Automobile-Catalog 1986 Mazda 323 Station Wagon 1.5 GLX	https://www.automobile-catalog.com/car/1986/55835/mazda_323_station_wagon_1_5_glx.html
EU-MAZDA-323-III-BW-WAGON-FACELIFT-01	4235	1645	1430	Automobile-Catalog 1993 Mazda 323 Station Wagon 1.6i GLX Catalyst	https://www.automobile-catalog.com/car/1993/1631675/mazda_323_station_wagon_1_6i_glx_cat.html
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370	Automobile-Catalog 1979 Mazda 626 1.6 Europe	https://www.automobile-catalog.com/car/1979/35270/mazda_626_1600.html
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395	Automobile-Catalog 1983 Mazda 626 1.6 LX	https://www.automobile-catalog.com/car/1983/1626035/mazda_626_1_6_lx.html
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350	Automobile-Catalog 1983 Mazda 626 1.6 LX 5-Door	https://www.automobile-catalog.com/car/1983/1626080/mazda_626_1_6_lx_5-door.html
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410	Automobile-Catalog 1983 Mazda 626 2.0 GLX	https://www.automobile-catalog.com/car/1983/1626350/mazda_626_2_0_glx.html
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365	Automobile-Catalog 1983 Mazda 626 2.0 GLX 5-Door	https://www.automobile-catalog.com/car/1983/1626110/mazda_626_2_0_glx_5-door.html
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410	Automobile-Catalog 1988 Mazda 626 2.0 LX Catalyst	https://www.automobile-catalog.com/car/1988/1633955/mazda_626_2_0_lx_cat.html
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375	Automobile-Catalog 1988 Mazda 626 2.0i GLX 5-Door Automatic Catalyst	https://www.automobile-catalog.com/car/1988/1634030/mazda_626_2_0i_glx_5-d_automatic_cat.html
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360	Automobile-Catalog 1988 Mazda 626 2.0i 16V GT Coupe	https://www.automobile-catalog.com/car/1988/1633940/mazda_626_2_0i_16v_gt_coupe.html
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430	Automobile-Catalog 1988 Mazda 626 2.0 12V GLX Estate	https://www.automobile-catalog.com/car/1988/1634480/mazda_626_2_0_12v_glx_estate.html
EU-MAZDA-929-I-LA4-SEDAN-4D-PREFL-01	4645	1715	1415	Automobile-Catalog 1979 Mazda 929L Europe	https://www.automobile-catalog.com/car/1979/1621895/mazda_929l.html
EU-MAZDA-929-I-LA4-SEDAN-4D-FACELIFT-01	4665	1710	1410	Automobile-Catalog 1980 Mazda 929L Europe	https://www.automobile-catalog.com/car/1980/25520/mazda_929.html
EU-MAZDA-929-III-HB-SEDAN-4D-01	4670	1690	1420	Automobile-Catalog 1982 Mazda 929 Europe	https://www.automobile-catalog.com/car/1982/25775/mazda_929.html
EU-MAZDA-929-III-HB-COUPE-2D-01	4640	1690	1355	Automobile-Catalog 1982 Mazda 929 Hardtop Europe	https://www.automobile-catalog.com/car/1982/1628945/mazda_929_hardtop.html
EU-MAZDA-929-II-LA4-WAGON-5D-01	4650	1715	1445	Automobile-Catalog 1982 Mazda 929 Station Wagon Europe	https://www.automobile-catalog.com/car/1982/1628900/mazda_929_station_wagon.html
EU-MAZDA-929-IV-HC-SEDAN-4D-01	4885	1705	1425	Automobile-Catalog 1988 Mazda 929 2.2i GLX Europe	https://www.automobile-catalog.com/car/1988/60350/mazda_929_2_2i_glx.html
EU-MAZDA-E-SERIES-III-SR2-VAN-01	4690	1690	1960	CarsGuide 1985 Mazda E2200 dimensions	https://www.carsguide.com.au/mazda/e2200/car-dimensions/1985
EU-MAZDA-E-SERIES-III-SR1-MPV-01	4965	1690	1955	Truck1 Mazda E2000 Bus SR1 technical data	https://www.truck1.eu/blog/mazda-e2000-bus-sr1-2-0-82-hp-tech-specs-t28416
EU-SSANGYONG-KYRON-I-SUV-5D-01	4660	1880	1755	CarsGuide 2006 SsangYong Kyron dimensions;Auto-Data SsangYong Kyron facelift 270 SPR	https://www.carsguide.com.au/ssangyong/kyron/car-dimensions/2006;https://www.auto-data.net/en/ssangyong-kyron-facelift-2007-270-spr-163hp-awd-t-tronic-41827
EU-MAZDA-RX-7-I-SA22C-COUPE-PREFL-01	4285	1675	1260	Automobile-Catalog 1979 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1979/37265/mazda_rx-7.html
EU-MAZDA-RX-7-I-SA22C-COUPE-FACELIFT-01	4320	1670	1260	Automobile-Catalog 1981 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1981/26795/mazda_rx-7.html
EU-MAZDA-323-IV-BG-S-SEDAN-4D-01	4215	1675	1375	Automobile-Catalog 1990 Mazda 323 1.3 16V LX Sedan Europe	https://www.automobile-catalog.com/car/1990/1645625/mazda_323_1_3_16v_lx_sedan.html
EU-MAZDA-323-IV-BG-C-HATCHBACK-3D-01	3995	1675	1380	Automobile-Catalog 1990 Mazda 323 1.3 16V LX Hatchback Europe	https://www.automobile-catalog.com/car/1990/1645610/mazda_323_1_3_16v_lx_hatchback.html
EU-MAZDA-323-IV-BG-C-HATCHBACK-GT-3D-01	4030	1675	1380	Automobile-Catalog 1990 Mazda 323 1.9i 16V GT Hatchback catalyst Europe	https://www.automobile-catalog.com/car/1990/64385/mazda_323_1_9i_16v_gt_hatchback_cat.html
EU-MAZDA-323-IV-BG-F-HATCHBACK-5D-01	4260	1675	1335	Automobile-Catalog 1990 Mazda 323F 1.6 16V GLX Europe	https://www.automobile-catalog.com/car/1990/1645640/mazda_323f_1_6_16v_glx.html
EU-MAZDA-RX-7-II-FC-COUPE-PREFL-01	4310	1690	1270	Automobile-Catalog 1986 Mazda RX-7 Europe	https://www.automobile-catalog.com/car/1986/54140/mazda_rx-7.html
EU-MAZDA-RX-7-II-FC-COUPE-FACELIFT-01	4335	1690	1265	Automobile-Catalog 1990 Mazda RX-7 Turbo II Europe	https://www.automobile-catalog.com/car/1990/1639205/mazda_rx-7_turbo_ii.html
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230	Automobile-Catalog 1990 Mazda MX-5 Europe	https://www.automobile-catalog.com/car/1990/1640945/mazda_mx-5.html
EU-MAZDA-121-II-DB-SEDAN-4D-01	3800	1655	1470	Automobile-Catalog 1991 Mazda 121 1.3 GLX Europe	https://www.automobile-catalog.com/car/1991/1647830/mazda_121_1_3_glx.html
EU-MAZDA-MX-3-EC-COUPE-3D-01	4220	1695	1310	Automobile-Catalog 1992 Mazda MX-3 16V Europe	https://www.automobile-catalog.com/car/1992/1648550/mazda_mx-3_16v.html
EU-MAZDA-MX-6-II-GE-COUPE-2D-01	4615	1750	1310	Automobile-Catalog 1992 Mazda MX-6 2.0i 16V Europe	https://www.automobile-catalog.com/car/1992/1655285/mazda_mx-6_2_0i_16v.html
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400	Automobile-Catalog 1992 Mazda 626 1.9i LX Sedan Europe	https://www.automobile-catalog.com/car/1992/1651100/mazda_626_1_9i_lx.html
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390	Automobile-Catalog 1992 Mazda 626 1.9i LX 5-door Europe	https://www.automobile-catalog.com/car/1992/1650995/mazda_626_1_9i_lx_5-d.html
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355	Auto-Data Mazda Xedos 6 CA	https://www.auto-data.net/en/mazda-xedos-6-model-1210
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395	Automobile-Catalog 1993 Mazda Xedos 9 2.5i V6 4WS Europe	https://www.automobile-catalog.com/car/1993/1653365/mazda_xedos_9_2_5i_v6_4ws.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3501-3600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html "https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html"
[2]: https://www.automobile-catalog.com/car/1987/1630220/mazda_323_1_5_glx_sedan.html "https://www.automobile-catalog.com/car/1987/1630220/mazda_323_1_5_glx_sedan.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3501-3600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3501-3600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4810 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1439 行）

