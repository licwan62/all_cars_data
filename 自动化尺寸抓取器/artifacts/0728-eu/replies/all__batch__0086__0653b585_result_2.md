# 任务：all 第 8501-8600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0086__0653b585


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8501-8600 行

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
all 第 8501-8600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425
EU-BMW-Z3-E36-7-ROADSTER-2-8-01	4025	1740	1293
EU-BMW-Z3-M-E36-7-ROADSTER-01	4025	1740	1266
EU-BUICK-SKYLARK-V-SEDAN-4D-1982-01	4600	1750	1364
EU-BUICK-SKYLARK-V-SEDAN-4D-PRE82-01	4620	1720	1359
EU-CATERHAM-SEVEN-CF-CONVERTIBLE-R500-01	3100	1575	800
EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	3300	1685	1140
EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	3380	1575	1115
EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	3460	1685	1115
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	4673	1849	1727
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	4167	1698	1391
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405
EU-FORD-GRANADA-II-SEDAN-2D-01	4633	1791	1416
EU-FORD-GRANADA-II-SEDAN-4D-01	4633	1791	1416
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380
EU-FORD-GRANADA-MK1-SEDAN-2D-01	4572	1791	1369
EU-FORD-GRANADA-MK1-SEDAN-4D-01	4572	1791	1369
EU-FORD-GRANADA-MK1-TURNIER-WAGON-01	4674	1791	1410
EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	4060	1570	1520
EU-FORD-TAUNUS-G13AL-WAGON-3D-01	4060	1570	1610
EU-FORD-TAUNUS-G13-SEDAN-2D-01	4060	1580	1550
EU-FORD-TAUNUS-G13-WAGON-3D-EARLY-01	4060	1580	1615
EU-FORD-TAUNUS-G13-WAGON-3D-LATE-01	4060	1580	1595
EU-FORD-TAUNUS-G93A-SEDAN-2D-01	4080	1485	1600
EU-FORD-TAUNUS-P2-SEDAN-FACELIFT-01	4375	1670	1470
EU-FORD-TAUNUS-P2-SEDAN-PREFL-01	4375	1670	1500
EU-FORD-TAUNUS-P2-WAGON-3D-01	4375	1670	1510
EU-FORD-TAUNUS-P3-COUPE-2D-01	4452	1670	1450
EU-FORD-TAUNUS-P3-SEDAN-01	4452	1670	1450
EU-FORD-TAUNUS-P3-WAGON-3D-01	4452	1670	1490
EU-FORD-TAUNUS-P4-COUPE-01	4322	1594	1424
EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	4248	1594	1458
EU-FORD-TAUNUS-P4-SEDAN-TS-01	4322	1594	1458
EU-FORD-TAUNUS-P4-WAGON-3D-01	4248	1594	1465
EU-FORD-TAUNUS-P5-SEDAN-01	4585	1715	1480
EU-FORD-TAUNUS-P6-COUPE-2D-01	4389	1603	1385
EU-FORD-TAUNUS-P6-SEDAN-01	4389	1603	1400
EU-FORD-TAUNUS-P6-WAGON-3D-01	4318	1603	1425
EU-FORD-TAUNUS-P7A-17M-SEDAN-01	4663	1756	1494
EU-FORD-TAUNUS-P7B-17M-SEDAN-01	4721	1756	1478
EU-FORD-TAUNUS-TC1-SEDAN-2D-01	4267	1701	1370
EU-FORD-TAUNUS-TC1-SEDAN-4D-01	4267	1701	1370
EU-FORD-TAUNUS-TC2-SEDAN-01	4267	1700	1370
EU-FORD-TAUNUS-TC2-SEDAN-2D-01	4380	1700	1362
EU-FORD-TAUNUS-TC2-SEDAN-4D-01	4380	1700	1362
EU-FORD-TAUNUS-TC2-WAGON-01	4440	1700	1366
EU-FORD-TAUNUS-TC3-SEDAN-2D-01	4340	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-2D-2P3-GHIA-01	4382	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-4D-01	4340	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-4D-2P3-GHIA-01	4382	1706	1363
EU-FORD-TAUNUS-TC3-WAGON-01	4440	1712	1355
EU-KIA-SPORTAGE-III-SL-SUV-5D-01	4440	1855	1635
EU-KIA-SPORTAGE-II-KM-SUV-01	4350	1800	1730
EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	4435	1765	1655
EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	4335	1730	1695
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1822	1462
EU-LEXUS-GS-III-S190-SEDAN-AWD-FACELIFT-01	4825	1820	1435
EU-LEXUS-GS-III-S190-SEDAN-AWD-PREFL-01	4825	1820	1435
EU-LEXUS-LS-I-XF10-SEDAN-4D-01	5005	1820	1425
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	4475	1710	1405
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	4435	1695	1405
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426
EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	3872	1655	1446
EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	3872	1655	1446
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356
EU-PEUGEOT-306-CABRIO-7D-PREFL-01	4144	1689	1356
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	4338	1689	1415
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	3995	1695	1365
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	3995	1692	1365
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	3995	1692	1365
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-3D-01	3995	1692	1367
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-5D-01	3995	1692	1367
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386
EU-PEUGEOT-306-SEDAN-7B-PREFL-01	4232	1689	1386
EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	3750	1460	1730
EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	3390	1395	1730
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	3370	1395	1870
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	3400	1395	1870
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-YETI-5L-SUV-FACELIFT-01	4222	1793	1691
EU-SKODA-YETI-5L-SUV-PREFL-01	4223	1793	1691
EU-TOYOTA-PASEO-L5-COUPE-2D-01	4160	1660	1290
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400
EU-VOLVO-C70-I-P80-COUPE-2D-01	4720	1820	1410
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439
EU-VW-SHARAN-I-MPV-01	4634	1810	1730

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	206	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1998	Dec 2012	2024-03-01	9466
Peugeot	206	1.6 I	Schrägheck	Frontantrieb	Benzin	65	89	Sep 1998	Dec 2000	2024-03-01	9467
Peugeot	206	1.9 D	Schrägheck	Frontantrieb	Diesel	51	69	Sep 1998	Nov 2001	2024-03-01	9468
Ford	Cougar	2.0 16V	Coupe	Frontantrieb	Benzin	96	131	Aug 1998	Dec 2001	2024-03-01	9469
Ford	Cougar	2.5 V6 24V	Coupe	Frontantrieb	Benzin	125	170	Aug 1998	Dec 2001	2024-03-01	9470
Chrysler	300m	3.5 V6 24V	Stufenheck	Frontantrieb	Benzin	187	254	Jul 1998	Aug 2000	2024-03-01	9471
Chrysler	300m	2.7 V6 24V	Stufenheck	Frontantrieb	Benzin	149	203	Nov 1998	Aug 2000	2024-03-01	9472
Lancia	Kappa	2.0 20V Turbo	Stufenheck	Frontantrieb	Benzin	162	220	Jun 1998	Oct 2001	2024-03-01	9473
Lancia	Kappa	2.0 20V Turbo	Coupe	Frontantrieb	Benzin	162	220	Jun 1998	Mar 2001	2024-03-01	9474
Lancia	Kappa	2.0 20V Turbo	Kombi	Frontantrieb	Benzin	162	220	Jun 1998	Oct 2001	2024-03-01	9475
Lancia	Kappa	2.4 JTD	Stufenheck	Frontantrieb	Diesel	100	136	Jun 1998	Oct 2001	2024-03-01	9476
Lancia	Kappa	2.4 JTD	Kombi	Frontantrieb	Diesel	100	136	Jun 1998	Oct 2001	2024-03-01	9477
BMW	Z3	M	Coupe	Heckantrieb	Benzin	236	321	Feb 1998	Jun 2001	2024-03-01	9479
Citroën	Xsara	1.9 SD	Schrägheck	Frontantrieb	Diesel	55	75	Jan 1998	Sep 2000	2024-03-01	9480
Citroën	Xsara	1.9 D	Kombi	Frontantrieb	Diesel	55	75	Jan 1998	Sep 2000	2024-03-01	9481
Piaggio	Porter	1.3 LPG	Bus	Heckantrieb	Benzin/Autogas (LPG)	52	71	Jan 2011	-	2024-03-01	9482
Piaggio	Porter	1.3	Bus	Heckantrieb	Benzin	53	72	Jan 2011	-	2024-03-01	9483
Piaggio	Porter	1.3 LPG	Bus	Heckantrieb	Benzin/Autogas (LPG)	53	72	Jan 2011	-	2024-03-01	9484
Piaggio	Porter	1.2 D	Bus	Heckantrieb	Diesel	47	64	Jan 2011	-	2024-03-01	9485
Piaggio	Ape	0.2	Pritsche/Fahrgestell	Heckantrieb	Gemisch	7	10	Jun 1982	Jul 1993	2024-03-01	9486
Piaggio	Ape	0.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	9	12	Jan 1982	Dec 1996	2024-03-01	9488
Piaggio	Ape	0.4 D	Kasten	Heckantrieb	Diesel	9	12	Jan 1982	Dec 1996	2024-03-01	9489
Piaggio	Ape	0.2	Kasten	Heckantrieb	Gemisch	7	10	Jun 1982	Jul 1993	2024-05-01	9490
Skoda	Yeti	1.8 TSI 4X4	SUV	Allrad	Benzin	112	152	Nov 2009	Dec 2017	2024-03-01	9491
Piaggio	Porter	Elektro	Bus	Heckantrieb	Elektro	11	15	Jan 1995	-	2024-03-01	9492
Piaggio	Ape	0.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	8	11	Jan 2007	-	2024-03-01	9496
Piaggio	Ape	0.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	6	8	Jan 2006	-	2024-03-01	9498
Mercedes-benz	Clk	CLK 200 Kompressor	Cabriolet	Heckantrieb	Benzin	141	192	Mar 1998	Jun 2000	2024-03-01	9499
Mercedes-benz	Clk	CLK 200	Cabriolet	Heckantrieb	Benzin	100	136	Mar 1998	Mar 2002	2024-03-01	9500
Mercedes-benz	Clk	CLK 230 Kompressor	Cabriolet	Heckantrieb	Benzin	142	193	Mar 1998	Jun 2000	2024-03-01	9501
Mercedes-benz	Clk	CLK 320	Cabriolet	Heckantrieb	Benzin	160	218	Mar 1998	Mar 2002	2024-03-01	9502
Alfa Romeo	145	1.8 I.e. 16V	Schrägheck	Frontantrieb	Benzin	106	144	Mar 1998	Jan 2001	2024-03-01	9503
Alfa Romeo	146	1.8 I.e. 16V T.s.	Schrägheck	Frontantrieb	Benzin	106	144	Mar 1998	Jan 2001	2024-03-01	9504
Alfa Romeo	145	2.0 16V	Schrägheck	Frontantrieb	Benzin	114	155	Mar 1998	Jan 2001	2024-03-01	9505
Alfa Romeo	146	2.0 16V	Schrägheck	Frontantrieb	Benzin	114	155	Mar 1997	Oct 2001	2024-03-01	9506
Volvo	C70 i	2	Cabriolet	Frontantrieb	Benzin	132	180	Mar 1998	Oct 2005	2024-03-01	9507
Volvo	C70 i	2.0 T	Cabriolet	Frontantrieb	Benzin	166	226	Mar 1998	Oct 2005	2024-03-01	9508
Volvo	C70 i	T5	Cabriolet	Frontantrieb	Benzin	176	239	Mar 1998	Oct 2005	2024-03-01	9509
Volvo	C70 i	2.4 T	Cabriolet	Frontantrieb	Benzin	142	193	Mar 1998	Oct 2005	2024-03-01	9510
VW	Golf iv	1.9 TDI 4motion	Schrägheck	Allrad	Diesel	66	90	Jul 1998	Apr 2002	2024-03-01	9511
Peugeot	306	1.9 D	Schrägheck	Frontantrieb	Diesel	55	75	Mar 1998	May 2001	2024-03-01	9512
Peugeot	306	1.9 D	Stufenheck	Frontantrieb	Diesel	55	75	Mar 1998	May 2001	2024-03-01	9513
Peugeot	306	1.9 D	Kombi	Frontantrieb	Diesel	55	75	Mar 1998	Apr 2002	2024-03-01	9514
Skoda	Octavia	1.6	Kombi	Frontantrieb	Benzin	74	101	Jul 1998	Dec 2007	2024-03-01	9515
Skoda	Octavia	1.8 20V	Kombi	Frontantrieb	Benzin	92	125	Jul 1998	Jul 2000	2024-03-01	9516
Skoda	Octavia	1.9 SDI	Kombi	Frontantrieb	Diesel	50	68	Jul 1998	Dec 2003	2024-03-01	9517
Skoda	Octavia	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Jul 1998	Mar 2010	2024-03-01	9518
Skoda	Octavia	1.9 TDI	Kombi	Frontantrieb	Diesel	81	110	Jul 1998	Jan 2006	2024-03-01	9519
Nissan	Primera	1.6 16V	Kombi	Frontantrieb	Benzin	66	90	Apr 1998	Dec 2001	2024-03-01	9520
Nissan	Primera	1.6 16V	Kombi	Frontantrieb	Benzin	73	99	Apr 1998	Dec 2001	2024-03-01	9521
Nissan	Primera	2.0 16V	Kombi	Frontantrieb	Benzin	85	115	Jun 1996	Dec 2001	2024-03-01	9522
Nissan	Primera	2.0 16V	Kombi	Frontantrieb	Benzin	96	131	Apr 1998	Dec 2001	2024-03-01	9523
Nissan	Primera	2.0 TD	Kombi	Frontantrieb	Diesel	66	90	Apr 1998	Dec 2001	2024-03-01	9524
Piaggio	Ape	0.4 D	Cabriolet	Heckantrieb	Diesel	8	11	Jan 2007	-	2024-03-01	9525
Piaggio	Ape	Elektro	Cabriolet	Heckantrieb	Elektro	9	12	Jan 2007	-	2024-03-01	9526
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	100	136	Nov 2005	Mar 2010	2024-03-01	9533
Buick	Skylark	2.4	Stufenheck	Frontantrieb	Benzin	112	152	Jan 1995	Dec 1999	2024-03-01	9534
Buick	Skylark	3.1	Stufenheck	Frontantrieb	Benzin	117	159	Jan 1994	Dec 1999	2024-03-01	9535
Cadillac	Srx	3	SUV	Frontantrieb	Benzin	198	269	Jan 2009	Dec 2016	2024-03-01	9536
Cadillac	Srx	3.0 AWD	SUV	Allrad	Benzin	198	269	Jan 2009	Dec 2016	2024-03-01	9537
Chevrolet	Captiva	2.4	SUV	Frontantrieb	Benzin	123	167	Mar 2011	-	2024-03-01	9538
Nissan	Micra ii	1.5 D	Schrägheck	Frontantrieb	Diesel	42	57	Feb 1998	Feb 2003	2024-03-01	9539
Mitsubishi	Carisma	1.8 16V GDI	Schrägheck	Frontantrieb	Benzin	92	125	Sep 1997	Jun 2006	2024-03-01	9540
Mitsubishi	Carisma	1.8 16V GDI	Stufenheck	Frontantrieb	Benzin	92	125	Sep 1997	Jun 2006	2024-03-01	9541
KIA	Sportage	2.0 TD 4WD	SUV	Allrad	Diesel	61	83	Oct 1997	Aug 2003	2024-03-01	9542
Honda	Civic vi aerodeck	1.4 16V	Kombi	Frontantrieb	Benzin	55	75	Apr 1998	Feb 2001	2024-03-01	9543
Honda	Civic vi aerodeck	1.4 16V	Kombi	Frontantrieb	Benzin	66	90	Apr 1998	Feb 2001	2024-03-01	9544
Honda	Civic vi aerodeck	1.5 16V	Kombi	Frontantrieb	Benzin	84	114	Apr 1998	Feb 2001	2024-03-01	9545
Honda	Civic vi aerodeck	1.6 16V	Kombi	Frontantrieb	Benzin	85	116	Apr 1998	Feb 2001	2024-03-01	9546
Honda	Civic vi aerodeck	1.8 16V	Kombi	Frontantrieb	Benzin	124	169	Apr 1998	Feb 2001	2024-03-01	9547
Honda	Civic vi aerodeck	2.0 I D	Kombi	Frontantrieb	Diesel	77	105	Apr 1998	Feb 2001	2024-03-01	9548
Nissan	Pathfinder ii	3.3 V6 4WD	Geländewagen geschlossen	Allrad	Benzin	125	170	Sep 1997	Dec 2004	2024-03-01	9549
KIA	Shuma	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	65	88	Oct 1997	Oct 2001	2024-03-01	9550
Nissan	Pathfinder ii	2.7 TD 4WD	Geländewagen geschlossen	Allrad	Diesel	96	131	Sep 1995	Dec 2004	2024-03-01	9551
KIA	Shuma i	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1997	Mar 2001	2024-03-01	9552
KIA	Shuma i	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	81	110	Oct 1997	Mar 2001	2024-03-01	9553
Hyundai	H-1 / starex	2.4 4WD	Bus	Allrad	Benzin	82	112	Feb 1998	Apr 2004	2024-03-01	9554
Hyundai	H-1 / starex	2.5 TD 4WD	Bus	Allrad	Diesel	59	80	Feb 1998	Apr 2004	2024-03-01	9555
Nissan	Pathfinder ii	3.2 TD 4WD	Geländewagen geschlossen	Allrad	Diesel	110	150	Sep 1995	Dec 2004	2024-03-01	9556
Ford	Granada	1.7	Kombi	Heckantrieb	Benzin	54	74	Aug 1977	Jul 1981	2024-03-01	9557
Ford	Taunus	1.3	Kombi	Heckantrieb	Benzin	40	54	Dec 1975	Jul 1979	2024-03-01	9558
Toyota	Land cruiser 100	4.7	Geländewagen geschlossen	Allrad	Benzin	173	235	Jan 1998	Aug 2007	2024-03-01	9559
Toyota	Land cruiser 100	4.2 TD	Geländewagen geschlossen	Allrad	Diesel	150	204	Jan 1998	Aug 2007	2024-03-01	9560
Toyota	Hilux vi	2.4 I 4WD	Pick-up	Allrad	Benzin	103	140	Aug 1997	Oct 2005	2024-03-01	9561
Lexus	Gs	300	Stufenheck	Heckantrieb	Benzin	156	212	Jan 1993	Aug 1997	2024-03-01	9562
Lexus	Gs	300	Stufenheck	Heckantrieb	Benzin	163	222	Aug 1997	Oct 2000	2024-03-01	9563
Lexus	Ls	400	Stufenheck	Heckantrieb	Benzin	209	284	Sep 1997	Oct 2000	2024-03-01	9564
Toyota	Rav 4 i cabrio	2.0 4WD	SUV	Allrad	Benzin	94	129	Dec 1997	Jun 2000	2024-03-01	9565
Toyota	Paseo	1.5	Cabriolet	Frontantrieb	Benzin	66	90	Oct 1996	Jan 1998	2024-03-01	9568
Lexus	Gs	400	Stufenheck	Heckantrieb	Benzin	216	294	Dec 1997	Nov 2000	2024-03-01	9569
Bedford	Blitz	1.8	Kasten	Heckantrieb	Benzin	49	67	Aug 1969	Oct 1987	2024-03-01	9578
Bedford	Blitz	2	Kasten	Heckantrieb	Benzin	56	76	Feb 1985	Oct 1987	2024-03-01	9579
Bedford	Blitz	2.3 D	Kasten	Heckantrieb	Diesel	46	63	Jan 1973	Oct 1987	2024-03-01	9580
Bedford	Blitz	2.1 D	Kasten	Heckantrieb	Diesel	44	60	Sep 1981	Oct 1987	2024-03-01	9581
Bedford	Blitz	2.0 D	Kasten	Heckantrieb	Diesel	44	60	Oct 1980	Oct 1983	2024-03-01	9582
Bedford	Blitz	2.3	Kasten	Heckantrieb	Benzin	58	79	Feb 1980	Oct 1983	2024-03-01	9583
Chevrolet	Captiva	2.4 4WD	SUV	Allrad	Benzin	123	167	Mar 2011	-	2024-03-01	9585
Chevrolet	Captiva	3.0 4WD	SUV	Allrad	Benzin	190	258	Nov 2010	Sep 2018	2024-03-01	9586
Caterham	Seven	2	Cabriolet	Heckantrieb	Benzin	131	178	Jan 2007	-	2024-03-01	9591
Chevrolet	Volt	EV 150	Schrägheck	Frontantrieb	Benzin/Elektro	111	151	Nov 2011	-	2024-03-01	9592


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 58 个输入 Ktype 的物理车身归并，共形成 67 行 READY 映射；其中复用既有尺寸组 23 个，本轮首次创建或因冲突新建尺寸组 14 个。
* Lancia Kappa 官方规格显示 Sedan/Wagon 宽度为 1826 mm，与累计表既有 `EU-LANCIA-KAPPA-838-SEDAN-01` 的 1822 mm 冲突；未覆盖旧组，按规则新建 `...SEDAN-02`。([Stellantis Media][1])
* 已闭合 Ford Cougar、Chrysler 300M、BMW Z3 M Coupe、Mercedes-Benz CLK A208 Cabriolet、Volvo C70 I Cabriolet 等尺寸组。([汽车数据网][2])
* 同时闭合 Xsara Break、Octavia I Combi、Cadillac SRX II、Civic VI Aerodeck、Kia Shuma Hatchback 和 Chevrolet Volt I。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：58
* READY 映射行：67
* 暂存 PENDING Ktype：42
* READY 映射已引用尺寸组：37
* 本轮新增或冲突新建尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9466_3dr	9466	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9466_5dr	9466	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9467_3dr	9467	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9467_5dr	9467	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9468_3dr	9468	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9468_5dr	9468	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9469	9469	Coupe	Cougar	BCV	3	EU-FORD-COUGAR-BCV-COUPE-3D-01	HIGH		READY
9470	9470	Coupe	Cougar	BCV	3	EU-FORD-COUGAR-BCV-COUPE-3D-01	HIGH		READY
9471	9471	Sedan	300M	LH	4	EU-CHRYSLER-300M-LH-SEDAN-4D-01	HIGH		READY
9472	9472	Sedan	300M	LH	4	EU-CHRYSLER-300M-LH-SEDAN-4D-01	HIGH		READY
9473	9473	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-02	HIGH	既有同名组尺寸冲突，改用新序号。	READY
9474	9474	Coupe	Kappa	838	2	EU-LANCIA-KAPPA-838-COUPE-2D-01	HIGH		READY
9475	9475	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-5D-01	HIGH		READY
9476	9476	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-02	HIGH	既有同名组尺寸冲突，改用新序号。	READY
9477	9477	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-5D-01	HIGH		READY
9479	9479	Coupe	Z3 M Coupe	E36/8	3	EU-BMW-Z3-M-E36-8-COUPE-3D-01	HIGH		READY
9480	9480	Hatchback	Xsara I	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	HIGH		READY
9481	9481	Wagon	Xsara I	N2	5	EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	HIGH		READY
9491_prefl	9491	SUV	Yeti	5L	5	EU-SKODA-YETI-5L-SUV-PREFL-01	HIGH	改款前物理分支。	READY
9491_facelift	9491	SUV	Yeti	5L	5	EU-SKODA-YETI-5L-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
9499	9499	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9500	9500	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9501	9501	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9502	9502	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9503	9503	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
9504	9504	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
9505	9505	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
9506	9506	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
9507	9507	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9508	9508	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9509	9509	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9510	9510	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9511_3dr	9511	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9511_5dr	9511	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9512_3dr	9512	Hatchback	306 Facelift		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9512_5dr	9512	Hatchback	306 Facelift		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9513	9513	Sedan	306 Facelift	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
9514	9514	Wagon	306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
9516	9516	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-01	HIGH		READY
9520	9520	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9521	9521	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9522	9522	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9523	9523	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9524	9524	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9533	9533	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
9536	9536	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-5D-01	HIGH		READY
9537	9537	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-5D-01	HIGH		READY
9538	9538	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9539_3dr	9539	Hatchback	Micra II	K11	3	EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	三门物理分支，共用同一尺寸组。	READY
9539_5dr	9539	Hatchback	Micra II	K11	5	EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	五门物理分支，共用同一尺寸组。	READY
9540_prefl	9540	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	HIGH	改款前物理分支。	READY
9540_facelift	9540	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理分支。	READY
9542_prefl	9542	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH	改款前物理分支。	READY
9542_facelift	9542	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
9543	9543	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9544	9544	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9545	9545	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9546	9546	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9547	9547	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9548	9548	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9552	9552	Hatchback	Shuma I	FB	5	EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	HIGH		READY
9553	9553	Hatchback	Shuma I	FB	5	EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	HIGH		READY
9557	9557	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
9558	9558	Wagon	Taunus TC2		5	EU-FORD-TAUNUS-TC2-WAGON-01	HIGH		READY
9585	9585	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9586	9586	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9592	9592	Hatchback	Volt I		5	EU-CHEVROLET-VOLT-I-HATCHBACK-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-COUGAR-BCV-COUPE-3D-01	4700	1770	1320	Auto-Data Ford Cougar BCV 2.5i V6 24V	https://www.auto-data.net/en/ford-cougar-bcv-2.5i-v6-24v-170hp-8019
EU-CHRYSLER-300M-LH-SEDAN-4D-01	5000	1892	1416	Automobile-Catalog 1998 Chrysler 300M 3.5 V6	https://www.automobile-catalog.com/car/1998/520280/chrysler_300m_3_5_v6.html
EU-LANCIA-KAPPA-838-SEDAN-02	4687	1826	1462	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-LANCIA-KAPPA-838-COUPE-2D-01	4567	1830	1425	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-LANCIA-KAPPA-838-WAGON-5D-01	4687	1826	1462	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-BMW-Z3-M-E36-8-COUPE-3D-01	4025	1740	1279	Auto-Data BMW Z3 M Coupe E36/8 3.2 321 Hp	https://www.auto-data.net/en/bmw-z3-m-coupe-e36-8-3.2-321hp-9921
EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	4354	1698	1420	Automobile-Catalog 1998 Citroen Xsara Break 1.9 D SX	https://www.automobile-catalog.com/car/1998/546875/citroen_xsara_break_1_9_d_sx.html
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380	Auto-Data Mercedes-Benz CLK A208 CLK 200	https://www.auto-data.net/en/mercedes-benz-clk-a208-clk-200-136hp-23446
EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	4720	1820	1410	Auto-Data Volvo C70 Convertible 2.0 20V	https://www.auto-data.net/en/volvo-c70-convertible-2.0-20v-180hp-9498
EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-01	4511	1731	1448	Automobile-Catalog 1998 Skoda Octavia Combi 1.9 TDI 90	https://www.automobile-catalog.com/car/1998/3134645/skoda_octavia_combi_1_9_tdi_90.html
EU-CADILLAC-SRX-II-SUV-5D-01	4834	1912	1670	Automobile-Catalog 2010 Cadillac SRX 3.0L V6 AWD	https://www.automobile-catalog.com/car/2010/1200710/cadillac_srx_3_0l_v-6_di_awd.html
EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	4425	1695	1440	Automobile-Catalog 1998 Honda Civic Aerodeck 1.4i S	https://www.automobile-catalog.com/car/1998/1118330/honda_civic_aerodeck_1_4i_s.html
EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	4475	1700	1410	Automobile-Catalog 1997 Kia Shuma 1.5 GX Di	https://www.automobile-catalog.com/car/1997/1344830/kia_shuma_1_5_gx_di.html
EU-CHEVROLET-VOLT-I-HATCHBACK-5D-01	4498	1788	1430	Automobile-Catalog 2011 Chevrolet Volt	https://www.automobile-catalog.com/car/2011/1207475/chevrolet_volt.html
```

## 下一步优先处理

1. 集中处理 Piaggio Porter/Ape 的 Bus、Pickup/Chassis、Van 与 Cabriolet 物理分支。
2. 核对 Hyundai H-1/Starex、Nissan Pathfinder II、Toyota Hilux VI、Bedford Blitz 和 Caterham Seven 的轴距、车顶或车身版本边界。
3. 补齐 Octavia I Wagon 跨改款、Buick Skylark、Carisma Sedan、Shuma Sedan、Land Cruiser 100、Lexus GS/LS、RAV4 Cabrio 和 Paseo Cabrio。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification "Lancia K '98 - TECHNICAL SPECIFICATION | Lancia | Stellantis Media"
[2]: https://www.auto-data.net/en/ford-cougar-bcv-2.5i-v6-24v-170hp-8019 "Ford Cougar (BCV) 2.5i V6 24V (170 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1998/546875/citroen_xsara_break_1_9_d_sx.html?utm_source=chatgpt.com "1998 Citroen Xsara Break 1.9 D SX (man. 5) - Automobile Catalog"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 Octavia I Combi、Buick Skylark VII、Carisma Sedan、Shuma Sedan、Land Cruiser 100、Lexus GS/LS、RAV4 Cabrio 与 Paseo Cabrio，共解决 16 个 PENDING Ktype。
* 修正上一轮 Octavia I Combi 改款前尺寸组：前驱车型三维确认为 `4511×1731×1457 mm`。按冲突规则未覆盖旧组，创建 `EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02`，并同步修改 Ktype `9516` 的引用。([汽车数据网][1])
* Octavia I Combi 改款后前驱外廓闭合为 `4513×1731×1457 mm`；Carisma Sedan 按改款前后拆分为 `4435×1710×1405 mm` 与 `4475×1710×1405 mm`。([汽车数据网][2])
* Land Cruiser J100 按 2002 年改款拆分高度；Lexus GS I、GS II、LS II facelift 及两款 Toyota 敞篷车尺寸已闭合。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* READY 映射行：90
* PENDING 输入 Ktype：26
* 当前映射引用的已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9515_prefl	9515	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9515_facelift	9515	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9516	9516	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	修正改款前尺寸组引用。	READY
9517_prefl	9517	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9517_facelift	9517	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9518_prefl	9518	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9518_facelift	9518	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9519_prefl	9519	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9519_facelift	9519	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9534	9534	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
9535	9535	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
9541_prefl	9541	Sedan	Carisma	DA	4	EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-PREFL-01	HIGH	改款前物理分支。	READY
9541_facelift	9541	Sedan	Carisma	DA	4	EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-FACELIFT-01	HIGH	改款后物理分支。	READY
9550	9550	Sedan	Shuma I	FB	4	EU-KIA-SHUMA-I-FB-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
9559_prefl	9559	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	HIGH	2002年改款前物理分支。	READY
9559_facelift	9559	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	HIGH	2002年改款后物理分支。	READY
9560_prefl	9560	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	HIGH	2002年改款前物理分支。	READY
9560_facelift	9560	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	HIGH	2002年改款后物理分支。	READY
9562	9562	Sedan	GS I	S140	4	EU-LEXUS-GS-I-S140-SEDAN-4D-01	HIGH		READY
9563	9563	Sedan	GS II	S160	4	EU-LEXUS-GS-II-S160-SEDAN-4D-01	HIGH		READY
9564	9564	Sedan	LS II	XF20	4	EU-LEXUS-LS-II-XF20-SEDAN-FACELIFT-01	HIGH	1997年后期改款外廓。	READY
9565	9565	Convertible	RAV4 I	XA10	3	EU-TOYOTA-RAV4-I-XA10-CONVERTIBLE-3D-01	HIGH	软顶三门物理外廓。	READY
9568	9568	Convertible	Paseo	L5	2	EU-TOYOTA-PASEO-L5-CONVERTIBLE-2D-01	HIGH		READY
9569	9569	Sedan	GS II	S160	4	EU-LEXUS-GS-II-S160-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	4511	1731	1457	Auto-Data Skoda Octavia I Combi Tour 1.9 TDI 110 Hp	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-1.9-tdi-110hp-14262
EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	4513	1731	1457	Auto-Data Skoda Octavia I Combi Tour facelift 1.9 SDI 68 Hp	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-facelift-2000-1.9-sdi-68hp-56469
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4808	1717	1361	Automobile-Catalog 1997 Buick Skylark Limited Sedan 2.4L Twin Cam	https://www.automobile-catalog.com/car/1997/323105/buick_skylark_limited_sedan_2_4l_twin_cam.html
EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-PREFL-01	4435	1710	1405	Auto-Data Mitsubishi Carisma Sedan 1.8 16V GDI 125 Hp	https://www.auto-data.net/en/mitsubishi-carisma-1.8-16v-gdi-125hp-15549
EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-FACELIFT-01	4475	1710	1405	Auto-Data Mitsubishi Carisma Sedan 1.8 16V GDI 122 Hp	https://www.auto-data.net/en/mitsubishi-carisma-1.8-16v-gdi-122hp-15548
EU-KIA-SHUMA-I-FB-SEDAN-4D-01	4427	1711	1413	Automobile-Catalog 1999 Kia Shuma 1.5 LS 4-dr	https://www.automobile-catalog.com/car/1999/1344740/kia_shuma_1_5_ls_4-dr.html
EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	4890	1940	1860	Auto-Data Toyota Land Cruiser J100	https://www.auto-data.net/en/toyota-land-cruiser-j100-generation-930
EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	4890	1940	1880	Auto-Data Toyota Land Cruiser J100 facelift 2002	https://www.auto-data.net/en/toyota-land-cruiser-j100-facelift-2002-generation-9133
EU-LEXUS-GS-I-S140-SEDAN-4D-01	4950	1795	1400	Auto-Data Lexus GS I 300	https://www.auto-data.net/en/lexus-gs-i-300-223hp-automatic-5919
EU-LEXUS-GS-II-S160-SEDAN-4D-01	4805	1800	1445	Auto-Data Lexus GS II	https://www.auto-data.net/en/lexus-gs-ii-generation-1364
EU-LEXUS-LS-II-XF20-SEDAN-FACELIFT-01	4995	1830	1435	Auto-Data Lexus LS II facelift 400 V8 284 Hp	https://www.auto-data.net/en/lexus-ls-ii-facelift-1998-400-v8-284hp-automatic-36920
EU-TOYOTA-RAV4-I-XA10-CONVERTIBLE-3D-01	3715	1695	1660	Auto-Data Toyota RAV4 I Soft top XA10	https://www.auto-data.net/en/toyota-rav4-i-soft-top-xa10-generation-978
EU-TOYOTA-PASEO-L5-CONVERTIBLE-2D-01	4160	1660	1320	Auto-Data Toyota Paseo Cabrio L5	https://www.auto-data.net/en/toyota-paseo-cabrio-l5-generation-786
```

## 下一步优先处理

1. 批量闭合 Piaggio Porter 与 Ape 的 Bus、Van、Pickup/Chassis 和开放式驾驶室分支。
2. 集中核对 Pathfinder II 与 Hyundai H-1/Starex 的改款、轴距及车身长度边界。
3. 最后处理 Hilux VI、Bedford Blitz/CF 与 Caterham Seven 的多车身或多底盘分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/skoda-octavia-i-combi-tour-1.9-tdi-110hp-14262?utm_source=chatgpt.com "Skoda Octavia I Combi Tour 1.9 TDI (110 Hp) - Auto-Data.net"
[2]: https://www.auto-data.net/en/skoda-octavia-i-combi-tour-facelift-2000-1.9-sdi-68hp-56469?utm_source=chatgpt.com "Skoda Octavia I Combi Tour (facelift 2000) 1.9 SDI (68 Hp)"
[3]: https://www.auto-data.net/en/toyota-land-cruiser-j100-facelift-2002-generation-9133 "Toyota Land Cruiser (J100, facelift 2002) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* Piaggio Porter 2011 Bus 与 11 kW ElectricPower Window Van 外廓已确认，5 个 Ktype 复用既有 `3400×1395×1870 mm` 尺寸组，不重复建组。
* Piaggio Ape Classic 的 8 kW 与 6 kW 版本共用同一 Pickup 外廓，首次创建 Ape Classic 尺寸组。
* Hyundai H-1/Starex 第一代 2.4 4WD 与 2.5 TD 4WD 已归入相同 A1 Bus 外廓，首次创建尺寸组。([汽车目录][1])
* Caterham Seven 2.0 178 hp 已按 S3 标准底盘和 SV 宽体底盘拆分，直接复用两个既有 Roadsport 尺寸组。([autoevolution][2])
* 本轮新增解决 10 个 PENDING Ktype；Ape TM、Calessino、Pathfinder II、Hilux VI 与 Bedford CF/Blitz 尚待闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：84
* READY 映射行：101
* PENDING 输入 Ktype：16
* 当前映射引用的已确认尺寸组：54
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9482	9482	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9483	9483	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9484	9484	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9485	9485	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9492	9492	MPV	Porter I ElectricPower			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	11 kW ElectricPower Window Van外廓。	READY
9496	9496	Pickup	Ape Classic		2	EU-PIAGGIO-APE-CLASSIC-PICKUP-01	HIGH		READY
9498	9498	Pickup	Ape Classic		2	EU-PIAGGIO-APE-CLASSIC-PICKUP-01	HIGH		READY
9554	9554	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-4D-01	HIGH		READY
9555	9555	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-4D-01	HIGH		READY
9591_s3	9591	Convertible	Seven Roadsport 175	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	HIGH	S3标准底盘物理分支。	READY
9591_sv	9591	Convertible	Seven Roadsport 175	SV	2	EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	HIGH	SV宽体底盘物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PIAGGIO-APE-CLASSIC-PICKUP-01	3145	1465	1635	Piaggio Ape Classic official brochure	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-Classic-E4-Brochure-2017-EN-1.pdf
EU-HYUNDAI-H1-I-A1-MPV-4D-01	4695	1820	1885	Automobile-Catalog Hyundai Starex 2400 HSV 4x4; Automobile-Catalog Hyundai H-1 Starex 2.5 TD	https://www.automobile-catalog.com/car/1998/1167770/hyundai_starex_2400_hsv_4x4.html;https://www.automobile-catalog.com/car/1998/1167800/hyundai_h-1_starex_2_5_td_automatic.html
```

## 下一步优先处理

1. 闭合 Ape TM Deck、Long Deck、Van 的早期与后期外廓边界，并确认 Calessino 宽度不含后视镜口径。
2. 拆分 Pathfinder II 改款及市场尺寸分支，并确认 Hilux VI 各 RZN 车身代码对应的 Cab 外廓。
3. 处理 Bedford CF/Blitz 的短轴、长轴和不同车顶 Van 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1998/1167770/hyundai_starex_2400_hsv_4x4.html?utm_source=chatgpt.com "1998 Hyundai Starex 2400 HSV 4x4 Specs Review (81 kW ..."
[2]: https://www.autoevolution.com/cars/caterham-roadsport-2007.html?utm_source=chatgpt.com "2007 Caterham Seven Roadsport Specs, Performance & ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Piaggio Ape TM Van 两个 Ktype，首次建立统一厢式尺寸组 `3210×1480×1780 mm`。([皮亚乔商用车][1])
* 分别闭合 Ape Calessino 422 cc Diesel 与 Electric Lithium；两者长宽相同，但官方资料显示高度分别为 1770 mm 和 1750 mm，因此独立建组。([意大利速度][2])
* Nissan Pathfinder II 的 3.3 V6、2.7 TD 与 3.2 TD 均确认对应 R50 五门外廓 `4530×1840×1750 mm`，三个 Ktype 共用一个尺寸组。([汽车数据网][3])
* 本轮新增解决 7 个 PENDING Ktype；剩余 9 个集中在 Ape TM Platform/Chassis、Hilux VI 和 Bedford CF/Blitz。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：91
* READY 映射行：108
* PENDING 输入 Ktype：9
* 当前映射引用的已确认尺寸组：58
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9489	9489	Van	Ape TM			EU-PIAGGIO-APE-TM-VAN-01	MEDIUM		READY
9490	9490	Van	Ape TM			EU-PIAGGIO-APE-TM-VAN-01	MEDIUM		READY
9525	9525	Convertible	Ape Calessino 2007	ZAPT2D4MC		EU-PIAGGIO-APE-CARESSINO-2007-CONVERTIBLE-DIESEL-01	HIGH	Diesel车身高度分支。	READY
9526	9526	Convertible	Ape Calessino Electric Lithium			EU-PIAGGIO-APE-CARESSINO-2009-CONVERTIBLE-ELECTRIC-01	HIGH	Electric Lithium车身高度分支。	READY
9549	9549	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
9551	9551	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
9556	9556	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PIAGGIO-APE-TM-VAN-01	3210	1480	1780	Piaggio Ape range official brochure	https://www.pojazdyuzytkowe.piaggio.com/brochures/vtl_ape.pdf
EU-PIAGGIO-APE-CARESSINO-2007-CONVERTIBLE-DIESEL-01	2940	1465	1770	Piaggio Ape Calessino 2007 technical specifications via ItaliaSpeed	https://www.italiaspeed.com/2007/cars/other/piaggio/07/ape_calessino/0207.html
EU-PIAGGIO-APE-CARESSINO-2009-CONVERTIBLE-ELECTRIC-01	2940	1465	1750	Piaggio Group Ape Calessino Electric Lithium technical specifications	https://www.piaggiogroup.com/sites/default/files/news/ape_calessino_2009_eng.pdf
EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	4530	1840	1750	Auto-Data Nissan Pathfinder II 3.3 V6;Auto-Data Nissan Pathfinder II 2.7 TD;Auto-Data Nissan Pathfinder II 3.2 TD	https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930;https://www.auto-data.net/en/nissan-pathfinder-ii-2.7-td-131hp-4wd-928;https://www.auto-data.net/en/nissan-pathfinder-ii-3.2-td-150hp-4wd-929
```

## 下一步优先处理

1. 处理 Ktype `9486`、`9488` 覆盖的 Ape TM Platform/Chassis 标准平台、长平台及翻斗外廓冲突。
2. 确认 Ktype `9561` 所含 Hilux VI `RZN14_ / RZN16_ / RZN19_` 对应的驾驶室和车身长度分支。
3. 批量闭合 Ktype `9578–9583` Bedford CF/Blitz 的 SWB、LWB、facelift 与 CF2 Van 分支。

推进信号：CONTINUE

[1]: https://www.pojazdyuzytkowe.piaggio.com/brochures/vtl_ape.pdf?utm_source=chatgpt.com "Ape range"
[2]: https://www.italiaspeed.com/2007/cars/other/piaggio/07/ape_calessino/0207.html?utm_source=chatgpt.com "The Piaggio-built Ape a very special ..."
[3]: https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930?utm_source=chatgpt.com "Nissan Pathfinder II 3.3 V6 (170 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* `9486`、`9488` 不能合并为单一 Ape TM Pickup 尺寸组。资料确认其平台/底盘系列包含标准货斗、长货斗、翻斗及底盘等不同外廓，长度、宽度存在差异，暂保留基础 PENDING 行，避免猜测性派生。([Scribd][1])
* `9561` 覆盖 `RZN14_ / RZN16_ / RZN19_`，且生产期横跨第六代 Hilux 外廓调整；Toyota 官方资料显示 2000 与 2001 改款后的 Double Cab 长度、宽度发生变化，当前尚不能确定该 Ktype 覆盖的全部 Cab/宽体分支。([Autodoc][2])
* Bedford CF/Blitz 已确认存在 106 英寸与126 英寸标准厢式轴距，部分发动机覆盖多个载重级别；当前阻塞点缩小为各发动机 Ktype 与 SWB/LWB、CF1/CF2 的具体适用关系。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：91
* PENDING 输入 Ktype：9
* READY 映射行：108
* PENDING 映射行：9
* 已确认尺寸组：58
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9486	9486	Pickup	Ape TM		2		LOW	Pritsche/Fahrgestell包含标准货斗、长货斗及底盘候选，尚未完成物理分支拆分。	PENDING: 需确认各量产平台或底盘分支及对应三维。
9488	9488	Pickup	Ape TM		2		LOW	Pritsche/Fahrgestell包含标准货斗、长货斗及底盘候选，柴油版本另有外廓差异。	PENDING: 需确认柴油平台或底盘分支及对应三维。
9561	9561	Pickup	Hilux VI			LOW	覆盖RZN14_、RZN16_、RZN19_并跨改款，Cab及普通或宽体边界尚未闭合。	PENDING: 需确认完整Cab、车身代码及改款外廓分支。
9578	9578	Van	Bedford CF			LOW	生产期覆盖CF1与CF2，短轴或长轴适用范围尚未闭合。	PENDING: 需确认1.8发动机对应的厢式轴距分支。
9579	9579	Van	Bedford CF2			LOW	CF2厢式车存在不同轴距，当前发动机与车身级别对应关系未闭合。	PENDING: 需确认2.0汽油发动机对应的SWB或LWB分支。
9580	9580	Van	Bedford CF			LOW	2.3D生产期跨改款并存在短轴或长轴候选。	PENDING: 需确认2.3D各轴距及CF1或CF2分支。
9581	9581	Van	Bedford CF			LOW	2.1D对应的载重级别和厢式轴距边界尚未闭合。	PENDING: 需确认2.1D适用的标准厢式车分支。
9582	9582	Van	Bedford CF1			LOW	2.0D存在不同载重级别和轴距候选。	PENDING: 需确认2.0D对应的SWB或LWB外廓。
9583	9583	Van	Bedford CF1			LOW	2.3汽油版本存在短轴或长轴厢式候选。	PENDING: 需确认2.3汽油发动机对应的轴距分支。
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

集中闭合 Bedford CF/Blitz 的标准 SWB、LWB 厢式尺寸及六个发动机 Ktype 的适用关系；随后按同样方式拆分 Ape TM 平台/底盘与 Hilux VI 改款前后 Cab 分支。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/527559817/Ape?utm_source=chatgpt.com "Manuale Stazione Di Servizio: APE TM Benzina | PDF - Scribd"
[2]: https://www.autodoc24.fr/car-parts/engine-oil-12094/toyota/hilux-pick-up/hilux-vi-pickup-n1/9561-2-4-i-4wd-rzn14-rzn16-rzn19?utm_source=chatgpt.com "Engine oil TOYOTA Hilux VI Pickup 2.4 i 4WD 140 hp Petrol 103 kW ..."
[3]: https://en.wikipedia.org/wiki/Bedford_CF?utm_source=chatgpt.com "Bedford CF"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Ktype `9486`、`9488` 已按 `Pritsche/Fahrgestell` 的实际外廓拆为标准货斗、长货斗、短底盘和长底盘四个分支；汽油与柴油版本复用相同的四个尺寸组。
* Piaggio Ape TM 官方使用手册分别列明：标准货斗 `3175×1480×1630 mm`、长货斗 `3390×1500×1630 mm`，Motor Chassis 则有 `3150 mm` 与 `3210 mm` 两种长度，宽高均为 `1455×1630 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：93
* PENDING 输入 Ktype：7
* READY 映射行：116
* PENDING 映射行：7
* 已确认尺寸组：62
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9486_deck	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-DECK-01	MEDIUM	标准货斗分支。	READY
9486_longdeck	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	MEDIUM	长货斗分支。	READY
9486_chassis_short	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	MEDIUM	短外廓底盘分支。	READY
9486_chassis_long	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	MEDIUM	长外廓底盘分支。	READY
9488_deck	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-DECK-01	MEDIUM	标准货斗分支。	READY
9488_longdeck	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	MEDIUM	长货斗分支。	READY
9488_chassis_short	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	MEDIUM	短外廓底盘分支。	READY
9488_chassis_long	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	MEDIUM	长外廓底盘分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PIAGGIO-APE-TM-PICKUP-DECK-01	3175	1480	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	3390	1500	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	3150	1455	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	3210	1455	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
```

## 下一步优先处理

优先拆分 Ktype `9561` 的 Hilux VI Cab、普通车身/宽体及改款分支；随后集中闭合 Ktype `9578–9583` 的 Bedford CF/Blitz SWB、LWB 和 CF1/CF2 外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Ktype `9578–9583` 的 Bedford CF/Blitz 厢式车分支。
* 官方规格区分短轴整体厢式车 `4410×1950×1980 mm` 与长轴整体厢式车 `4920×1950×2160 mm`，宽度均为明确不含后视镜口径。
* `1.8` 汽油版本仅建立短轴分支；其余五个发动机 Ktype 按适用范围拆为短轴和长轴分支。([维基百科][1])
* 当前仅剩 Ktype `9561` Hilux VI 的 Single Cab、Double Cab、改款及宽体边界尚未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* PENDING 输入 Ktype：1
* READY 映射行：127
* PENDING 映射行：1
* 已确认尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9578_swb	9578	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	HIGH	1.8L短轴整体厢式外廓。	READY
9579_swb	9579	Van	Bedford CF2			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9579_lwb	9579	Van	Bedford CF2			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9580_swb	9580	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9580_lwb	9580	Van	Bedford CF			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9581_swb	9581	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9581_lwb	9581	Van	Bedford CF			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9582_swb	9582	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9582_lwb	9582	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9583_swb	9583	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9583_lwb	9583	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BEDFORD-CF-VAN-SWB-01	4410	1950	1980	Bedford CF2 Specifications and Dimensions official brochure	https://www.bedfordcf.co.uk/br/br26_p4.jpg
EU-BEDFORD-CF-VAN-LWB-01	4920	1950	2160	Bedford CF2 Specifications and Dimensions official brochure	https://www.bedfordcf.co.uk/br/br26_p6.jpg
```

## 下一步优先处理

闭合 Ktype `9561` 的 Hilux VI Single Cab、Double Cab、改款前后及宽体 Double Cab 物理外廓分支；完成后立即执行机械检查并输出两张最终完整 TSV 和指定下载链接。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Bedford_CF?utm_source=chatgpt.com "Bedford CF"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8501-8600_ktype_dimension_mapping_final.tsv
- all_8501-8600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Ktype `9561` 已按改款前后、Single Cab/Double Cab，以及改款后是否配后踏步保险杠拆分为 6 个确定外廓。改款前尺寸为长度 4725 mm、宽度 1690 mm，高度按驾驶室分别为 1760/1800 mm；改款后长度为 4785 mm 或带后踏步保险杠的 4915 mm，宽度 1700 mm，高度分别为 1765/1795 mm。([Toyota Media Site][1])
* PENDING 已清零。
* 已完成机械检查：映射表 133 个唯一 `id`，覆盖全部 100 个输入 Ktype；尺寸组表包含 70 个唯一尺寸组；全部引用闭合，无孤立组，长宽高、来源和 URL 均非空。
* 已生成两个任务指定文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：133
* PENDING 映射：0
* 已确认尺寸组：70
* 映射引用闭合：是
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9466_3dr	9466	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9466_5dr	9466	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9467_3dr	9467	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9467_5dr	9467	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9468_3dr	9468	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9468_5dr	9468	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9469	9469	Coupe	Cougar	BCV	3	EU-FORD-COUGAR-BCV-COUPE-3D-01	HIGH		READY
9470	9470	Coupe	Cougar	BCV	3	EU-FORD-COUGAR-BCV-COUPE-3D-01	HIGH		READY
9471	9471	Sedan	300M	LH	4	EU-CHRYSLER-300M-LH-SEDAN-4D-01	HIGH		READY
9472	9472	Sedan	300M	LH	4	EU-CHRYSLER-300M-LH-SEDAN-4D-01	HIGH		READY
9473	9473	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-02	HIGH	既有同名组尺寸冲突，改用新序号。	READY
9474	9474	Coupe	Kappa	838	2	EU-LANCIA-KAPPA-838-COUPE-2D-01	HIGH		READY
9475	9475	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-5D-01	HIGH		READY
9476	9476	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-02	HIGH	既有同名组尺寸冲突，改用新序号。	READY
9477	9477	Wagon	Kappa	838	5	EU-LANCIA-KAPPA-838-WAGON-5D-01	HIGH		READY
9479	9479	Coupe	Z3 M Coupe	E36/8	3	EU-BMW-Z3-M-E36-8-COUPE-3D-01	HIGH		READY
9480	9480	Hatchback	Xsara I	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	HIGH		READY
9481	9481	Wagon	Xsara I	N2	5	EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	HIGH		READY
9482	9482	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9483	9483	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9484	9484	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9485	9485	MPV	Porter I Facelift			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	Window Van客运外廓。	READY
9486_deck	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-DECK-01	MEDIUM	标准货斗分支。	READY
9486_longdeck	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	MEDIUM	长货斗分支。	READY
9486_chassis_short	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	MEDIUM	短外廓底盘分支。	READY
9486_chassis_long	9486	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	MEDIUM	长外廓底盘分支。	READY
9488_deck	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-DECK-01	MEDIUM	标准货斗分支。	READY
9488_longdeck	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	MEDIUM	长货斗分支。	READY
9488_chassis_short	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	MEDIUM	短外廓底盘分支。	READY
9488_chassis_long	9488	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	MEDIUM	长外廓底盘分支。	READY
9489	9489	Van	Ape TM			EU-PIAGGIO-APE-TM-VAN-01	MEDIUM		READY
9490	9490	Van	Ape TM			EU-PIAGGIO-APE-TM-VAN-01	MEDIUM		READY
9491_prefl	9491	SUV	Yeti	5L	5	EU-SKODA-YETI-5L-SUV-PREFL-01	HIGH	改款前物理分支。	READY
9491_facelift	9491	SUV	Yeti	5L	5	EU-SKODA-YETI-5L-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
9492	9492	MPV	Porter I ElectricPower			EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	HIGH	11 kW ElectricPower Window Van外廓。	READY
9496	9496	Pickup	Ape Classic		2	EU-PIAGGIO-APE-CLASSIC-PICKUP-01	HIGH		READY
9498	9498	Pickup	Ape Classic		2	EU-PIAGGIO-APE-CLASSIC-PICKUP-01	HIGH		READY
9499	9499	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9500	9500	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9501	9501	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9502	9502	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9503	9503	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
9504	9504	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
9505	9505	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH		READY
9506	9506	Hatchback	146	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
9507	9507	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9508	9508	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9509	9509	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9510	9510	Convertible	C70 I	P80	2	EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	HIGH		READY
9511_3dr	9511	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9511_5dr	9511	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9512_3dr	9512	Hatchback	306 Facelift		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9512_5dr	9512	Hatchback	306 Facelift		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9513	9513	Sedan	306 Facelift	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
9514	9514	Wagon	306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
9515_prefl	9515	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9515_facelift	9515	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9516	9516	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	修正改款前尺寸组引用。	READY
9517_prefl	9517	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9517_facelift	9517	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9518_prefl	9518	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9518_facelift	9518	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9519_prefl	9519	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	HIGH	改款前物理分支。	READY
9519_facelift	9519	Wagon	Octavia I	1U5	5	EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
9520	9520	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9521	9521	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9522	9522	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9523	9523	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9524	9524	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH		READY
9525	9525	Convertible	Ape Calessino 2007	ZAPT2D4MC		EU-PIAGGIO-APE-CARESSINO-2007-CONVERTIBLE-DIESEL-01	HIGH	Diesel车身高度分支。	READY
9526	9526	Convertible	Ape Calessino Electric Lithium			EU-PIAGGIO-APE-CARESSINO-2009-CONVERTIBLE-ELECTRIC-01	HIGH	Electric Lithium车身高度分支。	READY
9533	9533	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH		READY
9534	9534	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
9535	9535	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
9536	9536	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-5D-01	HIGH		READY
9537	9537	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-5D-01	HIGH		READY
9538	9538	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9539_3dr	9539	Hatchback	Micra II	K11	3	EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	三门物理分支，共用同一尺寸组。	READY
9539_5dr	9539	Hatchback	Micra II	K11	5	EU-NISSAN-MICRA-II-K11-HATCHBACK-01	HIGH	五门物理分支，共用同一尺寸组。	READY
9540_prefl	9540	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	HIGH	改款前物理分支。	READY
9540_facelift	9540	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理分支。	READY
9541_prefl	9541	Sedan	Carisma	DA	4	EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-PREFL-01	HIGH	改款前物理分支。	READY
9541_facelift	9541	Sedan	Carisma	DA	4	EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-FACELIFT-01	HIGH	改款后物理分支。	READY
9542_prefl	9542	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH	改款前物理分支。	READY
9542_facelift	9542	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
9543	9543	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9544	9544	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9545	9545	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9546	9546	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9547	9547	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9548	9548	Wagon	Civic VI Aerodeck		5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH		READY
9549	9549	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
9550	9550	Sedan	Shuma I	FB	4	EU-KIA-SHUMA-I-FB-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
9551	9551	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
9552	9552	Hatchback	Shuma I	FB	5	EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	HIGH		READY
9553	9553	Hatchback	Shuma I	FB	5	EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	HIGH		READY
9554	9554	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-4D-01	HIGH		READY
9555	9555	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-4D-01	HIGH		READY
9556	9556	SUV	Pathfinder II	R50	5	EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	HIGH		READY
9557	9557	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
9558	9558	Wagon	Taunus TC2		5	EU-FORD-TAUNUS-TC2-WAGON-01	HIGH		READY
9559_prefl	9559	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	HIGH	2002年改款前物理分支。	READY
9559_facelift	9559	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	HIGH	2002年改款后物理分支。	READY
9560_prefl	9560	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	HIGH	2002年改款前物理分支。	READY
9560_facelift	9560	SUV	Land Cruiser 100	J100	5	EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	HIGH	2002年改款后物理分支。	READY
9561_single_prefl	9561	Pickup	Hilux VI	RZN168	2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-PREFL-01	HIGH	改款前Single Cab外廓。	READY
9561_double_prefl	9561	Pickup	Hilux VI	RZN168	4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-PREFL-01	HIGH	改款前Double Cab外廓。	READY
9561_single_facelift	9561	Pickup	Hilux VI	RZN168	2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	HIGH	改款后Single Cab标准后部外廓。	READY
9561_single_facelift_step	9561	Pickup	Hilux VI	RZN168	2	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	HIGH	改款后Single Cab后踏步保险杠外廓。	READY
9561_double_facelift	9561	Pickup	Hilux VI	RZN168	4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	HIGH	改款后Double Cab标准后部外廓。	READY
9561_double_facelift_step	9561	Pickup	Hilux VI	RZN168	4	EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	HIGH	改款后Double Cab后踏步保险杠外廓。	READY
9562	9562	Sedan	GS I	S140	4	EU-LEXUS-GS-I-S140-SEDAN-4D-01	HIGH		READY
9563	9563	Sedan	GS II	S160	4	EU-LEXUS-GS-II-S160-SEDAN-4D-01	HIGH		READY
9564	9564	Sedan	LS II	XF20	4	EU-LEXUS-LS-II-XF20-SEDAN-FACELIFT-01	HIGH	1997年后期改款外廓。	READY
9565	9565	Convertible	RAV4 I	XA10	3	EU-TOYOTA-RAV4-I-XA10-CONVERTIBLE-3D-01	HIGH	软顶三门物理外廓。	READY
9568	9568	Convertible	Paseo	L5	2	EU-TOYOTA-PASEO-L5-CONVERTIBLE-2D-01	HIGH		READY
9569	9569	Sedan	GS II	S160	4	EU-LEXUS-GS-II-S160-SEDAN-4D-01	HIGH		READY
9578_swb	9578	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	HIGH	1.8L短轴整体厢式外廓。	READY
9579_swb	9579	Van	Bedford CF2			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9579_lwb	9579	Van	Bedford CF2			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9580_swb	9580	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9580_lwb	9580	Van	Bedford CF			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9581_swb	9581	Van	Bedford CF			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9581_lwb	9581	Van	Bedford CF			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9582_swb	9582	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9582_lwb	9582	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9583_swb	9583	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-SWB-01	MEDIUM	短轴整体厢式外廓。	READY
9583_lwb	9583	Van	Bedford CF1 Facelift			EU-BEDFORD-CF-VAN-LWB-01	MEDIUM	长轴整体厢式外廓。	READY
9585	9585	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9586	9586	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
9591_s3	9591	Convertible	Seven Roadsport 175	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	HIGH	S3标准底盘物理分支。	READY
9591_sv	9591	Convertible	Seven Roadsport 175	SV	2	EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	HIGH	SV宽体底盘物理分支。	READY
9592	9592	Hatchback	Volt I		5	EU-CHEVROLET-VOLT-I-HATCHBACK-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8501-8600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426	Auto-Data Peugeot 206 1.1i 60 Hp	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426	Auto-Data Peugeot 206 1.1i 60 Hp	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-FORD-COUGAR-BCV-COUPE-3D-01	4700	1770	1320	Auto-Data Ford Cougar BCV 2.5i V6 24V	https://www.auto-data.net/en/ford-cougar-bcv-2.5i-v6-24v-170hp-8019
EU-CHRYSLER-300M-LH-SEDAN-4D-01	5000	1892	1416	Automobile-Catalog 1998 Chrysler 300M 3.5 V6	https://www.automobile-catalog.com/car/1998/520280/chrysler_300m_3_5_v6.html
EU-LANCIA-KAPPA-838-SEDAN-02	4687	1826	1462	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-LANCIA-KAPPA-838-COUPE-2D-01	4567	1830	1425	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-LANCIA-KAPPA-838-WAGON-5D-01	4687	1826	1462	Lancia K '98 official technical specification	https://www.media.stellantis.com/em-en/lancia/press/lancia-k-98-technical-specification
EU-BMW-Z3-M-E36-8-COUPE-3D-01	4025	1740	1279	Auto-Data BMW Z3 M Coupe E36/8 3.2 321 Hp	https://www.auto-data.net/en/bmw-z3-m-coupe-e36-8-3.2-321hp-9921
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405	Automobile-Catalog 1997 Citroen Xsara 1.8i SX	https://www.automobile-catalog.com/car/1997/546410/citroen_xsara_1_8i_sx.html
EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	4354	1698	1420	Automobile-Catalog 1998 Citroen Xsara Break 1.9 D SX	https://www.automobile-catalog.com/car/1998/546875/citroen_xsara_break_1_9_d_sx.html
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-02	3400	1395	1870	Piaggio Porter Electric Power official brochure	https://piaggiocommercialuk.com/wp-content/uploads/2018/02/Brochure-Porter_Electric-Power.pdf
EU-PIAGGIO-APE-TM-PICKUP-DECK-01	3175	1480	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-LONGDECK-01	3390	1500	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-SHORT-01	3150	1455	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-LONG-01	3210	1455	1630	Piaggio Ape TM / Ape TM Diesel official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-VAN-01	3210	1480	1780	Piaggio Ape range official brochure	https://www.pojazdyuzytkowe.piaggio.com/brochures/vtl_ape.pdf
EU-SKODA-YETI-5L-SUV-PREFL-01	4223	1793	1691	Škoda Auto Annual Report 2009	https://cdn.skoda-storyboard.com/2016/05/skoda-auto-annual-report-2009.pdf
EU-SKODA-YETI-5L-SUV-FACELIFT-01	4222	1793	1691	ŠKODA YETI technical data	https://cdn.skoda-storyboard.com/2016/12/TD_YETI_en.pdf
EU-PIAGGIO-APE-CLASSIC-PICKUP-01	3145	1465	1635	Piaggio Ape Classic official brochure	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-Classic-E4-Brochure-2017-EN-1.pdf
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380	Auto-Data Mercedes-Benz CLK A208 CLK 200	https://www.auto-data.net/en/mercedes-benz-clk-a208-clk-200-136hp-23446
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427	Automobile-Catalog 1996 Alfa Romeo 145 1.8 Twin Spark 16V	https://www.automobile-catalog.com/car/1996/218150/alfa_romeo_145_1_8_twin_spark_16v.html
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425	Auto-Data Alfa Romeo 146 930 facelift 1997	https://www.auto-data.net/en/alfa-romeo-146-930-facelift-1997-generation-7922
EU-VOLVO-C70-I-P80-CONVERTIBLE-2D-01	4720	1820	1410	Auto-Data Volvo C70 Convertible 2.0 20V	https://www.auto-data.net/en/volvo-c70-convertible-2.0-20v-180hp-9498
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI 90 Hp 4motion	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-4motion-8678
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI 90 Hp 4motion	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-4motion-8678
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380	Auto-Data Peugeot 306 Hatchback facelift 1997	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380	Auto-Data Peugeot 306 Hatchback facelift 1997	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386	Automobile-Catalog Peugeot 306 Sedan facelift	https://www.automobile-catalog.com/model/peugeot/306_2gen.html
EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	4338	1689	1415	Automobile-Catalog 1998 Peugeot 306 Break 1.4i XR	https://www.automobile-catalog.com/car/1998/2612015/peugeot_306_break_1_4i_xr.html
EU-SKODA-OCTAVIA-I-1U-WAGON-PREFL-02	4511	1731	1457	Auto-Data Skoda Octavia I Combi Tour 1.9 TDI 110 Hp	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-1.9-tdi-110hp-14262
EU-SKODA-OCTAVIA-I-1U-WAGON-FACELIFT-01	4513	1731	1457	Auto-Data Skoda Octavia I Combi Tour facelift 1.9 SDI 68 Hp	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-facelift-2000-1.9-sdi-68hp-56469
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500	Auto-Data Nissan Primera Wagon P10	https://www.auto-data.net/en/nissan-primera-wagon-p10-generation-188
EU-PIAGGIO-APE-CARESSINO-2007-CONVERTIBLE-DIESEL-01	2940	1465	1770	Piaggio Ape Calessino 2007 technical specifications via ItaliaSpeed	https://www.italiaspeed.com/2007/cars/other/piaggio/07/ape_calessino/0207.html
EU-PIAGGIO-APE-CARESSINO-2009-CONVERTIBLE-ELECTRIC-01	2940	1465	1750	Piaggio Group Ape Calessino Electric Lithium technical specifications	https://www.piaggiogroup.com/sites/default/files/news/ape_calessino_2009_eng.pdf
EU-VW-SHARAN-I-MPV-01	4634	1810	1730	Auto-Data Volkswagen Sharan I facelift 2004 2.0 TDI	https://www.auto-data.net/en/volkswagen-sharan-i-facelift-2004-2.0-tdi-140hp-44855
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4808	1717	1361	Automobile-Catalog 1997 Buick Skylark Limited Sedan 2.4L Twin Cam	https://www.automobile-catalog.com/car/1997/323105/buick_skylark_limited_sedan_2_4l_twin_cam.html
EU-CADILLAC-SRX-II-SUV-5D-01	4834	1912	1670	Automobile-Catalog 2010 Cadillac SRX 3.0L V6 AWD	https://www.automobile-catalog.com/car/2010/1200710/cadillac_srx_3_0l_v-6_di_awd.html
EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	4673	1849	1727	Auto-Data Chevrolet Captiva I facelift 2011 2.4 Ecotec AWD	https://www.auto-data.net/en/chevrolet-captiva-i-facelift-2011-2.4-ecotec-167hp-awd-16943
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440	Auto-Data Nissan Micra K11	https://www.auto-data.net/en/nissan-micra-k11-generation-208
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	4435	1695	1405	Auto-Data Mitsubishi Carisma Hatchback 1.8 16V GDI 125 Hp	https://www.auto-data.net/en/mitsubishi-carisma-hatchback-1.8-16v-gdi-125hp-15560
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	4475	1710	1405	Auto-Data Mitsubishi Carisma Hatchback 1.8 16V GDI 122 Hp	https://www.auto-data.net/en/mitsubishi-carisma-hatchback-1.8-16v-gdi-122hp-15559
EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-PREFL-01	4435	1710	1405	Auto-Data Mitsubishi Carisma Sedan 1.8 16V GDI 125 Hp	https://www.auto-data.net/en/mitsubishi-carisma-1.8-16v-gdi-125hp-15549
EU-MITSUBISHI-CARISMA-DA-SEDAN-4D-FACELIFT-01	4475	1710	1405	Auto-Data Mitsubishi Carisma Sedan 1.8 16V GDI 122 Hp	https://www.auto-data.net/en/mitsubishi-carisma-1.8-16v-gdi-122hp-15548
EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	4335	1730	1695	CarsGuide Kia Sportage 1997 dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/1997
EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	4435	1765	1655	CarsGuide Kia Sportage 2004 dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/2004
EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	4425	1695	1440	Automobile-Catalog 1998 Honda Civic Aerodeck 1.4i S	https://www.automobile-catalog.com/car/1998/1118330/honda_civic_aerodeck_1_4i_s.html
EU-NISSAN-PATHFINDER-II-R50-SUV-5D-01	4530	1840	1750	Auto-Data Nissan Pathfinder II 3.3 V6;Auto-Data Nissan Pathfinder II 2.7 TD;Auto-Data Nissan Pathfinder II 3.2 TD	https://www.auto-data.net/en/nissan-pathfinder-ii-3.3-v6-170hp-4wd-930;https://www.auto-data.net/en/nissan-pathfinder-ii-2.7-td-131hp-4wd-928;https://www.auto-data.net/en/nissan-pathfinder-ii-3.2-td-150hp-4wd-929
EU-KIA-SHUMA-I-FB-SEDAN-4D-01	4427	1711	1413	Automobile-Catalog 1999 Kia Shuma 1.5 LS 4-dr	https://www.automobile-catalog.com/car/1999/1344740/kia_shuma_1_5_ls_4-dr.html
EU-KIA-SHUMA-I-FB-HATCHBACK-5D-01	4475	1700	1410	Automobile-Catalog 1997 Kia Shuma 1.5 GX Di	https://www.automobile-catalog.com/car/1997/1344830/kia_shuma_1_5_gx_di.html
EU-HYUNDAI-H1-I-A1-MPV-4D-01	4695	1820	1885	Automobile-Catalog Hyundai Starex 2400 HSV 4x4;Automobile-Catalog Hyundai H-1 Starex 2.5 TD	https://www.automobile-catalog.com/car/1998/1167770/hyundai_starex_2400_hsv_4x4.html;https://www.automobile-catalog.com/car/1998/1167800/hyundai_h-1_starex_2_5_td_automatic.html
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380	Auto-Data Ford Granada Turnier GNU	https://www.auto-data.net/en/ford-granada-turnier-gnu-generation-1750
EU-FORD-TAUNUS-TC2-WAGON-01	4440	1700	1366	Automobile-Catalog 1977 Ford Taunus Turnier 1.3 L	https://www.automobile-catalog.com/car/1977/921245/ford_taunus_turnier_1_3_l.html
EU-TOYOTA-LAND-CRUISER-100-J100-SUV-PREFL-01	4890	1940	1860	Auto-Data Toyota Land Cruiser J100	https://www.auto-data.net/en/toyota-land-cruiser-j100-generation-930
EU-TOYOTA-LAND-CRUISER-100-J100-SUV-FACELIFT-01	4890	1940	1880	Auto-Data Toyota Land Cruiser J100 facelift 2002	https://www.auto-data.net/en/toyota-land-cruiser-j100-facelift-2002-generation-9133
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-PREFL-01	4725	1690	1760	Toyota Hilux sixth generation UK launch pack 1997	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Hilux-gen6-UK-launch-pack-1997.pdf
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-PREFL-01	4725	1690	1800	Toyota Hilux sixth generation UK launch pack 1997	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Hilux-gen6-UK-launch-pack-1997.pdf
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	4785	1700	1765	Toyota Hilux major technical specifications	https://toyotamanuals.gitlab.io/pz471-zx006-ca/htmlweb/ncf/ncf258e/m_07_0340.pdf
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	4915	1700	1765	Toyota Hilux major technical specifications	https://toyotamanuals.gitlab.io/pz471-zx006-ca/htmlweb/ncf/ncf258e/m_07_0340.pdf
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	4785	1700	1795	Toyota Hilux major technical specifications	https://toyotamanuals.gitlab.io/pz471-zx006-ca/htmlweb/ncf/ncf258e/m_07_0340.pdf
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	4915	1700	1795	Toyota Hilux major technical specifications	https://toyotamanuals.gitlab.io/pz471-zx006-ca/htmlweb/ncf/ncf258e/m_07_0340.pdf
EU-LEXUS-GS-I-S140-SEDAN-4D-01	4950	1795	1400	Auto-Data Lexus GS I 300	https://www.auto-data.net/en/lexus-gs-i-300-223hp-automatic-5919
EU-LEXUS-GS-II-S160-SEDAN-4D-01	4805	1800	1445	Auto-Data Lexus GS II	https://www.auto-data.net/en/lexus-gs-ii-generation-1364
EU-LEXUS-LS-II-XF20-SEDAN-FACELIFT-01	4995	1830	1435	Auto-Data Lexus LS II facelift 400 V8 284 Hp	https://www.auto-data.net/en/lexus-ls-ii-facelift-1998-400-v8-284hp-automatic-36920
EU-TOYOTA-RAV4-I-XA10-CONVERTIBLE-3D-01	3715	1695	1660	Auto-Data Toyota RAV4 I Soft top XA10	https://www.auto-data.net/en/toyota-rav4-i-soft-top-xa10-generation-978
EU-TOYOTA-PASEO-L5-CONVERTIBLE-2D-01	4160	1660	1320	Auto-Data Toyota Paseo Cabrio L5	https://www.auto-data.net/en/toyota-paseo-cabrio-l5-generation-786
EU-BEDFORD-CF-VAN-SWB-01	4410	1950	1980	Bedford CF2 Specifications and Dimensions official brochure	https://www.bedfordcf.co.uk/br/br26_p4.jpg
EU-BEDFORD-CF-VAN-LWB-01	4920	1950	2160	Bedford CF2 Specifications and Dimensions official brochure	https://www.bedfordcf.co.uk/br/br26_p6.jpg
EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	3380	1575	1115	Caterham Roadsport dimensions	https://www.caterhamlotus7.club/forums/topic/260513-what-are-the-dimensions-of-a-caterham-solved-table-attached/
EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	3460	1685	1115	Automobile-Catalog 2013 Caterham 7 SV Roadsport 175	https://www.automobile-catalog.com/car/2013/1201040/caterham_7_sv_roadsport_175.html
EU-CHEVROLET-VOLT-I-HATCHBACK-5D-01	4498	1788	1430	Automobile-Catalog 2011 Chevrolet Volt	https://www.automobile-catalog.com/car/2011/1207475/chevrolet_volt.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8501-8600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Hilux-gen6-UK-launch-pack-1997.pdf "https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Hilux-gen6-UK-launch-pack-1997.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8501-8600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8501-8600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10635 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3299 行）

