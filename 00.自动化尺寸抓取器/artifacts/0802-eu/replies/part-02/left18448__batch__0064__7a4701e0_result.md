# 任务：left18448 第 6301-6400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0064__7a4701e0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6301-6400 行

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
left18448.tsv

【当前独立任务】
left18448 第 6301-6400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2014	-	108101
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2014	-	108103
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2014	-	108105
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2017	-	128375
Ford USA	F-150	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2017	-	128377
Ford USA	F-150	6.2 4WD	Pick-up	Allrad	Benzin	Sep 2010	-	51684
Ford USA	F-150	6.2 4WD	Pick-up	Allrad	Benzin	Sep 2013	-	107127
Ford USA	F-150	6.2 SVT Raptor 4WD	Pick-up	Allrad	Benzin	Sep 2009	-	51477
Ford USA	F-150	EV Allrad	Pick-up	Allrad	Elektro	Apr 2023	-	153141
Ford USA	Flex	3.5 AWD	SUV	Allrad	Benzin	Sep 2009	-	50313
Ford USA	Mustang	3.3	Cabriolet	Heckantrieb	Benzin	Jan 1965	Dec 1970	150413
Ford USA	Mustang	3.7	Coupe	Heckantrieb	Benzin	Sep 2010	Aug 2014	57967
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	Sep 1993	May 1999	7998
Ford USA	Mustang	4.9	Coupe	Heckantrieb	Benzin	Sep 1993	Oct 1995	8000
Ford USA	Mustang	5	Coupe	Heckantrieb	Benzin	Sep 1993	Dec 1994	52839
Ford USA	Mustang	5	Coupe	Heckantrieb	Benzin	Sep 2010	-	57965
Ford USA	Mustang	5.4	Coupe	Heckantrieb	Benzin	Sep 2007	Dec 2009	108767
Ford USA	Mustang	2.3 Ecoboost	Coupe	Heckantrieb	Benzin	Jan 2015	Apr 2023	108873
Ford USA	Mustang	2.3 Ecoboost	Coupe	Heckantrieb	Benzin	Jul 2015	-	115865
Ford USA	Mustang	2.3 Ecoboost	Coupe	Heckantrieb	Benzin	Jun 2023	-	157173
Ford USA	Mustang	2.3 Ecoboost	Cabriolet	Heckantrieb	Benzin	Jun 2023	-	157194
Ford USA	Mustang	4.6 V8	Coupe	Heckantrieb	Benzin	Sep 2008	Feb 2010	57964
Ford USA	Mustang	5.0 Bullit	Coupe	Heckantrieb	Benzin	Jun 2023	-	157192
Ford USA	Mustang	5.0 Dark Horse	Coupe	Heckantrieb	Benzin	Feb 2024	-	157793
Ford USA	Mustang	5.0 GT	Coupe	Heckantrieb	Benzin	Jun 2023	-	157179
Ford USA	Mustang	5.0 GT	Coupe	Heckantrieb	Benzin	Jun 2023	-	157191
Ford USA	Mustang	5.0 GT	Coupe	Heckantrieb	Benzin	Feb 2024	-	158167
Ford USA	Mustang	5.0 GT	Cabriolet	Heckantrieb	Benzin	Feb 2024	-	158168
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	Jan 2015	Apr 2023	109565
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	Jul 2015	-	109962
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	Dec 2014	Apr 2023	121899
Ford USA	Mustang	5.2 Shelby Gt350	Coupe	Heckantrieb	Benzin	Nov 2015	-	117269
Ford USA	Mustang convertible	2.3	Cabriolet	Heckantrieb	Benzin	Nov 1987	Sep 1993	57957
Ford USA	Mustang convertible	3.7	Cabriolet	Heckantrieb	Benzin	Sep 2010	Aug 2014	57951
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	Sep 1993	Jul 1999	7999
Ford USA	Mustang convertible	4.9	Cabriolet	Heckantrieb	Benzin	Sep 1993	Dec 1995	8001
Ford USA	Mustang convertible	4.9	Cabriolet	Heckantrieb	Benzin	Nov 1987	Sep 1993	57955
Ford USA	Mustang convertible	5	Cabriolet	Heckantrieb	Benzin	Jan 2012	-	55018
Ford USA	Mustang convertible	5	Cabriolet	Heckantrieb	Benzin	Sep 2010	-	57952
Ford USA	Mustang convertible	5.8	Cabriolet	Heckantrieb	Benzin	Sep 2012	-	105930
Ford USA	Mustang convertible	2.3 Ecoboost	Cabriolet	Heckantrieb	Benzin	Jan 2015	Apr 2023	108876
Ford USA	Mustang convertible	2.3 Ecoboost	Cabriolet	Heckantrieb	Benzin	Jul 2015	Apr 2023	116599
Ford USA	Mustang convertible	3.7 V6	Cabriolet	Heckantrieb	Benzin	Feb 2014	Apr 2023	108877
Ford USA	Mustang convertible	4.6 V8	Cabriolet	Heckantrieb	Benzin	Apr 2009	Feb 2010	57950
Ford USA	Mustang convertible	5.0 V8	Cabriolet	Heckantrieb	Benzin	Jan 2015	Apr 2023	109564
Ford USA	Mustang convertible	5.0 V8	Cabriolet	Heckantrieb	Benzin	Jul 2015	Apr 2023	115872
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	Apr 2021	-	143871
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	Apr 2021	-	143876
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	Dec 2022	-	157623
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	Apr 2025	-	801866
Ford USA	Mustang mach-E	EV 4X4	Geländewagen geschlossen	Allrad	Elektro	Apr 2021	-	143870
Ford USA	Mustang mach-E	EV 4X4	Geländewagen geschlossen	Allrad	Elektro	Apr 2021	-	143872
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Apr 2021	-	143873
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Apr 2021	-	143874
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Oct 2023	-	156883
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Jun 2023	-	157624
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Apr 2025	-	801865
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	Apr 2025	-	801881
Ford USA	Mustang mach-E	EV GT 4X4	SUV	Allrad	Elektro	Nov 2021	-	146215
Ford USA	Mustang mach-E	EV GT 4X4	SUV	Allrad	Elektro	May 2024	-	800867
Ford USA	Mustang mach-E	EV GT 4X4	SUV	Allrad	Elektro	Mar 2022	-	801301
Ford USA	Ranger	2.0 Ecoblue	Pick-up	Heckantrieb	Diesel	Mar 2023	-	152212
Ford USA	Ranger	2.0 Ecoblue	Pick-up	Heckantrieb	Diesel	Nov 2022	-	800093
Ford USA	Ranger	2.0 Ecoblue	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2022	-	800094
Ford USA	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	Mar 2023	-	152213
Ford USA	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	Mar 2023	-	152273
Ford USA	Ranger	2.0 Ecoblue 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Apr 2022	-	152630
Ford USA	Ranger	2.0 Ecoblue AWD	Pick-up	Allrad	Diesel	Mar 2023	-	152202
Ford USA	Ranger	2.0 Ecoblue AWD	Pick-up	Allrad	Diesel	Mar 2023	-	152670
Ford USA	Ranger	2.0 Ecoblue Raptor 4X4	Pick-up	Allrad	Diesel	Dec 2023	-	157843
Ford USA	Ranger	2.3 Phev 4X4	Pick-up	Allrad	Benzin/Elektro	Sep 2024	-	801294
Ford USA	Ranger	3.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	Mar 2023	-	152205
Ford USA	Ranger	3.0 Ecoboost Raptor 4X4	Pick-up	Allrad	Benzin	Oct 2022	-	152214
Ford USA	Taurus	3	Stufenheck	Frontantrieb	Benzin	Sep 1995	Dec 1999	8002
Ford USA	Taurus	3	Kombi	Frontantrieb	Benzin	Sep 1996	Dec 1999	8003
Ford USA	Taurus	3	Stufenheck	Frontantrieb	Benzin	Jan 1996	Aug 1999	47261
Ford USA	Taurus	3.0 24V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Dec 1999	8004
Ford USA	Taurus	3.0 24V	Kombi	Frontantrieb	Benzin	Jun 1995	Dec 1999	8005
Ford USA	Taurus	3.0 24V	Stufenheck	Frontantrieb	Benzin	Sep 1999	Dec 2003	109826
Ford USA	Taurus	3.0 V6	Stufenheck	Frontantrieb	Benzin	Mar 1999	Dec 1999	14654
Ford USA	Taurus	3.0 V6	Kombi	Frontantrieb	Benzin	Jan 1996	Dec 1999	14655
Ford USA	Thunderbird	4.6	Coupe	Heckantrieb	Benzin	Jan 1994	Dec 1997	124766
Ford USA	Thunderbird	4.9	Coupe	Heckantrieb	Benzin	Jan 1989	Dec 1994	58103
Ford USA	Windstar	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Dec 2000	15370
Ford USA	Windstar	3.0 V6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 1995	Jun 1998	143238
Ford USA	Windstar	3.8 V6	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Jun 1998	8006
Forthing	T5 evo	1.5	SUV	Frontantrieb	Benzin	Nov 2023	-	157036
Forthing	T5 evo	LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Nov 2023	-	157037
Forthing	U-Tour	1.5	Großraumlimousine	Frontantrieb	Benzin	Nov 2023	-	157038
Forthing	U-Tour	1.5 HEV	Großraumlimousine	Frontantrieb	Benzin/Elektro	Oct 2025	-	802898
Forthing	U-Tour	LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Nov 2023	-	157039
Foton	Toano	Etoano Electric	Kasten	Heckantrieb	Elektro	Jan 2025	-	801811
Foton	Tunland	2.0 D Allrad	Pick-up	Allrad	Diesel	Feb 2026	-	146456
Foton	Tunland	2.0 G7	Pick-up	Heckantrieb	Diesel	Jan 2024	-	801495
FSO	126p	0.6	Schrägheck	Heckantrieb	Benzin	Sep 1972	Jul 1977	12919
FSO	Polonez i	1.3	Schrägheck	Heckantrieb	Benzin	Jan 1978	Dec 1980	12920
FSO	Polonez i	1.5	Schrägheck	Heckantrieb	Benzin	Jan 1978	Aug 1988	12921
FSO	Polonez i	1.5 Turbo	Schrägheck	Heckantrieb	Benzin	Jan 1978	Dec 1991	12922
GAC	Aion v	EV	SUV	Frontantrieb	Elektro	Sep 2025	-	160003
Galloper	Galloper	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Nov 1997	Aug 2002	151146


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 **Mustang Mach-E（CGW）15 个 Ktype** 的首轮聚类。普通 RWD、普通 AWD 在相同五门外廓下复用同一尺寸组；GT 因前后外饰和车高不同，独立建组。普通版尺寸采用明确区分含镜/不含镜宽度的 JATO/CarExpert 数据，并与 Ford 官方规格交叉核对。([CarExpert NZ][1])
* GT 组按同代 CGW 的 GT 专属外廓建档，三维采用 Ford 官方技术规格中的 `186.7 × 74.1 × 63.3 in` 换算值。由于当前 Ktype 属于较早年份而直接规格页为后续同代车型，映射置信度暂定 `MEDIUM`，但不存在未闭合外廓分支。
* `801865`、`801866`、`801881` 暂不强行关联。Ford 2025 规格中普通 Select 与 Premium 的高度分别为 `64.0 in` 和 `64.1 in`，而输入只标注 EV/EV 4X4，尚不能确定对应的具体高度分支。

## 当前批次进度

* 输入 Ktype：100
* 已评估：15
* READY 映射：12
* PENDING 映射：3
* 尚未展开：85
* 本轮首次确认尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143871	143871	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143876	143876	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
157623	157623	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
801866	801866	SUV	Mustang Mach-E I	CGW	5		MEDIUM	候选为CGW普通外廓；2025 Select/Premium高度分支尚未定位。	PENDING: 2025 Select/Premium外廓分支未确认
143870	143870	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143872	143872	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143873	143873	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143874	143874	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
156883	156883	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
157624	157624	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
801865	801865	SUV	Mustang Mach-E I	CGW	5		MEDIUM	候选为CGW普通外廓；2025 AWD Select/Premium高度分支尚未定位。	PENDING: 2025 AWD Select/Premium外廓分支未确认
801881	801881	SUV	Mustang Mach-E I	CGW	5		MEDIUM	候选为CGW普通外廓；2025 AWD Select/Premium高度分支尚未定位。	PENDING: 2025 AWD Select/Premium外廓分支未确认
146215	146215	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
800867	800867	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
801301	801301	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	4713	1881	1624	Ford 2021 Mustang Mach-E Technical Specifications; JATO Dynamics / CarExpert 2024 Ford Mustang Mach-E	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2021/mach-e/Mustang-Mach-E-Tech-Specs.pdf;https://www.carexpert.co.nz/ford/mustang-mach-e/2024
EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	4742	1882	1608	Ford 2025 Mustang Mach-E Technical Specifications	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025%20Ford-Mustang-Mach-E-Technical-Specifications.pdf
```

## 下一步优先处理

1. 集中闭合 Ranger 的 Single Cab、Extended Cab、Crew Cab、Cab & Chassis、Raptor 与 PHEV 外廓分支。
2. 批量处理 Mustang S550、S650，以及 Coupe、Convertible、Shelby GT350 的尺寸边界。
3. 最后处理 F-150；必须先拆清驾驶室、货斗、Raptor 和 Lightning，禁止仅按发动机直接共组。
4. 回查三个 2025 Mach-E Ktype 的具体 trim，使其落入 Select、Premium 或其他确定外廓。

推进信号：CONTINUE

[1]: https://www.carexpert.co.nz/ford/mustang-mach-e/2024?utm_source=chatgpt.com "2024 Ford Mustang Mach-E Reviews - Models & Range"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 8 个第七代 Mustang（S650）Ktype，并按物理外廓归并为普通 Fastback、Convertible、Dark Horse 三个尺寸组。EcoBoost、GT及不同功率标定未重复建组；`157192` 虽输入版本名为 `Bullit`，但仍归入普通 S650 Fastback 外廓。([autodoc.lv][1])
* 三个尺寸组统一采用不含后视镜宽度：普通 Fastback 为 `4811×1915×1397 mm`，Convertible 为 `4811×1915×1392 mm`，Dark Horse 为 `4818×1918×1402 mm`。([mustang6g.com][2])

## 当前批次进度

* 输入 Ktype：100
* 已评估：23
* READY 映射：20
* PENDING 映射：3
* 尚未展开：77
* 已确认尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
157173	157173	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
157194	157194	Convertible	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	HIGH	S650双门Convertible外廓。	READY
157192	157192	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	MEDIUM	输入版本名为Bullit；物理边界为S650双门Fastback。	READY
157793	157793	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-DARK-HORSE-01	HIGH	Dark Horse专属外廓。	READY
157179	157179	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
157191	157191	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
158167	158167	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
158168	158168	Convertible	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	HIGH	S650双门Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-S650-COUPE-01	4811	1915	1397	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/features-specs/
EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	4811	1915	1392	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Convertible Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/convertible/features-specs/
EU-FORD-USA-MUSTANG-S650-COUPE-DARK-HORSE-01	4818	1918	1402	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Dark Horse Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/dark-horse/features-specs/
```

## 下一步优先处理

1. 闭合新一代 Ranger 的 Single Cab、Super Cab、Double Cab、Chassis Cab、Raptor及PHEV分支。
2. 批量关联 S550 Mustang Coupe、Convertible和Shelby GT350。
3. 回查三个仍为 PENDING 的2025 Mustang Mach-E Ktype具体配置分支。

推进信号：CONTINUE

[1]: https://www.autodoc.lv/auto-dalas/skanas_signals_taure-10420/ford-usa/mustang/mustang-coupe-2023/157173-2-3-ecoboost-p8t?utm_source=chatgpt.com "FORD USA Mustang Mk7 Coupe (S650) 2.3 EcoBoost Skaņas ..."
[2]: https://www.mustang6g.com/forums/attachments/2024-mustang-technical-specifications-1-pdf.703774/?utm_source=chatgpt.com "2024 Mustang Technical Specifications"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 **11 个 S550 Mustang Ktype**，新增 20 条 READY 映射。普通 Coupe、Convertible 按 2015–2017 前期与 2018–2023 改款后不同外廓拆分；同一发动机 Ktype 跨越改款周期时输出 `prefl`、`facelift` 两条派生行。
* Shelby GT350 使用独立宽体外廓，不与普通 S550 Coupe 共组。Ford 官方规格确认 GT350 为 `188.9 × 75.9 × 54.2 in`。([福特媒体][1])
* 普通 S550 前期 Coupe、Convertible 长度均为 4784 mm，高度分别为 1381 mm、1394 mm；改款后官方规格为 188.5 in 长、75.4 in 不含镜宽，Fastback、Convertible 高度分别为 54.3 in、54.9 in。

## 当前批次进度

* 输入 Ktype：100
* 已评估 Ktype：34
* READY Ktype：31
* READY 映射行：40
* PENDING Ktype：3
* 尚未展开 Ktype：66
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108873_prefl	108873	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
108873_facelift	108873	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
115865_prefl	115865	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
115865_facelift	115865	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
109565_prefl	109565	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
109565_facelift	109565	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
109962_prefl	109962	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
109962_facelift	109962	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
121899_prefl	121899	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
121899_facelift	121899	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
117269	117269	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-GT350-01	HIGH	Shelby GT350专属宽体Fastback外廓。	READY
108876_prefl	108876	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
108876_facelift	108876	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
116599_prefl	116599	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
116599_facelift	116599	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
108877	108877	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	3.7 V6对应S550前期Convertible外廓。	READY
109564_prefl	109564	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
109564_facelift	109564	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
115872_prefl	115872	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
115872_facelift	115872	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	4784	1915	1381	Ford 2016 Mustang Technical Specifications; Ford Mustang Owner's Manual Coupe dimensions	https://media.ford.com/content/dam/lincolnmedia/lna/us/product/2016/2016-Ford-Mustang-Tech-Specs.pdf;https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1739779&Uid=G1739776&buildtype=web%2F1000&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=False&variantid=4230
EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	4788	1915	1379	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	4784	1915	1394	Ford 2016 Mustang Technical Specifications; Ford Mustang Owner's Manual Convertible dimensions	https://media.ford.com/content/dam/lincolnmedia/lna/us/product/2016/2016-Ford-Mustang-Tech-Specs.pdf;https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1739788&Uid=G1739786&buildtype=web%2F1000&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=False&variantid=4230
EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	4788	1915	1394	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-FORD-USA-MUSTANG-S550-COUPE-GT350-01	4798	1928	1377	Ford 2016 Shelby GT350 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/2015/08/24/gt350-gt350r-tech-specs.pdf
```

## 下一步优先处理

1. 闭合 Ranger 的 Single Cab、Super Cab、Double Cab、Chassis Cab、Raptor及PHEV物理分支。
2. 消除三个 2025 Mustang Mach-E PENDING，定位普通版具体高度配置。
3. 批量处理 S197、SN95及Fox-body Mustang Coupe/Convertible。
4. Ranger闭合后再进入 F-150，避免驾驶室和货斗分支误合并。

推进信号：CONTINUE

[1]: https://media.ford.com/content/dam/fordmedia/North%20America/US/2015/08/24/gt350-gt350r-tech-specs.pdf "2009 MUSTANG TECHNICAL SPECIFICATIONS"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已消除 3 个 2025 Mustang Mach-E 的原 PENDING。Ford 2025 欧洲技术资料确认：225 kW RWD 与 303 kW AWD 均属于普通 CGW 五门外廓，三维为 `4713 × 1881 × 1624 mm`，与已建尺寸组完全一致；290 kW AWD 也是非 GT 的 CGW 普通车身，因此一并复用现有标准组。
* 本轮未创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：34
* READY 映射行：43
* PENDING／尚未展开 Ktype：66
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801866	801866	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门2025普通RWD外廓。	READY
801865	801865	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门2025普通AWD外廓。	READY
801881	801881	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	MEDIUM	CGW五门2025非GT AWD外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 按已定位的 Ranger P703 车身边界，分别闭合 Extended Cab、Double Cab、Standard Cab和Cab & Chassis。
2. 独立处理 Ranger Raptor及PHEV，不与普通P703货斗车身直接共组。
3. 随后批量处理 S197、SN95和Fox-body Mustang。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 9 个 Ranger P703 Ktype，确认 Single Cab、Super Cab、Double Cab 与 Raptor 四种物理外廓；不同发动机、功率及驱动形式直接复用对应尺寸组。([allopneus.com][1])
* 首次创建 4 个尺寸组。普通 P703 三种驾驶室采用 Ford 官方 Ranger brochure 的不含后视镜宽度；Raptor 独立使用宽体尺寸。
* Cab & Chassis 两行及 PHEV 一行暂未强行映射，需分别解决改装后部外廓和 PHEV 配置高度边界。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：43
* READY 映射行：52
* PENDING／尚未展开 Ktype：57
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
152212	152212	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
800093	800093	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	HIGH	P703 Single Cab外廓。	READY
152213	152213	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	HIGH	P703 Double Cab外廓。	READY
152273	152273	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	HIGH	P703 Single Cab外廓。	READY
152202	152202	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
152670	152670	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
157843	157843	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	HIGH	P703 Double Cab Raptor宽体外廓。	READY
152205	152205	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	HIGH	P703 Double Cab外廓。	READY
152214	152214	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	HIGH	P703 Double Cab Raptor宽体外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	5350	1910	1877	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	5350	1910	1883	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	5350	1910	1886	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	5381	2028	1922	Auto-Data Ford Ranger IV Double Cab Raptor	https://www.auto-data.net/en/ford-ranger-iv-double-cab-raptor-3.0-ecoboost-v6-292hp-e-4wd-automatic-46825
```

## 下一步优先处理

1. 闭合 `801294` Ranger PHEV 的具体 Double Cab 高度及不含后视镜宽度。
2. 处理 `800094`、`152630` Cab & Chassis，避免把底盘驾驶室误套用完整 Pickup 后部外廓。
3. 批量处理 S197、SN95、Fox-body Mustang Coupe及Convertible。

推进信号：CONTINUE

[1]: https://www.allopneus.com/vehicule/ford/ranger/ranger-crew-cab-pickup?utm_source=chatgpt.com "Pneu FORD RANGER Crew Cab Pickup : Pression et dimensions des pneus - Allopneus.com"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Ford Flex `50313`，确认第一代 Flex 五门 SUV 外廓，采用 Ford 2010 官方车型手册中明确标注的**不含后视镜宽度**。([汽车目录档案][1])
* 闭合 8 个 Ford Taurus Ktype：第三代 Sedan、第三代 Wagon、第四代 Sedan 分别复用三个尺寸组；发动机和 24V 配置差异未重复建组。第三代 Sedan/Wagon 的尺寸边界由 Ford 车主手册数据及 Edmunds 交叉支持，第四代 Sedan 使用 2003 年规格数据。([Edmunds][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：52
* READY 映射行：61
* PENDING／尚未闭合 Ktype：48
* 已确认尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
50313	50313	SUV	Flex I		5	EU-FORD-USA-FLEX-I-SUV-01	HIGH	第一代Flex五门SUV外廓。	READY
8002	8002	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8003	8003	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
47261	47261	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8004	8004	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8005	8005	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
109826	109826	Sedan	Taurus IV		4	EU-FORD-USA-TAURUS-IV-SEDAN-01	HIGH	第四代Taurus四门Sedan外廓。	READY
14654	14654	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
14655	14655	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-FLEX-I-SUV-01	5126	1928	1727	Ford Flex 2010 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Flex-2010-USA.pdf
EU-FORD-USA-TAURUS-III-SEDAN-01	5017	1854	1400	Ford 1998 Taurus Owner's Manual; Edmunds 1999 Ford Taurus Sedan specifications	https://www.carmanualsonline.info/ford-taurus-1998-3-g-owners-manual/?srch=compression+ratio;https://www.edmunds.com/ford/taurus/1999/sedan/features-specs/
EU-FORD-USA-TAURUS-III-WAGON-01	5070	1854	1463	Ford 1998 Taurus Owner's Manual; Edmunds 1999 Ford Taurus Wagon specifications	https://www.carmanualsonline.info/ford-taurus-1998-3-g-owners-manual/?srch=compression+ratio;https://www.edmunds.com/ford/taurus/1999/wagon/features-specs/
EU-FORD-USA-TAURUS-IV-SEDAN-01	5019	1854	1425	Edmunds 2003 Ford Taurus specifications; The Car Connection 2003 Ford Taurus specifications	https://www.edmunds.com/ford/taurus/2003/features-specs/;https://www.thecarconnection.com/specifications/ford_taurus_2003
```

## 下一步优先处理

1. 闭合 Windstar 第一代 MPV 与 Cargo Van 外廓。
2. 批量处理 Thunderbird、SN95 Mustang 与 Fox-body Mustang。
3. 回到 Ranger PHEV 和两个 Cab & Chassis 阻塞项，解决欧洲市场长度口径及裸底盘后部边界。
4. Ranger 闭合后处理 F-150 的驾驶室、货斗、Raptor 与 Lightning 分支。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Flex-2010-USA.pdf?utm_source=chatgpt.com "Ford-Flex-2010-USA.pdf"
[2]: https://www.edmunds.com/ford/taurus/1999/sedan/features-specs/?utm_source=chatgpt.com "Used 1999 Ford Taurus Sedan Specs & Features | Edmunds"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Thunderbird 2 个 Ktype。`58103` 的 4.9 L 发动机限定为 MN12 前期外廓；`124766` 对应 1994–1997 后期外廓，两组长度和高度不同。([conceptcarz.com][1])
* 闭合 Windstar 3 个 Ktype。`15370` 跨越两代车型，拆为第一代和第二代；第一代 Cargo Van 与乘用 MPV 的标准高度不同，分别建组。([Edmunds][2])
* 闭合 FSO 126p 和 Polonez I 共 4 个 Ktype。126p 复用早期 600 型外廓；Polonez 长周期 Ktype 覆盖 `4272 mm` 和 `4322 mm` 两个已确认长度阶段，因此 `12921`、`12922` 拆为前期和改款后分支。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：61
* READY 映射行：73
* PENDING／尚未闭合 Ktype：39
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124766	124766	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-MN12-COUPE-FACELIFT-01	HIGH	MN12后期双门Coupe外廓。	READY
58103	58103	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-MN12-COUPE-PREFL-01	MEDIUM	4.9发动机限定为MN12前期外廓；输入结束年月晚于该发动机实际边界。	READY
15370_gen1	15370	MPV	Windstar I		3	EU-FORD-USA-WINDSTAR-I-MPV-01	HIGH	Ktype跨越换代，第一代三门乘用MPV外廓。	READY
15370_gen2	15370	MPV	Windstar II		4	EU-FORD-USA-WINDSTAR-II-MPV-01	HIGH	Ktype跨越换代，第二代四门乘用MPV外廓。	READY
143238	143238	Van	Windstar I		3	EU-FORD-USA-WINDSTAR-I-VAN-01	HIGH	第一代三门Cargo Van外廓。	READY
8006	8006	MPV	Windstar I		3	EU-FORD-USA-WINDSTAR-I-MPV-01	HIGH	第一代三门乘用MPV外廓。	READY
12919	12919	Hatchback	126p I		2	EU-FSO-126P-I-HATCHBACK-01	HIGH	早期126p双门外廓。	READY
12920	12920	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	HIGH	Polonez I早期五门外廓。	READY
12921_prefl	12921	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	MEDIUM	Ktype覆盖Polonez I早期外廓阶段。	READY
12921_facelift	12921	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖Polonez I加长改款外廓阶段。	READY
12922_prefl	12922	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	MEDIUM	Ktype覆盖Polonez I早期外廓阶段。	READY
12922_facelift	12922	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖Polonez I加长改款外廓阶段。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-THUNDERBIRD-MN12-COUPE-FACELIFT-01	5088	1847	1334	Edmunds 1997 Ford Thunderbird LX specifications	https://www.edmunds.com/ford/thunderbird/1997/st-6073/features-specs/
EU-FORD-USA-THUNDERBIRD-MN12-COUPE-PREFL-01	5047	1847	1339	Automobile-Catalog 1989 Ford Thunderbird SC specifications	https://www.automobile-catalog.com/car/1989/879065/ford_thunderbird_sc.html
EU-FORD-USA-WINDSTAR-I-MPV-01	5110	1915	1727	Edmunds 1995 Ford Windstar specifications	https://www.edmunds.com/ford/windstar/1995/features-specs/
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679	Edmunds 1999 Ford Windstar SE specifications	https://www.edmunds.com/ford/windstar/1999/st-8036/features-specs/
EU-FORD-USA-WINDSTAR-I-VAN-01	5110	1915	1725	Edmunds 1995 Ford Windstar Cargo specifications	https://www.edmunds.com/ford/windstar-cargo/1995/minivan/features-specs/
EU-FSO-126P-I-HATCHBACK-01	3054	1377	1335	Automobile-Catalog 1973 Polski Fiat 126p 600 specifications	https://www.automobile-catalog.com/car/1973/38975/polski_fiat_126p_600.html
EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	4272	1651	1420	Automobile-Catalog 1982 FSO Polonez 1500 specifications	https://www.automobile-catalog.com/car/1982/24335/fso_polonez_1500.html
EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	4322	1651	1420	Automobile-Catalog 1988 FSO Polonez 1.5 SL specifications	https://www.automobile-catalog.com/car/1988/52760/fso_polonez_1_5_sl.html
```

## 下一步优先处理

1. 批量闭合 SN95、Fox-body、S197 Mustang Coupe 与 Convertible。
2. 处理 Forthing T5 Evo、U-Tour及 GAC Aion V 等高复用乘用车组。
3. 继续解决 Ranger PHEV、两个 Cab & Chassis及 F-150 驾驶室／货斗分支。
4. 最后处理资料稀缺的 Foton、Galloper及早期 Mustang。

推进信号：CONTINUE

[1]: https://www.conceptcarz.com/s10558/ford-thunderbird.aspx?utm_source=chatgpt.com "1989 Ford Thunderbird Specifications & Dimensions"
[2]: https://www.edmunds.com/ford/windstar/1995/features-specs/ "Used 1995 Ford Windstar Specs & Features | Edmunds"
[3]: https://www.automobile-catalog.com/car/1973/38975/polski_fiat_126p_600.html?utm_source=chatgpt.com "1973 Polski Fiat 126p 600 Specs Review (16.91 kW / 23 PS / 23 hp) (since mid-year 1973 for Europe )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 13 个旧款 Mustang Ktype。S197 按 2009 前期、2010 改款、2011–2014 V6/GT及 Coupe/Convertible 的实际外廓差异建组；相同外廓的不同发动机 Ktype 直接复用。([Edmunds][1])
* SN95 长周期 Ktype 按 1994–1998 初期与 1999 New Edge 外廓拆分；Fox-body 2.3 与 5.0 Convertible 共用同一外廓组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* READY 映射行：89
* PENDING／尚未闭合 Ktype：26
* 已确认尺寸组：37
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57967	57967	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-V6-FACELIFT-01	HIGH	S197改款后V6 Coupe外廓。	READY
57965	57965	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-FACELIFT-01	HIGH	S197改款后GT Coupe外廓。	READY
57964_prefl	57964	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-PREFL-01	HIGH	Ktype跨越改款，2009年前期GT Coupe外廓。	READY
57964_facelift	57964	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-2010-01	HIGH	Ktype跨越改款，2010款GT Coupe外廓。	READY
57951	57951	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-V6-FACELIFT-01	HIGH	S197改款后V6 Convertible外廓。	READY
55018	55018	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	HIGH	S197改款后GT Convertible外廓。	READY
57952	57952	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	HIGH	S197改款后GT Convertible外廓。	READY
7998_prefl	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	Ktype跨越1999外观改款，SN95前期Coupe外廓。	READY
7998_facelift	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-NEW-EDGE-01	HIGH	Ktype跨越1999外观改款，New Edge Coupe外廓。	READY
8000	8000	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	SN95前期GT Coupe外廓。	READY
52839	52839	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	SN95前期GT Coupe外廓。	READY
7999_prefl	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1999外观改款，SN95前期Convertible外廓。	READY
7999_facelift	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-NEW-EDGE-01	HIGH	Ktype跨越1999外观改款，New Edge Convertible外廓。	READY
8001	8001	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	HIGH	SN95前期GT Convertible外廓。	READY
57957	57957	Convertible	Mustang III	Fox	2	EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	HIGH	Fox-body Convertible外廓。	READY
57955	57955	Convertible	Mustang III	Fox	2	EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	HIGH	Fox-body Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-S197-COUPE-V6-FACELIFT-01	4778	1877	1412	Edmunds 2011 Ford Mustang specifications	https://www.edmunds.com/ford/mustang/2011/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-PREFL-01	4765	1877	1407	Edmunds 2009 Ford Mustang Coupe GT specifications	https://www.edmunds.com/ford/mustang/2009/coupe/st-101006668/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-2010-01	4778	1877	1412	Edmunds 2010 Ford Mustang Coupe GT specifications	https://www.edmunds.com/ford/mustang/2010/coupe/st-101144372/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-FACELIFT-01	4778	1877	1417	Edmunds 2011 Ford Mustang GT specifications	https://www.edmunds.com/ford/mustang/2011/st-101274492/features-specs/
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-V6-FACELIFT-01	4778	1877	1425	Edmunds 2011 Ford Mustang Convertible V6 specifications	https://www.edmunds.com/ford/mustang/2011/convertible/st-101274488/features-specs/
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	4778	1877	1417	Edmunds 2011 Ford Mustang Convertible GT specifications	https://www.edmunds.com/ford/mustang/2011/convertible/st-101274492/features-specs/
EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	4610	1824	1344	Automobile-Catalog 1994 Ford Mustang Coupe 3.8 V6 specifications	https://www.automobile-catalog.com/car/1994/885155/ford_mustang_coupe_3_8l_v-6.html
EU-FORD-USA-MUSTANG-SN95-COUPE-NEW-EDGE-01	4653	1857	1349	Edmunds 1999 Ford Mustang Coupe specifications	https://www.edmunds.com/ford/mustang/1999/coupe/features-specs/
EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	4610	1824	1341	Automobile-Catalog 1994 Ford Mustang Convertible 3.8 V6 specifications	https://www.automobile-catalog.com/car/1994/885215/ford_mustang_convertible_3_8l_v-6.html
EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-NEW-EDGE-01	4653	1857	1351	Edmunds 1999 Ford Mustang Convertible specifications	https://www.edmunds.com/ford/mustang/1999/convertible/features-specs/
EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	4562	1735	1323	Automobile-Catalog 1993 Ford Mustang LX Convertible specifications	https://www.automobile-catalog.com/car/1993/870695/ford_mustang_lx_convertible_2_3l_automatic.html
```

## 下一步优先处理

1. 闭合 S197 Shelby GT500 Coupe、GT500 Convertible及第一代 Mustang Convertible。
2. 处理 Forthing T5 Evo、U-Tour、GAC Aion V及 Galloper。
3. 解决 Ranger PHEV、两个 Cab & Chassis。
4. 最后集中拆分 F-150 的驾驶室、货斗、Raptor及 Lightning 外廓。

推进信号：CONTINUE

[1]: https://www.edmunds.com/ford/mustang/2009/coupe/st-101006665/features-specs/?utm_source=chatgpt.com "Used 2009 Ford Mustang Coupe Premium Specs & Features"
[2]: https://www.automobile-catalog.com/car/1994/885185/ford_mustang_coupe_3_8l_v-6_automatic.html?utm_source=chatgpt.com "1994 Ford Mustang Coupe 3.8L V-6 automatic Specs Review (108 kW / 147 PS / 145 hp) (since mid-year 1993 for North America U.S.)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合剩余 2 个 Shelby GT500 Ktype，分别建立 S197 前期 Coupe 和 2013–2014 Convertible 专属外廓，不与普通 Mustang GT 共组。([Edmunds][1])
* 闭合 Forthing T5 EVO、U-Tour 共 5 个 Ktype。汽油、LPG及 HEV 未改变对应车型外廓，直接复用各自尺寸组；U-Tour HEV 官方技术资料确认三维及五门边界。([东风商用车][2])
* 闭合第二代 GAC Aion V `160003`，按欧洲／国际版五门 SUV 外廓建组。([GAC集团][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射行：97
* PENDING／尚未闭合 Ktype：18
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108767	108767	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT500-PREFL-01	HIGH	S197前期Shelby GT500 Coupe专属外廓。	READY
105930	105930	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT500-2013-01	HIGH	2013至2014 Shelby GT500 Convertible外廓。	READY
157036	157036	SUV	T5 EVO I		5	EU-FORTHING-T5-EVO-I-SUV-01	HIGH	T5 EVO五门SUV外廓。	READY
157037	157037	SUV	T5 EVO I		5	EU-FORTHING-T5-EVO-I-SUV-01	HIGH	LPG版本未改变T5 EVO外廓。	READY
157038	157038	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	M4五门七座MPV外廓。	READY
802898	802898	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	HEV版本与U-Tour M4标准外廓一致。	READY
157039	157039	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	LPG版本未改变U-Tour M4外廓。	READY
160003	160003	SUV	Aion V II	AY5-G	5	EU-GAC-AION-V-II-SUV-01	HIGH	第二代Aion V国际版五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-S197-COUPE-GT500-PREFL-01	4765	1877	1384	Edmunds 2009 Ford Shelby GT500 specifications	https://www.edmunds.com/ford/shelby-gt500/2009/features-specs/
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT500-2013-01	4780	1877	1400	Ford 2014 Shelby GT500 Technical Specifications	https://www.autoinfo.jp/release/Mustang_Shelby_GT500_spec_my14.pdf
EU-FORTHING-T5-EVO-I-SUV-01	4565	1860	1690	Dongfeng Forthing T5 EVO official specifications	https://www.forthingmotor.com/chinese-professional-dongfeng-forthing-t5evo-suv-vehicle-product/
EU-FORTHING-U-TOUR-M4-MPV-01	4850	1900	1715	Dongfeng Forthing U-Tour official specifications; Forthing Polska U-Tour HEV 2026 technical data	https://www.forthingmotor.com/dongfeng-mpv-u-tour-product/;https://forthing-auto.pl/document/6/a347909c99b10bb72864d9bdbcc48189.pdf
EU-GAC-AION-V-II-SUV-01	4605	1854	1686	GAC Australia Aion V official specifications	https://www.gacgroup.com/en-au/configuration/aion-v/2024
```

## 下一步优先处理

1. 闭合 Foton Toano、Tunland G7及 Tunland 2.0 D 三种商用车外廓。
2. 处理 Galloper Ktype 同时覆盖的三门短轴与五门长轴分支，解决外饰套件造成的尺寸口径冲突。
3. 闭合 Ranger PHEV及两个 Cab & Chassis。
4. 最后集中拆分 9 个 F-150 Ktype 的驾驶室、货斗、Raptor及 Lightning 外廓。

推进信号：CONTINUE

[1]: https://www.edmunds.com/ford/shelby-gt500/2009/features-specs/?utm_source=chatgpt.com "Used 2009 Ford Shelby GT500 Specs & Features"
[2]: https://www.forthingmotor.com/chinese-professional-dongfeng-forthing-t5evo-suv-vehicle-product/?utm_source=chatgpt.com "Chinese Professional Dongfeng Forthing T5evo SUV Vehicle"
[3]: https://www.gacgroup.com/en-au/configuration/aion-v/2024?utm_source=chatgpt.com "AION V Specification | GAC Australia"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Foton Tunland G7 `801495`，确认为四门 Double Cab 标准外廓，后轮驱动不改变车身三维。([foton][1])
* 闭合 Galloper `151146`。车身代码 `KNE1CP` 对应三门短轴车身，不与五门长轴 Galloper II 共组。([b-parts.co.uk][2])
* `150413` 的生产区间跨越第一代 Mustang 三次明确外廓变化，拆为 1965–1966、1967–1968、1969–1970 三条派生映射。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射行：102
* PENDING／尚未闭合 Ktype：15
* 已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
150413_1965_66	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1965-66-01	HIGH	第一代Mustang 1965至1966 Convertible外廓。	READY
150413_1967_68	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1967-68-01	HIGH	第一代Mustang 1967至1968 Convertible外廓。	READY
150413_1969_70	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1969-70-01	HIGH	第一代Mustang 1969至1970 Convertible外廓。	READY
801495	801495	Pickup	Tunland G7		4	EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	HIGH	Tunland G7四门Double Cab外廓。	READY
151146	151146	SUV	Galloper II	KNE1CP	3	EU-GALLOPER-GALLOPER-II-SUV-3D-01	HIGH	KNE1CP三门短轴外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1965-66-01	4613	1732	1298	Automobile-Catalog 1965 Ford Mustang Convertible Six; 1965 Ford Mustang Fact Sheet	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1965.html;https://over-drive-magazine.com/2022/10/07/1965-ford-mustang-fact-sheet/
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1967-68-01	4663	1801	1306	Automobile-Catalog 1967 and 1968 Ford Mustang Base Convertible; 1967 Ford Mustang Fact Sheet	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1967.html;https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1968.html;https://over-drive-magazine.com/2023/05/31/1967-ford-mustang-fact-sheet/
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1969-70-01	4760	1811	1303	Automobile-Catalog 1969 and 1970 Ford Mustang Base Convertible	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1969.html;https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1970.html
EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	5340	1940	1870	Foton Tunland G7 official distributor specifications	https://www.fotonnepal.com/vehicle/products/tunland-g7-pickup-van
EU-GALLOPER-GALLOPER-II-SUV-3D-01	4020	1770	1860	UltimateSpecs Galloper 2.5 TCI; B-Parts Galloper II KNE1CP body identification	https://www.ultimatespecs.com/car-specs/Galloper/5545/Galloper-Galloper-25-TCI.html;https://www.b-parts.co.uk/auto-parts/interior/dashboard-hyundai-galloper-ii-jk-01-1997-1998-1999-2000-2001-2002-2003-27057357
```

## 下一步优先处理

1. 闭合 Foton eToano `801811` 与新一代 Tunland `146456`。
2. 解决 Ranger PHEV `801294` 及两个 Cab & Chassis Ktype。
3. 集中拆分 9 个 F-150 Ktype 的驾驶室、货斗、Raptor与 Lightning 外廓。

推进信号：CONTINUE

[1]: https://www.foton-africa.com/products/foton-tunland-g7-red/?utm_source=chatgpt.com "Foton TUNLAND G7 Red"
[2]: https://www.b-parts.co.uk/auto-parts/interior/dashboard-hyundai-galloper-ii-jk-01-1997-1998-1999-2000-2001-2002-2003-27057357?utm_source=chatgpt.com "Dashboard HYUNDAI GALLOPER II (JK-01) 2.5 TD 27057357 | B-Parts"
[3]: https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1965.html?utm_source=chatgpt.com "1965 Ford (USA) Mustang Base Convertible full range specs"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Mustang `57950`，按 2009 前期与 2010 改款后 Convertible 外廓拆为两行；两组宽度均为明确的不含后视镜口径。([汽车目录][1])
* Ranger PHEV `801294` 覆盖 XLT、Sport、Wildtrak／Stormtrak 三种已确认高度分支。Ford 规格表明确给出四个配置相同的 `5367 mm` 长度、`1924 mm` 不含后视镜宽度，以及三种高度。
* Ranger 后驱 Chassis Cab `800094` 已闭合；四驱 Chassis Cab `152630` 因早期车身手册与后期整车规格的长度、高度阶段边界未闭合，保留 PENDING。([CarExpert NZ][2])
* Tunland G7 `146456` 直接复用既有尺寸组，未重复抓取。
* eToano `801811` 暂不强行建组：同一 130 kW 车型资料中存在 L2H2、L3H2及高顶外廓，高顶高度还存在 `2720/2760 mm` 市场口径差异。([Foton][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射行：109
* PENDING Ktype：2
* 尚未展开 Ktype：9
* 已确认尺寸组：53
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57950_prefl	57950	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-PREFL-01	HIGH	2009款S197 GT Convertible前期外廓。	READY
57950_facelift	57950	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-2010-01	HIGH	2010款S197 GT Convertible改款外廓。	READY
800094	800094	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-RWD-01	HIGH	P703单排后驱Chassis Cab外廓。	READY
152630	152630	Pickup	Ranger IV	P703	2		MEDIUM	P703单排四驱Chassis Cab阶段边界尚未闭合。	PENDING: 4x4 Chassis Cab长度与高度阶段边界未确认
801294_xlt	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-XLT-01	HIGH	P703 Double Cab PHEV XLT外廓。	READY
801294_sport	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-SPORT-01	HIGH	P703 Double Cab PHEV Sport外廓。	READY
801294_wildtrak_stormtrak	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-WILDTRAK-STORMTRAK-01	HIGH	P703 Double Cab PHEV Wildtrak与Stormtrak共用外廓。	READY
801811	801811	Van	eToano I			LOW	eToano货运Van存在多个长度及车顶分支。	PENDING: L2H2、L3H2及高顶分支与Ktype边界未确认
146456	146456	Pickup	Tunland G7		4	EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	HIGH	Tunland G7四门Double Cab外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-PREFL-01	4765	1877	1415	Automobile-Catalog 2009 Ford Mustang GT Convertible specifications	https://www.automobile-catalog.com/car/2009/1420895/ford_mustang_gt_convertible.html
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-2010-01	4778	1877	1425	Edmunds 2010 Ford Mustang Convertible GT Premium specifications	https://www.edmunds.com/ford/mustang/2010/convertible/st-101144375/features-specs/
EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-RWD-01	5225	1910	1880	CarExpert 2022 Ford Ranger XL 2D Chassis Cab RWD specifications	https://www.carexpert.co.nz/ford/ranger/2022-xl-2l-chassis-cab-rwd-diesel-automatic-jmmw88fw20221201
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-XLT-01	5367	1924	1871	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-SPORT-01	5367	1924	1883	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-WILDTRAK-STORMTRAK-01	5367	1924	1878	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
```

## 下一步优先处理

1. 消除 `152630` 的早期／后期四驱 Chassis Cab 外廓边界。
2. 确认 `801811` 是否覆盖 L2H2、L3H2和高顶全部分支，并解决高顶高度口径冲突。
3. 集中拆分剩余 9 个 F-150 Ktype 的驾驶室、货斗、Raptor及 Lightning 外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/1420895/ford_mustang_gt_convertible.html?utm_source=chatgpt.com "2009 Ford Mustang GT Convertible Specs Review (223.5 kW / 304 PS / 300 hp) (for North America U.S.)"
[2]: https://www.carexpert.co.nz/ford/ranger/2022-xl-2l-chassis-cab-rwd-diesel-automatic-jmmw88fw20221201 "2022 Ford Ranger XL Price and Specifications | CarExpert | CarExpert NZ"
[3]: https://www.fotonlcv.es/upload/ficha-tecnica/FOTON_ficha_eToano.pdf?utm_source=chatgpt.com "FOTON_ficha_eToano_mar25.ai"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已闭合 Ranger `152630`：确认为 P703 单排四驱 Chassis Cab，完整外廓为 `5225 × 1910 × 1875 mm`，宽度为不含后视镜口径。([CarExpert][1])
* 已闭合 eToano `801811`：通用 Ktype 覆盖 L2H2、L2H3、L3H2、L3H3 四种量产货运外廓，拆为四条派生映射。Foton 官方资料确认两种长度、两种车顶高度及 `2000 mm` 车身宽度；同系列官方规格明确该宽度不含后视镜。([福特汽车葡萄牙][2])
* 本轮原有两个 PENDING 均已消除；剩余未闭合项仅为 9 个 F-150 Ktype。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：114
* PENDING／尚未闭合 Ktype：9
* 已确认尺寸组：58
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
152630	152630	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-4X4-01	HIGH	P703单排四驱Chassis Cab外廓。	READY
801811_l2h2	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L2H2-01	MEDIUM	eToano标准轴距中顶货运外廓。	READY
801811_l2h3	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L2H3-01	MEDIUM	eToano标准轴距高顶货运外廓。	READY
801811_l3h2	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L3H2-01	MEDIUM	eToano长轴距中顶货运外廓。	READY
801811_l3h3	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L3H3-01	MEDIUM	eToano长轴距高顶货运外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-4X4-01	5225	1910	1875	CarExpert 2023 Ford Ranger XL 2.0 Cab Chassis 4x4 specifications	https://www.carexpert.com.au/ford/ranger/2023-xl-2l-cab-chassis-4x4-diesel-automatic-jsamafgm20221110
EU-FOTON-ETOANO-I-VAN-L2H2-01	5495	2000	2445	Foton Spain eToano official technical sheet; Foton official Toano body-width specification	https://www.fotonlcv.es/upload/ficha-tecnica/FOTON_ficha_eToano.pdf;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L2H3-01	5495	2000	2720	Foton Portugal eToano official specifications; Foton official Toano body-width specification	https://foton-portugal.pt/products/etoano/;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L3H2-01	5990	2000	2445	Foton Spain eToano official technical sheet; Foton official Toano body-width specification	https://www.fotonlcv.es/upload/ficha-tecnica/FOTON_ficha_eToano.pdf;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L3H3-01	5990	2000	2720	Foton Portugal eToano official specifications; Foton official Toano body-width specification	https://foton-portugal.pt/products/etoano/;https://www.foton-africa.com/products/foton-toano-white/
```

## 下一步优先处理

集中闭合剩余 9 个 F-150 Ktype：P552 Regular Cab、Extended Cab、Crew Cab及对应货斗长度；P415 Regular Cab、Crew Cab、SVT Raptor；最后处理 P702 Lightning Crew Cab。

推进信号：CONTINUE

[1]: https://www.carexpert.com.au/ford/ranger/2023-xl-2l-cab-chassis-4x4-diesel-automatic-jsamafgm20221110?utm_source=chatgpt.com "2023 Ford Ranger XL Price and Specifications"
[2]: https://foton-portugal.pt/products/etoano/?utm_source=chatgpt.com "eToano"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6301-6400_ktype_dimension_mapping_final.tsv
- left18448_6301-6400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 剩余 9 个 F-150 Ktype 已按 P552、P415、P702 代际及 Regular Cab、SuperCab、SuperCrew、Raptor、Lightning 和货斗长度拆分闭合。车型边界由对应 Ktype 车身页面确认，尺寸采用 Ford 车型资料及直接规格数据。([AUTODOC][1])
* P552、P415 和 Lightning 的驾驶室、货斗及宽体外廓尺寸已完成机械闭合。([Ford series][2])
* 已完成固定表头、唯一键、引用闭合、尺寸正整数及来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：129
* PENDING 映射：0
* DIMENSION_GROUP：73
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108101_6p5ft	108101	Pickup	F-150 XIII	P552	2	EU-FORD-USA-F-150-P552-PICKUP-REGULAR-CAB-6P5FT-01	HIGH	P552 Regular Cab 4x4 6.5-ft货斗外廓。	READY
108101_8ft	108101	Pickup	F-150 XIII	P552	2	EU-FORD-USA-F-150-P552-PICKUP-REGULAR-CAB-8FT-01	HIGH	P552 Regular Cab 4x4 8-ft货斗外廓。	READY
108103_5p5ft	108103	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-SUPERCREW-5P5FT-01	HIGH	P552 SuperCrew 4x4 5.5-ft货斗外廓。	READY
108103_6p5ft	108103	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-SUPERCREW-6P5FT-01	HIGH	P552 SuperCrew 4x4 6.5-ft货斗外廓。	READY
108105_6p5ft	108105	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-SUPERCAB-6P5FT-01	HIGH	P552 SuperCab 4x4 6.5-ft货斗外廓。	READY
108105_8ft	108105	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-SUPERCAB-8FT-01	HIGH	P552 SuperCab 4x4 8-ft货斗外廓。	READY
128375	128375	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-RAPTOR-SUPERCAB-01	HIGH	P552 Raptor SuperCab 5.5-ft货斗宽体外廓。	READY
128377	128377	Pickup	F-150 XIII	P552	4	EU-FORD-USA-F-150-P552-PICKUP-RAPTOR-SUPERCREW-01	HIGH	P552 Raptor SuperCrew 5.5-ft货斗宽体外廓。	READY
51684_prefl_5p5ft	51684	Pickup	F-150 XII	P415	4	EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-5P5FT-PREFL-01	HIGH	P415改款前SuperCrew 4x4 5.5-ft货斗外廓。	READY
51684_facelift_5p5ft	51684	Pickup	F-150 XII	P415	4	EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-5P5FT-FACELIFT-01	HIGH	P415改款后SuperCrew 4x4 5.5-ft货斗外廓。	READY
51684_facelift_6p5ft	51684	Pickup	F-150 XII	P415	4	EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-6P5FT-FACELIFT-01	HIGH	P415改款后SuperCrew 4x4 6.5-ft货斗外廓。	READY
107127_6p5ft	107127	Pickup	F-150 XII	P415	2	EU-FORD-USA-F-150-P415-PICKUP-REGULAR-CAB-6P5FT-FACELIFT-01	MEDIUM	P415改款后Regular Cab 4x4 6.5-ft货斗外廓。	READY
107127_8ft	107127	Pickup	F-150 XII	P415	2	EU-FORD-USA-F-150-P415-PICKUP-REGULAR-CAB-8FT-FACELIFT-01	MEDIUM	P415改款后Regular Cab 4x4 8-ft货斗外廓。	READY
51477	51477	Pickup	F-150 XII	P415	4	EU-FORD-USA-F-150-P415-PICKUP-SVT-RAPTOR-SUPERCAB-01	HIGH	P415 SVT Raptor SuperCab 5.5-ft货斗宽体外廓。	READY
153141	153141	Pickup	F-150 Lightning I	P702	4	EU-FORD-USA-F-150-P702-LIGHTNING-SUPERCREW-01	HIGH	P702 Lightning SuperCrew 5.5-ft货斗外廓。	READY
50313	50313	SUV	Flex I		5	EU-FORD-USA-FLEX-I-SUV-01	HIGH	第一代Flex五门SUV外廓。	READY
150413_1965_66	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1965-66-01	HIGH	第一代Mustang 1965至1966 Convertible外廓。	READY
150413_1967_68	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1967-68-01	HIGH	第一代Mustang 1967至1968 Convertible外廓。	READY
150413_1969_70	150413	Convertible	Mustang I		2	EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1969-70-01	HIGH	第一代Mustang 1969至1970 Convertible外廓。	READY
57967	57967	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-V6-FACELIFT-01	HIGH	S197改款后V6 Coupe外廓。	READY
7998_prefl	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	Ktype跨越1999外观改款，SN95前期Coupe外廓。	READY
7998_facelift	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-NEW-EDGE-01	HIGH	Ktype跨越1999外观改款，New Edge Coupe外廓。	READY
8000	8000	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	SN95前期GT Coupe外廓。	READY
52839	52839	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	HIGH	SN95前期GT Coupe外廓。	READY
57965	57965	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-FACELIFT-01	HIGH	S197改款后GT Coupe外廓。	READY
108767	108767	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT500-PREFL-01	HIGH	S197前期Shelby GT500 Coupe专属外廓。	READY
108873_prefl	108873	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
108873_facelift	108873	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
115865_prefl	115865	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
115865_facelift	115865	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
157173	157173	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
157194	157194	Convertible	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	HIGH	S650双门Convertible外廓。	READY
57964_prefl	57964	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-PREFL-01	HIGH	Ktype跨越改款，2009年前期GT Coupe外廓。	READY
57964_facelift	57964	Coupe	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-COUPE-GT-2010-01	HIGH	Ktype跨越改款，2010款GT Coupe外廓。	READY
157192	157192	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	MEDIUM	输入版本名为Bullit；物理边界为S650双门Fastback。	READY
157793	157793	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-DARK-HORSE-01	HIGH	Dark Horse专属外廓。	READY
157179	157179	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
157191	157191	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
158167	158167	Coupe	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-COUPE-01	HIGH	S650双门Fastback外廓。	READY
158168	158168	Convertible	Mustang VII	S650	2	EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	HIGH	S650双门Convertible外廓。	READY
109565_prefl	109565	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
109565_facelift	109565	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
109962_prefl	109962	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
109962_facelift	109962	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
121899_prefl	121899	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	HIGH	Ktype跨越S550改款，前期Fastback外廓。	READY
121899_facelift	121899	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Fastback外廓。	READY
117269	117269	Coupe	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-COUPE-GT350-01	HIGH	Shelby GT350专属宽体Fastback外廓。	READY
57957	57957	Convertible	Mustang III	Fox	2	EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	HIGH	Fox-body Convertible外廓。	READY
57951	57951	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-V6-FACELIFT-01	HIGH	S197改款后V6 Convertible外廓。	READY
7999_prefl	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1999外观改款，SN95前期Convertible外廓。	READY
7999_facelift	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-NEW-EDGE-01	HIGH	Ktype跨越1999外观改款，New Edge Convertible外廓。	READY
8001	8001	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	HIGH	SN95前期GT Convertible外廓。	READY
57955	57955	Convertible	Mustang III	Fox	2	EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	HIGH	Fox-body Convertible外廓。	READY
55018	55018	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	HIGH	S197改款后GT Convertible外廓。	READY
57952	57952	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	HIGH	S197改款后GT Convertible外廓。	READY
105930	105930	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT500-2013-01	HIGH	2013至2014 Shelby GT500 Convertible外廓。	READY
108876_prefl	108876	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
108876_facelift	108876	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
116599_prefl	116599	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
116599_facelift	116599	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
108877	108877	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	3.7 V6对应S550前期Convertible外廓。	READY
57950_prefl	57950	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-PREFL-01	HIGH	2009款S197 GT Convertible前期外廓。	READY
57950_facelift	57950	Convertible	Mustang V	S197	2	EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-2010-01	HIGH	2010款S197 GT Convertible改款外廓。	READY
109564_prefl	109564	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
109564_facelift	109564	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
115872_prefl	115872	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越S550改款，前期Convertible外廓。	READY
115872_facelift	115872	Convertible	Mustang VI	S550	2	EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越S550改款，改款后Convertible外廓。	READY
143871	143871	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143876	143876	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
157623	157623	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
801866	801866	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门2025普通RWD外廓。	READY
143870	143870	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143872	143872	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143873	143873	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
143874	143874	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
156883	156883	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
157624	157624	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门普通外廓。	READY
801865	801865	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	HIGH	CGW五门2025普通AWD外廓。	READY
801881	801881	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	MEDIUM	CGW五门2025非GT AWD外廓。	READY
146215	146215	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
800867	800867	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
801301	801301	SUV	Mustang Mach-E I	CGW	5	EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	MEDIUM	CGW五门GT外廓。	READY
152212	152212	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
800093	800093	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	HIGH	P703 Single Cab外廓。	READY
800094	800094	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-RWD-01	HIGH	P703单排后驱Chassis Cab外廓。	READY
152213	152213	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	HIGH	P703 Double Cab外廓。	READY
152273	152273	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	HIGH	P703 Single Cab外廓。	READY
152630	152630	Pickup	Ranger IV	P703	2	EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-4X4-01	HIGH	P703单排四驱Chassis Cab外廓。	READY
152202	152202	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
152670	152670	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	HIGH	P703 Super Cab外廓。	READY
157843	157843	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	HIGH	P703 Double Cab Raptor宽体外廓。	READY
801294_xlt	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-XLT-01	HIGH	P703 Double Cab PHEV XLT外廓。	READY
801294_sport	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-SPORT-01	HIGH	P703 Double Cab PHEV Sport外廓。	READY
801294_wildtrak_stormtrak	801294	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-PHEV-WILDTRAK-STORMTRAK-01	HIGH	P703 Double Cab PHEV Wildtrak与Stormtrak共用外廓。	READY
152205	152205	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	HIGH	P703 Double Cab外廓。	READY
152214	152214	Pickup	Ranger IV	P703	4	EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	HIGH	P703 Double Cab Raptor宽体外廓。	READY
8002	8002	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8003	8003	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
47261	47261	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8004	8004	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
8005	8005	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
109826	109826	Sedan	Taurus IV		4	EU-FORD-USA-TAURUS-IV-SEDAN-01	HIGH	第四代Taurus四门Sedan外廓。	READY
14654	14654	Sedan	Taurus III		4	EU-FORD-USA-TAURUS-III-SEDAN-01	HIGH	第三代Taurus四门Sedan外廓。	READY
14655	14655	Wagon	Taurus III		5	EU-FORD-USA-TAURUS-III-WAGON-01	HIGH	第三代Taurus五门Wagon外廓。	READY
124766	124766	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-MN12-COUPE-FACELIFT-01	HIGH	MN12后期双门Coupe外廓。	READY
58103	58103	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-MN12-COUPE-PREFL-01	MEDIUM	4.9发动机限定为MN12前期外廓；输入结束年月晚于该发动机实际边界。	READY
15370_gen1	15370	MPV	Windstar I		3	EU-FORD-USA-WINDSTAR-I-MPV-01	HIGH	Ktype跨越换代，第一代三门乘用MPV外廓。	READY
15370_gen2	15370	MPV	Windstar II		4	EU-FORD-USA-WINDSTAR-II-MPV-01	HIGH	Ktype跨越换代，第二代四门乘用MPV外廓。	READY
143238	143238	Van	Windstar I		3	EU-FORD-USA-WINDSTAR-I-VAN-01	HIGH	第一代三门Cargo Van外廓。	READY
8006	8006	MPV	Windstar I		3	EU-FORD-USA-WINDSTAR-I-MPV-01	HIGH	第一代三门乘用MPV外廓。	READY
157036	157036	SUV	T5 EVO I		5	EU-FORTHING-T5-EVO-I-SUV-01	HIGH	T5 EVO五门SUV外廓。	READY
157037	157037	SUV	T5 EVO I		5	EU-FORTHING-T5-EVO-I-SUV-01	HIGH	LPG版本未改变T5 EVO外廓。	READY
157038	157038	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	M4五门七座MPV外廓。	READY
802898	802898	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	HEV版本与U-Tour M4标准外廓一致。	READY
157039	157039	MPV	U-Tour I	M4	5	EU-FORTHING-U-TOUR-M4-MPV-01	HIGH	LPG版本未改变U-Tour M4外廓。	READY
801811_l2h2	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L2H2-01	MEDIUM	eToano标准轴距中顶货运外廓。	READY
801811_l2h3	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L2H3-01	MEDIUM	eToano标准轴距高顶货运外廓。	READY
801811_l3h2	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L3H2-01	MEDIUM	eToano长轴距中顶货运外廓。	READY
801811_l3h3	801811	Van	eToano I			EU-FOTON-ETOANO-I-VAN-L3H3-01	MEDIUM	eToano长轴距高顶货运外廓。	READY
146456	146456	Pickup	Tunland G7		4	EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	HIGH	Tunland G7四门Double Cab外廓。	READY
801495	801495	Pickup	Tunland G7		4	EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	HIGH	Tunland G7四门Double Cab外廓。	READY
12919	12919	Hatchback	126p I		2	EU-FSO-126P-I-HATCHBACK-01	HIGH	早期126p双门外廓。	READY
12920	12920	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	HIGH	Polonez I早期五门外廓。	READY
12921_prefl	12921	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	MEDIUM	Ktype覆盖Polonez I早期外廓阶段。	READY
12921_facelift	12921	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖Polonez I加长改款外廓阶段。	READY
12922_prefl	12922	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	MEDIUM	Ktype覆盖Polonez I早期外廓阶段。	READY
12922_facelift	12922	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	MEDIUM	Ktype覆盖Polonez I加长改款外廓阶段。	READY
160003	160003	SUV	Aion V II	AY5-G	5	EU-GAC-AION-V-II-SUV-01	HIGH	第二代Aion V国际版五门SUV外廓。	READY
151146	151146	SUV	Galloper II	KNE1CP	3	EU-GALLOPER-GALLOPER-II-SUV-3D-01	HIGH	KNE1CP三门短轴外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6301-6400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-F-150-P552-PICKUP-REGULAR-CAB-6P5FT-01	5316	2029	1948	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-REGULAR-CAB-8FT-01	5789	2029	1946	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-SUPERCREW-5P5FT-01	5890	2029	1953	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-SUPERCREW-6P5FT-01	6190	2029	1953	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-SUPERCAB-6P5FT-01	5890	2029	1953	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-SUPERCAB-8FT-01	6363	2029	1946	Ford 2015 F-150 Source Book dimensions	https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf
EU-FORD-USA-F-150-P552-PICKUP-RAPTOR-SUPERCAB-01	5588	2192	1994	Car and Driver 2017 Ford F-150 Raptor SuperCab specifications	https://www.caranddriver.com/ford/f-150-raptor/specs/2017/ford_f-150-raptor_ford-f-150-raptor_2017
EU-FORD-USA-F-150-P552-PICKUP-RAPTOR-SUPERCREW-01	5890	2192	1994	Edmunds 2017 Ford F-150 Raptor SuperCrew specifications	https://www.edmunds.com/ford/f-150/2017/raptor/features-specs/
EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-5P5FT-PREFL-01	5889	2012	1927	Ford 2011 F-150 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_f150.pdf
EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-5P5FT-FACELIFT-01	5890	2012	1948	Ford 2013 F-150 official brochure	https://dealerinspire-brochure.s3.amazonaws.com/45_2013_ford_f-150_usa.pdf
EU-FORD-USA-F-150-P415-PICKUP-SUPERCREW-6P5FT-FACELIFT-01	6195	2012	1943	Ford 2013 F-150 official brochure	https://dealerinspire-brochure.s3.amazonaws.com/45_2013_ford_f-150_usa.pdf
EU-FORD-USA-F-150-P415-PICKUP-REGULAR-CAB-6P5FT-FACELIFT-01	5415	2012	1930	Ford 2013 F-150 official brochure	https://dealerinspire-brochure.s3.amazonaws.com/45_2013_ford_f-150_usa.pdf
EU-FORD-USA-F-150-P415-PICKUP-REGULAR-CAB-8FT-FACELIFT-01	5890	2012	1930	Ford 2013 F-150 official brochure	https://dealerinspire-brochure.s3.amazonaws.com/45_2013_ford_f-150_usa.pdf
EU-FORD-USA-F-150-P415-PICKUP-SVT-RAPTOR-SUPERCAB-01	5603	2192	1994	Ford 2013 F-150 official brochure	https://dealerinspire-brochure.s3.amazonaws.com/45_2013_ford_f-150_usa.pdf
EU-FORD-USA-F-150-P702-LIGHTNING-SUPERCREW-01	5911	2032	2004	Ford F-150 Lightning official technical specifications	https://cdn.motor1.com/pdf-files/ford-f-150-lightning-specs.pdf
EU-FORD-USA-FLEX-I-SUV-01	5126	1928	1727	Ford Flex 2010 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Flex-2010-USA.pdf
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1965-66-01	4613	1732	1298	Automobile-Catalog 1965 Ford Mustang Convertible Six; 1965 Ford Mustang Fact Sheet	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1965.html;https://over-drive-magazine.com/2022/10/07/1965-ford-mustang-fact-sheet/
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1967-68-01	4663	1801	1306	Automobile-Catalog 1967 and 1968 Ford Mustang Base Convertible; 1967 Ford Mustang Fact Sheet	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1967.html;https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1968.html;https://over-drive-magazine.com/2023/05/31/1967-ford-mustang-fact-sheet/
EU-FORD-USA-MUSTANG-I-CONVERTIBLE-1969-70-01	4760	1811	1303	Automobile-Catalog 1969 and 1970 Ford Mustang Base Convertible	https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1969.html;https://www.automobile-catalog.com/make/ford_usa/mustang_1gen/mustang_1gen_base_convertible/1970.html
EU-FORD-USA-MUSTANG-S197-COUPE-V6-FACELIFT-01	4778	1877	1412	Edmunds 2011 Ford Mustang specifications	https://www.edmunds.com/ford/mustang/2011/features-specs/
EU-FORD-USA-MUSTANG-SN95-COUPE-PREFL-01	4610	1824	1344	Automobile-Catalog 1994 Ford Mustang Coupe 3.8 V6 specifications	https://www.automobile-catalog.com/car/1994/885155/ford_mustang_coupe_3_8l_v-6.html
EU-FORD-USA-MUSTANG-SN95-COUPE-NEW-EDGE-01	4653	1857	1349	Edmunds 1999 Ford Mustang Coupe specifications	https://www.edmunds.com/ford/mustang/1999/coupe/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-FACELIFT-01	4778	1877	1417	Edmunds 2011 Ford Mustang GT specifications	https://www.edmunds.com/ford/mustang/2011/st-101274492/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT500-PREFL-01	4765	1877	1384	Edmunds 2009 Ford Shelby GT500 specifications	https://www.edmunds.com/ford/shelby-gt500/2009/features-specs/
EU-FORD-USA-MUSTANG-S550-COUPE-PREFL-01	4784	1915	1381	Ford 2016 Mustang Technical Specifications; Ford Mustang Owner's Manual Coupe dimensions	https://media.ford.com/content/dam/lincolnmedia/lna/us/product/2016/2016-Ford-Mustang-Tech-Specs.pdf;https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1739779&Uid=G1739776&buildtype=web%2F1000&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=False&variantid=4230
EU-FORD-USA-MUSTANG-S550-COUPE-FACELIFT-01	4788	1915	1379	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-FORD-USA-MUSTANG-S650-COUPE-01	4811	1915	1397	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/features-specs/
EU-FORD-USA-MUSTANG-S650-CONVERTIBLE-01	4811	1915	1392	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Convertible Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/convertible/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-PREFL-01	4765	1877	1407	Edmunds 2009 Ford Mustang Coupe GT specifications	https://www.edmunds.com/ford/mustang/2009/coupe/st-101006668/features-specs/
EU-FORD-USA-MUSTANG-S197-COUPE-GT-2010-01	4778	1877	1412	Edmunds 2010 Ford Mustang Coupe GT specifications	https://www.edmunds.com/ford/mustang/2010/coupe/st-101144372/features-specs/
EU-FORD-USA-MUSTANG-S650-COUPE-DARK-HORSE-01	4818	1918	1402	Ford 2024 Mustang Technical Specifications; Edmunds 2024 Ford Mustang Dark Horse Features & Specs	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewMustang/2024_Ford_Mustang_technical_specification_EU.pdf;https://www.edmunds.com/ford/mustang/2024/dark-horse/features-specs/
EU-FORD-USA-MUSTANG-S550-COUPE-GT350-01	4798	1928	1377	Ford 2016 Shelby GT350 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/2015/08/24/gt350-gt350r-tech-specs.pdf
EU-FORD-USA-MUSTANG-FOX-CONVERTIBLE-01	4562	1735	1323	Automobile-Catalog 1993 Ford Mustang LX Convertible specifications	https://www.automobile-catalog.com/car/1993/870695/ford_mustang_lx_convertible_2_3l_automatic.html
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-V6-FACELIFT-01	4778	1877	1425	Edmunds 2011 Ford Mustang Convertible V6 specifications	https://www.edmunds.com/ford/mustang/2011/convertible/st-101274488/features-specs/
EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-PREFL-01	4610	1824	1341	Automobile-Catalog 1994 Ford Mustang Convertible 3.8 V6 specifications	https://www.automobile-catalog.com/car/1994/885215/ford_mustang_convertible_3_8l_v-6.html
EU-FORD-USA-MUSTANG-SN95-CONVERTIBLE-NEW-EDGE-01	4653	1857	1351	Edmunds 1999 Ford Mustang Convertible specifications	https://www.edmunds.com/ford/mustang/1999/convertible/features-specs/
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-FACELIFT-01	4778	1877	1417	Edmunds 2011 Ford Mustang Convertible GT specifications	https://www.edmunds.com/ford/mustang/2011/convertible/st-101274492/features-specs/
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT500-2013-01	4780	1877	1400	Ford 2014 Shelby GT500 Technical Specifications	https://www.autoinfo.jp/release/Mustang_Shelby_GT500_spec_my14.pdf
EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-PREFL-01	4784	1915	1394	Ford 2016 Mustang Technical Specifications; Ford Mustang Owner's Manual Convertible dimensions	https://media.ford.com/content/dam/lincolnmedia/lna/us/product/2016/2016-Ford-Mustang-Tech-Specs.pdf;https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1739788&Uid=G1739786&buildtype=web%2F1000&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=False&variantid=4230
EU-FORD-USA-MUSTANG-S550-CONVERTIBLE-FACELIFT-01	4788	1915	1394	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-PREFL-01	4765	1877	1415	Automobile-Catalog 2009 Ford Mustang GT Convertible specifications	https://www.automobile-catalog.com/car/2009/1420895/ford_mustang_gt_convertible.html
EU-FORD-USA-MUSTANG-S197-CONVERTIBLE-GT-2010-01	4778	1877	1425	Edmunds 2010 Ford Mustang Convertible GT Premium specifications	https://www.edmunds.com/ford/mustang/2010/convertible/st-101144375/features-specs/
EU-FORD-USA-MUSTANG-MACH-E-I-SUV-STANDARD-01	4713	1881	1624	Ford 2021 Mustang Mach-E Technical Specifications; JATO Dynamics / CarExpert 2024 Ford Mustang Mach-E	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2021/mach-e/Mustang-Mach-E-Tech-Specs.pdf;https://www.carexpert.co.nz/ford/mustang-mach-e/2024
EU-FORD-USA-MUSTANG-MACH-E-I-SUV-GT-01	4742	1882	1608	Ford 2025 Mustang Mach-E Technical Specifications	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025%20Ford-Mustang-Mach-E-Technical-Specifications.pdf
EU-FORD-USA-RANGER-P703-PICKUP-SUPER-CAB-01	5350	1910	1877	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-PICKUP-SINGLE-CAB-01	5350	1910	1883	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-RWD-01	5225	1910	1880	CarExpert 2022 Ford Ranger XL 2D Chassis Cab RWD specifications	https://www.carexpert.co.nz/ford/ranger/2022-xl-2l-chassis-cab-rwd-diesel-automatic-jmmw88fw20221201
EU-FORD-USA-RANGER-P703-PICKUP-DOUBLE-CAB-01	5350	1910	1886	Ford Next-Generation Ranger official brochure	https://www.ford.co.za/content/dam/ecomm/Release-3/ZA/next-gen-ranger/brochure/next-gen-ranger-brochure-feb-2023.pdf
EU-FORD-USA-RANGER-P703-CHASSIS-CAB-SINGLE-CAB-4X4-01	5225	1910	1875	CarExpert 2023 Ford Ranger XL 2.0 Cab Chassis 4x4 specifications	https://www.carexpert.com.au/ford/ranger/2023-xl-2l-cab-chassis-4x4-diesel-automatic-jsamafgm20221110
EU-FORD-USA-RANGER-P703-PICKUP-RAPTOR-01	5381	2028	1922	Auto-Data Ford Ranger IV Double Cab Raptor	https://www.auto-data.net/en/ford-ranger-iv-double-cab-raptor-3.0-ecoboost-v6-292hp-e-4wd-automatic-46825
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-XLT-01	5367	1924	1871	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-SPORT-01	5367	1924	1883	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
EU-FORD-USA-RANGER-P703-PICKUP-PHEV-WILDTRAK-STORMTRAK-01	5367	1924	1878	Ford Ranger PHEV MY2025.75 official brochure	https://media.adtorqueedge.com/new-cars/ford-au/phev-ranger/ranger-phev-brochure.pdf
EU-FORD-USA-TAURUS-III-SEDAN-01	5017	1854	1400	Ford 1998 Taurus Owner's Manual; Edmunds 1999 Ford Taurus Sedan specifications	https://www.carmanualsonline.info/ford-taurus-1998-3-g-owners-manual/?srch=compression+ratio;https://www.edmunds.com/ford/taurus/1999/sedan/features-specs/
EU-FORD-USA-TAURUS-III-WAGON-01	5070	1854	1463	Ford 1998 Taurus Owner's Manual; Edmunds 1999 Ford Taurus Wagon specifications	https://www.carmanualsonline.info/ford-taurus-1998-3-g-owners-manual/?srch=compression+ratio;https://www.edmunds.com/ford/taurus/1999/wagon/features-specs/
EU-FORD-USA-TAURUS-IV-SEDAN-01	5019	1854	1425	Edmunds 2003 Ford Taurus specifications; The Car Connection 2003 Ford Taurus specifications	https://www.edmunds.com/ford/taurus/2003/features-specs/;https://www.thecarconnection.com/specifications/ford_taurus_2003
EU-FORD-USA-THUNDERBIRD-MN12-COUPE-FACELIFT-01	5088	1847	1334	Edmunds 1997 Ford Thunderbird LX specifications	https://www.edmunds.com/ford/thunderbird/1997/st-6073/features-specs/
EU-FORD-USA-THUNDERBIRD-MN12-COUPE-PREFL-01	5047	1847	1339	Automobile-Catalog 1989 Ford Thunderbird SC specifications	https://www.automobile-catalog.com/car/1989/879065/ford_thunderbird_sc.html
EU-FORD-USA-WINDSTAR-I-MPV-01	5110	1915	1727	Edmunds 1995 Ford Windstar specifications	https://www.edmunds.com/ford/windstar/1995/features-specs/
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679	Edmunds 1999 Ford Windstar SE specifications	https://www.edmunds.com/ford/windstar/1999/st-8036/features-specs/
EU-FORD-USA-WINDSTAR-I-VAN-01	5110	1915	1725	Edmunds 1995 Ford Windstar Cargo specifications	https://www.edmunds.com/ford/windstar-cargo/1995/minivan/features-specs/
EU-FORTHING-T5-EVO-I-SUV-01	4565	1860	1690	Dongfeng Forthing T5 EVO official specifications	https://www.forthingmotor.com/chinese-professional-dongfeng-forthing-t5evo-suv-vehicle-product/
EU-FORTHING-U-TOUR-M4-MPV-01	4850	1900	1715	Dongfeng Forthing U-Tour official specifications; Forthing Polska U-Tour HEV 2026 technical data	https://www.forthingmotor.com/dongfeng-mpv-u-tour-product/;https://forthing-auto.pl/document/6/a347909c99b10bb72864d9bdbcc48189.pdf
EU-FOTON-ETOANO-I-VAN-L2H2-01	5495	2000	2445	Foton Spain eToano official technical sheet; Foton official Toano body-width specification	https://www.fotonlcv.es/upload/ficha-tecnica/FOTON_ficha_eToano.pdf;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L2H3-01	5495	2000	2720	Foton Portugal eToano official specifications; Foton official Toano body-width specification	https://foton-portugal.pt/products/etoano/;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L3H2-01	5990	2000	2445	Foton Spain eToano official technical sheet; Foton official Toano body-width specification	https://www.fotonlcv.es/upload/ficha-tecnica/FOTON_ficha_eToano.pdf;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-ETOANO-I-VAN-L3H3-01	5990	2000	2720	Foton Portugal eToano official specifications; Foton official Toano body-width specification	https://foton-portugal.pt/products/etoano/;https://www.foton-africa.com/products/foton-toano-white/
EU-FOTON-TUNLAND-G7-PICKUP-DOUBLE-CAB-01	5340	1940	1870	Foton Tunland G7 official distributor specifications	https://www.fotonnepal.com/vehicle/products/tunland-g7-pickup-van
EU-FSO-126P-I-HATCHBACK-01	3054	1377	1335	Automobile-Catalog 1973 Polski Fiat 126p 600 specifications	https://www.automobile-catalog.com/car/1973/38975/polski_fiat_126p_600.html
EU-FSO-POLONEZ-I-HATCHBACK-PREFL-01	4272	1651	1420	Automobile-Catalog 1982 FSO Polonez 1500 specifications	https://www.automobile-catalog.com/car/1982/24335/fso_polonez_1500.html
EU-FSO-POLONEZ-I-HATCHBACK-FACELIFT-01	4322	1651	1420	Automobile-Catalog 1988 FSO Polonez 1.5 SL specifications	https://www.automobile-catalog.com/car/1988/52760/fso_polonez_1_5_sl.html
EU-GAC-AION-V-II-SUV-01	4605	1854	1686	GAC Australia Aion V official specifications	https://www.gacgroup.com/en-au/configuration/aion-v/2024
EU-GALLOPER-GALLOPER-II-SUV-3D-01	4020	1770	1860	UltimateSpecs Galloper 2.5 TCI; B-Parts Galloper II KNE1CP body identification	https://www.ultimatespecs.com/car-specs/Galloper/5545/Galloper-Galloper-25-TCI.html;https://www.b-parts.co.uk/auto-parts/interior/dashboard-hyundai-galloper-ii-jk-01-1997-1998-1999-2000-2001-2002-2003-27057357
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6301-6400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.co.uk/car-parts/bulb-headlight-10527/ford-usa/f-150/f-150-standard-cab-pickup/108101-3-5-4wd?utm_source=chatgpt.com "FORD USA F-150 Mk13 (P552) Standard Cab Pickup 3.5 4WD ..."
[2]: https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf "https://www.fordfseries.com/wp-content/uploads/2019/01/2019-F150_rozm%C4%9Bry.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3319 行）
- 累计尺寸组：dimension_groups_final.tsv（825 行）

