# 任务：all 第 12501-12600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0126__3b9c53c3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 12501-12600 行

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
all 第 12501-12600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12501-12600_ktype_dimension_mapping_final.tsv
- all_12501-12600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALPINA-B3-E92-COUPE-2D-GT3-01	4668	1782	1405
EU-ALPINA-B3-S-BITURBO-E91-TOURING-ALLRAD-01	4541	1817	1465
EU-ALPINA-B3-S-BITURBO-E92-COUPE-01	4623	1782	1395
EU-ALPINA-B3-S-E90-SEDAN-AWD-01	4545	1817	1437
EU-ALPINA-B3-S-E90-SEDAN-RWD-01	4545	1817	1422
EU-ALPINA-B3-S-E91-WAGON-RWD-01	4541	1817	1450
EU-ALPINA-B3S-E92-COUPE-AWD-01	4622	1782	1410
EU-ALPINA-B3S-E93-CONVERTIBLE-01	4623	1782	1385
EU-AUDI-A3-8L-HATCHBACK-3D-01	4152	1735	1427
EU-AUDI-A4-B6-8E2-SEDAN-4D-01	4548	1772	1428
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408
EU-BMW-3-E46-COUPE-2D-01	4488	1757	1369
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415
EU-BMW-3-E46-TOURING-5D-01	4478	1739	1409
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776
EU-CADILLAC-CTS-II-COUPE-01	4788	1882	1422
EU-CADILLAC-CTS-II-COUPE-V-01	4788	1882	1422
EU-CADILLAC-CTS-II-SEDAN-01	4867	1842	1473
EU-CADILLAC-CTS-II-SPORT-WAGON-01	4878	1842	1463
EU-CADILLAC-CTS-II-WAGON-01	4878	1842	1473
EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	5113	1850	1730
EU-CHRYSLER-NEON-PL-SEDAN-4D-01	4364	1714	1369
EU-CHRYSLER-STRATUS-JA-SEDAN-01	4746	1822	1374
EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	4902	1780	1392
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	5302	2125	1990
EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	4552	1960	1990
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
EU-HONDA-JAZZ-III-GE-HYBRID-HATCHBACK-5D-01	3900	1695	1525
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4821	1943	1760
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4821	1938	1763
EU-LEXUS-IS-II-ALE20-FACELIFT-SEDAN-4D-01	4585	1800	1440
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	4225	1690	1940
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	4275	1760	1941
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	4230	1760	1931
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-03	4680	1760	1936
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510
EU-OPEL-ASTRA-G-COUPE-2D-01	4267	1709	1390
EU-OPEL-ASTRA-G-HATCHBACK-3D-01	4110	1709	1425
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425
EU-OPEL-ASTRA-G-SEDAN-4D-01	4252	1709	1425
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-996-CARRERA-COUPE-01	4430	1765	1305
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415
EU-SUBARU-IMPREZA-I-GFC-COUPE-2D-01	4350	1690	1410
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420
EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	4350	1690	1435
EU-SUZUKI-WAGON-R-EM-MPV-5D-01	3410	1575	1700
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-02	4500	1710	1400
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395
EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	4765	1785	1430
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-FACELIFT-01	4850	1825	1480
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-PREFL-01	4825	1825	1480
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	4200	1710	1460
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
EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	4100	1690	1380
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	4290	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	4270	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	4295	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	4340	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	4320	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	4320	1690	1445
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	3950	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	3945	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	3885	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	3950	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	3945	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	3885	1695	1510
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-3D-01	3785	1695	1530
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-5D-01	3785	1695	1530
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	4129	1721	1498
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	4081	1725	1500
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459
EU-VW-PASSAT-B5-3B5-WAGON-5D-01	4670	1740	1500
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Passat b5 variant	2	Kombi	Frontantrieb	Benzin	88	120	Apr 2000	Nov 2000	2024-03-01	16301
VW	Passat b5 variant	2.0 4motion	Kombi	Allrad	Benzin	88	120	Apr 2000	Nov 2000	2024-03-01	16302
Ford	Transit	2.5 TD	Bus	Heckantrieb	Diesel	55	75	Aug 1994	Jun 2000	2024-03-01	16303
Ford	Transit	2.5 TD	Kasten	Heckantrieb	Diesel	55	75	Jun 1994	Mar 2000	2024-03-01	16304
VW	Passat b5	1.8	Stufenheck	Frontantrieb	Benzin	85	115	Jan 1997	Nov 2000	2024-03-01	16306
VW	Passat b5	2.8 V6	Stufenheck	Frontantrieb	Benzin	132	180	May 1997	Sep 1999	2024-03-01	16307
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	165	224	Oct 2001	May 2003	2024-03-01	16314
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	85	116	Sep 2001	Mar 2003	2024-03-01	16315
Subaru	Impreza	2.0 WRX STI AWD	Stufenheck	Allrad	Benzin	195	265	Nov 2001	Jul 2005	2024-03-01	16316
Honda	Jazz ii	1.3 Idsi	Schrägheck	Frontantrieb	Benzin	61	83	Mar 2002	Jul 2008	2024-03-01	16317
Audi	A4 b6	2.4	Stufenheck	Frontantrieb	Benzin	125	170	Sep 2001	Dec 2004	2024-03-01	16318
Audi	A4 b6 avant	2.4	Kombi	Frontantrieb	Benzin	125	170	Sep 2001	Dec 2004	2024-03-01	16319
Lexus	Is i	300	Stufenheck	Heckantrieb	Benzin	157	213	Sep 2001	Jul 2005	2024-03-01	16320
Lexus	Is sportcross	300	Kombi	Heckantrieb	Benzin	157	213	Oct 2001	Oct 2005	2024-03-01	16321
Audi	A4 b6 avant	2.5 TDI Quattro	Kombi	Allrad	Diesel	132	180	Sep 2001	Dec 2004	2024-03-01	16322
Audi	A4 b6	2.4	Cabriolet	Frontantrieb	Benzin	125	170	Apr 2002	Dec 2005	2024-03-01	16323
Audi	A4 b6	3	Cabriolet	Frontantrieb	Benzin	162	220	Apr 2002	Dec 2005	2024-03-01	16324
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	85	115	Feb 2002	Feb 2005	2024-03-01	16325
BMW	3	318 I	Kombi	Heckantrieb	Benzin	105	143	Sep 2001	Jul 2005	2024-03-01	16326
BMW	3	318 CI	Cabriolet	Heckantrieb	Benzin	105	143	Sep 2001	Dec 2007	2024-03-01	16327
BMW	X5	4.6 IS	SUV	Allrad	Benzin	255	347	Oct 2001	Sep 2003	2024-03-01	16328
Chevrolet	Trans sport	3.4 V6 AWD	Großraumlimousine	Allrad	Benzin	138	188	Oct 2001	Sep 2005	2024-03-01	16329
Citroën	C3 i	1.1 I	Schrägheck	Frontantrieb	Benzin	44	60	Feb 2002	Dec 2009	2024-07-01	16330
Citroën	C3 i	1.4 HDI	Schrägheck	Frontantrieb	Diesel	50	68	Feb 2002	Dec 2009	2024-07-01	16331
VW	Polo	1.2 12V	Schrägheck	Frontantrieb	Benzin	47	64	Oct 2001	Jul 2007	2024-03-01	16332
VW	Polo	1.9 SDI	Schrägheck	Frontantrieb	Diesel	47	64	Oct 2001	Nov 2009	2024-03-01	16333
Citroën	C3 i	1.4 I Bivalent	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	54	73	Feb 2002	Dec 2009	2024-07-01	16334
Citroën	C3 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	80	109	Feb 2002	Aug 2010	2024-03-01	16335
Citroën	C3 i	1.4 16V HDI	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2002	Jun 2008	2024-07-01	16336
Ford	Fiesta v	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Nov 2001	Jun 2008	2024-03-01	16337
Ford	Fiesta v	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Nov 2001	Jun 2008	2024-03-01	16338
Audi	A4 b6 avant	2.5 TDI	Kombi	Frontantrieb	Diesel	114	155	Sep 2001	Jul 2002	2024-03-01	16339
VW	New beetle	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Nov 2001	Sep 2010	2024-03-01	16340
Rover	75	2.5 V6	Stufenheck	Frontantrieb	Benzin	130	177	Oct 2001	May 2005	2024-03-01	16341
MG	Zt- t	160	Kombi	Frontantrieb	Benzin	118	160	Oct 2001	Jul 2005	2025-12-01	16344
MG	Zt- t	190	Kombi	Frontantrieb	Benzin	140	190	Oct 2001	Jul 2005	2025-12-01	16345
VW	Passat b5.5	2	Stufenheck	Frontantrieb	Benzin	96	130	Nov 2001	May 2005	2024-03-01	16346
VW	Passat b5.5 variant	2	Kombi	Frontantrieb	Benzin	96	130	Nov 2001	May 2005	2024-03-01	16347
VW	Golf iv variant	2.0 Bi-fuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	85	116	Feb 2002	Jun 2006	2024-03-01	16348
VW	Bora	1.9 TDI	Kombi	Frontantrieb	Diesel	110	150	May 2001	May 2005	2024-03-01	16349
VW	Bora	1.9 TDI 4motion	Kombi	Allrad	Diesel	110	150	May 2001	May 2005	2024-03-01	16350
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	184	250	Sep 2001	Dec 2009	2024-03-01	16351
Volvo	S60 i	2.0 T	Stufenheck	Frontantrieb	Benzin	132	180	Jul 2000	Apr 2010	2024-03-01	16352
Lamborghini	Murciélago	6.2	Coupe	Allrad	Benzin	426	579	Nov 2001	Dec 2006	2024-03-01	16353
Alpina	B3	3.3 Allrad	Stufenheck	Allrad	Benzin	206	280	Nov 2001	Jan 2005	2024-03-01	16354
Alpina	B3	3.3 Allrad	Kombi	Allrad	Benzin	206	280	Nov 2001	Jan 2005	2024-03-01	16355
KIA	Carnival ii	2.5 V6	Großraumlimousine	Frontantrieb	Benzin	110	150	Oct 2001	Jun 2006	2024-03-01	16356
KIA	Carnival ii	2.9 Crdi	Großraumlimousine	Frontantrieb	Diesel	106	144	Oct 2001	Jun 2006	2024-03-01	16357
Suzuki	Wagon r+	1.3 4WD	Schrägheck	Allrad	Benzin	56	76	Oct 2001	-	2024-03-01	16358
Chrysler	Pt cruiser	1.6	Kombi	Frontantrieb	Benzin	85	116	Nov 2001	Dec 2010	2024-03-01	16359
Jeep	Grand cherokee iv	6.4 Srt8 4X4	SUV	Allrad	Benzin	344	468	Mar 2011	-	2024-03-01	16360
Ford	Fiesta v	1.6 16V	Schrägheck	Frontantrieb	Benzin	74	100	Nov 2001	Jun 2008	2024-03-01	16361
Toyota	Camry	2.4	Stufenheck	Frontantrieb	Benzin	112	152	Nov 2001	Nov 2006	2024-03-01	16362
Toyota	Camry	3	Stufenheck	Frontantrieb	Benzin	137	186	Aug 2001	Nov 2006	2024-03-01	16363
Toyota	Yaris	1.4 D-4d	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2001	Sep 2005	2024-03-01	16364
Toyota	Yaris	1.4 D-4d	Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2000	Sep 2005	2024-03-01	16365
Chrysler	Neon	1.6	Stufenheck	Frontantrieb	Benzin	85	116	Nov 2001	Dec 2006	2024-03-01	16366
Hyundai	Sonata iv	2.0 16V	Stufenheck	Frontantrieb	Benzin	96	131	Oct 2001	Nov 2004	2024-03-01	16367
Hyundai	Sonata iv	2.7 V6	Stufenheck	Frontantrieb	Benzin	127	173	Oct 2001	Nov 2004	2024-03-01	16368
Hyundai	ii	2	Coupe	Frontantrieb	Benzin	102	139	Mar 2002	Aug 2009	2024-03-01	16369
Hyundai	ii	2.7 V6	Coupe	Frontantrieb	Benzin	123	167	Mar 2002	Aug 2009	2024-03-01	16370
Opel	Astra g	2.0 OPC	Cabriolet	Frontantrieb	Benzin	141	192	Mar 2002	Oct 2005	2024-03-01	16371
Toyota	Corolla	1.4 Vvt-i	Schrägheck	Frontantrieb	Benzin	71	97	Nov 2001	Feb 2007	2024-03-01	16373
Toyota	Corolla	1.6 Vvt-i	Schrägheck	Frontantrieb	Benzin	81	110	Jan 2002	Dec 2006	2024-03-01	16374
Toyota	Corolla	1.8 Vvtl-i TS	Schrägheck	Frontantrieb	Benzin	141	192	Nov 2001	Feb 2007	2024-03-01	16375
Toyota	Corolla	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	66	90	Jan 2002	Dec 2006	2024-03-01	16376
Toyota	Corolla	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	81	110	Jan 2002	Dec 2006	2024-03-01	16377
Toyota	Corolla	1.4 Vvt-i	Kombi	Frontantrieb	Benzin	71	97	Jan 2002	Feb 2007	2024-03-01	16378
Toyota	Corolla	1.6 Vvt-i	Kombi	Frontantrieb	Benzin	81	110	Jan 2002	Aug 2007	2024-03-01	16379
Toyota	Corolla	2.0 D-4d	Kombi	Frontantrieb	Diesel	66	90	Jan 2002	Feb 2007	2024-03-01	16380
Toyota	Corolla	1.4 Vvt-i	Stufenheck	Frontantrieb	Benzin	71	97	Oct 2001	Oct 2006	2024-03-01	16381
Toyota	Corolla	1.6 Vvt-i	Stufenheck	Frontantrieb	Benzin	81	110	Oct 2001	Mar 2008	2024-03-01	16382
Toyota	Corolla	1.6 Vvt-i	Großraumlimousine	Frontantrieb	Benzin	81	110	Aug 2001	May 2004	2024-03-01	16384
Toyota	Corolla	2.0 D-4d	Großraumlimousine	Frontantrieb	Diesel	66	90	Jan 2002	May 2004	2024-03-01	16385
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	107	145	Jun 1994	Aug 1999	2024-03-01	16386
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	May 1994	Aug 1999	2024-03-01	16387
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	109	148	Apr 1996	Aug 1999	2024-03-01	16388
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	112	152	Apr 1996	Aug 1999	2024-03-01	16389
Plymouth	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	May 1994	Aug 1999	2024-03-01	16390
Plymouth	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	107	145	Jun 1994	Aug 1999	2024-03-01	16391
Plymouth	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	112	152	Apr 1996	Aug 1999	2024-03-01	16392
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Aug 1999	-	2024-03-01	16393
Dodge	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	112	152	Aug 1999	Dec 2002	2024-03-01	16394
Plymouth	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Aug 1999	-	2024-03-01	16395
Plymouth	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	112	152	Sep 1999	Sep 2005	2024-03-01	16396
Chrysler	Stratus	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Dec 1995	Apr 2001	2024-03-01	16397
Chrysler	Stratus	2.4 16V	Stufenheck	Frontantrieb	Benzin	112	152	Dec 1995	Apr 2001	2024-03-01	16398
Chrysler	Stratus	2.5 V6	Stufenheck	Frontantrieb	Benzin	125	170	Dec 1995	Apr 2001	2024-03-01	16399
Dodge	Stratus	2.4 16 V	Stufenheck	Frontantrieb	Benzin	103	140	Dec 1995	Apr 2001	2024-03-01	16400
Dodge	Stratus	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Dec 1995	Apr 2001	2024-03-01	16401
Dodge	Stratus	2.4 16V	Stufenheck	Frontantrieb	Benzin	112	152	Dec 1995	Apr 2001	2024-03-01	16402
Dodge	Stratus	2.5 V6	Stufenheck	Frontantrieb	Benzin	125	170	Dec 1995	Apr 2001	2024-03-01	16403
Plymouth	Breeze	2.4 16V	Stufenheck	Frontantrieb	Benzin	103	140	Dec 1995	Apr 2001	2024-03-01	16404
Plymouth	Breeze	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Dec 1995	Apr 2001	2024-03-01	16405
Plymouth	Breeze	2.4 16V	Stufenheck	Frontantrieb	Benzin	112	152	Dec 1995	Apr 2001	2024-03-01	16406
Mercedes-benz	G-Klasse	G 270 CDI	Geländewagen geschlossen	Allrad	Diesel	115	156	Oct 2001	Jul 2003	2024-03-01	16407
Porsche	911	3.6	Targa	Heckantrieb	Benzin	235	320	Dec 2001	Aug 2005	2024-03-01	16409
Dodge	Caravan	2.4 I	Großraumlimousine	Frontantrieb	Benzin	111	151	Jan 1995	Mar 2001	2024-03-01	16410
Dodge	Caravan	3	Großraumlimousine	Frontantrieb	Benzin	112	152	Jan 1995	Jun 2000	2024-03-01	16411
Cadillac	Cts	3.2	Stufenheck	Heckantrieb	Benzin	160	218	Mar 2002	Sep 2007	2024-03-01	16413


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖当前批次全部 **100 个输入 Ktype**，形成 **138 条映射行**。
* 已完成 **136 条 READY 映射**，闭合 **74 个尺寸组**：本轮首次创建 52 个，复用跨批次既有组 22 个。
* `16314` 为宽体 Audi S3 8L，外廓为 4159 × 1763 × 1415 mm，未错误复用普通 A3 8L 尺寸组。([汽车数据网][1])
* Transit Bus/Kasten 已按现有 VE6 facelift 的 SWB/LWB 与车顶高度组批量关联；本轮不重复输出其缓存尺寸组。
* Corolla IX Wagon 的直接规格页支持 4375 × 1710 × 1500 mm，已建立独立 Wagon 尺寸组。([汽车数据网][2])
* 剩余 `16354`、`16355`：当前资料能确认 B3 3.3 Allrad 车型存在，但尚未获得可追溯且能同时闭合宽度口径的轿车、旅行车完整三维，暂不猜测复用普通 BMW E46 组。([阿尔皮娜档案][3])

## 当前批次进度

* 输入 Ktype：100
* 已输出映射：138
* READY 映射：136
* PENDING 映射：2
* 已确认尺寸组：74
* 本轮首次创建尺寸组：52
* 复用既有尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16301	16301	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
16302	16302	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
16303_swb_lowroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_swb_midroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_lwb_midroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_lwb_highroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_swb_lowroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_swb_midroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_lwb_midroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_lwb_highroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16306	16306	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
16307	16307	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
16314	16314	Hatchback	S3 8L facelift	8L	3	EU-AUDI-S3-8L-HATCHBACK-3D-FACELIFT-01	HIGH		READY
16315	16315	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
16316_prefl	16316	Sedan	Impreza II	GDB	4	EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-PREFL-01	HIGH	改款前外廓。	READY
16316_facelift	16316	Sedan	Impreza II facelift	GDB	4	EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-FACELIFT-01	HIGH	2002年改款外廓。	READY
16317	16317	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
16318	16318	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH		READY
16319	16319	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16320	16320	Sedan	IS I	XE10	4	EU-LEXUS-IS-I-XE10-SEDAN-4D-01	HIGH		READY
16321	16321	Wagon	IS I SportCross	XE10	5	EU-LEXUS-IS-I-XE10-SPORTCROSS-WAGON-5D-01	HIGH		READY
16322	16322	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16323	16323	Convertible	A4 B6 Cabriolet	8H	2	EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	HIGH		READY
16324	16324	Convertible	A4 B6 Cabriolet	8H	2	EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	HIGH		READY
16325	16325	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
16326	16326	Wagon	3 Series E46 facelift	E46	5	EU-BMW-3-E46-TOURING-5D-01	HIGH		READY
16327	16327	Convertible	3 Series E46 facelift	E46	2	EU-BMW-3-E46-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
16328	16328	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-5D-4-6IS-01	HIGH		READY
16329	16329	MPV	Trans Sport II	U	5	EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	HIGH		READY
16330_prefl	16330	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16330_facelift	16330	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16331_prefl	16331	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16331_facelift	16331	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16332_3dr_prefl	16332	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	三门改款前外廓。	READY
16332_3dr_facelift	16332	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	三门改款外廓。	READY
16332_5dr_prefl	16332	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	五门改款前外廓。	READY
16332_5dr_facelift	16332	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	五门改款外廓。	READY
16333_3dr_prefl	16333	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	三门改款前外廓。	READY
16333_3dr_facelift	16333	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	三门改款外廓。	READY
16333_5dr_prefl	16333	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	五门改款前外廓。	READY
16333_5dr_facelift	16333	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	五门改款外廓。	READY
16334_prefl	16334	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16334_facelift	16334	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16335_prefl	16335	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16335_facelift	16335	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16336_prefl	16336	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16336_facelift	16336	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16337_3dr	16337	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门外廓。	READY
16337_5dr	16337	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门外廓。	READY
16338_3dr	16338	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门外廓。	READY
16338_5dr	16338	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门外廓。	READY
16339	16339	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16340_prefl	16340	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
16340_facelift	16340	Hatchback	New Beetle I facelift	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16341_prefl	16341	Sedan	75	R40	4	EU-ROVER-75-R40-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16341_facelift	16341	Sedan	75 facelift	R40	4	EU-ROVER-75-R40-SEDAN-4D-FACELIFT-01	HIGH	2004年改款外廓。	READY
16344	16344	Wagon	ZT-T		5	EU-MG-ZT-T-WAGON-5D-PREFL-01	HIGH		READY
16345_prefl	16345	Wagon	ZT-T		5	EU-MG-ZT-T-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
16345_facelift	16345	Wagon	ZT-T facelift		5	EU-MG-ZT-T-WAGON-5D-FACELIFT-01	HIGH	2004年改款外廓。	READY
16346	16346	Sedan	Passat B5.5	3B3	4	EU-VW-PASSAT-B5-3B3-SEDAN-FACELIFT-01	HIGH		READY
16347	16347	Wagon	Passat B5.5	3B6	5	EU-VW-PASSAT-B5-3B6-WAGON-FACELIFT-01	HIGH		READY
16348	16348	Wagon	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-WAGON-5D-01	HIGH		READY
16349	16349	Wagon	Bora Variant	1J6	5	EU-VW-BORA-1J6-WAGON-5D-01	HIGH		READY
16350	16350	Wagon	Bora Variant	1J6	5	EU-VW-BORA-1J6-WAGON-5D-01	HIGH		READY
16351	16351	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	MEDIUM	250 hp Aero对应2002–2005外廓；输入结束年月宽于该版本。	READY
16352	16352	Sedan	S60 I	P2	4	EU-VOLVO-S60-I-SEDAN-4D-01	HIGH		READY
16353	16353	Coupe	Murcielago		2	EU-LAMBORGHINI-MURCIELAGO-COUPE-2D-01	HIGH		READY
16354	16354	Sedan	B3 3.3 E46	E46	4		LOW	Allrad轿车外廓与BMW E46基准组是否完全一致尚未闭合。	PENDING: 缺少可追溯的B3 3.3 Allrad轿车完整三维来源
16355	16355	Wagon	B3 3.3 E46	E46	5		LOW	Allrad旅行车外廓与BMW E46基准组是否完全一致尚未闭合。	PENDING: 缺少可追溯的B3 3.3 Allrad旅行车完整三维来源
16356	16356	MPV	Carnival II	GQ	5	EU-KIA-CARNIVAL-II-GQ-MPV-5D-V6-01	HIGH		READY
16357	16357	MPV	Carnival II	GQ	5	EU-KIA-CARNIVAL-II-GQ-MPV-5D-CRDI-01	HIGH		READY
16358	16358	MPV	Wagon R+ II		5	EU-SUZUKI-WAGON-R-II-MPV-5D-4WD-01	HIGH	来源车型分类为五门MPV。	READY
16359	16359	Hatchback	PT Cruiser	PT	5	EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	HIGH	来源车型分类为五门Hatchback。	READY
16360_prefl	16360	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-PREFL-01	HIGH	SRT8改款前外廓。	READY
16360_facelift	16360	SUV	Grand Cherokee IV facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-FACELIFT-01	HIGH	SRT8改款外廓。	READY
16361_3dr_prefl	16361	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16361_3dr_facelift	16361	Hatchback	Fiesta V facelift		3	EU-FORD-FIESTA-V-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款外廓。	READY
16361_5dr_prefl	16361	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16361_5dr_facelift	16361	Hatchback	Fiesta V facelift		5	EU-FORD-FIESTA-V-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款外廓。	READY
16362	16362	Sedan	Camry V	XV30	4	EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	HIGH		READY
16363	16363	Sedan	Camry V	XV30	4	EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	HIGH		READY
16364_3dr_prefl	16364	Hatchback	Yaris I	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16364_3dr_facelift	16364	Hatchback	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款外廓。	READY
16364_5dr_prefl	16364	Hatchback	Yaris I	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16364_5dr_facelift	16364	Hatchback	Yaris I facelift	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款外廓。	READY
16365_prefl	16365	MPV	Yaris Verso	XP20	5	EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-PREFL-01	HIGH	改款前外廓。	READY
16365_facelift	16365	MPV	Yaris Verso facelift	XP20	5	EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-FACELIFT-01	HIGH	2003年改款外廓。	READY
16366	16366	Sedan	Neon II	PL2	4	EU-CHRYSLER-NEON-II-SEDAN-4D-01	HIGH		READY
16367	16367	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
16368	16368	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
16369	16369	Coupe	Coupe II	GK	2	EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	HIGH		READY
16370	16370	Coupe	Coupe II	GK	2	EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	HIGH		READY
16371	16371	Convertible	Astra G		2	EU-OPEL-ASTRA-G-CONVERTIBLE-2D-01	HIGH		READY
16373_3dr	16373	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16373_5dr	16373	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16374_3dr	16374	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16374_5dr	16374	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16375_3dr	16375	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16375_5dr	16375	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16376_3dr	16376	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16376_5dr	16376	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16377_3dr	16377	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16377_5dr	16377	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16378	16378	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16379	16379	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16380	16380	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16381	16381	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	HIGH		READY
16382	16382	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	HIGH		READY
16384	16384	MPV	Corolla Verso I	E120	5	EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	HIGH		READY
16385	16385	MPV	Corolla Verso I	E120	5	EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	HIGH		READY
16386	16386	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16387	16387	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16388	16388	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16389	16389	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16390	16390	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16391	16391	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16392	16392	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16393	16393	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH		READY
16394	16394	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH		READY
16395	16395	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL2外廓。	READY
16396	16396	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL2外廓。	READY
16397	16397	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16398	16398	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16399	16399	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16400	16400	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16401	16401	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16402	16402	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16403	16403	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16404	16404	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16405	16405	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16406	16406	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16407_3dr	16407	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	HIGH	三门短轴外廓。	READY
16407_5dr	16407	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	HIGH	五门长轴外廓。	READY
16409	16409	Targa	911 996 facelift	996	2	EU-PORSCHE-911-996-TARGA-FACELIFT-01	HIGH		READY
16410	16410	MPV	Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH		READY
16411_swb	16411	MPV	Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	短轴外廓。	READY
16411_lwb	16411	MPV	Grand Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	长轴外廓。	READY
16413	16413	Sedan	CTS I		4	EU-CADILLAC-CTS-I-SEDAN-4D-01	MEDIUM	功率标注存在市场换算差异，物理外廓一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-S3-8L-HATCHBACK-3D-FACELIFT-01	4159	1763	1415	Auto-Data Audi S3 (8L facelift 2001) 1.8 T quattro	https://www.auto-data.net/en/audi-s3-8l-facelift-2001-1.8-t-225hp-quattro-4908
EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-PREFL-01	4405	1730	1440	Automobile-Catalog Subaru Impreza 2.0 WRX STi 2001	https://www.automobile-catalog.com/car/2001/3255710/subaru_impreza_2_0_wrx_sti.html
EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-FACELIFT-01	4415	1740	1440	Auto-Data Subaru Impreza II facelift WRX STi	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2002-wrx-sti-2.0-265hp-awd-16082
EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	3830	1675	1525	Honda Jazz 02 press release	https://hondanews.eu/eu/en/media/pressreleases/34284/jazz-02
EU-AUDI-A4-B6-8E5-WAGON-5D-01	4548	1772	1428	Auto-Data Audi A4 Avant (B6 8E) 2.4 V6	https://www.auto-data.net/en/audi-a4-avant-b6-8e-2.4i-v6-30v-170hp-4398
EU-LEXUS-IS-I-XE10-SEDAN-4D-01	4400	1725	1405	Lexus IS 300 and SportCross launch pack 2001	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/141010DM4-IS-300-and-SportCross-launch-pack-2001.pdf
EU-LEXUS-IS-I-XE10-SPORTCROSS-WAGON-5D-01	4505	1725	1430	Lexus IS 300 and SportCross launch pack 2001	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/141010DM4-IS-300-and-SportCross-launch-pack-2001.pdf
EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	4573	1777	1391	Auto-Data Audi A4 Cabriolet (B6 8H) 2.4 V6	https://www.auto-data.net/en/audi-a4-cabriolet-b6-8h-2.4-v6-30v-170hp-26633
EU-BMW-3-E46-CONVERTIBLE-2D-FACELIFT-01	4488	1757	1369	Auto-Data BMW 3 Series Convertible E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-convertible-e46-facelift-2003-318ci-143hp-9964
EU-BMW-X5-E53-SUV-5D-4-6IS-01	4666	1872	1717	Auto-Data BMW X5 (E53) 4.6is	https://www.auto-data.net/en/bmw-x5-e53-4.6is-347hp-steptronic-9791
EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	3850	1667	1529	Auto-Data Citroen C3 I Phase I (2002)	https://www.auto-data.net/en/citroen-c3-i-phase-i-2002-generation-3324
EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	3860	1667	1510	Auto-Data Citroen C3 I Phase II 1.1i	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.1i-60hp-6055
EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	3917	1683	1467	Auto-Data Ford Fiesta VI Mk6 3-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-3-door-generation-7544
EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	3917	1683	1463	Auto-Data Ford Fiesta VI Mk6 5-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-5-door-generation-1765
EU-ROVER-75-R40-SEDAN-4D-PREFL-01	4747	1778	1424	Auto-Data Rover 75 2.5 V6	https://www.auto-data.net/es/rover-75-2.5-v6-177hp-11645
EU-ROVER-75-R40-SEDAN-4D-FACELIFT-01	4749	1778	1393	Auto-Data Rover 75 facelift 2.5 V6	https://www.auto-data.net/en/rover-75-facelift-2004-2.5-v6-177hp-49210
EU-MG-ZT-T-WAGON-5D-PREFL-01	4790	1780	1410	Auto-Data MG ZT-T 2.5 V6 pre-facelift	https://www.auto-data.net/en/mg-zt-t-2.5-i-v6-24v-160hp-14058
EU-MG-ZT-T-WAGON-5D-FACELIFT-01	4791	1778	1428	Auto-Data MG ZT-T facelift	https://www.auto-data.net/en/mg-zt-t-facelift-2004-1.8-t-160hp-49240
EU-VW-PASSAT-B5-3B3-SEDAN-FACELIFT-01	4703	1746	1462	Auto-Data Volkswagen Passat B5.5 2.0 20V	https://www.auto-data.net/en/volkswagen-passat-b5.5-2.0-20v-130hp-8917
EU-VW-PASSAT-B5-3B6-WAGON-FACELIFT-01	4682	1746	1498	Auto-Data Volkswagen Passat Variant B5.5 2.0 20V	https://www.auto-data.net/en/volkswagen-passat-variant-b5.5-2.0-20v-130hp-8941
EU-VW-GOLF-IV-1J5-WAGON-5D-01	4397	1735	1485	Auto-Data Volkswagen Golf IV Variant 2.0	https://www.auto-data.net/en/volkswagen-golf-iv-variant-2.0-116hp-8702
EU-VW-BORA-1J6-WAGON-5D-01	4409	1735	1485	Auto-Data Volkswagen Bora Variant 1.9 TDI 150	https://www.auto-data.net/en/volkswagen-bora-variant-1j6-1.9-tdi-150hp-8582
EU-VOLVO-S60-I-SEDAN-4D-01	4606	1804	1431	Auto-Data Volvo S60 I	https://www.auto-data.net/en/volvo-s60-generation-1929
EU-LAMBORGHINI-MURCIELAGO-COUPE-2D-01	4580	2045	1140	Auto-Data Lamborghini Murcielago 6.2 V12	https://www.auto-data.net/en/lamborghini-murcielago-6.2-v12-48v-580hp-3098
EU-KIA-CARNIVAL-II-GQ-MPV-5D-V6-01	4925	1900	1730	Auto-Data Kia Carnival facelift 2.5 V6	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.5i-v6-150hp-2747
EU-KIA-CARNIVAL-II-GQ-MPV-5D-CRDI-01	4925	1900	1735	Auto-Data Kia Carnival facelift 2.9 CRDI	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.9-crdi-144hp-2746
EU-SUZUKI-WAGON-R-II-MPV-5D-4WD-01	3500	1620	1705	Auto-Data Suzuki Wagon R+ II 1.3 4WD	https://www.auto-data.net/en/suzuki-wagon-r-ii-1.3-i-16v-76hp-4wd-16497
EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	4290	1705	1600	Auto-Data Chrysler PT Cruiser 1.6	https://www.auto-data.net/en/chrysler-pt-cruiser-1.6-i-16v-115hp-14748
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-PREFL-01	4859	1958	1756	Auto-Data Jeep Grand Cherokee WK2 SRT8 pre-facelift	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-srt8-6.4-v8-472hp-4x4-automatic-31085
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-FACELIFT-01	4846	1954	1749	Auto-Data Jeep Grand Cherokee WK2 facelift SRT8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-facelift-2013-srt8-6.4-v8-468hp-4x4-automatic-22135
EU-FORD-FIESTA-V-HATCHBACK-3D-FACELIFT-01	3922	1685	1468	Auto-Data Ford Fiesta VI Mk6 facelift 3-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-facelift-2005-3-door-generation-7546
EU-FORD-FIESTA-V-HATCHBACK-5D-FACELIFT-01	3924	1685	1464	Auto-Data Ford Fiesta VI Mk6 facelift 5-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-facelift-2005-5-door-generation-7545
EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	4815	1795	1500	Auto-Data Toyota Camry V XV30 2.4;Auto-Data Toyota Camry V XV30 3.0	https://www.auto-data.net/fr/toyota-camry-v-xv30-2.4-16v-152hp-3923;https://www.auto-data.net/en/toyota-camry-v-xv30-3.0-v6-186hp-automatic-3924
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	3615	1660	1500	Auto-Data Toyota Yaris I 3-door 1.4 DI	https://www.auto-data.net/en/toyota-yaris-i-3-door-1.4-di-75hp-4059
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 3-door 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-1.4-d-4d-75hp-50708
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	3615	1660	1500	Toyota Yaris I 5-door specifications	https://toyota.drive.place/yaris/i/group_hatchback_5d/304998
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 5-door 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-5-door-1.4-d-4d-75hp-50726
EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-PREFL-01	3890	1690	1680	Auto-Data Toyota Yaris Verso 1.4 DI	https://www.auto-data.net/en/toyota-yaris-verso-1.4-di-75hp-4062
EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-FACELIFT-01	3880	1690	1715	Auto-Data Toyota Yaris Verso facelift 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-verso-facelift-2003-1.4-d-4d-75hp-57468
EU-CHRYSLER-NEON-II-SEDAN-4D-01	4390	1715	1421	Auto-Data Chrysler Neon II 1.6	https://www.auto-data.net/en/chrysler-neon-ii-1.6-i-16v-115hp-14778
EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	4395	1760	1330	Auto-Data Hyundai Coupe II GK	https://www.auto-data.net/en/hyundai-coupe-ii-gk-generation-2991
EU-OPEL-ASTRA-G-CONVERTIBLE-2D-01	4267	1709	1390	Auto-Data Opel Astra G Cabrio	https://www.auto-data.net/de/opel-astra-g-cabrio-2.2-ecotec-16v-147hp-2412
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	4180	1710	1475	Auto-Data Toyota Corolla Hatch IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-hatch-ix-e120-e130-1.4-i-16v-97hp-3314
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	4180	1710	1475	Auto-Data Toyota Corolla Hatch IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-hatch-ix-e120-e130-1.4-i-16v-97hp-3314
EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	4375	1710	1500	Auto-Data Toyota Corolla Wagon IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-1.4-i-16v-97hp-3320
EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	4375	1710	1470	Auto-Data Toyota Corolla IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-ix-e120-e130-1.4-i-16v-97hp-3309
EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	4240	1710	1610	Auto-Data Toyota Corolla Verso I E120	https://www.auto-data.net/en/toyota-corolla-verso-i-e120-generation-817
EU-DODGE-NEON-II-SEDAN-4D-01	4430	1712	1422	Auto-Data Dodge Neon II 2.0	https://www.auto-data.net/en/dodge-neon-ii-2.0i-133hp-automatic-28836
EU-PORSCHE-911-996-TARGA-FACELIFT-01	4430	1770	1305	Auto-Data Porsche 911 Targa 996 facelift 3.6	https://www.auto-data.net/en/porsche-911-targa-996-facelift-2001-3.6-320hp-6605
EU-DODGE-CARAVAN-III-MPV-SWB-01	4733	1920	1740	Auto-Data Dodge Caravan III SWB 2.4	https://www.auto-data.net/en/dodge-caravan-iii-swb-2.4-152hp-automatic-2941
EU-DODGE-CARAVAN-III-MPV-LWB-01	5070	1950	1740	Auto-Data Dodge Caravan III LWB 3.0 V6	https://www.auto-data.net/en/dodge-caravan-iii-lwb-3.0-v6-152hp-automatic-31430
EU-CADILLAC-CTS-I-SEDAN-4D-01	4828	1793	1440	Auto-Data Cadillac CTS I 3.2 V6	https://www.auto-data.net/en/cadillac-cts-i-3.2i-v6-24v-223hp-11701
```

## 下一步优先处理

1. 仅处理 `16354` Alpina B3 3.3 Allrad Sedan 与 `16355` Alpina B3 3.3 Allrad Touring。
2. 优先寻找同期 Alpina 官方技术表、产品目录或可追溯规格页，确认两种车身的完整长宽高及不含后视镜宽度。
3. 若三维与现有 BMW E46 组完全相同则直接复用；存在任一三维差异时分别创建新的 Alpina B3 3.3 Allrad 尺寸组。
4. 两行闭合后立即进行一次机械检查并输出 COMPLETE，不重新核对其余已闭合尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s3-8l-facelift-2001-1.8-t-225hp-quattro-4908?utm_source=chatgpt.com "Audi S3 (8L, facelift 2001) 1.8 T (225 Hp) quattro"
[2]: https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-1.4-i-16v-97hp-3320?utm_source=chatgpt.com "Toyota Corolla Wagon IX (E120, E130) 1.4 i 16V (97 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.alpina-archive.com/?page_id=164&utm_source=chatgpt.com "Alpina-Archive | B3 3.3"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12501-12600_ktype_dimension_mapping_final.tsv
- all_12501-12600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合剩余 `16354`、`16355`：分别建立 Alpina B3 3.3 Allrad E46 Sedan 与 Touring 独立尺寸组，未覆盖或改写既有 BMW E46、Alpina 尺寸组。轿车外廓为 `4471 × 1739 × 1414 mm`，旅行车外廓为 `4478 × 1739 × 1409 mm`。([encyCARpedia][1])
* 已完成轻量机械收尾：固定表头、唯一主键、映射引用闭合、尺寸与来源非空、无孤立尺寸组、指定下载文件存在。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：138
* READY 映射：138
* PENDING 映射：0
* 最终尺寸组：76
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16301	16301	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
16302	16302	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
16303_swb_lowroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_swb_midroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_lwb_midroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16303_lwb_highroof	16303	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_swb_lowroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_swb_midroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_lwb_midroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16304_lwb_highroof	16304	Van	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	轴距/车顶外廓分支。	READY
16306	16306	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
16307	16307	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
16314	16314	Hatchback	S3 8L facelift	8L	3	EU-AUDI-S3-8L-HATCHBACK-3D-FACELIFT-01	HIGH		READY
16315	16315	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
16316_prefl	16316	Sedan	Impreza II	GDB	4	EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-PREFL-01	HIGH	改款前外廓。	READY
16316_facelift	16316	Sedan	Impreza II facelift	GDB	4	EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-FACELIFT-01	HIGH	2002年改款外廓。	READY
16317	16317	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
16318	16318	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH		READY
16319	16319	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16320	16320	Sedan	IS I	XE10	4	EU-LEXUS-IS-I-XE10-SEDAN-4D-01	HIGH		READY
16321	16321	Wagon	IS I SportCross	XE10	5	EU-LEXUS-IS-I-XE10-SPORTCROSS-WAGON-5D-01	HIGH		READY
16322	16322	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16323	16323	Convertible	A4 B6 Cabriolet	8H	2	EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	HIGH		READY
16324	16324	Convertible	A4 B6 Cabriolet	8H	2	EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	HIGH		READY
16325	16325	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
16326	16326	Wagon	3 Series E46 facelift	E46	5	EU-BMW-3-E46-TOURING-5D-01	HIGH		READY
16327	16327	Convertible	3 Series E46 facelift	E46	2	EU-BMW-3-E46-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
16328	16328	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-5D-4-6IS-01	HIGH		READY
16329	16329	MPV	Trans Sport II	U	5	EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	HIGH		READY
16330_prefl	16330	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16330_facelift	16330	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16331_prefl	16331	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16331_facelift	16331	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16332_3dr_prefl	16332	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	三门改款前外廓。	READY
16332_3dr_facelift	16332	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	三门改款外廓。	READY
16332_5dr_prefl	16332	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	五门改款前外廓。	READY
16332_5dr_facelift	16332	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	五门改款外廓。	READY
16333_3dr_prefl	16333	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	三门改款前外廓。	READY
16333_3dr_facelift	16333	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	三门改款外廓。	READY
16333_5dr_prefl	16333	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	五门改款前外廓。	READY
16333_5dr_facelift	16333	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	五门改款外廓。	READY
16334_prefl	16334	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16334_facelift	16334	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16335_prefl	16335	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16335_facelift	16335	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16336_prefl	16336	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
16336_facelift	16336	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16337_3dr	16337	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门外廓。	READY
16337_5dr	16337	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门外廓。	READY
16338_3dr	16338	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门外廓。	READY
16338_5dr	16338	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门外廓。	READY
16339	16339	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16340_prefl	16340	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
16340_facelift	16340	Hatchback	New Beetle I facelift	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	HIGH	2005年改款外廓。	READY
16341_prefl	16341	Sedan	75	R40	4	EU-ROVER-75-R40-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16341_facelift	16341	Sedan	75 facelift	R40	4	EU-ROVER-75-R40-SEDAN-4D-FACELIFT-01	HIGH	2004年改款外廓。	READY
16344	16344	Wagon	ZT-T		5	EU-MG-ZT-T-WAGON-5D-PREFL-01	HIGH		READY
16345_prefl	16345	Wagon	ZT-T		5	EU-MG-ZT-T-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
16345_facelift	16345	Wagon	ZT-T facelift		5	EU-MG-ZT-T-WAGON-5D-FACELIFT-01	HIGH	2004年改款外廓。	READY
16346	16346	Sedan	Passat B5.5	3B3	4	EU-VW-PASSAT-B5-3B3-SEDAN-FACELIFT-01	HIGH		READY
16347	16347	Wagon	Passat B5.5	3B6	5	EU-VW-PASSAT-B5-3B6-WAGON-FACELIFT-01	HIGH		READY
16348	16348	Wagon	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-WAGON-5D-01	HIGH		READY
16349	16349	Wagon	Bora Variant	1J6	5	EU-VW-BORA-1J6-WAGON-5D-01	HIGH		READY
16350	16350	Wagon	Bora Variant	1J6	5	EU-VW-BORA-1J6-WAGON-5D-01	HIGH		READY
16351	16351	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	MEDIUM	250 hp Aero对应2002–2005外廓；输入结束年月宽于该版本。	READY
16352	16352	Sedan	S60 I	P2	4	EU-VOLVO-S60-I-SEDAN-4D-01	HIGH		READY
16353	16353	Coupe	Murcielago		2	EU-LAMBORGHINI-MURCIELAGO-COUPE-2D-01	HIGH		READY
16354	16354	Sedan	B3 3.3 Allrad E46	E46	4	EU-ALPINA-B3-3-3-ALLRAD-E46-SEDAN-4D-01	HIGH		READY
16355	16355	Wagon	B3 3.3 Allrad E46	E46	5	EU-ALPINA-B3-3-3-ALLRAD-E46-WAGON-5D-01	HIGH		READY
16356	16356	MPV	Carnival II	GQ	5	EU-KIA-CARNIVAL-II-GQ-MPV-5D-V6-01	HIGH		READY
16357	16357	MPV	Carnival II	GQ	5	EU-KIA-CARNIVAL-II-GQ-MPV-5D-CRDI-01	HIGH		READY
16358	16358	MPV	Wagon R+ II		5	EU-SUZUKI-WAGON-R-II-MPV-5D-4WD-01	HIGH	来源车型分类为五门MPV。	READY
16359	16359	Hatchback	PT Cruiser	PT	5	EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	HIGH	来源车型分类为五门Hatchback。	READY
16360_prefl	16360	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-PREFL-01	HIGH	SRT8改款前外廓。	READY
16360_facelift	16360	SUV	Grand Cherokee IV facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-FACELIFT-01	HIGH	SRT8改款外廓。	READY
16361_3dr_prefl	16361	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16361_3dr_facelift	16361	Hatchback	Fiesta V facelift		3	EU-FORD-FIESTA-V-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款外廓。	READY
16361_5dr_prefl	16361	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16361_5dr_facelift	16361	Hatchback	Fiesta V facelift		5	EU-FORD-FIESTA-V-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款外廓。	READY
16362	16362	Sedan	Camry V	XV30	4	EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	HIGH		READY
16363	16363	Sedan	Camry V	XV30	4	EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	HIGH		READY
16364_3dr_prefl	16364	Hatchback	Yaris I	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16364_3dr_facelift	16364	Hatchback	Yaris I facelift	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款外廓。	READY
16364_5dr_prefl	16364	Hatchback	Yaris I	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16364_5dr_facelift	16364	Hatchback	Yaris I facelift	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款外廓。	READY
16365_prefl	16365	MPV	Yaris Verso	XP20	5	EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-PREFL-01	HIGH	改款前外廓。	READY
16365_facelift	16365	MPV	Yaris Verso facelift	XP20	5	EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-FACELIFT-01	HIGH	2003年改款外廓。	READY
16366	16366	Sedan	Neon II	PL2	4	EU-CHRYSLER-NEON-II-SEDAN-4D-01	HIGH		READY
16367	16367	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
16368	16368	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
16369	16369	Coupe	Coupe II	GK	2	EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	HIGH		READY
16370	16370	Coupe	Coupe II	GK	2	EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	HIGH		READY
16371	16371	Convertible	Astra G		2	EU-OPEL-ASTRA-G-CONVERTIBLE-2D-01	HIGH		READY
16373_3dr	16373	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16373_5dr	16373	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16374_3dr	16374	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16374_5dr	16374	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16375_3dr	16375	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16375_5dr	16375	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16376_3dr	16376	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16376_5dr	16376	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16377_3dr	16377	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16377_5dr	16377	Hatchback	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16378	16378	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16379	16379	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16380	16380	Wagon	Corolla IX	E120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	HIGH		READY
16381	16381	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	HIGH		READY
16382	16382	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	HIGH		READY
16384	16384	MPV	Corolla Verso I	E120	5	EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	HIGH		READY
16385	16385	MPV	Corolla Verso I	E120	5	EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	HIGH		READY
16386	16386	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16387	16387	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16388	16388	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16389	16389	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
16390	16390	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16391	16391	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16392	16392	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL外廓。	READY
16393	16393	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH		READY
16394	16394	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH		READY
16395	16395	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL2外廓。	READY
16396	16396	Sedan	Neon II	PL2	4	EU-DODGE-NEON-II-SEDAN-4D-01	HIGH	Plymouth品牌共享同一PL2外廓。	READY
16397	16397	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16398	16398	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16399	16399	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
16400	16400	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16401	16401	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16402	16402	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16403	16403	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Dodge品牌共享同一JA外廓。	READY
16404	16404	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16405	16405	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16406	16406	Sedan	Breeze	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH	Plymouth品牌共享同一JA外廓。	READY
16407_3dr	16407	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	HIGH	三门短轴外廓。	READY
16407_5dr	16407	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	HIGH	五门长轴外廓。	READY
16409	16409	Targa	911 996 facelift	996	2	EU-PORSCHE-911-996-TARGA-FACELIFT-01	HIGH		READY
16410	16410	MPV	Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH		READY
16411_swb	16411	MPV	Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	短轴外廓。	READY
16411_lwb	16411	MPV	Grand Caravan III	NS	5	EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	长轴外廓。	READY
16413	16413	Sedan	CTS I		4	EU-CADILLAC-CTS-I-SEDAN-4D-01	MEDIUM	功率标注存在市场换算差异，物理外廓一致。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_12501-12600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496	Encycarpedia Volkswagen Passat Variant TDI 4Motion B5	https://www.encycarpedia.com/volkswagen/99-passat-variant-tdi-4motion-estate
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Transit Center Ford Transit Mk5 1994-2000 specifications	https://www.transitcenter.uk/transit-mk1-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Transit Center Ford Transit Mk5 1994-2000 specifications	https://www.transitcenter.uk/transit-mk1-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Transit Center Ford Transit Mk5 1994-2000 specifications	https://www.transitcenter.uk/transit-mk1-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Transit Center Ford Transit Mk5 1994-2000 specifications	https://www.transitcenter.uk/transit-mk1-data-specification.php
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	CarsGuide Volkswagen Passat dimensions 1999	https://www.carsguide.com.au/volkswagen/passat/car-dimensions/1999
EU-AUDI-S3-8L-HATCHBACK-3D-FACELIFT-01	4159	1763	1415	Auto-Data Audi S3 (8L facelift 2001) 1.8 T quattro	https://www.auto-data.net/en/audi-s3-8l-facelift-2001-1.8-t-225hp-quattro-4908
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415	CarsGuide BMW 330i dimensions 2001	https://www.carsguide.com.au/bmw/3-series/330i/car-dimensions/2001
EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-PREFL-01	4405	1730	1440	Automobile-Catalog Subaru Impreza 2.0 WRX STi 2001	https://www.automobile-catalog.com/car/2001/3255710/subaru_impreza_2_0_wrx_sti.html
EU-SUBARU-IMPREZA-II-GDB-SEDAN-WRX-STI-FACELIFT-01	4415	1740	1440	Auto-Data Subaru Impreza II facelift WRX STi	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2002-wrx-sti-2.0-265hp-awd-16082
EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	3830	1675	1525	Honda Jazz 02 press release	https://hondanews.eu/eu/en/media/pressreleases/34284/jazz-02
EU-AUDI-A4-B6-8E2-SEDAN-4D-01	4548	1772	1428	Automobile-Catalog Audi A4 2.4 2002	https://www.automobile-catalog.com/car/2002/246755/audi_a4_2_4.html
EU-AUDI-A4-B6-8E5-WAGON-5D-01	4548	1772	1428	Auto-Data Audi A4 Avant (B6 8E) 2.4 V6	https://www.auto-data.net/en/audi-a4-avant-b6-8e-2.4i-v6-30v-170hp-4398
EU-LEXUS-IS-I-XE10-SEDAN-4D-01	4400	1725	1405	Lexus IS 300 and SportCross launch pack 2001	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/141010DM4-IS-300-and-SportCross-launch-pack-2001.pdf
EU-LEXUS-IS-I-XE10-SPORTCROSS-WAGON-5D-01	4505	1725	1430	Lexus IS 300 and SportCross launch pack 2001	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/141010DM4-IS-300-and-SportCross-launch-pack-2001.pdf
EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	4573	1777	1391	Auto-Data Audi A4 Cabriolet (B6 8H) 2.4 V6	https://www.auto-data.net/en/audi-a4-cabriolet-b6-8h-2.4-v6-30v-170hp-26633
EU-BMW-3-E46-TOURING-5D-01	4478	1739	1409	Encycarpedia BMW 318i Touring E46	https://www.encycarpedia.com/bmw/99-318i-touring-estate
EU-BMW-3-E46-CONVERTIBLE-2D-FACELIFT-01	4488	1757	1369	Auto-Data BMW 3 Series Convertible E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-convertible-e46-facelift-2003-318ci-143hp-9964
EU-BMW-X5-E53-SUV-5D-4-6IS-01	4666	1872	1717	Auto-Data BMW X5 (E53) 4.6is	https://www.auto-data.net/en/bmw-x5-e53-4.6is-347hp-steptronic-9791
EU-CHEVROLET-TRANS-SPORT-U-MPV-LWB-01	5113	1850	1730	Auto-Data Chevrolet Trans Sport U 3.4 V6	https://www.auto-data.net/en/chevrolet-trans-sport-u-3.4-i-v6-186hp-14448
EU-CITROEN-C3-I-HATCHBACK-5D-PREFL-01	3850	1667	1529	Auto-Data Citroen C3 I Phase I (2002)	https://www.auto-data.net/en/citroen-c3-i-phase-i-2002-generation-3324
EU-CITROEN-C3-I-HATCHBACK-5D-FACELIFT-01	3860	1667	1510	Auto-Data Citroen C3 I Phase II 1.1i	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.1i-60hp-6055
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465	Volkswagen Self-Study Programme 263 Polo Model Year 2002	https://www.volkspage.net/technik/ssp/ssp/SSP_263_d1.pdf
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467	Automoli Volkswagen Polo IV 9N facelift 2005	https://www.automoli.com/en/vehicles/volkswagen/polo/polo-iv-9n-facelift-2005-1854/
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465	Volkswagen Self-Study Programme 263 Polo Model Year 2002	https://www.volkspage.net/technik/ssp/ssp/SSP_263_d1.pdf
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467	Automoli Volkswagen Polo IV 9N facelift 2005	https://www.automoli.com/en/vehicles/volkswagen/polo/polo-iv-9n-facelift-2005-1854/
EU-FORD-FIESTA-V-HATCHBACK-3D-PREFL-01	3917	1683	1467	Auto-Data Ford Fiesta VI Mk6 3-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-3-door-generation-7544
EU-FORD-FIESTA-V-HATCHBACK-5D-PREFL-01	3917	1683	1463	Auto-Data Ford Fiesta VI Mk6 5-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-5-door-generation-1765
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	4081	1725	1500	AutoData1 Volkswagen New Beetle 9C 2.0 Automatic	https://www.autodata1.com/en/car/volkswagen/beetle/new-beetle-9c-20-115-hp-automatic
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Automoli Volkswagen New Beetle 9C facelift 2005	https://www.automoli.com/en/vehicles/volkswagen/beetle/new-beetle-9c-facelift-2005-5364/
EU-ROVER-75-R40-SEDAN-4D-PREFL-01	4747	1778	1424	Auto-Data Rover 75 2.5 V6	https://www.auto-data.net/es/rover-75-2.5-v6-177hp-11645
EU-ROVER-75-R40-SEDAN-4D-FACELIFT-01	4749	1778	1393	Auto-Data Rover 75 facelift 2.5 V6	https://www.auto-data.net/en/rover-75-facelift-2004-2.5-v6-177hp-49210
EU-MG-ZT-T-WAGON-5D-PREFL-01	4790	1780	1410	Auto-Data MG ZT-T 2.5 V6 pre-facelift	https://www.auto-data.net/en/mg-zt-t-2.5-i-v6-24v-160hp-14058
EU-MG-ZT-T-WAGON-5D-FACELIFT-01	4791	1778	1428	Auto-Data MG ZT-T facelift	https://www.auto-data.net/en/mg-zt-t-facelift-2004-1.8-t-160hp-49240
EU-VW-PASSAT-B5-3B3-SEDAN-FACELIFT-01	4703	1746	1462	Auto-Data Volkswagen Passat B5.5 2.0 20V	https://www.auto-data.net/en/volkswagen-passat-b5.5-2.0-20v-130hp-8917
EU-VW-PASSAT-B5-3B6-WAGON-FACELIFT-01	4682	1746	1498	Auto-Data Volkswagen Passat Variant B5.5 2.0 20V	https://www.auto-data.net/en/volkswagen-passat-variant-b5.5-2.0-20v-130hp-8941
EU-VW-GOLF-IV-1J5-WAGON-5D-01	4397	1735	1485	Auto-Data Volkswagen Golf IV Variant 2.0	https://www.auto-data.net/en/volkswagen-golf-iv-variant-2.0-116hp-8702
EU-VW-BORA-1J6-WAGON-5D-01	4409	1735	1485	Auto-Data Volkswagen Bora Variant 1.9 TDI 150	https://www.auto-data.net/en/volkswagen-bora-variant-1j6-1.9-tdi-150hp-8582
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449	Automobile-Catalog Saab 9-5 3.0 TiD 2001	https://www.automobile-catalog.com/car/2001/3033920/saab_9-5_3_0_tid.html
EU-VOLVO-S60-I-SEDAN-4D-01	4606	1804	1431	Auto-Data Volvo S60 I	https://www.auto-data.net/en/volvo-s60-generation-1929
EU-LAMBORGHINI-MURCIELAGO-COUPE-2D-01	4580	2045	1140	Auto-Data Lamborghini Murcielago 6.2 V12	https://www.auto-data.net/en/lamborghini-murcielago-6.2-v12-48v-580hp-3098
EU-ALPINA-B3-3-3-ALLRAD-E46-SEDAN-4D-01	4471	1739	1414	Automobile-Catalog Alpina B3 3.3 Allrad Switch-Tronic;Encycarpedia Alpina B3 3.3 Allrad E46 Saloon	https://www.automobile-catalog.com/car/2002/288035/alpina_b3_3_3_allrad_switch-tronic.html;https://www.encycarpedia.com/alpina/01-b3-3-3-allrad-e46-saloon
EU-ALPINA-B3-3-3-ALLRAD-E46-WAGON-5D-01	4478	1739	1409	Automobile-Catalog Alpina B3 3.3 Touring Allrad Switch-Tronic;Encycarpedia Alpina B3 3.3 Touring Allrad E46 Estate	https://www.automobile-catalog.com/car/2001/288050/alpina_b3_3_3_touring_allrad_switch-tronic.html;https://www.encycarpedia.com/alpina/01-b3-3-3-touring-allrad-e46-estate
EU-KIA-CARNIVAL-II-GQ-MPV-5D-V6-01	4925	1900	1730	Auto-Data Kia Carnival facelift 2.5 V6	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.5i-v6-150hp-2747
EU-KIA-CARNIVAL-II-GQ-MPV-5D-CRDI-01	4925	1900	1735	Auto-Data Kia Carnival facelift 2.9 CRDI	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.9-crdi-144hp-2746
EU-SUZUKI-WAGON-R-II-MPV-5D-4WD-01	3500	1620	1705	Auto-Data Suzuki Wagon R+ II 1.3 4WD	https://www.auto-data.net/en/suzuki-wagon-r-ii-1.3-i-16v-76hp-4wd-16497
EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	4290	1705	1600	Auto-Data Chrysler PT Cruiser 1.6	https://www.auto-data.net/en/chrysler-pt-cruiser-1.6-i-16v-115hp-14748
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-PREFL-01	4859	1958	1756	Auto-Data Jeep Grand Cherokee WK2 SRT8 pre-facelift	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-srt8-6.4-v8-472hp-4x4-automatic-31085
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-SRT8-FACELIFT-01	4846	1954	1749	Auto-Data Jeep Grand Cherokee WK2 facelift SRT8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-facelift-2013-srt8-6.4-v8-468hp-4x4-automatic-22135
EU-FORD-FIESTA-V-HATCHBACK-3D-FACELIFT-01	3922	1685	1468	Auto-Data Ford Fiesta VI Mk6 facelift 3-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-facelift-2005-3-door-generation-7546
EU-FORD-FIESTA-V-HATCHBACK-5D-FACELIFT-01	3924	1685	1464	Auto-Data Ford Fiesta VI Mk6 facelift 5-door	https://www.auto-data.net/en/ford-fiesta-vi-mk6-facelift-2005-5-door-generation-7545
EU-TOYOTA-CAMRY-V-XV30-SEDAN-4D-01	4815	1795	1500	Auto-Data Toyota Camry V XV30 2.4;Auto-Data Toyota Camry V XV30 3.0	https://www.auto-data.net/fr/toyota-camry-v-xv30-2.4-16v-152hp-3923;https://www.auto-data.net/en/toyota-camry-v-xv30-3.0-v6-186hp-automatic-3924
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	3615	1660	1500	Auto-Data Toyota Yaris I 3-door 1.4 DI	https://www.auto-data.net/en/toyota-yaris-i-3-door-1.4-di-75hp-4059
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 3-door 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-1.4-d-4d-75hp-50708
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	3615	1660	1500	Toyota Yaris I 5-door specifications	https://toyota.drive.place/yaris/i/group_hatchback_5d/304998
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3640	1660	1500	Auto-Data Toyota Yaris I facelift 5-door 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-5-door-1.4-d-4d-75hp-50726
EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-PREFL-01	3890	1690	1680	Auto-Data Toyota Yaris Verso 1.4 DI	https://www.auto-data.net/en/toyota-yaris-verso-1.4-di-75hp-4062
EU-TOYOTA-YARIS-VERSO-XP20-MPV-5D-FACELIFT-01	3880	1690	1715	Auto-Data Toyota Yaris Verso facelift 1.4 D-4D	https://www.auto-data.net/en/toyota-yaris-verso-facelift-2003-1.4-d-4d-75hp-57468
EU-CHRYSLER-NEON-II-SEDAN-4D-01	4390	1715	1421	Auto-Data Chrysler Neon II 1.6	https://www.auto-data.net/en/chrysler-neon-ii-1.6-i-16v-115hp-14778
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410	Auto-Data Hyundai Sonata IV EF	https://www.auto-data.net/en/hyundai-sonata-iv-ef-generation-2987
EU-HYUNDAI-COUPE-II-GK-COUPE-2D-01	4395	1760	1330	Auto-Data Hyundai Coupe II GK	https://www.auto-data.net/en/hyundai-coupe-ii-gk-generation-2991
EU-OPEL-ASTRA-G-CONVERTIBLE-2D-01	4267	1709	1390	Auto-Data Opel Astra G Cabrio	https://www.auto-data.net/de/opel-astra-g-cabrio-2.2-ecotec-16v-147hp-2412
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	4180	1710	1475	Auto-Data Toyota Corolla Hatch IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-hatch-ix-e120-e130-1.4-i-16v-97hp-3314
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	4180	1710	1475	Auto-Data Toyota Corolla Hatch IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-hatch-ix-e120-e130-1.4-i-16v-97hp-3314
EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	4375	1710	1500	Auto-Data Toyota Corolla Wagon IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-1.4-i-16v-97hp-3320
EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	4375	1710	1470	Auto-Data Toyota Corolla IX E120/E130 1.4	https://www.auto-data.net/en/toyota-corolla-ix-e120-e130-1.4-i-16v-97hp-3309
EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	4240	1710	1610	Auto-Data Toyota Corolla Verso I E120	https://www.auto-data.net/en/toyota-corolla-verso-i-e120-generation-817
EU-CHRYSLER-NEON-PL-SEDAN-4D-01	4364	1714	1369	Encycarpedia Chrysler Neon 2.0 LE	https://www.encycarpedia.com/chrysler/98-neon-2-0-le-saloon
EU-DODGE-NEON-II-SEDAN-4D-01	4430	1712	1422	Auto-Data Dodge Neon II 2.0	https://www.auto-data.net/en/dodge-neon-ii-2.0i-133hp-automatic-28836
EU-CHRYSLER-STRATUS-JA-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus JA Sedan	https://www.auto-data.net/en/chrysler-stratus-ja-2.5-v6-24v-163hp-automatic-14805
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	4230	1760	1931	Auto-Data Mercedes-Benz G-class W463 facelift 2000 G 270 CDI	https://www.auto-data.net/en/mercedes-benz-g-class-w463-facelift-2000-g-270-cdi-156hp-4matic-automatic-42222
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931	Automobile-Catalog Mercedes-Benz G 500 Station Wagon LWB	https://www.automobile-catalog.com/car/2008/1566275/mercedes-benz_g_500_station_wagon_lwb_7g-tronic.html
EU-PORSCHE-911-996-TARGA-FACELIFT-01	4430	1770	1305	Auto-Data Porsche 911 Targa 996 facelift 3.6	https://www.auto-data.net/en/porsche-911-targa-996-facelift-2001-3.6-320hp-6605
EU-DODGE-CARAVAN-III-MPV-SWB-01	4733	1920	1740	Auto-Data Dodge Caravan III SWB 2.4	https://www.auto-data.net/en/dodge-caravan-iii-swb-2.4-152hp-automatic-2941
EU-DODGE-CARAVAN-III-MPV-LWB-01	5070	1950	1740	Auto-Data Dodge Caravan III LWB 3.0 V6	https://www.auto-data.net/en/dodge-caravan-iii-lwb-3.0-v6-152hp-automatic-31430
EU-CADILLAC-CTS-I-SEDAN-4D-01	4828	1793	1440	Auto-Data Cadillac CTS I 3.2 V6	https://www.auto-data.net/en/cadillac-cts-i-3.2i-v6-24v-223hp-11701
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_12501-12600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.encycarpedia.com/alpina/01-b3-3-3-allrad-e46-saloon?utm_source=chatgpt.com "2001-2005 Alpina B3 3.3 Allrad E46 Specs & Performance ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_12501-12600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_12501-12600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（11210 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3527 行）

