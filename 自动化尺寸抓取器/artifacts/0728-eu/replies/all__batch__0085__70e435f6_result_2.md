# 任务：all 第 8401-8500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0085__70e435f6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8401-8500 行

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
all 第 8401-8500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330
EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	4260	1664	1330
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318
EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	4250	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	4120	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	4245	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	4258	1630	1290
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	4299	1776	1315
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	4285	1780	1315
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318
EU-AUDI-A8-D4-4H-A8L-SEDAN-4D-PREFL-01	5267	1949	1471
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514
EU-FIAT-TEMPRA-SEDAN-01	4354	1695	1445
EU-FIAT-TEMPRA-WAGON-4X4-01	4472	1695	1540
EU-FIAT-TEMPRA-WAGON-FWD-01	4472	1695	1500
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470
EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	4035	1698	1660
EU-MAZDA-CX-7-ER-SUV-01	4682	1872	1645
EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	3575	1719	1575
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296
EU-MERCEDES-BENZ-SL-W113-CONVERTIBLE-01	4285	1760	1320
EU-MERCEDES-BENZ-SL-W121-CONVERTIBLE-01	4290	1740	1320
EU-MINI-MINI-R53-HATCHBACK-3D-01	3655	1688	1416
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400
EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	3872	1655	1446
EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	3872	1655	1446
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465
EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	3750	1460	1730
EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	3390	1395	1730
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	3370	1395	1870
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-996-CARRERA-COUPE-01	4430	1765	1305
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492
EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	4635	1762	1434
EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	4635	1762	1466
EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	4654	1782	1507
EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	2500	1515	1549
EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	2500	1515	1529
EU-SUBARU-LEGACY-II-BD-SEDAN-01	4595	1695	1405
EU-SUBARU-LEGACY-II-BG-WAGON-01	4670	1695	1490
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-02	4500	1710	1400
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395
EU-TOYOTA-CAMRY-IV-XV20-SEDAN-4D-01	4765	1785	1430
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Arena combi	1.9 D	Bus	Frontantrieb	Diesel	44	60	Mar 1998	Aug 2001	2024-03-01	9320
Opel	Arena combi	2.5 D	Bus	Frontantrieb	Diesel	55	75	Mar 1998	Aug 2001	2024-03-01	9321
Opel	Arena	1.9 D	Kasten	Frontantrieb	Diesel	44	60	Mar 1998	Aug 2001	2024-03-01	9322
Opel	Arena	2.5 D	Kasten	Frontantrieb	Diesel	55	75	Mar 1998	Aug 2001	2024-03-01	9323
Nissan	Vanette cargo	1.6 I	Kasten	Heckantrieb	Benzin	71	97	Sep 1994	May 2001	2024-03-01	9324
Nissan	Vanette cargo	2.3 D	Kasten	Heckantrieb	Diesel	55	75	Sep 1994	May 2002	2024-03-01	9326
Nissan	Vanette cargo	2.3 D	Bus	Heckantrieb	Diesel	55	75	Sep 1994	May 2001	2024-03-01	9327
Nissan	Vanette cargo	2.0 D	Bus	Heckantrieb	Diesel	49	67	Jan 1996	May 2001	2024-03-01	9328
Nissan	Vanette cargo	1.6 I	Bus	Heckantrieb	Benzin	72	98	Jan 1996	May 2001	2024-03-01	9329
Audi	A8 d4	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	245	333	Jun 2010	Jan 2018	2024-03-01	9330
Fiat	Grande punto	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	88	120	Jul 2008	-	2024-03-01	9331
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	150	204	Dec 2010	Mar 2015	2024-03-01	9332
Audi	A7 sportback	2.8 FSI	Schrägheck	Frontantrieb	Benzin	150	204	Feb 2011	Mar 2015	2024-03-01	9333
Jaguar	Xk ii	5.0 Xkr-s	Coupe	Heckantrieb	Benzin	405	550	Jan 2011	Jul 2014	2024-03-01	9334
Audi	A7 sportback	3.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	228	310	Jan 2011	Mar 2015	2024-03-01	9335
Jaguar	Xk ii	5.0 XKR	Coupe	Heckantrieb	Benzin	390	530	Sep 2010	Jul 2014	2024-03-01	9336
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	165	224	Jun 2009	May 2012	2024-03-01	9337
Aston Martin	Virage vantage	6	Coupe	Heckantrieb	Benzin	365	496	Jun 2011	Aug 2012	2024-03-01	9338
Smart	City-	0.6	Coupe	Heckantrieb	Benzin	40	55	Jul 1998	Jan 2004	2024-03-01	9339
Mercedes-benz	Clk	CLK 430	Coupe	Heckantrieb	Benzin	205	279	Jul 1998	Jun 2002	2024-03-01	9340
Mercedes-benz	A-Klasse	A 160 CDI	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1998	Feb 2001	2024-03-01	9341
Mercedes-benz	A-Klasse	A 170 CDI	Schrägheck	Frontantrieb	Diesel	66	90	Jul 1998	Feb 2001	2024-03-01	9342
Daihatsu	Sirion	1.0 I	Schrägheck	Frontantrieb	Benzin	41	56	Apr 1998	Sep 2000	2024-03-01	9343
Aston Martin	Vantage	4.7 V8S	Coupe	Heckantrieb	Benzin	321	437	Jun 2011	Jul 2018	2024-03-01	9344
Fiat	Croma	2500 D	Schrägheck	Frontantrieb	Diesel	55	75	Dec 1985	Dec 1989	2024-03-01	9345
Aston Martin	Vantage	4.7 S	Cabriolet	Heckantrieb	Benzin	321	437	Jan 2011	-	2024-03-01	9346
Aston Martin	Virage volante	6	Cabriolet	Heckantrieb	Benzin	365	496	Jun 2011	Aug 2012	2024-03-01	9347
Aston Martin	One-77	7.3	Coupe	Heckantrieb	Benzin	559	760	Jun 2010	Jun 2012	2024-03-01	9348
Mercedes-benz	Sl	63 AMG	Cabriolet	Heckantrieb	Benzin	395	537	Jan 2012	May 2019	2024-03-01	9349
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	320	435	Jan 2012	Apr 2020	2024-03-01	9351
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	120	163	Feb 2008	Aug 2009	2024-03-01	9352
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	147	200	Mar 2010	Jun 2014	2024-03-01	9359
Lancia	Delta iii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2008	Aug 2014	2024-03-01	9365
Lancia	Musa	1.4	Großraumlimousine	Frontantrieb	Benzin	66	90	Oct 2007	Sep 2012	2024-03-01	9366
Citroën	Jumper i	2.8 D	Bus	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9375
Citroën	Jumper i	2.8 D	Kasten	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9376
Citroën	Jumper i	2.8 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9377
Peugeot	Boxer	2.8 D	Bus	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9378
Saab	9-3	2.0 I	Schrägheck	Frontantrieb	Benzin	96	131	Feb 1998	Sep 2002	2024-03-01	9379
Saab	9-3	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	136	185	Feb 1998	Sep 2002	2024-03-01	9380
Saab	9-3	2.3 I	Schrägheck	Frontantrieb	Benzin	110	150	Feb 1998	Sep 2002	2024-03-01	9381
Saab	9-3	2.2 TID	Schrägheck	Frontantrieb	Diesel	85	115	Feb 1998	Nov 2000	2024-03-01	9382
Alfa Romeo	Gtv	1.8 16V	Coupe	Frontantrieb	Benzin	106	144	May 1998	Oct 2005	2024-03-01	9383
Saab	9-3	2.0 I	Cabriolet	Frontantrieb	Benzin	96	131	Feb 1998	Aug 2003	2024-03-01	9384
Saab	9-3	2.0 Turbo	Cabriolet	Frontantrieb	Benzin	136	185	Feb 1998	Aug 2003	2024-03-01	9385
Saab	9-3	2.3 I	Cabriolet	Frontantrieb	Benzin	110	150	Feb 1998	Aug 2003	2024-03-01	9386
Subaru	Legacy ii	2.5 I 4WD	Stufenheck	Allrad	Benzin	110	150	Jun 1996	Mar 1999	2024-03-01	9387
Subaru	Legacy ii station wagon	2.5 I 4WD	Kombi	Allrad	Benzin	110	150	Jun 1996	Nov 1998	2024-03-01	9388
Mazda	Cx-7	2.2 Mzr-cd AWD	SUV	Allrad	Diesel	120	163	Jan 2012	Mar 2013	2024-03-01	9389
Peugeot	Boxer	2.8 D	Kasten	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9390
Peugeot	Boxer	2.8 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	64	87	Jan 1999	Feb 2002	2024-03-01	9391
VW	Golf iv	1.8	Cabriolet	Frontantrieb	Benzin	55	75	Jun 1998	Jun 2002	2024-03-01	9399
VW	Golf iv	1.8	Cabriolet	Frontantrieb	Benzin	66	90	Jun 1998	Jun 2002	2024-03-01	9400
Fiat	Croma	2500 TDE	Schrägheck	Frontantrieb	Diesel	77	105	Dec 1991	Aug 1996	2024-03-01	9401
Fiat	Tempra	1.6	Kombi	Frontantrieb	Benzin	63	86	Dec 1990	Apr 1993	2024-03-01	9404
Fiat	Tempra	1.6	Stufenheck	Frontantrieb	Benzin	63	86	Mar 1990	Apr 1994	2024-03-01	9405
Opel	Vectra a cc	1.7 D	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1992	Nov 1995	2024-03-01	9406
Skoda	Fabia ii	1.2 12V	Schrägheck	Frontantrieb	Benzin	44	60	Nov 2011	Dec 2014	2024-03-01	9409
Skoda	Fabia ii combi	1.2 12V	Kombi	Frontantrieb	Benzin	44	60	Nov 2011	Dec 2014	2024-03-01	9410
Rover	Streetwise	1.8	Schrägheck	Frontantrieb	Benzin	86	117	Aug 2003	May 2005	2024-03-01	9412
Rover	25	2.0 IDT	Schrägheck	Frontantrieb	Diesel	83	113	Jan 2002	Dec 2004	2024-03-01	9413
Porsche	911	3.4 Carrera	Cabriolet	Heckantrieb	Benzin	221	301	Feb 1998	Sep 2001	2024-03-01	9419
Hyundai	Sonata iv	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	118	160	Jun 1998	Oct 2001	2024-03-01	9420
Volvo	S80 i	2.9	Stufenheck	Frontantrieb	Benzin	150	204	May 1998	Jul 2006	2024-03-01	9421
Volvo	S80 i	T6	Stufenheck	Frontantrieb	Benzin	200	272	May 1998	Dec 2001	2024-03-01	9422
Alfa Romeo	Spider	1.8 16V	Cabriolet	Frontantrieb	Benzin	106	144	May 1998	Apr 2005	2024-03-01	9423
Alfa Romeo	Spider	2.0 T.spark 16V	Cabriolet	Frontantrieb	Benzin	114	155	May 1998	Aug 2000	2024-03-01	9424
Alfa Romeo	Spider	2.0 V6 Turbo	Cabriolet	Frontantrieb	Benzin	148	202	May 1998	Apr 2005	2024-03-01	9425
Bentley	Arnage	4.4 V8	Stufenheck	Heckantrieb	Benzin	260	354	Mar 1998	Dec 2013	2024-03-01	9426
Alfa Romeo	Gtv	2.0 T.spark 16V	Coupe	Frontantrieb	Benzin	114	155	Sep 1997	Mar 2003	2024-03-01	9427
Mazda	Mx-5 ii	1.6 16V	Cabriolet	Heckantrieb	Benzin	81	110	May 1998	Oct 2005	2024-03-01	9429
Mazda	Mx-5 ii	1.8 16V	Cabriolet	Heckantrieb	Benzin	103	140	May 1998	Oct 2005	2024-03-01	9430
Mercedes-benz	Sl	280	Cabriolet	Heckantrieb	Benzin	150	204	May 1998	Oct 2001	2024-03-01	9431
Mercedes-benz	Sl	320	Cabriolet	Heckantrieb	Benzin	165	224	May 1998	Oct 2001	2024-03-01	9432
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	225	306	May 1998	Oct 2001	2024-03-01	9433
Piaggio	Porter	Elektro	Pritsche/Fahrgestell	Heckantrieb	Elektro	18	24	Jan 2011	-	2024-03-01	9436
Piaggio	Porter	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	52	71	Jan 2011	-	2024-03-01	9437
Piaggio	Porter	1.3 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	52	71	Jan 2011	-	2024-03-01	9438
Piaggio	Porter	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	53	72	Jan 2011	-	2024-03-01	9439
Hyundai	I30	1.6	Schrägheck	Frontantrieb	Benzin	88	120	Jan 2012	Dec 2016	2024-03-01	9441
Toyota	Camry	2.5	Stufenheck	Frontantrieb	Benzin	133	181	Sep 2011	Mar 2018	2024-05-01	9445
Hyundai	Ix35	2.0 Crdi	SUV	Frontantrieb	Diesel	135	184	Aug 2009	Dec 2015	2025-02-03	9446
Fiat	Freemont	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	120	163	Aug 2011	Dec 2015	2024-03-01	9447
Piaggio	Porter	1.3 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	53	72	Jan 2011	-	2024-03-01	9448
Piaggio	Porter	1.2 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	47	64	Jan 2011	-	2024-03-01	9449
Piaggio	Porter	Elektro	Kasten	Heckantrieb	Elektro	18	24	Jan 2011	-	2024-03-01	9450
Piaggio	Porter	1.3	Kasten	Heckantrieb	Benzin	52	71	Jan 2011	-	2024-03-01	9451
Piaggio	Porter	1.3 LPG	Kasten	Heckantrieb	Benzin/Autogas (LPG)	52	71	Jan 2011	-	2024-03-01	9452
Piaggio	Porter	1.3	Kasten	Heckantrieb	Benzin	53	72	Jan 2011	-	2024-03-01	9453
Piaggio	Porter	1.3 LPG	Kasten	Heckantrieb	Benzin/Autogas (LPG)	53	72	Jan 2011	-	2024-03-01	9454
Rover	45 i	2.0 IDT	Schrägheck	Frontantrieb	Diesel	83	113	Jan 2004	May 2005	2024-03-01	9455
Rover	45 i	2.0 IDT	Stufenheck	Frontantrieb	Diesel	83	113	Jan 2004	May 2005	2024-03-01	9456
Piaggio	Porter	1.2 D	Kasten	Heckantrieb	Diesel	47	64	Jan 2011	-	2024-03-01	9457
Piaggio	Porter	Elektro	Bus	Heckantrieb	Elektro	18	24	Jan 2011	-	2024-03-01	9458
Lincoln	Ls	4.0 V8 32V	Stufenheck	Heckantrieb	Benzin	180	245	May 1998	-	2024-03-01	9460
Piaggio	Porter	1.3	Bus	Heckantrieb	Benzin	52	71	Jan 2011	-	2024-03-01	9461
Volvo	S80 i	2.4	Stufenheck	Frontantrieb	Benzin	103	140	Jan 1999	Jul 2006	2024-03-01	9462
Volvo	S80 i	2.0 T	Stufenheck	Frontantrieb	Benzin	166	226	Jun 1998	Jul 2006	2024-03-01	9463
Volvo	S80 i	2.5 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Jan 1999	Jul 2006	2024-03-01	9464
Peugeot	206	1.1 I	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1998	Feb 2007	2024-03-01	9465


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 63 条 READY 映射，覆盖 56 个输入 Ktype；其中 23 个尺寸组直接复用跨批次缓存，18 个尺寸组首次创建。
* 新建组集中覆盖 Nissan Vanette Cargo、Audi A8 D4/A7 C7/Q7 4L、Aston Martin Virage/Vantage/One-77、Daihatsu Sirion、VW Tiguan、MINI Clubman、Lancia Delta III 和 Saab 9-3 I。([汽车数据网][1])
* A8 D4 和 Delta III 按改款边界拆分；Saab 9-3 I 按 Hatchback 与 Convertible 分组。([汽车数据网][2])
* Jaguar XK X150 的 2011 年改款长度存在 `4794/4804 mm` 来源冲突，本轮暂不创建尺寸组，避免写入冲突尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：56
* READY 映射：63
* 待处理 Ktype：44
* 已确认尺寸组：41

  * 本轮首次创建：18
  * 复用既有尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9324	9324	Van	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-VAN-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9326	9326	Van	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-VAN-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9327	9327	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9328	9328	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9329	9329	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9330_prefl	9330	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-4D-PREFL-01	HIGH	改款前车身。	READY
9330_facelift	9330	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-4D-FACELIFT-01	HIGH	2013 年改款车身。	READY
9331_3dr	9331	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	三门车身。	READY
9331_5dr	9331	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	五门车身。	READY
9332	9332	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9333	9333	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9335	9335	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9337	9337	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	2009 年改款车身。	READY
9338	9338	Coupe	Virage II		2	EU-ASTON-MARTIN-VIRAGE-II-COUPE-2D-01	HIGH	双门 Coupe。	READY
9339_prefl	9339	Coupe	City-Coupé	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	HIGH	改款前车身。	READY
9339_facelift	9339	Coupe	City-Coupé	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	HIGH	改款后车身。	READY
9340	9340	Coupe	CLK I	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH	C208 双门 Coupe。	READY
9341	9341	Hatchback	A-Class I	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH	W168 五门车身。	READY
9342	9342	Hatchback	A-Class I	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH	W168 五门车身。	READY
9343	9343	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-5D-01	HIGH	M1 五门车身。	READY
9344	9344	Coupe	V8 Vantage		2	EU-ASTON-MARTIN-V8-VANTAGE-COUPE-S-01	HIGH	V8 Vantage S Coupe。	READY
9345	9345	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH	改款前五门车身。	READY
9346	9346	Convertible	V8 Vantage		2	EU-ASTON-MARTIN-V8-VANTAGE-ROADSTER-S-01	HIGH	V8 Vantage S Roadster。	READY
9347	9347	Convertible	Virage II		2	EU-ASTON-MARTIN-VIRAGE-II-VOLANTE-2D-01	HIGH	Virage Volante 双门车身。	READY
9348	9348	Coupe	One-77		2	EU-ASTON-MARTIN-ONE-77-COUPE-2D-01	HIGH	One-77 双门 Coupe。	READY
9352	9352	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	改款前五门 SUV。	READY
9359	9359	Wagon	Clubman I	R55	5	EU-MINI-CLUBMAN-R55-WAGON-5D-FACELIFT-01	HIGH	R55 改款后 Clubman。	READY
9365_prefl	9365	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	HIGH	改款前车身。	READY
9365_facelift	9365	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	HIGH	2011 年改款车身。	READY
9366	9366	MPV	Musa I		5	EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	HIGH	改款后五门 MPV。	READY
9379	9379	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9380	9380	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9381	9381	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9382	9382	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9383_prefl	9383	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前 Coupe。	READY
9383_facelift	9383	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	HIGH	改款后 Coupe。	READY
9384	9384	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9385	9385	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9386	9386	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9387	9387	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH	BD 四门 Sedan。	READY
9388	9388	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH	BG 五门 Wagon。	READY
9389	9389	SUV	CX-7	ER	5	EU-MAZDA-CX-7-ER-SUV-01	HIGH	ER 五门 SUV。	READY
9401	9401	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	改款后五门车身。	READY
9404	9404	Wagon	Tempra		5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	前驱五门 Wagon。	READY
9405	9405	Sedan	Tempra		4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	四门 Sedan。	READY
9406	9406	Hatchback	Vectra A CC		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH	改款后五门 Hatchback。	READY
9423_prefl	9423	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9423_facelift	9423	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	HIGH	改款后 Spider。	READY
9424	9424	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9425_prefl	9425	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9425_facelift	9425	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	HIGH	改款后 Spider。	READY
9427	9427	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前 Coupe。	READY
9431	9431	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9432	9432	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9433	9433	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9441	9441	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD 五门 Hatchback。	READY
9447	9447	MPV	Freemont		5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH	五门 MPV。	READY
9450	9450	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
9451	9451	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
9452	9452	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
9453	9453	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
9454	9454	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
9457	9457	Van	Porter I			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	改款后封闭式 Van。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-VANETTE-CARGO-VAN-01	4500	1695	1980	Auto-Data	https://www.auto-data.net/en/nissan-vanette-cargo-2.3-d-75hp-796
EU-NISSAN-VANETTE-CARGO-MPV-01	4500	1695	1980	Auto-Data	https://www.auto-data.net/en/nissan-vanette-cargo-2.3-d-75hp-796
EU-AUDI-A8-D4-4H-SEDAN-4D-PREFL-01	5137	1949	1460	Auto-Data	https://www.auto-data.net/en/audi-a8-d4-4h-3.0-tfsi-v6-333hp-quattro-tiptronic-53561
EU-AUDI-A8-D4-4H-SEDAN-4D-FACELIFT-01	5137	1949	1460	Auto-Data	https://www.auto-data.net/en/audi-a8-d4-4h-facelift-2013-3.0-tfsi-v6-333hp-quattro-tiptronic-53564
EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	4969	1911	1420	Auto-Data	https://www.auto-data.net/en/audi-a7-sportback-c7-3.0-tdi-v6-204hp-multitronic-19130
EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	5089	1983	1737	Auto-Data	https://www.auto-data.net/en/audi-q7-typ-4l-facelift-2009-3.0-tdi-v6-240hp-quattro-8-tiptronic-54848
EU-ASTON-MARTIN-VIRAGE-II-COUPE-2D-01	4703	1904	1282	Auto-Data	https://www.auto-data.net/en/aston-martin-virage-ii-generation-8015
EU-DAIHATSU-SIRION-M1-HATCHBACK-5D-01	3675	1595	1450	Auto-Data	https://www.auto-data.net/en/daihatsu-sirion-m1-1.0-i-12v-56hp-84
EU-ASTON-MARTIN-V8-VANTAGE-COUPE-S-01	4385	1865	1260	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-facelift-2008-s-4.7-v8-436hp-24274
EU-ASTON-MARTIN-V8-VANTAGE-ROADSTER-S-01	4385	1865	1270	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-facelift-2008-s-4.7-v8-436hp-24188
EU-ASTON-MARTIN-VIRAGE-II-VOLANTE-2D-01	4703	1904	1289	Auto-Data	https://www.auto-data.net/en/aston-martin-virage-ii-volante-generation-8016
EU-ASTON-MARTIN-ONE-77-COUPE-2D-01	4601	1999	1222	Auto-Data	https://www.auto-data.net/en/aston-martin-one-77-generation-4910
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4457	1809	1686	Auto-Data	https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tdi-170hp-4motion-41880
EU-MINI-CLUBMAN-R55-WAGON-5D-FACELIFT-01	3958	1683	1432	Auto-Data	https://www.auto-data.net/en/mini-clubman-r55-cooper-s-1.6-184hp-automatic-21579
EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	4510	1797	1497	Auto-Data	https://www.auto-data.net/en/lancia-delta-iii-844-1.6-multijet-16v-120hp-dpf-5048
EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	4520	1797	1499	Auto-Data	https://www.auto-data.net/en/lancia-delta-iii-844-facelift-2011-1.6-multijet-16v-120hp-45025
EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	4629	1711	1428	Auto-Data	https://www.auto-data.net/en/saab-9-3-model-1275
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1440	Auto-Data	https://www.auto-data.net/en/saab-9-3-convertible-i-generation-2541
```

## 下一步优先处理

1. 集中闭合 Opel Arena/Trafic I 的 Bus、Van、轴距和车顶分支。
2. 利用既有 Jumper/Boxer I 尺寸组，判定 9375–9378、9390–9391 的轴距、车顶及底盘配置。
3. 解决 Jaguar XK X150 改款长度冲突，并处理 Mercedes-Benz SL R231。
4. 批量完成 Fabia II、Rover 25/45、Golf Cabriolet、Porsche 996、Sonata IV、S80 I、MX-5 NB 和 Bentley Arnage。
5. 最后处理 Piaggio Porter Pickup/Bus、Camry XV50、ix35、Lincoln LS 与 Peugeot 206。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/nissan-vanette-cargo-2.3-d-75hp-796?utm_source=chatgpt.com "Nissan Vanette Cargo 2.3 d (75 Hp) /Minivan 1995 - 2002"
[2]: https://www.auto-data.net/en/lancia-delta-iii-844-1.6-multijet-16v-120hp-dpf-5048 "Lancia Delta III (844) 1.6 Multijet 16V (120 Hp) DPF | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增覆盖 21 个 Ktype、30 条 READY 映射；其中 Piaggio Porter 的 Pickup/长底盘分支直接复用已有两个尺寸组，不重复输出尺寸事实。
* Jaguar XK X150 已区分 2009/2011 XKR 外形阶段，并将具有专用前后空气动力套件、不同长度和高度的 XKR-S 独立建组。([汽车数据网][1])
* Mercedes-Benz SL R231、Golf IV Cabriolet、Fabia II Hatchback/Combi 已闭合；Fabia 两种车身的宽度均明确区分车身宽度与含后视镜宽度。([汽车数据网][2])
* Rover Streetwise 1.8 已按官方资料限定为五门；Rover 25 则按资料明确存在的三门、五门物理分支拆分。
* 同步闭合 Porsche 996 Cabriolet、Sonata EF、Bentley Arnage、MX-5 NB 1.6 和 ix35 改款前后尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：77
* READY 映射：93
* PENDING Ktype：23
* 已确认尺寸组：59
* 本轮首次创建尺寸组：16
* 本轮新增复用既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9334	9334	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-S-FACELIFT2011-01	HIGH	XKR-S 专用外部套件车身。	READY
9336_facelift09	9336	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2009-01	HIGH	2009 年改款 XKR 车身。	READY
9336_facelift11	9336	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2011-01	HIGH	2011 年改款 XKR 车身。	READY
9349	9349	Convertible	SL R231	R231	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231 改款前 AMG 车身。	READY
9351	9351	Convertible	SL R231	R231	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231 改款前标准车身。	READY
9399	9399	Convertible	Golf IV Cabriolet	1E7	2	EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	HIGH	1E7 双门敞篷车身。	READY
9400	9400	Convertible	Golf IV Cabriolet	1E7	2	EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	HIGH	1E7 双门敞篷车身。	READY
9409	9409	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-5J-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门 Hatchback。	READY
9410	9410	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-5J-WAGON-5D-FACELIFT-01	HIGH	改款后五门 Wagon。	READY
9412	9412	Hatchback	Streetwise		5	EU-ROVER-STREETWISE-HATCHBACK-5D-01	HIGH	1.8 版本仅对应五门车身。	READY
9413_3dr	9413	Hatchback	Rover 25	RF	3	EU-ROVER-25-RF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
9413_5dr	9413	Hatchback	Rover 25	RF	5	EU-ROVER-25-RF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
9419	9419	Convertible	911 996	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH	996 Carrera 双门敞篷车身。	READY
9420	9420	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH	EF 四门 Sedan。	READY
9426	9426	Sedan	Arnage I		4	EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	HIGH	四门 Sedan。	READY
9429	9429	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-6-01	HIGH	NB 1.6 双门 Roadster。	READY
9436_pickup	9436	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9436_chassis_long	9436	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9437_pickup	9437	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9437_chassis_long	9437	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9438_pickup	9438	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9438_chassis_long	9438	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9439_pickup	9439	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9439_chassis_long	9439	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9446_prefl	9446	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	改款前车身。	READY
9446_facelift	9446	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	2013 年改款车身。	READY
9448_pickup	9448	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9448_chassis_long	9448	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9449_pickup	9449	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9449_chassis_long	9449	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XK-X150-COUPE-XKR-S-FACELIFT2011-01	4804	1892	1312	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2011-r-s-5.0-v8-550hp-automatic-41775
EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2009-01	4794	1892	1322	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2009-r-5.0-v8-510hp-automatic-271
EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2011-01	4794	1892	1322	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2011-r-5.0-v8-510hp-automatic-41773
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	4617	1877	1315	Auto-Data SL 500;Auto-Data AMG SL 63	https://www.auto-data.net/en/mercedes-benz-sl-r231-sl-500-435hp-g-tronic-17417;https://www.auto-data.net/en/mercedes-benz-sl-r231-amg-sl-63-537hp-speedshift-18898
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iv-cabrio-2.0i-116hp-8713
EU-SKODA-FABIA-II-5J-HATCHBACK-5D-FACELIFT-01	4000	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-facelift-2010-1.2-mpi-60hp-20375
EU-SKODA-FABIA-II-5J-WAGON-5D-FACELIFT-01	4247	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-combi-facelift-2010-1.2-mpi-60hp-20326
EU-ROVER-STREETWISE-HATCHBACK-5D-01	3980	1740	1500	Rover Streetwise official brochure	https://xr793.com/wp-content/uploads/2022/12/2005-Rover-Sswise-UK.pdf
EU-ROVER-25-RF-HATCHBACK-3D-01	3990	1688	1419	Auto-Data	https://www.auto-data.net/en/rover-25-rf-2.0-td-113hp-11588
EU-ROVER-25-RF-HATCHBACK-5D-01	3990	1688	1419	Auto-Data	https://www.auto-data.net/en/rover-25-rf-2.0-td-113hp-11588
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-996-carrera-3.4-300hp-6601
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410	Auto-Data	https://www.auto-data.net/en/hyundai-sonata-iv-ef-2.5-v6-160hp-13826
EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	5390	1930	1515	Auto-Data	https://www.auto-data.net/en/bentley-arnage-i-4.4-v8-32v-turbo-354hp-6746
EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-6-01	3975	1680	1225	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.6-i-16v-110hp-11257
EU-HYUNDAI-IX35-LM-SUV-PREFL-01	4410	1820	1660	Auto-Data	https://www.auto-data.net/en/hyundai-ix35-2.0-crdi-184hp-18183
EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	4410	1820	1655	Auto-Data	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-2.0-crdi-184hp-4x4-18564
```

## 下一步优先处理

1. 集中解决 Opel Arena，以及 Citroën Jumper/Peugeot Boxer 的轴距、车顶和 Bus/Van/底盘分支。
2. 闭合 Volvo S80 I 改款边界、Rover 45 Hatchback/Sedan 与 Mazda MX-5 NB 1.8。
3. 完成 Camry XV50、Piaggio Porter Bus、Lincoln LS 和 Peugeot 206 的剩余映射。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2011-r-5.0-v8-510hp-automatic-41773 "Jaguar XK Coupe (X150, facelift 2011) R 5.0 V8 (510 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-sl-r231-sl-500-435hp-g-tronic-17417 "Mercedes-Benz SL (R231) SL 500 (435 Hp) G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/porsche-911-cabriolet-996-carrera-3.4-300hp-6601 "Porsche 911 Cabriolet (996) Carrera 3.4 (300 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Volvo S80 I、Mazda MX-5 NB、Toyota Camry XV50、Rover 45、Lincoln LS 和 Peugeot 206 的剩余映射；S80 与 Camry 按发生尺寸变化的改款边界拆分。([汽车数据网][1])
* Rover 45 的 Hatchback 与 Sedan 分别闭合为五门和四门车身；Peugeot 206 1.1i 按资料明确存在的三门、五门分支拆分。([汽车数据网][2])
* Piaggio Porter 2011 Euro 5 封闭式/玻璃车身得到 `3400×1395×1870 mm`，与既有 `VAN-01` 的 `3370×1395×1870 mm` 不同。未覆盖旧组，已建立 `VAN-02`，并同步修正本批 9450–9454、9457、9458、9461 的关联。
* 当前只剩 Opel Arena 4 个 Ktype，以及 Jumper/Boxer I 的 6 个多轴距、多车顶或底盘 Ktype。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射：111
* PENDING Ktype：10
* 已确认且仍被本批映射引用的尺寸组：69
* 本轮新增映射：18 行
* 本轮修正映射：6 行
* 本轮首次创建尺寸组：11
* 剩余 PENDING：`9320`、`9321`、`9322`、`9323`、`9375`、`9376`、`9377`、`9378`、`9390`、`9391`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9421_prefl	9421	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9421_facelift	9421	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9422	9422	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	T6 对应改款前车身。	READY
9430	9430	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-8-01	HIGH	NB 1.8 双门 Roadster。	READY
9445_prefl	9445	Sedan	Camry VII	XV50	4	EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9445_facelift	9445	Sedan	Camry VII	XV50	4	EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-FACELIFT-01	HIGH	2014 年改款四门车身。	READY
9450	9450	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9451	9451	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9452	9452	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9453	9453	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9454	9454	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9455	9455	Hatchback	Rover 45	RT	5	EU-ROVER-45-RT-HATCHBACK-5D-01	HIGH	RT 五门 Hatchback。	READY
9456	9456	Sedan	Rover 45	RT	4	EU-ROVER-45-RT-SEDAN-4D-01	HIGH	RT 四门 Sedan。	READY
9457	9457	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9458	9458	MPV	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 玻璃客运五门车身。	READY
9460	9460	Sedan	LS I	DEW98	4	EU-LINCOLN-LS-I-DEW98-SEDAN-4D-PREFL-01	HIGH	早期 V8 四门车身。	READY
9461	9461	MPV	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 玻璃客运五门车身。	READY
9462_prefl	9462	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9462_facelift	9462	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9463_prefl	9463	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9463_facelift	9463	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9464	9464	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	2.5 TDI 对应改款前车身。	READY
9465_3dr	9465	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9465_5dr	9465	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	4822	1832	1434	Auto-Data	https://www.auto-data.net/en/volvo-s80-2.9-24v-204hp-9381
EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	4850	1833	1454	Volvo Cars Media	https://www.volvocars.com/intl/media/press-releases/6AB4AB8D8EC721C8/
EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-8-01	3975	1680	1225	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8-i-16v-140hp-11259
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-PREFL-01	4825	1825	1480	Auto-Data	https://www.auto-data.net/en/toyota-camry-vii-xv50-generation-4696
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-FACELIFT-01	4850	1825	1480	Auto-Data	https://www.auto-data.net/en/toyota-camry-vii-xv50-facelift-2014-2.5-181hp-automatic-22779
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	3400	1395	1870	Piaggio Porter Euro 5 official price list;Coches.net JATO vehicle specifications	https://www.piaggio.com/mediaObject/piaggio/GR/Documents/second-hand-vehicles/PDFs/CV_Retail_20120110/original/CV_Retail_20120110.pdf;https://www.coches.net/fichas_tecnicas/piaggio/porter/industriales/5-puertas/12d_furgon_64cv_diesel/45576/700544720110315/
EU-ROVER-45-RT-HATCHBACK-5D-01	4362	1696	1394	Auto-Data	https://www.auto-data.net/en/rover-45-hatchback-rt-2.0-td-113hp-11517
EU-ROVER-45-RT-SEDAN-4D-01	4517	1696	1394	Auto-Data	https://www.auto-data.net/en/rover-45-rt-2.0-td-113hp-11511
EU-LINCOLN-LS-I-DEW98-SEDAN-4D-PREFL-01	4925	1859	1426	Lincoln LS 2000 Owner Guide	https://www.carmanualsonline.info/lincoln-ls-2000-owners-manual/?srch=width
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426	Auto-Data	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426	Auto-Data	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
```

## 下一步优先处理

1. 闭合 `9320–9323` Opel Arena 的 Combi/Van、标准轴距/长轴距和标准顶/高顶分支。
2. 对 `9375–9378、9390–9391` 只做配置边界判定，优先匹配已有 Jumper/Boxer I 的 SWB/MWB/LWB 与低顶/高顶尺寸组。
3. 仅在现有索引没有对应底盘或三维冲突时创建新组；10 个 PENDING 清零后立即进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-s80-2.9-24v-204hp-9381 "Volvo S80 2.9 24V (204 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/rover-45-hatchback-rt-2.0-td-113hp-11517 "Rover 45 Hatchback (RT) 2.0 TD (113 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Opel Arena 4 个 Ktype。THB Combi 与 TF1 Kasten 分别采用 `4542×1905×2026 mm` 和 `4542×1905×2019 mm`；来源明确区分 `1905 mm` 无镜宽与 `2290 mm` 展开后视镜宽。([Opel Team Niedersachsen][1])
* Citroën Jumper Bus、Peugeot Boxer Bus 和 Boxer Van 仅关联跨批次已有尺寸组，没有重复抓取或重复输出尺寸组。
* 第一代 Jumper/Boxer 确有多轴距和多车顶配置，因此按已有缓存中的 SWB、MWB、LWB 和高度分支派生映射。([Transit Center Ford Transit Spare Parts][2])
* 剩余阻塞缩减为 Citroën Jumper Van 以及 Citroën/Peugeot 两个底盘车型 Ktype。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射：128
* PENDING Ktype：3
* 已被当前批次引用的尺寸组：84
* 本轮新增 READY Ktype：7
* 本轮新增 READY 映射：17
* 本轮首次创建尺寸组：2
* 剩余 PENDING：`9376`、`9377`、`9391`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9320	9320	MPV	Arena I	THB	5	EU-OPEL-ARENA-I-THB-MPV-01	HIGH	THB Combi 标准车身。	READY
9321	9321	MPV	Arena I	THB	5	EU-OPEL-ARENA-I-THB-MPV-01	HIGH	THB Combi 标准车身。	READY
9322	9322	Van	Arena I	TF1	4	EU-OPEL-ARENA-I-TF1-VAN-01	HIGH	TF1 Kasten 标准车身。	READY
9323	9323	Van	Arena I	TF1	4	EU-OPEL-ARENA-I-TF1-VAN-01	HIGH	TF1 Kasten 标准车身。	READY
9375_swb_lowroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶物理分支。	READY
9375_mwb_lowroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	中轴低顶物理分支。	READY
9375_mwb_highroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	中轴高顶物理分支。	READY
9378_swb_h2130	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	短轴、车高 2130 mm 分支。	READY
9378_swb_h2150	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	短轴、车高 2150 mm 分支。	READY
9378_mwb_h2130	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	MEDIUM	中轴、车高 2130 mm 分支。	READY
9378_mwb_h2150	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	中轴、车高 2150 mm 分支。	READY
9378_mwb_highroof	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶物理分支。	READY
9390_swb_h2450	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	短轴高顶物理分支。	READY
9390_mwb_h2145	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	中轴低顶物理分支。	READY
9390_mwb_h2465	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	中轴高顶物理分支。	READY
9390_lwb_h2455	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	长轴高顶、车高 2455 mm 分支。	READY
9390_lwb_h2470	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	长轴高顶、车高 2470 mm 分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ARENA-I-THB-MPV-01	4542	1905	2026	Opel-Team Niedersachsen Arena technical data	https://www.opel-team-niedersachsen.de/arena-01.html
EU-OPEL-ARENA-I-TF1-VAN-01	4542	1905	2019	Opel-Team Niedersachsen Arena technical data	https://www.opel-team-niedersachsen.de/arena-01.html
```

## 下一步优先处理

1. 为 `9376` 闭合 Citroën Jumper I 230L Van 的 SWB、MWB、LWB 与低顶/高顶分支，只创建现有索引尚未包含的 Citroën 尺寸组。
2. 为 `9377`、`9391` 确认 230 系列底盘驾驶室的轴距、原厂车架总长、无镜宽度和驾驶室高度。
3. 三个 PENDING 清零后立即输出两张最终完整 TSV、两个指定下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.opel-team-niedersachsen.de/arena-01.html "Arena"
[2]: https://www.transitcenter.uk/citroen-jumper-1-data-specification.php?srsltid=AfmBOopqDOl7twKfG0YOHyf8MYbYAtnqCnggeVY3ed0hNemnUKKV__XA "Citroen Jumper I - Specifications"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* `9376` 已按短轴高顶、中轴低顶/高顶、长轴两种高度拆成 5 条 READY 映射，并首次创建对应 Citroën Jumper I 230L Van 尺寸组。官方 230 系列手册表格确认了各轴距的 `4655/5005/5505 mm` 长度、`1998 mm` 无镜车身宽度及对应高度边界。
* `9377`、`9391` 暂不强行 READY。官方 Pickup 表虽然确认了 `4770/5120/5620 mm` 长度和 `2000 mm` 无镜宽度，但部分 14/MAXI 分支高度仍以 `2090–2093`、`2092–2096`、`2119–2130 mm` 范围表示，尚不能无猜测地分配到具体派生行。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：133
* PENDING Ktype：2
* 已确认尺寸组：89
* 本轮新增 READY 映射：5
* 本轮首次创建尺寸组：5
* 剩余 PENDING：`9377`、`9391`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9376_swb_h2450	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	MEDIUM	短轴高顶物理分支。	READY
9376_mwb_h2145	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	MEDIUM	中轴低顶物理分支。	READY
9376_mwb_h2465	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	MEDIUM	中轴高顶物理分支。	READY
9376_lwb_h2455	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	MEDIUM	长轴高顶、车高 2455 mm 分支。	READY
9376_lwb_h2470	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	MEDIUM	长轴高顶、车高 2470 mm 分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Fiat Ducato 230 official owner handbook;Autogidas Citroën Jumper I specification	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf;https://autogidas.lt/en/auto-katalogas/citroen/jumper/i-31mh-vhhm0-1994-1998-k30288
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
```

## 下一步优先处理

1. 查明 `9377`、`9391` 的 2.8 D 对应 10、14、MAXI 中哪些具体底盘等级和轴距。
2. 为 14 中轴、14 长轴及 MAXI 长轴找到能把高度范围落实为单个整数的直接规格来源。
3. 两个底盘 Ktype 闭合后，立即执行一次机械收尾并输出完整两表、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8401-8500_ktype_dimension_mapping_final.tsv
- all_8401-8500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后两个底盘 Ktype `9377`、`9391` 已按 14 系列 SWB/MWB/LWB 与 MAXI 系列 MWB/LWB 完整拆分，尺寸取官方 230 系列手册中对应平台的最大整车外廓值。
* 已完成机械收尾：映射表严格 10 列、尺寸组表严格 6 列；`id` 与 `DIMENSION_GROUP_ID` 均唯一；所有外键闭合；不存在孤立尺寸组或空缺来源。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：143
* PENDING：0
* DIMENSION_GROUP：99
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9320	9320	MPV	Arena I	THB	5	EU-OPEL-ARENA-I-THB-MPV-01	HIGH	THB Combi 标准车身。	READY
9321	9321	MPV	Arena I	THB	5	EU-OPEL-ARENA-I-THB-MPV-01	HIGH	THB Combi 标准车身。	READY
9322	9322	Van	Arena I	TF1	4	EU-OPEL-ARENA-I-TF1-VAN-01	HIGH	TF1 Kasten 标准车身。	READY
9323	9323	Van	Arena I	TF1	4	EU-OPEL-ARENA-I-TF1-VAN-01	HIGH	TF1 Kasten 标准车身。	READY
9324	9324	Van	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-VAN-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9326	9326	Van	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-VAN-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9327	9327	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9328	9328	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9329	9329	MPV	Vanette Cargo			EU-NISSAN-VANETTE-CARGO-MPV-01	MEDIUM	客货车身按输入 BodyStyle 分组。	READY
9330_prefl	9330	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-4D-PREFL-01	HIGH	改款前车身。	READY
9330_facelift	9330	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-4D-FACELIFT-01	HIGH	2013 年改款车身。	READY
9331_3dr	9331	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	三门车身。	READY
9331_5dr	9331	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	五门车身。	READY
9332	9332	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9333	9333	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9334	9334	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-S-FACELIFT2011-01	HIGH	XKR-S 专用外部套件车身。	READY
9335	9335	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	HIGH	Sportback 五门车身。	READY
9336_facelift09	9336	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2009-01	HIGH	2009 年改款 XKR 车身。	READY
9336_facelift11	9336	Coupe	XK X150	X150	2	EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2011-01	HIGH	2011 年改款 XKR 车身。	READY
9337	9337	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	2009 年改款车身。	READY
9338	9338	Coupe	Virage II		2	EU-ASTON-MARTIN-VIRAGE-II-COUPE-2D-01	HIGH	双门 Coupe。	READY
9339_prefl	9339	Coupe	City-Coupé	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	HIGH	改款前车身。	READY
9339_facelift	9339	Coupe	City-Coupé	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	HIGH	改款后车身。	READY
9340	9340	Coupe	CLK I	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH	C208 双门 Coupe。	READY
9341	9341	Hatchback	A-Class I	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH	W168 五门车身。	READY
9342	9342	Hatchback	A-Class I	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH	W168 五门车身。	READY
9343	9343	Hatchback	Sirion I	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-5D-01	HIGH	M1 五门车身。	READY
9344	9344	Coupe	V8 Vantage		2	EU-ASTON-MARTIN-V8-VANTAGE-COUPE-S-01	HIGH	V8 Vantage S Coupe。	READY
9345	9345	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH	改款前五门车身。	READY
9346	9346	Convertible	V8 Vantage		2	EU-ASTON-MARTIN-V8-VANTAGE-ROADSTER-S-01	HIGH	V8 Vantage S Roadster。	READY
9347	9347	Convertible	Virage II		2	EU-ASTON-MARTIN-VIRAGE-II-VOLANTE-2D-01	HIGH	Virage Volante 双门车身。	READY
9348	9348	Coupe	One-77		2	EU-ASTON-MARTIN-ONE-77-COUPE-2D-01	HIGH	One-77 双门 Coupe。	READY
9349	9349	Convertible	SL R231	R231	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231 改款前 AMG 车身。	READY
9351	9351	Convertible	SL R231	R231	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231 改款前标准车身。	READY
9352	9352	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	改款前五门 SUV。	READY
9359	9359	Wagon	Clubman I	R55	5	EU-MINI-CLUBMAN-R55-WAGON-5D-FACELIFT-01	HIGH	R55 改款后 Clubman。	READY
9365_prefl	9365	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	HIGH	改款前车身。	READY
9365_facelift	9365	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	HIGH	2011 年改款车身。	READY
9366	9366	MPV	Musa I		5	EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	HIGH	改款后五门 MPV。	READY
9375_swb_lowroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶物理分支。	READY
9375_mwb_lowroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	中轴低顶物理分支。	READY
9375_mwb_highroof	9375	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	中轴高顶物理分支。	READY
9376_swb_h2450	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	MEDIUM	短轴高顶物理分支。	READY
9376_mwb_h2145	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	MEDIUM	中轴低顶物理分支。	READY
9376_mwb_h2465	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	MEDIUM	中轴高顶物理分支。	READY
9376_lwb_h2455	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	MEDIUM	长轴高顶、车高 2455 mm 分支。	READY
9376_lwb_h2470	9376	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	MEDIUM	长轴高顶、车高 2470 mm 分支。	READY
9377_14_swb	9377	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	MEDIUM	14 系列短轴平台/底盘分支。	READY
9377_14_mwb	9377	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	MEDIUM	14 系列中轴平台/底盘分支。	READY
9377_14_lwb	9377	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	MEDIUM	14 系列长轴平台/底盘分支。	READY
9377_maxi_mwb	9377	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	MEDIUM	MAXI 系列中轴平台/底盘分支。	READY
9377_maxi_lwb	9377	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	MEDIUM	MAXI 系列长轴平台/底盘分支。	READY
9378_swb_h2130	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	短轴、车高 2130 mm 分支。	READY
9378_swb_h2150	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	短轴、车高 2150 mm 分支。	READY
9378_mwb_h2130	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	MEDIUM	中轴、车高 2130 mm 分支。	READY
9378_mwb_h2150	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	中轴、车高 2150 mm 分支。	READY
9378_mwb_highroof	9378	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶物理分支。	READY
9379	9379	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9380	9380	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9381	9381	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9382	9382	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	HIGH	YS3D 五门车身。	READY
9383_prefl	9383	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前 Coupe。	READY
9383_facelift	9383	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	HIGH	改款后 Coupe。	READY
9384	9384	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9385	9385	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9386	9386	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷车身。	READY
9387	9387	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH	BD 四门 Sedan。	READY
9388	9388	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH	BG 五门 Wagon。	READY
9389	9389	SUV	CX-7	ER	5	EU-MAZDA-CX-7-ER-SUV-01	HIGH	ER 五门 SUV。	READY
9390_swb_h2450	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	MEDIUM	短轴高顶物理分支。	READY
9390_mwb_h2145	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	MEDIUM	中轴低顶物理分支。	READY
9390_mwb_h2465	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	MEDIUM	中轴高顶物理分支。	READY
9390_lwb_h2455	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	MEDIUM	长轴高顶、车高 2455 mm 分支。	READY
9390_lwb_h2470	9390	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	MEDIUM	长轴高顶、车高 2470 mm 分支。	READY
9391_14_swb	9391	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-PICKUP-14-SWB-01	MEDIUM	14 系列短轴平台/底盘分支。	READY
9391_14_mwb	9391	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-PICKUP-14-MWB-01	MEDIUM	14 系列中轴平台/底盘分支。	READY
9391_14_lwb	9391	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-PICKUP-14-LWB-01	MEDIUM	14 系列长轴平台/底盘分支。	READY
9391_maxi_mwb	9391	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-MWB-01	MEDIUM	MAXI 系列中轴平台/底盘分支。	READY
9391_maxi_lwb	9391	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-LWB-01	MEDIUM	MAXI 系列长轴平台/底盘分支。	READY
9399	9399	Convertible	Golf IV Cabriolet	1E7	2	EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	HIGH	1E7 双门敞篷车身。	READY
9400	9400	Convertible	Golf IV Cabriolet	1E7	2	EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	HIGH	1E7 双门敞篷车身。	READY
9401	9401	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	改款后五门车身。	READY
9404	9404	Wagon	Tempra		5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	前驱五门 Wagon。	READY
9405	9405	Sedan	Tempra		4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	四门 Sedan。	READY
9406	9406	Hatchback	Vectra A CC		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH	改款后五门 Hatchback。	READY
9409	9409	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-5J-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门 Hatchback。	READY
9410	9410	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-5J-WAGON-5D-FACELIFT-01	HIGH	改款后五门 Wagon。	READY
9412	9412	Hatchback	Streetwise		5	EU-ROVER-STREETWISE-HATCHBACK-5D-01	HIGH	1.8 版本仅对应五门车身。	READY
9413_3dr	9413	Hatchback	Rover 25	RF	3	EU-ROVER-25-RF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
9413_5dr	9413	Hatchback	Rover 25	RF	5	EU-ROVER-25-RF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
9419	9419	Convertible	911 996	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH	996 Carrera 双门敞篷车身。	READY
9420	9420	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH	EF 四门 Sedan。	READY
9421_prefl	9421	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9421_facelift	9421	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9422	9422	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	T6 对应改款前车身。	READY
9423_prefl	9423	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9423_facelift	9423	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	HIGH	改款后 Spider。	READY
9424	9424	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9425_prefl	9425	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	HIGH	改款前 Spider。	READY
9425_facelift	9425	Convertible	Spider 916	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	HIGH	改款后 Spider。	READY
9426	9426	Sedan	Arnage I		4	EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	HIGH	四门 Sedan。	READY
9427	9427	Coupe	GTV 916	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	改款前 Coupe。	READY
9429	9429	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-6-01	HIGH	NB 1.6 双门 Roadster。	READY
9430	9430	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-8-01	HIGH	NB 1.8 双门 Roadster。	READY
9431	9431	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9432	9432	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9433	9433	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998 年改款标准车身。	READY
9436_pickup	9436	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9436_chassis_long	9436	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9437_pickup	9437	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9437_chassis_long	9437	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9438_pickup	9438	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9438_chassis_long	9438	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9439_pickup	9439	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9439_chassis_long	9439	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9441	9441	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD 五门 Hatchback。	READY
9445_prefl	9445	Sedan	Camry VII	XV50	4	EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9445_facelift	9445	Sedan	Camry VII	XV50	4	EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-FACELIFT-01	HIGH	2014 年改款四门车身。	READY
9446_prefl	9446	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	改款前车身。	READY
9446_facelift	9446	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	2013 年改款车身。	READY
9447	9447	MPV	Freemont		5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH	五门 MPV。	READY
9448_pickup	9448	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9448_chassis_long	9448	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9449_pickup	9449	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货斗分支。	READY
9449_chassis_long	9449	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长底盘分支。	READY
9450	9450	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9451	9451	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9452	9452	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9453	9453	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9454	9454	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9455	9455	Hatchback	Rover 45	RT	5	EU-ROVER-45-RT-HATCHBACK-5D-01	HIGH	RT 五门 Hatchback。	READY
9456	9456	Sedan	Rover 45	RT	4	EU-ROVER-45-RT-SEDAN-4D-01	HIGH	RT 四门 Sedan。	READY
9457	9457	Van	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 封闭式五门车身。	READY
9458	9458	MPV	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 玻璃客运五门车身。	READY
9460	9460	Sedan	LS I	DEW98	4	EU-LINCOLN-LS-I-DEW98-SEDAN-4D-PREFL-01	HIGH	早期 V8 四门车身。	READY
9461	9461	MPV	Porter I	SS	5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	2011 Euro 5 玻璃客运五门车身。	READY
9462_prefl	9462	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9462_facelift	9462	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9463_prefl	9463	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前四门车身。	READY
9463_facelift	9463	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后四门车身。	READY
9464	9464	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	2.5 TDI 对应改款前车身。	READY
9465_3dr	9465	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9465_5dr	9465	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8401-8500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ARENA-I-THB-MPV-01	4542	1905	2026	Opel-Team Niedersachsen Arena technical data	https://www.opel-team-niedersachsen.de/arena-01.html
EU-OPEL-ARENA-I-TF1-VAN-01	4542	1905	2019	Opel-Team Niedersachsen Arena technical data	https://www.opel-team-niedersachsen.de/arena-01.html
EU-NISSAN-VANETTE-CARGO-VAN-01	4500	1695	1980	Auto-Data	https://www.auto-data.net/en/nissan-vanette-cargo-2.3-d-75hp-796
EU-NISSAN-VANETTE-CARGO-MPV-01	4500	1695	1980	Auto-Data	https://www.auto-data.net/en/nissan-vanette-cargo-2.3-d-75hp-796
EU-AUDI-A8-D4-4H-SEDAN-4D-PREFL-01	5137	1949	1460	Auto-Data	https://www.auto-data.net/en/audi-a8-d4-4h-3.0-tfsi-v6-333hp-quattro-tiptronic-53561
EU-AUDI-A8-D4-4H-SEDAN-4D-FACELIFT-01	5137	1949	1460	Auto-Data	https://www.auto-data.net/en/audi-a8-d4-4h-facelift-2013-3.0-tfsi-v6-333hp-quattro-tiptronic-53564
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Auto-Data	https://www.auto-data.net/en/fiat-grande-punto-199-1.6-multijet-120hp-35743
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Auto-Data	https://www.auto-data.net/en/fiat-grande-punto-199-1.6-multijet-120hp-35743
EU-AUDI-A7-C7-SPORTBACK-5D-PREFL-01	4969	1911	1420	Auto-Data	https://www.auto-data.net/en/audi-a7-sportback-c7-3.0-tdi-v6-204hp-multitronic-19130
EU-JAGUAR-XK-X150-COUPE-XKR-S-FACELIFT2011-01	4804	1892	1312	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2011-r-s-5.0-v8-550hp-automatic-41775
EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2009-01	4794	1892	1322	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2009-r-5.0-v8-510hp-automatic-271
EU-JAGUAR-XK-X150-COUPE-XKR-FACELIFT2011-01	4794	1892	1322	Auto-Data	https://www.auto-data.net/en/jaguar-xk-coupe-x150-facelift-2011-r-5.0-v8-510hp-automatic-41773
EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	5089	1983	1737	Auto-Data	https://www.auto-data.net/en/audi-q7-typ-4l-facelift-2009-3.0-tdi-v6-240hp-quattro-8-tiptronic-54848
EU-ASTON-MARTIN-VIRAGE-II-COUPE-2D-01	4703	1904	1282	Auto-Data	https://www.auto-data.net/en/aston-martin-virage-ii-generation-8015
EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	2500	1515	1529	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/3154295/smart_city-coupe_smart_and_pure_45.html
EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	2500	1515	1549	Auto-Data	https://www.auto-data.net/en/smart-fortwo-coupe-c450-0.7-i-61hp-14877
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371	Auto-Data	https://www.auto-data.net/en/mercedes-benz-clk-c208-facelift-1999-clk-200-136hp-23439
EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	3575	1719	1575	Auto-Data	https://www.auto-data.net/en/mercedes-benz-a-class-w168-a-160-cdi-60hp-13207
EU-DAIHATSU-SIRION-M1-HATCHBACK-5D-01	3675	1595	1450	Auto-Data	https://www.auto-data.net/en/daihatsu-sirion-m1-1.0-i-12v-56hp-84
EU-ASTON-MARTIN-V8-VANTAGE-COUPE-S-01	4385	1865	1260	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-facelift-2008-s-4.7-v8-436hp-24274
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/30920/fiat_croma_i_e_.html
EU-ASTON-MARTIN-V8-VANTAGE-ROADSTER-S-01	4385	1865	1270	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-facelift-2008-s-4.7-v8-436hp-24188
EU-ASTON-MARTIN-VIRAGE-II-VOLANTE-2D-01	4703	1904	1289	Auto-Data	https://www.auto-data.net/en/aston-martin-virage-ii-volante-generation-8016
EU-ASTON-MARTIN-ONE-77-COUPE-2D-01	4601	1999	1222	Auto-Data	https://www.auto-data.net/en/aston-martin-one-77-generation-4910
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	4617	1877	1315	Auto-Data SL 500;Auto-Data AMG SL 63	https://www.auto-data.net/en/mercedes-benz-sl-r231-sl-500-435hp-g-tronic-17417;https://www.auto-data.net/en/mercedes-benz-sl-r231-amg-sl-63-537hp-speedshift-18898
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4457	1809	1686	Auto-Data	https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tdi-170hp-4motion-41880
EU-MINI-CLUBMAN-R55-WAGON-5D-FACELIFT-01	3958	1683	1432	Auto-Data	https://www.auto-data.net/en/mini-clubman-r55-cooper-s-1.6-184hp-automatic-21579
EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	4510	1797	1497	Auto-Data	https://www.auto-data.net/en/lancia-delta-iii-844-1.6-multijet-16v-120hp-dpf-5048
EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	4520	1797	1499	Auto-Data	https://www.auto-data.net/en/lancia-delta-iii-844-facelift-2011-1.6-multijet-16v-120hp-45025
EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	4035	1698	1660	Auto-Data	https://www.auto-data.net/en/lancia-musa-facelift-2007-1.4-95hp-31786
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Fiat Ducato 230 official owner handbook;Autogidas Citroën Jumper I specification	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf;https://autogidas.lt/en/auto-katalogas/citroen/jumper/i-31mh-vhhm0-1994-1998-k30288
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	4770	2000	2093	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	5120	2000	2093	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	5620	2000	2096	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	5120	2000	2124	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	5620	2000	2130	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	4629	1711	1428	Auto-Data	https://www.auto-data.net/en/saab-9-3-model-1275
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318	Auto-Data	https://www.auto-data.net/en/alfa-romeo-gtv-916-3.0-v6-218hp-1518
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318	Auto-Data	https://www.auto-data.net/en/alfa-romeo-gtv-916-facelift-2003-generation-7972
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1440	Auto-Data	https://www.auto-data.net/en/saab-9-3-convertible-i-generation-2541
EU-SUBARU-LEGACY-II-BD-SEDAN-01	4595	1695	1405	Auto-Data	https://www.auto-data.net/en/subaru-legacy-ii-bd-bg-2.5-150hp-awd-16182
EU-SUBARU-LEGACY-II-BG-WAGON-01	4670	1695	1490	Auto-Data	https://www.auto-data.net/en/subaru-legacy-ii-station-wagon-bd-bg-2.5-150hp-awd-16186
EU-MAZDA-CX-7-ER-SUV-01	4682	1872	1645	Auto-Data	https://www.auto-data.net/en/mazda-cx-7-facelift-2009-generation-9808
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230-PICKUP-14-SWB-01	4770	2000	2093	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230-PICKUP-14-MWB-01	5120	2000	2093	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230-PICKUP-14-LWB-01	5620	2000	2096	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-MWB-01	5120	2000	2124	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-PEUGEOT-BOXER-I-230-PICKUP-MAXI-LWB-01	5620	2000	2130	Fiat Ducato 230 official owner handbook	https://camperclubskeller.nl/wp-content/uploads/2022/06/Ducato-Instructieboekje-2.8-jtd-2001-2007.pdf
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-iv-cabrio-2.0i-116hp-8713
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/717815/fiat_croma_1_9_tdi.html
EU-FIAT-TEMPRA-WAGON-FWD-01	4472	1695	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/718985/fiat_tempra_s__w__1_6_i_e_.html
EU-FIAT-TEMPRA-SEDAN-01	4354	1695	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/718910/fiat_tempra_1_6_i_e__sx.html
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400	Auto-Data	https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-1.7-d-60hp-2328
EU-SKODA-FABIA-II-5J-HATCHBACK-5D-FACELIFT-01	4000	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-facelift-2010-1.2-mpi-60hp-20375
EU-SKODA-FABIA-II-5J-WAGON-5D-FACELIFT-01	4247	1642	1498	Auto-Data	https://www.auto-data.net/en/skoda-fabia-ii-combi-facelift-2010-1.2-mpi-60hp-20326
EU-ROVER-STREETWISE-HATCHBACK-5D-01	3980	1740	1500	Rover Streetwise official brochure	https://xr793.com/wp-content/uploads/2022/12/2005-Rover-Sswise-UK.pdf
EU-ROVER-25-RF-HATCHBACK-3D-01	3990	1688	1419	Auto-Data	https://www.auto-data.net/en/rover-25-rf-2.0-td-113hp-11588
EU-ROVER-25-RF-HATCHBACK-5D-01	3990	1688	1419	Auto-Data	https://www.auto-data.net/en/rover-25-rf-2.0-td-113hp-11588
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305	Auto-Data	https://www.auto-data.net/en/porsche-911-cabriolet-996-carrera-3.4-300hp-6601
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410	Auto-Data	https://www.auto-data.net/en/hyundai-sonata-iv-ef-2.5-v6-160hp-13826
EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	4822	1832	1434	Auto-Data	https://www.auto-data.net/en/volvo-s80-2.9-24v-204hp-9381
EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	4850	1833	1454	Volvo Cars Media	https://www.volvocars.com/intl/media/press-releases/6AB4AB8D8EC721C8/
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	4285	1780	1315	Auto-Data	https://www.auto-data.net/en/alfa-romeo-spider-916-2.0-twin-spark-150hp-1444
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	4299	1776	1315	Auto-Data	https://www.auto-data.net/en/alfa-romeo-spider-916-facelift-2003-2.0-twin-spark-150hp-42149
EU-BENTLEY-ARNAGE-I-SEDAN-4D-01	5390	1930	1515	Auto-Data	https://www.auto-data.net/en/bentley-arnage-i-4.4-v8-32v-turbo-354hp-6746
EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-6-01	3975	1680	1225	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.6-i-16v-110hp-11257
EU-MAZDA-MX-5-II-NB-CONVERTIBLE-1-8-01	3975	1680	1225	Auto-Data	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8-i-16v-140hp-11259
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300	Auto-Data	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1998-sl-500-v8-306hp-automatic-41293
EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	3390	1395	1730	Piaggio Porter Euro 5 official price list	https://www.piaggio.com/mediaObject/piaggio/GR/Documents/second-hand-vehicles/PDFs/CV_Retail_20120110/original/CV_Retail_20120110.pdf
EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	3750	1460	1730	Piaggio Porter Euro 5 official price list	https://www.piaggio.com/mediaObject/piaggio/GR/Documents/second-hand-vehicles/PDFs/CV_Retail_20120110/original/CV_Retail_20120110.pdf
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470	Auto-Data	https://www.auto-data.net/en/hyundai-i30-ii-1.6-mpi-120hp-18535
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-PREFL-01	4825	1825	1480	Auto-Data	https://www.auto-data.net/en/toyota-camry-vii-xv50-generation-4696
EU-TOYOTA-CAMRY-VII-XV50-SEDAN-4D-FACELIFT-01	4850	1825	1480	Auto-Data	https://www.auto-data.net/en/toyota-camry-vii-xv50-facelift-2014-2.5-181hp-automatic-22779
EU-HYUNDAI-IX35-LM-SUV-PREFL-01	4410	1820	1660	Auto-Data	https://www.auto-data.net/en/hyundai-ix35-2.0-crdi-184hp-18183
EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	4410	1820	1655	Auto-Data	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-2.0-crdi-184hp-4x4-18564
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690	AutoScout24 technical data	https://www.autoscout24.it/auto/dati-tecnici/fiat/freemont/
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	3400	1395	1870	Piaggio Porter Euro 5 official price list;Coches.net JATO vehicle specifications	https://www.piaggio.com/mediaObject/piaggio/GR/Documents/second-hand-vehicles/PDFs/CV_Retail_20120110/original/CV_Retail_20120110.pdf;https://www.coches.net/fichas_tecnicas/piaggio/porter/industriales/5-puertas/12d_furgon_64cv_diesel/45576/700544720110315/
EU-ROVER-45-RT-HATCHBACK-5D-01	4362	1696	1394	Auto-Data	https://www.auto-data.net/en/rover-45-hatchback-rt-2.0-td-113hp-11517
EU-ROVER-45-RT-SEDAN-4D-01	4517	1696	1394	Auto-Data	https://www.auto-data.net/en/rover-45-rt-2.0-td-113hp-11511
EU-LINCOLN-LS-I-DEW98-SEDAN-4D-PREFL-01	4925	1859	1426	Lincoln LS 2000 Owner Guide	https://www.carmanualsonline.info/lincoln-ls-2000-owners-manual/?srch=width
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426	Auto-Data	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426	Auto-Data	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8401-8500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8401-8500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8401-8500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10502 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3255 行）

