# 任务：all 第 1901-2000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0020__08e9bbeb


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-KIA-CERATO-I-LD-SEDAN-01	4480	1735	1470
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1846
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Iveco	Daily iv	55s18w	Pritsche/Fahrgestell	Allrad	Diesel	130	177	Jun 2006	Aug 2011	2024-03-01	129256
Iveco	Daily iv	35s18w	Pritsche/Fahrgestell	Allrad	Diesel	130	177	Jun 2006	Aug 2011	2024-03-01	129257
KIA	Cerato i	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	66	90	Jul 2005	Aug 2006	2024-03-01	129259
Jaguar	F-Type	5.0 Scv8 SVR	Cabriolet	Heckantrieb	Benzin	423	575	May 2015	-	2024-03-01	129271
Iveco	Daily v	Naturalpower 35s14, 35c14, 40c14, 50c14, 65c14, 70c14	Kasten	Heckantrieb	CNG	100	136	Sep 2011	Feb 2014	2024-03-01	129295
Iveco	Daily v	Naturalpower 35s14, 35c14, 40c14, 50c14, 60c14, 65c14,...	Pritsche/Fahrgestell	Heckantrieb	CNG	100	136	Sep 2011	Feb 2014	2024-03-01	129296
Lamborghini	Huracán	5.2 LP 580-2	Targa	Heckantrieb	Benzin	426	579	Nov 2016	-	2024-08-01	129301
Hyundai	I40 i	2.0 GDI	Stufenheck	Frontantrieb	Benzin	130	177	Mar 2012	May 2019	2024-03-01	129307
Lada	Vesta	1.6	Kombi	Frontantrieb	Benzin	78	106	Aug 2017	-	2024-03-01	129309
Lada	Vesta	1.8	Kombi	Frontantrieb	Benzin	90	122	Jul 2016	-	2024-03-01	129310
Lada	Granta	1.6	Schrägheck	Frontantrieb	Benzin	72	98	Aug 2014	-	2024-03-01	129316
Ford	Ecosport	1.5 Tdci Ecoblue 4X4	SUV	Allrad	Diesel	92	125	Nov 2017	-	2024-03-01	129326
KIA	Cerato iii	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	100	136	Aug 2016	Jun 2018	2024-05-01	129327
Aston Martin	Db11 vantage	4.0 V8	Coupe	Heckantrieb	Benzin	375	510	Oct 2017	-	2024-03-01	129341
Aston Martin	Db11 volante	4.0 V8	Cabriolet	Heckantrieb	Benzin	375	510	Oct 2017	-	2024-03-01	129343
Aston Martin	Vantage	V8	Coupe	Heckantrieb	Benzin	375	510	Nov 2017	-	2024-03-01	129344
Jeep	Grand cherokee iv	3.0 CRD V6 4X4	SUV	Allrad	Diesel	160	218	Jan 2011	-	2024-03-01	129356
Mercedes-benz	E-Klasse	E 200 4-matic	Cabriolet	Allrad	Benzin	135	184	Oct 2017	-	2024-03-01	129373
Mercedes-benz	E-Klasse	E 220 D 4-matic	Cabriolet	Allrad	Diesel	143	194	Oct 2017	-	2024-03-01	129379
Mercedes-benz	E-Klasse	E 350 EQ Boost	Cabriolet	Heckantrieb	Benzin/Elektro	220	299	Oct 2017	-	2024-03-01	129383
Opel	Combo tour	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	70	95	Mar 2016	-	2024-03-01	129447
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	434	590	May 2015	Jul 2018	2024-03-01	129448
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	472	642	Oct 2017	Jul 2018	2024-03-01	129449
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	522	710	Jan 2017	May 2018	2024-03-01	129450
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	192	261	Mar 2018	-	2024-03-01	129453
Mercedes-benz	E-Klasse	E 350 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	220	299	Oct 2017	-	2024-03-01	129454
BMW	I8	Hybrid	Coupe	Allrad	Benzin/Elektro	275	374	Mar 2018	Jun 2020	2024-03-01	129466
BMW	I8	Hybrid	Cabriolet	Allrad	Benzin/Elektro	275	374	Mar 2018	Jun 2020	2024-03-01	129467
Bentley	Flying spur	4.0 V8	Stufenheck	Allrad	Benzin	373	507	Mar 2013	Oct 2020	2024-03-01	129483
Pagani	Zonda roadster	7.3	Cabriolet	Heckantrieb	Benzin	499	678	Jun 2009	May 2013	2024-03-01	129486
Pagani	Zonda	7.3	Coupe	Heckantrieb	Benzin	493	670	Jun 2010	May 2013	2024-03-01	129487
VW	Passat b5.5 variant	2.8 4motion	Kombi	Allrad	Benzin	140	190	Oct 2000	May 2005	2024-03-01	129488
VW	Passat b5.5	2.8	Stufenheck	Frontantrieb	Benzin	140	190	Oct 2000	May 2005	2024-03-01	129489
VW	Passat b5.5	2.8 4motion	Stufenheck	Allrad	Benzin	140	190	Oct 2000	May 2005	2024-03-01	129490
Bentley	Flying spur	W12 S 6.0	Stufenheck	Allrad	Benzin	467	635	Nov 2016	-	2024-03-01	129505
Renault	Clio iii	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Aug 2010	Dec 2014	2026-05-01	129510
Bentley	Flying spur	V8 S 4.0	Stufenheck	Allrad	Benzin	388	528	May 2016	-	2024-03-01	129511
Lotus	Elise	CUP 250	Cabriolet	Heckantrieb	Benzin	181	246	Feb 2016	-	2024-03-01	129512
Lotus	Exige	3.5	Cabriolet	Heckantrieb	Benzin	257	349	Jun 2012	Dec 2021	2025-06-01	129518
Lamborghini	Veneno	6.5 Lp750-4 AWD	Targa	Allrad	Benzin	551	749	Sep 2013	-	2024-03-01	129519
Bentley	Continental	6	Coupe	Allrad	Benzin	423	575	Jan 2011	Jul 2018	2024-03-01	129520
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	155	211	Nov 2013	Sep 2014	2024-03-01	129522
Honda	Jazz ii	1.3 Idsi	Schrägheck	Allrad	Benzin	63	86	Mar 2002	Sep 2007	2024-03-01	129526
Maserati	Ghibli	3.0 S	Stufenheck	Heckantrieb	Benzin	316	430	Jul 2017	-	2024-03-01	129536
Maserati	Ghibli	3.0 S Q4	Stufenheck	Allrad	Benzin	316	430	Jul 2017	-	2024-03-01	129538
Maserati	Quattroporte vi	3.0 S	Stufenheck	Heckantrieb	Benzin	316	430	Jul 2017	-	2024-03-01	129539
Maserati	Quattroporte vi	3.0 S Q4	Stufenheck	Allrad	Benzin	316	430	Jul 2017	-	2024-03-01	129540
Smart	Fortwo	Electric Drive	Cabriolet	Heckantrieb	Elektro	60	82	May 2017	-	2024-03-01	129541
Audi	Q2	2.0 Tfsi Quattro	SUV	Allrad	Benzin	140	190	May 2017	-	2024-03-01	129555
Daimler	Super eight	4.2	Stufenheck	Heckantrieb	Benzin	291	395	Sep 2005	Dec 2009	2024-03-01	129561
Citroën	Saxo	1.5 D	Kasten/Schrägheck	Frontantrieb	Diesel	43	58	Jul 2001	Jun 2003	2024-03-01	129574
Volvo	S90 ii	T4	Stufenheck	Frontantrieb	Benzin	140	190	Oct 2017	Dec 2021	2024-05-01	129575
Volvo	S90 ii	T6 AWD	Stufenheck	Allrad	Benzin	228	310	Oct 2017	Dec 2021	2024-05-01	129577
Volvo	S90 ii	T5	Stufenheck	Frontantrieb	Benzin	184	250	Oct 2017	Dec 2021	2024-05-01	129578
Volvo	V90 ii	T5	Kombi	Frontantrieb	Benzin	184	250	Oct 2017	Dec 2021	2024-05-01	129583
Volvo	V90 ii cross country	T5 AWD	Kombi	Allrad	Benzin	184	250	Oct 2017	-	2024-03-01	129586
Volvo	V90 ii	T6 AWD	Kombi	Allrad	Benzin	228	310	Oct 2017	Dec 2021	2024-05-01	129588
Porsche	Cayenne	3.0 AWD	SUV	Allrad	Benzin	250	340	May 2017	May 2023	2026-03-01	129589
Porsche	Cayenne	2.9 S AWD	SUV	Allrad	Benzin	324	441	May 2017	May 2023	2026-03-01	129590
Porsche	Cayenne	4.0 Turbo AWD	SUV	Allrad	Benzin	404	550	May 2017	May 2023	2026-03-01	129591
Volvo	Xc60 ii	T5	SUV	Frontantrieb	Benzin	184	250	Oct 2017	Dec 2020	2024-05-01	129592
Volvo	Xc60 ii	T5 AWD	SUV	Allrad	Benzin	184	250	Oct 2017	Dec 2020	2024-05-01	129593
Volvo	Xc60 ii	T6 AWD	SUV	Allrad	Benzin	228	310	Oct 2017	Dec 2021	2024-05-01	129595
Volvo	Xc90 ii	T6 AWD	SUV	Allrad	Benzin	228	310	Oct 2017	Dec 2021	2024-05-01	129596
Volvo	Xc90 ii	T5 AWD	SUV	Allrad	Benzin	184	250	Oct 2017	Dec 2020	2024-05-01	129597
BMW	X3	Sdrive 20 I	SUV	Heckantrieb	Benzin	135	184	Dec 2017	-	2024-03-01	129611
BMW	X3	Sdrive 20 I 1.6	SUV	Heckantrieb	Benzin	125	170	Dec 2017	-	2024-03-01	129613
BMW	5	530 XI	Stufenheck	Allrad	Benzin	200	272	Mar 2007	Oct 2009	2024-03-01	129618
Peugeot	308 sw ii	2.0 GT Bluehdi 180	Kombi	Frontantrieb	Diesel	130	177	Jun 2017	Jun 2021	2024-03-01	129620
BMW	5	530 XI	Kombi	Allrad	Benzin	200	272	Sep 2006	Sep 2008	2024-03-01	129623
Mercedes-benz	Cls	CLS 450 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	270	367	Dec 2017	-	2024-03-01	129627
Mercedes-benz	Cls	CLS 350 D 4-matic	Coupe	Allrad	Diesel	210	286	Dec 2017	-	2024-03-01	129628
Mercedes-benz	Cls	CLS 400 D 4-matic	Coupe	Allrad	Diesel	250	340	Dec 2017	-	2024-03-01	129629
Hyundai	I30	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2017	-	2024-03-01	129630
Hyundai	I30	1.4 T-gdi	Schrägheck	Frontantrieb	Benzin	103	140	Jun 2017	-	2024-03-01	129631
Land Rover	Discovery v	2.0 SI4 4X4	SUV	Allrad	Benzin	221	300	Sep 2017	-	2024-03-01	129632
BMW	3	M3 2.3	Cabriolet	Heckantrieb	Benzin	158	215	Jun 1988	Oct 1993	2024-03-01	129633
Volvo	V90 ii	T4	Kombi	Frontantrieb	Benzin	140	190	Oct 2017	Dec 2021	2024-05-01	129635
Hyundai	I10 ii	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	69	Sep 2016	Aug 2016	2024-03-01	129636
Lexus	Ls	500	Stufenheck	Heckantrieb	Benzin	310	421	Oct 2017	-	2024-03-01	129638
Suzuki	Swift v	1.4 Sport	Schrägheck	Frontantrieb	Benzin	103	140	Sep 2017	-	2024-03-01	129654
Land Rover	Range rover sport ii	2.0 SI4 4X4	SUV	Allrad	Benzin	221	300	Oct 2017	Mar 2022	2025-02-03	129660
Citroën	C4 cactus	1.2 Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Nov 2017	-	2024-03-01	129687
Mercedes-benz	X-Klasse	X 220 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Sep 2017	-	2024-03-01	129690
Mercedes-benz	X-Klasse	X 250 D 4-matic	Pritsche/Fahrgestell	Allrad	Diesel	140	190	Sep 2017	-	2024-03-01	129693
Koenigsegg	One:1	5.0 Flexfuel	Coupe	Heckantrieb	Benzin/Ethanol	1000	1360	Mar 2014	-	2024-03-01	129694
Mercedes-benz	S-Klasse	S 450 Maybach 4-matic	Stufenheck	Allrad	Benzin	270	367	Sep 2017	Jul 2020	2024-03-01	129707
Peugeot	308 ii	2.0 GT Bluehdi 180	Schrägheck	Frontantrieb	Diesel	130	177	Jun 2017	Jun 2021	2024-03-01	129708
KIA	Cerato koup iii	2.0 Cvvt	Coupe	Frontantrieb	Benzin	118	160	Mar 2016	-	2024-03-01	129735
Seat	Ibiza v	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Dec 2017	-	2024-03-01	129740
KIA	Cee'd	1.0 T-gdi	Kasten/Kombi	Frontantrieb	Benzin	88	120	Apr 2015	Jul 2018	2024-03-01	129746
KIA	Cee'd	1.4 Cvvt	Kasten/Kombi	Frontantrieb	Benzin	73	100	Apr 2015	Jul 2018	2024-03-01	129748
KIA	Cee'd	1.4 Crdi	Kasten/Kombi	Frontantrieb	Diesel	66	90	Apr 2015	Jul 2018	2024-03-01	129751
VW	Polo	1.6 TDI	Schrägheck	Frontantrieb	Diesel	59	80	Nov 2017	Jul 2019	2024-03-01	129754
VW	Polo	1.6 TDI	Schrägheck	Frontantrieb	Diesel	70	95	Nov 2017	Feb 2021	2024-03-01	129755
Land Rover	Range rover iv	5.0 Scv8 4X4	SUV	Allrad	Benzin	386	525	Nov 2017	Sep 2021	2025-02-03	129783
Land Rover	Range rover iv	5.0 Scv8 4X4	SUV	Allrad	Benzin	416	566	Nov 2017	Sep 2021	2025-02-03	129784
VW	Up!	1.0 GTI	Schrägheck	Frontantrieb	Benzin	85	115	Nov 2017	Nov 2023	2024-11-01	129787
Land Rover	Range rover sport ii	5.0 Scv8 4X4	SUV	Allrad	Benzin	386	525	Nov 2017	Mar 2022	2025-02-03	129791
Land Rover	Range rover sport ii	5.0 Scv8 4X4	SUV	Allrad	Benzin	423	575	Nov 2017	Mar 2022	2025-02-03	129792


--- Round 1 / 首次发送 ---
更新点

* 已按缓存优先闭合 26 个 Ktype，其中 6 个 Ktype 直接复用 5 个跨批次既有尺寸组，不重复输出尺寸来源。
* 新建并闭合 8 个共享尺寸组，覆盖 Volvo S90/V90/V90 Cross Country/XC60/XC90、Porsche Cayenne III、Mercedes-Benz CLS C257、Hyundai i30 III。来源页面同时明确了车身形式、门数、三维及不含后视镜宽度。([汽车数据网][1])
* Cayenne III、CLS C257 和 i30 III 的三维分别闭合为 `4918×1983×1696`、`4988×1890×1435`、`4340×1795×1455` mm。([汽车数据网][2])

当前批次进度

* 输入 Ktype：100
* READY 输入：26
* PENDING 输入：74
* READY 映射行：26
* 当前已引用尺寸组：13
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129326	129326	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	2017年改款五门SUV外廓，复用既有组。	READY
129327	129327	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH	YD四门改款轿车外廓，复用既有组。	READY
129575	129575	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轴距四门轿车外廓。	READY
129577	129577	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	驱动形式不改变标准车身外廓。	READY
129578	129578	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	发动机版本不改变标准车身外廓。	READY
129583	129583	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90第二代标准旅行车外廓。	READY
129586	129586	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country车身高度与标准V90不同。	READY
129588	129588	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	四驱及发动机版本不改变标准旅行车外廓。	READY
129589	129589	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA五门SUV标准外廓。	READY
129590	129590	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	S版本动力差异不改变本批标准SUV外廓。	READY
129591	129591	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	Turbo动力版本复用相同标准车身外廓。	READY
129592	129592	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60第二代五门标准SUV外廓。	READY
129593	129593	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	四驱形式不改变标准车身外廓。	READY
129595	129595	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	T6动力版本不改变标准车身外廓。	READY
129596	129596	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90第二代五门SUV外廓。	READY
129597	129597	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	T5与T6动力差异不改变标准车身外廓。	READY
129627	129627	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门轿跑车外廓。	READY
129628	129628	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	柴油动力版本复用C257标准外廓。	READY
129629	129629	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	柴油动力版本复用C257标准外廓。	READY
129630	129630	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背车标准外廓。	READY
129631	129631	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	发动机版本不改变PD五门掀背外廓。	READY
129632	129632	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH	L462五门SUV外廓，复用既有组。	READY
129660	129660	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	2017年改款L494外廓，复用既有组。	READY
129740	129740	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH	KJ1五门掀背车外廓，复用既有组。	READY
129791	129791	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款L494 V8版本复用既有外廓。	READY
129792	129792	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	SVR动力版本当前映射至已确认改款L494外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Auto-Data	https://www.auto-data.net/en/volvo-s90-2016-2.0-t4-190hp-automatic-35847
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data	https://www.auto-data.net/en/volvo-v90-2016-2.0-t5-250hp-automatic-32886
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Auto-Data	https://www.auto-data.net/en/volvo-v90-cross-country-generation-5155
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-3.0-v6-340hp-tiptronic-s-31653
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data	https://www.auto-data.net/en/volvo-xc60-ii-2.0-t5-250hp-automatic-32776
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Auto-Data	https://www.auto-data.net/en/volvo-xc90-ii-2.0-t6-310hp-awd-automatic-36309
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-cls-450-367hp-eq-boost-4matic-9g-tronic-32272
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-1.4-t-gdi-140hp-25965
```

下一步优先处理

1. 批量闭合共用率较高的 Bentley Continental/Flying Spur、Volvo XC90 I、Maserati Ghibli/Quattroporte、Mercedes-Benz E-Class C238/A238。
2. 处理 BMW E60/E61、G01 X3、Peugeot 308 II/SW、VW Passat B5.5 等单一标准外廓。
3. 最后集中拆分 Iveco Daily IV/V、Mercedes-Benz X-Class 等可能涉及轴距、车顶、驾驶室或底盘长度的多外廓 Ktype。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-s90-2016-2.0-t4-190hp-automatic-35847 "Volvo S90 (2016) 2.0 T4 (190 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/porsche-cayenne-iii-3.0-v6-340hp-tiptronic-s-31653 "Porsche Cayenne III 3.0 V6 (340 Hp) Tiptronic S | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **43 个 READY 映射**，首次创建并闭合 **31 个尺寸组**。
* 已批量闭合 Mercedes-Benz E-Class A238/C238、Bentley Flying Spur II、Maserati Ghibli/Quattroporte、BMW X3 G01/E60/E61 等共享物理外廓。([汽车数据网][1])
* Ktype `129754`、`129755` 直接关联既有 `EU-VW-POLO-VI-HATCHBACK-TSI-01`，本轮不重复输出该尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**69**
* PENDING 映射：**31**
* 当前已引用尺寸组：**45**
* 本轮首次创建尺寸组：**31**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129271	129271	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	HIGH	SVR双门敞篷外廓。	READY
129301	129301	Convertible	Huracán LP 580-2 Spyder		2	EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	HIGH	LP 580-2 Spyder双门敞篷外廓。	READY
129307	129307	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	VF四门轿车外廓。	READY
129316	129316	Hatchback	Granta I		5	EU-LADA-GRANTA-I-HATCHBACK-01	HIGH	五门掀背车外廓。	READY
129341	129341	Coupe	DB11		2	EU-ASTON-MARTIN-DB11-COUPE-01	HIGH	DB11双门硬顶外廓。	READY
129343	129343	Convertible	DB11 Volante		2	EU-ASTON-MARTIN-DB11-VOLANTE-CONVERTIBLE-01	HIGH	Volante双门敞篷外廓。	READY
129344	129344	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	HIGH	2018代双门硬顶外廓。	READY
129356	129356	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-01	HIGH	WK2五门SUV外廓。	READY
129373	129373	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129379	129379	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129383	129383	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129447	129447	MPV	Combo Tour D		5	EU-OPEL-COMBO-D-TOUR-MPV-01	HIGH	Combo Tour D五门乘用型外廓。	READY
129453	129453	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH	初期标准四门轿车外廓。	READY
129454	129454	Coupe	E-Class Coupe C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH	C238双门轿跑外廓。	READY
129466	129466	Coupe	i8 LCI	I12	2	EU-BMW-I8-I12-LCI-COUPE-01	HIGH	I12改款双门硬顶外廓。	READY
129467	129467	Convertible	i8 Roadster	I15	2	EU-BMW-I8-I15-ROADSTER-01	HIGH	I15双门敞篷外廓。	READY
129483	129483	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	第二代四门轿车标准外廓。	READY
129488	129488	Wagon	Passat B5.5 Variant	3BG	5	EU-VW-PASSAT-B5-5-3BG-WAGON-01	HIGH	3BG五门旅行车外廓。	READY
129489	129489	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-3BG-SEDAN-01	HIGH	3BG四门轿车外廓。	READY
129490	129490	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-3BG-SEDAN-01	HIGH	3BG四门轿车外廓。	READY
129505	129505	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	W12 S四门轿车标准外廓。	READY
129511	129511	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	V8 S四门轿车标准外廓。	READY
129536	129536	Sedan	Ghibli III facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157改款四门轿车外廓。	READY
129538	129538	Sedan	Ghibli III facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157改款四门轿车外廓。	READY
129539	129539	Sedan	Quattroporte VI facelift	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	HIGH	M156改款四门轿车外廓。	READY
129540	129540	Sedan	Quattroporte VI facelift	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	HIGH	M156改款四门轿车外廓。	READY
129541	129541	Convertible	Fortwo III Cabrio	A453	2	EU-SMART-FORTWO-III-A453-CONVERTIBLE-EV-01	HIGH	A453双门电动敞篷外廓。	READY
129555	129555	SUV	Q2	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH	GA五门SUV外廓。	READY
129611	129611	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01五门SUV标准外廓。	READY
129613	129613	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	MEDIUM	G01五门SUV标准外廓。	READY
129618	129618	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-SEDAN-FACELIFT-01	HIGH	E60改款四门轿车外廓。	READY
129620	129620	Wagon	308 SW II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	T9改款五门旅行车外廓。	READY
129623	129623	Wagon	5 Series Touring E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH	E61五门旅行车外廓。	READY
129636	129636	Hatchback	i10 II facelift		5	EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	HIGH	改款五门掀背外廓；输入日期字段倒置。	READY
129638	129638	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50四门标准轴距轿车外廓。	READY
129654	129654	Hatchback	Swift VI Sport		5	EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	HIGH	Swift VI Sport五门外廓；输入代际标签修正。	READY
129708	129708	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背外廓。	READY
129735	129735	Coupe	Cerato III Koup	YD	2	EU-KIA-CERATO-III-YD-KOUP-01	HIGH	YD双门Koup外廓。	READY
129746	129746	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129748	129748	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129751	129751	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129754	129754	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1五门标准外廓。	READY
129755	129755	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1五门标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	4475	1923	1308	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-convertible-svr-5.0-v8-575hp-awd-automatic-27244
EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	4459	1924	1180	Auto-Data	https://www.auto-data.net/en/lamborghini-huracan-lp-580-2-spyder-generation-8857
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470	Auto-Data	https://www.auto-data.net/en/hyundai-i40-sedan-2.0-gdi-177hp-18567
EU-LADA-GRANTA-I-HATCHBACK-01	4246	1700	1500	Auto-Data	https://www.auto-data.net/en/lada-granta-i-hatchback-1.6-16v-98hp-automatic-24201
EU-ASTON-MARTIN-DB11-COUPE-01	4750	1950	1290	Auto-Data	https://www.auto-data.net/en/aston-martin-db11-generation-4901
EU-ASTON-MARTIN-DB11-VOLANTE-CONVERTIBLE-01	4750	1950	1300	Auto-Data	https://www.auto-data.net/en/aston-martin-db11-volante-generation-6058
EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	4490	1942	1274	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-2018-generation-5998
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-01	4822	1943	1781	Auto-Data	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-3.0-crd-190hp-4x4-automatic-31162
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-220d-194hp-4matic-9g-tronic-33168
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845	Auto-Data	https://www.auto-data.net/bg/opel-combo-model-238
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443	Auto-Data	https://www.auto-data.net/en/tesla-model-3-long-range-75-kwh-287hp-32648
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	4826	1860	1430	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748
EU-BMW-I8-I12-LCI-COUPE-01	4689	1942	1293	Auto-Data	https://www.auto-data.net/en/bmw-i8-coupe-i12-lci-generation-6016
EU-BMW-I8-I15-ROADSTER-01	4689	1942	1291	Auto-Data	https://www.auto-data.net/en/bmw-i8-roadster-i15-generation-6017
EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	5299	1976	1488	Auto-Data	https://www.auto-data.net/en/bentley-flying-spur-ii-facelift-2015-4.0-v8-507hp-awd-automatic-22862
EU-VW-PASSAT-B5-5-3BG-WAGON-01	4682	1746	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b5.5-2.8-30v-v6-193hp-4motion-43107
EU-VW-PASSAT-B5-5-3BG-SEDAN-01	4703	1746	1462	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b5.5-1.6-102hp-43379
EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	4971	1945	1461	Auto-Data	https://www.auto-data.net/en/maserati-ghibli-iii-m157-facelift-2017-s-3.0-v6-430hp-automatic-27243
EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	5262	1948	1481	Auto-Data	https://www.auto-data.net/en/maserati-quattroporte-vi-m156-facelift-2016-s-q4-3.0-gdi-430hp-awd-automatic-32650
EU-SMART-FORTWO-III-A453-CONVERTIBLE-EV-01	2695	1663	1553	Auto-Data	https://www.auto-data.net/en/smart-fortwo-iii-cabrio-a453-17.6-kwh-82hp-electric-drive-32739
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Auto-Data	https://www.auto-data.net/en/audi-q2-2.0-tfsi-190hp-quattro-s-tronic-22876
EU-BMW-X3-G01-SUV-01	4708	1891	1676	Auto-Data	https://www.auto-data.net/en/bmw-x3-g01-20i-184hp-sdrive-steptronic-51143
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468	Auto-Data	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-530i-272hp-9607
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-sw-ii-phase-ii-2017-gt-2.0-bluehdi-180hp-automatic-32062
EU-BMW-5-E61-WAGON-01	4843	1846	1491	Auto-Data;Auto-Data	https://www.auto-data.net/en/bmw-5-series-touring-e61-530xi-258hp-9623;https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-530i-272hp-xdrive-steptronic-28288
EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	3665	1660	1500	Auto-Data	https://www.auto-data.net/en/hyundai-i10-ii-facelift-2016-1.0-lpg-69-67hp-29506
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450	Auto-Data	https://www.auto-data.net/fr/lexus-ls-v-500-v6-420hp-awd-automatic-28869
EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	3890	1735	1495	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-sport-1.4-140hp-automatic-32531
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-ii-phase-ii-2017-generation-5518
EU-KIA-CERATO-III-YD-KOUP-01	4530	1780	1410	Auto-Data	https://www.auto-data.net/ro/kia-cerato-model-275
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485	Auto-Data	https://www.auto-data.net/en/kia-ceed-model-1935
```

## 下一步优先处理

1. 闭合 Bentley Continental GT/GTC 的标准版、Speed、Supersports 外廓差异。
2. 集中拆分 Iveco Daily IV/V 与 Mercedes-Benz X-Class 的轴距、底盘、车顶和驾驶室分支。
3. 处理 Pagani、Lotus、Lamborghini Veneno、Koenigsegg 等低复用特殊车身，以及 Clio/Saxo 商用厢式分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bentley-flying-spur-ii-facelift-2015-4.0-v8-507hp-awd-automatic-22862?utm_source=chatgpt.com "Bentley Flying Spur II (facelift 2015) 4.0 V8 (507 Hp) AWD ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **26 个 READY 输入 Ktype、27 条 READY 映射**，首次创建 **21 个尺寸组**。
* `129520` 关联既有 Bentley Continental GT II 双门硬顶组；`129635` 关联上一轮已闭合的 Volvo V90 II 旅行车组，不重复输出尺寸组。
* `129787` 覆盖三门和五门 `up! GTI`，拆分为两个派生 `id`，但二者外廓相同，共用一个尺寸组。该车型确有三门和五门版本。([VW Press][1])
* 当前仅剩 4 个 Iveco Daily 多轴距/底盘 Ktype，以及 1 个跨多个外廓时期的 Honda Fit/Jazz GD2 Ktype。

## 当前批次进度

* 输入 Ktype：**100**
* READY 输入：**95**
* PENDING 输入：**5**
* READY 映射行：**96**
* 已确认且被引用尺寸组：**66**
* 本轮首次创建尺寸组：**21**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129259	129259	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-01	HIGH	LD五门掀背车外廓。	READY
129309	129309	Wagon	Vesta I SW		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW五门旅行车外廓。	READY
129310	129310	Wagon	Vesta I SW		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW五门旅行车外廓。	READY
129448	129448	Convertible	Continental GTC II facelift		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	HIGH	改款标准版双门敞篷外廓。	READY
129449	129449	Convertible	Continental GTC II facelift Speed		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	HIGH	Speed双门敞篷外廓。	READY
129450	129450	Convertible	Continental GTC II facelift Supersports		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	HIGH	Supersports专属外部套件外廓。	READY
129486	129486	Convertible	Zonda Cinque Roadster		2	EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	HIGH	Cinque Roadster双门敞篷外廓。	READY
129487	129487	Coupe	Zonda Cinque		2	EU-PAGANI-ZONDA-CINQUE-COUPE-01	HIGH	Cinque双门硬顶外廓。	READY
129510	129510	Van	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-VAN-3D-01	HIGH	三门掀背式商用厢车外廓。	READY
129512	129512	Convertible	Elise Series 3 Cup 250		2	EU-LOTUS-ELISE-SERIES-3-CUP-250-CONVERTIBLE-01	HIGH	Cup 250双门敞篷外廓。	READY
129518	129518	Convertible	Exige Series 3 S Roadster		2	EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	HIGH	第三代S Roadster双门敞篷外廓。	READY
129519	129519	Convertible	Veneno Roadster		2	EU-LAMBORGHINI-VENENO-ROADSTER-CONVERTIBLE-01	HIGH	Veneno Roadster双门开放式外廓。	READY
129520	129520	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH	第二代双门硬顶标准车身外廓。	READY
129522	129522	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-01	MEDIUM	第一代改款五门SUV外廓。	READY
129561	129561	Sedan	Super Eight	X350	4	EU-DAIMLER-SUPER-EIGHT-X350-SEDAN-01	HIGH	X350长轴距四门轿车外廓。	READY
129574	129574	Van	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-VAN-3D-01	HIGH	三门掀背式商用厢车外廓。	READY
129633	129633	Convertible	M3 E30	E30	2	EU-BMW-M3-E30-CONVERTIBLE-01	HIGH	E30 M3双门敞篷外廓。	READY
129635	129635	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90第二代五门标准旅行车外廓。	READY
129687	129687	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	第一代改款五门车身外廓。	READY
129690	129690	Pickup	X-Class	W470	4	EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	HIGH	W470双排座皮卡标准外廓。	READY
129693	129693	Pickup	X-Class	W470	4	EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	HIGH	W470双排座皮卡标准外廓。	READY
129694	129694	Coupe	One:1		2	EU-KOENIGSEGG-ONE-1-COUPE-01	HIGH	One:1双门硬顶宽体外廓。	READY
129707	129707	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-FACELIFT-SEDAN-01	MEDIUM	X222改款长轴距Maybach四门外廓。	READY
129783	129783	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH	L405改款标准轴距五门SUV外廓。	READY
129784	129784	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH	SVAutobiography Dynamic标准轴距外廓。	READY
129787_3dr	129787	Hatchback	up! I facelift		3	EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	HIGH	up! GTI三门物理分支。	READY
129787_5dr	129787	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	HIGH	up! GTI五门物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CERATO-I-LD-HATCHBACK-01	4340	1735	1470	CarFolio	https://www.carfolio.com/kia-cerato-1.5-crdi-hatchback-130680
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512	Auto-Data	https://www.auto-data.net/en/lada-vesta-sw-1.8-122hp-automatic-30842
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-6.0-w12-590hp-awd-automatic-22847
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-speed-6.0-635hp-awd-automatic-22860
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-supersport-6.0-w12-710hp-awd-automatic-30311
EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	4435	2055	1141	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2549810/pagani_zonda_cinque_roadster.html
EU-PAGANI-ZONDA-CINQUE-COUPE-01	4435	2055	1141	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/2549795/pagani_zonda_cinque.html
EU-RENAULT-CLIO-III-PHASE-II-VAN-3D-01	4032	1720	1497	Auto-Data	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-1.5-dci-75hp-fap-10408
EU-LOTUS-ELISE-SERIES-3-CUP-250-CONVERTIBLE-01	3824	1719	1117	Auto-Data	https://www.auto-data.net/en/lotus-elise-series-3-cup-250-1.8-246hp-24356
EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	4084	1802	1129	Auto-Data	https://www.auto-data.net/en/lotus-exige-iii-s-roadster-sport-350-3.5-v6-350hp-21318
EU-LAMBORGHINI-VENENO-ROADSTER-CONVERTIBLE-01	5020	2075	1165	Auto-Data	https://www.auto-data.net/en/lamborghini-veneno-lp-750-4-roadster-6.5-v12-750hp-43241
EU-VOLVO-XC90-I-FACELIFT-SUV-01	4807	1936	1784	Auto-Data	https://www.auto-data.net/en/volvo-xc90-facelift-2007-2.4-d5-200hp-awd-automatic-18204
EU-DAIMLER-SUPER-EIGHT-X350-SEDAN-01	5215	1898	1448	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1289360/daimler_super_eight.html
EU-CITROEN-SAXO-PHASE-II-VAN-3D-01	3718	1595	1360	Auto-Data	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.5-d-57hp-44815
EU-BMW-M3-E30-CONVERTIBLE-01	4345	1680	1370	Auto-Data	https://www.auto-data.net/en/bmw-m3-convertible-e30-2.3-215hp-cat-9885
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480	Auto-Data	https://www.auto-data.net/en/citroen-c4-cactus-phase-ii-2018-1.2-puretech-130hp-39020
EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	5340	1920	1819	Auto-Data	https://www.auto-data.net/en/mercedes-benz-x-class-x-220d-163hp-31024
EU-KOENIGSEGG-ONE-1-COUPE-01	4500	2060	1150	Koenigsegg official technical specifications	https://www.koenigsegg.com/technical-specifications-one1
EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-FACELIFT-SEDAN-01	5462	1899	1498	Auto-Data	https://www.auto-data.net/en/mercedes-benz-maybach-s-class-x222-facelift-2017-generation-5472
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869	Auto-Data;CarExpert	https://www.auto-data.net/en/land-rover-range-rover-iv-facelift-2017-5.0-v8-525hp-awd-automatic-supercharged-31385;https://www.carexpert.com.au/land-rover/range-rover/2018-svautobiography-dynamic/features-and-specs
EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	3600	1641	1504	Volkswagen UK official press kit	https://www.vwpress.co.uk/press-kits/258
```

## 下一步优先处理

1. 按驾驶室、轴距和底盘总长拆分 `129256`、`129257` 两个 Daily IV 四驱底盘 Ktype。
2. 按轴距与车顶高度闭合 `129295` Daily V NaturalPower 厢式车，并拆分 `129296` 底盘车分支。
3. 确认 `129526` Honda Fit/Jazz GD2 4WD 覆盖的改款前后外廓边界，创建稳定派生行后直接进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.vwpress.co.uk/press-kits/258?utm_source=chatgpt.com "up! GTI - VW Press UK"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Iveco Daily IV `35S18W`、`55S18W` 四驱单排底盘的短轴和中轴分支；两种载重级别的车高不同，分别建立尺寸组。Iveco 规格表列明两者均有 3050 mm 与 3400 mm 两种轴距。([yumpu.com][1])
* `129526` 对应 Honda Fit/Jazz `GD2` 四驱五门车型，生产区间跨越改款前后，拆分为 `prefl` 和 `facelift`。改款前后长度分别为 3830 mm 和 3845 mm，宽度与高度保持 1675 mm、1550 mm。([日本汽车交易所][2])
* 当前仅剩两个 Iveco Daily V NaturalPower 聚合 Ktype 尚未闭合。

## 当前批次进度

* 输入 Ktype：98 READY，2 PENDING
* READY 映射行：102
* PENDING 映射：2
* 已确认且被引用尺寸组：72
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129256_swb	129256	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘分支。	READY
129256_mwb	129256	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘分支。	READY
129257_swb	129257	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘分支。	READY
129257_mwb	129257	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘分支。	READY
129526_prefl	129526	Hatchback	Fit I / Jazz II	GD2	5	EU-HONDA-FIT-I-GD2-HATCHBACK-PREFL-01	HIGH	GD2四驱五门改款前外廓。	READY
129526_facelift	129526	Hatchback	Fit I / Jazz II	GD2	5	EU-HONDA-FIT-I-GD2-HATCHBACK-FACELIFT-01	HIGH	GD2四驱五门改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-SWB-01	4921	2016	2644	Iveco Daily 55S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390121/daily-55s18w-4x4-chassis-cab
EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-MWB-01	5432	2016	2634	Iveco Daily 55S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390121/daily-55s18w-4x4-chassis-cab
EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-SWB-01	4921	2016	2635	Iveco Daily 35S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390142/daily-35s18w-4x4-chassis-cabpmd/2
EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-MWB-01	5432	2016	2627	Iveco Daily 35S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390142/daily-35s18w-4x4-chassis-cabpmd/2
EU-HONDA-FIT-I-GD2-HATCHBACK-PREFL-01	3830	1675	1550	JapaneseCarTrade Honda Fit LA-GD2 specification	https://cars.japanesecartrade.com/detail/honda/fit/a/162412
EU-HONDA-FIT-I-GD2-HATCHBACK-FACELIFT-01	3845	1675	1550	JapaneseCarTrade Honda Fit DBA-GD2 specification	https://cars.japanesecartrade.com/detail/honda/fit/1.3a/162346
```

## 下一步优先处理

1. 按官方 NaturalPower 车型矩阵拆分 `129295` 的轴距、车顶高度和载重级别分支。
2. 按单排底盘轴距及不同载重级别闭合 `129296`。
3. 两项闭合后立即执行一次映射引用、唯一性、字段完整性和下载文件检查，并输出最终完整快照。

推进信号：CONTINUE

[1]: https://www.yumpu.com/en/document/view/21390142/daily-35s18w-4x4-chassis-cabpmd/2 "DAILY <strong>35S18W</str"
[2]: https://cars.japanesecartrade.com/detail/honda/fit/a/162412 "Honda Fit A 2002/11 Engine, Suspension and Price Specifications | JapaneseCarTrade.com"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后两个 Iveco Daily V NaturalPower 聚合 Ktype 已完成拆分：`129295` 拆为 7 个厢式车外廓，`129296` 拆为 14 个底盘驾驶室外廓，覆盖载重级别、单/双后轮、驾驶室和轴距差异。([CarsGuide][1])
* 已完成一次轻量机械检查：表头列数正确、`id` 和 `DIMENSION_GROUP_ID` 唯一、所有映射引用闭合、尺寸和来源字段完整、无孤立尺寸组。
* 当前批次 `PENDING=0`，以下为可直接落盘的最终完整快照。

## 当前批次进度

* 输入 Ktype：100
* READY 输入：100
* PENDING 输入：0
* 最终 Ktype 映射行：123
* 最终 DIMENSION_GROUP：94
* 映射表列数：10
* DIMENSION_GROUP 表列数：6

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129256_swb	129256	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘分支。	READY
129256_mwb	129256	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘分支。	READY
129257_swb	129257	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘分支。	READY
129257_mwb	129257	Pickup	Daily IV 4x4		2	EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘分支。	READY
129259	129259	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-01	HIGH	LD五门掀背车外廓。	READY
129271	129271	Convertible	F-Type X152	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	HIGH	SVR双门敞篷外廓。	READY
129295_swb_low_srw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-SWB-LOW-SRW-01	MEDIUM	短轴低顶单后轮厢式分支。	READY
129295_mwb_mid_srw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-SRW-01	MEDIUM	中轴中顶单后轮厢式分支。	READY
129295_lwb_mid_srw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-SRW-01	MEDIUM	长轴中顶单后轮厢式分支。	READY
129295_mwb_mid_drw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-DRW-01	MEDIUM	中轴中顶双后轮厢式分支。	READY
129295_lwb_mid_drw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-DRW-01	MEDIUM	长轴中顶双后轮厢式分支。	READY
129295_lwb_high_drw	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-DRW-01	MEDIUM	长轴高顶双后轮厢式分支。	READY
129295_lwb_high_70c	129295	Van	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-70C-01	MEDIUM	70C长轴高顶厢式分支。	READY
129296_35s_swb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-SWB-01	HIGH	35S短轴单排底盘分支。	READY
129296_35s_lwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-LWB-01	HIGH	35S长轴单排底盘分支。	READY
129296_35c_swb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-SWB-01	HIGH	35C短轴单排底盘分支。	READY
129296_35c_lwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-LWB-01	HIGH	35C长轴单排底盘分支。	READY
129296_35c_crew	129296	Pickup	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-CREW-01	HIGH	35C双排驾驶室底盘分支。	READY
129296_50c_swb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-SWB-01	HIGH	50C短轴单排底盘分支。	READY
129296_50c_mwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-MWB-01	HIGH	50C中轴单排底盘分支。	READY
129296_50c_lwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-LWB-01	HIGH	50C长轴单排底盘分支。	READY
129296_50c_crew	129296	Pickup	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-CREW-01	HIGH	50C双排驾驶室底盘分支。	READY
129296_heavy_swb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-SWB-01	HIGH	65C/70C短轴单排底盘分支。	READY
129296_heavy_mwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-MWB-01	HIGH	65C/70C中轴单排底盘分支。	READY
129296_heavy_lwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-LWB-01	HIGH	65C/70C长轴单排底盘分支。	READY
129296_heavy_xlwb	129296	Pickup	Daily V NaturalPower		2	EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-XLWB-01	HIGH	65C/70C超长轴单排底盘分支。	READY
129296_heavy_crew	129296	Pickup	Daily V NaturalPower		4	EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-CREW-01	HIGH	65C/70C双排驾驶室底盘分支。	READY
129301	129301	Convertible	Huracán LP 580-2 Spyder		2	EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	HIGH	LP 580-2 Spyder双门敞篷外廓。	READY
129307	129307	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	VF四门轿车外廓。	READY
129309	129309	Wagon	Vesta I SW		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW五门旅行车外廓。	READY
129310	129310	Wagon	Vesta I SW		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW五门旅行车外廓。	READY
129316	129316	Hatchback	Granta I		5	EU-LADA-GRANTA-I-HATCHBACK-01	HIGH	五门掀背车外廓。	READY
129326	129326	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	2017年改款五门SUV外廓。	READY
129327	129327	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH	YD四门改款轿车外廓。	READY
129341	129341	Coupe	DB11		2	EU-ASTON-MARTIN-DB11-COUPE-01	HIGH	DB11双门硬顶外廓。	READY
129343	129343	Convertible	DB11 Volante		2	EU-ASTON-MARTIN-DB11-VOLANTE-CONVERTIBLE-01	HIGH	Volante双门敞篷外廓。	READY
129344	129344	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	HIGH	2018代双门硬顶外廓。	READY
129356	129356	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-01	HIGH	WK2五门SUV外廓。	READY
129373	129373	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129379	129379	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129383	129383	Convertible	E-Class Cabriolet A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	HIGH	A238双门敞篷外廓。	READY
129447	129447	MPV	Combo Tour D		5	EU-OPEL-COMBO-D-TOUR-MPV-01	HIGH	Combo Tour D五门乘用型外廓。	READY
129448	129448	Convertible	Continental GTC II facelift		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	HIGH	改款标准版双门敞篷外廓。	READY
129449	129449	Convertible	Continental GTC II facelift Speed		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	HIGH	Speed双门敞篷外廓。	READY
129450	129450	Convertible	Continental GTC II facelift Supersports		2	EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	HIGH	Supersports专属外部套件外廓。	READY
129453	129453	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH	初期标准四门轿车外廓。	READY
129454	129454	Coupe	E-Class Coupe C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	HIGH	C238双门轿跑外廓。	READY
129466	129466	Coupe	i8 LCI	I12	2	EU-BMW-I8-I12-LCI-COUPE-01	HIGH	I12改款双门硬顶外廓。	READY
129467	129467	Convertible	i8 Roadster	I15	2	EU-BMW-I8-I15-ROADSTER-01	HIGH	I15双门敞篷外廓。	READY
129483	129483	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	第二代四门轿车标准外廓。	READY
129486	129486	Convertible	Zonda Cinque Roadster		2	EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	HIGH	Cinque Roadster双门敞篷外廓。	READY
129487	129487	Coupe	Zonda Cinque		2	EU-PAGANI-ZONDA-CINQUE-COUPE-01	HIGH	Cinque双门硬顶外廓。	READY
129488	129488	Wagon	Passat B5.5 Variant	3BG	5	EU-VW-PASSAT-B5-5-3BG-WAGON-01	HIGH	3BG五门旅行车外廓。	READY
129489	129489	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-3BG-SEDAN-01	HIGH	3BG四门轿车外廓。	READY
129490	129490	Sedan	Passat B5.5	3BG	4	EU-VW-PASSAT-B5-5-3BG-SEDAN-01	HIGH	3BG四门轿车外廓。	READY
129505	129505	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	第二代四门轿车标准外廓。	READY
129510	129510	Van	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-VAN-3D-01	HIGH	三门掀背式商用厢车外廓。	READY
129511	129511	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	HIGH	第二代四门轿车标准外廓。	READY
129512	129512	Convertible	Elise Series 3 Cup 250		2	EU-LOTUS-ELISE-SERIES-3-CUP-250-CONVERTIBLE-01	HIGH	Cup 250双门敞篷外廓。	READY
129518	129518	Convertible	Exige Series 3 S Roadster		2	EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	HIGH	第三代S Roadster双门敞篷外廓。	READY
129519	129519	Convertible	Veneno Roadster		2	EU-LAMBORGHINI-VENENO-ROADSTER-CONVERTIBLE-01	HIGH	Veneno Roadster双门开放式外廓。	READY
129520	129520	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH	第二代双门硬顶标准车身外廓。	READY
129522	129522	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-01	MEDIUM	第一代改款五门SUV外廓。	READY
129526_prefl	129526	Hatchback	Fit I / Jazz II	GD2	5	EU-HONDA-FIT-I-GD2-HATCHBACK-PREFL-01	HIGH	GD2四驱五门改款前外廓。	READY
129526_facelift	129526	Hatchback	Fit I / Jazz II	GD2	5	EU-HONDA-FIT-I-GD2-HATCHBACK-FACELIFT-01	HIGH	GD2四驱五门改款后外廓。	READY
129536	129536	Sedan	Ghibli III facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157改款四门轿车外廓。	READY
129538	129538	Sedan	Ghibli III facelift	M157	4	EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	HIGH	M157改款四门轿车外廓。	READY
129539	129539	Sedan	Quattroporte VI facelift	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	HIGH	M156改款四门轿车外廓。	READY
129540	129540	Sedan	Quattroporte VI facelift	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	HIGH	M156改款四门轿车外廓。	READY
129541	129541	Convertible	Fortwo III Cabrio	A453	2	EU-SMART-FORTWO-III-A453-CONVERTIBLE-EV-01	HIGH	A453双门电动敞篷外廓。	READY
129555	129555	SUV	Q2	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH	GA五门SUV外廓。	READY
129561	129561	Sedan	Super Eight	X350	4	EU-DAIMLER-SUPER-EIGHT-X350-SEDAN-01	HIGH	X350长轴距四门轿车外廓。	READY
129574	129574	Van	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-VAN-3D-01	HIGH	三门掀背式商用厢车外廓。	READY
129575	129575	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轴距四门轿车外廓。	READY
129577	129577	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轴距四门轿车外廓。	READY
129578	129578	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轴距四门轿车外廓。	READY
129583	129583	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90第二代标准旅行车外廓。	READY
129586	129586	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country车身高度与标准V90不同。	READY
129588	129588	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90第二代标准旅行车外廓。	READY
129589	129589	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA五门SUV标准外廓。	READY
129590	129590	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA五门SUV标准外廓。	READY
129591	129591	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA五门SUV标准外廓。	READY
129592	129592	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60第二代五门标准SUV外廓。	READY
129593	129593	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60第二代五门标准SUV外廓。	READY
129595	129595	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60第二代五门标准SUV外廓。	READY
129596	129596	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90第二代五门SUV外廓。	READY
129597	129597	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90第二代五门SUV外廓。	READY
129611	129611	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01五门SUV标准外廓。	READY
129613	129613	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	MEDIUM	G01五门SUV标准外廓。	READY
129618	129618	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-SEDAN-FACELIFT-01	HIGH	E60改款四门轿车外廓。	READY
129620	129620	Wagon	308 SW II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	T9改款五门旅行车外廓。	READY
129623	129623	Wagon	5 Series Touring E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH	E61五门旅行车外廓。	READY
129627	129627	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门轿跑车外廓。	READY
129628	129628	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门轿跑车外廓。	READY
129629	129629	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门轿跑车外廓。	READY
129630	129630	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背车标准外廓。	READY
129631	129631	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背车标准外廓。	READY
129632	129632	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH	L462五门SUV外廓。	READY
129633	129633	Convertible	M3 E30	E30	2	EU-BMW-M3-E30-CONVERTIBLE-01	HIGH	E30 M3双门敞篷外廓。	READY
129635	129635	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90第二代五门标准旅行车外廓。	READY
129636	129636	Hatchback	i10 II facelift		5	EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	HIGH	改款五门掀背外廓；输入日期字段倒置。	READY
129638	129638	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50四门标准轴距轿车外廓。	READY
129654	129654	Hatchback	Swift VI Sport		5	EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	HIGH	Swift VI Sport五门外廓；输入代际标签修正。	READY
129660	129660	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	2017年改款L494五门SUV外廓。	READY
129687	129687	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	第一代改款五门车身外廓。	READY
129690	129690	Pickup	X-Class	W470	4	EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	HIGH	W470双排座皮卡标准外廓。	READY
129693	129693	Pickup	X-Class	W470	4	EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	HIGH	W470双排座皮卡标准外廓。	READY
129694	129694	Coupe	One:1		2	EU-KOENIGSEGG-ONE-1-COUPE-01	HIGH	One:1双门硬顶宽体外廓。	READY
129707	129707	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-FACELIFT-SEDAN-01	MEDIUM	X222改款长轴距Maybach四门外廓。	READY
129708	129708	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背外廓。	READY
129735	129735	Coupe	Cerato III Koup	YD	2	EU-KIA-CERATO-III-YD-KOUP-01	HIGH	YD双门Koup外廓。	READY
129740	129740	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH	KJ1五门掀背车外廓。	READY
129746	129746	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129748	129748	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129751	129751	Van	Cee'd II facelift commercial wagon	JD	5	EU-KIA-CEED-II-JD-VAN-FACELIFT-01	HIGH	JD五门商用厢式外廓。	READY
129754	129754	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1五门标准外廓。	READY
129755	129755	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1五门标准外廓。	READY
129783	129783	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH	L405改款标准轴距五门SUV外廓。	READY
129784	129784	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH	L405改款标准轴距五门SUV外廓。	READY
129787_3dr	129787	Hatchback	up! I facelift		3	EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	HIGH	up! GTI三门物理分支。	READY
129787_5dr	129787	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	HIGH	up! GTI五门物理分支。	READY
129791	129791	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款L494五门SUV外廓。	READY
129792	129792	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款L494五门SUV外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1901-2000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-SWB-01	4921	2016	2644	Iveco Daily 55S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390121/daily-55s18w-4x4-chassis-cab
EU-IVECO-DAILY-IV-55S18W-CHASSIS-CAB-MWB-01	5432	2016	2634	Iveco Daily 55S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390121/daily-55s18w-4x4-chassis-cab
EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-SWB-01	4921	2016	2635	Iveco Daily 35S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390142/daily-35s18w-4x4-chassis-cabpmd/2
EU-IVECO-DAILY-IV-35S18W-CHASSIS-CAB-MWB-01	5432	2016	2627	Iveco Daily 35S18W 4x4 Chassis Cab official specification sheet, Yumpu archive	https://www.yumpu.com/en/document/view/21390142/daily-35s18w-4x4-chassis-cabpmd/2
EU-KIA-CERATO-I-LD-HATCHBACK-01	4340	1735	1470	CarFolio	https://www.carfolio.com/kia-cerato-1.5-crdi-hatchback-130680
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-SVR-01	4475	1923	1308	Auto-Data	https://www.auto-data.net/en/jaguar-f-type-convertible-svr-5.0-v8-575hp-awd-automatic-27244
EU-IVECO-DAILY-V-NATURALPOWER-VAN-SWB-LOW-SRW-01	5477	1996	2270	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-SRW-01	5977	1996	2640	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-SRW-01	7012	1996	2670	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-DRW-01	5997	1996	2745	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-DRW-01	7012	1996	2745	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-DRW-01	7012	1996	2930	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-70C-01	7012	1996	3025	CarsGuide 2012 Iveco Daily dimensions; GMB application catalog	https://www.carsguide.com.au/iveco/daily/car-dimensions/2012;https://am.gmb.co.kr/page/product_pdf.php?articleId=1245404556&code=GC50020&countrie=EN
EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-SWB-01	5899	1996	2225	Iveco Daily 35S14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/35S14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-LWB-01	6509	1996	2220	Iveco Daily 35S14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/35S14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-SWB-01	5899	1996	2280	Iveco Daily 35C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/35C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-LWB-01	6509	1996	2275	Iveco Daily 35C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/35C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-CREW-01	6090	1996	2290	Iveco Daily 35C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/35C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-SWB-01	5928	1996	2280	Iveco Daily 50C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/50C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-MWB-01	6538	1996	2275	Iveco Daily 50C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/50C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-LWB-01	7358	1996	2265	Iveco Daily 50C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/50C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-CREW-01	7358	1996	2280	Iveco Daily 50C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/50C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-SWB-01	5928	2060	2335	Iveco Daily 65C14 G official technical card; Iveco Daily 70C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/65C14G.pdf;https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/70C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-MWB-01	6538	2060	2330	Iveco Daily 65C14 G official technical card; Iveco Daily 70C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/65C14G.pdf;https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/70C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-LWB-01	7358	2060	2325	Iveco Daily 65C14 G official technical card; Iveco Daily 70C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/65C14G.pdf;https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/70C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-XLWB-01	8223	2060	2320	Iveco Daily 65C14 G official technical card; Iveco Daily 70C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/65C14G.pdf;https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/70C14G.pdf
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-CREW-01	7358	2060	2345	Iveco Daily 65C14 G official technical card; Iveco Daily 70C14 G official technical card	https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/65C14G.pdf;https://tnc.iveco.pl/upload/public/dealer-tnc/Daily%202012/70C14G.pdf
EU-LAMBORGHINI-HURACAN-LP580-2-CONVERTIBLE-01	4459	1924	1180	Auto-Data	https://www.auto-data.net/en/lamborghini-huracan-lp-580-2-spyder-generation-8857
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470	Auto-Data	https://www.auto-data.net/en/hyundai-i40-sedan-2.0-gdi-177hp-18567
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512	Auto-Data	https://www.auto-data.net/en/lada-vesta-sw-1.8-122hp-automatic-30842
EU-LADA-GRANTA-I-HATCHBACK-01	4246	1700	1500	Auto-Data	https://www.auto-data.net/en/lada-granta-i-hatchback-1.6-16v-98hp-automatic-24201
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Auto-Data	https://www.auto-data.net/en/ford-ecosport-model-2038
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435	Auto-Data	https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046
EU-ASTON-MARTIN-DB11-COUPE-01	4750	1950	1290	Auto-Data	https://www.auto-data.net/en/aston-martin-db11-generation-4901
EU-ASTON-MARTIN-DB11-VOLANTE-CONVERTIBLE-01	4750	1950	1300	Auto-Data	https://www.auto-data.net/en/aston-martin-db11-volante-generation-6058
EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	4490	1942	1274	Auto-Data	https://www.auto-data.net/en/aston-martin-v8-vantage-2018-generation-5998
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-01	4822	1943	1781	Auto-Data	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-3.0-crd-190hp-4x4-automatic-31162
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-01	4826	1860	1428	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-220d-194hp-4matic-9g-tronic-33168
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845	Auto-Data	https://www.auto-data.net/bg/opel-combo-model-238
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-6.0-w12-590hp-awd-automatic-22847
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-speed-6.0-635hp-awd-automatic-22860
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390	Auto-Data	https://www.auto-data.net/en/bentley-continental-gtc-ii-facelift-2015-supersport-6.0-w12-710hp-awd-automatic-30311
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443	Auto-Data	https://www.auto-data.net/en/tesla-model-3-long-range-75-kwh-287hp-32648
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-01	4826	1860	1430	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748
EU-BMW-I8-I12-LCI-COUPE-01	4689	1942	1293	Auto-Data	https://www.auto-data.net/en/bmw-i8-coupe-i12-lci-generation-6016
EU-BMW-I8-I15-ROADSTER-01	4689	1942	1291	Auto-Data	https://www.auto-data.net/en/bmw-i8-roadster-i15-generation-6017
EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	5299	1976	1488	Auto-Data	https://www.auto-data.net/en/bentley-flying-spur-ii-facelift-2015-4.0-v8-507hp-awd-automatic-22862
EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	4435	2055	1141	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2549810/pagani_zonda_cinque_roadster.html
EU-PAGANI-ZONDA-CINQUE-COUPE-01	4435	2055	1141	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/2549795/pagani_zonda_cinque.html
EU-VW-PASSAT-B5-5-3BG-WAGON-01	4682	1746	1498	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b5.5-2.8-30v-v6-193hp-4motion-43107
EU-VW-PASSAT-B5-5-3BG-SEDAN-01	4703	1746	1462	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b5.5-1.6-102hp-43379
EU-RENAULT-CLIO-III-PHASE-II-VAN-3D-01	4032	1720	1497	Auto-Data	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-1.5-dci-75hp-fap-10408
EU-LOTUS-ELISE-SERIES-3-CUP-250-CONVERTIBLE-01	3824	1719	1117	Auto-Data	https://www.auto-data.net/en/lotus-elise-series-3-cup-250-1.8-246hp-24356
EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	4084	1802	1129	Auto-Data	https://www.auto-data.net/en/lotus-exige-iii-s-roadster-sport-350-3.5-v6-350hp-21318
EU-LAMBORGHINI-VENENO-ROADSTER-CONVERTIBLE-01	5020	2075	1165	Auto-Data	https://www.auto-data.net/en/lamborghini-veneno-lp-750-4-roadster-6.5-v12-750hp-43241
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404	Auto-Data	https://www.auto-data.net/en/bentley-continental-gt-ii-facelift-2015-v8-s-4.0-528hp-awd-automatic-22898
EU-VOLVO-XC90-I-FACELIFT-SUV-01	4807	1936	1784	Auto-Data	https://www.auto-data.net/en/volvo-xc90-facelift-2007-2.4-d5-200hp-awd-automatic-18204
EU-HONDA-FIT-I-GD2-HATCHBACK-PREFL-01	3830	1675	1550	JapaneseCarTrade Honda Fit LA-GD2 specification	https://cars.japanesecartrade.com/detail/honda/fit/a/162412
EU-HONDA-FIT-I-GD2-HATCHBACK-FACELIFT-01	3845	1675	1550	JapaneseCarTrade Honda Fit DBA-GD2 specification	https://cars.japanesecartrade.com/detail/honda/fit/1.3a/162346
EU-MASERATI-GHIBLI-III-M157-FACELIFT-SEDAN-01	4971	1945	1461	Auto-Data	https://www.auto-data.net/en/maserati-ghibli-iii-m157-facelift-2017-s-3.0-v6-430hp-automatic-27243
EU-MASERATI-QUATTROPORTE-VI-M156-FACELIFT-SEDAN-01	5262	1948	1481	Auto-Data	https://www.auto-data.net/en/maserati-quattroporte-vi-m156-facelift-2016-s-q4-3.0-gdi-430hp-awd-automatic-32650
EU-SMART-FORTWO-III-A453-CONVERTIBLE-EV-01	2695	1663	1553	Auto-Data	https://www.auto-data.net/en/smart-fortwo-iii-cabrio-a453-17.6-kwh-82hp-electric-drive-32739
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Auto-Data	https://www.auto-data.net/en/audi-q2-2.0-tfsi-190hp-quattro-s-tronic-22876
EU-DAIMLER-SUPER-EIGHT-X350-SEDAN-01	5215	1898	1448	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1289360/daimler_super_eight.html
EU-CITROEN-SAXO-PHASE-II-VAN-3D-01	3718	1595	1360	Auto-Data	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.5-d-57hp-44815
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Auto-Data	https://www.auto-data.net/en/volvo-s90-2016-2.0-t4-190hp-automatic-35847
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data	https://www.auto-data.net/en/volvo-v90-2016-2.0-t5-250hp-automatic-32886
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Auto-Data	https://www.auto-data.net/en/volvo-v90-cross-country-generation-5155
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-3.0-v6-340hp-tiptronic-s-31653
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data	https://www.auto-data.net/en/volvo-xc60-ii-2.0-t5-250hp-automatic-32776
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Auto-Data	https://www.auto-data.net/en/volvo-xc90-ii-2.0-t6-310hp-awd-automatic-36309
EU-BMW-X3-G01-SUV-01	4708	1891	1676	Auto-Data	https://www.auto-data.net/en/bmw-x3-g01-20i-184hp-sdrive-steptronic-51143
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468	Auto-Data	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-530i-272hp-9607
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-sw-ii-phase-ii-2017-gt-2.0-bluehdi-180hp-automatic-32062
EU-BMW-5-E61-WAGON-01	4843	1846	1491	Auto-Data;Auto-Data	https://www.auto-data.net/en/bmw-5-series-touring-e61-530xi-258hp-9623;https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-530i-272hp-xdrive-steptronic-28288
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-cls-450-367hp-eq-boost-4matic-9g-tronic-32272
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-1.4-t-gdi-140hp-25965
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1846	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2521430/land-rover_discovery_td4_4wd.html
EU-BMW-M3-E30-CONVERTIBLE-01	4345	1680	1370	Auto-Data	https://www.auto-data.net/en/bmw-m3-convertible-e30-2.3-215hp-cat-9885
EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	3665	1660	1500	Auto-Data	https://www.auto-data.net/en/hyundai-i10-ii-facelift-2016-1.0-lpg-69-67hp-29506
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450	Auto-Data	https://www.auto-data.net/fr/lexus-ls-v-500-v6-420hp-awd-automatic-28869
EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	3890	1735	1495	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-sport-1.4-140hp-automatic-32531
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Auto-Data	https://www.auto-data.net/en/land-rover-range-rover-sport-ii-facelift-2017-2.0-si4-300hp-awd-automatic-31680
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480	Auto-Data	https://www.auto-data.net/en/citroen-c4-cactus-phase-ii-2018-1.2-puretech-130hp-39020
EU-MERCEDES-BENZ-X-CLASS-W470-PICKUP-01	5340	1920	1819	Auto-Data	https://www.auto-data.net/en/mercedes-benz-x-class-x-220d-163hp-31024
EU-KOENIGSEGG-ONE-1-COUPE-01	4500	2060	1150	Koenigsegg official technical specifications	https://www.koenigsegg.com/technical-specifications-one1
EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-FACELIFT-SEDAN-01	5462	1899	1498	Auto-Data	https://www.auto-data.net/en/mercedes-benz-maybach-s-class-x222-facelift-2017-generation-5472
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457	Auto-Data	https://www.auto-data.net/en/peugeot-308-ii-phase-ii-2017-generation-5518
EU-KIA-CERATO-III-YD-KOUP-01	4530	1780	1410	Auto-Data	https://www.auto-data.net/ro/kia-cerato-model-275
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	Auto-Data	https://www.auto-data.net/en/seat-ibiza-v-1.6-tdi-115hp-start-stop-33871
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485	Auto-Data	https://www.auto-data.net/en/kia-ceed-model-1935
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-vi-1.0-tsi-115hp-31890
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869	Auto-Data;CarExpert	https://www.auto-data.net/en/land-rover-range-rover-iv-facelift-2017-5.0-v8-525hp-awd-automatic-supercharged-31385;https://www.carexpert.com.au/land-rover/range-rover/2018-svautobiography-dynamic/features-and-specs
EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	3600	1641	1504	Volkswagen UK official press kit	https://www.vwpress.co.uk/press-kits/258
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1901-2000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carsguide.com.au/iveco/daily/car-dimensions/2012 "https://www.carsguide.com.au/iveco/daily/car-dimensions/2012"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（975 行）
- 累计尺寸组：dimension_groups_final.tsv（544 行）

- 尺寸冲突协调：
  - EU-ASTON-MARTIN-DB11-COUPE-01 -> EU-ASTON-MARTIN-DB11-COUPE-02：4739x1940x1279 与 4750x1950x1290，创建新尺寸组
