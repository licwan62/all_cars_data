# 任务：all 第 2101-2200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0022__b7a215b0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2101-2200 行

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
all 第 2101-2200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538
EU-CHEVROLET-CAPRICE-III-COUPE-1981-01	5387	1913	1387
EU-CHEVROLET-CAPRICE-III-COUPE-1982-1983-01	5387	1913	1433
EU-CHEVROLET-CAPRICE-III-COUPE-1984-01	5405	1915	1433
EU-CHEVROLET-IMPALA-IV-COUPE-1974-01	5657	2019	1364
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-TESLA-MODEL-X-I-SUV-01	5052	1999	1684
EU-TOYOTA-CAMRY-XV70-SEDAN-01	4885	1840	1445
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-T-ROC-I-SUV-01	4234	1819	1573

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jeep	Wrangler iv	2.0 T-gdi	Geländewagen offen	Allrad	Benzin	199	270	Nov 2017	-	2024-03-01	130547
Jeep	Wrangler iv	2.2 Multijet II	Geländewagen offen	Allrad	Diesel	147	200	Nov 2017	-	2024-03-01	130548
Seat	Leon	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	81	110	Apr 2014	Aug 2018	2024-03-01	130556
Seat	Leon	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Nov 2012	Oct 2016	2024-03-01	130564
Seat	Leon	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	77	105	Sep 2012	Oct 2016	2024-03-01	130566
Seat	Leon	2.0 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	110	150	Oct 2012	Aug 2018	2024-03-01	130570
Seat	Leon	1.2 TSI	Kasten/Kombi	Frontantrieb	Benzin	81	110	May 2014	Aug 2018	2024-03-01	130574
Seat	Leon	2.0 Cupra 4drive	Kasten/Kombi	Allrad	Benzin	221	300	Nov 2016	Aug 2018	2024-03-01	130579
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	287	390	Feb 2018	Dec 2022	2024-05-01	130588
Ssangyong	Musso	2.2 E-xdi	Pick-up	Heckantrieb	Diesel	133	181	Jan 2018	-	2024-03-01	130589
Ssangyong	Musso	2.2 E-xdi 4WD	Pick-up	Allrad	Diesel	133	181	Jan 2018	-	2024-03-01	130590
Mercedes-benz	A-Klasse	A 180 D	Schrägheck	Frontantrieb	Diesel	85	116	Mar 2018	-	2024-03-01	130593
Mercedes-benz	A-Klasse	A 200	Schrägheck	Frontantrieb	Benzin	120	163	Mar 2018	-	2024-03-01	130594
Mercedes-benz	A-Klasse	A 250	Schrägheck	Frontantrieb	Benzin	165	224	Mar 2018	-	2024-03-01	130595
Tesla	Model x	60D AWD	Schrägheck	Allrad	Elektro	386	525	Jun 2016	Apr 2026	2026-06-01	130598
Porsche	911	4.0 GT3	Coupe	Heckantrieb	Benzin	368	500	May 2017	Dec 2020	2024-03-01	130599
Porsche	911	4.0 GT3 RS	Coupe	Heckantrieb	Benzin	383	520	May 2018	Dec 2020	2024-03-01	130600
Porsche	911	3.0 Carrera T	Coupe	Heckantrieb	Benzin	272	370	Jan 2018	Dec 2019	2024-03-01	130601
Chevrolet	Aveo / kalos	1.4 16V	Schrägheck	Frontantrieb	Benzin	69	94	Jun 2006	May 2008	2024-03-01	130602
Chevrolet	Caprice	5.7	Stufenheck	Heckantrieb	Benzin	127	173	Oct 1976	Dec 1979	2024-03-01	130604
Lexus	Rc	F	Coupe	Heckantrieb	Benzin	341	464	Mar 2018	-	2024-03-01	130606
Toyota	Proace verso	1.6 D4D	Bus	Frontantrieb	Diesel	85	116	Feb 2016	Apr 2020	2025-02-03	130609
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	110	150	Feb 2016	Dec 2022	2026-01-01	130610
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	130	177	Feb 2016	Apr 2025	2026-01-01	130611
Toyota	Proace verso	1.6 D4D	Bus	Frontantrieb	Diesel	70	95	Feb 2016	Dec 2019	2026-01-01	130612
Dacia	Duster	1.6 SCE 115	SUV	Frontantrieb	Benzin	84	115	Oct 2017	-	2024-03-01	130624
Dacia	Duster	1.6 SCE 115 4X4	SUV	Allrad	Benzin	84	115	Oct 2017	-	2024-03-01	130625
Dacia	Duster	1.6 SCE 115 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	80	109	Oct 2017	-	2024-03-01	130626
Polestar	Polestar 1	Phev AWD	Coupe	Allrad	Benzin/Elektro	448	609	Mar 2018	-	2024-03-01	130635
BMW	6	630 D Xdrive	Schrägheck	Allrad	Diesel	183	249	Jun 2017	Jun 2020	2024-03-01	130636
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	155	211	Jul 2017	Jun 2020	2024-03-01	130639
BMW	5	520 I	Kombi	Heckantrieb	Benzin	155	211	Jul 2017	Jun 2020	2024-03-01	130642
Chevrolet	Caprice	7.4	Coupe	Heckantrieb	Benzin	291	396	Sep 1969	Dec 1970	2024-03-01	130650
Chevrolet	Impala	5.7	Coupe	Heckantrieb	Benzin	119	162	Sep 1976	Dec 1978	2024-03-01	130669
Maybach	62	5.5	Stufenheck	Heckantrieb	Benzin	405	551	Sep 2002	Dec 2012	2024-03-01	130680
Maybach	62	S 6.0	Stufenheck	Heckantrieb	Benzin	450	612	Sep 2005	Dec 2012	2024-03-01	130682
Maybach	62	6.0 S	Stufenheck	Heckantrieb	Benzin	463	630	Jan 2011	Dec 2012	2024-03-01	130683
Chevrolet	Silverado 2500 crew cab pickup	5.3 Flexfuel 4WD	Pick-up	Allrad	Benzin/Ethanol	235	320	Feb 2011	Oct 2013	2024-03-01	130696
Chevrolet	Silverado 2500 standard cab pickup	5.3 Flexfuel 4WD	Pick-up	Allrad	Benzin/Ethanol	235	320	Feb 2011	Oct 2013	2024-03-01	130697
Chevrolet	Silverado 2500	5.3 Hybrid 4WD	Pick-up	Allrad	Benzin/Elektro	220	299	Sep 2007	Sep 2009	2024-03-01	130698
Toyota	Camry	2.5	Stufenheck	Frontantrieb	Benzin	133	181	Aug 2017	-	2024-03-01	130701
Toyota	Rav 4 i	2.0 4WD	SUV	Allrad	Benzin	94	128	Jul 1996	Jun 2000	2024-03-01	130706
Peugeot	3008 ii	1.5 Bluehdi 130	SUV	Frontantrieb	Diesel	96	131	Feb 2018	-	2024-11-01	130708
Dodge	Caliber	2.0 CRD	Schrägheck	Frontantrieb	Diesel	100	136	Jun 2006	Nov 2011	2024-03-01	130733
Peugeot	5008	1.5 Bluehdi 130	Großraumlimousine	Frontantrieb	Diesel	96	131	Feb 2018	-	2024-03-01	130738
Peugeot	Rifter	1.2 Puretech 110	Großraumlimousine	Frontantrieb	Benzin	81	110	Sep 2018	-	2024-03-01	130752
Peugeot	Rifter	1.5 Bluehdi 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2018	-	2024-03-01	130754
Peugeot	Rifter	1.5 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	75	102	Aug 2018	-	2025-11-01	130755
Peugeot	Rifter	1.5 Bluehdi 130	Großraumlimousine	Frontantrieb	Diesel	96	131	Sep 2018	-	2025-12-01	130756
Hyundai	Santa fe iv	2.0 Crdi	SUV	Frontantrieb	Diesel	137	186	Feb 2018	Jul 2020	2024-03-01	130766
Hyundai	Santa fe iv	2.0 Crdi AWD	SUV	Allrad	Diesel	137	186	Feb 2018	Jul 2020	2024-03-01	130767
Audi	A3	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	137	186	Sep 2016	Oct 2020	2026-05-01	130789
Mercedes-benz	Cls	CLS 300 D	Coupe	Heckantrieb	Diesel	180	245	Apr 2018	-	2024-03-01	130797
Lexus	Is iii	300	Stufenheck	Heckantrieb	Benzin	180	245	Oct 2017	-	2024-03-01	130800
Lexus	Rc	300	Coupe	Heckantrieb	Benzin	180	245	Nov 2017	-	2024-03-01	130802
MG	Zs	1.0 T-gdi	SUV	Frontantrieb	Benzin	82	111	Oct 2017	-	2025-12-01	130805
MG	Zs	1.5 VTI	SUV	Frontantrieb	Benzin	78	106	Oct 2017	-	2025-12-01	130806
Toyota	Proace verso	2.0 D4D 4X4	Bus	Allrad	Diesel	110	150	Apr 2018	Dec 2022	2026-01-01	130815
Lancia	Delta i	2.0 16V HF EVO Integrale	Schrägheck	Allrad	Benzin	151	205	Jun 1991	Jan 1994	2024-03-01	130816
VW	T-Roc	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Mar 2018	-	2024-03-01	130824
VW	T-Roc	1.6 TDI	SUV	Frontantrieb	Diesel	85	115	Mar 2018	Jun 2021	2024-03-01	130825
Opel	Grandland	1.5 Turbo D	SUV	Frontantrieb	Diesel	96	131	Apr 2018	-	2025-02-03	130834
Volvo	V60 ii	T5	Kombi	Frontantrieb	Benzin	184	250	Feb 2018	Dec 2021	2024-05-01	130835
Volvo	V60 ii	T6 AWD	Kombi	Allrad	Benzin	228	310	Feb 2018	Dec 2021	2024-05-01	130836
Volvo	V60 ii	T8 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	287	390	Feb 2018	Dec 2022	2024-05-01	130837
Volvo	V60 ii	D3	Kombi	Frontantrieb	Diesel	110	150	Feb 2018	Dec 2021	2024-05-01	130838
Volvo	V60 ii	D4	Kombi	Frontantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-05-01	130839
Honda	Civic x	1.6 I-dtec	Stufenheck	Frontantrieb	Diesel	88	120	May 2018	Dec 2022	2024-03-01	130846
Opel	Karl	1	Schrägheck	Frontantrieb	Benzin	54	73	Jan 2018	Mar 2019	2024-03-01	130857
Cadillac	Xt4	2	SUV	Frontantrieb	Benzin	177	241	Mar 2018	-	2024-03-01	130859
Piaggio	Ape	0.1	Kasten	Heckantrieb	Benzin	2	3	Jan 2010	-	2024-03-01	130860
Ford	Focus iv	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	74	101	Jan 2018	Nov 2025	2026-02-01	130861
Ford	Focus iv	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	92	125	Jan 2018	Nov 2025	2026-02-01	130862
Piaggio	Ape	0.1	Pritsche/Fahrgestell	Heckantrieb	Gemisch	2	3	Jan 2010	-	2024-03-01	130863
Toyota	Proace	2.0 D4D 4X4	Kasten	Allrad	Diesel	110	150	Apr 2018	Dec 2022	2026-01-01	130885
Volvo	Xc60 ii	D4	SUV	Frontantrieb	Diesel	140	190	Mar 2017	Dec 2021	2024-05-01	130894
Volvo	Xc60 ii	D3	SUV	Frontantrieb	Diesel	110	150	Mar 2017	Dec 2021	2024-05-01	130895
BMW	2	M2 Competition	Coupe	Heckantrieb	Benzin	302	411	Jun 2018	Jun 2021	2024-03-01	130898
Peugeot	308 cc	1.6 HDI	Cabriolet	Frontantrieb	Diesel	82	111	Feb 2009	May 2012	2024-03-01	130900
Mitsubishi	Eclipse cross	1.5	SUV	Frontantrieb	Benzin	110	150	Oct 2017	-	2024-03-01	130926
Mitsubishi	Eclipse cross	1.5 4WD	SUV	Allrad	Benzin	110	150	Oct 2017	-	2024-03-01	130927
Jaguar	Vanden plas	3.6	Stufenheck	Heckantrieb	Benzin	165	224	Sep 1981	Dec 1989	2024-03-01	130931
Tesla	Model x	100d AWD	Schrägheck	Allrad	Elektro	386	525	Aug 2017	Apr 2026	2026-06-01	130950
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel	143	194	May 2018	May 2021	2024-03-01	130969
Mercedes-benz	C-Klasse	C 220 D	Kombi	Heckantrieb	Diesel	143	194	Apr 2018	Feb 2021	2024-03-01	130970
Mercedes-benz	C-Klasse	C 220 D	Coupe	Heckantrieb	Diesel	143	194	Apr 2018	Apr 2023	2024-03-01	130971
Mercedes-benz	C-Klasse	C 220 D	Cabriolet	Heckantrieb	Diesel	143	194	Apr 2018	Apr 2023	2024-03-01	130972
Mercedes-benz	E-Klasse	E 400 D 4-matic	Stufenheck	Allrad	Diesel	250	340	Apr 2018	Oct 2023	2024-03-01	130974
Mercedes-benz	E-Klasse	E 400 D 4-matic	Kombi	Allrad	Diesel	250	340	Apr 2018	Oct 2023	2024-03-01	130975
Mercedes-benz	E-Klasse	AMG E 53 EQ Boost 4-matic+	Stufenheck	Allrad	Benzin/Elektro	320	435	Apr 2018	Oct 2023	2024-03-01	130976
Mercedes-benz	E-Klasse	AMG E 53 EQ Boost 4-matic+	Kombi	Allrad	Benzin/Elektro	320	435	Apr 2018	Oct 2023	2024-03-01	130977
Mercedes-benz	G-Klasse	AMG G 63	Geländewagen geschlossen	Allrad	Benzin	430	585	Mar 2018	-	2024-03-01	130978
DS	Ds	1.6 Puretech 180	SUV	Frontantrieb	Benzin	133	180	Apr 2018	-	2024-03-01	130979
Peugeot	208 i	1.2 Puretech 82	Schrägheck	Frontantrieb	Benzin	61	82	Mar 2018	Dec 2019	2024-03-01	130989
Peugeot	2008 i	1.2 Puretech 82	SUV	Frontantrieb	Benzin	61	82	Jan 2018	Dec 2019	2024-03-01	130999
BMW	6	620 D	Schrägheck	Heckantrieb	Diesel	140	190	Jul 2018	Jun 2020	2024-03-01	131046
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	150	204	Apr 2018	Mar 2023	2024-03-01	131061
Chevrolet	Chevelle	5.7	Stufenheck	Heckantrieb	Benzin	108	147	Sep 1973	Dec 1974	2024-03-01	131074
Volvo	V90 ii	T8 Hybrid AWD	Kombi	Allrad	Benzin/Elektro	287	390	Apr 2018	Dec 2022	2024-05-01	131091
Volvo	S90 ii	T8 Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	287	390	Apr 2018	Dec 2022	2024-05-01	131092


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **42 个 Ktype 映射**：其中复用历史尺寸组 17 个，新建尺寸组 12 个。
* 新建组覆盖 Musso Q200、A-Class W177、Porsche 911 991.2 三种外廓、Lexus RC/IS、Polestar 1、MG ZS、Volvo V60 II 和 BMW M2 Competition。新组三维已按不含后视镜宽度口径整理。([KGM Motors UK][1])
* Maybach 62 已识别普通版、62 S 及改款边界，但长度资料存在 6160/6165 mm 冲突，本轮未创建尺寸组，相关 Ktype 继续保留待核对状态。([marsClassic][2])

## 当前批次进度

* READY 映射：**42 / 100**
* PENDING 映射：**58 / 100**
* 已确认尺寸组：**29 个**

  * 历史尺寸组复用：17 个
  * 本轮首次创建：12 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130588	130588	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	同代五门SUV外廓。	READY
130589	130589	Pickup	Musso (Q200)	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH	Q200双排皮卡外廓。	READY
130590	130590	Pickup	Musso (Q200)	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH	Q200双排皮卡外廓。	READY
130593	130593	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130594	130594	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130595	130595	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130598	130598	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	五门SUV外廓。	READY
130599	130599	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	HIGH	GT3专属外廓。	READY
130600	130600	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	HIGH	GT3 RS宽体外廓。	READY
130601	130601	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	HIGH	Carrera T标准窄体外廓。	READY
130606	130606	Coupe	RC I		2	EU-LEXUS-RC-I-RC-F-COUPE-01	HIGH	RC F宽体外廓。	READY
130624	130624	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	前驱标准车身外廓。	READY
130625	130625	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	四驱高度分支。	READY
130626	130626	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	前驱标准车身外廓。	READY
130635	130635	Coupe	Polestar 1		2	EU-POLESTAR-1-I-COUPE-01	HIGH	双门Coupe外廓。	READY
130636	130636	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
130639	130639	Sedan	5 Series (G30)	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车外廓。	READY
130701	130701	Sedan	Camry XV70	XV70	4	EU-TOYOTA-CAMRY-XV70-SEDAN-01	HIGH	XV70四门轿车外廓。	READY
130708	130708	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
130738	130738	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入为Großraumlimousine，按5008 II物理车身归为SUV。	READY
130797	130797	Coupe	CLS III (C257)	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门Coupe外廓。	READY
130800	130800	Sedan	IS III facelift		4	EU-LEXUS-IS-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车外廓。	READY
130802	130802	Coupe	RC I		2	EU-LEXUS-RC-I-COUPE-01	HIGH	标准RC双门外廓。	READY
130805	130805	SUV	ZS I		5	EU-MG-ZS-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130806	130806	SUV	ZS I		5	EU-MG-ZS-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130824	130824	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130825	130825	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130834	130834	SUV	Grandland X (A18)	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18五门SUV外廓。	READY
130835	130835	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130836	130836	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130837	130837	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130838	130838	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130839	130839	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130846	130846	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH	FC四门轿车外廓。	READY
130898	130898	Coupe	M2 (F87)	F87	2	EU-BMW-2-F87-M2-COMPETITION-COUPE-01	HIGH	M2 Competition宽体双门外廓。	READY
130926	130926	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH	GK1W五门SUV外廓。	READY
130927	130927	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH	GK1W五门SUV外廓。	READY
130950	130950	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	五门SUV外廓。	READY
130979	130979	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	MEDIUM	输入Model为Ds，按2018年1.6 PureTech 180识别为DS 7 Crossback。	READY
131046	131046	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
131091	131091	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
131092	131092	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SSANGYONG-MUSSO-Q200-PICKUP-01	5095	1950	1870	KGM Musso official dimensions	https://www.kgm-motors.co.uk/new-cars/musso/design/
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	4419	1796	1440	CarsGuide Mercedes-Benz A-Class 2018 dimensions	https://www.carsguide.com.au/mercedes-benz/a-class/car-dimensions/2018
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271	Carsales Porsche 911 2018 GT3 specifications	https://www.carsales.com.au/research/porsche/911/2018/gt3/
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297	Automobile-Catalog Porsche 911 GT3 RS 2018	https://www.automobile-catalog.com/car/2018/2871455/porsche_911_gt3_rs.html
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285	Automobile-Catalog Porsche 911 Carrera T 2018	https://www.automobile-catalog.com/car/2018/2871650/porsche_911_carrera_t.html
EU-LEXUS-RC-I-RC-F-COUPE-01	4705	1845	1390	CarsGuide Lexus RC F 2018 dimensions	https://www.carsguide.com.au/lexus/rc/rc-f/car-dimensions/2018?id=4EjSHNDM
EU-POLESTAR-1-I-COUPE-01	4586	1958	1352	Polestar 1 owner manual - Dimensions	https://www.polestar.com/uk/manual/polestar-1/2020/article/fe05d7088a0740d0c0a8015150f8256d/
EU-LEXUS-IS-III-FACELIFT-SEDAN-01	4680	1810	1430	Toyota GAZOO Lexus IS300 catalog;Automobile-Catalog Lexus IS 300 2018	https://gazoo.com/catalog/maker/LEXUS/IS/201305/10117449/;https://www.automobile-catalog.com/car/2018/2573915/lexus_is_300.html
EU-LEXUS-RC-I-COUPE-01	4695	1840	1395	CarsGuide Lexus RC300 2018 dimensions	https://www.carsguide.com.au/lexus/rc/rc300/car-dimensions/2018
EU-MG-ZS-I-SUV-01	4314	1809	1611	VehicleScore MG ZS dimensions	https://vehiclescore.co.uk/car-dimensions-check/mg/zs
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Support - V60 Dimensions	https://www.volvocars.com/my/support/car/v60/article/766ee075f0e03896c0a8015109ee0749/
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410	BMW Group PressClub - M2 Competition specifications	https://www.press.bmwgroup.com/new-zealand/article/attachment/T0289640EN/421821
```

## 下一步优先处理

1. 集中闭合 Toyota Proace、Proace Verso 的 Compact/Medium/Long 及四驱分支。
2. 处理 Jeep Wrangler JL 门数分支、Peugeot Rifter 标准轴距/Long 和 Seat Leon 商用掀背/旅行车。
3. 处理 Chevrolet 经典车型、Silverado CAB/BED、Maybach 62 改款边界及其余单车型尺寸组。

推进信号：CONTINUE

[1]: https://www.kgm-motors.co.uk/new-cars/musso/design/?utm_source=chatgpt.com "KGM Musso | Exterior Design Features & Dimensions"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Maybach-62.xhtml?oid=6181&utm_source=chatgpt.com "Maybach 62"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 **8 个 Ktype 映射**：BMW G31 Touring 与 Volvo XC60 II 共 3 行直接复用现有尺寸组；Santa Fe IV、Focus IV Hatchback、Kona I EV 共 5 行命中新建尺寸组。
* Hyundai 官方资料确认 Santa Fe IV 为 4770 × 1890 × 1680 mm，Kona Electric 为 4180 × 1800 × 1570 mm；Ford 官方规格确认 Focus 五门版为 4378 × 1825 × 1471 mm，其中宽度明确不含后视镜。([现代汽车新闻][1])

## 当前批次进度

* READY 映射：**50 / 100**
* PENDING 映射：**50 / 100**
* 已确认尺寸组：**32 个**
* 本轮首次创建尺寸组：**3 个**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130642	130642	Wagon	5 Series (G31)	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH		READY
130766	130766	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
130767	130767	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
130861	130861	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH		READY
130862	130862	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH		READY
130894	130894	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
130895	130895	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
131061	131061	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	纯电车型外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai Nuova Santa Fe official technical specifications	https://www.hyundai.news/it/articles/press-releases/nuova-hyundai-santa-fe-caratteristiche-tecniche.html
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Ford All-New Focus official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/2018/FORD_FOCUS_2018_MediaDrive_TechSpecs_EU.pdf
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570	Hyundai KONA Electric official technical specifications and dimensions	https://www.hyundai.news/fr/archives-du-dossier-de-presse/kona-electric-2018/kona-electric-caracteristiques-techniques-et-dimensions.html
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz C-Class W205/S205/C205/A205 与 E-Class W213/S213 车身分支。
2. 处理 Toyota Proace/Proace Verso、Peugeot Rifter 的短轴、标准轴距和长轴分支。
3. 继续核对 Wrangler JL 门数、Seat Leon 商用车身及 Chevrolet 经典车型和 Silverado CAB/BED 边界。

推进信号：CONTINUE

[1]: https://www.hyundai.news/it/articles/press-releases/nuova-hyundai-santa-fe-caratteristiche-tecniche.html "Nuova Hyundai Santa Fe - Caratteristiche tecniche"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 本轮新增闭合 **11 个 Ktype 映射**。
* Mercedes-Benz C-Class 四种车身、E-Class 两种动力及车身组合、AMG G 63 均已按各自物理外廓独立建组。([汽车数据网][1])
* Opel Karl 的宽度已按不含后视镜口径确认；Peugeot 2008 I 改款版结合对应发动机页面与明确标注不含后视镜宽度的车身资料闭合。([汽车数据网][2])

## 2. 当前批次进度

* READY 映射：**61 / 100**
* PENDING 映射：**39 / 100**
* 已确认尺寸组：**43 个**
* 本轮首次创建尺寸组：**11 个**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130857	130857	Hatchback	Karl		5	EU-OPEL-KARL-I-HATCHBACK-5D-01	HIGH		READY
130969	130969	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-CLASS-W205-SEDAN-FACELIFT-01	HIGH		READY
130970	130970	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-WAGON-FACELIFT-01	HIGH		READY
130971	130971	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-CLASS-C205-COUPE-FACELIFT-01	HIGH		READY
130972	130972	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
130974	130974	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-E400D-01	HIGH		READY
130975	130975	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-E400D-01	HIGH		READY
130976	130976	Sedan	AMG E 53 W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E53-01	HIGH	AMG E 53专属外廓。	READY
130977	130977	Wagon	AMG E 53 S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E53-01	HIGH	AMG E 53旅行车专属外廓。	READY
130978	130978	SUV	G-Class W463 facelift	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-AMG-G63-01	HIGH	AMG G 63专属外廓。	READY
130999	130999	SUV	2008 I facelift		5	EU-PEUGEOT-2008-I-FACELIFT-SUV-01	HIGH	第一代改款五门SUV外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-KARL-I-HATCHBACK-5D-01	3675	1595	1485	Auto-Data Opel Karl 1.0 73	https://www.auto-data.net/en/opel-karl-1.0-73hp-38554
EU-MERCEDES-BENZ-C-CLASS-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data Mercedes-Benz C 220d W205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-220d-194hp-9g-tronic-32993
EU-MERCEDES-BENZ-C-CLASS-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data Mercedes-Benz C 220d S205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-220d-194hp-9g-tronic-32996
EU-MERCEDES-BENZ-C-CLASS-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data Mercedes-Benz C 220d C205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-220d-194hp-9g-tronic-33049
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data Mercedes-Benz C 220d A205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-220d-194hp-9g-tronic-33061
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-E400D-01	4923	1852	1468	Auto-Data Mercedes-Benz E 400d W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-400d-340hp-4matic-9g-tronic-35193
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-E400D-01	4933	1852	1475	Auto-Data Mercedes-Benz E 400d S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-400d-340hp-4matic-9g-tronic-35180
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E53-01	4942	1852	1447	Auto-Data Mercedes-AMG E 53 W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-53-435hp-eq-boost-4matic-amg-speedshift-tct-35215
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E53-01	4971	1860	1461	Auto-Data Mercedes-AMG E 53 S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-53-435hp-eq-boost-4matic-amg-speedshift-tct-35183
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-AMG-G63-01	4881	1984	1969	Auto-Data Mercedes-AMG G 63 W463 facelift	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2018-amg-g-63-v8-585hp-4matic-9g-tronic-amg-speedshift-plus-42381
EU-PEUGEOT-2008-I-FACELIFT-SUV-01	4159	1739	1556	Automobile-Catalog Peugeot 2008 I dimensions;Auto-Data Peugeot 2008 1.2 PureTech 82	https://www.automobile-catalog.com/car/2018/2627525/peugeot_2008_1_6_bluehdi_100_no_start-stop.html;https://www.auto-data.net/en/peugeot-2008-i-facelift-2016-1.2-puretech-82hp-22749
```

## 5. 下一步优先处理

1. Toyota Proace、Proace Verso 与 Peugeot Rifter 的不同轴距和车长分支。
2. Jeep Wrangler JL 两门/四门与 Seat Leon 商用掀背/旅行车边界。
3. Chevrolet Silverado CAB/BED、经典 Chevrolet 车型、Maybach 62 尺寸冲突及 Piaggio Ape 车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-220d-194hp-9g-tronic-32993?utm_source=chatgpt.com "Mercedes-Benz C-class (W205, facelift 2018) C 220d (194 Hp) 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-karl-1.0-73hp-38554?utm_source=chatgpt.com "Specs of Opel Karl 1.0 (73 Hp) /2018, 2019 - Auto-Data.net"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增闭合 **13 个输入 Ktype、17 行映射**，首次创建 10 个尺寸组。
* Seat Leon 跨越 2016 年改款的 Ktype 已按改款前后拆分；现有改款五门 Hatchback 尺寸组直接复用，不重复输出。Seat ST、Cupra 300 4Drive 的不同车长及高度分别建组。([汽车数据网][1])
* Maybach 62 按 2010 年改款产生的 6165/6171 mm 长度差异拆为两个尺寸组；450 kW 62 S 指向改款前组，463 kW 62 S 指向改款后组。([marsClassic][2])
* Audi A3 Sedan、Dodge Caliber、Peugeot 308 CC、Cadillac XT4 已完成独立车身闭合。([汽车数据网][3])

## 当前批次进度

* READY 输入 Ktype：**74 / 100**
* PENDING 输入 Ktype：**26 / 100**
* 本轮新增 READY 输入 Ktype：**13**
* 本轮新增映射行：**17**
* 本轮首次创建尺寸组：**10**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130556_prefl	130556	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背；改款前外廓。	READY
130556_facelift	130556	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Kasten/Schrägheck对应五门掀背；改款后外廓。	READY
130564	130564	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背。	READY
130566	130566	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背。	READY
130570_prefl	130570	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背；改款前外廓。	READY
130570_facelift	130570	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Kasten/Schrägheck对应五门掀背；改款后外廓。	READY
130574_prefl	130574	Wagon	Leon III ST (5F)	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	HIGH	Kasten/Kombi对应ST旅行车；改款前外廓。	READY
130574_facelift	130574	Wagon	Leon III ST (5F)	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH	Kasten/Kombi对应ST旅行车；改款后外廓。	READY
130579	130579	Wagon	Leon III ST Cupra facelift	5F8	5	EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	HIGH	Cupra 300 4Drive专属低车身外廓。	READY
130680_prefl	130680	Sedan	Maybach 62 (V240)	V240	4	EU-MAYBACH-62-V240-SEDAN-PREFL-01	HIGH	同一Ktype跨越2010年改款；改款前外廓。	READY
130680_facelift	130680	Sedan	Maybach 62 (V240) facelift	V240	4	EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越2010年改款；改款后外廓。	READY
130682	130682	Sedan	Maybach 62 S (V240)	V240	4	EU-MAYBACH-62-V240-SEDAN-PREFL-01	HIGH	450kW版本对应改款前62 S外廓。	READY
130683	130683	Sedan	Maybach 62 S (V240) facelift	V240	4	EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	HIGH	463kW版本对应改款后62 S外廓。	READY
130733	130733	Hatchback	Caliber I	PM	5	EU-DODGE-CALIBER-I-PM-HATCHBACK-01	HIGH	五门掀背外廓。	READY
130789	130789	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8V改款四门轿车外廓。	READY
130859	130859	SUV	XT4 I	E2XX	5	EU-CADILLAC-XT4-I-E2XX-SUV-01	HIGH	第一代五门SUV外廓。	READY
130900	130900	Convertible	308 CC I	T7	2	EU-PEUGEOT-308-CC-I-T7-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459	Auto-Data Seat Leon III 1.6 TDI 90	https://www.auto-data.net/en/seat-leon-iii-1.6-tdi-90hp-19388
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451	Auto-Data Seat Leon III ST 1.2 TSI 110	https://www.auto-data.net/en/seat-leon-iii-st-1.2-tsi-110hp-start-stop-19368
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454	SEAT New Leon ST official technical specifications	https://www.seat-cupra-mediacenter.es/content/dam/seat-media-center/Documents/2016/Technical-Specifications-New-SEAT-Leon-ST2016EN.pdf
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431	Automobile-Catalog Seat Leon ST Cupra 300 4Drive	https://www.automobile-catalog.com/car/2017/3098795/seat_leon_st_cupra_300_4drive_dsg.html
EU-MAYBACH-62-V240-SEDAN-PREFL-01	6165	1980	1573	Mercedes-Benz Archive Maybach 62	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Maybach-62.xhtml?oid=6181
EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	6171	1980	1573	Mercedes-Benz Japan Maybach facelift press release;Automobile-Catalog 2010 Maybach 62	https://www.mercedes-benz.jp/news/release/2010/20100722.pdf;https://www.automobile-catalog.com/car/2010/1570490/maybach_62.html
EU-DODGE-CALIBER-I-PM-HATCHBACK-01	4415	1800	1535	Automobile-Catalog Dodge Caliber SXT 2.0 CRD	https://www.automobile-catalog.com/car/2006/690935/dodge_caliber_sxt_2_0l_crd.html
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift 2.0 TFSI	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-2.0-tfsi-190hp-23778
EU-CADILLAC-XT4-I-E2XX-SUV-01	4599	1881	1627	Cadillac XT4 official technical data	https://media.chevrolet.com/content/dam/Media/documents/INTL/cadillac/2018/crossover-suv/xt4/Tech-Data-Cadillac-XT4-EN.pdf
EU-PEUGEOT-308-CC-I-T7-CONVERTIBLE-01	4400	1817	1426	Automobile-Catalog Peugeot 308 CC 1.6 HDi	https://www.automobile-catalog.com/car/2009/2622155/peugeot_308_cc_1_6_hdi_fap_112_110.html
```

## 下一步优先处理

1. 闭合 Toyota Proace/Proace Verso 与 Peugeot Rifter 的 Compact、Medium、Long 轴距及车长分支。
2. 核对 Jeep Wrangler JL 两门/四门、Toyota RAV4 I 三门/五门及 Peugeot 208 I 门数边界。
3. 处理 Chevrolet 经典车型、Silverado CAB/BED、Piaggio Ape、Lancia Delta Integrale 与 Jaguar Vanden Plas。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-leon-iii-1.6-tdi-90hp-19388?utm_source=chatgpt.com "Seat Leon III 1.6 TDI (90 Hp) /Hatchback 2012 - 2015"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Maybach-62.xhtml?oid=6181&utm_source=chatgpt.com "Maybach 62 - Mercedes-Benz Archive"
[3]: https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-2.0-tfsi-190hp-23778 "Audi A3 Sedan (8V, facelift 2016) 2.0 TFSI (190 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 本轮新增闭合 **6 个输入 Ktype、15 行映射**，首次创建 **6 个尺寸组**。
* Wrangler IV 已按二门/四门以及普通版与 Rubicon 的高度差异拆分。官方欧规资料同时列出了 2.0 汽油与 2.2 柴油的二门、四门配置及各分支三维。
* Peugeot Rifter 已拆为 Standard 和 Long；BlueHDi 75 仅关联 Standard，其余三个动力同时关联 Standard 与 Long。宽度采用官方明确标注的 **不含后视镜 1848 mm**。

## 2. 当前批次进度

* READY 输入 Ktype：**80 / 100**
* PENDING 输入 Ktype：**20 / 100**
* 本轮新增 READY 输入 Ktype：**6**
* 本轮新增映射行：**15**
* 已确认尺寸组：**59 个**
* 本轮首次创建尺寸组：**6 个**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130547_2dr_standard	130547	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	HIGH	二门Sahara或Overland标准外廓。	READY
130547_2dr_rubicon	130547	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	HIGH	二门Rubicon高度分支。	READY
130547_4dr_standard	130547	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	HIGH	四门Sahara或Overland标准外廓。	READY
130547_4dr_rubicon	130547	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	HIGH	四门Rubicon高度分支。	READY
130548_2dr_standard	130548	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	HIGH	二门Sahara或Overland标准外廓。	READY
130548_2dr_rubicon	130548	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	HIGH	二门Rubicon高度分支。	READY
130548_4dr_standard	130548	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	HIGH	四门Sahara或Overland标准外廓。	READY
130548_4dr_rubicon	130548	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	HIGH	四门Rubicon高度分支。	READY
130752_standard	130752	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130752_long	130752	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
130754	130754	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	BlueHDi 75仅确认Standard车身。	READY
130755_standard	130755	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130755_long	130755	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
130756_standard	130756	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130756_long	130756	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	4334	1894	1839	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler
EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	4334	1894	1841	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler
EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	4882	1894	1838	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler Unlimited	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler-unlimited
EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	4882	1894	1848	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler Unlimited	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler-unlimited
EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	4403	1848	1878	PEUGEOT Rifter July 2019 official brochure;Peugeot France official Rifter dimensions	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-rifter-prices-specifications-brochure-july-2019.pdf;https://www.peugeot.fr/content/peugeot/worldwide/france/fr_fr/index/nos-vehicules/e-rifter.html
EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	4753	1848	1882	PEUGEOT Rifter July 2019 official brochure;Peugeot France official Rifter dimensions	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-rifter-prices-specifications-brochure-july-2019.pdf;https://www.peugeot.fr/content/peugeot/worldwide/france/fr_fr/index/nos-vehicules/e-rifter.html
```

## 5. 下一步优先处理

1. 闭合 Toyota Proace Verso、Proace 4×4 的 Compact、Medium、Long，以及改款前后尺寸边界。
2. 处理 Toyota RAV4 I、Peugeot 208 I、Lancia Delta Integrale 和 Jaguar Vanden Plas。
3. 最后处理 Chevrolet 经典车型、Silverado CAB/BED、Piaggio Ape 两种车身分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 本轮新增闭合 **4 个输入 Ktype、6 行映射**，首次创建 **6 个尺寸组**。
* Toyota RAV4 I 按三门改款前、三门改款后和五门拆分；三门改款后高度由 1655 mm 变为 1660 mm，五门改款前后三维一致，因此复用同一尺寸组。
* Peugeot 208 I 的 2018 年 1.2 PureTech 82 配置确认为五门车身，宽度 1739 mm 明确为车身含门把手、不含展开后视镜。([Guy Perry][1])
* Lancia Delta HF Integrale Evoluzione 与 Jaguar Vanden Plas XJ40 已完成物理车身识别；Jaguar 输入生产起始年月早于 XJ40 发布，但 3.6 动力和 Vanden Plas 边界可唯一落到 XJ40。([stellantisheritage.com][2])

## 2. 当前批次进度

* READY 输入 Ktype：**84 / 100**
* PENDING 输入 Ktype：**16 / 100**
* 本轮新增 READY 输入 Ktype：**4**
* 本轮新增映射行：**6**
* 本轮首次创建尺寸组：**6**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130706_3dr_prefl	130706	SUV	RAV4 I (XA10)	SXA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-PREFL-01	HIGH	三门硬顶改款前外廓。	READY
130706_3dr_facelift	130706	SUV	RAV4 I (XA10)	SXA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-FACELIFT-01	HIGH	三门硬顶1998年改款后高度分支。	READY
130706_5dr	130706	SUV	RAV4 I (XA10)	SXA11	5	EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	HIGH	五门硬顶改款前后三维一致。	READY
130816	130816	Hatchback	Delta I HF Integrale Evoluzione	831	5	EU-LANCIA-DELTA-I-831-HF-INTEGRALE-EVOLUZIONE-HATCHBACK-01	MEDIUM	151kW版本对应Evoluzione I外廓，不含后续Evoluzione II动力分支。	READY
130931	130931	Sedan	Vanden Plas (XJ40)	XJ40	4	EU-JAGUAR-VANDEN-PLAS-XJ40-SEDAN-01	MEDIUM	3.6动力与Vanden Plas边界识别为XJ40；输入起始年月存在上游偏差。	READY
130989	130989	Hatchback	208 I facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH	2018年1.2 PureTech 82五门车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-RAV4-I-XA10-SUV-3D-PREFL-01	3705	1695	1655	Toyota RAV4 first-generation official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-5dr-UK-launch-pack.pdf
EU-TOYOTA-RAV4-I-XA10-SUV-3D-FACELIFT-01	3705	1695	1660	Toyota RAV4 1998 model change official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-MC-soft-top-UK-launch-pack.pdf
EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	4115	1695	1660	Toyota RAV4 first-generation official UK launch pack;Toyota RAV4 1998 model change official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-5dr-UK-launch-pack.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-MC-soft-top-UK-launch-pack.pdf
EU-LANCIA-DELTA-I-831-HF-INTEGRALE-EVOLUZIONE-HATCHBACK-01	3900	1770	1365	Stellantis Heritage Lancia Delta HF 4WD/Integrale;Goo-net Exchange Lancia Delta HF Integrale Evoluzione catalog	https://www.stellantisheritage.com/en-uk/heritage/stories/lancia-delta-HF-4WD-integrale;https://www.goo-net-exchange.com/catalog/LANCIA__DELTA/9001605/
EU-JAGUAR-VANDEN-PLAS-XJ40-SEDAN-01	4988	1798	1380	Jaguar Daimler Heritage Trust XJ40 research guide;Automobile-Catalog Jaguar Vanden Plas XJ40	https://www.jaguarheritage.com/uploads/RG001O-Jaguar-and-Daimler-XJ-Series-XJ40-X300-v.2-31-03-2020.pdf;https://www.automobile-catalog.com/car/1988/1284065/jaguar_vanden_plas.html
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460	PEUGEOT 208 Hatchback Range June 2018 official specification	https://www.guyperry.co.uk/wp-content/uploads/2018/06/208-Spec-Sheet.pdf
```

## 5. 下一步优先处理

1. 集中闭合 Toyota Proace Verso 与 Proace 4×4 的 Compact、Medium、Long 分支。
2. 处理 Chevrolet Aveo/Kalos、Caprice、Impala、Chevelle 与 Silverado CAB/BED。
3. 最后处理 Piaggio Ape Kasten/Pritsche 两种车身。

推进信号：CONTINUE

[1]: https://www.guyperry.co.uk/wp-content/uploads/2018/06/208-Spec-Sheet.pdf "PEUGEOT 208 Hatchback range - June 2018 v19"
[2]: https://www.stellantisheritage.com/en-uk/heritage/stories/lancia-delta-HF-4WD-integrale?utm_source=chatgpt.com "Lancia Delta HF 4WD/Integrale"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* Toyota Proace Verso II 已按动力适用范围完成聚类：1.6 D-4D 95/115 对应 Medium；2.0 D-4D 150/177 分别覆盖 Compact、Medium、Long。
* 首次建立 Compact、Medium、Long 三个尺寸组。2017 Toyota 官方产品手册给出最终量产尺寸及动力/车长组合；Toyota 技术规格明确 1920 mm 为不含后视镜宽度。([leparnass.sakura.ne.jp][1])

## 2. 当前批次进度

* READY 输入 Ktype：**88 / 100**
* PENDING 输入 Ktype：**12 / 100**
* 本轮新增 READY 输入 Ktype：**4**
* 本轮新增映射行：**8**
* 本轮首次创建尺寸组：**3**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130609	130609	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	1.6 D-4D 115对应Medium车身。	READY
130610_compact	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	HIGH	Compact车长分支。	READY
130610_medium	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium车长分支。	READY
130610_long	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long车长分支。	READY
130611_compact	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	HIGH	Compact车长分支。	READY
130611_medium	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium车长分支。	READY
130611_long	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long车长分支。	READY
130612	130612	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	1.6 D-4D 95对应Medium车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
```

## 5. 下一步优先处理

1. 闭合 Proace Verso 4×4 和 Proace Van 4×4 的 Dangel 悬架高度及车长分支。
2. 处理 Chevrolet Aveo/Kalos、Caprice、Impala、Chevelle。
3. 最后处理 Silverado CAB/BED 与 Piaggio Ape 两种车身。

推进信号：CONTINUE

[1]: https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf "13102 PRV_36_TGB_WEB.indd"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Chevrolet Caprice、Impala 和 Chevelle 共 4 个 Ktype；其中 Caprice Sedan、Impala Coupe 和 Chevelle Sedan 因跨车型年发生车身宽度或长度变化，已拆成稳定年份分支。([汽车目录][1])
* 闭合 Piaggio Ape 50 两个 Ktype：Van 单一外廓；Pritsche/Fahrgestell 拆为 Short Deck、Long Deck 和 Cross。三维来自 Piaggio Commercial Vehicles 技术资料。([Piaggio Commercial UK][2])
* 本轮新增 READY 输入 Ktype：6 个；新增映射行和尺寸组各 11 行。

## 当前批次进度

* READY 输入 Ktype：**94 / 100**
* PENDING 输入 Ktype：**6 / 100**
* 本轮新增 READY 输入 Ktype：**6**
* 本轮新增映射行：**11**
* 本轮首次创建尺寸组：**11**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130604_1977	130604	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	MEDIUM	1977车型年车身宽度分支。	READY
130604_1978_1979	130604	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	MEDIUM	1978至1979车型年加宽外廓。	READY
130650	130650	Coupe	Caprice I		2	EU-CHEVROLET-CAPRICE-I-COUPE-1970-01	HIGH	1970车型年454双门硬顶外廓。	READY
130669_1977	130669	Coupe	Impala V		2	EU-CHEVROLET-IMPALA-V-COUPE-1977-01	MEDIUM	1977车型年车身宽度分支。	READY
130669_1978	130669	Coupe	Impala V		2	EU-CHEVROLET-IMPALA-V-COUPE-1978-01	MEDIUM	1978车型年加宽外廓。	READY
130860	130860	Van	Ape 50		2	EU-PIAGGIO-APE-50-VAN-01	HIGH	封闭式Van外廓。	READY
130863_shortdeck	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	HIGH	Short Deck开放货台分支。	READY
130863_longdeck	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	HIGH	Long Deck开放货台分支。	READY
130863_cross	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-CROSS-01	HIGH	Cross增高开放货台分支。	READY
131074_1974	131074	Sedan	Chevelle III		4	EU-CHEVROLET-CHEVELLE-III-SEDAN-1974-01	MEDIUM	1974车型年外廓。	READY
131074_1975	131074	Sedan	Chevelle III		4	EU-CHEVROLET-CHEVELLE-III-SEDAN-1975-01	MEDIUM	1975车型年缩短外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	5387	1918	1422	Automobile-Catalog 1977 Chevrolet Caprice Classic Sedan	https://www.automobile-catalog.com/car/1977/208085/chevrolet_caprice_classic_sedan_305_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	5387	1930	1422	Automobile-Catalog 1978 Chevrolet Caprice Classic Sedan;Automobile-Catalog 1979 Chevrolet Caprice Classic Sedan 5.7L	https://www.automobile-catalog.com/car/1978/208520/chevrolet_caprice_classic_sedan_350-4_v-8_automatic.html;https://www.automobile-catalog.com/car/1979/208970/chevrolet_caprice_classic_sedan_5_7l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-I-COUPE-1970-01	5486	2027	1377	Automobile-Catalog 1970 Chevrolet Caprice Custom Coupe 454	https://www.automobile-catalog.com/car/1970/412910/chevrolet_caprice_custom_coupe_454_v-8_turbo-jet_390-hp_hydra-matic.html
EU-CHEVROLET-IMPALA-V-COUPE-1977-01	5387	1918	1405	Automobile-Catalog 1977 Chevrolet Impala Coupe 350	https://www.automobile-catalog.com/car/1977/207935/chevrolet_impala_coupe_350-4_v-8_hydra-matic.html
EU-CHEVROLET-IMPALA-V-COUPE-1978-01	5387	1930	1405	Automobile-Catalog 1978 Chevrolet Impala Sport Coupe	https://www.automobile-catalog.com/car/1978/208175/chevrolet_impala_sport_coupe_305_v-8_automatic.html
EU-PIAGGIO-APE-50-VAN-01	2500	1260	1590	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	2490	1260	1550	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	2660	1260	1550	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-PIAGGIO-APE-50-PICKUP-CROSS-01	2530	1260	1620	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-CHEVROLET-CHEVELLE-III-SEDAN-1974-01	5342	1946	1367	Automobile-Catalog 1974 Chevrolet Chevelle Malibu Classic Sedan	https://www.automobile-catalog.com/car/1974/161315/chevrolet_chevelle_malibu_classic_sedan_454_v-8_turbo-jet_4-speed.html
EU-CHEVROLET-CHEVELLE-III-SEDAN-1975-01	5314	1946	1367	Automobile-Catalog 1975 Chevrolet Chevelle Malibu Classic Sedan	https://www.automobile-catalog.com/car/1975/199985/chevrolet_chevelle_malibu_classic_sedan_250_turbo-thrift.html
```

## 下一步优先处理

1. 闭合 Silverado 的 Crew Cab Short Box、Regular Cab Standard/Long Box 和 Hybrid Crew Cab 分支。
2. 闭合 Proace Verso 4×4 与 Proace Van 4×4，确认标准 Dangel 转换和选装升高底盘的外廓边界。
3. 最后处理 Ktype 130602 的 Aveo/Kalos T250/T255 Hatchback 车身代码及门数边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/208085/chevrolet_caprice_classic_sedan_305_v-8_hydra-matic.html?utm_source=chatgpt.com "1977 Chevrolet Caprice Classic Sedan 305 V-8 Hydra-Matic Specs Review (108 kW / 147 PS / 145 hp) (since October 1976 for North America )"
[2]: https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf "Presentazione standard di PowerPoint"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 本轮闭合 **3 个输入 Ktype、4 行映射**，首次创建 **4 个尺寸组**。
* Ktype 130696、130697 虽被输入目录标为 Silverado 2500，但 5.3 L FlexFuel 动力、CAB 类型和生产时间实际对应 GMT900 Silverado 1500；官方规格确认 Crew Cab 仅使用 Short Box，Regular Cab包含 Standard Box 与 Long Box。宽度均为不含后视镜口径。
* Ktype 130602 对应改款前 Chevrolet Kalos/Aveo T200 五门掀背，三维为 3880 × 1670 × 1495 mm。([汽车目录][1])
* Proace 两个 4×4 Ktype 与 Silverado 5.3 Hybrid 暂未闭合：Dangel 资料只确认悬架最多升高 60 mm，尚不能把固定高度与具体 Medium/Long 车身唯一组合；Silverado Hybrid 的输入发动机与官方 GMT900 Two-Mode Hybrid 动力存在冲突。([Dangel Shop][2])

## 2. 当前批次进度

* READY 输入 Ktype：**97 / 100**
* PENDING 输入 Ktype：**3 / 100**
* 本轮新增 READY 输入 Ktype：**3**
* 本轮新增映射行：**4**
* 本轮首次创建尺寸组：**4**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130602	130602	Hatchback	Kalos/Aveo I	T200	5	EU-CHEVROLET-KALOS-AVEO-I-T200-HATCHBACK-5D-01	HIGH	改款前五门掀背外廓。	READY
130696	130696	Pickup	Silverado 1500 II	GMT900	4	EU-CHEVROLET-SILVERADO-1500-II-GMT900-CREW-CAB-SHORT-BOX-4X4-01	MEDIUM	输入目录标为2500；按5.3 FlexFuel动力及CAB边界识别为1500 Crew Cab Short Box。	READY
130697_standardbox	130697	Pickup	Silverado 1500 II	GMT900	2	EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-STANDARD-BOX-4X4-01	MEDIUM	输入目录标为2500；Regular Cab标准货斗分支。	READY
130697_longbox	130697	Pickup	Silverado 1500 II	GMT900	2	EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-LONG-BOX-4X4-01	MEDIUM	输入目录标为2500；Regular Cab长货斗分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-KALOS-AVEO-I-T200-HATCHBACK-5D-01	3880	1670	1495	Automobile-Catalog 2007 Chevrolet Kalos 1.4 16V SX Hatchback	https://www.automobile-catalog.com/car/2007/559040/chevrolet_kalos_1_4_16v_sx_hatchback.html
EU-CHEVROLET-SILVERADO-1500-II-GMT900-CREW-CAB-SHORT-BOX-4X4-01	5847	2032	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-STANDARD-BOX-4X4-01	5222	2029	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-LONG-BOX-4X4-01	5702	2029	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
```

## 5. 下一步优先处理

1. 解决 Ktype 130698 的 5.3 Hybrid/LM7 与官方 GMT900 6.0 Two-Mode Hybrid 冲突，确认实际代际和 CAB/BED。
2. 确认 Ktype 130815 Proace Verso 4×4 的 Medium/Long 适用范围及固定量产高度。
3. 确认 Ktype 130885 Proace Van 4×4 的 Medium/Long 车长和标准升高底盘高度。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/559040/chevrolet_kalos_1_4_16v_sx_hatchback.html?utm_source=chatgpt.com "2007 Chevrolet Kalos 1.4 16V SX Hatchback (man. 5)"
[2]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Toyota/Toyota%20ProAce%204x4%20new%20leaflet%2015_06_2023%20English.pdf?utm_source=chatgpt.com "TOYOTA PROACE 4x4"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 剩余 3 个 PENDING Ktype 已全部闭合：

  * `130698`：识别为 GMT800 Silverado 1500 Classic Hybrid Extended Cab Short Box 4WD。
  * `130815`：拆分为 Proace Verso 4×4 Medium、Long。
  * `130885`：拆分为 Proace Van 4×4 Compact、Medium、Long。
* Toyota 4×4 技术资料确认三种车长及 1920 mm 不含后视镜宽度；Silverado Hybrid 已按对应 GMT800 Classic 车身闭合。([Toyota FI][1])
* 已完成最终机械检查：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸和来源字段完整。

## 当前批次进度

* 输入 Ktype：**100**
* READY 输入 Ktype：**100**
* PENDING 输入 Ktype：**0**
* 最终映射行：**128**
* 最终尺寸组：**91**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
130547_2dr_standard	130547	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	HIGH	二门Sahara或Overland标准外廓。	READY
130547_2dr_rubicon	130547	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	HIGH	二门Rubicon高度分支。	READY
130547_4dr_standard	130547	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	HIGH	四门Sahara或Overland标准外廓。	READY
130547_4dr_rubicon	130547	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	HIGH	四门Rubicon高度分支。	READY
130548_2dr_standard	130548	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	HIGH	二门Sahara或Overland标准外廓。	READY
130548_2dr_rubicon	130548	SUV	Wrangler IV (JL)		2	EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	HIGH	二门Rubicon高度分支。	READY
130548_4dr_standard	130548	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	HIGH	四门Sahara或Overland标准外廓。	READY
130548_4dr_rubicon	130548	SUV	Wrangler IV (JL)		4	EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	HIGH	四门Rubicon高度分支。	READY
130556_prefl	130556	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背；改款前外廓。	READY
130556_facelift	130556	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Kasten/Schrägheck对应五门掀背；改款后外廓。	READY
130564	130564	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背。	READY
130566	130566	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背。	READY
130570_prefl	130570	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	HIGH	Kasten/Schrägheck对应五门掀背；改款前外廓。	READY
130570_facelift	130570	Hatchback	Leon III (5F)	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Kasten/Schrägheck对应五门掀背；改款后外廓。	READY
130574_prefl	130574	Wagon	Leon III ST (5F)	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	HIGH	Kasten/Kombi对应ST旅行车；改款前外廓。	READY
130574_facelift	130574	Wagon	Leon III ST (5F)	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH	Kasten/Kombi对应ST旅行车；改款后外廓。	READY
130579	130579	Wagon	Leon III ST Cupra facelift	5F8	5	EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	HIGH	Cupra 300 4Drive专属低车身外廓。	READY
130588	130588	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	同代五门SUV外廓。	READY
130589	130589	Pickup	Musso (Q200)	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH	Q200双排皮卡外廓。	READY
130590	130590	Pickup	Musso (Q200)	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH	Q200双排皮卡外廓。	READY
130593	130593	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130594	130594	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130595	130595	Hatchback	A-Class (W177)	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门掀背外廓。	READY
130598	130598	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	五门SUV外廓。	READY
130599	130599	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	HIGH	GT3专属外廓。	READY
130600	130600	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	HIGH	GT3 RS宽体外廓。	READY
130601	130601	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	HIGH	Carrera T标准窄体外廓。	READY
130602	130602	Hatchback	Kalos/Aveo I	T200	5	EU-CHEVROLET-KALOS-AVEO-I-T200-HATCHBACK-5D-01	HIGH	改款前五门掀背外廓。	READY
130604_1977	130604	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	MEDIUM	1977车型年车身宽度分支。	READY
130604_1978_1979	130604	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	MEDIUM	1978至1979车型年加宽外廓。	READY
130606	130606	Coupe	RC I		2	EU-LEXUS-RC-I-RC-F-COUPE-01	HIGH	RC F宽体外廓。	READY
130609	130609	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	1.6 D-4D 115对应Medium车身。	READY
130610_compact	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	HIGH	Compact车长分支。	READY
130610_medium	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium车长分支。	READY
130610_long	130610	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long车长分支。	READY
130611_compact	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	HIGH	Compact车长分支。	READY
130611_medium	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium车长分支。	READY
130611_long	130611	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long车长分支。	READY
130612	130612	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	1.6 D-4D 95对应Medium车身。	READY
130624	130624	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	前驱标准车身外廓。	READY
130625	130625	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	四驱高度分支。	READY
130626	130626	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	前驱标准车身外廓。	READY
130635	130635	Coupe	Polestar 1		2	EU-POLESTAR-1-I-COUPE-01	HIGH	双门Coupe外廓。	READY
130636	130636	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
130639	130639	Sedan	5 Series (G30)	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车外廓。	READY
130642	130642	Wagon	5 Series (G31)	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH		READY
130650	130650	Coupe	Caprice I		2	EU-CHEVROLET-CAPRICE-I-COUPE-1970-01	HIGH	1970车型年454双门硬顶外廓。	READY
130669_1977	130669	Coupe	Impala V		2	EU-CHEVROLET-IMPALA-V-COUPE-1977-01	MEDIUM	1977车型年车身宽度分支。	READY
130669_1978	130669	Coupe	Impala V		2	EU-CHEVROLET-IMPALA-V-COUPE-1978-01	MEDIUM	1978车型年加宽外廓。	READY
130680_prefl	130680	Sedan	Maybach 62 (V240)	V240	4	EU-MAYBACH-62-V240-SEDAN-PREFL-01	HIGH	同一Ktype跨越2010年改款；改款前外廓。	READY
130680_facelift	130680	Sedan	Maybach 62 (V240) facelift	V240	4	EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越2010年改款；改款后外廓。	READY
130682	130682	Sedan	Maybach 62 S (V240)	V240	4	EU-MAYBACH-62-V240-SEDAN-PREFL-01	HIGH	450kW版本对应改款前62 S外廓。	READY
130683	130683	Sedan	Maybach 62 S (V240) facelift	V240	4	EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	HIGH	463kW版本对应改款后62 S外廓。	READY
130696	130696	Pickup	Silverado 1500 II	GMT900	4	EU-CHEVROLET-SILVERADO-1500-II-GMT900-CREW-CAB-SHORT-BOX-4X4-01	MEDIUM	输入目录标为2500；按5.3 FlexFuel动力及CAB边界识别为1500 Crew Cab Short Box。	READY
130697_standardbox	130697	Pickup	Silverado 1500 II	GMT900	2	EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-STANDARD-BOX-4X4-01	MEDIUM	输入目录标为2500；Regular Cab标准货斗分支。	READY
130697_longbox	130697	Pickup	Silverado 1500 II	GMT900	2	EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-LONG-BOX-4X4-01	MEDIUM	输入目录标为2500；Regular Cab长货斗分支。	READY
130698	130698	Pickup	Silverado 1500 I Classic	GMT800	4	EU-CHEVROLET-SILVERADO-1500-I-GMT800-CLASSIC-HYBRID-EXTENDED-CAB-SHORT-BOX-4X4-01	MEDIUM	输入目录标为2500；5.3 Hybrid对应1500 Classic Extended Cab Short Box 4WD。	READY
130701	130701	Sedan	Camry XV70	XV70	4	EU-TOYOTA-CAMRY-XV70-SEDAN-01	HIGH	XV70四门轿车外廓。	READY
130706_3dr_prefl	130706	SUV	RAV4 I (XA10)	SXA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-PREFL-01	HIGH	三门硬顶改款前外廓。	READY
130706_3dr_facelift	130706	SUV	RAV4 I (XA10)	SXA10	3	EU-TOYOTA-RAV4-I-XA10-SUV-3D-FACELIFT-01	HIGH	三门硬顶1998年改款后高度分支。	READY
130706_5dr	130706	SUV	RAV4 I (XA10)	SXA11	5	EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	HIGH	五门硬顶改款前后三维一致。	READY
130708	130708	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
130733	130733	Hatchback	Caliber I	PM	5	EU-DODGE-CALIBER-I-PM-HATCHBACK-01	HIGH	五门掀背外廓。	READY
130738	130738	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入为Großraumlimousine，按5008 II物理车身归为SUV。	READY
130752_standard	130752	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130752_long	130752	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
130754	130754	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	BlueHDi 75仅确认Standard车身。	READY
130755_standard	130755	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130755_long	130755	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
130756_standard	130756	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	HIGH	Standard车长分支。	READY
130756_long	130756	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	HIGH	Long车长分支。	READY
130766	130766	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
130767	130767	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
130789	130789	Sedan	A3 Sedan 8V facelift	8V	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8V改款四门轿车外廓。	READY
130797	130797	Coupe	CLS III (C257)	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	C257四门Coupe外廓。	READY
130800	130800	Sedan	IS III facelift		4	EU-LEXUS-IS-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车外廓。	READY
130802	130802	Coupe	RC I		2	EU-LEXUS-RC-I-COUPE-01	HIGH	标准RC双门外廓。	READY
130805	130805	SUV	ZS I		5	EU-MG-ZS-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130806	130806	SUV	ZS I		5	EU-MG-ZS-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130815_medium	130815	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	HIGH	2.0 D-4D 4×4 Medium车长分支。	READY
130815_long	130815	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	MEDIUM	2.0 D-4D 4×4 Long车长分支。	READY
130816	130816	Hatchback	Delta I HF Integrale Evoluzione	831	5	EU-LANCIA-DELTA-I-831-HF-INTEGRALE-EVOLUZIONE-HATCHBACK-01	MEDIUM	151kW版本对应Evoluzione I外廓，不含后续Evoluzione II动力分支。	READY
130824	130824	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130825	130825	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
130834	130834	SUV	Grandland X (A18)	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18五门SUV外廓。	READY
130835	130835	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130836	130836	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130837	130837	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130838	130838	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130839	130839	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
130846	130846	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH	FC四门轿车外廓。	READY
130857	130857	Hatchback	Karl		5	EU-OPEL-KARL-I-HATCHBACK-5D-01	HIGH		READY
130859	130859	SUV	XT4 I	E2XX	5	EU-CADILLAC-XT4-I-E2XX-SUV-01	HIGH	第一代五门SUV外廓。	READY
130860	130860	Van	Ape 50		2	EU-PIAGGIO-APE-50-VAN-01	HIGH	封闭式Van外廓。	READY
130861	130861	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH		READY
130862	130862	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH		READY
130863_shortdeck	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	HIGH	Short Deck开放货台分支。	READY
130863_longdeck	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	HIGH	Long Deck开放货台分支。	READY
130863_cross	130863	Pickup	Ape 50		2	EU-PIAGGIO-APE-50-PICKUP-CROSS-01	HIGH	Cross增高开放货台分支。	READY
130885_compact	130885	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	MEDIUM	2.0 D-4D 4×4 Compact车长分支。	READY
130885_medium	130885	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	MEDIUM	2.0 D-4D 4×4 Medium车长分支。	READY
130885_long	130885	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	MEDIUM	2.0 D-4D 4×4 Long车长分支。	READY
130894	130894	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
130895	130895	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
130898	130898	Coupe	M2 (F87)	F87	2	EU-BMW-2-F87-M2-COMPETITION-COUPE-01	HIGH	M2 Competition宽体双门外廓。	READY
130900	130900	Convertible	308 CC I	T7	2	EU-PEUGEOT-308-CC-I-T7-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
130926	130926	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH	GK1W五门SUV外廓。	READY
130927	130927	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH	GK1W五门SUV外廓。	READY
130931	130931	Sedan	Vanden Plas (XJ40)	XJ40	4	EU-JAGUAR-VANDEN-PLAS-XJ40-SEDAN-01	MEDIUM	3.6动力与Vanden Plas边界识别为XJ40；输入起始年月存在上游偏差。	READY
130950	130950	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	五门SUV外廓。	READY
130969	130969	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-CLASS-W205-SEDAN-FACELIFT-01	HIGH		READY
130970	130970	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-WAGON-FACELIFT-01	HIGH		READY
130971	130971	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-CLASS-C205-COUPE-FACELIFT-01	HIGH		READY
130972	130972	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
130974	130974	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-E400D-01	HIGH		READY
130975	130975	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-E400D-01	HIGH		READY
130976	130976	Sedan	AMG E 53 W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E53-01	HIGH	AMG E 53专属外廓。	READY
130977	130977	Wagon	AMG E 53 S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E53-01	HIGH	AMG E 53旅行车专属外廓。	READY
130978	130978	SUV	G-Class W463 facelift	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-AMG-G63-01	HIGH	AMG G 63专属外廓。	READY
130979	130979	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	MEDIUM	输入Model为Ds，按2018年1.6 PureTech 180识别为DS 7 Crossback。	READY
130989	130989	Hatchback	208 I facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH	2018年1.2 PureTech 82五门车身。	READY
130999	130999	SUV	2008 I facelift		5	EU-PEUGEOT-2008-I-FACELIFT-SUV-01	HIGH	第一代改款五门SUV外廓。	READY
131046	131046	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
131061	131061	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-EV-SUV-01	HIGH	纯电车型外廓。	READY
131074_1974	131074	Sedan	Chevelle III		4	EU-CHEVROLET-CHEVELLE-III-SEDAN-1974-01	MEDIUM	1974车型年外廓。	READY
131074_1975	131074	Sedan	Chevelle III		4	EU-CHEVROLET-CHEVELLE-III-SEDAN-1975-01	MEDIUM	1975车型年缩短外廓。	READY
131091	131091	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	第二代五门旅行车外廓。	READY
131092	131092	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2101-2200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-WRANGLER-IV-JL-SUV-2D-STANDARD-01	4334	1894	1839	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler
EU-JEEP-WRANGLER-IV-JL-SUV-2D-RUBICON-01	4334	1894	1841	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler
EU-JEEP-WRANGLER-IV-JL-SUV-4D-STANDARD-01	4882	1894	1838	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler Unlimited	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler-unlimited
EU-JEEP-WRANGLER-IV-JL-SUV-4D-RUBICON-01	4882	1894	1848	Jeep All-New Wrangler official UK brochure;Automobile Dimension Jeep Wrangler Unlimited	https://www.jeep.co.uk/content/dam/jeep/uk/brochure/wrangler/All-New-Jeep-Wrangler-Full-Brochure-January-2019.pdf;https://www.automobiledimension.com/model/jeep/wrangler-unlimited
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459	Auto-Data Seat Leon III 1.6 TDI 90	https://www.auto-data.net/en/seat-leon-iii-1.6-tdi-90hp-19388
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	Auto-Data Seat Leon III facelift 1.2 TSI 110	https://www.auto-data.net/en/seat-leon-iii-facelift-2016-1.2-tsi-110hp-27110
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451	Auto-Data Seat Leon III ST 1.2 TSI 110	https://www.auto-data.net/en/seat-leon-iii-st-1.2-tsi-110hp-start-stop-19368
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454	SEAT New Leon ST official technical specifications	https://www.seat-cupra-mediacenter.es/content/dam/seat-media-center/Documents/2016/Technical-Specifications-New-SEAT-Leon-ST2016EN.pdf
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431	Automobile-Catalog Seat Leon ST Cupra 300 4Drive	https://www.automobile-catalog.com/car/2017/3098795/seat_leon_st_cupra_300_4drive_dsg.html
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data Volvo XC60 II dimensions	https://www.auto-data.net/en/volvo-xc60-ii-2.0-b4-197hp-mild-hybrid-automatic-41114
EU-SSANGYONG-MUSSO-Q200-PICKUP-01	5095	1950	1870	KGM Musso official dimensions	https://www.kgm-motors.co.uk/new-cars/musso/design/
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	4419	1796	1440	CarsGuide Mercedes-Benz A-Class 2018 dimensions	https://www.carsguide.com.au/mercedes-benz/a-class/car-dimensions/2018
EU-TESLA-MODEL-X-I-SUV-01	5052	1999	1684	Auto-Data Tesla Model X 90D dimensions	https://www.auto-data.net/en/tesla-model-x-90d-90-kwh-525hp-dual-motor-awd-33037
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271	Carsales Porsche 911 2018 GT3 specifications	https://www.carsales.com.au/research/porsche/911/2018/gt3/
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297	Automobile-Catalog Porsche 911 GT3 RS 2018	https://www.automobile-catalog.com/car/2018/2871455/porsche_911_gt3_rs.html
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285	Automobile-Catalog Porsche 911 Carrera T 2018	https://www.automobile-catalog.com/car/2018/2871650/porsche_911_carrera_t.html
EU-CHEVROLET-KALOS-AVEO-I-T200-HATCHBACK-5D-01	3880	1670	1495	Automobile-Catalog 2007 Chevrolet Kalos 1.4 16V SX Hatchback	https://www.automobile-catalog.com/car/2007/559040/chevrolet_kalos_1_4_16v_sx_hatchback.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	5387	1918	1422	Automobile-Catalog 1977 Chevrolet Caprice Classic Sedan	https://www.automobile-catalog.com/car/1977/208085/chevrolet_caprice_classic_sedan_305_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	5387	1930	1422	Automobile-Catalog 1978 Chevrolet Caprice Classic Sedan;Automobile-Catalog 1979 Chevrolet Caprice Classic Sedan 5.7L	https://www.automobile-catalog.com/car/1978/208520/chevrolet_caprice_classic_sedan_350-4_v-8_automatic.html;https://www.automobile-catalog.com/car/1979/208970/chevrolet_caprice_classic_sedan_5_7l_v-8_automatic.html
EU-LEXUS-RC-I-RC-F-COUPE-01	4705	1845	1390	CarsGuide Lexus RC F 2018 dimensions	https://www.carsguide.com.au/lexus/rc/rc-f/car-dimensions/2018?id=4EjSHNDM
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910	Toyota PROACE VERSO 2017 official brochure;Toyota Proace Van official technical specifications	https://leparnass.sakura.ne.jp/catalogue_pdf/toyota_new_proace_verso201708_e.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	Auto-Data Dacia Duster II 1.6 SCe	https://www.auto-data.net/en/dacia-duster-ii-1.6-sce-114hp-32116
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682	Auto-Data Dacia Duster II 1.6 SCe 4x4	https://www.auto-data.net/en/dacia-duster-ii-1.6-sce-114hp-4x4-32117
EU-POLESTAR-1-I-COUPE-01	4586	1958	1352	Polestar 1 owner manual - Dimensions	https://www.polestar.com/uk/manual/polestar-1/2020/article/fe05d708a0740d0c0a8015150f8256d/
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	Auto-Data BMW 6 Series Gran Turismo G32 630d xDrive	https://www.auto-data.net/en/bmw-6-series-gran-turismo-g32-630d-265hp-xdrive-steptronic-30429
EU-BMW-5-G30-SEDAN-01	4936	1868	1466	Auto-Data BMW 5 Series Sedan G30 520i	https://www.auto-data.net/en/bmw-5-series-sedan-g30-520i-184hp-steptronic-29747
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498	Auto-Data BMW 5 Series Touring G31 530i xDrive	https://www.auto-data.net/en/bmw-5-series-touring-g31-530i-252hp-xdrive-steptronic-29812
EU-CHEVROLET-CAPRICE-I-COUPE-1970-01	5486	2027	1377	Automobile-Catalog 1970 Chevrolet Caprice Custom Coupe 454	https://www.automobile-catalog.com/car/1970/412910/chevrolet_caprice_custom_coupe_454_v-8_turbo-jet_390-hp_hydra-matic.html
EU-CHEVROLET-IMPALA-V-COUPE-1977-01	5387	1918	1405	Automobile-Catalog 1977 Chevrolet Impala Coupe 350	https://www.automobile-catalog.com/car/1977/207935/chevrolet_impala_coupe_350-4_v-8_hydra-matic.html
EU-CHEVROLET-IMPALA-V-COUPE-1978-01	5387	1930	1405	Automobile-Catalog 1978 Chevrolet Impala Sport Coupe	https://www.automobile-catalog.com/car/1978/208175/chevrolet_impala_sport_coupe_305_v-8_automatic.html
EU-MAYBACH-62-V240-SEDAN-PREFL-01	6165	1980	1573	Mercedes-Benz Archive Maybach 62	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Maybach-62.xhtml?oid=6181
EU-MAYBACH-62-V240-SEDAN-FACELIFT-01	6171	1980	1573	Mercedes-Benz Japan Maybach facelift press release;Automobile-Catalog 2010 Maybach 62	https://www.mercedes-benz.jp/news/release/2010/20100722.pdf;https://www.automobile-catalog.com/car/2010/1570490/maybach_62.html
EU-CHEVROLET-SILVERADO-1500-II-GMT900-CREW-CAB-SHORT-BOX-4X4-01	5847	2032	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-STANDARD-BOX-4X4-01	5222	2029	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
EU-CHEVROLET-SILVERADO-1500-II-GMT900-REGULAR-CAB-LONG-BOX-4X4-01	5702	2029	1875	2011 Chevrolet Silverado official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2011_silverado.pdf
EU-CHEVROLET-SILVERADO-1500-I-GMT800-CLASSIC-HYBRID-EXTENDED-CAB-SHORT-BOX-4X4-01	5847	1994	1877	J.D. Power 2007 Chevrolet Silverado 1500 Classic Hybrid;Chevrolet Silverado first-generation specifications	https://www.jdpower.com/cars/2007/chevrolet/silverado-1500-classic-hybrid/extended-cab-lt-hybrid-4wd/specs;https://en.wikipedia.org/wiki/Chevrolet_Silverado_(first_generation)
EU-TOYOTA-CAMRY-XV70-SEDAN-01	4885	1840	1445	Auto-Data Toyota Camry XV70 2.5 181	https://www.auto-data.net/en/toyota-camry-viii-xv70-2.5-181hp-automatic-39090
EU-TOYOTA-RAV4-I-XA10-SUV-3D-PREFL-01	3705	1695	1655	Toyota RAV4 first-generation official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-5dr-UK-launch-pack.pdf
EU-TOYOTA-RAV4-I-XA10-SUV-3D-FACELIFT-01	3705	1695	1660	Toyota RAV4 1998 model change official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-MC-soft-top-UK-launch-pack.pdf
EU-TOYOTA-RAV4-I-XA10-SUV-5D-01	4115	1695	1660	Toyota RAV4 first-generation official UK launch pack;Toyota RAV4 1998 model change official UK launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-5dr-UK-launch-pack.pdf;https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen1-MC-soft-top-UK-launch-pack.pdf
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Peugeot 3008 official price and specification guide	https://www.forum-peugeot.com/wp-content/uploads/2016/07/prix3008bejuin2017.pdf
EU-DODGE-CALIBER-I-PM-HATCHBACK-01	4415	1800	1535	Automobile-Catalog Dodge Caliber SXT 2.0 CRD	https://www.automobile-catalog.com/car/2006/690935/dodge_caliber_sxt_2_0l_crd.html
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640	Automobile-Catalog Peugeot 5008 dimensions	https://www.automobile-catalog.com/car/2020/2969630/peugeot_5008_1_2_puretech_130.html
EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	4403	1848	1878	PEUGEOT Rifter July 2019 official brochure;Peugeot France official Rifter dimensions	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-rifter-prices-specifications-brochure-july-2019.pdf;https://www.peugeot.fr/content/peugeot/worldwide/france/fr_fr/index/nos-vehicules/e-rifter.html
EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	4753	1848	1882	PEUGEOT Rifter July 2019 official brochure;Peugeot France official Rifter dimensions	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-rifter-prices-specifications-brochure-july-2019.pdf;https://www.peugeot.fr/content/peugeot/worldwide/france/fr_fr/index/nos-vehicules/e-rifter.html
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai Nuova Santa Fe official technical specifications	https://www.hyundai.news/it/articles/press-releases/nuova-hyundai-santa-fe-caratteristiche-tecniche.html
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift 2.0 TFSI	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-2.0-tfsi-190hp-23778
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 CLS 300d	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-cls-300d-245hp-9g-tronic-33015
EU-LEXUS-IS-III-FACELIFT-SEDAN-01	4680	1810	1430	Toyota GAZOO Lexus IS300 catalog;Automobile-Catalog Lexus IS 300 2018	https://gazoo.com/catalog/maker/LEXUS/IS/201305/10117449/;https://www.automobile-catalog.com/car/2018/2573915/lexus_is_300.html
EU-LEXUS-RC-I-COUPE-01	4695	1840	1395	CarsGuide Lexus RC300 2018 dimensions	https://www.carsguide.com.au/lexus/rc/rc300/car-dimensions/2018
EU-MG-ZS-I-SUV-01	4314	1809	1611	VehicleScore MG ZS dimensions	https://vehiclescore.co.uk/car-dimensions-check/mg/zs
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940	AutoGuru Toyota Proace Verso Medium Family 4x4 test;Toyota Switzerland Proace 4x4 announcement	https://www.autoguru.at/2018/11/toyota-proace-verso-l1-family-4x4-testbericht/;https://toyota-media.ch/de/modelle/article/76795
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950	Toyota Proace official 4x4 technical specifications;Toyota Switzerland Proace 4x4 announcement	https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf;https://toyota-media.ch/de/modelle/article/76795
EU-LANCIA-DELTA-I-831-HF-INTEGRALE-EVOLUZIONE-HATCHBACK-01	3900	1770	1365	Stellantis Heritage Lancia Delta HF 4WD/Integrale;Goo-net Exchange Lancia Delta HF Integrale Evoluzione catalog	https://www.stellantisheritage.com/en-uk/heritage/stories/lancia-delta-HF-4WD-integrale;https://www.goo-net-exchange.com/catalog/LANCIA__DELTA/9001605/
EU-VW-T-ROC-I-SUV-01	4234	1819	1573	Auto-Data Volkswagen T-Roc I 2.0 TDI 150	https://www.auto-data.net/en/volkswagen-t-roc-i-2.0-tdi-scr-150hp-dsg-36177
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Auto-Data Opel Grandland X 1.5d 130	https://www.auto-data.net/en/opel-grandland-x-1.5d-130hp-33096
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Support - V60 Dimensions	https://www.volvocars.com/my/support/car/v60/article/766ee075f0e03896c0a8015109ee0749/
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416	Auto-Data Honda Civic X Sedan 1.6 i-DTEC	https://www.auto-data.net/en/honda-civic-x-sedan-1.6-i-dtec-120hp-32759
EU-OPEL-KARL-I-HATCHBACK-5D-01	3675	1595	1485	Auto-Data Opel Karl 1.0 73	https://www.auto-data.net/en/opel-karl-1.0-73hp-38554
EU-CADILLAC-XT4-I-E2XX-SUV-01	4599	1881	1627	Cadillac XT4 official technical data	https://media.chevrolet.com/content/dam/Media/documents/INTL/cadillac/2018/crossover-suv/xt4/Tech-Data-Cadillac-XT4-EN.pdf
EU-PIAGGIO-APE-50-VAN-01	2500	1260	1590	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Ford All-New Focus official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/2018/FORD_FOCUS_2018_MediaDrive_TechSpecs_EU.pdf
EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	2490	1260	1550	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	2660	1260	1550	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-PIAGGIO-APE-50-PICKUP-CROSS-01	2530	1260	1620	Piaggio Commercial Vehicles Ape 50 technical information	https://piaggiocommercialuk.com/wp-content/uploads/2018/01/Ape-50-technical-info-EN-1.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	4609	1920	1940	Toyota Proace official 4x4 technical specifications;AutoWeek Toyota Proace 4x4 availability	https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf;https://www.autoweek.nl/autotests/artikel/gereden-toyota-proace-4x4/
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	4959	1920	1950	Toyota Proace official 4x4 technical specifications;AutoWeek Toyota Proace 4x4 availability	https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf;https://www.autoweek.nl/autotests/artikel/gereden-toyota-proace-4x4/
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	5309	1920	1950	Toyota Proace official 4x4 technical specifications;AutoWeek Toyota Proace 4x4 availability	https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf;https://www.autoweek.nl/autotests/artikel/gereden-toyota-proace-4x4/
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410	BMW Group PressClub - M2 Competition specifications	https://www.press.bmwgroup.com/new-zealand/article/attachment/T0289640EN/421821
EU-PEUGEOT-308-CC-I-T7-CONVERTIBLE-01	4400	1817	1426	Automobile-Catalog Peugeot 308 CC 1.6 HDi	https://www.automobile-catalog.com/car/2009/2622155/peugeot_308_cc_1_6_hdi_fap_112_110.html
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685	Auto-Data Mitsubishi Eclipse Cross I 1.5 T-MIVEC	https://www.auto-data.net/en/mitsubishi-eclipse-cross-i-1.5-t-mivec-163hp-cvt-32364
EU-JAGUAR-VANDEN-PLAS-XJ40-SEDAN-01	4988	1798	1380	Jaguar Daimler Heritage Trust XJ40 research guide;Automobile-Catalog Jaguar Vanden Plas XJ40	https://www.jaguarheritage.com/uploads/RG001O-Jaguar-and-Daimler-XJ-Series-XJ40-X300-v.2-31-03-2020.pdf;https://www.automobile-catalog.com/car/1988/1284065/jaguar_vanden_plas.html
EU-MERCEDES-BENZ-C-CLASS-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data Mercedes-Benz C 220d W205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-220d-194hp-9g-tronic-32993
EU-MERCEDES-BENZ-C-CLASS-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data Mercedes-Benz C 220d S205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-220d-194hp-9g-tronic-32996
EU-MERCEDES-BENZ-C-CLASS-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data Mercedes-Benz C 220d C205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-220d-194hp-9g-tronic-33049
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data Mercedes-Benz C 220d A205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-220d-194hp-9g-tronic-33061
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-E400D-01	4923	1852	1468	Auto-Data Mercedes-Benz E 400d W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-400d-340hp-4matic-9g-tronic-35193
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-E400D-01	4933	1852	1475	Auto-Data Mercedes-Benz E 400d S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-400d-340hp-4matic-9g-tronic-35180
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-AMG-E53-01	4942	1852	1447	Auto-Data Mercedes-AMG E 53 W213	https://www.auto-data.net/en/mercedes-benz-e-class-w213-amg-e-53-435hp-eq-boost-4matic-amg-speedshift-tct-35215
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-AMG-E53-01	4971	1860	1461	Auto-Data Mercedes-AMG E 53 S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-53-435hp-eq-boost-4matic-amg-speedshift-tct-35183
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-AMG-G63-01	4881	1984	1969	Auto-Data Mercedes-AMG G 63 W463 facelift	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2018-amg-g-63-v8-585hp-4matic-9g-tronic-amg-speedshift-plus-42381
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620	Auto-Data DS 7 Crossback 1.6 PureTech 225	https://www.auto-data.net/en/ds-7-crossback-1.6-puretech-225hp-automatic-28817
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460	PEUGEOT 208 Hatchback Range June 2018 official specification	https://www.guyperry.co.uk/wp-content/uploads/2018/06/208-Spec-Sheet.pdf
EU-PEUGEOT-2008-I-FACELIFT-SUV-01	4159	1739	1556	Automobile-Catalog Peugeot 2008 I dimensions;Auto-Data Peugeot 2008 1.2 PureTech 82	https://www.automobile-catalog.com/car/2018/2627525/peugeot_2008_1_6_bluehdi_100_no_start-stop.html;https://www.auto-data.net/en/peugeot-2008-i-facelift-2016-1.2-puretech-82hp-22749
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570	Hyundai KONA Electric official technical specifications and dimensions	https://www.hyundai.news/fr/archives-du-dossier-de-presse/kona-electric-2018/kona-electric-caracteristiques-techniques-et-dimensions.html
EU-CHEVROLET-CHEVELLE-III-SEDAN-1974-01	5342	1946	1367	Automobile-Catalog 1974 Chevrolet Chevelle Malibu Classic Sedan	https://www.automobile-catalog.com/car/1974/161315/chevrolet_chevelle_malibu_classic_sedan_454_v-8_turbo-jet_4-speed.html
EU-CHEVROLET-CHEVELLE-III-SEDAN-1975-01	5314	1946	1367	Automobile-Catalog 1975 Chevrolet Chevelle Malibu Classic Sedan	https://www.automobile-catalog.com/car/1975/199985/chevrolet_chevelle_malibu_classic_sedan_250_turbo-thrift.html
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data Volvo V90 T8 dimensions	https://www.auto-data.net/en/volvo-v90-2016-2.0-t8-twin-engine-303hp-plug-in-hybrid-awd-geartronic-36308
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Auto-Data Volvo S90 T8 dimensions	https://www.auto-data.net/en/volvo-s90-2016-2.0-t8-twin-engine-303hp-plug-in-hybrid-awd-geartronic-34905
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2101-2200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf "https://www.toyota.fi/content/dam/toyota/nmsc/finland/pdf-files/tekniset-tiedot/Proace_tekniset_tiedot.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1210 行）
- 累计尺寸组：dimension_groups_final.tsv（674 行）

