# 任务：left18448 第 2101-2200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0022__d5ee1dd9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2101-2200 行

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
left18448 第 2101-2200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2101-2200_ktype_dimension_mapping_final.tsv
- left18448_2101-2200_dimension_groups_final.tsv
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
EU-BMW-3-E46-SEDAN-XDRIVE-01	4471	1739	1434
EU-BMW-3-E46-TOURING-WAGON-01	4478	1739	1409
EU-BMW-3-E46-TOURING-WAGON-XDRIVE-01	4478	1739	1429
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
EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	4713	1827	1445
EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-PREFL-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	4713	1827	1445
EU-BMW-3-G21-WAGON-XDRIVE-PHEV-FACELIFT-01	4713	1827	1442
EU-BMW-3-G21-WAGON-XDRIVE-PHEV-PREFL-01	4709	1827	1442
EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	4709	1827	1445

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	3	335 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2014	-	100828
BMW	3	335 I	Stufenheck	Heckantrieb	Benzin	Nov 2011	Jul 2015	12471
BMW	3	335 I	Schrägheck	Heckantrieb	Benzin	Mar 2013	Jun 2016	58798
BMW	3	335 I	Kombi	Heckantrieb	Benzin	Mar 2013	Jun 2015	59221
BMW	3	335 I	Stufenheck	Heckantrieb	Benzin	Nov 2011	Jun 2013	107867
BMW	3	335 I	Stufenheck	Heckantrieb	Benzin	Jul 2013	Jul 2015	107869
BMW	3	335 I	Kombi	Heckantrieb	Benzin	Mar 2013	Jun 2013	107873
BMW	3	335 I	Kombi	Heckantrieb	Benzin	Jul 2013	Jun 2015	107875
BMW	3	335 I	Schrägheck	Heckantrieb	Benzin	Mar 2013	Mar 2014	107879
BMW	3	335 I	Schrägheck	Heckantrieb	Benzin	Apr 2014	Jun 2016	107883
BMW	3	335 I	Cabriolet	Heckantrieb	Benzin	May 2006	Oct 2013	121102
BMW	3	335 I	Stufenheck	Heckantrieb	Benzin	Mar 2006	Dec 2011	121918
BMW	3	335 I	Kombi	Heckantrieb	Benzin	Sep 2006	Jun 2012	122020
BMW	3	335 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Jul 2015	57295
BMW	3	335 I Xdrive	Kombi	Allrad	Benzin	Mar 2013	Jun 2015	59220
BMW	3	335 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2013	Jun 2016	59802
BMW	3	335 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Jun 2013	107868
BMW	3	335 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Jul 2015	107870
BMW	3	335 I Xdrive	Kombi	Allrad	Benzin	Mar 2013	Jun 2013	107874
BMW	3	335 I Xdrive	Kombi	Allrad	Benzin	Jul 2013	Jun 2015	107876
BMW	3	335 I Xdrive	Schrägheck	Allrad	Benzin	Mar 2013	Mar 2014	107881
BMW	3	335 I Xdrive	Schrägheck	Allrad	Benzin	Apr 2014	Jun 2016	107884
BMW	3	335 I Xdrive	Kombi	Allrad	Benzin	Sep 2008	Jun 2012	122021
BMW	3	340 I	Stufenheck	Heckantrieb	Benzin	Jul 2015	Oct 2018	113409
BMW	3	340 I	Kombi	Heckantrieb	Benzin	Jul 2015	Jun 2019	113446
BMW	3	340 I	Kombi	Heckantrieb	Benzin	Jul 2015	Jun 2019	117293
BMW	3	340 I	Stufenheck	Heckantrieb	Benzin	Jul 2015	Oct 2018	117345
BMW	3	340 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	-	120267
BMW	3	340 I	Schrägheck	Heckantrieb	Benzin	Jul 2016	-	126168
BMW	3	340 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2015	Oct 2018	113410
BMW	3	340 I Xdrive	Kombi	Allrad	Benzin	Jul 2015	Jun 2019	113447
BMW	3	340 I Xdrive	Kombi	Allrad	Benzin	Jul 2015	Jun 2019	117294
BMW	3	340 I Xdrive	Stufenheck	Allrad	Benzin	Jul 2015	Oct 2018	117344
BMW	3	340 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2016	-	120268
BMW	3	340 I Xdrive	Schrägheck	Allrad	Benzin	Jul 2016	-	126169
BMW	3	Activehybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2012	Jun 2015	57560
BMW	3	M 340 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	Nov 2020	-	142485
BMW	3	M 340 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	Nov 2020	-	142486
BMW	3	M 340 I Xdrive	Kombi	Allrad	Benzin/Elektro	Sep 2025	-	802380
BMW	3	M3	Coupe	Heckantrieb	Benzin	Jul 2000	May 2006	14776
BMW	3	M3	Cabriolet	Heckantrieb	Benzin	Mar 2001	Aug 2006	15635
BMW	3	M3	Stufenheck	Heckantrieb	Benzin	Mar 2014	Oct 2018	100819
BMW	3	M3 2.3	Cabriolet	Heckantrieb	Benzin	Jun 1988	Jun 1991	8884
BMW	3	M3 2.3	Cabriolet	Heckantrieb	Benzin	Jun 1988	Jul 1989	127095
BMW	3	M3 3.0	Stufenheck	Heckantrieb	Benzin	Oct 1994	Jul 1995	14602
BMW	3	M3 3.2	Stufenheck	Heckantrieb	Benzin	Oct 1995	Jan 1998	5112
BMW	3	M3 3.2	Coupe	Heckantrieb	Benzin	Oct 1995	Nov 1998	5113
BMW	3	M3 3.2	Cabriolet	Heckantrieb	Benzin	Mar 1996	Sep 1999	5114
BMW	3	M3 Competition	Stufenheck	Heckantrieb	Benzin	Mar 2016	Oct 2018	118192
BMW	3	M3 Competition Xdrive	Stufenheck	Allrad	Benzin	May 2021	-	143769
BMW	3	M3 Competition Xdrive	Kombi	Allrad	Benzin	Jul 2022	Jul 2024	148053
BMW	3	M3 Competition Xdrive	Kombi	Allrad	Benzin	Jul 2024	-	800064
BMW	3	M3 Competition Xdrive	Stufenheck	Allrad	Benzin	Jul 2024	-	800150
BMW	3	M3 CRT	Stufenheck	Heckantrieb	Benzin	Mar 2011	Dec 2011	117783
BMW	3	M3 CS Xdrive	Stufenheck	Allrad	Benzin	Mar 2023	-	152065
BMW	3	M3 CS Xdrive	Kombi	Allrad	Benzin	Mar 2025	-	801439
BMW	3	M3 CSL	Coupe	Heckantrieb	Benzin	May 2003	Dec 2003	17440
BMW	3	M3 GTS	Coupe	Heckantrieb	Benzin	Mar 2007	Jun 2013	54944
BMW	3	M340 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	Sep 2024	-	801263
BMW	4	3.0 CSL	Coupe	Heckantrieb	Benzin	Nov 2022	Feb 2023	154570
BMW	4	418 D	Coupe	Heckantrieb	Diesel	Mar 2014	Jun 2015	100842
BMW	4	418 D	Coupe	Heckantrieb	Diesel	Mar 2015	Oct 2017	110017
BMW	4	418 D	Coupe	Heckantrieb	Diesel	Jul 2015	Dec 2020	113458
BMW	4	418 D	Coupe	Heckantrieb	Diesel	Mar 2015	Oct 2017	116664
BMW	4	418 D	Coupe	Heckantrieb	Diesel	Mar 2014	Dec 2020	116677
BMW	4	418 I	Coupe	Heckantrieb	Benzin	Jul 2015	Dec 2020	115281
BMW	4	418 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	118964
BMW	4	420 D	Cabriolet	Heckantrieb	Diesel	Oct 2013	Jun 2015	58295
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Jul 2013	Feb 2015	59809
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Mar 2014	Feb 2015	100849
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Mar 2015	Jun 2020	110018
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Mar 2015	Dec 2020	110020
BMW	4	420 D	Cabriolet	Heckantrieb	Diesel	Oct 2013	Jun 2015	111116
BMW	4	420 D	Cabriolet	Heckantrieb	Diesel	Jul 2015	Jul 2020	113457
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Jul 2013	Jun 2020	116667
BMW	4	420 D	Cabriolet	Heckantrieb	Diesel	Nov 2013	Jul 2020	116672
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Mar 2014	Dec 2020	116673
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Jul 2013	Mar 2015	116778
BMW	4	420 D	Coupe	Heckantrieb	Diesel	Mar 2014	Feb 2015	116781
BMW	4	420 D	Cabriolet	Heckantrieb	Diesel	Jul 2015	Jul 2020	147604
BMW	4	420 D Mild-hybrid	Cabriolet	Heckantrieb	Diesel/Elektro	Nov 2020	-	142484
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	Jul 2021	-	144695
BMW	4	420 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	Jul 2021	-	144696
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Nov 2013	Feb 2015	53539
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Mar 2014	Feb 2015	100850
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Mar 2015	Jun 2020	110019
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Mar 2015	Dec 2020	110021
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Nov 2013	Jun 2020	116668
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Mar 2014	Dec 2020	116674
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Nov 2013	Mar 2015	116780
BMW	4	420 D Xdrive	Coupe	Allrad	Diesel	Mar 2014	Feb 2015	116782
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Nov 2013	Feb 2017	49226
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2014	Feb 2017	100851
BMW	4	420 I	Cabriolet	Heckantrieb	Benzin	Jul 2014	Feb 2016	105913
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Nov 2013	Feb 2017	116662
BMW	4	420 I	Cabriolet	Heckantrieb	Benzin	Jul 2014	Feb 2016	116670
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2014	Feb 2017	116675
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2016	May 2021	118954
BMW	4	420 I	Coupe	Heckantrieb	Benzin	Mar 2016	Jun 2020	118958
BMW	4	420 I	Cabriolet	Heckantrieb	Benzin	Mar 2016	Jul 2020	118960


--- Round 1 / 首次发送 ---
## 更新点

* 按缓存优先模式完成普通 BMW 3 系车型的第一轮关联。
* 复用 18 个既有尺寸组，本轮未重新抓取或重复输出其尺寸与来源。
* 对跨越 E9x 改款前后外廓的 3 个 Ktype 完成派生拆分：

  * `121102`：E93 Convertible pre-LCI / facelift
  * `121918`：E90 Sedan pre-LCI / facelift
  * `122020`：E91 Wagon pre-LCI / facelift
* `142486` 为 G20 改款前 M340i xDrive Sedan，但现有索引缺少对应尺寸组，暂不建立猜测性关联。
* M3 系列及 BMW 4 系留待按物理外廓集中建组。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：39
* READY 映射行：42
* PENDING Ktype：61
* 本轮复用既有尺寸组：18
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100828	100828	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
12471	12471	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
58798	58798	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
59221	59221	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107867	107867	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
107869	107869	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
107873	107873	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107875	107875	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107879	107879	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107883	107883	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
121102_prefl	121102	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	同一Ktype跨越E93改款前外廓。	READY
121102_facelift	121102	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	同一Ktype跨越E93改款后外廓。	READY
121918_prefl	121918	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	同一Ktype跨越E90改款前外廓。	READY
121918_facelift	121918	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越E90改款后外廓。	READY
122020_prefl	122020	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	同一Ktype跨越E91改款前外廓。	READY
122020_facelift	122020	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	同一Ktype跨越E91改款后外廓。	READY
57295	57295	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
59220	59220	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
59802	59802	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107868	107868	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
107870	107870	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
107874	107874	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
107876	107876	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
107881	107881	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107884	107884	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
122021	122021	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
113409	113409	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
113446	113446	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
117293	117293	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
117345	117345	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
120267	120267	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
126168	126168	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
113410	113410	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
113447	113447	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
117294	117294	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
117344	117344	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
120268	120268	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
126169	126169	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
57560	57560	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	ActiveHybrid 3不构成独立外廓。	READY
142485	142485	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	HIGH		READY
802380	802380	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
801263	801263	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无。本轮全部为既有尺寸组复用。

## 下一步优先处理

1. 核对并首次创建 `142486` 所需的 G20 改款前 xDrive Sedan 尺寸组。
2. 按 E30、E36、E46、E90/E92、F80、G80/G81 聚类处理 M3，并单独核对 CRT、CS、CSL、GTS、3.0 CSL 等特殊外部套件。
3. 按 F32 Coupe、F33 Convertible、G22 Coupe、G23 Convertible 聚类处理 BMW 4 系，同时区分改款前后及必要的 xDrive 高度差异。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2101-2200_ktype_dimension_mapping_final.tsv
- left18448_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 新建并闭合 10 个尺寸组：1 个 BMW 3 Series G20 xDrive pre-facelift 轿车组、3 个 M3/M3 Touring 组、6 个 BMW 4 Series 组。
* 关联并转为 READY 的新增 Ktype 共 49 个。
* BMW 4 Series 本轮已按 F32/F33/G22/G23 及 RWD/xDrive 外廓完成大部分映射。
* 仍待处理的主要是经典/特殊 M3 与 BMW 4 3.0 CSL 等少量未闭合车型。

当前批次进度

* READY 映射：88 / 100
* PENDING 映射：12 / 100
* 已确认并被当前批次引用的尺寸组：28
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142486	142486	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
100819	100819	Sedan	M3 F80	F80	4	EU-BMW-3-F80-M3-SEDAN-01	HIGH		READY
118192	118192	Sedan	M3 F80	F80	4	EU-BMW-3-F80-M3-SEDAN-01	HIGH	Competition未形成独立外廓。	READY
143769	143769	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	HIGH		READY
148053	148053	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	HIGH		READY
800064	800064	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	HIGH		READY
800150	800150	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	HIGH		READY
152065	152065	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	MEDIUM	CS外廓按G80 M3 Competition xDrive Sedan处理。	READY
801439	801439	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	MEDIUM	CS Touring外廓按G81 M3 Touring xDrive处理。	READY
100842	100842	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110017	110017	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
113458	113458	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116664	116664	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116677	116677	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
115281	115281	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118964	118964	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
58295	58295	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
59809	59809	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100849	100849	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110018	110018	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110020	110020	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
111116	111116	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
113457	113457	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116667	116667	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116672	116672	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116673	116673	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116778	116778	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116781	116781	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
147604	147604	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
142484	142484	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-CONVERTIBLE-01	HIGH		READY
144695	144695	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
144696	144696	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH		READY
53539	53539	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
100850	100850	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
110019	110019	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
110021	110021	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116668	116668	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116674	116674	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116780	116780	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116782	116782	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
49226	49226	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100851	100851	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
105913	105913	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116662	116662	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116670	116670	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116675	116675	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118954	118954	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	MEDIUM	按F32 Coupé外廓处理。	READY
118958	118958	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118960	118960	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1440	BMW 3 Series Sedan technical data	https://www.bmw.com/en/all-models/3-series/sedan/2018/bmw-3-series-sedan-technical-data.html
EU-BMW-3-F80-M3-SEDAN-01	4671	1877	1430	BMW M3 Sedan technical data	https://www.bmw.com/en/all-models/m-series/m3-sedan/2014/bmw-m3-sedan-technical-data.html
EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	4794	1903	1433	BMW M3 Sedan technical data	https://www.bmw.com/en/all-models/m-series/m3-sedan/2020/bmw-m3-sedan-technical-data.html
EU-BMW-3-G81-M3-TOURING-XDRIVE-01	4794	1903	1446	BMW M3 Touring technical data	https://www.bmw.com/en/all-models/m-series/m3-touring/2022/bmw-m3-touring-technical-data.html
EU-BMW-4-F32-COUPE-RWD-01	4638	1825	1362	BMW 4 Series Coupe technical data	https://www.bmw.com/en/all-models/4-series/coupe/2013/bmw-4-series-coupe-technical-data.html
EU-BMW-4-F32-COUPE-XDRIVE-01	4638	1825	1377	BMW 4 Series Coupe technical data	https://www.bmw.com/en/all-models/4-series/coupe/2013/bmw-4-series-coupe-technical-data.html
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384	BMW 4 Series Convertible technical data	https://www.bmw.com/en/all-models/4-series/convertible/2013/bmw-4-series-convertible-technical-data.html
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383	BMW 4 Series Coupe technical data	https://www.bmw.com/en/all-models/4-series/coupe/2020/bmw-4-series-coupe-technical-data.html
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1391	BMW 4 Series Coupe technical data	https://www.bmw.com/en/all-models/4-series/coupe/2020/bmw-4-series-coupe-technical-data.html
EU-BMW-4-G23-CONVERTIBLE-01	4768	1852	1384	BMW 4 Series Convertible technical data	https://www.bmw.com/en/all-models/4-series/convertible/2020/bmw-4-series-convertible-technical-data.html
```

下一步优先处理

1. 处理剩余 12 个 PENDING：`14776`、`15635`、`8884`、`127095`、`14602`、`5112`、`5113`、`5114`、`117783`、`17440`、`54944`、`154570`。
2. 先按经典/特殊 M3 聚类：E30 Cabriolet、E36 Sedan/Coupe/Cabriolet、E46 Coupe/Cabriolet/CSL、E90 CRT、E92 GTS。
3. 最后单独闭合 BMW 4 `154570`（3.0 CSL）并检查是否需要独立特殊外廓组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2101-2200_ktype_dimension_mapping_final.tsv
- left18448_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 闭合剩余经典及特殊 M3 中的 11 个 Ktype，新建 9 个尺寸组：

  * E30 M3 Convertible
  * E36 M3 Sedan、Coupe、Convertible
  * E46 M3 Coupe、Convertible、CSL
  * E90 M3 CRT
  * E92 M3 GTS
* E30、E36、E46 三代数据集中取自 BMW 官方 M3 历代技术规格；CRT 与 GTS 分别使用对应的 BMW 官方专项技术资料。
* `154570` 已确认是 2022 年限量 50 辆、采用专属宽体和空气动力学外廓的独立 BMW 3.0 CSL，但当前 BMW 官方发布资料未列出可直接落盘的完整长宽高，因此保持 PENDING，不猜测复用 M4 CSL 尺寸。([BMW Group PressClub][1])

当前批次进度

* READY Ktype：99 / 100
* PENDING Ktype：1 / 100
* READY 映射行：102
* 已确认并被当前批次引用的尺寸组：37
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14776	14776	Coupe	M3 E46	E46	2	EU-BMW-3-E46-M3-COUPE-01	HIGH		READY
15635	15635	Convertible	M3 E46	E46	2	EU-BMW-3-E46-M3-CONVERTIBLE-01	HIGH		READY
8884	8884	Convertible	M3 E30	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
127095	127095	Convertible	M3 E30	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
14602	14602	Sedan	M3 E36	E36	4	EU-BMW-3-E36-M3-SEDAN-01	HIGH		READY
5112	5112	Sedan	M3 E36	E36	4	EU-BMW-3-E36-M3-SEDAN-01	HIGH	3.2升版本未形成独立外廓。	READY
5113	5113	Coupe	M3 E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
5114	5114	Convertible	M3 E36	E36	2	EU-BMW-3-E36-M3-CONVERTIBLE-01	HIGH		READY
117783	117783	Sedan	M3 E90	E90	4	EU-BMW-3-E90-M3-CRT-SEDAN-01	HIGH	CRT专属外部配置。	READY
17440	17440	Coupe	M3 E46	E46	2	EU-BMW-3-E46-M3-CSL-COUPE-01	HIGH	CSL降低车身高度，独立尺寸组。	READY
54944	54944	Coupe	M3 E92	E92	2	EU-BMW-3-E92-M3-GTS-COUPE-01	HIGH	GTS专属空气动力学外廓。	READY
154570	154570	Coupe	3.0 CSL (2022)		2		MEDIUM	独立限量车型，具有专属宽体及空气动力学外廓。	PENDING: 尚缺可落盘的官方完整三维
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E46-M3-COUPE-01	4492	1780	1372	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E46-M3-CONVERTIBLE-01	4492	1780	1372	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-SEDAN-01	4433	1698	1365	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E90-M3-CRT-SEDAN-01	4614	1817	1416	BMW M3 CRT Official Technical Specifications	https://www.press.bmwgroup.com/middle-east/article/attachment/T0117882EN/171189
EU-BMW-3-E46-M3-CSL-COUPE-01	4492	1780	1365	BMW 25 Years M3 Official Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E92-M3-GTS-COUPE-01	4645	1804	1387	BMW M3 GTS Official Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0080423EN/120831
```

下一步优先处理

1. 仅处理 `154570`：查找 BMW 3.0 CSL 的官方 homologation、type-approval 或其他明确列出不含后视镜长宽高的原始技术记录。
2. 若获得完整三维，创建独立 3.0 CSL 尺寸组并立即进入最终机械收尾；不再重新核对本轮已闭合的 37 个尺寸组。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0405918EN/the-bmw-3-0-csl?language=en "The BMW 3.0 CSL."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2101-2200_ktype_dimension_mapping_final.tsv
- left18448_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 最后一个 PENDING Ktype `154570` 已闭合：建立独立尺寸组 `EU-BMW-4-3-0-CSL-COUPE-01`，三维为 `4794 × 1921 × 1386 mm`。BMW 官方资料确认该车为限量 50 辆的独立 3.0 CSL，规格来源提供完整外廓尺寸。([BMW Group PressClub][1])
* 机械收尾时将 `EU-BMW-4-G22-COUPE-XDRIVE-01` 高度修正为官方规格的 `1390 mm`。([BMW Group PressClub][2])
* 已完成固定表头、唯一主键、引用闭合、正整数三维、来源非空和指定下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：103
* 最终尺寸组：38
* 所有映射均为 `READY`，不存在孤立尺寸组或缺失引用。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100828	100828	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
12471	12471	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
58798	58798	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
59221	59221	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107867	107867	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
107869	107869	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH		READY
107873	107873	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107875	107875	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
107879	107879	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107883	107883	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
121102_prefl	121102	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	同一Ktype跨越E93改款前外廓。	READY
121102_facelift	121102	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	同一Ktype跨越E93改款后外廓。	READY
121918_prefl	121918	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	同一Ktype跨越E90改款前外廓。	READY
121918_facelift	121918	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越E90改款后外廓。	READY
122020_prefl	122020	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	同一Ktype跨越E91改款前外廓。	READY
122020_facelift	122020	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	同一Ktype跨越E91改款后外廓。	READY
57295	57295	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
59220	59220	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
59802	59802	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107868	107868	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
107870	107870	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
107874	107874	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
107876	107876	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
107881	107881	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
107884	107884	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
122021	122021	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
113409	113409	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
113446	113446	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
117293	117293	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
117345	117345	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
120267	120267	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
126168	126168	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
113410	113410	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
113447	113447	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
117294	117294	Wagon	3 Series F31	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
117344	117344	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
120268	120268	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
126169	126169	Hatchback	3 Series F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH	F34 Gran Turismo五门掀背外廓。	READY
57560	57560	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	ActiveHybrid 3不构成独立外廓。	READY
142485	142485	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	HIGH		READY
142486	142486	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
802380	802380	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	HIGH		READY
14776	14776	Coupe	M3 E46	E46	2	EU-BMW-3-E46-M3-COUPE-01	HIGH		READY
15635	15635	Convertible	M3 E46	E46	2	EU-BMW-3-E46-M3-CONVERTIBLE-01	HIGH		READY
100819	100819	Sedan	M3 F80	F80	4	EU-BMW-3-F80-M3-SEDAN-01	HIGH		READY
8884	8884	Convertible	M3 E30	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
127095	127095	Convertible	M3 E30	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
14602	14602	Sedan	M3 E36	E36	4	EU-BMW-3-E36-M3-SEDAN-01	HIGH		READY
5112	5112	Sedan	M3 E36	E36	4	EU-BMW-3-E36-M3-SEDAN-01	HIGH	3.2升版本未形成独立外廓。	READY
5113	5113	Coupe	M3 E36	E36	2	EU-BMW-3-E36-M3-COUPE-01	HIGH		READY
5114	5114	Convertible	M3 E36	E36	2	EU-BMW-3-E36-M3-CONVERTIBLE-01	HIGH		READY
118192	118192	Sedan	M3 F80	F80	4	EU-BMW-3-F80-M3-SEDAN-01	HIGH	Competition未形成独立外廓。	READY
143769	143769	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	HIGH		READY
148053	148053	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	HIGH		READY
800064	800064	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	HIGH		READY
800150	800150	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	HIGH		READY
117783	117783	Sedan	M3 E90	E90	4	EU-BMW-3-E90-M3-CRT-SEDAN-01	HIGH	CRT专属外部配置。	READY
152065	152065	Sedan	M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	MEDIUM	CS外廓按G80 M3 Competition xDrive Sedan处理。	READY
801439	801439	Wagon	M3 G81	G81	5	EU-BMW-3-G81-M3-TOURING-XDRIVE-01	MEDIUM	CS Touring外廓按G81 M3 Touring xDrive处理。	READY
17440	17440	Coupe	M3 E46	E46	2	EU-BMW-3-E46-M3-CSL-COUPE-01	HIGH	CSL降低车身高度，独立尺寸组。	READY
54944	54944	Coupe	M3 E92	E92	2	EU-BMW-3-E92-M3-GTS-COUPE-01	HIGH	GTS专属空气动力学外廓。	READY
801263	801263	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
154570	154570	Coupe	3.0 CSL (2022)		2	EU-BMW-4-3-0-CSL-COUPE-01	MEDIUM	限量50辆的独立宽体及空气动力学外廓。	READY
100842	100842	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110017	110017	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
113458	113458	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116664	116664	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116677	116677	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
115281	115281	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118964	118964	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
58295	58295	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
59809	59809	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100849	100849	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110018	110018	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
110020	110020	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
111116	111116	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
113457	113457	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116667	116667	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116672	116672	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116673	116673	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116778	116778	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116781	116781	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
147604	147604	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
142484	142484	Convertible	4 Series G23	G23	2	EU-BMW-4-G23-CONVERTIBLE-01	HIGH		READY
144695	144695	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH		READY
144696	144696	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH		READY
53539	53539	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
100850	100850	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
110019	110019	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
110021	110021	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116668	116668	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116674	116674	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116780	116780	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
116782	116782	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-XDRIVE-01	HIGH		READY
49226	49226	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
100851	100851	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
105913	105913	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116662	116662	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
116670	116670	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
116675	116675	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118954	118954	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	MEDIUM	按F32 Coupé外廓处理。	READY
118958	118958	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-RWD-01	HIGH		READY
118960	118960	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2101-2200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	4824	1828	1508	BMW Group PressClub F34 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0222722EN/specifications-bmw-3-series-gran-turismo-valid-from-03/14?language=en
EU-BMW-3-F30-SEDAN-RWD-PREFL-01	4624	1811	1429	BMW Group PressClub F30 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0136739EN/specifications-of-the-bmw-3-series-sedan-valid-from-march-2013?language=en
EU-BMW-3-F31-WAGON-RWD-PREFL-01	4624	1811	1429	BMW Group PressClub F31 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208689/Specifications_BMW_3_Series_Touring_330d_xDrive_03_2013.pdf
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384	BMW Group PressClub E93 international press kit	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0019146EN_GB/international-presskit%3A-the-new-bmw-3-series-convertible?language=en_GB
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	BMW Group PressClub E9x Coupe and Cabriolet specifications	https://www.press.bmwgroup.com/usa/article/detail/T0018038EN_US/the-new-3-series?language=en_US
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421	BMW Group PressClub E90/E91 historical technical specifications	https://www.press.bmwgroup.com/usa/article/detail/T0018038EN_US/the-new-3-series?language=en_US
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421	BMW Canada 2010 3 Series technical specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0037175EN/105888
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418	BMW Group PressClub E90/E91 historical technical specifications	https://www.press.bmwgroup.com/usa/article/detail/T0018038EN_US/the-new-3-series?language=en_US
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418	BMW Canada 2010 3 Series technical specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0037175EN/105888
EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	4624	1811	1434	BMW Group PressClub F30 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0136739EN/specifications-of-the-bmw-3-series-sedan-valid-from-march-2013?language=en
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434	BMW Group PressClub F31 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208689/Specifications_BMW_3_Series_Touring_330d_xDrive_03_2013.pdf
EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	4633	1811	1429	BMW Group PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0234765EN/specifications-bmw-3-series-sedan-and-bmw-3-series-touring-valid-from-may-2015?language=en
EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	4633	1811	1429	BMW Group PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0234765EN/specifications-bmw-3-series-sedan-and-bmw-3-series-touring-valid-from-may-2015?language=en
EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	4633	1811	1434	BMW Group PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0234765EN/specifications-bmw-3-series-sedan-and-bmw-3-series-touring-valid-from-may-2015?language=en
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434	BMW Group PressClub F30/F31 LCI technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0234765EN/specifications-bmw-3-series-sedan-and-bmw-3-series-touring-valid-from-may-2015?language=en
EU-BMW-3-G21-WAGON-XDRIVE-PREFL-01	4709	1827	1445	BMW Group PressClub G21 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0305733EN/446340
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1440	BMW Group PressClub G20 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0305731EN/specifications-of-the-new-bmw-3-series-sedan-320d-and-the-new-bmw-3-series-sedan-320d-xdrive-valid-from-03/2020?language=en
EU-BMW-3-G21-WAGON-XDRIVE-FACELIFT-01	4713	1827	1445	BMW Group PressClub G20/G21 facelift technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0442333EN/the-new-bmw-3-series-sedan-the-new-bmw-3-series-touring?language=en
EU-BMW-3-E46-M3-COUPE-01	4492	1780	1372	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E46-M3-CONVERTIBLE-01	4492	1780	1372	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-F80-M3-SEDAN-01	4671	1877	1430	BMW Group PressClub F80 M3 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0179962EN/specifications-of-the-new-bmw-m3-sedan-and-the-new-bmw-m4-coupe-valid-from-03/2014?language=en
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-SEDAN-01	4433	1698	1365	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-G80-M3-SEDAN-XDRIVE-01	4794	1903	1433	BMW Group PressClub G80 M3 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0316649EN/476823
EU-BMW-3-G81-M3-TOURING-XDRIVE-01	4794	1903	1446	BMW Group PressClub G81 M3 Touring technical specifications	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0401213EN_GB/the-new-bmw-m3-competition-touring-with-m-xdrive-%E2%80%93-the-first-ever-bmw-m3-touring?language=en_GB
EU-BMW-3-E90-M3-CRT-SEDAN-01	4614	1817	1416	BMW M3 CRT official technical specifications	https://www.press.bmwgroup.com/middle-east/article/attachment/T0117882EN/171189
EU-BMW-3-E46-M3-CSL-COUPE-01	4492	1780	1365	BMW 25 Years M3 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082320IT/125300
EU-BMW-3-E92-M3-GTS-COUPE-01	4645	1804	1387	BMW M3 GTS official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0080423EN/120831
EU-BMW-3-G20-SEDAN-XDRIVE-FACELIFT-01	4713	1827	1445	BMW Group PressClub G20/G21 facelift technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0442333EN/the-new-bmw-3-series-sedan-the-new-bmw-3-series-touring?language=en
EU-BMW-4-3-0-CSL-COUPE-01	4794	1921	1386	UltimateSpecs BMW CSL 3.0 dimensions; BMW Group PressClub 3.0 CSL model boundary	https://www.ultimatespecs.com/car-specs/BMW/138093/BMW-CSL-30.html;https://www.press.bmwgroup.com/global/article/detail/T0405918EN/the-bmw-3-0-csl?language=en
EU-BMW-4-F32-COUPE-RWD-01	4638	1825	1362	BMW Group PressClub F32 Coupe technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384	BMW Group PressClub F33 Convertible technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0149105EN/the-new-bmw-4-series-convertible?language=en
EU-BMW-4-G23-CONVERTIBLE-01	4768	1852	1384	BMW Group PressClub G23 Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0317628EN/472045
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383	BMW Group PressClub G22 Coupe technical specifications	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group PressClub G22 Coupe technical specifications	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-F32-COUPE-XDRIVE-01	4638	1825	1377	BMW Group PressClub F32 Coupe technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0142634EN/256334
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2101-2200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0405918EN/the-bmw-3-0-csl?language=en&utm_source=chatgpt.com "The BMW 3.0 CSL."
[2]: https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837?utm_source=chatgpt.com "Technical specifications."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2578 行）
- 累计尺寸组：dimension_groups_final.tsv（709 行）

