# 任务：all 第 1801-1900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0019__f840717f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1801-1900 行

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
all 第 1801-1900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-BENTLEY-CONTINENTAL-GT-II-V8S-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-W12-01	4850	1954	1405
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-340-SEDAN-01	4600	1765	1630
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-I-01	4895	1816	1354
EU-CHEVROLET-MALIBU-III-COUPE-PHASE-II-01	4895	1836	1415
EU-CHEVROLET-MALIBU-III-SEDAN-PHASE-I-01	4895	1816	1377
EU-CITROEN-BERLINGO-II-B9-MPV-4X4-01	4380	1810	1865
EU-CITROEN-BERLINGO-II-B9-VAN-L1-4X4-01	4380	1810	1812
EU-CITROEN-BERLINGO-II-B9-VAN-L2-4X4-01	4628	1810	1888
EU-CITROEN-C3-III-HATCHBACK-PREFL-01	3996	1749	1474
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-PREFL-VAN-5D-01	4358	1823	1484
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	4418	1835	1836
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	4818	1835	1839
EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	4818	1835	1840
EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	4418	1835	1861
EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	4818	1835	1861
EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	4065	1725	1450
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-01	4380	1810	1801
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291
EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	4507	1880	1297
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	5049	1937	1428
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454
EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	4645	1760	1470
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798
EU-VW-PASSAT-B8-ALLTRACK-WAGON-01	4777	1832	1506
EU-VW-POLO-III-6N1-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453
EU-VW-POLO-VI-AW1-HATCHBACK-01	4053	1751	1446

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
MAN	Tge	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	90	122	Aug 2017	Dec 2021	2025-11-01	128960
VW	Crafter	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	90	122	Aug 2017	Dec 2021	2025-11-01	128961
VW	Crafter	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	90	122	Aug 2017	Dec 2021	2025-11-01	128962
Fiat	Ducato	130 Multijet 2,3 D 4X4	Bus	Allrad	Diesel	96	131	Jun 2011	-	2024-03-01	128963
Fiat	Ducato	150 Multijet 2,3 D 4X4	Bus	Allrad	Diesel	110	150	Apr 2015	-	2024-03-01	128964
Fiat	Ducato	130 Multijet 2,3 D 4X4	Kasten	Allrad	Diesel	96	131	Jun 2011	-	2024-03-01	128966
Fiat	Ducato	150 Multijet 2,3 D 4X4	Kasten	Allrad	Diesel	110	150	Dec 2015	-	2025-02-03	128967
Citroën	C3 i	1.1 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	44	60	Jun 2006	Dec 2009	2024-03-01	128972
VW	Passat b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Jan 2016	Nov 2018	2025-02-03	128973
Seat	Arona	1.6 TDI	SUV	Frontantrieb	Diesel	70	95	Nov 2017	-	2024-03-01	128974
Porsche	718 cayman	2.5 GTS	Coupe	Heckantrieb	Benzin	269	365	Oct 2017	-	2024-03-01	128976
Porsche	718 boxster	2.5 GTS	Cabriolet	Heckantrieb	Benzin	269	365	Oct 2017	-	2024-03-01	128977
MAN	Tge	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	103	140	Oct 2017	-	2024-03-01	128979
MAN	Tge	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	130	177	May 2017	Jun 2024	2024-05-01	128980
MAN	Tge	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	103	140	Nov 2017	-	2024-03-01	128981
MAN	Tge	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	130	177	Jul 2017	Jun 2024	2024-05-01	128982
Mercedes-benz	S-Klasse	AMG S 63 4-matic+	Cabriolet	Allrad	Benzin	450	612	Oct 2017	Jul 2020	2024-03-01	129005
Mercedes-benz	S-Klasse	S 63 AMG 4-matic+	Coupe	Allrad	Benzin	450	612	Oct 2017	Jul 2020	2024-03-01	129007
Mercedes-benz	S-Klasse	S 450 4-matic	Coupe	Allrad	Benzin	270	367	Dec 2015	Jul 2020	2024-03-01	129009
Mercedes-benz	S-Klasse	S 560 4-matic	Coupe	Allrad	Benzin	345	469	Oct 2017	Jul 2020	2024-03-01	129010
Mercedes-benz	S-Klasse	S 560	Coupe	Heckantrieb	Benzin	345	469	Oct 2017	Jul 2020	2024-03-01	129011
Mercedes-benz	S-Klasse	S 560	Cabriolet	Heckantrieb	Benzin	345	469	Oct 2017	Jul 2020	2024-03-01	129012
Ford	Ecosport	1.5 Ti-vct	SUV	Frontantrieb	Benzin	81	110	Oct 2013	Jun 2022	2024-11-01	129013
Ford	Kuga ii	2.0 Ecoboost 4X4	SUV	Allrad	Benzin	178	242	Aug 2017	Jun 2018	2024-03-01	129015
Mitsubishi	Eclipse cross	1.5 T-mivec 4WD	SUV	Allrad	Benzin	120	163	Oct 2017	-	2024-03-01	129028
Mitsubishi	Eclipse cross	1.5 T-mivec	SUV	Frontantrieb	Benzin	120	163	Oct 2017	-	2024-03-01	129029
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	141	192	Apr 2008	Jul 2010	2024-03-01	129030
BMW	X2	Sdrive 20 I	SUV	Frontantrieb	Benzin	141	192	Nov 2017	Oct 2023	2024-03-01	129032
BMW	X2	Xdrive 20 D	SUV	Allrad	Diesel	140	190	Nov 2017	Oct 2023	2024-03-01	129033
BMW	X2	Xdrive 25 D	SUV	Allrad	Diesel	170	231	Nov 2017	Sep 2023	2024-03-01	129034
Fiat	Grande punto van	1.3 JTD Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Feb 2006	Jun 2013	2024-03-01	129035
Toyota	Prius	1.8 Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	100	136	Apr 2009	Dec 2015	2024-05-01	129038
BMW	X2	Xdrive 18 D	SUV	Allrad	Diesel	110	150	Mar 2018	Oct 2023	2024-03-01	129041
Toyota	Avalon	3.5	Stufenheck	Frontantrieb	Benzin	198	269	Oct 2005	Nov 2012	2024-03-01	129046
Opel	Astra g classic	1.6 16V	Stufenheck	Frontantrieb	Benzin	74	101	Mar 2004	Jan 2008	2024-03-01	129055
KIA	Rio iv	1.6	Stufenheck	Frontantrieb	Benzin	90	123	Jul 2017	-	2024-03-01	129056
VW	Arteon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2017	-	2024-03-01	129059
Opel	Astra g classic	1.4 16V	Stufenheck	Frontantrieb	Benzin	66	90	May 2004	Jul 2009	2024-03-01	129060
Opel	Astra g classic	1.4 16V	Schrägheck	Frontantrieb	Benzin	66	90	May 2004	Jul 2009	2024-03-01	129062
Ford USA	Aerostar	4.0 AWD	Großraumlimousine	Allrad	Benzin	114	155	Sep 1991	Dec 1997	2024-03-01	129063
Opel	Astra g classic	1.6 16V	Schrägheck	Frontantrieb	Benzin	74	101	May 2004	Feb 2006	2024-03-01	129065
Opel	Astra g classic	1.6	Schrägheck	Frontantrieb	Benzin	76	103	Mar 2006	Jun 2008	2024-03-01	129066
VW	Polo	1.6	Stufenheck	Frontantrieb	Benzin	81	110	May 2015	Mar 2020	2024-03-01	129067
Opel	Astra g classic	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	59	80	Jun 2004	Jul 2009	2024-03-01	129069
Opel	Astra g classic caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	59	80	May 2004	Jul 2009	2024-03-01	129072
Opel	Astra g classic caravan	1.4 16V	Kombi	Frontantrieb	Benzin	66	90	Jul 2004	Sep 2007	2024-03-01	129075
Opel	Astra g classic caravan	1.6	Kombi	Frontantrieb	Benzin	76	103	Feb 2006	Jul 2009	2024-03-01	129076
Ford	Transit	2.3 Bifuel	Kasten	Heckantrieb	Benzin/Autogas (LPG)	105	143	Mar 2001	Mar 2006	2024-03-01	129077
Peugeot	Partner	1.6 HDI 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	68	92	Apr 2010	-	2024-03-01	129078
VW	Polo	2.0 GTI	Schrägheck	Frontantrieb	Benzin	147	200	Nov 2017	Nov 2021	2026-07-01	129081
Seat	Ibiza v	1.6 TDI	Schrägheck	Frontantrieb	Diesel	59	80	Nov 2017	-	2024-03-01	129082
Opel	Astra g classic caravan	1.6	Kombi	Frontantrieb	Benzin	74	101	Jun 2004	Feb 2006	2024-03-01	129087
Opel	Astra h family caravan	1.4	Kombi	Frontantrieb	Benzin	66	90	Jan 2009	May 2014	2026-04-01	129088
Opel	Astra h family	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Jan 2009	May 2014	2026-04-01	129091
Opel	Astra h family	1.8	Stufenheck	Frontantrieb	Benzin	103	140	Jan 2009	Sep 2012	2026-04-01	129092
Seat	Ibiza v	1.0 TGI	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2017	-	2024-03-01	129093
Abarth	Punto	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Oct 2009	Feb 2012	2024-03-01	129101
Suzuki	Jimny	1.3 16V 4WD	Geländewagen offen	Allrad	Benzin	59	80	Sep 1998	-	2024-03-01	129105
Suzuki	Jimny	1.3	Geländewagen offen	Heckantrieb	Benzin	63	86	Aug 2004	-	2024-03-01	129107
Suzuki	Jimny	1.3 4WD	Geländewagen offen	Allrad	Benzin	63	86	Mar 2013	-	2024-03-01	129108
BMW	3	M3 CS	Stufenheck	Heckantrieb	Benzin	338	460	Jan 2018	Oct 2018	2024-03-01	129115
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	75	102	Nov 2017	-	2024-03-01	129118
Mini	Mini	ONE First	Schrägheck	Frontantrieb	Benzin	55	75	Nov 2017	-	2024-03-01	129119
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	75	102	Nov 2017	-	2024-03-01	129121
Mini	Mini	ONE First	Schrägheck	Frontantrieb	Benzin	55	75	Nov 2017	-	2024-03-01	129125
Mini	Mini	ONE	Cabriolet	Frontantrieb	Benzin	75	102	Nov 2017	-	2024-03-01	129127
Alfa Romeo	Stelvio	2.9 Q4	SUV	Allrad	Benzin	375	510	Nov 2017	-	2024-03-01	129130
DS	Ds	1.5 Bluehdi 130	SUV	Frontantrieb	Diesel	96	130	Sep 2017	-	2024-03-01	129160
Mercedes-benz	G-Klasse	G 300	Geländewagen geschlossen	Allrad	Benzin	125	170	Jun 1993	Aug 1997	2024-03-01	129165
VW	Crafter	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	130	177	May 2017	Jun 2024	2024-05-01	129166
Opel	Crossland x /	1.2 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	60	82	Oct 2017	-	2024-03-01	129169
Ford	Focus iii turnier	1.0 Ecoboost	Kombi	Frontantrieb	Benzin	103	140	Oct 2017	Feb 2020	2024-03-01	129170
Ford	Focus iii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	103	140	Oct 2017	Feb 2020	2024-03-01	129171
Ford	Focus iii	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	103	140	Oct 2017	Feb 2020	2024-03-01	129172
VW	Crafter	2.0 TDI 4motion	Kasten	Allrad	Diesel	103	140	Apr 2017	-	2024-03-01	129174
VW	Crafter	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	130	177	Jul 2017	Jun 2024	2024-05-01	129177
Porsche	911	3.8 GT2 RS	Coupe	Heckantrieb	Benzin	515	700	Jul 2017	May 2020	2024-03-01	129180
Porsche	Panamera	4.0 Turbo S E-hybrid	Kombi	Allrad	Benzin/Elektro	500	680	May 2017	Dec 2023	2024-08-01	129185
BMW	X2	Xdrive 20 D	SUV	Allrad	Diesel	120	163	Nov 2017	Oct 2023	2024-03-01	129187
VW	Crafter	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	103	140	Oct 2017	-	2024-03-01	129195
VW	Crafter	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	103	140	Nov 2017	-	2024-03-01	129196
VW	Crafter	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	103	140	Nov 2017	-	2024-03-01	129197
VW	Crafter	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	130	177	Nov 2017	-	2025-02-03	129198
MAN	Tge	2.0 TDI AWD	Pritsche/Fahrgestell	Allrad	Diesel	103	140	Nov 2017	-	2024-03-01	129201
Fiat	Punto	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	57	78	Mar 2009	Feb 2012	2024-03-01	129202
Fiat	Punto	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Mar 2009	Feb 2012	2024-03-01	129203
MAN	Tge	2.0 TDI AWD	Pritsche/Fahrgestell	Allrad	Diesel	130	177	Nov 2017	-	2024-03-01	129204
Seat	Leon	2.0 Cupra R	Schrägheck	Frontantrieb	Benzin	228	310	Nov 2017	Aug 2018	2024-03-01	129205
Bentley	Continental	6.0 GT Speed	Coupe	Allrad	Benzin	472	642	May 2016	Jul 2018	2024-03-01	129206
Citroën	Berlingo	1.6 HDI 90	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jul 2010	Dec 2018	2026-05-01	129210
Citroën	Ds3	1.6 Racing	Cabriolet	Frontantrieb	Benzin	149	203	Mar 2014	Jul 2015	2024-03-01	129219
Chevrolet	Malibu	2.0 D	Stufenheck	Frontantrieb	Diesel	115	156	Apr 2012	-	2024-03-01	129222
Bentley	Continental	6.0 GT Speed	Coupe	Allrad	Benzin	467	635	May 2014	May 2016	2024-03-01	129223
Dodge	Journey	2.0 CRD	Großraumlimousine	Frontantrieb	Diesel	100	136	Jun 2008	Dec 2011	2024-03-01	129225
Fiat	Ducato	110 Multijet 2,3 D	Bus	Frontantrieb	Diesel	82	111	May 2014	-	2024-03-01	129239
Fiat	Ducato	110 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	82	111	May 2014	-	2024-03-01	129240
Fiat	Ducato	110 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	82	111	Aug 2006	-	2024-03-01	129241
Ford	Escort vi turnier	1.4	Kombi	Frontantrieb	Benzin	54	73	Jan 1995	Dec 1996	2024-03-01	129250
Ford	Escort vi	1.4	Stufenheck	Frontantrieb	Benzin	54	73	Jan 1995	Dec 1996	2024-03-01	129252
Ferrari	Portofino	3.9	Cabriolet	Heckantrieb	Benzin	441	600	Aug 2017	-	2024-03-01	129253


--- Round 1 / 首次发送 ---
## 更新点

* 完成跨批次尺寸组缓存匹配，首轮闭合 **20 个 Ktype、56 条派生映射**。
* Crafter II、TGE I 的通用底盘车/厢式车按已确认的驾驶室、车长及车顶分支拆分。
* Arona、EcoSport、MINI R57、Arteon、Ibiza V、Stelvio、Crossland X、Panamera Sport Turismo、Fiat Punto 199 已关联既有尺寸组。
* 本轮全部复用既有尺寸组，未重复抓取或重复输出尺寸来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：20
* PENDING Ktype：80
* READY 映射：56
* 当前引用的已确认尺寸组：24
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128960_scab_l3	128960	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128960_scab_l4	128960	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128960_dcab_l3	128960	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128960_dcab_l4	128960	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128961_scab_l3	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128961_scab_l4	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128961_scab_l5	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
128961_dcab_l3	128961	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128961_dcab_l4	128961	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128962_l3h2	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128962_l3h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128962_l4h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128962_l4h4	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128962_l5h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128962_l5h4	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
128974	128974	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128981_scab_l3	128981	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128981_scab_l4	128981	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128981_dcab_l3	128981	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128981_dcab_l4	128981	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128982_scab_l3	128982	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128982_scab_l4	128982	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128982_dcab_l3	128982	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128982_dcab_l4	128982	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129013	129013	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH		READY
129030	129030	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	HIGH	改款前Cooper S敞篷外廓。	READY
129059	129059	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	改款前物理外廓。	READY
129082	129082	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
129093	129093	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
129130	129130	SUV	Stelvio	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
129166_l3h2	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129166_l3h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129166_l4h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129166_l4h4	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129166_l5h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129166_l5h4	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129169	129169	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
129177_scab_l3	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129177_scab_l4	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129177_scab_l5	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129177_dcab_l3	129177	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129177_dcab_l4	129177	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129185	129185	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo Sport Turismo物理外廓。	READY
129195_l3h2	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129195_l3h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129195_l4h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129195_l4h4	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129195_l5h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129195_l5h4	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129196_scab_l3	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129196_scab_l4	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129196_scab_l5	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129196_dcab_l3	129196	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129196_dcab_l4	129196	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129202	129202	Van	Punto Evo	199	3	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	三门商用Van与Punto 199同外廓。	READY
129203	129203	Van	Punto Evo	199	3	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	三门商用Van与Punto 199同外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 MAN TGE 厢式车、Crafter 4Motion、Ducato Bus/Van/Chassis及4×4多轴距、多车顶分支。
2. 批量处理 Mercedes-Benz C217/A217、BMW X2 F39、Opel Astra G/H Family、Ford Focus III facelift 和 MINI F56/F57。
3. 再处理 Porsche 718/911、Bentley Continental、Toyota Prius/Avalon、Suzuki Jimny等独立车型簇。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 **12 个 Ktype、12 条映射**。
* 首次创建并闭合 BMW X2 F39、Toyota Prius III Plug-in、MINI F55/F56/F57 和 Porsche 911 GT2 RS 共 **6 个尺寸组**。
* BMW、MINI 与 Porsche 尺寸采用厂商技术资料，并核对宽度为不含后视镜口径。([BMW Group PressClub][1])
* Prius Plug-in 尺寸采用 Toyota Europe 官方技术资料。([newsroom.toyota.eu][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：32
* PENDING Ktype：68
* READY 映射：68
* 已确认尺寸组：30
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129032	129032	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129033	129033	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129034	129034	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129038	129038	Hatchback	Prius III	ZVW35	5	EU-TOYOTA-PRIUS-III-XW30-PLUG-IN-HATCHBACK-01	HIGH		READY
129041	129041	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129118	129118	Hatchback	MINI F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH		READY
129119	129119	Hatchback	MINI F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH		READY
129121	129121	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-ONE-01	HIGH		READY
129125	129125	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-ONE-01	HIGH		READY
129127	129127	Convertible	MINI F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	HIGH		READY
129180	129180	Coupe	911 991.2	991.2	2	EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	HIGH		READY
129187	129187	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X2-F39-SUV-01	4360	1824	1526	BMW Group PressClub BMW X2 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0285189EN/414886
EU-TOYOTA-PRIUS-III-XW30-PLUG-IN-HATCHBACK-01	4480	1745	1490	Toyota Europe Prius Plug-in Hybrid technical data	https://newsroom.toyota.eu/2019-2014-toyota-geneva-motor-show-prius-plug-in-hybrid---towards-the-ultimate-eco-car/
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425	BMW Group PressClub MINI 5 door technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274783EN/397685
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414	BMW Group PressClub MINI 3 door technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0284470CS/413623
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415	BMW Group PressClub MINI Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0284420EN/413748
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297	Porsche Goodwood 2017 official technical data	https://newsroom.porsche.com/dam/jcr%3A914d7fe5-dc87-415e-9bee-8fee16daa804/Goodwood_2017_DE_EN_V4.pdf
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz S-Class C217/A217 Coupe与Cabriolet尺寸组。
2. 处理 Fiat Ducato Bus、Van、Chassis及4×4多轴距和多车顶分支。
3. 处理 Opel Astra G Classic、Astra H Family和Ford Focus III facelift车身簇。
4. 继续关联剩余 Crafter/TGE 4Motion、AWD厢式车及底盘车分支。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0285189EN/414886 "BMW Group PressClub"
[2]: https://newsroom.toyota.eu/2019-2014-toyota-geneva-motor-show-prius-plug-in-hybrid---towards-the-ultimate-eco-car/?utm_source=chatgpt.com "2014 Toyota Geneva Motor Show: Prius Plug-in Hybrid"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 MAN TGE 厢式车 2 个 Ktype，并首次创建 6 个稳定尺寸组。
* 闭合 Crafter 4Motion 厢式车、Crafter 4Motion 底盘车及 MAN TGE AWD 底盘车共 5 个 Ktype。
* 本轮新增 READY 映射 36 条；除 MAN TGE 厢式车尺寸组外，其余均关联既有尺寸组。
* MAN 官方技术资料确认 TGE 厢式车的 3 种长度、对应车顶分支及 2040 mm 不含后视镜车宽。([MAN Global][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：39
* PENDING Ktype：61
* READY 映射：104
* 已确认尺寸组：36
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128979_l3h2	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128979_l3h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128979_l4h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128979_l4h4	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128979_l5h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128979_l5h4	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
128980_l3h2	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128980_l3h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128980_l4h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128980_l4h4	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128980_l5h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128980_l5h4	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129174_l3h2	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129174_l3h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129174_l4h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129174_l4h4	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129174_l5h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129174_l5h4	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129197_scab_l3	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129197_scab_l4	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129197_scab_l5	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129197_dcab_l3	129197	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129197_dcab_l4	129197	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129198_scab_l3	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129198_scab_l4	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129198_scab_l5	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129198_dcab_l3	129198	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129198_dcab_l4	129198	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129201_scab_l3	129201	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129201_scab_l4	129201	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129201_dcab_l3	129201	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129201_dcab_l4	129201	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129204_scab_l3	129204	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129204_scab_l4	129204	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129204_dcab_l3	129204	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129204_dcab_l4	129204	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H4-01	6836	2040	2798	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L5H3-01	7391	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L5H4-01	7391	2040	2798	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
```

## 下一步优先处理

1. 闭合 Mercedes-Benz S-Class C217/A217 的 AMG 与普通外廓分支。
2. 批量处理 Opel Astra G Classic、Astra H Family 的 Sedan、Hatchback、Wagon 尺寸组。
3. 处理 Ford Focus III facelift 三种车身及 Fiat Ducato 多长度、多车顶分支。

推进信号：CONTINUE

[1]: https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf "730232-99852-Update Pricelist and Launch Brochure 297x210_DEE.indd"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
## 更新点

* 新增闭合 **7 个 Ktype、7 条映射**。
* 首次创建 Ford Focus III facelift Hatchback/Sedan、Volkswagen Passat B8 Sedan、Mitsubishi Eclipse Cross I、Ferrari Portofino 共 **5 个尺寸组**。
* Seat Leon Cupra R 直接复用既有 facelift 5-door 尺寸组。
* Ford、Volkswagen、Mitsubishi 与 Ferrari 的新尺寸组均已按官方资料确认三维及不含后视镜宽度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：46
* PENDING Ktype：54
* READY 映射：111
* 当前引用的已确认尺寸组：42
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128973	128973	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	改款前轿车物理外廓。	READY
129028	129028	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
129029	129029	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
129171	129171	Hatchback	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	HIGH		READY
129172	129172	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	HIGH		READY
129205	129205	Hatchback	Leon III facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Cupra R五门物理外廓。	READY
129253	129253	Convertible	Portofino	F164	2	EU-FERRARI-PORTOFINO-F164-CONVERTIBLE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456	Volkswagen UK The Passat and Passat Estate official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685	Mitsubishi Motors Eclipse Cross Geneva 2017 official specifications	https://media.mitsubishicars.com/releases/mitsubishi-motors-to-globally-premiere-eclipse-cross-compact-suv-at-geneva-international-motor-show-2017
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484	Ford South Africa New Focus Q1 2018 official brochure	https://www.ford.co.za/content/dam/Ford/website-assets/latam/za/nameplate/focus/brochure/Focus-Brochure-Q1-2018_EBrochure.pdf
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484	Ford South Africa New Focus Q1 2018 official brochure	https://www.ford.co.za/content/dam/Ford/website-assets/latam/za/nameplate/focus/brochure/Focus-Brochure-Q1-2018_EBrochure.pdf
EU-FERRARI-PORTOFINO-F164-CONVERTIBLE-01	4586	1938	1318	Ferrari Portofino official technical specifications	https://www.ferrari.com/en-EN/auto/ferrari-portofino
```

## 下一步优先处理

1. 批量闭合 Opel Astra G Classic 的 Sedan、Hatchback、Wagon 车型簇。
2. 处理 Opel Astra H Family 三种车身及 Ford Focus III Turnier。
3. 处理 Porsche 718 GTS、Mercedes-Benz C217/A217 和 Suzuki Jimny Cabrio。
4. 继续拆分 Fiat Ducato Bus、Van、Chassis Cab 的长度及车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 **6 个 Ktype、6 条映射**。
* 首次创建 Porsche 718 GTS Coupe/Convertible、Fiat Grande Punto 199 三门改款前车身、BMW M3 CS F80、DS 7 Crossback I、Ford Focus III facelift Wagon 共 **6 个尺寸组**。
* Porsche 欧洲市场长度及不含后视镜宽度结合 Porsche 技术资料与欧洲规格页闭合；BMW、DS 和 Ford 使用厂商技术资料。
* Grande Punto 与既有 4065 mm 的 Punto Evo 组外廓不同，建立 4030 mm 改款前独立组，未改写既有尺寸事实。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：52
* PENDING Ktype：48
* READY 映射：117
* 当前引用的已确认尺寸组：48
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128976	128976	Coupe	718 982	982	2	EU-PORSCHE-718-982-CAYMAN-GTS-COUPE-01	HIGH		READY
128977	128977	Convertible	718 982	982	2	EU-PORSCHE-718-982-BOXSTER-GTS-CONVERTIBLE-01	HIGH		READY
129035	129035	Van	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-PREFL-01	HIGH	三门商用车身。	READY
129115	129115	Sedan	3 Series F80	F80	4	EU-BMW-3-F80-M3-CS-SEDAN-01	HIGH		READY
129160	129160	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	HIGH		READY
129170	129170	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-718-982-CAYMAN-GTS-COUPE-01	4379	1801	1286	Porsche 718 Cayman GTS technical data;Automobile-Catalog Porsche 718 Cayman GTS Europe	https://newsroom.porsche.com/dam/jcr%3Afbd80b62-5236-4ff6-9f1b-e54ee42f6f7c/PCNA18_0996_us.pdf;https://www.automobile-catalog.com/car/2017/2872385/porsche_718_cayman_gts.html
EU-PORSCHE-718-982-BOXSTER-GTS-CONVERTIBLE-01	4379	1801	1272	Porsche 718 Boxster GTS technical data;Automobile-Catalog Porsche 718 Boxster GTS Europe	https://newsroom.porsche.com/dam/jcr%3A59fc370f-12ba-438a-a85c-2ce0bf4442a9/PCNA18_1002_718BoxsterGTS-technical-specifications.pdf;https://www.automobile-catalog.com/car/2017/2872355/porsche_718_boxster_gts.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-PREFL-01	4030	1687	1490	Automobile-Catalog Fiat Grande Punto 1.3 Multijet 75 Europe	https://www.automobile-catalog.com/car/2006/728030/fiat_grande_punto_1_3_multijet_16v_75_dynamic.html
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424	BMW Group PressClub M3 CS technical data	https://www.press.bmwgroup.com/global/article/attachment/T0275597EN/408532/M3_CS_Technical_Data_E.pdf
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620	DS 7 CROSSBACK official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds7crossbackpricesandspecs-6172c7be26ee3.pdf
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505	Ford New Focus official brochure	https://www.forddealers.co.nz/i/files/FordFocus_Brochure.pdf
```

## 下一步优先处理

1. 批量闭合 Opel Astra G Classic Sedan、Hatchback、Wagon 车型簇。
2. 处理 Opel Astra H Family Sedan、Hatchback、Wagon。
3. 闭合 Mercedes-Benz C217/A217 普通版与 AMG 外廓分支。
4. 处理 Fiat Ducato Bus、Van、Chassis Cab 的车长和车顶组合。
5. 处理 Toyota Avalon、Suzuki Jimny Cabrio、Ford Escort VI 和剩余独立车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/728030/fiat_grande_punto_1_3_multijet_16v_75_dynamic.html?utm_source=chatgpt.com "2006 Fiat Grande Punto 1.3 Multijet 16V 75 Dynamic (man. 5)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 续跑 ---
## 更新点

* 闭合 Opel Astra G Classic II 与 Astra H Family 共 **13 个 Ktype、13 条映射**。
* 首次创建 Sedan、Hatchback、Wagon 共 **6 个尺寸组**。
* Astra G Classic II 官方技术资料明确区分 4-door、5-door 和 Caravan，并给出不含后视镜宽度 1709 mm。([Dixi-Car][1])
* Astra H 官方用户手册分别确认五门、四门和旅行车的三维及不含后视镜宽度。([奥爵公用服务箱][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* PENDING Ktype：35
* READY 映射：130
* 当前引用的已确认尺寸组：54
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129055	129055	Sedan	Astra G Classic II	T98	4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH		READY
129060	129060	Sedan	Astra G Classic II	T98	4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH		READY
129062	129062	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129065	129065	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129066	129066	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129069	129069	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129072	129072	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129075	129075	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129076	129076	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129087	129087	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129088	129088	Wagon	Astra H Family	A04	5	EU-OPEL-ASTRA-H-FAMILY-WAGON-01	HIGH		READY
129091	129091	Hatchback	Astra H Family	A04	5	EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	HIGH		READY
129092	129092	Sedan	Astra H Family	A04	4	EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-OPEL-ASTRA-H-FAMILY-WAGON-01	4515	1753	1500	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	4249	1753	1460	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	4587	1753	1458	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
```

## 下一步优先处理

1. 闭合 Mercedes-Benz S-Class C217 Coupe 与 A217 Cabriolet 的普通版和 AMG 外廓。
2. 处理 Fiat Ducato Bus、Van、Chassis Cab 的长度、车顶及4×4分支。
3. 处理 Toyota Avalon、Ford Aerostar、Transit、Escort VI 和 Dodge Journey。
4. 闭合 Suzuki Jimny Cabrio、Kia Rio IV Sedan、VW Polo Sedan、Citroën DS3 Cabriolet等剩余独立车型。

推进信号：CONTINUE

[1]: https://dixi-car.pl/doc/opel-astra-classic-dane.pdf "PL_Astra_Classic_2007_tech.xls"
[2]: https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf?utm_source=chatgpt.com "Astra-H, v.9 (rev 5), zh-CN (Work nr: K589B_50)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 **10 个 Ktype、10 条映射**。
* 首次创建 Citroën C3 I facelift、Ford Kuga II facelift、Toyota Avalon III、Volkswagen Polo VI GTI、Abarth Punto Evo、Citroën DS3 Cabrio Racing、Chevrolet Malibu VIII 和 Dodge Journey I 共 **8 个尺寸组**。
* C3、Kuga、Avalon 与 Polo GTI 的三维及不含后视镜宽度已闭合。([汽车目录][1])
* Abarth、DS3 Cabrio Racing、Malibu 和 Journey 的对应物理外廓已闭合。([汽车数据网][2])
* 两个 Bentley Continental GT Speed Ktype 与既有 Continental GT II Coupe 尺寸组的三维一致，直接复用既有组，不重复建组。([CarsGuide][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：75
* PENDING Ktype：25
* READY 映射：140
* 当前引用的已确认尺寸组：63
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128972	128972	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
129015	129015	SUV	Kuga II facelift	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
129046	129046	Sedan	Avalon III	GSX30	4	EU-TOYOTA-AVALON-III-GSX30-SEDAN-01	HIGH		READY
129081	129081	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	HIGH	GTI专用保险杠及降低车身外廓。	READY
129101	129101	Hatchback	Punto Evo	199	3	EU-ABARTH-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	Abarth宽体外廓。	READY
129206	129206	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
129219	129219	Convertible	DS3 I Cabrio		2	EU-CITROEN-DS3-I-CABRIO-RACING-CONVERTIBLE-01	HIGH	Racing Cabrio物理外廓。	READY
129222	129222	Sedan	Malibu VIII	V300	4	EU-CHEVROLET-MALIBU-VIII-V300-SEDAN-01	HIGH	欧洲市场V300轿车外廓。	READY
129223	129223	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
129225	129225	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	3860	1667	1510	Automobile-Catalog Citroen C3 1.1i Style Europe	https://www.automobile-catalog.com/car/2006/548495/citroen_c3_1_1i_style.html
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Automobile-Catalog Ford Kuga 2.0 TDCi Europe	https://www.automobile-catalog.com/car/2017/2455610/ford_kuga_2_0_tdci_150_2x4.html
EU-TOYOTA-AVALON-III-GSX30-SEDAN-01	5009	1849	1486	Toyota 2006 Avalon official eBrochure	https://www.auto-brochures.com/makes/Toyota/Avalon/Toyota_US%20Avalon_2006.pdf
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438	Volkswagen UK The new Polo official brochure;Auto-Data Volkswagen Polo VI GTI 2.0 TSI DSG	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/polo/polo-nf/polo-nf-brochure-dec-2017.pdf;https://www.auto-data.net/en/volkswagen-polo-vi-gti-2.0-tsi-200hp-dsg-32275
EU-ABARTH-PUNTO-EVO-199-HATCHBACK-3D-01	4065	1721	1490	Auto-Data Abarth Punto Evo 199	https://www.auto-data.net/en/abarth-punto-model-3182
EU-CITROEN-DS3-I-CABRIO-RACING-CONVERTIBLE-01	3948	1715	1458	Automobile-Catalog Citroen DS3 Cabrio Racing;Auto-Data Citroen DS3 Phase I Cabrio	https://www.automobile-catalog.com/car/2014/2086055/citroen_ds3_cabrio_racing.html;https://www.auto-data.net/en/citroen-ds-3-phase-i-cabrio-generation-4406
EU-CHEVROLET-MALIBU-VIII-V300-SEDAN-01	4865	1855	1465	Automobile-Catalog Chevrolet Malibu 2.0 D LT Europe	https://www.automobile-catalog.com/car/2012/1777610/chevrolet_malibu_2_0_d_lt.html
EU-DODGE-JOURNEY-I-JC-MPV-01	4888	1878	1691	Automobile-Catalog Dodge Journey SXT 2.0 CRD Europe	https://www.automobile-catalog.com/car/2009/1227215/dodge_journey_sxt_2_0l_crd.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz C217/A217 Coupe、Cabriolet普通版及AMG外廓。
2. 批量拆分 Fiat Ducato Bus、Van、Chassis Cab 的长度、轴距、车顶及4×4分支。
3. 处理 Suzuki Jimny Cabrio三个Ktype、Ford Escort VI Sedan/Wagon和Ford Aerostar。
4. 处理 Kia Rio IV Sedan、VW Polo Sedan、Mercedes-Benz G 300、Ford Transit及Partner/Berlingo商用车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/548495/citroen_c3_1_1i_style.html?utm_source=chatgpt.com "2006 Citroen C3 1.1i Style Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[2]: https://www.auto-data.net/en/abarth-punto-model-3182?utm_source=chatgpt.com "Abarth Punto | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.carsguide.com.au/bentley/continental/car-dimensions/2016?utm_source=chatgpt.com "Bentley Continental Dimensions 2016 - Length, Width, Height ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 Mercedes-Benz S-Class C217/A217 facelift、Kia Rio IV Sedan 与 Volkswagen Polo V Sedan 共 **8 个 Ktype、8 条映射**。
* 首次创建普通版与 AMG 版 S-Class Coupe/Cabriolet、Rio Sedan、Polo Sedan 共 **6 个尺寸组**。
* Mercedes-AMG 组采用 Mercedes-Benz 官方补充手册明确的不含后视镜宽度；普通版 Coupe/Cabriolet 分别按欧洲市场车型资料闭合。
* Rio Sedan 与 Polo Sedan 分别采用 Kia 和 Volkswagen 厂商规格资料。([Kia Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* PENDING Ktype：17
* READY 映射：148
* 当前引用的已确认尺寸组：69
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129005	129005	Convertible	S-Class A217 facelift	A217	2	EU-MERCEDES-AMG-S-CLASS-A217-S63-CONVERTIBLE-FACELIFT-01	HIGH	AMG S 63 Cabriolet外廓。	READY
129007	129007	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-AMG-S-CLASS-C217-S63-COUPE-FACELIFT-01	HIGH	AMG S 63 Coupe外廓。	READY
129009	129009	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129010	129010	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129011	129011	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129012	129012	Convertible	S-Class A217 facelift	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-CONVERTIBLE-FACELIFT-01	HIGH	普通版Cabriolet外廓。	READY
129056	129056	Sedan	Rio IV	YB	4	EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
129067	129067	Sedan	Polo V Sedan facelift	602	4	EU-VW-POLO-V-602-SEDAN-FACELIFT-01	HIGH	Polo V四门轿车改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-AMG-S-CLASS-A217-S63-CONVERTIBLE-FACELIFT-01	5051	1913	1428	Mercedes-Benz Mercedes-AMG S-Class supplemental owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/no-no/pdf/mercedes-amg-s-klasse-ekstra-instruksjonsbok-mars-2020-1.pdf
EU-MERCEDES-AMG-S-CLASS-C217-S63-COUPE-FACELIFT-01	5051	1913	1428	Mercedes-Benz Mercedes-AMG S-Class supplemental owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/no-no/pdf/mercedes-amg-s-klasse-ekstra-instruksjonsbok-mars-2020-1.pdf
EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	5032	1899	1414	Automobile-Catalog Mercedes-Benz S 450 4MATIC Coupe Europe;Automobile-Catalog Mercedes-Benz S 560 4MATIC Coupe Europe	https://www.automobile-catalog.com/car/2017/2602985/mercedes-benz_s_450_4matic_coupe.html;https://www.automobile-catalog.com/car/2017/2603015/mercedes-benz_s_560_4matic_coupe.html
EU-MERCEDES-BENZ-S-CLASS-A217-CONVERTIBLE-FACELIFT-01	5032	1899	1420	Automobile-Catalog Mercedes-Benz S 560 Cabriolet Europe	https://www.automobile-catalog.com/car/2018/2603075/mercedes-benz_s_560_cabriolet.html
EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	4384	1725	1450	Kia Media 2018 Rio official specifications	https://www.kiamedia.com/us/en/models/rio/2018/specifications
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467	Volkswagen South Africa Polo Sedan official specifications	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/passenger-vehicles/2021/september/polo-sedan-online-brochure-my22.pdf
```

## 下一步优先处理

1. 闭合 Suzuki Jimny Cabrio 的生产阶段和外廓分支。
2. 处理 Ford Escort VI Sedan/Wagon、Aerostar与Transit。
3. 拆分 Fiat Ducato Bus、Van、Chassis Cab及4×4长度和车顶组合。
4. 处理 Mercedes-Benz G 300、Partner/Berlingo商用车分支。

推进信号：CONTINUE

[1]: https://www.kiamedia.com/us/en/models/rio/2018/specifications?utm_source=chatgpt.com "2018 Kia Rio Specifications"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
## 更新点

* 闭合 Ford Aerostar E-4WD Extended、Mercedes-Benz G 300 W463 SWB/LWB，以及 Ford Escort VI Sedan/Wagon，共 **4 个 Ktype、5 条映射**。
* 首次创建 **5 个 DIMENSION_GROUP**。Aerostar AWD 对应加长车身；G 300 明确拆分短轴三门与长轴五门；Escort VI 按 Sedan 和 Turnier 分组。([Edmunds][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* PENDING Ktype：13
* READY 映射：153
* 当前引用的已确认尺寸组：74
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129063	129063	MPV	Aerostar I	VN1		EU-FORD-AEROSTAR-VN1-MPV-E4WD-EXTENDED-01	HIGH	E-4WD加长车身外廓。	READY
129165_swb	129165	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
129165_lwb	129165	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
129250	129250	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH		READY
129252	129252	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-AEROSTAR-VN1-MPV-E4WD-EXTENDED-01	4834	1821	1851	Automobile-Catalog 1994 Ford Aerostar XLT E-4WD Extended	https://www.automobile-catalog.com/car/1994/1501685/ford_aerostar_xlt_e-4wd_extended_4_0l_v-6_automatic.html
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	4185	1690	1908	Auto-Data Mercedes-Benz G-Class W463 G 300 SWB	https://www.auto-data.net/en/mercedes-benz-g-class-w463-g-300-170hp-4matic-42310
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4635	1690	1936	Auto-Data Mercedes-Benz G-Class Long W463 G 300	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-g-300-170hp-4matic-automatic-42517
EU-FORD-ESCORT-VI-GAL-WAGON-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier GAL	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397	Auto-Data Ford Escort VI GAL	https://www.auto-data.net/en/ford-escort-vi-gal-1.4-71hp-7423
```

## 下一步优先处理

1. 解决 Suzuki Jimny Cabrio 改款前后保险杠造成的长度分支，并闭合3个Ktype。
2. 拆分 Fiat Ducato Bus、Van及Chassis Cab的长度、车顶和4×4组合。
3. 处理 Ford Transit Van以及Peugeot Partner/Citroën Berlingo商用车分支。

推进信号：CONTINUE

[1]: https://www.edmunds.com/ford/aerostar/1997/features-specs/?utm_source=chatgpt.com "Used 1997 Ford Aerostar Specs & Features | Edmunds"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / checkpoint 续跑 ---
## 更新点

* 闭合 Peugeot Partner II B9 的 L1/L2 Van、标准 Tepee 和高车身 Tepee 四个物理分支。
* 闭合 Suzuki Jimny III 的早期 Cabrio、JB43 Cabrio，以及 2012 facelift 硬顶车身；Ktype `129108` 的输入开放式标记已按 2013 年 1.3 4WD 量产硬顶资料纠正。([汽车数据网][1])
* 闭合 Citroën Berlingo II B9 Platform Cab。Peugeot 与 Citroën 资料均明确给出不含后视镜宽度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* PENDING Ktype：8
* READY 映射：161
* 当前引用的已确认尺寸组：82
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
129078_van_l1	129078	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车物理分支。	READY
129078_van_l2	129078	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2加长厢式车物理分支。	READY
129078_mpv_standard	129078	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	MEDIUM	标准高度Tepee物理分支。	READY
129078_mpv_outdoor	129078	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	MEDIUM	高车身Tepee物理分支。	READY
129105	129105	Convertible	Jimny III	JB33	3	EU-SUZUKI-JIMNY-III-JB33-CONVERTIBLE-PREFL-01	HIGH	早期Canvas Top物理外廓。	READY
129107	129107	Convertible	Jimny III	JB43	3	EU-SUZUKI-JIMNY-III-JB43-CONVERTIBLE-01	HIGH	JB43 Canvas Top物理外廓。	READY
129108	129108	SUV	Jimny III facelift	JB43	3	EU-SUZUKI-JIMNY-III-JB43-SUV-FACELIFT-2012-01	HIGH	输入开放式标记与2013量产资料冲突；按1.3 4WD硬顶车身闭合。	READY
129210	129210	Chassis Cab	Berlingo II	B9	2	EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	Platform Cab物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828	Peugeot Partner Van official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-partner-prices-specifications-brochure-08-2018.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner Van official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-partner-prices-specifications-brochure-08-2018.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801	Peugeot Partner Tepee official dimensions guide	https://www.autoeurope.no/peugeotfleet/documents/partner-dimensions.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862	Peugeot Partner Tepee official dimensions guide	https://www.autoeurope.no/peugeotfleet/documents/partner-dimensions.pdf
EU-SUZUKI-JIMNY-III-JB33-CONVERTIBLE-PREFL-01	3625	1600	1655	Auto-Data Suzuki Jimny Cabrio III 1.3 16V 80 Hp 4WD	https://www.auto-data.net/en/suzuki-jimny-cabrio-iii-1.3-16v-80hp-4wd-16460
EU-SUZUKI-JIMNY-III-JB43-CONVERTIBLE-01	3625	1600	1665	Automobile-Catalog Suzuki Jimny Cabrio 1.3 4WD Europe	https://www.automobile-catalog.com/car/2007/3394025/suzuki_jimny_cabrio_1_3_4wd.html
EU-SUZUKI-JIMNY-III-JB43-SUV-FACELIFT-2012-01	3675	1600	1705	Suzuki Jimny official brochure;Automobile-Catalog Suzuki Jimny 1.3 4WD Europe	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Jimny-2013-AU.pdf;https://www.automobile-catalog.com/car/2013/3394355/suzuki_jimny_1_3_4wd.html
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822	Citroën Berlingo official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Citroen-Berlingo-UK.pdf
```

## 下一步优先处理

1. 一次性闭合 Fiat Ducato X250/X290 Bus、Van和Chassis Cab的长度、车顶及4×4分支。
2. 闭合 Ford Transit V184 RWD 2.3 Bi-fuel的SWB、MWB、LWB及对应车顶分支。
3. PENDING 清零后立即进行一次机械收尾并输出两张最终完整TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/suzuki-jimny-cabrio-iii-1.3-16v-80hp-4wd-16460 "Suzuki Jimny Cabrio III 1.3 16V (80 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 **5 个 Ktype、18 条映射**：Fiat Ducato 130 4×4 Bus/Van、Ducato 110 前驱 Bus/Van，以及 Ford Transit 2.3 Bi-fuel Van。
* 首次创建 **16 个 DIMENSION_GROUP**。
* Ford 官方车型资料确认 2.3 Petrol/LPG 后驱版本覆盖 SWB、MWB、LWB 的对应车顶分支，并给出不含后视镜宽度。
* Fiat 官方价格表和乘用运输资料闭合 Ducato 110 的 L1/L2 Bus 与 Van 分支；Ducato-Dangel 130 4×4 分支按瑞士型式批准记录闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射：179
* 当前引用的已确认尺寸组：98
* 本轮首次创建尺寸组：16
* 剩余 PENDING：`128964`、`128967`、`129241`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128963	128963	MPV	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	MEDIUM	七座L3H2四驱Bus外廓。	READY
128966_l1h1	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	MEDIUM	L1H1四驱厢式车分支。	READY
128966_l2h1	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	MEDIUM	L2H1四驱厢式车分支。	READY
128966_l3h2	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	MEDIUM	L3H2四驱厢式车分支。	READY
128966_l3h3	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	MEDIUM	L3H3四驱厢式车分支。	READY
128966_l4h2	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	MEDIUM	L4H2四驱厢式车分支。	READY
129077_swb_lowroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
129077_swb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-SWB-MIDROOF-01	HIGH	SWB中顶物理分支。	READY
129077_mwb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-MWB-MIDROOF-01	HIGH	MWB中顶物理分支。	READY
129077_mwb_highroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
129077_lwb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-LWB-MIDROOF-01	HIGH	LWB中顶物理分支。	READY
129077_lwb_highroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶物理分支。	READY
129239_l1h1	129239	MPV	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H1-01	HIGH	L1H1乘用运输车分支。	READY
129239_l2h2	129239	MPV	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H2-01	HIGH	L2H2乘用运输车分支。	READY
129240_l1h1	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H1-01	HIGH	L1H1厢式车分支。	READY
129240_l1h2	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H2-01	HIGH	L1H2厢式车分支。	READY
129240_l2h1	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H1-01	HIGH	L2H1厢式车分支。	READY
129240_l2h2	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H2-01	HIGH	L2H2厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	5998	2050	2524	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	4963	2050	2254	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	5413	2050	2254	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	5998	2050	2522	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	5998	2050	2760	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	6363	2050	2522	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FORD-TRANSIT-V184-VAN-SWB-LOWROOF-01	4834	1974	2033	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-SWB-MIDROOF-01	4834	1974	2368	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-MWB-MIDROOF-01	5201	1974	2353	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-MWB-HIGHROOF-01	5201	1974	2674	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-LWB-MIDROOF-01	5651	1974	2354	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-LWB-HIGHROOF-01	5651	1974	2678	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FIAT-DUCATO-III-X290-L1H1-01	4963	2050	2254	Fiat Professional New Ducato 2014 official price list;Fiat Professional New Ducato Passenger Transport official brochure	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf;https://fiat.autospirit.ee/images/ducato/ducato_soiduauto.pdf
EU-FIAT-DUCATO-III-X290-L1H2-01	4963	2050	2524	Fiat Professional New Ducato 2014 official price list	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf
EU-FIAT-DUCATO-III-X290-L2H1-01	5413	2050	2254	Fiat Professional New Ducato 2014 official price list	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf
EU-FIAT-DUCATO-III-X290-L2H2-01	5413	2050	2524	Fiat Professional New Ducato 2014 official price list;Fiat Professional New Ducato Passenger Transport official brochure	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf;https://fiat.autospirit.ee/images/ducato/ducato_soiduauto.pdf
```

## 下一步优先处理

1. 确认 `128964` 的 150 Multijet 4×4 Bus 可用车长及车顶分支。
2. 确认 `128967` 的 150 Multijet 4×4 Van 是否除已发现的 L2H1 外还覆盖其他外廓。
3. 确认 `129241` 的 110 Multijet X250 Chassis Cab 可用轴距及单排/双排驾驶室范围。
4. 三项闭合后立即进行一次机械收尾并输出完整最终 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / checkpoint 续跑 ---
## 更新点

* 剩余 `128964`、`128967`、`129241` 已全部闭合。
* `128964`、`128967` 复用已确认的 Fiat Ducato Dangel 4×4 尺寸组，没有重复建组。
* `129241` 完成单排/双排驾驶室共 8 个物理分支，并首次创建对应尺寸组。
* 已完成机械校验：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源字段完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：193
* 最终 DIMENSION_GROUP：106
* 机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128960_scab_l3	128960	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128960_scab_l4	128960	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128960_dcab_l3	128960	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128960_dcab_l4	128960	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128961_scab_l3	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128961_scab_l4	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128961_scab_l5	128961	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
128961_dcab_l3	128961	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128961_dcab_l4	128961	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128962_l3h2	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128962_l3h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128962_l4h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128962_l4h4	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128962_l5h3	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128962_l5h4	128962	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
128963	128963	MPV	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	MEDIUM	七座L3H2四驱Bus外廓。	READY
128964	128964	MPV	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	MEDIUM	七座L3H2四驱Bus外廓。	READY
128966_l1h1	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	MEDIUM	L1H1四驱厢式车分支。	READY
128966_l2h1	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	MEDIUM	L2H1四驱厢式车分支。	READY
128966_l3h2	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	MEDIUM	L3H2四驱厢式车分支。	READY
128966_l3h3	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	MEDIUM	L3H3四驱厢式车分支。	READY
128966_l4h2	128966	Van	Ducato III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	MEDIUM	L4H2四驱厢式车分支。	READY
128967_l1h1	128967	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	MEDIUM	L1H1四驱厢式车分支。	READY
128967_l2h1	128967	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	MEDIUM	L2H1四驱厢式车分支。	READY
128967_l3h2	128967	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	MEDIUM	L3H2四驱厢式车分支。	READY
128967_l3h3	128967	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	MEDIUM	L3H3四驱厢式车分支。	READY
128967_l4h2	128967	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	MEDIUM	L4H2四驱厢式车分支。	READY
128972	128972	Hatchback	C3 I facelift		5	EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	HIGH		READY
128973	128973	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	改款前轿车物理外廓。	READY
128974	128974	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
128976	128976	Coupe	718 982	982	2	EU-PORSCHE-718-982-CAYMAN-GTS-COUPE-01	HIGH		READY
128977	128977	Convertible	718 982	982	2	EU-PORSCHE-718-982-BOXSTER-GTS-CONVERTIBLE-01	HIGH		READY
128979_l3h2	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128979_l3h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128979_l4h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128979_l4h4	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128979_l5h3	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128979_l5h4	128979	Van	TGE I			EU-MAN-TGE-I-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
128980_l3h2	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
128980_l3h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
128980_l4h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
128980_l4h4	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
128980_l5h3	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
128980_l5h4	128980	Van	TGE I			EU-MAN-TGE-I-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
128981_scab_l3	128981	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128981_scab_l4	128981	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128981_dcab_l3	128981	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128981_dcab_l4	128981	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
128982_scab_l3	128982	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
128982_scab_l4	128982	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
128982_dcab_l3	128982	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
128982_dcab_l4	128982	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129005	129005	Convertible	S-Class A217 facelift	A217	2	EU-MERCEDES-AMG-S-CLASS-A217-S63-CONVERTIBLE-FACELIFT-01	HIGH	AMG S 63 Cabriolet外廓。	READY
129007	129007	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-AMG-S-CLASS-C217-S63-COUPE-FACELIFT-01	HIGH	AMG S 63 Coupe外廓。	READY
129009	129009	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129010	129010	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129011	129011	Coupe	S-Class C217 facelift	C217	2	EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	HIGH	普通版Coupe外廓。	READY
129012	129012	Convertible	S-Class A217 facelift	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-CONVERTIBLE-FACELIFT-01	HIGH	普通版Cabriolet外廓。	READY
129013	129013	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH		READY
129015	129015	SUV	Kuga II facelift	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
129028	129028	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
129029	129029	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
129030	129030	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	HIGH	改款前Cooper S敞篷外廓。	READY
129032	129032	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129033	129033	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129034	129034	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129035	129035	Van	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-PREFL-01	HIGH	三门商用车身。	READY
129038	129038	Hatchback	Prius III	ZVW35	5	EU-TOYOTA-PRIUS-III-XW30-PLUG-IN-HATCHBACK-01	HIGH		READY
129041	129041	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129046	129046	Sedan	Avalon III	GSX30	4	EU-TOYOTA-AVALON-III-GSX30-SEDAN-01	HIGH		READY
129055	129055	Sedan	Astra G Classic II	T98	4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH		READY
129056	129056	Sedan	Rio IV	YB	4	EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
129059	129059	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	改款前物理外廓。	READY
129060	129060	Sedan	Astra G Classic II	T98	4	EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	HIGH		READY
129062	129062	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129063	129063	MPV	Aerostar I	VN1		EU-FORD-AEROSTAR-VN1-MPV-E4WD-EXTENDED-01	HIGH	E-4WD加长车身外廓。	READY
129065	129065	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129066	129066	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129067	129067	Sedan	Polo V Sedan facelift	602	4	EU-VW-POLO-V-602-SEDAN-FACELIFT-01	HIGH	Polo V四门轿车改款外廓。	READY
129069	129069	Hatchback	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	HIGH		READY
129072	129072	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129075	129075	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129076	129076	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129077_swb_lowroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
129077_swb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-SWB-MIDROOF-01	HIGH	SWB中顶物理分支。	READY
129077_mwb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-MWB-MIDROOF-01	HIGH	MWB中顶物理分支。	READY
129077_mwb_highroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
129077_lwb_midroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-LWB-MIDROOF-01	HIGH	LWB中顶物理分支。	READY
129077_lwb_highroof	129077	Van	Transit V184	V184		EU-FORD-TRANSIT-V184-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶物理分支。	READY
129078_van_l1	129078	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车物理分支。	READY
129078_van_l2	129078	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2加长厢式车物理分支。	READY
129078_mpv_standard	129078	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	MEDIUM	标准高度Tepee物理分支。	READY
129078_mpv_outdoor	129078	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	MEDIUM	高车身Tepee物理分支。	READY
129081	129081	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	HIGH	GTI专用保险杠及降低车身外廓。	READY
129082	129082	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
129087	129087	Wagon	Astra G Classic II	T98	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	HIGH		READY
129088	129088	Wagon	Astra H Family	A04	5	EU-OPEL-ASTRA-H-FAMILY-WAGON-01	HIGH		READY
129091	129091	Hatchback	Astra H Family	A04	5	EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	HIGH		READY
129092	129092	Sedan	Astra H Family	A04	4	EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	HIGH		READY
129093	129093	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
129101	129101	Hatchback	Punto Evo	199	3	EU-ABARTH-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	Abarth宽体外廓。	READY
129105	129105	Convertible	Jimny III	JB33	3	EU-SUZUKI-JIMNY-III-JB33-CONVERTIBLE-PREFL-01	HIGH	早期Canvas Top物理外廓。	READY
129107	129107	Convertible	Jimny III	JB43	3	EU-SUZUKI-JIMNY-III-JB43-CONVERTIBLE-01	HIGH	JB43 Canvas Top物理外廓。	READY
129108	129108	SUV	Jimny III facelift	JB43	3	EU-SUZUKI-JIMNY-III-JB43-SUV-FACELIFT-2012-01	HIGH	输入开放式标记与2013量产资料冲突；按1.3 4WD硬顶车身闭合。	READY
129115	129115	Sedan	3 Series F80	F80	4	EU-BMW-3-F80-M3-CS-SEDAN-01	HIGH		READY
129118	129118	Hatchback	MINI F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH		READY
129119	129119	Hatchback	MINI F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH		READY
129121	129121	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-ONE-01	HIGH		READY
129125	129125	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-ONE-01	HIGH		READY
129127	129127	Convertible	MINI F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	HIGH		READY
129130	129130	SUV	Stelvio	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
129160	129160	SUV	DS 7 Crossback I		5	EU-DS-DS7-CROSSBACK-I-SUV-01	HIGH		READY
129165_swb	129165	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
129165_lwb	129165	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
129166_l3h2	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129166_l3h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129166_l4h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129166_l4h4	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129166_l5h3	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129166_l5h4	129166	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129169	129169	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
129170	129170	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	HIGH		READY
129171	129171	Hatchback	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	HIGH		READY
129172	129172	Sedan	Focus III facelift	DYB	4	EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	HIGH		READY
129174_l3h2	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129174_l3h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129174_l4h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129174_l4h4	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129174_l5h3	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129174_l5h4	129174	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129177_scab_l3	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129177_scab_l4	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129177_scab_l5	129177	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129177_dcab_l3	129177	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129177_dcab_l4	129177	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129180	129180	Coupe	911 991.2	991.2	2	EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	HIGH		READY
129185	129185	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo Sport Turismo物理外廓。	READY
129187	129187	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
129195_l3h2	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	L3H2厢式车物理分支。	READY
129195_l3h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	L3H3厢式车物理分支。	READY
129195_l4h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	L4H3厢式车物理分支。	READY
129195_l4h4	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	L4H4厢式车物理分支。	READY
129195_l5h3	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	L5H3厢式车物理分支。	READY
129195_l5h4	129195	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	L5H4厢式车物理分支。	READY
129196_scab_l3	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129196_scab_l4	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129196_scab_l5	129196	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129196_dcab_l3	129196	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129196_dcab_l4	129196	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129197_scab_l3	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129197_scab_l4	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129197_scab_l5	129197	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129197_dcab_l3	129197	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129197_dcab_l4	129197	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129198_scab_l3	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129198_scab_l4	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129198_scab_l5	129198	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	MEDIUM	单排驾驶室L5物理分支。	READY
129198_dcab_l3	129198	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129198_dcab_l4	129198	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129201_scab_l3	129201	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129201_scab_l4	129201	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129201_dcab_l3	129201	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129201_dcab_l4	129201	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129202	129202	Van	Punto Evo	199	3	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	三门商用Van与Punto 199同外廓。	READY
129203	129203	Van	Punto Evo	199	3	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	三门商用Van与Punto 199同外廓。	READY
129204_scab_l3	129204	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	单排驾驶室L3物理分支。	READY
129204_scab_l4	129204	Chassis Cab	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	单排驾驶室L4物理分支。	READY
129204_dcab_l3	129204	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	双排驾驶室L3物理分支。	READY
129204_dcab_l4	129204	Chassis Cab	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	双排驾驶室L4物理分支。	READY
129205	129205	Hatchback	Leon III facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH	Cupra R五门物理外廓。	READY
129206	129206	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
129210	129210	Chassis Cab	Berlingo II	B9	2	EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	Platform Cab物理外廓。	READY
129219	129219	Convertible	DS3 I Cabrio		2	EU-CITROEN-DS3-I-CABRIO-RACING-CONVERTIBLE-01	HIGH	Racing Cabrio物理外廓。	READY
129222	129222	Sedan	Malibu VIII	V300	4	EU-CHEVROLET-MALIBU-VIII-V300-SEDAN-01	HIGH	欧洲市场V300轿车外廓。	READY
129223	129223	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
129225	129225	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-01	HIGH		READY
129239_l1h1	129239	MPV	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H1-01	HIGH	L1H1乘用运输车分支。	READY
129239_l2h2	129239	MPV	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H2-01	HIGH	L2H2乘用运输车分支。	READY
129240_l1h1	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H1-01	HIGH	L1H1厢式车分支。	READY
129240_l1h2	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L1H2-01	HIGH	L1H2厢式车分支。	READY
129240_l2h1	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H1-01	HIGH	L2H1厢式车分支。	READY
129240_l2h2	129240	Van	Ducato III facelift	X290		EU-FIAT-DUCATO-III-X290-L2H2-01	HIGH	L2H2厢式车分支。	READY
129241_scab_ch1	129241	Chassis Cab	Ducato III	X250	2	EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-CH1-01	MEDIUM	单排驾驶室CH1物理分支。	READY
129241_scab_mh1	129241	Chassis Cab	Ducato III	X250	2	EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MH1-01	MEDIUM	单排驾驶室MH1物理分支。	READY
129241_scab_mlh1	129241	Chassis Cab	Ducato III	X250	2	EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MLH1-01	MEDIUM	单排驾驶室MLH1物理分支。	READY
129241_scab_lh1	129241	Chassis Cab	Ducato III	X250	2	EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-LH1-01	MEDIUM	单排驾驶室LH1物理分支。	READY
129241_scab_xlh1	129241	Chassis Cab	Ducato III	X250	2	EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-XLH1-01	MEDIUM	单排驾驶室XLH1物理分支。	READY
129241_dcab_mh1	129241	Chassis Cab	Ducato III	X250	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	MEDIUM	双排驾驶室MH1物理分支。	READY
129241_dcab_lh1	129241	Chassis Cab	Ducato III	X250	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	MEDIUM	双排驾驶室LH1物理分支。	READY
129241_dcab_xlh1	129241	Chassis Cab	Ducato III	X250	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	MEDIUM	双排驾驶室XLH1物理分支。	READY
129250	129250	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH		READY
129252	129252	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH		READY
129253	129253	Convertible	Portofino	F164	2	EU-FERRARI-PORTOFINO-F164-CONVERTIBLE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1801-1900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305	Volkswagen Crafter official chassis cab brochure	https://www.volkswagenvans.ie/idhub/content/dam/onehub_nfz/importers/ie/models/downloads/my26/Crafter%20Chassis%20Cab%20Dropside%20Brochure.pdf
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305	Volkswagen Crafter official chassis cab brochure	https://www.volkswagenvans.ie/idhub/content/dam/onehub_nfz/importers/ie/models/downloads/my26/Crafter%20Chassis%20Cab%20Dropside%20Brochure.pdf
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321	Volkswagen Crafter official chassis cab brochure	https://www.volkswagenvans.ie/idhub/content/dam/onehub_nfz/importers/ie/models/downloads/my26/Crafter%20Chassis%20Cab%20Dropside%20Brochure.pdf
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321	Volkswagen Crafter official chassis cab brochure	https://www.volkswagenvans.ie/idhub/content/dam/onehub_nfz/importers/ie/models/downloads/my26/Crafter%20Chassis%20Cab%20Dropside%20Brochure.pdf
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Crafter official body-builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Crafter/Body-builder-guidelines-Crafter-EN-48-2023_01.pdf
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	5998	2050	2524	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	4963	2050	2254	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	5413	2050	2254	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	5998	2050	2522	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	5998	2050	2760	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	6363	2050	2522	Motoro Swiss type-approval data for Fiat-Dangel Ducato 4x4	https://motoro.ch/en/fiche-technique/fiat-dangel/ducato-4x4-2-3
EU-CITROEN-C3-I-FACELIFT-HATCHBACK-5D-01	3860	1667	1510	Automobile-Catalog Citroen C3 1.1i Style Europe	https://www.automobile-catalog.com/car/2006/548495/citroen_c3_1_1i_style.html
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456	Volkswagen UK Passat official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/arona/cars-specs-brochure-KJ7-NA-december-2018.pdf
EU-PORSCHE-718-982-CAYMAN-GTS-COUPE-01	4379	1801	1286	Porsche 718 Cayman GTS technical data;Automobile-Catalog Porsche 718 Cayman GTS Europe	https://newsroom.porsche.com/dam/jcr%3Afbd80b62-5236-4ff6-9f1b-e54ee42f6f7c/PCNA18_0996_us.pdf;https://www.automobile-catalog.com/car/2017/2872385/porsche_718_cayman_gts.html
EU-PORSCHE-718-982-BOXSTER-GTS-CONVERTIBLE-01	4379	1801	1272	Porsche 718 Boxster GTS technical data;Automobile-Catalog Porsche 718 Boxster GTS Europe	https://newsroom.porsche.com/dam/jcr%3A59fc370f-12ba-438a-a85c-2ce0bf4442a9/PCNA18_1002_718BoxsterGTS-technical-specifications.pdf;https://www.automobile-catalog.com/car/2017/2872355/porsche_718_boxster_gts.html
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H4-01	6836	2040	2798	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L5H3-01	7391	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L5H4-01	7391	2040	2798	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MERCEDES-AMG-S-CLASS-A217-S63-CONVERTIBLE-FACELIFT-01	5051	1913	1428	Mercedes-Benz Mercedes-AMG S-Class supplemental owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/no-no/pdf/mercedes-amg-s-klasse-ekstra-instruksjonsbok-mars-2020-1.pdf
EU-MERCEDES-AMG-S-CLASS-C217-S63-COUPE-FACELIFT-01	5051	1913	1428	Mercedes-Benz Mercedes-AMG S-Class supplemental owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/no-no/pdf/mercedes-amg-s-klasse-ekstra-instruksjonsbok-mars-2020-1.pdf
EU-MERCEDES-BENZ-S-CLASS-C217-COUPE-FACELIFT-01	5032	1899	1414	Automobile-Catalog Mercedes-Benz S 450 4MATIC Coupe Europe;Automobile-Catalog Mercedes-Benz S 560 4MATIC Coupe Europe	https://www.automobile-catalog.com/car/2017/2602985/mercedes-benz_s_450_4matic_coupe.html;https://www.automobile-catalog.com/car/2017/2603015/mercedes-benz_s_560_4matic_coupe.html
EU-MERCEDES-BENZ-S-CLASS-A217-CONVERTIBLE-FACELIFT-01	5032	1899	1420	Automobile-Catalog Mercedes-Benz S 560 Cabriolet Europe	https://www.automobile-catalog.com/car/2018/2603075/mercedes-benz_s_560_cabriolet.html
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Ford EcoSport official brochure	https://www.nl.ford.be/content/dam/guxeu/be/nl_be/documents/brochures/feature-pdfs/FT-New_EcoSport.pdf
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Automobile-Catalog Ford Kuga 2.0 TDCi Europe	https://www.automobile-catalog.com/car/2017/2455610/ford_kuga_2_0_tdci_150_2x4.html
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685	Mitsubishi Motors Eclipse Cross Geneva 2017 official specifications	https://media.mitsubishicars.com/releases/mitsubishi-motors-to-globally-premiere-eclipse-cross-compact-suv-at-geneva-international-motor-show-2017
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414	BMW Group PressClub MINI Cooper S Convertible technical specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0031660EN/52392
EU-BMW-X2-F39-SUV-01	4360	1824	1526	BMW Group PressClub BMW X2 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0285189EN/414886
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-PREFL-01	4030	1687	1490	Automobile-Catalog Fiat Grande Punto 1.3 Multijet 75 Europe	https://www.automobile-catalog.com/car/2006/728030/fiat_grande_punto_1_3_multijet_16v_75_dynamic.html
EU-TOYOTA-PRIUS-III-XW30-PLUG-IN-HATCHBACK-01	4480	1745	1490	Toyota Europe Prius Plug-in Hybrid technical data	https://newsroom.toyota.eu/2019-2014-toyota-geneva-motor-show-prius-plug-in-hybrid---towards-the-ultimate-eco-car/
EU-TOYOTA-AVALON-III-GSX30-SEDAN-01	5009	1849	1486	Toyota 2006 Avalon official eBrochure	https://www.auto-brochures.com/makes/Toyota/Avalon/Toyota_US%20Avalon_2006.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	4384	1725	1450	Kia Media 2018 Rio official specifications	https://www.kiamedia.com/us/en/models/rio/2018/specifications
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450	Volkswagen UK Arteon official price and specification guide	https://www.vwpress.co.uk/assets/documents/original/1826-New_Arteon_price_list_8_8_17_1.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-FORD-AEROSTAR-VN1-MPV-E4WD-EXTENDED-01	4834	1821	1851	Automobile-Catalog 1994 Ford Aerostar XLT E-4WD Extended	https://www.automobile-catalog.com/car/1994/1501685/ford_aerostar_xlt_e-4wd_extended_4_0l_v-6_automatic.html
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467	Volkswagen South Africa Polo Sedan official specifications	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/passenger-vehicles/2021/september/polo-sedan-online-brochure-my22.pdf
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465	General Motors Poland Opel Astra Classic II official technical data	https://dixi-car.pl/doc/opel-astra-classic-dane.pdf
EU-FORD-TRANSIT-V184-VAN-SWB-LOWROOF-01	4834	1974	2033	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-SWB-MIDROOF-01	4834	1974	2368	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-MWB-MIDROOF-01	5201	1974	2353	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-MWB-HIGHROOF-01	5201	1974	2674	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-LWB-MIDROOF-01	5651	1974	2354	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-V184-VAN-LWB-HIGHROOF-01	5651	1974	2678	Ford Panel Vans official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Panel-Vans-Specs-UK.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828	Peugeot Partner Van official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-partner-prices-specifications-brochure-08-2018.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner Van official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-partner-prices-specifications-brochure-08-2018.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801	Peugeot Partner Tepee official dimensions guide	https://www.autoeurope.no/peugeotfleet/documents/partner-dimensions.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862	Peugeot Partner Tepee official dimensions guide	https://www.autoeurope.no/peugeotfleet/documents/partner-dimensions.pdf
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438	Volkswagen UK new Polo official brochure;Auto-Data Volkswagen Polo VI GTI 2.0 TSI DSG	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/polo/polo-nf/polo-nf-brochure-dec-2017.pdf;https://www.auto-data.net/en/volkswagen-polo-vi-gti-2.0-tsi-200hp-dsg-32275
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	SEAT Ibiza official specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/ibiza/cars-specs-brochure-KJ1-NA-january-2019.pdf
EU-OPEL-ASTRA-H-FAMILY-WAGON-01	4515	1753	1500	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
EU-OPEL-ASTRA-H-FAMILY-HATCHBACK-5D-01	4249	1753	1460	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
EU-OPEL-ASTRA-H-FAMILY-SEDAN-01	4587	1753	1458	Opel Astra H official owner's manual	https://public-servicebox.opel.com/OVddb/OV/zh_CN/Astra_H/2010_2016/2012/manual_user/om_astra_2584_17_eu_my12_ed0811_9_zh_CN_online.pdf
EU-ABARTH-PUNTO-EVO-199-HATCHBACK-3D-01	4065	1721	1490	Auto-Data Abarth Punto Evo 199	https://www.auto-data.net/en/abarth-punto-model-3182
EU-SUZUKI-JIMNY-III-JB33-CONVERTIBLE-PREFL-01	3625	1600	1655	Auto-Data Suzuki Jimny Cabrio III 1.3 16V 80 Hp 4WD	https://www.auto-data.net/en/suzuki-jimny-cabrio-iii-1.3-16v-80hp-4wd-16460
EU-SUZUKI-JIMNY-III-JB43-CONVERTIBLE-01	3625	1600	1665	Automobile-Catalog Suzuki Jimny Cabrio 1.3 4WD Europe	https://www.automobile-catalog.com/car/2007/3394025/suzuki_jimny_cabrio_1_3_4wd.html
EU-SUZUKI-JIMNY-III-JB43-SUV-FACELIFT-2012-01	3675	1600	1705	Suzuki Jimny official brochure;Automobile-Catalog Suzuki Jimny 1.3 4WD Europe	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Jimny-2013-AU.pdf;https://www.automobile-catalog.com/car/2013/3394355/suzuki_jimny_1_3_4wd.html
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424	BMW Group PressClub M3 CS technical data	https://www.press.bmwgroup.com/global/article/attachment/T0275597EN/408532/M3_CS_Technical_Data_E.pdf
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425	BMW Group PressClub MINI 5 door technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274783EN/397685
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414	BMW Group PressClub MINI 3 door technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0284470CS/413623
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415	BMW Group PressClub MINI Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0284420EN/413748
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Alfa Romeo Stelvio Quadrifoglio official brochure	https://www.media.stellantis.com/uploads/uk/UK/2018/Alfa_Romeo/Press/Alfa_Romeo_Stelvio_Quadrifoglio_brochure.pdf
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620	DS 7 CROSSBACK official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds7crossbackpricesandspecs-6172c7be26ee3.pdf
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	4185	1690	1908	Auto-Data Mercedes-Benz G-Class W463 G 300 SWB	https://www.auto-data.net/en/mercedes-benz-g-class-w463-g-300-170hp-4matic-42310
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4635	1690	1936	Auto-Data Mercedes-Benz G-Class Long W463 G 300	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-g-300-170hp-4matic-automatic-42517
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Vauxhall Crossland X launch specifications archive	https://a3.myautoworld.com/36921/
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505	Ford New Focus official brochure	https://www.forddealers.co.nz/i/files/FordFocus_Brochure.pdf
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484	Ford South Africa New Focus Q1 2018 official brochure	https://www.ford.co.za/content/dam/Ford/website-assets/latam/za/nameplate/focus/brochure/Focus-Brochure-Q1-2018_EBrochure.pdf
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484	Ford South Africa New Focus Q1 2018 official brochure	https://www.ford.co.za/content/dam/Ford/website-assets/latam/za/nameplate/focus/brochure/Focus-Brochure-Q1-2018_EBrochure.pdf
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297	Porsche Goodwood 2017 official technical data	https://newsroom.porsche.com/dam/jcr%3A914d7fe5-dc87-415e-9bee-8fee16daa804/Goodwood_2017_DE_EN_V4.pdf
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432	Porsche Panamera Sport Turismo official press release	https://www.porsche.com/usa/aboutporsche/pressreleases/pag/?id=425281&pool=international-de
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490	Fiat Punto Evo official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Fiat-Punto-2010-UK.pdf
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	SEAT Leon official specifications brochure	https://www.seat.ps/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/cars-specs-brochure-5F1-NA-december-2018.pdf
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404	Honest John Bentley Continental GT technical specifications	https://www.honestjohn.co.uk/bentley/continental/gt/2010/specs/
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822	Citroen Berlingo official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Citroen-Berlingo-UK.pdf
EU-CITROEN-DS3-I-CABRIO-RACING-CONVERTIBLE-01	3948	1715	1458	Automobile-Catalog Citroen DS3 Cabrio Racing;Auto-Data Citroen DS3 Phase I Cabrio	https://www.automobile-catalog.com/car/2014/2086055/citroen_ds3_cabrio_racing.html;https://www.auto-data.net/en/citroen-ds-3-phase-i-cabrio-generation-4406
EU-CHEVROLET-MALIBU-VIII-V300-SEDAN-01	4865	1855	1465	Automobile-Catalog Chevrolet Malibu 2.0 D LT Europe	https://www.automobile-catalog.com/car/2012/1777610/chevrolet_malibu_2_0_d_lt.html
EU-DODGE-JOURNEY-I-JC-MPV-01	4888	1878	1691	Automobile-Catalog Dodge Journey SXT 2.0 CRD Europe	https://www.automobile-catalog.com/car/2009/1227215/dodge_journey_sxt_2_0l_crd.html
EU-FIAT-DUCATO-III-X290-L1H1-01	4963	2050	2254	Fiat Professional New Ducato 2014 official price list;Fiat Professional New Ducato Passenger Transport official brochure	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf;https://fiat.autospirit.ee/images/ducato/ducato_soiduauto.pdf
EU-FIAT-DUCATO-III-X290-L2H2-01	5413	2050	2524	Fiat Professional New Ducato 2014 official price list;Fiat Professional New Ducato Passenger Transport official brochure	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf;https://fiat.autospirit.ee/images/ducato/ducato_soiduauto.pdf
EU-FIAT-DUCATO-III-X290-L1H2-01	4963	2050	2524	Fiat Professional New Ducato 2014 official price list	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf
EU-FIAT-DUCATO-III-X290-L2H1-01	5413	2050	2254	Fiat Professional New Ducato 2014 official price list	https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-CH1-01	4908	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MH1-01	5358	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MLH1-01	5708	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-LH1-01	5943	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-XLH1-01	6308	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	5358	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	5943	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	6308	2050	2254	Fiat Professional New Ducato converter technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FORD-ESCORT-VI-GAL-WAGON-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier GAL	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397	Auto-Data Ford Escort VI GAL	https://www.auto-data.net/en/ford-escort-vi-gal-1.4-71hp-7423
EU-FERRARI-PORTOFINO-F164-CONVERTIBLE-01	4586	1938	1318	Ferrari Portofino official technical specifications	https://www.ferrari.com/en-EN/auto/ferrari-portofino
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1801-1900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（852 行）
- 累计尺寸组：dimension_groups_final.tsv（458 行）

