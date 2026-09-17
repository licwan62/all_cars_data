# 任务：left18448 第 2201-2300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0023__e4a94cee


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2201-2300 行

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
left18448 第 2201-2300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2201-2300_ktype_dimension_mapping_final.tsv
- left18448_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-4-3-0-CSL-COUPE-01	4794	1921	1386
EU-BMW-4-F32-COUPE-RWD-01	4638	1825	1362
EU-BMW-4-F32-COUPE-XDRIVE-01	4638	1825	1377
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390
EU-BMW-4-G23-CONVERTIBLE-01	4768	1852	1384

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	4	420 I	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	127901
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	127908
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2016	May 2021	127909
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Jul 2021	-	144692
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Nov 2013	Feb 2016	54208
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Jul 2014	Feb 2016	105922
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Nov 2013	Feb 2016	116663
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Jul 2014	Feb 2016	116676
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	May 2021	118955
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	Jun 2020	118959
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	May 2021	127911
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	Jun 2020	127912
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	Jul 2021	-	144723
BMW	4	425 D	Coupe	Heckantrieb	Diesel	Mar 2014	Feb 2016	100820
BMW	4	425 D	Cabriolet	Heckantrieb	Diesel	Jul 2014	Feb 2016	105918
BMW	4	425 D	Coupe	Heckantrieb	Diesel	Mar 2014	Feb 2016	116669
BMW	4	425 D	Cabriolet	Heckantrieb	Diesel	Jul 2014	Feb 2016	116671
BMW	4	425 D	Coupe	Heckantrieb	Diesel	Mar 2016	Oct 2017	118089
BMW	4	425 D	Cabriolet	Heckantrieb	Diesel	Mar 2016	Feb 2018	118183
BMW	4	425 D	Coupe	Heckantrieb	Diesel	Mar 2016	Feb 2018	118189
BMW	4	425 D	Coupe	Heckantrieb	Diesel	Mar 2016	Feb 2018	120539
BMW	4	428 I	Cabriolet	Heckantrieb	Benzin	Nov 2013	Feb 2017	58299
BMW	4	428 I	Coupe	Heckantrieb	Benzin	Jul 2013	Feb 2017	59805
BMW	4	428 I	Coupe	Heckantrieb	Benzin	Mar 2014	Jun 2016	100852
BMW	4	428 I Xdrive	Coupe	Allrad	Benzin	Jul 2013	Feb 2016	59806
BMW	4	428 I Xdrive	Cabriolet	Allrad	Benzin	Mar 2014	Feb 2016	100844
BMW	4	428 I Xdrive	Coupe	Allrad	Benzin	Mar 2014	Feb 2016	100853
BMW	4	430 D	Coupe	Heckantrieb	Diesel	Nov 2013	Jun 2020	54207
BMW	4	430 D	Cabriolet	Heckantrieb	Diesel	Jul 2014	Jul 2020	105920
BMW	4	430 D	Coupe	Heckantrieb	Diesel	Jul 2014	Dec 2020	105924
BMW	4	430 D	Coupe	Heckantrieb	Diesel	Nov 2013	Jun 2020	107914
BMW	4	430 D	Cabriolet	Heckantrieb	Diesel	Jul 2014	Jul 2020	107916
BMW	4	430 D	Coupe	Heckantrieb	Diesel	Jul 2014	Dec 2020	107917
BMW	4	430 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	May 2022	-	147747
BMW	4	430 D Xdrive	Coupe	Allrad	Diesel	Mar 2014	Jun 2020	100817
BMW	4	430 D Xdrive	Coupe	Allrad	Diesel	Jul 2014	Dec 2020	105925
BMW	4	430 D Xdrive	Coupe	Allrad	Diesel	Mar 2014	Jun 2020	107915
BMW	4	430 D Xdrive	Coupe	Allrad	Diesel	Jul 2014	Dec 2020	107918
BMW	4	430 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	118079
BMW	4	430 I	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	118179
BMW	4	430 I	Coupe	Heckantrieb	Benzin	Mar 2016	May 2021	118184
BMW	4	430 I	Coupe	Heckantrieb	Benzin	Jul 2021	-	144693
BMW	4	430 I	Cabriolet	Heckantrieb	Benzin	Jul 2021	-	145615
BMW	4	430 I	Coupe	Heckantrieb	Benzin	Jul 2021	-	145619
BMW	4	430 I	Coupe	Heckantrieb	Benzin/Elektro	Jul 2024	-	801024
BMW	4	430 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	Jul 2024	-	801023
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	Jun 2020	118080
BMW	4	430 I Xdrive	Cabriolet	Allrad	Benzin	Mar 2016	Jul 2020	118180
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	May 2021	118185
BMW	4	430 I Xdrive	Cabriolet	Allrad	Benzin	Jul 2021	-	145616
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	Jul 2021	-	145620
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	Mar 2022	-	147092
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	Jul 2021	-	152953
BMW	4	435 D Xdrive	Coupe	Allrad	Diesel	Nov 2013	Jun 2020	52003
BMW	4	435 D Xdrive	Cabriolet	Allrad	Diesel	Jul 2014	Jul 2020	105921
BMW	4	435 D Xdrive	Coupe	Allrad	Diesel	Jul 2014	Dec 2020	105926
BMW	4	435 I	Cabriolet	Heckantrieb	Benzin	Nov 2013	Feb 2016	58292
BMW	4	435 I	Coupe	Heckantrieb	Benzin	Jul 2013	Feb 2016	59807
BMW	4	435 I	Coupe	Heckantrieb	Benzin	Mar 2014	Feb 2016	100843
BMW	4	435 I	Coupe	Heckantrieb	Benzin	Jul 2013	Feb 2016	107890
BMW	4	435 I	Cabriolet	Heckantrieb	Benzin	Nov 2013	Feb 2016	107927
BMW	4	435 I	Coupe	Heckantrieb	Benzin	Mar 2014	Feb 2016	107928
BMW	4	435 I Xdrive	Coupe	Allrad	Benzin	Jul 2013	Feb 2016	59808
BMW	4	435 I Xdrive	Cabriolet	Allrad	Benzin	Jul 2014	Feb 2016	105915
BMW	4	435 I Xdrive	Coupe	Allrad	Benzin	Jul 2014	Feb 2016	105923
BMW	4	435 I Xdrive	Coupe	Allrad	Benzin	Jul 2013	Feb 2016	107893
BMW	4	435 I Xdrive	Cabriolet	Allrad	Benzin	Jul 2014	Feb 2016	107926
BMW	4	435 I Xdrive	Coupe	Allrad	Benzin	Jul 2014	Feb 2016	107929
BMW	4	440 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	118082
BMW	4	440 I	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	118181
BMW	4	440 I	Coupe	Heckantrieb	Benzin	Mar 2016	May 2021	118186
BMW	4	440 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	119033
BMW	4	440 I	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	119036
BMW	4	440 I	Coupe	Heckantrieb	Benzin	Mar 2016	May 2021	119039
BMW	4	440 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	Jun 2020	118084
BMW	4	440 I Xdrive	Cabriolet	Allrad	Benzin	Mar 2016	Jul 2020	118182
BMW	4	440 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	May 2021	118188
BMW	4	440 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	Jun 2020	119031
BMW	4	440 I Xdrive	Cabriolet	Allrad	Benzin	Mar 2016	Jul 2020	119037
BMW	4	440 I Xdrive	Coupe	Allrad	Benzin	Mar 2016	May 2021	119038
BMW	4	I4 Edrive35	Coupe	Heckantrieb	Elektro	Nov 2022	-	150711
BMW	4	I4 Edrive40	Coupe	Heckantrieb	Elektro	Nov 2021	-	144688
BMW	4	I4 M50 Xdrive	Coupe	Allrad	Elektro	Nov 2021	-	144689
BMW	4	I4 M60 Xdrive	Coupe	Allrad	Elektro	Jul 2025	-	802014
BMW	4	I4 Xdrive40	Coupe	Allrad	Elektro	Jul 2024	-	158778
BMW	4	M 440 I Mild-hybrid	Coupe	Heckantrieb	Benzin/Elektro	Jul 2021	-	144724
BMW	4	M 440 I Mild-hybrid	Cabriolet	Heckantrieb	Benzin/Elektro	Jul 2021	-	145795
BMW	4	M 440 I Mild-hybrid Xdrive	Cabriolet	Allrad	Benzin/Elektro	Nov 2020	-	142489
BMW	4	M 440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	Nov 2020	-	142849
BMW	4	M 440 I Mild-hybrid Xdrive	Cabriolet	Allrad	Benzin/Elektro	Sep 2025	-	802389
BMW	4	M 440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	Sep 2025	-	802392
BMW	4	M4	Coupe	Heckantrieb	Benzin	Mar 2014	Jun 2020	100821
BMW	4	M4	Cabriolet	Heckantrieb	Benzin	Jul 2014	Jul 2020	105899
BMW	4	M4 Competition	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	118090
BMW	4	M4 Competition	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	118193
BMW	4	M4 Competition M Xdrive	Coupe	Allrad	Benzin	May 2021	Feb 2024	143770
BMW	4	M4 Competition M Xdrive	Cabriolet	Allrad	Benzin	Jul 2021	Feb 2024	144249
BMW	4	M4 Competition M Xdrive	Coupe	Allrad	Benzin	Mar 2024	-	157687
BMW	4	M4 Competition M Xdrive	Cabriolet	Allrad	Benzin	Mar 2024	-	157688
BMW	4	M4 CS	Coupe	Heckantrieb	Benzin	Jul 2017	Jun 2019	127860


--- Round 1 / 首次发送 ---
## 更新点

* 完成 BMW 4 Series F32/F33、G22/G23、i4 G26，以及 M4 F82/F83/G82/G83 的物理外廓聚类。
* 已复用跨批次中三维一致的既有尺寸组，并为 F33/G23 xDrive、M440i、i4、M4 CS 和 M4 改款分支建立独立尺寸组。
* F32/F33 和 G22/G23 的 xDrive 高度分支、i4 五门 Gran Coupé 外廓，以及 M4 改款前后尺寸边界均已闭合。([BMW Group PressClub][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：100
* PENDING 映射：0
* 已确认并引用尺寸组：20
* `id` 唯一、尺寸组唯一、映射引用闭合、三维及来源完整。
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127901	127901	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
127908	127908	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
127909	127909	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
144692	144692	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
54208	54208	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105922	105922	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
116663	116663	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
116676	116676	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118955	118955	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118959	118959	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
127911	127911	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
127912	127912	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
144723	144723	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
100820	100820	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
105918	105918	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116669	116669	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116671	116671	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
118089	118089	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118183	118183	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
118189	118189	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
120539	120539	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
58299	58299	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
59805	59805	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100852	100852	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
59806	59806	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
100844	100844	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
100853	100853	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
54207	54207	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
105920	105920	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
105924	105924	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
107914	107914	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
107916	107916	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
107917	107917	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
147747	147747	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
100817	100817	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105925	105925	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
107915	107915	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
107918	107918	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118079	118079	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118179	118179	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
118184	118184	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
144693	144693	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
145615	145615	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-CONVERTIBLE-01	HIGH		READY
145619	145619	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
801024	801024	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
801023	801023	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118080	118080	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118180	118180	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118185	118185	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
145616	145616	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
145620	145620	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
147092	147092	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
152953	152953	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
52003	52003	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105921	105921	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105926	105926	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
58292	58292	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
59807	59807	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100843	100843	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
107890	107890	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
107927	107927	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
107928	107928	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
59808	59808	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105915	105915	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
105923	105923	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
107893	107893	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
107926	107926	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
107929	107929	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118082	118082	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118181	118181	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
118186	118186	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
119033	119033	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
119036	119036	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
119039	119039	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118084	118084	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118182	118182	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
118188	118188	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
119031	119031	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
119037	119037	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
119038	119038	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH	xDrive exterior-height branch.	READY
150711	150711	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26 five-door Gran Coupé.	READY
144688	144688	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26 five-door Gran Coupé.	READY
144689	144689	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26 five-door Gran Coupé.	READY
802014	802014	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26 five-door Gran Coupé.	READY
158778	158778	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26 five-door Gran Coupé.	READY
144724	144724	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-RWD-01	HIGH	M440i rear-wheel-drive exterior.	READY
145795	145795	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-M440I-CONVERTIBLE-RWD-01	HIGH	M440i rear-wheel-drive exterior.	READY
142489	142489	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-M440I-CONVERTIBLE-XDRIVE-01	HIGH	M440i xDrive-specific exterior.	READY
142849	142849	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH	M440i xDrive-specific exterior.	READY
802389	802389	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-M440I-CONVERTIBLE-XDRIVE-01	HIGH	M440i xDrive-specific exterior.	READY
802392	802392	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	HIGH	M440i xDrive-specific exterior.	READY
100821	100821	Coupe	M4 F82	F82	2	EU-BMW-M4-F82-COUPE-01	HIGH	F82 M4 coupe exterior.	READY
105899	105899	Convertible	M4 F83	F83	2	EU-BMW-M4-F83-CONVERTIBLE-01	HIGH	F83 M4 convertible exterior.	READY
118090	118090	Coupe	M4 F82	F82	2	EU-BMW-M4-F82-COUPE-01	HIGH	F82 M4 coupe exterior.	READY
118193	118193	Convertible	M4 F83	F83	2	EU-BMW-M4-F83-CONVERTIBLE-01	HIGH	F83 M4 convertible exterior.	READY
143770	143770	Coupe	M4 G82	G82	2	EU-BMW-M4-G82-COUPE-XDRIVE-PREFL-01	HIGH	Pre-facelift G82 xDrive exterior.	READY
144249	144249	Convertible	M4 G83	G83	2	EU-BMW-M4-G83-CONVERTIBLE-XDRIVE-PREFL-01	HIGH	Pre-facelift G83 xDrive exterior.	READY
157687	157687	Coupe	M4 G82	G82	2	EU-BMW-M4-G82-COUPE-XDRIVE-FACELIFT-01	HIGH	Facelift G82 xDrive exterior.	READY
157688	157688	Convertible	M4 G83	G83	2	EU-BMW-M4-G83-CONVERTIBLE-XDRIVE-FACELIFT-01	HIGH	Facelift G83 xDrive exterior.	READY
127860	127860	Coupe	M4 F82	F82	2	EU-BMW-M4-F82-CS-COUPE-01	HIGH	F82 M4 CS exterior.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2201-2300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0193233CS/281133
EU-BMW-4-F32-COUPE-RWD-01	4638	1825	1362	BMW Group PressClub launch technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326318EN/472221
EU-BMW-4-F32-COUPE-XDRIVE-01	4638	1825	1377	BMW Group PressClub launch technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0333558EN/480212
EU-BMW-4-F33-CONVERTIBLE-XDRIVE-01	4638	1825	1399	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252344EN/348100
EU-BMW-4-G23-CONVERTIBLE-01	4768	1852	1384	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0333556EN/480209
EU-BMW-4-G23-CONVERTIBLE-XDRIVE-01	4768	1852	1391	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0439260EN/632532
EU-BMW-I4-G26-GRAN-COUPE-01	4783	1852	1448	BMW Group PressClub technical specifications; BMW UK official technical data	https://www.press.bmwgroup.com/global/article/attachment/T0441229EN/617130;https://www.bmw.co.uk/en/all-models/m-models/bmw-i4-m60/bmw-i4-m60-xdrive-gran-coupe-technical-data.html
EU-BMW-4-G22-M440I-COUPE-RWD-01	4770	1852	1386	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0333558EN/480212
EU-BMW-4-G23-M440I-CONVERTIBLE-RWD-01	4770	1852	1387	Automobile-Catalog European specifications	https://www.automobile-catalog.com/car/2023/3047120/bmw_m440i_cabrio.html
EU-BMW-4-G23-M440I-CONVERTIBLE-XDRIVE-01	4770	1852	1394	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0439260EN/632532
EU-BMW-4-G22-M440I-COUPE-XDRIVE-01	4770	1852	1393	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0439260EN/632531
EU-BMW-M4-F82-COUPE-01	4671	1870	1383	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286620CS/417940
EU-BMW-M4-F83-CONVERTIBLE-01	4671	1870	1386	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286619CS/417939
EU-BMW-M4-G82-COUPE-XDRIVE-PREFL-01	4794	1887	1394	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/deutschland/article/attachment/T0329893DE/477737
EU-BMW-M4-G83-CONVERTIBLE-XDRIVE-PREFL-01	4794	1887	1395	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0333554IT/480716
EU-BMW-M4-G82-COUPE-XDRIVE-FACELIFT-01	4801	1887	1398	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/belux/article/attachment/T0439390FR/611365
EU-BMW-M4-G83-CONVERTIBLE-XDRIVE-FACELIFT-01	4801	1887	1399	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/belux/article/attachment/T0439390FR/611364
EU-BMW-M4-F82-CS-COUPE-01	4672	1870	1392	BMW Group PressClub technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0269820EN/386745
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2201-2300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334 "https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2678 行）
- 累计尺寸组：dimension_groups_final.tsv（723 行）

