# 任务：left18448 第 201-300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0003__e695b763


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 201-300 行

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
left18448 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Alfa Romeo	Stelvio	2.2 D Q4	SUV	Allrad	Diesel	Dec 2016	-	127369
Alfa Romeo	Tonale	1.3 Hybrid Q4	SUV	Allrad	Benzin/Elektro	Mar 2022	-	147895
Alfa Romeo	Tonale	1.3 Hybrid Q4	SUV	Allrad	Benzin/Elektro	Mar 2022	-	154501
Alfa Romeo	Tonale	1.3 Hybrid Q4	SUV	Allrad	Benzin/Elektro	Nov 2025	-	802536
Alfa Romeo	Tonale	1.5 Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147915
Alfa Romeo	Tonale	1.5 Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147916
Alfa Romeo	Tonale	1.5 Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	802535
Alfa Romeo	Tonale	1.6 Vgt-d	SUV	Frontantrieb	Diesel	Sep 2022	-	151312
Alpina	B10	3.2	Stufenheck	Heckantrieb	Benzin	Aug 1997	Dec 1998	11723
Alpina	B10	3.3	Stufenheck	Heckantrieb	Benzin	Jan 1999	Feb 2003	14805
Alpina	B10	3.3	Kombi	Heckantrieb	Benzin	Feb 1999	Oct 2003	14806
Alpina	B10	3.4	Stufenheck	Heckantrieb	Benzin	Apr 1988	Dec 1992	11686
Alpina	B10	4	Stufenheck	Heckantrieb	Benzin	Apr 1993	Nov 1994	11699
Alpina	B10	4	Kombi	Heckantrieb	Benzin	Apr 1994	Sep 1994	11721
Alpina	B10	4.6	Stufenheck	Heckantrieb	Benzin	Mar 1994	Apr 1995	11700
Alpina	B10	4.6	Kombi	Heckantrieb	Benzin	Jun 1994	Jun 1995	11722
Alpina	B10	3.0 Allrad	Stufenheck	Allrad	Benzin	Oct 1993	Mar 1995	11685
Alpina	B10	3.0 Allrad	Kombi	Allrad	Benzin	Nov 1993	Apr 1996	11720
Alpina	B10	3.4 Biturbo	Stufenheck	Heckantrieb	Benzin	Jan 1989	Jun 1993	11719
Alpina	B10	4.6 V8	Stufenheck	Heckantrieb	Benzin	Dec 1996	Oct 1998	11725
Alpina	B10	4.6 V8	Kombi	Heckantrieb	Benzin	Jan 1997	Oct 1998	11727
Alpina	B10	4.6 V8	Stufenheck	Heckantrieb	Benzin	Oct 1998	Sep 2002	14807
Alpina	B10	4.6 V8	Kombi	Heckantrieb	Benzin	Oct 1998	Sep 2002	14808
Alpina	B10	V8 S 4.8	Stufenheck	Heckantrieb	Benzin	Jan 2002	May 2004	16731
Alpina	B10	V8 S 4.8	Kombi	Heckantrieb	Benzin	Jan 2002	May 2004	17602
Alpina	B11	3.4	Stufenheck	Heckantrieb	Benzin	Jul 1987	Sep 1987	11728
Alpina	B11	3.4	Stufenheck	Heckantrieb	Benzin	Jan 1987	Sep 1987	11729
Alpina	B11	3.4	Stufenheck	Heckantrieb	Benzin	Oct 1987	Dec 1993	11730
Alpina	B11	4	Stufenheck	Heckantrieb	Benzin	May 1993	Feb 1994	11731
Alpina	B12	5	Coupe	Heckantrieb	Benzin	Jun 1990	May 1994	11734
Alpina	B12	5	Stufenheck	Heckantrieb	Benzin	Jul 1988	Jan 1994	11744
Alpina	B12	5.6	Coupe	Heckantrieb	Benzin	Nov 1992	Dec 1996	11735
Alpina	B12	5.7	Stufenheck	Heckantrieb	Benzin	Dec 1995	Sep 1998	11733
Alpina	B12	6	Stufenheck	Heckantrieb	Benzin	Jul 1999	Jul 2001	14574
Alpina	B3	2.7	Stufenheck	Heckantrieb	Benzin	Sep 1987	Jun 1992	11640
Alpina	B3	2.7	Kombi	Heckantrieb	Benzin	Sep 1987	Jun 1992	11647
Alpina	B3	2.7	Cabriolet	Heckantrieb	Benzin	Sep 1987	Jun 1992	11651
Alpina	B3	3	Stufenheck	Heckantrieb	Benzin	Apr 1993	Dec 1995	11652
Alpina	B3	3	Kombi	Heckantrieb	Benzin	Apr 1993	Feb 1996	11659
Alpina	B3	3	Cabriolet	Heckantrieb	Benzin	Apr 1993	Feb 1996	11662
Alpina	B3	3.3	Stufenheck	Heckantrieb	Benzin	Mar 1999	Jul 2002	12142
Alpina	B3	3.3	Coupe	Heckantrieb	Benzin	Mar 1999	Jul 2002	13999
Alpina	B3	3.3	Kombi	Heckantrieb	Benzin	Mar 1999	Jul 2002	14804
Alpina	B3	3.3	Cabriolet	Heckantrieb	Benzin	Oct 2000	Jul 2002	15933
Alpina	B3	2.7 Allrad	Stufenheck	Allrad	Benzin	Sep 1987	Jun 1992	11643
Alpina	B3	3.4 S	Stufenheck	Heckantrieb	Benzin	Aug 2002	Jan 2006	17598
Alpina	B3	3.4 S	Kombi	Heckantrieb	Benzin	Aug 2002	Jan 2006	17599
Alpina	B3	3.4 S	Coupe	Heckantrieb	Benzin	Nov 2002	Jan 2006	17600
Alpina	B3	3.4 S	Cabriolet	Heckantrieb	Benzin	Nov 2002	Dec 2005	17601
Alpina	B3	Biturbo	Cabriolet	Heckantrieb	Benzin	Sep 2007	Mar 2010	12267
Alpina	B3	Biturbo	Stufenheck	Heckantrieb	Benzin	Mar 2013	Feb 2017	100932
Alpina	B3	Biturbo	Kombi	Heckantrieb	Benzin	Mar 2013	Feb 2017	100934
Alpina	B3	Bi-turbo	Coupe	Heckantrieb	Benzin	Sep 2007	Mar 2010	12268
Alpina	B3	Bi-turbo	Kombi	Heckantrieb	Benzin	Sep 2007	Mar 2010	12270
Alpina	B3	Bi-turbo	Stufenheck	Heckantrieb	Benzin	Sep 2007	Mar 2010	50880
Alpina	B3	Biturbo Allrad	Stufenheck	Allrad	Benzin	Mar 2013	Feb 2017	100933
Alpina	B3	Biturbo Allrad	Kombi	Allrad	Benzin	Mar 2013	Feb 2017	100935
Alpina	B3	Biturbo Allrad	Kombi	Allrad	Benzin	Jan 2023	Dec 2025	151536
Alpina	B3	Biturbo Allrad	Stufenheck	Allrad	Benzin	Jan 2023	Dec 2025	151537
Alpina	B3	Biturbo Allrad	Stufenheck	Allrad	Benzin	Sep 2024	Dec 2025	800862
Alpina	B3	Biturbo Allrad	Kombi	Allrad	Benzin	Sep 2024	Dec 2025	800863
Alpina	B3	Bi-turbo Allrad	Coupe	Allrad	Benzin	Mar 2008	Mar 2010	12269
Alpina	B3	Bi-turbo Allrad	Kombi	Allrad	Benzin	Mar 2008	Mar 2010	12271
Alpina	B3	Bi-turbo Allrad	Stufenheck	Allrad	Benzin	Mar 2008	Mar 2010	50881
Alpina	B3	S Biturbo	Stufenheck	Heckantrieb	Benzin	Mar 2017	Aug 2018	127341
Alpina	B3	S Biturbo	Kombi	Heckantrieb	Benzin	Mar 2017	Jun 2019	127343
Alpina	B3	S Biturbo Allrad	Stufenheck	Allrad	Benzin	Mar 2017	Aug 2018	127342
Alpina	B3	S Biturbo Allrad	Kombi	Allrad	Benzin	Mar 2017	Jun 2019	127344
Alpina	B4	3.0 B4 Biturbo	Coupe	Heckantrieb	Benzin	Mar 2014	Feb 2017	100936
Alpina	B4	3.0 B4 Biturbo Allrad	Coupe	Allrad	Benzin	Mar 2014	Feb 2017	100937
Alpina	B4	Biturbo	Cabriolet	Heckantrieb	Benzin	Mar 2014	Feb 2017	100939
Alpina	B4	S Biturbo	Coupe	Heckantrieb	Benzin	Mar 2017	Aug 2018	127345
Alpina	B4	S Biturbo	Cabriolet	Heckantrieb	Benzin	Mar 2017	Aug 2018	127347
Alpina	B4	S Biturbo Allrad	Coupe	Allrad	Benzin	Mar 2017	Aug 2018	127346
Alpina	B4 gran	Biturbo Allrad	Coupe	Allrad	Benzin	Mar 2022	Jun 2024	148355
Alpina	B4 gran	Biturbo Allrad	Coupe	Allrad	Benzin	Jul 2024	Dec 2025	800861
Alpina	B5	4.4	Stufenheck	Heckantrieb	Benzin	Mar 2005	Sep 2010	18532
Alpina	B5	4.4	Kombi	Heckantrieb	Benzin	Mar 2005	Sep 2010	18533
Alpina	B5	Biturbo	Kombi	Heckantrieb	Benzin	Sep 2010	Dec 2011	58567
Alpina	B5	Biturbo	Stufenheck	Heckantrieb	Benzin	Sep 2010	Dec 2011	109711
Alpina	B5	Biturbo	Stufenheck	Heckantrieb	Benzin	Jan 2015	Dec 2016	113465
Alpina	B5	Biturbo	Kombi	Heckantrieb	Benzin	Jan 2015	Dec 2016	113468
Alpina	B5	Biturbo	Stufenheck	Allrad	Benzin	Mar 2017	Jun 2020	126216
Alpina	B5	Biturbo	Kombi	Allrad	Benzin	Mar 2017	Jun 2020	126217
Alpina	B5	Biturbo	Stufenheck	Allrad	Benzin	Jul 2020	Jun 2023	142895
Alpina	B5	Biturbo	Kombi	Allrad	Benzin	Jul 2020	Feb 2024	142899
Alpina	B5	GT	Kombi	Allrad	Benzin	Mar 2023	Feb 2024	154761
Alpina	B5	GT	Stufenheck	Allrad	Benzin	Mar 2023	Jun 2023	155069
Alpina	B5	S	Stufenheck	Heckantrieb	Benzin	Oct 2007	Mar 2010	13896
Alpina	B5	S	Kombi	Heckantrieb	Benzin	Oct 2007	Mar 2010	110085
Alpina	B6	2.8	Stufenheck	Heckantrieb	Benzin	Mar 1978	Aug 1981	11664
Alpina	B6	2.8	Stufenheck	Heckantrieb	Benzin	Sep 1981	Mar 1983	11665
Alpina	B6	2.8	Stufenheck	Heckantrieb	Benzin	Nov 1983	Jul 1986	11666
Alpina	B6	2.8	Stufenheck	Heckantrieb	Benzin	Mar 1992	Jul 1993	11669
Alpina	B6	3.4	Stufenheck	Heckantrieb	Benzin	Aug 1986	Dec 1990	11667
Alpina	B6	3.4	Stufenheck	Heckantrieb	Benzin	Aug 1984	Jul 1987	11668
Alpina	B6	4.4	Cabriolet	Heckantrieb	Benzin	Apr 2006	Aug 2007	11972
Alpina	B6	4.4	Cabriolet	Heckantrieb	Benzin	Aug 2007	Aug 2010	12511
Alpina	B6	4.4	Coupe	Heckantrieb	Benzin	Apr 2006	Aug 2007	12535
Alpina	B6	4.4	Coupe	Heckantrieb	Benzin	Aug 2007	Aug 2010	12537


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Alfa Romeo 8 个 Ktype：Stelvio 直接复用既有尺寸组；Tonale 按改款前后及 PHEV/标准车高拆分为 4 个尺寸组。
* Stelvio 官方规格与既有组 `4687×1903×1671 mm` 一致。([Stellantis Media][1])
* Tonale 改款前官方规格为长度 4528 mm、不含后视镜宽度 1841 mm；MHEV/柴油高度 1601 mm，PHEV Q4 高度 1614 mm。2025 年更新车型长度变为 4522 mm，宽度和两种车高分支保持不变。

## 当前批次进度

* 输入 Ktype：100
* READY：8
* PENDING：92
* 当前引用的已确认尺寸组：5

  * 复用既有组：1
  * 本轮首次创建：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127369	127369	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV物理外廓。	READY
147895	147895	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	HIGH	改款前PHEV Q4车高分支。	READY
154501	154501	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	HIGH	改款前PHEV Q4车高分支。	READY
802536	802536	SUV	Tonale I facelift		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-FACELIFT-01	HIGH	2025改款PHEV Q4车高分支。	READY
147915	147915	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
147916	147916	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
802535	802535	SUV	Tonale I facelift		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-FACELIFT-01	HIGH	2025改款标准车高分支。	READY
151312	151312	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	4528	1841	1614	Alfa Romeo Tonale MY22 official price list and technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/316671alfaromeotonalepricelistmy23_april-644269c82fa26.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	4528	1841	1601	Alfa Romeo Tonale MY22 official price list and technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/316671alfaromeotonalepricelistmy23_april-644269c82fa26.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-FACELIFT-01	4522	1841	1614	Alfa Romeo Tonale official technical sheet (2025 update)	https://www.media.stellantis.com/uploads/em/attachment/12347/newtonaletechnicalsheet_1-68f118f94faf3.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-FACELIFT-01	4522	1841	1601	Alfa Romeo Tonale official technical sheet (2025 update)	https://www.media.stellantis.com/uploads/em/attachment/12347/newtonaletechnicalsheet_1-68f118f94faf3.pdf
```

## 下一步优先处理

优先按代际和车身集中闭合 Alpina B10、B11、B12：先处理 E34/E39 Sedan、Touring，再处理 E32/E38 Sedan 与 E31 Coupe，避免按发动机版本重复建组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-alfa-romeo-stelvio?utm_source=chatgpt.com "THE ALFA ROMEO STELVIO - Stellantis Media"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 17 个 Alpina B10 Ktype 映射。
* 首次闭合 B10 E34 Sedan、E34 Touring、E39 Sedan、E39 Touring 四个尺寸组；相同车身的发动机和驱动版本直接共用。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* READY：25
* PENDING：75
* 已确认尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11723	11723	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14805	14805	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14806	14806	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
11686	11686	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11699	11699	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11721	11721	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11700	11700	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11722	11722	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11685	11685	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11720	11720	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11719	11719	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11725	11725	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
11727	11727	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
14807	14807	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14808	14808	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
16731	16731	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
17602	17602	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B10-E39-SEDAN-01	4775	1800	1415	Auto-Data Alpina B10 E39 generation specifications	https://www.auto-data.net/en/alpina-b10-e39-generation-431
EU-ALPINA-B10-E39-WAGON-01	4805	1800	1420	Auto-Data Alpina B10 Touring E39 generation specifications	https://www.auto-data.net/en/alpina-b10-touring-e39-generation-432
EU-ALPINA-B10-E34-SEDAN-01	4720	1751	1400	UltimateSpecs Alpina E34 5 Series specifications	https://www.ultimatespecs.com/car-specs/Alpina/M11356/E34-5-Series
EU-ALPINA-B10-E34-WAGON-01	4720	1751	1400	Auto-Data Alpina B10 Touring E34 generation specifications	https://www.auto-data.net/en/alpina-b10-touring-e34-generation-434
```

## 下一步优先处理

集中闭合 Alpina B11 E32 与 B12 E31、E32、E38，重点区分 E32 标准轴距和长轴距物理分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alpina-b10-e39-generation-431 "Alpina B10 (E39) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Alpina B11/B12 共 9 个 Ktype。
* 建立 B11 E32 Sedan、B12 E32 Sedan、B12 E31 Coupe、B12 E38 Sedan 四个尺寸组。
* B12 E32 按标准轴距 B12 5.0 落盘；官方资料确认其基于 BMW 750i E32，Automobile-Catalog 给出不含后视镜三维 `4910×1845×1391 mm`，未采用数据库中混入的长轴版本尺寸。([阿尔皮娜汽车][1])
* B12 E31 两种发动机版本共用 `4780×1855×1330 mm`；B12 E38 5.7 与 6.0 共用 `4984×1862×1415 mm`。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY：34
* PENDING：66
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11728	11728	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11729	11729	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11730	11730	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11731	11731	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11734	11734	Coupe	B12 E31	E31	2	EU-ALPINA-B12-E31-COUPE-01	HIGH	E31双门Coupe物理外廓。	READY
11744	11744	Sedan	B12 E32	E32	4	EU-ALPINA-B12-E32-SEDAN-01	HIGH	E32标准轴距四门轿车物理外廓。	READY
11735	11735	Coupe	B12 E31	E31	2	EU-ALPINA-B12-E31-COUPE-01	HIGH	E31双门Coupe物理外廓。	READY
11733	11733	Sedan	B12 E38	E38	4	EU-ALPINA-B12-E38-SEDAN-01	HIGH	E38四门轿车物理外廓。	READY
14574	14574	Sedan	B12 E38	E38	4	EU-ALPINA-B12-E38-SEDAN-01	HIGH	E38四门轿车物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B11-E32-SEDAN-01	4910	1845	1411	ALPINA E32 official model history; Drom Alpina B11 dimensions	https://www.alpina-automobiles.li/en/product-world/model-history/bmw-7-series/bmw-7-series-e32/;https://www.drom.ru/catalog/alpina/b11/specs/dimensions/
EU-ALPINA-B12-E31-COUPE-01	4780	1855	1330	Auto-Data Alpina B12 Coupe E31 specifications	https://www.auto-data.net/en/alpina-b12-coupe-e31-5.0-i-v12-350hp-1675
EU-ALPINA-B12-E32-SEDAN-01	4910	1845	1391	ALPINA E32 official model history; Automobile-Catalog Alpina B12 5.0 specifications	https://www.alpina-automobiles.li/en/product-world/model-history/bmw-7-series/bmw-7-series-e32/;https://www.automobile-catalog.com/car/1993/286985/alpina_b12_5_0.html
EU-ALPINA-B12-E38-SEDAN-01	4984	1862	1415	Auto-Data Alpina B12 E38 generation specifications	https://www.auto-data.net/en/alpina-b12-e38-generation-455
```

## 下一步优先处理

集中闭合 Alpina B3 E30、E36、E46：按 Sedan、Wagon、Coupe、Convertible 分别首次建组，再批量关联 2.7、3.0、3.3 与 3.4 S Ktype。

推进信号：CONTINUE

[1]: https://www.alpina-automobiles.li/en/product-world/model-history/bmw-7-series/bmw-7-series-e32/ "BMW 7 Series E32: ALPINA Automobiles"
[2]: https://www.auto-data.net/en/alpina-b12-coupe-e31-5.7-i-v12-24v-416hp-1676?utm_source=chatgpt.com "Alpina B12 Coupe (E31) 5.7 i V12 24V (416 Hp)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Alpina B3 E30、E36、E46 共 15 个输入 Ktype，新增 17 条映射行和 13 个尺寸组。
* E30 Sedan 的两门、四门分支分别建组；四驱版本外廓为 `4325×1662×1400 mm`，不同于后驱版本的 `4325×1645×1355 mm`。([汽车目录][1])
* E36 按 Sedan、Touring、Convertible 分组，采用对应配置的不含后视镜尺寸，未使用混合多个车身的代际汇总高度。([汽车目录][2])
* E46 的 3.3 与 3.4 S 在相同车身形式下共用外廓；Sedan、Touring、Coupe、Convertible 分别建组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：49
* READY 映射行：51
* PENDING Ktype：51
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11640_2dr	11640	Sedan	B3 E30	E30	2	EU-ALPINA-B3-E30-SEDAN-2D-01	MEDIUM	同一Ktype覆盖E30两门轿车分支。	READY
11640_4dr	11640	Sedan	B3 E30	E30	4	EU-ALPINA-B3-E30-SEDAN-4D-01	MEDIUM	同一Ktype覆盖E30四门轿车分支。	READY
11647	11647	Wagon	B3 E30	E30	5	EU-ALPINA-B3-E30-WAGON-01	HIGH	E30五门Touring物理外廓。	READY
11651	11651	Convertible	B3 E30	E30	2	EU-ALPINA-B3-E30-CONVERTIBLE-01	HIGH	E30双门Convertible物理外廓。	READY
11652	11652	Sedan	B3 E36	E36	4	EU-ALPINA-B3-E36-SEDAN-01	HIGH	E36四门Sedan物理外廓。	READY
11659	11659	Wagon	B3 E36	E36	5	EU-ALPINA-B3-E36-WAGON-01	HIGH	E36五门Touring物理外廓。	READY
11662	11662	Convertible	B3 E36	E36	2	EU-ALPINA-B3-E36-CONVERTIBLE-01	HIGH	E36双门Convertible物理外廓。	READY
12142	12142	Sedan	B3 E46	E46	4	EU-ALPINA-B3-E46-SEDAN-01	HIGH	E46四门Sedan物理外廓。	READY
13999	13999	Coupe	B3 E46	E46	2	EU-ALPINA-B3-E46-COUPE-01	HIGH	E46双门Coupe物理外廓。	READY
14804	14804	Wagon	B3 E46	E46	5	EU-ALPINA-B3-E46-WAGON-01	HIGH	E46五门Touring物理外廓。	READY
15933	15933	Convertible	B3 E46	E46	2	EU-ALPINA-B3-E46-CONVERTIBLE-01	HIGH	E46双门Convertible物理外廓。	READY
11643_2dr	11643	Sedan	B3 E30	E30	2	EU-ALPINA-B3-E30-SEDAN-2D-AWD-01	MEDIUM	同一四驱Ktype覆盖E30两门轿车分支。	READY
11643_4dr	11643	Sedan	B3 E30	E30	4	EU-ALPINA-B3-E30-SEDAN-4D-AWD-01	MEDIUM	同一四驱Ktype覆盖E30四门轿车分支。	READY
17598	17598	Sedan	B3 S E46	E46	4	EU-ALPINA-B3-E46-SEDAN-01	HIGH	E46四门Sedan物理外廓。	READY
17599	17599	Wagon	B3 S E46	E46	5	EU-ALPINA-B3-E46-WAGON-01	HIGH	E46五门Touring物理外廓。	READY
17600	17600	Coupe	B3 S E46	E46	2	EU-ALPINA-B3-E46-COUPE-01	HIGH	E46双门Coupe物理外廓。	READY
17601	17601	Convertible	B3 S E46	E46	2	EU-ALPINA-B3-E46-CONVERTIBLE-01	HIGH	E46双门Convertible物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-E30-SEDAN-2D-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 E30 Sedan specifications	https://www.automobile-catalog.com/car/1990/286505/alpina_b3_2_7_cat.html
EU-ALPINA-B3-E30-SEDAN-4D-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 E30 Sedan specifications	https://www.automobile-catalog.com/car/1990/286505/alpina_b3_2_7_cat.html
EU-ALPINA-B3-E30-WAGON-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 Touring E30 specifications	https://www.automobile-catalog.com/car/1990/286595/alpina_b3_2_7_touring_cat.html
EU-ALPINA-B3-E30-CONVERTIBLE-01	4325	1645	1345	Automobile-Catalog Alpina B3 2.7 Cabrio E30 specifications	https://www.automobile-catalog.com/car/1990/286610/alpina_b3_2_7_cabrio_cat.html
EU-ALPINA-B3-E36-SEDAN-01	4433	1698	1378	Automobile-Catalog Alpina B3 3.0 E36 Sedan specifications	https://www.automobile-catalog.com/car/1994/287180/alpina_b3_3_0.html
EU-ALPINA-B3-E36-WAGON-01	4433	1698	1371	Automobile-Catalog Alpina B3 3.0 Touring E36 specifications	https://www.automobile-catalog.com/car/1995/287240/alpina_b3_3_0_touring.html
EU-ALPINA-B3-E36-CONVERTIBLE-01	4433	1710	1328	Automobile-Catalog Alpina B3 3.0 Cabrio E36 specifications	https://www.automobile-catalog.com/car/1994/287210/alpina_b3_3_0_cabrio.html
EU-ALPINA-B3-E46-SEDAN-01	4471	1739	1395	Automobile-Catalog Alpina B3 3.3 Sedan; Automobile-Catalog Alpina B3 S Sedan	https://www.automobile-catalog.com/car/2001/287855/alpina_b3_3_3.html;https://www.automobile-catalog.com/car/2004/288065/alpina_b3_s.html
EU-ALPINA-B3-E46-COUPE-01	4488	1757	1367	Automobile-Catalog Alpina B3 3.3 Coupe; Automobile-Catalog Alpina B3 S Coupe	https://www.automobile-catalog.com/car/1999/287885/alpina_b3_3_3_coupe.html;https://www.automobile-catalog.com/car/2004/288095/alpina_b3_s_coupe.html
EU-ALPINA-B3-E46-WAGON-01	4478	1739	1389	Automobile-Catalog Alpina B3 3.3 Touring; Automobile-Catalog Alpina B3 S Touring	https://www.automobile-catalog.com/car/2000/287945/alpina_b3_3_3_touring.html;https://www.automobile-catalog.com/car/2004/288155/alpina_b3_s_touring.html
EU-ALPINA-B3-E46-CONVERTIBLE-01	4488	1757	1372	Automobile-Catalog Alpina B3 3.3 Cabrio; Automobile-Catalog Alpina B3 S Cabrio	https://www.automobile-catalog.com/car/2001/288020/alpina_b3_3_3_cabrio_switch-tronic.html;https://www.automobile-catalog.com/car/2004/288125/alpina_b3_s_cabrio.html
EU-ALPINA-B3-E30-SEDAN-2D-AWD-01	4325	1662	1400	Automobile-Catalog Alpina B3 2.7 Allrad E30 Sedan specifications	https://www.automobile-catalog.com/car/1987/286625/alpina_b3_2_7_allrad_cat.html
EU-ALPINA-B3-E30-SEDAN-4D-AWD-01	4325	1662	1400	Automobile-Catalog Alpina B3 2.7 Allrad E30 Sedan specifications	https://www.automobile-catalog.com/car/1987/286625/alpina_b3_2_7_allrad_cat.html
```

## 下一步优先处理

集中闭合 B3 E9x、F30/F31、G20/G21 与 B4 F32/F33、G26，优先区分 Sedan、Touring、Coupe、Convertible、Gran Coupe，以及普通版和改款版外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/286625/alpina_b3_2_7_allrad_cat.html?utm_source=chatgpt.com "1987 Alpina B3 2.7 Allrad catalyst Specs Review (150 kW / 204 PS / 201 hp) (since August 1987 for Europe )"
[2]: https://www.automobile-catalog.com/car/1994/287180/alpina_b3_3_0.html?utm_source=chatgpt.com "1994 Alpina B3 3.0 Specs Review (184 kW / 250 PS / 247 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/2001/287855/alpina_b3_3_3.html?utm_source=chatgpt.com "2001 Alpina B3 3.3 Specs Review (206 kW / 280 PS / 276 hp) (up to July 2001 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 B3 E9x 与 F30/F31 共 15 个 Ktype，新增 20 条映射。
* `50880` 覆盖 E90 改款前后两个不同长度分支，因此拆为 `prefl`、`facelift`；E91 四驱因车高变化单独建组，E92 后驱/四驱外廓一致而复用同组。([encyCARpedia][1])
* F30/F31 的 2013–2017 Ktype 按改款前后拆分；后驱与四驱在对应车身和改款阶段共用尺寸组。官方技术表分别确认改款前 Sedan/Touring 为 `4628×1811×1409/1410 mm`，B3 S 阶段为 `4632×1811×1431 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射行：71
* PENDING Ktype：36
* 已确认尺寸组：37
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12267	12267	Convertible	B3 BiTurbo E93	E93	2	EU-ALPINA-B3-E93-CONVERTIBLE-01	HIGH	E93双门硬顶Convertible物理外廓。	READY
100932_prefl	100932	Sedan	B3 BiTurbo F30	F30	4	EU-ALPINA-B3-F30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖F30改款前分支。	READY
100932_facelift	100932	Sedan	B3 BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖F30改款后分支。	READY
100934_prefl	100934	Wagon	B3 BiTurbo F31	F31	5	EU-ALPINA-B3-F31-WAGON-PREFL-01	HIGH	同一Ktype覆盖F31改款前分支。	READY
100934_facelift	100934	Wagon	B3 BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖F31改款后分支。	READY
12268	12268	Coupe	B3 BiTurbo E92	E92	2	EU-ALPINA-B3-E92-COUPE-01	HIGH	E92双门Coupe物理外廓。	READY
12270	12270	Wagon	B3 BiTurbo E91	E91	5	EU-ALPINA-B3-E91-WAGON-RWD-01	HIGH	E91后驱Touring物理外廓。	READY
50880_prefl	50880	Sedan	B3 BiTurbo E90	E90	4	EU-ALPINA-B3-E90-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖E90改款前分支。	READY
50880_facelift	50880	Sedan	B3 BiTurbo E90 LCI	E90	4	EU-ALPINA-B3-E90-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖E90改款后分支。	READY
100933_prefl	100933	Sedan	B3 BiTurbo F30	F30	4	EU-ALPINA-B3-F30-SEDAN-PREFL-01	HIGH	同一四驱Ktype覆盖F30改款前分支。	READY
100933_facelift	100933	Sedan	B3 BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	同一四驱Ktype覆盖F30改款后分支。	READY
100935_prefl	100935	Wagon	B3 BiTurbo F31	F31	5	EU-ALPINA-B3-F31-WAGON-PREFL-01	HIGH	同一四驱Ktype覆盖F31改款前分支。	READY
100935_facelift	100935	Wagon	B3 BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	同一四驱Ktype覆盖F31改款后分支。	READY
12269	12269	Coupe	B3 BiTurbo E92	E92	2	EU-ALPINA-B3-E92-COUPE-01	HIGH	E92四驱双门Coupe外廓与后驱版一致。	READY
12271	12271	Wagon	B3 BiTurbo E91	E91	5	EU-ALPINA-B3-E91-WAGON-AWD-01	HIGH	E91四驱Touring车高分支。	READY
50881	50881	Sedan	B3 BiTurbo E90	E90	4	EU-ALPINA-B3-E90-SEDAN-AWD-01	HIGH	E90四驱Sedan车高分支。	READY
127341	127341	Sedan	B3 S BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	F30 LCI后驱Sedan物理外廓。	READY
127343	127343	Wagon	B3 S BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	F31 LCI后驱Touring物理外廓。	READY
127342	127342	Sedan	B3 S BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	F30 LCI四驱Sedan外廓与后驱版一致。	READY
127344	127344	Wagon	B3 S BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	F31 LCI四驱Touring外廓与后驱版一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-E93-CONVERTIBLE-01	4580	1782	1395	Auto-Data Alpina B3 Cabrio E93 specifications	https://www.auto-data.net/en/alpina-b3-cabrio-e93-3.0i-biturbo-360hp-swtch-tronic-1699
EU-ALPINA-B3-F30-SEDAN-PREFL-01	4628	1811	1409	BMW ALPINA B3 BiTurbo official technical brochure	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b3_biturbo_saloon_touring.pdf
EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	4632	1811	1431	BMW ALPINA B3 S BiTurbo official technical brochure	https://i.i-sgcm.com/new_cars/cars/12239/brochures/brochure_20180129122504.pdf
EU-ALPINA-B3-F31-WAGON-PREFL-01	4628	1811	1410	BMW ALPINA B3 BiTurbo official technical brochure	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b3_biturbo_saloon_touring.pdf
EU-ALPINA-B3-F31-WAGON-FACELIFT-01	4632	1811	1431	BMW ALPINA B3 S BiTurbo official technical brochure	https://i.i-sgcm.com/new_cars/cars/12239/brochures/brochure_20180129122504.pdf
EU-ALPINA-B3-E92-COUPE-01	4578	1782	1395	Encycarpedia Alpina B3 Biturbo Coupe E92 specifications; Encycarpedia Alpina B3 Biturbo Coupe Allrad E92 specifications	https://www.encycarpedia.com/alpina/07-b3-biturbo-coupe-e92;https://www.encycarpedia.com/alpina/08-b3-biturbo-coupe-allrad-e92
EU-ALPINA-B3-E91-WAGON-RWD-01	4541	1817	1450	Automobile-Catalog Alpina B3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2009/1186025/alpina_b3_biturbo_touring.html
EU-ALPINA-B3-E90-SEDAN-PREFL-01	4520	1817	1422	Encycarpedia Alpina B3 Biturbo E90 pre-facelift specifications	https://www.encycarpedia.com/alpina/07-b3-biturbo-e90-saloon
EU-ALPINA-B3-E90-SEDAN-FACELIFT-01	4545	1817	1422	Automobile-Catalog Alpina B3 Biturbo E90 phase II specifications	https://www.automobile-catalog.com/make/alpina/3-series_e90_e91_e92_e93_alpina/3-series_e90-2_sedan_alpina/2008.html
EU-ALPINA-B3-E91-WAGON-AWD-01	4541	1817	1465	Automobile-Catalog Alpina B3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2008/1186040/alpina_b3_biturbo_touring_allrad.html
EU-ALPINA-B3-E90-SEDAN-AWD-01	4545	1817	1437	Encycarpedia Alpina B3 Biturbo Allrad E90 specifications	https://www.encycarpedia.com/alpina/08-b3-biturbo-allrad-e90-saloon
```

## 下一步优先处理

集中闭合 B3 G20/G21 的 2022 LCI 与 2024 GT 分支，以及 B4 F32/F33 和 G26 Gran Coupe 的改款前后尺寸组。

推进信号：CONTINUE

[1]: https://www.encycarpedia.com/alpina/07-b3-biturbo-e90-saloon?utm_source=chatgpt.com "2007 (E90) Alpina B3 Biturbo Specifications & Performance"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合剩余 4 个 B3 G20/G21 Ktype 和 8 个 B4 Ktype。
* B3 G20 Sedan 与 G21 Touring 分别建组；普通 LCI 与 GT 阶段外部三维一致，因此直接复用对应车身组。Sedan 为 `4723×1827×1440 mm`，Touring 为 `4723×1827×1438 mm`。([阿尔皮纳汽车][1])
* B4 F32 Coupe 的改款前后尺寸均为 `4640×1825×1373 mm`；F33 Convertible 均为 `4640×1825×1380 mm`，不因后驱、四驱或 S 版本重复建组。([七论坛][2])
* B4 G26 改款前为 `4792×1850×1440 mm`，2024 GT 改款后长度变为 4800 mm，建立独立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：76
* READY 映射行：83
* PENDING Ktype：24
* 已确认尺寸组：43
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151536	151536	Wagon	B3 G21 LCI	G21	5	EU-ALPINA-B3-G21-WAGON-LCI-01	HIGH	G21 LCI五门Touring物理外廓。	READY
151537	151537	Sedan	B3 G20 LCI	G20	4	EU-ALPINA-B3-G20-SEDAN-LCI-01	HIGH	G20 LCI四门Sedan物理外廓。	READY
800862	800862	Sedan	B3 GT G20	G20	4	EU-ALPINA-B3-G20-SEDAN-LCI-01	MEDIUM	G20 GT阶段外廓与对应LCI Sedan一致。	READY
800863	800863	Wagon	B3 GT G21	G21	5	EU-ALPINA-B3-G21-WAGON-LCI-01	MEDIUM	G21 GT阶段外廓与对应LCI Touring一致。	READY
100936	100936	Coupe	B4 F32	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32双门Coupe物理外廓。	READY
100937	100937	Coupe	B4 F32	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32四驱Coupe外廓与后驱版一致。	READY
100939	100939	Convertible	B4 F33	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-01	HIGH	F33双门Convertible物理外廓。	READY
127345	127345	Coupe	B4 S F32 LCI	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32 LCI Coupe外廓与改款前一致。	READY
127347	127347	Convertible	B4 S F33 LCI	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-01	HIGH	F33 LCI Convertible外廓与改款前一致。	READY
127346	127346	Coupe	B4 S F32 LCI	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32 LCI四驱Coupe外廓与后驱版一致。	READY
148355	148355	Coupe	B4 Gran Coupe G26	G26	5	EU-ALPINA-B4-G26-GRAN-COUPE-PREFL-01	HIGH	G26改款前五门Gran Coupe物理外廓。	READY
800861	800861	Coupe	B4 GT Gran Coupe G26	G26	5	EU-ALPINA-B4-G26-GRAN-COUPE-FACELIFT-01	HIGH	G26 GT改款后五门Gran Coupe物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-G21-WAGON-LCI-01	4723	1827	1438	ALPINA Automobiles B3 official technical data	https://www.alpinaautomobiles.com.au/models/b3/technical-data/
EU-ALPINA-B3-G20-SEDAN-LCI-01	4723	1827	1440	ALPINA Automobiles B3 official technical data	https://www.alpinaautomobiles.com.au/models/b3/technical-data/
EU-ALPINA-B4-F32-COUPE-01	4640	1825	1373	BMW ALPINA B4 BiTurbo official technical data; BMW ALPINA B4 S BiTurbo official brochure	https://www.7-forum.com/news/2013/alpina/b4_biturbo_technische_daten.pdf;https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-F33-CONVERTIBLE-01	4640	1825	1380	BMW ALPINA B4 S BiTurbo official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-G26-GRAN-COUPE-PREFL-01	4792	1850	1440	BMW ALPINA B4 Gran Coupe official press release and technical data	https://www.autoevolution.com/pdf/news_attachements/2023-alpina-b4-gran-coupe-debuts-with-more-torque-than-bmw-m4-competition-185238.pdf
EU-ALPINA-B4-G26-GRAN-COUPE-FACELIFT-01	4800	1850	1440	Auto-Data Alpina B4 Gran Coupe G26 facelift specifications	https://www.auto-data.net/en/alpina-b4-gran-coupe-g26-facelift-2024-generation-10266
```

## 下一步优先处理

集中闭合剩余 14 个 Alpina B5 Ktype：按 E60 Sedan、E61 Touring、F10 Sedan、F11 Touring、G30 Sedan、G31 Touring 建组，并单独核对 GT 阶段是否改变外部三维。

推进信号：CONTINUE

[1]: https://www.alpinaautomobiles.com.au/models/b3/technical-data/?utm_source=chatgpt.com "Technical Data - ALPINA Automobiles"
[2]: https://www.7-forum.com/news/2013/alpina/b4_biturbo_technische_daten.pdf "BMW_ALPINA_B4_BITURBO_PressInfo_2013_11_DE.pdf"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合剩余 14 个 Alpina B5 Ktype。
* E60/E61、F10/F11 改款前后、G30/G31 改款前后分别建组；同一车身阶段内的普通版、S 与 GT 不因动力版本重复建组。
* E60/E61 官方资料分别确认 `4841×1846×1468 mm` 与 `4843×1846×1491 mm`。F10/F11 改款前后存在长度或车高差异，因此保持独立尺寸组。([Alpina Register][1])
* G30/G31 改款前官方技术资料统一为 `4956×1868×1466 mm`；改款后长度增至 4978 mm，GT 使用相同认证外廓。([i.i-sgcm.com][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：97
* PENDING Ktype：10
* 已确认尺寸组：53
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18532	18532	Sedan	B5 E60	E60	4	EU-ALPINA-B5-E60-SEDAN-01	HIGH	E60四门Sedan物理外廓。	READY
18533	18533	Wagon	B5 E61	E61	5	EU-ALPINA-B5-E61-WAGON-01	HIGH	E61五门Touring物理外廓。	READY
58567	58567	Wagon	B5 BiTurbo F11	F11	5	EU-ALPINA-B5-F11-WAGON-PREFL-01	HIGH	F11改款前五门Touring物理外廓。	READY
109711	109711	Sedan	B5 BiTurbo F10	F10	4	EU-ALPINA-B5-F10-SEDAN-PREFL-01	HIGH	F10改款前四门Sedan物理外廓。	READY
113465	113465	Sedan	B5 BiTurbo F10 LCI	F10	4	EU-ALPINA-B5-F10-SEDAN-FACELIFT-01	HIGH	F10改款后四门Sedan物理外廓。	READY
113468	113468	Wagon	B5 BiTurbo F11 LCI	F11	5	EU-ALPINA-B5-F11-WAGON-FACELIFT-01	HIGH	F11改款后五门Touring物理外廓。	READY
126216	126216	Sedan	B5 BiTurbo G30	G30	4	EU-ALPINA-B5-G30-SEDAN-PREFL-01	HIGH	G30改款前四门Sedan物理外廓。	READY
126217	126217	Wagon	B5 BiTurbo G31	G31	5	EU-ALPINA-B5-G31-WAGON-PREFL-01	HIGH	G31改款前五门Touring物理外廓。	READY
142895	142895	Sedan	B5 BiTurbo G30 LCI	G30	4	EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	HIGH	G30改款后四门Sedan物理外廓。	READY
142899	142899	Wagon	B5 BiTurbo G31 LCI	G31	5	EU-ALPINA-B5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门Touring物理外廓。	READY
154761	154761	Wagon	B5 GT G31	G31	5	EU-ALPINA-B5-G31-WAGON-FACELIFT-01	HIGH	GT Touring认证外廓与G31改款版一致。	READY
155069	155069	Sedan	B5 GT G30	G30	4	EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	HIGH	GT Sedan认证外廓与G30改款版一致。	READY
13896	13896	Sedan	B5 S E60	E60	4	EU-ALPINA-B5-E60-SEDAN-01	HIGH	E60 B5 S外廓与对应Sedan一致。	READY
110085	110085	Wagon	B5 S E61	E61	5	EU-ALPINA-B5-E61-WAGON-01	HIGH	E61 B5 S外廓与对应Touring一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B5-E60-SEDAN-01	4841	1846	1468	BMW ALPINA B5 official sales brochure	https://www.thealpinaregister.com/downloads/brochures/alpina_b5_2005couk.pdf
EU-ALPINA-B5-E61-WAGON-01	4843	1846	1491	BMW ALPINA B5 official sales brochure	https://www.thealpinaregister.com/downloads/brochures/alpina_b5_2005couk.pdf
EU-ALPINA-B5-F11-WAGON-PREFL-01	4913	1860	1453	Auto-Data Alpina B5 Touring F11 specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-generation-4040
EU-ALPINA-B5-F10-SEDAN-PREFL-01	4905	1860	1469	Auto-Data Alpina B5 Sedan F10 specifications	https://www.auto-data.net/en/alpina-b5-sedan-f10-generation-4041
EU-ALPINA-B5-F10-SEDAN-FACELIFT-01	4913	1860	1469	Auto-Data Alpina B5 Sedan F10 LCI specifications	https://www.auto-data.net/en/alpina-b5-sedan-f10-lci-facelift-2013-generation-4879
EU-ALPINA-B5-F11-WAGON-FACELIFT-01	4913	1860	1480	Auto-Data Alpina B5 Touring F11 LCI specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-lci-facelift-2013-generation-4878
EU-ALPINA-B5-G30-SEDAN-PREFL-01	4956	1868	1466	BMW ALPINA B5 BiTurbo AWD official technical brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G31-WAGON-PREFL-01	4956	1868	1466	BMW ALPINA B5 BiTurbo AWD official technical brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	4978	1868	1466	Auto-Data Alpina B5 Sedan G30 facelift specifications	https://www.auto-data.net/en/alpina-b5-sedan-g30-facelift-2020-generation-8272
EU-ALPINA-B5-G31-WAGON-FACELIFT-01	4978	1868	1466	Auto-Data Alpina B5 Touring G31 facelift specifications	https://www.auto-data.net/en/alpina-b5-touring-g31-facelift-2020-generation-8271
```

## 下一步优先处理

集中闭合最后 10 个 Alpina B6 Ktype：先区分早期 E21、E30、E36 Sedan，再闭合 E64 Convertible 与 E63 Coupe 的改款前后边界。

推进信号：CONTINUE

[1]: https://www.thealpinaregister.com/downloads/brochures/alpina_b5_2005couk.pdf?utm_source=chatgpt.com "MANUFACTURER OF EXCLUSIVE AUTOMOBILES"
[2]: https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf?utm_source=chatgpt.com "BMW ALPINA B5 BITURBO"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_201-300_ktype_dimension_mapping_final.tsv
- left18448_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合最后 10 个 Alpina B6 Ktype。E21、E30 2.8、E30 B6 3.5 两门/四门、E36，以及 E63 Coupe/E64 Convertible 均已建立或关联确定尺寸组。([UltimateSpecs][1])
* 已完成轻量机械检查：表头正确、109 个 `id` 唯一、60 个 `DIMENSION_GROUP_ID` 唯一、映射引用完全闭合、无孤立尺寸组、三维及来源字段完整。
* 两个指定文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：109
* PENDING：0
* 最终尺寸组：60
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127369	127369	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV物理外廓。	READY
147895	147895	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	HIGH	改款前PHEV Q4车高分支。	READY
154501	154501	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	HIGH	改款前PHEV Q4车高分支。	READY
802536	802536	SUV	Tonale I facelift		5	EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-FACELIFT-01	HIGH	2025改款PHEV Q4车高分支。	READY
147915	147915	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
147916	147916	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
802535	802535	SUV	Tonale I facelift		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-FACELIFT-01	HIGH	2025改款标准车高分支。	READY
151312	151312	SUV	Tonale I		5	EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	HIGH	改款前标准车高分支。	READY
11723	11723	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14805	14805	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14806	14806	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
11686	11686	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11699	11699	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11721	11721	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11700	11700	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11722	11722	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11685	11685	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11720	11720	Wagon	B10 E34	E34	5	EU-ALPINA-B10-E34-WAGON-01	HIGH	E34五门Touring物理外廓。	READY
11719	11719	Sedan	B10 E34	E34	4	EU-ALPINA-B10-E34-SEDAN-01	HIGH	E34四门轿车物理外廓。	READY
11725	11725	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
11727	11727	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
14807	14807	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
14808	14808	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
16731	16731	Sedan	B10 E39	E39	4	EU-ALPINA-B10-E39-SEDAN-01	HIGH	E39四门轿车物理外廓。	READY
17602	17602	Wagon	B10 E39	E39	5	EU-ALPINA-B10-E39-WAGON-01	HIGH	E39五门Touring物理外廓。	READY
11728	11728	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11729	11729	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11730	11730	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11731	11731	Sedan	B11 E32	E32	4	EU-ALPINA-B11-E32-SEDAN-01	HIGH	E32四门轿车物理外廓。	READY
11734	11734	Coupe	B12 E31	E31	2	EU-ALPINA-B12-E31-COUPE-01	HIGH	E31双门Coupe物理外廓。	READY
11744	11744	Sedan	B12 E32	E32	4	EU-ALPINA-B12-E32-SEDAN-01	HIGH	E32标准轴距四门轿车物理外廓。	READY
11735	11735	Coupe	B12 E31	E31	2	EU-ALPINA-B12-E31-COUPE-01	HIGH	E31双门Coupe物理外廓。	READY
11733	11733	Sedan	B12 E38	E38	4	EU-ALPINA-B12-E38-SEDAN-01	HIGH	E38四门轿车物理外廓。	READY
14574	14574	Sedan	B12 E38	E38	4	EU-ALPINA-B12-E38-SEDAN-01	HIGH	E38四门轿车物理外廓。	READY
11640_2dr	11640	Sedan	B3 E30	E30	2	EU-ALPINA-B3-E30-SEDAN-2D-01	MEDIUM	同一Ktype覆盖E30两门轿车分支。	READY
11640_4dr	11640	Sedan	B3 E30	E30	4	EU-ALPINA-B3-E30-SEDAN-4D-01	MEDIUM	同一Ktype覆盖E30四门轿车分支。	READY
11647	11647	Wagon	B3 E30	E30	5	EU-ALPINA-B3-E30-WAGON-01	HIGH	E30五门Touring物理外廓。	READY
11651	11651	Convertible	B3 E30	E30	2	EU-ALPINA-B3-E30-CONVERTIBLE-01	HIGH	E30双门Convertible物理外廓。	READY
11652	11652	Sedan	B3 E36	E36	4	EU-ALPINA-B3-E36-SEDAN-01	HIGH	E36四门Sedan物理外廓。	READY
11659	11659	Wagon	B3 E36	E36	5	EU-ALPINA-B3-E36-WAGON-01	HIGH	E36五门Touring物理外廓。	READY
11662	11662	Convertible	B3 E36	E36	2	EU-ALPINA-B3-E36-CONVERTIBLE-01	HIGH	E36双门Convertible物理外廓。	READY
12142	12142	Sedan	B3 E46	E46	4	EU-ALPINA-B3-E46-SEDAN-01	HIGH	E46四门Sedan物理外廓。	READY
13999	13999	Coupe	B3 E46	E46	2	EU-ALPINA-B3-E46-COUPE-01	HIGH	E46双门Coupe物理外廓。	READY
14804	14804	Wagon	B3 E46	E46	5	EU-ALPINA-B3-E46-WAGON-01	HIGH	E46五门Touring物理外廓。	READY
15933	15933	Convertible	B3 E46	E46	2	EU-ALPINA-B3-E46-CONVERTIBLE-01	HIGH	E46双门Convertible物理外廓。	READY
11643_2dr	11643	Sedan	B3 E30	E30	2	EU-ALPINA-B3-E30-SEDAN-2D-AWD-01	MEDIUM	同一四驱Ktype覆盖E30两门轿车分支。	READY
11643_4dr	11643	Sedan	B3 E30	E30	4	EU-ALPINA-B3-E30-SEDAN-4D-AWD-01	MEDIUM	同一四驱Ktype覆盖E30四门轿车分支。	READY
17598	17598	Sedan	B3 S E46	E46	4	EU-ALPINA-B3-E46-SEDAN-01	HIGH	E46四门Sedan物理外廓。	READY
17599	17599	Wagon	B3 S E46	E46	5	EU-ALPINA-B3-E46-WAGON-01	HIGH	E46五门Touring物理外廓。	READY
17600	17600	Coupe	B3 S E46	E46	2	EU-ALPINA-B3-E46-COUPE-01	HIGH	E46双门Coupe物理外廓。	READY
17601	17601	Convertible	B3 S E46	E46	2	EU-ALPINA-B3-E46-CONVERTIBLE-01	HIGH	E46双门Convertible物理外廓。	READY
12267	12267	Convertible	B3 BiTurbo E93	E93	2	EU-ALPINA-B3-E93-CONVERTIBLE-01	HIGH	E93双门硬顶Convertible物理外廓。	READY
100932_prefl	100932	Sedan	B3 BiTurbo F30	F30	4	EU-ALPINA-B3-F30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖F30改款前分支。	READY
100932_facelift	100932	Sedan	B3 BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖F30改款后分支。	READY
100934_prefl	100934	Wagon	B3 BiTurbo F31	F31	5	EU-ALPINA-B3-F31-WAGON-PREFL-01	HIGH	同一Ktype覆盖F31改款前分支。	READY
100934_facelift	100934	Wagon	B3 BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖F31改款后分支。	READY
12268	12268	Coupe	B3 BiTurbo E92	E92	2	EU-ALPINA-B3-E92-COUPE-01	HIGH	E92双门Coupe物理外廓。	READY
12270	12270	Wagon	B3 BiTurbo E91	E91	5	EU-ALPINA-B3-E91-WAGON-RWD-01	HIGH	E91后驱Touring物理外廓。	READY
50880_prefl	50880	Sedan	B3 BiTurbo E90	E90	4	EU-ALPINA-B3-E90-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖E90改款前分支。	READY
50880_facelift	50880	Sedan	B3 BiTurbo E90 LCI	E90	4	EU-ALPINA-B3-E90-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖E90改款后分支。	READY
100933_prefl	100933	Sedan	B3 BiTurbo F30	F30	4	EU-ALPINA-B3-F30-SEDAN-PREFL-01	HIGH	同一四驱Ktype覆盖F30改款前分支。	READY
100933_facelift	100933	Sedan	B3 BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	同一四驱Ktype覆盖F30改款后分支。	READY
100935_prefl	100935	Wagon	B3 BiTurbo F31	F31	5	EU-ALPINA-B3-F31-WAGON-PREFL-01	HIGH	同一四驱Ktype覆盖F31改款前分支。	READY
100935_facelift	100935	Wagon	B3 BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	同一四驱Ktype覆盖F31改款后分支。	READY
151536	151536	Wagon	B3 G21 LCI	G21	5	EU-ALPINA-B3-G21-WAGON-LCI-01	HIGH	G21 LCI五门Touring物理外廓。	READY
151537	151537	Sedan	B3 G20 LCI	G20	4	EU-ALPINA-B3-G20-SEDAN-LCI-01	HIGH	G20 LCI四门Sedan物理外廓。	READY
800862	800862	Sedan	B3 GT G20	G20	4	EU-ALPINA-B3-G20-SEDAN-LCI-01	MEDIUM	G20 GT阶段外廓与对应LCI Sedan一致。	READY
800863	800863	Wagon	B3 GT G21	G21	5	EU-ALPINA-B3-G21-WAGON-LCI-01	MEDIUM	G21 GT阶段外廓与对应LCI Touring一致。	READY
12269	12269	Coupe	B3 BiTurbo E92	E92	2	EU-ALPINA-B3-E92-COUPE-01	HIGH	E92四驱双门Coupe外廓与后驱版一致。	READY
12271	12271	Wagon	B3 BiTurbo E91	E91	5	EU-ALPINA-B3-E91-WAGON-AWD-01	HIGH	E91四驱Touring车高分支。	READY
50881	50881	Sedan	B3 BiTurbo E90	E90	4	EU-ALPINA-B3-E90-SEDAN-AWD-01	HIGH	E90四驱Sedan车高分支。	READY
127341	127341	Sedan	B3 S BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	F30 LCI后驱Sedan物理外廓。	READY
127343	127343	Wagon	B3 S BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	F31 LCI后驱Touring物理外廓。	READY
127342	127342	Sedan	B3 S BiTurbo F30 LCI	F30	4	EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	HIGH	F30 LCI四驱Sedan外廓与后驱版一致。	READY
127344	127344	Wagon	B3 S BiTurbo F31 LCI	F31	5	EU-ALPINA-B3-F31-WAGON-FACELIFT-01	HIGH	F31 LCI四驱Touring外廓与后驱版一致。	READY
100936	100936	Coupe	B4 F32	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32双门Coupe物理外廓。	READY
100937	100937	Coupe	B4 F32	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32四驱Coupe外廓与后驱版一致。	READY
100939	100939	Convertible	B4 F33	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-01	HIGH	F33双门Convertible物理外廓。	READY
127345	127345	Coupe	B4 S F32 LCI	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32 LCI Coupe外廓与改款前一致。	READY
127347	127347	Convertible	B4 S F33 LCI	F33	2	EU-ALPINA-B4-F33-CONVERTIBLE-01	HIGH	F33 LCI Convertible外廓与改款前一致。	READY
127346	127346	Coupe	B4 S F32 LCI	F32	2	EU-ALPINA-B4-F32-COUPE-01	HIGH	F32 LCI四驱Coupe外廓与后驱版一致。	READY
148355	148355	Coupe	B4 Gran Coupe G26	G26	5	EU-ALPINA-B4-G26-GRAN-COUPE-PREFL-01	HIGH	G26改款前五门Gran Coupe物理外廓。	READY
800861	800861	Coupe	B4 GT Gran Coupe G26	G26	5	EU-ALPINA-B4-G26-GRAN-COUPE-FACELIFT-01	HIGH	G26 GT改款后五门Gran Coupe物理外廓。	READY
18532	18532	Sedan	B5 E60	E60	4	EU-ALPINA-B5-E60-SEDAN-01	HIGH	E60四门Sedan物理外廓。	READY
18533	18533	Wagon	B5 E61	E61	5	EU-ALPINA-B5-E61-WAGON-01	HIGH	E61五门Touring物理外廓。	READY
58567	58567	Wagon	B5 BiTurbo F11	F11	5	EU-ALPINA-B5-F11-WAGON-PREFL-01	HIGH	F11改款前五门Touring物理外廓。	READY
109711	109711	Sedan	B5 BiTurbo F10	F10	4	EU-ALPINA-B5-F10-SEDAN-PREFL-01	HIGH	F10改款前四门Sedan物理外廓。	READY
113465	113465	Sedan	B5 BiTurbo F10 LCI	F10	4	EU-ALPINA-B5-F10-SEDAN-FACELIFT-01	HIGH	F10改款后四门Sedan物理外廓。	READY
113468	113468	Wagon	B5 BiTurbo F11 LCI	F11	5	EU-ALPINA-B5-F11-WAGON-FACELIFT-01	HIGH	F11改款后五门Touring物理外廓。	READY
126216	126216	Sedan	B5 BiTurbo G30	G30	4	EU-ALPINA-B5-G30-SEDAN-PREFL-01	HIGH	G30改款前四门Sedan物理外廓。	READY
126217	126217	Wagon	B5 BiTurbo G31	G31	5	EU-ALPINA-B5-G31-WAGON-PREFL-01	HIGH	G31改款前五门Touring物理外廓。	READY
142895	142895	Sedan	B5 BiTurbo G30 LCI	G30	4	EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	HIGH	G30改款后四门Sedan物理外廓。	READY
142899	142899	Wagon	B5 BiTurbo G31 LCI	G31	5	EU-ALPINA-B5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门Touring物理外廓。	READY
154761	154761	Wagon	B5 GT G31	G31	5	EU-ALPINA-B5-G31-WAGON-FACELIFT-01	HIGH	GT Touring认证外廓与G31改款版一致。	READY
155069	155069	Sedan	B5 GT G30	G30	4	EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	HIGH	GT Sedan认证外廓与G30改款版一致。	READY
13896	13896	Sedan	B5 S E60	E60	4	EU-ALPINA-B5-E60-SEDAN-01	HIGH	E60 B5 S外廓与对应Sedan一致。	READY
110085	110085	Wagon	B5 S E61	E61	5	EU-ALPINA-B5-E61-WAGON-01	HIGH	E61 B5 S外廓与对应Touring一致。	READY
11664	11664	Sedan	B6 E21	E21	2	EU-ALPINA-B6-E21-SEDAN-01	HIGH	E21双门Sedan物理外廓。	READY
11665	11665	Sedan	B6 E21	E21	2	EU-ALPINA-B6-E21-SEDAN-01	HIGH	E21双门Sedan物理外廓。	READY
11666	11666	Sedan	B6 E30	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-01	HIGH	E30 B6 2.8双门Sedan物理外廓。	READY
11669	11669	Sedan	B6 E36	E36	4	EU-ALPINA-B6-E36-SEDAN-01	HIGH	E36四门Sedan物理外廓。	READY
11667_2dr	11667	Sedan	B6 E30	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	MEDIUM	同一Ktype覆盖E30 B6 3.5两门轿车分支。	READY
11667_4dr	11667	Sedan	B6 E30	E30	4	EU-ALPINA-B6-E30-SEDAN-4D-01	MEDIUM	同一Ktype覆盖E30 B6 3.5四门轿车分支。	READY
11668_2dr	11668	Sedan	B6 E30	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	MEDIUM	同一Ktype覆盖E30 B6 3.5两门轿车分支。	READY
11668_4dr	11668	Sedan	B6 E30	E30	4	EU-ALPINA-B6-E30-SEDAN-4D-01	MEDIUM	同一Ktype覆盖E30 B6 3.5四门轿车分支。	READY
11972	11972	Convertible	B6 E64	E64	2	EU-ALPINA-B6-E64-CONVERTIBLE-01	HIGH	E64双门Convertible物理外廓。	READY
12511	12511	Convertible	B6 S E64	E64	2	EU-ALPINA-B6-E64-CONVERTIBLE-01	HIGH	E64 B6 S外廓与B6 Convertible一致。	READY
12535	12535	Coupe	B6 E63	E63	2	EU-ALPINA-B6-E63-COUPE-01	HIGH	E63双门Coupe物理外廓。	READY
12537	12537	Coupe	B6 S E63	E63	2	EU-ALPINA-B6-E63-COUPE-01	HIGH	E63 B6 S外廓与B6 Coupe一致。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_201-300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Alfa Romeo Stelvio official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-alfa-romeo-stelvio
EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-PREFL-01	4528	1841	1614	Alfa Romeo Tonale MY22 official price list and technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/316671alfaromeotonalepricelistmy23_april-644269c82fa26.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-PHEV-FACELIFT-01	4522	1841	1614	Alfa Romeo Tonale official technical sheet (2025 update)	https://www.media.stellantis.com/uploads/em/attachment/12347/newtonaletechnicalsheet_1-68f118f94faf3.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-PREFL-01	4528	1841	1601	Alfa Romeo Tonale MY22 official price list and technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/316671alfaromeotonalepricelistmy23_april-644269c82fa26.pdf
EU-ALFA-ROMEO-TONALE-I-SUV-STANDARD-FACELIFT-01	4522	1841	1601	Alfa Romeo Tonale official technical sheet (2025 update)	https://www.media.stellantis.com/uploads/em/attachment/12347/newtonaletechnicalsheet_1-68f118f94faf3.pdf
EU-ALPINA-B10-E39-SEDAN-01	4775	1800	1415	Auto-Data Alpina B10 E39 generation specifications	https://www.auto-data.net/en/alpina-b10-e39-generation-431
EU-ALPINA-B10-E39-WAGON-01	4805	1800	1420	Auto-Data Alpina B10 Touring E39 generation specifications	https://www.auto-data.net/en/alpina-b10-touring-e39-generation-432
EU-ALPINA-B10-E34-SEDAN-01	4720	1751	1400	UltimateSpecs Alpina E34 5 Series specifications	https://www.ultimatespecs.com/car-specs/Alpina/M11356/E34-5-Series
EU-ALPINA-B10-E34-WAGON-01	4720	1751	1400	Auto-Data Alpina B10 Touring E34 generation specifications	https://www.auto-data.net/en/alpina-b10-touring-e34-generation-434
EU-ALPINA-B11-E32-SEDAN-01	4910	1845	1411	ALPINA E32 official model history; Drom Alpina B11 dimensions	https://www.alpina-automobiles.li/en/product-world/model-history/bmw-7-series/bmw-7-series-e32/;https://www.drom.ru/catalog/alpina/b11/specs/dimensions/
EU-ALPINA-B12-E31-COUPE-01	4780	1855	1330	Auto-Data Alpina B12 Coupe E31 specifications	https://www.auto-data.net/en/alpina-b12-coupe-e31-5.0-i-v12-350hp-1675
EU-ALPINA-B12-E32-SEDAN-01	4910	1845	1391	ALPINA E32 official model history; Automobile-Catalog Alpina B12 5.0 specifications	https://www.alpina-automobiles.li/en/product-world/model-history/bmw-7-series/bmw-7-series-e32/;https://www.automobile-catalog.com/car/1993/286985/alpina_b12_5_0.html
EU-ALPINA-B12-E38-SEDAN-01	4984	1862	1415	Auto-Data Alpina B12 E38 generation specifications	https://www.auto-data.net/en/alpina-b12-e38-generation-455
EU-ALPINA-B3-E30-SEDAN-2D-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 E30 Sedan specifications	https://www.automobile-catalog.com/car/1990/286505/alpina_b3_2_7_cat.html
EU-ALPINA-B3-E30-SEDAN-4D-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 E30 Sedan specifications	https://www.automobile-catalog.com/car/1990/286505/alpina_b3_2_7_cat.html
EU-ALPINA-B3-E30-WAGON-01	4325	1645	1355	Automobile-Catalog Alpina B3 2.7 Touring E30 specifications	https://www.automobile-catalog.com/car/1990/286595/alpina_b3_2_7_touring_cat.html
EU-ALPINA-B3-E30-CONVERTIBLE-01	4325	1645	1345	Automobile-Catalog Alpina B3 2.7 Cabrio E30 specifications	https://www.automobile-catalog.com/car/1990/286610/alpina_b3_2_7_cabrio_cat.html
EU-ALPINA-B3-E36-SEDAN-01	4433	1698	1378	Automobile-Catalog Alpina B3 3.0 E36 Sedan specifications	https://www.automobile-catalog.com/car/1994/287180/alpina_b3_3_0.html
EU-ALPINA-B3-E36-WAGON-01	4433	1698	1371	Automobile-Catalog Alpina B3 3.0 Touring E36 specifications	https://www.automobile-catalog.com/car/1995/287240/alpina_b3_3_0_touring.html
EU-ALPINA-B3-E36-CONVERTIBLE-01	4433	1710	1328	Automobile-Catalog Alpina B3 3.0 Cabrio E36 specifications	https://www.automobile-catalog.com/car/1994/287210/alpina_b3_3_0_cabrio.html
EU-ALPINA-B3-E46-SEDAN-01	4471	1739	1395	Automobile-Catalog Alpina B3 3.3 Sedan; Automobile-Catalog Alpina B3 S Sedan	https://www.automobile-catalog.com/car/2001/287855/alpina_b3_3_3.html;https://www.automobile-catalog.com/car/2004/288065/alpina_b3_s.html
EU-ALPINA-B3-E46-COUPE-01	4488	1757	1367	Automobile-Catalog Alpina B3 3.3 Coupe; Automobile-Catalog Alpina B3 S Coupe	https://www.automobile-catalog.com/car/1999/287885/alpina_b3_3_3_coupe.html;https://www.automobile-catalog.com/car/2004/288095/alpina_b3_s_coupe.html
EU-ALPINA-B3-E46-WAGON-01	4478	1739	1389	Automobile-Catalog Alpina B3 3.3 Touring; Automobile-Catalog Alpina B3 S Touring	https://www.automobile-catalog.com/car/2000/287945/alpina_b3_3_3_touring.html;https://www.automobile-catalog.com/car/2004/288155/alpina_b3_s_touring.html
EU-ALPINA-B3-E46-CONVERTIBLE-01	4488	1757	1372	Automobile-Catalog Alpina B3 3.3 Cabrio; Automobile-Catalog Alpina B3 S Cabrio	https://www.automobile-catalog.com/car/2001/288020/alpina_b3_3_3_cabrio_switch-tronic.html;https://www.automobile-catalog.com/car/2004/288125/alpina_b3_s_cabrio.html
EU-ALPINA-B3-E30-SEDAN-2D-AWD-01	4325	1662	1400	Automobile-Catalog Alpina B3 2.7 Allrad E30 Sedan specifications	https://www.automobile-catalog.com/car/1987/286625/alpina_b3_2_7_allrad_cat.html
EU-ALPINA-B3-E30-SEDAN-4D-AWD-01	4325	1662	1400	Automobile-Catalog Alpina B3 2.7 Allrad E30 Sedan specifications	https://www.automobile-catalog.com/car/1987/286625/alpina_b3_2_7_allrad_cat.html
EU-ALPINA-B3-E93-CONVERTIBLE-01	4580	1782	1395	Auto-Data Alpina B3 Cabrio E93 specifications	https://www.auto-data.net/en/alpina-b3-cabrio-e93-3.0i-biturbo-360hp-swtch-tronic-1699
EU-ALPINA-B3-F30-SEDAN-PREFL-01	4628	1811	1409	BMW ALPINA B3 BiTurbo official technical brochure	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b3_biturbo_saloon_touring.pdf
EU-ALPINA-B3-F30-SEDAN-FACELIFT-01	4632	1811	1431	BMW ALPINA B3 S BiTurbo official technical brochure	https://i.i-sgcm.com/new_cars/cars/12239/brochures/brochure_20180129122504.pdf
EU-ALPINA-B3-F31-WAGON-PREFL-01	4628	1811	1410	BMW ALPINA B3 BiTurbo official technical brochure	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b3_biturbo_saloon_touring.pdf
EU-ALPINA-B3-F31-WAGON-FACELIFT-01	4632	1811	1431	BMW ALPINA B3 S BiTurbo official technical brochure	https://i.i-sgcm.com/new_cars/cars/12239/brochures/brochure_20180129122504.pdf
EU-ALPINA-B3-E92-COUPE-01	4578	1782	1395	Encycarpedia Alpina B3 Biturbo Coupe E92 specifications; Encycarpedia Alpina B3 Biturbo Coupe Allrad E92 specifications	https://www.encycarpedia.com/alpina/07-b3-biturbo-coupe-e92;https://www.encycarpedia.com/alpina/08-b3-biturbo-coupe-allrad-e92
EU-ALPINA-B3-E91-WAGON-RWD-01	4541	1817	1450	Automobile-Catalog Alpina B3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2009/1186025/alpina_b3_biturbo_touring.html
EU-ALPINA-B3-E90-SEDAN-PREFL-01	4520	1817	1422	Encycarpedia Alpina B3 Biturbo E90 pre-facelift specifications	https://www.encycarpedia.com/alpina/07-b3-biturbo-e90-saloon
EU-ALPINA-B3-E90-SEDAN-FACELIFT-01	4545	1817	1422	Automobile-Catalog Alpina B3 Biturbo E90 phase II specifications	https://www.automobile-catalog.com/make/alpina/3-series_e90_e91_e92_e93_alpina/3-series_e90-2_sedan_alpina/2008.html
EU-ALPINA-B3-G21-WAGON-LCI-01	4723	1827	1438	ALPINA Automobiles B3 official technical data	https://www.alpinaautomobiles.com.au/models/b3/technical-data/
EU-ALPINA-B3-G20-SEDAN-LCI-01	4723	1827	1440	ALPINA Automobiles B3 official technical data	https://www.alpinaautomobiles.com.au/models/b3/technical-data/
EU-ALPINA-B3-E91-WAGON-AWD-01	4541	1817	1465	Automobile-Catalog Alpina B3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2008/1186040/alpina_b3_biturbo_touring_allrad.html
EU-ALPINA-B3-E90-SEDAN-AWD-01	4545	1817	1437	Encycarpedia Alpina B3 Biturbo Allrad E90 specifications	https://www.encycarpedia.com/alpina/08-b3-biturbo-allrad-e90-saloon
EU-ALPINA-B4-F32-COUPE-01	4640	1825	1373	BMW ALPINA B4 BiTurbo official technical data; BMW ALPINA B4 S BiTurbo official brochure	https://www.7-forum.com/news/2013/alpina/b4_biturbo_technische_daten.pdf;https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-F33-CONVERTIBLE-01	4640	1825	1380	BMW ALPINA B4 S BiTurbo official brochure	https://i.i-sgcm.com/new_cars/cars/12240/brochures/brochure_20180129030056.pdf
EU-ALPINA-B4-G26-GRAN-COUPE-PREFL-01	4792	1850	1440	BMW ALPINA B4 Gran Coupe official press release and technical data	https://www.autoevolution.com/pdf/news_attachements/2023-alpina-b4-gran-coupe-debuts-with-more-torque-than-bmw-m4-competition-185238.pdf
EU-ALPINA-B4-G26-GRAN-COUPE-FACELIFT-01	4800	1850	1440	Auto-Data Alpina B4 Gran Coupe G26 facelift specifications	https://www.auto-data.net/en/alpina-b4-gran-coupe-g26-facelift-2024-generation-10266
EU-ALPINA-B5-E60-SEDAN-01	4841	1846	1468	BMW ALPINA B5 official sales brochure	https://www.thealpinaregister.com/downloads/brochures/alpina_b5_2005couk.pdf
EU-ALPINA-B5-E61-WAGON-01	4843	1846	1491	BMW ALPINA B5 official sales brochure	https://www.thealpinaregister.com/downloads/brochures/alpina_b5_2005couk.pdf
EU-ALPINA-B5-F11-WAGON-PREFL-01	4913	1860	1453	Auto-Data Alpina B5 Touring F11 specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-generation-4040
EU-ALPINA-B5-F10-SEDAN-PREFL-01	4905	1860	1469	Auto-Data Alpina B5 Sedan F10 specifications	https://www.auto-data.net/en/alpina-b5-sedan-f10-generation-4041
EU-ALPINA-B5-F10-SEDAN-FACELIFT-01	4913	1860	1469	Auto-Data Alpina B5 Sedan F10 LCI specifications	https://www.auto-data.net/en/alpina-b5-sedan-f10-lci-facelift-2013-generation-4879
EU-ALPINA-B5-F11-WAGON-FACELIFT-01	4913	1860	1480	Auto-Data Alpina B5 Touring F11 LCI specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-lci-facelift-2013-generation-4878
EU-ALPINA-B5-G30-SEDAN-PREFL-01	4956	1868	1466	BMW ALPINA B5 BiTurbo AWD official technical brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G31-WAGON-PREFL-01	4956	1868	1466	BMW ALPINA B5 BiTurbo AWD official technical brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G30-SEDAN-FACELIFT-01	4978	1868	1466	Auto-Data Alpina B5 Sedan G30 facelift specifications	https://www.auto-data.net/en/alpina-b5-sedan-g30-facelift-2020-generation-8272
EU-ALPINA-B5-G31-WAGON-FACELIFT-01	4978	1868	1466	Auto-Data Alpina B5 Touring G31 facelift specifications	https://www.auto-data.net/en/alpina-b5-touring-g31-facelift-2020-generation-8271
EU-ALPINA-B6-E21-SEDAN-01	4355	1610	1360	UltimateSpecs Alpina E21 B6 2.8 specifications	https://www.ultimatespecs.com/car-specs/Alpina/109860/Alpina-E21-3-Series-B6-28.html
EU-ALPINA-B6-E30-SEDAN-2D-01	4325	1645	1350	Automobile-Catalog Alpina B6 2.8 E30 specifications	https://www.automobile-catalog.com/car/1984/286460/alpina_b6_2_8.html
EU-ALPINA-B6-E36-SEDAN-01	4433	1698	1373	Encycarpedia Alpina B6 2.8 E36 Sedan specifications	https://www.encycarpedia.com/alpina/91-b6-2-8-e36-saloon
EU-ALPINA-B6-E30-SEDAN-2D-02	4325	1645	1355	Automobile-Catalog Alpina B6 3.5 E30 specifications	https://www.automobile-catalog.com/car/1987/286670/alpina_b6_3_5.html
EU-ALPINA-B6-E30-SEDAN-4D-01	4325	1645	1355	Automobile-Catalog Alpina B6 3.5 E30 specifications	https://www.automobile-catalog.com/car/1987/286670/alpina_b6_3_5.html
EU-ALPINA-B6-E64-CONVERTIBLE-01	4820	1855	1371	Auto-Data Alpina B6 Cabrio E64 specifications	https://www.auto-data.net/en/alpina-b6-cabrio-e64-4.4-v8-500hp-switch-tronic-1661
EU-ALPINA-B6-E63-COUPE-01	4820	1855	1371	Auto-Data Alpina B6 Coupe E63 specifications	https://www.auto-data.net/en/alpina-b6-coupe-e63-4.4-v8-500hp-1659
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_201-300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ultimatespecs.com/car-specs/Alpina/109860/Alpina-E21-3-Series-B6-28.html?utm_source=chatgpt.com "Alpina E21 3 Series B6 2.8 Specs"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（367 行）
- 累计尺寸组：dimension_groups_final.tsv（153 行）

