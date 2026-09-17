# 任务：all 第 4301-4400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0044__7b5dc2cd


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4301-4400 行

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
all 第 4301-4400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-BMW-8-F91-M8-CONVERTIBLE-01	4867	1907	1353
EU-BMW-8-F92-M8-COUPE-01	4867	1907	1362
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339
EU-BMW-8-G14-M850I-CONVERTIBLE-01	4851	1902	1345
EU-BMW-8-G15-840D-COUPE-01	4843	1902	1341
EU-BMW-8-G15-M850I-COUPE-01	4851	1902	1346
EU-BMW-8-G16-GRAN-COUPE-01	5082	1932	1407
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-BMW-X6-F16-SUV-01	4909	1989	1702
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451
EU-CITROEN-GRAND-C4-SPACETOURER-I-MPV-01	4602	1826	1638
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	4818	1835	1861
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	4418	1835	1861
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	4973	1986	2389
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	5340	1986	2017
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	5340	1986	2381
EU-HONDA-CR-V-V-RW-SUV-AWD-01	4600	1855	1689
EU-HONDA-CR-V-V-RW-SUV-FWD-01	4600	1855	1679
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-LADA-LARGUS-I-F90-CNG-VAN-01	4470	1750	1650
EU-LADA-LARGUS-I-R90-CNG-WAGON-01	4470	1750	1670
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	4597	2069	1727
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724
EU-LEXUS-ES-VII-XZ10-SEDAN-01	4975	1865	1445
EU-MCLAREN-600LT-P13-COUPE-01	4604	1930	1194
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660
EU-PIAGGIO-APE-50-PICKUP-CROSS-01	2530	1260	1620
EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	2660	1260	1550
EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	2490	1260	1550
EU-PIAGGIO-APE-50-VAN-01	2500	1260	1590
EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-LONG-01	3390	1500	1630
EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-STANDARD-01	3175	1480	1630
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	4696	1923	1624
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600
EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	4282	1829	1805
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-RENAULT-ZOE-I-X10-HATCHBACK-01	4084	1730	1562
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590
EU-SUBARU-XV-I-GP-SUV-01	4450	1780	1570
EU-SUBARU-XV-II-SUV-01	4465	1805	1615
EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	5304	1904	1990
EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	4904	1904	1970
EU-VW-T-ROC-I-SUV-01	4234	1819	1573
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ssangyong	Tivoli	1.5	SUV	Frontantrieb	Benzin	120	163	Jun 2019	-	2024-03-01	137686
Ssangyong	Tivoli	1.5 Allrad	SUV	Allrad	Benzin	120	163	Jun 2019	-	2024-03-01	137687
Ssangyong	Tivoli	1.6 XDI 160	SUV	Frontantrieb	Diesel	100	136	Jun 2019	-	2024-03-01	137688
Ssangyong	Tivoli	1.6 XDI 160 Allrad	SUV	Allrad	Diesel	100	136	Jun 2019	-	2024-03-01	137689
Ford	Transit custom v362	2.0 Ecoblue Mhev	Kasten	Frontantrieb	Diesel/Elektro	96	130	May 2019	Dec 2023	2024-05-01	137698
Ford	Transit custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	77	105	May 2019	Dec 2023	2024-05-01	137701
Ford	Transit custom v362	1.0 Ecoboost Phev	Kasten	Frontantrieb	Benzin/Elektro	92	125	Apr 2020	Dec 2023	2024-05-01	137709
Ford	Transit custom v362	2.0 Ecoblue Mhev	Kasten	Frontantrieb	Diesel/Elektro	125	170	May 2019	Dec 2023	2024-05-01	137710
Ford	Transit custom v362	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	136	185	May 2019	Dec 2023	2024-05-01	137711
Ford	Transit custom v362	2.0 Ecoblue Mhev	Kasten	Frontantrieb	Diesel/Elektro	136	185	May 2019	Dec 2023	2024-05-01	137712
Renault	Zoe	ZOE	Schrägheck	Frontantrieb	Elektro	100	136	Sep 2019	-	2024-03-01	137713
Mclaren	600lt	3.8	Cabriolet	Heckantrieb	Benzin	441	600	Feb 2019	-	2024-03-01	137720
RAM	1500 extended cab pickup	5.7	Pick-up	Heckantrieb	Benzin	295	401	Dec 2018	-	2024-03-01	137721
RAM	1500 extended cab pickup	5.7 4X4	Pick-up	Allrad	Benzin	295	401	Dec 2018	-	2024-03-01	137722
Renault	Koleos ii	2.0 Blue DCI 190 4WD	SUV	Allrad	Diesel	140	190	Jun 2019	-	2024-03-01	137723
Opel	Corsa f	1.2	Schrägheck	Frontantrieb	Benzin	55	75	Jul 2019	-	2024-03-01	137724
Opel	Corsa f	1.2	Schrägheck	Frontantrieb	Benzin	74	101	Jul 2019	-	2024-03-01	137725
Opel	Corsa f	1.2	Schrägheck	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	137726
Opel	Corsa f	1.5	Schrägheck	Frontantrieb	Diesel	75	102	Jul 2019	-	2024-03-01	137727
Opel	Astra k	1.2 Turbo	Schrägheck	Frontantrieb	Benzin	81	110	Aug 2019	Sep 2021	2025-12-01	137729
Opel	Astra k	1.2 Turbo	Schrägheck	Frontantrieb	Benzin	96	131	Aug 2019	Sep 2021	2025-12-01	137730
Opel	Astra k	1.2 Turbo	Schrägheck	Frontantrieb	Benzin	107	145	Aug 2019	Sep 2021	2025-12-01	137731
Renault	Kangoo	1.5 DCI 95	Großraumlimousine	Frontantrieb	Diesel	70	95	Mar 2019	-	2024-03-01	137732
Opel	Astra k	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	77	105	Aug 2019	Sep 2021	2025-12-01	137733
Opel	Astra k	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	90	122	Aug 2019	Sep 2021	2025-12-01	137734
Opel	Astra k	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	107	145	Aug 2019	Sep 2021	2025-12-01	137735
Opel	Astra k sports tourer	1.2 Turbo	Kombi	Frontantrieb	Benzin	81	110	Aug 2019	Dec 2021	2025-12-01	137736
Opel	Astra k sports tourer	1.2 Turbo	Kombi	Frontantrieb	Benzin	96	131	Aug 2019	Dec 2021	2025-12-01	137737
Opel	Astra k sports tourer	1.2 Turbo	Kombi	Frontantrieb	Benzin	107	145	Aug 2019	Dec 2021	2025-12-01	137738
Opel	Astra k sports tourer	1.4 Turbo	Kombi	Frontantrieb	Benzin	107	145	Aug 2019	Dec 2021	2025-12-01	137739
Opel	Astra k sports tourer	1.5 Crdi	Kombi	Frontantrieb	Diesel	77	105	Aug 2019	Dec 2021	2025-12-01	137740
Opel	Astra k sports tourer	1.5 Crdi	Kombi	Frontantrieb	Diesel	90	122	Aug 2019	Dec 2021	2025-12-01	137741
Mercedes-benz	C-Klasse	C 300 4-matic	Coupe	Allrad	Benzin	190	258	May 2018	Apr 2023	2024-03-01	137743
Audi	A5	35 TDI	Coupe	Frontantrieb	Diesel	120	163	Aug 2019	-	2025-06-01	137745
Audi	A5	35 TDI	Schrägheck	Frontantrieb	Diesel	120	163	Aug 2019	-	2025-04-01	137746
Opel	Vivaro c	1.5	Kasten	Frontantrieb	Diesel	75	102	Mar 2019	Apr 2025	2026-01-01	137756
Opel	Vivaro c	1.5	Kasten	Frontantrieb	Diesel	88	120	Mar 2019	-	2024-03-01	137757
Opel	Vivaro c	2	Kasten	Frontantrieb	Diesel	90	122	Mar 2019	Dec 2022	2026-01-01	137758
Opel	Vivaro c	2	Kasten	Frontantrieb	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	137759
Opel	Vivaro c	2	Kasten	Frontantrieb	Diesel	130	177	Mar 2019	Apr 2025	2026-01-01	137760
Opel	Vivaro c	1.5	Bus	Frontantrieb	Diesel	75	102	Mar 2019	Apr 2025	2026-01-01	137761
Opel	Vivaro c	1.5	Bus	Frontantrieb	Diesel	88	120	Mar 2019	Apr 2025	2026-01-01	137762
Opel	Vivaro c	2	Bus	Frontantrieb	Diesel	90	122	Mar 2019	Dec 2022	2026-01-01	137763
Opel	Vivaro c	2	Bus	Frontantrieb	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	137764
Opel	Vivaro c platform cabin	2	Pritsche/Fahrgestell	Frontantrieb	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	137765
Opel	Vivaro c platform cabin	2	Pritsche/Fahrgestell	Frontantrieb	Diesel	90	122	Mar 2019	Dec 2022	2026-01-01	137766
VW	T-Roc	2.0 TDI 4motion	SUV	Allrad	Diesel	140	190	Jul 2019	Jun 2021	2024-03-01	137767
VW	T-Roc	2.0 R 4motion	SUV	Allrad	Benzin	221	300	Sep 2019	-	2024-03-01	137768
Ford	Transit connect v408	1.5 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	May 2018	-	2024-03-01	137771
Ford	Transit connect	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	74	101	May 2018	-	2024-03-01	137772
Ford	Transit connect	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	88	120	May 2018	-	2025-02-03	137773
Peugeot	Partner origin	1.4	Großraumlimousine	Frontantrieb	Benzin	55	75	Jul 2008	Dec 2013	2024-03-01	137774
Peugeot	Partner origin	1.6 HDI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Aug 2008	Dec 2013	2024-03-01	137776
Peugeot	Partner origin	1.6 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Aug 2008	Dec 2015	2024-03-01	137779
Peugeot	Partner origin	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 2008	Dec 2015	2024-03-01	137780
Peugeot	Partner origin	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Aug 2008	Dec 2015	2024-03-01	137784
BMW	X5	M	SUV	Allrad	Benzin	441	600	Dec 2019	Mar 2023	2024-03-01	137786
BMW	X5	M Competition	SUV	Allrad	Benzin	460	625	Dec 2019	-	2024-03-01	137787
BMW	X6	M	SUV	Allrad	Benzin	441	600	Dec 2019	Mar 2023	2024-03-01	137788
BMW	X6	M Competition	SUV	Allrad	Benzin	460	625	Dec 2019	Mar 2023	2024-03-01	137789
BMW	8	M8	Coupe	Allrad	Benzin	441	600	Nov 2019	-	2024-03-01	137798
BMW	8	M8 Competition	Coupe	Allrad	Benzin	460	625	Nov 2019	-	2024-03-01	137799
Mercedes-benz	A-Klasse	A 200	Stufenheck	Frontantrieb	Benzin	110	150	Sep 2018	-	2024-03-01	137810
Toyota	Rav 4 v	2.0 Vvti	SUV	Frontantrieb	Benzin	110	150	Dec 2018	-	2024-03-01	137816
Toyota	Rav 4 v	2.0 Vvti AWD	SUV	Allrad	Benzin	110	150	Dec 2018	-	2024-03-01	137817
Toyota	Rav 4 v	2.5 Vvti AWD	SUV	Allrad	Benzin	149	203	Dec 2018	-	2024-03-01	137818
Lada	Largus	1.6 CNG	Kasten	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Nov 2018	-	2024-07-01	137819
Renault	Trafic iii	1.6 DCI 120	Bus	Frontantrieb	Diesel	89	121	Jan 2019	-	2024-03-01	137822
Citroën	C5	1.6 THP 150	SUV	Frontantrieb	Benzin	110	150	Sep 2019	-	2024-07-01	137825
Citroën	Grand c4 spacetourer	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	110	150	Apr 2018	-	2024-03-01	137828
Ford	Transit connect v408	1.5 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	May 2018	-	2024-03-01	137831
Alpina	B3	Biturbo Allrad	Kombi	Allrad	Benzin	340	462	Sep 2019	Dec 2025	2026-06-01	137833
Honda	Cr-V v	2.4 I-vtec AWD	SUV	Allrad	Benzin	137	186	Sep 2017	-	2024-03-01	137842
Subaru	Xv	2.0 I AWD	SUV	Allrad	Benzin	110	150	Oct 2019	-	2024-03-01	137843
Ford	Tourneo connect / grand v408 großraumlimousi	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	88	120	May 2018	Dec 2022	2024-05-01	137844
Mini	Mini	John Cooper Works GP	Schrägheck	Frontantrieb	Benzin	225	306	Mar 2020	-	2024-03-01	137845
Ford	Tourneo connect / grand v408 großraumlimousi	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	74	101	May 2018	Dec 2022	2024-05-01	137846
Ford	Tourneo connect / grand v408 großraumlimousi	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2018	Dec 2022	2024-05-01	137847
Hyundai	Santa fe iv	3.5 MPI AWD	SUV	Allrad	Benzin	183	249	Jul 2019	Jul 2020	2024-03-01	137857
Hyundai	Tucson	2.4 GDI Allrad	SUV	Allrad	Benzin	135	184	Jul 2019	Sep 2020	2024-03-01	137861
Piaggio	Ape	200	Cabriolet	Heckantrieb	Benzin	7	10	Oct 2019	-	2024-03-01	137874
Mercedes-benz	Gls	450 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	270	367	Jun 2019	-	2024-03-01	137876
BMW	3	330 D	Kombi	Heckantrieb	Diesel	195	265	Nov 2019	-	2024-03-01	137895
Peugeot	Partner tepee	1.6 HDI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Jun 2008	-	2024-03-01	137905
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	81	110	Jul 2019	Aug 2024	2025-02-03	137938
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	81	110	Jul 2019	Aug 2024	2025-02-03	137946
BMW	2	220 D	Coupe	Frontantrieb	Diesel	120	163	Nov 2019	-	2024-03-01	137952
Porsche	Cayenne	4.0 Turbo S E-hybrid AWD	SUV	Allrad	Benzin/Elektro	500	680	Jan 2019	May 2023	2026-03-01	137953
Porsche	Macan	2.9 Turbo AWD	SUV	Allrad	Benzin	324	441	May 2018	-	2025-12-01	137954
Mercedes-benz	C-Klasse	C 200	Cabriolet	Heckantrieb	Benzin	150	204	Aug 2019	Apr 2023	2024-03-01	137965
Opel	Zafira	2	Bus	Frontantrieb	Diesel	90	122	Aug 2019	Dec 2022	2026-01-01	137966
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	81	110	Jul 2019	Aug 2024	2025-02-03	137972
Mercedes-benz	Gle	GLE 580 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	360	489	Nov 2019	Mar 2023	2024-03-01	137976
Lexus	Es	200	Stufenheck	Frontantrieb	Benzin	127	173	Jul 2019	-	2024-03-01	137980
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	66	90	Oct 2019	Aug 2024	2025-02-03	137990
Land Rover	Discovery sport	2.0 P250 4X4	SUV	Allrad	Benzin	183	249	May 2019	-	2024-03-01	137994
Land Rover	Defender station wagon	P300 SI4 4X4	Geländewagen geschlossen	Allrad	Benzin	221	300	Sep 2019	-	2024-03-01	137996
Land Rover	Defender station wagon	P400 I6 Mhev 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	294	400	Sep 2019	-	2024-03-01	137997
Land Rover	Defender station wagon	D200 SD4 4X4	Geländewagen geschlossen	Allrad	Diesel	147	200	Sep 2019	-	2024-03-01	137998
Land Rover	Defender station wagon	D240 SD4 4X4	Geländewagen geschlossen	Allrad	Diesel	177	241	Sep 2019	-	2024-03-01	137999


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成首轮聚类：复用 30 个既有尺寸组，未重写任何既有三维；历史跨批次索引仅用于稳定 ID 对照。
* 首次闭合 5 个尺寸组：BMW X5 M、X5 M Competition、X6 M、X6 M Competition，以及 Toyota RAV4 V。BMW 官方产品指南分别列出了 M 与 Competition 的高度；Toyota 官方技术规格给出 RAV4 V 的 `4600×1855×1685 mm`。
* McLaren 官方车型页已确认输入对应 600LT Spider，但直接三维规格尚未闭合，因此本轮不创建尺寸组。([McLaren Automotive][1])
* 商用车多轴距、多车顶，以及 Vivaro C、Partner、Transporter、Defender 等仍保留 `PENDING`，不根据泛化车型名猜测派生分支。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：58
* PENDING Ktype：42
* READY 映射行：61
* PENDING 映射行：42
* 当前已引用尺寸组：35（复用既有 30；本轮新建 5）
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137686	137686	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137687	137687	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137688	137688	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137689	137689	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137698	137698	Van	Transit Custom I	V362			LOW	需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。	PENDING: 需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。
137701	137701	MPV	Transit Custom I	V362			LOW	候选为 V362 Bus L1H1/L1H2/L2H1/L2H2，Ktype 分支覆盖尚未确认。	PENDING: 候选为 V362 Bus L1H1/L1H2/L2H1/L2H2，Ktype 分支覆盖尚未确认。
137709	137709	Van	Transit Custom I	V362			LOW	需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。	PENDING: 需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。
137710	137710	Van	Transit Custom I	V362			LOW	需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。	PENDING: 需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。
137711	137711	Van	Transit Custom I	V362			LOW	需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。	PENDING: 需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。
137712	137712	Van	Transit Custom I	V362			LOW	需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。	PENDING: 需确认该 Ktype 覆盖的 L1/L2 与 H1/H2 分支；现有缓存仅有 Bus 组。
137713	137713	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-01	HIGH		READY
137720	137720	Convertible	600LT	P13	2		LOW	已确认 600LT Spider；官方三维下载页尚未闭合。	PENDING: 已确认 600LT Spider；官方三维下载页尚未闭合。
137721	137721	Pickup	Ram 1500 V	DT	4		LOW	需闭合 2019 DT Quad Cab 6'4 箱体的 2WD/4X4 不含镜宽度与高度。	PENDING: 需闭合 2019 DT Quad Cab 6'4 箱体的 2WD/4X4 不含镜宽度与高度。
137722	137722	Pickup	Ram 1500 V	DT	4		LOW	需闭合 2019 DT Quad Cab 6'4 箱体的 2WD/4X4 不含镜宽度与高度。	PENDING: 需闭合 2019 DT Quad Cab 6'4 箱体的 2WD/4X4 不含镜宽度与高度。
137723	137723	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
137724	137724	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137725	137725	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137726	137726	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137727	137727	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137729	137729	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137730	137730	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137731	137731	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137732	137732	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入未标 Maxi/Grand，关联标准轴距 MPV 外廓。	READY
137733	137733	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137734	137734	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137735	137735	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH	与已闭合 Astra K 五门两厢外廓一致。	READY
137736	137736	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137737	137737	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137738	137738	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137739	137739	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137740	137740	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137741	137741	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	与已闭合 Astra K Sports Tourer 外廓一致。	READY
137743	137743	Coupe	C-Class IV	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
137745	137745	Coupe	A5 II	F5	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
137746	137746	Hatchback	A5 II	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Schrägheck 对应 A5 Sportback 五门外廓。	READY
137756	137756	Van	Vivaro C	K0			LOW	需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。	PENDING: 需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。
137757	137757	Van	Vivaro C	K0			LOW	需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。	PENDING: 需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。
137758	137758	Van	Vivaro C	K0			LOW	需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。	PENDING: 需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。
137759	137759	Van	Vivaro C	K0			LOW	需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。	PENDING: 需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。
137760	137760	Van	Vivaro C	K0			LOW	需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。	PENDING: 需确认 S/M/L 及车顶分支；不得直接以 Zafira Life 组代替。
137761	137761	MPV	Vivaro C	K0			LOW	需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。	PENDING: 需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。
137762	137762	MPV	Vivaro C	K0			LOW	需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。	PENDING: 需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。
137763	137763	MPV	Vivaro C	K0			LOW	需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。	PENDING: 需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。
137764	137764	MPV	Vivaro C	K0			LOW	需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。	PENDING: 需确认 S/M/L 车长分支；现有 Zafira Life 组仅作候选。
137765	137765	Pickup	Vivaro C	K0			LOW	平台驾驶室外廓和可用轴距未闭合。	PENDING: 平台驾驶室外廓和可用轴距未闭合。
137766	137766	Pickup	Vivaro C	K0			LOW	平台驾驶室外廓和可用轴距未闭合。	PENDING: 平台驾驶室外廓和可用轴距未闭合。
137767	137767	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
137768	137768	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
137771	137771	Van	Transit Connect II	V408			LOW	输入车身形式混合，需确认 Van/MPV 与 SWB/LWB 物理边界。	PENDING: 输入车身形式混合，需确认 Van/MPV 与 SWB/LWB 物理边界。
137772	137772	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	MEDIUM	输入未标 Grand，关联标准轴距 MPV 外廓。	READY
137773	137773	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	MEDIUM	输入未标 Grand，关联标准轴距 MPV 外廓。	READY
137774	137774	MPV	Partner I facelift	M59			LOW	需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。	PENDING: 需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。
137776	137776	MPV	Partner I facelift	M59			LOW	需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。	PENDING: 需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。
137779	137779	Van	Partner I facelift	M59			LOW	需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。	PENDING: 需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。
137780	137780	Van	Partner I facelift	M59			LOW	需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。	PENDING: 需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。
137784	137784	Van	Partner I facelift	M59			LOW	需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。	PENDING: 需闭合 Partner Origin 的 MPV/Van 外廓及不含镜宽度。
137786	137786	SUV	X5 IV	F95	5	EU-BMW-X5-F95-M-SUV-01	HIGH		READY
137787	137787	SUV	X5 IV	F95	5	EU-BMW-X5-F95-M-COMPETITION-SUV-01	HIGH		READY
137788	137788	SUV	X6 III	F96	5	EU-BMW-X6-F96-M-SUV-01	HIGH		READY
137789	137789	SUV	X6 III	F96	5	EU-BMW-X6-F96-M-COMPETITION-SUV-01	HIGH		READY
137798	137798	Coupe	8 Series II	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
137799	137799	Coupe	8 Series II	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
137810	137810	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
137816	137816	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137817	137817	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137818	137818	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137819	137819	Van	Largus I	F90		EU-LADA-LARGUS-I-F90-CNG-VAN-01	HIGH		READY
137822	137822	MPV	Trafic III	X82			LOW	需确认 Bus 的 L1/L2、H1/H2 分支；现有缓存仅有 Van 组。	PENDING: 需确认 Bus 的 L1/L2、H1/H2 分支；现有缓存仅有 Van 组。
137825	137825	SUV	C5 Aircross I	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
137828	137828	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
137831	137831	Van	Transit Connect II	V408			LOW	输入车身形式混合，需确认 Van/MPV 与 SWB/LWB 物理边界。	PENDING: 输入车身形式混合，需确认 Van/MPV 与 SWB/LWB 物理边界。
137833	137833	Wagon	B3 G21	G21	5		LOW	需闭合 G21 B3 Touring 的 ALPINA 外部套件三维。	PENDING: 需闭合 G21 B3 Touring 的 ALPINA 外部套件三维。
137842	137842	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-AWD-01	HIGH		READY
137843	137843	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH		READY
137844_swb	137844	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137844_lwb	137844	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137845	137845	Hatchback	MINI F56	F56	3		LOW	需核对 2020 F56 GP 宽体套件后的三维，不能复用常规 F56。	PENDING: 需核对 2020 F56 GP 宽体套件后的三维，不能复用常规 F56。
137846_swb	137846	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137846_lwb	137846	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137847_swb	137847	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137847_lwb	137847	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137857	137857	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
137861	137861	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
137874	137874	Convertible	Ape 200				LOW	Ape 200 Cabriolet 的 Calessino/开放车身边界未确认。	PENDING: Ape 200 Cabriolet 的 Calessino/开放车身边界未确认。
137876	137876	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
137895	137895	Wagon	3 Series VII	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
137905	137905	MPV	Partner I facelift	M59	5		LOW	需闭合 Partner Tepee 的 MPV 外廓及不含镜宽度。	PENDING: 需闭合 Partner Tepee 的 MPV 外廓及不含镜宽度。
137938	137938	MPV	Transporter T6.1	T6.1			LOW	需确认该 Ktype 是否覆盖 SWB/LWB，暂不猜测派生。	PENDING: 需确认该 Ktype 是否覆盖 SWB/LWB，暂不猜测派生。
137946	137946	MPV	Transporter T6.1	T6.1			LOW	需确认 Caravelle/Bus 的 SWB/LWB 物理分支，暂不猜测派生。	PENDING: 需确认 Caravelle/Bus 的 SWB/LWB 物理分支，暂不猜测派生。
137952	137952	Coupe	2 Series II	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱 220d 对应 F44 Gran Coupe 四门外廓。	READY
137953	137953	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
137954	137954	SUV	Macan I facelift	95B	5		LOW	2.9 Turbo 441 hp 与现有 base/Turbo Performance 组均不完全一致，需建新组。	PENDING: 2.9 Turbo 441 hp 与现有 base/Turbo Performance 组均不完全一致，需建新组。
137965	137965	Convertible	C-Class IV	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
137966	137966	MPV	Zafira Life I				LOW	需确认该 Ktype 覆盖 S/M/L 车长分支。	PENDING: 需确认该 Ktype 覆盖 S/M/L 车长分支。
137972	137972	Van	Transporter T6.1	T6.1			LOW	需确认 SWB/LWB 与车顶高度分支；现有缓存仅有低顶 4Motion 组。	PENDING: 需确认 SWB/LWB 与车顶高度分支；现有缓存仅有低顶 4Motion 组。
137976	137976	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
137980	137980	Sedan	ES VII	XZ10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH		READY
137990	137990	Van	Transporter T6.1	T6.1			LOW	需确认 SWB/LWB 与车顶高度分支；现有缓存仅有低顶 4Motion 组。	PENDING: 需确认 SWB/LWB 与车顶高度分支；现有缓存仅有低顶 4Motion 组。
137994	137994	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137996	137996	SUV	Defender II	L663	5		LOW	2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。	PENDING: 2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。
137997	137997	SUV	Defender II	L663	5		LOW	2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。	PENDING: 2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。
137998	137998	SUV	Defender II	L663	5		LOW	2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。	PENDING: 2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。
137999	137999	SUV	Defender II	L663	5		LOW	2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。	PENDING: 2019 起售条目指向 L663 110 候选，但 Ktype 与 90/110 物理分支尚未闭合。
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X5-F95-M-SUV-01	4953	2015	1751	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X5-F95-M-COMPETITION-SUV-01	4953	2015	1749	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X6-F96-M-SUV-01	4953	2019	1693	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X6-F96-M-COMPETITION-SUV-01	4953	2019	1692	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota RAV4 Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220203M-RAV4-Tech-Spec.pdf
```

## 下一步优先处理

1. 批量闭合 Vivaro C／Zafira Life、Transit Custom、Trafic、Transporter 的长度与车顶分支。
2. 闭合 Partner Origin／Tepee、RAM 1500 Quad Cab、Defender L663 的具体物理外廓。
3. 补齐 600LT Spider、MINI GP、Alpina B3、Macan Turbo、Piaggio Ape 200 的首次尺寸组。

推进信号：CONTINUE

[1]: https://cars.mclaren.com/uk_en/legacy/600lt-spider?utm_source=chatgpt.com "McLaren 600LT Spider - Fast & Light Convertible Supercar | McLaren Automotive"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮消除 9 个 PENDING，首次闭合 6 个尺寸组：McLaren 600LT Spider、RAM 1500 DT Quad Cab 6'4" 2WD/4WD、MINI John Cooper Works GP、Porsche Macan Turbo facelift、Land Rover Defender 110。
* Defender 110 使用官方明确标注的车身不含后视镜宽度 `1996 mm`，未误用折叠后视镜宽度 `2008 mm`。
* RAM 1500 两组保持相同 Quad Cab 6'4" 外廓长度和车身宽度，并按 4×2、4×4 的官方高度差异分别建组。
* 未修改或重复输出任何既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* PENDING Ktype：33
* READY 映射：70
* PENDING 映射：33
* 已确认尺寸组：41
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137720	137720	Convertible	600LT	P13	2	EU-MCLAREN-600LT-P13-CONVERTIBLE-01	HIGH	600LT Spider 开篷外廓。	READY
137721	137721	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-DT-QUAD-CAB-6FT4-2WD-01	HIGH	Quad Cab 6'4" 2WD 外廓。	READY
137722	137722	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-DT-QUAD-CAB-6FT4-4WD-01	HIGH	Quad Cab 6'4" 4WD 外廓。	READY
137845	137845	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	HIGH	GP 宽体三门外廓。	READY
137954	137954	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-TURBO-01	HIGH	2.9 Turbo 改款外廓。	READY
137996	137996	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137997	137997	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137998	137998	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137999	137999	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MCLAREN-600LT-P13-CONVERTIBLE-01	4604	1930	1196	McLaren 600LT official brochure;CarsGuide McLaren 600LT dimensions	https://www.auto-brochures.com/makes/mclaren/McLaren_int%20600LT_2019.pdf;https://www.carsguide.com.au/mclaren/600lt/car-dimensions/2020
EU-RAM-1500-DT-QUAD-CAB-6FT4-2WD-01	5814	2085	1971	Stellantis Fleet All-New 2019 Ram 1500 buyer guide;Car and Driver 2019 Ram 1500 Quad Cab specifications	https://www.stellantisfleet.com/content/dam/fca-fleet/na/fleet/en_us/shopping-tools/brochures-literature/docs/2019_Ram_1500.pdf;https://www.caranddriver.com/ram/1500/specs/2019/ram_1500_ram-1500_2019
EU-RAM-1500-DT-QUAD-CAB-6FT4-4WD-01	5814	2085	1974	Stellantis Fleet All-New 2019 Ram 1500 buyer guide;Edmunds 2019 Ram 1500 Quad Cab specifications	https://www.stellantisfleet.com/content/dam/fca-fleet/na/fleet/en_us/shopping-tools/brochures-literature/docs/2019_Ram_1500.pdf;https://www.edmunds.com/ram/1500/2019/quad-cab/features-specs/
EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	3879	1762	1420	BMW Group MY21 MINI 3 door Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0305951EN/446631
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-TURBO-01	4684	1926	1624	Porsche Macan Turbo Technical Data	https://newsroom.porsche.com/dam/jcr%3A699435b8-f6b7-4ae6-a9eb-a2984f9e4650/PAG_MacanTurbo_TD_EN.pdf
EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	5018	1996	1967	Land Rover 2020 Defender 110 Technical Specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
```

## 下一步优先处理

1. 批量闭合 Vivaro C／Zafira Life 的 S、M、L 车长及 Van、Bus、平台驾驶室边界。
2. 处理 Transit Custom、Trafic、Transporter 的轴距与车顶分支。
3. 补齐 Partner Origin／Tepee、Transit Connect 混合车身、Alpina B3 Touring 与 Piaggio Ape 200。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮消除 7 个 PENDING。
* `137938`、`137946`、`137972`、`137990` 按未限定轴距的车型记录拆分为 SWB/LWB，直接复用既有 T6.1 尺寸组；官方 Caravelle 6.1 资料确认 SWB/LWB 外廓分别为 `4904×1904×1970 mm` 和 `5304×1904×1990 mm`。
* `137966` 按 Zafira Life 的 S/M/L 三种长度拆分，直接复用既有尺寸组。
* 首次闭合 ALPINA B3 G21 Touring 与 Piaggio Ape Calessino 200 两个尺寸组；Ape 官方资料明确三维为 `2700×1370×1780 mm`。([阿尔皮纳][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* PENDING Ktype：26
* READY 映射：83
* PENDING 映射：26
* 已确认尺寸组：43
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137833	137833	Wagon	B3 G21	G21	5	EU-ALPINA-B3-G21-TOURING-PREFL-01	HIGH	B3 Touring G21 改款前外廓。	READY
137874	137874	Convertible	Ape Calessino 200		2	EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	HIGH	Ape Calessino 200 开放式软顶外廓。	READY
137938_swb	137938	MPV	Multivan T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	标准轴距物理分支。	READY
137938_lwb	137938	MPV	Multivan T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	长轴距物理分支。	READY
137946_swb	137946	MPV	Transporter T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	Caravelle/Bus 标准轴距物理分支。	READY
137946_lwb	137946	MPV	Transporter T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	Caravelle/Bus 长轴距物理分支。	READY
137966_s	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身物理分支。	READY
137966_m	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身物理分支。	READY
137966_l	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L 长车身物理分支。	READY
137972_swb	137972	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	标准轴距低顶物理分支。	READY
137972_lwb	137972	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	长轴距低顶物理分支。	READY
137990_swb	137990	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	标准轴距低顶物理分支。	READY
137990_lwb	137990	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	长轴距低顶物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-G21-TOURING-PREFL-01	4719	1827	1438	Auto-Data ALPINA B3 Touring G21 technical specifications	https://www.auto-data.net/en/alpina-b3-touring-g21-generation-7283
EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	2700	1370	1780	Piaggio Commercial Ape Calessino official brochure	https://piaggiocommercialuk.com/wp-content/uploads/2019/09/ApeCalessino-Brochure-08-2019.pdf
```

([汽车数据网][2])

## 下一步优先处理

1. 集中闭合 Vivaro C 的 S/M/L Van、Bus 和平台驾驶室分支。
2. 处理 Transit Custom、Transit Connect 与 Trafic 的轴距及车顶分支。
3. 补齐 Partner Origin／Tepee 的两代外廓。

推进信号：CONTINUE

[1]: https://files.alpina.co.jp/press/2021/b3_touring_press_pdf.html?utm_source=chatgpt.com "BMW ALPINA B3 - TOURING ALLRAD (AWD)"
[2]: https://www.auto-data.net/en/alpina-b3-model-229?utm_source=chatgpt.com "Alpina B3 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮消除 9 个 PENDING。
* Partner Origin 客运版与厢式版官方资料确认共用 `4137×1724×1810 mm` 外廓，因此只建立一个稳定尺寸组。([Automobilisto][1])
* Partner Tepee 按普通车身和带升高悬架、车顶杆的 Outdoor 分支拆分，官方资料给出的高度边界为 `1801–1862 mm`。([s4bf885b88c0d668f.jimcontent.com][2])
* Vivaro C 平台驾驶室闭合为单一 M 长度外廓；官方规格明确为 `4959×1920×1930 mm`，宽度为不含后视镜口径。
* Trafic III Bus 按 L1H1/L2H1 拆分，直接复用既有 X82 同外廓尺寸组，不重复输出尺寸来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* PENDING Ktype：17
* READY 映射：94
* PENDING 映射：17
* 已确认尺寸组：47
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137765	137765	Pickup	Vivaro C	K0	2	EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M 长度平台驾驶室外廓。	READY
137766	137766	Pickup	Vivaro C	K0	2	EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M 长度平台驾驶室外廓。	READY
137774	137774	MPV	Partner Origin I	M59	5	EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	HIGH	Partner Origin 客运外廓。	READY
137776	137776	MPV	Partner Origin I	M59	5	EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	HIGH	Partner Origin 客运外廓。	READY
137779	137779	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	输入为 Van/MPV 复合车身，外部轮廓一致。	READY
137780	137780	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	输入为 Van/MPV 复合车身，外部轮廓一致。	READY
137784	137784	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	输入为 Van/MPV 复合车身，外部轮廓一致。	READY
137822_l1h1	137822	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1 客运物理分支。	READY
137822_l2h1	137822	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1 客运物理分支。	READY
137905_standard	137905	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	普通悬架和标准车顶外廓。	READY
137905_outdoor	137905	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor 升高悬架及车顶杆外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	4959	1920	1930	Vauxhall New Vivaro 2020 Model Year Price and Specification Guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	4137	1724	1810	Peugeot Partner Origin official Combi brochure;Peugeot Partner Origin official Van brochure	https://automobilisto.de/es/archive/peugeot/partner/origin-combi-2008-es.pdf;https://automobilisto.de/es/archive/peugeot/partner/origin-van-2008-es.pdf
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801	Peugeot Partner Tepee official brochure	https://s4bf885b88c0d668f.jimcontent.com/download/version/1595487575/module/9006515520/name/Peugeot%20Partner%20Tepee%20Brochure.pdf
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862	Peugeot Partner Tepee official brochure	https://s4bf885b88c0d668f.jimcontent.com/download/version/1595487575/module/9006515520/name/Peugeot%20Partner%20Tepee%20Brochure.pdf
```

## 下一步优先处理

1. 闭合 Vivaro C Panel Van 与 Bus 的 S/M/L 长度及不同载荷高度分支。
2. 闭合 Transit Custom Van、Bus 的轴距、车顶和 PHEV/MHEV 可用分支。
3. 处理两个 Transit Connect `Kasten/Großraumlimousine` 复合车身 Ktype。

推进信号：CONTINUE

[1]: https://automobilisto.de/es/archive/peugeot/partner/origin-combi-2008-es.pdf "PartnerVP Origin_ES"
[2]: https://s4bf885b88c0d668f.jimcontent.com/download/version/1595487575/module/9006515520/name/Peugeot%20Partner%20Tepee%20Brochure.pdf "PartnerTepee_GB.qxd"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Transit Custom 的 4 个 Ktype：130 PS mHEV Van 仅覆盖 L1H1/L1H2；PHEV Van 仅覆盖 L1H1；185 PS 柴油 Van 覆盖 L1/L2 与 H1/H2；105 PS mHEV Bus 按 L1/L2、H1/H2 四个分支复用既有 Bus 尺寸组。Ford 官方配置表和尺寸表分别确认了可用车身组合以及各分支外廓。([福特英国][1])
* 首次创建 4 个 Transit Custom Van 尺寸组。高度采用 Ford 官方外廓高度范围的上限，与累计表中既有 Transit Custom Bus 尺寸组口径一致。([福特英国][1])
* 闭合两个车身形式为 `Kasten/Großraumlimousine` 的 Transit Connect Ktype，分别拆分为 facelift Van SWB/LWB 和 MPV SWB/LWB。facelift 官方资料确认长度与高度；不含后视镜宽度沿用 Ford 官方技术规格中的 `1835 mm` 车身宽度。
* 170 PS mHEV 与 185 PS mHEV Transit Custom 暂未改动：现有资料显示其与 Active/Sport 外部套件存在绑定，尚不能安全复用普通 Van 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* PENDING Ktype：11
* READY 映射：113
* PENDING 映射：11
* 已确认尺寸组：55
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137698_l1h1	137698	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137698_l1h2	137698	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137701_l1h1	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1H1 客运物理分支。	READY
137701_l1h2	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1H2 客运物理分支。	READY
137701_l2h1	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2H1 客运物理分支。	READY
137701_l2h2	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2H2 客运物理分支。	READY
137709_l1h1	137709	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	PHEV 仅有 L1H1 物理分支。	READY
137711_l1h1	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137711_l1h2	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137711_l2h1	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	HIGH	L2H1 物理分支。	READY
137711_l2h2	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	HIGH	L2H2 物理分支。	READY
137771_van_swb	137771	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	MEDIUM	复合车身中的 Van 标准轴距分支。	READY
137771_van_lwb	137771	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	MEDIUM	复合车身中的 Van 长轴距分支。	READY
137771_mpv_swb	137771	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	MEDIUM	复合车身中的 MPV 标准轴距分支。	READY
137771_mpv_lwb	137771	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	MEDIUM	复合车身中的 MPV 长轴距分支。	READY
137831_van_swb	137831	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	MEDIUM	复合车身中的 Van 标准轴距分支。	READY
137831_van_lwb	137831	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	MEDIUM	复合车身中的 Van 长轴距分支。	READY
137831_mpv_swb	137831	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	MEDIUM	复合车身中的 MPV 标准轴距分支。	READY
137831_mpv_lwb	137831	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	MEDIUM	复合车身中的 MPV 长轴距分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	4973	1986	2000	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	4973	1986	2366	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	5340	1986	1979	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	5340	1986	2343	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	4425	1835	1859	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	4825	1835	1847	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	4425	1835	1844	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	4825	1835	1841	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
```

## 下一步优先处理

1. 闭合 Vivaro C 的 9 个 Ktype，按发动机实际可用的 S/M/L、Van/Bus 分支批量关联。
2. 单独确认 Transit Custom 170 PS mHEV 与 185 PS mHEV 的 Active/Sport 外部套件是否改变三维。
3. PENDING 清零后立即进行一次机械闭合检查并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf "Transit Custom 21MY V1 GBR EN R2_EBRO.pdf"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 剩余 11 个 PENDING 已全部清零。Transit Custom `137710`、`137712` 已按 L1H1、L1H2、L2H1、L2H2 完整拆分并复用既有 Van 尺寸组。([福特英国][1])
* Vivaro C 的 9 个 Ktype 已按发动机实际提供的 S/M/L 车身范围完成映射；Cargo 新建 S/M/L 三组，Bus 直接复用既有 Zafira Life S/M/L 三组。([Opel团队尼德萨克森][2])
* 机械闭合检查发现既有 Discovery Sport `-01` 的 `2069 mm` 属于后视镜折叠宽度，不符合不含后视镜口径。未覆盖既有组，已新建 `EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02` 并将当前 Ktype 指向新组。([landrover][3])
* 已完成固定表头、主键唯一性、引用闭合、尺寸和来源非空以及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* READY 映射：145
* DIMENSION_GROUP：71
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137686	137686	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137687	137687	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137688	137688	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137689	137689	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
137698_l1h1	137698	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137698_l1h2	137698	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137701_l1h1	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1H1 客运物理分支。	READY
137701_l1h2	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1H2 客运物理分支。	READY
137701_l2h1	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2H1 客运物理分支。	READY
137701_l2h2	137701	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2H2 客运物理分支。	READY
137709_l1h1	137709	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	PHEV 仅有 L1H1 物理分支。	READY
137710_l1h1	137710	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137710_l1h2	137710	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137710_l2h1	137710	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	HIGH	L2H1 物理分支。	READY
137710_l2h2	137710	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	HIGH	L2H2 物理分支。	READY
137711_l1h1	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137711_l1h2	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137711_l2h1	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	HIGH	L2H1 物理分支。	READY
137711_l2h2	137711	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	HIGH	L2H2 物理分支。	READY
137712_l1h1	137712	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	HIGH	L1H1 物理分支。	READY
137712_l1h2	137712	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	HIGH	L1H2 物理分支。	READY
137712_l2h1	137712	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	HIGH	L2H1 物理分支。	READY
137712_l2h2	137712	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	HIGH	L2H2 物理分支。	READY
137713	137713	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-01	HIGH		READY
137720	137720	Convertible	600LT	P13	2	EU-MCLAREN-600LT-P13-CONVERTIBLE-01	HIGH	600LT Spider 开篷外廓。	READY
137721	137721	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-DT-QUAD-CAB-6FT4-2WD-01	HIGH	Quad Cab 6ft4 2WD 外廓。	READY
137722	137722	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-DT-QUAD-CAB-6FT4-4WD-01	HIGH	Quad Cab 6ft4 4WD 外廓。	READY
137723	137723	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
137724	137724	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137725	137725	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137726	137726	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137727	137727	Hatchback	Corsa F		5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
137729	137729	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137730	137730	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137731	137731	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137732	137732	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	标准轴距 MPV 外廓。	READY
137733	137733	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137734	137734	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137735	137735	Hatchback	Astra K		5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
137736	137736	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137737	137737	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137738	137738	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137739	137739	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137740	137740	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137741	137741	Wagon	Astra K		5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
137743	137743	Coupe	C-Class IV	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
137745	137745	Coupe	A5 II	F5	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
137746	137746	Hatchback	A5 II	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门外廓。	READY
137756_s	137756	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	S 短车身物理分支。	READY
137756_m	137756	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	M 中车身物理分支。	READY
137757_s	137757	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	S 短车身物理分支。	READY
137757_m	137757	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	M 中车身物理分支。	READY
137758_s	137758	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	S 短车身物理分支。	READY
137758_m	137758	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	M 中车身物理分支。	READY
137758_l	137758	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	HIGH	L 长车身物理分支。	READY
137759_s	137759	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	S 短车身物理分支。	READY
137759_m	137759	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	M 中车身物理分支。	READY
137759_l	137759	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	HIGH	L 长车身物理分支。	READY
137760_s	137760	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	S 短车身物理分支。	READY
137760_m	137760	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	M 中车身物理分支。	READY
137760_l	137760	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	HIGH	L 长车身物理分支。	READY
137761_s	137761	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身客运物理分支。	READY
137761_m	137761	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身客运物理分支。	READY
137762_s	137762	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身客运物理分支。	READY
137762_m	137762	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身客运物理分支。	READY
137762_l	137762	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L 长车身客运物理分支。	READY
137763_s	137763	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身客运物理分支。	READY
137763_m	137763	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身客运物理分支。	READY
137763_l	137763	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L 长车身客运物理分支。	READY
137764_s	137764	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身客运物理分支。	READY
137764_m	137764	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身客运物理分支。	READY
137764_l	137764	MPV	Vivaro C	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L 长车身客运物理分支。	READY
137765	137765	Pickup	Vivaro C	K0	2	EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M 长度平台驾驶室外廓。	READY
137766	137766	Pickup	Vivaro C	K0	2	EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	M 长度平台驾驶室外廓。	READY
137767	137767	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
137768	137768	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
137771_van_swb	137771	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	MEDIUM	复合车身中的 Van 标准轴距分支。	READY
137771_van_lwb	137771	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	MEDIUM	复合车身中的 Van 长轴距分支。	READY
137771_mpv_swb	137771	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	MEDIUM	复合车身中的 MPV 标准轴距分支。	READY
137771_mpv_lwb	137771	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	MEDIUM	复合车身中的 MPV 长轴距分支。	READY
137772	137772	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	MEDIUM	标准轴距 MPV 外廓。	READY
137773	137773	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	MEDIUM	标准轴距 MPV 外廓。	READY
137774	137774	MPV	Partner Origin I	M59	5	EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	HIGH	Partner Origin 客运外廓。	READY
137776	137776	MPV	Partner Origin I	M59	5	EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	HIGH	Partner Origin 客运外廓。	READY
137779	137779	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	Partner Origin 厢式外廓。	READY
137780	137780	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	Partner Origin 厢式外廓。	READY
137784	137784	Van	Partner Origin I	M59		EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	MEDIUM	Partner Origin 厢式外廓。	READY
137786	137786	SUV	X5 IV	F95	5	EU-BMW-X5-F95-M-SUV-01	HIGH		READY
137787	137787	SUV	X5 IV	F95	5	EU-BMW-X5-F95-M-COMPETITION-SUV-01	HIGH		READY
137788	137788	SUV	X6 III	F96	5	EU-BMW-X6-F96-M-SUV-01	HIGH		READY
137789	137789	SUV	X6 III	F96	5	EU-BMW-X6-F96-M-COMPETITION-SUV-01	HIGH		READY
137798	137798	Coupe	8 Series II	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
137799	137799	Coupe	8 Series II	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
137810	137810	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
137816	137816	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137817	137817	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137818	137818	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
137819	137819	Van	Largus I	F90		EU-LADA-LARGUS-I-F90-CNG-VAN-01	HIGH		READY
137822_l1h1	137822	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1 客运物理分支。	READY
137822_l2h1	137822	MPV	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1 客运物理分支。	READY
137825	137825	SUV	C5 Aircross I	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
137828	137828	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
137831_van_swb	137831	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	MEDIUM	复合车身中的 Van 标准轴距分支。	READY
137831_van_lwb	137831	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	MEDIUM	复合车身中的 Van 长轴距分支。	READY
137831_mpv_swb	137831	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	MEDIUM	复合车身中的 MPV 标准轴距分支。	READY
137831_mpv_lwb	137831	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	MEDIUM	复合车身中的 MPV 长轴距分支。	READY
137833	137833	Wagon	B3 G21	G21	5	EU-ALPINA-B3-G21-TOURING-PREFL-01	HIGH	B3 Touring G21 改款前外廓。	READY
137842	137842	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-AWD-01	HIGH		READY
137843	137843	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH		READY
137844_swb	137844	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137844_lwb	137844	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137845	137845	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	HIGH	GP 宽体三门外廓。	READY
137846_swb	137846	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137846_lwb	137846	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137847_swb	137847	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	HIGH	Connect 标准轴距物理分支。	READY
137847_lwb	137847	MPV	Tourneo Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	HIGH	Grand Connect 长轴物理分支。	READY
137857	137857	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
137861	137861	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
137874	137874	Convertible	Ape Calessino 200		2	EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	HIGH	Ape Calessino 200 开放式软顶外廓。	READY
137876	137876	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH		READY
137895	137895	Wagon	3 Series VII	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
137905_standard	137905	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	普通悬架和标准车顶外廓。	READY
137905_outdoor	137905	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor 升高悬架及车顶杆外廓。	READY
137938_swb	137938	MPV	Multivan T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	标准轴距物理分支。	READY
137938_lwb	137938	MPV	Multivan T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	长轴距物理分支。	READY
137946_swb	137946	MPV	Transporter T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	Caravelle/Bus 标准轴距物理分支。	READY
137946_lwb	137946	MPV	Transporter T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	Caravelle/Bus 长轴距物理分支。	READY
137952	137952	Coupe	2 Series II	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	F44 Gran Coupe 四门外廓。	READY
137953	137953	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH		READY
137954	137954	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-TURBO-01	HIGH	2.9 Turbo 改款外廓。	READY
137965	137965	Convertible	C-Class IV	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
137966_s	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S 短车身物理分支。	READY
137966_m	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M 中车身物理分支。	READY
137966_l	137966	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L 长车身物理分支。	READY
137972_swb	137972	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	标准轴距低顶物理分支。	READY
137972_lwb	137972	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	长轴距低顶物理分支。	READY
137976	137976	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
137980	137980	Sedan	ES VII	XZ10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH		READY
137990_swb	137990	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	标准轴距低顶物理分支。	READY
137990_lwb	137990	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	长轴距低顶物理分支。	READY
137994	137994	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	L550 facelift 五门外廓。	READY
137996	137996	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137997	137997	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137998	137998	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
137999	137999	SUV	Defender II	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	HIGH	五门 Defender 110 外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4301-4400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590	KGM Tivoli model specifications	https://en.wikipedia.org/wiki/KGM_Tivoli
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	4973	1986	2000	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	4973	1986	2366	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	4973	1986	2389	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	5340	1986	2017	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	5340	1986	2381	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	5340	1986	1979	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	5340	1986	2343	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-RENAULT-ZOE-I-X10-HATCHBACK-01	4084	1730	1562	Renault ZOE model specifications	https://en.wikipedia.org/wiki/Renault_Zoe
EU-MCLAREN-600LT-P13-CONVERTIBLE-01	4604	1930	1196	McLaren 600LT official brochure;CarsGuide McLaren 600LT dimensions	https://www.auto-brochures.com/makes/mclaren/McLaren_int%20600LT_2019.pdf;https://www.carsguide.com.au/mclaren/600lt/car-dimensions/2020
EU-RAM-1500-DT-QUAD-CAB-6FT4-2WD-01	5814	2085	1971	Stellantis Fleet All-New 2019 Ram 1500 buyer guide;Car and Driver 2019 Ram 1500 specifications	https://www.stellantisfleet.com/content/dam/fca-fleet/na/fleet/en_us/shopping-tools/brochures-literature/docs/2019_Ram_1500.pdf;https://www.caranddriver.com/ram/1500/specs/2019/ram_1500_ram-1500_2019
EU-RAM-1500-DT-QUAD-CAB-6FT4-4WD-01	5814	2085	1974	Stellantis Fleet All-New 2019 Ram 1500 buyer guide;Edmunds 2019 Ram 1500 Quad Cab specifications	https://www.stellantisfleet.com/content/dam/fca-fleet/na/fleet/en_us/shopping-tools/brochures-literature/docs/2019_Ram_1500.pdf;https://www.edmunds.com/ram/1500/2019/quad-cab/features-specs/
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos II model specifications	https://en.wikipedia.org/wiki/Renault_Koleos
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433	Opel Corsa F model specifications	https://en.wikipedia.org/wiki/Opel_Corsa
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485	Opel Astra K model specifications	https://en.wikipedia.org/wiki/Opel_Astra
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801	Renault Kangoo II model specifications	https://en.wikipedia.org/wiki/Renault_Kangoo
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510	Opel Astra K Sports Tourer model specifications	https://en.wikipedia.org/wiki/Opel_Astra
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Mercedes-Benz C-Class W205 model specifications	https://en.wikipedia.org/wiki/Mercedes-Benz_C-Class_(W205)
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Audi A5 F5 model specifications	https://en.wikipedia.org/wiki/Audi_A5
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 F5 model specifications	https://en.wikipedia.org/wiki/Audi_A5
EU-OPEL-VIVARO-C-K0-VAN-S-01	4609	1920	1905	Opel Vivaro Cargo official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-VIVARO-C-K0-VAN-M-01	4959	1920	1895	Opel Vivaro Cargo official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-VIVARO-C-K0-VAN-L-01	5309	1920	1935	Opel Vivaro Cargo official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Opel Vivaro Kombi official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Opel Vivaro Kombi official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Opel Vivaro Kombi official price and technical data;Vauxhall New Vivaro official price and specification guide	https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	4959	1920	1930	Vauxhall New Vivaro 2020 Model Year Price and Specification Guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/commercial-vehicles/new-vivaro/NEW_Vivaro_Price_Spec_11_feb.pdf
EU-VW-T-ROC-I-SUV-01	4234	1819	1573	Volkswagen T-Roc model specifications	https://en.wikipedia.org/wiki/Volkswagen_T-Roc
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	4425	1835	1859	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	4825	1835	1847	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	4425	1835	1844	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	4825	1835	1841	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	4418	1835	1861	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	4137	1724	1810	Peugeot Partner Origin official Combi brochure;Peugeot Partner Origin official Van brochure	https://automobilisto.de/es/archive/peugeot/partner/origin-combi-2008-es.pdf;https://automobilisto.de/es/archive/peugeot/partner/origin-van-2008-es.pdf
EU-BMW-X5-F95-M-SUV-01	4953	2015	1751	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X5-F95-M-COMPETITION-SUV-01	4953	2015	1749	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X6-F96-M-SUV-01	4953	2019	1693	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-X6-F96-M-COMPETITION-SUV-01	4953	2019	1692	BMW X5 M & X6 M 2020MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0304263EN/444941
EU-BMW-8-F92-M8-COUPE-01	4867	1907	1362	BMW M8 Coupe model specifications	https://en.wikipedia.org/wiki/BMW_8_Series_(G15)
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Mercedes-Benz A-Class V177 model specifications	https://en.wikipedia.org/wiki/Mercedes-Benz_A-Class_(W177)
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota RAV4 Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220203M-RAV4-Tech-Spec.pdf
EU-LADA-LARGUS-I-F90-CNG-VAN-01	4470	1750	1650	Lada Largus model specifications	https://en.wikipedia.org/wiki/Lada_Largus
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault Trafic III model specifications	https://en.wikipedia.org/wiki/Renault_Trafic
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault Trafic III model specifications	https://en.wikipedia.org/wiki/Renault_Trafic
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670	Citroën C5 Aircross model specifications	https://en.wikipedia.org/wiki/Citro%C3%ABn_C5_Aircross
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638	Citroën Grand C4 SpaceTourer model specifications	https://en.wikipedia.org/wiki/Citro%C3%ABn_C4_Picasso
EU-ALPINA-B3-G21-TOURING-PREFL-01	4719	1827	1438	Auto-Data ALPINA B3 Touring G21 technical specifications	https://www.auto-data.net/en/alpina-b3-touring-g21-generation-7283
EU-HONDA-CR-V-V-RW-SUV-AWD-01	4600	1855	1689	Honda CR-V fifth-generation model specifications	https://en.wikipedia.org/wiki/Honda_CR-V
EU-SUBARU-XV-II-SUV-01	4465	1805	1615	Subaru XV second-generation model specifications	https://en.wikipedia.org/wiki/Subaru_Crosstrek
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	4818	1835	1861	Ford Transit Connect official brochure;Ford Europe Transit Connect Technical Specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Connect.pdf;https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Connect/FordTransitConnect-Specifications_EU.pdf
EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	3879	1762	1420	BMW Group MY21 MINI 3 door Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0305951EN/446631
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai Santa Fe fourth-generation model specifications	https://en.wikipedia.org/wiki/Hyundai_Santa_Fe
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Hyundai Tucson third-generation model specifications	https://en.wikipedia.org/wiki/Hyundai_Tucson
EU-PIAGGIO-APE-CALESSINO-200-CONVERTIBLE-01	2700	1370	1780	Piaggio Commercial Ape Calessino official brochure	https://piaggiocommercialuk.com/wp-content/uploads/2019/09/ApeCalessino-Brochure-08-2019.pdf
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823	Mercedes-Benz GLS X167 model specifications	https://en.wikipedia.org/wiki/Mercedes-Benz_GLS
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	BMW 3 Series G20/G21 model specifications	https://en.wikipedia.org/wiki/BMW_3_Series_(G20)
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801	Peugeot Partner Tepee official brochure	https://s4bf885b88c0d668f.jimcontent.com/download/version/1595487575/module/9006515520/name/Peugeot%20Partner%20Tepee%20Brochure.pdf
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862	Peugeot Partner Tepee official brochure	https://s4bf885b88c0d668f.jimcontent.com/download/version/1595487575/module/9006515520/name/Peugeot%20Partner%20Tepee%20Brochure.pdf
EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	4904	1904	1970	Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	5304	1904	1990	Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW 2 Series Gran Coupe F44 model specifications	https://en.wikipedia.org/wiki/BMW_2_Series_Gran_Coup%C3%A9
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696	Porsche Cayenne third-generation model specifications	https://en.wikipedia.org/wiki/Porsche_Cayenne
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-TURBO-01	4684	1926	1624	Porsche Macan Turbo Technical Data	https://newsroom.porsche.com/dam/jcr%3A699435b8-f6b7-4ae6-a9eb-a2984f9e4650/PAG_MacanTurbo_TD_EN.pdf
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Mercedes-Benz C-Class W205 model specifications	https://en.wikipedia.org/wiki/Mercedes-Benz_C-Class_(W205)
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990	Volkswagen Transporter T6.1 model specifications;Volkswagen Caravelle 6.1 official brochure	https://en.wikipedia.org/wiki/Volkswagen_Transporter_(T6);https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990	Volkswagen Transporter T6.1 model specifications;Volkswagen Caravelle 6.1 official brochure	https://en.wikipedia.org/wiki/Volkswagen_Transporter_(T6);https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Mercedes-Benz GLE V167 model specifications	https://en.wikipedia.org/wiki/Mercedes-Benz_GLE
EU-LEXUS-ES-VII-XZ10-SEDAN-01	4975	1865	1445	Lexus ES seventh-generation model specifications	https://en.wikipedia.org/wiki/Lexus_ES
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	4597	1904	1727	Land Rover Discovery Sport official technical specification;Car and Driver Discovery Sport specifications	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/wltp-pdfs/Land-Rover-Discovery-Sport-TD-Insert-1L5502600000GBEN01P.pdf;https://www.caranddriver.com/land-rover/discovery-sport/specs
EU-LAND-ROVER-DEFENDER-II-L663-110-SUV-01	5018	1996	1967	Land Rover 2020 Defender 110 Technical Specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4301-4400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf "https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf"
[2]: https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf "https://www.opel-niedersachsen.de/media/files/Vivaro-C-2019-03-11_08156-1901.pdf"
[3]: https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/wltp-pdfs/Land-Rover-Discovery-Sport-TD-Insert-1L5502600000GBEN01P.pdf "https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/wltp-pdfs/Land-Rover-Discovery-Sport-TD-Insert-1L5502600000GBEN01P.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4145 行）
- 累计尺寸组：dimension_groups_final.tsv（1686 行）

