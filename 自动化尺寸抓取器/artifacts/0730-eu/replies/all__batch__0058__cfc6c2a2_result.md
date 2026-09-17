# 任务：all 第 5701-5800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0058__cfc6c2a2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5701-5800 行

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
all 第 5701-5800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q5-FY-SUV-FACELIFT-01	4682	1893	1662
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741
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
EU-BMW-3-G80-M3-SEDAN-RWD-01	4794	1903	1433
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393
EU-BMW-4-G23-CONVERTIBLE-RWD-01	4768	1852	1384
EU-BMW-4-G23-M440-XDRIVE-CONVERTIBLE-01	4770	1852	1394
EU-BMW-4-G82-M4-COUPE-RWD-01	4794	1887	1393
EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	4673	1849	1727
EU-MAZDA-CX-5-II-KF-SUV-01	4550	1840	1675
EU-MERCEDES-BENZ-A-KLASSE-V177-A250E-SEDAN-PREFL-01	4549	1796	1458
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-A250E-HATCHBACK-PREFL-01	4419	1796	1452
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1616
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494
EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	4424	1804	1494
EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	4650	1850	1662
EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	4634	1834	1659
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-OPEL-CROSSLAND-X-P17-SUV-02	4212	1765	1605
EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	4151	1791	1532
EU-OPEL-MOKKA-B-GASOLINE-SUV-01	4151	1791	1531
EU-OPEL-MOKKA-X-J13-SUV-01	4275	1781	1658
EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	4959	1920	1930
EU-OPEL-VIVARO-C-K0-VAN-L-01	5309	1920	1935
EU-OPEL-VIVARO-C-K0-VAN-M-01	4959	1920	1895
EU-OPEL-VIVARO-C-K0-VAN-S-01	4609	1920	1905
EU-VW-GOLF-VIII-CD-GTI-CLUBSPORT-HATCHBACK-01	4295	1789	1465
EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	4633	1789	1498
EU-VW-GOLF-VIII-GTI-HATCHBACK-01	4287	1789	1478
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477
EU-VW-TIGUAN-II-AD1-SUV-FWD-FACELIFT-01	4509	1839	1675
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Passat b8 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	90	122	Jul 2020	Mar 2024	2025-02-03	142472
VW	Passat b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	147	200	Aug 2020	Mar 2024	2025-02-03	142473
VW	Passat b8	2.0 TDI 4motion	Stufenheck	Allrad	Diesel	147	200	Aug 2020	Mar 2024	2025-02-03	142474
VW	Passat b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	90	122	Jul 2020	Mar 2024	2025-02-03	142475
Mercedes-benz	A-Klasse	A 180 D	Schrägheck	Frontantrieb	Diesel	85	116	Oct 2020	-	2024-03-01	142476
Mercedes-benz	A-Klasse	A 200 4-matic	Schrägheck	Allrad	Benzin	120	163	Oct 2020	-	2024-03-01	142477
BMW	3	316 D	Stufenheck	Heckantrieb	Diesel	85	116	Nov 2020	-	2024-03-01	142479
BMW	3	316 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	85	116	Nov 2020	-	2024-03-01	142480
BMW	3	316 D	Kombi	Heckantrieb	Diesel	90	122	Nov 2020	-	2024-03-01	142481
BMW	3	316 D	Kombi	Heckantrieb	Diesel	85	116	Nov 2020	-	2024-03-01	142482
BMW	3	316 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	85	116	Nov 2020	-	2024-03-01	142483
BMW	4	420 D Mild-hybrid	Cabriolet	Heckantrieb	Diesel/Elektro	120	163	Nov 2020	-	2024-03-01	142484
BMW	3	M 340 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	275	374	Nov 2020	-	2024-03-01	142485
BMW	3	M 340 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	275	374	Nov 2020	-	2024-03-01	142486
Mercedes-benz	A-Klasse	A 180 D	Stufenheck	Frontantrieb	Diesel	85	116	Oct 2020	-	2024-03-01	142487
Mercedes-benz	A-Klasse	A 200 4-matic	Stufenheck	Allrad	Benzin	120	163	Oct 2020	-	2024-03-01	142488
BMW	4	M 440 I Mild-hybrid Xdrive	Cabriolet	Allrad	Benzin/Elektro	275	374	Nov 2020	-	2024-03-01	142489
Mercedes-benz	B-Klasse sports tourer	B 180 D	Schrägheck	Frontantrieb	Diesel	85	116	Oct 2020	-	2024-03-01	142492
Mercedes-benz	B-Klasse sports tourer	B 200 4-matic	Schrägheck	Allrad	Benzin	120	163	Oct 2020	-	2024-03-01	142493
Mercedes-benz	Cla	CLA 180 D	Kombi	Frontantrieb	Diesel	85	116	Oct 2020	-	2024-03-01	142494
Mercedes-benz	Cla	CLA 180 D	Coupe	Frontantrieb	Diesel	85	116	Oct 2020	-	2024-03-01	142495
Mercedes-benz	Cla	CLA 200 4-matic	Coupe	Allrad	Benzin	120	163	Oct 2020	-	2024-03-01	142496
Mercedes-benz	Gla	GLA 200 4-matic	SUV	Allrad	Benzin	120	163	Oct 2020	-	2024-03-01	142497
Mercedes-benz	Glb	GLB 200 4-matic	SUV	Allrad	Benzin	120	163	Dec 2019	Mar 2023	2025-06-01	142498
Opel	Vivaro c	Vivaro-e	Kasten	Frontantrieb	Elektro	100	136	Sep 2020	Mar 2024	2025-02-03	142501
Opel	Vivaro c	Vivaro-e	Bus	Frontantrieb	Elektro	100	136	Sep 2020	Mar 2024	2025-02-03	142502
Opel	Vivaro c platform cabin	Vivaro-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	100	136	Sep 2020	Mar 2024	2025-02-03	142503
Audi	A7 sportback	55 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	270	367	Jul 2019	-	2024-03-01	142514
Audi	Q5	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	110	150	Jun 2012	May 2017	2024-03-01	142516
Chevrolet	Lumina apv mini cargo van	3.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	90	122	Sep 1990	Dec 1995	2024-03-01	142517
Chevrolet	Lumina apv mini cargo van	3.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	134	182	Sep 1995	Dec 1996	2024-03-01	142518
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Apr 2004	May 2006	2024-03-01	142524
Pontiac	Trans sport	3.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	134	182	Nov 1996	Aug 1998	2024-03-01	142525
Audi	Q5	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	100	136	May 2014	May 2017	2024-03-01	142529
Audi	Q5	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	140	190	May 2015	May 2017	2024-03-01	142530
Audi	Q5	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	190	258	Nov 2013	May 2017	2024-03-01	142531
Audi	Q5	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	210	286	Jul 2017	Nov 2020	2024-03-01	142532
Audi	Q5	3.0 SQ5 TDI Quattro	Kasten/SUV	Allrad	Diesel	230	313	Dec 2012	May 2015	2024-03-01	142533
Audi	Q5	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	180	245	Jun 2012	May 2017	2024-03-01	142534
VW	Tiguan	2.0 TSI R 4motion	SUV	Allrad	Benzin	235	320	Nov 2020	Apr 2024	2025-06-01	142540
VW	Golf viii	2.0 TSI R 4motion	Schrägheck	Allrad	Benzin	235	320	Sep 2020	-	2024-03-01	142541
Audi	Q5	2.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	125	170	Nov 2008	Sep 2012	2024-03-01	142542
Audi	Q5	2.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	130	177	Jul 2012	Jun 2014	2024-03-01	142543
Audi	Q5	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	176	239	Nov 2008	Apr 2013	2024-03-01	142545
Audi	Q5	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	105	143	Nov 2011	May 2013	2024-03-01	142546
Audi	Q5	3.0 SQ5 TDI Mild Hybrid Quattro	Kasten/SUV	Allrad	Diesel/Elektro	255	347	Feb 2019	Nov 2020	2024-03-01	142547
Audi	Q5	3.2 FSI Quattro	Kasten/SUV	Allrad	Benzin	199	271	Nov 2008	Sep 2012	2024-03-01	142548
Audi	Q5	2.0 Tfsi Quattro	Kasten/SUV	Allrad	Benzin	155	211	Nov 2008	Sep 2012	2024-03-01	142549
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	150	204	Nov 2010	Aug 2015	2024-03-01	142550
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	155	211	Mar 2006	May 2010	2024-03-01	142551
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	160	218	Aug 2015	Dec 2019	2024-03-01	142552
Dfsk	C35	1.5	Kasten	Heckantrieb	Benzin	74	101	Feb 2018	-	2024-03-01	142553
Dfsk	C35	1.5 4WD	Kasten	Allrad	Benzin	74	101	Feb 2018	-	2024-03-01	142554
Dfsk	C31	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	74	101	Feb 2018	-	2024-03-01	142555
Dfsk	C31	1.5 4WD	Pritsche/Fahrgestell	Allrad	Benzin	74	101	Feb 2018	-	2024-03-01	142556
Dfsk	C32	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	74	101	Feb 2018	-	2024-03-01	142557
Dfsk	C32	1.5 4WD	Pritsche/Fahrgestell	Allrad	Benzin	74	101	Feb 2018	-	2024-03-01	142558
Audi	Q5	3.0 SQ5 TDI Quattro	Kasten/SUV	Allrad	Diesel	240	326	Apr 2015	May 2017	2024-03-01	142559
Audi	Q5	3.0 SQ5 TDI Quattro	Kasten/SUV	Allrad	Diesel	250	340	Nov 2015	May 2017	2024-03-01	142560
Chevrolet	Captiva	Vcdi Allrad	Kasten/SUV	Allrad	Diesel	110	150	Jul 2006	Feb 2011	2024-03-01	142561
Chevrolet	Captiva	Vcdi	Kasten/SUV	Frontantrieb	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	142562
VW	Touran	1.4 TSI Ecofuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	110	150	May 2010	May 2015	2024-03-01	142564
Audi	Q7	3.0 45 TDI Mild Hybrid Quattro	Kasten/SUV	Allrad	Diesel/Elektro	170	231	Jul 2018	Dec 2019	2024-03-01	142566
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	171	232	Mar 2006	May 2008	2024-03-01	142567
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	176	240	Nov 2007	May 2012	2024-03-01	142568
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	180	245	May 2011	Aug 2015	2024-03-01	142569
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	200	272	Jan 2015	Dec 2019	2024-03-01	142570
Audi	Q7	3.0 50 TDI Mild Hybrid Quattro	Kasten/SUV	Allrad	Diesel/Elektro	210	286	Jul 2018	Dec 2019	2024-03-01	142573
Audi	Q7	3.0 Tfsi Quattro	Kasten/SUV	Allrad	Benzin	245	333	May 2010	Aug 2015	2024-03-01	142574
Audi	Q7	3.6 FSI Quattro	Kasten/SUV	Allrad	Benzin	206	280	Aug 2006	May 2010	2024-03-01	142575
Audi	Q7	4.0 SQ7 TDI Quattro	Kasten/SUV	Allrad	Diesel	320	435	Apr 2016	-	2024-03-01	142576
Audi	Q7	4.2 TDI Quattro	Kasten/SUV	Allrad	Diesel	240	326	Mar 2007	Jun 2009	2024-03-01	142577
Audi	Q7	4.2 TDI Quattro	Kasten/SUV	Allrad	Diesel	250	340	Mar 2007	Aug 2015	2024-03-01	142578
Audi	Q7	4.2 FSI Quattro	Kasten/SUV	Allrad	Benzin	257	350	Aug 2006	May 2010	2024-03-01	142579
Audi	Q7	6.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	368	500	Sep 2008	May 2014	2024-03-01	142580
Opel	Mokka	1.5	SUV	Frontantrieb	Diesel	81	110	Oct 2020	-	2024-03-01	142598
Opel	Crossland x /	1.5	SUV	Frontantrieb	Diesel	81	110	Oct 2020	-	2024-03-01	142600
Mazda	Cx-5	Skyactiv-g	Kasten/SUV	Frontantrieb	Benzin	121	165	Apr 2015	Feb 2017	2024-03-01	142602
Mazda	Cx-5	Skyactiv-g AWD	Kasten/SUV	Allrad	Benzin	118	160	Apr 2015	Feb 2017	2024-03-01	142603
Mazda	Cx-5	Skyactiv-g AWD	Kasten/SUV	Allrad	Benzin	141	192	Apr 2015	Feb 2017	2024-03-01	142604
Mazda	Cx-5	Skyactiv-d	Kasten/SUV	Frontantrieb	Diesel	110	150	Apr 2015	Feb 2017	2024-03-01	142605
Mazda	Cx-5	Skyactiv-d AWD	Kasten/SUV	Allrad	Diesel	110	150	Apr 2015	Feb 2017	2024-03-01	142606
Mazda	Cx-5	Skyactiv-d AWD	Kasten/SUV	Allrad	Diesel	129	175	Apr 2015	Feb 2017	2024-03-01	142607
Peugeot	806	TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Jul 1995	Aug 2002	2024-03-01	142608
Peugeot	806	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Jun 1999	Feb 2003	2024-03-01	142609
Peugeot	806	DT	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Feb 1997	May 2000	2024-03-01	142610
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	97	132	May 1998	Sep 2000	2024-03-01	142611
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	100	136	May 2000	Feb 2003	2024-03-01	142612
Peugeot	806	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	108	147	Feb 1997	May 2000	2024-03-01	142613
Genesis	G80	2.5 T-gdi AWD	Stufenheck	Allrad	Benzin	224	304	Aug 2020	-	2025-12-01	142615
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	79	107	Jun 2002	May 2006	2024-03-01	142624
Peugeot	807	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	94	128	Apr 2004	May 2006	2024-03-01	142626
Peugeot	807	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	120	163	May 2010	-	2024-03-01	142636
Peugeot	2008 i van	Puretech 130	Kasten/SUV	Frontantrieb	Benzin	96	131	Jan 2018	Nov 2019	2024-11-01	142637
Peugeot	2008 i van	Bluehdi 100	Kasten/SUV	Frontantrieb	Diesel	75	102	May 2018	-	2024-03-01	142638
Peugeot	2008 i van	Bluehdi 120	Kasten/SUV	Frontantrieb	Diesel	88	120	May 2018	-	2024-03-01	142639
Peugeot	3008 van	HDI 110	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Jun 2009	Aug 2016	2024-11-01	142640
Peugeot	3008 van	HDI 150	Kasten/Großraumlimousine	Frontantrieb	Diesel	110	150	Jun 2009	Aug 2016	2024-11-01	142641
Peugeot	3008 van	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	120	163	Jun 2009	Aug 2016	2024-11-01	142642
VW	Touran	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	125	170	May 2010	May 2015	2024-03-01	142643


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Passat B8、A-Class、BMW G20/G21/G23、CLA、GLA、GLB、Vivaro 平台驾驶室、Captiva、Mokka B 等现有尺寸组的关联复用。
* 首次闭合 B-Class W247、Audi A7 C8、Lumina APV、Pontiac Trans Sport II、Peugeot 806/807、Tiguan R、Golf R、Genesis G80 RG3、Peugeot 3008 I 共 10 类物理外廓。相关三维分别由对应车型规格页支持。([汽车数据网][1])
* Touran 2010–2015 第二次改款外廓为 `4397 × 1794 × 1674 mm`，与已有的 `EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01` 三维不一致，因此未覆盖旧组，另建 `EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01`。([大众汽车爱尔兰][2])
* Mokka B 1.5 Diesel 的三维与已有汽油尺寸组一致，已按相同物理外廓复用。([汽车数据网][3])
* Crossland 142600 暂未关联已有组：2020 改款资料显示长度约 4217 mm，而现有两个组均为 4212 mm，需要继续厘清 Ktype 对应改款前还是改款后外廓。([Vauxhall][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：48
* PENDING 映射：52
* READY 映射当前引用尺寸组：28
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142472	142472	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	B8 Variant 改款旅行车外廓。	READY
142473	142473	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	B8 Variant 改款旅行车外廓。	READY
142474	142474	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	B8 改款四门三厢外廓。	READY
142475	142475	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	B8 改款四门三厢外廓。	READY
142476	142476	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177 五门掀背外廓。	READY
142477	142477	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177 五门掀背外廓。	READY
142479	142479	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20 后驱四门三厢外廓。	READY
142480	142480	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20 后驱四门三厢外廓。	READY
142481	142481	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	G21 后驱旅行车外廓。	READY
142482	142482	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	G21 后驱旅行车外廓。	READY
142483	142483	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	G21 后驱旅行车外廓。	READY
142484	142484	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-CONVERTIBLE-RWD-01	HIGH	G23 后驱双门敞篷外廓。	READY
142485	142485	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	G21 M340i xDrive 旅行车外廓。	READY
142486	142486	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	MEDIUM	G20 M340 xDrive 四门三厢外廓。	READY
142487	142487	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177 改款前四门三厢外廓。	READY
142488	142488	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177 改款前四门三厢外廓。	READY
142489	142489	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-M440-XDRIVE-CONVERTIBLE-01	HIGH	G23 M440 xDrive 双门敞篷外廓。	READY
142492	142492	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	HIGH	W247 五门 Sports Tourer 外廓。	READY
142493	142493	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	HIGH	W247 五门 Sports Tourer 外廓。	READY
142494	142494	Wagon	CLA X118	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH	X118 五门 Shooting Brake 外廓。	READY
142495	142495	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 四门 Coupe 外廓。	READY
142496	142496	Coupe	CLA C118	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH	C118 四门 Coupe 外廓。	READY
142497	142497	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 改款前五门 SUV 外廓。	READY
142498	142498	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247 改款前五门 SUV 外廓。	READY
142503	142503	Pickup	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	HIGH	中轴平台驾驶室外廓。	READY
142514	142514	Hatchback	A7 C8		5	EU-AUDI-A7-C8-LIFTBACK-PREFL-01	HIGH	C8 Sportback 五门升降尾门外廓。	READY
142517	142517	MPV	Lumina APV I		4	EU-CHEVROLET-LUMINA-APV-I-MPV-01	HIGH	第一代 APV 四门厢式 MPV 外廓。	READY
142524	142524	MPV	Peugeot 807		5	EU-PEUGEOT-807-MPV-01	HIGH	807 五门 MPV 外廓。	READY
142525	142525	MPV	Trans Sport II			EU-PONTIAC-TRANS-SPORT-II-MPV-01	HIGH	第二代 Trans Sport MPV 外廓。	READY
142540	142540	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-R-SUV-FACELIFT-01	HIGH	AD1 改款 R 外廓。	READY
142541	142541	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-R-HATCHBACK-01	HIGH	Golf VIII R 五门掀背外廓。	READY
142561	142561	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	HIGH	C100 改款前五门 SUV 外廓。	READY
142562	142562	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	HIGH	C100 改款前五门 SUV 外廓。	READY
142564	142564	MPV	Touran I facelift	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	1T3 第二次改款五门 MPV 外廓。	READY
142598	142598	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GASOLINE-SUV-01	HIGH	Mokka B 标准五门 SUV 外廓。	READY
142608	142608	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142609	142609	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142610	142610	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142611	142611	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142612	142612	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142613	142613	MPV	Peugeot 806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221 五门 MPV 外廓。	READY
142615	142615	Sedan	G80 III	RG3	4	EU-GENESIS-G80-III-RG3-SEDAN-AWD-01	HIGH	RG3 AWD 四门三厢外廓。	READY
142624	142624	MPV	Peugeot 807		5	EU-PEUGEOT-807-MPV-01	HIGH	807 五门 MPV 外廓。	READY
142626	142626	MPV	Peugeot 807		5	EU-PEUGEOT-807-MPV-01	HIGH	807 五门 MPV 外廓。	READY
142640	142640	MPV	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	第一代 3008 五门商用化外廓。	READY
142641	142641	MPV	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	第一代 3008 五门商用化外廓。	READY
142642	142642	MPV	Peugeot 3008 I		5	EU-PEUGEOT-3008-I-MPV-01	MEDIUM	第一代 3008 五门商用化外廓。	READY
142643	142643	MPV	Touran I facelift	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH	1T3 第二次改款五门 MPV 外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	4419	1796	1562	Auto-Data	https://www.auto-data.net/en/mercedes-benz-b-class-model-1363
EU-AUDI-A7-C8-LIFTBACK-PREFL-01	4969	1908	1422	Audi official facts and figures;Auto-Data	https://www.audi.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835;https://www.auto-data.net/en/audi-a7-sportback-c8-55-tfsi-e-367hp-plug-in-hybrid-quattro-ultra-s-tronic-37660
EU-CHEVROLET-LUMINA-APV-I-MPV-01	4844	1877	1669	Auto-Data	https://www.auto-data.net/en/chevrolet-lumina-apv-generation-3163
EU-PEUGEOT-807-MPV-01	4730	1850	1750	Auto-Data	https://www.auto-data.net/en/peugeot-807-generation-1262
EU-PONTIAC-TRANS-SPORT-II-MPV-01	5115	1845	1730	Auto-Data	https://www.auto-data.net/en/pontiac-trans-sport-ii-generation-1387
EU-VW-TIGUAN-II-R-SUV-FACELIFT-01	4514	1859	1668	Auto-Data	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-r-2.0-tsi-320hp-4motion-dsg-41760
EU-VW-GOLF-VIII-R-HATCHBACK-01	4290	1789	1458	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-viii-r-2.0-tsi-320hp-4motion-dsg-41722
EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	4397	1794	1674	Volkswagen official previous models;Auto-Data	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/touran-1.html;https://www.auto-data.net/en/volkswagen-touran-i-facelift-2010-tgi-1.4-tsi-150hp-dsg-bluemotion-20584
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Auto-Data	https://www.auto-data.net/en/peugeot-806-221-generation-1253
EU-GENESIS-G80-III-RG3-SEDAN-AWD-01	4996	1925	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2972600/genesis_g80_2_5t_awd.html
EU-PEUGEOT-3008-I-MPV-01	4365	1837	1639	Auto-Data	https://www.auto-data.net/en/peugeot-3008-model-577
```

## 下一步优先处理

1. 集中闭合 Audi Q5 8R 的改款前、改款后及 SQ5 外廓分支。
2. 闭合 Audi Q7 4L、4M 改款前及 SQ7 特殊外廓。
3. 确认 Vivaro-e Kasten/Bus 的 S、M、L 长度分支及 DFSK C31/C32/C35 车身边界。
4. 解决 Crossland 改款长度、Mazda CX-5 2015 高度、Peugeot 2008 宽度口径、Lumina APV 3.4 代际及 807 后期车型边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-b-class-model-1363?utm_source=chatgpt.com "Specs for all generations of Mercedes-Benz B-class"
[2]: https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/touran-1.html "VW Touran Type 1T (2003–2015) models"
[3]: https://www.auto-data.net/en/opel-mokka-b-1.5-diesel-110hp-41306?utm_source=chatgpt.com "Opel Mokka B 1.5 Diesel (110 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/crossland/price-guides/Crossland_X_Spec_ePG_2_September_2020_Library-1602148545.pdf?utm_source=chatgpt.com "Price and Specification Guide  |  2 September 2020  |  Model Year 2020.5"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Audi Q5 8R 改款前、改款后、SQ5 8R、SQ5 FY 四类外廓，并批量关联 16 个 Ktype。([Dezo's Garage][1])
* 已闭合 Audi Q7 4L 改款前、改款后、Q7 V12 TDI、SQ7 4M 外廓；跨越改款边界的 `142568` 拆分为两条派生映射。
* 已闭合 DFSK C31、C32、C35，Mazda CX-5 KE 改款型和 Peugeot 2008 I 外廓。
* Crossland、Lumina APV、Peugeot 807 直接关联已闭合尺寸组，未重复创建。
* 当前仅剩 Vivaro-e Kasten 与 Bus 的长度分支边界待闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：99
* PENDING Ktype：2
* 已确认并引用尺寸组：44
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142516	142516	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142518	142518	MPV	Lumina APV I		4	EU-CHEVROLET-LUMINA-APV-I-MPV-01	HIGH	第一代APV末期3.4版本外廓。	READY
142529	142529	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142530	142530	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142531	142531	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142532	142532	SUV	Q5 II	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH	FY改款前标准SUV外廓。	READY
142533	142533	SUV	SQ5 I	8R	5	EU-AUDI-SQ5-8R-SUV-01	HIGH	8R SQ5宽体及运动外部套件外廓。	READY
142534	142534	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142542	142542	SUV	Q5 I	8R	5	EU-AUDI-Q5-8R-SUV-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
142543	142543	SUV	Q5 I facelift	8R	5	EU-AUDI-Q5-8R-SUV-FACELIFT-01	HIGH	8R改款标准SUV外廓。	READY
142545	142545	SUV	Q5 I	8R	5	EU-AUDI-Q5-8R-SUV-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
142546	142546	SUV	Q5 I	8R	5	EU-AUDI-Q5-8R-SUV-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
142547	142547	SUV	SQ5 II	FY	5	EU-AUDI-SQ5-FY-TDI-SUV-PREFL-01	HIGH	FY改款前SQ5 TDI外廓。	READY
142548	142548	SUV	Q5 I	8R	5	EU-AUDI-Q5-8R-SUV-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
142549	142549	SUV	Q5 I	8R	5	EU-AUDI-Q5-8R-SUV-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
142550	142550	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	4L改款标准SUV外廓。	READY
142551	142551	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	4L改款前标准SUV外廓。	READY
142552	142552	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前标准SUV外廓。	READY
142553	142553	Van	C35	C35		EU-DFSK-C35-VAN-01	HIGH	C35封闭式厢式车外廓。	READY
142554	142554	Van	C35	C35		EU-DFSK-C35-VAN-01	HIGH	四驱系统不改变C35车身外廓。	READY
142555	142555	Pickup	C31	C31	2	EU-DFSK-C31-SINGLE-CAB-PICKUP-01	HIGH	C31单排驾驶室平台货车外廓。	READY
142556	142556	Pickup	C31	C31	2	EU-DFSK-C31-SINGLE-CAB-PICKUP-01	HIGH	四驱系统不改变C31驾驶室及平台外廓。	READY
142557	142557	Pickup	C32	C32	4	EU-DFSK-C32-DOUBLE-CAB-PICKUP-01	HIGH	C32双排驾驶室平台货车外廓。	READY
142558	142558	Pickup	C32	C32	4	EU-DFSK-C32-DOUBLE-CAB-PICKUP-01	HIGH	四驱系统不改变C32驾驶室及平台外廓。	READY
142559	142559	SUV	SQ5 I	8R	5	EU-AUDI-SQ5-8R-SUV-01	HIGH	8R SQ5宽体及运动外部套件外廓。	READY
142560	142560	SUV	SQ5 I	8R	5	EU-AUDI-SQ5-8R-SUV-01	HIGH	8R SQ5宽体及运动外部套件外廓。	READY
142566	142566	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前标准SUV外廓。	READY
142567	142567	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	4L改款前标准SUV外廓。	READY
142568_prefl	142568	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	该Ktype覆盖改款前外廓分支。	READY
142568_facelift	142568	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	该Ktype覆盖改款后外廓分支。	READY
142569	142569	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	4L改款标准SUV外廓。	READY
142570	142570	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前标准SUV外廓。	READY
142573	142573	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	4M改款前标准SUV外廓。	READY
142574	142574	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	HIGH	4L改款标准SUV外廓。	READY
142575	142575	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	4L改款前标准SUV外廓。	READY
142576	142576	SUV	SQ7 I	4M	5	EU-AUDI-SQ7-4M-TDI-SUV-PREFL-01	HIGH	4M SQ7 TDI特殊外部套件外廓。	READY
142577	142577	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	4L改款前标准SUV外廓。	READY
142578	142578	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	MEDIUM	250kW版本对应4L改款外廓。	READY
142579	142579	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-PREFL-01	HIGH	4L改款前标准SUV外廓。	READY
142580	142580	SUV	Q7 V12 TDI	4L	5	EU-AUDI-Q7-I-4L-V12-TDI-SUV-01	HIGH	V12专属前后保险杠、侧裙及轮拱外廓。	READY
142600	142600	SUV	Crossland facelift	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-02	HIGH	P17改款五门SUV外廓。	READY
142602	142602	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142603	142603	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142604	142604	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142605	142605	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142606	142606	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142607	142607	SUV	CX-5 I facelift	KE	5	EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	HIGH	KE改款五门SUV外廓。	READY
142636	142636	MPV	Peugeot 807		5	EU-PEUGEOT-807-MPV-01	HIGH	807后期柴油版本保持既有五门MPV外廓。	READY
142637	142637	Van	2008 I	A94	5	EU-PEUGEOT-2008-I-VAN-01	HIGH	第一代2008商用化五门外廓。	READY
142638	142638	Van	2008 I	A94	5	EU-PEUGEOT-2008-I-VAN-01	HIGH	第一代2008商用化五门外廓。	READY
142639	142639	Van	2008 I	A94	5	EU-PEUGEOT-2008-I-VAN-01	HIGH	第一代2008商用化五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q5-8R-SUV-FACELIFT-01	4629	1898	1655	Audi Q5 and SQ5 UK Pricing and Specification Guide	https://xr793.com/wp-content/uploads/2022/10/2013-Audi-Q5-SQ5-UK.pdf
EU-AUDI-Q5-8R-SUV-PREFL-01	4629	1880	1653	Audi Q5 UK Pricing and Specification Guide	https://xr793.com/wp-content/uploads/2022/10/2009-Audi-Q5-UK.pdf
EU-AUDI-SQ5-8R-SUV-01	4644	1911	1624	Audi Q5 and SQ5 UK Pricing and Specification Guide	https://xr793.com/wp-content/uploads/2022/10/2013-Audi-Q5-SQ5-UK.pdf
EU-AUDI-SQ5-FY-TDI-SUV-PREFL-01	4671	1893	1635	Audi UK SQ5 Technical Data	https://press.audi.co.uk/assets/documents/original/21087-AudiUK00017568AudiSQ5TFSIQ520TDI.pdf
EU-AUDI-Q7-I-4L-SUV-PREFL-01	5086	1983	1737	Audi UK Q7 4.2 FSI Technical Data	https://press.audi.co.uk/assets/documents/original/21721-AudiUK00000878Q742FSIquattrotechdata.pdf
EU-AUDI-Q7-I-4L-SUV-FACELIFT-01	5089	1983	1737	Audi Q7 UK Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/21705-AudiUK00000110Q7PriceandSpecification.pdf
EU-AUDI-SQ7-4M-TDI-SUV-PREFL-01	5069	1968	1741	Audi UK SQ7 4.0 TDI Technical Data	https://press.audi.co.uk/assets/documents/original/22075-AudiUK00016128AudiSQ7TDI40litre.pdf
EU-AUDI-Q7-I-4L-V12-TDI-SUV-01	5086	1983	1737	Audi UK Q7 6.0 TDI Technical Data	https://press.audi.co.uk/assets/documents/original/21707-AudiUK00000163Q7PI60TDIquattro.pdf
EU-DFSK-C35-VAN-01	4500	1680	1960	DFSK C35 and C37 specification sheet	https://static.multiaviso.com/vehicle/specs/22-VRZC564XLBE6-dfsk-otros-modelos-2017-furgon-c35.pdf
EU-DFSK-C31-SINGLE-CAB-PICKUP-01	4730	1655	1890	DFSK C31/C32 official distributor brochure	https://dfsk-auto.pl/file/cenniki/katalog_c31_c32.pdf
EU-DFSK-C32-DOUBLE-CAB-PICKUP-01	4940	1655	1910	DFSK C31/C32 official distributor brochure	https://dfsk-auto.pl/file/cenniki/katalog_c31_c32.pdf
EU-MAZDA-CX-5-I-KE-SUV-FACELIFT-01	4555	1840	1710	Mazda CX-5 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Mazda-CX-5-2015-UK.pdf
EU-PEUGEOT-2008-I-VAN-01	4159	1739	1556	Peugeot 2008 model-year brochure	https://autocatalogarchive.com/wp-content/uploads/2019/08/Peugeot-2008-2018-MY.pdf
```

## 下一步优先处理

闭合 `142501` Vivaro-e Kasten 的 S/M/L 覆盖范围，以及 `142502` Vivaro-e Bus 的 M/L 分支与对应高度；完成后立即进入一次轻量机械收尾并输出两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/10/2009-Audi-Q5-UK.pdf?utm_source=chatgpt.com "2009-Audi-Q5-UK.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

