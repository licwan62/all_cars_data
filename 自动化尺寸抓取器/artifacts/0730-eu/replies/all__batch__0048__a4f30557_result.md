# 任务：all 第 4701-4800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0048__a4f30557


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
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460
EU-AUDI-A8-D5-S8-SEDAN-01	5179	1945	1474
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473
EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	4506	1851	1602
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434
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
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-BMW-X4-F98-M-COMPETITION-SUV-01	4758	1927	1620
EU-BMW-X4-F98-M-SUV-01	4758	1927	1618
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	5943	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	5358	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	6308	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-CH1-01	4908	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-LH1-01	5943	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MH1-01	5358	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MLH1-01	5708	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-XLH1-01	6308	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	5998	2050	2522
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	5998	2050	2760
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	6363	2050	2522
EU-FIAT-DUCATO-III-X290-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-X290-L1H2-01	4963	2050	2524
EU-FIAT-DUCATO-III-X290-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-X290-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	4908	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	5358	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X290-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-X290-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	5413	2050	2269
EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	5413	2050	2254
EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	5413	2050	2539
EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	5413	2050	2524
EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	5998	2050	2534
EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	5998	2050	2524
EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	5998	2050	2774
EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	5998	2050	2764
EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	6363	2050	2534
EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	6363	2050	2539
EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	6363	2050	2774
EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	6363	2050	2779
EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	3538	1589	1576
EU-FIAT-PANDA-III-319-NATURAL-POWER-HATCHBACK-01	3653	1643	1605
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470
EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	4775	1815	1470
EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	4770	1815	1470
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	4475	1923	1308
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
EU-MAZDA-CX-30-DM-SUV-01	4395	1795	1540
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
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	5052	1913	1422
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424
EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	5246	1899	1494
EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	5096	1871	1479
EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	5125	1905	1493
EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	5116	1899	1496
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300
EU-PORSCHE-BOXSTER-981-CONVERTIBLE-01	4374	1801	1282
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1292
EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	4282	1829	1805
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
EU-VW-T-CROSS-I-C1-SUV-PREFL-01	4108	1760	1584

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Panda	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	51	69	Jan 2020	-	2024-03-01	139163
Hyundai	I40 i cw	2.0 Cvvt	Kombi	Frontantrieb	Benzin	130	177	Jul 2011	May 2019	2024-03-01	139167
Hyundai	I40 i	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	121	165	Mar 2012	May 2019	2024-03-01	139168
Hyundai	I40 i	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	130	177	Mar 2012	May 2019	2024-03-01	139169
Dacia	Dokker	1.3 TCE 100	Kasten/Großraumlimousine	Frontantrieb	Benzin	75	102	Aug 2019	Dec 2021	2024-11-01	139171
Dacia	Dokker	1.3 TCE 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Aug 2019	Dec 2021	2024-11-01	139172
Dacia	Dokker	1.3 TCE 100	Großraumlimousine	Frontantrieb	Benzin	75	102	Aug 2019	Dec 2021	2024-11-01	139173
VW	Caddy alltrack iv	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	81	110	May 2015	Sep 2020	2025-06-01	139174
VW	Caddy alltrack iv	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	103	140	May 2015	Sep 2020	2025-06-01	139175
VW	Caddy alltrack iv	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2015	Sep 2020	2025-11-01	139176
VW	Caddy alltrack iv	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2015	Nov 2017	2025-06-01	139177
VW	Caddy alltrack iv	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	75	102	May 2015	Sep 2020	2025-06-01	139178
BMW	3	320 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	120	163	Mar 2020	-	2024-03-01	139184
BMW	3	320 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139186
Jaguar	F-Type	5.0 Scv8 P450	Cabriolet	Heckantrieb	Benzin	331	450	Dec 2019	-	2024-03-01	139188
BMW	3	320 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	120	163	Mar 2020	-	2024-03-01	139189
Jaguar	F-Type	5.0 Scv8 P450 AWD	Cabriolet	Allrad	Benzin	331	450	Dec 2019	-	2024-03-01	139190
Jaguar	F-Type	5.0 Scv8 P450	Coupe	Heckantrieb	Benzin	331	450	Dec 2019	-	2024-03-01	139191
BMW	3	320 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139192
Jaguar	F-Type	5.0 Scv8 P450 AWD	Coupe	Allrad	Benzin	331	450	Dec 2019	-	2024-03-01	139193
BMW	3	320 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	120	163	Mar 2020	-	2024-03-01	139198
BMW	3	320 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139199
BMW	3	320 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	120	163	Mar 2020	-	2024-03-01	139200
BMW	3	320 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139201
BMW	X3	Xdrive 20 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	120	163	Apr 2020	-	2024-03-01	139202
BMW	X3	Xdrive 20 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	140	190	Apr 2020	-	2024-03-01	139203
BMW	X4	Xdrive 20 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	120	163	Apr 2020	-	2024-03-01	139204
BMW	X4	Xdrive 20 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	140	190	Apr 2020	-	2024-03-01	139205
BMW	1	120 D	Schrägheck	Frontantrieb	Diesel	140	190	Mar 2020	-	2024-03-01	139207
Renault	Captur ii	TCE 100	Schrägheck	Frontantrieb	Benzin	74	101	Jan 2020	-	2024-03-01	139208
Renault	Captur ii	TCE 130	Schrägheck	Frontantrieb	Benzin	96	131	Jan 2020	-	2024-03-01	139209
Renault	Captur ii	TCE 155	Schrägheck	Frontantrieb	Benzin	113	154	Jan 2020	-	2024-03-01	139210
Renault	Captur ii	Blue DCI 95	Schrägheck	Frontantrieb	Diesel	70	95	Jan 2020	-	2024-03-01	139211
Renault	Captur ii	Blue DCI 115	Schrägheck	Frontantrieb	Diesel	85	116	Jan 2020	-	2024-03-01	139212
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	115	156	Mar 2020	-	2024-03-01	139215
BMW	3	318 I	Kombi	Heckantrieb	Benzin	115	156	Mar 2020	-	2024-03-01	139216
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	190	258	Jul 2020	-	2024-11-01	139218
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	210	286	Jul 2020	-	2024-11-01	139219
Ford USA	Mustang mach-E	First Edition	Geländewagen geschlossen	Heckantrieb	Elektro	248	337	Oct 2020	-	2024-11-01	139220
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	190	258	Jul 2020	-	2024-11-01	139221
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	248	337	Jul 2020	-	2024-11-01	139222
Polestar	Polestar 2	EV	Schrägheck	Allrad	Elektro	300	408	Apr 2019	Dec 2023	2024-03-01	139223
Toyota	Proace city	1.2 Vvt-i 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Oct 2019	-	2024-03-01	139226
Toyota	Proace city	1.2 Vvt-i 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Oct 2019	-	2024-03-01	139227
Toyota	Proace city	1.5 D-4d 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2019	-	2024-03-01	139228
Toyota	Proace city	1.5 D-4d 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Oct 2019	-	2024-03-01	139229
Toyota	Proace city	1.5 D-4d 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Oct 2019	-	2024-03-01	139230
Toyota	Proace city verso	1.2 Vvt-i 110	Großraumlimousine	Frontantrieb	Benzin	81	110	Oct 2019	-	2024-03-01	139234
Toyota	Proace city verso	1.5 D-4d 100	Großraumlimousine	Frontantrieb	Diesel	75	102	Oct 2019	-	2024-03-01	139235
Toyota	Proace city verso	1.5 D-4d 130	Großraumlimousine	Frontantrieb	Diesel	96	131	Oct 2019	-	2024-03-01	139236
Toyota	Proace city verso	1.2 Vvt-i 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Oct 2019	-	2024-03-01	139238
Hyundai	Ioniq	Electric	Schrägheck	Frontantrieb	Elektro	100	136	Jul 2019	Jul 2022	2024-05-01	139239
Audi	A5	30 TDI Mild Hybrid	Coupe	Frontantrieb	Diesel/Elektro	100	136	Oct 2019	-	2024-03-01	139240
Audi	A5	30 TDI Mild Hybrid	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Oct 2019	-	2024-03-01	139241
Saab	9-3x	2.0 T16 XWD	Kombi	Allrad	Benzin	162	220	Jan 2011	Feb 2015	2024-03-01	139242
Skoda	Octavia	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Nov 2019	-	2024-03-01	139248
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	85	116	Nov 2019	-	2024-03-01	139249
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	139250
Fiat	Ducato	2.0 LPG	Bus	Frontantrieb	Benzin/Autogas (LPG)	71	97	Nov 2002	Jul 2006	2024-03-01	139254
Fiat	Ducato	2.0 LPG	Kasten	Frontantrieb	Benzin/Autogas (LPG)	71	97	Nov 2002	Jul 2006	2024-03-01	139255
Porsche	Taycan	4S	Stufenheck	Allrad	Elektro	390	530	May 2019	Dec 2023	2024-07-01	139256
Porsche	Taycan	Turbo	Stufenheck	Allrad	Elektro	500	680	May 2019	Dec 2023	2024-07-01	139257
Porsche	Taycan	Turbo S	Stufenheck	Allrad	Elektro	560	761	May 2019	Dec 2023	2024-07-01	139258
Mazda	Cx-30	Skyactiv-g M Hybrid	SUV	Frontantrieb	Benzin/Elektro	110	150	Jan 2020	-	2024-03-01	139259
Mazda	Cx-30	Skyactiv-g M Hybrid AWD	SUV	Allrad	Benzin/Elektro	110	150	Jan 2020	-	2024-03-01	139260
VW	T-Cross	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jan 2020	-	2024-03-01	139261
Volvo	Xc60 ii	B5 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	184	250	Jan 2020	-	2024-03-01	139262
Volvo	Xc60 ii	B5 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	184	250	Jan 2020	-	2024-03-01	139263
Volvo	Xc90 ii	B5 Mild Hybrid AWD	SUV	Allrad	Benzin/Elektro	184	250	Jan 2020	-	2025-06-01	139264
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	160	218	Mar 2005	Mar 2007	2024-03-01	139265
Audi	A8 d5	60 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	320	435	Nov 2019	-	2024-03-01	139266
Mazda	3	2.0 Skyactiv-g M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Jan 2020	-	2024-03-01	139267
Hyundai	Sonata viii	2.5 MPI	Stufenheck	Frontantrieb	Benzin	132	179	Jan 2020	-	2024-03-01	139268
Hyundai	Sonata viii	2.0 Cvvl	Stufenheck	Frontantrieb	Benzin	110	150	Jan 2020	-	2024-03-01	139269
Audi	Q3	40 Tfsi Quattro	SUV	Allrad	Benzin	140	190	Nov 2019	Jun 2021	2025-06-01	139270
BMW	3	325 XI	Stufenheck	Allrad	Benzin	160	218	Sep 2005	Aug 2006	2024-03-01	139273
KIA	Ceed	1.0 T-gdi	Kombi	Frontantrieb	Benzin	74	101	Sep 2019	-	2024-03-01	139275
Audi	A6 c8	50 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	220	299	Nov 2019	-	2024-03-01	139279
Renault	Kangoo	1.5 DCI 80	Kasten/Großraumlimousine	Frontantrieb	Diesel	59	80	Oct 2019	-	2024-03-01	139280
Mercedes-benz	C-Klasse	C 300 DE	Stufenheck	Heckantrieb	Diesel/Elektro	225	306	May 2019	May 2021	2024-03-01	139281
Mercedes-benz	C-Klasse	C 300 E	Stufenheck	Heckantrieb	Benzin/Elektro	235	320	Jul 2019	May 2021	2024-03-01	139283
Mercedes-benz	E-Klasse	E 300 DE	Stufenheck	Heckantrieb	Diesel/Elektro	225	306	Oct 2018	Oct 2023	2024-03-01	139284
Mercedes-benz	E-Klasse	E 300 E	Stufenheck	Heckantrieb	Benzin/Elektro	235	320	Nov 2018	Oct 2023	2024-03-01	139285
Renault	Kangoo	1.6 16V Flex	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	78	106	Feb 2008	-	2024-03-01	139286
Mercedes-benz	S-Klasse	S 560 E	Stufenheck	Heckantrieb	Benzin/Elektro	350	476	Oct 2018	Jul 2020	2024-03-01	139287
KIA	Xceed	1.6 GDI Hybrid	SUV	Frontantrieb	Benzin/Elektro	104	141	Dec 2019	-	2024-03-01	139293
Rolls-royce	Wraith	V12	Coupe	Heckantrieb	Benzin	441	600	Jul 2019	-	2024-03-01	139294
KIA	Seltos	1.6 MPI	SUV	Frontantrieb	Benzin	90	122	Sep 2019	-	2024-03-01	139295
KIA	Seltos	1.6 MPI 4WD	SUV	Allrad	Benzin	89	121	Sep 2019	-	2024-03-01	139296
KIA	Seltos	2.0 MPI 4WD	SUV	Allrad	Benzin	110	150	Aug 2019	-	2024-03-01	139297
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	280	381	Nov 2006	Dec 2008	2024-03-01	139305
Renault	Kangoo	1.5 DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Oct 2019	-	2024-03-01	139307
Renault	Kangoo	1.5 DCI 115	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Oct 2019	-	2024-03-01	139308
Skoda	Kamiq	1.0 TGI CNG	SUV	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2019	-	2024-03-01	139309
Skoda	Scala	1.0 TGI CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2019	-	2024-03-01	139310
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	300	408	Aug 2009	May 2012	2024-03-01	139314
Porsche	911	3.8	Cabriolet	Heckantrieb	Benzin	300	408	Aug 2010	May 2011	2024-03-01	139321
Ford	Grand c-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	63	86	Dec 2010	Jun 2019	2024-03-01	139324
Hyundai	Venue	1.6	SUV	Frontantrieb	Benzin	90	122	Sep 2019	-	2024-03-01	139326
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	235	320	Aug 2010	May 2012	2024-03-01	139327


--- Round 1 / 首次发送 ---
更新点

* 已覆盖本批次全部 100 个输入 Ktype，共形成 103 条映射；其中 `139167`、`139284`、`139285` 因生产区间跨越外廓变化的改款节点拆分为派生行。
* 本轮完成 71 条 READY 映射，复用 31 个已有尺寸组，并首次闭合 12 个尺寸组。新增组涵盖 Panda Hybrid、F-Type P450、Captur II、Mustang Mach-E、Polestar 2、Ioniq Electric、Octavia IV Combi、Taycan 和 Sonata DN8。([汽车目录][1])
* 剩余 PENDING 主要集中在同时覆盖多个轴距、车顶或厢式/乘用外廓的输入，未创建猜测性派生行，且未填写候选 `DIMENSION_GROUP_ID`。

当前批次进度

* 输入 Ktype：100 / 100 已覆盖
* 当前映射行：103
* READY 映射：71
* PENDING 映射：32
* 已确认并被引用的尺寸组：43
* 本轮首次创建尺寸组：12
* 直接复用已有尺寸组：31
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139163	139163	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-FACELIFT-01	HIGH		READY
139167_prefl	139167	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139167_facelift	139167	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139168	139168	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH		READY
139169	139169	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH		READY
139171	139171	Kasten/Großraumlimousine	Dokker I				LOW	输入同时覆盖厢式与乘用车身，需确认是否拆分 Van/MPV。	PENDING: 混合车身边界未闭合
139172	139172	Kasten/Großraumlimousine	Dokker I				LOW	输入同时覆盖厢式与乘用车身，需确认是否拆分 Van/MPV。	PENDING: 混合车身边界未闭合
139173	139173	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
139174	139174	MPV	Caddy IV	2K	5		LOW	需确认 Alltrack 是否同时覆盖标准轴距与 Maxi 外廓。	PENDING: 轴距分支未闭合
139175	139175	MPV	Caddy IV	2K	5		LOW	需确认 Alltrack 是否同时覆盖标准轴距与 Maxi 外廓。	PENDING: 轴距分支未闭合
139176	139176	MPV	Caddy IV	2K	5		LOW	需确认 Alltrack 是否同时覆盖标准轴距与 Maxi 外廓。	PENDING: 轴距分支未闭合
139177	139177	MPV	Caddy IV	2K	5		LOW	需确认 Alltrack 是否同时覆盖标准轴距与 Maxi 外廓。	PENDING: 轴距分支未闭合
139178	139178	MPV	Caddy IV	2K	5		LOW	需确认 Alltrack 是否同时覆盖标准轴距与 Maxi 外廓。	PENDING: 轴距分支未闭合
139184	139184	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139186	139186	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139188	139188	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	HIGH		READY
139189	139189	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
139190	139190	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	HIGH		READY
139191	139191	Coupe	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	HIGH		READY
139192	139192	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
139193	139193	Coupe	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	HIGH		READY
139198	139198	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139199	139199	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139200	139200	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
139201	139201	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
139202	139202	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
139203	139203	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
139204	139204	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
139205	139205	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
139207	139207	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
139208	139208	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139209	139209	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139210	139210	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139211	139211	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139212	139212	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139215	139215	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139216	139216	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139218	139218	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139219	139219	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139220	139220	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139221	139221	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139222	139222	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139223	139223	Hatchback	Polestar 2 I		5	EU-POLESTAR-2-I-HATCHBACK-01	HIGH		READY
139226	139226	Kasten/Großraumlimousine	Proace City I	K9			LOW	需确认标准轴距/长轴距及厢式分支。	PENDING: 轴距与车身分支未闭合
139227	139227	Kasten/Großraumlimousine	Proace City I	K9			LOW	需确认标准轴距/长轴距及厢式分支。	PENDING: 轴距与车身分支未闭合
139228	139228	Kasten/Großraumlimousine	Proace City I	K9			LOW	需确认标准轴距/长轴距及厢式分支。	PENDING: 轴距与车身分支未闭合
139229	139229	Kasten/Großraumlimousine	Proace City I	K9			LOW	需确认标准轴距/长轴距及厢式分支。	PENDING: 轴距与车身分支未闭合
139230	139230	Kasten/Großraumlimousine	Proace City I	K9			LOW	需确认标准轴距/长轴距及厢式分支。	PENDING: 轴距与车身分支未闭合
139234	139234	MPV	Proace City Verso I	K9	5		LOW	需确认标准轴距/长轴距乘用分支。	PENDING: 轴距分支未闭合
139235	139235	MPV	Proace City Verso I	K9	5		LOW	需确认标准轴距/长轴距乘用分支。	PENDING: 轴距分支未闭合
139236	139236	MPV	Proace City Verso I	K9	5		LOW	需确认标准轴距/长轴距乘用分支。	PENDING: 轴距分支未闭合
139238	139238	MPV	Proace City Verso I	K9	5		LOW	需确认标准轴距/长轴距乘用分支。	PENDING: 轴距分支未闭合
139239	139239	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-AE-HATCHBACK-FACELIFT-ELECTRIC-01	HIGH		READY
139240	139240	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
139241	139241	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH		READY
139242	139242	Wagon	9-3 II	YS3F	5		MEDIUM	9-3X 抬高车身与外部护板需单独建组。	PENDING: 专属外廓尺寸组未闭合
139248	139248	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139249	139249	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139250	139250	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139254	139254	MPV	Ducato II	244			LOW	Bus 车身存在多轴距/车顶组合，需确认完整分支。	PENDING: 多外廓分支未闭合
139255	139255	Van	Ducato II	244			LOW	Kasten 车身存在多轴距/车顶组合，需确认完整分支。	PENDING: 多外廓分支未闭合
139256	139256	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-4S-SEDAN-01	HIGH		READY
139257	139257	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-TURBO-SEDAN-01	HIGH		READY
139258	139258	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-TURBO-S-SEDAN-01	HIGH		READY
139259	139259	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
139260	139260	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
139261	139261	SUV	T-Cross I	C1	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
139262	139262	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
139263	139263	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
139264	139264	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
139265	139265	Sedan	5 Series E60	E60	4		MEDIUM	改款前 E60 需建立独立尺寸组，不能直接复用 facelift 组。	PENDING: 改款前尺寸组未闭合
139266	139266	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
139267	139267	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
139268	139268	Sedan	Sonata VIII	DN8	4	EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	HIGH		READY
139269	139269	Sedan	Sonata VIII	DN8	4	EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	HIGH		READY
139270	139270	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
139273	139273	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH		READY
139275	139275	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139279	139279	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
139280	139280	Kasten/Großraumlimousine	Kangoo II	X61			LOW	输入同时覆盖厢式/乘用及短轴/长轴，需完整拆分。	PENDING: 车身与轴距分支未闭合
139281	139281	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
139283	139283	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
139284_prefl	139284	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139284_facelift	139284	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139285_prefl	139285	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139285_facelift	139285	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139286	139286	Kasten/Großraumlimousine	Kangoo I	KC			LOW	Flex 版本对应第一代车身且输入混合厢式/乘用，需单独闭合。	PENDING: 代际与混合车身未闭合
139287	139287	Sedan	S-Class W222	V222	4		MEDIUM	S 560 e 长轴 facelift 外廓需单独建组。	PENDING: 专属长轴尺寸组未闭合
139293	139293	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH		READY
139294	139294	Coupe	Wraith I	RR5	2		MEDIUM	Wraith 外廓尺寸组尚未闭合。	PENDING: 尺寸组未闭合
139295	139295	SUV	Seltos I	SP2	5		MEDIUM	前驱版本高度需与既有 4WD 组分开核对。	PENDING: 前驱尺寸组未闭合
139296	139296	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH		READY
139297	139297	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH		READY
139305	139305	Targa	911 997.1	997	2		MEDIUM	Targa 4S 改款前宽体外廓需单独建组。	PENDING: 尺寸组未闭合
139307	139307	Kasten/Großraumlimousine	Kangoo II	X61			LOW	输入同时覆盖厢式/乘用及短轴/长轴，需完整拆分。	PENDING: 车身与轴距分支未闭合
139308	139308	Kasten/Großraumlimousine	Kangoo II	X61			LOW	输入同时覆盖厢式/乘用及短轴/长轴，需完整拆分。	PENDING: 车身与轴距分支未闭合
139309	139309	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
139310	139310	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
139314	139314	Targa	911 997.2	997	2		MEDIUM	Targa 4S 改款后宽体外廓需单独建组。	PENDING: 尺寸组未闭合
139321	139321	Convertible	911 997.2	997	2		MEDIUM	3.8 Cabriolet 改款后普通车身需单独建组。	PENDING: 尺寸组未闭合
139324	139324	MPV	Grand C-Max II	C344	5		MEDIUM	生产区间跨 facelift，需确认前后外廓是否拆分。	PENDING: 改款边界未闭合
139326	139326	SUV	Venue I	QX	5		MEDIUM	Venue 尺寸组尚未闭合。	PENDING: 尺寸组未闭合
139327	139327	Convertible	Boxster 987.2	987.2	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-III-319-HATCHBACK-FACELIFT-01	3653	1643	1551	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2971340/fiat_panda_hybrid.html
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	4470	1923	1307	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-convertible-facelift-2020-5.0-v8-450hp-awd-quickshift-38191
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	4470	1923	1311	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-coupe-facelift-2020-5.0-v8-450hp-quickshift-38186
EU-RENAULT-CAPTUR-II-HJB-SUV-01	4227	1797	1576	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2987615/renault_captur_tce_130.html
EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	4713	1881	1624	Auto-Data	https://www.auto-data.net/en/ford-mustang-mach-e-standard-range-75.7-kwh-269hp-38063
EU-POLESTAR-2-I-HATCHBACK-01	4606	1859	1479	Auto-Data	https://www.auto-data.net/en/polestar-2-78-kwh-408hp-long-range-dual-motor-awd-36263
EU-HYUNDAI-IONIQ-I-AE-HATCHBACK-FACELIFT-ELECTRIC-01	4470	1820	1475	Auto-Data	https://www.auto-data.net/en/hyundai-ioniq-facelift-2019-40.4-kwh-136hp-electric-37746
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/3148310/skoda_octavia_combi_1_5_tsi_act_150.html
EU-PORSCHE-TAYCAN-I-Y1A-4S-SEDAN-01	4963	1966	1379	EV Database	https://ev-database.org/car/1237/Porsche-Taycan-4S
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-SEDAN-01	4963	1966	1381	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2909915/porsche_taycan_turbo.html
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-S-SEDAN-01	4963	1966	1378	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2909930/porsche_taycan_turbo_s.html
EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	4900	1860	1445	Hyundai Sonata 2020 owner manual (Carmanualsonline mirror)	https://www.carmanualsonline.info/hyundai-sonata-2020-owner-s-manual/2
```

下一步优先处理

1. 按共用物理车身一次性闭合 Proace City / Verso 的标准轴距与长轴距分支，预计消除 9 条 PENDING。
2. 核对 Caddy Alltrack IV 是否实际覆盖 Maxi，并批量处理 5 个 Ktype。
3. 联合处理 Kangoo I、Kangoo II、Dokker 和 Ducato 的厢式/乘用、轴距与车顶组合，避免逐 Ktype 重复抓取。
4. 最后闭合 9-3X、E60 改款前、S 560 e 长轴、Wraith、Seltos 前驱、911 997 三种车身、Grand C-Max 和 Venue 等单车型尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2020/2971340/fiat_panda_hybrid.html?utm_source=chatgpt.com "2020 Fiat Panda 1.0 GSE Hybrid Specs Review (51.5 kW / 70 PS / 69 hp) (since July 2020 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已按尺寸组聚类闭合 Dokker、Caddy Alltrack IV、Proace City/Verso 与 Kangoo II；确认 Caddy Alltrack 本批版本为短轴外廓，并完成 Proace City、Kangoo 的厢式/乘用及长短轴拆分。
* 同时补齐 Saab 9-3X、BMW E60 改款前、Rolls-Royce Wraith、Kia Seltos 前驱和 Hyundai Venue 尺寸组。([汽车数据网][1])
* 本轮新增 51 条 READY 映射，首次创建 12 个尺寸组；既有 Dokker MPV、Kangoo MPV 和 Kangoo 短轴厢式组直接复用，未重复输出。

## 当前批次进度

* 输入 Ktype：100 / 100 已覆盖
* 当前映射行：130
* READY 映射：122
* PENDING 映射：8
* 已确认并被引用的尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139171_van	139171	Van	Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	输入合并厢式/乘用车身，拆分厢式外廓。	READY
139171_mpv	139171	MPV	Dokker I	F67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	输入合并厢式/乘用车身，拆分乘用外廓。	READY
139172_van	139172	Van	Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	输入合并厢式/乘用车身，拆分厢式外廓。	READY
139172_mpv	139172	MPV	Dokker I	F67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	输入合并厢式/乘用车身，拆分乘用外廓。	READY
139174	139174	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139175	139175	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139176	139176	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139177	139177	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139178	139178	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139226_van_swb	139226	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139226_van_lwb	139226	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139226_mpv_swb	139226	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139226_mpv_lwb	139226	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139227_van_swb	139227	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139227_van_lwb	139227	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139227_mpv_swb	139227	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139227_mpv_lwb	139227	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139228	139228	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	HIGH	75 hp版本仅命中短轴厢式外廓。	READY
139229_van_swb	139229	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139229_van_lwb	139229	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139229_mpv_swb	139229	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139229_mpv_lwb	139229	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139230_van_swb	139230	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139230_van_lwb	139230	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139230_mpv_swb	139230	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139230_mpv_lwb	139230	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139234_swb	139234	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139234_lwb	139234	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139235_swb	139235	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139235_lwb	139235	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139236_swb	139236	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139236_lwb	139236	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139238_swb	139238	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139238_lwb	139238	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139242	139242	Wagon	9-3X II	YS3F	5	EU-SAAB-9-3X-II-YS3F-WAGON-XWD-01	MEDIUM	9-3X专属抬高外廓。	READY
139265	139265	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-PREFL-01	HIGH		READY
139280_van_swb	139280	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139280_van_lwb	139280	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139280_mpv_swb	139280	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139280_mpv_lwb	139280	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139294	139294	Coupe	Wraith I	RR5	2	EU-ROLLS-ROYCE-WRAITH-I-RR5-COUPE-01	HIGH		READY
139295	139295	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-FWD-01	HIGH		READY
139307_van_swb	139307	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139307_van_lwb	139307	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139307_mpv_swb	139307	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139307_mpv_lwb	139307	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139308_van_swb	139308	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139308_van_lwb	139308	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139308_mpv_swb	139308	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139308_mpv_lwb	139308	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139326	139326	SUV	Venue I	QX	5	EU-HYUNDAI-VENUE-I-QX-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-DOKKER-I-F67-VAN-01	4363	1751	1809	Auto-Data	https://www.auto-data.net/en/dacia-dokker-model-1998
EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	4430	1793	1824	Volkswagen Caddy Trendline and Alltrack official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	4403	1848	1880	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-l1-generation-9202
EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	4753	1848	1812	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-l2-generation-9203
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	4403	1848	1800	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-verso-l1-generation-9207
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	4753	1848	1810	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-verso-l2-generation-9208
EU-SAAB-9-3X-II-YS3F-WAGON-XWD-01	4690	1802	1574	Auto-Data	https://www.auto-data.net/en/saab-9-3x-ii-2.0t-210hp-xwd-sentronic-54615
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/278660/bmw_525i.html
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	4666	1829	1810	Renault Kangoo Van official brochure	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf
EU-ROLLS-ROYCE-WRAITH-I-RR5-COUPE-01	5285	1947	1507	Carsales	https://www.carsales.com.au/research/rolls-royce/wraith/2019/
EU-KIA-SELTOS-I-SP2-SUV-FWD-01	4370	1800	1615	Practical Motoring	https://practicalmotoring.com.au/car-reviews/2019-kia-seltos-review-australia/
EU-HYUNDAI-VENUE-I-QX-SUV-01	4040	1770	1592	Carsales	https://www.carsales.com.au/research/hyundai/venue/2019/
```

## 下一步优先处理

1. 闭合 Ducato II 244 Bus 与 Kasten 的轴距、车顶组合。
2. 拆分 Kangoo I 厢式与乘用外廓。
3. 补齐 S 560 e 长轴 facelift 尺寸组。
4. 集中闭合 Porsche 911 997.1 Targa 4S、997.2 Targa 4S 与 997.2 Cabriolet。
5. 核对 Grand C-Max 改款前后外廓，消除最后一组改款边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/saab-9-3x-ii-2.0t-210hp-xwd-sentronic-54615?utm_source=chatgpt.com "Saab 9-3X II 2.0T (210 Hp) XWD Sentronic"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Fiat Ducato 244 Bus 的两种已确认物理外廓：标准顶与高顶；Ktype `139254` 已拆分为两条 READY 映射。([Engine In Detail][1])
* 修正 `139286` 的代际归属：该记录对应 Kangoo II Express `FW01`，而非 Kangoo I，并建立 Phase I 短轴厢式尺寸组。
* 闭合 Mercedes-Benz S 560 e 长轴版、三种 Porsche 911 997 分支以及 Ford Grand C-Max 改款前外廓。([汽车目录][2])
* 当前仅剩 Ktype `139255`：Fiat Ducato 244 Van 2.0 LPG。现有资料只能确认该动力对应多个厢式车身候选，尚未闭合各轴距和车顶组合，因此未创建猜测性派生行。

## 2. 当前批次进度

* 输入 Ktype：100 / 100 已覆盖
* 当前映射行：131
* READY 映射：130
* PENDING 映射：1
* 已确认并被引用的尺寸组：63
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139254_l2h1	139254	MPV	Ducato II	244	4	EU-FIAT-DUCATO-II-244-BUS-L2H1-01	HIGH	Ktype覆盖标准顶 Bus 外廓。	READY
139254_l2h2	139254	MPV	Ducato II	244	4	EU-FIAT-DUCATO-II-244-BUS-L2H2-01	HIGH	Ktype覆盖高顶 Bus 外廓。	READY
139286	139286	Van	Kangoo II	FW01		EU-RENAULT-KANGOO-II-X61-PHASE-I-VAN-SWB-01	HIGH	确认对应 Kangoo II Express FW01。	READY
139287	139287	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	HIGH	S 560 e长轴物理外廓。	READY
139305	139305	Targa	911 997.1	997	2	EU-PORSCHE-911-997-1-TARGA-4S-01	HIGH	997.1 Targa 4S宽体外廓。	READY
139314	139314	Targa	911 997.2	997	2	EU-PORSCHE-911-997-2-TARGA-4S-01	HIGH	997.2 Targa 4S宽体外廓。	READY
139321	139321	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	MEDIUM	300 kW版本对应 Carrera GTS Cabriolet外廓。	READY
139324	139324	MPV	Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-C344-MPV-PREFL-01	HIGH	XTDA 1.6 Ti对应改款前外廓。	READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-244-BUS-L2H1-01	5099	2024	2125	EngineInDetail Fiat Ducato Estate 15 long	https://www.engineindetail.com/pa/fiat-ducato-estate-wagon-15-long-2003
EU-FIAT-DUCATO-II-244-BUS-L2H2-01	5099	2024	2470	EngineInDetail Fiat Ducato Estate 15 High roof medium	https://www.engineindetail.com/pa/fiat-ducato-estate-wagon-15-high-roof-medium-2003
EU-RENAULT-KANGOO-II-X61-PHASE-I-VAN-SWB-01	4213	1829	1844	Auto-Data Renault Kangoo II Express 1.6 16V	https://www.auto-data.net/en/renault-kangoo-ii-express-1.6-16v-105hp-40616
EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	5255	1905	1503	Automobile-Catalog Mercedes-Benz S 560 e Lang	https://www.automobile-catalog.com/car/2018/2968670/mercedes-benz_s_560_e_lang.html
EU-PORSCHE-911-997-1-TARGA-4S-01	4427	1852	1300	Porsche 911 997 official brochure (mirror)	https://mrsportscars.com/wp-content/uploads/2016/08/Porsche-911-997-Series-Full-Brochure.pdf
EU-PORSCHE-911-997-2-TARGA-4S-01	4435	1852	1300	Automobile-Catalog Porsche 911 Targa 4S PDK	https://www.automobile-catalog.com/car/2010/2868485/porsche_911_targa_4s_pdk.html
EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	4435	1852	1300	Automobile-Catalog Porsche 911 Carrera GTS Cabriolet PDK	https://www.automobile-catalog.com/car/2011/2868695/porsche_911_carrera_gts_cabriolet_pdk.html
EU-FORD-GRAND-C-MAX-II-C344-MPV-PREFL-01	4520	1828	1684	Ford C-Max and Grand C-Max official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf
```

## 5. 下一步优先处理

1. 仅处理 Ktype `139255`，确定 Ducato 244 Van 2.0 LPG 实际覆盖的轴距与车顶组合。
2. 闭合后立即执行一次机械检查，并输出两张最终完整 TSV及指定 sandbox 下载链接，不再重新核验本轮已经确认的 63 个尺寸组。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/fiat-ducato-estate-wagon-15-long-2003 "Fiat Ducato Estate (Wagon) 15 long 2003 - Specs, Review & Tests"
[2]: https://www.automobile-catalog.com/car/2018/2968670/mercedes-benz_s_560_e_lang.html?utm_source=chatgpt.com "2018 Mercedes-Benz S 560 e Lang Specs Review ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4701-4800_ktype_dimension_mapping_final.tsv
- all_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合最后一个阻塞项 `139255`。Fiat 官方手册确认 2.0 汽油/LPG 厢式车包含中轴高顶、中轴超高顶、长轴高顶、长轴超高顶四个物理分支，对应 `244CTMNB AG/BG` 与 `244CTMNC AG/BG`；Fiat eLearn 尺寸表闭合四组三维。
* 已完成一次机械收尾：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 均唯一，全部映射引用闭合，尺寸及来源字段完整，不存在孤立尺寸组或 `PENDING`。

## 当前批次进度

* 输入 Ktype：100 / 100
* 最终映射行：134
* READY：134
* PENDING：0
* DIMENSION_GROUP：70
* 机械校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139163	139163	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-FACELIFT-01	HIGH		READY
139167_prefl	139167	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139167_facelift	139167	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139168	139168	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH		READY
139169	139169	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH		READY
139171_van	139171	Van	Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	输入合并厢式/乘用车身，拆分厢式外廓。	READY
139171_mpv	139171	MPV	Dokker I	F67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	输入合并厢式/乘用车身，拆分乘用外廓。	READY
139172_van	139172	Van	Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	输入合并厢式/乘用车身，拆分厢式外廓。	READY
139172_mpv	139172	MPV	Dokker I	F67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	输入合并厢式/乘用车身，拆分乘用外廓。	READY
139173	139173	MPV	Dokker I	F67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
139174	139174	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139175	139175	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139176	139176	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139177	139177	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139178	139178	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	HIGH		READY
139184	139184	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139186	139186	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139188	139188	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	HIGH		READY
139189	139189	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
139190	139190	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	HIGH		READY
139191	139191	Coupe	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	HIGH		READY
139192	139192	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
139193	139193	Coupe	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	HIGH		READY
139198	139198	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139199	139199	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139200	139200	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
139201	139201	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
139202	139202	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
139203	139203	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
139204	139204	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
139205	139205	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
139207	139207	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
139208	139208	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139209	139209	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139210	139210	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139211	139211	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139212	139212	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH		READY
139215	139215	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
139216	139216	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
139218	139218	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139219	139219	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139220	139220	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139221	139221	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139222	139222	SUV	Mustang Mach-E I	CX727	5	EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	HIGH		READY
139223	139223	Hatchback	Polestar 2 I		5	EU-POLESTAR-2-I-HATCHBACK-01	HIGH		READY
139226_van_swb	139226	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139226_van_lwb	139226	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139226_mpv_swb	139226	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139226_mpv_lwb	139226	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139227_van_swb	139227	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139227_van_lwb	139227	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139227_mpv_swb	139227	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139227_mpv_lwb	139227	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139228	139228	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	HIGH	75 hp版本仅命中短轴厢式外廓。	READY
139229_van_swb	139229	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139229_van_lwb	139229	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139229_mpv_swb	139229	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139229_mpv_lwb	139229	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139230_van_swb	139230	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139230_van_lwb	139230	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139230_mpv_swb	139230	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139230_mpv_lwb	139230	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139234_swb	139234	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139234_lwb	139234	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139235_swb	139235	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139235_lwb	139235	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139236_swb	139236	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139236_lwb	139236	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139238_swb	139238	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	HIGH	Verso覆盖短轴外廓。	READY
139238_lwb	139238	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	HIGH	Verso覆盖长轴外廓。	READY
139239	139239	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-AE-HATCHBACK-FACELIFT-ELECTRIC-01	HIGH		READY
139240	139240	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
139241	139241	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH		READY
139242	139242	Wagon	9-3X II	YS3F	5	EU-SAAB-9-3X-II-YS3F-WAGON-XWD-01	MEDIUM	9-3X专属抬高外廓。	READY
139248	139248	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139249	139249	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139250	139250	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
139254_l2h1	139254	MPV	Ducato II	244	4	EU-FIAT-DUCATO-II-244-BUS-L2H1-01	HIGH	Ktype覆盖标准顶 Bus 外廓。	READY
139254_l2h2	139254	MPV	Ducato II	244	4	EU-FIAT-DUCATO-II-244-BUS-L2H2-01	HIGH	Ktype覆盖高顶 Bus 外廓。	READY
139255_mwb_highroof	139255	Van	Ducato II	244CTMNB		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-LPG-01	HIGH	中轴高顶汽油/LPG厢式外廓。	READY
139255_mwb_extrahigh	139255	Van	Ducato II	244CTMNB		EU-FIAT-DUCATO-II-244-VAN-MWB-EXTRAHIGH-LPG-01	HIGH	中轴超高顶汽油/LPG厢式外廓。	READY
139255_lwb_highroof	139255	Van	Ducato II	244CTMNC		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-LPG-01	HIGH	长轴高顶汽油/LPG厢式外廓。	READY
139255_lwb_extrahigh	139255	Van	Ducato II	244CTMNC		EU-FIAT-DUCATO-II-244-VAN-LWB-EXTRAHIGH-LPG-01	HIGH	长轴超高顶汽油/LPG厢式外廓。	READY
139256	139256	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-4S-SEDAN-01	HIGH		READY
139257	139257	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-TURBO-SEDAN-01	HIGH		READY
139258	139258	Sedan	Taycan I	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-TURBO-S-SEDAN-01	HIGH		READY
139259	139259	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
139260	139260	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
139261	139261	SUV	T-Cross I	C1	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
139262	139262	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
139263	139263	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
139264	139264	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
139265	139265	Sedan	5 Series E60	E60	4	EU-BMW-5-E60-SEDAN-PREFL-01	HIGH		READY
139266	139266	Sedan	A8 D5	4N2	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
139267	139267	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
139268	139268	Sedan	Sonata VIII	DN8	4	EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	HIGH		READY
139269	139269	Sedan	Sonata VIII	DN8	4	EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	HIGH		READY
139270	139270	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
139273	139273	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH		READY
139275	139275	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139279	139279	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
139280_van_swb	139280	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139280_van_lwb	139280	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139280_mpv_swb	139280	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139280_mpv_lwb	139280	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139281	139281	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
139283	139283	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
139284_prefl	139284	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139284_facelift	139284	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139285_prefl	139285	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越改款，拆分改款前外廓。	READY
139285_facelift	139285	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，拆分改款后外廓。	READY
139286	139286	Van	Kangoo II	FW01		EU-RENAULT-KANGOO-II-X61-PHASE-I-VAN-SWB-01	HIGH	确认对应 Kangoo II Express FW01。	READY
139287	139287	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	HIGH	S 560 e长轴物理外廓。	READY
139293	139293	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH		READY
139294	139294	Coupe	Wraith I	RR5	2	EU-ROLLS-ROYCE-WRAITH-I-RR5-COUPE-01	HIGH		READY
139295	139295	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-FWD-01	HIGH		READY
139296	139296	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH		READY
139297	139297	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH		READY
139305	139305	Targa	911 997.1	997	2	EU-PORSCHE-911-997-1-TARGA-4S-01	HIGH	997.1 Targa 4S宽体外廓。	READY
139307_van_swb	139307	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139307_van_lwb	139307	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139307_mpv_swb	139307	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139307_mpv_lwb	139307	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139308_van_swb	139308	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴厢式外廓。	READY
139308_van_lwb	139308	Van	Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴厢式外廓。	READY
139308_mpv_swb	139308	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	MEDIUM	输入合并厢式/乘用车身，拆分短轴乘用外廓。	READY
139308_mpv_lwb	139308	MPV	Kangoo II	X61	5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	MEDIUM	输入合并厢式/乘用车身，拆分长轴乘用外廓。	READY
139309	139309	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
139310	139310	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
139314	139314	Targa	911 997.2	997	2	EU-PORSCHE-911-997-2-TARGA-4S-01	HIGH	997.2 Targa 4S宽体外廓。	READY
139321	139321	Convertible	911 997.2	997	2	EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	MEDIUM	300 kW版本对应 Carrera GTS Cabriolet外廓。	READY
139324	139324	MPV	Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-C344-MPV-PREFL-01	HIGH	XTDA 1.6 Ti对应改款前外廓。	READY
139326	139326	SUV	Venue I	QX	5	EU-HYUNDAI-VENUE-I-QX-SUV-01	HIGH		READY
139327	139327	Convertible	Boxster 987.2	987.2	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4701-4800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-III-319-HATCHBACK-FACELIFT-01	3653	1643	1551	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2971340/fiat_panda_hybrid.html
EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	4770	1815	1470	Hyundai i40 official specifications	https://www.hyundai.news/eu/models/i40/press-kit/i40-technical-specifications.html
EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	4775	1815	1470	Hyundai i40 official specifications	https://www.hyundai.news/eu/models/i40/press-kit/i40-technical-specifications.html
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470	Hyundai i40 official specifications	https://www.hyundai.news/eu/models/i40/press-kit/i40-technical-specifications.html
EU-DACIA-DOKKER-I-F67-VAN-01	4363	1751	1809	Auto-Data	https://www.auto-data.net/en/dacia-dokker-model-1998
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Dacia Dokker official brochure	https://www.dacia.ie/CountriesData/Ireland/images/Brochures/Dokker-brochure.pdf
EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	4430	1793	1824	Volkswagen Caddy Trendline and Alltrack official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan official technical data	https://www.press.bmwgroup.com/global/article/detail/T0285543EN/the-all-new-bmw-3-series-sedan
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-P450-01	4470	1923	1307	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-convertible-facelift-2020-5.0-v8-450hp-awd-quickshift-38191
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan official technical data	https://www.press.bmwgroup.com/global/article/detail/T0285543EN/the-all-new-bmw-3-series-sedan
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-P450-01	4470	1923	1311	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-coupe-facelift-2020-5.0-v8-450hp-quickshift-38186
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	BMW 3 Series Touring official technical data	https://www.press.bmwgroup.com/global/article/detail/T0297384EN/the-all-new-bmw-3-series-touring
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445	BMW 3 Series Touring official technical data	https://www.press.bmwgroup.com/global/article/detail/T0297384EN/the-all-new-bmw-3-series-touring
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW X3 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0268062EN/the-new-bmw-x3
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	BMW X4 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0280098EN/the-all-new-bmw-x4
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	BMW 1 Series official technical data	https://www.press.bmwgroup.com/global/article/detail/T0296727EN/the-all-new-bmw-1-series
EU-RENAULT-CAPTUR-II-HJB-SUV-01	4227	1797	1576	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/2987615/renault_captur_tce_130.html
EU-FORD-MUSTANG-MACH-E-I-CX727-SUV-01	4713	1881	1624	Auto-Data	https://www.auto-data.net/en/ford-mustang-mach-e-standard-range-75.7-kwh-269hp-38063
EU-POLESTAR-2-I-HATCHBACK-01	4606	1859	1479	Auto-Data	https://www.auto-data.net/en/polestar-2-78-kwh-408hp-long-range-dual-motor-awd-36263
EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	4403	1848	1880	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-l1-generation-9202
EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	4753	1848	1812	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-l2-generation-9203
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	4403	1848	1800	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-verso-l1-generation-9207
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	4753	1848	1810	Auto-Data	https://www.auto-data.net/en/toyota-proace-city-verso-l2-generation-9208
EU-HYUNDAI-IONIQ-I-AE-HATCHBACK-FACELIFT-ELECTRIC-01	4470	1820	1475	Auto-Data	https://www.auto-data.net/en/hyundai-ioniq-facelift-2019-40.4-kwh-136hp-electric-37746
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Audi A5 official technical data	https://www.audi-mediacenter.com/en/audi-a5-coupe-14934
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a5-sportback-14935
EU-SAAB-9-3X-II-YS3F-WAGON-XWD-01	4690	1802	1574	Auto-Data	https://www.auto-data.net/en/saab-9-3x-ii-2.0t-210hp-xwd-sentronic-54615
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2020/3148310/skoda_octavia_combi_1_5_tsi_act_150.html
EU-FIAT-DUCATO-II-244-BUS-L2H1-01	5099	2024	2125	EngineInDetail Fiat Ducato Estate 15 long	https://www.engineindetail.com/pa/fiat-ducato-estate-wagon-15-long-2003
EU-FIAT-DUCATO-II-244-BUS-L2H2-01	5099	2024	2470	EngineInDetail Fiat Ducato Estate 15 High roof medium	https://www.engineindetail.com/pa/fiat-ducato-estate-wagon-15-high-roof-medium-2003
EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-LPG-01	5099	2024	2480	Fiat Ducato 244 official owner handbook; Fiat eLearn vehicle dimensions	https://www.fiatcesaro.it/editorcms/77_244_DUCATO_603_45_860_IT_03_04_05_L_LG.pdf;https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-II-244-VAN-MWB-EXTRAHIGH-LPG-01	5099	2024	2735	Fiat Ducato 244 official owner handbook; Fiat eLearn vehicle dimensions	https://www.fiatcesaro.it/editorcms/77_244_DUCATO_603_45_860_IT_03_04_05_L_LG.pdf;https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-LPG-01	5599	2024	2480	Fiat Ducato 244 official owner handbook; Fiat eLearn vehicle dimensions	https://www.fiatcesaro.it/editorcms/77_244_DUCATO_603_45_860_IT_03_04_05_L_LG.pdf;https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-II-244-VAN-LWB-EXTRAHIGH-LPG-01	5599	2024	2860	Fiat Ducato 244 official owner handbook; Fiat eLearn vehicle dimensions	https://www.fiatcesaro.it/editorcms/77_244_DUCATO_603_45_860_IT_03_04_05_L_LG.pdf;https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-PORSCHE-TAYCAN-I-Y1A-4S-SEDAN-01	4963	1966	1379	EV Database	https://ev-database.org/car/1237/Porsche-Taycan-4S
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-SEDAN-01	4963	1966	1381	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2909915/porsche_taycan_turbo.html
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-S-SEDAN-01	4963	1966	1378	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2909930/porsche_taycan_turbo_s.html
EU-MAZDA-CX-30-DM-SUV-01	4395	1795	1540	Mazda CX-30 official specifications	https://www.mazda-press.com/eu/news/2019/mazda-cx-30/
EU-VW-T-CROSS-I-C1-SUV-PREFL-01	4108	1760	1584	Volkswagen T-Cross official technical data	https://www.volkswagen-newsroom.com/en/t-cross-14932/technical-data
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo XC60 official specifications	https://www.media.volvocars.com/global/en-gb/models/xc60/2020/specifications
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo XC90 official specifications	https://www.media.volvocars.com/global/en-gb/models/xc90/2020/specifications
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/278660/bmw_525i.html
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473	Audi A8 official technical data	https://www.audi-mediacenter.com/en/audi-a8-15061
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Mazda3 official specifications	https://www.mazda-press.com/eu/news/2019/all-new-mazda3/
EU-HYUNDAI-SONATA-VIII-DN8-SEDAN-01	4900	1860	1445	Hyundai Sonata 2020 owner manual (Carmanualsonline mirror)	https://www.carmanualsonline.info/hyundai-sonata-2020-owner-s-manual/2
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Audi Q3 official technical data	https://www.audi-mediacenter.com/en/audi-q3-14877
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421	BMW 3 Series E90 official brochure	https://www.auto-brochures.com/makes/BMW/3%20Series/BMW_US%203Series_2006.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed Sportswagon official specifications	https://press.kia.com/eu/en/home/models/ceed/ceed-sportswagon.html
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi A6 Sedan official technical data	https://www.audi-mediacenter.com/en/audi-a6-sedan-14821
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	4282	1829	1805	Renault Kangoo Van official brochure	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-LWB-01	4666	1829	1810	Renault Kangoo Van official brochure	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801	Renault Kangoo official brochure	https://www.press.renault.co.uk/assets/documents/original/10707-KangooBrochureJuly2017.pdf
EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	4666	1829	1802	Renault Kangoo official brochure	https://www.press.renault.co.uk/assets/documents/original/10707-KangooBrochureJuly2017.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Mercedes-Benz C-Class official technical data	https://media.mercedes-benz.com/article/7a2a9c68-1155-4fa0-8aec-0e2826a89cd0
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Mercedes-Benz E-Class official technical data	https://media.mercedes-benz.com/article/9c4933c9-2774-4aea-80e4-785b44bd959c
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Mercedes-Benz E-Class official technical data	https://media.mercedes-benz.com/article/672184a2-c654-4aa9-94a9-44af929680e4
EU-RENAULT-KANGOO-II-X61-PHASE-I-VAN-SWB-01	4213	1829	1844	Auto-Data Renault Kangoo II Express 1.6 16V	https://www.auto-data.net/en/renault-kangoo-ii-express-1.6-16v-105hp-40616
EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	5255	1905	1503	Automobile-Catalog Mercedes-Benz S 560 e Lang	https://www.automobile-catalog.com/car/2018/2968670/mercedes-benz_s_560_e_lang.html
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495	Kia XCeed official specifications	https://press.kia.com/eu/en/home/models/xceed/xceed.html
EU-ROLLS-ROYCE-WRAITH-I-RR5-COUPE-01	5285	1947	1507	Carsales	https://www.carsales.com.au/research/rolls-royce/wraith/2019/
EU-KIA-SELTOS-I-SP2-SUV-FWD-01	4370	1800	1615	Practical Motoring	https://practicalmotoring.com.au/car-reviews/2019-kia-seltos-review-australia/
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620	Kia Seltos official specifications	https://www.kia.com/content/dam/kwcms/au/en/files/vehicle-specification/seltos/kia-seltos-specification.pdf
EU-PORSCHE-911-997-1-TARGA-4S-01	4427	1852	1300	Porsche 911 997 official brochure (mirror)	https://mrsportscars.com/wp-content/uploads/2016/08/Porsche-911-997-Series-Full-Brochure.pdf
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531	Skoda Kamiq official technical data	https://www.skoda-storyboard.com/en/press-kits/skoda-kamiq-press-kit/technical-data/
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471	Skoda Scala official technical data	https://www.skoda-storyboard.com/en/press-kits/skoda-scala-press-kit/technical-data/
EU-PORSCHE-911-997-2-TARGA-4S-01	4435	1852	1300	Automobile-Catalog Porsche 911 Targa 4S PDK	https://www.automobile-catalog.com/car/2010/2868485/porsche_911_targa_4s_pdk.html
EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	4435	1852	1300	Automobile-Catalog Porsche 911 Carrera GTS Cabriolet PDK	https://www.automobile-catalog.com/car/2011/2868695/porsche_911_carrera_gts_cabriolet_pdk.html
EU-FORD-GRAND-C-MAX-II-C344-MPV-PREFL-01	4520	1828	1684	Ford C-Max and Grand C-Max official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf
EU-HYUNDAI-VENUE-I-QX-SUV-01	4040	1770	1592	Carsales	https://www.carsales.com.au/research/hyundai/venue/2019/
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1292	Porsche Boxster 987.2 official brochure (mirror)	https://www.auto-brochures.com/makes/Porsche/Boxster/Porsche_US%20Boxster_2012.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4701-4800_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4860 行）
- 累计尺寸组：dimension_groups_final.tsv（1846 行）

