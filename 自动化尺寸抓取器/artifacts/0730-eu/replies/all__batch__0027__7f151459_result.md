# 任务：all 第 2601-2700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0027__7f151459


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2601-2700 行

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
all 第 2601-2700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	3860	1667	1510
EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	3941	1728	1524
EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	3941	1728	1538
EU-CITROEN-C3-III-HATCHBACK-PREFL-01	3996	1749	1474
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570
EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	4731	1936	1652
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684
EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	4236	1805	1667
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	5120	1934	1850
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465
EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	4249	1753	1460
EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	4249	1753	1460
EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	4587	1753	1458
EU-OPEL-ASTRA-H-FAMILY-WAGON-01	4515	1753	1500
EU-OPEL-ASTRA-H-HATCHBACK-5D-FACELIFT-01	4249	1753	1460
EU-OPEL-ASTRA-H-SEDAN-01	4587	1753	1458
EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	4515	1753	1500
EU-PEUGEOT-206-PLUS-HATCHBACK-01	3872	1655	1446
EU-PEUGEOT-207-SW-WAGON-PREFL-01	4156	1748	1527
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466
EU-RENAULT-CAPTUR-I-SUV-01	4122	1778	1566
EU-SUBARU-IMPREZA-II-GD-RB320-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GG-GB270-WAGON-01	4465	1695	1485
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480
EU-VOLVO-760-765-WAGON-FACELIFT-01	4790	1760	1435
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	E-Klasse	E 450 4-matic	Cabriolet	Allrad	Benzin	270	367	Aug 2018	-	2024-03-01	132378
Subaru	Impreza	2.0 WRX STI Prodrive Performance Package AWD	Stufenheck	Allrad	Benzin	224	305	Apr 2001	Oct 2002	2024-03-01	132406
Toyota	Land cruiser van	3.0 D4D 4WD	Kasten/Geländewagen geschlossen	Allrad	Diesel	140	190	Jan 2011	-	2024-03-01	132409
Rolls-royce	Cullinan	V12	SUV	Allrad	Benzin	420	571	Aug 2018	-	2024-03-01	132411
Skoda	Fabia i praktik	1.4	Kasten/Kombi	Frontantrieb	Benzin	55	75	May 2004	Dec 2007	2024-03-01	132416
Renault	Megane ii hatchback van	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	60	82	Aug 2003	Feb 2008	2024-03-01	132419
Renault	Captur i	1.3 TCE 150	Schrägheck	Frontantrieb	Benzin	110	150	Mar 2018	Dec 2019	2025-12-01	132439
Aixam	500	0.5 D	Cabriolet	Frontantrieb	Diesel	10	14	Oct 1996	Jul 2007	2024-03-01	132441
Mercedes-benz	A-Klasse	A 180 D	Stufenheck	Frontantrieb	Diesel	85	116	Sep 2018	-	2024-03-01	132444
Mercedes-benz	A-Klasse	A 200	Stufenheck	Frontantrieb	Benzin	120	163	Sep 2018	-	2024-03-01	132445
Mercedes-benz	A-Klasse	A 220 4-matic	Stufenheck	Allrad	Benzin	140	190	Sep 2018	-	2024-03-01	132446
Mercedes-benz	A-Klasse	A 250	Stufenheck	Frontantrieb	Benzin	165	224	Sep 2018	-	2024-03-01	132447
Mercedes-benz	A-Klasse	A 250 4-matic	Stufenheck	Allrad	Benzin	165	224	Sep 2018	-	2024-03-01	132448
Volvo	760	2.4 Tdic	Stufenheck	Heckantrieb	Diesel	90	122	Sep 1987	Aug 1990	2024-03-01	132454
VW	Polo	1.6	Stufenheck	Frontantrieb	Benzin	66	90	May 2015	Mar 2020	2024-03-01	132464
BMW	X3	Xdrive M40 I	SUV	Allrad	Benzin	260	354	Sep 2018	Aug 2019	2024-03-01	132498
Fiat	500x	2.0 D Multijet 4X4	SUV	Allrad	Diesel	110	150	Sep 2018	Sep 2020	2024-03-01	132500
Fiat	500x	1.3	SUV	Frontantrieb	Benzin	110	150	Sep 2018	-	2024-03-01	132501
Fiat	500x	1	SUV	Frontantrieb	Benzin	88	120	Sep 2018	-	2024-03-01	132508
Peugeot	Bipper	1.3 HDI 80 / Bluehdi 80	Kasten/Großraumlimousine	Frontantrieb	Diesel	59	80	Dec 2015	-	2024-03-01	132515
Peugeot	301	1.6 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	85	116	Jul 2014	-	2024-03-01	132516
Ford	Focus iv	1.5 Ecoboost	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2018	Nov 2025	2026-02-01	132517
Ford	Focus iv	1.5 Ecoboost	Schrägheck	Frontantrieb	Benzin	134	182	Sep 2018	Nov 2025	2026-02-01	132518
Ford	Focus iv turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	110	150	Sep 2018	Nov 2025	2026-02-01	132520
Ford	Focus iv turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	134	182	Sep 2018	Nov 2025	2026-02-01	132521
KIA	Sportage iv	1.6 Crdi	SUV	Frontantrieb	Diesel	85	116	Jul 2018	Sep 2022	2024-03-01	132529
Peugeot	508 sw	2.2 HDI	Kasten/Kombi	Frontantrieb	Diesel	150	204	Nov 2011	-	2024-03-01	132533
KIA	Sportage iv	1.6 Crdi	SUV	Frontantrieb	Diesel	100	136	Jul 2018	Sep 2022	2024-03-01	132534
KIA	Sportage iv	1.6 Crdi AWD	SUV	Allrad	Diesel	100	136	Jul 2018	Sep 2022	2024-03-01	132537
Opel	Astra j gtc	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	96	131	Jan 2012	Oct 2015	2024-05-01	132538
Citroën	C4 ii	2.0 HDI / Bluehdi 160	Schrägheck	Frontantrieb	Diesel	120	163	Oct 2010	-	2024-03-01	132542
Peugeot	207/207+	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	54	73	Aug 2007	Dec 2013	2024-03-01	132551
Citroën	Xm	2	Kombi	Frontantrieb	Benzin	89	121	Aug 1994	Jul 1999	2024-03-01	132553
Citroën	Xm	2	Schrägheck	Frontantrieb	Benzin	89	121	Aug 1994	Jul 1999	2024-03-01	132557
Maserati	Biturbo	2	Cabriolet	Heckantrieb	Benzin	138	188	Jan 1987	Dec 1990	2024-03-01	132559
Maserati	Biturbo	2	Cabriolet	Heckantrieb	Benzin	164	223	Jan 1989	Dec 1991	2024-03-01	132560
KIA	Ceed	1.0 T-gdi	Kombi	Frontantrieb	Benzin	88	120	May 2018	-	2024-03-01	132563
KIA	Ceed	1.4	Kombi	Frontantrieb	Benzin	73	99	Apr 2018	Dec 2020	2024-08-01	132568
KIA	Ceed	1.4 T-gdi	Kombi	Frontantrieb	Benzin	103	140	Apr 2018	Dec 2020	2024-08-01	132569
Citroën	C6	3.0 HDI	Stufenheck	Frontantrieb	Diesel	155	211	Jun 2009	Dec 2010	2024-03-01	132571
KIA	Ceed	1.6 Crdi 115	Kombi	Frontantrieb	Diesel	85	116	May 2018	-	2024-03-01	132574
Citroën	Xsara	1.6 16V LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jun 2004	Dec 2010	2024-03-01	132575
Citroën	C5	2.2 HDI	Stufenheck	Frontantrieb	Diesel	120	163	Apr 2009	Dec 2011	2024-07-01	132580
KIA	Ceed	1.6 Crdi 136	Kombi	Frontantrieb	Diesel	100	136	May 2018	-	2024-03-01	132581
Citroën	C3 i	1.4 I Bivalent	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	49	67	Jan 2008	Dec 2009	2024-03-01	132585
Peugeot	207 sw	1.6 HDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Aug 2007	Dec 2012	2024-03-01	132587
Jeep	Renegade	1.6 CRD	SUV	Frontantrieb	Diesel	70	95	Nov 2016	-	2024-03-01	132589
Opel	Zafira	1.6 Flexfuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	85	116	Aug 2008	Dec 2012	2024-03-01	132592
Jaguar	Xf sportbrake	2.0 AWD	Kombi	Allrad	Benzin	221	300	Aug 2018	-	2024-03-01	132593
Opel	Astra h	1.6	Stufenheck	Frontantrieb	Benzin	77	105	Feb 2007	Jun 2010	2024-03-01	132594
Opel	Astra h	1.4	Stufenheck	Frontantrieb	Benzin	66	90	Feb 2007	Jun 2010	2024-03-01	132595
Jaguar	E-Pace	2.0 P200 AWD	SUV	Allrad	Benzin	147	200	Aug 2018	-	2024-03-01	132596
Jaguar	F-Pace	5.0 Scv8 SVR AWD	SUV	Allrad	Benzin	405	551	Aug 2018	-	2024-03-01	132598
Peugeot	207	1.6 VTI	Kasten/Schrägheck	Frontantrieb	Benzin	88	120	Mar 2007	Dec 2012	2024-03-01	132600
Peugeot	307	2.0 HDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Apr 2003	Apr 2008	2024-03-01	132607
Peugeot	307	2.0 HDI	Kasten/Kombi	Frontantrieb	Diesel	100	136	Apr 2004	Nov 2007	2024-03-01	132608
Opel	Zafira	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	76	103	Oct 2003	Jun 2005	2024-03-01	132615
Peugeot	307	1.6 HDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Apr 2006	Oct 2008	2024-03-01	132616
KIA	Stonic	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	101	Aug 2018	-	2024-03-01	132617
Opel	Astra g cc	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	76	103	Nov 2002	Jun 2007	2024-03-01	132619
Opel	Astra g caravan	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	76	103	Jun 2002	Jul 2004	2024-03-01	132620
KIA	Stonic	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2018	Dec 2025	2026-03-01	132622
KIA	Stonic	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	100	136	Aug 2018	Dec 2025	2026-03-01	132624
Opel	Vectra b	2.2 I 16V	Stufenheck	Frontantrieb	Benzin	102	139	Jul 2000	Jul 2002	2024-03-01	132626
Opel	Vectra b cc	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	85	116	Jul 2000	Jul 2003	2024-03-01	132627
Opel	Vectra b cc	2.2 I 16V	Schrägheck	Frontantrieb	Benzin	102	139	Jul 2000	Jul 2002	2024-03-01	132628
Hyundai	Kona	1.6 Crdi E-vgt	SUV	Frontantrieb	Diesel	100	136	Aug 2018	Aug 2021	2024-05-01	132630
Hyundai	Kona	1.6 Crdi E-vgt AWD	SUV	Allrad	Diesel	100	136	Aug 2018	Aug 2021	2024-05-01	132632
Hyundai	Kona	1.6 Crdi	SUV	Frontantrieb	Diesel	85	116	Aug 2018	Nov 2020	2024-05-01	132633
Opel	Vectra b caravan	2.0 I 16V	Kombi	Frontantrieb	Benzin	85	116	Jul 2000	Jul 2003	2024-03-01	132635
Opel	Vectra b caravan	2.2 I 16V	Kombi	Frontantrieb	Benzin	102	139	Jul 2000	Jul 2002	2024-03-01	132637
Opel	Zafira	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	74	101	Apr 1999	Jun 2005	2024-03-01	132638
Peugeot	406	1.8 Bifuel	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	85	116	Sep 2000	May 2004	2024-03-01	132640
Audi	Q7	50 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	210	286	Jul 2018	-	2024-03-01	132641
Audi	Q7	45 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	170	231	Jul 2018	-	2024-03-01	132642
Ford	Mondeo v	1.5 Ecoboost	Schrägheck	Frontantrieb	Benzin	121	165	May 2018	Mar 2022	2026-04-01	132643
Opel	Astra g	1.4 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Mar 1998	Jan 2005	2024-03-01	132644
Peugeot	406	1.8 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	85	116	Oct 2000	Feb 2004	2024-03-01	132645
Ford	Mondeo v turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	121	165	May 2018	Mar 2022	2026-04-01	132646
Peugeot	206	1.6 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jul 2000	Apr 2009	2024-03-01	132647
Opel	Astra g caravan	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	74	101	Mar 1998	Jul 2004	2024-03-01	132649
Audi	A7 sportback	40 TDI Mild Hybrid	Schrägheck	Frontantrieb	Diesel/Elektro	150	204	Sep 2018	-	2024-03-01	132656
Opel	Frontera	2.0 I	Geländewagen geschlossen	Allrad	Benzin	85	115	May 1993	Aug 1998	2024-11-01	132657
Peugeot	206 van	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Sep 2002	Feb 2007	2024-03-01	132659
Mercedes-benz	Gl-Klasse	GL 350 CDI / Bluetec 4-matic	SUV	Allrad	Diesel	183	249	Jul 2012	Oct 2015	2024-03-01	132662
Peugeot	106 ii	1.1 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	44	60	Apr 1996	Mar 2001	2024-03-01	132677
Citroën	C3 ii	1.6 Bluehdi	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Mar 2015	Sep 2016	2024-03-01	132684
Citroën	C4 ii	1.6 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	68	92	Jun 2010	-	2024-03-01	132690
Citroën	C4 ii	1.6 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	82	111	Nov 2009	-	2024-03-01	132693
Citroën	C3 ii	1.4 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Jun 2010	Sep 2016	2024-03-01	132701
Citroën	C5	2.0 HDI	Kasten/Kombi	Frontantrieb	Diesel	80	109	Jun 2002	Aug 2004	2024-07-01	132705
Citroën	C4 i	2.0 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	100	136	Feb 2005	Dec 2010	2024-03-01	132706
KIA	Optima	2	Stufenheck	Frontantrieb	Benzin	110	150	Sep 2015	Dec 2019	2024-03-01	132710
Citroën	C5	2.2 HDI	Kasten/Kombi	Frontantrieb	Diesel	98	133	Jun 2002	Aug 2004	2024-07-01	132713
Citroën	C2	1.4 HDI	Kasten/Schrägheck	Frontantrieb	Diesel	51	69	Nov 2003	Apr 2005	2024-03-01	132714
Citroën	C2	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Nov 2003	Dec 2009	2024-03-01	132715
Citroën	C5	1.8 16V	Kasten/Kombi	Frontantrieb	Benzin	85	116	Sep 2004	Aug 2005	2024-07-01	132716
Citroën	C5	1.6 HDI	Kasten/Kombi	Frontantrieb	Diesel	80	109	Sep 2004	Jan 2008	2024-07-01	132719
Citroën	C5	2.0 HDI	Kasten/Kombi	Frontantrieb	Diesel	100	136	Sep 2004	Jan 2008	2024-07-01	132721
Citroën	C5	2.0 16V	Kasten/Kombi	Frontantrieb	Benzin	103	140	Nov 2004	Jan 2008	2024-07-01	132724


--- Round 1 / 首次发送 ---
更新点

* 先按物理外廓聚类，完成 40 个输入 Ktype 的映射，共形成 46 条 READY 映射行。
* 复用跨批次已有尺寸组 14 个；本轮首次闭合尺寸组 13 个。
* Focus IV Turnier、Peugeot 207 SW、Hyundai Kona 和 Citroën C3 II 的生产区间跨越尺寸或外廓阶段，已拆分派生行，没有保留无后缀基础行。
* Cullinan、A-Class V177、Fiat 500X AWD、Astra J GTC、Ceed Sportswagon、Stonic 和 Kona 的尺寸由厂商或官方资料闭合。([BMW Group PressClub][1])
* Subaru Prodrive、Citroën C6、Peugeot 207 SW facelift、Jaguar XF Sportbrake 和 E-PACE 已完成独立尺寸组核对。([中古車ならスグダス | SUBARU （公式）][2])

当前批次进度

* 输入 Ktype：100
* READY Ktype：40
* READY 映射行：46
* PENDING Ktype：60
* 当前引用尺寸组：27
* 本轮新建尺寸组：13
* 复用已有尺寸组：14
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132378	132378	Convertible	E-Class W213	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	A238双门标准车身敞篷版。	READY
132406	132406	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-PRODRIVE-SEDAN-01	HIGH	GD四门Prodrive Performance Package外廓。	READY
132411	132411	SUV	Cullinan I		5	EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	HIGH	第一代Cullinan标准车身。	READY
132439	132439	SUV	Captur I	J87	5	EU-RENAULT-CAPTUR-I-SUV-01	HIGH		READY
132444	132444	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132445	132445	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132446	132446	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132447	132447	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132448	132448	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132464	132464	Sedan	Polo V	602	4	EU-VW-POLO-V-602-SEDAN-FACELIFT-01	HIGH	602四门改款轿车。	READY
132498	132498	SUV	X3 III	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01标准车身，M40i动力不改变外廓。	READY
132500	132500	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	HIGH	改款后4x4 Cross外廓。	READY
132520_prefl	132520	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132520_facelift	132520	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132521_prefl	132521	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132521_facelift	132521	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132529	132529	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
132534	132534	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
132537	132537	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	AWD不改变该外廓尺寸。	READY
132538	132538	Hatchback	Astra J		3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	HIGH	GTC三门独立宽体外廓。	READY
132563	132563	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132568	132568	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132569	132569	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132571	132571	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH	第一代C6四门轿车。	READY
132574	132574	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132581	132581	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132585	132585	Hatchback	C3 I		5	EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	HIGH	第一代C3改款五门外廓。	READY
132587_prefl	132587	Wagon	207 I		5	EU-PEUGEOT-207-SW-WAGON-PREFL-01	HIGH	Ktype生产区间跨2009改款，改款前分支。	READY
132587_facelift	132587	Wagon	207 I		5	EU-PEUGEOT-207-SW-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨2009改款，改款后分支。	READY
132593	132593	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-01	HIGH	X260 Sportbrake五门旅行车。	READY
132594	132594	Sedan	Astra H	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH	L69四门轿车外廓。	READY
132595	132595	Sedan	Astra H	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH	L69四门轿车外廓。	READY
132596	132596	SUV	E-PACE I	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH	X540标准SUV外廓。	READY
132617	132617	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132622	132622	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132624	132624	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132630_prefl	132630	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	Ktype生产区间跨改款，改款前柴油分支。	READY
132630_facelift	132630	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后柴油分支。	READY
132632_prefl	132632	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	Ktype生产区间跨改款，改款前AWD柴油分支。	READY
132632_facelift	132632	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后AWD柴油分支。	READY
132633	132633	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	生产结束时间位于改款前阶段。	READY
132662	132662	SUV	GL-Class II	X166	5	EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	HIGH		READY
132684	132684	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	商用衍生版保持Phase II五门车身外廓。	READY
132701_phase_i	132701	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	Ktype生产区间跨阶段，Phase I商用分支。	READY
132701_phase_ii	132701	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	Ktype生产区间跨阶段，Phase II商用分支。	READY
132710	132710	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-IMPREZA-II-GD-PRODRIVE-SEDAN-01	4405	1730	1435	Subaru official WEB catalog - Impreza WRX STI Prodrive Style	https://ucar.subaru.jp/php/catalog/grade.php?baitai=iphone&cat_id=4502540
EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	5341	2164	1835	Rolls-Royce Motor Cars press information - Effortless Everywhere: The Rolls-Royce Cullinan	https://www.press.rolls-roycemotorcars.com/united-kingdom/article/detail/T0280959EN/effortless-everywhere%3A-the-rolls-royce-cullinan?language=en_GB
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Mercedes-Benz The A-Class Saloon V177 brochure	https://www.mercedes-benzcaribbean.com/assets/brochures/A_Klasse_V177_ePaper_1219_02_ENG.pdf
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607	Fiat 500X December 2018 official technical specification	https://www.media.stellantis.com/uploads/fr/FR/2019/FIAT/INFORMATIONS_TECHNIQUES/Fiche_technique_gamme_tarifs_500X_d_c_2018.pdf
EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	4466	1840	1482	Vauxhall Astra GTC official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/cars/gtc/GTC_Spec_PG_2_October_2012.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed Sportswagon Geneva 2018 official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/Motorshows/Geneva-2018/10%20-%20Kia%20Ceed%20SW%20Geneva%20reveal%20-%20Final%20-%206%20Mar%202018.doc
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464	Citroën C6 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2024/06/Citroen-C6-2011-UK.pdf
EU-PEUGEOT-207-SW-WAGON-FACELIFT-01	4164	1748	1527	Auto-Data Peugeot 207 SW facelift 2009	https://www.auto-data.net/en/peugeot-207-sw-facelift-2009-generation-3902
EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-01	4955	1880	1496	Jaguar XF Sportbrake 2019 model year official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XF-SB_19MY_MB-GE_V10d_DX.pdf
EU-JAGUAR-E-PACE-X540-SUV-01	4395	1900	1649	Jaguar E-PACE official specifications; Car and Driver 2018 Jaguar E-PACE specifications	https://www.jaguar.com/en-xi/jdx/jaguar-range/e-pace/specifications/index.html;https://www.caranddriver.com/jaguar/e-pace/specs/2018/jaguar_e-pace_jaguar-e-pace_2018
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Kia Stonic 2018 official brochure	https://www.kia.com/content/dam/kwcms/kme/mt/mt/assets/contents/utility/brochures/StonicBrochure_210X210_AV_Jan-Feb2018.pdf
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550	Hyundai KONA 2018 official brochure	https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/brochure/model/os/kona-ebrochure-2018.pdf
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550	Hyundai KONA facelift official catalog	https://www.hyundai.com/contents/repn-car/catalog_en/kona-catalog.pdf
```

下一步优先处理

1. 集中闭合 PSA 旧款商用衍生车：Bipper、Megane II van、Peugeot 206/307 van、Citroën C2/C4/C5 van。
2. 解决明确跨改款或多外廓的 Ktype：Focus IV hatch、Audi Q7 4M、Fiat 500X FWD、Peugeot 301、Jaguar F-PACE SVR。
3. 按车身聚类处理 Opel 旧平台：Zafira A/B、Vectra B 三种车身、Astra G 三门/五门/旅行版。
4. 补齐 Land Cruiser Van、Fabia Praktik、Aixam 500 Cabriolet、Citroën XM 和 Maserati Biturbo Spyder 等低复用车型。

推进信号：CONTINUE

[1]: https://www.press.rolls-roycemotorcars.com/united-kingdom/article/detail/T0280959EN/effortless-everywhere%3A-the-rolls-royce-cullinan?language=en_GB&utm_source=chatgpt.com "EFFORTLESS EVERYWHERE: THE ROLLS-ROYCE CULLINAN"
[2]: https://ucar.subaru.jp/php/catalog/grade.php?baitai=iphone&cat_id=4502540&utm_source=chatgpt.com "インプレッサＷＲＸＳＴｉプロドライブスタイル（2001年10月）カタログ・スペック情報 | インプレッサＷＲＸ 2000年8月 (平成12年8月) 〜2002年11月 (平成14年11月) 発売モデル | インプレッサＷＲＸのモデル一覧 | WEBカタログ車種一覧 | 中古車ならスグダス | SUBARU （公式）"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 18 个 Ktype，共新增 22 条 READY 映射；Focus IV Hatchback 因生产期跨改款拆分为改款前、改款后分支，改款前直接复用已有尺寸组。
* 完成 Fiat 500X Urban/Cross、Opel Vectra B 三种车身和 Zafira A 改款版尺寸组。([汽车数据网][1])
* 完成 Peugeot 406 Phase II 轿车/旅行车及 Citroën C5 I Break 改款前后尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：58
* READY 映射行：68
* PENDING Ktype：42
* 当前引用尺寸组：39
* 本轮首次创建尺寸组：11
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132501_urban	132501	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	2018款Urban Look物理外廓。	READY
132501_cross	132501	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	2018款Cross Look物理外廓。	READY
132508_urban	132508	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	2018款Urban Look物理外廓。	READY
132508_cross	132508	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	2018款Cross Look物理外廓。	READY
132517_prefl	132517	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132517_facelift	132517	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132518_prefl	132518	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132518_facelift	132518	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132615	132615	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	HIGH	T98改款后五门MPV外廓。	READY
132626	132626	Sedan	Vectra B		4	EU-OPEL-VECTRA-B-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
132627	132627	Hatchback	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	HIGH	改款后五门掀背外廓。	READY
132628	132628	Hatchback	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	HIGH	改款后五门掀背外廓。	READY
132635	132635	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	HIGH	改款后五门旅行车外廓。	READY
132637	132637	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	HIGH	改款后五门旅行车外廓。	READY
132640	132640	Sedan	406 I Phase II		4	EU-PEUGEOT-406-I-PHASE-II-SEDAN-01	HIGH	Phase II四门轿车外廓。	READY
132645	132645	Wagon	406 I Phase II		5	EU-PEUGEOT-406-I-PHASE-II-WAGON-01	HIGH	Phase II五门旅行车外廓。	READY
132705	132705	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	商用衍生版保留Break改款前外廓。	READY
132713	132713	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	商用衍生版保留Break改款前外廓。	READY
132716	132716	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132719	132719	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132721	132721	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132724	132724	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595	Fiat New 500X 2018 official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT/Schede-Tecniche/180903_Fiat_New_500X_Technical-Sheet.pdf
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603	Fiat New 500X 2018 official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT/Schede-Tecniche/180903_Fiat_New_500X_Technical-Sheet.pdf
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471	Ford Focus official feature and technical specification	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684	Automobile-Catalog 2004 Opel Zafira 1.6 16V	https://www.automobile-catalog.com/car/2004/2521790/opel_zafira_1_6_16v.html
EU-OPEL-VECTRA-B-FACELIFT-SEDAN-01	4495	1707	1425	Auto-Data Opel Vectra B facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-facelift-1999-2.2-16-v-147hp-automatic-26138
EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	4495	1707	1425	Auto-Data Opel Vectra B CC facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-cc-facelift-1999-2.2-16v-147hp-2293
EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	4490	1710	1490	Auto-Data Opel Vectra B Caravan facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-caravan-facelift-1999-2.2-16v-147hp-2281
EU-PEUGEOT-406-I-PHASE-II-SEDAN-01	4598	1765	1412	Automobile-Catalog 2001 Peugeot 406 1.8i 16V	https://www.automobile-catalog.com/car/2001/2614625/peugeot_406_1_8i_16v.html
EU-PEUGEOT-406-I-PHASE-II-WAGON-01	4736	1760	1460	Automobile-Catalog 2001 Peugeot 406 Break 1.8i 16V	https://www.automobile-catalog.com/car/2001/2614640/peugeot_406_break_1_8i_16v.html
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516	Automobile-Catalog 2003 Citroën C5 Break 2.0 HDi 110 SX	https://www.automobile-catalog.com/car/2003/549365/citroen_c5_break_2_0_hdi_110_sx.html
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555	Automobile-Catalog 2005 Citroën C5 Break 2.0 HDi 135 FAP Tendance	https://www.automobile-catalog.com/car/2005/549935/citroen_c5_break_2_0_hdi_135_fap_tendance.html
```

## 下一步优先处理

1. 集中处理 Renault Megane II、Peugeot 206/307、Citroën C2/C4 的厢式商用衍生车。
2. 解决 Peugeot 301、Audi Q7、Jaguar F-PACE 等跨改款或特殊外部套件边界。
3. 处理 Astra G、Zafira B、Frontera 等剩余 Opel 旧平台车型。
4. 补齐 Land Cruiser Van、Fabia Praktik、Aixam 500、Citroën XM 和 Maserati Biturbo 等低复用车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-vectra-b-facelift-1999-2.2-16-v-147hp-automatic-26138?utm_source=chatgpt.com "Opel Vectra B (facelift 1999) 2.2 16 V (147 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2003/549365/citroen_c5_break_2_0_hdi_110_sx.html?utm_source=chatgpt.com "2003 Citroen C5 Break 2.0 HDi 110 SX (man. 5)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 Volvo 760、Peugeot 301/508 SW、Citroën XM、Xsara Picasso、C5 II、C4 II、C2，以及 Opel Zafira/Astra 相关映射。
* Peugeot 301 与 Zafira A 的 Ktype 跨越改款边界，已分别拆为 `prefl`、`facelift` 派生行。
* C4 II、C2、508 SW 的商用衍生版本沿用对应乘用车物理外廓，但映射层 `NormalizedBodyStyle` 保持为 `Van`。([德国汽车俱乐部][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射行：85
* PENDING Ktype：27
* 当前引用尺寸组：52
* 本轮首次创建尺寸组：11
* 本轮复用既有尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132454	132454	Sedan	760 Facelift	764	4	EU-VOLVO-760-764-SEDAN-FACELIFT-01	HIGH	764四门改款轿车外廓。	READY
132516_prefl	132516	Sedan	301 I		4	EU-PEUGEOT-301-I-SEDAN-PREFL-01	HIGH	Ktype生产区间覆盖改款前分支。	READY
132516_facelift	132516	Sedan	301 I		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH	Ktype生产区间覆盖改款后分支。	READY
132533	132533	Van	508 I		5	EU-PEUGEOT-508-I-SW-WAGON-PREFL-01	HIGH	商用衍生版保留第一代508 SW改款前外廓。	READY
132542	132542	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	Phase I五门掀背外廓。	READY
132553	132553	Wagon	XM II	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4五门旅行车外廓。	READY
132557	132557	Hatchback	XM II	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-5D-01	HIGH	Y4五门掀背外廓。	READY
132575	132575	MPV	Xsara Picasso I Phase II	N68	5	EU-CITROEN-XSARA-PICASSO-N68-PHASE-II-MPV-01	HIGH	N68改款五门MPV外廓。	READY
132580	132580	Sedan	C5 II	RD	4	EU-CITROEN-C5-II-RD-SEDAN-01	HIGH	RD四门轿车外廓。	READY
132592	132592	MPV	Zafira B Facelift	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	A05改款五门MPV外廓。	READY
132638_prefl	132638	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	HIGH	Ktype生产区间覆盖改款前分支。	READY
132638_facelift	132638	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后分支。	READY
132644	132644	Sedan	Astra G		4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH	Astra G四门轿车外廓。	READY
132690	132690	Van	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	商用衍生版保留Phase I五门掀背外廓。	READY
132693	132693	Van	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	商用衍生版保留Phase I五门掀背外廓。	READY
132714	132714	Van	C2 I	JM	3	EU-CITROEN-C2-I-JM-VAN-3D-01	HIGH	商用衍生版保留C2三门外廓。	READY
132715	132715	Van	C2 I	JM	3	EU-CITROEN-C2-I-JM-VAN-3D-01	HIGH	商用衍生版保留C2三门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-760-764-SEDAN-FACELIFT-01	4785	1750	1410	ADAC Volvo 740/760 2.4 TD GLE technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/volvo/740-760/1generation/261098/
EU-PEUGEOT-301-I-SEDAN-PREFL-01	4442	1748	1466	Automobile-Catalog 2014 Peugeot 301 1.6 VTi	https://www.automobile-catalog.com/car/2014/2624060/peugeot_301_1_6_vti.html
EU-PEUGEOT-508-I-SW-WAGON-PREFL-01	4813	1853	1476	Automobile-Catalog 2011 Peugeot 508 SW 2.2 HDi FAP 204	https://www.automobile-catalog.com/car/2011/2625365/peugeot_508_sw_2_2_hdi_fap_204_200.html
EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	4329	1789	1489	Auto-Data Citroën C4 II Hatchback Phase I; Auto-Data Citroën C4 model dimensions	https://www.auto-data.net/en/citroen-c4-ii-hatchback-phase-i-2010-generation-4005;https://www.auto-data.net/en/citroen-c4-model-1695
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1456	Automobile-Catalog 1995 Citroën XM Break 2.0 16V	https://www.automobile-catalog.com/car/1995/544925/citroen_xm_break_2_0_16v_automatic.html
EU-CITROEN-XM-Y4-HATCHBACK-5D-01	4708	1794	1389	Automobile-Catalog 1995 Citroën XM 2.0 16V SX	https://www.automobile-catalog.com/car/1995/544775/citroen_xm_2_0_16v_sx.html
EU-CITROEN-XSARA-PICASSO-N68-PHASE-II-MPV-01	4276	1751	1637	Auto-Data Citroën Xsara Picasso N68 Phase II 1.6 16V	https://www.auto-data.net/en/citroen-xsara-picasso-n68-phase-ii-1.6-16v-109hp-15111
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451	CarsGuide Citroën C5 2009 dimensions	https://www.carsguide.com.au/citroen/c5/car-dimensions/2009
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635	Auto-Data Vauxhall Zafira B Facelift 1.6 XER	https://www.auto-data.net/en/vauxhall-zafira-b-facelift-2008-1.6-xer-115hp-25711
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684	Auto-Data Opel Zafira A generation	https://www.auto-data.net/en/opel-zafira-a-t3000-generation-574
EU-CITROEN-C2-I-JM-VAN-3D-01	3666	1659	1461	Auto-Data Citroën C2 I Phase I 1.1i	https://www.auto-data.net/en/citroen-c2-i-phase-i-2003-1.1i-60hp-14984
```

## 下一步优先处理

1. 处理 Land Cruiser Van、Fabia Praktik、Megane II Van、Bipper 和 Peugeot 206/307 商用衍生车。
2. 核对 Audi Q7、Jaguar F-PACE SVR、Audi A7、Ford Mondeo V 的改款或特殊外部套件边界。
3. 闭合 Aixam 500 Cabriolet、Maserati Biturbo Spyder、Opel Frontera 等低复用车型。
4. 处理剩余 Astra G、Peugeot 206/207、Citroën C5/C4 I 等车身簇。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/volvo/740-760/1generation/261098/?utm_source=chatgpt.com "Volvo 740 2.4 TD GLE (10/86 - 12/89): Technische Daten, Bilder, Preise | ADAC"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Škoda Fabia I Praktik；其 Ktype 覆盖 2004 年外廓调整，按改款前后拆分为两个尺寸分支。资料明确 Praktik 基于 Fabia Combi，五门车身，长度由 4222 mm 调整为 4232 mm。([allcarcentral.com][1])
* 闭合 Peugeot Bipper 厢式车；Peugeot 资料确认长度和高度，同平台 Fiat Fiorino 官方资料补充不含后视镜车身宽度 1716 mm。([autosynergy.co.uk][2])
* 闭合 Ford Mondeo V 五门掀背和旅行车，官方技术规格同时给出了不含后视镜宽度。([Ford From the Road][3])
* 闭合 Audi A7 Sportback C8，并将两个 Astra G Caravan Ktype 直接关联既有旅行车尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：80
* READY 映射行：93
* PENDING Ktype：20
* 当前引用尺寸组：58
* 本轮新增尺寸组：6
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132416_prefl	132416	Van	Fabia I Praktik	6Y5	5	EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-PREFL-01	HIGH	Ktype覆盖2004年外廓调整，改款前分支。	READY
132416_facelift	132416	Van	Fabia I Praktik	6Y5	5	EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-FACELIFT-01	HIGH	Ktype覆盖2004年外廓调整，改款后分支。	READY
132515	132515	Van	Bipper I			EU-PEUGEOT-BIPPER-I-VAN-01	HIGH	标准轴距厢式车外廓。	READY
132620	132620	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH	F35五门旅行车外廓。	READY
132643	132643	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH	CD391五门掀背外廓。	READY
132646	132646	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH	CD391五门旅行车外廓。	READY
132649	132649	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH	F35五门旅行车外廓。	READY
132656	132656	Hatchback	A7 II	4K8	5	EU-AUDI-A7-II-4K8-SPORTBACK-01	HIGH	4K8五门Sportback标准外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-PREFL-01	4222	1646	1452	Škoda Auto historical Fabia Praktik data sheet	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-FACELIFT-01	4232	1646	1452	Škoda Auto historical Fabia Praktik data sheet	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-PEUGEOT-BIPPER-I-VAN-01	3864	1716	1721	Peugeot Bipper official brochure;Stellantis Fiat Professional Fiorino official press pack	https://www.autosynergy.co.uk/assets/brochures/peugeot-bipper.pdf;https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482	Ford Mondeo official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501	Ford Mondeo official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-AUDI-A7-II-4K8-SPORTBACK-01	4969	1908	1422	Audi MediaCenter new A7 Sportback official press information	https://www.audi-mediacenter.com/en/the-new-audi-a7-sportback-progressive-in-design-and-technology-9831/download
```

## 下一步优先处理

1. 闭合 Peugeot 206、207 和 307 的乘用及厢式衍生车，优先确认三门、五门和改款边界。
2. 处理 Audi Q7、Jaguar F-PACE SVR 和 Jeep Renegade 的跨改款或特殊保险杠外廓。
3. 处理 Land Cruiser Van、Megane II Van、Opel Frontera 和 Citroën C4 I Van。
4. 最后处理 Aixam 500、Maserati Biturbo Cabriolet 和 Peugeot 106 II 等低复用车型。

推进信号：CONTINUE

[1]: https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf "(Microsoft Word - \212koda Fabia Praktik 2002-2006.doc)"
[2]: https://www.autosynergy.co.uk/assets/brochures/peugeot-bipper.pdf "Bipper Van May 2015"
[3]: https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf "Mondeo Technical Specifications - PDF"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 Peugeot 207/207+、206、307 和 106 II 车身簇；门数或改款造成外廓边界差异的 Ktype 已拆分，商用衍生版直接关联对应乘用车外廓组。([汽车目录][1])
* Audi Q7 45/50 TDI 均覆盖 4M 改款前后尺寸，统一拆为 `prefl` 和 `facelift` 两套尺寸组。([德国汽车俱乐部][2])
* Jaguar F-PACE SVR 已按改款前后专属保险杠外廓拆分；两阶段均使用不含后视镜宽度 1936 mm。([CarExpert NZ][3])
* 完成 Maserati Biturbo Spyder、Jeep Renegade 95 PS 和 Opel Frontera A Sport。Renegade 95 PS 本轮仅落入已确认的改款前外廓，未把未知结束日期解释为持续至改款后。([斯泰兰蒂斯媒体][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：123
* PENDING Ktype：5
* 当前引用尺寸组：78
* 本轮首次创建尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132551_3dr_prefl	132551	Hatchback	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	HIGH	三门改款前物理外廓。	READY
132551_3dr_facelift	132551	Hatchback	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后物理外廓。	READY
132551_5dr_prefl	132551	Hatchback	207 I		5	EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	HIGH	五门改款前物理外廓。	READY
132551_5dr_facelift	132551	Hatchback	207 I		5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后物理外廓。	READY
132559	132559	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	双门Spyder外廓。	READY
132560	132560	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	双门Spyder外廓。	READY
132589	132589	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	HIGH	95 PS前驱改款前外廓。	READY
132598_prefl	132598	SUV	F-PACE I	X761	5	EU-JAGUAR-F-PACE-X761-SVR-SUV-PREFL-01	HIGH	SVR改款前专属外廓。	READY
132598_facelift	132598	SUV	F-PACE I	X761	5	EU-JAGUAR-F-PACE-X761-SVR-SUV-FACELIFT-01	HIGH	SVR改款后专属外廓。	READY
132600_prefl	132600	Van	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门商用衍生版改款前外廓。	READY
132600_facelift	132600	Van	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门商用衍生版改款后外廓。	READY
132607_prefl	132607	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-PREFL-01	HIGH	旅行车商用衍生版改款前外廓。	READY
132607_facelift	132607	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132608_prefl	132608	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-PREFL-01	HIGH	旅行车商用衍生版改款前外廓。	READY
132608_facelift	132608	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132616	132616	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132641_prefl	132641	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前外廓。	READY
132641_facelift	132641	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款后外廓。	READY
132642_prefl	132642	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前外廓。	READY
132642_facelift	132642	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款后外廓。	READY
132647_3dr_prefl	132647	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理外廓。	READY
132647_3dr_facelift	132647	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后物理外廓。	READY
132647_5dr_prefl	132647	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理外廓。	READY
132647_5dr_facelift	132647	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后物理外廓。	READY
132657_prefl	132657	SUV	Frontera A		3	EU-OPEL-FRONTERA-A-SPORT-HARDTOP-PREFL-01	HIGH	三门Sport硬顶改款前外廓。	READY
132657_facelift	132657	SUV	Frontera A		3	EU-OPEL-FRONTERA-A-SPORT-HARDTOP-FACELIFT-01	HIGH	三门Sport硬顶改款后外廓。	READY
132659_prefl	132659	Van	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门商用衍生版改款前外廓。	READY
132659_facelift	132659	Van	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门商用衍生版改款后外廓。	READY
132677_3dr	132677	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
132677_5dr	132677	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1748	1472	Automobile-Catalog 2007 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472	Automobile-Catalog 2009 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2009/2621015/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	4030	1748	1472	Automobile-Catalog 2007 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472	Automobile-Catalog 2009 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2009/2621015/peugeot_207_1_4_vti_95.html
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog Maserati Biturbo Spyder range	https://www.automobile-catalog.com/make/maserati/biturbo/biturbo_spyder/1987.html
EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	4236	1805	1667	CarExpert 2016 Jeep Renegade Longitude dimensions	https://www.carexpert.com.au/jeep/renegade/2016/longitude/exterior-and-dimensions
EU-JAGUAR-F-PACE-X761-SVR-SUV-PREFL-01	4737	1936	1670	CarExpert 2021 Jaguar F-PACE SVR exterior dimensions	https://www.carexpert.co.nz/jaguar/f-pace/2021/svr/exterior-and-dimensions
EU-JAGUAR-F-PACE-X761-SVR-SUV-FACELIFT-01	4762	1936	1670	Jaguar F-PACE SVR 21MY official technical data;Automobile-Catalog 2021 Jaguar F-PACE SVR	https://jlrnewsroom.media/wp-content/uploads/2020/12/Jaguar-F-PACE-SVR-21MY_Tech-Data_021220.pdf;https://www.automobile-catalog.com/car/2021/3045830/jaguar_f-pace_svr.html
EU-PEUGEOT-307-I-WAGON-PREFL-01	4419	1757	1544	Automobile-Catalog 2003 Peugeot 307 Break 2.0 HDi 90	https://www.automobile-catalog.com/car/2003/2617400/peugeot_307_break_estate_2_0_hdi_90.html
EU-PEUGEOT-307-I-WAGON-FACELIFT-01	4428	1762	1560	Auto-Data Peugeot 307 Station Wagon facelift 1.6 HDi 90	https://www.auto-data.net/en/peugeot-307-station-wagon-facelift-2005-1.6-hdi-90hp-5281
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741	ADAC Audi Q7 45 TDI 08/18-06/19;ADAC Audi Q7 50 TDI 08/18-06/19	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292871/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292872/
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741	Audi Q7 45/50 TDI official technical data	https://www.audi.ee/dam/nemo/ee/Mudelikataloogid/tehniline_info/Tehniline%20info%20Q7%20quattro_1.pdf
EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	3835	1652	1426	Automobile-Catalog 2000 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2000/2615555/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	3822	1652	1425	Automobile-Catalog 2004 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2004/2615960/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-5D-PREFL-01	3835	1652	1426	Automobile-Catalog 2000 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2000/2615555/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-5D-FACELIFT-01	3822	1652	1425	Automobile-Catalog 2004 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2004/2615960/peugeot_206_1_6_16v_110.html
EU-OPEL-FRONTERA-A-SPORT-HARDTOP-PREFL-01	4207	1780	1698	Automobile-Catalog 1993 Opel Frontera Sport 2.0i	https://www.automobile-catalog.com/car/1993/2493395/opel_frontera_sport_2_0i.html
EU-OPEL-FRONTERA-A-SPORT-HARDTOP-FACELIFT-01	4192	1780	1721	Automobile-Catalog 1996 Opel Frontera Sport 2.0i	https://www.automobile-catalog.com/car/1996/2493680/opel_frontera_sport_2_0i.html
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.1i	https://www.auto-data.net/en/peugeot-106-ii-1-1.1-i-60hp-5405
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.1i	https://www.auto-data.net/en/peugeot-106-ii-1-1.1-i-60hp-5405
```

## 下一步优先处理

1. Toyota Land Cruiser Van：确认 Ktype 是否同时覆盖三门/五门及 2013 年改款边界。
2. Renault Megane II Hatchback Van：确认三门商用版与五门商用版覆盖关系。
3. Aixam 500 Cabriolet：闭合老款微型车三维和明确的不含镜宽度。
4. Opel Astra G CC：确认该 Ktype 的三门/五门边界并关联既有五门组或新建三门组。
5. Citroën C4 I Van：确认商用衍生版基于 Coupe 三门还是 Hatchback 五门。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html "https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html"
[2]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292871/ "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292871/"
[3]: https://www.carexpert.co.nz/jaguar/f-pace/2021/svr/exterior-and-dimensions "https://www.carexpert.co.nz/jaguar/f-pace/2021/svr/exterior-and-dimensions"
[4]: https://www.media.stellantis.com/de-de/jeep/press/jeep-renegade-fur-das-modelljahr-2018-mehr-konnektivitat-funktionalitat-und-noch-attraktivere-preisvorteile-fur-kunden "https://www.media.stellantis.com/de-de/jeep/press/jeep-renegade-fur-das-modelljahr-2018-mehr-konnektivitat-funktionalitat-und-noch-attraktivere-preisvorteile-fur-kunden"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Toyota Land Cruiser Van Ktype 已按三门/五门及 2013 年改款前后拆为四个物理分支；四套规格均明确区分车身宽度与含后视镜宽度。([汽车数据网][1])
* Renault Megane II Hatchback Van 已闭合为 KM0/2 五门厢式衍生外廓。([汽车数据网][2])
* Opel Astra G CC Ktype 覆盖 F08 三门和 F48 五门；五门复用既有尺寸组，三门首次单独建组。该代三门和五门具有相同三维，但物理车门结构不同。([汽车目录][3])
* Citroën C4 I Van 已确认基于三门 C4 Coupé Enterprise 外廓。([网车秀][4])
* Aixam 500 Cabriolet 仍为唯一 PENDING：现有资料分别给出 `2885×1450×1380` 和 `2885×1440×1365`，且均未充分证明为 Cabriolet 专属、不含后视镜口径，暂不强行建组。([VehicleScore][5])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* READY 映射行：131
* PENDING Ktype：1
* PENDING 映射行：1
* 已确认并被引用尺寸组：85
* 本轮首次创建尺寸组：7
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132409_3dr_prefl	132409	Van	Land Cruiser Prado J150	KDJ155	3	EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-PREFL-01	HIGH	KDJ155三门短轴商用外廓，改款前分支。	READY
132409_3dr_facelift	132409	Van	Land Cruiser Prado J150	KDJ155	3	EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-FACELIFT-01	HIGH	KDJ155三门短轴商用外廓，2013改款分支。	READY
132409_5dr_prefl	132409	Van	Land Cruiser Prado J150	KDJ150	5	EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-PREFL-01	HIGH	KDJ150五门长轴商用外廓，改款前分支。	READY
132409_5dr_facelift	132409	Van	Land Cruiser Prado J150	KDJ150	5	EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-FACELIFT-01	HIGH	KDJ150五门长轴商用外廓，2013改款分支。	READY
132419	132419	Van	Megane II	KM0/2	5	EU-RENAULT-MEGANE-II-KM0-2-VAN-5D-01	HIGH	KM0/2五门厢式衍生外廓。	READY
132441	132441	Convertible	500 Cabriolet		2		LOW	Cabriolet专属三维及不含后视镜宽度尚未闭合。	PENDING: Cabriolet专属尺寸来源存在宽度和高度冲突
132619_3dr	132619	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-FACELIFT-01	HIGH	F08三门掀背物理外廓。	READY
132619_5dr	132619	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH	F48五门掀背物理外廓。	READY
132706	132706	Van	C4 I	LR	3	EU-CITROEN-C4-I-LR-VAN-3D-01	MEDIUM	LR三门C4 Coupé商用衍生外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-PREFL-01	4485	1885	1875	Auto-Data Toyota Land Cruiser Prado J150 3-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-3-door-3.0-d-4d-190hp-4wd-43380
EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-FACELIFT-01	4505	1885	1830	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 3-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-3-door-3.0-d-4d-190hp-4wd-22000
EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-PREFL-01	4760	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 5-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-5-door-3.0-d-4d-190hp-4wd-46917
EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-FACELIFT-01	4780	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 5-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-3.0-d-4d-190hp-4wd-21998
EU-RENAULT-MEGANE-II-KM0-2-VAN-5D-01	4209	1777	1458	Auto-Data Renault Megane II 1.5 dCi 82;Automobile-Catalog Renault Megane 1.5 dCi 80	https://www.auto-data.net/en/renault-megane-ii-1.5-dci-82hp-10531;https://www.automobile-catalog.com/car/2004/2953670/renault_megane_1_5_dci_80.html
EU-OPEL-ASTRA-G-HATCHBACK-3D-FACELIFT-01	4110	1709	1425	Auto-Data Opel Astra G;Automobile-Catalog 2003 Opel Astra G 3/5-door Hatchback	https://www.auto-data.net/en/opel-astra-model-252;https://www.automobile-catalog.com/car/2003/2518505/opel_astra_1_6.html
EU-CITROEN-C4-I-LR-VAN-3D-01	4273	1769	1456	Auto-Data Citroën C4 I Coupé 2.0 HDi 136;Citroën C4 Coupé Enterprise	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-i-2004-2.0-hdi-16v-136hp-15170;https://www.netcarshow.com/citroen/2005-c4_coupe_enterprise/
```

## 下一步优先处理

1. 仅处理 `132441` Aixam 500 Cabriolet：寻找 Cabriolet 专属技术资料，并确认宽度明确不含外后视镜。
2. 尺寸闭合后立即执行一次机械收尾，汇总两张完整 TSV 并生成指定下载文件。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-3-door-3.0-d-4d-190hp-4wd-43380 "Toyota Land Cruiser Prado (J150) 3-door 3.0 D-4D (190 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-megane-ii-1.5-dci-82hp-10531 "Renault Megane II 1.5 dCi (82 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/make/opel/astra_g/astra_g_hatch/2003.html?utm_source=chatgpt.com "2003 Opel Astra G 3/5-Door Hatchback full range specs"
[4]: https://www.netcarshow.com/citroen/2005-c4_coupe_enterprise/?utm_source=chatgpt.com "Citroen C4 Coupe Enterprise (2005)"
[5]: https://vehiclescore.co.uk/car-dimensions-check/aixam/500?utm_source=chatgpt.com "AIXAM 500 Dimensions - Length, Width, Height"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2601-2700_ktype_dimension_mapping_final.tsv
- all_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* `132441` 已闭合。瑞士车型认证 `6AA706` 将左右后视镜单独列项，并记录整车尺寸为 `2600 × 1385 × 1330 mm`；据此采用 `1385 mm` 作为不含后视镜车身宽度。([typenscheine.ch][1])
* 已完成最终机械检查：固定表头正确、`id` 和 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源字段完整。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：132
* PENDING 映射：0
* DIMENSION_GROUP：88
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132378	132378	Convertible	E-Class W213	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	A238双门标准车身敞篷版。	READY
132406	132406	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-PRODRIVE-SEDAN-01	HIGH	GD四门Prodrive Performance Package外廓。	READY
132409_3dr_prefl	132409	Van	Land Cruiser Prado J150	KDJ155	3	EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-PREFL-01	HIGH	KDJ155三门短轴商用外廓，改款前分支。	READY
132409_3dr_facelift	132409	Van	Land Cruiser Prado J150	KDJ155	3	EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-FACELIFT-01	HIGH	KDJ155三门短轴商用外廓，2013改款分支。	READY
132409_5dr_prefl	132409	Van	Land Cruiser Prado J150	KDJ150	5	EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-PREFL-01	HIGH	KDJ150五门长轴商用外廓，改款前分支。	READY
132409_5dr_facelift	132409	Van	Land Cruiser Prado J150	KDJ150	5	EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-FACELIFT-01	HIGH	KDJ150五门长轴商用外廓，2013改款分支。	READY
132411	132411	SUV	Cullinan I		5	EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	HIGH	第一代Cullinan标准车身。	READY
132416_prefl	132416	Van	Fabia I Praktik	6Y5	5	EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-PREFL-01	HIGH	Ktype覆盖2004年外廓调整，改款前分支。	READY
132416_facelift	132416	Van	Fabia I Praktik	6Y5	5	EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-FACELIFT-01	HIGH	Ktype覆盖2004年外廓调整，改款后分支。	READY
132419	132419	Van	Megane II	KM0/2	5	EU-RENAULT-MEGANE-II-KM0-2-VAN-5D-01	HIGH	KM0/2五门厢式衍生外廓。	READY
132439	132439	SUV	Captur I	J87	5	EU-RENAULT-CAPTUR-I-SUV-01	HIGH		READY
132441	132441	Convertible	MAC 500		2	EU-AIXAM-MAC-500-CABRIOLET-01	HIGH	MAC 500双座敞篷车外廓。	READY
132444	132444	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132445	132445	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132446	132446	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132447	132447	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132448	132448	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177改款前轿车外廓。	READY
132454	132454	Sedan	760 Facelift	764	4	EU-VOLVO-760-764-SEDAN-FACELIFT-01	HIGH	764四门改款轿车外廓。	READY
132464	132464	Sedan	Polo V	602	4	EU-VW-POLO-V-602-SEDAN-FACELIFT-01	HIGH	602四门改款轿车。	READY
132498	132498	SUV	X3 III	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01标准车身，M40i动力不改变外廓。	READY
132500	132500	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	HIGH	改款后4x4 Cross外廓。	READY
132501_urban	132501	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	2018款Urban Look物理外廓。	READY
132501_cross	132501	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	2018款Cross Look物理外廓。	READY
132508_urban	132508	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	2018款Urban Look物理外廓。	READY
132508_cross	132508	SUV	500X I	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	2018款Cross Look物理外廓。	READY
132515	132515	Van	Bipper I			EU-PEUGEOT-BIPPER-I-VAN-01	HIGH	标准轴距厢式车外廓。	READY
132516_prefl	132516	Sedan	301 I		4	EU-PEUGEOT-301-I-SEDAN-PREFL-01	HIGH	Ktype生产区间覆盖改款前分支。	READY
132516_facelift	132516	Sedan	301 I		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH	Ktype生产区间覆盖改款后分支。	READY
132517_prefl	132517	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132517_facelift	132517	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132518_prefl	132518	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132518_facelift	132518	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132520_prefl	132520	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132520_facelift	132520	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132521_prefl	132521	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	Ktype生产区间跨改款，改款前分支。	READY
132521_facelift	132521	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后分支。	READY
132529	132529	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
132533	132533	Van	508 I		5	EU-PEUGEOT-508-I-SW-WAGON-PREFL-01	HIGH	商用衍生版保留第一代508 SW改款前外廓。	READY
132534	132534	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
132537	132537	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	AWD不改变该外廓尺寸。	READY
132538	132538	Hatchback	Astra J		3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	HIGH	GTC三门独立宽体外廓。	READY
132542	132542	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	Phase I五门掀背外廓。	READY
132551_3dr_prefl	132551	Hatchback	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	HIGH	三门改款前物理外廓。	READY
132551_3dr_facelift	132551	Hatchback	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后物理外廓。	READY
132551_5dr_prefl	132551	Hatchback	207 I		5	EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	HIGH	五门改款前物理外廓。	READY
132551_5dr_facelift	132551	Hatchback	207 I		5	EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后物理外廓。	READY
132553	132553	Wagon	XM II	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4五门旅行车外廓。	READY
132557	132557	Hatchback	XM II	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-5D-01	HIGH	Y4五门掀背外廓。	READY
132559	132559	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	双门Spyder外廓。	READY
132560	132560	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	HIGH	双门Spyder外廓。	READY
132563	132563	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132568	132568	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132569	132569	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132571	132571	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH	第一代C6四门轿车。	READY
132574	132574	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132575	132575	MPV	Xsara Picasso I Phase II	N68	5	EU-CITROEN-XSARA-PICASSO-N68-PHASE-II-MPV-01	HIGH	N68改款五门MPV外廓。	READY
132580	132580	Sedan	C5 II	RD	4	EU-CITROEN-C5-II-RD-SEDAN-01	HIGH	RD四门轿车外廓。	READY
132581	132581	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon外廓。	READY
132585	132585	Hatchback	C3 I		5	EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	HIGH	第一代C3改款五门外廓。	READY
132587_prefl	132587	Wagon	207 I		5	EU-PEUGEOT-207-SW-WAGON-PREFL-01	HIGH	Ktype生产区间跨2009改款，改款前分支。	READY
132587_facelift	132587	Wagon	207 I		5	EU-PEUGEOT-207-SW-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨2009改款，改款后分支。	READY
132589	132589	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	HIGH	95 PS前驱改款前外廓。	READY
132592	132592	MPV	Zafira B Facelift	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	A05改款五门MPV外廓。	READY
132593	132593	Wagon	XF II	X260	5	EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-01	HIGH	X260 Sportbrake五门旅行车。	READY
132594	132594	Sedan	Astra H	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH	L69四门轿车外廓。	READY
132595	132595	Sedan	Astra H	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH	L69四门轿车外廓。	READY
132596	132596	SUV	E-PACE I	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH	X540标准SUV外廓。	READY
132598_prefl	132598	SUV	F-PACE I	X761	5	EU-JAGUAR-F-PACE-X761-SVR-SUV-PREFL-01	HIGH	SVR改款前专属外廓。	READY
132598_facelift	132598	SUV	F-PACE I	X761	5	EU-JAGUAR-F-PACE-X761-SVR-SUV-FACELIFT-01	HIGH	SVR改款后专属外廓。	READY
132600_prefl	132600	Van	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门商用衍生版改款前外廓。	READY
132600_facelift	132600	Van	207 I		3	EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门商用衍生版改款后外廓。	READY
132607_prefl	132607	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-PREFL-01	HIGH	旅行车商用衍生版改款前外廓。	READY
132607_facelift	132607	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132608_prefl	132608	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-PREFL-01	HIGH	旅行车商用衍生版改款前外廓。	READY
132608_facelift	132608	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132615	132615	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	HIGH	T98改款后五门MPV外廓。	READY
132616	132616	Van	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-FACELIFT-01	HIGH	旅行车商用衍生版改款后外廓。	READY
132617	132617	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132619_3dr	132619	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-FACELIFT-01	HIGH	F08三门掀背物理外廓。	READY
132619_5dr	132619	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH	F48五门掀背物理外廓。	READY
132620	132620	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH	F35五门旅行车外廓。	READY
132622	132622	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132624	132624	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	YB五门跨界车标准外廓。	READY
132626	132626	Sedan	Vectra B		4	EU-OPEL-VECTRA-B-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
132627	132627	Hatchback	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	HIGH	改款后五门掀背外廓。	READY
132628	132628	Hatchback	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	HIGH	改款后五门掀背外廓。	READY
132630_prefl	132630	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	Ktype生产区间跨改款，改款前柴油分支。	READY
132630_facelift	132630	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后柴油分支。	READY
132632_prefl	132632	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	Ktype生产区间跨改款，改款前AWD柴油分支。	READY
132632_facelift	132632	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	HIGH	Ktype生产区间跨改款，改款后AWD柴油分支。	READY
132633	132633	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	HIGH	生产结束时间位于改款前阶段。	READY
132635	132635	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	HIGH	改款后五门旅行车外廓。	READY
132637	132637	Wagon	Vectra B		5	EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	HIGH	改款后五门旅行车外廓。	READY
132638_prefl	132638	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	HIGH	Ktype生产区间覆盖改款前分支。	READY
132638_facelift	132638	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后分支。	READY
132640	132640	Sedan	406 I Phase II		4	EU-PEUGEOT-406-I-PHASE-II-SEDAN-01	HIGH	Phase II四门轿车外廓。	READY
132641_prefl	132641	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前外廓。	READY
132641_facelift	132641	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款后外廓。	READY
132642_prefl	132642	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前外廓。	READY
132642_facelift	132642	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH	4M改款后外廓。	READY
132643	132643	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH	CD391五门掀背外廓。	READY
132644	132644	Sedan	Astra G		4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH	Astra G四门轿车外廓。	READY
132645	132645	Wagon	406 I Phase II		5	EU-PEUGEOT-406-I-PHASE-II-WAGON-01	HIGH	Phase II五门旅行车外廓。	READY
132646	132646	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH	CD391五门旅行车外廓。	READY
132647_3dr_prefl	132647	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理外廓。	READY
132647_3dr_facelift	132647	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后物理外廓。	READY
132647_5dr_prefl	132647	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理外廓。	READY
132647_5dr_facelift	132647	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后物理外廓。	READY
132649	132649	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH	F35五门旅行车外廓。	READY
132656	132656	Hatchback	A7 II	4K8	5	EU-AUDI-A7-II-4K8-SPORTBACK-01	HIGH	4K8五门Sportback标准外廓。	READY
132657_prefl	132657	SUV	Frontera A		3	EU-OPEL-FRONTERA-A-SPORT-HARDTOP-PREFL-01	HIGH	三门Sport硬顶改款前外廓。	READY
132657_facelift	132657	SUV	Frontera A		3	EU-OPEL-FRONTERA-A-SPORT-HARDTOP-FACELIFT-01	HIGH	三门Sport硬顶改款后外廓。	READY
132659_prefl	132659	Van	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	MEDIUM	三门商用衍生版改款前外廓。	READY
132659_facelift	132659	Van	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门商用衍生版改款后外廓。	READY
132662	132662	SUV	GL-Class II	X166	5	EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	HIGH		READY
132677_3dr	132677	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	MEDIUM	三门物理外廓。	READY
132677_5dr	132677	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	MEDIUM	五门物理外廓。	READY
132684	132684	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	商用衍生版保持Phase II五门车身外廓。	READY
132690	132690	Van	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	商用衍生版保留Phase I五门掀背外廓。	READY
132693	132693	Van	C4 II Phase I	B7	5	EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	HIGH	商用衍生版保留Phase I五门掀背外廓。	READY
132701_phase_i	132701	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	Ktype生产区间跨阶段，Phase I商用分支。	READY
132701_phase_ii	132701	Van	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	Ktype生产区间跨阶段，Phase II商用分支。	READY
132705	132705	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	商用衍生版保留Break改款前外廓。	READY
132706	132706	Van	C4 I	LR	3	EU-CITROEN-C4-I-LR-VAN-3D-01	MEDIUM	LR三门C4 Coupé商用衍生外廓。	READY
132710	132710	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
132713	132713	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	商用衍生版保留Break改款前外廓。	READY
132714	132714	Van	C2 I	JM	3	EU-CITROEN-C2-I-JM-VAN-3D-01	HIGH	商用衍生版保留C2三门外廓。	READY
132715	132715	Van	C2 I	JM	3	EU-CITROEN-C2-I-JM-VAN-3D-01	HIGH	商用衍生版保留C2三门外廓。	READY
132716	132716	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132719	132719	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132721	132721	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
132724	132724	Van	C5 I	DE	5	EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	HIGH	商用衍生版保留Break改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2601-2700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 300d	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300d-245hp-9g-tronic-33169
EU-SUBARU-IMPREZA-II-GD-PRODRIVE-SEDAN-01	4405	1730	1435	Subaru official WEB catalog - Impreza WRX STI Prodrive Style	https://ucar.subaru.jp/php/catalog/grade.php?baitai=iphone&cat_id=4502540
EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-PREFL-01	4485	1885	1875	Auto-Data Toyota Land Cruiser Prado J150 3-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-3-door-3.0-d-4d-190hp-4wd-43380
EU-TOYOTA-LAND-CRUISER-J150-VAN-3D-FACELIFT-01	4505	1885	1830	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 3-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-3-door-3.0-d-4d-190hp-4wd-22000
EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-PREFL-01	4760	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 5-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-5-door-3.0-d-4d-190hp-4wd-46917
EU-TOYOTA-LAND-CRUISER-J150-VAN-5D-FACELIFT-01	4780	1885	1845	Auto-Data Toyota Land Cruiser Prado J150 facelift 2013 5-door 3.0 D-4D 190	https://www.auto-data.net/en/toyota-land-cruiser-prado-j150-facelift-2013-5-door-3.0-d-4d-190hp-4wd-21998
EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	5341	2164	1835	Rolls-Royce Motor Cars press information - Effortless Everywhere: The Rolls-Royce Cullinan	https://www.press.rolls-roycemotorcars.com/united-kingdom/article/detail/T0280959EN/effortless-everywhere%3A-the-rolls-royce-cullinan?language=en_GB
EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-PREFL-01	4222	1646	1452	Škoda Auto historical Fabia Praktik data sheet	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-6Y5-PRAKTIK-VAN-FACELIFT-01	4232	1646	1452	Škoda Auto historical Fabia Praktik data sheet	https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-RENAULT-MEGANE-II-KM0-2-VAN-5D-01	4209	1777	1458	Auto-Data Renault Megane II 1.5 dCi 82;Automobile-Catalog Renault Megane 1.5 dCi 80	https://www.auto-data.net/en/renault-megane-ii-1.5-dci-82hp-10531;https://www.automobile-catalog.com/car/2004/2953670/renault_megane_1_5_dci_80.html
EU-RENAULT-CAPTUR-I-SUV-01	4122	1778	1566	Auto-Data Renault Captur facelift 2017	https://www.auto-data.net/en/renault-captur-facelift-2017-generation-5532
EU-AIXAM-MAC-500-CABRIOLET-01	2600	1385	1330	Swiss type approval 6AA706 AIXAM Mac 500	https://typenscheine.ch/de/Info/6AA706-AIXAMMac500
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Mercedes-Benz The A-Class Saloon V177 brochure	https://www.mercedes-benzcaribbean.com/assets/brochures/A_Klasse_V177_ePaper_1219_02_ENG.pdf
EU-VOLVO-760-764-SEDAN-FACELIFT-01	4785	1750	1410	ADAC Volvo 740/760 2.4 TD GLE technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/volvo/740-760/1generation/261098/
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467	Auto-Data Volkswagen Polo V Sedan facelift 2014	https://www.auto-data.net/en/volkswagen-polo-model-888
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW Group specifications of the BMW X3 valid from 09/2018	https://www.press.bmwgroup.com/global/article/detail/T0286558EN/specifications-of-the-bmw-x3-valid-from-09/2018
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607	Fiat 500X December 2018 official technical specification	https://www.media.stellantis.com/uploads/fr/FR/2019/FIAT/INFORMATIONS_TECHNIQUES/Fiche_technique_gamme_tarifs_500X_d_c_2018.pdf
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595	Fiat New 500X 2018 official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT/Schede-Tecniche/180903_Fiat_New_500X_Technical-Sheet.pdf
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603	Fiat New 500X 2018 official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT/Schede-Tecniche/180903_Fiat_New_500X_Technical-Sheet.pdf
EU-PEUGEOT-BIPPER-I-VAN-01	3864	1716	1721	Peugeot Bipper official brochure;Stellantis Fiat Professional Fiorino official press pack	https://www.autosynergy.co.uk/assets/brochures/peugeot-bipper.pdf;https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-PEUGEOT-301-I-SEDAN-PREFL-01	4442	1748	1466	Automobile-Catalog 2014 Peugeot 301 1.6 VTi	https://www.automobile-catalog.com/car/2014/2624060/peugeot_301_1_6_vti.html
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466	Auto-Data Peugeot 301 facelift 2017	https://www.auto-data.net/en/peugeot-301-facelift-2017-generation-5417
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Ford all-new Focus 2018 official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/2018/FORD_FOCUS_2018_MediaDrive_TechSpecs_EU.pdf
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471	Ford Focus official feature and technical specification	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481	Ford Focus official information brochure	https://www.ford.de/content/dam/guxeu/de/documents/shop/kaufen/angebote/ford-focus-business/BRO-Ford_Focus_Infobroschuere.pdf
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497	Ford Focus official feature and technical specification	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Kia Sportage official brochure	https://www.kia.com/content/dam/kwcms/ph/en/pdf/updated-pdf/FA_KIA_SPORTAGE_Brochure-rev_compressed.pdf
EU-PEUGEOT-508-I-SW-WAGON-PREFL-01	4813	1853	1476	Automobile-Catalog 2011 Peugeot 508 SW 2.2 HDi FAP 204	https://www.automobile-catalog.com/car/2011/2625365/peugeot_508_sw_2_2_hdi_fap_204_200.html
EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	4466	1840	1482	Vauxhall Astra GTC official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/cars/gtc/GTC_Spec_PG_2_October_2012.pdf
EU-CITROEN-C4-II-HATCHBACK-PHASE-I-01	4329	1789	1489	Auto-Data Citroën C4 II Hatchback Phase I;Auto-Data Citroën C4 model dimensions	https://www.auto-data.net/en/citroen-c4-ii-hatchback-phase-i-2010-generation-4005;https://www.auto-data.net/en/citroen-c4-model-1695
EU-PEUGEOT-207-I-HATCHBACK-3D-PREFL-01	4030	1748	1472	Automobile-Catalog 2007 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-3D-FACELIFT-01	4045	1748	1472	Automobile-Catalog 2009 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2009/2621015/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-5D-PREFL-01	4030	1748	1472	Automobile-Catalog 2007 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2007/2620400/peugeot_207_1_4_vti_95.html
EU-PEUGEOT-207-I-HATCHBACK-5D-FACELIFT-01	4045	1748	1472	Automobile-Catalog 2009 Peugeot 207 1.4 VTi 95	https://www.automobile-catalog.com/car/2009/2621015/peugeot_207_1_4_vti_95.html
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1456	Automobile-Catalog 1995 Citroën XM Break 2.0 16V	https://www.automobile-catalog.com/car/1995/544925/citroen_xm_break_2_0_16v_automatic.html
EU-CITROEN-XM-Y4-HATCHBACK-5D-01	4708	1794	1389	Automobile-Catalog 1995 Citroën XM 2.0 16V SX	https://www.automobile-catalog.com/car/1995/544775/citroen_xm_2_0_16v_sx.html
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog Maserati Biturbo Spyder range	https://www.automobile-catalog.com/make/maserati/biturbo/biturbo_spyder/1987.html
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed Sportswagon Geneva 2018 official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/Motorshows/Geneva-2018/10%20-%20Kia%20Ceed%20SW%20Geneva%20reveal%20-%20Final%20-%206%20Mar%202018.doc
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464	Citroën C6 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2024/06/Citroen-C6-2011-UK.pdf
EU-CITROEN-XSARA-PICASSO-N68-PHASE-II-MPV-01	4276	1751	1637	Auto-Data Citroën Xsara Picasso N68 Phase II 1.6 16V	https://www.auto-data.net/en/citroen-xsara-picasso-n68-phase-ii-1.6-16v-109hp-15111
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451	CarsGuide Citroën C5 2009 dimensions	https://www.carsguide.com.au/citroen/c5/car-dimensions/2009
EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	3860	1667	1510	Auto-Data Citroën C3 I Phase II 2005	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-generation-5286
EU-PEUGEOT-207-SW-WAGON-PREFL-01	4156	1748	1527	Auto-Data Peugeot 207 SW	https://www.auto-data.net/en/peugeot-207-sw-generation-6453
EU-PEUGEOT-207-SW-WAGON-FACELIFT-01	4164	1748	1527	Auto-Data Peugeot 207 SW facelift 2009	https://www.auto-data.net/en/peugeot-207-sw-facelift-2009-generation-3902
EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	4236	1805	1667	CarExpert 2016 Jeep Renegade Longitude dimensions	https://www.carexpert.com.au/jeep/renegade/2016/longitude/exterior-and-dimensions
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635	Auto-Data Vauxhall Zafira B Facelift 1.6 XER	https://www.auto-data.net/en/vauxhall-zafira-b-facelift-2008-1.6-xer-115hp-25711
EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-01	4955	1880	1496	Jaguar XF Sportbrake 2019 model year official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/XF-SB_19MY_MB-GE_V10d_DX.pdf
EU-OPEL-ASTRA-H-SEDAN-01	4587	1753	1458	Auto-Data Opel Astra H Sedan	https://www.auto-data.net/en/opel-astra-h-sedan-generation-546
EU-JAGUAR-E-PACE-X540-SUV-01	4395	1900	1649	Jaguar E-PACE official specifications;Car and Driver 2018 Jaguar E-PACE specifications	https://www.jaguar.com/en-xi/jdx/jaguar-range/e-pace/specifications/index.html;https://www.caranddriver.com/jaguar/e-pace/specs/2018/jaguar_e-pace_jaguar-e-pace_2018
EU-JAGUAR-F-PACE-X761-SVR-SUV-PREFL-01	4737	1936	1670	CarExpert 2021 Jaguar F-PACE SVR exterior dimensions	https://www.carexpert.co.nz/jaguar/f-pace/2021/svr/exterior-and-dimensions
EU-JAGUAR-F-PACE-X761-SVR-SUV-FACELIFT-01	4762	1936	1670	Jaguar F-PACE SVR 21MY official technical data;Automobile-Catalog 2021 Jaguar F-PACE SVR	https://jlrnewsroom.media/wp-content/uploads/2020/12/Jaguar-F-PACE-SVR-21MY_Tech-Data_021220.pdf;https://www.automobile-catalog.com/car/2021/3045830/jaguar_f-pace_svr.html
EU-PEUGEOT-307-I-WAGON-PREFL-01	4419	1757	1544	Automobile-Catalog 2003 Peugeot 307 Break 2.0 HDi 90	https://www.automobile-catalog.com/car/2003/2617400/peugeot_307_break_estate_2_0_hdi_90.html
EU-PEUGEOT-307-I-WAGON-FACELIFT-01	4428	1762	1560	Auto-Data Peugeot 307 Station Wagon facelift 1.6 HDi 90	https://www.auto-data.net/en/peugeot-307-station-wagon-facelift-2005-1.6-hdi-90hp-5281
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684	Automobile-Catalog 2004 Opel Zafira 1.6 16V	https://www.automobile-catalog.com/car/2004/2521790/opel_zafira_1_6_16v.html
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Kia Stonic 2018 official brochure	https://www.kia.com/content/dam/kwcms/kme/mt/mt/assets/contents/utility/brochures/StonicBrochure_210X210_AV_Jan-Feb2018.pdf
EU-OPEL-ASTRA-G-HATCHBACK-3D-FACELIFT-01	4110	1709	1425	Auto-Data Opel Astra G;Automobile-Catalog 2003 Opel Astra G 3/5-door Hatchback	https://www.auto-data.net/en/opel-astra-model-252;https://www.automobile-catalog.com/car/2003/2518505/opel_astra_1_6.html
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-OPEL-VECTRA-B-FACELIFT-SEDAN-01	4495	1707	1425	Auto-Data Opel Vectra B facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-facelift-1999-2.2-16-v-147hp-automatic-26138
EU-OPEL-VECTRA-B-FACELIFT-HATCHBACK-5D-01	4495	1707	1425	Auto-Data Opel Vectra B CC facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-cc-facelift-1999-2.2-16v-147hp-2293
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550	Hyundai KONA 2018 official brochure	https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/brochure/model/os/kona-ebrochure-2018.pdf
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550	Hyundai KONA facelift official catalog	https://www.hyundai.com/contents/repn-car/catalog_en/kona-catalog.pdf
EU-OPEL-VECTRA-B-FACELIFT-WAGON-01	4490	1710	1490	Auto-Data Opel Vectra B Caravan facelift 2.2 16V	https://www.auto-data.net/en/opel-vectra-b-caravan-facelift-1999-2.2-16v-147hp-2281
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684	Auto-Data Opel Zafira A generation	https://www.auto-data.net/en/opel-zafira-a-t3000-generation-574
EU-PEUGEOT-406-I-PHASE-II-SEDAN-01	4598	1765	1412	Automobile-Catalog 2001 Peugeot 406 1.8i 16V	https://www.automobile-catalog.com/car/2001/2614625/peugeot_406_1_8i_16v.html
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741	ADAC Audi Q7 45 TDI 08/18-06/19;ADAC Audi Q7 50 TDI 08/18-06/19	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292871/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q7/4m/292872/
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741	Audi Q7 45/50 TDI official technical data	https://www.audi.ee/dam/nemo/ee/Mudelikataloogid/tehniline_info/Tehniline%20info%20Q7%20quattro_1.pdf
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482	Ford Mondeo official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-PEUGEOT-406-I-PHASE-II-WAGON-01	4736	1760	1460	Automobile-Catalog 2001 Peugeot 406 Break 1.8i 16V	https://www.automobile-catalog.com/car/2001/2614640/peugeot_406_break_1_8i_16v.html
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501	Ford Mondeo official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-PEUGEOT-206-I-HATCHBACK-3D-PREFL-01	3835	1652	1426	Automobile-Catalog 2000 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2000/2615555/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-3D-FACELIFT-01	3822	1652	1425	Automobile-Catalog 2004 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2004/2615960/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-5D-PREFL-01	3835	1652	1426	Automobile-Catalog 2000 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2000/2615555/peugeot_206_1_6_16v_110.html
EU-PEUGEOT-206-I-HATCHBACK-5D-FACELIFT-01	3822	1652	1425	Automobile-Catalog 2004 Peugeot 206 1.6 16V 110	https://www.automobile-catalog.com/car/2004/2615960/peugeot_206_1_6_16v_110.html
EU-AUDI-A7-II-4K8-SPORTBACK-01	4969	1908	1422	Audi MediaCenter new A7 Sportback official press information	https://www.audi-mediacenter.com/en/the-new-audi-a7-sportback-progressive-in-design-and-technology-9831/download
EU-OPEL-FRONTERA-A-SPORT-HARDTOP-PREFL-01	4207	1780	1698	Automobile-Catalog 1993 Opel Frontera Sport 2.0i	https://www.automobile-catalog.com/car/1993/2493395/opel_frontera_sport_2_0i.html
EU-OPEL-FRONTERA-A-SPORT-HARDTOP-FACELIFT-01	4192	1780	1721	Automobile-Catalog 1996 Opel Frontera Sport 2.0i	https://www.automobile-catalog.com/car/1996/2493680/opel_frontera_sport_2_0i.html
EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	5120	1934	1850	Auto-Data Mercedes-Benz GL X166 GL 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-gl-x166-gl-350-bluetec-258hp-4matic-g-tronic-18788
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.1i	https://www.auto-data.net/en/peugeot-106-ii-1-1.1-i-60hp-5405
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.1i	https://www.auto-data.net/en/peugeot-106-ii-1-1.1-i-60hp-5405
EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	3941	1728	1538	Auto-Data Citroën C3 II Phase II 2013	https://www.auto-data.net/en/citroen-c3-model-1690
EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	3941	1728	1524	Auto-Data Citroën C3 II Phase I 2009	https://www.auto-data.net/en/citroen-c3-model-1690
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516	Automobile-Catalog 2003 Citroën C5 Break 2.0 HDi 110 SX	https://www.automobile-catalog.com/car/2003/549365/citroen_c5_break_2_0_hdi_110_sx.html
EU-CITROEN-C4-I-LR-VAN-3D-01	4273	1769	1456	Auto-Data Citroën C4 I Coupé 2.0 HDi 136;Citroën C4 Coupé Enterprise	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-i-2004-2.0-hdi-16v-136hp-15170;https://www.netcarshow.com/citroen/2005-c4_coupe_enterprise/
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Kia Optima official brochure	https://www.kia.com/content/dam/kwcms/kme/es/es/assets/contents/catalogos/optima/optima.pdf
EU-CITROEN-C2-I-JM-VAN-3D-01	3666	1659	1461	Auto-Data Citroën C2 I Phase I 1.1i	https://www.auto-data.net/en/citroen-c2-i-phase-i-2003-1.1i-60hp-14984
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555	Automobile-Catalog 2005 Citroën C5 Break 2.0 HDi 135 FAP Tendance	https://www.automobile-catalog.com/car/2005/549935/citroen_c5_break_2_0_hdi_135_fap_tendance.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2601-2700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://typenscheine.ch/de/Info/6AA706-AIXAMMac500?utm_source=chatgpt.com "6AA706 - AIXAM Mac 500"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1932 行）
- 累计尺寸组：dimension_groups_final.tsv（975 行）

- 尺寸冲突协调：
  - EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-01 -> EU-JAGUAR-XF-X260-SPORTBRAKE-WAGON-02：4955x1987x1496 与 4955x1880x1496，创建新尺寸组
