# 任务：all 第 3201-3300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0033__f2f316be


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3201-3300 行

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
all 第 3201-3300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427
EU-AUDI-A4-B7-8ED-WAGON-01	4586	1772	1453
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391
EU-AUDI-A4-B7-CONVERTIBLE-02	4570	1780	1390
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453
EU-AUDI-A4-B7-WAGON-5D-02	4586	1772	1427
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-A4-B8-FACELIFT-SEDAN-01	4701	1826	1427
EU-AUDI-A4-B8-FACELIFT-WAGON-01	4699	1826	1436
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	5039	1902	1491
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	5039	1902	1491
EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	5179	1902	1484
EU-FIAT-IDEA-MPV-350-01	3930	1698	1660
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	5651	1974	2524
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	5651	1974	2303
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	5201	1974	2529
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	5201	1974	2309
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	4834	1974	1974
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	4834	1974	2313
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-02	6474	2084	2380
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	6390	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	6002	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	5552	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	6390	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	6002	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	5552	1974	2030
EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	6403	2084	2624
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	6403	2084	2380
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	6403	2008	2624
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	6403	1974	2624
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	5680	1974	2590
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	5680	1974	2381
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	5680	1974	2606
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	5680	1974	2394
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	5230	1974	2594
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	5230	1974	2047
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	5230	1974	2611
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	5230	1974	2397
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	6403	2084	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-02	6474	2084	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-02	6474	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-02	5751	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-02	5751	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475
EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	3785	1719	1143
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-NISSAN-PATHFINDER-III-R51-SUV-01	4740	1850	1865
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870
EU-RENAULT-CLIO-II-HATCHBACK-01	3773	1639	1417
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-3D-02	3986	1719	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-02	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477
EU-RENAULT-CLIO-II-PHASE-III-VAN-01	3811	1639	1417
EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	4496	1810	1636
EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	4493	1810	1636
EU-RENAULT-KANGOO-I-FACELIFT-MPV-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844
EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	4510	1750	1430
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	4228	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	4498	1777	1460
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695
EU-SUZUKI-GRAND-VITARA-II-3D-PREFL-SUV-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	3905	1695	1685
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	3905	1780	1740
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Saab	9-5	2.3 T Biopower	Stufenheck	Frontantrieb	Benzin/Ethanol	152	207	Nov 2006	Dec 2009	2024-03-01	29885
Lotus	Esprit s4	2.2	Coupe	Heckantrieb	Benzin	170	231	Sep 1990	Dec 1991	2024-03-01	29890
Lotus	Esprit s4	2.2	Coupe	Heckantrieb	Benzin	160	218	Sep 1988	Mar 1992	2024-03-01	29891
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	99	135	Oct 2003	-	2024-03-01	29910
Saab	9-3	2.8 Turbo V6	Stufenheck	Frontantrieb	Benzin	203	276	Apr 2008	Feb 2015	2024-03-01	29913
MG	Zr	2.0 TD	Schrägheck	Frontantrieb	Diesel	83	113	Dec 2002	Apr 2005	2025-12-01	29914
Renault	Grand scénic ii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	78	106	May 2005	Jan 2009	2024-03-01	29917
Saab	9-3	2.8 Turbo V6	Kombi	Frontantrieb	Benzin	203	276	May 2008	Feb 2015	2024-03-01	29919
Opel	Insignia a sports tourer	1.6	Kombi	Frontantrieb	Benzin	85	116	Jul 2008	Jun 2012	2024-03-01	29923
Opel	Insignia a sports tourer	1.8	Kombi	Frontantrieb	Benzin	103	140	Jul 2008	Mar 2017	2024-03-01	29924
Opel	Insignia a sports tourer	2.0 Turbo	Kombi	Frontantrieb	Benzin	162	220	Jul 2008	Jun 2013	2024-03-01	29925
Opel	Insignia a sports tourer	2.8 V6 Turbo 4X4	Kombi	Allrad	Benzin	191	260	Oct 2008	Jun 2013	2024-03-01	29926
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	81	110	Jul 2008	Jun 2013	2024-03-01	29927
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	96	131	Jul 2008	Jun 2015	2024-03-01	29928
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	118	160	Jul 2008	Jun 2015	2024-03-01	29929
Opel	Insignia a	2.0 Biturbo Cdti	Schrägheck	Frontantrieb	Diesel	140	190	Jul 2008	Dec 2011	2024-03-01	29930
Opel	Insignia a sports tourer	2.0 Biturbo Cdti	Kombi	Frontantrieb	Diesel	140	190	Jul 2008	Mar 2017	2024-03-01	29932
BMW	1	118 D	Cabriolet	Heckantrieb	Diesel	105	143	Sep 2008	Dec 2013	2024-03-01	29943
BMW	1	123 D	Cabriolet	Heckantrieb	Diesel	150	204	Sep 2008	Dec 2013	2024-03-01	29944
BMW	7	740 I, LI	Stufenheck	Heckantrieb	Benzin	240	326	Sep 2008	Jun 2012	2024-03-01	29945
BMW	7	750 I, LI	Stufenheck	Heckantrieb	Benzin	300	408	Sep 2008	Jun 2012	2024-03-01	29946
BMW	7	730 D	Stufenheck	Heckantrieb	Diesel	180	245	Sep 2008	Jun 2012	2024-03-01	29947
Renault	Kangoo	1.6	Großraumlimousine	Frontantrieb	Benzin	78	106	Feb 2009	Dec 2012	2024-03-01	29948
Renault	Kangoo	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	76	103	Feb 2009	Dec 2012	2024-03-01	29949
Renault	Megane iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	74	101	Nov 2008	Aug 2015	2024-03-01	29950
Renault	Megane iii	2.0 TCE	Schrägheck	Frontantrieb	Benzin	132	180	Nov 2008	Aug 2015	2024-03-01	29951
Renault	Megane iii	2.0 CVT	Schrägheck	Frontantrieb	Benzin	103	140	Feb 2009	Aug 2015	2024-03-01	29952
Renault	Megane iii	1.4 TCE	Schrägheck	Frontantrieb	Benzin	96	131	Apr 2009	Aug 2015	2024-03-01	29953
Renault	Megane iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	66	90	Nov 2008	Aug 2015	2024-03-01	29954
Renault	Megane iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	81	110	Feb 2009	Dec 2015	2024-03-01	29956
Renault	Megane iii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	118	160	Apr 2009	Aug 2015	2024-03-01	29957
Renault	Megane iii	1.4 TCE	Coupe	Frontantrieb	Benzin	96	131	Apr 2009	Aug 2015	2024-03-01	29958
Renault	Megane iii	1.6 16V	Coupe	Frontantrieb	Benzin	74	101	Nov 2008	Aug 2015	2024-03-01	29959
Renault	Megane iii	2.0 TCE	Coupe	Frontantrieb	Benzin	132	180	Nov 2008	Aug 2015	2024-03-01	29960
Renault	Megane iii	1.5 DCI	Coupe	Frontantrieb	Diesel	66	90	Nov 2008	Aug 2015	2024-03-01	29961
Renault	Megane iii	1.5 DCI	Coupe	Frontantrieb	Diesel	81	110	Feb 2009	Aug 2015	2024-03-01	29962
Renault	Megane iii	2.0 DCI	Coupe	Frontantrieb	Diesel	118	160	Apr 2009	Aug 2015	2024-03-01	29963
Renault	Laguna	2.0 GT	Coupe	Frontantrieb	Benzin	150	204	Sep 2008	Dec 2015	2024-03-01	29964
Renault	Laguna	2.0 DCI	Coupe	Frontantrieb	Diesel	110	150	Sep 2008	Dec 2015	2024-03-01	29965
Renault	Laguna	2.0 DCI GT	Coupe	Frontantrieb	Diesel	131	178	Sep 2008	Dec 2015	2024-03-01	29966
Ford	Transit	2.4 Tdci 4X4	Kasten	Allrad	Diesel	103	140	Nov 2006	Aug 2014	2024-03-01	29967
Ford	Transit	2.4 Tdci 4X4	Pritsche/Fahrgestell	Allrad	Diesel	103	140	Nov 2006	Aug 2014	2024-03-01	29968
Ford	Transit	2.2 Tdci	Kasten	Frontantrieb	Diesel	103	140	Oct 2007	Aug 2014	2024-03-01	29969
Ford	Transit	2.2 Tdci	Bus	Frontantrieb	Diesel	103	140	Oct 2007	Aug 2014	2024-03-01	29970
Ford	Transit	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Oct 2007	Aug 2014	2025-12-01	29971
Ford	Transit tourneo	2.2 Tdci	Bus	Frontantrieb	Diesel	103	140	Oct 2007	Aug 2014	2024-03-01	29972
Audi	A5	2.0 Tfsi	Coupe	Frontantrieb	Benzin	132	180	Nov 2008	Mar 2012	2024-03-01	29973
Audi	A5	2.0 Tfsi	Coupe	Frontantrieb	Benzin	155	211	Jun 2008	Nov 2013	2024-03-01	29974
Audi	A5	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	155	211	Jun 2008	Jan 2017	2024-03-01	29975
Audi	A5	2.7 TDI	Coupe	Frontantrieb	Diesel	120	163	Sep 2007	Mar 2012	2024-03-01	29976
Audi	A5	3.0 TDI Quattro	Coupe	Allrad	Diesel	155	211	Mar 2008	May 2010	2024-03-01	29977
Audi	A4 b7	2.0 TDI	Cabriolet	Frontantrieb	Diesel	100	136	Jan 2006	Mar 2009	2024-03-01	29978
Hyundai	Sonata v	3.3	Stufenheck	Frontantrieb	Benzin	184	250	Jan 2008	Dec 2010	2024-03-01	29979
Hyundai	Sonata v	2.0 Vvti GLS	Stufenheck	Frontantrieb	Benzin	121	165	Jan 2008	Dec 2010	2024-03-01	29980
Land Rover	Defender cabrio	2.4 TD4 4X4	Geländewagen offen	Allrad	Diesel	90	122	May 2007	Feb 2016	2024-03-01	29982
Land Rover	Defender station wagon	2.4 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	90	122	Oct 2006	Feb 2016	2024-03-01	29983
Land Rover	Defender pick up	2.4 TD4 4X4	Geländewagen offen	Allrad	Diesel	90	122	May 2007	Feb 2016	2024-03-01	29984
Nissan	Murano ii	3.5 4X4	SUV	Allrad	Benzin	188	256	Oct 2008	Sep 2014	2024-03-01	29985
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	58	78	Aug 2008	Aug 2013	2024-03-01	29986
Renault	Clio iii grandtour	1.2 16V Hi-flex	Kombi	Frontantrieb	Benzin/Ethanol	55	75	Jul 2008	Dec 2014	2026-05-01	29987
Renault	Clio iii	1.2 16V Hi-flex	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	55	75	Jul 2008	Dec 2014	2026-05-01	29988
Renault	Modus / grand	1.2 16V Hi-flex	Schrägheck	Frontantrieb	Benzin/Ethanol	55	75	Oct 2008	Dec 2013	2025-12-01	29989
VW	Golf vi	1.4	Schrägheck	Frontantrieb	Benzin	59	80	Oct 2008	Nov 2012	2024-03-01	29990
VW	Golf vi	1.6	Schrägheck	Frontantrieb	Benzin	75	102	Oct 2008	Nov 2012	2024-03-01	29991
VW	Golf vi	1.4 TSI	Schrägheck	Frontantrieb	Benzin	90	122	Oct 2008	Nov 2012	2024-03-01	29992
VW	Golf vi	1.4 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Oct 2008	Nov 2012	2024-03-01	29993
VW	Golf vi	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Oct 2008	May 2013	2024-03-01	29994
VW	Golf vi	2.0 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Oct 2008	Nov 2012	2024-03-01	29995
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	110	150	May 2008	Jul 2018	2024-03-01	29996
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	103	140	Mar 2008	Jul 2018	2024-03-01	29997
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	47	64	Jun 2005	Dec 2010	2026-05-01	29998
Renault	Thalia i	1.5 DCI	Stufenheck	Frontantrieb	Diesel	47	64	Jun 2005	Feb 2009	2025-12-01	29999
Audi	A4 b8	1.8 Tfsi Quattro	Stufenheck	Allrad	Benzin	118	160	Sep 2008	Mar 2012	2024-03-01	30000
Audi	A4 b8	S4 Quattro	Stufenheck	Allrad	Benzin	245	333	Nov 2008	Dec 2015	2024-03-01	30001
Audi	A4 b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Aug 2008	Dec 2015	2024-03-01	30002
Audi	A4 b8	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	155	211	Jun 2008	May 2010	2024-03-01	30003
Audi	A4 b8 avant	1.8 Tfsi Quattro	Kombi	Allrad	Benzin	118	160	Sep 2008	Mar 2012	2024-03-01	30004
Audi	A4 b8 avant	S4 Quattro	Kombi	Allrad	Benzin	245	333	Nov 2008	Dec 2015	2024-03-01	30005
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	100	136	Apr 2008	Dec 2015	2024-03-01	30006
Audi	A4 b8 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	125	170	Aug 2008	Mar 2012	2024-03-01	30007
Audi	A4 b8 avant	2.7 TDI	Kombi	Frontantrieb	Diesel	140	190	Apr 2008	Mar 2012	2024-03-01	30008
Mitsubishi	Lancer v	EVO I	Stufenheck	Allrad	Benzin	184	250	Oct 1992	Dec 1993	2024-03-01	30017
Peugeot	Partner	1.6 HDI 16V 4X4	Kasten/Großraumlimousine	Allrad	Diesel	66	90	Sep 2009	-	2025-11-01	30023
Jaguar	Xk 8	4	Coupe	Heckantrieb	Benzin	216	294	May 1996	Jul 2005	2024-03-01	30052
Jaguar	Xk 8 convertible	4	Cabriolet	Heckantrieb	Benzin	216	294	May 1996	Jul 1999	2024-03-01	30053
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	140	190	Jun 1999	Sep 2003	2024-03-01	30057
Ford USA	Windstar	3.8	Großraumlimousine	Frontantrieb	Benzin	127	173	Sep 2000	Aug 2004	2024-03-01	30058
Ford USA	Explorer	4.0 4WD	SUV	Allrad	Benzin	150	204	Oct 1999	Dec 2001	2024-03-01	30068
Mazda	323 ii hatchback	1.6	Schrägheck	Frontantrieb	Benzin	63	86	Jun 1986	Mar 1987	2024-03-01	30073
Nissan	Pathfinder ii	3.3	Geländewagen geschlossen	Heckantrieb	Benzin	125	170	May 1999	Dec 2004	2024-03-01	30094
Suzuki	Grand vitara i	2.7	Geländewagen geschlossen	Heckantrieb	Benzin	135	184	Sep 2003	Aug 2006	2024-03-01	30102
Cadillac	Eldorado	4.6	Coupe	Frontantrieb	Benzin	205	279	Oct 1993	Sep 2002	2024-03-01	30106
Subaru	Impreza	1.6	Stufenheck	Frontantrieb	Benzin	70	95	Jun 2001	Sep 2006	2024-03-01	30111
Renault	Megane ii	2	Schrägheck	Frontantrieb	Benzin	169	230	Aug 2006	Feb 2008	2024-03-01	30118
Toyota	4	2.7	SUV	Heckantrieb	Benzin	112	152	Nov 1995	Jul 2002	2024-03-01	30126
Mercedes-benz	Vito / mixto	123	Kasten	Heckantrieb	Benzin	170	231	Jun 2004	Jul 2008	2024-03-01	30127
Saab	9-3	2	Cabriolet	Frontantrieb	Benzin	143	194	Apr 2006	Sep 2007	2024-03-01	30128
Fiat	Idea	1.4	Großraumlimousine	Frontantrieb	Benzin	66	90	Dec 2003	-	2024-03-01	30129
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	48	65	May 2005	Nov 2010	2026-05-01	30141
Ssangyong	Actyon	2.0 XDI	SUV	Heckantrieb	Diesel	104	141	Nov 2005	-	2025-12-01	30143


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 35 个既有尺寸组复用，并首次闭合 9 个新尺寸组。
* 新建组覆盖 MG ZR 三门/五门、BMW F01/F02、Laguna III Coupe、Murano Z51、MiTo 及 Golf VI 三门/五门。相关页面分别明确给出了车身形式、门数及不含后视镜宽度。([汽车数据网][1])
* Murano Z51 改款前后核对为相同三维；Golf VI 三门和五门宽度、高度不同，已拆为独立尺寸组。([汽车数据网][2])
* 尚未处理完成的重点是 Megane III 改款边界，以及 Transit、Defender、Vito 等多轴距、多车顶商用车分支。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：62
* 待处理 Ktype：38
* READY 映射：92
* PENDING 映射：38
* 当前引用尺寸组：44
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29885	29885	Sedan	Saab 9-5 I Facelift 2005	YS3E	4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH		READY
29890	29890	Coupe	Lotus Esprit X180		2		LOW	车型名为Esprit S4但生产期为1990-1991，需核对实际子型与外廓。	PENDING: 车型名与生产期冲突
29891	29891	Coupe	Lotus Esprit X180		2		LOW	车型名为Esprit S4但生产期为1988-1992，需核对实际子型与外廓。	PENDING: 车型名与生产期冲突
29910	29910	Convertible	Lotus Elise S2	111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	HIGH		READY
29913	29913	Sedan	Saab 9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH		READY
29914_3dr	29914	Hatchback	MG ZR	RF	3	EU-MG-ZR-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29914_5dr	29914	Hatchback	MG ZR	RF	5	EU-MG-ZR-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29917_prefl	29917	MPV	Renault Grand Scenic II Phase I		5	EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	HIGH	生产期跨Phase I与Phase II，拆分改款前外廓。	READY
29917_facelift	29917	MPV	Renault Grand Scenic II Phase II		5	EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	生产期跨Phase I与Phase II，拆分改款后外廓。	READY
29919	29919	Wagon	Saab 9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH		READY
29923	29923	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29924_prefl	29924	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29924_facelift	29924	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29925	29925	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29926	29926	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29927	29927	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29928_prefl	29928	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29928_facelift	29928	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29929_prefl	29929	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29929_facelift	29929	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29930	29930	Hatchback	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH		READY
29932_prefl	29932	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29932_facelift	29932	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29943	29943	Convertible	BMW 1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
29944	29944	Convertible	BMW 1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
29945_swb	29945	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH	VariantName同时包含i与Li，拆分短轴车身。	READY
29945_lwb	29945	Sedan	BMW 7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	HIGH	VariantName同时包含i与Li，拆分长轴车身。	READY
29946_swb	29946	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH	VariantName同时包含i与Li，拆分短轴车身。	READY
29946_lwb	29946	Sedan	BMW 7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	HIGH	VariantName同时包含i与Li，拆分长轴车身。	READY
29947	29947	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH		READY
29948	29948	MPV	Renault Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
29949	29949	MPV	Renault Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
29950	29950	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29951	29951	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29952	29952	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29953	29953	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29954	29954	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29956	29956	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29957	29957	Hatchback	Renault Megane III		5		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29958	29958	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29959	29959	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29960	29960	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29961	29961	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29962	29962	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29963	29963	Coupe	Renault Megane III Coupe		3		MEDIUM	生产期可能跨改款，需按外廓变化确认并建立尺寸组。	PENDING: 改款边界与尺寸组未闭合
29964	29964	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29965	29965	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29966	29966	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29967	29967	Van	Ford Transit Mk7				LOW	四驱厢式车可能覆盖多个轴距和车顶，需确认具体物理分支。	PENDING: 轴距/车顶分支未确认
29968	29968	Pickup	Ford Transit Mk7				LOW	四驱Pritsche/Fahrgestell可能覆盖单排/双排及多个轴距，需确认具体物理分支。	PENDING: CAB/轴距分支未确认
29969	29969	Van	Ford Transit Mk7				LOW	前驱厢式车可能覆盖多个轴距和车顶，需确认全部物理分支。	PENDING: 轴距/车顶分支未确认
29970	29970	MPV	Ford Transit Mk7				LOW	Bus可能覆盖不同轴距、车顶和座位布局，需确认物理分支。	PENDING: 轴距/车顶分支未确认
29971	29971	Pickup	Ford Transit Mk7				LOW	前驱Pritsche/Fahrgestell可能覆盖多个轴距及驾驶室形式，需确认物理分支。	PENDING: CAB/轴距分支未确认
29972	29972	MPV	Ford Transit Mk7 Tourneo				MEDIUM	需确认该Ktype是否仅对应SWB低顶Tourneo。	PENDING: 物理分支未确认
29973	29973	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29974_prefl	29974	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29974_facelift	29974	Coupe	Audi A5 8T Facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29975_prefl	29975	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29975_facelift	29975	Coupe	Audi A5 8T Facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29976	29976	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29977	29977	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29978	29978	Convertible	Audi A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH		READY
29979	29979	Sedan	Hyundai Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
29980	29980	Sedan	Hyundai Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
29982	29982	Convertible	Land Rover Defender L316		2		LOW	开放式Defender需确认90/110轴距及软顶车身边界。	PENDING: 轴距/车身分支未确认
29983	29983	SUV	Land Rover Defender L316				LOW	Station Wagon可能覆盖90与110轴距，需拆分并首次建组。	PENDING: 轴距分支未确认
29984	29984	Pickup	Land Rover Defender L316				LOW	Pick Up可能覆盖110与130及驾驶室形式，需确认全部分支。	PENDING: CAB/轴距分支未确认
29985	29985	SUV	Nissan Murano II	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-5D-01	HIGH	改款前后已核对为同一三维，复用同一尺寸组。	READY
29986	29986	Hatchback	Alfa Romeo MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH		READY
29987	29987	Wagon	Renault Clio III Grandtour		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
29988_3dr_prefl	29988	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_5dr_prefl	29988	Hatchback	Renault Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_3dr_facelift	29988	Hatchback	Renault Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_5dr_facelift	29988	Hatchback	Renault Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29989	29989	Hatchback	Renault Modus I		5		LOW	Model同时标注Modus/Grand，需拆分标准轴距与Grand外廓。	PENDING: 标准版/Grand尺寸组未闭合
29990_3dr	29990	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29990_5dr	29990	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29991_3dr	29991	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29991_5dr	29991	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29992_3dr	29992	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29992_5dr	29992	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29993_3dr	29993	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29993_5dr	29993	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29994_3dr	29994	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29994_5dr	29994	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29995_3dr	29995	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29995_5dr	29995	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29996_prefl	29996	SUV	Volkswagen Tiguan 5N Pre-facelift	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29996_facelift	29996	SUV	Volkswagen Tiguan 5N Facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29997_prefl	29997	SUV	Volkswagen Tiguan 5N Pre-facelift	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29997_facelift	29997	SUV	Volkswagen Tiguan 5N Facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29998	29998	Hatchback	Renault Clio II			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH		READY
29999	29999	Sedan	Renault Thalia I Facelift		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	HIGH		READY
30000	30000	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
30001_prefl	30001	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30001_facelift	30001	Sedan	Audi A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30002_prefl	30002	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30002_facelift	30002	Sedan	Audi A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30003	30003	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
30004	30004	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30005_prefl	30005	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30005_facelift	30005	Wagon	Audi A4 B8 Avant Facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30006_prefl	30006	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30006_facelift	30006	Wagon	Audi A4 B8 Avant Facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30007	30007	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30008	30008	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30017	30017	Sedan	Mitsubishi Lancer Evolution I	CD9A	4		MEDIUM	需首次建立Evolution I尺寸组。	PENDING: 缺少已确认尺寸组
30023	30023	Van	Peugeot Partner II	B9			LOW	4X4版本可能有Dangel改装高度，需确认L1/L2及特殊悬架外廓。	PENDING: 轴距/4X4外廓未确认
30052	30052	Coupe	Jaguar XK8 X100	X100	2		MEDIUM	需首次建立X100 Coupe尺寸组。	PENDING: 缺少已确认尺寸组
30053	30053	Convertible	Jaguar XK8 X100	X100	2		MEDIUM	需首次建立X100 Convertible尺寸组。	PENDING: 缺少已确认尺寸组
30057	30057	Convertible	Ford Mustang IV New Edge	SN95	2		MEDIUM	需首次建立1999-2003 Convertible尺寸组。	PENDING: 缺少已确认尺寸组
30058	30058	MPV	Ford Windstar II		5		MEDIUM	需首次建立2000-2004 Windstar尺寸组。	PENDING: 缺少已确认尺寸组
30068	30068	SUV	Ford Explorer II		5		MEDIUM	现有Explorer III组不适用，需首次建立1999-2001 Explorer II尺寸组。	PENDING: 缺少已确认尺寸组
30073	30073	Hatchback	Mazda 323 BF				LOW	需确认三门/五门覆盖边界及对应外廓。	PENDING: 门数分支未确认
30094	30094	SUV	Nissan Pathfinder II	R50	5		MEDIUM	需首次建立R50尺寸组。	PENDING: 缺少已确认尺寸组
30102	30102	SUV	Suzuki Grand Vitara I		5		LOW	2.7版本可能对应XL-7长车身，需确认车型边界与尺寸。	PENDING: 子型与外廓未确认
30106	30106	Coupe	Cadillac Eldorado X		2		MEDIUM	需首次建立1993-2002 Eldorado尺寸组。	PENDING: 缺少已确认尺寸组
30111_prefl	30111	Sedan	Subaru Impreza II Pre-facelift	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	HIGH	生产期跨三种前后外廓，拆分初期车型。	READY
30111_facelift1	30111	Sedan	Subaru Impreza II Facelift 1	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	HIGH	生产期跨三种前后外廓，拆分第一次改款。	READY
30111_facelift2	30111	Sedan	Subaru Impreza II Facelift 2	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH	生产期跨三种前后外廓，拆分第二次改款。	READY
30118	30118	Hatchback	Renault Megane II Phase II RS		3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	高功率RS为三门外形。	READY
30126	30126	SUV	Toyota 4Runner III	N180	5		LOW	输入Model为“4”，需确认是否为4Runner/Hilux Surf及改款外廓。	PENDING: 车型名称与外廓未闭合
30127	30127	Van	Mercedes-Benz Vito W639	W639			LOW	Vito/Mixto Kasten可能覆盖Compact/Long/Extra-long及不同车顶，需确认全部分支。	PENDING: 轴距/车顶分支未确认
30128	30128	Convertible	Saab 9-3 II Pre-facelift	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH		READY
30129	30129	MPV	Fiat Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
30141_3dr_prefl	30141	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_5dr_prefl	30141	Hatchback	Renault Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_3dr_facelift	30141	Hatchback	Renault Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_5dr_facelift	30141	Hatchback	Renault Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30143	30143	SUV	SsangYong Actyon I	CJ	5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MG-ZR-HATCHBACK-3D-01	4011	1690	1400	Auto-Data.net MG ZR 2.0 TDi (113 Hp)	https://www.auto-data.net/en/mg-zr-2.0-tdi-113hp-14045
EU-MG-ZR-HATCHBACK-5D-01	4011	1690	1400	Auto-Data.net MG ZR 2.0 TDi (113 Hp)	https://www.auto-data.net/en/mg-zr-2.0-tdi-113hp-14045
EU-BMW-7-SERIES-F01-SEDAN-SWB-01	5072	1902	1479	Auto-Data.net BMW 7 Series (F01) 740i (326 Hp)	https://www.auto-data.net/en/bmw-7-series-f01-740i-326hp-steptronic-9703
EU-BMW-7-SERIES-F02-SEDAN-LWB-01	5212	1902	1479	Auto-Data.net BMW 7 Series Long (F02) generation	https://www.auto-data.net/en/bmw-7-series-long-f02-generation-4308
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400	Auto-Data.net Renault Laguna Coupe 2.0 dCi FAP (150 Hp)	https://www.auto-data.net/en/renault-laguna-coupe-2.0-dci-fap-150hp-10281
EU-NISSAN-MURANO-II-Z51-SUV-5D-01	4860	1885	1720	Auto-Data.net Nissan Murano II (Z51) 3.5 (256 Hp); Auto-Data.net Nissan Murano II (Z51 facelift 2010) 3.5 V6	https://www.auto-data.net/en/nissan-murano-ii-z51-3.5-256hp-17037;https://www.auto-data.net/en/nissan-murano-ii-z51-facelift-2010-3.5-v6-249hp-4wd-cvt-24767
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440	Auto-Data.net Alfa Romeo MiTo 1.4 MPI (78 Hp)	https://www.auto-data.net/en/alfa-romeo-mito-1.4-mpi-78hp-16682
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479	Auto-Data.net Volkswagen Golf VI (3-door) 1.4 TSI (122 Hp)	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-1.4-tsi-122hp-8595
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480	Auto-Data.net Volkswagen Golf VI (5-door) 1.6 (102 Hp)	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-1.6-102hp-41256
```

## 下一步优先处理

1. 批量闭合 Renault Megane III Hatchback 与 Coupe 的改款前后尺寸组，一次解决 Ktype 29950–29963。
2. 处理普通乘用车新组：Evolution I、XK8、Mustang、Windstar、Explorer II、Pathfinder R50、Eldorado。
3. 核对 Lotus Esprit、Mazda 323、Grand Vitara 2.7、Toyota“4”等车型或子型名称冲突。
4. 最后集中拆解 Transit、Defender、Partner 4X4、Vito 的轴距、车顶和驾驶室分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mg-zr-2.0-tdi-113hp-14045 "MG ZR 2.0 TDi (113 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/nissan-murano-ii-z51-3.5-256hp-17037 "Nissan Murano II (Z51) 3.5 (256 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮关闭 20 个 Ktype 的 PENDING，新增 40 行 READY 映射；首次创建 13 个尺寸组。
* Renault Megane III 已按外廓变化批量闭合：Hatchback 分改款前与改款后两个尺寸组；Coupe 分 Phase I、Phase II、Phase III 三个尺寸组。Modus / Grand Modus 已按标准轴距和长轴距拆分。([汽车数据网][1])
* 同时闭合 Mitsubishi Lancer Evolution I、Jaguar XK8 Coupe/Convertible、Ford Mustang Convertible、Ford Explorer II 和 Cadillac Eldorado XII。([汽车目录][2])
* Toyota 4Runner 2.7 后驱资料仍给出多个悬架/轮胎配置高度范围，无法落盘单一 HeightMM，本轮保持原 PENDING，未创建猜测性尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：82
* 待处理 Ktype：18
* READY 映射：132
* PENDING 映射：18
* 已确认尺寸组：57
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29950_prefl	29950	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29950_facelift	29950	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29951_prefl	29951	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29951_facelift	29951	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29952_prefl	29952	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29952_facelift	29952	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29953_prefl	29953	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29953_facelift	29953	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29954_prefl	29954	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29954_facelift	29954	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29956_prefl	29956	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29956_facelift	29956	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29957_prefl	29957	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29957_facelift	29957	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29958_prefl	29958	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29958_facelift1	29958	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29958_facelift2	29958	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29959_prefl	29959	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29959_facelift1	29959	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29959_facelift2	29959	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29960_prefl	29960	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29960_facelift1	29960	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29960_facelift2	29960	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29961_prefl	29961	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29961_facelift1	29961	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29961_facelift2	29961	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29962_prefl	29962	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29962_facelift1	29962	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29962_facelift2	29962	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29963_prefl	29963	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29963_facelift1	29963	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29963_facelift2	29963	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29989_swb	29989	MPV	Renault Modus I Phase II		5	EU-RENAULT-MODUS-I-PHASE-II-MPV-SWB-5D-01	HIGH	输入Model覆盖标准版与Grand，按轴距外廓拆分。	READY
29989_lwb	29989	MPV	Renault Grand Modus I Phase II		5	EU-RENAULT-GRAND-MODUS-I-PHASE-II-MPV-LWB-5D-01	HIGH	输入Model覆盖标准版与Grand，按轴距外廓拆分。	READY
30017	30017	Sedan	Mitsubishi Lancer Evolution I	CD9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-I-CD9A-SEDAN-4D-01	HIGH		READY
30052	30052	Coupe	Jaguar XK8 X100	X100	2	EU-JAGUAR-XK8-X100-COUPE-2D-01	HIGH		READY
30053	30053	Convertible	Jaguar XK8 X100	X100	2	EU-JAGUAR-XK8-X100-CONVERTIBLE-2D-01	HIGH		READY
30057	30057	Convertible	Ford Mustang IV New Edge	SN95	2	EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	HIGH		READY
30068	30068	SUV	Ford Explorer II		5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	HIGH		READY
30106	30106	Coupe	Cadillac Eldorado XII		2	EU-CADILLAC-ELDORADO-XII-COUPE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	4295	1808	1491	Auto-Data.net Renault Megane III generation	https://www.auto-data.net/en/renault-megane-iii-generation-2145
EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	4295	1808	1471	Auto-Data.net Renault Megane III Phase II;Auto-Data.net Renault Megane III Phase III	https://www.auto-data.net/en/renault-megane-iii-phase-ii-2012-generation-3872;https://www.auto-data.net/en/renault-megane-iii-phase-iii-2014-generation-4123
EU-RENAULT-MEGANE-III-COUPE-PREFL-01	4299	1804	1435	Auto-Data.net Renault Megane III Coupe	https://www.auto-data.net/en/renault-megane-iii-coupe-generation-2146
EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	4299	1785	1423	Auto-Data.net Renault Megane III Coupe Phase II	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-ii-2012-generation-3875
EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	4299	1848	1435	Auto-Data.net Renault Megane III Coupe Phase III	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-iii-2014-generation-4288
EU-RENAULT-MODUS-I-PHASE-II-MPV-SWB-5D-01	3874	1709	1589	Auto-Data.net Renault Modus Phase II	https://www.auto-data.net/en/renault-modus-phase-ii-generation-5554
EU-RENAULT-GRAND-MODUS-I-PHASE-II-MPV-LWB-5D-01	4034	1709	1589	Auto-Data.net Renault Grand Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-16v-75hp-29949
EU-MITSUBISHI-LANCER-EVOLUTION-I-CD9A-SEDAN-4D-01	4310	1695	1395	Automobile-Catalog 1992 Mitsubishi Lancer GSR Evolution	https://www.automobile-catalog.com/car/1992/1950440/mitsubishi_lancer_gsr_evolution.html
EU-JAGUAR-XK8-X100-COUPE-2D-01	4760	1829	1306	Auto-Data.net Jaguar XK Coupe X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x100-4.0-v8-284hp-automatic-240
EU-JAGUAR-XK8-X100-CONVERTIBLE-2D-01	4760	1829	1306	Auto-Data.net Jaguar XK Convertible X100	https://www.auto-data.net/en/jaguar-xk-convertible-x100-generation-68
EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	4653	1857	1351	Auto-Data.net Ford Mustang Convertible IV 3.8 V6	https://www.auto-data.net/en/ford-mustang-convertible-iv-3.8-v6-190hp-7779
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800	Auto-Data.net Ford Explorer II 4.0 XLT 4WD	https://www.auto-data.net/en/ford-explorer-ii-4.0-xlt-4wd-208hp-7872
EU-CADILLAC-ELDORADO-XII-COUPE-2D-01	5136	1918	1370	Auto-Data.net Cadillac Eldorado XII	https://www.auto-data.net/en/cadillac-eldorado-xii-generation-2483
```

## 下一步优先处理

1. 集中拆解 Transit 和 Vito/Mixto 的轴距、车顶及驾驶室分支。
2. 处理 Defender 90/110/130 与 Peugeot Partner 4X4 特殊底盘外廓。
3. 最后关闭 Lotus Esprit、Windstar、Mazda 323、Pathfinder R50、Grand Vitara 2.7 和 Toyota 4Runner 的车型或高度配置冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-megane-iii-generation-2145 "Renault Megane III | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1992/1950440/mitsubishi_lancer_gsr_evolution.html?utm_source=chatgpt.com "1992 Mitsubishi Lancer GSR Evolution Specs Review (184 ..."
[3]: https://www.auto-data.net/en/toyota-4runner-iii-2.7-16v-150hp-30908 "Toyota 4Runner III 2.7 16V (150 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮消除 9 个 Ktype 的 PENDING，新增 18 行 READY 映射，首次创建 7 个尺寸组。
* Lotus Esprit 两个功率版本已按生产期和功率归入 X180 时期共同外廓；输入中的“S4”标签与生产期冲突，不再用于代际判定。([汽车数据网][1])
* Transit 29969、29970、29972 已按前驱厢式车、Bus 和 Tourneo 的轴距及车顶分支链接既有缓存组，没有重复创建尺寸组。Ford 资料明确区分 SWB、MWB、LWB、低顶、中顶和高顶外廓。
* Mazda 323 BF 已拆分三门和五门；Pathfinder R50、Grand Vitara XL-7 以及后驱 4Runner III 已完成首次建组。4Runner 因生产期覆盖两种车长，拆分改款前后。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：91
* 待处理 Ktype：9
* READY 映射：150
* PENDING 映射：9
* 已确认尺寸组：64
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29890	29890	Coupe	Lotus Esprit X180		2	EU-LOTUS-ESPRIT-X180-COUPE-2D-01	MEDIUM	功率与生产期对应X180时期Esprit；输入S4标签不作为代际依据。	READY
29891	29891	Coupe	Lotus Esprit X180		2	EU-LOTUS-ESPRIT-X180-COUPE-2D-01	MEDIUM	功率与生产期对应X180时期Esprit；输入S4标签不作为代际依据。	READY
29969_swb_lowroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_swb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_lowroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_highroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_lwb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_lwb_highroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29970_mwb_medroof	29970	MPV	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	MEDIUM	前驱Bus按中轴和长轴中顶外廓拆分。	READY
29970_lwb_medroof	29970	MPV	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	MEDIUM	前驱Bus按中轴和长轴中顶外廓拆分。	READY
29972	29972	MPV	Ford Transit Mk7 Tourneo			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH		READY
30073_3dr	30073	Hatchback	Mazda 323 III	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门掀背车身。	READY
30073_5dr	30073	Hatchback	Mazda 323 III	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门掀背车身。	READY
30094	30094	SUV	Nissan Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
30102	30102	SUV	Suzuki Grand Vitara I XL-7	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	HIGH	2.7版本对应XL-7长车身。	READY
30126_prefl	30126	SUV	Toyota 4Runner III Pre-facelift	N180	5	EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-PREFL-01	MEDIUM	输入Model“4”按2.7后驱及生产期确认4Runner III；生产期跨外廓变更。	READY
30126_facelift	30126	SUV	Toyota 4Runner III Facelift	N180	5	EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-FACELIFT-01	MEDIUM	输入Model“4”按2.7后驱及生产期确认4Runner III；生产期跨外廓变更。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LOTUS-ESPRIT-X180-COUPE-2D-01	4330	1860	1150	Auto-Data.net Lotus Esprit 2.2 i Turbo (231 Hp);Auto-Data.net Lotus Esprit 2.2 Turbo (218 Hp)	https://www.auto-data.net/en/lotus-esprit-2.2-i-turbo-231hp-8302;https://www.auto-data.net/en/lotus-esprit-2.2-turbo-218hp-8304
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6i LX catalyst 3-door	https://www.automobile-catalog.com/car/1986/1630055/mazda_323_1_6i_lx_cat.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6i GLX catalyst 5-door	https://www.automobile-catalog.com/car/1986/1630040/mazda_323_1_6i_glx_cat.html
EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	4530	1840	1750	Auto-Data.net Nissan Pathfinder II 3.3 V6 (170 Hp) 4WD	https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930
EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	4760	1780	1740	Automobile-Catalog 2004 Suzuki Grand Vitara XL-7 2.7 V6	https://www.automobile-catalog.com/car/2004/3353120/suzuki_grand_vitara_xl-7_2_7_v6.html
EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-PREFL-01	4540	1690	1690	AutoDetective 1996 Toyota 4Runner 2WD	https://www.autodetective.com/directory/1996/toyota/4runner/trim/2wd/
EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-FACELIFT-01	4656	1689	1715	Edmunds 2000 Toyota 4Runner Base	https://www.edmunds.com/toyota/4runner/2000/st-11110/features-specs/
```

## 下一步优先处理

1. 使用 Land Rover 官方尺寸表批量关闭 Defender 90、110、130 的开放式、Station Wagon 和 Pickup 分支。
2. 关闭 Transit 4×4 厢式车、4×4 Fahrgestell 及前驱 Fahrgestell 分支。
3. 最后处理 Peugeot Partner 4×4、Ford Windstar 和 Mercedes-Benz Vito 123 的特殊底盘或市场尺寸冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lotus-esprit-2.2-i-turbo-231hp-8302 "Lotus Esprit 2.2 i Turbo (231 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1985/1630055/mazda_323_1_6i_lx_cat.html?utm_source=chatgpt.com "1985 Mazda 323 1.6i LX catalyst Specs Review (63 kW / 86 PS / 84 hp) (since mid-year 1985 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 关闭 4 个 Ktype 的 PENDING：`29967`、`29968`、`29971`、`30058`。
* Transit AWD 厢式车已拆分为 SWB 低/中顶、MWB 中/高顶及 LWB 中/高顶六个物理分支；AWD 底盘车确认对应 MWB 单排分支。相关映射均复用既有尺寸组，不重复输出尺寸事实。
* Transit 2.2 TDCi 前驱底盘车拆分为 MWB 与 EF 两个分支，均复用既有尺寸组。
* Ford Windstar II 首次闭合一个尺寸组；来源明确区分不含后视镜宽度。([Edmunds][1])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：95
* 待处理 Ktype：5
* READY 映射：160
* PENDING 映射：5
* 当前引用尺寸组：74
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29967_swb_lowroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_swb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_mwb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_mwb_highroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_lwb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_lwb_highroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29968	29968	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	AWD单排底盘车MWB物理外廓。	READY
29971_mwb	29971	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	Ktype覆盖前驱单排底盘车的MWB与EF分支。	READY
29971_ef	29971	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	Ktype覆盖前驱单排底盘车的MWB与EF分支。	READY
30058	30058	MPV	Ford Windstar II			EU-FORD-USA-WINDSTAR-II-MPV-01	MEDIUM		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679	Edmunds 2000 Ford Windstar Limited specifications	https://www.edmunds.com/ford/windstar/2000/st-11732/features-specs/
```

## 下一步优先处理

1. 批量关闭 Defender 90、110、130 的软顶、Station Wagon 与 Pickup 分支。
2. 核对 Peugeot Partner B9 Dangel 4×4 的 L1/L2、Van/MPV 外廓。
3. 关闭 Mercedes-Benz Vito 123 W639 的 Compact、Long、Extra-long 车身分支。

推进信号：CONTINUE

[1]: https://www.edmunds.com/ford/windstar/2000/st-11732/features-specs/ "Used 2000 Ford Windstar Limited Specs & Features | Edmunds"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Defender 已依据 2012 年官方车型表拆分为 90 Soft Top、90/110 Station Wagon，以及五种 Pickup 外廓；高度统一采用标准配置基准值 2021 mm，不采用选装轮胎或悬架造成的最大高度。([陆虎媒体中心][1])
* Vito 123 已确认覆盖 Compact、Long 标准顶、Long 高顶和 Extra Long 标准顶四种厢式车外廓；尺寸采用同代 Mercedes-Benz 技术规格，并以 Vito 123 车型目录确认对应分支。
* Partner B9 4×4 已确认 Tepee 4×4、L1 Van 与 L2 Van 存在不同高度记录，但当前 Ktype 对 L1/L2 的覆盖边界及 1834、1865、1988 mm 高度口径尚未闭合，因此保留唯一 PENDING，不创建猜测性尺寸组。([Ultimate Specs][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：99
* 待处理 Ktype：1
* READY 映射：172
* PENDING 映射：1
* 已确认尺寸组：86
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29982_90_softtop	29982	Convertible	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SOFTTOP-01	MEDIUM	90 Soft Top物理外廓。	READY
29983_90	29983	SUV	Defender L316	L316	3	EU-LAND-ROVER-DEFENDER-L316-SUV-90-STATION-WAGON-01	MEDIUM	Ktype覆盖90与110 Station Wagon，按轴距拆分。	READY
29983_110	29983	SUV	Defender L316	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-STATION-WAGON-01	MEDIUM	Ktype覆盖90与110 Station Wagon，按轴距拆分。	READY
29984_90	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-90-01	MEDIUM	Ktype覆盖多个轴距及驾驶室/货斗外廓。	READY
29984_110	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-01	MEDIUM	Ktype覆盖多个轴距及驾驶室/货斗外廓。	READY
29984_110_hcpu	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-HCPU-01	MEDIUM	110 High Capacity Pick Up外廓。	READY
29984_110_dcpu	29984	Pickup	Defender L316	L316	4	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-DCPU-01	MEDIUM	110 Double Cab Pick Up外廓。	READY
29984_130_dchcpu	29984	Pickup	Defender L316	L316	4	EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-DCHCPU-01	MEDIUM	130 Double Cab High Capacity Pick Up外廓。	READY
30023	30023	Van	Peugeot Partner II	B9			LOW	已确认Tepee 4x4、L1 Van和L2 Van存在不同外廓，但当前Ktype覆盖边界及高度口径尚未闭合。	PENDING: L1/L2与Van/MPV分支高度冲突
30127_compact	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-STANDARDROOF-01	HIGH	Ktype覆盖Compact、Long、Long高顶及Extra Long外廓。	READY
30127_long	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-STANDARDROOF-01	HIGH	Ktype覆盖Compact、Long、Long高顶及Extra Long外廓。	READY
30127_long_highroof	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶物理外廓。	READY
30127_extralong	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-STANDARDROOF-01	HIGH	Extra Long标准顶物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SOFTTOP-01	3894	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-SUV-90-STATION-WAGON-01	3894	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-SUV-110-STATION-WAGON-01	4785	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-90-01	3649	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-01	4370	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-HCPU-01	4631	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-DCPU-01	4438	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-DCHCPU-01	5170	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-STANDARDROOF-01	4748	1901	1902	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-STANDARDROOF-01	4993	1901	1902	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-STANDARDROOF-01	5223	1901	1900	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
```

## 下一步优先处理

只处理 `30023`：确认该 Ktype 是否同时覆盖 Partner B9 Dangel 4×4 的 L1 Van、L2 Van和 Tepee，并分别闭合三个高度口径；关闭后立即输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://media.landrover.com/en/tech-specs "Land Rover Media Centre"
[2]: https://www.ultimatespecs.com/car-specs/Peugeot/26394/Peugeot-Partner-2-Tepee-Extreme-HDi-90-4x4.html?utm_source=chatgpt.com "Peugeot Partner 2 Tepee Extreme HDi 90 4x4 Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后一个 `Ktype=30023` 已关闭，拆分为 Dangel 4×4 的 L1 厢式车、L2 厢式车和 Tepee 乘用车三个物理外廓。Dangel 资料确认 L1/L2 车身和 90 hp 商用/乘用版本；厢式车高度按标准车身高度加官方 60 mm 抬升量闭合，Tepee 使用直接规格记录。
* 已补齐所有映射引用的既有及本批新建尺寸组。
* 机械检查通过：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、100 个输入 Ktype 全覆盖、映射引用闭合、三维与来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：175
* PENDING 映射：0
* DIMENSION_GROUP：98
* 唯一映射 id：175
* 所有映射均为 `READY`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
29885	29885	Sedan	Saab 9-5 I Facelift 2005	YS3E	4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH		READY
29890	29890	Coupe	Lotus Esprit X180		2	EU-LOTUS-ESPRIT-X180-COUPE-2D-01	MEDIUM	功率与生产期对应X180时期Esprit；输入S4标签不作为代际依据。	READY
29891	29891	Coupe	Lotus Esprit X180		2	EU-LOTUS-ESPRIT-X180-COUPE-2D-01	MEDIUM	功率与生产期对应X180时期Esprit；输入S4标签不作为代际依据。	READY
29910	29910	Convertible	Lotus Elise S2	111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	HIGH		READY
29913	29913	Sedan	Saab 9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH		READY
29914_3dr	29914	Hatchback	MG ZR	RF	3	EU-MG-ZR-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29914_5dr	29914	Hatchback	MG ZR	RF	5	EU-MG-ZR-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29917_prefl	29917	MPV	Renault Grand Scenic II Phase I		5	EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	HIGH	生产期跨Phase I与Phase II，拆分改款前外廓。	READY
29917_facelift	29917	MPV	Renault Grand Scenic II Phase II		5	EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	生产期跨Phase I与Phase II，拆分改款后外廓。	READY
29919	29919	Wagon	Saab 9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH		READY
29923	29923	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29924_prefl	29924	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29924_facelift	29924	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29925	29925	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29926	29926	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29927	29927	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH		READY
29928_prefl	29928	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29928_facelift	29928	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29929_prefl	29929	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29929_facelift	29929	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29930	29930	Hatchback	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH		READY
29932_prefl	29932	Wagon	Opel Insignia A Pre-facelift	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29932_facelift	29932	Wagon	Opel Insignia A Facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29943	29943	Convertible	BMW 1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
29944	29944	Convertible	BMW 1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
29945_swb	29945	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH	VariantName同时包含i与Li，拆分短轴车身。	READY
29945_lwb	29945	Sedan	BMW 7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	HIGH	VariantName同时包含i与Li，拆分长轴车身。	READY
29946_swb	29946	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH	VariantName同时包含i与Li，拆分短轴车身。	READY
29946_lwb	29946	Sedan	BMW 7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	HIGH	VariantName同时包含i与Li，拆分长轴车身。	READY
29947	29947	Sedan	BMW 7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH		READY
29948	29948	MPV	Renault Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
29949	29949	MPV	Renault Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
29950_prefl	29950	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29950_facelift	29950	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29951_prefl	29951	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29951_facelift	29951	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29952_prefl	29952	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29952_facelift	29952	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29953_prefl	29953	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29953_facelift	29953	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29954_prefl	29954	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29954_facelift	29954	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29956_prefl	29956	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29956_facelift	29956	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29957_prefl	29957	Hatchback	Renault Megane III Phase I		5	EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	HIGH	生产期跨改款，改款前外廓。	READY
29957_facelift	29957	Hatchback	Renault Megane III Phase II-III		5	EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	HIGH	Phase II与Phase III三维一致，合并同一物理分支。	READY
29958_prefl	29958	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29958_facelift1	29958	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29958_facelift2	29958	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29959_prefl	29959	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29959_facelift1	29959	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29959_facelift2	29959	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29960_prefl	29960	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29960_facelift1	29960	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29960_facelift2	29960	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29961_prefl	29961	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29961_facelift1	29961	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29961_facelift2	29961	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29962_prefl	29962	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29962_facelift1	29962	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29962_facelift2	29962	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29963_prefl	29963	Coupe	Renault Megane III Coupe Phase I		3	EU-RENAULT-MEGANE-III-COUPE-PREFL-01	HIGH	生产期跨三阶段外廓，改款前分支。	READY
29963_facelift1	29963	Coupe	Renault Megane III Coupe Phase II		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	HIGH	生产期跨三阶段外廓，第一次改款分支。	READY
29963_facelift2	29963	Coupe	Renault Megane III Coupe Phase III		3	EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	HIGH	生产期跨三阶段外廓，第二次改款分支。	READY
29964	29964	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29965	29965	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29966	29966	Coupe	Renault Laguna III Coupe		2	EU-RENAULT-LAGUNA-III-COUPE-2D-01	HIGH		READY
29967_swb_lowroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_swb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_mwb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_mwb_highroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_lwb_medroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29967_lwb_highroof	29967	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖AWD厢式车的轴距与车顶物理分支。	READY
29968	29968	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	AWD单排底盘车MWB物理外廓。	READY
29969_swb_lowroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_swb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_lowroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_mwb_highroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_lwb_medroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29969_lwb_highroof	29969	Van	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖前驱厢式车的轴距与车顶物理分支。	READY
29970_mwb_medroof	29970	MPV	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	MEDIUM	前驱Bus按中轴和长轴中顶外廓拆分。	READY
29970_lwb_medroof	29970	MPV	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	MEDIUM	前驱Bus按中轴和长轴中顶外廓拆分。	READY
29971_mwb	29971	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	Ktype覆盖前驱单排底盘车的MWB与EF分支。	READY
29971_ef	29971	Pickup	Ford Transit Mk7			EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	Ktype覆盖前驱单排底盘车的MWB与EF分支。	READY
29972	29972	MPV	Ford Transit Mk7 Tourneo			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH		READY
29973	29973	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29974_prefl	29974	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29974_facelift	29974	Coupe	Audi A5 8T Facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29975_prefl	29975	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29975_facelift	29975	Coupe	Audi A5 8T Facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29976	29976	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29977	29977	Coupe	Audi A5 8T Pre-facelift	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH		READY
29978	29978	Convertible	Audi A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH		READY
29979	29979	Sedan	Hyundai Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
29980	29980	Sedan	Hyundai Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
29982_90_softtop	29982	Convertible	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SOFTTOP-01	MEDIUM	90 Soft Top物理外廓。	READY
29983_90	29983	SUV	Defender L316	L316	3	EU-LAND-ROVER-DEFENDER-L316-SUV-90-STATION-WAGON-01	MEDIUM	Ktype覆盖90与110 Station Wagon，按轴距拆分。	READY
29983_110	29983	SUV	Defender L316	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-STATION-WAGON-01	MEDIUM	Ktype覆盖90与110 Station Wagon，按轴距拆分。	READY
29984_90	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-90-01	MEDIUM	Ktype覆盖多个轴距及驾驶室/货斗外廓。	READY
29984_110	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-01	MEDIUM	Ktype覆盖多个轴距及驾驶室/货斗外廓。	READY
29984_110_hcpu	29984	Pickup	Defender L316	L316	2	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-HCPU-01	MEDIUM	110 High Capacity Pick Up外廓。	READY
29984_110_dcpu	29984	Pickup	Defender L316	L316	4	EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-DCPU-01	MEDIUM	110 Double Cab Pick Up外廓。	READY
29984_130_dchcpu	29984	Pickup	Defender L316	L316	4	EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-DCHCPU-01	MEDIUM	130 Double Cab High Capacity Pick Up外廓。	READY
29985	29985	SUV	Nissan Murano II	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-5D-01	HIGH	改款前后已核对为同一三维，复用同一尺寸组。	READY
29986	29986	Hatchback	Alfa Romeo MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH		READY
29987	29987	Wagon	Renault Clio III Grandtour		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
29988_3dr_prefl	29988	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_5dr_prefl	29988	Hatchback	Renault Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_3dr_facelift	29988	Hatchback	Renault Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29988_5dr_facelift	29988	Hatchback	Renault Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
29989_swb	29989	MPV	Renault Modus I Phase II		5	EU-RENAULT-MODUS-I-PHASE-II-MPV-SWB-5D-01	HIGH	输入Model覆盖标准版与Grand，按轴距外廓拆分。	READY
29989_lwb	29989	MPV	Renault Grand Modus I Phase II		5	EU-RENAULT-GRAND-MODUS-I-PHASE-II-MPV-LWB-5D-01	HIGH	输入Model覆盖标准版与Grand，按轴距外廓拆分。	READY
29990_3dr	29990	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29990_5dr	29990	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29991_3dr	29991	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29991_5dr	29991	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29992_3dr	29992	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29992_5dr	29992	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29993_3dr	29993	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29993_5dr	29993	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29994_3dr	29994	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29994_5dr	29994	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29995_3dr	29995	Hatchback	Volkswagen Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29995_5dr	29995	Hatchback	Volkswagen Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门车身，按门数拆分。	READY
29996_prefl	29996	SUV	Volkswagen Tiguan 5N Pre-facelift	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29996_facelift	29996	SUV	Volkswagen Tiguan 5N Facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29997_prefl	29997	SUV	Volkswagen Tiguan 5N Pre-facelift	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
29997_facelift	29997	SUV	Volkswagen Tiguan 5N Facelift	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
29998	29998	Hatchback	Renault Clio II			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH		READY
29999	29999	Sedan	Renault Thalia I Facelift		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	HIGH		READY
30000	30000	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
30001_prefl	30001	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30001_facelift	30001	Sedan	Audi A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30002_prefl	30002	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30002_facelift	30002	Sedan	Audi A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30003	30003	Sedan	Audi A4 B8 Pre-facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
30004	30004	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30005_prefl	30005	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30005_facelift	30005	Wagon	Audi A4 B8 Avant Facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30006_prefl	30006	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	生产期跨改款，拆分改款前外廓。	READY
30006_facelift	30006	Wagon	Audi A4 B8 Avant Facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	生产期跨改款，拆分改款后外廓。	READY
30007	30007	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30008	30008	Wagon	Audi A4 B8 Avant Pre-facelift	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
30017	30017	Sedan	Mitsubishi Lancer Evolution I	CD9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-I-CD9A-SEDAN-4D-01	HIGH		READY
30023_van_l1	30023	Van	Peugeot Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L1-01	MEDIUM	Ktype覆盖4×4 Dangel的L1厢式车、L2厢式车及Tepee乘用车外廓。	READY
30023_van_l2	30023	Van	Peugeot Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L2-01	MEDIUM	Ktype覆盖4×4 Dangel的L1厢式车、L2厢式车及Tepee乘用车外廓。	READY
30023_tepee	30023	MPV	Peugeot Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-MPV-5D-01	MEDIUM	Ktype覆盖4×4 Dangel的L1厢式车、L2厢式车及Tepee乘用车外廓。	READY
30052	30052	Coupe	Jaguar XK8 X100	X100	2	EU-JAGUAR-XK8-X100-COUPE-2D-01	HIGH		READY
30053	30053	Convertible	Jaguar XK8 X100	X100	2	EU-JAGUAR-XK8-X100-CONVERTIBLE-2D-01	HIGH		READY
30057	30057	Convertible	Ford Mustang IV New Edge	SN95	2	EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	HIGH		READY
30058	30058	MPV	Ford Windstar II			EU-FORD-USA-WINDSTAR-II-MPV-01	MEDIUM		READY
30068	30068	SUV	Ford Explorer II		5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	HIGH		READY
30073_3dr	30073	Hatchback	Mazda 323 III	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	HIGH	Ktype覆盖三门与五门掀背车身。	READY
30073_5dr	30073	Hatchback	Mazda 323 III	BF	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	HIGH	Ktype覆盖三门与五门掀背车身。	READY
30094	30094	SUV	Nissan Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
30102	30102	SUV	Suzuki Grand Vitara I XL-7	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	HIGH	2.7版本对应XL-7长车身。	READY
30106	30106	Coupe	Cadillac Eldorado XII		2	EU-CADILLAC-ELDORADO-XII-COUPE-2D-01	HIGH		READY
30111_prefl	30111	Sedan	Subaru Impreza II Pre-facelift	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	HIGH	生产期跨三种前后外廓，拆分初期车型。	READY
30111_facelift1	30111	Sedan	Subaru Impreza II Facelift 1	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	HIGH	生产期跨三种前后外廓，拆分第一次改款。	READY
30111_facelift2	30111	Sedan	Subaru Impreza II Facelift 2	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH	生产期跨三种前后外廓，拆分第二次改款。	READY
30118	30118	Hatchback	Renault Megane II Phase II RS		3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	高功率RS为三门外形。	READY
30126_prefl	30126	SUV	Toyota 4Runner III Pre-facelift	N180	5	EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-PREFL-01	MEDIUM	输入Model“4”按2.7后驱及生产期确认4Runner III；生产期跨外廓变更。	READY
30126_facelift	30126	SUV	Toyota 4Runner III Facelift	N180	5	EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-FACELIFT-01	MEDIUM	输入Model“4”按2.7后驱及生产期确认4Runner III；生产期跨外廓变更。	READY
30127_compact	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-STANDARDROOF-01	HIGH	Ktype覆盖Compact、Long、Long高顶及Extra Long外廓。	READY
30127_long	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-STANDARDROOF-01	HIGH	Ktype覆盖Compact、Long、Long高顶及Extra Long外廓。	READY
30127_long_highroof	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶物理外廓。	READY
30127_extralong	30127	Van	Mercedes-Benz Vito W639	W639	4	EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-STANDARDROOF-01	HIGH	Extra Long标准顶物理外廓。	READY
30128	30128	Convertible	Saab 9-3 II Pre-facelift	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH		READY
30129	30129	MPV	Fiat Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
30141_3dr_prefl	30141	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_5dr_prefl	30141	Hatchback	Renault Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_3dr_facelift	30141	Hatchback	Renault Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30141_5dr_facelift	30141	Hatchback	Renault Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖三门/五门外形，拆分物理分支。	READY
30143	30143	SUV	SsangYong Actyon I	CJ	5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3201-3300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data.net Saab 9-5 facelift 2005	https://www.auto-data.net/en/saab-9-5-facelift-2005-generation-8066
EU-LOTUS-ESPRIT-X180-COUPE-2D-01	4330	1860	1150	Auto-Data.net Lotus Esprit 2.2 Turbo 231 Hp;Auto-Data.net Lotus Esprit 2.2 Turbo 218 Hp	https://www.auto-data.net/en/lotus-esprit-2.2-i-turbo-231hp-8302;https://www.auto-data.net/en/lotus-esprit-2.2-turbo-218hp-8304
EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	3785	1719	1143	Auto-Data.net Lotus Elise Series 2	https://www.auto-data.net/en/lotus-elise-series-2-generation-1829
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450	Auto-Data.net Saab 9-3 Sedan II facelift 2007	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-2.8t-v6-280hp-11923
EU-MG-ZR-HATCHBACK-3D-01	4011	1690	1400	Auto-Data.net MG ZR 2.0 TDi 113 Hp	https://www.auto-data.net/en/mg-zr-2.0-tdi-113hp-14045
EU-MG-ZR-HATCHBACK-5D-01	4011	1690	1400	Auto-Data.net MG ZR 2.0 TDi 113 Hp	https://www.auto-data.net/en/mg-zr-2.0-tdi-113hp-14045
EU-RENAULT-GRAND-SCENIC-II-PHASE-I-MPV-5D-01	4493	1810	1636	Auto-Data.net Renault Grand Scenic II Phase I	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-i-2.0-16v-135hp-39395
EU-RENAULT-GRAND-SCENIC-II-PHASE-II-MPV-5D-01	4496	1810	1636	Auto-Data.net Renault Grand Scenic II Phase II	https://www.auto-data.net/en/renault-grand-scenic-ii-phase-ii-generation-7616
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496	Auto-Data.net Saab 9-3 Sport Combi II facelift 2007	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-generation-8068
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520	Automobile-Catalog 2009 Opel Insignia Sports Tourer 2.0 CDTI 160	https://www.automobile-catalog.com/car/2009/2535425/opel_insignia_sports_tourer_2_0_cdti_160.html
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513	Auto-Data.net Opel Insignia Sports Tourer A facelift 2013	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-facelift-2013-generation-4216
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498	Auto-Data.net Opel Insignia Hatchback A	https://www.auto-data.net/en/opel-insignia-hatchback-a-generation-492
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411	Auto-Data.net BMW 1 Series Convertible E88 118d	https://www.auto-data.net/en/bmw-1-series-convertible-e88-118d-143hp-17236
EU-BMW-7-SERIES-F01-SEDAN-SWB-01	5072	1902	1479	Auto-Data.net BMW 7 Series F01 740i	https://www.auto-data.net/en/bmw-7-series-f01-740i-326hp-steptronic-9703
EU-BMW-7-SERIES-F02-SEDAN-LWB-01	5212	1902	1479	Auto-Data.net BMW 7 Series Long F02	https://www.auto-data.net/en/bmw-7-series-long-f02-generation-4308
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data.net Renault Kangoo II 1.5 dCi 103 Hp	https://www.auto-data.net/en/renault-kangoo-ii-1.5-dci-103hp-33901
EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	4295	1808	1491	Auto-Data.net Renault Megane III	https://www.auto-data.net/en/renault-megane-iii-generation-2145
EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	4295	1808	1471	Auto-Data.net Renault Megane III Phase II;Auto-Data.net Renault Megane III Phase III	https://www.auto-data.net/en/renault-megane-iii-phase-ii-2012-generation-3872;https://www.auto-data.net/en/renault-megane-iii-phase-iii-2014-generation-4123
EU-RENAULT-MEGANE-III-COUPE-PREFL-01	4299	1804	1435	Auto-Data.net Renault Megane III Coupe	https://www.auto-data.net/en/renault-megane-iii-coupe-generation-2146
EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	4299	1785	1423	Auto-Data.net Renault Megane III Coupe Phase II	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-ii-2012-generation-3875
EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	4299	1848	1435	Auto-Data.net Renault Megane III Coupe Phase III	https://www.auto-data.net/en/renault-megane-iii-coupe-phase-iii-2014-generation-4288
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400	Auto-Data.net Renault Laguna Coupe 2.0 dCi 150 Hp	https://www.auto-data.net/en/renault-laguna-coupe-2.0-dci-fap-150hp-10281
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030	Ford Transit Chassis Cab 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070	Ford Transit 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372	Auto-Data.net Audi A5 Coupe 8T3	https://www.auto-data.net/en/audi-a5-coupe-8t3-2.0-tfsi-180hp-multitronic-4510
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372	Auto-Data.net Audi A5 Coupe 8T3 facelift 2011	https://www.auto-data.net/en/audi-a5-coupe-8t3-facelift-2011-generation-4152
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391	Auto-Data.net Audi A4 Cabriolet B7 8H	https://www.auto-data.net/en/audi-a4-cabriolet-b7-8h-generation-1083
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475	Auto-Data.net Hyundai Sonata V NF facelift 2008	https://www.auto-data.net/en/hyundai-sonata-v-nf-facelift-2008-2.0-165hp-29529
EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SOFTTOP-01	3894	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-SUV-90-STATION-WAGON-01	3894	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-SUV-110-STATION-WAGON-01	4785	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-90-01	3649	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-01	4370	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-HCPU-01	4631	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-110-DCPU-01	4438	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-LAND-ROVER-DEFENDER-L316-PICKUP-130-DCHCPU-01	5170	1790	2021	Land Rover Defender 2012 official brochure;CarsGuide Land Rover Defender 2012 dimensions	https://www.xr793.com/wp-content/uploads/2019/02/2012-Land-Rover-Defender.pdf;https://www.carsguide.com.au/land-rover/defender/car-dimensions/2012
EU-NISSAN-MURANO-II-Z51-SUV-5D-01	4860	1885	1720	Auto-Data.net Nissan Murano II Z51;Auto-Data.net Nissan Murano II Z51 facelift	https://www.auto-data.net/en/nissan-murano-ii-z51-3.5-256hp-17037;https://www.auto-data.net/en/nissan-murano-ii-z51-facelift-2010-3.5-v6-249hp-4wd-cvt-24767
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440	Auto-Data.net Alfa Romeo MiTo 1.4 MPI	https://www.auto-data.net/en/alfa-romeo-mito-1.4-mpi-78hp-16682
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497	Auto-Data.net Renault Clio III Grandtour Phase I	https://www.auto-data.net/fr/renault-clio-iii-grandtour-phase-i-generation-11030
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495	Auto-Data.net Renault Clio III Phase I 3-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-generation-2130
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495	Auto-Data.net Renault Clio III Phase I 5-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-generation-11029
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497	Auto-Data.net Renault Clio III Phase II 3-door	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-generation-5024
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497	Auto-Data.net Renault Clio III Phase II 5-door	https://www.auto-data.net/fr/renault-clio-iii-phase-ii-2009-5-door-generation-11031
EU-RENAULT-MODUS-I-PHASE-II-MPV-SWB-5D-01	3874	1709	1589	Auto-Data.net Renault Modus Phase II	https://www.auto-data.net/en/renault-modus-phase-ii-generation-5554
EU-RENAULT-GRAND-MODUS-I-PHASE-II-MPV-LWB-5D-01	4034	1709	1589	Auto-Data.net Renault Grand Modus Phase II 1.2 16V	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-16v-75hp-29949
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479	Auto-Data.net Volkswagen Golf VI 3-door	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-1.4-tsi-122hp-8595
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480	Auto-Data.net Volkswagen Golf VI 5-door	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-1.6-102hp-41256
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data.net Volkswagen Tiguan I	https://www.auto-data.net/en/volkswagen-tiguan-i-generation-1849
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data.net Volkswagen Tiguan I facelift 2011	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-generation-3790
EU-RENAULT-CLIO-II-HATCHBACK-01	3773	1639	1417	Auto-Data.net Renault Clio II Phase II	https://www.auto-data.net/en/renault-clio-ii-phase-ii-2001-3-door-generation-9000
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437	Auto-Data.net Renault Symbol I facelift 2002	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-generation-2168
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Auto-Data.net Audi A4 B8 8K	https://www.auto-data.net/en/audi-a4-b8-8k-generation-1084
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Auto-Data.net Audi A4 B8 8K facelift 2011	https://www.auto-data.net/en/audi-a4-b8-8k-facelift-2011-generation-4133
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data.net Audi A4 Avant B8 8K	https://www.auto-data.net/en/audi-a4-avant-b8-8k-2.0-tdi-143hp-4330
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data.net Audi A4 Avant B8 facelift 2011	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-generation-4134
EU-MITSUBISHI-LANCER-EVOLUTION-I-CD9A-SEDAN-4D-01	4310	1695	1395	Automobile-Catalog 1992 Mitsubishi Lancer GSR Evolution	https://www.automobile-catalog.com/car/1992/1950440/mitsubishi_lancer_gsr_evolution.html
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L1-01	4380	1810	1894	Peugeot Partner official handbook;Peugeot Partner 4x4 Dangel official press dossier	https://www.manualslib.com/manual/1288694/Peugeot-Partner-2016.html;https://www.avto.info/f/docs/Obvestila/dosje_press.Peugeot_Partner_4x4_Dangel_LOWRES.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L2-01	4628	1810	1894	Peugeot Partner official handbook;Peugeot Partner 4x4 Dangel official press dossier	https://www.manualslib.com/manual/1288694/Peugeot-Partner-2016.html;https://www.avto.info/f/docs/Obvestila/dosje_press.Peugeot_Partner_4x4_Dangel_LOWRES.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-MPV-5D-01	4380	1810	1865	UltimateSpecs Peugeot Partner 2 Tepee Extreme HDi 90 4x4	https://www.ultimatespecs.com/car-specs/Peugeot/26394/Peugeot-Partner-2-Tepee-Extreme-HDi-90-4x4.html
EU-JAGUAR-XK8-X100-COUPE-2D-01	4760	1829	1306	Auto-Data.net Jaguar XK Coupe X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x100-4.0-v8-284hp-automatic-240
EU-JAGUAR-XK8-X100-CONVERTIBLE-2D-01	4760	1829	1306	Auto-Data.net Jaguar XK Convertible X100	https://www.auto-data.net/en/jaguar-xk-convertible-x100-generation-68
EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	4653	1857	1351	Auto-Data.net Ford Mustang Convertible IV 3.8 V6	https://www.auto-data.net/en/ford-mustang-convertible-iv-3.8-v6-190hp-7779
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679	Edmunds 2000 Ford Windstar Limited specifications	https://www.edmunds.com/ford/windstar/2000/st-11732/features-specs/
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4790	1790	1800	Auto-Data.net Ford Explorer II 4.0 XLT 4WD	https://www.auto-data.net/en/ford-explorer-ii-4.0-xlt-4wd-208hp-7872
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6i LX 3-door	https://www.automobile-catalog.com/car/1986/1630055/mazda_323_1_6i_lx_cat.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6i GLX 5-door	https://www.automobile-catalog.com/car/1986/1630040/mazda_323_1_6i_glx_cat.html
EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	4530	1840	1750	Auto-Data.net Nissan Pathfinder II 3.3 V6 4WD	https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930
EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	4760	1780	1740	Automobile-Catalog 2004 Suzuki Grand Vitara XL-7 2.7 V6	https://www.automobile-catalog.com/car/2004/3353120/suzuki_grand_vitara_xl-7_2_7_v6.html
EU-CADILLAC-ELDORADO-XII-COUPE-2D-01	5136	1918	1370	Auto-Data.net Cadillac Eldorado XII	https://www.auto-data.net/en/cadillac-eldorado-xii-generation-2483
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440	Auto-Data.net Subaru Impreza II	https://www.auto-data.net/en/subaru-impreza-ii-generation-3590
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440	Auto-Data.net Subaru Impreza II facelift 2002	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2002-generation-8239
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440	Auto-Data.net Subaru Impreza II facelift 2005	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2005-generation-8240
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458	Auto-Data.net Renault Megane II Phase II 3-door	https://www.auto-data.net/en/renault-megane-ii-phase-ii-3-door-generation-7614
EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-PREFL-01	4540	1690	1690	AutoDetective 1996 Toyota 4Runner 2WD	https://www.autodetective.com/directory/1996/toyota/4runner/trim/2wd/
EU-TOYOTA-4RUNNER-III-N180-SUV-RWD-FACELIFT-01	4656	1689	1715	Edmunds 2000 Toyota 4Runner Base specifications	https://www.edmunds.com/toyota/4runner/2000/st-11110/features-specs/
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-STANDARDROOF-01	4748	1901	1902	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-STANDARDROOF-01	4993	1901	1902	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-STANDARDROOF-01	5223	1901	1900	Mercedes-Benz Vito Van and Crew Cab 2008 technical data;AutoScout24 Mercedes-Benz Vito 123 specifications	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/vito/vito-123-13990/
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data.net Saab 9-3 Convertible II	https://www.auto-data.net/en/saab-9-3-convertible-ii-generation-2539
EU-FIAT-IDEA-MPV-350-01	3930	1698	1660	Auto-Data.net Fiat Idea	https://www.auto-data.net/en/fiat-idea-generation-1603
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740	Auto-Data.net SsangYong Actyon	https://www.auto-data.net/en/ssangyong-actyon-generation-3564
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3201-3300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3201-3300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3201-3300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3958 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1916 行）

