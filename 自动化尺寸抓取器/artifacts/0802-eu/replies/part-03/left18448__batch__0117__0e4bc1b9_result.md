# 任务：left18448 第 11601-11700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0117__0e4bc1b9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11601-11700 行

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
left18448 第 11601-11700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Nissan	Almera i hatchback	2.0 GTI	Schrägheck	Frontantrieb	Benzin	Jul 1996	Mar 2000	5991
Nissan	Almera ii	1.5	Stufenheck	Frontantrieb	Benzin	Jul 2000	Nov 2006	14915
Nissan	Almera ii	1.5	Stufenheck	Frontantrieb	Benzin	Oct 2002	Sep 2006	17242
Nissan	Almera ii	1.8	Stufenheck	Frontantrieb	Benzin	Jul 2000	Nov 2002	15110
Nissan	Almera ii	1.8	Stufenheck	Frontantrieb	Benzin	Oct 2002	Sep 2006	17243
Nissan	Almera ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	Jan 2003	Sep 2006	17244
Nissan	Almera ii	2.2 DCI	Stufenheck	Frontantrieb	Diesel	Sep 2003	Sep 2006	17683
Nissan	Almera ii	2.2 DCI	Stufenheck	Frontantrieb	Diesel	Sep 2003	Sep 2006	17684
Nissan	Almera ii	2.2 DI	Stufenheck	Frontantrieb	Diesel	Jul 2000	Apr 2003	14916
Nissan	Almera ii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	Mar 2000	Nov 2006	14657
Nissan	Almera ii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	Oct 2002	Sep 2006	17239
Nissan	Almera ii hatchback	1.8	Schrägheck	Frontantrieb	Benzin	Jan 2000	Nov 2002	14658
Nissan	Almera ii hatchback	1.8	Schrägheck	Frontantrieb	Benzin	Oct 2002	Sep 2006	17240
Nissan	Almera ii hatchback	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Jan 2003	Sep 2006	17241
Nissan	Almera ii hatchback	2.2 DCI	Schrägheck	Frontantrieb	Diesel	Sep 2003	Sep 2006	17681
Nissan	Almera ii hatchback	2.2 DCI	Schrägheck	Frontantrieb	Diesel	Sep 2003	Sep 2006	17682
Nissan	Almera ii hatchback	2.2 DI	Schrägheck	Frontantrieb	Diesel	Mar 2000	Apr 2003	14659
Nissan	Almera tino	1.8	Großraumlimousine	Frontantrieb	Benzin	Aug 2000	Feb 2006	11262
Nissan	Almera tino	1.8	Großraumlimousine	Frontantrieb	Benzin	Dec 2002	Feb 2006	17690
Nissan	Almera tino	2	Großraumlimousine	Frontantrieb	Benzin	Aug 2000	Jan 2003	11263
Nissan	Almera tino	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	Aug 2000	Feb 2006	14917
Nissan	Almera tino	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	Sep 2003	Feb 2006	17685
Nissan	Almera tino	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	Sep 2003	Feb 2006	17686
Nissan	Ariya	EV	SUV	Frontantrieb	Elektro	Jul 2020	-	144397
Nissan	Ariya	EV	SUV	Frontantrieb	Elektro	Jul 2020	-	144398
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	Jul 2020	-	144399
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	Jul 2020	-	144400
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	Jul 2020	-	144403
Nissan	Ariya	EV E-4orce	SUV	Allrad	Elektro	Nov 2024	-	801088
Nissan	Bluebird	1.6	Stufenheck	Frontantrieb	Benzin	May 2013	-	125847
Nissan	Bluebird	1.8	Stufenheck	Heckantrieb	Benzin	Jul 1974	Nov 1979	10679
Nissan	Bluebird	1.8	Schrägheck	Frontantrieb	Benzin	Jan 1987	Apr 1990	125980
Nissan	Bluebird	2.0 TD	Stufenheck	Heckantrieb	Diesel	Jan 1983	Sep 1983	17015
Nissan	Cabstar	28.11 Dci, 32.11 Dci, 35.11 DCI 2.5	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2013	50635
Nissan	Cabstar	28.12 Dci, 32.12 Dci, 34.12 Dci, 35.12 DCI 2.5	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2013	119611
Nissan	Cabstar	35.13 Dci, 45.13 DCI 2.5	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2012	119607
Nissan	Cabstar	35.14 DCI 3.0	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2013	119609
Nissan	Cabstar	35.14 Dci, 45.14 DCI 2.5	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2013	119612
Nissan	Cabstar	35.15 Dci, 45.15 DCI 3.0	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	Dec 2013	119610
Nissan	Cedric	3	Stufenheck	Heckantrieb	Benzin	Sep 1987	May 1991	59711
Nissan	Cedric	3	Stufenheck	Heckantrieb	Benzin	Jun 1991	Oct 1995	59712
Nissan	Cherry	1	Stufenheck	Frontantrieb	Benzin	Sep 1970	Sep 1978	10680
Nissan	Datsun 140j	1.4	Stufenheck	Heckantrieb	Benzin	Jan 1973	May 1977	10660
Nissan	Datsun 160j	1.6	Stufenheck	Heckantrieb	Benzin	Jan 1973	Jan 1978	10661
Nissan	Elgrand	3.5	Großraumlimousine	Frontantrieb	Benzin	Sep 2010	-	51940
Nissan	Figaro	1	Coupe	Frontantrieb	Benzin	Feb 1991	Apr 1992	34714
Nissan	Gt-R	Nismo	Coupe	Allrad	Benzin	Jul 2014	-	107483
Nissan	Gt-R	V6	Coupe	Allrad	Benzin	Oct 2011	-	55403
Nissan	Gt-R	V6	Coupe	Allrad	Benzin	Jul 2012	-	113192
Nissan	Gt-R	V6	Coupe	Allrad	Benzin	Jun 2016	-	121620
Nissan	Interstar	DCI 100	Kasten	Frontantrieb	Diesel	Nov 2003	Mar 2006	18105
Nissan	Interstar	DCI 105	Kasten	Frontantrieb	Diesel	Jun 2024	-	158681
Nissan	Interstar	DCI 110	Kasten	Frontantrieb	Diesel	Nov 2021	Dec 2024	146146
Nissan	Interstar	DCI 115	Bus	Frontantrieb	Diesel	Apr 2002	Aug 2006	16949
Nissan	Interstar	DCI 115	Kasten	Frontantrieb	Diesel	Apr 2002	-	16952
Nissan	Interstar	DCI 130	Kasten	Frontantrieb	Diesel	Jun 2024	-	158682
Nissan	Interstar	DCI 130 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2024	-	800287
Nissan	Interstar	DCI 130 RWD	Kasten	Heckantrieb	Diesel	Nov 2021	Dec 2024	146152
Nissan	Interstar	DCI 130 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2021	Dec 2024	146153
Nissan	Interstar	DCI 135	Kasten	Frontantrieb	Diesel	Nov 2021	Dec 2024	146147
Nissan	Interstar	DCI 140	Kasten	Frontantrieb	Diesel	Nov 2003	-	18103
Nissan	Interstar	DCI 140	Bus	Frontantrieb	Diesel	Nov 2003	-	18104
Nissan	Interstar	DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2021	Dec 2024	146150
Nissan	Interstar	DCI 145 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2021	Dec 2024	146154
Nissan	Interstar	DCI 145 RWD	Kasten	Heckantrieb	Diesel	Nov 2021	Dec 2024	146155
Nissan	Interstar	DCI 150	Kasten	Frontantrieb	Diesel	Nov 2021	Dec 2024	146148
Nissan	Interstar	DCI 150	Kasten	Frontantrieb	Diesel	Jun 2024	-	158683
Nissan	Interstar	DCI 150 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2024	-	800288
Nissan	Interstar	DCI 150 Heckantrieb	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2025	-	802484
Nissan	Interstar	DCI 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2021	Dec 2024	146151
Nissan	Interstar	DCI 165	Kasten	Frontantrieb	Diesel	Oct 2022	Dec 2024	152815
Nissan	Interstar	DCI 165 RWD	Kasten	Heckantrieb	Diesel	Nov 2021	Dec 2024	146156
Nissan	Interstar	DCI 165 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 2021	Dec 2024	146157
Nissan	Interstar	DCI 170	Kasten	Frontantrieb	Diesel	Jun 2024	-	158684
Nissan	Interstar	DCI 170 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 2024	-	800289
Nissan	Interstar	DCI 170 Heckantrieb	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2025	-	802485
Nissan	Interstar	DCI 180	Kasten	Frontantrieb	Diesel	Nov 2021	Dec 2024	146149
Nissan	Interstar	DCI 80	Bus	Frontantrieb	Diesel	Apr 2002	Aug 2006	16947
Nissan	Interstar	DCI 80	Kasten	Frontantrieb	Diesel	Apr 2002	Aug 2006	16950
Nissan	Interstar	DCI 90	Bus	Frontantrieb	Diesel	Jul 2002	Aug 2006	16948
Nissan	Interstar	DCI 90	Kasten	Frontantrieb	Diesel	Jul 2002	-	16951
Nissan	Interstar	Interstar-e	Kasten	Frontantrieb	Elektro	Sep 2024	-	800285
Nissan	Interstar	Interstar-e	Kasten	Frontantrieb	Elektro	Sep 2024	-	800286
Nissan	Interstar	Interstar-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Sep 2024	-	800986
Nissan	Interstar	Interstar-e	Pritsche/Fahrgestell	Frontantrieb	Elektro	Sep 2024	-	800987
Nissan	Juke	1.6	SUV	Frontantrieb	Benzin	Jun 2010	Dec 2019	34721
Nissan	Juke	1.6	SUV	Frontantrieb	Benzin	May 2013	Dec 2019	59302
Nissan	Juke	1.6	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Dec 2019	142860
Nissan	Juke	1.2 Dig-t	SUV	Frontantrieb	Benzin	May 2014	Dec 2019	106276
Nissan	Juke	1.5 DCI	SUV	Frontantrieb	Diesel	Jun 2010	Dec 2019	34725
Nissan	Juke	1.6 Dig-t	SUV	Frontantrieb	Benzin	Jun 2010	Dec 2019	34724
Nissan	Juke	1.6 Dig-t 4X4	SUV	Allrad	Benzin	Jun 2010	Dec 2019	34723
Nissan	Juke	1.6 Dig-t Nismo	SUV	Frontantrieb	Benzin	Nov 2012	Dec 2019	58599
Nissan	Juke	1.6 Dig-t Nismo 4X4	SUV	Allrad	Benzin	Nov 2012	Dec 2019	53454
Nissan	Juke	1.6 Dig-t Nismo RS	SUV	Frontantrieb	Benzin	Aug 2014	Dec 2019	107628
Nissan	Juke	1.6 Dig-t Nismo RS 4X4	SUV	Allrad	Benzin	Aug 2014	Dec 2019	108986
Nissan	Juke	1.6 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Aug 2019	-	148232
Nissan	Juke	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2012	Dec 2019	126913
Nissan	Juke	Cvtc	Kasten/SUV	Frontantrieb	Benzin	Mar 2013	Dec 2019	142859
Nissan	Juke	DCI	Kasten/SUV	Frontantrieb	Diesel	Jun 2010	Dec 2019	142928


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 Almera I、Almera II、Almera Tino 与 Ariya 共 29 个输入 Ktype。Almera II 轿车改款后长度由 4425 mm 增至 4435 mm，掀背车由 4184 mm 增至 4197 mm，因此按改款前后拆组；掀背 Ktype 同时按三门、五门拆分。([汽车目录][1])
* Ariya 普通 FE0 与 NISMO 外廓分别闭合为 4595×1850×1660 mm 和 4655×1850×1650 mm，宽度均为不含后视镜口径。
* Ktype `801088` 已确认是 320 kW／435 PS 的 Ariya e-4ORCE NISMO，关联独立 NISMO 尺寸组。([B-Parts][2])
* Almera Tino V10 当前所列动力版本复用同一五门 MPV 外廓组。([汽车目录][3])

## 当前批次进度

* 已闭合输入 Ktype：29 / 100
* READY 映射：40 行
* 待处理输入 Ktype：71
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5991	5991	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-HATCHBACK-3D-01	HIGH	N15 GTI仅三门。	READY
14915_prefl	14915	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	MEDIUM	该Ktype跨越2002年改款，按改款前外廓拆分。	READY
14915_facelift	14915	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越2002年改款，按改款后外廓拆分。	READY
17242	17242	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
15110	15110	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	HIGH	N16四门轿车。	READY
17243	17243	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17244	17244	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17683	17683	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17684	17684	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
14916	14916	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	HIGH	N16四门轿车。	READY
14657_3dr_prefl	14657	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_5dr_prefl	14657	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_3dr_facelift	14657	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_5dr_facelift	14657	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
17239_3dr	17239	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17239_5dr	17239	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14658_3dr	14658	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14658_5dr	14658	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17240_3dr	17240	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17240_5dr	17240	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17241_3dr	17241	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17241_5dr	17241	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17681_3dr	17681	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17681_5dr	17681	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17682_3dr	17682	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17682_5dr	17682	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14659_3dr	14659	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14659_5dr	14659	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
11262	11262	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17690	17690	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
11263	11263	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
14917	14917	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17685	17685	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17686	17686	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
144397	144397	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144398	144398	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144399	144399	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144400	144400	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144403	144403	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
801088	801088	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-NISMO-SUV-01	HIGH	320 kW/435 PS Ktype，对应NISMO外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-ALMERA-I-HATCHBACK-3D-01	4120	1690	1395	Automobile-Catalog 1998 Nissan Almera 2.0 GTi specifications	https://www.automobile-catalog.com/car/1998/2252525/nissan_almera_2_0_gti.html
EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	4425	1695	1445	Automobile-Catalog 2000 Nissan Almera Sedan 1.5 Base specifications	https://www.automobile-catalog.com/car/2000/2283380/nissan_almera_sedan_1_5_base.html
EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	4435	1695	1445	Automobile-Catalog 2004 Nissan Almera Sedan 1.5 Acenta specifications	https://www.automobile-catalog.com/car/2004/2283605/nissan_almera_sedan_1_5_acenta.html
EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	4184	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2000 Nissan Almera 1.5 Base specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2000/2283305/nissan_almera_1_5_base.html
EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	4184	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2000 Nissan Almera 1.5 Base specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2000/2283305/nissan_almera_1_5_base.html
EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	4197	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2003 Nissan Almera 1.5 Acenta specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2003/2283455/nissan_almera_1_5_acenta.html
EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	4197	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2003 Nissan Almera 1.5 Acenta specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2003/2283455/nissan_almera_1_5_acenta.html
EU-NISSAN-ALMERA-TINO-MPV-01	4264	1758	1608	Automobile-Catalog 2003 Nissan Almera Tino 1.8 Acenta specifications	https://www.automobile-catalog.com/car/2003/2285660/nissan_almera_tino_1_8_acenta_automatic.html
EU-NISSAN-ARIYA-FE0-SUV-01	4595	1850	1660	Nissan ARIYA official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Ariya_UK.pdf
EU-NISSAN-ARIYA-FE0-NISMO-SUV-01	4655	1850	1650	Nissan ARIYA official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Ariya_UK.pdf
```

## 下一步优先处理

1. 闭合 Juke F15 标准车身、F15 Nismo/Nismo RS 外部套件和 F16 Hybrid 三类外廓。
2. 按代际处理 Bluebird、Cedric、Cherry、Datsun 140J/160J、Figaro 与 GT-R。
3. 集中拆分 Cabstar 和 Interstar 的轴距、车顶、驱动形式、客车/厢式车及底盘驾驶室分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/2283380/nissan_almera_sedan_1_5_base.html?utm_source=chatgpt.com "2000 Nissan Almera Sedan 1.5 Base Specs Review (66 kW / 90 PS / 89 hp) (since June 2000 for Europe )"
[2]: https://www.b-parts.co.uk/auto-parts/body-parts/tailgate/nissan-ariya-fe0-ev-e-4orce-801088-vv?utm_source=chatgpt.com "Tailgate for NISSAN ARIYA (FE0) EV e-4ORCE (435 hp)"
[3]: https://www.automobile-catalog.com/car/2003/2285675/nissan_almera_tino_1_8_tekna.html?utm_source=chatgpt.com "2003 Nissan Almera Tino 1.8 Tekna Specs Review (85 kW / 116 PS / 114 hp) (since April 2003 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 修正 Ariya NISMO 高度：日产官方 NISMO 技术表明确为 `4655×1850×1660 mm`。为避免覆盖上一轮已建立的 `-01`，新建 `EU-NISSAN-ARIYA-FE0-NISMO-SUV-02`，并将 Ktype `801088` 改指新组。
* 首次闭合 Juke：F15 标准车身、F15 NISMO/NISMO RS、F16 Hybrid 共三个尺寸组；F15 四驱及商用登记版本未改变对应外廓。
* 首次闭合 GT-R R35 改款前标准车身、2017 款改款后标准车身及 NISMO 外廓；同时闭合 Figaro FK10。([汽车目录][1])

## 当前批次进度

* READY 输入 Ktype：49 / 100
* READY 映射：60 行
* 待处理输入 Ktype：51
* 当前有效尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801088	801088	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-NISMO-SUV-02	HIGH	NISMO专属外部套件。	READY
34714	34714	Convertible	Figaro	FK10	2	EU-NISSAN-FIGARO-FK10-CONVERTIBLE-01	HIGH	输入BodyStyle为Coupe；实际为双门敞篷车身。	READY
107483	107483	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-NISMO-COUPE-01	HIGH	NISMO专属前后外部套件。	READY
55403	55403	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	2012款标准外廓。	READY
113192	113192	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	2013款标准外廓。	READY
121620	121620	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-FACELIFT-01	HIGH	2017款改款后标准外廓。	READY
34721	34721	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
59302	59302	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
142860	142860	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
106276	106276	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34725	34725	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34724	34724	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34723	34723	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
58599	58599	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO外部套件。	READY
53454	53454	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO外部套件。	READY
107628	107628	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO RS外部套件。	READY
108986	108986	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO RS外部套件。	READY
148232	148232	SUV	Juke II	F16	5	EU-NISSAN-JUKE-F16-HYBRID-SUV-01	HIGH		READY
126913	126913	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
142859	142859	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
142928	142928	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-ARIYA-FE0-NISMO-SUV-02	4655	1850	1660	Nissan ARIYA NISMO official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_ARIYA_NISMO_UK.pdf
EU-NISSAN-FIGARO-FK10-CONVERTIBLE-01	3740	1630	1365	Nissan Heritage Collection Figaro 1991 FK10	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/397_figaro.html
EU-NISSAN-GT-R-R35-NISMO-COUPE-01	4690	1895	1370	Nissan GT-R NISMO official specifications; Car Watch 2017 GT-R NISMO Europe specification report	https://www3.nissan.co.jp/content/dam/Nissan/jp/vehicles/GT-R/pdf/gt-r_nismo_specification.pdf;https://car.watch.impress.co.jp/docs/news/759581.html
EU-NISSAN-GT-R-R35-COUPE-PREFL-01	4670	1895	1370	Automobile-Catalog 2012 Nissan GT-R Black Edition specifications	https://www.automobile-catalog.com/car/2012/2182730/nissan_gt-r_black_edition.html
EU-NISSAN-GT-R-R35-COUPE-FACELIFT-01	4710	1895	1370	Nissan GT-R official brochure; Automobile-Catalog 2017 Nissan GT-R Europe specifications	https://www-asia.nissan-cdn.net/content/dam/Nissan/in/brochures/GT-R%20Brochure%20Final_Web.pdf;https://www.automobile-catalog.com/car/2017/2409620/nissan_gt-r.html
EU-NISSAN-JUKE-F15-SUV-01	4135	1765	1565	Nissan JUKE official Australia brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Files/Brochures/Models/Juke/JUK0139r02_Nissan_JUKE_Brochure%20PDF.pdf
EU-NISSAN-JUKE-F15-NISMO-SUV-01	4165	1770	1565	Automobile-Catalog 2014 Nissan Juke Nismo Europe specifications; Automobile-Catalog 2015 Nissan Juke Nismo RS Europe specifications	https://www.automobile-catalog.com/car/2014/2320565/nissan_juke_nismo.html;https://www.automobile-catalog.com/car/2015/2321090/nissan_juke_nismo_rs.html
EU-NISSAN-JUKE-F16-HYBRID-SUV-01	4210	1800	1593	Nissan JUKE official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Juke_UK.pdf
```

## 下一步优先处理

1. 闭合 Bluebird、Cedric、Cherry、Datsun 140J/160J 与 Elgrand。
2. 聚类处理 2002—2006 年 Interstar 客车及厢式车分支。
3. 拆分 2021—2025 年 Interstar 和 Cabstar 的轴距、车顶、驱动及底盘驾驶室外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/2182730/nissan_gt-r_black_edition.html?utm_source=chatgpt.com "2012 Nissan GT-R Black Edition Specs Review (404.5 kW ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Bluebird Sylphy B17、Bluebird T12/T72 掀背车改款前后和 Bluebird 910 轿车，共覆盖 3 个输入 Ktype、4 个物理外廓。Sylphy B17 使用日产官方规格；T12/T72 的长度由 4365 mm 变为 4420 mm，因此 Ktype `125980` 拆分为改款前后两行。([日产][1])
* 首次闭合 Cedric Y31、Y32 两代四门硬顶轿车。([汽车目录][2])
* Cherry E10 的输入记录覆盖二门和四门轿车，Ktype `10680` 按门数拆分；两个车身外廓尺寸相同，但作为不同物理车身分别建组。([日产汽车全球网站][3])
* 首次闭合 Datsun 140J 与 160J 的 710 系列四门轿车尺寸组。([汽车目录][4])

## 当前批次进度

* READY 输入 Ktype：57 / 100
* READY 映射：70 行
* PENDING 输入 Ktype：43
* 当前有效尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125847	125847	Sedan	Bluebird Sylphy III	B17	4	EU-NISSAN-BLUEBIRD-SYLPHY-B17-SEDAN-01	HIGH		READY
125980_prefl	125980	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-PREFL-01	HIGH	该Ktype跨越T12/T72外观改款，按改款前外廓拆分。	READY
125980_facelift	125980	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-FACELIFT-01	HIGH	该Ktype跨越T12/T72外观改款，按改款后外廓拆分。	READY
17015	17015	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-01	HIGH		READY
59711	59711	Sedan	Cedric Y31	Y31	4	EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	HIGH	四门硬顶轿车。	READY
59712	59712	Sedan	Cedric Y32	Y32	4	EU-NISSAN-CEDRIC-Y32-HARDTOP-SEDAN-01	HIGH	四门硬顶轿车。	READY
10680_2dr	10680	Sedan	Cherry I	E10	2	EU-NISSAN-CHERRY-E10-SEDAN-2D-01	MEDIUM	E10车型条目覆盖二门与四门轿车，按门数拆分。	READY
10680_4dr	10680	Sedan	Cherry I	E10	4	EU-NISSAN-CHERRY-E10-SEDAN-4D-01	MEDIUM	E10车型条目覆盖二门与四门轿车，按门数拆分。	READY
10660	10660	Sedan	Datsun 140J 710	710	4	EU-NISSAN-DATSUN-140J-710-SEDAN-01	MEDIUM	710系列四门出口轿车。	READY
10661	10661	Sedan	Datsun 160J 710	710	4	EU-NISSAN-DATSUN-160J-710-SEDAN-01	MEDIUM	710系列四门出口轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-BLUEBIRD-SYLPHY-B17-SEDAN-01	4615	1760	1495	Nissan Sylphy official brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/ph/brochures/Sylphy_DigitalBrochure.pdf
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-PREFL-01	4365	1690	1395	Automobile-Catalog 1987 Nissan Bluebird 1.8 GS 5-d specifications	https://www.automobile-catalog.com/car/1987/2236220/nissan_bluebird_1_8_gs_5-d.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-FACELIFT-01	4420	1690	1395	Automobile-Catalog 1990 Nissan Bluebird 1.8 GS 5-d specifications	https://www.automobile-catalog.com/car/1990/2236625/nissan_bluebird_1_8_gs_5-d.html
EU-NISSAN-BLUEBIRD-910-SEDAN-01	4395	1655	1400	Automobile-Catalog 1983 Datsun Bluebird 2.0 Turbo D specifications	https://www.automobile-catalog.com/car/1983/2120180/datsun_bluebird_2_0_turbo_d.html
EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	4860	1720	1380	Automobile-Catalog 1988 Nissan Cedric V30 Turbo Brougham VIP Hardtop specifications	https://www.automobile-catalog.com/car/1988/2152115/nissan_cedric_4door_hardtop_v30_turbo_brougham_vip.html
EU-NISSAN-CEDRIC-Y32-HARDTOP-SEDAN-01	4780	1745	1410	Auto-Data Nissan Cedric Y32 3.0i V6 Turbo specifications	https://www.auto-data.net/en/nissan-cedric-y32-3.0i-v6-24v-turbo-255hp-automatic-919
EU-NISSAN-CHERRY-E10-SEDAN-2D-01	3610	1470	1380	Nissan Heritage Collection Cherry 2-door Deluxe	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/cherry_2door_deluxe.html
EU-NISSAN-CHERRY-E10-SEDAN-4D-01	3610	1470	1380	Automobile-Catalog 1970 Nissan Cherry 4Door DX specifications	https://www.automobile-catalog.com/car/1970/2091875/nissan_cherry_4door_deluxe_3-speed.html
EU-NISSAN-DATSUN-140J-710-SEDAN-01	4120	1580	1405	Automobile-Catalog 1975 Datsun 140J Deluxe specifications	https://www.automobile-catalog.com/car/1975/2094650/datsun_140j_deluxe.html
EU-NISSAN-DATSUN-160J-710-SEDAN-01	4120	1580	1395	Automobile-Catalog 1973 Datsun 160J Deluxe specifications	https://www.automobile-catalog.com/car/1973/2094725/datsun_160j_deluxe.html
```

## 下一步优先处理

1. 解决 Bluebird B610 与 Elgrand E52 的具体外廓边界。
2. 闭合 2002—2006 年 Interstar 客车和厢式车的轴距、车顶分支。
3. 集中拆分 2021—2025 年 Interstar 与 Cabstar 的轴距、车顶、驱动形式及底盘驾驶室分支。

推进信号：CONTINUE

[1]: https://www-asia.nissan-cdn.net/content/dam/Nissan/ph/brochures/Sylphy_DigitalBrochure.pdf "Sylphy_DigitalBrochure"
[2]: https://www.automobile-catalog.com/car/1988/2152115/nissan_cedric_4door_hardtop_v30_turbo_brougham_vip.html?utm_source=chatgpt.com "1988 Nissan Cedric 4Door Hardtop V30 Turbo Brougham ..."
[3]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/cherry_2door_deluxe.html "Nissan | Heritage Collection | Cherry 2-door Deluxe"
[4]: https://www.automobile-catalog.com/car/1975/2094650/datsun_140j_deluxe.html?utm_source=chatgpt.com "1975 Datsun 140J Deluxe Specs Review (48 kW / 65 PS ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Ktype `10679` 的生产区间跨越 Bluebird 610 与 810 两代四门轿车，已拆分为两个物理外廓；610 使用日产历史资料，810 使用对应 1.8 四门轿车规格。([日产汽车全球网站][1])
* 首次闭合 2024 年 All-New Interstar 厢式车的 `L2H2`、`L3H2`、`L3H3` 三个外廓组。标准后踏板属于厢式车标准配置，因此长度采用含标准后踏板的 `5780/6410 mm`，宽度均为官方明确的不含后视镜 `2080 mm`。
* `dCi 105` 关联 L2H2；`dCi 130/150/170` 分别关联 L2H2、L3H2、L3H3。([Citygate Leasing][2])

## 当前批次进度

* READY 输入 Ktype：62 / 100
* READY 映射：82 行
* PENDING 输入 Ktype：38
* 当前有效尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10679_610	10679	Sedan	Bluebird 610	610	4	EU-NISSAN-BLUEBIRD-610-SEDAN-01	HIGH	该Ktype跨越610与810两代四门轿车。	READY
10679_810	10679	Sedan	Bluebird 810	810	4	EU-NISSAN-BLUEBIRD-810-SEDAN-01	HIGH	该Ktype跨越610与810两代四门轿车。	READY
158681_l2h2	158681	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	MEDIUM	L2H2厢式车外廓。	READY
158682_l2h2	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158682_l3h2	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158682_l3h3	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
158683_l2h2	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158683_l3h2	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158683_l3h3	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
158684_l2h2	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158684_l3h2	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158684_l3h3	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-BLUEBIRD-610-SEDAN-01	4215	1600	1405	Nissan Heritage Collection Datsun Bluebird U 1600GL	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/bluebird_u_1600gl.html
EU-NISSAN-BLUEBIRD-810-SEDAN-01	4260	1630	1390	Automobile-Catalog 1977 Datsun Bluebird 180B Sedan; Bind Nissan Bluebird 810 1.8 AT specifications	https://www.automobile-catalog.com/car/1977/35720/datsun_bluebird_180_b.html;https://bind.lt/en/technical-specifications/nissan/bluebird-1/810-restyling/sedan/1-8-at-88-hp
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	5780	2080	2498	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	6410	2080	2498	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	6410	2080	2756	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
```

## 下一步优先处理

1. 闭合 Elgrand E52 的不同外部套件及改款分支。
2. 处理 2024 年 Interstar-e 厢式车与底盘车 Ktype。
3. 集中拆分 2021–2024 年 Interstar 的 L/H、FWD/RWD 和厢式车/底盘驾驶室分支。
4. 最后处理 Cabstar 的驾驶室、轴距及底盘外廓。

推进信号：CONTINUE

[1]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/bluebird_u_1600gl.html?utm_source=chatgpt.com "Datsun Bluebird U 1600GL (1975 : 610)"
[2]: https://www.citygateleasing.co.uk/nissan-van-lease-deals/business/interstar/panelvan-f33-l2-diesel-2-0-dci-105ps-h2-acenta-van/?utm_source=chatgpt.com "Nissan Interstar F33 L2 Diesel 2.0 DCI 105PS H2 Acenta Van"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 首次闭合 Interstar X70 厢式车的 L1H1、L2H2、L3H2、L3H3 四个尺寸组，并批量关联 dCi 80、dCi 100、dCi 115、dCi 140。2004 年日产规格表同时明确了各动力可用的轴距/车顶组合；1990 mm 宽度由日产后续官方手册明确为不含后视镜口径。
* Interstar-e Ktype `800285`、`800286` 已关联既有 All-New Interstar L2H2、L3H2 尺寸组；电动厢式车不包含 L3H3 分支。

## 当前批次进度

* READY 输入 Ktype：68 / 100
* READY 映射：95 行
* PENDING 输入 Ktype：32
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18105_l1h1	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
18105_l2h2	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
18105_l3h2	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
16952_l2h2	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
16952_l3h2	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
16952_l3h3	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
18103_l3h2	18103	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
18103_l3h3	18103	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
16950	16950	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
800285_l2h2	800285	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2电动厢式车外廓。	READY
800285_l3h2	800285	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2电动厢式车外廓。	READY
800286_l2h2	800286	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2电动厢式车外廓。	READY
800286_l3h2	800286	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2电动厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	4899	1990	2256	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	5399	1990	2493	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	5899	1990	2490	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	5899	1990	2720	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
```

## 下一步优先处理

1. 闭合 Interstar X70 的 dCi 90 客车/厢式车及 dCi 80、115、140 客车分支。
2. 批量处理 2021–2024 年 Interstar 厢式车的 FWD/RWD、L1–L4 和 H1–H3 外廓。
3. 处理 All-New Interstar 及 Interstar-e 底盘驾驶室分支。
4. 最后拆分 Cabstar 驾驶室、轴距和底盘外廓，并完成 Elgrand E52。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 2021–2024 年 Interstar II `X62B` 前驱厢式车中的 dCi 110 与 dCi 135 分支。首次建立 L1H1、L2H2、L2H3、L3H2、L3H3 五个尺寸组；宽度统一采用官方明确的不含后视镜 `2070 mm`。([日产][1])
* Ktype `51940` 的 Elgrand E52 仍存在多个原厂外部套件长度分支，暂不创建猜测性派生行。([日产历史][2])
* Interstar X70 客车资料的车高口径尚有冲突，本轮未新建客车尺寸组。

## 当前批次进度

* READY 输入 Ktype：70 / 100
* READY 映射：102 行
* PENDING 输入 Ktype：30
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146146_l1h1	146146	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146146_l2h2	146146	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146147_l1h1	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146147_l2h2	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146147_l2h3	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	MEDIUM	L2H3前驱高顶厢式车外廓。	READY
146147_l3h2	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146147_l3h3	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	5048	2070	2307	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	5548	2070	2499	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	5548	2070	2749	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	6198	2070	2488	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	6198	2070	2744	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
```

## 下一步优先处理

1. 关联 dCi 150、dCi 165 与 dCi 180 前驱厢式车到现有 X62B 尺寸组。
2. 首次建立 X62B 后驱 L3/L4 厢式车尺寸组，并处理 dCi 130、145、165 RWD。
3. 闭合 X62B 与 All-New Interstar 底盘驾驶室分支。
4. 解决 X70 客车尺寸冲突，随后处理 Cabstar 与 Elgrand E52。

推进信号：CONTINUE

[1]: https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf?utm_source=chatgpt.com "Nissan Interstar"
[2]: https://history.nissan.co.jp/ELGRAND/E52/1008/PDF/elgrand_specification.pdf?utm_source=chatgpt.com "350Highway STAR Premium） 単位："


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已将 X62B 的 dCi 150、dCi 180 前驱厢式车批量关联至现有 `L1H1`、`L2H2`、`L3H2`、`L3H3` 尺寸组，不重复输出既有尺寸事实。日产价目资料明确列有这些动力与车身组合。([ADAC][1])
* 首次闭合 X62B 后驱厢式车的 `L3H2`、`L3H3`、`L4H2`、`L4H3` 四个外廓组，并批量关联 dCi 130、dCi 145、dCi 165 RWD。官方同平台尺寸资料明确长度、宽度及后驱 H2/H3 高度；日产价目资料同时覆盖相关后驱动力与车身组合。

## 当前批次进度

* READY 输入 Ktype：75 / 100
* READY 映射：122 行
* PENDING 输入 Ktype：25
* 已确认尺寸组：45
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146152_l3h2	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146152_l3h3	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146152_l4h2	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146152_l4h3	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146155_l3h2	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146155_l3h3	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146155_l4h2	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146155_l4h3	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146148_l1h1	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146148_l2h2	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146148_l3h2	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146148_l3h3	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
146156_l3h2	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146156_l3h3	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146156_l4h2	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146156_l4h3	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146149_l1h1	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146149_l2h2	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146149_l3h2	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146149_l3h3	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	6198	2070	2550	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	6198	2070	2815	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	6848	2070	2550	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	6848	2070	2815	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
```

## 下一步优先处理

1. 确认 Ktype `152815` 的 dCi 165 前驱厢式车具体 L/H 分支，并关联现有 X62B 前驱组。
2. 批量闭合 X62B 前驱与后驱底盘驾驶室 Ktype。
3. 闭合 All-New Interstar 柴油及电动底盘驾驶室分支。
4. 处理 X70 客车、Cabstar F24 与 Elgrand E52。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/interstar/m1-m2/323254/?utm_source=chatgpt.com "Nissan Interstar Kastenwagen L1H1 3,3t dCi 150 Tekna (12/21 - 10/24): Technische Daten, Bilder, Preise | ADAC"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* 闭合 Interstar II `X62B` 前驱底盘驾驶室的单排 L2/L3、双排 L2/L3 四种外廓，并关联 dCi 145、dCi 165 Ktype。日产 2022 年资料明确区分单排/双排驾驶室及对应长度、高度，宽度均为不含后视镜的 2070 mm。
* 闭合 All-New Interstar `XDE` 前驱底盘驾驶室的单排 L2/L3及双排 L3 外廓。柴油 dCi 130/150/170 覆盖三个分支；Interstar-e 仅关联单排 L2/L3。
* Ktype `152815` 已关联现有 X62B 前驱厢式车 L2H2、L2H3、L3H2、L3H3 四组，不重复输出已有尺寸组。([AIC 德国][1])

## 当前批次进度

* READY 输入 Ktype：83 / 100
* READY 映射：147 行
* PENDING 输入 Ktype：17
* 已确认尺寸组：52
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800287_sc_l2	800287	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800287_sc_l3	800287	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800287_dc_l3	800287	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
146150_sc_l2	146150	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
146150_sc_l3	146150	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
146150_dc_l2	146150	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	MEDIUM	前驱双排驾驶室L2底盘。	READY
146150_dc_l3	146150	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
800288_sc_l2	800288	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800288_sc_l3	800288	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800288_dc_l3	800288	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
146151_sc_l2	146151	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
146151_sc_l3	146151	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
146151_dc_l2	146151	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	MEDIUM	前驱双排驾驶室L2底盘。	READY
146151_dc_l3	146151	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
152815_l2h2	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
152815_l2h3	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	MEDIUM	L2H3前驱高顶厢式车外廓。	READY
152815_l3h2	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
152815_l3h3	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
800289_sc_l2	800289	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800289_sc_l3	800289	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800289_dc_l3	800289	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
800986_sc_l2	800986	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	电动前驱单排驾驶室L2底盘。	READY
800986_sc_l3	800986	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	电动前驱单排驾驶室L3底盘。	READY
800987_sc_l2	800987	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	电动前驱单排驾驶室L2底盘。	READY
800987_sc_l3	800987	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	电动前驱单排驾驶室L3底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	5730	2080	2257	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	6360	2080	2257	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	6360	2080	2362	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	5549	2070	2265	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	6199	2070	2258	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	5549	2070	2272	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	6199	2070	2263	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
```

## 下一步优先处理

1. 闭合 X62B 后驱底盘驾驶室 dCi 130、145、165 的 SRW/DRW、单排/双排和 L2–L4 分支。
2. 闭合 All-New Interstar `XDE` 后驱双后轮 L3/L4 底盘分支。
3. 关联 X70 客车与 dCi 90 厢式车到现有 X70 外廓组。
4. 最后处理 Cabstar F24 与 Elgrand E52。

推进信号：CONTINUE

[1]: https://www.aic-germany.de/de/produktkatalog/13139?utm_source=chatgpt.com "Der Produktkatalog von AIC Germany"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
## 更新点

* 首次闭合 Interstar II `X62B` 后驱单排底盘驾驶室的 L2 SRW、L2 DRW、L3 SRW、L3 DRW、L4 DRW 五个物理分支。官方资料区分单后轮与双后轮，并分别给出长度、不含后视镜宽度和高度。
* dCi 130、dCi 145、dCi 165 RWD 三个 Ktype 已批量关联上述新尺寸组。

## 当前批次进度

* READY 输入 Ktype：86 / 100
* READY 映射：162 行
* PENDING 输入 Ktype：14
* 已确认尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146153_sc_l2_srw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146153_sc_l2_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146153_sc_l3_srw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146153_sc_l3_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146153_sc_l4_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
146154_sc_l2_srw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146154_sc_l2_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146154_sc_l3_srw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146154_sc_l3_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146154_sc_l4_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
146157_sc_l2_srw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146157_sc_l2_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146157_sc_l3_srw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146157_sc_l3_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146157_sc_l4_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	5549	2070	2284	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	5549	2070	2284	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	6199	2070	2283	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	6099	2070	2276	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	6749	2070	2273	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
```

## 下一步优先处理

1. 闭合 2025 年 All-New Interstar 后驱底盘驾驶室 Ktype `802484`、`802485`。
2. 关联 Interstar X70 客车与 dCi 90 厢式车分支。
3. 集中处理 Cabstar F24 的驾驶室、轴距及底盘外廓。
4. 最后解决 Elgrand E52 的原厂外部套件分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / checkpoint 续跑 ---
## 更新点

* 闭合 All-New Interstar `XDE` 后驱双后轮底盘驾驶室：dCi 150 与 dCi 170 均拆分为单排/双排、L3/L4 四个分支。官方技术表给出 L3/L4 总长分别为 6360/6955 mm，单排车高 2257 mm、双排车高 2362 mm；后驱版本均为双后轮。
* Ktype `16951` 已关联现有 Interstar X70 厢式车四个尺寸组；本轮未重复输出既有尺寸事实。dCi 90 存在短、中、长轴及长轴不同车顶版本，外廓尺寸沿用已闭合的 X70 车身组。

## 当前批次进度

* READY 输入 Ktype：89 / 100
* READY 映射：174 行
* PENDING 输入 Ktype：11
* 已确认尺寸组：61
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
802484_sc_l3_drw	802484	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	HIGH	后驱单排驾驶室L3双后轮底盘。	READY
802484_sc_l4_drw	802484	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	HIGH	后驱单排驾驶室L4双后轮底盘。	READY
802484_dc_l3_drw	802484	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	HIGH	后驱双排驾驶室L3双后轮底盘。	READY
802484_dc_l4_drw	802484	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	HIGH	后驱双排驾驶室L4双后轮底盘。	READY
802485_sc_l3_drw	802485	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	HIGH	后驱单排驾驶室L3双后轮底盘。	READY
802485_sc_l4_drw	802485	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	HIGH	后驱单排驾驶室L4双后轮底盘。	READY
802485_dc_l3_drw	802485	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	HIGH	后驱双排驾驶室L3双后轮底盘。	READY
802485_dc_l4_drw	802485	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	HIGH	后驱双排驾驶室L4双后轮底盘。	READY
16951_l1h1	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	MEDIUM	L1H1厢式车外廓。	READY
16951_l2h2	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	MEDIUM	L2H2厢式车外廓。	READY
16951_l3h2	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	MEDIUM	L3H2厢式车外廓。	READY
16951_l3h3	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	6360	2080	2257	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	6955	2080	2257	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	6360	2080	2362	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	6955	2080	2362	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
```

## 下一步优先处理

1. 闭合 Interstar X70 的 dCi 80、dCi 90、dCi 115、dCi 140 客车分支。
2. 集中拆分 Cabstar F24 六个 Ktype 的单排/双排及 2500、2900、3400 mm 轴距底盘。
3. 最后闭合 Elgrand E52 的标准车身、Urban Chrome及历次改款外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / checkpoint 续跑 ---
## 更新点

* 已闭合 Interstar X70 客车分支：dCi 80 关联短轴低顶；dCi 115 关联中轴中顶、长轴中顶和长轴高顶；dCi 140 关联长轴中顶和长轴高顶。dCi 90 按该 Ktype 覆盖范围关联四个既有 X70 外廓组，不重复建立尺寸组。日产规格表明确列出 X70 的四种外廓及相应动力可用范围。
* 已闭合 Cabstar F24 六个 Ktype。按单排/双排、轴距、SRW/DRW 和 GVW 导致的车高差异拆分；`.12`、`.14` 动力版本复用相同 GVW、驾驶室、轴距及轮胎结构对应的 F24 外廓。日产 F24 官方手册明确给出不含后视镜宽度、底盘长度和高度。
* Elgrand E52 已补入一条 PENDING 基础行，尚待闭合改款前标准、Urban Chrome 与改款后长度边界。

## 当前批次进度

* READY 输入 Ktype：99 / 100
* READY 映射：235 行
* PENDING 输入 Ktype：1
* PENDING 映射：1 行
* 已确认尺寸组：76
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16947_l1h1	16947	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	dCi 80短轴低顶客车外廓。	READY
16948_l1h1	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	MEDIUM	短轴低顶客车外廓。	READY
16948_l2h2	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	MEDIUM	中轴中顶客车外廓。	READY
16948_l3h2	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	MEDIUM	长轴中顶客车外廓。	READY
16948_l3h3	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	MEDIUM	长轴高顶客车外廓。	READY
16949_l2h2	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	dCi 115中轴中顶客车外廓。	READY
16949_l3h2	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	dCi 115长轴中顶客车外廓。	READY
16949_l3h3	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	dCi 115长轴高顶客车外廓。	READY
18104_l3h2	18104	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	dCi 140长轴中顶客车外廓。	READY
18104_l3h3	18104	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	dCi 140长轴高顶客车外廓。	READY
50635_28_sc_l1_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	HIGH	28系列单排L1单后轮底盘。	READY
50635_28_sc_l2_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	HIGH	28系列单排L2单后轮底盘。	READY
50635_32_sc_l1_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	HIGH	32系列单排L1单后轮底盘。	READY
50635_32_sc_l2_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	HIGH	32系列单排L2单后轮底盘。	READY
50635_32_sc_l3_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	HIGH	32系列单排L3单后轮底盘。	READY
50635_35_sc_l1_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
50635_35_sc_l2_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
50635_35_sc_l3_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119611_28_sc_l1_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	MEDIUM	28系列单排L1单后轮底盘。	READY
119611_28_sc_l2_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	MEDIUM	28系列单排L2单后轮底盘。	READY
119611_32_34_sc_l1_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	MEDIUM	32/34系列单排L1单后轮底盘。	READY
119611_32_34_sc_l2_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	MEDIUM	32/34系列单排L2单后轮底盘。	READY
119611_32_34_sc_l3_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	MEDIUM	32/34系列单排L3单后轮底盘。	READY
119611_35_sc_l1_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119611_35_sc_l2_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119611_35_sc_l3_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119607_35_sc_l1_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
119607_35_sc_l2_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
119607_35_sc_l3_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119607_35_dc_l2_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	HIGH	35系列双排L2双后轮底盘。	READY
119607_35_dc_l3_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	HIGH	35系列双排L3双后轮底盘。	READY
119607_45_sc_l1_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	HIGH	45系列单排L1双后轮底盘。	READY
119607_45_sc_l2_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	HIGH	45系列单排L2双后轮底盘。	READY
119607_45_sc_l3_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	HIGH	45系列单排L3双后轮底盘。	READY
119607_45_dc_l2_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	HIGH	45系列双排L2双后轮底盘。	READY
119607_45_dc_l3_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	HIGH	45系列双排L3双后轮底盘。	READY
119609_35_sc_l1_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119609_35_sc_l2_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119609_35_sc_l3_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119609_35_dc_l2_drw	119609	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	MEDIUM	35系列双排L2双后轮底盘。	READY
119609_35_dc_l3_drw	119609	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	MEDIUM	35系列双排L3双后轮底盘。	READY
119612_35_sc_l1_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119612_35_sc_l2_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119612_35_sc_l3_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119612_35_dc_l2_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	MEDIUM	35系列双排L2双后轮底盘。	READY
119612_35_dc_l3_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	MEDIUM	35系列双排L3双后轮底盘。	READY
119612_45_sc_l1_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	MEDIUM	45系列单排L1双后轮底盘。	READY
119612_45_sc_l2_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	MEDIUM	45系列单排L2双后轮底盘。	READY
119612_45_sc_l3_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	MEDIUM	45系列单排L3双后轮底盘。	READY
119612_45_dc_l2_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	MEDIUM	45系列双排L2双后轮底盘。	READY
119612_45_dc_l3_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	MEDIUM	45系列双排L3双后轮底盘。	READY
119610_35_sc_l1_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
119610_35_sc_l2_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
119610_35_sc_l3_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119610_35_dc_l2_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	HIGH	35系列双排L2双后轮底盘。	READY
119610_35_dc_l3_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	HIGH	35系列双排L3双后轮底盘。	READY
119610_45_sc_l1_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	HIGH	45系列单排L1双后轮底盘。	READY
119610_45_sc_l2_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	HIGH	45系列单排L2双后轮底盘。	READY
119610_45_sc_l3_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	HIGH	45系列单排L3双后轮底盘。	READY
119610_45_dc_l2_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	HIGH	45系列双排L2双后轮底盘。	READY
119610_45_dc_l3_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	HIGH	45系列双排L3双后轮底盘。	READY
51940	51940	MPV	Elgrand III	PE52	5		LOW	候选分支为改款前标准、Urban Chrome及改款后外廓。	PENDING: 原厂外部套件长度边界待闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	4545	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	4545	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	5245	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	6045	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	4545	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	6045	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	6045	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	4745	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	5445	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	6345	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	5445	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	6345	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
```

## 下一步优先处理

1. 仅闭合 Ktype `51940` 的 Elgrand E52 改款前标准、Urban Chrome 与改款后外廓。
2. PENDING 清零后立即执行一次机械检查，生成两张完整 TSV 和两个指定 sandbox 下载文件。

推进信号：CONTINUE


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11601-11700_ktype_dimension_mapping_final.tsv
- left18448_11601-11700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / checkpoint 续跑 ---
## 更新点

* 最后一个阻塞 Ktype `51940` 已闭合：E52 改款前标准外廓为 `4915×1850×1815 mm`；2014 年后标准外廓为 `4945×1850×1815 mm`；Urban Chrome 外部套件为 `4975×1850×1815 mm`；第二次改款标准外廓为 `4965×1850×1815 mm`。([日産历史][1])
* 已完成机械检查：固定表头正确、100 个输入 Ktype 全覆盖、239 个映射 `id` 唯一、80 个尺寸组唯一、引用闭合、无孤立尺寸组、尺寸与来源字段完整、全部映射为 `READY`。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：239
* PENDING 映射：0
* DIMENSION_GROUP：80
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5991	5991	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-HATCHBACK-3D-01	HIGH	N15 GTI仅三门。	READY
14915_prefl	14915	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	MEDIUM	该Ktype跨越2002年改款，按改款前外廓拆分。	READY
14915_facelift	14915	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越2002年改款，按改款后外廓拆分。	READY
17242	17242	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
15110	15110	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	HIGH	N16四门轿车。	READY
17243	17243	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17244	17244	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17683	17683	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
17684	17684	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	HIGH	N16四门轿车。	READY
14916	14916	Sedan	Almera II	N16	4	EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	HIGH	N16四门轿车。	READY
14657_3dr_prefl	14657	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_5dr_prefl	14657	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_3dr_facelift	14657	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
14657_5dr_facelift	14657	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支并跨越2002年改款。	READY
17239_3dr	17239	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17239_5dr	17239	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14658_3dr	14658	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14658_5dr	14658	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17240_3dr	17240	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17240_5dr	17240	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17241_3dr	17241	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17241_5dr	17241	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17681_3dr	17681	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17681_5dr	17681	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17682_3dr	17682	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
17682_5dr	17682	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14659_3dr	14659	Hatchback	Almera II	N16	3	EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
14659_5dr	14659	Hatchback	Almera II	N16	5	EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	MEDIUM	该Ktype覆盖三门/五门分支。	READY
11262	11262	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17690	17690	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
11263	11263	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
14917	14917	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17685	17685	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
17686	17686	MPV	Almera Tino	V10	5	EU-NISSAN-ALMERA-TINO-MPV-01	HIGH	V10五门MPV。	READY
144397	144397	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144398	144398	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144399	144399	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144400	144400	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
144403	144403	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-SUV-01	HIGH	FE0标准车身。	READY
801088	801088	SUV	Ariya I	FE0	5	EU-NISSAN-ARIYA-FE0-NISMO-SUV-02	HIGH	NISMO专属外部套件。	READY
125847	125847	Sedan	Bluebird Sylphy III	B17	4	EU-NISSAN-BLUEBIRD-SYLPHY-B17-SEDAN-01	HIGH		READY
10679_610	10679	Sedan	Bluebird 610	610	4	EU-NISSAN-BLUEBIRD-610-SEDAN-01	HIGH	该Ktype跨越610与810两代四门轿车。	READY
10679_810	10679	Sedan	Bluebird 810	810	4	EU-NISSAN-BLUEBIRD-810-SEDAN-01	HIGH	该Ktype跨越610与810两代四门轿车。	READY
125980_prefl	125980	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-PREFL-01	HIGH	该Ktype跨越T12/T72外观改款，按改款前外廓拆分。	READY
125980_facelift	125980	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-FACELIFT-01	HIGH	该Ktype跨越T12/T72外观改款，按改款后外廓拆分。	READY
17015	17015	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-01	HIGH		READY
50635_28_sc_l1_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	HIGH	28系列单排L1单后轮底盘。	READY
50635_28_sc_l2_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	HIGH	28系列单排L2单后轮底盘。	READY
50635_32_sc_l1_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	HIGH	32系列单排L1单后轮底盘。	READY
50635_32_sc_l2_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	HIGH	32系列单排L2单后轮底盘。	READY
50635_32_sc_l3_srw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	HIGH	32系列单排L3单后轮底盘。	READY
50635_35_sc_l1_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
50635_35_sc_l2_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
50635_35_sc_l3_drw	50635	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119611_28_sc_l1_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	MEDIUM	28系列单排L1单后轮底盘。	READY
119611_28_sc_l2_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	MEDIUM	28系列单排L2单后轮底盘。	READY
119611_32_34_sc_l1_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	MEDIUM	32/34系列单排L1单后轮底盘。	READY
119611_32_34_sc_l2_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	MEDIUM	32/34系列单排L2单后轮底盘。	READY
119611_32_34_sc_l3_srw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	MEDIUM	32/34系列单排L3单后轮底盘。	READY
119611_35_sc_l1_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119611_35_sc_l2_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119611_35_sc_l3_drw	119611	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119607_35_sc_l1_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
119607_35_sc_l2_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
119607_35_sc_l3_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119607_35_dc_l2_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	HIGH	35系列双排L2双后轮底盘。	READY
119607_35_dc_l3_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	HIGH	35系列双排L3双后轮底盘。	READY
119607_45_sc_l1_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	HIGH	45系列单排L1双后轮底盘。	READY
119607_45_sc_l2_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	HIGH	45系列单排L2双后轮底盘。	READY
119607_45_sc_l3_drw	119607	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	HIGH	45系列单排L3双后轮底盘。	READY
119607_45_dc_l2_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	HIGH	45系列双排L2双后轮底盘。	READY
119607_45_dc_l3_drw	119607	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	HIGH	45系列双排L3双后轮底盘。	READY
119609_35_sc_l1_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119609_35_sc_l2_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119609_35_sc_l3_drw	119609	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119609_35_dc_l2_drw	119609	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	MEDIUM	35系列双排L2双后轮底盘。	READY
119609_35_dc_l3_drw	119609	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	MEDIUM	35系列双排L3双后轮底盘。	READY
119612_35_sc_l1_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	MEDIUM	35系列单排L1双后轮底盘。	READY
119612_35_sc_l2_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	MEDIUM	35系列单排L2双后轮底盘。	READY
119612_35_sc_l3_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	MEDIUM	35系列单排L3双后轮底盘。	READY
119612_35_dc_l2_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	MEDIUM	35系列双排L2双后轮底盘。	READY
119612_35_dc_l3_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	MEDIUM	35系列双排L3双后轮底盘。	READY
119612_45_sc_l1_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	MEDIUM	45系列单排L1双后轮底盘。	READY
119612_45_sc_l2_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	MEDIUM	45系列单排L2双后轮底盘。	READY
119612_45_sc_l3_drw	119612	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	MEDIUM	45系列单排L3双后轮底盘。	READY
119612_45_dc_l2_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	MEDIUM	45系列双排L2双后轮底盘。	READY
119612_45_dc_l3_drw	119612	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	MEDIUM	45系列双排L3双后轮底盘。	READY
119610_35_sc_l1_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	HIGH	35系列单排L1双后轮底盘。	READY
119610_35_sc_l2_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	HIGH	35系列单排L2双后轮底盘。	READY
119610_35_sc_l3_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	HIGH	35系列单排L3双后轮底盘。	READY
119610_35_dc_l2_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	HIGH	35系列双排L2双后轮底盘。	READY
119610_35_dc_l3_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	HIGH	35系列双排L3双后轮底盘。	READY
119610_45_sc_l1_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	HIGH	45系列单排L1双后轮底盘。	READY
119610_45_sc_l2_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	HIGH	45系列单排L2双后轮底盘。	READY
119610_45_sc_l3_drw	119610	Pickup	Cabstar F24	F24	2	EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	HIGH	45系列单排L3双后轮底盘。	READY
119610_45_dc_l2_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	HIGH	45系列双排L2双后轮底盘。	READY
119610_45_dc_l3_drw	119610	Pickup	Cabstar F24	F24	4	EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	HIGH	45系列双排L3双后轮底盘。	READY
59711	59711	Sedan	Cedric Y31	Y31	4	EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	HIGH	四门硬顶轿车。	READY
59712	59712	Sedan	Cedric Y32	Y32	4	EU-NISSAN-CEDRIC-Y32-HARDTOP-SEDAN-01	HIGH	四门硬顶轿车。	READY
10680_2dr	10680	Sedan	Cherry I	E10	2	EU-NISSAN-CHERRY-E10-SEDAN-2D-01	MEDIUM	E10车型条目覆盖二门与四门轿车，按门数拆分。	READY
10680_4dr	10680	Sedan	Cherry I	E10	4	EU-NISSAN-CHERRY-E10-SEDAN-4D-01	MEDIUM	E10车型条目覆盖二门与四门轿车，按门数拆分。	READY
10660	10660	Sedan	Datsun 140J 710	710	4	EU-NISSAN-DATSUN-140J-710-SEDAN-01	MEDIUM	710系列四门出口轿车。	READY
10661	10661	Sedan	Datsun 160J 710	710	4	EU-NISSAN-DATSUN-160J-710-SEDAN-01	MEDIUM	710系列四门出口轿车。	READY
51940_prefl	51940	MPV	Elgrand III	PE52	5	EU-NISSAN-ELGRAND-E52-MPV-PREFL-01	HIGH	2010至2014年改款前标准外廓。	READY
51940_facelift	51940	MPV	Elgrand III	PE52	5	EU-NISSAN-ELGRAND-E52-MPV-FACELIFT-01	HIGH	2014年改款后标准外廓。	READY
51940_urban_chrome	51940	MPV	Elgrand III	PE52	5	EU-NISSAN-ELGRAND-E52-MPV-URBAN-CHROME-01	HIGH	Urban Chrome前后外部套件外廓。	READY
51940_restyle	51940	MPV	Elgrand III	PE52	5	EU-NISSAN-ELGRAND-E52-MPV-RESTYLE-01	HIGH	2020年第二次改款标准外廓。	READY
34714	34714	Convertible	Figaro	FK10	2	EU-NISSAN-FIGARO-FK10-CONVERTIBLE-01	HIGH	输入BodyStyle为Coupe；实际为双门敞篷车身。	READY
107483	107483	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-NISMO-COUPE-01	HIGH	NISMO专属前后外部套件。	READY
55403	55403	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	2012款标准外廓。	READY
113192	113192	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-PREFL-01	HIGH	2013款标准外廓。	READY
121620	121620	Coupe	GT-R R35	R35	2	EU-NISSAN-GT-R-R35-COUPE-FACELIFT-01	HIGH	2017款改款后标准外廓。	READY
18105_l1h1	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
18105_l2h2	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
18105_l3h2	18105	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158681_l2h2	158681	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	MEDIUM	L2H2厢式车外廓。	READY
146146_l1h1	146146	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146146_l2h2	146146	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
16949_l2h2	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	dCi 115中轴中顶客车外廓。	READY
16949_l3h2	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	dCi 115长轴中顶客车外廓。	READY
16949_l3h3	16949	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	dCi 115长轴高顶客车外廓。	READY
16952_l2h2	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
16952_l3h2	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
16952_l3h3	16952	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
158682_l2h2	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158682_l3h2	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158682_l3h3	158682	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
800287_sc_l2	800287	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800287_sc_l3	800287	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800287_dc_l3	800287	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
146152_l3h2	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146152_l3h3	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146152_l4h2	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146152_l4h3	146152	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146153_sc_l2_srw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146153_sc_l2_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146153_sc_l3_srw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146153_sc_l3_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146153_sc_l4_drw	146153	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
146147_l1h1	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146147_l2h2	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146147_l2h3	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	MEDIUM	L2H3前驱高顶厢式车外廓。	READY
146147_l3h2	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146147_l3h3	146147	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
18103_l3h2	18103	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
18103_l3h3	18103	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
18104_l3h2	18104	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	HIGH	dCi 140长轴中顶客车外廓。	READY
18104_l3h3	18104	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	HIGH	dCi 140长轴高顶客车外廓。	READY
146150_sc_l2	146150	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
146150_sc_l3	146150	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
146150_dc_l2	146150	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	MEDIUM	前驱双排驾驶室L2底盘。	READY
146150_dc_l3	146150	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
146154_sc_l2_srw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146154_sc_l2_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146154_sc_l3_srw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146154_sc_l3_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146154_sc_l4_drw	146154	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
146155_l3h2	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146155_l3h3	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146155_l4h2	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146155_l4h3	146155	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146148_l1h1	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146148_l2h2	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146148_l3h2	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146148_l3h3	146148	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
158683_l2h2	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158683_l3h2	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158683_l3h3	158683	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	HIGH	L3H3高顶厢式车外廓。	READY
800288_sc_l2	800288	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800288_sc_l3	800288	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800288_dc_l3	800288	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
802484_sc_l3_drw	802484	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	HIGH	后驱单排驾驶室L3双后轮底盘。	READY
802484_sc_l4_drw	802484	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	HIGH	后驱单排驾驶室L4双后轮底盘。	READY
802484_dc_l3_drw	802484	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	HIGH	后驱双排驾驶室L3双后轮底盘。	READY
802484_dc_l4_drw	802484	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	HIGH	后驱双排驾驶室L4双后轮底盘。	READY
146151_sc_l2	146151	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
146151_sc_l3	146151	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
146151_dc_l2	146151	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	MEDIUM	前驱双排驾驶室L2底盘。	READY
146151_dc_l3	146151	Pickup	Interstar II	X62B	4	EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
152815_l2h2	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
152815_l2h3	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	MEDIUM	L2H3前驱高顶厢式车外廓。	READY
152815_l3h2	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
152815_l3h3	152815	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
146156_l3h2	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	MEDIUM	L3H2后驱厢式车外廓。	READY
146156_l3h3	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	MEDIUM	L3H3后驱高顶厢式车外廓。	READY
146156_l4h2	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	MEDIUM	L4H2后驱加长厢式车外廓。	READY
146156_l4h3	146156	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	MEDIUM	L4H3后驱加长高顶厢式车外廓。	READY
146157_sc_l2_srw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	MEDIUM	后驱单排驾驶室L2单后轮底盘。	READY
146157_sc_l2_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	MEDIUM	后驱单排驾驶室L2双后轮底盘。	READY
146157_sc_l3_srw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	MEDIUM	后驱单排驾驶室L3单后轮底盘。	READY
146157_sc_l3_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	MEDIUM	后驱单排驾驶室L3双后轮底盘。	READY
146157_sc_l4_drw	146157	Pickup	Interstar II	X62B	2	EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	MEDIUM	后驱单排驾驶室L4双后轮底盘。	READY
158684_l2h2	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
158684_l3h2	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
158684_l3h3	158684	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
800289_sc_l2	800289	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	前驱单排驾驶室L2底盘。	READY
800289_sc_l3	800289	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	前驱单排驾驶室L3底盘。	READY
800289_dc_l3	800289	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	MEDIUM	前驱双排驾驶室L3底盘。	READY
802485_sc_l3_drw	802485	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	HIGH	后驱单排驾驶室L3双后轮底盘。	READY
802485_sc_l4_drw	802485	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	HIGH	后驱单排驾驶室L4双后轮底盘。	READY
802485_dc_l3_drw	802485	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	HIGH	后驱双排驾驶室L3双后轮底盘。	READY
802485_dc_l4_drw	802485	Pickup	All-New Interstar	XDE	4	EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	HIGH	后驱双排驾驶室L4双后轮底盘。	READY
146149_l1h1	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	MEDIUM	L1H1前驱厢式车外廓。	READY
146149_l2h2	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	MEDIUM	L2H2前驱厢式车外廓。	READY
146149_l3h2	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	MEDIUM	L3H2前驱厢式车外廓。	READY
146149_l3h3	146149	Van	Interstar II	X62B		EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	MEDIUM	L3H3前驱高顶厢式车外廓。	READY
16947_l1h1	16947	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	dCi 80短轴低顶客车外廓。	READY
16950	16950	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
16948_l1h1	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	MEDIUM	短轴低顶客车外廓。	READY
16948_l2h2	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	MEDIUM	中轴中顶客车外廓。	READY
16948_l3h2	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	MEDIUM	长轴中顶客车外廓。	READY
16948_l3h3	16948	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	MEDIUM	长轴高顶客车外廓。	READY
16951_l1h1	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	MEDIUM	L1H1厢式车外廓。	READY
16951_l2h2	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	MEDIUM	L2H2厢式车外廓。	READY
16951_l3h2	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	MEDIUM	L3H2厢式车外廓。	READY
16951_l3h3	16951	Van	Interstar I	X70		EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	MEDIUM	L3H3高顶厢式车外廓。	READY
800285_l2h2	800285	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2电动厢式车外廓。	READY
800285_l3h2	800285	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2电动厢式车外廓。	READY
800286_l2h2	800286	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	HIGH	L2H2电动厢式车外廓。	READY
800286_l3h2	800286	Van	All-New Interstar			EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	HIGH	L3H2电动厢式车外廓。	READY
800986_sc_l2	800986	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	电动前驱单排驾驶室L2底盘。	READY
800986_sc_l3	800986	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	电动前驱单排驾驶室L3底盘。	READY
800987_sc_l2	800987	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	MEDIUM	电动前驱单排驾驶室L2底盘。	READY
800987_sc_l3	800987	Pickup	All-New Interstar	XDE	2	EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	MEDIUM	电动前驱单排驾驶室L3底盘。	READY
34721	34721	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
59302	59302	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
142860	142860	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
106276	106276	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34725	34725	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34724	34724	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
34723	34723	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
58599	58599	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO外部套件。	READY
53454	53454	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO外部套件。	READY
107628	107628	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO RS外部套件。	READY
108986	108986	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-NISMO-SUV-01	HIGH	NISMO RS外部套件。	READY
148232	148232	SUV	Juke II	F16	5	EU-NISSAN-JUKE-F16-HYBRID-SUV-01	HIGH		READY
126913	126913	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	HIGH		READY
142859	142859	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
142928	142928	SUV	Juke I	F15	5	EU-NISSAN-JUKE-F15-SUV-01	MEDIUM	商用登记不改变F15外部轮廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_11601-11700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-ALMERA-I-HATCHBACK-3D-01	4120	1690	1395	Automobile-Catalog 1998 Nissan Almera 2.0 GTi specifications	https://www.automobile-catalog.com/car/1998/2252525/nissan_almera_2_0_gti.html
EU-NISSAN-ALMERA-II-SEDAN-PREFL-01	4425	1695	1445	Automobile-Catalog 2000 Nissan Almera Sedan 1.5 Base specifications	https://www.automobile-catalog.com/car/2000/2283380/nissan_almera_sedan_1_5_base.html
EU-NISSAN-ALMERA-II-SEDAN-FACELIFT-01	4435	1695	1445	Automobile-Catalog 2004 Nissan Almera Sedan 1.5 Acenta specifications	https://www.automobile-catalog.com/car/2004/2283605/nissan_almera_sedan_1_5_acenta.html
EU-NISSAN-ALMERA-II-HATCHBACK-3D-PREFL-01	4184	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2000 Nissan Almera 1.5 Base specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2000/2283305/nissan_almera_1_5_base.html
EU-NISSAN-ALMERA-II-HATCHBACK-5D-PREFL-01	4184	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2000 Nissan Almera 1.5 Base specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2000/2283305/nissan_almera_1_5_base.html
EU-NISSAN-ALMERA-II-HATCHBACK-3D-FACELIFT-01	4197	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2003 Nissan Almera 1.5 Acenta specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2003/2283455/nissan_almera_1_5_acenta.html
EU-NISSAN-ALMERA-II-HATCHBACK-5D-FACELIFT-01	4197	1706	1448	Nissan Almera electronic brochure; Automobile-Catalog 2003 Nissan Almera 1.5 Acenta specifications	https://xr793.com/wp-content/uploads/2022/10/2007-Nissan-Almera-UK.pdf;https://www.automobile-catalog.com/car/2003/2283455/nissan_almera_1_5_acenta.html
EU-NISSAN-ALMERA-TINO-MPV-01	4264	1758	1608	Automobile-Catalog 2003 Nissan Almera Tino 1.8 Acenta specifications	https://www.automobile-catalog.com/car/2003/2285660/nissan_almera_tino_1_8_acenta_automatic.html
EU-NISSAN-ARIYA-FE0-SUV-01	4595	1850	1660	Nissan ARIYA official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Ariya_UK.pdf
EU-NISSAN-ARIYA-FE0-NISMO-SUV-02	4655	1850	1660	Nissan ARIYA NISMO official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_ARIYA_NISMO_UK.pdf
EU-NISSAN-BLUEBIRD-SYLPHY-B17-SEDAN-01	4615	1760	1495	Nissan Sylphy official brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/ph/brochures/Sylphy_DigitalBrochure.pdf
EU-NISSAN-BLUEBIRD-610-SEDAN-01	4215	1600	1405	Nissan Heritage Collection Datsun Bluebird U 1600GL	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/bluebird_u_1600gl.html
EU-NISSAN-BLUEBIRD-810-SEDAN-01	4260	1630	1390	Automobile-Catalog 1977 Datsun Bluebird 180B Sedan; Bind Nissan Bluebird 810 1.8 AT specifications	https://www.automobile-catalog.com/car/1977/35720/datsun_bluebird_180_b.html;https://bind.lt/en/technical-specifications/nissan/bluebird-1/810-restyling/sedan/1-8-at-88-hp
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-PREFL-01	4365	1690	1395	Automobile-Catalog 1987 Nissan Bluebird 1.8 GS 5-d specifications	https://www.automobile-catalog.com/car/1987/2236220/nissan_bluebird_1_8_gs_5-d.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-FACELIFT-01	4420	1690	1395	Automobile-Catalog 1990 Nissan Bluebird 1.8 GS 5-d specifications	https://www.automobile-catalog.com/car/1990/2236625/nissan_bluebird_1_8_gs_5-d.html
EU-NISSAN-BLUEBIRD-910-SEDAN-01	4395	1655	1400	Automobile-Catalog 1983 Datsun Bluebird 2.0 Turbo D specifications	https://www.automobile-catalog.com/car/1983/2120180/datsun_bluebird_2_0_turbo_d.html
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-28-01	4545	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-28-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-SRW-32-34-01	4545	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-SRW-32-34-01	5245	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-SRW-32-34-01	6045	1870	2122	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-35-01	4545	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-35-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-35-01	6045	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-35-01	5245	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-35-01	6045	1870	2116	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L1-DRW-45-01	4745	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L2-DRW-45-01	5445	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-SC-L3-DRW-45-01	6345	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L2-DRW-45-01	5445	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CABSTAR-F24-CHASSIS-DC-L3-DRW-45-01	6345	1870	2135	Nissan Cabstar F24 official owner manual	https://www.nissan-cdn.net/content/dam/Nissan/greece/manuals/cabstar/CABSTAR_F24_2008_JUNE.pdf
EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	4860	1720	1380	Automobile-Catalog 1988 Nissan Cedric V30 Turbo Brougham VIP Hardtop specifications	https://www.automobile-catalog.com/car/1988/2152115/nissan_cedric_4door_hardtop_v30_turbo_brougham_vip.html
EU-NISSAN-CEDRIC-Y32-HARDTOP-SEDAN-01	4780	1745	1410	Auto-Data Nissan Cedric Y32 3.0i V6 Turbo specifications	https://www.auto-data.net/en/nissan-cedric-y32-3.0i-v6-24v-turbo-255hp-automatic-919
EU-NISSAN-CHERRY-E10-SEDAN-2D-01	3610	1470	1380	Nissan Heritage Collection Cherry 2-door Deluxe	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/cherry_2door_deluxe.html
EU-NISSAN-CHERRY-E10-SEDAN-4D-01	3610	1470	1380	Automobile-Catalog 1970 Nissan Cherry 4Door DX specifications	https://www.automobile-catalog.com/car/1970/2091875/nissan_cherry_4door_deluxe_3-speed.html
EU-NISSAN-DATSUN-140J-710-SEDAN-01	4120	1580	1405	Automobile-Catalog 1975 Datsun 140J Deluxe specifications	https://www.automobile-catalog.com/car/1975/2094650/datsun_140j_deluxe.html
EU-NISSAN-DATSUN-160J-710-SEDAN-01	4120	1580	1395	Automobile-Catalog 1973 Datsun 160J Deluxe specifications	https://www.automobile-catalog.com/car/1973/2094725/datsun_160j_deluxe.html
EU-NISSAN-ELGRAND-E52-MPV-PREFL-01	4915	1850	1815	Nissan Elgrand E52 official historical grade specifications	https://history.nissan.co.jp/ELGRAND/E52/1008/e521008g52.html?gradeID=G52&model=ELGRAND
EU-NISSAN-ELGRAND-E52-MPV-FACELIFT-01	4945	1850	1815	Nissan Elgrand official 2018 specifications	https://www.nissan-cdn.net/content/dam/Nissan/jp/vehicles/elgrand/1801/pdf/elgrand_specification.pdf
EU-NISSAN-ELGRAND-E52-MPV-URBAN-CHROME-01	4975	1850	1815	Nissan Elgrand official 2018 specifications	https://www.nissan-cdn.net/content/dam/Nissan/jp/vehicles/elgrand/1801/pdf/elgrand_specification.pdf
EU-NISSAN-ELGRAND-E52-MPV-RESTYLE-01	4965	1850	1815	Nissan Hong Kong Elgrand Restyle official specifications	https://en.nissan.com.hk/vehicles/new/elgrand/specifications.html
EU-NISSAN-FIGARO-FK10-CONVERTIBLE-01	3740	1630	1365	Nissan Heritage Collection Figaro 1991 FK10	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/397_figaro.html
EU-NISSAN-GT-R-R35-NISMO-COUPE-01	4690	1895	1370	Nissan GT-R NISMO official specifications; Car Watch 2017 GT-R NISMO Europe specification report	https://www3.nissan.co.jp/content/dam/Nissan/jp/vehicles/GT-R/pdf/gt-r_nismo_specification.pdf;https://car.watch.impress.co.jp/docs/news/759581.html
EU-NISSAN-GT-R-R35-COUPE-PREFL-01	4670	1895	1370	Automobile-Catalog 2012 Nissan GT-R Black Edition specifications	https://www.automobile-catalog.com/car/2012/2182730/nissan_gt-r_black_edition.html
EU-NISSAN-GT-R-R35-COUPE-FACELIFT-01	4710	1895	1370	Nissan GT-R official brochure; Automobile-Catalog 2017 Nissan GT-R Europe specifications	https://www-asia.nissan-cdn.net/content/dam/Nissan/in/brochures/GT-R%20Brochure%20Final_Web.pdf;https://www.automobile-catalog.com/car/2017/2409620/nissan_gt-r.html
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L1H1-01	4899	1990	2256	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L2H2-01	5399	1990	2493	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H2-01	5899	1990	2490	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L2H2-01	5780	2080	2498	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L1H1-01	5048	2070	2307	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H2-01	5548	2070	2499	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X70-PANEL-VAN-L3H3-01	5899	1990	2720	Nissan Interstar 2004 official specifications brochure; Nissan Interstar official brochure	https://xr793.com/wp-content/uploads/2022/10/2004-Nissan-Interstar-Specs-UK.pdf;https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H2-01	6410	2080	2498	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
EU-NISSAN-INTERSTAR-ALL-NEW-PANEL-VAN-L3H3-01	6410	2080	2756	Nissan All-New Interstar official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Interstar_UK.pdf
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L2-01	5730	2080	2257	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-SC-L3-01	6360	2080	2257	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-FWD-DC-L3-01	6360	2080	2362	Nissan All-New Interstar official technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H2-01	6198	2070	2550	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L3H3-01	6198	2070	2815	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H2-01	6848	2070	2550	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-RWD-L4H3-01	6848	2070	2815	Nissan NV400 official brochure; Nissan Interstar 2022 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/dk/brochures/Nissan_NV400_DK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-SRW-01	5549	2070	2284	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L2-DRW-01	5549	2070	2284	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-SRW-01	6199	2070	2283	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L3-DRW-01	6099	2070	2276	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-RWD-SC-L4-DRW-01	6749	2070	2273	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L2H3-01	5548	2070	2749	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H2-01	6198	2070	2488	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-PANEL-VAN-FWD-L3H3-01	6198	2070	2744	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L2-01	5549	2070	2265	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-SC-L3-01	6199	2070	2258	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L2-01	5549	2070	2272	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-X62B-CHASSIS-FWD-DC-L3-01	6199	2070	2263	Nissan Interstar 2022 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/Interstar%20042022-compressed.pdf
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L3-DRW-01	6360	2080	2257	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-SC-L4-DRW-01	6955	2080	2257	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L3-DRW-01	6360	2080	2362	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-INTERSTAR-XDE-CHASSIS-RWD-DC-L4-DRW-01	6955	2080	2362	Nissan All-New Interstar official chassis technical sheet; Nissan Interstar official technical information	https://www-europe.nissan-cdn.net/content/dam/Nissan/fr/brochures/fiches_techniques/fiche_technique_Interstar_Fourgon_cabine_approfondie_chassis_plancher.pdf;https://www.nissan.hu/jarmuvek/uj/interstar/technical-information.html
EU-NISSAN-JUKE-F15-SUV-01	4135	1765	1565	Nissan JUKE official Australia brochure	https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Files/Brochures/Models/Juke/JUK0139r02_Nissan_JUKE_Brochure%20PDF.pdf
EU-NISSAN-JUKE-F15-NISMO-SUV-01	4165	1770	1565	Automobile-Catalog 2014 Nissan Juke Nismo Europe specifications; Automobile-Catalog 2015 Nissan Juke Nismo RS Europe specifications	https://www.automobile-catalog.com/car/2014/2320565/nissan_juke_nismo.html;https://www.automobile-catalog.com/car/2015/2321090/nissan_juke_nismo_rs.html
EU-NISSAN-JUKE-F16-HYBRID-SUV-01	4210	1800	1593	Nissan JUKE official UK brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Juke_UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_11601-11700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://history.nissan.co.jp/ELGRAND/E52/1008/e521008g52.html?gradeID=G52&model=ELGRAND "日産：エルグランド [ ELGRAND ] ミニバン/ワゴン ｜ グレード ｜ グレード詳細"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3031 行）
- 累计尺寸组：dimension_groups_final.tsv（938 行）

