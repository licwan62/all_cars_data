# 任务：left18448 第 6701-6800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0068__63ddfd86


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6701-6800 行

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
left18448 第 6701-6800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Hyundai	Equus / centennial	3.0 24V	Stufenheck	Frontantrieb	Benzin	Oct 1999	Mar 2009	111963
Hyundai	Equus / centennial	3.8 GDI	Stufenheck	Heckantrieb	Benzin	Mar 2009	Dec 2016	54907
Hyundai	Equus / centennial	4.6 V8	Stufenheck	Heckantrieb	Benzin	Mar 2009	Dec 2016	54905
Hyundai	Equus / centennial	5.0 GDI	Stufenheck	Heckantrieb	Benzin	Mar 2009	Dec 2016	54906
Hyundai	Galloper	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Aug 1998	Dec 2003	16943
Hyundai	Galloper	2.5 TD Intercooler	Geländewagen geschlossen	Allrad	Diesel	Aug 1998	Dec 2003	15145
Hyundai	Galloper	3.0 V6	Geländewagen geschlossen	Allrad	Benzin	Aug 1998	Dec 2003	15144
Hyundai	Genesis	2.0 Cvvt	Coupe	Heckantrieb	Benzin	Feb 2013	Feb 2014	117566
Hyundai	Genesis	2.0 T	Coupe	Heckantrieb	Benzin	Apr 2012	Feb 2014	55398
Hyundai	Genesis	2.0 T	Coupe	Heckantrieb	Benzin	Nov 2011	Dec 2014	59400
Hyundai	Genesis	3.0 GDI	Stufenheck	Heckantrieb	Benzin	Jun 2014	Jul 2017	108015
Hyundai	Genesis	3.0 GDI 4WD	Stufenheck	Allrad	Benzin	Jun 2014	Jul 2017	108016
Hyundai	Genesis	3.3 24V	Stufenheck	Heckantrieb	Benzin	Jun 2008	Dec 2014	111966
Hyundai	Genesis	3.3 24V	Stufenheck	Heckantrieb	Benzin	Jan 2008	Dec 2014	111979
Hyundai	Genesis	3.8 GDI	Stufenheck	Heckantrieb	Benzin	Sep 2011	Dec 2014	53682
Hyundai	Genesis	3.8 GDI	Stufenheck	Heckantrieb	Benzin	Jun 2014	Jul 2017	116891
Hyundai	Genesis	3.8 GDI 4WD	Stufenheck	Allrad	Benzin	Jun 2014	Jul 2017	108014
Hyundai	Genesis	3.8 V6	Stufenheck	Heckantrieb	Benzin	Jan 2011	Dec 2014	52428
Hyundai	Genesis	3.8 V6	Coupe	Heckantrieb	Benzin	Apr 2012	-	55397
Hyundai	Genesis	3.8 V6	Coupe	Heckantrieb	Benzin	Nov 2011	Dec 2014	59399
Hyundai	Getz	1.1	Schrägheck	Frontantrieb	Benzin	Sep 2002	Sep 2005	16978
Hyundai	Getz	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2003	Sep 2005	18027
Hyundai	Getz	1.6	Schrägheck	Frontantrieb	Benzin	Sep 2002	Sep 2005	16813
Hyundai	Getz	1.3 I	Schrägheck	Frontantrieb	Benzin	Sep 2002	Mar 2004	16814
Hyundai	Getz	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	Mar 2003	Sep 2005	16812
Hyundai	Grace	2.4	Kasten	Heckantrieb	Benzin	Jul 1993	Jul 1997	57620
Hyundai	Grace	2.4	Kasten	Heckantrieb	Benzin	Oct 1997	Dec 2004	117567
Hyundai	Grand santa fé	2.2 Crdi Allrad	SUV	Allrad	Diesel	Sep 2013	Nov 2018	116960
Hyundai	Grand santa fé	3.3 Allrad	SUV	Allrad	Benzin	Feb 2014	Nov 2018	100972
Hyundai	Grandeur	2.4	Stufenheck	Frontantrieb	Benzin	Sep 2006	Dec 2008	111975
Hyundai	Grandeur	1.6 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Nov 2022	-	154669
Hyundai	Grandeur	2.2 D	Stufenheck	Frontantrieb	Diesel	Jan 2011	Dec 2017	111980
Hyundai	Grandeur	2.4 16V	Stufenheck	Frontantrieb	Benzin	Jan 2011	Oct 2016	111981
Hyundai	H-1	2.4	Kasten	Heckantrieb	Benzin	Mar 2000	Apr 2004	14737
Hyundai	H-1	2.5 Crdi	Kasten	Heckantrieb	Diesel	Aug 2003	Dec 2007	17758
Hyundai	H-1	2.5 TD	Kasten	Heckantrieb	Diesel	Mar 2000	Sep 2000	14736
Hyundai	H-1	2.5 TD	Kasten	Heckantrieb	Diesel	Mar 2000	Oct 2006	15381
Hyundai	H-1	2.5 TD	Kasten	Heckantrieb	Diesel	Oct 2001	Aug 2007	17466
Hyundai	H-1 / starex	2.5 Crdi	Bus	Heckantrieb	Diesel	Dec 2002	Apr 2004	54936
Hyundai	H-1 cargo	2.5 Crdi	Kasten	Heckantrieb	Diesel	Feb 2008	-	55576
Hyundai	H-1 cargo	2.5 Crdi	Kasten	Heckantrieb	Diesel	Jan 2009	-	55577
Hyundai	H-1 cargo	2.5 Crdi	Kasten	Heckantrieb	Diesel	Aug 2009	-	55578
Hyundai	H-1 travel	2.4 I	Bus	Heckantrieb	Benzin	Feb 2008	-	34959
Hyundai	H-1 travel	2.5 Crdi	Bus	Heckantrieb	Diesel	Jul 2008	-	11235
Hyundai	H-1 travel	2.5 Crdi	Bus	Heckantrieb	Diesel	May 2008	-	56114
Hyundai	H-1 travel	2.5 Crdi	Bus	Heckantrieb	Diesel	Aug 2011	-	57267
Hyundai	H-1 travel	2.5 Crdi	Bus	Heckantrieb	Diesel	Jul 2010	-	107665
Hyundai	H100	2.4	Bus	Heckantrieb	Benzin	Jul 1993	Mar 2000	14192
Hyundai	H100	2.4 TD	Kasten	Heckantrieb	Benzin	Jul 1993	Jul 1997	113299
Hyundai	H100	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2004	-	55625
Hyundai	H100	2.5 D	Bus	Heckantrieb	Diesel	Dec 1994	Mar 2000	8169
Hyundai	H100	2.5 D	Kasten	Heckantrieb	Diesel	Dec 1994	Mar 2000	10559
Hyundai	H100	2.5 D	Kasten	Heckantrieb	Diesel	Jul 1993	Dec 1994	10560
Hyundai	H100	2.5 TD	Bus	Heckantrieb	Diesel	Jul 1993	Mar 2000	15919
Hyundai	H100	2.5 Tdic	Kasten	Heckantrieb	Diesel	Jun 1998	Oct 2003	56036
Hyundai	H350	2.5 Crdi	Bus	Heckantrieb	Diesel	Apr 2015	-	113116
Hyundai	H350	2.5 Crdi	Bus	Heckantrieb	Diesel	Apr 2015	-	113118
Hyundai	H350	2.5 Crdi	Kasten	Heckantrieb	Diesel	Apr 2015	-	113119
Hyundai	H350	2.5 Crdi	Kasten	Heckantrieb	Diesel	Apr 2015	-	113120
Hyundai	H350	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2015	-	113122
Hyundai	H350	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	Apr 2015	-	113123
Hyundai	Highway van	2.0 Crdi	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2001	Mar 2004	120007
Hyundai	Highway van	2.0 Cvvt	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2003	Mar 2004	120008
Hyundai	i	1.6 16V	Coupe	Frontantrieb	Benzin	Mar 1998	Apr 2002	10161
Hyundai	i	1.6 I 16V	Coupe	Frontantrieb	Benzin	Dec 1996	Apr 2002	11139
Hyundai	i	1.6 I 16V	Coupe	Frontantrieb	Benzin	Aug 2000	Jan 2002	55793
Hyundai	i	2.0 16V	Coupe	Frontantrieb	Benzin	Mar 2001	Apr 2002	16168
Hyundai	I10 i	1	Schrägheck	Frontantrieb	Benzin	Jan 2011	Dec 2013	59401
Hyundai	I10 i	1.1	Schrägheck	Frontantrieb	Benzin	Nov 2008	Dec 2013	120679
Hyundai	I10 i	1.1 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Apr 2011	Dec 2013	14034
Hyundai	I10 ii	1	Schrägheck	Frontantrieb	Benzin	Aug 2013	Dec 2019	100581
Hyundai	I10 ii	1.2	Schrägheck	Frontantrieb	Benzin	Dec 2013	Dec 2019	100584
Hyundai	I10 ii	1.2	Stufenheck	Frontantrieb	Benzin	Aug 2015	-	115521
Hyundai	I10 ii	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2014	Dec 2019	100792
Hyundai	I10 iii	1.0 MPI	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	800262
Hyundai	I10 iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	800264
Hyundai	I10 iii	1.2 MPI	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	800263
Hyundai	I20 active	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Sep 2015	Jun 2018	122142
Hyundai	I20 active	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Sep 2015	Jun 2018	122145
Hyundai	I20 active	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	Sep 2015	Jun 2018	122150
Hyundai	I20 i	1.2	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2015	57273
Hyundai	I20 i	1.1 Crdi	Schrägheck	Frontantrieb	Diesel	Mar 2012	Dec 2015	57272
Hyundai	I20 i	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	Aug 2008	Dec 2015	34801
Hyundai	I20 i	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Jan 2009	Dec 2012	59405
Hyundai	I20 ii	1.2	Schrägheck	Frontantrieb	Benzin	Nov 2014	Mar 2020	108798
Hyundai	I20 ii	1.2	Schrägheck	Frontantrieb	Benzin	Nov 2014	Aug 2020	108806
Hyundai	I20 ii	1.2	Coupe	Frontantrieb	Benzin	May 2015	Sep 2021	121091
Hyundai	I20 ii	1.4	Schrägheck	Frontantrieb	Benzin	Nov 2014	Jun 2018	108807
Hyundai	I20 ii	1.4	Coupe	Frontantrieb	Benzin	May 2015	Sep 2021	114617
Hyundai	I20 ii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jan 2016	Aug 2020	118529
Hyundai	I20 ii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jan 2016	Aug 2020	118530
Hyundai	I20 ii	1.1 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2014	Jun 2018	108809
Hyundai	I20 ii	1.1 Crdi	Coupe	Frontantrieb	Diesel	May 2015	Sep 2021	121094
Hyundai	I20 ii	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2014	Jun 2018	108810
Hyundai	I20 ii	1.4 Crdi	Coupe	Frontantrieb	Diesel	May 2015	Sep 2021	114618
Hyundai	I20 iii	1.2	Schrägheck	Frontantrieb	Benzin	May 2024	-	159193
Hyundai	I20 iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Oct 2025	-	802507
Hyundai	I20 iii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2024	-	801093
Hyundai	I20 iii	1.4 MPI	Schrägheck	Frontantrieb	Benzin	May 2021	-	146414
Hyundai	I20 iii	1.6 T-gdi N	Schrägheck	Frontantrieb	Benzin	Nov 2020	-	145703


--- Round 1 / 首次发送 ---
更新点

* 首轮按物理外廓聚类，闭合 **i10 III、i20 II、i20 III** 共 19 个 Ktype 映射。
* 新建 7 个尺寸组；发动机、燃料和功率差异均复用对应车身组，未重复建组。
* i10 III 标准版与 N Line、i20 II 五门与三门 Coupe、i20 III 改款前后及 N 高性能版分别建组。
* 三维均采用 Hyundai 官方技术资料，宽度字段明确为不含后视镜口径。

当前批次进度

* 输入 Ktype：100
* READY 映射：19
* 待处理映射：81
* 已确认尺寸组：7
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800262	800262	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-5D-01	HIGH	第三代五门标准外廓。	READY
800264	800264	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-NLINE-01	HIGH	1.0 T-GDI对应N Line五门外廓。	READY
800263	800263	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-5D-01	HIGH	第三代五门标准外廓。	READY
108798	108798	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
108806	108806	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
121091	121091	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
108807	108807	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
114617	114617	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
118529	118529	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
118530	118530	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
108809	108809	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
121094	121094	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
108810	108810	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
114618	114618	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
159193	159193	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	HIGH	第三代五门改款后标准外廓。	READY
802507	802507	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	MEDIUM	2025年Ktype按第三代改款后标准五门外廓关联。	READY
801093	801093	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	HIGH	第三代五门改款后标准外廓。	READY
146414	146414	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-01	HIGH	第三代五门改款前标准外廓。	READY
145703	145703	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-N-01	HIGH	N高性能版独立外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I10-III-HATCHBACK-5D-01	3670	1680	1480	Hyundai Motor UK i10 technical specifications MY25	https://www.hyundai.news/newsroom/dam/uk/press-kits/hyundai-uk-i10-tech-spec-pricing-model-year-2025-0424.pdf
EU-HYUNDAI-I10-III-HATCHBACK-NLINE-01	3670	1680	1483	Hyundai Motor UK i10 technical specifications MY25	https://www.hyundai.news/newsroom/dam/uk/press-kits/hyundai-uk-i10-tech-spec-pricing-model-year-2025-0424.pdf
EU-HYUNDAI-I20-II-HATCHBACK-5D-01	4035	1734	1474	Hyundai Motor UK i20 PLAY technical specifications	https://www.hyundai.news/newsroom/dam/eu/uk/20190729_model_i20_play/i20_PLAY_Release_technical.pdf
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449	Hyundai Motor Europe New Generation i20 Coupe press information	https://www.hyundai.news/newsroom/dam/eu/press-kits/2015_i20_coupe/NewGeneration_i20_Coupe_Press_Information_032015.pdf
EU-HYUNDAI-I20-III-HATCHBACK-5D-02	4065	1775	1450	Hyundai Motor Europe i20 technical data August 2023	https://www.hyundai.news/newsroom/dam/eu/press-kits/20230908_i20/hyundai-i20-technical-data-0823.pdf
EU-HYUNDAI-I20-III-HATCHBACK-5D-01	4040	1775	1450	Hyundai Motor Europe i20 and i20 N Line technical data June 2021	https://www.hyundai.news/newsroom/dam/eu/models/20210610_sop_i20_n_and_i20_n_line/hyundai-sop-i20-and-i20-n-line-tech-data.pdf
EU-HYUNDAI-I20-III-HATCHBACK-N-01	4075	1775	1440	Hyundai Motor UK i20 N technical data June 2021	https://www.hyundai.news/newsroom/dam/eu/uk/20210617_i20_n_pricing_specs/hyundai-uk-i20-n-technical-data-0621.pdf
```

下一步优先处理

1. 闭合 i10 I、i10 II 的 Hatchback，并单独核对 i10 II Sedan。
2. 核对 i20 Active 的加高车身、外部包围和车顶行李架口径，避免错误复用普通 i20 II。
3. 批量处理 Equus、Genesis、Getz、Grandeur等乘用车尺寸组。
4. 将 H-1、H100、H350 按 Van、Bus、轴距、车顶和底盘形式拆分，禁止以发动机版本代替物理分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 新增闭合 i10 I、i10 II 五门 Hatchback 和欧洲版 i20 II Active，共新增 9 条 READY 映射。
* i10 I 统一关联 PA 五门外廓；i10 II 标准五门统一关联 IA 外廓；发动机和 LPG 差异未重复建组。
* i20 Active 使用欧洲车型的 4065×1760×1529 mm 外廓，没有误用印度版 3995×1760×1555 mm 规格。

当前批次进度

* 输入 Ktype：100
* READY 映射：28
* PENDING 映射：72
* 已确认尺寸组：10
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59401	59401	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	HIGH	PA五门外廓。	READY
120679	120679	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	MEDIUM	PA五门外廓。	READY
14034	14034	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	MEDIUM	PA五门外廓。	READY
100581	100581	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
100584	100584	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
100792	100792	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
122142	122142	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
122145	122145	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
122150	122150	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I10-I-HATCHBACK-5D-01	3565	1595	1540	Hyundai Motor UK i10 2011 Model Year official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Hyundai-i10-UK.pdf
EU-HYUNDAI-I10-II-HATCHBACK-5D-01	3665	1660	1500	Hyundai Ireland New i10 official brochure	https://www.hyundai.ie/assets/i10-brochure.pdf
EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	4065	1760	1529	Hyundai Motor UK i20 2017 Model Year official brochure	https://xr793.com/wp-content/uploads/2022/09/2017-Hyundai-i20-UK.pdf
```

下一步优先处理

1. 核对 i10 II Sedan Ktype `115521`，不得复用欧洲五门 Hatchback 组。
2. 批量闭合 Getz、Genesis Coupe 与 Genesis Sedan 的高复用乘用车尺寸组。
3. 处理 Equus、Grandeur和 Grand Santa Fe 的代际边界。
4. 最后集中拆分 H-1、H100、H350 的 Bus、Van、底盘、轴距及车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 闭合 Genesis Coupe 第一代改款双门外廓，5 个 Ktype 复用同一 BK 尺寸组；2013 年车型资料明确宽度不含后视镜。([Dezo's Garage][1])
* 闭合 Genesis II 四门 DH 外廓，3.0/3.8、后驱/四驱共 4 个 Ktype 复用同组；官方资料给出 4990×1890×1480 mm，并明确宽度不含后视镜。([现代新闻][2])
* 闭合 i10 II Sedan 对应的 Xcent BA 四门外廓；官方车型资料给出 3995×1660×1520 mm。([HYUNDAI MOTORS][3])

当前批次进度

* 输入 Ktype：100
* READY 映射：38
* PENDING 映射：62
* 已确认尺寸组：13
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117566	117566	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
55398	55398	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
59400	59400	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
108015	108015	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
108016	108016	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
116891	116891	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
108014	108014	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
55397	55397	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
59399	59399	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
115521	115521	Sedan	i10 II / Xcent	BA	4	EU-HYUNDAI-I10-II-SEDAN-4D-01	MEDIUM	BA四门Xcent Sedan外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	4630	1864	1384	Hyundai 2013 Genesis Coupe official brochure archive	https://xr793.com/wp-content/uploads/2017/02/2013-Hyundai-Genesis-Coupe.pdf
EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	4990	1890	1480	Hyundai Motor Deutschland Genesis Sportlimousine technical data; Hyundai Motor Company All-New Genesis launch specifications	https://www.hyundai.news/newsroom/dam/de/Pressemappen/Genesis_Sportlimousine/genesis_sportlimousine_2014_3_technische_daten_d7205f1.pdf;https://www.hyundai.com/content/hyundai/ww/data/news/data/2013/0000002864/attach/131126_Hyundai%20All%20New%20Genesis%20Launch%20in%20Korea.doc
EU-HYUNDAI-I10-II-SEDAN-4D-01	3995	1660	1520	Hyundai Motor India XCENT official brochure	https://www.hyundai.com/content/dam/hyundai/in/en/data/build-a-car/download-e-broucher/XCENT_Sedan_brochure.pdf
```

下一步优先处理

1. Getz TB 改款前的三门、五门物理边界。
2. Genesis I Sedan BH 的生产阶段和外廓。
3. Equus/Centennial 第一代与第二代。
4. Grandeur、Grand Santa Fe 和 Galloper。
5. 最后集中拆分 H-1、H100、H350 商用车的车身、轴距和车顶分支。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2017/02/2013-Hyundai-Genesis-Coupe.pdf?utm_source=chatgpt.com "2013 HYUNDAI"
[2]: https://www.hyundai.news/newsroom/dam/de/Pressemappen/Genesis_Sportlimousine/genesis_sportlimousine_2014_3_technische_daten_d7205f1.pdf?utm_source=chatgpt.com "TECHNISCHE DATEN1 Karosserie 3.8 V6 GDI"
[3]: https://www.hyundai.com/content/dam/hyundai/in/en/data/build-a-car/download-e-broucher/XCENT_Sedan_brochure.pdf?utm_source=chatgpt.com "xcent"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 闭合 Genesis I Sedan 的改款前、改款后两套外廓。跨越 2012 年外观改款的 3 个 Ktype 拆成 `prefl`、`facelift` 派生行；仅覆盖 GDI 改款车型的 `53682` 直接关联改款后组。Hyundai 资料确认 2012 款采用重新设计的前后保险杠等外部变化。([汽车目录档案][1])
* 闭合 Grand Santa Fe 2 个 Ktype，复用同一 NC 长轴五门 SUV 尺寸组；官方德国技术资料明确宽度为不含后视镜 1885 mm。([现代新闻][2])
* 闭合 Grandeur V 两个 Ktype和 Grandeur VII Hybrid 一个 Ktype。第五代三维为 4910×1860×1470 mm；第七代官方目录为 5035×1880×1460 mm。

当前批次进度

* 输入 Ktype：100
* READY Ktype：47
* PENDING Ktype：53
* READY 映射行：50
* 已确认尺寸组：18
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
111966_prefl	111966	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
111966_facelift	111966	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
111979_prefl	111979	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
111979_facelift	111979	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
53682	53682	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	HIGH	3.8 GDI对应改款后四门外廓。	READY
52428_prefl	52428	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
52428_facelift	52428	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
116960	116960	SUV	Grand Santa Fe III	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	HIGH	NC长轴五门SUV外廓。	READY
100972	100972	SUV	Grand Santa Fe III	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	HIGH	NC长轴五门SUV外廓。	READY
111980	111980	Sedan	Grandeur V	HG	4	EU-HYUNDAI-GRANDEUR-V-SEDAN-01	HIGH	HG四门Sedan外廓。	READY
111981	111981	Sedan	Grandeur V	HG	4	EU-HYUNDAI-GRANDEUR-V-SEDAN-01	HIGH	HG四门Sedan外廓。	READY
154669	154669	Sedan	Grandeur VII	GN7	4	EU-HYUNDAI-GRANDEUR-VII-SEDAN-01	HIGH	GN7四门Hybrid Sedan外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	4976	1890	1481	Hyundai Motor America 2009 Genesis official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-Genesis-2009-USA.pdf
EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	4985	1890	1480	Hyundai Canada 2012 Genesis Sedan official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2012_genesis_sedan.pdf
EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	4915	1885	1695	Hyundai Motor Deutschland Grand Santa Fe official technical data	https://www.hyundai.news/newsroom/dam/de/Pressemappen/Grand_Santa_Fe/hyundai_grand_santa_fe_technische_daten_2018.pdf
EU-HYUNDAI-GRANDEUR-V-SEDAN-01	4910	1860	1470	Hyundai Motor America Azera official press information; Hyundai Azera 2012 Owner's Manual	https://www.hyundainews.com/assets/documents/original/21808-2013AZERA%3AMODERNDESIGN%2CSMARTTECHNOLOGY%2CPERFORMANCEANDSAFETY.pdf;https://www.carmanualsonline.info/hyundai-azera-2012-owner-s-manual/?srch=dimensions
EU-HYUNDAI-GRANDEUR-VII-SEDAN-01	5035	1880	1460	Hyundai Motor Company Grandeur official English catalog	https://www.hyundai.com/content/dam/hyundai/kr/ko/data/vehicles/catalog/en/grandeur-catalog-eng.pdf
```

下一步优先处理

1. Equus/Centennial 第一代跨改款外廓和第二代普通悬架、空气悬架高度边界。
2. Getz TB 改款前三门、五门分支及其共同三维。
3. Galloper、Grandeur IV 和第一代 Coupe。
4. 随后处理 Grace、Highway Van，再集中拆分 H-1、H100、H350 商用车的轴距、车顶和底盘形式。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-Genesis-2009-USA.pdf?utm_source=chatgpt.com "09 hyundai _genesis"
[2]: https://www.hyundai.news/newsroom/dam/de/Pressemappen/Grand_Santa_Fe/hyundai_grand_santa_fe_technische_daten_2018.pdf "Hyundai Grand Santa Fe | Technische Daten | Stand: 1.2017"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 闭合 Equus/Centennial 第二代 3 个 Ktype。官方资料显示改款前后标准轴距车型长度、宽度保持一致，完整外廓按官方公制规格落盘为 5160×1890×1490 mm，宽度明确不含外后视镜。
* 闭合 Getz TB 改款前 5 个 Ktype。官方规格同时列出三门和五门车型，三维均为 3810×1665×1495 mm；因门体结构不同，分别建立稳定的三门、五门尺寸组。([Dezo's Garage][1])
* 本轮新增 8 个 READY Ktype、13 条映射行和 3 个尺寸组。

当前批次进度

* 输入 Ktype：100
* READY Ktype：55
* PENDING Ktype：45
* READY 映射行：63
* 已确认尺寸组：21
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
54907	54907	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
54905	54905	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
54906	54906	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
16978_3dr	16978	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16978_5dr	16978	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
18027_3dr	18027	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
18027_5dr	18027	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16813_3dr	16813	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16813_5dr	16813	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16814_3dr	16814	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16814_5dr	16814	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16812_3dr	16812	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16812_5dr	16812	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-EQUUS-II-SEDAN-01	5160	1890	1490	Hyundai Motor America 2011 Equus engineering information;Hyundai Motor America 2014 Equus official press information	https://www.hyundainews.com/assets/documents/original/10865-HYUNDAIRELEASESENGINEERINGANDFEATUREINFORMATIONFORTHEALL-NEW2011HYUNDAIEQUUS.pdf;https://www.hyundainews.com/assets/documents/original/22126-REDESIGNED2014EQUUSOFFERSDRIVER-FOCUSEDTECHNOLOGIES%2CPREMIUMDESIGN%2CSUSPENSIONREFINEMENTANDADVANCEDSAFETYFEATURES.pdf
EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	3810	1665	1495	Hyundai Motor Company Australia Getz official specification sheet	https://xr793.com/wp-content/uploads/2023/04/2005-Hyundai-Getz-Specs-AUS.pdf
EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	3810	1665	1495	Hyundai Motor Company Australia Getz official specification sheet	https://xr793.com/wp-content/uploads/2023/04/2005-Hyundai-Getz-Specs-AUS.pdf
```

下一步优先处理

1. 闭合 Equus/Centennial 第一代和 Grandeur IV。
2. 处理 Galloper、第一代 Hyundai Coupe 和 Highway Van。
3. 核对 Grace 与早期 H100 的 Bus、Van及轴距边界。
4. 集中拆分 H-1、H100、H350 的车身、轴距、车顶和底盘形式。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2023/04/2005-Hyundai-Getz-Specs-AUS.pdf "RHADA00111_Getz Spec Sheet FA"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 已闭合剩余全部乘用车、SUV 与 MPV：Equus I、Grandeur IV、Galloper II、Coupe I、i20 I 和 Highway Van。
* Equus I、Coupe I 依据改款前后外廓变化拆分；Galloper II 按三门短轴和五门长轴拆分。([汽车目录][1])
* i20 I 改款前为 3940 mm、改款后为 3995 mm；按实际发动机对应的三门、五门供应范围建立四个尺寸组。([汽车目录][2])
* 当前剩余 30 个 Ktype 全部属于 Grace、H-1、H100、H350 商用车体系。

当前批次进度

* 输入 Ktype：100
* READY Ktype：70
* PENDING Ktype：30
* READY 映射行：88
* 已确认尺寸组：33
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
111963_prefl	111963	Sedan	Equus I pre-facelift		4	EU-HYUNDAI-EQUUS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖2003年改款前四门外廓。	READY
111963_facelift	111963	Sedan	Equus I facelift		4	EU-HYUNDAI-EQUUS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖2003年改款后四门外廓。	READY
16943_swb	16943	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
16943_lwb	16943	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
15145_swb	15145	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
15145_lwb	15145	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
15144_swb	15144	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
15144_lwb	15144	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
111975	111975	Sedan	Grandeur IV	TG	4	EU-HYUNDAI-GRANDEUR-IV-SEDAN-01	HIGH	TG四门Sedan外廓。	READY
120007	120007	MPV	Trajet I	FO	5	EU-HYUNDAI-TRAJET-I-MPV-01	HIGH	FO五门Highway Van外廓。	READY
120008	120008	MPV	Trajet I	FO	5	EU-HYUNDAI-TRAJET-I-MPV-01	HIGH	FO五门Highway Van外廓。	READY
10161_prefl	10161	Coupe	Coupe I pre-facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖RD改款前三门外廓。	READY
10161_facelift	10161	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖RD改款后三门外廓。	READY
11139_prefl	11139	Coupe	Coupe I pre-facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖RD改款前三门外廓。	READY
11139_facelift	11139	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖RD改款后三门外廓。	READY
55793	55793	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	HIGH	RD改款后三门外廓。	READY
16168	16168	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	HIGH	RD改款后三门外廓。	READY
57273_3dr	57273	Hatchback	i20 I facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-FACELIFT-01	HIGH	PB改款后三门1.2外廓。	READY
57273_5dr	57273	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	HIGH	PB改款后五门1.2外廓。	READY
57272	57272	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	HIGH	PB改款后1.1 CRDi五门外廓。	READY
34801_prefl_3dr	34801	Hatchback	i20 I pre-facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖PB改款前三门外廓。	READY
34801_prefl_5dr	34801	Hatchback	i20 I pre-facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype生产区间覆盖PB改款前五门外廓。	READY
34801_facelift_5dr	34801	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖PB改款后1.4 CRDi五门外廓。	READY
59405_3dr	59405	Hatchback	i20 I pre-facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	MEDIUM	PB改款前1.6 CRDi三门外廓。	READY
59405_5dr	59405	Hatchback	i20 I pre-facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	MEDIUM	PB改款前1.6 CRDi五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-EQUUS-I-SEDAN-PREFL-01	5065	1870	1465	Automobile-Catalog 1999 Hyundai Equus GS 300 specifications	https://www.automobile-catalog.com/car/1999/1348370/hyundai_equus_gs_300.html
EU-HYUNDAI-EQUUS-I-SEDAN-FACELIFT-01	5120	1870	1480	Automobile-Catalog 2003 Hyundai Equus JS 350 specifications	https://www.automobile-catalog.com/car/2003/1169375/hyundai_equus_js_350.html
EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	4085	1770	1860	Automobile-Catalog 1999 Hyundai Galloper 3.0 V6 Innovation 3-Dr specifications	https://www.automobile-catalog.com/car/1999/1166135/hyundai_galloper_3_0_v6_innovation_3-dr.html
EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	4635	1770	1900	Automobile-Catalog 1999 Hyundai Galloper 3.0 V6 Exceed 5-Dr specifications	https://www.automobile-catalog.com/car/1999/1166210/hyundai_galloper_3_0_v6_exceed_5-dr.html
EU-HYUNDAI-GRANDEUR-IV-SEDAN-01	4895	1865	1490	Automobile-Catalog 2006 Hyundai Grandeur Q240 specifications	https://www.automobile-catalog.com/car/2006/1177010/hyundai_grandeur_q240.html
EU-HYUNDAI-TRAJET-I-MPV-01	4695	1840	1710	Automobile-Catalog Hyundai Trajet 2.0 CRDi and 2.0 16V specifications	https://www.automobile-catalog.com/car/2001/1169555/hyundai_trajet_2_0_crdi_gls.html;https://www.automobile-catalog.com/car/2002/1169525/hyundai_trajet_2_0_16v_gls_automatic.html
EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	4340	1730	1303	Automobile-Catalog 1998 Hyundai Coupe 1.6 specifications	https://www.automobile-catalog.com/car/1998/1165745/hyundai_coupe_1_6.html
EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	4345	1730	1303	Automobile-Catalog 2001 Hyundai Coupe 1.6 SE specifications	https://www.automobile-catalog.com/car/2001/1165880/hyundai_coupe_1_6_se.html
EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	3940	1710	1490	Automobile-Catalog Hyundai i20 I 1.4 CRDi European specifications	https://www.automobile-catalog.com/car/2010/1181180/hyundai_i20_1_4_crdi_90.html
EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	3940	1710	1490	Automobile-Catalog Hyundai i20 I 1.4 CRDi European specifications	https://www.automobile-catalog.com/car/2010/1181180/hyundai_i20_1_4_crdi_90.html
EU-HYUNDAI-I20-I-HATCHBACK-3D-FACELIFT-01	3995	1710	1490	Hyundai Motor UK i20 official brochure;Automobile-Catalog 2012 Hyundai i20 1.2 Classic specifications	https://xr793.com/wp-content/uploads/2022/09/2013-Hyundai-i20-UK.pdf;https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	3995	1710	1490	Hyundai Motor UK i20 official brochure;Automobile-Catalog 2012 Hyundai i20 1.2 Classic specifications	https://xr793.com/wp-content/uploads/2022/09/2013-Hyundai-i20-UK.pdf;https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
```

下一步优先处理

1. 先闭合第一代 H-1/Starex 的标准轴距、Jumbo 长轴及 Bus/Van 分支。
2. 将第二代 H-1 Cargo 与 Travel 按相同车身外廓批量关联，核对 Cargo 与 Travel 的车高差异。
3. 处理 Grace 与早期 H100 的 Bus、Van和改款边界。
4. 最后拆分 H100 底盘车及 H350 的 Bus、Van、底盘、轴距和车顶高度。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1999/1348370/hyundai_equus_gs_300.html?utm_source=chatgpt.com "1999 Hyundai Equus GS 300 Specs Review (145 kW / 197 PS / 194 hp) (since mid-year 1999 for Asia Korea DM)"
[2]: https://www.automobile-catalog.com/car/2009/1181105/hyundai_i20_1_6_crdi_115_style.html?utm_source=chatgpt.com "2009 Hyundai i20 1.6 CRDi 115 Style Specs Review (85 kW / 116 PS / 114 hp) (since mid-year 2009 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
更新点

* 闭合第二代 H-1 Cargo 与 H-1 Travel，共新增 8 条 READY 映射。
* Cargo 三个 CRDi Ktype 复用 TQ 货运车外廓 `5125×1920×1935 mm`；Travel 五个汽油/柴油 Ktype 复用 TQ 乘用车外廓 `5125×1920×1925 mm`。宽度均为不含后视镜车身宽度。([ICB Dubai][1])
* 输入结束年月为 `-`，未据此推定覆盖后期外观改款，也未创建猜测性的 facelift 派生行。

当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* PENDING Ktype：22
* READY 映射行：96
* 已确认尺寸组：35
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
55576	55576	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
55577	55577	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
55578	55578	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
34959	34959	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
11235	11235	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
56114	56114	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
57267	57267	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
107665	107665	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H1-II-VAN-CARGO-01	5125	1920	1935	Hyundai H1 2011 specification sheet — 6 Seater Panel Van	https://www.icbdubai.com/download/hyundai/Hyundai_H1_2011.pdf
EU-HYUNDAI-H1-II-MPV-TRAVEL-01	5125	1920	1925	Hyundai H1 2011 specification sheet — 12 Seater	https://www.icbdubai.com/download/hyundai/Hyundai_H1_2011.pdf
```

下一步优先处理

1. 闭合第一代 H-1/Starex A1 的标准轴距、长轴、改款前后及 Bus/Van 分支。
2. 处理 Grace 与早期 H100 的 Bus、Van及改款边界。
3. 拆分 H100 底盘车和 H350 的轴距、车顶高度及 Bus/Van/底盘分支。

推进信号：CONTINUE

[1]: https://www.icbdubai.com/download/hyundai/Hyundai_H1_2011.pdf?utm_source=chatgpt.com "Microsoft Word - Hyundai_H1_2011.doc-1"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
更新点

* 闭合全部 6 个 H350 Ktype，共新增 9 条 READY 映射。
* H350 Bus 的 150 PS、170 PS 复用中轴 Bus 外廓。
* H350 Van 的两个动力版本均拆分为 SWB 与 LWB；H350 底盘车 170 PS 仅关联中轴，150 PS 同时关联短轴与中轴。Hyundai 官方规格明确列出各车身的长度、车宽不含后视镜口径及高度。([现代汽车货车与客车][1])

当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* PENDING Ktype：16
* READY 映射行：105
* 已确认尺寸组：40
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
113116	113116	MPV	H350			EU-HYUNDAI-H350-BUS-LWB-01	HIGH	H350中轴Bus外廓。	READY
113118	113118	MPV	H350			EU-HYUNDAI-H350-BUS-LWB-01	HIGH	H350中轴Bus外廓。	READY
113119_swb	113119	Van	H350			EU-HYUNDAI-H350-VAN-SWB-01	HIGH	H350短轴封闭式货运车外廓。	READY
113119_lwb	113119	Van	H350			EU-HYUNDAI-H350-VAN-LWB-01	HIGH	H350中轴封闭式货运车外廓。	READY
113120_swb	113120	Van	H350			EU-HYUNDAI-H350-VAN-SWB-01	HIGH	H350短轴封闭式货运车外廓。	READY
113120_lwb	113120	Van	H350			EU-HYUNDAI-H350-VAN-LWB-01	HIGH	H350中轴封闭式货运车外廓。	READY
113122_lwb	113122	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-LWB-01	HIGH	170 PS底盘车中轴驾驶室外廓。	READY
113123_swb	113123	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-SWB-01	HIGH	150 PS底盘车短轴驾驶室外廓。	READY
113123_lwb	113123	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-LWB-01	HIGH	150 PS底盘车中轴驾驶室外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H350-BUS-LWB-01	6195	2038	2673	Hyundai Commercial Vehicle H350 official specifications — Bus medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-VAN-SWB-01	5515	2038	2685	Hyundai Commercial Vehicle H350 official specifications — Van short body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-VAN-LWB-01	6195	2038	2690	Hyundai Commercial Vehicle H350 official specifications — Van medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-CHASSIS-SWB-01	5724	2038	2320	Hyundai Commercial Vehicle H350 official specifications — Truck short body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-CHASSIS-LWB-01	6167	2038	2320	Hyundai Commercial Vehicle H350 official specifications — Truck medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
```

下一步优先处理

1. 集中闭合第一代 H-1/Starex 的标准轴距、Jumbo 长轴、Bus与Van分支。
2. 处理 Grace 与早期 H100 的共用车身、改款边界和Bus/Van差异。
3. 最后闭合 H100 底盘车；PENDING 清零后立即进行一次机械检查并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521&utm_source=chatgpt.com "H350"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
更新点

* 闭合第一代 H-1 Kasten 的 5 个 Ktype，统一关联 A1 长轴封闭式货运车外廓。
* 该欧洲 Kasten 车身外廓为 `5035×1820×1980 mm`；2.5 TD 与 2.5 CRDi 的车辆资料均指向同一长轴货运车身，发动机差异未重复建组。([Gazoo][1])
* `54936` 属于 H-1/Starex Bus，不复用 Kasten 尺寸组，留待按短轴、长轴乘用车外廓独立闭合。([汽车配件商店][2])

当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* PENDING Ktype：11
* READY 映射行：110
* 已确认尺寸组：41
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14737	14737	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
17758	17758	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
14736	14736	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	MEDIUM	A1长轴封闭式货运外廓。	READY
15381	15381	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
17466	17466	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H1-I-VAN-LWB-01	5035	1820	1980	Croatian vehicle homologation database Hyundai H-1 Furgon 2.5 CRDi;Autosieger Hyundai H-1 Kastenwagen technical data	https://jomologia.hr/Detalji?id=30818&redniBroj=0;https://www.autosieger.de/hyundai-h-1-Autokatalog216.html
```

下一步优先处理

1. 闭合 `54936` H-1/Starex Bus 的短轴、长轴乘用车分支。
2. 将 Grace 与 Grace-based H100 Bus/Van 批量关联至已确认的共用外廓。
3. 最后独立处理 `55625` Porter II/H100 底盘车，随后清零 PENDING 并输出最终完整产物。

推进信号：CONTINUE

[1]: https://gazoo.pl/samochody/hyundai/hyundai-h-1/wymiary/?utm_source=chatgpt.com "Wymiary Hyundai H-1 - długość, szerokość, wysokość, rozstaw osi - gazoo.pl"
[2]: https://www.autoersatzteile.de/hyundai-autoteile/h-1-starex/54936?utm_source=chatgpt.com "Ersatzteile Hyundai H1 Starex 2.5 CRDi 163 PS D4CB 2002 - 2004"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6701-6800_ktype_dimension_mapping_final.tsv
- left18448_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 最后 11 个商用车 Ktype 已闭合：H-1 I 长轴乘用 Bus、Grace/H100 乘用及货运车身、H100 II/Porter II 标准驾驶室长轴底盘车。
* H-1 I 长轴乘用版采用 `5035×1820×1965 mm`；Grace/H100 共用基础车身采用 `4790×1690×1965 mm`；H100 II 标准驾驶室长轴低货台采用 `4850×1740×1970 mm`。([汽车数据网][1])
* 已完成轻量机械检查：表头正确、121 个 `id` 唯一、45 个尺寸组唯一、映射引用全部闭合、无孤立尺寸组，尺寸及来源字段均非空。
* 两个指定文件已创建并通过校验。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* READY 映射行：121
* 已确认尺寸组：45
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
111963_prefl	111963	Sedan	Equus I pre-facelift		4	EU-HYUNDAI-EQUUS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖2003年改款前四门外廓。	READY
111963_facelift	111963	Sedan	Equus I facelift		4	EU-HYUNDAI-EQUUS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖2003年改款后四门外廓。	READY
54907	54907	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
54905	54905	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
54906	54906	Sedan	Equus II		4	EU-HYUNDAI-EQUUS-II-SEDAN-01	HIGH	第二代四门标准轴距外廓。	READY
16943_swb	16943	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
16943_lwb	16943	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
15145_swb	15145	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
15145_lwb	15145	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
15144_swb	15144	SUV	Galloper II		3	EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	MEDIUM	三门短轴外廓。	READY
15144_lwb	15144	SUV	Galloper II		5	EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	MEDIUM	五门长轴外廓。	READY
117566	117566	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
55398	55398	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
59400	59400	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
108015	108015	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
108016	108016	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
111966_prefl	111966	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
111966_facelift	111966	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
111979_prefl	111979	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
111979_facelift	111979	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
53682	53682	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	HIGH	3.8 GDI对应改款后四门外廓。	READY
116891	116891	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
108014	108014	Sedan	Genesis II	DH	4	EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	HIGH	DH四门Sedan外廓。	READY
52428_prefl	52428	Sedan	Genesis I pre-facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	MEDIUM	Ktype生产区间覆盖改款前外廓。	READY
52428_facelift	52428	Sedan	Genesis I facelift	BH	4	EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	MEDIUM	Ktype生产区间覆盖改款后外廓。	READY
55397	55397	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
59399	59399	Coupe	Genesis Coupe I facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	HIGH	BK改款双门Coupe外廓。	READY
16978_3dr	16978	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16978_5dr	16978	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
18027_3dr	18027	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
18027_5dr	18027	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16813_3dr	16813	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16813_5dr	16813	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16814_3dr	16814	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16814_5dr	16814	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
16812_3dr	16812	Hatchback	Getz I pre-facelift	TB	3	EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	MEDIUM	TB改款前三门外廓。	READY
16812_5dr	16812	Hatchback	Getz I pre-facelift	TB	5	EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	MEDIUM	TB改款前五门外廓。	READY
57620	57620	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	Grace/H100封闭式货运外廓。	READY
117567	117567	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	Grace/H100封闭式货运外廓。	READY
116960	116960	SUV	Grand Santa Fe III	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	HIGH	NC长轴五门SUV外廓。	READY
100972	100972	SUV	Grand Santa Fe III	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	HIGH	NC长轴五门SUV外廓。	READY
111975	111975	Sedan	Grandeur IV	TG	4	EU-HYUNDAI-GRANDEUR-IV-SEDAN-01	HIGH	TG四门Sedan外廓。	READY
154669	154669	Sedan	Grandeur VII	GN7	4	EU-HYUNDAI-GRANDEUR-VII-SEDAN-01	HIGH	GN7四门Hybrid Sedan外廓。	READY
111980	111980	Sedan	Grandeur V	HG	4	EU-HYUNDAI-GRANDEUR-V-SEDAN-01	HIGH	HG四门Sedan外廓。	READY
111981	111981	Sedan	Grandeur V	HG	4	EU-HYUNDAI-GRANDEUR-V-SEDAN-01	HIGH	HG四门Sedan外廓。	READY
14737	14737	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
17758	17758	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
14736	14736	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	MEDIUM	A1长轴封闭式货运外廓。	READY
15381	15381	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
17466	17466	Van	H-1 I	A1	4	EU-HYUNDAI-H1-I-VAN-LWB-01	HIGH	A1长轴封闭式货运外廓。	READY
54936	54936	MPV	H-1 I	A1	4	EU-HYUNDAI-H1-I-MPV-LWB-01	HIGH	A1长轴乘用Bus外廓。	READY
55576	55576	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
55577	55577	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
55578	55578	Van	H-1 II	TQ		EU-HYUNDAI-H1-II-VAN-CARGO-01	HIGH	TQ Cargo货运外廓。	READY
34959	34959	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
11235	11235	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
56114	56114	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
57267	57267	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
107665	107665	MPV	H-1 II	TQ	5	EU-HYUNDAI-H1-II-MPV-TRAVEL-01	HIGH	TQ Travel乘用外廓。	READY
14192	14192	MPV	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-MPV-01	MEDIUM	H100/Grace乘用Bus外廓。	READY
113299	113299	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	H100/Grace封闭式货运外廓。	READY
55625	55625	Pickup	H100 II / Porter II	HR	2	EU-HYUNDAI-H100-II-PICKUP-STDCAB-LWB-01	MEDIUM	HR标准驾驶室长轴低货台外廓。	READY
8169	8169	MPV	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-MPV-01	MEDIUM	H100/Grace乘用Bus外廓。	READY
10559	10559	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	H100/Grace封闭式货运外廓。	READY
10560	10560	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	H100/Grace封闭式货运外廓。	READY
15919	15919	MPV	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-MPV-01	MEDIUM	H100/Grace乘用Bus外廓。	READY
56036	56036	Van	H100 / Grace I	P		EU-HYUNDAI-H100-GRACE-I-VAN-01	MEDIUM	H100/Grace封闭式货运外廓。	READY
113116	113116	MPV	H350			EU-HYUNDAI-H350-BUS-LWB-01	HIGH	H350中轴Bus外廓。	READY
113118	113118	MPV	H350			EU-HYUNDAI-H350-BUS-LWB-01	HIGH	H350中轴Bus外廓。	READY
113119_swb	113119	Van	H350			EU-HYUNDAI-H350-VAN-SWB-01	HIGH	H350短轴封闭式货运车外廓。	READY
113119_lwb	113119	Van	H350			EU-HYUNDAI-H350-VAN-LWB-01	HIGH	H350中轴封闭式货运车外廓。	READY
113120_swb	113120	Van	H350			EU-HYUNDAI-H350-VAN-SWB-01	HIGH	H350短轴封闭式货运车外廓。	READY
113120_lwb	113120	Van	H350			EU-HYUNDAI-H350-VAN-LWB-01	HIGH	H350中轴封闭式货运车外廓。	READY
113122_lwb	113122	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-LWB-01	HIGH	170 PS底盘车中轴驾驶室外廓。	READY
113123_swb	113123	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-SWB-01	HIGH	150 PS底盘车短轴驾驶室外廓。	READY
113123_lwb	113123	Pickup	H350			EU-HYUNDAI-H350-CHASSIS-LWB-01	HIGH	150 PS底盘车中轴驾驶室外廓。	READY
120007	120007	MPV	Trajet I	FO	5	EU-HYUNDAI-TRAJET-I-MPV-01	HIGH	FO五门Highway Van外廓。	READY
120008	120008	MPV	Trajet I	FO	5	EU-HYUNDAI-TRAJET-I-MPV-01	HIGH	FO五门Highway Van外廓。	READY
10161_prefl	10161	Coupe	Coupe I pre-facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖RD改款前三门外廓。	READY
10161_facelift	10161	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖RD改款后三门外廓。	READY
11139_prefl	11139	Coupe	Coupe I pre-facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖RD改款前三门外廓。	READY
11139_facelift	11139	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖RD改款后三门外廓。	READY
55793	55793	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	HIGH	RD改款后三门外廓。	READY
16168	16168	Coupe	Coupe I facelift	RD	3	EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	HIGH	RD改款后三门外廓。	READY
59401	59401	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	HIGH	PA五门外廓。	READY
120679	120679	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	MEDIUM	PA五门外廓。	READY
14034	14034	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-01	MEDIUM	PA五门外廓。	READY
100581	100581	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
100584	100584	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
115521	115521	Sedan	i10 II / Xcent	BA	4	EU-HYUNDAI-I10-II-SEDAN-4D-01	MEDIUM	BA四门Xcent Sedan外廓。	READY
100792	100792	Hatchback	i10 II	IA	5	EU-HYUNDAI-I10-II-HATCHBACK-5D-01	HIGH	IA五门外廓。	READY
800262	800262	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-5D-01	HIGH	第三代五门标准外廓。	READY
800264	800264	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-NLINE-01	HIGH	1.0 T-GDI对应N Line五门外廓。	READY
800263	800263	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-5D-01	HIGH	第三代五门标准外廓。	READY
122142	122142	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
122145	122145	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
122150	122150	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	HIGH	Active加高五门外廓。	READY
57273_3dr	57273	Hatchback	i20 I facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-FACELIFT-01	HIGH	PB改款后三门1.2外廓。	READY
57273_5dr	57273	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	HIGH	PB改款后五门1.2外廓。	READY
57272	57272	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	HIGH	PB改款后1.1 CRDi五门外廓。	READY
34801_prefl_3dr	34801	Hatchback	i20 I pre-facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype生产区间覆盖PB改款前三门外廓。	READY
34801_prefl_5dr	34801	Hatchback	i20 I pre-facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype生产区间覆盖PB改款前五门外廓。	READY
34801_facelift_5dr	34801	Hatchback	i20 I facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype生产区间覆盖PB改款后1.4 CRDi五门外廓。	READY
59405_3dr	59405	Hatchback	i20 I pre-facelift	PB	3	EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	MEDIUM	PB改款前1.6 CRDi三门外廓。	READY
59405_5dr	59405	Hatchback	i20 I pre-facelift	PB	5	EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	MEDIUM	PB改款前1.6 CRDi五门外廓。	READY
108798	108798	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
108806	108806	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
121091	121091	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
108807	108807	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
114617	114617	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
118529	118529	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
118530	118530	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
108809	108809	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
121094	121094	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
108810	108810	Hatchback	i20 II		5	EU-HYUNDAI-I20-II-HATCHBACK-5D-01	HIGH	第二代五门外廓。	READY
114618	114618	Coupe	i20 II		3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH	第二代三门Coupe独立外廓。	READY
159193	159193	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	HIGH	第三代五门改款后标准外廓。	READY
802507	802507	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	MEDIUM	2025年Ktype按第三代改款后标准五门外廓关联。	READY
801093	801093	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-02	HIGH	第三代五门改款后标准外廓。	READY
146414	146414	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-5D-01	HIGH	第三代五门改款前标准外廓。	READY
145703	145703	Hatchback	i20 III		5	EU-HYUNDAI-I20-III-HATCHBACK-N-01	HIGH	N高性能版独立外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6701-6800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-EQUUS-I-SEDAN-PREFL-01	5065	1870	1465	Automobile-Catalog 1999 Hyundai Equus GS 300 specifications	https://www.automobile-catalog.com/car/1999/1348370/hyundai_equus_gs_300.html
EU-HYUNDAI-EQUUS-I-SEDAN-FACELIFT-01	5120	1870	1480	Automobile-Catalog 2003 Hyundai Equus JS 350 specifications	https://www.automobile-catalog.com/car/2003/1169375/hyundai_equus_js_350.html
EU-HYUNDAI-EQUUS-II-SEDAN-01	5160	1890	1490	Hyundai Motor America 2011 Equus engineering information;Hyundai Motor America 2014 Equus official press information	https://www.hyundainews.com/assets/documents/original/10865-HYUNDAIRELEASESENGINEERINGANDFEATUREINFORMATIONFORTHEALL-NEW2011HYUNDAIEQUUS.pdf;https://www.hyundainews.com/assets/documents/original/22126-REDESIGNED2014EQUUSOFFERSDRIVER-FOCUSEDTECHNOLOGIES%2CPREMIUMDESIGN%2CSUSPENSIONREFINEMENTANDADVANCEDSAFETYFEATURES.pdf
EU-HYUNDAI-GALLOPER-II-SUV-SWB-01	4085	1770	1860	Automobile-Catalog 1999 Hyundai Galloper 3.0 V6 Innovation 3-Dr specifications	https://www.automobile-catalog.com/car/1999/1166135/hyundai_galloper_3_0_v6_innovation_3-dr.html
EU-HYUNDAI-GALLOPER-II-SUV-LWB-01	4635	1770	1900	Automobile-Catalog 1999 Hyundai Galloper 3.0 V6 Exceed 5-Dr specifications	https://www.automobile-catalog.com/car/1999/1166210/hyundai_galloper_3_0_v6_exceed_5-dr.html
EU-HYUNDAI-GENESIS-COUPE-I-FACELIFT-2D-01	4630	1864	1384	Hyundai 2013 Genesis Coupe official brochure archive	https://xr793.com/wp-content/uploads/2017/02/2013-Hyundai-Genesis-Coupe.pdf
EU-HYUNDAI-GENESIS-II-SEDAN-4D-01	4990	1890	1480	Hyundai Motor Deutschland Genesis Sportlimousine technical data;Hyundai Motor Company All-New Genesis launch specifications	https://www.hyundai.news/newsroom/dam/de/Pressemappen/Genesis_Sportlimousine/genesis_sportlimousine_2014_3_technische_daten_d7205f1.pdf;https://www.hyundai.com/content/hyundai/ww/data/news/data/2013/0000002864/attach/131126_Hyundai%20All%20New%20Genesis%20Launch%20in%20Korea.doc
EU-HYUNDAI-GENESIS-I-SEDAN-PREFL-01	4976	1890	1481	Hyundai Motor America 2009 Genesis official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-Genesis-2009-USA.pdf
EU-HYUNDAI-GENESIS-I-SEDAN-FACELIFT-01	4985	1890	1480	Hyundai Canada 2012 Genesis Sedan official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2012_genesis_sedan.pdf
EU-HYUNDAI-GETZ-I-HATCHBACK-3D-PREFL-01	3810	1665	1495	Hyundai Motor Company Australia Getz official specification sheet	https://xr793.com/wp-content/uploads/2023/04/2005-Hyundai-Getz-Specs-AUS.pdf
EU-HYUNDAI-GETZ-I-HATCHBACK-5D-PREFL-01	3810	1665	1495	Hyundai Motor Company Australia Getz official specification sheet	https://xr793.com/wp-content/uploads/2023/04/2005-Hyundai-Getz-Specs-AUS.pdf
EU-HYUNDAI-H100-GRACE-I-VAN-01	4790	1690	1965	Auto.ru Hyundai Grace 1986-2004 dimensions	https://auto.ru/catalog/cars/hyundai/grace/specifications/
EU-HYUNDAI-GRAND-SANTA-FE-III-SUV-01	4915	1885	1695	Hyundai Motor Deutschland Grand Santa Fe official technical data	https://www.hyundai.news/newsroom/dam/de/Pressemappen/Grand_Santa_Fe/hyundai_grand_santa_fe_technische_daten_2018.pdf
EU-HYUNDAI-GRANDEUR-IV-SEDAN-01	4895	1865	1490	Automobile-Catalog 2006 Hyundai Grandeur Q240 specifications	https://www.automobile-catalog.com/car/2006/1177010/hyundai_grandeur_q240.html
EU-HYUNDAI-GRANDEUR-VII-SEDAN-01	5035	1880	1460	Hyundai Motor Company Grandeur official English catalog	https://www.hyundai.com/content/dam/hyundai/kr/ko/data/vehicles/catalog/en/grandeur-catalog-eng.pdf
EU-HYUNDAI-GRANDEUR-V-SEDAN-01	4910	1860	1470	Hyundai Motor America Azera official press information;Hyundai Azera 2012 Owner's Manual	https://www.hyundainews.com/assets/documents/original/21808-2013AZERA%3AMODERNDESIGN%2CSMARTTECHNOLOGY%2CPERFORMANCEANDSAFETY.pdf;https://www.carmanualsonline.info/hyundai-azera-2012-owner-s-manual/?srch=dimensions
EU-HYUNDAI-H1-I-VAN-LWB-01	5035	1820	1980	Croatian vehicle homologation database Hyundai H-1 Furgon 2.5 CRDi;Autosieger Hyundai H-1 Kastenwagen technical data	https://jomologia.hr/Detalji?id=30818&redniBroj=0;https://www.autosieger.de/hyundai-h-1-Autokatalog216.html
EU-HYUNDAI-H1-I-MPV-LWB-01	5035	1820	1965	Auto-Data Hyundai H-1 I Starex 2.5 CRDI LWB specifications	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-crdi-lwb-140hp-13855
EU-HYUNDAI-H1-II-VAN-CARGO-01	5125	1920	1935	Hyundai H1 2011 specification sheet — 6 Seater Panel Van	https://www.icbdubai.com/download/hyundai/Hyundai_H1_2011.pdf
EU-HYUNDAI-H1-II-MPV-TRAVEL-01	5125	1920	1925	Hyundai H1 2011 specification sheet — 12 Seater	https://www.icbdubai.com/download/hyundai/Hyundai_H1_2011.pdf
EU-HYUNDAI-H100-GRACE-I-MPV-01	4790	1690	1965	Auto.ru Hyundai Grace 1986-2004 dimensions	https://auto.ru/catalog/cars/hyundai/grace/specifications/
EU-HYUNDAI-H100-II-PICKUP-STDCAB-LWB-01	4850	1740	1970	Hyundai Motor Company H100 official brochure — LWB standard cab low deck	https://www.hyundai.sc/sites/default/files/hyundai-h100.pdf
EU-HYUNDAI-H350-BUS-LWB-01	6195	2038	2673	Hyundai Commercial Vehicle H350 official specifications — Bus medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-VAN-SWB-01	5515	2038	2685	Hyundai Commercial Vehicle H350 official specifications — Van short body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-VAN-LWB-01	6195	2038	2690	Hyundai Commercial Vehicle H350 official specifications — Van medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-CHASSIS-LWB-01	6167	2038	2320	Hyundai Commercial Vehicle H350 official specifications — Truck medium body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-H350-CHASSIS-SWB-01	5724	2038	2320	Hyundai Commercial Vehicle H350 official specifications — Truck short body	https://trucknbus.hyundai.com/global/file/downloadBlb?fil_sn=BF00001521
EU-HYUNDAI-TRAJET-I-MPV-01	4695	1840	1710	Automobile-Catalog Hyundai Trajet 2.0 CRDi and 2.0 16V specifications	https://www.automobile-catalog.com/car/2001/1169555/hyundai_trajet_2_0_crdi_gls.html;https://www.automobile-catalog.com/car/2002/1169525/hyundai_trajet_2_0_16v_gls_automatic.html
EU-HYUNDAI-COUPE-I-COUPE-3D-PREFL-01	4340	1730	1303	Automobile-Catalog 1998 Hyundai Coupe 1.6 specifications	https://www.automobile-catalog.com/car/1998/1165745/hyundai_coupe_1_6.html
EU-HYUNDAI-COUPE-I-COUPE-3D-FACELIFT-01	4345	1730	1303	Automobile-Catalog 2001 Hyundai Coupe 1.6 SE specifications	https://www.automobile-catalog.com/car/2001/1165880/hyundai_coupe_1_6_se.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-01	3565	1595	1540	Hyundai Motor UK i10 2011 Model Year official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Hyundai-i10-UK.pdf
EU-HYUNDAI-I10-II-HATCHBACK-5D-01	3665	1660	1500	Hyundai Ireland New i10 official brochure	https://www.hyundai.ie/assets/i10-brochure.pdf
EU-HYUNDAI-I10-II-SEDAN-4D-01	3995	1660	1520	Hyundai Motor India XCENT official brochure	https://www.hyundai.com/content/dam/hyundai/in/en/data/build-a-car/download-e-broucher/XCENT_Sedan_brochure.pdf
EU-HYUNDAI-I10-III-HATCHBACK-5D-01	3670	1680	1480	Hyundai Motor UK i10 technical specifications MY25	https://www.hyundai.news/newsroom/dam/uk/press-kits/hyundai-uk-i10-tech-spec-pricing-model-year-2025-0424.pdf
EU-HYUNDAI-I10-III-HATCHBACK-NLINE-01	3670	1680	1483	Hyundai Motor UK i10 technical specifications MY25	https://www.hyundai.news/newsroom/dam/uk/press-kits/hyundai-uk-i10-tech-spec-pricing-model-year-2025-0424.pdf
EU-HYUNDAI-I20-II-HATCHBACK-ACTIVE-01	4065	1760	1529	Hyundai Motor UK i20 2017 Model Year official brochure	https://xr793.com/wp-content/uploads/2022/09/2017-Hyundai-i20-UK.pdf
EU-HYUNDAI-I20-I-HATCHBACK-3D-FACELIFT-01	3995	1710	1490	Hyundai Motor UK i20 official brochure;Automobile-Catalog 2012 Hyundai i20 1.2 Classic specifications	https://xr793.com/wp-content/uploads/2022/09/2013-Hyundai-i20-UK.pdf;https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
EU-HYUNDAI-I20-I-HATCHBACK-5D-FACELIFT-01	3995	1710	1490	Hyundai Motor UK i20 official brochure;Automobile-Catalog 2012 Hyundai i20 1.2 Classic specifications	https://xr793.com/wp-content/uploads/2022/09/2013-Hyundai-i20-UK.pdf;https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
EU-HYUNDAI-I20-I-HATCHBACK-3D-PREFL-01	3940	1710	1490	Automobile-Catalog Hyundai i20 I 1.4 CRDi European specifications	https://www.automobile-catalog.com/car/2010/1181180/hyundai_i20_1_4_crdi_90.html
EU-HYUNDAI-I20-I-HATCHBACK-5D-PREFL-01	3940	1710	1490	Automobile-Catalog Hyundai i20 I 1.4 CRDi European specifications	https://www.automobile-catalog.com/car/2010/1181180/hyundai_i20_1_4_crdi_90.html
EU-HYUNDAI-I20-II-HATCHBACK-5D-01	4035	1734	1474	Hyundai Motor UK i20 PLAY technical specifications	https://www.hyundai.news/newsroom/dam/eu/uk/20190729_model_i20_play/i20_PLAY_Release_technical.pdf
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449	Hyundai Motor Europe New Generation i20 Coupe press information	https://www.hyundai.news/newsroom/dam/eu/press-kits/2015_i20_coupe/NewGeneration_i20_Coupe_Press_Information_032015.pdf
EU-HYUNDAI-I20-III-HATCHBACK-5D-02	4065	1775	1450	Hyundai Motor Europe i20 technical data August 2023	https://www.hyundai.news/newsroom/dam/eu/press-kits/20230908_i20/hyundai-i20-technical-data-0823.pdf
EU-HYUNDAI-I20-III-HATCHBACK-5D-01	4040	1775	1450	Hyundai Motor Europe i20 and i20 N Line technical data June 2021	https://www.hyundai.news/newsroom/dam/eu/models/20210610_sop_i20_n_and_i20_n_line/hyundai-sop-i20-and-i20-n-line-tech-data.pdf
EU-HYUNDAI-I20-III-HATCHBACK-N-01	4075	1775	1440	Hyundai Motor UK i20 N technical data June 2021	https://www.hyundai.news/newsroom/dam/eu/uk/20210617_i20_n_pricing_specs/hyundai-uk-i20-n-technical-data-0621.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6701-6800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-crdi-lwb-140hp-13855 "Hyundai H-1 I Starex 2.5 CRDI LWB (140 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3820 行）
- 累计尺寸组：dimension_groups_final.tsv（1058 行）

