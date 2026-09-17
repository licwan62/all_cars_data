# 任务：all 第 4501-4600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0046__66587237


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
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	4435	1844	1244
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474
EU-CITROEN-C-CROSSER-I-SUV-5D-01	4645	1805	1715
EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	4512	1923	1199
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-KUGA-I-C394-SUV-5D-01	4443	1842	1710
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480
EU-HYUNDAI-IX35-LM-SUV-5D-01	4410	1820	1660
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	4044	1748	1393
EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	4037	1748	1397
EU-PEUGEOT-207-HATCHBACK-3D-01	4030	1720	1472
EU-PEUGEOT-207-HATCHBACK-5D-01	4030	1720	1472
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1720	1472
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472
EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	4030	1720	1472
EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	4045	1748	1472
EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	4030	1720	1472
EU-PEUGEOT-207-I-SW-WAGON-5D-01	4156	1748	1527
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	5599	2024	2505
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	4749	2024	2515
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-LWB-01	5506	2020	2150
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-MWB-01	5006	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-LWB-01	5490	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-MWB-01	4990	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-CAB-LWB-01	5680	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-DOUBLE-CAB-LWB-01	5710	2020	2150
EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	5599	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870
EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690
EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	4749	2024	2515
EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-II-BUS-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-BUS-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-BUS-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760
EU-RENAULT-KANGOO-I-ELECTROAD-MPV-5D-01	3990	1660	1820
EU-RENAULT-KANGOO-I-FACELIFT-MPV-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498
EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	3992	1642	1498
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468
EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	4214	1684	1607
EU-SKODA-ROOMSTER-5J-MPV-PREFL-01	4205	1684	1607
EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	4214	1684	1607
EU-SKODA-ROOMSTER-I-MPV-PREFL-01	4205	1684	1607
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	4213	1684	1607
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	4205	1684	1607
EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Hyundai	Ix35	2.0 4WD	SUV	Allrad	Benzin	120	163	Jan 2010	Dec 2015	2024-03-01	33132
Hyundai	Ix35	2.0 Crdi	SUV	Frontantrieb	Diesel	100	136	Jan 2010	Dec 2015	2024-03-01	33133
Hyundai	Ix35	2.0 Crdi 4WD	SUV	Allrad	Diesel	100	136	Jan 2010	Dec 2015	2024-03-01	33134
Hyundai	Ix35	2.0 Crdi 4WD	SUV	Allrad	Diesel	135	184	Jan 2010	Dec 2015	2024-03-01	33135
Hyundai	Ix35	2	SUV	Frontantrieb	Benzin	122	166	Jan 2010	Dec 2015	2024-03-01	33149
Hyundai	H-1 cargo	2.4	Kasten	Heckantrieb	Benzin	129	175	Mar 2008	-	2024-03-01	33152
Hyundai	H-1 cargo	2.5 Crdi	Kasten	Heckantrieb	Diesel	81	110	Feb 2008	-	2024-03-01	33153
Ferrari	F430	F430	Cabriolet	Heckantrieb	Benzin	357	486	Mar 2008	Dec 2009	2024-03-01	33163
Ferrari	F430	F430	Coupe	Heckantrieb	Benzin	357	486	Mar 2008	Dec 2009	2024-03-01	33164
Ferrari	F430	430 Scuderia	Coupe	Heckantrieb	Benzin	372	506	Sep 2007	Dec 2009	2024-03-01	33165
Hyundai	I30	1.4	Kombi	Frontantrieb	Benzin	80	109	Nov 2009	Jun 2012	2024-03-01	33176
Opel	Insignia a	2.0 Cdti 4X4	Stufenheck	Allrad	Diesel	120	163	Jul 2013	Mar 2017	2024-03-01	33191
Suzuki	Sx4 s-Cross	1.6	Schrägheck	Frontantrieb	Benzin	88	120	Aug 2013	Jun 2022	2025-06-01	33192
Mercedes-benz	G-Klasse	G 500	Geländewagen offen	Allrad	Benzin	285	388	Dec 2009	Aug 2014	2024-03-01	33193
Renault	Modus / grand	1.5 DCI	Schrägheck	Frontantrieb	Diesel	60	82	Sep 2004	Oct 2007	2025-12-01	33195
Honda	Integra	1.8	Coupe	Frontantrieb	Benzin	107	146	Jul 1993	Nov 2001	2024-03-01	33203
Mitsubishi	Pajero iv	3.2 Di-d 4WD	SUV	Allrad	Diesel	147	200	Jan 2009	-	2024-03-01	33209
Honda	Jazz iii	1.5 I-vtec	Schrägheck	Frontantrieb	Benzin	88	120	Jul 2008	Jun 2014	2026-04-01	33211
Chevrolet	Corvette	6.2	Cabriolet	Heckantrieb	Benzin	321	437	Feb 2008	Aug 2013	2024-03-01	33213
Peugeot	207	1.4 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Apr 2007	-	2024-03-01	33230
Peugeot	207	1.6 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Apr 2007	Oct 2012	2024-03-01	33231
Skoda	Fabia ii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Mar 2010	Dec 2014	2024-03-01	33243
Skoda	Fabia ii combi	1.2 TSI	Kombi	Frontantrieb	Benzin	77	105	Mar 2010	Dec 2014	2024-03-01	33244
Skoda	Octavia	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Feb 2010	Jun 2013	2024-03-01	33245
Skoda	Octavia	1.2 TSI	Kombi	Frontantrieb	Benzin	77	105	Feb 2010	Apr 2013	2024-03-01	33246
Skoda	Roomster	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	77	105	Mar 2010	May 2015	2024-03-01	33247
Seat	Altea	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	77	105	Apr 2010	Jul 2015	2024-05-01	33248
Seat	Altea	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	77	105	Apr 2010	Jul 2015	2024-05-01	33249
Seat	Leon	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Feb 2010	Dec 2012	2024-03-01	33250
Audi	A3	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Apr 2010	Aug 2012	2024-03-01	33251
Audi	A3	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Apr 2010	Mar 2013	2024-03-01	33252
Citroën	Berlingo	1.6 VTI 120	Großraumlimousine	Frontantrieb	Benzin	88	120	Nov 2009	Dec 2018	2026-05-01	33258
Peugeot	207/207+	1.6 16V Turbo	Schrägheck	Frontantrieb	Benzin	115	156	Oct 2009	Dec 2012	2024-03-01	33259
Peugeot	207/207+	1.6 HDI	Schrägheck	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2012	2024-03-01	33260
Peugeot	207/207+	1.6 HDI 110	Schrägheck	Frontantrieb	Diesel	82	112	Aug 2009	Dec 2012	2024-03-01	33261
Peugeot	207 cc	1.6 HDI	Cabriolet	Frontantrieb	Diesel	82	112	Aug 2009	Oct 2013	2024-03-01	33262
Peugeot	207 cc	1.6 16V Turbo	Cabriolet	Frontantrieb	Benzin	115	156	Oct 2009	Dec 2013	2024-03-01	33263
Peugeot	207 sw	1.6 HDI	Kombi	Frontantrieb	Diesel	82	112	Aug 2009	Oct 2013	2024-03-01	33264
Peugeot	207 sw	1.6 HDI	Kombi	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2013	2024-03-01	33265
Peugeot	3008 i	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	120	163	Jun 2009	Aug 2016	2024-11-01	33266
Peugeot	308 i	1.4 16V	Schrägheck	Frontantrieb	Benzin	72	98	Dec 2009	Oct 2014	2024-03-01	33267
Peugeot	308 i	1.6 THP 16V	Schrägheck	Frontantrieb	Benzin	115	156	Oct 2009	Oct 2014	2024-03-01	33269
Peugeot	308 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	68	92	Nov 2009	Oct 2014	2024-03-01	33270
Peugeot	308 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	82	112	Dec 2009	Oct 2014	2024-03-01	33271
Peugeot	308 sw i	1.6 THP 16V	Kombi	Frontantrieb	Benzin	115	156	Oct 2009	Oct 2014	2024-03-01	33272
Peugeot	308 sw i	1.6 HDI	Kombi	Frontantrieb	Diesel	82	112	Dec 2009	Oct 2014	2024-03-01	33273
Peugeot	Boxer	3.0 HDI 145	Bus	Frontantrieb	Diesel	107	146	Apr 2010	Dec 2013	2024-03-01	33274
Peugeot	Boxer	3.0 HDI 145	Kasten	Frontantrieb	Diesel	107	146	Apr 2010	Dec 2013	2024-03-01	33275
Peugeot	Boxer	3.0 HDI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2010	Dec 2013	2024-03-01	33276
Renault	Kangoo	1.6 16V LPG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	78	106	Feb 2008	-	2024-03-01	33277
Renault	Master iii	2.3 DCI 100 FWD	Kasten	Frontantrieb	Diesel	74	101	Feb 2010	Jun 2014	2026-03-01	33278
Renault	Master iii	2.3 DCI 125 FWD	Kasten	Frontantrieb	Diesel	92	125	Feb 2010	Jun 2019	2026-03-01	33279
Renault	Master iii	2.3 DCI 125 RWD	Kasten	Heckantrieb	Diesel	92	125	Feb 2010	Jun 2019	2026-03-01	33280
Renault	Master iii	2.3 DCI 145 RWD	Kasten	Heckantrieb	Diesel	107	146	Feb 2010	Dec 2024	2026-03-01	33281
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	88	120	Apr 2010	Dec 2020	2024-03-01	33298
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	125	170	Apr 2010	Oct 2018	2024-03-01	33299
Alfa Romeo	Giulietta	1.8 TBI	Schrägheck	Frontantrieb	Benzin	173	235	Apr 2010	Feb 2016	2024-03-01	33300
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	125	170	Apr 2010	Dec 2020	2024-03-01	33301
Alfa Romeo	Giulietta	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	77	105	Apr 2010	Feb 2016	2024-03-01	33302
Audi	A1	1.2 Tfsi	Schrägheck	Frontantrieb	Benzin	63	86	May 2010	Apr 2015	2024-03-01	33303
Audi	A1	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	May 2010	Apr 2015	2024-03-01	33304
Audi	A1	1.4 Tfsi	Schrägheck	Frontantrieb	Benzin	90	122	May 2010	Apr 2015	2024-03-01	33305
VW	Touareg	3.6 V6 FSI	SUV	Allrad	Benzin	206	280	Apr 2010	Mar 2018	2024-03-01	33306
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	176	240	Jan 2010	Mar 2018	2024-03-01	33307
VW	Touareg	4.2 V8 TDI	SUV	Allrad	Diesel	250	340	Jan 2010	Mar 2018	2024-03-01	33308
VW	Touareg	3.0 V6 TSI Hybrid	SUV	Allrad	Benzin/Elektro	279	379	Apr 2010	Mar 2018	2024-03-01	33309
Skoda	Fabia ii	1.2 TSI	Schrägheck	Frontantrieb	Benzin	63	86	Mar 2010	Dec 2014	2024-03-01	33311
Skoda	Fabia ii combi	1.2 TSI	Kombi	Frontantrieb	Benzin	63	86	Mar 2010	Dec 2014	2024-03-01	33312
Skoda	Roomster	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	63	86	Mar 2010	May 2015	2024-03-01	33313
Skoda	Fabia ii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Mar 2010	Dec 2014	2024-03-01	33314
Skoda	Fabia ii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Mar 2010	Dec 2014	2024-03-01	33315
Skoda	Fabia ii combi	1.6 TDI	Kombi	Frontantrieb	Diesel	66	90	Mar 2010	Dec 2014	2024-03-01	33316
Skoda	Fabia ii combi	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Mar 2010	Dec 2014	2024-03-01	33317
Skoda	Roomster	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	66	90	Mar 2010	May 2015	2024-03-01	33320
Skoda	Roomster	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	77	105	Mar 2010	May 2015	2024-03-01	33321
Skoda	Superb ii	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Oct 2009	Mar 2010	2024-03-01	33322
Citroën	C2	1.4 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Sep 2006	Dec 2009	2024-03-01	33323
Seat	Ibiza iv st	1.2 TDI	Kombi	Frontantrieb	Diesel	55	75	Apr 2010	May 2015	2024-03-01	33324
Seat	Ibiza iv st	1.2 TSI	Kombi	Frontantrieb	Benzin	77	105	Sep 2010	May 2015	2024-03-01	33325
Seat	Ibiza iv st	1.2	Kombi	Frontantrieb	Benzin	44	60	May 2010	May 2015	2024-03-01	33326
Seat	Ibiza iv st	1.2	Kombi	Frontantrieb	Benzin	51	70	May 2010	May 2015	2024-03-01	33327
Seat	Ibiza iv st	1.4	Kombi	Frontantrieb	Benzin	63	85	Mar 2010	May 2015	2024-03-01	33328
Seat	Ibiza iv st	1.6 TDI	Kombi	Frontantrieb	Diesel	66	90	Mar 2010	May 2015	2024-03-01	33329
Seat	Ibiza iv st	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Mar 2010	May 2015	2024-03-01	33330
Ford	C-Max	2.0 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	107	145	Apr 2009	Sep 2010	2024-03-01	33331
Ford	C-Max	2.0 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	107	145	Jun 2008	Sep 2010	2024-03-01	33332
Ford	Fiesta vi	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	71	97	Jan 2009	Apr 2017	2024-03-01	33333
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	70	95	Feb 2010	Dec 2015	2024-03-01	33334
Ford	Fiesta vi van	1.25	Kasten/Schrägheck	Frontantrieb	Benzin	60	82	Jan 2009	Apr 2017	2024-07-01	33335
Ford	Fiesta vi van	1.4 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Jan 2009	Apr 2017	2024-07-01	33336
Ford	Fiesta vi van	1.6 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Jan 2009	Apr 2017	2024-07-01	33337
Ford	Kuga i	2.0 Tdci	SUV	Frontantrieb	Diesel	103	140	Mar 2010	Nov 2012	2024-03-01	33338
Ford	Kuga i	2.0 Tdci 4X4	SUV	Allrad	Diesel	103	140	Mar 2010	Nov 2012	2024-03-01	33339
Ford	Kuga i	2.0 Tdci 4X4	SUV	Allrad	Diesel	120	163	Mar 2010	Nov 2012	2024-03-01	33340
Citroën	C-Crosser	2.2 HDI	Kasten/SUV	Allrad	Diesel	115	156	Jan 2009	-	2024-03-01	33341
Ford	Focus ii	2.0 CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	107	145	Apr 2009	Jul 2011	2024-03-01	33342
Ford	Focus ii	2.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	107	145	Jun 2008	Jul 2011	2024-03-01	33343
Ford	Focus ii turnier	2.0 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	107	145	Jun 2008	Jul 2011	2024-03-01	33344
Ford	Focus ii turnier	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	85	115	Oct 2009	Sep 2012	2024-03-01	33345
Ford	Focus ii	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	85	115	Oct 2009	Jul 2011	2024-03-01	33346


--- Round 1 / checkpoint 续跑 ---
## 更新点

* 按缓存优先完成既有尺寸组关联，已覆盖 77 个输入 Ktype。
* 新建并闭合 Ferrari F430 Coupe、F430 Spider 两个尺寸([法拉利][1])([法拉利][1])
* 未对复用尺寸组重复输出三维和来源。
* 剩余 PENDING 集中于 H-1 Cargo、G-Class Cabriolet、Modus、Integra、Master III、Audi A1、Touareg II、Ibiza IV ST。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：77
* PENDING 输入 Ktype：23
* READY 映射行：96
* PENDING 映射行：23
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33132	33132	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33133	33133	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33134	33134	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33135	33135	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33149	33149	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33152	33152	Van	H-1 TQ	TQ			LOW	需确认短/长轴及车顶高度分支。	PENDING: H-1 Cargo外廓分支未闭合
33153	33153	Van	H-1 TQ	TQ			LOW	需确认短/长轴及车顶高度分支。	PENDING: H-1 Cargo外廓分支未闭合
33163	33163	Convertible	F430	F131	2	EU-FERRARI-F430-F131-CONVERTIBLE-2D-01	HIGH		READY
33164	33164	Coupe	F430	F131	2	EU-FERRARI-F430-F131-COUPE-2D-01	HIGH		READY
33165	33165	Coupe	F430	F131	2	EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	HIGH		READY
33176	33176	Wagon	i30 FD	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
33191	33191	Sedan	Insignia A facelift	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH		READY
33192	33192	Hatchback	SX4 S-Cross I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH		READY
33193	33193	Convertible	G-Class W463	W463	2		LOW	需确认G 500 Cabriolet短轴外廓及不含后视镜宽度。	PENDING: G-Class Cabriolet尺寸未闭合
33195	33195	Hatchback	Modus I	J77	5		LOW	需排除Grand Modus并闭合标准Modus外廓。	PENDING: Modus/Grand边界未闭合
33203	33203	Coupe	Integra III	DC2	3		LOW	需闭合欧洲版DC2三维及宽度口径。	PENDING: Integra DC2尺寸未闭合
33209_3dr	33209	SUV	Pajero IV	V80	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	短轴三门分支。	READY
33209_5dr	33209	SUV	Pajero IV	V90	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	长轴五门分支。	READY
33211	33211	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	HIGH		READY
33213	33213	Convertible	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	HIGH		READY
33230_prefl	33230	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门厢式版改款前外廓。	READY
33230_facelift	33230	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门厢式版改款后外廓。	READY
33231_prefl	33231	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门厢式版改款前外廓。	READY
33231_facelift	33231	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门厢式版改款后外廓。	READY
33243	33243	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33244	33244	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33245	33245	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
33246	33246	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
33247	33247	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33248	33248	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33249	33249	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33250	33250	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH		READY
33251	33251	Hatchback	A3 II facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH		READY
33252	33252	Hatchback	A3 II facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
33258	33258	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
33259_3dr	33259	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33259_5dr	33259	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33260_3dr	33260	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33260_5dr	33260	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33261_3dr	33261	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33261_5dr	33261	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33262	33262	Convertible	207 CC facelift	WD	2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH		READY
33263	33263	Convertible	207 CC facelift	WD	2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH		READY
33264	33264	Wagon	207 SW I	WK	5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
33265	33265	Wagon	207 SW I	WK	5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
33266	33266	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH		READY
33267	33267	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33269	33269	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33270	33270	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33271	33271	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33272	33272	Wagon	308 SW I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
33273	33273	Wagon	308 SW I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
33274_l1h1	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L1H1-01	HIGH	L1H1客车分支。	READY
33274_l2h2	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L2H2-01	HIGH	L2H2客车分支。	READY
33274_l3h2	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L3H2-01	HIGH	L3H2客车分支。	READY
33275_l1h1	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	HIGH	L1H1厢式车分支。	READY
33275_l1h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	HIGH	L1H2厢式车分支。	READY
33275_l2h1	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	HIGH	L2H1厢式车分支。	READY
33275_l2h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	HIGH	L2H2厢式车分支。	READY
33275_l3h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	HIGH	L3H2厢式车分支。	READY
33275_l3h3	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	HIGH	L3H3厢式车分支。	READY
33275_l4h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	HIGH	L4H2厢式车分支。	READY
33275_l4h3	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	HIGH	L4H3厢式车分支。	READY
33276_l1	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	HIGH	L1底盘驾驶室分支。	READY
33276_l2	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	HIGH	L2底盘驾驶室分支。	READY
33276_l3	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	HIGH	L3底盘驾驶室分支。	READY
33276_l4	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	HIGH	L4底盘驾驶室分支。	READY
33277_mpv	33277	MPV	Kangoo II			EU-RENAULT-KANGOO-II-MPV-5D-01	MEDIUM	乘用MPV分支。	READY
33277_van	33277	Van	Kangoo II			EU-RENAULT-KANGOO-II-VAN-01	MEDIUM	厢式车分支。	READY
33278	33278	Van	Master III	X62			LOW	需按FWD闭合可用L/H外廓分支。	PENDING: Master III FWD尺寸分支未闭合
33279	33279	Van	Master III	X62			LOW	需按FWD闭合可用L/H外廓分支。	PENDING: Master III FWD尺寸分支未闭合
33280	33280	Van	Master III	X62			LOW	需按RWD闭合可用L/H外廓分支。	PENDING: Master III RWD尺寸分支未闭合
33281	33281	Van	Master III	X62			LOW	需按RWD闭合可用L/H外廓分支。	PENDING: Master III RWD尺寸分支未闭合
33298	33298	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33299	33299	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33300	33300	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33301	33301	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33302	33302	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33303	33303	Hatchback	A1 I	8X1	3		LOW	2010起三门A1，需闭合官方三维及宽度口径。	PENDING: Audi A1 8X1尺寸未闭合
33304	33304	Hatchback	A1 I	8X1	3		LOW	2010起三门A1，需闭合官方三维及宽度口径。	PENDING: Audi A1 8X1尺寸未闭合
33305	33305	Hatchback	A1 I	8X1	3		LOW	2010起三门A1，需闭合官方三维及宽度口径。	PENDING: Audi A1 8X1尺寸未闭合
33306	33306	SUV	Touareg II	7P5	5		LOW	生产期跨2014改款，需确认改款前后外廓并拆分。	PENDING: Touareg II改款边界未闭合
33307	33307	SUV	Touareg II	7P5	5		LOW	生产期跨2014改款，需确认改款前后外廓并拆分。	PENDING: Touareg II改款边界未闭合
33308	33308	SUV	Touareg II	7P5	5		LOW	生产期跨2014改款，需确认改款前后外廓并拆分。	PENDING: Touareg II改款边界未闭合
33309	33309	SUV	Touareg II	7P5	5		LOW	生产期跨2014改款，需确认改款前后外廓并拆分。	PENDING: Touareg II改款边界未闭合
33311	33311	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33312	33312	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33313	33313	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33314	33314	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33315	33315	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33316	33316	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33317	33317	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33320	33320	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33321	33321	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33322	33322	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH		READY
33323	33323	Van	C2 I	JM	3	EU-CITROEN-C2-I-HATCHBACK-3D-01	MEDIUM	三门厢式版与乘用车外廓一致。	READY
33324	33324	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33325	33325	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33326	33326	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33327	33327	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33328	33328	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33329	33329	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33330	33330	Wagon	Ibiza IV ST	6J8	5		LOW	需闭合ST旅行版三维及不含后视镜宽度。	PENDING: Ibiza IV ST尺寸未闭合
33331	33331	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
33332	33332	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
33333	33333	Hatchback	Fiesta VII	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	当前Ktype未区分三门/五门，外廓尺寸组一致。	READY
33334	33334	Hatchback	Fiesta VII	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	当前Ktype未区分三门/五门，外廓尺寸组一致。	READY
33335	33335	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33336	33336	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33337	33337	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33338	33338	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33339	33339	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33340	33340	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33341	33341	Van	C-Crosser I	CW0	5	EU-CITROEN-C-CROSSER-I-SUV-5D-01	MEDIUM	商用厢式版与SUV外廓一致。	READY
33342	33342	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
33343	33343	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
33344	33344	Wagon	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
33345	33345	Wagon	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
33346	33346	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FERRARI-F430-F131-CONVERTIBLE-2D-01	4511	1923	1234	Ferrari F430 Spider official model page	https://www.ferrari.com/en-EN/auto/f430-spider
EU-FERRARI-F430-F131-COUPE-2D-01	4511	1923	1214	Ferrari F430 official model page	https://www.ferrari.com/en-EN/auto/f430
```

## 下一步优先处理

1. 优先闭合 Renault Master III 的 FWD/RWD 长度与车顶组合，一次解决 4 个 Ktype。
2. 批量闭合 Audi A1、Touareg II 改款前后、Ibiza IV ST 三个重复引用量较高的尺寸组。
3. 最后处理 H-1 Cargo、G-Class Cabriolet、Modus、Integra 四个独立外廓。

推进信号：CONTINUE

[1]: https://www.ferrari.com/en-EN/auto/f430-spider?utm_source=chatgpt.com "Ferrari F430 Spider (2005) - Ferrari.com"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 闭合 Hyundai H-1 Cargo、Renault Modus、Audi A1 8X1、SEAT Ibiza IV ST 四个外廓家族，共消除 13 个 PENDING。
* Audi A1 使用原厂技术数据确认 `3954 × 1740 × 1416 mm`，其中宽度明确为不含后视镜；Ibiza ST 技术规格确认 `4236 × 1693 × 1445 mm`。([奥迪新闻][1])
* H-1 使用 2009 年车主手册规格闭合为 `5125 × 1920 × 1925 mm`；33195 的生产期截至 2007 年，闭合为标准轴距 Modus，而非后续 Grand Modus。([汽车手册在线][2])
* 本轮未重复输出任何已存在尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：90
* PENDING 输入 Ktype：10
* READY 映射行：109
* PENDING 映射行：10
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33152	33152	Van	H-1 TQ	TQ		EU-HYUNDAI-H-1-TQ-VAN-01	HIGH		READY
33153	33153	Van	H-1 TQ	TQ		EU-HYUNDAI-H-1-TQ-VAN-01	HIGH		READY
33195	33195	Hatchback	Modus I	J77	5	EU-RENAULT-MODUS-I-HATCHBACK-5D-01	HIGH	生产期早于Grand Modus，闭合为标准Modus外廓。	READY
33303	33303	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33304	33304	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33305	33305	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33324	33324	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33325	33325	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33326	33326	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33327	33327	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33328	33328	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33329	33329	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33330	33330	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H-1-TQ-VAN-01	5125	1920	1925	Hyundai H-1 (Grand Starex) 2009 Owner's Manual	https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2009-owner-s-manual-rhd-uk-australia/?srch=dimensions
EU-RENAULT-MODUS-I-HATCHBACK-5D-01	3792	1695	1589	Automobile-Catalog 2004 Renault Modus 1.6 16V 88 specifications	https://www.automobile-catalog.com/car/2004/2951165/renault_modus_1_6_16v_88.html
EU-AUDI-A1-8X1-HATCHBACK-3D-01	3954	1740	1416	Audi UK A1 1.4 TFSI official technical data	https://press.audi.co.uk/assets/documents/original/9527-AudiUK00000111A114TFSIStronic122g.pdf
EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	4236	1693	1445	SEAT Ibiza ST technical specifications	https://www.motorshow.me/uploadImages/GalleryDocs/Doc6003.pdf
```

## 下一步优先处理

1. 闭合 Renault Master III 的 FWD/RWD、长度、车顶高度及改款边界，处理 33278–33281。
2. 按具体发动机生产期判断 Touareg II 是否需要改款前后双分支，处理 33306–33309。
3. 最后解决 G 500 Cabriolet 高度来源冲突和 Integra DC2 欧洲版宽度冲突。

推进信号：CONTINUE

[1]: https://press.audi.co.uk/assets/documents/original/9527-AudiUK00000111A114TFSIStronic122g.pdf "A1 1.4 TFSI S tronic 122g Technical Data UK October 2010.xls"
[2]: https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2009-owner-s-manual-rhd-uk-australia/?srch=dimensions&utm_source=chatgpt.com "dimensions Hyundai H-1 (Grand Starex) 2009 Owner's Manual - RHD (UK, Australia) (303 Pages)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* 33193 已按 2012 年改款前后拆分为两个 G 500 Cabriolet 外廓。
* 33203 已闭合为 Honda Integra III DC2 三门 Coupe 尺寸组。
* 33306–33309 已按 Touareg II 改款前后外廓拆分；官方资料确认车长由 4795 mm 变为 4801 mm，车身宽度均为 1940 mm，高度均为 1732 mm。([大众汽车英国][1])
* Touareg 的 3.6 FSI、V8 TDI 与 Hybrid 均存在改款后版本，因此保留改款前后两个物理分支。([vw.ca][2])
* 本轮共消除 6 个 PENDING；当前仅剩 Renault Master III 四个 Ktype。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：96
* PENDING 输入 Ktype：4
* READY 映射行：120
* PENDING 映射行：4
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33193_prefl	33193	Convertible	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-PREFL-01	HIGH	2012改款前敞篷外廓。	READY
33193_facelift	33193	Convertible	G-Class W463 facelift	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-01	HIGH	2012改款后敞篷外廓。	READY
33203	33203	Coupe	Integra III	DC2	3	EU-HONDA-INTEGRA-III-DC2-COUPE-3D-01	HIGH	三门Liftback Coupe外廓。	READY
33306_prefl	33306	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33306_facelift	33306	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
33307_prefl	33307	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33307_facelift	33307	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	MEDIUM	2014改款后外廓。	READY
33308_prefl	33308	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33308_facelift	33308	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
33309_prefl	33309	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33309_facelift	33309	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-PREFL-01	4257	1760	1941	Mercedes-Benz Public Archive G 500 short wheelbase 2008–2012	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-500-kurzer-Radstand-2008---2012.xhtml?oid=191039063
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-01	4257	1760	1951	Auto-Data Mercedes-Benz G-Class Cabriolet W463 facelift 2012 G 500	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w463-facelift-2012-g-500-v8-388hp-4matic-7g-tronic-plus-42490
EU-HONDA-INTEGRA-III-DC2-COUPE-3D-01	4380	1710	1335	Auto-Data Honda Integra III DC2; CarsGuide 2000 Honda Integra GSi dimensions	https://www.auto-data.net/en/honda-integra-iii-dc2-generation-2579;https://www.carsguide.com.au/honda/integra/car-dimensions/2000
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1732	Volkswagen UK Touareg official brochure February 2011	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touareg/touareg-nf/vw-touareg-nf-brochure-feb-2011.pdf
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1732	Volkswagen UK Touareg official brochure December 2015	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touareg/touareg-fl/vw-touareg-fl-brochure-dec-2015.pdf
```

## 下一步优先处理

1. 一次性闭合 Master III FWD 的 L1/L2/L3 与 H1/H2/H3 外廓组合，并同步更新 33278、33279。
2. 闭合 Master III RWD 的 L3/L4、H2/H3 及 SRW/DRW 差异，并同步更新 33280、33281。
3. 四个 Master Ktype 闭合后立即进行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touareg/touareg-nf/vw-touareg-nf-brochure-feb-2011.pdf?utm_source=chatgpt.com "TOUAREG"
[2]: https://www.vw.ca/idhub/content/dam/onehub_pkw/importers/ca/2022/en/editorial-pieces/older-model-content/buyers-guides/touareg/2015-Volkswagen-Touareg.pdf?utm_source=chatgpt.com "2015 Touareg"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
## 更新点

* 闭合 33278、33279 的 FWD 六种 L/H 外廓，以及 33280 的 RWD 七种 L/H、SRW/DRW 外廓。
* Renault 官方尺寸表明确列出各分支的总长、`2070 mm` 不含后视镜宽度及空载高度；高度存在配置区间时，按“最大外部高度”口径采用该配置区间上限。
* 33281 尚未闭合：其生产期跨越 2019 年外观更新，更新后的车长变为 L3 `6225 mm`、L4 `6875 mm`，不能直接复用本轮建立的 2010–2019 组；仍需完成改款后 RWD 的 SRW/DRW 分支边界。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：99
* PENDING 输入 Ktype：1
* READY 映射行：139
* PENDING 映射行：1
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33278_l1h1	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	HIGH	FWD L1H1外廓。	READY
33278_l1h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	HIGH	FWD L1H2外廓。	READY
33278_l2h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	HIGH	FWD L2H2外廓。	READY
33278_l2h3	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	HIGH	FWD L2H3外廓。	READY
33278_l3h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	HIGH	FWD L3H2外廓。	READY
33278_l3h3	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	HIGH	FWD L3H3外廓。	READY
33279_l1h1	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	HIGH	FWD L1H1外廓。	READY
33279_l1h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	HIGH	FWD L1H2外廓。	READY
33279_l2h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	HIGH	FWD L2H2外廓。	READY
33279_l2h3	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	HIGH	FWD L2H3外廓。	READY
33279_l3h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	HIGH	FWD L3H2外廓。	READY
33279_l3h3	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	HIGH	FWD L3H3外廓。	READY
33280_l3h2_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	HIGH	RWD L3H2单后轮外廓。	READY
33280_l3h2_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	HIGH	RWD L3H2双后轮外廓。	READY
33280_l3h3_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	HIGH	RWD L3H3双后轮外廓。	READY
33280_l4h2_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	HIGH	RWD L4H2单后轮外廓。	READY
33280_l4h2_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	HIGH	RWD L4H2双后轮外廓。	READY
33280_l4h3_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	HIGH	RWD L4H3单后轮外廓。	READY
33280_l4h3_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	HIGH	RWD L4H3双后轮外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	5048	2070	2303	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	5048	2070	2496	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	5548	2070	2499	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	5548	2070	2749	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	6198	2070	2488	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	6198	2070	2744	Renault UK Master official press kit January 2018, Master Panel FWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	6198	2070	2527	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	6198	2070	2549	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	6198	2070	2815	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	6848	2070	2527	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	6848	2070	2557	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	6848	2070	2786	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	6848	2070	2808	Renault UK Master official press kit January 2018, Master Panel RWD dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
```

## 下一步优先处理

闭合 33281 的 2019–2024 RWD L3/L4、H2/H3 与 SRW/DRW 外廓；完成后 `PENDING=0`，下一轮直接进行机械收尾并输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
## 更新点

* 已闭合最后一个 PENDING：Ktype `33281`。
* `33281` 按 2019 改款前后、L3/L4、H2/H3、SRW/DRW 外廓拆分；改款后官方尺寸图确认车长为 `6225/6875 mm`、车身宽度为 `2070 mm`，并分别列出 H2/H3 高度及单后轮、双后轮配置。([雷诺新闻][1])
* 已完成机械检查：映射表 10 列、尺寸组表 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；全部引用闭合；无孤立尺寸组；三维、来源和 URL 均非空。
* 已创建两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：154
* PENDING 映射行：0
* DIMENSION_GROUP：85
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33132	33132	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33133	33133	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33134	33134	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33135	33135	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33149	33149	SUV	ix35 LM	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
33152	33152	Van	H-1 TQ	TQ		EU-HYUNDAI-H-1-TQ-VAN-01	HIGH		READY
33153	33153	Van	H-1 TQ	TQ		EU-HYUNDAI-H-1-TQ-VAN-01	HIGH		READY
33163	33163	Convertible	F430	F131	2	EU-FERRARI-F430-F131-CONVERTIBLE-2D-01	HIGH		READY
33164	33164	Coupe	F430	F131	2	EU-FERRARI-F430-F131-COUPE-2D-01	HIGH		READY
33165	33165	Coupe	F430	F131	2	EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	HIGH		READY
33176	33176	Wagon	i30 FD	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
33191	33191	Sedan	Insignia A facelift	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH		READY
33192	33192	Hatchback	SX4 S-Cross I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH		READY
33193_prefl	33193	Convertible	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-PREFL-01	HIGH	2012改款前敞篷外廓。	READY
33193_facelift	33193	Convertible	G-Class W463 facelift	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-01	HIGH	2012改款后敞篷外廓。	READY
33195	33195	Hatchback	Modus I	J77	5	EU-RENAULT-MODUS-I-HATCHBACK-5D-01	HIGH	生产期早于Grand Modus，闭合为标准Modus外廓。	READY
33203	33203	Coupe	Integra III	DC2	3	EU-HONDA-INTEGRA-III-DC2-COUPE-3D-01	HIGH	三门Liftback Coupe外廓。	READY
33209_3dr	33209	SUV	Pajero IV	V80	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	短轴三门分支。	READY
33209_5dr	33209	SUV	Pajero IV	V90	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	长轴五门分支。	READY
33211	33211	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	HIGH		READY
33213	33213	Convertible	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	HIGH		READY
33230_prefl	33230	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门厢式版改款前外廓。	READY
33230_facelift	33230	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门厢式版改款后外廓。	READY
33231_prefl	33231	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门厢式版改款前外廓。	READY
33231_facelift	33231	Van	207 I	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门厢式版改款后外廓。	READY
33243	33243	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33244	33244	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33245	33245	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
33246	33246	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	HIGH		READY
33247	33247	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33248	33248	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33249	33249	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33250	33250	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH		READY
33251	33251	Hatchback	A3 II facelift	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH		READY
33252	33252	Hatchback	A3 II facelift	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH		READY
33258	33258	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
33259_3dr	33259	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33259_5dr	33259	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33260_3dr	33260	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33260_5dr	33260	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33261_3dr	33261	Hatchback	207 I facelift	WC	3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门分支。	READY
33261_5dr	33261	Hatchback	207 I facelift	WA	5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门分支。	READY
33262	33262	Convertible	207 CC facelift	WD	2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH		READY
33263	33263	Convertible	207 CC facelift	WD	2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH		READY
33264	33264	Wagon	207 SW I	WK	5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
33265	33265	Wagon	207 SW I	WK	5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
33266	33266	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH		READY
33267	33267	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33269	33269	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33270	33270	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33271	33271	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
33272	33272	Wagon	308 SW I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
33273	33273	Wagon	308 SW I	T7	5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH		READY
33274_l1h1	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L1H1-01	HIGH	L1H1客车分支。	READY
33274_l2h2	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L2H2-01	HIGH	L2H2客车分支。	READY
33274_l3h2	33274	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L3H2-01	HIGH	L3H2客车分支。	READY
33275_l1h1	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	HIGH	L1H1厢式车分支。	READY
33275_l1h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	HIGH	L1H2厢式车分支。	READY
33275_l2h1	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	HIGH	L2H1厢式车分支。	READY
33275_l2h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	HIGH	L2H2厢式车分支。	READY
33275_l3h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	HIGH	L3H2厢式车分支。	READY
33275_l3h3	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	HIGH	L3H3厢式车分支。	READY
33275_l4h2	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	HIGH	L4H2厢式车分支。	READY
33275_l4h3	33275	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	HIGH	L4H3厢式车分支。	READY
33276_l1	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	HIGH	L1底盘驾驶室分支。	READY
33276_l2	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	HIGH	L2底盘驾驶室分支。	READY
33276_l3	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	HIGH	L3底盘驾驶室分支。	READY
33276_l4	33276	Chassis Cab	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	HIGH	L4底盘驾驶室分支。	READY
33277_mpv	33277	MPV	Kangoo II			EU-RENAULT-KANGOO-II-MPV-5D-01	MEDIUM	乘用MPV分支。	READY
33277_van	33277	Van	Kangoo II			EU-RENAULT-KANGOO-II-VAN-01	MEDIUM	厢式车分支。	READY
33278_l1h1	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	HIGH	FWD L1H1外廓。	READY
33278_l1h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	HIGH	FWD L1H2外廓。	READY
33278_l2h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	HIGH	FWD L2H2外廓。	READY
33278_l2h3	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	HIGH	FWD L2H3外廓。	READY
33278_l3h2	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	HIGH	FWD L3H2外廓。	READY
33278_l3h3	33278	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	HIGH	FWD L3H3外廓。	READY
33279_l1h1	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	HIGH	FWD L1H1外廓。	READY
33279_l1h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	HIGH	FWD L1H2外廓。	READY
33279_l2h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	HIGH	FWD L2H2外廓。	READY
33279_l2h3	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	HIGH	FWD L2H3外廓。	READY
33279_l3h2	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	HIGH	FWD L3H2外廓。	READY
33279_l3h3	33279	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	HIGH	FWD L3H3外廓。	READY
33280_l3h2_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	HIGH	RWD L3H2单后轮外廓。	READY
33280_l3h2_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	HIGH	RWD L3H2双后轮外廓。	READY
33280_l3h3_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	HIGH	RWD L3H3双后轮外廓。	READY
33280_l4h2_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	HIGH	RWD L4H2单后轮外廓。	READY
33280_l4h2_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	HIGH	RWD L4H2双后轮外廓。	READY
33280_l4h3_srw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	HIGH	RWD L4H3单后轮外廓。	READY
33280_l4h3_drw	33280	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	HIGH	RWD L4H3双后轮外廓。	READY
33281_l3h2_srw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	HIGH	2019改款前RWD L3H2单后轮外廓。	READY
33281_l3h2_drw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	HIGH	2019改款前RWD L3H2双后轮外廓。	READY
33281_l3h3_drw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	HIGH	2019改款前RWD L3H3双后轮外廓。	READY
33281_l4h2_srw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	HIGH	2019改款前RWD L4H2单后轮外廓。	READY
33281_l4h2_drw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	HIGH	2019改款前RWD L4H2双后轮外廓。	READY
33281_l4h3_srw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	HIGH	2019改款前RWD L4H3单后轮外廓。	READY
33281_l4h3_drw_prefl	33281	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	HIGH	2019改款前RWD L4H3双后轮外廓。	READY
33281_l3h2_srw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-FACELIFT-01	HIGH	2019改款后RWD L3H2单后轮外廓。	READY
33281_l3h2_drw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-FACELIFT-01	HIGH	2019改款后RWD L3H2双后轮外廓。	READY
33281_l3h3_srw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-SRW-FACELIFT-01	HIGH	2019改款后RWD L3H3单后轮外廓。	READY
33281_l3h3_drw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-FACELIFT-01	HIGH	2019改款后RWD L3H3双后轮外廓。	READY
33281_l4h2_srw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-FACELIFT-01	HIGH	2019改款后RWD L4H2单后轮外廓。	READY
33281_l4h2_drw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-FACELIFT-01	HIGH	2019改款后RWD L4H2双后轮外廓。	READY
33281_l4h3_srw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-FACELIFT-01	HIGH	2019改款后RWD L4H3单后轮外廓。	READY
33281_l4h3_drw_facelift	33281	Van	Master III facelift	X62		EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-FACELIFT-01	HIGH	2019改款后RWD L4H3双后轮外廓。	READY
33298	33298	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33299	33299	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33300	33300	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33301	33301	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33302	33302	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
33303	33303	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33304	33304	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33305	33305	Hatchback	A1 I	8X1	3	EU-AUDI-A1-8X1-HATCHBACK-3D-01	HIGH		READY
33306_prefl	33306	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33306_facelift	33306	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
33307_prefl	33307	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33307_facelift	33307	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	MEDIUM	2014改款后外廓。	READY
33308_prefl	33308	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33308_facelift	33308	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
33309_prefl	33309	SUV	Touareg II pre-facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	2014改款前外廓。	READY
33309_facelift	33309	SUV	Touareg II facelift	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	2014改款后外廓。	READY
33311	33311	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33312	33312	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33313	33313	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33314	33314	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33315	33315	Hatchback	Fabia II facelift	5J2	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH		READY
33316	33316	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33317	33317	Wagon	Fabia II Combi facelift	5J5	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH		READY
33320	33320	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33321	33321	MPV	Roomster I facelift	5J	5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH		READY
33322	33322	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH		READY
33323	33323	Van	C2 I	JM	3	EU-CITROEN-C2-I-HATCHBACK-3D-01	MEDIUM	三门厢式版与乘用车外廓一致。	READY
33324	33324	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33325	33325	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33326	33326	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33327	33327	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33328	33328	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33329	33329	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33330	33330	Wagon	Ibiza IV ST	6J8	5	EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	HIGH		READY
33331	33331	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
33332	33332	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH		READY
33333	33333	Hatchback	Fiesta VII	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	当前Ktype未区分三门/五门，外廓尺寸组一致。	READY
33334	33334	Hatchback	Fiesta VII	CB1		EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	当前Ktype未区分三门/五门，外廓尺寸组一致。	READY
33335	33335	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33336	33336	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33337	33337	Van	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	HIGH	三门厢式版与乘用车外廓一致。	READY
33338	33338	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33339	33339	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33340	33340	SUV	Kuga I	C394	5	EU-FORD-KUGA-I-C394-SUV-5D-01	HIGH		READY
33341	33341	Van	C-Crosser I	CW0	5	EU-CITROEN-C-CROSSER-I-SUV-5D-01	MEDIUM	商用厢式版与SUV外廓一致。	READY
33342	33342	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
33343	33343	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
33344	33344	Wagon	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
33345	33345	Wagon	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
33346	33346	Hatchback	Focus II facelift	DA3		EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	当前Ktype未区分三门/五门，复用已闭合外廓组。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4501-4600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-IX35-LM-SUV-5D-01	4410	1820	1660	AutoData1 Hyundai ix35 2.0 CVVT specifications	https://www.autodata1.com/en/car/hyundai/ix35/ix35-20-cvvt-163-hp
EU-HYUNDAI-H-1-TQ-VAN-01	5125	1920	1925	Hyundai H-1 (Grand Starex) 2009 Owner's Manual	https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2009-owner-s-manual-rhd-uk-australia/?srch=dimensions
EU-FERRARI-F430-F131-CONVERTIBLE-2D-01	4511	1923	1234	Ferrari F430 Spider official model page	https://www.ferrari.com/en-EN/auto/f430-spider
EU-FERRARI-F430-F131-COUPE-2D-01	4511	1923	1214	Ferrari F430 official model page	https://www.ferrari.com/en-EN/auto/f430
EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	4512	1923	1199	Ferrari 430 Scuderia official model page	https://www.ferrari.com/en-EN/auto/430-scuderia
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565	Hyundai Heritage i30 FD/CW	https://www.hyundai.com/kr/ko/brand/brandstory/heritage/2000-i30-fd-cw
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	Vauxhall Insignia official specification guide June 2013	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/insignia-a/Insignia_Spec_PG_12_June_2013.pdf
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575	Auto-Data Suzuki SX4 S-Cross model specifications	https://www.auto-data.net/en/suzuki-sx4-model-1911
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-PREFL-01	4257	1760	1941	Mercedes-Benz Public Archive G 500 short wheelbase 2008–2012	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-500-kurzer-Radstand-2008---2012.xhtml?oid=191039063
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-01	4257	1760	1951	Auto-Data Mercedes-Benz G-Class Cabriolet W463 facelift 2012 G 500	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w463-facelift-2012-g-500-v8-388hp-4matic-7g-tronic-plus-42490
EU-RENAULT-MODUS-I-HATCHBACK-5D-01	3792	1695	1589	Automobile-Catalog 2004 Renault Modus 1.6 16V specifications	https://www.automobile-catalog.com/car/2004/2951165/renault_modus_1_6_16v_88.html
EU-HONDA-INTEGRA-III-DC2-COUPE-3D-01	4380	1710	1335	Auto-Data Honda Integra III DC2; CarsGuide 2000 Honda Integra dimensions	https://www.auto-data.net/en/honda-integra-iii-dc2-generation-2579;https://www.carsguide.com.au/honda/integra/car-dimensions/2000
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV generation specifications	https://www.auto-data.net/en/mitsubishi-pajero-iv-generation-3400
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870	Auto-Data Mitsubishi Pajero IV generation specifications	https://www.auto-data.net/en/mitsubishi-pajero-iv-generation-3400
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525	Auto-Data Honda Jazz model specifications	https://www.auto-data.net/en/honda-jazz-model-1289
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246	C6 Registry Corvette Convertible specifications	https://www.c6registry.com/January04/Convertible/specifications.htm
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 model specifications	https://www.auto-data.net/en/peugeot-207-model-572
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 model specifications	https://www.auto-data.net/en/peugeot-207-model-572
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498	Auto-Data Skoda Fabia II specifications	https://www.auto-data.net/en/skoda-fabia-ii-generation-3089
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498	Auto-Data Skoda Fabia II Combi facelift specifications	https://www.auto-data.net/en/skoda-fabia-ii-combi-facelift-2010-1.2-mpi-70hp-20327
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift generation	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-generation-3094
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift generation	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-generation-3094
EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	4214	1684	1607	Auto-Data Skoda Roomster facelift specifications	https://www.auto-data.net/en/skoda-roomster-facelift-2010-1.4-86hp-19232
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data Seat Altea facelift 2009 specifications	https://www.auto-data.net/en/seat-altea-facelift-2009-generation-4202
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	AutoData1 Seat Leon II facelift specifications	https://www.autodata1.com/en/car/seat/leon/leon-ii-1p-facelift-2009-fr-20-tdi-cr-170-hp-dpf-dsg
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	auto motor und sport Audi A3 8P/8PA technical data	https://www.auto-motor-und-sport.de/marken-modelle/audi/a3/8p-8pa/technische-daten/
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423	auto motor und sport Audi A3 8P/8PA technical data	https://www.auto-motor-und-sport.de/marken-modelle/audi/a3/8p-8pa/technische-daten/
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801	Auto-Data Citroen Berlingo model specifications	https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 model specifications	https://www.auto-data.net/en/peugeot-207-model-572
EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	4044	1748	1393	Auto-Data Peugeot 207 CC facelift generation	https://www.auto-data.net/en/peugeot-207-cc-facelift-2009-generation-6456
EU-PEUGEOT-207-I-SW-WAGON-5D-01	4156	1748	1527	Auto-Data Peugeot 207 SW generation	https://www.auto-data.net/en/peugeot-207-sw-generation-6453
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628	Auto-Data Peugeot 3008 model specifications	https://www.auto-data.net/en/peugeot-3008-model-577
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498	Auto-Data Peugeot 308 model specifications	https://www.auto-data.net/en/peugeot-308-model-573
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564	Auto-Data Peugeot 308 model specifications	https://www.auto-data.net/en/peugeot-308-model-573
EU-PEUGEOT-BOXER-II-BUS-L1H1-01	4963	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-BUS-L2H2-01	5413	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-BUS-L3H2-01	5998	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270	Peugeot Boxer 2008 Owner Manual technical data	https://www.carmanualsonline.info/peugeot-boxer-2008-owner-s-manual/?srch=technical+data
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data Renault Kangoo model specifications	https://www.auto-data.net/en/renault-kangoo-model-1045
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844	Auto-Data Renault Kangoo model specifications	https://www.auto-data.net/en/renault-kangoo-model-1045
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H1-PREFL-01	5048	2070	2303	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L1H2-PREFL-01	5048	2070	2496	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H2-PREFL-01	5548	2070	2499	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L2H3-PREFL-01	5548	2070	2749	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H2-PREFL-01	6198	2070	2488	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-FWD-L3H3-PREFL-01	6198	2070	2744	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-PREFL-01	6198	2070	2527	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-PREFL-01	6198	2070	2549	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-PREFL-01	6198	2070	2815	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-PREFL-01	6848	2070	2527	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-PREFL-01	6848	2070	2557	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-PREFL-01	6848	2070	2786	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-PREFL-01	6848	2070	2808	Renault UK Master official press kit January 2018, panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/14002-RenaultMasterPressKitJanuary2018.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-SRW-FACELIFT-01	6225	2070	2549	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H2-DRW-FACELIFT-01	6225	2070	2549	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-SRW-FACELIFT-01	6225	2070	2815	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L3H3-DRW-FACELIFT-01	6225	2070	2815	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-SRW-FACELIFT-01	6875	2070	2557	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H2-DRW-FACELIFT-01	6875	2070	2557	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-SRW-FACELIFT-01	6875	2070	2808	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-X62-VAN-RWD-L4H3-DRW-FACELIFT-01	6875	2070	2808	Renault UK Master official brochure April 2022, rear-wheel-drive panel van dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data Alfa Romeo Giulietta Type 940 specifications	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-facelift-2016-1.750-tbi-240hp-tct-22851
EU-AUDI-A1-8X1-HATCHBACK-3D-01	3954	1740	1416	Audi UK A1 1.4 TFSI official technical data	https://press.audi.co.uk/assets/documents/original/9527-AudiUK00000111A114TFSIStronic122g.pdf
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1732	Volkswagen UK Touareg official brochure February 2011	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touareg/touareg-nf/vw-touareg-nf-brochure-feb-2011.pdf
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1732	Volkswagen UK Touareg official brochure December 2015	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touareg/touareg-fl/vw-touareg-fl-brochure-dec-2015.pdf
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510	Auto-Data Skoda Superb II Combi specifications	https://www.auto-data.net/en/skoda-superb-ii-combi-2.0-tdi-cr-140hp-dsg-19320
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474	Auto-Data Citroen C2 model specifications	https://www.auto-data.net/en/citroen-c2-model-1695
EU-SEAT-IBIZA-IV-ST-6J8-WAGON-5D-01	4236	1693	1445	SEAT Ibiza ST technical specifications	https://www.motorshow.me/uploadImages/GalleryDocs/Doc6003.pdf
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588	Auto-Data Ford C-Max I facelift specifications	https://www.auto-data.net/en/ford-c-max-facelift-2007-generation-1012
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481	Auto-Data Ford Fiesta VII specifications	https://www.auto-data.net/en/ford-fiesta-vii-generation-1017
EU-FORD-KUGA-I-C394-SUV-5D-01	4443	1842	1710	Auto-Data Ford Kuga I specifications	https://www.auto-data.net/en/ford-kuga-i-generation-1019
EU-CITROEN-C-CROSSER-I-SUV-5D-01	4645	1805	1715	Auto-Data Citroen C-Crosser specifications	https://www.auto-data.net/en/citroen-c-crosser-generation-3765
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500	Auto-Data Ford Focus II facelift specifications	https://www.auto-data.net/en/ford-focus-ii-hatchback-facelift-2008-generation-997
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503	Auto-Data Ford Focus II facelift specifications	https://www.auto-data.net/en/ford-focus-ii-hatchback-facelift-2008-generation-997
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4501-4600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf "https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（7415 行）
- 累计尺寸组：dimension_groups_final.tsv（2895 行）

