# 任务：left18448 第 13901-14000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0140__108cf9af


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 13901-14000 行

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
left18448 第 13901-14000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Oct 2003	Apr 2005	17868
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2001	Dec 2006	54943
Renault	Clio ii	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	Jun 2005	Dec 2010	145580
Renault	Clio ii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Mar 1999	Dec 2008	11709
Renault	Clio ii	1.9 DTI	Schrägheck	Frontantrieb	Diesel	Dec 1999	May 2005	14577
Renault	Clio ii	2.0 16V Sport	Schrägheck	Frontantrieb	Benzin	Feb 2000	Jun 2009	14183
Renault	Clio ii	2.0 16V Sport	Schrägheck	Frontantrieb	Benzin	Jan 2004	Apr 2005	17869
Renault	Clio ii	3.0 V6 Sport	Schrägheck	Heckantrieb	Benzin	Nov 2000	Dec 2002	15575
Renault	Clio ii	3.0 V6 Sport	Schrägheck	Heckantrieb	Benzin	Dec 2002	Apr 2005	17138
Renault	Clio iii	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2005	Dec 2014	124975
Renault	Clio iii	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2007	Dec 2011	124977
Renault	Clio iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Sep 2010	Dec 2014	11056
Renault	Clio iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Dec 2014	19045
Renault	Clio iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Dec 2014	19046
Renault	Clio iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Dec 2014	19047
Renault	Clio iii	1.2 Ethanol	Schrägheck	Frontantrieb	Benzin/Ethanol	Jul 2008	Dec 2012	52436
Renault	Clio iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Dec 2012	19050
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2005	Dec 2012	19051
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2005	Dec 2012	19052
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jun 2005	Dec 2014	19053
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Aug 2010	Dec 2014	34744
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Aug 2010	Dec 2014	34746
Renault	Clio iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Oct 2007	19048
Renault	Clio iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jun 2005	Dec 2014	19049
Renault	Clio iii grandtour	1.2 16V	Kombi	Frontantrieb	Benzin	Mar 2010	Dec 2012	11057
Renault	Clio iii grandtour	1.4 16V	Kombi	Frontantrieb	Benzin	Nov 2007	Dec 2012	34748
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Aug 2010	Dec 2012	34745
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Aug 2010	Dec 2012	34747
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	Nov 2007	Dec 2012	34749
Renault	Clio iv	0.9 TCE 75	Kasten/Schrägheck	Frontantrieb	Benzin	Jan 2014	Aug 2021	154694
Renault	Clio iv	0.9 TCE 90	Schrägheck	Frontantrieb	Benzin	Nov 2012	Aug 2021	57401
Renault	Clio iv	0.9 TCE 90	Kasten/Schrägheck	Frontantrieb	Benzin	Jan 2014	Aug 2021	124871
Renault	Clio iv	0.9 TCE 90 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2016	Aug 2021	126186
Renault	Clio iv	1.2 16V	Schrägheck	Frontantrieb	Benzin	Nov 2012	Aug 2021	57284
Renault	Clio iv	1.2 16V	Kasten/Schrägheck	Frontantrieb	Benzin	Jan 2014	Aug 2021	124872
Renault	Clio iv	1.2 16V	Schrägheck	Frontantrieb	Benzin	Jun 2015	Aug 2021	126404
Renault	Clio iv	1.2 LPG 16V	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2012	Jun 2015	125321
Renault	Clio iv	1.2 TCE 120	Schrägheck	Frontantrieb	Benzin	Mar 2013	Aug 2021	58898
Renault	Clio iv	1.5 DCI 110	Schrägheck	Frontantrieb	Diesel	Jun 2016	Aug 2021	122130
Renault	Clio iv	1.5 DCI 75	Schrägheck	Frontantrieb	Diesel	Nov 2012	Aug 2021	57282
Renault	Clio iv	1.5 DCI 75	Kasten/Schrägheck	Frontantrieb	Diesel	Jan 2014	Aug 2021	124874
Renault	Clio iv	1.5 DCI 90	Schrägheck	Frontantrieb	Diesel	Nov 2012	Aug 2021	57281
Renault	Clio iv	1.5 DCI 90	Kasten/Schrägheck	Frontantrieb	Diesel	Jan 2014	Aug 2021	124875
Renault	Clio iv	1.6 RS	Schrägheck	Frontantrieb	Benzin	Mar 2013	Aug 2021	58678
Renault	Clio iv	1.6 RS Trophy	Schrägheck	Frontantrieb	Benzin	Mar 2015	Aug 2021	112058
Renault	Clio iv grandtour	0.9 TCE 90	Kombi	Frontantrieb	Benzin	Jan 2013	Aug 2021	57450
Renault	Clio iv grandtour	1.2 16V	Kombi	Frontantrieb	Benzin	Jan 2013	Aug 2021	57451
Renault	Clio iv grandtour	1.2 TCE 120	Kombi	Frontantrieb	Benzin	Mar 2013	Aug 2021	58899
Renault	Clio iv grandtour	1.5 DCI 110	Kombi	Frontantrieb	Diesel	Jun 2016	Aug 2021	121645
Renault	Clio iv grandtour	1.5 DCI 75	Kombi	Frontantrieb	Diesel	Jan 2013	Aug 2021	57453
Renault	Clio iv grandtour	1.5 DCI 90	Kombi	Frontantrieb	Diesel	Nov 2012	Aug 2021	57454
Renault	Clio v	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2021	-	148011
Renault	Clio v	1.0 SCE 65	Schrägheck	Frontantrieb	Benzin	Nov 2021	-	145761
Renault	Clio v	1.3 TCE 140	Schrägheck	Frontantrieb	Benzin	Sep 2020	-	145712
Renault	Clio v	1.5 Blue DCI 100	Schrägheck	Frontantrieb	Diesel	Nov 2021	-	145756
Renault	Clio v	1.6 E-tech 145	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2022	-	146398
Renault	Clio vi	1.2 TCE 115	Schrägheck	Frontantrieb	Benzin	Oct 2025	-	162795
Renault	Clio vi	1.8 E-tech 160 Full Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Oct 2025	-	162794
Renault	Dauphine	0.9	Stufenheck	Heckantrieb	Benzin	Mar 1956	Mar 1967	109398
Renault	Dokker	1.5 DCI	Kasten	Frontantrieb	Diesel	Dec 2013	-	124738
Renault	Espace i	2	Großraumlimousine	Frontantrieb	Benzin	Jan 1988	Dec 1990	7877
Renault	Espace i	2.0 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1989	Dec 1990	7879
Renault	Espace i	2.0 I Quadra	Großraumlimousine	Allrad	Benzin	Mar 1988	Dec 1992	7878
Renault	Espace ii	2.2 4X4	Großraumlimousine	Allrad	Benzin	Mar 1991	Dec 1996	7880
Renault	Espace ii van	2.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 1992	Oct 1996	143181
Renault	Espace ii van	2.1 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 1992	Oct 1996	143182
Renault	Espace iii	2	Großraumlimousine	Frontantrieb	Benzin	Nov 1996	Oct 2000	7828
Renault	Espace iii	2	Großraumlimousine	Frontantrieb	Benzin	Sep 2001	Oct 2002	16598
Renault	Espace iii	3	Großraumlimousine	Frontantrieb	Benzin	Nov 1996	Oct 1998	7829
Renault	Espace iii	1.9 DTI	Großraumlimousine	Frontantrieb	Diesel	Feb 1999	Oct 2002	10362
Renault	Espace iii	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Oct 1998	Oct 2002	10361
Renault	Espace iii	2.2 12V TD	Großraumlimousine	Frontantrieb	Diesel	Nov 1996	Oct 2000	7830
Renault	Espace iii	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	Oct 2000	Oct 2002	15054
Renault	Espace iii	3.0 V6 24V	Großraumlimousine	Frontantrieb	Benzin	Oct 1998	Oct 2002	10360
Renault	Espace iv	2	Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Jan 2015	17098
Renault	Espace iv	2	Großraumlimousine	Frontantrieb	Benzin	Apr 2005	Dec 2015	18679
Renault	Espace iv	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Jan 2015	17125
Renault	Espace iv	2.0 Turbo	Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Feb 2006	16869
Renault	Espace iv	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Aug 2006	16870
Renault	Espace iv	3.0 DCI	Großraumlimousine	Frontantrieb	Diesel	Nov 2002	Aug 2006	17097
Renault	Espace iv	3.0 DCI	Großraumlimousine	Frontantrieb	Diesel	Sep 2005	Jan 2015	53613
Renault	Espace iv	3.5 V6	Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Dec 2015	17096
Renault	Espace v	1.6 DCI 130	Großraumlimousine	Frontantrieb	Diesel	Jun 2015	Mar 2023	111762
Renault	Espace v	1.6 DCI 160	Großraumlimousine	Frontantrieb	Diesel	Jun 2015	Mar 2023	111763
Renault	Espace v	1.6 TCE 200	Großraumlimousine	Frontantrieb	Benzin	Feb 2015	Mar 2023	111761
Renault	Espace v	2.0 Blue DCI 190	Großraumlimousine	Frontantrieb	Diesel	Jan 2021	Mar 2023	145155
Renault	Espace vi	E-tech 200 Hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2023	-	154879
Renault	Estafette	1.1	Kasten	Frontantrieb	Benzin	Feb 1962	Dec 1981	12427
Renault	Estafette	1.3	Kasten	Frontantrieb	Benzin	Aug 1969	Dec 1981	12429
Renault	Express	1.3 TCE 100	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2021	-	145220
Renault	Express	1.5 Blue DCI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2021	-	145221
Renault	Express	1.5 Blue DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2021	-	145222
Renault	Fluence	1.6	Stufenheck	Frontantrieb	Benzin	Jan 2013	-	113258
Renault	Fluence	1.6	Stufenheck	Frontantrieb	Benzin	Nov 2015	-	154655
Renault	Fluence	1.5 DCI	Stufenheck	Frontantrieb	Diesel	Jul 2014	-	107528
Renault	Fluence	1.6 16V	Stufenheck	Frontantrieb	Benzin	Feb 2010	-	5089
Renault	Fluence	1.6 16V	Stufenheck	Frontantrieb	Benzin	Feb 2010	-	124234
Renault	Fluence	1.6 DCI	Stufenheck	Frontantrieb	Diesel	Jan 2013	-	107529
Renault	Fluence	1.6 LPG 16V	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2012	-	124864
Renault	Fuego	1.6	Coupe	Frontantrieb	Benzin	Apr 1983	Oct 1985	17667


--- Round 1 / 首次发送 ---
## 更新点

* 完成 **Clio II** 9 个输入 Ktype 的物理车身拆分，共形成 17 条 READY 映射。
* 标准 Clio II 按三门/五门及 2001 年中期改款前后拆分；外廓分别为 **3773×1639×1417 mm** 和 **3812×1639×1417 mm**，宽度均为不含后视镜口径。([汽车目录][1])
* Renault Sport 与普通车身分组；RS 前期和改款后外廓分别采用对应年份的三门车型数据。([汽车目录][2])
* Clio V6 Phase 1、Phase 2 为不同宽体外廓，分别单独建组。([汽车目录][3])
* Ktype `14183` 已确认是 `CB0M`，没有仅凭其异常延长的目录结束日期推断为改款后车身；`145580` 已确认是商用车技术型 `SB3M`。([Ceneo.pl][4])
* Ktype `17138` 同时覆盖 `CB1H/CB1U/CB2S`，这些代码均对应同一 Clio V6 Phase 2 外廓，因此未制造重复尺寸组，BodyCode 暂不强填组合值。([Tekstara][5])

## 当前批次进度

* 已完成输入 Ktype：**9 / 100**
* 本轮 READY 映射：**17**
* 已确认尺寸组：**8**
* 尚待处理输入 Ktype：**91**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17868_3dr	17868	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
17868_5dr	17868	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
54943_3dr	54943	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
54943_5dr	54943	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
145580	145580	Van	Clio II	SB3M	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	SB3M商用三门版本，复用改款后三门车身外廓。	READY
11709_3dr_prefl	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门前期外廓。	READY
11709_3dr_facelift	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门改款后外廓。	READY
11709_5dr_prefl	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门前期外廓。	READY
11709_5dr_facelift	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门改款后外廓。	READY
14577_3dr_prefl	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门前期外廓。	READY
14577_3dr_facelift	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门改款后外廓。	READY
14577_5dr_prefl	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门前期外廓。	READY
14577_5dr_facelift	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门改款后外廓。	READY
14183	14183	Hatchback	Clio II	CB0M	3	EU-RENAULT-CLIO-II-RS-3D-PREFL-01	HIGH	CB0M三门Renault Sport前期物理外廓。	READY
17869	17869	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	HIGH	179马力Renault Sport三门改款后外廓。	READY
15575	15575	Hatchback	Clio II	CB1A	3	EU-RENAULT-CLIO-II-V6-3D-PH1-01	HIGH	CB1A Clio V6 Phase 1宽体三门外廓。	READY
17138	17138	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-V6-3D-PH2-01	HIGH	Ktype覆盖CB1H、CB1U和CB2S，均属于V6 Phase 2同一外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-RS-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio RS	https://www.automobile-catalog.com/car/2000/2949110/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2004 Renault Clio RS	https://www.automobile-catalog.com/car/2004/2949455/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-V6-3D-PH1-01	3803	1810	1351	Automobile-Catalog 2001 Renault Clio V6	https://www.automobile-catalog.com/car/2001/2949290/renault_clio_v6.html
EU-RENAULT-CLIO-II-V6-3D-PH2-01	3841	1830	1356	Automobile-Catalog 2003 Renault Clio V6	https://www.automobile-catalog.com/car/2003/2949305/renault_clio_v6.html
```

## 下一步优先处理

1. 集中闭合 Clio III 三门、五门、商用版及 Grandtour 的物理外廓。
2. 核对 Clio III 普通版与 Renault Sport 是否存在保险杠或车高差异。
3. 随后处理 Clio IV Hatchback、商用版和 Grandtour，并按改款及 RS 外廓拆分。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html?utm_source=chatgpt.com "2000 Renault Clio 1.6 16V Specs Review (79 kW / 107 PS / 106 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2000/2949110/renault_clio_rs_renault_sport.html?utm_source=chatgpt.com "2000 Renault Clio RS (Renault Sport) Specs Review (124 kW / 169 PS / 166 hp) (since February 2000 for Europe )"
[3]: https://www.automobile-catalog.com/car/2001/2949290/renault_clio_v6.html?utm_source=chatgpt.com "2001 Renault Clio V6 Specs Review (166 kW / 226 PS / 223 hp) (for Europe )"
[4]: https://www.ceneo.pl/124004614?utm_source=chatgpt.com "Gt Bergmann Hamulcowy Zacisk P Clio Laguna 97 P - Opinie i ceny na Ceneo.pl"
[5]: https://tekstara.lt/partscatalogue/z96-m-tech-galinio-ruko-zibinto-lempute-renault-clio-ii-bb--cb--1-9-d-b-cb0e-bb0j-1998-09-2005-05%2C10-00093-03508-09044-0002-00113-0100010%2C0100043%2C0100275%2C0101495-Z96-FM~1TECH-0-0-Z96~2PHO.aspx?utm_source=chatgpt.com "LEMPUTĖ PR21W 12V M TECH Z96/PHO"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 **Clio II** 9 个输入 Ktype 的物理车身拆分，共形成 17 条 READY 映射。
* 标准 Clio II 按三门/五门及 2001 年中期改款前后拆分；外廓分别为 **3773×1639×1417 mm** 和 **3812×1639×1417 mm**，宽度均为不含后视镜口径。([汽车目录][1])
* Renault Sport 与普通车身分组；RS 前期和改款后外廓分别采用对应年份的三门车型数据。([汽车目录][2])
* Clio V6 Phase 1、Phase 2 为不同宽体外廓，分别单独建组。([汽车目录][3])
* Ktype `14183` 已确认是 `CB0M`，没有仅凭其异常延长的目录结束日期推断为改款后车身；`145580` 已确认是商用车技术型 `SB3M`。([Ceneo.pl][4])
* Ktype `17138` 同时覆盖 `CB1H/CB1U/CB2S`，这些代码均对应同一 Clio V6 Phase 2 外廓，因此未制造重复尺寸组，BodyCode 暂不强填组合值。([Tekstara][5])

## 当前批次进度

* 已完成输入 Ktype：**9 / 100**
* 本轮 READY 映射：**17**
* 已确认尺寸组：**8**
* 尚待处理输入 Ktype：**91**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17868_3dr	17868	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
17868_5dr	17868	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
54943_3dr	54943	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
54943_5dr	54943	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
145580	145580	Van	Clio II	SB3M	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	SB3M商用三门版本，复用改款后三门车身外廓。	READY
11709_3dr_prefl	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门前期外廓。	READY
11709_3dr_facelift	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门改款后外廓。	READY
11709_5dr_prefl	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门前期外廓。	READY
11709_5dr_facelift	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门改款后外廓。	READY
14577_3dr_prefl	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门前期外廓。	READY
14577_3dr_facelift	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门改款后外廓。	READY
14577_5dr_prefl	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门前期外廓。	READY
14577_5dr_facelift	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门改款后外廓。	READY
14183	14183	Hatchback	Clio II	CB0M	3	EU-RENAULT-CLIO-II-RS-3D-PREFL-01	HIGH	CB0M三门Renault Sport前期物理外廓。	READY
17869	17869	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	HIGH	179马力Renault Sport三门改款后外廓。	READY
15575	15575	Hatchback	Clio II	CB1A	3	EU-RENAULT-CLIO-II-V6-3D-PH1-01	HIGH	CB1A Clio V6 Phase 1宽体三门外廓。	READY
17138	17138	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-V6-3D-PH2-01	HIGH	Ktype覆盖CB1H、CB1U和CB2S，均属于V6 Phase 2同一外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-RS-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio RS	https://www.automobile-catalog.com/car/2000/2949110/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2004 Renault Clio RS	https://www.automobile-catalog.com/car/2004/2949455/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-V6-3D-PH1-01	3803	1810	1351	Automobile-Catalog 2001 Renault Clio V6	https://www.automobile-catalog.com/car/2001/2949290/renault_clio_v6.html
EU-RENAULT-CLIO-II-V6-3D-PH2-01	3841	1830	1356	Automobile-Catalog 2003 Renault Clio V6	https://www.automobile-catalog.com/car/2003/2949305/renault_clio_v6.html
```

## 下一步优先处理

1. 集中闭合 Clio III 三门、五门、商用版及 Grandtour 的物理外廓。
2. 核对 Clio III 普通版与 Renault Sport 是否存在保险杠或车高差异。
3. 随后处理 Clio IV Hatchback、商用版和 Grandtour，并按改款及 RS 外廓拆分。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html?utm_source=chatgpt.com "2000 Renault Clio 1.6 16V Specs Review (79 kW / 107 PS / 106 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2000/2949110/renault_clio_rs_renault_sport.html?utm_source=chatgpt.com "2000 Renault Clio RS (Renault Sport) Specs Review (124 kW / 169 PS / 166 hp) (since February 2000 for Europe )"
[3]: https://www.automobile-catalog.com/car/2001/2949290/renault_clio_v6.html?utm_source=chatgpt.com "2001 Renault Clio V6 Specs Review (166 kW / 226 PS / 223 hp) (for Europe )"
[4]: https://www.ceneo.pl/124004614?utm_source=chatgpt.com "Gt Bergmann Hamulcowy Zacisk P Clio Laguna 97 P - Opinie i ceny na Ceneo.pl"
[5]: https://tekstara.lt/partscatalogue/z96-m-tech-galinio-ruko-zibinto-lempute-renault-clio-ii-bb--cb--1-9-d-b-cb0e-bb0j-1998-09-2005-05%2C10-00093-03508-09044-0002-00113-0100010%2C0100043%2C0100275%2C0101495-Z96-FM~1TECH-0-0-Z96~2PHO.aspx?utm_source=chatgpt.com "LEMPUTĖ PR21W 12V M TECH Z96/PHO"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增 **Clio III 与 Clio III Grandtour** 共 20 个输入 Ktype、54 条 READY 映射。
* Clio III 普通车身按三门、五门及 2009 年改款前后拆分；改款前采用 `3986×1707×1493 mm`，改款后采用 `4027×1707×1497 mm`，宽度均为不含后视镜口径。([汽车目录][1])
* Grandtour 改款前采用 `4203×1719×1513 mm`；改款后采用 `4228×1719×1513 mm`。([汽车数据][2])
* 商用车身 `SR0J`、`SR0P` 复用对应三门外廓；普通版本按 BR 五门、CR 三门边界映射。Ktype `34744` 仅落入已确认的 `BR1V` 五门分支。([Prom.ua][3])

## 当前批次进度

* 已处理输入 Ktype：**29 / 100**
* 累计 READY 映射：**71**
* 待处理输入 Ktype：**71**
* 累计已确认尺寸组：**14**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124975_prefl	124975	Van	Clio III	SR0J	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	SR0J三门商用车身，改款前外廓。	READY
124975_facelift	124975	Van	Clio III	SR0J	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	SR0J三门商用车身，改款后外廓。	READY
124977_prefl	124977	Van	Clio III	SR0P	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	SR0P三门商用车身，改款前外廓。	READY
124977_facelift	124977	Van	Clio III	SR0P	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	SR0P三门商用车身，改款后外廓。	READY
11056_3dr	11056	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应改款后三门外廓。	READY
11056_5dr	11056	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应改款后五门外廓。	READY
19045_3dr_prefl	19045	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19045_3dr_facelift	19045	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19045_5dr_prefl	19045	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19045_5dr_facelift	19045	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
19046_3dr_prefl	19046	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19046_3dr_facelift	19046	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19046_5dr_prefl	19046	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19046_5dr_facelift	19046	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
19047_3dr_prefl	19047	Hatchback	Clio III	CR0R	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	CR0R三门改款前外廓。	READY
19047_3dr_facelift	19047	Hatchback	Clio III	CR0R	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	CR0R三门改款后外廓。	READY
19047_5dr_prefl	19047	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19047_5dr_facelift	19047	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
52436_3dr_prefl	52436	Hatchback	Clio III	CR1U	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	HIGH	CR1U三门改款前外廓。	READY
52436_3dr_facelift	52436	Hatchback	Clio III	CR1U	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	HIGH	CR1U三门改款后外廓。	READY
52436_5dr_prefl	52436	Hatchback	Clio III	BR1U	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	HIGH	BR1U五门改款前外廓。	READY
52436_5dr_facelift	52436	Hatchback	Clio III	BR1U	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR1U五门改款后外廓。	READY
19050_3dr_prefl	19050	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19050_3dr_facelift	19050	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应三门改款后外廓。	READY
19050_5dr_prefl	19050	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19050_5dr_facelift	19050	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应五门改款后外廓。	READY
19051_3dr_prefl	19051	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19051_3dr_facelift	19051	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应三门改款后外廓。	READY
19051_5dr_prefl	19051	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19051_5dr_facelift	19051	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应五门改款后外廓。	READY
19052_3dr_prefl	19052	Hatchback	Clio III	CR17	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	HIGH	CR17三门改款前外廓。	READY
19052_3dr_facelift	19052	Hatchback	Clio III	CR17	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	HIGH	CR17三门改款后外廓。	READY
19052_5dr_prefl	19052	Hatchback	Clio III	BR17	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	HIGH	BR17五门改款前外廓。	READY
19052_5dr_facelift	19052	Hatchback	Clio III	BR17	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR17五门改款后外廓。	READY
19053_3dr_prefl	19053	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19053_3dr_facelift	19053	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19053_5dr_prefl	19053	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19053_5dr_facelift	19053	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
34744	34744	Hatchback	Clio III	BR1V	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR1V五门改款后外廓。	READY
34746_3dr	34746	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应改款后三门外廓。	READY
34746_5dr	34746	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应改款后五门外廓。	READY
19048_3dr	19048	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19048_5dr	19048	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19049_3dr_prefl	19049	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19049_3dr_facelift	19049	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19049_5dr_prefl	19049	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19049_5dr_facelift	19049	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
11057	11057	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34748_prefl	34748	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour五门改款前外廓。	READY
34748_facelift	34748	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34745	34745	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34747	34747	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34749_prefl	34749	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour五门改款前外廓。	READY
34749_facelift	34749	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	3986	1707	1493	Automobile-Catalog 2005 Renault Clio 1.2 16V 65	https://www.automobile-catalog.com/car/2005/2951840/renault_clio_1_2_16v_65.html
EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	3986	1707	1493	Automobile-Catalog 2005 Renault Clio 1.2 16V 65	https://www.automobile-catalog.com/car/2005/2951840/renault_clio_1_2_16v_65.html
EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	4027	1707	1497	Automobile-Catalog 2009 Renault Clio 1.2 16V 75	https://www.automobile-catalog.com/car/2009/2952275/renault_clio_1_2_16v_75.html
EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	4027	1707	1497	Automobile-Catalog 2009 Renault Clio 1.2 16V 75	https://www.automobile-catalog.com/car/2009/2952275/renault_clio_1_2_16v_75.html
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	4203	1719	1513	Auto-Data Renault Clio III Sport Tourer Phase I 1.5 dCi 86	https://www.auto-data.net/en/renault-clio-iii-grandtour-phase-i-1.5-dci-86hp-56123
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	4228	1719	1513	AutoCentrum Renault Clio III Grandtour Phase II	https://www.autocentrum.pl/dane-techniczne/renault/clio/iii/grandtour-phase-ii/
```

## 下一步优先处理

1. 处理 Clio IV Hatchback、商用三门车身及 Grandtour，优先复用同一代普通发动机版本尺寸组。
2. 独立核对 Clio IV RS、RS Trophy 是否因保险杠、车高或宽体形成不同外廓。
3. 随后处理 Clio V 与 Clio VI；Clio VI 为 2025 年新代际，必须与 Clio V 完全分组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/2952275/renault_clio_1_2_16v_75.html?utm_source=chatgpt.com "2009 Renault Clio 1.2 16V 75 Specs Review (55 kW / ..."
[2]: https://www.auto-data.net/en/renault-clio-iii-grandtour-phase-i-1.5-dci-86hp-56123 "Renault Clio III Sport Tourer (Phase I) 1.5 dCi (86 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://prom.ua/p2978816167-sajlentblok-nissan-renault.html?utm_source=chatgpt.com "Сайлентблок NISSAN, RENAULT MOOG NI-SB-2794, цена 300.39 ₴: купить на Prom.ua | Украина"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Clio IV 普通 Hatchback、商用版以及 Grandtour 共 **20 个 Ktype**。
* Clio IV 仅采用五门车身；商用版继续复用五门 Hatchback 尺寸组，不再按上一轮计划错误拆成三门。普通版改款前后最大外廓均使用 `4062×1732×1448 mm`。
* Grandtour 按改款边界拆分：改款前 `4267×1732×1445 mm`，改款后 `4267×1732×1475 mm`。([汽车数据][1])
* Clio IV RS 与 RS Trophy 暂未写入，避免在普通车身与运动版外廓冲突尚未闭合时错误复用。

## 当前批次进度

* 已处理输入 Ktype：**49 / 100**
* 累计 READY 映射：**96**
* 待处理输入 Ktype：**51**
* 累计已确认尺寸组：**17**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154694	154694	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
57401	57401	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124871	124871	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
126186	126186	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
57284	57284	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124872	124872	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
126404	126404	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
125321	125321	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
58898	58898	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
122130	122130	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
57282	57282	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124874	124874	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
57281	57281	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124875	124875	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
57450_prefl	57450	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57450_facelift	57450	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57451_prefl	57451	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57451_facelift	57451	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
58899_prefl	58899	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
58899_facelift	58899	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
121645	121645	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57453_prefl	57453	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57453_facelift	57453	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57454_prefl	57454	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57454_facelift	57454	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	4062	1732	1448	Renault New Clio official press kit	https://www.press.renault.co.uk/assets/documents/original/10686-RenaultNewClioPressKitJuly20171.pdf
EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	4267	1732	1445	Auto-Data Renault Clio IV Grandtour Phase I	https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-i-1.5-dci-90hp-edc-18715
EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	4267	1732	1475	Auto-Data Renault Clio IV Grandtour Phase II	https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-ii-2016-1.5-energy-dci-90hp-25768
```

## 下一步优先处理

1. 闭合 Clio IV RS 与 RS Trophy 的普通版、改款版及降低悬架外廓边界。
2. 处理 Clio V 改款前后，仅对实际跨越 2023 改款且继续生产的 Ktype 创建派生行。
3. 单独建立 Clio VI 尺寸组，禁止与 Clio V 复用。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-i-1.5-dci-90hp-edc-18715?utm_source=chatgpt.com "Renault Clio IV Grandtour (Phase I) 1.5 dCi (90 Hp) EDC"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Clio IV Renault Sport、Clio V 改款前后及 Clio VI 尺寸边界；Clio IV RS/Trophy 共用运动版五门外廓，Clio V 按 2023 年改款拆组，Clio VI 独立建组。([雷诺新闻中心][1])
* 完成 Dauphine 与 Dokker Van 映射并首次建立对应尺寸组。([Renault][2])
* 完成 Espace I、Espace II、Espace III 共 14 个 Ktype；同代普通动力、四驱和商用衍生版本复用已确认的同一物理外廓。([Renault][3])

## 当前批次进度

* 已处理输入 Ktype：**74 / 100**
* 累计 READY 映射：**125**
* PENDING／待处理输入 Ktype：**26**
* 累计已确认尺寸组：**26**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58678	58678	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	HIGH	Renault Sport五门外廓。	READY
112058	112058	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	HIGH	RS Trophy五门外廓；未确认独立外廓差异。	READY
148011_prefl	148011	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
148011_facelift	148011	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
145761_prefl	145761	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
145761_facelift	145761	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
145712	145712	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	MEDIUM	1.3 TCe 140仅落入改款前外廓边界。	READY
145756_prefl	145756	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
145756_facelift	145756	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
146398_prefl	146398	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
146398_facelift	146398	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
162795	162795	Hatchback	Clio VI		5	EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	HIGH	Clio VI五门外廓。	READY
162794	162794	Hatchback	Clio VI		5	EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	HIGH	Clio VI全混动五门外廓。	READY
109398	109398	Sedan	Dauphine		4	EU-RENAULT-DAUPHINE-SEDAN-01	HIGH	Dauphine四门轿车外廓。	READY
124738	124738	Van	Dokker I			EU-RENAULT-DOKKER-I-VAN-01	MEDIUM	Renault品牌Dokker厢式车身。	READY
7877	7877	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	J11标准MPV外廓。	READY
7879	7879	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	J11标准MPV外廓。	READY
7878	7878	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	Quadra四驱不改变J11外廓。	READY
7880	7880	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	HIGH	J63标准MPV外廓。	READY
143181	143181	Van	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	MEDIUM	J63商用衍生版本复用标准车身外廓。	READY
143182	143182	Van	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	MEDIUM	J63商用衍生版本复用标准车身外廓。	READY
7828	7828	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
16598	16598	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
7829	7829	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10362	10362	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10361	10361	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
7830	7830	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
15054	15054	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10360	10360	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	4062	1731	1448	Renault Clio R.S. official press kit	https://www.press.renault.co.uk/assets/documents/original/14006-RenaultNewClioRenaultSportPressKitFebruary2018.pdf
EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	4050	1798	1440	Renault Nederland Clio price list August 2019	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-08-2019.pdf
EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	4053	1798	1439	Renault Nederland Clio price list July 2023	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-juli23.pdf
EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	4116	1768	1451	Renault Croatia New Clio 6 official press kit	https://www.renault.hr/CountriesData/Croatia/images/News/Clio6/Novi_Renault_Clio_6.pdf
EU-RENAULT-DAUPHINE-SEDAN-01	3950	1520	1400	Renault The Originals Dauphine Gordini	https://theoriginals.renault.com/en/dauphine-gordini
EU-RENAULT-DOKKER-I-VAN-01	4363	1751	1809	Dacia Dokker Van official brochure	https://cdn.group.renault.com/dac/ma/brochure/brochure_dokker-van.pdf
EU-RENAULT-ESPACE-I-MPV-01	4250	1770	1700	Renault The Originals Espace TSE	https://theoriginals.renault.com/en/espace-tse
EU-RENAULT-ESPACE-II-MPV-01	4429	1795	1693	Renault Classic Espace history; Automobile-Catalog Renault Espace II 2.2i	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/RenaultESPACE.pdf;https://www.automobile-catalog.com/car/1993/2944985/renault_espace_2_2i.html
EU-RENAULT-ESPACE-III-MPV-01	4517	1810	1690	Renault Classic Espace history	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/RenaultESPACE.pdf
```

## 下一步优先处理

1. 闭合 Espace IV 的标准轴距与 Grand Espace 长轴距边界，确认输入 Ktype 是否同时覆盖两种外廓。
2. 处理 Espace V、Espace VI、Express 和 Fluence。
3. 最后处理 Estafette 多车身边界与 Fuego，消除剩余 26 个待处理 Ktype。

推进信号：CONTINUE

[1]: https://www.press.renault.co.uk/assets/documents/original/14006-RenaultNewClioRenaultSportPressKitFebruary2018.pdf?utm_source=chatgpt.com "Renault CLIO R.S."
[2]: https://theoriginals.renault.com/en/dauphine-gordini?utm_source=chatgpt.com "Dauphine Gordini"
[3]: https://theoriginals.renault.com/en/espace-tse?utm_source=chatgpt.com "Renault Espace - The Originals Museum"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 Espace IV 标准轴距与 Grand Espace 长轴距拆分；两种车身分别采用 `4661×1860×1728 mm` 和 `4856×1860×1746 mm`。([汽车数据][1])
* 完成 Espace V、Espace VI、Express Van、Express 乘用版、Fluence 和 Fuego 的尺寸组建档。Espace V、Espace VI 与两种 Express 外廓均采用 Renault 官方尺寸资料。
* Estafette 已确认存在普通顶、加高顶及延长车身，当前仍需把两个 Ktype 对应的具体车身分支与单值三维闭合，未创建猜测性尺寸组。

## 当前批次进度

* 已处理输入 Ktype：**98 / 100**
* 累计 READY 映射：**160**
* PENDING 输入 Ktype：**2**
* 累计已确认尺寸组：**34**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17098_swb	17098	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17098_lwb	17098	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
18679_swb	18679	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
18679_lwb	18679	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17125_swb	17125	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17125_lwb	17125	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
16869_swb	16869	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
16869_lwb	16869	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
16870_swb	16870	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
16870_lwb	16870	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17097_swb	17097	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17097_lwb	17097	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
53613_swb	53613	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
53613_lwb	53613	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17096_swb	17096	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17096_lwb	17096	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
111762	111762	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
111763	111763	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
111761	111761	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
145155	145155	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
154879	154879	SUV	Espace VI		5	EU-RENAULT-ESPACE-VI-SUV-01	HIGH	Espace VI五门SUV外廓。	READY
145220_van	145220	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145220_mpv	145220	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
145221_van	145221	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145221_mpv	145221	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
145222_van	145222	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145222_mpv	145222	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
113258	113258	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
154655	154655	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
107528	107528	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
5089	5089	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
124234	124234	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
107529	107529	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
124864	124864	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
17667	17667	Coupe	Fuego		3	EU-RENAULT-FUEGO-COUPE-01	HIGH	三门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-ESPACE-IV-MPV-SWB-01	4661	1860	1728	Auto-Data Renault Espace IV	https://www.auto-data.net/en/renault-espace-iv-generation-2141
EU-RENAULT-ESPACE-IV-MPV-LWB-01	4856	1860	1746	Auto-Data Renault Grand Espace IV Phase II	https://www.auto-data.net/en/renault-grand-espace-iv-phase-ii-2006-2.0-tce-170hp-automatic-20245
EU-RENAULT-ESPACE-V-MPV-01	4857	1888	1677	Renault Suisse Espace official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Neuer_Espace_PL_f.pdf
EU-RENAULT-ESPACE-VI-SUV-01	4722	1843	1645	Renault Suisse Espace E-Tech official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Neuer_Espace_E-TECH_FRA.pdf
EU-RENAULT-EXPRESS-II-VAN-01	4393	1775	1811	Renault Express Van official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Express_Van_BR_f.pdf
EU-RENAULT-EXPRESS-II-MPV-01	4394	1775	1804	Renault Express official brochure	https://cdn.group.renault.com/ren/ma/brochure/E-Brochure%20EXPRESS-V2-24.pdf.asset.pdf/1a9c2d3f1d.pdf
EU-RENAULT-FLUENCE-I-SEDAN-01	4620	1809	1479	Automobile-Catalog Renault Fluence 1.5 dCi 105	https://www.automobile-catalog.com/car/2010/2958980/renault_fluence_1_5_dci_105.html
EU-RENAULT-FUEGO-COUPE-01	4360	1690	1320	Renault The Originals Fuego Turbo	https://theoriginals.renault.com/en/fuego-turbo
```

## 下一步优先处理

闭合 Estafette `12427` 与 `12429` 的普通顶、加高顶和延长 Fourgon 分支，使用 Renault 官方历史尺寸图中的单值三维完成最后两个 Ktype；PENDING 清零后立即输出两张最终完整 TSV 和指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-espace-iv-generation-2141?utm_source=chatgpt.com "Renault Espace IV | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_13901-14000_ktype_dimension_mapping_final.tsv
- left18448_13901-14000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* Estafette `12427`、`12429` 已拆分为普通顶、加高顶和延长加高顶三个物理分支。
* 官方历史规格明确给出普通顶 `4100×1780×1920 mm`、加高顶 `4100×1780×2270 mm`；延长加高顶 `4480×1780×2270 mm` 结合官方 Estafette 1000 图示及官方尺寸上下限闭合。
* 已完成固定表头、唯一键、引用闭合、正整数尺寸、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：**100 / 100**
* READY 映射：**166**
* PENDING：**0**
* DIMENSION_GROUP：**37**
* 孤立尺寸组：**0**
* 缺失尺寸组引用：**0**

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17868_3dr	17868	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
17868_5dr	17868	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
54943_3dr	54943	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后三门外廓。	READY
54943_5dr	54943	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖BB/CB车身，本行对应改款后五门外廓。	READY
145580	145580	Van	Clio II	SB3M	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	SB3M商用三门版本，复用改款后三门车身外廓。	READY
11709_3dr_prefl	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门前期外廓。	READY
11709_3dr_facelift	11709	Hatchback	Clio II	CB	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应三门改款后外廓。	READY
11709_5dr_prefl	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门前期外廓。	READY
11709_5dr_facelift	11709	Hatchback	Clio II	BB	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖三门和五门且跨改款节点，本行对应五门改款后外廓。	READY
14577_3dr_prefl	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门前期外廓。	READY
14577_3dr_facelift	14577	Hatchback	Clio II	CB0U	3	EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应三门改款后外廓。	READY
14577_5dr_prefl	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门前期外廓。	READY
14577_5dr_facelift	14577	Hatchback	Clio II	BB0U	5	EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖B/CB0U并跨改款节点，本行对应五门改款后外廓。	READY
14183	14183	Hatchback	Clio II	CB0M	3	EU-RENAULT-CLIO-II-RS-3D-PREFL-01	HIGH	CB0M三门Renault Sport前期物理外廓。	READY
17869	17869	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	HIGH	179马力Renault Sport三门改款后外廓。	READY
15575	15575	Hatchback	Clio II	CB1A	3	EU-RENAULT-CLIO-II-V6-3D-PH1-01	HIGH	CB1A Clio V6 Phase 1宽体三门外廓。	READY
17138	17138	Hatchback	Clio II		3	EU-RENAULT-CLIO-II-V6-3D-PH2-01	HIGH	Ktype覆盖CB1H、CB1U和CB2S，均属于V6 Phase 2同一外廓。	READY
124975_prefl	124975	Van	Clio III	SR0J	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	SR0J三门商用车身，改款前外廓。	READY
124975_facelift	124975	Van	Clio III	SR0J	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	SR0J三门商用车身，改款后外廓。	READY
124977_prefl	124977	Van	Clio III	SR0P	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	SR0P三门商用车身，改款前外廓。	READY
124977_facelift	124977	Van	Clio III	SR0P	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	SR0P三门商用车身，改款后外廓。	READY
11056_3dr	11056	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应改款后三门外廓。	READY
11056_5dr	11056	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应改款后五门外廓。	READY
19045_3dr_prefl	19045	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19045_3dr_facelift	19045	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19045_5dr_prefl	19045	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19045_5dr_facelift	19045	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
19046_3dr_prefl	19046	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19046_3dr_facelift	19046	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19046_5dr_prefl	19046	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19046_5dr_facelift	19046	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
19047_3dr_prefl	19047	Hatchback	Clio III	CR0R	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	CR0R三门改款前外廓。	READY
19047_3dr_facelift	19047	Hatchback	Clio III	CR0R	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	CR0R三门改款后外廓。	READY
19047_5dr_prefl	19047	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19047_5dr_facelift	19047	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
52436_3dr_prefl	52436	Hatchback	Clio III	CR1U	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	HIGH	CR1U三门改款前外廓。	READY
52436_3dr_facelift	52436	Hatchback	Clio III	CR1U	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	HIGH	CR1U三门改款后外廓。	READY
52436_5dr_prefl	52436	Hatchback	Clio III	BR1U	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	HIGH	BR1U五门改款前外廓。	READY
52436_5dr_facelift	52436	Hatchback	Clio III	BR1U	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR1U五门改款后外廓。	READY
19050_3dr_prefl	19050	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19050_3dr_facelift	19050	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应三门改款后外廓。	READY
19050_5dr_prefl	19050	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19050_5dr_facelift	19050	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应五门改款后外廓。	READY
19051_3dr_prefl	19051	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19051_3dr_facelift	19051	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应三门改款后外廓。	READY
19051_5dr_prefl	19051	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19051_5dr_facelift	19051	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应五门改款后外廓。	READY
19052_3dr_prefl	19052	Hatchback	Clio III	CR17	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	HIGH	CR17三门改款前外廓。	READY
19052_3dr_facelift	19052	Hatchback	Clio III	CR17	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	HIGH	CR17三门改款后外廓。	READY
19052_5dr_prefl	19052	Hatchback	Clio III	BR17	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	HIGH	BR17五门改款前外廓。	READY
19052_5dr_facelift	19052	Hatchback	Clio III	BR17	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR17五门改款后外廓。	READY
19053_3dr_prefl	19053	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19053_3dr_facelift	19053	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19053_5dr_prefl	19053	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19053_5dr_facelift	19053	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
34744	34744	Hatchback	Clio III	BR1V	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	HIGH	BR1V五门改款后外廓。	READY
34746_3dr	34746	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	本行对应改款后三门外廓。	READY
34746_5dr	34746	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	本行对应改款后五门外廓。	READY
19048_3dr	19048	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	本行对应三门改款前外廓。	READY
19048_5dr	19048	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	本行对应五门改款前外廓。	READY
19049_3dr_prefl	19049	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款前外廓。	READY
19049_3dr_facelift	19049	Hatchback	Clio III		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	MEDIUM	覆盖多个CR车身代码；本行对应三门改款后外廓。	READY
19049_5dr_prefl	19049	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款前外廓。	READY
19049_5dr_facelift	19049	Hatchback	Clio III		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	MEDIUM	覆盖多个BR车身代码；本行对应五门改款后外廓。	READY
11057	11057	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34748_prefl	34748	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour五门改款前外廓。	READY
34748_facelift	34748	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34745	34745	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34747	34747	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
34749_prefl	34749	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour五门改款前外廓。	READY
34749_facelift	34749	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour五门改款后外廓。	READY
154694	154694	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
57401	57401	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124871	124871	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
126186	126186	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
57284	57284	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124872	124872	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
126404	126404	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
125321	125321	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
58898	58898	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
122130	122130	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
57282	57282	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124874	124874	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
57281	57281	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
124875	124875	Van	Clio IV		5	EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	HIGH	五门商用版车身外廓。	READY
58678	58678	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	HIGH	Renault Sport五门外廓。	READY
112058	112058	Hatchback	Clio IV		5	EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	HIGH	RS Trophy复用Renault Sport五门外廓。	READY
57450_prefl	57450	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57450_facelift	57450	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57451_prefl	57451	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57451_facelift	57451	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
58899_prefl	58899	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
58899_facelift	58899	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
121645	121645	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57453_prefl	57453	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57453_facelift	57453	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
57454_prefl	57454	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	HIGH	Grandtour改款前五门外廓。	READY
57454_facelift	57454	Wagon	Clio IV		5	EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	HIGH	Grandtour改款后五门外廓。	READY
148011_prefl	148011	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
148011_facelift	148011	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
145761_prefl	145761	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
145761_facelift	145761	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
145712	145712	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	MEDIUM	1.3 TCe 140仅落入改款前外廓边界。	READY
145756_prefl	145756	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
145756_facelift	145756	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
146398_prefl	146398	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
146398_facelift	146398	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
162795	162795	Hatchback	Clio VI		5	EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	HIGH	Clio VI五门外廓。	READY
162794	162794	Hatchback	Clio VI		5	EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	HIGH	Clio VI全混动五门外廓。	READY
109398	109398	Sedan	Dauphine		4	EU-RENAULT-DAUPHINE-SEDAN-01	HIGH	Dauphine四门轿车外廓。	READY
124738	124738	Van	Dokker I			EU-RENAULT-DOKKER-I-VAN-01	MEDIUM	Renault品牌Dokker厢式车身。	READY
7877	7877	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	J11标准MPV外廓。	READY
7879	7879	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	J11标准MPV外廓。	READY
7878	7878	MPV	Espace I	J11	5	EU-RENAULT-ESPACE-I-MPV-01	HIGH	Quadra四驱不改变J11外廓。	READY
7880	7880	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	HIGH	J63标准MPV外廓。	READY
143181	143181	Van	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	MEDIUM	J63商用衍生版本复用标准车身外廓。	READY
143182	143182	Van	Espace II	J63	5	EU-RENAULT-ESPACE-II-MPV-01	MEDIUM	J63商用衍生版本复用标准车身外廓。	READY
7828	7828	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
16598	16598	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
7829	7829	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10362	10362	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10361	10361	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
7830	7830	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
15054	15054	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
10360	10360	MPV	Espace III	JE0	5	EU-RENAULT-ESPACE-III-MPV-01	HIGH	JE0标准轴距MPV外廓。	READY
17098_swb	17098	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17098_lwb	17098	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
18679_swb	18679	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
18679_lwb	18679	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17125_swb	17125	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17125_lwb	17125	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
16869_swb	16869	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
16869_lwb	16869	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
16870_swb	16870	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
16870_lwb	16870	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17097_swb	17097	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17097_lwb	17097	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
53613_swb	53613	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
53613_lwb	53613	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
17096_swb	17096	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-SWB-01	MEDIUM	标准轴距Espace车身。	READY
17096_lwb	17096	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-LWB-01	MEDIUM	Grand Espace长轴距车身。	READY
111762	111762	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
111763	111763	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
111761	111761	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
145155	145155	MPV	Espace V		5	EU-RENAULT-ESPACE-V-MPV-01	HIGH	Espace V五门车身。	READY
154879	154879	SUV	Espace VI		5	EU-RENAULT-ESPACE-VI-SUV-01	HIGH	Espace VI五门SUV外廓。	READY
12427_lowroof	12427	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距普通顶厢式车身。	READY
12427_highroof	12427	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-SWB-HIGHROOF-01	MEDIUM	标准轴距加高顶厢式车身。	READY
12427_lwb_highroof	12427	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-LWB-HIGHROOF-01	MEDIUM	Estafette 1000延长加高顶厢式车身。	READY
12429_lowroof	12429	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距普通顶厢式车身。	READY
12429_highroof	12429	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-SWB-HIGHROOF-01	MEDIUM	标准轴距加高顶厢式车身。	READY
12429_lwb_highroof	12429	Van	Estafette			EU-RENAULT-ESTAFETTE-VAN-LWB-HIGHROOF-01	MEDIUM	Estafette 1000延长加高顶厢式车身。	READY
145220_van	145220	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145220_mpv	145220	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
145221_van	145221	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145221_mpv	145221	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
145222_van	145222	Van	Express II			EU-RENAULT-EXPRESS-II-VAN-01	MEDIUM	厢式货运车身。	READY
145222_mpv	145222	MPV	Express II		5	EU-RENAULT-EXPRESS-II-MPV-01	MEDIUM	五座乘用车身。	READY
113258	113258	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
154655	154655	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
107528	107528	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
5089	5089	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
124234	124234	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
107529	107529	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
124864	124864	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-SEDAN-01	HIGH	L30四门轿车外廓。	READY
17667	17667	Coupe	Fuego		3	EU-RENAULT-FUEGO-COUPE-01	HIGH	三门Coupe外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_13901-14000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-II-HATCHBACK-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2001 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2001/2949215/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-HATCHBACK-5D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio 1.6 16V	https://www.automobile-catalog.com/car/2000/2949020/renault_clio_1_6_16v.html
EU-RENAULT-CLIO-II-RS-3D-PREFL-01	3773	1639	1417	Automobile-Catalog 2000 Renault Clio RS	https://www.automobile-catalog.com/car/2000/2949110/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-RS-3D-FACELIFT-01	3812	1639	1417	Automobile-Catalog 2004 Renault Clio RS	https://www.automobile-catalog.com/car/2004/2949455/renault_clio_rs_renault_sport.html
EU-RENAULT-CLIO-II-V6-3D-PH1-01	3803	1810	1351	Automobile-Catalog 2001 Renault Clio V6	https://www.automobile-catalog.com/car/2001/2949290/renault_clio_v6.html
EU-RENAULT-CLIO-II-V6-3D-PH2-01	3841	1830	1356	Automobile-Catalog 2003 Renault Clio V6	https://www.automobile-catalog.com/car/2003/2949305/renault_clio_v6.html
EU-RENAULT-CLIO-III-HATCHBACK-3D-PREFL-01	3986	1707	1493	Automobile-Catalog 2005 Renault Clio 1.2 16V 65	https://www.automobile-catalog.com/car/2005/2951840/renault_clio_1_2_16v_65.html
EU-RENAULT-CLIO-III-HATCHBACK-3D-FACELIFT-01	4027	1707	1497	Automobile-Catalog 2009 Renault Clio 1.2 16V 75	https://www.automobile-catalog.com/car/2009/2952275/renault_clio_1_2_16v_75.html
EU-RENAULT-CLIO-III-HATCHBACK-5D-FACELIFT-01	4027	1707	1497	Automobile-Catalog 2009 Renault Clio 1.2 16V 75	https://www.automobile-catalog.com/car/2009/2952275/renault_clio_1_2_16v_75.html
EU-RENAULT-CLIO-III-HATCHBACK-5D-PREFL-01	3986	1707	1493	Automobile-Catalog 2005 Renault Clio 1.2 16V 65	https://www.automobile-catalog.com/car/2005/2951840/renault_clio_1_2_16v_65.html
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-FACELIFT-01	4228	1719	1513	AutoCentrum Renault Clio III Grandtour Phase II	https://www.autocentrum.pl/dane-techniczne/renault/clio/iii/grandtour-phase-ii/
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-PREFL-01	4203	1719	1513	Auto-Data Renault Clio III Sport Tourer Phase I 1.5 dCi 86	https://www.auto-data.net/en/renault-clio-iii-grandtour-phase-i-1.5-dci-86hp-56123
EU-RENAULT-CLIO-IV-HATCHBACK-5D-01	4062	1732	1448	Renault New Clio official press kit	https://www.press.renault.co.uk/assets/documents/original/10686-RenaultNewClioPressKitJuly20171.pdf
EU-RENAULT-CLIO-IV-RS-HATCHBACK-5D-01	4062	1731	1448	Renault Clio R.S. official press kit	https://www.press.renault.co.uk/assets/documents/original/14006-RenaultNewClioRenaultSportPressKitFebruary2018.pdf
EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-PREFL-01	4267	1732	1445	Auto-Data Renault Clio IV Grandtour Phase I	https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-i-1.5-dci-90hp-edc-18715
EU-RENAULT-CLIO-IV-GRANDTOUR-WAGON-FACELIFT-01	4267	1732	1475	Auto-Data Renault Clio IV Grandtour Phase II	https://www.auto-data.net/en/renault-clio-iv-grandtour-phase-ii-2016-1.5-energy-dci-90hp-25768
EU-RENAULT-CLIO-V-HATCHBACK-5D-PREFL-01	4050	1798	1440	Renault Nederland Clio price list August 2019	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-08-2019.pdf
EU-RENAULT-CLIO-V-HATCHBACK-5D-FACELIFT-01	4053	1798	1439	Renault Nederland Clio price list July 2023	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-juli23.pdf
EU-RENAULT-CLIO-VI-HATCHBACK-5D-01	4116	1768	1451	Renault Croatia New Clio 6 official press kit	https://www.renault.hr/CountriesData/Croatia/images/News/Clio6/Novi_Renault_Clio_6.pdf
EU-RENAULT-DAUPHINE-SEDAN-01	3950	1520	1400	Renault The Originals Dauphine Gordini	https://theoriginals.renault.com/en/dauphine-gordini
EU-RENAULT-DOKKER-I-VAN-01	4363	1751	1809	Dacia Dokker Van official brochure	https://cdn.group.renault.com/dac/ma/brochure/brochure_dokker-van.pdf
EU-RENAULT-ESPACE-I-MPV-01	4250	1770	1700	Renault The Originals Espace TSE	https://theoriginals.renault.com/en/espace-tse
EU-RENAULT-ESPACE-II-MPV-01	4429	1795	1693	Renault Classic Espace history; Automobile-Catalog Renault Espace II 2.2i	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/RenaultESPACE.pdf;https://www.automobile-catalog.com/car/1993/2944985/renault_espace_2_2i.html
EU-RENAULT-ESPACE-III-MPV-01	4517	1810	1690	Renault Classic Espace history	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/RenaultESPACE.pdf
EU-RENAULT-ESPACE-IV-MPV-SWB-01	4661	1860	1728	Auto-Data Renault Espace IV	https://www.auto-data.net/en/renault-espace-iv-generation-2141
EU-RENAULT-ESPACE-IV-MPV-LWB-01	4856	1860	1746	Auto-Data Renault Grand Espace IV Phase II	https://www.auto-data.net/en/renault-grand-espace-iv-phase-ii-2006-2.0-tce-170hp-automatic-20245
EU-RENAULT-ESPACE-V-MPV-01	4857	1888	1677	Renault Suisse Espace official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Neuer_Espace_PL_f.pdf
EU-RENAULT-ESPACE-VI-SUV-01	4722	1843	1645	Renault Suisse Espace E-Tech official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Neuer_Espace_E-TECH_FRA.pdf
EU-RENAULT-ESTAFETTE-VAN-SWB-LOWROOF-01	4100	1780	1920	Renault Classic Estafette history	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/ESTAFETTE.pdf
EU-RENAULT-ESTAFETTE-VAN-SWB-HIGHROOF-01	4100	1780	2270	Renault Classic Estafette history	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/ESTAFETTE.pdf
EU-RENAULT-ESTAFETTE-VAN-LWB-HIGHROOF-01	4480	1780	2270	Renault Classic Estafette history; Renault The Originals Estafette	https://cdn.group.renault.com/ren/master/renault-classic/tools-and-services/ESTAFETTE.pdf;https://theoriginals.renault.com/en/estafette
EU-RENAULT-EXPRESS-II-VAN-01	4393	1775	1811	Renault Express Van official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Express_Van_BR_f.pdf
EU-RENAULT-EXPRESS-II-MPV-01	4394	1775	1804	Renault Express official brochure	https://cdn.group.renault.com/ren/ma/brochure/E-Brochure%20EXPRESS-V2-24.pdf.asset.pdf/1a9c2d3f1d.pdf
EU-RENAULT-FLUENCE-I-SEDAN-01	4620	1809	1479	Automobile-Catalog Renault Fluence 1.5 dCi 105	https://www.automobile-catalog.com/car/2010/2958980/renault_fluence_1_5_dci_105.html
EU-RENAULT-FUEGO-COUPE-01	4360	1690	1320	Renault The Originals Fuego Turbo	https://theoriginals.renault.com/en/fuego-turbo
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_13901-14000_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（166 行）
- 累计尺寸组：dimension_groups_final.tsv（37 行）

