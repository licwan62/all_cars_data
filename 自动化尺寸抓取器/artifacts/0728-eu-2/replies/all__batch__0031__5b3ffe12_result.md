# 任务：all 第 3001-3100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0031__5b3ffe12


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3001-3100 行

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
all 第 3001-3100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495
EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	4273	1769	1456
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	3718	1595	1390
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	3718	1620	1360
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368
EU-FORD-FIESTA-II-MK2-HATCHBACK-3D-01	3565	1567	1360
EU-FORD-FIESTA-V-VAN-3D-FACELIFT-01	3918	1683	1468
EU-FORD-FIESTA-V-VAN-3D-PREFL-01	3917	1683	1467
EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	5228	2000	1971
EU-FORD-USA-EXPEDITION-I-SUV-01	5197	1996	1890
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480
EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	4325	1830	1730
EU-HYUNDAI-TUCSON-JM-SUV-01	4325	1830	1730
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660
EU-LANCIA-MUSA-I-MPV-PREFL-01	3985	1698	1688
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	4691	1777	1432
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935
EU-PEUGEOT-306-I-CONVERTIBLE-FACELIFT-01	4179	1680	1356
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-LWB-01	5506	2020	2150
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-MWB-01	5006	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-LWB-01	5490	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-MWB-01	4990	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-CAB-LWB-01	5680	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-DOUBLE-CAB-LWB-01	5710	2020	2150
EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	5599	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870
EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690
EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	4749	2024	2515
EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-II-BUS-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-BUS-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-BUS-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-3D-02	3986	1719	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-02	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477
EU-RENAULT-CLIO-II-PHASE-III-VAN-01	3811	1639	1417
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-RENAULT-RAPID-I-BODY-01	4056	1566	1776
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568
EU-TOYOTA-COROLLA-E120-SEDAN-01	4375	1710	1470
EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	4195	1655	1360
EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	4200	1710	1440
EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	4370	1770	1625
EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	4360	1770	1620
EU-VOLVO-S70-SEDAN-01	4720	1760	1400
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-V70-II-FACELIFT-WAGON-01	4710	1804	1465
EU-VOLVO-V70-II-FACELIFT-WAGON-AWD-01	4710	1804	1514
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VOLVO-V70-II-WAGON-FACELIFT-01	4710	1804	1465
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	93	126	Nov 2005	Nov 2006	2024-03-01	28568
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	88	120	Nov 2005	May 2007	2024-03-01	28569
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	120	163	Aug 2005	May 2009	2024-03-01	28570
Volvo	S80 ii	2.0 TDI	Stufenheck	Frontantrieb	Diesel	100	136	Feb 2008	Mar 2011	2024-03-01	28571
VW	Transporter t4	2.8 VR6	Pritsche/Fahrgestell	Frontantrieb	Benzin	150	204	Jun 2000	Apr 2003	2024-03-01	28574
Audi	A6 c6	RS6 Quattro	Stufenheck	Allrad	Benzin	426	580	Sep 2008	Aug 2010	2024-03-01	28576
Hyundai	Tucson	2.0 Crdi	SUV	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2010	2024-03-01	28577
Hyundai	Tucson	2.0 Crdi Allrad	SUV	Allrad	Diesel	88	120	Jan 2007	Mar 2010	2024-03-01	28578
Hyundai	I30	1.4	Schrägheck	Frontantrieb	Benzin	77	105	Oct 2007	Nov 2011	2024-03-01	28579
Hyundai	I30	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Oct 2007	Nov 2011	2024-03-01	28580
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	66	90	Oct 2007	Nov 2011	2024-03-01	28581
Hyundai	I30	1.6	Kombi	Frontantrieb	Benzin	85	116	Feb 2008	Jun 2012	2024-03-01	28582
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	66	90	Feb 2008	Jun 2012	2024-03-01	28583
Hyundai	I30	2.0 Crdi	Kombi	Frontantrieb	Diesel	103	140	Feb 2008	Jun 2012	2024-03-01	28584
Hyundai	I30	1.6	Kombi	Frontantrieb	Benzin	93	126	Feb 2008	Jun 2012	2024-03-01	28585
Ford	Fiesta	1.6 TI	Stufenheck	Frontantrieb	Benzin	88	120	Apr 2010	Apr 2017	2024-07-01	28588
Citroën	C4 i	1.6 VTI 120	Schrägheck	Frontantrieb	Benzin	88	120	Jul 2008	Jul 2011	2024-03-01	28589
Citroën	C4 i	1.6 THP 150	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2008	Jul 2011	2024-03-01	28590
Citroën	C4 i	1.6 THP 140	Schrägheck	Frontantrieb	Benzin	103	140	Jul 2008	Jul 2011	2024-03-01	28591
Citroën	C4	1.6 VTI 120	Coupe	Frontantrieb	Benzin	88	120	Jul 2008	Jul 2011	2024-03-01	28592
Citroën	C4	1.6 THP 150	Coupe	Frontantrieb	Benzin	110	150	Jul 2008	Jul 2011	2024-03-01	28593
Citroën	C4 grand picasso i	1.6 VTI 120	Großraumlimousine	Frontantrieb	Benzin	88	120	Jul 2008	Aug 2013	2024-03-01	28594
Citroën	C4 grand picasso i	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	103	140	Jul 2008	Dec 2010	2024-03-01	28595
Citroën	C4 picasso i	1.6 VTI 120	Großraumlimousine	Frontantrieb	Benzin	88	120	Jul 2008	Aug 2013	2024-03-01	28596
Citroën	C4 picasso i	1.6 THP 140	Großraumlimousine	Frontantrieb	Benzin	103	140	Jul 2008	Aug 2013	2024-03-01	28597
Lancia	Musa	1.6 D Multijet	Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2008	Sep 2012	2024-03-01	28599
Maserati	Gran turismo i	4.2	Coupe	Heckantrieb	Benzin	298	405	Sep 2007	-	2024-03-01	28600
Maserati	Gran turismo i	4.7 S	Coupe	Heckantrieb	Benzin	323	439	Aug 2008	Dec 2012	2024-03-01	28601
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	Jul 2005	May 2010	2024-03-01	28602
Seat	Toledo	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	100	136	Sep 2004	May 2009	2024-03-01	28603
Infiniti	Fx	37 AWD	SUV	Allrad	Benzin	235	320	Oct 2008	-	2024-03-01	28604
Infiniti	Fx	50 AWD	SUV	Allrad	Benzin	287	390	Oct 2008	-	2024-03-01	28605
Infiniti	Ex	37	SUV	Allrad	Benzin	228	310	Oct 2008	-	2024-03-01	28606
Infiniti	G	37	Coupe	Heckantrieb	Benzin	243	330	Sep 2007	-	2024-03-01	28607
Infiniti	G	37	Stufenheck	Heckantrieb	Benzin	243	330	Oct 2008	-	2024-03-01	28608
Chevrolet	Aveo / kalos	1.4	Stufenheck	Frontantrieb	Benzin	74	101	Sep 2008	-	2024-03-01	28619
Hyundai	ii	2	Coupe	Frontantrieb	Benzin	100	136	Aug 2001	Aug 2009	2024-03-01	28620
Mercedes-benz	Viano	3.5	Bus	Heckantrieb	Benzin	190	258	Sep 2007	-	2024-03-01	28621
Renault	Rapid	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	34	46	Sep 1985	Aug 1991	2024-03-01	28622
Renault	Rapid	1	Kasten/Großraumlimousine	Frontantrieb	Benzin	31	42	Sep 1985	Aug 1991	2024-03-01	28623
Citroën	Zx	2	Schrägheck	Frontantrieb	Benzin	122	166	Sep 1996	Oct 1997	2024-03-01	28626
Citroën	Zx	2	Schrägheck	Frontantrieb	Benzin	90	122	Jul 1994	Oct 1997	2024-03-01	28628
Citroën	Zx	1.8	Schrägheck	Frontantrieb	Benzin	76	103	Mar 1991	Oct 1997	2024-03-01	28629
Citroën	Zx	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1994	Oct 1997	2024-03-01	28630
Citroën	Zx	1.9 DT	Schrägheck	Frontantrieb	Diesel	65	88	Jul 1994	Oct 1997	2024-03-01	28631
Citroën	Zx	1.9 DT	Schrägheck	Frontantrieb	Diesel	68	92	Jun 1992	Jun 1994	2024-03-01	28632
Renault	Laguna i	2	Schrägheck	Frontantrieb	Benzin	102	139	Sep 1999	Feb 2001	2024-03-01	28635
Renault	Laguna i	2	Schrägheck	Frontantrieb	Benzin	103	140	Jun 1995	Feb 2001	2024-03-01	28636
Renault	Laguna i	1.8	Schrägheck	Frontantrieb	Benzin	70	95	Jun 1995	Jun 1998	2024-03-01	28637
Renault	Laguna i	2	Schrägheck	Frontantrieb	Benzin	84	114	Jun 1995	Feb 2001	2024-03-01	28638
Renault	Laguna i	1.8	Schrägheck	Frontantrieb	Benzin	69	94	Jun 1995	Feb 2001	2024-03-01	28639
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	118	160	Sep 1990	Sep 1993	2024-03-01	28640
Peugeot	205 i	1.9 CTI	Cabriolet	Frontantrieb	Benzin	74	101	Aug 1987	Jul 1990	2024-03-01	28641
Peugeot	205 ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jul 1988	Sep 1998	2024-03-01	28642
Peugeot	205 ii	1.8 XDT	Schrägheck	Frontantrieb	Diesel	58	79	Aug 1990	May 1997	2024-03-01	28643
Peugeot	205 ii	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1990	Jul 1992	2024-03-01	28644
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	82	111	Jan 1990	Dec 1993	2024-03-01	28645
Volvo	240	2	Kombi	Heckantrieb	Benzin	82	111	Sep 1988	Dec 1993	2024-03-01	28646
Peugeot	306	1.8	Stufenheck	Frontantrieb	Benzin	74	101	Jun 1994	May 2001	2024-03-01	28655
Alfa Romeo	164	3	Stufenheck	Frontantrieb	Benzin	138	188	Nov 1987	Sep 1991	2024-03-01	28662
Alfa Romeo	164	3	Stufenheck	Frontantrieb	Benzin	168	228	Apr 1993	Feb 1995	2024-03-01	28671
Mercedes-benz	Cla	CLA 180 CDI / D	Coupe	Frontantrieb	Diesel	80	109	Oct 2013	May 2018	2024-03-01	28672
Alfa Romeo	164	3.0 24V QV Allrad	Stufenheck	Allrad	Benzin	171	233	Nov 1992	Oct 1997	2024-03-01	28673
Austin	Montego	1.3	Stufenheck	Frontantrieb	Benzin	46	62	Apr 1984	Dec 1985	2024-03-01	28676
Austin	Montego	2.0 D	Kombi	Frontantrieb	Diesel	61	82	Dec 1988	Sep 1992	2024-03-01	28677
Peugeot	405 i break	1.6	Kombi	Frontantrieb	Benzin	68	92	May 1988	Jul 1992	2024-03-01	28678
Peugeot	405 i break	1.9	Kombi	Frontantrieb	Benzin	72	98	May 1988	Jul 1992	2024-03-01	28679
Peugeot	405 i break	1.9 Allrad	Kombi	Allrad	Benzin	77	105	Sep 1988	Jul 1992	2024-03-01	28680
Peugeot	405 ii break	1.4	Kombi	Frontantrieb	Benzin	58	79	Jul 1993	Jun 1994	2024-03-01	28682
Peugeot	405 ii break	1.9 D	Kombi	Frontantrieb	Diesel	51	69	Sep 1993	Dec 1995	2024-03-01	28683
Peugeot	Boxer	2.8 HDI	Bus	Frontantrieb	Diesel	93	126	Oct 2000	Nov 2001	2024-03-01	28684
Ford	Fiesta iii	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1989	Dec 1992	2024-03-01	28685
Ford	Fiesta iii	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1989	Dec 1995	2024-03-01	28686
Peugeot	504	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1979	Aug 1982	2024-03-01	28688
Peugeot	504	2.1 D	Stufenheck	Heckantrieb	Diesel	49	67	Sep 1979	Aug 1982	2024-03-01	28689
Peugeot	504	2	Stufenheck	Heckantrieb	Benzin	69	94	Sep 1979	Aug 1982	2024-03-01	28690
Peugeot	504	2.1 D	Stufenheck	Heckantrieb	Diesel	43	58	Sep 1979	Aug 1982	2024-03-01	28691
Peugeot	505	2	Stufenheck	Heckantrieb	Benzin	69	94	Sep 1983	Sep 1985	2024-03-01	28692
Opel	Vectra a	1.6	Stufenheck	Frontantrieb	Benzin	51	69	Aug 1992	Jul 1993	2024-03-01	28697
Renault	19 ii chamade	1.8	Stufenheck	Frontantrieb	Benzin	79	107	May 1992	Nov 1995	2024-03-01	28701
Renault	19 ii chamade	1.8	Stufenheck	Frontantrieb	Benzin	67	91	May 1992	Sep 1994	2024-03-01	28702
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	55	75	May 1992	Nov 1995	2024-03-01	28703
Renault	19 ii chamade	1.9 D	Stufenheck	Frontantrieb	Diesel	68	92	May 1992	Nov 1995	2024-03-01	28704
Renault	19 ii chamade	1.4	Stufenheck	Frontantrieb	Benzin	57	78	Oct 1994	Nov 1995	2024-03-01	28705
Renault	19 ii chamade	1.4	Stufenheck	Frontantrieb	Benzin	44	60	May 1992	Sep 1994	2024-03-01	28706
Renault	21	2	Stufenheck	Frontantrieb	Benzin	86	117	Apr 1986	Jun 1989	2024-03-01	28707
Renault	21	2.1 TD	Stufenheck	Frontantrieb	Diesel	50	68	Apr 1986	Jun 1989	2024-03-01	28709
Ford USA	Expedition	5.4 XLT 4X4	SUV	Allrad	Benzin	224	305	Jan 2007	-	2024-03-01	28724
Citroën	Saxo	1.5 D	Schrägheck	Frontantrieb	Diesel	43	58	Jul 2001	Apr 2004	2024-03-01	28731
Chevrolet	Nova	5.7	Stufenheck	Heckantrieb	Benzin	119	162	Jan 1973	Dec 1979	2024-03-01	28733
Chevrolet	Nova	5.7	Coupe	Heckantrieb	Benzin	119	162	Sep 1973	Dec 1979	2024-03-01	28734
Volvo	V70 i	2.4 AWD	Kombi	Allrad	Benzin	121	165	Jun 1998	Dec 1999	2024-03-01	28741
Audi	A6 c5	3.0 Quattro	Stufenheck	Allrad	Benzin	160	218	Jun 2001	Jul 2004	2024-03-01	28743
Audi	A6 c5	2.8 Quattro	Stufenheck	Allrad	Benzin	140	190	Jul 1999	May 2001	2024-03-01	28744
Peugeot	Boxer	2.8 HDI	Kasten	Frontantrieb	Diesel	93	126	Oct 2000	Nov 2001	2024-03-01	28745
Asia Motors	Rocsta	2.2 D	Geländewagen offen	Heckantrieb	Diesel	45	61	Jul 1993	Dec 1998	2024-03-01	28746
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	85	115	May 1992	Apr 1997	2024-03-01	28759
Volvo	S70	2.4 Blu-fuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	103	140	Jul 1997	Sep 2000	2024-03-01	28764
Renault	Clio ii	1.9 D	Schrägheck	Frontantrieb	Diesel	48	65	Feb 2000	May 2001	2026-05-01	28765
Renault	Clio ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	59	80	Jun 2001	Oct 2003	2026-05-01	28767


--- Round 1 / 首次发送 ---
## 更新点

* 复用 22 个跨批次既有尺寸组，未重复输出既有尺寸及来源。
* 首次闭合 10 个尺寸组：Audi A4 B7 Avant、Audi RS6 C6 Sedan、Citroën C4 I Phase II 五门/三门、Infiniti FX/EX/G37、Chevrolet Aveo T250 Sedan、Hyundai Coupe II GK。A4、RS6、C4 与 Infiniti 各组的车身边界和三维已由对应直接规格页闭合。([汽车目录][1])
* Aveo 28619 未错误复用已有 T200 组；其 101 hp、2008 年后轿车记录对应更长的 T250 四门外廓。Hyundai 输入 Model=`ii` 的 28620 已按年份、功率及 Coupe 车身闭合至 Coupe II GK。([汽车目录][2])
* 已拆分 Leon II、CLA C117 的改款前后分支，以及 Viano W639 长度、C4 Picasso I 悬架高度和 Saxo 三门/五门分支。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：44
* READY 映射行：51
* PENDING Ktype：56
* 当前引用尺寸组：32
* 本轮首次创建尺寸组：10
* 复用既有尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28568	28568	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-8ED-WAGON-01	HIGH		READY
28569	28569	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH		READY
28570	28570	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH		READY
28571	28571	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
28576	28576	Sedan	RS6 C6	4F2	4	EU-AUDI-RS6-C6-4F2-SEDAN-01	HIGH	RS6宽体轿车外廓。	READY
28577	28577	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH		READY
28578	28578	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH		READY
28579	28579	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28580	28580	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28581	28581	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28582	28582	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28583	28583	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28584	28584	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28585	28585	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28589	28589	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28590	28590	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28591	28591	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28592	28592	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
28593	28593	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
28596_coil	28596	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一Ktype覆盖钢簧高度分支。	READY
28596_airsusp	28596	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一Ktype覆盖后空气悬架高度分支。	READY
28597_coil	28597	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一Ktype覆盖钢簧高度分支。	READY
28597_airsusp	28597	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一Ktype覆盖后空气悬架高度分支。	READY
28599	28599	MPV	Musa I facelift	350	5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	HIGH		READY
28602_prefl	28602	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	生产区间跨改款，拆分改款前外廓。	READY
28602_facelift	28602	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	生产区间跨改款，拆分改款后外廓。	READY
28603	28603	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
28604	28604	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
28605	28605	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
28606	28606	SUV	EX	J50	5	EU-INFINITI-EX-J50-SUV-5D-01	HIGH		READY
28607	28607	Coupe	G37	CV36	2	EU-INFINITI-G37-V36-COUPE-2D-01	HIGH		READY
28608	28608	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
28619	28619	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	HIGH	2008年后101 hp四门轿车外廓。	READY
28620	28620	Coupe	Coupe II	GK	3	EU-HYUNDAI-COUPE-II-GK-COUPE-3D-01	HIGH	输入Model为“ii”，按车身、年份与2.0版本闭合至Hyundai Coupe II GK。	READY
28621_compact	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
28621_long	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
28621_extralong	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	MEDIUM	同一Ktype覆盖Extra-long车长分支。	READY
28622	28622	Van	Rapid I			EU-RENAULT-RAPID-I-BODY-01	MEDIUM	Kasten/Großraumlimousine统一按厢式车外廓映射。	READY
28623	28623	Van	Rapid I			EU-RENAULT-RAPID-I-BODY-01	MEDIUM	Kasten/Großraumlimousine统一按厢式车外廓映射。	READY
28672_prefl	28672	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	HIGH	生产区间跨改款，拆分改款前外廓。	READY
28672_facelift	28672	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	HIGH	生产区间跨改款，拆分改款后外廓。	READY
28701	28701	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28702	28702	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28703	28703	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28704	28704	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28705	28705	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28706	28706	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28724	28724	SUV	Expedition II	U222	5	EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	HIGH		READY
28731_3dr	28731	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门外廓。	READY
28731_5dr	28731	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门外廓。	READY
28764	28764	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B7-8ED-WAGON-01	4586	1772	1453	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/247565/audi_a4_avant_2_0.html
EU-AUDI-RS6-C6-4F2-SEDAN-01	4928	1889	1456	Auto-Data	https://www.auto-data.net/en/audi-rs6-4f-c6-generation-1122
EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	4275	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1214735/citroen_c4_vti_120_vtr.html
EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	4288	1769	1456	Auto-Data	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-ii-2008-generation-5305
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680	Auto-Data	https://www.auto-data.net/en/infiniti-fx-ii-generation-3046
EU-INFINITI-EX-J50-SUV-5D-01	4630	1800	1575	Auto-Data	https://www.auto-data.net/en/infiniti-ex-37-generation-3038
EU-INFINITI-G37-V36-COUPE-2D-01	4655	1824	1395	Auto-Data	https://www.auto-data.net/en/infiniti-g37-coupe-v36-generation-3049
EU-INFINITI-G37-V36-SEDAN-4D-01	4755	1773	1469	Auto-Data	https://www.auto-data.net/en/infiniti-g37-sedan-v36-generation-9612
EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	4310	1710	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/559175/chevrolet_aveo_1_4_lt_sedan.html
EU-HYUNDAI-COUPE-II-GK-COUPE-3D-01	4395	1760	1330	Auto-Data	https://www.auto-data.net/en/hyundai-coupe-ii-gk-generation-2991
```

## 下一步优先处理

1. 集中闭合 VW Transporter T4 Pritsche/Fahrgestell、Peugeot Boxer I 230 Bus/Kasten 的轴距、车顶和车身长度分支。
2. 处理 Citroën Grand C4 Picasso I 的钢簧/空气悬架高度边界，以及 Maserati GranTurismo 早期 4.2/4.7 的无后视镜宽度冲突。
3. 批量闭合 Citroën ZX、Renault Laguna I、Peugeot 205/405、Volvo 240/940、Alfa Romeo 164 等乘用车聚类。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/247565/audi_a4_avant_2_0.html?utm_source=chatgpt.com "2008 Audi A4 Avant 2.0 Specs Review (96 kW / 131 PS / 129 hp) (up to mid-year 2008 for Europe )"
[2]: https://www.automobile-catalog.com/car/2008/559175/chevrolet_aveo_1_4_lt_sedan.html?utm_source=chatgpt.com "2008 Chevrolet Aveo 1.4 LT Sedan Specs Review (74 kW ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 21 个 READY Ktype、23 行映射，PENDING 从 56 降至 35。
* Maserati GranTurismo 4.2 与 GranTurismo S 4.7 的无后视镜宽度不同，分别建立尺寸组，不按发动机版本盲目合并。([汽车档案库][1])
* Citroën ZX Phase II 三门与五门三维一致，复用同一组；Phase I 三门与五门外廓不同，分别建组。([汽车数据网][2])
* 批量闭合 Laguna I Hatchback、Volvo 940 Sedan、Peugeot 205 facelift Hatchback、Fiesta III Hatchback、Peugeot 505 Sedan 和 Vectra A facelift Sedan。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* PENDING Ktype：35
* READY 映射行：74
* 已确认并被本批引用的尺寸组：43
* 本轮新增尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28600	28600	Coupe	GranTurismo I	M145	2	EU-MASERATI-GRANTURISMO-I-M145-COUPE-4.2-01	HIGH		READY
28601	28601	Coupe	GranTurismo I	M145	2	EU-MASERATI-GRANTURISMO-I-M145-COUPE-S-4.7-01	HIGH	GranTurismo S宽体外廓。	READY
28626	28626	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28628	28628	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28629_prefl	28629	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产区间跨Phase I/II，拆分改款前外廓。	READY
28629_facelift	28629	Hatchback	ZX Phase II	N2	3	EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	MEDIUM	生产区间跨Phase I/II，拆分改款后外廓。	READY
28630	28630	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28631	28631	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28632_3dr	28632	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	HIGH	同一Ktype覆盖Phase I三门外廓。	READY
28632_5dr	28632	Hatchback	ZX Phase I	N2	5	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-5D-01	HIGH	同一Ktype覆盖Phase I五门外廓。	READY
28635	28635	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28636	28636	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28637	28637	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28638	28638	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28639	28639	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28640	28640	Sedan	940	944	4	EU-VOLVO-940-944-SEDAN-4D-01	HIGH		READY
28642	28642	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28643	28643	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28644	28644	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28685	28685	Hatchback	Fiesta III (Mk3)			EU-FORD-FIESTA-III-MK3-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28686	28686	Hatchback	Fiesta III (Mk3)			EU-FORD-FIESTA-III-MK3-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28692	28692	Sedan	505	551A	4	EU-PEUGEOT-505-551A-SEDAN-4D-01	HIGH		READY
28697	28697	Sedan	Vectra A facelift		4	EU-OPEL-VECTRA-A-FACELIFT-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MASERATI-GRANTURISMO-I-M145-COUPE-4.2-01	4881	1847	1353	Maserati GranTurismo 2008 brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2018/02/Maserati-GranTurismo-2008-USA.pdf; https://www.automobile-catalog.com/car/2008/1447985/maserati_granturismo.html
EU-MASERATI-GRANTURISMO-I-M145-COUPE-S-4.7-01	4881	1915	1353	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1448000/maserati_granturismo_s.html
EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	4085	1705	1404	Auto-Data; Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-ii-3-door-generation-9053; https://www.auto-data.net/en/citroen-zx-n2-phase-ii-5-door-generation-9034
EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	4085	1718	1405	Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-i-3-door-generation-9038
EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-5D-01	4085	1707	1404	Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-i-5-door-generation-3340
EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	4510	1750	1430	Auto-Data	https://www.auto-data.net/en/renault-laguna-1.8-16v-120hp-10335
EU-VOLVO-940-944-SEDAN-4D-01	4871	1750	1425	Auto-Data	https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286
EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	3705	1560	1375	Auto-Data	https://www.auto-data.net/en/peugeot-205-i-20a-c-facelift-1987-1.4-i-75hp-5648
EU-FORD-FIESTA-III-MK3-HATCHBACK-01	3743	1606	1379	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-110hp-8058
EU-PEUGEOT-505-551A-SEDAN-4D-01	4580	1735	1440	Auto-Data	https://www.auto-data.net/en/peugeot-505-551a-2.0-98hp-5500
EU-OPEL-VECTRA-A-FACELIFT-SEDAN-4D-01	4432	1706	1400	Auto-Data	https://www.auto-data.net/en/opel-vectra-a-facelift-1992-1.6i-71hp-2299
```

## 下一步优先处理

1. 批量闭合 Volvo 240 Sedan/Wagon、Peugeot 405 Break Phase I/II、Peugeot 504 Sedan 和 Renault 21 Sedan。
2. 处理 Audi A6 C5 Sedan、Volvo V70 I AWD、Toyota Corolla E100 Sedan、Chevrolet Nova Sedan/Coupe。
3. 最后处理存在多轴距、车顶或开放式车身边界的 Transporter T4、Boxer I、Viano、Rocsta，以及剩余门数分支。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2018/02/Maserati-GranTurismo-2008-USA.pdf?utm_source=chatgpt.com "MASERATI GRANTURISMO"
[2]: https://www.auto-data.net/en/citroen-zx-n2-phase-ii-5-door-generation-9034 "Citroen ZX (N2, Phase II) 5-door | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/renault-laguna-1.8-16v-120hp-10335 "Renault Laguna 1.8 16V (120 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增 14 个 READY Ktype、14 行映射；PENDING 从 35 降至 21。
* 集中闭合 Volvo 240 Sedan/Wagon、Peugeot 504 Sedan、Renault 21 Phase I Sedan 和 Volvo V70 I Wagon。([汽车目录][1])
* 闭合 Audi A6 C5 改款前后、Toyota Corolla E100 Sedan，以及三维一致的 Renault Clio II Phase I/II Hatchback。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* PENDING Ktype：21
* READY 映射行：88
* 已确认并被本批引用的尺寸组：52
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28645	28645	Sedan	240	P244	4	EU-VOLVO-240-P244-SEDAN-4D-01	HIGH		READY
28646	28646	Wagon	240	P245	5	EU-VOLVO-240-P245-WAGON-5D-01	HIGH		READY
28688	28688	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28689	28689	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28690	28690	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28691	28691	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28707	28707	Sedan	Renault 21 Phase I		4	EU-RENAULT-21-PHASE-I-SEDAN-4D-01	HIGH		READY
28709	28709	Sedan	Renault 21 Phase I		4	EU-RENAULT-21-PHASE-I-SEDAN-4D-01	HIGH		READY
28741	28741	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
28743	28743	Sedan	A6 C5 facelift	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-FACELIFT-01	HIGH		READY
28744	28744	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-PREFL-01	HIGH		READY
28759	28759	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-E100-SEDAN-4D-01	HIGH		READY
28765	28765	Hatchback	Clio II Phase I			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28767	28767	Hatchback	Clio II Phase II			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH	三门和五门三维一致；改款未改变三维。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-240-P244-SEDAN-4D-01	4785	1707	1427	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/45905/volvo_244_turbo.html
EU-VOLVO-240-P245-WAGON-5D-01	4785	1707	1460	Auto Motor und Sport	https://www.auto-motor-und-sport.de/marken-modelle/volvo/240/technische-daten/
EU-PEUGEOT-504-SEDAN-4D-01	4490	1690	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/2557640/peugeot_504.html
EU-RENAULT-21-PHASE-I-SEDAN-4D-01	4462	1714	1414	Automobile-Catalog; Automobile-Catalog	https://www.automobile-catalog.com/car/1986/52340/renault_21_txe.html; https://www.automobile-catalog.com/car/1986/55805/renault_21_turbo_d.html
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430	Auto-Data	https://www.auto-data.net/en/volvo-v70-i-2.4-20v-turbo-193hp-awd-9270
EU-AUDI-A6-C5-4B2-SEDAN-FACELIFT-01	4796	1810	1453	Auto-Data	https://www.auto-data.net/en/audi-a6-4b-c5-facelift-2001-3.0-v6-220hp-quattro-tiptronic-26953
EU-AUDI-A6-C5-4B2-SEDAN-PREFL-01	4796	1810	1451	Auto-Data	https://www.auto-data.net/en/audi-a6-4b-c5-2.8-v6-30v-193hp-quattro-4714
EU-TOYOTA-COROLLA-E100-SEDAN-4D-01	4270	1685	1380	Auto-Data	https://www.auto-data.net/en/toyota-corolla-vii-e100-1.6-si-114hp-3351
EU-RENAULT-CLIO-II-HATCHBACK-01	3773	1639	1417	Autogidas; Carfolio	https://autogidas.lt/en/auto-katalogas/renault/clio/ii-1.6i-16v-1998-2001-k30192; https://www.carfolio.com/renault-clio-ii-sport-phase-2-100144
```

## 下一步优先处理

1. 闭合 Alfa Romeo 164 改款前、改款后及 Q4 外廓。
2. 集中处理 Austin Montego Sedan/Wagon、Peugeot 306 Sedan 和 Peugeot 205 CTI。
3. 最后处理多轴距或多车顶的 Transporter T4、Boxer I，以及 Chevrolet Nova、Rocsta 等剩余特殊外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/45905/volvo_244_turbo.html?utm_source=chatgpt.com "1990 Volvo 244 Turbo Specs Review (114 kW / 155 PS / 153 hp) (up to mid-year 1990 for Europe )"
[2]: https://www.auto-data.net/en/audi-a6-4b-c5-2.8-v6-30v-193hp-quattro-4714?utm_source=chatgpt.com "Audi A6 (4B,C5) 2.8 V6 30V (193 Hp) quattro /Sedan 1997"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增 12 个 READY Ktype、12 行映射；PENDING 从 21 降至 9。
* 闭合 Peugeot 205 Cabriolet、Peugeot 405 Break 改款前后及 Asia Motors Rocsta 开放式车身。405 Break 的前驱与四驱版本外廓一致，复用同一改款前尺寸组。([汽车数据网][1])
* Austin Montego Sedan 与 Estate 属于不同车身及改款阶段，分别建立尺寸组。([汽车目录][2])
* Alfa Romeo 164 按早期 3.0、后期 24V 和 Q4 全轮驱动车身边界拆为三个尺寸组，未因车型名称相同强行合并。([autoweek.nl][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* PENDING Ktype：9
* READY 映射行：100
* 已确认并被本批引用的尺寸组：61
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28641	28641	Convertible	205 I	741B	2	EU-PEUGEOT-205-I-CABRIOLET-01	HIGH		READY
28662	28662	Sedan	164	164A	4	EU-ALFA-ROMEO-164-PREFL-SEDAN-01	HIGH		READY
28671	28671	Sedan	164		4	EU-ALFA-ROMEO-164-24V-SEDAN-01	MEDIUM		READY
28673	28673	Sedan	164		4	EU-ALFA-ROMEO-164-Q4-SEDAN-01	MEDIUM	Q4全轮驱动车身。	READY
28676	28676	Sedan	Montego Phase I		4	EU-AUSTIN-MONTEGO-PHASE-I-SEDAN-4D-01	HIGH		READY
28677	28677	Wagon	Montego Phase II		5	EU-AUSTIN-MONTEGO-PHASE-II-WAGON-5D-01	HIGH		READY
28678	28678	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28679	28679	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28680	28680	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28682	28682	Wagon	405 I facelift	15E	5	EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	MEDIUM		READY
28683	28683	Wagon	405 I facelift	15E	5	EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	HIGH		READY
28746	28746	SUV	Rocsta			EU-ASIA-MOTORS-ROCSTA-SUV-OPEN-01	MEDIUM	开放式越野车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-205-I-CABRIOLET-01	3705	1590	1375	Auto-Data	https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276
EU-ALFA-ROMEO-164-PREFL-SEDAN-01	4555	1760	1400	AutoWeek; Brembo Parts	https://www.autoweek.nl/auto/4262/alfa-romeo-164-3-0-v6/; https://www.bremboparts.com/europe/en/catalogue/alfa-romeo-164-164-3-0-164a/000028662-1
EU-ALFA-ROMEO-164-24V-SEDAN-01	4550	1760	1390	Auto-Data	https://www.auto-data.net/en/alfa-romeo-164-164-3.0-i-v6-24v-230hp-1256
EU-ALFA-ROMEO-164-Q4-SEDAN-01	4670	1760	1360	Auto-Data	https://www.auto-data.net/en/alfa-romeo-164-164-3.0-24v-228hp-q4-1254
EU-AUSTIN-MONTEGO-PHASE-I-SEDAN-4D-01	4468	1710	1418	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/62645/austin_montego_1_3.html
EU-AUSTIN-MONTEGO-PHASE-II-WAGON-5D-01	4465	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1701050/montego_estate_2_0_l_automatic.html
EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	4398	1714	1450	Auto-Data	https://www.auto-data.net/en/peugeot-405-i-break-15e-generation-1272
EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	4398	1714	1481	Auto-Data	https://www.auto-data.net/en/peugeot-405-i-break-15e-facelift-1992-generation-1270
EU-ASIA-MOTORS-ROCSTA-SUV-OPEN-01	3720	1690	1820	Auto-Data	https://www.auto-data.net/en/asia-rocsta-generation-671
```

## 下一步优先处理

1. 闭合 VW Transporter T4 Pritsche/Fahrgestell，以及 Peugeot Boxer I 230 Bus/Kasten 的轴距和车顶派生分支。
2. 核对 Grand C4 Picasso I 的标准车顶与悬架高度、Ford Fiesta Sedan 和 Peugeot 306 Sedan 的改款边界。
3. 拆分 Chevrolet Nova 1973–1974 与 1975–1979 两代 Sedan/Coupe 外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276?utm_source=chatgpt.com "Peugeot 205 I Cabrio (741B,20D) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1984/62645/austin_montego_1_3.html?utm_source=chatgpt.com "1984 Austin Montego 1.3 Specs Review (50.5 kW / 69 PS / 68 hp) (since April 1984 for Europe )"
[3]: https://www.autoweek.nl/auto/4262/alfa-romeo-164-3-0-v6/ "Alfa Romeo 164 3.0 V6 catalogusprijs en specificaties - AutoWeek"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Ford Fiesta VII Sedan；前后期规格均支持同一套 `4409 × 1722 × 1473 mm` 外廓，不拆分改款组。([汽车数据网][1])
* Citroën Grand C4 Picasso I 按后空气悬架与金属弹簧拆分；官方尺寸图确认长度 `4590 mm`、不含后视镜宽度 `1830 mm`，对应高度为 `1690/1710 mm`。([Dezo's Garage][2])
* Peugeot 306 Sedan 的生产区间跨越 Phase I/Phase II，按长度 `4232/4267 mm` 拆分两个尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* PENDING Ktype：5
* READY 映射行：107
* 已确认并被本批引用的尺寸组：66
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28588	28588	Sedan	Fiesta VII Sedan (Mk7)		4	EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	HIGH		READY
28594_airsusp	28594	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	MEDIUM	后空气悬架外廓。	READY
28594_coil	28594	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	MEDIUM	金属弹簧外廓。	READY
28595_airsusp	28595	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	MEDIUM	后空气悬架外廓。	READY
28595_coil	28595	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	MEDIUM	金属弹簧外廓。	READY
28655_prefl	28655	Sedan	306 Phase I	7B	4	EU-PEUGEOT-306-PHASE-I-SEDAN-4D-01	MEDIUM	生产区间跨改款，改款前外廓。	READY
28655_facelift	28655	Sedan	306 Phase II	7B	4	EU-PEUGEOT-306-PHASE-II-SEDAN-4D-01	MEDIUM	生产区间跨改款，改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473	Auto-Data; Car and Driver	https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-1.6-ti-vct-120hp-56327; https://www.caranddriver.com/ford/fiesta/specs/2017/ford_fiesta_ford-fiesta-sedan_2017
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	4590	1830	1690	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	4590	1830	1710	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-PEUGEOT-306-PHASE-I-SEDAN-4D-01	4232	1689	1386	Auto-Data	https://www.auto-data.net/en/peugeot-306-sedan-7b-1.8-st-101hp-5685
EU-PEUGEOT-306-PHASE-II-SEDAN-4D-01	4267	1689	1386	Auto-Data	https://www.auto-data.net/en/peugeot-306-sedan-facelift-1997-generation-6619
```

## 下一步优先处理

1. 闭合 Chevrolet Nova Sedan/Coupe 在 1973、1974及1975–1979 年间的代际与 Base/Custom 外廓分支。
2. 闭合 VW Transporter T4 长车头 Pritsche/Fahrgestell，以及 Peugeot Boxer 230P Bus、230L Kasten 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-1.6-ti-vct-120hp-56327 "Ford Fiesta VII Sedan (Mk7) 1.6 Ti-VCT (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf "C4 Picasso STéFi Brochure Cover"
[3]: https://www.auto-data.net/en/peugeot-306-sedan-7b-1.8-st-101hp-5685?utm_source=chatgpt.com "Peugeot 306 Sedan (7B) 1.8 ST (101 Hp)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Chevrolet Nova 两个 Ktype 已按车型年外廓变化完整拆分：1973、1974、1975–1976、1977–1979。
* Sedan 与 Coupe 即使部分年份三维相同，仍因物理车身形式不同使用独立尺寸组。
* 1973、1974、1975、1977–1979 的尺寸均由对应 Chevrolet 车型资料闭合；宽度统一采用不含后视镜的 overall width。([汽车档案库][1])
* 本轮新增 2 个 READY Ktype、8 行映射、8 个尺寸组。
* 剩余 PENDING：Transporter T4 一个、Peugeot Boxer I 两个。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射行：115
* 已确认并被本批引用的尺寸组：74
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28733_1973	28733	Sedan	Nova III	X	4	EU-CHEVROLET-NOVA-III-X-SEDAN-1973-01	HIGH	1973车型年轿车外廓。	READY
28733_1974	28733	Sedan	Nova III	X	4	EU-CHEVROLET-NOVA-III-X-SEDAN-1974-01	HIGH	1974车型年保险杠改变车长。	READY
28733_1975_76	28733	Sedan	Nova IV	X	4	EU-CHEVROLET-NOVA-IV-X-SEDAN-1975-1976-01	HIGH	第四代1975至1976车型年外廓。	READY
28733_1977_79	28733	Sedan	Nova IV	X	4	EU-CHEVROLET-NOVA-IV-X-SEDAN-1977-1979-01	HIGH	第四代1977至1979车型年高度分支。	READY
28734_1973	28734	Coupe	Nova III	X	2	EU-CHEVROLET-NOVA-III-X-COUPE-1973-01	HIGH	1973车型年双门Coupe外廓。	READY
28734_1974	28734	Coupe	Nova III	X	2	EU-CHEVROLET-NOVA-III-X-COUPE-1974-01	HIGH	1974车型年保险杠改变车长。	READY
28734_1975_76	28734	Coupe	Nova IV	X	2	EU-CHEVROLET-NOVA-IV-X-COUPE-1975-1976-01	HIGH	第四代1975至1976车型年双门外廓。	READY
28734_1977_79	28734	Coupe	Nova IV	X	2	EU-CHEVROLET-NOVA-IV-X-COUPE-1977-1979-01	HIGH	第四代1977至1979车型年高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-NOVA-III-X-SEDAN-1973-01	4956	1839	1369	Chevrolet Nova 1973 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf
EU-CHEVROLET-NOVA-III-X-SEDAN-1974-01	4996	1839	1369	Chevrolet Nova 1974 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1974-USA.pdf
EU-CHEVROLET-NOVA-IV-X-SEDAN-1975-1976-01	4996	1834	1379	Chevrolet Nova 1975 brochure; Chevrolet Concours and Nova 1976 brochure	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Nova.pdf; https://xr793.com/wp-content/uploads/2018/10/1976-Chevrolet-Concours-and-Nova.pdf
EU-CHEVROLET-NOVA-IV-X-SEDAN-1977-1979-01	4996	1834	1361	Chevrolet Nova 1977 brochure; Chevrolet 1978 Nova vehicle information kit; Chevrolet 1979 Nova vehicle information kit	https://xr793.com/wp-content/uploads/2021/08/1977-Chevrolet-Nova-V2.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Nova.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-Nova.pdf
EU-CHEVROLET-NOVA-III-X-COUPE-1973-01	4956	1839	1334	Chevrolet Nova 1973 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf
EU-CHEVROLET-NOVA-III-X-COUPE-1974-01	4996	1839	1334	Chevrolet Nova 1974 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1974-USA.pdf
EU-CHEVROLET-NOVA-IV-X-COUPE-1975-1976-01	4996	1834	1379	Chevrolet Nova 1975 brochure; Chevrolet Concours and Nova 1976 brochure	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Nova.pdf; https://xr793.com/wp-content/uploads/2018/10/1976-Chevrolet-Concours-and-Nova.pdf
EU-CHEVROLET-NOVA-IV-X-COUPE-1977-1979-01	4996	1834	1339	Chevrolet Nova 1977 brochure; Chevrolet 1978 Nova vehicle information kit; Chevrolet 1979 Nova vehicle information kit	https://xr793.com/wp-content/uploads/2021/08/1977-Chevrolet-Nova-V2.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Nova.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-Nova.pdf
```

## 下一步优先处理

1. 闭合 `28574` Transporter T4 的 SWB/LWB、Pritschenwagen/Fahrgestell 完整三维分支。
2. 闭合 `28684` Boxer I 230P Bus 的轴距与车顶分支。
3. 闭合 `28745` Boxer I 230L Kasten 的轴距与车顶分支；三个 Ktype 全部 READY 后立即机械汇总并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf "https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 `28684` Boxer I 230P Bus 和 `28745` Boxer I 230L Van。2.8 HDi/TED 资料明确列出 Bus/Minibus 的 `C、M、MH` 外廓，以及 Van 的 `C、CS、M、MH、MHS、LH、LHS` 外廓；尺寸表同时给出各配置的完整长宽高，宽度 `2024 mm` 为不含后视镜车身宽度。([汽车手册在线][1])
* 本轮新增 2 个 READY Ktype、10 行映射、10 个尺寸组。
* `28574` 暂不创建猜测性分支：Volkswagen 资料确认 VR6 的 Pritschenwagen 和 Fahrgestell 同时存在 `2920 mm`、`3320 mm` 轴距及单排/双排驾驶室边界，但现有完整尺寸图只闭合了长轴距 Fahrgestell、Pritsche 和 Doppelkabine，短轴距完整三维仍未闭合。([yumpu.com][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：125
* 已确认并被本批引用的尺寸组：84
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28684_swb_lowroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	HIGH	短轴距标准顶Bus外廓。	READY
28684_mwb_lowroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	HIGH	中轴距标准顶Combi外廓。	READY
28684_mwb_highroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	HIGH	中轴距高顶Bus外廓。	READY
28745_swb_lowroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	HIGH	短轴距标准顶外廓。	READY
28745_swb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	HIGH	短轴距高顶外廓。	READY
28745_mwb_lowroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	HIGH	中轴距标准顶外廓。	READY
28745_mwb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	HIGH	中轴距高顶外廓。	READY
28745_mwb_superhighroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴距超高顶外廓。	READY
28745_lwb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	HIGH	长轴距高顶外廓。	READY
28745_lwb_superhighroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴距超高顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	4749	2024	2515	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	5599	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
```

## 下一步优先处理

1. 只处理最后的 `28574`：优先闭合 T4 VR6 短轴距 Pritsche 与 Fahrgestell 的完整长宽高。
2. 同步确认该 Ktype 是否覆盖长轴距单排、长轴距双排及裸 Fahrgestell 全部分支。
3. `28574` 转为 READY 后，立即执行一次机械检查并输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data "https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data"
[2]: https://www.yumpu.com/de/document/view/22290523/aufbaurichtlinie-transporter-t4-umbauportalde "https://www.yumpu.com/de/document/view/22290523/aufbaurichtlinie-transporter-t4-umbauportalde"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* `28574` 已拆出并闭合 3 个 Fahrgestell 分支：短轴单排驾驶室、长轴单排驾驶室、长轴双排驾驶室。
* Volkswagen 官方 T4 改装指南的 VR6/TDI 表确认这些底盘形式存在；官方尺寸图给出的完整外廓分别为 `4736 × 1840 × 1920 mm`、`5136 × 1840 × 1920 mm`、`5136 × 1840 × 1910 mm`。
* Pritschenwagen、Tiefladepritsche 的完整整车三维尚未闭合，不用裸底盘尺寸替代，继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* 完全 READY Ktype：99
* PENDING Ktype：1
* READY 映射行：128
* PENDING 映射行：4
* 已确认并被本批引用的尺寸组：87
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28574_swb_chassis	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	HIGH	短轴单排驾驶室裸底盘外廓。	READY
28574_lwb_chassis	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	HIGH	长轴单排驾驶室裸底盘外廓。	READY
28574_lwb_doka_chassis	28574	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排驾驶室裸底盘外廓。	READY
28574_swb_pickup	28574	Pickup	Transporter T4		2		MEDIUM	短轴单排Pritschenwagen分支。	PENDING: 完整整车三维尚未闭合
28574_lwb_pickup	28574	Pickup	Transporter T4		2		MEDIUM	长轴单排Pritschenwagen分支。	PENDING: 完整整车三维尚未闭合
28574_lwb_lowbed	28574	Pickup	Transporter T4		2		LOW	长轴Tiefladepritsche分支。	PENDING: 完整整车三维尚未闭合
28574_lwb_doka_pickup	28574	Pickup	Transporter T4		4		MEDIUM	长轴双排Pritschenwagen分支。	PENDING: 完整整车三维尚未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	4736	1840	1920	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	5136	1840	1920	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	5136	1840	1910	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
```

## 下一步优先处理

1. 只补齐 `28574` 四个成品货台分支的完整长宽高：SWB Pritsche、LWB Pritsche、LWB Tiefladepritsche、LWB Doppelkabine Pritsche。
2. 不再核对已闭合的三个 Fahrgestell 尺寸组。
3. 四个分支闭合后立即执行一次机械汇总并输出 COMPLETE。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* `28574` 最后四个成品货台分支已闭合：SWB Pritschenwagen、LWB Pritschenwagen、LWB Tiefladepritsche、LWB Doppelkabine Pritschenwagen。
* Volkswagen 官方资料确认 T4 的短/长轴、单排/双排、Pritschenwagen、Tiefladepritsche 与 Fahrgestell 物理分支；成品货台外廓按对应尺寸资料落盘。Tiefladepritsche 保留独立尺寸组，映射置信度为 `MEDIUM`。
* 已完成机械检查：100 个输入 Ktype 全覆盖，132 个 `id` 唯一，92 个尺寸组唯一，映射引用全部闭合，无孤立组、无缺失尺寸或来源、无 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* READY 映射行：132
* DIMENSION_GROUP：92
* 两张表固定表头、唯一性、引用闭合及下载文件检查全部通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28568	28568	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-8ED-WAGON-01	HIGH		READY
28569	28569	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH		READY
28570	28570	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH		READY
28571	28571	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
28574_swb_chassis	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	HIGH	短轴单排驾驶室裸底盘外廓。	READY
28574_swb_pickup	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	HIGH	短轴单排Pritschenwagen外廓。	READY
28574_lwb_chassis	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	HIGH	长轴单排驾驶室裸底盘外廓。	READY
28574_lwb_pickup	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	HIGH	长轴单排Pritschenwagen外廓。	READY
28574_lwb_lowbed	28574	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	MEDIUM	长轴Tiefladepritsche外廓。	READY
28574_lwb_doka_chassis	28574	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排驾驶室裸底盘外廓。	READY
28574_lwb_doka_pickup	28574	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	HIGH	长轴双排Pritschenwagen外廓。	READY
28576	28576	Sedan	RS6 C6	4F2	4	EU-AUDI-RS6-C6-4F2-SEDAN-01	HIGH	RS6宽体轿车外廓。	READY
28577	28577	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH		READY
28578	28578	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH		READY
28579	28579	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28580	28580	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28581	28581	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
28582	28582	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28583	28583	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28584	28584	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28585	28585	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH		READY
28588	28588	Sedan	Fiesta VII Sedan (Mk7)		4	EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	HIGH		READY
28589	28589	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28590	28590	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28591	28591	Hatchback	C4 I Phase II	LC	5	EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
28592	28592	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
28593	28593	Coupe	C4 I Phase II	LA	3	EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	HIGH		READY
28594_airsusp	28594	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	MEDIUM	后空气悬架外廓。	READY
28594_coil	28594	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	MEDIUM	金属弹簧外廓。	READY
28595_airsusp	28595	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	MEDIUM	后空气悬架外廓。	READY
28595_coil	28595	MPV	Grand C4 Picasso I	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	MEDIUM	金属弹簧外廓。	READY
28596_coil	28596	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一Ktype覆盖钢簧高度分支。	READY
28596_airsusp	28596	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一Ktype覆盖后空气悬架高度分支。	READY
28597_coil	28597	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一Ktype覆盖钢簧高度分支。	READY
28597_airsusp	28597	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一Ktype覆盖后空气悬架高度分支。	READY
28599	28599	MPV	Musa I facelift	350	5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	HIGH		READY
28600	28600	Coupe	GranTurismo I	M145	2	EU-MASERATI-GRANTURISMO-I-M145-COUPE-4.2-01	HIGH		READY
28601	28601	Coupe	GranTurismo I	M145	2	EU-MASERATI-GRANTURISMO-I-M145-COUPE-S-4.7-01	HIGH	GranTurismo S宽体外廓。	READY
28602_prefl	28602	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	生产区间跨改款，拆分改款前外廓。	READY
28602_facelift	28602	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	生产区间跨改款，拆分改款后外廓。	READY
28603	28603	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH		READY
28604	28604	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
28605	28605	SUV	FX II	S51	5	EU-INFINITI-FX-II-S51-SUV-5D-01	HIGH		READY
28606	28606	SUV	EX	J50	5	EU-INFINITI-EX-J50-SUV-5D-01	HIGH		READY
28607	28607	Coupe	G37	CV36	2	EU-INFINITI-G37-V36-COUPE-2D-01	HIGH		READY
28608	28608	Sedan	G37	V36	4	EU-INFINITI-G37-V36-SEDAN-4D-01	HIGH		READY
28619	28619	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	HIGH	2008年后101 hp四门轿车外廓。	READY
28620	28620	Coupe	Coupe II	GK	3	EU-HYUNDAI-COUPE-II-GK-COUPE-3D-01	HIGH	输入Model为“ii”，按车身、年份与2.0版本闭合至Hyundai Coupe II GK。	READY
28621_compact	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
28621_long	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
28621_extralong	28621	MPV	Viano W639	W639		EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	MEDIUM	同一Ktype覆盖Extra-long车长分支。	READY
28622	28622	Van	Rapid I			EU-RENAULT-RAPID-I-BODY-01	MEDIUM	Kasten/Großraumlimousine统一按厢式车外廓映射。	READY
28623	28623	Van	Rapid I			EU-RENAULT-RAPID-I-BODY-01	MEDIUM	Kasten/Großraumlimousine统一按厢式车外廓映射。	READY
28626	28626	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28628	28628	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28629_prefl	28629	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产区间跨Phase I/II，拆分改款前外廓。	READY
28629_facelift	28629	Hatchback	ZX Phase II	N2	3	EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	MEDIUM	生产区间跨Phase I/II，拆分改款后外廓。	READY
28630	28630	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28631	28631	Hatchback	ZX Phase II	N2		EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28632_3dr	28632	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	HIGH	同一Ktype覆盖Phase I三门外廓。	READY
28632_5dr	28632	Hatchback	ZX Phase I	N2	5	EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-5D-01	HIGH	同一Ktype覆盖Phase I五门外廓。	READY
28635	28635	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28636	28636	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28637	28637	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28638	28638	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28639	28639	Hatchback	Laguna I		5	EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	HIGH		READY
28640	28640	Sedan	940	944	4	EU-VOLVO-940-944-SEDAN-4D-01	HIGH		READY
28641	28641	Convertible	205 I	741B	2	EU-PEUGEOT-205-I-CABRIOLET-01	HIGH		READY
28642	28642	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28643	28643	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28644	28644	Hatchback	205 facelift			EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28645	28645	Sedan	240	P244	4	EU-VOLVO-240-P244-SEDAN-4D-01	HIGH		READY
28646	28646	Wagon	240	P245	5	EU-VOLVO-240-P245-WAGON-5D-01	HIGH		READY
28655_prefl	28655	Sedan	306 Phase I	7B	4	EU-PEUGEOT-306-PHASE-I-SEDAN-4D-01	MEDIUM	生产区间跨改款，改款前外廓。	READY
28655_facelift	28655	Sedan	306 Phase II	7B	4	EU-PEUGEOT-306-PHASE-II-SEDAN-4D-01	MEDIUM	生产区间跨改款，改款后外廓。	READY
28662	28662	Sedan	164	164A	4	EU-ALFA-ROMEO-164-PREFL-SEDAN-01	HIGH		READY
28671	28671	Sedan	164		4	EU-ALFA-ROMEO-164-24V-SEDAN-01	MEDIUM		READY
28672_prefl	28672	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	HIGH	生产区间跨改款，拆分改款前外廓。	READY
28672_facelift	28672	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	HIGH	生产区间跨改款，拆分改款后外廓。	READY
28673	28673	Sedan	164		4	EU-ALFA-ROMEO-164-Q4-SEDAN-01	MEDIUM	Q4全轮驱动车身。	READY
28676	28676	Sedan	Montego Phase I		4	EU-AUSTIN-MONTEGO-PHASE-I-SEDAN-4D-01	HIGH		READY
28677	28677	Wagon	Montego Phase II		5	EU-AUSTIN-MONTEGO-PHASE-II-WAGON-5D-01	HIGH		READY
28678	28678	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28679	28679	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28680	28680	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	HIGH		READY
28682	28682	Wagon	405 I facelift	15E	5	EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	MEDIUM		READY
28683	28683	Wagon	405 I facelift	15E	5	EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	HIGH		READY
28684_swb_lowroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	HIGH	短轴距标准顶Bus外廓。	READY
28684_mwb_lowroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	HIGH	中轴距标准顶Combi外廓。	READY
28684_mwb_highroof	28684	MPV	Boxer I	230P		EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	HIGH	中轴距高顶Bus外廓。	READY
28685	28685	Hatchback	Fiesta III (Mk3)			EU-FORD-FIESTA-III-MK3-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28686	28686	Hatchback	Fiesta III (Mk3)			EU-FORD-FIESTA-III-MK3-HATCHBACK-01	HIGH	三门和五门共用相同外廓。	READY
28688	28688	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28689	28689	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28690	28690	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28691	28691	Sedan	504		4	EU-PEUGEOT-504-SEDAN-4D-01	HIGH		READY
28692	28692	Sedan	505	551A	4	EU-PEUGEOT-505-551A-SEDAN-4D-01	HIGH		READY
28697	28697	Sedan	Vectra A facelift		4	EU-OPEL-VECTRA-A-FACELIFT-SEDAN-4D-01	HIGH		READY
28701	28701	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28702	28702	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28703	28703	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28704	28704	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28705	28705	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28706	28706	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
28707	28707	Sedan	Renault 21 Phase I		4	EU-RENAULT-21-PHASE-I-SEDAN-4D-01	HIGH		READY
28709	28709	Sedan	Renault 21 Phase I		4	EU-RENAULT-21-PHASE-I-SEDAN-4D-01	HIGH		READY
28724	28724	SUV	Expedition II	U222	5	EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	HIGH		READY
28731_3dr	28731	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门外廓。	READY
28731_5dr	28731	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门外廓。	READY
28733_1973	28733	Sedan	Nova III	X	4	EU-CHEVROLET-NOVA-III-X-SEDAN-1973-01	HIGH	1973车型年轿车外廓。	READY
28733_1974	28733	Sedan	Nova III	X	4	EU-CHEVROLET-NOVA-III-X-SEDAN-1974-01	HIGH	1974车型年保险杠改变车长。	READY
28733_1975_76	28733	Sedan	Nova IV	X	4	EU-CHEVROLET-NOVA-IV-X-SEDAN-1975-1976-01	HIGH	第四代1975至1976车型年外廓。	READY
28733_1977_79	28733	Sedan	Nova IV	X	4	EU-CHEVROLET-NOVA-IV-X-SEDAN-1977-1979-01	HIGH	第四代1977至1979车型年高度分支。	READY
28734_1973	28734	Coupe	Nova III	X	2	EU-CHEVROLET-NOVA-III-X-COUPE-1973-01	HIGH	1973车型年双门Coupe外廓。	READY
28734_1974	28734	Coupe	Nova III	X	2	EU-CHEVROLET-NOVA-III-X-COUPE-1974-01	HIGH	1974车型年保险杠改变车长。	READY
28734_1975_76	28734	Coupe	Nova IV	X	2	EU-CHEVROLET-NOVA-IV-X-COUPE-1975-1976-01	HIGH	第四代1975至1976车型年双门外廓。	READY
28734_1977_79	28734	Coupe	Nova IV	X	2	EU-CHEVROLET-NOVA-IV-X-COUPE-1977-1979-01	HIGH	第四代1977至1979车型年高度分支。	READY
28741	28741	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
28743	28743	Sedan	A6 C5 facelift	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-FACELIFT-01	HIGH		READY
28744	28744	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-PREFL-01	HIGH		READY
28745_swb_lowroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	HIGH	短轴距标准顶外廓。	READY
28745_swb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	HIGH	短轴距高顶外廓。	READY
28745_mwb_lowroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	HIGH	中轴距标准顶外廓。	READY
28745_mwb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	HIGH	中轴距高顶外廓。	READY
28745_mwb_superhighroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴距超高顶外廓。	READY
28745_lwb_highroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	HIGH	长轴距高顶外廓。	READY
28745_lwb_superhighroof	28745	Van	Boxer I	230L		EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴距超高顶外廓。	READY
28746	28746	SUV	Rocsta			EU-ASIA-MOTORS-ROCSTA-SUV-OPEN-01	MEDIUM	开放式越野车身。	READY
28759	28759	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-E100-SEDAN-4D-01	HIGH		READY
28764	28764	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	HIGH		READY
28765	28765	Hatchback	Clio II Phase I			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH	三门和五门三维一致。	READY
28767	28767	Hatchback	Clio II Phase II			EU-RENAULT-CLIO-II-HATCHBACK-01	HIGH	三门和五门三维一致；改款未改变三维。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3001-3100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B7-8ED-WAGON-01	4586	1772	1453	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/247565/audi_a4_avant_2_0.html
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b6-generation-1895
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0i-16v-fsi-150hp-automatic-28713
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493	Auto-Data	https://www.auto-data.net/en/volvo-s80-ii-2.4-d-163hp-geartronic-24566
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	4736	1840	1920	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	4871	1970	1910	Drom T4 dimensions catalogue	https://www.drom.ru/catalog/lcv/volkswagen/transporter/specs/dimensions/
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	5136	1840	1920	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	5271	1970	1910	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines; Drom T4 dimensions catalogue	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf; https://www.drom.ru/catalog/lcv/volkswagen/transporter/specs/dimensions/
EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	5271	1970	1910	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines; Drom T4 dimensions catalogue	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf; https://www.drom.ru/catalog/lcv/volkswagen/transporter/specs/dimensions/
EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	5136	1840	1910	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf
EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	5271	1970	1910	Volkswagen Commercial Vehicles Transporter T4 body builder guidelines; Drom T4 dimensions catalogue	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Transporter/Archiv/Aufbaurichtlinien_fm_Transporter_T4_DE_05-2007.pdf; https://www.drom.ru/catalog/lcv/volkswagen/transporter/specs/dimensions/
EU-AUDI-RS6-C6-4F2-SEDAN-01	4928	1889	1456	Auto-Data	https://www.auto-data.net/en/audi-rs6-4f-c6-generation-1122
EU-HYUNDAI-TUCSON-JM-SUV-01	4325	1830	1730	Auto-Data	https://www.auto-data.net/en/hyundai-tucson-i-generation-2973
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480	Auto-Data	https://www.auto-data.net/en/hyundai-i30-i-generation-2963
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565	Auto-Data	https://www.auto-data.net/en/hyundai-i30-i-cw-generation-2962
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473	Auto-Data; Car and Driver	https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-1.6-ti-vct-120hp-56327; https://www.caranddriver.com/ford/fiesta/specs/2017/ford_fiesta_ford-fiesta-sedan_2017
EU-CITROEN-C4-I-PHASE-II-HATCHBACK-5D-01	4275	1773	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1214735/citroen_c4_vti_120_vtr.html
EU-CITROEN-C4-I-PHASE-II-COUPE-3D-01	4288	1769	1456	Auto-Data	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-ii-2008-generation-5305
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-AIRSUSP-01	4590	1830	1690	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-GRAND-PICASSO-I-UA-MPV-COIL-01	4590	1830	1710	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660	Citroën C4 Picasso / Grand C4 Picasso official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660	Auto-Data	https://www.auto-data.net/en/lancia-musa-facelift-2007-generation-5697
EU-MASERATI-GRANTURISMO-I-M145-COUPE-4.2-01	4881	1847	1353	Maserati GranTurismo 2008 brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2018/02/Maserati-GranTurismo-2008-USA.pdf; https://www.automobile-catalog.com/car/2008/1447985/maserati_granturismo.html
EU-MASERATI-GRANTURISMO-I-M145-COUPE-S-4.7-01	4881	1915	1353	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1448000/maserati_granturismo_s.html
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data	https://www.auto-data.net/en/seat-leon-ii-1p-2.0-tdi-16v-136hp-automatic-46459
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-fr-2.0-tdi-cr-170hp-dpf-46487
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data	https://www.auto-data.net/en/seat-toledo-iii-5p-generation-2911
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680	Auto-Data	https://www.auto-data.net/en/infiniti-fx-ii-generation-3046
EU-INFINITI-EX-J50-SUV-5D-01	4630	1800	1575	Auto-Data	https://www.auto-data.net/en/infiniti-ex-37-generation-3038
EU-INFINITI-G37-V36-COUPE-2D-01	4655	1824	1395	Auto-Data	https://www.auto-data.net/en/infiniti-g37-coupe-v36-generation-3049
EU-INFINITI-G37-V36-SEDAN-4D-01	4755	1773	1469	Auto-Data	https://www.auto-data.net/en/infiniti-g37-sedan-v36-generation-9612
EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	4310	1710	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/559175/chevrolet_aveo_1_4_lt_sedan.html
EU-HYUNDAI-COUPE-II-GK-COUPE-3D-01	4395	1760	1330	Auto-Data	https://www.auto-data.net/en/hyundai-coupe-ii-gk-generation-2991
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875	Auto-Data	https://www.auto-data.net/en/mercedes-benz-viano-w639-generation-2783
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875	Auto-Data	https://www.auto-data.net/en/mercedes-benz-viano-w639-generation-2783
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872	Auto-Data	https://www.auto-data.net/en/mercedes-benz-viano-w639-generation-2783
EU-RENAULT-RAPID-I-BODY-01	4056	1566	1776	Auto.ru	https://auto.ru/catalog/cars/renault/rapid/25004691/25004702/specifications/
EU-CITROEN-ZX-N2-PHASE-II-HATCHBACK-01	4085	1705	1404	Auto-Data; Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-ii-3-door-generation-9053; https://www.auto-data.net/en/citroen-zx-n2-phase-ii-5-door-generation-9034
EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-3D-01	4085	1718	1405	Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-i-3-door-generation-9038
EU-CITROEN-ZX-N2-PHASE-I-HATCHBACK-5D-01	4085	1707	1404	Auto-Data	https://www.auto-data.net/en/citroen-zx-n2-phase-i-5-door-generation-3340
EU-RENAULT-LAGUNA-I-HATCHBACK-5D-01	4510	1750	1430	Auto-Data	https://www.auto-data.net/en/renault-laguna-1.8-16v-120hp-10335
EU-VOLVO-940-944-SEDAN-4D-01	4871	1750	1425	Auto-Data	https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286
EU-PEUGEOT-205-I-CABRIOLET-01	3705	1590	1375	Auto-Data	https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276
EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	3705	1560	1375	Auto-Data	https://www.auto-data.net/en/peugeot-205-i-20a-c-facelift-1987-1.4-i-75hp-5648
EU-VOLVO-240-P244-SEDAN-4D-01	4785	1707	1427	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/45905/volvo_244_turbo.html
EU-VOLVO-240-P245-WAGON-5D-01	4785	1707	1460	Auto Motor und Sport	https://www.auto-motor-und-sport.de/marken-modelle/volvo/240/technische-daten/
EU-PEUGEOT-306-PHASE-I-SEDAN-4D-01	4232	1689	1386	Auto-Data	https://www.auto-data.net/en/peugeot-306-sedan-7b-1.8-st-101hp-5685
EU-PEUGEOT-306-PHASE-II-SEDAN-4D-01	4267	1689	1386	Auto-Data	https://www.auto-data.net/en/peugeot-306-sedan-facelift-1997-generation-6619
EU-ALFA-ROMEO-164-PREFL-SEDAN-01	4555	1760	1400	AutoWeek; Brembo Parts	https://www.autoweek.nl/auto/4262/alfa-romeo-164-3-0-v6/; https://www.bremboparts.com/europe/en/catalogue/alfa-romeo-164-164-3-0-164a/000028662-1
EU-ALFA-ROMEO-164-24V-SEDAN-01	4550	1760	1390	Auto-Data	https://www.auto-data.net/en/alfa-romeo-164-164-3.0-i-v6-24v-230hp-1256
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	4691	1777	1432	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-cla-200-cdi-136hp-18684
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	4640	1777	1432	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-facelift-2016-generation-4746
EU-ALFA-ROMEO-164-Q4-SEDAN-01	4670	1760	1360	Auto-Data	https://www.auto-data.net/en/alfa-romeo-164-164-3.0-24v-228hp-q4-1254
EU-AUSTIN-MONTEGO-PHASE-I-SEDAN-4D-01	4468	1710	1418	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/62645/austin_montego_1_3.html
EU-AUSTIN-MONTEGO-PHASE-II-WAGON-5D-01	4465	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1701050/montego_estate_2_0_l_automatic.html
EU-PEUGEOT-405-I-15E-WAGON-PREFL-01	4398	1714	1450	Auto-Data	https://www.auto-data.net/en/peugeot-405-i-break-15e-generation-1272
EU-PEUGEOT-405-I-15E-WAGON-FACELIFT-01	4398	1714	1481	Auto-Data	https://www.auto-data.net/en/peugeot-405-i-break-15e-facelift-1992-generation-1270
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-FORD-FIESTA-III-MK3-HATCHBACK-01	3743	1606	1379	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-110hp-8058
EU-PEUGEOT-504-SEDAN-4D-01	4490	1690	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/2557640/peugeot_504.html
EU-PEUGEOT-505-551A-SEDAN-4D-01	4580	1735	1440	Auto-Data	https://www.auto-data.net/en/peugeot-505-551a-2.0-98hp-5500
EU-OPEL-VECTRA-A-FACELIFT-SEDAN-4D-01	4432	1706	1400	Auto-Data	https://www.auto-data.net/en/opel-vectra-a-facelift-1992-1.6i-71hp-2299
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2943245/renault_19_4d_1_8_95.html
EU-RENAULT-21-PHASE-I-SEDAN-4D-01	4462	1714	1414	Automobile-Catalog; Automobile-Catalog	https://www.automobile-catalog.com/car/1986/52340/renault_21_txe.html; https://www.automobile-catalog.com/car/1986/55805/renault_21_turbo_d.html
EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	5228	2000	1971	Auto-Data	https://www.auto-data.net/en/ford-expedition-ii-generation-1709
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360	Auto-Data	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-generation-8655
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-5-door-generation-8656
EU-CHEVROLET-NOVA-III-X-SEDAN-1973-01	4956	1839	1369	Chevrolet Nova 1973 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf
EU-CHEVROLET-NOVA-III-X-SEDAN-1974-01	4996	1839	1369	Chevrolet Nova 1974 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1974-USA.pdf
EU-CHEVROLET-NOVA-IV-X-SEDAN-1975-1976-01	4996	1834	1379	Chevrolet Nova 1975 brochure; Chevrolet Concours and Nova 1976 brochure	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Nova.pdf; https://xr793.com/wp-content/uploads/2018/10/1976-Chevrolet-Concours-and-Nova.pdf
EU-CHEVROLET-NOVA-IV-X-SEDAN-1977-1979-01	4996	1834	1361	Chevrolet Nova 1977 brochure; Chevrolet 1978 Nova vehicle information kit; Chevrolet 1979 Nova vehicle information kit	https://xr793.com/wp-content/uploads/2021/08/1977-Chevrolet-Nova-V2.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Nova.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-Nova.pdf
EU-CHEVROLET-NOVA-III-X-COUPE-1973-01	4956	1839	1334	Chevrolet Nova 1973 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1973-USA.pdf
EU-CHEVROLET-NOVA-III-X-COUPE-1974-01	4996	1839	1334	Chevrolet Nova 1974 brochure	https://autocatalogarchive.com/wp-content/uploads/2025/06/Chevrolet-Nova-1974-USA.pdf
EU-CHEVROLET-NOVA-IV-X-COUPE-1975-1976-01	4996	1834	1379	Chevrolet Nova 1975 brochure; Chevrolet Concours and Nova 1976 brochure	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Nova.pdf; https://xr793.com/wp-content/uploads/2018/10/1976-Chevrolet-Concours-and-Nova.pdf
EU-CHEVROLET-NOVA-IV-X-COUPE-1977-1979-01	4996	1834	1339	Chevrolet Nova 1977 brochure; Chevrolet 1978 Nova vehicle information kit; Chevrolet 1979 Nova vehicle information kit	https://xr793.com/wp-content/uploads/2021/08/1977-Chevrolet-Nova-V2.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Nova.pdf; https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1979-Chevrolet-Nova.pdf
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430	Auto-Data	https://www.auto-data.net/en/volvo-v70-i-2.4-20v-turbo-193hp-awd-9270
EU-AUDI-A6-C5-4B2-SEDAN-FACELIFT-01	4796	1810	1453	Auto-Data	https://www.auto-data.net/en/audi-a6-4b-c5-facelift-2001-3.0-v6-220hp-quattro-tiptronic-26953
EU-AUDI-A6-C5-4B2-SEDAN-PREFL-01	4796	1810	1451	Auto-Data	https://www.auto-data.net/en/audi-a6-4b-c5-2.8-v6-30v-193hp-quattro-4714
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	4749	2024	2515	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	5599	2024	2505	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870	Peugeot Boxer 2002 User Guide	https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/2/?srch=technical+data
EU-ASIA-MOTORS-ROCSTA-SUV-OPEN-01	3720	1690	1820	Auto-Data	https://www.auto-data.net/en/asia-rocsta-generation-671
EU-TOYOTA-COROLLA-E100-SEDAN-4D-01	4270	1685	1380	Auto-Data	https://www.auto-data.net/en/toyota-corolla-vii-e100-1.6-si-114hp-3351
EU-VOLVO-S70-SEDAN-01	4720	1760	1400	Auto-Data	https://www.auto-data.net/en/volvo-s70-generation-1939
EU-RENAULT-CLIO-II-HATCHBACK-01	3773	1639	1417	Autogidas; Carfolio	https://autogidas.lt/en/auto-katalogas/renault/clio/ii-1.6i-16v-1998-2001-k30192; https://www.carfolio.com/renault-clio-ii-sport-phase-2-100144
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3001-3100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3001-3100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3001-3100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3783 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1871 行）

