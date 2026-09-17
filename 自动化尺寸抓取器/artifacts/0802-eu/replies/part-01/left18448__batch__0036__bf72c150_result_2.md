# 任务：left18448 第 3501-3600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0036__bf72c150


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3501-3600 行

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
left18448 第 3501-3600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	4380	1810	1865
EU-CITROEN-BERLINGO-II-B9-MPV-01	4380	1810	1852
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1828
EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	4380	1810	1828
EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	4380	1810	1801
EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	4380	1810	1831
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-M-01	4403	1848	1895
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-XL-01	4753	1848	1895
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-HIGH-01	4401	1848	1860
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-LOW-01	4401	1848	1796
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-HIGH-01	4751	1848	1860
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-LOW-01	4751	1848	1812
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-BERLINGO-III-K9-VAN-M-HIGH-01	4403	1848	1860
EU-CITROEN-BERLINGO-III-K9-VAN-M-LOW-01	4403	1848	1796
EU-CITROEN-BERLINGO-III-K9-VAN-XL-HIGH-01	4753	1848	1860
EU-CITROEN-BERLINGO-III-K9-VAN-XL-LOW-01	4753	1848	1812
EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	4123	1719	1912
EU-CITROEN-BERLINGO-I-M49-EARLY-01	4108	1698	1802
EU-CITROEN-BERLINGO-I-M49-LATE-01	4108	1719	1802
EU-CITROEN-BERLINGO-I-M59-DANGEL-4X4-01	4137	1724	1950
EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	4137	1724	1810

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Citroën	Berlingo	Electrique	Großraumlimousine	Frontantrieb	Elektro	Jan 2000	Oct 2002	15053
Citroën	Bx	11	Schrägheck	Frontantrieb	Benzin	Oct 1988	Jun 1992	15055
Citroën	Bx	14	Kombi	Frontantrieb	Benzin	Jan 1989	Dec 1989	14131
Citroën	Bx	15	Schrägheck	Frontantrieb	Benzin	Oct 1987	May 1992	15056
Citroën	Bx	15	Kombi	Frontantrieb	Benzin	Oct 1987	May 1992	15057
Citroën	Bx	16	Kombi	Frontantrieb	Benzin	Jun 1985	Jun 1988	14132
Citroën	Bx	19	Schrägheck	Frontantrieb	Benzin	Jul 1986	May 1989	15058
Citroën	Bx	19	Schrägheck	Frontantrieb	Benzin	Sep 1984	Jan 1992	123830
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	Jan 1987	Jan 1992	123831
Citroën	Bx	18 D	Kombi	Frontantrieb	Diesel	Oct 1985	Sep 1993	15060
Citroën	Bx	19 GTI	Schrägheck	Frontantrieb	Benzin	Oct 1984	Jun 1994	113288
Citroën	C1	1	Schrägheck	Frontantrieb	Benzin	Jun 2005	Sep 2014	18584
Citroën	C1	1.0 VTI 68	Schrägheck	Frontantrieb	Benzin	Apr 2014	Apr 2018	105909
Citroën	C1	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Apr 2014	Apr 2018	105910
Citroën	C1	1.4 HDI	Schrägheck	Frontantrieb	Diesel	Jun 2005	Sep 2014	18585
Citroën	C15	1.4 E	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 1987	Dec 1996	6590
Citroën	C15	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2000	Dec 2005	18017
Citroën	C2	1.1	Schrägheck	Frontantrieb	Benzin	Sep 2003	Sep 2012	17330
Citroën	C2	1.4	Schrägheck	Frontantrieb	Benzin	Sep 2003	Dec 2009	17331
Citroën	C2	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2003	Oct 2010	17332
Citroën	C2	1.4 HDI	Schrägheck	Frontantrieb	Diesel	Jul 2003	Dec 2009	17333
Citroën	C2	1.6 VTS	Schrägheck	Frontantrieb	Benzin	Oct 2004	Dec 2009	18613
Citroën	C25	2.5 D 4X4	Bus	Allrad	Diesel	Jan 1987	Feb 1994	6591
Citroën	C3 aircross i	1.2 Puretech 110	SUV	Frontantrieb	Benzin	Jun 2017	-	128136
Citroën	C3 aircross i	1.2 Puretech 130	SUV	Frontantrieb	Benzin	Jul 2017	-	128184
Citroën	C3 aircross i	1.2 Puretech 82	SUV	Frontantrieb	Benzin	Jun 2017	-	128135
Citroën	C3 aircross i	1.6 Bluehdi 100	SUV	Frontantrieb	Diesel	Jul 2017	Aug 2018	128133
Citroën	C3 aircross i	1.6 Bluehdi 115	SUV	Frontantrieb	Diesel	Jun 2017	May 2018	128185
Citroën	C3 aircross i	1.6 Bluehdi 120	SUV	Frontantrieb	Diesel	Jul 2017	May 2018	128134
Citroën	C3 aircross ii	1.2 Hybrid 136	SUV	Frontantrieb	Benzin/Elektro	Oct 2024	Apr 2025	801816
Citroën	C3 aircross ii	1.2 Hybrid 145	SUV	Frontantrieb	Benzin/Elektro	Apr 2025	-	800210
Citroën	C3 aircross ii	1.2 Puretech 100	SUV	Frontantrieb	Benzin	Jul 2024	-	800209
Citroën	C3 aircross ii	Ë-c3	SUV	Frontantrieb	Elektro	Apr 2024	-	800208
Citroën	C3 i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Dec 2003	Aug 2010	17892
Citroën	C3 i	1.6 16V HDI	Schrägheck	Frontantrieb	Diesel	Sep 2005	Dec 2009	19017
Citroën	C3 ii	1.0 VTI 68	Schrägheck	Frontantrieb	Benzin	Aug 2012	Sep 2016	58663
Citroën	C3 ii	1.1 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2010	Sep 2016	12292
Citroën	C3 ii	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	Oct 2014	Sep 2016	109326
Citroën	C3 ii	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Jun 2012	Sep 2016	58664
Citroën	C3 ii	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2013	Sep 2016	53297
Citroën	C3 ii	1.4 VTI	Schrägheck	Frontantrieb	Benzin	Nov 2009	Sep 2016	117928
Citroën	C3 ii	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Jul 2014	Sep 2016	113665
Citroën	C3 ii	1.6 Bluehdi 75	Schrägheck	Frontantrieb	Diesel	Apr 2015	Sep 2016	113666
Citroën	C3 ii	1.6 HDI 115	Schrägheck	Frontantrieb	Diesel	Sep 2012	Sep 2016	58666
Citroën	C3 iii	1.2 VTI 68	Schrägheck	Frontantrieb	Benzin	Jul 2016	-	121982
Citroën	C3 iii van	1.2 VTI	Kasten/Schrägheck	Frontantrieb	Benzin	Jul 2016	-	146803
Citroën	C3 iv	1.2 Hybrid 110	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2024	-	801160
Citroën	C3 iv	1.2 Puretech 100	Schrägheck	Frontantrieb	Benzin	Apr 2024	-	158589
Citroën	C3 iv	Ë-c3	Schrägheck	Frontantrieb	Elektro	Jan 2024	-	157568
Citroën	C3 iv van	Ë-c3	Kasten/Schrägheck	Frontantrieb	Elektro	Apr 2024	-	801490
Citroën	C3 iv van	Puretech 100	Kasten/Schrägheck	Frontantrieb	Benzin	Apr 2024	-	801291
Citroën	C3 origin iii	1.2 Puretech 110	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	801393
Citroën	C3 origin iii	1.2 Puretech 82	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	801399
Citroën	C3 origin iii	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Mar 2024	-	802343
Citroën	C3 picasso	1.2 THP 110	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Dec 2015	112336
Citroën	C3 picasso	1.4 VTI 95 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Sep 2010	Nov 2015	56263
Citroën	C3 picasso	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Aug 2017	112338
Citroën	C3 picasso	1.6 HDI 115	Großraumlimousine	Frontantrieb	Diesel	Jan 2013	Mar 2015	58588
Citroën	C3 picasso	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Mar 2015	33783
Citroën	C3 pluriel	1.4	Cabriolet	Frontantrieb	Benzin	May 2003	-	17277
Citroën	C3 pluriel	1.6	Cabriolet	Frontantrieb	Benzin	May 2003	-	17276
Citroën	C3 pluriel	1.4 HDI	Cabriolet	Frontantrieb	Diesel	Apr 2004	-	18085
Citroën	C35	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Nov 1973	Jan 1994	18874
Citroën	C35	2.2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 1973	Jan 1980	18875
Citroën	C35	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Feb 1980	Jan 1994	18876
Citroën	C4	1.4 16V	Coupe	Frontantrieb	Benzin	Nov 2004	Jul 2011	18339
Citroën	C4	1.6 16V	Coupe	Frontantrieb	Benzin	Nov 2004	Jul 2011	18340
Citroën	C4	1.6 HDI	Coupe	Frontantrieb	Diesel	Nov 2004	Jul 2011	18343
Citroën	C4	1.6 HDI	Coupe	Frontantrieb	Diesel	Nov 2004	Jul 2011	18344
Citroën	C4	2.0 16V	Coupe	Frontantrieb	Benzin	Nov 2004	Jul 2007	18341
Citroën	C4	2.0 16V	Coupe	Frontantrieb	Benzin	Nov 2004	Dec 2010	18342
Citroën	C4	2.0 HDI	Coupe	Frontantrieb	Diesel	Nov 2004	Dec 2010	18345
Citroën	C4	2.0 VTR	Coupe	Frontantrieb	Benzin	Oct 2006	Dec 2007	100901
Citroën	C4 aircross	1.6	SUV	Frontantrieb	Benzin	Apr 2012	-	55133
Citroën	C4 aircross	1.6 HDI 115	SUV	Frontantrieb	Diesel	Apr 2012	-	55134
Citroën	C4 aircross	1.6 HDI 115 AWC	SUV	Allrad	Diesel	May 2012	-	55135
Citroën	C4 aircross	1.8 HDI 150	SUV	Frontantrieb	Diesel	Apr 2012	-	55136
Citroën	C4 aircross	1.8 HDI 150 AWC	SUV	Allrad	Diesel	Apr 2012	-	55137
Citroën	C4 cactus	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	Sep 2014	-	108027
Citroën	C4 cactus	1.2 VTI 75 / Puretech 75	Schrägheck	Frontantrieb	Benzin	Sep 2014	-	108026
Citroën	C4 cactus	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Sep 2014	-	105914
Citroën	C4 cactus	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Sep 2014	Jun 2018	108028
Citroën	C4 cactus	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	Sep 2014	-	105916
Citroën	C4 grand picasso ii	1.2 THP 130	Großraumlimousine	Frontantrieb	Benzin	Apr 2014	-	112367
Citroën	C4 grand picasso ii	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Apr 2016	114209
Citroën	C4 grand picasso ii	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	Jul 2014	Dec 2018	108851
Citroën	C4 grand picasso ii	1.6 HDI / Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	Mar 2018	53293
Citroën	C4 grand picasso ii	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	53221
Citroën	C4 grand picasso ii	1.6 THP 155	Großraumlimousine	Frontantrieb	Benzin	Sep 2013	-	53217
Citroën	C4 grand picasso ii	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	Jul 2014	-	108158
Citroën	C4 grand picasso ii	1.6 VTI 120	Großraumlimousine	Frontantrieb	Benzin	Sep 2013	-	53216
Citroën	C4 grand picasso ii	2.0 Bluehdi 135	Großraumlimousine	Frontantrieb	Diesel	Sep 2013	-	117923
Citroën	C4 grand picasso ii	2.0 Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	Jun 2013	-	53296
Citroën	C4 i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Nov 2004	Jul 2011	18332
Citroën	C4 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	Nov 2004	Jul 2011	18333
Citroën	C4 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Nov 2004	Jul 2011	18336
Citroën	C4 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Nov 2004	Jul 2011	18337
Citroën	C4 i	1.6 HDI	Stufenheck	Frontantrieb	Diesel	Apr 2010	Nov 2012	145964
Citroën	C4 i	1.6 HDI	Stufenheck	Frontantrieb	Diesel	Apr 2010	Nov 2012	145965
Citroën	C4 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Apr 2010	Nov 2012	145966


--- Round 1 / 首次发送 ---
## 更新点

* 复用既有 `EU-CITROEN-BERLINGO-I-M49-LATE-01`，未重复创建 Berlingo 尺寸组。
* 闭合 BX 普通 Hatchback/Wagon 的 Phase I、Phase II 四个外廓；跨越 1986 年改款的 Ktype 已拆分，GTI 特殊外观暂不纳入。
* C1 II 官方资料同时列出三门、五门车型，二者外部三维相同，因此映射拆门数、共用一个尺寸组。([汽车目录档案][1])
* C15 标准封闭式车身尺寸已闭合为 `3995×1636×1801 mm`。([Dezo's Garage][2])
* 闭合 C3 I 改款前后、C3 Picasso、C3 Pluriel；Pluriel 三维由产品技术资料直接支持。([c3pluriel.fr][3])
* 闭合 C4 I Coupe/Hatchback 的 Phase I、Phase II 外廓；Phase II Coupe 的宽度明确为不含后视镜口径。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：51
* READY 覆盖输入 Ktype：36
* PENDING 输入 Ktype：64
* 已确认尺寸组：15，其中新建 14 个、复用既有组 1 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15053	15053	MPV	Berlingo I	M49	5	EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	复用既有M49后期MPV尺寸组。	READY
15055	15055	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
14131	14131	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
15056	15056	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
15057	15057	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
14132_prefl	14132	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
14132_facelift	14132	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
15058	15058	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
123830_prefl	123830	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
123830_facelift	123830	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
123831	123831	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
15060_prefl	15060	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
15060_facelift	15060	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
105909_3dr	105909	Hatchback	C1 II		3	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖三门车身。	READY
105909_5dr	105909	Hatchback	C1 II		5	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖五门车身。	READY
105910_3dr	105910	Hatchback	C1 II		3	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖三门车身。	READY
105910_5dr	105910	Hatchback	C1 II		5	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖五门车身。	READY
6590	6590	Van	C15 I	VD		EU-CITROEN-C15-I-VAN-01	MEDIUM	输入车身形式混合Van/MPV；按标准C15封闭式车身。	READY
18017	18017	Van	C15 I	VD		EU-CITROEN-C15-I-VAN-01	MEDIUM	输入车身形式混合Van/MPV；按标准C15封闭式车身。	READY
17892_prefl	17892	Hatchback	C3 I Phase I		5	EU-CITROEN-C3-I-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2005年改款，按改款前分支拆分。	READY
17892_facelift	17892	Hatchback	C3 I Phase II		5	EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2005年改款，按改款后分支拆分。	READY
19017	19017	Hatchback	C3 I Phase II		5	EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
112336	112336	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
56263	56263	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
112338	112338	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
58588	58588	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
33783	33783	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
17277	17277	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
17276	17276	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
18085	18085	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
18339_prefl	18339	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18339_facelift	18339	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18340_prefl	18340	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18340_facelift	18340	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18343_prefl	18343	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18343_facelift	18343	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18344_prefl	18344	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18344_facelift	18344	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18341	18341	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH		READY
18345_prefl	18345	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18345_facelift	18345	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
100901	100901	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH		READY
18332_prefl	18332	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18332_facelift	18332	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18333_prefl	18333	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18333_facelift	18333	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18336_prefl	18336	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18336_facelift	18336	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18337_prefl	18337	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18337_facelift	18337	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
145966	145966	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1650	1365	Automobile-Catalog; Citroënët	https://www.automobile-catalog.com/car/1985/2029220/citroen_bx_19_d.html;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1361	Auto-Data; Citroënët	https://www.auto-data.net/en/citroen-bx-i-phase-ii-1987-19-tzi-109hp-cat-15254;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	4399	1660	1431	Automobile-Catalog; Citroënët	https://www.automobile-catalog.com/car/1985/54530/citroen_bx_break_19_rd.html;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	4399	1682	1431	Auto-Data; Citroënët	https://www.auto-data.net/en/citroen-bx-i-break-phase-ii-1987-14-e-72hp-15266;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-C1-II-HATCHBACK-01	3465	1615	1460	Citroën C1 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/11/Citroen-C1-2014-UK.pdf
EU-CITROEN-C15-I-VAN-01	3995	1636	1801	Citroën Vans 2005 technical specifications	https://xr793.com/wp-content/uploads/2022/09/2005-Citroen-Van-Tech-Specs-UK.pdf
EU-CITROEN-C3-I-PHASE-I-HATCHBACK-5D-01	3850	1667	1529	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/548285/citroen_c3_1_4i_16v_sx.html
EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	3860	1667	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/548615/citroen_c3_1_4i_16v_exclusive_senso_drive.html
EU-CITROEN-C3-PICASSO-I-MPV-5D-01	4078	1766	1631	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2140025/citroen_c3_picasso_bluehdi_100_exclusive.html
EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	3934	1700	1563	Citroën C3 Pluriel product and technical brochure	https://c3pluriel.fr/wp-content/uploads/2024/05/Brochure-c3-pluriel-2006-cote-azur-GB.pdf
EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	4273	1769	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/551405/citroen_c4_coupe_1_6i_16v_vtr.html
EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	4288	1769	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1214945/citroen_c4_coupe_1_4_16v_vtr.html
EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	4260	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/551210/citroen_c4_2_0i_16v_style.html
EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	4275	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1214780/citroen_c4_hdi_90_fap_comfort.html
```

## 下一步优先处理

1. 闭合 C2、C3 II、C3 III/Origin、C3 IV，以及两代 C3 Aircross 的普通高度、车顶纵杆和改款边界。
2. 处理 C4 Aircross、C4 Cactus、C4 Grand Picasso II 与 C4 I Sedan，重点解决高度或改款尺寸冲突。
3. 最后处理 BX GTI、C1 I、C25 4X4 Bus、C35 Platform/Chassis 等特殊外廓。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/11/Citroen-C1-2014-UK.pdf?utm_source=chatgpt.com "NEW CITROËN C1"
[2]: https://xr793.com/wp-content/uploads/2022/09/2005-Citroen-Van-Tech-Specs-UK.pdf?utm_source=chatgpt.com "Citroën Vans"
[3]: https://c3pluriel.fr/wp-content/uploads/2024/05/Brochure-c3-pluriel-2006-cote-azur-GB.pdf?utm_source=chatgpt.com "CITROËN C3 PLURIELPRODUCT & TECHNICAL"
[4]: https://www.automobile-catalog.com/make/citroen/c4_1gen/c4_series_ii_1gen_hatchback/2010.html?utm_source=chatgpt.com "2010 Citroen C4 1gen/II Hatchback full range specs"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 闭合 C2 I 三门 Hatchback 尺寸组；2009 官方资料给出的外廓为 `3666 × 1659 × 1477 mm`，因此未按发动机或普通配置拆组。([汽车目录档案][1])
* C3 II 按改款前后拆为两个外廓：Phase I 为 `3941 × 1728 × 1524 mm`，Phase II 为 `3941 × 1728 × 1538 mm`；跨越改款期的五个 Ktype 已生成 `prefl`、`facelift` 派生行。([汽车目录][2])
* C3 III、C3 III Van 与 C3 Origin III 共用同一外廓；官方规格明确宽度为不含后视镜的 `1749 mm`。
* C4 Aircross 的前驱、四驱和发动机差异不改变外廓，本轮统一链接至 `4341 × 1800 × 1625 mm` 尺寸组。([德国汽车俱乐部][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 映射行：80
* READY 覆盖输入 Ktype：60
* PENDING 输入 Ktype：40
* 已确认尺寸组：20
* 本轮新增 READY 映射：29 行，覆盖 24 个输入 Ktype
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17330	17330	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17331	17331	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17332	17332	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17333	17333	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
18613	18613	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
58663_prefl	58663	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58663_facelift	58663	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
12292_prefl	12292	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
12292_facelift	12292	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
109326	109326	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58664_prefl	58664	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58664_facelift	58664	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
53297	53297	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
117928_prefl	117928	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
117928_facelift	117928	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
113665	113665	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
113666	113666	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58666_prefl	58666	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58666_facelift	58666	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
121982	121982	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
146803	146803	Van	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH	封闭货运版沿用五门车身外廓。	READY
801393	801393	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
801399	801399	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
802343	802343	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
55133	55133	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55134	55134	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55135	55135	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55136	55136	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55137	55137	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1477	Citroën C2 2009 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Citroen-C2-2009-UK.pdf
EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	3941	1728	1524	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1213280/citroen_c3_1_4i_sx.html
EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	3941	1728	1538	Auto-Data	https://www.auto-data.net/en/citroen-c3-ii-phase-ii-2013-1.0-puretech-68hp-27457
EU-CITROEN-C3-III-HATCHBACK-5D-01	3996	1749	1474	Citroën New Zealand C3 official specifications	https://www.citroen.co.nz/content/dam/citroen/new_zealand/documents/2024/citroen-c3-prices-and-specifications-01-2024-CZQ-engine.pdf
EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	4341	1800	1625	ADAC vehicle catalogue	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/citroen/c4-aircross/1generation/232295/
```

## 5. 下一步优先处理

1. 闭合 C3 Aircross I 与 C3 Aircross II，区分两代车型及可能的车顶高度口径。
2. 处理 C3 IV 乘用版与 Van，重点区分无行李架、带行李架及商用版高度。
3. 闭合 C4 Cactus Phase I、C4 Grand Picasso II 和 C4 I Sedan。
4. 最后处理 BX GTI、C1 I、C25 4X4 Bus、C35 Platform/Chassis 等特殊外廓。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2017/07/Citroen-C2-2009-UK.pdf?utm_source=chatgpt.com "Citroën C2"
[2]: https://www.automobile-catalog.com/car/2009/1213280/citroen_c3_1_4i_sx.html?utm_source=chatgpt.com "2009 Citroen C3 1.4i SX (man. 5) (model since mid-year ..."
[3]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/citroen/c4-aircross/1generation/232295/?utm_source=chatgpt.com "Citroen C4 Aircross e-HDi 150 Exclusive 4WD (06/12 - 01/15): Technische Daten, Bilder, Preise | ADAC"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 C3 Aircross I 六个 Ktype，统一关联五门 SUV 外廓 `4155 × 1765 × 1637 mm`。
* 闭合 C3 Aircross II 四个 Ktype；燃油、混动和纯电版本统一关联 `4395 × 1795 × 1660 mm` 外廓。
* 闭合 C3 IV 乘用版及五门封闭货运衍生版，统一关联 `4015 × 1755 × 1577 mm` 外廓。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 映射行：95
* READY 覆盖输入 Ktype：75
* PENDING 输入 Ktype：25
* 已确认尺寸组：23
* 本轮新增 READY 映射：15 行
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128136	128136	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128184	128184	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128135	128135	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128133	128133	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128185	128185	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128134	128134	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
801816	801816	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800210	800210	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800209	800209	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800208	800208	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
801160	801160	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
158589	158589	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
157568	157568	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
801490	801490	Van	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	MEDIUM	五门封闭货运衍生车身。	READY
801291	801291	Van	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	MEDIUM	五门封闭货运衍生车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	4155	1765	1637	Citroën UK C3 Aircross official price and specification guide	https://www.citroen.co.uk/content/dam/citroen/uk/view-price---spec-guide/C3_Aircross_Price_Specification_guide.pdf
EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	4395	1795	1660	Citroën UK New C3 Aircross official price and specification guide; Automobile Dimension	https://www.media.stellantis.com/uploads/uk/attachment/5583/newc3aircrosspricespecificationguide-67a0b03e58700.pdf;https://www.automobiledimension.com/model/citroen/c3-aircross
EU-CITROEN-C3-IV-HATCHBACK-5D-01	4015	1755	1577	Citroën UK New C3 official price and specification guide; Citroën Türkiye New ë-C3 digital catalogue	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/car-range/New-C3-price-and-specification-guide.pdf;https://talep.citroen.com.tr/dijital-katalog/yeni-ec3
```

## 5. 下一步优先处理

1. 闭合 C4 Cactus 与 C4 Grand Picasso II，优先批量解决共用外廓。
2. 处理 C4 I Sedan 和剩余 C4 Coupe 跨改款 Ktype。
3. 最后核对 C1 I、BX GTI、C25 4X4 Bus、C35 Platform/Chassis 等特殊或多外廓车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合 C1 I 汽油、柴油 Ktype 的三门/五门分支；官方技术表列出的外部三维均为 `3435 × 1630 × 1465 mm`。
* BX 19 GTI 按已闭合的 Phase I、Phase II 普通五门外廓拆分，复用既有尺寸组。
* C4 Coupe 2.0 16V Ktype `18342` 按改款前后拆分，复用既有 LA Coupe 尺寸组。
* C4 Cactus I 根据官方资料中的无车顶纵杆/带车顶纵杆高度拆分；跨越 2018 年改款的 Ktype 同时拆分 Phase I、Phase II。Phase I 为 `4157 × 1729 × 1480/1530 mm`，Phase II 为 `4169 × 1729 × 1480/1530 mm`。([citroen.manymanuals.com][1])
* 闭合 C4 I Sedan 两个柴油 Ktype，共用 `4770 × 1770 × 1510 mm` 四门 Sedan 外廓。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 映射行：119
* READY 覆盖输入 Ktype：86
* PENDING 输入 Ktype：14
* 已确认尺寸组：29
* 本轮新增 READY 映射：24 行
* 本轮覆盖新增输入 Ktype：11
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
113288_prefl	113288	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1986年外廓改款，拆分改款前分支。	READY
113288_facelift	113288	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1986年外廓改款，拆分改款后分支。	READY
18584_3dr	18584	Hatchback	C1 I		3	EU-CITROEN-C1-I-HATCHBACK-01	HIGH	同一Ktype覆盖三门车身。	READY
18584_5dr	18584	Hatchback	C1 I		5	EU-CITROEN-C1-I-HATCHBACK-01	HIGH	同一Ktype覆盖五门车身。	READY
18585_3dr	18585	Hatchback	C1 I		3	EU-CITROEN-C1-I-HATCHBACK-01	MEDIUM	同一Ktype覆盖三门车身。	READY
18585_5dr	18585	Hatchback	C1 I		5	EU-CITROEN-C1-I-HATCHBACK-01	MEDIUM	同一Ktype覆盖五门车身。	READY
18342_prefl	18342	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH	跨越2008年外廓改款，拆分改款前分支。	READY
18342_facelift	18342	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	HIGH	跨越2008年外廓改款，拆分改款后分支。	READY
108027_prefl_low	108027	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	改款前无纵向车顶杆外廓。	READY
108027_prefl_roofrails	108027	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	改款前带纵向车顶杆外廓。	READY
108027_facelift_low	108027	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	MEDIUM	改款后无纵向车顶杆外廓。	READY
108027_facelift_roofrails	108027	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	MEDIUM	改款后带纵向车顶杆外廓。	READY
108026_low	108026	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
108026_roofrails	108026	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
105914_low	105914	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
105914_roofrails	105914	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
108028_prefl_low	108028	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	改款前无纵向车顶杆外廓。	READY
108028_prefl_roofrails	108028	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	改款前带纵向车顶杆外廓。	READY
108028_facelift_low	108028	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	MEDIUM	改款后无纵向车顶杆外廓。	READY
108028_facelift_roofrails	108028	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	MEDIUM	改款后带纵向车顶杆外廓。	READY
105916_low	105916	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
105916_roofrails	105916	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
145964	145964	Sedan	C4 I Sedan		4	EU-CITROEN-C4-I-SEDAN-4D-01	HIGH		READY
145965	145965	Sedan	C4 I Sedan		4	EU-CITROEN-C4-I-SEDAN-4D-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C1-I-HATCHBACK-01	3435	1630	1465	Citroën C1 2010 official technical specification	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C1-UK.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	4157	1729	1480	Citroën C4 Cactus 2015 official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Citroen-C4-Cactus-UK.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	4157	1729	1530	Citroën C4 Cactus 2015 official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Citroen-C4-Cactus-UK.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	4169	1729	1480	Citroën C4 Cactus 2020 official range brochure	https://d1amhj1m505d5v.cloudfront.net/wp-content/uploads/sites/21/2020/02/citroen-c4-cactus-range-brochure-february-2020.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	4169	1729	1530	Citroën C4 Cactus 2020 official range brochure	https://d1amhj1m505d5v.cloudfront.net/wp-content/uploads/sites/21/2020/02/citroen-c4-cactus-range-brochure-february-2020.pdf
EU-CITROEN-C4-I-SEDAN-4D-01	4770	1770	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1218635/citroen_c4_sedan_2_0i_16v_sx.html
```

## 5. 下一步优先处理

1. 闭合 C4 Grand Picasso II 十个 Ktype，按改款前后及无车顶纵杆/带车顶纵杆外廓批量关联。
2. 核对 C25 2.5 D 4X4 Bus 的轴距、车长及车顶分支。
3. 最后处理 C35 三个 Platform/Chassis Ktype 的轴距和驾驶室外廓分支。

推进信号：CONTINUE

[1]: https://citroen.manymanuals.com/cars/c4-cactus/brochure-34076/49?utm_source=chatgpt.com "CITROEN C4 Cactus Brochure download pdf (Page 49)"
[2]: https://www.automobile-catalog.com/car/2008/1218635/citroen_c4_sedan_2_0i_16v_sx.html?utm_source=chatgpt.com "2008 Citroen C4 Sedan 2.0i 16V SX (man. 5)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* C4 Grand Picasso II 改款前外廓闭合为 `4597 × 1826 × 1644 mm`；改款后前部造型使车长增至 `4602 mm`，宽度仍为不含后视镜的 `1826 mm`，最大标准高度仍为 `1644 mm`。([ManualMachine][1])
* `1.2 THP 130`、`1.6 BlueHDi 120`、`1.6 HDI / BlueHDi 115`、`1.6 THP 165` 和 `2.0 BlueHDi 150` 覆盖或延续至 2016 年改款后的车型，已拆分 `prefl` 与 `facelift` 外廓。改款车型自 2016 年 9 月起在英国上市。([Stellantis Media][2])
* `1.6 BlueHDi 100` 明确于 2016 年改款前结束，仅关联改款前尺寸组。
* 本轮覆盖剩余 10 个 C4 Grand Picasso II Ktype；当前仅剩 C25 4×4 Bus 与三个 C35 Platform/Chassis Ktype。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 映射行：134
* READY 覆盖输入 Ktype：96
* PENDING 输入 Ktype：4
* 已确认尺寸组：31
* 本轮新增 READY 映射：15 行
* 本轮覆盖新增输入 Ktype：10
* 本轮首次创建尺寸组：2 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
112367_prefl	112367	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
112367_facelift	112367	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
114209	114209	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
108851_prefl	108851	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
108851_facelift	108851	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53293_prefl	53293	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
53293_facelift	53293	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53221	53221	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
53217	53217	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
108158_prefl	108158	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
108158_facelift	108158	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53216	53216	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
117923	117923	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	MEDIUM		READY
53296_prefl	53296	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
53296_facelift	53296	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	4597	1826	1644	Citroën C4 Picasso and Grand C4 Picasso official brochure	https://manualmachine.com/citroen/c4picasso/1971866-brochure/
EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	4602	1826	1644	Citroën New Grand C4 Picasso official brochure	https://web-assets.cdn.dealersolutions.com.au/modular.multisite.dealer.solutions/wp-content/uploads/2018/05/18114317/citroen-grand-c4-picasso-brochure-sep17.pdf
```

## 5. 下一步优先处理

1. 核对 Ktype `6591` 的 C25 2.5 D 4×4 Bus 轴距、车长和车顶外廓分支。
2. 一次性核对 Ktype `18874`、`18875`、`18876` 的 C35 Platform/Chassis 驾驶室外廓及是否存在必须拆分的轴距分支。
3. PENDING 清零后立即执行一次机械闭合检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://manualmachine.com/citroen/c4picasso/1971866-brochure/?utm_source=chatgpt.com "CITROEN C4 Picasso, Grand C4 Picasso Brochure - ManualMachine.com"
[2]: https://www.media.stellantis.com/uk-en/citroen/press/uk-pricing-and-specification-announced-for-new-citroen-c4-picasso-new-grand-c4-picasso?utm_source=chatgpt.com "UK PRICING AND SPECIFICATION ANNOUNCED FOR NEW CITROËN C4 PICASSO & NEW GRAND C4 PICASSO | Citroën | Stellantis Media"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3501-3600_ktype_dimension_mapping_final.tsv
- left18448_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后 4 个 PENDING 已闭合：C25 4×4 Bus 关联标准四驱 Combi/Bus 外廓；C35 三个 Ktype 均按 SWB、LWB 两种平台驾驶室外廓拆分。([车辆信息][1])([车辆信息][1])定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，无孤立尺寸组，三维和来源均非空。
* 两个指定文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：141
* PENDING 映射：0
* 已确认尺寸组：34
* 全部输入 Ktype 已覆盖。
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15053	15053	MPV	Berlingo I	M49	5	EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	复用既有M49后期MPV尺寸组。	READY
15055	15055	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
14131	14131	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
15056	15056	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
15057	15057	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
14132_prefl	14132	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
14132_facelift	14132	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
15058	15058	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
123830_prefl	123830	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
123830_facelift	123830	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
123831	123831	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH		READY
15060_prefl	15060	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款前分支拆分。	READY
15060_facelift	15060	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	HIGH	跨越1986年外廓改款，按改款后分支拆分。	READY
113288_prefl	113288	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1986年外廓改款，拆分改款前分支。	READY
113288_facelift	113288	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1986年外廓改款，拆分改款后分支。	READY
18584_3dr	18584	Hatchback	C1 I		3	EU-CITROEN-C1-I-HATCHBACK-01	HIGH	同一Ktype覆盖三门车身。	READY
18584_5dr	18584	Hatchback	C1 I		5	EU-CITROEN-C1-I-HATCHBACK-01	HIGH	同一Ktype覆盖五门车身。	READY
105909_3dr	105909	Hatchback	C1 II		3	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖三门车身。	READY
105909_5dr	105909	Hatchback	C1 II		5	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖五门车身。	READY
105910_3dr	105910	Hatchback	C1 II		3	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖三门车身。	READY
105910_5dr	105910	Hatchback	C1 II		5	EU-CITROEN-C1-II-HATCHBACK-01	MEDIUM	同一发动机Ktype覆盖五门车身。	READY
18585_3dr	18585	Hatchback	C1 I		3	EU-CITROEN-C1-I-HATCHBACK-01	MEDIUM	同一Ktype覆盖三门车身。	READY
18585_5dr	18585	Hatchback	C1 I		5	EU-CITROEN-C1-I-HATCHBACK-01	MEDIUM	同一Ktype覆盖五门车身。	READY
6590	6590	Van	C15 I	VD		EU-CITROEN-C15-I-VAN-01	MEDIUM	输入车身形式混合Van/MPV；按标准C15封闭式车身。	READY
18017	18017	Van	C15 I	VD		EU-CITROEN-C15-I-VAN-01	MEDIUM	输入车身形式混合Van/MPV；按标准C15封闭式车身。	READY
17330	17330	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17331	17331	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17332	17332	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
17333	17333	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
18613	18613	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH		READY
6591	6591	MPV	C25 I		4	EU-CITROEN-C25-I-DANGEL-4X4-BUS-01	MEDIUM	四驱Combi/Bus标准车身外廓。	READY
128136	128136	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128184	128184	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128135	128135	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128133	128133	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128185	128185	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
128134	128134	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	HIGH		READY
801816	801816	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800210	800210	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800209	800209	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
800208	800208	SUV	C3 Aircross II		5	EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	HIGH		READY
17892_prefl	17892	Hatchback	C3 I Phase I		5	EU-CITROEN-C3-I-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2005年改款，按改款前分支拆分。	READY
17892_facelift	17892	Hatchback	C3 I Phase II		5	EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2005年改款，按改款后分支拆分。	READY
19017	19017	Hatchback	C3 I Phase II		5	EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58663_prefl	58663	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58663_facelift	58663	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
12292_prefl	12292	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
12292_facelift	12292	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
109326	109326	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58664_prefl	58664	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58664_facelift	58664	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
53297	53297	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
117928_prefl	117928	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
117928_facelift	117928	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
113665	113665	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
113666	113666	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58666_prefl	58666	Hatchback	C3 II Phase I		5	EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款前外廓。	READY
58666_facelift	58666	Hatchback	C3 II Phase II		5	EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	HIGH	跨越2013年改款，拆分改款后外廓。	READY
121982	121982	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
146803	146803	Van	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH	封闭货运版沿用五门车身外廓。	READY
801160	801160	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
158589	158589	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
157568	157568	Hatchback	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	HIGH		READY
801490	801490	Van	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	MEDIUM	五门封闭货运衍生车身。	READY
801291	801291	Van	C3 IV		5	EU-CITROEN-C3-IV-HATCHBACK-5D-01	MEDIUM	五门封闭货运衍生车身。	READY
801393	801393	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
801399	801399	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
802343	802343	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-5D-01	HIGH		READY
112336	112336	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
56263	56263	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
112338	112338	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
58588	58588	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
33783	33783	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-5D-01	HIGH		READY
17277	17277	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
17276	17276	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
18085	18085	Convertible	C3 Pluriel I		2	EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	HIGH	固定双门可转换车身。	READY
18874_swb	18874	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-SWB-01	MEDIUM	平台/底盘驾驶室短轴分支。	READY
18874_lwb	18874	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-LWB-01	MEDIUM	平台/底盘驾驶室长轴分支。	READY
18875_swb	18875	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-SWB-01	MEDIUM	平台/底盘驾驶室短轴分支。	READY
18875_lwb	18875	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-LWB-01	MEDIUM	平台/底盘驾驶室长轴分支。	READY
18876_swb	18876	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-SWB-01	MEDIUM	平台/底盘驾驶室短轴分支。	READY
18876_lwb	18876	Pickup	C35 I		2	EU-CITROEN-C35-I-PLATFORM-CAB-LWB-01	MEDIUM	平台/底盘驾驶室长轴分支。	READY
18339_prefl	18339	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18339_facelift	18339	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18340_prefl	18340	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18340_facelift	18340	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18343_prefl	18343	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18343_facelift	18343	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18344_prefl	18344	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18344_facelift	18344	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18341	18341	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH		READY
18342_prefl	18342	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH	跨越2008年外廓改款，拆分改款前分支。	READY
18342_facelift	18342	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	HIGH	跨越2008年外廓改款，拆分改款后分支。	READY
18345_prefl	18345	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18345_facelift	18345	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
100901	100901	Coupe	C4 I Phase I	LA	3	EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	HIGH		READY
55133	55133	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55134	55134	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55135	55135	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55136	55136	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
55137	55137	SUV	C4 Aircross I		5	EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	HIGH		READY
108027_prefl_low	108027	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	改款前无纵向车顶杆外廓。	READY
108027_prefl_roofrails	108027	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	改款前带纵向车顶杆外廓。	READY
108027_facelift_low	108027	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	MEDIUM	改款后无纵向车顶杆外廓。	READY
108027_facelift_roofrails	108027	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	MEDIUM	改款后带纵向车顶杆外廓。	READY
108026_low	108026	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
108026_roofrails	108026	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
105914_low	105914	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
105914_roofrails	105914	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
108028_prefl_low	108028	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	改款前无纵向车顶杆外廓。	READY
108028_prefl_roofrails	108028	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	改款前带纵向车顶杆外廓。	READY
108028_facelift_low	108028	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	MEDIUM	改款后无纵向车顶杆外廓。	READY
108028_facelift_roofrails	108028	Hatchback	C4 Cactus I Phase II		5	EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	MEDIUM	改款后带纵向车顶杆外廓。	READY
105916_low	105916	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	MEDIUM	无纵向车顶杆外廓。	READY
105916_roofrails	105916	Hatchback	C4 Cactus I Phase I		5	EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	MEDIUM	带纵向车顶杆外廓。	READY
112367_prefl	112367	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
112367_facelift	112367	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
114209	114209	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
108851_prefl	108851	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
108851_facelift	108851	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53293_prefl	53293	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
53293_facelift	53293	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53221	53221	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
53217	53217	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
108158_prefl	108158	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
108158_facelift	108158	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
53216	53216	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH		READY
117923	117923	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	MEDIUM		READY
53296_prefl	53296	MPV	C4 Grand Picasso II Phase I		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	HIGH	跨越2016年外廓改款，改款前分支。	READY
53296_facelift	53296	MPV	C4 Grand Picasso II Phase II		5	EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	HIGH	跨越2016年外廓改款，改款后分支。	READY
18332_prefl	18332	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18332_facelift	18332	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18333_prefl	18333	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18333_facelift	18333	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18336_prefl	18336	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18336_facelift	18336	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
18337_prefl	18337	Hatchback	C4 I Phase I	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	MEDIUM	跨越2008年外廓改款，按改款前分支拆分。	READY
18337_facelift	18337	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	MEDIUM	跨越2008年外廓改款，按改款后分支拆分。	READY
145964	145964	Sedan	C4 I Sedan		4	EU-CITROEN-C4-I-SEDAN-4D-01	HIGH		READY
145965	145965	Sedan	C4 I Sedan		4	EU-CITROEN-C4-I-SEDAN-4D-01	HIGH		READY
145966	145966	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_3501-3600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-I-M49-LATE-01	4108	1719	1802	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/547835/citroen_berlingo_multispace_1_6i_16v.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1361	Auto-Data; Citroënët	https://www.auto-data.net/en/citroen-bx-i-phase-ii-1987-19-tzi-109hp-cat-15254;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-II-WAGON-5D-01	4399	1682	1431	Auto-Data; Citroënët	https://www.auto-data.net/en/citroen-bx-i-break-phase-ii-1987-14-e-72hp-15266;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-I-WAGON-5D-01	4399	1660	1431	Automobile-Catalog; Citroënët	https://www.automobile-catalog.com/car/1985/54530/citroen_bx_break_19_rd.html;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1650	1365	Automobile-Catalog; Citroënët	https://www.automobile-catalog.com/car/1985/2029220/citroen_bx_19_d.html;https://www.citroenet.org.uk/passenger-cars/psa/bx/bx-16.html
EU-CITROEN-C1-I-HATCHBACK-01	3435	1630	1465	Citroën C1 2010 official technical specification	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C1-UK.pdf
EU-CITROEN-C1-II-HATCHBACK-01	3465	1615	1460	Citroën C1 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/11/Citroen-C1-2014-UK.pdf
EU-CITROEN-C15-I-VAN-01	3995	1636	1801	Citroën Vans 2005 technical specifications	https://xr793.com/wp-content/uploads/2022/09/2005-Citroen-Van-Tech-Specs-UK.pdf
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1477	Citroën C2 2009 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Citroen-C2-2009-UK.pdf
EU-CITROEN-C25-I-DANGEL-4X4-BUS-01	4765	1965	2100	Citroën C25 workshop manual; Autocasión C25 1400 4x4 vehicle specification	https://ckc.dk/pubs/MAN008900-C25.pdf;https://www.autocasion.com/marcas/citroen/c25-industrial/c-25-furgon-1400-4x4-4-puertas-15686
EU-CITROEN-C3-AIRCROSS-I-SUV-5D-01	4155	1765	1637	Citroën UK C3 Aircross official price and specification guide	https://www.citroen.co.uk/content/dam/citroen/uk/view-price---spec-guide/C3_Aircross_Price_Specification_guide.pdf
EU-CITROEN-C3-AIRCROSS-II-SUV-5D-01	4395	1795	1660	Citroën UK New C3 Aircross official price and specification guide; Automobile Dimension	https://www.media.stellantis.com/uploads/uk/attachment/5583/newc3aircrosspricespecificationguide-67a0b03e58700.pdf;https://www.automobiledimension.com/model/citroen/c3-aircross
EU-CITROEN-C3-I-PHASE-I-HATCHBACK-5D-01	3850	1667	1529	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/548285/citroen_c3_1_4i_16v_sx.html
EU-CITROEN-C3-I-PHASE-II-HATCHBACK-5D-01	3860	1667	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/548615/citroen_c3_1_4i_16v_exclusive_senso_drive.html
EU-CITROEN-C3-II-PHASE-I-HATCHBACK-5D-01	3941	1728	1524	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1213280/citroen_c3_1_4i_sx.html
EU-CITROEN-C3-II-PHASE-II-HATCHBACK-5D-01	3941	1728	1538	Auto-Data	https://www.auto-data.net/en/citroen-c3-ii-phase-ii-2013-1.0-puretech-68hp-27457
EU-CITROEN-C3-III-HATCHBACK-5D-01	3996	1749	1474	Citroën New Zealand C3 official specifications	https://www.citroen.co.nz/content/dam/citroen/new_zealand/documents/2024/citroen-c3-prices-and-specifications-01-2024-CZQ-engine.pdf
EU-CITROEN-C3-IV-HATCHBACK-5D-01	4015	1755	1577	Citroën UK New C3 official price and specification guide; Citroën Türkiye New ë-C3 digital catalogue	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/car-range/New-C3-price-and-specification-guide.pdf;https://talep.citroen.com.tr/dijital-katalog/yeni-ec3
EU-CITROEN-C3-PICASSO-I-MPV-5D-01	4078	1766	1631	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2140025/citroen_c3_picasso_bluehdi_100_exclusive.html
EU-CITROEN-C3-PLURIEL-I-CONVERTIBLE-2D-01	3934	1700	1563	Citroën C3 Pluriel product and technical brochure	https://c3pluriel.fr/wp-content/uploads/2024/05/Brochure-c3-pluriel-2006-cote-azur-GB.pdf
EU-CITROEN-C35-I-PLATFORM-CAB-SWB-01	4948	1990	2370	Citroën C35 workshop manual; Citroën Range Vans 1979 official brochure	https://ckc.dk/pubs/MAN008900-C35.pdf;https://autocatalogarchive.com/wp-content/uploads/2023/09/Citroen-Range-Vans-1979-FR.pdf
EU-CITROEN-C35-I-PLATFORM-CAB-LWB-01	5948	1990	2370	Citroën C35 workshop manual; Citroën Range Vans 1979 official brochure	https://ckc.dk/pubs/MAN008900-C35.pdf;https://autocatalogarchive.com/wp-content/uploads/2023/09/Citroen-Range-Vans-1979-FR.pdf
EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-I-01	4273	1769	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/551405/citroen_c4_coupe_1_6i_16v_vtr.html
EU-CITROEN-C4-I-LA-COUPE-3D-PHASE-II-01	4288	1769	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1214945/citroen_c4_coupe_1_4_16v_vtr.html
EU-CITROEN-C4-AIRCROSS-I-SUV-5D-01	4341	1800	1625	ADAC vehicle catalogue	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/citroen/c4-aircross/1generation/232295/
EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-LOW-01	4157	1729	1480	Citroën C4 Cactus 2015 official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Citroen-C4-Cactus-UK.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-I-HATCHBACK-ROOFRAILS-01	4157	1729	1530	Citroën C4 Cactus 2015 official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Citroen-C4-Cactus-UK.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-LOW-01	4169	1729	1480	Citroën C4 Cactus 2020 official range brochure	https://d1amhj1m505d5v.cloudfront.net/wp-content/uploads/sites/21/2020/02/citroen-c4-cactus-range-brochure-february-2020.pdf
EU-CITROEN-C4-CACTUS-I-PHASE-II-HATCHBACK-ROOFRAILS-01	4169	1729	1530	Citroën C4 Cactus 2020 official range brochure	https://d1amhj1m505d5v.cloudfront.net/wp-content/uploads/sites/21/2020/02/citroen-c4-cactus-range-brochure-february-2020.pdf
EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-I-MPV-5D-01	4597	1826	1644	Citroën C4 Picasso and Grand C4 Picasso official brochure	https://manualmachine.com/citroen/c4picasso/1971866-brochure/
EU-CITROEN-C4-GRAND-PICASSO-II-PHASE-II-MPV-5D-01	4602	1826	1644	Citroën New Grand C4 Picasso official brochure	https://web-assets.cdn.dealersolutions.com.au/modular.multisite.dealer.solutions/wp-content/uploads/2018/05/18114317/citroen-grand-c4-picasso-brochure-sep17.pdf
EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-I-01	4260	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/551210/citroen_c4_2_0i_16v_style.html
EU-CITROEN-C4-I-LC-HATCHBACK-5D-PHASE-II-01	4275	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1214780/citroen_c4_hdi_90_fap_comfort.html
EU-CITROEN-C4-I-SEDAN-4D-01	4770	1770	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1218635/citroen_c4_sedan_2_0i_16v_sx.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_3501-3600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.car.info/en-se/citroen/c25/c25-combi-1400-120196321 "https://www.car.info/en-se/citroen/c25/c25-combi-1400-120196321"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4197 行）
- 累计尺寸组：dimension_groups_final.tsv（1227 行）

