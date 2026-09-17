# 任务：all 第 1401-1500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0015__3b5c219b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1401-1500 行

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
all 第 1401-1500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-BMW-6-E24-COUPE-FACELIFT-01	4815	1725	1365
EU-CATERHAM-SEVEN-485-CONVERTIBLE-S3-01	3100	1575	1115
EU-CATERHAM-SEVEN-485-CONVERTIBLE-SV-01	3300	1685	1140
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4065	1735	1476
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455
EU-IVECO-DAILY-VI-4X4-CHASSIS-LWB-01	6818	2056	2501
EU-IVECO-DAILY-VI-4X4-CHASSIS-MWB-01	5853	2056	2506
EU-IVECO-DAILY-VI-4X4-CHASSIS-SWB-01	5348	2056	2508
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644
EU-LADA-SAMARA-2108-HATCHBACK-3D-01	4006	1650	1402
EU-LADA-SAMARA-2109-HATCHBACK-5D-01	4006	1650	1402
EU-LADA-SAMARA-2113-HATCHBACK-3D-01	4122	1650	1402
EU-LADA-SAMARA-2114-HATCHBACK-5D-01	4122	1650	1402
EU-LAMBORGHINI-AVENTADOR-LP750-SV-ROADSTER-01	4835	2030	1136
EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	4656	1890	1639
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1500
EU-RENAULT-GRAND-SCENIC-IV-MPV-01	4634	1866	1655
EU-RENAULT-SCENIC-IV-MPV-01	4406	1866	1653
EU-SMART-FORFOUR-II-HATCHBACK-01	3525	1665	1543
EU-SMART-FORTWO-A450-CONVERTIBLE-01	2500	1537	1549
EU-SMART-FORTWO-III-CONVERTIBLE-01	2740	1663	1543
EU-SMART-FORTWO-III-COUPE-01	2740	1663	1543
EU-SUZUKI-VITARA-IV-SUV-01	4175	1775	1610
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Austin-healey	100	2.6	Cabriolet	Heckantrieb	Benzin	87	118	Jan 1957	Dec 1959	2024-03-01	127250
Austin-healey	Sprite mk.iv	1.3	Cabriolet	Heckantrieb	Benzin	49	67	Mar 1966	Oct 1971	2024-03-01	127251
Autobianchi	Primula	1.2	Coupe	Frontantrieb	Benzin	48	65	Jun 1968	Oct 1970	2024-03-01	127252
Autobianchi	Y10	1.1 4WD	Schrägheck	Allrad	Benzin	37	50	Feb 1990	Apr 1991	2024-03-01	127253
Autobianchi	Y10	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Feb 1990	Sep 1992	2024-03-01	127254
Lada	Toscana	1.7	Stufenheck	Heckantrieb	Benzin	62	84	Mar 1991	Oct 2001	2024-03-01	127260
Bitter	Type 3	3.0 I	Cabriolet	Heckantrieb	Benzin	130	177	Mar 1987	Dec 1990	2024-03-01	127261
Caterham	Seven	1.6	Cabriolet	Heckantrieb	Benzin	70	95	Jun 1986	Dec 1991	2024-03-01	127267
Ferrari	208/308	308 Gtsi	Targa	Heckantrieb	Benzin	158	215	Oct 1980	Dec 1982	2024-03-01	127270
Ferrari	208/308	308 Gtbi	Coupe	Heckantrieb	Benzin	158	215	Oct 1980	Dec 1982	2024-03-01	127271
Ferrari	Mondial	3	Cabriolet	Heckantrieb	Benzin	172	234	May 1986	Sep 1987	2024-03-01	127274
Ferrari	Mondial	3	Coupe	Heckantrieb	Benzin	172	234	May 1986	Sep 1987	2024-03-01	127275
Lada	Samara	1.5	Schrägheck	Frontantrieb	Benzin	53	72	Aug 2003	Dec 2013	2024-03-01	127296
Lada	Toscana	1.6	Stufenheck	Heckantrieb	Benzin	57	78	Oct 1985	May 1994	2024-03-01	127297
Renault	Scénic iv	1.5 DCI 110 Hybrid Assist	Großraumlimousine	Frontantrieb	Diesel/Elektro	81	110	Apr 2017	Jul 2022	2024-05-01	127326
Renault	Grand scénic iv	1.5 DCI 110 Hybrid Assist	Großraumlimousine	Frontantrieb	Diesel/Elektro	81	110	Apr 2017	Mar 2023	2024-05-01	127327
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	210	286	May 2017	Jul 2020	2024-03-01	127328
Mercedes-benz	S-Klasse	S 400 D 4-matic	Stufenheck	Allrad	Diesel	250	340	May 2017	Jul 2020	2024-03-01	127329
Mercedes-benz	S-Klasse	S 560 4-matic	Stufenheck	Allrad	Benzin	345	469	May 2017	Jul 2020	2024-03-01	127330
Mercedes-benz	S-Klasse	AMG S 63 4-matic+	Stufenheck	Allrad	Benzin	450	612	May 2017	Jul 2020	2024-03-01	127331
Mercedes-benz	S-Klasse	S 560 Maybach 4-matic	Stufenheck	Allrad	Benzin	345	469	Jul 2017	Jul 2020	2024-03-01	127332
Mercedes-benz	E-Klasse	AMG E 63 4-matic+	Kombi	Allrad	Benzin	420	571	May 2017	Oct 2023	2024-03-01	127339
Mercedes-benz	E-Klasse	AMG E 63 S 4-matic+	Kombi	Allrad	Benzin	450	612	May 2017	Oct 2023	2024-03-01	127340
Alpina	B3	S Biturbo	Stufenheck	Heckantrieb	Benzin	324	440	Mar 2017	Aug 2018	2024-03-01	127341
Alpina	B3	S Biturbo Allrad	Stufenheck	Allrad	Benzin	324	440	Mar 2017	Aug 2018	2024-03-01	127342
Alpina	B3	S Biturbo	Kombi	Heckantrieb	Benzin	324	440	Mar 2017	Jun 2019	2024-03-01	127343
Alpina	B3	S Biturbo Allrad	Kombi	Allrad	Benzin	324	440	Mar 2017	Jun 2019	2024-03-01	127344
Alpina	B4	S Biturbo	Coupe	Heckantrieb	Benzin	324	440	Mar 2017	Aug 2018	2024-03-01	127345
Alpina	B4	S Biturbo Allrad	Coupe	Allrad	Benzin	324	440	Mar 2017	Aug 2018	2024-03-01	127346
Alpina	B4	S Biturbo	Cabriolet	Heckantrieb	Benzin	324	440	Mar 2017	Aug 2018	2024-03-01	127347
Smart	Fortwo	Electric Drive / EQ	Coupe	Heckantrieb	Elektro	41	56	May 2017	-	2024-03-01	127348
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	60	82	May 2017	-	2024-03-01	127350
Smart	Forfour	Electric Drive / EQ	Schrägheck	Heckantrieb	Elektro	41	56	May 2017	-	2024-03-01	127352
Smart	Forfour	Electric Drive	Schrägheck	Heckantrieb	Elektro	60	82	May 2017	-	2024-03-01	127353
Smart	Fortwo	Electric Drive / EQ	Cabriolet	Heckantrieb	Elektro	41	56	May 2017	-	2024-03-01	127355
Mercedes-benz	E-Klasse	E 220 D	Coupe	Heckantrieb	Diesel	120	163	Dec 2016	-	2024-03-01	127356
Hyundai	I30	1.0 T-gdi	Kombi	Frontantrieb	Benzin	88	120	Mar 2017	-	2024-03-01	127357
Hyundai	I30	1.4 T-gdi	Kombi	Frontantrieb	Benzin	103	140	Mar 2017	Dec 2020	2024-07-01	127358
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	81	110	Mar 2017	-	2024-03-01	127359
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	100	136	Mar 2017	-	2024-03-01	127360
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	110	150	Dec 2016	-	2024-03-01	127368
Alfa Romeo	Stelvio	2.2 D Q4	SUV	Allrad	Diesel	132	180	Dec 2016	-	2024-03-01	127369
Suzuki	Grand vitara ii	2.7 Allrad	Geländewagen geschlossen	Allrad	Benzin	136	185	Jan 2007	Dec 2008	2024-03-01	127378
Land Rover	Discovery sport	2.0 4X4	SUV	Allrad	Benzin	213	290	Aug 2017	-	2024-03-01	127384
Land Rover	Range rover evoque	2.0 D 4X4	SUV	Allrad	Diesel	177	241	Aug 2017	Dec 2019	2024-03-01	127386
Land Rover	Discovery sport	2.0 D 4X4	SUV	Allrad	Diesel	177	241	Aug 2017	-	2024-03-01	127390
Citroën	Xsara	1.4	Kasten/Kombi	Frontantrieb	Benzin	55	75	Sep 2000	Mar 2005	2024-03-01	127398
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	64	87	Aug 2014	-	2024-03-01	127402
Citroën	Xsara	2.0 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Sep 2000	Mar 2005	2024-03-01	127408
Suzuki	Vitara	1.6 I 16V	Geländewagen geschlossen	Heckantrieb	Benzin	71	97	Jan 1990	Dec 1998	2024-03-01	127412
JAC	Iev6e	EV	Schrägheck	Frontantrieb	Elektro	45	61	May 2017	-	2024-03-01	127454
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	125	170	Mar 2017	-	2024-03-01	127507
Opel	Insignia b sports tourer	2.0 Cdti 4X4	Kombi	Allrad	Diesel	125	170	Mar 2017	-	2024-03-01	127508
Fiat	500l	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	59	80	Apr 2017	-	2024-03-01	127510
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	103	140	Jun 2017	-	2024-03-01	127518
Jeep	Compass	1.4 Multiair	SUV	Frontantrieb	Benzin	103	140	Mar 2017	-	2024-03-01	127519
Jeep	Compass	1.4 Multiair 4X4	SUV	Allrad	Benzin	125	170	Mar 2017	-	2024-03-01	127520
Jeep	Compass	1.6 CRD	SUV	Frontantrieb	Diesel	88	120	Mar 2017	-	2024-03-01	127521
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	103	140	Mar 2017	-	2024-03-01	127522
Jaguar	Xf sportbrake	2.0 D	Kombi	Heckantrieb	Diesel	120	163	Jul 2017	-	2024-03-01	127526
Jaguar	Xf sportbrake	2.0 D	Kombi	Heckantrieb	Diesel	132	180	Jul 2017	-	2024-03-01	127527
Jaguar	Xf sportbrake	2.0 D AWD	Kombi	Allrad	Diesel	132	180	Jul 2017	-	2024-03-01	127528
Jaguar	Xf sportbrake	2.0 D AWD	Kombi	Allrad	Diesel	177	241	Jul 2017	-	2024-03-01	127529
Jaguar	Xf sportbrake	3.0 D	Kombi	Heckantrieb	Diesel	221	300	Jul 2017	-	2024-03-01	127530
Jaguar	Xf sportbrake	2	Kombi	Heckantrieb	Benzin	184	250	Jul 2017	-	2024-03-01	127534
Iveco	Daily vi	35s60e	Kasten	Heckantrieb	Elektro	60	82	Oct 2015	-	2024-03-01	127609
Iveco	Daily vi	50c80e	Kasten	Heckantrieb	Elektro	80	109	Oct 2015	-	2025-02-03	127611
Iveco	Daily vi	35s60e, 35c60e	Pritsche/Fahrgestell	Heckantrieb	Elektro	60	82	Oct 2015	-	2024-03-01	127615
Iveco	Daily vi	45c80e, 50c80e	Pritsche/Fahrgestell	Heckantrieb	Elektro	80	109	Oct 2015	-	2024-03-01	127618
Mercedes-benz	E-Klasse	E 220 D	Cabriolet	Heckantrieb	Diesel	143	194	Jun 2017	-	2024-03-01	127634
Mercedes-benz	E-Klasse	E 200	Cabriolet	Heckantrieb	Benzin	135	184	Jun 2017	-	2024-03-01	127635
Mercedes-benz	E-Klasse	E 300	Cabriolet	Heckantrieb	Benzin	180	245	Jun 2017	-	2024-03-01	127636
Mercedes-benz	E-Klasse	E 400 4-matic	Cabriolet	Allrad	Benzin	245	333	Jun 2017	-	2024-03-01	127637
Iveco	Daily vi	40c15, 50c15, 60c15	Bus	Heckantrieb	Diesel	110	150	Apr 2016	-	2024-03-01	127646
Iveco	Daily vi	40c18, 50c18, 60c18	Bus	Heckantrieb	Diesel	132	180	Apr 2016	-	2024-03-01	127648
Peugeot	404	1.6	Kombi	Heckantrieb	Benzin	54	73	Apr 1962	May 1971	2025-02-03	127656
Lamborghini	Aventador	6.5 LP 740-4 AWD	Coupe	Allrad	Benzin	544	740	May 2017	-	2024-03-01	127663
Lamborghini	Huracán	5.2 Performante	Coupe	Allrad	Benzin	470	640	Mar 2017	-	2024-03-01	127664
Mercedes-benz	E-Klasse	E 220 D	Cabriolet	Heckantrieb	Diesel	120	163	Jun 2017	-	2024-03-01	127675
Mercedes-benz	E-Klasse	E 200 4-matic	Coupe	Allrad	Benzin	135	184	Jun 2017	-	2024-03-01	127680
Mercedes-benz	E-Klasse	E 350 D 4-matic	Kombi	Allrad	Diesel	190	258	Jun 2017	May 2018	2024-03-01	127681
Mercedes-benz	E-Klasse	E 350 D 4-matic	Kombi	Allrad	Diesel	190	258	Jun 2017	May 2018	2024-03-01	127682
Mercedes-benz	Glc	AMG 63 4-matic+	SUV	Allrad	Benzin	350	476	Jun 2017	Jun 2022	2024-03-01	127683
Mercedes-benz	Glc	AMG 63 4-matic+	SUV	Allrad	Benzin	350	476	Jun 2017	Mar 2023	2024-03-01	127685
Mercedes-benz	Glc	AMG 63 S 4-matic+	SUV	Allrad	Benzin	375	510	Jun 2017	Jun 2022	2024-03-01	127686
Mercedes-benz	Glc	AMG 63 S 4-matic+	SUV	Allrad	Benzin	375	510	Jun 2017	Mar 2023	2024-03-01	127687
Opel	Grandland	1.2	SUV	Frontantrieb	Benzin	96	131	Jun 2017	-	2025-02-03	127689
Opel	Grandland	1.6 Turbo D	SUV	Frontantrieb	Diesel	88	120	Jun 2017	Jul 2021	2025-02-03	127690
Mercedes-benz	Gle	AMG 43 4-matic	SUV	Allrad	Benzin	287	390	Jun 2017	Oct 2019	2024-03-01	127693
Chrysler	300c	5.7	Stufenheck	Heckantrieb	Benzin	265	360	May 2009	Dec 2010	2024-03-01	127701
Mercedes-benz	Gle	AMG 43 4-matic	SUV	Allrad	Benzin	287	390	Jun 2017	Oct 2018	2024-03-01	127721
Mercedes-benz	S-Klasse	S 450 4-matic	Stufenheck	Allrad	Benzin	270	367	Feb 2017	Jul 2020	2024-03-01	127736
Mercedes-benz	S-Klasse	S 450	Stufenheck	Heckantrieb	Benzin	270	367	Feb 2017	Jul 2020	2024-03-01	127739
Ford USA	Explorer	4.0 4WD	SUV	Allrad	Benzin	157	214	Sep 1998	Dec 2001	2024-03-01	127741
Toyota	Proace	2.0 D4D	Pritsche/Fahrgestell	Frontantrieb	Diesel	110	150	Feb 2016	Dec 2022	2026-01-01	127812
Honda	Civic x	2.0 Type-r	Schrägheck	Frontantrieb	Benzin	235	320	Jun 2017	Dec 2022	2024-03-01	127817
BMW	6	630 I	Schrägheck	Heckantrieb	Benzin	190	258	Jul 2017	Jun 2020	2024-03-01	127825
BMW	6	640 I	Schrägheck	Heckantrieb	Benzin	250	340	Jun 2017	Jun 2020	2024-03-01	127827
BMW	6	640 I Xdrive	Schrägheck	Allrad	Benzin	250	340	Jun 2017	Jun 2020	2024-03-01	127828
BMW	6	630 D	Schrägheck	Heckantrieb	Diesel	195	265	Jun 2017	Jun 2020	2024-03-01	127829


--- Round 1 / 首次发送 ---
## 更新点

* 按缓存优先模式恢复 **17 个输入 Ktype**，生成 **19 条 READY 映射**。
* `127296`（Lada Samara）拆分为 3 门/5 门两个已确认外廓。
* `127518`（Ford Fiesta VII）拆分为 3 门/5 门两个已确认外廓。
* 本轮共复用跨批次已有的 **13 个 DIMENSION_GROUP**，未重复抓取三维或来源。
* 其余车型进入按物理车身聚类的待处理队列。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：17
* PENDING 输入 Ktype：83
* READY 映射行：19
* 本轮复用尺寸组：13
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127296_3dr	127296	Hatchback	Samara 2	2113	3	EU-LADA-SAMARA-2113-HATCHBACK-3D-01	HIGH	拆分为2113三门物理外廓。	READY
127296_5dr	127296	Hatchback	Samara 2	2114	5	EU-LADA-SAMARA-2114-HATCHBACK-5D-01	HIGH	拆分为2114五门物理外廓。	READY
127326	127326	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
127327	127327	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
127348	127348	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH		READY
127350	127350	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH		READY
127352	127352	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH		READY
127353	127353	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH		READY
127355	127355	Convertible	Fortwo III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-01	HIGH		READY
127368	127368	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127369	127369	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127507	127507	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH		READY
127508	127508	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH		READY
127518_3dr	127518	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	HIGH	拆分为三门物理外廓。	READY
127518_5dr	127518	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	HIGH	拆分为五门物理外廓。	READY
127519	127519	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127520	127520	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127521	127521	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127522	127522	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无。本轮引用的 13 个尺寸组均为跨批次已有尺寸组，未重复输出。

## 下一步优先处理

1. 按共同外廓批量闭合 Mercedes-Benz S-Class、E-Class、GLC 和 GLE，重点区分标准轴距、长轴距、Maybach、SUV 与 Coupe。
2. 集中处理 Alpina B3/B4、Hyundai i30 Wagon、Jaguar XF Sportbrake 等可覆盖多个 Ktype 的尺寸组。
3. 单独拆分 Iveco Daily VI 的厢式车、底盘和 Bus 长度/高度分支。
4. 再处理历史车型及潜在多外廓车型：Austin-Healey、Caterham、Suzuki Vitara、Ford Explorer、Citroën Xsara。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 **22 个 Ktype、22 条 READY 映射**。
* 首次创建并确认 **9 个 DIMENSION_GROUP**。
* 批量完成 Hyundai i30 Wagon、Land Rover Discovery Sport、Range Rover Evoque、Jaguar XF Sportbrake、Lamborghini、Opel Grandland X、Honda Civic Type R 和 BMW 6 Series Gran Turismo。
* 上轮已确认的映射和尺寸组继续缓存复用，未重复输出。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：39
* PENDING 输入 Ktype：61
* READY 映射行：41
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127357	127357	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127358	127358	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127359	127359	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127360	127360	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127384	127384	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	HIGH		READY
127386	127386	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	HIGH		READY
127390	127390	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	HIGH		READY
127526	127526	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127527	127527	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127528	127528	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127529	127529	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127530	127530	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127534	127534	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127663	127663	Coupe	Aventador S		2	EU-LAMBORGHINI-AVENTADOR-S-COUPE-01	HIGH		READY
127664	127664	Coupe	Huracán Performante		2	EU-LAMBORGHINI-HURACAN-PERFORMANTE-COUPE-01	HIGH		READY
127689	127689	SUV	Grandland X I		5	EU-OPEL-GRANDLAND-X-I-SUV-01	HIGH		READY
127690	127690	SUV	Grandland X I		5	EU-OPEL-GRANDLAND-X-I-SUV-01	HIGH		READY
127817	127817	Hatchback	Civic X	FK8	5	EU-HONDA-CIVIC-X-FK8-TYPE-R-HATCHBACK-01	HIGH	Type R宽体外廓独立于普通Civic X Hatchback。	READY
127825	127825	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127827	127827	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127828	127828	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127829	127829	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Hyundai Ireland All-New i30 Tourer official brochure	https://www.hyundai.ie/assets/car/all-new-i30-tourer/files/hyundai-i30-tourer-20pp-brochure-final-min.pdf
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	4599	2000	1724	Land Rover Discovery Sport 17MY official brochure; Automobile-Catalog 2018 Discovery Sport Si4 290 AWD	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/discovery-sport/LRGL-DISS00-RTR0311_L550_17MY_MB_EURO_V17_FINAL_tcm295-799848.pdf;https://www.automobile-catalog.com/car/2018/2564795/land-rover_discovery_sport_si4_290_awd.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	4370	1900	1635	Automobile-Catalog 2017 Range Rover Evoque SD4 240 AWD	https://www.automobile-catalog.com/car/2017/2564810/range_rover_evoque_5-door_sd4_240_awd.html
EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	4955	1880	1496	Jaguar Media Newsroom New XF Sportbrake; Automobile-Catalog 2017 Jaguar XF Sportbrake 20d	https://archive.jaguar.com/news/2017/06/new-jaguar-xf-sportbrake;https://www.automobile-catalog.com/car/2017/2559845/jaguar_xf_sportbrake_20d.html
EU-LAMBORGHINI-AVENTADOR-S-COUPE-01	4797	2030	1136	Lamborghini Aventador S official history; Automobile-Catalog 2017 Lamborghini Aventador S	https://www.lamborghini.com/en-en/history/aventador-s;https://www.automobile-catalog.com/car/2017/2606675/lamborghini_aventador_s.html
EU-LAMBORGHINI-HURACAN-PERFORMANTE-COUPE-01	4506	1924	1165	Lamborghini Huracán Performante official history; Automobile-Catalog 2017 Huracán Performante	https://www.lamborghini.com/en-en/history/huracan-performante;https://www.automobile-catalog.com/car/2017/2606720/lamborghini_huracan_performante.html
EU-OPEL-GRANDLAND-X-I-SUV-01	4477	1856	1609	Vauxhall Grandland X official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/grandland/price-guides/014_Grandland_X_Spec_PG_19_December_2017-1516896885.pdf
EU-HONDA-CIVIC-X-FK8-TYPE-R-HATCHBACK-01	4557	1877	1434	Honda Civic 2017 Type R press information; Honda Type R official specification	https://www.honda.co.jp/factbook/auto/CIVIC/201707/;https://cdn.honda.co.za/acc/general/cars/civic-type-r/Honda-Type-R-Specifications.pdf
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	BMW UK 6 Series Gran Turismo official technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0271717EN_GB/395434
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz W222/X222、S213、C238/A238、X253 AMG 和 W166/C292。
2. 处理 Alpina B3/B4 的 Sedan、Wagon、Coupe 和 Convertible 四个外廓。
3. 集中处理历史车型 Austin-Healey、Autobianchi、Ferrari、Lada、Peugeot 与 Suzuki。
4. 最后拆分 Iveco Daily VI 电动厢式车、底盘和 Bus 的轴距及车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增闭合 **20 个 Ktype、20 条 READY 映射**。
* 首次创建 **8 个 DIMENSION_GROUP**，覆盖 Alpina B3/B4、Mercedes-Benz E-Class C238/A238/S213 和 Mercedes-AMG GLC X253。
* B3 Sedan/Wagon 虽三维一致，但 BodyStyle 不同，分别建组；B4 Coupe/Convertible 因高度不同分别建组。BMW ALPINA 技术资料给出的 B3 Sedan、Touring 均为 4632×1811×1431 mm；B4 Coupe 与 Convertible 分别为 4640×1825×1373 mm、4640×1825×1380 mm。
* E-Class C238、A238 和 S213 分别闭合为 4826×1860×1430 mm、4826×1860×1428 mm、4933×1852×1475 mm；来源均明确区分车身宽度与含后视镜宽度。([汽车数据网][1])
* GLC 63 与 GLC 63 S 的 X253 SUV 外廓相同，统一复用一个尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：59
* PENDING 输入 Ktype：41
* READY 映射行：61
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127341	127341	Sedan	B3 S	F30	4	EU-ALPINA-B3-S-F30-SEDAN-01	HIGH		READY
127342	127342	Sedan	B3 S	F30	4	EU-ALPINA-B3-S-F30-SEDAN-01	HIGH		READY
127343	127343	Wagon	B3 S	F31	5	EU-ALPINA-B3-S-F31-WAGON-01	HIGH		READY
127344	127344	Wagon	B3 S	F31	5	EU-ALPINA-B3-S-F31-WAGON-01	HIGH		READY
127345	127345	Coupe	B4 S	F32	2	EU-ALPINA-B4-S-F32-COUPE-01	HIGH		READY
127346	127346	Coupe	B4 S	F32	2	EU-ALPINA-B4-S-F32-COUPE-01	HIGH		READY
127347	127347	Convertible	B4 S	F33	2	EU-ALPINA-B4-S-F33-CONVERTIBLE-01	HIGH		READY
127356	127356	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH		READY
127634	127634	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127635	127635	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127636	127636	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127637	127637	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127675	127675	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127680	127680	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH		READY
127681	127681	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
127682	127682	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
127683	127683	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127685	127685	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127686	127686	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127687	127687	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-S-F30-SEDAN-01	4632	1811	1431	BMW ALPINA B3 S BITURBO technical data sheet	https://www.7-forum.com/news/2017/alpina/alpina_b3_s_biturbo_technische_daten.pdf
EU-ALPINA-B3-S-F31-WAGON-01	4632	1811	1431	BMW ALPINA B3 S BITURBO technical data sheet	https://www.7-forum.com/news/2017/alpina/alpina_b3_s_biturbo_technische_daten.pdf
EU-ALPINA-B4-S-F32-COUPE-01	4640	1825	1373	Automobile-Catalog 2017 Alpina B4 S Biturbo Coupe	https://www.automobile-catalog.com/car/2017/2681210/alpina_b4_s_biturbo_coupe.html
EU-ALPINA-B4-S-F33-CONVERTIBLE-01	4640	1825	1380	Automobile-Catalog 2017 Alpina B4 S Biturbo Cabrio	https://www.automobile-catalog.com/car/2017/2681240/alpina_b4_s_biturbo_cabrio.html
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-9g-tronic-27376
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-220d-194hp-9g-tronic-30240
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Mercedes-Benz E-Class Saloon and Estate official brochure	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-MERCEDES-AMG-GLC-X253-SUV-01	4679	1930	1628	Automobile-Catalog Mercedes-AMG GLC 63 4MATIC+; Automobile-Catalog Mercedes-AMG GLC 63 S 4MATIC+	https://www.automobile-catalog.com/car/2017/2560415/mercedes-amg_glc_63_4matic_plus.html;https://www.automobile-catalog.com/car/2017/2560430/mercedes-amg_glc_63_s_4matic_plus.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz W222/X222 标准轴距、长轴距与 Maybach 分支。
2. 处理 Mercedes-AMG E 63/E 63 S S213，以及 GLE W166/C292 两种车身。
3. 批量解决 Iveco Daily VI 厢式车、底盘和 Bus 的轴距、车顶分支。
4. 集中处理历史车型 Austin-Healey、Autobianchi、Ferrari、Lada、Peugeot、Suzuki 和 Ford Explorer。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-9g-tronic-27376?utm_source=chatgpt.com "Mercedes-Benz E-class Coupe (C238) E 220d (194 Hp) 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2017/2560415/mercedes-amg_glc_63_4matic_plus.html?utm_source=chatgpt.com "2017 Mercedes-AMG GLC 63 4MATIC+ Specs Review (350 kW / 476 PS / 469 hp) (since June 2017 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增闭合 **11 个 Ktype、11 条 READY 映射**。
* 首次创建 **6 个 DIMENSION_GROUP**：

  * Mercedes-Benz S-Class W222 标准轴距
  * Mercedes-AMG S 63 V222 长轴距
  * Mercedes-Maybach S 560 X222
  * Mercedes-AMG E 63/E 63 S S213 Wagon
  * Mercedes-AMG GLE 43 W166 SUV
  * Mercedes-AMG GLE 43 C292 SUV-Coupe
* S-Class 标准轴距、长轴距 AMG 与 Maybach 外廓分别建组；E 63 与 E 63 S Wagon 复用同一物理外廓。
* 两个 GLE Ktype 按 W166 常规 SUV 与 C292 SUV-Coupe 分支分别闭合。([media.mbusa.com][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：70
* PENDING 输入 Ktype：30
* READY 映射行：72
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127328	127328	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127329	127329	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127330	127330	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127331	127331	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-AMG-S63-V222-FACELIFT-SEDAN-LWB-01	HIGH	AMG S63长轴距外廓。	READY
127332	127332	Sedan	Mercedes-Maybach S-Class Facelift	X222	4	EU-MERCEDES-MAYBACH-S560-X222-FACELIFT-SEDAN-01	HIGH	Maybach加长车身外廓。	READY
127339	127339	Wagon	E-Class V	S213	5	EU-MERCEDES-AMG-E63-S213-WAGON-01	HIGH		READY
127340	127340	Wagon	E-Class V	S213	5	EU-MERCEDES-AMG-E63-S213-WAGON-01	HIGH		READY
127693	127693	SUV	GLE I	W166	5	EU-MERCEDES-AMG-GLE43-W166-SUV-01	MEDIUM	W166常规SUV分支。	READY
127721	127721	SUV	GLE I Coupe	C292	5	EU-MERCEDES-AMG-GLE43-C292-SUV-COUPE-01	MEDIUM	C292 SUV-Coupe分支。	READY
127736	127736	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127739	127739	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	5141	1905	1498	Mercedes-Benz UK New S-Class official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2018/01/new-s-class.pdf
EU-MERCEDES-AMG-S63-V222-FACELIFT-SEDAN-LWB-01	5294	1914	1499	Mercedes-Benz UK New S-Class official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2018/01/new-s-class.pdf
EU-MERCEDES-MAYBACH-S560-X222-FACELIFT-SEDAN-01	5462	1905	1498	Automobile-Catalog 2018 Mercedes-Maybach S 560 4MATIC	https://www.automobile-catalog.com/car/2018/2564570/mercedes-maybach_s_560_4matic.html
EU-MERCEDES-AMG-E63-S213-WAGON-01	4993	1907	1460	Mercedes-AMG E-Class official owners manual supplement September 2017	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-qa/pdf/mercedes-amg-e-class-owners-manual-supplement-september-2017-1.pdf
EU-MERCEDES-AMG-GLE43-W166-SUV-01	4816	1999	1760	Mercedes-Benz USA 2017 Mercedes-AMG GLE43 official specifications	https://media.mbusa.com/releases/release-95853e11e010b7b5e744226d7f297469-2017-mercedes-amg-gle43-specifications
EU-MERCEDES-AMG-GLE43-C292-SUV-COUPE-01	4892	2004	1720	Car and Driver 2017 Mercedes-AMG GLE43 Coupe specifications	https://www.caranddriver.com/mercedes-amg/gle43-coupe-4matic-gle63-s-coupe-4matic/specs/2017/mercedes-amg_gle43-coupe-4matic-gle63-s-coupe-4matic_mercedes-amg-gle43-coupe-4matic_2017
```

## 下一步优先处理

1. 批量闭合 Iveco Daily VI 电动厢式车、底盘和 Bus 的轴距及车顶分支。
2. 处理 Austin-Healey、Autobianchi、Ferrari、Lada、Peugeot 等历史车型。
3. 处理 Citroën Xsara Van、Suzuki Vitara/Grand Vitara、Ford Explorer 等潜在多外廓车型。
4. 最后闭合 JAC iEV6E、Fiat 500L、Lada Granta、Chrysler 300C 和 Toyota Proace Chassis。

推进信号：CONTINUE

[1]: https://media.mbusa.com/releases/release-95853e11e010b7b5e744226d7f297469-2017-mercedes-amg-gle43-specifications?utm_source=chatgpt.com "2017 Mercedes-AMG GLE43 Specifications"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 新增闭合 **10 个 Ktype、10 条 READY 映射**。
* 首次创建 **10 个 DIMENSION_GROUP**。
* Austin-Healey 100-Six 与 Sprite Mk IV 分别闭合；100-Six 的 BN4/BN6 车身代码边界不影响本次确认的外廓，因此映射层不强填组合 BodyCode。([汽车目录][1])
* Autobianchi Y10 Series II 的 4WD 与前驱版尺寸不同，分别建组：4WD 为 3390×1540×1460 mm，前驱版为 3390×1510×1430 mm。([Automoto.it][2])
* Ferrari 308 GTBi/GTSi 与 Mondial 3.2 Coupe/Cabriolet 按不同 BodyStyle 分别建组，三维采用 Ferrari 官方历史规格。([法拉利][3])
* Peugeot 404 Wagon 与 Chrysler 300C I Facelift Sedan 已闭合。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：80
* PENDING 输入 Ktype：20
* READY 映射行：82
* 已确认尺寸组：46
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127250	127250	Convertible	100-Six		2	EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	MEDIUM	BN4与BN6不在本行强行合并填写BodyCode；确认外廓一致。	READY
127251	127251	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH		READY
127253	127253	Hatchback	Y10 Series II		3	EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-4WD-01	HIGH	4WD版具有独立宽度和高度外廓。	READY
127254	127254	Hatchback	Y10 Series II		3	EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-FWD-01	HIGH	前驱版外廓。	READY
127270	127270	Convertible	308 GTBi/GTSi		2	EU-FERRARI-308-GTSI-TARGA-01	HIGH	Targa车身独立于GTBi Coupe。	READY
127271	127271	Coupe	308 GTBi/GTSi		2	EU-FERRARI-308-GTBI-COUPE-01	HIGH		READY
127274	127274	Convertible	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	HIGH		READY
127275	127275	Coupe	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-COUPE-01	HIGH		READY
127656	127656	Wagon	404		5	EU-PEUGEOT-404-WAGON-01	MEDIUM	Break与Familiale在该发动机Ktype下按共同Wagon外廓映射。	READY
127701	127701	Sedan	300C I Facelift	LX	4	EU-CHRYSLER-300C-I-FACELIFT-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	4001	1537	1244	Automobile-Catalog 1957 Austin-Healey 100-Six 2-seater	https://www.automobile-catalog.com/car/1957/258680/austin-healey_100_six_2-seater_overdrive.html
EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	3496	1394	1200	Austin-Healey Sprite Mk IV official brochure; Automobile-Catalog 1967 Austin-Healey Sprite Mk IV	https://www.auto-brochures.com/makes/austin-healey/Austin-Healey_int%20Sprite_1967.pdf;https://www.automobile-catalog.com/car/1967/75710/austin-healey_sprite_mk_iv.html
EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-4WD-01	3390	1540	1460	Automoto Autobianchi Y10 Fire 1.1 i.e. cat 4WD	https://www.automoto.it/catalogo/autobianchi/y10/fire-11-ie-cat-4wd-my-91/10356
EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-FWD-01	3390	1510	1430	Automoto Autobianchi Y10 Fire 1.1 i.e. cat LX	https://www.automoto.it/catalogo/autobianchi/y10/fire-11-ie-cat-lx/10362
EU-FERRARI-308-GTSI-TARGA-01	4230	1720	1120	Ferrari 308 GTSi official historical specification	https://www.ferrari.com/en-EN/auto/308-gtsi
EU-FERRARI-308-GTBI-COUPE-01	4230	1720	1120	Ferrari 308 GTBi official historical specification	https://www.ferrari.com/en-EN/auto/308-gtbi
EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	4535	1795	1265	Ferrari 3.2 Mondial Cabriolet official historical specification	https://www.ferrari.com/en-EN/auto/3.2-mondial-cabriolet
EU-FERRARI-MONDIAL-3-2-COUPE-01	4535	1795	1235	Ferrari 3.2 Mondial official historical specification	https://www.ferrari.com/en-EN/auto/3.2-mondial
EU-PEUGEOT-404-WAGON-01	4582	1625	1490	Automobile-Catalog 1963 Peugeot 404 Break Super Luxe	https://www.automobile-catalog.com/car/1963/2554295/peugeot_404_break_super_luxe.html
EU-CHRYSLER-300C-I-FACELIFT-SEDAN-01	5015	1880	1475	Automobile-Catalog 2008 Chrysler 300C 5.7 V8 Hemi Europe	https://www.automobile-catalog.com/car/2008/524465/chrysler_300c_5_7_v8_hemi.html
```

## 下一步优先处理

1. 闭合 Autobianchi Primula、Bitter Type 3、Caterham Seven、Lada Toscana、Suzuki Grand Vitara 和 Ford Explorer。
2. 拆分 Citroën Xsara Kasten/Wagon 与 Kasten/Hatchback 两种外廓。
3. 处理 Lada Granta、Suzuki Vitara、JAC iEV6E、Fiat 500L 和 Toyota Proace Chassis。
4. 最后集中处理 Iveco Daily VI Van、Chassis 和 Bus 的轴距及车顶派生分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1957/258680/austin-healey_100_six_2-seater_overdrive.html?utm_source=chatgpt.com "1957 Austin-Healey 100 Six (2-seater) overdrive Specs ..."
[2]: https://www.automoto.it/catalogo/autobianchi/y10/fire-11-ie-cat-4wd-my-91/10356 "Autobianchi Y10 Fire 1.1 i.e. cat 4WD: prezzo e scheda tecnica - Automoto.it"
[3]: https://www.ferrari.com/en-EN/auto/3.2-mondial-cabriolet?utm_source=chatgpt.com "Ferrari 3.2 Mondial Cabriolet (1985) - Ferrari.com"
[4]: https://www.automobile-catalog.com/car/1963/2554295/peugeot_404_break_super_luxe.html?utm_source=chatgpt.com "1963 Peugeot 404 Break Super Luxe Specs Review (48 kW / 65 PS / 64 hp) (since September 1963 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 新增闭合 **7 个 Ktype、9 条 READY 映射**，首次创建 **9 个 DIMENSION_GROUP**。
* `127412` 的 Suzuki Vitara 1.6 16V 已确认同时覆盖 3 门短轴和 5 门长轴两种物理外廓，分别为 3632×1630×1662 mm 和 4030×1635×1700 mm，因此拆成两条派生映射。([汽车数据网][1])
* `127741` 的 Ford Explorer 4.0 SOHC 同时存在 3 门 Sport 和 5 门车型，分别采用 4562×1783×1702 mm 与 4813×1783×1720 mm，不合并尺寸组。([汽车目录][2])
* Bitter Type 3、Grand Vitara II、Granta Liftback、JAC iEV6E 和 Fiat 500L Natural Power 的物理外廓已闭合。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：87
* PENDING 输入 Ktype：13
* READY 映射行：91
* 已确认尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127261	127261	Convertible	Type 3		2	EU-BITTER-TYPE-3-CONVERTIBLE-01	HIGH		READY
127378	127378	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	HIGH		READY
127402	127402	Hatchback	Granta I		5	EU-LADA-GRANTA-I-LIFTBACK-01	HIGH		READY
127412_3dr	127412	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-3D-01	HIGH	三门短轴物理外廓。	READY
127412_5dr	127412	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-5D-01	HIGH	五门长轴物理外廓。	READY
127454	127454	Hatchback	iEV6E I		5	EU-JAC-IEV6E-I-HATCHBACK-01	MEDIUM		READY
127510	127510	Hatchback	500L Facelift 2017		5	EU-FIAT-500L-FACELIFT-2017-HATCHBACK-01	HIGH		READY
127741_3dr	127741	SUV	Explorer II		3	EU-FORD-USA-EXPLORER-II-SUV-3D-01	MEDIUM	4.0 SOHC三门Sport物理外廓。	READY
127741_5dr	127741	SUV	Explorer II		5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	MEDIUM	4.0 SOHC五门物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BITTER-TYPE-3-CONVERTIBLE-01	4450	1765	1395	Automobile-Catalog 1988 Bitter Type 3 Cabriolet 3.0	https://www.automobile-catalog.com/car/1988/261695/bitter_type_3_cabriolet_3_0.html
EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	4470	1810	1695	Auto-Data Suzuki Grand Vitara II 5 Door 2.7 V6 4WD	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-2.7-v6-185hp-4wd-45647
EU-LADA-GRANTA-I-LIFTBACK-01	4246	1700	1500	Auto-Data Lada Granta I Hatchback	https://www.auto-data.net/en/lada-granta-i-hatchback-generation-4625
EU-SUZUKI-VITARA-I-SUV-3D-01	3632	1630	1662	Auto-Data Suzuki Vitara 1.6 i 16V 3 Door	https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-16v-3-dr-97hp-16429
EU-SUZUKI-VITARA-I-SUV-5D-01	4030	1635	1700	Auto-Data Suzuki Vitara 1.6 i 16V 5 Door	https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-16v-5-dr-97hp-16430
EU-JAC-IEV6E-I-HATCHBACK-01	3630	1670	1475	AutoCango 2017 JAC iEV6E 22 kWh specifications	https://www.autocango.com/ar/carspecs-detail/JAC-iEV6E-7E8WW
EU-FIAT-500L-FACELIFT-2017-HATCHBACK-01	4242	1784	1658	Auto-Data Fiat 500L 0.9 TwinAir Turbo Methane	https://www.auto-data.net/en/fiat-500l-facelift-2017-0.9-twinair-85-80hp-turbo-methane-30037
EU-FORD-USA-EXPLORER-II-SUV-3D-01	4562	1783	1702	Automobile-Catalog 1998 Ford Explorer Sport 4WD 4.0 SOHC	https://www.automobile-catalog.com/car/1998/889460/ford_explorer_sport_4wd_4_0l_sohc_v-6_automatic.html
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4813	1783	1720	Edmunds 1998 Ford Explorer 4-Door specifications	https://www.edmunds.com/ford/explorer/1998/suv/st-9451/features-specs/
```

## 下一步优先处理

1. 解决 Autobianchi Primula Coupe 的标准 Coupe 与 Coupe S 尺寸冲突。
2. 闭合 Lada Toscana 1.6/1.7 和 Caterham Seven 1.6，确认是否可共同复用既有 S3 尺寸组。
3. 拆分 Citroën Xsara 商用 Wagon 与商用 Hatchback 外廓。
4. 确认 Toyota Proace Platform Cab 的 Medium 单一分支。
5. 最后集中处理 Iveco Daily VI Van、Chassis 和 Bus 的轴距、车顶及吨位派生分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-16v-3-dr-97hp-16429 "Suzuki Vitara (ET,TA) 1.6 i 16V (3 dr) (97 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1998/889460/ford_explorer_sport_4wd_4_0l_sohc_v-6_automatic.html?utm_source=chatgpt.com "1998 Ford Explorer Sport 4WD 4.0L SOHC V-6 automatic ..."
[3]: https://www.automobile-catalog.com/car/1988/261695/bitter_type_3_cabriolet_3_0.html?utm_source=chatgpt.com "1988 Bitter Type 3 Cabriolet 3.0 (man. 5) (model for Europe ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1) 更新点

* 新增闭合 **7 个 Ktype、7 条 READY 映射**。
* 首次创建 **6 个 DIMENSION_GROUP**；Toyota Proace Platform Cab 直接复用已有 `EU-TOYOTA-PROACE-II-BODY-MEDIUM-01`。
* Lada Toscana 1.6 与 1.7 对应不同 2107 派生型号，已按不同三维分别建组。([ultimatespecs.com][1])
* Citroën Xsara 商用旅行车和商用掀背车按 N2/N1 两种物理外廓分组；宽度均采用不含后视镜口径。([汽车数据网][2])
* 当前仅剩 Iveco Daily VI 的 6 个 Ktype 尚未闭合。

## 2) 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：94
* PENDING 输入 Ktype：6
* READY 映射行：98
* 已确认尺寸组：61
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127252	127252	Coupe	Primula Coupé		2	EU-AUTOBIANCHI-PRIMULA-COUPE-01	MEDIUM	1.2升双门Coupé物理外廓。	READY
127260	127260	Sedan	2107	21073	4	EU-LADA-2107-21073-SEDAN-01	HIGH	1.7升21073外廓。	READY
127267	127267	Convertible	Seven S3	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-01	MEDIUM	1986至1991年S3窄体车架。	READY
127297	127297	Sedan	2107	21074	4	EU-LADA-2107-21074-SEDAN-01	HIGH	1.6升21074外廓。	READY
127398	127398	Van	Xsara I Facelift	N2	5	EU-CITROEN-XSARA-I-FACELIFT-VAN-WAGON-01	MEDIUM	N2旅行车式商用外廓。	READY
127408	127408	Van	Xsara I Facelift	N1	5	EU-CITROEN-XSARA-I-FACELIFT-VAN-HATCHBACK-01	MEDIUM	N1掀背式商用外廓。	READY
127812	127812	Pickup	Proace II		2	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium Platform Cab物理外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-PRIMULA-COUPE-01	3785	1580	1350	Automobile-Catalog 1968 Autobianchi Primula Coupe	https://www.automobile-catalog.com/car/1968/259160/autobianchi_primula_coupe.html
EU-LADA-2107-21073-SEDAN-01	4140	1620	1430	UltimateSpecs Lada 2107 1.7i	https://www.ultimatespecs.com/car-specs/Lada/5528/Lada-2107-17i.html
EU-CATERHAM-SEVEN-S3-CONVERTIBLE-01	3378	1575	1093	CarSized Caterham Seven 1973 Roadster	https://www.carsized.com/en/cars/caterham-seven-1973-roadster/
EU-LADA-2107-21074-SEDAN-01	4128	1620	1446	UltimateSpecs Lada 2107 1.6	https://www.ultimatespecs.com/car-specs/Lada/666/Lada-2107-16.html
EU-CITROEN-XSARA-I-FACELIFT-VAN-WAGON-01	4369	1705	1420	Auto-Data Citroen Xsara Break N2 Phase II 1.4 i	https://www.auto-data.net/en/citroen-xsara-break-n2-phase-ii-1.4-i-75hp-46541
EU-CITROEN-XSARA-I-FACELIFT-VAN-HATCHBACK-01	4188	1705	1405	Automobile-Catalog 2000 Citroen Xsara 2.0 HDi 90	https://www.automobile-catalog.com/car/2000/547265/citroen_xsara_2_0_hdi_90_exclusive.html
```

## 5) 下一步优先处理

1. 将 `127609`、`127611` 的 Iveco Daily VI 电动厢式车按轴距、车身长度和车顶高度完整派生。
2. 将 `127615`、`127618` 的电动底盘车按 SWB、MWB、LWB及单/双后轮边界拆分。
3. 将 `127646`、`127648` 的 Bus 按实际客车车身长度和高度分支闭合。
4. 六个 Ktype 全部 READY 后，立即执行一次机械检查并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Lada/666/Lada-2107-16.html "Lada 2107 1.6 Specs, Performance, Comparisons"
[2]: https://www.auto-data.net/en/citroen-xsara-break-n2-phase-ii-1.4-i-75hp-46541 "Citroen Xsara Break (N2, Phase II) 1.4 i (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1) 更新点

* `127609` 已按 Daily VI Electric 35S60E 的 V7、V9、V11、V12、V13、V16、V18 七种已确认厢式车外廓拆分并全部转为 READY。各分支的长度、车身宽度及高度已分别闭合。([largus.fr][1])
* 首次创建 7 个 DIMENSION_GROUP。
* 其余已确认 Ktype 和尺寸组保持不变，未重复核对或输出。

## 2) 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：95
* PENDING 输入 Ktype：5
* READY 映射行：105
* 已确认尺寸组：68
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127609_v7	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V7-01	HIGH	V7短轴低顶厢式车外廓。	READY
127609_v9	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V9-01	HIGH	V9中轴低顶厢式车外廓。	READY
127609_v11	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V11-01	HIGH	V11中轴高顶厢式车外廓。	READY
127609_v12	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V12-01	HIGH	V12加长中轴高顶厢式车外廓。	READY
127609_v13	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V13-01	HIGH	V13加长中轴超高顶厢式车外廓。	READY
127609_v16	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V16-01	HIGH	V16长轴高顶厢式车外廓。	READY
127609_v18	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V18-01	HIGH	V18长轴超高顶厢式车外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V7-01	5000	2010	2200	L'Argus Iveco Daily 35S60EV7 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV7-1930599.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V9-01	5520	2010	2200	L'Argus Iveco Daily 35S60EV9 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV9-1930600.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V11-01	5520	2010	2610	L'Argus Iveco Daily 35S60EV11 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV11-1930601.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V12-01	5920	2010	2580	L'Argus Iveco Daily 35S60EV12 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV12-1930602.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V13-01	5920	2010	2780	L'Argus Iveco Daily 35S60EV13 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV13-1930603.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V16-01	7090	2010	2580	L'Argus Iveco Daily 35S60EV16 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV16-1930604.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V18-01	7090	2010	2780	L'Argus Iveco Daily 35S60EV18 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV18-1930605.html
```

## 5) 下一步优先处理

1. 闭合 `127611` 的 Daily VI 50C80E 电动厢式车长度与车顶分支。
2. 批量闭合 `127615`、`127618` 的电动底盘车轴距及 SRW/DRW 外廓。
3. 闭合 `127646`、`127648` 的 40C、50C、60C Bus 分支。
4. 剩余五个 Ktype 全部 READY 后，立即组装最终完整双表及两个指定下载文件。

推进信号：CONTINUE

[1]: https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV7-1930599.html "www.largus.fr"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1) 更新点

* 闭合 `127615` 的 Iveco Daily VI 35S60E/35C60E 电动底盘车。
* 按 **SRW/DRW 与轴距**拆分为 7 个物理分支：35S60E 包含 3000、3450、3750、4100 mm 四种轴距；35C60E 包含 3450、3750、4100 mm 三种轴距。各分支长度和高度不同，不能合并为单一尺寸组。([largus.fr][1])
* 本轮首次创建 7 个 DIMENSION_GROUP；其他已确认记录保持不变。

## 2) 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* READY 映射行：112
* 已确认尺寸组：75
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127615_srw_wb3000	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3000-01	HIGH	35S60E单后轮、3000毫米轴距底盘。	READY
127615_srw_wb3450	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3450-01	HIGH	35S60E单后轮、3450毫米轴距底盘。	READY
127615_srw_wb3750	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3750-01	HIGH	35S60E单后轮、3750毫米轴距底盘。	READY
127615_srw_wb4100	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB4100-01	HIGH	35S60E单后轮、4100毫米轴距底盘。	READY
127615_drw_wb3450	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	HIGH	35C60E双后轮、3450毫米轴距底盘。	READY
127615_drw_wb3750	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	HIGH	35C60E双后轮、3750毫米轴距底盘。	READY
127615_drw_wb4100	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	HIGH	35C60E双后轮、4100毫米轴距底盘。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3000-01	5020	2010	2230	L'Argus Iveco Daily 35S60E Empattement 3000 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3000-1928100.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3450-01	5900	2010	2240	L'Argus Iveco Daily 35S60E Empattement 3450 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3450-1928101.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3750-01	6510	2010	2220	L'Argus Iveco Daily 35S60E Empattement 3750 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3750-1928102.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB4100-01	6510	2010	2190	L'Argus Iveco Daily 35S60E Empattement 4100 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B4100-1928099.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	5800	2010	2200	L'Argus Iveco Daily 35C60E Empattement 3450 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B3450-1928104.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	6410	2010	2190	L'Argus Iveco Daily 35C60E Empattement 3750 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B3750-1928105.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	6810	2010	2190	L'Argus Iveco Daily 35C60E Empattement 4100 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B4100-1928103.html
```

## 5) 下一步优先处理

1. 闭合 `127611` 的 50C80E 电动厢式车 V16/V18 车顶分支。
2. 闭合 `127618` 的 45C80E、50C80E 电动底盘轴距分支。
3. 统一处理 `127646`、`127648` 的 Daily VI Bus 40C、50C、60C 车身分支。
4. 剩余 4 个 Ktype 全部 READY 后，立即输出最终完整双表及两个指定下载文件。

推进信号：CONTINUE

[1]: https://www.largus.fr/fiche-technique/utilitaires-legers/Iveco/Daily%2BCcb/2019.html "www.largus.fr"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1) 更新点

* `127618` 已按缓存优先模式闭合。
* 45C80E、50C80E 均链接至本批此前确认的 Daily VI 电动双后轮底盘尺寸组，按 3450、3750、4100 mm 三种轴距拆分。
* 新增 **3 条 READY 映射**；本轮未新建或修正尺寸组，未重复抓取三维和来源。

## 2) 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* PENDING 输入 Ktype：3
* READY 映射行：115
* 已确认尺寸组：75
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127618_drw_wb3450	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	HIGH	45C80E/50C80E双后轮、3450毫米轴距底盘。	READY
127618_drw_wb3750	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	HIGH	45C80E/50C80E双后轮、3750毫米轴距底盘。	READY
127618_drw_wb4100	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	HIGH	45C80E/50C80E双后轮、4100毫米轴距底盘。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无。

## 5) 下一步优先处理

1. 闭合 `127611` 的 Daily VI 50C80E 电动厢式车车身长度和车顶分支。
2. 联合处理 `127646`、`127648` 的 Daily VI Bus 40C、50C、60C 外廓；两种功率只建立映射，不重复创建相同尺寸组。
3. 三个剩余 Ktype 全部 READY 后，立即执行一次机械收尾并输出完整双表及指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 剩余 `127611`、`127646`、`127648` 已全部闭合。
* 当前 100 个输入 Ktype 全部为 `READY`，不存在 `PENDING`。
* 完整快照包含 **123 条 Ktype 映射、79 个尺寸组**。机械汇总发现此前进度中的尺寸组数量少计 1 个，最终表已按实际引用去重计数，不影响任何既有映射。
* 已完成固定表头、`id` 唯一、尺寸组 ID 唯一、引用闭合、非空尺寸与来源、孤立尺寸组检查。
* 已创建两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* Ktype 映射行：123
* DIMENSION_GROUP：79
* 重复 `id`：0
* 未闭合尺寸组引用：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127250	127250	Convertible	100-Six		2	EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	MEDIUM	BN4与BN6不在本行强行合并填写BodyCode；确认外廓一致。	READY
127251	127251	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH		READY
127252	127252	Coupe	Primula Coupé		2	EU-AUTOBIANCHI-PRIMULA-COUPE-01	MEDIUM	1.2升双门Coupé物理外廓。	READY
127253	127253	Hatchback	Y10 Series II		3	EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-4WD-01	HIGH	4WD版具有独立宽度和高度外廓。	READY
127254	127254	Hatchback	Y10 Series II		3	EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-FWD-01	HIGH	前驱版外廓。	READY
127260	127260	Sedan	2107	21073	4	EU-LADA-2107-21073-SEDAN-01	HIGH	1.7升21073外廓。	READY
127261	127261	Convertible	Type 3		2	EU-BITTER-TYPE-3-CONVERTIBLE-01	HIGH		READY
127267	127267	Convertible	Seven S3	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-01	MEDIUM	1986至1991年S3窄体车架。	READY
127270	127270	Convertible	308 GTBi/GTSi		2	EU-FERRARI-308-GTSI-TARGA-01	HIGH	Targa车身独立于GTBi Coupe。	READY
127271	127271	Coupe	308 GTBi/GTSi		2	EU-FERRARI-308-GTBI-COUPE-01	HIGH		READY
127274	127274	Convertible	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	HIGH		READY
127275	127275	Coupe	Mondial 3.2		2	EU-FERRARI-MONDIAL-3-2-COUPE-01	HIGH		READY
127296_3dr	127296	Hatchback	Samara 2	2113	3	EU-LADA-SAMARA-2113-HATCHBACK-3D-01	HIGH	拆分为2113三门物理外廓。	READY
127296_5dr	127296	Hatchback	Samara 2	2114	5	EU-LADA-SAMARA-2114-HATCHBACK-5D-01	HIGH	拆分为2114五门物理外廓。	READY
127297	127297	Sedan	2107	21074	4	EU-LADA-2107-21074-SEDAN-01	HIGH	1.6升21074外廓。	READY
127326	127326	MPV	Scénic IV		5	EU-RENAULT-SCENIC-IV-MPV-01	HIGH		READY
127327	127327	MPV	Grand Scénic IV		5	EU-RENAULT-GRAND-SCENIC-IV-MPV-01	HIGH		READY
127328	127328	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127329	127329	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127330	127330	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127331	127331	Sedan	S-Class VI Facelift	V222	4	EU-MERCEDES-AMG-S63-V222-FACELIFT-SEDAN-LWB-01	HIGH	AMG S63长轴距外廓。	READY
127332	127332	Sedan	Mercedes-Maybach S-Class Facelift	X222	4	EU-MERCEDES-MAYBACH-S560-X222-FACELIFT-SEDAN-01	HIGH	Maybach加长车身外廓。	READY
127339	127339	Wagon	E-Class V	S213	5	EU-MERCEDES-AMG-E63-S213-WAGON-01	HIGH		READY
127340	127340	Wagon	E-Class V	S213	5	EU-MERCEDES-AMG-E63-S213-WAGON-01	HIGH		READY
127341	127341	Sedan	B3 S	F30	4	EU-ALPINA-B3-S-F30-SEDAN-01	HIGH		READY
127342	127342	Sedan	B3 S	F30	4	EU-ALPINA-B3-S-F30-SEDAN-01	HIGH		READY
127343	127343	Wagon	B3 S	F31	5	EU-ALPINA-B3-S-F31-WAGON-01	HIGH		READY
127344	127344	Wagon	B3 S	F31	5	EU-ALPINA-B3-S-F31-WAGON-01	HIGH		READY
127345	127345	Coupe	B4 S	F32	2	EU-ALPINA-B4-S-F32-COUPE-01	HIGH		READY
127346	127346	Coupe	B4 S	F32	2	EU-ALPINA-B4-S-F32-COUPE-01	HIGH		READY
127347	127347	Convertible	B4 S	F33	2	EU-ALPINA-B4-S-F33-CONVERTIBLE-01	HIGH		READY
127348	127348	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH		READY
127350	127350	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH		READY
127352	127352	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH		READY
127353	127353	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH		READY
127355	127355	Convertible	Fortwo III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-01	HIGH		READY
127356	127356	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH		READY
127357	127357	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127358	127358	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127359	127359	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127360	127360	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127368	127368	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127369	127369	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127378	127378	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	HIGH		READY
127384	127384	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	HIGH		READY
127386	127386	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	HIGH		READY
127390	127390	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	HIGH		READY
127398	127398	Van	Xsara I Facelift	N2	5	EU-CITROEN-XSARA-I-FACELIFT-VAN-WAGON-01	MEDIUM	N2旅行车式商用外廓。	READY
127402	127402	Hatchback	Granta I		5	EU-LADA-GRANTA-I-LIFTBACK-01	HIGH		READY
127408	127408	Van	Xsara I Facelift	N1	5	EU-CITROEN-XSARA-I-FACELIFT-VAN-HATCHBACK-01	MEDIUM	N1掀背式商用外廓。	READY
127412_3dr	127412	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-3D-01	HIGH	三门短轴物理外廓。	READY
127412_5dr	127412	SUV	Vitara I		5	EU-SUZUKI-VITARA-I-SUV-5D-01	HIGH	五门长轴物理外廓。	READY
127454	127454	Hatchback	iEV6E I		5	EU-JAC-IEV6E-I-HATCHBACK-01	MEDIUM		READY
127507	127507	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH		READY
127508	127508	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH		READY
127510	127510	Hatchback	500L Facelift 2017		5	EU-FIAT-500L-FACELIFT-2017-HATCHBACK-01	HIGH		READY
127518_3dr	127518	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	HIGH	拆分为三门物理外廓。	READY
127518_5dr	127518	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	HIGH	拆分为五门物理外廓。	READY
127519	127519	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127520	127520	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127521	127521	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127522	127522	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH		READY
127526	127526	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127527	127527	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127528	127528	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127529	127529	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127530	127530	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127534	127534	Wagon	XF II	X260	5	EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	HIGH		READY
127609_v7	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V7-01	HIGH	V7短轴低顶厢式车外廓。	READY
127609_v9	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V9-01	HIGH	V9中轴低顶厢式车外廓。	READY
127609_v11	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V11-01	HIGH	V11中轴高顶厢式车外廓。	READY
127609_v12	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V12-01	HIGH	V12加长中轴高顶厢式车外廓。	READY
127609_v13	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V13-01	HIGH	V13加长中轴超高顶厢式车外廓。	READY
127609_v16	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V16-01	HIGH	V16长轴高顶厢式车外廓。	READY
127609_v18	127609	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V18-01	HIGH	V18长轴超高顶厢式车外廓。	READY
127611_v16	127611	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V16-01	HIGH	V16长轴高顶厢式车外廓。	READY
127611_v18	127611	Van	Daily VI		4	EU-IVECO-DAILY-VI-ELECTRIC-VAN-V18-01	HIGH	V18长轴超高顶厢式车外廓。	READY
127615_srw_wb3000	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3000-01	HIGH	35S60E单后轮、3000毫米轴距底盘。	READY
127615_srw_wb3450	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3450-01	HIGH	35S60E单后轮、3450毫米轴距底盘。	READY
127615_srw_wb3750	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3750-01	HIGH	35S60E单后轮、3750毫米轴距底盘。	READY
127615_srw_wb4100	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB4100-01	HIGH	35S60E单后轮、4100毫米轴距底盘。	READY
127615_drw_wb3450	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	HIGH	35C60E双后轮、3450毫米轴距底盘。	READY
127615_drw_wb3750	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	HIGH	35C60E双后轮、3750毫米轴距底盘。	READY
127615_drw_wb4100	127615	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	HIGH	35C60E双后轮、4100毫米轴距底盘。	READY
127618_drw_wb3450	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	HIGH	45C80E/50C80E双后轮、3450毫米轴距底盘。	READY
127618_drw_wb3750	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	HIGH	45C80E/50C80E双后轮、3750毫米轴距底盘。	READY
127618_drw_wb4100	127618	Pickup	Daily VI		2	EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	HIGH	45C80E/50C80E双后轮、4100毫米轴距底盘。	READY
127634	127634	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127635	127635	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127636	127636	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127637	127637	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127646_wb3520l	127646	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB3520L-01	HIGH	3520L短车身Minibus外廓。	READY
127646_wb4100	127646	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB4100-01	HIGH	4100长车身Minibus外廓。	READY
127646_wb4100l	127646	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB4100L-01	HIGH	4100L加长高顶Minibus外廓。	READY
127648_wb3520l	127648	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB3520L-01	HIGH	3520L短车身Minibus外廓。	READY
127648_wb4100	127648	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB4100-01	HIGH	4100长车身Minibus外廓。	READY
127648_wb4100l	127648	Bus	Daily VI			EU-IVECO-DAILY-VI-MINIBUS-WB4100L-01	HIGH	4100L加长高顶Minibus外廓。	READY
127656	127656	Wagon	404		5	EU-PEUGEOT-404-WAGON-01	MEDIUM	Break与Familiale在该发动机Ktype下按共同Wagon外廓映射。	READY
127663	127663	Coupe	Aventador S		2	EU-LAMBORGHINI-AVENTADOR-S-COUPE-01	HIGH		READY
127664	127664	Coupe	Huracán Performante		2	EU-LAMBORGHINI-HURACAN-PERFORMANTE-COUPE-01	HIGH		READY
127675	127675	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH		READY
127680	127680	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH		READY
127681	127681	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
127682	127682	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
127683	127683	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127685	127685	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127686	127686	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127687	127687	SUV	GLC X253	X253	5	EU-MERCEDES-AMG-GLC-X253-SUV-01	HIGH		READY
127689	127689	SUV	Grandland X I		5	EU-OPEL-GRANDLAND-X-I-SUV-01	HIGH		READY
127690	127690	SUV	Grandland X I		5	EU-OPEL-GRANDLAND-X-I-SUV-01	HIGH		READY
127693	127693	SUV	GLE I	W166	5	EU-MERCEDES-AMG-GLE43-W166-SUV-01	MEDIUM	W166常规SUV分支。	READY
127701	127701	Sedan	300C I Facelift	LX	4	EU-CHRYSLER-300C-I-FACELIFT-SEDAN-01	HIGH		READY
127721	127721	SUV	GLE I Coupe	C292	5	EU-MERCEDES-AMG-GLE43-C292-SUV-COUPE-01	MEDIUM	C292 SUV-Coupe分支。	READY
127736	127736	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127739	127739	Sedan	S-Class VI Facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	HIGH	标准轴距W222外廓。	READY
127741_3dr	127741	SUV	Explorer II		3	EU-FORD-USA-EXPLORER-II-SUV-3D-01	MEDIUM	4.0 SOHC三门Sport物理外廓。	READY
127741_5dr	127741	SUV	Explorer II		5	EU-FORD-USA-EXPLORER-II-SUV-5D-01	MEDIUM	4.0 SOHC五门物理外廓。	READY
127812	127812	Pickup	Proace II		2	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium Platform Cab物理外廓。	READY
127817	127817	Hatchback	Civic X	FK8	5	EU-HONDA-CIVIC-X-FK8-TYPE-R-HATCHBACK-01	HIGH	Type R宽体外廓独立于普通Civic X Hatchback。	READY
127825	127825	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127827	127827	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127828	127828	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127829	127829	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1401-1500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	4001	1537	1244	Automobile-Catalog 1957 Austin-Healey 100-Six 2-seater	https://www.automobile-catalog.com/car/1957/258680/austin-healey_100_six_2-seater_overdrive.html
EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	3496	1394	1200	Austin-Healey Sprite Mk IV official brochure; Automobile-Catalog 1967 Austin-Healey Sprite Mk IV	https://www.auto-brochures.com/makes/austin-healey/Austin-Healey_int%20Sprite_1967.pdf;https://www.automobile-catalog.com/car/1967/75710/austin-healey_sprite_mk_iv.html
EU-AUTOBIANCHI-PRIMULA-COUPE-01	3785	1580	1350	Automobile-Catalog 1968 Autobianchi Primula Coupe	https://www.automobile-catalog.com/car/1968/259160/autobianchi_primula_coupe.html
EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-4WD-01	3390	1540	1460	Automoto Autobianchi Y10 Fire 1.1 i.e. cat 4WD	https://www.automoto.it/catalogo/autobianchi/y10/fire-11-ie-cat-4wd-my-91/10356
EU-AUTOBIANCHI-Y10-SERIES-II-HATCHBACK-FWD-01	3390	1510	1430	Automoto Autobianchi Y10 Fire 1.1 i.e. cat LX	https://www.automoto.it/catalogo/autobianchi/y10/fire-11-ie-cat-lx/10362
EU-LADA-2107-21073-SEDAN-01	4140	1620	1430	UltimateSpecs Lada 2107 1.7i	https://www.ultimatespecs.com/car-specs/Lada/5528/Lada-2107-17i.html
EU-BITTER-TYPE-3-CONVERTIBLE-01	4450	1765	1395	Automobile-Catalog 1988 Bitter Type 3 Cabriolet 3.0	https://www.automobile-catalog.com/car/1988/261695/bitter_type_3_cabriolet_3_0.html
EU-CATERHAM-SEVEN-S3-CONVERTIBLE-01	3378	1575	1093	CarSized Caterham Seven 1973 Roadster	https://www.carsized.com/en/cars/caterham-seven-1973-roadster/
EU-FERRARI-308-GTSI-TARGA-01	4230	1720	1120	Ferrari 308 GTSi official historical specification	https://www.ferrari.com/en-EN/auto/308-gtsi
EU-FERRARI-308-GTBI-COUPE-01	4230	1720	1120	Ferrari 308 GTBi official historical specification	https://www.ferrari.com/en-EN/auto/308-gtbi
EU-FERRARI-MONDIAL-3-2-CONVERTIBLE-01	4535	1795	1265	Ferrari 3.2 Mondial Cabriolet official historical specification	https://www.ferrari.com/en-EN/auto/3.2-mondial-cabriolet
EU-FERRARI-MONDIAL-3-2-COUPE-01	4535	1795	1235	Ferrari 3.2 Mondial official historical specification	https://www.ferrari.com/en-EN/auto/3.2-mondial
EU-LADA-SAMARA-2113-HATCHBACK-3D-01	4122	1650	1402	Drom Lada 2113 Samara dimensions	https://www.drom.ru/catalog/lada/2113/specs/dimensions/
EU-LADA-SAMARA-2114-HATCHBACK-5D-01	4122	1650	1402	Drom Lada 2114 Samara dimensions	https://www.drom.ru/catalog/lada/2114/specs/dimensions/
EU-LADA-2107-21074-SEDAN-01	4128	1620	1446	UltimateSpecs Lada 2107 1.6	https://www.ultimatespecs.com/car-specs/Lada/666/Lada-2107-16.html
EU-RENAULT-SCENIC-IV-MPV-01	4406	1866	1653	Renault Scénic official user manual dimensions	https://www.user-manual.renault.com/en/content/hcb/technical-specifications/information-about-vehicle/dimensions-metres
EU-RENAULT-GRAND-SCENIC-IV-MPV-01	4634	1866	1655	Renault Grand Scénic official user manual dimensions	https://www.user-manual.renault.com/en/content/hcb/technical-specifications/information-about-vehicle/dimensions-metres
EU-MERCEDES-BENZ-S-CLASS-W222-FACELIFT-SEDAN-SWB-01	5141	1905	1498	Mercedes-Benz UK New S-Class official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2018/01/new-s-class.pdf
EU-MERCEDES-AMG-S63-V222-FACELIFT-SEDAN-LWB-01	5294	1914	1499	Mercedes-Benz UK New S-Class official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2018/01/new-s-class.pdf
EU-MERCEDES-MAYBACH-S560-X222-FACELIFT-SEDAN-01	5462	1905	1498	Automobile-Catalog 2018 Mercedes-Maybach S 560 4MATIC	https://www.automobile-catalog.com/car/2018/2564570/mercedes-maybach_s_560_4matic.html
EU-MERCEDES-AMG-E63-S213-WAGON-01	4993	1907	1460	Mercedes-AMG E-Class official owners manual supplement September 2017	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-qa/pdf/mercedes-amg-e-class-owners-manual-supplement-september-2017-1.pdf
EU-ALPINA-B3-S-F30-SEDAN-01	4632	1811	1431	BMW ALPINA B3 S BITURBO technical data sheet	https://www.7-forum.com/news/2017/alpina/alpina_b3_s_biturbo_technische_daten.pdf
EU-ALPINA-B3-S-F31-WAGON-01	4632	1811	1431	BMW ALPINA B3 S BITURBO technical data sheet	https://www.7-forum.com/news/2017/alpina/alpina_b3_s_biturbo_technische_daten.pdf
EU-ALPINA-B4-S-F32-COUPE-01	4640	1825	1373	Automobile-Catalog 2017 Alpina B4 S Biturbo Coupe	https://www.automobile-catalog.com/car/2017/2681210/alpina_b4_s_biturbo_coupe.html
EU-ALPINA-B4-S-F33-CONVERTIBLE-01	4640	1825	1380	Automobile-Catalog 2017 Alpina B4 S Biturbo Cabrio	https://www.automobile-catalog.com/car/2017/2681240/alpina_b4_s_biturbo_cabrio.html
EU-SMART-FORTWO-III-COUPE-01	2740	1663	1543	smart 453 official owner's manual	https://moba.i.mercedes-benz.com/markets-smart/ece-row/baix/cars/smart-fortwo-453/en_GB/downloads/04_16/BA_smart_453_3_4_2016-1a_alle_Maerkte_1_en_GB.pdf
EU-SMART-FORFOUR-II-HATCHBACK-01	3525	1665	1543	smart forfour official technical data	https://www.forfour.co.uk/documents/brochures/technicaldata.pdf
EU-SMART-FORTWO-III-CONVERTIBLE-01	2740	1663	1543	smart 453 official owner's manual	https://moba.i.mercedes-benz.com/markets-smart/ece-row/baix/cars/smart-fortwo-453/en_GB/downloads/04_16/BA_smart_453_3_4_2016-1a_alle_Maerkte_1_en_GB.pdf
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-9g-tronic-27376
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Hyundai Ireland All-New i30 Tourer official brochure	https://www.hyundai.ie/assets/car/all-new-i30-tourer/files/hyundai-i30-tourer-20pp-brochure-final-min.pdf
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Alfa Romeo Stelvio official technical specification	https://www.media.stellantis.com/be-fr/alfa-romeo/press/alfa-romeo-stelvio
EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	4470	1810	1695	Auto-Data Suzuki Grand Vitara II 5 Door 2.7 V6 4WD	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-2.7-v6-185hp-4wd-45647
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-01	4599	2000	1724	Land Rover Discovery Sport 17MY official brochure; Automobile-Catalog 2018 Discovery Sport Si4 290 AWD	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/discovery-sport/LRGL-DISS00-RTR0311_L550_17MY_MB_EURO_V17_FINAL_tcm295-799848.pdf;https://www.automobile-catalog.com/car/2018/2564795/land-rover_discovery_sport_si4_290_awd.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	4370	1900	1635	Automobile-Catalog 2017 Range Rover Evoque SD4 240 AWD	https://www.automobile-catalog.com/car/2017/2564810/range_rover_evoque_5-door_sd4_240_awd.html
EU-CITROEN-XSARA-I-FACELIFT-VAN-WAGON-01	4369	1705	1420	Auto-Data Citroen Xsara Break N2 Phase II 1.4 i	https://www.auto-data.net/en/citroen-xsara-break-n2-phase-ii-1.4-i-75hp-46541
EU-LADA-GRANTA-I-LIFTBACK-01	4246	1700	1500	Auto-Data Lada Granta I Hatchback	https://www.auto-data.net/en/lada-granta-i-hatchback-generation-4625
EU-CITROEN-XSARA-I-FACELIFT-VAN-HATCHBACK-01	4188	1705	1405	Automobile-Catalog 2000 Citroen Xsara 2.0 HDi 90	https://www.automobile-catalog.com/car/2000/547265/citroen_xsara_2_0_hdi_90_exclusive.html
EU-SUZUKI-VITARA-I-SUV-3D-01	3632	1630	1662	Auto-Data Suzuki Vitara 1.6 i 16V 3 Door	https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-16v-3-dr-97hp-16429
EU-SUZUKI-VITARA-I-SUV-5D-01	4030	1635	1700	Auto-Data Suzuki Vitara 1.6 i 16V 5 Door	https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-16v-5-dr-97hp-16430
EU-JAC-IEV6E-I-HATCHBACK-01	3630	1670	1475	AutoCango 2017 JAC iEV6E 22 kWh specifications	https://www.autocango.com/ar/carspecs-detail/JAC-iEV6E-7E8WW
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Opel Ireland New Insignia official brochure	https://www.readkong.com/page/the-new-insignia2018-models-edition-2-1116078
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1500	Opel Ireland New Insignia official brochure	https://www.readkong.com/page/the-new-insignia2018-models-edition-2-1116078
EU-FIAT-500L-FACELIFT-2017-HATCHBACK-01	4242	1784	1658	Auto-Data Fiat 500L 0.9 TwinAir Turbo Methane	https://www.auto-data.net/en/fiat-500l-facelift-2017-0.9-twinair-85-80hp-turbo-methane-30037
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford Fiesta 2017 official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Fiesta/FordFiesta2017_FiestaDrive_TechSpecs_EU.pdf
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4065	1735	1476	Ford Fiesta 2017 official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Fiesta/FordFiesta2017_FiestaDrive_TechSpecs_EU.pdf
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644	Jeep Compass official brochure	https://www.jeep-id.com/content/dam/cross-regional/asean/jeep/common/brochure/jeep-compass-id.pdf
EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	4955	1880	1496	Jaguar Media Newsroom New XF Sportbrake; Automobile-Catalog 2017 Jaguar XF Sportbrake 20d	https://archive.jaguar.com/news/2017/06/new-jaguar-xf-sportbrake;https://www.automobile-catalog.com/car/2017/2559845/jaguar_xf_sportbrake_20d.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V7-01	5000	2010	2200	L'Argus Iveco Daily 35S60EV7 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV7-1930599.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V9-01	5520	2010	2200	L'Argus Iveco Daily 35S60EV9 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV9-1930600.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V11-01	5520	2010	2610	L'Argus Iveco Daily 35S60EV11 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV11-1930601.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V12-01	5920	2010	2580	L'Argus Iveco Daily 35S60EV12 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV12-1930602.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V13-01	5920	2010	2780	L'Argus Iveco Daily 35S60EV13 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV13-1930603.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V16-01	7090	2010	2580	L'Argus Iveco Daily 35S60EV16 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV16-1930604.html
EU-IVECO-DAILY-VI-ELECTRIC-VAN-V18-01	7090	2010	2780	L'Argus Iveco Daily 35S60EV18 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2B35s%2BFg/III/2018/Fourgon/35S60EV18-1930605.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3000-01	5020	2010	2230	L'Argus Iveco Daily 35S60E Empattement 3000 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3000-1928100.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3450-01	5900	2010	2240	L'Argus Iveco Daily 35S60E Empattement 3450 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3450-1928101.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB3750-01	6510	2010	2220	L'Argus Iveco Daily 35S60E Empattement 3750 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B3750-1928102.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-SRW-WB4100-01	6510	2010	2190	L'Argus Iveco Daily 35S60E Empattement 4100 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35S60E%2BEmpattement%2B4100-1928099.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3450-01	5800	2010	2200	L'Argus Iveco Daily 35C60E Empattement 3450 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B3450-1928104.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB3750-01	6410	2010	2190	L'Argus Iveco Daily 35C60E Empattement 3750 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B3750-1928105.html
EU-IVECO-DAILY-VI-ELECTRIC-CHASSIS-DRW-WB4100-01	6810	2010	2190	L'Argus Iveco Daily 35C60E Empattement 4100 technical sheet	https://www.largus.fr/fiche-technique/Iveco/Daily%2BCcb/III/2019/Ch%C3%A2ssis%2BCabine/35C60E%2BEmpattement%2B4100-1928103.html
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-220d-194hp-9g-tronic-30240
EU-IVECO-DAILY-VI-MINIBUS-WB3520L-01	5950	2052	2784	IVECO Daily Minibus official brochure	https://www.contracteo.be/sites/default/files/entreprise/minibus_daily_en.pdf
EU-IVECO-DAILY-VI-MINIBUS-WB4100-01	7120	2052	2784	IVECO Daily Minibus official brochure	https://www.contracteo.be/sites/default/files/entreprise/minibus_daily_en.pdf
EU-IVECO-DAILY-VI-MINIBUS-WB4100L-01	7515	2174	2905	IVECO Daily Minibus official brochure	https://www.contracteo.be/sites/default/files/entreprise/minibus_daily_en.pdf
EU-PEUGEOT-404-WAGON-01	4582	1625	1490	Automobile-Catalog 1963 Peugeot 404 Break Super Luxe	https://www.automobile-catalog.com/car/1963/2554295/peugeot_404_break_super_luxe.html
EU-LAMBORGHINI-AVENTADOR-S-COUPE-01	4797	2030	1136	Lamborghini Aventador S official history; Automobile-Catalog 2017 Lamborghini Aventador S	https://www.lamborghini.com/en-en/history/aventador-s;https://www.automobile-catalog.com/car/2017/2606675/lamborghini_aventador_s.html
EU-LAMBORGHINI-HURACAN-PERFORMANTE-COUPE-01	4506	1924	1165	Lamborghini Huracán Performante official history; Automobile-Catalog 2017 Huracán Performante	https://www.lamborghini.com/en-en/history/huracan-performante;https://www.automobile-catalog.com/car/2017/2606720/lamborghini_huracan_performante.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Mercedes-Benz E-Class Saloon and Estate official brochure	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-MERCEDES-AMG-GLC-X253-SUV-01	4679	1930	1628	Automobile-Catalog Mercedes-AMG GLC 63 4MATIC+; Automobile-Catalog Mercedes-AMG GLC 63 S 4MATIC+	https://www.automobile-catalog.com/car/2017/2560415/mercedes-amg_glc_63_4matic_plus.html;https://www.automobile-catalog.com/car/2017/2560430/mercedes-amg_glc_63_s_4matic_plus.html
EU-OPEL-GRANDLAND-X-I-SUV-01	4477	1856	1609	Vauxhall Grandland X official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/grandland/price-guides/014_Grandland_X_Spec_PG_19_December_2017-1516896885.pdf
EU-MERCEDES-AMG-GLE43-W166-SUV-01	4816	1999	1760	Mercedes-Benz USA 2017 Mercedes-AMG GLE43 official specifications	https://media.mbusa.com/releases/release-95853e11e010b7b5e744226d7f297469-2017-mercedes-amg-gle43-specifications
EU-CHRYSLER-300C-I-FACELIFT-SEDAN-01	5015	1880	1475	Automobile-Catalog 2008 Chrysler 300C 5.7 V8 Hemi Europe	https://www.automobile-catalog.com/car/2008/524465/chrysler_300c_5_7_v8_hemi.html
EU-MERCEDES-AMG-GLE43-C292-SUV-COUPE-01	4892	2004	1720	Car and Driver 2017 Mercedes-AMG GLE43 Coupe specifications	https://www.caranddriver.com/mercedes-amg/gle43-coupe-4matic-gle63-s-coupe-4matic/specs/2017/mercedes-amg_gle43-coupe-4matic-gle63-s-coupe-4matic_mercedes-amg-gle43-coupe-4matic_2017
EU-FORD-USA-EXPLORER-II-SUV-3D-01	4562	1783	1702	Automobile-Catalog 1998 Ford Explorer Sport 4WD 4.0 SOHC	https://www.automobile-catalog.com/car/1998/889460/ford_explorer_sport_4wd_4_0l_sohc_v-6_automatic.html
EU-FORD-USA-EXPLORER-II-SUV-5D-01	4813	1783	1720	Edmunds 1998 Ford Explorer 4-Door specifications	https://www.edmunds.com/ford/explorer/1998/suv/st-9451/features-specs/
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota Proace official brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-archive/proace/proace-jul-21.pdf
EU-HONDA-CIVIC-X-FK8-TYPE-R-HATCHBACK-01	4557	1877	1434	Honda Civic 2017 Type R press information; Honda Type R official specification	https://www.honda.co.jp/factbook/auto/CIVIC/201707/;https://cdn.honda.co.za/acc/general/cars/civic-type-r/Honda-Type-R-Specifications.pdf
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	BMW UK 6 Series Gran Turismo official technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0271717EN_GB/395434
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1401-1500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1401-1500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1401-1500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1572 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（787 行）

