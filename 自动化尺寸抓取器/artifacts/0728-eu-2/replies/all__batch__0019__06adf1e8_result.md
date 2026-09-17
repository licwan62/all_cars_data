# 任务：all 第 1801-1900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0019__06adf1e8


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1801-1900 行

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
all 第 1801-1900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391
EU-AUDI-A4-B7-CONVERTIBLE-02	4570	1780	1390
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453
EU-AUDI-A4-B7-WAGON-5D-02	4586	1772	1427
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810
EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	3860	1667	1510
EU-CITROEN-C3-I-HATCHBACK-PHASE-I-01	3850	1667	1529
EU-CITROEN-C3-I-HATCHBACK-PHASE-II-01	3860	1667	1510
EU-CITROEN-JUMPER-III-BUS-VAN-L1H1-01	4963	2050	2254
EU-CITROEN-JUMPER-III-BUS-VAN-L2H1-01	5413	2050	2254
EU-CITROEN-JUMPER-III-BUS-VAN-L2H2-01	5413	2050	2524
EU-CITROEN-JUMPER-III-BUS-VAN-L3H2-01	5998	2050	2524
EU-CITROEN-JUMPER-III-BUS-VAN-L4H2-01	6363	2050	2524
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	4908	2050	2153
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	5358	2050	2153
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	5708	2050	2153
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	5943	2050	2153
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	6208	2050	2153
EU-CITROEN-JUMPER-III-VAN-L1H1-01	4963	2050	2254
EU-CITROEN-JUMPER-III-VAN-L2H1-01	5413	2050	2254
EU-CITROEN-JUMPER-III-VAN-L2H2-01	5413	2050	2524
EU-CITROEN-JUMPER-III-VAN-L3H2-01	5998	2050	2524
EU-CITROEN-JUMPER-III-VAN-L3H3-01	5998	2050	2764
EU-CITROEN-JUMPER-III-VAN-L4H2-01	6363	2050	2524
EU-CITROEN-JUMPER-III-VAN-L4H3-01	6363	2050	2764
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368
EU-DAEWOO-NUBIRA-III-WAGON-5D-01	4580	1725	1460
EU-DAEWOO-NUBIRA-J100-WAGON-01	4514	1700	1432
EU-DAEWOO-NUBIRA-J150-SEDAN-01	4495	1700	1430
EU-DAEWOO-NUBIRA-J150-WAGON-01	4550	1720	1430
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	5681	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	5681	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	5181	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	5181	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	4831	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	5980	2040	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	5980	2040	2125
EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	5998	2050	2524
EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	5413	2050	2524
EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	4963	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779
EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	5599	2024	2470
EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	5099	2024	2470
EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	5099	2024	2480
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X230-TRUCK-LWB-01	5620	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-MWB-01	5120	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-SWB-01	4770	2000	2100
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522
EU-FIAT-STRADA-178-PICKUP-LONGCAB-01	4444	1664	1525
EU-FIAT-STRADA-178-PICKUP-SHORTCAB-01	4444	1664	1525
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030
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
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700
EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	4785	1870	1710
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-FACELIFT-01	4390	1695	1306
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-PREFL-01	4390	1695	1321
EU-MITSUBISHI-ECLIPSE-I-COUPE-01	4390	1695	1321
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488
EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	4040	1713	1488
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488
EU-OPEL-MOVANO-A-BUS-L1H1-01	4899	1990	2253
EU-OPEL-MOVANO-A-BUS-L2H2-01	5399	1990	2493
EU-OPEL-MOVANO-A-BUS-L3H3-01	5899	1990	2720
EU-OPEL-MOVANO-A-VAN-L1H1-01	4899	1990	2253
EU-OPEL-MOVANO-A-VAN-L1H2-01	4899	1990	2496
EU-OPEL-MOVANO-A-VAN-L2H2-01	5399	1990	2493
EU-OPEL-MOVANO-A-VAN-L3H2-01	5899	1990	2490
EU-OPEL-MOVANO-A-VAN-L3H3-01	5899	1990	2720
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	5869	1990	2195
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	5369	1990	2200
EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	5869	1990	2203
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-PEUGEOT-307-I-FACELIFT-HATCHBACK-01	4212	1746	1510
EU-PEUGEOT-307-I-FACELIFT-WAGON-01	4432	1757	1544
EU-PEUGEOT-307-I-WAGON-01	4419	1757	1544
EU-PEUGEOT-307-WAGON-PREFL-01	4419	1757	1544
EU-RENAULT-KANGOO-I-FACELIFT-MPV-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504
EU-VW-NEW-BEETLE-9C-HATCHBACK-01	4081	1725	1500
EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	4129	1721	1502
EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	4129	1721	1498

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Kangoo	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	64	87	Feb 2008	-	2024-03-01	23491
Renault	Kangoo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	78	106	Feb 2008	-	2024-03-01	23492
Renault	Kangoo	1.5 DCI 70	Kasten/Großraumlimousine	Frontantrieb	Diesel	50	68	Feb 2008	-	2024-03-01	23493
Renault	Kangoo	1.5 DCI 85	Kasten/Großraumlimousine	Frontantrieb	Diesel	63	86	Feb 2008	-	2024-03-01	23494
Renault	Kangoo	1.5 DCI 105	Kasten/Großraumlimousine	Frontantrieb	Diesel	76	103	Feb 2008	-	2024-03-01	23495
Daihatsu	Cuore vii	1	Schrägheck	Frontantrieb	Benzin	51	70	Apr 2007	-	2024-03-01	23496
Opel	Corsa d	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	110	150	May 2007	Aug 2014	2024-03-01	23497
Opel	Vivaro a	2.5 Cdti	Kasten	Frontantrieb	Diesel	84	114	Aug 2006	Mar 2010	2024-03-01	23498
Opel	Vivaro a	2.5 Cdti	Bus	Frontantrieb	Diesel	84	114	Aug 2006	Mar 2010	2024-03-01	23499
Opel	Movano a	2.5 Cdti	Kasten	Frontantrieb	Diesel	107	146	Oct 2003	-	2024-03-01	23500
Opel	Movano a	2.5 Cdti	Bus	Frontantrieb	Diesel	107	146	Aug 2006	-	2024-03-01	23501
Opel	Movano a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	-	2024-03-01	23502
Opel	Movano a	2.5 Cdti	Bus	Frontantrieb	Diesel	88	120	Aug 2006	-	2024-03-01	23503
Opel	Movano a	2.5 Cdti	Kasten	Frontantrieb	Diesel	88	120	Oct 2003	-	2024-03-01	23504
Opel	Movano a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2006	-	2024-03-01	23505
Renault	Rapid	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	43	58	Sep 1991	Aug 1997	2024-03-01	23508
Jaguar	Xj	4	Stufenheck	Heckantrieb	Benzin	166	226	Oct 1989	Aug 1994	2024-03-01	23515
Saab	900 i	2	Stufenheck	Frontantrieb	Benzin	74	100	Jul 1982	Dec 1988	2024-03-01	23517
Citroën	Xm	3	Kombi	Frontantrieb	Benzin	123	167	May 1989	Jul 1994	2024-03-01	23524
Peugeot	306	1.8	Cabriolet	Frontantrieb	Benzin	74	101	May 1997	Apr 1999	2024-03-01	23539
Mazda	323 iii station wagon	1.6	Kombi	Frontantrieb	Benzin	63	86	Sep 1992	Oct 1995	2024-03-01	23547
Opel	Omega a caravan	2	Kombi	Heckantrieb	Benzin	85	116	Sep 1987	Apr 1994	2024-03-01	23549
Isuzu	Trooper i	2.6 4WD	Geländewagen geschlossen	Allrad	Benzin	85	116	Nov 1986	Jul 1991	2024-03-01	23576
Maserati	Biturbo	420 SI	Stufenheck	Heckantrieb	Benzin	162	220	Oct 1986	Sep 1988	2024-03-01	23586
Chrysler	Voyager / grand iii	2.4 AWD	Großraumlimousine	Allrad	Benzin	111	151	Feb 1997	Mar 2001	2024-03-01	23587
Pontiac	Trans sport	3.1	Großraumlimousine	Frontantrieb	Benzin	89	121	Aug 1989	Dec 1992	2024-03-01	23621
Ford USA	Taurus	3	Stufenheck	Frontantrieb	Benzin	95	129	Nov 1998	Dec 1999	2024-03-01	23624
Ford USA	Taurus	3	Kombi	Frontantrieb	Benzin	95	129	Nov 1998	Dec 1999	2024-03-01	23625
Chevrolet	Blazer s10	4.3 AWD	Geländewagen geschlossen	Allrad	Benzin	119	162	Oct 1994	Sep 1995	2024-03-01	23632
Buick	Skylark	2.3	Stufenheck	Frontantrieb	Benzin	90	122	Oct 1993	Sep 1994	2024-03-01	23634
Cadillac	Seville	4.9	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1990	Sep 1991	2024-03-01	23636
Chevrolet	Beretta	2.3	Coupe	Frontantrieb	Benzin	134	182	Oct 1992	Sep 1996	2024-03-01	23638
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	186	253	Oct 1989	Sep 1991	2024-03-01	23642
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	152	207	Sep 1996	Aug 2002	2024-03-01	23643
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	150	204	Oct 1999	Aug 2002	2024-03-01	23644
Fiat	Doblo cargo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	88	120	Oct 2011	Dec 2023	2025-02-03	23647
Fiat	Palio	1.4	Schrägheck	Frontantrieb	Benzin	57	78	Oct 2005	-	2024-03-01	23650
Citroën	Jumper i	2.0 4X4	Kasten	Allrad	Benzin	80	109	Oct 1996	Jan 2002	2024-03-01	23657
Opel	Astra g cc	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Sep 2007	Dec 2009	2024-03-01	23659
Opel	Astra g classic caravan	1.4	Kombi	Frontantrieb	Benzin	66	90	Oct 2007	Jul 2009	2024-03-01	23660
Daewoo	Nubira	1.6	Schrägheck	Frontantrieb	Benzin	76	103	Aug 2002	Jul 2003	2024-03-01	23661
KIA	Cee'd	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	66	90	May 2012	Jul 2018	2024-03-01	23662
Chrysler	Voyager i	3	Großraumlimousine	Frontantrieb	Benzin	100	136	Oct 1987	Sep 1990	2024-03-01	23674
Chrysler	Voyager i	3	Großraumlimousine	Frontantrieb	Benzin	101	137	Oct 1987	Sep 1990	2024-03-01	23675
Chrysler	Voyager i	3.3	Großraumlimousine	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1990	2024-03-01	23678
Daewoo	Lanos	1.5	Schrägheck	Frontantrieb	Benzin	73	99	Oct 1997	Jun 1999	2024-03-01	23679
Citroën	C25	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	55	75	Nov 1983	Jan 1994	2024-03-01	23681
Opel	Astra g	1.4	Stufenheck	Frontantrieb	Benzin	66	90	Sep 2007	Dec 2009	2024-03-01	23685
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	135	184	Aug 2013	Aug 2020	2024-03-01	23695
Morgan	Plus eight	3.9	Cabriolet	Heckantrieb	Benzin	140	190	May 1995	Oct 2004	2024-03-01	23697
Fiat	Panda	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	40	54	Sep 2000	Feb 2004	2024-03-01	23700
Fiat	Panda	1.1 4X4	Kasten/Schrägheck	Allrad	Benzin	40	54	Sep 2000	Feb 2004	2024-03-01	23701
Fiat	Doblo kombi	1.4	Bus	Frontantrieb	Benzin	88	120	Oct 2011	Dec 2023	2025-02-03	23703
Hyundai	Elantra iii	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Jun 2000	Jul 2006	2024-03-01	23718
Peugeot	307	1.6 HDI 90	Kombi	Frontantrieb	Diesel	66	90	Apr 2005	Apr 2008	2024-03-01	23722
Isuzu	Trooper ii	2.6 4X4	Geländewagen geschlossen	Allrad	Benzin	85	116	Aug 1991	Apr 1996	2024-03-01	23725
Isuzu	Trooper ii	2.6 4X4	Geländewagen offen	Allrad	Benzin	85	116	Aug 1991	Apr 1996	2024-03-01	23726
Audi	A6 c6	3	Stufenheck	Frontantrieb	Benzin	160	218	Aug 2004	May 2006	2024-03-01	23728
Nissan	350z roadster	3.5	Cabriolet	Heckantrieb	Benzin	230	313	Sep 2005	Dec 2009	2024-03-01	23729
Audi	A4 b7	3.0 Quattro	Stufenheck	Allrad	Benzin	160	218	Nov 2004	Jul 2006	2024-03-01	23735
Audi	A4 b7 avant	3.0 Quattro	Kombi	Allrad	Benzin	160	218	Nov 2004	Jul 2006	2024-03-01	23736
Chevrolet	Epica	2	Stufenheck	Frontantrieb	Benzin	94	128	Jan 2005	Dec 2006	2024-03-01	23739
Ssangyong	Actyon	2.3 4X4	SUV	Allrad	Benzin	110	150	Nov 2006	-	2025-12-01	23742
Mitsubishi	Eclipse	3	Cabriolet	Frontantrieb	Benzin	149	203	May 1999	Mar 2005	2024-03-01	23750
Mitsubishi	Eclipse	3	Cabriolet	Frontantrieb	Benzin	157	213	May 1999	Mar 2005	2024-03-01	23751
Chevrolet	Caprice	5.7	Stufenheck	Heckantrieb	Benzin	194	264	Oct 1993	Sep 1996	2024-03-01	23756
Buick	Century	2.5	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1981	Sep 1986	2024-03-01	23757
Buick	Century	3	Stufenheck	Frontantrieb	Benzin	82	111	Oct 1981	Sep 1986	2024-03-01	23758
Buick	Century	3.8	Stufenheck	Frontantrieb	Benzin	94	128	Oct 1983	Sep 1986	2024-03-01	23759
Buick	Century	3	Kombi	Frontantrieb	Benzin	82	111	Oct 1981	Aug 1983	2024-03-01	23760
Buick	Century	3.8	Kombi	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1988	2024-03-01	23761
Buick	Century	2.2	Stufenheck	Frontantrieb	Benzin	82	112	Oct 1991	Sep 1996	2024-03-01	23762
Buick	Century	3.1	Stufenheck	Frontantrieb	Benzin	130	177	Oct 1993	Sep 1996	2024-03-01	23763
Buick	Century	2.2	Kombi	Frontantrieb	Benzin	82	111	Oct 1991	Sep 1996	2024-03-01	23764
VW	Golf v variant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	147	200	Jun 2007	Jul 2009	2024-03-01	23795
Chrysler	Voyager iv	2.5 CRD	Großraumlimousine	Frontantrieb	Diesel	88	120	Aug 2005	Dec 2008	2024-03-01	23796
Jeep	Grand cherokee ii	2.7 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	120	163	Oct 2004	Sep 2005	2024-03-01	23797
Hyundai	H-1	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	103	140	Dec 2002	Oct 2005	2024-03-01	23798
Mitsubishi	Pajero classic	3.2 Di-d	Geländewagen geschlossen	Allrad	Diesel	125	170	Sep 2006	-	2024-03-01	23808
Peugeot	J5	2.5 DT	Kasten	Frontantrieb	Diesel	70	95	Sep 1990	Jan 1994	2024-03-01	23812
Daihatsu	Cuore v	1.0 Dvvt	Schrägheck	Frontantrieb	Benzin	43	58	Oct 2000	Feb 2003	2024-03-01	23816
Daihatsu	Terios	1.3 Vvt-i 4X4	Geländewagen geschlossen	Allrad	Benzin	63	86	Nov 2005	-	2024-03-01	23818
Citroën	Saxo	Electric	Schrägheck	Frontantrieb	Elektro	20	27	Nov 1996	Jun 2003	2024-03-01	23825
Citroën	Berlingo	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	28	38	Jul 2003	Dec 2005	2024-03-01	23826
Citroën	C3 i	1.4 HDI	Schrägheck	Frontantrieb	Diesel	55	75	May 2005	Dec 2009	2024-07-01	23829
Fiat	Ducato	2.8 JTD	Bus	Frontantrieb	Diesel	107	145	Apr 2004	Jul 2006	2024-03-01	23831
Lotus	Esprit s2	2.2 S2	Coupe	Heckantrieb	Benzin	118	160	Oct 1981	Aug 1984	2024-03-01	23834
VW	Lt 28-35 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	70	95	Aug 1992	Apr 1996	2024-03-01	23844
VW	Lt 40-55 i	2.4 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	70	95	Aug 1992	Apr 1996	2024-03-01	23846
Ford	Transit	2.4 TD	Kasten	Frontantrieb	Diesel	55	75	Aug 2000	Aug 2003	2024-03-01	23848
Opel	Insignia a sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	120	163	Jul 2013	Jun 2015	2024-03-01	23849
VW	Lt 28-35 ii	2.8 TDI	Bus	Heckantrieb	Diesel	116	158	May 2001	Jun 2006	2024-03-01	23856
Fiat	Strada	1.3 D Multijet	Pick-up	Frontantrieb	Diesel	70	95	Oct 2010	-	2024-03-01	23857
Jeep	Cherokee	2.5 TDI 4X4	Geländewagen geschlossen	Allrad	Diesel	85	116	Oct 1996	Sep 2001	2024-03-01	23859
Chrysler	Voyager / grand iii	2.5 Tdic AWD	Großraumlimousine	Allrad	Diesel	85	116	Oct 1995	Mar 2001	2024-03-01	23861
Buick	Century	3.8 T-type	Kombi	Frontantrieb	Benzin	94	128	Oct 1986	Sep 1989	2024-03-01	23864
VW	New beetle	2.5	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2005	Sep 2010	2024-03-01	23865
VW	New beetle	2.5	Cabriolet	Frontantrieb	Benzin	110	150	Jul 2005	Sep 2010	2024-03-01	23866
Morris	Mini	850	Schrägheck	Frontantrieb	Benzin	25	34	Jan 1967	Aug 1979	2024-03-01	24063
Renault	Thalia i	1.6	Stufenheck	Frontantrieb	Benzin	82	112	Jan 2004	Dec 2008	2024-03-01	24066


--- Round 1 / 首次发送 ---
## 更新点

* 优先完成可直接命中跨批次缓存、且物理外廓边界明确的车型。
* 新增/确认 25 个输入 Ktype，共 29 条映射。
* `23757`、`23758`、`23759` 按 Buick Century IV 改款前后外廓拆分。
* `23826` 按 Berlingo I M59 的 Van 与 MPV 外廓拆分。
* 本轮引用 21 个既有尺寸组，未重复抓取尺寸或来源，未新建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：25
* READY 映射：29
* PENDING Ktype：75
* 已引用确认尺寸组：21
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23642	23642	Convertible	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH		READY
23695	23695	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
23722	23722	Wagon	307 I		5	EU-PEUGEOT-307-I-FACELIFT-WAGON-01	HIGH	改款旅行车外廓。	READY
23728	23728	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4F2-01	HIGH	改款前轿车外廓。	READY
23735	23735	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
23736	23736	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
23739	23739	Sedan	Epica V200	V200	4	EU-CHEVROLET-EPICA-V200-SEDAN-01	HIGH		READY
23742	23742	SUV	Actyon I	C100	5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
23756	23756	Sedan	Caprice IV		4	EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23757_prefl	23757	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23757_facelift	23757	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23758_prefl	23758	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23758_facelift	23758	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23759_prefl	23759	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23759_facelift	23759	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23760	23760	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH	改款前旅行车外廓。	READY
23761	23761	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23762	23762	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23763	23763	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23764	23764	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23795	23795	Wagon	Golf V	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
23818	23818	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH		READY
23826_van	23826	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	原始组合车身拆分为厢式车外廓。	READY
23826_mpv	23826	MPV	Berlingo I	M59	5	EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	原始组合车身拆分为乘用MPV外廓。	READY
23829	23829	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	HIGH	改款两厢车外廓。	READY
23864	23864	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23865	23865	Hatchback	New Beetle I	9C1	3	EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	HIGH		READY
23866	23866	Convertible	New Beetle I	1Y7	2	EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
24066	24066	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	HIGH	改款轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量拆分 Opel Vivaro A、Movano A 的轴距、车顶和 Bus/Van/Chassis 外廓，并复用既有尺寸组。
2. 处理 Renault Kangoo II、Opel Corsa D 等已有候选尺寸组但需确认车身分支的 Ktype。
3. 处理 Fiat Ducato、Citroën Jumper、Ford Transit、VW LT 等多轴距商用车。
4. 再集中创建乘用车新尺寸组，避免逐 Ktype 重复抓取。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Renault Kangoo II 5 个 Ktype 的 Van/MPV 分支；首次创建 Kangoo II Express Van 尺寸组。该组采用 4213 × 1829 × 1844 mm，来源同时列出含镜宽度 2133 mm，可确认 `WidthMM=1829` 为不含后视镜口径。([汽车数据][1])
* 完成 Opel Vivaro A 两个 Ktype 的 SWB/LWB、低顶/高顶分支。
* 完成 Opel Movano A 六个 Ktype 的 Van、Bus、Chassis Cab 与 Crew Cab 分支；底盘车型按中轴、长轴边界链接已有缓存组。([Only Manuals][2])
* 本轮新增 READY Ktype 13 个、READY 映射 38 条；首次创建尺寸组 1 个。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：38
* READY 映射：67
* PENDING Ktype：62
* 已引用确认尺寸组：40
* 本轮首次创建/修正尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23491_van	23491	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23491_mpv	23491	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23492_van	23492	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23492_mpv	23492	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23493_van	23493	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23493_mpv	23493	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23494_van	23494	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23494_mpv	23494	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23495_van	23495	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23495_mpv	23495	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23498_swb_lowroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
23498_swb_highroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
23498_lwb_lowroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	长轴低顶外廓。	READY
23498_lwb_highroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
23499_swb	23499	MPV	Vivaro A	X83		EU-OPEL-VIVARO-A-BUS-SWB-01	HIGH	短轴Bus外廓。	READY
23499_lwb	23499	MPV	Vivaro A	X83		EU-OPEL-VIVARO-A-BUS-LWB-01	HIGH	长轴Bus外廓。	READY
23500_l1h1	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H1-01	HIGH	L1H1外廓。	READY
23500_l1h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H2-01	HIGH	L1H2外廓。	READY
23500_l2h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L2H2-01	HIGH	L2H2外廓。	READY
23500_l3h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H2-01	HIGH	L3H2外廓。	READY
23500_l3h3	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H3-01	HIGH	L3H3外廓。	READY
23501_l1h1	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	HIGH	L1H1 Bus外廓。	READY
23501_l2h2	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	HIGH	L2H2 Bus外廓。	READY
23501_l3h3	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	HIGH	L3H3 Bus外廓。	READY
23502_chassis_mwb	23502	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘外廓。	READY
23502_chassis_lwb	23502	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘外廓。	READY
23502_crew_lwb	23502	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	长轴双排底盘外廓。	READY
23503_l1h1	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	HIGH	L1H1 Bus外廓。	READY
23503_l2h2	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	HIGH	L2H2 Bus外廓。	READY
23503_l3h3	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	HIGH	L3H3 Bus外廓。	READY
23504_l1h1	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H1-01	HIGH	L1H1外廓。	READY
23504_l1h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H2-01	HIGH	L1H2外廓。	READY
23504_l2h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L2H2-01	HIGH	L2H2外廓。	READY
23504_l3h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H2-01	HIGH	L3H2外廓。	READY
23504_l3h3	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H3-01	HIGH	L3H3外廓。	READY
23505_chassis_mwb	23505	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘外廓。	READY
23505_chassis_lwb	23505	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘外廓。	READY
23505_crew_lwb	23505	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	长轴双排底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844	Auto-Data Renault Kangoo II Express	https://www.auto-data.net/en/renault-kangoo-ii-express-generation-7589
```

## 下一步优先处理

1. 处理 `23496` Daihatsu Cuore VII 与 `23497` Opel Corsa D 1.6 Turbo 的门数及性能外廓分支。
2. 集中处理 `23508–23643` 的老款乘用车和美系车型，优先创建可由多个 Ktype 复用的 Voyager、Taurus、Explorer 尺寸组。
3. 随后处理 Astra G、Fiat Panda、Isuzu Trooper 和 Mitsubishi Eclipse 等可批量闭合车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-kangoo-ii-express-generation-7589?utm_source=chatgpt.com "Renault Kangoo II Express | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.onlymanuals.com/vauxhall/movano/vauxhall_movano_owners_manual_2007_2007?utm_source=chatgpt.com "Vauxhall - Movano - Owners Manual - 2007 - 2007"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 `23496` Daihatsu Cuore VII，确认 L276 五门外廓并首次建立尺寸组。来源明确给出 3470 × 1475 × 1530 mm，宽度为不含后视镜口径。([汽车目录][1])
* 完成 `23497` Opel Corsa D 1.6 Turbo，按 L08 三门与 L68 五门拆分，直接复用既有 Corsa D 尺寸组。([AUTODOC][2])
* 完成 Astra G 集群 `23659`、`23660`、`23685`，分别闭合 F08 三门、F48 五门、F35 旅行车和 F69 轿车边界；首次建立 4 个尺寸组。规格页分别列出车身宽度和含后视镜宽度，当前 `WidthMM` 口径已闭合。([AUTODOC 丹麦][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：43
* READY 映射：74
* PENDING Ktype：57
* 已引用确认尺寸组：47
* 本轮首次创建/修正尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23496	23496	Hatchback	Cuore VII	L276	5	EU-DAIHATSU-CUORE-VII-L276-HATCHBACK-5D-01	HIGH		READY
23497_3dr	23497	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门外廓。	READY
23497_5dr	23497	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门外廓。	READY
23659_3dr	23659	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-F08-HATCHBACK-3D-01	HIGH	F08三门外廓。	READY
23659_5dr	23659	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-F48-HATCHBACK-5D-01	HIGH	F48五门外廓。	READY
23660	23660	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-F35-WAGON-5D-01	HIGH		READY
23685	23685	Sedan	Astra G	F69	4	EU-OPEL-ASTRA-G-F69-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CUORE-VII-L276-HATCHBACK-5D-01	3470	1475	1530	Automobile-Catalog Daihatsu Cuore Top	https://www.automobile-catalog.com/car/2007/581105/daihatsu_cuore_top.html
EU-OPEL-ASTRA-G-F08-HATCHBACK-3D-01	4110	1709	1425	Auto-Data Opel Astra G 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.4-ecotec-16v-90hp-2432
EU-OPEL-ASTRA-G-F48-HATCHBACK-5D-01	4110	1709	1425	Auto-Data Opel Astra G 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.4-ecotec-16v-90hp-2432
EU-OPEL-ASTRA-G-F35-WAGON-5D-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-caravan-1.4-ecotec-16v-90hp-2415
EU-OPEL-ASTRA-G-F69-SEDAN-4D-01	4252	1709	1425	Auto-Data Opel Astra G Classic 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-classic-1.4-ecotec-16v-90hp-2393
```

## 下一步优先处理

1. 处理 `23700`、`23701` Fiat Panda 141，分离前驱与 4×4 的不同外廓。
2. 处理 `23825` Citroën Saxo Electric 的门数及改款前后边界，优先复用既有 Phase II 尺寸组。
3. 批量处理 `23831` Fiat Ducato Bus、`23848` Ford Transit Van 等已有商用车尺寸缓存。
4. 继续闭合 `23816` Cuore V、`23818` 后续相邻车型及其他可成组处理的乘用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/581105/daihatsu_cuore_top.html?utm_source=chatgpt.com "2007 Daihatsu Cuore Top Specs Review (51 kW / 69 PS / 68 hp) (since mid-year 2007 for Europe export)"
[2]: https://www.autodoc.parts/car-parts/spark-plug-10251/opel/corsa/corsa-d/23497-1-6-turbo-l08-l68?utm_source=chatgpt.com "Opel Corsa D 1.6 Turbo Spark plug (150 hp Petrol A 16 LEL)"
[3]: https://www.autodoc.dk/reservedele/koelevandsslanger-10200/opel/astra/astra-g-hatchback-f48-f08/23659-1-4-f08-f48?utm_source=chatgpt.com "Kølerslanger Opel Astra G CC 1.4 90 HK Benzin Z 14 XEP"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 `23700`、`23701` Fiat Panda 141A 厢式车型，前驱与四驱外廓分别建组；四驱车型的长度、高度均不同，不能共用尺寸组。([allopneus.com][1])
* 完成 `23816` Daihatsu Cuore V L701，按三门、五门拆为两条映射；两种门数共用同一套外部三维。([allopneus.com][2])
* 完成 `23857` Fiat Strada 278。官方 95 HP 技术表确认 6 种不同外廓；当前三维与累计表中既有 Strada 178 尺寸组不一致，因此未覆盖或复用旧组，新增 6 个 Strada 278 尺寸组。([Stellantis Media][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：47
* READY 映射：84
* PENDING Ktype：53
* 已引用确认尺寸组：56
* 本轮首次创建/修正尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23700	23700	Van	Panda I	141A	3	EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	HIGH	三门前驱厢式外廓。	READY
23701	23701	Van	Panda I	141A	3	EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	HIGH	三门四驱厢式外廓。	READY
23816_3dr	23816	Hatchback	Cuore V	L701	3	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	MEDIUM	L701三门外廓。	READY
23816_5dr	23816	Hatchback	Cuore V	L701	5	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	MEDIUM	L701五门外廓；三维与三门一致。	READY
23857_working_shortcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-WORKING-SHORTCAB-01	HIGH	Working短驾驶室外廓。	READY
23857_working_crewcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-WORKING-CREWCAB-01	HIGH	Working双排驾驶室外廓。	READY
23857_trekking_shortcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-TREKKING-SHORTCAB-01	HIGH	Trekking短驾驶室外廓。	READY
23857_trekking_longcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-TREKKING-LONGCAB-01	HIGH	Trekking加长驾驶室外廓。	READY
23857_adventure_longcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-ADVENTURE-LONGCAB-01	HIGH	Adventure加长驾驶室宽体外廓。	READY
23857_adventure_crewcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-ADVENTURE-CREWCAB-01	HIGH	Adventure双排驾驶室宽体外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420	Auto-Data Fiat Panda 1100 ie; Automobile-Catalog Fiat Panda 1.1 i.e. Selecta	https://www.auto-data.net/en/fiat-panda-zaf-141-facelift-1991-1100-ie-55hp-6915;https://www.automobile-catalog.com/car/1997/715460/fiat_panda_1_1i_e__selecta.html
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485	Automobile-Catalog 2001 Fiat Panda 1.1 i.e. 4x4	https://www.automobile-catalog.com/car/2001/715445/fiat_panda_1_1i_e__4x4.html
EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	3410	1475	1420	Auto-Data Daihatsu Cuore; Automobile-Catalog 2000 Daihatsu Cuore GLX	https://www.auto-data.net/en/daihatsu-cuore-model-15;https://www.automobile-catalog.com/car/2000/574895/daihatsu_cuore_glx.html
EU-FIAT-STRADA-278-PICKUP-WORKING-SHORTCAB-01	4409	1664	1525	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-WORKING-CREWCAB-01	4409	1664	1580	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-TREKKING-SHORTCAB-01	4409	1664	1564	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-TREKKING-LONGCAB-01	4409	1664	1588	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-ADVENTURE-LONGCAB-01	4457	1740	1648	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-ADVENTURE-CREWCAB-01	4457	1740	1631	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
```

## 下一步优先处理

1. 闭合 `23825` Citroën Saxo Electric 的三门、五门及改款前后边界。
2. 处理 `23831` Fiat Ducato II Bus，并优先匹配已确认的 X244 轴距和车顶尺寸组。
3. 集中处理 `23750`、`23751` Mitsubishi Eclipse III Convertible 和 `23729` Nissan 350Z Roadster。
4. 随后处理 `23647`、`23703` Fiat Doblò II 的 Cargo 与乘用车外廓。

推进信号：CONTINUE

[1]: https://www.allopneus.com/vehicule/fiat/panda/panda-van?utm_source=chatgpt.com "Pneu FIAT PANDA VAN : Pression et dimensions des pneus - Allopneus.com"
[2]: https://www.allopneus.com/vehicule/daihatsu/cuore/cuore?utm_source=chatgpt.com "Pneu DAIHATSU CUORE : Pression et dimensions des pneus - Allopneus.com"
[3]: https://www.media.stellantis.com/em-en/fiat-professional/press/marketing-of-the-new-fiat-strada-to-kick-off-soon "Marketing of the New Fiat Strada to kick off soon | FIAT Professional | Stellantis Media"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 Peugeot 306 Cabriolet 改款版、Maserati 420 Si、Ford Taurus III 轿车/旅行车、Nissan 350Z Roadster 改款版，以及两个 Mitsubishi Eclipse III Spyder Ktype。
* Taurus III 轿车与旅行车的长度、高度不同，分别建立尺寸组；两者宽度均按明确标注的不含后视镜口径落盘。([汽车数据][1])
* `23750`、`23751` 均对应 Eclipse III 3.0 Spyder D53A，共用同一物理外廓；宽度已由明确标注不含后视镜的规格交叉确认。([汽车数据][2])
* `23729` 的 313 HP 版本对应 2007–2009 年 Z33 改款 Roadster 外廓。([汽车数据][3])
* 本轮完成 7 个 Ktype，首次创建 6 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：54
* READY 映射：91
* PENDING Ktype：46
* 已引用确认尺寸组：62
* 本轮首次创建/修正尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23539	23539	Convertible	306 Cabrio facelift 1997	7D	2	EU-PEUGEOT-306-I-CONVERTIBLE-FACELIFT-01	HIGH	1997改款敞篷外廓。	READY
23586	23586	Sedan	Biturbo 420 Si	AM332	4	EU-MASERATI-BITURBO-420-SI-SEDAN-01	HIGH	420 Si四门轿车外廓。	READY
23624	23624	Sedan	Taurus III		4	EU-FORD-TAURUS-III-SEDAN-4D-01	MEDIUM	Taurus III四门轿车外廓。	READY
23625	23625	Wagon	Taurus III		5	EU-FORD-TAURUS-III-WAGON-5D-01	MEDIUM	Taurus III五门旅行车外廓。	READY
23729	23729	Convertible	350Z Roadster facelift 2007	Z33	2	EU-NISSAN-350Z-Z33-ROADSTER-FACELIFT-01	HIGH	313 HP改款Roadster外廓。	READY
23750	23750	Convertible	Eclipse Spyder III (3G)	D53A	2	EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	HIGH	D53A敞篷外廓。	READY
23751	23751	Convertible	Eclipse Spyder III (3G)	D53A	2	EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	HIGH	D53A敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-306-I-CONVERTIBLE-FACELIFT-01	4179	1680	1356	Auto-Data Peugeot 306 Cabrio facelift 1997 1.8i	https://www.auto-data.net/en/peugeot-306-cabrio-facelift-1997-1.8i-101hp-automatic-5676
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360	Automobile-Catalog 1988 Maserati 420 Si	https://www.automobile-catalog.com/car/1988/1445585/maserati_420_si.html
EU-FORD-TAURUS-III-SEDAN-4D-01	5016	1854	1400	Auto-Data Ford Taurus III 3.0 V6	https://www.auto-data.net/en/ford-taurus-iii-3.0-v6-145hp-automatic-7924
EU-FORD-TAURUS-III-WAGON-5D-01	5070	1854	1463	Edmunds 1999 Ford Taurus Wagon SE	https://www.edmunds.com/ford/taurus/1999/wagon/st-12295/features-specs/
EU-NISSAN-350Z-Z33-ROADSTER-FACELIFT-01	4315	1815	1330	Auto-Data Nissan 350Z Roadster Z33 facelift 313 HP	https://www.auto-data.net/en/nissan-350z-roadster-z33-facelift-2007-3.5i-v6-24v-313hp-25040
EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	4455	1750	1340	Auto-Data Mitsubishi Eclipse Spyder III GT 3.0	https://www.auto-data.net/en/mitsubishi-eclipse-spyder-iii-3g-gt-3.0-i-v6-24v-200hp-15621
```

## 下一步优先处理

1. 闭合 `23825` Citroën Saxo Electric 的 Phase I、Phase II 物理边界。
2. 集中处理 Chrysler Voyager I、Voyager III 和 Voyager IV，避免代际及标准轴距/Grand 车身混用。
3. 处理 Buick Skylark、Chevrolet Beretta、Cadillac Seville IV 等美系轿车组。
4. 后续再处理 Ducato、Transit、Jumper、VW LT 等多轴距商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-taurus-iii-3.0-v6-145hp-automatic-7924 "Ford Taurus III 3.0 V6 (145 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-eclipse-spyder-iii-3g-gt-3.0-i-v6-24v-200hp-15621 "Mitsubishi Eclipse Spyder III (3G) GT 3.0 i V6 24V (200 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/nissan-350z-roadster-z33-facelift-2007-3.5i-v6-24v-313hp-25040 "Nissan 350Z Roadster (Z33, facelift 2007) 3.5i V6 24V (313 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 `23825` Citroën Saxo Electric，按 Phase I 与 Phase II 外廓拆分；Phase II 直接复用既有三门尺寸组，Phase I 首次建组。([汽车数据][1])
* 完成 `23634` Buick Skylark VII Sedan、`23636` Cadillac Seville IV Sedan、`23638` Chevrolet Beretta Z26 Coupe。宽度均按不含后视镜口径闭合。([Edmunds][2])
* 完成 `23674`、`23675` Chrysler Voyager I 3.0，两个 Ktype 复用同一标准轴距五门外廓尺寸组。([Allopneus][3])
* 本轮新增 READY Ktype 6 个、READY 映射 7 条，首次创建尺寸组 5 个。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：60
* READY 映射：98
* PENDING Ktype：40
* 已引用确认尺寸组：68
* 本轮首次创建/修正尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23634	23634	Sedan	Skylark VII	N	4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
23636	23636	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门轿车外廓。	READY
23638	23638	Coupe	Beretta	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	两门Z26外廓。	READY
23674	23674	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23675	23675	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23825_prefl	23825	Hatchback	Saxo Phase I	SA13	3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	Phase I三门电动车外廓。	READY
23825_facelift	23825	Hatchback	Saxo Phase II	SA13	3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门电动车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4803	1715	1351	Edmunds 1994 Buick Skylark Sedan specifications	https://www.edmunds.com/buick/skylark/1994/sedan/features-specs/
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351	Edmunds 1991 Cadillac Seville Sedan specifications	https://www.edmunds.com/cadillac/seville/1991/sedan/st-10559/features-specs/
EU-CHEVROLET-BERETTA-L-COUPE-2D-01	4757	1735	1346	Automobile-Catalog 1994 Chevrolet Beretta Z26 2.3L Quad-4	https://www.automobile-catalog.com/car/1994/470645/chevrolet_beretta_z26_2_3l_quad-4.html
EU-CHRYSLER-VOYAGER-I-MPV-5D-01	4503	1833	1637	Automobile-Catalog 1989 Chrysler Voyager LE 3.0 V6	https://www.automobile-catalog.com/car/1989/516575/chrysler_voyager_le_3_0_v6_automatic.html
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	3718	1595	1390	Auto-Data Citroen Saxo Phase I 3-door Electric	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-12-kwh-27hp-46431
```

## 下一步优先处理

1. 处理 `23517` Saab 900 I 轿车的改款前后外廓。
2. 集中闭合 `23524` Citroën XM Wagon、`23547` Mazda 323 III Wagon、`23549` Opel Omega A Caravan。
3. 处理 `23576`、`23725`、`23726` Isuzu Trooper I/II 的长短车身及封闭/敞开分支。
4. 随后处理 Voyager III/IV、Explorer、Blazer S10 等美系 SUV/MPV。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-12-kwh-27hp-46431 "Citroen Saxo (Phase I, 1996) 3-door 12 kWh (27 Hp) | Technical specs, data, battery, electric range, Dimensions"
[2]: https://www.edmunds.com/buick/skylark/1994/sedan/features-specs/ "Used 1994 Buick Skylark Sedan Specs & Features | Edmunds"
[3]: https://www.allopneus.com/vehicule/chrysler/voyager/voyager?utm_source=chatgpt.com "Pneu CHRYSLER VOYAGER : Pression et dimensions des pneus - Allopneus.com"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 完成 `23524` Citroën XM Y3 Break，确认 3.0 V6 旅行车外廓为 4963 × 1794 × 1464 mm。([汽车目录][1])
* 完成 `23547` Mazda 323 III BF Station Wagon；输入功率与前驱版本边界一致，建立五门旅行车尺寸组。([汽车目录][2])
* 完成 `23549` Opel Omega A Caravan。该 Ktype 跨越 1990 年改款，但核对到的 2.0i Caravan 外廓未形成需要拆组的可靠三维差异，因此保持单一尺寸组。([引擎详解][3])
* 完成 `23576` Isuzu Trooper I 2.6 封闭式 SUV，按三门短车身和五门长车身拆分，两种外廓不可共组。([五十铃驾驭空间][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射：103
* PENDING Ktype：36
* 已引用确认尺寸组：73
* 本轮首次创建/修正尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23524	23524	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-5D-01	HIGH	Y3五门旅行车外廓。	READY
23547	23547	Wagon	323 III	BF	5	EU-MAZDA-323-III-BF-WAGON-5D-01	HIGH	BF五门前驱旅行车外廓。	READY
23549	23549	Wagon	Omega A		5	EU-OPEL-OMEGA-A-WAGON-5D-01	MEDIUM	Omega A五门Caravan外廓。	READY
23576_3dr	23576	SUV	Trooper I	UBS17	3	EU-ISUZU-TROOPER-I-UBS17-SUV-3D-01	MEDIUM	三门短车身封闭式外廓。	READY
23576_5dr	23576	SUV	Trooper I	UBS17	5	EU-ISUZU-TROOPER-I-UBS17-SUV-5D-01	MEDIUM	五门长车身封闭式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-XM-Y3-WAGON-5D-01	4963	1794	1464	Automobile-Catalog 1993 Citroen XM Break V6	https://www.automobile-catalog.com/car/1993/541625/citroen_xm_break_v6.html
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430	AutoEvolution Mazda 323 BF Station Wagon; Auto-Data Mazda 323 III Station Wagon BF 1.6	https://www.autoevolution.com/cars/mazda-323-mk2-station-wagon-1989.html;https://www.auto-data.net/en/mazda-323-iii-station-wagon-bf-1.6-86hp-11192
EU-OPEL-OMEGA-A-WAGON-5D-01	4730	1772	1481	Automobile-Catalog Opel Omega Caravan GL 2.0i; EngineInDetail Opel Omega Caravan 2.0i Club	https://www.automobile-catalog.com/car/1987/57560/opel_omega_caravan_2_0i_gl.html;https://www.engineindetail.com/pa/opel-omega-caravan-2-0i-club-1991
EU-ISUZU-TROOPER-I-UBS17-SUV-3D-01	4122	1651	1844	Drive.Place Isuzu Trooper I 2.6 3-door	https://isuzu.drive.place/trooper/i/group_offroad_3d/396678
EU-ISUZU-TROOPER-I-UBS17-SUV-5D-01	4470	1651	1821	Drive.Place Isuzu Trooper I 2.6 5-door	https://isuzu.drive.place/trooper/i/group_offroad_5d/396491
```

## 下一步优先处理

1. 处理 `23517` Saab 900 I Sedan，核对 1987 年前后保险杠及车长变化。
2. 处理 `23725`、`23726` Isuzu Trooper II 的封闭式与软顶车身，避免与本轮 Trooper I 尺寸组混用。
3. 集中闭合 Voyager III、Voyager IV、Pontiac Trans Sport 和 Ford Explorer。
4. 随后处理 Ducato、Jumper、Transit、VW LT 等多轴距商用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1993/541625/citroen_xm_break_v6.html?utm_source=chatgpt.com "1993 Citroen XM Break V6 (man. 5) (model for Europe ) car ..."
[2]: https://www.automobile-catalog.com/make/mazda/323_3gen/323_3gen_wagon/1992.html?utm_source=chatgpt.com "1992 Mazda 323 3gen Wagon (BF) full range specs"
[3]: https://www.engineindetail.com/pa/opel-omega-caravan-2-0i-club-1991?utm_source=chatgpt.com "Opel Omega Caravan 2.0i Club 1991 - Specs, Review & ..."
[4]: https://isuzu.drive.place/trooper/i/group_offroad_3d/396678?utm_source=chatgpt.com "Isuzu Trooper I 2.6 MT 120 hp 3 door SUV — specifications"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 新增完成 9 个 Ktype，共 10 条 READY 映射：`23515`、`23621`、`23662`、`23678`、`23679`、`23718`、`23797`、`23834`、`23849`。
* `23679` 按三门和五门拆分，两种车身外部三维一致并共用一个尺寸组。
* `23678` 直接复用既有 Voyager I 尺寸组；本轮未重复输出该尺寸组。
* 首次创建 Jaguar XJ40、Pontiac Trans Sport I、Kia Cee'd II、Daewoo Lanos、Hyundai Elantra III、Jeep Grand Cherokee WJ、Lotus Esprit S3 和 Opel Insignia A Sports Tourer 尺寸组。([Zoomcar][1])
* Grand Cherokee、Esprit 与 Insignia 的宽度口径均已按不含后视镜数据闭合。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射：113
* PENDING Ktype：27
* 已引用确认尺寸组：81
* 本轮首次创建/修正尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23515	23515	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	HIGH		READY
23621	23621	MPV	Trans Sport I		3	EU-PONTIAC-TRANS-SPORT-I-MPV-3D-01	MEDIUM		READY
23662	23662	Hatchback	Cee'd II	JD	5	EU-KIA-CEED-II-HATCHBACK-5D-01	HIGH		READY
23678	23678	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23679_3dr	23679	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	HIGH	三门外廓。	READY
23679_5dr	23679	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	HIGH	五门外廓；三维与三门一致。	READY
23718	23718	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-01	HIGH		READY
23797	23797	SUV	Grand Cherokee II facelift 2003	WJ	5	EU-JEEP-GRAND-CHEROKEE-II-WJ-FACELIFT-SUV-01	HIGH		READY
23834	23834	Coupe	Esprit S3	Type 85	2	EU-LOTUS-ESPRIT-S3-COUPE-2D-01	HIGH		READY
23849	23849	Wagon	Insignia A facelift 2013		5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360	Zoomcar Jaguar XJ40 technical specifications	https://zoomcar.fr/fiche-technique/jaguar/xj40-modell-94-xj6-3-6-a-NAT65599.html
EU-PONTIAC-TRANS-SPORT-I-MPV-3D-01	4946	1886	1670	Auto Motor und Sport Pontiac Trans Sport technical data	https://www.auto-motor-und-sport.de/marken-modelle/pontiac/trans-sport/technische-daten/
EU-KIA-CEED-II-HATCHBACK-5D-01	4310	1780	1470	Auto-Data Kia Cee'd model specifications; Auto-Data Kia Cee'd II facelift 1.4 CVVT	https://www.auto-data.net/en/kia-ceed-model-1935;https://www.auto-data.net/en/kia-ceed-ii-facelift-2015-1.4-cvvt-100hp-41346
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	4074	1678	1432	Automobile-Catalog 1998 Daewoo Lanos 1.5 SX Hatchback	https://www.automobile-catalog.com/car/1998/555770/daewoo_lanos_1_5_sx_hatchback.html
EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-01	4495	1720	1425	Auto-Data Hyundai Elantra III 1.6 Sedan	https://www.auto-data.net/en/hyundai-elantra-iii-1.6-107hp-automatic-29321
EU-JEEP-GRAND-CHEROKEE-II-WJ-FACELIFT-SUV-01	4611	1858	1805	Auto-Data Jeep Grand Cherokee II WJ facelift 2.7 CRD	https://www.auto-data.net/en/jeep-grand-cherokee-ii-wj-facelift-2003-2.7-crd-163hp-4x4-automatic-1159
EU-LOTUS-ESPRIT-S3-COUPE-2D-01	4191	1854	1118	Automobile-Catalog 1982 Lotus Esprit S3	https://www.automobile-catalog.com/car/1982/1434635/lotus_esprit_s3.html
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513	Automobile-Catalog Opel Insignia Sports Tourer 2.0 CDTI 163 4x4	https://www.automobile-catalog.com/car/2013/2537810/opel_insignia_sports_tourer_2_0_cdti_ecoflex_163_4x4.html
```

## 下一步优先处理

1. 闭合 `23517` Saab 900 I Sedan 的生产期外廓边界。
2. 处理 `23725`、`23726` Isuzu Trooper II 的三门、五门及软顶分支。
3. 集中处理 `23587`、`23861` Voyager III 与 `23796` Voyager IV。
4. 处理 `23632` Blazer S10、`23643`、`23644` Explorer 和 `23859` Cherokee XJ。
5. 最后集中处理 Ducato、Jumper、C25、J5、Transit、VW LT 等多轴距商用车。

推进信号：CONTINUE

[1]: https://zoomcar.fr/fiche-technique/jaguar/xj40-modell-94-xj6-3-6-a-NAT65599.html?utm_source=chatgpt.com "Fiche technique JAGUAR XJ40 Modell -94 XJ6 3.6 A Berline 1989 65599 | zoomcar.fr"
[2]: https://www.auto-data.net/en/jeep-grand-cherokee-ii-wj-facelift-2003-2.7-crd-163hp-4x4-automatic-1159?utm_source=chatgpt.com "Jeep Grand Cherokee II (WJ, facelift 2003) 2.7 CRD (163 ..."


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 完成 Saab 900 I Sedan、Ford Explorer II U2 两个 Ktype、Chrysler Voyager IV 以及 Voyager/Grand Voyager III 两个组合 Ktype。
* `23587`、`23861` 均明确覆盖 Voyager III 与 Grand Voyager III，按标准轴距和长轴距拆分，共用两个稳定尺寸组。([Meyer Motoren][1])
* `23643`、`23644` 均对应 Explorer U2 五门车身，发动机功率差异不触发重复建组。([PKW Teile][2])
* `23796` 对应 Voyager IV RG/RS 的 2.5 CRD 120 HP 版本，链接标准轴距 Voyager IV 外廓。([Alkatrészek][3])
* 本轮新增 6 个 READY Ktype、8 条 READY 映射、5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射：121
* PENDING Ktype：21
* 已引用确认尺寸组：86
* 本轮首次创建/修正尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23517	23517	Sedan	900 I		4	EU-SAAB-900-I-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
23587_voyager	23587	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	MEDIUM	标准轴距Voyager外廓。	READY
23587_grand	23587	MPV	Grand Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	MEDIUM	长轴Grand Voyager外廓。	READY
23643	23643	SUV	Explorer II	U2	5	EU-FORD-EXPLORER-II-U2-SUV-5D-01	HIGH		READY
23644	23644	SUV	Explorer II	U2	5	EU-FORD-EXPLORER-II-U2-SUV-5D-01	HIGH		READY
23796	23796	MPV	Voyager IV	RG	5	EU-CHRYSLER-VOYAGER-IV-RG-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23861_voyager	23861	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	MEDIUM	标准轴距Voyager外廓。	READY
23861_grand	23861	MPV	Grand Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	MEDIUM	长轴Grand Voyager外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-900-I-SEDAN-4D-01	4680	1690	1422	Drive.Place Saab 900 I Sedan 2.0	https://saab.drive.place/900/i/group_sedan/424878
EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	4733	1950	1740	Auto-Data Chrysler Voyager III 2.5 TD	https://www.auto-data.net/en/chrysler-voyager-iii-2.5-td-116hp-14835
EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	5070	1950	1740	Auto-Data Chrysler Grand Voyager III 2.5 TD	https://www.auto-data.net/en/chrysler-grand-voyager-iii-2.5-td-115hp-14772
EU-FORD-EXPLORER-II-U2-SUV-5D-01	4790	1790	1800	Auto-Data Ford Explorer II 4.0 XLT	https://www.auto-data.net/en/ford-explorer-ii-4.0-xlt-162hp-7871
EU-CHRYSLER-VOYAGER-IV-RG-MPV-5D-01	4805	1995	1750	Auto-Data Chrysler Voyager IV 2.5 CRD TD	https://www.auto-data.net/en/chrysler-voyager-iv-2.5-crd-td-143hp-14827
```

## 下一步优先处理

1. 处理 `23725`、`23726` Isuzu Trooper II 的封闭式三门、五门及软顶分支。
2. 处理 `23859` Jeep Cherokee XJ 三门和五门，先解决现有来源间宽度、高度差异。
3. 闭合 `23632` Chevrolet Blazer S10 与剩余老款 SUV。
4. 集中处理 Doblò、Palio、Nubira、Mitsubishi Pajero Classic 等单一或少分支车型。
5. 最后批量处理 Jumper、C25、J5、Ducato、Transit、VW LT 和 Hyundai H-1 商用车分支。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/23861/chrysler/voyager_3_grand_voyager_3_gs_ns_/2_5_tdic_awd_23861?utm_source=chatgpt.com "2.5 TDiC AWD | Voyager 3/Grand Voyager 3 (GS, NS) | Chrysler | Manufacturers | Meyer Motoren"
[2]: https://www.pkwteile.de/autoteile/ford-usa-ersatzteile/explorer-u2/23643?utm_source=chatgpt.com "Ersatzteile FORD USA EXPLORER (U2) 4.0 207 PS Benzin 1996 - 2002 T40VSEX ❱❱❱ Teilekatalog online"
[3]: https://alkatreszek.hu/termekek/uzemanyag_rendszer/porlasztocsucs_befecskendezo_szelep/Chrysler/Voyager/voyager_iv_rg_rs_1999_09_2008_12?utm_source=chatgpt.com "Vásároljon CHRYSLER VOYAGER IV (RG, RS) 1999/09 2008/12 Porlasztócsúcs, befecskendező szelep autóalkatrészeket - Kovács"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 完成 `23661` Daewoo Nubira J100 五门两厢车映射并首次建组。([汽车配件商店][1])
* 完成 `23697` Morgan Plus 8 敞篷车映射并首次建组。([CarsGuide][2])
* 完成 `23808` Mitsubishi Pajero III Classic，按 `V68W` 三门短车身和 `V78W` 五门长车身拆分，首次创建两个尺寸组。([Meyer Motoren][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射：125
* PENDING Ktype：18
* 已引用确认尺寸组：90
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23661	23661	Hatchback	Nubira I	J100	5	EU-DAEWOO-NUBIRA-J100-HATCHBACK-5D-01	HIGH		READY
23697	23697	Convertible	Plus 8 Series 1		2	EU-MORGAN-PLUS-8-SERIES-1-CONVERTIBLE-01	MEDIUM		READY
23808_3dr	23808	SUV	Pajero III Classic	V68W	3	EU-MITSUBISHI-PAJERO-III-CLASSIC-V68W-SUV-3D-01	HIGH	V68W三门短车身。	READY
23808_5dr	23808	SUV	Pajero III Classic	V78W	5	EU-MITSUBISHI-PAJERO-III-CLASSIC-V78W-SUV-5D-01	HIGH	V78W五门长车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAEWOO-NUBIRA-J100-HATCHBACK-5D-01	4280	1699	1430	AutoEvolution Daewoo Nubira Hatchback 1.6	https://www.autoevolution.com/cars/daewoo-nubira-hatchback-2000.html
EU-MORGAN-PLUS-8-SERIES-1-CONVERTIBLE-01	3730	1580	1320	CarsGuide 1995 Morgan Plus dimensions	https://www.carsguide.com.au/morgan/plus/car-dimensions/1995
EU-MITSUBISHI-PAJERO-III-CLASSIC-V68W-SUV-3D-01	4295	1885	1845	Automobile-Catalog 2006 Mitsubishi Pajero 3.2 DI-D Classic 3-door	https://www.automobile-catalog.com/car/2006/2015180/mitsubishi_pajero_3_2_di-d_classic_3door.html
EU-MITSUBISHI-PAJERO-III-CLASSIC-V78W-SUV-5D-01	4810	1885	1855	Automobile-Catalog 2006 Mitsubishi Pajero 3.2 DI-D Classic 5-door	https://www.automobile-catalog.com/car/2006/2015285/mitsubishi_pajero_3_2_di-d_classic_5door.html
```

## 下一步优先处理

1. 批量闭合 `23647`、`23703` Fiat Doblò II Cargo与乘用车外廓。
2. 解决 `23859` Jeep Cherokee XJ 的改款前后及三门、五门边界。
3. 处理 `23650` Fiat Palio、`24063` Morris Mini 和 `23508` Renault Rapid。
4. 集中处理剩余 Jumper、C25、J5、Ducato、Transit、VW LT、Hyundai H-1 商用车分支。

推进信号：CONTINUE

[1]: https://www.buycarparts.co.uk/daewoo/nubira-klaj/23661/10213/coil-springs?utm_source=chatgpt.com "Coil spring DAEWOO Nubira Hatchback (J100) 1.6 103 hp Petrol ..."
[2]: https://www.carsguide.com.au/morgan/plus/car-dimensions/1995?utm_source=chatgpt.com "Morgan Plus Dimensions 1995 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[3]: https://www.meyermotoren.de/fahrzeuge/23808/mitsubishi/pajero_classic_v2_v6_v7_/3_2_di-d_v68w_v78w_?utm_source=chatgpt.com "3.2 DI-D (V68W, V78W) | Pajero Classic (V2, V6, V7) | MITSUBISHI | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 完成 `23647` Fiat Doblò II Cargo，按短轴低顶、长轴低顶、短轴高顶、长轴高顶拆分；官方技术规格确认 120 T-Jet 覆盖这四种外廓。
* 完成 `23703` Fiat Doblò II Kombi，按短轴和长轴拆分；120 T-Jet 未扩展到仅柴油配置的 Combi XL。
* Cargo 与 Kombi 外部三维完全相同的短轴、长轴车身复用同一尺寸组，没有按用途重复建组。
* 本轮新增 READY Ktype 2 个、READY 映射 6 条，首次创建尺寸组 4 个。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射：131
* PENDING Ktype：16
* 已引用确认尺寸组：94
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23647_swb_lowroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
23647_lwb_lowroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	HIGH	长轴低顶外廓。	READY
23647_swb_highroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
23647_lwb_highroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
23703_swb	23703	MPV	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	HIGH	短轴Kombi外廓。	READY
23703_lwb	23703	MPV	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	HIGH	长轴Kombi外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
```

## 下一步优先处理

1. 闭合 `23725`、`23726` Isuzu Trooper II 的三门、五门和软顶分支。
2. 处理 `23859` Jeep Cherokee XJ 与 `23632` Chevrolet Blazer S10。
3. 完成 `23508` Renault Rapid、`23650` Fiat Palio、`24063` Morris Mini。
4. 最后集中处理剩余 Jumper、C25、J5、Ducato、Transit、VW LT 与 Hyundai H-1 商用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 完成 Renault Rapid、Chevrolet Blazer S10 II、Fiat Palio I、Isuzu Trooper II、Jeep Cherokee XJ 与 Morris Mini，共新增 7 个 READY Ktype、12 条映射。
* `23632` 按两门短车身与四门长车身拆分；两种 Blazer S10 II 外廓长度和高度不同。([AUTODOC][1])
* `23725` 按三门、五门拆分，`23726` 单独对应软顶外廓。当前三维与累计表中的 Trooper I 组不同，因此创建 Trooper II 新组，未覆盖既有尺寸事实。([Autodoc][2])
* `23859` 的生产期跨越 Cherokee XJ 改款节点，按改款前、改款后两种已确认外廓拆分。([汽车目录][3])
* 本轮首次创建 10 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射：143
* PENDING Ktype：9
* 已引用确认尺寸组：104
* 本轮首次创建/修正尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23508_van	23508	Van	Rapid I	F40		EU-RENAULT-RAPID-I-BODY-01	MEDIUM	厢式车外廓。	READY
23508_mpv	23508	MPV	Rapid I	G40		EU-RENAULT-RAPID-I-BODY-01	MEDIUM	乘用组合车外廓；三维与厢式车一致。	READY
23632_2dr	23632	SUV	Blazer S10 II		2	EU-CHEVROLET-BLAZER-S10-II-SUV-2D-01	HIGH	两门短车身外廓。	READY
23632_4dr	23632	SUV	Blazer S10 II		4	EU-CHEVROLET-BLAZER-S10-II-SUV-4D-01	HIGH	四门长车身外廓。	READY
23650_3dr	23650	Hatchback	Palio I facelift 2004	178BX	3	EU-FIAT-PALIO-I-178-HATCHBACK-01	MEDIUM	三门外廓。	READY
23650_5dr	23650	Hatchback	Palio I facelift 2004	178BX	5	EU-FIAT-PALIO-I-178-HATCHBACK-01	MEDIUM	五门外廓；三维与三门一致。	READY
23725_3dr	23725	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-UB-SUV-3D-01	MEDIUM	三门短车身封闭式外廓。	READY
23725_5dr	23725	SUV	Trooper II	UB	5	EU-ISUZU-TROOPER-II-UB-SUV-5D-01	MEDIUM	五门长车身封闭式外廓。	READY
23726	23726	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-UB-SUV-SOFTTOP-01	MEDIUM	三门短车身软顶外廓。	READY
23859_prefl	23859	SUV	Cherokee XJ pre-facelift	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	MEDIUM	改款前五门外廓。	READY
23859_facelift	23859	SUV	Cherokee XJ facelift	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	MEDIUM	改款后五门外廓。	READY
24063	24063	Hatchback	Mini Mk II–IV	ADO15	2	EU-MORRIS-MINI-ADO15-HATCHBACK-2D-01	MEDIUM	生产期内外部三维一致。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-RAPID-I-BODY-01	4056	1566	1776	Auto.ru Renault Rapid 1.4 specifications	https://auto.ru/catalog/cars/renault/rapid/25004691/25004702/specifications/
EU-CHEVROLET-BLAZER-S10-II-SUV-2D-01	4437	1689	1699	Automobile-Catalog 1995 Chevrolet Blazer 2-door 4WD	https://www.automobile-catalog.com/car/1995/482885/chevrolet_blazer_2-door_4wd_automatic.html
EU-CHEVROLET-BLAZER-S10-II-SUV-4D-01	4602	1689	1702	Automobile-Catalog 1995 Chevrolet Blazer LT 4-door AWD	https://www.automobile-catalog.com/car/1995/482930/chevrolet_blazer_lt_4-door_awd_automatic.html
EU-FIAT-PALIO-I-178-HATCHBACK-01	3827	1634	1446	Automobile-Catalog 2005 Fiat Palio ELX 1.4	https://www.automobile-catalog.com/car/2005/734810/fiat_palio_elx_1_4.html
EU-ISUZU-TROOPER-II-UB-SUV-3D-01	4145	1650	1815	Automobile-Catalog 1991 Isuzu Trooper 2.6i 3-door	https://www.automobile-catalog.com/car/1991/1260155/isuzu_trooper_2_6i_cat.html
EU-ISUZU-TROOPER-II-UB-SUV-5D-01	4495	1650	1815	Automobile-Catalog 1991 Isuzu Trooper Long 5-door 2.6i	https://www.automobile-catalog.com/car/1991/1260215/isuzu_trooper_long_5-door_2_6i_cat.html
EU-ISUZU-TROOPER-II-UB-SUV-SOFTTOP-01	4145	1650	1830	Automobile-Catalog 1991 Isuzu Trooper Canvas Top 2.6i	https://www.automobile-catalog.com/car/1991/1260185/isuzu_trooper_canvas-top_2_6i_cat.html
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700	Automobile-Catalog 1996 Jeep Cherokee 2.5 TD Limited	https://www.automobile-catalog.com/car/1996/1314380/jeep_cherokee_2_5_td_limited.html
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625	Automobile-Catalog 1997 Jeep Cherokee 2.5 TD Limited	https://www.automobile-catalog.com/car/1997/1319420/jeep_cherokee_2_5_td_limited.html
EU-MORRIS-MINI-ADO15-HATCHBACK-2D-01	3054	1410	1346	Automobile-Catalog 1967 Morris Mini-Cooper Mk II	https://www.automobile-catalog.com/car/1967/2034095/morris_mini-cooper_mk_ii.html
```

## 下一步优先处理

1. 集中闭合剩余 9 个商用车 Ktype：`23657`、`23681`、`23798`、`23812`、`23831`、`23844`、`23846`、`23848`、`23856`。
2. 优先匹配累计缓存中的 Fiat Ducato II、Ford Transit 系列尺寸组。
3. 对 Jumper I、C25、J5、VW LT I/II 和 Hyundai H-1，仅补建尚未存在且物理边界明确的轴距、车顶或底盘分支。

推进信号：CONTINUE

[1]: https://www.autodoc.lv/auto-dalas/bremzu_uzlikas-10130/chevrolet/blazer-s10/blazer-s10/23632-4-3-awd?utm_source=chatgpt.com "CHEVROLET Blazer S10 II 4.3 AWD Bremžu kluči"
[2]: https://www.autodoc.co.uk/car-parts/steering-links-control-arm-trailing-link-diagonal-arm-10671/isuzu/trooper/trooper-ub/23725-2-6-4x4?utm_source=chatgpt.com "ISUZU Trooper II Off-Road (UB) 2.6 4x4 Suspension arm - 116 hp ..."
[3]: https://www.automobile-catalog.com/car/1996/1314380/jeep_cherokee_2_5_td_limited.html?utm_source=chatgpt.com "1996 Jeep Cherokee 2.5 TD Limited Specs Review (85 kW / 116 PS / 114 hp) (up to mid-year 1996 for Europe )"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 完成 `23848` Ford Transit V185 前驱厢式车，按 SWB/MWB/LWB 与低顶/中顶/高顶拆分为 6 个物理外廓。官方规格表同时列出含镜/不含镜宽度，统一采用不含后视镜的 `1974 mm`；高度采用各配置的最大空载车高。([Dezo's Garage][1])
* 完成 `23856` Volkswagen LT II 2.8 TDI Bus，按中轴高顶和长轴高顶拆分。该发动机对应两种确认外廓，宽度均为 `1933 mm`。([VehicleScore][2])
* 本轮新增 READY Ktype 2 个、READY 映射 8 条，首次创建尺寸组 8 个。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射：151
* PENDING Ktype：7
* 已引用确认尺寸组：112
* 本轮首次创建/修正尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23848_swb_lowroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱短轴低顶外廓。	READY
23848_swb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱短轴中顶外廓。	READY
23848_mwb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱中轴中顶外廓。	READY
23848_mwb_highroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱中轴高顶外廓。	READY
23848_lwb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱长轴中顶外廓。	READY
23848_lwb_highroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱长轴高顶外廓。	READY
23856_mwb_highroof	23856	MPV	LT II			EU-VW-LT-II-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶Bus外廓。	READY
23856_lwb_highroof	23856	MPV	LT II			EU-VW-LT-II-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	4834	1974	1974	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	4834	1974	2313	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	5201	1974	2309	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	5201	1974	2529	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	5651	1974	2303	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	5651	1974	2524	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-VW-LT-II-BUS-MWB-HIGHROOF-01	5585	1933	2570	Drom Volkswagen LT II dimensions;VehicleScore Volkswagen LT dimensions	https://www.drom.ru/catalog/lcv/volkswagen/lt/specs/dimensions/;https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
EU-VW-LT-II-BUS-LWB-HIGHROOF-01	6535	1933	2570	Drom Volkswagen LT II dimensions;VehicleScore Volkswagen LT dimensions	https://www.drom.ru/catalog/lcv/volkswagen/lt/specs/dimensions/;https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
```

## 下一步优先处理

1. 集中闭合 Sevel 商用车组：`23657` Jumper I、`23681` C25、`23812` J5、`23831` Ducato II Bus。
2. 处理 `23844`、`23846` Volkswagen LT I Syncro 底盘，重点区分轴距、LT 级别及四驱车高。
3. 最后闭合 `23798` Hyundai H-1 底盘驾驶室外廓。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf "Transit 2002.75 SPEC.qxd"
[2]: https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt?utm_source=chatgpt.com "VOLKSWAGEN LT Dimensions - Length, Width, Height"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 完成 `23657` Citroën Jumper I 2.0 4×4 Van。该 Ktype 确认覆盖两套不同外廓，按 `L1H1` 与 `L2H2` 拆分；两套规格均为四驱 Fourgon，不能合并。([Motoro][1])
* 完成 `23798` Hyundai H-1 I 2.5 CRDi 底盘驾驶室，确认单一外廓为 `4695 × 1820 × 1880 mm`。([汽车数据1][2])
* 本轮新增 2 个 READY Ktype、3 条 READY 映射和 3 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射：154
* PENDING Ktype：5
* 已引用确认尺寸组：115
* 本轮首次创建/修正尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23657_l1h1	23657	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-L1H1-01	HIGH	L1H1四驱厢式外廓。	READY
23657_l2h2	23657	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-L2H2-01	HIGH	L2H2四驱厢式外廓。	READY
23798	23798	Pickup	H-1 I		2	EU-HYUNDAI-H1-I-CHASSIS-CAB-01	HIGH	单排底盘驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-I-230L-VAN-4X4-L1H1-01	4655	1998	2150	Motoro Citroën Jumper 2.0i 4x4 technical specifications	https://motoro.ch/en/fiche-technique/citroen/jumper-2-0i-4x4
EU-CITROEN-JUMPER-I-230L-VAN-4X4-L2H2-01	5005	1998	2470	Motoro Citroën Jumper 2.0i 4x4 technical specifications	https://motoro.ch/en/fiche-technique/citroen/jumper-2-0i-4x4
EU-HYUNDAI-H1-I-CHASSIS-CAB-01	4695	1820	1880	Autodata1 Hyundai H-1 I Starex 2.5 CRDI Chassis	https://www.autodata1.com/en/car/hyundai/h-1/h-1-i-starex-25-crdi-140-hp
```

## 下一步优先处理

1. 闭合 `23681` Citroën C25 2.5 D 底盘的轴距和单排驾驶室分支。
2. 闭合 `23812` Peugeot J5 2.5 DT Van 的短轴、长轴及车顶组合。
3. 确认 `23831` Fiat Ducato 244 Bus 2.8 JTD 145 HP 实际覆盖的车身长度和车顶配置。
4. 最后解决 `23844`、`23846` VW LT I Syncro 底盘的四驱专属车高，避免误用普通后驱底盘尺寸。

推进信号：CONTINUE

[1]: https://motoro.ch/en/fiche-technique/citroen/jumper-2-0i-4x4 "motoro.ch"
[2]: https://www.autodata1.com/en/car/hyundai/h-1/h-1-i-starex-25-crdi-140-hp "Hyundai H-1 I Starex 2.5 CRDI (140 Hp)"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 完成 `23681` Citroën C25 2.5 D 底盘车型，按短轴、中轴、长轴 1400 级和长轴 1800 级拆分。
* 短轴与中轴的轴距不同，但外部三维相同，因此保留两个派生 `id` 并共用一个尺寸组；长轴 1400 与 1800 车型高度不同，分别建组。
* Ktype 生产期横跨 `280/290` 系列，无法为每条分支唯一指定一个 BodyCode，因此 `BodyCode` 留空，不写组合代码。([AutoDoc][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射：158
* PENDING Ktype：4
* 已引用确认尺寸组：118
* 本轮首次创建/修正尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23681_swb	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	短轴单排底盘外廓。	READY
23681_mwb	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	中轴单排底盘外廓；三维与短轴相同。	READY
23681_lwb_1400	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	长轴1400级单排底盘外廓。	READY
23681_lwb_1800	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	MEDIUM	长轴1800级单排底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108	Zoomcar Citroën C25 Chassis Cab 1400 D Court;Zoomcar Citroën C25 Chassis Cab 1400 D Moyen	https://zoomcar.fr/fiche-technique-utilitaire/citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-court-NAT56141.html;https://zoomcar.fr/fiche-technique-utilitaire/top-citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-moyen-NAT56140.html
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108	Zoomcar Citroën C25 Chassis Cab 1400 D Long	https://zoomcar.fr/fiche-technique-utilitaire/top-citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-long-NAT56144.html
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080	Zoomcar Citroën C25 Chassis Cab 1800 D Long	https://zoomcar.fr/fiche-technique/citroen/c25-chassis-cabine-c25-chassis-cab-1800-d-long-NAT56155.html
```

## 下一步优先处理

1. 闭合 `23812` Peugeot J5 290L Van 的短轴、长轴及车顶分支。
2. 确认 `23831` Fiat Ducato 244 Bus 2.8 JTD Power 实际覆盖的乘用车身组合，并优先复用既有 X244 尺寸组。
3. 解决 `23844` LT 35 与 `23846` LT 55 Syncro 底盘外廓；目前车型目录分级与官方四驱车身矩阵仍需对齐，禁止直接按普通后驱 LT 尺寸落盘。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/tailgate-struts-10926/citroen/c25/c25-platform-chassis-280-290/23681-2-5-d?utm_source=chatgpt.com "Boot struts Citroen C25 280 2.5 D 75 hp Diesel 55 kW 1983"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 完成 `23846` Volkswagen LT I 2.4 TD 4×4 底盘车型，按单排货台、双排货台、单排底盘和双排底盘拆分。官方资料确认 LT 4×4 仅采用 `2950 mm` 轴距，并覆盖 Pritsche、Doppelkabine 与 Fahrgestell；双排货台整车尺寸直接为 `5330 × 2140 × 2310 mm`。其余分支采用 Volkswagen 官方 LT 对应车身的长度、宽度，以及 LT 4×4 的加高车身高度闭合。
* `23844` 暂不强行关联：输入车型族为 `LT 28-35 I Syncro`，但 Volkswagen 官方 LT 4×4 资料明确限定为 LT40/LT45，车型级别边界存在实质冲突。
* 将尚未闭合的 `23812`、`23831`、`23844` 正式落为 PENDING 映射行，避免输入 Ktype 在累计映射中缺行。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射：162
* PENDING Ktype：3
* PENDING 映射：3
* 已引用确认尺寸组：122
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23812	23812	Van	J5 I	290L			LOW	候选为短轴、长轴及不同车顶的J5 290厢式车外廓。	PENDING: 2.5 DT对应的轴距与车顶组合尚未闭合
23831	23831	MPV	Ducato II	244			LOW	候选为Ducato X244 Bus车身。	PENDING: 2.8 JTD Power实际覆盖的Bus长度与车顶组合尚未闭合
23844	23844	Pickup	LT I 4x4	Typ 21			LOW	输入车型族与官方LT4x4级别边界冲突。	PENDING: 官方资料仅确认LT40/LT45 4x4，无法确认LT28-35映射边界
23846_pickup_singlecab	23846	Pickup	LT I 4x4	Typ 21	2	EU-VW-LT-I-4X4-PICKUP-MWB-SINGLECAB-01	MEDIUM	中轴单排货台外廓。	READY
23846_pickup_doublecab	23846	Pickup	LT I 4x4	Typ 21	4	EU-VW-LT-I-4X4-PICKUP-MWB-DOUBLECAB-01	HIGH	中轴双排货台外廓。	READY
23846_chassis_singlecab	23846	Pickup	LT I 4x4	Typ 21	2	EU-VW-LT-I-4X4-CHASSIS-CAB-MWB-01	MEDIUM	中轴单排底盘驾驶室外廓。	READY
23846_chassis_doublecab	23846	Pickup	LT I 4x4	Typ 21	4	EU-VW-LT-I-4X4-CHASSIS-DOUBLECAB-MWB-01	MEDIUM	中轴双排底盘驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-LT-I-4X4-PICKUP-MWB-SINGLECAB-01	5630	2140	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-4X4-PICKUP-MWB-DOUBLECAB-01	5330	2140	2310	Volkswagen AG LT 4x4 action information	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf
EU-VW-LT-I-4X4-CHASSIS-CAB-MWB-01	5245	2050	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-4X4-CHASSIS-DOUBLECAB-MWB-01	5245	2050	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
```

## 下一步优先处理

1. 先闭合 `23831` Fiat Ducato 244 Bus 2.8 JTD Power，并优先关联已有 X244 尺寸组。
2. 再闭合 `23812` Peugeot J5 290L 2.5 DT 的轴距与车顶组合。
3. 最后处理 `23844`：优先查明 Ktype 是否误归入 LT28-35 车型族；确认后关联现有 LT 4×4 组或单独保留正确物理分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 修正 `23844` 的阻塞原因：该 Ktype 确实对应 **VW LT 35 Pritsche/Fahrgestell 2.4 TD Syncro 95 PS、ACL、1992–1996**，上一轮“仅有 LT40/LT45 4×4”的冲突判断不适用于该 Ktype。当前仅剩底盘/货台分支及 Syncro 专属高度未闭合。([Autodoc][1])
* `23812` 已锁定为 **Peugeot J5 Kasten 290L、2.5 DT、CRD93L、前驱**；发动机和车身系列不再存疑，但该 Ktype 覆盖的轴距及车顶组合仍未确认。([Allegro][2])
* `23831` 已锁定为 **Fiat Ducato Bus 244/Z、2.8 JTD Power、8140.43N、145 HP、2004–2006**；仍需确定 Bus 实际覆盖的长度和车顶组合，不能直接把全部 X244 Van 尺寸组套入。([Autodoc][3])
* 本轮未新建或修改尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射：162
* PENDING Ktype：3
* PENDING 映射：3
* 已引用确认尺寸组：122
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23812	23812	Van	J5 I	290L			LOW	已确认CRD93L前驱厢式车型；候选涉及不同轴距和车顶外廓。	PENDING: 2.5 DT实际覆盖的轴距与车顶组合尚未闭合
23831	23831	MPV	Ducato II	244			LOW	已确认8140.43N的145 HP Bus车型；不能直接套用全部X244厢式车分支。	PENDING: 2.8 JTD Power Bus实际覆盖的长度与车顶组合尚未闭合
23844	23844	Pickup	LT I	281-363			LOW	已确认LT35 2.4 TD Syncro ACL底盘车型存在。	PENDING: 货台与底盘驾驶室分支及Syncro专属高度尚未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查明 `23831` 的 X244 Bus 车身型号矩阵，优先复用已有尺寸组。
2. 查明 `23812` 的 J5 290L 2.5 DT 轴距和车顶适用范围。
3. 对齐 `23844` 的 LT35 Syncro 货台/底盘分支，并确认四驱状态下的车高后完成最终闭合。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/motor-windscreen-wipers-10234/vw/lt/lt-28-35-i-platform-chassis-281-363/23844-2-4-td-syncro "Wiper motor for VW LT 35 Platform 2.4 TD Syncro 95 hp Diesel 1992 - 1996 ACL | AUTODOC"
[2]: https://allegro.pl/oferta/klosz-lampy-tyl-iveco-daily-00-le-06-truck-84-96-17740039360?utm_source=chatgpt.com "KLOSZ LAMPY TYŁ IVECO DAILY 00&gt; LE &gt;06 TRUCK 84-96 5901797021672 za 21.00PLN z Rąbień - Allegro - (17740039360)"
[3]: https://www.autodoc.co.uk/car-parts/inner-tie-rod-10298/fiat/ducato/ducato-bus-244-z/23831-2-8-jtd?utm_source=chatgpt.com "Fiat Ducato 244 2.8 JTD Inner tie rod (145 hp Diesel 8140.43N)"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* `23831` 已闭合为 Ducato X244 **中轴标准顶 Panorama**，直接复用既有尺寸组 `EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01`，不重复建立尺寸组。官方车型矩阵将 8140.43N 的 2.8 JTD Power 配置列入中轴 Panorama，既有组尺寸为 5099 × 2024 × 2150 mm。([汽车手册在线][1])
* `23812` 已按 J5 290L 厢式车的短轴/长轴及标准顶/高顶拆成四个外廓，首次创建四个尺寸组。J5 资料确认两种车长为 4759 mm、5489 mm，宽度均为 1965 mm，标准顶与高顶分别为 2108 mm、2420 mm。([WheelsAge][2])
* `23844` 仍是唯一 PENDING：现有 Volkswagen 官方普通 LT 资料可确认 LT35 货台的基础三维，但尚未直接确认 1992–1996 LT35 Syncro 的专属整车高度，不能机械套用普通后驱高度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* READY 映射：167
* PENDING Ktype：1
* PENDING 映射：1
* 已引用确认尺寸组：126
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23812_swb_lowroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
23812_swb_highroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
23812_lwb_lowroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
23812_lwb_highroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
23831	23831	MPV	Ducato II	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	HIGH	中轴标准顶Panorama外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-J5-I-VAN-SWB-LOWROOF-01	4759	1965	2108	Peugeot Range Commercials official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf
EU-PEUGEOT-J5-I-VAN-SWB-HIGHROOF-01	4759	1965	2420	Peugeot Range Commercials official brochure;WheelsAge Peugeot J5 Van 1300 High Roof	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf;https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof/specifications
EU-PEUGEOT-J5-I-VAN-LWB-LOWROOF-01	5489	1965	2108	Peugeot Range Commercials official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf
EU-PEUGEOT-J5-I-VAN-LWB-HIGHROOF-01	5489	1965	2420	Peugeot Range Commercials official brochure;WheelsAge Peugeot J5 Van 1300 High Roof Long	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf;https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof_long/specifications
```

## 下一步优先处理

1. 只处理 `23844`：确认 LT35 2.4 TD Syncro 的货台/底盘分支及四驱状态下的完整车高。
2. 闭合后立即执行一次机械检查，并在下一条回复输出两张最终完整 TSV、两个指定下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/fiat-ducato-244-2005-3-g-owners-manual/4/?srch=automatic&utm_source=chatgpt.com "automatic FIAT DUCATO 244 2005 3.G Owner's Guide (258 Pages)"
[2]: https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof_long/specifications?utm_source=chatgpt.com "Specifications of Peugeot J5 Van 1300 High Roof Long ..."


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 最后一个阻塞 Ktype `23844` 已闭合。精确车型目录确认其为 VW LT 35 2.4 TD Syncro 95 PS、ACL、Pritsche/Fahrgestell；按单排货台、双排货台、单排底盘、双排底盘关联既有 LT I 4×4 尺寸组，不重复建组。([AUTODOC][1])
* 已完成固定表头、唯一主键、映射引用、正整数三维、来源字段和下载文件检查。
* 当前批次不存在 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：171
* PENDING：0
* DIMENSION_GROUP：127
* 唯一 `id`：171
* 唯一 `DIMENSION_GROUP_ID`：127
* 映射引用全部闭合，无孤立尺寸组。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23491_van	23491	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23491_mpv	23491	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23492_van	23492	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23492_mpv	23492	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23493_van	23493	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23493_mpv	23493	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23494_van	23494	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23494_mpv	23494	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23495_van	23495	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-VAN-01	HIGH	厢式车外廓。	READY
23495_mpv	23495	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH	乘用MPV外廓。	READY
23496	23496	Hatchback	Cuore VII	L276	5	EU-DAIHATSU-CUORE-VII-L276-HATCHBACK-5D-01	HIGH		READY
23497_3dr	23497	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门外廓。	READY
23497_5dr	23497	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门外廓。	READY
23498_swb_lowroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
23498_swb_highroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
23498_lwb_lowroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	长轴低顶外廓。	READY
23498_lwb_highroof	23498	Van	Vivaro A	X83		EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
23499_swb	23499	MPV	Vivaro A	X83		EU-OPEL-VIVARO-A-BUS-SWB-01	HIGH	短轴Bus外廓。	READY
23499_lwb	23499	MPV	Vivaro A	X83		EU-OPEL-VIVARO-A-BUS-LWB-01	HIGH	长轴Bus外廓。	READY
23500_l1h1	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H1-01	HIGH	L1H1外廓。	READY
23500_l1h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H2-01	HIGH	L1H2外廓。	READY
23500_l2h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L2H2-01	HIGH	L2H2外廓。	READY
23500_l3h2	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H2-01	HIGH	L3H2外廓。	READY
23500_l3h3	23500	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H3-01	HIGH	L3H3外廓。	READY
23501_l1h1	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	HIGH	L1H1 Bus外廓。	READY
23501_l2h2	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	HIGH	L2H2 Bus外廓。	READY
23501_l3h3	23501	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	HIGH	L3H3 Bus外廓。	READY
23502_chassis_mwb	23502	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘外廓。	READY
23502_chassis_lwb	23502	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘外廓。	READY
23502_crew_lwb	23502	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	长轴双排底盘外廓。	READY
23503_l1h1	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	HIGH	L1H1 Bus外廓。	READY
23503_l2h2	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	HIGH	L2H2 Bus外廓。	READY
23503_l3h3	23503	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	HIGH	L3H3 Bus外廓。	READY
23504_l1h1	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H1-01	HIGH	L1H1外廓。	READY
23504_l1h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L1H2-01	HIGH	L1H2外廓。	READY
23504_l2h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L2H2-01	HIGH	L2H2外廓。	READY
23504_l3h2	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H2-01	HIGH	L3H2外廓。	READY
23504_l3h3	23504	Van	Movano A	X70		EU-OPEL-MOVANO-A-VAN-L3H3-01	HIGH	L3H3外廓。	READY
23505_chassis_mwb	23505	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘外廓。	READY
23505_chassis_lwb	23505	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘外廓。	READY
23505_crew_lwb	23505	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	长轴双排底盘外廓。	READY
23508_van	23508	Van	Rapid I	F40		EU-RENAULT-RAPID-I-BODY-01	MEDIUM	厢式车外廓。	READY
23508_mpv	23508	MPV	Rapid I	G40		EU-RENAULT-RAPID-I-BODY-01	MEDIUM	乘用组合车外廓；三维与厢式车一致。	READY
23515	23515	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	HIGH		READY
23517	23517	Sedan	900 I		4	EU-SAAB-900-I-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
23524	23524	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-5D-01	HIGH	Y3五门旅行车外廓。	READY
23539	23539	Convertible	306 Cabrio facelift 1997	7D	2	EU-PEUGEOT-306-I-CONVERTIBLE-FACELIFT-01	HIGH	1997改款敞篷外廓。	READY
23547	23547	Wagon	323 III	BF	5	EU-MAZDA-323-III-BF-WAGON-5D-01	HIGH	BF五门前驱旅行车外廓。	READY
23549	23549	Wagon	Omega A		5	EU-OPEL-OMEGA-A-WAGON-5D-01	MEDIUM	Omega A五门Caravan外廓。	READY
23576_3dr	23576	SUV	Trooper I	UBS17	3	EU-ISUZU-TROOPER-I-UBS17-SUV-3D-01	MEDIUM	三门短车身封闭式外廓。	READY
23576_5dr	23576	SUV	Trooper I	UBS17	5	EU-ISUZU-TROOPER-I-UBS17-SUV-5D-01	MEDIUM	五门长车身封闭式外廓。	READY
23586	23586	Sedan	Biturbo 420 Si	AM332	4	EU-MASERATI-BITURBO-420-SI-SEDAN-01	HIGH	420 Si四门轿车外廓。	READY
23587_voyager	23587	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	MEDIUM	标准轴距Voyager外廓。	READY
23587_grand	23587	MPV	Grand Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	MEDIUM	长轴Grand Voyager外廓。	READY
23621	23621	MPV	Trans Sport I		3	EU-PONTIAC-TRANS-SPORT-I-MPV-3D-01	MEDIUM		READY
23624	23624	Sedan	Taurus III		4	EU-FORD-TAURUS-III-SEDAN-4D-01	MEDIUM	Taurus III四门轿车外廓。	READY
23625	23625	Wagon	Taurus III		5	EU-FORD-TAURUS-III-WAGON-5D-01	MEDIUM	Taurus III五门旅行车外廓。	READY
23632_2dr	23632	SUV	Blazer S10 II		2	EU-CHEVROLET-BLAZER-S10-II-SUV-2D-01	HIGH	两门短车身外廓。	READY
23632_4dr	23632	SUV	Blazer S10 II		4	EU-CHEVROLET-BLAZER-S10-II-SUV-4D-01	HIGH	四门长车身外廓。	READY
23634	23634	Sedan	Skylark VII	N	4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
23636	23636	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门轿车外廓。	READY
23638	23638	Coupe	Beretta	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	两门Z26外廓。	READY
23642	23642	Convertible	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH		READY
23643	23643	SUV	Explorer II	U2	5	EU-FORD-EXPLORER-II-U2-SUV-5D-01	HIGH		READY
23644	23644	SUV	Explorer II	U2	5	EU-FORD-EXPLORER-II-U2-SUV-5D-01	HIGH		READY
23647_swb_lowroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
23647_lwb_lowroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	HIGH	长轴低顶外廓。	READY
23647_swb_highroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
23647_lwb_highroof	23647	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
23650_3dr	23650	Hatchback	Palio I facelift 2004	178BX	3	EU-FIAT-PALIO-I-178-HATCHBACK-01	MEDIUM	三门外廓。	READY
23650_5dr	23650	Hatchback	Palio I facelift 2004	178BX	5	EU-FIAT-PALIO-I-178-HATCHBACK-01	MEDIUM	五门外廓；三维与三门一致。	READY
23657_l1h1	23657	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-L1H1-01	HIGH	L1H1四驱厢式外廓。	READY
23657_l2h2	23657	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-L2H2-01	HIGH	L2H2四驱厢式外廓。	READY
23659_3dr	23659	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-F08-HATCHBACK-3D-01	HIGH	F08三门外廓。	READY
23659_5dr	23659	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-F48-HATCHBACK-5D-01	HIGH	F48五门外廓。	READY
23660	23660	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-F35-WAGON-5D-01	HIGH		READY
23661	23661	Hatchback	Nubira I	J100	5	EU-DAEWOO-NUBIRA-J100-HATCHBACK-5D-01	HIGH		READY
23662	23662	Hatchback	Cee'd II	JD	5	EU-KIA-CEED-II-HATCHBACK-5D-01	HIGH		READY
23674	23674	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23675	23675	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23678	23678	MPV	Voyager I	AS	5	EU-CHRYSLER-VOYAGER-I-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23679_3dr	23679	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	HIGH	三门外廓。	READY
23679_5dr	23679	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	HIGH	五门外廓；三维与三门一致。	READY
23681_swb	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	短轴单排底盘外廓。	READY
23681_mwb	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	中轴单排底盘外廓；三维与短轴相同。	READY
23681_lwb_1400	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	长轴1400级单排底盘外廓。	READY
23681_lwb_1800	23681	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	MEDIUM	长轴1800级单排底盘外廓。	READY
23685	23685	Sedan	Astra G	F69	4	EU-OPEL-ASTRA-G-F69-SEDAN-4D-01	HIGH		READY
23695	23695	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
23697	23697	Convertible	Plus 8 Series 1		2	EU-MORGAN-PLUS-8-SERIES-1-CONVERTIBLE-01	MEDIUM		READY
23700	23700	Van	Panda I	141A	3	EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	HIGH	三门前驱厢式外廓。	READY
23701	23701	Van	Panda I	141A	3	EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	HIGH	三门四驱厢式外廓。	READY
23703_swb	23703	MPV	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	HIGH	短轴Kombi外廓。	READY
23703_lwb	23703	MPV	Doblò II	263		EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	HIGH	长轴Kombi外廓。	READY
23718	23718	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-01	HIGH		READY
23722	23722	Wagon	307 I		5	EU-PEUGEOT-307-I-FACELIFT-WAGON-01	HIGH	改款旅行车外廓。	READY
23725_3dr	23725	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-UB-SUV-3D-01	MEDIUM	三门短车身封闭式外廓。	READY
23725_5dr	23725	SUV	Trooper II	UB	5	EU-ISUZU-TROOPER-II-UB-SUV-5D-01	MEDIUM	五门长车身封闭式外廓。	READY
23726	23726	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-UB-SUV-SOFTTOP-01	MEDIUM	三门短车身软顶外廓。	READY
23728	23728	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4F2-01	HIGH	改款前轿车外廓。	READY
23729	23729	Convertible	350Z Roadster facelift 2007	Z33	2	EU-NISSAN-350Z-Z33-ROADSTER-FACELIFT-01	HIGH	313 HP改款Roadster外廓。	READY
23735	23735	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
23736	23736	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
23739	23739	Sedan	Epica V200	V200	4	EU-CHEVROLET-EPICA-V200-SEDAN-01	HIGH		READY
23742	23742	SUV	Actyon I	C100	5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	HIGH		READY
23750	23750	Convertible	Eclipse Spyder III (3G)	D53A	2	EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	HIGH	D53A敞篷外廓。	READY
23751	23751	Convertible	Eclipse Spyder III (3G)	D53A	2	EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	HIGH	D53A敞篷外廓。	READY
23756	23756	Sedan	Caprice IV		4	EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23757_prefl	23757	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23757_facelift	23757	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23758_prefl	23758	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23758_facelift	23758	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23759_prefl	23759	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	HIGH	跨越已确认的改款前外廓。	READY
23759_facelift	23759	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	跨越已确认的改款后外廓。	READY
23760	23760	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH	改款前旅行车外廓。	READY
23761	23761	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23762	23762	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23763	23763	Sedan	Century IV		4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH	改款轿车外廓。	READY
23764	23764	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23795	23795	Wagon	Golf V	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
23796	23796	MPV	Voyager IV	RG	5	EU-CHRYSLER-VOYAGER-IV-RG-MPV-5D-01	MEDIUM	标准轴距五门外廓。	READY
23797	23797	SUV	Grand Cherokee II facelift 2003	WJ	5	EU-JEEP-GRAND-CHEROKEE-II-WJ-FACELIFT-SUV-01	HIGH		READY
23798	23798	Pickup	H-1 I		2	EU-HYUNDAI-H1-I-CHASSIS-CAB-01	HIGH	单排底盘驾驶室外廓。	READY
23808_3dr	23808	SUV	Pajero III Classic	V68W	3	EU-MITSUBISHI-PAJERO-III-CLASSIC-V68W-SUV-3D-01	HIGH	V68W三门短车身。	READY
23808_5dr	23808	SUV	Pajero III Classic	V78W	5	EU-MITSUBISHI-PAJERO-III-CLASSIC-V78W-SUV-5D-01	HIGH	V78W五门长车身。	READY
23812_swb_lowroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
23812_swb_highroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
23812_lwb_lowroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
23812_lwb_highroof	23812	Van	J5 I	290L		EU-PEUGEOT-J5-I-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
23816_3dr	23816	Hatchback	Cuore V	L701	3	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	MEDIUM	L701三门外廓。	READY
23816_5dr	23816	Hatchback	Cuore V	L701	5	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	MEDIUM	L701五门外廓；三维与三门一致。	READY
23818	23818	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH		READY
23825_prefl	23825	Hatchback	Saxo Phase I	SA13	3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	Phase I三门电动车外廓。	READY
23825_facelift	23825	Hatchback	Saxo Phase II	SA13	3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门电动车外廓。	READY
23826_van	23826	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	原始组合车身拆分为厢式车外廓。	READY
23826_mpv	23826	MPV	Berlingo I	M59	5	EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	原始组合车身拆分为乘用MPV外廓。	READY
23829	23829	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	HIGH	改款两厢车外廓。	READY
23831	23831	MPV	Ducato II	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	HIGH	中轴标准顶Panorama外廓。	READY
23834	23834	Coupe	Esprit S3	Type 85	2	EU-LOTUS-ESPRIT-S3-COUPE-2D-01	HIGH		READY
23844_pickup_singlecab	23844	Pickup	LT I Syncro	Typ 21	2	EU-VW-LT-I-4X4-PICKUP-MWB-SINGLECAB-01	MEDIUM	LT35 Syncro中轴单排货台外廓。	READY
23844_pickup_doublecab	23844	Pickup	LT I Syncro	Typ 21	4	EU-VW-LT-I-4X4-PICKUP-MWB-DOUBLECAB-01	MEDIUM	LT35 Syncro中轴双排货台外廓。	READY
23844_chassis_singlecab	23844	Pickup	LT I Syncro	Typ 21	2	EU-VW-LT-I-4X4-CHASSIS-CAB-MWB-01	MEDIUM	LT35 Syncro中轴单排底盘驾驶室外廓。	READY
23844_chassis_doublecab	23844	Pickup	LT I Syncro	Typ 21	4	EU-VW-LT-I-4X4-CHASSIS-DOUBLECAB-MWB-01	MEDIUM	LT35 Syncro中轴双排底盘驾驶室外廓。	READY
23846_pickup_singlecab	23846	Pickup	LT I 4x4	Typ 21	2	EU-VW-LT-I-4X4-PICKUP-MWB-SINGLECAB-01	MEDIUM	中轴单排货台外廓。	READY
23846_pickup_doublecab	23846	Pickup	LT I 4x4	Typ 21	4	EU-VW-LT-I-4X4-PICKUP-MWB-DOUBLECAB-01	HIGH	中轴双排货台外廓。	READY
23846_chassis_singlecab	23846	Pickup	LT I 4x4	Typ 21	2	EU-VW-LT-I-4X4-CHASSIS-CAB-MWB-01	MEDIUM	中轴单排底盘驾驶室外廓。	READY
23846_chassis_doublecab	23846	Pickup	LT I 4x4	Typ 21	4	EU-VW-LT-I-4X4-CHASSIS-DOUBLECAB-MWB-01	MEDIUM	中轴双排底盘驾驶室外廓。	READY
23848_swb_lowroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱短轴低顶外廓。	READY
23848_swb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱短轴中顶外廓。	READY
23848_mwb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱中轴中顶外廓。	READY
23848_mwb_highroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱中轴高顶外廓。	READY
23848_lwb_medroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱长轴中顶外廓。	READY
23848_lwb_highroof	23848	Van	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱长轴高顶外廓。	READY
23849	23849	Wagon	Insignia A facelift 2013		5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH		READY
23856_mwb_highroof	23856	MPV	LT II			EU-VW-LT-II-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶Bus外廓。	READY
23856_lwb_highroof	23856	MPV	LT II			EU-VW-LT-II-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
23857_working_shortcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-WORKING-SHORTCAB-01	HIGH	Working短驾驶室外廓。	READY
23857_working_crewcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-WORKING-CREWCAB-01	HIGH	Working双排驾驶室外廓。	READY
23857_trekking_shortcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-TREKKING-SHORTCAB-01	HIGH	Trekking短驾驶室外廓。	READY
23857_trekking_longcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-TREKKING-LONGCAB-01	HIGH	Trekking加长驾驶室外廓。	READY
23857_adventure_longcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-ADVENTURE-LONGCAB-01	HIGH	Adventure加长驾驶室宽体外廓。	READY
23857_adventure_crewcab	23857	Pickup	Strada 278	278		EU-FIAT-STRADA-278-PICKUP-ADVENTURE-CREWCAB-01	HIGH	Adventure双排驾驶室宽体外廓。	READY
23859_prefl	23859	SUV	Cherokee XJ pre-facelift	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	MEDIUM	改款前五门外廓。	READY
23859_facelift	23859	SUV	Cherokee XJ facelift	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	MEDIUM	改款后五门外廓。	READY
23861_voyager	23861	MPV	Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	MEDIUM	标准轴距Voyager外廓。	READY
23861_grand	23861	MPV	Grand Voyager III		4	EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	MEDIUM	长轴Grand Voyager外廓。	READY
23864	23864	Wagon	Century IV		5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	改款旅行车外廓。	READY
23865	23865	Hatchback	New Beetle I	9C1	3	EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	HIGH		READY
23866	23866	Convertible	New Beetle I	1Y7	2	EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
24063	24063	Hatchback	Mini Mk II–IV	ADO15	2	EU-MORRIS-MINI-ADO15-HATCHBACK-2D-01	MEDIUM	生产期内外部三维一致。	READY
24066	24066	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	HIGH	改款轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1801-1900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844	Auto-Data Renault Kangoo II Express	https://www.auto-data.net/en/renault-kangoo-ii-express-generation-7589
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data Renault Kangoo II 1.6 16V	https://www.auto-data.net/en/renault-kangoo-ii-1.6-16v-106hp-33902
EU-DAIHATSU-CUORE-VII-L276-HATCHBACK-5D-01	3470	1475	1530	Automobile-Catalog Daihatsu Cuore Top	https://www.automobile-catalog.com/car/2007/581105/daihatsu_cuore_top.html
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure February 2007	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure February 2007	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960	Vauxhall Vivaro official brochure May 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-MOVANO-A-VAN-L1H1-01	4899	1990	2253	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-VAN-L1H2-01	4899	1990	2496	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-VAN-L2H2-01	5399	1990	2493	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-VAN-L3H2-01	5899	1990	2490	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-VAN-L3H3-01	5899	1990	2720	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-BUS-L1H1-01	4899	1990	2253	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-BUS-L2H2-01	5399	1990	2493	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-BUS-L3H3-01	5899	1990	2720	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	5369	1990	2200	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	5869	1990	2195	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	5869	1990	2203	Transit Center Opel Movano A technical specifications	https://www.transitcenter.uk/opel-movano-a-data-specification.php
EU-RENAULT-RAPID-I-BODY-01	4056	1566	1776	Auto.ru Renault Rapid 1.4 specifications	https://auto.ru/catalog/cars/renault/rapid/25004691/25004702/specifications/
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360	Zoomcar Jaguar XJ40 technical specifications	https://zoomcar.fr/fiche-technique/jaguar/xj40-modell-94-xj6-3-6-a-NAT65599.html
EU-SAAB-900-I-SEDAN-4D-01	4680	1690	1422	Drive.Place Saab 900 I Sedan 2.0	https://saab.drive.place/900/i/group_sedan/424878
EU-CITROEN-XM-Y3-WAGON-5D-01	4963	1794	1464	Automobile-Catalog 1993 Citroen XM Break V6	https://www.automobile-catalog.com/car/1993/541625/citroen_xm_break_v6.html
EU-PEUGEOT-306-I-CONVERTIBLE-FACELIFT-01	4179	1680	1356	Auto-Data Peugeot 306 Cabrio facelift 1997 1.8i	https://www.auto-data.net/en/peugeot-306-cabrio-facelift-1997-1.8i-101hp-automatic-5676
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430	AutoEvolution Mazda 323 BF Station Wagon;Auto-Data Mazda 323 III Station Wagon BF 1.6	https://www.autoevolution.com/cars/mazda-323-mk2-station-wagon-1989.html;https://www.auto-data.net/en/mazda-323-iii-station-wagon-bf-1.6-86hp-11192
EU-OPEL-OMEGA-A-WAGON-5D-01	4730	1772	1481	Automobile-Catalog Opel Omega Caravan GL 2.0i;EngineInDetail Opel Omega Caravan 2.0i Club	https://www.automobile-catalog.com/car/1987/57560/opel_omega_caravan_2_0i_gl.html;https://www.engineindetail.com/pa/opel-omega-caravan-2-0i-club-1991
EU-ISUZU-TROOPER-I-UBS17-SUV-3D-01	4122	1651	1844	Drive.Place Isuzu Trooper I 2.6 3-door	https://isuzu.drive.place/trooper/i/group_offroad_3d/396678
EU-ISUZU-TROOPER-I-UBS17-SUV-5D-01	4470	1651	1821	Drive.Place Isuzu Trooper I 2.6 5-door	https://isuzu.drive.place/trooper/i/group_offroad_5d/396491
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360	Automobile-Catalog 1988 Maserati 420 Si	https://www.automobile-catalog.com/car/1988/1445585/maserati_420_si.html
EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	4733	1950	1740	Auto-Data Chrysler Voyager III 2.5 TD	https://www.auto-data.net/en/chrysler-voyager-iii-2.5-td-116hp-14835
EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	5070	1950	1740	Auto-Data Chrysler Grand Voyager III 2.5 TD	https://www.auto-data.net/en/chrysler-grand-voyager-iii-2.5-td-115hp-14772
EU-PONTIAC-TRANS-SPORT-I-MPV-3D-01	4946	1886	1670	Auto Motor und Sport Pontiac Trans Sport technical data	https://www.auto-motor-und-sport.de/marken-modelle/pontiac/trans-sport/technische-daten/
EU-FORD-TAURUS-III-SEDAN-4D-01	5016	1854	1400	Auto-Data Ford Taurus III 3.0 V6	https://www.auto-data.net/en/ford-taurus-iii-3.0-v6-145hp-automatic-7924
EU-FORD-TAURUS-III-WAGON-5D-01	5070	1854	1463	Edmunds 1999 Ford Taurus Wagon SE	https://www.edmunds.com/ford/taurus/1999/wagon/st-12295/features-specs/
EU-CHEVROLET-BLAZER-S10-II-SUV-2D-01	4437	1689	1699	Automobile-Catalog 1995 Chevrolet Blazer 2-door 4WD	https://www.automobile-catalog.com/car/1995/482885/chevrolet_blazer_2-door_4wd_automatic.html
EU-CHEVROLET-BLAZER-S10-II-SUV-4D-01	4602	1689	1702	Automobile-Catalog 1995 Chevrolet Blazer LT 4-door AWD	https://www.automobile-catalog.com/car/1995/482930/chevrolet_blazer_lt_4-door_awd_automatic.html
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4803	1715	1351	Edmunds 1994 Buick Skylark Sedan specifications	https://www.edmunds.com/buick/skylark/1994/sedan/features-specs/
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351	Edmunds 1991 Cadillac Seville Sedan specifications	https://www.edmunds.com/cadillac/seville/1991/sedan/st-10559/features-specs/
EU-CHEVROLET-BERETTA-L-COUPE-2D-01	4757	1735	1346	Automobile-Catalog 1994 Chevrolet Beretta Z26 2.3L Quad-4	https://www.automobile-catalog.com/car/1994/470645/chevrolet_beretta_z26_2_3l_quad-4.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201	Corvette Action Center 1996 Corvette overview	https://www.corvetteactioncenter.com/specs/c4/1996/96overview.html
EU-FORD-EXPLORER-II-U2-SUV-5D-01	4790	1790	1800	Auto-Data Ford Explorer II 4.0 XLT	https://www.auto-data.net/en/ford-explorer-ii-4.0-xlt-162hp-7871
EU-FIAT-DOBLO-II-263-BODY-SWB-LOWROOF-01	4406	1832	1845	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-LWB-LOWROOF-01	4756	1832	1880	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-SWB-HIGHROOF-01	4406	1832	2125	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-BODY-LWB-HIGHROOF-01	4756	1832	2125	Fiat Professional New Doblò Cargo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-PALIO-I-178-HATCHBACK-01	3827	1634	1446	Automobile-Catalog 2005 Fiat Palio ELX 1.4	https://www.automobile-catalog.com/car/2005/734810/fiat_palio_elx_1_4.html
EU-CITROEN-JUMPER-I-230L-VAN-4X4-L1H1-01	4655	1998	2150	Motoro Citroën Jumper 2.0i 4x4 technical specifications	https://motoro.ch/en/fiche-technique/citroen/jumper-2-0i-4x4
EU-CITROEN-JUMPER-I-230L-VAN-4X4-L2H2-01	5005	1998	2470	Motoro Citroën Jumper 2.0i 4x4 technical specifications	https://motoro.ch/en/fiche-technique/citroen/jumper-2-0i-4x4
EU-OPEL-ASTRA-G-F08-HATCHBACK-3D-01	4110	1709	1425	Auto-Data Opel Astra G 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.4-ecotec-16v-90hp-2432
EU-OPEL-ASTRA-G-F48-HATCHBACK-5D-01	4110	1709	1425	Auto-Data Opel Astra G 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.4-ecotec-16v-90hp-2432
EU-OPEL-ASTRA-G-F35-WAGON-5D-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-caravan-1.4-ecotec-16v-90hp-2415
EU-DAEWOO-NUBIRA-J100-HATCHBACK-5D-01	4280	1699	1430	AutoEvolution Daewoo Nubira Hatchback 1.6	https://www.autoevolution.com/cars/daewoo-nubira-hatchback-2000.html
EU-KIA-CEED-II-HATCHBACK-5D-01	4310	1780	1470	Auto-Data Kia Cee'd model specifications;Auto-Data Kia Cee'd II facelift 1.4 CVVT	https://www.auto-data.net/en/kia-ceed-model-1935;https://www.auto-data.net/en/kia-ceed-ii-facelift-2015-1.4-cvvt-100hp-41346
EU-CHRYSLER-VOYAGER-I-MPV-5D-01	4503	1833	1637	Automobile-Catalog 1989 Chrysler Voyager LE 3.0 V6	https://www.automobile-catalog.com/car/1989/516575/chrysler_voyager_le_3_0_v6_automatic.html
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-01	4074	1678	1432	Automobile-Catalog 1998 Daewoo Lanos 1.5 SX Hatchback	https://www.automobile-catalog.com/car/1998/555770/daewoo_lanos_1_5_sx_hatchback.html
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108	Zoomcar Citroën C25 Chassis Cab 1400 D Court;Zoomcar Citroën C25 Chassis Cab 1400 D Moyen	https://zoomcar.fr/fiche-technique-utilitaire/citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-court-NAT56141.html;https://zoomcar.fr/fiche-technique-utilitaire/top-citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-moyen-NAT56140.html
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108	Zoomcar Citroën C25 Chassis Cab 1400 D Long	https://zoomcar.fr/fiche-technique-utilitaire/top-citroen/c25-chassis-cabine-c25-chassis-cab-1400-d-long-NAT56144.html
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080	Zoomcar Citroën C25 Chassis Cab 1800 D Long	https://zoomcar.fr/fiche-technique/citroen/c25-chassis-cabine-c25-chassis-cab-1800-d-long-NAT56155.html
EU-OPEL-ASTRA-G-F69-SEDAN-4D-01	4252	1709	1425	Auto-Data Opel Astra G Classic 1.4 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-classic-1.4-ecotec-16v-90hp-2393
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data Seat Leon III ST facelift 2.0 TDI	https://www.auto-data.net/en/seat-leon-iii-st-facelift-2016-2.0-tdi-184hp-26978
EU-MORGAN-PLUS-8-SERIES-1-CONVERTIBLE-01	3730	1580	1320	CarsGuide 1995 Morgan Plus dimensions	https://www.carsguide.com.au/morgan/plus/car-dimensions/1995
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420	Auto-Data Fiat Panda 1100 ie;Automobile-Catalog Fiat Panda 1.1 i.e. Selecta	https://www.auto-data.net/en/fiat-panda-zaf-141-facelift-1991-1100-ie-55hp-6915;https://www.automobile-catalog.com/car/1997/715460/fiat_panda_1_1i_e__selecta.html
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485	Automobile-Catalog 2001 Fiat Panda 1.1 i.e. 4x4	https://www.automobile-catalog.com/car/2001/715445/fiat_panda_1_1i_e__4x4.html
EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-01	4495	1720	1425	Auto-Data Hyundai Elantra III 1.6 Sedan	https://www.auto-data.net/en/hyundai-elantra-iii-1.6-107hp-automatic-29321
EU-PEUGEOT-307-I-FACELIFT-WAGON-01	4432	1757	1544	Auto-Data Peugeot 307 Station Wagon facelift generation	https://www.auto-data.net/en/peugeot-307-station-wagon-facelift-2005-generation-4268
EU-ISUZU-TROOPER-II-UB-SUV-3D-01	4145	1650	1815	Automobile-Catalog 1991 Isuzu Trooper 2.6i 3-door	https://www.automobile-catalog.com/car/1991/1260155/isuzu_trooper_2_6i_cat.html
EU-ISUZU-TROOPER-II-UB-SUV-5D-01	4495	1650	1815	Automobile-Catalog 1991 Isuzu Trooper Long 5-door 2.6i	https://www.automobile-catalog.com/car/1991/1260215/isuzu_trooper_long_5-door_2_6i_cat.html
EU-ISUZU-TROOPER-II-UB-SUV-SOFTTOP-01	4145	1650	1830	Automobile-Catalog 1991 Isuzu Trooper Canvas Top 2.6i	https://www.automobile-catalog.com/car/1991/1260185/isuzu_trooper_canvas-top_2_6i_cat.html
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459	Auto-Data Audi A6 4F C6 2.4i V6	https://www.auto-data.net/en/audi-a6-4f-c6-2.4i-v6-24v-177hp-4641
EU-NISSAN-350Z-Z33-ROADSTER-FACELIFT-01	4315	1815	1330	Auto-Data Nissan 350Z Roadster Z33 facelift 313 HP	https://www.auto-data.net/en/nissan-350z-roadster-z33-facelift-2007-3.5i-v6-24v-313hp-25040
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data Audi A4 B7 3.0 TDI quattro	https://www.auto-data.net/en/audi-a4-b7-8e-3.0-tdi-v6-204hp-quattro-4376
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453	Automobile-Catalog 2004 Audi A4 Avant 3.0 TDI Quattro	https://www.automobile-catalog.com/car/2004/248375/audi_a4_avant_3_0_tdi_quattro.html
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440	Automobile-Catalog 2004 Daewoo Evanda V200 2.0 CDX	https://www.automobile-catalog.com/car/2004/557675/daewoo_evanda_2_0_cdx_automatic.html
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740	Auto-Data SsangYong Actyon 2.3	https://www.auto-data.net/en/ssangyong-actyon-2.3-150hp-15988
EU-MITSUBISHI-ECLIPSE-III-D53A-CONVERTIBLE-01	4455	1750	1340	Auto-Data Mitsubishi Eclipse Spyder III GT 3.0	https://www.auto-data.net/en/mitsubishi-eclipse-spyder-iii-3g-gt-3.0-i-v6-24v-200hp-15621
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415	Automobile-Catalog 1995 Chevrolet Caprice Classic Sedan 5.7	https://www.automobile-catalog.com/car/1995/472115/chevrolet_caprice_classic_sedan_5_7l_v-8.html
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364	Automobile-Catalog 1984 Buick Century Limited Sedan	https://www.automobile-catalog.com/car/1984/314270/buick_century_limited_sedan_3_0l_v-6.html
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364	Automobile-Catalog 1987 Buick Century Limited Sedan	https://www.automobile-catalog.com/car/1987/315605/buick_century_limited_sedan_3_8l_v-6.html
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377	Automobile-Catalog 1984 Buick Century Custom Wagon	https://www.automobile-catalog.com/car/1984/314540/buick_century_custom_wagon_2_5l.html
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377	Automobile-Catalog 1989 Buick Century Custom Wagon	https://www.automobile-catalog.com/car/1989/320150/buick_century_custom_wagon_3_3l_v-6.html
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Volkswagen Newsroom Golf V Variant profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-variant-profile-19526
EU-CHRYSLER-VOYAGER-IV-RG-MPV-5D-01	4805	1995	1750	Auto-Data Chrysler Voyager IV 2.5 CRD TD	https://www.auto-data.net/en/chrysler-voyager-iv-2.5-crd-td-143hp-14827
EU-JEEP-GRAND-CHEROKEE-II-WJ-FACELIFT-SUV-01	4611	1858	1805	Auto-Data Jeep Grand Cherokee II WJ facelift 2.7 CRD	https://www.auto-data.net/en/jeep-grand-cherokee-ii-wj-facelift-2003-2.7-crd-163hp-4x4-automatic-1159
EU-HYUNDAI-H1-I-CHASSIS-CAB-01	4695	1820	1880	Autodata1 Hyundai H-1 I Starex 2.5 CRDI Chassis	https://www.autodata1.com/en/car/hyundai/h-1/h-1-i-starex-25-crdi-140-hp
EU-MITSUBISHI-PAJERO-III-CLASSIC-V68W-SUV-3D-01	4295	1885	1845	Automobile-Catalog 2006 Mitsubishi Pajero 3.2 DI-D Classic 3-door	https://www.automobile-catalog.com/car/2006/2015180/mitsubishi_pajero_3_2_di-d_classic_3door.html
EU-MITSUBISHI-PAJERO-III-CLASSIC-V78W-SUV-5D-01	4810	1885	1855	Automobile-Catalog 2006 Mitsubishi Pajero 3.2 DI-D Classic 5-door	https://www.automobile-catalog.com/car/2006/2015285/mitsubishi_pajero_3_2_di-d_classic_5door.html
EU-PEUGEOT-J5-I-VAN-SWB-LOWROOF-01	4759	1965	2108	Peugeot Range Commercials official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf
EU-PEUGEOT-J5-I-VAN-SWB-HIGHROOF-01	4759	1965	2420	Peugeot Range Commercials official brochure;WheelsAge Peugeot J5 Van 1300 High Roof	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf;https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof/specifications
EU-PEUGEOT-J5-I-VAN-LWB-LOWROOF-01	5489	1965	2108	Peugeot Range Commercials official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf
EU-PEUGEOT-J5-I-VAN-LWB-HIGHROOF-01	5489	1965	2420	Peugeot Range Commercials official brochure;WheelsAge Peugeot J5 Van 1300 High Roof Long	https://autocatalogarchive.com/wp-content/uploads/2023/03/Peugeot-Range-Commercials-1988-NL.pdf;https://en.wheelsage.org/peugeot/j5/280/van_1300_high_roof_long/specifications
EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	3410	1475	1420	Auto-Data Daihatsu Cuore;Automobile-Catalog 2000 Daihatsu Cuore GLX	https://www.auto-data.net/en/daihatsu-cuore-model-15;https://www.automobile-catalog.com/car/2000/574895/daihatsu_cuore_glx.html
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740	Auto-Data Daihatsu Terios model specifications	https://www.auto-data.net/en/daihatsu-terios-model-13
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	3718	1595	1390	Auto-Data Citroen Saxo Phase I 3-door Electric	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-12-kwh-27hp-46431
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360	CarsArt Citroen Saxo Phase II 3-door 1.5 D	https://www.carsart.net/en/cars/citroen/saxo/phase-ii-1999-3-door/1500cc-d-57hp/
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819	Parkers Citroen Berlingo Van M59 dimensions	https://www.parkers.co.uk/vans-pickups/citroen/berlingo/1996-dimensions/
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810	Auto-Data Citroen Berlingo I M59	https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	3860	1667	1510	Auto-Data Citroen C3 I facelift model specifications	https://www.auto-data.net/en/citroen-c3-model-1690
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato 244 owner handbook	https://www.carmanualsonline.info/fiat-ducato-244-2005-3-g-owners-manual
EU-LOTUS-ESPRIT-S3-COUPE-2D-01	4191	1854	1118	Automobile-Catalog 1982 Lotus Esprit S3	https://www.automobile-catalog.com/car/1982/1434635/lotus_esprit_s3.html
EU-VW-LT-I-4X4-PICKUP-MWB-SINGLECAB-01	5630	2140	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-4X4-PICKUP-MWB-DOUBLECAB-01	5330	2140	2310	Volkswagen AG LT 4x4 action information	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf
EU-VW-LT-I-4X4-CHASSIS-CAB-MWB-01	5245	2050	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-4X4-CHASSIS-DOUBLECAB-MWB-01	5245	2050	2310	Volkswagen AG LT 4x4 action information;Volkswagen LT Technical Data and Equipment	https://vwlt.co.uk/wp-content/uploads/1987-12%20Der%20VW%20LT%204x4.pdf;https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	4834	1974	1974	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	4834	1974	2313	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	5201	1974	2309	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	5201	1974	2529	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	5651	1974	2303	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	5651	1974	2524	Ford Transit 2002.75 official specifications brochure	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513	Automobile-Catalog Opel Insignia Sports Tourer 2.0 CDTI 163 4x4	https://www.automobile-catalog.com/car/2013/2537810/opel_insignia_sports_tourer_2_0_cdti_ecoflex_163_4x4.html
EU-VW-LT-II-BUS-MWB-HIGHROOF-01	5585	1933	2570	Drom Volkswagen LT II dimensions;VehicleScore Volkswagen LT dimensions	https://www.drom.ru/catalog/lcv/volkswagen/lt/specs/dimensions/;https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
EU-VW-LT-II-BUS-LWB-HIGHROOF-01	6535	1933	2570	Drom Volkswagen LT II dimensions;VehicleScore Volkswagen LT dimensions	https://www.drom.ru/catalog/lcv/volkswagen/lt/specs/dimensions/;https://vehiclescore.co.uk/car-dimensions-check/volkswagen/lt
EU-FIAT-STRADA-278-PICKUP-WORKING-SHORTCAB-01	4409	1664	1525	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-WORKING-CREWCAB-01	4409	1664	1580	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-TREKKING-SHORTCAB-01	4409	1664	1564	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-TREKKING-LONGCAB-01	4409	1664	1588	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-ADVENTURE-LONGCAB-01	4457	1740	1648	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-FIAT-STRADA-278-PICKUP-ADVENTURE-CREWCAB-01	4457	1740	1631	Fiat Professional New Strada official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT_PROF/SCHEDE_TECNICHE/120127_FP_NuovoStrada_ST_ENG.pdf
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700	Automobile-Catalog 1996 Jeep Cherokee 2.5 TD Limited	https://www.automobile-catalog.com/car/1996/1314380/jeep_cherokee_2_5_td_limited.html
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625	Automobile-Catalog 1997 Jeep Cherokee 2.5 TD Limited	https://www.automobile-catalog.com/car/1997/1319420/jeep_cherokee_2_5_td_limited.html
EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Auto-Data Volkswagen New Beetle 9C facelift 1.4	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-1.4-75hp-28063
EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	4129	1721	1502	Auto-Data Volkswagen New Beetle Convertible facelift 1.6	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-facelift-2005-1.6-102hp-28091
EU-MORRIS-MINI-ADO15-HATCHBACK-2D-01	3054	1410	1346	Automobile-Catalog 1967 Morris Mini-Cooper Mk II	https://www.automobile-catalog.com/car/1967/2034095/morris_mini-cooper_mk_ii.html
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437	AutoCentrum Renault Thalia I technical data	https://www.autocentrum.pl/dane-techniczne/renault/thalia/i/silnik-benzynowy-1.4-75km-2001-2008/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1801-1900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.lu/autoteile/lenkungsfilter-10691/vw/lt/lt-28-35-i-pritsche-fahrgestell-281-363/23844-2-4-td-syncro "https://www.autodoc.lu/autoteile/lenkungsfilter-10691/vw/lt/lt-28-35-i-pritsche-fahrgestell-281-363/23844-2-4-td-syncro"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1801-1900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1801-1900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2807 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1462 行）

