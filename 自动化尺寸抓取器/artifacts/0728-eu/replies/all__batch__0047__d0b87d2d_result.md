# 任务：all 第 4601-4700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0047__d0b87d2d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4601-4700 行

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
all 第 4601-4700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-155-167-SEDAN-PREFL-01	4443	1700	1440
EU-ALFA-ROMEO-155-167-SEDAN-Q4-WIDEBODY-01	4443	1730	1440
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-01	4443	1730	1425
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	4443	1730	1440
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-BMW-6-F13-COUPE-01	4894	1894	1369
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468
EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	3408	1500	1485
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420
EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	3380	1460	1445
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540
EU-FIAT-PANDA-II-4X4-HATCHBACK-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-4X4-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	3538	1589	1614
EU-FIAT-PANDA-III-319-HATCHBACK-01	3653	1643	1551
EU-FIAT-PANDA-I-PREFL-4X4-01	3390	1485	1470
EU-FIAT-ULYSSE-I-220-MPV-01	4454	1834	1714
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424
EU-FORD-ORION-III-GAL-SEDAN-01	4229	1690	1395
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389
EU-FORD-ORION-II-SEDAN-02	4210	1640	1390
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407
EU-FORD-SIERRA-MK1-HATCHBACK-3D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-GHIA-01	4425	1725	1408
EU-FORD-SIERRA-MK1-WAGON-01	4491	1712	1438
EU-FORD-SIERRA-MK1-WAGON-GHIA-01	4522	1729	1438
EU-FORD-SIERRA-MK1-XR4I-HATCHBACK-3D-01	4459	1728	1392
EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	4459	1725	1378
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428
EU-HONDA-NSX-I-NA1-COUPE-2D-FACELIFT-01	4425	1810	1170
EU-HONDA-NSX-I-NA1-COUPE-2D-PREFL-01	4430	1810	1170
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402
EU-LADA-SAMARA-I-HATCHBACK-5D-01	4006	1650	1402
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1822	1462
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440
EU-LEXUS-LS-I-XF10-SEDAN-4D-01	5005	1820	1425
EU-MAZDA-323-S-V-BA-SEDAN-4D-01	4340	1710	1420
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	4855	2000	2455
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	5235	2000	2525
EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	5885	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	5885	2000	2530
EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	5885	2000	2240
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440
EU-NISSAN-SUNNY-B11-COUPE-3D-01	4135	1620	1355
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385
EU-NISSAN-SUNNY-B11-WAGON-5D-01	4255	1620	1360
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370
EU-NISSAN-SUNNY-B310-WAGON-5D-01	4050	1590	1390
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-02	4215	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4215	1640	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525
EU-OPEL-KADETT-E-CARAVAN-01	4228	1666	1430
EU-OPEL-KADETT-E-CONVERTIBLE-16-01	3998	1663	1385
EU-OPEL-KADETT-E-CONVERTIBLE-20-01	3998	1663	1380
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400
EU-OPEL-KADETT-E-SEDAN-01	4218	1658	1400
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-BASE-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-WIDE-01	4283	1636	1426
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443
EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	4770	1820	1440
EU-SUZUKI-VITARA-I-SUV-CLOSED-01	3620	1630	1665
EU-SUZUKI-VITARA-I-SUV-OPEN-01	3620	1630	1665
EU-TALBOT-HORIZON-HATCHBACK-01	3960	1680	1410
EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	4490	1690	1745
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415
EU-VW-CADDY-III-2K-VAN-01	4405	1794	1833
EU-VW-CORRADO-53I-COUPE-FACELIFT-01	4050	1690	1310
EU-VW-CORRADO-53I-COUPE-PREFL-01	4048	1674	1318
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1303-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-TYPE113-1600-01	4060	1550	1500
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Lada	Samara	1500	Stufenheck	Frontantrieb	Benzin	52	71	Nov 1994	Dec 2006	2024-03-01	4744
Nissan	Maxima / qx iv	2	Stufenheck	Frontantrieb	Benzin	103	140	Feb 1995	Aug 2000	2024-03-01	4745
Citroën	Evasion	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	66	90	Nov 1994	Jul 2002	2024-03-01	4746
Peugeot	806	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	66	90	Jul 1995	Aug 2002	2024-03-01	4747
Renault	19 ii	1.8	Cabriolet	Frontantrieb	Benzin	79	107	Jul 1994	Jun 1996	2024-03-01	4748
Renault	Espace ii	2.1 TD	Großraumlimousine	Frontantrieb	Diesel	66	90	Nov 1994	Oct 1996	2024-03-01	4749
Lancia	Dedra	1.6	Kombi	Frontantrieb	Benzin	66	90	Oct 1994	Jul 1999	2024-03-01	4750
Alfa Romeo	146	1.7 I.e. 16V	Schrägheck	Frontantrieb	Benzin	95	129	Dec 1994	Dec 1996	2024-03-01	4751
Alfa Romeo	146	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	76	103	Dec 1994	Dec 1996	2024-03-01	4752
Alfa Romeo	146	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Dec 1994	Dec 1996	2024-03-01	4753
Alfa Romeo	146	1.9 TD	Schrägheck	Frontantrieb	Diesel	66	90	Dec 1994	Feb 1999	2024-03-01	4754
Fiat	Panda	1100	Schrägheck	Frontantrieb	Benzin	40	54	Feb 1995	Sep 2003	2024-03-01	4755
Fiat	Panda	1100 4X4	Schrägheck	Allrad	Benzin	40	54	Feb 1995	Jul 2004	2024-03-01	4756
Lancia	Y10	1.1 Fire	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1995	Dec 1995	2024-03-01	4757
Lancia	Y10	1.1 Fire Allrad	Schrägheck	Allrad	Benzin	40	54	Jan 1995	Dec 1995	2024-03-01	4758
Fiat	Ulysse	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	66	90	Feb 1995	Aug 2002	2024-03-01	4759
Fiat	Barchetta	1.8 16V	Cabriolet	Frontantrieb	Benzin	96	130	Apr 1995	May 2005	2024-03-01	4760
Lancia	Kappa	2.0 16V Turbo	Stufenheck	Frontantrieb	Benzin	151	205	Feb 1995	Oct 2001	2024-03-01	4761
Alfa Romeo	155	2.0 T.s. 16V	Stufenheck	Frontantrieb	Benzin	110	150	Mar 1995	Dec 1997	2024-03-01	4762
Lexus	Ls	400	Stufenheck	Heckantrieb	Benzin	194	264	Dec 1994	Aug 1997	2024-03-01	4763
Honda	Nsx i	3.0 24V Vtec Automatic	Cabriolet	Heckantrieb	Benzin	188	256	Mar 1995	Sep 2005	2024-03-01	4764
Honda	Nsx i	3.0 24V Vtec	Cabriolet	Heckantrieb	Benzin	201	274	Mar 1995	Sep 2005	2024-03-01	4765
Honda	Shuttle	2.2 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Oct 1994	Feb 1998	2024-03-01	4766
BMW	6	M6	Cabriolet	Heckantrieb	Benzin	412	560	Mar 2012	Jun 2018	2024-03-01	4767
Suzuki	Vitara	2.0 V6 24V Allrad	Geländewagen geschlossen	Allrad	Benzin	100	136	Dec 1994	Mar 1998	2024-03-01	4768
Suzuki	Baleno	1.3 I 16V	Schrägheck	Frontantrieb	Benzin	63	85	Jul 1995	May 2002	2024-03-01	4769
Suzuki	Baleno	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	72	98	Jul 1995	May 2002	2024-03-01	4770
Suzuki	Baleno	1.6 I 16V 4X4	Schrägheck	Allrad	Benzin	72	98	Jul 1995	May 2002	2024-03-01	4771
Suzuki	Baleno	1.3 I 16V	Stufenheck	Frontantrieb	Benzin	63	85	Jul 1995	May 2002	2024-03-01	4772
Suzuki	Baleno	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	72	98	Jul 1995	May 2002	2024-03-01	4773
Suzuki	Baleno	1.6 I 16V 4X4	Stufenheck	Allrad	Benzin	72	98	Jul 1995	May 2002	2024-03-01	4774
Toyota	Carina e vi sportswagon	1.6 I	Kombi	Frontantrieb	Benzin	73	99	Feb 1995	Sep 1997	2024-03-01	4775
Toyota	Carina e vi sportswagon	1.8 I	Kombi	Frontantrieb	Benzin	79	107	Feb 1995	Sep 1997	2024-03-01	4776
Toyota	Land cruiser 80	4.2 TD 24V	Geländewagen geschlossen	Allrad	Diesel	125	170	Jan 1995	Dec 1997	2024-03-01	4777
Toyota	Land cruiser 80	4.5 24V	Geländewagen geschlossen	Allrad	Benzin	151	205	Aug 1992	Dec 1997	2024-03-01	4778
Nissan	Micra ii	1.3 I 16V	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1992	Sep 2000	2024-03-01	4779
Nissan	Sunny	1.6 I	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1990	May 1995	2024-03-01	4780
Mitsubishi	L400	2.0 16V	Bus	Heckantrieb	Benzin	85	115	May 1995	May 2000	2024-03-01	4781
Mitsubishi	L400	2.4 I 4WD	Bus	Allrad	Benzin	97	132	May 1995	May 2000	2024-03-01	4783
Mitsubishi	L400	2.5 TD	Bus	Heckantrieb	Diesel	73	99	May 1995	May 2000	2024-03-01	4785
Mitsubishi	L400	2.5 TD 4WD	Bus	Allrad	Diesel	73	99	May 1995	May 2000	2024-03-01	4786
Daihatsu	Cuore iv	0.8	Schrägheck	Frontantrieb	Benzin	32	43	Jan 1995	Aug 1998	2024-03-01	4787
Mazda	Mx-5 i	1.6	Cabriolet	Heckantrieb	Benzin	66	90	Jan 1995	Apr 1998	2024-03-01	4788
Mazda	323 s v	1.7 TD	Stufenheck	Frontantrieb	Diesel	60	82	May 1994	Sep 1998	2024-03-01	4789
Mazda	Xedos 9	2.3 24V	Stufenheck	Frontantrieb	Benzin	155	211	Feb 1995	Jan 2000	2024-03-01	4790
VW	Kaefer	1302 1.3	Stufenheck	Heckantrieb	Benzin	32	44	Aug 1970	Aug 1972	2024-03-01	4791
Opel	Kadett e	1.6 I	Cabriolet	Frontantrieb	Benzin	60	82	Jul 1989	Feb 1993	2024-03-01	4792
VW	Corrado	2.0 I	Coupe	Frontantrieb	Benzin	85	115	Apr 1993	Dec 1995	2024-03-01	4793
Mercedes-benz	T1	207 D 2.4	Bus	Heckantrieb	Diesel	53	72	Jul 1982	Jan 1990	2024-03-01	4794
Ford	Orion ii	1.6 I	Stufenheck	Frontantrieb	Benzin	77	105	Mar 1986	Jul 1990	2024-03-01	4795
Ford	Sierra	2.8 4X4	Kombi	Allrad	Benzin	110	150	Jan 1987	Aug 1988	2024-03-01	4796
Peugeot	305 ii break	1.9	Kombi	Frontantrieb	Benzin	75	102	Sep 1984	Oct 1987	2024-03-01	4797
Renault	19 ii	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Apr 1992	Dec 1995	2024-03-01	4798
Renault	19 ii	1.9 DT	Schrägheck	Frontantrieb	Diesel	66	90	Apr 1992	Dec 1995	2024-03-01	4799
Renault	19 ii chamade	1.9 DT	Stufenheck	Frontantrieb	Diesel	66	90	Apr 1992	Dec 1995	2024-03-01	4800
Renault	19 ii chamade	1.8 16V	Stufenheck	Frontantrieb	Benzin	99	135	Apr 1992	Dec 1995	2024-03-01	4801
Renault	Safrane i	2.2	Schrägheck	Frontantrieb	Benzin	79	107	Apr 1992	Jul 1996	2024-03-01	4802
Renault	Safrane i	2.2	Schrägheck	Frontantrieb	Benzin	101	137	Apr 1992	Jul 1996	2024-03-01	4803
Renault	Safrane i	3.0 V6	Schrägheck	Frontantrieb	Benzin	123	167	Dec 1992	Jul 1996	2024-03-01	4804
Renault	Safrane i	2.5 DT	Schrägheck	Frontantrieb	Diesel	83	113	Dec 1992	Jul 1996	2024-03-01	4805
Renault	Clio i	1.8 RSI	Schrägheck	Frontantrieb	Benzin	80	109	Jan 1993	Aug 1995	2026-05-01	4806
Renault	Clio i	Williams	Schrägheck	Frontantrieb	Benzin	108	147	Jan 1994	Sep 1998	2026-05-01	4807
Talbot	Horizon	1.4	Schrägheck	Frontantrieb	Benzin	48	65	Feb 1982	Sep 1984	2024-03-01	4808
Toyota	Corolla	2.0 D	Schrägheck	Frontantrieb	Diesel	53	72	Jul 1992	Apr 1997	2024-03-01	4809
Toyota	Corolla	2.0 D	Schrägheck	Frontantrieb	Diesel	53	72	Jul 1992	Apr 1997	2024-03-01	4810
Toyota	Corolla	2.0 D	Kombi	Frontantrieb	Diesel	53	72	Jul 1992	Apr 1997	2024-03-01	4811
Toyota	Land cruiser 80	4.2 TD	Geländewagen geschlossen	Allrad	Diesel	118	160	Aug 1992	Dec 1997	2024-03-01	4812
Toyota	4	3.0 EFI	SUV	Allrad	Benzin	105	143	Jan 1990	Oct 1995	2025-02-03	4813
Mitsubishi	Lancer v station wagon	1.6 16V	Kombi	Frontantrieb	Benzin	83	113	Dec 1992	Oct 2003	2024-03-01	4814
Mitsubishi	Lancer v station wagon	2.0 D	Kombi	Frontantrieb	Diesel	50	68	Dec 1992	Oct 2003	2024-03-01	4815
VW	Caddy i	1.5	Pick-up	Frontantrieb	Benzin	51	70	Aug 1982	Jul 1983	2024-03-01	4816
VW	Caddy i	1.6	Pick-up	Frontantrieb	Benzin	55	75	Jan 1983	Jul 1992	2024-03-01	4817
VW	Caddy i	1.8	Pick-up	Frontantrieb	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	4818
Skoda	Octavia	2.0 TDI 4X4	Kombi	Allrad	Diesel	81	110	May 2011	Feb 2013	2024-03-01	4819
VW	Caddy i	1.6 D	Pick-up	Frontantrieb	Diesel	40	55	Aug 1982	Jul 1992	2024-03-01	4820
Mazda	323 c iv	1.7 D	Schrägheck	Frontantrieb	Diesel	41	56	Aug 1989	Jul 1994	2024-03-01	4821
Mazda	323 c iv	1.8 16V Turbo 4WD	Schrägheck	Allrad	Benzin	136	185	Jan 1993	Jul 1994	2024-03-01	4822
Mazda	626 iv hatchback	2.0 D GLX Comprex	Schrägheck	Frontantrieb	Diesel	55	75	Jan 1993	Apr 1997	2024-03-01	4823
Mazda	626 iii station wagon	2.0 D Comprex	Kombi	Frontantrieb	Diesel	55	75	May 1993	Nov 1996	2024-03-01	4824
Mazda	Xedos 6	1.6 16V	Stufenheck	Frontantrieb	Benzin	83	113	Jan 1992	Mar 1994	2024-03-01	4825
Volvo	850	2.4	Kombi	Frontantrieb	Benzin	103	140	Aug 1992	Jul 1994	2024-03-01	4826
Ford	Mondeo i	2.0 I 16V 4X4	Schrägheck	Allrad	Benzin	97	132	Dec 1994	Aug 1996	2024-03-01	4827
Porsche	911	3.8 Turbo	Coupe	Allrad	Benzin	368	500	Sep 2009	Dec 2012	2024-03-01	4828
Nissan	Primastar	DCI 115	Bus	Frontantrieb	Diesel	84	114	Sep 2008	-	2024-03-01	4829
Nissan	Primastar	2.5 DCI 115	Kasten	Frontantrieb	Diesel	84	114	Sep 2008	-	2024-03-01	4830
Lada	Samara	1500	Schrägheck	Frontantrieb	Benzin	52	71	Feb 1995	Dec 2006	2024-03-01	4831
Mercedes-benz	S-Klasse	500 SEC	Coupe	Heckantrieb	Benzin	195	265	Sep 1985	Jun 1991	2024-03-01	4832
Porsche	911	3.8 Carrera S / GTS	Coupe	Heckantrieb	Benzin	300	408	Jun 2009	Dec 2011	2024-03-01	4833
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel	55	75	Jun 1993	Jun 1995	2024-03-01	4834
Mercedes-benz	E-Klasse	E 250 Turbo-d	Stufenheck	Heckantrieb	Diesel	93	126	Jun 1993	Jun 1995	2024-03-01	4835
Mercedes-benz	E-Klasse	E 300 Turbo-d 4-matic	Stufenheck	Allrad	Diesel	108	147	Jun 1993	Jun 1995	2024-03-01	4836
Mercedes-benz	E-Klasse	E 300 Turbo-d	Stufenheck	Heckantrieb	Diesel	108	147	Jun 1993	Jun 1995	2024-03-01	4837
Mercedes-benz	E-Klasse	E 300 4-matic	Stufenheck	Allrad	Benzin	132	180	Jun 1993	Jun 1995	2024-03-01	4838
Mercedes-benz	E-Klasse	E 300 T Turbo-d	Kombi	Heckantrieb	Diesel	108	147	Jun 1993	Jun 1996	2024-03-01	4839
Mercedes-benz	E-Klasse	E 300 T 4-matic	Kombi	Allrad	Benzin	132	180	Jun 1993	Jun 1996	2024-03-01	4840
Mercedes-benz	E-Klasse	E 300 T Turbo-d 4-matic	Kombi	Allrad	Diesel	108	147	Jun 1993	Jun 1996	2024-03-01	4841
VW	Polo	1	Stufenheck	Frontantrieb	Benzin	29	40	Jan 1985	Oct 1986	2024-03-01	4842
VW	Polo	1	Stufenheck	Frontantrieb	Benzin	33	45	Jan 1985	Sep 1994	2024-03-01	4843
VW	Polo	1.3 D	Stufenheck	Frontantrieb	Diesel	33	45	Aug 1986	Dec 1988	2024-03-01	4844
VW	Polo	1.3 CAT	Stufenheck	Frontantrieb	Benzin	40	55	Jul 1987	Sep 1994	2024-03-01	4845


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成 43 条既有尺寸组关联，不重复抓取既有尺寸。
* 首次闭合 8 个尺寸组：Alfa Romeo 146、Fiat Barchetta、BMW M6 F12 Cabriolet、Mercedes-Benz C126 500 SEC，以及 W124/S124 两驱与 4MATIC 外廓分支。
* Alfa Romeo 146 已确认 930 五门车身为 `4257 × 1712 × 1425 mm`；BMW M6 F12 改款前后均为 `4898 × 1899 × 1368 mm`，因此没有因 LCI 重复建组。([汽车数据][1])
* W124/S124 的 4MATIC 版本高度与后驱版本不同，已分别建组，未按发动机配置重复拆分。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：51
* PENDING 映射：49
* READY 映射当前引用尺寸组：38
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4744	4744	Sedan	Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
4746	4746	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4747	4747	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH		READY
4748	4748	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH		READY
4749	4749	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH		READY
4750	4750	Wagon	Dedra I facelift	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
4751	4751	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4752	4752	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4753	4753	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4754	4754	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4755	4755	Hatchback	Panda I facelift	141A	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
4756	4756	Hatchback	Panda I facelift	141A	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
4757	4757	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH		READY
4758	4758	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	HIGH		READY
4759	4759	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH		READY
4760	4760	Convertible	Barchetta	183	2	EU-FIAT-BARCHETTA-183-CONVERTIBLE-2D-01	HIGH		READY
4761	4761	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
4763	4763	Sedan	LS I	UCF10	4	EU-LEXUS-LS-I-XF10-SEDAN-4D-01	HIGH		READY
4767	4767	Convertible	M6 F12	F12	2	EU-BMW-M6-F12-CONVERTIBLE-2D-01	HIGH	改款前后外廓尺寸一致，合并为同一尺寸组。	READY
4788	4788	Convertible	MX-5 I	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH		READY
4789	4789	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4790	4790	Sedan	Xedos 9	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH		READY
4791	4791	Sedan	Kaefer 1302	1302	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
4792	4792	Convertible	Kadett E	E	2	EU-OPEL-KADETT-E-CONVERTIBLE-16-01	HIGH		READY
4793	4793	Coupe	Corrado facelift	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH		READY
4798	4798	Hatchback	Renault 19 II	B53		EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	三门与五门外廓尺寸一致，输入未区分门数。	READY
4799	4799	Hatchback	Renault 19 II	B53		EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	三门与五门外廓尺寸一致，输入未区分门数。	READY
4800	4800	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH		READY
4801	4801	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH		READY
4802	4802	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4803	4803	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4804	4804	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4805	4805	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4806	4806	Hatchback	Clio I	57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
4807	4807	Hatchback	Clio I	57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
4808	4808	Hatchback	Horizon	C2	5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
4811	4811	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH		READY
4812	4812	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4813	4813	SUV	4Runner II	N130	5	EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	HIGH		READY
4825	4825	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4826	4826	Wagon	850	850	5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
4827	4827	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
4832	4832	Coupe	S-Class Coupe C126 facelift	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-500SEC-FACELIFT-01	HIGH		READY
4834	4834	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4835	4835	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4836	4836	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	HIGH		READY
4837	4837	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4838	4838	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	HIGH		READY
4839	4839	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-RWD-01	HIGH		READY
4840	4840	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	HIGH		READY
4841	4841	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425	Auto-Data Alfa Romeo 146 930 1.7 i.e.	https://www.auto-data.net/en/alfa-romeo-146-930-1.7-i.e.-129hp-1274
EU-FIAT-BARCHETTA-183-CONVERTIBLE-2D-01	3916	1640	1265	Auto-Data Fiat Barchetta 183 1.8 16V	https://www.auto-data.net/en/fiat-barchetta-183-1.8-16v-130hp-7035
EU-BMW-M6-F12-CONVERTIBLE-2D-01	4898	1899	1368	Auto-Data BMW M6 Convertible F12M; Auto-Data BMW M6 Convertible F12M LCI	https://www.auto-data.net/en/bmw-m6-convertible-f12m-4.4-v8-560hp-17796;https://www.auto-data.net/en/bmw-m6-convertible-f12m-lci-facelift-2014-4.4-v8-560hp-33137
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-500SEC-FACELIFT-01	4935	1828	1407	Auto-Data Mercedes-Benz 500 SEC C126 facelift	https://www.auto-data.net/en/mercedes-benz-s-class-coupe-c126-facelift-1985-500-sec-v8-265hp-automatic-13125
EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	4740	1740	1425	Auto-Data Mercedes-Benz E-Class W124 E 200 D	https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-200-d-75hp-12995
EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	4740	1740	1452	Auto-Data Mercedes-Benz E-Class W124 E 300 4MATIC; Auto-Data Mercedes-Benz E-Class W124 E 300 Turbodiesel 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-300-180hp-4matic-automatic-13002;https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-300-turbodiesel-147hp-4matic-automatic-13005
EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-RWD-01	4765	1740	1490	Auto-Data Mercedes-Benz E-Class S124 E 300 T Turbodiesel	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-turbodiesel-147hp-automatic-13027
EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	4765	1740	1498	Auto-Data Mercedes-Benz E-Class S124 E 300 T 4MATIC; Auto-Data Mercedes-Benz E-Class S124 E 300 T Turbodiesel 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-180hp-4matic-automatic-13025;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-turbodiesel-147hp-4matic-automatic-13028
```

## 下一步优先处理

1. 闭合 Suzuki Baleno 的 Hatchback、Sedan 与 4WD 高度分支。
2. 处理 Mitsubishi L400、Mercedes-Benz T1、Nissan Primastar 的轴距和车顶派生。
3. 核对 Honda NSX-T 改款边界、Nissan Maxima A32 外观改款尺寸，以及 Porsche 911 997 Carrera S、GTS、Turbo 宽体分支。
4. 处理 Corolla E100 两条相同发动机记录的 Compact/Liftback Ktype 边界，以及 Samara Hatchback 三门/五门分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-146-930-1.7-i.e.-129hp-1274 "Alfa Romeo 146 (930) 1.7 i.e. (129 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-200-d-75hp-12995?utm_source=chatgpt.com "Mercedes-Benz E-class (W124) E 200 D (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 已继续按缓存优先模式闭合 29 个输入 Ktype，并直接复用 5 个既有尺寸组：`EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01`、`EU-SUZUKI-VITARA-I-SUV-CLOSED-01`、`EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01`、`EU-NISSAN-MICRA-II-K11-HATCHBACK-01`、`EU-LADA-SAMARA-I-HATCHBACK-3D-01`。
* 本轮首次创建 15 个新尺寸组：Maxima A32、NSX-T prefl/facelift、Carina E Sportswagon、Cuore IV、Lancer V wagon、Caddy I pickup、Octavia II Combi facelift 4x4、Mazda 323 C IV、Mazda 626 IV hatchback、Mazda 626 III wagon、997.2 Turbo、997.2 Carrera S、997.2 GTS、Polo II sedan。
* Honda NSX I Cabriolet 已按外廓变化拆成 prefl / facelift 两个物理分支；Porsche 911 `Carrera S / GTS` 已按窄体 / 宽体拆分，不保留无后缀基础行。

当前批次进度

* READY 映射：80
* PENDING 映射：20
* 已确认尺寸组：53
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4745	4745	Sedan	Maxima / QX IV	A32	4	EU-NISSAN-MAXIMA-IV-A32-SEDAN-4D-01	HIGH		READY
4762	4762	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	HIGH		READY
4764_prefl	4764	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	HIGH	1995-2001 open-top pre-facelift branch.	READY
4764_facelift	4764	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2002-2005 open-top facelift branch.	READY
4765_prefl	4765	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	HIGH	1995-2001 open-top pre-facelift branch.	READY
4765_facelift	4765	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2002-2005 open-top facelift branch.	READY
4768	4768	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH		READY
4775	4775	Wagon	Carina E VI	T190	5	EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	HIGH		READY
4776	4776	Wagon	Carina E VI	T190	5	EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	HIGH		READY
4777	4777	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4778	4778	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4779	4779	Hatchback	Micra II	K11		EU-NISSAN-MICRA-II-K11-HATCHBACK-01	MEDIUM	3门/5门外廓尺寸一致，输入未区分门数。	READY
4787	4787	Hatchback	Cuore IV	L501		EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	MEDIUM	3门/5门外廓尺寸一致，输入未区分门数。	READY
4814	4814	Wagon	Lancer V Station Wagon	CBW	5	EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	HIGH		READY
4815	4815	Wagon	Lancer V Station Wagon	CBW	5	EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	HIGH		READY
4816	4816	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4817	4817	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4818	4818	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4819	4819	Wagon	Octavia II facelift	1Z	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH		READY
4820	4820	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4821	4821	Hatchback	323 C IV	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
4822	4822	Hatchback	323 C IV	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
4823	4823	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4824	4824	Wagon	626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH		READY
4828	4828	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-TURBO-01	HIGH		READY
4831	4831	Hatchback	Samara I			EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	3门/5门外廓尺寸一致，输入未区分门数。	READY
4833_carreras	4833	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	HIGH	Carrera S narrow-body branch.	READY
4833_gts	4833	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-GTS-01	HIGH	GTS wide-body branch.	READY
4842	4842	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4843	4843	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4844	4844	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4845	4845	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-MAXIMA-IV-A32-SEDAN-4D-01	4765	1770	1430	Auto-Data Nissan Maxima QX IV (A32) 2.0 V6	https://www.auto-data.net/en/nissan-maxima-qx-iv-a32-2.0-v6-140hp-1917
EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	4430	1810	1170	Auto-Data Honda NSX I NA1 Targa 3.0 V6 VTEC	https://www.auto-data.net/en/honda-nsx-i-na1-targa-3.0-v6-vtec-274hp-11430
EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX I facelift Targa 3.0 V6 VTEC	https://www.auto-data.net/en/honda-nsx-i-facelift-na1-targa-3.0-v6-vtec-274hp-11431
EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	4530	1695	1440	Auto-Data Toyota Carina E VI Sportswagon 1.8i	https://www.auto-data.net/en/toyota-carina-e-sportswagon-t190-1.8-i-107hp-5396
EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	3295	1395	1435	Auto-Data Daihatsu Cuore IV (L501) 0.8	https://www.auto-data.net/en/daihatsu-cuore-iv-l501-0.8-44hp-4561
EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	4270	1690	1465	Auto-Data Mitsubishi Lancer V Station Wagon (CBW) 1.6 16V	https://www.auto-data.net/en/mitsubishi-lancer-v-station-wagon-cbw-1.6-16v-113hp-11637
EU-VW-CADDY-I-14D-PICKUP-01	4380	1640	1490	Auto-Data Volkswagen Caddy I (14D) 1.6	https://www.auto-data.net/en/vw-caddy-i-14d-1.6-75hp-1294
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468	Auto-Data Skoda Octavia II Combi (1Z) facelift 2.0 TDI 4x4	https://www.auto-data.net/en/skoda-octavia-combi-ii-1z-facelift-2.0-tdi-4x4-110hp-12675
EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	3995	1670	1400	Auto-Data Mazda 323 C IV (BG) 1.7 D	https://www.auto-data.net/en/mazda-323-c-iv-bg-1.7-d-56hp-10476
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4680	1750	1400	Auto-Data Mazda 626 IV (GE) Hatchback 2.0 D Comprex	https://www.auto-data.net/en/mazda-626-iv-ge-hatchback-2.0-d-comprex-75hp-10183
EU-MAZDA-626-III-GV-WAGON-5D-01	4660	1755	1440	Auto-Data Mazda 626 III (GV) Station Wagon 2.0 D Comprex	https://www.auto-data.net/en/mazda-626-iii-gv-station-wagon-2.0-d-comprex-75hp-10171
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300	Auto-Data Porsche 911 Coupe (997 II) Turbo 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-turbo-3.8-500hp-pdk-21424
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300	Auto-Data Porsche 911 Coupe (997 II) Carrera S 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-carrera-s-3.8-408hp-21407
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300	Auto-Data Porsche 911 Coupe (997 II) Carrera GTS 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-carrera-gts-3.8-408hp-21414
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350	Auto-Data Volkswagen Polo II Classic / Derby (86C) 1.3 D	https://www.auto-data.net/en/vw-polo-classic-ii-86c-1.3-d-45hp-1879
```

下一步优先处理

1. 闭合 Honda Shuttle、Mitsubishi L400、Mercedes-Benz T1、Nissan Primastar 的轴距/车顶物理分支。
2. 处理 Suzuki Baleno hatchback / sedan 及其 4WD 高度差异。
3. 解决 Nissan Sunny hatchback、Toyota Corolla hatchback 两组门数/车身形态歧义。
4. 处理 Ford Orion II、Ford Sierra Kombi、Peugeot 305 II Break 的现有分支归属。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Honda Shuttle、Suzuki Baleno、Nissan Sunny、Ford Orion/Sierra、Peugeot 305、Toyota Corolla 与 Nissan Primastar 共 15 个输入 Ktype 的闭合。
* Ktype `4766` 已确认对应 Shuttle RA1 2.2 16V，采用 `4750 × 1790 × 1640 mm` 外廓。([AUTODOC][1])
* Baleno 按实际三维拆为三种 Hatchback 外廓：1.3 窄体、1.6 前驱宽体、1.6 四驱增高外廓；Sedan 前驱及四驱三维一致，复用一个尺寸组。([汽车数据][2])
* Primastar 根据官方车型手册完整派生 L1/L2、H1/H2、六座/九座及 L1H1 载荷级分支。手册示意图中的 `Overall Width E=1904 mm` 测量线位于后视镜内侧，符合不含后视镜宽度口径。([Dezo's Garage][3])
* Sunny N14 三门/五门、Orion II、Sierra Turnier II、305 II Break 与 Corolla E100 两种 Hatchback 分支均直接关联跨批次既有尺寸组，不重复输出尺寸组。

## 当前批次进度

* READY 输入 Ktype：95 / 100
* READY 映射行：106
* PENDING 输入 Ktype：5
* 本轮新增 READY 输入 Ktype：15
* 本轮新增 READY 映射行：23
* 本轮首次创建尺寸组：14
* 剩余 PENDING：`4781`、`4783`、`4785`、`4786`、`4794`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4766	4766	MPV	Shuttle I	RA1	5	EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	HIGH		READY
4769	4769	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	HIGH		READY
4770	4770	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	HIGH		READY
4771	4771	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	HIGH		READY
4772	4772	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4773	4773	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4774	4774	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4780_3dr	4780	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	三门物理外廓分支。	READY
4780_5dr	4780	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	五门物理外廓分支。	READY
4795	4795	Sedan	Orion II	AFF	4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
4796	4796	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
4797	4797	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-01	HIGH		READY
4809	4809	Hatchback	Corolla VII E100	CE100	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH		READY
4810	4810	Hatchback	Corolla VII E100	CE100	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH		READY
4829_l1h1_6seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-6SEAT-01	HIGH	L1H1六座物理外廓。	READY
4829_l1h1_9seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-9SEAT-01	HIGH	L1H1九座物理外廓。	READY
4829_l2h1_6seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-6SEAT-01	HIGH	L2H1六座物理外廓。	READY
4829_l2h1_9seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-9SEAT-01	HIGH	L2H1九座物理外廓。	READY
4830_l1h1_1t	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-1T-01	HIGH	L1H1 1.0t载荷级物理外廓。	READY
4830_l1h1_12t	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-12T-01	HIGH	L1H1 1.2t载荷级物理外廓。	READY
4830_l1h2	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H2-01	HIGH	L1H2短轴高顶物理外廓。	READY
4830_l2h1	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H1-01	HIGH	L2H1长轴低顶物理外廓。	READY
4830_l2h2	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H2-01	HIGH	L2H2长轴高顶物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	4750	1790	1640	BASt IMPROVER Final Report; UltimateSpecs Honda Shuttle 2.2i	https://www.bast.de/DE/Publikationen/BerichteBASt/Fachveroeffentlichungen/Fahrzeugtechnik/Unterseiten/F-improver-subproject-1.pdf?__blob=publicationFile&v=1;https://www.ultimatespecs.com/car-specs/Honda/7993/Honda-Shuttle-22i.html
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390	Auto-Data Suzuki Baleno Hatchback EG 1.3 i 16V	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.3-i-16v-85hp-automatic-23930
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390	Auto-Data Suzuki Baleno Hatchback EG 1.6 i 16V	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.6-i-16v-98hp-16482
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	3870	1680	1395	Automobile-Catalog Suzuki Baleno Hatchback 1.6 GL 4WD	https://www.automobile-catalog.com/car/1996/3387020/suzuki_baleno_hatchback_1_6_gl_4wd.html
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390	Auto-Data Suzuki Baleno EG 1.3 sedan; Automobile-Catalog Suzuki Baleno Sedan 1.6 GLX 4WD	https://www.auto-data.net/en/suzuki-baleno-eg-1995-1.3-i-16v-85hp-automatic-23934;https://www.automobile-catalog.com/car/1995/3387065/suzuki_baleno_sedan_1_6_glx_4wd.html
EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-6SEAT-01	4782	1904	1942	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-9SEAT-01	4782	1904	1963	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-6SEAT-01	5182	1904	1952	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-9SEAT-01	5182	1904	1968	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-1T-01	4782	1904	1955	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-12T-01	4782	1904	1963	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H2-01	4782	1904	2492	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H1-01	5182	1904	1962	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H2-01	5182	1904	2477	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
```

## 下一步优先处理

1. 集中闭合 Mitsubishi L400 的 `4781`、`4783`、`4785`、`4786`，确认短轴/长轴、低顶/高顶及四驱增高外廓分支。
2. 闭合 Mercedes-Benz T1 Bus `4794`，仅创建客车车身实际覆盖的轴距和车顶分支，不复用现有 Kasten、Platform 尺寸组。
3. PENDING 清零后直接进行一次机械闭合检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/sensor-speed-13031/honda/shuttle/shuttle-ra/4766-2-2-16v-ra1 "https://www.autodoc.parts/car-parts/sensor-speed-13031/honda/shuttle/shuttle-ra/4766-2-2-16v-ra1"
[2]: https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.3-i-16v-85hp-automatic-23930 "https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.3-i-16v-85hp-automatic-23930"
[3]: https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf "https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合最后 5 个 PENDING Ktype：`4781`、`4783`、`4785`、`4786`、`4794`。
* Mitsubishi L400 按 1996 年 9 月前后车身长度变化，以及两驱、四驱汽油、四驱柴油高度差异完成物理分支拆分。
* Mercedes-Benz T1 Bus 已按短轴和长轴客车外廓完成派生，并复用既有 `L1H1`、`L2H1` 尺寸组。
* 已完成固定表头、唯一性、引用闭合、正整数三维、来源非空及下载文件名机械校验。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：116
* PENDING：0
* 当前映射引用尺寸组：85
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一且引用闭合：通过
* 孤立尺寸组：0
* 最终校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4744	4744	Sedan	Samara I	21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
4745	4745	Sedan	Maxima / QX IV	A32	4	EU-NISSAN-MAXIMA-IV-A32-SEDAN-4D-01	HIGH		READY
4746	4746	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
4747	4747	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH		READY
4748	4748	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH		READY
4749	4749	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH		READY
4750	4750	Wagon	Dedra I facelift	835	5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
4751	4751	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4752	4752	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4753	4753	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4754	4754	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH		READY
4755	4755	Hatchback	Panda I facelift	141A	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
4756	4756	Hatchback	Panda I facelift	141A	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
4757	4757	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH		READY
4758	4758	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	HIGH		READY
4759	4759	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH		READY
4760	4760	Convertible	Barchetta	183	2	EU-FIAT-BARCHETTA-183-CONVERTIBLE-2D-01	HIGH		READY
4761	4761	Sedan	Kappa	838	4	EU-LANCIA-KAPPA-838-SEDAN-01	HIGH		READY
4762	4762	Sedan	155 (167)	167	4	EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	HIGH		READY
4763	4763	Sedan	LS I	UCF10	4	EU-LEXUS-LS-I-XF10-SEDAN-4D-01	HIGH		READY
4764_prefl	4764	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	HIGH	1995-2001 open-top pre-facelift branch.	READY
4764_facelift	4764	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2002-2005 open-top facelift branch.	READY
4765_prefl	4765	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	HIGH	1995-2001 open-top pre-facelift branch.	READY
4765_facelift	4765	Convertible	NSX I	NA1	2	EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2002-2005 open-top facelift branch.	READY
4766	4766	MPV	Shuttle I	RA1	5	EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	HIGH		READY
4767	4767	Convertible	M6 F12	F12	2	EU-BMW-M6-F12-CONVERTIBLE-2D-01	HIGH	改款前后外廓尺寸一致，合并为同一尺寸组。	READY
4768	4768	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH		READY
4769	4769	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	HIGH		READY
4770	4770	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	HIGH		READY
4771	4771	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	HIGH		READY
4772	4772	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4773	4773	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4774	4774	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
4775	4775	Wagon	Carina E VI	T190	5	EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	HIGH		READY
4776	4776	Wagon	Carina E VI	T190	5	EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	HIGH		READY
4777	4777	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4778	4778	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4779	4779	Hatchback	Micra II	K11		EU-NISSAN-MICRA-II-K11-HATCHBACK-01	MEDIUM	3门/5门外廓尺寸一致，输入未区分门数。	READY
4780_3dr	4780	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH	三门物理外廓分支。	READY
4780_5dr	4780	Hatchback	Sunny N14	N14	5	EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	HIGH	五门物理外廓分支。	READY
4781_prefl	4781	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-PREFL-01	HIGH	1995-08/1996前期外廓。	READY
4781_facelift	4781	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-FACELIFT-01	HIGH	09/1996-2000后期外廓。	READY
4783_prefl	4783	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-PREFL-01	HIGH	1995-08/1996前期四驱外廓。	READY
4783_facelift	4783	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-PETROL-FACELIFT-01	HIGH	09/1996-2000后期四驱汽油外廓。	READY
4785_prefl	4785	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-PREFL-01	HIGH	1995-08/1996前期外廓。	READY
4785_facelift	4785	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-FACELIFT-01	HIGH	09/1996-2000后期外廓。	READY
4786_prefl	4786	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-PREFL-01	HIGH	1995-08/1996前期四驱外廓。	READY
4786_facelift	4786	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-DIESEL-FACELIFT-01	HIGH	09/1996-2000后期四驱柴油外廓。	READY
4787	4787	Hatchback	Cuore IV	L501		EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	MEDIUM	3门/5门外廓尺寸一致，输入未区分门数。	READY
4788	4788	Convertible	MX-5 I	NA	2	EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	HIGH		READY
4789	4789	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-4D-01	HIGH		READY
4790	4790	Sedan	Xedos 9	TA	4	EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	HIGH		READY
4791	4791	Sedan	Kaefer 1302	1302	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
4792	4792	Convertible	Kadett E	E	2	EU-OPEL-KADETT-E-CONVERTIBLE-16-01	HIGH		READY
4793	4793	Coupe	Corrado facelift	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH		READY
4794_l1	4794	MPV	T1 (W601)			EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	601.371/601.376短轴客车外廓。	READY
4794_l2	4794	MPV	T1 (W601)	601.377		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	HIGH	601.377长轴客车外廓。	READY
4795	4795	Sedan	Orion II	AFF	4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
4796	4796	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
4797	4797	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-01	HIGH		READY
4798	4798	Hatchback	Renault 19 II	B53		EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	三门与五门外廓尺寸一致，输入未区分门数。	READY
4799	4799	Hatchback	Renault 19 II	B53		EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	三门与五门外廓尺寸一致，输入未区分门数。	READY
4800	4800	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH		READY
4801	4801	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH		READY
4802	4802	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4803	4803	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4804	4804	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4805	4805	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH		READY
4806	4806	Hatchback	Clio I	57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
4807	4807	Hatchback	Clio I	57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
4808	4808	Hatchback	Horizon	C2	5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
4809	4809	Hatchback	Corolla VII E100	CE100	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH		READY
4810	4810	Hatchback	Corolla VII E100	CE100	5	EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	HIGH		READY
4811	4811	Wagon	Corolla VII E100	CE100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH		READY
4812	4812	SUV	Land Cruiser 80	J80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
4813	4813	SUV	4Runner II	N130	5	EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	HIGH		READY
4814	4814	Wagon	Lancer V Station Wagon	CBW	5	EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	HIGH		READY
4815	4815	Wagon	Lancer V Station Wagon	CBW	5	EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	HIGH		READY
4816	4816	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4817	4817	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4818	4818	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4819	4819	Wagon	Octavia II facelift	1Z	5	EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	HIGH		READY
4820	4820	Pickup	Caddy I	14D	2	EU-VW-CADDY-I-14D-PICKUP-01	HIGH		READY
4821	4821	Hatchback	323 C IV	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
4822	4822	Hatchback	323 C IV	BG	3	EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	HIGH		READY
4823	4823	Hatchback	626 IV	GE	5	EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	HIGH		READY
4824	4824	Wagon	626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH		READY
4825	4825	Sedan	Xedos 6	CA	4	EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	HIGH		READY
4826	4826	Wagon	850	850	5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
4827	4827	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
4828	4828	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-TURBO-01	HIGH		READY
4829_l1h1_6seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-6SEAT-01	HIGH	L1H1六座物理外廓。	READY
4829_l1h1_9seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-9SEAT-01	HIGH	L1H1九座物理外廓。	READY
4829_l2h1_6seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-6SEAT-01	HIGH	L2H1六座物理外廓。	READY
4829_l2h1_9seat	4829	MPV	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-9SEAT-01	HIGH	L2H1九座物理外廓。	READY
4830_l1h1_1t	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-1T-01	HIGH	L1H1 1.0t载荷级物理外廓。	READY
4830_l1h1_12t	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-12T-01	HIGH	L1H1 1.2t载荷级物理外廓。	READY
4830_l1h2	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H2-01	HIGH	L1H2短轴高顶物理外廓。	READY
4830_l2h1	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H1-01	HIGH	L2H1长轴低顶物理外廓。	READY
4830_l2h2	4830	Van	Primastar I	X83		EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H2-01	HIGH	L2H2长轴高顶物理外廓。	READY
4831	4831	Hatchback	Samara I			EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	三门/五门外廓尺寸一致，输入未区分门数。	READY
4832	4832	Coupe	S-Class Coupe C126 facelift	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-500SEC-FACELIFT-01	HIGH		READY
4833_carreras	4833	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	HIGH	Carrera S narrow-body branch.	READY
4833_gts	4833	Coupe	911 (997.2)	997	2	EU-PORSCHE-911-997-2-COUPE-GTS-01	HIGH	GTS wide-body branch.	READY
4834	4834	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4835	4835	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4836	4836	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	HIGH		READY
4837	4837	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	HIGH		READY
4838	4838	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	HIGH		READY
4839	4839	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-RWD-01	HIGH		READY
4840	4840	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	HIGH		READY
4841	4841	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	HIGH		READY
4842	4842	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4843	4843	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4844	4844	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
4845	4845	Sedan	Polo II / Derby	86C		EU-VW-POLO-II-TYPE86C-SEDAN-01	MEDIUM	2门/4门资料口径一致，输入未区分门数。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4601-4700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402	Auto-Data Lada 21099 1.5	https://www.auto-data.net/en/lada-21099-1.5-70hp-13270
EU-NISSAN-MAXIMA-IV-A32-SEDAN-4D-01	4765	1770	1430	Auto-Data Nissan Maxima QX IV (A32) 2.0 V6	https://www.auto-data.net/en/nissan-maxima-qx-iv-a32-2.0-v6-140hp-1917
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714	Auto-Data Citroen Evasion (22) 1.9 TD	https://www.auto-data.net/en/citroen-evasion-22-1.9-td-90hp-14904
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Auto-Data Peugeot 806 (221) 2.0 Turbo	https://www.auto-data.net/en/peugeot-806-221-2.0-turbo-147hp-5479
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410	Auto-Data Renault 19 Cabriolet (D53) facelift	https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-generation-2187
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693	Auto-Data Renault Espace II (J63) 2.1 TD	https://www.auto-data.net/en/renault-espace-ii-j63-2.1-td-88hp-10508
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449	Auto-Data Lancia Dedra Station Wagon (835) 1.6	https://www.auto-data.net/en/lancia-dedra-station-wagon-835-1.6-90hp-5002
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425	Auto-Data Alfa Romeo 146 (930) 1.7 i.e.	https://www.auto-data.net/en/alfa-romeo-146-930-1.7-i.e.-129hp-1274
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420	Automobile-Catalog Fiat Panda 750 L	https://www.automobile-catalog.com/car/1986/715055/fiat_panda_750_l_5-speed.html
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468	Automobile-Catalog Fiat Panda 1000 4x4	https://www.automobile-catalog.com/car/1991/31340/fiat_panda_1000_4x4.html
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440	Auto-Data Lancia Y10 (156) specification archive	https://www.auto-data.net/en/lancia-y10-156-generation-1167
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460	Auto-Data Lancia Y10 (156) 4WD specification archive	https://www.auto-data.net/en/lancia-y10-156-generation-1167
EU-FIAT-ULYSSE-I-220-MPV-01	4454	1834	1714	Auto-Data Fiat Ulysse I (220) specification archive	https://www.auto-data.net/en/fiat-ulysse-i-22-220-generation-1615
EU-FIAT-BARCHETTA-183-CONVERTIBLE-2D-01	3916	1640	1265	Auto-Data Fiat Barchetta (183) 1.8 16V	https://www.auto-data.net/en/fiat-barchetta-183-1.8-16v-130hp-7035
EU-LANCIA-KAPPA-838-SEDAN-01	4687	1822	1462	Auto-Data Lancia Kappa (838) 2.0 LE Automatic	https://www.auto-data.net/en/lancia-kappa-838-2.0-le-146hp-automatic-28665
EU-ALFA-ROMEO-155-167-SEDAN-WIDEBODY-1440-01	4443	1730	1440	Auto-Data Alfa Romeo 155 (167) 2.0 Twin Spark 16V	https://www.auto-data.net/en/alfa-romeo-155-167-2.0-twin-spark-16v-150hp-1371
EU-LEXUS-LS-I-XF10-SEDAN-4D-01	5005	1820	1425	Auto-Data Lexus LS I (XF10) specification archive	https://www.auto-data.net/en/lexus-ls-i-generation-1357
EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-PREFL-01	4430	1810	1170	Auto-Data Honda NSX I (NA1) Targa 3.0 V6 VTEC	https://www.auto-data.net/en/honda-nsx-i-na1-targa-3.0-v6-vtec-274hp-11430
EU-HONDA-NSX-I-NA1-CONVERTIBLE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX I facelift Targa 3.0 V6 VTEC	https://www.auto-data.net/en/honda-nsx-i-facelift-na1-targa-3.0-v6-vtec-274hp-11431
EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	4750	1790	1640	BASt IMPROVER Final Report; UltimateSpecs Honda Shuttle 2.2i	https://www.bast.de/DE/Publikationen/BerichteBASt/Fachveroeffentlichungen/Fahrzeugtechnik/Unterseiten/F-improver-subproject-1.pdf?__blob=publicationFile&v=1;https://www.ultimatespecs.com/car-specs/Honda/7993/Honda-Shuttle-22i.html
EU-BMW-M6-F12-CONVERTIBLE-2D-01	4898	1899	1368	Auto-Data BMW M6 Convertible (F12M); Auto-Data BMW M6 Convertible (F12M LCI)	https://www.auto-data.net/en/bmw-m6-convertible-f12m-4.4-v8-560hp-17796;https://www.auto-data.net/en/bmw-m6-convertible-f12m-lci-facelift-2014-4.4-v8-560hp-33137
EU-SUZUKI-VITARA-I-SUV-CLOSED-01	3620	1630	1665	Auto-Data Suzuki Vitara (ET/TA) 1.6 i	https://www.auto-data.net/en/suzuki-vitara-et-ta-1.6-i-80hp-16428
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390	Auto-Data Suzuki Baleno Hatchback (EG) 1.3 i 16V	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.3-i-16v-85hp-automatic-23930
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390	Auto-Data Suzuki Baleno Hatchback (EG) 1.6 i 16V	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.6-i-16v-98hp-16482
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	3870	1680	1395	Automobile-Catalog Suzuki Baleno Hatchback 1.6 GL 4WD	https://www.automobile-catalog.com/car/1996/3387020/suzuki_baleno_hatchback_1_6_gl_4wd.html
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390	Auto-Data Suzuki Baleno (EG) 1.3 sedan; Automobile-Catalog Suzuki Baleno Sedan 1.6 GLX 4WD	https://www.auto-data.net/en/suzuki-baleno-eg-1995-1.3-i-16v-85hp-automatic-23934;https://www.automobile-catalog.com/car/1995/3387065/suzuki_baleno_sedan_1_6_glx_4wd.html
EU-TOYOTA-CARINA-E-VI-T190-WAGON-5D-01	4530	1695	1440	Auto-Data Toyota Carina E Sportswagon (T190) 1.8 i	https://www.auto-data.net/en/toyota-carina-e-sportswagon-t190-1.8-i-107hp-5396
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900	Auto-Data Toyota Land Cruiser (J80) 4.2 TD 24V	https://www.auto-data.net/en/toyota-land-cruiser-j80-4.2-td-24v-170hp-4wd-3723
EU-NISSAN-MICRA-II-K11-HATCHBACK-01	3746	1595	1440	Auto-Data Nissan Micra II (K11) specification archive	https://www.auto-data.net/en/nissan-micra-k11-generation-208
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395	Automobile-Catalog Nissan Sunny 1.4 LX 3d	https://www.automobile-catalog.com/car/1991/2247695/nissan_sunny_1_4_lx_3d.html
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395	Automobile-Catalog Nissan Sunny 1.4 LX 5d	https://www.automobile-catalog.com/car/1991/2247725/nissan_sunny_1_4_lx_5d.html
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-PREFL-01	4595	1695	1855	Automobile-Catalog Mitsubishi Space Gear 2000 GLX; Automobile-Catalog Mitsubishi Space Gear 2500 TD GLX	https://www.automobile-catalog.com/car/1995/2019935/mitsubishi_space_gear_2000_glx.html;https://www.automobile-catalog.com/car/1995/2019980/mitsubishi_space_gear_2500_td_glx.html
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-2WD-FACELIFT-01	4655	1695	1855	Automobile-Catalog Mitsubishi Space Gear 2000 GLX (Sep 1996); Auto-Data Mitsubishi Space Gear (PA0) 2.0 i 16V GL	https://www.automobile-catalog.com/car/1996/2020010/mitsubishi_space_gear_2000_glx.html;https://www.auto-data.net/en/mitsubishi-space-gear-pa0-2.0-i-16v-gl-113hp-15460
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-PREFL-01	4595	1695	1965	Automobile-Catalog Mitsubishi Space Gear 2400 GLX 4WD; Automobile-Catalog Mitsubishi Space Gear 2500 TD GLX 4WD	https://www.automobile-catalog.com/car/1995/2020040/mitsubishi_space_gear_2400_glx_4wd.html;https://www.automobile-catalog.com/car/1995/2019995/mitsubishi_space_gear_2500_td_glx_4wd.html
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-PETROL-FACELIFT-01	4655	1695	1855	Auto-Data Mitsubishi Space Gear (PA0) 2.4 i 16V GL 4WD	https://www.auto-data.net/en/mitsubishi-space-gear-pa0-2.4-i-16v-gl-4wd-128hp-15461
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-4WD-DIESEL-FACELIFT-01	4655	1695	1965	Auto-Data Mitsubishi Space Gear (PA0) 2.5 TD 4WD	https://www.auto-data.net/en/mitsubishi-space-gear-pa0-2.5-td-4wd-99hp-15463
EU-DAIHATSU-CUORE-IV-L501-HATCHBACK-01	3295	1395	1435	Auto-Data Daihatsu Cuore IV (L501) 0.8	https://www.auto-data.net/en/daihatsu-cuore-iv-l501-0.8-44hp-4561
EU-MAZDA-MX-5-I-NA-CONVERTIBLE-2D-01	3975	1675	1230	Auto-Data Mazda MX-5 I (NA) specification archive	https://www.auto-data.net/en/mazda-mx-5-i-na-generation-1235
EU-MAZDA-323-S-V-BA-SEDAN-4D-01	4340	1710	1420	Auto-Data Mazda 323 S V (BA) specification archive	https://www.auto-data.net/en/mazda-323-s-v-ba-generation-1272
EU-MAZDA-XEDOS-9-TA-SEDAN-4D-01	4825	1770	1395	Auto-Data Mazda Xedos 9 (TA) specification archive	https://www.auto-data.net/en/mazda-xedos-9-ta-generation-1267
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500	Auto-Data Volkswagen Kaefer 1302 1.6	https://www.auto-data.net/en/volkswagen-kaefer-1302-1.6-48hp-8356
EU-OPEL-KADETT-E-CONVERTIBLE-16-01	3998	1663	1385	Auto-Data Opel Kadett E Cabrio 1.6i	https://www.auto-data.net/en/opel-kadett-e-cabrio-1.6i-82hp-25922
EU-VW-CORRADO-53I-COUPE-FACELIFT-01	4050	1690	1310	Auto-Data Volkswagen Corrado (53I) 2.0 i	https://www.auto-data.net/en/volkswagen-corrado-53i-2.0-i-115hp-8598
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170	Mercedes-Benz T1 technical specification archive	https://www.automobile-catalog.com/model/mercedes-benz/t1.html
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240	Mercedes-Benz T1 technical specification archive	https://www.automobile-catalog.com/model/mercedes-benz/t1.html
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389	Auto-Data Ford Orion II (AFF) specification archive	https://www.auto-data.net/en/ford-orion-ii-aff-generation-1737
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428	Auto-Data Ford Sierra Turnier II 2.8 4x4	https://www.auto-data.net/en/ford-sierra-turnier-ii-2.8-4x4-150hp-7610
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426	Automobile-Catalog Peugeot 305 Break GL	https://www.automobile-catalog.com/car/1983/2568200/peugeot_305_break_gl.html
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417	Auto-Data Renault 19 II hatchback specification archive	https://www.auto-data.net/en/renault-19-model-1048
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417	Auto-Data Renault 19 Chamade (L53) facelift specification archive	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-generation-2186
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443	Auto-Data Renault Safrane I (B54) specification archive	https://www.auto-data.net/en/renault-safrane-i-b54-generation-2157
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Auto-Data Renault Clio I specification archive	https://www.auto-data.net/en/renault-clio-i-generation-2162
EU-TALBOT-HORIZON-HATCHBACK-01	3960	1680	1410	Automobile-Catalog Talbot Horizon specification archive	https://www.automobile-catalog.com/model/talbot/horizon.html
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380	Auto-Data Toyota Corolla VII Compact (E100) specification archive	https://www.auto-data.net/en/toyota-corolla-compact-e100-generation-1534
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375	Auto-Data Toyota Corolla VII Liftback (E100) specification archive	https://www.auto-data.net/en/toyota-corolla-liftback-e100-generation-1535
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460	Auto-Data Toyota Corolla VII Wagon (E100) specification archive	https://www.auto-data.net/en/toyota-corolla-wagon-e100-generation-1536
EU-TOYOTA-4RUNNER-II-N130-SUV-5D-01	4490	1690	1745	Auto-Data Toyota 4Runner II (N130) specification archive	https://www.auto-data.net/en/toyota-4runner-ii-n130-generation-1513
EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	4270	1690	1465	Auto-Data Mitsubishi Lancer V Station Wagon (CBW) 1.6 16V	https://www.auto-data.net/en/mitsubishi-lancer-v-station-wagon-cbw-1.6-16v-113hp-11637
EU-VW-CADDY-I-14D-PICKUP-01	4380	1640	1490	Auto-Data Volkswagen Caddy I (14D) 1.6	https://www.auto-data.net/en/vw-caddy-i-14d-1.6-75hp-1294
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468	Auto-Data Skoda Octavia II Combi (1Z) facelift 2.0 TDI 4x4	https://www.auto-data.net/en/skoda-octavia-combi-ii-1z-facelift-2.0-tdi-4x4-110hp-12675
EU-MAZDA-323-C-IV-BG-HATCHBACK-3D-01	3995	1670	1400	Auto-Data Mazda 323 C IV (BG) 1.7 D	https://www.auto-data.net/en/mazda-323-c-iv-bg-1.7-d-56hp-10476
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4680	1750	1400	Auto-Data Mazda 626 IV (GE) Hatchback 2.0 D Comprex	https://www.auto-data.net/en/mazda-626-iv-ge-hatchback-2.0-d-comprex-75hp-10183
EU-MAZDA-626-III-GV-WAGON-5D-01	4660	1755	1440	Auto-Data Mazda 626 III (GV) Station Wagon 2.0 D Comprex	https://www.auto-data.net/en/mazda-626-iii-gv-station-wagon-2.0-d-comprex-75hp-10171
EU-MAZDA-XEDOS-6-CA-SEDAN-4D-01	4560	1700	1355	Auto-Data Mazda Xedos 6 (CA) specification archive	https://www.auto-data.net/en/mazda-xedos-6-ca-generation-1266
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Auto-Data Volvo 850 Estate specification archive	https://www.auto-data.net/en/volvo-850-estate-generation-913
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424	Ford Mondeo 1995 UK official brochure archive	https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Mondeo-1995-UK.pdf
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300	Auto-Data Porsche 911 Coupe (997 II) Turbo 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-turbo-3.8-500hp-pdk-21424
EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-6SEAT-01	4782	1904	1942	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L1H1-9SEAT-01	4782	1904	1963	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-6SEAT-01	5182	1904	1952	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-MPV-L2H1-9SEAT-01	5182	1904	1968	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-1T-01	4782	1904	1955	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H1-12T-01	4782	1904	1963	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L1H2-01	4782	1904	2492	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H1-01	5182	1904	1962	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-I-X83-VAN-L2H2-01	5182	1904	2477	Nissan Primastar official UK brochure (2011 archive copy)	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402	Auto-Data Lada 2109 specification archive	https://www.auto-data.net/en/lada-2109-model-1418
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-500SEC-FACELIFT-01	4935	1828	1407	Auto-Data Mercedes-Benz 500 SEC (C126 facelift)	https://www.auto-data.net/en/mercedes-benz-s-class-coupe-c126-facelift-1985-500-sec-v8-265hp-automatic-13125
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300	Auto-Data Porsche 911 Coupe (997 II) Carrera S 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-carrera-s-3.8-408hp-21407
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300	Auto-Data Porsche 911 Coupe (997 II) Carrera GTS 3.8	https://www.auto-data.net/en/porsche-911-coupe-997-ii-carrera-gts-3.8-408hp-21414
EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-RWD-01	4740	1740	1425	Auto-Data Mercedes-Benz E-Class (W124) E 200 D	https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-200-d-75hp-12995
EU-MERCEDES-BENZ-E-CLASS-W124-SEDAN-4MATIC-01	4740	1740	1452	Auto-Data Mercedes-Benz E-Class (W124) E 300 4MATIC; Auto-Data Mercedes-Benz E-Class (W124) E 300 Turbodiesel 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-300-180hp-4matic-automatic-13002;https://www.auto-data.net/en/mercedes-benz-e-class-w124-e-300-turbodiesel-147hp-4matic-automatic-13005
EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-RWD-01	4765	1740	1490	Auto-Data Mercedes-Benz E-Class T-Modell (S124) E 300 T Turbodiesel	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-turbodiesel-147hp-automatic-13027
EU-MERCEDES-BENZ-E-CLASS-S124-WAGON-4MATIC-01	4765	1740	1498	Auto-Data Mercedes-Benz E-Class T-Modell (S124) E 300 T 4MATIC; Auto-Data Mercedes-Benz E-Class T-Modell (S124) E 300 T Turbodiesel 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-180hp-4matic-automatic-13025;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s124-e-300-t-turbodiesel-147hp-4matic-automatic-13028
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350	Auto-Data Volkswagen Polo Classic II (86C) 1.3 D	https://www.auto-data.net/en/vw-polo-classic-ii-86c-1.3-d-45hp-1879
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4601-4700_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4601-4700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4601-4700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6193 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1892 行）

- 尺寸冲突协调：
  - EU-MAZDA-626-IV-GE-HATCHBACK-5D-01 -> EU-MAZDA-626-IV-GE-HATCHBACK-5D-02：4695x1750x1390 与 4680x1750x1400，创建新尺寸组
  - EU-MAZDA-626-III-GV-WAGON-5D-01 -> EU-MAZDA-626-III-GV-WAGON-5D-02：4610x1690x1430 与 4660x1755x1440，创建新尺寸组
