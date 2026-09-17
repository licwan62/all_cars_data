# 任务：all 第 401-500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0005__8c48e4f9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 401-500 行

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
all 第 401-500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q2-GA-SUV-PREFL-01	4191	1794	1508
EU-AUDI-TT-8S-COUPE-01	4177	1832	1353
EU-AUDI-TT-8S-FACELIFT-TTS-ROADSTER-01	4199	1832	1341
EU-AUDI-TT-8S-ROADSTER-01	4177	1832	1355
EU-AUDI-TT-8S-RS-COUPE-01	4191	1832	1344
EU-AUDI-TT-8S-RS-ROADSTER-01	4191	1832	1346
EU-BENTLEY-CONTINENTAL-GT-II-V8S-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	4850	1954	1405
EU-BMW-4-F32-COUPE-01	4638	1825	1377
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384
EU-BMW-4-F82-COUPE-M4-CS-01	4672	1870	1392
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525
EU-CITROEN-JUMPY-II-VAN-L1H1-4X4-01	4805	1895	1942
EU-CITROEN-JUMPY-II-VAN-L2H1-4X4-01	5135	1895	1942
EU-CITROEN-JUMPY-III-BUS-M-01	4959	1920	1890
EU-CITROEN-JUMPY-III-BUS-XL-01	5309	1920	1890
EU-CITROEN-JUMPY-III-BUS-XS-01	4609	1920	1905
EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	4118	1791	1534
EU-FORD-KUGA-III-SUV-FHEV-AWD-01	4614	1883	1658
EU-FORD-KUGA-III-SUV-STANDARD-01	4614	1883	1678
EU-FORD-KUGA-III-SUV-STLINE-01	4620	1883	1666
EU-FORD-KUGA-III-SUV-VIGNALE-01	4629	1883	1680
EU-HYUNDAI-IONIQ-I-HATCHBACK-01	4470	1820	1450
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	4803	2032	1665
EU-MERCEDES-BENZ-EQA-I-H243-SUV-01	4463	1834	1620
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455
EU-OPEL-ASTRA-J-HATCHBACK-5D-01	4419	1814	1510
EU-OPEL-ASTRA-J-SPORTS-TOURER-01	4698	1814	1535
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1500
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291
EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	4507	1880	1297
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	5049	1937	1428
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678
EU-RENAULT-LATITUDE-X43-SEDAN-01	4897	1832	1483
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1800	1442
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1800	1456
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1448
EU-SEAT-TARRACO-I-SUV-01	4735	1839	1674
EU-TESLA-MODEL-3-I-SEDAN-FACELIFT-2020-01	4694	1849	1443
EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	4694	1849	1443
EU-TOYOTA-COROLLA-IX-E120-WAGON-01	4410	1710	1520
EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	4245	1665	1300
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	4295	1690	1385
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
KIA	Sorento iv	2.5 MPI AWD	SUV	Allrad	Benzin	132	180	Apr 2021	-	2024-03-01	144125
Audi	Tt	TTS Tfsi Quattro	Coupe	Allrad	Benzin	235	320	Jan 2021	-	2025-04-01	144132
Mercedes-benz	Eqa	EQA 300 4-matic	SUV	Allrad	Elektro	168	228	May 2021	-	2024-03-01	144139
Mercedes-benz	Eqa	EQA 350 4-matic	SUV	Allrad	Elektro	215	292	May 2021	-	2024-03-01	144140
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	173	235	May 2021	-	2024-03-01	144141
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	225	305	May 2021	-	2024-03-01	144142
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	160	218	May 2021	-	2026-07-01	144143
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	125	170	May 2021	-	2024-03-01	144144
Ford	Kuga iii	2.0 Ecoblue 4X4	SUV	Allrad	Diesel	110	150	Feb 2021	-	2024-03-01	144146
Renault	Latitude	1.6 RS	Stufenheck	Frontantrieb	Benzin	132	180	Apr 2014	-	2024-03-01	144148
Elaris	Leo	EV	SUV	Frontantrieb	Elektro	125	170	Jan 2020	-	2024-03-01	144149
Peugeot	Expert	2.0 16V	Pritsche/Fahrgestell	Frontantrieb	Benzin	103	140	Jan 2007	Mar 2016	2024-03-01	144167
Citroën	Jumpy ii	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Jan 2009	Mar 2016	2024-03-01	144169
Citroën	Jumpy ii	2.0 I	Pritsche/Fahrgestell	Frontantrieb	Benzin	103	140	Nov 2006	Mar 2016	2024-03-01	144170
Citroën	Jumpy ii	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	120	163	Jul 2010	Mar 2016	2024-03-01	144171
Citroën	Jumpy ii	2.0 HDI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	72	98	Jul 2011	Mar 2016	2024-03-01	144172
VW	Lt 28-35 i	2.4 D	Kasten	Heckantrieb	Diesel	57	78	Dec 1982	Jul 1992	2024-03-01	144173
VW	Lt 28-35 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	57	78	Dec 1982	Jul 1992	2024-03-01	144174
VW	Lt 40-55 i	2.4 D	Kasten	Heckantrieb	Diesel	57	78	Dec 1982	Jul 1992	2024-03-01	144175
VW	Lt 40-55 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	57	78	Dec 1982	Jul 1992	2024-03-01	144176
Porsche	911	GT3	Coupe	Heckantrieb	Benzin	375	510	May 2021	Dec 2025	2026-07-01	144198
Audi	Q4 e-Tron	35	SUV	Heckantrieb	Elektro	125	170	May 2021	-	2025-11-01	144200
Audi	Q4 e-Tron	40	SUV	Heckantrieb	Elektro	150	204	Mar 2021	-	2025-11-01	144201
Audi	Q4 e-Tron	50 Quattro	SUV	Allrad	Elektro	220	300	Mar 2021	-	2025-11-01	144202
Mercedes-benz	C-Klasse	C 300 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	235	320	Jul 2019	May 2021	2024-03-01	144206
Jeep	Compass	1.6 Multijet	SUV	Frontantrieb	Diesel	96	130	Apr 2021	-	2024-03-01	144208
Jeep	Compass	1.3 Hybrid 4X4	SUV	Allrad	Benzin/Elektro	140	190	Apr 2021	-	2024-03-01	144209
Seat	Leon	2.0 Tfsi	Kombi	Frontantrieb	Benzin	140	190	Mar 2021	-	2024-03-01	144218
Seat	Leon	TDI 4drive	Kombi	Allrad	Diesel	110	150	Nov 2020	-	2026-03-01	144219
Nissan	Micra v	1.0 Ig-t	Schrägheck	Frontantrieb	Benzin	68	92	Jan 2021	-	2024-03-01	144220
Mercedes-benz	S-Klasse	S 680 Maybach 4-matic	Stufenheck	Allrad	Benzin	450	612	May 2021	-	2024-03-01	144221
Seat	Tarraco	TSI E-hybrid	SUV	Frontantrieb	Benzin/Elektro	180	245	Feb 2021	May 2024	2026-03-01	144223
Sevic	V500	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	10	14	Jan 2020	-	2024-03-01	144229
BMW	4	M4 Competition M Xdrive	Cabriolet	Allrad	Benzin	375	510	Jul 2021	Feb 2024	2024-05-01	144249
Audi	Q2	30 TDI	SUV	Frontantrieb	Diesel	85	116	Feb 2021	-	2025-06-01	144266
Dodge	Charger	6.2 SRT Hellcat Redeye	Stufenheck	Heckantrieb	Benzin	594	808	Sep 2020	-	2024-03-01	144308
Dodge	Durango	6.2 SRT Hellcat	SUV	Allrad	Benzin	529	719	Sep 2020	-	2024-03-01	144310
Nissan	Micra iv	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Oct 2015	-	2024-11-01	144315
Porsche	Panamera	2.9 4S E-hybrid	Kombi	Allrad	Benzin/Elektro	412	560	Aug 2020	Dec 2023	2024-08-01	144319
Hyundai	Tucson	1.6 T-gdi Htrac	SUV	Allrad	Benzin	132	180	Jan 2021	-	2026-04-01	144326
Hyundai	Tucson	2.0 MPI	SUV	Frontantrieb	Benzin	115	156	Jan 2021	-	2026-04-01	144327
Land Rover	Range rover velar	2.0 D200 4X4	SUV	Allrad	Diesel	150	204	Jul 2020	-	2024-08-01	144365
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	370	503	May 2021	-	2024-03-01	144367
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	370	503	May 2021	-	2024-03-01	144368
Peugeot	208 ii	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	68	92	Oct 2019	-	2024-03-01	144371
Renault	Koleos ii	2.0 Blue DCI 185	SUV	Frontantrieb	Diesel	135	184	Jan 2020	-	2025-06-01	144374
Renault	Koleos ii	2.0 Blue DCI 185 4WD	SUV	Allrad	Diesel	135	184	Jan 2020	-	2025-06-01	144375
Peugeot	405 ii	1.9	Stufenheck	Frontantrieb	Benzin	71	97	Jun 1992	Apr 1997	2024-03-01	144387
Opel	Astra j	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	74	101	Jun 2012	Oct 2015	2024-03-01	144388
Nissan	Ariya	EV	SUV	Frontantrieb	Elektro	160	218	Jul 2020	-	2024-03-01	144397
Nissan	Ariya	EV	SUV	Frontantrieb	Elektro	178	242	Jul 2020	-	2024-03-01	144398
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	205	279	Jul 2020	-	2024-03-01	144399
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	225	306	Jul 2020	-	2024-03-01	144400
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	290	394	Jul 2020	-	2024-03-01	144403
Nissan	Micra iv	1.2 Dig-s	Schrägheck	Frontantrieb	Benzin	72	98	Mar 2011	-	2024-11-01	144408
Nissan	Qashqai iii	1.3 Dig-t	SUV	Frontantrieb	Benzin/Elektro	103	140	Apr 2021	-	2024-03-01	144424
Nissan	Qashqai iii	1.3 Dig-t	SUV	Frontantrieb	Benzin/Elektro	116	158	Apr 2021	-	2024-03-01	144425
Nissan	Qashqai iii	1.3 Dig-t Allrad	SUV	Allrad	Benzin/Elektro	116	158	Apr 2021	-	2024-03-01	144426
Toyota	Rav 4 v	2.5 Hybrid AWD	SUV	Allrad	Benzin/Elektro	225	306	Sep 2020	-	2024-03-01	144429
Mitsubishi	Outlander iv	2.5	SUV	Frontantrieb	Benzin	135	184	Jun 2021	-	2025-02-03	144430
Mitsubishi	Outlander iv	2.5 Allrad	SUV	Allrad	Benzin	135	184	Jun 2021	-	2025-02-03	144431
Bentley	Continental	6.0 W12 AWD	Coupe	Allrad	Benzin	485	659	Jun 2021	-	2024-03-01	144433
Peugeot	208 ii	1.6 VTI 115	Schrägheck	Frontantrieb	Benzin	85	116	Nov 2019	-	2024-03-01	144434
Peugeot	208 ii	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	60	82	Jun 2019	-	2024-03-01	144436
Citroën	C4 iii	1.2 Puretech 100	Schrägheck	Frontantrieb	Benzin	74	101	Apr 2021	-	2024-03-01	144440
Toyota	Mirai	FCV	Stufenheck	Heckantrieb	Wasserstoff	134	182	Nov 2020	-	2024-03-01	144462
Porsche	Panamera	2.9 4S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	412	560	Aug 2020	Dec 2023	2024-08-01	144472
VW	Kaefer	1500 1.5	Stufenheck	Heckantrieb	Benzin	29	40	Sep 1966	Jul 1970	2024-03-01	144476
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	350	476	Jun 2019	-	2024-03-01	144477
Opel	Insignia b sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	154	210	Apr 2020	-	2024-07-01	144478
DS	Ds	Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Oct 2021	Dec 2024	2025-12-01	144480
DS	Ds	Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	130	Oct 2021	Aug 2025	2025-12-01	144481
DS	Ds	Puretech 180	Schrägheck	Frontantrieb	Benzin	132	180	Oct 2021	Oct 2022	2025-12-01	144482
DS	Ds	Puretech 225	Schrägheck	Frontantrieb	Benzin	165	224	Oct 2021	Aug 2022	2025-12-01	144483
DS	Ds	E-tense 225	Schrägheck	Frontantrieb	Benzin/Elektro	165	224	Oct 2021	Aug 2025	2025-12-01	144484
DS	Ds	1.6 E-tense 225	Stufenheck	Frontantrieb	Benzin/Elektro	165	225	Sep 2020	Jun 2022	2025-12-01	144486
Renault	Symbol/logan iii	1.0 SCE	Stufenheck	Frontantrieb	Benzin	54	73	Jan 2017	Nov 2019	2024-03-01	144494
Peugeot	308 iii	Puretech 110	Schrägheck	Frontantrieb	Benzin	81	110	Jul 2021	-	2024-03-01	144511
Volvo	Xc40	Recharge AWD	SUV	Allrad	Elektro	300	408	Nov 2020	-	2025-06-01	144518
Peugeot	308 iii	Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Jul 2021	-	2024-03-01	144519
Peugeot	308 iii	Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	131	Jul 2021	-	2024-03-01	144520
Peugeot	308 iii	Hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	165	224	Jul 2021	-	2024-03-01	144522
Peugeot	308 iii	Hybrid 180	Schrägheck	Frontantrieb	Benzin/Elektro	133	181	Jul 2021	-	2024-03-01	144523
Mazda	3	Skyactiv-x M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	137	186	Feb 2021	-	2024-03-01	144528
Mazda	3	Skyactiv-x M Hybrid AWD	Schrägheck	Allrad	Benzin/Elektro	137	186	Feb 2021	-	2024-03-01	144529
Mazda	3	2.0 Skyactiv-x M Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	137	186	Feb 2021	-	2024-03-01	144530
Ferrari	275 gtb	3.3	Coupe	Heckantrieb	Benzin	206	280	Sep 1963	Sep 1965	2024-03-01	144563
Toyota	Corolla	2.0 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	135	184	May 2021	-	2024-03-01	144564
Toyota	Corolla	2.0 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	135	184	May 2021	-	2024-03-01	144565
Porsche	911	2	Coupe	Heckantrieb	Benzin	96	130	Jan 1963	Jul 1967	2024-03-01	144566
Toyota	Corolla	1.8 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	90	122	Oct 2018	-	2024-03-01	144574
Toyota	Corolla	1.8 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	90	122	Feb 2019	-	2024-03-01	144575
Sevic	S70	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	2	3	Jan 2020	-	2024-03-01	144608
Ferrari	400	S I	Coupe	Heckantrieb	Benzin	294	400	Jan 1959	Dec 1964	2024-03-01	144609
Ferrari	400	S II	Coupe	Heckantrieb	Benzin	250	340	Jan 1961	Dec 1964	2024-03-01	144610
Ferrari	400	S I	Cabriolet	Heckantrieb	Benzin	294	400	Jan 1959	Dec 1964	2024-03-01	144611
Ferrari	400	S II	Cabriolet	Heckantrieb	Benzin	250	340	Jan 1961	Dec 1964	2024-03-01	144612
Mercedes-benz	Gle	GLE 300 D EQ Boost 4-matic	SUV	Allrad	Diesel/Elektro	200	272	Jun 2021	Mar 2023	2024-03-01	144630
Mercedes-benz	Gle	GLE 300 D EQ Boost 4-matic	SUV	Allrad	Diesel/Elektro	200	272	Jun 2021	Mar 2023	2024-03-01	144631
Ferrari	275 gts	3.3	Cabriolet	Heckantrieb	Benzin	191	260	Jan 1964	Dec 1966	2024-03-01	144654


--- Round 1 / 首次发送 ---
ChatGPT 说：Unusual activity has been detected from your device. Try again later. (eb5a1a69-b819-4575-98f6-e377a15e3aff)


--- 发送 / 推进信号纠偏 / Round 2 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---


