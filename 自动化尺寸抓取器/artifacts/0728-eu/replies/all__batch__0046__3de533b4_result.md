# 任务：all 第 4501-4600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0046__3de533b4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4501-4600 行

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
all 第 4501-4600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-100-C1-COUPE-01	4398	1750	1340
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421
EU-AUDI-100-C2-AVANT-01	4587	1768	1390
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390
EU-AUDI-100-C2-WAGON-FACELIFT-01	4590	1768	1390
EU-AUDI-100-C2-WAGON-PREFL-01	4587	1768	1390
EU-AUDI-100-C3-AVANT-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-02	4793	1814	1421
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422
EU-AUDI-100-C3-WAGON-QUATTRO-01	4793	1814	1422
EU-AUDI-100-C4-SEDAN-FWD-01	4790	1777	1431
EU-AUDI-100-C4-SEDAN-QUATTRO-01	4790	1777	1437
EU-AUDI-100-C4-WAGON-FWD-01	4790	1777	1440
EU-AUDI-100-C4-WAGON-QUATTRO-01	4790	1777	1448
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-20-01	4383	1682	1376
EU-AUDI-80-B2-SEDAN-QUATTRO-22-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	4406	1682	1350
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406
EU-AUDI-80-B4-WAGON-01	4482	1695	1408
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-FORD-USA-EXPLORER-I-UN46-SUV-3D-01	4430	1783	1715
EU-FORD-USA-EXPLORER-I-UN46-SUV-5D-01	4681	1783	1709
EU-HONDA-PRELUDE-I-COUPE-2D-01	4090	1635	1290
EU-HONDA-PRELUDE-II-COUPE-2D-01	4295	1690	1295
EU-HONDA-PRELUDE-II-COUPE-2D-FACELIFT-01	4375	1690	1295
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295
EU-HONDA-PRELUDE-IV-COUPE-2D-01	4440	1765	1290
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449
EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	4590	1752	1433
EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	4590	1758	1435
EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	4590	1755	1440
EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	4605	1752	1435
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	4783	1928	1789
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400
EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	4239	1688	1400
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-GSI-3D-01	4086	1688	1410
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410
EU-OPEL-ASTRA-F-WAGON-5D-01	4278	1688	1475
EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	4192	1780	1721
EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	4692	1764	1753
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410
EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	4545	1695	1425
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c4	2.5 TDI	Stufenheck	Frontantrieb	Diesel	85	116	Jun 1994	Oct 1997	2024-03-01	4641
Audi	A6 c4 avant	2	Kombi	Frontantrieb	Benzin	74	100	Jun 1994	Dec 1997	2024-03-01	4643
Audi	A6 c4 avant	2	Kombi	Frontantrieb	Benzin	85	115	Jun 1994	Dec 1997	2024-03-01	4644
Audi	A6 c4 avant	2.0 16V	Kombi	Frontantrieb	Benzin	103	140	Jun 1994	Dec 1997	2024-03-01	4645
Audi	A6 c4 avant	2.6	Kombi	Frontantrieb	Benzin	110	150	Jun 1994	Dec 1997	2024-03-01	4646
Audi	A6 c4 avant	2.8	Kombi	Frontantrieb	Benzin	128	174	Jun 1994	Dec 1997	2024-03-01	4647
Audi	A6 c4 avant	2.5 TDI	Kombi	Frontantrieb	Diesel	85	116	Jun 1994	Dec 1997	2024-03-01	4649
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	85	115	Sep 1993	Nov 1998	2024-03-01	4650
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	75	102	Jul 1988	Jun 1991	2024-03-01	4651
Opel	Astra f	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	100	136	Feb 1995	Sep 1998	2024-03-01	4652
Opel	Astra f caravan	2.0 I 16V	Kombi	Frontantrieb	Benzin	100	136	Feb 1995	Jan 1998	2024-03-01	4653
Opel	Astra f cc	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	100	136	Feb 1995	Jan 1998	2024-03-01	4654
Audi	A6 c4	2.0 16V Quattro	Stufenheck	Allrad	Benzin	103	140	Jun 1994	Oct 1997	2024-03-01	4655
Audi	A6 c4	2.6 Quattro	Stufenheck	Allrad	Benzin	110	150	Jun 1994	Oct 1997	2024-03-01	4656
Audi	A6 c4	2.8 Quattro	Stufenheck	Allrad	Benzin	128	174	Jun 1994	Oct 1997	2024-03-01	4657
Audi	A6 c4	S6 Turbo Quattro	Stufenheck	Allrad	Benzin	169	230	Jun 1994	Oct 1997	2024-03-01	4658
Audi	A6 c4	S6 4.2 Quattro	Stufenheck	Allrad	Benzin	213	290	Jun 1994	Oct 1997	2024-03-01	4659
Audi	A6 c4 avant	2.0 16V Quattro	Kombi	Allrad	Benzin	103	140	Jun 1994	Dec 1997	2024-03-01	4660
Audi	A6 c4 avant	S6 4.2 Quattro	Kombi	Allrad	Benzin	213	290	Jun 1994	Dec 1997	2024-03-01	4661
Audi	A6 c4 avant	2.8 Quattro	Kombi	Allrad	Benzin	128	174	Jun 1994	Dec 1997	2024-03-01	4662
Audi	A6 c4 avant	S6 Turbo Quattro	Kombi	Allrad	Benzin	169	230	Jun 1994	Dec 1997	2024-03-01	4663
Jeep	Grand cherokee iv	3.6 V6 4X4	SUV	Allrad	Benzin	210	286	Nov 2010	-	2024-03-01	4664
Audi	80	RS2 Quattro	Kombi	Allrad	Benzin	232	315	Mar 1994	May 1995	2024-03-01	4665
Audi	80	2.0 E	Stufenheck	Frontantrieb	Benzin	82	112	Aug 1988	Oct 1990	2024-03-01	4666
Audi	80	2.3 E Quattro	Kombi	Allrad	Benzin	98	133	Sep 1991	Nov 1994	2024-03-01	4667
Audi	80	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Jul 1992	Jan 1996	2024-03-01	4668
Audi	100	S4 V8 Quattro	Kombi	Allrad	Benzin	206	280	Oct 1992	Jul 1994	2024-03-01	4669
Audi	100	S4 V8 Quattro	Stufenheck	Allrad	Benzin	206	280	Oct 1992	Jul 1994	2024-03-01	4670
Audi	80	1.6 E	Kombi	Frontantrieb	Benzin	74	101	Jun 1993	Jan 1996	2024-03-01	4671
Porsche	911	3.6 Turbo 4	Coupe	Allrad	Benzin	300	408	Mar 1995	Sep 1997	2024-03-01	4672
Porsche	911	3.6 Turbo GT2	Coupe	Heckantrieb	Benzin	316	430	Mar 1995	Sep 1997	2024-03-01	4673
Porsche	911	3.8 Carrera	Coupe	Heckantrieb	Benzin	210	286	Jun 1995	Sep 1997	2024-03-01	4674
Porsche	911	3.8 Carrera 4	Coupe	Allrad	Benzin	210	286	Jun 1995	Sep 1997	2024-03-01	4675
Jeep	Grand cherokee iv	5.7 V8 4X4	SUV	Allrad	Benzin	259	352	Nov 2010	-	2024-03-01	4676
Porsche	911	3.8 Carrera 4	Cabriolet	Allrad	Benzin	210	286	Jun 1995	Sep 1997	2024-03-01	4677
Porsche	911	3.8 Carrera RS	Coupe	Heckantrieb	Benzin	221	300	Jun 1995	Sep 1997	2024-03-01	4678
VW	Polo	64 1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Oct 1994	Oct 1999	2024-03-01	4679
VW	Golf iii variant	1.9 TDI Syncro	Kombi	Allrad	Diesel	66	90	Jul 1995	Apr 1999	2024-03-01	4681
VW	Sharan	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	66	90	Sep 1995	Mar 2010	2024-03-01	4682
VW	Sharan	2	Großraumlimousine	Frontantrieb	Benzin	85	115	Sep 1995	Mar 2010	2024-03-01	4683
VW	Sharan	2.8 VR6	Großraumlimousine	Frontantrieb	Benzin	128	174	Sep 1995	Apr 2000	2024-03-01	4684
Mercedes-benz	Sprinter 2-T	208 D	Bus	Heckantrieb	Diesel	58	79	Feb 1995	Apr 2000	2024-03-01	4685
Mercedes-benz	Sprinter 2-T	212 D	Bus	Heckantrieb	Diesel	90	122	Feb 1995	Apr 2000	2024-03-01	4686
Mercedes-benz	Sprinter 2-T	214	Bus	Heckantrieb	Benzin	105	143	Feb 1995	May 2006	2024-03-01	4687
Mercedes-benz	C-Klasse	C 180	Stufenheck	Heckantrieb	Benzin	89	121	Nov 1994	May 2000	2024-03-01	4688
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel	70	95	Jun 1995	Jul 1999	2024-03-01	4689
Mercedes-benz	E-Klasse	E 250 D	Stufenheck	Heckantrieb	Diesel	83	113	Jun 1995	Jul 1999	2024-03-01	4690
Mercedes-benz	E-Klasse	E 200	Stufenheck	Heckantrieb	Benzin	100	136	Jun 1995	Aug 2000	2024-03-01	4691
Mercedes-benz	E-Klasse	E 300 D	Stufenheck	Heckantrieb	Diesel	100	136	Jun 1995	Jun 1997	2024-03-01	4692
Mercedes-benz	E-Klasse	E 230	Stufenheck	Heckantrieb	Benzin	110	150	Jun 1995	Jun 1997	2024-03-01	4693
Mercedes-benz	E-Klasse	E 320	Stufenheck	Heckantrieb	Benzin	162	220	Jun 1995	Jun 1997	2024-03-01	4694
Mitsubishi	Eclipse i	2.0 I 16V	Coupe	Frontantrieb	Benzin	110	150	Apr 1991	Nov 1995	2024-03-01	4695
Ford	Scorpio ii	2.0 I	Stufenheck	Heckantrieb	Benzin	85	115	Oct 1994	Aug 1998	2024-03-01	4696
Ford	Scorpio ii	2.0 I 16V	Stufenheck	Heckantrieb	Benzin	100	136	Oct 1994	Aug 1998	2024-03-01	4697
Ford	Scorpio ii	2.9 I 24V	Stufenheck	Heckantrieb	Benzin	152	207	Oct 1994	Aug 1998	2024-03-01	4698
Ford	Scorpio ii	2.5 TD	Stufenheck	Heckantrieb	Diesel	85	115	Oct 1994	Aug 1998	2024-03-01	4699
Ford	Scorpio ii turnier	2.0 I	Kombi	Heckantrieb	Benzin	85	115	Oct 1994	Aug 1998	2024-03-01	4700
Ford	Scorpio ii turnier	2.0 I 16V	Kombi	Heckantrieb	Benzin	100	136	Oct 1994	Aug 1998	2024-03-01	4701
Ford	Scorpio ii turnier	2.9 I 24V	Kombi	Heckantrieb	Benzin	152	207	Oct 1994	Aug 1998	2024-03-01	4702
Ford	Scorpio ii turnier	2.5 TD	Kombi	Heckantrieb	Diesel	85	115	Oct 1994	Aug 1998	2024-03-01	4703
Ford	Scorpio ii	2.9 I	Stufenheck	Heckantrieb	Benzin	110	150	Feb 1995	Aug 1998	2024-03-01	4704
Ford	Scorpio ii turnier	2.9 I	Kombi	Heckantrieb	Benzin	110	150	Feb 1995	Aug 1998	2024-03-01	4705
Jeep	Grand cherokee iii	3.0 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	155	211	May 2006	Dec 2010	2024-03-01	4706
Lancia	Dedra	2.0 I.e. Turbo	Stufenheck	Frontantrieb	Benzin	119	162	Apr 1991	Jul 1999	2024-03-01	4707
Lancia	Thema	3000 V6	Stufenheck	Frontantrieb	Benzin	126	171	Aug 1992	Jul 1994	2024-03-01	4708
Lancia	A 112	1.0 Abarth	Schrägheck	Frontantrieb	Benzin	51	69	Mar 1978	Feb 1984	2024-03-01	4709
Honda	Prelude	2.2 I 16V Vtec	Coupe	Frontantrieb	Benzin	136	185	Feb 1993	Sep 1996	2026-01-01	4710
Ford	Mondeo i	2.0 I 16V 4X4	Stufenheck	Allrad	Benzin	97	132	Dec 1994	Aug 1996	2024-03-01	4711
Ford	Mondeo i turnier	2.0 I 16V 4X4	Kombi	Allrad	Benzin	97	132	Dec 1994	Aug 1996	2024-03-01	4712
Ford	Escort vi	1.6 16V 4X4	Schrägheck	Allrad	Benzin	66	90	Jan 1995	Oct 1998	2024-03-01	4713
Ford	Galaxy i	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	66	90	Mar 1995	May 2006	2024-03-01	4714
Ford	Galaxy i	2.0 I	Großraumlimousine	Frontantrieb	Benzin	85	116	Nov 1995	May 2006	2024-03-01	4715
Ford	Galaxy i	2.8 I V6	Großraumlimousine	Frontantrieb	Benzin	128	174	Nov 1995	Apr 2000	2024-03-01	4716
Ford	Transit	2	Kasten	Heckantrieb	Benzin	84	114	Jun 1994	Mar 2000	2024-03-01	4717
Land Rover	Range rover sport i	5.0 4X4	SUV	Allrad	Benzin	372	506	Apr 2009	Mar 2013	2024-03-01	4718
Ford USA	Probe ii	2.5 V6 24V	Coupe	Frontantrieb	Benzin	120	163	Dec 1994	Mar 1998	2024-03-01	4719
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	115	156	Mar 1995	Dec 2001	2024-03-01	4720
Rover	600	620 SDI	Stufenheck	Frontantrieb	Diesel	77	105	May 1994	Jun 1999	2024-03-01	4721
Porsche	911	3.8 Carrera	Cabriolet	Heckantrieb	Benzin	210	286	Jun 1995	Sep 1997	2024-03-01	4722
Rover	400	414 SI	Schrägheck	Frontantrieb	Benzin	76	103	May 1995	Mar 2000	2024-03-01	4723
Rover	400	416 SI	Schrägheck	Frontantrieb	Benzin	82	112	May 1995	Mar 2000	2024-03-01	4724
Rover	400	416 SI	Schrägheck	Frontantrieb	Benzin	83	113	Jun 1995	Mar 2000	2024-03-01	4725
Opel	Frontera	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	83	113	Mar 1995	Aug 1998	2024-11-01	4726
Opel	Frontera	2.8 TD	Geländewagen offen	Allrad	Diesel	83	113	Mar 1995	Aug 1996	2024-11-01	4727
Opel	Frontera	2.2 I	Geländewagen geschlossen	Allrad	Benzin	100	136	Mar 1995	Oct 1998	2024-11-01	4728
Toyota	Carina e vi	1.6	Stufenheck	Frontantrieb	Benzin	73	99	Jan 1995	Sep 1997	2024-03-01	4729
Toyota	Carina e vi	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	79	107	Jan 1995	Sep 1997	2024-03-01	4730
Toyota	Carina e vi	1.6	Schrägheck	Frontantrieb	Benzin	73	99	Dec 1993	Sep 1997	2024-03-01	4731
Toyota	Carina e vi	1.8	Schrägheck	Frontantrieb	Benzin	79	107	Jan 1995	Sep 1997	2024-03-01	4732
BMW	3	M3 3.0	Coupe	Heckantrieb	Benzin	217	295	Sep 1993	May 1995	2024-03-01	4733
Skoda	Felicia i	1.3	Schrägheck	Frontantrieb	Benzin	40	54	Oct 1994	Mar 1998	2024-03-01	4734
Skoda	Felicia i	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Oct 1994	Mar 1998	2024-03-01	4735
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	120	163	Sep 2011	Oct 2016	2024-03-01	4736
Volvo	850	2	Kombi	Frontantrieb	Benzin	93	126	Aug 1994	Dec 1996	2024-03-01	4737
Volvo	850	2	Stufenheck	Frontantrieb	Benzin	93	126	Aug 1994	Dec 1996	2024-03-01	4738
Volvo	940	2.3 TI	Kombi	Heckantrieb	Benzin	99	135	Jan 1995	Oct 1998	2024-03-01	4739
Volvo	940	2.3 TI	Stufenheck	Heckantrieb	Benzin	99	135	Jan 1995	Oct 1998	2024-03-01	4740
Opel	Vectra a	1.7 D	Stufenheck	Frontantrieb	Diesel	44	60	Jul 1992	Nov 1995	2024-03-01	4741
Opel	Vectra a	1.6 I	Stufenheck	Frontantrieb	Benzin	52	71	Sep 1993	Nov 1995	2024-03-01	4742
Opel	Astra f cc	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	92	125	Jun 1993	Aug 1994	2024-03-01	4743


--- Round 1 / 首次发送 ---
更新点

* 已按缓存优先完成 49 个输入 Ktype，共形成 52 条 READY 映射；其中 E30 316i、Lancia Dedra 和 BMW F10 因门数或改款边界拆成派生行。
* 已直接复用 27 个累计尺寸组，没有重复输出其尺寸和来源。
* 首次创建 8 个尺寸组：Audi C4 S6 轿车/Avant、Audi RS2 Avant、Audi 100 C4 S4 轿车/Avant，以及 Porsche 993 Turbo、GT2、Carrera RS。S6、S4、RS2 和三种 Porsche 993 高性能车身的三维均与普通车身存在明确差异。([汽车数据网][1])
* Audi A6 C4 普通 quattro 车型的车身三维与对应普通 A6 C4 轿车/Avant 缓存组一致，已直接建立关联。([汽车数据网][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：49
* READY 映射行：52
* PENDING／尚未闭合输入 Ktype：51
* 本轮映射引用尺寸组：35
* 本轮首次创建尺寸组：8
* 复用既有尺寸组：27
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4641	4641	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4643	4643	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4644	4644	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4645	4645	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4646	4646	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4647	4647	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4649	4649	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4650	4650	Sedan	3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH		READY
4651_2dr	4651	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	MEDIUM	输入未区分双门与四门，按E30 316i两种轿车外廓派生。	READY
4651_4dr	4651	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	MEDIUM	输入未区分双门与四门，按E30 316i两种轿车外廓派生。	READY
4652	4652	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
4653	4653	Wagon	Astra F facelift		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH		READY
4655	4655	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4656	4656	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4657	4657	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4658	4658	Sedan	S6 C4	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
4659	4659	Sedan	S6 C4	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
4660	4660	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4661	4661	Wagon	S6 C4	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
4662	4662	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4663	4663	Wagon	S6 C4	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
4665	4665	Wagon	RS2 Avant	8C	5	EU-AUDI-80-B4-RS2-AVANT-01	HIGH		READY
4666	4666	Sedan	80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
4667	4667	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4668	4668	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4669	4669	Wagon	100 S4 C4	4A	5	EU-AUDI-100-C4-S4-AVANT-WAGON-01	HIGH		READY
4670	4670	Sedan	100 S4 C4	4A	4	EU-AUDI-100-C4-S4-SEDAN-01	HIGH		READY
4671	4671	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4672	4672	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-TURBO-01	HIGH		READY
4673	4673	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-GT2-01	HIGH		READY
4678	4678	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	HIGH		READY
4681	4681	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
4707_prefl	4707	Sedan	Dedra I pre-facelift	835	4	EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	HIGH	同一Ktype跨改款前后外廓，拆分映射。	READY
4707_facelift	4707	Sedan	Dedra I facelift	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH	同一Ktype跨改款前后外廓，拆分映射。	READY
4710	4710	Coupe	Prelude IV	BB1	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH		READY
4711	4711	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
4712	4712	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
4718	4718	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	HIGH		READY
4721	4721	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4729	4729	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
4730	4730	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
4731	4731	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH		READY
4732	4732	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH		READY
4733	4733	Coupe	3 Series E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
4736_prefl	4736	Sedan	5 Series F10 pre-facelift	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	MEDIUM	生产区间跨F10改款，按改款前后外廓派生。	READY
4736_facelift	4736	Sedan	5 Series F10 facelift	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	MEDIUM	生产区间跨F10改款，按改款前后外廓派生。	READY
4737	4737	Wagon	850	855	5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
4738	4738	Sedan	850	854	4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
4739	4739	Wagon	940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
4740	4740	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
4741	4741	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
4742	4742	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430	Auto-Data Audi S6 (4A,C4)	https://www.auto-data.net/en/audi-s6-4a-c4-generation-1107
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440	Auto-Data Audi S6 Avant (4A,C4)	https://www.auto-data.net/en/audi-s6-avant-4a-c4-generation-1108
EU-AUDI-80-B4-RS2-AVANT-01	4510	1695	1386	Auto-Data Audi RS2 Avant	https://www.auto-data.net/en/audi-rs2-avant-generation-1092
EU-AUDI-100-C4-S4-AVANT-WAGON-01	4790	1805	1422	Auto-Data Audi S4 Avant (4A,C4) 4.2 V8 quattro	https://www.auto-data.net/en/audi-s4-avant-4a-c4-4.2-v8-280hp-quattro-4082
EU-AUDI-100-C4-S4-SEDAN-01	4790	1805	1420	Auto-Data Audi S4 (4A,C4) 4.2 V8 quattro	https://www.auto-data.net/en/audi-s4-4a-c4-4.2-v8-280hp-quattro-4265
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285	Auto-Data Porsche 911 (993) Turbo 3.6	https://www.auto-data.net/en/porsche-911-993-turbo-3.6-408hp-6611
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270	Auto-Data Porsche 911 (993) GT2 3.6	https://www.auto-data.net/en/porsche-911-993-gt2-3.6-430hp-6612
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270	Auto-Data Porsche 911 (993) Carrera RS 3.8	https://www.auto-data.net/en/porsche-911-993-carrera-rs-3.8-300hp-6614
```

下一步优先处理

1. 闭合 Jeep Grand Cherokee WK/WK2 的改款边界及普通悬架外廓。
2. 集中处理 VW Sharan／Ford Galaxy 共平台 MPV 的改款分支。
3. 拆分 Mercedes-Benz Sprinter 2-T Bus 与 Ford Transit Kasten 的轴距、车顶组合。
4. 闭合 Mercedes-Benz W202、W210 跨改款车型。
5. 处理 Porsche 993 3.8 Carrera／Carrera 4／Cabriolet 的窄体、宽体边界。
6. 再处理 Scorpio II、Explorer II、Frontera A、Rover 400、Felicia I 等剩余独立尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s6-4a-c4-generation-1107 "Audi S6 (4A,C4) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/audi-a6-4a-c4-2.8-v6-174hp-quattro-4761 "Audi A6 (4A,C4) 2.8 V6 (174 Hp) quattro | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 继续按缓存优先推进，本轮新增闭合 23 个输入 Ktype，全部直接关联既有尺寸组或新增 5 个尺寸组。
* 本轮完成了 Astra F CC 三/五门派生、VW Polo 6N、VW Sharan I、Ford Galaxy I、Mercedes-Benz W210 sedan、Rover 400 HH-R hatchback、Opel Frontera A、Skoda Felicia I。
* 仍待处理的阻塞点已收敛到少量“跨改款/跨轴距/高性能宽体/门数未明”的车型族。

当前批次进度

* READY 输入 Ktype：72 / 100
* PENDING 输入 Ktype：28 / 100
* READY 映射行：75
* 已引用尺寸组：45
* 本轮首次创建/修正尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4654_3dr	4654	Hatchback	Astra F CC		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4654_5dr	4654	Hatchback	Astra F CC		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4679	4679	Hatchback	Polo III (6N)	6N		EU-VW-POLO-III-6N-HATCHBACK-01	HIGH		READY
4682	4682	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4683	4683	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4684	4684	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4689	4689	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4690	4690	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4691	4691	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4692	4692	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4693	4693	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4694	4694	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4714	4714	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4715	4715	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4716	4716	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4723	4723	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4724	4724	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4725	4725	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4726	4726	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH		READY
4727	4727	SUV	Frontera A Sport		3	EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	HIGH		READY
4728	4728	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH		READY
4734	4734	Hatchback	Felicia I		5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH		READY
4735	4735	Hatchback	Felicia I		5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH		READY
4743_3dr	4743	Hatchback	Astra F CC		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4743_5dr	4743	Hatchback	Astra F CC		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SHARAN-I-MPV-01	4634	1810	1730	Auto-Data Volkswagen Sharan I	https://www.auto-data.net/en/volkswagen-sharan-i-generation-1901
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420	Auto-Data Mercedes-Benz E-Class (W210)	https://www.auto-data.net/en/mercedes-benz-e-class-w210-generation-1125
EU-FORD-GALAXY-I-MPV-01	4634	1810	1730	Auto-Data Ford Galaxy I	https://www.auto-data.net/en/ford-galaxy-i-generation-917
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390	Auto-Data Rover 400 Hatchback (HH-R)	https://www.auto-data.net/en/rover-400-hatchback-hh-r-generation-387
EU-SKODA-FELICIA-I-HATCHBACK-01	3883	1635	1415	Auto-Data Skoda Felicia I Hatchback	https://www.auto-data.net/en/skoda-felicia-i-generation-1368
```

下一步优先处理

1. 闭合 Porsche 993 3.8 Carrera / Carrera 4 / Cabriolet 的窄体、宽体与敞篷边界。
2. 处理 Jeep Grand Cherokee III / IV 两代 SUV。
3. 处理 Mercedes-Benz C-Klasse W202 与 Sprinter 2-T Bus。
4. 处理 Ford Scorpio II sedan / turnier、Ford Transit Kasten、Ford USA Explorer / Probe II。
5. 处理 Lancia Thema / A112、Mitsubishi Eclipse I 及剩余未闭合单车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增闭合 17 个输入 Ktype：Porsche 993 普通 Carrera 车身直接复用既有组；Mercedes-Benz W202 按改款前后拆分；Mitsubishi Eclipse I、Ford Scorpio II 轿车/旅行车和 Jeep Grand Cherokee III 首次建组。W202、Eclipse、Scorpio 与 Jeep 的三维及不含后视镜宽度已完成尺寸组级核对。([汽车数据网][1])
* Ford Scorpio II 的部分页面把 `1875 mm` 混入宽度字段；结合明确同时列出 `Width 1760 mm` 与 `Width including mirrors 1875 mm` 的规格页，本轮统一落盘不含后视镜宽度 `1760 mm`。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：89
* PENDING 输入 Ktype：11
* READY 映射行：93
* 当前批次引用尺寸组：53
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4674	4674	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4675	4675	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4677	4677	Convertible	911 993	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4688_prefl	4688	Sedan	C-Klasse W202 pre-facelift	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	同一Ktype生产区间跨越1997年改款，拆分改款前外廓。	READY
4688_facelift	4688	Sedan	C-Klasse W202 facelift	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	同一Ktype生产区间跨越1997年改款，拆分改款后外廓。	READY
4695	4695	Coupe	Eclipse I (1G)		2	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-01	HIGH		READY
4696	4696	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4697	4697	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4698	4698	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4699	4699	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4700	4700	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4701	4701	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4702	4702	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4703	4703	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4704	4704	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4705	4705	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4706	4706	SUV	Grand Cherokee III	WH	5	EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	HIGH		READY
4722	4722	Convertible	911 993	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414	Auto-Data Mercedes-Benz C-class W202 C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-180-122hp-12643
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427	Auto-Data Mercedes-Benz C-class W202 facelift C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-facelift-1997-c-180-122hp-5g-tronic-44185
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-01	4340	1690	1305	Auto-Data Mitsubishi Eclipse I 1G 2.0 i 16V	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-2.0-i-16v-150hp-15626
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1402	Auto-Data Ford Scorpio II 2.9i 24V	https://www.auto-data.net/en/ford-scorpio-ii-gfr-ggr-2.9i-24v-207hp-8144
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442	Auto-Data Ford Scorpio II Turnier 2.9i 24V	https://www.auto-data.net/en/ford-scorpio-ii-turnier-2.9i-24v-210hp-8151
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	4750	1870	1740	Auto-Data Jeep Grand Cherokee III 3.0 CRD 4x4;Automobile-Catalog 2010 Jeep Grand Cherokee 3.0 CRD Limited	https://www.auto-data.net/de/jeep-grand-cherokee-iii-wk-3.0-crd-218hp-4x4-automatic-1151;https://www.automobile-catalog.com/car/2010/1326815/jeep_grand_cherokee_3_0_crd_limited_quadra-drive_ii_dpf.html
```

## 下一步优先处理

1. Jeep Grand Cherokee IV：`4664`、`4676`，闭合 WK2 改款前、2013 改款和后期外廓。
2. Mercedes-Benz Sprinter 2-T Bus：`4685`–`4687`，拆分实际轴距和车顶组合。
3. Ford Transit Kasten：`4717`，闭合车长及车顶分支。
4. Lancia Thema、A112：`4708`、`4709`。
5. Ford Escort、Probe、Explorer：`4713`、`4719`、`4720`。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-180-122hp-12643 "Mercedes-Benz C-class (W202) C 180 (122 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/ford-scorpio-ii-gfr-ggr-2.0-i-115hp-8138 "1994 Ford Scorpio II (GFR,GGR) 2.0 i (115 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 本轮闭合 Jeep Grand Cherokee IV 两个 Ktype，并按 WK2 改款前后拆分；闭合 Ford USA Explorer II，并按 1995–1997、1998、1999–2001 三种外廓拆分。
* 其余 8 个 Ktype 尚需闭合明确物理分支，未创建猜测性尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：92
* PENDING 输入 Ktype：8
* READY 映射行：100
* 当前批次引用尺寸组：58
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4664_prefl	4664	SUV	Grand Cherokee IV (WK2) pre-facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	HIGH	生产区间跨越2013年改款，拆分改款前外廓。	READY
4664_facelift	4664	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH	生产区间跨越2013年改款，拆分改款后外廓。	READY
4676_prefl	4676	SUV	Grand Cherokee IV (WK2) pre-facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	MEDIUM	生产区间跨越2013年改款，拆分改款前外廓。	READY
4676_facelift	4676	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	MEDIUM	生产区间跨越2013年改款，拆分改款后外廓。	READY
4720_prefl	4720	SUV	Explorer II pre-facelift	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	MEDIUM	输入区间覆盖1995至1997年五门外廓。	READY
4720_1998	4720	SUV	Explorer II 1998 update	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	MEDIUM	1998年五门车身长度发生变化，独立派生。	READY
4720_facelift	4720	SUV	Explorer II facelift	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	MEDIUM	输入区间覆盖1999至2001年五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4821	1938	1763	Edmunds 2011 Jeep Grand Cherokee Features and Specs	https://www.edmunds.com/jeep/grand-cherokee/2011/features-specs/
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4821	1943	1760	Edmunds 2014 Jeep Grand Cherokee Features and Specs	https://www.edmunds.com/jeep/grand-cherokee/2014/features-specs/
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	4788	1783	1702	Edmunds 1995 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1995/features-specs/
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	4813	1783	1715	Edmunds 1998 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1998/features-specs/
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	4844	1783	1720	Edmunds 1999 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1999/features-specs/
```

下一步优先处理

1. Mercedes-Benz Sprinter 2-T Bus：`4685`、`4686`、`4687`，确认各 Ktype 覆盖的轴距和车顶组合。
2. Ford Transit Kasten：`4717`，确认 VE6 的车长与车顶分支。
3. 闭合 Lancia Thema Series 3、Lancia A112 Abarth、Ford Escort VI Hatchback 和 Ford Probe II：`4708`、`4709`、`4713`、`4719`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 5 个输入 Ktype：Lancia Thema、Lancia A112 Abarth、Ford Escort 4x4、Ford Transit Kasten、Ford Probe II。
* A112 因 1979 年前后外廓尺寸变化拆为 Series IV 与 Series V–VI；Escort 1.6 16V 4x4 已确认对应五门掀背车，不创建无证据的三门派生行。([汽车目录][1])
* Ford Transit Kasten 直接复用已有 VE6 facelift 四个轴距/车顶尺寸组，本轮不重复输出缓存尺寸。
* 剩余阻塞仅为 Mercedes-Benz Sprinter 2-T Bus 的 3 个 Ktype。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* PENDING 输入 Ktype：3
* READY 映射行：109
* 当前批次引用尺寸组：67
* 本轮首次创建尺寸组：5
* 本轮新增引用的既有尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4708	4708	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
4709_series4	4709	Hatchback	A112 Series IV		3	EU-LANCIA-A112-SERIES-IV-HATCHBACK-3D-01	MEDIUM	生产区间跨越1979年外廓更新，拆分早期车身。	READY
4709_series5_6	4709	Hatchback	A112 Series V-VI		3	EU-LANCIA-A112-SERIES-V-VI-HATCHBACK-3D-01	MEDIUM	生产区间跨越1979年外廓更新，拆分后期车身。	READY
4713	4713	Hatchback	Escort VI facelift		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	HIGH	1.6 16V Flair 4x4对应五门车身。	READY
4717_swb_lowroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	输入未区分短轴低顶分支。	READY
4717_swb_midroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	输入未区分短轴中顶分支。	READY
4717_lwb_midroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	输入未区分长轴中顶分支。	READY
4717_lwb_highroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	输入未区分长轴高顶分支。	READY
4719	4719	Coupe	Probe II	ECP	2	EU-FORD-USA-PROBE-II-ECP-COUPE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435	Automobile-Catalog 1992 Lancia Thema 3.0 V6 LX	https://www.automobile-catalog.com/car/1992/1380305/lancia_thema_3_0_v6_lx.html
EU-LANCIA-A112-SERIES-IV-HATCHBACK-3D-01	3230	1480	1340	Automobile-Catalog 1977 Autobianchi A-112 Abarth 70HP	https://www.automobile-catalog.com/car/1977/75860/autobianchi_a-112_abarth_70hp.html
EU-LANCIA-A112-SERIES-V-VI-HATCHBACK-3D-01	3268	1480	1360	UltimateSpecs Autobianchi A 112 Abarth	https://www.ultimatespecs.com/car-specs/Autobianchi/465/Autobianchi-A-112-Abarth.html
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398	Automobile-Catalog 1995 Ford Escort 1.6i 16V Flair 4x4	https://www.automobile-catalog.com/car/1995/952250/ford_escort_1_6i_16v_flair_4x4.html
EU-FORD-USA-PROBE-II-ECP-COUPE-01	4544	1773	1310	Auto-Data Ford Probe II ECP GT 2.5 V6 24V	https://www.auto-data.net/en/ford-probe-ii-ecp-gt-2.5-v6-24v-165hp-7995
```

## 下一步优先处理

1. 闭合 `4685` Sprinter 208 D Bus 的 `901.371 / 902.371 / 902.372` 短轴、长轴物理边界。
2. 闭合 `4686` Sprinter 212 D Bus 的 `902.471 / 902.472` 分支。
3. 闭合 `4687` Sprinter 214 Bus 的 `902.071 / 902.072 / 902.671 / 902.672` 分支，并确认各分支车顶高度。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/75860/autobianchi_a-112_abarth_70hp.html?utm_source=chatgpt.com "1977 Autobianchi A-112 Abarth (70hp) Specs Review ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 恢复已完成回复 ---
## 更新点

* 剩余 `4685`、`4686`、`4687` 已按 Sprinter I 的短轴/长轴及改款前后物理外廓闭合，共关联 4 个尺寸组。EPC 车身代码用于确认 `3000 mm` 与 `3550 mm` 轴距边界，三维分别由对应年份的 Sprinter 规格页面闭合。([猫车][1])
* 已完成机械检查：表头固定、`id` 唯一、尺寸组唯一、映射引用全部闭合，尺寸及来源字段均非空。
* 当前批次已达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* 最终 Ktype 映射行：119
* 最终 DIMENSION_GROUP：71
* 孤立尺寸组：0
* 缺失映射引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4641	4641	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4643	4643	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4644	4644	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4645	4645	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4646	4646	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4647	4647	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4649	4649	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4650	4650	Sedan	3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH		READY
4651_2dr	4651	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	MEDIUM	输入未区分双门与四门，按E30 316i两种轿车外廓派生。	READY
4651_4dr	4651	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	MEDIUM	输入未区分双门与四门，按E30 316i两种轿车外廓派生。	READY
4652	4652	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
4653	4653	Wagon	Astra F facelift		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH		READY
4654_3dr	4654	Hatchback	Astra F CC		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4654_5dr	4654	Hatchback	Astra F CC		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4655	4655	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4656	4656	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4657	4657	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4658	4658	Sedan	S6 C4	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
4659	4659	Sedan	S6 C4	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
4660	4660	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4661	4661	Wagon	S6 C4	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
4662	4662	Wagon	A6 C4	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
4663	4663	Wagon	S6 C4	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
4664_prefl	4664	SUV	Grand Cherokee IV (WK2) pre-facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	HIGH	生产区间跨越2013年改款，拆分改款前外廓。	READY
4664_facelift	4664	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH	生产区间跨越2013年改款，拆分改款后外廓。	READY
4665	4665	Wagon	RS2 Avant	8C	5	EU-AUDI-80-B4-RS2-AVANT-01	HIGH		READY
4666	4666	Sedan	80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
4667	4667	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4668	4668	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4669	4669	Wagon	100 S4 C4	4A	5	EU-AUDI-100-C4-S4-AVANT-WAGON-01	HIGH		READY
4670	4670	Sedan	100 S4 C4	4A	4	EU-AUDI-100-C4-S4-SEDAN-01	HIGH		READY
4671	4671	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH		READY
4672	4672	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-TURBO-01	HIGH		READY
4673	4673	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-GT2-01	HIGH		READY
4674	4674	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4675	4675	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4676_prefl	4676	SUV	Grand Cherokee IV (WK2) pre-facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	MEDIUM	生产区间跨越2013年改款，拆分改款前外廓。	READY
4676_facelift	4676	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	MEDIUM	生产区间跨越2013年改款，拆分改款后外廓。	READY
4677	4677	Convertible	911 993	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4678	4678	Coupe	911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	HIGH		READY
4679	4679	Hatchback	Polo III (6N)	6N		EU-VW-POLO-III-6N-HATCHBACK-01	HIGH		READY
4681	4681	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
4682	4682	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4683	4683	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4684	4684	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
4685_swb	4685	MPV	Sprinter I pre-facelift			EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-PREFL-01	MEDIUM	输入同时覆盖3000 mm短轴车身，合并901.371与902.371相同外廓。	READY
4685_lwb	4685	MPV	Sprinter I pre-facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-PREFL-01	MEDIUM	902.372为3550 mm长轴车身。	READY
4686_swb	4686	MPV	Sprinter I pre-facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-PREFL-01	HIGH	902.471为3000 mm短轴车身。	READY
4686_lwb	4686	MPV	Sprinter I pre-facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-PREFL-01	HIGH	902.472为3550 mm长轴车身。	READY
4687_swb_prefl	4687	MPV	Sprinter I pre-facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-PREFL-01	MEDIUM	902.071为改款前3000 mm短轴车身。	READY
4687_lwb_prefl	4687	MPV	Sprinter I pre-facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-PREFL-01	MEDIUM	902.072为改款前3550 mm长轴车身。	READY
4687_swb_facelift	4687	MPV	Sprinter I facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-FACELIFT-01	MEDIUM	902.671为改款后3000 mm短轴车身。	READY
4687_lwb_facelift	4687	MPV	Sprinter I facelift	W902		EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-FACELIFT-01	MEDIUM	902.672为改款后3550 mm长轴车身。	READY
4688_prefl	4688	Sedan	C-Klasse W202 pre-facelift	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	同一Ktype生产区间跨越1997年改款，拆分改款前外廓。	READY
4688_facelift	4688	Sedan	C-Klasse W202 facelift	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	同一Ktype生产区间跨越1997年改款，拆分改款后外廓。	READY
4689	4689	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4690	4690	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4691	4691	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4692	4692	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4693	4693	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4694	4694	Sedan	E-Klasse W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
4695	4695	Coupe	Eclipse I (1G)		2	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-01	HIGH		READY
4696	4696	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4697	4697	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4698	4698	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4699	4699	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4700	4700	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4701	4701	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4702	4702	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4703	4703	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4704	4704	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH		READY
4705	4705	Wagon	Scorpio II Turnier		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH		READY
4706	4706	SUV	Grand Cherokee III	WH	5	EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	HIGH		READY
4707_prefl	4707	Sedan	Dedra I pre-facelift	835	4	EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	HIGH	同一Ktype跨改款前后外廓，拆分映射。	READY
4707_facelift	4707	Sedan	Dedra I facelift	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH	同一Ktype跨改款前后外廓，拆分映射。	READY
4708	4708	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
4709_series4	4709	Hatchback	A112 Series IV		3	EU-LANCIA-A112-SERIES-IV-HATCHBACK-3D-01	MEDIUM	生产区间跨越1979年外廓更新，拆分早期车身。	READY
4709_series5_6	4709	Hatchback	A112 Series V-VI		3	EU-LANCIA-A112-SERIES-V-VI-HATCHBACK-3D-01	MEDIUM	生产区间跨越1979年外廓更新，拆分后期车身。	READY
4710	4710	Coupe	Prelude IV	BB1	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH		READY
4711	4711	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
4712	4712	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
4713	4713	Hatchback	Escort VI facelift		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	HIGH	1.6 16V Flair 4x4对应五门车身。	READY
4714	4714	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4715	4715	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4716	4716	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
4717_swb_lowroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	输入未区分短轴低顶分支。	READY
4717_swb_midroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	输入未区分短轴中顶分支。	READY
4717_lwb_midroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	输入未区分长轴中顶分支。	READY
4717_lwb_highroof	4717	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	输入未区分长轴高顶分支。	READY
4718	4718	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	HIGH		READY
4719	4719	Coupe	Probe II	ECP	2	EU-FORD-USA-PROBE-II-ECP-COUPE-01	HIGH		READY
4720_prefl	4720	SUV	Explorer II pre-facelift	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	MEDIUM	输入区间覆盖1995至1997年五门外廓。	READY
4720_1998	4720	SUV	Explorer II 1998 update	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	MEDIUM	1998年五门车身长度发生变化，独立派生。	READY
4720_facelift	4720	SUV	Explorer II facelift	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	MEDIUM	输入区间覆盖1999至2001年五门外廓。	READY
4721	4721	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4722	4722	Convertible	911 993	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4723	4723	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4724	4724	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4725	4725	Hatchback	400 II (HH-R)		5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
4726	4726	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH		READY
4727	4727	SUV	Frontera A Sport		3	EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	HIGH		READY
4728	4728	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH		READY
4729	4729	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
4730	4730	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
4731	4731	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH		READY
4732	4732	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH		READY
4733	4733	Coupe	3 Series E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
4734	4734	Hatchback	Felicia I		5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH		READY
4735	4735	Hatchback	Felicia I		5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH		READY
4736_prefl	4736	Sedan	5 Series F10 pre-facelift	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	MEDIUM	生产区间跨F10改款，按改款前后外廓派生。	READY
4736_facelift	4736	Sedan	5 Series F10 facelift	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	MEDIUM	生产区间跨F10改款，按改款前后外廓派生。	READY
4737	4737	Wagon	850	855	5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
4738	4738	Sedan	850	854	4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
4739	4739	Wagon	940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
4740	4740	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
4741	4741	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
4742	4742	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
4743_3dr	4743	Hatchback	Astra F CC		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
4743_5dr	4743	Hatchback	Astra F CC		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入未区分三门/五门，按Astra F CC两种掀背外廓派生。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4501-4600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Auto-Data Audi A6 (4A,C4) 2.5 TDI	https://www.auto-data.net/en/audi-a6-4a-c4-2.5-tdi-115hp-automatic-26650
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440	Auto-Data Audi A6 Avant (4A,C4) 2.5 TDI	https://www.auto-data.net/en/audi-a6-avant-4a-c4-2.5-tdi-115hp-4771
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	Auto-Data BMW 3 Series Sedan (E36) 318i	https://www.auto-data.net/en/bmw-3-series-sedan-e36-318i-115hp-10036
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	Auto-Data BMW 3 Series Coupe (E30 facelift) 316i	https://www.auto-data.net/en/bmw-3-series-coupe-e30-facelift-1987-316i-102hp-42597
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	Auto-Data BMW 3 Series Sedan (E30 facelift) 316i	https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-316i-100hp-10071
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410	Auto-Data Opel Astra F Classic facelift 2.0i 16V	https://www.auto-data.net/en/opel-astra-f-classic-facelift-1994-2.0i-ecotec-16v-136hp-2470
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525	Auto-Data Opel Astra F Caravan facelift 2.0i 16V	https://www.auto-data.net/en/opel-astra-f-caravan-facelift-1994-2.0i-ecotec-16v-136hp-automatic-25904
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410	Auto-Data Opel Astra F facelift 2.0i 16V	https://www.auto-data.net/en/opel-astra-f-facelift-1994-2.0i-ecotec-16v-136hp-automatic-35064
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410	Auto-Data Opel Astra F facelift 2.0i 16V	https://www.auto-data.net/en/opel-astra-f-facelift-1994-2.0i-ecotec-16v-136hp-automatic-35064
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430	Auto-Data Audi S6 (4A,C4)	https://www.auto-data.net/en/audi-s6-4a-c4-generation-1107
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440	Auto-Data Audi S6 Avant (4A,C4)	https://www.auto-data.net/en/audi-s6-avant-4a-c4-generation-1108
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4821	1938	1763	Edmunds 2011 Jeep Grand Cherokee Features and Specs	https://www.edmunds.com/jeep/grand-cherokee/2011/features-specs/
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4821	1943	1760	Edmunds 2014 Jeep Grand Cherokee Features and Specs	https://www.edmunds.com/jeep/grand-cherokee/2014/features-specs/
EU-AUDI-80-B4-RS2-AVANT-01	4510	1695	1386	Auto-Data Audi RS2 Avant	https://www.auto-data.net/en/audi-rs2-avant-generation-1092
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397	Auto-Data Audi 80 B3 2.0 E	https://www.auto-data.net/en/audi-80-b3-typ-89-89q-8a-2.0-e-113hp-4592
EU-AUDI-80-B4-WAGON-01	4482	1695	1408	Auto-Data Audi 80 Avant B4 1.9 TDI	https://www.auto-data.net/en/audi-80-avant-b4-typ-8c-1.9-tdi-90hp-4545
EU-AUDI-100-C4-S4-AVANT-WAGON-01	4790	1805	1422	Auto-Data Audi S4 Avant (4A,C4) 4.2 V8 quattro	https://www.auto-data.net/en/audi-s4-avant-4a-c4-4.2-v8-280hp-quattro-4082
EU-AUDI-100-C4-S4-SEDAN-01	4790	1805	1420	Auto-Data Audi S4 (4A,C4) 4.2 V8 quattro	https://www.auto-data.net/en/audi-s4-4a-c4-4.2-v8-280hp-quattro-4265
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285	Auto-Data Porsche 911 (993) Turbo 3.6	https://www.auto-data.net/en/porsche-911-993-turbo-3.6-408hp-6611
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270	Auto-Data Porsche 911 (993) GT2 3.6	https://www.auto-data.net/en/porsche-911-993-gt2-3.6-430hp-6612
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315	Auto-Data Porsche 911 (993) generation	https://www.auto-data.net/en/porsche-911-993-generation-1519
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300	Auto-Data Porsche 911 Cabriolet (993) generation	https://www.auto-data.net/en/porsche-911-cabriolet-993-generation-1520
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270	Auto-Data Porsche 911 (993) Carrera RS 3.8	https://www.auto-data.net/en/porsche-911-993-carrera-rs-3.8-300hp-6614
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Auto-Data Volkswagen Polo III (6N) 1.9 SDI	https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.9-sdi-64hp-8475
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant 1.9 TDI Syncro	https://www.auto-data.net/en/volkswagen-golf-iii-variant-1.9-tdi-syncro-90hp-8745
EU-VW-SHARAN-I-MPV-01	4634	1810	1730	Auto-Data Volkswagen Sharan I	https://www.auto-data.net/en/volkswagen-sharan-i-generation-1901
EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-PREFL-01	4835	1933	2335	Truck1 Mercedes-Benz Sprinter 212 D technical data;Mercedes-Benz EPC/Catcar W901-W902 station wagon codes	https://www.truck1.eu/blog/mercedes-benz-sprinter-212-d-tech-specs-t2041;https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en
EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-PREFL-01	5585	1933	2345	CarExpert 1998 Mercedes-Benz Sprinter window van;Mercedes-Benz EPC/Catcar W902 station wagon codes	https://www.carexpert.co.nz/mercedes-benz/sprinter/1998-2-9l-window-van-rwd-diesel-manual-jjo8fsma19980401;https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en
EU-MERCEDES-BENZ-SPRINTER-I-BUS-SWB-FACELIFT-01	4890	1933	2370	CarsGuide 2005 Mercedes-Benz Sprinter dimensions;Mercedes-Benz EPC/Catcar W902 station wagon codes	https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2005;https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en
EU-MERCEDES-BENZ-SPRINTER-I-BUS-LWB-FACELIFT-01	5640	1933	2345	CarsGuide 2005 Mercedes-Benz Sprinter dimensions;Mercedes-Benz EPC/Catcar W902 station wagon codes	https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2005;https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414	Auto-Data Mercedes-Benz C-Class W202 C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-180-122hp-12643
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427	Auto-Data Mercedes-Benz C-Class W202 facelift C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-facelift-1997-c-180-122hp-5g-tronic-44185
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420	Auto-Data Mercedes-Benz E-Class W210	https://www.auto-data.net/en/mercedes-benz-e-class-w210-generation-1125
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-01	4340	1690	1305	Auto-Data Mitsubishi Eclipse I 1G 2.0 i 16V	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-2.0-i-16v-150hp-15626
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1402	Auto-Data Ford Scorpio II 2.9i 24V	https://www.auto-data.net/en/ford-scorpio-ii-gfr-ggr-2.9i-24v-207hp-8144
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442	Auto-Data Ford Scorpio II Turnier 2.9i 24V	https://www.auto-data.net/en/ford-scorpio-ii-turnier-2.9i-24v-210hp-8151
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	4750	1870	1740	Auto-Data Jeep Grand Cherokee III 3.0 CRD 4x4;Automobile-Catalog 2010 Jeep Grand Cherokee 3.0 CRD Limited	https://www.auto-data.net/de/jeep-grand-cherokee-iii-wk-3.0-crd-218hp-4x4-automatic-1151;https://www.automobile-catalog.com/car/2010/1326815/jeep_grand_cherokee_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430	Auto-Data Lancia Dedra (835) 2.0 i.e.	https://www.auto-data.net/en/lancia-dedra-835-2.0-i.e.-113hp-5000
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430	Auto-Data Lancia Dedra (835) 2.0 i.e. Turbo	https://www.auto-data.net/en/lancia-dedra-835-2.0-i.e.-turbo-162hp-5001
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435	Automobile-Catalog 1992 Lancia Thema 3.0 V6 LX	https://www.automobile-catalog.com/car/1992/1380305/lancia_thema_3_0_v6_lx.html
EU-LANCIA-A112-SERIES-IV-HATCHBACK-3D-01	3230	1480	1340	Automobile-Catalog 1977 Autobianchi A-112 Abarth 70HP	https://www.automobile-catalog.com/car/1977/75860/autobianchi_a-112_abarth_70hp.html
EU-LANCIA-A112-SERIES-V-VI-HATCHBACK-3D-01	3268	1480	1360	UltimateSpecs Autobianchi A 112 Abarth	https://www.ultimatespecs.com/car-specs/Autobianchi/465/Autobianchi-A-112-Abarth.html
EU-HONDA-PRELUDE-IV-COUPE-2D-01	4440	1765	1290	Auto-Data Honda Prelude IV BB1 2.2 VTEC	https://www.auto-data.net/en/honda-prelude-iv-bb-2.2-i-16v-vtec-bb1-185hp-12200
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424	Auto-Data Ford Mondeo I Sedan generation	https://www.auto-data.net/en/ford-mondeo-i-sedan-generation-1703
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510	Auto-Data Ford Mondeo I Wagon 2.0i 4x4	https://www.auto-data.net/en/ford-mondeo-i-wagon-2.0i-4x4-136hp-7741
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398	Automobile-Catalog 1995 Ford Escort 1.6i 16V Flair 4x4	https://www.automobile-catalog.com/car/1995/952250/ford_escort_1_6i_16v_flair_4x4.html
EU-FORD-GALAXY-I-MPV-01	4634	1810	1730	Auto-Data Ford Galaxy I	https://www.auto-data.net/en/ford-galaxy-i-generation-917
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Autotrader Australia Ford Transit dimensions	https://www.autotrader.com.au/ford/transit/dimensions
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Autotrader Australia Ford Transit dimensions	https://www.autotrader.com.au/ford/transit/dimensions
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Autotrader Australia Ford Transit dimensions	https://www.autotrader.com.au/ford/transit/dimensions
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Autotrader Australia Ford Transit dimensions	https://www.autotrader.com.au/ford/transit/dimensions
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	4783	1928	1789	Auto-Data Range Rover Sport I facelift 5.0 Supercharged	https://www.auto-data.net/en/land-rover-range-rover-sport-i-facelift-2009-5.0-lr-v8-supercharged-510hp-awd-automatic-23040
EU-FORD-USA-PROBE-II-ECP-COUPE-01	4544	1773	1310	Auto-Data Ford Probe II ECP GT 2.5 V6 24V	https://www.auto-data.net/en/ford-probe-ii-ecp-gt-2.5-v6-24v-165hp-7995
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	4788	1783	1702	Edmunds 1995 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1995/features-specs/
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	4813	1783	1715	Edmunds 1998 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1998/features-specs/
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	4844	1783	1720	Edmunds 1999 Ford Explorer Features and Specs	https://www.edmunds.com/ford/explorer/1999/features-specs/
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380	Auto-Data Rover 600 RH 620 SDi	https://www.auto-data.net/en/rover-600-rh-620-sdi-105hp-11591
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390	Auto-Data Rover 400 Hatchback HH-R	https://www.auto-data.net/en/rover-400-hatchback-hh-r-generation-387
EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	4692	1764	1753	Auto-Data Opel Frontera A 2.8 TDi 4x4	https://www.auto-data.net/en/opel-frontera-a-2.8-tdi-113hp-4x4-25887
EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	4192	1780	1721	Auto-Data Opel Frontera A Sport	https://www.auto-data.net/en/opel-frontera-a-sport-generation-569
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410	Auto-Data Toyota Carina E T19 1.6 i 16V	https://www.auto-data.net/en/toyota-carina-e-t19-1.6-i-16v-99hp-3997
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410	Auto-Data Toyota Carina E Hatch T19 1.6 i 16V	https://www.auto-data.net/en/toyota-carina-e-hatch-t19-1.6-i-16v-99hp-3984
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335	Auto-Data BMW M3 Coupe E36 3.0i	https://www.auto-data.net/en/bmw-m3-coupe-e36-3.0i-286hp-9879
EU-SKODA-FELICIA-I-HATCHBACK-01	3883	1635	1415	Auto-Data Skoda Felicia I Hatchback	https://www.auto-data.net/en/skoda-felicia-i-generation-1368
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	Auto-Data BMW 5 Series Sedan F10 525d	https://www.auto-data.net/en/bmw-5-series-sedan-f10-525d-218hp-17270
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464	Auto-Data BMW 5 Series Sedan F10 LCI 520i	https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-520i-184hp-steptronic-19958
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Auto-Data Volvo 850 Combi LW 2.0 10V	https://www.auto-data.net/en/volvo-850-combi-lw-2.0-10v-126hp-9197
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415	Auto-Data Volvo 850 LS 2.0 10V	https://www.auto-data.net/en/volvo-850-ls-2.0-10v-126hp-9207
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435	Auto-Data Volvo 940 Combi 945 2.3i Turbo	https://www.auto-data.net/en/volvo-940-combi-945-2.3i-turbo-165hp-9297
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425	Auto-Data Volvo 940 944 2.3i Turbo	https://www.auto-data.net/en/volvo-940-944-2.3i-turbo-165hp-9288
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Auto-Data Opel Vectra A facelift 1.7 D	https://www.auto-data.net/en/opel-vectra-a-facelift-1992-1.7-d-60hp-2303
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4501-4600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en&utm_source=chatgpt.com "Van-Europe - Catcar.info"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4501-4600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4501-4600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6077 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1850 行）

