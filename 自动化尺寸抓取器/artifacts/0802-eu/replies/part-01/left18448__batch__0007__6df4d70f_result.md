# 任务：left18448 第 601-700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0007__6df4d70f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 601-700 行

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
left18448 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_601-700_ktype_dimension_mapping_final.tsv
- left18448_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8L-HATCHBACK-01	4152	1735	1427
EU-AUDI-A3-8P7-CABRIOLET-FACELIFT-2008-01	4238	1765	1424
EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	4292	1765	1423
EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-PREFL-01	4203	1765	1421
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-CABRIOLET-PREFL-01	4421	1793	1409
EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	4241	1777	1424
EU-AUDI-A3-8V-HATCHBACK-PREFL-01	4237	1777	1421
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SEDAN-PREFL-01	4456	1796	1416
EU-AUDI-A3-8V-SPORTBACK-ETRON-FACELIFT-01	4311	1785	1426
EU-AUDI-A3-8V-SPORTBACK-ETRON-PREFL-01	4312	1785	1424
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A3-8V-SPORTBACK-PREFL-01	4310	1785	1425

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Audi	A3	2.0 FSI	Schrägheck	Frontantrieb	Benzin	May 2003	Jun 2008	17009
Audi	A3	2.0 FSI	Schrägheck	Frontantrieb	Benzin	Sep 2004	Jun 2008	18069
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2003	Aug 2012	17458
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2004	Mar 2013	18357
Audi	A3	2.0 TDI	Stufenheck	Frontantrieb	Diesel	Oct 2013	Oct 2020	53263
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Oct 2020	53313
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2012	Oct 2020	55094
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Apr 2012	Dec 2017	55095
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Jan 2013	Aug 2016	55591
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Dec 2017	55593
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Sep 2012	Oct 2020	55597
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Mar 2013	Oct 2020	55599
Audi	A3	2.0 TDI	Stufenheck	Frontantrieb	Diesel	May 2013	Oct 2020	59618
Audi	A3	2.0 TDI	Stufenheck	Frontantrieb	Diesel	May 2013	Oct 2020	59619
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Jul 2018	59621
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Aug 2016	59624
Audi	A3	2.0 TDI	Stufenheck	Frontantrieb	Diesel	Sep 2013	Aug 2016	59629
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	May 2013	Aug 2016	59630
Audi	A3	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Oct 2013	Oct 2020	100044
Audi	A3	2.0 TDI	Stufenheck	Frontantrieb	Diesel	May 2014	Jul 2018	105627
Audi	A3	2.0 TDI	Cabriolet	Frontantrieb	Diesel	May 2014	Jul 2016	106221
Audi	A3	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Oct 2013	Jul 2016	106382
Audi	A3	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	May 2003	Aug 2012	17173
Audi	A3	2.0 TDI 16V	Schrägheck	Frontantrieb	Diesel	Sep 2004	Mar 2013	18071
Audi	A3	2.0 TDI 16V Quattro	Schrägheck	Allrad	Diesel	Aug 2004	Aug 2012	18360
Audi	A3	2.0 TDI 16V Quattro	Schrägheck	Allrad	Diesel	Nov 2005	Mar 2013	18710
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	May 2003	Jun 2008	18356
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	Oct 2012	Dec 2017	55592
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	Dec 2012	Dec 2017	55594
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	May 2013	Jul 2018	55598
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	Feb 2013	Oct 2020	58948
Audi	A3	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	Oct 2013	Oct 2020	100046
Audi	A3	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	Mar 2014	Oct 2020	100776
Audi	A3	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	May 2014	Jul 2018	105628
Audi	A3	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	May 2014	Oct 2020	106222
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Sep 2004	Mar 2013	18082
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Sep 2004	Aug 2012	18358
Audi	A3	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	Nov 2015	Oct 2020	118767
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	May 2016	Dec 2017	120627
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	May 2016	Oct 2020	120629
Audi	A3	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	May 2016	Oct 2020	120632
Audi	A3	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	May 2016	Oct 2020	120633
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	Sep 2004	Mar 2013	18083
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	Sep 2004	Aug 2012	18359
Audi	A3	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	May 2014	Oct 2020	116310
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2016	Dec 2017	120616
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2016	Oct 2020	120617
Audi	A3	2.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	May 2016	Oct 2020	120618
Audi	A3	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	May 2016	Oct 2020	120620
Audi	A3	3.2 V6 Quattro	Schrägheck	Allrad	Benzin	Jul 2003	May 2009	17577
Audi	A3	3.2 V6 Quattro	Schrägheck	Allrad	Benzin	Sep 2004	May 2009	18070
Audi	A3	30 Tfsi	Stufenheck	Frontantrieb	Benzin	May 2024	-	158507
Audi	A3	30 Tfsi	Schrägheck	Frontantrieb	Benzin	May 2024	-	158522
Audi	A3	30 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	May 2024	-	158514
Audi	A3	30 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	May 2024	-	158521
Audi	A3	35 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2022	-	148316
Audi	A3	35 TDI	Schrägheck	Frontantrieb	Diesel	Feb 2024	-	158250
Audi	A3	35 Tfsi	Stufenheck	Frontantrieb	Benzin	Aug 2020	-	146890
Audi	A3	35 Tfsi	Schrägheck	Frontantrieb	Benzin	Aug 2021	-	147109
Audi	A3	35 Tfsi	Schrägheck	Frontantrieb	Benzin	Sep 2024	-	800828
Audi	A3	35 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2022	-	148318
Audi	A3	35 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Feb 2024	-	158252
Audi	A3	40 E-tron	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2018	Oct 2020	151896
Audi	A3	40 TDI Quattro	Stufenheck	Allrad	Diesel	Dec 2020	-	143265
Audi	A3	40 TDI Quattro	Schrägheck	Allrad	Diesel	Dec 2020	-	143266
Audi	A3	40 Tfsi E	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2024	-	801113
Audi	A3	40 Tfsi Quattro	Stufenheck	Allrad	Benzin	Jul 2021	-	144929
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	Jul 2021	-	144930
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	Jul 2022	-	148317
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	Aug 2024	-	801698
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	Mar 2025	-	801713
Audi	A3	40 Tfsi Quattro	Stufenheck	Allrad	Benzin	Apr 2025	-	801860
Audi	A3	40 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2022	-	148312
Audi	A3	40 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2024	-	801077
Audi	A3	45 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2021	-	144931
Audi	A3	45 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	Nov 2024	-	801108
Audi	A3	RS3 Quattro	Schrägheck	Allrad	Benzin	Jan 2011	Dec 2012	10523
Audi	A3	RS3 Quattro	Schrägheck	Allrad	Benzin	Mar 2015	Aug 2016	112295
Audi	A3	RS3 Quattro	Schrägheck	Allrad	Benzin	Apr 2017	Oct 2020	126875
Audi	A3	RS3 Quattro	Stufenheck	Allrad	Benzin	Apr 2017	Oct 2020	126876
Audi	A3	RS3 Tfsi Quattro	Stufenheck	Allrad	Benzin	Jul 2021	-	145088
Audi	A3	RS3 Tfsi Quattro	Schrägheck	Allrad	Benzin	Jul 2021	-	145089
Audi	A3	RS3 Tfsi Quattro	Stufenheck	Allrad	Benzin	Jan 2022	-	149409
Audi	A3	RS3 Tfsi Quattro	Schrägheck	Allrad	Benzin	Nov 2022	-	151160
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Mar 1999	Apr 2002	11268
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	Oct 2013	Oct 2020	50895
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	Oct 2013	May 2014	54775
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Feb 2013	Jul 2014	57437
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Nov 2012	Aug 2016	57438
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Nov 2012	Oct 2020	59244
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	May 2013	Aug 2016	59631
Audi	A3	S3 Quattro	Cabriolet	Allrad	Benzin	Apr 2014	Oct 2020	100931
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	May 2014	Aug 2016	106371
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	May 2014	Aug 2016	106376
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	May 2014	Aug 2016	106381
Audi	A3	S3 Quattro	Cabriolet	Allrad	Benzin	Mar 2014	Jul 2016	106383
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	May 2014	Oct 2020	108249
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Jun 2016	Dec 2017	120607
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	Jun 2016	Oct 2020	120608
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	Jun 2016	Oct 2020	120609


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖当前批次全部 100 个输入 Ktype；跨越确定改款或不同物理车身的记录已拆分，最终形成 146 条唯一映射。
* 已复用跨批次缓存中的 14 个 A3 8P/8V 尺寸组，并首次闭合 21 个 A3 8Y、PHEV、S3、RS3 专用尺寸组。
* Ktype 对应的 8V1/8VK、8VA/8VF、8VS/8VM、8V7/8VE 等车身边界已按 TecDoc 车型适用信息核对；RS3 改款 Sportback 和 Sedan 分别使用 8VF、8VM。([Allegro][1])
* 新建的 S3、RS3 专用尺寸组与 8Y 普通/PHEV 尺寸组均采用不含后视镜宽度；Audi 官方技术资料明确标示 S3/RS3 的车身尺寸口径。([Audi 新闻中心][2])

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：146
* PENDING 映射：0
* DIMENSION_GROUP：35
* 映射引用闭合：35 / 35
* 孤立尺寸组：0
* 机械检查：10 列与 6 列表头、唯一主键、正整数三维、来源非空及下载文件均已通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17009_prefl	17009	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
17009_facelift2005	17009	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
18069	18069	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
17458_prefl	17458	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
17458_facelift2005	17458	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
17458_facelift2008	17458	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
18357_prefl	18357	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18357_facelift2008	18357	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
53263_prefl	53263	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
53263_facelift	53263	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
53313_prefl	53313	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
53313_facelift	53313	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
55094_prefl	55094	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55094_facelift	55094	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
55095_prefl	55095	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55095_facelift	55095	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
55591	55591	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55593_prefl	55593	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55593_facelift	55593	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
55597_prefl	55597	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
55597_facelift	55597	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
55599_prefl	55599	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
55599_facelift	55599	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
59618_prefl	59618	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
59618_facelift	59618	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
59619_prefl	59619	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
59619_facelift	59619	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
59621_prefl	59621	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
59621_facelift	59621	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
59624	59624	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
59629	59629	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
59630	59630	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
100044_prefl	100044	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
100044_facelift	100044	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
105627_prefl	105627	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
105627_facelift	105627	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
106221	106221	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
106382	106382	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
17173_prefl	17173	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
17173_facelift2005	17173	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
17173_facelift2008	17173	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
18071_prefl	18071	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18071_facelift2008	18071	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
18360_prefl	18360	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
18360_facelift2005	18360	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
18360_facelift2008	18360	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
18710_prefl	18710	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18710_facelift2008	18710	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
18356_prefl	18356	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
18356_facelift2005	18356	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
55592_prefl	55592	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55592_facelift	55592	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
55594_prefl	55594	Hatchback	A3 8V	8V1	3	EU-AUDI-A3-8V-HATCHBACK-PREFL-01	HIGH	8V1三门，改款前外廓。	READY
55594_facelift	55594	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
55598_prefl	55598	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
55598_facelift	55598	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
58948_prefl	58948	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-PREFL-01	HIGH	8VA五门Sportback，改款前外廓。	READY
58948_facelift	58948	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
100046_prefl	100046	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
100046_facelift	100046	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
100776_prefl	100776	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
100776_facelift	100776	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
105628_prefl	105628	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
105628_facelift	105628	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
106222_prefl	106222	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
106222_facelift	106222	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
18082_prefl	18082	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18082_facelift2008	18082	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
18358_prefl	18358	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
18358_facelift2005	18358	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
18358_facelift2008	18358	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
118767_prefl	118767	Sedan	A3 8V	8VS	4	EU-AUDI-A3-8V-SEDAN-PREFL-01	HIGH	8VS四门Sedan，改款前外廓。	READY
118767_facelift	118767	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
120627	120627	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
120629	120629	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
120632	120632	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
120633	120633	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
18083_prefl	18083	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18083_facelift2008	18083	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
18359_prefl	18359	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
18359_facelift2005	18359	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
18359_facelift2008	18359	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
116310_prefl	116310	Convertible	A3 8V	8V7	2	EU-AUDI-A3-8V-CABRIOLET-PREFL-01	HIGH	8V7双门Cabriolet，改款前外廓。	READY
116310_facelift	116310	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
120616	120616	Hatchback	A3 8V	8VK	3	EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	HIGH	8VK三门，2016改款外廓。	READY
120617	120617	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	8VF五门Sportback，2016改款外廓。	READY
120618	120618	Sedan	A3 8V	8VM	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8VM四门Sedan，2016改款外廓。	READY
120620	120620	Convertible	A3 8V	8VE	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH	8VE双门Cabriolet，2016改款外廓。	READY
17577_prefl	17577	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-PREFL-01	HIGH	8P1三门，改款前外廓。	READY
17577_facelift2005	17577	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	HIGH	8P1三门，2005改款外廓。	READY
17577_facelift2008	17577	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	HIGH	8P1三门，2008改款外廓。	READY
18070_prefl	18070	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	HIGH	8PA五门Sportback，2008改款前外廓。	READY
18070_facelift2008	18070	Hatchback	A3 8P	8PA	5	EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	HIGH	8PA五门Sportback，2008改款外廓。	READY
158507	158507	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-FACELIFT-2024-01	HIGH	8YS四门Sedan，2024改款外廓。	READY
158522	158522	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	HIGH	8YA五门Sportback，2024改款外廓。	READY
158514	158514	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-FACELIFT-2024-01	HIGH	8YS四门Sedan，2024改款外廓。	READY
158521	158521	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	HIGH	8YA五门Sportback，2024改款外廓。	READY
148316	148316	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
158250	158250	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	MEDIUM	8YA五门Sportback，2024年2月起始，按改款前外廓。	READY
146890	146890	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH	8YS四门Sedan，2024改款前外廓。	READY
147109	147109	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
800828	800828	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	HIGH	8YA五门Sportback，2024改款外廓。	READY
148318	148318	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
158252	158252	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	MEDIUM	8YA五门Sportback，2024年2月起始，按改款前外廓。	READY
151896	151896	Hatchback	A3 8V	8VF	5	EU-AUDI-A3-8V-SPORTBACK-ETRON-FACELIFT-01	HIGH	8VF五门Sportback e-tron，2016改款外廓。	READY
143265	143265	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH	8YS四门Sedan，2024改款前外廓。	READY
143266	143266	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
801113	801113	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PHEV-FACELIFT-2024-01	HIGH	8YA五门Sportback PHEV，2024改款外廓。	READY
144929	144929	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH	8YS四门Sedan，2024改款前外廓。	READY
144930	144930	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
148317	148317	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8YA五门Sportback，2024改款前外廓。	READY
801698	801698	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	HIGH	8YA五门Sportback，2024改款外廓。	READY
801713	801713	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	HIGH	8YA五门Sportback，2024改款外廓。	READY
801860	801860	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-FACELIFT-2024-01	HIGH	8YS四门Sedan，2024改款外廓。	READY
148312	148312	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PHEV-PREFL-01	HIGH	8YA五门Sportback PHEV，2024改款前外廓。	READY
801077	801077	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PHEV-FACELIFT-2024-01	HIGH	8YA五门Sportback PHEV，2024改款外廓。	READY
144931	144931	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PHEV-PREFL-01	HIGH	8YA五门Sportback PHEV，2024改款前外廓。	READY
801108	801108	Hatchback	A3 8Y	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PHEV-FACELIFT-2024-01	HIGH	8YA五门Sportback PHEV，2024改款外廓。	READY
10523	10523	Hatchback	RS 3 8P	8PA	5	EU-AUDI-A3-8PA-RS3-SPORTBACK-01	HIGH	8PA五门RS 3专用外廓。	READY
112295	112295	Hatchback	RS 3 8V	8VA	5	EU-AUDI-A3-8VA-RS3-SPORTBACK-PREFL-01	HIGH	8VA五门RS 3，改款前专用外廓。	READY
126875	126875	Hatchback	RS 3 8V	8VF	5	EU-AUDI-A3-8VF-RS3-SPORTBACK-FACELIFT-01	HIGH	8VF五门RS 3，2017改款专用外廓。	READY
126876	126876	Sedan	RS 3 8V	8VM	4	EU-AUDI-A3-8VM-RS3-SEDAN-FACELIFT-01	HIGH	8VM四门RS 3 Sedan专用外廓。	READY
145088	145088	Sedan	RS 3 8Y	8YS	4	EU-AUDI-A3-8Y-RS3-SEDAN-PREFL-01	HIGH	8YS四门RS 3 Sedan，2024改款前专用宽体外廓。	READY
145089	145089	Hatchback	RS 3 8Y	8YA	5	EU-AUDI-A3-8Y-RS3-SPORTBACK-PREFL-01	HIGH	8YA五门RS 3 Sportback，2024改款前专用宽体外廓。	READY
149409	149409	Sedan	RS 3 8Y	8YS	4	EU-AUDI-A3-8Y-RS3-SEDAN-PREFL-01	HIGH	8YS四门RS 3 Sedan，2024改款前专用宽体外廓。	READY
151160	151160	Hatchback	RS 3 8Y	8YA	5	EU-AUDI-A3-8Y-RS3-SPORTBACK-PREFL-01	HIGH	8YA五门RS 3 Sportback，2024改款前专用宽体外廓。	READY
11268	11268	Hatchback	S3 8L	8L1	3	EU-AUDI-A3-8L-S3-HATCHBACK-01	HIGH	8L1三门S3外廓；前后期三维一致。	READY
50895_prefl	50895	Sedan	S3 8V	8VS	4	EU-AUDI-A3-8VS-S3-SEDAN-PREFL-01	HIGH	8VS四门S3 Sedan，改款前专用外廓。	READY
50895_facelift	50895	Sedan	S3 8V	8VM	4	EU-AUDI-A3-8VM-S3-SEDAN-FACELIFT-01	HIGH	8VM四门S3 Sedan，2016改款专用外廓。	READY
54775	54775	Sedan	S3 8V	8VS	4	EU-AUDI-A3-8VS-S3-SEDAN-PREFL-01	HIGH	8VS四门S3 Sedan，改款前专用外廓。	READY
57437	57437	Hatchback	S3 8V	8V1	3	EU-AUDI-A3-8V-S3-HATCHBACK-PREFL-01	HIGH	8V1三门S3，改款前专用外廓。	READY
57438	57438	Hatchback	S3 8V	8V1	3	EU-AUDI-A3-8V-S3-HATCHBACK-PREFL-01	HIGH	8V1三门S3，改款前专用外廓。	READY
59244_prefl	59244	Hatchback	S3 8V	8VA	5	EU-AUDI-A3-8VA-S3-SPORTBACK-PREFL-01	HIGH	8VA五门S3 Sportback，改款前专用外廓。	READY
59244_facelift	59244	Hatchback	S3 8V	8VF	5	EU-AUDI-A3-8VF-S3-SPORTBACK-FACELIFT-01	HIGH	8VF五门S3 Sportback，2016改款专用外廓。	READY
59631	59631	Hatchback	S3 8V	8VA	5	EU-AUDI-A3-8VA-S3-SPORTBACK-PREFL-01	HIGH	8VA五门S3 Sportback，改款前专用外廓。	READY
100931_prefl	100931	Convertible	S3 8V	8V7	2	EU-AUDI-A3-8V7-S3-CABRIOLET-PREFL-01	HIGH	8V7双门S3 Cabriolet，改款前专用外廓。	READY
100931_facelift	100931	Convertible	S3 8V	8VE	2	EU-AUDI-A3-8VE-S3-CABRIOLET-FACELIFT-01	HIGH	8VE双门S3 Cabriolet，2016改款专用外廓。	READY
106371	106371	Hatchback	S3 8V	8V1	3	EU-AUDI-A3-8V-S3-HATCHBACK-PREFL-01	HIGH	8V1三门S3，改款前专用外廓。	READY
106376	106376	Sedan	S3 8V	8VS	4	EU-AUDI-A3-8VS-S3-SEDAN-PREFL-01	HIGH	8VS四门S3 Sedan，改款前专用外廓。	READY
106381	106381	Hatchback	S3 8V	8VA	5	EU-AUDI-A3-8VA-S3-SPORTBACK-PREFL-01	HIGH	8VA五门S3 Sportback，改款前专用外廓。	READY
106383	106383	Convertible	S3 8V	8V7	2	EU-AUDI-A3-8V7-S3-CABRIOLET-PREFL-01	HIGH	8V7双门S3 Cabriolet，改款前专用外廓。	READY
108249_prefl	108249	Sedan	S3 8V	8VS	4	EU-AUDI-A3-8VS-S3-SEDAN-PREFL-01	HIGH	8VS四门S3 Sedan，改款前专用外廓。	READY
108249_facelift	108249	Sedan	S3 8V	8VM	4	EU-AUDI-A3-8VM-S3-SEDAN-FACELIFT-01	HIGH	8VM四门S3 Sedan，2016改款专用外廓。	READY
120607	120607	Hatchback	S3 8V	8VK	3	EU-AUDI-A3-8V-S3-HATCHBACK-FACELIFT-01	HIGH	8VK三门S3，2016改款专用外廓。	READY
120608	120608	Hatchback	S3 8V	8VF	5	EU-AUDI-A3-8VF-S3-SPORTBACK-FACELIFT-01	HIGH	8VF五门S3 Sportback，2016改款专用外廓。	READY
120609	120609	Sedan	S3 8V	8VM	4	EU-AUDI-A3-8VM-S3-SEDAN-FACELIFT-01	HIGH	8VM四门S3 Sedan，2016改款专用外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_601-700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A3-8P-HATCHBACK-PREFL-01	4203	1765	1421	Auto-Data Audi A3 8P technical specifications	https://www.auto-data.net/en/audi-a3-8p-2.0-tdi-16v-140hp-4190
EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2005-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005 technical specifications	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-generation-8936
EU-AUDI-A3-8PA-SPORTBACK-PREFL-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8pa-generation-1067
EU-AUDI-A3-8P-HATCHBACK-FACELIFT-2008-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008 technical specifications	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-generation-5194
EU-AUDI-A3-8PA-SPORTBACK-FACELIFT-2008-01	4292	1765	1423	Auto-Data Audi A3 Sportback 8PA facelift 2008 technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8pa-facelift-2008-generation-5196
EU-AUDI-A3-8V-SEDAN-PREFL-01	4456	1796	1416	Automobile-Catalog 2014 Audi A3 Limousine technical data	https://www.automobile-catalog.com/car/2014/1916795/audi_a3_limousine_sedan_1_4_tfsi_cod_s-tronic.html
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Automobile-Catalog 2016 Audi A3 Limousine technical data	https://www.automobile-catalog.com/car/2016/2502575/audi_a3_limousine_1_4_tfsi_150_cod_s-tronic.html
EU-AUDI-A3-8V-SPORTBACK-PREFL-01	4310	1785	1425	Auto-Data Audi A3 Sportback 8V technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8v-1.4-tfsi-125hp-s-tronic-23123
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Auto-Data Audi A3 Sportback 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-40-tfsi-190hp-s-tronic-52331
EU-AUDI-A3-8V-HATCHBACK-PREFL-01	4237	1777	1421	Auto-Data Audi A3 8V technical specifications	https://www.auto-data.net/en/audi-a3-8v-1.2-tfsi-105hp-start-stop-26318
EU-AUDI-A3-8V-HATCHBACK-FACELIFT-01	4241	1777	1424	Auto-Data Audi A3 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-a3-8v-facelift-2016-generation-4776
EU-AUDI-A3-8V-CABRIOLET-PREFL-01	4421	1793	1409	Automobile-Catalog 2015 Audi A3 Cabriolet technical data	https://www.automobile-catalog.com/car/2015/1960640/audi_a3_cabriolet_1_8_tfsi_s-tronic.html
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409	Automobile-Catalog 2017 Audi A3 Cabriolet technical data	https://www.automobile-catalog.com/car/2017/2502725/audi_a3_cabriolet_1_4_tfsi_115.html
EU-AUDI-A3-8Y-SEDAN-FACELIFT-2024-01	4504	1816	1417	Auto-Data Audi A3 Sedan 8Y facelift 2024 technical specifications	https://www.auto-data.net/en/audi-a3-sedan-8y-facelift-2024-35-tfsi-150hp-52194
EU-AUDI-A3-8Y-SPORTBACK-FACELIFT-2024-01	4352	1816	1441	Auto-Data Audi A3 Sportback 8Y facelift 2024 technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8y-facelift-2024-35-tfsi-150hp-52191
EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	4343	1816	1449	Auto-Data Audi A3 Sportback 8Y 35 TDI technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8y-35-tdi-150hp-49020
EU-AUDI-A3-8Y-SEDAN-PREFL-01	4495	1816	1425	Auto-Data Audi A3 Sedan 8Y 35 TFSI technical specifications	https://www.auto-data.net/en/audi-a3-sedan-8y-35-tfsi-150hp-39703
EU-AUDI-A3-8V-SPORTBACK-ETRON-FACELIFT-01	4311	1785	1426	Auto-Data Audi A3 Sportback 8V facelift 40 e-tron technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-40-e-tron-1.4-tfsi-204hp-plug-in-hybrid-s-tronic-32672
EU-AUDI-A3-8Y-SPORTBACK-PHEV-FACELIFT-2024-01	4352	1816	1451	Auto-Data Audi A3 Sportback 8Y facelift 2024 40 TFSI e technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8y-facelift-2024-40-tfsi-e-204hp-plug-in-hybrid-s-tronic-52953
EU-AUDI-A3-8Y-SPORTBACK-PHEV-PREFL-01	4343	1816	1458	Auto-Data Audi A3 Sportback 8Y 40 TFSI e technical specifications	https://www.auto-data.net/en/audi-a3-sportback-8y-40-tfsi-e-204hp-plug-in-hybrid-s-tronic-41343
EU-AUDI-A3-8PA-RS3-SPORTBACK-01	4302	1794	1402	Audi UK RS 3 Sportback Technical Data	https://press.audi.co.uk/assets/documents/original/12016-AudiUK00000104RS3SportbackTechnicalData.pdf
EU-AUDI-A3-8VA-RS3-SPORTBACK-PREFL-01	4343	1800	1411	Audi UK RS 3 Sportback Technical Data	https://press.audi.co.uk/assets/documents/original/12064-AudiUK00000312AudiRS3Sportback25.pdf
EU-AUDI-A3-8VF-RS3-SPORTBACK-FACELIFT-01	4335	1800	1411	Audi UK RS 3 Sportback Technical Data	https://press.audi.co.uk/assets/documents/original/12143-AudiUK00018633AudiRS3Sportback25.pdf
EU-AUDI-A3-8VM-RS3-SEDAN-FACELIFT-01	4479	1802	1397	Audi UK RS 3 Saloon Technical Data	https://press.audi.co.uk/assets/documents/original/12241-AudiUK00017565AudiRS3SaloonTechnical.pdf
EU-AUDI-A3-8Y-RS3-SEDAN-PREFL-01	4542	1851	1412	Audi MediaCenter RS 3 Sedan technical data	https://www.audi-mediacenter.com/system/production/car_motorizations/468/file_en/1d135b0858d0dbde3c70b0690ae8652197730017/eTD-Audi-RS3-Sedan-TFSI_231027.pdf?1698933729=&disposition=attachment
EU-AUDI-A3-8Y-RS3-SPORTBACK-PREFL-01	4389	1851	1436	Audi MediaCenter RS 3 Sportback technical data	https://www.audi-mediacenter.com/system/production/car_motorizations/241/file_en/28776b93cf213d6a3c2e4336e62484200208389e/eTD-Audi-RS3-Sportback-TFSI_231027.pdf?1698933692=&disposition=attachment
EU-AUDI-A3-8L-S3-HATCHBACK-01	4159	1763	1415	Audi UK S3 225bhp Technical Specification	https://press.audi.co.uk/assets/documents/original/11660-AudiUK00001906S3225bhpTechnicalSpecification.pdf
EU-AUDI-A3-8VS-S3-SEDAN-PREFL-01	4469	1796	1392	Auto-Data Audi S3 Sedan 8V technical specifications	https://www.auto-data.net/en/audi-s3-sedan-8v-generation-4080
EU-AUDI-A3-8VM-S3-SEDAN-FACELIFT-01	4466	1796	1392	Auto-Data Audi S3 Sedan 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-s3-sedan-8v-facelift-2016-generation-4780
EU-AUDI-A3-8V-S3-HATCHBACK-PREFL-01	4254	1777	1401	Auto-Data Audi S3 8V technical specifications	https://www.auto-data.net/en/audi-s3-8v-generation-3991
EU-AUDI-A3-8VA-S3-SPORTBACK-PREFL-01	4324	1785	1404	Auto-Data Audi S3 Sportback 8V technical specifications	https://www.auto-data.net/en/audi-s3-sportback-8v-generation-4017
EU-AUDI-A3-8VF-S3-SPORTBACK-FACELIFT-01	4322	1785	1404	Auto-Data Audi S3 Sportback 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-s3-sportback-8v-facelift-2016-generation-4782
EU-AUDI-A3-8V7-S3-CABRIOLET-PREFL-01	4434	1793	1388	Auto-Data Audi S3 Cabriolet 8V technical specifications	https://www.auto-data.net/en/audi-s3-cabriolet-8v-generation-4638
EU-AUDI-A3-8VE-S3-CABRIOLET-FACELIFT-01	4431	1793	1388	Auto-Data Audi S3 Cabriolet 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-s3-cabriolet-8v-facelift-2016-generation-4779
EU-AUDI-A3-8V-S3-HATCHBACK-FACELIFT-01	4252	1777	1401	Auto-Data Audi S3 8V facelift 2016 technical specifications	https://www.auto-data.net/en/audi-s3-8v-facelift-2016-generation-4781
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_601-700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://allegro.pl/produkt/dpa-88071887402-kratka-wentylacyjna-zderzak-11bd8ab2-70dc-4a45-bc97-27724536e5be?utm_source=chatgpt.com "DPA 88071887402 Kratka wentylacyjna, zderzak, 6936397465822 • Cena • Opinie - Allegro"
[2]: https://press.audi.co.uk/assets/documents/original/11660-AudiUK00001906S3225bhpTechnicalSpecification.pdf "https://press.audi.co.uk/assets/documents/original/11660-AudiUK00001906S3225bhpTechnicalSpecification.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（870 行）
- 累计尺寸组：dimension_groups_final.tsv（354 行）

