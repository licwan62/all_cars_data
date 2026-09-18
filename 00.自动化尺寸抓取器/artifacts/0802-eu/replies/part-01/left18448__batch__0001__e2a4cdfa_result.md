# 任务：left18448 第 1-100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0001__e2a4cdfa


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1-100 行

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
left18448 第 1-100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	May 2010	-	58731
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	May 2016	-	120080
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	May 2016	-	120081
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	Jun 2016	-	121446
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	Jun 2010	-	59224
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	May 2008	-	59698
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	May 2016	-	121235
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	May 2016	-	122082
Abarth	500e	Scorpionissima	Schrägheck	Frontantrieb	Elektro	Feb 2023	-	152402
Abarth	500e	Scorpionissima	Cabriolet	Frontantrieb	Elektro	Feb 2023	-	152403
Abarth	600e	Scorpionissima	SUV	Frontantrieb	Elektro	Oct 2024	-	160058
Abarth	600e	Turismo	SUV	Frontantrieb	Elektro	Oct 2024	-	160053
Abarth	Punto	1.4 Supersport	Schrägheck	Frontantrieb	Benzin	Mar 2012	-	56931
Abarth	Ritmo	125 TC 2.0	Schrägheck	Frontantrieb	Benzin	Nov 1981	Dec 1987	14518
AC	428	7	Cabriolet	Heckantrieb	Benzin	Jan 1965	Dec 1974	12424
AC	Ace	4.6	Cabriolet	Heckantrieb	Benzin	Oct 1998	-	12428
AC	Ace	4.9	Cabriolet	Heckantrieb	Benzin	Jan 1995	Oct 1998	12426
AC	Ace	4.9	Cabriolet	Heckantrieb	Benzin	Oct 1998	-	12430
AC	Ace	4.9 Super Charger	Cabriolet	Heckantrieb	Benzin	Oct 1998	-	12431
AC	Aceca	4.6	Coupe	Heckantrieb	Benzin	Oct 1998	Dec 2001	12434
AC	Aceca	4.9	Coupe	Heckantrieb	Benzin	Sep 1993	Dec 1997	12436
AC	Aceca	4.9 Super Charger	Coupe	Heckantrieb	Benzin	Oct 1998	Dec 2001	12437
AC	Cobra iv	4.9	Cabriolet	Heckantrieb	Benzin	Jan 1990	Oct 1997	12439
AC	Cobra iv	4.9	Cabriolet	Heckantrieb	Benzin	Jan 1990	Oct 1997	12442
AC	Cobra iv	5.8	Cabriolet	Heckantrieb	Benzin	Jan 1990	Oct 1997	12443
AC	Cobra iv	4.9 Super Charger	Cabriolet	Heckantrieb	Benzin	Oct 1997	-	12440
Addax	Mt	Mt10 Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2018	-	154955
Addax	Mt	Mt15 Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2018	-	154956
Addax	Mtn	Mt15n Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2020	-	154957
Addax	Mtn	Mt8n Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2023	-	154960
Addax	Mtx	Mt15x Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2023	-	154958
Aeolus	Yixuan	1.5	Stufenheck	Frontantrieb	Benzin	Aug 2022	-	149025
Aion	Hyptec ht	EV	SUV	Heckantrieb	Elektro	Dec 2025	-	163182
Aion	V	EV	SUV	Frontantrieb	Elektro	Sep 2025	-	163649
Aiways	U6	EV	SUV	Frontantrieb	Elektro	Oct 2022	-	150630
Aixam	City	0.4	Schrägheck	Frontantrieb	Diesel	Jan 2012	Dec 2016	100175
Aixam	City	Electric	Schrägheck	Frontantrieb	Elektro	Jan 2012	Dec 2016	106507
Aixam	Crossline	0.5	Schrägheck	Frontantrieb	Benzin	Jan 2012	Dec 2016	12773
Aixam	Crossline	0.6	Schrägheck	Frontantrieb	Diesel	Jan 2012	Dec 2016	127221
Aixam	Crossover	0.5 GTR	Schrägheck	Frontantrieb	Benzin	Jan 2012	Dec 2016	118699
Aixam	D-Truck	0.4	Kasten	Frontantrieb	Diesel	May 2014	-	106509
Aixam	D-Truck	0.4	Pick-up	Frontantrieb	Diesel	Jan 2012	-	106510
Aixam	D-Truck	0.4	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2014	-	106511
Aixam	D-Truck	0.6	Kasten	Frontantrieb	Diesel	May 2015	-	118039
Aixam	D-Truck	0.6	Pick-up	Frontantrieb	Diesel	May 2015	-	118040
Aixam	D-Truck	0.6	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2015	-	118041
Aixam	D-Truck	Electric	Kasten	Frontantrieb	Elektro	Oct 2024	-	801824
Aixam	D-Truck	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Oct 2024	-	801825
Aixam	Mega	E-scouty	Schrägheck	Frontantrieb	Elektro	May 2024	-	163905
Aixam	Minauto	Electric	Schrägheck	Frontantrieb	Elektro	Oct 2024	-	801819
Aixam	Roadline	0.6	Schrägheck	Frontantrieb	Diesel	Sep 2009	Jul 2012	112213
Aixam	Scouty	0.4	Cabriolet	Frontantrieb	Diesel	Apr 2007	-	100181
Alfa Romeo	33	1.3	Schrägheck	Frontantrieb	Benzin	Jun 1983	Jun 1990	127183
Alfa Romeo	33	1.5	Schrägheck	Frontantrieb	Benzin	Jan 1990	Apr 1993	17422
Alfa Romeo	33	1.7 16V 4X4	Kombi	Allrad	Benzin	Jul 1990	Sep 1994	125927
Alfa Romeo	145	1.6 16V T.s.	Schrägheck	Frontantrieb	Benzin	Sep 1997	Dec 2000	54968
Alfa Romeo	145	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Feb 1999	Jan 2001	11899
Alfa Romeo	146	1.6 16V T.s.	Schrägheck	Frontantrieb	Benzin	Sep 1997	Dec 2000	54967
Alfa Romeo	146	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Feb 1999	Jan 2001	12242
Alfa Romeo	147	1.6 16V T.spark	Schrägheck	Frontantrieb	Benzin	Jan 2001	Mar 2010	15529
Alfa Romeo	147	1.6 16V T.spark ECO	Schrägheck	Frontantrieb	Benzin	Jan 2001	Mar 2010	15579
Alfa Romeo	147	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Apr 2001	Mar 2010	16441
Alfa Romeo	147	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Jun 2003	Mar 2010	17436
Alfa Romeo	147	1.9 JTD 16V	Schrägheck	Frontantrieb	Diesel	Nov 2002	Mar 2010	17161
Alfa Romeo	147	1.9 Jtdm 16V	Schrägheck	Frontantrieb	Diesel	Sep 2004	Mar 2010	18933
Alfa Romeo	147	1.9 Jtdm 8V	Schrägheck	Frontantrieb	Diesel	Jul 2005	Mar 2010	18932
Alfa Romeo	147	2.0 16V T.spark	Schrägheck	Frontantrieb	Benzin	Jan 2001	Mar 2010	15528
Alfa Romeo	147	3.2 GTA	Schrägheck	Frontantrieb	Benzin	Feb 2003	Mar 2010	17121
Alfa Romeo	155	1.6 16V T.s.	Stufenheck	Frontantrieb	Benzin	May 1996	Dec 1997	5749
Alfa Romeo	155	1.7 T.s. 16V	Stufenheck	Frontantrieb	Benzin	May 1996	Dec 1997	5748
Alfa Romeo	156	1.6 16V T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2005	8808
Alfa Romeo	156	1.6 16V T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2005	54965
Alfa Romeo	156	1.6 16V T.spark	Kombi	Frontantrieb	Benzin	Jan 2000	Sep 2005	54966
Alfa Romeo	156	1.6 16V T.spark.	Kombi	Frontantrieb	Benzin	May 2000	May 2006	14784
Alfa Romeo	156	1.8 16V T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1997	Oct 2000	8809
Alfa Romeo	156	1.8 16V T.spark	Kombi	Frontantrieb	Benzin	May 2000	Oct 2000	14785
Alfa Romeo	156	1.8 16V T.spark	Kombi	Frontantrieb	Benzin	Feb 1997	May 2006	15616
Alfa Romeo	156	1.8 16V T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2005	15617
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	Sep 1997	Oct 2000	8812
Alfa Romeo	156	1.9 JTD	Kombi	Frontantrieb	Diesel	May 2000	Oct 2000	14788
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2000	May 2001	15688
Alfa Romeo	156	1.9 JTD	Kombi	Frontantrieb	Diesel	Oct 2000	May 2001	15692
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	May 2001	Sep 2005	16584
Alfa Romeo	156	1.9 JTD	Kombi	Frontantrieb	Diesel	May 2001	May 2006	16586
Alfa Romeo	156	1.9 JTD 16V	Stufenheck	Frontantrieb	Diesel	Nov 2002	Sep 2005	17162
Alfa Romeo	156	1.9 JTD 16V	Kombi	Frontantrieb	Diesel	Nov 2002	May 2006	17163
Alfa Romeo	156	1.9 JTD 16V Q4	Kombi	Allrad	Diesel	Jul 2004	May 2006	18205
Alfa Romeo	156	2.0 16V T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1997	Jun 2002	8810
Alfa Romeo	156	2.0 16V T.spark	Kombi	Frontantrieb	Benzin	May 2000	Jun 2002	14786
Alfa Romeo	156	2.0 16V T.spark	Kombi	Frontantrieb	Benzin	Oct 2000	Mar 2002	15618
Alfa Romeo	156	2.0 16V T.spark	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2002	15619
Alfa Romeo	156	2.0 JTS	Stufenheck	Frontantrieb	Benzin	Mar 2002	Sep 2005	16617
Alfa Romeo	156	2.0 JTS	Kombi	Frontantrieb	Benzin	Mar 2002	May 2006	16619
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Sep 1997	Sep 2003	8813
Alfa Romeo	156	2.4 JTD	Kombi	Frontantrieb	Diesel	May 2000	Sep 2003	14789
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2000	Sep 2005	15690
Alfa Romeo	156	2.4 JTD	Kombi	Frontantrieb	Diesel	Oct 2000	May 2006	15693
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Mar 2002	Sep 2005	16618
Alfa Romeo	156	2.4 JTD	Kombi	Frontantrieb	Diesel	Mar 2002	May 2006	16620
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2003	Sep 2005	17622


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓闭合首批 **12 个 Abarth Ktype**，共建立 **7 个尺寸组**。
* Abarth 500/500C 312 系列区分为 2016 年前掀背、软顶以及 2016 facelift 后的 595、595C；官方 2016 技术规格确认 595 与 595C 均为 `3660 × 1627 × 1485 mm`。([Stellantis Media][1])
* 2016 年前 500 掀背采用 `3657 × 1627 × 1485 mm`；500C 软顶采用 `3657 × 1627 × 1488 mm`，宽度均为不含后视镜口径。([汽车目录][2])
* Abarth 500e 的 332 掀背和软顶分别建组，ADAC 对两种车身均给出 `3673 × 1682 × 1518 mm`。([ADAC][3])
* Abarth 600e Turismo 与 Scorpionissima 共用 365 五门 SUV 外廓；官方资料确认长度和高度，车身无镜宽度以规格数据库的 `1779 mm` 闭合。([Stellantis Media][4])
* Ktype `59698` 的目录生产起始时间早于 Abarth 500C 的公开上市时间，但车型目录仍指向 312 软顶物理车身，因此以 `MEDIUM` 置信度关联，未另建猜测尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：12
* 待处理/未闭合 Ktype：88
* 已确认尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58731	58731	Hatchback	500/595/695 (312)	312	3	EU-ABARTH-500-312-PREFL-HATCHBACK-01	HIGH	312 三门掀背，2016 年前外廓。	READY
120080	120080	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
120081	120081	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
121446	121446	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
59224	59224	Convertible	500C/595C/695C (312)	312	2	EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	HIGH	312 双门软顶，2016 年前外廓。	READY
59698	59698	Convertible	500C/595C/695C (312)	312	2	EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	MEDIUM	Ktype 目录指向 312 双门软顶；输入起始月早于车型公开上市。	READY
121235	121235	Convertible	595C (312)	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH	312 双门软顶，2016 facelift 外廓。	READY
122082	122082	Convertible	595C (312)	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH	312 双门软顶，2016 facelift 外廓。	READY
152402	152402	Hatchback	500e (332)	332	3	EU-ABARTH-500E-332-HATCHBACK-01	HIGH	332 三门纯电掀背。	READY
152403	152403	Convertible	500e (332)	332	2	EU-ABARTH-500E-332-CONVERTIBLE-01	HIGH	332 双门纯电软顶。	READY
160058	160058	SUV	600e (365)	365	5	EU-ABARTH-600E-365-SUV-01	HIGH	365 五门 SUV；Scorpionissima 与 Turismo 共用外廓。	READY
160053	160053	SUV	600e (365)	365	5	EU-ABARTH-600E-365-SUV-01	HIGH	365 五门 SUV；Turismo 与 Scorpionissima 共用外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ABARTH-500-312-PREFL-HATCHBACK-01	3657	1627	1485	Automobile-Catalog 2010 Abarth 500 specifications	https://www.automobile-catalog.com/car/2010/728645/abarth_500.html
EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	3660	1627	1485	New Abarth 595 official technical specifications	https://www.media.stellantis.com/uploads/em/2016/ABARTH/Schde_tecniche/160607_Abarth_595_Technical-Specs_ENG.pdf
EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	3657	1627	1488	Auto-Data Abarth 500C generation specifications	https://www.auto-data.net/en/abarth-500c-generation-8152
EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	3660	1627	1485	New Abarth 595 official technical specifications	https://www.media.stellantis.com/uploads/em/2016/ABARTH/Schde_tecniche/160607_Abarth_595_Technical-Specs_ENG.pdf
EU-ABARTH-500E-332-HATCHBACK-01	3673	1682	1518	ADAC Abarth 500e technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/abarth/500-595-695/2generation/328228/
EU-ABARTH-500E-332-CONVERTIBLE-01	3673	1682	1518	ADAC Abarth 500e Cabrio technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/abarth/500-595-695/2generation/328231/
EU-ABARTH-600E-365-SUV-01	4187	1779	1502	Abarth 600e official technical sheet; Automobile-Catalog Abarth 600e Scorpionissima specifications	https://www.media.stellantis.com/uploads/it/model-document/abarth600e_technicalsheet-6720bb5f92145.pdf;https://www.automobile-catalog.com/car/2024/3380030/abarth_600e_scorpionissima.html
```

## 下一步优先处理

1. 闭合 Abarth Punto 与 Ritmo，避免与普通 Fiat Punto、Ritmo 的发动机版本资料混淆。
2. 按共同车身优先处理 Alfa Romeo 147、156：先核对 147 是否需要按改款或门数拆组，再批量关联其余发动机 Ktype；156 分 Sedan、Sportwagon，并核对 Crosswagon/Q4 是否改变外廓。
3. 随后处理 Alfa Romeo 33、145、146、155。
4. AC、Addax 与 Aixam 等低资料覆盖车型按独立车身聚类处理，无法确认无镜宽度时保持 PENDING，不创建临时尺寸组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2016/ABARTH/Schde_tecniche/160607_Abarth_595_Technical-Specs_ENG.pdf "Microsoft Word - New Abarth 595_Technical Specs .docx"
[2]: https://www.automobile-catalog.com/car/2010/728645/abarth_500.html?utm_source=chatgpt.com "Detailed specs review of 2010 Abarth 500 model for Europe"
[3]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/abarth/500-595-695/2generation/328228/?utm_source=chatgpt.com "Abarth 500e (42 kWh) (ab 05/23): Technische Daten, Bilder, Preise | ADAC"
[4]: https://www.media.stellantis.com/uploads/it/model-document/abarth600e_technicalsheet-6720bb5f92145.pdf "Abarth 600e Technical sheet.xlsx"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 闭合 Abarth Punto Supersport、Alfa Romeo 145/146、155 与 33 Series II 共 **8 个 Ktype**。
* Alfa Romeo 145、146 的相关 Ktype 跨越 1999 年外观改款，已按改款前后不同三维拆分；JTD Ktype 仅关联改款后尺寸组。([汽车目录][1])
* Abarth Punto Supersport 采用三门 199 车身的无镜宽度规格；Alfa Romeo 155 与 33 Series II 分别闭合为 167 四门轿车和 907A 五门掀背车尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：20
* READY 映射行：22
* PENDING Ktype：80
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56931	56931	Hatchback	Punto (199)	199	3	EU-ABARTH-PUNTO-199-HATCHBACK-01	HIGH	199系列三门Supersport外廓。	READY
54968_prefl	54968	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-PREFL-HATCHBACK-01	HIGH	1999外观改款前的三门外廓。	READY
54968_facelift	54968	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	HIGH	1999外观改款后的三门外廓。	READY
11899	11899	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	HIGH	JTD对应1999改款后三门外廓。	READY
54967_prefl	54967	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-PREFL-HATCHBACK-01	HIGH	1999外观改款前的五门外廓。	READY
54967_facelift	54967	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	HIGH	1999外观改款后的五门外廓。	READY
12242	12242	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	HIGH	JTD对应1999改款后五门外廓。	READY
5749	5749	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-01	HIGH	167系列四门轿车外廓。	READY
5748	5748	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-01	HIGH	167系列四门轿车外廓。	READY
17422	17422	Hatchback	33 Series II	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH	907A第二系列五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ABARTH-PUNTO-199-HATCHBACK-01	4065	1726	1490	Automobile-Catalog 2014 Abarth Punto Supersport specifications	https://www.automobile-catalog.com/car/2014/1759490/abarth_punto_supersport.html
EU-ALFA-ROMEO-145-930-PREFL-HATCHBACK-01	4093	1712	1427	Automobile-Catalog 1997 Alfa Romeo 145 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1997/218135/alfa_romeo_145_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	4061	1712	1431	Automobile-Catalog 1999 Alfa Romeo 145 1.9 JTD specifications	https://www.automobile-catalog.com/car/1999/218225/alfa_romeo_145_1_9_jtd.html
EU-ALFA-ROMEO-146-930-PREFL-HATCHBACK-01	4257	1712	1425	Automobile-Catalog 1998 Alfa Romeo 146 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1998/218180/alfa_romeo_146_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	4235	1712	1425	Automobile-Catalog 1999 Alfa Romeo 146 1.9 JTD specifications	https://www.automobile-catalog.com/car/1999/218360/alfa_romeo_146_1_9_jtd.html
EU-ALFA-ROMEO-155-167-SEDAN-01	4443	1730	1425	Automobile-Catalog 1996 Alfa Romeo 155 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1996/217640/alfa_romeo_155_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Automobile-Catalog 1990 Alfa Romeo 33 1.5 specifications	https://www.automobile-catalog.com/car/1990/216740/alfa_romeo_33_1_5.html
```

## 下一步优先处理

1. 闭合 Alfa Romeo 147 的改款前、改款后及 GTA 宽体尺寸组，再批量关联全部 147 Ktype。
2. 处理 Alfa Romeo 156 Sedan、Sportwagon 与 Q4，按车身形式及改款边界聚类。
3. 补齐 Alfa Romeo 33 第一系列和 907B Sport Wagon 4×4。
4. 随后处理 AC、Addax、Aixam 等低复用车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1999/1761935/alfa_romeo_145_limited_500_1_9_jtd.html?utm_source=chatgpt.com "1999 Alfa Romeo 145 Limited 500 1.9 JTD (man. 5)"
[2]: https://www.automobile-catalog.com/car/2014/1759490/abarth_punto_supersport.html?utm_source=chatgpt.com "2014 Abarth Punto Supersport Specs Review (132 kW / 180 PS / 177 hp) (for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* 已闭合全部 **30 个 Alfa Romeo 156 Ktype**，新增 **46 条 READY 映射**。
* 按 2003 年外观改款、Sedan/Sportwagon 以及升高底盘 Q4，首次建立 5 个尺寸组；跨越改款时间的 Ktype 已拆分为 `prefl` 与 `facelift` 派生行。改款前 Sedan、Sportwagon 分别为 `4430×1745×1415` 和 `4430×1745×1420 mm`；改款后分别为 `4435×1743×1390` 和 `4441×1743×1390 mm`。([汽车目录][1])
* Ktype `18205` 对应升高底盘 Sportwagon Q4，独立采用 `4441×1743×1458 mm` 尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：50
* READY 映射行：68
* PENDING Ktype：50
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8808_prefl	8808	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
8808_facelift	8808	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
54965_prefl	54965	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
54965_facelift	54965	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
54966_prefl	54966	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
54966_facelift	54966	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
14784_prefl	14784	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
14784_facelift	14784	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8809	8809	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14785	14785	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15616_prefl	15616	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15616_facelift	15616	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
15617_prefl	15617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15617_facelift	15617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8812	8812	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14788	14788	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15688	15688	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
15692	15692	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
16584_prefl	16584	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16584_facelift	16584	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16586_prefl	16586	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16586_facelift	16586	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17162_prefl	17162	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
17162_facelift	17162	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17163_prefl	17163	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
17163_facelift	17163	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
18205	18205	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-Q4-WAGON-01	HIGH	Q4升高底盘五门旅行车外廓。	READY
8810	8810	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14786	14786	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15618	15618	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15619	15619	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
16617_prefl	16617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16617_facelift	16617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16619_prefl	16619	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16619_facelift	16619	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8813	8813	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	截至2003年9月的改款前四门轿车。	READY
14789	14789	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	截至2003年9月的改款前五门旅行车。	READY
15690_prefl	15690	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15690_facelift	15690	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
15693_prefl	15693	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15693_facelift	15693	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16618_prefl	16618	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16618_facelift	16618	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16620_prefl	16620	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16620_facelift	16620	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17622	17622	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	2003外观改款后四门轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	4430	1745	1415	Automobile-Catalog 1998 Alfa Romeo 156 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/1998/218735/alfa_romeo_156_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	4430	1745	1420	Automobile-Catalog 2000 Alfa Romeo 156 Sportwagon 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/2000/218855/alfa_romeo_156_sportwagon_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	4435	1743	1390	Automobile-Catalog 2005 Alfa Romeo 156 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/2005/220565/alfa_romeo_156_1_6_twin_spark_16v_impression_business__base.html
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon 2.4 JTD specifications	https://www.automobile-catalog.com/car/2004/220265/alfa_romeo_156_sportwagon_2_4_jtd_20v_distinctive_exclusive__lusso.html
EU-ALFA-ROMEO-156-932-Q4-WAGON-01	4441	1743	1458	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon Q4 specifications	https://www.automobile-catalog.com/car/2004/220610/alfa_romeo_156_sportwagon_q4.html
```

## 下一步优先处理

1. 闭合 Alfa Romeo 147 的普通改款前、普通改款后及 GTA 特殊外廓，并批量关联其 10 个 Ktype。
2. 补齐 Alfa Romeo 33 第一系列与 33 Sport Wagon 4×4。
3. 处理 Abarth Ritmo 后，按 AC、Addax、Aixam 车型聚类依次消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1998/218735/alfa_romeo_156_1_6_twin_spark_16v.html?utm_source=chatgpt.com "1998 Alfa Romeo 156 1.6 Twin Spark 16V (man. 5)"
[2]: https://www.automobile-catalog.com/car/2004/220610/alfa_romeo_156_sportwagon_q4.html?utm_source=chatgpt.com "2004 Alfa Romeo 156 Sportwagon Q4 (man. 6)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
## 更新点

* 闭合全部 **9 个 Alfa Romeo 147 Ktype**，新增 **31 条 READY 映射**。
* 普通车型按三门/五门及 2004 年改款前后拆分；两种门数复用同一时期尺寸组。官方资料确认改款前普通 1.6/JTD 外廓为 `4170 × 1729 × 1442 mm`，2.0 低车身为 `4170 × 1729 × 1421 mm`。([Stellantis Media][1])
* 2004 年末改款后外廓统一为 `4223 × 1729 × 1442 mm`，并继续提供三门和五门车身。([Stellantis Media][2])
* 147 GTA 因加宽翼子板、专用保险杠和降低车身独立建组。([Stellantis Media][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：59
* READY 映射行：99
* PENDING Ktype：41
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15529_3dr_prefl	15529	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
15529_5dr_prefl	15529	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
15529_3dr_facelift	15529	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15529_5dr_facelift	15529	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
15579_3dr_prefl	15579	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
15579_5dr_prefl	15579	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
15579_3dr_facelift	15579	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15579_5dr_facelift	15579	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
16441_3dr_prefl	16441	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
16441_5dr_prefl	16441	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
16441_3dr_facelift	16441	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
16441_5dr_facelift	16441	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17436_3dr_prefl	17436	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
17436_5dr_prefl	17436	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
17436_3dr_facelift	17436	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
17436_5dr_facelift	17436	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17161_3dr_prefl	17161	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
17161_5dr_prefl	17161	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
17161_3dr_facelift	17161	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
17161_5dr_facelift	17161	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
18933_3dr_prefl	18933	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	MEDIUM	起始月跨越改款切换期；保留改款前三门分支。	READY
18933_5dr_prefl	18933	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	MEDIUM	起始月跨越改款切换期；保留改款前五门分支。	READY
18933_3dr_facelift	18933	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
18933_5dr_facelift	18933	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
18932_3dr	18932	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
18932_5dr	18932	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
15528_3dr_prefl	15528	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	HIGH	改款前2.0低车身三门外廓。	READY
15528_5dr_prefl	15528	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	HIGH	改款前2.0低车身五门外廓。	READY
15528_3dr_facelift	15528	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15528_5dr_facelift	15528	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17121	17121	Hatchback	147 GTA (937)	937	3	EU-ALFA-ROMEO-147-GTA-937-HATCHBACK-01	HIGH	GTA三门宽体及降低车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	4170	1729	1421	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	4223	1729	1442	Alfa Romeo New 147 official technical specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
EU-ALFA-ROMEO-147-GTA-937-HATCHBACK-01	4213	1764	1412	Alfa Romeo 147 GTA official press information; Automobile-Catalog 2003 Alfa Romeo 147 GTA specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-romeo-147-gta-in-uk;https://www.automobile-catalog.com/car/2003/221360/alfa_romeo_147_gta.html
```

## 下一步优先处理

1. 闭合 Alfa Romeo 33 第一系列掀背和 907B Sport Wagon 4×4。
2. 处理 Abarth Ritmo 125 TC。
3. 按车型聚类处理 AC 428、Ace、Aceca 与 Cobra IV。
4. 随后集中处理 Addax 和 Aixam，优先确认不同货箱、厢式车及底盘车外廓。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147 "NEW PERFORMANCE DIESEL FOR ALFA 147 | Alfa Romeo | Stellantis Media"
[2]: https://www.media.stellantis.com/em-en/alfa-romeo/press/new-alfa-147?utm_source=chatgpt.com "New Alfa 147 | Alfa Romeo"
[3]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-romeo-147-gta-in-uk "ALFA ROMEO 147 GTA IN UK | Alfa Romeo | Stellantis Media"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
## 更新点

* 闭合 **10 个 Ktype**，新增 **11 条 READY 映射**和 **6 个尺寸组**。
* Alfa Romeo 33 Ktype `127183` 覆盖第一系列前后两种高度外廓，拆分为 `prefl` 与 `facelift`；33 Sport Wagon 4×4 使用 907B 五门旅行车外廓。([汽车目录][1])
* AC Ace 的相关发动机版本复用 `4420 × 1870 × 1300 mm` 外廓；Aceca III 使用独立的 `4660 × 1890 × 1340 mm` Coupé 外廓。([汽车目录][2])
* Abarth Ritmo 125 TC 已按三门第一系列外廓闭合。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：69
* READY 映射行：110
* PENDING Ktype：31
* 已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14518	14518	Hatchback	Ritmo I	138A	3	EU-ABARTH-RITMO-I-HATCHBACK-01	HIGH	125 TC三门第一系列外廓。	READY
12428	12428	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12426	12426	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12430	12430	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12431	12431	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	机械增压版本不改变外廓。	READY
12434	12434	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	HIGH	Aceca III双门Coupé外廓。	READY
12436	12436	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	MEDIUM	输入起始时间早于Aceca III公开车型期；目录车型指向同一Coupé外廓。	READY
12437	12437	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	HIGH	机械增压版本不改变外廓。	READY
127183_prefl	127183	Hatchback	33 Series I	905	5	EU-ALFA-ROMEO-33-905-PREFL-HATCHBACK-01	HIGH	第一系列早期五门外廓。	READY
127183_facelift	127183	Hatchback	33 Series I	905	5	EU-ALFA-ROMEO-33-905-FACELIFT-HATCHBACK-01	HIGH	第一系列后期增高五门外廓。	READY
125927	125927	Wagon	33 Series II Sport Wagon	907B	5	EU-ALFA-ROMEO-33-907B-4X4-WAGON-01	HIGH	907B五门四驱旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ABARTH-RITMO-I-HATCHBACK-01	3937	1687	1370	Automobile-Catalog 1981 Fiat Ritmo Abarth 125 TC specifications	https://www.automobile-catalog.com/car/1981/714170/fiat_ritmo_abarth_125_tc.html
EU-AC-ACE-III-CONVERTIBLE-01	4420	1870	1300	Automobile-Catalog AC Ace 4.9L and 4.6L specifications	https://www.automobile-catalog.com/car/1995/213185/ac_ace_4_9l_v-8.html;https://www.automobile-catalog.com/car/1998/213290/ac_ace_4_6l_v-8_32v.html
EU-AC-ACECA-III-COUPE-01	4660	1890	1340	Automobile-Catalog 1998 AC Aceca 4.6L specifications	https://www.automobile-catalog.com/car/1998/213305/ac_aceca_4_6l_v-8_32v.html
EU-ALFA-ROMEO-33-905-PREFL-HATCHBACK-01	4015	1612	1303	Automobile-Catalog 1983 Alfa Romeo 33 1.3 specifications	https://www.automobile-catalog.com/car/1983/214760/alfa_romeo_33_1_3.html
EU-ALFA-ROMEO-33-905-FACELIFT-HATCHBACK-01	4015	1612	1345	Automobile-Catalog 1987 Alfa Romeo 33 1.3 S specifications	https://www.automobile-catalog.com/car/1987/215000/alfa_romeo_33_1_3_s.html
EU-ALFA-ROMEO-33-907B-4X4-WAGON-01	4200	1614	1350	Auto-Data Alfa Romeo 33 Sport Wagon 1.7 16V 4x4 specifications	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.7-16v-129hp-4x4-1393
```

## 下一步优先处理

1. 闭合 AC 428 与跨越外廓更新期的 Cobra IV。
2. 集中处理 Addax MT、MTN、MTX 的平台及载货车身边界。
3. 闭合 Aeolus Yixuan、Aion Hyptec HT、Aion V 与 Aiways U6。
4. 最后按 City/Crossline、D-Truck 和新一代轻型车平台批量处理剩余 Aixam Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/214760/alfa_romeo_33_1_3.html?utm_source=chatgpt.com "1983 Alfa Romeo 33 1.3 Specs Review (55 kW / 75 PS / 74 ..."
[2]: https://www.automobile-catalog.com/car/1995/213185/ac_ace_4_9l_v-8.html?utm_source=chatgpt.com "1995 AC Ace 4.9L V-8 (man. 5) (model for Europe ) car ..."
[3]: https://www.automobile-catalog.com/car/1981/714170/fiat_ritmo_abarth_125_tc.html?utm_source=chatgpt.com "1981 Fiat Ritmo Abarth 125 TC (man. 5)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 续跑 ---
## 更新点

* 闭合剩余 **5 个 AC Ktype**。AC 428、Cobra IV 标准版、Lightweight、5.8 Competition 与后期 Superblower 按明确外廓分别建组；其中 Cobra IV 5.8 Competition 的无镜三维为 `4115 × 1735 × 1245 mm`，Superblower 为 `4200 × 1745 × 1200 mm`。([汽车目录][1])
* 闭合 Aeolus Yixuan、Hyptec HT、第二代 Aion V 与 Aiways U6 共 **4 个 Ktype**。Aion V 使用欧洲官方 `4605 × 1854 × 1686 mm` 规格；Hyptec HT 使用 GAC 官方 `4935 × 1920 × 1700 mm` 规格。([CarNewsChina.com][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：78
* READY 映射行：119
* PENDING Ktype：22
* 已确认尺寸组：38
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12424	12424	Convertible	428 Frua		2	EU-AC-428-FRUA-CONVERTIBLE-01	HIGH	Frua双门敞篷外廓。	READY
12439	12439	Convertible	Cobra IV	291F	2	EU-AC-COBRA-IV-291F-STANDARD-CONVERTIBLE-01	HIGH	184 kW标准Mk IV外廓。	READY
12442	12442	Convertible	Cobra IV Lightweight	291F	2	EU-AC-COBRA-IV-291F-LIGHTWEIGHT-CONVERTIBLE-01	HIGH	250 kW Lightweight双门外廓。	READY
12443	12443	Convertible	Cobra IV Competition	291F	2	EU-AC-COBRA-IV-291F-COMPETITION-CONVERTIBLE-01	MEDIUM	5.8 Competition外廓；目录生产期宽于已查证车型期。	READY
12440	12440	Convertible	Cobra IV Superblower	291N	2	EU-AC-COBRA-IV-291N-SUPERBLOWER-CONVERTIBLE-01	HIGH	291N机械增压后期外廓。	READY
149025	149025	Sedan	Yixuan I	D53	4	EU-AEOLUS-YIXUAN-I-MACH-SEDAN-01	HIGH	1.5自然吸气Mach Edition四门外廓。	READY
163182	163182	SUV	Hyptec HT		5	EU-AION-HYPTEC-HT-SUV-01	HIGH	Hyptec HT五门纯电SUV外廓。	READY
163649	163649	SUV	Aion V II		5	EU-AION-V-II-EU-SUV-01	HIGH	第二代欧洲规格五门纯电SUV。	READY
150630	150630	SUV	U6		5	EU-AIWAYS-U6-SUV-01	HIGH	U6五门纯电SUV Coupé外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AC-428-FRUA-CONVERTIBLE-01	4420	1702	1295	Automobile-Catalog 1966 AC 428 Frua Convertible specifications	https://www.automobile-catalog.com/car/1966/64805/ac_428_convertible.html
EU-AC-COBRA-IV-291F-STANDARD-CONVERTIBLE-01	4115	1735	1245	Automobile-Catalog 1990 AC Cobra Mk IV specifications	https://www.automobile-catalog.com/car/1990/212960/ac_cobra_mk_iv.html
EU-AC-COBRA-IV-291F-LIGHTWEIGHT-CONVERTIBLE-01	4155	1745	1230	Auto-Data AC Cobra Mk IV Lightweight specifications	https://www.auto-data.net/en/ac-cobra-mk-iv-4.9-i-v8-lightweight-340hp-10
EU-AC-COBRA-IV-291F-COMPETITION-CONVERTIBLE-01	4115	1735	1245	Automobile-Catalog 1990 AC Cobra Mk IV Competition 5.8L specifications	https://www.automobile-catalog.com/car/1990/213050/ac_cobra_mk_iv_competition_5_8l.html
EU-AC-COBRA-IV-291N-SUPERBLOWER-CONVERTIBLE-01	4200	1745	1200	Auto-Data AC Cobra Mk IV Superblower specifications	https://www.auto-data.net/en/ac-cobra-mk-iv-4.9-i-v8-superblower-326hp-11
EU-AEOLUS-YIXUAN-I-MACH-SEDAN-01	4670	1812	1490	CarNewsChina Aeolus Yixuan Mach Edition specifications	https://carnewschina.com/2022/10/29/dongfeng-aeolus-yixuan-mach-edition-launched-in-china-price-starts-at-8900-usd/
EU-AION-HYPTEC-HT-SUV-01	4935	1920	1700	GAC official HYPTEC HT specifications	https://www.gacgroup.com/en-hk/configuration/hyptec-ht/2024
EU-AION-V-II-EU-SUV-01	4605	1854	1686	GAC Europe official AION V specifications	https://www.gacgroup.com/en-eu/configuration/aion-v/2024
EU-AIWAYS-U6-SUV-01	4805	1880	1641	EV Database Aiways U6 specifications	https://ev-database.org/car/1766/Aiways-U6
```

## 下一步优先处理

1. 按 MT、MTN、MTX 平台及载货车身配置闭合 5 个 Addax Ktype。
2. 集中闭合 Aixam City、Crossline、Crossover、Roadline 与 Scouty。
3. 最后处理 Aixam D-Truck 各厢式、Pick-up、底盘车分支，以及 Mega E-scouty 和新款 Minauto。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1966/64805/ac_428_convertible.html?utm_source=chatgpt.com "1966 AC 428 Frua Convertible Specs Review (257 kW / 350 PS / 345 hp) (since mid-year 1966 for Europe )"
[2]: https://carnewschina.com/2022/10/29/dongfeng-aeolus-yixuan-mach-edition-launched-in-china-price-starts-at-8900-usd/?utm_source=chatgpt.com "Dongfeng Aeolus Yixuan Mach Edition Launched In ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 续跑 ---
## 更新点

* 闭合 Aixam City、Crossline、Crossover 和 Mega E-Scouty 共 **6 个 Ktype**，首次建立 **4 个尺寸组**。
* City 的柴油与纯电版本复用同一外廓；Crossline 的不同发动机版本复用同一外廓。Crossover GTR 按对应 Crossover 车身闭合。维修及车主资料分别确认三组无镜外廓尺寸。([manualzz.com][1])
* Mega E-Scouty 采用官方技术表所列 `2650 × 1500 × 1480 mm` 外廓。([Aixam][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：84
* READY 映射行：125
* PENDING Ktype：16
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100175	100175	Hatchback	City Impulsion		3	EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	HIGH	Impulsion系列三门城市车外廓。	READY
106507	106507	Hatchback	City Impulsion		3	EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	HIGH	纯电版本复用同一三门外廓。	READY
12773	12773	Hatchback	Crossline Impulsion		3	EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	HIGH	Impulsion系列三门Crossline外廓。	READY
127221	127221	Hatchback	Crossline Impulsion		3	EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	HIGH	发动机版本不改变物理外廓。	READY
118699	118699	Hatchback	Crossover Impulsion		3	EU-AIXAM-CROSSOVER-IMPULSION-HATCHBACK-01	HIGH	GTR版本对应Crossover三门外廓。	READY
163905	163905	Hatchback	E-Scouty		3	EU-MEGA-E-SCOUTY-HATCHBACK-01	HIGH	三门纯电轻型车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	2720	1500	1470	Aixam City and Crossline workshop manual	https://manualzz.com/doc/7220729/aixam-city-workshop-manual
EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	2990	1500	1540	Aixam City and Crossline workshop manual	https://manualzz.com/doc/7220729/aixam-city-workshop-manual
EU-AIXAM-CROSSOVER-IMPULSION-HATCHBACK-01	3095	1500	1565	Aixam City Crossline and Crossover owners manual	https://www.onlymanuals.com/index.php/aixam/crossline/aixam_crossline_owners_manual_1992_1992
EU-MEGA-E-SCOUTY-HATCHBACK-01	2650	1500	1480	Aixam-Mega E-Scouty official technical sheet	https://www.aixam.com/force_dl.php?fichier=ressources%2Fgammes%2Faixam_mega_escouty_ft_2025_web.pdf
```

## 下一步优先处理

1. 闭合 Addax MT、MTN、MTX，优先区分平板、底盘车及不同平台外廓。
2. 处理 Aixam D-Truck 柴油与纯电车型的厢式、Pick-up 和底盘车分支。
3. 补齐 Aixam Roadline、Scouty 与新款 Minauto Electric。

推进信号：CONTINUE

[1]: https://manualzz.com/doc/7220729/aixam-city-workshop-manual?utm_source=chatgpt.com "Aixam CITY Workshop Manual - L6e Quadricycle | Manualzz"
[2]: https://www.aixam.com/force_dl.php?fichier=ressources%2Fgammes%2Faixam_mega_escouty_ft_2025_web.pdf&utm_source=chatgpt.com "FINITIONS ET CARACTÉRISTIQUES"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* 本轮闭合剩余 **11 个 Aixam Ktype**，首次建立 **8 个尺寸组**。
* 第一代 D-Truck 按官方技术规格拆分为 Van、Pick-up 和 Drop Side，三者无镜宽度均为 1500 mm；2024 年电动 e-Truck 使用后期 3000 mm 车身，并按 Van 与栏板平台分别建组。
* Roadline 0.6 使用瑞士型式批准规格 `2897 × 1474 × 1440 mm`；Scouty 使用 `2674 × 1474 × 1480 mm` 敞篷外廓。([Motoro][1])
* Minauto Electric 对应 Minauto II 三门车身，长度与无镜宽度为 `2759 × 1500 mm`，高度按同代资料闭合为 `1470 mm`。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：95
* READY 映射行：136
* PENDING Ktype：5
* 已确认尺寸组：50
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106509	106509	Van	D-Truck I		2	EU-AIXAM-D-TRUCK-I-VAN-01	HIGH	第一代双门厢式车外廓。	READY
106510	106510	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-PICKUP-01	HIGH	第一代双门开放式货厢外廓。	READY
106511	106511	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按标准完成式栏板平台外廓落组。	READY
118039	118039	Van	D-Truck I		2	EU-AIXAM-D-TRUCK-I-VAN-01	HIGH	0.6柴油版本复用第一代双门厢式外廓。	READY
118040	118040	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-PICKUP-01	HIGH	0.6柴油版本复用第一代开放式货厢外廓。	READY
118041	118041	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按标准完成式栏板平台外廓落组。	READY
801824	801824	Van	e-Truck RS		2	EU-AIXAM-E-TRUCK-RS-VAN-01	HIGH	后期双门纯电厢式车外廓。	READY
801825	801825	Pickup	e-Truck RS		2	EU-AIXAM-E-TRUCK-RS-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按后期纯电栏板平台外廓落组。	READY
801819	801819	Hatchback	Minauto II		3	EU-AIXAM-MINAUTO-II-HATCHBACK-01	HIGH	Minauto II三门纯电车身。	READY
112213	112213	Hatchback	Roadline I		3	EU-AIXAM-ROADLINE-I-HATCHBACK-01	HIGH	Roadline长轴三门掀背外廓。	READY
100181	100181	Convertible	Scouty I		2	EU-AIXAM-SCOUTY-I-CONVERTIBLE-01	HIGH	Scouty双门可拆卸软顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AIXAM-D-TRUCK-I-VAN-01	3317	1500	1815	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-D-TRUCK-I-PICKUP-01	3272	1500	1750	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-D-TRUCK-I-DROPSIDE-01	3385	1500	1750	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-E-TRUCK-RS-VAN-01	3000	1500	1830	Aixam Germany official Pro Diesel and Electric specifications	https://aixam.de/wp-content/uploads/Aixam-Pro-Ausstattung.pdf
EU-AIXAM-E-TRUCK-RS-DROPSIDE-01	3000	1500	1750	Aixam Germany official Pro Diesel and Electric specifications	https://aixam.de/wp-content/uploads/Aixam-Pro-Ausstattung.pdf
EU-AIXAM-MINAUTO-II-HATCHBACK-01	2759	1500	1470	Aixam Germany official Minauto equipment sheet;Auto-Data Aixam MINAUTO II eMINAUTO specifications;Brno University of Technology small-city-vehicle frame study	https://aixam.de/wp-content/uploads/Ausstattung-Minauto.pdf;https://www.auto-data.net/en/aixam-minauto-ii-eminauto-5.44-kwh-8hp-53013;https://www.vut.cz/www_base/zav_prace_soubor_verejne.php?file_id=282856
EU-AIXAM-ROADLINE-I-HATCHBACK-01	2897	1474	1440	Motoro.ch Swiss type-approved AIXAM Roadline specifications	https://motoro.ch/en/fiche-technique/aixam/roadline
EU-AIXAM-SCOUTY-I-CONVERTIBLE-01	2674	1474	1480	Auta5P Aixam Scouty specifications;Dauto.ch Swiss type approval	https://auta5p.eu/lang/en/katalog/auto.php?idf=Aixam-Scouty-272;https://www.dauto.ch/typenscheine/aixam-scouty-gtr-6aa749-vlgl09vbac3-e2-2002-24-2002-24-0016
```

## 下一步优先处理

1. 闭合 Addax MT10、MT15、MT15N、MT8N 与 MT15X 共 5 个剩余 Ktype。
2. 区分 MT、MTN、MTX 平台以及标准栏板、底盘车可能造成的外廓差异。
3. PENDING 清零后，下一轮直接进行一次机械检查并输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://motoro.ch/en/fiche-technique/aixam/roadline "motoro.ch"
[2]: https://www.auto-data.net/en/aixam-minauto-ii-eminauto-5.44-kwh-8hp-53013 "Aixam MINAUTO II eMINAUTO 5.44 kWh (8 Hp) | Technical specs, data, battery, electric range, Dimensions"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1-100_ktype_dimension_mapping_final.tsv
- left18448_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
## 更新点

* 剩余 5 个 Addax Ktype 已闭合：MT10/MT15 复用第一代 MT 标准栏板平台；MT8N/MT15N 复用 MTN 标准平台；MT15X 使用 MTX 加长平台。
* 已完成机械检查：固定表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、所有映射引用闭合、三维及来源字段完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：141
* PENDING：0
* DIMENSION_GROUP：53
* 批次状态：全部完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58731	58731	Hatchback	500/595/695 (312)	312	3	EU-ABARTH-500-312-PREFL-HATCHBACK-01	HIGH	312 三门掀背，2016 年前外廓。	READY
120080	120080	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
120081	120081	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
121446	121446	Hatchback	595 (312)	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	HIGH	312 三门掀背，2016 facelift 外廓。	READY
59224	59224	Convertible	500C/595C/695C (312)	312	2	EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	HIGH	312 双门软顶，2016 年前外廓。	READY
59698	59698	Convertible	500C/595C/695C (312)	312	2	EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	MEDIUM	Ktype 目录指向 312 双门软顶；输入起始月早于车型公开上市。	READY
121235	121235	Convertible	595C (312)	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH	312 双门软顶，2016 facelift 外廓。	READY
122082	122082	Convertible	595C (312)	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH	312 双门软顶，2016 facelift 外廓。	READY
152402	152402	Hatchback	500e (332)	332	3	EU-ABARTH-500E-332-HATCHBACK-01	HIGH	332 三门纯电掀背。	READY
152403	152403	Convertible	500e (332)	332	2	EU-ABARTH-500E-332-CONVERTIBLE-01	HIGH	332 双门纯电软顶。	READY
160058	160058	SUV	600e (365)	365	5	EU-ABARTH-600E-365-SUV-01	HIGH	365 五门 SUV；Scorpionissima 与 Turismo 共用外廓。	READY
160053	160053	SUV	600e (365)	365	5	EU-ABARTH-600E-365-SUV-01	HIGH	365 五门 SUV；Turismo 与 Scorpionissima 共用外廓。	READY
56931	56931	Hatchback	Punto (199)	199	3	EU-ABARTH-PUNTO-199-HATCHBACK-01	HIGH	199系列三门Supersport外廓。	READY
14518	14518	Hatchback	Ritmo I	138A	3	EU-ABARTH-RITMO-I-HATCHBACK-01	HIGH	125 TC三门第一系列外廓。	READY
12424	12424	Convertible	428 Frua		2	EU-AC-428-FRUA-CONVERTIBLE-01	HIGH	Frua双门敞篷外廓。	READY
12428	12428	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12426	12426	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12430	12430	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	Ace III双门敞篷外廓。	READY
12431	12431	Convertible	Ace III		2	EU-AC-ACE-III-CONVERTIBLE-01	HIGH	机械增压版本不改变外廓。	READY
12434	12434	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	HIGH	Aceca III双门Coupé外廓。	READY
12436	12436	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	MEDIUM	输入起始时间早于Aceca III公开车型期；目录车型指向同一Coupé外廓。	READY
12437	12437	Coupe	Aceca III		2	EU-AC-ACECA-III-COUPE-01	HIGH	机械增压版本不改变外廓。	READY
12439	12439	Convertible	Cobra IV	291F	2	EU-AC-COBRA-IV-291F-STANDARD-CONVERTIBLE-01	HIGH	184 kW标准Mk IV外廓。	READY
12442	12442	Convertible	Cobra IV Lightweight	291F	2	EU-AC-COBRA-IV-291F-LIGHTWEIGHT-CONVERTIBLE-01	HIGH	250 kW Lightweight双门外廓。	READY
12443	12443	Convertible	Cobra IV Competition	291F	2	EU-AC-COBRA-IV-291F-COMPETITION-CONVERTIBLE-01	MEDIUM	5.8 Competition外廓；目录生产期宽于已查证车型期。	READY
12440	12440	Convertible	Cobra IV Superblower	291N	2	EU-AC-COBRA-IV-291N-SUPERBLOWER-CONVERTIBLE-01	HIGH	291N机械增压后期外廓。	READY
154955	154955	Pickup	MT		2	EU-ADDAX-MT-FLATBED-01	HIGH	MT10与MT15电池和动力差异不改变标准栏板平台外廓。	READY
154956	154956	Pickup	MT		2	EU-ADDAX-MT-FLATBED-01	HIGH	MT10与MT15电池和动力差异不改变标准栏板平台外廓。	READY
154957	154957	Pickup	MTN		2	EU-ADDAX-MTN-FLATBED-01	HIGH	MT15N标准轴距栏板平台外廓。	READY
154960	154960	Pickup	MTN		2	EU-ADDAX-MTN-FLATBED-01	HIGH	MT8N与MT15N共用标准轴距栏板平台外廓。	READY
154958	154958	Pickup	MTX		2	EU-ADDAX-MTX-LWB-FLATBED-01	HIGH	MT15X加长底盘栏板平台外廓。	READY
149025	149025	Sedan	Yixuan I	D53	4	EU-AEOLUS-YIXUAN-I-MACH-SEDAN-01	HIGH	1.5自然吸气Mach Edition四门外廓。	READY
163182	163182	SUV	Hyptec HT		5	EU-AION-HYPTEC-HT-SUV-01	HIGH	Hyptec HT五门纯电SUV外廓。	READY
163649	163649	SUV	Aion V II		5	EU-AION-V-II-EU-SUV-01	HIGH	第二代欧洲规格五门纯电SUV。	READY
150630	150630	SUV	U6		5	EU-AIWAYS-U6-SUV-01	HIGH	U6五门纯电SUV Coupé外廓。	READY
100175	100175	Hatchback	City Impulsion		3	EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	HIGH	Impulsion系列三门城市车外廓。	READY
106507	106507	Hatchback	City Impulsion		3	EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	HIGH	纯电版本复用同一三门外廓。	READY
12773	12773	Hatchback	Crossline Impulsion		3	EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	HIGH	Impulsion系列三门Crossline外廓。	READY
127221	127221	Hatchback	Crossline Impulsion		3	EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	HIGH	发动机版本不改变物理外廓。	READY
118699	118699	Hatchback	Crossover Impulsion		3	EU-AIXAM-CROSSOVER-IMPULSION-HATCHBACK-01	HIGH	GTR版本对应Crossover三门外廓。	READY
106509	106509	Van	D-Truck I		2	EU-AIXAM-D-TRUCK-I-VAN-01	HIGH	第一代双门厢式车外廓。	READY
106510	106510	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-PICKUP-01	HIGH	第一代双门开放式货厢外廓。	READY
106511	106511	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按标准完成式栏板平台外廓落组。	READY
118039	118039	Van	D-Truck I		2	EU-AIXAM-D-TRUCK-I-VAN-01	HIGH	0.6柴油版本复用第一代双门厢式外廓。	READY
118040	118040	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-PICKUP-01	HIGH	0.6柴油版本复用第一代开放式货厢外廓。	READY
118041	118041	Pickup	D-Truck I		2	EU-AIXAM-D-TRUCK-I-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按标准完成式栏板平台外廓落组。	READY
801824	801824	Van	e-Truck RS		2	EU-AIXAM-E-TRUCK-RS-VAN-01	HIGH	后期双门纯电厢式车外廓。	READY
801825	801825	Pickup	e-Truck RS		2	EU-AIXAM-E-TRUCK-RS-DROPSIDE-01	MEDIUM	Pritsche/Fahrgestell按后期纯电栏板平台外廓落组。	READY
163905	163905	Hatchback	E-Scouty		3	EU-MEGA-E-SCOUTY-HATCHBACK-01	HIGH	三门纯电轻型车外廓。	READY
801819	801819	Hatchback	Minauto II		3	EU-AIXAM-MINAUTO-II-HATCHBACK-01	HIGH	Minauto II三门纯电车身。	READY
112213	112213	Hatchback	Roadline I		3	EU-AIXAM-ROADLINE-I-HATCHBACK-01	HIGH	Roadline长轴三门掀背外廓。	READY
100181	100181	Convertible	Scouty I		2	EU-AIXAM-SCOUTY-I-CONVERTIBLE-01	HIGH	Scouty双门可拆卸软顶外廓。	READY
127183_prefl	127183	Hatchback	33 Series I	905	5	EU-ALFA-ROMEO-33-905-PREFL-HATCHBACK-01	HIGH	第一系列早期五门外廓。	READY
127183_facelift	127183	Hatchback	33 Series I	905	5	EU-ALFA-ROMEO-33-905-FACELIFT-HATCHBACK-01	HIGH	第一系列后期增高五门外廓。	READY
17422	17422	Hatchback	33 Series II	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH	907A第二系列五门掀背外廓。	READY
125927	125927	Wagon	33 Series II Sport Wagon	907B	5	EU-ALFA-ROMEO-33-907B-4X4-WAGON-01	HIGH	907B五门四驱旅行车外廓。	READY
54968_prefl	54968	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-PREFL-HATCHBACK-01	HIGH	1999外观改款前的三门外廓。	READY
54968_facelift	54968	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	HIGH	1999外观改款后的三门外廓。	READY
11899	11899	Hatchback	145 (930)	930A	3	EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	HIGH	JTD对应1999改款后三门外廓。	READY
54967_prefl	54967	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-PREFL-HATCHBACK-01	HIGH	1999外观改款前的五门外廓。	READY
54967_facelift	54967	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	HIGH	1999外观改款后的五门外廓。	READY
12242	12242	Hatchback	146 (930)	930B	5	EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	HIGH	JTD对应1999改款后五门外廓。	READY
15529_3dr_prefl	15529	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
15529_5dr_prefl	15529	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
15529_3dr_facelift	15529	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15529_5dr_facelift	15529	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
15579_3dr_prefl	15579	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
15579_5dr_prefl	15579	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
15579_3dr_facelift	15579	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15579_5dr_facelift	15579	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
16441_3dr_prefl	16441	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
16441_5dr_prefl	16441	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
16441_3dr_facelift	16441	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
16441_5dr_facelift	16441	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17436_3dr_prefl	17436	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
17436_5dr_prefl	17436	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
17436_3dr_facelift	17436	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
17436_5dr_facelift	17436	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17161_3dr_prefl	17161	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937三门，2004改款前外廓。	READY
17161_5dr_prefl	17161	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	HIGH	937五门，2004改款前外廓。	READY
17161_3dr_facelift	17161	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
17161_5dr_facelift	17161	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
18933_3dr_prefl	18933	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	MEDIUM	起始月跨越改款切换期；保留改款前三门分支。	READY
18933_5dr_prefl	18933	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	MEDIUM	起始月跨越改款切换期；保留改款前五门分支。	READY
18933_3dr_facelift	18933	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
18933_5dr_facelift	18933	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
18932_3dr	18932	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
18932_5dr	18932	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
15528_3dr_prefl	15528	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	HIGH	改款前2.0低车身三门外廓。	READY
15528_5dr_prefl	15528	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	HIGH	改款前2.0低车身五门外廓。	READY
15528_3dr_facelift	15528	Hatchback	147 (937)	937	3	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937三门，2004改款后外廓。	READY
15528_5dr_facelift	15528	Hatchback	147 (937)	937	5	EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	HIGH	937五门，2004改款后外廓。	READY
17121	17121	Hatchback	147 GTA (937)	937	3	EU-ALFA-ROMEO-147-GTA-937-HATCHBACK-01	HIGH	GTA三门宽体及降低车身外廓。	READY
5749	5749	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-01	HIGH	167系列四门轿车外廓。	READY
5748	5748	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-01	HIGH	167系列四门轿车外廓。	READY
8808_prefl	8808	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
8808_facelift	8808	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
54965_prefl	54965	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
54965_facelift	54965	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
54966_prefl	54966	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
54966_facelift	54966	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
14784_prefl	14784	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
14784_facelift	14784	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8809	8809	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14785	14785	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15616_prefl	15616	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15616_facelift	15616	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
15617_prefl	15617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15617_facelift	15617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8812	8812	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14788	14788	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15688	15688	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
15692	15692	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
16584_prefl	16584	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16584_facelift	16584	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16586_prefl	16586	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16586_facelift	16586	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17162_prefl	17162	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
17162_facelift	17162	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17163_prefl	17163	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
17163_facelift	17163	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
18205	18205	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-Q4-WAGON-01	HIGH	Q4升高底盘五门旅行车外廓。	READY
8810	8810	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
14786	14786	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15618	15618	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	2003外观改款前五门旅行车。	READY
15619	15619	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	2003外观改款前四门轿车。	READY
16617_prefl	16617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16617_facelift	16617	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16619_prefl	16619	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16619_facelift	16619	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
8813	8813	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	截至2003年9月的改款前四门轿车。	READY
14789	14789	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	截至2003年9月的改款前五门旅行车。	READY
15690_prefl	15690	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15690_facelift	15690	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
15693_prefl	15693	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
15693_facelift	15693	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16618_prefl	16618	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16618_facelift	16618	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	跨越2003外观改款；改款后外廓。	READY
16620_prefl	16620	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	跨越2003外观改款；改款前外廓。	READY
16620_facelift	16620	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	跨越2003外观改款；改款后外廓。	READY
17622	17622	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	2003外观改款后四门轿车。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1-100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ABARTH-500-312-PREFL-HATCHBACK-01	3657	1627	1485	Automobile-Catalog 2010 Abarth 500 specifications	https://www.automobile-catalog.com/car/2010/728645/abarth_500.html
EU-ABARTH-595-312-FACELIFT-HATCHBACK-01	3660	1627	1485	New Abarth 595 official technical specifications	https://www.media.stellantis.com/uploads/em/2016/ABARTH/Schde_tecniche/160607_Abarth_595_Technical-Specs_ENG.pdf
EU-ABARTH-500C-312-PREFL-CONVERTIBLE-01	3657	1627	1488	Auto-Data Abarth 500C generation specifications	https://www.auto-data.net/en/abarth-500c-generation-8152
EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	3660	1627	1485	New Abarth 595 official technical specifications	https://www.media.stellantis.com/uploads/em/2016/ABARTH/Schde_tecniche/160607_Abarth_595_Technical-Specs_ENG.pdf
EU-ABARTH-500E-332-HATCHBACK-01	3673	1682	1518	ADAC Abarth 500e technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/abarth/500-595-695/2generation/328228/
EU-ABARTH-500E-332-CONVERTIBLE-01	3673	1682	1518	ADAC Abarth 500e Cabrio technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/abarth/500-595-695/2generation/328231/
EU-ABARTH-600E-365-SUV-01	4187	1779	1502	Abarth 600e official technical sheet; Automobile-Catalog Abarth 600e Scorpionissima specifications	https://www.media.stellantis.com/uploads/it/model-document/abarth600e_technicalsheet-6720bb5f92145.pdf;https://www.automobile-catalog.com/car/2024/3380030/abarth_600e_scorpionissima.html
EU-ABARTH-PUNTO-199-HATCHBACK-01	4065	1726	1490	Automobile-Catalog 2014 Abarth Punto Supersport specifications	https://www.automobile-catalog.com/car/2014/1759490/abarth_punto_supersport.html
EU-ABARTH-RITMO-I-HATCHBACK-01	3937	1687	1370	Automobile-Catalog 1981 Fiat Ritmo Abarth 125 TC specifications	https://www.automobile-catalog.com/car/1981/714170/fiat_ritmo_abarth_125_tc.html
EU-AC-428-FRUA-CONVERTIBLE-01	4420	1702	1295	Automobile-Catalog 1966 AC 428 Frua Convertible specifications	https://www.automobile-catalog.com/car/1966/64805/ac_428_convertible.html
EU-AC-ACE-III-CONVERTIBLE-01	4420	1870	1300	Automobile-Catalog AC Ace 4.9L and 4.6L specifications	https://www.automobile-catalog.com/car/1995/213185/ac_ace_4_9l_v-8.html;https://www.automobile-catalog.com/car/1998/213290/ac_ace_4_6l_v-8_32v.html
EU-AC-ACECA-III-COUPE-01	4660	1890	1340	Automobile-Catalog 1998 AC Aceca 4.6L specifications	https://www.automobile-catalog.com/car/1998/213305/ac_aceca_4_6l_v-8_32v.html
EU-AC-COBRA-IV-291F-STANDARD-CONVERTIBLE-01	4115	1735	1245	Automobile-Catalog 1990 AC Cobra Mk IV specifications	https://www.automobile-catalog.com/car/1990/212960/ac_cobra_mk_iv.html
EU-AC-COBRA-IV-291F-LIGHTWEIGHT-CONVERTIBLE-01	4155	1745	1230	Auto-Data AC Cobra Mk IV Lightweight specifications	https://www.auto-data.net/en/ac-cobra-mk-iv-4.9-i-v8-lightweight-340hp-10
EU-AC-COBRA-IV-291F-COMPETITION-CONVERTIBLE-01	4115	1735	1245	Automobile-Catalog 1990 AC Cobra Mk IV Competition 5.8L specifications	https://www.automobile-catalog.com/car/1990/213050/ac_cobra_mk_iv_competition_5_8l.html
EU-AC-COBRA-IV-291N-SUPERBLOWER-CONVERTIBLE-01	4200	1745	1200	Auto-Data AC Cobra Mk IV Superblower specifications	https://www.auto-data.net/en/ac-cobra-mk-iv-4.9-i-v8-superblower-326hp-11
EU-ADDAX-MT-FLATBED-01	3590	1500	1990	Addax Motors official MT10/MT15 brochure; KOMUFA Addax MT15 vehicle data	https://www.hh-garden.be/wp-content/uploads/2020/04/Flyer_Addax_NL.pdf;https://komufa.de/addax-elektrotransporter.html?___from_store=en&___store=de
EU-ADDAX-MTN-FLATBED-01	3655	1450	1990	Addax Motors MT15n official flatbed technical sheet	https://www.addaxmotors.com/uploads/files/Technical-sheet/MT15n_Flatbed.pdf
EU-ADDAX-MTX-LWB-FLATBED-01	4165	1450	1990	ISEKI MT15x COMBI technical sheet	https://www.iseki.fr/wp-content/uploads/2022/09/MT15x_COMBI.pdf
EU-AEOLUS-YIXUAN-I-MACH-SEDAN-01	4670	1812	1490	CarNewsChina Aeolus Yixuan Mach Edition specifications	https://carnewschina.com/2022/10/29/dongfeng-aeolus-yixuan-mach-edition-launched-in-china-price-starts-at-8900-usd/
EU-AION-HYPTEC-HT-SUV-01	4935	1920	1700	GAC official HYPTEC HT specifications	https://www.gacgroup.com/en-hk/configuration/hyptec-ht/2024
EU-AION-V-II-EU-SUV-01	4605	1854	1686	GAC Europe official AION V specifications	https://www.gacgroup.com/en-eu/configuration/aion-v/2024
EU-AIWAYS-U6-SUV-01	4805	1880	1641	EV Database Aiways U6 specifications	https://ev-database.org/car/1766/Aiways-U6
EU-AIXAM-CITY-IMPULSION-HATCHBACK-01	2720	1500	1470	Aixam City and Crossline workshop manual	https://manualzz.com/doc/7220729/aixam-city-workshop-manual
EU-AIXAM-CROSSLINE-IMPULSION-HATCHBACK-01	2990	1500	1540	Aixam City and Crossline workshop manual	https://manualzz.com/doc/7220729/aixam-city-workshop-manual
EU-AIXAM-CROSSOVER-IMPULSION-HATCHBACK-01	3095	1500	1565	Aixam City Crossline and Crossover owners manual	https://www.onlymanuals.com/index.php/aixam/crossline/aixam_crossline_owners_manual_1992_1992
EU-AIXAM-D-TRUCK-I-VAN-01	3317	1500	1815	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-D-TRUCK-I-PICKUP-01	3272	1500	1750	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-D-TRUCK-I-DROPSIDE-01	3385	1500	1750	Aixam Pro D-Truck official technical specifications	https://www.aixam-pro.com/ressources/brochures/technical_specifications.pdf
EU-AIXAM-E-TRUCK-RS-VAN-01	3000	1500	1830	Aixam Germany official Pro Diesel and Electric specifications	https://aixam.de/wp-content/uploads/Aixam-Pro-Ausstattung.pdf
EU-AIXAM-E-TRUCK-RS-DROPSIDE-01	3000	1500	1750	Aixam Germany official Pro Diesel and Electric specifications	https://aixam.de/wp-content/uploads/Aixam-Pro-Ausstattung.pdf
EU-MEGA-E-SCOUTY-HATCHBACK-01	2650	1500	1480	Aixam-Mega E-Scouty official technical sheet	https://www.aixam.com/force_dl.php?fichier=ressources%2Fgammes%2Faixam_mega_escouty_ft_2025_web.pdf
EU-AIXAM-MINAUTO-II-HATCHBACK-01	2759	1500	1470	Aixam Germany official Minauto equipment sheet;Auto-Data Aixam MINAUTO II eMINAUTO specifications;Brno University of Technology small-city-vehicle frame study	https://aixam.de/wp-content/uploads/Ausstattung-Minauto.pdf;https://www.auto-data.net/en/aixam-minauto-ii-eminauto-5.44-kwh-8hp-53013;https://www.vut.cz/www_base/zav_prace_soubor_verejne.php?file_id=282856
EU-AIXAM-ROADLINE-I-HATCHBACK-01	2897	1474	1440	Motoro.ch Swiss type-approved AIXAM Roadline specifications	https://motoro.ch/en/fiche-technique/aixam/roadline
EU-AIXAM-SCOUTY-I-CONVERTIBLE-01	2674	1474	1480	Auta5P Aixam Scouty specifications;Dauto.ch Swiss type approval	https://auta5p.eu/lang/en/katalog/auto.php?idf=Aixam-Scouty-272;https://www.dauto.ch/typenscheine/aixam-scouty-gtr-6aa749-vlgl09vbac3-e2-2002-24-2002-24-0016
EU-ALFA-ROMEO-33-905-PREFL-HATCHBACK-01	4015	1612	1303	Automobile-Catalog 1983 Alfa Romeo 33 1.3 specifications	https://www.automobile-catalog.com/car/1983/214760/alfa_romeo_33_1_3.html
EU-ALFA-ROMEO-33-905-FACELIFT-HATCHBACK-01	4015	1612	1345	Automobile-Catalog 1987 Alfa Romeo 33 1.3 S specifications	https://www.automobile-catalog.com/car/1987/215000/alfa_romeo_33_1_3_s.html
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Automobile-Catalog 1990 Alfa Romeo 33 1.5 specifications	https://www.automobile-catalog.com/car/1990/216740/alfa_romeo_33_1_5.html
EU-ALFA-ROMEO-33-907B-4X4-WAGON-01	4200	1614	1350	Auto-Data Alfa Romeo 33 Sport Wagon 1.7 16V 4x4 specifications	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.7-16v-129hp-4x4-1393
EU-ALFA-ROMEO-145-930-PREFL-HATCHBACK-01	4093	1712	1427	Automobile-Catalog 1997 Alfa Romeo 145 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1997/218135/alfa_romeo_145_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-145-930-FACELIFT-HATCHBACK-01	4061	1712	1431	Automobile-Catalog 1999 Alfa Romeo 145 1.9 JTD specifications	https://www.automobile-catalog.com/car/1999/218225/alfa_romeo_145_1_9_jtd.html
EU-ALFA-ROMEO-146-930-PREFL-HATCHBACK-01	4257	1712	1425	Automobile-Catalog 1998 Alfa Romeo 146 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1998/218180/alfa_romeo_146_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-146-930-FACELIFT-HATCHBACK-01	4235	1712	1425	Automobile-Catalog 1999 Alfa Romeo 146 1.9 JTD specifications	https://www.automobile-catalog.com/car/1999/218360/alfa_romeo_146_1_9_jtd.html
EU-ALFA-ROMEO-147-937-PREFL-HATCHBACK-01	4170	1729	1442	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-937-FACELIFT-HATCHBACK-01	4223	1729	1442	Alfa Romeo New 147 official technical specifications	https://www.media.stellantis.com/it-it/alfa-romeo/press/la-nuova-gamma-di-alfa-147
EU-ALFA-ROMEO-147-937-PREFL-LOW-HATCHBACK-01	4170	1729	1421	Alfa Romeo 147 official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-GTA-937-HATCHBACK-01	4213	1764	1412	Alfa Romeo 147 GTA official press information; Automobile-Catalog 2003 Alfa Romeo 147 GTA specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-romeo-147-gta-in-uk;https://www.automobile-catalog.com/car/2003/221360/alfa_romeo_147_gta.html
EU-ALFA-ROMEO-155-167-SEDAN-01	4443	1730	1425	Automobile-Catalog 1996 Alfa Romeo 155 1.6 Twin Spark 16V specifications	https://www.automobile-catalog.com/car/1996/217640/alfa_romeo_155_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	4430	1745	1415	Automobile-Catalog 1998 Alfa Romeo 156 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/1998/218735/alfa_romeo_156_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	4435	1743	1390	Automobile-Catalog 2005 Alfa Romeo 156 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/2005/220565/alfa_romeo_156_1_6_twin_spark_16v_impression_business__base.html
EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	4430	1745	1420	Automobile-Catalog 2000 Alfa Romeo 156 Sportwagon 1.6 Twin Spark specifications	https://www.automobile-catalog.com/car/2000/218855/alfa_romeo_156_sportwagon_1_6_twin_spark_16v.html
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon 2.4 JTD specifications	https://www.automobile-catalog.com/car/2004/220265/alfa_romeo_156_sportwagon_2_4_jtd_20v_distinctive_exclusive__lusso.html
EU-ALFA-ROMEO-156-932-Q4-WAGON-01	4441	1743	1458	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon Q4 specifications	https://www.automobile-catalog.com/car/2004/220610/alfa_romeo_156_sportwagon_q4.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1-100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（141 行）
- 累计尺寸组：dimension_groups_final.tsv（53 行）

