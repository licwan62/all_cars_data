# 任务：left18448 第 9701-9800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0098__4717c83f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9701-9800 行

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
left18448 第 9701-9800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	4937	1881	1418
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	4953	1881	1419

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	Cls	CLS 220 Bluetec / D	Kombi	Heckantrieb	Diesel	May 2014	Dec 2017	106302
Mercedes-benz	Cls	CLS 250 Bluetec / D 4-matic	Coupe	Allrad	Diesel	May 2014	Dec 2017	106296
Mercedes-benz	Cls	CLS 250 Bluetec / D 4-matic	Kombi	Allrad	Diesel	May 2014	Dec 2017	106303
Mercedes-benz	Cls	CLS 250 CDI / Bluetec / D	Kombi	Heckantrieb	Diesel	Oct 2012	Dec 2017	57247
Mercedes-benz	Cls	CLS 300 D 4-matic	Coupe	Allrad	Diesel/Elektro	Apr 2021	-	143725
Mercedes-benz	Cls	CLS 320 CDI	Coupe	Heckantrieb	Diesel	Jan 2005	Dec 2010	18962
Mercedes-benz	Cls	CLS 320 CDI	Coupe	Heckantrieb	Diesel	Jan 2005	Dec 2010	54940
Mercedes-benz	Cls	CLS 350	Coupe	Heckantrieb	Benzin	Oct 2004	Dec 2010	17965
Mercedes-benz	Cls	CLS 350	Kombi	Heckantrieb	Benzin	Oct 2012	Aug 2014	57243
Mercedes-benz	Cls	CLS 350 Bluetec / D	Coupe	Heckantrieb	Diesel	Feb 2013	Dec 2017	59483
Mercedes-benz	Cls	CLS 350 Bluetec / D	Coupe	Heckantrieb	Diesel	Jun 2014	Dec 2017	106297
Mercedes-benz	Cls	CLS 350 Bluetec / D	Kombi	Heckantrieb	Diesel	May 2014	Dec 2017	106304
Mercedes-benz	Cls	CLS 350 Bluetec / D 4-matic	Coupe	Allrad	Diesel	Feb 2013	Dec 2017	59484
Mercedes-benz	Cls	CLS 350 Bluetec / D 4-matic	Kombi	Allrad	Diesel	May 2014	Dec 2017	106305
Mercedes-benz	Cls	CLS 350 CDI / D	Kombi	Heckantrieb	Diesel	Oct 2012	Aug 2014	57249
Mercedes-benz	Cls	CLS 350 CDI / D 4-matic	Coupe	Allrad	Diesel	Sep 2011	Aug 2014	11394
Mercedes-benz	Cls	CLS 350 CDI / D 4-matic	Kombi	Allrad	Diesel	Oct 2012	Aug 2014	57250
Mercedes-benz	Cls	CLS 350 D 4-matic	Coupe	Allrad	Diesel	Apr 2015	Dec 2017	112369
Mercedes-benz	Cls	CLS 350 D 4-matic	Kombi	Allrad	Diesel	Apr 2015	Dec 2017	112372
Mercedes-benz	Cls	CLS 400	Coupe	Heckantrieb	Benzin	May 2014	Dec 2017	106298
Mercedes-benz	Cls	CLS 400	Kombi	Heckantrieb	Benzin	May 2014	Dec 2017	106307
Mercedes-benz	Cls	CLS 400	Coupe	Heckantrieb	Benzin	Jul 2014	Dec 2017	107644
Mercedes-benz	Cls	CLS 400	Kombi	Heckantrieb	Benzin	Jul 2014	Dec 2017	107651
Mercedes-benz	Cls	CLS 400 4-matic	Coupe	Allrad	Benzin	May 2014	Dec 2017	106299
Mercedes-benz	Cls	CLS 400 4-matic	Kombi	Allrad	Benzin	May 2014	Dec 2017	106308
Mercedes-benz	Cls	CLS 400 4-matic	Coupe	Allrad	Benzin	Jul 2014	Dec 2017	107650
Mercedes-benz	Cls	CLS 400 4-matic	Kombi	Allrad	Benzin	Jul 2014	Dec 2017	107653
Mercedes-benz	Cls	CLS 500	Coupe	Heckantrieb	Benzin	Oct 2004	Dec 2010	17966
Mercedes-benz	Cls	CLS 500	Kombi	Heckantrieb	Benzin	Oct 2012	Dec 2017	57244
Mercedes-benz	Cls	CLS 500 4-matic	Coupe	Allrad	Benzin	Sep 2011	Dec 2017	11393
Mercedes-benz	Cls	CLS 500 4-matic	Kombi	Allrad	Benzin	Oct 2012	Dec 2017	57245
Mercedes-benz	Cls	CLS 55 AMG	Coupe	Heckantrieb	Benzin	Jan 2005	Dec 2010	18233
Mercedes-benz	Cls	CLS 63 AMG	Coupe	Heckantrieb	Benzin	Jan 2011	Dec 2017	14920
Mercedes-benz	Cls	CLS 63 AMG	Kombi	Heckantrieb	Benzin	Oct 2012	Dec 2017	57246
Mercedes-benz	Cls	CLS 63 AMG	Kombi	Heckantrieb	Benzin	May 2013	Dec 2017	59014
Mercedes-benz	Cls	CLS 63 AMG	Coupe	Heckantrieb	Benzin	Feb 2013	Dec 2017	59443
Mercedes-benz	Cls	CLS 63 AMG	Kombi	Heckantrieb	Benzin	Feb 2013	Dec 2017	59446
Mercedes-benz	Cls	CLS 63 AMG 4-matic	Kombi	Allrad	Benzin	May 2013	Dec 2017	59015
Mercedes-benz	Cls	CLS 63 AMG 4-matic	Kombi	Allrad	Benzin	Feb 2013	Dec 2017	59016
Mercedes-benz	Cls	CLS 63 AMG 4-matic	Coupe	Allrad	Benzin	May 2013	Dec 2017	59017
Mercedes-benz	Cls	CLS 63 AMG 4-matic	Coupe	Allrad	Benzin	Feb 2013	Dec 2017	59018
Mercedes-benz	E-Klasse	AMG E 43 4-matic	Stufenheck	Allrad	Benzin	Jul 2016	May 2018	120741
Mercedes-benz	E-Klasse	AMG E 63 4-matic+	Stufenheck	Allrad	Benzin	Jan 2017	Nov 2021	125169
Mercedes-benz	E-Klasse	AMG E 63 4-matic+	Kombi	Allrad	Benzin	May 2017	Oct 2023	127339
Mercedes-benz	E-Klasse	AMG E 63 S 4-matic+	Stufenheck	Allrad	Benzin	Jan 2017	Oct 2023	125170
Mercedes-benz	E-Klasse	AMG E 63 S 4-matic+	Kombi	Allrad	Benzin	May 2017	Oct 2023	127340
Mercedes-benz	E-Klasse	E 180	Stufenheck	Heckantrieb	Benzin	Jan 2016	Jun 2019	126006
Mercedes-benz	E-Klasse	E 180	Stufenheck	Heckantrieb	Benzin	Jul 2019	Oct 2023	147702
Mercedes-benz	E-Klasse	E 180	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2023	-	156038
Mercedes-benz	E-Klasse	E 200	Cabriolet	Heckantrieb	Benzin	Mar 2013	Dec 2016	59030
Mercedes-benz	E-Klasse	E 200	Coupe	Heckantrieb	Benzin	Jun 2013	Dec 2016	59047
Mercedes-benz	E-Klasse	E 200	Kombi	Heckantrieb	Benzin	Nov 2012	Dec 2016	59461
Mercedes-benz	E-Klasse	E 200	Stufenheck	Heckantrieb	Benzin	Jan 2016	May 2019	118513
Mercedes-benz	E-Klasse	E 200	Kombi	Heckantrieb	Benzin	Jul 2016	Jun 2020	120722
Mercedes-benz	E-Klasse	E 200	Coupe	Heckantrieb	Benzin	Dec 2016	-	124820
Mercedes-benz	E-Klasse	E 200	Cabriolet	Heckantrieb	Benzin	Jun 2017	-	127635
Mercedes-benz	E-Klasse	E 200	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2023	-	155288
Mercedes-benz	E-Klasse	E 200	Kombi	Heckantrieb	Benzin/Elektro	Jul 2023	-	156002
Mercedes-benz	E-Klasse	E 200 4-matic	Stufenheck	Allrad	Benzin	Jul 2016	Jun 2019	120726
Mercedes-benz	E-Klasse	E 200 4-matic	Kombi	Allrad	Benzin	Jan 2017	Jun 2019	125163
Mercedes-benz	E-Klasse	E 200 4-matic	Coupe	Allrad	Benzin	Jun 2017	-	127680
Mercedes-benz	E-Klasse	E 200 4-matic	Stufenheck	Allrad	Benzin/Elektro	Jul 2023	-	156365
Mercedes-benz	E-Klasse	E 200 4-matic	Kombi	Allrad	Benzin/Elektro	Feb 2024	-	157584
Mercedes-benz	E-Klasse	E 200 CDI	Stufenheck	Heckantrieb	Diesel	Jun 1998	Mar 2002	10146
Mercedes-benz	E-Klasse	E 200 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	12580
Mercedes-benz	E-Klasse	E 200 CDI	Stufenheck	Heckantrieb	Diesel	Jul 2002	Dec 2008	16991
Mercedes-benz	E-Klasse	E 200 CDI	Stufenheck	Heckantrieb	Diesel	Jul 2002	Dec 2008	16992
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel	Jul 2016	Jun 2020	120746
Mercedes-benz	E-Klasse	E 200 D	Kombi	Heckantrieb	Diesel/Elektro	Nov 2024	-	800989
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel/Elektro	Nov 2024	-	800992
Mercedes-benz	E-Klasse	E 200 Kompressor	Stufenheck	Heckantrieb	Benzin	Aug 2000	Mar 2002	15061
Mercedes-benz	E-Klasse	E 200 Kompressor	Stufenheck	Heckantrieb	Benzin	Nov 2002	Dec 2008	17128
Mercedes-benz	E-Klasse	E 200 NGT	Stufenheck	Heckantrieb	Benzin/Erdgas (CNG)	Mar 2004	Dec 2008	17964
Mercedes-benz	E-Klasse	E 200 NGT	Stufenheck	Heckantrieb	Benzin/Erdgas (CNG)	Jul 2013	Dec 2015	100542
Mercedes-benz	E-Klasse	E 200 T Kompressor	Kombi	Heckantrieb	Benzin	Aug 2000	Mar 2003	15063
Mercedes-benz	E-Klasse	E 200 T Kompressor	Kombi	Heckantrieb	Benzin	Mar 2003	Jul 2009	17164
Mercedes-benz	E-Klasse	E 220 Bluetec	Stufenheck	Heckantrieb	Diesel	May 2014	Dec 2015	106309
Mercedes-benz	E-Klasse	E 220 Bluetec	Cabriolet	Heckantrieb	Diesel	May 2014	Dec 2016	106312
Mercedes-benz	E-Klasse	E 220 Bluetec	Coupe	Heckantrieb	Diesel	May 2014	Dec 2016	106314
Mercedes-benz	E-Klasse	E 220 Bluetec	Kombi	Heckantrieb	Diesel	May 2015	Dec 2016	116184
Mercedes-benz	E-Klasse	E 220 Bluetec 4-matic	Stufenheck	Allrad	Diesel	Jan 2015	Dec 2015	109458
Mercedes-benz	E-Klasse	E 220 Bluetec 4-matic	Kombi	Allrad	Diesel	Dec 2014	Dec 2016	109474
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Jun 1998	Jul 1999	10144
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2003	Dec 2008	11236
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	12583
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2002	Dec 2008	16594
Mercedes-benz	E-Klasse	E 220 CDI	Kombi	Heckantrieb	Diesel	Aug 2009	Aug 2014	53147
Mercedes-benz	E-Klasse	E 220 CDI	Cabriolet	Heckantrieb	Diesel	Feb 2010	Dec 2016	53201
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	54955
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	Jan 2009	Dec 2015	58601
Mercedes-benz	E-Klasse	E 220 CDI	Coupe	Heckantrieb	Diesel	Feb 2010	Dec 2014	107887
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel	May 1996	Mar 2002	11081
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel	Jan 2016	Oct 2023	118515
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel	Jan 2016	Oct 2023	118793
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel	Jul 2016	Oct 2023	120725
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel	Jul 2016	Oct 2023	121773
Mercedes-benz	E-Klasse	E 220 D	Coupe	Heckantrieb	Diesel	Dec 2016	-	124818
Mercedes-benz	E-Klasse	E 220 D	Coupe	Heckantrieb	Diesel	Dec 2016	-	127356
Mercedes-benz	E-Klasse	E 220 D	Cabriolet	Heckantrieb	Diesel	Jun 2017	-	127634
Mercedes-benz	E-Klasse	E 220 D	Cabriolet	Heckantrieb	Diesel	Jun 2017	-	127675


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 CLS 第一轮物理车身聚类，闭合 **C219 标准悬架、C219 CLS 500、C219 AMG、C218 改款前标准车身、X218 改款前标准车身**共 5 个新尺寸组。
* 已复用已有的 C218 Coupe facelift 与 X218 Shooting Brake facelift 两个尺寸组，未重复输出缓存尺寸。
* C219 的 320 CDI、350、500 和 AMG 在对应生产阶段的外廓已由 Mercedes-Benz Public Archive 闭合；其中 CLS 500 的 2008—2010 facelift 仍为 4913 × 1873 × 1390 mm。([marsClassic][1])
* C218/X218 改款前普通 350 CDI 后驱与四驱车型分别确认使用 4940 × 1881 × 1416 mm 和 4956 × 1881 × 1416 mm 外廓，可供同车身标准悬架柴油 Ktype 复用。([marsClassic][2])
* 暂未把 CLS 500、CLS 63 AMG 混入普通 C218/X218 组：官方资料显示 CLS 500 存在不同高度，CLS 63 AMG 资料还出现高度范围，需要下一轮独立闭合。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* 本轮形成 READY 映射：22 行
* 已闭合 Ktype：19
* 待处理/PENDING Ktype：81
* 当前引用尺寸组：7

  * 本轮首次创建：5
  * 复用既有缓存：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106302	106302	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
106296	106296	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106303	106303	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
57247_prefl	57247	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57247_facelift	57247	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
18962	18962	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓；facelift前三维不变。	READY
54940	54940	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓；facelift前三维不变。	READY
17965	17965	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓。	READY
59483_prefl	59483	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
59483_facelift	59483	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
106297	106297	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106304	106304	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
59484_prefl	59484	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
59484_facelift	59484	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
106305	106305	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
57249	57249	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
11394	11394	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	HIGH	C218改款前四门Coupe标准外廓。	READY
57250	57250	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
112369	112369	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
112372	112372	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
17966	17966	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-02	HIGH	C219 CLS 500 AIRMATIC外廓。	READY
18233	18233	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-AMG-01	MEDIUM	Ktype生产区间覆盖C219 AMG车型更替，但AMG物理外廓保持一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-C219-COUPE-01	4913	1873	1403	Mercedes-Benz Public Archive CLS 350 2004-2006;Mercedes-Benz Public Archive CLS 320 CDI 2005-2008;Mercedes-Benz Public Archive CLS 320 CDI 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-2004---2006-only-for-export-until-2010.xhtml?oid=192528692;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-320-CDI-2005---2008.xhtml?oid=192528691;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-320-CDI-2008---2010-from-042009-CLS-350-CDI.xhtml?oid=192528704
EU-MERCEDES-BENZ-CLS-C219-COUPE-02	4913	1873	1390	Mercedes-Benz Public Archive CLS 500 2004-2006;Mercedes-Benz Public Archive CLS 500 2006-2008;Mercedes-Benz Public Archive CLS 500 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2004---2006.xhtml?oid=192528694;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2006---2008.xhtml?oid=192528695;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2008---2010.xhtml?oid=192528707
EU-MERCEDES-BENZ-CLS-C219-COUPE-AMG-01	4915	1873	1389	Mercedes-Benz Public Archive CLS 55 AMG 2004-2006;Mercedes-Benz Public Archive CLS 63 AMG 2006-2008;Mercedes-Benz Public Archive CLS 63 AMG 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-55-AMG-2004---2006.xhtml?oid=192528696;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2006---2008.xhtml?oid=192528697;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2008---2010.xhtml?oid=192528708
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	4940	1881	1416	Mercedes-Benz Public Archive CLS 350 CDI 2010-2014;Mercedes-Benz Public Archive CLS 350 CDI 4MATIC 2011-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-BlueEFFICIENCY-2010---2014-from-032013-CLS-350-CDI.xhtml?oid=191274637;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-4MATIC-BlueEFFICIENCY-2011---2014-from-032013-CLS-350-CDI-4MATIC.xhtml?oid=191274638
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	4956	1881	1416	Mercedes-Benz Public Archive CLS 350 CDI Shooting Brake 2012-2014;Mercedes-Benz Public Archive CLS 350 CDI 4MATIC Shooting Brake 2012-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-BlueEFFICIENCY-2012---2014-from-032013-CLS-350-CDI.xhtml?oid=191336308;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-4MATIC-BlueEFFICIENCY-2012---2014-from-032013-CLS-350-CDI-4MATIC.xhtml?oid=191336309
```

## 下一步优先处理

1. 独立闭合 C218/X218 的 CLS 350 汽油、CLS 400、CLS 500 与 CLS 63 AMG，不误用普通悬架组。
2. 处理第三代 CLS C257 的 Ktype `143725`。
3. 完成剩余 CLS 后，按 W210/S210、W211/S211、W212/S212/C207/A207、W213/S213/C238/A238、W214/S214 对 E-Klasse 批量聚类。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-320-CDI-2008---2010-from-042009-CLS-350-CDI.xhtml?oid=192528704 "CLS 320 CDI, 2008 - 2010 (from 04.2009: CLS 350 CDI)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-BlueEFFICIENCY-2010---2014-from-032013-CLS-350-CDI.xhtml?oid=191274637 "CLS 350 CDI BlueEFFICIENCY, 2010 - 2014 (from 03.2013: CLS 350 CDI)"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-BlueEFFICIENCY-2010---2014-from-032013-CLS-500.xhtml?oid=191274642&utm_source=chatgpt.com "CLS 500 BlueEFFICIENCY, 2010 - 2014 (from 03.2013: CLS 500)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已将 8 个 CLS 400 Ktype 批量关联至现有 C218/X218 facelift 尺寸组；facelift Coupe 与 Shooting Brake 的三维分别与缓存的 `4937×1881×1418`、`4953×1881×1419` 完全一致。([汽车历史查询][1])
* 已完成 CLS 500 的改款边界拆分。改款前 C218 4MATIC 为 `4940×1881×1404`，新建 C218 pre-facelift 第 02 组；改款前 X218 后驱与四驱均为 `4956×1881×1421`，共用 X218 pre-facelift 第 02 组。([marsClassic][2])
* CLS 500 facelift 分支与现有缓存尺寸完全一致，直接复用，不重复建组。([汽车目录][3])
* 已闭合 C257 facelift 的 CLS 300 D 4MATIC，三维为 `4988×1890×1435`。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：38 行
* 已闭合 Ktype：32
* PENDING Ktype：68
* 当前引用尺寸组：10
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143725	143725	Coupe	CLS C257	C257	4	EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	HIGH	C257 facelift四门Coupe外廓。	READY
57243	57243	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
106298	106298	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106307	106307	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
107644	107644	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
107651	107651	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
106299	106299	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106308	106308	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
107650	107650	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
107653	107653	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
57244_prefl	57244	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57244_facelift	57244	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
11393_prefl	11393	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
11393_facelift	11393	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57245_prefl	57245	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57245_facelift	57245	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 facelift 2021 CLS 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-facelift-2021-cls-300d-265hp-mild-hybrid-4matic-9g-tronic-43348
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	4956	1881	1421	Mercedes-Benz Public Archive CLS 500 BlueEFFICIENCY Shooting Brake 2012-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-BlueEFFICIENCY-2012---2014-from-032013-CLS-500.xhtml?oid=191336311
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-02	4940	1881	1404	Mercedes-Benz Public Archive CLS 500 4MATIC BlueEFFICIENCY 2011-2014	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-500-4MATIC-BlueEFFICIENCY-2011---2014-ab-032013-CLS-500-4MATIC.xhtml?oid=191274643
```

## 下一步优先处理

1. 闭合 C218/X218 的 CLS 63 AMG 后驱、4MATIC 与 facelift 外廓分支。
2. CLS 全部完成后，按 W210/S210、W211/S211、W212/S212/C207/A207 聚类处理 E-Klasse。
3. 优先批量复用同代同车身缓存，仅对 AMG 外部套件、改款和不同车身形式首次建组。

推进信号：CONTINUE

[1]: https://www.automoli.com/en/vehicles/mercedes-benz/cls/cls-coupe-c218-facelift-2014-4374/?utm_source=chatgpt.com "Mercedes-Benz CLS coupe (C218 facelift, 2014)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-500-4MATIC-BlueEFFICIENCY-2011---2014-ab-032013-CLS-500-4MATIC.xhtml?oid=191274643 "
            CLS 500 4MATIC BlueEFFICIENCY, 2011 - 2014 (ab 03.2013: CLS 500 4MATIC)

    "
[3]: https://www.automobile-catalog.com/car/2015/2505275/mercedes-benz_cls_500_4matic.html?utm_source=chatgpt.com "2015 Mercedes-Benz CLS 500 4MATIC (aut. 9)"
[4]: https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-facelift-2021-cls-300d-265hp-mild-hybrid-4matic-9g-tronic-43348?utm_source=chatgpt.com "Specs of Mercedes-Benz CLS coupe (C257, facelift 2021) ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已拆分 9 个跨越 2014 改款的 CLS 63 AMG Ktype，并闭合全部改款前分支。
* C218 后驱 AMG 改款前三维确定为 `4996×1881×1406 mm`；X218 后驱 AMG 为 `5000×1881×1412 mm`。([汽车目录][1])
* C218 4MATIC AMG 改款前为 `4995×1881×1416 mm`；X218 4MATIC AMG 为 `5000×1881×1436 mm`。普通 AMG 与 S 版本在对应车身和驱动下三维一致，可共用尺寸组。([marsClassic][2])
* 改款后 C218 AMG 资料存在 `4937×1881×1418`、`4967×1881×1411` 和 `4967×1881×1431` 等冲突；X218 AMG 也存在 `4953×1881×1419` 与 `5000×1881×1412` 的冲突。本轮未猜测建组，相关 facelift 分支保持 PENDING。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：47 行
* 显式 PENDING 映射：9 行
* 完全闭合 Ktype：32
* 已部分闭合 Ktype：9
* 尚未开始处理 Ktype：59
* 尚未完全闭合 Ktype：68
* 已确认尺寸组：14
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14920_prefl	14920	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG外廓。	READY
14920_facelift	14920	Coupe	CLS C218	C218	4		LOW	改款后AMG Coupe三维来源存在实质冲突。	PENDING: 改款后AMG Coupe三维冲突待闭合
57246_prefl	57246	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
57246_facelift	57246	Wagon	CLS X218	X218	5		LOW	改款后AMG Shooting Brake三维来源存在实质冲突。	PENDING: 改款后AMG Shooting Brake三维冲突待闭合
59014_prefl	59014	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
59014_facelift	59014	Wagon	CLS X218	X218	5		LOW	改款后AMG Shooting Brake三维来源存在实质冲突。	PENDING: 改款后AMG Shooting Brake三维冲突待闭合
59443_prefl	59443	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG外廓。	READY
59443_facelift	59443	Coupe	CLS C218	C218	4		LOW	改款后AMG Coupe三维来源存在实质冲突。	PENDING: 改款后AMG Coupe三维冲突待闭合
59446_prefl	59446	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
59446_facelift	59446	Wagon	CLS X218	X218	5		LOW	改款后AMG Shooting Brake三维来源存在实质冲突。	PENDING: 改款后AMG Shooting Brake三维冲突待闭合
59015_prefl	59015	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG Shooting Brake外廓。	READY
59015_facelift	59015	Wagon	CLS X218	X218	5		LOW	改款后4MATIC AMG Shooting Brake三维来源存在实质冲突。	PENDING: 改款后4MATIC AMG Shooting Brake三维冲突待闭合
59016_prefl	59016	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG Shooting Brake外廓。	READY
59016_facelift	59016	Wagon	CLS X218	X218	5		LOW	改款后4MATIC AMG Shooting Brake三维来源存在实质冲突。	PENDING: 改款后4MATIC AMG Shooting Brake三维冲突待闭合
59017_prefl	59017	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG外廓。	READY
59017_facelift	59017	Coupe	CLS C218	C218	4		LOW	改款后4MATIC AMG Coupe三维来源存在实质冲突。	PENDING: 改款后4MATIC AMG Coupe三维冲突待闭合
59018_prefl	59018	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG外廓。	READY
59018_facelift	59018	Coupe	CLS C218	C218	4		LOW	改款后4MATIC AMG Coupe三维来源存在实质冲突。	PENDING: 改款后4MATIC AMG Coupe三维冲突待闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	4996	1881	1406	Mercedes-Benz Public Archive CLS 63 AMG 2011-2014;Automobile-Catalog 2012 Mercedes-Benz CLS 63 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2011---2014.xhtml?oid=191274644;https://www.automobile-catalog.com/car/2012/1557350/mercedes-benz_cls_63_amg.html
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	5000	1881	1412	Mercedes-Benz Public Archive CLS 63 AMG Shooting Brake 2012-2014;Automobile-Catalog 2013 Mercedes-Benz CLS 63 AMG Shooting Brake	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2012---2014.xhtml?oid=191336313;https://www.automobile-catalog.com/car/2013/1781960/mercedes-benz_cls_63_amg_shooting_brake.html
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	4995	1881	1416	Mercedes-Benz Public Archive CLS 63 AMG 4MATIC 2013-2014;Mercedes-Benz Public Archive CLS 63 AMG S 4MATIC 2013-2014	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-63-AMG-4MATIC-2013---2014.xhtml?oid=191274645;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-S-4MATIC-2013---2014.xhtml?oid=191274646
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	5000	1881	1436	Mercedes-Benz Public Archive CLS 63 AMG 4MATIC Shooting Brake 2013-2014;Mercedes-Benz Public Archive CLS 63 AMG S 4MATIC Shooting Brake 2013-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-4MATIC-2013---2014.xhtml?oid=191336314;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-S-4MATIC-2013---2014.xhtml?oid=191336315
```

## 下一步优先处理

1. 仅针对 C218/X218 facelift AMG 冲突，按后驱、4MATIC、Coupe、Shooting Brake 四个边界寻找同市场厂商规格，闭合本轮 9 个 PENDING 分支。
2. CLS 全部闭合后，批量处理 E-Klasse 的 W210/S210 与 W211/S211，优先复用同代同车身尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/1557350/mercedes-benz_cls_63_amg.html?utm_source=chatgpt.com "2012 Mercedes-Benz CLS 63 AMG Specs Review (386 kW ..."
[2]: https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-63-AMG-4MATIC-2013---2014.xhtml?oid=191274645 "
            CLS 63 AMG 4MATIC, 2013 - 2014

    "
[3]: https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-amg-cls-63-v8-557hp-amg-speedshift-mct-20858 "Mercedes-Benz CLS coupe (C218 facelift, 2014) AMG CLS 63 V8 (557 Hp) AMG SPEEDSHIFT MCT | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合上一轮 9 个 CLS 63 AMG facelift PENDING 分支，按 Coupe/Shooting Brake、后驱/4MATIC 建立 4 个尺寸组。C218 后驱与 4MATIC 高度分别为 1411 mm、1431 mm；X218 后驱与 4MATIC 高度分别为 1413 mm、1436 mm。([CARLEXANDRIA Auto Broschüren Kataloge][1])
* 已完成早期 E-Klasse 的 W210/S210、W211/S211 聚类，15 个 Ktype 全部闭合；跨 1999 年或 2006 年改款的 Ktype 按物理外廓拆分。([marsClassic][2])
* 本轮首次创建 11 个尺寸组，未重复输出或重建既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全闭合 Ktype：56
* 尚未闭合 Ktype：44
* READY 映射：78 行
* 已确认尺寸组：25
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14920_facelift	14920	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	HIGH	2014改款后后驱AMG四门Coupe外廓。	READY
57246_facelift	57246	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	2014改款后后驱AMG五门Shooting Brake外廓。	READY
59014_facelift	59014	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	2014改款后后驱AMG五门Shooting Brake外廓。	READY
59443_facelift	59443	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	HIGH	2014改款后后驱AMG四门Coupe外廓。	READY
59446_facelift	59446	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	2014改款后后驱AMG五门Shooting Brake外廓。	READY
59015_facelift	59015	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	HIGH	2014改款后4MATIC AMG五门Shooting Brake外廓。	READY
59016_facelift	59016	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	HIGH	2014改款后4MATIC AMG五门Shooting Brake外廓。	READY
59017_facelift	59017	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	HIGH	2014改款后4MATIC AMG四门Coupe外廓。	READY
59018_facelift	59018	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	HIGH	2014改款后4MATIC AMG四门Coupe外廓。	READY
10146_prefl	10146	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越1999改款，按物理外廓拆分。	READY
10146_facelift	10146	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越1999改款，按物理外廓拆分。	READY
12580	12580	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
16991_prefl	16991	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
16991_facelift	16991	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
16992_prefl	16992	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
16992_facelift	16992	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
15061	15061	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
17128_prefl	17128	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
17128_facelift	17128	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
17964_prefl	17964	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
17964_facelift	17964	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
15063	15063	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-CLASS-S210-WAGON-FACELIFT-01	HIGH	S210 facelift五门Wagon外廓。	READY
17164_prefl	17164	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
17164_facelift	17164	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
10144	10144	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	HIGH	W210改款前四门Sedan外廓。	READY
11236_prefl	11236	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
11236_facelift	11236	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
12583	12583	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
16594_prefl	16594	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
16594_facelift	16594	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按物理外廓拆分。	READY
54955	54955	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
11081	11081	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	MEDIUM	E 220 D对应W210改款前四门Sedan外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	4967	1881	1411	Auto-Data Mercedes-Benz CLS C218 facelift AMG CLS 63 RWD	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-amg-cls-63-v8-557hp-amg-speedshift-mct-20858
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	5000	1881	1413	Mercedes-AMG Driving Performance CLS 63 AMG Shooting Brake brochure	https://mercedes.ekka.gr/amg/pdf/the_world_of_mercedes-amg.pdf
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	5000	1881	1436	Mercedes-AMG Driving Performance CLS 63 AMG 4MATIC Shooting Brake brochure	https://mercedes.ekka.gr/amg/pdf/the_world_of_mercedes-amg.pdf
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	4967	1881	1431	Auto-Data Mercedes-Benz CLS C218 facelift AMG CLS 63 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-amg-cls-63-v8-557hp-4matic-amg-speedshift-mct-20918
EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	4795	1799	1436	Mercedes-Benz Public Archive E 220 CDI W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=5325
EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	4818	1799	1440	Mercedes-Benz Public Archive E 200 CDI W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-CDI.xhtml?oid=5344
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	4818	1822	1450	Mercedes-Benz Public Archive E 200 CDI W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-CDI.xhtml?oid=5368
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	4856	1822	1483	Mercedes-Benz Public Archive E 220 CDI W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=2461815
EU-MERCEDES-BENZ-E-CLASS-S210-WAGON-FACELIFT-01	4816	1799	1505	Mercedes-Benz Public Archive E 200 Kompressor station wagon S210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Kompressor-station-wagon.xhtml?oid=5427
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFACELIFT-01	4850	1822	1496	Mercedes-Benz Public Archive E 200 Kompressor station wagon S211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Kompressor-station-wagon.xhtml?oid=5464
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 200 Compressor station wagon S211 facelift	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Compressor-station-wagon.xhtml?oid=2461882
```

## 下一步优先处理

1. 批量闭合 W212/S212 facelift 的 Sedan、Wagon、Coupe、Cabriolet Ktype。
2. 随后处理 W213/S213/C238/A238，并单独核对 AMG E 43、E 63 的外部套件与高度差异。
3. 最后处理 W214/S214 及 2024 年后的 E 200 D Ktype。

推进信号：CONTINUE

[1]: https://carlexandria.com/download/158273/?tmstv=1771697412&v=158274&utm_source=chatgpt.com "Driving Performance."
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-CDI.xhtml?oid=5344 "E 200 CDI"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 W212/S212/C207/A207 共 **14 个 Ktype**，新增 19 行 READY 映射；其中 5 个跨越 2013 年改款的 Ktype 已拆分为 `prefl`、`facelift` 两个物理分支。
* W212/S212 的后驱与 4MATIC 车型存在高度差异，已分别建组：W212 facelift 后驱为 1475 mm、4MATIC 为 1490 mm；S212 facelift 后驱为 1507 mm、4MATIC 为 1509 mm。([marsClassic][1])
* C207/A207 改款前后长度由 4698 mm 增至 4703 mm；Coupe 与 Convertible 的高度分别保持 1397 mm、1398 mm，因此按车身形式及改款边界独立建组。([marsClassic][2])
* 本轮首次创建 10 个尺寸组；未重复输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全闭合 Ktype：70
* 尚待处理 Ktype：30
* READY 映射：97 行
* 已确认尺寸组：35
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59030	59030	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207 facelift双门Convertible外廓。	READY
59047	59047	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	C207 facelift双门Coupe外廓。	READY
59461_prefl	59461	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
59461_facelift	59461	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
100542	100542	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	W212 facelift四门Sedan后驱外廓。	READY
106309	106309	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	W212 facelift四门Sedan后驱外廓。	READY
106312	106312	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207 facelift双门Convertible外廓。	READY
106314	106314	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	C207 facelift双门Coupe外廓。	READY
116184	116184	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	S212 facelift五门Wagon后驱外廓。	READY
109458	109458	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-FACELIFT-01	HIGH	W212 facelift四门Sedan 4MATIC外廓。	READY
109474	109474	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-4MATIC-FACELIFT-01	HIGH	S212 facelift五门Wagon 4MATIC外廓。	READY
53147_prefl	53147	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53147_facelift	53147	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53201_prefl	53201	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53201_facelift	53201	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
58601_prefl	58601	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
58601_facelift	58601	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
107887_prefl	107887	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
107887_facelift	107887	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Auto-Data Mercedes-Benz E-Class Cabrio A207 facelift E 220 BlueTEC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-facelift-2013-e-220-bluetec-170hp-43870
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data Mercedes-Benz E-Class Coupe C207 facelift E 220 BlueTEC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-e-220-bluetec-170hp-43883
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	4895	1854	1512	Mercedes-Benz E-Class Saloon and Estate official brochure 2009	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	4905	1854	1507	Mercedes-Benz E-Class official brochure 2014	https://baaf-ks.com/upload/models/eclass/brosure/eclassw212_brosur.pdf
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	4879	1854	1475	Mercedes-Benz Public Archive E 220 BlueTEC 2014-2016;Mercedes-Benz Public Archive E 200 Natural Gas Drive 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-2014---2016.xhtml?oid=188541008;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Natural-Gas-Drive-2013---2015.xhtml?oid=188541026
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-FACELIFT-01	4879	1854	1490	Mercedes-Benz Public Archive E 220 BlueTEC 4MATIC 2015-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-4MATIC-2015---2016.xhtml?oid=188541009
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-4MATIC-FACELIFT-01	4905	1854	1509	Mercedes-Benz Public Archive E 220 BlueTEC 4MATIC station wagon 2015-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-4MATIC-2015---2016.xhtml?oid=188837494
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFACELIFT-01	4698	1786	1398	Auto-Data Mercedes-Benz E-Class Cabrio A207 E 220 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-e-220-cdi-blueefficiency-170hp-17384
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFACELIFT-01	4868	1854	1470	Mercedes-Benz E-Class Saloon and Estate official brochure 2009	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFACELIFT-01	4698	1786	1397	Mercedes-Benz Public Archive E 220 CDI BlueEFFICIENCY 2010-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-BlueEFFICIENCY-2010---2013.xhtml?oid=188954779
```

## 下一步优先处理

1. 批量闭合 W213/S213 标准 Sedan、Wagon 的改款前后及后驱/4MATIC高度边界。
2. 闭合 C238/A238 Coupe、Convertible，并处理跨改款生产区间。
3. 单独处理 AMG E 43、E 63、E 63 S 外部套件，最后闭合 W214/S214 的 2023—2024 年后车型。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-2014---2016.xhtml?oid=188541008&utm_source=chatgpt.com "E 220 BlueTEC, 2014 - 2016 - Mercedes Benz Archive"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-BlueEFFICIENCY-2010---2013.xhtml?oid=188954779 "E 220 CDI BlueEFFICIENCY, 2010 - 2013"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9701-9800_ktype_dimension_mapping_final.tsv
- left18448_9701-9800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 W213/S213、C238/A238、W214/S214 标准车身及 AMG E 63/E 63 S 分支；跨 2020 年改款的车型已按实际外廓拆分。([汽车数据网][1])
* 非 S 版 AMG E 63 仅落入已确认的改款前尺寸组；E 63 S 根据改款前规格及 Mercedes-Benz USA 改款后官方规格分别建组。([汽车数据网][2])
* 已完成轻量机械检查：表头固定、`id` 和尺寸组 ID 唯一、引用全部闭合、尺寸和来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：142 行
* PENDING 映射：0
* DIMENSION_GROUP：52 组
* 缺失映射引用：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106302	106302	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
106296	106296	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106303	106303	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
57247_prefl	57247	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57247_facelift	57247	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
143725	143725	Coupe	CLS C257	C257	4	EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	HIGH	C257 facelift四门Coupe外廓。	READY
18962	18962	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓；facelift前三维不变。	READY
54940	54940	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓；facelift前三维不变。	READY
17965	17965	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-01	HIGH	C219四门Coupe标准外廓。	READY
57243	57243	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
59483_prefl	59483	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
59483_facelift	59483	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
106297	106297	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106304	106304	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
59484_prefl	59484	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
59484_facelift	59484	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
106305	106305	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
57249	57249	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
11394	11394	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	HIGH	C218改款前四门Coupe标准外廓。	READY
57250	57250	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	HIGH	X218改款前五门Shooting Brake标准外廓。	READY
112369	112369	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
112372	112372	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
106298	106298	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106307	106307	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
107644	107644	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
107651	107651	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
106299	106299	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
106308	106308	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
107650	107650	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	C218 facelift四门Coupe外廓。	READY
107653	107653	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	X218 facelift五门Shooting Brake外廓。	READY
17966	17966	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-02	HIGH	C219 CLS 500 AIRMATIC外廓。	READY
57244_prefl	57244	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57244_facelift	57244	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
11393_prefl	11393	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
11393_facelift	11393	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57245_prefl	57245	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
57245_facelift	57245	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	HIGH	Ktype跨越2014改款，按prefl/facelift物理外廓拆分。	READY
18233	18233	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-AMG-01	MEDIUM	Ktype生产区间覆盖C219 AMG车型更替，但AMG物理外廓保持一致。	READY
14920_prefl	14920	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG外廓。	READY
14920_facelift	14920	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后后驱AMG外廓。	READY
57246_prefl	57246	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
57246_facelift	57246	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后后驱AMG Shooting Brake外廓。	READY
59014_prefl	59014	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
59014_facelift	59014	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后后驱AMG Shooting Brake外廓。	READY
59443_prefl	59443	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG外廓。	READY
59443_facelift	59443	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后后驱AMG外廓。	READY
59446_prefl	59446	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前后驱AMG Shooting Brake外廓。	READY
59446_facelift	59446	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后后驱AMG Shooting Brake外廓。	READY
59015_prefl	59015	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG Shooting Brake外廓。	READY
59015_facelift	59015	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后4MATIC AMG Shooting Brake外廓。	READY
59016_prefl	59016	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG Shooting Brake外廓。	READY
59016_facelift	59016	Wagon	CLS X218	X218	5	EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后4MATIC AMG Shooting Brake外廓。	READY
59017_prefl	59017	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG外廓。	READY
59017_facelift	59017	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后4MATIC AMG外廓。	READY
59018_prefl	59018	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	HIGH	Ktype跨越2014改款；改款前4MATIC AMG外廓。	READY
59018_facelift	59018	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	HIGH	Ktype跨越2014改款；改款后4MATIC AMG外廓。	READY
120741	120741	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	HIGH	W213改款前四门Sedan外廓；AMG E 43三维与标准车身组一致。	READY
125169	125169	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63-PREFACELIFT-01	HIGH	W213改款前AMG E 63四门Sedan宽体外廓。	READY
127339	127339	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63-PREFACELIFT-01	HIGH	S213改款前AMG E 63五门Wagon宽体外廓。	READY
125170_prefl	125170	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63S-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
125170_facelift	125170	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63S-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127340_prefl	127340	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63S-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127340_facelift	127340	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63S-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
126006	126006	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	HIGH	W213改款前四门Sedan外廓。	READY
147702_prefl	147702	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
147702_facelift	147702	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
156038	156038	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-RWD-01	HIGH	W214四门Sedan后驱外廓。	READY
59030	59030	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207 facelift双门Convertible外廓。	READY
59047	59047	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	C207 facelift双门Coupe外廓。	READY
59461_prefl	59461	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
59461_facelift	59461	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
118513	118513	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	HIGH	W213改款前四门Sedan外廓。	READY
120722	120722	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFACELIFT-01	HIGH	S213改款前五门Wagon外廓。	READY
124820_prefl	124820	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
124820_facelift	124820	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127635_prefl	127635	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127635_facelift	127635	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
155288	155288	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-RWD-01	HIGH	W214四门Sedan后驱外廓。	READY
156002	156002	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-CLASS-S214-WAGON-01	HIGH	S214五门Wagon外廓。	READY
120726	120726	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	HIGH	W213改款前四门Sedan 4MATIC外廓。	READY
125163	125163	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFACELIFT-01	HIGH	S213改款前五门Wagon 4MATIC外廓。	READY
127680_prefl	127680	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127680_facelift	127680	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
156365	156365	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-4MATIC-01	HIGH	W214四门Sedan 4MATIC外廓。	READY
157584	157584	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-CLASS-S214-WAGON-01	HIGH	S214五门Wagon 4MATIC外廓。	READY
10146_prefl	10146	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越1999改款，按prefl/facelift物理外廓拆分。	READY
10146_facelift	10146	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越1999改款，按prefl/facelift物理外廓拆分。	READY
12580	12580	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
16991_prefl	16991	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
16991_facelift	16991	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
16992_prefl	16992	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
16992_facelift	16992	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
120746	120746	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	HIGH	W213改款前四门Sedan外廓。	READY
800989	800989	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-CLASS-S214-WAGON-01	HIGH	S214五门Wagon外廓。	READY
800992	800992	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-RWD-01	HIGH	W214四门Sedan后驱外廓。	READY
15061	15061	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
17128_prefl	17128	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
17128_facelift	17128	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
17964_prefl	17964	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
17964_facelift	17964	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
100542	100542	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	W212 facelift四门Sedan后驱外廓。	READY
15063	15063	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-CLASS-S210-WAGON-FACELIFT-01	HIGH	S210 facelift五门Wagon外廓。	READY
17164_prefl	17164	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
17164_facelift	17164	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
106309	106309	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	W212 facelift四门Sedan后驱外廓。	READY
106312	106312	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207 facelift双门Convertible外廓。	READY
106314	106314	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	C207 facelift双门Coupe外廓。	READY
116184	116184	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	HIGH	S212 facelift五门Wagon后驱外廓。	READY
109458	109458	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-FACELIFT-01	HIGH	W212 facelift四门Sedan 4MATIC外廓。	READY
109474	109474	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-4MATIC-FACELIFT-01	HIGH	S212 facelift五门Wagon 4MATIC外廓。	READY
10144	10144	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	HIGH	W210改款前四门Sedan外廓。	READY
11236_prefl	11236	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
11236_facelift	11236	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
12583	12583	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
16594_prefl	16594	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
16594_facelift	16594	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2006改款，按prefl/facelift物理外廓拆分。	READY
53147_prefl	53147	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53147_facelift	53147	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53201_prefl	53201	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
53201_facelift	53201	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
54955	54955	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	HIGH	W210 facelift四门Sedan外廓。	READY
58601_prefl	58601	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
58601_facelift	58601	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
107887_prefl	107887	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
107887_facelift	107887	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2013改款，按prefl/facelift物理外廓拆分。	READY
11081	11081	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	MEDIUM	E 220 D对应W210改款前四门Sedan外廓。	READY
118515_prefl	118515	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
118515_facelift	118515	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
118793_prefl	118793	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
118793_facelift	118793	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
120725_prefl	120725	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
120725_facelift	120725	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
121773_prefl	121773	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
121773_facelift	121773	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
124818_prefl	124818	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
124818_facelift	124818	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127356_prefl	127356	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127356_facelift	127356	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127634_prefl	127634	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127634_facelift	127634	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127675_prefl	127675	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
127675_facelift	127675	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越2020改款，按prefl/facelift物理外廓拆分。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_9701-9800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-FACELIFT-01	4953	1881	1419	Auto-Data Mercedes-Benz CLS X218 facelift CLS 220 BlueTEC	https://www.auto-data.net/en/mercedes-benz-cls-shooting-brake-x218-facelift-2014-cls-220-bluetec-170hp-9g-tronic-20859
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-01	4937	1881	1418	Auto-Data Mercedes-Benz CLS C218 facelift CLS 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-cls-350-bluetec-v6-258hp-9g-tronic-20855
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-01	4956	1881	1416	Mercedes-Benz Public Archive CLS 350 CDI Shooting Brake 2012-2014;Mercedes-Benz Public Archive CLS 350 CDI 4MATIC Shooting Brake 2012-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-BlueEFFICIENCY-2012---2014-from-032013-CLS-350-CDI.xhtml?oid=191336308;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-4MATIC-BlueEFFICIENCY-2012---2014-from-032013-CLS-350-CDI-4MATIC.xhtml?oid=191336309
EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 facelift 2021 CLS 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-facelift-2021-cls-300d-265hp-mild-hybrid-4matic-9g-tronic-43348
EU-MERCEDES-BENZ-CLS-C219-COUPE-01	4913	1873	1403	Mercedes-Benz Public Archive CLS 350 2004-2006;Mercedes-Benz Public Archive CLS 320 CDI 2005-2008;Mercedes-Benz Public Archive CLS 320 CDI 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-2004---2006-only-for-export-until-2010.xhtml?oid=192528692;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-320-CDI-2005---2008.xhtml?oid=192528691;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-320-CDI-2008---2010-from-042009-CLS-350-CDI.xhtml?oid=192528704
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-01	4940	1881	1416	Mercedes-Benz Public Archive CLS 350 CDI 2010-2014;Mercedes-Benz Public Archive CLS 350 CDI 4MATIC 2011-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-BlueEFFICIENCY-2010---2014-from-032013-CLS-350-CDI.xhtml?oid=191274637;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-350-CDI-4MATIC-BlueEFFICIENCY-2011---2014-from-032013-CLS-350-CDI-4MATIC.xhtml?oid=191274638
EU-MERCEDES-BENZ-CLS-C219-COUPE-02	4913	1873	1390	Mercedes-Benz Public Archive CLS 500 2004-2006;Mercedes-Benz Public Archive CLS 500 2006-2008;Mercedes-Benz Public Archive CLS 500 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2004---2006.xhtml?oid=192528694;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2006---2008.xhtml?oid=192528695;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-2008---2010.xhtml?oid=192528707
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-PREFACELIFT-02	4956	1881	1421	Mercedes-Benz Public Archive CLS 500 BlueEFFICIENCY Shooting Brake 2012-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-500-BlueEFFICIENCY-2012---2014-from-032013-CLS-500.xhtml?oid=191336311
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFACELIFT-02	4940	1881	1404	Mercedes-Benz Public Archive CLS 500 4MATIC BlueEFFICIENCY 2011-2014	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-500-4MATIC-BlueEFFICIENCY-2011---2014-ab-032013-CLS-500-4MATIC.xhtml?oid=191274643
EU-MERCEDES-BENZ-CLS-C219-COUPE-AMG-01	4915	1873	1389	Mercedes-Benz Public Archive CLS 55 AMG 2004-2006;Mercedes-Benz Public Archive CLS 63 AMG 2006-2008;Mercedes-Benz Public Archive CLS 63 AMG 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-55-AMG-2004---2006.xhtml?oid=192528696;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2006---2008.xhtml?oid=192528697;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2008---2010.xhtml?oid=192528708
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-PREFACELIFT-01	4996	1881	1406	Mercedes-Benz Public Archive CLS 63 AMG 2011-2014;Automobile-Catalog 2012 Mercedes-Benz CLS 63 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2011---2014.xhtml?oid=191274644;https://www.automobile-catalog.com/car/2012/1557350/mercedes-benz_cls_63_amg.html
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-RWD-FACELIFT-01	4967	1881	1411	Auto-Data Mercedes-Benz CLS C218 facelift AMG CLS 63 RWD	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-amg-cls-63-v8-557hp-amg-speedshift-mct-20858
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-PREFACELIFT-01	5000	1881	1412	Mercedes-Benz Public Archive CLS 63 AMG Shooting Brake 2012-2014;Automobile-Catalog 2013 Mercedes-Benz CLS 63 AMG Shooting Brake	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-2012---2014.xhtml?oid=191336313;https://www.automobile-catalog.com/car/2013/1781960/mercedes-benz_cls_63_amg_shooting_brake.html
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-RWD-FACELIFT-01	5000	1881	1413	Mercedes-AMG Driving Performance CLS 63 AMG Shooting Brake brochure	https://mercedes.ekka.gr/amg/pdf/the_world_of_mercedes-amg.pdf
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-PREFACELIFT-01	5000	1881	1436	Mercedes-Benz Public Archive CLS 63 AMG 4MATIC Shooting Brake 2013-2014;Mercedes-Benz Public Archive CLS 63 AMG S 4MATIC Shooting Brake 2013-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-4MATIC-2013---2014.xhtml?oid=191336314;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-S-4MATIC-2013---2014.xhtml?oid=191336315
EU-MERCEDES-BENZ-CLS-X218-SHOOTING-BRAKE-AMG-4MATIC-FACELIFT-01	5000	1881	1436	Mercedes-AMG Driving Performance CLS 63 AMG 4MATIC Shooting Brake brochure	https://mercedes.ekka.gr/amg/pdf/the_world_of_mercedes-amg.pdf
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-PREFACELIFT-01	4995	1881	1416	Mercedes-Benz Public Archive CLS 63 AMG 4MATIC 2013-2014;Mercedes-Benz Public Archive CLS 63 AMG S 4MATIC 2013-2014	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CLS-63-AMG-4MATIC-2013---2014.xhtml?oid=191274645;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLS-63-AMG-S-4MATIC-2013---2014.xhtml?oid=191274646
EU-MERCEDES-BENZ-CLS-C218-COUPE-AMG-4MATIC-FACELIFT-01	4967	1881	1431	Auto-Data Mercedes-Benz CLS C218 facelift AMG CLS 63 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-amg-cls-63-v8-557hp-4matic-amg-speedshift-mct-20918
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFACELIFT-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-29667
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63-PREFACELIFT-01	4988	1907	1468	Auto-Data Mercedes-Benz E-Class W213 AMG E 63 4MATIC+	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-v8-571hp-4matic-mct-29710
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63-PREFACELIFT-01	4971	1907	1474	Auto-Data Mercedes-Benz E-Class T-Modell S213 AMG E 63 4MATIC+	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-63-v8-571hp-4matic-mct-30777
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63S-PREFACELIFT-01	4988	1907	1463	Auto-Data Mercedes-Benz E-Class W213 AMG E 63 S 4MATIC+	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-s-v8-612hp-4matic-mct-29924
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E63S-FACELIFT-01	4989	1908	1438	Mercedes-Benz USA 2021 Mercedes-AMG E 63 S Sedan specifications	https://media.mbusa.com/releases/release-f263b73b74ccd81a68d0f509780e2a97-2021-mercedes-amg-e-63-s-sedan-specifications
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63S-PREFACELIFT-01	5000	1907	1475	Auto-Data Mercedes-Benz E-Class T-Modell S213 AMG E 63 S 4MATIC+	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-63-s-v8-612hp-4matic-mct-30805
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E63S-FACELIFT-01	5006	1908	1473	Mercedes-Benz USA 2021 Mercedes-AMG E 63 S Wagon specifications	https://media.mbusa.com/releases/release-f263b73b74ccd81a68d0f509780e66ce-2021-mercedes-amg-e-63-s-wagon-specifications
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift E 200	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-200-197hp-eq-boost-9g-tronic-40979
EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-RWD-01	4949	1880	1468	Auto-Data Mercedes-Benz E-Class W214 E 180;Auto-Data Mercedes-Benz E-Class W214 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-180-170hp-mild-hybrid-9g-tronic-51801;https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-220d-197hp-mild-hybrid-9g-tronic-48453
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Auto-Data Mercedes-Benz E-Class Cabrio A207 facelift E 220 BlueTEC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-facelift-2013-e-220-bluetec-170hp-43870
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data Mercedes-Benz E-Class Coupe C207 facelift E 220 BlueTEC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-e-220-bluetec-170hp-43883
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFACELIFT-01	4895	1854	1512	Mercedes-Benz E-Class Saloon and Estate official brochure 2009	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-FACELIFT-01	4905	1854	1507	Mercedes-Benz E-Class official brochure 2014	https://baaf-ks.com/upload/models/eclass/brosure/eclassw212_brosur.pdf
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFACELIFT-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class T-Modell S213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200-184hp-9g-tronic-25816
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFACELIFT-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-200-184hp-9g-tronic-27317
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E-Class Coupe C238 facelift E 200	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-200-197hp-eq-boost-9g-tronic-41064
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFACELIFT-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-200-184hp-9g-tronic-30244
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class Cabrio A238 facelift E 200	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-200-197hp-eq-boost-9g-tronic-41072
EU-MERCEDES-BENZ-E-CLASS-S214-WAGON-01	4949	1880	1469	Auto-Data Mercedes-Benz E-Class T-Modell S214 E 200;Auto-Data Mercedes-Benz E-Class T-Modell S214 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-200-204hp-mild-hybrid-9g-tronic-48918;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-220d-197hp-mild-hybrid-9g-tronic-48917
EU-MERCEDES-BENZ-E-CLASS-W214-SEDAN-4MATIC-01	4949	1880	1469	Auto-Data Mercedes-Benz E-Class W214 E 200 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-200-204hp-mild-hybrid-4matic-9g-tronic-50065
EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-PREFACELIFT-01	4795	1799	1436	Mercedes-Benz Public Archive E 220 CDI W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=5325
EU-MERCEDES-BENZ-E-CLASS-W210-SEDAN-FACELIFT-01	4818	1799	1440	Mercedes-Benz Public Archive E 200 CDI W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-CDI.xhtml?oid=5344
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFACELIFT-01	4818	1822	1450	Mercedes-Benz Public Archive E 200 CDI W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-CDI.xhtml?oid=5368
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	4856	1822	1483	Mercedes-Benz Public Archive E 220 CDI W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=2461815
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	4879	1854	1475	Mercedes-Benz Public Archive E 220 BlueTEC 2014-2016;Mercedes-Benz Public Archive E 200 Natural Gas Drive 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-2014---2016.xhtml?oid=188541008;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Natural-Gas-Drive-2013---2015.xhtml?oid=188541026
EU-MERCEDES-BENZ-E-CLASS-S210-WAGON-FACELIFT-01	4816	1799	1505	Mercedes-Benz Public Archive E 200 Kompressor station wagon S210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Kompressor-station-wagon.xhtml?oid=5427
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFACELIFT-01	4850	1822	1496	Mercedes-Benz Public Archive E 200 Kompressor station wagon S211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Kompressor-station-wagon.xhtml?oid=5464
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 200 Compressor station wagon S211 facelift	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-200-Compressor-station-wagon.xhtml?oid=2461882
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-FACELIFT-01	4879	1854	1490	Mercedes-Benz Public Archive E 220 BlueTEC 4MATIC 2015-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-4MATIC-2015---2016.xhtml?oid=188541009
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-4MATIC-FACELIFT-01	4905	1854	1509	Mercedes-Benz Public Archive E 220 BlueTEC 4MATIC station wagon 2015-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-BlueTEC-4MATIC-2015---2016.xhtml?oid=188837494
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFACELIFT-01	4698	1786	1398	Auto-Data Mercedes-Benz E-Class Cabrio A207 E 220 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-e-220-cdi-blueefficiency-170hp-17384
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFACELIFT-01	4868	1854	1470	Mercedes-Benz E-Class Saloon and Estate official brochure 2009	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFACELIFT-01	4698	1786	1397	Mercedes-Benz Public Archive E 220 CDI BlueEFFICIENCY 2010-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-BlueEFFICIENCY-2010---2013.xhtml?oid=188954779
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Auto-Data Mercedes-Benz E-Class T-Modell S213 facelift E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-194hp-9g-tronic-40982
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_9701-9800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-29667 "Mercedes-Benz E-class (W213) E 200 (184 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-63-v8-571hp-4matic-mct-29710?utm_source=chatgpt.com "Mercedes-Benz E-class (W213) AMG E 63 V8 (571 Hp) ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（493 行）
- 累计尺寸组：dimension_groups_final.tsv（121 行）

