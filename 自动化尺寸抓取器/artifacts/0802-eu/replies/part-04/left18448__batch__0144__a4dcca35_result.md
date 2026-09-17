# 任务：left18448 第 14301-14400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0144__a4dcca35


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 14301-14400 行

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
left18448 第 14301-14400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14301-14400_ktype_dimension_mapping_final.tsv
- left18448_14301-14400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	4209	1777	1457
EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-SEDAN-4D-01	4498	1777	1460
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	4485	1811	1434

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Renault	Megane ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	May 2005	Jun 2008	18791
Renault	Megane ii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Nov 2002	Feb 2008	16917
Renault	Megane ii	1.6 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2005	Feb 2008	59947
Renault	Megane ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	Nov 2002	Feb 2008	16920
Renault	Megane ii	1.9 DCI	Stufenheck	Frontantrieb	Diesel	Sep 2003	-	17729
Renault	Megane ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	Mar 2004	Aug 2006	18215
Renault	Megane ii	1.9 DCI	Stufenheck	Frontantrieb	Diesel	Mar 2004	-	18216
Renault	Megane ii	1.9 DCI	Stufenheck	Frontantrieb	Diesel	May 2005	-	18786
Renault	Megane ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	May 2005	Dec 2009	18792
Renault	Megane ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	May 2005	Feb 2008	19040
Renault	Megane ii	1.9 DCI	Stufenheck	Frontantrieb	Diesel	May 2005	-	19041
Renault	Megane ii	2.0 16V	Schrägheck	Frontantrieb	Benzin	Nov 2002	Feb 2008	16918
Renault	Megane ii	2.0 16V Turbo	Schrägheck	Frontantrieb	Benzin	May 2004	Feb 2008	18437
Renault	Megane ii	2.0 Renault Sport	Schrägheck	Frontantrieb	Benzin	May 2004	Oct 2009	18081
Renault	Megane ii coupé-	1.6	Cabriolet	Frontantrieb	Benzin	Sep 2003	Mar 2009	17721
Renault	Megane ii coupé-	2	Cabriolet	Frontantrieb	Benzin	Sep 2003	Dec 2009	17722
Renault	Megane ii coupé-	2	Cabriolet	Frontantrieb	Benzin	Sep 2003	Feb 2007	56038
Renault	Megane ii coupé-	1.9 DCI	Cabriolet	Frontantrieb	Diesel	Sep 2003	Mar 2009	17723
Renault	Megane ii coupé-	1.9 DCI	Cabriolet	Frontantrieb	Diesel	May 2005	Feb 2007	18783
Renault	Megane ii coupé-	2.0 16V Turbo	Cabriolet	Frontantrieb	Benzin	May 2004	Mar 2009	18438
Renault	Megane ii grandtour	1.4	Kombi	Frontantrieb	Benzin	Aug 2003	Jul 2009	17730
Renault	Megane ii grandtour	1.6	Kombi	Frontantrieb	Benzin	Aug 2003	Jul 2009	17731
Renault	Megane ii grandtour	2	Kombi	Frontantrieb	Benzin	Aug 2003	Jul 2009	17732
Renault	Megane ii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Aug 2003	May 2006	17733
Renault	Megane ii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Feb 2004	Mar 2006	18218
Renault	Megane ii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	May 2005	Jun 2008	18788
Renault	Megane ii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	May 2005	Jul 2009	18789
Renault	Megane ii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	May 2005	Jul 2009	8178
Renault	Megane ii grandtour	1.6 LPG 16V	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Jan 2006	Aug 2009	124865
Renault	Megane ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	May 2005	Jul 2009	5072
Renault	Megane ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	Aug 2003	Jul 2009	17734
Renault	Megane ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	Mar 2004	Feb 2007	18217
Renault	Megane ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	May 2005	Jul 2009	18787
Renault	Megane ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	May 2005	Jul 2009	19042
Renault	Megane iii	1.2 TCE	Coupe	Frontantrieb	Benzin	Mar 2012	Aug 2015	15530
Renault	Megane iii	1.2 TCE	Schrägheck	Frontantrieb	Benzin	Mar 2012	Aug 2015	16982
Renault	Megane iii	1.2 TCE	Coupe	Frontantrieb	Benzin	Jan 2013	Aug 2015	59339
Renault	Megane iii	1.2 TCE	Schrägheck	Frontantrieb	Benzin	Jan 2013	Jan 2016	59341
Renault	Megane iii	1.5 DCI	Coupe	Frontantrieb	Diesel	Nov 2008	Aug 2015	34764
Renault	Megane iii	1.5 DCI	Coupe	Frontantrieb	Diesel	Feb 2009	Aug 2015	34765
Renault	Megane iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Nov 2013	Aug 2015	100413
Renault	Megane iii	1.5 DCI	Coupe	Frontantrieb	Diesel	Jul 2014	Aug 2015	113303
Renault	Megane iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Nov 2008	Jan 2016	16124
Renault	Megane iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jan 2013	Aug 2015	121722
Renault	Megane iii	1.6 DCI	Schrägheck	Frontantrieb	Diesel	Apr 2011	Aug 2015	15146
Renault	Megane iii	1.6 DCI	Coupe	Frontantrieb	Diesel	Apr 2011	Aug 2015	15189
Renault	Megane iii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	Jul 2012	Aug 2015	56793
Renault	Megane iii	2.0 DCI	Coupe	Frontantrieb	Diesel	Jul 2012	Aug 2015	56794
Renault	Megane iii	2.0 R.s.	Coupe	Frontantrieb	Benzin	Nov 2008	Sep 2016	57297
Renault	Megane iii	2.0 R.s.	Coupe	Frontantrieb	Benzin	Jul 2014	Sep 2016	108031
Renault	Megane iii	2.0 TCE	Coupe	Frontantrieb	Benzin	May 2009	Aug 2015	3
Renault	Megane iii	2.0 TCE	Coupe	Frontantrieb	Benzin	Jun 2012	Aug 2015	59346
Renault	Megane iii	2.0 TCE	Schrägheck	Frontantrieb	Benzin	Jun 2012	Aug 2015	59349
Renault	Megane iii	2.0 TCE 220	Coupe	Frontantrieb	Benzin	Nov 2013	Aug 2015	100411
Renault	Megane iii	2.0 TCE 220	Schrägheck	Frontantrieb	Benzin	Nov 2013	Jan 2016	100412
Renault	Megane iii grandtour	1.2 TCE	Kombi	Frontantrieb	Benzin	Jan 2013	Jan 2016	59340
Renault	Megane iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Mar 2009	Aug 2015	54521
Renault	Megane iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Nov 2013	Aug 2015	100414
Renault	Megane iii grandtour	1.6 DCI	Kombi	Frontantrieb	Diesel	Apr 2011	Aug 2015	15283
Renault	Megane iii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	Jul 2012	Aug 2015	56795
Renault	Megane iii grandtour	2.0 TCE	Kombi	Frontantrieb	Benzin	Sep 2012	Jan 2016	59343
Renault	Megane iii grandtour	2.0 TCE	Kombi	Frontantrieb	Benzin	Sep 2012	Aug 2015	59344
Renault	Megane iv	1.0 TCE 115	Schrägheck	Frontantrieb	Benzin	Oct 2020	-	143488
Renault	Megane iv	1.2 TCE 100	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	117852
Renault	Megane iv	1.2 TCE 130	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	117850
Renault	Megane iv	1.2 TCE 130	Stufenheck	Frontantrieb	Benzin	Oct 2016	-	128575
Renault	Megane iv	1.3 TCE 160	Schrägheck	Frontantrieb	Benzin	Aug 2020	-	145240
Renault	Megane iv	1.5 DCI 110	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	117855
Renault	Megane iv	1.5 DCI 90	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	117854
Renault	Megane iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	124736
Renault	Megane iv	1.6 DCI 130	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	117856
Renault	Megane iv	1.6 DCI 165	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	120270
Renault	Megane iv	1.6 E-tech 160	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2021	-	145204
Renault	Megane iv	1.6 SCE	Stufenheck	Frontantrieb	Benzin	Oct 2016	-	128574
Renault	Megane iv	1.6 TCE 165	Schrägheck	Frontantrieb	Benzin	Jul 2017	-	128472
Renault	Megane iv	1.6 TCE 205	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	117853
Renault	Megane iv grandtour	1.0 TCE 115	Kombi	Frontantrieb	Benzin	Jul 2021	-	145213
Renault	Megane iv grandtour	1.2 TCE 100	Kombi	Frontantrieb	Benzin	Apr 2016	-	120272
Renault	Megane iv grandtour	1.2 TCE 130	Kombi	Frontantrieb	Benzin	Apr 2016	-	120273
Renault	Megane iv grandtour	1.3 TCE 160	Kombi	Frontantrieb	Benzin	Aug 2020	-	145311
Renault	Megane iv grandtour	1.5 DCI 110	Kombi	Frontantrieb	Diesel	Apr 2016	-	120276
Renault	Megane iv grandtour	1.5 DCI 90	Kombi	Frontantrieb	Diesel	Apr 2016	-	120275
Renault	Megane iv grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	Apr 2016	-	127217
Renault	Megane iv grandtour	1.6 DCI 130	Kombi	Frontantrieb	Diesel	Apr 2016	-	120277
Renault	Megane iv grandtour	1.6 DCI 165	Kombi	Frontantrieb	Diesel	Apr 2016	-	120279
Renault	Megane iv grandtour	1.6 TCE 165	Kombi	Frontantrieb	Benzin	Jul 2017	-	128394
Renault	Megane iv grandtour	1.6 TCE 205	Kombi	Frontantrieb	Benzin	Apr 2016	-	120274
Renault	Megane scénic	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Apr 1998	Oct 1999	11406
Renault	Megane scénic	1.9 D	Großraumlimousine	Frontantrieb	Diesel	Mar 1997	Sep 1999	8008
Renault	Megane scénic	2.0 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1999	Sep 1999	11482
Renault	Megane scénic van	1.9 DT	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 1997	Sep 1999	143179
Renault	Megane scénic van	1.9 DTI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 1997	Sep 1999	143180
Renault	Modus / grand	1.2	Schrägheck	Frontantrieb	Benzin	Apr 2011	Dec 2013	10955
Renault	Modus / grand	1.2	Schrägheck	Frontantrieb	Benzin	Dec 2004	Dec 2013	18311
Renault	Modus / grand	1.2	Schrägheck	Frontantrieb	Benzin	May 2005	Oct 2007	18680
Renault	Modus / grand	1.4	Schrägheck	Frontantrieb	Benzin	Dec 2004	Dec 2013	18555
Renault	Modus / grand	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2004	Oct 2007	18312
Renault	Modus / grand	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2004	Dec 2013	18313
Renault	Modus / grand	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Dec 2004	Dec 2013	18314
Renault	Modus / grand	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Dec 2004	Dec 2013	18315


--- Round 1 / 首次发送 ---
## 更新点

* 复用既有 `EU-RENAULT-MEGANE-II-SEDAN-4D-01`，完成 4 个 Mégane II 三厢 Ktype 映射。
* 首次闭合 Mégane II CC 与 Grandtour 两个尺寸组；其不含后视镜宽度分别核定为 1777 mm。([汽车数据网][1])
* 首次闭合 Mégane IV Hatchback、Sedan、Wagon 三个尺寸组，宽度统一采用官方资料中的不含后视镜 1814 mm。
* 首次闭合 Mégane Scénic I 乘用 MPV 和早期标准轴距 Modus 尺寸组。([汽车数据网][2])

## 当前批次进度

* READY Ktype：54 / 100
* 待处理 Ktype：46 / 100
* 本轮复用既有尺寸组：1
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17729	17729	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18216	18216	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18786	18786	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
19041	19041	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17721	17721	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17722	17722	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
56038	56038	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17723	17723	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
18783	18783	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
18438	18438	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17730	17730	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17731	17731	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17732	17732	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17733	17733	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18218	18218	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18788	18788	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18789	18789	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
8178	8178	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
124865	124865	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
5072	5072	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17734	17734	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18217	18217	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18787	18787	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
19042	19042	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
143488	143488	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117852	117852	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117850	117850	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
128575	128575	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-4D-01	HIGH		READY
145240	145240	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117855	117855	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117854	117854	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
124736	124736	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117856	117856	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
120270	120270	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
145204	145204	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
128574	128574	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-4D-01	HIGH		READY
128472	128472	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117853	117853	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
145213	145213	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120272	120272	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120273	120273	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
145311	145311	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120276	120276	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120275	120275	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
127217	127217	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120277	120277	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120279	120279	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
128394	128394	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120274	120274	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
11406	11406	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
8008	8008	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
11482	11482	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
18680	18680	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	输入车身形式为Schrägheck；按Modus五门小型MPV物理车身归一。	READY
18312	18312	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	输入车身形式为Schrägheck；按Modus五门小型MPV物理车身归一。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II 1.6 16V	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-1.6-16v-112hp-30321
EU-RENAULT-MEGANE-II-WAGON-5D-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II 1.6 16V	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-automatic-30335
EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	4359	1814	1447	Renault UK Megane official press kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14254-RenaultMeganePressKitMay2018.pdf
EU-RENAULT-MEGANE-IV-SEDAN-4D-01	4632	1814	1443	Renault Megane GrandCoupe official brochure	https://renault.com.eg/CountriesData/Egypt/images/Brochures/Megane_GrandCoupe.pdf
EU-RENAULT-MEGANE-IV-WAGON-5D-01	4626	1814	1457	Renault UK Megane Sport Tourer official press kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14255-RenaultMeganeSportTourerPressKitMay2018.pdf
EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	4134	1719	1675	Auto-Data Renault Megane Scenic generation	https://www.auto-data.net/en/renault-megane-scenic-generation-6217
EU-RENAULT-MODUS-I-MPV-5D-01	3792	1695	1589	Auto-Data Renault Modus 1.5 dCi 86	https://www.auto-data.net/en/renault-modus-1.5-dci-86hp-10627
```

## 下一步优先处理

1. 核定 10 个 Mégane II Hatchback Ktype 分别覆盖三门、五门还是两种外廓，随后复用已有 3D/5D 尺寸组。
2. 集中处理 Mégane III Hatchback、Coupe、RS 和 Grandtour，按 2014 改款、RS 宽体及 GT 220 外廓拆分。
3. 确认两个 Mégane Scénic Van Ktype 是否与乘用版共享完整外廓。
4. 拆分剩余 Modus Ktype 的标准 Modus、New Modus 与 Grand Modus 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-1.6-16v-112hp-30321 "Renault Megane II CC (Phase II, 2006) 1.6 16V (112 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-megane-scenic-generation-6217 "Renault Megane Scenic | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14301-14400_ktype_dimension_mapping_final.tsv
- left18448_14301-14400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已完成剩余 Mégane II 三门/五门分支，并复用既有 3D、5D、Sedan 尺寸组。
* Mégane III 已按 Hatchback、Coupe、Wagon、Renault Sport 宽体，以及改款前后尺寸差异完成拆分。官方资料分别支持改款前 Hatchback/旅行版、改款后车型及 Renault Sport 外廓。([Dezo's Garage][1])
* Modus 已拆分为初期标准轴距、改款标准轴距和 Grand Modus 三种物理外廓。([汽车目录档案][2])
* Mégane Scénic Van 已按与乘用版共享外部车身处理。
* 两张表已完成机械检查：表头正确、`id` 唯一、尺寸组唯一、映射引用闭合、无孤立尺寸组、三维和来源字段完整。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：145
* PENDING 映射：0
* DIMENSION_GROUP：19
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18791_3dr	18791	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18791_5dr	18791	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
16917_3dr	16917	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
16917_5dr	16917	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
59947_3dr	59947	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
59947_5dr	59947	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
16920_3dr	16920	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
16920_5dr	16920	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
17729	17729	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18215_3dr	18215	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18215_5dr	18215	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18216	18216	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18786	18786	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18792_3dr	18792	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18792_5dr	18792	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
19040_3dr	19040	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
19040_5dr	19040	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
19041	19041	Sedan	Megane II		4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
16918_3dr	16918	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
16918_5dr	16918	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18437_3dr	18437	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18437_5dr	18437	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18081_3dr	18081	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
18081_5dr	18081	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门物理外廓。	READY
17721	17721	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17722	17722	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
56038	56038	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17723	17723	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
18783	18783	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
18438	18438	Convertible	Megane II		2	EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	HIGH		READY
17730	17730	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17731	17731	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17732	17732	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17733	17733	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18218	18218	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18788	18788	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18789	18789	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
8178	8178	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
124865	124865	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
5072	5072	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
17734	17734	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18217	18217	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
18787	18787	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
19042	19042	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-5D-01	HIGH		READY
15530_prefl	15530	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15530_facelift	15530	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
16982_prefl	16982	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
16982_facelift	16982	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59339_prefl	59339	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59339_facelift	59339	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59341_prefl	59341	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59341_facelift	59341	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
34764_prefl	34764	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
34764_facelift	34764	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
34765_prefl	34765	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
34765_facelift	34765	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100413_prefl	100413	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100413_facelift	100413	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
113303	113303	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH		READY
16124_prefl	16124	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
16124_facelift	16124	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
121722_prefl	121722	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
121722_facelift	121722	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15146_prefl	15146	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15146_facelift	15146	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15189_prefl	15189	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15189_facelift	15189	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56793_prefl	56793	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56793_facelift	56793	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56794_prefl	56794	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56794_facelift	56794	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
57297	57297	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-RS-COUPE-3D-01	HIGH	Renault Sport宽体外廓。	READY
108031	108031	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-RS-COUPE-3D-01	HIGH	Renault Sport宽体外廓。	READY
3_prefl	3	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
3_facelift	3	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59346_prefl	59346	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59346_facelift	59346	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59349_prefl	59349	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59349_facelift	59349	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100411_prefl	100411	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100411_facelift	100411	Coupe	Megane III		3	EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100412_prefl	100412	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100412_facelift	100412	Hatchback	Megane III		5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59340_prefl	59340	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59340_facelift	59340	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
54521_prefl	54521	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
54521_facelift	54521	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100414_prefl	100414	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
100414_facelift	100414	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15283_prefl	15283	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
15283_facelift	15283	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56795_prefl	56795	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
56795_facelift	56795	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59343_prefl	59343	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59343_facelift	59343	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59344_prefl	59344	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
59344_facelift	59344	Wagon	Megane III		5	EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨2014年改款，外廓长度变化。	READY
143488	143488	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117852	117852	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117850	117850	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
128575	128575	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-4D-01	HIGH		READY
145240	145240	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117855	117855	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117854	117854	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
124736	124736	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117856	117856	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
120270	120270	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
145204	145204	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
128574	128574	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-4D-01	HIGH		READY
128472	128472	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
117853	117853	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	HIGH		READY
145213	145213	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120272	120272	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120273	120273	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
145311	145311	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120276	120276	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120275	120275	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
127217	127217	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120277	120277	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120279	120279	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
128394	128394	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
120274	120274	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-5D-01	HIGH		READY
11406	11406	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
8008	8008	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
11482	11482	MPV	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	HIGH		READY
143179	143179	Van	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	MEDIUM	商用厢式衍生版与乘用版共享外部车身。	READY
143180	143180	Van	Megane Scenic I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	MEDIUM	商用厢式衍生版与乘用版共享外部车身。	READY
10955_facelift	10955	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖改款Modus与Grand Modus外廓。	READY
10955_grand	10955	MPV	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖改款Modus与Grand Modus外廓。	READY
18311_prefl	18311	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18311_facelift	18311	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18311_grand	18311	MPV	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18680	18680	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	输入车身形式为Schrägheck；按Modus五门小型MPV物理车身归一。	READY
18555_prefl	18555	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前与改款后外廓；1.4版本不建立Grand分支。	READY
18555_facelift	18555	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖标准Modus改款前与改款后外廓；1.4版本不建立Grand分支。	READY
18312	18312	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	输入车身形式为Schrägheck；按Modus五门小型MPV物理车身归一。	READY
18313_prefl	18313	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18313_facelift	18313	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18313_grand	18313	MPV	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18314_prefl	18314	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18314_facelift	18314	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18314_grand	18314	MPV	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18315_prefl	18315	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18315_facelift	18315	MPV	Modus I		5	EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
18315_grand	18315	MPV	Grand Modus I		5	EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	MEDIUM	同一Ktype覆盖标准Modus改款前、改款后及Grand Modus外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_14301-14400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	4209	1777	1457	Drive.Place Renault Megane II 3-door Hatchback	https://renault.drive.place/megane/ii/group_hatchback_3d/245016
EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	4209	1777	1458	Drive.Place Renault Megane II 5-door Hatchback	https://renault.drive.place/megane/ii/group_hatchback_5d/245226
EU-RENAULT-MEGANE-II-SEDAN-4D-01	4498	1777	1460	Auto-Data Renault Megane II Classic Phase II	https://www.auto-data.net/en/renault-megane-ii-classic-phase-ii-2006-1.6-16v-112hp-automatic-30336
EU-RENAULT-MEGANE-II-CC-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-1.6-16v-112hp-30321
EU-RENAULT-MEGANE-II-WAGON-5D-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-automatic-30335
EU-RENAULT-MEGANE-III-COUPE-3D-PREFL-01	4299	1804	1423	Renault Megane Coupe official brochure 2011	https://autocatalogarchive.com/wp-content/uploads/2022/02/Renault-Megane-Coupe-2011-UK.pdf
EU-RENAULT-MEGANE-III-COUPE-3D-FACELIFT-01	4312	1804	1423	Renault Megane Coupe and Renaultsport official brochure 2016	https://xr793.com/wp-content/uploads/2022/12/2016-Renault-Megane-Coupe-Renaultsport-UK.pdf
EU-RENAULT-MEGANE-III-HATCHBACK-5D-PREFL-01	4295	1808	1471	Renault Megane Hatch and Sport Tourer official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Renault-Megane-Hatch-ST-UK.pdf
EU-RENAULT-MEGANE-III-HATCHBACK-5D-FACELIFT-01	4302	1808	1471	Renault Megane official brochure 2014	https://autocatalogarchive.com/wp-content/uploads/2022/02/Renault-Megane-2014-UK.pdf
EU-RENAULT-MEGANE-III-RS-COUPE-3D-01	4299	1848	1435	Renault Megane Coupe and Renaultsport official brochure 2016	https://xr793.com/wp-content/uploads/2022/12/2016-Renault-Megane-Coupe-Renaultsport-UK.pdf
EU-RENAULT-MEGANE-III-WAGON-5D-PREFL-01	4559	1804	1507	Renault Megane Hatch and Sport Tourer official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Renault-Megane-Hatch-ST-UK.pdf
EU-RENAULT-MEGANE-III-WAGON-5D-FACELIFT-01	4567	1804	1507	Renault Megane official brochure 2014	https://autocatalogarchive.com/wp-content/uploads/2022/02/Renault-Megane-2014-UK.pdf
EU-RENAULT-MEGANE-IV-HATCHBACK-5D-01	4359	1814	1447	Renault UK Megane official press kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14254-RenaultMeganePressKitMay2018.pdf
EU-RENAULT-MEGANE-IV-SEDAN-4D-01	4632	1814	1443	Renault Megane GrandCoupe official brochure	https://renault.com.eg/CountriesData/Egypt/images/Brochures/Megane_GrandCoupe.pdf
EU-RENAULT-MEGANE-IV-WAGON-5D-01	4626	1814	1457	Renault UK Megane Sport Tourer official press kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14255-RenaultMeganeSportTourerPressKitMay2018.pdf
EU-RENAULT-MEGANE-SCENIC-I-MPV-5D-01	4134	1719	1675	Auto-Data Renault Megane Scenic generation	https://www.auto-data.net/en/renault-megane-scenic-generation-6217
EU-RENAULT-MODUS-I-MPV-5D-FACELIFT-01	3874	1695	1586	Renault Modus and Grand Modus official brochure 2011	https://autocatalogarchive.com/wp-content/uploads/2021/06/Renault-Modus-2011-UK.pdf
EU-RENAULT-GRAND-MODUS-I-MPV-5D-01	4034	1695	1586	Renault Modus and Grand Modus official brochure 2011	https://autocatalogarchive.com/wp-content/uploads/2021/06/Renault-Modus-2011-UK.pdf
EU-RENAULT-MODUS-I-MPV-5D-01	3792	1695	1589	Auto-Data Renault Modus 1.5 dCi 86	https://www.auto-data.net/en/renault-modus-1.5-dci-86hp-10627
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_14301-14400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://xr793.com/wp-content/uploads/2022/12/2011-Renault-Megane-Hatch-ST-UK.pdf "https://xr793.com/wp-content/uploads/2022/12/2011-Renault-Megane-Hatch-ST-UK.pdf"
[2]: https://autocatalogarchive.com/wp-content/uploads/2021/06/Renault-Modus-2011-UK.pdf "https://autocatalogarchive.com/wp-content/uploads/2021/06/Renault-Modus-2011-UK.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（877 行）
- 累计尺寸组：dimension_groups_final.tsv（155 行）

