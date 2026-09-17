# 任务：all 第 3701-3800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0038__17252bb2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3701-3800 行

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
all 第 3701-3800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340
EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	4036	1692	1395
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	4104	1696	1397
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	4104	1696	1397
EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	4104	1696	1397
EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	4036	1692	1395
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	4108	1696	1379
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	4040	1692	1389
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	4108	1696	1370
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-PREFL-01	4036	1692	1389
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	4211	1738	1425
EU-FORD-ESCORT-V-WAGON-PREFL-01	4268	1690	1414
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490
EU-FORD-SCORPIO-I-HATCHBACK-01	4669	1760	1440
EU-FORD-SCORPIO-I-HATCHBACK-5D-01	4669	1760	1490
EU-FORD-SCORPIO-I-SEDAN-01	4744	1766	1450
EU-FORD-SCORPIO-I-SEDAN-4D-01	4744	1766	1450
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
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
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430
EU-LANCIA-DELTA-II-HATCHBACK-01	4011	1703	1430
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	4665	1800	1680
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400
EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	4239	1688	1400
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-GSI-3D-01	4086	1688	1410
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410
EU-OPEL-ASTRA-F-WAGON-5D-01	4278	1688	1475
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410
EU-TOYOTA-CARINA-E-VI-T19-WAGON-5D-01	4545	1695	1425
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	4370	1635	1320
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	4330	1635	1320
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	4370	1635	1310
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	4330	1635	1310
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	4370	1640	1315
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	4330	1640	1315
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	4370	1640	1320
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	4330	1640	1320
EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	4450	1665	1320
EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	4410	1690	1320
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	4410	1710	1290
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	4380	1710	1290
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	4365	1710	1290
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	4620	1685	1315
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	4620	1720	1315
EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	4430	1705	1320
EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	4420	1690	1300
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980
EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	4140	1695	1240
EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	4620	1745	1310
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Lancia	Delta ii	1.9 TD	Schrägheck	Frontantrieb	Diesel	66	90	Oct 1994	Aug 1999	2024-03-01	3827
Lancia	Delta ii	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	51	69	Oct 1994	Aug 1999	2024-03-01	3828
Lancia	Delta ii	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1994	Aug 1999	2024-03-01	3829
Lancia	Dedra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	74	101	Jul 1994	Jul 1999	2024-03-01	3830
Lancia	Dedra	1.6 LE CAT	Stufenheck	Frontantrieb	Benzin	66	90	Jul 1994	Jul 1999	2024-03-01	3831
Lancia	Dedra	2.0 16V	Stufenheck	Frontantrieb	Benzin	102	139	Jul 1994	Jul 1999	2024-03-01	3832
Lancia	Dedra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1993	Jul 1999	2024-03-01	3833
Lancia	Dedra	1.8 I.e.	Kombi	Frontantrieb	Benzin	74	101	Jul 1994	Jul 1999	2024-03-01	3834
Lancia	Dedra	2.0 16V	Kombi	Frontantrieb	Benzin	102	139	Jul 1994	Jul 1999	2024-03-01	3835
Lancia	Dedra	2.0 Integrale	Kombi	Allrad	Benzin	102	139	Jul 1994	Jul 1999	2024-03-01	3836
Lancia	Dedra	1.9 TDS	Kombi	Frontantrieb	Diesel	66	90	Jul 1994	Jul 1999	2024-03-01	3837
Lancia	Kappa	2.0 20V	Stufenheck	Frontantrieb	Benzin	107	146	Oct 1994	Oct 2001	2024-03-01	3838
Lancia	Kappa	2.4 20V	Stufenheck	Frontantrieb	Benzin	129	175	Aug 1994	Oct 2001	2024-03-01	3839
Lancia	Kappa	3.0 24V	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1994	Oct 2001	2024-03-01	3840
Lancia	Kappa	2.4 T.ds	Stufenheck	Frontantrieb	Diesel	91	124	Aug 1994	Oct 2001	2024-03-01	3841
BMW	3	M3 3.0	Coupe	Heckantrieb	Benzin	210	286	Nov 1992	Jul 1995	2024-03-01	3842
BMW	8	850 CSI	Coupe	Heckantrieb	Benzin	280	380	Nov 1992	Dec 1996	2024-03-01	3843
Mitsubishi	Outlander ii	2.2 Di-d 4WD	SUV	Allrad	Diesel	103	140	Sep 2010	Nov 2012	2024-03-01	3844
BMW	3	M3 3.0	Cabriolet	Heckantrieb	Benzin	210	286	Apr 1994	Jul 1995	2024-03-01	3845
BMW	5	M5	Kombi	Heckantrieb	Benzin	250	340	Apr 1992	Jul 1995	2024-03-01	3846
Toyota	Celica	1.8 I 16V	Coupe	Frontantrieb	Benzin	85	116	Nov 1993	Nov 1999	2024-03-01	3847
Toyota	Celica	2.0 I 16V	Coupe	Frontantrieb	Benzin	129	175	Nov 1993	Nov 1999	2024-03-01	3848
Toyota	Celica	2.0 I Turbo 4WD	Coupe	Allrad	Benzin	178	242	Feb 1994	Nov 1999	2024-03-01	3849
Toyota	Carina e vi	2.0 GTI 16V	Stufenheck	Frontantrieb	Benzin	129	175	Mar 1994	Sep 1997	2024-03-01	3850
Toyota	Carina e vi	2.0 GTI 16V	Schrägheck	Frontantrieb	Benzin	129	175	Mar 1994	Sep 1997	2024-03-01	3851
Toyota	Mr2 ii	2.0 16V	Coupe	Heckantrieb	Benzin	129	175	Dec 1989	Jul 1999	2024-03-01	3852
Toyota	Hiace iv	2.4 D	Bus	Heckantrieb	Diesel	57	78	Aug 1989	Dec 2004	2024-03-01	3853
Toyota	4	3.0 TD	SUV	Allrad	Diesel	92	125	Oct 1993	Mar 1996	2025-02-03	3854
Lexus	Es	300	Stufenheck	Frontantrieb	Benzin	138	188	Sep 1991	Dec 1997	2024-03-01	3855
Toyota	Supra	3.0 I Bi-turbo	Coupe	Heckantrieb	Benzin	243	330	May 1993	Jul 2002	2024-03-01	3856
Toyota	Rav 4 i	2.0 4WD	SUV	Allrad	Benzin	95	129	Jun 1994	Jun 2000	2024-03-01	3857
Opel	Omega b	2	Stufenheck	Heckantrieb	Benzin	85	116	Mar 1994	Sep 1999	2024-03-01	3858
Opel	Omega b	2.0 16V	Stufenheck	Heckantrieb	Benzin	100	136	Mar 1994	Sep 1999	2024-03-01	3859
Opel	Omega b	2.5 V6	Stufenheck	Heckantrieb	Benzin	125	170	Mar 1994	Sep 2000	2024-03-01	3860
Opel	Omega b	3.0 V6	Stufenheck	Heckantrieb	Benzin	155	211	Apr 1994	Feb 2001	2024-03-01	3861
Opel	Omega b	2.5 TD	Stufenheck	Heckantrieb	Diesel	96	130	Apr 1994	Jul 2003	2024-03-01	3862
Opel	Omega b caravan	2	Kombi	Heckantrieb	Benzin	85	116	Mar 1994	Sep 1999	2024-03-01	3863
Opel	Omega b caravan	2.0 16V	Kombi	Heckantrieb	Benzin	100	136	Mar 1994	Sep 1999	2024-03-01	3864
Opel	Omega b caravan	2.5 V6	Kombi	Heckantrieb	Benzin	125	170	Mar 1994	Sep 2000	2024-03-01	3865
Opel	Omega b caravan	2.5 TD	Kombi	Heckantrieb	Diesel	96	131	Apr 1994	Jul 2001	2024-03-01	3866
Opel	Omega b caravan	3.0 V6	Kombi	Heckantrieb	Benzin	155	211	Apr 1994	Feb 2001	2024-03-01	3867
Opel	Astra f	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	85	116	Nov 1994	Sep 1998	2024-03-01	3868
Opel	Astra f cc	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	85	116	Sep 1994	Jan 1998	2024-03-01	3869
Opel	Vectra a	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1992	Aug 1995	2024-03-01	3870
Opel	Vectra a cc	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1992	Aug 1995	2024-03-01	3871
Opel	Vectra a	2.0 I 16V 4X4	Stufenheck	Allrad	Benzin	100	136	Jun 1994	Nov 1995	2024-03-01	3872
VW	Multivan t5	2.0 TDI	Bus	Frontantrieb	Diesel	100	136	May 2010	Aug 2015	2024-03-01	3873
VW	Multivan t5	2.0 TDI 4motion	Bus	Allrad	Diesel	100	136	May 2010	Aug 2015	2024-03-01	3874
Opel	Corsa b	1.4 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1994	Sep 2000	2024-03-01	3875
Opel	Corsa b	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	78	106	Sep 1994	Sep 2000	2024-03-01	3876
Opel	Astra f cc	1.7 TD	Schrägheck	Frontantrieb	Diesel	50	68	Nov 1994	Jan 1998	2024-03-01	3877
Opel	Astra f caravan	1.7 TD	Kombi	Frontantrieb	Diesel	50	68	Nov 1994	Jan 1998	2024-03-01	3878
Opel	Astra f	1.7 TD	Stufenheck	Frontantrieb	Diesel	50	68	Nov 1994	Sep 1998	2024-03-01	3879
Opel	Astra f	1.8 I 16V	Cabriolet	Frontantrieb	Benzin	85	116	Nov 1994	Mar 2001	2024-03-01	3880
Audi	A8 d2	4.2 Quattro	Stufenheck	Allrad	Benzin	220	299	Mar 1994	Nov 1998	2024-03-01	3881
Audi	A8 d2	2.8	Stufenheck	Frontantrieb	Benzin	128	174	Mar 1994	Mar 1996	2024-03-01	3882
Ford	Escort v	RS 2000 4X4	Schrägheck	Allrad	Benzin	110	150	May 1991	Jan 1995	2024-03-01	3883
Ford	Escort v	1.8 Xr3i 16V 4X4	Schrägheck	Allrad	Benzin	77	105	Aug 1993	Jan 1995	2024-03-01	3884
Audi	A6 c4	1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Jun 1994	Oct 1997	2024-03-01	3885
Audi	A6 c4 avant	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Jun 1994	Dec 1997	2024-03-01	3886
Ford	Escort v	1.8 Xr3i 16V 4X4	Schrägheck	Allrad	Benzin	96	130	Aug 1993	Jan 1995	2024-03-01	3887
Ford	Escort v	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1990	Dec 1994	2024-03-01	3890
Audi	A8 d2	2.8 Quattro	Stufenheck	Allrad	Benzin	128	174	Mar 1994	Mar 1996	2024-03-01	3891
Audi	A8 d2	4.2 Quattro	Stufenheck	Allrad	Benzin	180	245	Mar 1994	Jul 1996	2024-03-01	3892
Audi	A6 c4	2.5 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Aug 1994	Oct 1997	2024-03-01	3893
Audi	A6 c4 avant	2.5 TDI	Kombi	Frontantrieb	Diesel	103	140	Aug 1994	Dec 1997	2024-03-01	3894
Ford	Escort v	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1993	Jan 1995	2024-03-01	3895
Ford	Escort v turnier	1.4	Kombi	Frontantrieb	Benzin	55	75	Jan 1994	Jan 1995	2024-03-01	3896
Ford	Escort v	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	65	88	Jan 1994	Jan 1995	2024-03-01	3897
Ford	Escort v	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	65	88	Jan 1994	Jan 1995	2024-03-01	3898
Ford	Escort v turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	65	88	Jan 1994	Jan 1995	2024-03-01	3899
Ford	Fiesta iii	1.6	Schrägheck	Frontantrieb	Benzin	65	88	Jan 1989	Jan 1994	2024-03-01	3900
Ford	Escort v	1.4 I	Cabriolet	Frontantrieb	Benzin	55	75	Jul 1993	Jan 1995	2024-03-01	3902
Ford	Escort v	1.6 I 16V	Cabriolet	Frontantrieb	Benzin	65	88	Feb 1994	Jan 1995	2024-03-01	3903
Ford	Transit	2.5 DI	Bus	Heckantrieb	Diesel	56	76	Jul 1994	Mar 2000	2024-03-01	3905
Dacia	Logan	1.4	Pick-up	Frontantrieb	Benzin	55	75	Jan 2009	-	2024-03-01	3906
Ford	Transit	2.5 DI	Bus	Heckantrieb	Diesel	51	69	Aug 1994	Mar 2000	2024-03-01	3908
Mazda	6	2.2 Mzr-cd	Schrägheck	Frontantrieb	Diesel	132	180	Jan 2010	Dec 2012	2024-03-01	3909
Mazda	6	2.2 D	Schrägheck	Frontantrieb	Diesel	95	129	Jan 2010	Dec 2012	2024-03-01	3910
Ford	Mondeo i turnier	1.8 I 16V	Kombi	Frontantrieb	Benzin	82	112	Jul 1994	Aug 1996	2024-03-01	3911
Ford	Mondeo i	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	82	112	Jul 1994	Aug 1996	2024-03-01	3912
Ford	Mondeo i	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	82	112	Jan 1994	Aug 1996	2024-03-01	3913
Ford	Mondeo i	2.5 I 24V	Schrägheck	Frontantrieb	Benzin	125	170	Jul 1994	Aug 1996	2024-03-01	3914
Ford	Mondeo i	2.5 I 24V	Stufenheck	Frontantrieb	Benzin	125	170	Jul 1994	Aug 1996	2024-03-01	3915
Ford	Mondeo i	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	65	88	Jul 1994	Aug 1996	2024-03-01	3916
Ford	Mondeo i	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	65	88	Jul 1994	Aug 1996	2024-03-01	3917
Ford	Mondeo i turnier	2.5 I 24V	Kombi	Frontantrieb	Benzin	125	170	Jul 1994	Aug 1996	2024-03-01	3918
Ford	Mondeo i turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	65	88	Jul 1994	Aug 1996	2024-03-01	3919
Ford	Scorpio i turnier	2.9 24V	Kombi	Heckantrieb	Benzin	143	195	Aug 1993	Sep 1994	2024-03-01	3920
Ford	Scorpio i	2.5 TD	Schrägheck	Heckantrieb	Diesel	85	115	Aug 1993	Sep 1994	2024-03-01	3921
Ford	Scorpio i	2.5 TD	Stufenheck	Heckantrieb	Diesel	85	115	Aug 1993	Sep 1994	2024-03-01	3922
Ford	Scorpio i turnier	2.5 TD	Kombi	Heckantrieb	Diesel	85	115	Aug 1993	Sep 1994	2024-03-01	3923
VW	Golf iii	2.9 VR6 Syncro	Schrägheck	Allrad	Benzin	140	190	Oct 1994	Aug 1997	2024-03-01	3924
VW	Passat b3/b4 variant	2.9 VR6 Syncro	Kombi	Allrad	Benzin	135	184	Jan 1994	May 1997	2024-03-01	3925
Mazda	6	2.0 MZR	Schrägheck	Frontantrieb	Benzin	114	155	Jan 2010	Dec 2012	2024-03-01	3926
VW	Passat b3/b4	2.0 16V	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1994	Aug 1996	2024-03-01	3927
VW	Passat b3/b4 variant	2.0 16V	Kombi	Frontantrieb	Benzin	110	150	Jan 1994	May 1997	2024-03-01	3928
VW	Golf iii variant	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Mar 1994	Apr 1999	2024-03-01	3929
Mazda	6	2.0 MZR	Kombi	Frontantrieb	Benzin	114	155	Jan 2010	Jul 2013	2024-03-01	3930
VW	Polo	55 1.3	Schrägheck	Frontantrieb	Benzin	40	55	Oct 1994	Apr 1997	2024-03-01	3931


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成 **62/100 个输入 Ktype** 的物理外廓闭合，共形成 **74 条 READY 映射**。
* 本轮复用历史尺寸组 17 个，首次创建尺寸组 21 个。
* `3857` 已拆分为 RAV4 I 三门、五门；Omega B 跨 1999 年改款的记录已拆分前期与改款外廓。
* Multivan T5 的 FWD 与 4MOTION 三维一致，复用同一个尺寸组；Toyota“4”已确认对应五门 Toyota 4Runner II 3.0 TD。([汽车数据网][1])

## 当前批次进度

* 已闭合输入 Ktype：**62 / 100**
* READY 映射：**74**
* 待处理输入 Ktype：**38**
* 当前已引用尺寸组：**38**

  * 本轮首次创建：21
  * 复用已有缓存：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3827	3827	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3828	3828	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3829	3829	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3830	3830	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3831	3831	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3832	3832	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3833_prefl	3833	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	MEDIUM	生产区间跨越前期与改款外廓。	READY
3833_facelift	3833	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越前期与改款外廓。	READY
3834	3834	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3835	3835	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3836	3836	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3837	3837	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3838	3838	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3839	3839	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3840	3840	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3841	3841	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3842	3842	Coupe	3 Series E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
3843	3843	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850CSI-01	HIGH	850 CSi 特殊外廓高度。	READY
3844	3844	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH		READY
3845	3845	Convertible	3 Series E36	E36	2	EU-BMW-3-E36-M3-CONVERTIBLE-01	HIGH		READY
3846	3846	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-M5-WAGON-01	HIGH	M5 Touring 特殊车身高度。	READY
3847	3847	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	HIGH	三门 liftback 外廓。	READY
3848	3848	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	HIGH	三门 liftback 外廓。	READY
3849	3849	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-GTFOUR-01	HIGH	GT-Four 独立外廓。	READY
3850	3850	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
3851	3851	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	五门 liftback 外廓。	READY
3852	3852	Coupe	MR2 II	SW20	2	EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	HIGH	T-bar/targa 双门外廓。	READY
3853	3853	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH		READY
3854	3854	SUV	4Runner II	KZN130	5	EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	HIGH		READY
3855	3855	Sedan	ES II	XV10	4	EU-LEXUS-ES-II-XV10-SEDAN-01	HIGH		READY
3856	3856	Coupe	Supra IV	A80	3	EU-TOYOTA-SUPRA-IV-A80-COUPE-3D-01	HIGH		READY
3857_3dr	3857	SUV	RAV4 I	XA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3857_5dr	3857	SUV	RAV4 I	XA10	5	EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3858	3858	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH		READY
3859	3859	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH		READY
3860_prefl	3860	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3860_facelift	3860	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3861_prefl	3861	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3861_facelift	3861	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3862_prefl	3862	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3862_facelift	3862	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3863	3863	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH		READY
3864	3864	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH		READY
3865_prefl	3865	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3865_facelift	3865	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3866_prefl	3866	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3866_facelift	3866	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3867_prefl	3867	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3867_facelift	3867	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3868	3868	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
3869_3dr	3869	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3869_5dr	3869	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3870	3870	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
3871	3871	Hatchback	Vectra A CC		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH		READY
3872	3872	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
3873	3873	MPV	Multivan T5 facelift		5	EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	MEDIUM	100 kW/136 PS 版本；FWD 与 4MOTION 外廓一致。	READY
3874	3874	MPV	Multivan T5 facelift		5	EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	MEDIUM	100 kW/136 PS 版本；FWD 与 4MOTION 外廓一致。	READY
3875_3dr	3875	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3875_5dr	3875	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3876_3dr	3876	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3876_5dr	3876	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3877_3dr	3877	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3877_5dr	3877	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3878	3878	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH		READY
3879	3879	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
3880	3880	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
3881	3881	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3882	3882	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3885	3885	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
3886	3886	Wagon	A6 C4 Avant	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
3891	3891	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3892	3892	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3893	3893	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
3894	3894	Wagon	A6 C4 Avant	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449	Auto-Data.net Lancia Dedra Station Wagon 1.6	https://www.auto-data.net/en/lancia-dedra-station-wagon-835-1.6-90hp-5002
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1822	1462	Auto-Data.net Lancia Kappa 2.0 LE	https://www.auto-data.net/en/lancia-kappa-838-2.0-le-146hp-5077
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335	Auto-Data.net BMW M3 Coupe E36 3.0i	https://www.auto-data.net/en/bmw-m3-coupe-e36-3.0i-286hp-9879
EU-BMW-8-E31-COUPE-850CSI-01	4780	1855	1330	Auto-Data.net BMW 8 Series E31 850 CSi	https://www.auto-data.net/en/bmw-8-series-e31-850csi-5.6-380hp-9864
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340	Auto-Data.net BMW M3 Convertible E36 3.0i	https://www.auto-data.net/en/bmw-m3-convertible-e36-3.0i-286hp-9876
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392	Auto-Data.net BMW M5 Touring E34 3.8	https://www.auto-data.net/en/bmw-m5-touring-e34-3.8-340hp-manual-6-speed-9665
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	4425	1750	1305	Auto-Data.net Toyota Celica T20 2.0 i 16V	https://www.auto-data.net/en/toyota-celica-t20-2.0-i-16v-175hp-3129
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-GTFOUR-01	4420	1750	1305	Auto-Data.net Toyota Celica T20 GT-Four	https://www.auto-data.net/en/toyota-celica-t20-2.0-turbo-242hp-gt-four-3130
EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	4490	1690	1745	Auto-Data.net Toyota 4Runner II 3.0 TD	https://www.auto-data.net/en/toyota-4runner-ii-3.0-td-125hp-4x4-3123
EU-LEXUS-ES-II-XV10-SEDAN-01	4770	1778	1370	Auto-Data.net Lexus ES II XV10 300	https://www.auto-data.net/en/lexus-es-ii-xv10-300-188hp-5874
EU-TOYOTA-SUPRA-IV-A80-COUPE-3D-01	4520	1810	1275	Auto-Data.net Toyota Supra IV A80 3.0 Twin Turbo	https://www.auto-data.net/en/toyota-supra-iv-a80-3.0i-24v-t-turbo-330hp-3454
EU-TOYOTA-RAV4-I-XA10-SUV-3D-01	3705	1695	1655	Auto-Data.net Toyota RAV4 I XA10 3-door 2.0i	https://www.auto-data.net/en/toyota-rav4-i-xa10-3-door-2.0i-16v-129hp-4wd-3849
EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	4115	1695	1660	Auto-Data.net Toyota RAV4 I XA10 5-door 2.0i	https://www.auto-data.net/en/toyota-rav4-i-xa10-5-door-2.0i-16v-129hp-4wd-3850
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450	Auto-Data.net Opel Omega B	https://www.auto-data.net/en/opel-omega-b-generation-514
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455	Auto-Data.net Opel Omega B facelift 1999	https://www.auto-data.net/en/opel-omega-b-facelift-1999-generation-5160
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500	Auto-Data.net Opel Omega B Caravan	https://www.auto-data.net/en/opel-omega-b-caravan-generation-513
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540	Auto-Data.net Opel Omega B Caravan facelift 2.5i V6	https://www.auto-data.net/en/opel-omega-b-caravan-facelift-1999-2.5i-v6-170hp-26073
EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	4892	1904	1970	Auto-Data.net VW Multivan T5 2.0 TDI; Auto-Data.net VW Multivan T5 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-20539;https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-4motion-20540
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440	Auto-Data.net Audi A8 D2 4.2 V8 quattro	https://www.auto-data.net/en/audi-a8-d2-4d-4.2-v8-32v-300hp-quattro-tiptronic-4848
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Auto-Data.net Audi A6 C4	https://www.auto-data.net/en/audi-a6-4a-c4-generation-1119
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440	Auto-Data.net Audi A6 Avant C4	https://www.auto-data.net/en/audi-a6-avant-4a-c4-generation-1120
```

Lancia、BMW 的新增尺寸组分别核对了 Dedra/Kappa、M3 Coupe、M3 Convertible、850 CSi 和 M5 Touring 的独立外廓；850 CSi 的高度与已有普通 850 组不同，因此未覆盖历史组。([汽车数据网][2])

Toyota/Lexus 部分已核对 Celica T20 标准前驱与 GT-Four、4Runner II、Supra A80，以及 RAV4 XA10 三门和五门的不同长度与高度。([汽车数据网][3])

Omega B 的轿车和旅行版均按 1999 年改款前后建立独立尺寸组；Audi A6 C4 轿车与 Avant 高度不同，分别建组。([汽车数据网][4])

## 下一步优先处理

1. 闭合 Ford Escort V 的 RS2000、XR3i、普通三/五门、三厢、旅行版和敞篷分支。
2. 集中处理 Ford Transit 1994–2000 的轴距与车顶组合。
3. 补齐 Dacia Logan Pick-up、Mazda 6 GH、Passat B3/B4、Polo 6N。
4. 解决 Scorpio I 掀背高度分支后，完成 Mondeo、Golf III 等剩余缓存挂接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-4motion-20540 "https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-4motion-20540"
[2]: https://www.auto-data.net/en/lancia-dedra-station-wagon-835-1.6-90hp-5002 "Lancia Dedra Station Wagon (835) 1.6 (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/toyota-celica-t20-2.0-i-16v-175hp-3129 "Toyota Celica (T20) 2.0 i 16V (175 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/opel-omega-b-generation-514 "https://www.auto-data.net/en/opel-omega-b-generation-514"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 **36 个输入 Ktype、44 条 READY 映射**；Ford Escort、Fiesta、Mondeo、Scorpio、Golf III 等直接复用已有尺寸组。
* 首次创建 8 个尺寸组：Escort VI 三厢、Dacia Logan Pick-up、Mazda 6 GH 改款掀背/旅行版、Passat B4 三厢/普通旅行版/Syncro 旅行版、Polo III 6N。
* `3905`、`3908` 暂未闭合：输入只标注 Transit Bus，现有缓存包含 SWB/LWB 及不同车顶分支，尚不能确定完整派生边界。
* Escort VI 三厢、Dacia Logan Pick-up、Mazda 6 GH、Passat B4 和 Polo 6N 的新尺寸组均已确认不含后视镜车宽。([汽车数据网][1])

## 当前批次进度

* READY 输入 Ktype：**98 / 100**
* PENDING 输入 Ktype：**2 / 100**
* READY 映射：**118**
* PENDING 映射：**2**
* 已确认并被引用尺寸组：**64**
* 本轮首次创建尺寸组：**8**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3883_prefl	3883	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
3883_facelift	3883	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
3884	3884	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH		READY
3887	3887	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH		READY
3890_3dr_prefl	3890	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	MEDIUM	三门改款前分支。	READY
3890_5dr_prefl	3890	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	MEDIUM	五门改款前分支。	READY
3890_3dr_facelift	3890	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款后分支。	READY
3890_5dr_facelift	3890	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款后分支。	READY
3895	3895	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
3896	3896	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH		READY
3897_3dr	3897	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	HIGH	三门分支。	READY
3897_5dr	3897	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	HIGH	五门分支。	READY
3898	3898	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
3899	3899	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH		READY
3900_3dr	3900	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	三门标准外廓。	READY
3900_5dr	3900	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	五门与三门共用外廓尺寸。	READY
3902	3902	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
3903	3903	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
3905	3905	MPV	Transit VE6 facelift	VE6			LOW	SWB/LWB 与车顶高度分支尚未闭合。	PENDING: 轴距和车顶分支未闭合
3906	3906	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
3908	3908	MPV	Transit VE6 facelift	VE6			LOW	SWB/LWB 与车顶高度分支尚未闭合。	PENDING: 轴距和车顶分支未闭合
3909	3909	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3910	3910	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3911	3911	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3912	3912	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3913	3913	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3914	3914	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3915	3915	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3916	3916	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3917	3917	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3918	3918	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3919	3919	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3920	3920	Wagon	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
3921	3921	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-5D-01	HIGH		READY
3922	3922	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-4D-01	HIGH		READY
3923	3923	Wagon	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
3924_3dr	3924	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	三门分支。	READY
3924_5dr	3924	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	五门分支。	READY
3925	3925	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-WAGON-SYNCRO-01	HIGH	Syncro 独立车身高度。	READY
3926	3926	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3927	3927	Sedan	Passat B4	3A2	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH		READY
3928	3928	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-WAGON-01	HIGH		READY
3929	3929	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
3930	3930	Wagon	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH		READY
3931_3dr	3931	Hatchback	Polo III	6N1	3	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH	三门分支。	READY
3931_5dr	3931	Hatchback	Polo III	6N1	5	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH	五门与三门共用外廓尺寸。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397	Auto-Data.net Ford Escort VI GAL Sedan	https://www.auto-data.net/en/ford-escort-vi-gal-1.3-60hp-7422
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554	Auto-Data.net Dacia Logan I Pick-up	https://www.auto-data.net/en/dacia-logan-i-pick-up-1.6-mpi-84hp-57272
EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	4755	1795	1440	Auto-Data.net Mazda 6 II Hatchback GH facelift	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-2.2-cd-180hp-16786
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490	Auto-Data.net Mazda 6 II Combi GH facelift	https://www.auto-data.net/en/mazda-6-ii-combi-gh-facelift-2010-2.2-cd-180hp-16793
EU-VW-PASSAT-B4-WAGON-SYNCRO-01	4595	1720	1485	Auto-Data.net Volkswagen Passat Variant B4 2.9 VR6 Syncro	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.9-vr6-184hp-syncro-8993
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Auto-Data.net Volkswagen Passat B4 Sedan	https://www.auto-data.net/en/volkswagen-passat-b4-2.0-16v-150hp-8969
EU-VW-PASSAT-B4-WAGON-01	4595	1720	1445	Auto-Data.net Volkswagen Passat Variant B4	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.0-16v-150hp-8990
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Auto-Data.net Volkswagen Polo III 6N	https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.3-55hp-8472
```

新建尺寸组的三维与页面记录一致；Dacia 页面还分别列出了车身宽度和含后视镜宽度，因此落盘采用 1735 mm 的不含镜宽度。([汽车数据网][2])

## 下一步优先处理

1. 仅处理 `3905`、`3908` 两个 Transit Bus Ktype。
2. 根据其 Ktype 对应目录边界，在已有 VE6 缓存中确定 SWB/LWB 和 lowroof/midroof/highroof 分支。
3. 两个 Ktype 闭合后立即执行一次机械检查，并在下一轮输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-escort-vi-gal-1.3-60hp-7422 "Ford Escort VI (GAL) 1.3 (60 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/dacia-logan-i-pick-up-1.6-mpi-84hp-57272 "Dacia Logan I Pick-up 1.6 MPI (84 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* `3905`、`3908` 已按同一 Ktype 覆盖的实际车身边界，分别拆分为短轴低顶、短轴中顶、长轴中顶、长轴高顶四个分支，并直接复用既有 Transit VE6 facelift 尺寸组。([Brembo Parts][1])
* 已完成最终机械检查：表头固定、126 个 `id` 唯一、68 个 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合，无孤立尺寸组，三维及来源字段完整。
* 当前批次 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：**100 / 100 READY**
* READY 映射：**126**
* PENDING 映射：**0**
* 最终尺寸组：**68**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3827	3827	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3828	3828	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3829	3829	Hatchback	Delta II	836	5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
3830	3830	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3831	3831	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3832	3832	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
3833_prefl	3833	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	MEDIUM	生产区间跨越前期与改款外廓。	READY
3833_facelift	3833	Sedan	Dedra I	835	4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越前期与改款外廓。	READY
3834	3834	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3835	3835	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3836	3836	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3837	3837	Wagon	Dedra I	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
3838	3838	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3839	3839	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3840	3840	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3841	3841	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
3842	3842	Coupe	3 Series E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
3843	3843	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850CSI-01	HIGH	850 CSi 特殊外廓高度。	READY
3844	3844	SUV	Outlander II facelift	CW0	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH		READY
3845	3845	Convertible	3 Series E36	E36	2	EU-BMW-3-E36-M3-CONVERTIBLE-01	HIGH		READY
3846	3846	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-M5-WAGON-01	HIGH	M5 Touring 特殊车身高度。	READY
3847	3847	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	HIGH	三门 liftback 外廓。	READY
3848	3848	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	HIGH	三门 liftback 外廓。	READY
3849	3849	Coupe	Celica VI	T20	3	EU-TOYOTA-CELICA-VI-T20-COUPE-3D-GTFOUR-01	HIGH	GT-Four 独立外廓。	READY
3850	3850	Sedan	Carina E VI	T19	4	EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	HIGH		READY
3851	3851	Hatchback	Carina E VI	T19	5	EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	HIGH	五门 liftback 外廓。	READY
3852	3852	Coupe	MR2 II	SW20	2	EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	HIGH	T-bar/targa 双门外廓。	READY
3853	3853	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH		READY
3854	3854	SUV	4Runner II	KZN130	5	EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	HIGH		READY
3855	3855	Sedan	ES II	XV10	4	EU-LEXUS-ES-II-XV10-SEDAN-01	HIGH		READY
3856	3856	Coupe	Supra IV	A80	3	EU-TOYOTA-SUPRA-IV-A80-COUPE-3D-01	HIGH		READY
3857_3dr	3857	SUV	RAV4 I	XA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3857_5dr	3857	SUV	RAV4 I	XA10	5	EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3858	3858	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH		READY
3859	3859	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH		READY
3860_prefl	3860	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3860_facelift	3860	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3861_prefl	3861	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3861_facelift	3861	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3862_prefl	3862	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3862_facelift	3862	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3863	3863	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH		READY
3864	3864	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH		READY
3865_prefl	3865	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3865_facelift	3865	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3866_prefl	3866	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3866_facelift	3866	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3867_prefl	3867	Wagon	Omega B Caravan		5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3867_facelift	3867	Wagon	Omega B Caravan facelift		5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	MEDIUM	生产区间跨越 1999 年改款。	READY
3868	3868	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
3869_3dr	3869	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3869_5dr	3869	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3870	3870	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
3871	3871	Hatchback	Vectra A CC		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH		READY
3872	3872	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
3873	3873	MPV	Multivan T5 facelift		5	EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	MEDIUM	100 kW/136 PS 版本；FWD 与 4MOTION 外廓一致。	READY
3874	3874	MPV	Multivan T5 facelift		5	EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	MEDIUM	100 kW/136 PS 版本；FWD 与 4MOTION 外廓一致。	READY
3875_3dr	3875	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3875_5dr	3875	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3876_3dr	3876	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3876_5dr	3876	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3877_3dr	3877	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3877_5dr	3877	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	HIGH	同一 Ktype 覆盖三门与五门外廓。	READY
3878	3878	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH		READY
3879	3879	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
3880	3880	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
3881	3881	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3882	3882	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3883_prefl	3883	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
3883_facelift	3883	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
3884	3884	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH		READY
3885	3885	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
3886	3886	Wagon	A6 C4 Avant	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
3887	3887	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH		READY
3890_3dr_prefl	3890	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	MEDIUM	三门改款前分支。	READY
3890_5dr_prefl	3890	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	MEDIUM	五门改款前分支。	READY
3890_3dr_facelift	3890	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款后分支。	READY
3890_5dr_facelift	3890	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款后分支。	READY
3891	3891	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3892	3892	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH		READY
3893	3893	Sedan	A6 C4	4A	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
3894	3894	Wagon	A6 C4 Avant	4A	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
3895	3895	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
3896	3896	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH		READY
3897_3dr	3897	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	HIGH	三门分支。	READY
3897_5dr	3897	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	HIGH	五门分支。	READY
3898	3898	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
3899	3899	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH		READY
3900_3dr	3900	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	三门标准外廓。	READY
3900_5dr	3900	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	五门与三门共用外廓尺寸。	READY
3902	3902	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
3903	3903	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
3905_swb_lowroof	3905	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理分支。	READY
3905_swb_midroof	3905	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理分支。	READY
3905_lwb_midroof	3905	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理分支。	READY
3905_lwb_highroof	3905	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理分支。	READY
3906	3906	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
3908_swb_lowroof	3908	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理分支。	READY
3908_swb_midroof	3908	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理分支。	READY
3908_lwb_midroof	3908	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理分支。	READY
3908_lwb_highroof	3908	MPV	Transit VE6 facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理分支。	READY
3909	3909	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3910	3910	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3911	3911	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3912	3912	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3913	3913	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3914	3914	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3915	3915	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3916	3916	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
3917	3917	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
3918	3918	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3919	3919	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
3920	3920	Wagon	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
3921	3921	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-5D-01	HIGH		READY
3922	3922	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-4D-01	HIGH		READY
3923	3923	Wagon	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
3924_3dr	3924	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	三门分支。	READY
3924_5dr	3924	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	五门分支。	READY
3925	3925	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-WAGON-SYNCRO-01	HIGH	Syncro 独立车身高度。	READY
3926	3926	Hatchback	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	HIGH		READY
3927	3927	Sedan	Passat B4	3A2	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH		READY
3928	3928	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-WAGON-01	HIGH		READY
3929	3929	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
3930	3930	Wagon	6 II GH facelift	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH		READY
3931_3dr	3931	Hatchback	Polo III	6N1	3	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH	三门分支。	READY
3931_5dr	3931	Hatchback	Polo III	6N1	5	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH	五门与三门共用外廓尺寸。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3701-3800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-DELTA-II-HATCHBACK-01	4011	1703	1430	Automobile-Catalog 1996 Lancia Delta 1.6 i.e.	https://www.automobile-catalog.com/car/1996/1382660/lancia_delta_1_6_i_e_.html
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430	Automobile-Catalog 1999 Lancia Dedra 1.6	https://www.automobile-catalog.com/car/1999/1382420/lancia_dedra_1_6.html
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430	Automobile-Catalog 1990 Lancia Dedra 1.6 i.e.	https://www.automobile-catalog.com/car/1990/1381610/lancia_dedra_1_6_i_e_.html
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449	Auto-Data.net Lancia Dedra Station Wagon 1.6	https://www.auto-data.net/en/lancia-dedra-station-wagon-835-1.6-90hp-5002
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1822	1462	Auto-Data.net Lancia Kappa 2.0 LE	https://www.auto-data.net/en/lancia-kappa-838-2.0-le-146hp-5077
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335	Auto-Data.net BMW M3 Coupe E36 3.0i	https://www.auto-data.net/en/bmw-m3-coupe-e36-3.0i-286hp-9879
EU-BMW-8-E31-COUPE-850CSI-01	4780	1855	1330	Auto-Data.net BMW 8 Series E31 850 CSi	https://www.auto-data.net/en/bmw-8-series-e31-850csi-5.6-380hp-9864
EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	4665	1800	1680	Auto-Data.net Mitsubishi Outlander II facelift	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2010-generation-2353
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340	Auto-Data.net BMW M3 Convertible E36 3.0i	https://www.auto-data.net/en/bmw-m3-convertible-e36-3.0i-286hp-9876
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392	Auto-Data.net BMW M5 Touring E34 3.8	https://www.auto-data.net/en/bmw-m5-touring-e34-3.8-340hp-manual-6-speed-9665
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	4425	1750	1305	Auto-Data.net Toyota Celica T20 2.0 i 16V	https://www.auto-data.net/en/toyota-celica-t20-2.0-i-16v-175hp-3129
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-GTFOUR-01	4420	1750	1305	Auto-Data.net Toyota Celica T20 GT-Four	https://www.auto-data.net/en/toyota-celica-t20-2.0-turbo-242hp-gt-four-3130
EU-TOYOTA-CARINA-E-VI-T19-SEDAN-4D-01	4530	1695	1410	Automobile-Catalog 1995 Toyota Carina E 4-door	https://www.automobile-catalog.com/car/1995/3602480/toyota_carina_e_4door_2_0_diesel.html
EU-TOYOTA-CARINA-E-VI-T19-LIFTBACK-5D-01	4530	1695	1410	Toyota Carina E T19 vehicle specifications	https://www.automoli.com/gb/vehicles/toyota/carina/carina-e-t19-1036/
EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	4140	1695	1240	Auto-Data.net Toyota MR2 W2 SW20	https://www.auto-data.net/en/toyota-mr-2-w2-2.0-16v-sw20-156hp-3897
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980	Toyota Hiace H100 specifications	https://autoprostor.rs/catalog/toyota/hiace/10849/61950/
EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	4490	1690	1745	Auto-Data.net Toyota 4Runner II 3.0 TD	https://www.auto-data.net/en/toyota-4runner-ii-3.0-td-125hp-4x4-3123
EU-LEXUS-ES-II-XV10-SEDAN-01	4770	1778	1370	Auto-Data.net Lexus ES II XV10 300	https://www.auto-data.net/en/lexus-es-ii-xv10-300-188hp-5874
EU-TOYOTA-SUPRA-IV-A80-COUPE-3D-01	4520	1810	1275	Auto-Data.net Toyota Supra IV A80 Twin Turbo	https://www.auto-data.net/en/toyota-supra-iv-a80-3.0i-24v-t-turbo-330hp-3454
EU-TOYOTA-RAV4-I-XA10-SUV-3D-01	3705	1695	1655	Auto-Data.net Toyota RAV4 I XA10 3-door	https://www.auto-data.net/en/toyota-rav4-i-xa10-3-door-2.0i-16v-129hp-4wd-3849
EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	4115	1695	1660	Auto-Data.net Toyota RAV4 I XA10 5-door	https://www.auto-data.net/en/toyota-rav4-i-xa10-5-door-2.0i-16v-129hp-4wd-3850
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450	Auto-Data.net Opel Omega B	https://www.auto-data.net/en/opel-omega-b-generation-514
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455	Auto-Data.net Opel Omega B facelift 1999	https://www.auto-data.net/en/opel-omega-b-facelift-1999-generation-5160
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500	Auto-Data.net Opel Omega B Caravan	https://www.auto-data.net/en/opel-omega-b-caravan-generation-513
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540	Auto-Data.net Opel Omega B Caravan facelift	https://www.auto-data.net/en/opel-omega-b-caravan-facelift-1999-2.5i-v6-170hp-26073
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410	Auto-Data.net Opel Astra F Classic Sedan	https://www.auto-data.net/en/opel-astra-f-classic-generation-556
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410	Auto-Data.net Opel Astra F	https://www.auto-data.net/en/opel-astra-f-1.8-16v-125hp-16698
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410	Auto-Data.net Opel Astra F	https://www.auto-data.net/en/opel-astra-f-1.8-16v-125hp-16698
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Auto-Data.net Opel Vectra A facelift	https://www.auto-data.net/en/opel-vectra-a-facelift-1992-2.0i-16v-136hp-2314
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400	Auto-Data.net Opel Vectra A CC facelift	https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-2.0i-16v-136hp-automatic-26086
EU-VW-MULTIVAN-T5-FACELIFT-MPV-SWB-01	4892	1904	1970	Auto-Data.net VW Multivan T5 2.0 TDI; Auto-Data.net VW Multivan T5 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-20539;https://www.auto-data.net/en/volkswagen-multivan-t5-facelift-2009-2.0-tdi-140hp-4motion-20540
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420	Auto-Data.net Opel Corsa B	https://www.auto-data.net/en/opel-corsa-b-1.4i-60hp-2114
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420	Auto-Data.net Opel Corsa B	https://www.auto-data.net/en/opel-corsa-b-1.4i-60hp-2114
EU-OPEL-ASTRA-F-WAGON-5D-01	4278	1688	1475	Auto-Data.net Opel Astra F Caravan	https://www.auto-data.net/en/opel-astra-f-caravan-1.7-d-57hp-2485
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400	Auto-Data.net Opel Astra F Cabrio facelift	https://www.auto-data.net/en/opel-astra-f-cabrio-facelift-1994-1.8i-ecotec-16v-116hp-2475
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440	Auto-Data.net Audi A8 D2 4.2 V8 quattro	https://www.auto-data.net/en/audi-a8-d2-4d-4.2-v8-32v-300hp-quattro-tiptronic-4848
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	4040	1692	1389	Auto-Data.net Ford Escort V RS 2000	https://www.auto-data.net/en/ford-escort-v-gal-rs-2000-150hp-7468
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	4108	1696	1379	Auto-Data.net Ford Escort VI RS 2000 4x4	https://www.auto-data.net/en/ford-escort-vi-hatch-gal-2.0-i-16v-rs-2000-4x4-150hp-7458
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	4108	1696	1370	Auto-Data.net Ford Escort VI XR3i 4x4	https://www.auto-data.net/en/ford-escort-vi-gal-1.8-xr3i-16v-4x4-105hp-7430
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Auto-Data.net Audi A6 C4	https://www.auto-data.net/en/audi-a6-4a-c4-generation-1119
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440	Auto-Data.net Audi A6 Avant C4	https://www.auto-data.net/en/audi-a6-avant-4a-c4-generation-1120
EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	4036	1692	1395	Automobile-Catalog 1991 Ford Escort 1.3 L	https://www.automobile-catalog.com/car/1991/944735/ford_escort_1_3_l.html
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	4104	1696	1397	Auto-Data.net Ford Escort VI Hatch	https://www.auto-data.net/en/ford-escort-vi-hatch-gal-1.4-73hp-7449
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	4104	1696	1397	Auto-Data.net Ford Escort VI Hatch	https://www.auto-data.net/en/ford-escort-vi-hatch-gal-1.4-73hp-7449
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397	Auto-Data.net Ford Escort VI GAL Sedan	https://www.auto-data.net/en/ford-escort-vi-gal-1.3-60hp-7422
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410	Auto-Data.net Ford Escort VI Turnier	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-1.4-75hp-7437
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389	Automobile-Catalog 1991 Ford Fiesta S 1.6	https://www.automobile-catalog.com/car/1991/61475/ford_fiesta_s_1_6.html
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379	Auto-Data.net Ford Escort VI Cabrio XR3i	https://www.auto-data.net/en/ford-escort-vi-cabrio-all-1.8-i-16v-xr3i-130hp-7447
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Transit Center Ford Transit MK4 specifications	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Transit Center Ford Transit MK4 specifications	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Transit Center Ford Transit MK4 specifications	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Transit Center Ford Transit MK4 specifications	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554	Auto-Data.net Dacia Logan I Pick-up	https://www.auto-data.net/en/dacia-logan-i-pick-up-1.6-mpi-84hp-57272
EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	4755	1795	1440	Auto-Data.net Mazda 6 II Hatchback GH facelift	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-2.2-cd-180hp-16786
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510	Auto-Data.net Ford Mondeo I Wagon	https://www.auto-data.net/en/ford-mondeo-i-wagon-generation-1705
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424	Automobile-Catalog 1994 Ford Mondeo 5-door 1.8i	https://www.automobile-catalog.com/car/1994/947465/ford_mondeo_5-dr_1_8i_16v_clx_lx.html
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424	Automobile-Catalog Ford Mondeo Mk I Sedan catalogue	https://www.automobile-catalog.com/make/ford_europe/mondeo_1gen/mondeo_1gen_sedan/1994.html
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490	Auto-Data.net Ford Scorpio I Turnier GGE	https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-generation-1790
EU-FORD-SCORPIO-I-HATCHBACK-5D-01	4669	1760	1490	Auto-Data.net Ford Scorpio I Hatch GGE	https://www.auto-data.net/en/ford-scorpio-i-hatch-gge-generation-1789
EU-FORD-SCORPIO-I-SEDAN-4D-01	4744	1766	1450	Auto-Data.net Ford Scorpio I Sedan	https://www.auto-data.net/en/ford-scorpio-i-gae-gge-generation-1788
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Auto-Data.net Volkswagen Golf III	https://www.auto-data.net/en/volkswagen-golf-iii-2.0-115hp-8727
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Auto-Data.net Volkswagen Golf III	https://www.auto-data.net/en/volkswagen-golf-iii-2.0-115hp-8727
EU-VW-PASSAT-B4-WAGON-SYNCRO-01	4595	1720	1485	Auto-Data.net Volkswagen Passat Variant B4 VR6 Syncro	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.9-vr6-184hp-syncro-8993
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Auto-Data.net Volkswagen Passat B4 Sedan	https://www.auto-data.net/en/volkswagen-passat-b4-2.0-16v-150hp-8969
EU-VW-PASSAT-B4-WAGON-01	4595	1720	1445	Auto-Data.net Volkswagen Passat Variant B4	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.0-16v-150hp-8990
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data.net Volkswagen Golf III Variant 1.9 TDI	https://www.auto-data.net/en/volkswagen-golf-iii-variant-1.9-tdi-90hp-automatic-28702
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490	Auto-Data.net Mazda 6 II Combi GH facelift	https://www.auto-data.net/en/mazda-6-ii-combi-gh-facelift-2010-2.2-cd-180hp-16793
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Auto-Data.net Volkswagen Polo III 6N	https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.3-55hp-8472
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3701-3800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.bremboparts.com/europe/en/catalogue/ford-transit-bus-e-2-5-di-ebl-ecl-eds-edl/000003905-1 "https://www.bremboparts.com/europe/en/catalogue/ford-transit-bus-e-2-5-di-ebl-ecl-eds-edl/000003905-1"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3701-3800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3701-3800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5078 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1499 行）

