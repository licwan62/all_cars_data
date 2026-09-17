# 任务：all 第 3101-3200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0032__67a75159


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3101-3200 行

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
all 第 3101-3200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-BMW-X2-F39-SUV-01	4360	1824	1526
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534
EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	4069	1733	1519
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	4623	1859	1707
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683
EU-KIA-CERATO-I-LD-HATCHBACK-01	4340	1735	1470
EU-KIA-CERATO-I-LD-SEDAN-01	4480	1735	1470
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435
EU-KIA-CERATO-III-YD-KOUP-01	4530	1780	1410
EU-KIA-CERATO-IV-BD-SEDAN-01	4640	1800	1450
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1846
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	4656	1801	1684
EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	4646	1801	1659
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	5333	1920	1890
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	4983	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730
EU-SUBARU-XV-II-SUV-01	4465	1805	1615
EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	3500	1600	1470
EU-SUZUKI-VITARA-I-SUV-3D-01	3632	1630	1662
EU-SUZUKI-VITARA-I-SUV-5D-01	4030	1635	1700
EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	4268	1799	1442
EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	4255	1799	1452
EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	4562	1799	1515
EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	4562	1799	1481
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-V-6R-VAN-3D-PREFL-01	3970	1682	1484
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A4 b9	40 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	140	190	May 2017	-	2024-03-01	133645
Audi	A4 b9	2.0 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	185	252	May 2017	Nov 2019	2024-03-01	133649
Audi	A4 b9	2.0 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	185	252	May 2017	Nov 2019	2024-03-01	133650
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	198	269	Jan 1965	Dec 1968	2024-03-01	133651
Audi	A5	40 Tfsi Mild Hybrid	Coupe	Frontantrieb	Benzin/Elektro	140	190	May 2017	-	2024-03-01	133652
Audi	A5	2.0 Tfsi Mild Hybrid	Coupe	Frontantrieb	Benzin/Elektro	185	252	May 2017	Feb 2020	2024-03-01	133653
Audi	A5	2.0 Tfsi Mild Hybrid Quattro	Coupe	Allrad	Benzin/Elektro	185	252	May 2017	Feb 2020	2024-03-01	133654
Audi	A5	40 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	140	190	May 2017	-	2024-03-01	133655
Audi	A5	2.0 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	185	252	May 2017	Feb 2020	2024-03-01	133656
Audi	A5	2.0 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	185	252	May 2017	Feb 2020	2024-03-01	133657
Audi	A4 b9 avant	40 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	140	190	May 2017	-	2024-07-01	133658
Audi	A4 b9 avant	2.0 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	185	252	May 2017	Oct 2019	2024-03-01	133659
Audi	A4 b9 avant	2.0 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	185	252	May 2017	Jun 2018	2025-06-01	133660
Audi	A5	40 Tfsi Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	140	190	May 2017	-	2024-03-01	133668
Audi	A5	2.0 Tfsi Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	185	252	May 2017	Dec 2019	2024-03-01	133669
Audi	A5	2.0 Tfsi Mild Hybrid Quattro	Cabriolet	Allrad	Benzin/Elektro	185	252	May 2017	Apr 2020	2026-07-01	133670
Nissan	300zx	3.0 Turbo	Coupe	Heckantrieb	Benzin	168	228	Apr 1984	Oct 1990	2024-03-01	133676
Nissan	300zx	3.0 Turbo	Coupe	Heckantrieb	Benzin	149	203	May 1987	Oct 1990	2024-03-01	133677
Audi	Q2	30 Tfsi	SUV	Frontantrieb	Benzin	85	116	Jul 2018	-	2025-06-01	133679
Hyundai	Tucson	2.0 Crdi Hybrid 48V Allrad	SUV	Allrad	Diesel/Elektro	136	185	Oct 2018	Dec 2020	2024-03-01	133680
Nissan	Qashqai ii	1.3 Dig-t	SUV	Frontantrieb	Benzin	103	140	Aug 2018	Sep 2020	2026-06-01	133682
Nissan	Qashqai ii	1.3 Dig-t	SUV	Frontantrieb	Benzin	118	160	Aug 2018	Sep 2020	2026-06-01	133683
Nissan	Qashqai ii	1.5 DCI	SUV	Frontantrieb	Diesel	85	116	Jun 2018	Sep 2020	2026-06-01	133684
Ferrari	488 spider	3.9 Pista	Cabriolet	Heckantrieb	Benzin	530	721	Aug 2018	-	2024-03-01	133685
KIA	Sportage iv	2.0 Crdi Eco-dynamics+ AWD	SUV	Allrad	Diesel/Elektro	136	185	Jun 2018	Sep 2022	2024-03-01	133699
KIA	Optima	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	100	136	Jun 2018	Dec 2019	2025-12-01	133700
KIA	Optima	1.6 T-gdi	Stufenheck	Frontantrieb	Benzin	132	179	Sep 2018	Dec 2019	2024-03-01	133701
Alpina	B4	S Biturbo	Coupe	Heckantrieb	Benzin	332	452	Sep 2018	-	2024-03-01	133709
Alpina	B4	S Biturbo Allrad	Coupe	Allrad	Benzin	332	452	Sep 2018	-	2024-03-01	133710
Alpina	B4	S Biturbo	Cabriolet	Heckantrieb	Benzin	332	452	Sep 2018	-	2024-03-01	133711
Jeep	Cherokee	2.2 CRD	SUV	Frontantrieb	Diesel	110	150	Sep 2018	-	2024-03-01	133714
Land Rover	Discovery v	3.0 Sdv6 4X4	SUV	Allrad	Diesel	225	306	Sep 2018	-	2024-03-01	133716
Suzuki	Vitara	1	SUV	Frontantrieb	Benzin	82	111	Oct 2018	-	2024-03-01	133719
Suzuki	Vitara	1.0 Allgrip	SUV	Allrad	Benzin	82	111	Oct 2018	-	2024-03-01	133720
KIA	Niro i	E-niro	SUV	Frontantrieb	Elektro	150	204	Aug 2018	Aug 2022	2024-03-01	133722
KIA	Niro i	E-niro	SUV	Frontantrieb	Elektro	100	136	Aug 2018	Aug 2022	2024-03-01	133723
Skoda	Superb iii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Feb 2017	Jun 2024	2025-06-01	133731
Skoda	Superb iii	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Mar 2015	Jun 2024	2025-06-01	133732
Porsche	Panamera	4.0 GTS	Schrägheck	Allrad	Benzin	338	460	Jan 2018	Dec 2023	2024-08-01	133739
Porsche	Panamera	4.0 GTS	Kombi	Allrad	Benzin	338	460	Jan 2018	Dec 2023	2024-08-01	133740
VW	Golf vii	1.5 TGI	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	130	Nov 2018	Aug 2020	2024-03-01	133745
BMW	X2	Sdrive 20 D	SUV	Frontantrieb	Diesel	120	163	Nov 2018	Oct 2023	2024-03-01	133766
Citroën	C25	2.5 D	Kasten	Frontantrieb	Diesel	54	73	Feb 1985	Jul 1994	2024-03-01	133767
Citroën	Jumpy iii	1.5 Bluehdi 100	Bus	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	133769
Citroën	Jumpy iii	1.5 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Jun 2018	Apr 2025	2026-01-01	133770
DR	Dr 3	1.5	SUV	Frontantrieb	Benzin	78	106	Feb 2018	Aug 2022	2024-03-01	133779
DR	Dr 3	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	78	106	Feb 2018	Aug 2022	2024-03-01	133780
DR	Dr 3	1.5 CNG	SUV	Frontantrieb	Benzin/Erdgas (CNG)	78	106	Feb 2018	Aug 2022	2024-03-01	133781
Citroën	Jumpy iii	1.5 Bluehdi 100	Kasten	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	133787
Citroën	Jumpy iii	1.5 Bluehdi 120	Kasten	Frontantrieb	Diesel	88	120	Jun 2018	-	2024-03-01	133788
Peugeot	Traveller	1.5 Bluehdi 100	Bus	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	133795
Peugeot	Traveller	1.5 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Jun 2018	Apr 2025	2026-01-01	133796
Peugeot	Expert	1.5 Bluehdi 100	Bus	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	133797
Peugeot	Expert	1.5 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Jun 2018	Apr 2025	2026-01-01	133798
Peugeot	Expert	1.5 Bluehdi 100	Kasten	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2025-12-01	133799
Peugeot	Expert	1.5 Bluehdi 120	Kasten	Frontantrieb	Diesel	88	120	Jun 2018	-	2024-03-01	133800
Mercedes-benz	Cls	CLS 350 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	220	299	Aug 2018	-	2024-03-01	133801
Subaru	Xv	1.6 Bifuel AWD	SUV	Allrad	Benzin/Autogas (LPG)	84	114	Mar 2012	Dec 2017	2025-06-01	133816
Subaru	Xv	2.0 Bifuel AWD	SUV	Allrad	Benzin/Autogas (LPG)	110	150	Mar 2012	Dec 2017	2025-06-01	133817
Subaru	Forester	2.0 Bifuel AWD	SUV	Allrad	Benzin/Autogas (LPG)	110	150	Mar 2013	-	2024-03-01	133818
Nissan	Note	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	65	88	Jan 2006	Aug 2013	2024-03-01	133828
Nissan	Tiida	1.5 DCI	Schrägheck	Frontantrieb	Diesel	76	103	Mar 2007	Jun 2013	2024-03-01	133829
Nissan	Gt-R	V6	Coupe	Allrad	Benzin	353	480	Dec 2008	-	2024-03-01	133830
Nissan	Rogue	2.5	SUV	Frontantrieb	Benzin	124	169	Jan 2010	Nov 2013	2024-03-01	133834
Nissan	Terrano	1.6 4X4	SUV	Allrad	Benzin	84	114	Dec 2015	-	2024-03-01	133848
Suzuki	Splash	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	63	86	Apr 2008	Dec 2014	2024-03-01	133855
Skoda	Kodiaq i	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2018	-	2024-05-01	133857
Skoda	Superb iii	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	200	272	Mar 2015	Jun 2024	2025-06-01	133859
VW	Caddy iv	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2018	Sep 2020	2024-03-01	133860
Skoda	Superb iii	2.0 TSI 4X4	Kombi	Allrad	Benzin	200	272	Mar 2015	Jun 2024	2025-06-01	133863
VW	Touran	1.5 TSI	Großraumlimousine	Frontantrieb	Benzin	110	150	Nov 2018	-	2024-03-01	133864
VW	Polo	1.0 MPI	Schrägheck	Frontantrieb	Benzin	59	80	Sep 2018	-	2024-03-01	133865
Suzuki	Swift iii	1.3 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	68	92	Sep 2008	Dec 2010	2024-03-01	133866
VW	Passat b8	1.5 TSI	Stufenheck	Frontantrieb	Benzin	110	150	Aug 2018	Mar 2024	2025-02-03	133867
VW	Passat b8 variant	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Aug 2018	Mar 2024	2025-02-03	133868
Suzuki	Alto vii	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	50	68	Apr 2009	-	2024-03-01	133870
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	146	199	Aug 2018	Aug 2024	2025-06-01	133871
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	146	199	Aug 2018	Aug 2024	2025-06-01	133872
KIA	Cerato i	1.5 Crdi	Stufenheck	Frontantrieb	Diesel	54	73	Jul 2005	Aug 2006	2024-03-01	133874
Ford USA	Edge	2.0 Ecoblue	SUV	Frontantrieb	Diesel	110	150	Aug 2018	-	2024-03-01	133875
Mercedes-benz	E-Klasse	E 350 D	Coupe	Heckantrieb	Diesel	210	286	Nov 2018	-	2024-03-01	133880
Mercedes-benz	E-Klasse	E 350 D	Cabriolet	Heckantrieb	Diesel	210	286	Nov 2018	-	2024-03-01	133881
Dacia	Logan	1.6 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Aug 2004	Mar 2011	2024-03-01	133882
Mercedes-benz	Sprinter 4-T	411 CDI	Kasten	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	133884
Mercedes-benz	Sprinter 4-T	411 CDI RWD	Kasten	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	133886
Dacia	Logan	1.2 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	53	72	Feb 2013	-	2024-03-01	133887
Mercedes-benz	Sprinter 4-T	414 CDI	Kasten	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	133888
KIA	Cerato i	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	54	73	Jul 2005	Aug 2006	2024-03-01	133889
KIA	Cee'd	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	91	124	Jun 2007	Dec 2011	2024-03-01	133892
KIA	Cee'd	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jan 2009	Dec 2010	2024-03-01	133893
KIA	Cee'd	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jan 2009	Dec 2010	2024-03-01	133894
Dacia	Sandero	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Jun 2008	Dec 2012	2024-03-01	133896
Dacia	Logan	1.6 LPG	Kasten/Kombi	Frontantrieb	Benzin/Autogas (LPG)	62	84	May 2010	Dec 2012	2024-03-01	133899
KIA	Cee'd	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Jun 2011	Apr 2012	2024-03-01	133900
KIA	Cee'd	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	64	87	Jun 2011	Apr 2012	2024-03-01	133901
KIA	Picanto i	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	45	61	Jan 2009	Apr 2011	2024-03-01	133904
KIA	Picanto i	1.1 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	48	65	Jan 2009	Apr 2011	2024-03-01	133906
KIA	Pro cee'd	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	85	116	Feb 2008	Sep 2012	2024-03-01	133907
Lada	Vesta	1.6 CNG	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	78	106	Aug 2017	-	2024-03-01	133913
Mercedes-benz	Gle	GLE 450 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	270	367	Oct 2018	-	2024-03-01	133935


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 32 个既有尺寸组映射，并首次创建 4 个尺寸组。
* 新闭合车型包括 Nissan Qashqai II facelift 前驱版、Ferrari 488 Pista Spider，以及 Alpina B4 S Coupé/Cabriolet。Qashqai 官方资料确认前驱标准车高三维为 4394×1806×1590 mm；Ferrari 官方资料确认 488 Pista Spider 为 4605×1975×1206 mm；Alpina 技术资料分别确认 Coupé 高 1373 mm、Cabriolet 高 1380 mm。
* Audi、Hyundai、KIA、Jeep、Land Rover、BMW、Mercedes-Benz、VW、Suzuki、Dacia 等已确认车型直接复用既有尺寸组，未重复抓取三维或来源。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：36
* 尚待处理 Ktype：64
* READY 映射当前引用尺寸组：24
* 本轮首次创建尺寸组：4
* 本批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133645	133645	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133649	133649	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133650	133650	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133652	133652	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
133653	133653	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
133654	133654	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
133655	133655	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
133656	133656	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
133657	133657	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
133658	133658	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133659	133659	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133660	133660	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133679	133679	SUV	Q2 GA	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
133680	133680	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133682	133682	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133683	133683	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133684	133684	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133685	133685	Convertible	488 Pista Spider		2	EU-FERRARI-488-PISTA-SPIDER-CONVERTIBLE-01	HIGH		READY
133699	133699	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
133700	133700	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
133701	133701	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
133709	133709	Coupe	B4 F32 facelift	F32	2	EU-ALPINA-B4-F32-COUPE-FACELIFT-01	HIGH		READY
133710	133710	Coupe	B4 F32 facelift	F32	2	EU-ALPINA-B4-F32-COUPE-FACELIFT-01	HIGH		READY
133711	133711	Convertible	B4 F33 facelift	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-FACELIFT-01	HIGH		READY
133714	133714	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	HIGH	前驱标准车高。	READY
133716	133716	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
133745	133745	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-HATCHBACK-TGI-01	HIGH		READY
133766	133766	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133801	133801	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH		READY
133865	133865	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH		READY
133870	133870	Hatchback	Alto VII	GF	5	EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	HIGH		READY
133874	133874	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-01	HIGH		READY
133880	133880	Coupe	E-Class V	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
133881	133881	Convertible	E-Class V	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH		READY
133889	133889	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-01	HIGH		READY
133896	133896	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Nissan Qashqai MY18 official brochure (11/2019)	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/QASHQAI_Brochure_November_2019.pdf
EU-FERRARI-488-PISTA-SPIDER-CONVERTIBLE-01	4605	1975	1206	Ferrari 488 Pista Spider official press kit	https://cdn.ferrari.com/cms/network/media/pdf/cs_ferrari_488_pista_spider_gbr.pdf
EU-ALPINA-B4-F32-COUPE-FACELIFT-01	4640	1825	1373	BMW ALPINA B4 S BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-F33-CONVERTIBLE-FACELIFT-01	4640	1825	1380	BMW ALPINA B4 S BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
```

## 下一步优先处理

1. 集中拆分 Jumpy、Expert、Traveller 的 Compact/Standard/Long、车顶高度及 facelift 分支。
2. 闭合 Audi A5 Cabriolet、Jaguar E-Type、Nissan 300ZX、KIA e-Niro、Skoda Superb 与 Porsche Panamera GTS。
3. 最后处理 C25、Sprinter、T6 等多轴距、多车顶复杂商用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 9 个 Ktype；修正 2 个已闭合 Audi A5 Ktype。原 `id=133652`、`id=133655` 基础行撤销，分别改为 `prefl` 与 `facelift` 派生行。
* Audi 官方资料确认 A5 改款前后外廓发生变化，因此 133652、133655、133668 按改款边界拆分；133669、133670 保持改款前外廓。
* 首次闭合 Kia e-Niro、Subaru XV I、Subaru Forester IV 尺寸组；Nissan Rogue 直接复用既有改款前、改款后尺寸组。([起亚新闻官网][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：45
* READY 映射行：49
* PENDING Ktype：55
* 当前引用尺寸组：33
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133652_prefl	133652	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	改款前外廓。	READY
133652_facelift	133652	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
133655_prefl	133655	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	改款前外廓。	READY
133655_facelift	133655	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133668_prefl	133668	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133668_facelift	133668	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	改款后外廓。	READY
133669	133669	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133670	133670	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133722	133722	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	HIGH		READY
133723	133723	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	HIGH		READY
133816	133816	SUV	XV I	GP3	5	EU-SUBARU-XV-I-GP-SUV-01	HIGH		READY
133817	133817	SUV	XV I	GP7	5	EU-SUBARU-XV-I-GP-SUV-01	HIGH		READY
133818	133818	SUV	Forester IV	SJ5	5	EU-SUBARU-FORESTER-IV-SJ-SUV-01	HIGH		READY
133834_prefl	133834	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	HIGH	改款前外廓。	READY
133834_facelift	133834	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371	Audi A5/S5 Coupé & Cabriolet official data information 2017	https://audi-press.jp/presskits/b7rqqm00000034lo-att/2017_Audi_A5_S5.pdf
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	4375	1805	1560	Kia e-Niro 2018 official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/eNiro_PETD/Kia%20e-Niro%20-%202018%20PETD%20-%20December%202018.doc
EU-SUBARU-XV-I-GP-SUV-01	4450	1780	1570	Subaru Deutschland XV MY2012 official technical brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/XV/XV_MJ2012.pdf
EU-SUBARU-FORESTER-IV-SJ-SUV-01	4595	1795	1735	Subaru Deutschland Forester MY2013 official technical brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/Forester/Forester_MJ2013_PTA.pdf
```

## 下一步优先处理

1. 闭合 Jaguar E-Type、Nissan 300ZX、Note、Tiida、GT-R、Terrano 等乘用车尺寸组。
2. 批量处理 Skoda Superb III、Porsche Panamera GTS、VW Passat B8 的车身及改款分支。
3. 集中拆分 Jumpy、Expert、Traveller、Caddy、T6、Sprinter 的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://press.kia.com/content/dam/kiapress/EU/Press-Kits/eNiro_PETD/Kia%20e-Niro%20-%202018%20PETD%20-%20December%202018.doc?utm_source=chatgpt.com "Kia e-Niro - 2018 PETD - December ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新闭合 5 个 Ktype，首次创建 4 个尺寸组。
* Suzuki Vitara 两个驱动版本复用同一改款后外廓；VW Touran、Ford Edge 改款版和 Lada Vesta Sedan 分别完成首次建组。宽度均采用不含后视镜口径。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：50
* READY 映射行：54
* PENDING Ktype：50
* 当前引用尺寸组：37
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133719	133719	SUV	Vitara IV facelift	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133720	133720	SUV	Vitara IV facelift	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133864	133864	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH		READY
133875	133875	SUV	Edge II facelift		5	EU-FORD-EDGE-II-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133913	133913	Sedan	Vesta I		4	EU-LADA-VESTA-I-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	4175	1775	1610	Suzuki Vitara 2019 official distributor brochure	https://i.i-sgcm.com/new_cars/cars/11721/brochures/brochure_20190221114722.pdf
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659	Volkswagen UK Touran official brochure June 2017	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touran/touran-nf/vw-touran-nf-brochure-june-2017.pdf
EU-FORD-EDGE-II-SUV-FACELIFT-01	4834	1928	1732	Ford UK Edge 2019 official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-edge.pdf
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497	LADA Vesta sedan official specifications	https://lada-swiss.ch/cars/vesta/sedan/tth.html
```

## 下一步优先处理

1. 闭合 Skoda Superb III Liftback/Wagon 的改款前后分支。
2. 处理 Porsche Panamera GTS、Nissan Tiida、Note、300ZX 等乘用车尺寸组。
3. 集中拆分 Jumpy、Expert、Traveller、T6 和 Sprinter 的轴距、车顶及车身形式。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新闭合 6 个 Ktype，共新增 10 条派生映射。
* Skoda Superb III 的 Liftback 与 Combi 均确认改款前后长度发生变化，4 个跨改款 Ktype 已分别拆分为 `prefl`、`facelift` 分支。官方规格分别确认改款前 Liftback 为 4861×1864×1468 mm、Combi 为 4856×1864×1477 mm；改款后分别为 4869×1864×1469 mm、4862×1864×1477 mm。
* Porsche 官方欧洲车型资料确认 Panamera GTS 与 Panamera GTS Sport Turismo 分别为 5053×1937×1417 mm、5053×1937×1422 mm，宽度均为不含后视镜口径。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：56
* READY 映射行：64
* PENDING Ktype：44
* 当前引用尺寸组：43
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133731_prefl	133731	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133731_facelift	133731	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133732_prefl	133732	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133732_facelift	133732	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
133739	133739	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	HIGH	GTS外部套件外廓。	READY
133740	133740	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	HIGH	GTS Sport Turismo外廓。	READY
133859_prefl	133859	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133859_facelift	133859	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133863_prefl	133863	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133863_facelift	133863	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	4861	1864	1468	ŠKODA Superb official technical specifications 2018	https://cdn.skoda-storyboard.com/2018/02/TD-SUPERB_en.pdf
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469	ŠKODA Superb official technical specifications 2019	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	4856	1864	1477	ŠKODA Superb Combi official technical specifications 2018	https://cdn.skoda-storyboard.com/2016/05/TD-SUPERB-COMBI-en-1.pdf
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477	ŠKODA Superb Combi official technical specifications 2019	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417	Porsche Panamera GTS official EU fact sheet	https://newsroom.porsche.com/dam/jcr%3A1db5ef7e-115f-47d2-8540-305be8e1d9ea/S18_2880.pdf
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422	Porsche Panamera GTS Sport Turismo official EU fact sheet	https://newsroom.porsche.com/dam/jcr%3A3dc7b94b-bb34-4062-ac60-1027bfed763d/S18_2882.pdf
```

## 下一步优先处理

1. 批量闭合 Peugeot Traveller 的 Compact、Standard、Long 及 facelift 分支，优先复用现有尺寸组。
2. 处理 Nissan Note、Tiida、Terrano，以及 Suzuki Splash、Swift 等单车身乘用车。
3. 随后集中拆分 Jumpy、Expert、Caddy、T6、C25 和 Sprinter 的轴距、车顶与车身形式。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 新闭合 4 个 Ktype，新增 6 条映射。
* Nissan GT-R 133830 已限定为早期 353 kW／480 PS 的 R35 外廓，尺寸为 4655×1895×1370 mm。([日产汽车全球网站][1])
* Nissan Terrano 133848 已匹配 1.6 84 kW、4WD 的 D10；官方资料同时确认车身宽 1822 mm、不含后视镜，外部尺寸为 4315×1822×1695 mm。
* VW Passat B8 Sedan 与 Variant 的 1.5 TSI Ktype 均跨越 2019 年改款边界，已拆分为 `prefl`、`facelift`。改款前 Sedan/Variant 分别为 4767×1832×1456 mm、4767×1832×1477 mm；改款后分别为 4775×1832×1483 mm、4773×1832×1516 mm。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：60
* READY 映射行：70
* PENDING Ktype：40
* 当前引用尺寸组：48
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133830	133830	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	353 kW早期R35外廓。	READY
133848	133848	SUV	Terrano III	D10	5	EU-NISSAN-TERRANO-III-D10-SUV-01	HIGH		READY
133867_prefl	133867	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
133867_facelift	133867	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
133868_prefl	133868	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133868_facelift	133868	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-GT-R-R35-COUPE-PREFL-01	4655	1895	1370	Nissan Heritage Collection NISSAN GT-R R35 official specifications	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/418_nissan_gt-r.html
EU-NISSAN-TERRANO-III-D10-SUV-01	4315	1822	1695	Nissan Terrano official brochure	https://www.nissan-cdn.net/content/dam/Nissan/kz/brochures/nissan-terrano-brochure.pdf
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483	Volkswagen UK New Passat official brochure 2019	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-ix/new-passat-estate-brochure.pdf
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477	Volkswagen UK Passat and Passat Estate official brochure 2016	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516	Volkswagen UK New Passat official brochure 2019	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-ix/new-passat-estate-brochure.pdf
```

## 下一步优先处理

1. 直接复用现有 Traveller Compact、Standard、Long 及 facelift 尺寸组，闭合 133795、133796 的有效长度分支。
2. 闭合 Nissan Note E11、Tiida C11、300ZX Z31，并处理可能存在的改款尺寸差异。
3. 随后集中处理 Citroën Jumpy、Peugeot Expert、VW T6、C25 与 Sprinter 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/418_nissan_gt-r.html "Nissan | Heritage Collection | NISSAN GT-R"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 DR 3 的汽油、LPG、CNG 三个 Ktype；燃料形式不改变车身外廓，统一关联首次创建的 DR 3 尺寸组。DR 官方规格给出的外部尺寸为 4200×1760×1570 mm。([DR Automobiles][1])
* 闭合 Škoda Kodiaq 133857。该 Ktype 跨越第一代 2021 年改款边界，拆分为改款前、改款后两条映射；官方技术资料显示两者长度和宽度相同，标准车高由 1655 mm 变为 1661 mm。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射行：75
* PENDING Ktype：36
* 当前引用尺寸组：51
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133779	133779	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133780	133780	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133781	133781	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133857_prefl	133857	SUV	Kodiaq I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH	改款前外廓。	READY
133857_facelift	133857	SUV	Kodiaq I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DR-DR3-I-SUV-01	4200	1760	1570	DR Automobiles DR 3 official specifications	https://drautomobiles.com/dr-3/
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655	ŠKODA KODIAQ official technical specifications 2018	https://cdn.skoda-storyboard.com/2018/02/TD-KODIAQ_en.pdf
EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	4697	1882	1661	ŠKODA KODIAQ official technical specifications 2021	https://cdn.skoda-storyboard.com/2021/06/TD_KODIAQ_en.pdf
```

## 下一步优先处理

1. 闭合 Nissan Note E11、Tiida C11、300ZX Z31 及 Suzuki Splash、Swift 等单一乘用车外廓。
2. 处理 Dacia Logan Sedan、MCV、Van 和 Kia Cee'd／Pro cee'd／Picanto 的共享车身组。
3. 最后集中拆分 Jumpy、Expert、Traveller、C25、T6、Caddy 与 Sprinter 的长度、车顶和客货版本。

推进信号：CONTINUE

[1]: https://drautomobiles.com/dr-3/ "DR 3 - DR Automobiles"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 新闭合 Ktype `133935`，首次创建 Mercedes-Benz GLE V167 尺寸组。
* Mercedes-Benz 官方资料将该版本明确为 270 kW／367 PS 的 GLE 450 4MATIC，并分别列出车身宽度 1947 mm、含外后视镜宽度 2157 mm，因此 `WidthMM=1947` 满足不含后视镜口径；整车长宽高为 4924×1947×1772 mm。([Mercedes-Benz Österreich][1])
* Nissan、Suzuki、第一代 Kia Cee’d 等候选车型仍存在改款、门数或车身分支边界，本轮未创建猜测性映射。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* READY 映射行：76
* PENDING Ktype：35
* 已确认并引用尺寸组：52
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133935	133935	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Mercedes-Benz Österreich Der neue Mercedes-Benz GLE official press information	https://media.mercedes-benz.at/news-der-neue-mercedes-benz-gle?id=75942&imageid=241349&l=deutsch&menueid=10014
```

## 下一步优先处理

1. 闭合 Dacia Logan／Logan MCV 与 VW Caddy IV 的改款、SWB／LWB分支。
2. 集中处理 Nissan Note、Tiida、300ZX，以及 Suzuki Splash、Swift 的改款和车身边界。
3. 随后处理 Kia Cee’d／Pro cee’d／Picanto，再进入 Jumpy、Expert、Traveller、T6、C25 与 Sprinter 商用车分支。

推进信号：CONTINUE

[1]: https://media.mercedes-benz.at/news-der-neue-mercedes-benz-gle?id=75942&imageid=241349&l=deutsch&menueid=10014 "Der neue Mercedes-Benz GLE - Mercedes-Benz Österreich"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Peugeot Traveller Ktype `133795`、`133796`。
* 两个 Ktype 均按缓存中的改款前 `Compact / Standard / Long` 和改款后 `Standard / Long` 拆分。
* 本轮全部复用既有尺寸组，未重新抓取三维或来源，未创建新尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* READY 映射行：86
* PENDING Ktype：33
* 已确认并引用尺寸组：57
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133795_compact	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	改款前Compact外廓。	READY
133795_standard	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	改款前Standard外廓。	READY
133795_long	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	改款前Long外廓。	READY
133795_standard_facelift	133795	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	HIGH	改款后Standard外廓。	READY
133795_long_facelift	133795	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	HIGH	改款后Long外廓。	READY
133796_compact	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	改款前Compact外廓。	READY
133796_standard	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	改款前Standard外廓。	READY
133796_long	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	改款前Long外廓。	READY
133796_standard_facelift	133796	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	HIGH	改款后Standard外廓。	READY
133796_long_facelift	133796	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	HIGH	改款后Long外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量闭合 Citroën Jumpy III Bus／Van 和 Peugeot Expert Bus／Van 的 Compact、Standard、Long、车顶及改款分支。
2. 处理 Nissan Note E11、Tiida C11、300ZX Z31 的改款或车身边界。
3. 随后处理 Dacia Logan、Kia Cee’d／Pro cee’d／Picanto，以及 VW Caddy IV、T6 和 Mercedes-Benz Sprinter 多尺寸分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 新闭合 7 个 Ktype，新增 12 条映射。
* Suzuki Splash 按 2012 年改款边界拆分，改款前后尺寸均为 `3715×1680×1590 mm`。([汽车数据][1])
* Suzuki Swift 1.3 LPG 覆盖三门、五门车身，按门数拆分；两种外廓尺寸均为 `3695×1690×1500 mm`。([汽车数据][2])
* Kia Cee'd 第一代 Hatchback 与 Wagon 分别完成改款前后分组；Hatchback 为 `4235×1790×1480 mm`，Wagon 改款前为 `4470×1790×1490 mm`、改款后为 `4470×1790×1525 mm`。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* READY 映射行：98
* PENDING Ktype：26
* 已确认并引用尺寸组：65
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133855_prefl	133855	Hatchback	Splash I		5	EU-SUZUKI-SPLASH-I-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133855_facelift	133855	Hatchback	Splash I facelift		5	EU-SUZUKI-SPLASH-I-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133866_3dr	133866	Hatchback	Swift III		3	EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
133866_5dr	133866	Hatchback	Swift III		5	EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
133892_prefl	133892	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133892_facelift	133892	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133893_prefl	133893	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133893_facelift	133893	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133894_prefl	133894	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-ED-WAGON-PREFL-01	HIGH	改款前旅行车外廓。	READY
133894_facelift	133894	Wagon	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
133900	133900	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH		READY
133901	133901	Wagon	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SPLASH-I-HATCHBACK-PREFL-01	3715	1680	1590	Auto-Data Suzuki Splash 1.2i specifications	https://www.auto-data.net/en/suzuki-splash-1.2i-86hp-16489
EU-SUZUKI-SPLASH-I-HATCHBACK-FACELIFT-01	3715	1680	1590	Auto-Data Suzuki Splash facelift 2012 specifications	https://www.auto-data.net/en/suzuki-splash-facelift-2012-generation-4515
EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	3695	1690	1500	Auto-Data Suzuki Swift 1.3i specifications	https://www.auto-data.net/en/suzuki-swift-iv-1.3-i-16v-92hp-16523
EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	3695	1690	1500	Auto-Data Suzuki Swift 1.3i specifications	https://www.auto-data.net/en/suzuki-swift-iv-1.3-i-16v-92hp-16523
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480	Auto-Data Kia Cee'd I specifications	https://www.auto-data.net/en/kia-ceed-i-1.6-cvvt-122hp-42278
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480	Auto-Data Kia Cee'd I facelift specifications	https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.4-16v-90hp-17062
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I specifications	https://www.auto-data.net/en/kia-ceed-sw-i-1.4-cvvt-109hp-42437
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift specifications	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.4-16v-90hp-17071
```

## 下一步优先处理

1. 闭合 Kia Pro cee'd、Picanto I facelift，以及 Nissan Note E11、Tiida C11。
2. 处理 Dacia Logan Sedan、MCV、Van 和 VW Caddy IV。
3. 最后集中拆分 Citroën Jumpy、Peugeot Expert、VW T6、Citroën C25 与 Mercedes-Benz Sprinter 的长度和车顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/suzuki-splash-1.2i-86hp-16489 "Suzuki Splash 1.2i (86 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/suzuki-swift-iv-1.3-i-16v-92hp-16523 "Suzuki Swift IV 1.3 i 16V (92 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/kia-ceed-i-1.6-cvvt-122hp-42278?utm_source=chatgpt.com "Kia Cee'd I 1.6 CVVT (122 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 新闭合 6 个 Ktype，新增 9 条映射和 9 个尺寸组。
* Nissan Note E11 按改款前后拆分，两者三维均为 `4083×1690×1550 mm`；Tiida C11 欧洲版 1.5 dCi 确认为五门 Hatchback，三维为 `4302×1695×1533 mm`，宽度不含后视镜。([汽车数据][1])
* Dacia Logan I Sedan 按 2008 年改款拆分为 `4247×1740×1534 mm` 和 `4288×1740×1534 mm`；Logan II MCV 为 `4492×1733×1550 mm`，资料同时单列含镜宽度 1994 mm，因此落盘宽度采用不含后视镜的 1733 mm。([汽车数据][2])
* Kia Picanto I facelift 1.0 和 Pro cee’d I 已闭合；Pro cee’d 因 2011 年外观改款拆分，改款前后三维均为 `4250×1790×1450 mm`。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：80
* READY 映射行：107
* PENDING Ktype：20
* 已确认并引用尺寸组：74
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133828_prefl	133828	MPV	Note I	E11	5	EU-NISSAN-NOTE-I-E11-MPV-PREFL-01	HIGH	改款前外廓。	READY
133828_facelift	133828	MPV	Note I facelift	E11	5	EU-NISSAN-NOTE-I-E11-MPV-FACELIFT-01	HIGH	改款后外廓。	READY
133829	133829	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-I-C11-HATCHBACK-01	HIGH		READY
133882_prefl	133882	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
133882_facelift	133882	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
133887	133887	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
133904	133904	Hatchback	Picanto I facelift	SA	5	EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	HIGH		READY
133907_prefl	133907	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前三门外廓。	READY
133907_facelift	133907	Hatchback	Pro cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后三门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NOTE-I-E11-MPV-PREFL-01	4083	1690	1550	Auto-Data Nissan Note I E11 1.4 i 16V specifications	https://www.auto-data.net/en/nissan-note-i-e11-1.4-i-16v-88hp-842
EU-NISSAN-NOTE-I-E11-MPV-FACELIFT-01	4083	1690	1550	Automobile-Catalog 2010 Nissan Note 1.4 N-TEC specifications	https://www.automobile-catalog.com/car/2010/2293520/nissan_note_1_4_n-tec.html
EU-NISSAN-TIIDA-I-C11-HATCHBACK-01	4302	1695	1533	Automobile-Catalog 2008 Nissan Tiida Hatchback 1.5 dCi Europe specifications	https://www.automobile-catalog.com/car/2008/2291540/nissan_tiida_hatchback_1_5_dci.html
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.6 8V specifications	https://www.auto-data.net/en/dacia-logan-i-1.6-8v-87hp-15893
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534	Auto-Data Dacia Logan I facelift 1.6 specifications	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.6-85hp-17992
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550	Auto-Data Dacia Logan II MCV 1.2 specifications	https://www.auto-data.net/en/dacia-logan-ii-mcv-1.2-75hp-18335
EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	3535	1595	1480	Automobile-Catalog 2009 Kia Picanto 1.0 specifications	https://www.automobile-catalog.com/car/2009/1353920/kia_picanto_1_1_0.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-PREFL-01	4250	1790	1450	Automobile-Catalog 2008 Kia Pro_Cee'd 1.6 CVVT specifications	https://www.automobile-catalog.com/car/2008/1359935/kia_pro_cee_d_1_6_cvvt_ex.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-FACELIFT-01	4250	1790	1450	Auto-Data Kia Pro Cee'd I facelift specifications	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
```

## 下一步优先处理

1. 处理 Kia Picanto 1.1 LPG 的不同保险杠外廓边界，以及 Dacia Logan I `Kasten/Kombi` 的 Van／MCV 分支。
2. 批量闭合 Citroën Jumpy III Bus／Van 与 Peugeot Expert Bus／Van，优先复用现有 Compact、M、XL 和车顶高度尺寸组。
3. 最后集中处理 VW Caddy IV、Multivan／Transporter T6、Citroën C25、Mercedes-Benz Sprinter 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/nissan-note-i-e11-1.4-i-16v-88hp-842 "Nissan Note I (E11) 1.4 i 16V (88 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/dacia-logan-i-1.6-8v-87hp-15893 "Dacia Logan I 1.6 8V (87 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/2009/1353920/kia_picanto_1_1_0.html?utm_source=chatgpt.com "2009 Kia Picanto 1 1.0 (man. 5) (model since mid-year ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Jaguar E-Type、Nissan 300ZX、Dacia Logan `Kasten/Kombi` 和 Kia Picanto 共 5 个 Ktype。
* Jaguar E-Type 4.2 Fixed Head Coupé 按 Series I 与 Series 1½ 外廓拆分；长度、宽度相同，资料中的标准高度分别为 1222 mm 和 1219 mm。([汽车目录][1])
* Nissan 300ZX Z31 欧洲 2+2 Turbo 按改款前后拆分：改款前为 4540×1725×1310 mm，改款后为 4605×1725×1310 mm；133677 仅关联改款后外廓。([汽车目录][2])
* Dacia Logan `Kasten/Kombi` 按 Van 与 MCV Wagon 分支拆分；Kia Picanto 1.1 LPG 直接复用既有 Picanto I facelift 尺寸组。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射行：115
* PENDING Ktype：15
* 已确认并引用尺寸组：80
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133651_series1	133651	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-SERIES-1-COUPE-01	HIGH	Series I固定顶双座外廓。	READY
133651_series1half	133651	Coupe	E-Type Series 1½		3	EU-JAGUAR-E-TYPE-SERIES-1-5-COUPE-01	HIGH	Series 1½固定顶双座外廓。	READY
133676_prefl	133676	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-PREFL-01	HIGH	改款前2+2外廓。	READY
133676_facelift	133676	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	HIGH	改款后2+2外廓。	READY
133677	133677	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	HIGH	改款后2+2外廓。	READY
133899_van	133899	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-VAN-FACELIFT-01	MEDIUM	Kasten货运车身分支。	READY
133899_wagon	133899	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	HIGH	Kombi旅行车分支。	READY
133906	133906	Hatchback	Picanto I facelift	SA	5	EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-E-TYPE-SERIES-1-COUPE-01	4455	1657	1222	Automobile-Catalog 1966 Jaguar E-Type 4.2 Litre Fixed Head Coupe specifications	https://www.automobile-catalog.com/car/1966/1277030/jaguar_e-type_4_2_litre_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-SERIES-1-5-COUPE-01	4455	1657	1219	Automobile-Catalog 1968 Jaguar E-Type 4.2 Litre Fixed Head Coupe specifications	https://www.automobile-catalog.com/car/1968/1277465/jaguar_e-type_4_2_litre_fixed_head_coupe.html
EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-PREFL-01	4540	1725	1310	Automobile-Catalog 1984 Nissan 300ZX Turbo specifications	https://www.automobile-catalog.com/car/1984/2185415/nissan_300_zx_turbo.html
EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	4605	1725	1310	Automobile-Catalog 1987 Nissan 300ZX 2+2 dimensions; Automobile-Catalog 1987 Nissan 300ZX Turbo catalyst	https://www.automobile-catalog.com/car/1987/2185325/nissan_300_zx_22.html;https://www.automobile-catalog.com/car/1987/2185310/nissan_300_zx_turbo_cat.html
EU-DACIA-LOGAN-I-VAN-FACELIFT-01	4450	1740	1640	Auto-Data Dacia Logan I Van specifications	https://www.auto-data.net/en/dacia-logan-i-van-generation-3530
EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.6 MPI LPG specifications	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-mpi-8v-84-82hp-lpg-46184
```

## 下一步优先处理

1. 批量闭合 Citroën Jumpy III Van 的 XS、M、XL、低顶、高顶及 facelift 分支，优先复用既有尺寸组。
2. 处理 Peugeot Expert Bus／Van 和 Citroën Jumpy Bus 的 Compact、Standard、Long 及改款分支。
3. 最后集中处理 VW Caddy IV、Multivan／Transporter T6、Citroën C25 与 Mercedes-Benz Sprinter 多轴距、多车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1968/1277465/jaguar_e-type_4_2_litre_fixed_head_coupe.html?utm_source=chatgpt.com "1968 Jaguar E-Type 4.2 Litre Fixed Head Coupe Specs Review (198 kW / 269 PS / 265 hp) (up to mid-year 1968 for Europe )"
[2]: https://www.automobile-catalog.com/car/1984/2185415/nissan_300_zx_turbo.html?utm_source=chatgpt.com "1984 Nissan 300ZX Turbo Specs Review (167.5 kW ..."
[3]: https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-mpi-8v-84-82hp-lpg-46184?utm_source=chatgpt.com "Dacia Logan I MCV (facelift 2008) 1.6 MPI 8V (84/82 Hp) LPG"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Citroën Jumpy III Kasten 的 `133787`、`133788`。
* `133787` 的 BlueHDi 100 对应改款前 XS、M、XL 三种低载荷外廓；`133788` 的 BlueHDi 120 对应改款前 XS、M、XL，并覆盖改款后 M、XL。
* 官方尺寸表确认改款前 XS／M／XL 分别为 4609／4959／5309 mm，车宽均为不含后视镜的 1920 mm；2024 年改款后仅保留 M、XL 两种长度。
* 全部复用跨批次既有尺寸组，未重复创建或修正尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* READY 映射行：123
* PENDING Ktype：13
* 已确认并引用尺寸组：85
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133787_xs_low	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	改款前XS低载荷外廓。	READY
133787_m_low	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	改款前M低载荷外廓。	READY
133787_xl	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	改款前XL外廓。	READY
133788_xs_low	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	改款前XS低载荷外廓。	READY
133788_m_low	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	改款前M低载荷外廓。	READY
133788_xl	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	改款前XL外廓。	READY
133788_m_facelift	133788	Van	Jumpy III facelift	K0		EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	HIGH	改款后M外廓。	READY
133788_xl_facelift	133788	Van	Jumpy III facelift	K0		EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	HIGH	改款后XL外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Jumpy III Bus 与 Peugeot Expert Bus 的 Compact／Standard／Long及改款分支。
2. 首次创建并批量复用 Peugeot Expert Van 的 Compact／Standard／Long及改款尺寸组。
3. 最后处理 Caddy IV、T6、C25 和 Sprinter 多轴距、多车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 Citroën Jumpy III Bus 的 `133769`、`133770`，以及 Peugeot Expert III Bus 的 `133797`、`133798`。
* Jumpy Bus 按改款前 `XS / M / XL` 和改款后 `M / XL` 拆分。改款前官方技术资料对应 `4606 / 4956 / 5306 × 1920 mm`，XS 高 1905 mm，M、XL 高 1890 mm；改款后官方尺寸图对应 M、XL 长度 `4983 / 5333 mm`、不含后视镜宽 1920 mm，高度分别为 1895、1935 mm。([思域汽车][1])
* Expert Bus 的改款前 `Compact / Standard / Long` 直接复用既有尺寸组；改款后首次创建 Standard、Long 两组，官方尺寸为 `4983 / 5333 × 1920 × 1890 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：143
* PENDING Ktype：9
* 已确认并引用尺寸组：95
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133769_xs	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XS-01	HIGH	改款前XS外廓。	READY
133769_m	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-M-01	HIGH	改款前M外廓。	READY
133769_xl	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XL-01	HIGH	改款前XL外廓。	READY
133769_m_facelift	133769	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	HIGH	改款后M外廓。	READY
133769_xl_facelift	133769	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	HIGH	改款后XL外廓。	READY
133770_xs	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XS-01	HIGH	改款前XS外廓。	READY
133770_m	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-M-01	HIGH	改款前M外廓。	READY
133770_xl	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XL-01	HIGH	改款前XL外廓。	READY
133770_m_facelift	133770	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	HIGH	改款后M外廓。	READY
133770_xl_facelift	133770	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	HIGH	改款后XL外廓。	READY
133797_compact	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	改款前Compact外廓。	READY
133797_standard	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	改款前Standard外廓。	READY
133797_long	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	改款前Long外廓。	READY
133797_standard_facelift	133797	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133797_long_facelift	133797	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133798_compact	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	改款前Compact外廓。	READY
133798_standard	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	改款前Standard外廓。	READY
133798_long	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	改款前Long外廓。	READY
133798_standard_facelift	133798	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133798_long_facelift	133798	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895	Citroën ë-Jumpy Kombi official price and technical data April 2024	https://www.citroen.de/content/dam/citroen/germany/pdfs/brochure/04-24/Preisliste-%C3%AB-Jumpy_Kombi_12042024.pdf
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935	Citroën ë-Jumpy Kombi official price and technical data April 2024	https://www.citroen.de/content/dam/citroen/germany/pdfs/brochure/04-24/Preisliste-%C3%AB-Jumpy_Kombi_12042024.pdf
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	4983	1920	1890	Peugeot Expert Kombi and Traveller official dimensions	https://www.peugeot.de/content/dam/peugeot/germany/downloads/Preisliste_E-Traveller.pdf
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	5333	1920	1890	Peugeot Expert Kombi and Traveller official dimensions	https://www.peugeot.de/content/dam/peugeot/germany/downloads/Preisliste_E-Traveller.pdf
```

## 下一步优先处理

1. 闭合 Peugeot Expert Kasten `133799`、`133800` 的 Compact／Standard／Long及改款分支。
2. 处理 VW Caddy IV `133860` 与 Multivan／Transporter T6 `133871`、`133872` 的 SWB／LWB和车顶分支。
3. 最后集中闭合 Citroën C25 `133767` 与 Mercedes-Benz Sprinter `133884`、`133886`、`133888` 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf?utm_source=chatgpt.com "CITROËN SPACETOURER, JUMPY KOMBI"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 闭合 Peugeot Expert Kasten 的 `133799`、`133800`。
* 两个 Ktype 均拆分为改款前 `Compact / Standard / Long`，以及改款后 `Standard / Long`。官方资料确认旧款提供 Compact 车身；改款前 Standard／Long 为 `4959 / 5309 × 1920 × 1904 / 1935 mm`，改款后 Standard／Long 为 `4981 / 5331 × 1924 × 1910 mm`，宽度均采用官方明确标注的不含后视镜口径。([Stellantis Media][1])
* 本轮首次创建 5 个 Peugeot Expert Van 尺寸组，没有改写既有跨批次尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射行：153
* PENDING Ktype：7
* 已确认并引用尺寸组：100
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133799_compact	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	改款前Compact外廓。	READY
133799_standard	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	改款前Standard外廓。	READY
133799_long	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	改款前Long外廓。	READY
133799_standard_facelift	133799	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133799_long_facelift	133799	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133800_compact	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	改款前Compact外廓。	READY
133800_standard	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	改款前Standard外廓。	READY
133800_long	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	改款前Long外廓。	READY
133800_standard_facelift	133800	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133800_long_facelift	133800	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910	PEUGEOT Traveller and Expert official handbook 2020	https://public.servicebox.peugeot.com/APddb/modeles/expert/eGuide_expert_expert3vp_ed01-20/pdfs/9999_9999_328_en-GB.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904	PEUGEOT Expert official UK specification guide 2024 model year	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935	PEUGEOT Expert official UK specification guide 2024 model year	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	4981	1924	1910	PEUGEOT Expert official Ireland specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/expert-spec.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	5331	1924	1910	PEUGEOT Expert official Ireland specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/expert-spec.pdf
```

## 下一步优先处理

1. 闭合 VW Caddy IV `133860` 的标准轴距与 Maxi 分支。
2. 闭合 Multivan／Transporter T6 的 SWB／LWB及标准顶分支。
3. 最后处理 Citroën C25 与 Mercedes-Benz Sprinter `133884`、`133886`、`133888` 的轴距和车顶组合。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/peugeot/press/peugeot-launches-revised-expert-range "PEUGEOT LAUNCHES REVISED EXPERT RANGE | Peugeot | Stellantis Media"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 闭合 VW Caddy IV `133860`，按标准轴距与 Maxi 长轴距拆分。官方乘用版尺寸分别为 `4408×1793×1822 mm` 和 `4878×1793×1831 mm`，其中宽度为不含后视镜口径。
* 闭合 VW Multivan T6.1 `133871` 和 Transporter／Caravelle T6.1 `133872`，两者复用相同客运车身尺寸组，分别拆分为短轴距和长轴距。官方资料确认外廓为 `4904×1904×1970 mm` 和 `5304×1904×1990 mm`。
* 本轮首次创建 4 个尺寸组；未改写任何既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：159
* PENDING Ktype：4
* 已确认并引用尺寸组：104
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133860_swb	133860	MPV	Caddy IV	SA	5	EU-VW-CADDY-IV-MPV-SWB-01	HIGH	标准轴距外廓。	READY
133860_lwb	133860	MPV	Caddy IV	SA	5	EU-VW-CADDY-IV-MPV-LWB-01	HIGH	Maxi长轴距外廓。	READY
133871_swb	133871	MPV	Multivan T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-SWB-01	HIGH	短轴距外廓。	READY
133871_lwb	133871	MPV	Multivan T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-LWB-01	HIGH	长轴距外廓。	READY
133872_swb	133872	MPV	Transporter/Caravelle T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-SWB-01	HIGH	短轴距客运外廓。	READY
133872_lwb	133872	MPV	Transporter/Caravelle T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-LWB-01	HIGH	长轴距客运外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Caddy Trendline and Alltrack official MY20 brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831	Volkswagen Caddy Trendline and Alltrack official MY20 brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-VW-T6-1-PASSENGER-BUS-SWB-01	4904	1904	1970	Volkswagen Multivan official specifications February 2020; Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf;https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-T6-1-PASSENGER-BUS-LWB-01	5304	1904	1990	Volkswagen Multivan official specifications February 2020; Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf;https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
```

## 下一步优先处理

1. 闭合 Mercedes-Benz Sprinter `133884`、`133886`、`133888`，按 4-T、前驱／后驱、轴距与车顶组合确认有效分支。
2. 闭合 Citroën C25 `133767` 的轴距、车顶及生产期外廓分支。
3. 达到 `PENDING=0` 后立即进行一次机械闭合检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 最后闭合 Citroën C25 `133767` 与 Mercedes-Benz Sprinter 4-T `133884`、`133886`、`133888`。
* C25 按短轴低顶、长轴高顶拆分；Sprinter 按前驱 W910 的 L1H1／L2H1，以及后驱 W907 的 L1H1 拆分。Mercedes-Benz 官方尺寸资料明确区分车身宽度与含后视镜宽度；C25 长轴高顶规格为 `5489×1965×2420 mm`。([MB Vans][1])
* 已完成固定表头、唯一主键、外键引用、尺寸字段、来源字段和下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* 最终映射行：166
* PENDING Ktype：0
* 最终 DIMENSION_GROUP：110
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 长宽高和来源空值：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133645	133645	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133649	133649	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133650	133650	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
133651_series1	133651	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-SERIES-1-COUPE-01	HIGH	Series I固定顶双座外廓。	READY
133651_series1half	133651	Coupe	E-Type Series 1½		3	EU-JAGUAR-E-TYPE-SERIES-1-5-COUPE-01	HIGH	Series 1½固定顶双座外廓。	READY
133652_prefl	133652	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	改款前外廓。	READY
133652_facelift	133652	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
133653	133653	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
133654	133654	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
133655_prefl	133655	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	改款前外廓。	READY
133655_facelift	133655	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133656	133656	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
133657	133657	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
133658	133658	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133659	133659	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133660	133660	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
133668_prefl	133668	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133668_facelift	133668	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	改款后外廓。	READY
133669	133669	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133670	133670	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	改款前外廓。	READY
133676_prefl	133676	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-PREFL-01	HIGH	改款前2+2外廓。	READY
133676_facelift	133676	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	HIGH	改款后2+2外廓。	READY
133677	133677	Coupe	300ZX Z31	Z31	3	EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	HIGH	改款后2+2外廓。	READY
133679	133679	SUV	Q2 GA	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
133680	133680	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
133682	133682	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133683	133683	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133684	133684	SUV	Qashqai II facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	前驱标准车高。	READY
133685	133685	Convertible	488 Pista Spider		2	EU-FERRARI-488-PISTA-SPIDER-CONVERTIBLE-01	HIGH		READY
133699	133699	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
133700	133700	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
133701	133701	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
133709	133709	Coupe	B4 F32 facelift	F32	2	EU-ALPINA-B4-F32-COUPE-FACELIFT-01	HIGH		READY
133710	133710	Coupe	B4 F32 facelift	F32	2	EU-ALPINA-B4-F32-COUPE-FACELIFT-01	HIGH		READY
133711	133711	Convertible	B4 F33 facelift	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-FACELIFT-01	HIGH		READY
133714	133714	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	HIGH	前驱标准车高。	READY
133716	133716	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
133719	133719	SUV	Vitara IV facelift	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133720	133720	SUV	Vitara IV facelift	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133722	133722	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	HIGH		READY
133723	133723	SUV	Niro I	DE	5	EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	HIGH		READY
133731_prefl	133731	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133731_facelift	133731	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133732_prefl	133732	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133732_facelift	133732	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
133739	133739	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	HIGH	GTS外部套件外廓。	READY
133740	133740	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	HIGH	GTS Sport Turismo外廓。	READY
133745	133745	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-HATCHBACK-TGI-01	HIGH		READY
133766	133766	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133767_swb_lowroof	133767	Van	C25 I	280		EU-CITROEN-C25-I-VAN-SWB-LOWROOF-01	MEDIUM	短轴距低顶外廓。	READY
133767_lwb_highroof	133767	Van	C25 I	290		EU-CITROEN-C25-I-VAN-LWB-HIGHROOF-01	MEDIUM	长轴距高顶外廓。	READY
133769_xs	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XS-01	HIGH	改款前XS外廓。	READY
133769_m	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-M-01	HIGH	改款前M外廓。	READY
133769_xl	133769	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XL-01	HIGH	改款前XL外廓。	READY
133769_m_facelift	133769	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	HIGH	改款后M外廓。	READY
133769_xl_facelift	133769	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	HIGH	改款后XL外廓。	READY
133770_xs	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XS-01	HIGH	改款前XS外廓。	READY
133770_m	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-M-01	HIGH	改款前M外廓。	READY
133770_xl	133770	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-COMBI-XL-01	HIGH	改款前XL外廓。	READY
133770_m_facelift	133770	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	HIGH	改款后M外廓。	READY
133770_xl_facelift	133770	MPV	Jumpy III facelift	K0	5	EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	HIGH	改款后XL外廓。	READY
133779	133779	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133780	133780	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133781	133781	SUV	DR 3 I		5	EU-DR-DR3-I-SUV-01	HIGH		READY
133787_xs_low	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	改款前XS低载荷外廓。	READY
133787_m_low	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	改款前M低载荷外廓。	READY
133787_xl	133787	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	改款前XL外廓。	READY
133788_xs_low	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	改款前XS低载荷外廓。	READY
133788_m_low	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	改款前M低载荷外廓。	READY
133788_xl	133788	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	改款前XL外廓。	READY
133788_m_facelift	133788	Van	Jumpy III facelift	K0		EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	HIGH	改款后M外廓。	READY
133788_xl_facelift	133788	Van	Jumpy III facelift	K0		EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	HIGH	改款后XL外廓。	READY
133795_compact	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	改款前Compact外廓。	READY
133795_standard	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	改款前Standard外廓。	READY
133795_long	133795	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	改款前Long外廓。	READY
133795_standard_facelift	133795	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	HIGH	改款后Standard外廓。	READY
133795_long_facelift	133795	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	HIGH	改款后Long外廓。	READY
133796_compact	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	改款前Compact外廓。	READY
133796_standard	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	改款前Standard外廓。	READY
133796_long	133796	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	改款前Long外廓。	READY
133796_standard_facelift	133796	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	HIGH	改款后Standard外廓。	READY
133796_long_facelift	133796	MPV	Traveller I facelift	K0	5	EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	HIGH	改款后Long外廓。	READY
133797_compact	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	改款前Compact外廓。	READY
133797_standard	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	改款前Standard外廓。	READY
133797_long	133797	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	改款前Long外廓。	READY
133797_standard_facelift	133797	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133797_long_facelift	133797	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133798_compact	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	改款前Compact外廓。	READY
133798_standard	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	改款前Standard外廓。	READY
133798_long	133798	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	改款前Long外廓。	READY
133798_standard_facelift	133798	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133798_long_facelift	133798	MPV	Expert III facelift	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133799_compact	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	改款前Compact外廓。	READY
133799_standard	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	改款前Standard外廓。	READY
133799_long	133799	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	改款前Long外廓。	READY
133799_standard_facelift	133799	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133799_long_facelift	133799	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133800_compact	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	改款前Compact外廓。	READY
133800_standard	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	改款前Standard外廓。	READY
133800_long	133800	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	改款前Long外廓。	READY
133800_standard_facelift	133800	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	HIGH	改款后Standard外廓。	READY
133800_long_facelift	133800	Van	Expert III facelift	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	HIGH	改款后Long外廓。	READY
133801	133801	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH		READY
133816	133816	SUV	XV I	GP3	5	EU-SUBARU-XV-I-GP-SUV-01	HIGH		READY
133817	133817	SUV	XV I	GP7	5	EU-SUBARU-XV-I-GP-SUV-01	HIGH		READY
133818	133818	SUV	Forester IV	SJ5	5	EU-SUBARU-FORESTER-IV-SJ-SUV-01	HIGH		READY
133828_prefl	133828	MPV	Note I	E11	5	EU-NISSAN-NOTE-I-E11-MPV-PREFL-01	HIGH	改款前外廓。	READY
133828_facelift	133828	MPV	Note I facelift	E11	5	EU-NISSAN-NOTE-I-E11-MPV-FACELIFT-01	HIGH	改款后外廓。	READY
133829	133829	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-I-C11-HATCHBACK-01	HIGH		READY
133830	133830	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	353 kW早期R35外廓。	READY
133834_prefl	133834	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	HIGH	改款前外廓。	READY
133834_facelift	133834	SUV	Rogue I	S35	5	EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133848	133848	SUV	Terrano III	D10	5	EU-NISSAN-TERRANO-III-D10-SUV-01	HIGH		READY
133855_prefl	133855	Hatchback	Splash I		5	EU-SUZUKI-SPLASH-I-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133855_facelift	133855	Hatchback	Splash I facelift		5	EU-SUZUKI-SPLASH-I-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133857_prefl	133857	SUV	Kodiaq I		5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH	改款前外廓。	READY
133857_facelift	133857	SUV	Kodiaq I		5	EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133859_prefl	133859	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133859_facelift	133859	Hatchback	Superb III	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133860_swb	133860	MPV	Caddy IV	SA	5	EU-VW-CADDY-IV-MPV-SWB-01	HIGH	标准轴距外廓。	READY
133860_lwb	133860	MPV	Caddy IV	SA	5	EU-VW-CADDY-IV-MPV-LWB-01	HIGH	Maxi长轴距外廓。	READY
133863_prefl	133863	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133863_facelift	133863	Wagon	Superb III	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
133864	133864	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH		READY
133865	133865	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH		READY
133866_3dr	133866	Hatchback	Swift III		3	EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
133866_5dr	133866	Hatchback	Swift III		5	EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
133867_prefl	133867	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
133867_facelift	133867	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
133868_prefl	133868	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	HIGH	改款前外廓。	READY
133868_facelift	133868	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
133870	133870	Hatchback	Alto VII	GF	5	EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	HIGH		READY
133871_swb	133871	MPV	Multivan T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-SWB-01	HIGH	短轴距外廓。	READY
133871_lwb	133871	MPV	Multivan T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-LWB-01	HIGH	长轴距外廓。	READY
133872_swb	133872	MPV	Transporter/Caravelle T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-SWB-01	HIGH	短轴距客运外廓。	READY
133872_lwb	133872	MPV	Transporter/Caravelle T6.1	SG		EU-VW-T6-1-PASSENGER-BUS-LWB-01	HIGH	长轴距客运外廓。	READY
133874	133874	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-01	HIGH		READY
133875	133875	SUV	Edge II facelift		5	EU-FORD-EDGE-II-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
133880	133880	Coupe	E-Class V	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
133881	133881	Convertible	E-Class V	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH		READY
133882_prefl	133882	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
133882_facelift	133882	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
133884_l1h1	133884	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	前驱L1H1外廓。	READY
133884_l2h1	133884	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	前驱L2H1外廓。	READY
133886_l1h1	133886	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L1-H1-RWD-01	MEDIUM	后驱L1H1外廓。	READY
133887	133887	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
133888_l1h1	133888	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	前驱L1H1外廓。	READY
133888_l2h1	133888	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	前驱L2H1外廓。	READY
133889	133889	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-01	HIGH		READY
133892_prefl	133892	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133892_facelift	133892	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133893_prefl	133893	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
133893_facelift	133893	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
133894_prefl	133894	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-ED-WAGON-PREFL-01	HIGH	改款前旅行车外廓。	READY
133894_facelift	133894	Wagon	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
133896	133896	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
133899_van	133899	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-VAN-FACELIFT-01	MEDIUM	Kasten货运车身分支。	READY
133899_wagon	133899	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	HIGH	Kombi旅行车分支。	READY
133900	133900	Hatchback	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH		READY
133901	133901	Wagon	Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	HIGH		READY
133904	133904	Hatchback	Picanto I facelift	SA	5	EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	HIGH		READY
133906	133906	Hatchback	Picanto I facelift	SA	5	EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	HIGH		READY
133907_prefl	133907	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-PREFL-01	HIGH	改款前三门外廓。	READY
133907_facelift	133907	Hatchback	Pro cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-FACELIFT-01	HIGH	改款后三门外廓。	READY
133913	133913	Sedan	Vesta I		4	EU-LADA-VESTA-I-SEDAN-01	HIGH		READY
133935	133935	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3101-3200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-AUDI-A4-B9-SEDAN-01
EU-JAGUAR-E-TYPE-SERIES-1-COUPE-01	4455	1657	1222	Automobile-Catalog 1966 Jaguar E-Type 4.2 Litre Fixed Head Coupe specifications	https://www.automobile-catalog.com/car/1966/1277030/jaguar_e-type_4_2_litre_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-SERIES-1-5-COUPE-01	4455	1657	1219	Automobile-Catalog 1968 Jaguar E-Type 4.2 Litre Fixed Head Coupe specifications	https://www.automobile-catalog.com/car/1968/1277465/jaguar_e-type_4_2_litre_fixed_head_coupe.html
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-AUDI-A5-F5-COUPE-01
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-AUDI-A5-F5-SPORTBACK-01
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-AUDI-A4-B9-AVANT-WAGON-01
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371	Audi A5/S5 Coupé & Cabriolet official data information 2017	https://audi-press.jp/presskits/b7rqqm00000034lo-att/2017_Audi_A5_S5.pdf
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Audi A5 New Look and New Technologies official press kit	https://www.audi-mediacenter.com/en/the-audi-a5-new-look-and-new-technologies-12622/download
EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-PREFL-01	4540	1725	1310	Automobile-Catalog 1984 Nissan 300ZX Turbo specifications	https://www.automobile-catalog.com/car/1984/2185415/nissan_300_zx_turbo.html
EU-NISSAN-300ZX-Z31-COUPE-2PLUS2-FACELIFT-01	4605	1725	1310	Automobile-Catalog 1987 Nissan 300ZX 2+2 dimensions; Automobile-Catalog 1987 Nissan 300ZX Turbo catalyst	https://www.automobile-catalog.com/car/1987/2185325/nissan_300_zx_22.html;https://www.automobile-catalog.com/car/1987/2185310/nissan_300_zx_turbo_cat.html
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-AUDI-Q2-GA-SUV-01
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-HYUNDAI-TUCSON-III-TL-SUV-01
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Nissan Qashqai MY18 official brochure November 2019	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/QASHQAI_Brochure_November_2019.pdf
EU-FERRARI-488-PISTA-SPIDER-CONVERTIBLE-01	4605	1975	1206	Ferrari 488 Pista Spider official press kit	https://cdn.ferrari.com/cms/network/media/pdf/cs_ferrari_488_pista_spider_gbr.pdf
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-KIA-SPORTAGE-IV-SUV-01
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-KIA-OPTIMA-JF-SEDAN-01
EU-ALPINA-B4-F32-COUPE-FACELIFT-01	4640	1825	1373	BMW ALPINA B4 S BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-F33-CONVERTIBLE-FACELIFT-01	4640	1825	1380	BMW ALPINA B4 S BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1846	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01
EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	4175	1775	1610	Suzuki Vitara 2019 official distributor brochure	https://i.i-sgcm.com/new_cars/cars/11721/brochures/brochure_20190221114722.pdf
EU-KIA-NIRO-I-DE-E-NIRO-SUV-01	4375	1805	1560	Kia e-Niro 2018 official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/eNiro_PETD/Kia%20e-Niro%20-%202018%20PETD%20-%20December%202018.doc
EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	4861	1864	1468	ŠKODA Superb official technical specifications 2018	https://cdn.skoda-storyboard.com/2018/02/TD-SUPERB_en.pdf
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469	ŠKODA Superb official technical specifications 2019	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	4856	1864	1477	ŠKODA Superb Combi official technical specifications	https://cdn.skoda-storyboard.com/2016/05/TD-SUPERB-COMBI-en-1.pdf
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477	ŠKODA Superb Combi official technical specifications 2019	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417	Porsche Panamera GTS official EU fact sheet	https://newsroom.porsche.com/dam/jcr%3A1db5ef7e-115f-47d2-8540-305be8e1d9ea/S18_2880.pdf
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422	Porsche Panamera GTS Sport Turismo official EU fact sheet	https://newsroom.porsche.com/dam/jcr%3A3dc7b94b-bb34-4062-ac60-1027bfed763d/S18_2882.pdf
EU-VW-GOLF-VII-HATCHBACK-TGI-01	4258	1799	1492	Auto-Data Volkswagen Golf VII facelift 1.5 TGI 130 specifications	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.5-tgi-130hp-dsg-37257
EU-BMW-X2-F39-SUV-01	4360	1824	1526	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-BMW-X2-F39-SUV-01
EU-CITROEN-C25-I-VAN-SWB-LOWROOF-01	4759	1965	2108	Citroën C25 / Peugeot J5 / Talbot Express / Fiat Ducato I model dimensions	https://ru.wikipedia.org/wiki/Citro%C3%ABn_C25_-_Peugeot_J5_-_Talbot_Express_-_Fiat_Ducato_I
EU-CITROEN-C25-I-VAN-LWB-HIGHROOF-01	5489	1965	2420	WheelsAge Citroën C25 LWB Van High specifications	https://en.wheelsage.org/twins/group/120233/specifications
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890	Citroën SpaceTourer and Jumpy Kombi official technical specifications	https://www.citroenauto.hu/files/haszongepjarmuvek/jumpy/muszaki-jumpy-furgon.pdf
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895	Citroën ë-Jumpy Kombi official price and technical data April 2024	https://www.citroen.de/content/dam/citroen/germany/pdfs/brochure/04-24/Preisliste-%C3%AB-Jumpy_Kombi_12042024.pdf
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935	Citroën ë-Jumpy Kombi official price and technical data April 2024	https://www.citroen.de/content/dam/citroen/germany/pdfs/brochure/04-24/Preisliste-%C3%AB-Jumpy_Kombi_12042024.pdf
EU-DR-DR3-I-SUV-01	4200	1760	1570	DR Automobiles DR 3 official specifications	https://drautomobiles.com/dr-3/
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-CITROEN-JUMPY-III-VAN-XS-LOW-01
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-CITROEN-JUMPY-III-VAN-M-LOW-01
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-CITROEN-JUMPY-III-VAN-XL-01
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	4983	1920	1890	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	5333	1920	1890	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	4983	1920	1890	Peugeot Expert Kombi and Traveller official dimensions	https://www.peugeot.de/content/dam/peugeot/germany/downloads/Preisliste_E-Traveller.pdf
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	5333	1920	1890	Peugeot Expert Kombi and Traveller official dimensions	https://www.peugeot.de/content/dam/peugeot/germany/downloads/Preisliste_E-Traveller.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910	PEUGEOT Traveller and Expert official handbook 2020	https://public.servicebox.peugeot.com/APddb/modeles/expert/eGuide_expert_expert3vp_ed01-20/pdfs/9999_9999_328_en-GB.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904	PEUGEOT Expert official UK specification guide 2024 model year	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935	PEUGEOT Expert official UK specification guide 2024 model year	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	4981	1924	1910	PEUGEOT Expert official Ireland specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/expert-spec.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	5331	1924	1910	PEUGEOT Expert official Ireland specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/expert-spec.pdf
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01
EU-SUBARU-XV-I-GP-SUV-01	4450	1780	1570	Subaru Deutschland XV MY2012 official technical brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/XV/XV_MJ2012.pdf
EU-SUBARU-FORESTER-IV-SJ-SUV-01	4595	1795	1735	Subaru Deutschland Forester MY2013 official technical brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/Forester/Forester_MJ2013_PTA.pdf
EU-NISSAN-NOTE-I-E11-MPV-PREFL-01	4083	1690	1550	Auto-Data Nissan Note I E11 1.4 i 16V specifications	https://www.auto-data.net/en/nissan-note-i-e11-1.4-i-16v-88hp-842
EU-NISSAN-NOTE-I-E11-MPV-FACELIFT-01	4083	1690	1550	Automobile-Catalog 2010 Nissan Note 1.4 N-TEC specifications	https://www.automobile-catalog.com/car/2010/2293520/nissan_note_1_4_n-tec.html
EU-NISSAN-TIIDA-I-C11-HATCHBACK-01	4302	1695	1533	Automobile-Catalog 2008 Nissan Tiida Hatchback 1.5 dCi Europe specifications	https://www.automobile-catalog.com/car/2008/2291540/nissan_tiida_hatchback_1_5_dci.html
EU-NISSAN-GT-R-R35-COUPE-PREFL-01	4655	1895	1370	Nissan Heritage Collection NISSAN GT-R R35 official specifications	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/418_nissan_gt-r.html
EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01	4646	1801	1659	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-NISSAN-ROGUE-I-S35-SUV-PREFL-01
EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01	4656	1801	1684	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-NISSAN-ROGUE-I-S35-SUV-FACELIFT-01
EU-NISSAN-TERRANO-III-D10-SUV-01	4315	1822	1695	Nissan Terrano official brochure	https://www.nissan-cdn.net/content/dam/Nissan/kz/brochures/nissan-terrano-brochure.pdf
EU-SUZUKI-SPLASH-I-HATCHBACK-PREFL-01	3715	1680	1590	Auto-Data Suzuki Splash 1.2i specifications	https://www.auto-data.net/en/suzuki-splash-1.2i-86hp-16489
EU-SUZUKI-SPLASH-I-HATCHBACK-FACELIFT-01	3715	1680	1590	Auto-Data Suzuki Splash facelift 2012 specifications	https://www.auto-data.net/en/suzuki-splash-facelift-2012-generation-4515
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655	ŠKODA KODIAQ official technical specifications 2018	https://cdn.skoda-storyboard.com/2018/02/TD-KODIAQ_en.pdf
EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	4697	1882	1661	ŠKODA KODIAQ official technical specifications 2021	https://cdn.skoda-storyboard.com/2021/06/TD_KODIAQ_en.pdf
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Caddy Trendline and Alltrack official MY20 brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831	Volkswagen Caddy Trendline and Alltrack official MY20 brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/april/caddy-trendline-and-alltrack-online-brochure.pdf
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659	Volkswagen UK Touran official brochure June 2017	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touran/touran-nf/vw-touran-nf-brochure-june-2017.pdf
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-VW-POLO-VI-HATCHBACK-TSI-01
EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	3695	1690	1500	Auto-Data Suzuki Swift 1.3i specifications	https://www.auto-data.net/en/suzuki-swift-iv-1.3-i-16v-92hp-16523
EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	3695	1690	1500	Auto-Data Suzuki Swift 1.3i specifications	https://www.auto-data.net/en/suzuki-swift-iv-1.3-i-16v-92hp-16523
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-VW-PASSAT-B8-SEDAN-PREFL-01
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483	Volkswagen UK New Passat official brochure 2019	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-ix/new-passat-estate-brochure.pdf
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477	Volkswagen UK Passat and Passat Estate official brochure 2016	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516	Volkswagen UK New Passat official brochure 2019	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-ix/new-passat-estate-brochure.pdf
EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	3500	1600	1470	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01
EU-VW-T6-1-PASSENGER-BUS-SWB-01	4904	1904	1970	Volkswagen Multivan official specifications February 2020; Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf;https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-T6-1-PASSENGER-BUS-LWB-01	5304	1904	1990	Volkswagen Multivan official specifications February 2020; Volkswagen Caravelle 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf;https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-KIA-CERATO-I-LD-SEDAN-01	4480	1735	1470	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-KIA-CERATO-I-LD-SEDAN-01
EU-FORD-EDGE-II-SUV-FACELIFT-01	4834	1928	1732	Ford UK Edge 2019 official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-edge.pdf
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.6 8V specifications	https://www.auto-data.net/en/dacia-logan-i-1.6-8v-87hp-15893
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534	Auto-Data Dacia Logan I facelift 1.6 specifications	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.6-85hp-17992
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	5267	2020	2356	Mercedes-Benz Sprinter Panel and Crew Van official price list 2023	https://media.mbvans.co.uk/assets/documents/original/5951-SprinterPanelandCrewVanPricelistNOV2023.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	5932	2020	2351	Mercedes-Benz Sprinter Panel and Crew Van official price list 2023	https://media.mbvans.co.uk/assets/documents/original/5951-SprinterPanelandCrewVanPricelistNOV2023.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L1-H1-RWD-01	5267	2020	2356	Auto-Data Mercedes-Benz Sprinter 411 CDI RWD Compact W907 specifications	https://www.auto-data.net/en/mercedes-benz-sprinter-panel-van-compact-w907-w910-411-cdi-114hp-w907-48747
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550	Auto-Data Dacia Logan II MCV 1.2 specifications	https://www.auto-data.net/en/dacia-logan-ii-mcv-1.2-75hp-18335
EU-KIA-CERATO-I-LD-HATCHBACK-01	4340	1735	1470	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-KIA-CERATO-I-LD-HATCHBACK-01
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480	Auto-Data Kia Cee'd I specifications	https://www.auto-data.net/en/kia-ceed-i-1.6-cvvt-122hp-42278
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480	Auto-Data Kia Cee'd I facelift specifications	https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.4-16v-90hp-17062
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I specifications	https://www.auto-data.net/en/kia-ceed-sw-i-1.4-cvvt-109hp-42437
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift specifications	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.4-16v-90hp-17071
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534	Task-provided cross-batch verified DIMENSION_GROUP cache	cache://task-provided-cross-batch-index/EU-DACIA-SANDERO-I-HATCHBACK-01
EU-DACIA-LOGAN-I-VAN-FACELIFT-01	4450	1740	1640	Auto-Data Dacia Logan I Van specifications	https://www.auto-data.net/en/dacia-logan-i-van-generation-3530
EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.6 MPI LPG specifications	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-mpi-8v-84-82hp-lpg-46184
EU-KIA-PICANTO-I-SA-HATCHBACK-FACELIFT-01	3535	1595	1480	Automobile-Catalog 2009 Kia Picanto 1.0 specifications	https://www.automobile-catalog.com/car/2009/1353920/kia_picanto_1_1_0.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-PREFL-01	4250	1790	1450	Automobile-Catalog 2008 Kia Pro_Cee'd 1.6 CVVT specifications	https://www.automobile-catalog.com/car/2008/1359935/kia_pro_cee_d_1_6_cvvt_ex.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-FACELIFT-01	4250	1790	1450	Auto-Data Kia Pro Cee'd I facelift specifications	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497	LADA Vesta sedan official specifications	https://lada-swiss.ch/cars/vesta/sedan/tth.html
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Mercedes-Benz Österreich Der neue Mercedes-Benz GLE official press information	https://media.mercedes-benz.at/news-der-neue-mercedes-benz-gle?id=75942&imageid=241349&l=deutsch&menueid=10014
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3101-3200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.mbvans.co.uk/assets/documents/original/5951-SprinterPanelandCrewVanPricelistNOV2023.pdf "https://media.mbvans.co.uk/assets/documents/original/5951-SprinterPanelandCrewVanPricelistNOV2023.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2549 行）
- 累计尺寸组：dimension_groups_final.tsv（1246 行）

