# 任务：all 第 3701-3800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0038__4509f83f


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
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-CITROEN-XM-Y3-WAGON-5D-01	4963	1794	1464
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-02	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-02	4250	1735	1525
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-BRAVO-II-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-LINEA-323-SEDAN-01	4560	1730	1494
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-HYUNDAI-MATRIX-FACELIFT-MPV-01	4025	1740	1685
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375
EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	4435	1765	1465
EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	4415	1755	1465
EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	4580	1755	1465
EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	4917	1873	1430
EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	4913	1873	1390
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	4107	1777	1296
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	4107	1788	1298
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	4532	1827	1298
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	4562	1820	1317
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261
EU-MERCEDES-BENZ-SLR-R199-ROADSTER-01	4656	1908	1281
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	4330	1780	1615
EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	4315	1780	1605
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-RENAULT-KANGOO-I-FACELIFT-MPV-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1835
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839
EU-RENAULT-KANGOO-II-VAN-01	4213	1829	1844
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	4220	1760	1515
EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	4220	1760	1505
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517
EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	5059	1903	1450
EU-VW-PHAETON-3D-SEDAN-PREFL-01	5055	1903	1450
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	3	320 D Xdrive	Stufenheck	Allrad	Diesel	130	177	Sep 2008	Feb 2010	2024-03-01	31031
BMW	3	325 I Xdrive	Kombi	Allrad	Benzin	160	218	Sep 2008	Jun 2012	2024-03-01	31032
BMW	3	330 I Xdrive	Kombi	Allrad	Benzin	200	272	Sep 2007	Jun 2012	2024-03-01	31033
BMW	3	335 I Xdrive	Kombi	Allrad	Benzin	225	306	Sep 2008	Jun 2012	2024-03-01	31034
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	130	177	Sep 2008	Feb 2010	2024-03-01	31035
BMW	3	325 I Xdrive	Coupe	Allrad	Benzin	160	218	Sep 2008	Dec 2013	2024-03-01	31036
BMW	3	330 I Xdrive	Coupe	Allrad	Benzin	200	272	Mar 2010	Jun 2013	2024-03-01	31037
BMW	3	335 I Xdrive	Coupe	Allrad	Benzin	225	306	Nov 2008	Dec 2013	2024-03-01	31038
BMW	3	320 D Xdrive	Coupe	Allrad	Diesel	130	177	Sep 2008	Feb 2010	2024-03-01	31039
BMW	3	330 D Xdrive	Coupe	Allrad	Diesel	180	245	Feb 2010	Jun 2013	2024-03-01	31040
Mercedes-benz	B-Klasse sports tourer	B 180 NGT	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	85	116	Apr 2008	Nov 2011	2024-03-01	31041
Mercedes-benz	E-Klasse	E 250 CGI	Stufenheck	Heckantrieb	Benzin	150	204	Jan 2009	Dec 2015	2024-03-01	31042
Mercedes-benz	E-Klasse	E 350 CGI	Stufenheck	Heckantrieb	Benzin	215	292	Jan 2009	Aug 2011	2024-03-01	31044
Mercedes-benz	E-Klasse	E 350 4-matic	Stufenheck	Allrad	Benzin	200	272	Jan 2009	Aug 2011	2024-03-01	31045
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	285	388	Jan 2009	Dec 2011	2024-03-01	31046
Mercedes-benz	E-Klasse	E 500 4-matic	Stufenheck	Allrad	Benzin	285	388	Jan 2009	Dec 2011	2024-03-01	31047
Mercedes-benz	E-Klasse	E 220 CDI / Bluetec	Stufenheck	Heckantrieb	Diesel	125	170	Jan 2009	Dec 2016	2024-03-01	31048
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec	Stufenheck	Heckantrieb	Diesel	150	204	Jan 2009	Dec 2016	2024-03-01	31049
Mercedes-benz	E-Klasse	E 350 Bluetec	Stufenheck	Heckantrieb	Diesel	155	211	Jan 2009	Dec 2015	2024-03-01	31050
Mercedes-benz	E-Klasse	E 350 CDI	Stufenheck	Heckantrieb	Diesel	170	231	Jan 2009	Dec 2015	2024-03-01	31051
Mercedes-benz	E-Klasse	E 250 CGI	Coupe	Heckantrieb	Benzin	150	204	Jan 2009	Dec 2016	2024-03-01	31053
Mercedes-benz	E-Klasse	E 350 CGI	Coupe	Heckantrieb	Benzin	215	292	Jan 2009	Dec 2011	2024-03-01	31054
Mercedes-benz	E-Klasse	E 500	Coupe	Heckantrieb	Benzin	285	388	Jan 2009	Dec 2016	2024-03-01	31055
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec / D	Coupe	Heckantrieb	Diesel	150	204	Jan 2009	Dec 2016	2024-03-01	31056
Mercedes-benz	E-Klasse	E 350 CDI	Coupe	Heckantrieb	Diesel	170	231	Jan 2009	Jun 2011	2024-03-01	31057
Nissan	Qashqai i	1.5 DCI	SUV	Frontantrieb	Diesel	76	103	Aug 2008	Jan 2010	2025-06-01	31058
Mercedes-benz	A-Klasse	A 160	Schrägheck	Frontantrieb	Benzin	70	95	Apr 2009	Jun 2012	2024-03-01	31059
Mercedes-benz	A-Klasse	A 180	Schrägheck	Frontantrieb	Benzin	85	116	Apr 2009	Jun 2012	2024-03-01	31060
Mercedes-benz	B-Klasse sports tourer	B 160	Schrägheck	Frontantrieb	Benzin	70	95	Apr 2009	Nov 2011	2024-03-01	31061
Mercedes-benz	B-Klasse sports tourer	B 180	Schrägheck	Frontantrieb	Benzin	85	116	Apr 2009	Nov 2011	2024-03-01	31062
Mercedes-benz	Cls	CLS 300	Coupe	Heckantrieb	Benzin	170	231	Apr 2009	Dec 2010	2024-03-01	31063
Mercedes-benz	Cls	CLS 350 CDI	Coupe	Heckantrieb	Diesel	165	224	Apr 2009	Dec 2010	2024-03-01	31064
Mercedes-benz	Sl	300	Cabriolet	Heckantrieb	Benzin	170	231	Apr 2009	Jan 2012	2024-03-01	31066
Mercedes-benz	Slk	300	Cabriolet	Heckantrieb	Benzin	170	231	Apr 2009	Feb 2011	2024-03-01	31067
Jaguar	X-Type i	2.2 D	Stufenheck	Frontantrieb	Diesel	107	146	Jan 2007	Nov 2009	2024-03-01	31068
Jaguar	X-Type i	2.2 D	Kombi	Frontantrieb	Diesel	107	146	Jan 2007	Dec 2009	2024-03-01	31069
VW	Jetta iii	1.4 TSI	Stufenheck	Frontantrieb	Benzin	118	160	Jul 2008	Oct 2010	2024-03-01	31070
Audi	Tt	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	147	200	Jun 2008	Jun 2010	2024-03-01	31071
Audi	Tt	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	147	200	Jun 2008	Jun 2010	2024-03-01	31072
Audi	A3	1.6	Cabriolet	Frontantrieb	Benzin	75	102	Sep 2008	May 2010	2024-03-01	31073
Mazda	3	1.6 MZR	Schrägheck	Frontantrieb	Benzin	77	105	Dec 2008	Sep 2014	2024-03-01	31074
Mazda	3	2.0 MZR Disi	Schrägheck	Frontantrieb	Benzin	111	151	Dec 2008	May 2013	2024-03-01	31075
Mazda	3	2.0 MZR	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2009	Sep 2014	2024-03-01	31076
Mazda	3	1.6 Mz-cd	Schrägheck	Frontantrieb	Diesel	80	109	Dec 2008	May 2013	2024-03-01	31077
Mazda	3	2.2 MZR CD	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2009	Oct 2013	2024-03-01	31078
Mazda	3	2.2 MZR CD	Schrägheck	Frontantrieb	Diesel	136	185	Jan 2009	May 2013	2024-03-01	31079
Mazda	3	1.6 MZR	Stufenheck	Frontantrieb	Benzin	77	105	Dec 2008	Sep 2014	2024-03-01	31080
Mazda	3	2.0 MZR	Stufenheck	Frontantrieb	Benzin	110	150	Mar 2009	Sep 2014	2024-03-01	31081
Mazda	3	2.0 MZR Disi	Stufenheck	Frontantrieb	Benzin	111	151	Feb 2009	May 2013	2024-03-01	31082
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	50	68	Nov 2008	Dec 2012	2025-12-01	31083
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	63	86	Nov 2008	Dec 2012	2025-12-01	31084
Dacia	Sandero	1.2 16V	Schrägheck	Frontantrieb	Benzin	55	75	Nov 2008	Jun 2013	2025-12-01	31086
Fiat	Bravo ii	2.0 D Multijet	Schrägheck	Frontantrieb	Diesel	121	165	Sep 2008	Dec 2014	2024-03-01	31091
Fiat	Linea	1.6 D Multijet	Stufenheck	Frontantrieb	Diesel	77	105	Jun 2009	-	2024-03-01	31092
Ford	Focus iii	1.6 TI	Stufenheck	Frontantrieb	Benzin	63	85	Aug 2011	Feb 2020	2024-03-01	31093
Ford	Focus iii	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	74	100	Feb 2012	Feb 2020	2024-03-01	31094
Ford	Focus iii	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	92	125	Feb 2012	Feb 2020	2024-03-01	31095
VW	Eos	1.4 TSI	Cabriolet	Frontantrieb	Benzin	90	122	Nov 2007	Aug 2015	2024-03-01	31096
VW	Eos	1.4 TSI	Cabriolet	Frontantrieb	Benzin	118	160	May 2008	Aug 2015	2024-03-01	31100
VW	Phaeton	3.6 V6 4motion	Stufenheck	Allrad	Benzin	206	280	Nov 2008	Mar 2016	2024-03-01	31101
VW	Phaeton	3.0 V6 TDI 4motion	Stufenheck	Allrad	Diesel	176	240	Nov 2008	Mar 2016	2024-03-01	31102
VW	Phaeton	3.0 V6 TDI 4motion	Stufenheck	Allrad	Diesel	171	233	Jun 2007	Nov 2008	2024-03-01	31103
Honda	Insight	1.3 IMA	Schrägheck	Frontantrieb	Benzin/Elektro	65	88	Apr 2009	Dec 2013	2025-12-01	31104
VW	Eos	3.6 V6	Cabriolet	Frontantrieb	Benzin	191	260	May 2009	Nov 2010	2024-03-01	31105
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Nov 2008	Jul 2010	2024-03-01	31106
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	81	110	Nov 2008	Nov 2010	2024-03-01	31107
VW	Passat b6 variant	2.0 Bluetdi	Kombi	Frontantrieb	Diesel	105	143	Jan 2009	Nov 2010	2024-03-01	31108
VW	Passat b6	2.0 Bluetdi	Stufenheck	Frontantrieb	Diesel	105	143	Jan 2009	Nov 2010	2024-03-01	31109
VW	Sharan	2.0 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	85	115	Apr 2006	Mar 2010	2024-03-01	31110
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	55	75	Mar 2009	Mar 2010	2024-03-01	31111
Seat	Ibiza iv	1.6	Schrägheck	Frontantrieb	Benzin	77	105	May 2008	Mar 2012	2024-03-01	31112
Seat	Ibiza iv sc	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Jul 2008	May 2015	2025-06-01	31113
Seat	Leon	1.6	Schrägheck	Frontantrieb	Benzin	75	102	Oct 2005	Jun 2006	2024-03-01	31114
Toyota	Auris	1.33 Dual-vvti	Schrägheck	Frontantrieb	Benzin	74	101	May 2009	Sep 2012	2024-03-01	31115
Toyota	Auris	1.6	Schrägheck	Frontantrieb	Benzin	97	132	May 2009	Sep 2012	2024-03-01	31116
Renault	Kangoo	Elect'road RE	Großraumlimousine	Frontantrieb	Elektro	22	30	Jan 2002	Dec 2004	2024-03-01	31117
Opel	Insignia a	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Jul 2008	Mar 2017	2024-03-01	31120
Opel	Insignia a	2.0 Turbo 4X4	Schrägheck	Allrad	Benzin	162	220	Jul 2008	Mar 2017	2024-03-01	31121
Opel	Insignia a	2.0 Biturbo Cdti 4X4	Schrägheck	Allrad	Diesel	140	190	May 2009	Dec 2011	2024-03-01	31122
Opel	Insignia a	2.0 Biturbo Cdti 4X4	Stufenheck	Allrad	Diesel	140	190	Jul 2008	Dec 2011	2024-03-01	31123
Opel	Insignia a sports tourer	2.0 Biturbo Cdti 4X4	Kombi	Allrad	Diesel	140	190	Jul 2008	Mar 2017	2024-03-01	31124
Dacia	Logan	1.4	Kasten/Kombi	Frontantrieb	Benzin	55	75	Mar 2009	-	2024-03-01	31125
Dacia	Logan	1.6	Kasten/Kombi	Frontantrieb	Benzin	64	87	Mar 2009	-	2024-03-01	31126
Dacia	Logan	1.5 DCI	Kasten/Kombi	Frontantrieb	Diesel	50	68	Mar 2009	-	2024-03-01	31127
Dacia	Logan	1.5 DCI	Kasten/Kombi	Frontantrieb	Diesel	63	86	Mar 2009	-	2024-03-01	31128
Dacia	Logan	1.6	Pick-up	Frontantrieb	Benzin	64	87	Mar 2008	-	2024-03-01	31129
Dacia	Logan	1.5 DCI	Pick-up	Frontantrieb	Diesel	50	68	Mar 2008	-	2024-03-01	31130
Dacia	Logan	1.5 DCI	Pick-up	Frontantrieb	Diesel	63	86	Mar 2008	-	2024-03-01	31131
Hyundai	H-1 travel	2.5 Crdi	Bus	Heckantrieb	Diesel	125	170	May 2008	-	2024-03-01	31132
Hyundai	Matrix	1.6	Großraumlimousine	Frontantrieb	Benzin	66	90	Jan 2002	Dec 2005	2024-03-01	31133
Toyota	Rav 4 iii	2	SUV	Frontantrieb	Benzin	116	158	Dec 2008	Jun 2013	2024-03-01	31135
Toyota	Rav 4 iii	2.0 4WD	SUV	Allrad	Benzin	116	158	Dec 2008	Jun 2013	2024-03-01	31136
Citroën	Bx	19 4X4	Kombi	Allrad	Benzin	78	107	Jun 1989	May 1991	2024-03-01	31138
Toyota	Rav 4 iii	2.2 D 4WD	SUV	Allrad	Diesel	110	150	Dec 2008	Jun 2013	2024-03-01	31139
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	88	120	Dec 2008	Jul 2010	2024-03-01	31140
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	128	174	Dec 2008	Jul 2010	2024-03-01	31141
Toyota	Iq	1	Schrägheck	Frontantrieb	Benzin	50	68	Jan 2009	Dec 2015	2024-03-01	31142
Toyota	Iq	1.33	Schrägheck	Frontantrieb	Benzin	72	98	Jan 2009	Dec 2015	2024-03-01	31143
Toyota	Iq	1.4 D-4d	Schrägheck	Frontantrieb	Diesel	66	90	Jan 2009	Dec 2015	2024-03-01	31144
Citroën	Xm	2	Schrägheck	Frontantrieb	Benzin	94	128	May 1989	Jun 1994	2024-03-01	31145


--- Round 1 / 首次发送 ---
更新点

* 复用跨批次已有尺寸组，完成 BMW E90/E91/E92、Nissan Qashqai、Audi TT/A3、Fiat Bravo/Linea、VW Phaeton/Passat/Sharan、MINI R56、SEAT、Toyota Auris、Opel Insignia 等映射。
* 首次创建并闭合 6 个 Mercedes-Benz 尺寸组：W245、W169、W212 改款前后、C207 改款前后。来源页面分别列出车身宽度与含后视镜宽度，因此本轮 `WidthMM` 使用明确的不含后视镜数值。([汽车数据][1])
* 未按输入表的宽泛结束日期机械拆分 Opel Insignia：180 hp、220 hp 4X4 和 190 hp 版本均限定在 2013 年改款前外廓，避免错误创建 facelift 派生行。([汽车数据][2])

当前批次进度

* 已闭合输入 Ktype：56 / 100
* READY 映射：65 行
* 待处理 Ktype：44
* 当前已引用尺寸组：32 个
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31031	31031	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	E90 LCI四门轿车。	READY
31032	31032	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31033_prefl	31033	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	该Ktype跨越E91改款，拆分改款前外廓。	READY
31033_facelift	31033	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	该Ktype跨越E91改款，拆分改款后外廓。	READY
31034	31034	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31035	31035	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31036_prefl	31036	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	该Ktype跨越E92改款，拆分改款前外廓。	READY
31036_facelift	31036	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	该Ktype跨越E92改款，拆分改款后外廓。	READY
31037	31037	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	E92 LCI双门轿跑。	READY
31038_prefl	31038	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	该Ktype跨越E92改款，拆分改款前外廓。	READY
31038_facelift	31038	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	该Ktype跨越E92改款，拆分改款后外廓。	READY
31039	31039	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	E92改款前双门轿跑。	READY
31040	31040	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	245 hp版本对应E92 LCI外廓。	READY
31041	31041	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31042	31042	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31044	31044	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31045	31045	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31046	31046	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31047	31047	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31048_prefl	31048	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该Ktype跨越W212改款，拆分改款前外廓。	READY
31048_facelift	31048	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	该Ktype跨越W212改款，拆分改款后外廓。	READY
31049_prefl	31049	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该Ktype跨越W212改款，拆分改款前外廓。	READY
31049_facelift	31049	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	该Ktype跨越W212改款，拆分改款后外廓。	READY
31050	31050	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31051	31051	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31053	31053	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31054	31054	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31055	31055	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31056_prefl	31056	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该Ktype跨越C207改款，拆分改款前外廓。	READY
31056_facelift	31056	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	该Ktype跨越C207改款，拆分改款后外廓。	READY
31057	31057	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31058	31058	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	J10改款前五门SUV。	READY
31059	31059	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	W169改款后五门掀背车。	READY
31060	31060	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	W169改款后五门掀背车。	READY
31061	31061	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31062	31062	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31063	31063	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门轿跑。	READY
31064	31064	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门轿跑。	READY
31066	31066	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008年第二次改款后的R230双门敞篷。	READY
31071	31071	Convertible	TT 8J	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	8J9改款前双门Roadster。	READY
31072	31072	Coupe	TT 8J	8J3	2	EU-AUDI-TT-8J-COUPE-01	HIGH	8J3双门Coupe。	READY
31073	31073	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH	8P7双门Cabriolet。	READY
31091	31091	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背车。	READY
31092	31092	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车。	READY
31101_prefl	31101	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31101_facelift	31101	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31102_prefl	31102	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31102_facelift	31102	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31103	31103	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	2010年改款前四门轿车。	READY
31106	31106	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
31107	31107	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
31108	31108	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
31109	31109	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
31110	31110	MPV	Sharan I facelift	7M	5	EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	HIGH	7M改款后五门MPV。	READY
31111	31111	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门掀背车。	READY
31113_prefl	31113	Hatchback	Ibiza IV 6J	6J1	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	SC三门Ktype跨越改款，拆分改款前外廓。	READY
31113_facelift	31113	Hatchback	Ibiza IV 6J	6J1	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	SC三门Ktype跨越改款，拆分改款后外廓。	READY
31114	31114	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	1P改款前五门掀背车。	READY
31115	31115	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	E150标准车身五门掀背车。	READY
31116	31116	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	E150标准车身五门掀背车。	READY
31120	31120	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	180 hp版本仅对应改款前五门外廓。	READY
31121	31121	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	220 hp 4X4版本仅对应改款前五门外廓。	READY
31122	31122	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	190 hp版本对应改款前五门外廓。	READY
31123	31123	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	190 hp版本对应改款前四门外廓。	READY
31124	31124	Wagon	Insignia A Sports Tourer		5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	190 hp版本对应改款前旅行车外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	4273	1777	1604	Auto-Data.net Mercedes-Benz B-class W245 facelift specification	https://www.auto-data.net/en/mercedes-benz-b-class-w245-facelift-2008-b-180-cdi-109hp-12509
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	4868	1854	1470	Auto-Data.net Mercedes-Benz E-class W212 E 250 CGI specification	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	4879	1854	1474	Auto-Data.net Mercedes-Benz E-class W212 facelift specification	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-250-bluetec-204hp-9g-tronic-52776
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	4698	1786	1397	Auto-Data.net Mercedes-Benz E-class Coupe C207 E 250 CGI specification	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-e-250-cgi-blueefficiency-204hp-5g-tronic-17395
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data.net Mercedes-Benz E-class Coupe C207 facelift specification	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-e-250-cdi-204hp-18764
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	3883	1764	1593	Auto-Data.net Mercedes-Benz A-class W169 facelift A 160 specification	https://www.auto-data.net/en/mercedes-benz-a-class-w169-facelift-2008-a-160-blueefficiency-95hp-52071
```

下一步优先处理

1. 按共享外廓聚类闭合 Mazda 3 BL 掀背/轿车、Dacia Sandero I、Ford Focus III Sedan 和 VW Eos 改款前后。
2. 随后处理 Jaguar X-Type、Dacia Logan Van/Pickup、Hyundai H-1/Matrix、Toyota RAV4 III/iQ、MINI R57。
3. 最后集中解决资料较少的 Renault Kangoo Elect'road、Citroën BX 4X4 Wagon、Citroën XM Hatchback 和 Mercedes-Benz SLK 300。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371 "Mercedes-Benz E-class (W212) E 250 CGI BlueEFFICIENCY (204 Hp) 5G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-insignia-hatchback-a-1.6-turbo-180hp-1775?utm_source=chatgpt.com "Opel Insignia Hatchback (A) 1.6 Turbo (180 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 闭合 31 个剩余 Ktype，新增 44 行 READY 映射。
* 首次建立 17 个尺寸组，覆盖 SLK R171、Jaguar X-Type、Jetta III、Mazda3 BL、Sandero I、Focus III Sedan、Eos、Insight II、Ibiza IV 五门版以及 Logan Van/Pickup。
* Mazda3 BL、Focus III Sedan 和 VW Eos 按改款前后拆分；发动机、燃料和功率差异未重复建组。
* 仍有 13 个 Ktype 待闭合。

当前批次进度

* 已闭合输入 Ktype：87 / 100
* READY 映射：109 行
* PENDING 输入 Ktype：13
* 已确认并引用尺寸组：49 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31067	31067	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK300-01	HIGH	SLK 300双门硬顶敞篷外廓。	READY
31068	31068	Sedan	X-Type I	X400	4	EU-JAGUAR-X-TYPE-I-X400-SEDAN-4D-01	HIGH	X400四门轿车。	READY
31069	31069	Wagon	X-Type I	X400	5	EU-JAGUAR-X-TYPE-I-X400-WAGON-5D-01	HIGH	X400五门旅行车。	READY
31070	31070	Sedan	Jetta III	1K2	4	EU-VW-JETTA-III-1K2-SEDAN-4D-01	HIGH	1K2四门轿车。	READY
31074_prefl	31074	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31074_facelift	31074	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31075_prefl	31075	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31075_facelift	31075	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31076_prefl	31076	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31076_facelift	31076	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31077	31077	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	80kW版本对应改款前外廓。	READY
31078_prefl	31078	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31078_facelift	31078	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31079_prefl	31079	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31079_facelift	31079	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31080_prefl	31080	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31080_facelift	31080	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31081_prefl	31081	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31081_facelift	31081	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31082_prefl	31082	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	MEDIUM	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31082_facelift	31082	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	MEDIUM	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31083	31083	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31084	31084	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31086	31086	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31093_prefl	31093	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31093_facelift	31093	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31094_prefl	31094	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31094_facelift	31094	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31095_prefl	31095	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31095_facelift	31095	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31096_prefl	31096	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31096_facelift	31096	Convertible	Eos facelift	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31100_prefl	31100	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31100_facelift	31100	Convertible	Eos facelift	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31104	31104	Hatchback	Insight II	ZE2	5	EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	HIGH	88 hp版本对应改款前ZE2外廓。	READY
31105	31105	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	3.6 V6版本对应改款前外廓。	READY
31112	31112	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	6J5改款前五门掀背车。	READY
31125	31125	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31126	31126	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31127	31127	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31128	31128	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31129	31129	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
31130	31130	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
31131	31131	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK300-01	4107	1788	1296	Auto-Data.net Mercedes-Benz SLK R171 facelift SLK 300 specification	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-300-v6-231hp-42047
EU-JAGUAR-X-TYPE-I-X400-SEDAN-4D-01	4672	1789	1392	Auto-Data.net Jaguar X-Type X400 2.2 D specification	https://www.auto-data.net/en/jaguar-x-type-x400-2.2-d-155hp-166
EU-JAGUAR-X-TYPE-I-X400-WAGON-5D-01	4716	1789	1483	Auto-Data.net Jaguar X-Type model specification	https://www.auto-data.net/en/jaguar-x-type-model-38
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459	Auto-Data.net Volkswagen Jetta V 1.4 TSI specification	https://www.auto-data.net/en/volkswagen-jetta-v-1.4-tsi-160hp-dsg-9076
EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	4460	1755	1470	Auto-Data.net Mazda3 II BL Hatchback specification	https://www.auto-data.net/en/mazda-3-ii-hatchback-bl-1.6i-105hp-31460
EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	4460	1755	1470	Auto-Data.net Mazda3 II BL facelift Hatchback specification	https://www.auto-data.net/en/mazda-3-ii-hatchback-bl-facelift-2011-1.6i-105hp-17501
EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	4580	1755	1470	Auto-Data.net Mazda3 II BL Sedan specification	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-1.6i-105hp-31347
EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	4580	1755	1470	Auto-Data.net Mazda3 II BL facelift Sedan specification	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-facelift-2011-1.6i-105hp-17497
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534	Auto-Data.net Dacia Sandero I specification	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-68hp-46137
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484	Auto-Data.net Ford Focus III Sedan specification	https://www.auto-data.net/en/ford-focus-iii-sedan-1.0-ecoboost-125hp-start-stop-18071
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484	Auto-Data.net Ford Focus III Sedan facelift specification	https://www.auto-data.net/en/ford-focus-iii-sedan-facelift-2014-1.0-ecoboost-100hp-20062
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443	Auto-Data.net Volkswagen Eos specification	https://www.auto-data.net/en/volkswagen-eos-1.4-tsi-122hp-44191
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444	Auto-Data.net Volkswagen Eos facelift specification	https://www.auto-data.net/en/volkswagen-eos-facelift-2010-1.4-tsi-122hp-20465
EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	4396	1695	1425	Auto-Data.net Honda Insight II specification	https://www.auto-data.net/en/honda-insight-ii-1.3-i-vtec-88hp-hybrid-cvt-12359
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data.net SEAT Ibiza IV 1.6 MPI specification	https://www.auto-data.net/en/seat-ibiza-iv-1.6-mpi-105hp-13469
EU-DACIA-LOGAN-I-VAN-5D-01	4450	1740	1636	Auto-Data.net Dacia Logan I Van specification	https://www.auto-data.net/en/dacia-logan-i-van-1.4-75hp-15887
EU-DACIA-LOGAN-I-PICKUP-2D-01	4499	1735	1554	Auto-Data.net Dacia Logan I Pick-up specification	https://www.auto-data.net/en/dacia-logan-i-pick-up-1.6-mpi-87hp-57271
```

下一步优先处理

1. 闭合 Toyota RAV4 III、Toyota iQ、MINI R57、Hyundai H-1 Travel 和 Hyundai Matrix。
2. 最后处理 Renault Kangoo Elect’road、Citroën BX 4X4 Wagon 与 Citroën XM Hatchback。
3. 达到 PENDING=0 后直接执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3701-3800_ktype_dimension_mapping_final.tsv
- all_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 最后 13 个输入 Ktype 已全部闭合。
* 新增 Kangoo Elect’road、Hyundai H-1、Matrix、RAV4 两个外廓阶段、Citroën BX、MINI R57 两种外廓、Toyota iQ、Citroën XM 共 10 个尺寸组。
* 已完成固定表头、唯一性、Ktype 覆盖、映射引用、尺寸正整数、来源非空及下载文件检查。
* 机械校验后的最终计数为 125 行映射、59 个尺寸组。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：125
* PENDING 映射：0
* 已确认尺寸组：59
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
31031	31031	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	E90 LCI四门轿车。	READY
31032	31032	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31033_prefl	31033	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	该Ktype跨越E91改款，拆分改款前外廓。	READY
31033_facelift	31033	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	该Ktype跨越E91改款，拆分改款后外廓。	READY
31034	31034	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31035	31035	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91 LCI五门旅行车。	READY
31036_prefl	31036	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	该Ktype跨越E92改款，拆分改款前外廓。	READY
31036_facelift	31036	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	该Ktype跨越E92改款，拆分改款后外廓。	READY
31037	31037	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	E92 LCI双门轿跑。	READY
31038_prefl	31038	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	该Ktype跨越E92改款，拆分改款前外廓。	READY
31038_facelift	31038	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	该Ktype跨越E92改款，拆分改款后外廓。	READY
31039	31039	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	E92改款前双门轿跑。	READY
31040	31040	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	245 hp版本对应E92 LCI外廓。	READY
31041	31041	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31042	31042	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31044	31044	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31045	31045	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31046	31046	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31047	31047	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31048_prefl	31048	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该Ktype跨越W212改款，拆分改款前外廓。	READY
31048_facelift	31048	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	该Ktype跨越W212改款，拆分改款后外廓。	READY
31049_prefl	31049	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该Ktype跨越W212改款，拆分改款前外廓。	READY
31049_facelift	31049	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	HIGH	该Ktype跨越W212改款，拆分改款后外廓。	READY
31050	31050	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31051	31051	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	该功率版本对应W212改款前四门轿车。	READY
31053	31053	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31054	31054	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31055	31055	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31056_prefl	31056	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该Ktype跨越C207改款，拆分改款前外廓。	READY
31056_facelift	31056	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	该Ktype跨越C207改款，拆分改款后外廓。	READY
31057	31057	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	该功率版本对应C207改款前双门轿跑。	READY
31058	31058	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	J10改款前五门SUV。	READY
31059	31059	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	W169改款后五门掀背车。	READY
31060	31060	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	HIGH	W169改款后五门掀背车。	READY
31061	31061	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31062	31062	MPV	B-Class W245 facelift	W245	5	EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	HIGH	Sports Tourer按W245五门MPV归类。	READY
31063	31063	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门轿跑。	READY
31064	31064	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门轿跑。	READY
31066	31066	Convertible	SL R230 facelift 2008	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	HIGH	2008年第二次改款后的R230双门敞篷。	READY
31067	31067	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK300-01	HIGH	SLK 300双门硬顶敞篷外廓。	READY
31068	31068	Sedan	X-Type I	X400	4	EU-JAGUAR-X-TYPE-I-X400-SEDAN-4D-01	HIGH	X400四门轿车。	READY
31069	31069	Wagon	X-Type I	X400	5	EU-JAGUAR-X-TYPE-I-X400-WAGON-5D-01	HIGH	X400五门旅行车。	READY
31070	31070	Sedan	Jetta III	1K2	4	EU-VW-JETTA-III-1K2-SEDAN-4D-01	HIGH	1K2四门轿车。	READY
31071	31071	Convertible	TT 8J	8J9	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH	8J9改款前双门Roadster。	READY
31072	31072	Coupe	TT 8J	8J3	2	EU-AUDI-TT-8J-COUPE-01	HIGH	8J3双门Coupe。	READY
31073	31073	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH	8P7双门Cabriolet。	READY
31074_prefl	31074	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31074_facelift	31074	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31075_prefl	31075	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31075_facelift	31075	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31076_prefl	31076	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31076_facelift	31076	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31077	31077	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	80kW版本对应改款前外廓。	READY
31078_prefl	31078	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31078_facelift	31078	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31079_prefl	31079	Hatchback	Mazda3 II BL	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31079_facelift	31079	Hatchback	Mazda3 II BL facelift	BL	5	EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31080_prefl	31080	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31080_facelift	31080	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31081_prefl	31081	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31081_facelift	31081	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31082_prefl	31082	Sedan	Mazda3 II BL	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	MEDIUM	该Ktype跨越2011年改款，拆分改款前外廓。	READY
31082_facelift	31082	Sedan	Mazda3 II BL facelift	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	MEDIUM	该Ktype跨越2011年改款，拆分改款后外廓。	READY
31083	31083	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31084	31084	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31086	31086	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	Sandero I五门掀背车。	READY
31091	31091	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背车。	READY
31092	31092	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车。	READY
31093_prefl	31093	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31093_facelift	31093	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31094_prefl	31094	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31094_facelift	31094	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31095_prefl	31095	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	HIGH	该Ktype跨越2014年改款，拆分改款前外廓。	READY
31095_facelift	31095	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	HIGH	该Ktype跨越2014年改款，拆分改款后外廓。	READY
31096_prefl	31096	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31096_facelift	31096	Convertible	Eos facelift	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31100_prefl	31100	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31100_facelift	31100	Convertible	Eos facelift	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31101_prefl	31101	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31101_facelift	31101	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31102_prefl	31102	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	该Ktype跨越2010年改款，拆分改款前外廓。	READY
31102_facelift	31102	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	该Ktype跨越2010年改款，拆分改款后外廓。	READY
31103	31103	Sedan	Phaeton 3D	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	2010年改款前四门轿车。	READY
31104	31104	Hatchback	Insight II	ZE2	5	EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	HIGH	88 hp版本对应改款前ZE2外廓。	READY
31105	31105	Convertible	Eos	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	HIGH	3.6 V6版本对应改款前外廓。	READY
31106	31106	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
31107	31107	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
31108	31108	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
31109	31109	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
31110	31110	MPV	Sharan I facelift	7M	5	EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	HIGH	7M改款后五门MPV。	READY
31111	31111	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门掀背车。	READY
31112	31112	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	HIGH	6J5改款前五门掀背车。	READY
31113_prefl	31113	Hatchback	Ibiza IV 6J	6J1	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	SC三门Ktype跨越改款，拆分改款前外廓。	READY
31113_facelift	31113	Hatchback	Ibiza IV 6J	6J1	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	SC三门Ktype跨越改款，拆分改款后外廓。	READY
31114	31114	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	1P改款前五门掀背车。	READY
31115	31115	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	E150标准车身五门掀背车。	READY
31116	31116	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	E150标准车身五门掀背车。	READY
31117	31117	MPV	Kangoo I Elect'road		5	EU-RENAULT-KANGOO-I-ELECTROAD-MPV-5D-01	HIGH	Elect'road乘用五门车身。	READY
31120	31120	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	180 hp版本仅对应改款前五门外廓。	READY
31121	31121	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	220 hp 4X4版本仅对应改款前五门外廓。	READY
31122	31122	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	190 hp版本对应改款前五门外廓。	READY
31123	31123	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	190 hp版本对应改款前四门外廓。	READY
31124	31124	Wagon	Insignia A Sports Tourer		5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	190 hp版本对应改款前旅行车外廓。	READY
31125	31125	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31126	31126	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31127	31127	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31128	31128	Van	Logan I Van		5	EU-DACIA-LOGAN-I-VAN-5D-01	HIGH	封闭式五门货运车身。	READY
31129	31129	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
31130	31130	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
31131	31131	Pickup	Logan I Pick-up		2	EU-DACIA-LOGAN-I-PICKUP-2D-01	HIGH	双门单排座Pickup外廓。	READY
31132	31132	MPV	H-1 II Travel	TQ	5	EU-HYUNDAI-H-1-II-TRAVEL-MPV-01	HIGH	Travel乘用五门长车身。	READY
31133	31133	MPV	Matrix	FC	4	EU-HYUNDAI-MATRIX-PREFL-MPV-01	HIGH	2001款改款前四门MPV外廓。	READY
31135_facelift2008	31135	SUV	RAV4 III XA30 facelift 2008	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2008-01	HIGH	该Ktype跨越2010年外廓变化，拆分2008年改款外廓。	READY
31135_facelift2010	31135	SUV	RAV4 III XA30 facelift 2010	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2010-01	HIGH	该Ktype跨越2010年外廓变化，拆分2010年改款外廓。	READY
31136_facelift2008	31136	SUV	RAV4 III XA30 facelift 2008	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2008-01	HIGH	该Ktype跨越2010年外廓变化，拆分2008年改款外廓。	READY
31136_facelift2010	31136	SUV	RAV4 III XA30 facelift 2010	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2010-01	HIGH	该Ktype跨越2010年外廓变化，拆分2010年改款外廓。	READY
31138	31138	Wagon	BX I Break Phase II		5	EU-CITROEN-BX-I-BREAK-PHASE-II-WAGON-4X4-01	HIGH	四驱Break五门旅行车。	READY
31139_facelift2008	31139	SUV	RAV4 III XA30 facelift 2008	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2008-01	HIGH	该Ktype跨越2010年外廓变化，拆分2008年改款外廓。	READY
31139_facelift2010	31139	SUV	RAV4 III XA30 facelift 2010	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2010-01	HIGH	该Ktype跨越2010年外廓变化，拆分2010年改款外廓。	READY
31140	31140	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	HIGH	Cooper双门敞篷外廓。	READY
31141	31141	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	HIGH	Cooper S保险杠造成独立长度外廓。	READY
31142	31142	Hatchback	iQ I	KGJ10	3	EU-TOYOTA-IQ-I-HATCHBACK-3D-01	HIGH	KGJ10三门掀背车。	READY
31143	31143	Hatchback	iQ I	NGJ10	3	EU-TOYOTA-IQ-I-HATCHBACK-3D-01	HIGH	NGJ10三门掀背车。	READY
31144	31144	Hatchback	iQ I	NUJ10	3	EU-TOYOTA-IQ-I-HATCHBACK-3D-01	HIGH	NUJ10三门掀背车。	READY
31145	31145	Hatchback	XM I Y3	Y3	5	EU-CITROEN-XM-Y3-HATCHBACK-5D-01	HIGH	Y3五门掀背车。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3701-3800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	Auto-Data.net BMW 3 Series E90 LCI 320d xDrive specification	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-320d-177hp-xdrive-27800
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data.net BMW 3 Series E91 LCI 330i xDrive specification	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-330i-272hp-xdrive-27796
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data.net BMW 3 Series E91 specification	https://www.auto-data.net/en/bmw-3-series-touring-e91-330i-258hp-steptronic-20750
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	Auto-Data.net BMW 3 Series E92 335i xDrive specification	https://www.auto-data.net/en/bmw-3-series-coupe-e92-335i-306hp-xdrive-steptronic-20722
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data.net BMW 3 Series E92 LCI specification	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-335i-306hp-xdrive-steptronic-20737
EU-MERCEDES-BENZ-B-CLASS-W245-MPV-FACELIFT-01	4273	1777	1604	Auto-Data.net Mercedes-Benz B-Class W245 facelift specification	https://www.auto-data.net/en/mercedes-benz-b-class-w245-facelift-2008-b-180-cdi-109hp-12509
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	4868	1854	1470	Auto-Data.net Mercedes-Benz E-Class W212 specification	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	4879	1854	1474	Auto-Data.net Mercedes-Benz E-Class W212 facelift specification	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-250-bluetec-204hp-9g-tronic-52776
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	4698	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 specification	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-e-250-cgi-blueefficiency-204hp-5g-tronic-17395
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 facelift specification	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-e-250-cdi-204hp-18764
EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	4315	1780	1605	Auto-Data.net Nissan Qashqai I J10 specification	https://www.auto-data.net/en/nissan-qashqai-i-j10-1.5-dci-103hp-729
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-FACELIFT-01	3883	1764	1593	Auto-Data.net Mercedes-Benz A-Class W169 facelift specification	https://www.auto-data.net/en/mercedes-benz-a-class-w169-facelift-2008-a-160-blueefficiency-95hp-52071
EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	4917	1873	1430	Auto-Data.net Mercedes-Benz CLS C219 facelift specification	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-facellift-2008-cls-350-cdi-v6-224hp-7g-tronic-44336
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-02	4562	1820	1317	Auto-Data.net Mercedes-Benz SL R230 facelift 2008 specification	https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2008-sl-300-v6-231hp-7g-tronic-41268
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK300-01	4107	1788	1296	Auto-Data.net Mercedes-Benz SLK R171 facelift SLK 300 specification	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-300-v6-231hp-42047
EU-JAGUAR-X-TYPE-I-X400-SEDAN-4D-01	4672	1789	1392	Auto-Data.net Jaguar X-Type X400 2.2 D specification	https://www.auto-data.net/en/jaguar-x-type-x400-2.2-d-155hp-166
EU-JAGUAR-X-TYPE-I-X400-WAGON-5D-01	4716	1789	1483	Auto-Data.net Jaguar X-Type model specification	https://www.auto-data.net/en/jaguar-x-type-model-38
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459	Auto-Data.net Volkswagen Jetta V 1.4 TSI specification	https://www.auto-data.net/en/volkswagen-jetta-v-1.4-tsi-160hp-dsg-9076
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358	Auto-Data.net Audi TT Roadster 8J specification	https://www.auto-data.net/en/audi-tt-roadster-8j-2.0-tfsi-200hp-quattro-s-tronic-17877
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352	Auto-Data.net Audi TT Coupe 8J specification	https://www.auto-data.net/en/audi-tt-coupe-8j-2.0-tfsi-200hp-quattro-s-tronic-4878
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424	Auto-Data.net Audi A3 Cabriolet 8P specification	https://www.auto-data.net/en/audi-a3-cabriolet-8p-facelift-2008-1.6-102hp-4228
EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	4460	1755	1470	Auto-Data.net Mazda3 II BL Hatchback specification	https://www.auto-data.net/en/mazda-3-ii-hatchback-bl-1.6i-105hp-31460
EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	4460	1755	1470	Auto-Data.net Mazda3 II BL facelift Hatchback specification	https://www.auto-data.net/en/mazda-3-ii-hatchback-bl-facelift-2011-1.6i-105hp-17501
EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	4580	1755	1470	Auto-Data.net Mazda3 II BL Sedan specification	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-1.6i-105hp-31347
EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	4580	1755	1470	Auto-Data.net Mazda3 II BL facelift Sedan specification	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-facelift-2011-1.6i-105hp-17497
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534	Auto-Data.net Dacia Sandero I specification	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-68hp-46137
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data.net Fiat Bravo II 198 specification	https://www.auto-data.net/en/fiat-bravo-ii-198-2.0-multijet-165hp-16762
EU-FIAT-LINEA-323-SEDAN-01	4560	1730	1494	Auto-Data.net Fiat Linea specification	https://www.auto-data.net/en/fiat-linea-1.4-i-77hp-7121
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484	Auto-Data.net Ford Focus III Sedan specification	https://www.auto-data.net/en/ford-focus-iii-sedan-1.0-ecoboost-125hp-start-stop-18071
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484	Auto-Data.net Ford Focus III Sedan facelift specification	https://www.auto-data.net/en/ford-focus-iii-sedan-facelift-2014-1.0-ecoboost-100hp-20062
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443	Auto-Data.net Volkswagen Eos specification	https://www.auto-data.net/en/volkswagen-eos-1.4-tsi-122hp-44191
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444	Auto-Data.net Volkswagen Eos facelift specification	https://www.auto-data.net/en/volkswagen-eos-facelift-2010-1.4-tsi-122hp-20465
EU-VW-PHAETON-3D-SEDAN-PREFL-01	5055	1903	1450	Auto-Data.net Volkswagen Phaeton pre-facelift generation specification	https://www.auto-data.net/en/volkswagen-phaeton-generation-1916
EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	5059	1903	1450	Auto-Data.net Volkswagen Phaeton facelift 2010 specification	https://www.auto-data.net/en/volkswagen-phaeton-facelift-2010-3.6-v6-fsi-280hp-4motion-tiptronic-16871
EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	4396	1695	1425	Auto-Data.net Honda Insight II specification	https://www.auto-data.net/en/honda-insight-ii-1.3-i-vtec-88hp-hybrid-cvt-12359
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data.net Volkswagen Passat B6 Sedan specification	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tdi-110hp-40820
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data.net Volkswagen Passat Variant B6 specification	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-tdi-110hp-40822
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730	Auto-Data.net Volkswagen Sharan I facelift specification	https://www.auto-data.net/en/volkswagen-sharan-i-facelift-2004-2.0-115hp-44643
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	Auto-Data.net MINI Hatch R56 One specification	https://www.auto-data.net/en/mini-hatch-r56-one-1.6-75hp-21496
EU-SEAT-IBIZA-IV-6J5-HATCHBACK-5D-PREFL-01	4052	1693	1445	Auto-Data.net SEAT Ibiza IV 1.6 MPI specification	https://www.auto-data.net/en/seat-ibiza-iv-1.6-mpi-105hp-13469
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428	Auto-Data.net SEAT Ibiza IV SC specification	https://www.auto-data.net/en/seat-ibiza-iv-sc-1.6-mpi-105hp-16891
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428	Auto-Data.net SEAT Ibiza IV SC facelift specification	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.6-tdi-105hp-19336
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data.net SEAT Leon II 1P specification	https://www.auto-data.net/en/seat-leon-ii-1p-1.6-mpi-102hp-13601
EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	4220	1760	1515	Auto-Data.net Toyota Auris I specification	https://www.auto-data.net/en/toyota-auris-i-1.3-16v-vvt-i-101hp-3498
EU-RENAULT-KANGOO-I-ELECTROAD-MPV-5D-01	3990	1660	1820	Renault/ADEME 2002 clean-vehicle brochure	https://www.ecolo.org/documents/documents_in_french/vehic-elec_VP_VU.pdf
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498	Auto-Data.net Opel Insignia A Hatchback specification	https://www.auto-data.net/en/opel-insignia-hatchback-a-1.6-turbo-180hp-1775
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data.net Opel Insignia A Sedan specification	https://www.auto-data.net/en/opel-insignia-sedan-a-2.0-cdti-190hp-4x4-dpf-1800
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520	Auto-Data.net Opel Insignia A Sports Tourer specification	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-2.0-biturbo-cdti-195hp-automatic-25980
EU-DACIA-LOGAN-I-VAN-5D-01	4450	1740	1636	Auto-Data.net Dacia Logan I Van specification	https://www.auto-data.net/en/dacia-logan-i-van-1.4-75hp-15887
EU-DACIA-LOGAN-I-PICKUP-2D-01	4499	1735	1554	Auto-Data.net Dacia Logan I Pick-up specification	https://www.auto-data.net/en/dacia-logan-i-pick-up-1.6-mpi-87hp-57271
EU-HYUNDAI-H-1-II-TRAVEL-MPV-01	5150	1920	1925	Auto-Data.net Hyundai H-1 II Travel specification	https://www.auto-data.net/en/hyundai-h-1-ii-travel-2.5-crdi-170hp-automatic-25081
EU-HYUNDAI-MATRIX-PREFL-MPV-01	4025	1740	1635	Auto-Data.net Hyundai Matrix 1.6 specification	https://www.auto-data.net/en/hyundai-matrix-1.6-103hp-13862
EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2008-01	4415	1815	1720	Auto-Data.net Toyota RAV4 III XA30 facelift 2008 specification	https://www.auto-data.net/en/toyota-rav4-iii-xa30-facelift-2008-2.2-d-4d-150hp-4wd-37225
EU-TOYOTA-RAV4-III-XA30-SUV-FACELIFT-2010-01	4445	1815	1720	Auto-Data.net Toyota RAV4 III XA30 facelift 2010 specification	https://www.auto-data.net/en/toyota-rav4-iii-xa30-facelift-2010-2.2-d-4d-150hp-4wd-37208
EU-CITROEN-BX-I-BREAK-PHASE-II-WAGON-4X4-01	4399	1682	1440	Auto-Data.net Citroen BX I Break Phase II 1.9 Evasion 4x4 specification	https://www.auto-data.net/en/citroen-bx-i-break-phase-ii-1987-1.9-evasion-107hp-4x4-15264
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414	Auto-Data.net MINI Convertible R57 Cooper specification	https://www.auto-data.net/en/mini-convertible-r57-cooper-1.6i-16v-120hp-15326
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414	Auto-Data.net MINI Convertible R57 Cooper S specification	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6-175hp-21563
EU-TOYOTA-IQ-I-HATCHBACK-3D-01	2985	1680	1500	Auto-Data.net Toyota iQ specification	https://www.auto-data.net/en/toyota-iq-1.0-vvt-i-68hp-cvt-3485
EU-CITROEN-XM-Y3-HATCHBACK-5D-01	4709	1793	1385	Automobile-Catalog 1989 Citroen XM 2.0 Injection specification	https://www.automobile-catalog.com/car/1989/64190/citroen_xm_2_0_injection.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3701-3800_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3701-3800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3701-3800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4539 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2089 行）

