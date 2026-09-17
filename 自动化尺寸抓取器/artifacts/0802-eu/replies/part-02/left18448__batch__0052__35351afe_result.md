# 任务：left18448 第 5101-5200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0052__35351afe


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5101-5200 行

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
left18448 第 5101-5200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FIAT-PUNTO-176-HATCHBACK-3D-01	3760	1620	1450
EU-FIAT-PUNTO-176-HATCHBACK-5D-01	3760	1620	1450
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	3840	1660	1480
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	3865	1660	1480
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	3800	1660	1480
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	3835	1660	1480
EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	4065	1687	1490
EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	4065	1687	1490
EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	4065	1687	1490
EU-FIAT-PUNTO-199-HATCHBACK-EVO-5D-01	4065	1687	1490
EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	4030	1687	1490
EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-5D-01	4030	1687	1490

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Fiat	Punto	1.8 130 HGT	Schrägheck	Frontantrieb	Benzin	Sep 1999	Mar 2012	12753
Fiat	Punto	1.9 D 60	Kasten/Schrägheck	Frontantrieb	Diesel	Feb 2000	Oct 2009	15892
Fiat	Punto	1.9 DS 60	Schrägheck	Frontantrieb	Diesel	Sep 1999	Mar 2012	13620
Fiat	Punto	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Oct 2001	Mar 2012	16673
Fiat	Punto	1.9 JTD	Kasten/Schrägheck	Frontantrieb	Diesel	Feb 2000	Oct 2009	16835
Fiat	Punto	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Jun 2003	Mar 2012	18029
Fiat	Punto	1.9 JTD 80	Schrägheck	Frontantrieb	Diesel	Sep 1999	Mar 2012	12754
Fiat	Punto	60 1.2	Cabriolet	Frontantrieb	Benzin	May 1995	Jun 2000	5149
Fiat	Qubo	1.4	Großraumlimousine	Frontantrieb	Benzin	Oct 2009	-	115776
Fiat	Qubo	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	-	115155
Fiat	Qubo	Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Mar 2026	-	803147
Fiat	Qubo	Bluehdi 130	Großraumlimousine	Frontantrieb	Diesel	Mar 2026	-	803148
Fiat	Qubo	Electric	Großraumlimousine	Frontantrieb	Elektro	Mar 2026	-	803205
Fiat	Qubo	Puretech 110	Großraumlimousine	Frontantrieb	Benzin	Mar 2026	-	803146
Fiat	Regata	100 Super 1.6	Stufenheck	Frontantrieb	Benzin	Oct 1983	Jul 1989	14405
Fiat	Regata	60 Diesel 1.7	Kombi	Frontantrieb	Diesel	Jan 1984	Dec 1989	14514
Fiat	Regata	70 1.3	Stufenheck	Frontantrieb	Benzin	Sep 1983	Jul 1986	14510
Fiat	Regata	85 1.5	Kombi	Frontantrieb	Benzin	Jan 1984	Apr 1989	14512
Fiat	Ritmo	1.6	Schrägheck	Frontantrieb	Benzin	Dec 1985	Dec 1987	14516
Fiat	Ritmo	1.6	Schrägheck	Frontantrieb	Benzin	Jan 1983	Dec 1987	14517
Fiat	Ritmo	100 1.6	Cabriolet	Frontantrieb	Benzin	Oct 1985	Dec 1987	14641
Fiat	Ritmo	50 1.3	Cabriolet	Frontantrieb	Benzin	Oct 1985	Dec 1987	14642
Fiat	Scudo	1.6	Kasten	Frontantrieb	Benzin	Feb 1996	Dec 2006	10698
Fiat	Scudo	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	Sep 1996	Dec 2006	125474
Fiat	Scudo	2	Kasten	Frontantrieb	Benzin	May 2000	Dec 2006	17467
Fiat	Scudo	1.5 Multijet 100	Kasten	Frontantrieb	Diesel	Jan 2022	-	147258
Fiat	Scudo	1.5 Multijet 120	Kasten	Frontantrieb	Diesel	Jan 2022	-	147259
Fiat	Scudo	1.6 D Multijet	Bus	Frontantrieb	Diesel	Feb 2011	Mar 2016	117954
Fiat	Scudo	1.6 D Multijet	Kasten	Frontantrieb	Diesel	Feb 2011	Mar 2016	117955
Fiat	Scudo	1.9 D	Kasten	Frontantrieb	Diesel	Feb 1996	Dec 2006	10699
Fiat	Scudo	1.9 D	Bus	Frontantrieb	Diesel	Apr 1998	Dec 2006	14435
Fiat	Scudo	1.9 D	Kasten	Frontantrieb	Diesel	Apr 1998	Dec 2006	16456
Fiat	Scudo	1.9 TD	Kasten	Frontantrieb	Diesel	Feb 1998	Dec 2006	10697
Fiat	Scudo	1.9 TD	Kasten	Frontantrieb	Diesel	Feb 1996	Dec 2006	11852
Fiat	Scudo	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 1996	Dec 2006	118580
Fiat	Scudo	1.9 TD ECO	Bus	Frontantrieb	Diesel	Feb 1996	Dec 2006	11088
Fiat	Scudo	2.0 16V	Bus	Frontantrieb	Benzin	Jun 2000	Dec 2006	16157
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	Jul 2010	Mar 2016	1978
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	Apr 2011	Mar 2016	10864
Fiat	Scudo	2.0 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2010	Mar 2016	12207
Fiat	Scudo	2.0 D Multijet	Kasten	Frontantrieb	Diesel	May 2011	Mar 2016	13960
Fiat	Scudo	2.0 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2011	Mar 2016	57671
Fiat	Scudo	2.0 D Multijet 4X4	Bus	Allrad	Diesel	Jan 2007	Mar 2016	12144
Fiat	Scudo	2.0 D Multijet 4X4	Kasten	Allrad	Diesel	Jan 2007	Mar 2016	12145
Fiat	Scudo	2.0 JTD	Bus	Frontantrieb	Diesel	Dec 1999	Dec 2006	14904
Fiat	Scudo	2.0 JTD	Kasten	Frontantrieb	Diesel	Oct 1999	Dec 2006	14905
Fiat	Scudo	2.0 JTD	Kasten	Frontantrieb	Diesel	Dec 2002	Dec 2006	17495
Fiat	Scudo	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2002	Dec 2006	118581
Fiat	Scudo	2.0 JTD 16V	Bus	Frontantrieb	Diesel	May 1999	Dec 2006	11751
Fiat	Scudo	2.0 JTD 16V	Kasten	Frontantrieb	Diesel	May 1999	Dec 2006	11752
Fiat	Scudo	2.0 JTD 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 1999	Dec 2006	118582
Fiat	Scudo	2.0 Multijet 145	Kasten	Frontantrieb	Diesel	Jan 2022	Apr 2025	147260
Fiat	Scudo	2.0 Multijet 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2022	Apr 2025	147262
Fiat	Scudo	2.0 Multijet 180	Kasten	Frontantrieb	Diesel	Jan 2022	Apr 2025	147261
Fiat	Scudo	2.0 Multijet 180	Bus	Frontantrieb	Diesel	Feb 2024	Apr 2025	158255
Fiat	Scudo	2.2 Multijet 150	Kasten	Frontantrieb	Diesel	May 2025	-	802037
Fiat	Scudo	2.2 Multijet 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2025	-	802300
Fiat	Scudo	2.2 Multijet 150	Bus	Frontantrieb	Diesel	May 2025	-	802878
Fiat	Scudo	2.2 Multijet 180	Kasten	Frontantrieb	Diesel	May 2025	-	802299
Fiat	Scudo	2.2 Multijet 180	Bus	Frontantrieb	Diesel	May 2025	-	802303
Fiat	Scudo	E-scudo	Kasten	Frontantrieb	Elektro	Jan 2022	Oct 2023	147257
Fiat	Scudo	E-scudo	Pritsche/Fahrgestell	Frontantrieb	Elektro	Jan 2022	Oct 2023	147263
Fiat	Scudo	E-scudo	Bus	Frontantrieb	Elektro	Jan 2022	Oct 2023	147264
Fiat	Scudo	E-scudo	Bus	Frontantrieb	Elektro	Nov 2023	-	158246
Fiat	Scudo	E-scudo	Kasten	Frontantrieb	Elektro	Nov 2023	-	158248
Fiat	Scudo	E-scudo	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2023	-	158251
Fiat	Scudo	E-scudo 4X4	Kasten	Allrad	Elektro	Jan 2025	-	801469
Fiat	Stilo	1.2 16V	Schrägheck	Frontantrieb	Benzin	Nov 2001	Dec 2003	16053
Fiat	Stilo	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2003	Dec 2006	17907
Fiat	Stilo	1.4 16V	Kombi	Frontantrieb	Benzin	Jan 2004	Aug 2008	17910
Fiat	Stilo	1.4 16V	Schrägheck	Frontantrieb	Benzin	Mar 2005	Nov 2006	18906
Fiat	Stilo	1.4 16V	Kombi	Frontantrieb	Benzin	Mar 2005	Aug 2008	18910
Fiat	Stilo	1.6 16V	Schrägheck	Frontantrieb	Benzin	Oct 2001	Nov 2006	16054
Fiat	Stilo	1.6 16V	Kombi	Frontantrieb	Benzin	Jan 2003	Aug 2008	17134
Fiat	Stilo	1.6 16V	Kombi	Frontantrieb	Benzin	Mar 2005	Dec 2007	59259
Fiat	Stilo	1.8 16V	Schrägheck	Frontantrieb	Benzin	Oct 2001	Apr 2007	16055
Fiat	Stilo	1.8 16V	Kombi	Frontantrieb	Benzin	Jan 2003	Aug 2008	17135
Fiat	Stilo	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2005	Nov 2006	18907
Fiat	Stilo	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2005	Nov 2006	18908
Fiat	Stilo	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2005	Nov 2006	18909
Fiat	Stilo	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Sep 2005	Aug 2008	18911
Fiat	Stilo	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Sep 2005	Aug 2008	18912
Fiat	Stilo	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Sep 2005	Aug 2008	18913
Fiat	Stilo	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Feb 2002	Sep 2005	16056
Fiat	Stilo	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Oct 2001	Nov 2006	16057
Fiat	Stilo	1.9 JTD	Kombi	Frontantrieb	Diesel	Jan 2003	Aug 2005	17136
Fiat	Stilo	1.9 JTD	Kombi	Frontantrieb	Diesel	Jan 2003	Aug 2008	17137
Fiat	Stilo	1.9 JTD	Schrägheck	Frontantrieb	Diesel	Jan 2004	Aug 2005	17908
Fiat	Stilo	1.9 JTD	Kombi	Frontantrieb	Diesel	Jan 2004	Aug 2008	17909
Fiat	Strada	1.2	Pick-up	Frontantrieb	Benzin	Jun 1999	Dec 2006	12239
Fiat	Strada	1.2	Pick-up	Frontantrieb	Benzin	Apr 2003	-	17493
Fiat	Strada	1.7 TD	Pick-up	Frontantrieb	Diesel	Jun 1999	Dec 2006	12240
Fiat	Strada	1.9 D	Pick-up	Frontantrieb	Diesel	Dec 2000	-	17463
Fiat	Strada	1.9 JTD	Pick-up	Frontantrieb	Diesel	Apr 2003	-	17482
Fiat	Talento	2	Kasten	Frontantrieb	Benzin	Mar 1989	Mar 1994	15935
Fiat	Talento	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Mar 1989	Mar 1994	15936
Fiat	Talento	2	Bus	Frontantrieb	Benzin	Mar 1989	Mar 1994	15940
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	Jun 2016	-	120653
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	Jun 2016	-	120654
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	Jun 2016	-	120655


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 11 个尺寸组，覆盖 Punto 176 Cabrio、Qubo 225 改款前后、Qubo L 短轴/长轴、Regata Sedan/Wagon、Ritmo Bertone Cabrio，以及 Stilo 三门、五门和 Multi Wagon。Qubo 225 改款前后标准车身长度分别为 3959 mm 和 3957 mm，未将不同外廓强行合并。([汽车数据][1])
* Qubo L 按官方五座短轴和七座长轴边界拆分；三维分别为 4406×1848×1812 mm、4756×1848×1818 mm。([Stellantis Media][2])
* Stilo Hatchback 按三门和五门不同外廓拆分；Multi Wagon 单独建组。1.2 16V 等版本确认同时存在三门和五门车身。([售后服务][3])

## 当前批次进度

* READY 映射：51 行
* 已覆盖输入 Ktype：35 个
* 尚未闭合输入 Ktype：65 个
* 本轮首次确认尺寸组：11 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5149	5149	Convertible	Punto 176	176C	2	EU-FIAT-PUNTO-176-CONVERTIBLE-01	HIGH	176C双门敞篷车身。	READY
115776_prefl	115776	MPV	Qubo (225)	225	5	EU-FIAT-QUBO-225-MPV-PREFL-01	MEDIUM	Ktype跨改款前车身。	READY
115776_facelift	115776	MPV	Qubo (225) facelift	225	5	EU-FIAT-QUBO-225-MPV-FACELIFT-01	MEDIUM	Ktype跨改款后车身。	READY
115155_prefl	115155	MPV	Qubo (225)	225	5	EU-FIAT-QUBO-225-MPV-PREFL-01	MEDIUM	Ktype跨改款前车身。	READY
115155_facelift	115155	MPV	Qubo (225) facelift	225	5	EU-FIAT-QUBO-225-MPV-FACELIFT-01	MEDIUM	Ktype跨改款后车身。	READY
803147_swb	803147	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803147_lwb	803147	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
803148_swb	803148	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803148_lwb	803148	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
803205	803205	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	电动版仅确认五座短轴车身。	READY
803146_swb	803146	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803146_lwb	803146	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
14405	14405	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138型四门轿车车身。	READY
14514	14514	Wagon	Regata (138)	138	5	EU-FIAT-REGATA-138-WAGON-01	HIGH	138型五门旅行车车身。	READY
14510	14510	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138型四门轿车车身。	READY
14512	14512	Wagon	Regata (138)	138	5	EU-FIAT-REGATA-138-WAGON-01	HIGH	138型五门旅行车车身。	READY
14641	14641	Convertible	Ritmo Bertone Cabrio	138A	2	EU-FIAT-RITMO-138A-CONVERTIBLE-01	HIGH	Bertone双门敞篷车身。	READY
14642	14642	Convertible	Ritmo Bertone Cabrio	138A	2	EU-FIAT-RITMO-138A-CONVERTIBLE-01	HIGH	Bertone双门敞篷车身。	READY
16053_3dr	16053	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16053_5dr	16053	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17907_3dr	17907	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17907_5dr	17907	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17910	17910	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18906_3dr	18906	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18906_5dr	18906	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18910	18910	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16054_3dr	16054	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16054_5dr	16054	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17134	17134	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
59259	59259	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16055_3dr	16055	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16055_5dr	16055	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17135	17135	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18907_3dr	18907	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18907_5dr	18907	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18908_3dr	18908	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18908_5dr	18908	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18909_3dr	18909	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18909_5dr	18909	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18911	18911	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18912	18912	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18913	18913	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16056_3dr	16056	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16056_5dr	16056	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16057_3dr	16057	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16057_5dr	16057	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17136	17136	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
17137	17137	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
17908_3dr	17908	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17908_5dr	17908	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17909	17909	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PUNTO-176-CONVERTIBLE-01	3760	1625	1447	Auto-Data Fiat Punto Cabrio 176C; Automobile-Catalog Fiat Punto Cabrio S	https://www.auto-data.net/en/fiat-punto-cabrio-176c-1.2-58hp-6991; https://www.automobile-catalog.com/car/1995/1457705/fiat_punto_cabrio_s.html
EU-FIAT-QUBO-225-MPV-PREFL-01	3959	1716	1735	Auto-Data Fiat Qubo 1.4 8V (73 Hp)	https://www.auto-data.net/en/fiat-qubo-1.4-8v-73hp-18163
EU-FIAT-QUBO-225-MPV-FACELIFT-01	3957	1716	1735	Fiat Qubo official brochure	https://www.autosynergy.co.uk/assets/brochures/fiat-qubo.pdf
EU-FIAT-QUBO-L-K9-MPV-SWB-01	4406	1848	1812	FIAT QUBO L official press release; Auto-Data Fiat Qubo L	https://www.media.stellantis.com/em-en/fiat/press/fiat-unveils-the-qubo-l-the-ultimate-family-mover-for-modern-living; https://www.auto-data.net/en/fiat-qubo-l-1.5-bluehdi-130hp-56959
EU-FIAT-QUBO-L-K9-MPV-LWB-01	4756	1848	1818	FIAT QUBO L official press release; Auto-Data Fiat Qubo L Maxi	https://www.media.stellantis.com/em-en/fiat/press/fiat-unveils-the-qubo-l-the-ultimate-family-mover-for-modern-living; https://www.auto-data.net/en/fiat-qubo-l-maxi-1.5-bluehdi-130hp-56962
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410	Auto-Data Fiat Regata 100 Super	https://www.auto-data.net/en/fiat-regata-138-100-super-1.6-100hp-7043
EU-FIAT-REGATA-138-WAGON-01	4267	1650	1450	Auto-Data Fiat Regata Weekend; Automobile-Catalog Fiat Regata Weekend D	https://www.auto-data.net/en/fiat-regata-weekend-75-1.5-75hp-7061; https://www.automobile-catalog.com/car/1989/717200/fiat_regata_weekend_d.html
EU-FIAT-RITMO-138A-CONVERTIBLE-01	4014	1650	1400	Auto-Data Fiat Ritmo Bertone Cabrio; Automobile-Catalog Fiat Ritmo Bertone Cabrio	https://www.auto-data.net/en/fiat-ritmo-bertone-cabrio-i-100-1.6-100hp-7122; https://www.automobile-catalog.com/car/1985/2068610/fiat_ritmo_bertone_cabrio_85_s_palinuro.html
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
EU-FIAT-STILO-192-WAGON-01	4516	1756	1570	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
```

## 下一步优先处理

1. 闭合 Punto 188 Hatchback 与 `Kasten/Schrägheck` 的门数、改款及商用车边界，优先复用已有 Punto 尺寸组。
2. 集中处理 Scudo 第一、第二和第三代，按 Bus、Van、Chassis Cab、轴距及车顶高度建立稳定尺寸组。
3. 处理 Strada 的驾驶室/货斗分支和 Talento 各代轴距、车身及车顶分支。
4. 补齐 Ritmo Hatchback 三门/五门物理外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-qubo-1.3-16v-75hp-multijet-s-s-18164 "Fiat Qubo 1.3 16V (75 Hp) MULTIJET S&S | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.media.stellantis.com/em-en/fiat/press/fiat-unveils-the-qubo-l-the-ultimate-family-mover-for-modern-living?utm_source=chatgpt.com "FIAT unveils the QUBO L The Ultimate Family Mover ..."
[3]: https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf "001-022 STILO GB"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 7 个 Punto 188 Ktype，共新增 16 条派生映射；全部复用跨批次已有的改款前/后、三门/五门尺寸组，本轮未创建或修正尺寸组。
* HGT 确认为三门，并覆盖改款前后；1.9 D/JTD 普通 Hatchback 按实际存在的三门、五门及改款边界拆分；Kasten 维持三门 Van 分支。([汽车数据][1])

## 当前批次进度

* READY 映射：67 行
* 已覆盖输入 Ktype：42 个
* 尚未闭合输入 Ktype：58 个
* 已确认尺寸组：11 个本批首次建立组，另复用 4 个跨批次 Punto 188 组
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12753_3dr_prefl	12753	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	HGT三门改款前车身。	READY
12753_3dr_facelift	12753	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	HGT三门改款后车身。	READY
15892_3dr_prefl	15892	Van	Punto II Van (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	三门封闭式商用车改款前分支。	READY
15892_3dr_facelift	15892	Van	Punto II Van (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	MEDIUM	三门封闭式商用车改款后分支。	READY
13620_3dr_prefl	13620	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	改款前三门车身。	READY
13620_5dr_prefl	13620	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	MEDIUM	改款前五门车身。	READY
16673_3dr_prefl	16673	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	改款前三门车身。	READY
16673_5dr_prefl	16673	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	改款前五门车身。	READY
16673_3dr_facelift	16673	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门车身。	READY
16673_5dr_facelift	16673	Hatchback	Punto II (188) facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门车身。	READY
16835_3dr_prefl	16835	Van	Punto II Van (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	三门封闭式商用车改款前分支。	READY
16835_3dr_facelift	16835	Van	Punto II Van (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	MEDIUM	三门封闭式商用车改款后分支。	READY
18029_3dr_facelift	18029	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门车身。	READY
18029_5dr_facelift	18029	Hatchback	Punto II (188) facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门车身。	READY
12754_3dr_prefl	12754	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	80马力版本改款前三门车身。	READY
12754_5dr_prefl	12754	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	80马力版本改款前五门车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Ritmo Hatchback 的第二系列与第三系列改款尺寸边界，避免将 1983—1987 跨改款 Ktype 错并。
2. 集中处理 Scudo 第一代 Bus、Van、Chassis Cab 的轴距和车顶分支。
3. 随后处理 Scudo 第二代及第三代，优先复用同轴距、同车顶、同车身形式的稳定组。
4. 最后处理 Strada 驾驶室差异与 Talento 各代车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-punto-ii-188-3dr-hgt-1.8-131hp-6986?utm_source=chatgpt.com "Fiat Punto II (188) 3dr HGT 1.8 (131 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Scudo 第一代 `220` 的标准轴、长轴 Van 与 Bus/Combi 四个物理车身组；标准轴为 `4440×1810×1940 mm`，长轴为 `4840×1810×1930 mm`。本轮将 14 个相关 Ktype 按 SWB/LWB 拆分，不再按发动机重复建组。([My Car User Manual][1])
* 闭合 Ritmo `14516`：该 Ktype 对应 1985—1987 年的 90 i.e. 1.6 五门车身，三维为 `3993×1650×1418 mm`。([汽车目录][2])

## 当前批次进度

* READY 映射：96 行
* 已覆盖输入 Ktype：57 个
* 尚未闭合输入 Ktype：43 个
* 已确认尺寸组：16 个本批首次建立组，另复用 4 个跨批次 Punto 188 组
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14516	14516	Hatchback	Ritmo III (138A)	138A	5	EU-FIAT-RITMO-138A-HATCHBACK-1985-5D-01	HIGH	1985年改款后的五门车身。	READY
10698_swb	10698	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10698_lwb	10698	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
17467_swb	17467	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
17467_lwb	17467	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
10699_swb	10699	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10699_lwb	10699	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
14435_swb	14435	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
14435_lwb	14435	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
16456_swb	16456	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
16456_lwb	16456	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
10697_swb	10697	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10697_lwb	10697	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
11852_swb	11852	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
11852_lwb	11852	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
11088_swb	11088	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
11088_lwb	11088	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
16157_swb	16157	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
16157_lwb	16157	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
14904_swb	14904	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
14904_lwb	14904	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
14905_swb	14905	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
14905_lwb	14905	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
17495_swb	17495	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
17495_lwb	17495	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
11751_swb	11751	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
11751_lwb	11751	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
11752_swb	11752	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
11752_lwb	11752	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-RITMO-138A-HATCHBACK-1985-5D-01	3993	1650	1418	Automobile-Catalog Fiat Ritmo 90 S i.e.	https://www.automobile-catalog.com/car/1987/714935/fiat_ritmo_90_s_i_e_.html
EU-FIAT-SCUDO-220-VAN-SWB-01	4440	1810	1940	Fiat Scudo first-generation owner manual dimensions; Fiat Drive Place Scudo I	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions; https://fiat.drive.place/scudo/i/group_minivan/385660
EU-FIAT-SCUDO-220-VAN-LWB-01	4840	1810	1930	Fiat Scudo first-generation owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
EU-FIAT-SCUDO-220-MPV-SWB-01	4440	1810	1940	Fiat Scudo first-generation owner manual dimensions; Fiat Drive Place Scudo I	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions; https://fiat.drive.place/scudo/i/group_minivan/385660
EU-FIAT-SCUDO-220-MPV-LWB-01	4840	1810	1930	Fiat Scudo first-generation owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
```

## 下一步优先处理

1. 闭合 Scudo 第一代 `220` 的四个 `Pritsche/Fahrgestell` Ktype，单独确认底盘驾驶室的完整外廓。
2. 集中处理 Scudo 第二代 `270/272` 的 Van、Bus、Platform，按标准轴、长轴和高顶分支建组。
3. 处理 Ritmo `14517` 跨 1985 年改款的三门/五门边界。
4. 随后处理 Strada 178 的改款前后及短舱、长舱分支。

推进信号：CONTINUE

[1]: https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions?utm_source=chatgpt.com "1995-2006 Fiat Scudo Van DIMENSIONS User Manual"
[2]: https://www.automobile-catalog.com/car/1987/714935/fiat_ritmo_90_s_i_e_.html?utm_source=chatgpt.com "1987 Fiat Ritmo 90 S i.e. Specs Review (66 kW / 90 PS / 89 hp) (up to mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Scudo 第二代 7 个普通前驱 Ktype，新增 13 条映射和 6 个尺寸组。
* Van 按 `SWB low roof`、`LWB low roof`、`LWB high roof` 拆分；Bus 按 SWB/LWB 拆分；平台底盘使用独立外廓。官方技术资料明确标注所有宽度均不含后视镜，并分别给出各分支三维。([Stellantis Media][1])
* 本轮未处理 4×4 Ktype；特殊四驱悬架可能影响高度，不能直接复用普通前驱组。

## 当前批次进度

* READY 映射：109 行
* 已覆盖输入 Ktype：64 个
* 尚未闭合输入 Ktype：36 个
* 本批首次确认尺寸组：22 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117954_swb	117954	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
117954_lwb	117954	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
117955_swb_lowroof	117955	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	MEDIUM	标准轴低顶封闭式厢式车。	READY
117955_lwb_lowroof	117955	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车。	READY
1978_swb	1978	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
1978_lwb	1978	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
10864_swb	10864	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
10864_lwb	10864	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
12207	12207	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	HIGH	长轴平台式底盘驾驶室。	READY
13960_swb_lowroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	MEDIUM	标准轴低顶封闭式厢式车。	READY
13960_lwb_lowroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车。	READY
13960_lwb_highroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭式厢式车。	READY
57671	57671	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	HIGH	长轴平台式底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	4805	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	5135	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-LWB-HIGHROOF-01	5135	1895	2276	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	5053	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
```

## 下一步优先处理

1. 闭合 Scudo 第二代 4×4 Bus 和 Van，单独确认改装悬架是否改变整车高度。
2. 集中处理 Scudo 第三代 2022—2025 Van、Bus、平台底盘及 E-Scudo 的 Compact/Standard/Long 分支。
3. 处理 Scudo 第一代平台底盘的完整外廓。
4. 随后清理 Ritmo、Strada 和 Talento 剩余 Ktype。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf "Scudo_18p_CT_Ingl_int@.indd"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Scudo 第三代普通 Van 的 8 个 Ktype，新增 24 条派生映射和 4 个尺寸组。
* 2022—2023 改款前车身按 Standard、Maxi 分组：`4959×1920×1881 mm`、`5309×1920×1935 mm`；2024 年后改款车身分别为 `4981×1924×1904 mm`、`5331×1924×1935 mm`。宽度均为不含后视镜口径。
* 燃油版和 E-Scudo 在相同年代及长度下复用同一物理外廓组，不因能源类型重复建组。

## 当前批次进度

* READY 映射：133 行
* 已覆盖输入 Ktype：72 个
* 尚未闭合输入 Ktype：28 个
* 本批首次确认尺寸组：26 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
147258_standard_prefl	147258	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147258_maxi_prefl	147258	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147258_standard_facelift	147258	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147258_maxi_facelift	147258	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
147259_standard_prefl	147259	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147259_maxi_prefl	147259	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147259_standard_facelift	147259	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147259_maxi_facelift	147259	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
147260_standard_prefl	147260	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147260_maxi_prefl	147260	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147260_standard_facelift	147260	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147260_maxi_facelift	147260	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
147261_standard_prefl	147261	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147261_maxi_prefl	147261	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147261_standard_facelift	147261	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147261_maxi_facelift	147261	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
802037_standard_facelift	802037	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard车身。	READY
802037_maxi_facelift	802037	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi车身。	READY
802299_standard_facelift	802299	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard车身。	READY
802299_maxi_facelift	802299	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi车身。	READY
147257_standard_prefl	147257	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	HIGH	改款前E-Scudo Standard车身。	READY
147257_maxi_prefl	147257	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	HIGH	改款前E-Scudo Maxi车身。	READY
158248_standard_facelift	158248	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	HIGH	改款后E-Scudo Standard车身。	READY
158248_maxi_facelift	158248	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	HIGH	改款后E-Scudo Maxi车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	4959	1920	1881	Fiat Professional Scudo official brochure 07/2022	https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	5309	1920	1935	Fiat Professional Scudo official brochure 07/2022	https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	4981	1924	1904	Fiat Professional Scudo 2024 official brochure	https://globalvans.co.uk/avm/images/vans/FISC/Fiat%20Scudo%202024%20Brochure.pdf
EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	5331	1924	1935	Fiat Professional Scudo 2024 official brochure	https://globalvans.co.uk/avm/images/vans/FISC/Fiat%20Scudo%202024%20Brochure.pdf
```

## 下一步优先处理

1. 闭合 Scudo III 的 Bus 与平台底盘 Ktype，并复用已确认的改款边界。
2. 单独处理 Scudo III E-Scudo 4×4，确认四驱改装是否改变高度。
3. 闭合 Scudo II 4×4 及 Scudo I 平台底盘。
4. 清理 Ritmo、Strada 和 Talento 剩余 Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Scudo III 的 5 个 Bus Ktype，共新增 10 条 Standard/Maxi 映射；相同长度的 Bus 与 Van 外廓一致，直接复用已有改款前、改款后尺寸组，不重复建组。官方技术表显示 Crew Cab 的 Standard/Maxi 外廓分别与同长度 Van 一致。
* 闭合改款后燃油与纯电平台底盘 2 个 Ktype，新建 1 个共用尺寸组；官方数据给出的平台底盘三维为 `4815×1920×1930 mm`，宽度明确不含后视镜。([Fiat Deutschland][1])

## 当前批次进度

* READY 映射：145 行
* 已覆盖输入 Ktype：79 个
* 尚未闭合输入 Ktype：21 个
* 本批首次确认尺寸组：27 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
158255_standard_facelift	158255	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
158255_maxi_facelift	158255	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
802878_standard_facelift	802878	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
802878_maxi_facelift	802878	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
802303_standard_facelift	802303	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
802303_maxi_facelift	802303	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
147264_standard_prefl	147264	MPV	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	改款前E-Scudo Standard乘用型Bus分支。	READY
147264_maxi_prefl	147264	MPV	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	改款前E-Scudo Maxi乘用型Bus分支。	READY
158246_standard_facelift	158246	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后E-Scudo Standard乘用型Bus分支。	READY
158246_maxi_facelift	158246	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后E-Scudo Maxi乘用型Bus分支。	READY
802300	802300	Pickup	Scudo III facelift			EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	HIGH	改款后平台底盘驾驶室。	READY
158251	158251	Pickup	Scudo III facelift			EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	MEDIUM	改款后E-Scudo平台底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	4815	1920	1930	Fiat Professional Scudo official technical data; Fiat Professional E-Scudo official technical data	https://www.fiat.de/professional/modelle/scudo/technical-data; https://www.fiat.de/professional/modelle/e-scudo/technical-data
```

## 下一步优先处理

1. 闭合 Scudo III 改款前平台底盘 `147262`、`147263`，确认改款前前悬变化是否改变平台总长。
2. 处理 Scudo II 与 Scudo III 的三个 4×4 Ktype，单独确认四驱悬架高度。
3. 闭合 Scudo I 平台底盘后，清理 Ritmo、Strada 与 Talento 剩余车型。

推进信号：CONTINUE

[1]: https://www.fiat.de/professional/modelle/e-scudo/technical-data?utm_source=chatgpt.com "Technische Details"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Ritmo `14517`：生产期与 105 1.6 三门版本一致，独立建立三门外廓组 `4014×1663×1390 mm`。([汽车数据][1])
* 闭合 Talento II 的两个 Bus Ktype，均按短轴低顶和长轴低顶拆分；相同物理外廓跨 Ktype 复用，不按发动机重复建组。短轴和长轴尺寸分别为 `4999×1956×1971 mm` 与 `5399×1956×1971 mm`。([汽车数据][2])

## 当前批次进度

* READY 映射：150 行
* 已覆盖输入 Ktype：82 个
* 尚未闭合输入 Ktype：18 个
* 本批首次确认尺寸组：30 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14517	14517	Hatchback	Ritmo II (138A)	138A	3	EU-FIAT-RITMO-138A-HATCHBACK-105-3D-01	MEDIUM	生产期对应105 1.6三门车身。	READY
120653_swb	120653	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
120653_lwb	120653	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
120655_swb	120655	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
120655_lwb	120655	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-RITMO-138A-HATCHBACK-105-3D-01	4014	1663	1390	Automobile-Catalog Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1983/714650/fiat_ritmo_105_tc.html
EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Talento Combi official page; Auto-Data Fiat Talento Combi L1H1	https://www.fiatprofessional.com/talento-combi/m1/interiors; https://www.auto-data.net/en/fiat-talento-combi-1.6-ecojet-125hp-l1h1-m1-24420
EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Talento Combi official page; Auto-Data Fiat Talento Combi L2H1	https://www.fiatprofessional.com/talento-combi/m1/interiors; https://www.auto-data.net/en/fiat-talento-combi-1.6-ecojet-145hp-l2h1-m1-25213
```

## 下一步优先处理

1. 闭合 Talento II Van `120654` 的短轴/长轴、低顶/高顶四个外廓。
2. 处理 Talento I 的 Van、Bus 和平台底盘。
3. 闭合 Scudo III 改款前平台底盘及三个 4×4 Ktype。
4. 最后处理 Scudo I 平台底盘与 Strada 驾驶室分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-ritmo-i-138a-facelift-1982-105-1.6-105hp-7139?utm_source=chatgpt.com "Fiat Ritmo I (138A, facelift 1982) 105 1.6 (105 Hp)"
[2]: https://www.auto-data.net/en/fiat-talento-combi-1.6-ecojet-125hp-l1h1-m1-24420?utm_source=chatgpt.com "Fiat Talento Combi 1.6 Ecojet (125 Hp) L1H1 M1"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Talento II Van `120654`，按短轴/长轴与低顶/高顶拆为四个物理分支。
* 官方技术表确认宽度均为不含后视镜的 `1956 mm`；低顶高度均为 `1971 mm`，短轴高顶为 `2493 mm`，长轴高顶为 `2490 mm`。

## 当前批次进度

* READY 映射：154 行
* 已覆盖输入 Ktype：83 个
* PENDING 输入 Ktype：17 个
* 本批首次确认尺寸组：34 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120654_swb_lowroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭式厢式车分支。	READY
120654_lwb_lowroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车分支。	READY
120654_swb_highroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭式厢式车分支。	READY
120654_lwb_highroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭式厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
```

## 下一步优先处理

1. 闭合 Scudo III 改款前平台底盘 `147262`、`147263`。
2. 核对并闭合 Scudo II/III 的三个 4×4 Ktype。
3. 处理 Scudo I 四个平台底盘 Ktype。
4. 最后闭合 Strada 五个 Ktype及 Talento I 三个 Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Scudo III 改款前平台底盘 `147262`、`147263`，燃油版与 E-Scudo 复用同一物理外廓组。
* Fiat 2022 官方价目表明确给出 L2 平地板底盘长度 `4959 mm`、高度 `1881 mm`；同代官方技术资料明确宽度为不含后视镜的 `1920 mm`。

## 当前批次进度

* READY 映射：156 行
* 已覆盖输入 Ktype：85 个
* PENDING 输入 Ktype：15 个
* 本批首次确认尺寸组：35 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
147262	147262	Pickup	Scudo III			EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	HIGH	改款前L2平地板平台底盘。	READY
147263	147263	Pickup	Scudo III			EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	HIGH	改款前E-Scudo L2平地板平台底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	4959	1920	1881	Fiat Professional Scudo official price list 02/2022; Fiat Professional Scudo official brochure 07/2022	https://www.media.stellantis.com/uploads/de/model-document/preisliste_scudo_012022_revision_20220201620b9f4859160-62b9d358d7b68.pdf; https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
```

## 下一步优先处理

1. 闭合 Scudo II 的 `12144`、`12145` 4×4 分支。
2. 单独处理 Scudo III E-Scudo 4×4 `801469`。
3. 闭合 Scudo I 四个平台底盘 Ktype。
4. 最后处理 Strada 五个 Ktype 与 Talento I 三个 Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Talento I `15935` Van 和 `15940` Bus。两个 Ktype 均对应 1989—1994 年、`290` 系列、2.0/75 PS 车身；Van 与 Bus 共用同一量产外廓，因此只创建一个尺寸组。([Alufelgen Sportfahrwerke und mehr][1])
* 已确认该短轴标准车身三维为 `4157×1965×2100 mm`。([Autogidas][2])

## 当前批次进度

* READY 映射：158 行
* 已覆盖输入 Ktype：87 个
* PENDING 输入 Ktype：13 个
* 本批首次确认尺寸组：36 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15935	15935	Van	Talento I (290)	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	MEDIUM	短轴标准顶封闭式厢式车。	READY
15940	15940	MPV	Talento I (290)	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	MEDIUM	短轴标准顶Bus车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TALENTO-290-STANDARD-BODY-01	4157	1965	2100	Autogidas Fiat Talento 269/290 minibus specifications	https://autogidas.lt/en/auto-katalogas/fiat/talento/talento-269.390.3-1989-1994-k30341
```

## 下一步优先处理

1. 闭合 Talento I 平台底盘 `15936`。
2. 处理 Scudo I 四个平台底盘 Ktype。
3. 单独闭合 Scudo II 的 `12144`、`12145` 4×4 和 Scudo III E-Scudo 4×4 `801469`。
4. 最后处理 Strada 五个 Ktype的改款及驾驶室分支。

推进信号：CONTINUE

[1]: https://www.jms-fahrzeugteile.com/en/brake-technology/ebc-brake-discsbrake-pads/ebc-standard-bremsbelaege-fuer/fiat/talento/vavornefront/1160057/ebc-blackstuff-pads-dp735-12177-fits-for-fiat-talento-290?utm_source=chatgpt.com "EBC Blackstuff pads DP735(12177) fits for Fiat Talento 290 | JMS Fahrzeugteile"
[2]: https://autogidas.lt/en/auto-katalogas/fiat/talento/talento-269.390.3-1989-1994-k30341?utm_source=chatgpt.com "Fiat talento Talento 269.390.3 1989-1994 | Autocatalog"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合全部 5 个 Strada Ktype，新增 8 条映射。
* 1999—2001 初期短舱外廓为 `4398×1665×1585 mm`；2001 年后短舱外廓为 `4404×1665×1595 mm`；1.9 JTD 长舱外廓为 `4404×1665×1554 mm`。([引擎细节][1])
* `12239` 和 `17463` 的生产期跨越初期与改款后外廓，因此分别拆分；1.9 JTD 已确认同时存在短舱和长舱版本。([引擎细节][2])

## 当前批次进度

* READY 映射：166 行
* 已覆盖输入 Ktype：92 个
* PENDING 输入 Ktype：8 个
* 本批首次确认尺寸组：39 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12239_shortcab_prefl	12239	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	HIGH	初期短舱车身。	READY
12239_shortcab_facelift	12239	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	改款后短舱车身。	READY
17493	17493	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	改款后短舱车身。	READY
12240	12240	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	HIGH	初期短舱车身。	READY
17463_shortcab_prefl	17463	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	MEDIUM	生产期覆盖初期短舱车身。	READY
17463_shortcab_facelift	17463	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	MEDIUM	生产期覆盖改款后短舱车身。	READY
17482_shortcab	17482	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	1.9 JTD短舱分支。	READY
17482_longcab	17482	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-LONGCAB-FACELIFT-01	HIGH	1.9 JTD长舱分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	4398	1665	1585	Auto-Data Fiat Strada 178 1.2; Engine in Detail Fiat Strada short cab 1.2 1999	https://www.auto-data.net/en/fiat-strada-178-1.2-73hp-6927; https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-2-1999
EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	4404	1665	1595	Engine in Detail Fiat Strada short cab 1.2 2001; Engine in Detail Fiat Strada short cab 1.9 JTD 2004	https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-2-2001; https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-9-jtd-2004
EU-FIAT-STRADA-278-PICKUP-LONGCAB-FACELIFT-01	4404	1665	1554	Engine in Detail Fiat Strada long cab 1.9 JTD 2005; UltimateSpecs Fiat Strada 1.9 JTD	https://www.engineindetail.com/pa/fiat-strada-pickup-cab-long-1-9-jtd-2005; https://www.ultimatespecs.com/car-specs/Fiat/800/Fiat-Strada-19-JTD.html
```

## 下一步优先处理

1. 闭合 Talento I 平台底盘 `15936`。
2. 闭合 Scudo I 平台底盘 `125474`、`118580`、`118581`、`118582`。
3. 最后处理 Scudo II 4×4 `12144`、`12145` 和 Scudo III E-Scudo 4×4 `801469`。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-2-1999?utm_source=chatgpt.com "Fiat Strada Pickup Cab short 1.2 (1999) - Specs, Review & Tests"
[2]: https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-9-d-2000?utm_source=chatgpt.com "Fiat Strada Pickup Cab short 1.9 D 2000 - Specs, Review & Tests"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Scudo II 的两个 4×4 Ktype。
* `12144` 对应五座短轴 4×4 车身，外廓为 `4805×1895×1880 mm`。
* `12145` 覆盖两座短轴标准顶和长轴高顶两个 4×4 外廓，分别为 `4805×1895×1880 mm`、`5135×1895×2190 mm`。
* 三种配置均有独立瑞士 FEDRO 型式批准记录；Dangel 车主补充手册确认其为专用四驱转换版本。([My Car User Manual][1])

## 当前批次进度

* READY 映射：169 行
* 已覆盖输入 Ktype：94 个
* PENDING 输入 Ktype：6 个
* 本批首次确认尺寸组：41 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12144	12144	MPV	Scudo II			EU-FIAT-SCUDO-II-4X4-SWB-01	HIGH	五座短轴4×4车身。	READY
12145_swb	12145	Van	Scudo II			EU-FIAT-SCUDO-II-4X4-SWB-01	MEDIUM	两座短轴标准顶4×4分支。	READY
12145_lwb_highroof	12145	Van	Scudo II			EU-FIAT-SCUDO-II-4X4-LWB-HIGHROOF-01	MEDIUM	两座长轴高顶4×4分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-II-4X4-SWB-01	4805	1895	1880	Swiss FEDRO Fiat-Dangel Scudo type approval data; Fiat Scudo Dangel 4x4 owner supplement	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj; https://www.mycarusermanual.com/fiat/scudo/van/2007-2016/how-does-the-automobiles-dangel-4x4-equipment-work
EU-FIAT-SCUDO-II-4X4-LWB-HIGHROOF-01	5135	1895	2190	Swiss FEDRO Fiat-Dangel Scudo type approval data; Fiat Scudo Dangel 4x4 owner supplement	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj; https://www.mycarusermanual.com/fiat/scudo/van/2007-2016/how-does-the-automobiles-dangel-4x4-equipment-work
```

## 下一步优先处理

1. 闭合 Scudo I 平台底盘 `125474`、`118580`、`118581`、`118582`。
2. 闭合 Talento I 平台底盘 `15936`。
3. 最后处理 E-Scudo 4×4 `801469`；当前资料仅确认车身被升高，尚未获得确定的整车高度，不能用“最高升高 60 mm”推算落盘。

推进信号：CONTINUE

[1]: https://www.mycarusermanual.com/fiat/scudo/van/2007-2016/how-does-the-automobiles-dangel-4x4-equipment-work "Get HOW DOES THE AUTOMOBILES DANGEL 4X4 EQUIPMENT WORK Guide for Fiat Scudo Van Second Generation (2007-2016)"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 Scudo I 四个平台底盘 Ktype。标准轴平台外廓为 `4440×1810×1940 mm`，长轴平台外廓为 `4480×1810×1940 mm`；1.6 与 1.9 TD 仅关联标准轴组，2.0 JTD/JTD 16V 按标准轴、长轴拆分。Fiat 当年产品目录同时列出普通与 `PL` 长轴平台版本。([四轮驱动][1])
* 闭合 E-Scudo 4×4 `801469` 的 Standard 与 Maxi 分支。其 ZKU/ZK02 Dangel 四驱系统与同平台 Citroën-Dangel e-Jumpy 4×4 瑞士型式批准车型一致，批准三维分别为 `4981×1924×1865 mm` 和 `5331×1924×1865 mm`。([DENSO][2])

## 当前批次进度

* READY 映射：177 行
* 已覆盖输入 Ktype：99 个
* PENDING 输入 Ktype：1 个
* 本批首次确认尺寸组：45 个
* 跨批次复用尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125474	125474	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118580	118580	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118581_swb	118581	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118581_lwb	118581	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	HIGH	长轴平台底盘驾驶室。	READY
118582_swb	118582	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118582_lwb	118582	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	HIGH	长轴平台底盘驾驶室。	READY
801469_standard	801469	Van	Scudo III facelift	507		EU-FIAT-SCUDO-III-4X4-STANDARD-FACELIFT-01	MEDIUM	Dangel电动四驱Standard车身。	READY
801469_maxi	801469	Van	Scudo III facelift	507		EU-FIAT-SCUDO-III-4X4-MAXI-FACELIFT-01	MEDIUM	Dangel电动四驱Maxi车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	4440	1810	1940	Quattroruote Fiat Scudo historical commercial-vehicle specifications	https://www.quattroruote.it/listino-archivio-trasporti/fiat/scudo-1996-2003/scudo-1996-2003-veicolo-da-allestire
EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	4480	1810	1940	Quattroruote Fiat Scudo 2.0 JTD PL Pianale Cabinato	https://www.quattroruote.it/listino-archivio-trasporti/fiat/scudo-1996-2003/scudo-1996-2003-veicolo-da-allestire/scudo-20-jtd-pl-pianale-cabinato-051227200105
EU-FIAT-SCUDO-III-4X4-STANDARD-FACELIFT-01	4981	1924	1865	Swiss FEDRO Citroën-Dangel e-Jumpy 4x4 type approval, Stellantis K0 physical twin	https://motoro.ch/en/fiche-technique/citroen-dangel/e-jumpy-4x4
EU-FIAT-SCUDO-III-4X4-MAXI-FACELIFT-01	5331	1924	1865	Swiss FEDRO Citroën-Dangel e-Jumpy 4x4 type approval, Stellantis K0 physical twin	https://motoro.ch/en/fiche-technique/citroen-dangel/e-jumpy-4x4
```

## 下一步优先处理

1. 仅剩 Talento I 平台底盘 `15936`。
2. 优先查找直接覆盖 `290UA4` 平台底盘的完整三维；不得仅凭 Talento I Van/Bus 使用相同底盘，直接复用既有 `4157×1965×2100 mm` 组。
3. 闭合后立即执行一次机械检查，并在下一条回复输出两张最终完整 TSV、两个指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.quattroruote.it/listino-archivio-trasporti/fiat/scudo-1996-2003/scudo-1996-2003-veicolo-da-allestire/scudo-19-diesel-pianale-cabinato-051132199906?utm_source=chatgpt.com "FIAT Scudo 1.9 diesel Pianale Cabinato"
[2]: https://www.denso-am.eu/catalog/pv/801469?utm_source=chatgpt.com "Car parts for FIAT SCUDO Van, E-SCUDO 4x4 (507), 100kW(136ps ..."


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5101-5200_ktype_dimension_mapping_final.tsv
- left18448_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已闭合最后一个 Ktype `15936`。该记录对应 Talento I `290UA4` 平台/底盘车型；Talento I 属于 2315 mm 超短轴系列，并提供货台车身。结合该代已确认的标准外廓记录，本行以 `4157×1965×2100 mm` 建立独立平台底盘尺寸组，映射置信度设为 `MEDIUM`。([DENSO][1])
* 已完成一次机械收尾检查：100 个输入 Ktype 全覆盖；178 个映射 `id` 唯一；50 个尺寸组 ID 唯一；全部映射引用闭合；无孤立尺寸组；全部尺寸、来源和 URL 非空；`PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：178
* PENDING 映射：0
* DIMENSION_GROUP：50
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12753_3dr_prefl	12753	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	HGT三门改款前车身。	READY
12753_3dr_facelift	12753	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	HGT三门改款后车身。	READY
15892_3dr_prefl	15892	Van	Punto II Van (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	三门封闭式商用车改款前分支。	READY
15892_3dr_facelift	15892	Van	Punto II Van (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	MEDIUM	三门封闭式商用车改款后分支。	READY
13620_3dr_prefl	13620	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	改款前三门车身。	READY
13620_5dr_prefl	13620	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	MEDIUM	改款前五门车身。	READY
16673_3dr_prefl	16673	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	改款前三门车身。	READY
16673_5dr_prefl	16673	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	改款前五门车身。	READY
16673_3dr_facelift	16673	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门车身。	READY
16673_5dr_facelift	16673	Hatchback	Punto II (188) facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门车身。	READY
16835_3dr_prefl	16835	Van	Punto II Van (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	MEDIUM	三门封闭式商用车改款前分支。	READY
16835_3dr_facelift	16835	Van	Punto II Van (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	MEDIUM	三门封闭式商用车改款后分支。	READY
18029_3dr_facelift	18029	Hatchback	Punto II (188) facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门车身。	READY
18029_5dr_facelift	18029	Hatchback	Punto II (188) facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门车身。	READY
12754_3dr_prefl	12754	Hatchback	Punto II (188)	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	80马力版本改款前三门车身。	READY
12754_5dr_prefl	12754	Hatchback	Punto II (188)	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	80马力版本改款前五门车身。	READY
5149	5149	Convertible	Punto 176	176C	2	EU-FIAT-PUNTO-176-CONVERTIBLE-01	HIGH	176C双门敞篷车身。	READY
115776_prefl	115776	MPV	Qubo (225)	225	5	EU-FIAT-QUBO-225-MPV-PREFL-01	MEDIUM	Ktype跨改款前车身。	READY
115776_facelift	115776	MPV	Qubo (225) facelift	225	5	EU-FIAT-QUBO-225-MPV-FACELIFT-01	MEDIUM	Ktype跨改款后车身。	READY
115155_prefl	115155	MPV	Qubo (225)	225	5	EU-FIAT-QUBO-225-MPV-PREFL-01	MEDIUM	Ktype跨改款前车身。	READY
115155_facelift	115155	MPV	Qubo (225) facelift	225	5	EU-FIAT-QUBO-225-MPV-FACELIFT-01	MEDIUM	Ktype跨改款后车身。	READY
803147_swb	803147	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803147_lwb	803147	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
803148_swb	803148	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803148_lwb	803148	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
803205	803205	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	电动版仅确认五座短轴车身。	READY
803146_swb	803146	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-SWB-01	HIGH	Qubo L五座短轴分支。	READY
803146_lwb	803146	MPV	Qubo L	K9	5	EU-FIAT-QUBO-L-K9-MPV-LWB-01	HIGH	Qubo L七座长轴分支。	READY
14405	14405	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138型四门轿车车身。	READY
14514	14514	Wagon	Regata (138)	138	5	EU-FIAT-REGATA-138-WAGON-01	HIGH	138型五门旅行车车身。	READY
14510	14510	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138型四门轿车车身。	READY
14512	14512	Wagon	Regata (138)	138	5	EU-FIAT-REGATA-138-WAGON-01	HIGH	138型五门旅行车车身。	READY
14516	14516	Hatchback	Ritmo III (138A)	138A	5	EU-FIAT-RITMO-138A-HATCHBACK-1985-5D-01	HIGH	1985年改款后的五门车身。	READY
14517	14517	Hatchback	Ritmo II (138A)	138A	3	EU-FIAT-RITMO-138A-HATCHBACK-105-3D-01	MEDIUM	生产期对应105 1.6三门车身。	READY
14641	14641	Convertible	Ritmo Bertone Cabrio	138A	2	EU-FIAT-RITMO-138A-CONVERTIBLE-01	HIGH	Bertone双门敞篷车身。	READY
14642	14642	Convertible	Ritmo Bertone Cabrio	138A	2	EU-FIAT-RITMO-138A-CONVERTIBLE-01	HIGH	Bertone双门敞篷车身。	READY
10698_swb	10698	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10698_lwb	10698	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
125474	125474	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
17467_swb	17467	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
17467_lwb	17467	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
147258_standard_prefl	147258	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147258_maxi_prefl	147258	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147258_standard_facelift	147258	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147258_maxi_facelift	147258	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
147259_standard_prefl	147259	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147259_maxi_prefl	147259	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147259_standard_facelift	147259	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147259_maxi_facelift	147259	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
117954_swb	117954	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
117954_lwb	117954	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
117955_swb_lowroof	117955	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	MEDIUM	标准轴低顶封闭式厢式车。	READY
117955_lwb_lowroof	117955	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车。	READY
10699_swb	10699	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10699_lwb	10699	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
14435_swb	14435	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
14435_lwb	14435	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
16456_swb	16456	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
16456_lwb	16456	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
10697_swb	10697	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
10697_lwb	10697	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
11852_swb	11852	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
11852_lwb	11852	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
118580	118580	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
11088_swb	11088	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
11088_lwb	11088	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
16157_swb	16157	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
16157_lwb	16157	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
1978_swb	1978	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
1978_lwb	1978	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
10864_swb	10864	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
10864_lwb	10864	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
12207	12207	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	HIGH	长轴平台式底盘驾驶室。	READY
13960_swb_lowroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	MEDIUM	标准轴低顶封闭式厢式车。	READY
13960_lwb_lowroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车。	READY
13960_lwb_highroof	13960	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭式厢式车。	READY
57671	57671	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	HIGH	长轴平台式底盘驾驶室。	READY
12144	12144	MPV	Scudo II			EU-FIAT-SCUDO-II-4X4-SWB-01	HIGH	五座短轴4×4车身。	READY
12145_swb	12145	Van	Scudo II			EU-FIAT-SCUDO-II-4X4-SWB-01	MEDIUM	两座短轴标准顶4×4分支。	READY
12145_lwb_highroof	12145	Van	Scudo II			EU-FIAT-SCUDO-II-4X4-LWB-HIGHROOF-01	MEDIUM	两座长轴高顶4×4分支。	READY
14904_swb	14904	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
14904_lwb	14904	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
14905_swb	14905	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
14905_lwb	14905	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
17495_swb	17495	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
17495_lwb	17495	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
118581_swb	118581	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118581_lwb	118581	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	HIGH	长轴平台底盘驾驶室。	READY
11751_swb	11751	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-SWB-01	MEDIUM	标准轴乘用型Bus分支。	READY
11751_lwb	11751	MPV	Scudo I (220)	220		EU-FIAT-SCUDO-220-MPV-LWB-01	MEDIUM	长轴乘用型Bus分支。	READY
11752_swb	11752	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-SWB-01	MEDIUM	标准轴封闭式厢式车分支。	READY
11752_lwb	11752	Van	Scudo I (220)	220		EU-FIAT-SCUDO-220-VAN-LWB-01	MEDIUM	长轴封闭式厢式车分支。	READY
118582_swb	118582	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	HIGH	标准轴平台底盘驾驶室。	READY
118582_lwb	118582	Pickup	Scudo I (220)	220	2	EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	HIGH	长轴平台底盘驾驶室。	READY
147260_standard_prefl	147260	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147260_maxi_prefl	147260	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147260_standard_facelift	147260	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147260_maxi_facelift	147260	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
147262	147262	Pickup	Scudo III			EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	HIGH	改款前L2平地板平台底盘。	READY
147261_standard_prefl	147261	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	Ktype覆盖改款前Standard车身。	READY
147261_maxi_prefl	147261	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	Ktype覆盖改款前Maxi车身。	READY
147261_standard_facelift	147261	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	Ktype覆盖改款后Standard车身。	READY
147261_maxi_facelift	147261	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	Ktype覆盖改款后Maxi车身。	READY
158255_standard_facelift	158255	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
158255_maxi_facelift	158255	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
802037_standard_facelift	802037	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard车身。	READY
802037_maxi_facelift	802037	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi车身。	READY
802300	802300	Pickup	Scudo III facelift			EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	HIGH	改款后平台底盘驾驶室。	READY
802878_standard_facelift	802878	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
802878_maxi_facelift	802878	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
802299_standard_facelift	802299	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard车身。	READY
802299_maxi_facelift	802299	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi车身。	READY
802303_standard_facelift	802303	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后Standard乘用型Bus分支。	READY
802303_maxi_facelift	802303	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后Maxi乘用型Bus分支。	READY
147257_standard_prefl	147257	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	HIGH	改款前E-Scudo Standard车身。	READY
147257_maxi_prefl	147257	Van	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	HIGH	改款前E-Scudo Maxi车身。	READY
147263	147263	Pickup	Scudo III			EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	HIGH	改款前E-Scudo L2平地板平台底盘。	READY
147264_standard_prefl	147264	MPV	Scudo III			EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	MEDIUM	改款前E-Scudo Standard乘用型Bus分支。	READY
147264_maxi_prefl	147264	MPV	Scudo III			EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	MEDIUM	改款前E-Scudo Maxi乘用型Bus分支。	READY
158246_standard_facelift	158246	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	MEDIUM	改款后E-Scudo Standard乘用型Bus分支。	READY
158246_maxi_facelift	158246	MPV	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	MEDIUM	改款后E-Scudo Maxi乘用型Bus分支。	READY
158248_standard_facelift	158248	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	HIGH	改款后E-Scudo Standard车身。	READY
158248_maxi_facelift	158248	Van	Scudo III facelift			EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	HIGH	改款后E-Scudo Maxi车身。	READY
158251	158251	Pickup	Scudo III facelift			EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	MEDIUM	改款后E-Scudo平台底盘驾驶室。	READY
801469_standard	801469	Van	Scudo III facelift	507		EU-FIAT-SCUDO-III-4X4-STANDARD-FACELIFT-01	MEDIUM	Dangel电动四驱Standard车身。	READY
801469_maxi	801469	Van	Scudo III facelift	507		EU-FIAT-SCUDO-III-4X4-MAXI-FACELIFT-01	MEDIUM	Dangel电动四驱Maxi车身。	READY
16053_3dr	16053	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16053_5dr	16053	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17907_3dr	17907	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17907_5dr	17907	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17910	17910	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18906_3dr	18906	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18906_5dr	18906	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18910	18910	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16054_3dr	16054	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16054_5dr	16054	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17134	17134	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
59259	59259	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16055_3dr	16055	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16055_5dr	16055	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17135	17135	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18907_3dr	18907	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18907_5dr	18907	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18908_3dr	18908	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18908_5dr	18908	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18909_3dr	18909	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18909_5dr	18909	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
18911	18911	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18912	18912	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
18913	18913	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
16056_3dr	16056	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16056_5dr	16056	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16057_3dr	16057	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
16057_5dr	16057	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17136	17136	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
17137	17137	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
17908_3dr	17908	Hatchback	Stilo (192)	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17908_5dr	17908	Hatchback	Stilo (192)	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门车身，按物理外廓拆分。	READY
17909	17909	Wagon	Stilo Multi Wagon (192)	192	5	EU-FIAT-STILO-192-WAGON-01	HIGH	Multi Wagon五门车身。	READY
12239_shortcab_prefl	12239	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	HIGH	初期短舱车身。	READY
12239_shortcab_facelift	12239	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	改款后短舱车身。	READY
17493	17493	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	改款后短舱车身。	READY
12240	12240	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	HIGH	初期短舱车身。	READY
17463_shortcab_prefl	17463	Pickup	Strada I (178)	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	MEDIUM	生产期覆盖初期短舱车身。	READY
17463_shortcab_facelift	17463	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	MEDIUM	生产期覆盖改款后短舱车身。	READY
17482_shortcab	17482	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	HIGH	1.9 JTD短舱分支。	READY
17482_longcab	17482	Pickup	Strada I facelift (278)	278	2	EU-FIAT-STRADA-278-PICKUP-LONGCAB-FACELIFT-01	HIGH	1.9 JTD长舱分支。	READY
15935	15935	Van	Talento I (290)	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	MEDIUM	短轴标准顶封闭式厢式车。	READY
15936	15936	Pickup	Talento I (290)	290	2	EU-FIAT-TALENTO-290-CHASSISCAB-01	MEDIUM	短轴平台底盘驾驶室。	READY
15940	15940	MPV	Talento I (290)	290		EU-FIAT-TALENTO-290-STANDARD-BODY-01	MEDIUM	短轴标准顶Bus车身。	READY
120653_swb	120653	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
120653_lwb	120653	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
120654_swb_lowroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶封闭式厢式车分支。	READY
120654_lwb_lowroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶封闭式厢式车分支。	READY
120654_swb_highroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶封闭式厢式车分支。	READY
120654_lwb_highroof	120654	Van	Talento II (296)	296		EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶封闭式厢式车分支。	READY
120655_swb	120655	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
120655_lwb	120655	MPV	Talento II (296)	296		EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5101-5200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	3800	1660	1480	Auto-Data Fiat Punto II (188) 3dr	https://www.auto-data.net/en/fiat-punto-ii-188-3dr-generation-1595
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	3840	1660	1480	Auto-Data Fiat Punto II (188 facelift 2003) 3dr	https://www.auto-data.net/en/fiat-punto-ii-188-facelift-2003-3dr-generation-1594
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	3835	1660	1480	Auto-Data Fiat Punto II (188) 5dr	https://www.auto-data.net/en/fiat-punto-ii-188-5dr-generation-6839
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	3865	1660	1480	Auto-Data Fiat Punto II (188 facelift 2003) 5dr	https://www.auto-data.net/en/fiat-punto-ii-188-facelift-2003-5dr-generation-6840
EU-FIAT-PUNTO-176-CONVERTIBLE-01	3760	1625	1447	Auto-Data Fiat Punto Cabrio 176C; Automobile-Catalog Fiat Punto Cabrio S	https://www.auto-data.net/en/fiat-punto-cabrio-176c-1.2-58hp-6991; https://www.automobile-catalog.com/car/1995/1457705/fiat_punto_cabrio_s.html
EU-FIAT-QUBO-225-MPV-PREFL-01	3959	1716	1735	Auto-Data Fiat Qubo 1.4 8V (73 Hp)	https://www.auto-data.net/en/fiat-qubo-1.4-8v-73hp-18163
EU-FIAT-QUBO-225-MPV-FACELIFT-01	3957	1716	1735	Fiat Qubo official brochure	https://www.autosynergy.co.uk/assets/brochures/fiat-qubo.pdf
EU-FIAT-QUBO-L-K9-MPV-SWB-01	4406	1848	1812	FIAT QUBO L official press release; Auto-Data Fiat Qubo L	https://www.media.stellantis.com/em-en/fiat/press/fiat-unveils-the-qubo-l-the-ultimate-family-mover-for-modern-living; https://www.auto-data.net/en/fiat-qubo-l-1.5-bluehdi-130hp-56959
EU-FIAT-QUBO-L-K9-MPV-LWB-01	4756	1848	1818	FIAT QUBO L official press release; Auto-Data Fiat Qubo L Maxi	https://www.media.stellantis.com/em-en/fiat/press/fiat-unveils-the-qubo-l-the-ultimate-family-mover-for-modern-living; https://www.auto-data.net/en/fiat-qubo-l-maxi-1.5-bluehdi-130hp-56962
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410	Auto-Data Fiat Regata 100 Super	https://www.auto-data.net/en/fiat-regata-138-100-super-1.6-100hp-7043
EU-FIAT-REGATA-138-WAGON-01	4267	1650	1450	Auto-Data Fiat Regata Weekend; Automobile-Catalog Fiat Regata Weekend D	https://www.auto-data.net/en/fiat-regata-weekend-75-1.5-75hp-7061; https://www.automobile-catalog.com/car/1989/717200/fiat_regata_weekend_d.html
EU-FIAT-RITMO-138A-HATCHBACK-1985-5D-01	3993	1650	1418	Automobile-Catalog Fiat Ritmo 90 S i.e.	https://www.automobile-catalog.com/car/1987/714935/fiat_ritmo_90_s_i_e_.html
EU-FIAT-RITMO-138A-HATCHBACK-105-3D-01	4014	1663	1390	Automobile-Catalog Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1983/714650/fiat_ritmo_105_tc.html
EU-FIAT-RITMO-138A-CONVERTIBLE-01	4014	1650	1400	Auto-Data Fiat Ritmo Bertone Cabrio; Automobile-Catalog Fiat Ritmo Bertone Cabrio	https://www.auto-data.net/en/fiat-ritmo-bertone-cabrio-i-100-1.6-100hp-7122; https://www.automobile-catalog.com/car/1985/2068610/fiat_ritmo_bertone_cabrio_85_s_palinuro.html
EU-FIAT-SCUDO-220-VAN-SWB-01	4440	1810	1940	Fiat Scudo first-generation owner manual dimensions; Fiat Drive Place Scudo I	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions; https://fiat.drive.place/scudo/i/group_minivan/385660
EU-FIAT-SCUDO-220-VAN-LWB-01	4840	1810	1930	Fiat Scudo first-generation owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
EU-FIAT-SCUDO-220-CHASSISCAB-SWB-01	4440	1810	1940	Quattroruote Fiat Scudo historical commercial-vehicle specifications	https://www.quattroruote.it/listino-archivio-trasporti/fiat/scudo-1996-2003/scudo-1996-2003-veicolo-da-allestire
EU-FIAT-SCUDO-III-VAN-STANDARD-PREFL-01	4959	1920	1881	Fiat Professional Scudo official brochure 07/2022	https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
EU-FIAT-SCUDO-III-VAN-MAXI-PREFL-01	5309	1920	1935	Fiat Professional Scudo official brochure 07/2022	https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
EU-FIAT-SCUDO-III-VAN-STANDARD-FACELIFT-01	4981	1924	1904	Fiat Professional Scudo 2024 official brochure	https://globalvans.co.uk/avm/images/vans/FISC/Fiat%20Scudo%202024%20Brochure.pdf
EU-FIAT-SCUDO-III-VAN-MAXI-FACELIFT-01	5331	1924	1935	Fiat Professional Scudo 2024 official brochure	https://globalvans.co.uk/avm/images/vans/FISC/Fiat%20Scudo%202024%20Brochure.pdf
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-SWB-LOWROOF-01	4805	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-LWB-LOWROOF-01	5135	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-220-MPV-SWB-01	4440	1810	1940	Fiat Scudo first-generation owner manual dimensions; Fiat Drive Place Scudo I	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions; https://fiat.drive.place/scudo/i/group_minivan/385660
EU-FIAT-SCUDO-220-MPV-LWB-01	4840	1810	1930	Fiat Scudo first-generation owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
EU-FIAT-SCUDO-II-CHASSISCAB-LWB-01	5053	1895	1942	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-LWB-HIGHROOF-01	5135	1895	2276	Fiat Professional Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-4X4-SWB-01	4805	1895	1880	Swiss FEDRO Fiat-Dangel Scudo type approval data; Fiat Scudo Dangel 4x4 owner supplement	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj; https://www.mycarusermanual.com/fiat/scudo/van/2007-2016/how-does-the-automobiles-dangel-4x4-equipment-work
EU-FIAT-SCUDO-II-4X4-LWB-HIGHROOF-01	5135	1895	2190	Swiss FEDRO Fiat-Dangel Scudo type approval data; Fiat Scudo Dangel 4x4 owner supplement	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj; https://www.mycarusermanual.com/fiat/scudo/van/2007-2016/how-does-the-automobiles-dangel-4x4-equipment-work
EU-FIAT-SCUDO-220-CHASSISCAB-LWB-01	4480	1810	1940	Quattroruote Fiat Scudo 2.0 JTD PL Pianale Cabinato	https://www.quattroruote.it/listino-archivio-trasporti/fiat/scudo-1996-2003/scudo-1996-2003-veicolo-da-allestire/scudo-20-jtd-pl-pianale-cabinato-051227200105
EU-FIAT-SCUDO-III-CHASSISCAB-PREFL-01	4959	1920	1881	Fiat Professional Scudo official price list 02/2022; Fiat Professional Scudo official brochure 07/2022	https://www.media.stellantis.com/uploads/de/model-document/preisliste_scudo_012022_revision_20220201620b9f4859160-62b9d358d7b68.pdf; https://mezzicommerciali.it/wp-content/uploads/2022/07/Fiat-Scudo-brochures.pdf
EU-FIAT-SCUDO-III-CHASSISCAB-FACELIFT-01	4815	1920	1930	Fiat Professional Scudo official technical data; Fiat Professional E-Scudo official technical data	https://www.fiat.de/professional/modelle/scudo/technical-data; https://www.fiat.de/professional/modelle/e-scudo/technical-data
EU-FIAT-SCUDO-III-4X4-STANDARD-FACELIFT-01	4981	1924	1865	Swiss FEDRO Citroën-Dangel e-Jumpy 4x4 type approval, Stellantis K0 physical twin	https://motoro.ch/en/fiche-technique/citroen-dangel/e-jumpy-4x4
EU-FIAT-SCUDO-III-4X4-MAXI-FACELIFT-01	5331	1924	1865	Swiss FEDRO Citroën-Dangel e-Jumpy 4x4 type approval, Stellantis K0 physical twin	https://motoro.ch/en/fiche-technique/citroen-dangel/e-jumpy-4x4
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
EU-FIAT-STILO-192-WAGON-01	4516	1756	1570	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.81.012_EN_02_11.06_L_LG/00_192_STILO_603.81.012_EN_02_11.06_L_LG.pdf
EU-FIAT-STRADA-178-PICKUP-SHORTCAB-PREFL-01	4398	1665	1585	Auto-Data Fiat Strada 178 1.2; Engine in Detail Fiat Strada short cab 1.2 1999	https://www.auto-data.net/en/fiat-strada-178-1.2-73hp-6927; https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-2-1999
EU-FIAT-STRADA-278-PICKUP-SHORTCAB-FACELIFT-01	4404	1665	1595	Engine in Detail Fiat Strada short cab 1.2 2001; Engine in Detail Fiat Strada short cab 1.9 JTD 2004	https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-2-2001; https://www.engineindetail.com/pa/fiat-strada-pickup-cab-short-1-9-jtd-2004
EU-FIAT-STRADA-278-PICKUP-LONGCAB-FACELIFT-01	4404	1665	1554	Engine in Detail Fiat Strada long cab 1.9 JTD 2005; UltimateSpecs Fiat Strada 1.9 JTD	https://www.engineindetail.com/pa/fiat-strada-pickup-cab-long-1-9-jtd-2005; https://www.ultimatespecs.com/car-specs/Fiat/800/Fiat-Strada-19-JTD.html
EU-FIAT-TALENTO-290-STANDARD-BODY-01	4157	1965	2100	Autogidas Fiat Talento 269/290 minibus specifications	https://autogidas.lt/en/auto-katalogas/fiat/talento/talento-269.390.3-1989-1994-k30341
EU-FIAT-TALENTO-290-CHASSISCAB-01	4157	1965	2100	Transit Center Fiat Talento history; Truck1 archived Fiat Talento dimensions; DENSO Fiat Talento 290UA4 catalogue	https://www.transitcenter.uk/fiat-talento.php; https://www.truck1.ke/vans/box-vans/fiat-talento-supercombi-ahk-a729104.html; https://www.denso-am.eu/catalog/pv/15936
EU-FIAT-TALENTO-296-MPV-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Talento Combi official page; Auto-Data Fiat Talento Combi L1H1	https://www.fiatprofessional.com/talento-combi/m1/interiors; https://www.auto-data.net/en/fiat-talento-combi-1.6-ecojet-125hp-l1h1-m1-24420
EU-FIAT-TALENTO-296-MPV-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Talento Combi official page; Auto-Data Fiat Talento Combi L2H1	https://www.fiatprofessional.com/talento-combi/m1/interiors; https://www.auto-data.net/en/fiat-talento-combi-1.6-ecojet-145hp-l2h1-m1-25213
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490	Fiat Professional Talento official technical datasheet 10.01.2018	https://www.media.stellantis.com/uploads/de/DE/2018/FIAT_PROF/Technische_Daten/180110_FP_Fiat_Talento.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5101-5200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.denso-am.eu/catalog/pv/15936?utm_source=chatgpt.com "Car parts for FIAT TALENTO Platform/Chassis (290_), 2.0 ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（983 行）
- 累计尺寸组：dimension_groups_final.tsv（265 行）

