# 任务：all 第 4201-4300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0043__cfcd9b33


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4201-4300 行

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
all 第 4201-4300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479
EU-CITROEN-C5-I-PHASE-I-HATCHBACK-5D-01	4618	1770	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4745	1780	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-02	4750	1770	1480
EU-CITROEN-C5-I-PHASE-II-WAGON-01	4839	1780	1511
EU-CITROEN-C5-I-PHASE-I-WAGON-5D-01	4760	1770	1520
EU-FIAT-BRAVA-HATCHBACK-5D-01	4187	1741	1410
EU-FIAT-PUNTO-2012-HATCHBACK-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	4065	1687	1490
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-NISSAN-BLUEBIRD-610-SEDAN-4D-01	4215	1600	1405
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467
EU-RENAULT-MEGANE-III-COUPE-FACELIFT1-01	4299	1785	1423
EU-RENAULT-MEGANE-III-COUPE-FACELIFT2-01	4299	1848	1435
EU-RENAULT-MEGANE-III-COUPE-PREFL-01	4299	1804	1435
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-III-01	4567	1804	1507
EU-RENAULT-MEGANE-III-GRANDTOUR-PHASE-I-II-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-FACELIFT-5D-01	4295	1808	1471
EU-RENAULT-MEGANE-III-HATCHBACK-PREFL-5D-01	4295	1808	1491
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	4228	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	4498	1777	1460
EU-RENAULT-SCENIC-III-MPV-FACELIFT-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PREFL-01	4344	1845	1637
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-VOLVO-V40-I-VW-WAGON-5D-FACELIFT-01	4516	1720	1425
EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	4206	1759	1580
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592
EU-VW-GOLF-PLUS-V-MPV-PREFL-01	4206	1759	1592
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	70	95	Oct 2009	Feb 2012	2024-03-01	32252
Fiat	Punto	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	88	120	Oct 2009	Feb 2012	2024-03-01	32253
VW	Multivan t5	2.0 TDI	Bus	Frontantrieb	Diesel	62	84	Sep 2009	Aug 2015	2024-03-01	32254
VW	Transporter t5	2.0 TDI	Bus	Frontantrieb	Diesel	62	84	Sep 2009	Aug 2015	2024-03-01	32255
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	62	84	Sep 2009	Aug 2015	2024-03-01	32256
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	62	84	Sep 2009	Aug 2015	2024-03-01	32257
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	75	102	Sep 2009	Aug 2015	2024-03-01	32258
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	75	102	Sep 2009	Aug 2015	2024-03-01	32259
VW	Transporter t5	2.0 TDI	Bus	Frontantrieb	Diesel	75	102	Sep 2009	Aug 2015	2024-03-01	32260
VW	Multivan t5	2.0 TDI	Bus	Frontantrieb	Diesel	75	102	Sep 2009	Aug 2015	2024-03-01	32261
VW	Multivan t5	2.0 TDI	Bus	Frontantrieb	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32262
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32263
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32264
VW	Transporter t5	2.0 TDI	Bus	Frontantrieb	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32265
VW	Transporter t5	2.0 TDI 4motion	Bus	Allrad	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32266
VW	Transporter t5	2.0 TDI 4motion	Kasten	Allrad	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32267
VW	Transporter t5	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32268
VW	Multivan t5	2.0 TDI 4motion	Bus	Allrad	Diesel	103	140	Sep 2009	Aug 2015	2024-03-01	32269
VW	Multivan t5	2.0 Bitdi	Bus	Frontantrieb	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32270
VW	Multivan t5	2.0 Bitdi 4motion	Bus	Allrad	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32271
VW	Transporter t5	2.0 Bitdi	Pritsche/Fahrgestell	Frontantrieb	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32272
VW	Transporter t5	2.0 Bitdi	Kasten	Frontantrieb	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32273
VW	Transporter t5	2.0 Bitdi	Bus	Frontantrieb	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32274
VW	Transporter t5	2.0 Bitdi 4motion	Pritsche/Fahrgestell	Allrad	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32275
VW	Transporter t5	2.0 Bitdi 4motion	Kasten	Allrad	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32276
VW	Transporter t5	2.0 Bitdi 4motion	Bus	Allrad	Diesel	132	180	Sep 2009	Aug 2015	2024-03-01	32277
Chevrolet	Aveo / kalos	1.4	Stufenheck	Frontantrieb	Benzin	61	83	Mar 2005	-	2024-03-01	32290
Nissan	Bluebird	2.4 I	Stufenheck	Frontantrieb	Benzin	112	152	Jun 1992	May 1997	2024-03-01	32312
Peugeot	405 ii	1.6	Stufenheck	Frontantrieb	Benzin	68	92	Aug 1992	Aug 1994	2024-03-01	32345
Volvo	V40	T4	Schrägheck	Frontantrieb	Benzin	132	180	Jul 2013	Dec 2015	2024-03-01	32346
Volvo	V40 cross country	T5 AWD	Schrägheck	Allrad	Benzin	157	214	Mar 2013	Dec 2015	2024-03-01	32357
Daihatsu	Move	1.0 I	Großraumlimousine	Frontantrieb	Benzin	40	54	Oct 1998	Dec 2000	2024-03-01	32359
Ford	Mondeo iv	1.8 Tdci	Schrägheck	Frontantrieb	Diesel	92	125	Jun 2007	Jan 2015	2024-03-01	32387
Ford	Mondeo iv	1.8 Tdci	Stufenheck	Frontantrieb	Diesel	92	125	Jun 2007	Jan 2015	2024-03-01	32388
Ford	Mondeo iv turnier	1.8 Tdci	Kombi	Frontantrieb	Diesel	92	125	Jun 2007	Dec 2012	2024-03-01	32389
Alfa Romeo	Mito	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	85	115	Aug 2008	Aug 2015	2024-03-01	32396
Alfa Romeo	Mito	1.4 Tjet	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2008	Jun 2011	2024-03-01	32398
Zastava	10	1.2 60	Schrägheck	Frontantrieb	Benzin	44	60	Oct 2005	-	2024-03-01	32406
VW	Golf vi variant	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Jul 2009	Jul 2013	2024-03-01	32585
VW	Golf vi variant	1.6	Kombi	Frontantrieb	Benzin	75	102	Jul 2009	Jul 2013	2024-03-01	32586
VW	Golf vi variant	1.4	Kombi	Frontantrieb	Benzin	59	80	Jul 2009	Jul 2013	2024-03-01	32589
VW	Golf vi variant	1.4 TSI	Kombi	Frontantrieb	Benzin	90	122	Jul 2009	Jul 2013	2024-03-01	32601
VW	Golf vi variant	1.4 TSI	Kombi	Frontantrieb	Benzin	118	160	Jul 2009	Jul 2013	2024-03-01	32606
VW	Golf vi variant	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Jul 2009	Jul 2013	2024-03-01	32609
VW	Golf vi variant	1.6 TDI 4motion	Kombi	Allrad	Diesel	77	105	Jul 2009	Jul 2013	2024-03-01	32612
VW	Golf vi variant	1.2 TSI	Kombi	Frontantrieb	Benzin	77	105	Jul 2009	Jul 2013	2024-03-01	32621
VW	Golf vi	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Nov 2008	Nov 2012	2024-03-01	32625
VW	Golf vi	2.0 R 4motion	Schrägheck	Allrad	Benzin	199	270	Nov 2009	Nov 2012	2024-03-01	32626
VW	Jetta iii	1.6 TDI	Stufenheck	Frontantrieb	Diesel	77	105	Jun 2009	Oct 2010	2024-03-01	32629
VW	Golf plus v	1.2 TSI	Schrägheck	Frontantrieb	Benzin	77	105	Nov 2009	Dec 2013	2024-03-01	32630
VW	Scirocco	2.0 R	Coupe	Frontantrieb	Benzin	195	265	Nov 2009	Nov 2017	2024-03-01	32631
BMW	1	120 I	Coupe	Heckantrieb	Benzin	125	170	Oct 2007	Oct 2013	2024-03-01	32675
BMW	1	118 D	Coupe	Heckantrieb	Diesel	105	143	Sep 2009	Oct 2013	2024-03-01	32676
Mercedes-benz	C-Klasse	C 350 CDI	Stufenheck	Heckantrieb	Diesel	170	231	Oct 2009	Jan 2014	2024-03-01	32677
Mercedes-benz	C-Klasse	C 350 CDI 4-matic	Stufenheck	Allrad	Diesel	170	231	Oct 2009	Jan 2014	2024-03-01	32678
Mercedes-benz	C-Klasse	C 350 CDI	Kombi	Heckantrieb	Diesel	170	231	Oct 2009	Aug 2014	2024-03-01	32679
Mercedes-benz	C-Klasse	C 350 CDI 4-matic	Kombi	Allrad	Diesel	170	231	Oct 2009	Aug 2014	2024-03-01	32681
Renault	Scénic ii	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	92	125	Jun 2003	Nov 2008	2024-03-01	32682
Mercedes-benz	E-Klasse	E 63 AMG	Kombi	Heckantrieb	Benzin	386	525	Aug 2009	Dec 2011	2024-03-01	32683
Ford	Mondeo iv	2.0 Flexifuel	Stufenheck	Frontantrieb	Benzin/Ethanol	107	145	Mar 2009	Jan 2015	2024-03-01	32685
Renault	Megane ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2002	Feb 2008	2024-03-01	32686
Renault	Megane ii coupé-	1.9 DCI	Cabriolet	Frontantrieb	Diesel	85	115	Sep 2003	Mar 2009	2024-03-01	32687
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	32688
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	120	163	Jun 2006	Jun 2008	2024-03-01	32689
Audi	A3	2.0 TDI	Cabriolet	Frontantrieb	Diesel	100	136	Apr 2008	May 2013	2024-03-01	32690
Chevrolet	Nubira	1.8	Stufenheck	Frontantrieb	Benzin	89	121	Jan 2006	Sep 2007	2024-03-01	32691
Fiat	Brava	1.6 16V	Schrägheck	Frontantrieb	Benzin	76	103	Jan 1999	Dec 2002	2024-03-01	32692
Ford	Galaxy ii	2.0 Flexifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	107	145	May 2006	Jun 2015	2024-03-01	32693
Ford	Mondeo iv	1.6 TI	Stufenheck	Frontantrieb	Benzin	81	110	Mar 2007	Jan 2015	2024-03-01	32699
Ford	Mondeo iv	1.8 Tdci	Stufenheck	Frontantrieb	Diesel	74	100	Mar 2007	Jan 2015	2024-03-01	32701
Ford	S-Max	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	74	100	Jan 2007	Dec 2010	2024-03-01	32705
Alfa Romeo	Mito	1.4 Turbo Multiair	Schrägheck	Frontantrieb	Benzin	99	135	Oct 2009	Dec 2014	2024-03-01	32741
Alfa Romeo	Mito	1.4 Multiair	Schrägheck	Frontantrieb	Benzin	125	170	Sep 2009	Oct 2018	2024-03-01	32742
Alfa Romeo	Mito	1.3 Multijet	Schrägheck	Frontantrieb	Diesel	70	95	Sep 2009	Oct 2018	2024-03-01	32743
Seat	Altea	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	77	105	Oct 2009	Jul 2015	2024-05-01	32744
Seat	Altea	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	77	105	Oct 2009	Jul 2015	2024-05-01	32745
Seat	Ibiza iv	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	May 2009	May 2015	2024-03-01	32746
Seat	Ibiza iv	2.0 TDI	Schrägheck	Frontantrieb	Diesel	105	143	Jan 2010	May 2015	2024-03-01	32747
Seat	Ibiza iv sc	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	May 2009	May 2015	2025-06-01	32748
Seat	Ibiza iv sc	2.0 TDI	Schrägheck	Frontantrieb	Diesel	105	143	Jan 2010	May 2015	2025-06-01	32749
Skoda	Yeti	1.2 TSI	SUV	Frontantrieb	Benzin	77	105	Sep 2009	May 2015	2024-03-01	32750
Skoda	Yeti	1.8 TSI 4X4	SUV	Allrad	Benzin	118	160	May 2009	Dec 2017	2024-03-01	32751
Skoda	Yeti	2.0 TDI	SUV	Frontantrieb	Diesel	81	110	Nov 2009	Dec 2017	2024-03-01	32752
Skoda	Yeti	2.0 TDI 4X4	SUV	Allrad	Diesel	81	110	Nov 2009	Dec 2017	2024-03-01	32753
Skoda	Yeti	2.0 TDI 4X4	SUV	Allrad	Diesel	103	140	May 2009	Dec 2017	2024-03-01	32754
Skoda	Yeti	2.0 TDI 4X4	SUV	Allrad	Diesel	125	170	Nov 2009	May 2015	2024-03-01	32755
Skoda	Superb ii	1.4 TSI	Kombi	Frontantrieb	Benzin	92	125	Oct 2009	May 2015	2024-03-01	32783
Skoda	Superb ii	1.8 TSI	Kombi	Frontantrieb	Benzin	118	160	Oct 2009	May 2015	2024-03-01	32784
Skoda	Superb ii	1.8 TSI 4X4	Kombi	Allrad	Benzin	118	160	Oct 2009	May 2015	2024-03-01	32785
Skoda	Superb ii	3.6 V6 4X4	Kombi	Allrad	Benzin	191	260	Oct 2009	May 2015	2024-03-01	32786
Skoda	Superb ii	2.0 TDI 16V	Kombi	Frontantrieb	Diesel	103	140	Oct 2009	May 2015	2024-03-01	32787
Skoda	Superb ii	2.0 TDI	Kombi	Frontantrieb	Diesel	125	170	Oct 2009	May 2015	2024-03-01	32788
Skoda	Superb ii	2.0 TDI 4X4	Kombi	Allrad	Diesel	125	170	Oct 2009	May 2015	2024-03-01	32789
VW	Passat b6	2.0 TDI 4motion	Stufenheck	Allrad	Diesel	125	170	May 2009	Jul 2010	2024-03-01	32791
VW	Passat b6 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	125	170	May 2009	Nov 2010	2024-03-01	32792
Citroën	C5	1.6 THP 155	Stufenheck	Frontantrieb	Benzin	115	156	Apr 2009	Jul 2016	2024-07-01	32793
Citroën	C5	2.0 HDI 165	Stufenheck	Frontantrieb	Diesel	120	163	Apr 2009	Jul 2016	2024-07-01	32794
Citroën	C5	1.6 THP 155	Kombi	Frontantrieb	Benzin	115	156	Apr 2009	Jul 2016	2024-07-01	32795
Citroën	C5	2.0 HDI 165	Kombi	Frontantrieb	Diesel	120	163	Apr 2009	Jul 2016	2024-07-01	32796
VW	Passat cc b6	2.0 TDI 4motion	Coupe	Allrad	Diesel	125	170	Nov 2009	Jan 2012	2024-03-01	32797


--- Round 1 / 首次发送 ---
## 更新点

* 完成 100 个输入 Ktype 的全量映射。
* T5 按 MPV、Van、单排/双排底盘、SWB/LWB 及不同车顶高度拆分，并复用已有尺寸组。
* MiTo 按对应动力版本分别关联 `4060×1720×1440` 与 `4063×1720×1446` 两套尺寸组。([汽车数据][1])
* Ibiza 已纠正普通 1.6 TDI 与 2.0 TDI/FR 的外廓混组问题，分别处理三门、五门及改款前后尺寸。([汽车数据][2])
* 已完成表头、主键唯一、尺寸组唯一、引用闭合、来源非空和下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：193
* PENDING 映射：0
* 已确认且被引用尺寸组：79
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
32252_3dr	32252	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门外廓。	READY
32252_5dr	32252	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门外廓。	READY
32253_3dr	32253	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门外廓。	READY
32253_5dr	32253	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门外廓。	READY
32254	32254	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32255_swb_lowroof	32255	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32255_swb_midroof	32255	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32255_lwb_lowroof	32255	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32255_lwb_midroof	32255	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32255_lwb_highroof	32255	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32256_swb_lowroof	32256	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32256_swb_medroof	32256	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32256_lwb_lowroof	32256	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32256_lwb_medroof	32256	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32256_lwb_highroof	32256	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32257_singlecab_lwb	32257	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	HIGH	Pritsche/Fahrgestell单排长轴外廓。	READY
32257_doublecab_lwb	32257	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	Pritsche/Fahrgestell双排长轴外廓。	READY
32258_singlecab_lwb	32258	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	HIGH	Pritsche/Fahrgestell单排长轴外廓。	READY
32258_doublecab_lwb	32258	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	Pritsche/Fahrgestell双排长轴外廓。	READY
32259_swb_lowroof	32259	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32259_swb_medroof	32259	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32259_lwb_lowroof	32259	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32259_lwb_medroof	32259	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32259_lwb_highroof	32259	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32260_swb_lowroof	32260	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32260_swb_midroof	32260	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32260_lwb_lowroof	32260	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32260_lwb_midroof	32260	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32260_lwb_highroof	32260	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32261	32261	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32262	32262	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32263_singlecab_lwb	32263	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	HIGH	Pritsche/Fahrgestell单排长轴外廓。	READY
32263_doublecab_lwb	32263	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	Pritsche/Fahrgestell双排长轴外廓。	READY
32264_swb_lowroof	32264	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32264_swb_medroof	32264	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32264_lwb_lowroof	32264	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32264_lwb_medroof	32264	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32264_lwb_highroof	32264	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32265_swb_lowroof	32265	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32265_swb_midroof	32265	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32265_lwb_lowroof	32265	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32265_lwb_midroof	32265	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32265_lwb_highroof	32265	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32266_swb_lowroof	32266	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32266_swb_midroof	32266	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32266_lwb_lowroof	32266	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32266_lwb_midroof	32266	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32266_lwb_highroof	32266	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32267_swb_lowroof	32267	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32267_swb_medroof	32267	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32267_lwb_lowroof	32267	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32267_lwb_medroof	32267	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32267_lwb_highroof	32267	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32268_singlecab_lwb_4motion	32268	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	HIGH	4Motion单排长轴外廓。	READY
32268_doublecab_lwb_4motion	32268	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	HIGH	4Motion双排长轴外廓。	READY
32269	32269	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32270	32270	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32271	32271	MPV	T5	7HM	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	Multivan标准轴距乘用车身。	READY
32272_singlecab_lwb	32272	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	HIGH	Pritsche/Fahrgestell单排长轴外廓。	READY
32272_doublecab_lwb	32272	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	Pritsche/Fahrgestell双排长轴外廓。	READY
32273_swb_lowroof	32273	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32273_swb_medroof	32273	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32273_lwb_lowroof	32273	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32273_lwb_medroof	32273	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32273_lwb_highroof	32273	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32274_swb_lowroof	32274	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32274_swb_midroof	32274	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32274_lwb_lowroof	32274	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32274_lwb_midroof	32274	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32274_lwb_highroof	32274	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32275_singlecab_lwb_4motion	32275	Pickup	T5	7J0	2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	HIGH	4Motion单排长轴外廓。	READY
32275_doublecab_lwb_4motion	32275	Pickup	T5	7J0	4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	HIGH	4Motion双排长轴外廓。	READY
32276_swb_lowroof	32276	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32276_swb_medroof	32276	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32276_lwb_lowroof	32276	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32276_lwb_medroof	32276	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32276_lwb_highroof	32276	Van	T5	7HA		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	HIGH	Kasten按轴距与车顶高度拆分。	READY
32277_swb_lowroof	32277	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32277_swb_midroof	32277	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32277_lwb_lowroof	32277	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32277_lwb_midroof	32277	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32277_lwb_highroof	32277	MPV	T5	7HB		EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	HIGH	Bus/Kombi按轴距与车顶高度拆分。	READY
32290	32290	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH		READY
32312	32312	Sedan	Bluebird U13	U13	4	EU-NISSAN-BLUEBIRD-U13-SEDAN-4D-01	HIGH		READY
32345	32345	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-4B-SEDAN-4D-01	HIGH		READY
32346	32346	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-5D-01	HIGH		READY
32357	32357	Hatchback	V40 Cross Country I		5	EU-VOLVO-V40-CROSS-COUNTRY-I-HATCHBACK-5D-01	HIGH	Cross Country独立增高外廓。	READY
32359	32359	MPV	Move L9	L9	5	EU-DAIHATSU-MOVE-L9-MPV-5D-01	HIGH		READY
32387_prefl	32387	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32387_facelift	32387	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32388_prefl	32388	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32388_facelift	32388	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32389_prefl	32389	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32389_facelift	32389	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32396	32396	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	对应动力版本外廓。	READY
32398	32398	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	对应动力版本外廓。	READY
32406	32406	Hatchback	Zastava 10	188	5	EU-ZASTAVA-10-HATCHBACK-5D-01	HIGH		READY
32585	32585	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32586	32586	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32589	32589	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32601	32601	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32606	32606	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32609	32609	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32612	32612	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32621	32621	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
32625_3dr	32625	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门外廓。	READY
32625_5dr	32625	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门外廓。	READY
32626_3dr	32626	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门外廓。	READY
32626_5dr	32626	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门外廓。	READY
32629	32629	Sedan	Jetta III	1K2	4	EU-VW-JETTA-III-1K2-SEDAN-4D-01	HIGH		READY
32630	32630	MPV	Golf Plus VI	5M1	5	EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	HIGH	2009年后改款Golf Plus按MPV归类。	READY
32631_prefl	32631	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32631_facelift	32631	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32675	32675	Coupe	1 Series E82	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
32676	32676	Coupe	1 Series E82	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
32677_prefl	32677	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32677_facelift	32677	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-FACELIFT-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32678_prefl	32678	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32678_facelift	32678	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-FACELIFT-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32679_prefl	32679	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32679_facelift	32679	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-FACELIFT-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32681_prefl	32681	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32681_facelift	32681	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-FACELIFT-01	HIGH	生产期跨越2011年改款，按外廓差异拆分。	READY
32682_prefl	32682	MPV	Scénic II	JM	5	EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	HIGH	生产区间覆盖Phase I外廓。	READY
32682_facelift	32682	MPV	Scénic II	JM	5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	生产区间覆盖Phase II外廓。	READY
32683	32683	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-E63-AMG-WAGON-5D-01	HIGH	E 63 AMG旅行车外廓。	READY
32685_prefl	32685	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32685_facelift	32685	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32686_3dr_prefl	32686	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-PHASE-I-HATCHBACK-3D-01	HIGH	三门Phase I外廓。	READY
32686_5dr_prefl	32686	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-PHASE-I-HATCHBACK-5D-01	HIGH	五门Phase I外廓。	READY
32686_3dr_facelift	32686	Hatchback	Megane II		3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门Phase II外廓。	READY
32686_5dr_facelift	32686	Hatchback	Megane II		5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门Phase II外廓。	READY
32687_prefl	32687	Convertible	Megane II CC		2	EU-RENAULT-MEGANE-II-CC-PHASE-I-CONVERTIBLE-2D-01	HIGH	CC Phase I外廓。	READY
32687_facelift	32687	Convertible	Megane II CC		2	EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	HIGH	CC Phase II外廓。	READY
32688	32688	Hatchback	A3 II	8P1	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH		READY
32689	32689	Hatchback	A3 II Sportback	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH		READY
32690	32690	Convertible	A3 II Cabriolet	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
32691	32691	Sedan	Nubira J200	J200	4	EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	HIGH		READY
32692	32692	Hatchback	Brava	182	5	EU-FIAT-BRAVA-HATCHBACK-5D-01	HIGH		READY
32693_prefl	32693	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32693_facelift	32693	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH	生产区间覆盖改款后外廓。	READY
32699_prefl	32699	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32699_facelift	32699	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32701_prefl	32701	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32701_facelift	32701	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
32705_prefl	32705	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
32705_facelift	32705	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH	生产区间覆盖改款后外廓。	READY
32741	32741	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	HIGH	对应动力版本外廓。	READY
32742	32742	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	对应动力版本外廓。	READY
32743	32743	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	HIGH	对应动力版本外廓。	READY
32744	32744	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
32745	32745	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
32746_prefl	32746	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	五门改款前标准外廓。	READY
32746_facelift	32746	Hatchback	Ibiza IV	6P1	5	EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	HIGH	五门2012 facelift标准外廓。	READY
32747_prefl	32747	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	HIGH	2.0 TDI采用五门FR外部套件外廓。	READY
32747_facelift	32747	Hatchback	Ibiza IV	6P1	5	EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	HIGH	2.0 TDI采用五门facelift FR外廓。	READY
32748_prefl	32748	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	SC三门改款前外廓。	READY
32748_facelift	32748	Hatchback	Ibiza IV SC	6P5	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	SC三门2012 facelift标准外廓。	READY
32749_prefl	32749	Hatchback	Ibiza IV SC	6J1	3	EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	HIGH	SC三门2.0 TDI改款前外廓。	READY
32749_facelift	32749	Hatchback	Ibiza IV SC	6P5	3	EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	HIGH	SC三门2.0 TDI采用facelift FR外廓。	READY
32750_prefl	32750	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32750_facelift	32750	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32751_prefl	32751	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32751_facelift	32751	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32752_prefl	32752	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32752_facelift	32752	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32753_prefl	32753	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32753_facelift	32753	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32754_prefl	32754	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32754_facelift	32754	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32755_prefl	32755	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32755_facelift	32755	SUV	Yeti I	5L	5	EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32783_prefl	32783	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32783_facelift	32783	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32784_prefl	32784	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32784_facelift	32784	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32785_prefl	32785	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32785_facelift	32785	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32786_prefl	32786	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32786_facelift	32786	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32787_prefl	32787	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32787_facelift	32787	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32788_prefl	32788	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32788_facelift	32788	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32789_prefl	32789	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	HIGH	生产区间覆盖2013改款前外廓。	READY
32789_facelift	32789	Wagon	Superb II	3T5	5	EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	HIGH	生产区间覆盖2013改款后外廓。	READY
32791	32791	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH		READY
32792	32792	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH		READY
32793	32793	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
32794	32794	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
32795	32795	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
32796	32796	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
32797	32797	Coupe	Passat CC I	357	4	EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	HIGH	四门Coupe车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4201-4300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	4065	1687	1490	Auto-Data Fiat Punto Evo (199) specifications	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-95hp-start-stop-dpf-16757
EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	4065	1687	1490	Auto-Data Fiat Punto Evo (199) specifications	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-95hp-start-stop-dpf-16757
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470	Parkers Volkswagen Transporter T5 dimensions	https://www.parkers.co.uk/vans-pickups/volkswagen/transporter/2003-dimensions/
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949	Honest John Volkswagen Transporter T5 chassis-cab specifications	https://vans.honestjohn.co.uk/specs/detail/?v=VW-TRA0210
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949	Honest John Volkswagen Transporter T5 chassis-cab specifications	https://vans.honestjohn.co.uk/specs/detail/?v=VW-TRA0210
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963	Honest John Volkswagen Transporter T5 chassis-cab specifications	https://vans.honestjohn.co.uk/specs/detail/?v=VW-TRA0210
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963	Honest John Volkswagen Transporter T5 chassis-cab specifications	https://vans.honestjohn.co.uk/specs/detail/?v=VW-TRA0210
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495	Automobile-Catalog Chevrolet Kalos T200 Sedan specifications	https://www.automobile-catalog.com/car/2006/559070/chevrolet_kalos_1_4_16v_sx_sedan.html
EU-NISSAN-BLUEBIRD-U13-SEDAN-4D-01	4585	1695	1405	Auto-Data Nissan Bluebird U13 specifications	https://www.auto-data.net/en/nissan-bluebird-u13-2.4-152hp-25078
EU-PEUGEOT-405-II-4B-SEDAN-4D-01	4408	1714	1406	Auto-Data Peugeot 405 I facelift specifications	https://www.auto-data.net/en/peugeot-405-i-15b-facelift-1992-1.6-88hp-5566
EU-VOLVO-V40-II-HATCHBACK-5D-01	4369	1802	1445	Auto-Data Volvo V40 2012 specifications	https://www.auto-data.net/en/volvo-v40-2012-1.6-t4-180hp-17577
EU-VOLVO-V40-CROSS-COUNTRY-I-HATCHBACK-5D-01	4370	1802	1458	Volvo Cars V40 Cross Country dimensions	https://www.volvocars.com/en-om/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/
EU-DAIHATSU-MOVE-L9-MPV-5D-01	3410	1475	1695	Auto-Data Daihatsu Move L9 specifications	https://www.auto-data.net/en/daihatsu-move-l9-1.0-i-12v-56hp-99
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Auto-Data Ford Mondeo generation specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-01	4060	1720	1440	Auto-Data Alfa Romeo MiTo 1.6 JTDm specifications	https://www.auto-data.net/en/alfa-romeo-mito-1.6-jtdm-120hp-16680
EU-ZASTAVA-10-HATCHBACK-5D-01	3865	1660	1480	Auto-Data Zastava 10 specifications	https://www.auto-data.net/en/zastava-10-model-1231
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504	Volkswagen Newsroom Golf VI Variant vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-6-variant-profile-19529
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479	Auto-Data Volkswagen Golf generation specifications	https://www.auto-data.net/en/volkswagen-golf-model-896
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480	Auto-Data Volkswagen Golf generation specifications	https://www.auto-data.net/en/volkswagen-golf-model-896
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459	Auto-Data Volkswagen Jetta generation specifications	https://www.auto-data.net/en/volkswagen-jetta-model-887
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592	Auto-Data Volkswagen Golf generation specifications	https://www.auto-data.net/en/volkswagen-golf-model-896
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404	Auto-Data Volkswagen Scirocco generation specifications	https://www.auto-data.net/en/volkswagen-scirocco-model-898
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406	Auto-Data Volkswagen Scirocco generation specifications	https://www.auto-data.net/en/volkswagen-scirocco-model-898
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423	Auto-Data BMW 1 Series Coupe E82 specifications	https://www.auto-data.net/en/bmw-1-series-coupe-e82-120i-170hp-9987
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	4581	1770	1447	Mercedes-Benz Public Archive C 350 CDI BlueEFFICIENCY (W204)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-350-CDI-BlueEFFICIENCY-2009---2011.xhtml?oid=189266730
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-FACELIFT-01	4591	1770	1447	Auto-Data Mercedes-Benz C-class W204 facelift C 350 CDI specifications	https://www.auto-data.net/en/mercedes-benz-c-class-w204-facelift-2011-c-350-cdi-blueefficiency-v6-265hp-7g-tronic-plus-43183
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-PREFL-01	4596	1770	1459	Auto-Data Mercedes-Benz C-class T-modell S204 C 350 CDI specifications	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-c-350-cdi-blueefficiency-v6-231hp-7g-tronic-52861
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-FACELIFT-01	4606	1770	1459	Auto-Data Mercedes-Benz C-class T-modell S204 facelift C 350 CDI specifications	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-facelift-2011-c-350-cdi-blueefficiency-v6-265hp-7g-tronic-plus-18664
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620	Auto-Data Renault Scenic generation specifications	https://www.auto-data.net/en/renault-scenic-model-1022
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620	Auto-Data Renault Scenic generation specifications	https://www.auto-data.net/en/renault-scenic-model-1022
EU-MERCEDES-BENZ-E-CLASS-S212-E63-AMG-WAGON-5D-01	4895	1854	1512	Auto-Data Mercedes-Benz E-class T-modell S212 AMG E 63 specifications	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-amg-e-63-v8-525hp-amg-speedshift-mct-44941
EU-RENAULT-MEGANE-II-PHASE-I-HATCHBACK-3D-01	4209	1777	1458	Auto-Data Renault Megane II Coupe specifications	https://www.auto-data.net/en/renault-megane-ii-coupe-1.6-16v-113hp-30258
EU-RENAULT-MEGANE-II-PHASE-I-HATCHBACK-5D-01	4209	1777	1458	Auto-Data Renault Megane II hatchback specifications	https://www.auto-data.net/en/renault-megane-ii-1.6-16v-113hp-30326
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458	Auto-Data Renault Megane II Coupe specifications	https://www.auto-data.net/en/renault-megane-ii-coupe-1.6-16v-113hp-30258
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458	Auto-Data Renault Megane II hatchback specifications	https://www.auto-data.net/en/renault-megane-ii-1.6-16v-113hp-30326
EU-RENAULT-MEGANE-II-CC-PHASE-I-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data Renault Megane II CC generation specifications	https://www.auto-data.net/en/renault-megane-model-1026
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404	Auto-Data Renault Megane II CC generation specifications	https://www.auto-data.net/en/renault-megane-model-1026
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 generation specifications	https://www.auto-data.net/en/audi-a3-model-496
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423	Auto-Data Audi A3 generation specifications	https://www.auto-data.net/en/audi-a3-model-496
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424	Auto-Data Audi A3 generation specifications	https://www.auto-data.net/en/audi-a3-model-496
EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	4515	1725	1445	Auto-Data Chevrolet Nubira specifications	https://www.auto-data.net/en/chevrolet-nubira-model-1576
EU-FIAT-BRAVA-HATCHBACK-5D-01	4187	1741	1410	Auto-Data Fiat Brava generation specifications	https://www.auto-data.net/en/fiat-brava-model-1234
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723	Auto-Data Ford Galaxy generation specifications	https://www.auto-data.net/en/ford-galaxy-model-815
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758	Auto-Data Ford Galaxy generation specifications	https://www.auto-data.net/en/ford-galaxy-model-815
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658	Auto-Data Ford S-MAX generation specifications	https://www.auto-data.net/en/ford-s-max-model-836
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Auto-Data Ford S-MAX generation specifications	https://www.auto-data.net/en/ford-s-max-model-836
EU-ALFA-ROMEO-MITO-955-HATCHBACK-3D-02	4063	1720	1446	Auto-Data Alfa Romeo MiTo 1.4 TB MultiAir 170 specifications	https://www.auto-data.net/en/alfa-romeo-mito-1.4-tb-multiair-170hp-44386
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data Seat Altea generation specifications	https://www.auto-data.net/en/seat-altea-model-1460
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data Seat Ibiza IV 1.6 TDI 105 specifications	https://www.auto-data.net/en/seat-ibiza-iv-1.6-tdi-105hp-36507
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FACELIFT-01	4061	1693	1445	Auto-Data Seat Ibiza IV facelift 1.6 TDI 105 specifications	https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-1.6-tdi-105hp-16879
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-FR-PREFL-01	4088	1693	1441	Auto-Data Seat Ibiza IV 2.0 TDI 143 specifications	https://www.auto-data.net/en/seat-ibiza-iv-2.0-tdi-143hp-44362
EU-SEAT-IBIZA-IV-6P1-HATCHBACK-5D-FR-FACELIFT-01	4082	1693	1441	Auto-Data Seat Ibiza IV facelift 2.0 TDI 143 specifications	https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-2.0-tdi-143hp-16882
EU-SEAT-IBIZA-IV-6J1-HATCHBACK-3D-PREFL-01	4034	1693	1428	Auto-Data Seat Ibiza IV SC FR 2.0 TDI 143 specifications;Zoomcar Seat Ibiza IV SC 1.6 TDI specifications	https://www.auto-data.net/en/seat-ibiza-iv-sc-fr-2.0-tdi-143hp-36482;https://zoomcar.fr/fiche-technique/seat/ibiza-iv-sc-1-6-tdi-105-fap-r-ference-NAT122587.html
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428	Auto-Data Seat Ibiza IV SC facelift 1.6 TDI 105 specifications	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.6-tdi-105hp-19336
EU-SEAT-IBIZA-IV-6P5-HATCHBACK-3D-FR-FACELIFT-01	4066	1693	1424	Auto-Data Seat Ibiza IV SC facelift 2.0 TDI 143 specifications	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-2.0-tdi-143hp-19337
EU-SKODA-YETI-I-5L-SUV-PREFL-01	4223	1793	1691	Auto-Data Skoda Yeti specifications	https://www.auto-data.net/en/skoda-yeti-generation-3102
EU-SKODA-YETI-I-5L-SUV-FACELIFT-01	4222	1793	1691	Auto-Data Skoda Yeti facelift specifications	https://www.auto-data.net/en/skoda-yeti-facelift-2013-generation-4188
EU-SKODA-SUPERB-II-3T5-WAGON-5D-PREFL-01	4838	1817	1510	Auto-Data Skoda Superb II Combi specifications	https://www.auto-data.net/en/skoda-superb-ii-combi-1.4-tsi-125hp-14294
EU-SKODA-SUPERB-II-3T5-WAGON-5D-FACELIFT-01	4833	1817	1511	Auto-Data Skoda Superb II Combi facelift specifications	https://www.auto-data.net/en/skoda-superb-ii-combi-facelift-2013-1.4-tsi-125hp-19264
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 generation specifications	https://www.auto-data.net/en/volkswagen-passat-model-882
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat B6 generation specifications	https://www.auto-data.net/en/volkswagen-passat-model-882
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451	Auto-Data Citroen C5 X7 generation specifications	https://www.auto-data.net/en/citroen-c5-model-704
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479	Auto-Data Citroen C5 X7 generation specifications	https://www.auto-data.net/en/citroen-c5-model-704
EU-VW-PASSAT-CC-B6-357-COUPE-4D-01	4799	1855	1417	Auto-Data Volkswagen Passat CC I 2.0 TDI 4MOTION specifications	https://www.auto-data.net/en/volkswagen-passat-cc-i-2.0-tdi-bmt-170hp-4motion-dsg-16851
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4201-4300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/alfa-romeo-mito-1.6-jtdm-120hp-16680 "https://www.auto-data.net/en/alfa-romeo-mito-1.6-jtdm-120hp-16680"
[2]: https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-1.6-tdi-105hp-16879?utm_source=chatgpt.com "Seat Ibiza IV (facelift 2012) 1.6 TDI (105 Hp)"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4201-4300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4201-4300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5029 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2191 行）

