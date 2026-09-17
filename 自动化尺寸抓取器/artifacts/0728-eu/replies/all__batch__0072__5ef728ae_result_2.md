# 任务：all 第 7101-7200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0072__5ef728ae


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7101-7200 行

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
all 第 7101-7200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7101-7200_ktype_dimension_mapping_final.tsv
- all_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FIAT-127-DIESEL-EARLY-HATCHBACK-3D-01	3745	1545	1410
EU-FIAT-127-PANORAMA-WAGON-01	3920	1545	1425
EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	3595	1527	1380
EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	3645	1527	1380
EU-FIAT-127-SERIES-II-HATCHBACK-5D-01	3645	1527	1380
EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	3711	1552	1370
EU-FIAT-127-SERIES-III-HATCHBACK-5D-01	3711	1552	1370
EU-FIAT-127-SERIES-II-SPORT-HATCHBACK-3D-01	3645	1536	1380
EU-FIAT-127-SERIES-I-SPECIAL-HATCHBACK-3D-01	3635	1527	1380
EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	3745	1545	1405
EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	4285	1650	1310
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	3895	1620	1380
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	3895	1620	1380
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	3895	1620	1355
EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	3885	1620	1380
EU-LANCIA-DELTA-I-HATCHBACK-EVOLUZIONE-01	3900	1770	1365
EU-LANCIA-DELTA-I-HATCHBACK-INTEGRALE-16V-01	3898	1686	1365
EU-LANCIA-DELTA-I-HATCHBACK-INTEGRALE-8V-01	3900	1700	1380
EU-LANCIA-DELTA-II-HATCHBACK-01	4011	1703	1430
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385
EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	4590	1752	1433
EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	4590	1758	1435
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435
EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	4590	1755	1440
EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	4605	1752	1435
EU-LANCIA-TREVI-828-SEDAN-01	4355	1706	1400
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440
EU-MERCEDES-BENZ-VITO-W638-BUS-01	4660	1880	1875
EU-RENAULT-18-135-WAGON-1982-01	4487	1689	1402
EU-RENAULT-18-135-WAGON-EARLY-01	4451	1682	1402
EU-RENAULT-18-135-WAGON-PHASE2-01	4487	1696	1402
EU-RENAULT-19-I-HATCHBACK-BC53-01	4156	1694	1412
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417
EU-RENAULT-19-II-L53-CHAMADE-SEDAN-01	4248	1696	1412
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417
EU-RENAULT-19-I-SEDAN-L53-01	4262	1694	1412
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	4498	1714	1400
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	4510	1722	1385
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415
EU-RENAULT-25-B29-HATCHBACK-01	4715	1805	1415
EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	4500	1732	1431
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	127	1	Kombi	Frontantrieb	Benzin	37	50	Jan 1977	Dec 1986	2024-03-01	7568
Porsche	356	A 1600	Coupe	Heckantrieb	Benzin	44	60	Jan 1955	Dec 1959	2024-03-01	7570
Porsche	356	A 1600 Super	Coupe	Heckantrieb	Benzin	55	75	Jan 1955	Dec 1959	2024-03-01	7571
Porsche	356	B 1600	Coupe	Heckantrieb	Benzin	44	60	Sep 1959	Aug 1963	2024-03-01	7574
Porsche	356	B 1600 Super 75	Coupe	Heckantrieb	Benzin	55	75	Jan 1959	Dec 1963	2024-03-01	7575
Porsche	356	B 1600 Super 90	Coupe	Heckantrieb	Benzin	66	90	Jan 1959	Dec 1963	2024-03-01	7576
Porsche	356	C 1600	Coupe	Heckantrieb	Benzin	55	75	Jan 1963	Dec 1965	2024-03-01	7577
Porsche	356	C 1600 SC	Coupe	Heckantrieb	Benzin	70	95	Jan 1963	Dec 1965	2024-03-01	7578
Porsche	356	B 2000 GS Carrera 2	Coupe	Heckantrieb	Benzin	96	130	Jan 1961	Dec 1964	2024-03-01	7579
Porsche	356	C 2000 GS Carrera 2	Coupe	Heckantrieb	Benzin	96	130	Jan 1961	Dec 1964	2024-03-01	7580
Lancia	Beta	1600	Coupe	Frontantrieb	Benzin	74	101	Apr 1976	Dec 1984	2024-03-01	7581
Porsche	356	1100	Coupe	Heckantrieb	Benzin	29	40	Jan 1950	Dec 1955	2024-03-01	7582
Porsche	356	1300 S	Coupe	Heckantrieb	Benzin	44	60	Jan 1950	Dec 1955	2024-03-01	7584
Porsche	356	1300	Coupe	Heckantrieb	Benzin	32	44	Jan 1950	Dec 1955	2024-03-01	7585
Lancia	Beta	1300	Coupe	Frontantrieb	Benzin	62	84	Dec 1981	Dec 1984	2024-03-01	7586
Porsche	356	1500	Coupe	Heckantrieb	Benzin	40	55	Jan 1950	Dec 1955	2024-03-01	7587
Porsche	356	1500	Coupe	Heckantrieb	Benzin	44	60	Jan 1950	Dec 1955	2024-03-01	7588
Lancia	Beta	2000	Coupe	Frontantrieb	Benzin	85	116	Jan 1981	Dec 1984	2024-03-01	7589
Porsche	356	1500 S	Coupe	Heckantrieb	Benzin	51	70	Jan 1954	Dec 1955	2024-03-01	7591
Lancia	Beta	2000	Coupe	Frontantrieb	Benzin	88	120	Apr 1976	Dec 1984	2024-03-01	7592
Renault	21	2.1 D 4X4	Kombi	Allrad	Diesel	48	65	Oct 1988	May 1992	2024-03-01	7593
Lancia	Beta	2000 I.e.	Coupe	Frontantrieb	Benzin	90	122	Dec 1981	Dec 1984	2024-03-01	7594
Lancia	Beta	2000 VX	Coupe	Frontantrieb	Benzin	99	135	Jul 1983	Dec 1984	2024-03-01	7595
Porsche	356	A 1500 GS Carrera	Coupe	Heckantrieb	Benzin	81	110	Jan 1955	Dec 1961	2024-03-01	7596
Porsche	356	A 1600 GS Carrera	Coupe	Heckantrieb	Benzin	85	115	Jan 1955	Dec 1961	2024-03-01	7597
Lancia	Beta	2000	Schrägheck	Frontantrieb	Benzin	85	116	Apr 1979	Sep 1984	2024-03-01	7598
Porsche	356	A 1600 GS Carrera	Coupe	Heckantrieb	Benzin	77	105	Jan 1955	Dec 1961	2024-03-01	7600
Lancia	Beta	2000	Schrägheck	Frontantrieb	Benzin	88	120	May 1976	May 1978	2024-03-01	7601
Lancia	Beta	2000 Volumex	Schrägheck	Frontantrieb	Benzin	99	135	Jul 1983	Sep 1984	2024-03-01	7602
Porsche	356	A 1500 GS Carrera	Coupe	Heckantrieb	Benzin	73	100	Jan 1955	Dec 1961	2024-03-01	7603
Porsche	356	C 2000 GS Carrera 2	Coupe	Heckantrieb	Benzin	103	140	Oct 1961	Mar 1968	2024-03-01	7604
Mercedes-benz	Vito / mixto	110 CDI	Kasten	Heckantrieb	Diesel	70	95	Sep 2010	Aug 2014	2025-12-01	7605
Mercedes-benz	Vito / mixto	113 CDI	Kasten	Heckantrieb	Diesel	100	136	Sep 2010	Aug 2014	2025-12-01	7606
Lancia	Beta	2	Targa	Heckantrieb	Benzin	88	120	Sep 1975	May 1981	2024-03-01	7607
Porsche	912	1.6	Targa	Heckantrieb	Benzin	66	90	Mar 1965	Feb 1970	2024-03-01	7608
Porsche	912	1.6	Coupe	Heckantrieb	Benzin	66	90	Jan 1965	Dec 1969	2024-03-01	7609
Mercedes-benz	Vito / mixto	116 CDI	Kasten	Heckantrieb	Diesel	120	163	Sep 2010	Aug 2014	2025-12-01	7610
Lancia	Beta	2000	Targa	Frontantrieb	Benzin	85	116	Apr 1979	Oct 1986	2024-03-01	7611
Lancia	Beta	2000	Targa	Frontantrieb	Benzin	88	120	May 1976	Nov 1979	2024-03-01	7612
Lancia	Delta i	1.6 HF Turbo	Schrägheck	Frontantrieb	Benzin	96	131	Oct 1983	Dec 1986	2024-03-01	7613
Mercedes-benz	Vito / mixto	122 CDI	Kasten	Heckantrieb	Diesel	165	224	Sep 2010	Aug 2014	2025-12-01	7614
Lancia	Thema	2000 16V	Stufenheck	Frontantrieb	Benzin	112	152	Aug 1992	Dec 1993	2024-03-01	7615
Renault	21	2.1 D	Stufenheck	Frontantrieb	Diesel	51	69	Oct 1992	Jun 1994	2024-03-01	7616
Renault	21	2.1 D	Stufenheck	Frontantrieb	Diesel	53	72	May 1989	Jun 1994	2024-03-01	7617
Renault	21	2.1 D	Schrägheck	Frontantrieb	Diesel	53	72	Sep 1989	Dec 1992	2024-03-01	7618
Renault	21	2.1 D	Schrägheck	Frontantrieb	Diesel	51	69	Apr 1992	Jun 1994	2024-03-01	7619
Lancia	Trevi	2000 Volumex	Stufenheck	Frontantrieb	Benzin	99	135	Aug 1983	May 1985	2024-03-01	7620
Mercedes-benz	Vito	110 CDI	Bus	Heckantrieb	Diesel	70	95	Sep 2010	Aug 2014	2024-03-01	7621
Lancia	Beta	1600	Schrägheck	Frontantrieb	Benzin	74	101	Aug 1973	Jul 1982	2024-03-01	7622
Lancia	Thema	2500 Turbo DS	Stufenheck	Frontantrieb	Diesel	85	116	May 1992	Jul 1994	2024-03-01	7623
Lancia	Thema	8.32	Stufenheck	Frontantrieb	Benzin	151	205	Oct 1987	May 1992	2024-03-01	7624
Mercedes-benz	Vito	113 CDI	Bus	Heckantrieb	Diesel	100	136	Sep 2010	-	2024-03-01	7625
Renault	19 i	1.4	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1989	May 1993	2024-03-01	7626
Mercedes-benz	Vito	116 CDI	Bus	Heckantrieb	Diesel	120	163	Sep 2010	-	2024-03-01	7627
Lancia	Thema	2000 16V Turbo	Stufenheck	Frontantrieb	Benzin	148	201	Oct 1992	Jul 1994	2024-03-01	7628
Lancia	Thema	2500 Turbo DS	Kombi	Frontantrieb	Diesel	74	101	Mar 1987	Sep 1990	2024-03-01	7629
Lancia	Thema	2000 Turbo 16V	Kombi	Frontantrieb	Benzin	148	201	Nov 1992	Jul 1994	2024-03-01	7630
Lancia	Y10	1.0 Fire Allrad	Schrägheck	Allrad	Benzin	32	44	Dec 1986	Feb 1989	2024-03-01	7631
Lancia	Prisma	1.5	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1985	Feb 1992	2024-03-01	7632
Lancia	Prisma	1.6	Stufenheck	Frontantrieb	Benzin	73	99	Aug 1986	Feb 1992	2024-03-01	7633
Lancia	Prisma	1.5	Stufenheck	Frontantrieb	Benzin	59	80	May 1986	Jul 1989	2024-03-01	7634
Lancia	Delta i	1.6 GT I.e.	Schrägheck	Frontantrieb	Benzin	80	109	Aug 1986	Aug 1988	2024-03-01	7635
Lancia	Delta i	1.6 HF Turbo	Schrägheck	Frontantrieb	Benzin	103	140	Aug 1986	Aug 1988	2024-03-01	7636
Lancia	Delta i	1.9 Turbo DS	Schrägheck	Frontantrieb	Diesel	59	80	Oct 1986	Dec 1989	2024-03-01	7637
Lancia	Delta i	2.0 HF Integrale	Schrägheck	Allrad	Benzin	122	166	Nov 1986	Aug 1988	2024-03-01	7638
Lancia	Thema	2000 16V Turbo	Stufenheck	Frontantrieb	Benzin	133	181	Dec 1988	Jun 1990	2024-03-01	7639
Lancia	Thema	2500 Turbo DS	Kombi	Frontantrieb	Diesel	85	116	Sep 1992	Jul 1994	2024-03-01	7640
Lancia	Gamma	2500	Schrägheck	Frontantrieb	Benzin	103	140	Mar 1978	Oct 1986	2024-03-01	7641
Lancia	Gamma	2500	Coupe	Frontantrieb	Benzin	103	140	Sep 1977	Oct 1986	2024-03-01	7642
Lancia	Fulvia	1.3	Coupe	Frontantrieb	Benzin	65	88	Sep 1968	Jul 1975	2024-03-01	7643
Porsche	356 /speedster	1500	Cabriolet	Heckantrieb	Benzin	44	60	Jan 1950	Dec 1955	2024-03-01	7644
Porsche	356 /speedster	1300 S	Cabriolet	Heckantrieb	Benzin	44	60	Jan 1950	Dec 1955	2024-03-01	7645
Porsche	356 /speedster	1500 S	Cabriolet	Heckantrieb	Benzin	51	70	Jan 1950	Dec 1955	2024-03-01	7646
Porsche	356 /speedster	A 1600	Cabriolet	Heckantrieb	Benzin	44	60	Jan 1955	Dec 1959	2024-03-01	7647
Mercedes-benz	Vito	122 CDI	Bus	Heckantrieb	Diesel	165	224	Sep 2010	-	2024-03-01	7648
Porsche	356 /speedster	A 1600 GS Carrera	Cabriolet	Heckantrieb	Benzin	85	115	Jan 1955	Dec 1959	2024-03-01	7649
Porsche	356 /speedster	A 1500 GS Carrera	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1955	Dec 1959	2024-03-01	7650
Porsche	356 /speedster	B 1600 Super 90	Cabriolet	Heckantrieb	Benzin	66	90	Jan 1959	Dec 1963	2024-03-01	7651
Porsche	356 /speedster	C 1600	Cabriolet	Heckantrieb	Benzin	55	75	Jan 1963	Dec 1965	2024-03-01	7652
Renault	25	2.5 V6 Turbo	Schrägheck	Frontantrieb	Benzin	151	205	Jan 1990	Dec 1992	2024-03-01	7653
Porsche	356 /speedster	C 1600 SC	Cabriolet	Heckantrieb	Benzin	70	95	Jan 1963	Dec 1965	2024-03-01	7654
Porsche	356 /speedster	C 2000 GS Carrera 2	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1963	Dec 1965	2024-03-01	7655
Porsche	356 /speedster	B 2000 GS Carrera 2	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1959	Dec 1963	2024-03-01	7656
Porsche	356 /speedster	1100	Cabriolet	Heckantrieb	Benzin	29	40	Jan 1950	Dec 1955	2024-03-01	7657
Porsche	356 /speedster	1300	Cabriolet	Heckantrieb	Benzin	32	44	Jan 1950	Dec 1955	2024-03-01	7658
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	100	136	Jul 2010	-	2024-03-01	7659
Renault	25	2.2	Schrägheck	Frontantrieb	Benzin	91	124	Apr 1984	Dec 1989	2024-03-01	7660
Porsche	356 /speedster	B 1600	Cabriolet	Heckantrieb	Benzin	44	60	Sep 1959	Aug 1963	2024-03-01	7662
Renault	25	2.8 V6	Schrägheck	Frontantrieb	Benzin	115	156	Jun 1987	Feb 1990	2024-03-01	7663
Porsche	356 /speedster	A 1600 S	Cabriolet	Heckantrieb	Benzin	55	75	Jan 1955	Dec 1959	2024-03-01	7664
Porsche	356 /speedster	A 1500 GS Carrera	Cabriolet	Heckantrieb	Benzin	73	99	Jan 1955	Dec 1961	2024-03-01	7665
Porsche	356 /speedster	A 1600 GS Carrera	Cabriolet	Heckantrieb	Benzin	77	105	Jan 1955	Dec 1961	2024-03-01	7666
Renault	25	2.2	Schrägheck	Frontantrieb	Benzin	76	103	Nov 1985	Mar 1989	2024-03-01	7667
Renault	25	2.1 Diesel	Schrägheck	Frontantrieb	Diesel	51	69	Jun 1989	Dec 1992	2024-03-01	7668
Renault	30	2.6	Schrägheck	Frontantrieb	Benzin	96	131	Feb 1975	Jul 1976	2024-03-01	7669
Renault	30	2.6 TS	Schrägheck	Frontantrieb	Benzin	94	128	Jul 1978	Jan 1984	2024-03-01	7670
Renault	30	2.1 Turbo-d	Schrägheck	Frontantrieb	Diesel	63	86	Feb 1982	Mar 1986	2024-03-01	7671
Renault	18	1.6 TS	Stufenheck	Frontantrieb	Benzin	71	97	May 1982	Jul 1986	2024-03-01	7672
Renault	18	2	Stufenheck	Frontantrieb	Benzin	77	105	May 1982	Jul 1986	2024-03-01	7673
Renault	18	1.6 TS	Kombi	Frontantrieb	Benzin	71	97	May 1982	Jul 1986	2024-03-01	7674


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Porsche 356 Coupe、Porsche 912、Lancia Beta、Gamma、Fulvia、Y10 4WD、Thema 8.32、Renault 18 Sedan、Renault 19 I 三门/五门等尺寸组闭合。
* W639 已按官方资料拆分为 Panel Van 的 Compact、Long 标准顶、Long 高顶、Extra-long 标准顶，以及乘用车身的三种长度；官方资料明确高顶仅用于 Long 车身，宽度统一为不含后视镜的 1901 mm。([Dezo's Garage][1])
* Renault 19 I 当前证据得到宽度 1684 mm，与既有 `BC53-01` 的 1694 mm 冲突，因此未覆盖旧组，按规则创建新的 `3D-02` 和 `5D-02`。([汽车目录][2])
* 当前剩余阻塞集中在两个簇：Porsche `356 /speedster` 的 Cabriolet/Speedster边界，以及跨越 Renault 21 1989 改款的 2.1 D 4x4 Wagon。

## 当前批次进度

* 输入 Ktype：100
* 已 READY 的输入 Ktype：82
* PENDING 输入 Ktype：18
* READY 映射行：107
* PENDING 映射行：18
* 当前已引用尺寸组：43
* 本轮首次创建尺寸组：24
* 复用既有尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7568	7568	Wagon	127 Panorama	127	3	EU-FIAT-127-PANORAMA-WAGON-01	HIGH		READY
7570	7570	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7571	7571	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7574	7574	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7575	7575	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7576	7576	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7577	7577	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7578	7578	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7579	7579	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7580	7580	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7581	7581	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7582	7582	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7584	7584	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7585	7585	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7586	7586	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7587	7587	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7588	7588	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7589	7589	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7591	7591	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7592	7592	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7593	7593	Wagon	21 Nevada 4x4	K48	5		MEDIUM	生产区间跨越1989年改款，候选为改款前与改款后4x4旅行车外廓。	PENDING: 尚未闭合改款前后2.1 D 4x4旅行车分支
7594	7594	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7595	7595	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7596	7596	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7597	7597	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7598	7598	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7600	7600	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7601	7601	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7602	7602	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7603	7603	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7604	7604	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7605_compact	7605	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7605_long	7605	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7605_long_highroof	7605	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7605_extralong	7605	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7606_compact	7606	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7606_long	7606	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7606_long_highroof	7606	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7606_extralong	7606	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7607	7607	Targa	Beta Montecarlo	137AS	2	EU-LANCIA-BETA-MONTECARLO-TARGA-2D-01	HIGH	后置驱动记录对应Beta Montecarlo Targa车身。	READY
7608	7608	Targa	912	912	2	EU-PORSCHE-912-TARGA-2D-01	HIGH		READY
7609	7609	Coupe	912	912	2	EU-PORSCHE-912-COUPE-2D-01	HIGH		READY
7610_compact	7610	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7610_long	7610	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7610_long_highroof	7610	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7610_extralong	7610	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7611	7611	Targa	Beta Spider	828BS	2	EU-LANCIA-BETA-828-SPIDER-2D-01	HIGH		READY
7612	7612	Targa	Beta Spider	828BS	2	EU-LANCIA-BETA-828-SPIDER-2D-01	HIGH		READY
7613_fl1982	7613	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	覆盖1982年改款后至1986年改款前外廓。	READY
7613_fl1986	7613	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH	覆盖1986年改款后HF Turbo外廓。	READY
7614_compact	7614	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7614_long	7614	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7614_long_highroof	7614	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7614_extralong	7614	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7615	7615	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7616	7616	Sedan	21 Phase II	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH		READY
7617_phase1	7617	Sedan	21 Phase I	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	生产起点覆盖改款前外廓。	READY
7617_phase2	7617	Sedan	21 Phase II	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	生产区间覆盖改款后外廓。	READY
7618	7618	Hatchback	21 Phase II	B48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH		READY
7619	7619	Hatchback	21 Phase II	B48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH		READY
7620	7620	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-01	HIGH		READY
7621_compact	7621	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7621_long	7621	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7621_extralong	7621	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7622	7622	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7623	7623	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7624	7624	Sedan	Thema I 8.32	834	4	EU-LANCIA-THEMA-I-8-32-SEDAN-01	HIGH	8.32专属外廓。	READY
7625_compact	7625	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7625_long	7625	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7625_extralong	7625	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7626_3dr	7626	Hatchback	19 I	B53	3	EU-RENAULT-19-I-HATCHBACK-3D-02	HIGH	三门物理分支。	READY
7626_5dr	7626	Hatchback	19 I	C53	5	EU-RENAULT-19-I-HATCHBACK-5D-02	HIGH	五门物理分支。	READY
7627_compact	7627	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7627_long	7627	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7627_extralong	7627	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7628	7628	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7629	7629	Wagon	Thema I Series 1/2	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	HIGH	系列1与系列2旅行车三维一致，复用稳定尺寸组。	READY
7630	7630	Wagon	Thema I Series 3	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	HIGH		READY
7631	7631	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	HIGH	四驱宽体/增高外廓。	READY
7632	7632	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7633	7633	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7634	7634	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7635	7635	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH		READY
7636	7636	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH		READY
7637	7637	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH		READY
7638	7638	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-HATCHBACK-INTEGRALE-8V-01	HIGH		READY
7639	7639	Sedan	Thema I Series 2	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	HIGH		READY
7640	7640	Wagon	Thema I Series 3	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	HIGH		READY
7641	7641	Hatchback	Gamma	830	5	EU-LANCIA-GAMMA-830-HATCHBACK-5D-01	HIGH		READY
7642	7642	Coupe	Gamma Coupe	830	2	EU-LANCIA-GAMMA-830-COUPE-2D-01	HIGH		READY
7643	7643	Coupe	Fulvia Coupe	818	2	EU-LANCIA-FULVIA-818-COUPE-2D-01	HIGH		READY
7644	7644	Convertible	356 Pre-A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7645	7645	Convertible	356 Pre-A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7646	7646	Convertible	356 Pre-A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7647	7647	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7648_compact	7648	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7648_long	7648	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7648_extralong	7648	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7649	7649	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7650	7650	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7651	7651	Convertible	356 B		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7652	7652	Convertible	356 C		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7653	7653	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7654	7654	Convertible	356 C		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7655	7655	Convertible	356 C		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7656	7656	Convertible	356 B		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7657	7657	Convertible	356 Pre-A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7658	7658	Convertible	356 Pre-A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7659_compact	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7659_long	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7659_extralong	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7660	7660	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7662	7662	Convertible	356 B		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7663	7663	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7664	7664	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7665	7665	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7666	7666	Convertible	356 A		2		LOW	输入Model合并356与Speedster，尚不能确认该Ktype仅对应标准Cabriolet还是同时覆盖低风挡Speedster。	PENDING: Cabriolet/Speedster物理分支未闭合
7667	7667	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7668	7668	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7669	7669	Hatchback	30 pre-facelift	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	HIGH		READY
7670	7670	Hatchback	30 facelift	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	HIGH		READY
7671	7671	Hatchback	30 facelift	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	HIGH		READY
7672	7672	Sedan	18 Phase 2	134	4	EU-RENAULT-18-134-SEDAN-1982-01	HIGH		READY
7673	7673	Sedan	18 Phase 2	134	4	EU-RENAULT-18-134-SEDAN-1982-01	HIGH		READY
7674	7674	Wagon	18 Phase 2	135	5	EU-RENAULT-18-135-WAGON-1982-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-356-PRE-A-COUPE-2D-01	3950	1660	1300	Automobile-Catalog 1954 Porsche 356 1500 Coupe	https://www.automobile-catalog.com/car/1954/2580380/porsche_356_1500_coupe.html
EU-PORSCHE-356-A-COUPE-2D-01	3950	1670	1310	Automobile-Catalog 1958 Porsche 356 A 1600 Coupe	https://www.automobile-catalog.com/car/1958/2580965/porsche_356_a1600_coupe.html
EU-PORSCHE-356-B-COUPE-2D-01	4010	1670	1330	Automobile-Catalog 1959 Porsche 356 B 1600 Coupe	https://www.automobile-catalog.com/car/1959/2581235/porsche_356_b1600_coupe.html
EU-PORSCHE-356-C-COUPE-2D-01	4010	1670	1315	Automobile-Catalog 1964 Porsche 356 C 1600 C Coupe	https://www.automobile-catalog.com/car/1964/2581820/porsche_356_c1600_c_coupe.html
EU-LANCIA-BETA-828-COUPE-2D-01	3995	1650	1285	Automobile-Catalog 1976 Lancia Beta Coupe 1600	https://www.automobile-catalog.com/car/1976/34955/lancia_beta_coupe_1600_2a_serie.html
EU-LANCIA-BETA-MONTECARLO-TARGA-2D-01	3813	1696	1190	Automobile-Catalog 1976 Lancia Beta Montecarlo	https://www.automobile-catalog.com/car/1976/1377590/lancia_beta_montecarlo.html
EU-PORSCHE-912-TARGA-2D-01	4163	1610	1320	Automobile-Catalog 1967 Porsche 912 Targa	https://www.automobile-catalog.com/car/1967/2589275/porsche_912_targa_4-speed.html
EU-PORSCHE-912-COUPE-2D-01	4163	1610	1320	Automobile-Catalog 1965 Porsche 912 Coupe	https://www.automobile-catalog.com/car/1965/2588510/porsche_912_coupe_4-speed.html
EU-LANCIA-BETA-828-SPIDER-2D-01	4035	1650	1263	Automobile-Catalog 1979 Lancia Beta Spyder 2000	https://www.automobile-catalog.com/car/1979/1376765/lancia_beta_spyder_2000_2a_serie_fl.html
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	4763	1901	1902	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	5008	1901	1902	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	5008	1901	2329	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	5238	1901	1900	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	4763	1901	1875	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	5008	1901	1875	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	5238	1901	1872	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-LANCIA-THEMA-I-8-32-SEDAN-01	4590	1733	1420	Automobile-Catalog 1987 Lancia Thema 8.32	https://www.automobile-catalog.com/car/1987/54410/lancia_thema_8_32.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	3392	1537	1460	Automobile-Catalog 1987 Lancia Y10 4WD	https://www.automobile-catalog.com/car/1987/1380740/lancia_y10_4wd.html
EU-LANCIA-GAMMA-830-HATCHBACK-5D-01	4580	1730	1410	Automobile-Catalog 1978 Lancia Gamma 2500	https://www.automobile-catalog.com/car/1978/1378340/lancia_gamma_2500.html
EU-LANCIA-GAMMA-830-COUPE-2D-01	4485	1730	1330	Automobile-Catalog 1978 Lancia Gamma Coupe 2500	https://www.automobile-catalog.com/car/1978/1378370/lancia_gamma_coupe_2500.html
EU-LANCIA-FULVIA-818-COUPE-2D-01	3975	1555	1300	Automobile-Catalog 1969 Lancia Fulvia Coupe Rallye 1.3 S	https://www.automobile-catalog.com/car/1969/1376030/lancia_fulvia_coupe_rallye_1_3_s.html
EU-RENAULT-19-I-HATCHBACK-3D-02	4156	1684	1412	Automobile-Catalog 1990 Renault 19 1.4	https://www.automobile-catalog.com/car/1990/2942000/renault_19_1_4_80_automatic.html
EU-RENAULT-19-I-HATCHBACK-5D-02	4156	1684	1412	Automobile-Catalog 1990 Renault 19 1.4	https://www.automobile-catalog.com/car/1990/2942000/renault_19_1_4_80_automatic.html
EU-RENAULT-18-134-SEDAN-1982-01	4394	1689	1405	Automobile-Catalog 1982 Renault 18 TS	https://www.automobile-catalog.com/car/1982/2931020/renault_18_ts.html
```

## 下一步优先处理

1. 按发动机与生产阶段核对 17 个 `356 /speedster` Ktype 是否仅属于 Cabriolet，或需要派生 Cabriolet/Speedster 两套物理分支。
2. 闭合 Ktype `7593` 的 Renault 21 Nevada 2.1 D 4x4 改款前、改款后尺寸组。
3. PENDING 清零后仅执行一次引用闭合和表头机械检查，随后直接输出两张完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf "https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf"
[2]: https://www.automobile-catalog.com/make/renault/19/19/1989.html "https://www.automobile-catalog.com/make/renault/19/19/1989.html"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7101-7200_ktype_dimension_mapping_final.tsv
- all_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已将 Ktype `7593` 拆分为 Renault 21 Phase I 与 Phase II 两个 4x4 Wagon 外廓；改款前为 `4644×1722×1440 mm`，改款后复用既有 `4693×1726×1450 mm` 尺寸组。([汽车目录][1])
* Porsche 356 开篷车型已按实际车身分支拆分为 Cabriolet、Speedster、Convertible D 与 Roadster；C 系列及 Carrera 2 对应记录按已确认的 Cabriolet 边界落盘。([porsche.com][2])
* 已完成固定表头、`id` 唯一性、尺寸组唯一性、映射引用闭合、字段完整性和孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* 最终映射行：140
* PENDING：0
* 最终尺寸组：53
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7568	7568	Wagon	127 Panorama	127	3	EU-FIAT-127-PANORAMA-WAGON-01	HIGH		READY
7570	7570	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7571	7571	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7574	7574	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7575	7575	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7576	7576	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7577	7577	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7578	7578	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7579	7579	Coupe	356 B	356B	2	EU-PORSCHE-356-B-COUPE-2D-01	HIGH		READY
7580	7580	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7581	7581	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7582	7582	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7584	7584	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7585	7585	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7586	7586	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7587	7587	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7588	7588	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7589	7589	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7591	7591	Coupe	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-COUPE-2D-01	HIGH		READY
7592	7592	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7593_phase1	7593	Wagon	21 Phase I	K48	5	EU-RENAULT-21-K48-WAGON-PHASE1-4X4-01	HIGH	1988年改款前4x4旅行车外廓。	READY
7593_phase2	7593	Wagon	21 Phase II	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	1989年改款后4x4旅行车外廓。	READY
7594	7594	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7595	7595	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828-COUPE-2D-01	HIGH		READY
7596	7596	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7597	7597	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7598	7598	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7600	7600	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7601	7601	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7602	7602	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7603	7603	Coupe	356 A	356A	2	EU-PORSCHE-356-A-COUPE-2D-01	HIGH		READY
7604	7604	Coupe	356 C	356C	2	EU-PORSCHE-356-C-COUPE-2D-01	HIGH		READY
7605_compact	7605	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7605_long	7605	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7605_long_highroof	7605	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7605_extralong	7605	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7606_compact	7606	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7606_long	7606	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7606_long_highroof	7606	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7606_extralong	7606	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7607	7607	Targa	Beta Montecarlo	137AS	2	EU-LANCIA-BETA-MONTECARLO-TARGA-2D-01	HIGH	后置驱动记录对应Beta Montecarlo Targa车身。	READY
7608	7608	Targa	912	912	2	EU-PORSCHE-912-TARGA-2D-01	HIGH		READY
7609	7609	Coupe	912	912	2	EU-PORSCHE-912-COUPE-2D-01	HIGH		READY
7610_compact	7610	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7610_long	7610	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7610_long_highroof	7610	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7610_extralong	7610	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7611	7611	Targa	Beta Spider	828BS	2	EU-LANCIA-BETA-828-SPIDER-2D-01	HIGH		READY
7612	7612	Targa	Beta Spider	828BS	2	EU-LANCIA-BETA-828-SPIDER-2D-01	HIGH		READY
7613_fl1982	7613	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	覆盖1982年改款后至1986年改款前外廓。	READY
7613_fl1986	7613	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH	覆盖1986年改款后HF Turbo外廓。	READY
7614_compact	7614	Van	Vito W639 facelift	639.601		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	HIGH	紧凑车身。	READY
7614_long	7614	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	HIGH	长车身标准顶。	READY
7614_long_highroof	7614	Van	Vito W639 facelift	639.603		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	HIGH	长车身高顶。	READY
7614_extralong	7614	Van	Vito W639 facelift	639.605		EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	HIGH	超长车身标准顶。	READY
7615	7615	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7616	7616	Sedan	21 Phase II	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH		READY
7617_phase1	7617	Sedan	21 Phase I	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	生产起点覆盖改款前外廓。	READY
7617_phase2	7617	Sedan	21 Phase II	L48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	生产区间覆盖改款后外廓。	READY
7618	7618	Hatchback	21 Phase II	B48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH		READY
7619	7619	Hatchback	21 Phase II	B48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH		READY
7620	7620	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-01	HIGH		READY
7621_compact	7621	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7621_long	7621	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7621_extralong	7621	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7622	7622	Hatchback	Beta HPE	828BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH		READY
7623	7623	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7624	7624	Sedan	Thema I 8.32	834	4	EU-LANCIA-THEMA-I-8-32-SEDAN-01	HIGH	8.32专属外廓。	READY
7625_compact	7625	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7625_long	7625	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7625_extralong	7625	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7626_3dr	7626	Hatchback	19 I	B53	3	EU-RENAULT-19-I-HATCHBACK-3D-02	HIGH	三门物理分支。	READY
7626_5dr	7626	Hatchback	19 I	C53	5	EU-RENAULT-19-I-HATCHBACK-5D-02	HIGH	五门物理分支。	READY
7627_compact	7627	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7627_long	7627	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7627_extralong	7627	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7628	7628	Sedan	Thema I Series 3	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	HIGH		READY
7629	7629	Wagon	Thema I Series 1/2	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	HIGH	系列1与系列2旅行车三维一致，复用稳定尺寸组。	READY
7630	7630	Wagon	Thema I Series 3	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	HIGH		READY
7631	7631	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	HIGH	四驱宽体/增高外廓。	READY
7632	7632	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7633	7633	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7634	7634	Sedan	Prisma	831AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH		READY
7635	7635	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH		READY
7636	7636	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH		READY
7637	7637	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH		READY
7638	7638	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-HATCHBACK-INTEGRALE-8V-01	HIGH		READY
7639	7639	Sedan	Thema I Series 2	834	4	EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	HIGH		READY
7640	7640	Wagon	Thema I Series 3	834	5	EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	HIGH		READY
7641	7641	Hatchback	Gamma	830	5	EU-LANCIA-GAMMA-830-HATCHBACK-5D-01	HIGH		READY
7642	7642	Coupe	Gamma Coupe	830	2	EU-LANCIA-GAMMA-830-COUPE-2D-01	HIGH		READY
7643	7643	Coupe	Fulvia Coupe	818	2	EU-LANCIA-FULVIA-818-COUPE-2D-01	HIGH		READY
7644_cabriolet	7644	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7644_speedster	7644	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7645_cabriolet	7645	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7645_speedster	7645	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7646_cabriolet	7646	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7646_speedster	7646	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7647_cabriolet	7647	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7647_speedster	7647	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7647_convertibled	7647	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CONVERTIBLE-D-2D-01	HIGH	Convertible D外廓。	READY
7648_compact	7648	MPV	Vito W639 facelift	639.701		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7648_long	7648	MPV	Vito W639 facelift	639.703		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7648_extralong	7648	MPV	Vito W639 facelift	639.705		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7649_cabriolet	7649	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7649_speedster	7649	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7650_cabriolet	7650	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7650_speedster	7650	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7651_cabriolet	7651	Convertible	356 B	356B	2	EU-PORSCHE-356-B-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7651_roadster	7651	Convertible	356 B	356B	2	EU-PORSCHE-356-B-ROADSTER-2D-01	HIGH	Roadster外廓。	READY
7652	7652	Convertible	356 C	356C	2	EU-PORSCHE-356-C-CABRIOLET-2D-01	HIGH	C系列开篷版Cabriolet外廓。	READY
7653	7653	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7654	7654	Convertible	356 C	356C	2	EU-PORSCHE-356-C-CABRIOLET-2D-01	HIGH	C系列开篷版Cabriolet外廓。	READY
7655	7655	Convertible	356 C	356C	2	EU-PORSCHE-356-C-CABRIOLET-2D-01	HIGH	Carrera 2开篷版Cabriolet外廓。	READY
7656	7656	Convertible	356 B	356B	2	EU-PORSCHE-356-B-CABRIOLET-2D-01	HIGH	Carrera 2开篷版Cabriolet外廓。	READY
7657	7657	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	HIGH	1100版本早于Speedster，仅映射Cabriolet外廓。	READY
7658_cabriolet	7658	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7658_speedster	7658	Convertible	356 Pre-A	356	2	EU-PORSCHE-356-PRE-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7659_compact	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	HIGH	紧凑乘用车身。	READY
7659_long	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	HIGH	长乘用车身。	READY
7659_extralong	7659	MPV	Viano W639 facelift	W639		EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	HIGH	超长乘用车身。	READY
7660	7660	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7662_cabriolet	7662	Convertible	356 B	356B	2	EU-PORSCHE-356-B-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7662_roadster	7662	Convertible	356 B	356B	2	EU-PORSCHE-356-B-ROADSTER-2D-01	HIGH	Roadster外廓。	READY
7663	7663	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7664_cabriolet	7664	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7664_speedster	7664	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7664_convertibled	7664	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CONVERTIBLE-D-2D-01	HIGH	Convertible D外廓。	READY
7665_cabriolet	7665	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7665_speedster	7665	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7666_cabriolet	7666	Convertible	356 A	356A	2	EU-PORSCHE-356-A-CABRIOLET-2D-01	HIGH	标准Cabriolet外廓。	READY
7666_speedster	7666	Convertible	356 A	356A	2	EU-PORSCHE-356-A-SPEEDSTER-2D-01	HIGH	低风挡Speedster外廓。	READY
7667	7667	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7668	7668	Hatchback	25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH		READY
7669	7669	Hatchback	30 pre-facelift	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	HIGH		READY
7670	7670	Hatchback	30 facelift	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	HIGH		READY
7671	7671	Hatchback	30 facelift	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	HIGH		READY
7672	7672	Sedan	18 Phase 2	134	4	EU-RENAULT-18-134-SEDAN-1982-01	HIGH		READY
7673	7673	Sedan	18 Phase 2	134	4	EU-RENAULT-18-134-SEDAN-1982-01	HIGH		READY
7674	7674	Wagon	18 Phase 2	135	5	EU-RENAULT-18-135-WAGON-1982-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7101-7200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-127-PANORAMA-WAGON-01	3920	1545	1425	Automobile-Catalog 1983 Fiat 127 Panorama	https://www.automobile-catalog.com/car/1983/711470/fiat_127_panorama.html
EU-PORSCHE-356-A-COUPE-2D-01	3950	1670	1310	Automobile-Catalog 1958 Porsche 356 A 1600 Coupe	https://www.automobile-catalog.com/car/1958/2580965/porsche_356_a1600_coupe.html
EU-PORSCHE-356-B-COUPE-2D-01	4010	1670	1330	Automobile-Catalog 1959 Porsche 356 B 1600 Coupe	https://www.automobile-catalog.com/car/1959/2581235/porsche_356_b1600_coupe.html
EU-PORSCHE-356-C-COUPE-2D-01	4010	1670	1315	Automobile-Catalog 1964 Porsche 356 C 1600 C Coupe	https://www.automobile-catalog.com/car/1964/2581820/porsche_356_c1600_c_coupe.html
EU-LANCIA-BETA-828-COUPE-2D-01	3995	1650	1285	Automobile-Catalog 1976 Lancia Beta Coupe 1600	https://www.automobile-catalog.com/car/1976/34955/lancia_beta_coupe_1600_2a_serie.html
EU-PORSCHE-356-PRE-A-COUPE-2D-01	3950	1660	1300	Automobile-Catalog 1954 Porsche 356 1500 Coupe	https://www.automobile-catalog.com/car/1954/2580380/porsche_356_1500_coupe.html
EU-RENAULT-21-K48-WAGON-PHASE1-4X4-01	4644	1722	1440	Automobile-Catalog 1988 Renault 21 Nevada GTD 4x4	https://www.automobile-catalog.com/car/1988/2940110/renault_21_nevada_savanna_gtd_4x4.html
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450	Automobile-Catalog 1990 Renault 21 Nevada GTD 4x4	https://www.automobile-catalog.com/car/1990/2940770/renault_21_nevada_savanna_gtd_4x4.html
EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	4285	1650	1310	Automobile-Catalog 1978 Lancia Beta HPE 2000	https://www.automobile-catalog.com/car/1978/1376735/lancia_beta_hpe_2000_2a_serie_fl.html
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-COMPACT-01	4763	1901	1902	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-STANDARD-ROOF-01	5008	1901	1902	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-LONG-HIGH-ROOF-01	5008	1901	2329	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-PANEL-VAN-EXTRA-LONG-STANDARD-ROOF-01	5238	1901	1900	Mercedes-Benz The Vito Panel Van & Dualiner 2011 brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vito-Panel-Van-Dualiner-UK.pdf
EU-LANCIA-BETA-MONTECARLO-TARGA-2D-01	3813	1696	1190	Automobile-Catalog 1976 Lancia Beta Montecarlo	https://www.automobile-catalog.com/car/1976/1377590/lancia_beta_montecarlo.html
EU-PORSCHE-912-TARGA-2D-01	4163	1610	1320	Automobile-Catalog 1967 Porsche 912 Targa	https://www.automobile-catalog.com/car/1967/2589275/porsche_912_targa_4-speed.html
EU-PORSCHE-912-COUPE-2D-01	4163	1610	1320	Automobile-Catalog 1965 Porsche 912 Coupe	https://www.automobile-catalog.com/car/1965/2588510/porsche_912_coupe_4-speed.html
EU-LANCIA-BETA-828-SPIDER-2D-01	4035	1650	1263	Automobile-Catalog 1979 Lancia Beta Spyder 2000	https://www.automobile-catalog.com/car/1979/1376765/lancia_beta_spyder_2000_2a_serie_fl.html
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	3895	1620	1380	Auto-Data Lancia Delta I 831 facelift 1982	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1982-generation-9199
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	3895	1620	1355	Automobile-Catalog 1989 Lancia Delta HF Rallye Turbo	https://www.automobile-catalog.com/car/1989/1379435/lancia_delta_hf_rallye_turbo.html
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435	Automobile-Catalog 1992 Lancia Thema 2.0 ie	https://www.automobile-catalog.com/car/1992/1380245/lancia_thema_2_0_i_e_.html
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415	Auto-Data Renault 21 B48 2.1 D	https://www.auto-data.net/en/renault-21-b48-2.1-d-74hp-10376
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414	Automobile-Catalog 1987 Renault 21 TD	https://www.automobile-catalog.com/car/1987/2939795/renault_21_td.html
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415	Auto-Data Renault 21 Hatchback L48	https://www.auto-data.net/en/renault-21-hatchback-l48-generation-2128
EU-LANCIA-TREVI-828-SEDAN-01	4355	1706	1400	Automobile-Catalog 1980 Lancia Beta Trevi 2000	https://www.automobile-catalog.com/car/1980/1376945/lancia_beta_trevi_2000.html
EU-MERCEDES-BENZ-W639-PASSENGER-COMPACT-01	4763	1901	1875	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-MERCEDES-BENZ-W639-PASSENGER-LONG-01	5008	1901	1875	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-MERCEDES-BENZ-W639-PASSENGER-EXTRA-LONG-01	5238	1901	1872	Mercedes-Benz The Viano 2012 official brochure	https://xr793.com/wp-content/uploads/2022/12/2012-Mercedes-Benz-Viano-UK.pdf
EU-LANCIA-THEMA-I-8-32-SEDAN-01	4590	1733	1420	Automobile-Catalog 1987 Lancia Thema 8.32	https://www.automobile-catalog.com/car/1987/54410/lancia_thema_8_32.html
EU-RENAULT-19-I-HATCHBACK-3D-02	4156	1684	1412	Automobile-Catalog 1990 Renault 19 1.4	https://www.automobile-catalog.com/car/1990/2942000/renault_19_1_4_80_automatic.html
EU-RENAULT-19-I-HATCHBACK-5D-02	4156	1684	1412	Automobile-Catalog 1990 Renault 19 1.4	https://www.automobile-catalog.com/car/1990/2942000/renault_19_1_4_80_automatic.html
EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	4590	1755	1440	Automobile-Catalog 1991 Lancia Thema Station Wagon Turbo DS	https://www.automobile-catalog.com/car/1991/54425/lancia_thema_station_wagon_turbo_ds.html
EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	4605	1752	1435	Automobile-Catalog 1993 Lancia Thema Station Wagon 16V LE	https://www.automobile-catalog.com/car/1993/1380365/lancia_thema_station_wagon_16v_le.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	3392	1537	1460	Automobile-Catalog 1987 Lancia Y10 4WD	https://www.automobile-catalog.com/car/1987/1380740/lancia_y10_4wd.html
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385	Automobile-Catalog 1988 Lancia Prisma Integrale	https://www.automobile-catalog.com/car/1988/1379255/lancia_prisma_integrale.html
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	3895	1620	1380	Automobile-Catalog 1986 Lancia Delta LX	https://www.automobile-catalog.com/car/1986/1378880/lancia_delta_lx.html
EU-LANCIA-DELTA-I-HATCHBACK-INTEGRALE-8V-01	3900	1700	1380	Automobile-Catalog 1988 Lancia Delta HF Integrale	https://www.automobile-catalog.com/car/1988/1379195/lancia_delta_hf_integrale.html
EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	4590	1758	1435	Automobile-Catalog 1989 Lancia Thema Turbo DS automatic	https://www.automobile-catalog.com/car/1989/1380080/lancia_thema_turbo_ds_automatica.html
EU-LANCIA-GAMMA-830-HATCHBACK-5D-01	4580	1730	1410	Automobile-Catalog 1978 Lancia Gamma 2500	https://www.automobile-catalog.com/car/1978/1378340/lancia_gamma_2500.html
EU-LANCIA-GAMMA-830-COUPE-2D-01	4485	1730	1330	Automobile-Catalog 1978 Lancia Gamma Coupe 2500	https://www.automobile-catalog.com/car/1978/1378370/lancia_gamma_coupe_2500.html
EU-LANCIA-FULVIA-818-COUPE-2D-01	3975	1555	1300	Automobile-Catalog 1969 Lancia Fulvia Coupe Rallye 1.3 S	https://www.automobile-catalog.com/car/1969/1376030/lancia_fulvia_coupe_rallye_1_3_s.html
EU-PORSCHE-356-PRE-A-CABRIOLET-2D-01	3950	1660	1300	Automobile-Catalog 1955 Porsche 356 1500 Cabriolet	https://www.automobile-catalog.com/car/1955/2580350/porsche_356_1500_cabriolet.html
EU-PORSCHE-356-PRE-A-SPEEDSTER-2D-01	3950	1660	1220	Automobile-Catalog 1955 Porsche 356 1500 Speedster	https://www.automobile-catalog.com/car/1955/2580305/porsche_356_1500_speedster.html
EU-PORSCHE-356-A-CABRIOLET-2D-01	3950	1670	1310	Automobile-Catalog 1958 Porsche 356 A 1600 Cabriolet	https://www.automobile-catalog.com/car/1958/2580905/porsche_356_a1600_cabriolet.html
EU-PORSCHE-356-A-SPEEDSTER-2D-01	3950	1670	1220	Automobile-Catalog 1957 Porsche 356 A 1600 Speedster	https://www.automobile-catalog.com/car/1957/2580755/porsche_356_a1600_speedster.html
EU-PORSCHE-356-A-CONVERTIBLE-D-2D-01	3950	1670	1290	Automobile-Catalog 1959 Porsche 356 A 1600 Convertible D	https://www.automobile-catalog.com/car/1959/2580875/porsche_356_a1600_convertible_d.html
EU-PORSCHE-356-B-CABRIOLET-2D-01	4010	1670	1330	Automobile-Catalog 1961 Porsche 356 B 1600 Cabriolet	https://www.automobile-catalog.com/car/1961/2581160/porsche_356_b1600_cabriolet.html
EU-PORSCHE-356-B-ROADSTER-2D-01	4010	1670	1310	Automobile-Catalog 1960 Porsche 356 B 1600 Roadster	https://www.automobile-catalog.com/car/1960/2581280/porsche_356_b1600_roadster.html
EU-PORSCHE-356-C-CABRIOLET-2D-01	4010	1670	1315	Automobile-Catalog 1964 Porsche 356 C 1600 SC Cabriolet	https://www.automobile-catalog.com/car/1964/2581895/porsche_356_c1600_sc_cabriolet.html
EU-RENAULT-25-B29-HATCHBACK-01	4715	1805	1415	Auto-Data Renault 25 B29	https://www.auto-data.net/en/renault-25-b29-generation-2140
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431	Automobile-Catalog 1975 Renault 30 TS	https://www.automobile-catalog.com/car/1975/31505/renault_30_ts.html
EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	4500	1732	1431	Automobile-Catalog 1981 Renault 30 TX	https://www.automobile-catalog.com/car/1981/36530/renault_30_tx.html
EU-RENAULT-18-134-SEDAN-1982-01	4394	1689	1405	Automobile-Catalog 1982 Renault 18 TS	https://www.automobile-catalog.com/car/1982/2931020/renault_18_ts.html
EU-RENAULT-18-135-WAGON-1982-01	4487	1689	1402	Automobile-Catalog 1982 Renault 18 Break GTS	https://www.automobile-catalog.com/car/1982/2931590/renault_18_break_gts.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7101-7200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1988/2940110/renault_21_nevada_savanna_gtd_4x4.html "https://www.automobile-catalog.com/car/1988/2940110/renault_21_nevada_savanna_gtd_4x4.html"
[2]: https://www.porsche.com/australia/accessoriesandservice/classic/models/356/356-a/ "https://www.porsche.com/australia/accessoriesandservice/classic/models/356/356-a/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7101-7200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7101-7200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9113 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2817 行）

