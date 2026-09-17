# 任务：all 第 12701-12800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0128__8b1275c9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 12701-12800 行

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
all 第 12701-12800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B6-8E2-SEDAN-4D-01	4548	1772	1428
EU-AUDI-A4-B6-8E5-WAGON-5D-01	4548	1772	1428
EU-AUDI-A4-B6-8H-CONVERTIBLE-2D-01	4573	1777	1391
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453
EU-AUDI-A6-C5-4B5-WAGON-5D-01	4796	1810	1479
EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	5390	1930	1515
EU-CHRYSLER-NEON-II-SEDAN-4D-01	4390	1715	1421
EU-CHRYSLER-NEON-PL-SEDAN-4D-01	4364	1714	1369
EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	4290	1705	1600
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	4167	1698	1391
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-FACELIFT-01	4188	1705	1405
EU-CITROEN-XSARA-I-N2-WAGON-5D-FACELIFT-01	4369	1705	1420
EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	4354	1698	1420
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1698	1430
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1698	1430
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505
EU-FORD-FOCUS-I-SEDAN-4D-01	4362	1698	1430
EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	4438	1698	1447
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	5302	2125	1990
EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	4552	1960	1990
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-HONDA-CR-V-III-SUV-01	4519	1820	1679
EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	4972	1956	1865
EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	3575	1719	1575
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	4868	1854	1470
EU-MINI-MINI-R53-HATCHBACK-3D-01	3655	1688	1416
EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	3961	1683	1426
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	4567	1760	1482
EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	4675	1760	1482
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	4467	1801	1645
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844
EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	4046	1672	1870
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	3995	1672	1835
EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	4598	1772	1433
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	4576	1772	1429
EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	4803	1811	1445
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	4082	1698	1368
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	4028	1698	1368
EU-RENAULT-MEGANE-I-GRANDTOUR-WAGON-5D-FACELIFT-01	4437	1698	1420
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420
EU-RENAULT-THALIA-II-L35-SEDAN-01	4261	1639	1439
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980
EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	4615	1690	1935
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	4785	1700	1795
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	4915	1700	1795
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-PREFL-01	4725	1690	1800
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	4785	1700	1765
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	4915	1700	1765
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-PREFL-01	4725	1690	1760
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547
EU-VOLVO-XC90-I-SUV-FACELIFT-01	4807	1936	1784
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Land Rover	Range rover iii	4.4 4X4	Geländewagen geschlossen	Allrad	Benzin	210	286	Mar 2002	Aug 2005	2024-03-01	16519
Land Rover	Range rover iii	3.0 D 4X4	Geländewagen geschlossen	Allrad	Diesel	130	177	Mar 2002	Aug 2012	2024-03-01	16520
VW	Polo	1.2	Schrägheck	Frontantrieb	Benzin	40	54	Jan 2002	May 2007	2024-03-01	16521
Honda	Civic vii hatchback	1.7 Ctdi	Schrägheck	Frontantrieb	Diesel	74	100	Jan 2002	Sep 2005	2024-03-01	16522
Seat	Ibiza iii	1.2	Schrägheck	Frontantrieb	Benzin	47	64	Feb 2002	Jun 2006	2024-03-01	16523
Seat	Ibiza iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	74	100	Feb 2002	Nov 2009	2024-03-01	16524
Seat	Ibiza iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	74	100	Feb 2002	Nov 2009	2024-03-01	16525
Seat	Ibiza iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	96	131	Feb 2002	Nov 2009	2024-03-01	16526
Lancia	Thesis	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	136	185	Jul 2002	Jul 2009	2024-03-01	16527
Lancia	Thesis	2.4	Stufenheck	Frontantrieb	Benzin	125	170	Jul 2002	Jul 2009	2024-03-01	16528
Lancia	Thesis	2.4 JTD	Stufenheck	Frontantrieb	Diesel	110	150	Jul 2002	Jul 2009	2024-03-01	16529
Opel	Vectra c cc	3.2 V6	Schrägheck	Frontantrieb	Benzin	155	211	Aug 2002	Jul 2006	2024-03-01	16530
Chrysler	Neon	2.0 16V R/T	Stufenheck	Frontantrieb	Benzin	110	150	Oct 2001	Dec 2006	2024-03-01	16544
Peugeot	307	1.4 HDI	Schrägheck	Frontantrieb	Diesel	50	68	Oct 2001	Jun 2005	2024-03-01	16545
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	65	88	Aug 2001	Aug 2006	2024-03-01	16546
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	75	102	Aug 2001	Aug 2006	2024-03-01	16547
Toyota	Hilux vi	2.5 D-4d	Pick-up	Heckantrieb	Diesel	65	88	Nov 2001	Jul 2005	2024-03-01	16548
Toyota	Hilux vi	2.5 D-4d 4WD	Pick-up	Allrad	Diesel	75	102	Nov 2001	Jul 2005	2024-03-01	16549
Suzuki	Grand vitara i	2.7 4X4	Geländewagen geschlossen	Allrad	Benzin	127	173	Sep 2001	Jul 2003	2024-03-01	16550
Ford	Transit	2.4 TDE	Bus	Heckantrieb	Diesel	92	125	Jul 2001	May 2006	2024-03-01	16551
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	74	101	Oct 2001	May 2008	2024-03-01	16552
Renault	Thalia i	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Aug 2000	Oct 2005	2025-12-01	16553
Renault	Thalia i	1.4 16V	Stufenheck	Frontantrieb	Benzin	72	98	Aug 2000	Feb 2009	2025-12-01	16554
Renault	Kangoo	1.5 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	48	65	Dec 2001	-	2024-03-01	16555
Toyota	Hiace iv	2.7	Bus	Heckantrieb	Benzin	106	144	Jul 1998	Dec 2006	2024-03-01	16556
Toyota	Hiace iv	2.5 D-4d	Kasten	Heckantrieb	Diesel	65	88	Aug 2001	Aug 2006	2024-03-01	16557
Toyota	Hiace iv	2.5 D-4d	Kasten	Heckantrieb	Diesel	75	102	Aug 2001	Aug 2006	2024-03-01	16558
Citroën	Xsara	1.6 I	Coupe	Frontantrieb	Benzin	65	88	Feb 1998	Sep 2000	2024-03-01	16559
VW	Phaeton	6.0 W12 4motion	Stufenheck	Allrad	Benzin	309	420	Apr 2002	Dec 2005	2024-03-01	16561
Ford	Transit	2.9 I	Bus	Heckantrieb	Benzin	107	145	Jan 1991	Sep 1994	2024-03-01	16562
Ford	Transit	2.0 CNG	Bus	Heckantrieb	Benzin/Erdgas (CNG)	84	114	Jun 1994	Mar 2000	2024-03-01	16563
Mercedes-benz	E-Klasse	E 320	Stufenheck	Heckantrieb	Benzin	165	224	Mar 2002	Dec 2008	2024-03-01	16564
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	225	306	Mar 2002	Dec 2008	2024-03-01	16565
Maserati	4200 gt /	4.2	Coupe	Heckantrieb	Benzin	287	390	Mar 2002	Dec 2007	2024-03-01	16566
Volvo	S40 i	2.0 T	Stufenheck	Frontantrieb	Benzin	120	163	Jun 2001	Dec 2003	2024-03-01	16568
Volvo	V40	2.0 T	Kombi	Frontantrieb	Benzin	120	163	Jun 2001	Jun 2004	2024-03-01	16569
Volvo	Xc90 i	2.5 T AWD	SUV	Allrad	Benzin	154	209	Oct 2002	Sep 2014	2024-03-01	16570
Volvo	Xc90 i	T6 AWD	SUV	Allrad	Benzin	200	272	Oct 2002	Dec 2006	2024-03-01	16571
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	120	163	Oct 2002	Dec 2006	2024-03-01	16572
Honda	Cr-V ii	2	SUV	Allrad	Benzin	110	150	Sep 2001	Mar 2007	2024-03-01	16573
Mercedes-benz	Sprinter 5-T	516 CDI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	120	163	Mar 2009	Dec 2018	2024-03-01	16574
Mercedes-benz	Sprinter 3,5-T	316 CDI 4X4	Bus	Allrad	Diesel	120	163	Aug 2011	Dec 2018	2024-03-01	16575
Jaguar	X-Type i	2.1 V6	Stufenheck	Frontantrieb	Benzin	115	156	Mar 2002	Nov 2009	2024-03-01	16576
Renault	Megane i coach	2.0 16V	Coupe	Frontantrieb	Benzin	102	139	Jan 2002	Aug 2003	2024-03-01	16577
Renault	Megane i	2.0 16V	Cabriolet	Frontantrieb	Benzin	102	139	Jan 2002	Aug 2003	2024-03-01	16578
Opel	Zafira	2.2 DTI 16V	Großraumlimousine	Frontantrieb	Diesel	92	125	Jan 2002	Jun 2005	2024-03-01	16579
Chrysler	Pt cruiser	2.2 CRD	Kombi	Frontantrieb	Diesel	89	121	Mar 2002	Dec 2010	2024-03-01	16581
Renault	Laguna ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	74	100	Oct 2001	May 2005	2024-03-01	16582
Renault	Laguna ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	74	100	Oct 2001	May 2005	2024-03-01	16583
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	85	115	May 2001	Sep 2005	2024-03-01	16584
Alfa Romeo	156	1.9 JTD	Kombi	Frontantrieb	Diesel	85	115	May 2001	May 2006	2024-03-01	16586
Lancia	Lybra	1.9 JTD	Stufenheck	Frontantrieb	Diesel	85	116	May 2001	Oct 2005	2024-03-01	16587
Lancia	Lybra	1.9 JTD	Kombi	Frontantrieb	Diesel	85	116	May 2001	Oct 2005	2024-03-01	16588
Fiat	Multipla	1.6 16V Bipower	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	76	103	Oct 2001	Aug 2005	2026-02-01	16589
Hyundai	Accent ii	1.5	Schrägheck	Frontantrieb	Benzin	66	90	Jan 2000	Nov 2005	2024-03-01	16590
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	78	106	Mar 2002	Aug 2008	2024-03-01	16591
Mercedes-benz	A-Klasse	A 210	Schrägheck	Frontantrieb	Benzin	103	140	Dec 2001	Aug 2004	2024-03-01	16592
Mercedes-benz	E-Klasse	E 240	Stufenheck	Heckantrieb	Benzin	130	177	Mar 2002	Dec 2008	2024-03-01	16593
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	110	150	Mar 2002	Dec 2008	2024-03-01	16594
Mercedes-benz	E-Klasse	E 270 CDI	Stufenheck	Heckantrieb	Diesel	130	177	Mar 2002	Dec 2008	2024-03-01	16595
Audi	A4 b6	2.0 FSI	Stufenheck	Frontantrieb	Benzin	110	150	Jul 2002	Dec 2004	2024-03-01	16596
Honda	Integra	2.0 16V Type-r	Coupe	Frontantrieb	Benzin	162	220	Feb 2002	Oct 2007	2025-12-01	16597
Renault	Espace iii	2	Großraumlimousine	Frontantrieb	Benzin	102	139	Sep 2001	Oct 2002	2024-03-01	16598
Volvo	V70 ii	2.4 D	Kombi	Frontantrieb	Diesel	96	131	Jul 2001	Aug 2007	2024-03-01	16599
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	120	163	Mar 2002	Sep 2006	2024-03-01	16600
Audi	A4 b6 avant	1.9 TDI	Kombi	Frontantrieb	Diesel	74	101	Nov 2001	Dec 2004	2024-03-01	16601
Audi	A4 b6	1.9 TDI Quattro	Stufenheck	Allrad	Diesel	96	130	Nov 2001	Dec 2004	2024-03-01	16602
Audi	A4 b6 avant	1.9 TDI Quattro	Kombi	Allrad	Diesel	96	130	Nov 2001	Dec 2004	2024-03-01	16603
MG	Zr	105	Schrägheck	Frontantrieb	Benzin	76	103	Jun 2001	Apr 2005	2025-12-01	16604
MG	Zr	120	Schrägheck	Frontantrieb	Benzin	86	117	Jun 2001	Apr 2005	2025-12-01	16605
MG	Zr	2.0 TD	Schrägheck	Frontantrieb	Diesel	74	100	Jun 2001	Apr 2005	2025-12-01	16606
Bentley	Arnage	6.8 V8 T	Stufenheck	Heckantrieb	Benzin	336	457	Feb 2002	Oct 2009	2024-03-01	16607
MG	Zs	120	Stufenheck	Frontantrieb	Benzin	86	117	Jul 2001	Apr 2005	2025-12-01	16608
MG	Zs	120	Schrägheck	Frontantrieb	Benzin	86	117	Jul 2001	Oct 2005	2025-12-01	16609
Alfa Romeo	156	3.2 GTA	Stufenheck	Frontantrieb	Benzin	184	250	Mar 2002	Sep 2005	2024-03-01	16610
Alfa Romeo	156	3.2 GTA	Kombi	Frontantrieb	Benzin	184	250	Mar 2002	May 2006	2024-03-01	16611
Peugeot	307	1.6 16V	Kombi	Frontantrieb	Benzin	80	109	Mar 2002	Apr 2008	2024-03-01	16612
Peugeot	307	2.0 16V	Kombi	Frontantrieb	Benzin	100	136	Mar 2002	Jun 2005	2024-03-01	16613
Peugeot	307	2.0 HDI 90	Kombi	Frontantrieb	Diesel	66	90	Mar 2002	Apr 2008	2024-03-01	16614
Peugeot	307	2.0 HDI 110	Kombi	Frontantrieb	Diesel	79	107	Mar 2002	Dec 2009	2024-03-01	16615
Smart	Crossblade	0.6	Cabriolet	Heckantrieb	Benzin	52	71	Jun 2002	Dec 2003	2024-03-01	16616
Alfa Romeo	156	2.0 JTS	Stufenheck	Frontantrieb	Benzin	122	166	Mar 2002	Sep 2005	2024-03-01	16617
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	110	150	Mar 2002	Sep 2005	2024-03-01	16618
Alfa Romeo	156	2.0 JTS	Kombi	Frontantrieb	Benzin	122	166	Mar 2002	May 2006	2024-03-01	16619
Alfa Romeo	156	2.4 JTD	Kombi	Frontantrieb	Diesel	110	150	Mar 2002	May 2006	2024-03-01	16620
MG	Tf	135	Cabriolet	Heckantrieb	Benzin	100	136	Mar 2002	Dec 2009	2025-12-01	16621
MG	Tf	120	Cabriolet	Heckantrieb	Benzin	88	120	Mar 2002	Dec 2009	2025-12-01	16622
MG	Tf	115	Cabriolet	Heckantrieb	Benzin	85	116	Mar 2002	Dec 2009	2025-12-01	16623
Ford	Fusion	1.4	Kombi	Frontantrieb	Benzin	59	80	Aug 2002	Dec 2012	2024-03-01	16624
Ford	Fusion	1.6	Kombi	Frontantrieb	Benzin	74	100	Aug 2002	Nov 2009	2024-03-01	16625
Ford	Fusion	1.4 Tdci	Kombi	Frontantrieb	Diesel	50	68	Aug 2002	Dec 2012	2024-03-01	16626
Audi	A6 c5	RS6 Quattro	Stufenheck	Allrad	Benzin	331	450	Jul 2002	Jan 2005	2024-03-01	16627
Audi	A6 c5 avant	RS6 Quattro	Kombi	Allrad	Benzin	331	450	Jul 2002	Jan 2005	2024-03-01	16628
Mercedes-benz	Clk	CLK 320	Coupe	Heckantrieb	Benzin	160	218	Jun 2002	May 2009	2024-03-01	16629
Mercedes-benz	Clk	CLK 500	Coupe	Heckantrieb	Benzin	225	306	Jun 2002	May 2009	2024-03-01	16630
Ford	Focus i	St170	Schrägheck	Frontantrieb	Benzin	127	173	Mar 2002	Nov 2004	2024-03-01	16631
Ford	Mondeo iii	St220	Schrägheck	Frontantrieb	Benzin	166	226	Apr 2002	Mar 2007	2024-03-01	16632
Ford	Mondeo iii	St220	Stufenheck	Frontantrieb	Benzin	166	226	Apr 2002	Mar 2007	2024-03-01	16633
Ford	Mondeo iii turnier	St220	Kombi	Frontantrieb	Benzin	166	226	Apr 2002	Mar 2007	2024-03-01	16634
Suzuki	Liana	1.3	Stufenheck	Frontantrieb	Benzin	66	90	Mar 2002	-	2024-03-01	16635


--- Round 1 / 首次发送 ---
## 更新点

* 复用 16 个已有尺寸组，完成 Hiace IV、Xsara、S40/V40、Megane I、Zafira A、Laguna II、Primera P12、A4 B6、Mini R53 等映射，不重复输出缓存尺寸组。
* 首次闭合 Lancia Thesis、Maserati Coupé M138、Honda CR-V II、Jaguar X-Type 四个尺寸组。([汽车目录][1])
* 首次闭合 Smart Crossblade、Suzuki Liana Sedan，以及 Ford Fusion I 改款前、改款后两个不同外廓；3 个 Fusion Ktype 均已拆分关联。([汽车目录][2])

## 当前批次进度

* READY Ktype：32 / 100
* READY 映射行：35
* PENDING Ktype：68
* 已确认尺寸组：24

  * 复用已有组：16
  * 本轮首次创建：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16527	16527	Sedan	Thesis I	841	4	EU-LANCIA-THESIS-I-SEDAN-4D-01	HIGH	841四门轿车外廓。	READY
16528	16528	Sedan	Thesis I	841	4	EU-LANCIA-THESIS-I-SEDAN-4D-01	HIGH	841四门轿车外廓。	READY
16529	16529	Sedan	Thesis I	841	4	EU-LANCIA-THESIS-I-SEDAN-4D-01	HIGH	841四门轿车外廓。	READY
16544	16544	Sedan	Neon II		4	EU-CHRYSLER-NEON-II-SEDAN-4D-01	HIGH	第二代四门轿车外廓。	READY
16546	16546	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH	H100客车外廓。	READY
16547	16547	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH	H100客车外廓。	READY
16556	16556	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH	H100客车外廓。	READY
16557	16557	Van	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	HIGH	H100后驱低顶厢式外廓。	READY
16558	16558	Van	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	HIGH	H100后驱低顶厢式外廓。	READY
16559	16559	Coupe	Xsara I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	改款前三门标准Coupe外廓。	READY
16566	16566	Coupe	Coupe M138	M138	2	EU-MASERATI-COUPE-M138-COUPE-2D-01	HIGH	M138双门Coupe外廓。	READY
16568	16568	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH	VS四门轿车外廓。	READY
16569	16569	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH	VW五门旅行车外廓。	READY
16573	16573	SUV	CR-V II	RD5	5	EU-HONDA-CR-V-II-RD-SUV-5D-01	HIGH	RD5五门四驱SUV外廓。	READY
16576	16576	Sedan	X-Type I	X400	4	EU-JAGUAR-X-TYPE-X400-SEDAN-4D-01	HIGH	X400四门轿车外廓。	READY
16577	16577	Coupe	Megane I	DA	3	EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	HIGH	DA改款后三门Coupe外廓。	READY
16578	16578	Convertible	Megane I	EA	2	EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	HIGH	EA改款后敞篷外廓。	READY
16579	16579	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	HIGH	T98五门MPV外廓。	READY
16582	16582	Hatchback	Laguna II	B74	5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
16583	16583	Wagon	Laguna II	K74	5	EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	HIGH	改款前Grandtour五门旅行车外廓。	READY
16591	16591	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12四门轿车外廓。	READY
16592	16592	Hatchback	A-Klasse W168	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH	W168五门掀背外廓。	READY
16596	16596	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH	8E2四门轿车外廓。	READY
16600	16600	Hatchback	Mini I	R53	3	EU-MINI-MINI-R53-HATCHBACK-3D-01	HIGH	R53三门掀背外廓。	READY
16601	16601	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH	8E5五门Avant外廓。	READY
16602	16602	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH	8E2四门轿车外廓。	READY
16603	16603	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH	8E5五门Avant外廓。	READY
16616	16616	Convertible	Crossblade	W450	2	EU-SMART-CROSSBLADE-W450-ROADSTER-2D-01	HIGH	W450 Crossblade双门开放式外廓。	READY
16624_prefl	16624	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16624_facelift	16624	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16625_prefl	16625	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16625_facelift	16625	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16626_prefl	16626	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16626_facelift	16626	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-JU2-MPV-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16635	16635	Sedan	Liana I	ER	4	EU-SUZUKI-LIANA-I-ER-SEDAN-4D-01	HIGH	ER四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-THESIS-I-SEDAN-4D-01	4888	1830	1465	Automobile-Catalog 2002 Lancia Thesis 2.0 Turbo Executive	https://www.automobile-catalog.com/car/2002/1385045/lancia_thesis_2_0_turbo_executive.html
EU-MASERATI-COUPE-M138-COUPE-2D-01	4523	1822	1305	Automobile-Catalog 2002 Maserati Coupe Cambiocorsa	https://www.automobile-catalog.com/car/2002/1447550/maserati_coupe_cambiocorsa.html
EU-HONDA-CR-V-II-RD-SUV-5D-01	4570	1780	1710	Honda Europe CR-V 02 press release	https://hondanews.eu/eu/en/cars/media/pressreleases/34287/cr-v-02
EU-JAGUAR-X-TYPE-X400-SEDAN-4D-01	4672	1789	1392	Automobile-Catalog 2002 Jaguar X-Type 2.0 V6 automatic	https://www.automobile-catalog.com/car/2002/1290530/jaguar_x-type_2_0_v6_automatic.html
EU-SMART-CROSSBLADE-W450-ROADSTER-2D-01	2622	1618	1508	Automobile-Catalog 2002 Smart Crossblade	https://www.automobile-catalog.com/car/2002/3154490/smart_crossblade.html
EU-FORD-FUSION-I-JU2-MPV-5D-PREFL-01	4018	1720	1498	Automobile-Catalog 2002 Ford Fusion 1.4 16V Ambiente	https://www.automobile-catalog.com/car/2002/960125/ford_fusion_1_4_16v_ambiente.html
EU-FORD-FUSION-I-JU2-MPV-5D-FACELIFT-01	4013	1724	1543	Automobile-Catalog 2006 Ford Fusion 1.4 16V Plus	https://www.automobile-catalog.com/car/2006/961490/ford_fusion_1_4_16v_.html
EU-SUZUKI-LIANA-I-ER-SEDAN-4D-01	4350	1690	1545	Automobile-Catalog 2002 Suzuki Liana Sedan 1.3	https://www.automobile-catalog.com/car/2002/3390140/suzuki_liana_sedan_1_3.html
```

## 下一步优先处理

1. 聚类处理 Polo 9N、Ibiza III、Peugeot 307 的门数及改款前后分支。
2. 处理 Range Rover III、XC90 I、Vectra C CC、Mercedes-Benz W211/CLK C209 的跨改款外廓。
3. 集中处理 Transit、Sprinter、Hilux、Kangoo 等多轴距、多车顶或多车身配置。
4. 闭合 Alfa Romeo 156、MG ZR/ZS/TF、Mondeo III 等尚未建立的乘用车尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/1385045/lancia_thesis_2_0_turbo_executive.html?utm_source=chatgpt.com "2002 Lancia Thesis 2.0 Turbo Executive (man. 6)"
[2]: https://www.automobile-catalog.com/car/2002/3154490/smart_crossblade.html?utm_source=chatgpt.com "2002 Smart Crossblade Specs Review (52 kW / 71 PS / 70 hp) (since March 2002 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 复用 Polo IV、Hilux VI、Arnage I、Focus I 的 11 个既有尺寸组，新增对应物理分支映射，不重复输出缓存尺寸事实。
* Honda 官方资料确认 Civic VII 1.7 CTDi 同时覆盖 EP4 三门与 EU9 五门，两种外廓分别建组。([本田新闻][1])
* Honda 官方资料确认 Integra Type-R 为 DC5 三门 Coupe，闭合对应尺寸组。([Honda Global][2])

## 当前批次进度

* READY Ktype：40 / 100
* READY 映射行：57
* PENDING Ktype：60
* 已确认尺寸组：38
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16521_3dr_prefl	16521	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	9N1改款前三门外廓。	READY
16521_3dr_facelift	16521	Hatchback	Polo IV	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	9N3改款后三门外廓。	READY
16521_5dr_prefl	16521	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	9N1改款前五门外廓。	READY
16521_5dr_facelift	16521	Hatchback	Polo IV	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	9N3改款后五门外廓。	READY
16522_3dr	16522	Hatchback	Civic VII	EP4	3	EU-HONDA-CIVIC-VII-EP4-HATCHBACK-3D-01	HIGH	EP4三门柴油掀背外廓。	READY
16522_5dr	16522	Hatchback	Civic VII	EU9	5	EU-HONDA-CIVIC-VII-EU9-HATCHBACK-5D-01	HIGH	EU9五门柴油掀背外廓。	READY
16548_single	16548	Pickup	Hilux VI		2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	MEDIUM	改款后单排标准后部外廓。	READY
16548_single_step	16548	Pickup	Hilux VI		2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	MEDIUM	改款后单排带后踏步外廓。	READY
16548_double	16548	Pickup	Hilux VI		4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	MEDIUM	改款后双排标准后部外廓。	READY
16548_double_step	16548	Pickup	Hilux VI		4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	MEDIUM	改款后双排带后踏步外廓。	READY
16549_single	16549	Pickup	Hilux VI		2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	MEDIUM	改款后单排标准后部外廓。	READY
16549_single_step	16549	Pickup	Hilux VI		2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	MEDIUM	改款后单排带后踏步外廓。	READY
16549_double	16549	Pickup	Hilux VI		4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	MEDIUM	改款后双排标准后部外廓。	READY
16549_double_step	16549	Pickup	Hilux VI		4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	MEDIUM	改款后双排带后踏步外廓。	READY
16552_3dr_prefl	16552	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	HIGH	9N1改款前三门外廓。	READY
16552_3dr_facelift	16552	Hatchback	Polo IV	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	HIGH	9N3改款后三门外廓。	READY
16552_5dr_prefl	16552	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	HIGH	9N1改款前五门外廓。	READY
16552_5dr_facelift	16552	Hatchback	Polo IV	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	HIGH	9N3改款后五门外廓。	READY
16597	16597	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-01	HIGH	DC5 Type-R三门Coupe外廓。	READY
16607	16607	Sedan	Arnage I		4	EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	HIGH	Arnage四门轿车外廓。	READY
16631_3dr	16631	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	HIGH	ST170三门掀背外廓。	READY
16631_5dr	16631	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	HIGH	ST170五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-VII-EP4-HATCHBACK-3D-01	4140	1695	1440	Honda Civic CTDi official press release	https://hondanews.eu/eu/en/cars/media/pressreleases/34257/civic-ctdi
EU-HONDA-CIVIC-VII-EU9-HATCHBACK-5D-01	4285	1695	1495	Honda Civic CTDi official press release	https://hondanews.eu/eu/en/cars/media/pressreleases/34257/civic-ctdi
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-01	4385	1725	1385	Honda New Integra prototype official release	https://global.honda/jp/news/2001/4010413b-integra.html
```

## 下一步优先处理

1. 批量闭合 Seat Ibiza III、Peugeot 307 的门数和改款分支。
2. 处理 Range Rover III、XC90 I、Vectra C CC 与 Mercedes-Benz W211/C209。
3. 集中拆分 Transit、Sprinter、Kangoo 的轴距和车顶外廓。
4. 闭合 Alfa Romeo 156、MG ZR/ZS/TF、Mondeo III 等乘用车尺寸组。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/en/cars/media/pressreleases/34257/civic-ctdi?utm_source=chatgpt.com "Civic CTDi"
[2]: https://global.honda/en/newsroom/news/2001/4010702-integra-eng.html?utm_source=chatgpt.com "Honda Announces Integra Full Model Change | Honda Global Corporate Website"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Seat Ibiza III（6L1）改款前/后及三门/五门分支；改款前三维为 3953×1698×1441 mm，改款后为 3977×1698×1441 mm，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Range Rover III L322 初期 4.4 V8 与 3.0 TD6 共用外廓。([汽车目录][2])
* 新建 Volvo XC90 I 改款前尺寸组；2.5 T 跨改款拆分，T6 与 120 kW D5 关联改款前组。([Volvo Car Club][3])
* 闭合 Suzuki Grand Vitara XL-7 2.7 五门外廓；Chrysler PT Cruiser 直接复用既有尺寸组。([汽车目录][4])

## 当前批次进度

* READY Ktype：51 / 100
* READY 映射行：79
* PENDING Ktype：49
* 已确认尺寸组：45
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16519	16519	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-2002-2005-01	HIGH	L322初期4.4 V8五门外廓。	READY
16520	16520	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-2002-2005-01	HIGH	3.0 TD6对应L322初期五门外廓。	READY
16523_3dr_prefl	16523	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门外廓。	READY
16523_5dr_prefl	16523	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16524_3dr_prefl	16524	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门外廓。	READY
16524_3dr_facelift	16524	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
16524_5dr_prefl	16524	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16524_5dr_facelift	16524	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16525_3dr_prefl	16525	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门外廓。	READY
16525_3dr_facelift	16525	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
16525_5dr_prefl	16525	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16525_5dr_facelift	16525	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16526_3dr_prefl	16526	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-PREFL-01	HIGH	改款前三门外廓。	READY
16526_3dr_facelift	16526	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
16526_5dr_prefl	16526	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-PREFL-01	HIGH	改款前五门外廓。	READY
16526_5dr_facelift	16526	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门外廓。	READY
16550	16550	SUV	Grand Vitara I XL-7	HT	5	EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	HIGH	2.7 V6对应XL-7五门加长外廓。	READY
16570_prefl	16570	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-PREFL-01	HIGH	改款前五门SUV外廓。	READY
16570_facelift	16570	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
16571	16571	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-PREFL-01	HIGH	T6对应改款前五门SUV外廓。	READY
16572	16572	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-PREFL-01	HIGH	120 kW D5对应改款前五门SUV外廓。	READY
16581	16581	Hatchback	PT Cruiser	PT	5	EU-CHRYSLER-PT-CRUISER-HATCHBACK-5D-01	HIGH	PT Cruiser五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-2002-2005-01	4950	1956	1863	Automobile-Catalog 2002 Range Rover V8 HSE; Automobile-Catalog 2002 Range Rover TD6 HSE	https://www.automobile-catalog.com/car/2002/1404065/range_rover_v8_hse.html; https://www.automobile-catalog.com/car/2002/1404080/range_rover_td6_hse.html
EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-PREFL-01	3953	1698	1441	Automobile-Catalog 2002 SEAT Ibiza 1.4 16V	https://www.automobile-catalog.com/car/2002/3076310/seat_ibiza_1_4_16v_75.html
EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-PREFL-01	3953	1698	1441	Automobile-Catalog 2002 SEAT Ibiza 1.4 16V	https://www.automobile-catalog.com/car/2002/3076310/seat_ibiza_1_4_16v_75.html
EU-SEAT-IBIZA-III-6L1-HATCHBACK-3D-FACELIFT-01	3977	1698	1441	Automobile-Catalog 2006 SEAT Ibiza 1.4 16V	https://www.automobile-catalog.com/car/2006/3080870/seat_ibiza_1_4_16v_100.html
EU-SEAT-IBIZA-III-6L1-HATCHBACK-5D-FACELIFT-01	3977	1698	1441	Automobile-Catalog 2006 SEAT Ibiza 1.4 16V	https://www.automobile-catalog.com/car/2006/3080870/seat_ibiza_1_4_16v_100.html
EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	4700	1780	1740	Automobile-Catalog 2002 Suzuki Grand Vitara XL-7	https://www.automobile-catalog.com/car/2002/3352865/suzuki_grand_vitara_xl-7.html
EU-VOLVO-XC90-I-SUV-PREFL-01	4798	1898	1784	Volvo XC90 official UK product specification April 2003	https://www.volvoclub.org.uk/pdf/xc90/XC90_Full_Product_Spec_Apr2003.pdf
```

## 下一步优先处理

1. 批量闭合 Peugeot 307 Hatchback、Break/Wagon 的改款和门数分支。
2. 处理 Mercedes-Benz W211、CLK C209 与 Opel Vectra C CC。
3. 闭合 Alfa Romeo 156 Sedan/Sportwagon/GTA、Lancia Lybra 与 Fiat Multipla。
4. 最后集中处理 Transit、Sprinter、Kangoo 等多轴距、多车顶商用车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/3076310/seat_ibiza_1_4_16v_75.html?utm_source=chatgpt.com "2002 Seat Ibiza 1.4 16V (75) Specs Review (55 kW / ..."
[2]: https://www.automobile-catalog.com/car/2002/1404080/range_rover_td6_hse.html?utm_source=chatgpt.com "2002 Range Rover TD6 HSE Specs Review (130 kW / 177 PS / 174 hp) (since mid-year 2002 for Europe )"
[3]: https://www.volvoclub.org.uk/pdf/xc90/XC90_Full_Product_Spec_Apr2003.pdf?utm_source=chatgpt.com "Volvo XC90 Brochure April 2003"
[4]: https://www.automobile-catalog.com/car/2002/3352865/suzuki_grand_vitara_xl-7.html?utm_source=chatgpt.com "2002 Suzuki Grand Vitara XL-7 Specs Review (127 kW / 173 PS / 170 hp) (for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Peugeot 307 掀背与旅行车外廓：掀背按三门/五门及 2005 年改款前后拆分；旅行车按改款前后拆分。改款前后长宽发生变化，不能共用尺寸组。([汽车目录][1])
* 闭合 Alfa Romeo 156 标准 Sedan、Sportwagon 及 GTA Sedan 外廓；2003 年外观改款后长度和宽度发生变化，分别建立改款前后尺寸组。([汽车目录][2])

## 当前批次进度

* READY Ktype：63 / 100
* READY 映射行：104
* PENDING Ktype：37
* 已确认尺寸组：57
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16545_3dr_prefl	16545	Hatchback	307 I		3	EU-PEUGEOT-307-I-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门掀背外廓。	READY
16545_3dr_facelift	16545	Hatchback	307 I		3	EU-PEUGEOT-307-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门掀背外廓。	READY
16545_5dr_prefl	16545	Hatchback	307 I		5	EU-PEUGEOT-307-I-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门掀背外廓。	READY
16545_5dr_facelift	16545	Hatchback	307 I		5	EU-PEUGEOT-307-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门掀背外廓。	READY
16584_prefl	16584	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-PREFL-01	HIGH	外观改款前四门轿车外廓。	READY
16584_facelift	16584	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-FACELIFT-01	HIGH	外观改款后四门轿车外廓。	READY
16586_prefl	16586	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-PREFL-01	HIGH	外观改款前Sportwagon外廓。	READY
16586_facelift	16586	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-FACELIFT-01	HIGH	外观改款后Sportwagon外廓。	READY
16610_prefl	16610	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-GTA-SEDAN-4D-PREFL-01	HIGH	改款前GTA宽体轿车外廓。	READY
16610_facelift	16610	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-GTA-SEDAN-4D-FACELIFT-01	HIGH	改款后GTA宽体轿车外廓。	READY
16612_prefl	16612	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-PREFL-01	HIGH	改款前五门旅行车外廓。	READY
16612_facelift	16612	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-FACELIFT-01	HIGH	改款后五门旅行车外廓。	READY
16613	16613	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-PREFL-01	MEDIUM	100 kW版本对应改款前五门旅行车外廓。	READY
16614_prefl	16614	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-PREFL-01	MEDIUM	改款前五门旅行车外廓。	READY
16614_facelift	16614	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-FACELIFT-01	MEDIUM	改款后五门旅行车外廓。	READY
16615_prefl	16615	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-PREFL-01	MEDIUM	改款前五门旅行车外廓。	READY
16615_facelift	16615	Wagon	307 I		5	EU-PEUGEOT-307-I-WAGON-5D-FACELIFT-01	MEDIUM	改款后五门旅行车外廓。	READY
16617_prefl	16617	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-PREFL-01	HIGH	外观改款前四门轿车外廓。	READY
16617_facelift	16617	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-FACELIFT-01	HIGH	外观改款后四门轿车外廓。	READY
16618_prefl	16618	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-PREFL-01	HIGH	外观改款前四门轿车外廓。	READY
16618_facelift	16618	Sedan	156 I	932	4	EU-ALFA-ROMEO-156-I-932-SEDAN-4D-FACELIFT-01	HIGH	外观改款后四门轿车外廓。	READY
16619_prefl	16619	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-PREFL-01	HIGH	外观改款前Sportwagon外廓。	READY
16619_facelift	16619	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-FACELIFT-01	HIGH	外观改款后Sportwagon外廓。	READY
16620_prefl	16620	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-PREFL-01	HIGH	外观改款前Sportwagon外廓。	READY
16620_facelift	16620	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-WAGON-5D-FACELIFT-01	HIGH	外观改款后Sportwagon外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-307-I-HATCHBACK-3D-PREFL-01	4202	1730	1512	Automobile-Catalog 2002 Peugeot 307 1.4 HDi 70; AutoEvolution Peugeot 307 3 Doors 2001-2005	https://www.automobile-catalog.com/car/2002/2617280/peugeot_307_1_4_hdi_70.html; https://www.autoevolution.com/cars/peugeot-307-3-doors-2001.html
EU-PEUGEOT-307-I-HATCHBACK-3D-FACELIFT-01	4212	1746	1510	Automobile-Catalog 2006 Peugeot 307 1.4 16V 90; AutoEvolution Peugeot 307 3 Doors 2005-2008	https://www.automobile-catalog.com/car/2006/2617835/peugeot_307_1_4_16v_90.html; https://www.autoevolution.com/cars/peugeot-307-3-doors-2005.html
EU-PEUGEOT-307-I-HATCHBACK-5D-PREFL-01	4202	1730	1512	Automobile-Catalog 2002 Peugeot 307 1.4 HDi 70; AutoEvolution Peugeot 307 5 Doors 2001-2005	https://www.automobile-catalog.com/car/2002/2617280/peugeot_307_1_4_hdi_70.html; https://www.autoevolution.com/cars/peugeot-307-5-doors-2001.html
EU-PEUGEOT-307-I-HATCHBACK-5D-FACELIFT-01	4212	1746	1510	Automobile-Catalog 2006 Peugeot 307 1.4 16V 90; AutoEvolution Peugeot 307 5 Doors 2005-2008	https://www.automobile-catalog.com/car/2006/2617835/peugeot_307_1_4_16v_90.html; https://www.autoevolution.com/cars/peugeot-307-5-doors-2005.html
EU-PEUGEOT-307-I-WAGON-5D-PREFL-01	4419	1757	1544	Automobile-Catalog 2002 Peugeot 307 Break 1.6 16V 110	https://www.automobile-catalog.com/car/2002/2617340/peugeot_307_break_estate_1_6_16v_110.html
EU-PEUGEOT-307-I-WAGON-5D-FACELIFT-01	4432	1757	1544	Automobile-Catalog 2006 Peugeot 307 Break 1.6 16V 110	https://www.automobile-catalog.com/car/2006/2617970/peugeot_307_break_estate_1_6_16v_110.html
EU-ALFA-ROMEO-156-I-932-SEDAN-4D-PREFL-01	4430	1745	1415	Automobile-Catalog 2002 Alfa Romeo 156 1.9 JTD	https://www.automobile-catalog.com/car/2002/219335/alfa_romeo_156_1_9_jtd.html
EU-ALFA-ROMEO-156-I-932-SEDAN-4D-FACELIFT-01	4435	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 2.0 JTS 16V	https://www.automobile-catalog.com/car/2004/220325/alfa_romeo_156_2_0_jts_16v_progression_classic__turismo_or_veloce.html
EU-ALFA-ROMEO-156-I-932-WAGON-5D-PREFL-01	4430	1745	1420	Automobile-Catalog 2002 Alfa Romeo 156 Sportwagon 1.9 JTD	https://www.automobile-catalog.com/car/2002/219455/alfa_romeo_156_sportwagon_1_9_jtd.html
EU-ALFA-ROMEO-156-I-932-WAGON-5D-FACELIFT-01	4441	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon 2.0 JTS 16V Selespeed	https://www.automobile-catalog.com/car/2004/220190/alfa_romeo_156_sportwagon_2_0_jts_16v_distinctive_exclusive__lusso_selespeed.html
EU-ALFA-ROMEO-156-I-932-GTA-SEDAN-4D-PREFL-01	4430	1765	1402	Automobile-Catalog 2002 Alfa Romeo 156 GTA	https://www.automobile-catalog.com/car/2002/219980/alfa_romeo_156_gta.html
EU-ALFA-ROMEO-156-I-932-GTA-SEDAN-4D-FACELIFT-01	4435	1765	1402	Automobile-Catalog 2004 Alfa Romeo 156 GTA	https://www.automobile-catalog.com/car/2004/220130/alfa_romeo_156_gta.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz W211 Sedan 与 CLK C209 Coupe，并处理覆盖多个悬架高度或改款阶段的版本。
2. 解决 Opel Vectra C CC 3.2 V6 输入结束年月与实际改款/发动机停产边界冲突。
3. 闭合 Lancia Lybra Sedan/Wagon、Fiat Multipla 与 Ford Mondeo III 三种车身。
4. 处理 MG ZR、ZS、TF 后，再集中处理 Transit、Sprinter、Kangoo 等商用车多轴距和多车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/2617280/peugeot_307_1_4_hdi_70.html?utm_source=chatgpt.com "2002 Peugeot 307 1.4 HDi 70 Specs Review (50 kW ..."
[2]: https://www.automobile-catalog.com/car/2002/219980/alfa_romeo_156_gta.html?utm_source=chatgpt.com "2002 Alfa Romeo 156 GTA Specs Review (184 kW / 250 PS / 247 hp) (since mid-year 2002 for Europe Australia )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz W211 五个 Ktype。E 240/E 220 CDI、E 320/E 270 CDI 分别按标准悬架与低车身运动悬架拆分；E 500 使用其标准 AIRMATIC 外廓。Mercedes-Benz 官方档案确认各分支长宽一致，但车身高度存在明确差异。([marsClassic][1])
* 闭合 CLK C209 的 CLK 320、CLK 500。两者因保险杠/外廓长度及标准高度不同分别建组，并各自保留运动悬架低车身分支。([marsClassic][2])

## 当前批次进度

* READY Ktype：70 / 100
* READY 映射行：117
* PENDING Ktype：30
* 已确认尺寸组：66
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16564_standard	16564	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1449-01	HIGH	标准悬架四门轿车外廓。	READY
16564_sport	16564	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1432-01	HIGH	运动悬架低车身四门轿车外廓。	READY
16565	16565	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-AIRMATIC-H1430-01	HIGH	E 500标准AIRMATIC四门轿车外廓。	READY
16593_standard	16593	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1450-01	HIGH	标准悬架四门轿车外廓。	READY
16593_sport	16593	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1433-01	HIGH	运动悬架低车身四门轿车外廓。	READY
16594_standard	16594	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1450-01	HIGH	标准悬架四门轿车外廓。	READY
16594_sport	16594	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1433-01	HIGH	运动悬架低车身四门轿车外廓。	READY
16595_standard	16595	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1449-01	HIGH	标准悬架四门轿车外廓。	READY
16595_sport	16595	Sedan	E-Klasse W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1432-01	HIGH	运动悬架低车身四门轿车外廓。	READY
16629_standard	16629	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-320-STANDARD-01	HIGH	CLK 320标准悬架双门Coupe外廓。	READY
16629_sport	16629	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-320-SPORT-01	HIGH	CLK 320运动悬架低车身外廓。	READY
16630_standard	16630	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-500-STANDARD-01	HIGH	CLK 500标准悬架双门Coupe外廓。	READY
16630_sport	16630	Coupe	CLK II	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-500-SPORT-01	HIGH	CLK 500运动悬架低车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1449-01	4818	1822	1449	Mercedes-Benz Public Archive E 320; Mercedes-Benz Public Archive E 270 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-320.xhtml?oid=5373; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-270-CDI.xhtml?oid=5370
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1432-01	4818	1822	1432	Mercedes-Benz Public Archive E 320; Mercedes-Benz Public Archive E 270 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-320.xhtml?oid=5373; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-270-CDI.xhtml?oid=5370
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-STANDARD-H1450-01	4818	1822	1450	Mercedes-Benz Public Archive E 240; Mercedes-Benz Public Archive E 220 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240.xhtml?oid=5372; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=5369
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-SPORT-H1433-01	4818	1822	1433	Mercedes-Benz Public Archive E 240; Mercedes-Benz Public Archive E 220 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240.xhtml?oid=5372; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI.xhtml?oid=5369
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-AIRMATIC-H1430-01	4818	1822	1430	Mercedes-Benz Public Archive E 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500.xhtml?oid=5374
EU-MERCEDES-BENZ-CLK-C209-COUPE-320-STANDARD-01	4638	1740	1413	Mercedes-Benz Public Archive CLK 320	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-320.xhtml?oid=4610
EU-MERCEDES-BENZ-CLK-C209-COUPE-320-SPORT-01	4638	1740	1400	Mercedes-Benz Public Archive CLK 320	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-320.xhtml?oid=4610
EU-MERCEDES-BENZ-CLK-C209-COUPE-500-STANDARD-01	4643	1740	1415	Mercedes-Benz Public Archive CLK 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-500.xhtml?oid=4611
EU-MERCEDES-BENZ-CLK-C209-COUPE-500-SPORT-01	4643	1740	1400	Mercedes-Benz Public Archive CLK 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-500.xhtml?oid=4611
```

## 下一步优先处理

1. 闭合 Audi RS6 C5 Sedan/Avant、VW Phaeton W12 的标准轴距和长轴距边界。
2. 批量处理 Lancia Lybra Sedan/Wagon、Fiat Multipla、Hyundai Accent II 与 Renault Espace III。
3. 闭合 MG ZR、ZS、TF 和 Ford Mondeo III 三种车身。
4. 最后集中处理 Transit、Sprinter、Kangoo 等多轴距、多车顶商用车型。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-320.xhtml?oid=5373 "E 320"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-500.xhtml?oid=4611 "CLK 500"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Vectra C GTS 3.2 V6、Phaeton W12 LWB、Lancia Lybra Sedan/Wagon 与 Fiat Multipla 改款前后外廓；Phaeton W12 按官方规格限定为长轴距车身。([汽车目录][1])
* 闭合 Hyundai Accent II 三门/五门及 LC/LC2 改款分支；汽油车型改款后高度采用 1395 mm，不套用柴油车型的 1405 mm。([汽车目录][2])
* 闭合 Espace III、V70 II、MG ZR/ZS/TF。V70 使用官方规格中的不含后视镜宽度；MG ZR 的三个动力版本批量复用同一组三门/五门外廓。([汽车目录][3])
* 闭合 Alfa Romeo 156 Sportwagon GTA 改款前后、Audi RS6 C5 Sedan/Avant，以及 Mondeo III ST220 三种车身。([汽车目录][4])

## 当前批次进度

* READY Ktype：92 / 100
* READY 映射行：147
* PENDING Ktype：8
* 已确认尺寸组：90
* 本轮首次创建尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16530	16530	Hatchback	Vectra C		5	EU-OPEL-VECTRA-C-GTS-HATCHBACK-5D-PREFL-01	HIGH	3.2 V6对应改款前GTS五门外廓。	READY
16561	16561	Sedan	Phaeton I	3D	4	EU-VW-PHAETON-I-3D-SEDAN-LWB-W12-01	HIGH	W12对应长轴距四门轿车外廓。	READY
16587	16587	Sedan	Lybra I	839	4	EU-LANCIA-LYBRA-I-839-SEDAN-4D-01	HIGH	839四门轿车外廓。	READY
16588	16588	Wagon	Lybra I	839	5	EU-LANCIA-LYBRA-I-839-WAGON-5D-01	HIGH	839五门旅行车外廓。	READY
16589_prefl	16589	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-I-186-MPV-5D-PREFL-01	HIGH	改款前五门MPV外廓。	READY
16589_facelift	16589	MPV	Multipla I	186	5	EU-FIAT-MULTIPLA-I-186-MPV-5D-FACELIFT-01	HIGH	改款后五门MPV外廓。	READY
16590_3dr_prefl	16590	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	LC改款前三门掀背外廓。	READY
16590_5dr_prefl	16590	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	LC改款前五门掀背外廓。	READY
16590_3dr_facelift	16590	Hatchback	Accent II	LC2	3	EU-HYUNDAI-ACCENT-II-LC2-HATCHBACK-3D-FACELIFT-01	HIGH	LC2改款后三门掀背外廓。	READY
16590_5dr_facelift	16590	Hatchback	Accent II	LC2	5	EU-HYUNDAI-ACCENT-II-LC2-HATCHBACK-5D-FACELIFT-01	HIGH	LC2改款后五门掀背外廓。	READY
16598	16598	MPV	Espace III	JE	5	EU-RENAULT-ESPACE-III-JE-MPV-5D-01	HIGH	JE标准轴距五门MPV外廓。	READY
16599	16599	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-5D-01	HIGH	前驱五门旅行车标准外廓。	READY
16604_3dr	16604	Hatchback	ZR I		3	EU-MG-ZR-I-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
16604_5dr	16604	Hatchback	ZR I		5	EU-MG-ZR-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
16605_3dr	16605	Hatchback	ZR I		3	EU-MG-ZR-I-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
16605_5dr	16605	Hatchback	ZR I		5	EU-MG-ZR-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
16606_3dr	16606	Hatchback	ZR I		3	EU-MG-ZR-I-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
16606_5dr	16606	Hatchback	ZR I		5	EU-MG-ZR-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
16608	16608	Sedan	ZS I		4	EU-MG-ZS-I-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
16609	16609	Hatchback	ZS I		5	EU-MG-ZS-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
16611_prefl	16611	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-GTA-WAGON-5D-PREFL-01	HIGH	改款前GTA Sportwagon外廓。	READY
16611_facelift	16611	Wagon	156 I	932	5	EU-ALFA-ROMEO-156-I-932-GTA-WAGON-5D-FACELIFT-01	HIGH	改款后GTA Sportwagon外廓。	READY
16621	16621	Convertible	TF I	RD	2	EU-MG-TF-I-RD-CONVERTIBLE-2D-01	HIGH	RD双门敞篷外廓。	READY
16622	16622	Convertible	TF I	RD	2	EU-MG-TF-I-RD-CONVERTIBLE-2D-01	HIGH	RD双门敞篷外廓。	READY
16623	16623	Convertible	TF I	RD	2	EU-MG-TF-I-RD-CONVERTIBLE-2D-01	HIGH	RD双门敞篷外廓。	READY
16627	16627	Sedan	RS6 C5	4B	4	EU-AUDI-RS6-C5-4B-SEDAN-4D-01	HIGH	4B宽体四门RS6外廓。	READY
16628	16628	Wagon	RS6 C5	4B	5	EU-AUDI-RS6-C5-4B-WAGON-5D-01	HIGH	4B宽体五门RS6 Avant外廓。	READY
16632	16632	Hatchback	Mondeo III	B4Y	5	EU-FORD-MONDEO-III-B4Y-HATCHBACK-5D-ST220-01	HIGH	B4Y五门ST220外廓。	READY
16633	16633	Sedan	Mondeo III	B5Y	4	EU-FORD-MONDEO-III-B5Y-SEDAN-4D-ST220-01	HIGH	B5Y四门ST220外廓。	READY
16634	16634	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-BWY-WAGON-5D-ST220-01	HIGH	BWY五门ST220旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VECTRA-C-GTS-HATCHBACK-5D-PREFL-01	4596	1798	1460	Automobile-Catalog 2002 Opel Vectra GTS 3.2 V6	https://www.automobile-catalog.com/car/2002/2522420/opel_vectra_gts_3_2_v6.html
EU-VW-PHAETON-I-3D-SEDAN-LWB-W12-01	5175	1903	1450	Volkswagen Phaeton official technical specification	https://www.vwpress.co.uk/assets/documents/original/16822-phaeton_spec.pdf
EU-LANCIA-LYBRA-I-839-SEDAN-4D-01	4466	1743	1462	Automobile-Catalog 2002 Lancia Lybra 1.9 JTD	https://www.automobile-catalog.com/car/2002/1384805/lancia_lybra_1_9_jtd.html
EU-LANCIA-LYBRA-I-839-WAGON-5D-01	4466	1743	1470	Automobile-Catalog 2002 Lancia Lybra Station Wagon 1.9 JTD	https://www.automobile-catalog.com/car/2002/1384835/lancia_lybra_station_wagon_1_9_jtd.html
EU-FIAT-MULTIPLA-I-186-MPV-5D-PREFL-01	3994	1871	1695	Automobile-Catalog 2002 Fiat Multipla 100 16V Bipower	https://www.automobile-catalog.com/car/2002/723515/fiat_multipla_100_16v_bipower_gasolina.html
EU-FIAT-MULTIPLA-I-186-MPV-5D-FACELIFT-01	4089	1871	1721	Automobile-Catalog Fiat Multipla 1.6 16V Natural Power	https://www.automobile-catalog.com/car/2006/723680/fiat_multipla_1_6_16v_natural_power_cng.html
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	4200	1670	1395	Automobile-Catalog 2002 Hyundai Accent 1.5 MVi 3-Dr	https://www.automobile-catalog.com/car/2002/1168310/hyundai_accent_1_5_mvi_3-dr.html
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	4200	1670	1395	Automobile-Catalog 2002 Hyundai Accent 1.5 GLS 5-Dr	https://www.automobile-catalog.com/car/2002/1168070/hyundai_accent_1_5_gls_5-dr.html
EU-HYUNDAI-ACCENT-II-LC2-HATCHBACK-3D-FACELIFT-01	4215	1680	1395	Automobile-Catalog 2004 Hyundai Accent 1.6 Fun 3-Dr	https://www.automobile-catalog.com/car/2004/1168385/hyundai_accent_1_6_fun_3-dr.html
EU-HYUNDAI-ACCENT-II-LC2-HATCHBACK-5D-FACELIFT-01	4215	1680	1395	Automobile-Catalog 2004 Hyundai Accent 1.6 CDX 5-Dr	https://www.automobile-catalog.com/car/2004/1168490/hyundai_accent_1_6_cdx_5-dr.html
EU-RENAULT-ESPACE-III-JE-MPV-5D-01	4517	1810	1690	Automobile-Catalog Renault Espace 2.0 16V	https://www.automobile-catalog.com/car/1999/2948135/renault_espace_2_0_16v.html
EU-VOLVO-V70-II-WAGON-5D-01	4710	1804	1465	Volvo MY2003 V70 official product specification	https://www.volvoclub.org.uk/press/volvo2003uk/v70/V70_Full_Product_Spec.pdf
EU-MG-ZR-I-HATCHBACK-3D-01	4011	1688	1400	Automobile-Catalog 2002 MG ZR 105	https://www.automobile-catalog.com/car/2002/1702625/mg_zr_105.html
EU-MG-ZR-I-HATCHBACK-5D-01	4011	1688	1400	Automobile-Catalog 2002 MG ZR 105	https://www.automobile-catalog.com/car/2002/1702625/mg_zr_105.html
EU-MG-ZS-I-SEDAN-4D-01	4530	1696	1390	Automobile-Catalog 2002 MG ZS 120 Saloon	https://www.automobile-catalog.com/car/2002/1703000/mg_zs_120_saloon.html
EU-MG-ZS-I-HATCHBACK-5D-01	4377	1696	1386	Automobile-Catalog 2002 MG ZS 120 Hatchback	https://www.automobile-catalog.com/car/2002/1702910/mg_zs_120_hatchback.html
EU-ALFA-ROMEO-156-I-932-GTA-WAGON-5D-PREFL-01	4430	1765	1411	Automobile-Catalog 2002 Alfa Romeo 156 Sportwagon GTA	https://www.automobile-catalog.com/car/2002/219965/alfa_romeo_156_sportwagon_gta.html
EU-ALFA-ROMEO-156-I-932-GTA-WAGON-5D-FACELIFT-01	4441	1765	1390	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon GTA Selespeed	https://www.automobile-catalog.com/car/2004/221405/alfa_romeo_156_sportwagon_gta_selespeed.html
EU-MG-TF-I-RD-CONVERTIBLE-2D-01	3943	1628	1261	Automobile-Catalog 2002 MG TF 135	https://www.automobile-catalog.com/car/2002/1702205/mg_tf_135.html
EU-AUDI-RS6-C5-4B-SEDAN-4D-01	4858	1850	1425	Automobile-Catalog 2002 Audi RS6	https://www.automobile-catalog.com/car/2002/245600/audi_rs6_tiptronic.html
EU-AUDI-RS6-C5-4B-WAGON-5D-01	4858	1850	1425	Automobile-Catalog 2002 Audi RS6 Avant	https://www.automobile-catalog.com/car/2002/245585/audi_rs6_avant_tiptronic.html
EU-FORD-MONDEO-III-B4Y-HATCHBACK-5D-ST220-01	4731	1812	1415	Automobile-Catalog 2002 Ford Mondeo 5-door ST220	https://www.automobile-catalog.com/car/2002/971120/ford_mondeo_5-dr_st_220.html
EU-FORD-MONDEO-III-B5Y-SEDAN-4D-ST220-01	4731	1812	1415	Automobile-Catalog 2002 Ford Mondeo 4-door ST220	https://www.automobile-catalog.com/car/2002/971105/ford_mondeo_4-dr_st_220.html
EU-FORD-MONDEO-III-BWY-WAGON-5D-ST220-01	4804	1812	1427	Automobile-Catalog 2002 Ford Mondeo Turnier ST220	https://www.automobile-catalog.com/car/2002/971135/ford_mondeo_turnier_st_220.html
```

## 下一步优先处理

1. 集中闭合 Transit Ktype `16551`、`16562`、`16563`，按代际、改款阶段、轴距和车顶拆分，并优先复用已有 VE6 尺寸组。
2. 处理 Thalia I Ktype `16553`、`16554` 的改款阶段。
3. 处理 Kangoo Ktype `16555` 的 Van/MPV 与改款前后边界，优先关联现有 Kangoo I 尺寸组。
4. 最后闭合 Sprinter Ktype `16574`、`16575` 的轴距、车顶及平台/Bus 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/1384835/lancia_lybra_station_wagon_1_9_jtd.html?utm_source=chatgpt.com "2002 Lancia Lybra Station Wagon 1.9 JTD (man. 5)"
[2]: https://www.automobile-catalog.com/car/2002/1168310/hyundai_accent_1_5_mvi_3-dr.html?utm_source=chatgpt.com "2002 Hyundai Accent 1.5 MVi 3-Dr Specs Review (73.5 kW ..."
[3]: https://www.automobile-catalog.com/car/1999/2948135/renault_espace_2_0_16v.html?utm_source=chatgpt.com "1999 Renault Espace 2.0 16V Specs Review (103 kW ..."
[4]: https://www.automobile-catalog.com/car/2002/219965/alfa_romeo_156_sportwagon_gta.html?utm_source=chatgpt.com "2002 Alfa Romeo 156 Sportwagon GTA Specs Review (184 kW ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Transit Mk6 2.4 TDE 125 PS 的 V185 长轴中顶 Bus 外廓；官方规格明确宽度 1974 mm 为不含后视镜口径，具体 350 L Bus 规格为 5651×1974×2351 mm。([Dezo's Garage][1])
* 闭合 Thalia I 改款前、改款后两个外廓；长度由 4150 mm 变为 4171 mm，宽度和高度保持 1639×1437 mm。([汽车数据网][2])
* 为 Kangoo I Express FC 改款前 Van 首次建组；其余 Kangoo I、Transit VE64/VE83 分支直接复用已有尺寸组。Kangoo Express 改款前 1.5 dCi 外廓为 3995×1663×1827 mm。([车艺网][3])

## 当前批次进度

* READY Ktype：98 / 100
* READY 映射行：164
* PENDING Ktype：2
* 已确认尺寸组：94
* 本轮首次创建尺寸组：4
* 剩余：`16574`、`16575`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16551_lwb_midroof	16551	MPV	Transit Mk6	V185		EU-FORD-TRANSIT-MK6-V185-BUS-LWB-MIDROOF-01	HIGH	长轴中顶Bus外廓。	READY
16553_prefl	16553	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-4D-PREFL-01	HIGH	改款前四门轿车外廓。	READY
16553_facelift	16553	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-4D-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
16554_prefl	16554	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-4D-PREFL-01	HIGH	改款前四门轿车外廓。	READY
16554_facelift	16554	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-4D-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
16555_mpv_prefl	16555	MPV	Kangoo I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	改款前KC乘用车外廓。	READY
16555_van_prefl	16555	Van	Kangoo I	FC		EU-RENAULT-KANGOO-I-FC-VAN-PREFL-01	HIGH	改款前FC厢式车外廓。	READY
16555_mpv_facelift	16555	MPV	Kangoo I	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	改款后KC标准高度乘用车外廓。	READY
16555_van_facelift	16555	Van	Kangoo I	FC		EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	HIGH	改款后FC厢式车外廓。	READY
16562_swb_pre92	16562	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	MEDIUM	1992年前短轴低顶Bus外廓。	READY
16562_lwb_pre92	16562	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	MEDIUM	1992年前长轴中顶Bus外廓。	READY
16562_swb_post92	16562	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	MEDIUM	1992年后短轴低顶Bus外廓。	READY
16562_lwb_post92	16562	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	MEDIUM	1992年后长轴中顶Bus外廓。	READY
16563_swb_lowroof	16563	MPV	Transit Mk4	VE83		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
16563_swb_midroof	16563	MPV	Transit Mk4	VE83		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶Bus外廓。	READY
16563_lwb_midroof	16563	MPV	Transit Mk4	VE83		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
16563_lwb_highroof	16563	MPV	Transit Mk4	VE83		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK6-V185-BUS-LWB-MIDROOF-01	5651	1974	2351	Ford Transit official specifications October 2002; Coches.net Ford Transit 350 L Bus M2 14 plazas 125 CV	https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf; https://www.coches.net/fichas_tecnicas/ford/transit/industriales/4-puertas/350_l_bus_m2_14_plazas_125cv_asm_125cv_diesel/21341/41388020050101/
EU-RENAULT-THALIA-I-SEDAN-4D-PREFL-01	4150	1639	1437	Auto-Data Renault Clio Symbol I 1.4 75 Hp	https://www.auto-data.net/en/renault-clio-symbol-i-1.4-75hp-10428
EU-RENAULT-THALIA-I-SEDAN-4D-FACELIFT-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 2002 1.4 16V 98 Hp	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-1.4-16v-98hp-10663
EU-RENAULT-KANGOO-I-FC-VAN-PREFL-01	3995	1663	1827	Auto-Data Renault Kangoo I Express FC 1.5 dCi 65 Hp	https://www.auto-data.net/en/renault-kangoo-i-express-fc-1.5-dci-65hp-10731
```

## 下一步优先处理

1. 闭合 `16574` Sprinter 5-T 516 CDI 4X4 的单排/双排驾驶室及轴距分支。
2. 闭合 `16575` Sprinter 3.5-T 316 CDI 4X4 Bus 的车长和车顶分支。
3. 两项完成后立即执行一次机械闭合检查并输出最终两张完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2003-Ford-Transit-Specs-UK.pdf "Transit 2002.75 SPEC.qxd"
[2]: https://www.auto-data.net/en/renault-clio-symbol-i-1.4-75hp-10428?utm_source=chatgpt.com "Renault Clio Symbol I 1.4 (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.carsart.net/en/cars/renault/kangoo/i-express-fc/1500cc-dci-82hp?utm_source=chatgpt.com "2002 Renault Kangoo 1.5 dCi (82 Hp) MPG, Fuel Consumption & Reliability Review"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12701-12800_ktype_dimension_mapping_final.tsv
- all_12701-12800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口

