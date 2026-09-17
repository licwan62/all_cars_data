# 任务：all 第 8701-8800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0088__f294e46d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8701-8800 行

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
all 第 8701-8800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	3975	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	3995	1616	1370
EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	3995	1616	1370
EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	3890	1590	1370
EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	3926	1590	1370
EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GT-EARLY-01	4190	1660	1330
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	4205	1660	1330
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-16-SHORTNOSE-01	4240	1620	1430
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES1-01	4280	1620	1430
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES2-01	4385	1640	1430
EU-ALFA-ROMEO-ALFETTA-116-SEDAN-SERIES3-01	4410	1640	1430
EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	4140	1560	1430
EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	4160	1560	1430
EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	4080	1580	1315
EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	4187	1842	1353
EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	4198	1842	1358
EU-BMW-1600-GT-COUPE-2D-01	4050	1550	1280
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421
EU-BMW-7-E23-SEDAN-01	4860	1800	1430
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-BMW-X6-E71-SUV-01	4877	1983	1690
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1698	1430
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1698	1430
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505
EU-FORD-FOCUS-I-SEDAN-4D-01	4362	1698	1430
EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	4438	1698	1447
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764
EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	4820	1884	1723
EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	4410	1820	1655
EU-HYUNDAI-IX35-LM-SUV-PREFL-01	4410	1820	1660
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	5158	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	5043	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	5038	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473
EU-MINI-MINI-R53-HATCHBACK-3D-01	3655	1688	1416
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500
EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	4515	1753	1500
EU-SAAB-9-3-II-FACELIFT-CONVERTIBLE-2D-01	4647	1762	1437
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492
EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	4635	1762	1434
EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	4635	1762	1466
EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	4654	1782	1507
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1440
EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	4629	1711	1428
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
KIA	Cee'd	1.6	Schrägheck	Frontantrieb	Benzin	85	115	Sep 2007	Dec 2012	2024-03-01	9809
KIA	Cee'd	1.4	Schrägheck	Frontantrieb	Benzin	77	105	Dec 2006	Dec 2012	2024-03-01	9810
KIA	Venga	1.4 Crdi 75	Schrägheck	Frontantrieb	Diesel	57	78	Feb 2010	Mar 2019	2024-05-01	9814
Hyundai	Veloster	1.6 GDI	Coupe	Frontantrieb	Benzin	103	140	Mar 2011	Dec 2017	2024-03-01	9815
Land Rover	Range rover evoque	2.2 D	SUV	Frontantrieb	Diesel	110	150	Jun 2011	Dec 2019	2024-03-01	9816
Land Rover	Range rover evoque	2.2 D 4X4	SUV	Allrad	Diesel	110	150	Jun 2011	Dec 2019	2024-03-01	9817
Land Rover	Range rover evoque	2.2 D 4X4	SUV	Allrad	Diesel	140	190	May 2011	Dec 2019	2024-03-01	9818
Hyundai	Sonata iv	2.0 16V	Stufenheck	Frontantrieb	Benzin	100	136	Jun 1998	Oct 2001	2024-03-01	9819
Opel	Monterey b	3.5 V6 24V	Geländewagen geschlossen	Allrad	Benzin	158	215	Jul 1998	Aug 1999	2024-03-01	9821
Opel	Monterey b	3.0 DTI	Geländewagen geschlossen	Allrad	Diesel	117	159	Jul 1998	Aug 1999	2024-03-01	9822
Alfa Romeo	1750-2000	2000	Stufenheck	Heckantrieb	Benzin	97	132	Oct 1971	Jul 1975	2024-03-01	9823
Land Rover	Range rover evoque	2.0 4X4	SUV	Allrad	Benzin	177	241	Jun 2011	Dec 2019	2024-03-01	9824
Mitsubishi	I	Miev	Schrägheck	Heckantrieb	Elektro	49	67	Feb 2011	May 2020	2024-03-01	9830
Alfa Romeo	Alfasud	1.3	Kombi	Frontantrieb	Benzin	48	65	Jan 1978	Jul 1979	2024-03-01	9839
Alfa Romeo	Alfetta	2	Coupe	Heckantrieb	Benzin	96	131	Jun 1977	Dec 1984	2024-03-01	9840
Alfa Romeo	Giulia	1300 Super	Coupe	Heckantrieb	Benzin	64	87	Jan 1974	Dec 1978	2024-03-01	9841
Alfa Romeo	Giulia	1600 Super	Coupe	Heckantrieb	Benzin	76	103	Jan 1974	Dec 1978	2024-03-01	9842
Ford	Galaxy ii	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	147	200	Nov 2010	Jun 2015	2024-03-01	9854
BMW	7	730 I, LI	Stufenheck	Heckantrieb	Benzin	190	258	Sep 2009	Jun 2015	2024-03-01	9863
Jeep	Compass	2.2 CRD 4X4	SUV	Allrad	Diesel	120	163	Dec 2010	-	2024-03-01	9867
Mercedes-benz	S-Klasse	S 250 CDI	Stufenheck	Heckantrieb	Diesel	150	204	Jan 2011	Dec 2013	2024-03-01	9869
Mercedes-benz	S-Klasse	S 350 Bluetec	Stufenheck	Heckantrieb	Diesel	190	258	Apr 2011	Dec 2013	2024-03-01	9870
Mercedes-benz	S-Klasse	S 350 Bluetec 4-matic	Stufenheck	Allrad	Diesel	190	258	Apr 2011	Dec 2013	2024-03-01	9871
Mercedes-benz	S-Klasse	S 350 CGI	Stufenheck	Heckantrieb	Benzin	225	306	Apr 2011	Dec 2013	2024-03-01	9872
Mercedes-benz	S-Klasse	S 350 CGI 4-matic	Stufenheck	Allrad	Benzin	225	306	Apr 2011	Dec 2013	2024-03-01	9873
Mercedes-benz	S-Klasse	S 500 CGI	Stufenheck	Heckantrieb	Benzin	320	435	Apr 2011	Dec 2013	2024-03-01	9874
Mercedes-benz	S-Klasse	S 500 CGI 4-matic	Stufenheck	Allrad	Benzin	320	435	Mar 2011	Dec 2013	2024-03-01	9875
Mercedes-benz	S-Klasse	S 63 AMG	Stufenheck	Heckantrieb	Benzin	400	544	Mar 2011	Dec 2013	2024-03-01	9876
BMW	1	M	Coupe	Heckantrieb	Benzin	250	340	Mar 2011	Jun 2012	2024-03-01	9877
Mercedes-benz	S-Klasse	S 65 AMG	Stufenheck	Heckantrieb	Benzin	463	630	Oct 2010	Dec 2013	2024-03-01	9878
Mercedes-benz	C-Klasse	C 200 CDI	Kombi	Heckantrieb	Diesel	100	136	Aug 2010	Aug 2014	2024-03-01	9891
Hyundai	I10 i	1.1	Schrägheck	Frontantrieb	Benzin	51	69	Apr 2011	Dec 2013	2024-03-01	9892
Hyundai	I10 i	1.2	Schrägheck	Frontantrieb	Benzin	63	86	Apr 2011	Dec 2013	2024-03-01	9893
Mini	Mini	Cooper D	Schrägheck	Frontantrieb	Diesel	82	112	Feb 2011	Nov 2013	2024-03-01	9894
Mini	Mini	Cooper SD	Schrägheck	Frontantrieb	Diesel	105	143	Feb 2011	Nov 2013	2024-03-01	9895
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	82	112	Feb 2011	Jun 2014	2024-03-01	9896
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	105	143	Feb 2011	Jun 2014	2024-03-01	9897
Mini	Mini	Cooper D	Cabriolet	Frontantrieb	Diesel	82	112	Feb 2011	May 2015	2024-03-01	9898
Ford	Focus i	2.0 16V	Schrägheck	Frontantrieb	Benzin	96	131	Oct 1998	Nov 2004	2024-03-01	9899
Ford	Focus i	1.8 Turbo DI / Tddi	Schrägheck	Frontantrieb	Diesel	66	90	Oct 1998	Nov 2004	2024-03-01	9900
Audi	Tt	1.8 T	Coupe	Frontantrieb	Benzin	132	180	Oct 1998	Jun 2006	2024-03-01	9901
Audi	Tt	1.8 T Quattro	Coupe	Allrad	Benzin	132	180	Oct 1998	Jun 2006	2024-03-01	9902
Audi	Tt	1.8 T Quattro	Coupe	Allrad	Benzin	165	224	Oct 1998	Jun 2006	2024-03-01	9903
VW	Polo	120 1.6 16V GTI	Schrägheck	Frontantrieb	Benzin	88	120	Sep 1998	Oct 1999	2024-03-01	9904
Mazda	323 s vi	1.3 16V	Stufenheck	Frontantrieb	Benzin	54	73	Sep 1998	Jan 2001	2024-03-01	9905
Mazda	323 s vi	1.5 16V	Stufenheck	Frontantrieb	Benzin	65	88	Sep 1998	Jan 2001	2024-03-01	9906
Mazda	323 f vi	1.3 16V	Schrägheck	Frontantrieb	Benzin	54	73	Sep 1998	Jan 2001	2024-03-01	9907
Mazda	323 f vi	1.5 16V	Schrägheck	Frontantrieb	Benzin	65	88	Sep 1998	Jan 2001	2024-03-01	9908
Mazda	323 f vi	1.9 16V	Schrägheck	Frontantrieb	Benzin	84	114	Sep 1998	Jan 2001	2024-03-01	9909
Mazda	323 s vi	2.0 D	Stufenheck	Frontantrieb	Diesel	52	71	Sep 1998	May 2004	2024-03-01	9910
Mazda	323 s vi	2.0 TD	Stufenheck	Frontantrieb	Diesel	66	90	Sep 1998	May 2004	2024-03-01	9911
Mazda	323 f vi	2.0 D	Schrägheck	Frontantrieb	Diesel	52	71	Sep 1998	May 2004	2024-03-01	9912
Mazda	323 f vi	2.0 TD	Schrägheck	Frontantrieb	Diesel	66	90	Sep 1998	Dec 2001	2024-03-01	9913
Mercedes-benz	Clk	CLK 430	Cabriolet	Heckantrieb	Benzin	205	279	Sep 1998	Mar 2002	2024-03-01	9914
Mini	Mini	Cooper SD	Cabriolet	Frontantrieb	Diesel	105	143	Jun 2009	May 2015	2024-03-01	9915
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	82	112	Mar 2011	Oct 2016	2024-03-01	9916
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	105	143	Mar 2011	Oct 2016	2024-03-01	9917
Mini	Mini	Cooper SD All4	Kombi	Allrad	Diesel	105	143	Mar 2011	Oct 2016	2024-03-01	9918
FSO	125p	1.3 1300	Stufenheck	Heckantrieb	Benzin	47	64	Oct 1967	Aug 1992	2024-03-01	9919
FSO	125p	1.5 1500	Stufenheck	Heckantrieb	Benzin	55	75	Oct 1967	Aug 1992	2024-03-01	9920
FSO	125p	1.3	Kombi	Heckantrieb	Benzin	47	64	Oct 1967	Aug 1992	2024-03-01	9921
FSO	126p	0.6	Schrägheck	Heckantrieb	Benzin	22	30	Jul 1977	Dec 1991	2024-03-01	9922
FSO	132p	1.6	Stufenheck	Heckantrieb	Benzin	72	98	Jan 1974	Sep 1978	2024-03-01	9923
FSO	125p	1.5	Kombi	Heckantrieb	Benzin	55	75	Oct 1967	Aug 1992	2024-03-01	9924
FSO	127p	0.9	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1969	Oct 1976	2024-03-01	9925
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	82	112	Mar 2011	Oct 2016	2024-03-01	9926
FSO	132p	1.8	Stufenheck	Heckantrieb	Benzin	79	107	Jul 1975	Sep 1978	2024-03-01	9927
Saab	9-3x	2.0 T Biopower XWD	Kombi	Allrad	Benzin/Ethanol	162	220	Jan 2011	Dec 2012	2024-03-01	9928
FSO	Polonez i	1.5	Schrägheck	Heckantrieb	Benzin	55	75	Oct 1977	Aug 1988	2024-03-01	9929
Hyundai	Ix35	1.6	SUV	Frontantrieb	Benzin	99	135	Nov 2010	Dec 2015	2024-03-01	9930
Hyundai	Ix35	1.7 Crdi	SUV	Frontantrieb	Diesel	85	116	Nov 2010	Dec 2015	2024-03-01	9931
FSO	Polonez ii	1.5 I	Schrägheck	Heckantrieb	Benzin	55	75	Aug 1988	Aug 1992	2024-03-01	9932
FSO	Polonez ii	1.9 D	Schrägheck	Heckantrieb	Diesel	51	69	Aug 1988	Aug 1992	2024-03-01	9933
KIA	Pro cee'd	1.4	Schrägheck	Frontantrieb	Benzin	77	105	Feb 2008	Sep 2012	2024-03-01	9934
FSO	Polonez i	1.6	Schrägheck	Heckantrieb	Benzin	64	87	Aug 1986	Aug 1988	2024-03-01	9935
FSO	Polonez ii	1.5	Schrägheck	Heckantrieb	Benzin	55	75	Aug 1988	Aug 1992	2024-03-01	9936
FSO	Polonez ii	1.6	Schrägheck	Heckantrieb	Benzin	64	87	Aug 1988	Aug 1992	2024-03-01	9937
Hyundai	H-1 / starex	2.4 4WD	Bus	Allrad	Benzin	99	135	Jun 2001	Apr 2004	2024-03-01	9938
FSO	Polonez iii	1.9 D	Schrägheck	Heckantrieb	Diesel	51	69	Sep 1992	Mar 2002	2024-03-01	9939
FSO	Polonez iii	1.6 I	Stufenheck	Heckantrieb	Benzin	57	78	Sep 1992	Mar 2002	2024-03-01	9940
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec 4-matic	Stufenheck	Allrad	Diesel	150	204	Jan 2011	Dec 2015	2024-03-01	9941
Mercedes-benz	E-Klasse	E 300 CDI / Bluetec	Stufenheck	Heckantrieb	Diesel	170	231	Mar 2011	Dec 2015	2024-03-01	9942
Mercedes-benz	E-Klasse	E 350 CDI	Stufenheck	Heckantrieb	Diesel	195	265	Mar 2011	Dec 2015	2024-03-01	9943
Mercedes-benz	E-Klasse	E 350 CDI 4-matic	Stufenheck	Allrad	Diesel	195	265	Mar 2011	Dec 2015	2024-03-01	9944
Mercedes-benz	E-Klasse	E 200 NGT	Stufenheck	Heckantrieb	Benzin/Erdgas (CNG)	120	163	Mar 2011	Dec 2015	2024-03-01	9945
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	155	211	Apr 2010	Jul 2014	2024-03-01	9946
Porsche	Panamera	4.8 Turbo S	Schrägheck	Allrad	Benzin	404	550	May 2011	Jul 2013	2024-03-01	9947
Opel	Astra h gtc	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Mar 2005	Oct 2010	2024-03-01	9948
Opel	Astra h	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Aug 2009	Oct 2010	2024-03-01	9949
Saab	9-3	2.0 T BIO Power	Stufenheck	Frontantrieb	Benzin/Ethanol	162	220	Jan 2011	Feb 2015	2024-03-01	9953
Saab	9-3	2.0 T BIO Power	Stufenheck	Frontantrieb	Benzin/Ethanol	120	163	Jan 2007	Feb 2015	2024-03-01	9954
Saab	9-3	2.0 T	Stufenheck	Frontantrieb	Benzin	162	220	Jan 2011	Feb 2015	2024-03-01	9955
Opel	Astra h	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Apr 2004	Oct 2004	2024-03-01	9956
Saab	9-3	2.0 T	Stufenheck	Frontantrieb	Benzin	120	163	Jan 2007	Feb 2015	2024-03-01	9957
Skoda	Roomster	1.2 TSI	Kasten/Kombi	Frontantrieb	Benzin	63	86	Mar 2010	May 2015	2024-03-01	9958
FSO	Polonez iii	1.4 I 16V	Schrägheck	Heckantrieb	Benzin	76	103	Sep 1992	Mar 2002	2024-03-01	9959
FSO	Polonez iii	1.6 I	Schrägheck	Heckantrieb	Benzin	57	78	Sep 1992	Mar 2002	2024-03-01	9960
Skoda	Roomster	1.2 TDI	Kasten/Kombi	Frontantrieb	Diesel	55	75	Mar 2010	May 2015	2024-03-01	9961
Saab	9-3	2.0 T XWD	Stufenheck	Allrad	Benzin	162	220	Jan 2008	Feb 2015	2024-03-01	9962
Saab	9-3	2.0 T Biopower XWD	Stufenheck	Allrad	Benzin/Ethanol	162	220	Jan 2008	Feb 2015	2024-03-01	9963


--- Round 1 / 首次发送 ---
## 更新点

* 复用跨批次缓存中的 15 个既有尺寸组，完成 21 个 Ktype、26 条映射。
* Focus I 按三门/五门拆分；ix35 与 X6 按改款前后拆分。
* 本轮未创建或修正尺寸组，未重复输出既有尺寸来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：21
* READY 映射行：26
* PENDING Ktype：79
* 当前已引用尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9819	9819	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
9839	9839	Wagon	Alfasud	904B2	3	EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	HIGH	904B2旅行车物理外廓。	READY
9854	9854	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	改款后WA6外廓。	READY
9876	9876	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	HIGH	S 63 AMG短轴车身。	READY
9878	9878	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	HIGH	S 65 AMG长轴车身。	READY
9894	9894	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
9895	9895	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
9898	9898	Convertible	MINI II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	HIGH	改款后R57外廓。	READY
9899_3dr	9899	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	HIGH	Ktype未限定门数，拆分三门外廓。	READY
9899_5dr	9899	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	HIGH	Ktype未限定门数，拆分五门外廓。	READY
9900_3dr	9900	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	HIGH	Ktype未限定门数，拆分三门外廓。	READY
9900_5dr	9900	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	HIGH	Ktype未限定门数，拆分五门外廓。	READY
9914	9914	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9915	9915	Convertible	MINI II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	Cooper SD版本对应改款后R57；输入起始日期偏早。	READY
9930_prefl	9930	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9930_facelift	9930	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9931_prefl	9931	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9931_facelift	9931	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9946_prefl	9946	SUV	X6 I	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	MEDIUM	输入生产区间跨越改款外廓。	READY
9946_facelift	9946	SUV	X6 I	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	MEDIUM	输入生产区间跨越改款外廓。	READY
9953	9953	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	HIGH	220 PS版本对应Griffin外廓。	READY
9954	9954	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS版本对应Griffin外廓；输入起始日期偏早。	READY
9955	9955	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	HIGH	220 PS版本对应Griffin外廓。	READY
9957	9957	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS版本对应Griffin外廓；输入起始日期偏早。	READY
9962	9962	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	220 PS XWD版本对应Griffin外廓；输入起始日期偏早。	READY
9963	9963	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	220 PS BioPower XWD版本对应Griffin外廓；输入起始日期偏早。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Kia Cee'd ED、Pro cee'd ED、Venga YN 三个车身簇。
2. 核对 Range Rover Evoque L538 三门 Coupe 与五门 SUV 分支。
3. 处理 Mercedes-Benz W221 标准车身、S204 Wagon 和 W212 改款前后尺寸组。
4. 随后处理 Mazda 323 BJ、FSO 125p/Polonez 系列等尚无缓存的历史车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Kia Cee’d ED、Pro cee’d ED 与 Venga YN 的改款前后边界，新建 6 个尺寸组，完成 4 个 Ktype、8 条映射。([KIA клуб България][1])
* Range Rover Evoque L538 按三门/五门及 Dynamic 外观长度拆为 4 个尺寸组，完成 4 个 Ktype、16 条映射。
* 另闭合 Mitsubishi i-MiEV、BMW 1 Series M Coupe、Hyundai i10 PA、MINI Clubman R55、Audi TT 8N 和 Porsche Panamera Turbo S，共新建 7 个尺寸组。([SG Petch][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：39
* READY 映射行：60
* PENDING Ktype：61
* 当前已引用尺寸组：32
* 本轮首次创建尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9809_prefl	9809	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9809_facelift	9809	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9810_prefl	9810	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9810_facelift	9810	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9814_prefl	9814	MPV	Venga	YN	5	EU-KIA-VENGA-YN-MPV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9814_facelift	9814	MPV	Venga	YN	5	EU-KIA-VENGA-YN-MPV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9816_3dr	9816	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9816_3dr_dynamic	9816	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9816_5dr	9816	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9816_5dr_dynamic	9816	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9817_3dr	9817	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9817_3dr_dynamic	9817	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9817_5dr	9817	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9817_5dr_dynamic	9817	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9818_3dr	9818	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9818_3dr_dynamic	9818	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9818_5dr	9818	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9818_5dr_dynamic	9818	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9824_3dr	9824	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9824_3dr_dynamic	9824	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9824_5dr	9824	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9824_5dr_dynamic	9824	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9830	9830	Hatchback	i-MiEV		5	EU-MITSUBISHI-I-MIEV-HATCHBACK-5D-01	HIGH		READY
9877	9877	Coupe	1 Series M Coupe	E82	2	EU-BMW-1-SERIES-M-E82-COUPE-2D-01	HIGH		READY
9892	9892	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	HIGH		READY
9893	9893	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	HIGH		READY
9896	9896	Wagon	MINI II Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	HIGH		READY
9897	9897	Wagon	MINI II Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	HIGH		READY
9901	9901	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-FWD-01	HIGH		READY
9902	9902	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-QUATTRO-01	HIGH		READY
9903	9903	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-QUATTRO-01	HIGH		READY
9934_prefl	9934	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-PREFL-01	MEDIUM	输入生产区间跨越三门改款外廓。	READY
9934_facelift	9934	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入生产区间跨越三门改款外廓。	READY
9947	9947	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-TURBO-S-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	4235	1790	1480	Kia cee'd Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	4260	1790	1480	Kia Cee'd 2010 owner's manual	https://www.carmanualsonline.info/kia-ceed-2010-owners-manual/?srch=dimensions
EU-KIA-VENGA-YN-MPV-PREFL-01	4068	1765	1600	Kia Media Site Venga archive	https://www.kiapressoffice.com/models/venga-archive-2014-2015
EU-KIA-VENGA-YN-MPV-FACELIFT-01	4075	1765	1600	Kia Venga MY15 official brochure	https://prod2-eu.kia.com/content/dam/kwcms/kme/global/en/assets/contents/utility/brochure/product-brochure/kia-venga-my15-product-brochure.pdf
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	4355	1900	1605	Land Rover Range Rover Evoque official brochure;Car and Driver	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.caranddriver.com/land-rover/range-rover-evoque/specs/2014/land-rover_range-rover-evoque_land-rover-range-rover-evoque_2014
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	4365	1900	1605	Land Rover Range Rover Evoque official brochure;Car and Driver	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.caranddriver.com/land-rover/range-rover-evoque/specs/2014/land-rover_range-rover-evoque_land-rover-range-rover-evoque_2014
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	4355	1900	1635	Land Rover Range Rover Evoque official brochure;Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.automobile-catalog.com/car/2014/2045600/range_rover_evoque_si4_prestige.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	4365	1900	1635	Land Rover Range Rover Evoque official brochure;Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.automobile-catalog.com/car/2014/2045600/range_rover_evoque_si4_prestige.html
EU-MITSUBISHI-I-MIEV-HATCHBACK-5D-01	3475	1475	1610	Mitsubishi i-MiEV brochure	https://cdn.sgpetch.co.uk/content/vehicle_media/Mitsubishi/I_MIEV_pdf_brochure.pdf
EU-BMW-1-SERIES-M-E82-COUPE-2D-01	4380	1803	1420	BMW Group PressClub;Auto-Data	https://www.press.bmwgroup.com/global/article/detail/T0091933EN/the-bmw-1-series-m-coupe?language=en;https://www.auto-data.net/en/bmw-1m-model-3458
EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	3565	1595	1540	Hyundai i10 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Hyundai-i10-UK.pdf
EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	3961	1683	1426	MINI Corporate Communications specifications;Automobile-Catalog	https://libraryofmotoring.info/pdf/specifications/2011-mini-cooper-sd-clubman.pdf;https://www.automobile-catalog.com/car/2011/1754780/mini_cooper_d_clubman.html
EU-AUDI-TT-8N-COUPE-FWD-01	4041	1764	1346	Audi UK technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-AUDI-TT-8N-COUPE-QUATTRO-01	4041	1764	1345	Audi UK technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-PREFL-01	4250	1790	1450	Kia cee'd Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-FACELIFT-01	4250	1790	1450	Auto-Data	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
EU-PORSCHE-PANAMERA-970-HATCHBACK-TURBO-S-01	4970	1931	1418	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-turbo-s-4.8-v8-550hp-pdk-56301
```

## 下一步优先处理

1. Mercedes-Benz W221、W212 与 S204 的标准轴距、长轴及改款边界。
2. MINI Countryman R60、Hyundai Veloster 与 Jeep Compass 的改款和特殊悬架分支。
3. Mazda 323 BJ、FSO 125p/Polonez 与其他尚无缓存的历史车型簇。

推进信号：CONTINUE

[1]: https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf "cee'd product Guide"
[2]: https://cdn.sgpetch.co.uk/content/vehicle_media/Mitsubishi/I_MIEV_pdf_brochure.pdf?utm_source=chatgpt.com "iMiEV 11MY pha brochure"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Veloster FS、Compass I facelift、Astra H GTC/五门和 Roomster 5J，共新增 6 个尺寸组。
* Mercedes-Benz C 200 CDI S204 的输入区间跨越改款，按改款前后拆为两个外廓尺寸组。([marsClassic][1])
* 闭合 MINI Countryman R60 与 Alfa Romeo 2000 Berlina；VW Polo III GTI 直接复用既有 6N 尺寸组。([AUSmotive][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：53
* READY 映射行：75
* PENDING Ktype：47
* 当前已引用尺寸组：42
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9815	9815	Coupe	Veloster I	FS	3	EU-HYUNDAI-VELOSTER-FS-COUPE-3D-01	HIGH		READY
9823	9823	Sedan	1750-2000 Berlina	105.12	4	EU-ALFA-ROMEO-2000-BERLINA-10512-SEDAN-4D-01	HIGH		READY
9867	9867	SUV	Compass I facelift		5	EU-JEEP-COMPASS-I-SUV-FACELIFT-01	HIGH		READY
9891_prefl	9891	Wagon	C-Class III	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9891_facelift	9891	Wagon	C-Class III	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9904	9904	Hatchback	Polo III	6N	3	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH		READY
9916	9916	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9917	9917	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9918	9918	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9926	9926	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9948	9948	Hatchback	Astra H GTC	A04	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-01	HIGH		READY
9949	9949	Hatchback	Astra H	A04	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH		READY
9956	9956	Hatchback	Astra H	A04	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH		READY
9958	9958	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	HIGH		READY
9961	9961	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-VELOSTER-FS-COUPE-3D-01	4220	1790	1399	Hyundai 2012 Veloster brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2012_veloster.pdf
EU-ALFA-ROMEO-2000-BERLINA-10512-SEDAN-4D-01	4390	1565	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/71840/alfa_romeo_2000_berlina.html
EU-JEEP-COMPASS-I-SUV-FACELIFT-01	4448	1812	1663	Jeep Compass 2011 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Jeep-Compass-UK.pdf
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-BlueEFFICIENCY-Estate-2009---2011.xhtml?oid=189508160
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Mercedes-Benz C-Class Saloon and Estate brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/C-Class_saloon_estate_W204_S204_0613.pdf
EU-MINI-COUNTRYMAN-R60-SUV-5D-01	4097	1789	1561	MINI Countryman technical specifications	https://www.ausmotive.com/downloads/MINI/Countryman-tech-specs-Feb2011.pdf
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-01	4290	1753	1415	Vauxhall Astra 2009 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1467	Vauxhall Astra 2009 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	4214	1684	1607	Skoda Roomster international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Skoda-Roomster-2012-INT.pdf
```

## 下一步优先处理

1. 集中闭合 Mercedes-Benz W221 与 W212 的标准轴距和改款分支。
2. 处理 Mazda 323 BJ 的 Sedan/Hatchback 及改款前后尺寸组。
3. 处理 Opel Monterey B、Alfa Romeo Alfetta/Giulia Coupe 和 Hyundai H-1 的多外廓边界。
4. 最后集中处理 FSO 125p、132p、126p 与 Polonez 历史车型簇。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-BlueEFFICIENCY-Estate-2009---2011.xhtml?oid=189508160&utm_source=chatgpt.com "C 200 CDI BlueEFFICIENCY, 2009 - 2011"
[2]: https://www.ausmotive.com/downloads/MINI/Countryman-tech-specs-Feb2011.pdf?utm_source=chatgpt.com "R60 Cooper Countryman - AUSmotive.com"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz W221/V221 标准轴距与长轴距，以及 W212 改款前后外廓，完成 12 个 Ktype、24 条映射。([marsClassic][1])
* 闭合 Mazda 323 BJ Sedan/Hatchback 的改款前后外廓，完成 9 个 Ktype、18 条映射。([汽车目录][2])
* 闭合 Opel Monterey B 三门/五门、Alfetta GTV 改款分支；Giulia 1300/1600 Super 修正为四门 Sedan 并复用既有尺寸组。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射行：125
* PENDING Ktype：21
* 当前已引用尺寸组：53
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9821_3dr	9821	SUV	Monterey B	UBS	3	EU-OPEL-MONTEREY-B-SUV-3D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分三门分支。	READY
9821_5dr	9821	SUV	Monterey B	UBS	5	EU-OPEL-MONTEREY-B-SUV-5D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分五门分支。	READY
9822_3dr	9822	SUV	Monterey B	UBS	3	EU-OPEL-MONTEREY-B-SUV-3D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分三门分支。	READY
9822_5dr	9822	SUV	Monterey B	UBS	5	EU-OPEL-MONTEREY-B-SUV-5D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分五门分支。	READY
9840_prefl	9840	Coupe	Alfetta GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9840_facelift	9840	Coupe	Alfetta GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9841	9841	Sedan	Giulia Nuova Super	115.09	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	HIGH	输入BodyStyle误标为Coupe；1300 Super为四门Sedan。	READY
9842	9842	Sedan	Giulia Nuova Super	105.26	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	HIGH	输入BodyStyle误标为Coupe；1600 Super为四门Sedan。	READY
9869_swb	9869	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9869_lwb	9869	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9870_swb	9870	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9870_lwb	9870	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9871_swb	9871	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9871_lwb	9871	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9872_swb	9872	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9872_lwb	9872	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9873_swb	9873	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9873_lwb	9873	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9874_swb	9874	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9874_lwb	9874	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9875_swb	9875	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9875_lwb	9875	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9905_prefl	9905	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9905_facelift	9905	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9906_prefl	9906	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9906_facelift	9906	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9907_prefl	9907	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9907_facelift	9907	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9908_prefl	9908	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9908_facelift	9908	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9909_prefl	9909	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9909_facelift	9909	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9910_prefl	9910	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9910_facelift	9910	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9911_prefl	9911	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9911_facelift	9911	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9912_prefl	9912	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9912_facelift	9912	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9913_prefl	9913	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9913_facelift	9913	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9941_prefl	9941	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9941_facelift	9941	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9942_prefl	9942	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9942_facelift	9942	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9943_prefl	9943	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9943_facelift	9943	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9944_prefl	9944	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9944_facelift	9944	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9945_prefl	9945	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9945_facelift	9945	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MONTEREY-B-SUV-3D-01	4365	1835	1830	AutoData1 Opel Monterey B RS specifications	https://www.autodata1.com/en/car/opel/monterey/monterey-b-rs-35-v6-24v-215-hp-4x4
EU-OPEL-MONTEREY-B-SUV-5D-01	4795	1835	1840	Auto-Data Vauxhall Monterey Mk II specifications	https://www.auto-data.net/en/vauxhall-monterey-mk-ii-5-dr-facelift-1998-3.5-v6-24v-215hp-6070
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-FACELIFT-01	4260	1664	1330	Automobile-Catalog Alfa Romeo GTV 2.0 specifications	https://www.automobile-catalog.com/car/1984/144125/alfa_romeo_gtv_2_0.html
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data;Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-250-cdi-blueefficiency-204hp-7g-tronic-plus-36924;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data;Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-350-cdi-bluetec-258hp-4matic-g-tronic-36888;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-250-CDI-BlueEFFICIENCY-lang-2011---2013.xhtml?oid=191730294
EU-MAZDA-323-BJ-SEDAN-PREFL-01	4315	1705	1410	Automobile-Catalog Mazda 323 S specifications	https://www.automobile-catalog.com/car/1998/1672175/mazda_323_s_2_0_d.html
EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	4365	1705	1410	Automobile-Catalog Mazda 323 S specifications	https://www.automobile-catalog.com/car/2001/1672325/mazda_323_s_1_6.html
EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	4200	1705	1410	Automobile-Catalog Mazda 323 F specifications	https://www.automobile-catalog.com/car/1998/1672295/mazda_323_f_2_0_td.html
EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	4250	1705	1420	ADAC Mazda 323 BJ facelift specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mazda/323/bj-facelift/994371/
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	4868	1854	1470	Mercedes-Benz E-Class Saloon official brochure	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474	Mercedes-Benz E-Class Saloon and Estate official brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/E-Class_saloon_estate_W212_S212_0413.pdf
```

## 下一步优先处理

1. 集中闭合 FSO 125p、126p、127p、132p 与 Polonez I–III 历史车型簇。
2. 处理 Hyundai H-1/Starex、Saab 9-3X 与剩余特殊车身。
3. 完成剩余 Ktype 后立即进行一次机械闭合检查并输出两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889&utm_source=chatgpt.com "221 series S-Class Saloons, 2009 - 2013"
[2]: https://www.automobile-catalog.com/car/1998/1672175/mazda_323_s_2_0_d.html?utm_source=chatgpt.com "1998 Mazda 323 S 2.0 D Specs Review (52 kW ..."
[3]: https://www.auto-data.net/en/vauxhall-monterey-mk-ii-5-dr-facelift-1998-3.5-v6-24v-215hp-6070?utm_source=chatgpt.com "Vauxhall Monterey Mk II (5 dr) (facelift 1998) 3.5 V6 24V (215 Hp)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 BMW 730i/730Li 的短轴、长轴及改款前后四个物理分支，新建 4 个尺寸组。BMW 官方改款资料明确给出 730i 与 730Li 的不同长宽高。
* 完成 FSO 125p Sedan/Wagon 改款前后、126p 600、127p，以及 Polonez I–III 的外廓分组。125p 在 1975 年前后发生长度和宽度变化，Polonez Caro/Atu Plus 也具有不同车长。([汽车目录][1])
* 完成 Saab 9-3X 与 Hyundai H-1/Starex 4WD 尺寸组。([汽车目录][2])
* 本轮共完成 19 个 Ktype、30 条 READY 映射，新建 18 个尺寸组。
* FSO 132p 的 1.6 和 1.8 仍需确认第一至第三系列以及 GL/GLS 保险杠外廓覆盖，暂保留 2 条 PENDING。现有资料显示 1974 年中及 1977 年均发生外廓变化，且第二系列同排量不同版本存在不同车长。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：155
* PENDING Ktype：2
* PENDING 映射行：2
* 当前映射总行数：157
* 当前已引用尺寸组：71
* 本轮首次创建尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9863_swb_prefl	9863	Sedan	7 Series V	F01	4	EU-BMW-7-F01-SEDAN-SWB-PREFL-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；短轴改款前外廓。	READY
9863_swb_facelift	9863	Sedan	7 Series V	F01	4	EU-BMW-7-F01-SEDAN-SWB-FACELIFT-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；短轴改款后外廓。	READY
9863_lwb_prefl	9863	Sedan	7 Series V	F02	4	EU-BMW-7-F02-SEDAN-LWB-PREFL-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；长轴改款前外廓。	READY
9863_lwb_facelift	9863	Sedan	7 Series V	F02	4	EU-BMW-7-F02-SEDAN-LWB-FACELIFT-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；长轴改款后外廓。	READY
9919_prefl	9919	Sedan	125p		4	EU-FSO-125P-SEDAN-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9919_facelift	9919	Sedan	125p		4	EU-FSO-125P-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9920_prefl	9920	Sedan	125p		4	EU-FSO-125P-SEDAN-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9920_facelift	9920	Sedan	125p		4	EU-FSO-125P-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9921_prefl	9921	Wagon	125p		5	EU-FSO-125P-WAGON-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9921_facelift	9921	Wagon	125p		5	EU-FSO-125P-WAGON-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9922	9922	Hatchback	126p		2	EU-FSO-126P-HATCHBACK-2D-600-01	MEDIUM	0.6/30 PS版本对应早期600外廓；输入结束日期晚于该版本实际覆盖。	READY
9923	9923	Sedan	132p		4		LOW	候选覆盖Fiat 132第一至第三系列；第二系列GL与GLS亦存在车长差异。	PENDING: 需确认132p 1.6各系列与GL/GLS外廓边界
9924_prefl	9924	Wagon	125p		5	EU-FSO-125P-WAGON-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9924_facelift	9924	Wagon	125p		5	EU-FSO-125P-WAGON-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9925	9925	Hatchback	127p		3	EU-FSO-127P-HATCHBACK-3D-01	MEDIUM	输入起始日期早于127p实际投产；按0.9三门外廓。	READY
9927	9927	Sedan	132p		4		LOW	1.8/107 PS版本在第二系列与第三系列之间的实际波兰装配覆盖尚未闭合。	PENDING: 需确认132p 1.8第三系列实际覆盖
9928	9928	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3X-II-WAGON-5D-01	HIGH		READY
9929	9929	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-5D-01	HIGH		READY
9932	9932	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9933	9933	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9935	9935	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-5D-01	HIGH		READY
9936	9936	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9937	9937	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9938	9938	MPV	H-1 I / Starex		5	EU-HYUNDAI-H1-STAREX-I-MPV-4WD-01	HIGH		READY
9939_prefl	9939	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9939_facelift	9939	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9940_prefl	9940	Sedan	Polonez III		4	EU-FSO-POLONEZ-III-ATU-SEDAN-PREFL-01	MEDIUM	输入起始日期早于Atu Sedan投产，按实际Sedan阶段拆分。	READY
9940_facelift	9940	Sedan	Polonez III		4	EU-FSO-POLONEZ-III-ATU-PLUS-SEDAN-FACELIFT-01	MEDIUM	输入区间跨越Atu Plus外廓变更。	READY
9959_prefl	9959	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9959_facelift	9959	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9960_prefl	9960	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9960_facelift	9960	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-7-F01-SEDAN-SWB-PREFL-01	5072	1902	1479	Auto-Data BMW 7 Series F01/F02 generation	https://www.auto-data.net/en/bmw-7-series-model-945
EU-BMW-7-F01-SEDAN-SWB-FACELIFT-01	5079	1902	1471	BMW 730i and 730Li official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0131447EN/207820
EU-BMW-7-F02-SEDAN-LWB-PREFL-01	5212	1902	1484	SGCarMart BMW 730Li specifications	https://www.sgcarmart.com/new_cars/newcars_print.php?CarCode=10097&Subcode=191
EU-BMW-7-F02-SEDAN-LWB-FACELIFT-01	5219	1902	1481	BMW 730i and 730Li official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0131447EN/207820
EU-FSO-125P-SEDAN-PREFL-01	4233	1625	1440	Automobile-Catalog Polski Fiat 125p 1300	https://www.automobile-catalog.com/car/1972/29645/polski_fiat_125p_1300.html
EU-FSO-125P-SEDAN-FACELIFT-01	4226	1630	1440	Automobile-Catalog Polski Fiat 125p 1300	https://www.automobile-catalog.com/car/1980/39365/polski_fiat_125p_1300.html
EU-FSO-125P-WAGON-PREFL-01	4234	1625	1473	Automobile-Catalog Polski Fiat 125p 1500 Kombi	https://www.automobile-catalog.com/car/1972/2736170/polski_fiat_125p_1500_kombi.html
EU-FSO-125P-WAGON-FACELIFT-01	4234	1630	1473	Automobile-Catalog Polski Fiat 125p 1500 Kombi	https://www.automobile-catalog.com/car/1980/27515/polski_fiat_125p_kombi_1500.html
EU-FSO-126P-HATCHBACK-2D-600-01	3054	1377	1335	Automobile-Catalog Polski Fiat 126p 600	https://www.automobile-catalog.com/car/1977/38975/polski_fiat_126p_600.html
EU-FSO-127P-HATCHBACK-3D-01	3595	1527	1370	Automobile-Catalog Fiat 127 body specification	https://www.automobile-catalog.com/car/1972/711230/fiat_127.html
EU-SAAB-9-3X-II-WAGON-5D-01	4690	1802	1527	Automobile-Catalog Saab 9-3X 2.0T XWD	https://www.automobile-catalog.com/car/2011/3038660/saab_9-3x_2_0t_xwd_automatic.html
EU-FSO-POLONEZ-I-HATCHBACK-5D-01	4272	1651	1420	Automobile-Catalog FSO Polonez 1500 Lux	https://www.automobile-catalog.com/car/1981/2736515/fso_polonez_1500.html
EU-FSO-POLONEZ-II-HATCHBACK-5D-01	4322	1651	1420	Automobile-Catalog FSO Polonez 1.5 SLE	https://www.automobile-catalog.com/car/1990/2736905/fso_polonez_1_5_sle.html
EU-HYUNDAI-H1-STAREX-I-MPV-4WD-01	4695	1820	1885	Automobile-Catalog Hyundai Starex 2400 HSV 4x4	https://www.automobile-catalog.com/car/1998/1167770/hyundai_starex_2400_hsv_4x4.html
EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	4318	1650	1420	Automobile-Catalog FSO Polonez Caro 1.6 GLi	https://www.automobile-catalog.com/car/1992/2737040/fso_polonez_caro_1_6_gli.html
EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	4369	1650	1420	Automobile-Catalog FSO Polonez Caro Plus 1.6 GSi	https://www.automobile-catalog.com/car/1999/2737250/fso_polonez_caro_plus_1_6_gsi.html
EU-FSO-POLONEZ-III-ATU-SEDAN-PREFL-01	4318	1650	1420	Automobile-Catalog FSO Polonez Atu 1.6 GLi	https://www.automobile-catalog.com/car/1996/2737190/fso_polonez_atu_1_6_gli.html
EU-FSO-POLONEZ-III-ATU-PLUS-SEDAN-FACELIFT-01	4369	1650	1420	Automobile-Catalog FSO Polonez Atu Plus 1.6 GSi	https://www.automobile-catalog.com/car/1999/2737280/fso_polonez_atu_plus_1_6_gsi.html
```

## 下一步优先处理

1. 确认 132p 1.6 在第一系列、第二系列 GL/GLS 和第三系列中的完整物理分支。
2. 确认 132p 1.8/107 PS 是否实际覆盖第三系列，以及波兰装配批次的结束边界。
3. 两条映射闭合后立即执行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/23585/polski_fiat_125p_1500.html?utm_source=chatgpt.com "1972 Polski Fiat 125p 1500 Specs Review (51.5 kW / 70 PS / 69 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2011/3038660/saab_9-3x_2_0t_xwd_automatic.html?utm_source=chatgpt.com "2011 Saab 9-3X 2.0T XWD automatic (aut. 6)"
[3]: https://www.automobile-catalog.com/car/1974/713210/fiat_132_1600.html?utm_source=chatgpt.com "1974 Fiat 132 1600 Specs Review (72 kW / 98 PS / 97 hp) (up to mid-year 1974 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8701-8800_ktype_dimension_mapping_final.tsv
- all_8701-8800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* FSO 132p 的最后两条待处理映射已闭合：Ktype 9923 按 Series II 与 Series III 两种外廓拆分；Ktype 9927 的 1.8/107 PS 对应 Series II，后续同排量版本功率已变更，因此不扩展至 Series III。([汽车目录][1])
* 已完成一次机械收尾检查：表头固定、映射 `id` 唯一、尺寸组 ID 唯一、全部引用闭合，无孤立尺寸组、空尺寸或空来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* 最终映射行：158
* PENDING：0
* 最终 DIMENSION_GROUP：75
* 全部映射均为 `READY`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9809_prefl	9809	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9809_facelift	9809	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9810_prefl	9810	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9810_facelift	9810	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9814_prefl	9814	MPV	Venga	YN	5	EU-KIA-VENGA-YN-MPV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9814_facelift	9814	MPV	Venga	YN	5	EU-KIA-VENGA-YN-MPV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9815	9815	Coupe	Veloster I	FS	3	EU-HYUNDAI-VELOSTER-FS-COUPE-3D-01	HIGH		READY
9816_3dr	9816	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9816_3dr_dynamic	9816	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9816_5dr	9816	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9816_5dr_dynamic	9816	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9817_3dr	9817	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9817_3dr_dynamic	9817	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9817_5dr	9817	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9817_5dr_dynamic	9817	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9818_3dr	9818	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9818_3dr_dynamic	9818	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9818_5dr	9818	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9818_5dr_dynamic	9818	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9819	9819	Sedan	Sonata IV	EF	4	EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	HIGH		READY
9821_3dr	9821	SUV	Monterey B	UBS	3	EU-OPEL-MONTEREY-B-SUV-3D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分三门分支。	READY
9821_5dr	9821	SUV	Monterey B	UBS	5	EU-OPEL-MONTEREY-B-SUV-5D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分五门分支。	READY
9822_3dr	9822	SUV	Monterey B	UBS	3	EU-OPEL-MONTEREY-B-SUV-3D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分三门分支。	READY
9822_5dr	9822	SUV	Monterey B	UBS	5	EU-OPEL-MONTEREY-B-SUV-5D-01	MEDIUM	Ktype未限定三门与五门外廓，拆分五门分支。	READY
9823	9823	Sedan	1750-2000 Berlina	105.12	4	EU-ALFA-ROMEO-2000-BERLINA-10512-SEDAN-4D-01	HIGH		READY
9824_3dr	9824	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	MEDIUM	Ktype未限定三门标准外观分支。	READY
9824_3dr_dynamic	9824	SUV	Range Rover Evoque I	L538	3	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	MEDIUM	Ktype未限定三门Dynamic外观分支。	READY
9824_5dr	9824	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	MEDIUM	Ktype未限定五门标准外观分支。	READY
9824_5dr_dynamic	9824	SUV	Range Rover Evoque I	L538	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	MEDIUM	Ktype未限定五门Dynamic外观分支。	READY
9830	9830	Hatchback	i-MiEV		5	EU-MITSUBISHI-I-MIEV-HATCHBACK-5D-01	HIGH		READY
9839	9839	Wagon	Alfasud	904B2	3	EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	HIGH	904B2旅行车物理外廓。	READY
9840_prefl	9840	Coupe	Alfetta GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9840_facelift	9840	Coupe	Alfetta GTV	116	3	EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9841	9841	Sedan	Giulia Nuova Super	115.09	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	HIGH	输入BodyStyle误标为Coupe；1300 Super为四门Sedan。	READY
9842	9842	Sedan	Giulia Nuova Super	105.26	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	HIGH	输入BodyStyle误标为Coupe；1600 Super为四门Sedan。	READY
9854	9854	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	改款后WA6外廓。	READY
9863_swb_prefl	9863	Sedan	7 Series V	F01	4	EU-BMW-7-F01-SEDAN-SWB-PREFL-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；短轴改款前外廓。	READY
9863_swb_facelift	9863	Sedan	7 Series V	F01	4	EU-BMW-7-F01-SEDAN-SWB-FACELIFT-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；短轴改款后外廓。	READY
9863_lwb_prefl	9863	Sedan	7 Series V	F02	4	EU-BMW-7-F02-SEDAN-LWB-PREFL-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；长轴改款前外廓。	READY
9863_lwb_facelift	9863	Sedan	7 Series V	F02	4	EU-BMW-7-F02-SEDAN-LWB-FACELIFT-01	HIGH	VariantName同时包含730i与730Li，生产区间跨越改款；长轴改款后外廓。	READY
9867	9867	SUV	Compass I facelift		5	EU-JEEP-COMPASS-I-SUV-FACELIFT-01	HIGH		READY
9869_swb	9869	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9869_lwb	9869	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9870_swb	9870	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9870_lwb	9870	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9871_swb	9871	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9871_lwb	9871	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9872_swb	9872	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9872_lwb	9872	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9873_swb	9873	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9873_lwb	9873	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9874_swb	9874	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9874_lwb	9874	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9875_swb	9875	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分短轴外廓。	READY
9875_lwb	9875	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	Ktype未限定轴距，拆分长轴外廓。	READY
9876	9876	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	HIGH	S 63 AMG短轴车身。	READY
9877	9877	Coupe	1 Series M Coupe	E82	2	EU-BMW-1-SERIES-M-E82-COUPE-2D-01	HIGH		READY
9878	9878	Sedan	S-Class W221 facelift	V221	4	EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	HIGH	S 65 AMG长轴车身。	READY
9891_prefl	9891	Wagon	C-Class III	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9891_facelift	9891	Wagon	C-Class III	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9892	9892	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	HIGH		READY
9893	9893	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	HIGH		READY
9894	9894	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
9895	9895	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
9896	9896	Wagon	MINI II Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	HIGH		READY
9897	9897	Wagon	MINI II Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	HIGH		READY
9898	9898	Convertible	MINI II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	HIGH	改款后R57外廓。	READY
9899_3dr	9899	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	HIGH	Ktype未限定门数，拆分三门外廓。	READY
9899_5dr	9899	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	HIGH	Ktype未限定门数，拆分五门外廓。	READY
9900_3dr	9900	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	HIGH	Ktype未限定门数，拆分三门外廓。	READY
9900_5dr	9900	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	HIGH	Ktype未限定门数，拆分五门外廓。	READY
9901	9901	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-FWD-01	HIGH		READY
9902	9902	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-QUATTRO-01	HIGH		READY
9903	9903	Coupe	TT I	8N	3	EU-AUDI-TT-8N-COUPE-QUATTRO-01	HIGH		READY
9904	9904	Hatchback	Polo III	6N	3	EU-VW-POLO-III-6N-HATCHBACK-01	HIGH		READY
9905_prefl	9905	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9905_facelift	9905	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9906_prefl	9906	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9906_facelift	9906	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9907_prefl	9907	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9907_facelift	9907	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9908_prefl	9908	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9908_facelift	9908	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9909_prefl	9909	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9909_facelift	9909	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9910_prefl	9910	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9910_facelift	9910	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9911_prefl	9911	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9911_facelift	9911	Sedan	323 VI	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9912_prefl	9912	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9912_facelift	9912	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9913_prefl	9913	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9913_facelift	9913	Hatchback	323 VI	BJ	5	EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9914	9914	Convertible	CLK I	A208	2	EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	HIGH		READY
9915	9915	Convertible	MINI II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	Cooper SD版本对应改款后R57；输入起始日期偏早。	READY
9916	9916	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9917	9917	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9918	9918	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9919_prefl	9919	Sedan	125p		4	EU-FSO-125P-SEDAN-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9919_facelift	9919	Sedan	125p		4	EU-FSO-125P-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9920_prefl	9920	Sedan	125p		4	EU-FSO-125P-SEDAN-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9920_facelift	9920	Sedan	125p		4	EU-FSO-125P-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9921_prefl	9921	Wagon	125p		5	EU-FSO-125P-WAGON-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9921_facelift	9921	Wagon	125p		5	EU-FSO-125P-WAGON-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9922	9922	Hatchback	126p		2	EU-FSO-126P-HATCHBACK-2D-600-01	MEDIUM	0.6/30 PS版本对应早期600外廓；输入结束日期晚于该版本实际覆盖。	READY
9923_series2	9923	Sedan	132p Series II		4	EU-FSO-132P-SEDAN-SERIES2-01	HIGH	1.6/98 PS覆盖第二系列外廓。	READY
9923_series3	9923	Sedan	132p Series III		4	EU-FSO-132P-SEDAN-SERIES3-01	HIGH	1.6/98 PS覆盖第三系列外廓。	READY
9924_prefl	9924	Wagon	125p		5	EU-FSO-125P-WAGON-PREFL-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9924_facelift	9924	Wagon	125p		5	EU-FSO-125P-WAGON-FACELIFT-01	HIGH	输入生产区间跨越1975年外廓变更。	READY
9925	9925	Hatchback	127p		3	EU-FSO-127P-HATCHBACK-3D-01	MEDIUM	输入起始日期早于127p实际投产；按0.9三门外廓。	READY
9926	9926	SUV	Countryman I	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH		READY
9927	9927	Sedan	132p Series II		4	EU-FSO-132P-SEDAN-SERIES2-01	MEDIUM	1.8/107 PS仅对应第二系列；输入结束日期偏晚。	READY
9928	9928	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3X-II-WAGON-5D-01	HIGH		READY
9929	9929	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-5D-01	HIGH		READY
9930_prefl	9930	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9930_facelift	9930	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9931_prefl	9931	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9931_facelift	9931	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9932	9932	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9933	9933	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9934_prefl	9934	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-PREFL-01	MEDIUM	输入生产区间跨越三门改款外廓。	READY
9934_facelift	9934	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入生产区间跨越三门改款外廓。	READY
9935	9935	Hatchback	Polonez I		5	EU-FSO-POLONEZ-I-HATCHBACK-5D-01	HIGH		READY
9936	9936	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9937	9937	Hatchback	Polonez II		5	EU-FSO-POLONEZ-II-HATCHBACK-5D-01	HIGH		READY
9938	9938	MPV	H-1 I / Starex		5	EU-HYUNDAI-H1-STAREX-I-MPV-4WD-01	HIGH		READY
9939_prefl	9939	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9939_facelift	9939	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9940_prefl	9940	Sedan	Polonez III		4	EU-FSO-POLONEZ-III-ATU-SEDAN-PREFL-01	MEDIUM	输入起始日期早于Atu Sedan投产，按实际Sedan阶段拆分。	READY
9940_facelift	9940	Sedan	Polonez III		4	EU-FSO-POLONEZ-III-ATU-PLUS-SEDAN-FACELIFT-01	MEDIUM	输入区间跨越Atu Plus外廓变更。	READY
9941_prefl	9941	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9941_facelift	9941	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9942_prefl	9942	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9942_facelift	9942	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9943_prefl	9943	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9943_facelift	9943	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9944_prefl	9944	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9944_facelift	9944	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9945_prefl	9945	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	HIGH	输入生产区间跨越改款外廓。	READY
9945_facelift	9945	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH	输入生产区间跨越改款外廓。	READY
9946_prefl	9946	SUV	X6 I	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	MEDIUM	输入生产区间跨越改款外廓。	READY
9946_facelift	9946	SUV	X6 I	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	MEDIUM	输入生产区间跨越改款外廓。	READY
9947	9947	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-TURBO-S-01	HIGH		READY
9948	9948	Hatchback	Astra H GTC	A04	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-01	HIGH		READY
9949	9949	Hatchback	Astra H	A04	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH		READY
9953	9953	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	HIGH	220 PS版本对应Griffin外廓。	READY
9954	9954	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS版本对应Griffin外廓；输入起始日期偏早。	READY
9955	9955	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	HIGH	220 PS版本对应Griffin外廓。	READY
9956	9956	Hatchback	Astra H	A04	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH		READY
9957	9957	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS版本对应Griffin外廓；输入起始日期偏早。	READY
9958	9958	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	HIGH		READY
9959_prefl	9959	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9959_facelift	9959	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9960_prefl	9960	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9960_facelift	9960	Hatchback	Polonez III		5	EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	HIGH	输入生产区间跨越Caro Plus外廓变更。	READY
9961	9961	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	HIGH		READY
9962	9962	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	220 PS XWD版本对应Griffin外廓；输入起始日期偏早。	READY
9963	9963	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	220 PS BioPower XWD版本对应Griffin外廓；输入起始日期偏早。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8701-8800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CEED-ED-HATCHBACK-5D-PREFL-01	4235	1790	1480	Kia cee'd Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-KIA-CEED-ED-HATCHBACK-5D-FACELIFT-01	4260	1790	1480	Kia Cee'd 2010 owner's manual	https://www.carmanualsonline.info/kia-ceed-2010-owners-manual/?srch=dimensions
EU-KIA-VENGA-YN-MPV-PREFL-01	4068	1765	1600	Kia Media Site Venga archive	https://www.kiapressoffice.com/models/venga-archive-2014-2015
EU-KIA-VENGA-YN-MPV-FACELIFT-01	4075	1765	1600	Kia Venga MY15 official brochure	https://prod2-eu.kia.com/content/dam/kwcms/kme/global/en/assets/contents/utility/brochure/product-brochure/kia-venga-my15-product-brochure.pdf
EU-HYUNDAI-VELOSTER-FS-COUPE-3D-01	4220	1790	1399	Hyundai 2012 Veloster brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2012_veloster.pdf
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-01	4355	1900	1605	Land Rover Range Rover Evoque official brochure;Car and Driver	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.caranddriver.com/land-rover/range-rover-evoque/specs/2014/land-rover_range-rover-evoque_land-rover-range-rover-evoque_2014
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-3D-DYNAMIC-01	4365	1900	1605	Land Rover Range Rover Evoque official brochure;Car and Driver	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.caranddriver.com/land-rover/range-rover-evoque/specs/2014/land-rover_range-rover-evoque_land-rover-range-rover-evoque_2014
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-01	4355	1900	1635	Land Rover Range Rover Evoque official brochure;Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.automobile-catalog.com/car/2014/2045600/range_rover_evoque_si4_prestige.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-L538-SUV-5D-DYNAMIC-01	4365	1900	1635	Land Rover Range Rover Evoque official brochure;Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/10/2014-Range-Rover-Evoque-UK.pdf;https://www.automobile-catalog.com/car/2014/2045600/range_rover_evoque_si4_prestige.html
EU-HYUNDAI-SONATA-IV-EF-SEDAN-4D-01	4710	1818	1410	Auto.ru Hyundai Sonata IV EF specifications	https://auto.ru/catalog/cars/hyundai/sonata/3483580/4995105/specifications/4995105__4995107/
EU-OPEL-MONTEREY-B-SUV-3D-01	4365	1835	1830	AutoData1 Opel Monterey B RS specifications	https://www.autodata1.com/en/car/opel/monterey/monterey-b-rs-35-v6-24v-215-hp-4x4
EU-OPEL-MONTEREY-B-SUV-5D-01	4795	1835	1840	Auto-Data Vauxhall Monterey Mk II specifications	https://www.auto-data.net/en/vauxhall-monterey-mk-ii-5-dr-facelift-1998-3.5-v6-24v-215hp-6070
EU-ALFA-ROMEO-2000-BERLINA-10512-SEDAN-4D-01	4390	1565	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/71840/alfa_romeo_2000_berlina.html
EU-MITSUBISHI-I-MIEV-HATCHBACK-5D-01	3475	1475	1610	Mitsubishi i-MiEV brochure	https://cdn.sgpetch.co.uk/content/vehicle_media/Mitsubishi/I_MIEV_pdf_brochure.pdf
EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	3975	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Giardinetta 1.3	https://www.automobile-catalog.com/car/1979/143135/alfa_romeo_alfasud_giardinietta_1_3.html
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-PREFL-01	4205	1660	1330	Automobile-Catalog Alfa Romeo Alfetta GTV 2000	https://www.automobile-catalog.com/car/1977/144020/alfa_romeo_alfetta_gtv_2000.html
EU-ALFA-ROMEO-ALFETTA-116-COUPE-GTV2000-FACELIFT-01	4260	1664	1330	Automobile-Catalog Alfa Romeo GTV 2.0 specifications	https://www.automobile-catalog.com/car/1984/144125/alfa_romeo_gtv_2_0.html
EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	4160	1560	1430	Auto Motor und Sport Alfa Romeo Giulia 105/115 specifications	https://www.auto-motor-und-sport.de/marken-modelle/alfa-romeo/giulia/typ-105-115/technische-daten/
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764	Auto-Data Ford Galaxy II facelift	https://www.auto-data.net/en/ford-galaxy-ii-facelift-2010-2.2-tdci-200hp-51885
EU-BMW-7-F01-SEDAN-SWB-PREFL-01	5072	1902	1479	Auto-Data BMW 7 Series F01/F02 generation	https://www.auto-data.net/en/bmw-7-series-model-945
EU-BMW-7-F01-SEDAN-SWB-FACELIFT-01	5079	1902	1471	BMW 730i and 730Li official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0131447EN/207820
EU-BMW-7-F02-SEDAN-LWB-PREFL-01	5212	1902	1484	SGCarMart BMW 730Li specifications	https://www.sgcarmart.com/new_cars/newcars_print.php?CarCode=10097&Subcode=191
EU-BMW-7-F02-SEDAN-LWB-FACELIFT-01	5219	1902	1481	BMW 730i and 730Li official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0131447EN/207820
EU-JEEP-COMPASS-I-SUV-FACELIFT-01	4448	1812	1663	Jeep Compass 2011 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Jeep-Compass-UK.pdf
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data;Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-s-250-cdi-blueefficiency-204hp-7g-tronic-plus-36924;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data;Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-350-cdi-bluetec-258hp-4matic-g-tronic-36888;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-250-CDI-BlueEFFICIENCY-lang-2011---2013.xhtml?oid=191730294
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473	Bind Mercedes-Benz S 63 AMG W221 facelift	https://bind.lt/en/technical-specifications/mercedes-benz/s-class/w221-restyling/amg-sedan-4-doors/s-63-performance-package-speedshift-mct-571-hp
EU-BMW-1-SERIES-M-E82-COUPE-2D-01	4380	1803	1420	BMW Group PressClub;Auto-Data	https://www.press.bmwgroup.com/global/article/detail/T0091933EN/the-bmw-1-series-m-coupe?language=en;https://www.auto-data.net/en/bmw-1m-model-3458
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478	AutoData1 Mercedes-Benz S 65 AMG V221	https://www.autodata1.com/en/car/mercedes-benz/s-class/s-class-w221-amg-s-65-612-hp
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-BlueEFFICIENCY-Estate-2009---2011.xhtml?oid=189508160
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Mercedes-Benz C-Class Saloon and Estate brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/C-Class_saloon_estate_W204_S204_0613.pdf
EU-HYUNDAI-I10-PA-HATCHBACK-5D-FACELIFT-01	3565	1595	1540	Hyundai i10 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Hyundai-i10-UK.pdf
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	BMW Group PressClub MINI Cooper specifications	https://www.press.bmwgroup.com/global/article/attachment/T0076947EN/114936
EU-MINI-MINI-R55-CLUBMAN-WAGON-5D-FACELIFT-01	3961	1683	1426	MINI Corporate Communications specifications;Automobile-Catalog	https://libraryofmotoring.info/pdf/specifications/2011-mini-cooper-sd-clubman.pdf;https://www.automobile-catalog.com/car/2011/1754780/mini_cooper_d_clubman.html
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414	AutoData1 MINI Convertible R57 facelift Cooper SD	https://www.autodata1.com/en/car/mini/convertible/convertible-r57-facelift-2011-cooper-sd-20-143-hp-automatic
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I	https://www.auto-data.net/en/ford-focus-hatchback-i-1.8-16v-115hp-7364
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I	https://www.auto-data.net/en/ford-focus-hatchback-i-1.8-16v-115hp-7364
EU-AUDI-TT-8N-COUPE-FWD-01	4041	1764	1346	Audi UK technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-AUDI-TT-8N-COUPE-QUATTRO-01	4041	1764	1345	Audi UK technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	CarsGuide Volkswagen Polo 1996 dimensions	https://www.carsguide.com.au/volkswagen/polo/car-dimensions/1996
EU-MAZDA-323-BJ-SEDAN-PREFL-01	4315	1705	1410	Automobile-Catalog Mazda 323 S specifications	https://www.automobile-catalog.com/car/1998/1672175/mazda_323_s_2_0_d.html
EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	4365	1705	1410	Automobile-Catalog Mazda 323 S specifications	https://www.automobile-catalog.com/car/2001/1672325/mazda_323_s_1_6.html
EU-MAZDA-323-BJ-HATCHBACK-PREFL-01	4200	1705	1410	Automobile-Catalog Mazda 323 F specifications	https://www.automobile-catalog.com/car/1998/1672295/mazda_323_f_2_0_td.html
EU-MAZDA-323-BJ-HATCHBACK-FACELIFT-01	4250	1705	1420	ADAC Mazda 323 BJ facelift specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mazda/323/bj-facelift/994371/
EU-MERCEDES-BENZ-CLK-A208-CONVERTIBLE-2D-01	4567	1722	1380	Australian Car.Reviews Mercedes-Benz A208 CLK Cabriolet	https://australiancar.reviews/review-mercedes-benz-a208-clk-cabriolet-1998-03/
EU-MINI-COUNTRYMAN-R60-SUV-5D-01	4097	1789	1561	MINI Countryman technical specifications	https://www.ausmotive.com/downloads/MINI/Countryman-tech-specs-Feb2011.pdf
EU-FSO-125P-SEDAN-PREFL-01	4233	1625	1440	Automobile-Catalog Polski Fiat 125p 1300	https://www.automobile-catalog.com/car/1972/29645/polski_fiat_125p_1300.html
EU-FSO-125P-SEDAN-FACELIFT-01	4226	1630	1440	Automobile-Catalog Polski Fiat 125p 1300	https://www.automobile-catalog.com/car/1980/39365/polski_fiat_125p_1300.html
EU-FSO-125P-WAGON-PREFL-01	4234	1625	1473	Automobile-Catalog Polski Fiat 125p 1500 Kombi	https://www.automobile-catalog.com/car/1972/2736170/polski_fiat_125p_1500_kombi.html
EU-FSO-125P-WAGON-FACELIFT-01	4234	1630	1473	Automobile-Catalog Polski Fiat 125p 1500 Kombi	https://www.automobile-catalog.com/car/1980/27515/polski_fiat_125p_kombi_1500.html
EU-FSO-126P-HATCHBACK-2D-600-01	3054	1377	1335	Automobile-Catalog Polski Fiat 126p 600	https://www.automobile-catalog.com/car/1977/38975/polski_fiat_126p_600.html
EU-FSO-132P-SEDAN-SERIES2-01	4405	1640	1425	Automobile-Catalog Fiat 132 Series II	https://www.automobile-catalog.com/car/1974/713495/fiat_132_gls_1600.html
EU-FSO-132P-SEDAN-SERIES3-01	4400	1640	1420	CarsGuide Fiat 132 1978 dimensions	https://www.carsguide.com.au/fiat/132/car-dimensions/1978
EU-FSO-127P-HATCHBACK-3D-01	3595	1527	1370	Automobile-Catalog Fiat 127 body specification	https://www.automobile-catalog.com/car/1972/711230/fiat_127.html
EU-SAAB-9-3X-II-WAGON-5D-01	4690	1802	1527	Automobile-Catalog Saab 9-3X 2.0T XWD	https://www.automobile-catalog.com/car/2011/3038660/saab_9-3x_2_0t_xwd_automatic.html
EU-FSO-POLONEZ-I-HATCHBACK-5D-01	4272	1651	1420	Automobile-Catalog FSO Polonez 1500 Lux	https://www.automobile-catalog.com/car/1981/2736515/fso_polonez_1500.html
EU-HYUNDAI-IX35-LM-SUV-PREFL-01	4410	1820	1660	Hyundai ix35 2011 owner manual	https://www.carmanualsonline.info/hyundai-ix35-2011-owners-manual/?srch=dimensions
EU-HYUNDAI-IX35-LM-SUV-FACELIFT-01	4410	1820	1655	Hyundai ix35 2014 owner manual	https://www.carmanualsonline.info/hyundai-ix35-2014-owners-manual/?srch=dimensions
EU-FSO-POLONEZ-II-HATCHBACK-5D-01	4322	1651	1420	Automobile-Catalog FSO Polonez 1.5 SLE	https://www.automobile-catalog.com/car/1990/2736905/fso_polonez_1_5_sle.html
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-PREFL-01	4250	1790	1450	Kia cee'd Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-FACELIFT-01	4250	1790	1450	Auto-Data	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
EU-HYUNDAI-H1-STAREX-I-MPV-4WD-01	4695	1820	1885	Automobile-Catalog Hyundai Starex 2400 HSV 4x4	https://www.automobile-catalog.com/car/1998/1167770/hyundai_starex_2400_hsv_4x4.html
EU-FSO-POLONEZ-III-CARO-HATCHBACK-PREFL-01	4318	1650	1420	Automobile-Catalog FSO Polonez Caro 1.6 GLi	https://www.automobile-catalog.com/car/1992/2737040/fso_polonez_caro_1_6_gli.html
EU-FSO-POLONEZ-III-CARO-PLUS-HATCHBACK-FACELIFT-01	4369	1650	1420	Automobile-Catalog FSO Polonez Caro Plus 1.6 GSi	https://www.automobile-catalog.com/car/1999/2737250/fso_polonez_caro_plus_1_6_gsi.html
EU-FSO-POLONEZ-III-ATU-SEDAN-PREFL-01	4318	1650	1420	Automobile-Catalog FSO Polonez Atu 1.6 GLi	https://www.automobile-catalog.com/car/1996/2737190/fso_polonez_atu_1_6_gli.html
EU-FSO-POLONEZ-III-ATU-PLUS-SEDAN-FACELIFT-01	4369	1650	1420	Automobile-Catalog FSO Polonez Atu Plus 1.6 GSi	https://www.automobile-catalog.com/car/1999/2737280/fso_polonez_atu_plus_1_6_gsi.html
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-01	4868	1854	1470	Mercedes-Benz E-Class Saloon official brochure	https://ragtop.org/mbbrochures/2010/international/E-Class_WS212_1109_02.pdf
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474	Mercedes-Benz E-Class Saloon and Estate official brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/E-Class_saloon_estate_W212_S212_0413.pdf
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690	BMW Group PressClub 2008 X6 technical data	https://www.press.bmwgroup.com/usa/article/attachment/T0020002EN_US/38642
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699	BMW Group PressClub X6 specifications 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124596EN/207899
EU-PORSCHE-PANAMERA-970-HATCHBACK-TURBO-S-01	4970	1931	1418	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-turbo-s-4.8-v8-550hp-pdk-56301
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-01	4290	1753	1415	Vauxhall Astra 2009 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1467	Vauxhall Astra 2009 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_August_2008.pdf
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486	Auto-Data Saab 9-3 Sedan II Griffin	https://www.auto-data.net/en/saab-9-3-sedan-ii-griffin-facelift-2011-1.9-ttid-160hp-54571
EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	4214	1684	1607	Skoda Roomster international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Skoda-Roomster-2012-INT.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8701-8800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1974/713495/fiat_132_gls_1600.html?utm_source=chatgpt.com "1974 Fiat 132 GLS 1600 Specs Review (72 kW / 98 PS ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8701-8800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8701-8800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10932 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3413 行）

- 尺寸冲突协调：
  - EU-MINI-COUNTRYMAN-R60-SUV-5D-01 -> EU-MINI-COUNTRYMAN-R60-SUV-5D-02：4110x1789x1561 与 4097x1789x1561，创建新尺寸组
