# 任务：all 第 4701-4800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0048__f687a87a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4701-4800 行

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
all 第 4701-4800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ABARTH-500-312-HATCHBACK-01	3657	1627	1485
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485
EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	4041	1721	1490
EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	4660	1828	1417
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422
EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	4660	1828	1452
EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	4660	1828	1452
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1422
EU-ALFA-ROMEO-159-SEDAN-02	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-01	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	4660	1828	1422
EU-AUDI-R8-I-42-CONVERTIBLE-V10-FACELIFT-01	4440	1929	1244
EU-AUDI-R8-I-42-CONVERTIBLE-V10-PREFL-01	4434	1904	1244
EU-AUDI-R8-I-42-COUPE-V10-FACELIFT-01	4440	1929	1252
EU-AUDI-R8-I-42-COUPE-V10-PREFL-01	4434	1930	1252
EU-AUDI-R8-I-COUPE-V8-PREFL-01	4431	1904	1252
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E30-CONVERTIBLE-2D-01	4325	1645	1370
EU-BMW-3-SERIES-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-BMW-3-SERIES-F30-SEDAN-4D-FACELIFT-01	4633	1811	1429
EU-BMW-3-SERIES-F30-SEDAN-4D-PREFL-01	4624	1811	1429
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	5004	1901	1559
EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	4998	1901	1559
EU-BMW-5-SERIES-F10-SEDAN-LCI-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-X3-E83-SUV-5D-FACELIFT-01	4569	1853	1674
EU-CADILLAC-BLS-SEDAN-01	4680	1752	1471
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543
EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	4515	1725	1445
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535
EU-INFINITI-EX-J50-SUV-5D-01	4630	1800	1575
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680
EU-INFINITI-FX-I-S50-SUV-5D-01	4803	1925	1651
EU-INFINITI-G37-V36-COUPE-2D-01	4655	1824	1395
EU-INFINITI-G37-V36-SEDAN-4D-01	4755	1773	1469
EU-JEEP-CHEROKEE-IV-KK-SUV-5D-01	4493	1839	1797
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700
EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	4785	1870	1710
EU-KIA-CARENS-III-UN-MPV-01	4545	1820	1650
EU-KIA-OPTIMA-III-TF-SEDAN-4D-01	4845	1830	1455
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660
EU-LANCIA-MUSA-I-MPV-PREFL-01	3985	1698	1688
EU-LANCIA-PHEDRA-I-MPV-01	4750	1863	1760
EU-LANCIA-PHEDRA-I-MPV-02	4750	1863	1759
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385
EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-01	5220	1850	1774
EU-NISSAN-NAVARA-D40-KING-CAB-PICKUP-01	5220	1850	1774
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488
EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	4040	1713	1488
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488
EU-PEUGEOT-EXPERT-I-BUS-01	4440	1810	1940
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	5016	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-LWB-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-SWB-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	4805	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	5135	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276
EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	4522	1844	1919
EU-PEUGEOT-EXPERT-I-VAN-01	4440	1810	1940
EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	4782	1928	1699
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	5048	2070	2303
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	5048	2070	2496
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	5548	2070	2749
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	6198	2070	2488
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	6198	2070	2744
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-FACELIFT-01	6225	2070	2549
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	6198	2070	2549
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-FACELIFT-01	6225	2070	2549
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	6198	2070	2527
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-FACELIFT-01	6225	2070	2815
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	6198	2070	2815
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-SRW-FACELIFT-01	6225	2070	2815
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-FACELIFT-01	6875	2070	2557
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	6848	2070	2557
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-FACELIFT-01	6875	2070	2557
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	6848	2070	2527
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-FACELIFT-01	6875	2070	2808
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	6848	2070	2808
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-FACELIFT-01	6875	2070	2808
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	6848	2070	2786
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	4170	1700	1680
EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	4827	1792	1475
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459
EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	5008	1868	1466
EU-SAAB-9-5-PREFL-SEDAN-4D-01	4810	1790	1450
EU-SAAB-9-5-PREFL-WAGON-5D-01	4808	1792	1497
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	4088	1693	1441
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	4061	1693	1445
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	4082	1693	1441
EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	4066	1693	1424
EU-SEAT-IBIZA-IV-SC-CUPRA-HATCHBACK-3D-FACELIFT-01	4055	1693	1420
EU-SEAT-IBIZA-IV-SC-CUPRA-HATCHBACK-3D-PREFL-01	4063	1693	1420
EU-SEAT-IBIZA-IV-SC-FR-HATCHBACK-3D-PREFL-01	4072	1693	1424
EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	4236	1693	1445
EU-SEAT-IBIZA-IV-ST-WAGON-FACELIFT-FR-01	4240	1693	1442
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498
EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	3992	1642	1498
EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	4222	1793	1691
EU-SKODA-YETI-I-5L-SUV-PREFL-01	4223	1793	1691
EU-SSANGYONG-KYRON-DJ-SUV-01	4660	1880	1755
EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	4660	1880	1740
EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	4660	1880	1755
EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	4745	1821	1506
EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	4735	1780	1505
EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	4790	1780	1535
EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	4775	1780	1535
EU-TOYOTA-HIACE-IV-BUS-LWB-01	5240	1800	1995
EU-TOYOTA-HIACE-IV-BUS-SWB-01	4795	1800	2000
EU-TOYOTA-HIACE-IV-H100-VAN-LH102-SWB-01	4615	1690	1935
EU-TOYOTA-HIACE-IV-H100-VAN-LH112-LWB-01	4950	1690	1960
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	4715	1800	1955
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	5160	1800	1955
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-NORACK-01	4689	1826	1679
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-ROOFRACK-01	4689	1826	1735
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1865
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1855
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443
EU-VW-SHARAN-I-7M8-PREFL-MPV-01	4620	1810	1730
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730
EU-VW-SHARAN-II-7N-MPV-5D-01	4854	1904	1720
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Saab	9-5	2.0 T Biopower	Stufenheck	Frontantrieb	Benzin/Ethanol	162	220	May 2010	Jan 2012	2024-03-01	33500
Saab	9-5	2.0 Turbo XWD	Stufenheck	Allrad	Benzin	162	220	May 2010	Jan 2012	2024-03-01	33501
Saab	9-5	2.0 T Biopower XWD	Stufenheck	Allrad	Benzin/Ethanol	162	220	May 2010	Jan 2012	2024-03-01	33502
Saab	9-5	2.8 Turbo V6 XWD	Stufenheck	Allrad	Benzin	221	301	May 2010	Jan 2012	2024-03-01	33503
Saab	9-5	2.0 TID	Stufenheck	Frontantrieb	Diesel	118	160	May 2010	Jan 2012	2024-03-01	33504
KIA	Optima	1.7 Crdi	Stufenheck	Frontantrieb	Diesel	100	136	Mar 2012	Dec 2015	2024-05-01	33510
Toyota	Highlander	3.5	SUV	Frontantrieb	Benzin	201	273	May 2007	Feb 2014	2024-03-01	33532
Toyota	Highlander	3.5 4WD	SUV	Allrad	Benzin	201	273	Jun 2007	Feb 2014	2024-03-01	33534
Nissan	Navara	2.5 DCI 4WD	Pritsche/Fahrgestell	Allrad	Diesel	106	144	Aug 2008	-	2024-03-01	33565
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	115	156	Feb 2007	Dec 2011	2024-03-01	33573
Toyota	Land cruiser prado	3.0 D-4d	Geländewagen geschlossen	Allrad	Diesel	127	173	Aug 2009	-	2024-03-01	33574
Renault	Scénic i	1.9 D	Großraumlimousine	Frontantrieb	Diesel	47	64	Sep 1999	Mar 2001	2024-03-01	33576
Infiniti	Fx	30D AWD	SUV	Allrad	Diesel	175	238	Apr 2010	-	2024-03-01	33582
Infiniti	Ex	30D	SUV	Allrad	Diesel	175	238	Apr 2010	-	2024-03-01	33583
Nissan	Nv200	1.6 16V	Kasten	Frontantrieb	Benzin	81	110	Feb 2010	-	2024-03-01	33584
Nissan	Nv200	1.5 DCI 85	Kasten	Frontantrieb	Diesel	63	86	Feb 2010	-	2024-03-01	33585
Toyota	Land cruiser prado	4.0 V6 Vvti	Geländewagen geschlossen	Allrad	Benzin	183	249	Nov 2012	-	2024-03-01	33586
Nissan	Nv200 / evalia	1.6 16V	Bus	Frontantrieb	Benzin	81	110	Jul 2010	-	2026-01-01	33587
Nissan	Nv200 / evalia	1.5 DCI 85	Bus	Frontantrieb	Diesel	63	86	Jul 2010	-	2026-01-01	33588
Mercedes-benz	E-Klasse	E 250	Stufenheck	Heckantrieb	Benzin	155	211	Jan 2013	Dec 2016	2024-03-01	33590
Lancia	Musa	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	70	95	Mar 2009	Sep 2012	2024-03-01	33592
Lancia	Phedra	2.2 D Multijet	Großraumlimousine	Frontantrieb	Diesel	125	170	Mar 2008	Nov 2010	2024-03-01	33593
Mitsubishi	Lancer viii	2.0 I Ralliart 4WD	Stufenheck	Allrad	Benzin	177	241	Oct 2008	-	2024-03-01	33598
KIA	Carens iii	1.6 Cvvt	Großraumlimousine	Frontantrieb	Benzin	97	132	Aug 2009	Mar 2013	2024-05-01	33606
KIA	Carens iii	2.0 Crdi 135	Großraumlimousine	Frontantrieb	Diesel	100	136	Aug 2009	Mar 2013	2024-05-01	33607
Chevrolet	Lanos	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Nov 2005	Dec 2010	2024-03-01	33608
Chevrolet	Lanos	1.6 16V	Stufenheck	Frontantrieb	Benzin	78	106	Nov 2005	Dec 2010	2024-03-01	33610
Peugeot	Expert	2.0 HDI 165	Bus	Frontantrieb	Diesel	120	163	Sep 2009	-	2024-03-01	33620
Peugeot	Expert	2.0 HDI 165	Kasten	Frontantrieb	Diesel	120	163	Sep 2009	-	2024-03-01	33621
Mitsubishi	Lancer v	EVO II	Stufenheck	Allrad	Benzin	192	261	Jan 1994	Jul 1995	2024-03-01	33629
Toyota	Hiace iv	2.5 D-4d	Kasten	Heckantrieb	Diesel	70	95	Sep 2006	Dec 2012	2024-03-01	33640
Toyota	Hiace iv	2.5 D-4d 4WD	Bus	Allrad	Diesel	86	117	Sep 2006	Dec 2012	2024-03-01	33641
VW	Eos	2.0 TDI 16V	Cabriolet	Frontantrieb	Diesel	103	140	May 2008	Aug 2015	2024-03-01	33645
Audi	R8	4.2 FSI Quattro	Coupe	Allrad	Benzin	316	430	Jul 2010	Jul 2015	2024-03-01	33658
Audi	R8	4.2 FSI Quattro	Cabriolet	Allrad	Benzin	316	430	Sep 2010	Jul 2015	2024-03-01	33659
Porsche	Cayenne	3.6	SUV	Allrad	Benzin	220	300	Jun 2010	Dec 2018	2025-06-01	33662
Porsche	Cayenne	4.8 S	SUV	Allrad	Benzin	294	400	Jun 2010	May 2014	2025-06-01	33663
Porsche	Cayenne	3.0 S E-hybrid	SUV	Allrad	Benzin/Elektro	306	416	May 2011	May 2017	2024-03-01	33664
Cadillac	Bls	2.0 T AWD	Kombi	Allrad	Benzin	154	210	Dec 2007	Dec 2010	2024-03-01	33665
Chevrolet	Nubira	2.0 D	Stufenheck	Frontantrieb	Diesel	89	121	Jan 2005	Dec 2011	2024-03-01	33666
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	118	160	Aug 2008	-	2024-03-01	33667
Abarth	Grande punto	1.4 Esseesse / Supersport	Schrägheck	Frontantrieb	Benzin	132	180	May 2008	Jun 2010	2024-03-01	33668
Infiniti	G	37 X	Stufenheck	Allrad	Benzin	235	320	Oct 2008	-	2024-03-01	33670
Infiniti	G	37	Stufenheck	Heckantrieb	Benzin	235	320	Oct 2008	-	2024-03-01	33671
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	90	122	Aug 2010	Jul 2018	2024-03-01	33673
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	81	110	May 2010	Jul 2018	2024-03-01	33674
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	May 2010	Jan 2013	2024-03-01	33675
Seat	Altea	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	75	102	Sep 2009	Jun 2013	2024-05-01	33676
Seat	Altea	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	75	102	Sep 2009	Jun 2013	2024-05-01	33677
Dodge	Caliber	2.2 CRD	Schrägheck	Frontantrieb	Diesel	120	163	Jul 2010	Nov 2011	2024-03-01	33678
Skoda	Fabia ii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	55	75	Apr 2010	Dec 2014	2024-03-01	33679
Skoda	Fabia ii combi	1.6 TDI	Kombi	Frontantrieb	Diesel	55	75	Apr 2010	Dec 2014	2024-03-01	33680
Skoda	Fabia ii	1.4 TSI RS	Schrägheck	Frontantrieb	Benzin	132	180	May 2010	Dec 2014	2024-03-01	33681
Skoda	Fabia ii combi	1.4 TSI RS	Kombi	Frontantrieb	Benzin	132	180	May 2010	Dec 2014	2024-03-01	33682
Skoda	Yeti	1.4 TSI	SUV	Frontantrieb	Benzin	90	122	Jun 2010	May 2015	2024-03-01	33683
Jeep	Cherokee	3.7 V6 4X4	Geländewagen geschlossen	Allrad	Benzin	151	205	Jan 2008	-	2024-03-01	33684
Alfa Romeo	159	2.0 Jtdm	Stufenheck	Frontantrieb	Diesel	100	136	Jun 2010	Nov 2011	2024-03-01	33685
Alfa Romeo	159	2.0 Jtdm	Kombi	Frontantrieb	Diesel	100	136	Jun 2010	Nov 2011	2024-03-01	33686
Jeep	Grand cherokee iii	5.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	259	352	Jan 2009	Dec 2010	2024-03-01	33687
Ssangyong	Kyron	3.2 M320 4X4	SUV	Allrad	Benzin	162	220	Mar 2006	Dec 2014	2024-08-01	33688
Seat	Ibiza iv	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Sep 2010	Mar 2012	2024-03-01	33689
Seat	Ibiza iv sc	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Sep 2010	May 2015	2025-06-01	33690
Subaru	Legacy v	2.5 GT AWD	Stufenheck	Allrad	Benzin	195	265	Jul 2010	Dec 2014	2024-03-01	33693
Subaru	Legacy v station wagon	2.5 GT AWD	Kombi	Allrad	Benzin	195	265	Jul 2010	Dec 2014	2024-03-01	33694
Renault	Master iii	2.3 DCI 145 FWD	Kasten	Frontantrieb	Diesel	107	146	Feb 2010	Dec 2024	2026-03-01	33706
Renault	Master iii	2.3 DCI 100 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Feb 2010	Jun 2014	2026-03-01	33707
Renault	Master iii	2.3 DCI 125 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	92	125	Feb 2010	Jun 2019	2026-03-01	33708
Renault	Master iii	2.3 DCI 125 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	92	125	Feb 2010	Jun 2019	2026-03-01	33709
Renault	Master iii	2.3 DCI 145 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	107	146	Feb 2010	Dec 2024	2026-03-01	33710
Renault	Master iii	2.3 DCI 145 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Feb 2010	Dec 2024	2026-03-01	33711
Peugeot	Partner tepee	1.6 VTI	Großraumlimousine	Frontantrieb	Benzin	88	120	Sep 2009	Apr 2016	2024-03-01	33712
KIA	Sportage iii	2.0 Cvvt	SUV	Frontantrieb	Benzin	120	163	Jul 2010	Dec 2015	2024-05-01	33713
KIA	Sportage iii	2.0 Cvvt AWD	SUV	Allrad	Benzin	120	163	Jul 2010	Dec 2015	2024-05-01	33714
KIA	Sportage iii	2.0 Crdi	SUV	Frontantrieb	Diesel	100	136	Jul 2010	Dec 2015	2024-05-01	33715
KIA	Sportage iii	2.0 Crdi AWD	SUV	Allrad	Diesel	100	136	Jul 2010	Dec 2015	2024-05-01	33716
Opel	Corsa d	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	70	95	Jun 2009	Aug 2014	2024-03-01	33721
Opel	Corsa d	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	96	130	Dec 2009	Aug 2014	2024-03-01	33722
Opel	Corsa d	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Dec 2009	Aug 2014	2024-03-01	33723
Opel	Corsa d	1.2	Schrägheck	Frontantrieb	Benzin	63	86	Dec 2009	Aug 2014	2024-03-01	33724
Opel	Corsa d	1.4	Schrägheck	Frontantrieb	Benzin	74	100	Dec 2009	Aug 2014	2024-03-01	33725
Tata	Xenon	2.2 Dicor 4X4	Pick-up	Allrad	Diesel	103	140	Jan 2009	-	2024-03-01	33749
BMW	5	550 I Xdrive	Stufenheck	Allrad	Benzin	300	408	Aug 2010	Jun 2013	2024-03-01	33763
BMW	5	535 D	Stufenheck	Heckantrieb	Diesel	220	299	Sep 2010	Aug 2011	2024-03-01	33764
BMW	5	535 D Xdrive	Schrägheck	Allrad	Diesel	220	299	Mar 2010	Jun 2012	2024-03-01	33765
BMW	5	535 I Xdrive	Schrägheck	Allrad	Benzin	225	306	Sep 2010	Feb 2017	2024-03-01	33766
BMW	5	550 I Xdrive	Schrägheck	Allrad	Benzin	300	408	Jun 2010	Jun 2012	2024-03-01	33767
BMW	5	530 D Xdrive	Schrägheck	Allrad	Diesel	180	245	Jun 2010	Jun 2012	2024-03-01	33768
BMW	5	535 D	Schrägheck	Heckantrieb	Diesel	220	299	Mar 2010	Jun 2012	2024-03-01	33769
BMW	5	523 I	Kombi	Heckantrieb	Benzin	150	204	Nov 2009	Aug 2011	2024-03-01	33770
BMW	5	528 I	Kombi	Heckantrieb	Benzin	190	258	Nov 2009	Aug 2011	2024-03-01	33771
BMW	5	535 I	Kombi	Heckantrieb	Benzin	225	306	Jun 2010	Feb 2017	2024-03-01	33772
BMW	5	520 D	Kombi	Heckantrieb	Diesel	135	184	Jun 2010	Jun 2014	2024-03-01	33773
BMW	5	525 D	Kombi	Heckantrieb	Diesel	150	204	Sep 2010	Aug 2011	2024-03-01	33774
BMW	5	530 D	Kombi	Heckantrieb	Diesel	180	245	Jun 2010	Aug 2011	2024-03-01	33775
BMW	5	535 D	Kombi	Heckantrieb	Diesel	220	299	Sep 2010	Aug 2011	2024-03-01	33776
BMW	X3	Xdrive 35 I	SUV	Allrad	Benzin	225	306	Sep 2010	Aug 2017	2024-03-01	33777
BMW	X3	Xdrive 20 D	SUV	Allrad	Diesel	135	184	Sep 2010	Mar 2014	2024-03-01	33778
Citroën	Berlingo	1.6 VTI 95	Großraumlimousine	Frontantrieb	Benzin	72	98	Jul 2010	Dec 2018	2026-05-01	33779
Citroën	Berlingo	1.6 HDI 110	Großraumlimousine	Frontantrieb	Diesel	82	112	Jul 2010	Dec 2018	2026-05-01	33780
Citroën	Berlingo	1.6 VTI 95	Kasten/Großraumlimousine	Frontantrieb	Benzin	72	98	Jul 2010	Dec 2018	2026-05-01	33781


--- Round 1 / 首次发送 ---
## 更新点

* 完成首轮缓存优先聚类。
* 闭合 56 个输入 Ktype，生成 75 条 READY 映射。
* 本轮全部复用跨批次已有尺寸组，未重复抓取或重复创建 DIMENSION_GROUP。
* 已拆分明确跨改款、门数或轴距差异的物理分支。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：56
* 未闭合输入 Ktype：44
* READY 映射：75
* PENDING 输入 Ktype：44
* 本轮引用既有尺寸组：52
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33500	33500	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33501	33501	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33502	33502	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33503	33503	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33504	33504	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33510	33510	Sedan	Optima III	TF	4	EU-KIA-OPTIMA-III-TF-SEDAN-4D-01	HIGH		READY
33573_prefl	33573	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33573_facelift	33573	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33576	33576	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	HIGH		READY
33582	33582	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
33583	33583	SUV	EX	J50	5	EU-INFINITI-EX-J50-SUV-5D-01	HIGH		READY
33592	33592	MPV	Musa I		5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	HIGH		READY
33598	33598	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
33606	33606	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH		READY
33607	33607	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH		READY
33640_swb	33640	Van	Hiace IV		4	EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	MEDIUM	输入未区分轴距，拆分短轴外廓。	READY
33640_lwb	33640	Van	Hiace IV		4	EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	MEDIUM	输入未区分轴距，拆分长轴外廓。	READY
33641_swb	33641	MPV	Hiace IV		4	EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距，拆分短轴外廓。	READY
33641_lwb	33641	MPV	Hiace IV		4	EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距，拆分长轴外廓。	READY
33645_prefl	33645	Convertible	Eos I	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33645_facelift	33645	Convertible	Eos I	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33658_prefl	33658	Coupe	R8 I	42	2	EU-AUDI-R8-I-COUPE-V8-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33658_facelift	33658	Coupe	R8 I	42	2	EU-AUDI-R8-I-42-COUPE-V10-FACELIFT-01	HIGH	改款后 V8 与既有改款车身外廓一致，复用现有组。	READY
33659_prefl	33659	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V10-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33659_facelift	33659	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V10-FACELIFT-01	HIGH	改款后 V8 与既有改款车身外廓一致，复用现有组。	READY
33665	33665	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
33666	33666	Sedan	Nubira J200	J200	4	EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	HIGH		READY
33667	33667	Hatchback	500	312	3	EU-ABARTH-500-312-HATCHBACK-01	HIGH		READY
33668	33668	Hatchback	Grande Punto	199	3	EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH		READY
33670	33670	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
33671	33671	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
33673_prefl	33673	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33673_facelift	33673	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33674_prefl	33674	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33674_facelift	33674	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33675	33675	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33676	33676	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33677	33677	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33678	33678	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
33679	33679	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33680	33680	Wagon	Fabia II Combi	5J	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33683_prefl	33683	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33683_facelift	33683	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33684	33684	SUV	Cherokee IV	KK	5	EU-JEEP-CHEROKEE-IV-KK-SUV-5D-01	HIGH		READY
33685	33685	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
33686	33686	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
33688_prefl	33688	SUV	Kyron I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33688_facelift	33688	SUV	Kyron I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33689	33689	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH		READY
33690_prefl	33690	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33690_facelift	33690	Hatchback	Ibiza IV SC	6P	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33693_prefl	33693	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33693_facelift	33693	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33694_prefl	33694	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33694_facelift	33694	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33721_3dr	33721	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33721_5dr	33721	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33722_3dr	33722	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33722_5dr	33722	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33723_3dr	33723	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33723_5dr	33723	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33724_3dr	33724	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33724_5dr	33724	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33725_3dr	33725	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33725_5dr	33725	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33763	33763	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33764	33764	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33765	33765	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33766_prefl	33766	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33766_facelift	33766	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33767	33767	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33768	33768	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33769	33769	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33779	33779	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
33780	33780	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量闭合 Nissan NV200/Evalia、Mercedes-Benz E-Class W212 facelift、KIA Sportage III 和 BMW 5 Series F11/X3 F25。
2. 核对 Toyota Highlander XU40、Land Cruiser Prado J150、Porsche Cayenne 958 的改款边界。
3. 最后处理 Navara、Expert、Master III、Tata Xenon 等需要拆分驾驶室、轴距、车顶或底盘形式的宽泛 Ktype。
4. 解决 Lancia Phedra 两个既有尺寸组之间的 1 mm 高度边界，避免无依据选组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 24 个 Ktype，主要覆盖 NV200/Evalia、E-Class W212、Lanos、Expert II、Lancer Evolution II、Sportage III、BMW F11/X3 F25，以及 Berlingo B9 混合车身项。
* 修正上一轮 Audi R8 4.2 FSI 改款映射：V8 改款车型不能复用宽度为 1929 mm 的 V10 尺寸组。
* Nissan、Kia、BMW 与 Audi 技术资料明确区分了不含后视镜宽度及相关车顶/改款外廓。
* Mercedes-Benz E 250、Chevrolet Lanos 和 Lancer Evolution II 的新尺寸组由对应直接规格页闭合。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：80
* READY 映射：113
* PENDING 输入 Ktype：20
* 本轮首次创建/修正尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33584	33584	Van	NV200 I	M20		EU-NISSAN-NV200-M20-VAN-01	HIGH		READY
33585	33585	Van	NV200 I	M20		EU-NISSAN-NV200-M20-VAN-01	HIGH		READY
33587	33587	MPV	NV200 I	M20	5	EU-NISSAN-NV200-M20-MPV-01	HIGH		READY
33588	33588	MPV	NV200 I	M20	5	EU-NISSAN-NV200-M20-MPV-01	HIGH		READY
33590	33590	Sedan	E-Class W212 facelift	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-FACELIFT-SEDAN-01	HIGH		READY
33608	33608	Sedan	Lanos I facelift	T150	4	EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	HIGH		READY
33610	33610	Sedan	Lanos I facelift	T150	4	EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	HIGH		READY
33620_l1_low	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	MEDIUM	输入未区分轴距和车高，拆分L1低车身。	READY
33620_l1_standard	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	MEDIUM	输入未区分轴距和车高，拆分L1标准车身。	READY
33620_l2_low	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	MEDIUM	输入未区分轴距和车高，拆分L2低车身。	READY
33620_l2_standard	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	MEDIUM	输入未区分轴距和车高，拆分L2标准车身。	READY
33621_l1h1_low	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	MEDIUM	输入未区分轴距和车高，拆分L1H1低车身。	READY
33621_l1h1_standard	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	MEDIUM	输入未区分轴距和车高，拆分L1H1标准车身。	READY
33621_l2h1_low	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	MEDIUM	输入未区分轴距和车高，拆分L2H1低车身。	READY
33621_l2h1_standard	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	MEDIUM	输入未区分轴距和车高，拆分L2H1标准车身。	READY
33621_l2h2	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	MEDIUM	输入未区分车顶高度，拆分L2H2高顶车身。	READY
33629	33629	Sedan	Lancer Evolution II	CE9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-II-CE9A-SEDAN-4D-01	HIGH		READY
33658_facelift	33658	Coupe	R8 I facelift	42	2	EU-AUDI-R8-I-42-COUPE-V8-FACELIFT-01	HIGH	纠正为V8改款外廓。	READY
33659_prefl	33659	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V8-PREFL-01	HIGH	纠正为V8改款前外廓。	READY
33659_facelift	33659	Convertible	R8 I facelift	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V8-FACELIFT-01	HIGH	纠正为V8改款后外廓。	READY
33713_norack	33713	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33713_roofrack	33713	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33714_norack	33714	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33714_roofrack	33714	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33715_norack	33715	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33715_roofrack	33715	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33716_norack	33716	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33716_roofrack	33716	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33770	33770	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33771	33771	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33772	33772	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33773	33773	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33774	33774	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33775	33775	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33776	33776	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33777_prefl	33777	SUV	X3 F25	F25	5	EU-BMW-X3-F25-SUV-5D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33777_facelift	33777	SUV	X3 F25 LCI	F25	5	EU-BMW-X3-F25-SUV-5D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33778	33778	SUV	X3 F25	F25	5	EU-BMW-X3-F25-SUV-5D-PREFL-01	HIGH	生产结束时间早于改款车型批量生产。	READY
33781_mpv	33781	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	MEDIUM	输入同时覆盖Kasten和Großraumlimousine，拆分乘用车身。	READY
33781_van_l1	33781	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	输入未区分轴距，拆分L1厢式车身。	READY
33781_van_l2	33781	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	MEDIUM	输入未区分轴距，拆分L2厢式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV200-M20-VAN-01	4400	1695	1860	Nissan NV200 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV200_combi_UK.pdf
EU-NISSAN-NV200-M20-MPV-01	4400	1695	1860	Nissan NV200 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV200_combi_UK.pdf
EU-MERCEDES-BENZ-E-CLASS-W212-FACELIFT-SEDAN-01	4879	1854	1474	Auto-Data Mercedes-Benz E-class W212 facelift E 250	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-250-211hp-7g-tronic-plus-18732
EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	4237	1678	1432	Auto-Data Chevrolet Lanos	https://www.auto-data.net/en/chevrolet-lanos-model-1595
EU-MITSUBISHI-LANCER-EVOLUTION-II-CE9A-SEDAN-4D-01	4310	1695	1420	Auto-Data Mitsubishi Lancer Evolution II	https://www.auto-data.net/en/mitsubishi-lancer-evolution-model-2861
EU-AUDI-R8-I-42-COUPE-V8-FACELIFT-01	4440	1904	1252	Audi R8 technical data March 2013	https://www.ausmotive.com/downloads/Audi/R8-AU-tech-data-March2013.pdf
EU-AUDI-R8-I-42-CONVERTIBLE-V8-PREFL-01	4435	1904	1244	Audi R8 Spyder 4.2 FSI quattro technical data	https://autoinfo.jp/release/R8_Spyder_4.2FSI_my11_spec.pdf
EU-AUDI-R8-I-42-CONVERTIBLE-V8-FACELIFT-01	4440	1904	1244	Audi R8 technical data March 2013	https://www.ausmotive.com/downloads/Audi/R8-AU-tech-data-March2013.pdf
EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	4440	1855	1635	Kia Sportage R official catalogue	https://www.kia.com/content/dam/kwcms/kr/ko/files/RSL/catalog/catalog_sportage-r.pdf
EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	4440	1855	1645	Kia Sportage R official catalogue	https://www.kia.com/content/dam/kwcms/kr/ko/files/RSL/catalog/catalog_sportage-r.pdf
EU-BMW-5-SERIES-F11-WAGON-5D-01	4907	1860	1462	BMW 5 Series Touring F11 official technical data; BMW 5 Series Touring F11 LCI official technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0080392FR/127666; https://www.press.bmwgroup.com/global/article/attachment/T0203606EN/294945
EU-BMW-X3-F25-SUV-5D-PREFL-01	4648	1881	1661	BMW X3 F25 official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0085745ES/131980
EU-BMW-X3-F25-SUV-5D-FACELIFT-01	4657	1881	1661	BMW X3 F25 LCI official specification sheet	https://bps.bmw.com.tw/uploads/bps/1631866697_CCvKpX.pdf
```

## 下一步优先处理

1. 闭合 Fabia II RS Hatchback/Combi、Grand Cherokee III 5.7 和 Lancia Phedra，优先解决单一车身尺寸组。
2. 核对 Cayenne 958、Highlander XU40 和 Prado J150 的改款、门数及车顶边界。
3. 最后集中处理 Navara 底盘、Master III 底盘车、Partner Tepee 跨改款和 Tata Xenon 驾驶室分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-250-211hp-7g-tronic-plus-18732?utm_source=chatgpt.com "Mercedes-Benz E-class (W212, facelift 2013) E 250 (211 ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新闭合 9 个 Ktype，覆盖 Highlander XU40、Phedra、Cayenne 958、Fabia II RS/Combi RS 与 Partner Tepee。
* Highlander 的前驱与四驱版本共用同一外廓；Cayenne 3.6 与 4.8 S 共用改款前外廓；416 hp S E-Hybrid 使用改款后外廓。官方规格已明确不含后视镜宽度。
* Fabia II RS 两厢和 Combi RS 因长度、高度不同分别建组。
* Phedra 与 Partner Tepee 本轮复用既有尺寸组，不重复输出尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：89
* READY 映射：122
* PENDING 输入 Ktype：11
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33532	33532	SUV	Highlander II	XU40	5	EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	HIGH		READY
33534	33534	SUV	Highlander II	XU40	5	EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	HIGH		READY
33593	33593	MPV	Phedra I		5	EU-LANCIA-PHEDRA-I-MPV-02	HIGH		READY
33662	33662	SUV	Cayenne II	958	5	EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	HIGH		READY
33663	33663	SUV	Cayenne II	958	5	EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	HIGH		READY
33664	33664	SUV	Cayenne II facelift	958	5	EU-PORSCHE-CAYENNE-958-SUV-S-E-HYBRID-FACELIFT-01	HIGH		READY
33681	33681	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-RS-HATCHBACK-5D-01	HIGH		READY
33682	33682	Wagon	Fabia II Combi	5J	5	EU-SKODA-FABIA-II-RS-COMBI-WAGON-5D-01	HIGH		READY
33712	33712	MPV	Partner II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	MEDIUM	Partner Tepee与Berlingo II B9共用乘用车物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	4785	1910	1760	Toyota Canada 2008 Highlander official specifications	https://media.toyota.ca/en/specifications/2008/2008-highlander--highlander-hybrid-specifications.html
EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	4846	1939	1705	Porsche 2011 Cayenne and Cayenne S official specifications	https://newsroom.porsche.com/dam/jcr%3A88587da7-01da-43c1-8dd9-8de1dd4ccd6d/2011_Cayenne_Specifications.pdf
EU-PORSCHE-CAYENNE-958-SUV-S-E-HYBRID-FACELIFT-01	4855	1939	1705	Porsche The New Cayenne official press kit	https://newsroom.porsche.com/dam/jcr%3A13b2afec-e26a-4280-8e16-06686a45d53b/Press
EU-SKODA-FABIA-II-RS-HATCHBACK-5D-01	4029	1642	1492	ŠKODA Fabia official UK brochure November 2011	https://blog.le-parnass.com/catalogue_pdf/skoda_fabia.pdf
EU-SKODA-FABIA-II-RS-COMBI-WAGON-5D-01	4276	1642	1494	ŠKODA Fabia official UK brochure November 2011	https://blog.le-parnass.com/catalogue_pdf/skoda_fabia.pdf
```

## 下一步优先处理

1. 闭合 Grand Cherokee III 5.7 和 Tata Xenon，确认标准车身与驾驶室分支。
2. 处理 Land Cruiser Prado J150 的三门、五门及改款边界。
3. 集中处理 Navara D40 底盘车和 Renault Master III 的厢式车、底盘车、轴距、车顶及单双后轮分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新闭合 3 个 Ktype，新增 4 条 READY 映射。
* `33574` 确认同时覆盖 Prado J150 三门和五门外廓，分别为 `4485×1885×1875 mm` 与 `4760×1885×1890 mm`；来源同时列出含镜宽度，落盘宽度可确认是不含后视镜口径。([汽车数据网][1])
* `33687` 确认为 Grand Cherokee III 非 SRT8 的 5.7 V8 标准外廓，不能复用既有 SRT8 尺寸组。([汽车目录][2])
* `33749` 确认为 Xenon 2.2 d 4×4 四门五座 Pickup 外廓。([汽车数据网][3])
* `33565` 已确认属于 D40 Flatbed/Chassis，而非现有 King Cab 或 Double Cab Pickup 尺寸组，因此继续保留待处理。([阿罗普纽斯][4])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：92
* READY 映射：126
* PENDING 输入 Ktype：8
* 已确认尺寸组：74
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33574_3dr	33574	SUV	Land Cruiser Prado J150	J150	3	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-PREFL-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33574_5dr	33574	SUV	Land Cruiser Prado J150	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33687	33687	SUV	Grand Cherokee III	WH	5	EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-5D-5.7-01	HIGH	非SRT8标准车身外廓。	READY
33749	33749	Pickup	Xenon		4	EU-TATA-XENON-PICKUP-DOUBLE-CAB-4D-01	MEDIUM	四门五座双排驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-PREFL-01	4485	1885	1875	Auto-Data Toyota Land Cruiser Prado J150 3-door 3.0 D-4D	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-3-door-3.0-d-4d-173hp-4wd-automatic-43381
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	4760	1885	1890	Auto-Data Toyota Land Cruiser Prado J150 5-door 3.0 D-4D	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-5-door-3.0-d-4d-173hp-4wd-automatic-3679
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-5D-5.7-01	4750	1870	1740	Automobile-Catalog 2009 Jeep Grand Cherokee 5.7 V8 Hemi Overland	https://www.automobile-catalog.com/car/2009/1326845/jeep_grand_cherokee_5_7_v8_hemi_overland.html
EU-TATA-XENON-PICKUP-DOUBLE-CAB-4D-01	5125	1860	1833	Auto-Data Tata Xenon 2.2 d 140 Hp 4x4	https://www.auto-data.net/en/tata-xenon-2.2-d-140hp-4x4-27681
```

## 下一步优先处理

1. 解决 `33586` Prado J150 4.0 V6 跨两次改款的外廓及宽度冲突。
2. 闭合 `33565` Navara D40 Flatbed/Chassis 的准确驾驶室与完整外廓。
3. 批量闭合 `33706–33711` Master III 的 FWD/RWD、Van/Chassis、轴距、车顶、单双后轮及改款分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-5-door-3.0-d-4d-173hp-4wd-automatic-3679 "Toyota Land Cruiser Prado (J150) 5-door 3.0 D-4D (173 Hp) 4WD Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2009/1326845/jeep_grand_cherokee_5_7_v8_hemi_overland.html?utm_source=chatgpt.com "2009 Jeep Grand Cherokee 5.7 V8 Hemi Overland (aut. 5)"
[3]: https://www.auto-data.net/en/tata-xenon-2.2-d-140hp-4x4-27681 "Tata Xenon 2.2 d (140 Hp) 4x4 | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.allopneus.com/vehicule/nissan/navara/navara-camion-plate-forme-chassis "Pneu NISSAN NAVARA Camion plate-forme/Châssis : Pression et dimensions des pneus - Allopneus.com"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 新闭合 `33586` 及 `33708–33711`，新增 27 条 READY 映射。
* Prado J150 按改款前、2013 改款和 2017 改款拆分三套五门外廓。([汽车数据网][1])
* Master III 底盘车按前后驱、单/双排、轴距、单双后轮、长后悬及 2019 改款边界拆分；尺寸宽度均采用官方资料中的不含后视镜车身宽度。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：97
* READY 映射：153
* PENDING 输入 Ktype：3
* 已确认尺寸组：93
* 本轮首次创建尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33586_prefl	33586	SUV	Land Cruiser Prado J150	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	HIGH	改款前五门外廓。	READY
33586_facelift2013	33586	SUV	Land Cruiser Prado J150 facelift 2013	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2013-01	HIGH	2013改款五门外廓。	READY
33586_facelift2017	33586	SUV	Land Cruiser Prado J150 facelift 2017	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2017-01	HIGH	2017改款五门外廓。	READY
33708_single_l2	33708	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	单排L2前驱底盘外廓。	READY
33708_single_l3	33708	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	单排L3前驱底盘外廓。	READY
33708_double_l2	33708	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	MEDIUM	双排L2前驱底盘外廓。	READY
33708_double_l3	33708	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	双排L3前驱底盘外廓。	READY
33709_single_l2_srw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	MEDIUM	单排L2后驱单后轮外廓。	READY
33709_single_l2_drw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	MEDIUM	单排L2后驱双后轮外廓。	READY
33709_single_l3_srw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	MEDIUM	单排L3后驱单后轮外廓。	READY
33710_single_l2_srw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	MEDIUM	单排L2后驱单后轮外廓。	READY
33710_single_l2_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	MEDIUM	单排L2后驱双后轮外廓。	READY
33710_single_l2_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-PREFL-01	MEDIUM	单排L2后驱长后悬双后轮外廓。	READY
33710_single_l3_srw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	MEDIUM	单排L3后驱单后轮外廓。	READY
33710_single_l3_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-PREFL-01	MEDIUM	单排L3后驱长后悬双后轮外廓。	READY
33710_double_l2_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-PREFL-01	MEDIUM	双排L2后驱长后悬双后轮外廓。	READY
33710_double_l3_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L3-LONGOVERHANG-DRW-PREFL-01	MEDIUM	双排L3后驱长后悬双后轮外廓。	READY
33710_single_l2_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后单排L2长后悬双后轮外廓。	READY
33710_single_l3_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后单排L3长后悬双后轮外廓。	READY
33710_double_l2_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后双排L2长后悬双后轮外廓。	READY
33711_single_l2_prefl	33711	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	单排L2前驱底盘外廓。	READY
33711_single_l3_prefl	33711	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	单排L3前驱底盘外廓。	READY
33711_double_l2_prefl	33711	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	MEDIUM	双排L2前驱底盘外廓。	READY
33711_double_l3_prefl	33711	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	双排L3前驱底盘外廓。	READY
33711_single_l2_facelift	33711	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-FACELIFT-01	MEDIUM	2019改款后单排L2前驱底盘外廓。	READY
33711_single_l3_facelift	33711	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-FACELIFT-01	MEDIUM	2019改款后单排L3前驱底盘外廓。	READY
33711_double_l3_facelift	33711	Chassis Cab	Master III facelift 2019	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-FACELIFT-01	MEDIUM	2019改款后双排L3前驱底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2013-01	4780	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 5-door 4.0 V6	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-4.0-v6-dual-vvt-i-281hp-automatic-18524
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2017-01	4840	1855	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2017 5-door 4.0 V6	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2017-5-door-4.0-v6-249hp-4wd-automatic-32881
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	5643	2070	2265	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	6293	2070	2258	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	5643	2070	2272	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	6293	2070	2263	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	5643	2070	2284	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	5643	2070	2283	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-PREFL-01	6193	2070	2283	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	6293	2070	2276	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-PREFL-01	6843	2070	2286	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-PREFL-01	6193	2070	2301	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L3-LONGOVERHANG-DRW-PREFL-01	6843	2070	2286	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-FACELIFT-01	6220	2070	2283	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-FACELIFT-01	6870	2070	2273	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-FACELIFT-01	6220	2070	2301	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-FACELIFT-01	5670	2070	2265	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-FACELIFT-01	6320	2070	2258	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-FACELIFT-01	6320	2070	2263	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
```

## 下一步优先处理

1. 闭合 `33565` Navara D40 Flatbed/Chassis 的驾驶室和底盘长度分支。
2. 闭合 `33706` Master III FWD Van 的 2019 改款后各轴距和车顶外廓。
3. 核对 `33707` Master III dCi 100 FWD 底盘车实际可用的单排、双排和轴距范围。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-4.0-v6-dual-vvt-i-281hp-automatic-18524?utm_source=chatgpt.com "Toyota Land Cruiser Prado (J150, facelift 2013) 5-door 4.0 ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 `33706`：按 Master III FWD 厢式车的 L1/L2/L3、H1/H2/H3 及 2019 改款前后拆分，共新增 12 条 READY 映射。官方尺寸表确认改款后车身宽度为不含后视镜的 `2070 mm`。([Autodoc][1])
* 闭合 `33707`：dCi 100 FWD 底盘车覆盖单排 L2、单排 L3 和双排 L3，共新增 3 条 READY 映射；均复用本批已建立的底盘尺寸组。([K Motorshop][2])
* 本轮首次创建 6 个 Master III 2019 改款后 FWD Van 尺寸组。
* 仅剩 `33565` Nissan Navara D40 Platform/Chassis 尚未闭合。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：99
* READY 映射：168
* PENDING 输入 Ktype：1
* 已确认尺寸组：99
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33706_l1h1_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	MEDIUM	L1H1改款前厢式车外廓。	READY
33706_l1h1_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-FACELIFT-01	MEDIUM	2019改款后L1H1厢式车外廓。	READY
33706_l1h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	MEDIUM	L1H2改款前厢式车外廓。	READY
33706_l1h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-FACELIFT-01	MEDIUM	2019改款后L1H2厢式车外廓。	READY
33706_l2h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	MEDIUM	L2H2改款前厢式车外廓。	READY
33706_l2h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-FACELIFT-01	MEDIUM	2019改款后L2H2厢式车外廓。	READY
33706_l2h3_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	MEDIUM	L2H3改款前厢式车外廓。	READY
33706_l2h3_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-FACELIFT-01	MEDIUM	2019改款后L2H3厢式车外廓。	READY
33706_l3h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	MEDIUM	L3H2改款前厢式车外廓。	READY
33706_l3h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-FACELIFT-01	MEDIUM	2019改款后L3H2厢式车外廓。	READY
33706_l3h3_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	MEDIUM	L3H3改款前厢式车外廓。	READY
33706_l3h3_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-FACELIFT-01	MEDIUM	2019改款后L3H3厢式车外廓。	READY
33707_single_l2	33707	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	dCi 100前驱单排L2底盘外廓。	READY
33707_single_l3	33707	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	dCi 100前驱单排L3底盘外廓。	READY
33707_double_l3	33707	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	dCi 100前驱双排L3底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-FACELIFT-01	5075	2070	2307	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-FACELIFT-01	5075	2070	2500	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-FACELIFT-01	5575	2070	2499	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-FACELIFT-01	5575	2070	2749	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-FACELIFT-01	6225	2070	2488	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-FACELIFT-01	6225	2070	2744	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
```

## 下一步优先处理

1. 仅处理 `33565` Nissan Navara D40 Platform/Chassis。
2. 确认该 Ktype 实际覆盖 King Cab、Double Cab 或独立底盘车外廓，避免仅因两种 Pickup 缓存尺寸相同而错误合并。
3. 闭合后立即执行一次机械检查，并输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/pilot-bearing-10159/renault/master/master-iii-box-fv/33706-2-3-dci-145-fwd-fv0e-fv0f-fv0h-fv02-fv0m-fv0s?utm_source=chatgpt.com "Pilot bearing Renault Master 3 Van 2.3 dCi FWD 146 hp ..."
[2]: https://www.kmotorshop.com/en/article-list/list/car/33707/tree-shop%7C363?utm_source=chatgpt.com "RENAULT MASTER III Platform/Chassis (EV, HV, UV) 2.3 dCi ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合最后一个 Ktype `33565`。Nissan 官方资料确认 144 PS 4WD 对应 Double Cab VISIA，外廓为 `5296 × 1848 × 1913 mm`，宽度为不含后视镜口径。([英国汽车租赁][1])
* 新建 `EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-02`，未覆盖已有三维不同的 `...-01`。
* 已完成固定表头、唯一主键、映射引用闭合、尺寸及来源非空、孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：169
* PENDING：0
* DIMENSION_GROUP：115
* 所有输入 Ktype 均已覆盖，全部映射引用闭合。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33500	33500	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33501	33501	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33502	33502	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33503	33503	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33504	33504	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33510	33510	Sedan	Optima III	TF	4	EU-KIA-OPTIMA-III-TF-SEDAN-4D-01	HIGH		READY
33532	33532	SUV	Highlander II	XU40	5	EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	HIGH		READY
33534	33534	SUV	Highlander II	XU40	5	EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	HIGH		READY
33565	33565	Pickup	Navara D40	D40	4	EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-02	MEDIUM	144 PS 4WD车型对应Double Cab VISIA；输入车身类别为底盘目录分类。	READY
33573_prefl	33573	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33573_facelift	33573	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33574_3dr	33574	SUV	Land Cruiser Prado J150	J150	3	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-PREFL-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33574_5dr	33574	SUV	Land Cruiser Prado J150	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33576	33576	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	HIGH		READY
33582	33582	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
33583	33583	SUV	EX	J50	5	EU-INFINITI-EX-J50-SUV-5D-01	HIGH		READY
33584	33584	Van	NV200 I	M20		EU-NISSAN-NV200-M20-VAN-01	HIGH		READY
33585	33585	Van	NV200 I	M20		EU-NISSAN-NV200-M20-VAN-01	HIGH		READY
33586_prefl	33586	SUV	Land Cruiser Prado J150	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	HIGH	改款前五门外廓。	READY
33586_facelift2013	33586	SUV	Land Cruiser Prado J150 facelift 2013	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2013-01	HIGH	2013改款五门外廓。	READY
33586_facelift2017	33586	SUV	Land Cruiser Prado J150 facelift 2017	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2017-01	HIGH	2017改款五门外廓。	READY
33587	33587	MPV	NV200 I	M20	5	EU-NISSAN-NV200-M20-MPV-01	HIGH		READY
33588	33588	MPV	NV200 I	M20	5	EU-NISSAN-NV200-M20-MPV-01	HIGH		READY
33590	33590	Sedan	E-Class W212 facelift	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-FACELIFT-SEDAN-01	HIGH		READY
33592	33592	MPV	Musa I		5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	HIGH		READY
33593	33593	MPV	Phedra I		5	EU-LANCIA-PHEDRA-I-MPV-02	HIGH		READY
33598	33598	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
33606	33606	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH		READY
33607	33607	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH		READY
33608	33608	Sedan	Lanos I facelift	T150	4	EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	HIGH		READY
33610	33610	Sedan	Lanos I facelift	T150	4	EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	HIGH		READY
33620_l1_low	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	MEDIUM	输入未区分轴距和车高，拆分L1低车身。	READY
33620_l1_standard	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	MEDIUM	输入未区分轴距和车高，拆分L1标准车身。	READY
33620_l2_low	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	MEDIUM	输入未区分轴距和车高，拆分L2低车身。	READY
33620_l2_standard	33620	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	MEDIUM	输入未区分轴距和车高，拆分L2标准车身。	READY
33621_l1h1_low	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	MEDIUM	输入未区分轴距和车高，拆分L1H1低车身。	READY
33621_l1h1_standard	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	MEDIUM	输入未区分轴距和车高，拆分L1H1标准车身。	READY
33621_l2h1_low	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	MEDIUM	输入未区分轴距和车高，拆分L2H1低车身。	READY
33621_l2h1_standard	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	MEDIUM	输入未区分轴距和车高，拆分L2H1标准车身。	READY
33621_l2h2	33621	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	MEDIUM	输入未区分车顶高度，拆分L2H2高顶车身。	READY
33629	33629	Sedan	Lancer Evolution II	CE9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-II-CE9A-SEDAN-4D-01	HIGH		READY
33640_swb	33640	Van	Hiace IV		4	EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	MEDIUM	输入未区分轴距，拆分短轴外廓。	READY
33640_lwb	33640	Van	Hiace IV		4	EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	MEDIUM	输入未区分轴距，拆分长轴外廓。	READY
33641_swb	33641	MPV	Hiace IV		4	EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距，拆分短轴外廓。	READY
33641_lwb	33641	MPV	Hiace IV		4	EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距，拆分长轴外廓。	READY
33645_prefl	33645	Convertible	Eos I	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33645_facelift	33645	Convertible	Eos I	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33658_prefl	33658	Coupe	R8 I	42	2	EU-AUDI-R8-I-COUPE-V8-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33658_facelift	33658	Coupe	R8 I facelift	42	2	EU-AUDI-R8-I-42-COUPE-V8-FACELIFT-01	HIGH	纠正为V8改款外廓。	READY
33659_prefl	33659	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V8-PREFL-01	HIGH	纠正为V8改款前外廓。	READY
33659_facelift	33659	Convertible	R8 I facelift	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V8-FACELIFT-01	HIGH	纠正为V8改款后外廓。	READY
33662	33662	SUV	Cayenne II	958	5	EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	HIGH		READY
33663	33663	SUV	Cayenne II	958	5	EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	HIGH		READY
33664	33664	SUV	Cayenne II facelift	958	5	EU-PORSCHE-CAYENNE-958-SUV-S-E-HYBRID-FACELIFT-01	HIGH		READY
33665	33665	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
33666	33666	Sedan	Nubira J200	J200	4	EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	HIGH		READY
33667	33667	Hatchback	500	312	3	EU-ABARTH-500-312-HATCHBACK-01	HIGH		READY
33668	33668	Hatchback	Grande Punto	199	3	EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH		READY
33670	33670	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
33671	33671	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
33673_prefl	33673	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33673_facelift	33673	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33674_prefl	33674	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33674_facelift	33674	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33675	33675	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33676	33676	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33677	33677	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33678	33678	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
33679	33679	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33680	33680	Wagon	Fabia II Combi	5J	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33681	33681	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-RS-HATCHBACK-5D-01	HIGH		READY
33682	33682	Wagon	Fabia II Combi	5J	5	EU-SKODA-FABIA-II-RS-COMBI-WAGON-5D-01	HIGH		READY
33683_prefl	33683	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33683_facelift	33683	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33684	33684	SUV	Cherokee IV	KK	5	EU-JEEP-CHEROKEE-IV-KK-SUV-5D-01	HIGH		READY
33685	33685	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
33686	33686	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
33687	33687	SUV	Grand Cherokee III	WH	5	EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-5D-5.7-01	HIGH	非SRT8标准车身外廓。	READY
33688_prefl	33688	SUV	Kyron I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33688_facelift	33688	SUV	Kyron I	DJ	5	EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33689	33689	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH		READY
33690_prefl	33690	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33690_facelift	33690	Hatchback	Ibiza IV SC	6P	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33693_prefl	33693	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33693_facelift	33693	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33694_prefl	33694	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33694_facelift	33694	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33706_l1h1_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	MEDIUM	L1H1改款前厢式车外廓。	READY
33706_l1h1_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-FACELIFT-01	MEDIUM	2019改款后L1H1厢式车外廓。	READY
33706_l1h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	MEDIUM	L1H2改款前厢式车外廓。	READY
33706_l1h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-FACELIFT-01	MEDIUM	2019改款后L1H2厢式车外廓。	READY
33706_l2h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	MEDIUM	L2H2改款前厢式车外廓。	READY
33706_l2h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-FACELIFT-01	MEDIUM	2019改款后L2H2厢式车外廓。	READY
33706_l2h3_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	MEDIUM	L2H3改款前厢式车外廓。	READY
33706_l2h3_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-FACELIFT-01	MEDIUM	2019改款后L2H3厢式车外廓。	READY
33706_l3h2_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	MEDIUM	L3H2改款前厢式车外廓。	READY
33706_l3h2_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-FACELIFT-01	MEDIUM	2019改款后L3H2厢式车外廓。	READY
33706_l3h3_prefl	33706	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	MEDIUM	L3H3改款前厢式车外廓。	READY
33706_l3h3_facelift	33706	Van	Master III facelift 2019	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-FACELIFT-01	MEDIUM	2019改款后L3H3厢式车外廓。	READY
33707_single_l2	33707	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	dCi 100前驱单排L2底盘外廓。	READY
33707_single_l3	33707	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	dCi 100前驱单排L3底盘外廓。	READY
33707_double_l3	33707	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	dCi 100前驱双排L3底盘外廓。	READY
33708_single_l2	33708	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	单排L2前驱底盘外廓。	READY
33708_single_l3	33708	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	单排L3前驱底盘外廓。	READY
33708_double_l2	33708	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	MEDIUM	双排L2前驱底盘外廓。	READY
33708_double_l3	33708	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	双排L3前驱底盘外廓。	READY
33709_single_l2_srw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	MEDIUM	单排L2后驱单后轮外廓。	READY
33709_single_l2_drw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	MEDIUM	单排L2后驱双后轮外廓。	READY
33709_single_l3_srw	33709	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	MEDIUM	单排L3后驱单后轮外廓。	READY
33710_single_l2_srw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	MEDIUM	单排L2后驱单后轮外廓。	READY
33710_single_l2_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	MEDIUM	单排L2后驱双后轮外廓。	READY
33710_single_l2_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-PREFL-01	MEDIUM	单排L2后驱长后悬双后轮外廓。	READY
33710_single_l3_srw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	MEDIUM	单排L3后驱单后轮外廓。	READY
33710_single_l3_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-PREFL-01	MEDIUM	单排L3后驱长后悬双后轮外廓。	READY
33710_double_l2_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-PREFL-01	MEDIUM	双排L2后驱长后悬双后轮外廓。	READY
33710_double_l3_longoverhang_drw_prefl	33710	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L3-LONGOVERHANG-DRW-PREFL-01	MEDIUM	双排L3后驱长后悬双后轮外廓。	READY
33710_single_l2_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后单排L2长后悬双后轮外廓。	READY
33710_single_l3_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后单排L3长后悬双后轮外廓。	READY
33710_double_l2_longoverhang_drw_facelift	33710	Chassis Cab	Master III facelift 2019	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-FACELIFT-01	MEDIUM	2019改款后双排L2长后悬双后轮外廓。	READY
33711_single_l2_prefl	33711	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	MEDIUM	单排L2前驱底盘外廓。	READY
33711_single_l3_prefl	33711	Chassis Cab	Master III	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	MEDIUM	单排L3前驱底盘外廓。	READY
33711_double_l2_prefl	33711	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	MEDIUM	双排L2前驱底盘外廓。	READY
33711_double_l3_prefl	33711	Chassis Cab	Master III	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	MEDIUM	双排L3前驱底盘外廓。	READY
33711_single_l2_facelift	33711	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-FACELIFT-01	MEDIUM	2019改款后单排L2前驱底盘外廓。	READY
33711_single_l3_facelift	33711	Chassis Cab	Master III facelift 2019	X62	2	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-FACELIFT-01	MEDIUM	2019改款后单排L3前驱底盘外廓。	READY
33711_double_l3_facelift	33711	Chassis Cab	Master III facelift 2019	X62	4	EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-FACELIFT-01	MEDIUM	2019改款后双排L3前驱底盘外廓。	READY
33712	33712	MPV	Partner II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	MEDIUM	Partner Tepee与Berlingo II B9共用乘用车物理外廓。	READY
33713_norack	33713	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33713_roofrack	33713	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33714_norack	33714	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33714_roofrack	33714	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33715_norack	33715	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33715_roofrack	33715	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33716_norack	33716	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	HIGH	输入未区分车顶行李架，拆分无行李架外廓。	READY
33716_roofrack	33716	SUV	Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	HIGH	输入未区分车顶行李架，拆分带行李架外廓。	READY
33721_3dr	33721	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33721_5dr	33721	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33722_3dr	33722	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33722_5dr	33722	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33723_3dr	33723	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33723_5dr	33723	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33724_3dr	33724	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33724_5dr	33724	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33725_3dr	33725	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	输入未区分门数，拆分三门外廓。	READY
33725_5dr	33725	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	输入未区分门数，拆分五门外廓。	READY
33749	33749	Pickup	Xenon		4	EU-TATA-XENON-PICKUP-DOUBLE-CAB-4D-01	MEDIUM	四门五座双排驾驶室外廓。	READY
33763	33763	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33764	33764	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33765	33765	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33766_prefl	33766	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33766_facelift	33766	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33767	33767	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33768	33768	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33769	33769	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
33770	33770	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33771	33771	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33772	33772	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33773	33773	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33774	33774	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33775	33775	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33776	33776	Wagon	5 Series F11	F11	5	EU-BMW-5-SERIES-F11-WAGON-5D-01	HIGH		READY
33777_prefl	33777	SUV	X3 F25	F25	5	EU-BMW-X3-F25-SUV-5D-PREFL-01	HIGH	跨改款生产期，拆分改款前外廓。	READY
33777_facelift	33777	SUV	X3 F25 LCI	F25	5	EU-BMW-X3-F25-SUV-5D-FACELIFT-01	HIGH	跨改款生产期，拆分改款后外廓。	READY
33778	33778	SUV	X3 F25	F25	5	EU-BMW-X3-F25-SUV-5D-PREFL-01	HIGH	生产结束时间早于改款车型批量生产。	READY
33779	33779	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
33780	33780	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
33781_mpv	33781	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	MEDIUM	输入同时覆盖Kasten和Großraumlimousine，拆分乘用车身。	READY
33781_van_l1	33781	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	输入未区分轴距，拆分L1厢式车身。	READY
33781_van_l2	33781	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	MEDIUM	输入未区分轴距，拆分L2厢式车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4701-4800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	5008	1868	1466	AutoZine Saab 9-5 2010 specifications	https://www.autozine.org/Archive/Saab/old/95_2010.html
EU-KIA-OPTIMA-III-TF-SEDAN-4D-01	4845	1830	1455	Kia Optima K5 official brochure	https://www.kia.com/content/dam/kwcms/sg/en/pdf/Optima%20K5-brochure.pdf
EU-TOYOTA-HIGHLANDER-II-XU40-SUV-5D-01	4785	1910	1760	Toyota Canada 2008 Highlander official specifications	https://media.toyota.ca/en/specifications/2008/2008-highlander--highlander-hybrid-specifications.html
EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-02	5296	1848	1913	Nissan Navara official UK brochure June 2013	https://www.ukcarline.co.uk/uploads/pds/Nissan%20Navara%20Brochure.pdf
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421	BMW 3 Series Sedan E90 ACEA technical data MY07	https://www.tomic.ba/fs/cjenik/E90%20ACEA%20Technik%200307.pdf
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	BMW 3 Series Sedan E90 LCI official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0084820ES/132004
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-PREFL-01	4485	1885	1875	Auto-Data Toyota Land Cruiser Prado J150 3-door 3.0 D-4D	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-3-door-3.0-d-4d-173hp-4wd-automatic-43381
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-PREFL-01	4760	1885	1890	Auto-Data Toyota Land Cruiser Prado J150 5-door 3.0 D-4D	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-5-door-3.0-d-4d-173hp-4wd-automatic-3679
EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	4170	1700	1680	Carplanner Renault Scenic Phase II specifications	https://www.carplanner.ee/catalogue/renault/scenic/readmore/6881/
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680	ADAC Infiniti FX S51 vehicle catalogue	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/infiniti/fx/s51/223878/
EU-INFINITI-EX-J50-SUV-5D-01	4630	1800	1575	Auto-Data Infiniti EX model specifications	https://www.auto-data.net/en/infiniti-ex-model-1527
EU-NISSAN-NV200-M20-VAN-01	4400	1695	1860	Nissan NV200 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV200_combi_UK.pdf
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2013-01	4780	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 5-door 4.0 V6	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-4.0-v6-dual-vvt-i-281hp-automatic-18524
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-2017-01	4840	1855	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2017 5-door 4.0 V6	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2017-5-door-4.0-v6-249hp-4wd-automatic-32881
EU-NISSAN-NV200-M20-MPV-01	4400	1695	1860	Nissan NV200 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV200_combi_UK.pdf
EU-MERCEDES-BENZ-E-CLASS-W212-FACELIFT-SEDAN-01	4879	1854	1474	Auto-Data Mercedes-Benz E-class W212 facelift E 250	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-250-211hp-7g-tronic-plus-18732
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660	Auto-Data Lancia Musa facelift 1.3 Multijet 95	https://www.auto-data.net/en/lancia-musa-facelift-2007-1.3-multijet-95hp-30856
EU-LANCIA-PHEDRA-I-MPV-02	4750	1863	1759	Automobile-Catalog Lancia Phedra 2.0 JTD Multijet	https://www.automobile-catalog.com/car/2009/1386665/lancia_phedra_2_0_jtd_multijet_16v_120_argento.html
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Mitsubishi 2010 Lancer official press kit	https://media.mitsubishicars.com/en-US/releases/2010-lancer-press-kit
EU-KIA-CARENS-III-UN-MPV-01	4545	1820	1650	Kia Carens 2013 owner manual dimensions	https://www.carmanualsonline.info/kia-carens-2013-3-g-owner-s-manual/34
EU-CHEVROLET-LANOS-T150-SEDAN-4D-01	4237	1678	1432	Auto-Data Chevrolet Lanos	https://www.auto-data.net/en/chevrolet-lanos-model-1595
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880	Peugeot Expert Tepee technical specifications	https://www.jezdzik.net/eng/cars/peugeot/expert/peugeot-expert-tepee-2%2C0-hdi-120km.html
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942	Peugeot Expert technical sheet	https://www.caradisiac.com/VUL-Peugeot-Expert-la-fiche-technique-28775.htm
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880	Peugeot Expert Tepee technical specifications	https://www.pkw.de/autokatalog/peugeot/expert/tepee
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942	Peugeot Expert technical sheet	https://www.caradisiac.com/VUL-Peugeot-Expert-la-fiche-technique-28775.htm
EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	4805	1895	1880	Peugeot Expert technical specifications	https://yauto.cz/vin/VF3XARHKH64249883/
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942	Peugeot Expert technical sheet	https://www.caradisiac.com/VUL-Peugeot-Expert-la-fiche-technique-28775.htm
EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	5135	1895	1880	Peugeot Expert technical specifications	https://www.autoscout24.es/coches/datos-tecnicos/peugeot/expert/
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942	Peugeot Expert owner's manual dimensions	https://www.carmanualsonline.info/peugeot-expert-vu-2011-kezel%C3%A9si-%C3%BAtmutat%C3%B3-in-hungarian/14
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276	Peugeot Expert owner's manual dimensions	https://www.carmanualsonline.info/peugeot-expert-vu-2011-kezel%C3%A9si-%C3%BAtmutat%C3%B3-in-hungarian/14
EU-MITSUBISHI-LANCER-EVOLUTION-II-CE9A-SEDAN-4D-01	4310	1695	1420	Auto-Data Mitsubishi Lancer Evolution II	https://www.auto-data.net/en/mitsubishi-lancer-evolution-model-2861
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	4715	1800	1955	Toyota Hiace Van official model information	https://media.toyota.co.uk/toyota-hiace-van/
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	5160	1800	1955	Toyota Hiace Van official model information	https://media.toyota.co.uk/toyota-hiace-van/
EU-TOYOTA-HIACE-IV-BUS-SWB-01	4795	1800	2000	Toyota Hiace official product specification	https://toyotasverigebroschyr.com/webbroschyr/produktblad_arkiv/Hiace/hia_pf_web_0808-0.pdf
EU-TOYOTA-HIACE-IV-BUS-LWB-01	5240	1800	1995	Toyota Hiace official product specification	https://toyotasverigebroschyr.com/webbroschyr/produktblad_arkiv/Hiace/hia_pf_web_0808-0.pdf
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443	Auto-Data Volkswagen Eos model specifications	https://www.auto-data.net/en/volkswagen-eos-model-886
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444	Auto-Data Volkswagen Eos model specifications	https://www.auto-data.net/en/volkswagen-eos-model-886
EU-AUDI-R8-I-COUPE-V8-PREFL-01	4431	1904	1252	Audi R8 2007 owner manual dimensions	https://www.carmanualsonline.info/audi-r8-2007-owners-manual/?srch=dimensions
EU-AUDI-R8-I-42-COUPE-V8-FACELIFT-01	4440	1904	1252	Audi R8 technical data March 2013	https://www.ausmotive.com/downloads/Audi/R8-AU-tech-data-March2013.pdf
EU-AUDI-R8-I-42-CONVERTIBLE-V8-PREFL-01	4435	1904	1244	Audi R8 Spyder 4.2 FSI quattro technical data	https://autoinfo.jp/release/R8_Spyder_4.2FSI_my11_spec.pdf
EU-AUDI-R8-I-42-CONVERTIBLE-V8-FACELIFT-01	4440	1904	1244	Audi R8 technical data March 2013	https://www.ausmotive.com/downloads/Audi/R8-AU-tech-data-March2013.pdf
EU-PORSCHE-CAYENNE-958-SUV-PREFL-01	4846	1939	1705	Porsche 2011 Cayenne and Cayenne S official specifications	https://newsroom.porsche.com/dam/jcr%3A88587da7-01da-43c1-8dd9-8de1dd4ccd6d/2011_Cayenne_Specifications.pdf
EU-PORSCHE-CAYENNE-958-SUV-S-E-HYBRID-FACELIFT-01	4855	1939	1705	Porsche The New Cayenne official press kit	https://newsroom.porsche.com/dam/jcr%3A13b2afec-e26a-4280-8e16-06686a45d53b/Press
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543	Automobile-Catalog Cadillac BLS Wagon 2.0 T	https://www.automobile-catalog.com/car/2008/336500/cadillac_bls_wagon_2_0_t_175-hp.html
EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	4515	1725	1445	Automobile-Catalog Chevrolet Nubira-Lacetti J200 Sedan	https://www.automobile-catalog.com/car/2009/558740/chevrolet_nubira-lacetti_1_6_sx_sedan_automatic.html
EU-ABARTH-500-312-HATCHBACK-01	3657	1627	1485	Abarth 500 official press pack	https://www.media.stellantis.com/uk-en/abarth/press/abarth-500-rebirth-of-a-legend-press-pack
EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	4041	1721	1490	Abarth Grande Punto official press pack	https://www.media.stellantis.com/uk-en/abarth/press/abarth-roars-back-to-the-uk-press-pack
EU-INFINITI-G37-V36-SEDAN-4D-01	4755	1773	1469	Infiniti G37 2010 owner manual dimensions	https://www.carmanualsonline.info/infiniti-g37-2010-owners-manual/?srch=dimensions
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data Volkswagen Tiguan I 2.0 TSI 4Motion	https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tsi-200hp-automatic-4motion-8383
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data Volkswagen Tiguan I facelift 1.4 TSI BMT	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-1.4-tsi-bmt-125hp-44098
EU-VW-SHARAN-II-7N-MPV-5D-01	4854	1904	1720	Volkswagen Sharan official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/30891/sharan-brochure.pdf
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data Seat Altea facelift 2009 specifications	https://www.auto-data.net/en/seat-altea-facelift-2009-generation-4202
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535	Dodge Caliber official technical specifications	https://www.australiancar.reviews/_pdfs/Dodge_Caliber_PM_TechnicalSpecifications_200610.pdf
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498	Škoda Fabia 2011 owner manual dimensions	https://www.carmanualsonline.info/skoda-fabia-2011-2-g-5j-owner-s-manual/?srch=dimensions
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498	Škoda Fabia 2011 owner manual dimensions	https://www.carmanualsonline.info/skoda-fabia-2011-2-g-5j-owner-s-manual/?srch=dimensions
EU-SKODA-FABIA-II-RS-HATCHBACK-5D-01	4029	1642	1492	ŠKODA Fabia official UK brochure November 2011	https://blog.le-parnass.com/catalogue_pdf/skoda_fabia.pdf
EU-SKODA-FABIA-II-RS-COMBI-WAGON-5D-01	4276	1642	1494	ŠKODA Fabia official UK brochure November 2011	https://blog.le-parnass.com/catalogue_pdf/skoda_fabia.pdf
EU-SKODA-YETI-I-5L-SUV-PREFL-01	4223	1793	1691	Car Dimensions Škoda Yeti specifications	https://www.car-dimensions.com/dimensions/Skoda_Yeti/
EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	4222	1793	1691	Auto-Data Škoda Yeti facelift 2013 specifications	https://www.auto-data.net/en/skoda-yeti-facelift-2013-generation-4188
EU-JEEP-CHEROKEE-IV-KK-SUV-5D-01	4493	1839	1797	Auto-Data Jeep Cherokee IV KK specifications	https://www.auto-data.net/en/jeep-cherokee-iv-kk-generation-331
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422	Car Dimensions Alfa Romeo 159 specifications	https://www.car-dimensions.com/dimensions/alfa_romeo_159/
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422	Car Dimensions Alfa Romeo 159 specifications	https://www.car-dimensions.com/dimensions/alfa_romeo_159/
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-5D-5.7-01	4750	1870	1740	Automobile-Catalog 2009 Jeep Grand Cherokee 5.7 V8 Hemi Overland	https://www.automobile-catalog.com/car/2009/1326845/jeep_grand_cherokee_5_7_v8_hemi_overland.html
EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	4660	1880	1755	SsangYong Kyron official owner manual	https://ssangyong-club.org/manual/kyron/kyron_Rusian.pdf
EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	4660	1880	1740	SsangYong Kyron official owner manual	https://ssangyong-club.org/manual/kyron/kyron_Rusian.pdf
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data Seat Ibiza IV 1.4 five-door	https://www.auto-data.net/en/seat-ibiza-iv-1.4-85hp-13468
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428	Auto-Data Seat Ibiza IV SC 1.4	https://www.auto-data.net/en/seat-ibiza-iv-sc-1.4-85hp-44348
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428	Auto-Data Seat Ibiza IV SC facelift 2012 1.4	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.4-16v-85hp-19334
EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	4735	1780	1505	Auto-Data Subaru Legacy model specifications	https://www.auto-data.net/en/subaru-legacy-model-1844
EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	4745	1821	1506	Auto-Data Subaru Legacy V facelift 2012 specifications	https://www.auto-data.net/en/subaru-legacy-v-facelift-2012-generation-4612
EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	4775	1780	1535	Auto-Data Subaru Legacy model specifications	https://www.auto-data.net/en/subaru-legacy-model-1844
EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	4790	1780	1535	Auto-Data Subaru Legacy V Station Wagon facelift 2012 specifications	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-generation-4613
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	5048	2070	2303	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-FACELIFT-01	5075	2070	2307	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	5048	2070	2496	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-FACELIFT-01	5075	2070	2500	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	5548	2070	2499	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-FACELIFT-01	5575	2070	2499	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	5548	2070	2749	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-FACELIFT-01	5575	2070	2749	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	6198	2070	2488	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-FACELIFT-01	6225	2070	2488	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	6198	2070	2744	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-FACELIFT-01	6225	2070	2744	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-PREFL-01	5643	2070	2265	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-PREFL-01	6293	2070	2258	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-PREFL-01	6293	2070	2263	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L2-PREFL-01	5643	2070	2272	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-SRW-PREFL-01	5643	2070	2284	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-DRW-PREFL-01	5643	2070	2283	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-SRW-PREFL-01	6293	2070	2276	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-PREFL-01	6193	2070	2283	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-PREFL-01	6843	2070	2286	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-PREFL-01	6193	2070	2301	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L3-LONGOVERHANG-DRW-PREFL-01	6843	2070	2286	Renault Master official UK brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/10729-MasterVaneBrochureJuly2017.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L2-LONGOVERHANG-DRW-FACELIFT-01	6220	2070	2283	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-SINGLE-L3-LONGOVERHANG-DRW-FACELIFT-01	6870	2070	2273	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-RWD-DOUBLE-L2-LONGOVERHANG-DRW-FACELIFT-01	6220	2070	2301	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L2-FACELIFT-01	5670	2070	2265	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-SINGLE-L3-FACELIFT-01	6320	2070	2258	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-CAB-FWD-DOUBLE-L3-FACELIFT-01	6320	2070	2263	Renault Master official UK brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801	Citroën Berlingo official handbook	https://www.citroeneuropass.com.au/i/VehicleManual/Berlingo.pdf
EU-KIA-SPORTAGE-III-SL-SUV-NORACK-01	4440	1855	1635	Kia Sportage R official catalogue	https://www.kia.com/content/dam/kwcms/kr/ko/files/RSL/catalog/catalog_sportage-r.pdf
EU-KIA-SPORTAGE-III-SL-SUV-ROOFRACK-01	4440	1855	1645	Kia Sportage R official catalogue	https://www.kia.com/content/dam/kwcms/kr/ko/files/RSL/catalog/catalog_sportage-r.pdf
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-TATA-XENON-PICKUP-DOUBLE-CAB-4D-01	5125	1860	1833	Auto-Data Tata Xenon 2.2 d 140 Hp 4x4	https://www.auto-data.net/en/tata-xenon-2.2-d-140hp-4x4-27681
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	BMW 5 Series Sedan F10 official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0098606ES/146834
EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	4998	1901	1559	Auto-Data BMW 5 Series Gran Turismo F07 specifications	https://www.auto-data.net/en/bmw-5-series-gran-turismo-f07-generation-3850
EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	5004	1901	1559	Auto-Data BMW 5 Series Gran Turismo F07 LCI specifications	https://www.auto-data.net/en/bmw-5-series-gran-turismo-f07-lci-facelift-2013-generation-4262
EU-BMW-5-SERIES-F11-WAGON-5D-01	4907	1860	1462	BMW 5 Series Touring F11 official technical data; BMW 5 Series Touring F11 LCI official technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0080392FR/127666; https://www.press.bmwgroup.com/global/article/attachment/T0203606EN/294945
EU-BMW-X3-F25-SUV-5D-PREFL-01	4648	1881	1661	BMW X3 F25 official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0085745ES/131980
EU-BMW-X3-F25-SUV-5D-FACELIFT-01	4657	1881	1661	BMW X3 F25 LCI official specification sheet	https://bps.bmw.com.tw/uploads/bps/1631866697_CCvKpX.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801	Citroën Berlingo official handbook	https://www.citroeneuropass.com.au/i/VehicleManual/Berlingo.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828	Citroën Berlingo official handbook	https://www.citroeneuropass.com.au/i/VehicleManual/Berlingo.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4701-4800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ukcarline.co.uk/uploads/pds/Nissan%20Navara%20Brochure.pdf "https://www.ukcarline.co.uk/uploads/pds/Nissan%20Navara%20Brochure.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（7735 行）
- 累计尺寸组：dimension_groups_final.tsv（2968 行）

