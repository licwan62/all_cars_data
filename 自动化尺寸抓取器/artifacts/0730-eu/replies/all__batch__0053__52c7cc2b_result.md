# 任务：all 第 5201-5300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0053__52c7cc2b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5201-5300 行

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
all 第 5201-5300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741
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
EU-BMW-7-F01-SEDAN-FACELIFT-01	5079	1902	1471
EU-BMW-7-F01-SEDAN-PREFL-01	5072	1902	1479
EU-BMW-7-G11-LCI-SEDAN-01	5120	1902	1467
EU-BMW-7-G11-SEDAN-01	5098	1902	1478
EU-BMW-7-G12-LCI-SEDAN-LWB-01	5260	1902	1479
EU-BMW-7-G12-SEDAN-LWB-01	5238	1902	1485
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-BMW-X4-F98-M-COMPETITION-SUV-01	4758	1927	1620
EU-BMW-X4-F98-M-SUV-01	4758	1927	1618
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-F95-M-COMPETITION-SUV-01	4953	2015	1749
EU-BMW-X5-F95-M-SUV-01	4953	2015	1751
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-BMW-X6-F16-SUV-01	4909	1989	1702
EU-BMW-X6-F96-M-COMPETITION-SUV-01	4953	2019	1692
EU-BMW-X6-F96-M-SUV-01	4953	2019	1693
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696
EU-BMW-X7-G07-SUV-01	5151	2000	1805
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	4973	1986	1979
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	5340	1986	1977
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	4973	1986	2389
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	5340	1986	2017
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	5340	1986	2381
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H1-01	4973	1986	2000
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1H2-01	4973	1986	2366
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H1-01	5340	1986	1979
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2H2-01	5340	1986	2343
EU-FORD-USA-MUSTANG-S550-ECOBOOST-COUPE-PREFL-01	4784	1916	1381
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-CONVERTIBLE-01	4789	1916	1387
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-COUPE-01	4789	1916	1373
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382
EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	4784	1916	1381
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
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680
EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	4325	1795	1720
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450
EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	4384	1725	1450
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495
EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	4971	1945	1461
EU-MERCEDES-BENZ-AMG-GT-R190-GT-R-ROADSTER-01	4551	2007	1260
EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	4551	1939	1260
EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	5054	1953	1455
EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	5054	1953	1442
EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	5054	1953	1447
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435
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
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1616
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494
EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	4424	1804	1494
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
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	5333	1920	1890
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	4983	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435
EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	4653	1790	1445
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1865
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	4840	1885	1845
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510
EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	3940	1745	1500
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	5	530 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	183	249	Jul 2020	Jun 2023	2024-03-01	141093
BMW	5	530 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	183	249	Jul 2020	Jun 2023	2024-03-01	141094
Mercedes-benz	Cla	CLA 200 D 4-matic	Coupe	Allrad	Diesel	110	150	Apr 2019	-	2024-03-01	141097
Mercedes-benz	Cla	CLA 220 D 4-matic	Coupe	Allrad	Diesel	140	190	Jul 2020	-	2024-03-01	141102
BMW	5	520 I Mild-hybrid	Kombi	Heckantrieb	Benzin/Elektro	120	163	Jul 2020	-	2024-03-01	141103
BMW	5	518 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	100	136	Jul 2020	-	2024-03-01	141104
BMW	5	518 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	110	150	Jul 2020	-	2024-03-01	141105
BMW	5	520 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	120	163	Nov 2019	-	2024-03-01	141106
Mercedes-benz	Cla	CLA 250 E	Coupe	Frontantrieb	Benzin/Elektro	160	218	Jun 2020	-	2024-03-01	141107
BMW	5	530 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	183	249	Jul 2020	-	2024-03-01	141108
BMW	5	530 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	183	249	Jul 2020	-	2024-03-01	141109
Toyota	Yaris	1.6 GR 4WD	Schrägheck	Allrad	Benzin	192	261	Feb 2020	-	2024-03-01	141131
BMW	7	730 D, LD Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	May 2022	2024-03-01	141133
BMW	7	730 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	155	211	Jul 2020	Jun 2022	2024-03-01	141134
BMW	7	730 D, LD Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	210	286	Jul 2020	Jun 2022	2024-03-01	141135
BMW	7	740 D, LD Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	250	340	Jul 2020	Jun 2022	2024-03-01	141138
BMW	X3	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	183	249	Jul 2020	-	2024-03-01	141142
BMW	X3	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	141143
BMW	X3	Xdrive M40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2025-06-01	141144
BMW	X3	Sdrive 18 D Mild-hybrid	SUV	Heckantrieb	Diesel/Elektro	100	136	Jul 2020	-	2024-03-01	141145
BMW	X3	Sdrive 18 D Mild-hybrid	SUV	Heckantrieb	Diesel/Elektro	110	150	Jul 2020	-	2024-03-01	141146
BMW	X4	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	183	249	Jul 2020	-	2024-03-01	141147
BMW	X4	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	141148
BMW	X4	Xdrive M40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2024-03-01	141149
BMW	X5	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	183	249	Aug 2020	-	2024-03-01	141150
BMW	X5	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	210	286	Aug 2020	-	2024-03-01	141151
BMW	X6	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	183	249	Aug 2020	-	2024-03-01	141152
BMW	X6	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	210	286	Aug 2020	Mar 2023	2024-03-01	141153
BMW	X6	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	155	211	Aug 2020	-	2024-03-01	141154
BMW	X7	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	Aug 2020	-	2025-06-01	141161
BMW	X7	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	155	211	Aug 2020	-	2025-06-01	141162
Mercedes-benz	Cla	CLA 250 E	Kombi	Frontantrieb	Benzin/Elektro	160	218	Jun 2020	-	2024-03-01	141183
Mercedes-benz	Eqv	EQV 300	Bus	Frontantrieb	Elektro	150	204	Jun 2020	-	2024-03-01	141189
Mercedes-benz	Marco polo camper	170 CDI	Bus	Frontantrieb	Diesel	75	102	Jun 2020	-	2024-03-01	141206
Mercedes-benz	Marco polo camper	200 CDI	Bus	Frontantrieb	Diesel	100	136	Jun 2020	-	2024-03-01	141212
Ford USA	Mustang	5.2 Shelby Gt500	Coupe	Heckantrieb	Benzin	567	771	Sep 2019	Apr 2023	2024-05-01	141216
BMW	X3	IX3	SUV	Heckantrieb	Elektro	210	286	Sep 2020	-	2024-11-01	141225
BMW	Ix3	Electric	SUV	Heckantrieb	Elektro	80	109	Sep 2020	-	2025-04-01	141226
Hyundai	I30	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Jun 2020	-	2025-04-01	141227
Mercedes-benz	Sprinter 3,5-T	311 CDI RWD	Kasten	Heckantrieb	Diesel	84	114	Jun 2020	-	2024-03-01	141254
Toyota	Corolla	1.8 Vvti Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	90	122	Feb 2019	-	2025-06-01	141256
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	53	72	Feb 2020	-	2024-03-01	141257
Mercedes-benz	Sprinter 3,5-T	311 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Jun 2020	-	2024-03-01	141259
Citroën	C4 iii	Ë-c4	Schrägheck	Frontantrieb	Elektro	100	136	Oct 2020	-	2024-05-01	141260
Mercedes-benz	Sprinter 3-T	211 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Jun 2020	-	2024-03-01	141261
Mercedes-benz	Sprinter 3,5-T	315 CDI RWD	Kasten	Heckantrieb	Diesel	110	150	Jun 2020	-	2024-03-01	141267
Mercedes-benz	Sprinter 3,5-T	315 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2020	-	2024-03-01	141268
Mercedes-benz	Sprinter 3-T	215 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2020	-	2024-03-01	141269
Mercedes-benz	Sprinter 3,5-T	317 CDI RWD	Kasten	Heckantrieb	Diesel	125	170	Jun 2020	-	2024-03-01	141271
Mercedes-benz	Sprinter 3,5-T	317 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	125	170	Jun 2020	-	2024-03-01	141272
Mercedes-benz	Sprinter 3-T	217 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	125	170	Jun 2020	-	2024-03-01	141273
Mercedes-benz	Sprinter 4-T	417 CDI RWD	Kasten	Heckantrieb	Diesel	125	170	Jun 2020	-	2024-03-01	141274
Maserati	Ghibli	Mhev	Stufenheck	Heckantrieb	Benzin/Elektro	243	330	Jul 2020	-	2024-03-01	141285
Audi	80	2	Stufenheck	Frontantrieb	Benzin	81	110	Oct 1983	Sep 1984	2024-03-01	141297
Mercedes-benz	Vito mixto	114 CDI 4-matic	Kasten	Allrad	Diesel	100	136	Mar 2019	-	2024-03-01	141298
Toyota	Land cruiser prado	2.8 D-4d	Geländewagen geschlossen	Allrad	Diesel	150	204	Jul 2020	-	2024-03-01	141303
Hyundai	Tucson	2.0 Cvvt Allrad	SUV	Allrad	Benzin	110	150	Jun 2015	Sep 2020	2024-03-01	141304
Lada	Niva ii	1.7 4X4	Geländewagen geschlossen	Allrad	Benzin	59	80	Jul 2020	Feb 2021	2024-03-01	141321
KIA	Rio iv	1.25 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	82	May 2019	-	2025-11-01	141324
KIA	Sportage iv	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	93	126	Jul 2020	Sep 2022	2024-03-01	141325
KIA	Xceed	1.6 T-gdi	SUV	Frontantrieb	Benzin	147	200	Sep 2019	-	2025-04-01	141348
KIA	Soul iii cargo	E-soul	Kasten/Schrägheck	Frontantrieb	Elektro	100	136	Jun 2020	-	2024-03-01	141349
KIA	Rio iv	1.0 T-gdi 120 Eco-dynamics+	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Aug 2020	Apr 2023	2025-11-01	141350
Renault	Symbol/logan iii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	70	95	Nov 2019	-	2024-03-01	141356
Peugeot	Expert	E-expert	Kasten	Frontantrieb	Elektro	100	136	Sep 2020	-	2024-03-01	141357
Peugeot	Traveller	E-traveller	Bus	Frontantrieb	Elektro	100	136	Sep 2020	Oct 2023	2024-07-01	141358
Ford	Tourneo custom v362	1.0 Ecoboost Phev	Bus	Frontantrieb	Benzin/Elektro	92	125	Apr 2020	Dec 2023	2024-05-01	141359
Ford	Transit custom v362	1.0 Ecoboost Phev	Bus	Frontantrieb	Benzin/Elektro	92	125	Apr 2020	Dec 2023	2024-05-01	141360
Mercedes-benz	Gla	GLA 250 E	SUV	Frontantrieb	Benzin/Elektro	160	218	Jun 2020	-	2024-03-01	141371
Mercedes-benz	Gla	GLA 180	SUV	Frontantrieb	Benzin	100	136	Jul 2020	-	2024-03-01	141373
Mercedes-benz	E-Klasse	E 400 D 4-matic	Stufenheck	Allrad	Diesel	243	330	Jun 2020	Oct 2023	2024-03-01	141374
KIA	Ceed	GDI Hybrid	Kasten/Kombi	Frontantrieb	Benzin/Elektro	104	141	Dec 2019	-	2024-03-01	141383
KIA	Proceed	1.4 T-gdi	Kasten/Kombi	Frontantrieb	Benzin	103	140	Oct 2018	Dec 2020	2024-08-01	141384
KIA	Proceed	1.6 Crdi 136	Kasten/Kombi	Frontantrieb	Diesel	100	136	Oct 2018	-	2024-03-01	141386
Audi	Q7	SQ7 Quattro	SUV	Allrad	Benzin	373	507	Feb 2020	-	2024-03-01	141387
Peugeot	Traveller	2.0 Bluehdi 145	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2025-12-01	141389
KIA	Proceed	1.6 T-gdi GT	Kasten/Kombi	Frontantrieb	Benzin	150	204	Oct 2018	-	2024-03-01	141390
Mercedes-benz	Cls	CLS 400 D 4-matic	Coupe	Allrad	Diesel	243	330	Jun 2020	-	2024-03-01	141391
Mercedes-benz	E-Klasse	E 400 D 4-matic	Coupe	Allrad	Diesel	243	330	Jul 2020	-	2024-03-01	141392
Mercedes-benz	E-Klasse	E 400 D 4-matic	Cabriolet	Allrad	Diesel	243	330	Jul 2020	-	2024-03-01	141393
KIA	Xceed	1.4 T-gdi	Kasten/SUV	Frontantrieb	Benzin	103	140	Jun 2019	Dec 2020	2024-08-01	141394
KIA	Xceed	1.6 Crdi	Kasten/SUV	Frontantrieb	Diesel	100	136	Jun 2019	-	2024-03-01	141395
Mercedes-benz	E-Klasse	E 450 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	270	367	Jul 2020	-	2024-03-01	141396
KIA	Xceed	1.6 T-gdi	Kasten/SUV	Frontantrieb	Benzin	150	204	Jun 2019	-	2024-03-01	141397
Mercedes-benz	E-Klasse	E 450 EQ Boost 4-matic	Cabriolet	Allrad	Benzin/Elektro	270	367	Jul 2020	-	2024-03-01	141399
KIA	Xceed	1.6 GDI Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	104	141	Dec 2019	-	2024-03-01	141400
KIA	Sportage iv van	1.6 T-gdi	Kasten/SUV	Frontantrieb	Benzin	130	177	May 2018	-	2024-03-01	141401
KIA	Sportage iv van	1.6 Crdi Eco-dynamics+	Kasten/SUV	Frontantrieb	Diesel/Elektro	100	136	Mar 2019	-	2024-03-01	141403
KIA	Sportage iv van	1.6 Crdi Eco-dynamics+ Allrad	Kasten/SUV	Allrad	Diesel/Elektro	100	136	Mar 2019	-	2024-03-01	141404
KIA	Stinger	3.3 T-gdi 4WD	Kasten/Schrägheck	Allrad	Benzin	269	366	Jul 2018	Dec 2023	2026-04-01	141406
Mercedes-benz	Amg gt roadster	GT	Cabriolet	Heckantrieb	Benzin	390	530	Jul 2020	Dec 2021	2024-03-01	141411
Mercedes-benz	Amg gt	GT	Coupe	Heckantrieb	Benzin	390	530	Jul 2020	Dec 2021	2024-03-01	141412
VW	Arteon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Sep 2020	-	2024-03-01	141422
VW	Arteon	2.0 TDI	Kombi	Frontantrieb	Diesel	140	190	Sep 2020	-	2024-03-01	141423
VW	Arteon	2.0 TDI 4motion	Kombi	Allrad	Diesel	140	190	Sep 2020	-	2024-03-01	141424
VW	Arteon	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Aug 2020	-	2024-03-01	141426
VW	Arteon	2.0 TSI 4motion	Kombi	Allrad	Benzin	200	272	Jun 2020	-	2024-03-01	141428
Land Rover	88/109 mk i	2.0 4X4	Geländewagen geschlossen	Allrad	Benzin	39	53	Jul 1956	Aug 1958	2024-03-01	141430
Land Rover	88/109 mk i	2.0 D 4X4	Geländewagen geschlossen	Allrad	Diesel	39	53	Jan 1957	Aug 1958	2024-03-01	141431
Land Rover	88/109 mk ii	2.0 D 4X4	Geländewagen geschlossen	Allrad	Diesel	39	53	Sep 1958	Nov 1961	2024-03-01	141432


--- Round 1 / 首次发送 ---
## 更新点

* 按物理车身聚类复用跨批次缓存，完成 60 个 Ktype 的映射。
* BMW 7 系含 `D/LD` 的 Ktype 已拆分为 SWB、LWB 两个物理分支。
* Peugeot Expert、Traveller 和 Ford Tourneo Custom 已按车身长度拆分。
* 本轮共新增 68 条 READY 映射，引用 36 个既有尺寸组；未重复输出尺寸组事实。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：60
* READY 映射行：68
* PENDING Ktype：40
* 已引用尺寸组：36
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141093	141093	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI sedan.	READY
141094	141094	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI sedan.	READY
141097	141097	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141102	141102	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141103	141103	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141104	141104	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141105	141105	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141106	141106	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141107	141107	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141108	141108	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141109	141109	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141133_swb	141133	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	730 D standard-wheelbase branch.	READY
141133_lwb	141133	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	730 LD long-wheelbase branch.	READY
141134	141134	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	G11 LCI standard-wheelbase sedan.	READY
141135_swb	141135	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	730 D/LD xDrive standard-wheelbase branch.	READY
141135_lwb	141135	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	730 D/LD xDrive long-wheelbase branch.	READY
141138_swb	141138	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	740 D/LD xDrive standard-wheelbase branch.	READY
141138_lwb	141138	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	740 D/LD xDrive long-wheelbase branch.	READY
141142	141142	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141143	141143	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141144	141144	SUV	X3 G01	G01	5	EU-BMW-X3-G01-M40I-SUV-01	MEDIUM	G01 M40 exterior-envelope branch.	READY
141145	141145	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141146	141146	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141147	141147	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH	G02 standard-body SUV.	READY
141148	141148	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH	G02 standard-body SUV.	READY
141149	141149	SUV	X4 G02	G02	5	EU-BMW-X4-G02-M40D-SUV-01	HIGH	G02 M40d exterior branch.	READY
141150	141150	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05 pre-facelift SUV.	READY
141151	141151	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05 pre-facelift SUV.	READY
141152	141152	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141153	141153	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141154	141154	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141161	141161	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	G07 pre-facelift SUV.	READY
141162	141162	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	G07 pre-facelift SUV.	READY
141183	141183	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH	X118 Shooting Brake.	READY
141227	141227	Hatchback	i30 III PD	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD five-door hatchback.	READY
141256	141256	Sedan	Corolla XII E210	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH	E210 sedan.	READY
141257	141257	Hatchback	Yaris IV XP210	XP210	5	EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	HIGH	XP210 five-door hatchback.	READY
141285	141285	Sedan	Ghibli III M157 facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157 facelift sedan.	READY
141303	141303	SUV	Land Cruiser Prado J150 facelift	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	HIGH	J150 facelift five-door SUV.	READY
141304	141304	SUV	Tucson III TL	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH	TL five-door SUV.	READY
141324	141324	Hatchback	Rio IV YB	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	YB five-door hatchback.	READY
141325	141325	SUV	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL five-door SUV.	READY
141348	141348	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141350	141350	Hatchback	Rio IV YB	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	YB five-door hatchback.	READY
141357_compact	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact body-length branch.	READY
141357_standard	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard body-length branch.	READY
141357_long	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long body-length branch.	READY
141358_compact	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact body-length branch.	READY
141358_standard	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard body-length branch.	READY
141358_long	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long body-length branch.	READY
141359_l1	141359	MPV	Tourneo Custom V362	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1 body-length branch.	READY
141359_l2	141359	MPV	Tourneo Custom V362	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2 body-length branch.	READY
141371	141371	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 pre-facelift SUV.	READY
141373	141373	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 pre-facelift SUV.	READY
141374	141374	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	W213 facelift sedan.	READY
141384	141384	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141386	141386	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141387	141387	SUV	Q7 II 4M facelift	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M facelift SUV.	READY
141390	141390	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141391	141391	Coupe	CLS III C257	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257 four-door coupe.	READY
141394	141394	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141395	141395	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141397	141397	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141400	141400	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141401	141401	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141403	141403	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141404	141404	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141406	141406	Liftback	Stinger I CK	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	CK five-door liftback.	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无（本轮全部复用跨批次已有尺寸组）。

## 下一步优先处理

1. 集中闭合 Mercedes-Benz Sprinter Kasten 与 Pritsche/Fahrgestell 的轴距、车长和车顶分支：`141254`、`141259`、`141261`、`141267`、`141268`、`141269`、`141271`、`141272`、`141273`、`141274`。
2. 闭合 Mercedes-Benz EQV、Marco Polo、Vito Mixto 和 Transit Custom Bus 的长度、车顶分支。
3. 创建 GR Yaris、BMW iX3、Citroën ë-C4、Arteon Shooting Brake、AMG GT、Land Rover Series I/II 等尚未进入缓存的尺寸组。
4. 核对 E-Class Coupe/Cabriolet facelift、Peugeot Traveller 145、Ceed SW PHEV 等可能存在版本尺寸差异的映射。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 19 个 Ktype，其中 GR Yaris、Shelby GT500、BMW iX3、Citroën ë-C4、Kia e-Soul、AMG GT Coupé 和 Arteon Shooting Brake 首次建立尺寸组。
* Ford 官方技术规格确认 Shelby GT500 标准车身为 4813 × 1946 × 1379 mm；碳纤维赛道套件高度不同，但当前 Ktype 未指向该套件，未创建猜测性分支。([福特媒体][1])
* Transit Custom PHEV Bus 官方配置仅为 L1H1，直接关联既有 `BUS-L1H1` 组。([福特英国][2])
* GR Yaris、iX3、ë-C4、e-Soul 和 Arteon Shooting Brake 的三维已按官方资料闭合。([丰田欧盟新闻中心][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射行：87
* PENDING Ktype：21
* 已确认尺寸组：48
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141131	141131	Hatchback	Yaris IV XP210 (GR Yaris)	GXPA16	3	EU-TOYOTA-YARIS-IV-XP210-GR-HATCHBACK-3D-01	HIGH	GR Yaris三门宽体外廓。	READY
141216	141216	Coupe	Mustang VI S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-SHELBY-GT500-COUPE-01	HIGH	Shelby GT500标准车身；不含Carbon Fiber Track Package分支。	READY
141225	141225	SUV	iX3 G08	G08	5	EU-BMW-IX3-G08-SUV-01	HIGH	G08纯电SUV外廓。	READY
141226	141226	SUV	iX3 G08	G08	5	EU-BMW-IX3-G08-SUV-01	HIGH	G08纯电SUV外廓。	READY
141260	141260	Hatchback	C4 III C41	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41五门掀背外廓。	READY
141349	141349	Van	Soul III SK3	SK3	5	EU-KIA-SOUL-III-SK3-EV-HATCHBACK-01	HIGH	货运登记版本复用e-Soul五门物理外廓。	READY
141360	141360	MPV	Transit Custom V362 facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	PHEV Bus仅有L1H1车身分支。	READY
141383	141383	Wagon	Ceed III CD	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	货运登记的Ceed Sportswagon PHEV外廓。	READY
141392	141392	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑。	READY
141393	141393	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷。	READY
141396	141396	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑。	READY
141399	141399	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷。	READY
141411	141411	Convertible	AMG GT I R190 facelift	R190	2	EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	MEDIUM	标准宽度R190 GT Roadster外廓。	READY
141412	141412	Coupe	AMG GT I C190 facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-C190-GT-COUPE-01	HIGH	标准宽度C190 GT Coupé外廓。	READY
141422	141422	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141423	141423	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141424	141424	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141426	141426	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141428	141428	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-YARIS-IV-XP210-GR-HATCHBACK-3D-01	3995	1805	1455	Toyota Europe GR Yaris official press kit	https://newsroom.toyota.eu/gr-yaris-born-from-the-world-rally-championship/
EU-FORD-USA-MUSTANG-S550-SHELBY-GT500-COUPE-01	4813	1946	1379	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-BMW-IX3-G08-SUV-01	4734	1891	1668	BMW Group Press iX3 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0314265EN/457881
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Citroën New C4 and ë-C4 official press release	https://www.media.stellantis.com/uk-en/citroen/press/new-c4-and-new-e-c4-100-electric-citroen-reinvents-the-compact-hatchback
EU-KIA-SOUL-III-SK3-EV-HATCHBACK-01	4195	1800	1605	Kia e-Soul official specifications	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/spechsheet/e-Soul-Specifications.pdf
EU-MERCEDES-BENZ-AMG-GT-C190-GT-COUPE-01	4544	1939	1287	Automobile-Catalog 2020 Mercedes-AMG GT specifications	https://www.automobile-catalog.com/car/2020/2874830/mercedes-amg_gt.html
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	4866	1871	1462	Volkswagen Newsroom Arteon Shooting Brake technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
```

## 下一步优先处理

1. 批量闭合 10 个 Sprinter Kasten、Pritsche/Fahrgestell Ktype 的轴距、车长和车顶分支。
2. 处理 EQV、Marco Polo Camper 与 Vito Mixto 的 Long/Extra-long 和露营车车顶边界。
3. 处理 Peugeot Traveller BlueHDi 145、Audi 80 B2、Lada Niva II、Renault Symbol/Logan III。
4. 最后集中处理 Land Rover Series I/II 的 88/109 英寸轴距派生分支。

推进信号：CONTINUE

[1]: https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf?utm_source=chatgpt.com "2020 FORD MUSTANG"
[2]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-transit-custom-PHEV.pdf "Transit Custom PHEV Effective 24th February 2020 Customer version.xlsx"
[3]: https://newsroom.toyota.eu/gr-yaris-born-from-the-world-rally-championship/?utm_source=chatgpt.com "GR Yaris: Born from the World Rally Championship"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Lada Niva II 与 Renault Symbol III 两个尺寸组；官方资料分别确认其标准外廓和不含后视镜宽度。
* Peugeot Traveller BlueHDi 145 确认同时覆盖 Standard 与 Long 车长，拆成两个派生映射并复用已有尺寸组，不重复输出尺寸事实。([标致][1])
* 本轮新增 3 个 READY Ktype、4 条 READY 映射及2个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射行：91
* PENDING Ktype：18
* 已确认尺寸组：50
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141321	141321	SUV	Niva II		5	EU-LADA-NIVA-II-SUV-01	HIGH	五门SUV外廓。	READY
141356	141356	Sedan	Symbol III facelift		4	EU-RENAULT-SYMBOL-III-SEDAN-FACELIFT-01	HIGH	四门轿车外廓。	READY
141389_standard	141389	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
141389_long	141389	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long车长分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-NIVA-II-SUV-01	4056	1800	1690	LADA Niva official owner manual	https://static.lada.ru/vaz/files/exp_manual/lada_niva_re_01_07_2020.pdf
EU-RENAULT-SYMBOL-III-SEDAN-FACELIFT-01	4354	1733	1517	Renault Symbol November 2019 official brochure	https://cdn.group.renault.com/ren/tr/brochures/symbol-l46/tr-renault-symbol-112019.pdf
```

## 下一步优先处理

1. 集中闭合 10 个 Sprinter Kasten、Pritsche/Fahrgestell Ktype 的轴距、车长和车顶分支。
2. 处理 EQV、Marco Polo Camper、Vito Mixto 四个 W447 系列 Ktype。
3. 最后处理 Audi 80 B2 与三个 Land Rover Series I/II 历史车型分支。

推进信号：CONTINUE

[1]: https://www.peugeot.fr/content/dam/peugeot/france/b2c/documentation/tarifs/Traveller_21C.pdf "Copie de Fichier_Fusionne_Traveller_21C_V2.0.xlsm"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz EQV 300 的 Long、Extra Long 两个车长分支，以及 Marco Polo Activity 170 d/200 d 的共同物理外廓。([汽车数据网][1])
* 闭合 Sprinter W907 Kasten 的 L2H1、L2H2、L3H2、L4H2 四个后驱尺寸组，并按官方车型供应范围拆分 311、315、317、417 CDI 映射。([Kinahan][2])
* Audi 80 B2 的二门、四门边界已拆分；两种车身外廓三维相同，共用一个尺寸组。([汽车目录][3])
* 本轮新增 8 个 READY Ktype、15 条 READY 映射和 8 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：106
* PENDING Ktype：10
* 已确认尺寸组：58
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141189_long	141189	MPV	EQV V447	V447	5	EU-MERCEDES-BENZ-EQV-V447-MPV-LONG-01	HIGH	Long车身分支。	READY
141189_extra_long	141189	MPV	EQV V447	V447	5	EU-MERCEDES-BENZ-EQV-V447-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
141206	141206	MPV	Marco Polo Activity W447	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	HIGH	Marco Polo Activity弹出式车顶外廓。	READY
141212	141212	MPV	Marco Polo Activity W447	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	HIGH	Marco Polo Activity弹出式车顶外廓。	READY
141254_l2h1	141254	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H1-RWD-01	HIGH	L2H1车身分支。	READY
141254_l2h2	141254	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141267_l2h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141267_l3h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身分支。	READY
141267_l4h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	HIGH	L4H2车身分支。	READY
141271_l2h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141271_l3h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身分支。	READY
141271_l4h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	HIGH	L4H2车身分支。	READY
141274	141274	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身外廓。	READY
141297_2dr	141297	Sedan	Audi 80 B2	Typ 81	2	EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	MEDIUM	双门车身分支。	READY
141297_4dr	141297	Sedan	Audi 80 B2	Typ 81	4	EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	MEDIUM	四门车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQV-V447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz EQV official brochure	https://i.i-sgcm.com/new_cars/cars/21620/brochures/brochure_20221011015941.pdf
EU-MERCEDES-BENZ-EQV-V447-MPV-EXTRA-LONG-01	5370	1928	1901	Auto-Data Mercedes-Benz EQV model specifications	https://www.auto-data.net/en/mercedes-benz-eqv-model-2839
EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo August 2019 official price list	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_marco_polo_series_2019_g.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H1-RWD-01	5932	2020	2361	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	5932	2020	2650	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	6967	2020	2646	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	7367	2020	2643	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	4383	1682	1365	Automobile-Catalog 1983 Audi 80 2.0 CD specifications	https://www.automobile-catalog.com/car/1983/230375/audi_80_2_0_cd.html
```

## 下一步优先处理

1. 闭合 6 个 Sprinter Pritsche/Fahrgestell Ktype 的后驱轴距与驾驶室底盘长度分支。
2. 闭合 Vito Mixto 114 CDI 4MATIC 的 Compact、Long、Extra Long 供应边界。
3. 处理 Land Rover Series I/II 的 88、109 英寸轴距硬顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-eqv-model-2839 "https://www.auto-data.net/en/mercedes-benz-eqv-model-2839"
[2]: https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf "https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf"
[3]: https://www.automobile-catalog.com/car/1983/230375/audi_80_2_0_cd.html "https://www.automobile-catalog.com/car/1983/230375/audi_80_2_0_cd.html"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 `141298` Mercedes-Benz Vito Mixto 114 CDI 4MATIC。该 Ktype 覆盖 `447.701`、`447.703`、`447.705` 三个车身代码，分别拆为 Compact、Long、Extra Long；官方 Vito 资料确认对应长度为 4895、5140、5370 mm，车身宽度均为 1928 mm、高度均为 1910 mm。([AUTODOC][1])
* Sprinter 底盘车现有资料尚未完整闭合短轴及双排驾驶室的同配置三维，本轮未创建推测性尺寸组。([Scribd][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：109
* PENDING Ktype：9
* 已确认尺寸组：61
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141298_compact	141298	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-MIXTO-COMPACT-01	HIGH	Compact车长分支。	READY
141298_long	141298	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-MIXTO-LONG-01	HIGH	Long车长分支。	READY
141298_extra_long	141298	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-MIXTO-EXTRA-LONG-01	HIGH	Extra Long车长分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W447-MIXTO-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-MIXTO-LONG-01	5140	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-MIXTO-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
```

## 下一步优先处理

1. 闭合 6 个 Sprinter Pritsche/Fahrgestell Ktype 的单排、双排驾驶室及 3250/3665/4325 mm 轴距分支。
2. 闭合 Land Rover Series I/II 的 88、109 英寸硬顶车身分支，解决不同资料间的高度口径冲突。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/brake-pad-set-10130/mercedes-benz/vito/vito-mixto-w447/141298-114-cdi-4-matic-447-701-447-703-447-705?utm_source=chatgpt.com "Mercedes Vito Mixto W447 114 CDI 4-matic Brake pads - 136 hp Diesel 100 kW 2019 - 2026 OM 654.920 ▷ AUTODOC"
[2]: https://www.scribd.com/document/812415290/ARL-Sprinter-BR-907-NA2018-2a-20180207-sv?utm_source=chatgpt.com "ARL Sprinter BR 907 NA2018-2a 20180207 SV | PDF"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Land Rover Series I、Series II 的 88 英寸与 109 英寸封闭车身分支，3 个 Ktype 均拆为 SWB/LWB 两行。
* Series I 官方规格表确认 88 英寸车身为 140 × 62 × 76 英寸，109 英寸车身为 173.5 × 62 × 78 英寸；Series II 官方规格分别确认 88 英寸为 142⅜ × 64 × 77½ 英寸、109 英寸为 175 × 64 × 81 英寸。按统一规则换算并取整。([汽车手册][1])
* 本轮新增 6 条 READY 映射和 4 个尺寸组；当前仅剩 6 个 Sprinter 底盘车 Ktype 待闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射行：115
* PENDING Ktype：6
* 已确认尺寸组：65
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141430_88	141430	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141430_109	141430	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
141431_88	141431	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141431_109	141431	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
141432_88	141432	SUV	Series II			EU-LAND-ROVER-SERIES-II-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141432_109	141432	SUV	Series II			EU-LAND-ROVER-SERIES-II-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-SERIES-I-SUV-88-01	3556	1575	1930	Rover Company Land-Rover 1957 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-I-SUV-109-01	4407	1575	1981	Rover Company Land-Rover 1957 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-II-SUV-88-01	3616	1626	1969	Rover Company Land-Rover Series II 1958 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1958.pdf
EU-LAND-ROVER-SERIES-II-SUV-109-01	4445	1626	2057	Rover Company Land-Rover Series II 109 Pick-Up 1958 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Series-II-Pick-Up-1958-UK.pdf
```

## 下一步优先处理

1. 一次性闭合 `141259`、`141261`、`141268`、`141269`、`141272`、`141273` 的 Sprinter W907 单排驾驶室底盘分支。
2. 按 `907.12x/907.13x/907.22x/907.23x` 车身代码确认可供应轴距，消除 3 吨与 3.5 吨版本的高度冲突。
3. PENDING 清零后立即组装两张最终完整 TSV，并创建两个指定文件。

推进信号：CONTINUE

[1]: https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf?utm_source=chatgpt.com "UNES"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后 6 个 Ktype 的车身代码边界已确认：

  * `141259`、`141268`、`141272` 覆盖 `907.131/133/135` 单排驾驶室及 `907.231/233/235` 双排驾驶室。
  * `141261` 覆盖 `907.123/221/223`。
  * `141269`、`141273` 覆盖 `907.221/223`。([AUTODOC][1])
* 官方 2022 资料已闭合单排 L2 `5886×2020×2318`、单排 L3 `6695×2020×2311`、双排 L3 `6695×2020×2301`；图纸中的 `2020 mm` 为不含后视镜车身宽度。
* 3250 mm 轴距和双排 L2 的资料仍有外廓口径冲突：部分数据库记录的是裸底盘，部分记录包含原厂平台，长度、宽度和高度不能混为同一尺寸组。([汽车侦察24][2])
* 为避免只闭合部分派生分支后产生不完整 Ktype 或孤立尺寸组，本轮暂不落盘上述已确认的局部分支。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射行：115
* PENDING Ktype：6
* 已确认尺寸组：65
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 只核对 `907.131/231` 的 3250 mm 轴距裸底盘三维。
2. 只核对 `907.223/233` 双排驾驶室 L2 的裸底盘高度，排除带平台宽度和长度。
3. 两个缺口闭合后，一次性输出 6 个 Ktype 的全部派生映射；若届时 `PENDING=0`，同轮直接生成两张最终完整 TSV 和指定下载文件。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/brake-disc-back-plate-15099/mercedes-benz/sprinter/sprinter-3-5-t-platform-chassis-907-910/141259-311-cdi-rwd-907-131-907-133-907-135-907-231-907-233 "Brake disc backing plate for Sprinter 907 910 311 CDI RWD 114 hp Diesel 2020 - 2026 OM 654.920 | AUTODOC"
[2]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-cab-317-cdi-32-3-5t-rwd-autres-diesel-7014/?srsltid=AfmBOopuFaTXyrMe3V_gH52FTZnGYSXn--tAYD3XWA46f5AUh369YZb4&utm_source=chatgpt.com "Mercedes-Benz SPRINTER CHASSIS CAB 317 CDI 32 3.5 ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 最后 6 个 Sprinter 底盘车 Ktype 已按单排/双排驾驶室及 L1/L2/L3 物理分支闭合。Mercedes-Benz 规格资料支持 L2、L3 单排及 L3 双排尺寸，具体配置页补齐 L1 和 L2 双排边界。([梅赛德斯-奔驰卡车服务与销售][1])
* 新增 26 条 Sprinter 派生映射和 6 个尺寸组。
* 已完成机械检查：映射表严格 10 列、尺寸组表严格 6 列，`id` 和 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，无孤立尺寸组或空缺来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：140
* PENDING Ktype：0
* DIMENSION_GROUP：71
* 所有映射均为 `READY`。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141093	141093	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI sedan.	READY
141094	141094	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI sedan.	READY
141097	141097	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141102	141102	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141103	141103	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141104	141104	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141105	141105	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141106	141106	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141107	141107	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 four-door coupe.	READY
141108	141108	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141109	141109	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI wagon.	READY
141131	141131	Hatchback	Yaris IV XP210 (GR Yaris)	GXPA16	3	EU-TOYOTA-YARIS-IV-XP210-GR-HATCHBACK-3D-01	HIGH	GR Yaris三门宽体外廓。	READY
141133_swb	141133	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	730 D standard-wheelbase branch.	READY
141133_lwb	141133	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	730 LD long-wheelbase branch.	READY
141134	141134	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	G11 LCI standard-wheelbase sedan.	READY
141135_swb	141135	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	730 D/LD xDrive standard-wheelbase branch.	READY
141135_lwb	141135	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	730 D/LD xDrive long-wheelbase branch.	READY
141138_swb	141138	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	740 D/LD xDrive standard-wheelbase branch.	READY
141138_lwb	141138	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	740 D/LD xDrive long-wheelbase branch.	READY
141142	141142	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141143	141143	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141144	141144	SUV	X3 G01	G01	5	EU-BMW-X3-G01-M40I-SUV-01	MEDIUM	G01 M40 exterior-envelope branch.	READY
141145	141145	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141146	141146	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 standard-body SUV.	READY
141147	141147	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH	G02 standard-body SUV.	READY
141148	141148	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH	G02 standard-body SUV.	READY
141149	141149	SUV	X4 G02	G02	5	EU-BMW-X4-G02-M40D-SUV-01	HIGH	G02 M40d exterior branch.	READY
141150	141150	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05 pre-facelift SUV.	READY
141151	141151	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05 pre-facelift SUV.	READY
141152	141152	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141153	141153	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141154	141154	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06 pre-facelift SUV.	READY
141161	141161	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	G07 pre-facelift SUV.	READY
141162	141162	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	G07 pre-facelift SUV.	READY
141183	141183	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH	X118 Shooting Brake.	READY
141189_long	141189	MPV	EQV V447	V447	5	EU-MERCEDES-BENZ-EQV-V447-MPV-LONG-01	HIGH	Long车身分支。	READY
141189_extra_long	141189	MPV	EQV V447	V447	5	EU-MERCEDES-BENZ-EQV-V447-MPV-EXTRA-LONG-01	HIGH	Extra Long车身分支。	READY
141206	141206	MPV	Marco Polo Activity W447	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	HIGH	Marco Polo Activity弹出式车顶外廓。	READY
141212	141212	MPV	Marco Polo Activity W447	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	HIGH	Marco Polo Activity弹出式车顶外廓。	READY
141216	141216	Coupe	Mustang VI S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-SHELBY-GT500-COUPE-01	HIGH	Shelby GT500标准车身；不含Carbon Fiber Track Package分支。	READY
141225	141225	SUV	iX3 G08	G08	5	EU-BMW-IX3-G08-SUV-01	HIGH	G08纯电SUV外廓。	READY
141226	141226	SUV	iX3 G08	G08	5	EU-BMW-IX3-G08-SUV-01	HIGH	G08纯电SUV外廓。	READY
141227	141227	Hatchback	i30 III PD	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD five-door hatchback.	READY
141254_l2h1	141254	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H1-RWD-01	HIGH	L2H1车身分支。	READY
141254_l2h2	141254	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141256	141256	Sedan	Corolla XII E210	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH	E210 sedan.	READY
141257	141257	Hatchback	Yaris IV XP210	XP210	5	EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	HIGH	XP210 five-door hatchback.	READY
141259_single_l1	141259	Pickup	Sprinter III W907	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-RWD-01	HIGH	单排驾驶室L1底盘分支。	READY
141259_single_l2	141259	Pickup	Sprinter III W907	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-RWD-01	HIGH	单排驾驶室L2底盘分支。	READY
141259_single_l3	141259	Pickup	Sprinter III W907	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-RWD-01	HIGH	单排驾驶室L3底盘分支。	READY
141259_crew_l1	141259	Pickup	Sprinter III W907	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141259_crew_l2	141259	Pickup	Sprinter III W907	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141259_crew_l3	141259	Pickup	Sprinter III W907	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L3-RWD-01	HIGH	双排驾驶室L3底盘分支。	READY
141260	141260	Hatchback	C4 III C41	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41五门掀背外廓。	READY
141261_single_l2	141261	Pickup	Sprinter III W907	907.123	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-RWD-01	HIGH	单排驾驶室L2底盘分支。	READY
141261_crew_l1	141261	Pickup	Sprinter III W907	907.221	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141261_crew_l2	141261	Pickup	Sprinter III W907	907.223	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141267_l2h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141267_l3h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身分支。	READY
141267_l4h2	141267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	HIGH	L4H2车身分支。	READY
141268_single_l1	141268	Pickup	Sprinter III W907	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-RWD-01	HIGH	单排驾驶室L1底盘分支。	READY
141268_single_l2	141268	Pickup	Sprinter III W907	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-RWD-01	HIGH	单排驾驶室L2底盘分支。	READY
141268_single_l3	141268	Pickup	Sprinter III W907	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-RWD-01	HIGH	单排驾驶室L3底盘分支。	READY
141268_crew_l1	141268	Pickup	Sprinter III W907	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141268_crew_l2	141268	Pickup	Sprinter III W907	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141268_crew_l3	141268	Pickup	Sprinter III W907	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L3-RWD-01	HIGH	双排驾驶室L3底盘分支。	READY
141269_crew_l1	141269	Pickup	Sprinter III W907	907.221	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141269_crew_l2	141269	Pickup	Sprinter III W907	907.223	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141271_l2h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	HIGH	L2H2车身分支。	READY
141271_l3h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身分支。	READY
141271_l4h2	141271	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	HIGH	L4H2车身分支。	READY
141272_single_l1	141272	Pickup	Sprinter III W907	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-RWD-01	HIGH	单排驾驶室L1底盘分支。	READY
141272_single_l2	141272	Pickup	Sprinter III W907	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-RWD-01	HIGH	单排驾驶室L2底盘分支。	READY
141272_single_l3	141272	Pickup	Sprinter III W907	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-RWD-01	HIGH	单排驾驶室L3底盘分支。	READY
141272_crew_l1	141272	Pickup	Sprinter III W907	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141272_crew_l2	141272	Pickup	Sprinter III W907	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141272_crew_l3	141272	Pickup	Sprinter III W907	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L3-RWD-01	HIGH	双排驾驶室L3底盘分支。	READY
141273_crew_l1	141273	Pickup	Sprinter III W907	907.221	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	HIGH	双排驾驶室L1底盘分支。	READY
141273_crew_l2	141273	Pickup	Sprinter III W907	907.223	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	HIGH	双排驾驶室L2底盘分支。	READY
141274	141274	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	HIGH	L3H2车身外廓。	READY
141285	141285	Sedan	Ghibli III M157 facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157 facelift sedan.	READY
141297_2dr	141297	Sedan	Audi 80 B2	Typ 81	2	EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	MEDIUM	双门车身分支。	READY
141297_4dr	141297	Sedan	Audi 80 B2	Typ 81	4	EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	MEDIUM	四门车身分支。	READY
141298_compact	141298	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-MIXTO-COMPACT-01	HIGH	Compact车长分支。	READY
141298_long	141298	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-MIXTO-LONG-01	HIGH	Long车长分支。	READY
141298_extra_long	141298	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-MIXTO-EXTRA-LONG-01	HIGH	Extra Long车长分支。	READY
141303	141303	SUV	Land Cruiser Prado J150 facelift	J150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	HIGH	J150 facelift five-door SUV.	READY
141304	141304	SUV	Tucson III TL	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH	TL five-door SUV.	READY
141321	141321	SUV	Niva II		5	EU-LADA-NIVA-II-SUV-01	HIGH	五门SUV外廓。	READY
141324	141324	Hatchback	Rio IV YB	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	YB five-door hatchback.	READY
141325	141325	SUV	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL five-door SUV.	READY
141348	141348	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141349	141349	Van	Soul III SK3	SK3	5	EU-KIA-SOUL-III-SK3-EV-HATCHBACK-01	HIGH	货运登记版本复用e-Soul五门物理外廓。	READY
141350	141350	Hatchback	Rio IV YB	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	YB five-door hatchback.	READY
141356	141356	Sedan	Symbol III facelift		4	EU-RENAULT-SYMBOL-III-SEDAN-FACELIFT-01	HIGH	四门轿车外廓。	READY
141357_compact	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact body-length branch.	READY
141357_standard	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard body-length branch.	READY
141357_long	141357	Van	Expert III K0	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long body-length branch.	READY
141358_compact	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact body-length branch.	READY
141358_standard	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard body-length branch.	READY
141358_long	141358	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long body-length branch.	READY
141359_l1	141359	MPV	Tourneo Custom V362	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1 body-length branch.	READY
141359_l2	141359	MPV	Tourneo Custom V362	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2 body-length branch.	READY
141360	141360	MPV	Transit Custom V362 facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	PHEV Bus仅有L1H1车身分支。	READY
141371	141371	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 pre-facelift SUV.	READY
141373	141373	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 pre-facelift SUV.	READY
141374	141374	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	W213 facelift sedan.	READY
141383	141383	Wagon	Ceed III CD	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	货运登记的Ceed Sportswagon PHEV外廓。	READY
141384	141384	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141386	141386	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141387	141387	SUV	Q7 II 4M facelift	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M facelift SUV.	READY
141389_standard	141389	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
141389_long	141389	MPV	Traveller I K0	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long车长分支。	READY
141390	141390	Wagon	ProCeed III CD	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD shooting-brake body.	READY
141391	141391	Coupe	CLS III C257	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257 four-door coupe.	READY
141392	141392	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑。	READY
141393	141393	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷。	READY
141394	141394	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141395	141395	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141396	141396	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑。	READY
141397	141397	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141399	141399	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷。	READY
141400	141400	SUV	XCeed I CD	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD pre-facelift five-door crossover.	READY
141401	141401	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141403	141403	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141404	141404	Van	Sportage IV QL	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	QL cargo-registered five-door SUV exterior.	READY
141406	141406	Liftback	Stinger I CK	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH	CK five-door liftback.	READY
141411	141411	Convertible	AMG GT I R190 facelift	R190	2	EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	MEDIUM	标准宽度R190 GT Roadster外廓。	READY
141412	141412	Coupe	AMG GT I C190 facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-C190-GT-COUPE-01	HIGH	标准宽度C190 GT Coupé外廓。	READY
141422	141422	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141423	141423	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141424	141424	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141426	141426	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141428	141428	Wagon	Arteon I 3H Shooting Brake	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	五门Shooting Brake外廓。	READY
141430_88	141430	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141430_109	141430	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
141431_88	141431	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141431_109	141431	SUV	Series I			EU-LAND-ROVER-SERIES-I-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
141432_88	141432	SUV	Series II			EU-LAND-ROVER-SERIES-II-SUV-88-01	MEDIUM	88英寸封闭车身外廓分支。	READY
141432_109	141432	SUV	Series II			EU-LAND-ROVER-SERIES-II-SUV-109-01	MEDIUM	109英寸封闭车身外廓分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5201-5300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group Press 5 Series Sedan technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0308529EN/464009
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439	CarsGuide Mercedes-Benz CLA-Class dimensions	https://www.carsguide.com.au/mercedes-benz/cla-class/car-dimensions/2021
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498	BMW Group Press 5 Series Touring technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318750EN/463132
EU-TOYOTA-YARIS-IV-XP210-GR-HATCHBACK-3D-01	3995	1805	1455	Toyota Europe GR Yaris official press kit	https://newsroom.toyota.eu/gr-yaris-born-from-the-world-rally-championship/
EU-BMW-7-G11-LCI-SEDAN-01	5120	1902	1467	BMW Group Press 7 Series LCI press kit	https://www.press.bmwgroup.com/south-africa/article/detail/T0300037EN/the-new-bmw-7-series-now-available-in-south-africa?language=en
EU-BMW-7-G12-LCI-SEDAN-LWB-01	5260	1902	1479	BMW Group Press 7 Series LCI press kit	https://www.press.bmwgroup.com/south-africa/article/detail/T0300037EN/the-new-bmw-7-series-now-available-in-south-africa?language=en
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW Group Press X3 xDrive20i technical data	https://www.press.bmwgroup.com/brazil/article/detail/T0286184PT/novo-bmw-x3-xdrive20i-x-line-chega-%C3%A0s-concession%C3%A1rias-por-r-276-950?language=pt
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676	BMW Group Press X3 launch technical data	https://www.press.bmwgroup.com/brazil/article/detail/T0277809PT/nova-gera%C3%A7%C3%A3o-do-bmw-x3-tem-pr%C3%A9-venda-no-brasil-a-partir-de-r-309-950
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	BMW Group Press X4 technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0291271EN/432797
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621	BMW Group Press X4 technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0291271EN/432797
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW Group Press all-new X5	https://www.press.bmwgroup.com/global/article/detail/T0281455EN/the-all-new-bmw-x5%3A-the-prestige-sav-with-the-most-innovative-technologies
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW Group Press new X6	https://www.press.bmwgroup.com/global/article/detail/T0297827EN/the-new-bmw-x6-a-leader-with-broad-shoulders
EU-BMW-X7-G07-SUV-01	5151	2000	1805	BMW Group Press first-ever X7	https://www.press.bmwgroup.com/middle-east/article/detail/T0286727EN/the-first-ever-bmw-x7?language=en
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442	Mercedes-Benz Media CLA Shooting Brake technical data	https://media.mercedes-benz.com/article/f38dfb3b-a7ec-489f-845a-0c88fdaef6fa
EU-MERCEDES-BENZ-EQV-V447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz EQV official brochure	https://i.i-sgcm.com/new_cars/cars/21620/brochures/brochure_20221011015941.pdf
EU-MERCEDES-BENZ-EQV-V447-MPV-EXTRA-LONG-01	5370	1928	1901	Auto-Data Mercedes-Benz EQV model specifications	https://www.auto-data.net/en/mercedes-benz-eqv-model-2839
EU-MERCEDES-BENZ-MARCO-POLO-W447-ACTIVITY-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo August 2019 official price list	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_marco_polo_series_2019_g.pdf
EU-FORD-USA-MUSTANG-S550-SHELBY-GT500-COUPE-01	4813	1946	1379	Ford 2020 Mustang Technical Specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2020/mustang/2020-Mustang-Tech_Specs.pdf
EU-BMW-IX3-G08-SUV-01	4734	1891	1668	BMW Group Press iX3 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0314265EN/457881
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Hyundai i30 official technical specifications	https://www.hyundai.news/newsroom/dam/uk/press-kits/hyundai-uk-i30-tech-spec-pricing-model-year-2023-0424.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H1-RWD-01	5932	2020	2361	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L2H2-RWD-01	5932	2020	2650	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435	Toyota Europe Corolla Sedan official press kit	https://newsroom.toyota.eu/2019-corolla-sedan/
EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	3940	1745	1500	Toyota Europe New Yaris official press kit	https://newsroom.toyota.eu/2020-new-yaris/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-RWD-01	5321	2020	2289	AutoScout24 Mercedes-Benz Sprinter chassis cab specifications	https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-cab-311-cdi-32-3-5t-rwd-autres-diesel-7014/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-RWD-01	5886	2020	2288	Mercedes-Benz Sprinter chassis cab official brochure	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-RWD-01	6696	2020	2280	Mercedes-Benz Sprinter chassis cab official brochure	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L1-RWD-01	5321	2020	2289	AutoScout24 Mercedes-Benz Sprinter double-cab specifications	https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-dble-cab-311-cdi-32-3-5t-rwd-autres-diesel-7015/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L2-RWD-01	5886	2020	2289	AutoScout24 Mercedes-Benz Sprinter double-cab specifications	https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-dble-cab-311-cdi-37-3-5t-rwd-autres-diesel-7015/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREWCAB-L3-RWD-01	6696	2020	2301	Mercedes-Benz Sprinter chassis cab official brochure	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Citroën New C4 and ë-C4 official press release	https://www.media.stellantis.com/uk-en/citroen/press/new-c4-and-new-e-c4-100-electric-citroen-reinvents-the-compact-hatchback
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L3H2-RWD-01	6967	2020	2646	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-L4H2-RWD-01	7367	2020	2643	Mercedes-Benz Sprinter January 2021 official brochure	https://www.kinahan.ie/custom/public/files/sprinter-panel-ebrochure-2021-1-.pdf
EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	4971	1945	1461	Maserati Ghibli official mini book	https://www.maserati.com/content/dam/dealers/jp/default/EN_Maserati-MY19-MiniBook-Ghibli.pdf
EU-AUDI-80-B2-TYP81-SEDAN-PREFL-01	4383	1682	1365	Automobile-Catalog 1983 Audi 80 2.0 CD specifications	https://www.automobile-catalog.com/car/1983/230375/audi_80_2_0_cd.html
EU-MERCEDES-BENZ-VITO-W447-MIXTO-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-MIXTO-LONG-01	5140	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-MIXTO-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Tourer June 2020 official price list	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	4840	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 2.8 D-4D	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2017-5-door-2.8-d-4d-204hp-4wd-48023
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	CarExpert Hyundai Tucson TL dimensions	https://www.carexpert.com.au/hyundai/tucson/2017-elite-r-series-sunroof-awd-f96ebe7b
EU-LADA-NIVA-II-SUV-01	4056	1800	1690	LADA Niva official owner manual	https://static.lada.ru/vaz/files/exp_manual/lada_niva_re_01_07_2020.pdf
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450	CarsGuide Kia Rio dimensions	https://www.carsguide.com.au/kia/rio/car-dimensions/2020
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Auto-Data Kia Sportage IV specifications	https://www.auto-data.net/en/kia-sportage-iv-1.6-t-gdi-177hp-awd-dct-22747
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495	Kia XCeed official technical specifications	https://eu-www.kia.com/content/dam/kwcms/kme/hu/hu/assets/contents/utility/Brochure/specification/kia-xceed-muszaki-adatok.pdf
EU-KIA-SOUL-III-SK3-EV-HATCHBACK-01	4195	1800	1605	Kia e-Soul official specifications	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/spechsheet/e-Soul-Specifications.pdf
EU-RENAULT-SYMBOL-III-SEDAN-FACELIFT-01	4354	1733	1517	Renault Symbol November 2019 official brochure	https://cdn.group.renault.com/ren/tr/brochures/symbol-l46/tr-renault-symbol-112019.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910	Peugeot Expert official specifications	https://motorlib.carsireland.ie/brand-dealers/peugeot/spec/expert.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904	Peugeot Expert official specifications	https://motorlib.carsireland.ie/brand-dealers/peugeot/spec/expert.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935	Peugeot Expert official specifications	https://motorlib.carsireland.ie/brand-dealers/peugeot/spec/expert.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905	Peugeot Traveller official brochure	https://www.peugeot.fr/content/dam/peugeot/france/b2c/documentation/brochures/TRAVELLER_BROCHURE.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890	Peugeot Traveller official brochure	https://www.peugeot.fr/content/dam/peugeot/france/b2c/documentation/brochures/TRAVELLER_BROCHURE.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890	Peugeot Traveller official brochure	https://www.peugeot.fr/content/dam/peugeot/france/b2c/documentation/brochures/TRAVELLER_BROCHURE.pdf
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	4973	1986	1979	Ford Transit Custom PHEV official price list	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-transit-custom-PHEV.pdf
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	5340	1986	1977	Ford Transit Custom PHEV official price list	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-transit-custom-PHEV.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020	Ford Transit Custom PHEV official price list	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-transit-custom-PHEV.pdf
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	VehicleScore Mercedes-Benz GLA dimensions	https://vehiclescore.co.uk/car-dimensions-check/mercedes-benz/gla
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift specifications	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-450-367hp-eq-boost-4matic-9g-tronic-40875
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed official brochure	https://www.kia.com/content/dam/kwcms/kme/pl/pl/assets/contents/utility/Brochure/Kia-Ceed-5D-SW-MY-20-katalog.pdf
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Auto-Data Kia ProCeed III specifications	https://www.auto-data.net/en/kia-proceed-iii-1.4-t-gdi-140hp-dct-34474
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741	Audi Q7 official dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-q7-1446/download
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 specifications	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-cls-450-367hp-eq-boost-4matic-9g-tronic-32272
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428	Automoli Mercedes-Benz E-Class C238 facelift technical data	https://www.automoli.com/en/vehicles/mercedes-benz/klasa-e/klasa-e-coupe-c238-facelift-2020-7864/
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class A238 facelift technical data	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-generation-7863
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400	Kia Stinger official technical specifications	https://www.kia.com/content/dam/kwcms/kme/gr/el/assets/vehicles/info/Kia-Stinger-Texnika-Xaraktiristika.pdf
EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	4551	1939	1260	Auto-Data Mercedes-AMG GT Roadster S specifications	https://www.auto-data.net/en/mercedes-benz-amg-gt-roadster-r190-s-4.0-v8-522hp-dct-35068
EU-MERCEDES-BENZ-AMG-GT-C190-GT-COUPE-01	4544	1939	1287	Automobile-Catalog 2020 Mercedes-AMG GT specifications	https://www.automobile-catalog.com/car/2020/2874830/mercedes-amg_gt.html
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	4866	1871	1462	Volkswagen Newsroom Arteon Shooting Brake technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
EU-LAND-ROVER-SERIES-I-SUV-88-01	3556	1575	1930	Rover Company Land-Rover 1957 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-I-SUV-109-01	4407	1575	1981	Rover Company Land-Rover 1957 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20I/Land%20Rover_BR%20Series%20I_1957.pdf
EU-LAND-ROVER-SERIES-II-SUV-88-01	3616	1626	1969	Rover Company Land-Rover Series II 1958 official brochure	https://www.auto-brochures.com/makes/landrover/Series%20II/Land%20Rover_BR%20Series%20II_1958.pdf
EU-LAND-ROVER-SERIES-II-SUV-109-01	4445	1626	2057	Rover Company Land-Rover Series II 109 Pick-Up 1958 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Series-II-Pick-Up-1958-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5201-5300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf "https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5545 行）
- 累计尺寸组：dimension_groups_final.tsv（2038 行）

