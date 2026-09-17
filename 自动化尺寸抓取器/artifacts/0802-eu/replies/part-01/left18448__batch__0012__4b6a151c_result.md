# 任务：left18448 第 1101-1200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0012__4b6a151c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1101-1200 行

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
left18448.tsv

【当前独立任务】
left18448 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1101-1200_ktype_dimension_mapping_final.tsv
- left18448_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455
EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	4933	1874	1455

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Audi	A6 c7	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Mar 2011	Sep 2018	12075
Audi	A6 c7	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Sep 2014	Sep 2018	108443
Audi	A6 c7	S6 Quattro	Stufenheck	Allrad	Benzin	Feb 2012	Sep 2018	11717
Audi	A6 c7	S6 Quattro	Stufenheck	Allrad	Benzin	Oct 2014	Sep 2018	108559
Audi	A6 c7 avant	1.8 Tfsi	Kombi	Frontantrieb	Benzin	Sep 2014	Sep 2018	108560
Audi	A6 c7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	May 2011	Sep 2018	10413
Audi	A6 c7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	May 2011	Sep 2018	10435
Audi	A6 c7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	Nov 2013	Sep 2018	100059
Audi	A6 c7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	Sep 2014	Sep 2018	108581
Audi	A6 c7 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	Apr 2015	Sep 2018	112282
Audi	A6 c7 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	Jun 2011	Sep 2018	11724
Audi	A6 c7 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	Sep 2014	Sep 2018	108582
Audi	A6 c7 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	May 2015	Sep 2018	115127
Audi	A6 c7 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	May 2015	Sep 2018	115195
Audi	A6 c7 avant	2.8 FSI	Kombi	Frontantrieb	Benzin	May 2011	Apr 2015	10396
Audi	A6 c7 avant	2.8 FSI Quattro	Kombi	Allrad	Benzin	May 2011	Apr 2015	10399
Audi	A6 c7 avant	2.8 FSI Quattro	Kombi	Allrad	Benzin	Sep 2014	Sep 2018	118396
Audi	A6 c7 avant	3.0 TDI	Kombi	Frontantrieb	Diesel	May 2011	Sep 2018	10416
Audi	A6 c7 avant	3.0 TDI	Kombi	Frontantrieb	Diesel	Sep 2014	Sep 2018	108585
Audi	A6 c7 avant	3.0 TDI	Kombi	Frontantrieb	Diesel	Sep 2014	Sep 2018	108588
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	May 2011	Sep 2018	10418
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	May 2011	Sep 2018	10429
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Nov 2011	Sep 2018	11716
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Sep 2014	Sep 2018	108590
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Sep 2014	Sep 2018	108591
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Sep 2014	Sep 2018	108592
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Sep 2014	Sep 2018	108593
Audi	A6 c7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	Sep 2014	Sep 2018	108594
Audi	A6 c7 avant	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	May 2011	May 2012	10410
Audi	A6 c7 avant	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	Nov 2011	Sep 2018	12076
Audi	A6 c7 avant	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	Sep 2014	Sep 2018	108599
Audi	A6 c7 avant	RS6 Performance Quattro	Kombi	Allrad	Benzin	Nov 2015	Sep 2018	117769
Audi	A6 c7 avant	RS6 Quattro	Kombi	Allrad	Benzin	Jan 2013	Sep 2018	59276
Audi	A6 c7 avant	S6 Quattro	Kombi	Allrad	Benzin	Feb 2012	Sep 2018	11718
Audi	A6 c7 avant	S6 Quattro	Kombi	Allrad	Benzin	Oct 2014	Sep 2018	108595
Audi	A6 c8	35 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	Nov 2020	-	143622
Audi	A6 c8	40 TDI	Stufenheck	Frontantrieb	Diesel	Feb 2019	-	144064
Audi	A6 c8	40 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	Jul 2018	-	143623
Audi	A6 c8	40 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	150779
Audi	A6 c8	45 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	Jan 2021	-	143058
Audi	A6 c8	45 TDI Quattro	Stufenheck	Allrad	Diesel	Jul 2019	-	144063
Audi	A6 c8	50 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	Feb 2021	-	143949
Audi	A6 c8	55 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	Feb 2021	-	146513
Audi	A6 c8	S6 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	Jan 2021	-	144062
Audi	A6 c8 avant	35 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	Oct 2020	-	143625
Audi	A6 c8 avant	40 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Jan 2021	-	150780
Audi	A6 c8 avant	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	Jan 2021	-	143059
Audi	A6 c8 avant	45 TDI Quattro	Kombi	Allrad	Diesel	Jul 2019	-	143951
Audi	A6 c8 avant	50 Tfsi E Quattro	Kombi	Allrad	Benzin/Elektro	Feb 2021	-	143950
Audi	A6 c8 avant	RS6 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	Jan 2023	-	151533
Audi	A6 c8 avant	S6 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	Nov 2020	-	143493
Audi	A6 c9	2.0 TDI Mhev Plus	Stufenheck	Frontantrieb	Diesel/Elektro	Apr 2025	-	161528
Audi	A6 c9	2.0 TDI Mhev Plus Quattro	Stufenheck	Allrad	Diesel/Elektro	Apr 2025	-	161531
Audi	A6 c9	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	Apr 2025	-	161526
Audi	A6 c9	2.0 Tfsi Mhev Quattro	Stufenheck	Allrad	Benzin/Elektro	Feb 2026	-	163610
Audi	A6 c9	2.0 Tfsi Phev Quattro	Stufenheck	Allrad	Benzin/Elektro	Apr 2025	-	161875
Audi	A6 c9	2.0 Tfsi Phev Quattro	Stufenheck	Allrad	Benzin/Elektro	Apr 2025	-	161876
Audi	A6 c9	3.0 TDI Mhev Plus Quattro	Stufenheck	Allrad	Diesel/Elektro	Oct 2025	-	163229
Audi	A6 c9	3.0 Tfsi Mhev Plus Quattro	Stufenheck	Allrad	Benzin/Elektro	Apr 2025	-	161527
Audi	A6 c9 avant	2.0 TDI Mhev Plus	Kombi	Frontantrieb	Diesel/Elektro	May 2025	-	161009
Audi	A6 c9 avant	2.0 TDI Mhev Plus Quattro	Kombi	Allrad	Diesel/Elektro	May 2025	-	161010
Audi	A6 c9 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	May 2025	-	161005
Audi	A6 c9 avant	2.0 Tfsi Mhev Quattro	Kombi	Allrad	Benzin/Elektro	Jun 2026	-	163615
Audi	A6 c9 avant	2.0 Tfsi Phev Quattro	Kombi	Allrad	Benzin/Elektro	May 2025	-	161719
Audi	A6 c9 avant	2.0 Tfsi Phev Quattro	Kombi	Allrad	Benzin/Elektro	Apr 2025	-	161874
Audi	A6 c9 avant	3.0 TDI Mhev Plus Quattro	Kombi	Allrad	Diesel/Elektro	Oct 2025	-	163228
Audi	A6 c9 avant	3.0 Tfsi Mhev Plus Quattro	Kombi	Allrad	Benzin/Elektro	May 2025	-	161008
Audi	A6 e-Tron avant	83	Kombi	Heckantrieb	Elektro	Oct 2024	-	160002
Audi	A6 e-Tron avant	100 Quattro	Kombi	Allrad	Elektro	Oct 2024	-	160005
Audi	A6 e-Tron avant	Performance	Kombi	Heckantrieb	Elektro	Jul 2024	-	159453
Audi	A6 e-Tron avant	S6 Quattro	Kombi	Allrad	Elektro	Jul 2024	-	159456
Audi	A6 e-Tron sportback	83	Schrägheck	Heckantrieb	Elektro	Oct 2024	-	160000
Audi	A6 e-Tron sportback	100 Quattro	Schrägheck	Allrad	Elektro	Oct 2024	-	160004
Audi	A6 e-Tron sportback	Performance	Schrägheck	Heckantrieb	Elektro	Jul 2024	-	159450
Audi	A6 e-Tron sportback	S6 Quattro	Schrägheck	Allrad	Elektro	Jul 2024	-	159452
Audi	A7 sportback	1.8 Tfsi	Schrägheck	Frontantrieb	Benzin	Apr 2015	May 2018	115128
Audi	A7 sportback	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Sep 2014	May 2018	107858
Audi	A7 sportback	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2015	May 2018	115129
Audi	A7 sportback	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2015	May 2018	115196
Audi	A7 sportback	2.8 FSI Quattro	Schrägheck	Allrad	Benzin	Oct 2010	Mar 2015	34939
Audi	A7 sportback	3.0 TDI	Schrägheck	Frontantrieb	Diesel	Jul 2014	May 2018	107348
Audi	A7 sportback	3.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2015	May 2018	117764
Audi	A7 sportback	3.0 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2015	May 2018	117950
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Nov 2011	Mar 2015	11790
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Oct 2010	Jun 2016	34941
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	May 2013	Jun 2017	58357
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Jul 2014	May 2018	107347
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	May 2014	May 2018	107350
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	May 2014	May 2018	107351
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Jul 2014	May 2018	107509
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Sep 2014	May 2018	107859
Audi	A7 sportback	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	Nov 2015	May 2018	117765
Audi	A7 sportback	3.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	Oct 2010	May 2012	34940
Audi	A7 sportback	3.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2014	May 2018	107349
Audi	A7 sportback	3.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	May 2016	May 2018	143953
Audi	A7 sportback	35 TDI Mild Hybrid	Schrägheck	Frontantrieb	Diesel/Elektro	Oct 2020	-	147279
Audi	A7 sportback	40 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2020	-	146096
Audi	A7 sportback	40 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2020	-	150553
Audi	A7 sportback	45 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	Jan 2021	-	143061
Audi	A7 sportback	50 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	Feb 2021	-	143954


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 **Audi A6 C7 普通版、S6、RS6** 的轿车及 Avant 外廓聚类。
* 普通 A6 C7 轿车直接复用跨批次已有的改款前、改款后两个尺寸组，不重复输出尺寸组记录。
* 本轮首次闭合 7 个尺寸组：普通 Avant 前后期、S6 Sedan 前后期、S6 Avant 前后期及 RS6 Avant。A6/S6 官方技术资料和车型手册支持这些前后期尺寸边界；RS6 前后期三维相同，因此两个 BodyCode 分支复用同一尺寸组。([奥迪新闻中心][1])
* 对生产期跨越 2014 年改款的 Ktype，按 `prefl`、`facelift` 拆分映射；拆分后不保留无后缀基础行。

## 当前批次进度

* 输入 Ktype 总数：100
* 已完成输入 Ktype：35
* 本轮 READY 映射行：50
* 待处理输入 Ktype：65
* 已确认并引用尺寸组：9

  * 跨批次复用：2
  * 本轮首次创建：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12075_prefl	12075	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前4G2轿车外廓。	READY
12075_facelift	12075	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后4GC轿车外廓。	READY
108443	108443	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	HIGH	改款后4GC轿车外廓。	READY
11717_prefl	11717	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-S6-4G2-SEDAN-PREFL-01	HIGH	S6改款前4G2轿车外廓。	READY
11717_facelift	11717	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	HIGH	S6改款后4GC轿车外廓。	READY
108559	108559	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	HIGH	S6改款后4GC轿车外廓。	READY
108560	108560	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10413_prefl	10413	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10413_facelift	10413	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10435_prefl	10435	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10435_facelift	10435	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
100059_prefl	100059	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
100059_facelift	100059	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108581	108581	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
112282	112282	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
11724_prefl	11724	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
11724_facelift	11724	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108582	108582	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
115127	115127	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
115195	115195	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10396_prefl	10396	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10396_facelift	10396	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10399_prefl	10399	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10399_facelift	10399	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
118396	118396	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10416_prefl	10416	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10416_facelift	10416	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108585	108585	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108588	108588	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10418_prefl	10418	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10418_facelift	10418	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10429_prefl	10429	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10429_facelift	10429	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
11716_prefl	11716	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
11716_facelift	11716	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108590	108590	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108591	108591	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108592	108592	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108593	108593	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108594	108594	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10410	10410	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	改款前4G5 Avant外廓。	READY
12076_prefl	12076	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
12076_facelift	12076	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108599	108599	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
117769	117769	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6 Performance改款后4GD Avant车身。	READY
59276_prefl	59276	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6改款前4G5 Avant车身。	READY
59276_facelift	59276	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6改款后4GD Avant车身；三维未变化，复用同组。	READY
11718_prefl	11718	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-S6-4G5-WAGON-PREFL-01	HIGH	S6改款前4G5 Avant外廓。	READY
11718_facelift	11718	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	HIGH	S6改款后4GD Avant外廓。	READY
108595	108595	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	HIGH	S6改款后4GD Avant外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C7-S6-4G2-SEDAN-PREFL-01	4931	1874	1440	Audi S6 C7 Technical Data UK	https://press.audi.co.uk/assets/documents/original/18642-AudiUK00000036S6C7TechnicalDataUK.pdf
EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	4931	1874	1430	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	4943	1874	1461	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	4926	1874	1461	Audi A6 Saloon and Avant official UK brochure	https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf
EU-AUDI-A6-C7-RS6-WAGON-01	4979	1936	1461	Audi RS 6 Avant technical data	https://www.ausmotive.com/downloads/Audi/RS6-Avant-AU-tech-data-July2013.pdf
EU-AUDI-A6-C7-S6-4G5-WAGON-PREFL-01	4934	1874	1446	Audi S6 C7 Technical Data UK	https://press.audi.co.uk/assets/documents/original/18642-AudiUK00000036S6C7TechnicalDataUK.pdf
EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	4942	1874	1436	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
```

## 下一步优先处理

1. 闭合 A6 C8 普通 Sedan、普通 Avant、S6 Sedan、S6 Avant 和 RS6 Avant 尺寸组。
2. 处理 A6 C9 Sedan/Avant，并核对 2025 与 2026 输入是否存在导致三维变化的版本边界。
3. 闭合 A6 e-tron Avant、Sportback 两种外廓。
4. 最后处理 A7 C7 前后期及 A7 C8，将剩余 Ktype 批量关联到缓存尺寸组。

推进信号：CONTINUE

[1]: https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf?utm_source=chatgpt.com "The new Audi A6 Saloon and Avant Pricing and Specification ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1101-1200_ktype_dimension_mapping_final.tsv
- left18448_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 A6 C8 普通 Sedan/Avant、S6 Sedan/Avant 和 RS6 Avant 五种外廓，尺寸采用 Audi 官方尺寸图。([audi.com][1])
* 已闭合 A6 C9 Sedan/Avant、A6 e-tron Avant/Sportback，以及 A7 C7 改款前后和 A7 C8 Sportback；A6 e-tron 官方资料明确给出不含后视镜宽度。([Audi EMEA][2])
* 已完成轻量机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，无孤立尺寸组，三维及来源均完整。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：119
* PENDING：0
* 完整尺寸组：21
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12075_prefl	12075	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前4G2轿车外廓。	READY
12075_facelift	12075	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后4GC轿车外廓。	READY
108443	108443	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	HIGH	改款后4GC轿车外廓。	READY
11717_prefl	11717	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-S6-4G2-SEDAN-PREFL-01	HIGH	S6改款前4G2轿车外廓。	READY
11717_facelift	11717	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	HIGH	S6改款后4GC轿车外廓。	READY
108559	108559	Sedan	A6 C7	4GC	4	EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	HIGH	S6改款后4GC轿车外廓。	READY
108560	108560	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10413_prefl	10413	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10413_facelift	10413	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10435_prefl	10435	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10435_facelift	10435	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
100059_prefl	100059	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
100059_facelift	100059	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108581	108581	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
112282	112282	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
11724_prefl	11724	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
11724_facelift	11724	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108582	108582	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
115127	115127	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
115195	115195	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10396_prefl	10396	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10396_facelift	10396	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10399_prefl	10399	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10399_facelift	10399	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
118396	118396	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10416_prefl	10416	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10416_facelift	10416	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108585	108585	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108588	108588	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10418_prefl	10418	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10418_facelift	10418	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
10429_prefl	10429	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
10429_facelift	10429	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
11716_prefl	11716	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
11716_facelift	11716	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108590	108590	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108591	108591	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108592	108592	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108593	108593	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
108594	108594	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
10410	10410	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	改款前4G5 Avant外廓。	READY
12076_prefl	12076	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	HIGH	Ktype覆盖改款前4G5 Avant外廓。	READY
12076_facelift	12076	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	Ktype覆盖改款后4GD Avant外廓。	READY
108599	108599	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	HIGH	改款后4GD Avant外廓。	READY
117769	117769	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6 Performance改款后4GD Avant车身。	READY
59276_prefl	59276	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6改款前4G5 Avant车身。	READY
59276_facelift	59276	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-RS6-WAGON-01	HIGH	RS6改款后4GD Avant车身；三维未变化，复用同组。	READY
11718_prefl	11718	Wagon	A6 C7	4G5	5	EU-AUDI-A6-C7-S6-4G5-WAGON-PREFL-01	HIGH	S6改款前4G5 Avant外廓。	READY
11718_facelift	11718	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	HIGH	S6改款后4GD Avant外廓。	READY
108595	108595	Wagon	A6 C7	4GD	5	EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	HIGH	S6改款后4GD Avant外廓。	READY
143622	143622	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
144064	144064	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
143623	143623	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
150779	150779	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
143058	143058	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
144063	144063	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
143949	143949	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
146513	146513	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	A6 C8四门轿车外廓。	READY
144062	144062	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-S6-4A2-SEDAN-01	HIGH	S6 C8四门轿车外廓。	READY
143625	143625	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	A6 C8五门Avant外廓。	READY
150780	150780	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	A6 C8五门Avant外廓。	READY
143059	143059	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	A6 C8五门Avant外廓。	READY
143951	143951	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	A6 C8五门Avant外廓。	READY
143950	143950	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	A6 C8五门Avant外廓。	READY
151533	151533	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-RS6-4A5-WAGON-01	HIGH	RS6 C8宽体Avant外廓。	READY
143493	143493	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-S6-4A5-WAGON-01	HIGH	S6 C8五门Avant外廓。	READY
161528	161528	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161531	161531	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161526	161526	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
163610	163610	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161875	161875	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161876	161876	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
163229	163229	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161527	161527	Sedan	A6 C9		4	EU-AUDI-A6-C9-SEDAN-01	HIGH	A6 C9四门轿车外廓。	READY
161009	161009	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
161010	161010	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
161005	161005	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
163615	163615	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
161719	161719	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
161874	161874	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
163228	163228	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
161008	161008	Wagon	A6 C9		5	EU-AUDI-A6-C9-WAGON-01	HIGH	A6 C9五门Avant外廓。	READY
160002	160002	Wagon	A6 e-tron		5	EU-AUDI-A6-E-TRON-WAGON-01	HIGH	PPE纯电五门Avant外廓。	READY
160005	160005	Wagon	A6 e-tron		5	EU-AUDI-A6-E-TRON-WAGON-01	HIGH	PPE纯电五门Avant外廓。	READY
159453	159453	Wagon	A6 e-tron		5	EU-AUDI-A6-E-TRON-WAGON-01	HIGH	PPE纯电五门Avant外廓。	READY
159456	159456	Wagon	A6 e-tron		5	EU-AUDI-A6-E-TRON-WAGON-01	HIGH	PPE纯电五门Avant外廓。	READY
160000	160000	Hatchback	A6 e-tron		5	EU-AUDI-A6-E-TRON-SPORTBACK-01	HIGH	PPE纯电五门Sportback外廓。	READY
160004	160004	Hatchback	A6 e-tron		5	EU-AUDI-A6-E-TRON-SPORTBACK-01	HIGH	PPE纯电五门Sportback外廓。	READY
159450	159450	Hatchback	A6 e-tron		5	EU-AUDI-A6-E-TRON-SPORTBACK-01	HIGH	PPE纯电五门Sportback外廓。	READY
159452	159452	Hatchback	A6 e-tron		5	EU-AUDI-A6-E-TRON-SPORTBACK-01	HIGH	PPE纯电五门Sportback外廓。	READY
115128	115128	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
107858	107858	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
115129	115129	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
115196	115196	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
34939_prefl	34939	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-PREFL-01	HIGH	Ktype覆盖2014年改款前Sportback外廓。	READY
34939_facelift	34939	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	Ktype覆盖2014年改款后Sportback外廓。	READY
107348	107348	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
117764	117764	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
117950	117950	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
11790_prefl	11790	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-PREFL-01	HIGH	Ktype覆盖2014年改款前Sportback外廓。	READY
11790_facelift	11790	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	Ktype覆盖2014年改款后Sportback外廓。	READY
34941_prefl	34941	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-PREFL-01	HIGH	Ktype覆盖2014年改款前Sportback外廓。	READY
34941_facelift	34941	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	Ktype覆盖2014年改款后Sportback外廓。	READY
58357_prefl	58357	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-PREFL-01	HIGH	Ktype覆盖2014年改款前Sportback外廓。	READY
58357_facelift	58357	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	Ktype覆盖2014年改款后Sportback外廓。	READY
107347	107347	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
107350	107350	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
107351	107351	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
107509	107509	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
107859	107859	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
117765	117765	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
34940	34940	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-PREFL-01	HIGH	2014年改款前五门Sportback外廓。	READY
107349	107349	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
143953	143953	Hatchback	A7 C7		5	EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	HIGH	2014年改款后五门Sportback外廓。	READY
147279	147279	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	A7 C8五门Sportback外廓。	READY
146096	146096	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	A7 C8五门Sportback外廓。	READY
150553	150553	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	A7 C8五门Sportback外廓。	READY
143061	143061	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	A7 C8五门Sportback外廓。	READY
143954	143954	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH	A7 C8五门Sportback外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1101-1200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455	Audi A6 Saloon and Avant official UK brochure	https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf
EU-AUDI-A6-C7-4GC-SEDAN-FACELIFT-01	4933	1874	1455	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C7-S6-4G2-SEDAN-PREFL-01	4931	1874	1440	Audi S6 C7 Technical Data UK	https://press.audi.co.uk/assets/documents/original/18642-AudiUK00000036S6C7TechnicalDataUK.pdf
EU-AUDI-A6-C7-S6-4GC-SEDAN-FACELIFT-01	4931	1874	1430	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C7-4GD-WAGON-FACELIFT-01	4943	1874	1461	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C7-4G5-WAGON-PREFL-01	4926	1874	1461	Audi A6 Saloon and Avant official UK brochure	https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf
EU-AUDI-A6-C7-RS6-WAGON-01	4979	1936	1461	Audi RS 6 Avant technical data	https://www.ausmotive.com/downloads/Audi/RS6-Avant-AU-tech-data-July2013.pdf
EU-AUDI-A6-C7-S6-4G5-WAGON-PREFL-01	4934	1874	1446	Audi S6 C7 Technical Data UK	https://press.audi.co.uk/assets/documents/original/18642-AudiUK00000036S6C7TechnicalDataUK.pdf
EU-AUDI-A6-C7-S6-4GD-WAGON-FACELIFT-01	4942	1874	1436	Audi A6/S6 Saloon and Avant UK brochure (2015)	https://xr793.com/wp-content/uploads/2022/10/2015-Audi-A6-S6-Saloon-Avant-UK.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi A6 Sedan official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-sedan-1403/download
EU-AUDI-A6-C8-S6-4A2-SEDAN-01	4964	1886	1446	Audi S6 Sedan TDI official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-s6-sedan-tdi-1405/download
EU-AUDI-A6-C8-4A5-WAGON-01	4939	1886	1494	Audi A6 Avant official dimensions	https://www.audi.com/de/publikationen/abmessungen/abmessungen-a6-avant-1400/download
EU-AUDI-A6-C8-RS6-4A5-WAGON-01	4995	1951	1460	Audi RS 6 Avant official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-rs-6-avant-1431/download
EU-AUDI-A6-C8-S6-4A5-WAGON-01	4964	1886	1481	Audi S6 Avant TDI official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-s6-avant-tdi-1404/download
EU-AUDI-A6-C9-SEDAN-01	4999	1875	1452	Audi A6 Sedan official technical data (2025)	https://emea-dam.audi.com/adobe/assets/urn%3Aaaid%3Aaem%3Ad1fc5489-95a6-422d-9f73-b345904e94df/original/as/AudiA6-%28C9%29_2025_EN_Public_NoPR.pdf
EU-AUDI-A6-C9-WAGON-01	4999	1897	1472	Audi A6 Avant official dimensions (2025)	https://media.audi.com/is/content/audi/nemo/models/a6/a6-avant/my-2025-nf/dimensions/a6-avant-dimensions-1.pdf
EU-AUDI-A6-E-TRON-WAGON-01	4928	1923	1527	Audi A6 e-tron official press kit	https://www.audi-mediacenter.com/en/the-audi-a6-e-tron-the-new-electric-avant-garde-16391/download
EU-AUDI-A6-E-TRON-SPORTBACK-01	4928	1923	1487	Audi A6 e-tron official press kit	https://www.audi-mediacenter.com/en/the-audi-a6-e-tron-the-new-electric-avant-garde-16391/download
EU-AUDI-A7-C7-SPORTBACK-FACELIFT-01	4974	1911	1420	Audi A7 Sportback official UK press information	https://press.audi.co.uk/assets/documents/original/19236-AudiUK00000403AudiA7SportbackFullUK.pdf
EU-AUDI-A7-C7-SPORTBACK-PREFL-01	4969	1911	1420	Audi A7 Sportback official UK brochure (2010)	https://xr793.com/wp-content/uploads/2022/10/2010-Audi-A7-Sept-10-UK.pdf
EU-AUDI-A7-C8-4KA-SPORTBACK-01	4969	1908	1422	Audi A7 Sportback official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a7-sportback-1406/download
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1101-1200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.audi.com/en/publications/dimensions/dimensions-a6-sedan-1403/download "A6 Limousine MA Abmessungen 0523"
[2]: https://emea-dam.audi.com/adobe/assets/urn%3Aaaid%3Aaem%3Ad1fc5489-95a6-422d-9f73-b345904e94df/original/as/AudiA6-%28C9%29_2025_EN_Public_NoPR.pdf "AudiA6(C9)_2025_EN_Public_NoPR"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1431 行）
- 累计尺寸组：dimension_groups_final.tsv（453 行）

