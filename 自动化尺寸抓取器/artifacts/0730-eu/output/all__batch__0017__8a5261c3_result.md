# 任务：all 第 1601-1700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0017__8a5261c3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1601-1700 行

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
all 第 1601-1700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-BENTLEY-CONTINENTAL-GT-II-V8S-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	4570	1800	1440
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	4569	1801	1435
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655
EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	4165	1801	1565
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457
EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	4955	1880	1496
EU-JEEP-CHEROKEE-XJ-SUV-5D-01	4200	1720	1621
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	4370	1900	1609
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	4370	1900	1635
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	4304	1706	1459
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515
EU-VW-POLO-III-6N1-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Crossland x /	1.6 Turbo D	SUV	Frontantrieb	Diesel	85	116	Aug 2017	Apr 2019	2025-02-03	128186
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	110	150	Jun 2017	-	2024-03-01	128188
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	132	180	Mar 2017	-	2024-03-01	128189
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Jun 2017	-	2024-03-01	128190
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	110	150	Jun 2017	-	2024-03-01	128191
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	140	190	Jun 2017	Jul 2021	2024-03-01	128192
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	176	240	Jun 2017	Sep 2020	2024-03-01	128193
VW	Polo	1	Schrägheck	Frontantrieb	Benzin	55	75	Jun 2017	Aug 2021	2024-03-01	128213
VW	Polo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Jun 2017	-	2024-03-01	128214
VW	Polo	1	Schrägheck	Frontantrieb	Benzin	48	65	Aug 2017	Feb 2020	2024-03-01	128215
Chevrolet	Aveo / kalos	1.5	Stufenheck	Frontantrieb	Benzin	63	86	Oct 2004	May 2006	2024-03-01	128219
Land Rover	Range rover evoque	2.0 4X4	SUV	Allrad	Benzin	177	241	Aug 2017	Dec 2019	2024-03-01	128221
Chevrolet	Rezzo	1.6	Großraumlimousine	Frontantrieb	Benzin	66	90	Mar 2005	Mar 2009	2024-03-01	128228
Land Rover	Range rover evoque	2.0 4X4	Cabriolet	Allrad	Benzin	177	241	Aug 2017	Dec 2019	2024-03-01	128231
KIA	Stinger	2.0 T-gdi	Schrägheck	Heckantrieb	Benzin	188	256	Jun 2017	Dec 2023	2026-04-01	128232
KIA	Stinger	3.3 T-gdi	Schrägheck	Heckantrieb	Benzin	272	370	Jun 2017	Dec 2023	2026-04-01	128235
Hyundai	Ix35	2.0 Cvvt 4WD	SUV	Allrad	Benzin	110	150	Aug 2013	Dec 2015	2024-03-01	128236
Honda	Pilot	3.5 4WD	SUV	Allrad	Benzin	189	257	Jan 2010	Jun 2015	2024-03-01	128257
KIA	Stinger	3.3 T-gdi 4WD	Schrägheck	Allrad	Benzin	272	370	Jun 2017	Dec 2023	2026-04-01	128259
Hyundai	Elantra vi	1.6	Stufenheck	Frontantrieb	Benzin	94	128	Feb 2016	Dec 2020	2024-05-01	128261
Seat	Arona	1.0 TSI	SUV	Frontantrieb	Benzin	70	95	Jul 2017	-	2024-03-01	128275
Seat	Arona	1.0 TSI	SUV	Frontantrieb	Benzin	85	116	Jul 2017	-	2025-06-01	128277
Seat	Arona	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2017	-	2024-03-01	128278
Seat	Arona	1.6 TDI	SUV	Frontantrieb	Diesel	85	115	Jul 2017	-	2024-03-01	128280
Skoda	Karoq	1.0 TSI	SUV	Frontantrieb	Benzin	85	116	Jul 2017	-	2025-06-01	128286
Skoda	Karoq	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2017	-	2024-03-01	128287
Skoda	Karoq	1.6 TDI	SUV	Frontantrieb	Diesel	85	115	Jul 2017	-	2024-03-01	128288
Skoda	Karoq	2.0 TDI 4X4	SUV	Allrad	Diesel	110	150	Jul 2017	-	2024-03-01	128289
Hyundai	I30	1.4 MPI	Kombi	Frontantrieb	Benzin	74	101	Mar 2017	Dec 2020	2024-07-01	128291
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	130	177	Jun 2017	Mar 2023	2024-03-01	128292
Hyundai	Kona	1.0 T-gdi	SUV	Frontantrieb	Benzin	88	120	Jul 2017	Apr 2023	2024-05-01	128293
Audi	Q5	3.0 TDI Quattro	SUV	Allrad	Diesel	210	286	Jul 2017	Nov 2020	2024-03-01	128294
VW	Golf sportsvan vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	63	86	May 2017	Jul 2019	2024-03-01	128298
VW	Golf sportsvan vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	May 2017	Jul 2018	2024-03-01	128299
VW	Golf sportsvan vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	May 2017	Aug 2020	2024-03-01	128300
VW	Golf sportsvan vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	130	May 2017	Aug 2020	2024-03-01	128301
Jeep	Cherokee	3.2 4X4	SUV	Allrad	Benzin	202	275	Jan 2014	-	2024-03-01	128303
Seat	Ibiza v	1.0 MPI	Schrägheck	Frontantrieb	Benzin	48	65	Jul 2017	-	2025-12-01	128304
Seat	Ibiza v	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2017	-	2024-03-01	128305
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	221	300	Jun 2017	-	2024-03-01	128315
VW	Golf vii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	96	130	Jul 2017	Aug 2020	2024-03-01	128340
VW	Golf vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	130	May 2017	Aug 2020	2024-03-01	128344
Mazda	Mx-5 rf	1.5	Targa	Heckantrieb	Benzin	96	131	Aug 2017	-	2024-03-01	128357
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	336	457	Sep 2017	-	2024-03-01	128375
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	336	457	Sep 2017	-	2024-03-01	128377
Renault	Megane iv grandtour	1.6 TCE 165	Kombi	Frontantrieb	Benzin	121	165	Jul 2017	-	2024-03-01	128394
Skoda	Octavia	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Feb 2017	Oct 2020	2024-03-01	128418
Skoda	Octavia	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Feb 2017	Oct 2020	2024-03-01	128420
Lotus	Evora	3.5 430	Coupe	Heckantrieb	Benzin	321	436	Jun 2017	-	2024-03-01	128430
Mercedes-benz	E-Klasse	E 350 D 4-matic	Cabriolet	Allrad	Diesel	190	258	Jun 2017	-	2024-03-01	128437
Audi	A5	2.0 TDI	Cabriolet	Frontantrieb	Diesel	110	150	Aug 2017	Dec 2019	2024-03-01	128451
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	May 2017	Feb 2020	2024-05-01	128454
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	446	607	Jun 2017	May 2020	2024-03-01	128457
BMW	I3	S Electric	Schrägheck	Heckantrieb	Elektro	135	184	Nov 2017	-	2024-03-01	128458
BMW	I3	S Range Extender	Schrägheck	Heckantrieb	Benzin/Elektro	135	184	Nov 2017	-	2024-03-01	128459
BMW	I3	S Electric	Schrägheck	Heckantrieb	Elektro	75	102	Nov 2017	-	2026-06-01	128460
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	270	367	Jul 2017	Jul 2020	2024-03-01	128462
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	270	367	Jul 2017	Jul 2020	2024-03-01	128463
Mercedes-benz	S-Klasse	S 500 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	320	435	Jul 2017	Jul 2020	2024-03-01	128464
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Jun 2017	Dec 2019	2024-03-01	128465
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2017	Dec 2019	2024-03-01	128467
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Jun 2017	Dec 2019	2024-03-01	128469
Skoda	Rapid	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2017	Dec 2019	2024-03-01	128470
Skoda	Karoq	2.0 TDI 4X4	SUV	Allrad	Diesel	140	190	Jul 2017	-	2024-03-01	128471
Renault	Megane iv	1.6 TCE 165	Schrägheck	Frontantrieb	Benzin	121	165	Jul 2017	-	2024-03-01	128472
Renault	Kangoo	1.5 DCI 90	Großraumlimousine	Frontantrieb	Diesel	67	91	Aug 2017	-	2024-03-01	128473
Saab	9-3	2.8 Turbo V6	Stufenheck	Frontantrieb	Benzin	206	280	May 2008	Dec 2010	2024-03-01	128488
Saab	9-3	2.8 Turbo V6	Kombi	Frontantrieb	Benzin	206	280	May 2008	Dec 2010	2024-03-01	128489
Mini	Mini	Cooper SD	Cabriolet	Frontantrieb	Diesel	100	136	Jan 2011	May 2015	2024-03-01	128490
Renault	Kangoo	1.6 16V LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	78	106	Dec 2008	-	2024-03-01	128491
Renault	Megane cc	1.6 16V Hi-flex	Cabriolet	Frontantrieb	Benzin/Ethanol	81	110	Jun 2010	Aug 2015	2024-03-01	128492
VW	T-Roc	2.0 TSI 4motion	SUV	Allrad	Benzin	140	190	Jul 2017	-	2024-03-01	128493
Ford	Mondeo iv	2.0 Scti	Stufenheck	Frontantrieb	Benzin	149	203	Mar 2010	Jan 2015	2024-03-01	128494
VW	T-Roc	1.0 TSI	SUV	Frontantrieb	Benzin	85	116	Jul 2017	-	2025-06-01	128495
Ford	Mondeo iv	1.6 TI	Stufenheck	Frontantrieb	Benzin	88	120	Mar 2010	Jan 2015	2024-03-01	128496
KIA	Stinger	2.2 Crdi VGT	Schrägheck	Heckantrieb	Diesel	147	200	Jun 2017	Dec 2023	2026-04-01	128498
KIA	Stinger	2.2 Crdi VGT 4WD	Schrägheck	Allrad	Diesel	147	200	Jun 2017	Dec 2023	2026-04-01	128499
Alpina	D5	S Allrad	Stufenheck	Allrad	Diesel	285	388	Jul 2017	Jun 2020	2024-03-01	128500
Volvo	S40 i	1.8 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	90	122	Mar 1999	Dec 2004	2024-03-01	128501
Opel	Zafira	1.8 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	103	140	Jul 2009	Apr 2015	2024-03-01	128502
Volvo	V40	1.8 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	90	122	Mar 1999	Jun 2004	2024-03-01	128503
Volvo	V50	1.6 D	Kombi	Frontantrieb	Diesel	80	109	Mar 2005	Dec 2012	2024-03-01	128504
Alpina	D5	S Allrad	Kombi	Allrad	Diesel	285	388	Jul 2017	Jun 2020	2024-03-01	128505
KIA	Stonic	1.2 Cvvt	Schrägheck	Frontantrieb	Benzin	62	84	Jul 2017	Dec 2025	2026-03-01	128506
KIA	Stonic	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	73	99	Jul 2017	Dec 2025	2026-03-01	128507
KIA	Stonic	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	88	120	Jul 2017	Dec 2025	2026-07-01	128508
KIA	Stonic	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	81	110	Jul 2017	Dec 2025	2026-03-01	128510
VW	Atlas	3.6 FSI 4motion	SUV	Allrad	Benzin	206	280	Dec 2016	-	2024-03-01	128511
Mercedes-benz	S-Klasse	S 450 CDI	Stufenheck	Heckantrieb	Diesel	235	320	Jan 2009	Dec 2013	2024-03-01	128514
KIA	Picanto iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	100	Mar 2017	-	2024-03-01	128519
Ford	Ka+ iii	1.2	Stufenheck	Frontantrieb	Benzin	63	85	Jun 2016	Dec 2020	2026-04-01	128525
Mercedes-benz	M-Klasse	ML 320 CDI 4-matic	SUV	Allrad	Diesel	155	211	Jul 2005	Jul 2011	2024-03-01	128534
Mercedes-benz	Sprinter 4,6-T	413 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	95	129	Jun 2006	Dec 2016	2024-03-01	128563
Jaguar	Xf sportbrake	3.0 AWD	Kombi	Allrad	Benzin	280	380	Jul 2017	-	2024-03-01	128567
Jaguar	Xf sportbrake	3	Kombi	Heckantrieb	Benzin	280	380	Jul 2017	-	2024-03-01	128568
Bentley	Continental	6.0 W12 AWD	Coupe	Allrad	Benzin	467	635	Sep 2017	-	2024-03-01	128569
Jaguar	Xj	5.0 Scv8 R575	Stufenheck	Heckantrieb	Benzin	423	575	Jun 2017	Dec 2019	2025-02-03	128571
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	220	299	Oct 1998	Dec 2003	2024-03-01	128572
Renault	Megane iv	1.6 SCE	Stufenheck	Frontantrieb	Benzin	84	115	Oct 2016	-	2024-03-01	128574
Renault	Megane iv	1.2 TCE 130	Stufenheck	Frontantrieb	Benzin	97	130	Oct 2016	-	2024-03-01	128575


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 51 个 Ktype 映射，其中 38 条关联跨批次既有尺寸组。
* 首次创建 4 个尺寸组：SEAT Arona、Škoda Karoq 前驱、Škoda Karoq 四驱、KIA Stinger。
* Karoq 官方技术资料明确区分前驱高度 1603 mm 与四驱高度 1607 mm；Arona 与 Stinger 三维来自对应官方技术资料，Stinger 宽度口径为不含后视镜。([mundoseat.seat.com][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：51
* PENDING 映射：49
* 当前已引用尺寸组：27
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128186	128186	SUV	Crossland X I	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
128188	128188	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH	前驱外廓高度分支。	READY
128189	128189	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128190	128190	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH	前驱外廓高度分支。	READY
128191	128191	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128192	128192	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128193	128193	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128221	128221	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	HIGH		READY
128231	128231	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	HIGH	两门敞篷物理外廓。	READY
128232	128232	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128235	128235	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128236	128236	SUV	ix35 I	LM	5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	HIGH		READY
128259	128259	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128261	128261	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	HIGH	标准车身外廓。	READY
128275	128275	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128277	128277	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128278	128278	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128280	128280	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128286	128286	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128287	128287	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128288	128288	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128289	128289	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	HIGH	4×4外廓高度分支。	READY
128291	128291	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
128292	128292	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128293	128293	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128294	128294	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
128298	128298	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128299	128299	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128300	128300	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128301	128301	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128304	128304	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
128305	128305	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
128315	128315	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
128340	128340	Wagon	Golf VII	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
128344	128344	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH	五门掀背物理外廓。	READY
128418	128418	Hatchback	Octavia III	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH		READY
128420	128420	Wagon	Octavia III	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
128451	128451	Convertible	A5 II	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	两门敞篷物理外廓。	READY
128454	128454	Hatchback	A5 II	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	五门Sportback物理外廓。	READY
128465	128465	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128467	128467	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128469	128469	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128470	128470	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128471	128471	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	HIGH	4×4外廓高度分支。	READY
128494	128494	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
128496	128496	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
128498	128498	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128499	128499	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128519	128519	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
128567	128567	Wagon	XF II Sportbrake	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH	Sportbrake物理外廓。	READY
128568	128568	Wagon	XF II Sportbrake	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH	Sportbrake物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official technical specifications	https://www.seat-cupra-mediacenter.com/content/dam/seat-media-center/Documents/2017/TS%20New%20SEAT%20Arona_EN.pdf
EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	4382	1841	1603	ŠKODA KAROQ official technical specifications (11 October 2017)	https://cdn.skoda-storyboard.com/2017/10/TD-KAROQ-en-1.pdf
EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	4382	1841	1607	ŠKODA KAROQ official technical specifications (11 October 2017)	https://cdn.skoda-storyboard.com/2017/10/TD-KAROQ-en-1.pdf
EU-KIA-STINGER-I-CK-HATCHBACK-01	4830	1870	1400	Kia Stinger Geneva 2017 official press material	https://press.kia.com/content/dam/kiapress/EU/download-files/Geneva-2017/Geneva-Kia-Stinger-Final-6-March.doc
```

## 下一步优先处理

1. 批量闭合 VW Polo VI、Chevrolet Aveo/Rezzo、SEAT/Škoda 之外的普通单一车身组。
2. 核对 F-150 的 SuperCab/SuperCrew 分支，以及 Sprinter 4.6-T 的轴距、驾驶室和底盘分支。
3. 核对 S-Klasse、Jaguar XJ R575 的短轴/长轴边界。
4. 继续处理 BMW i3s、T-Roc、Mazda MX-5 RF、Lotus Evora、Porsche 911 Turbo S 等未建组车型。

推进信号：CONTINUE

[1]: https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/global_site/img/Models/Arona/GD2/TS_New_SEAT_Arona_EN.pdf?utm_source=chatgpt.com "SEAT Arona"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 20 个输入 Ktype，共新增 21 条 READY 映射；`128504` 因 Volvo V50 改款前后外廓变化拆分为 `prefl` 和 `facelift` 两条派生映射。改款前后尺寸分别为 4514×1770×1452 mm 与 4522×1770×1457 mm。([汽车数据网][1])
* 首次创建 12 个尺寸组，覆盖 Polo VI、Kalos/Aveo T200 Sedan、BMW i3s、Mercedes-Benz E-Class A238、Saab 9-3 Sedan/SportCombi、Megane III CC、T-Roc、Volvo V50 改款前后、Ford Ka+ 和 Megane IV Sedan。([volkswagen-newsroom.com][2])
* Saab 9-3 Sedan 与 SportCombi 已按不同车身外廓分别建组；T-Roc 的前驱和四驱 Ktype 本轮确认共用相同外廓尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：71
* READY 映射行：72
* PENDING Ktype：29
* 当前已引用尺寸组：39
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128213	128213	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128214	128214	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128215	128215	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128219	128219	Sedan	Kalos/Aveo T200	T200	4	EU-CHEVROLET-KALOS-AVEO-T200-SEDAN-01	MEDIUM	T200四门轿车物理外廓。	READY
128394	128394	Wagon	Megane IV	K9A	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH		READY
128437	128437	Convertible	E-Class V	A238	2	EU-MERCEDES-BENZ-E-CLASS-V-A238-CONVERTIBLE-01	HIGH	A238双门敞篷物理外廓。	READY
128458	128458	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128459	128459	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128460	128460	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128472	128472	Hatchback	Megane IV	B9A	5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
128488	128488	Sedan	9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-01	HIGH		READY
128489	128489	Wagon	9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-SPORTCOMBI-WAGON-01	HIGH	SportCombi物理外廓。	READY
128490	128490	Convertible	MINI Convertible II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH		READY
128492	128492	Convertible	Megane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	HIGH	双门硬顶敞篷物理外廓。	READY
128493	128493	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
128495	128495	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
128504_prefl	128504	Wagon	V50 I	MW	5	EU-VOLVO-V50-I-MW-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
128504_facelift	128504	Wagon	V50 I Facelift	MW	5	EU-VOLVO-V50-I-MW-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
128525	128525	Hatchback	Ka+ III	B562	5	EU-FORD-KA-PLUS-III-B562-HATCHBACK-01	HIGH	输入为Stufenheck，车型资料确认五门掀背外廓。	READY
128574	128574	Sedan	Megane IV	L9A	4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH	四门Grand Coupé物理外廓。	READY
128575	128575	Sedan	Megane IV	L9A	4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH	四门Grand Coupé物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-VI-AW1-HATCHBACK-01	4053	1751	1446	Volkswagen Newsroom – Expressively designed compact car	https://www.volkswagen-newsroom.com/en/the-new-polo-driving-presentation-2574/expressively-designed-compact-car-2595
EU-CHEVROLET-KALOS-AVEO-T200-SEDAN-01	4235	1670	1495	Automobile-Catalog 2004 Daewoo Kalos 1.5 LK	https://www.automobile-catalog.com/car/2004/1349780/daewoo_kalos_1_5_lk.html
EU-MERCEDES-BENZ-E-CLASS-V-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-350d-258hp-4matic-9g-tronic-31747
EU-BMW-I3-I01-HATCHBACK-S-01	4006	1791	1570	BMW Group official BMW i3 and BMW i3s specifications	https://www.press.bmwgroup.com/global/article/attachment/T0280411EN/406749/The_new_BMW_i3_LCI_BMW_i3s_Specifications.pdf
EU-SAAB-9-3-II-FACELIFT-SEDAN-01	4647	1762	1450	Auto-Data Saab 9-3 Sedan II Facelift 2.8T V6	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-2.8t-v6-280hp-11923
EU-SAAB-9-3-II-FACELIFT-SPORTCOMBI-WAGON-01	4670	1762	1496	Auto-Data Saab 9-3 Sport Combi II Facelift 2.8T V6	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-2.8t-v6-280hp-42457
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	Auto-Data Renault Megane III CC 1.6 16V	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392
EU-VW-T-ROC-I-A11-SUV-01	4234	1819	1573	Auto-Data Volkswagen T-Roc I 2.0 TSI 4MOTION; Auto-Data Volkswagen T-Roc I 1.0 TSI	https://www.auto-data.net/en/volkswagen-t-roc-2.0-tsi-190hp-4motion-dsg-31218;https://www.auto-data.net/en/volkswagen-t-roc-i-1.0-tsi-116hp-31216
EU-VOLVO-V50-I-MW-WAGON-PREFL-01	4514	1770	1452	Auto-Data Volvo V50 1.6 D	https://www.auto-data.net/en/volvo-v50-1.6-d-110hp-9575
EU-VOLVO-V50-I-MW-WAGON-FACELIFT-01	4522	1770	1457	Auto-Data Volvo V50 Facelift 1.6 D DRIVe	https://www.auto-data.net/en/volvo-v50-facelift-2007-1.6-d-drive-109hp-17176
EU-FORD-KA-PLUS-III-B562-HATCHBACK-01	3929	1695	1524	Auto-Data Ford Ka+ 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-1.2-ti-vct-85hp-25181
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443	Auto-Data Renault Megane IV Sedan 1.6 SCe	https://www.auto-data.net/en/renault-megane-iv-sedan-1.6-sce-115hp-26377
```

## 下一步优先处理

1. 优先闭合 Chevrolet Rezzo、Volvo S40/V40、Opel Zafira B、Mercedes-Benz ML W164 等单一或可明确拆分的历史车身。
2. 核对 F-150 Raptor 两个 Ktype 分别对应的 SuperCab/SuperCrew 分支，禁止在驾驶室边界未确认前猜测关联。
3. 处理 S-Class、Jaguar XJ、Sprinter 4.6-T 等短轴/长轴或底盘分支。
4. 最后处理 Honda Pilot、Jeep Cherokee、Kangoo 与 Stonic 等存在配置高度或车身分支冲突的记录。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-v50-1.6-d-110hp-9575?utm_source=chatgpt.com "Volvo V50 1.6 D (110 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.volkswagen-newsroom.com/en/the-new-polo-driving-presentation-2574/expressively-designed-compact-car-2595 "Expressively designed compact car | Volkswagen Newsroom"
[3]: https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-2.8t-v6-280hp-11923?utm_source=chatgpt.com "Saab 9-3 Sedan II (facelift 2007) 2.8T V6 (280 Hp)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **16 个 READY 映射**，首次创建 **13 个 DIMENSION_GROUP**；已闭合 Rezzo、MX-5 RF、Evora GT430、911 Turbo S Exclusive、Kangoo II、Alpina D5 S、Zafira B、Stonic、Atlas、M-Class W164 和 Continental GT III。关键尺寸由车型直接规格页、Porsche 产品资料、ALPINA 官方手册和 Kia 官方技术资料闭合。([汽车数据网][1])
* Kangoo 改款前后分别建立尺寸组；Stonic 的 4 个发动机 Ktype 共用一个物理外廓组；Alpina D5 S Sedan 与 Touring 按不同车身分别建组，官方资料记录两者三维均为 4956×1868×1466 mm。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：87
* READY 映射行：88
* PENDING Ktype：13
* 当前已引用尺寸组：52
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128228	128228	MPV	Rezzo I	U100	5	EU-CHEVROLET-REZZO-I-U100-MPV-01	HIGH		READY
128357	128357	Targa	MX-5 IV RF	ND	2	EU-MAZDA-MX-5-IV-ND-RF-TARGA-01	HIGH	RF可伸缩硬顶物理外廓。	READY
128430	128430	Coupe	Evora I GT430	122	2	EU-LOTUS-EVORA-I-TYPE-122-GT430-COUPE-01	HIGH	GT430专用空气动力外廓。	READY
128457	128457	Coupe	911 VII Facelift	991	2	EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	HIGH	991.2 Turbo S Exclusive Series宽体外廓。	READY
128473	128473	MPV	Kangoo II Facelift	K61	5	EU-RENAULT-KANGOO-II-K61-MPV-FACELIFT-01	HIGH	标准轴距乘用版改款外廓。	READY
128491	128491	MPV	Kangoo II	K61	5	EU-RENAULT-KANGOO-II-K61-MPV-PREFL-01	HIGH	标准轴距乘用版改款前外廓。	READY
128500	128500	Sedan	D5 S	G30	4	EU-ALPINA-D5-S-G30-SEDAN-01	HIGH	四门Limousine物理外廓。	READY
128502	128502	MPV	Zafira B Facelift	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH		READY
128505	128505	Wagon	D5 S	G31	5	EU-ALPINA-D5-S-G31-WAGON-01	HIGH	Touring物理外廓。	READY
128506	128506	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128507	128507	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128508	128508	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128510	128510	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128511	128511	SUV	Atlas I	CA1	5	EU-VW-ATLAS-I-CA1-SUV-4MOTION-PREFL-01	HIGH	4Motion改款前物理外廓。	READY
128534	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-01	HIGH		READY
128569	128569	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	HIGH	第三代W12双门物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-REZZO-I-U100-MPV-01	4350	1755	1580	Auto-Data Chevrolet Rezzo 1.6 i 16V	https://www.auto-data.net/en/chevrolet-rezzo-1.6-i-16v-105hp-14444
EU-MAZDA-MX-5-IV-ND-RF-TARGA-01	3915	1735	1230	Auto-Data Mazda MX-5 IV RF 1.5 SkyActiv-G	https://www.auto-data.net/en/mazda-mx-5-iv-rf-1.5-skyactiv-g-131hp-32714
EU-LOTUS-EVORA-I-TYPE-122-GT430-COUPE-01	4396	1845	1229	Auto-Data Lotus Evora GT430	https://www.auto-data.net/en/lotus-evora-gt430-generation-5676
EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	4507	1880	1297	Porsche 911 Turbo S Exclusive Series product brochure	https://autocatalogarchive.com/wp-content/uploads/2019/08/Porsche-911-Turbo-S-Exclusive-Series-2017-UK.pdf
EU-RENAULT-KANGOO-II-K61-MPV-FACELIFT-01	4282	1829	1839	Auto-Data Renault Kangoo II Facelift 1.5 dCi 90	https://www.auto-data.net/en/renault-kangoo-ii-facelift-2013-1.5-dci-90hp-19782
EU-RENAULT-KANGOO-II-K61-MPV-PREFL-01	4213	1829	1839	Auto-Data Renault Kangoo II passenger body	https://www.auto-data.net/en/renault-kangoo-ii-1.6-8v-87hp-33903
EU-ALPINA-D5-S-G30-SEDAN-01	4956	1868	1466	BMW ALPINA D5 S Allrad official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/D5_S/epaper/ausgabe.pdf
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635	AutoData24 Opel Zafira B 1.8 i 16V	https://autodata24.com/opel/zafira/zafira-b/18-i-16v-140-hp/details
EU-ALPINA-D5-S-G31-WAGON-01	4956	1868	1466	BMW ALPINA D5 S Allrad official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/D5_S/epaper/ausgabe.pdf
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Kia Stonic official 2017 technical specifications	https://press.kia.com/content/dam/kiapress/EU/PressPhotos/Europe/IAA2017/Worddocument/Kia%20Stonic.doc
EU-VW-ATLAS-I-CA1-SUV-4MOTION-PREFL-01	5037	1989	1778	Car and Driver 2018 Volkswagen Atlas specifications	https://www.caranddriver.com/volkswagen/atlas/specs/2018/volkswagen_atlas_volkswagen-atlas_2018
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-01	4780	1911	1815	Auto-Data Mercedes-Benz M-Class W164 ML 320 CDI	https://www.auto-data.net/en/mercedes-benz-m-class-w164-ml-320-cdi-v6-224hp-4matic-7g-tronic-12759
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	4850	1954	1405	Automobile-Catalog 2018 Bentley Continental GT W12	https://www.automobile-catalog.com/car/2018/2606630/bentley_continental_gt.html
```

## 下一步优先处理

1. 核对并拆分 Mercedes-Benz S-Class W220、W221、W222 的短轴与长轴物理分支。
2. 确认两个 F-150 Raptor Ktype 分别对应 SuperCab 或 SuperCrew。
3. 处理 Volvo S40/V40 跨改款外廓，以及 Jaguar XJR575 的 SWB/LWB 分支。
4. 最后闭合 Honda Pilot 配置高度、Jeep Cherokee KL 标准版/Trailhawk 和 Sprinter 4.6-T 多轴距驾驶室分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/chevrolet-rezzo-1.6-i-16v-105hp-14444?utm_source=chatgpt.com "Chevrolet Rezzo 1.6 i 16V (105 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-kangoo-ii-facelift-2013-1.5-dci-90hp-19782?utm_source=chatgpt.com "Renault Kangoo II (facelift 2013) 1.5 dCi (90 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 9 个 Ktype，新增 16 条 READY 映射。Honda Pilot 因 2012 款前脸改款造成长度变化拆分为改款前、改款后；Jeep Cherokee 3.2 4×4 拆分为标准 AWD 与 Trailhawk 外廓。([本田新闻][1])
* `128375` 已确认对应 F-150 Raptor SuperCab，`128377` 对应 SuperCrew；两者尺寸按 2017 Ford F-150 规格表分别闭合。([Auto Doc][2])
* Mercedes-Benz W222/V222、W221/V221 已依据 Ktype 所含明确车身代码拆分短轴和长轴；Jaguar XJR575 按官方资料拆分 SWB/LWB。([meyermotoren.de][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：96
* READY 映射行：104
* PENDING Ktype：4
* 当前已引用尺寸组：64
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128257_prefl	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-YF4-SUV-PREFL-01	HIGH	2010-2011改款前4WD物理外廓。	READY
128257_facelift	128257	SUV	Pilot II Facelift	YF4	5	EU-HONDA-PILOT-II-YF4-SUV-FACELIFT-01	HIGH	2012-2015改款后4WD物理外廓。	READY
128303_standard	128303	SUV	Cherokee V	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	Longitude/Limited标准3.2 AWD外廓。	READY
128303_trailhawk	128303	SUV	Cherokee V	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk专用悬架及保险杠外廓。	READY
128375	128375	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCAB-01	HIGH	Extended Cab/SuperCab物理外廓。	READY
128377	128377	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCREW-01	HIGH	Crew Cab/SuperCrew物理外廓。	READY
128462_swb	128462	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.058短轴外廓。	READY
128462_lwb	128462	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.158长轴外廓。	READY
128463_swb	128463	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.059短轴外廓。	READY
128463_lwb	128463	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.159长轴外廓。	READY
128464_swb	128464	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.060短轴外廓。	READY
128464_lwb	128464	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.160长轴外廓。	READY
128514_swb	128514	Sedan	S-Class V Facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	车身代码221.028短轴外廓。	READY
128514_lwb	128514	Sedan	S-Class V Facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	车身代码221.128长轴外廓。	READY
128571_swb	128571	Sedan	XJ X351 Facelift	X351	4	EU-JAGUAR-XJ-X351-XJR575-SEDAN-SWB-01	MEDIUM	XJR575标准轴距物理外廓。	READY
128571_lwb	128571	Sedan	XJ X351 Facelift	X351	4	EU-JAGUAR-XJ-X351-XJR575-SEDAN-LWB-01	MEDIUM	XJR575长轴距物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-PILOT-II-YF4-SUV-PREFL-01	4849	1994	1847	Honda News – 2010 Honda Pilot Features and Specifications	https://hondanews.com/en-US/honda-automobiles/releases/release-5d7679a29f2311d6f31025004c34bb67-2010-honda-pilot-features-and-specifications
EU-HONDA-PILOT-II-YF4-SUV-FACELIFT-01	4862	1994	1847	Honda News – 2012 Honda Pilot Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-4509ac20f72a429d892191934c064ecc-2012-honda-pilot-specifications-and-features
EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	4624	1859	1634	Jeep Australia MY17 Cherokee Buyer’s Guide	https://tools.jeep.com.au/brochures/model-specs-cherokee.pdf
EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	4626	1904	1686	Jeep Australia MY17 Cherokee Buyer’s Guide	https://tools.jeep.com.au/brochures/model-specs-cherokee.pdf
EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCAB-01	5588	2192	1994	Ford 2017 F-150 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/03/Ford-F-150-2017-CA.pdf
EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCREW-01	5890	2192	1994	Ford 2017 F-150 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/03/Ford-F-150-2017-CA.pdf
EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	5141	1905	1498	Auto-Data Mercedes-Benz S-Class W222 Facelift S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-450-367hp-eq-boost-g-tronic-30764
EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	5271	1905	1496	Auto-Data Mercedes-Benz S-Class Long V222 Facelift S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-facelift-2017-s-450-367hp-eq-boost-g-tronic-31736
EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-Class W221 Facelift S 450 CDI	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-450-cdi-v8-320hp-g-tronic-36906
EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data Mercedes-Benz S-Class Long V221 Facelift S 450 CDI	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-450-cdi-v8-320hp-g-tronic-36900
EU-JAGUAR-XJ-X351-XJR575-SEDAN-SWB-01	5130	1899	1460	Jaguar XJ 18MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XJ_18MY_MB_V4a-GB-EN_DX.pdf
EU-JAGUAR-XJ-X351-XJR575-SEDAN-LWB-01	5255	1899	1460	Jaguar XJ 18MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XJ_18MY_MB_V4a-GB-EN_DX.pdf
```

## 下一步优先处理

1. 闭合 `128501` Volvo S40 I 与 `128503` Volvo V40 的改款前、改款后尺寸边界。
2. 拆分 `128572` Mercedes-Benz S 500 的 W220、V220、facelift 及 `220.875` Pullman 外廓。
3. 最后处理 `128563` Sprinter 4.6-T B906 的单排/双排驾驶室及多轴距底盘分支。

推进信号：CONTINUE

[1]: https://hondanews.com/en-US/honda-automobiles/releases/release-5d7679a29f2311d6f31025004c34bb67-2010-honda-pilot-features-and-specifications?utm_source=chatgpt.com "2010 Honda Pilot Features and Specifications"
[2]: https://www.auto-doc.ie/car-parts/air-conditioning/ford-usa/f-150/f-150-extended-cab-pickup/128375-3-5-4wd?srsltid=AfmBOoqNZh2wAmUjDry6f5X76gsvvadrk01bpY-rSeWCfs6ojrz7YbZO&utm_source=chatgpt.com "Air conditioning FORD USA F-150 XIII (P552) Extended Cab ..."
[3]: https://www.meyermotoren.de/en/fahrzeuge/128462/mercedes-benz/s-class_w222_v222_x222_/s_450_eq_boost_222_158_222_058_128462?utm_source=chatgpt.com "S 450 EQ Boost (222.158, 222.058) | S-Klasse (W222, V222, X222) | Mercedes-Benz | Manufacturers | Meyer Motoren"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 4 个 Ktype：Volvo S40/V40 按 Phase II 改款前后拆分；Sprinter 4.6-T 按单排/双排驾驶室和 3665/4325 mm 轴距拆分；S 500 按 W220 短轴、V220 长轴、改款前后及 Pullman 分支拆分。([catalogonuevo.icerbrakes.com][1])
* 已完成轻量机械收尾：固定表头正确，117 个 `id` 唯一，80 个 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，尺寸和来源字段均非空。
* 当前批次 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：117
* PENDING 映射：0
* DIMENSION_GROUP：80
* 引用闭合检查：通过
* 最终状态：已完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128186	128186	SUV	Crossland X I	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
128188	128188	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH	前驱外廓高度分支。	READY
128189	128189	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128190	128190	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH	前驱外廓高度分支。	READY
128191	128191	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128192	128192	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128193	128193	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH	4Motion外廓高度分支。	READY
128213	128213	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128214	128214	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128215	128215	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-HATCHBACK-01	HIGH		READY
128219	128219	Sedan	Kalos/Aveo T200	T200	4	EU-CHEVROLET-KALOS-AVEO-T200-SEDAN-01	MEDIUM	T200四门轿车物理外廓。	READY
128221	128221	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	HIGH		READY
128228	128228	MPV	Rezzo I	U100	5	EU-CHEVROLET-REZZO-I-U100-MPV-01	HIGH		READY
128231	128231	Convertible	Range Rover Evoque I	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	HIGH	两门敞篷物理外廓。	READY
128232	128232	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128235	128235	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128236	128236	SUV	ix35 I	LM	5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	HIGH		READY
128257_prefl	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-YF4-SUV-PREFL-01	HIGH	2010-2011改款前4WD物理外廓。	READY
128257_facelift	128257	SUV	Pilot II Facelift	YF4	5	EU-HONDA-PILOT-II-YF4-SUV-FACELIFT-01	HIGH	2012-2015改款后4WD物理外廓。	READY
128259	128259	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128261	128261	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	HIGH	标准车身外廓。	READY
128275	128275	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128277	128277	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128278	128278	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128280	128280	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128286	128286	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128287	128287	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128288	128288	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH	前驱外廓高度分支。	READY
128289	128289	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	HIGH	4×4外廓高度分支。	READY
128291	128291	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
128292	128292	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128293	128293	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128294	128294	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
128298	128298	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128299	128299	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128300	128300	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128301	128301	Hatchback	Golf VII Sportsvan	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	HIGH		READY
128303_standard	128303	SUV	Cherokee V	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	Longitude/Limited标准3.2 AWD外廓。	READY
128303_trailhawk	128303	SUV	Cherokee V	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk专用悬架及保险杠外廓。	READY
128304	128304	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
128305	128305	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
128315	128315	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
128340	128340	Wagon	Golf VII	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
128344	128344	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH	五门掀背物理外廓。	READY
128357	128357	Targa	MX-5 IV RF	ND	2	EU-MAZDA-MX-5-IV-ND-RF-TARGA-01	HIGH	RF可伸缩硬顶物理外廓。	READY
128375	128375	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCAB-01	HIGH	Extended Cab/SuperCab物理外廓。	READY
128377	128377	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCREW-01	HIGH	Crew Cab/SuperCrew物理外廓。	READY
128394	128394	Wagon	Megane IV	K9A	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH		READY
128418	128418	Hatchback	Octavia III	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH		READY
128420	128420	Wagon	Octavia III	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
128430	128430	Coupe	Evora I GT430	122	2	EU-LOTUS-EVORA-I-TYPE-122-GT430-COUPE-01	HIGH	GT430专用空气动力外廓。	READY
128437	128437	Convertible	E-Class V	A238	2	EU-MERCEDES-BENZ-E-CLASS-V-A238-CONVERTIBLE-01	HIGH	A238双门敞篷物理外廓。	READY
128451	128451	Convertible	A5 II	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	两门敞篷物理外廓。	READY
128454	128454	Hatchback	A5 II	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	五门Sportback物理外廓。	READY
128457	128457	Coupe	911 VII Facelift	991	2	EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	HIGH	991.2 Turbo S Exclusive Series宽体外廓。	READY
128458	128458	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128459	128459	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128460	128460	Hatchback	i3 I	I01	5	EU-BMW-I3-I01-HATCHBACK-S-01	HIGH	i3s运动外廓。	READY
128462_swb	128462	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.058短轴外廓。	READY
128462_lwb	128462	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.158长轴外廓。	READY
128463_swb	128463	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.059短轴外廓。	READY
128463_lwb	128463	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.159长轴外廓。	READY
128464_swb	128464	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	HIGH	车身代码222.060短轴外廓。	READY
128464_lwb	128464	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	HIGH	车身代码222.160长轴外廓。	READY
128465	128465	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128467	128467	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128469	128469	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128470	128470	Hatchback	Rapid I	NH1	5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	Spaceback物理外廓。	READY
128471	128471	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	HIGH	4×4外廓高度分支。	READY
128472	128472	Hatchback	Megane IV	B9A	5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
128473	128473	MPV	Kangoo II Facelift	K61	5	EU-RENAULT-KANGOO-II-K61-MPV-FACELIFT-01	HIGH	标准轴距乘用版改款外廓。	READY
128488	128488	Sedan	9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-01	HIGH		READY
128489	128489	Wagon	9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-SPORTCOMBI-WAGON-01	HIGH	SportCombi物理外廓。	READY
128490	128490	Convertible	MINI Convertible II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH		READY
128491	128491	MPV	Kangoo II	K61	5	EU-RENAULT-KANGOO-II-K61-MPV-PREFL-01	HIGH	标准轴距乘用版改款前外廓。	READY
128492	128492	Convertible	Megane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	HIGH	双门硬顶敞篷物理外廓。	READY
128493	128493	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
128494	128494	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
128495	128495	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
128496	128496	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
128498	128498	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128499	128499	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-CK-HATCHBACK-01	HIGH		READY
128500	128500	Sedan	D5 S	G30	4	EU-ALPINA-D5-S-G30-SEDAN-01	HIGH	四门Limousine物理外廓。	READY
128501_prefl	128501	Sedan	S40 I	644	4	EU-VOLVO-S40-I-644-SEDAN-PREFL-01	HIGH	2000年Phase II改款前物理外廓。	READY
128501_facelift	128501	Sedan	S40 I Facelift	644	4	EU-VOLVO-S40-I-644-SEDAN-FACELIFT-01	HIGH	2000年Phase II改款后物理外廓。	READY
128502	128502	MPV	Zafira B Facelift	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH		READY
128503_prefl	128503	Wagon	V40 I	645	5	EU-VOLVO-V40-I-645-WAGON-PREFL-01	HIGH	2000年Phase II改款前物理外廓。	READY
128503_facelift	128503	Wagon	V40 I Facelift	645	5	EU-VOLVO-V40-I-645-WAGON-FACELIFT-01	HIGH	2000年Phase II改款后物理外廓。	READY
128504_prefl	128504	Wagon	V50 I	MW	5	EU-VOLVO-V50-I-MW-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
128504_facelift	128504	Wagon	V50 I Facelift	MW	5	EU-VOLVO-V50-I-MW-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
128505	128505	Wagon	D5 S	G31	5	EU-ALPINA-D5-S-G31-WAGON-01	HIGH	Touring物理外廓。	READY
128506	128506	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128507	128507	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128508	128508	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128510	128510	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	输入Schrägheck按厂商跨界SUV车身归类。	READY
128511	128511	SUV	Atlas I	CA1	5	EU-VW-ATLAS-I-CA1-SUV-4MOTION-PREFL-01	HIGH	4Motion改款前物理外廓。	READY
128514_swb	128514	Sedan	S-Class V Facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	车身代码221.028短轴外廓。	READY
128514_lwb	128514	Sedan	S-Class V Facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	车身代码221.128长轴外廓。	READY
128519	128519	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
128525	128525	Hatchback	Ka+ III	B562	5	EU-FORD-KA-PLUS-III-B562-HATCHBACK-01	HIGH	输入为Stufenheck，车型资料确认五门掀背外廓。	READY
128534	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-01	HIGH		READY
128563_singlecab_3665	128563	Pickup	Sprinter II	906.153	2	EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-SINGLE-3665-01	MEDIUM	单排驾驶室、3665 mm轴距底盘外廓。	READY
128563_singlecab_4325	128563	Pickup	Sprinter II	906.155	2	EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-SINGLE-4325-01	MEDIUM	单排驾驶室、4325 mm轴距底盘外廓。	READY
128563_crewcab_3665	128563	Pickup	Sprinter II	906.253	4	EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-CREW-3665-01	MEDIUM	双排驾驶室、3665 mm轴距底盘外廓。	READY
128563_crewcab_4325	128563	Pickup	Sprinter II	906.255	4	EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-CREW-4325-01	MEDIUM	双排驾驶室、4325 mm轴距底盘外廓。	READY
128567	128567	Wagon	XF II Sportbrake	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH	Sportbrake物理外廓。	READY
128568	128568	Wagon	XF II Sportbrake	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH	Sportbrake物理外廓。	READY
128569	128569	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	HIGH	第三代W12双门物理外廓。	READY
128571_swb	128571	Sedan	XJ X351 Facelift	X351	4	EU-JAGUAR-XJ-X351-XJR575-SEDAN-SWB-01	MEDIUM	XJR575标准轴距物理外廓。	READY
128571_lwb	128571	Sedan	XJ X351 Facelift	X351	4	EU-JAGUAR-XJ-X351-XJR575-SEDAN-LWB-01	MEDIUM	XJR575长轴距物理外廓。	READY
128572_swb_prefl	128572	Sedan	S-Class IV	W220	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.075短轴改款前物理外廓。	READY
128572_swb_facelift	128572	Sedan	S-Class IV Facelift	W220	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.075短轴改款后物理外廓。	READY
128572_lwb_prefl	128572	Sedan	S-Class IV	V220	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.175长轴改款前物理外廓。	READY
128572_lwb_facelift	128572	Sedan	S-Class IV Facelift	V220	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.175长轴改款后物理外廓。	READY
128572_pullman	128572	Sedan	S-Class IV Pullman	VV220	4	EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	HIGH	220.875 Pullman加长物理外廓。	READY
128574	128574	Sedan	Megane IV	L9A	4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH	四门Grand Coupé物理外廓。	READY
128575	128575	Sedan	Megane IV	L9A	4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH	四门Grand Coupé物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1601-1700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Auto-Data Opel Crossland X	https://www.auto-data.net/en/opel-crossland-x-generation-5355
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654	ADAC VW Tiguan II 2.0 TDI SCR Trendline	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/vw/tiguan/ii/251707/
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673	ADAC VW Tiguan II 2.0 TDI SCR Highline 4MOTION	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/vw/tiguan/ii/254748/
EU-VW-POLO-VI-AW1-HATCHBACK-01	4053	1751	1446	Volkswagen Newsroom – Expressively designed compact car	https://www.volkswagen-newsroom.com/en/the-new-polo-driving-presentation-2574/expressively-designed-compact-car-2595
EU-CHEVROLET-KALOS-AVEO-T200-SEDAN-01	4235	1670	1495	Automobile-Catalog 2004 Daewoo Kalos 1.5 LK	https://www.automobile-catalog.com/car/2004/1349780/daewoo_kalos_1_5_lk.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	4370	1900	1635	Land Rover Range Rover Evoque 17MY official brochure	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/evoque/LRGL_EVO017_RTR0040_L538_17MY_MB_EURO_FINAL_tcm295-799868.pdf
EU-CHEVROLET-REZZO-I-U100-MPV-01	4350	1755	1580	Auto-Data Chevrolet Rezzo 1.6 i 16V	https://www.auto-data.net/en/chevrolet-rezzo-1.6-i-16v-105hp-14444
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	4370	1900	1609	Land Rover Range Rover Evoque 17MY official brochure	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/evoque/LRGL_EVO017_RTR0040_L538_17MY_MB_EURO_FINAL_tcm295-799868.pdf
EU-KIA-STINGER-I-CK-HATCHBACK-01	4830	1870	1400	Kia Stinger Geneva 2017 official press material	https://press.kia.com/content/dam/kiapress/EU/download-files/Geneva-2017/Geneva-Kia-Stinger-Final-6-March.doc
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655	Auto-Data Hyundai ix35 Facelift 2.0 GDI 4X4	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-2.0-gdi-166hp-4x4-18559
EU-HONDA-PILOT-II-YF4-SUV-PREFL-01	4849	1994	1847	Honda News – 2010 Honda Pilot Features and Specifications	https://hondanews.com/en-US/honda-automobiles/releases/release-5d7679a29f2311d6f31025004c34bb67-2010-honda-pilot-features-and-specifications
EU-HONDA-PILOT-II-YF4-SUV-FACELIFT-01	4862	1994	1847	Honda News – 2012 Honda Pilot Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-4509ac20f72a429d892191934c064ecc-2012-honda-pilot-specifications-and-features
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	4569	1801	1435	Auto-Data Hyundai Elantra VI AD	https://www.auto-data.net/en/hyundai-elantra-vi-ad-2.0-149hp-automatic-32726
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official technical specifications	https://www.seat-cupra-mediacenter.com/content/dam/seat-media-center/Documents/2017/TS%20New%20SEAT%20Arona_EN.pdf
EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	4382	1841	1603	ŠKODA KAROQ official technical specifications (11 October 2017)	https://cdn.skoda-storyboard.com/2017/10/TD-KAROQ-en-1.pdf
EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	4382	1841	1607	ŠKODA KAROQ official technical specifications (11 October 2017)	https://cdn.skoda-storyboard.com/2017/10/TD-KAROQ-en-1.pdf
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Auto-Data Hyundai i30 III CW 1.4	https://www.auto-data.net/en/hyundai-i30-iii-cw-1.4-100hp-30226
EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	4165	1801	1565	Auto-Data Hyundai Kona I	https://www.auto-data.net/en/hyundai-kona-i-2.0-150hp-automatic-32747
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659	Auto-Data Audi Q5 II FY 3.0 TDI quattro	https://www.auto-data.net/en/audi-q5-ii-fy-3.0-tdi-286hp-quattro-tiptronic-31986
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613	ADAC VW Golf Sportsvan 1.5 TSI	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/vw/golf/vii-facelift/309879/
EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	4624	1859	1634	Jeep Australia MY17 Cherokee Buyer’s Guide	https://tools.jeep.com.au/brochures/model-specs-cherokee.pdf
EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	4626	1904	1686	Jeep Australia MY17 Cherokee Buyer’s Guide	https://tools.jeep.com.au/brochures/model-specs-cherokee.pdf
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	SEAT Media Center – New SEAT Ibiza platform and measures	https://www.seat-cupra-mediacenter.com/SEAT-Brand/presskits/newseatibiza/platform-and-measures
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457	Jaguar XF 17MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-X26017-PRT0076_XF_17MY_MB_GEE_FINAL.pdf
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515	Auto-Data Volkswagen Golf VII Variant Facelift 1.5 TSI	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.5-tsi-act-131hp-bluemotion-36013
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Auto-Data Volkswagen Golf VII 5-door Facelift 1.5 TSI	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.5-tsi-act-131hp-35974
EU-MAZDA-MX-5-IV-ND-RF-TARGA-01	3915	1735	1230	Auto-Data Mazda MX-5 IV RF 1.5 SkyActiv-G	https://www.auto-data.net/en/mazda-mx-5-iv-rf-1.5-skyactiv-g-131hp-32714
EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCAB-01	5588	2192	1994	Ford 2017 F-150 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/03/Ford-F-150-2017-CA.pdf
EU-FORD-USA-F150-XIII-P552-RAPTOR-SUPERCREW-01	5890	2192	1994	Ford 2017 F-150 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/03/Ford-F-150-2017-CA.pdf
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449	ADAC Renault Mégane Grandtour ENERGY TCe 130	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/renault/megane/iv/258728/
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Auto-Data Škoda Octavia III Facelift 1.5 TSI	https://www.auto-data.net/en/skoda-octavia-iii-facelift-2017-1.5-tsi-150hp-35790
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Auto-Data Škoda Octavia III Combi Facelift 1.5 TSI	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-1.5-tsi-150hp-35808
EU-LOTUS-EVORA-I-TYPE-122-GT430-COUPE-01	4396	1845	1229	Auto-Data Lotus Evora GT430	https://www.auto-data.net/en/lotus-evora-gt430-generation-5676
EU-MERCEDES-BENZ-E-CLASS-V-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-350d-258hp-4matic-9g-tronic-31747
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	Australian Car.Reviews Audi F5 A5 Cabriolet	https://australiancar.reviews/review-audi-f5-a5-cabriolet-2017-on/
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	ADAC Audi A5 Sportback F5	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a5/f5/295796/
EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	4507	1880	1297	Porsche 911 Turbo S Exclusive Series product brochure	https://autocatalogarchive.com/wp-content/uploads/2019/08/Porsche-911-Turbo-S-Exclusive-Series-2017-UK.pdf
EU-BMW-I3-I01-HATCHBACK-S-01	4006	1791	1570	BMW Group official BMW i3 and BMW i3s specifications	https://www.press.bmwgroup.com/global/article/attachment/T0280411EN/406749/The_new_BMW_i3_LCI_BMW_i3s_Specifications.pdf
EU-MERCEDES-BENZ-S-CLASS-VI-W222-SEDAN-FACELIFT-01	5141	1905	1498	Auto-Data Mercedes-Benz S-Class W222 Facelift S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-450-367hp-eq-boost-g-tronic-30764
EU-MERCEDES-BENZ-S-CLASS-VI-V222-SEDAN-LWB-FACELIFT-01	5271	1905	1496	Auto-Data Mercedes-Benz S-Class Long V222 Facelift S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-facelift-2017-s-450-367hp-eq-boost-g-tronic-31736
EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	4304	1706	1459	ŠKODA RAPID SPACEBACK official technical data	https://cdn.skoda-storyboard.com/2016/05/RAPID-SPACEBACK-en.pdf
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Auto-Data Renault Megane IV 1.2 Energy TCe	https://www.auto-data.net/en/renault-megane-iv-1.2-energy-tce-130hp-22554
EU-RENAULT-KANGOO-II-K61-MPV-FACELIFT-01	4282	1829	1839	Auto-Data Renault Kangoo II Facelift 1.5 dCi 90	https://www.auto-data.net/en/renault-kangoo-ii-facelift-2013-1.5-dci-90hp-19782
EU-SAAB-9-3-II-FACELIFT-SEDAN-01	4647	1762	1450	Auto-Data Saab 9-3 Sedan II Facelift 2.8T V6	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-2.8t-v6-280hp-11923
EU-SAAB-9-3-II-FACELIFT-SPORTCOMBI-WAGON-01	4670	1762	1496	Auto-Data Saab 9-3 Sport Combi II Facelift 2.8T V6	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-2.8t-v6-280hp-42457
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414	Auto-Data MINI Convertible R57 Facelift	https://www.auto-data.net/en/mini-convertible-r57-facelift-2011-generation-4509
EU-RENAULT-KANGOO-II-K61-MPV-PREFL-01	4213	1829	1839	Auto-Data Renault Kangoo II passenger body	https://www.auto-data.net/en/renault-kangoo-ii-1.6-8v-87hp-33903
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	Auto-Data Renault Megane III CC 1.6 16V	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392
EU-VW-T-ROC-I-A11-SUV-01	4234	1819	1573	Auto-Data Volkswagen T-Roc I 2.0 TSI 4MOTION;Auto-Data Volkswagen T-Roc I 1.0 TSI	https://www.auto-data.net/en/volkswagen-t-roc-2.0-tsi-190hp-4motion-dsg-31218;https://www.auto-data.net/en/volkswagen-t-roc-i-1.0-tsi-116hp-31216
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500	Automobile-Catalog 2010 Ford Mondeo Mk IV Phase II Sedan	https://www.automobile-catalog.com/make/ford_europe/mondeo_4gen/mondeo_4gen2_sedan/2010.html
EU-ALPINA-D5-S-G30-SEDAN-01	4956	1868	1466	BMW ALPINA D5 S Allrad official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/D5_S/epaper/ausgabe.pdf
EU-VOLVO-S40-I-644-SEDAN-PREFL-01	4483	1717	1411	Encycarpedia 1999 Volvo S40 1.6	https://www.encycarpedia.com/volvo/99-s40-1-6-saloon
EU-VOLVO-S40-I-644-SEDAN-FACELIFT-01	4516	1716	1422	CarsGuide 2001 Volvo S40 dimensions	https://www.carsguide.com.au/volvo/s40/car-dimensions/2001
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635	AutoData24 Opel Zafira B 1.8 i 16V	https://autodata24.com/opel/zafira/zafira-b/18-i-16v-140-hp/details
EU-VOLVO-V40-I-645-WAGON-PREFL-01	4483	1717	1413	Carfolio 1999 Volvo V40 1.9D	https://www.carfolio.com/volvo-v40-1.9d-283074
EU-VOLVO-V40-I-645-WAGON-FACELIFT-01	4516	1720	1425	Auto-Data Volvo V40 Combi VW generation	https://www.auto-data.net/en/volvo-v40-combi-vw-generation-1967
EU-VOLVO-V50-I-MW-WAGON-PREFL-01	4514	1770	1452	Auto-Data Volvo V50 1.6 D	https://www.auto-data.net/en/volvo-v50-1.6-d-110hp-9575
EU-VOLVO-V50-I-MW-WAGON-FACELIFT-01	4522	1770	1457	Auto-Data Volvo V50 Facelift 1.6 D DRIVe	https://www.auto-data.net/en/volvo-v50-facelift-2007-1.6-d-drive-109hp-17176
EU-ALPINA-D5-S-G31-WAGON-01	4956	1868	1466	BMW ALPINA D5 S Allrad official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/D5_S/epaper/ausgabe.pdf
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Kia Stonic official 2017 technical specifications	https://press.kia.com/content/dam/kiapress/EU/PressPhotos/Europe/IAA2017/Worddocument/Kia%20Stonic.doc
EU-VW-ATLAS-I-CA1-SUV-4MOTION-PREFL-01	5037	1989	1778	Car and Driver 2018 Volkswagen Atlas specifications	https://www.caranddriver.com/volkswagen/atlas/specs/2018/volkswagen_atlas_volkswagen-atlas_2018
EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-Class W221 Facelift S 450 CDI	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-450-cdi-v8-320hp-g-tronic-36906
EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data Mercedes-Benz S-Class Long V221 Facelift S 450 CDI	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-450-cdi-v8-320hp-g-tronic-36900
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485	Kia Picanto 2017 official specification	https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/All-New%20Picanto/Specifications/picanto_2017-specification.pdf
EU-FORD-KA-PLUS-III-B562-HATCHBACK-01	3929	1695	1524	Auto-Data Ford Ka+ 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-1.2-ti-vct-85hp-25181
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-01	4780	1911	1815	Auto-Data Mercedes-Benz M-Class W164 ML 320 CDI	https://www.auto-data.net/en/mercedes-benz-m-class-w164-ml-320-cdi-v6-224hp-4matic-7g-tronic-12759
EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-SINGLE-3665-01	5870	1990	2360	Mercedes-Benz Sprinter Bodybuilder Directives;Mercedes-Benz Sprinter Cab Chassis Spec Sheet (January 2008)	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08
EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-SINGLE-4325-01	6845	1990	2385	Mercedes-Benz Sprinter Bodybuilder Directives;Mercedes-Benz Sprinter Cab Chassis Spec Sheet (January 2008)	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08
EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-CREW-3665-01	5870	1990	2360	Mercedes-Benz Sprinter Bodybuilder Directives;Mercedes-Benz Sprinter Cab Chassis Spec Sheet (January 2008)	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08
EU-MERCEDES-BENZ-SPRINTER-II-B906-PICKUP-CREW-4325-01	6845	1990	2385	Mercedes-Benz Sprinter Bodybuilder Directives;Mercedes-Benz Sprinter Cab Chassis Spec Sheet (January 2008)	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08
EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	4955	1880	1496	Jaguar XF Saloon and Sportbrake official technical specification	https://www.jaguar.com/content/dam/jdx/pdfs/wltp-figures/Jaguar-XF-WLTP-Insert-1X2602300M00WXXEN01P.pdf
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	4850	1954	1405	Automobile-Catalog 2018 Bentley Continental GT W12	https://www.automobile-catalog.com/car/2018/2606630/bentley_continental_gt.html
EU-JAGUAR-XJ-X351-XJR575-SEDAN-SWB-01	5130	1899	1460	Jaguar XJ 18MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XJ_18MY_MB_V4a-GB-EN_DX.pdf
EU-JAGUAR-XJ-X351-XJR575-SEDAN-LWB-01	5255	1899	1460	Jaguar XJ 18MY official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XJ_18MY_MB_V4a-GB-EN_DX.pdf
EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	5038	1855	1444	Mercedes-Benz Public Archive – S 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500.xhtml?oid=4959
EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	5043	1855	1444	Mercedes-Benz Public Archive – S 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500.xhtml?oid=2461756
EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	5158	1855	1444	Mercedes-Benz Public Archive – S 500 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-long-wheelbase.xhtml?oid=4961
EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444	Mercedes-Benz Public Archive – S 500 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-long-wheelbase.xhtml?oid=2461757
EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	6158	1855	1462	Mercedes-Benz Public Archive – S 500 Pullman	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-Pullman.xhtml?oid=4970
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443	Auto-Data Renault Megane IV Sedan 1.6 SCe	https://www.auto-data.net/en/renault-megane-iv-sedan-1.6-sce-115hp-26377
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1601-1700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://catalogonuevo.icerbrakes.com/Vehiculo/Details?idTipoVehiculo=2&idVehiculo=128501&utm_source=chatgpt.com "Vehicle VOLVO - S40 (644) - 1.8 LPG details - Web Catalogo"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1601-1700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1601-1700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1799 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（882 行）

