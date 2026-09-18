# 任务：left18448 第 2601-2700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0027__d378e4f9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2601-2700 行

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
left18448 第 2601-2700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-BMW-7-E65-SEDAN-FACELIFT-01	5039	1902	1491
EU-BMW-7-E65-SEDAN-PREFL-01	5029	1902	1492
EU-BMW-7-E66-SEDAN-FACELIFT-01	5179	1902	1484
EU-BMW-7-E66-SEDAN-PREFL-01	5169	1902	1492
EU-BMW-7-F01-SEDAN-FACELIFT-01	5079	1902	1471
EU-BMW-7-F01-SEDAN-PREFL-01	5072	1902	1479
EU-BMW-7-G11-SEDAN-FACELIFT-01	5120	1902	1467
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1478
EU-BMW-7-G12-SEDAN-FACELIFT-01	5260	1902	1479
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1485
EU-BMW-7-G70-SEDAN-01	5391	1950	1544

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	7	740 D, LD Xdrive	Stufenheck	Allrad	Diesel	Nov 2015	Jun 2020	116787
BMW	7	740 E, LE	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2016	Feb 2019	119083
BMW	7	740 I, IL	Stufenheck	Heckantrieb	Benzin	Feb 1996	Jul 2001	5104
BMW	7	740 I, LI	Stufenheck	Heckantrieb	Benzin	Mar 2005	Aug 2008	18982
BMW	7	740 I, LI	Stufenheck	Heckantrieb	Benzin	Jul 2012	Dec 2015	55352
BMW	7	740 I, LI	Stufenheck	Heckantrieb	Benzin	Jul 2015	Feb 2019	114061
BMW	7	740 I, LI Mild Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2022	-	148086
BMW	7	740 I, LI Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Dec 2015	106004
BMW	7	740 I,li	Stufenheck	Heckantrieb	Benzin	Mar 2019	Jun 2022	146610
BMW	7	740 LE Xdrive	Stufenheck	Allrad	Benzin/Elektro	Jul 2016	Feb 2019	119085
BMW	7	740 LI Xdrive	Stufenheck	Allrad	Benzin	Mar 2016	Feb 2019	118190
BMW	7	740 LI Xdrive	Stufenheck	Allrad	Benzin	Mar 2019	Jun 2022	146604
BMW	7	740d Xdrive	Stufenheck	Allrad	Diesel/Elektro	Nov 2022	-	147484
BMW	7	745 D	Stufenheck	Heckantrieb	Diesel	Jul 2005	Jul 2008	18988
BMW	7	745 I, LI	Stufenheck	Heckantrieb	Benzin	Jul 2001	Mar 2005	16179
BMW	7	750 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2012	Dec 2015	55358
BMW	7	750 D, LD Xdrive	Stufenheck	Allrad	Diesel	Jul 2016	Oct 2020	120295
BMW	7	750 I, LI	Stufenheck	Heckantrieb	Benzin	Mar 2005	Aug 2008	18984
BMW	7	750 I, LI	Stufenheck	Heckantrieb	Benzin	Jul 2012	Jun 2015	57271
BMW	7	750 I, LI	Stufenheck	Heckantrieb	Benzin	Nov 2015	Feb 2019	116785
BMW	7	750 I, LI Xdrive	Stufenheck	Allrad	Benzin	Jul 2012	Jun 2015	57277
BMW	7	750 I, LI Xdrive	Stufenheck	Allrad	Benzin	Sep 2015	Feb 2019	114062
BMW	7	750e Plug-in Hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	Nov 2022	-	147487
BMW	7	760 I, LI	Stufenheck	Heckantrieb	Benzin	Jan 2003	Aug 2008	17151
BMW	7	Activehybrid 7	Stufenheck	Heckantrieb	Benzin/Elektro	Apr 2010	Jun 2012	5752
BMW	7	Activehybrid 7	Stufenheck	Heckantrieb	Benzin/Elektro	Aug 2012	Jun 2015	55360
BMW	7	I7 Edrive50, L	Stufenheck	Heckantrieb	Elektro	Apr 2023	-	153523
BMW	7	I7 M70 Xdrive	Stufenheck	Allrad	Elektro	Jul 2023	-	154577
BMW	7	I7 Xdrive60, L	Stufenheck	Allrad	Elektro	Jul 2022	-	147489
BMW	7	M 760 I, LI Xdrive	Stufenheck	Allrad	Benzin	Dec 2016	Feb 2019	120288
BMW	7	M 760e Plug-in Hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	Nov 2022	-	147488
BMW	7	Xdrive 760 I	Stufenheck	Allrad	Benzin/Elektro	Jul 2022	-	149410
BMW	8	840 CI	Coupe	Heckantrieb	Benzin	Mar 1996	Jun 1999	5107
BMW	8	840 I	Coupe	Heckantrieb	Benzin	Nov 2020	-	143023
BMW	8	840 I	Cabriolet	Heckantrieb	Benzin	Nov 2020	-	143025
BMW	8	840 I	Coupe	Heckantrieb	Benzin	Nov 2020	-	143027
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	Nov 2020	-	143024
BMW	8	840 I Xdrive	Cabriolet	Allrad	Benzin	Nov 2020	-	143026
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	Nov 2020	-	143028
BMW	315	315 2-fenster Cabrio	Cabriolet	Heckantrieb	Benzin	Apr 1934	Jun 1937	155792
BMW	315	315 4-fenster Cabrio	Cabriolet	Heckantrieb	Benzin	Apr 1934	Jun 1937	155793
BMW	315	315 Cabrio-limousine	Stufenheck	Heckantrieb	Benzin	Apr 1934	Jun 1937	155791
BMW	315	315 Limousine	Stufenheck	Heckantrieb	Benzin	Apr 1934	Jun 1937	155790
BMW	315	315 Tourenwagen	Cabriolet	Heckantrieb	Benzin	Apr 1934	Jun 1937	155794
BMW	319	319 2-fenster Cabrio	Cabriolet	Heckantrieb	Benzin	Dec 1934	Mar 1937	155811
BMW	319	319 4-fenster Cabrio	Cabriolet	Heckantrieb	Benzin	Dec 1934	Mar 1937	155812
BMW	319	319 Cabrio-limousine	Stufenheck	Heckantrieb	Benzin	Dec 1934	Mar 1937	155809
BMW	319	319 Limousine	Stufenheck	Heckantrieb	Benzin	Dec 1934	Mar 1937	155808
BMW	319	319 Tourenwagen	Cabriolet	Heckantrieb	Benzin	Dec 1934	Mar 1937	155813
BMW	320	320 4-fenster Cabriolet	Cabriolet	Heckantrieb	Benzin	Feb 1937	Sep 1937	155823
BMW	320	320 4-fenster Cabriolet	Cabriolet	Heckantrieb	Benzin	Mar 1937	Dec 1938	155824
BMW	320	320 Limousine	Stufenheck	Heckantrieb	Benzin	Feb 1937	Sep 1937	155821
BMW	320	320 Limousine	Stufenheck	Heckantrieb	Benzin	Mar 1937	Dec 1938	155822
BMW	320	320 Reutter-cabriolet	Cabriolet	Heckantrieb	Benzin	Mar 1938	Dec 1938	155825
BMW	321	321 4-fenster Cabriolet	Cabriolet	Heckantrieb	Benzin	Dec 1938	Apr 1941	155828
BMW	321	321 Limousine	Stufenheck	Heckantrieb	Benzin	Dec 1938	Apr 1941	155827
BMW	326	326 2-tür Cabriolet	Cabriolet	Heckantrieb	Benzin	Feb 1936	Apr 1941	155830
BMW	326	326 4-tür Cabriolet	Cabriolet	Heckantrieb	Benzin	Feb 1936	Apr 1941	155833
BMW	326	326 Limousine	Stufenheck	Heckantrieb	Benzin	Feb 1936	Apr 1941	155829
BMW	340	340	Stufenheck	Heckantrieb	Benzin	Oct 1949	Jun 1952	126152
BMW	501	2.1	Schrägheck	Heckantrieb	Benzin	Jul 1952	Jan 1959	8814
BMW	502	2.6	Stufenheck	Heckantrieb	Benzin	Sep 1954	Dec 1963	126142
BMW	502	3.2	Stufenheck	Heckantrieb	Benzin	Sep 1954	Dec 1963	126143
BMW	502	3.2 Super	Stufenheck	Heckantrieb	Benzin	Sep 1954	Dec 1963	126144
BMW	507	Touring Sport	Cabriolet	Heckantrieb	Benzin	Oct 1956	Jul 1959	126135
BMW	507	Touring Sport	Cabriolet	Heckantrieb	Benzin	Oct 1956	Jul 1959	126137
BMW	600	0.6	Schrägheck	Heckantrieb	Benzin	Dec 1957	May 1961	10584
BMW	700	0.7	Coupe	Heckantrieb	Benzin	Aug 1959	Apr 1964	16111
BMW	700	0.7	Stufenheck	Heckantrieb	Benzin	Jan 1959	Nov 1966	16113
BMW	700	0.7 A	Stufenheck	Heckantrieb	Benzin	Jan 1959	Nov 1966	8815
BMW	700	0.7 S	Coupe	Heckantrieb	Benzin	Aug 1959	Apr 1964	16112
BMW	1502-2002	1502	Stufenheck	Heckantrieb	Benzin	Jan 1975	Jul 1977	2
BMW	1502-2002	1602	Stufenheck	Heckantrieb	Benzin	Apr 1971	Jul 1975	4
BMW	1502-2002	1802	Stufenheck	Heckantrieb	Benzin	May 1971	Jul 1975	5
BMW	1502-2002	2002	Stufenheck	Heckantrieb	Benzin	Feb 1968	Jul 1975	6
BMW	1502-2002	2002	Cabriolet	Heckantrieb	Benzin	May 1971	Jul 1975	7
BMW	1502-2002	2002 TII	Stufenheck	Heckantrieb	Benzin	Apr 1971	Jun 1975	8
BMW	1502-2002	2002 Turbo	Stufenheck	Heckantrieb	Benzin	Jan 1974	Jul 1975	9
BMW	315 roadster	315/1	Cabriolet	Heckantrieb	Benzin	Apr 1934	Jul 1935	155795
BMW	319 roadster	319/1	Cabriolet	Heckantrieb	Benzin	Feb 1935	Jul 1936	155815
BMW	Glas	2600 V8	Stufenheck	Heckantrieb	Benzin	Sep 1967	May 1968	121988
BMW	Glas	3000 V8	Stufenheck	Heckantrieb	Benzin	Sep 1967	May 1968	121983
BMW	I3	50 Xdrive	Stufenheck	Allrad	Elektro	Mar 2026	-	164103
BMW	I3	Electric	Schrägheck	Heckantrieb	Elektro	Aug 2013	-	108045
BMW	I3	Range Extender	Schrägheck	Heckantrieb	Benzin/Elektro	Aug 2013	-	108046
BMW	I3	S Electric	Schrägheck	Heckantrieb	Elektro	Nov 2017	-	128458
BMW	I3	S Electric	Schrägheck	Heckantrieb	Elektro	Nov 2017	-	128460
BMW	I3	S Range Extender	Schrägheck	Heckantrieb	Benzin/Elektro	Nov 2017	-	128459
BMW	I8	Hybrid	Coupe	Allrad	Benzin/Elektro	Mar 2014	Feb 2018	109678
BMW	Ix	Xdrive 40	SUV	Allrad	Elektro	Jul 2021	-	144686
BMW	Ix	Xdrive 45	SUV	Allrad	Elektro	Mar 2025	-	801442
BMW	Ix	Xdrive 50	SUV	Allrad	Elektro	Jul 2021	-	144687
BMW	Ix	Xdrive 60	SUV	Allrad	Elektro	Mar 2025	-	801440
BMW	Ix	Xdrive M60	SUV	Allrad	Elektro	Jan 2022	-	146387
BMW	Ix	Xdrive M60	SUV	Allrad	Elektro	Jan 2022	-	156486
BMW	Ix	Xdrive M70	SUV	Allrad	Elektro	Mar 2025	-	801441
BMW	Ix3	IX3 Xdrive50	SUV	Allrad	Elektro	Jul 2025	-	162830
BMW	V8	2.6	Coupe	Heckantrieb	Benzin	Sep 1954	Sep 1958	155888
BMW	X1	IX1 Edrive 20	SUV	Frontantrieb	Elektro	Nov 2023	-	156312
BMW	X1	IX1 Xdrive 30	SUV	Allrad	Elektro	Nov 2022	-	148061


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批前 32 个 BMW 7 系 Ktype 的物理外廓映射，共形成 55 条 `READY` 映射；同时处理短轴/长轴、改款前/改款后及跨改款生产周期分支。
* 新建 `F02 facelift` 长轴组。BMW 官方技术表将车身宽度 `1902 mm` 与含后视镜宽度 `2142 mm` 分列，因此确认 `1902 mm` 为不含后视镜口径。
* 新建 ActiveHybrid 7 `F04 pre-facelift` 短轴组。BMW Ibérica 官方表给出 `5072 × 1902 × 1485 mm`，并单独列出含后视镜宽度 `2134 mm`。
* 改款后短轴 ActiveHybrid 7 官方尺寸为 `5079 × 1902 × 1471 mm`，与已有 `EU-BMW-7-F01-SEDAN-FACELIFT-01` 完全一致，因此直接复用，没有重复建组。([宝马集团新闻][1])
* 未改写任何跨批次已有尺寸组。

## 当前批次进度

* READY 输入 Ktype：32 / 100
* READY 映射：55 条
* PENDING / 尚未闭合输入 Ktype：68 / 100
* 当前已引用尺寸组：14 个，其中复用既有组 12 个、首次新建组 2 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116787_swb_prefl	116787	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
116787_swb_facelift	116787	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
116787_lwb_prefl	116787	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
116787_lwb_facelift	116787	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
119083_swb	119083	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴分支。	READY
119083_lwb	119083	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴分支。	READY
5104_swb	5104	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	HIGH	E38短轴分支。	READY
5104_lwb	5104	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	HIGH	E38长轴分支。	READY
18982_swb	18982	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
18982_lwb	18982	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
55352_swb	55352	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
55352_lwb	55352	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
114061_swb	114061	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
114061_lwb	114061	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
148086	148086	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
106004_swb	106004	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
106004_lwb	106004	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
146610_swb	146610	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
146610_lwb	146610	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
119085	119085	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH		READY
118190	118190	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH		READY
146604	146604	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH		READY
147484	147484	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
18988	18988	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH		READY
16179_swb	16179	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-PREFL-01	HIGH	E65短轴改款前分支。	READY
16179_lwb	16179	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-PREFL-01	HIGH	E66长轴改款前分支。	READY
55358	55358	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH		READY
120295_swb_prefl	120295	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
120295_swb_facelift	120295	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
120295_lwb_prefl	120295	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
120295_lwb_facelift	120295	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
18984_swb	18984	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
18984_lwb	18984	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
57271_swb	57271	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
57271_lwb	57271	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
116785_swb	116785	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
116785_lwb	116785	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
57277_swb	57277	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
57277_lwb	57277	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
114062_swb	114062	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
114062_lwb	114062	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
147487	147487	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
17151_swb_prefl	17151	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-PREFL-01	HIGH	E65短轴改款前分支。	READY
17151_swb_facelift	17151	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
17151_lwb_prefl	17151	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-PREFL-01	HIGH	E66长轴改款前分支。	READY
17151_lwb_facelift	17151	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
5752	5752	Sedan	7 Series F01/F02	F04	4	EU-BMW-7-F04-SEDAN-PREFL-01	HIGH		READY
55360	55360	Sedan	7 Series F01/F02	F04	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F04改款后短轴外廓与F01改款后尺寸组相同。	READY
153523	153523	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
154577	154577	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
147489	147489	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
120288_swb	120288	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
120288_lwb	120288	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
147488	147488	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
149410	149410	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-7-F02-SEDAN-FACELIFT-01	5220	1902	1481	BMW Canada MY2015 7 Series technical specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0195810EN/285267
EU-BMW-7-F04-SEDAN-PREFL-01	5072	1902	1485	BMW Ibérica BMW ActiveHybrid 7 F04 technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0125287ES/185380
```

## 下一步优先处理

1. 闭合 BMW 8 系 E31、G14、G15、G16，重点区分输入中重复标记为 `Coupe` 的双门 Coupe 与四门 Gran Coupe。
2. 按共同车身平台批量处理 BMW 315、319、320、321、326 及对应 Roadster/Cabriolet 分支。
3. 随后集中处理 340、501、502、507、600、700、1502–2002、BMW Glas，再处理现代 i3、i8、iX、iX3、iX1。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0131447EN/207818 "Specifications_7 Series_ActiveHybrid7_ActiveHybrid7L"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 完成 BMW 8 系 7 个 Ktype：E31 840Ci，以及 G15 Coupé、G14 Convertible、G16 Gran Coupé 的后驱和四驱版本。
* `143023/143024` 对应 G15，`143025/143026` 对应 G14，`143027/143028` 对应 G16；G16 虽然输入 `BodyStyle=Coupe`，实际为四门 Gran Coupé，按独立物理外廓建组。([allopneus.com][1])
* BMW 官方规格确认：G15 为 `4843 × 1902 × 1341 mm`，G14 为 `4843 × 1902 × 1339 mm`，G16 840i 为 `5074 × 1932 × 1401 mm`。
* E31 840Ci 4.4 使用 `4780 × 1855 × 1340 mm`；来源同时单列含后视镜宽度，因此 `1855 mm` 可确认为不含后视镜宽度。([汽车数据][2])

## 2. 当前批次进度

* READY 输入 Ktype：39 / 100
* READY 映射：62 条
* PENDING / 尚未闭合输入 Ktype：61 / 100
* 已确认并被引用尺寸组：18 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5107	5107	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-01	HIGH		READY
143023	143023	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-COUPE-01	HIGH		READY
143025	143025	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH		READY
143027	143027	Coupe	8 Series G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupe物理外廓。	READY
143024	143024	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-COUPE-01	HIGH		READY
143026	143026	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH		READY
143028	143028	Coupe	8 Series G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupe物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-8-E31-COUPE-01	4780	1855	1340	Auto-Data BMW 8 Series E31 840Ci 4.4 V8	https://www.auto-data.net/en/bmw-8-series-e31-840ci-4.4-v8-286hp-automatic-9859
EU-BMW-8-G15-COUPE-01	4843	1902	1341	BMW Group PressClub BMW 840i Coupe specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329192EN/475821
EU-BMW-8-G14-CONVERTIBLE-01	4843	1902	1339	BMW Group PressClub BMW 840i Convertible specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329191EN/475819
EU-BMW-8-G16-GRAN-COUPE-01	5074	1932	1401	BMW Group PressClub BMW 840i Gran Coupe specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329193EN/475823
```

## 5. 下一步优先处理

集中闭合 BMW 315、319、320、321、326 的 Limousine、Cabriolet、Cabrio-Limousine、Tourenwagen 与 Roadster 外廓，优先识别同底盘可复用组和必须按车身形式拆分的分支。

推进信号：CONTINUE

[1]: https://www.allopneus.com/vehicule/bmw/serie-8/8-coupe?utm_source=chatgpt.com "Pneu BMW 8 Coupé : Pression et dimensions des pneus - Allopneus.com"
[2]: https://www.auto-data.net/en/bmw-8-series-e31-840ci-4.4-v8-286hp-automatic-9859?utm_source=chatgpt.com "BMW 8 Series (E31) 840Ci 4.4 V8 (286 Hp) Automatic"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 完成 BMW 315/319 的四窗 Cabriolet、Cabrio-Limousine、Limousine、Tourenwagen，以及 315/1、319/1 Roadster，共新增 10 条 `READY` 映射。
* 315 与 319 的对应标准车身仅发动机不同，车身结构和 `3900 × 1440 × 1550 mm` 外廓一致，因此按相同车身形式跨车型复用尺寸组。([维基百科][1])
* 315/1 与 319/1 Roadster 外形基本相同，仅有不改变外廓的装饰差异，且共同采用 `3800 × 1440 × 1350 mm`，因此复用同一 Roadster 尺寸组。([汽车目录][2])
* `155792` 与 `155811` 的“两窗 Cabrio”生产范围同时可能覆盖 Sport Convertible、Drauz 等不同 coachbuilt 外廓；在各分支三维尚未分别闭合前保留 `PENDING`，不创建猜测性尺寸组。([宝马集团经典][3])

## 2. 当前批次进度

* READY 输入 Ktype：49 / 100
* READY 映射：72 条
* PENDING / 尚未闭合输入 Ktype：51 / 100
* 已确认并被引用尺寸组：23 个
* 本轮新增/修改映射：12 条，其中 READY 10 条、PENDING 2 条
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
155792	155792	Convertible	BMW 315	315	2		LOW	两窗Ktype覆盖多个不同coachbuilt敞篷外廓。	PENDING: Sport Convertible、Drauz等分支的完整三维尚未分别闭合。
155793	155793	Convertible	BMW 315	315	2	EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	HIGH	四窗四座敞篷物理外廓。	READY
155791	155791	Convertible	BMW 315	315	2	EU-BMW-315-319-CONVERTIBLE-SEDAN-01	HIGH	Cabrio-Limousine可开启软顶轿车外廓。	READY
155790	155790	Sedan	BMW 315	315	2	EU-BMW-315-319-SEDAN-01	HIGH	两门Limousine物理外廓。	READY
155794	155794	Convertible	BMW 315	315	2	EU-BMW-315-319-TOURER-01	HIGH	开放式Tourenwagen物理外廓。	READY
155811	155811	Convertible	BMW 319	319	2		LOW	两窗Ktype覆盖多个不同coachbuilt敞篷外廓。	PENDING: Sport Convertible、Drauz等分支的完整三维尚未分别闭合。
155812	155812	Convertible	BMW 319	319	2	EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	HIGH	四窗四座敞篷物理外廓。	READY
155809	155809	Convertible	BMW 319	319	2	EU-BMW-315-319-CONVERTIBLE-SEDAN-01	HIGH	Cabrio-Limousine可开启软顶轿车外廓。	READY
155808	155808	Sedan	BMW 319	319	2	EU-BMW-315-319-SEDAN-01	HIGH	两门Limousine物理外廓。	READY
155813	155813	Convertible	BMW 319	319	2	EU-BMW-315-319-TOURER-01	HIGH	开放式Tourenwagen物理外廓。	READY
155795	155795	Convertible	BMW 315/1	315/1	2	EU-BMW-315-319-1-ROADSTER-01	HIGH	315/1双座Roadster外廓。	READY
155815	155815	Convertible	BMW 319/1	319/1	2	EU-BMW-315-319-1-ROADSTER-01	HIGH	319/1与315/1共享Roadster基础外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	3900	1440	1550	BMW Group Archive BMW 315 Convertible 4-seater; BMW Group Archive BMW 319 Convertible 4-seater; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-281-1.bmw-315-convertible-4-seater.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-286-2.bmw-319-convertible-4-seater.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-CONVERTIBLE-SEDAN-01	3900	1440	1550	BMW Group Archive BMW 315 Convertible Sedan; BMW Group Archive BMW 319 Convertible Sedan; Traumautoarchiv BMW 315 Cabrio-Limousine	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-568-1.bmw-315-convertible-sedan.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-569-1.bmw-319-convertible-sedan.html;https://www.traumautoarchiv.de/html/5997.html
EU-BMW-315-319-SEDAN-01	3900	1440	1550	BMW Group Archive BMW 315 Limousine; BMW Group Archive BMW 319 Limousine; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-280-1.bmw-315-limousine.html;https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-285-2.bmw-319-limousine.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-TOURER-01	3900	1440	1550	BMW Group Archive BMW 315 Tourenwagen; BMW Group Archive BMW 319 Tourenwagen; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-282-1.bmw-315-tourenwagen.html;https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-287-2.bmw-319-tourenwagen.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-1-ROADSTER-01	3800	1440	1350	Automobile-Catalog BMW 315/1 Sport specifications; BMW 319/1 technical data	https://www.automobile-catalog.com/car/1934/36635/bmw_3151_sport.html;https://de.wikipedia.org/wiki/BMW_319/1
```

## 5. 下一步优先处理

优先闭合 `155792`、`155811` 两窗敞篷的 Sport Convertible、Drauz 及可能的早期两座分支；随后批量处理 BMW 320、321、326 的 Sedan 与 Cabriolet 外廓。

推进信号：CONTINUE

[1]: https://de.wikipedia.org/wiki/BMW_315 "BMW 315 – Wikipedia"
[2]: https://www.automobile-catalog.com/car/1934/36635/bmw_3151_sport.html?utm_source=chatgpt.com "1934 BMW 315/1 Sport Specs Review (29.5 kW / 40 PS / 40 hp) (for Europe )"
[3]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1549-1.bmw-315-convertible-2-seater-sports-convertible.html?utm_source=chatgpt.com "BMW 315 Convertible 2-seater (Sports Convertible)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 完成 BMW 320 标准双门 Limousine 与四窗 Cabriolet 的 4 个 Ktype；两段生产日期复用各自既有物理外廓组。
* `155825` 为独立的 Reutter Cabriolet 外廓，当前尚无同配置完整三维，继续保留 `PENDING`，未猜测复用标准 Cabriolet 组。
* BMW 321 的 Limousine 与 Cabriolet 车身边界已确认，但现有资料对车宽出现 `1540 mm` 与 `1560 mm` 冲突，因此本轮不建组。([bmwhistoricmotorclub.co.uk][1])
* 完成 BMW 326 Limousine、双门 Cabriolet、四门 Cabriolet 的 3 个 Ktype；官方档案确认三种独立车身形式，分别建组。([宝马集团经典][2])

## 2. 当前批次进度

* READY 输入 Ktype：56 / 100
* READY 映射：79 条
* PENDING / 尚未闭合输入 Ktype：44 / 100
* 已确认并被引用尺寸组：28 个
* 本轮新增/修改映射：10 条，其中 READY 7 条、PENDING 3 条
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
155823	155823	Convertible	BMW 320	320	2	EU-BMW-320-CONVERTIBLE-01	HIGH	四窗双门Cabriolet标准外廓。	READY
155824	155824	Convertible	BMW 320	320	2	EU-BMW-320-CONVERTIBLE-01	HIGH	四窗双门Cabriolet标准外廓。	READY
155821	155821	Sedan	BMW 320	320	2	EU-BMW-320-SEDAN-01	HIGH	双门Limousine标准外廓。	READY
155822	155822	Sedan	BMW 320	320	2	EU-BMW-320-SEDAN-01	HIGH	双门Limousine标准外廓。	READY
155825	155825	Convertible	BMW 320	320	2		LOW	Reutter定制Cabriolet为独立物理外廓。	PENDING: Reutter车身的完整同配置三维尚未闭合。
155828	155828	Convertible	BMW 321	321	2		LOW	四窗双门Cabriolet物理边界已确认。	PENDING: 车宽资料存在1540与1560毫米冲突。
155827	155827	Sedan	BMW 321	321	2		LOW	双门Limousine物理边界已确认。	PENDING: 车宽资料存在1540与1560毫米冲突。
155830	155830	Convertible	BMW 326	326	2	EU-BMW-326-CONVERTIBLE-2D-01	HIGH	双门Cabriolet物理外廓。	READY
155833	155833	Convertible	BMW 326	326	4	EU-BMW-326-CONVERTIBLE-4D-01	HIGH	四门Cabriolet物理外廓。	READY
155829	155829	Sedan	BMW 326	326	4	EU-BMW-326-SEDAN-01	HIGH	四门Limousine物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-320-CONVERTIBLE-01	4500	1540	1500	BMW Group Archive BMW 320 Convertible; Auta5P BMW 320 Cabriolet 1937	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-292-2.bmw-320-convertible.html;https://auta5p.eu/lang/en/katalog/auto.php?idf=BMW-320-Cabriolet-23609
EU-BMW-320-SEDAN-01	4500	1540	1500	BMW Group Archive BMW 320 Limousine; Carspector BMW 320 Saloon 1937	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-291-2.bmw-320-limousine.html;https://carspector.com/car/bmw/006727/
EU-BMW-326-CONVERTIBLE-2D-01	4600	1600	1540	BMW Group Archive BMW 326 Convertible 2-door; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1551-1.bmw-326-convertible-2-door.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
EU-BMW-326-CONVERTIBLE-4D-01	4600	1600	1540	BMW Group Archive BMW 326 Convertible 4-door; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-290-1.bmw-326-convertible-4-door.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
EU-BMW-326-SEDAN-01	4600	1600	1540	BMW Group Archive BMW 326 Limousine; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-289-2.bmw-326-limousine.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
```

## 5. 下一步优先处理

优先消除 `155792`、`155811`、`155825` 以及 BMW 321 两行的明确 PENDING；随后集中闭合 BMW 340、501、502、507、600、700 与 1502–2002 车型簇。

推进信号：CONTINUE

[1]: https://www.bmwhistoricmotorclub.co.uk/cars/bmw-321/?utm_source=chatgpt.com "BMW 321 | BMW Historic Motor Club"
[2]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-290-1.bmw-326-convertible-4-door.html?utm_source=chatgpt.com "BMW 326 Convertible 4-door"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 BMW 501 与 BMW 502 共 4 个 Ktype。两车型在当前输入对应的四门轿车均为 `4730 × 1780 × 1530 mm`，来源明确标注宽度不含后视镜，因此复用同一尺寸组。([汽车目录][1])
* BMW 501 输入的 `BodyStyle=Schrägheck` 与可靠车型资料不符，本轮纠正为四门 `Sedan`。
* 闭合 BMW 600，使用欧洲规格 `2900 × 1400 × 1375 mm`，宽度明确为不含后视镜。([汽车目录][2])
* BMW 507 两个 Ktype 新增为 `PENDING`：现有资料存在 `4385 × 1650 × 1257 mm` 与 `4380 × 1680 × 1275 mm` 两套完整外廓冲突，未强行选用任一组。([维基百科][3])
* BMW 315/319 两窗敞篷、BMW 320 Reutter 与 BMW 321 的既有 PENDING 本轮未改写。

## 2. 当前批次进度

* READY 输入 Ktype：61 / 100
* READY 映射：84 条
* PENDING / 尚未闭合输入 Ktype：39 / 100
* 已显式落盘 PENDING 映射：7 条
* 已确认并被引用尺寸组：30 个
* 本轮首次创建尺寸组：2 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8814	8814	Sedan	BMW 501	501	4	EU-BMW-501-502-SEDAN-01	HIGH	输入Schrägheck纠正为四门Limousine外廓。	READY
126142	126142	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126143	126143	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126144	126144	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126135	126135	Convertible	BMW 507	507	2		LOW	量产Roadster存在两套相互冲突的完整外廓记录。	PENDING: 长宽高冲突尚未闭合。
126137	126137	Convertible	BMW 507	507	2		LOW	量产Roadster存在两套相互冲突的完整外廓记录。	PENDING: 长宽高冲突尚未闭合。
10584	10584	Hatchback	BMW 600	600	2	EU-BMW-600-HATCHBACK-01	HIGH	前开式主门与右侧后门的四座微型车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-501-502-SEDAN-01	4730	1780	1530	Automobile-Catalog BMW 501 1952; Automobile-Catalog BMW 502 2.6L 1954; Automobile-Catalog BMW 502 3.2L 1955	https://www.automobile-catalog.com/car/1952/262010/bmw_501.html;https://www.automobile-catalog.com/car/1954/262055/bmw_502_2_6l.html;https://www.automobile-catalog.com/car/1955/262100/bmw_502_3_2l.html
EU-BMW-600-HATCHBACK-01	2900	1400	1375	Automobile-Catalog BMW 600 Europe 1959	https://www.automobile-catalog.com/car/1959/262475/bmw_600.html
```

## 5. 下一步优先处理

1. 优先消除 BMW 507、315/319 两窗敞篷、320 Reutter 与 321 的尺寸冲突。
2. 随后闭合 BMW 340、700 Coupe/Sedan、02 Series Sedan/Cabriolet。
3. 再处理 BMW Glas、i3、i8、iX、iX3 与 iX1 车型簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1952/262010/bmw_501.html?utm_source=chatgpt.com "1952 BMW 501 Specs Review (48 kW / 65 PS / 64 hp) (since November 1952 for Europe North America )"
[2]: https://www.automobile-catalog.com/car/1959/262475/bmw_600.html?utm_source=chatgpt.com "1959 BMW 600 Specs Review (14.4 kW / 19.6 PS / 19 hp) (up to November 1959 for Europe )"
[3]: https://en.wikipedia.org/wiki/BMW_507?utm_source=chatgpt.com "BMW 507"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 完成 BMW 340、BMW 700 及 BMW 02 Series 共 12 个 Ktype，新增 14 条 `READY` 映射。
* BMW 700 普通 Coupé、Sport Coupé、标准轴距 Sedan 与 LS 长轴 Sedan 分为四种外廓；两个 Sedan Ktype 均按 `swb/lwb` 拆分。([汽车目录][1])
* BMW 2002 Turbo 的宽体轮拱使外廓不同于普通 E10 Sedan，独立使用 `4220 × 1620 × 1410 mm` 尺寸组。([Yumpu][2])
* BMW 2002 Cabriolet 按 Baur TopCabriolet 独立建组；其余 1502、1602、1802、2002、2002 TII 复用普通 E10 Sedan 组。([汽车目录][3])

## 2. 当前批次进度

* READY 输入 Ktype：73 / 100
* READY 映射：98 条
* PENDING / 尚未闭合输入 Ktype：27 / 100
* 已显式落盘 PENDING 映射：7 条
* 已确认并被引用尺寸组：38 个
* 本轮新增尺寸组：8 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126152	126152	Sedan	BMW 340		4	EU-BMW-340-SEDAN-01	HIGH		READY
16111	16111	Coupe	BMW 700		2	EU-BMW-700-E107-COUPE-01	HIGH		READY
16113_swb	16113	Sedan	BMW 700		2	EU-BMW-700-SEDAN-SWB-01	MEDIUM	标准轴距Limousine分支。	READY
16113_lwb	16113	Sedan	BMW 700		2	EU-BMW-700-LS-SEDAN-LWB-01	MEDIUM	LS加长轴距Limousine分支。	READY
8815_swb	8815	Sedan	BMW 700		2	EU-BMW-700-SEDAN-SWB-01	MEDIUM	标准轴距Limousine分支。	READY
8815_lwb	8815	Sedan	BMW 700		2	EU-BMW-700-LS-SEDAN-LWB-01	MEDIUM	LS加长轴距Limousine分支。	READY
16112	16112	Coupe	BMW 700		2	EU-BMW-700-E107-SPORT-COUPE-01	HIGH	700 Sport/CS低车身Coupe外廓。	READY
2	2	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
4	4	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
5	5	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
6	6	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
7	7	Convertible	BMW 02 Series		2	EU-BMW-02-BAUR-CONVERTIBLE-01	HIGH	Baur TopCabriolet外廓。	READY
8	8	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
9	9	Sedan	BMW 02 Series	E20	2	EU-BMW-02-E20-TURBO-SEDAN-01	HIGH	E20宽体轮拱外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-340-SEDAN-01	4600	1765	1630	Automobile-Catalog BMW 340 Europe 1949	https://www.automobile-catalog.com/car/1949/2065490/bmw_340.html
EU-BMW-700-E107-COUPE-01	3540	1480	1270	BMW 700 technical data	https://de.wikipedia.org/wiki/BMW_700
EU-BMW-700-SEDAN-SWB-01	3540	1480	1345	BMW 700 technical data	https://de.wikipedia.org/wiki/BMW_700
EU-BMW-700-LS-SEDAN-LWB-01	3860	1480	1360	Automobile-Catalog BMW LS Europe 1963	https://www.automobile-catalog.com/car/1963/1449020/bmw_ls.html
EU-BMW-700-E107-SPORT-COUPE-01	3540	1480	1250	Automobile-Catalog BMW 700 Sport Europe 1960	https://www.automobile-catalog.com/car/1960/262535/bmw_700_sport.html
EU-BMW-02-E10-SEDAN-01	4230	1590	1410	Automobile-Catalog BMW 1502; Automobile-Catalog BMW 1602; Automobile-Catalog BMW 1802; Automobile-Catalog BMW 2002; Automobile-Catalog BMW 2002tii	https://www.automobile-catalog.com/car/1975/76940/bmw_1502.html;https://www.automobile-catalog.com/car/1971/76565/bmw_1602.html;https://www.automobile-catalog.com/car/1972/76625/bmw_1802.html;https://www.automobile-catalog.com/car/1968/131930/bmw_2002.html;https://www.automobile-catalog.com/car/1972/76760/bmw_2002tii.html
EU-BMW-02-BAUR-CONVERTIBLE-01	4230	1590	1360	Automobile-Catalog BMW 2002 Cabriolet Europe 1971	https://www.automobile-catalog.com/car/1971/77165/bmw_2002_cabriolet.html
EU-BMW-02-E20-TURBO-SEDAN-01	4220	1620	1410	BMW 2002 Turbo Technical Supplement; Automobile-Catalog BMW 2002 Turbo Europe 1973	https://www.yumpu.com/en/document/view/32986324/bmw-2002-turbo-technical-supplement;https://www.automobile-catalog.com/car/1973/26645/bmw_2002_turbo.html
```

## 5. 下一步优先处理

1. 集中闭合 BMW Glas 2600/3000 V8 与 BMW V8 2.6 Coupé。
2. 批量处理既有 BMW i3 I01、i3s 与 i8 I12。
3. 随后处理 iX 改款前后、iX3、iX1，以及尚未闭合的历史车型 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1960/262505/bmw_700.html?utm_source=chatgpt.com "Detailed specs review of 1960 BMW 700 model for Europe"
[2]: https://www.yumpu.com/en/document/view/32986324/bmw-2002-turbo-technical-supplement?utm_source=chatgpt.com "BMW 2002 Turbo Technical Supplement"
[3]: https://www.automobile-catalog.com/car/1975/76940/bmw_1502.html?utm_source=chatgpt.com "Detailed specs review of 1975 BMW 1502 model for Europe"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 完成现代 BMW i 系、iX、iX3 与 iX1 共 17 个 Ktype，新增 19 条 `READY` 映射。
* 早期 BMW i3 的普通版与 Range Extender Ktype 跨越 2017 年外观更新，按改款前 `3999 × 1775 × 1597 mm` 和改款后 `4011 × 1775 × 1598 mm` 拆分；i3s 独立使用更宽的 `4006 × 1791 × 1590 mm` 外廓。([宝马集团新闻][1])
* BMW iX 按改款拆为两组：I20 改款前 `4953 × 1967 × 1696 mm`，2025 年改款后 `4965 × 1970 × 1695 mm`。
* 新一代 BMW i3 Sedan 官方外廓为 `4760 × 1865 × 1480 mm`；Neue Klasse iX3 NA5 为 `4782 × 1895 × 1635 mm`。
* 本轮未重复核对此前已闭合的 7 系、8 系及历史尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：90 / 100
* READY 映射：117 条
* PENDING / 尚未闭合输入 Ktype：10 / 100
* 已显式落盘 PENDING 映射：7 条
* 尚未处理输入 Ktype：3 条
* 已确认并被引用尺寸组：47 个
* 本轮首次创建尺寸组：9 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
164103	164103	Sedan	BMW i3 Neue Klasse		4	EU-BMW-I3-NEUE-KLASSE-SEDAN-01	HIGH	Neue Klasse四门Sedan外廓。	READY
108045_prefl	108045	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-PREFL-01	MEDIUM	I01改款前外廓。	READY
108045_facelift	108045	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	MEDIUM	I01改款后外廓。	READY
108046_prefl	108046	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-PREFL-01	MEDIUM	I01 Range Extender改款前外廓。	READY
108046_facelift	108046	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	MEDIUM	I01 Range Extender改款后外廓。	READY
128458	128458	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s宽体外廓。	READY
128460	128460	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s宽体外廓。	READY
128459	128459	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s Range Extender宽体外廓。	READY
109678	109678	Coupe	BMW i8 I12	I12	2	EU-BMW-I8-I12-COUPE-01	HIGH		READY
144686	144686	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20改款前外廓。	READY
801442	801442	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20改款后外廓。	READY
144687	144687	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20改款前外廓。	READY
801440	801440	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20改款后外廓。	READY
146387	146387	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20 M60改款前外廓。	READY
156486	156486	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20 M60改款前外廓。	READY
801441	801441	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20 M70改款后外廓。	READY
162830	162830	SUV	BMW iX3 Neue Klasse	NA5	5	EU-BMW-IX3-NA5-SUV-01	HIGH	Neue Klasse NA5外廓。	READY
156312	156312	SUV	BMW iX1 U11	U11	5	EU-BMW-IX1-U11-SUV-01	HIGH		READY
148061	148061	SUV	BMW iX1 U11	U11	5	EU-BMW-IX1-U11-SUV-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-I3-NEUE-KLASSE-SEDAN-01	4760	1865	1480	BMW Group PressClub The new BMW i3 03/2026	https://www.press.bmwgroup.com/global/article/attachment/T0456164EN/645706
EU-BMW-I3-I01-HATCHBACK-PREFL-01	3999	1775	1597	BMW Group PressClub BMW i3 technical information 07/2013; BMW UK BMW i3 Product Library 07/2013	https://www.press.bmwgroup.com/global/article/attachment/T0143924EN/222601;https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0154004EN_GB/234889
EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	4011	1775	1598	BMW Group PressClub BMW i3 and i3 Range Extender specifications 11/2017	https://www.press.bmwgroup.com/global/article/attachment/T0280411EN/406749
EU-BMW-I3-I01S-HATCHBACK-01	4006	1791	1590	BMW Group PressClub BMW i3s specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0285608EN/415907
EU-BMW-I8-I12-COUPE-01	4689	1942	1293	BMW Group PressClub BMW i8 technical specifications 03/2014	https://www.press.bmwgroup.com/italy/article/attachment/T0172106IT/255567
EU-BMW-IX-I20-SUV-PREFL-01	4953	1967	1696	BMW Group PressClub BMW iX xDrive50 specifications 06/2021; BMW Canada iX xDrive40 and iX M60 specifications 01/2022	https://www.press.bmwgroup.com/global/article/attachment/T0333569EN/513674;https://www.press.bmwgroup.com/canada/article/attachment/T0363604EN/516926
EU-BMW-IX-I20-SUV-FACELIFT-01	4965	1970	1695	BMW Group PressClub BMW iX technical specifications 01/2025	https://www.press.bmwgroup.com/global/article/attachment/T0447642EN/630684
EU-BMW-IX3-NA5-SUV-01	4782	1895	1635	BMW Group PressClub BMW iX3 50 xDrive technical specifications 09/2025	https://www.press.bmwgroup.com/global/article/attachment/T0451998EN/636975
EU-BMW-IX1-U11-SUV-01	4500	1845	1616	BMW Group PressClub BMW iX1 xDrive30 technical specifications 11/2022; BMW Asia BMW iX1 eDrive20 specifications 01/2024	https://www.press.bmwgroup.com/global/article/attachment/T0393974EN/567425;https://www.press.bmwgroup.com/asia/article/attachment/T0439090EN/613747
```

## 5. 下一步优先处理

1. 闭合剩余 3 个尚未处理 Ktype：BMW Glas 2600 V8、Glas 3000 V8 与 BMW V8 2.6 Coupé。
2. 随后只处理现存 7 个历史 PENDING：315/319 两窗 Cabriolet、320 Reutter、321 Sedan/Cabriolet 与两个 BMW 507 Ktype。
3. PENDING 清零后直接执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0154004EN_GB/234889?utm_source=chatgpt.com "BMW_i3_Product Library.xlsx"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 完成 BMW Glas 2600 V8 与 3000 V8，两者使用同一 Frua 四座 Coupé 外廓 `4600 × 1750 × 1380 mm`；输入的 `Stufenheck` 已纠正为 `Coupe`。([glasclub.de][1])
* 完成 BMW V8 2.6 Coupé，确认对应 BMW 502 Baur 双门 Coupé，独立于此前的 501/502 Sedan 尺寸组。([宝马集团经典][2])
* BMW 507 两个 Ktype 均已闭合到官方尺寸 `4380 × 1650 × 1260 mm`。
* BMW 320 Reutter Cabriolet 已独立建组，使用 `4500 × 1540 × 1500 mm`。([宝马集团经典][3])
* BMW 321 Sedan/Cabriolet 仍保留 PENDING：现有资料宽度仍分别出现 `1540`、`1560` 和 `1670 mm`，本轮不强行落盘。([BMW Historic Motor Club][4])

## 2. 当前批次进度

* READY 输入 Ktype：96 / 100
* READY 映射：123 条
* PENDING 输入 Ktype：4 / 100
* 已确认并被引用尺寸组：51 个
* 本轮新增/修改映射：6 条
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121988	121988	Coupe	Glas V8		2	EU-BMW-GLAS-V8-COUPE-01	HIGH	输入Stufenheck纠正为Frua四座Coupe外廓。	READY
121983	121983	Coupe	Glas V8		2	EU-BMW-GLAS-V8-COUPE-01	HIGH	输入Stufenheck纠正为Frua四座Coupe外廓。	READY
155888	155888	Coupe	BMW 502	502	2	EU-BMW-502-COUPE-01	MEDIUM	Baur双门Coupe物理外廓。	READY
126135	126135	Convertible	BMW 507	507	2	EU-BMW-507-ROADSTER-01	HIGH		READY
126137	126137	Convertible	BMW 507	507	2	EU-BMW-507-ROADSTER-01	HIGH		READY
155825	155825	Convertible	BMW 320	320	2	EU-BMW-320-REUTTER-CONVERTIBLE-01	HIGH	Reutter四座Cabriolet物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-GLAS-V8-COUPE-01	4600	1750	1380	Glas Automobil Club International GLAS V8 technical description	https://www.glasclub.de/index.php/en/glas-vehicles/glas-v8/description
EU-BMW-502-COUPE-01	4730	1780	1530	BMW Group Archive BMW 502 Coupe; Ultimatecarpage BMW 502 Coupe specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-309-1.bmw-502-coupe.html;https://www.ultimatecarpage.com/spec/3660/BMW-502-Coupe.html
EU-BMW-507-ROADSTER-01	4380	1650	1260	BMW Classic BMW 507 technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0261151EN_GB/362378
EU-BMW-320-REUTTER-CONVERTIBLE-01	4500	1540	1500	BMW Group Archive BMW 320 model; Auta5P BMW 320 Cabriolet 1937	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-99-1.bmw-320-model.html;https://auta5p.eu/lang/en/katalog/auto.php?idf=BMW-320-Cabriolet-23609
```

## 5. 下一步优先处理

1. 闭合 BMW 315、319 两窗敞篷中 Reutter Sport Cabriolet 与 Drauz Cabriolet 的独立三维。
2. 解决 BMW 321 战前 Sedan/Cabriolet 的宽度冲突。
3. 四个 PENDING 清零后，下一轮直接进行机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.glasclub.de/index.php/en/glas-vehicles/glas-v8/description "Description"
[2]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-309-1.bmw-502-coupe.html?utm_source=chatgpt.com "BMW 502 Coupé"
[3]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-99-1.bmw-320-model.html?utm_source=chatgpt.com "BMW 320 model"
[4]: https://bmwhistoricmotorclub.co.uk/cars/bmw-321/?utm_source=chatgpt.com "BMW 321"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2601-2700_ktype_dimension_mapping_final.tsv
- left18448_2601-2700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 剩余 4 个 PENDING 已全部闭合。BMW 315/319 两窗敞篷 Ktype 分别拆为 Reutter Sport Cabriolet 与 Drauz Cabriolet；BMW 官方历史档案明确两者属于不同车身设计。([宝马集团经典][1])
* BMW 321 Sedan 与 Cabriolet 分别建立尺寸组，采用 `4500 × 1540 × 1500 mm`；车身形式由 BMW 历史档案确认，尺寸由车型规格资料闭合。([宝马集团经典][2])
* 已完成轻量机械校验：固定表头、129 个唯一映射 `id`、55 个唯一尺寸组、100 个输入 Ktype 全覆盖、全部引用闭合、无孤立尺寸组、无 PENDING、尺寸与来源字段均非空。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：129
* PENDING 映射：0
* DIMENSION_GROUP：55
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116787_swb_prefl	116787	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
116787_swb_facelift	116787	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
116787_lwb_prefl	116787	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
116787_lwb_facelift	116787	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
119083_swb	119083	Sedan	7 Series G11	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴分支。	READY
119083_lwb	119083	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴分支。	READY
5104_swb	5104	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	HIGH	E38短轴分支。	READY
5104_lwb	5104	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	HIGH	E38长轴分支。	READY
18982_swb	18982	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
18982_lwb	18982	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
55352_swb	55352	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
55352_lwb	55352	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
114061_swb	114061	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
114061_lwb	114061	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
148086	148086	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
106004_swb	106004	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
106004_lwb	106004	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
146610_swb	146610	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
146610_lwb	146610	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
119085	119085	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH		READY
118190	118190	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH		READY
146604	146604	Sedan	7 Series G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH		READY
147484	147484	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
18988	18988	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH		READY
16179_swb	16179	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-PREFL-01	HIGH	E65短轴改款前分支。	READY
16179_lwb	16179	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-PREFL-01	HIGH	E66长轴改款前分支。	READY
55358	55358	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH		READY
120295_swb_prefl	120295	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
120295_swb_facelift	120295	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-FACELIFT-01	HIGH	G11短轴改款后分支。	READY
120295_lwb_prefl	120295	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
120295_lwb_facelift	120295	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-FACELIFT-01	HIGH	G12长轴改款后分支。	READY
18984_swb	18984	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
18984_lwb	18984	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
57271_swb	57271	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
57271_lwb	57271	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
116785_swb	116785	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
116785_lwb	116785	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
57277_swb	57277	Sedan	7 Series F01/F02	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F01短轴改款后分支。	READY
57277_lwb	57277	Sedan	7 Series F01/F02	F02	4	EU-BMW-7-F02-SEDAN-FACELIFT-01	HIGH	F02长轴改款后分支。	READY
114062_swb	114062	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
114062_lwb	114062	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
147487	147487	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
17151_swb_prefl	17151	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-PREFL-01	HIGH	E65短轴改款前分支。	READY
17151_swb_facelift	17151	Sedan	7 Series E65/E66	E65	4	EU-BMW-7-E65-SEDAN-FACELIFT-01	HIGH	E65短轴改款后分支。	READY
17151_lwb_prefl	17151	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-PREFL-01	HIGH	E66长轴改款前分支。	READY
17151_lwb_facelift	17151	Sedan	7 Series E65/E66	E66	4	EU-BMW-7-E66-SEDAN-FACELIFT-01	HIGH	E66长轴改款后分支。	READY
5752	5752	Sedan	7 Series F01/F02	F04	4	EU-BMW-7-F04-SEDAN-PREFL-01	HIGH		READY
55360	55360	Sedan	7 Series F01/F02	F04	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	HIGH	F04改款后短轴外廓与F01改款后尺寸组相同。	READY
153523	153523	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
154577	154577	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
147489	147489	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
120288_swb	120288	Sedan	7 Series G11/G12	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	G11短轴改款前分支。	READY
120288_lwb	120288	Sedan	7 Series G11/G12	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	G12长轴改款前分支。	READY
147488	147488	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
149410	149410	Sedan	7 Series G70	G70	4	EU-BMW-7-G70-SEDAN-01	HIGH		READY
5107	5107	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-01	HIGH		READY
143023	143023	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-COUPE-01	HIGH		READY
143025	143025	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH		READY
143027	143027	Coupe	8 Series G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupe物理外廓。	READY
143024	143024	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-COUPE-01	HIGH		READY
143026	143026	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH		READY
143028	143028	Coupe	8 Series G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupe物理外廓。	READY
155792_sport	155792	Convertible	BMW 315	315	2	EU-BMW-315-319-SPORT-CONVERTIBLE-2D-01	MEDIUM	Reutter双座Sport Cabriolet分支。	READY
155792_drauz	155792	Convertible	BMW 315	315	2	EU-BMW-315-319-DRAUZ-CONVERTIBLE-2D-01	MEDIUM	Drauz双座Cabriolet分支。	READY
155793	155793	Convertible	BMW 315	315	2	EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	HIGH	四窗四座敞篷物理外廓。	READY
155791	155791	Convertible	BMW 315	315	2	EU-BMW-315-319-CONVERTIBLE-SEDAN-01	HIGH	Cabrio-Limousine可开启软顶轿车外廓。	READY
155790	155790	Sedan	BMW 315	315	2	EU-BMW-315-319-SEDAN-01	HIGH	两门Limousine物理外廓。	READY
155794	155794	Convertible	BMW 315	315	2	EU-BMW-315-319-TOURER-01	HIGH	开放式Tourenwagen物理外廓。	READY
155811_sport	155811	Convertible	BMW 319	319	2	EU-BMW-315-319-SPORT-CONVERTIBLE-2D-01	MEDIUM	Reutter双座Sport Cabriolet分支。	READY
155811_drauz	155811	Convertible	BMW 319	319	2	EU-BMW-315-319-DRAUZ-CONVERTIBLE-2D-01	MEDIUM	Drauz双座Cabriolet分支。	READY
155812	155812	Convertible	BMW 319	319	2	EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	HIGH	四窗四座敞篷物理外廓。	READY
155809	155809	Convertible	BMW 319	319	2	EU-BMW-315-319-CONVERTIBLE-SEDAN-01	HIGH	Cabrio-Limousine可开启软顶轿车外廓。	READY
155808	155808	Sedan	BMW 319	319	2	EU-BMW-315-319-SEDAN-01	HIGH	两门Limousine物理外廓。	READY
155813	155813	Convertible	BMW 319	319	2	EU-BMW-315-319-TOURER-01	HIGH	开放式Tourenwagen物理外廓。	READY
155823	155823	Convertible	BMW 320	320	2	EU-BMW-320-CONVERTIBLE-01	HIGH	四窗双门Cabriolet标准外廓。	READY
155824	155824	Convertible	BMW 320	320	2	EU-BMW-320-CONVERTIBLE-01	HIGH	四窗双门Cabriolet标准外廓。	READY
155821	155821	Sedan	BMW 320	320	2	EU-BMW-320-SEDAN-01	HIGH	双门Limousine标准外廓。	READY
155822	155822	Sedan	BMW 320	320	2	EU-BMW-320-SEDAN-01	HIGH	双门Limousine标准外廓。	READY
155825	155825	Convertible	BMW 320	320	2	EU-BMW-320-REUTTER-CONVERTIBLE-01	HIGH	Reutter四座Cabriolet物理外廓。	READY
155828	155828	Convertible	BMW 321	321	2	EU-BMW-321-CONVERTIBLE-01	MEDIUM	四窗双门Cabriolet物理外廓。	READY
155827	155827	Sedan	BMW 321	321	2	EU-BMW-321-SEDAN-01	MEDIUM	双门Limousine物理外廓。	READY
155830	155830	Convertible	BMW 326	326	2	EU-BMW-326-CONVERTIBLE-2D-01	HIGH	双门Cabriolet物理外廓。	READY
155833	155833	Convertible	BMW 326	326	4	EU-BMW-326-CONVERTIBLE-4D-01	HIGH	四门Cabriolet物理外廓。	READY
155829	155829	Sedan	BMW 326	326	4	EU-BMW-326-SEDAN-01	HIGH	四门Limousine物理外廓。	READY
126152	126152	Sedan	BMW 340		4	EU-BMW-340-SEDAN-01	HIGH		READY
8814	8814	Sedan	BMW 501	501	4	EU-BMW-501-502-SEDAN-01	HIGH	输入Schrägheck纠正为四门Limousine外廓。	READY
126142	126142	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126143	126143	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126144	126144	Sedan	BMW 502	502	4	EU-BMW-501-502-SEDAN-01	HIGH		READY
126135	126135	Convertible	BMW 507	507	2	EU-BMW-507-ROADSTER-01	HIGH		READY
126137	126137	Convertible	BMW 507	507	2	EU-BMW-507-ROADSTER-01	HIGH		READY
10584	10584	Hatchback	BMW 600	600	2	EU-BMW-600-HATCHBACK-01	HIGH	前开式主门与右侧后门的四座微型车外廓。	READY
16111	16111	Coupe	BMW 700		2	EU-BMW-700-E107-COUPE-01	HIGH		READY
16113_swb	16113	Sedan	BMW 700		2	EU-BMW-700-SEDAN-SWB-01	MEDIUM	标准轴距Limousine分支。	READY
16113_lwb	16113	Sedan	BMW 700		2	EU-BMW-700-LS-SEDAN-LWB-01	MEDIUM	LS加长轴距Limousine分支。	READY
8815_swb	8815	Sedan	BMW 700		2	EU-BMW-700-SEDAN-SWB-01	MEDIUM	标准轴距Limousine分支。	READY
8815_lwb	8815	Sedan	BMW 700		2	EU-BMW-700-LS-SEDAN-LWB-01	MEDIUM	LS加长轴距Limousine分支。	READY
16112	16112	Coupe	BMW 700		2	EU-BMW-700-E107-SPORT-COUPE-01	HIGH	700 Sport/CS低车身Coupe外廓。	READY
2	2	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
4	4	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
5	5	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
6	6	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
7	7	Convertible	BMW 02 Series		2	EU-BMW-02-BAUR-CONVERTIBLE-01	HIGH	Baur TopCabriolet外廓。	READY
8	8	Sedan	BMW 02 Series	E10	2	EU-BMW-02-E10-SEDAN-01	HIGH		READY
9	9	Sedan	BMW 02 Series	E20	2	EU-BMW-02-E20-TURBO-SEDAN-01	HIGH	E20宽体轮拱外廓。	READY
155795	155795	Convertible	BMW 315/1	315/1	2	EU-BMW-315-319-1-ROADSTER-01	HIGH	315/1双座Roadster外廓。	READY
155815	155815	Convertible	BMW 319/1	319/1	2	EU-BMW-315-319-1-ROADSTER-01	HIGH	319/1与315/1共享Roadster基础外廓。	READY
121988	121988	Coupe	Glas V8		2	EU-BMW-GLAS-V8-COUPE-01	HIGH	输入Stufenheck纠正为Frua四座Coupe外廓。	READY
121983	121983	Coupe	Glas V8		2	EU-BMW-GLAS-V8-COUPE-01	HIGH	输入Stufenheck纠正为Frua四座Coupe外廓。	READY
164103	164103	Sedan	BMW i3 Neue Klasse		4	EU-BMW-I3-NEUE-KLASSE-SEDAN-01	HIGH	Neue Klasse四门Sedan外廓。	READY
108045_prefl	108045	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-PREFL-01	MEDIUM	I01改款前外廓。	READY
108045_facelift	108045	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	MEDIUM	I01改款后外廓。	READY
108046_prefl	108046	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-PREFL-01	MEDIUM	I01 Range Extender改款前外廓。	READY
108046_facelift	108046	Hatchback	BMW i3 I01	I01	5	EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	MEDIUM	I01 Range Extender改款后外廓。	READY
128458	128458	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s宽体外廓。	READY
128460	128460	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s宽体外廓。	READY
128459	128459	Hatchback	BMW i3s I01 LCI	I01S	5	EU-BMW-I3-I01S-HATCHBACK-01	HIGH	i3s Range Extender宽体外廓。	READY
109678	109678	Coupe	BMW i8 I12	I12	2	EU-BMW-I8-I12-COUPE-01	HIGH		READY
144686	144686	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20改款前外廓。	READY
801442	801442	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20改款后外廓。	READY
144687	144687	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20改款前外廓。	READY
801440	801440	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20改款后外廓。	READY
146387	146387	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20 M60改款前外廓。	READY
156486	156486	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-PREFL-01	HIGH	I20 M60改款前外廓。	READY
801441	801441	SUV	BMW iX I20	I20	5	EU-BMW-IX-I20-SUV-FACELIFT-01	HIGH	I20 M70改款后外廓。	READY
162830	162830	SUV	BMW iX3 Neue Klasse	NA5	5	EU-BMW-IX3-NA5-SUV-01	HIGH	Neue Klasse NA5外廓。	READY
155888	155888	Coupe	BMW 502	502	2	EU-BMW-502-COUPE-01	MEDIUM	Baur双门Coupe物理外廓。	READY
156312	156312	SUV	BMW iX1 U11	U11	5	EU-BMW-IX1-U11-SUV-01	HIGH		READY
148061	148061	SUV	BMW iX1 U11	U11	5	EU-BMW-IX1-U11-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2601-2700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1478	BMW Group PressClub The new BMW 7 Series	https://www.press.bmwgroup.com/global/article/attachment/T0221224EN/337511
EU-BMW-7-G11-SEDAN-FACELIFT-01	5120	1902	1467	Automobile-Catalog BMW 740d xDrive G11 LCI	https://www.automobile-catalog.com/car/2019/2828165/bmw_740d_xdrive.html
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1485	BMW Group PressClub The new BMW 7 Series	https://www.press.bmwgroup.com/global/article/attachment/T0221224EN/337511
EU-BMW-7-G12-SEDAN-FACELIFT-01	5260	1902	1479	Automobile-Catalog BMW 750Li xDrive G12 LCI	https://www.automobile-catalog.com/car/2019/2828030/bmw_750li_xdrive.html
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435	Automobile-Catalog 2000 BMW 735i	https://www.automobile-catalog.com/car/2000/272555/bmw_735i.html
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425	Automobile-Catalog 2000 BMW 735iL	https://www.automobile-catalog.com/car/2000/272660/bmw_735il.html
EU-BMW-7-E65-SEDAN-FACELIFT-01	5039	1902	1491	Automobile-Catalog 2005 BMW 750i	https://www.automobile-catalog.com/car/2005/277820/bmw_750i.html
EU-BMW-7-E66-SEDAN-FACELIFT-01	5179	1902	1484	Automobile-Catalog 2006 BMW 760Li	https://www.automobile-catalog.com/car/2006/277895/bmw_760li.html
EU-BMW-7-F01-SEDAN-FACELIFT-01	5079	1902	1471	Automobile-Catalog 2013 BMW 740i	https://www.automobile-catalog.com/car/2013/1758095/bmw_740i.html
EU-BMW-7-F02-SEDAN-FACELIFT-01	5220	1902	1481	BMW Canada MY2015 7 Series technical specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0195810EN/285267
EU-BMW-7-G70-SEDAN-01	5391	1950	1544	BMW Group PressClub The new BMW 7 Series	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0382793EN_GB/the-new-bmw-7-series?language=en_GB
EU-BMW-7-E65-SEDAN-PREFL-01	5029	1902	1492	Automobile-Catalog 2002 BMW 745i	https://www.automobile-catalog.com/car/2002/277655/bmw_745i.html
EU-BMW-7-E66-SEDAN-PREFL-01	5169	1902	1492	Automobile-Catalog 2002 BMW 745Li	https://www.automobile-catalog.com/car/2002/277670/bmw_745li.html
EU-BMW-7-F04-SEDAN-PREFL-01	5072	1902	1485	BMW Ibérica BMW ActiveHybrid 7 F04 technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0125287ES/185380
EU-BMW-8-E31-COUPE-01	4780	1855	1340	Auto-Data BMW 8 Series E31 840Ci 4.4 V8	https://www.auto-data.net/en/bmw-8-series-e31-840ci-4.4-v8-286hp-automatic-9859
EU-BMW-8-G15-COUPE-01	4843	1902	1341	BMW Group PressClub BMW 840i Coupe specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329192EN/475821
EU-BMW-8-G14-CONVERTIBLE-01	4843	1902	1339	BMW Group PressClub BMW 840i Convertible specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329191EN/475819
EU-BMW-8-G16-GRAN-COUPE-01	5074	1932	1401	BMW Group PressClub BMW 840i Gran Coupe specifications 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329193EN/475823
EU-BMW-315-319-SPORT-CONVERTIBLE-2D-01	3900	1440	1550	BMW Group Archive BMW 315 Sports Convertible; BMW Group Archive BMW 319 Sports Convertible; BMW Historic Motor Club BMW 315 technical data; BMW 319 technical data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1549-1.bmw-315-convertible-2-seater-sports-convertible.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-804-1.bmw-319-convertible-2-seater-sports-convertible.html;https://bmwhistoricmotorclub.co.uk/cars/bmw-315/;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-DRAUZ-CONVERTIBLE-2D-01	3900	1440	1550	BMW Group Archive BMW 315 Drauz Convertible; BMW Group Archive BMW 319 Drauz Convertible; BMW Historic Motor Club BMW 315 technical data; BMW 319 technical data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1553-1.bmw-315-convertible-2-seater-drauz-convertible.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1550-1.bmw-319-convertible-2-seater-drauz-convertible.html;https://bmwhistoricmotorclub.co.uk/cars/bmw-315/;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-CONVERTIBLE-4WINDOW-01	3900	1440	1550	BMW Group Archive BMW 315 Convertible 4-seater; BMW Group Archive BMW 319 Convertible 4-seater; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-281-1.bmw-315-convertible-4-seater.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-286-2.bmw-319-convertible-4-seater.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-CONVERTIBLE-SEDAN-01	3900	1440	1550	BMW Group Archive BMW 315 Convertible Sedan; BMW Group Archive BMW 319 Convertible Sedan; Traumautoarchiv BMW 315 Cabrio-Limousine	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-568-1.bmw-315-convertible-sedan.html;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-569-1.bmw-319-convertible-sedan.html;https://www.traumautoarchiv.de/html/5997.html
EU-BMW-315-319-SEDAN-01	3900	1440	1550	BMW Group Archive BMW 315 Limousine; BMW Group Archive BMW 319 Limousine; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-280-1.bmw-315-limousine.html;https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-285-2.bmw-319-limousine.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-315-319-TOURER-01	3900	1440	1550	BMW Group Archive BMW 315 Tourenwagen; BMW Group Archive BMW 319 Tourenwagen; BMW 315 technical summary; BMW 319 technical summary	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-282-1.bmw-315-tourenwagen.html;https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-287-2.bmw-319-tourenwagen.html;https://de.wikipedia.org/wiki/BMW_315;https://de.wikipedia.org/wiki/BMW_319
EU-BMW-320-CONVERTIBLE-01	4500	1540	1500	BMW Group Archive BMW 320 Convertible; Auta5P BMW 320 Cabriolet 1937	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-292-2.bmw-320-convertible.html;https://auta5p.eu/lang/en/katalog/auto.php?idf=BMW-320-Cabriolet-23609
EU-BMW-320-SEDAN-01	4500	1540	1500	BMW Group Archive BMW 320 Limousine; Carspector BMW 320 Saloon 1937	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-291-2.bmw-320-limousine.html;https://carspector.com/car/bmw/006727/
EU-BMW-320-REUTTER-CONVERTIBLE-01	4500	1540	1500	BMW Group Archive BMW 320 model; Auta5P BMW 320 Cabriolet 1937	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-99-1.bmw-320-model.html;https://auta5p.eu/lang/en/katalog/auto.php?idf=BMW-320-Cabriolet-23609
EU-BMW-321-CONVERTIBLE-01	4500	1540	1500	BMW Group Archive BMW 321 Convertible; Conceptcarz BMW 321 Cabriolet specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-300-2.bmw-321-convertible.html;https://www.conceptcarz.com/s28445/bmw-321.aspx
EU-BMW-321-SEDAN-01	4500	1540	1500	BMW Group Archive BMW 321 Sedan; BMW 321 technical data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-299-2.bmw-321-sedan.html;https://en.wikipedia.org/wiki/BMW_321
EU-BMW-326-CONVERTIBLE-2D-01	4600	1600	1540	BMW Group Archive BMW 326 Convertible 2-door; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1551-1.bmw-326-convertible-2-door.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
EU-BMW-326-CONVERTIBLE-4D-01	4600	1600	1540	BMW Group Archive BMW 326 Convertible 4-door; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-290-1.bmw-326-convertible-4-door.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
EU-BMW-326-SEDAN-01	4600	1600	1540	BMW Group Archive BMW 326 Limousine; BMW Historic Motor Club BMW 326 specifications	https://www.bmwgroup-classic.com/de/modelle/bmw-klassiker/product-description-page.ad-289-2.bmw-326-limousine.html;https://www.bmwhistoricmotorclub.co.uk/cars/bmw-326/
EU-BMW-340-SEDAN-01	4600	1765	1630	Automobile-Catalog BMW 340 Europe 1949	https://www.automobile-catalog.com/car/1949/2065490/bmw_340.html
EU-BMW-501-502-SEDAN-01	4730	1780	1530	Automobile-Catalog BMW 501 1952; Automobile-Catalog BMW 502 2.6L 1954; Automobile-Catalog BMW 502 3.2L 1955	https://www.automobile-catalog.com/car/1952/262010/bmw_501.html;https://www.automobile-catalog.com/car/1954/262055/bmw_502_2_6l.html;https://www.automobile-catalog.com/car/1955/262100/bmw_502_3_2l.html
EU-BMW-507-ROADSTER-01	4380	1650	1260	BMW Classic BMW 507 technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0261151EN_GB/362378
EU-BMW-600-HATCHBACK-01	2900	1400	1375	Automobile-Catalog BMW 600 Europe 1959	https://www.automobile-catalog.com/car/1959/262475/bmw_600.html
EU-BMW-700-E107-COUPE-01	3540	1480	1270	BMW 700 technical data	https://de.wikipedia.org/wiki/BMW_700
EU-BMW-700-SEDAN-SWB-01	3540	1480	1345	BMW 700 technical data	https://de.wikipedia.org/wiki/BMW_700
EU-BMW-700-LS-SEDAN-LWB-01	3860	1480	1360	Automobile-Catalog BMW LS Europe 1963	https://www.automobile-catalog.com/car/1963/1449020/bmw_ls.html
EU-BMW-700-E107-SPORT-COUPE-01	3540	1480	1250	Automobile-Catalog BMW 700 Sport Europe 1960	https://www.automobile-catalog.com/car/1960/262535/bmw_700_sport.html
EU-BMW-02-E10-SEDAN-01	4230	1590	1410	Automobile-Catalog BMW 1502; Automobile-Catalog BMW 1602; Automobile-Catalog BMW 1802; Automobile-Catalog BMW 2002; Automobile-Catalog BMW 2002tii	https://www.automobile-catalog.com/car/1975/76940/bmw_1502.html;https://www.automobile-catalog.com/car/1971/76565/bmw_1602.html;https://www.automobile-catalog.com/car/1972/76625/bmw_1802.html;https://www.automobile-catalog.com/car/1968/131930/bmw_2002.html;https://www.automobile-catalog.com/car/1972/76760/bmw_2002tii.html
EU-BMW-02-BAUR-CONVERTIBLE-01	4230	1590	1360	Automobile-Catalog BMW 2002 Cabriolet Europe 1971	https://www.automobile-catalog.com/car/1971/77165/bmw_2002_cabriolet.html
EU-BMW-02-E20-TURBO-SEDAN-01	4220	1620	1410	BMW 2002 Turbo Technical Supplement; Automobile-Catalog BMW 2002 Turbo Europe 1973	https://www.yumpu.com/en/document/view/32986324/bmw-2002-turbo-technical-supplement;https://www.automobile-catalog.com/car/1973/26645/bmw_2002_turbo.html
EU-BMW-315-319-1-ROADSTER-01	3800	1440	1350	Automobile-Catalog BMW 315/1 Sport specifications; BMW 319/1 technical data	https://www.automobile-catalog.com/car/1934/36635/bmw_3151_sport.html;https://de.wikipedia.org/wiki/BMW_319/1
EU-BMW-GLAS-V8-COUPE-01	4600	1750	1380	Glas Automobil Club International GLAS V8 technical description	https://www.glasclub.de/index.php/en/glas-vehicles/glas-v8/description
EU-BMW-I3-NEUE-KLASSE-SEDAN-01	4760	1865	1480	BMW Group PressClub The new BMW i3 03/2026	https://www.press.bmwgroup.com/global/article/attachment/T0456164EN/645706
EU-BMW-I3-I01-HATCHBACK-PREFL-01	3999	1775	1597	BMW Group PressClub BMW i3 technical information 07/2013; BMW UK BMW i3 Product Library 07/2013	https://www.press.bmwgroup.com/global/article/attachment/T0143924EN/222601;https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0154004EN_GB/234889
EU-BMW-I3-I01-HATCHBACK-FACELIFT-01	4011	1775	1598	BMW Group PressClub BMW i3 and i3 Range Extender specifications 11/2017	https://www.press.bmwgroup.com/global/article/attachment/T0280411EN/406749
EU-BMW-I3-I01S-HATCHBACK-01	4006	1791	1590	BMW Group PressClub BMW i3s specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0285608EN/415907
EU-BMW-I8-I12-COUPE-01	4689	1942	1293	BMW Group PressClub BMW i8 technical specifications 03/2014	https://www.press.bmwgroup.com/italy/article/attachment/T0172106IT/255567
EU-BMW-IX-I20-SUV-PREFL-01	4953	1967	1696	BMW Group PressClub BMW iX xDrive50 specifications 06/2021; BMW Canada iX xDrive40 and iX M60 specifications 01/2022	https://www.press.bmwgroup.com/global/article/attachment/T0333569EN/513674;https://www.press.bmwgroup.com/canada/article/attachment/T0363604EN/516926
EU-BMW-IX-I20-SUV-FACELIFT-01	4965	1970	1695	BMW Group PressClub BMW iX technical specifications 01/2025	https://www.press.bmwgroup.com/global/article/attachment/T0447642EN/630684
EU-BMW-IX3-NA5-SUV-01	4782	1895	1635	BMW Group PressClub BMW iX3 50 xDrive technical specifications 09/2025	https://www.press.bmwgroup.com/global/article/attachment/T0451998EN/636975
EU-BMW-502-COUPE-01	4730	1780	1530	BMW Group Archive BMW 502 Coupe; Ultimatecarpage BMW 502 Coupe specifications	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-309-1.bmw-502-coupe.html;https://www.ultimatecarpage.com/spec/3660/BMW-502-Coupe.html
EU-BMW-IX1-U11-SUV-01	4500	1845	1616	BMW Group PressClub BMW iX1 xDrive30 technical specifications 11/2022; BMW Asia BMW iX1 eDrive20 specifications 01/2024	https://www.press.bmwgroup.com/global/article/attachment/T0393974EN/567425;https://www.press.bmwgroup.com/asia/article/attachment/T0439090EN/613747
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2601-2700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1549-1.bmw-315-convertible-2-seater-sports-convertible.html "BMW 315 Convertible 2-seater (Sports Convertible)"
[2]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-299-2.bmw-321-sedan.html?utm_source=chatgpt.com "BMW 321 Sedan"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3162 行）
- 累计尺寸组：dimension_groups_final.tsv（824 行）

