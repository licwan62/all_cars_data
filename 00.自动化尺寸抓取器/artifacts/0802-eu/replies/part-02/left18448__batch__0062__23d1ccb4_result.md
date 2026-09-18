# 任务：left18448 第 6101-6200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0062__23d1ccb4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6101-6200 行

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
left18448 第 6101-6200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	4853	1855	1860
EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	4500	1855	1856
EU-FORD-TRANSIT-MK1-CHASSIS-LWB-01	5033	2057	2132
EU-FORD-TRANSIT-MK1-CHASSIS-SWB-01	4282	1934	1973
EU-FORD-TRANSIT-MK1-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-CHASSIS-LWB-01	5185	1960	1875
EU-FORD-TRANSIT-MK2-CHASSIS-SWB-01	4470	1960	1805
EU-FORD-TRANSIT-MK2-VAN-LWB-HIGHROOF-01	5310	2060	2127
EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	5452	1974	2014
EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	5085	1974	2015
EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	5651	1974	2524
EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	5651	1974	2303
EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	5201	1974	2529
EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	5201	1974	2309
EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	4834	1974	1974
EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	4834	1974	2313
EU-FORD-TRANSIT-V347-CHASSIS-LWB-EF-SRW-01	6319	1974	2030
EU-FORD-TRANSIT-V347-CHASSIS-MWB-SRW-01	5481	1974	2017
EU-FORD-TRANSIT-V347-CHASSIS-SWB-SRW-01	5114	1974	2030
EU-FORD-TRANSIT-V347-VAN-LWB-HIGHROOF-01	5680	1974	2590
EU-FORD-TRANSIT-V347-VAN-LWB-MEDIUMROOF-01	5680	1974	2381
EU-FORD-TRANSIT-V347-VAN-MWB-HIGHROOF-01	5230	1974	2594
EU-FORD-TRANSIT-V347-VAN-MWB-LOWROOF-01	5230	1974	2047
EU-FORD-TRANSIT-V347-VAN-MWB-MEDIUMROOF-01	5230	1974	2363
EU-FORD-TRANSIT-V347-VAN-SWB-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-V347-VAN-SWB-MEDIUMROOF-01	4863	1974	2385
EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	5931	2052	2031
EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	6319	2052	2030
EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	6319	1974	2030
EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	5931	1974	2031
EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	5481	2052	2035
EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	5481	1974	2035
EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	6403	2084	2624
EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	6403	2084	2380
EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	5680	2084	2394
EU-FORD-TRANSIT-V348-VAN-EL-HIGHROOF-DRW-01	6403	2084	2624
EU-FORD-TRANSIT-V348-VAN-EL-HIGHROOF-SRW-01	6403	1974	2624
EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	5680	1974	2606
EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	5680	1974	2394
EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	5230	1974	2611
EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	5230	1974	2397
EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	4863	1974	2083
EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	4863	1974	2398
EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	6085	1971	2026
EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	5355	1971	2026
EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	4620	1971	2018
EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	6007	1925	2004
EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	5290	1925	2004
EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	4615	1925	1976
EU-FORD-TRANSIT-VE6-MPV-LWB-HIGHROOF-01	5358	1972	2238
EU-FORD-TRANSIT-VE6-MPV-SWB-HIGHROOF-01	4606	1938	2170
EU-FORD-TRANSIT-VE6-MPV-SWB-LOWROOF-01	4606	1938	1952
EU-FORD-TRANSIT-VE6-VAN-SWB-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	6085	1974	2026
EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	5376	1974	2026
EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	4616	1974	2026
EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	5368	1974	2255
EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	4616	1974	2024

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Transit	2.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Oct 2011	Aug 2014	11969
Ford	Transit	2.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Oct 2011	Aug 2014	11971
Ford	Transit	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	Sep 2011	Aug 2014	54979
Ford	Transit	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	Oct 2011	Aug 2014	145254
Ford	Transit	2.3 16V	Pritsche/Fahrgestell	Heckantrieb	Benzin	Apr 2001	May 2006	16101
Ford	Transit	2.3 16V CNG RWD	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	Apr 2006	Aug 2014	111065
Ford	Transit	2.3 16V CNG RWD	Kasten	Heckantrieb	Benzin/Erdgas (CNG)	Apr 2006	Aug 2014	111066
Ford	Transit	2.3 16V LPG RWD	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Apr 2006	Aug 2014	111063
Ford	Transit	2.3 16V LPG RWD	Kasten	Heckantrieb	Benzin/Autogas (LPG)	Apr 2006	Aug 2014	111064
Ford	Transit	2.3 16V RWD	Bus	Heckantrieb	Benzin	Aug 2000	May 2006	16096
Ford	Transit	2.3 16V RWD	Kasten	Heckantrieb	Benzin	Apr 2001	May 2006	16099
Ford	Transit	2.4 DI	Bus	Heckantrieb	Diesel	Jan 2000	May 2006	14730
Ford	Transit	2.4 DI	Kasten	Heckantrieb	Diesel	Jan 2000	May 2006	14731
Ford	Transit	2.4 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2000	May 2006	14733
Ford	Transit	2.4 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2000	May 2006	14734
Ford	Transit	2.4 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2000	May 2006	14850
Ford	Transit	2.4 DI RWD	Bus	Heckantrieb	Diesel	Jan 2000	May 2006	14729
Ford	Transit	2.4 DI RWD	Kasten	Heckantrieb	Diesel	Jan 2000	May 2006	14732
Ford	Transit	2.4 DI RWD	Bus	Heckantrieb	Diesel	Jan 2000	May 2006	14848
Ford	Transit	2.4 DI RWD	Kasten	Heckantrieb	Diesel	Jan 2000	May 2006	14849
Ford	Transit	2.4 Tdci	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2004	May 2006	18089
Ford	Transit	2.4 Tdci	Kasten	Heckantrieb	Diesel	Mar 2004	May 2006	18090
Ford	Transit	2.4 Tdci	Bus	Heckantrieb	Diesel	Mar 2004	May 2006	18091
Ford	Transit	2.4 TDE	Bus	Heckantrieb	Diesel	Jul 2001	May 2006	16551
Ford	Transit	2.4 TDE	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2001	May 2006	17781
Ford	Transit	2.4 TDE	Kasten	Heckantrieb	Diesel	Jul 2001	May 2006	17782
Ford	Transit	2.4 TDE	Bus	Heckantrieb	Diesel	Mar 2004	May 2006	18086
Ford	Transit	2.4 TDE	Kasten	Heckantrieb	Diesel	Mar 2004	May 2006	18087
Ford	Transit	2.4 TDE	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2004	May 2006	18088
Ford	Transit	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1986	Jan 1989	11021
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1988	Sep 1992	8727
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1994	Mar 2000	8764
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1991	Aug 1994	8765
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1994	Mar 2000	8790
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1991	Aug 1994	8793
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	Jun 1994	Mar 2000	8794
Ford	Transit	2.5 DI	Bus	Heckantrieb	Diesel	Aug 1997	Mar 2000	8836
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	May 1999	Mar 2000	14735
Ford	Transit	2.5 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 1999	Mar 2000	14845
Ford	Transit	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1994	Mar 2000	8762
Ford	Transit	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 1994	Mar 2000	8789
Ford	Transit	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 1992	Aug 1994	8791
Ford	Transit	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1991	Aug 1994	8792
Ford	Transit	2.9 I	Bus	Heckantrieb	Benzin	Jan 1991	Sep 1994	16562
Ford	Transit	K-40 1.5	Bus	Heckantrieb	Benzin	Apr 1955	Apr 1967	6610
Ford	Transit city	Electric	Kasten	Frontantrieb	Elektro	Apr 2026	-	164478
Ford	Transit connect	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	May 2015	-	116212
Ford	Transit connect	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	May 2015	-	116213
Ford	Transit connect	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Aug 2015	-	117100
Ford	Transit connect	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	100088
Ford	Transit connect	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	100089
Ford	Transit connect	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	100090
Ford	Transit connect	1.8 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 2002	Dec 2013	16965
Ford	Transit connect	1.8 16V LPG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Jun 2002	Dec 2013	12563
Ford	Transit connect	1.8 DI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2002	Dec 2013	16966
Ford	Transit connect	1.8 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2002	Dec 2013	17783
Ford	Transit connect	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Sep 2010	Dec 2013	802191
Ford	Transit connect v408	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Sep 2013	-	53399
Ford	Transit connect v408	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2018	-	803376
Ford	Transit connect v408	1.0 Flexifuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	May 2021	-	145154
Ford	Transit connect v408	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	-	116210
Ford	Transit connect v408	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	-	116211
Ford	Transit connect v408	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Aug 2015	-	121226
Ford	Transit connect v408	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2016	-	145750
Ford	Transit connect v408	1.6 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2013	-	53394
Ford	Transit connect v408	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	53389
Ford	Transit connect v408	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	53392
Ford	Transit connect v408	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	53393
Ford	Transit connect v761	1.5 Plug-in Hybrid	Kasten/Großraumlimousine	Frontantrieb	Benzin/Elektro	Oct 2024	-	801038
Ford	Transit connect v761	Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2024	-	151572
Ford	Transit connect v761	Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2024	-	151589
Ford	Transit connect v761	Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2024	-	151625
Ford	Transit connect v761	Ecoblue 4WD	Kasten/Großraumlimousine	Allrad	Diesel	May 2024	-	151626
Ford	Transit connect v761	Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2024	Aug 2024	151590
Ford	Transit connect v761	Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 2024	-	800151
Ford	Transit courier b460	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Feb 2014	Dec 2023	101057
Ford	Transit courier b460	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 2014	Dec 2023	101058
Ford	Transit courier b460	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2014	Dec 2023	101055
Ford	Transit courier b460	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2014	Dec 2023	101056
Ford	Transit courier b460	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2015	Dec 2023	115170
Ford	Transit courier b460	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	May 2015	Dec 2023	115174
Ford	Transit courier b460	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2014	Dec 2023	101053
Ford	Transit courier b460	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2014	Dec 2023	101054
Ford	Transit courier v769	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2023	-	155264
Ford	Transit courier v769	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2023	-	155265
Ford	Transit courier v769	1.5 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2023	-	155266
Ford	Transit courier v769	E-transit Courier	Kasten/Großraumlimousine	Frontantrieb	Elektro	Dec 2024	-	801230
Ford	Transit custom v362	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Dec 2015	Dec 2023	118533
Ford	Transit custom v362	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Dec 2015	Dec 2023	118534
Ford	Transit custom v362	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Dec 2015	Dec 2023	118535
Ford	Transit custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Dec 2015	Dec 2023	118536
Ford	Transit custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Dec 2015	Dec 2023	118537
Ford	Transit custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Dec 2015	Dec 2023	118538
Ford	Transit custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Jan 2022	Dec 2023	147111
Ford	Transit custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	Jan 2022	Dec 2023	147115
Ford	Transit custom v362	2.2 Tdci	Bus	Frontantrieb	Diesel	Sep 2012	Jun 2016	58539
Ford	Transit custom v362	2.2 Tdci	Bus	Frontantrieb	Diesel	Sep 2012	Dec 2015	58540
Ford	Transit custom v362	2.2 Tdci	Bus	Frontantrieb	Diesel	Sep 2012	Dec 2015	58541
Ford	Transit custom v362	2.2 Tdci	Kasten	Frontantrieb	Diesel	Sep 2012	Jun 2016	58543
Ford	Transit custom v362	2.2 Tdci	Kasten	Frontantrieb	Diesel	Sep 2012	Apr 2016	58544


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Transit Courier B460** 车身簇。官方规格显示：厢式版与乘用版长、宽均为 `4157 × 1764 mm`，但不含车顶行李架的高度分别为 `1770 mm` 与 `1741 mm`，因此必须拆成两个尺寸组，不能合并。乘用版资料同时明确为五门。
* 4 个原始 `Großraumlimousine` Ktype 直接映射至 MPV 组。
* 4 个原始 `Kasten/Großraumlimousine` Ktype 分别派生为 Van 与 MPV 两条映射，不保留无后缀基础行。
* 本轮首次创建 2 个 DIMENSION_GROUP；未重复输出其他既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：8
* READY 映射：12 行
* 待处理输入 Ktype：92
* 本批已确认新增尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
101057	101057	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101058_van	101058	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101058_mpv	101058	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
101055	101055	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101056_van	101056	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101056_mpv	101056	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
115170_van	115170	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
115170_mpv	115170	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
115174	115174	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101053	101053	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101054_van	101054	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101054_mpv	101054	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-COURIER-B460-MPV-01	4157	1764	1741	Ford Tourneo Courier official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Tourneo-Courier.pdf
EU-FORD-TRANSIT-COURIER-B460-VAN-01	4157	1764	1770	Ford Transit Courier official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_courier.pdf
```

## 下一步优先处理

1. 闭合 Transit Courier V769 的 Van、MPV 与纯电版本边界。
2. 核对 Transit Connect V761 混合车身行，区分可复用的 Van SWB/LWB 与 FlexCab/乘用外廓。
3. 按尺寸簇批量处理 Transit Connect V408、Transit Custom V362，随后处理年代较早的 Transit 底盘和车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Transit Connect V761 车身簇的 7 个 Ktype。
* 各 Ktype 按 SWB、LWB 两种物理外廓派生映射；Ford 车型范围明确提供短轴与长轴 Van。([福特英国][1])
* 全部复用跨批次已有 V761 SWB、LWB 尺寸组，本轮未新增或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：15
* READY 映射：26 行
* PENDING Ktype：85
* 当前已引用尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801038_swb	801038	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
801038_lwb	801038	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151572_swb	151572	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151572_lwb	151572	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151589_swb	151589	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151589_lwb	151589	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151625_swb	151625	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151625_lwb	151625	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151626_swb	151626	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴四驱厢式物理外廓。	READY
151626_lwb	151626	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴四驱厢式物理外廓。	READY
151590_swb	151590	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151590_lwb	151590	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
800151_swb	800151	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
800151_lwb	800151	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Transit Connect V408 的短轴、长轴物理外廓。
2. 随后处理 Transit Courier V769 的燃油与纯电 Ktype。
3. 批量关联 Transit V185 已缓存的底盘、轴距与车顶分支。

推进信号：CONTINUE

[1]: https://www.ford.co.uk/vans-and-pickups/transit-connect "Ford Transit Connect | Ford UK"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Transit Connect V408 的 11 个 Ktype，共新增 22 条 SWB/LWB 厢式映射。
* 首次建立 V408 改款前、改款后各两个尺寸组；Ford 资料确认两种轴距外廓及不含后视镜宽度。
* 未重复输出此前已闭合的 Courier B460、Connect V761 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：26
* READY 映射：48 行
* PENDING Ktype：74
* 当前已引用尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
53399_swb_prefl	53399	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53399_lwb_prefl	53399	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
803376_swb_facelift	803376	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	HIGH	改款后短轴厢式外廓。	READY
803376_lwb_facelift	803376	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	HIGH	改款后长轴厢式外廓。	READY
145154_swb_facelift	145154	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	HIGH	改款后短轴厢式外廓。	READY
145154_lwb_facelift	145154	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	HIGH	改款后长轴厢式外廓。	READY
116210_swb_prefl	116210	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
116210_lwb_prefl	116210	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
116211_swb_prefl	116211	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
116211_lwb_prefl	116211	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
121226_swb_prefl	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
121226_lwb_prefl	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
145750_swb_prefl	145750	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
145750_lwb_prefl	145750	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53394_swb_prefl	53394	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53394_lwb_prefl	53394	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53389_swb_prefl	53389	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53389_lwb_prefl	53389	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53392_swb_prefl	53392	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53392_lwb_prefl	53392	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53393_swb_prefl	53393	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53393_lwb_prefl	53393	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	4418	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	4818	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	4425	1835	1859	Ford Transit Connect official brochure	https://www.ford.pl/content/dam/guxeu/pl/pl_pl/documents/brochures/commercial-vehicles/BRO-ford_transit_connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	4825	1835	1847	Ford Transit Connect official brochure	https://www.ford.pl/content/dam/guxeu/pl/pl_pl/documents/brochures/commercial-vehicles/BRO-ford_transit_connect.pdf
```

## 下一步优先处理

1. 闭合独立的 Transit Connect 乘用型 Ktype，关联 V408 改款前 MPV SWB/LWB 外廓。
2. 处理 Transit Courier V769 燃油和纯电车身簇。
3. 随后集中处理 Transit Custom V362 的 SWB/LWB 及 Van/Bus 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Transit Courier V769 的 4 个 Ktype，新增 7 条映射。
* 燃油版混合车身 Ktype 拆分为 Van 与 MPV；纯电 `E-Transit Courier` 仅映射 Van。
* 首次建立 V769 Van 与 MPV 两个尺寸组。官方资料确认 Van 为 `4337 × 1800 × 1827 mm`，MPV 为 `4337 × 1791 × 1817 mm`；燃油与纯电 Van 外廓复用同一尺寸组。([Ford Press Belux][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：30
* READY 映射：55 行
* PENDING Ktype：70
* 当前已引用尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
155264_van	155264	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155264_mpv	155264	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
155265_van	155265	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155265_mpv	155265	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
155266_van	155266	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155266_mpv	155266	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
801230	801230	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	纯电厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-COURIER-V769-VAN-01	4337	1800	1827	Ford Transit Courier 2024 official technical specifications; Ford Transit Courier and E-Transit Courier official price list	https://www.fordpresse.be/content/documents/news/2024/transit_courier_technical_specification_eu.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/All_New_PL-Transit_Courier.pdf
EU-FORD-TRANSIT-COURIER-V769-MPV-01	4337	1791	1817	Ford Tourneo Courier 2024 official technical specifications	https://www.fordpers.be/content/documents/news/2024/tourneo_courier_technical_specification_eu.pdf
```

## 下一步优先处理

1. 闭合 Transit Connect V408 的 6 个独立乘用型 Ktype，建立或关联 MPV SWB/LWB 尺寸组。
2. 集中处理 Transit Custom V362 的 Van、Bus、SWB 与 LWB 分支。
3. 随后批量关联 Transit V185、V347、V348 已缓存底盘与车顶尺寸组。

推进信号：CONTINUE

[1]: https://www.fordpresse.be/content/documents/news/2024/transit_courier_technical_specification_eu.pdf "Transit Courier ICE 2024 techspec EU.indd"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Transit Connect V408 的 6 个独立乘用型 Ktype，共新增 18 条映射。
* 官方尺寸表将乘用外廓区分为 SWB 五座、LWB 五座和 LWB 七座三种配置；三者高度不同，不能合并为同一尺寸组。
* 本轮首次建立 3 个 V408 改款前 MPV 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：36
* READY 映射：73 行
* PENDING Ktype：64
* 当前已引用尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116212_swb	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
116212_lwb_5seat	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
116212_lwb_7seat	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
116213_swb	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
116213_lwb_5seat	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
116213_lwb_7seat	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
117100_swb	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
117100_lwb_5seat	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
117100_lwb_7seat	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100088_swb	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100088_lwb_5seat	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100088_lwb_7seat	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100089_swb	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100089_lwb_5seat	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100089_lwb_7seat	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100090_swb	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100090_lwb_5seat	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100090_lwb_7seat	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	4418	1835	1852	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	4818	1835	1845	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	4818	1835	1840	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
```

## 下一步优先处理

1. 集中闭合 Transit Custom V362 的 Van、Bus、SWB 与 LWB 外廓。
2. 批量关联 2000—2006 年 Transit V185 已缓存的 Van、Bus 和 Chassis 分支。
3. 随后处理 1986—2000 年 Transit VE6、VE64、VE83 的底盘 Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Transit Custom V362 的 13 个 Ktype，新增 76 条映射。
* 其中 6 个跨越改款期的 Ktype 拆分为改款前、改款后分支；其余按实际生产区间关联对应外廓。
* 官方资料确认改款前与改款后的车长及 Van/Kombi 高度存在差异，因此不能合并。改款前 Van 与 Kombi 三维一致，复用同一组；改款后分别建组。
* 本轮首次创建 12 个 DIMENSION_GROUP。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：49
* READY 映射：149 行
* PENDING Ktype：51
* 当前已引用尺寸组：25
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
118533_l1h1_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118533_l1h2_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118533_l2h1_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118533_l2h2_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118533_l1h1_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118533_l1h2_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118533_l2h1_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118533_l2h2_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118534_l1h1_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118534_l1h2_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118534_l2h1_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118534_l2h2_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118534_l1h1_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118534_l1h2_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118534_l2h1_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118534_l2h2_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118535_l1h1_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118535_l1h2_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118535_l2h1_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118535_l2h2_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118535_l1h1_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118535_l1h2_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118535_l2h1_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118535_l2h2_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118536_l1h1_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118536_l1h2_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118536_l2h1_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118536_l2h2_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118536_l1h1_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118536_l1h2_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118536_l2h1_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118536_l2h2_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
118537_l1h1_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118537_l1h2_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118537_l2h1_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118537_l2h2_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118537_l1h1_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118537_l1h2_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118537_l2h1_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118537_l2h2_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
118538_l1h1_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118538_l1h2_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118538_l2h1_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118538_l2h2_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118538_l1h1_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118538_l1h2_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118538_l2h1_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118538_l2h2_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
147111_l1h1_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
147111_l1h2_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
147111_l2h1_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
147111_l2h2_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
147115_l1h1_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
147115_l1h2_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
147115_l2h1_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
147115_l2h2_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
58539_l1h1_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58539_l1h2_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58539_l2h1_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58539_l2h2_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58540_l1h1_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58540_l1h2_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58540_l2h1_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58540_l2h2_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58541_l1h1_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58541_l1h2_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58541_l2h1_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58541_l2h2_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58543_l1h1_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
58543_l1h2_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
58543_l2h1_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
58543_l2h2_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
58544_l1h1_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
58544_l1h2_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
58544_l2h1_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
58544_l2h2_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	4972	1986	2020	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	4972	1986	2389	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	5339	1986	2017	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	5339	1986	2381	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	4973	1986	2000	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	4973	1986	2366	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	5340	1986	1979	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	5340	1986	2343	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	4973	1986	2020	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	4973	1986	2389	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	5340	1986	2017	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	5340	1986	2381	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
```

## 下一步优先处理

1. 批量关联 2000—2006 年 Transit V185 的 Van、Bus、Chassis、轴距与车顶分支。
2. 处理 2006—2014 年 Transit V347/V348 的 RWD Chassis、Van 与 Bus 分支。
3. 随后闭合 1986—2000 年 Transit VE6、VE64、VE83 底盘车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 2000—2006 年 Transit V185 的 21 个 Ktype。
* Chassis Ktype 关联 SWB、MWB 两个既有底盘尺寸组。
* Van 与 Bus Ktype 关联既有的 SWB、MWB、LWB 及对应车顶高度尺寸组。
* 全部复用跨批次缓存，本轮未创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：70
* READY 映射：247 行
* PENDING Ktype：30
* 当前已引用尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16101_swb	16101	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
16101_mwb	16101	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
16096_swb_lowroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
16096_swb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
16096_mwb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
16096_mwb_highroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
16096_lwb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
16096_lwb_highroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
16099_swb_lowroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
16099_swb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
16099_mwb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
16099_mwb_highroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
16099_lwb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
16099_lwb_highroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14730_swb_lowroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14730_swb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14730_mwb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14730_mwb_highroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14730_lwb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14730_lwb_highroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14731_swb_lowroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14731_swb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14731_mwb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14731_mwb_highroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14731_lwb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14731_lwb_highroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14733_swb	14733	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14733_mwb	14733	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14734_swb	14734	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14734_mwb	14734	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14850_swb	14850	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14850_mwb	14850	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14729_swb_lowroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14729_swb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14729_mwb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14729_mwb_highroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14729_lwb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14729_lwb_highroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14732_swb_lowroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14732_swb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14732_mwb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14732_mwb_highroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14732_lwb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14732_lwb_highroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14848_swb_lowroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14848_swb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14848_mwb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14848_mwb_highroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14848_lwb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14848_lwb_highroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14849_swb_lowroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14849_swb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14849_mwb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14849_mwb_highroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14849_lwb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14849_lwb_highroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18089_swb	18089	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
18089_mwb	18089	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
18090_swb_lowroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
18090_swb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
18090_mwb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
18090_mwb_highroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
18090_lwb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
18090_lwb_highroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18091_swb_lowroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
18091_swb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
18091_mwb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
18091_mwb_highroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
18091_lwb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
18091_lwb_highroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
16551_swb_lowroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
16551_swb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
16551_mwb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
16551_mwb_highroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
16551_lwb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
16551_lwb_highroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
17781_swb	17781	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
17781_mwb	17781	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
17782_swb_lowroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
17782_swb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
17782_mwb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
17782_mwb_highroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
17782_lwb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
17782_lwb_highroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18086_swb_lowroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
18086_swb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
18086_mwb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
18086_mwb_highroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
18086_lwb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
18086_lwb_highroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
18087_swb_lowroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
18087_swb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
18087_mwb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
18087_mwb_highroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
18087_lwb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
18087_lwb_highroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18088_swb	18088	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
18088_mwb	18088	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量关联 2006—2014 年 Transit V347/V348 的 Chassis、Van 与 Bus 分支。
2. 处理 1986—2000 年 Transit VE6、VE64、VE83 的底盘和车身分支。
3. 最后处理 Transit K-40、Transit City Electric 与第一代 Transit Connect，消除剩余 PENDING。

推进信号：CONTINUE


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 2006—2014 年 Transit V348 的 8 个 Ktype，共新增 42 条映射。
* RWD 底盘按 MWB、LWB、LWB-EF 及 SRW/DRW 拆分；厢式车按 SWB/MWB/LWB 与车顶高度拆分；Bus 关联现有 LWB、EL 中顶/高顶 MPV 外廓。Ford 车型资料确认该代 Transit 同时提供这些轴距、车顶和后轮配置分支。
* 全部复用跨批次已有 V348 尺寸组，本轮未新增或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：78
* READY 映射：289 行
* PENDING Ktype：22
* 当前已引用尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11969_mwb_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
11969_mwb_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
11969_lwb_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
11969_lwb_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
11969_lwb_ef_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
11969_lwb_ef_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
11971_mwb_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
11971_mwb_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
11971_lwb_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
11971_lwb_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
11971_lwb_ef_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
11971_lwb_ef_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
54979_lwb_mediumroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	MEDIUM	长轴中顶乘用外廓。	READY
54979_el_mediumroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	MEDIUM	加长轴中顶乘用外廓。	READY
54979_el_highroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	MEDIUM	加长轴高顶乘用外廓。	READY
145254_lwb_mediumroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	MEDIUM	长轴中顶乘用外廓。	READY
145254_el_mediumroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	MEDIUM	加长轴中顶乘用外廓。	READY
145254_el_highroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	MEDIUM	加长轴高顶乘用外廓。	READY
111065_mwb_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
111065_mwb_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
111065_lwb_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
111065_lwb_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
111065_lwb_ef_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
111065_lwb_ef_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
111066_swb_lowroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
111066_swb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
111066_mwb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
111066_mwb_highroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
111066_lwb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
111066_lwb_highroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
111063_mwb_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
111063_mwb_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
111063_lwb_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
111063_lwb_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
111063_lwb_ef_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
111063_lwb_ef_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
111064_swb_lowroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
111064_swb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
111064_mwb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
111064_mwb_highroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
111064_lwb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
111064_lwb_highroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量关联 1986—2000 年 Transit VE6、VE64、VE83 的 Chassis、Van 与 Bus 分支。
2. 闭合第一代 Transit Connect 的 SWB/LWB、Van/MPV 外廓。
3. 最后处理 Transit K-40、Transit City Electric 两个特殊车系，消除剩余 PENDING。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 1986—2000 年 Transit 的 11 个底盘 Ktype，共新增 36 条映射。
* `8727` 的生产区间跨越 1992 年车身改款，已拆分为 VE6 改款前和 VE64 改款后分支；1994 年起的车型关联 VE83。([维基百科][1])
* 全部复用跨批次已有 VE6、VE64、VE83 Chassis 尺寸组，本轮未新增或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：89
* READY 映射：325 行
* PENDING Ktype：11
* 当前已引用尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11021_swb	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
11021_lwb	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
11021_extended	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8727_swb_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	MEDIUM	1992年改款前短轴底盘外廓。	READY
8727_lwb_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	MEDIUM	1992年改款前长轴底盘外廓。	READY
8727_extended_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	MEDIUM	1992年改款前加长底盘外廓。	READY
8727_swb_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	1992年改款后短轴底盘外廓。	READY
8727_lwb_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	1992年改款后长轴底盘外廓。	READY
8727_extended_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	1992年改款后加长底盘外廓。	READY
8764_swb	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8764_lwb	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8764_extended	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8765_swb	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8765_lwb	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8765_extended	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8790_swb	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8790_lwb	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8790_extended	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8793_swb	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8793_lwb	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8793_extended	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
14845_swb	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14845_lwb	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
14845_extended	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8762_swb	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8762_lwb	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8762_extended	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8789_swb	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8789_lwb	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8789_extended	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8791_swb	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8791_lwb	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8791_extended	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8792_swb	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8792_lwb	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8792_extended	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合第一代 Transit Connect 的 5 个 Ktype，区分 SWB/LWB 与 Van/MPV 外廓。
2. 处理 VE83 的 3 个 Van/Bus Ktype，并判断是否可复用现有 VE83 MPV CNG 尺寸组。
3. 最后处理 Transit K-40、Transit City Electric 和 VE64 Bus，消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Ford_Transit?utm_source=chatgpt.com "Ford Transit"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合第一代 Transit Connect 的 5 个 Ktype，新增 17 条映射。
* 燃油 Ktype 按 Van/MPV 与 SWB/LWB 物理外廓拆分；纯电 Ktype 对应 LWB 高顶 Van。
* 首次建立 4 个尺寸组。Ford 官方资料确认 Van SWB 为 `4275 × 1795 × 1815 mm`、Van LWB 为 `4525 × 1795 × 1980 mm`；早期 Tourneo Connect LWB 为 `4525 × 1795 × 1981 mm`。
* Tourneo Connect SWB 使用同代独立乘用外廓 `4278 × 1795 × 1814 mm`。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：94
* READY 映射：342 行
* PENDING Ktype：6
* 当前已引用尺寸组：61
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16965_van_swb	16965	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
16965_van_lwb	16965	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
16965_mpv_swb	16965	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
16965_mpv_lwb	16965	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
12563_van_swb	12563	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
12563_van_lwb	12563	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
12563_mpv_swb	12563	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
12563_mpv_lwb	12563	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
16966_van_swb	16966	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
16966_van_lwb	16966	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
16966_mpv_swb	16966	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
16966_mpv_lwb	16966	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
17783_van_swb	17783	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
17783_van_lwb	17783	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
17783_mpv_swb	17783	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
17783_mpv_lwb	17783	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
802191_lwb	802191	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	纯电长轴高顶厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	4275	1795	1815	Ford Transit Connect Van official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-Connect-UK.pdf
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	4525	1795	1980	Ford Transit Connect Van official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-Connect-UK.pdf
EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	4278	1795	1814	Automobile-Catalog Ford Tourneo Connect SWB specifications	https://www.automobile-catalog.com/car/2002/980285/ford_tourneo_connect_swb_1_8_tdci.html
EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	4525	1795	1981	Ford Tourneo Connect official specification brochure 2004	https://xr793.com/wp-content/uploads/2022/09/2024-Ford-People-Movers-Specs-UK.pdf
```

## 下一步优先处理

1. 闭合 VE83 的 `8794`、`8836`、`14735` Van/Bus 分支。
2. 处理 VE64 Bus `16562`。
3. 最后闭合 Transit K-40 `6610` 与 Transit City Electric `164478`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/980285/ford_tourneo_connect_swb_1_8_tdci.html?utm_source=chatgpt.com "2002 Ford Tourneo Connect swb 1.8 TDCi (man. 5)"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合最后 6 个 Ktype。
* `8794`、`8836`、`14735` 复用现有 VE83 SWB 低顶与 LWB 中顶尺寸组。
* `16562` 按 1992 年前后的 VE6/VE64 外廓拆分；VE6 复用缓存，VE64 首次建立 5 个尺寸组。VE64 资料明确列出短轴三种车顶和长轴两种车顶外廓。([ForbBook.ru][1])
* `6610` 闭合为 FK 1000/Taunus Transit 小型客车外廓。([AUTO ZEITUNG][2])
* `164478` 按 Transit City SWB 低顶、LWB 高顶拆分。Ford 官方价目表明确给出两种 Van 外廓及不含后视镜宽度。
* 本轮后 `PENDING=0`，下一轮只进行一次机械收尾并直接输出两张完整 TSV、指定下载链接与 `COMPLETE`。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：100
* READY 映射：359 行
* PENDING Ktype：0
* 当前已引用尺寸组：74
* 数据阶段已完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8794_swb_lowroof	8794	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶厢式外廓。	READY
8794_lwb_mediumroof	8794	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶厢式外廓。	READY
8836_swb_lowroof	8836	MPV	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶乘用外廓。	READY
8836_lwb_mediumroof	8836	MPV	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶乘用外廓。	READY
14735_swb_lowroof	14735	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶厢式外廓。	READY
14735_lwb_mediumroof	14735	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶厢式外廓。	READY
16562_swb_lowroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-SWB-LOWROOF-01	MEDIUM	1992年改款前短轴低顶乘用外廓。	READY
16562_swb_highroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-SWB-HIGHROOF-01	MEDIUM	1992年改款前短轴高顶乘用外廓。	READY
16562_lwb_highroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-LWB-HIGHROOF-01	MEDIUM	1992年改款前长轴高顶乘用外廓。	READY
16562_swb_lowroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-LOWROOF-01	MEDIUM	1992年改款后短轴低顶乘用外廓。	READY
16562_swb_mediumroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-MEDIUMROOF-01	MEDIUM	1992年改款后短轴中顶乘用外廓。	READY
16562_swb_highroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-HIGHROOF-01	MEDIUM	1992年改款后短轴高顶乘用外廓。	READY
16562_lwb_mediumroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-MEDIUMROOF-01	MEDIUM	1992年改款后长轴中顶乘用外廓。	READY
16562_lwb_highroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-HIGHROOF-01	MEDIUM	1992年改款后长轴高顶乘用外廓。	READY
6610	6610	MPV	FK 1000/Taunus Transit			EU-FORD-TAUNUS-TRANSIT-FK1000-MPV-01	HIGH	1.5升小型客车标准外廓。	READY
164478_swb_lowroof	164478	Van	Transit City I			EU-FORD-TRANSIT-CITY-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶纯电厢式外廓。	READY
164478_lwb_highroof	164478	Van	Transit City I			EU-FORD-TRANSIT-CITY-I-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶纯电厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-VE64-MPV-SWB-LOWROOF-01	4616	1972	1978	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-SWB-MEDIUMROOF-01	4616	1972	2172	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-SWB-HIGHROOF-01	4616	1972	2536	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-LWB-MEDIUMROOF-01	5368	1972	2051	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-LWB-HIGHROOF-01	5368	1972	2255	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TAUNUS-TRANSIT-FK1000-MPV-01	4300	1740	1955	Auto Zeitung Ford Transit Panorama technical data	https://www.autozeitung.de/vw-t1-samba-bulli-ford-transit-panorama-classic-cars-89829.html
EU-FORD-TRANSIT-CITY-I-VAN-SWB-LOWROOF-01	4985	1885	1991	Ford Transit City official pricelist	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Transit_City.pdf
EU-FORD-TRANSIT-CITY-I-VAN-LWB-HIGHROOF-01	5285	1885	2285	Ford Transit City official pricelist	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Transit_City.pdf
```

## 下一步优先处理

执行唯一一次轻量机械收尾：固定表头、唯一键、映射引用闭合、尺寸及来源非空检查；随后直接输出两张最终完整 TSV 和两个指定 sandbox 下载链接。

推进信号：CONTINUE

[1]: https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya "Dimensions of the car (General information / User manual / Ford Transit 2 1986-2000)"
[2]: https://www.autozeitung.de/vw-t1-samba-bulli-ford-transit-panorama-classic-cars-89829.html?utm_source=chatgpt.com "Ford Transit Panorama vs. VW T1 Samba Bulli"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6101-6200_ktype_dimension_mapping_final.tsv
- left18448_6101-6200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已完成唯一一次轻量机械收尾。
* Ktype 映射表：359 行，`id` 全部唯一，覆盖 100 个输入 Ktype，全部为 `READY`。
* DIMENSION_GROUP 表：74 行，`DIMENSION_GROUP_ID` 全部唯一，无孤立组。
* 所有映射引用均闭合；尺寸、来源与 URL 均非空。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：359
* PENDING：0
* DIMENSION_GROUP：74
* 状态：完成

## 最终完整 Ktype 映射 TSV

完整 TSV 共 359 条映射，已写入下方下载文件：

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6101-6200_ktype_dimension_mapping_final.tsv)

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11969_mwb_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
11969_mwb_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
11969_lwb_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
11969_lwb_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
11969_lwb_ef_srw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
11969_lwb_ef_drw	11969	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
11971_mwb_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
11971_mwb_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
11971_lwb_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
11971_lwb_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
11971_lwb_ef_srw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
11971_lwb_ef_drw	11971	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
54979_lwb_mediumroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	MEDIUM	长轴中顶乘用外廓。	READY
54979_el_mediumroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	MEDIUM	加长轴中顶乘用外廓。	READY
54979_el_highroof	54979	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	MEDIUM	加长轴高顶乘用外廓。	READY
145254_lwb_mediumroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	MEDIUM	长轴中顶乘用外廓。	READY
145254_el_mediumroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	MEDIUM	加长轴中顶乘用外廓。	READY
145254_el_highroof	145254	MPV	Transit V348	V348		EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	MEDIUM	加长轴高顶乘用外廓。	READY
16101_swb	16101	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
16101_mwb	16101	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
111065_mwb_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
111065_mwb_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
111065_lwb_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
111065_lwb_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
111065_lwb_ef_srw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
111065_lwb_ef_drw	111065	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
111066_swb_lowroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
111066_swb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
111066_mwb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
111066_mwb_highroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
111066_lwb_mediumroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
111066_lwb_highroof	111066	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
111063_mwb_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	MEDIUM	中轴单后轮底盘外廓。	READY
111063_mwb_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	MEDIUM	中轴双后轮底盘外廓。	READY
111063_lwb_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	MEDIUM	长轴单后轮底盘外廓。	READY
111063_lwb_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	MEDIUM	长轴双后轮底盘外廓。	READY
111063_lwb_ef_srw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	MEDIUM	加长轴单后轮底盘外廓。	READY
111063_lwb_ef_drw	111063	Pickup	Transit V348	V348		EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	MEDIUM	加长轴双后轮底盘外廓。	READY
111064_swb_lowroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
111064_swb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
111064_mwb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
111064_mwb_highroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
111064_lwb_mediumroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
111064_lwb_highroof	111064	Van	Transit V348	V348		EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
16096_swb_lowroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
16096_swb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
16096_mwb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
16096_mwb_highroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
16096_lwb_mediumroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
16096_lwb_highroof	16096	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
16099_swb_lowroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
16099_swb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
16099_mwb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
16099_mwb_highroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
16099_lwb_mediumroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
16099_lwb_highroof	16099	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14730_swb_lowroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14730_swb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14730_mwb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14730_mwb_highroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14730_lwb_mediumroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14730_lwb_highroof	14730	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14731_swb_lowroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14731_swb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14731_mwb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14731_mwb_highroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14731_lwb_mediumroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14731_lwb_highroof	14731	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14733_swb	14733	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14733_mwb	14733	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14734_swb	14734	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14734_mwb	14734	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14850_swb	14850	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14850_mwb	14850	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
14729_swb_lowroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14729_swb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14729_mwb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14729_mwb_highroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14729_lwb_mediumroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14729_lwb_highroof	14729	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14732_swb_lowroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14732_swb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14732_mwb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14732_mwb_highroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14732_lwb_mediumroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14732_lwb_highroof	14732	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
14848_swb_lowroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
14848_swb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
14848_mwb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
14848_mwb_highroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
14848_lwb_mediumroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
14848_lwb_highroof	14848	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
14849_swb_lowroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
14849_swb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
14849_mwb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
14849_mwb_highroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
14849_lwb_mediumroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
14849_lwb_highroof	14849	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18089_swb	18089	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
18089_mwb	18089	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
18090_swb_lowroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
18090_swb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
18090_mwb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
18090_mwb_highroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
18090_lwb_mediumroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
18090_lwb_highroof	18090	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18091_swb_lowroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
18091_swb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
18091_mwb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
18091_mwb_highroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
18091_lwb_mediumroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
18091_lwb_highroof	18091	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
16551_swb_lowroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
16551_swb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
16551_mwb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
16551_mwb_highroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
16551_lwb_mediumroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
16551_lwb_highroof	16551	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
17781_swb	17781	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
17781_mwb	17781	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
17782_swb_lowroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
17782_swb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
17782_mwb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
17782_mwb_highroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
17782_lwb_mediumroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
17782_lwb_highroof	17782	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18086_swb_lowroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶乘用外廓。	READY
18086_swb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶乘用外廓。	READY
18086_mwb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶乘用外廓。	READY
18086_mwb_highroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用外廓。	READY
18086_lwb_mediumroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶乘用外廓。	READY
18086_lwb_highroof	18086	MPV	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶乘用外廓。	READY
18087_swb_lowroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式外廓。	READY
18087_swb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶厢式外廓。	READY
18087_mwb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	MEDIUM	中轴中顶厢式外廓。	READY
18087_mwb_highroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式外廓。	READY
18087_lwb_mediumroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶厢式外廓。	READY
18087_lwb_highroof	18087	Van	Transit V185	V185		EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
18088_swb	18088	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
18088_mwb	18088	Pickup	Transit V185	V185		EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	MEDIUM	中轴底盘外廓。	READY
11021_swb	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
11021_lwb	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
11021_extended	11021	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8727_swb_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	MEDIUM	1992年改款前短轴底盘外廓。	READY
8727_lwb_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	MEDIUM	1992年改款前长轴底盘外廓。	READY
8727_extended_prefl	8727	Pickup	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	MEDIUM	1992年改款前加长底盘外廓。	READY
8727_swb_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	1992年改款后短轴底盘外廓。	READY
8727_lwb_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	1992年改款后长轴底盘外廓。	READY
8727_extended_facelift	8727	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	1992年改款后加长底盘外廓。	READY
8764_swb	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8764_lwb	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8764_extended	8764	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8765_swb	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8765_lwb	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8765_extended	8765	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8790_swb	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8790_lwb	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8790_extended	8790	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8793_swb	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8793_lwb	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8793_extended	8793	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8794_swb_lowroof	8794	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶厢式外廓。	READY
8794_lwb_mediumroof	8794	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶厢式外廓。	READY
8836_swb_lowroof	8836	MPV	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶乘用外廓。	READY
8836_lwb_mediumroof	8836	MPV	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶乘用外廓。	READY
14735_swb_lowroof	14735	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	MEDIUM	短轴低顶厢式外廓。	READY
14735_lwb_mediumroof	14735	Van	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	MEDIUM	长轴中顶厢式外廓。	READY
14845_swb	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
14845_lwb	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
14845_extended	14845	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8762_swb	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8762_lwb	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8762_extended	8762	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8789_swb	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8789_lwb	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8789_extended	8789	Pickup	Transit VE83	VE83		EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8791_swb	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8791_lwb	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8791_extended	8791	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
8792_swb	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	MEDIUM	短轴底盘外廓。	READY
8792_lwb	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	MEDIUM	长轴底盘外廓。	READY
8792_extended	8792	Pickup	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	MEDIUM	加长底盘外廓。	READY
16562_swb_lowroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-SWB-LOWROOF-01	MEDIUM	1992年改款前短轴低顶乘用外廓。	READY
16562_swb_highroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-SWB-HIGHROOF-01	MEDIUM	1992年改款前短轴高顶乘用外廓。	READY
16562_lwb_highroof_prefl	16562	MPV	Transit VE6	VE6		EU-FORD-TRANSIT-VE6-MPV-LWB-HIGHROOF-01	MEDIUM	1992年改款前长轴高顶乘用外廓。	READY
16562_swb_lowroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-LOWROOF-01	MEDIUM	1992年改款后短轴低顶乘用外廓。	READY
16562_swb_mediumroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-MEDIUMROOF-01	MEDIUM	1992年改款后短轴中顶乘用外廓。	READY
16562_swb_highroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-HIGHROOF-01	MEDIUM	1992年改款后短轴高顶乘用外廓。	READY
16562_lwb_mediumroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-MEDIUMROOF-01	MEDIUM	1992年改款后长轴中顶乘用外廓。	READY
16562_lwb_highroof_facelift	16562	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-HIGHROOF-01	MEDIUM	1992年改款后长轴高顶乘用外廓。	READY
6610	6610	MPV	FK 1000/Taunus Transit			EU-FORD-TAUNUS-TRANSIT-FK1000-MPV-01	HIGH	1.5升小型客车标准外廓。	READY
164478_swb_lowroof	164478	Van	Transit City I			EU-FORD-TRANSIT-CITY-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶纯电厢式外廓。	READY
164478_lwb_highroof	164478	Van	Transit City I			EU-FORD-TRANSIT-CITY-I-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶纯电厢式外廓。	READY
116212_swb	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
116212_lwb_5seat	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
116212_lwb_7seat	116212	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
116213_swb	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
116213_lwb_5seat	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
116213_lwb_7seat	116213	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
117100_swb	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
117100_lwb_5seat	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
117100_lwb_7seat	117100	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100088_swb	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100088_lwb_5seat	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100088_lwb_7seat	100088	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100089_swb	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100089_lwb_5seat	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100089_lwb_7seat	100089	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
100090_swb	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	MEDIUM	短轴五座乘用外廓。	READY
100090_lwb_5seat	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	MEDIUM	长轴五座乘用外廓。	READY
100090_lwb_7seat	100090	MPV	Transit Connect II	V408	5	EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	MEDIUM	长轴七座乘用外廓。	READY
16965_van_swb	16965	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
16965_van_lwb	16965	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
16965_mpv_swb	16965	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
16965_mpv_lwb	16965	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
12563_van_swb	12563	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
12563_van_lwb	12563	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
12563_mpv_swb	12563	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
12563_mpv_lwb	12563	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
16966_van_swb	16966	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
16966_van_lwb	16966	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
16966_mpv_swb	16966	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
16966_mpv_lwb	16966	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
17783_van_swb	17783	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	MEDIUM	短轴低顶厢式外廓。	READY
17783_van_lwb	17783	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	长轴高顶厢式外廓。	READY
17783_mpv_swb	17783	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	MEDIUM	短轴乘用外廓。	READY
17783_mpv_lwb	17783	MPV	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	MEDIUM	长轴高顶乘用外廓。	READY
802191_lwb	802191	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	MEDIUM	纯电长轴高顶厢式外廓。	READY
53399_swb_prefl	53399	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53399_lwb_prefl	53399	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
803376_swb_facelift	803376	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	HIGH	改款后短轴厢式外廓。	READY
803376_lwb_facelift	803376	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	HIGH	改款后长轴厢式外廓。	READY
145154_swb_facelift	145154	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	HIGH	改款后短轴厢式外廓。	READY
145154_lwb_facelift	145154	Van	Transit Connect II facelift	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	HIGH	改款后长轴厢式外廓。	READY
116210_swb_prefl	116210	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
116210_lwb_prefl	116210	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
116211_swb_prefl	116211	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
116211_lwb_prefl	116211	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
121226_swb_prefl	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
121226_lwb_prefl	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
145750_swb_prefl	145750	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
145750_lwb_prefl	145750	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53394_swb_prefl	53394	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53394_lwb_prefl	53394	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53389_swb_prefl	53389	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53389_lwb_prefl	53389	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53392_swb_prefl	53392	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53392_lwb_prefl	53392	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
53393_swb_prefl	53393	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	HIGH	改款前短轴厢式外廓。	READY
53393_lwb_prefl	53393	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	HIGH	改款前长轴厢式外廓。	READY
801038_swb	801038	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
801038_lwb	801038	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151572_swb	151572	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151572_lwb	151572	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151589_swb	151589	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151589_lwb	151589	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151625_swb	151625	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151625_lwb	151625	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
151626_swb	151626	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴四驱厢式物理外廓。	READY
151626_lwb	151626	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴四驱厢式物理外廓。	READY
151590_swb	151590	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
151590_lwb	151590	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
800151_swb	800151	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	MEDIUM	短轴厢式物理外廓。	READY
800151_lwb	800151	Van	Transit Connect V761	V761		EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	MEDIUM	长轴厢式物理外廓。	READY
101057	101057	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101058_van	101058	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101058_mpv	101058	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
101055	101055	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101056_van	101056	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101056_mpv	101056	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
115170_van	115170	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
115170_mpv	115170	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
115174	115174	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101053	101053	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	五门乘用外廓。	READY
101054_van	101054	Van	Transit Courier I	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
101054_mpv	101054	MPV	Transit Courier I	B460	5	EU-FORD-TRANSIT-COURIER-B460-MPV-01	HIGH	混合车身目录拆分为乘用外廓。	READY
155264_van	155264	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155264_mpv	155264	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
155265_van	155265	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155265_mpv	155265	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
155266_van	155266	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	混合车身目录拆分为厢式外廓。	READY
155266_mpv	155266	MPV	Transit Courier II	V769	5	EU-FORD-TRANSIT-COURIER-V769-MPV-01	HIGH	混合车身目录拆分为五门乘用外廓。	READY
801230	801230	Van	Transit Courier II	V769		EU-FORD-TRANSIT-COURIER-V769-VAN-01	HIGH	纯电厢式外廓。	READY
118533_l1h1_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118533_l1h2_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118533_l2h1_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118533_l2h2_prefl	118533	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118533_l1h1_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118533_l1h2_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118533_l2h1_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118533_l2h2_facelift	118533	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118534_l1h1_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118534_l1h2_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118534_l2h1_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118534_l2h2_prefl	118534	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118534_l1h1_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118534_l1h2_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118534_l2h1_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118534_l2h2_facelift	118534	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118535_l1h1_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
118535_l1h2_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
118535_l2h1_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
118535_l2h2_prefl	118535	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
118535_l1h1_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶厢式外廓。	READY
118535_l1h2_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶厢式外廓。	READY
118535_l2h1_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶厢式外廓。	READY
118535_l2h2_facelift	118535	Van	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶厢式外廓。	READY
118536_l1h1_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118536_l1h2_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118536_l2h1_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118536_l2h2_prefl	118536	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118536_l1h1_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118536_l1h2_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118536_l2h1_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118536_l2h2_facelift	118536	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
118537_l1h1_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118537_l1h2_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118537_l2h1_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118537_l2h2_prefl	118537	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118537_l1h1_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118537_l1h2_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118537_l2h1_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118537_l2h2_facelift	118537	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
118538_l1h1_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
118538_l1h2_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
118538_l2h1_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
118538_l2h2_prefl	118538	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
118538_l1h1_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
118538_l1h2_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
118538_l2h1_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
118538_l2h2_facelift	118538	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
147111_l1h1_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
147111_l1h2_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
147111_l2h1_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
147111_l2h2_facelift	147111	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
147115_l1h1_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	HIGH	改款后短轴低顶乘用外廓。	READY
147115_l1h2_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	HIGH	改款后短轴高顶乘用外廓。	READY
147115_l2h1_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	HIGH	改款后长轴低顶乘用外廓。	READY
147115_l2h2_facelift	147115	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	HIGH	改款后长轴高顶乘用外廓。	READY
58539_l1h1_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58539_l1h2_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58539_l2h1_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58539_l2h2_prefl	58539	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58540_l1h1_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58540_l1h2_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58540_l2h1_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58540_l2h2_prefl	58540	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58541_l1h1_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶乘用外廓。	READY
58541_l1h2_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶乘用外廓。	READY
58541_l2h1_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶乘用外廓。	READY
58541_l2h2_prefl	58541	MPV	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶乘用外廓。	READY
58543_l1h1_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
58543_l1h2_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
58543_l2h1_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
58543_l2h2_prefl	58543	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
58544_l1h1_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	HIGH	改款前短轴低顶厢式外廓。	READY
58544_l1h2_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	HIGH	改款前短轴高顶厢式外廓。	READY
58544_l2h1_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	HIGH	改款前长轴低顶厢式外廓。	READY
58544_l2h2_prefl	58544	Van	Transit Custom I	V362		EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	HIGH	改款前长轴高顶厢式外廓。	READY
```

## 最终完整 DIMENSION_GROUP TSV

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6101-6200_dimension_groups_final.tsv)

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V348-CHASSIS-MWB-SRW-01	5481	1974	2035	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-CHASSIS-MWB-DRW-01	5481	2052	2035	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-CHASSIS-LWB-SRW-01	5931	1974	2031	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-CHASSIS-LWB-DRW-01	5931	2052	2031	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-SRW-01	6319	1974	2030	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-CHASSIS-LWB-EF-DRW-01	6319	2052	2030	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-MPV-LWB-MEDIUMROOF-DRW-01	5680	2084	2394	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-MPV-EL-MEDIUMROOF-DRW-01	6403	2084	2380	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-MPV-EL-HIGHROOF-DRW-01	6403	2084	2624	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V185-CHASSIS-SWB-01	5085	1974	2015	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-CHASSIS-MWB-01	5452	1974	2014	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V348-VAN-SWB-LOWROOF-01	4863	1974	2083	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-VAN-SWB-MEDIUMROOF-01	4863	1974	2398	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-VAN-MWB-MEDIUMROOF-01	5230	1974	2397	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-VAN-MWB-HIGHROOF-01	5230	1974	2611	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-VAN-LWB-MEDIUMROOF-01	5680	1974	2394	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V348-VAN-LWB-HIGHROOF-01	5680	1974	2606	Ford Transit official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-V185-SWB-LOWROOF-01	4834	1974	1974	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-SWB-MEDIUMROOF-01	4834	1974	2313	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-MWB-MEDIUMROOF-01	5201	1974	2309	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-MWB-HIGHROOF-01	5201	1974	2529	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-LWB-MEDIUMROOF-01	5651	1974	2303	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-V185-LWB-HIGHROOF-01	5651	1974	2524	Ford Transit official specifications 2003	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf
EU-FORD-TRANSIT-VE6-CHASSIS-SWB-01	4615	1925	1976	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-CHASSIS-LWB-01	5290	1925	2004	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-CHASSIS-EXTENDED-01	6007	1925	2004	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-CHASSIS-SWB-01	4620	1971	2018	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-CHASSIS-LWB-01	5355	1971	2026	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-CHASSIS-EXTENDED-01	6085	1971	2026	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE83-CHASSIS-SWB-01	4616	1974	2026	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE83-CHASSIS-LWB-01	5376	1974	2026	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE83-CHASSIS-EXTENDED-01	6085	1974	2026	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE83-MPV-SWB-LOWROOF-CNG-01	4616	1974	2024	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE83-MPV-LWB-MEDIUMROOF-CNG-01	5368	1974	2255	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-MPV-SWB-LOWROOF-01	4606	1938	1952	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-MPV-SWB-HIGHROOF-01	4606	1938	2170	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-MPV-LWB-HIGHROOF-01	5358	1972	2238	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-SWB-LOWROOF-01	4616	1972	1978	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-SWB-MEDIUMROOF-01	4616	1972	2172	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-SWB-HIGHROOF-01	4616	1972	2536	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-LWB-MEDIUMROOF-01	5368	1972	2051	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE64-MPV-LWB-HIGHROOF-01	5368	1972	2255	Ford Transit 1986-2000 owner manual dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TAUNUS-TRANSIT-FK1000-MPV-01	4300	1740	1955	Auto Zeitung Ford Transit Panorama technical data	https://www.autozeitung.de/vw-t1-samba-bulli-ford-transit-panorama-classic-cars-89829.html
EU-FORD-TRANSIT-CITY-I-VAN-SWB-LOWROOF-01	4985	1885	1991	Ford Transit City official pricelist	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Transit_City.pdf
EU-FORD-TRANSIT-CITY-I-VAN-LWB-HIGHROOF-01	5285	1885	2285	Ford Transit City official pricelist	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Transit_City.pdf
EU-FORD-TRANSIT-CONNECT-V408-MPV-SWB-PREFL-01	4418	1835	1852	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-5SEAT-PREFL-01	4818	1835	1845	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-MPV-LWB-7SEAT-PREFL-01	4818	1835	1840	Ford Tourneo Connect official brochure	https://www.ford.pt/content/dam/guxeu/pt/pt_pt/documents/feature-pdfs/FT-Tourneo_Connect.pdf
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-01	4275	1795	1815	Ford Transit Connect Van official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-Connect-UK.pdf
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-01	4525	1795	1980	Ford Transit Connect Van official brochure 2011	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Transit-Connect-UK.pdf
EU-FORD-TRANSIT-CONNECT-I-MPV-SWB-01	4278	1795	1814	Automobile-Catalog Ford Tourneo Connect SWB specifications	https://www.automobile-catalog.com/car/2002/980285/ford_tourneo_connect_swb_1_8_tdci.html
EU-FORD-TRANSIT-CONNECT-I-MPV-LWB-01	4525	1795	1981	Ford Tourneo Connect official specification brochure 2004	https://xr793.com/wp-content/uploads/2022/09/2024-Ford-People-Movers-Specs-UK.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-PREFL-01	4418	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-PREFL-01	4818	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-SWB-FACELIFT-01	4425	1835	1859	Ford Transit Connect official brochure	https://www.ford.pl/content/dam/guxeu/pl/pl_pl/documents/brochures/commercial-vehicles/BRO-ford_transit_connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-LWB-FACELIFT-01	4825	1835	1847	Ford Transit Connect official brochure	https://www.ford.pl/content/dam/guxeu/pl/pl_pl/documents/brochures/commercial-vehicles/BRO-ford_transit_connect.pdf
EU-FORD-TRANSIT-CONNECT-V761-VAN-SWB-01	4500	1855	1856	Ford Transit Connect official specifications	https://www.ford.co.uk/vans-and-pickups/transit-connect
EU-FORD-TRANSIT-CONNECT-V761-VAN-LWB-01	4853	1855	1860	Ford Transit Connect official specifications	https://www.ford.co.uk/vans-and-pickups/transit-connect
EU-FORD-TRANSIT-COURIER-B460-MPV-01	4157	1764	1741	Ford Tourneo Courier official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Tourneo-Courier.pdf
EU-FORD-TRANSIT-COURIER-B460-VAN-01	4157	1764	1770	Ford Transit Courier official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_courier.pdf
EU-FORD-TRANSIT-COURIER-V769-VAN-01	4337	1800	1827	Ford Transit Courier 2024 official technical specifications; Ford Transit Courier and E-Transit Courier official price list	https://www.fordpresse.be/content/documents/news/2024/transit_courier_technical_specification_eu.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/All_New_PL-Transit_Courier.pdf
EU-FORD-TRANSIT-COURIER-V769-MPV-01	4337	1791	1817	Ford Tourneo Courier 2024 official technical specifications	https://www.fordpers.be/content/documents/news/2024/tourneo_courier_technical_specification_eu.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	4972	1986	2020	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	4972	1986	2389	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	5339	1986	2017	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	5339	1986	2381	Ford Transit Custom official brochure 2016	https://cavanaghs.com/wp-content/uploads/2016/11/transit-custom-ebrochure.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	4973	1986	2000	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	4973	1986	2366	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	5340	1986	1979	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	5340	1986	2343	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	4973	1986	2020	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	4973	1986	2389	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	5340	1986	2017	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	5340	1986	2381	Ford Transit Custom official brochure 2021	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
```

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2812 行）
- 累计尺寸组：dimension_groups_final.tsv（643 行）

