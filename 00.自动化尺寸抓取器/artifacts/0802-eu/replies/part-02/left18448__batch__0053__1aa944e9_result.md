# 任务：left18448 第 5201-5300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0053__1aa944e9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5201-5300 行

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
left18448 第 5201-5300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FIAT-TALENTO-290-CHASSISCAB-01	4157	1965	2100
EU-FIAT-TALENTO-290-STANDARD-BODY-01	4157	1965	2100
EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	5399	1956	1971
EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	4999	1956	1971
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	Jun 2016	-	120656
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2016	-	120661
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2016	-	120662
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2016	-	120663
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2016	-	120664
Fiat	Talento	1.6 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2016	-	120665
Fiat	Talento	1.6 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2016	-	120666
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	May 2018	-	145404
Fiat	Talento	1.9 D	Kasten	Frontantrieb	Diesel	Mar 1989	Mar 1994	15922
Fiat	Talento	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1989	Mar 1994	15923
Fiat	Talento	1.9 D	Bus	Frontantrieb	Diesel	Mar 1989	Mar 1994	15939
Fiat	Tempra	1.4	Kasten/Kombi	Frontantrieb	Benzin	Apr 1991	Jun 1993	143380
Fiat	Tempra	1.6	Kasten/Kombi	Frontantrieb	Benzin	Apr 1991	Jun 1993	143381
Fiat	Tempra	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	Jun 1993	Jul 1996	143382
Fiat	Tipo	1	Schrägheck	Frontantrieb	Benzin	Nov 2020	-	142956
Fiat	Tipo	1	Kombi	Frontantrieb	Benzin	Nov 2020	-	142958
Fiat	Tipo	1	Stufenheck	Frontantrieb	Benzin	Nov 2020	-	143261
Fiat	Tipo	1.4	Stufenheck	Frontantrieb	Benzin	Oct 2015	-	117867
Fiat	Tipo	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2016	-	119838
Fiat	Tipo	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2016	Oct 2020	119841
Fiat	Tipo	1.4	Kombi	Frontantrieb	Benzin	Mar 2016	Oct 2020	119843
Fiat	Tipo	1.4	Kombi	Frontantrieb	Benzin	Mar 2016	Oct 2020	119849
Fiat	Tipo	1.6	Stufenheck	Frontantrieb	Benzin	Oct 2015	Oct 2020	117868
Fiat	Tipo	1.6	Schrägheck	Frontantrieb	Benzin	Jul 2016	Oct 2020	122038
Fiat	Tipo	1.6	Kombi	Frontantrieb	Benzin	Jul 2016	Oct 2020	122039
Fiat	Tipo	1.3 D	Stufenheck	Frontantrieb	Diesel	Oct 2015	Oct 2020	117869
Fiat	Tipo	1.3 D	Schrägheck	Frontantrieb	Diesel	Mar 2016	-	119840
Fiat	Tipo	1.3 D	Kombi	Frontantrieb	Diesel	Mar 2016	-	119848
Fiat	Tipo	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	May 1989	Apr 1995	14646
Fiat	Tipo	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	May 2016	Oct 2020	120721
Fiat	Tipo	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	May 2016	Oct 2020	120723
Fiat	Tipo	1.4 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	May 2016	Oct 2020	121442
Fiat	Tipo	1.5 T4 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2022	-	147199
Fiat	Tipo	1.5 T4 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	Mar 2022	-	147200
Fiat	Tipo	1.5 T4 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Mar 2022	-	147708
Fiat	Tipo	1.6 D	Stufenheck	Frontantrieb	Diesel	Oct 2015	Oct 2020	117870
Fiat	Tipo	1.6 D	Schrägheck	Frontantrieb	Diesel	Mar 2016	Oct 2020	119839
Fiat	Tipo	1.6 D	Kombi	Frontantrieb	Diesel	Mar 2016	Oct 2020	119847
Fiat	Tipo	1.6 D	Stufenheck	Frontantrieb	Diesel	Sep 2016	Oct 2020	123395
Fiat	Tipo	1.6 D	Schrägheck	Frontantrieb	Diesel	Sep 2016	Oct 2020	123396
Fiat	Tipo	1.6 D	Kombi	Frontantrieb	Diesel	Sep 2016	Oct 2020	123398
Fiat	Tipo	1.6 Multijet	Schrägheck	Frontantrieb	Diesel	Nov 2020	-	142978
Fiat	Tipo	1.6 Multijet	Kombi	Frontantrieb	Diesel	Nov 2020	-	142981
Fiat	Tipo	1.6 Multijet	Stufenheck	Frontantrieb	Diesel	Nov 2020	-	146860
Fiat	Tipo	1.8 I.E	Schrägheck	Frontantrieb	Benzin	Mar 1993	Apr 1995	18925
Fiat	Tipo	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	Oct 1990	Jun 1993	14643
Fiat	Tipo	1.8 I.e.16v Sport	Schrägheck	Frontantrieb	Benzin	Nov 1989	Jun 1992	13280
Fiat	Topolino	Electric	Schrägheck	Frontantrieb	Elektro	Sep 2023	-	156216
Fiat	Ulysse	1.8	Großraumlimousine	Frontantrieb	Benzin	May 1997	Aug 2002	8847
Fiat	Ulysse	2	Großraumlimousine	Frontantrieb	Benzin	Aug 2002	Jun 2011	16892
Fiat	Ulysse	3	Großraumlimousine	Frontantrieb	Benzin	Aug 2002	Jun 2011	16893
Fiat	Ulysse	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	May 1997	Dec 1999	116063
Fiat	Ulysse	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 1998	Sep 2000	11372
Fiat	Ulysse	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Aug 2002	15815
Fiat	Ulysse	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	Oct 1999	Aug 2002	14159
Fiat	Ulysse	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	Aug 2002	Aug 2006	16894
Fiat	Ulysse	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	May 2003	Aug 2006	17494
Fiat	Ulysse	2.0 JTD 16V	Großraumlimousine	Frontantrieb	Diesel	May 1999	Aug 2002	11753
Fiat	Ulysse	2.0 Multijet 180	Bus	Frontantrieb	Diesel	Jan 2022	Apr 2025	157532
Fiat	Ulysse	2.1 TD	Großraumlimousine	Frontantrieb	Diesel	Mar 1996	Oct 1999	5737
Fiat	Ulysse	2.2 JTD	Großraumlimousine	Frontantrieb	Diesel	Aug 2002	Aug 2006	16895
Fiat	Ulysse	2.2 Multijet 150	Bus	Frontantrieb	Diesel	May 2025	-	802879
Fiat	Ulysse	2.2 Multijet 180	Bus	Frontantrieb	Diesel	May 2025	-	802302
Fiat	Ulysse	E-ulysse	Bus	Frontantrieb	Elektro	Jan 2022	Oct 2023	147265
Fiat	Ulysse	E-ulysse	Bus	Frontantrieb	Elektro	Nov 2023	-	158247
Fiat	Uno	1.1	Schrägheck	Frontantrieb	Benzin	Oct 1988	Jun 2006	55918
Fiat	Uno	1.1	Schrägheck	Frontantrieb	Benzin	Apr 1986	Jun 2006	58803
Fiat	Uno	1.4 Turbo I.e.	Schrägheck	Frontantrieb	Benzin	Dec 1989	Dec 1996	14547
Fiat	Uno	50 1.1	Schrägheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	8862
Fiat	Uno	60 1.1	Schrägheck	Frontantrieb	Benzin	Apr 1989	Dec 1992	14545
Fiat	Uno	70 I.e. 1.4	Schrägheck	Frontantrieb	Benzin	Sep 1989	Dec 1993	14546
Fiat	Uno	70 S 1.4	Schrägheck	Frontantrieb	Benzin	Oct 1988	Jun 2006	15896
Firefly	Firefly	EV	Schrägheck	Heckantrieb	Elektro	Apr 2025	-	161560
Fisker	Karma	2.0 Range Extender	Stufenheck	Heckantrieb	Benzin/Elektro	Feb 2012	-	55253
Fisker	Ocean	Extreme Allrad	SUV	Allrad	Elektro	Feb 2023	-	157313
Fisker	Ocean	ONE Allrad	SUV	Allrad	Elektro	Feb 2023	-	151939
Fisker	Ocean	ONE Allrad	SUV	Allrad	Elektro	Feb 2023	-	155605
Fisker	Ocean	Sport	SUV	Frontantrieb	Elektro	Feb 2023	-	151940
Fisker	Ocean	Ultra Allrad	SUV	Allrad	Elektro	Feb 2023	-	151941
Ford	A-Series	2.4 A0406	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1973	Dec 1982	156213
Ford	A-Series	2.4 A0506	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1973	Dec 1982	156214
Ford	B-Max	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	55466
Ford	B-Max	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	108801
Ford	B-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	55105
Ford	B-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	55106
Ford	B-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	59492
Ford	B-Max	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	108797
Ford	B-Max	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	108800
Ford	B-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Feb 2016	Dec 2017	118618
Ford	B-Max	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 2012	Dec 2017	142732
Ford	B-Max	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Aug 2013	Dec 2017	105988
Ford	B-Max	1.4 LPG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Oct 2012	Dec 2017	142735
Ford	B-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Oct 2012	Dec 2017	55537
Ford	B-Max	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 2012	Dec 2017	108803
Ford	B-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Apr 2015	Dec 2017	113165
Ford	B-Max	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2015	Dec 2017	113677
Ford	B-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Oct 2012	Dec 2017	55108
Ford	B-Max	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 2012	Dec 2017	108804
Ford	B-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	55107
Ford	B-Max	1.6 TI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Dec 2017	108802


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **52 条映射**：Talento 290 共 3 条、Tipo II 共 29 条、Topolino 共 1 条、Ford B-Max 共 19 条。
* Talento 290 直接复用跨批次已有尺寸组，未重复输出尺寸事实。
* Fiat Tipo II 的 Hatchback、Wagon、Sedan 三种外廓已分别建组；官方资料明确列出三种长度、高度及不含后视镜宽度。([Stellantis Media][1])
* Topolino 已按 Fiat 官方技术表闭合为 2535 × 1400 × 1530 mm。([Stellantis Media][2])
* B-Max MPV 与厢式衍生版复用同一外廓；厢式衍生版映射置信度暂定为 `MEDIUM`。([汽车档案馆][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：52
* PENDING 映射：48
* 已确认并引用尺寸组：7
* 本轮首次创建尺寸组：5
* 复用跨批次已有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15922	15922	Van	Talento I	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	HIGH	290 标准车身厢式车。	READY
15923	15923	Pickup	Talento I	290	2	EU-FIAT-TALENTO-290-CHASSISCAB-01	HIGH	290 底盘驾驶室物理车身。	READY
15939	15939	MPV	Talento I	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	HIGH	290 客车复用标准车身外廓。	READY
142956	142956	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
142958	142958	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
143261	143261	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
117867	117867	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119838	119838	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119841	119841	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119843	119843	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
119849	119849	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
117868	117868	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
122038	122038	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
122039	122039	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
117869	117869	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119840	119840	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119848	119848	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
120721	120721	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
120723	120723	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
121442	121442	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
147199	147199	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
147200	147200	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
147708	147708	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
117870	117870	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119839	119839	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119847	119847	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
123395	123395	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
123396	123396	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
123398	123398	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
142978	142978	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
142981	142981	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
146860	146860	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
156216	156216	Hatchback	Topolino (2023)		2	EU-FIAT-TOPOLINO-2023-HATCHBACK-01	HIGH	封闭式双门微型车身。	READY
55466	55466	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108801	108801	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55105	55105	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
55106	55106	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
59492	59492	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108797	108797	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
108800	108800	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
118618	118618	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
142732	142732	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
105988	105988	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
142735	142735	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55537	55537	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108803	108803	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
113165	113165	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
113677	113677	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55108	55108	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108804	108804	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55107	55107	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108802	108802	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TIPO-357-WAGON-01	4571	1792	1514	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TOPOLINO-2023-HATCHBACK-01	2535	1400	1530	Fiat Topolino official technical sheet	https://www.media.stellantis.com/uploads/em/attachment/9567/fiattopolino_technicalsheet-64a4110fb3089.pdf
EU-FORD-B-MAX-B232-MPV-01	4077	1751	1604	Ford B-MAX official brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-B-Max-2012-UK.pdf;https://www.automobile-catalog.com/car/2012/1775780/ford_b-max_1_0_ecoboost_100_titanium.html
```

## 下一步优先处理

1. 闭合 Talento 296 的 Bus、Kasten 与 Pritsche/Fahrgestell分支，优先复用现有 SWB/LWB、低顶/高顶缓存组，并单独确认底盘驾驶室。
2. 按代际集中处理 Ulysse：第一代、第二代以及当前 K0 平台柴油和纯电版本。
3. 处理 Tempra、第一代 Tipo 与 Uno，重点确认三门/五门及改款前后的外廓边界。
4. 最后处理 Firefly、Fisker Karma/Ocean 和 Ford A-Series。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf "TIPO_Family_Cat_52p_PL_04_2_2904_26.indd"
[2]: https://www.media.stellantis.com/uploads/em/attachment/9567/fiattopolino_technicalsheet-64a4110fb3089.pdf "Fiat Topolino_Technical Sheet.xlsx"
[3]: https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-B-Max-2012-UK.pdf?utm_source=chatgpt.com "FORD B-MAX"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 **25 个输入 Ktype**，新增 **39 条 READY 映射行**。
* Talento 296 的 Bus 与 Kasten 已按 SWB/LWB、低顶/高顶派生，并直接复用已有 6 个尺寸组，未重复输出尺寸事实。
* 新建 Ulysse I、Ulysse II、Firefly、Fisker Karma、Fisker Ocean 共 5 个尺寸组。Ulysse II 使用 Fiat 官方规格；Firefly 使用官方用户手册明确的不含后视镜宽度；Fisker 两组采用明确三维规格。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：77
* PENDING 输入 Ktype：23
* READY 映射行：91
* 已确认并引用尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120656_swb	120656	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	SWB低顶客车物理外廓。	READY
120656_lwb	120656	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	LWB低顶客车物理外廓。	READY
120661_swb_lowroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120661_swb_highroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120661_lwb_lowroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120661_lwb_highroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120662_swb_lowroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120662_swb_highroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120662_lwb_lowroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120662_lwb_highroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120663_swb_lowroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120663_swb_highroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120663_lwb_lowroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120663_lwb_highroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120664_swb_lowroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120664_swb_highroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120664_lwb_lowroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120664_lwb_highroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
145404_swb	145404	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	SWB低顶客车物理外廓。	READY
145404_lwb	145404	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	LWB低顶客车物理外廓。	READY
8847	8847	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16892	16892	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
16893	16893	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
116063	116063	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
11372	11372	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
15815	15815	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
14159	14159	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16894	16894	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
17494	17494	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
11753	11753	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
5737	5737	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16895	16895	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
161560	161560	Hatchback	Firefly I		5	EU-FIREFLY-FIREFLY-I-HATCHBACK-01	HIGH	五门纯电掀背车物理外廓。	READY
55253	55253	Sedan	Karma I		4	EU-FISKER-KARMA-I-SEDAN-01	HIGH	四门量产轿车物理外廓。	READY
157313	157313	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151939	151939	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
155605	155605	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151940	151940	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151941	151941	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-ULYSSE-220-MPV-01	4454	1834	1714	Auto-Data Fiat Ulysse I 22/220 generation specifications	https://www.auto-data.net/en/fiat-ulysse-i-22-220-generation-1615
EU-FIAT-ULYSSE-179-MPV-01	4719	1863	1752	Fiat New Ulysse official press kit	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-ulysse
EU-FIREFLY-FIREFLY-I-HATCHBACK-01	4003	1781	1557	Firefly international owner manual	https://cdn-up-public.firefly.world/www-firefly/user-instructions/FIREFLY/index.html
EU-FISKER-KARMA-I-SEDAN-01	4998	1984	1330	Automobile-Catalog 2012 Fisker Karma specifications	https://www.automobile-catalog.com/car/2012/2970215/fisker_karma.html
EU-FISKER-OCEAN-I-SUV-01	4774	1982	1631	Fisker Ocean Specifications press sheet	https://www.autoevolution.com/pdf/news_attachements/first-fisker-ocean-delivery-shuts-up-everyone-who-doubted-the-company-would-make-it-214648.pdf
```

## 下一步优先处理

1. 闭合 Fiat Tempra Kasten/Kombi 与第一代 Tipo。
2. 处理当前代 Ulysse 的 L2/L3、改款前后车身边界。
3. 处理 Fiat Uno 的三门/五门及改款边界。
4. 最后确认 Talento 296 底盘驾驶室和 Ford A-Series A0406/A0506。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-ulysse-i-22-220-generation-1615?utm_source=chatgpt.com "Fiat Ulysse I (22/220) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 **14 个输入 Ktype**，新增 **18 条 READY 映射行**。
* Tempra 商用版按 Tempra S.W./Marengo 外廓统一建组；Tipo I 的三门和五门版本复用相同三维外廓。([汽车目录][1])
* Uno I 按 1989 年改款前后拆分两个尺寸组；同一阶段的三门、五门版本共用相同外廓。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：91
* PENDING 输入 Ktype：9
* READY 映射行：109
* 已确认并引用尺寸组：22
* 剩余：Talento 2 个、Ulysse 5 个、Ford A-Series 2 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143380	143380	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
143381	143381	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
143382	143382	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
14646	14646	Hatchback	Tipo I	160		EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	三门与五门版本共用同一外廓。	READY
18925	18925	Hatchback	Tipo I	160	3	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	改款三门掀背车身。	READY
14643	14643	Hatchback	Tipo I	160	5	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	五门掀背车身。	READY
13280	13280	Hatchback	Tipo I	160	5	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	五门16V运动版车身。	READY
55918_prefl	55918	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
55918_facelift	55918	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
58803_prefl	58803	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
58803_facelift	58803	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14547	14547	Hatchback	Uno I	146	3	EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	HIGH	改款后三门Turbo车身。	READY
8862	8862	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14545_prefl	14545	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
14545_facelift	14545	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14546	14546	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
15896_prefl	15896	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
15896_facelift	15896	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TEMPRA-159-VAN-01	4472	1695	1500	Automobile-Catalog 1991 Fiat Tempra S.W. specifications	https://www.automobile-catalog.com/car/1991/719255/fiat_tempra_s__w__2_0_i_e__sx_automatic.html
EU-FIAT-TIPO-160-HATCHBACK-01	3958	1700	1445	Automobile-Catalog 1989 Fiat Tipo specifications; Automobile-Catalog 1993 Fiat Tipo 3-door specifications	https://www.automobile-catalog.com/car/1989/60620/fiat_tipo_1_1.html;https://www.automobile-catalog.com/car/1993/718490/fiat_tipo_1_4_i_e__s_3p.html
EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	3644	1555	1432	Automobile-Catalog 1983 Fiat Uno 70 S specifications	https://www.automobile-catalog.com/car/1983/715820/fiat_uno_70_s.html
EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	3691	1560	1420	AutoEvolution Fiat Uno 1989-1994 three-door specifications; AutoEvolution Fiat Uno 1989-1994 five-door specifications	https://www.autoevolution.com/cars/fiat-uno-3-doors-1989.html;https://www.autoevolution.com/cars/fiat-uno-5-doors-1989.html
```

## 下一步优先处理

1. 区分 Ulysse III 2022 初始车身与 2023/2024 改款车身，并闭合 Standard、Long 外廓。
2. 确认 Talento 296 底盘驾驶室的 SWB/LWB 分支及完整外廓。
3. 最后闭合 Ford A0406、A0506 不同承载底盘外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1991/719255/fiat_tempra_s__w__2_0_i_e__sx_automatic.html?utm_source=chatgpt.com "1991 Fiat Tempra SW 2.0 ie SX automatic (aut. 4)"
[2]: https://www.automobile-catalog.com/car/1983/715820/fiat_uno_70_s.html?utm_source=chatgpt.com "1983 Fiat Uno 70 S Specs Review (50 kW / 68 PS / 67 hp) ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Ktype `147265`，按已确认的 Standard 与 Long 两种物理车长拆分为两条派生映射。Fiat 官方发布资料确认该代 E-Ulysse 提供两种车长；对应规格页明确给出车身宽度 1920 mm、不含后视镜，以及各自完整三维。([Stellantis Media][1])
* Talento 296 Platform Cab 暂未建组：Fiat 官方表仅给出长度 5248 mm 和高度 1953 mm，宽度栏为空，尚不满足 `WidthMM=WITHOUT_MIRRORS` 的硬性条件。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：92
* PENDING 输入 Ktype：8
* READY 映射行：111
* 已确认并引用尺寸组：24
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
147265_standard	147265	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	HIGH	标准车长车身。	READY
147265_long	147265	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	HIGH	长车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	4956	1920	1890	Fiat E-Ulysse official launch release; EV Database Fiat E-Ulysse L2 75 kWh	https://www.media.stellantis.com/em-en/fiat/press/new-e-ulysse-continuing-the-fiat-journey-towards-electrification;https://ev-database.org/car/1722/Fiat-E-Ulysse-L2-75-kWh
EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	5306	1920	1890	Fiat E-Ulysse official launch release; EV Database Fiat E-Ulysse L3 50 kWh	https://www.media.stellantis.com/em-en/fiat/press/new-e-ulysse-continuing-the-fiat-journey-towards-electrification;https://ev-database.org/car/1723/Fiat-E-Ulysse-L3-50-kWh
```

## 下一步优先处理

1. 闭合 Ulysse `157532`、`158247`、`802879`、`802302` 的改款边界、Standard/Long 分支及不含后视镜宽度。
2. 补齐 Talento `120665`、`120666` Platform Cab 官方宽度口径。
3. 确认 Ford A-Series `156213`、`156214` 各自底盘与轴距分支，禁止用临时尺寸猜测建组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/fiat/press/new-e-ulysse-continuing-the-fiat-journey-towards-electrification?utm_source=chatgpt.com "New E-Ulysse, continuing the FIAT journey towards ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 **6 个输入 Ktype**，新增 **12 条 READY 映射**。
* Ulysse `157532` 覆盖改款前后，按 Standard/Long 与 pre-facelift/facelift 拆分；其余 3 个现代 Ulysse Ktype 按 Standard/Long 建立映射。
* 改款前 Ulysse 直接复用已有两个尺寸组；改款后官方规格为 Standard `4983×1920×1895`、Long `5333×1920×1935` mm，宽度明确不含后视镜。([菲亚特瑞士][1])
* Talento 296 Floor Cab 两个 Ktype 共用同一外廓，官方资料闭合为 `5248×1956×1953` mm。([菲亚特专业][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* PENDING 输入 Ktype：2
* READY 映射行：123
* 已确认并引用尺寸组：27
* 剩余：Ford A-Series `156213`、`156214`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
157532_standard_prefl	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	MEDIUM	标准车长改款前物理外廓。	READY
157532_standard_facelift	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	MEDIUM	标准车长改款后物理外廓。	READY
157532_long_prefl	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	MEDIUM	长车身改款前物理外廓。	READY
157532_long_facelift	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	MEDIUM	长车身改款后物理外廓。	READY
802879_standard	802879	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
802879_long	802879	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
802302_standard	802302	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
802302_long	802302	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
158247_standard	158247	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
158247_long	158247	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
120665	120665	Pickup	Talento II	296	2	EU-FIAT-TALENTO-296-FLOORCAB-01	HIGH	296长轴低顶平台底盘。	READY
120666	120666	Pickup	Talento II	296	2	EU-FIAT-TALENTO-296-FLOORCAB-01	HIGH	296长轴低顶平台底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	4983	1920	1895	Fiat Professional Switzerland Ulysse MY26 official price list	https://www.fiat.ch/content/dam/fiat2023/ch/professional/pricelists/ulysse/2026/07/PL-Ulysse_MY26_FR.pdf
EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	5333	1920	1935	Fiat Professional Switzerland Ulysse MY26 official price list	https://www.fiat.ch/content/dam/fiat2023/ch/professional/pricelists/ulysse/2026/07/PL-Ulysse_MY26_FR.pdf
EU-FIAT-TALENTO-296-FLOORCAB-01	5248	1956	1953	Fiat Professional Talento Floor Cab official specifications; Stellantis Talento official model document	https://www.fiatprofessional.com/talento/floor-cab;https://www.media.stellantis.com/em-en/download-model-document/66
```

## 下一步优先处理

1. 仅处理 Ford A-Series `156213`（A0406）与 `156214`（A0506）。
2. 确认两种底盘的轴距分支、完整车长、车宽和驾驶室高度；不得把车厢改装后的尺寸当作标准底盘外廓。
3. 两个 Ktype 闭合后立即执行一次机械检查，并在下一轮输出两张最终完整 TSV、两个指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.fiat.ch/content/dam/fiat2023/ch/professional/pricelists/ulysse/2026/07/PL-Ulysse_MY26_FR.pdf "CH-Fiat_Professional-Ulysse-506_ULYSSE-MY26"
[2]: https://www.fiatprofessional.com/talento/floor-cab?utm_source=chatgpt.com "Fiat Talento Floor Cab ׀ Cargo Van ׀ Fiat Professional"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已确认 Ford A-Series `A0406` 与 `A0506` 不能各自直接落成单一尺寸组：该车系原厂提供 **4 种轴距**，并有超过 350 种底盘、载重和车身组合。([维基百科][1])
* 同一 `A0406` 的现存登记样本出现 `6200×2200 mm` 和 `6300×2200 mm` 等不同完成车外廓；这些尺寸受后装货厢影响，且缺少高度，不能作为标准底盘完整三维。([车主查询][2])
* `A0506` 登记样本同样存在完成车外廓差异，暂不能据此创建稳定尺寸组。([车主查询][3])
* 已将最后两个 Ktype 明确落为 PENDING，未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* READY 映射行：123
* PENDING 映射行：2
* 已引用尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156213	156213	Pickup	A-Series	A0406	2		LOW	已确认覆盖多轴距及多种后装车身，尚不能建立唯一物理外廓分支。	PENDING: 缺少可追溯的原厂轴距分支及标准底盘完整长宽高
156214	156214	Pickup	A-Series	A0506	2		LOW	已确认覆盖多轴距及多种后装车身，尚不能建立唯一物理外廓分支。	PENDING: 缺少可追溯的原厂轴距分支及标准底盘完整长宽高
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 获取 Ford 原厂 `Ford's Go-Between` 或 `Anatomy of the A-series light truck range` 技术规格表。
2. 确认 `A0406`、`A0506` 分别对应的原厂轴距分支，以及每个分支的标准底盘长度、不含后视镜宽度和驾驶室高度。
3. 闭合两个 Ktype 后仅执行一次机械检查，随即输出两张最终完整 TSV 和两个指定下载链接。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Ford_A_series "Ford A series - Wikipedia"
[2]: https://regnr.info/BL35086 "BL35086 - FORD A0406 1975 Rød - Hvem eier bilen?"
[3]: https://regnr.info/BC23759 "BC23759 - FORD A0506 1974 - Hvem eier bilen?"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已进一步确认 `A0406` 属于 3.5 吨底盘驾驶室，`A0506` 存在 4.6 吨和 5 吨规格；整个 A-Series 还覆盖 3050、3300、3680、3960 mm 四种轴距，型号本身不足以唯一确定完整物理外廓。([商业汽车档案馆][1])
* 当前取得的原厂资料仅有宣传册封面，没有包含长宽高的规格页；现有完成车辆数据受后装货厢影响，仍不能建立合规尺寸组。
* 本轮未修改既有 PENDING 映射，也未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* READY 映射行：123
* PENDING 映射行：2
* 已确认并引用尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 定向获取 Ford 原厂 `Ford's Go-Between` 规格内页或 A-Series 车身制造商尺寸图。
2. 只提取 `A0406`、`A0506` 可用轴距分支的标准底盘总长、不含后视镜宽度和驾驶室高度。
3. 两个 Ktype 闭合后立即进行一次机械检查，并输出最终两张完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://archive.commercialmotor.com/article/14th-september-1979/60/lightweights-fit-all-forms-of-work?utm_source=chatgpt.com "Lightweights fit all forms of work | 14th September 1979"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已进一步确认型号边界：`A0406` 为 3.5 吨、2.4 L 柴油的较轻底盘；`A0506` 为 4.6/5.0 吨、2.4 L 柴油的加强型底盘。A-Series 整体提供 3050–3960 mm 的多种轴距，输入 Ktype 没有限定具体轴距或完成车身，因此仍不能创建唯一尺寸组。([FOMCC][1])
* 已将两个 PENDING 行的 Notes 和阻塞原因收紧到实际缺失项。
* 现有登记记录只有受后装车身影响的完成车长度、宽度，且缺少高度与不含后视镜宽度口径，未据此建组。([车主查询][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* READY 映射行：123
* PENDING 映射行：2
* 已确认并引用尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156213	156213	Pickup	A-Series	A0406	2		LOW	A0406轻型底盘；Ktype未限定轴距或完成车身分支。	PENDING: 缺少各适用轴距分支的标准底盘完整长宽高及不含后视镜宽度
156214	156214	Pickup	A-Series	A0506	2		LOW	A0506加强型底盘；Ktype未限定轴距、载重等级或完成车身分支。	PENDING: 缺少各适用轴距分支的标准底盘完整长宽高及不含后视镜宽度
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 定向获取原厂 A-Series 底盘尺寸矩阵内页，而非宣传册封面或完成车登记数据。
2. 仅在资料同时明确型号适用轴距、标准底盘总长、不含后视镜宽度和驾驶室高度后创建派生分支。
3. 两个 Ktype 闭合后立即进行机械检查并输出最终完整产物。

推进信号：CONTINUE

[1]: https://www.fomcc.de/a_serie.htm "Ford A-Serie"
[2]: https://regnr.info/YZ21456 "YZ21456 - FORD A0406 1974 - Hvem eier bilen?"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 原厂 Ford A-Serie 车型矩阵已确认：A04 底盘包含 3300、3960 mm 两种轴距；A05 底盘包含 3300、3680、3960 mm 三种轴距。现将两个无后缀 PENDING 行改为五个明确物理分支。
* 该资料页未提供各轴距分支的标准底盘总长、不含后视镜宽度及驾驶室高度，因此本轮不创建尺寸组，也不猜测填值。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* READY 映射行：123
* PENDING 输入 Ktype：2
* PENDING 派生映射行：5
* 已确认并引用尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156213_swb	156213	Pickup	A-Series	A0406	2		LOW	A04短轴分支，轴距3300 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
156213_lwb	156213	Pickup	A-Series	A0406	2		LOW	A04长轴分支，轴距3960 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
156214_swb	156214	Pickup	A-Series	A0506	2		LOW	A05短轴分支，轴距3300 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
156214_mwb	156214	Pickup	A-Series	A0506	2		LOW	A05中轴分支，轴距3680 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
156214_lwb	156214	Pickup	A-Series	A0506	2		LOW	A05长轴分支，轴距3960 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅补齐上述五个已确认轴距分支的标准底盘总长、不含后视镜宽度和驾驶室高度。
2. 优先查找 Ford A-Serie 原厂技术数据页、车身制造商尺寸图或 homologation 资料，不再处理已闭合车型。
3. 五个分支尺寸闭合后，立即执行一次机械检查并输出最终两张完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 根据 Ford 1980 年 A-Series 原厂价格表，修正 `A0406` 的轴距边界：2.4 L 柴油版实际提供 **3050 mm** 和 **3680 mm**，上一轮记录的 3300/3960 mm 属于其他 A04 动力型号，不适用于当前 Ktype。
* `A0506` 的 3300、3680、3960 mm 三个轴距分支维持不变。([eBay UK][1])
* 尚未取得五个轴距分支对应的标准底盘完整三维，本轮未创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：98
* READY 映射行：123
* PENDING 输入 Ktype：2
* PENDING 派生映射行：5
* 已确认并引用尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156213_swb	156213	Pickup	A-Series	A0406	2		LOW	A0406短轴分支，轴距3050 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
156213_lwb	156213	Pickup	A-Series	A0406	2		LOW	A0406长轴分支，轴距3680 mm。	PENDING: 缺少该轴距标准底盘完整长宽高及不含后视镜宽度
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅查找 Ford A-Series 原厂车身制造商尺寸图或底盘布置图。
2. 补齐 A0406 的 3050/3680 mm 和 A0506 的 3300/3680/3960 mm 分支所对应的底盘总长、不含后视镜宽度及驾驶室高度。
3. 五个分支闭合后立即机械检查并输出最终完整产物。

推进信号：CONTINUE

[1]: https://www.ebay.co.uk/itm/365774191906 "1980 FORD A SERIES TRUCKS PRICE LIST - A0406 A0506 A0509 A0510 A0609 A0610 Mint! | eBay UK"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5201-5300_ktype_dimension_mapping_final.tsv
- left18448_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* Ford A-Series 最后 5 个物理分支已闭合：A0406 的 3050/3680 mm 轴距，以及 A0506 的 3300/3680/3960 mm 轴距。原厂规格页同时给出了对应总长、2200 mm 车身宽度及空载高度。
* 已完成轻量机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、引用全部闭合、尺寸与来源非空。
* 已生成两个指定文件名的最终 TSV。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：128
* PENDING：0
* DIMENSION_GROUP：32
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120656_swb	120656	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	SWB低顶客车物理外廓。	READY
120656_lwb	120656	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	LWB低顶客车物理外廓。	READY
120661_swb_lowroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120661_swb_highroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120661_lwb_lowroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120661_lwb_highroof	120661	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120662_swb_lowroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120662_swb_highroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120662_lwb_lowroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120662_lwb_highroof	120662	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120663_swb_lowroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120663_swb_highroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120663_lwb_lowroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120663_lwb_highroof	120663	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120664_swb_lowroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶厢式车物理外廓。	READY
120664_swb_highroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶厢式车物理外廓。	READY
120664_lwb_lowroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶厢式车物理外廓。	READY
120664_lwb_highroof	120664	Van	Talento II	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶厢式车物理外廓。	READY
120665	120665	Pickup	Talento II	296	2	EU-FIAT-TALENTO-296-FLOORCAB-01	HIGH	296长轴低顶平台底盘。	READY
120666	120666	Pickup	Talento II	296	2	EU-FIAT-TALENTO-296-FLOORCAB-01	HIGH	296长轴低顶平台底盘。	READY
145404_swb	145404	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	SWB低顶客车物理外廓。	READY
145404_lwb	145404	MPV	Talento II	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	LWB低顶客车物理外廓。	READY
15922	15922	Van	Talento I	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	HIGH	290 标准车身厢式车。	READY
15923	15923	Pickup	Talento I	290	2	EU-FIAT-TALENTO-290-CHASSISCAB-01	HIGH	290 底盘驾驶室物理车身。	READY
15939	15939	MPV	Talento I	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	HIGH	290 客车复用标准车身外廓。	READY
143380	143380	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
143381	143381	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
143382	143382	Van	Tempra I	159	5	EU-FIAT-TEMPRA-159-VAN-01	HIGH	Tempra旅行车基础商用车外廓。	READY
142956	142956	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
142958	142958	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
143261	143261	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
117867	117867	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119838	119838	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119841	119841	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119843	119843	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
119849	119849	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
117868	117868	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
122038	122038	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
122039	122039	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
117869	117869	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119840	119840	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119848	119848	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
14646	14646	Hatchback	Tipo I	160		EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	三门与五门版本共用同一外廓。	READY
120721	120721	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
120723	120723	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
121442	121442	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
147199	147199	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
147200	147200	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
147708	147708	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
117870	117870	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
119839	119839	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
119847	119847	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
123395	123395	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	四门三厢物理车身。	READY
123396	123396	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	五门掀背物理车身。	READY
123398	123398	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	五门旅行车物理车身。	READY
142978	142978	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	改款标准五门掀背车身。	READY
142981	142981	Wagon	Tipo II	357	5	EU-FIAT-TIPO-357-WAGON-01	HIGH	改款标准五门旅行车车身。	READY
146860	146860	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	改款标准四门三厢车身。	READY
18925	18925	Hatchback	Tipo I	160	3	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	改款三门掀背车身。	READY
14643	14643	Hatchback	Tipo I	160	5	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	五门掀背车身。	READY
13280	13280	Hatchback	Tipo I	160	5	EU-FIAT-TIPO-160-HATCHBACK-01	HIGH	五门16V运动版车身。	READY
156216	156216	Hatchback	Topolino (2023)		2	EU-FIAT-TOPOLINO-2023-HATCHBACK-01	HIGH	封闭式双门微型车身。	READY
8847	8847	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16892	16892	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
16893	16893	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
116063	116063	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
11372	11372	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
15815	15815	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
14159	14159	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16894	16894	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
17494	17494	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
11753	11753	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
157532_standard_prefl	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	MEDIUM	标准车长改款前物理外廓。	READY
157532_standard_facelift	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	MEDIUM	标准车长改款后物理外廓。	READY
157532_long_prefl	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	MEDIUM	长车身改款前物理外廓。	READY
157532_long_facelift	157532	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	MEDIUM	长车身改款后物理外廓。	READY
5737	5737	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-220-MPV-01	HIGH	Ulysse第一代五门MPV。	READY
16895	16895	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-179-MPV-01	HIGH	Ulysse第二代五门MPV。	READY
802879_standard	802879	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
802879_long	802879	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
802302_standard	802302	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
802302_long	802302	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
147265_standard	147265	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	HIGH	标准车长车身。	READY
147265_long	147265	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	HIGH	长车身。	READY
158247_standard	158247	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	HIGH	标准车长改款后物理外廓。	READY
158247_long	158247	MPV	Ulysse III		5	EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	HIGH	长车身改款后物理外廓。	READY
55918_prefl	55918	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
55918_facelift	55918	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
58803_prefl	58803	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
58803_facelift	58803	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14547	14547	Hatchback	Uno I	146	3	EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	HIGH	改款后三门Turbo车身。	READY
8862	8862	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14545_prefl	14545	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
14545_facelift	14545	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
14546	14546	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
15896_prefl	15896	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	MEDIUM	1989年改款前物理外廓。	READY
15896_facelift	15896	Hatchback	Uno I	146		EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	MEDIUM	1989年改款后物理外廓。	READY
161560	161560	Hatchback	Firefly I		5	EU-FIREFLY-FIREFLY-I-HATCHBACK-01	HIGH	五门纯电掀背车物理外廓。	READY
55253	55253	Sedan	Karma I		4	EU-FISKER-KARMA-I-SEDAN-01	HIGH	四门量产轿车物理外廓。	READY
157313	157313	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151939	151939	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
155605	155605	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151940	151940	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
151941	151941	SUV	Ocean I	FM29	5	EU-FISKER-OCEAN-I-SUV-01	HIGH	量产SUV标准物理外廓。	READY
156213_swb	156213	Pickup	A-Series	A0406	2	EU-FORD-A-SERIES-A0406-PICKUP-SWB-01	HIGH	A0406短轴分支，轴距3050 mm。	READY
156213_lwb	156213	Pickup	A-Series	A0406	2	EU-FORD-A-SERIES-A0406-PICKUP-LWB-01	HIGH	A0406长轴分支，轴距3680 mm。	READY
156214_swb	156214	Pickup	A-Series	A0506	2	EU-FORD-A-SERIES-A0506-PICKUP-SWB-01	HIGH	A0506短轴分支，轴距3300 mm。	READY
156214_mwb	156214	Pickup	A-Series	A0506	2	EU-FORD-A-SERIES-A0506-PICKUP-MWB-01	HIGH	A0506中轴分支，轴距3680 mm。	READY
156214_lwb	156214	Pickup	A-Series	A0506	2	EU-FORD-A-SERIES-A0506-PICKUP-LWB-01	HIGH	A0506长轴分支，轴距3960 mm。	READY
55466	55466	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108801	108801	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55105	55105	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
55106	55106	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
59492	59492	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108797	108797	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
108800	108800	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
118618	118618	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
142732	142732	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
105988	105988	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
142735	142735	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55537	55537	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108803	108803	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
113165	113165	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
113677	113677	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55108	55108	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108804	108804	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
55107	55107	MPV	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	HIGH	五门 MPV 物理车身。	READY
108802	108802	Van	B-Max I	B232	5	EU-FORD-B-MAX-B232-MPV-01	MEDIUM	厢式衍生版复用 B-Max 外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5201-5300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TALENTO-290-CHASSISCAB-01	4157	1965	2100	Autogidas Fiat Talento 269.390.3 specifications	https://autogidas.lt/en/auto-katalogas/fiat/talento/talento-269.390.3-1989-1994-k30341
EU-FIAT-TALENTO-290-STANDARD-BODY-01	4157	1965	2100	Autogidas Fiat Talento 269.390.3 specifications	https://autogidas.lt/en/auto-katalogas/fiat/talento/talento-269.390.3-1989-1994-k30341
EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Range official price list December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TIPO-357-WAGON-01	4571	1792	1514	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Fiat Tipo 5D/Sedan/SW official brochure	https://www.media.stellantis.com/uploads/pl/PL/2017/FIAT/Files/Katalog_TIPO_5D_i_SW.pdf
EU-FIAT-TOPOLINO-2023-HATCHBACK-01	2535	1400	1530	Fiat Topolino official technical sheet	https://www.media.stellantis.com/uploads/em/attachment/9567/fiattopolino_technicalsheet-64a4110fb3089.pdf
EU-FORD-B-MAX-B232-MPV-01	4077	1751	1604	Ford B-MAX official brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-B-Max-2012-UK.pdf;https://www.automobile-catalog.com/car/2012/1775780/ford_b-max_1_0_ecoboost_100_titanium.html
EU-FIAT-ULYSSE-220-MPV-01	4454	1834	1714	Auto-Data Fiat Ulysse I 22/220 generation specifications	https://www.auto-data.net/en/fiat-ulysse-i-22-220-generation-1615
EU-FIAT-ULYSSE-179-MPV-01	4719	1863	1752	Fiat New Ulysse official press kit	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-ulysse
EU-FIREFLY-FIREFLY-I-HATCHBACK-01	4003	1781	1557	Firefly international owner manual	https://cdn-up-public.firefly.world/www-firefly/user-instructions/FIREFLY/index.html
EU-FISKER-KARMA-I-SEDAN-01	4998	1984	1330	Automobile-Catalog 2012 Fisker Karma specifications	https://www.automobile-catalog.com/car/2012/2970215/fisker_karma.html
EU-FISKER-OCEAN-I-SUV-01	4774	1982	1631	Fisker Ocean Specifications press sheet	https://www.autoevolution.com/pdf/news_attachements/first-fisker-ocean-delivery-shuts-up-everyone-who-doubted-the-company-would-make-it-214648.pdf
EU-FIAT-TEMPRA-159-VAN-01	4472	1695	1500	Automobile-Catalog 1991 Fiat Tempra S.W. specifications	https://www.automobile-catalog.com/car/1991/719255/fiat_tempra_s__w__2_0_i_e__sx_automatic.html
EU-FIAT-TIPO-160-HATCHBACK-01	3958	1700	1445	Automobile-Catalog 1989 Fiat Tipo specifications; Automobile-Catalog 1993 Fiat Tipo 3-door specifications	https://www.automobile-catalog.com/car/1989/60620/fiat_tipo_1_1.html;https://www.automobile-catalog.com/car/1993/718490/fiat_tipo_1_4_i_e__s_3p.html
EU-FIAT-UNO-146-HATCHBACK-PREFACELIFT-01	3644	1555	1432	Automobile-Catalog 1983 Fiat Uno 70 S specifications	https://www.automobile-catalog.com/car/1983/715820/fiat_uno_70_s.html
EU-FIAT-UNO-146-HATCHBACK-FACELIFT-01	3691	1560	1420	AutoEvolution Fiat Uno 1989-1994 three-door specifications; AutoEvolution Fiat Uno 1989-1994 five-door specifications	https://www.autoevolution.com/cars/fiat-uno-3-doors-1989.html;https://www.autoevolution.com/cars/fiat-uno-5-doors-1989.html
EU-FIAT-ULYSSE-III-MPV-STANDARD-PREFACELIFT-01	4956	1920	1890	Fiat E-Ulysse official launch release; EV Database Fiat E-Ulysse L2 75 kWh	https://www.media.stellantis.com/em-en/fiat/press/new-e-ulysse-continuing-the-fiat-journey-towards-electrification;https://ev-database.org/car/1722/Fiat-E-Ulysse-L2-75-kWh
EU-FIAT-ULYSSE-III-MPV-LONG-PREFACELIFT-01	5306	1920	1890	Fiat E-Ulysse official launch release; EV Database Fiat E-Ulysse L3 50 kWh	https://www.media.stellantis.com/em-en/fiat/press/new-e-ulysse-continuing-the-fiat-journey-towards-electrification;https://ev-database.org/car/1723/Fiat-E-Ulysse-L3-50-kWh
EU-FIAT-ULYSSE-III-MPV-STANDARD-FACELIFT-01	4983	1920	1895	Fiat Professional Switzerland Ulysse MY26 official price list	https://www.fiat.ch/content/dam/fiat2023/ch/professional/pricelists/ulysse/2026/07/PL-Ulysse_MY26_FR.pdf
EU-FIAT-ULYSSE-III-MPV-LONG-FACELIFT-01	5333	1920	1935	Fiat Professional Switzerland Ulysse MY26 official price list	https://www.fiat.ch/content/dam/fiat2023/ch/professional/pricelists/ulysse/2026/07/PL-Ulysse_MY26_FR.pdf
EU-FIAT-TALENTO-296-FLOORCAB-01	5248	1956	1953	Fiat Professional Talento Floor Cab official specifications; Stellantis Talento official model document	https://www.fiatprofessional.com/talento/floor-cab;https://www.media.stellantis.com/em-en/download-model-document/66
EU-FORD-A-SERIES-A0406-PICKUP-SWB-01	5230	2200	2063	Ford A-Series official 1978 brochure, General Specifications and Dimensions	https://i.ebayimg.com/images/g/WsgAAeSw~RVowRmj/s-l1600.webp
EU-FORD-A-SERIES-A0406-PICKUP-LWB-01	6320	2200	2063	Ford A-Series official 1978 brochure, General Specifications and Dimensions	https://i.ebayimg.com/images/g/WsgAAeSw~RVowRmj/s-l1600.webp
EU-FORD-A-SERIES-A0506-PICKUP-SWB-01	5450	2200	2106	Ford A-Series official 1978 brochure, General Specifications and Dimensions	https://i.ebayimg.com/images/g/WsgAAeSw~RVowRmj/s-l1600.webp
EU-FORD-A-SERIES-A0506-PICKUP-MWB-01	6320	2200	2106	Ford A-Series official 1978 brochure, General Specifications and Dimensions	https://i.ebayimg.com/images/g/WsgAAeSw~RVowRmj/s-l1600.webp
EU-FORD-A-SERIES-A0506-PICKUP-LWB-01	6820	2200	2106	Ford A-Series official 1978 brochure, General Specifications and Dimensions	https://i.ebayimg.com/images/g/WsgAAeSw~RVowRmj/s-l1600.webp
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5201-5300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1111 行）
- 累计尺寸组：dimension_groups_final.tsv（289 行）

