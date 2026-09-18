# 任务：left18448 第 2001-2100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0021__6d260cc2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2001-2100 行

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
left18448 第 2001-2100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2001-2100_ktype_dimension_mapping_final.tsv
- left18448_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E30-SEDAN-320IS-01	4325	1645	1380
EU-BMW-3-E30-TOURING-WAGON-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1698	1393
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-COUPE-01	4433	1710	1366
EU-BMW-3-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-E36-TOURING-WAGON-01	4433	1698	1391
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-01	4488	1757	1372
EU-BMW-3-E46-COUPE-01	4488	1757	1369
EU-BMW-3-E46-SEDAN-01	4471	1739	1415
EU-BMW-3-E46-TOURING-WAGON-01	4478	1739	1409
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	4633	1811	1429
EU-BMW-3-F30-SEDAN-RWD-PREFL-01	4624	1811	1429
EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	4633	1811	1429
EU-BMW-3-F31-WAGON-RWD-PREFL-01	4624	1811	1429
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	4824	1828	1508
EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	4713	1827	1440
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-PREFL-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-PHEV-FACELIFT-01	4713	1827	1442
EU-BMW-3-G21-WAGON-XDRIVE-PHEV-PREFL-01	4709	1827	1442

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	3	323 TI	Schrägheck	Heckantrieb	Benzin	Sep 1997	Aug 2000	8784
BMW	3	323 TI	Schrägheck	Heckantrieb	Benzin	Jan 1999	Aug 2000	121968
BMW	3	325 CI	Coupe	Heckantrieb	Benzin	Sep 2000	May 2006	15449
BMW	3	325 CI	Cabriolet	Heckantrieb	Benzin	Sep 2000	Aug 2006	15451
BMW	3	325 D	Cabriolet	Heckantrieb	Diesel	Sep 2009	Sep 2013	12491
BMW	3	325 D	Kombi	Heckantrieb	Diesel	Feb 2010	Jun 2012	34767
BMW	3	325 D	Coupe	Heckantrieb	Diesel	Sep 2009	Jun 2013	34768
BMW	3	325 D	Cabriolet	Heckantrieb	Diesel	Mar 2007	Dec 2010	53145
BMW	3	325 D	Coupe	Heckantrieb	Diesel	Feb 2007	Feb 2010	53146
BMW	3	325 D	Schrägheck	Heckantrieb	Diesel	Jul 2013	Jun 2016	53384
BMW	3	325 D	Kombi	Heckantrieb	Diesel	Mar 2013	Feb 2016	59219
BMW	3	325 D	Stufenheck	Heckantrieb	Diesel	Mar 2013	Feb 2016	59223
BMW	3	325 D	Schrägheck	Heckantrieb	Diesel	Jul 2013	Jun 2016	59804
BMW	3	325 D	Stufenheck	Heckantrieb	Diesel	Mar 2013	Feb 2016	116643
BMW	3	325 D	Kombi	Heckantrieb	Diesel	Mar 2013	Feb 2016	116644
BMW	3	325 D	Stufenheck	Heckantrieb	Diesel	Mar 2016	Feb 2018	118077
BMW	3	325 D	Kombi	Heckantrieb	Diesel	Mar 2016	Feb 2018	118078
BMW	3	325 D	Schrägheck	Heckantrieb	Diesel	Jul 2016	Feb 2018	120542
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	Sep 2000	Feb 2005	15454
BMW	3	325 I	Kombi	Heckantrieb	Benzin	Sep 2000	Feb 2005	15455
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	Dec 2004	Dec 2011	18450
BMW	3	325 I	Kombi	Heckantrieb	Benzin	Dec 2004	Aug 2008	18759
BMW	3	325 I	Coupe	Heckantrieb	Benzin	Mar 2010	Jun 2013	52830
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	Oct 2006	Dec 2013	52885
BMW	3	325 I	Coupe	Heckantrieb	Benzin	Mar 2010	Jun 2013	53148
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	Jan 2006	Dec 2011	54518
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	Mar 2007	Dec 2011	117778
BMW	3	325 I	Coupe	Heckantrieb	Benzin	Mar 2010	Oct 2013	118827
BMW	3	325 I	Kombi	Heckantrieb	Benzin	Dec 2004	Dec 2010	124763
BMW	3	325 I Xdrive	Coupe	Allrad	Benzin	Mar 2010	Apr 2013	118826
BMW	3	325 IS	Coupe	Heckantrieb	Benzin	Oct 1991	Aug 1995	35674
BMW	3	325 TI	Schrägheck	Heckantrieb	Benzin	Apr 2001	Dec 2004	15925
BMW	3	325 XI	Stufenheck	Allrad	Benzin	Sep 2000	Feb 2005	15456
BMW	3	325 XI	Kombi	Allrad	Benzin	Sep 2000	Feb 2005	15457
BMW	3	325 XI	Stufenheck	Allrad	Benzin	Sep 2005	Aug 2008	19101
BMW	3	325 XI	Kombi	Allrad	Benzin	Aug 2005	Aug 2008	19104
BMW	3	328 CI	Coupe	Heckantrieb	Benzin	Dec 1998	May 2000	10503
BMW	3	328 I	Kombi	Heckantrieb	Benzin	Jun 1999	May 2000	12140
BMW	3	328 I	Stufenheck	Heckantrieb	Benzin	Nov 2011	Oct 2018	12470
BMW	3	328 I	Kombi	Heckantrieb	Benzin	Jul 2012	Jun 2015	55124
BMW	3	328 I	Stufenheck	Heckantrieb	Benzin	Sep 2006	Dec 2011	58077
BMW	3	328 I	Coupe	Heckantrieb	Benzin	Jun 2006	Jun 2013	58079
BMW	3	328 I	Schrägheck	Heckantrieb	Benzin	Mar 2013	Jun 2016	58797
BMW	3	328 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Aug 2016	57294
BMW	3	328 I Xdrive	Kombi	Allrad	Benzin	Mar 2013	Jun 2016	59402
BMW	3	328 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2013	Jun 2016	59801
BMW	3	330 CD	Coupe	Heckantrieb	Diesel	Mar 2003	Jul 2006	17206
BMW	3	330 CI	Cabriolet	Heckantrieb	Benzin	Jun 2000	Aug 2006	14926
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Oct 1999	Feb 2005	13874
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Oct 1999	Feb 2005	14185
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Mar 2003	Feb 2005	17351
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Mar 2003	Feb 2005	17353
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Sep 2005	Sep 2008	18968
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Dec 2004	Aug 2008	18969
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Jul 2012	Jun 2019	55128
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Jul 2012	Oct 2018	58949
BMW	3	330 D	Schrägheck	Heckantrieb	Diesel	Mar 2014	-	100827
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Jul 2012	Oct 2018	117281
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Jul 2012	Jun 2019	117286
BMW	3	330 D	Schrägheck	Heckantrieb	Diesel	Mar 2014	-	117290
BMW	3	330 D	Kombi	Heckantrieb	Diesel	Jun 2005	May 2012	124776
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	Sep 2005	Dec 2011	124777
BMW	3	330 D M Performance Power KIT Xdrive	Kombi	Allrad	Diesel	Mar 2013	Jun 2019	117289
BMW	3	330 D Xdrive	Stufenheck	Allrad	Diesel	Mar 2013	Oct 2018	59222
BMW	3	330 D Xdrive	Kombi	Allrad	Diesel	Mar 2013	Jun 2019	59404
BMW	3	330 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2014	-	100818
BMW	3	330 D Xdrive	Stufenheck	Allrad	Diesel	Mar 2013	Oct 2018	117282
BMW	3	330 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2014	-	117291
BMW	3	330 E	Stufenheck	Heckantrieb	Benzin/Elektro	Nov 2015	Oct 2018	117341
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	Jun 2000	Feb 2005	14922
BMW	3	330 I	Kombi	Heckantrieb	Benzin	Jun 2000	Feb 2005	14923
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	Dec 2004	Oct 2011	18451
BMW	3	330 I	Kombi	Heckantrieb	Benzin	Aug 2005	Aug 2007	18760
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	Jul 2015	Oct 2018	113407
BMW	3	330 I	Kombi	Heckantrieb	Benzin	Jul 2015	Jun 2019	113444
BMW	3	330 I	Coupe	Heckantrieb	Benzin	Sep 2007	Jun 2013	118548
BMW	3	330 I	Cabriolet	Heckantrieb	Benzin	Mar 2007	Feb 2010	118553
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	Mar 2007	Dec 2011	118622
BMW	3	330 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	-	120265
BMW	3	330 I	Kombi	Heckantrieb	Benzin	Mar 2007	Jun 2012	143242
BMW	3	330 I	Kombi	Heckantrieb	Benzin	Jul 2019	-	148049
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	Jul 2022	-	148051
BMW	3	330 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2015	Oct 2018	113408
BMW	3	330 I Xdrive	Kombi	Allrad	Benzin	Jul 2015	Jun 2019	113445
BMW	3	330 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2016	-	120266
BMW	3	330 I Xdrive	Kombi	Allrad	Benzin	Jul 2019	-	148050
BMW	3	330 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2022	-	148052
BMW	3	330 XD	Kombi	Allrad	Diesel	Jan 2000	Mar 2003	14773
BMW	3	330 XD	Stufenheck	Allrad	Diesel	Jan 2000	Feb 2003	14774
BMW	3	330 XD	Stufenheck	Allrad	Diesel	Sep 2002	Dec 2004	17352
BMW	3	330 XD	Kombi	Allrad	Diesel	Aug 2002	May 2005	17354
BMW	3	330 XD	Stufenheck	Allrad	Diesel	Sep 2005	Aug 2008	19103
BMW	3	330 XD	Kombi	Allrad	Diesel	Sep 2005	Jun 2012	19106
BMW	3	330 XI	Stufenheck	Allrad	Benzin	Jun 2000	Feb 2005	14802
BMW	3	330 XI	Kombi	Allrad	Benzin	Jun 2000	Feb 2005	14803
BMW	3	330 XI	Coupe	Allrad	Benzin	Jun 2000	Jul 2006	14921
BMW	3	330 XI	Stufenheck	Allrad	Benzin	Sep 2005	Aug 2007	19102
BMW	3	330 XI	Kombi	Allrad	Benzin	Sep 2005	Aug 2007	19105
BMW	3	335 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2013	Oct 2018	53089
BMW	3	335 D Xdrive	Kombi	Allrad	Diesel	Nov 2013	Jun 2019	100708


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批 100 个输入 Ktype 的全量映射；因部分 Ktype 跨越改款前后，最终形成 136 条 `READY` 映射。
* 新建 5 个尺寸组：E46 四驱三厢、E46 汽油四驱旅行版、G20 改款后 xDrive 三厢、G21 改款前/后 xDrive 旅([宝马集团新闻][1])0xi Touring 因高度 1429 mm 独立建组。E46 四驱 Sedan 使用 4471×1739×1434。([汽车数据][2])xDrive 的外廓为 4624×1811×1429，与普通后驱三厢一致，因此复用现有 RWD 组；其他普通 F30/F31 xDrive 分支按已确认的 1434 mm 高度组关联。([宝马集团新闻][1])rive 外廓已与历史 PHEV xDrive 尺寸组分离，未覆盖或改写既有尺寸事实。([宝马集团新闻][3])入 Ktype：100
* READY 映射：136
* PENDING 映射：0
* 当前引用尺寸组：32
* 本批新增尺寸组：5
* `id`、`DIMENSION_GROUP_ID` 唯一性、映射引用闭合、尺寸及来源非空检查：全部通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8784	8784	Hatchback	3 Series E36	E36/5	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH		READY
121968	121968	Hatchback	3 Series E36	E36/5	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH		READY
15449	15449	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
15451	15451	Convertible	3 Series E46	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-01	HIGH		READY
12491_prefl	12491	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
12491_facelift	12491	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
34767	34767	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
34768_prefl	34768	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
34768_facelift	34768	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
53145_prefl	53145	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
53145_facelift	53145	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
53146	53146	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH		READY
53384	53384	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
59219_prefl	59219	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
59219_facelift	59219	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
59223_prefl	59223	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
59223_facelift	59223	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
59804	59804	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
116643_prefl	116643	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
116643_facelift	116643	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
116644_prefl	116644	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
116644_facelift	116644	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
118077	118077	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
118078	118078	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
120542	120542	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
15454	15454	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
15455	15455	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18450_prefl	18450	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
18450_facelift	18450	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
18759	18759	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH		READY
52830	52830	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
52885_prefl	52885	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
52885_facelift	52885	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
53148	53148	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
54518_prefl	54518	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
54518_facelift	54518	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
117778_prefl	117778	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
117778_facelift	117778	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
118827	118827	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
124763_prefl	124763	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
124763_facelift	124763	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
118826	118826	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	xDrive 未改变 E92 Coupe 外廓。	READY
35674	35674	Coupe	3 Series E36	E36/2	2	EU-BMW-3-E36-COUPE-01	HIGH		READY
15925	15925	Hatchback	3 Series E46	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH		READY
15456	15456	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-XDRIVE-01	HIGH	xi 四驱三厢外廓。	READY
15457	15457	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-XDRIVE-01	HIGH	xi 四驱旅行版抬高外廓。	READY
19101	19101	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	xDrive 未形成独立外廓。	READY
19104	19104	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	xDrive 未形成独立外廓。	READY
10503	10503	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
12140	12140	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
12470_prefl	12470	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
12470_facelift	12470	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
55124	55124	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
58077_prefl	58077	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
58077_facelift	58077	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
58079_prefl	58079	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
58079_facelift	58079	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
58797	58797	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
57294_prefl	57294	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
57294_facelift	57294	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
59402_prefl	59402	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
59402_facelift	59402	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
59801	59801	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	xDrive 未改变 F34 Gran Turismo 外廓。	READY
17206	17206	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
14926	14926	Convertible	3 Series E46	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-01	HIGH		READY
13874	13874	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
14185	14185	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
17351	17351	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
17353	17353	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18968	18968	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH		READY
18969	18969	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH		READY
55128_prefl	55128	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
55128_facelift	55128	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
58949_prefl	58949	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
58949_facelift	58949	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
100827	100827	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
117281_prefl	117281	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
117281_facelift	117281	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
117286_prefl	117286	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	改款前物理外廓。	READY
117286_facelift	117286	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	改款后物理外廓。	READY
117290	117290	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
124776_prefl	124776	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
124776_facelift	124776	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
124777_prefl	124777	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
124777_facelift	124777	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
117289_prefl	117289	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
117289_facelift	117289	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
59222_prefl	59222	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前 330d xDrive 外廓与 F30 标准三厢一致。	READY
59222_facelift	59222	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
59404_prefl	59404	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
59404_facelift	59404	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
100818	100818	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	xDrive 未改变 F34 Gran Turismo 外廓。	READY
117282_prefl	117282	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	改款前 330d xDrive 外廓与 F30 标准三厢一致。	READY
117282_facelift	117282	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
117291	117291	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	xDrive 未改变 F34 Gran Turismo 外廓。	READY
117341	117341	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	PHEV 未改变 F30 Sedan 外廓。	READY
14922	14922	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
14923	14923	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18451_prefl	18451	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
18451_facelift	18451	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
18760	18760	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH		READY
113407	113407	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
113444	113444	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
118548_prefl	118548	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
118548_facelift	118548	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
118553	118553	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
118622_prefl	118622	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
118622_facelift	118622	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
120265	120265	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
143242_prefl	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
143242_facelift	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
148049_prefl	148049	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-PREFL-01	MEDIUM	G21 改款前旅行版外廓。	READY
148049_facelift	148049	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	MEDIUM	同一 Ktype 经现行零件目录覆盖改款后旅行版。	READY
148051	148051	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	HIGH		READY
113408	113408	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
113445	113445	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
120266	120266	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	xDrive 未改变 F34 Gran Turismo 外廓。	READY
148050_prefl	148050	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	MEDIUM	G21 改款前 xDrive 旅行版外廓。	READY
148050_facelift	148050	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	MEDIUM	同一 Ktype 经现行零件目录覆盖改款后 xDrive 旅行版。	READY
148052	148052	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
14773	14773	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH	330xd Touring 外廓与标准 E46 Touring 一致。	READY
14774	14774	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-XDRIVE-01	HIGH	xd 四驱三厢外廓。	READY
17352	17352	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-XDRIVE-01	HIGH	xd 四驱三厢外廓。	READY
17354	17354	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH	330xd Touring 外廓与标准 E46 Touring 一致。	READY
19103	19103	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	xDrive 未形成独立外廓。	READY
19106_prefl	19106	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前 xDrive 旅行版外廓。	READY
19106_facelift	19106	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后 xDrive 旅行版外廓。	READY
14802	14802	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-XDRIVE-01	HIGH	xi 四驱三厢外廓。	READY
14803	14803	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-XDRIVE-01	HIGH	xi 四驱旅行版抬高外廓。	READY
14921	14921	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	MEDIUM	输入及零件目录标注 E46 Coupe 330 xi；未形成独立外廓。	READY
19102	19102	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	xDrive 未形成独立外廓。	READY
19105	19105	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	xDrive 未形成独立外廓。	READY
53089_prefl	53089	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
53089_facelift	53089	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
100708_prefl	100708	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH	改款前物理外廓。	READY
100708_facelift	100708	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH	改款后物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2001-2100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1698	1393	Automobile-Catalog 1997 BMW 323ti Compact	https://www.automobile-catalog.com/car/1997/270665/bmw_323ti_compact.html
EU-BMW-3-E46-COUPE-01	4488	1757	1369	CarsGuide 2000 BMW 328Ci dimensions; CarsGuide 2005 BMW 325Ci dimensions	https://www.carsguide.com.au/bmw/3-series/328ci/car-dimensions/2000; https://www.carsguide.com.au/bmw/3-series/325ci/car-dimensions/2005
EU-BMW-3-E46-CONVERTIBLE-01	4488	1757	1372	Automoli BMW 3 Series Convertible E46	https://www.automoli.com/us/vehicles/bmw/seria-3/3-series-convertible-e46-8368/
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384	BMW E93 ACEA technical data	https://tomic.ba/fs/cjenik/E93%20ACEA%20Technik%200307.pdf
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	BMW PressClub E93 LCI technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0080392FR/127660
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418	Automoli BMW 3 Series Touring E91 LCI	https://www.automoli.com/en/vehicles/bmw/seria-3/seria-3-touring-e91-lci-facelift-2008-4365/
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	BMW E92 ACEA technical data	https://www.tomic.ba/fs/cjenik/E92%20ACEA%20Technik%200307.pdf
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	BMW Media Information E92 LCI technical data	https://treffseiten.de/bmw/info/daten/daten_325i_330i_335i_coupe_10_03.pdf
EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	4824	1828	1508	Automoli BMW 3 Series Gran Turismo F34	https://www.automoli.com/en/vehicles/bmw/seria-3/seria-3-gran-turismo-f34-3971/
EU-BMW-3-F31-WAGON-RWD-PREFL-01	4624	1811	1429	BMW PressClub F31 335i Touring technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208682/Specifications_BMW_3_Series_Touring_335i_03_2013.pdf
EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	4633	1811	1429	BMW PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-F30-SEDAN-RWD-PREFL-01	4624	1811	1429	BMW PressClub F30 Sedan technical specifications; BMW PressClub F30 330d xDrive technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0123675EN/181126; https://www.press.bmwgroup.com/global/article/attachment/T0136739EN/209104
EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	4633	1811	1429	BMW PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-E46-SEDAN-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan E46 325i	https://www.auto-data.net/en/bmw-3-series-sedan-e46-325i-192hp-56642
EU-BMW-3-E46-TOURING-WAGON-01	4478	1739	1409	Automoli BMW 3 Series Touring E46; Encycarpedia BMW 330xd Touring E46	https://www.automoli.com/en/vehicles/bmw/seria-3/seria-3-touring-e46-2038/; https://www.encycarpedia.com/bmw/00-330xd-touring-estate
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421	BMW E90 ACEA technical data	https://www.tomic.ba/fs/cjenik/E90%20ACEA%20Technik%200307.pdf
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421	BMW PressClub E90 LCI technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0080392FR/127659
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418	BMW E91 ACEA technical data	https://tomic.ba/fs/cjenik/E91%20ACEA%20Technik%200307.pdf
EU-BMW-3-E36-COUPE-01	4433	1710	1366	Automoli BMW 3 Series Coupe E36	https://www.automoli.com/en/vehicles/bmw/seria-3/seria-3-coupe-e36-2043/
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408	Auto-Data BMW 3 Series Compact E46	https://www.auto-data.net/en/bmw-3-series-compact-e46-generation-2035
EU-BMW-3-E46-SEDAN-XDRIVE-01	4471	1739	1434	Auto-Data BMW E46 330xi Sedan; Auto-Data BMW E46 330xd Sedan	https://www.auto-data.net/en/bmw-3-series-sedan-e46-330xi-231hp-automatic-21147; https://www.auto-data.net/en/bmw-3-series-sedan-e46-330xd-184hp-9992
EU-BMW-3-E46-TOURING-WAGON-XDRIVE-01	4478	1739	1429	Auto-Data BMW 3 Series Touring E46 facelift 330xi	https://www.auto-data.net/en/bmw-3-series-touring-e46-facelift-2001-330xi-231hp-42595
EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	4624	1811	1434	BMW PressClub F30 320i/328i xDrive technical specifications	https://www.press.bmwgroup.com/slovak/article/attachment/T0134236SK/202168
EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	4633	1811	1434	BMW PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434	BMW PressClub F31 335i xDrive Touring technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208687/Specifications_BMW_3_Series_Touring_335i_xDrive_03_2013.pdf
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434	BMW PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-G21-WAGON-RWD-PREFL-01	4709	1827	1440	BMW PressClub G21 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0297109EN/432678/The_new_BMW_3_Series_Touring_Specifications.pdf
EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	4713	1827	1440	BMW PressClub G21 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620073
EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	4713	1827	1440	BMW PressClub G20 LCI technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0442604CS/616678
EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	4709	1827	1445	BMW PressClub G21 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0297109EN/432678/The_new_BMW_3_Series_Touring_Specifications.pdf
EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	4713	1827	1445	BMW PressClub G21 LCI technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620073
EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	4713	1827	1445	BMW PressClub G20 LCI technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0442604CS/616678
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2001-2100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0136739EN/209104 "https://www.press.bmwgroup.com/global/article/attachment/T0136739EN/209104"
[2]: https://www.auto-data.net/en/bmw-3-series-touring-e46-facelift-2001-330xi-231hp-42595 "https://www.auto-data.net/en/bmw-3-series-touring-e46-facelift-2001-330xi-231hp-42595"
[3]: https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620073 "https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620073"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2475 行）
- 累计尺寸组：dimension_groups_final.tsv（689 行）

