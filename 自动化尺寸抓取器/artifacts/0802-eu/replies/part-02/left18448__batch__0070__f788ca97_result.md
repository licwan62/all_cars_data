# 任务：left18448 第 6901-7000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0070__f788ca97


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6901-7000 行

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
left18448 第 6901-7000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6901-7000_ktype_dimension_mapping_final.tsv
- left18448_6901-7000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Hyundai	Ix20	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Jun 2011	Jul 2019	10602
Hyundai	Ix20	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Jun 2011	Jul 2019	59408
Hyundai	Ix35	2.0 4WD	SUV	Allrad	Benzin	Sep 2014	Jun 2015	125220
Hyundai	Ix35	2.0 Cvvt	SUV	Frontantrieb	Benzin	Aug 2009	Jul 2013	114089
Hyundai	Ix35	2.0 Cvvt 4WD	SUV	Allrad	Benzin	Aug 2013	Dec 2015	128236
Hyundai	Ix35	2.0 GDI	SUV	Frontantrieb	Benzin	Aug 2013	Dec 2015	100807
Hyundai	Ix35	2.0 GDI 4WD	SUV	Allrad	Benzin	Aug 2013	Dec 2015	100805
Hyundai	Ix35	2.4 Dcvvt-i 4WD	SUV	Allrad	Benzin	Jul 2010	Dec 2013	110519
Hyundai	Ix35	Crdi	Kasten/SUV	Frontantrieb	Diesel	Sep 2010	Dec 2015	142773
Hyundai	Ix35	Crdi	Kasten/SUV	Frontantrieb	Diesel	Aug 2009	Dec 2015	142776
Hyundai	Ix35	Crdi 4WD	Kasten/SUV	Allrad	Diesel	Aug 2009	Dec 2015	143063
Hyundai	Ix35	Fcev	SUV	Frontantrieb	Wasserstoff	Oct 2012	-	110481
Hyundai	Ix35	Fuel Cell	SUV	Frontantrieb	Wasserstoff	Sep 2014	Dec 2015	109541
Hyundai	Ix35	GDI	Kasten/SUV	Frontantrieb	Benzin	May 2015	Dec 2015	142769
Hyundai	Ix55	3.0 V6 Crdi 4WD	SUV	Allrad	Diesel	Sep 2011	Dec 2012	12258
Hyundai	Ix55	3.8 V6	SUV	Frontantrieb	Benzin	Jan 2011	Nov 2012	55399
Hyundai	Ix55	3.8 V6 4WD	SUV	Allrad	Benzin	Jan 2011	Nov 2012	55400
Hyundai	Kona	1.0 T-gdi	SUV	Frontantrieb	Benzin	Jul 2017	Apr 2023	128293
Hyundai	Kona	1.0 T-gdi	SUV	Frontantrieb	Benzin	Apr 2023	-	154502
Hyundai	Kona	1.0 T-gdi	SUV	Frontantrieb	Benzin	Apr 2023	-	801332
Hyundai	Kona	1.0 T-gdi	SUV	Frontantrieb	Benzin	Aug 2025	-	802217
Hyundai	Kona	1.0 T-gdi GPL	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jul 2025	-	802519
Hyundai	Kona	1.0 T-gdi Hybrid 48V	SUV	Frontantrieb	Benzin/Elektro	Nov 2020	Apr 2023	142767
Hyundai	Kona	1.0 T-gdi Hybrid 48V	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	153711
Hyundai	Kona	1.0 T-gdi Hybrid 48V	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	801333
Hyundai	Kona	1.6 Crdi Hybrid 48V	SUV	Frontantrieb	Diesel/Elektro	Nov 2020	Aug 2021	142770
Hyundai	Kona	1.6 Crdi Hybrid 48V 4WD	SUV	Allrad	Diesel/Elektro	Nov 2020	Aug 2021	142777
Hyundai	Kona	1.6 GDI Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2024	-	801147
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Jul 2017	Dec 2020	128030
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Nov 2020	Apr 2023	142772
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Apr 2023	-	154503
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Sep 2024	-	801025
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Apr 2024	-	801314
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Aug 2025	-	802218
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	Aug 2025	-	802219
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	Jun 2017	Mar 2023	128292
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	Nov 2020	Apr 2023	142774
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	Apr 2023	-	154505
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	Apr 2024	-	801313
Hyundai	Kona	1.6 T-gdi 4WD	SUV	Allrad	Benzin	Aug 2025	-	802220
Hyundai	Kona	1.6 T-gdi HEV	SUV	Frontantrieb	Benzin/Elektro	Aug 2025	-	802221
Hyundai	Kona	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	153710
Hyundai	Kona	2.0 N	SUV	Frontantrieb	Benzin	Jul 2021	Mar 2023	145514
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	Jul 2023	-	155214
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	Jul 2023	-	155215
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	Jul 2023	-	157457
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	Jul 2023	-	157520
Hyundai	Kona	EV	SUV	Frontantrieb	Elektro	Jul 2023	-	157900
Hyundai	Kona	GDI Hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2023	-	156030
Hyundai	Lantra ii	1.9 D	Stufenheck	Frontantrieb	Diesel	Mar 1998	Sep 2000	14769
Hyundai	Lantra ii	1.9 D	Kombi	Frontantrieb	Diesel	Mar 1998	Oct 2000	14770
Hyundai	Lantra ii	2.0 16V	Stufenheck	Frontantrieb	Benzin	Aug 1996	Sep 2000	7824
Hyundai	Matrix	1.6	Großraumlimousine	Frontantrieb	Benzin	Jun 2001	Aug 2010	16001
Hyundai	Matrix	1.5 Crdi	Großraumlimousine	Frontantrieb	Diesel	Dec 2004	Aug 2010	18753
Hyundai	Nexo	Fcfv	SUV	Frontantrieb	Wasserstoff	May 2025	-	162910
Hyundai	Porter	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2012	-	117370
Hyundai	Santa fé i	2	SUV	Frontantrieb	Benzin	Aug 2001	Mar 2006	18024
Hyundai	Santa fé i	2.0 Crdi 4X4	SUV	Allrad	Diesel	Apr 2001	Mar 2006	15974
Hyundai	Santa fé i	2.4 16V	SUV	Frontantrieb	Benzin	Feb 2001	Mar 2006	15376
Hyundai	Santa fé i	2.4 16V	SUV	Frontantrieb	Benzin	Feb 2001	Mar 2006	16171
Hyundai	Santa fé i	2.4 16V 4X4	SUV	Allrad	Benzin	Feb 2001	Mar 2006	16002
Hyundai	Santa fé i	2.4 16V 4X4	SUV	Allrad	Benzin	Feb 2001	Mar 2006	16172
Hyundai	Santa fé i	2.4 4X4	Kasten/SUV	Allrad	Benzin	Aug 2000	Dec 2005	142802
Hyundai	Santa fé i	2.7 4X4	SUV	Allrad	Benzin	Sep 2002	Dec 2004	109535
Hyundai	Santa fé i	2.7 V6 4X4	SUV	Allrad	Benzin	Feb 2001	Mar 2006	15378
Hyundai	Santa fé i	Crdi	Kasten/SUV	Frontantrieb	Diesel	Aug 2001	Jul 2003	142804
Hyundai	Santa fé i	Crdi 4X4	Kasten/SUV	Allrad	Diesel	Apr 2001	Dec 2005	142805
Hyundai	Santa fé i	Crdi 4X4	Kasten/SUV	Allrad	Diesel	Aug 2003	Mar 2006	142806
Hyundai	Santa fé ii	2.0 Crdi 4X4	SUV	Allrad	Diesel	Mar 2006	Dec 2012	111969
Hyundai	Santa fé ii	2.2 Crdi	SUV	Frontantrieb	Diesel	Jan 2009	Dec 2012	34960
Hyundai	Santa fé ii	2.2 Crdi 4X4	SUV	Allrad	Diesel	Jan 2009	Dec 2012	34961
Hyundai	Santa fé ii	2.4 4X4	SUV	Allrad	Benzin	Jul 2010	Dec 2012	34963
Hyundai	Santa fé ii	Crdi	Kasten/SUV	Frontantrieb	Diesel	Sep 2006	Dec 2011	142809
Hyundai	Santa fé ii	Crdi	Kasten/SUV	Frontantrieb	Diesel	Jan 2009	May 2013	142812
Hyundai	Santa fé ii	Crdi 4X4	Kasten/SUV	Allrad	Diesel	Sep 2006	Dec 2011	142810
Hyundai	Santa fé ii	Crdi 4X4	Kasten/SUV	Allrad	Diesel	Nov 2005	Dec 2011	142811
Hyundai	Santa fé ii	Crdi 4X4	Kasten/SUV	Allrad	Diesel	Jan 2009	May 2013	142813
Hyundai	Santa fé iii	2.4	SUV	Frontantrieb	Benzin	Sep 2012	Oct 2015	55794
Hyundai	Santa fé iii	2.0 Crdi	SUV	Frontantrieb	Diesel	Sep 2012	Aug 2018	55795
Hyundai	Santa fé iii	2.0 Crdi	SUV	Frontantrieb	Diesel	May 2015	Aug 2018	117229
Hyundai	Santa fé iii	2.0 Crdi 4WD	SUV	Allrad	Diesel	Sep 2012	Aug 2018	56797
Hyundai	Santa fé iii	2.0 Crdi 4WD	SUV	Allrad	Diesel	Sep 2012	Aug 2018	127211
Hyundai	Santa fé iii	2.2 Crdi	SUV	Frontantrieb	Diesel	Sep 2012	Dec 2018	55796
Hyundai	Santa fé iii	2.2 Crdi	SUV	Frontantrieb	Diesel	Oct 2015	Aug 2018	117226
Hyundai	Santa fé iii	2.2 Crdi 4WD	SUV	Allrad	Diesel	Sep 2012	Dec 2018	55797
Hyundai	Santa fé iii	2.2 Crdi 4WD	SUV	Allrad	Diesel	Oct 2015	Aug 2018	116947
Hyundai	Santa fé iii	2.4 4WD	SUV	Allrad	Benzin	Sep 2012	Oct 2015	56796
Hyundai	Santa fé iii	2.4 Ccvt	SUV	Frontantrieb	Benzin	Sep 2012	Dec 2018	117585
Hyundai	Santa fé iii	2.4 GDI	SUV	Frontantrieb	Benzin	May 2015	Aug 2018	117223
Hyundai	Santa fé iii	2.4 GDI 4WD	SUV	Allrad	Benzin	May 2015	Aug 2018	117225
Hyundai	Santa fé iii	Crdi 4X4	Kasten/SUV	Allrad	Diesel	May 2015	Oct 2018	142814
Hyundai	Santa fe iv	1.6 T-gdi Hybrid	SUV	Frontantrieb	Benzin/Elektro	Aug 2020	-	142820
Hyundai	Santa fe iv	1.6 T-gdi Hybrid Htrac	SUV	Allrad	Benzin/Elektro	Aug 2020	-	142822
Hyundai	Santa fe iv	1.6 T-gdi Plug-in-hybrid Htrac	SUV	Allrad	Benzin/Elektro	Mar 2021	-	145697
Hyundai	Santa fe iv	2.2 Crdi	SUV	Frontantrieb	Diesel	Nov 2020	-	142992
Hyundai	Santa fe iv	2.2 Crdi	SUV	Frontantrieb	Diesel	Apr 2022	-	147246
Hyundai	Santa fe iv	2.2 Crdi Htrac	SUV	Allrad	Diesel	Nov 2020	-	142991
Hyundai	Santa fe iv	2.2 Crdi Htrac	SUV	Allrad	Diesel	Apr 2022	-	147249
Hyundai	Santa fe iv	2.5 MPI	SUV	Frontantrieb	Benzin	Jul 2021	-	143732
Hyundai	Santa fe iv	2.5 MPI AWD	SUV	Allrad	Benzin	Jul 2021	-	146965


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖全部 **100 个输入 Ktype**。跨改款车型与 Porter 多驾驶室/轴距车型完成语义化派生，共形成 **119 条映射记录**。
* 复用用户提供的两个 ix20 历史尺寸组，未改写其 ID 或三维。
* ix35 Fuel Cell、Kona 第二代燃油/混动与 EV、Lantra II 改款前后、Santa Fe II 改款前后均已按不同物理外廓分组。官方资料确认 ix35 Fuel Cell 为 4410×1820×1655 mm；Kona II ICE/HEV 与 EV 的外廓分别为 4350×1825×1580 mm 和 4355×1825×1575 mm。([现代快讯][1])
* Lantra II 的轿车和旅行车均按 J2/J3 改款边界拆分；Santa Fe II 的改款前后尺寸差异也已独立建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**119**
* PENDING 映射：**0**
* 已确认尺寸组：**26**
* Ktype 映射列数：**10**
* DIMENSION_GROUP 列数：**6**
* `id` 与 `DIMENSION_GROUP_ID` 唯一性、映射外键闭合、孤立尺寸组、尺寸正整数及来源非空检查：**全部通过**

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10602_prefl	10602	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	MEDIUM	生产区间跨2015改款；改款前五门外廓。	READY
10602_facelift	10602	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	MEDIUM	生产区间跨2015改款；改款后五门外廓。	READY
59408_prefl	59408	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	MEDIUM	生产区间跨2015改款；改款前五门外廓。	READY
59408_facelift	59408	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	MEDIUM	生产区间跨2015改款；改款后五门外廓。	READY
125220	125220	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
114089	114089	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
128236	128236	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
100807	100807	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
100805	100805	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
110519	110519	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	HIGH		READY
142773	142773	Van	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	MEDIUM	商用封窗/货运登记，复用LM乘用车身外廓。	READY
142776	142776	Van	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	MEDIUM	商用封窗/货运登记，复用LM乘用车身外廓。	READY
143063	143063	Van	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	MEDIUM	商用封窗/货运登记，复用LM乘用车身外廓。	READY
110481	110481	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FCEV-01	HIGH	燃料电池版独立外廓高度。	READY
109541	109541	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-FCEV-01	HIGH	燃料电池版独立外廓高度。	READY
142769	142769	Van	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-01	MEDIUM	商用封窗/货运登记，复用LM乘用车身外廓。	READY
12258	12258	SUV	ix55	EN	5	EU-HYUNDAI-IX55-EN-SUV-01	HIGH		READY
55399	55399	SUV	ix55	EN	5	EU-HYUNDAI-IX55-EN-SUV-01	HIGH		READY
55400	55400	SUV	ix55	EN	5	EU-HYUNDAI-IX55-EN-SUV-01	HIGH		READY
128293_prefl	128293	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	MEDIUM	生产区间跨2020改款；改款前外廓。	READY
128293_facelift	128293	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	MEDIUM	生产区间跨2020改款；改款后外廓。	READY
154502	154502	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
801332	801332	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802217	802217	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802519	802519	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
142767	142767	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	HIGH		READY
153711	153711	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
801333	801333	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
142770	142770	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	HIGH		READY
142777	142777	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	HIGH		READY
801147	801147	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
128030	128030	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
142772	142772	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	HIGH		READY
154503	154503	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
801025	801025	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
801314	801314	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802218	802218	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802219	802219	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
128292_prefl	128292	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	MEDIUM	生产区间跨2020改款；改款前外廓。	READY
128292_facelift	128292	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	MEDIUM	生产区间跨2020改款；改款后外廓。	READY
142774	142774	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	HIGH		READY
154505	154505	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
801313	801313	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802220	802220	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
802221	802221	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
153710	153710	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
145514	145514	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-N-01	HIGH	KONA N专属保险杠外廓。	READY
155214	155214	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	HIGH		READY
155215	155215	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	HIGH		READY
157457	157457	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	HIGH		READY
157520	157520	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	HIGH		READY
157900	157900	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	HIGH		READY
156030	156030	SUV	Kona II	SX2	5	EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	HIGH		READY
14769_prefl	14769	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-01	MEDIUM	生产区间跨1998改款；J2改款前外廓。	READY
14769_facelift	14769	Sedan	Lantra II	J3	4	EU-HYUNDAI-LANTRA-II-J3-SEDAN-01	MEDIUM	生产区间跨1998改款；J3改款后外廓。	READY
14770_prefl	14770	Wagon	Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	MEDIUM	生产区间跨1998改款；J2改款前外廓。	READY
14770_facelift	14770	Wagon	Lantra II	J3	5	EU-HYUNDAI-LANTRA-II-J3-WAGON-01	MEDIUM	生产区间跨1998改款；J3改款后外廓。	READY
7824_prefl	7824	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-01	MEDIUM	生产区间跨1998改款；J2改款前外廓。	READY
7824_facelift	7824	Sedan	Lantra II	J3	4	EU-HYUNDAI-LANTRA-II-J3-SEDAN-01	MEDIUM	生产区间跨1998改款；J3改款后外廓。	READY
16001	16001	MPV	Matrix	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-01	HIGH		READY
18753	18753	MPV	Matrix	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-01	HIGH		READY
162910	162910	SUV	NEXO II	NH2	5	EU-HYUNDAI-NEXO-II-NH2-SUV-01	HIGH		READY
117370_supercab_lwb	117370	Pickup	Porter II	HR		EU-HYUNDAI-PORTER-II-HR-PICKUP-SUPERCAB-LWB-01	MEDIUM	Ktype覆盖多种后驱驾驶室/轴距；长轴Super Cab。	READY
117370_doublecab_lwb	117370	Pickup	Porter II	HR		EU-HYUNDAI-PORTER-II-HR-PICKUP-DOUBLECAB-LWB-01	MEDIUM	Ktype覆盖多种后驱驾驶室/轴距；长轴Double Cab。	READY
117370_standardcab_xlwb	117370	Pickup	Porter II	HR		EU-HYUNDAI-PORTER-II-HR-PICKUP-STANDARDCAB-XLWB-01	MEDIUM	Ktype覆盖多种后驱驾驶室/轴距；超长轴Standard Cab。	READY
117370_supercab_xlwb	117370	Pickup	Porter II	HR		EU-HYUNDAI-PORTER-II-HR-PICKUP-SUPERCAB-XLWB-01	MEDIUM	Ktype覆盖多种后驱驾驶室/轴距；超长轴Super Cab。	READY
117370_doublecab_xlwb	117370	Pickup	Porter II	HR		EU-HYUNDAI-PORTER-II-HR-PICKUP-DOUBLECAB-XLWB-01	MEDIUM	Ktype覆盖多种后驱驾驶室/轴距；超长轴Double Cab。	READY
18024	18024	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
15974	15974	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
15376	15376	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
16171	16171	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
16002	16002	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
16172	16172	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
142802	142802	Van	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	MEDIUM	商用封窗/货运登记，复用SM乘用车身外廓。	READY
109535	109535	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
15378	15378	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH		READY
142804	142804	Van	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	MEDIUM	商用封窗/货运登记，复用SM乘用车身外廓。	READY
142805	142805	Van	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	MEDIUM	商用封窗/货运登记，复用SM乘用车身外廓。	READY
142806	142806	Van	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	MEDIUM	商用封窗/货运登记，复用SM乘用车身外廓。	READY
111969_prefl	111969	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；改款前外廓。	READY
111969_facelift	111969	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；改款后外廓。	READY
34960_prefl	34960	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；改款前外廓。	READY
34960_facelift	34960	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；改款后外廓。	READY
34961_prefl	34961	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；改款前外廓。	READY
34961_facelift	34961	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；改款后外廓。	READY
34963	34963	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	HIGH		READY
142809_prefl	142809	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款前外廓。	READY
142809_facelift	142809	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款后外廓。	READY
142812_prefl	142812	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款前外廓。	READY
142812_facelift	142812	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款后外廓。	READY
142810_prefl	142810	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款前外廓。	READY
142810_facelift	142810	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款后外廓。	READY
142811_prefl	142811	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款前外廓。	READY
142811_facelift	142811	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款后外廓。	READY
142813_prefl	142813	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款前外廓。	READY
142813_facelift	142813	Van	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	MEDIUM	生产区间跨2009改款；商用封窗/货运登记；改款后外廓。	READY
55794	55794	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
55795	55795	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
117229	117229	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
56797	56797	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
127211	127211	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
55796	55796	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
117226	117226	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
55797	55797	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
116947	116947	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
56796	56796	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
117585	117585	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
117223	117223	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
117225	117225	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	HIGH		READY
142814	142814	Van	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	MEDIUM	商用封窗/货运登记，复用欧洲DM乘用车身外廓。	READY
142820	142820	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
142822	142822	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
145697	145697	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
142992	142992	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
147246	147246	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
142991	142991	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
147249	147249	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
143732	143732	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
146965	146965	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6901-7000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600	Auto-Data Hyundai ix20 specifications	https://www.auto-data.net/en/hyundai-ix20-model-2117
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600	Auto-Data Hyundai ix20 facelift specifications	https://www.auto-data.net/en/hyundai-ix20-facelift-2015-generation-4833
EU-HYUNDAI-IX35-LM-SUV-01	4410	1820	1660	Hyundai ix35 owner manual dimensions	https://www.carmanualsonline.info/hyundai-ix35-2012-owners-manual/?srch=dimensions
EU-HYUNDAI-IX35-LM-SUV-FCEV-01	4410	1820	1655	Hyundai ix35 Fuel Cell official technical data	https://www.hyundai.news/newsroom/dam/de/Pressemappen/ix35_Fuel_Cell/ix35_FuelCell_2015_Techn_Daten.pdf
EU-HYUNDAI-IX55-EN-SUV-01	4840	1945	1750	Auto-Data Hyundai ix55 specifications	https://www.auto-data.net/en/hyundai-ix55-model-1479
EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	4165	1800	1565	Hyundai KONA official technical specifications	https://www.hyundai.news/newsroom/dam/uk/press-kits/20180827_kona/Hyundai_Kona_-_Specifications.pdf
EU-HYUNDAI-KONA-I-OS-SUV-FACELIFT-01	4205	1800	1565	Auto-Data Hyundai KONA I facelift specifications	https://www.auto-data.net/en/hyundai-kona-i-facelift-2020-1.0-t-gdi-120hp-mild-hybrid-42463
EU-HYUNDAI-KONA-II-SX2-SUV-ICE-HEV-01	4350	1825	1580	Hyundai all-new KONA official press release	https://www.hyundai.news/eu/articles/press-releases/hyundais-upscaled-all-new-kona-arrives.html
EU-HYUNDAI-KONA-I-OS-SUV-N-01	4215	1800	1565	Hyundai KONA N official technical specifications	https://www.hyundai.news/newsroom/dam/eu/uk/20210728_kona_n/hyundai-kona-n-technical-specifications-uk-0721.pdf
EU-HYUNDAI-KONA-II-SX2-SUV-EV-01	4355	1825	1575	Hyundai all-new KONA Electric official press kit	https://www.hyundai.news/eu/models/suv/kona/press-kit/all-new-kona-roomier-smart-space-and-high-tech-convenience-features-july25.html
EU-HYUNDAI-LANTRA-II-J2-SEDAN-01	4420	1700	1393	Auto-Data Hyundai Elantra II sedan specifications	https://www.auto-data.net/en/hyundai-elantra-ii-generation-3008
EU-HYUNDAI-LANTRA-II-J3-SEDAN-01	4448	1702	1393	Automobile-Catalog Hyundai Lantra facelift sedan specifications	https://www.automobile-catalog.com/car/1998/1165160/hyundai_lantra_1_6i_16v_gsi.html
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457	Automobile-Catalog Hyundai Lantra wagon specifications	https://www.automobile-catalog.com/car/1997/1165010/hyundai_lantra_wagon_2_0i_16v_cdx.html
EU-HYUNDAI-LANTRA-II-J3-WAGON-01	4459	1702	1457	Automobile-Catalog Hyundai Lantra facelift wagon specifications	https://www.automobile-catalog.com/car/2000/1164725/hyundai_lantra_wagon_2_0i_16v_gls.html
EU-HYUNDAI-MATRIX-FC-MPV-01	4025	1740	1635	Auto-Data Hyundai Matrix specifications	https://www.auto-data.net/en/hyundai-matrix-model-1494
EU-HYUNDAI-NEXO-II-NH2-SUV-01	4750	1865	1640	Hyundai NEXO official press release	https://www.hyundai.news/eu/articles/press-releases/nexo-seoul-mobility-show-2025.html
EU-HYUNDAI-PORTER-II-HR-PICKUP-SUPERCAB-LWB-01	4775	1740	1970	Hyundai Porter II official brochure	https://www.hyundai.com/contents/repn-car/catalog_en/porter2-electric-catalog.pdf
EU-HYUNDAI-PORTER-II-HR-PICKUP-DOUBLECAB-LWB-01	4810	1740	1970	Hyundai Porter II official brochure	https://www.hyundai.com/contents/repn-car/catalog_en/porter2-electric-catalog.pdf
EU-HYUNDAI-PORTER-II-HR-PICKUP-STANDARDCAB-XLWB-01	5175	1740	1970	Hyundai Porter II official brochure	https://www.hyundai.com/contents/repn-car/catalog_en/porter2-electric-catalog.pdf
EU-HYUNDAI-PORTER-II-HR-PICKUP-SUPERCAB-XLWB-01	5100	1740	1970	Hyundai Porter II official brochure	https://www.hyundai.com/contents/repn-car/catalog_en/porter2-electric-catalog.pdf
EU-HYUNDAI-PORTER-II-HR-PICKUP-DOUBLECAB-XLWB-01	5135	1740	1970	Hyundai Porter II official brochure	https://www.hyundai.com/contents/repn-car/catalog_en/porter2-electric-catalog.pdf
EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	4500	1820	1730	Hyundai Santa Fe 2005 UK official brochure archive	https://autocatalogarchive.com/wp-content/uploads/2024/04/Hyundai-Santa-Fe-2005-UK.pdf
EU-HYUNDAI-SANTA-FE-II-CM-SUV-PREFL-01	4675	1890	1795	Automobile-Catalog Hyundai Santa Fe II specifications	https://www.automobile-catalog.com/car/2006/1177340/hyundai_santa_fe_2_2_crdi_2wd_gls.html
EU-HYUNDAI-SANTA-FE-II-CM-SUV-FACELIFT-01	4676	1890	1760	Auto-Data Hyundai Santa Fe II facelift specifications	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-facelift-2009-generation-9340
EU-HYUNDAI-SANTA-FE-III-DM-SUV-01	4690	1880	1680	Auto-Data Hyundai Santa Fe III DM;Auto-Data Hyundai Santa Fe III DM facelift	https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-generation-4096;https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-facelift-2015-2.0-crdi-150hp-4wd-24772
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	4785	1900	1710	Hyundai New Santa Fe official pricing specification and technical data	https://www.hyundai.news/newsroom/dam/eu/uk/20210302_new_santa_fe_prices_specifications/hyundai_new_santa_fe_pricing_spec_tech.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6901-7000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.hyundai.news/newsroom/dam/de/Pressemappen/ix35_Fuel_Cell/ix35_FuelCell_2015_Techn_Daten.pdf "https://www.hyundai.news/newsroom/dam/de/Pressemappen/ix35_Fuel_Cell/ix35_FuelCell_2015_Techn_Daten.pdf"
[2]: https://www.auto-data.net/en/hyundai-elantra-ii-wagon-generation-3009 "https://www.auto-data.net/en/hyundai-elantra-ii-wagon-generation-3009"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4052 行）
- 累计尺寸组：dimension_groups_final.tsv（1110 行）

