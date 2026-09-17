# 任务：all 第 5301-5400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0054__f1b80d26


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5301-5400 行

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
all 第 5301-5400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A3-8Y-SEDAN-PREFL-01	4495	1816	1425
EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	4343	1816	1449
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	4738	1842	1435
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-A6-C8-AVANT-TFSI-E-01	4939	1886	1494
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460
EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	5012	1998	1694
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705
EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	4818	1948	1391
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GT-III-V8-COUPE-01	4850	1966	1405
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390
EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	4850	1954	1399
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	4709	1827	1444
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	4825	1835	1841
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	4425	1835	1844
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-LWB-01	4818	1835	1861
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-SWB-01	4418	1835	1861
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-LWB-01	4825	1835	1847
EU-FORD-TRANSIT-CONNECT-II-V408-VAN-FACELIFT-SWB-01	4425	1835	1859
EU-FORD-USA-MUSTANG-S550-ECOBOOST-COUPE-PREFL-01	4784	1916	1381
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-CONVERTIBLE-01	4789	1916	1387
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-COUPE-01	4789	1916	1373
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382
EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	4784	1916	1381
EU-FORD-USA-MUSTANG-S550-SHELBY-GT500-COUPE-01	4813	1946	1379
EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	4280	1775	1480
EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	4245	1775	1480
EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	4500	1775	1565
EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	4475	1775	1565
EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	4485	1780	1500
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	4165	1800	1565
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680
EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	4325	1795	1720
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	4405	1810	1630
EU-JEEP-COMPASS-II-MP-PREFL-4XE-SUV-01	4394	1819	1649
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1695
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	4935	1852	1481
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	5052	1913	1422
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424
EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	5246	1899	1494
EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	5255	1905	1503
EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	5096	1871	1479
EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	5125	1905	1493
EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	5116	1899	1496
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	5333	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	4983	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	5331	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	4981	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3500	1620	1705

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Land Rover	88/109 mk ii	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	57	77	Sep 1958	Nov 1961	2024-03-01	141433
Citroën	Jumpy iii	Ë-jumpy	Kasten	Frontantrieb	Elektro	100	136	Sep 2020	-	2024-05-01	141435
Land Rover	88/109 mk iia	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	51	69	Sep 1963	Oct 1971	2024-03-01	141437
Land Rover	88/109 mk iia	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	57	78	Dec 1961	Oct 1971	2024-03-01	141438
Land Rover	88/109 mk iia	2.6 4X4	Geländewagen geschlossen	Allrad	Benzin	64	87	Sep 1967	Oct 1971	2024-03-01	141440
Land Rover	88/109 mk iia	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Sep 1963	Oct 1971	2024-03-01	141441
Land Rover	88/109 mk iii	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	51	69	Nov 1971	Dec 1986	2024-03-01	141442
Land Rover	88/109 mk iii	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	68	92	Jan 1980	Dec 1983	2024-03-01	141444
Land Rover	88/109 mk iii	2.3 D 4X4	Geländewagen geschlossen	Allrad	Diesel	46	63	Nov 1971	Dec 1986	2024-03-01	141445
Land Rover	88/109 mk iii	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	94	128	Nov 1979	May 1984	2025-12-01	141446
Ford	Transit connect	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	55	75	May 2018	-	2024-03-01	141447
BMW	5	530 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	215	292	Jul 2020	Jun 2023	2024-03-01	141450
BMW	5	530 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	215	292	Jul 2020	Jun 2023	2024-03-01	141451
Land Rover	88/109 mk i	2.0 4X4	Geländewagen offen	Allrad	Benzin	39	53	Jul 1956	Aug 1958	2024-03-01	141452
Land Rover	88/109 mk i	2.0 D 4X4	Geländewagen offen	Allrad	Diesel	39	53	Jan 1957	Aug 1958	2024-03-01	141453
Land Rover	88/109 mk ii	2.0 D 4X4	Geländewagen offen	Allrad	Diesel	39	53	Sep 1958	Nov 1961	2024-03-01	141454
Land Rover	88/109 mk ii	2.3 4X4	Geländewagen offen	Allrad	Benzin	57	77	Sep 1958	Nov 1961	2024-03-01	141455
Land Rover	88/109 mk iia	2.3 4X4	Geländewagen offen	Allrad	Benzin	51	69	Sep 1963	Oct 1971	2024-03-01	141456
Land Rover	88/109 mk iia	2.3 4X4	Geländewagen offen	Allrad	Benzin	57	78	Dec 1961	Oct 1971	2024-03-01	141457
Land Rover	88/109 mk iia	2.6 4X4	Geländewagen offen	Allrad	Benzin	64	87	Sep 1967	Oct 1971	2024-03-01	141460
Land Rover	88/109 mk iia	2.3 D 4X4	Geländewagen offen	Allrad	Diesel	46	63	Sep 1963	Oct 1971	2024-03-01	141461
Land Rover	88/109 mk iii	2.3 4X4	Geländewagen offen	Allrad	Benzin	51	69	Nov 1971	Oct 1985	2024-03-01	141462
Land Rover	88/109 mk iii	2.3 D 4X4	Geländewagen offen	Allrad	Diesel	46	63	Nov 1971	Oct 1985	2024-03-01	141465
Land Rover	88/109 mk iii	3.5 4X4	Geländewagen offen	Allrad	Benzin	68	92	Jan 1980	Dec 1983	2024-03-01	141488
Land Rover	88/109 mk iii	3.5 4X4	Geländewagen offen	Allrad	Benzin	94	128	Nov 1979	May 1984	2025-12-01	141489
Suzuki	Wagon r+	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Jan 2005	Dec 2008	2024-03-01	141493
BMW	3	316 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	90	122	Jul 2020	-	2024-03-01	141494
BMW	3	316 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	90	122	Aug 2020	-	2024-03-01	141496
BMW	3	318 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	100	136	Apr 2020	-	2024-03-01	141498
BMW	3	318 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	110	150	Apr 2020	-	2024-03-01	141499
BMW	3	318 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	100	136	Aug 2020	-	2024-03-01	141501
BMW	3	318 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	110	150	Aug 2020	-	2024-03-01	141502
Lancia	Flaminia	2.8	Cabriolet	Heckantrieb	Benzin	110	150	Jan 1963	Dec 1969	2024-03-01	141504
Peugeot	508 ii	Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Jun 2020	-	2024-03-01	141507
Peugeot	508 sw ii	Puretech 130	Kombi	Frontantrieb	Benzin	96	131	Jun 2020	-	2024-03-01	141508
Lancia	Flaminia gt	2.8	Coupe	Heckantrieb	Benzin	110	150	Jan 1963	Dec 1969	2024-03-01	141509
Hyundai	I30	1.0 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Nov 2016	-	2024-03-01	141510
Hyundai	I30	1.4 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	103	140	Nov 2016	Dec 2020	2025-02-03	141511
Hyundai	Kona	1.0 T-gdi	Kasten/SUV	Frontantrieb	Benzin	88	120	Jul 2017	-	2024-03-01	141512
Hyundai	Kona	1.6 GDI Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	104	141	Jun 2019	-	2024-03-01	141514
Lancia	Flaminia	2.8	Coupe	Heckantrieb	Benzin	112	152	Jan 1963	Dec 1969	2024-03-01	141515
Hyundai	Kona	EV	Kasten/SUV	Frontantrieb	Elektro	150	204	Apr 2018	-	2024-03-01	141516
Hyundai	Tucson	1.6 Crdi	Kasten/SUV	Frontantrieb	Diesel	100	136	Aug 2018	Dec 2020	2024-03-01	141517
Hyundai	Tucson	1.6 T-gdi	Kasten/SUV	Frontantrieb	Benzin	130	177	Jun 2015	Dec 2020	2024-03-01	141518
Hyundai	Santa fe iv	2.2 Crdi	Kasten/SUV	Frontantrieb	Diesel	147	200	Jul 2018	Nov 2020	2024-03-01	141519
Hyundai	Santa fe iv	2.2 Crdi AWD	Kasten/SUV	Allrad	Diesel	147	200	Jul 2018	Nov 2020	2024-03-01	141520
Ligier	Pulse 4	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	8	11	Aug 2019	-	2024-03-01	141521
Skoda	Octavia	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141524
Bentley	Continental	4.0 GTC AWD	Cabriolet	Allrad	Benzin	373	507	Feb 2012	Jul 2018	2024-03-01	141525
Daihatsu	Cuore v	1	Schrägheck	Frontantrieb	Benzin	41	56	Nov 1998	Dec 2002	2024-03-01	141526
BMW	3	320 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	150	204	Jul 2020	-	2024-03-01	141528
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	330	449	Dec 2019	Apr 2023	2024-05-01	141530
BMW	3	320 E Plug-in-hybrid	Kombi	Heckantrieb	Benzin/Elektro	150	204	Jul 2020	-	2024-03-01	141531
Ford USA	Mustang convertible	5.0 V8	Cabriolet	Heckantrieb	Benzin	330	449	Dec 2019	Apr 2023	2024-05-01	141532
Jeep	Compass	1.3	SUV	Frontantrieb	Benzin	96	131	Aug 2020	-	2024-03-01	141533
Peugeot	Expert	E-expert	Pritsche/Fahrgestell	Frontantrieb	Elektro	100	136	Sep 2020	Oct 2023	2024-07-01	141534
Skoda	Octavia	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141535
VW	Id.3	1ST	Schrägheck	Heckantrieb	Elektro	150	204	Nov 2019	-	2024-03-01	141537
Audi	A3	30 Tfsi	Stufenheck	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141544
Audi	A4 allroad b9	40 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	150	204	Sep 2020	-	2024-03-01	141545
Audi	A4 allroad b9	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	195	265	Aug 2020	-	2024-03-01	141546
Mercedes-benz	E-Klasse	E 300 E	Kombi	Heckantrieb	Benzin/Elektro	235	320	Jun 2020	Aug 2023	2024-03-01	141547
Mercedes-benz	E-Klasse	E 450 EQ Boost	Kombi	Allrad	Benzin/Elektro	270	367	Aug 2020	Aug 2023	2024-03-01	141548
Mercedes-benz	E-Klasse	E 200 EQ Boost	Kombi	Allrad	Benzin/Elektro	145	197	Aug 2020	Aug 2023	2024-03-01	141549
Audi	A4 b9 avant	40 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	150	204	May 2020	-	2024-03-01	141567
Mercedes-benz	E-Klasse	E 400 D 4-matic	Kombi	Allrad	Diesel	243	330	Jul 2020	Oct 2023	2024-03-01	141568
Audi	A4 b9 avant	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	195	265	Aug 2020	-	2024-03-01	141570
Audi	A4 b9 avant	40 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141573
Mercedes-benz	E-Klasse	E 400 D 4-matic	Kombi	Allrad	Diesel	243	330	Jul 2020	Oct 2023	2024-03-01	141574
Audi	A4 b9 avant	40 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141576
Audi	A4 b9	40 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141578
Audi	A4 b9	40 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141579
Audi	A4 b9	45 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	195	265	Aug 2020	-	2024-03-01	141580
Audi	A4 b9	40 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	150	204	May 2020	-	2024-03-01	141581
KIA	Sorento iv	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	169	230	Jun 2020	-	2024-03-01	141583
KIA	Sorento iv	1.6 T-gdi Hybrid AWD	SUV	Allrad	Benzin/Elektro	169	230	Jun 2020	-	2024-03-01	141585
Audi	A6 c8 avant	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141586
Audi	A6 c8 avant	45 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141587
Renault	Koleos ii	1.3 TCE 160	SUV	Frontantrieb	Benzin	116	158	Jul 2020	-	2024-03-01	141588
Mercedes-benz	124	200 CE	Coupe	Heckantrieb	Benzin	100	136	Jul 1992	Jul 1993	2024-03-01	141593
Mercedes-benz	124	200 CE	Coupe	Heckantrieb	Benzin	87	118	Mar 1990	Dec 1992	2024-03-01	141594
Mercedes-benz	124	200 CE	Coupe	Heckantrieb	Benzin	90	122	Mar 1990	Dec 1992	2024-03-01	141595
Audi	A6 c8	45 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141611
Audi	A6 c8	45 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141612
Mercedes-benz	S-Klasse	300 SEL	Stufenheck	Heckantrieb	Benzin	125	170	Mar 1966	Dec 1967	2024-03-01	141613
Audi	A7 sportback	45 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141614
Audi	A7 sportback	45 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	195	265	May 2020	-	2024-03-01	141615
Audi	Q8	SQ8 Quattro	SUV	Allrad	Benzin	373	507	Feb 2020	-	2024-03-01	141616
Audi	A5	40 Tfsi Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	150	204	Jul 2020	-	2025-06-01	141618
Audi	A5	40 Tfsi Mild Hybrid Quattro	Cabriolet	Allrad	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141619
Audi	A5	35 Tfsi Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	110	150	Jun 2020	-	2024-03-01	141620
Audi	A5	45 Tfsi Mild Hybrid Quattro	Cabriolet	Allrad	Benzin/Elektro	195	265	Jun 2020	-	2024-03-01	141621
Audi	A5	40 TDI Mild Hybrid Quattro	Cabriolet	Allrad	Diesel/Elektro	150	204	Sep 2020	-	2024-03-01	141622
Audi	A5	40 Tfsi Mild Hybrid	Coupe	Frontantrieb	Benzin/Elektro	150	204	Jul 2020	-	2024-03-01	141623
Audi	A5	40 Tfsi Mild Hybrid Quattro	Coupe	Allrad	Benzin/Elektro	150	204	Jul 2020	-	2024-03-01	141624
Audi	A5	45 Tfsi Mild Hybrid Quattro	Coupe	Allrad	Benzin/Elektro	195	265	Oct 2019	-	2024-03-01	141625
Audi	A5	40 TDI Mild Hybrid Quattro	Coupe	Allrad	Diesel/Elektro	150	204	Sep 2020	-	2024-03-01	141626
Audi	A5	40 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141627
Audi	A5	40 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	141628
Audi	A5	45 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	195	265	Oct 2019	-	2024-03-01	141629


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 100 个输入 Ktype 的首轮车身聚类，生成 126 条映射行。21 个 `Land Rover 88/109` Ktype 已按 `88 SWB / 109 LWB` 拆分，但因门数、开放/封闭车顶及统一三维尚未闭合，暂不创建猜测性尺寸组。
* `Hyundai Kona` 的 ICE、Hybrid 和 EV Ktype 均跨越改款节点，已拆分为 `prefl / facelift`。官方资料确认改款后 Hybrid 为 `4205×1800×1565 mm`，改款后 EV 为 `4205×1800×1570 mm`，其中宽度为不含后视镜口径。
* Audi A4 allroad 改款车型的官方三维为 `4762×1847×1493 mm`，与已有 `4750×1842×1493 mm` 组不一致，因此未覆盖历史组，新增独立 facelift 尺寸组。
* Mercedes-Benz C124 200 CE 与 W109 300 SEL 已使用 Mercedes-Benz 官方历史档案闭合尺寸组。([marsClassic][1])
* 本轮新增 15 个尺寸组；其余已闭合映射直接复用跨批次已有尺寸组，未重复输出尺寸记录。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：126
* READY 映射：80
* PENDING 映射：46
* 涉及 PENDING 的输入 Ktype：24
* 已确认并引用尺寸组：49
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141433_swb	141433	SUV	Land Rover Series II	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141433_lwb	141433	SUV	Land Rover Series II	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141435	141435	Van	Jumpy III	K0			MEDIUM	候选包含XS、M、XL及不同车高分支。	PENDING: Ktype覆盖的长度与车高分支尚未闭合
141437_swb	141437	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141437_lwb	141437	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141438_swb	141438	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141438_lwb	141438	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141440_swb	141440	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141440_lwb	141440	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141441_swb	141441	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141441_lwb	141441	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141442_swb	141442	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141442_lwb	141442	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141444_swb	141444	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141444_lwb	141444	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141445_swb	141445	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141445_lwb	141445	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141446_swb	141446	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141446_lwb	141446	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141447_swb	141447	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	HIGH	短轴乘用车身。	READY
141447_lwb	141447	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	HIGH	长轴乘用车身。	READY
141450	141450	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH		READY
141451	141451	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH		READY
141452_swb	141452	SUV	Land Rover Series I	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141452_lwb	141452	SUV	Land Rover Series I	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141453_swb	141453	SUV	Land Rover Series I	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141453_lwb	141453	SUV	Land Rover Series I	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141454_swb	141454	SUV	Land Rover Series II	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141454_lwb	141454	SUV	Land Rover Series II	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141455_swb	141455	SUV	Land Rover Series II	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141455_lwb	141455	SUV	Land Rover Series II	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141456_swb	141456	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141456_lwb	141456	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141457_swb	141457	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141457_lwb	141457	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141460_swb	141460	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141460_lwb	141460	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141461_swb	141461	SUV	Land Rover Series IIA	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141461_lwb	141461	SUV	Land Rover Series IIA	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141462_swb	141462	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141462_lwb	141462	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141465_swb	141465	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141465_lwb	141465	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141488_swb	141488	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141488_lwb	141488	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141489_swb	141489	SUV	Land Rover Series III	88			MEDIUM	已确认覆盖88英寸短轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141489_lwb	141489	SUV	Land Rover Series III	109			MEDIUM	已确认覆盖109英寸长轴；门数、车顶及统一尺寸仍待闭合。	PENDING: 88/109车身分支的门数、车顶与三维尚未闭合
141493	141493	Hatchback	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
141494	141494	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141496	141496	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141498	141498	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141499	141499	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141501	141501	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141502	141502	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141504	141504	Convertible	Flaminia Touring		2	EU-LANCIA-FLAMINIA-TOURING-CONVERTIBLE-01	HIGH		READY
141507	141507	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门Fastback外廓。	READY
141508	141508	Wagon	508 II	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
141509	141509	Coupe	Flaminia Touring GT		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-01	HIGH		READY
141510	141510	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
141511	141511	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
141512_prefl	141512	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	改款前ICE外廓。	READY
141512_facelift	141512	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	改款后ICE外廓。	READY
141514_prefl	141514	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	HIGH	改款前Hybrid外廓。	READY
141514_facelift	141514	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-FACELIFT-01	HIGH	改款后Hybrid外廓。	READY
141515	141515	Coupe	Flaminia Pininfarina	3B	2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-01	HIGH		READY
141516_prefl	141516	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	改款前EV外廓。	READY
141516_facelift	141516	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-FACELIFT-01	HIGH	改款后EV外廓。	READY
141517	141517	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
141518	141518	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
141519	141519	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
141520	141520	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
141521_swb	141521	Pickup	Pulse 4		2		MEDIUM	官方资料确认短车架分支，三维与车身边界待闭合。	PENDING: 短车架三维与物理边界尚未闭合
141521_lwb	141521	Pickup	Pulse 4		2		MEDIUM	官方资料确认长车架分支，三维与车身边界待闭合。	PENDING: 长车架三维与物理边界尚未闭合
141524	141524	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH		READY
141525	141525	Convertible	Continental GTC II facelift		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	HIGH		READY
141526	141526	Hatchback	Cuore V	L701	3	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	HIGH		READY
141528	141528	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	HIGH	320e与330e共用PHEV外廓。	READY
141530	141530	Coupe	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH		READY
141531	141531	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	320e与330e共用PHEV外廓。	READY
141532	141532	Convertible	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	HIGH		READY
141533	141533	SUV	Compass II pre-facelift	MP	5	EU-JEEP-COMPASS-II-MP-PREFL-FWD-SUV-01	HIGH	前驱1.3车高边界。	READY
141534	141534	Pickup	Expert III	K0	2		MEDIUM	候选为电动平台/底盘驾驶室配置。	PENDING: Ktype覆盖的轴距与平台车三维尚未闭合
141535	141535	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
141537	141537	Hatchback	ID.3 I		5	EU-VOLKSWAGEN-ID3-I-HATCHBACK-PREFL-01	HIGH		READY
141544	141544	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH		READY
141545	141545	Wagon	A4 allroad B9 facelift	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	HIGH		READY
141546	141546	Wagon	A4 allroad B9 facelift	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	HIGH		READY
141547	141547	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	HIGH	E300e插混车高边界。	READY
141548	141548	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	HIGH	E450 4MATIC车高边界。	READY
141549	141549	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E200-4MATIC-01	HIGH	E200 4MATIC车高边界。	READY
141567	141567	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141568	141568	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH		READY
141570	141570	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141573	141573	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141574	141574	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH		READY
141576	141576	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141578	141578	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141579	141579	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141580	141580	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141581	141581	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141583	141583	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
141585	141585	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
141586	141586	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
141587	141587	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
141588	141588	SUV	Koleos II	HC	5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
141593	141593	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141594	141594	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141595	141595	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141611	141611	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
141612	141612	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
141613	141613	Sedan	S-Class W109	W109	4	EU-MERCEDES-BENZ-S-KLASSE-W109-300SEL-SEDAN-01	HIGH		READY
141614	141614	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-C8-4K8-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
141615	141615	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-C8-4K8-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
141616	141616	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SQ8-SUV-01	HIGH		READY
141618	141618	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141619	141619	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141620	141620	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141621	141621	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141622	141622	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141623	141623	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141624	141624	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141625	141625	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141626	141626	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141627	141627	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
141628	141628	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
141629	141629	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-FLAMINIA-TOURING-CONVERTIBLE-01	4500	1680	1300	Automobile-Catalog 1964 Lancia Flaminia Cabriolet 3C 2.8 Touring	https://www.automobile-catalog.com/car/1964/1374800/lancia_flaminia_cabriolet_3c_2_8_touring.html
EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-01	4500	1680	1305	Automobile-Catalog 1963 Lancia Flaminia GT 3C 2.8 Touring	https://www.automobile-catalog.com/car/1963/1374785/lancia_flaminia_gt_3c_2_8_touring.html
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-FACELIFT-01	4205	1800	1565	Hyundai Motor Europe 2020 New Kona technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200902_new_kona_and_kona_n-line/202009_Technical_Data_new_Kona_and_all-new_Kona_N-Line.pdf
EU-LANCIA-FLAMINIA-PININFARINA-COUPE-01	4680	1740	1420	Automobile-Catalog 1963 Lancia Flaminia Coupe 3B 2.8	https://www.automobile-catalog.com/car/1963/1374770/lancia_flaminia_coupe_3b_2_8.html
EU-HYUNDAI-KONA-I-OS-EV-SUV-FACELIFT-01	4205	1800	1570	Hyundai Motor UK New KONA Electric technical data	https://www.hyundai.news/newsroom/dam/eu/uk/20210308_kona_electric/hyundai-kona-electric-pricing-specs-tech-0321.pdf
EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	3410	1475	1420	Auto-Data Daihatsu Cuore L701 1.0 i 56 Hp	https://www.auto-data.net/en/daihatsu-cuore-l701-1.0-i-l701-56hp-51
EU-JEEP-COMPASS-II-MP-PREFL-FWD-SUV-01	4394	1819	1629	Auto-Data Jeep Compass II MP 1.3 GSE T4 130 Hp	https://www.auto-data.net/en/jeep-compass-ii-mp-1.3-gse-t4-130hp-50874
EU-VOLKSWAGEN-ID3-I-HATCHBACK-PREFL-01	4261	1809	1552	Volkswagen Newsroom ID.3 visionary design	https://www.volkswagen-newsroom.com/en/the-id3-a-new-era-begins-5327/visionary-design-5329
EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	4762	1847	1493	Audi UK A4 allroad 45 TFSI quattro technical data	https://press.audi.co.uk/assets/documents/original/4236-AudiUK00029686AudiA4allroad45TFSI.pdf
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	4945	1852	1476	Automobile-Catalog 2021 Mercedes-Benz E 300 e T-Modell	https://www.automobile-catalog.com/car/2021/2968445/mercedes-benz_e_300_e_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	4945	1852	1467	Automobile-Catalog 2020 Mercedes-Benz E 450 4MATIC T-Modell	https://www.automobile-catalog.com/car/2020/2968505/mercedes-benz_e_450_4matic_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E200-4MATIC-01	4945	1852	1461	Automobile-Catalog 2020 Mercedes-Benz E 200 4MATIC T-Modell	https://www.automobile-catalog.com/car/2020/2968460/mercedes-benz_e_200_4matic_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	4655	1740	1394	Mercedes-Benz Public Archive 200 CE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-CE.xhtml?oid=4602
EU-MERCEDES-BENZ-S-KLASSE-W109-300SEL-SEDAN-01	5000	1810	1415	Mercedes-Benz Public Archive 300 SEL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL.xhtml?oid=4911
EU-AUDI-A7-C8-4K8-SPORTBACK-01	4969	1908	1422	Automobile-Catalog 2020 Audi A7 Sportback 45 TFSI; Automobile-Catalog 2020 Audi A7 Sportback 45 TFSI quattro	https://www.automobile-catalog.com/car/2020/2913500/audi_a7_sportback_45_tfsi.html;https://www.automobile-catalog.com/car/2020/2979680/audi_a7_sportback_45_tfsi_quattro.html
```

## 下一步优先处理

1. 集中闭合 Land Rover Series I、II、IIA、III 的 88/109 短长轴、开放/封闭车顶和门数边界，批量消除 42 条 PENDING 映射。
2. 核对 Citroën ë-Jumpy K0 的 XS、M、XL及车高覆盖范围，并优先复用已有 Jumpy III 尺寸组。
3. 闭合 Peugeot e-Expert 平台/底盘驾驶室的轴距分支。
4. 闭合 Ligier Pulse 4 短车架和长车架的完整三维。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-CE.xhtml?oid=4602 "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-CE.xhtml?oid=4602"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* `141435` 已按 ë-Jumpy 的 XS、M、XL 三种长度及缓存中已有的低/高车身分支拆为 5 条 READY 映射，全部复用既有尺寸组，不重复输出尺寸数据。Citroën 发布资料确认该车型覆盖三种长度。([Stellantis Media][1])
* `141534` 已确认是标准长度的 e-Expert 平台/底盘驾驶室，2 门，外廓为 `5210 × 1920 × 1890 mm`，新建一个尺寸组。Peugeot 车型资料确认电动版提供标准长度 Chassis Cab；规格页直接列出该平台车的长宽高。([斯莱特里车库][2])
* `141521` 已按 Ligier Pulse 4 短车架、长车架拆分并闭合。厂家技术图给出短版 `2600 × 1458 × 1812 mm`、长版 `3356 × 1458 × 1812 mm`；图中另列含后视镜总宽 `1764 mm`，因此落盘宽度采用不含后视镜的 `1458 mm`。
* 删除上一轮中 6 条不成立的临时 SWB 分支：`141440_swb`、`141444_swb`、`141446_swb`、`141460_swb`、`141488_swb`、`141489_swb`。2.6 L 发动机限长轴车型，Series III Stage One V8 属于 109 英寸车身。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：88
* PENDING 映射：36
* 涉及 PENDING 的输入 Ktype：21
* 已确认并引用尺寸组：57
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141435_xs_low	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS标准车高厢式车分支。	READY
141435_xs_high	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	HIGH	XS高车身厢式车分支。	READY
141435_m_low	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M标准车高厢式车分支。	READY
141435_m_high	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	HIGH	M高车身厢式车分支。	READY
141435_xl	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL厢式车分支。	READY
141521_swb	141521	Pickup	Pulse 4		2	EU-LIGIER-PULSE-4-PLATFORM-SWB-01	HIGH	短车架平台车分支。	READY
141521_lwb	141521	Pickup	Pulse 4		2	EU-LIGIER-PULSE-4-PLATFORM-LWB-01	HIGH	长车架平台车分支。	READY
141534	141534	Pickup	Expert III	K0	2	EU-PEUGEOT-EXPERT-III-K0-E-EXPERT-CHASSIS-STANDARD-01	HIGH	标准长度电动平台/底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LIGIER-PULSE-4-PLATFORM-SWB-01	2600	1458	1812	Ligier Professional Pulse 4 technical characteristics	https://www.dra-go.com/productos/FichatecnicaLIGIERPULSE4.pdf
EU-LIGIER-PULSE-4-PLATFORM-LWB-01	3356	1458	1812	Ligier Professional Pulse 4 technical characteristics	https://www.dra-go.com/productos/FichatecnicaLIGIERPULSE4.pdf
EU-PEUGEOT-EXPERT-III-K0-E-EXPERT-CHASSIS-STANDARD-01	5210	1920	1890	La Centrale Peugeot Expert III Plancher Cabine 50 kWh Standard; Peugeot e-Expert launch information	https://www.lacentrale.fr/fiche-technique-voiture-peugeot-expert-iii%2Bplancher%2Bcabine%2B50%2Bkwh%2Bstandard-2020.html;https://www.slatterysgarage.ie/new-peugeot-e-expert/
```

## 下一步优先处理

1. 集中闭合剩余 21 个 Land Rover Ktype／36 条映射。
2. 先建立 Series I 开放式 88/109 两组，再分别闭合 Series II、IIA、III 的封闭式与开放式 SWB/LWB 组。
3. 保留已确认的发动机边界：2.6 L 与 3.5 L V8 只关联 109 英寸长轴组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/citroen/press/citroen-e-jumpy-100-electric-opening-of-orders?utm_source=chatgpt.com "CITROËN Ë-JUMPY 100% ËLECTRIC: OPENING OF ..."
[2]: https://www.slatterysgarage.ie/new-peugeot-e-expert/ "NEW PEUGEOT e-EXPERT -"
[3]: https://en.wikipedia.org/wiki/Land_Rover_series?utm_source=chatgpt.com "Land Rover series"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Land Rover Series I 与 Series II 的开放式 88 英寸短轴、109 英寸长轴车身。
* 4 个 Ktype、8 条映射由 `PENDING` 更新为 `READY`。
* 开放式车型统一确认为 2 门；尺寸按 1957 年 Series I 与 1960 年 Series II 原厂宣传册首次建组。([汽车手册][1])
* 已闭合尺寸组未重新抓取或重复输出。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：96
* PENDING 映射：28
* 涉及 PENDING 的输入 Ktype：17
* 已确认并引用尺寸组：61
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141452_swb	141452	SUV	Land Rover Series I	88	2	EU-LAND-ROVER-SERIES-I-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141452_lwb	141452	SUV	Land Rover Series I	109	2	EU-LAND-ROVER-SERIES-I-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141453_swb	141453	SUV	Land Rover Series I	88	2	EU-LAND-ROVER-SERIES-I-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141453_lwb	141453	SUV	Land Rover Series I	109	2	EU-LAND-ROVER-SERIES-I-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141454_swb	141454	SUV	Land Rover Series II	88	2	EU-LAND-ROVER-SERIES-II-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141454_lwb	141454	SUV	Land Rover Series II	109	2	EU-LAND-ROVER-SERIES-II-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141455_swb	141455	SUV	Land Rover Series II	88	2	EU-LAND-ROVER-SERIES-II-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141455_lwb	141455	SUV	Land Rover Series II	109	2	EU-LAND-ROVER-SERIES-II-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-SERIES-I-88-OPEN-01	3569	1588	1930	Rover Company 1957 Land-Rover Series I brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-I-109-OPEN-01	4407	1588	1981	Rover Company 1957 Land-Rover Series I brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-II-88-OPEN-01	3620	1630	1970	Rover Company 1960 Land-Rover Series II brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1960.pdf
EU-LAND-ROVER-SERIES-II-109-OPEN-01	4440	1630	2060	Rover Company 1960 Land-Rover Series II brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1960.pdf
```

## 下一步优先处理

1. 闭合 Series IIA 开放式 88/109 分支。
2. 闭合 Series III 开放式 88/109 分支，其中 2.6 L 与 3.5 L V8 仅保留 109 长轴。
3. 最后集中处理 Series II、IIA、III 封闭式车身的 88 三门、109 三门及五门边界。

推进信号：CONTINUE

[1]: https://www.auto-brochures.com/land_rover.html "Auto-Brochures | Land Rover Car & Truck PDF Sales Brochure/Catalog/Flyer/Info Discovery Sport Evoque LR2 LR3 LR4 Range Rover Sport Series I Series II Series III Velar"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Land Rover Series IIA 开放式 88/109 车身，7 条映射转为 `READY`。
* 已闭合 Land Rover Series III 开放式 88/109 车身，4 条映射转为 `READY`。
* 两个 3.5 V8 Ktype 已关联独立的 Series III Stage One V8 109 开放式尺寸组。官方 1980 年资料明确给出帆布顶外廓 `4445 × 1680 × 1980 mm`。
* Series IIA 与普通 Series III 开放式尺寸分别使用已核对的具体车型规格页面闭合，宽度均为不含后视镜口径。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：109
* PENDING 映射：15
* 涉及 PENDING 的输入 Ktype：9
* 已确认并引用尺寸组：66
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141456_swb	141456	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141456_lwb	141456	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141457_swb	141457	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141457_lwb	141457	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141460_lwb	141460	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	2.6升109英寸开放式长轴车身。	READY
141461_swb	141461	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141461_lwb	141461	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141462_swb	141462	SUV	Land Rover Series III	88	2	EU-LAND-ROVER-SERIES-III-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141462_lwb	141462	SUV	Land Rover Series III	109	2	EU-LAND-ROVER-SERIES-III-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141465_swb	141465	SUV	Land Rover Series III	88	2	EU-LAND-ROVER-SERIES-III-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141465_lwb	141465	SUV	Land Rover Series III	109	2	EU-LAND-ROVER-SERIES-III-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141488_lwb	141488	SUV	Land Rover Series III Stage One V8	109	2	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	HIGH	109英寸Stage One V8开放式车身。	READY
141489_lwb	141489	SUV	Land Rover Series III Stage One V8	109	2	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	MEDIUM	高功率标注对应109英寸V8开放式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	3620	1676	1969	Automobile-Catalog 1964 Land-Rover 88 Diesel	https://www.automobile-catalog.com/car/1964/1392050/land-rover_88_diesel.html
EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	4440	1676	2068	Automobile-Catalog 1969 Land-Rover 109 Diesel	https://www.automobile-catalog.com/car/1969/1392440/land-rover_109_diesel.html
EU-LAND-ROVER-SERIES-III-88-OPEN-01	3621	1692	1969	Automobile-Catalog 1975 Land-Rover 88 4-Cylinder Petrol	https://www.automobile-catalog.com/car/1975/1392950/land-rover_88_4-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-109-OPEN-01	4445	1692	1969	Automobile-Catalog 1975 Land-Rover 109 6-Cylinder Petrol	https://www.automobile-catalog.com/car/1975/1392875/land-rover_109_6-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	4445	1680	1980	Leyland Australia 1980 Land Rover 109 Series III 3.5 brochure	https://roverp6australia.net/wp-content/uploads/2020/09/1980-Land-Rover-Series-3-109-Inch-3.5-Brochure-Australia-PDF.pdf
```

## 下一步优先处理

1. 闭合剩余 9 个封闭式 Land Rover Ktype、15 条映射。
2. 优先创建 Series II 封闭式 88/109 两组。
3. 批量闭合 Series IIA 封闭式 88/109，并单独确认 2.6 升仅关联 109 分支。
4. 最后闭合 Series III 普通封闭式 88/109及 Stage One V8 109 封闭式组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1964/1392050/land-rover_88_diesel.html?utm_source=chatgpt.com "1964 Land-Rover 88 Diesel Specs Review (37.5 kW ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 9 个 Land Rover Ktype、15 条封闭式车身映射。
* 本轮首次创建 7 个封闭式 Land Rover 尺寸组；已确认的开放式及其他车型尺寸组均直接复用。
* 已完成机械检查：表头正确、124 个 `id` 唯一、73 个 `DIMENSION_GROUP_ID` 唯一、全部映射引用闭合、尺寸及来源字段完整。
* 当前已无 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* 最终 Ktype 映射：124 行
* READY 映射：124
* PENDING 映射：0
* 最终 DIMENSION_GROUP：73 行
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141433_swb	141433	SUV	Land Rover Series II	88	3	EU-LAND-ROVER-SERIES-II-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141433_lwb	141433	SUV	Land Rover Series II	109	5	EU-LAND-ROVER-SERIES-II-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141435_xs_low	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS标准车高厢式车分支。	READY
141435_xs_high	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	HIGH	XS高车身厢式车分支。	READY
141435_m_low	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M标准车高厢式车分支。	READY
141435_m_high	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	HIGH	M高车身厢式车分支。	READY
141435_xl	141435	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL厢式车分支。	READY
141437_swb	141437	SUV	Land Rover Series IIA	88	3	EU-LAND-ROVER-SERIES-IIA-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141437_lwb	141437	SUV	Land Rover Series IIA	109	5	EU-LAND-ROVER-SERIES-IIA-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141438_swb	141438	SUV	Land Rover Series IIA	88	3	EU-LAND-ROVER-SERIES-IIA-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141438_lwb	141438	SUV	Land Rover Series IIA	109	5	EU-LAND-ROVER-SERIES-IIA-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141440_lwb	141440	SUV	Land Rover Series IIA	109	5	EU-LAND-ROVER-SERIES-IIA-109-CLOSED-01	HIGH	2.6升109英寸五门封闭式长轴车身。	READY
141441_swb	141441	SUV	Land Rover Series IIA	88	3	EU-LAND-ROVER-SERIES-IIA-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141441_lwb	141441	SUV	Land Rover Series IIA	109	5	EU-LAND-ROVER-SERIES-IIA-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141442_swb	141442	SUV	Land Rover Series III	88	3	EU-LAND-ROVER-SERIES-III-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141442_lwb	141442	SUV	Land Rover Series III	109	5	EU-LAND-ROVER-SERIES-III-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141444_lwb	141444	SUV	Land Rover Series III Stage One V8	109	5	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-CLOSED-01	HIGH	109英寸Stage One V8五门封闭式车身。	READY
141445_swb	141445	SUV	Land Rover Series III	88	3	EU-LAND-ROVER-SERIES-III-88-CLOSED-01	HIGH	88英寸三门封闭式短轴车身。	READY
141445_lwb	141445	SUV	Land Rover Series III	109	5	EU-LAND-ROVER-SERIES-III-109-CLOSED-01	HIGH	109英寸五门封闭式长轴车身。	READY
141446_lwb	141446	SUV	Land Rover Series III Stage One V8	109	5	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-CLOSED-01	MEDIUM	高功率标注对应109英寸Stage One V8五门封闭式外廓。	READY
141447_swb	141447	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	HIGH	短轴乘用车身。	READY
141447_lwb	141447	MPV	Transit Connect II facelift	V408	5	EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	HIGH	长轴乘用车身。	READY
141450	141450	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH		READY
141451	141451	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH		READY
141452_swb	141452	SUV	Land Rover Series I	88	2	EU-LAND-ROVER-SERIES-I-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141452_lwb	141452	SUV	Land Rover Series I	109	2	EU-LAND-ROVER-SERIES-I-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141453_swb	141453	SUV	Land Rover Series I	88	2	EU-LAND-ROVER-SERIES-I-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141453_lwb	141453	SUV	Land Rover Series I	109	2	EU-LAND-ROVER-SERIES-I-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141454_swb	141454	SUV	Land Rover Series II	88	2	EU-LAND-ROVER-SERIES-II-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141454_lwb	141454	SUV	Land Rover Series II	109	2	EU-LAND-ROVER-SERIES-II-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141455_swb	141455	SUV	Land Rover Series II	88	2	EU-LAND-ROVER-SERIES-II-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141455_lwb	141455	SUV	Land Rover Series II	109	2	EU-LAND-ROVER-SERIES-II-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141456_swb	141456	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141456_lwb	141456	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141457_swb	141457	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141457_lwb	141457	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141460_lwb	141460	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	2.6升109英寸开放式长轴车身。	READY
141461_swb	141461	SUV	Land Rover Series IIA	88	2	EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141461_lwb	141461	SUV	Land Rover Series IIA	109	2	EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141462_swb	141462	SUV	Land Rover Series III	88	2	EU-LAND-ROVER-SERIES-III-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141462_lwb	141462	SUV	Land Rover Series III	109	2	EU-LAND-ROVER-SERIES-III-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141465_swb	141465	SUV	Land Rover Series III	88	2	EU-LAND-ROVER-SERIES-III-88-OPEN-01	HIGH	88英寸开放式短轴车身。	READY
141465_lwb	141465	SUV	Land Rover Series III	109	2	EU-LAND-ROVER-SERIES-III-109-OPEN-01	HIGH	109英寸开放式长轴车身。	READY
141488_lwb	141488	SUV	Land Rover Series III Stage One V8	109	2	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	HIGH	109英寸Stage One V8开放式车身。	READY
141489_lwb	141489	SUV	Land Rover Series III Stage One V8	109	2	EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	MEDIUM	高功率标注对应109英寸V8开放式外廓。	READY
141493	141493	Hatchback	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
141494	141494	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141496	141496	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141498	141498	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141499	141499	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
141501	141501	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141502	141502	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
141504	141504	Convertible	Flaminia Touring		2	EU-LANCIA-FLAMINIA-TOURING-CONVERTIBLE-01	HIGH		READY
141507	141507	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门Fastback外廓。	READY
141508	141508	Wagon	508 II	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
141509	141509	Coupe	Flaminia Touring GT		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-01	HIGH		READY
141510	141510	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
141511	141511	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
141512_prefl	141512	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	改款前ICE外廓。	READY
141512_facelift	141512	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	改款后ICE外廓。	READY
141514_prefl	141514	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	HIGH	改款前Hybrid外廓。	READY
141514_facelift	141514	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-FACELIFT-01	HIGH	改款后Hybrid外廓。	READY
141515	141515	Coupe	Flaminia Pininfarina	3B	2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-01	HIGH		READY
141516_prefl	141516	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	改款前EV外廓。	READY
141516_facelift	141516	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-FACELIFT-01	HIGH	改款后EV外廓。	READY
141517	141517	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
141518	141518	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
141519	141519	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
141520	141520	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
141521_swb	141521	Pickup	Pulse 4		2	EU-LIGIER-PULSE-4-PLATFORM-SWB-01	HIGH	短车架平台车分支。	READY
141521_lwb	141521	Pickup	Pulse 4		2	EU-LIGIER-PULSE-4-PLATFORM-LWB-01	HIGH	长车架平台车分支。	READY
141524	141524	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH		READY
141525	141525	Convertible	Continental GTC II facelift		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	HIGH		READY
141526	141526	Hatchback	Cuore V	L701	3	EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	HIGH		READY
141528	141528	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	HIGH	320e与330e共用PHEV外廓。	READY
141530	141530	Coupe	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH		READY
141531	141531	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	320e与330e共用PHEV外廓。	READY
141532	141532	Convertible	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	HIGH		READY
141533	141533	SUV	Compass II pre-facelift	MP	5	EU-JEEP-COMPASS-II-MP-PREFL-FWD-SUV-01	HIGH	前驱1.3车高边界。	READY
141534	141534	Pickup	Expert III	K0	2	EU-PEUGEOT-EXPERT-III-K0-E-EXPERT-CHASSIS-STANDARD-01	HIGH	标准长度电动平台/底盘驾驶室。	READY
141535	141535	Wagon	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH		READY
141537	141537	Hatchback	ID.3 I		5	EU-VOLKSWAGEN-ID3-I-HATCHBACK-PREFL-01	HIGH		READY
141544	141544	Sedan	A3 8Y	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH		READY
141545	141545	Wagon	A4 allroad B9 facelift	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	HIGH		READY
141546	141546	Wagon	A4 allroad B9 facelift	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	HIGH		READY
141547	141547	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	HIGH	E300e插混车高边界。	READY
141548	141548	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	HIGH	E450 4MATIC车高边界。	READY
141549	141549	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E200-4MATIC-01	HIGH	E200 4MATIC车高边界。	READY
141567	141567	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141568	141568	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH		READY
141570	141570	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141573	141573	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141574	141574	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH		READY
141576	141576	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH		READY
141578	141578	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141579	141579	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141580	141580	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141581	141581	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH		READY
141583	141583	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
141585	141585	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
141586	141586	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
141587	141587	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
141588	141588	SUV	Koleos II	HC	5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
141593	141593	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141594	141594	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141595	141595	Coupe	E-Class C124 phase I	C124	2	EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	HIGH		READY
141611	141611	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
141612	141612	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
141613	141613	Sedan	S-Class W109	W109	4	EU-MERCEDES-BENZ-S-KLASSE-W109-300SEL-SEDAN-01	HIGH		READY
141614	141614	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-C8-4K8-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
141615	141615	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-C8-4K8-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
141616	141616	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SQ8-SUV-01	HIGH		READY
141618	141618	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141619	141619	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141620	141620	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141621	141621	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141622	141622	Convertible	A5 F5 facelift	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
141623	141623	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141624	141624	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141625	141625	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141626	141626	Coupe	A5 F5 facelift	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH		READY
141627	141627	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
141628	141628	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
141629	141629	Hatchback	A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门Sportback外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5301-5400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-SERIES-II-88-CLOSED-01	3620	1628	1969	Automobile-Catalog 1960 Land-Rover 88 Wagon Diesel	https://www.automobile-catalog.com/car/1960/1391870/land-rover_88_wagon_diesel.html
EU-LAND-ROVER-SERIES-II-109-CLOSED-01	4445	1628	2068	Automobile-Catalog 1960 Land-Rover 109 Station Wagon	https://www.automobile-catalog.com/car/1960/1391960/land-rover_109_station_wagon.html
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910	Citroën Jumpy and ë-Jumpy 2020 technical data	https://mezzicommerciali.it/wp-content/uploads/2020/10/Citroen-Jumpy-e-Jumpy-%E2%80%93-DATI-TECNICI-2020.pdf
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950	Citroën Jumpy and ë-Jumpy 2020 technical data	https://mezzicommerciali.it/wp-content/uploads/2020/10/Citroen-Jumpy-e-Jumpy-%E2%80%93-DATI-TECNICI-2020.pdf
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899	Citroën Jumpy and ë-Jumpy 2020 technical data	https://mezzicommerciali.it/wp-content/uploads/2020/10/Citroen-Jumpy-e-Jumpy-%E2%80%93-DATI-TECNICI-2020.pdf
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935	Citroën Jumpy and ë-Jumpy 2020 technical data	https://mezzicommerciali.it/wp-content/uploads/2020/10/Citroen-Jumpy-e-Jumpy-%E2%80%93-DATI-TECNICI-2020.pdf
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940	Citroën Jumpy and ë-Jumpy 2020 technical data	https://mezzicommerciali.it/wp-content/uploads/2020/10/Citroen-Jumpy-e-Jumpy-%E2%80%93-DATI-TECNICI-2020.pdf
EU-LAND-ROVER-SERIES-IIA-88-CLOSED-01	3620	1676	1969	Automobile-Catalog 1969 Land-Rover 88 Wagon Diesel	https://www.automobile-catalog.com/car/1969/1392545/land-rover_88_wagon_diesel.html
EU-LAND-ROVER-SERIES-IIA-109-CLOSED-01	4440	1676	2068	Automobile-Catalog 1969 Land-Rover 109 Station Wagon 2.25-litre	https://www.automobile-catalog.com/car/1969/1392455/land-rover_109_station_wagon_2_25-litre.html
EU-LAND-ROVER-SERIES-III-88-CLOSED-01	3621	1692	1969	Automobile-Catalog 1977 Land-Rover 88 Station Wagon 4-cylinder Petrol	https://www.automobile-catalog.com/car/1977/1392980/land-rover_88_station_wagon_4-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-109-CLOSED-01	4445	1692	1969	Automobile-Catalog 1975 Land-Rover 109 Station Wagon 4-cylinder Petrol	https://www.automobile-catalog.com/car/1975/1392905/land-rover_109_station_wagon_4-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-CLOSED-01	4445	1690	2007	Automobile-Catalog 1982 Land-Rover 109 Station Wagon Stage One V8	https://www.automobile-catalog.com/car/1982/1393040/land-rover_109_station_wagon_stage-1_v8.html
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-SWB-01	4425	1835	1844	Ford Transit Connect owner manual SWB dimensions	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1608973&Uid=G1608972&countryCode=USA&div=f&languageCode=en&userMarket=GBR&vFilteringEnabled=False&variantid=4091
EU-FORD-TRANSIT-CONNECT-II-V408-MPV-FACELIFT-LWB-01	4825	1835	1841	Ford Transit Connect owner manual LWB dimensions	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1608967&Uid=G1608966&countryCode=USA&div=f&languageCode=en&userMarket=GBR&vFilteringEnabled=False&variantid=4091
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483	BMW 530e Sedan technical data	https://www.press.bmwgroup.com/global/article/attachment/T0325537EN/471546
EU-LAND-ROVER-SERIES-I-88-OPEN-01	3569	1588	1930	Rover Company 1957 Land-Rover Series I brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-I-109-OPEN-01	4407	1588	1981	Rover Company 1957 Land-Rover Series I brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-II-88-OPEN-01	3620	1630	1970	Rover Company 1960 Land-Rover Series II brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1960.pdf
EU-LAND-ROVER-SERIES-II-109-OPEN-01	4440	1630	2060	Rover Company 1960 Land-Rover Series II brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1960.pdf
EU-LAND-ROVER-SERIES-IIA-88-OPEN-01	3620	1676	1969	Automobile-Catalog 1964 Land-Rover 88 Diesel	https://www.automobile-catalog.com/car/1964/1392050/land-rover_88_diesel.html
EU-LAND-ROVER-SERIES-IIA-109-OPEN-01	4440	1676	2068	Automobile-Catalog 1969 Land-Rover 109 Diesel	https://www.automobile-catalog.com/car/1969/1392440/land-rover_109_diesel.html
EU-LAND-ROVER-SERIES-III-88-OPEN-01	3621	1692	1969	Automobile-Catalog 1975 Land-Rover 88 4-Cylinder Petrol	https://www.automobile-catalog.com/car/1975/1392950/land-rover_88_4-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-109-OPEN-01	4445	1692	1969	Automobile-Catalog 1975 Land-Rover 109 6-Cylinder Petrol	https://www.automobile-catalog.com/car/1975/1392875/land-rover_109_6-cylinder_petrol.html
EU-LAND-ROVER-SERIES-III-STAGE-ONE-V8-109-OPEN-01	4445	1680	1980	Leyland Australia 1980 Land Rover 109 Series III 3.5 brochure	https://roverp6australia.net/wp-content/uploads/2020/09/1980-Land-Rover-Series-3-109-Inch-3.5-Brochure-Australia-PDF.pdf
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3500	1620	1705	Auto-Data Suzuki Wagon R+ II specifications	https://www.auto-data.net/en/suzuki-wagon-r-ii-generation-3708
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	BMW 3 Series Touring technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0305733EN/446340
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0305731EN/specifications-of-the-new-bmw-3-series-sedan-320d-and-the-new-bmw-3-series-sedan-320d-xdrive-valid-from-03/2020
EU-LANCIA-FLAMINIA-TOURING-CONVERTIBLE-01	4500	1680	1300	Automobile-Catalog 1964 Lancia Flaminia Cabriolet 3C 2.8 Touring	https://www.automobile-catalog.com/car/1964/1374800/lancia_flaminia_cabriolet_3c_2_8_touring.html
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404	Peugeot New 508 press information	https://www.media.stellantis.com/em-en/peugeot/press/the-new-peugeot-508-the-radical-saloon
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 SW product information	https://www.media.stellantis.com/em-en/peugeot/508
EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-01	4500	1680	1305	Automobile-Catalog 1963 Lancia Flaminia GT 3C 2.8 Touring	https://www.automobile-catalog.com/car/1963/1374785/lancia_flaminia_gt_3c_2_8_touring.html
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Hyundai i30 press kit technical data	https://www.hyundai.news/eu/models/i-range/i30/press-kit.html
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550	Hyundai 2017 Kona model specifications	https://www.hyundai.com/kr/ko/brand/brandstory/model/kona-history/2017-kona
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550	Hyundai Motor Europe 2020 New Kona technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200902_new_kona_and_kona_n-line/202009_Technical_Data_new_Kona_and_all-new_Kona_N-Line.pdf
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	4165	1800	1565	Hyundai Kona Hybrid technical data	https://www.hyundai.news/newsroom/dam/eu/uk/20190603_all-new_kona_hybrid/Hyundai_Kona_Hybrid_Technical.pdf
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-FACELIFT-01	4205	1800	1565	Hyundai Motor Europe 2020 New Kona technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200902_new_kona_and_kona_n-line/202009_Technical_Data_new_Kona_and_all-new_Kona_N-Line.pdf
EU-LANCIA-FLAMINIA-PININFARINA-COUPE-01	4680	1740	1420	Automobile-Catalog 1963 Lancia Flaminia Coupe 3B 2.8	https://www.automobile-catalog.com/car/1963/1374770/lancia_flaminia_coupe_3b_2_8.html
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570	Hyundai Kona Electric technical data	https://www.hyundai.news/newsroom/dam/uk/press-kits/20180828_kona_electric/Hyundai_Kona_Electric_-_Technical_data_and_specifications.pdf
EU-HYUNDAI-KONA-I-OS-EV-SUV-FACELIFT-01	4205	1800	1570	Hyundai Motor UK New KONA Electric technical data	https://www.hyundai.news/newsroom/dam/eu/uk/20210308_kona_electric/hyundai-kona-electric-pricing-specs-tech-0321.pdf
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Hyundai Tucson TL facelift brochure	https://www.hyundai.com/content/dam/hyundai/lb/en/data/marketing/brochure/product/tucson-2018/TL_PE_2018_GEN_LHD_ENG_28p_FINAL_Low.pdf
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai 2018 Santa Fe TM model specifications	https://www.hyundai.com/kr/ko/brand/brandstory/model/santafe-history/2018-santa-fe
EU-LIGIER-PULSE-4-PLATFORM-SWB-01	2600	1458	1812	Ligier Professional Pulse 4 technical characteristics	https://www.dra-go.com/productos/FichatecnicaLIGIERPULSE4.pdf
EU-LIGIER-PULSE-4-PLATFORM-LWB-01	3356	1458	1812	Ligier Professional Pulse 4 technical characteristics	https://www.dra-go.com/productos/FichatecnicaLIGIERPULSE4.pdf
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470	Škoda Octavia specifications brochure	https://www.skoda.com.au/_doc/5ccfeae2-641f-441f-a45a-cae89fb27990
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403	Automobile-Catalog 2012 Bentley Continental GTC V8	https://www.automobile-catalog.com/car/2012/1614980/bentley_continental_gtc_v8.html
EU-DAIHATSU-CUORE-V-L701-HATCHBACK-01	3410	1475	1420	Auto-Data Daihatsu Cuore L701 1.0 i 56 Hp	https://www.auto-data.net/en/daihatsu-cuore-l701-1.0-i-l701-56hp-51
EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	4709	1827	1444	BMW 330e Sedan technical specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0302235EN_GB/462801
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382	Ford 2020 Mustang technical specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442	BMW 3 Series Touring plug-in hybrid specifications	https://www.press.bmwgroup.com/ireland/article/detail/T0300673EN/the-new-bmw-3-series-touring
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396	Ford 2020 Mustang technical specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-JEEP-COMPASS-II-MP-PREFL-FWD-SUV-01	4394	1819	1629	Auto-Data Jeep Compass II MP 1.3 GSE T4 130 Hp	https://www.auto-data.net/en/jeep-compass-ii-mp-1.3-gse-t4-130hp-50874
EU-PEUGEOT-EXPERT-III-K0-E-EXPERT-CHASSIS-STANDARD-01	5210	1920	1890	La Centrale Peugeot Expert III Plancher Cabine 50 kWh Standard; Peugeot e-Expert launch information	https://www.lacentrale.fr/fiche-technique-voiture-peugeot-expert-iii%2Bplancher%2Bcabine%2B50%2Bkwh%2Bstandard-2020.html;https://www.slatterysgarage.ie/new-peugeot-e-expert/
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468	Škoda Octavia specifications brochure	https://www.skoda.com.au/_doc/5ccfeae2-641f-441f-a45a-cae89fb27990
EU-VOLKSWAGEN-ID3-I-HATCHBACK-PREFL-01	4261	1809	1552	Volkswagen Newsroom ID.3 visionary design	https://www.volkswagen-newsroom.com/en/the-id3-a-new-era-begins-5327/visionary-design-5329
EU-AUDI-A3-8Y-SEDAN-PREFL-01	4495	1816	1425	Audi A3 Sedan dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a3-sedan-1383
EU-AUDI-A4-ALLROAD-B9-WAGON-FACELIFT-01	4762	1847	1493	Audi UK A4 allroad 45 TFSI quattro technical data	https://press.audi.co.uk/assets/documents/original/4236-AudiUK00029686AudiA4allroad45TFSI.pdf
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	4945	1852	1476	Automobile-Catalog 2021 Mercedes-Benz E 300 e T-Modell	https://www.automobile-catalog.com/car/2021/2968445/mercedes-benz_e_300_e_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	4945	1852	1467	Automobile-Catalog 2020 Mercedes-Benz E 450 4MATIC T-Modell	https://www.automobile-catalog.com/car/2020/2968505/mercedes-benz_e_450_4matic_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E200-4MATIC-01	4945	1852	1461	Automobile-Catalog 2020 Mercedes-Benz E 200 4MATIC T-Modell	https://www.automobile-catalog.com/car/2020/2968460/mercedes-benz_e_200_4matic_t-modell.html
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460	Audi A4 technical specifications brochure	https://media.audi.com/is/content/audi/country/vn/assets/catalogs/audi-a4/AudiA4_2024_NoPR_ENG_11Oct24.pdf
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460	Mercedes-Benz 2020 E-Class facelift media information	https://file.media.mercedes-benz.com/article/cbd23719-1e0e-4814-b763-3222fa5d7168
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431	Audi A4 technical specifications brochure	https://media.audi.com/is/content/audi/country/vn/assets/catalogs/audi-a4/AudiA4_2024_NoPR_ENG_11Oct24.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1695	Kia Sorento specifications	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/spechsheet/Sorento-Specifications.pdf
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	Audi A6 Avant dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-avant-1400
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos dimensions	https://www.user-manual.renault.com/en/content/renault-koleos/technical-specifications/information-about-vehicle/dimensions-mm
EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	4655	1740	1394	Mercedes-Benz Public Archive 200 CE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-CE.xhtml?oid=4602
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi A6 Sedan dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-sedan-1403
EU-MERCEDES-BENZ-S-KLASSE-W109-300SEL-SEDAN-01	5000	1810	1415	Mercedes-Benz Public Archive 300 SEL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL.xhtml?oid=4911
EU-AUDI-A7-C8-4K8-SPORTBACK-01	4969	1908	1422	Automobile-Catalog 2020 Audi A7 Sportback 45 TFSI; Automobile-Catalog 2020 Audi A7 Sportback 45 TFSI quattro	https://www.automobile-catalog.com/car/2020/2913500/audi_a7_sportback_45_tfsi.html;https://www.automobile-catalog.com/car/2020/2979680/audi_a7_sportback_45_tfsi_quattro.html
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708	Audi SQ8 dimensions	https://www.audi.com/en/publications/dimensions/dimensions-sq8-1424
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Audi A5 Cabriolet dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a5-cabriolet-1394
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Audi A5 Coupé dimensions	https://www.audi.com/en/publications/dimensions/dimensions-audi-a5-coupe-until-2024-1607
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 Sportback dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a5-sportback-1393
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5301-5400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5669 行）
- 累计尺寸组：dimension_groups_final.tsv（2072 行）

