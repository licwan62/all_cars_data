# 任务：left18448 第 6601-6700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0067__fa751bf1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6601-6700 行

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
left18448 第 6601-6700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6601-6700_ktype_dimension_mapping_final.tsv
- left18448_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-HONDA-INTEGRA-I-DA-HATCHBACK-5D-01	4350	1665	1345
EU-HONDA-INTEGRA-III-DB7-SEDAN-4D-01	4525	1695	1370
EU-HONDA-INTEGRA-III-TYPE-R-DC2-EU-COUPE-3D-01	4400	1695	1320
EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-96SPEC-COUPE-3D-01	4380	1695	1320
EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-98SPEC-COUPE-3D-01	4380	1695	1330
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	4400	1725	1395
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	4400	1725	1400

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Honda	Integra	1.8 Vtir	Coupe	Frontantrieb	Benzin	Jul 1993	Nov 1999	57289
Honda	Integra	2.0 16V Type-r	Coupe	Frontantrieb	Benzin	Feb 2002	Oct 2007	16597
Honda	Jazz ii	1.2 I-dsi	Schrägheck	Frontantrieb	Benzin	Mar 2002	Jul 2008	16816
Honda	Jazz ii	1.4 Idsi	Schrägheck	Frontantrieb	Benzin	Dec 2006	Oct 2008	120218
Honda	Jazz iv	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2015	-	116390
Honda	Jazz iv	1.5	Schrägheck	Frontantrieb	Benzin	Sep 2017	-	126827
Honda	Jazz v	1.5 Ehev	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2023	-	154977
Honda	Logo	1.3	Schrägheck	Frontantrieb	Benzin	Mar 1999	Mar 2002	11415
Honda	Nsx i	3.2 24V Vtec	Coupe	Heckantrieb	Benzin	Jan 1997	Sep 2005	7822
Honda	Nsx i	3.2 24V Vtec	Cabriolet	Heckantrieb	Benzin	Jan 1997	Sep 2005	7823
Honda	Nsx ii	3.5 Hybrid	Coupe	Allrad	Benzin/Elektro	Jun 2016	-	127200
Honda	Odyssey	3.5	Großraumlimousine	Frontantrieb	Benzin	Sep 2004	Dec 2010	44329
Honda	Odyssey	3.5	Großraumlimousine	Frontantrieb	Benzin	Aug 2010	-	55241
Honda	Pilot	3.5 4WD	SUV	Allrad	Benzin	Sep 2008	-	14686
Honda	Pilot	3.5 4WD	SUV	Allrad	Benzin	Jan 2011	-	106543
Honda	Pilot	3.5 4WD	SUV	Allrad	Benzin	Jan 2010	Jun 2015	128257
Honda	Pilot	3.5 AWD	SUV	Allrad	Benzin	Sep 2002	Dec 2004	44336
Honda	Prelude	2.0 16V	Coupe	Frontantrieb	Benzin	Oct 1996	Oct 2000	7820
Honda	Prelude	2.0 E:hev	Coupe	Frontantrieb	Benzin/Elektro	Nov 2025	-	162855
Honda	Prelude	2.0 I EX 16V	Coupe	Frontantrieb	Benzin	Oct 1987	Dec 1990	10581
Honda	Prelude	2.2 16V	Coupe	Frontantrieb	Benzin	Oct 1996	Oct 2000	7821
Honda	Prelude	2.2 16V	Coupe	Frontantrieb	Benzin	Oct 1996	Dec 2001	11510
Honda	S2000	2	Cabriolet	Heckantrieb	Benzin	Jun 1999	Jun 2009	10469
Honda	Stream	1.7 16V	Großraumlimousine	Frontantrieb	Benzin	May 2001	Sep 2006	15955
Honda	Stream	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 2001	Sep 2006	15956
Honda	Zr-V	E:hev	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	154814
Hongqi	Eh7	EV	Stufenheck	Heckantrieb	Elektro	Mar 2024	-	158130
Hongqi	Ehs7	EV	SUV	Heckantrieb	Elektro	Mar 2025	-	162809
Hongqi	Ehs7	EV 4WD	SUV	Allrad	Elektro	Mar 2025	-	160687
Hongqi	E-Hs9	EV AWD	SUV	Allrad	Elektro	Dec 2020	-	142868
Hongqi	E-Hs9	EV AWD	SUV	Allrad	Elektro	Dec 2020	-	142869
Hongqi	H6	2	Schrägheck	Frontantrieb	Benzin	Jan 2025	-	803442
Hongqi	Hs3	1.5 T	SUV	Frontantrieb	Benzin	Dec 2025	-	802897
Hongqi	Hs3	2.0 T AWD	SUV	Allrad	Benzin	Dec 2025	-	802896
Hongqi	Hs5	2.0 AWD	SUV	Allrad	Benzin	May 2025	-	803374
Hongqi	Hs5	2.0 AWD	SUV	Allrad	Benzin	May 2025	-	803375
Hummer	H1	6.5 D 4WD	Geländewagen geschlossen	Allrad	Diesel	Sep 2001	Dec 2003	44427
Hummer	H2	6.0 AWD	Geländewagen geschlossen	Allrad	Benzin	Sep 2003	Dec 2004	44431
Hummer	Hummer h1	6.5 D	Geländewagen geschlossen	Allrad	Diesel	Jan 1992	Sep 1997	12749
Hummer	Hummer h1	6.5 Turbo D 4WD	Geländewagen geschlossen	Allrad	Diesel	Jan 1992	Dec 2004	12750
Hummer	Hummer h2	6.2 AWD	Geländewagen geschlossen	Allrad	Benzin	Oct 2004	-	18257
Hummer	Hummer h2	6.2 Flex AWD	Geländewagen geschlossen	Allrad	Benzin/Ethanol	Sep 2008	Dec 2009	18443
Hummer	Hummer h2 sut	6.0 AWD	Pick-up	Allrad	Benzin	Sep 2004	-	18809
Hummer	Hummer h2 sut	6.2 Flexfuel AWD	Pick-up	Allrad	Benzin/Ethanol	Sep 2008	Dec 2009	120505
Hummer	Hummer h3	3.5	Geländewagen geschlossen	Allrad	Benzin	Apr 2005	-	18977
Hummer	Hummer h3	5.3 Flexfuel 4WD	Geländewagen geschlossen	Allrad	Benzin/Ethanol	Sep 2009	Dec 2010	51049
Hummer	Hummer h3t	3.7 4WD	Pick-up	Allrad	Benzin	Oct 2008	Dec 2010	53710
Hyundai	Accent ii	1.3	Schrägheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	14597
Hyundai	Accent ii	1.3	Schrägheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	15952
Hyundai	Accent ii	1.3	Schrägheck	Frontantrieb	Benzin	Aug 2002	Nov 2005	17757
Hyundai	Accent ii	1.3	Stufenheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	18693
Hyundai	Accent ii	1.3	Stufenheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	18694
Hyundai	Accent ii	1.5	Schrägheck	Frontantrieb	Benzin	Sep 2000	Feb 2003	15380
Hyundai	Accent ii	1.5	Schrägheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	16590
Hyundai	Accent ii	1.5	Stufenheck	Frontantrieb	Benzin	Jan 2000	Nov 2005	16721
Hyundai	Accent ii	1.5	Stufenheck	Frontantrieb	Benzin	Sep 1999	Oct 2002	55825
Hyundai	Accent ii	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2002	Nov 2005	17767
Hyundai	Accent ii	1.6	Stufenheck	Frontantrieb	Benzin	Dec 2002	Nov 2005	17769
Hyundai	Accent ii	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	Apr 2002	Nov 2005	16811
Hyundai	Accent ii	1.5 Crdi	Stufenheck	Frontantrieb	Diesel	Jan 2002	Nov 2005	18695
Hyundai	Accent iv	1.4	Stufenheck	Frontantrieb	Benzin	Nov 2010	Dec 2017	55641
Hyundai	Accent iv	1.4	Stufenheck	Frontantrieb	Benzin	Nov 2010	-	106316
Hyundai	Accent iv	1.6	Stufenheck	Frontantrieb	Benzin	Nov 2010	-	55642
Hyundai	Accent iv	1.6	Stufenheck	Frontantrieb	Benzin	Nov 2010	Dec 2017	55644
Hyundai	Accent iv	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	Nov 2010	Dec 2017	55645
Hyundai	Accent iv	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	Apr 2011	Dec 2017	109977
Hyundai	Atos	1.0 I	Schrägheck	Frontantrieb	Benzin	Mar 2001	Jul 2003	16169
Hyundai	Bayon	1.0 T-gdi	SUV	Frontantrieb	Benzin	May 2021	-	145128
Hyundai	Bayon	1.0 T-gdi	SUV	Frontantrieb	Benzin	Oct 2025	-	802506
Hyundai	Bayon	1.0 T-gdi 48v-hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2021	-	145129
Hyundai	Bayon	1.0 T-gdi 48v-hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2021	-	145131
Hyundai	Bayon	1.2 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	May 2023	-	154573
Hyundai	Bayon	1.2 MPI	SUV	Frontantrieb	Benzin	May 2021	-	145123
Hyundai	Bayon	1.2 MPI	SUV	Frontantrieb	Benzin	Nov 2024	-	801327
Hyundai	Bayon	1.4 MPI	SUV	Frontantrieb	Benzin	May 2021	-	145517
Hyundai	Creta	2	SUV	Frontantrieb	Benzin	Jan 2016	Jan 2021	121109
Hyundai	Elantra iii	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15127
Hyundai	Elantra iii	1.6	Stufenheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15129
Hyundai	Elantra iii	1.6	Stufenheck	Frontantrieb	Benzin	May 2003	May 2006	17570
Hyundai	Elantra iii	1.6	Schrägheck	Frontantrieb	Benzin	May 2003	Jul 2006	17571
Hyundai	Elantra iii	1.8	Stufenheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15948
Hyundai	Elantra iii	1.8	Schrägheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15949
Hyundai	Elantra iii	2	Schrägheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15128
Hyundai	Elantra iii	2	Stufenheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15130
Hyundai	Elantra iii	2	Stufenheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15950
Hyundai	Elantra iii	2	Schrägheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	15951
Hyundai	Elantra iii	2	Stufenheck	Frontantrieb	Benzin	Oct 2003	Jul 2006	17496
Hyundai	Elantra iii	2	Schrägheck	Frontantrieb	Benzin	Oct 2003	Jul 2006	17497
Hyundai	Elantra iii	2.0 Crdi	Schrägheck	Frontantrieb	Diesel	Apr 2001	Jul 2006	15971
Hyundai	Elantra iii	2.0 Crdi	Stufenheck	Frontantrieb	Diesel	Apr 2001	Jul 2006	15972
Hyundai	Elantra iv	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	Nov 2005	Dec 2011	110520
Hyundai	Elantra iv	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	Jun 2006	May 2010	18892
Hyundai	Elantra v	1.6	Stufenheck	Frontantrieb	Benzin	Apr 2011	Apr 2016	55681
Hyundai	Elantra v	1.6	Stufenheck	Frontantrieb	Benzin	Jun 2011	Dec 2015	58679
Hyundai	Elantra v	1.8	Stufenheck	Frontantrieb	Benzin	Sep 2010	Dec 2016	17255
Hyundai	Elantra vi	1.6	Stufenheck	Frontantrieb	Benzin	Feb 2016	Dec 2020	128261
Hyundai	Elantra vi	2	Stufenheck	Frontantrieb	Benzin	Feb 2016	Dec 2020	119635
Hyundai	Elantra vi	2	Stufenheck	Frontantrieb	Benzin	Oct 2015	Dec 2020	128002
Hyundai	Elantra vi	1.6 SR Turbo	Stufenheck	Frontantrieb	Benzin	Feb 2016	Dec 2020	123947
Hyundai	Equus / centennial	3.8	Stufenheck	Heckantrieb	Benzin	Mar 2009	Dec 2016	54904


--- Round 1 / 首次发送 ---
## 更新点

* 完成前 26 个 Honda Ktype 的车身聚类，新增 18 个尺寸组，并复用已有的 2 个 Integra DC5 尺寸组。
* `Product End Month-Year=-` 未被解释为持续生产：Jazz 116390、Odyssey 55241、Pilot 14686/106543 暂不猜测跨改款分支。
* Jazz 2023 改款和 Prelude 2026 采用 Honda 官方规格；Integra VTi-R、NSX、Pilot、S2000 等使用对应车型直接规格页闭合。([本田][1])

## 当前批次进度

* 已处理输入 Ktype：26 / 100
* READY 映射：24 行
* PENDING 映射：6 行
* 本轮新增尺寸组：18
* 本轮复用已有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57289	57289	Coupe	Integra III	DC2	3	EU-HONDA-INTEGRA-III-DC2-VTIR-COUPE-3D-01	HIGH	DC2 VTi-R三门车身；与既有Type-R尺寸组分离。	READY
16597_prefl	16597	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	HIGH	改款前物理分支。	READY
16597_facelift	16597	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	HIGH	改款后物理分支。	READY
16816	16816	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
120218	120218	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
116390	116390	Hatchback	Jazz IV	GK	5		MEDIUM	候选为2015款与2017改款车身；输入结束时间未知，Ktype跨改款边界未闭合。	PENDING: Ktype是否跨越2017改款尚未确认
126827	126827	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-01	HIGH	2017改款五门车身。	READY
154977	154977	Hatchback	Jazz V		5	EU-HONDA-JAZZ-V-GR-HATCHBACK-5D-FACELIFT-01	HIGH	2023改款五门车身。	READY
11415	11415	Hatchback	Logo I	GA3	5	EU-HONDA-LOGO-I-GA3-HATCHBACK-5D-01	HIGH		READY
7822_prefl	7822	Coupe	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-COUPE-2D-PREFL-01	HIGH	固定前照灯改款前分支。	READY
7822_facelift	7822	Coupe	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-COUPE-2D-FACELIFT-01	HIGH	2002改款分支。	READY
7823	7823	Convertible	NSX I	NA2	2		MEDIUM	候选为NA2 NSX-T改款前后分支；改款前敞篷车身直接尺寸来源尚未闭合。	PENDING: NSX-T改款前直接尺寸来源缺失
127200	127200	Coupe	NSX II	NC1	2	EU-HONDA-NSX-II-NC1-COUPE-2D-01	HIGH		READY
44329	44329	MPV	Odyssey III		5		LOW	候选为北美Odyssey III 3.5；不同配置的标准车高边界尚未闭合。	PENDING: 标准无附件车高存在配置差异
55241	55241	MPV	Odyssey IV		5		MEDIUM	候选为改款前及2014改款车身；输入结束时间未知，且改款后不含后视镜宽度未闭合。	PENDING: 跨改款边界及改款后车身宽度未确认
14686	14686	SUV	Pilot II		5		MEDIUM	开始时间属于改款前车身，但输入结束时间未知，不能据此推定覆盖2012改款。	PENDING: Ktype改款边界未确认
106543	106543	SUV	Pilot II		5		MEDIUM	开始时间属于改款前车身，但输入结束时间未知，不能据此推定覆盖2012改款。	PENDING: Ktype改款边界未确认
128257_prefl	128257	SUV	Pilot II		5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	2012改款前物理分支。	READY
128257_facelift	128257	SUV	Pilot II		5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	2012改款后物理分支。	READY
44336	44336	SUV	Pilot I		5	EU-HONDA-PILOT-I-SUV-5D-01	HIGH		READY
7820	7820	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
162855	162855	Coupe	Prelude VI		3	EU-HONDA-PRELUDE-VI-COUPE-3D-01	HIGH	2026欧洲版三门掀背式Coupe车身。	READY
10581	10581	Coupe	Prelude III		2	EU-HONDA-PRELUDE-III-BA-COUPE-2D-01	HIGH		READY
7821	7821	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
11510	11510	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
10469_prefl	10469	Convertible	S2000 I	AP1	2	EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-PREFL-01	HIGH	2004改款前物理分支。	READY
10469_facelift	10469	Convertible	S2000 I	AP1	2	EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2004改款后物理分支。	READY
15955	15955	MPV	Stream I		5	EU-HONDA-STREAM-I-MPV-5D-01	HIGH		READY
15956	15956	MPV	Stream I		5	EU-HONDA-STREAM-I-MPV-5D-01	HIGH		READY
154814	154814	SUV	ZR-V I		5	EU-HONDA-ZR-V-I-SUV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-INTEGRA-III-DC2-VTIR-COUPE-3D-01	4380	1710	1335	CarsGuide Honda Integra dimensions	https://www.carsguide.com.au/honda/integra/car-dimensions/1993
EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	3830	1675	1525	Auto-Data Honda Jazz generation specifications	https://www.auto-data.net/en/honda-jazz-i-generation-2588
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-01	4051	1694	1544	Auto-Data Honda Jazz facelift 2017 specifications	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.5-i-vtec-130hp-32645
EU-HONDA-JAZZ-V-GR-HATCHBACK-5D-FACELIFT-01	4089	1694	1526	Honda UK Jazz Hybrid official specifications	https://www.honda.co.uk/cars/new/jazz-hybrid/specifications.html
EU-HONDA-LOGO-I-GA3-HATCHBACK-5D-01	3785	1645	1520	Auto-Data Honda Logo specifications	https://www.auto-data.net/en/honda-logo-model-1309
EU-HONDA-NSX-I-NA2-COUPE-2D-PREFL-01	4425	1810	1170	Auto-Data Honda NSX I Coupe specifications	https://www.auto-data.net/en/honda-nsx-i-coupe-generation-2669
EU-HONDA-NSX-I-NA2-COUPE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX I Coupe facelift 2002 specifications	https://www.auto-data.net/en/honda-nsx-i-coupe-facelift-2002-generation-8112
EU-HONDA-NSX-II-NC1-COUPE-2D-01	4487	1920	1204	Auto-Data Honda NSX II specifications	https://www.auto-data.net/en/honda-nsx-ii-coupe-3.5-i-vtec-bi-turbo-v6-581hp-hybrid-sh-awd-dct-32058
EU-HONDA-PILOT-II-SUV-5D-PREFL-01	4849	1994	1803	Auto-Data Honda Pilot II specifications	https://www.auto-data.net/en/honda-pilot-ii-3.5-v6-253hp-4wd-automatic-41040
EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	4862	1994	1839	Auto-Data Honda Pilot II facelift 2012 specifications	https://www.auto-data.net/en/honda-pilot-ii-facelift-2012-3.5-v6-253hp-4wd-automatic-41042
EU-HONDA-PILOT-I-SUV-5D-01	4775	1964	1793	Auto-Data Honda Pilot I specifications	https://www.auto-data.net/en/honda-pilot-i-3.5-v6-243hp-awd-automatic-12181
EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	4545	1750	1315	Auto-Data Honda Prelude V specifications	https://www.auto-data.net/en/honda-prelude-v-bb-2.2-16v-bb6-bb8-185hp-12197
EU-HONDA-PRELUDE-VI-COUPE-3D-01	4525	1880	1349	Honda Europe 2026 Prelude official technical specification	https://hondanews.eu/eu/en/cars/media/pressreleases/553085/2026-honda-prelude-coupe-ehev-technical-specification-eu
EU-HONDA-PRELUDE-III-BA-COUPE-2D-01	4460	1695	1295	Auto-Data Honda Prelude specifications	https://www.auto-data.net/en/honda-prelude-model-1305
EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-PREFL-01	4135	1750	1270	Auto-Data Honda S2000 AP1 specifications	https://www.auto-data.net/en/honda-s2000-ap1-generation-2670
EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-FACELIFT-01	4135	1750	1285	Auto-Data Honda S2000 AP1 facelift 2004 specifications	https://www.auto-data.net/en/honda-s2000-ap1-facelift-2004-generation-7192
EU-HONDA-STREAM-I-MPV-5D-01	4570	1695	1605	Auto-Data Honda Stream specifications	https://www.auto-data.net/en/honda-stream-model-1301
EU-HONDA-ZR-V-I-SUV-5D-01	4570	1840	1620	Auto-Data Honda ZR-V specifications	https://www.auto-data.net/en/honda-zr-v-model-3222
```

## 下一步优先处理

1. 消除 6 个 Honda PENDING：优先补齐 NSX-T、Odyssey III/IV，以及 Jazz/Pilot 的 Ktype 改款边界。
2. 随后按共享外廓批量处理 Hongqi 和 Hummer。
3. 再集中建立 Hyundai Accent II、Elantra III 等高复用尺寸组。

推进信号：CONTINUE

[1]: https://www.honda.co.uk/cars/new/jazz-hybrid/specifications.html?utm_source=chatgpt.com "Honda Jazz Hybrid | Specifications"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6601-6700_ktype_dimension_mapping_final.tsv
- left18448_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 消除上一轮全部 6 个 Honda 待定映射，并将跨改款 Ktype 拆成稳定物理分支。
* Jazz Ktype `116390` 确认为 GK 五门 1.3，覆盖改款前后；因 1.3 改款后尺寸与现有 1.5 改款组不同，新建 `FACELIFT-02`，未覆盖既有组。([Web Catalogo][1])
* NSX-T Ktype `7823` 确认为 NA2、1997–2005，拆分 2002 改款前后两个外廓。([AUTODOC UK][2])
* Odyssey Ktype `44329` 闭合为 RL3/RL4 两个改款分支；`55241` 闭合为 RL5 改款前后分支。([AUTODOC][3])
* Pilot 三个跨改款 4WD Ktype 统一确认 BodyCode 为 `YF4`，直接复用上一轮已建 Pilot II 两个尺寸组，不重复输出尺寸组。([AUTODOC][4])

## 当前批次进度

* 已处理输入 Ktype：26 / 100
* READY 映射：36 行
* PENDING／尚未处理：74 个 Ktype
* 已确认尺寸组：28 个
* 本轮首次创建尺寸组：8 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116390_prefl	116390	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-PREFL-01	HIGH	2015至2017改款前外廓。	READY
116390_facelift	116390	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-02	HIGH	2017改款后1.3外廓；不复用既有1.5改款尺寸组。	READY
7823_prefl	7823	Convertible	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-PREFL-01	HIGH	NSX-T 2002改款前物理外廓。	READY
7823_facelift	7823	Convertible	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-FACELIFT-01	HIGH	NSX-T 2002改款后物理外廓。	READY
44329_prefl	44329	MPV	Odyssey III	RL3	5	EU-HONDA-ODYSSEY-III-RL3-MPV-5D-PREFL-01	HIGH	RL3改款前物理外廓。	READY
44329_facelift	44329	MPV	Odyssey III	RL4	5	EU-HONDA-ODYSSEY-III-RL4-MPV-5D-FACELIFT-01	HIGH	RL4改款后物理外廓。	READY
55241_prefl	55241	MPV	Odyssey IV	RL5	5	EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-PREFL-01	HIGH	RL5 2011至2013改款前外廓。	READY
55241_facelift	55241	MPV	Odyssey IV	RL5	5	EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-FACELIFT-01	HIGH	RL5 2014改款后外廓。	READY
14686_prefl	14686	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
14686_facelift	14686	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
106543_prefl	106543	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
106543_facelift	106543	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
128257_prefl	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
128257_facelift	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-PREFL-01	3995	1694	1525	Auto-Data Honda Jazz III generation specifications	https://www.auto-data.net/en/honda-jazz-iii-generation-4552
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-02	4028	1694	1525	Auto-Data Honda Jazz III facelift 2017 1.3 i-VTEC specifications	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.3-i-vtec-102hp-32643
EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-PREFL-01	4420	1810	1175	Auto-Data Honda NSX-T I 3.2 V6 VTEC specifications	https://www.auto-data.net/en/honda-nsx-t-i-3.2-v6-vtec-280hp-54809
EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX-T I facelift 2002 3.2 V6 VTEC specifications	https://www.auto-data.net/en/honda-nsx-t-i-facelift-2002-3.2-v6-vtec-280hp-54802
EU-HONDA-ODYSSEY-III-RL3-MPV-5D-PREFL-01	5105	1958	1748	Honda News 2005 Honda Odyssey Body	https://hondanews.com/en-US/honda-automobiles/releases/release-726e2461d33d92cff8f2a2004c34c3a1-2005-honda-odyssey-body
EU-HONDA-ODYSSEY-III-RL4-MPV-5D-FACELIFT-01	5133	1958	1748	Honda News 2009 Honda Odyssey Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-c0fe0dfee5573ce4bac3eb004c34bc52-2009-honda-odyssey-specifications-and-features
EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-PREFL-01	5154	2012	1737	Honda News 2011 Honda Odyssey Overview	https://hondanews.com/en-US/honda-automobiles/releases/release-39ea457927744650b4ae2f39934ae503-2011-honda-odyssey-overview
EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-FACELIFT-01	5154	2012	1737	Honda News 2014 Honda Odyssey Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-1267ee1d741b4207924b585d98cf5a56-2014-honda-odyssey-specifications-and-features
```

## 下一步优先处理

1. 按重复外廓聚类处理 Hongqi：EHS7、E-HS9、HS5 的重复 Ktype 优先一次闭合。
2. 批量处理 Hummer H1、H2、H2 SUT、H3、H3T，严格区分 SUV、Pickup 和跨改款外廓。
3. 随后建立 Hyundai Accent II、Accent IV、Elantra III 的高复用尺寸组。

推进信号：CONTINUE

[1]: https://catalogonuevo.rbrake.com/Vehiculo/Details?idTipoVehiculo=2&idVehiculo=116390&utm_source=chatgpt.com "Vehicle HONDA - JAZZ III (GK_) - 1.3 details - Web Catalogo"
[2]: https://www.autodoc.co.uk/car-parts/gasket-cylinder-head-10325/honda/nsx/nsx-convertible-na/7823-3-2-24v-vtec-na2?utm_source=chatgpt.com "NSX Convertible NA 3.2 24V Vtec Head gasket (280 hp Petrol ..."
[3]: https://www.autodoc.es/repuestos/bocina-bocina-electroneumatica-10420/honda/odyssey/odyssey-rl5/55241-3-5 "Claxon HONDA Odyssey (RL5) 3.5 252cv Gasolina 185kW 2010 - 2026 Motor Otto J35Z8 | precio en AUTODOC"
[4]: https://www.auto-doc.fr/pieces-detachees/avertisseur-sonore-trompette-10420/honda/pilot/pilot-2008/14686-3-5-4wd "Klaxon HONDA Pilot (YF3, YF4) 3.5 4WD 253 CV Essence 186 KW 2008 - 2026 J35Z4 | prix dans AUTODOC"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6601-6700_ktype_dimension_mapping_final.tsv
- left18448_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 10 个 Hongqi Ktype：相同驱动或不同动力版本直接复用同一物理尺寸组，共首次创建 6 个尺寸组。EH7、EHS7、E-HS9、HS3、HS5 均采用 Hongqi 官方规格；H6 采用 Hongqi 俄罗斯官方规格。([hongqi-auto.com][1])
* 完成 11 个 Hummer Ktype：H1、H2 SUV、H2 SUT、H3、H3T 分为 5 个稳定物理尺寸组；同一车身的发动机、燃料和年份版本复用组，不重复建组。H2、H3 和 H3T 的宽度来源明确为不含后视镜口径。([汽车数据网][2])

## 当前批次进度

* 已覆盖输入 Ktype：47 / 100
* READY 映射：57 行
* 当前已输出 PENDING 映射：0 行
* 尚未处理 Ktype：53
* 已确认尺寸组：39 个
* 本轮首次创建尺寸组：11 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
158130	158130	Sedan	EH7 I		4	EU-HONGQI-EH7-I-SEDAN-4D-01	HIGH		READY
162809	162809	SUV	EHS7 I		5	EU-HONGQI-EHS7-I-SUV-5D-01	HIGH		READY
160687	160687	SUV	EHS7 I		5	EU-HONGQI-EHS7-I-SUV-5D-01	HIGH		READY
142868	142868	SUV	E-HS9 I		5	EU-HONGQI-E-HS9-I-SUV-5D-01	HIGH		READY
142869	142869	SUV	E-HS9 I		5	EU-HONGQI-E-HS9-I-SUV-5D-01	HIGH		READY
803442	803442	Hatchback	H6 I		5	EU-HONGQI-H6-I-HATCHBACK-5D-01	HIGH	五门掀背式车身。	READY
802897	802897	SUV	HS3 I		5	EU-HONGQI-HS3-I-SUV-5D-01	HIGH		READY
802896	802896	SUV	HS3 I		5	EU-HONGQI-HS3-I-SUV-5D-01	HIGH		READY
803374	803374	SUV	HS5 II		5	EU-HONGQI-HS5-II-SUV-5D-01	HIGH		READY
803375	803375	SUV	HS5 II		5	EU-HONGQI-HS5-II-SUV-5D-01	HIGH		READY
44427	44427	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
12749	12749	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
12750	12750	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
44431	44431	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
18257	18257	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
18443	18443	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
18809	18809	Pickup	H2 I	GMT825	4	EU-HUMMER-H2-I-PICKUP-4D-01	HIGH	H2 SUT四门短货斗车身。	READY
120505	120505	Pickup	H2 I	GMT825	4	EU-HUMMER-H2-I-PICKUP-4D-01	HIGH	H2 SUT四门短货斗车身。	READY
18977	18977	SUV	H3 I	GMT345	5	EU-HUMMER-H3-I-SUV-5D-01	HIGH		READY
51049	51049	SUV	H3 I	GMT345	5	EU-HUMMER-H3-I-SUV-5D-01	HIGH		READY
53710	53710	Pickup	H3T I	GMT745	4	EU-HUMMER-H3T-I-PICKUP-4D-01	HIGH	四门乘员舱短货斗车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONGQI-EH7-I-SEDAN-4D-01	4980	1915	1490	Hongqi official EH7 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_eh7.html
EU-HONGQI-EHS7-I-SUV-5D-01	4925	1950	1680	Hongqi official EHS7 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_ehs7.html
EU-HONGQI-E-HS9-I-SUV-5D-01	5209	2010	1731	Hongqi official E-HS9 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_E-hs9.html
EU-HONGQI-H6-I-HATCHBACK-5D-01	4990	1876	1450	Hongqi Russia official H6 specifications	https://hongqi.ru/news/hongqi-h6
EU-HONGQI-HS3-I-SUV-5D-01	4655	1900	1668	Hongqi official HS3 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_hs3.html
EU-HONGQI-HS5-II-SUV-5D-01	4785	1905	1700	Hongqi official HS5 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_hs5.html
EU-HUMMER-H1-I-SUV-4D-01	4686	2197	1905	Auto-Data Hummer H1 generation specifications	https://www.auto-data.net/en/hummer-h1-model-2237
EU-HUMMER-H2-I-SUV-5D-01	4821	2062	2012	Edmunds 2004 HUMMER H2 specifications	https://www.edmunds.com/hummer/h2/2004/st-100273977/features-specs/
EU-HUMMER-H2-I-PICKUP-4D-01	5170	2063	2012	Automobile-Catalog 2008 Hummer H2 SUT specifications	https://www.automobile-catalog.com/car/2008/1430915/hummer_h2_sut.html
EU-HUMMER-H3-I-SUV-5D-01	4763	1895	1859	Edmunds 2009 HUMMER H3 specifications	https://www.edmunds.com/hummer/h3/2009/features-specs/
EU-HUMMER-H3T-I-PICKUP-4D-01	5403	1905	1831	Edmunds 2009 HUMMER H3T specifications	https://www.edmunds.com/hummer/h3t/2009/features-specs/
```

## 下一步优先处理

1. 批量闭合 Hyundai Accent II 的 Hatchback、Sedan 两种外廓。
2. 闭合 Accent IV Sedan、Atos 和 Creta。
3. 随后集中处理 Bayon 改款边界及 Elantra III Hatchback、Sedan 高复用尺寸组。

推进信号：CONTINUE

[1]: https://www.hongqi-auto.com/pages/cartype/cartype_eh7.html?utm_source=chatgpt.com "HONGQI AUTO OFFICIAL WEBSITE-MODELS_E_H7"
[2]: https://www.auto-data.net/en/hummer-h1-model-2237?utm_source=chatgpt.com "Hummer H1 | Technical Specs, Fuel consumption ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6601-6700_ktype_dimension_mapping_final.tsv
- left18448_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 纠正上一轮进度口径：虽然已输出映射中没有 `PENDING` 行，但仍有 53 个输入 Ktype 尚未闭合，不能视为 `PENDING=0`。本轮起将所有尚未处理 Ktype 计入待完成数。
* 完成 Accent IV Sedan 的 6 个 Ktype，共用一个尺寸组。
* 完成 Bayon 的 8 个 Ktype：2021 首发外廓和 2024 改款外廓分别建组；较早且结束日期未知的 Ktype，依据后续新增改款 Ktype 分流至首发组，置信度设为 `MEDIUM`。
* 完成 Creta I 的 1 个 Ktype。
* 本轮四个尺寸组均由 Hyundai 官方资料首次闭合：Accent IV 为 `4370×1705×1455`，Bayon 首发版为 `4180×1775×1490`，改款版为 `4180×1775×1500`，Creta I 为 `4270×1780×1630`。

## 当前批次进度

* 已覆盖输入 Ktype：62 / 100
* READY 映射：72 行
* PENDING／尚未处理 Ktype：38
* 已确认尺寸组：43 个
* 本轮新增尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
55641	55641	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
106316	106316	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55642	55642	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55644	55644	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55645	55645	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
109977	109977	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
145128	145128	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
802506	802506	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	HIGH	2024改款外廓。	READY
145129	145129	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
145131	145131	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
154573	154573	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
145123	145123	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
801327	801327	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	HIGH	2024改款外廓。	READY
145517	145517	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
121109	121109	SUV	Creta I		5	EU-HYUNDAI-CRETA-I-SUV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	4370	1705	1455	Hyundai Motor Company Accent official catalogue	https://www.hyundai.com/content/dam/hyundai/kr/ko/html/pdf/en-cn-catalog/en-catalog/accent-catalog-eng.pdf
EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	4180	1775	1490	Hyundai Motor Europe all-new BAYON official press kit	https://www.hyundai.news/eu/models/suv/bayon/press-kit/all-new-hyundai-bayon-a-stylish-and-sleek-crossover-suv.html
EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	4180	1775	1500	Hyundai Motor UK BAYON official technical specifications	https://dmassets.hyundai.com/is/content/hyundaiautoever/BAYON_Tech_Specpdf
EU-HYUNDAI-CRETA-I-SUV-5D-01	4270	1780	1630	Hyundai Motor India Creta official brochure	https://www.hyundai.com/content/dam/hyundai/et/en/data/marketing/brochure/product/creta/creta-ebrochure-2015.pdf
```

## 下一步优先处理

1. 闭合 Accent II Hatchback 与 Sedan，并严格区分改款前后是否改变长度。
2. 闭合 Elantra III Hatchback 与 Sedan 的高复用尺寸组。
3. 随后处理 Atos、Elantra IV、Elantra V、Elantra VI 和 Equus。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6601-6700_ktype_dimension_mapping_final.tsv
- left18448_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 38 个 Hyundai Ktype。本轮新增或修改 77 条映射，首次创建 20 个尺寸组。
* Accent II LC 按三门／五门、改款前／改款后和 Sedan 外廓拆分；改款前 Hatchback 为 `4200×1670×1395`，改款后为 `4215×1680×1395`，Sedan 则分别为 `4235×1670×1395` 与 `4260×1680×1405`。([汽车数据网][1])
* Elantra III、IV、V、VI 已按 BodyStyle、车身代码和改款边界闭合；SR Turbo 因外廓规格不同，使用独立尺寸组。([汽车数据网][2])
* Equus II VI 已拆分改款前后；改款后英寸规格按规则换算并取整为 `5159×1890×1491`。([汽车数据网][3])
* 已完成一次机械收尾：表头正确、149 个 `id` 唯一、63 个尺寸组唯一、100 个输入 Ktype 全覆盖、所有引用闭合、无孤立尺寸组、无空缺三维或来源。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：149
* PENDING 映射：0
* DIMENSION_GROUP：63
* 未闭合引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57289	57289	Coupe	Integra III	DC2	3	EU-HONDA-INTEGRA-III-DC2-VTIR-COUPE-3D-01	HIGH	DC2 VTi-R三门车身；与既有Type-R尺寸组分离。	READY
16597_prefl	16597	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	HIGH	改款前物理分支。	READY
16597_facelift	16597	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	HIGH	改款后物理分支。	READY
16816	16816	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
120218	120218	Hatchback	Jazz II	GD	5	EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	HIGH		READY
116390_prefl	116390	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-PREFL-01	HIGH	2015至2017改款前外廓。	READY
116390_facelift	116390	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-02	HIGH	2017改款后1.3外廓；不复用既有1.5改款尺寸组。	READY
126827	126827	Hatchback	Jazz IV	GK	5	EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-01	HIGH	2017改款五门车身。	READY
154977	154977	Hatchback	Jazz V		5	EU-HONDA-JAZZ-V-GR-HATCHBACK-5D-FACELIFT-01	HIGH	2023改款五门车身。	READY
11415	11415	Hatchback	Logo I	GA3	5	EU-HONDA-LOGO-I-GA3-HATCHBACK-5D-01	HIGH		READY
7822_prefl	7822	Coupe	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-COUPE-2D-PREFL-01	HIGH	固定前照灯改款前分支。	READY
7822_facelift	7822	Coupe	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-COUPE-2D-FACELIFT-01	HIGH	2002改款分支。	READY
7823_prefl	7823	Convertible	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-PREFL-01	HIGH	NSX-T 2002改款前物理外廓。	READY
7823_facelift	7823	Convertible	NSX I	NA2	2	EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-FACELIFT-01	HIGH	NSX-T 2002改款后物理外廓。	READY
127200	127200	Coupe	NSX II	NC1	2	EU-HONDA-NSX-II-NC1-COUPE-2D-01	HIGH		READY
44329_prefl	44329	MPV	Odyssey III	RL3	5	EU-HONDA-ODYSSEY-III-RL3-MPV-5D-PREFL-01	HIGH	RL3改款前物理外廓。	READY
44329_facelift	44329	MPV	Odyssey III	RL4	5	EU-HONDA-ODYSSEY-III-RL4-MPV-5D-FACELIFT-01	HIGH	RL4改款后物理外廓。	READY
55241_prefl	55241	MPV	Odyssey IV	RL5	5	EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-PREFL-01	HIGH	RL5 2011至2013改款前外廓。	READY
55241_facelift	55241	MPV	Odyssey IV	RL5	5	EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-FACELIFT-01	HIGH	RL5 2014改款后外廓。	READY
14686_prefl	14686	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
14686_facelift	14686	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
106543_prefl	106543	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
106543_facelift	106543	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
128257_prefl	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-PREFL-01	HIGH	YF4四驱改款前物理外廓。	READY
128257_facelift	128257	SUV	Pilot II	YF4	5	EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	HIGH	YF4四驱2012改款后物理外廓。	READY
44336	44336	SUV	Pilot I		5	EU-HONDA-PILOT-I-SUV-5D-01	HIGH		READY
7820	7820	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
162855	162855	Coupe	Prelude VI		3	EU-HONDA-PRELUDE-VI-COUPE-3D-01	HIGH	2026欧洲版三门掀背式Coupe车身。	READY
10581	10581	Coupe	Prelude III		2	EU-HONDA-PRELUDE-III-BA-COUPE-2D-01	HIGH		READY
7821	7821	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
11510	11510	Coupe	Prelude V		2	EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	HIGH		READY
10469_prefl	10469	Convertible	S2000 I	AP1	2	EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-PREFL-01	HIGH	2004改款前物理分支。	READY
10469_facelift	10469	Convertible	S2000 I	AP1	2	EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-FACELIFT-01	HIGH	2004改款后物理分支。	READY
15955	15955	MPV	Stream I		5	EU-HONDA-STREAM-I-MPV-5D-01	HIGH		READY
15956	15956	MPV	Stream I		5	EU-HONDA-STREAM-I-MPV-5D-01	HIGH		READY
154814	154814	SUV	ZR-V I		5	EU-HONDA-ZR-V-I-SUV-5D-01	HIGH		READY
158130	158130	Sedan	EH7 I		4	EU-HONGQI-EH7-I-SEDAN-4D-01	HIGH		READY
162809	162809	SUV	EHS7 I		5	EU-HONGQI-EHS7-I-SUV-5D-01	HIGH		READY
160687	160687	SUV	EHS7 I		5	EU-HONGQI-EHS7-I-SUV-5D-01	HIGH		READY
142868	142868	SUV	E-HS9 I		5	EU-HONGQI-E-HS9-I-SUV-5D-01	HIGH		READY
142869	142869	SUV	E-HS9 I		5	EU-HONGQI-E-HS9-I-SUV-5D-01	HIGH		READY
803442	803442	Hatchback	H6 I		5	EU-HONGQI-H6-I-HATCHBACK-5D-01	HIGH	五门掀背式车身。	READY
802897	802897	SUV	HS3 I		5	EU-HONGQI-HS3-I-SUV-5D-01	HIGH		READY
802896	802896	SUV	HS3 I		5	EU-HONGQI-HS3-I-SUV-5D-01	HIGH		READY
803374	803374	SUV	HS5 II		5	EU-HONGQI-HS5-II-SUV-5D-01	HIGH		READY
803375	803375	SUV	HS5 II		5	EU-HONGQI-HS5-II-SUV-5D-01	HIGH		READY
44427	44427	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
44431	44431	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
12749	12749	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
12750	12750	SUV	H1 I		4	EU-HUMMER-H1-I-SUV-4D-01	HIGH	四门封闭式车身。	READY
18257	18257	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
18443	18443	SUV	H2 I	GMT825	5	EU-HUMMER-H2-I-SUV-5D-01	HIGH		READY
18809	18809	Pickup	H2 I	GMT825	4	EU-HUMMER-H2-I-PICKUP-4D-01	HIGH	H2 SUT四门短货斗车身。	READY
120505	120505	Pickup	H2 I	GMT825	4	EU-HUMMER-H2-I-PICKUP-4D-01	HIGH	H2 SUT四门短货斗车身。	READY
18977	18977	SUV	H3 I	GMT345	5	EU-HUMMER-H3-I-SUV-5D-01	HIGH		READY
51049	51049	SUV	H3 I	GMT345	5	EU-HUMMER-H3-I-SUV-5D-01	HIGH		READY
53710	53710	Pickup	H3T I	GMT745	4	EU-HUMMER-H3T-I-PICKUP-4D-01	HIGH	四门乘员舱短货斗车身。	READY
14597_3dr_prefl	14597	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
14597_5dr_prefl	14597	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
14597_3dr_facelift	14597	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
14597_5dr_facelift	14597	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
15952_3dr_prefl	15952	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
15952_5dr_prefl	15952	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
15952_3dr_facelift	15952	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
15952_5dr_facelift	15952	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
17757_3dr_prefl	17757	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
17757_5dr_prefl	17757	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
17757_3dr_facelift	17757	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
17757_5dr_facelift	17757	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
18693_prefl	18693	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
18693_facelift	18693	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
18694_prefl	18694	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
18694_facelift	18694	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
15380_3dr_prefl	15380	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
15380_5dr_prefl	15380	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16590_3dr_prefl	16590	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16590_5dr_prefl	16590	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16590_3dr_facelift	16590	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
16590_5dr_facelift	16590	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
16721_prefl	16721	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16721_facelift	16721	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
55825	55825	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
17767_3dr_facelift	17767	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
17767_5dr_facelift	17767	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
17769	17769	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
16811_3dr_prefl	16811	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	HIGH	三门改款前外廓。	READY
16811_5dr_prefl	16811	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
16811_3dr_facelift	16811	Hatchback	Accent II	LC	3	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	HIGH	三门改款后外廓。	READY
16811_5dr_facelift	16811	Hatchback	Accent II	LC	5	EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
18695_prefl	18695	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
18695_facelift	18695	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
55641	55641	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
106316	106316	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55642	55642	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55644	55644	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
55645	55645	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
109977	109977	Sedan	Accent IV		4	EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	HIGH		READY
16169	16169	Hatchback	Atos I		5	EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	HIGH		READY
145128	145128	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
802506	802506	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	HIGH	2024改款外廓。	READY
145129	145129	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
145131	145131	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
154573	154573	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
145123	145123	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
801327	801327	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	HIGH	2024改款外廓。	READY
145517	145517	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	MEDIUM	2021首发外廓；2024改款由后续新Ktype承接。	READY
121109	121109	SUV	Creta I		5	EU-HYUNDAI-CRETA-I-SUV-5D-01	HIGH		READY
15127_prefl	15127	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
15127_facelift	15127	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15129_prefl	15129	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
15129_facelift	15129	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
17570	17570	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
17571	17571	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15948_prefl	15948	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
15948_facelift	15948	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15949_prefl	15949	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
15949_facelift	15949	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15128_prefl	15128	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
15128_facelift	15128	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15130_prefl	15130	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
15130_facelift	15130	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15950_prefl	15950	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
15950_facelift	15950	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15951_prefl	15951	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
15951_facelift	15951	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
17496	17496	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
17497	17497	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15971_prefl	15971	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
15971_facelift	15971	Hatchback	Elantra III	XD	5	EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	HIGH	2003改款后外廓。	READY
15972_prefl	15972	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
15972_facelift	15972	Sedan	Elantra III	XD	4	EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	HIGH	2003改款后外廓。	READY
110520	110520	Sedan	Elantra IV	HD	4	EU-HYUNDAI-ELANTRA-IV-HD-SEDAN-4D-01	HIGH		READY
18892	18892	Sedan	Elantra IV	HD	4	EU-HYUNDAI-ELANTRA-IV-HD-SEDAN-4D-01	HIGH		READY
55681_prefl	55681	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-PREFL-01	HIGH	2013改款前外廓。	READY
55681_facelift	55681	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-FACELIFT-01	HIGH	2013改款后外廓。	READY
58679_prefl	58679	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-PREFL-01	HIGH	2013改款前外廓。	READY
58679_facelift	58679	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-FACELIFT-01	HIGH	2013改款后外廓。	READY
17255_prefl	17255	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-PREFL-01	HIGH	2013改款前外廓。	READY
17255_facelift	17255	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-FACELIFT-01	HIGH	2013改款后外廓。	READY
128261_prefl	128261	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-PREFL-01	HIGH	2019改款前外廓。	READY
128261_facelift	128261	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-FACELIFT-01	HIGH	2019改款后外廓。	READY
119635_prefl	119635	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-PREFL-01	HIGH	2019改款前外廓。	READY
119635_facelift	119635	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-FACELIFT-01	HIGH	2019改款后外廓。	READY
128002_prefl	128002	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-PREFL-01	HIGH	2019改款前外廓。	READY
128002_facelift	128002	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-FACELIFT-01	HIGH	2019改款后外廓。	READY
123947_prefl	123947	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SR-SEDAN-4D-PREFL-01	HIGH	SR Turbo改款前外廓。	READY
123947_facelift	123947	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SR-SEDAN-4D-FACELIFT-01	HIGH	SR Turbo改款后外廓。	READY
54904_prefl	54904	Sedan	Equus II	VI	4	EU-HYUNDAI-EQUUS-II-VI-SEDAN-4D-PREFL-01	HIGH	2014改款前外廓。	READY
54904_facelift	54904	Sedan	Equus II	VI	4	EU-HYUNDAI-EQUUS-II-VI-SEDAN-4D-FACELIFT-01	HIGH	2014改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6601-6700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-INTEGRA-III-DC2-VTIR-COUPE-3D-01	4380	1710	1335	CarsGuide Honda Integra dimensions	https://www.carsguide.com.au/honda/integra/car-dimensions/1993
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	4400	1725	1400	Auto-Data Honda Integra IV (DC5) generation specifications	https://www.auto-data.net/en/honda-integra-iv-dc5-generation-2578
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	4400	1725	1395	Auto-Data Honda Integra IV (DC5 facelift 2004) generation specifications	https://www.auto-data.net/en/honda-integra-iv-dc5-facelift-2004-generation-9180
EU-HONDA-JAZZ-II-GD-HATCHBACK-5D-01	3830	1675	1525	Auto-Data Honda Jazz generation specifications	https://www.auto-data.net/en/honda-jazz-i-generation-2588
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-PREFL-01	3995	1694	1525	Auto-Data Honda Jazz III generation specifications	https://www.auto-data.net/en/honda-jazz-iii-generation-4552
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-02	4028	1694	1525	Auto-Data Honda Jazz III facelift 2017 1.3 i-VTEC specifications	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.3-i-vtec-102hp-32643
EU-HONDA-JAZZ-IV-GK-HATCHBACK-5D-FACELIFT-01	4051	1694	1544	Auto-Data Honda Jazz facelift 2017 specifications	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.5-i-vtec-130hp-32645
EU-HONDA-JAZZ-V-GR-HATCHBACK-5D-FACELIFT-01	4089	1694	1526	Honda UK Jazz Hybrid official specifications	https://www.honda.co.uk/cars/new/jazz-hybrid/specifications.html
EU-HONDA-LOGO-I-GA3-HATCHBACK-5D-01	3785	1645	1520	Auto-Data Honda Logo specifications	https://www.auto-data.net/en/honda-logo-model-1309
EU-HONDA-NSX-I-NA2-COUPE-2D-PREFL-01	4425	1810	1170	Auto-Data Honda NSX I Coupe specifications	https://www.auto-data.net/en/honda-nsx-i-coupe-generation-2669
EU-HONDA-NSX-I-NA2-COUPE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX I Coupe facelift 2002 specifications	https://www.auto-data.net/en/honda-nsx-i-coupe-facelift-2002-generation-8112
EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-PREFL-01	4420	1810	1175	Auto-Data Honda NSX-T I 3.2 V6 VTEC specifications	https://www.auto-data.net/en/honda-nsx-t-i-3.2-v6-vtec-280hp-54809
EU-HONDA-NSX-I-NA2-CONVERTIBLE-2D-FACELIFT-01	4425	1810	1170	Auto-Data Honda NSX-T I facelift 2002 3.2 V6 VTEC specifications	https://www.auto-data.net/en/honda-nsx-t-i-facelift-2002-3.2-v6-vtec-280hp-54802
EU-HONDA-NSX-II-NC1-COUPE-2D-01	4487	1920	1204	Auto-Data Honda NSX II specifications	https://www.auto-data.net/en/honda-nsx-ii-coupe-3.5-i-vtec-bi-turbo-v6-581hp-hybrid-sh-awd-dct-32058
EU-HONDA-ODYSSEY-III-RL3-MPV-5D-PREFL-01	5105	1958	1748	Honda News 2005 Honda Odyssey Body	https://hondanews.com/en-US/honda-automobiles/releases/release-726e2461d33d92cff8f2a2004c34c3a1-2005-honda-odyssey-body
EU-HONDA-ODYSSEY-III-RL4-MPV-5D-FACELIFT-01	5133	1958	1748	Honda News 2009 Honda Odyssey Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-c0fe0dfee5573ce4bac3eb004c34bc52-2009-honda-odyssey-specifications-and-features
EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-PREFL-01	5154	2012	1737	Honda News 2011 Honda Odyssey Overview	https://hondanews.com/en-US/honda-automobiles/releases/release-39ea457927744650b4ae2f39934ae503-2011-honda-odyssey-overview
EU-HONDA-ODYSSEY-IV-RL5-MPV-5D-FACELIFT-01	5154	2012	1737	Honda News 2014 Honda Odyssey Specifications and Features	https://hondanews.com/en-US/honda-automobiles/releases/release-1267ee1d741b4207924b585d98cf5a56-2014-honda-odyssey-specifications-and-features
EU-HONDA-PILOT-II-SUV-5D-PREFL-01	4849	1994	1803	Auto-Data Honda Pilot II specifications	https://www.auto-data.net/en/honda-pilot-ii-3.5-v6-253hp-4wd-automatic-41040
EU-HONDA-PILOT-II-SUV-5D-FACELIFT-01	4862	1994	1839	Auto-Data Honda Pilot II facelift 2012 specifications	https://www.auto-data.net/en/honda-pilot-ii-facelift-2012-3.5-v6-253hp-4wd-automatic-41042
EU-HONDA-PILOT-I-SUV-5D-01	4775	1964	1793	Auto-Data Honda Pilot I specifications	https://www.auto-data.net/en/honda-pilot-i-3.5-v6-243hp-awd-automatic-12181
EU-HONDA-PRELUDE-V-BB-COUPE-2D-01	4545	1750	1315	Auto-Data Honda Prelude V specifications	https://www.auto-data.net/en/honda-prelude-v-bb-2.2-16v-bb6-bb8-185hp-12197
EU-HONDA-PRELUDE-VI-COUPE-3D-01	4525	1880	1349	Honda Europe 2026 Prelude official technical specification	https://hondanews.eu/eu/en/cars/media/pressreleases/553085/2026-honda-prelude-coupe-ehev-technical-specification-eu
EU-HONDA-PRELUDE-III-BA-COUPE-2D-01	4460	1695	1295	Auto-Data Honda Prelude specifications	https://www.auto-data.net/en/honda-prelude-model-1305
EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-PREFL-01	4135	1750	1270	Auto-Data Honda S2000 AP1 specifications	https://www.auto-data.net/en/honda-s2000-ap1-generation-2670
EU-HONDA-S2000-I-AP1-CONVERTIBLE-2D-FACELIFT-01	4135	1750	1285	Auto-Data Honda S2000 AP1 facelift 2004 specifications	https://www.auto-data.net/en/honda-s2000-ap1-facelift-2004-generation-7192
EU-HONDA-STREAM-I-MPV-5D-01	4570	1695	1605	Auto-Data Honda Stream specifications	https://www.auto-data.net/en/honda-stream-model-1301
EU-HONDA-ZR-V-I-SUV-5D-01	4570	1840	1620	Auto-Data Honda ZR-V specifications	https://www.auto-data.net/en/honda-zr-v-model-3222
EU-HONGQI-EH7-I-SEDAN-4D-01	4980	1915	1490	Hongqi official EH7 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_eh7.html
EU-HONGQI-EHS7-I-SUV-5D-01	4925	1950	1680	Hongqi official EHS7 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_ehs7.html
EU-HONGQI-E-HS9-I-SUV-5D-01	5209	2010	1731	Hongqi official E-HS9 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_E-hs9.html
EU-HONGQI-H6-I-HATCHBACK-5D-01	4990	1876	1450	Hongqi Russia official H6 specifications	https://hongqi.ru/news/hongqi-h6
EU-HONGQI-HS3-I-SUV-5D-01	4655	1900	1668	Hongqi official HS3 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_hs3.html
EU-HONGQI-HS5-II-SUV-5D-01	4785	1905	1700	Hongqi official HS5 specifications	https://www.hongqi-auto.com/pages/cartype/cartype_hs5.html
EU-HUMMER-H1-I-SUV-4D-01	4686	2197	1905	Auto-Data Hummer H1 generation specifications	https://www.auto-data.net/en/hummer-h1-model-2237
EU-HUMMER-H2-I-SUV-5D-01	4821	2062	2012	Edmunds 2004 HUMMER H2 specifications	https://www.edmunds.com/hummer/h2/2004/st-100273977/features-specs/
EU-HUMMER-H2-I-PICKUP-4D-01	5170	2063	2012	Automobile-Catalog 2008 Hummer H2 SUT specifications	https://www.automobile-catalog.com/car/2008/1430915/hummer_h2_sut.html
EU-HUMMER-H3-I-SUV-5D-01	4763	1895	1859	Edmunds 2009 HUMMER H3 specifications	https://www.edmunds.com/hummer/h3/2009/features-specs/
EU-HUMMER-H3T-I-PICKUP-4D-01	5403	1905	1831	Edmunds 2009 HUMMER H3T specifications	https://www.edmunds.com/hummer/h3t/2009/features-specs/
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-PREFL-01	4200	1670	1395	Auto-Data Hyundai Accent Hatchback II pre-facelift specifications	https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.3-i-12v-75hp-13695
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-PREFL-01	4200	1670	1395	Auto-Data Hyundai Accent Hatchback II pre-facelift specifications	https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.3-i-12v-75hp-13695
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-3D-FACELIFT-01	4215	1680	1395	Auto-Data Hyundai Accent Hatchback II facelift specifications	https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.5-crdi-82hp-13697
EU-HYUNDAI-ACCENT-II-LC-HATCHBACK-5D-FACELIFT-01	4215	1680	1395	Auto-Data Hyundai Accent Hatchback II facelift specifications	https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.5-crdi-82hp-13697
EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-PREFL-01	4235	1670	1395	Auto-Data Hyundai Accent II Sedan pre-facelift specifications	https://www.auto-data.net/en/hyundai-accent-ii-1.5-i-12v-92hp-13691
EU-HYUNDAI-ACCENT-II-LC-SEDAN-4D-FACELIFT-01	4260	1680	1405	Auto-Data Hyundai Accent II Sedan facelift specifications	https://www.auto-data.net/en/hyundai-accent-ii-1.6-i-16v-105hp-13694
EU-HYUNDAI-ACCENT-IV-SEDAN-4D-01	4370	1705	1455	Hyundai Motor Company Accent official catalogue	https://www.hyundai.com/content/dam/hyundai/kr/ko/html/pdf/en-cn-catalog/en-catalog/accent-catalog-eng.pdf
EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	3495	1495	1615	Auto-Data Hyundai Atos 1.0 i specifications	https://www.auto-data.net/en/hyundai-atos-1.0-i-58hp-13735
EU-HYUNDAI-BAYON-I-SUV-5D-PREFL-01	4180	1775	1490	Hyundai Motor Europe all-new BAYON official press kit	https://www.hyundai.news/eu/models/suv/bayon/press-kit/all-new-hyundai-bayon-a-stylish-and-sleek-crossover-suv.html
EU-HYUNDAI-BAYON-I-SUV-5D-FACELIFT-01	4180	1775	1500	Hyundai Motor UK BAYON official technical specifications	https://dmassets.hyundai.com/is/content/hyundaiautoever/BAYON_Tech_Specpdf
EU-HYUNDAI-CRETA-I-SUV-5D-01	4270	1780	1630	Hyundai Motor India Creta official brochure	https://www.hyundai.com/content/dam/hyundai/et/en/data/marketing/brochure/product/creta/creta-ebrochure-2015.pdf
EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-PREFL-01	4495	1720	1425	Auto-Data Hyundai Elantra III Hatchback specifications	https://www.auto-data.net/en/hyundai-elantra-iii-hatchback-generation-3007
EU-HYUNDAI-ELANTRA-III-XD-HATCHBACK-5D-FACELIFT-01	4495	1720	1425	Auto-Data Hyundai Elantra III Hatchback specifications	https://www.auto-data.net/en/hyundai-elantra-iii-hatchback-generation-3007
EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-PREFL-01	4495	1720	1425	Auto-Data Hyundai Elantra III Sedan specifications	https://www.auto-data.net/en/hyundai-elantra-iii-generation-3006
EU-HYUNDAI-ELANTRA-III-XD-SEDAN-4D-FACELIFT-01	4495	1720	1425	Auto-Data Hyundai Elantra III Sedan specifications	https://www.auto-data.net/en/hyundai-elantra-iii-generation-3006
EU-HYUNDAI-ELANTRA-IV-HD-SEDAN-4D-01	4505	1775	1490	Auto-Data Hyundai Elantra IV specifications	https://www.auto-data.net/en/hyundai-elantra-iv-generation-3005
EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-PREFL-01	4529	1775	1435	Auto-Data Hyundai Elantra V specifications	https://www.auto-data.net/en/hyundai-elantra-v-generation-7209
EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-FACELIFT-01	4550	1775	1445	Auto-Data Hyundai Elantra V facelift 2013 specifications	https://www.auto-data.net/en/hyundai-elantra-v-facelift-2013-generation-8042
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-PREFL-01	4569	1801	1435	Auto-Data Hyundai Elantra VI (AD) specifications	https://www.auto-data.net/en/hyundai-elantra-vi-ad-generation-6034
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-4D-FACELIFT-01	4620	1800	1435	Auto-Data Hyundai Elantra VI (AD facelift 2019) specifications	https://www.auto-data.net/en/hyundai-elantra-vi-ad-facelift-2019-generation-6531
EU-HYUNDAI-ELANTRA-VI-AD-SR-SEDAN-4D-PREFL-01	4570	1800	1440	Carsales 2017 Hyundai Elantra SR Turbo specifications	https://www.carsales.com.au/research/hyundai/elantra/2017/sr-turbo/
EU-HYUNDAI-ELANTRA-VI-AD-SR-SEDAN-4D-FACELIFT-01	4620	1800	1440	Carsales 2020 Hyundai Elantra Sport Premium specifications	https://www.carsales.com.au/research/hyundai/elantra/2020/sport-premium/
EU-HYUNDAI-EQUUS-II-VI-SEDAN-4D-PREFL-01	5160	1890	1495	Auto-Data Hyundai Equus (VI) specifications	https://www.auto-data.net/en/hyundai-equus-vi-generation-8562
EU-HYUNDAI-EQUUS-II-VI-SEDAN-4D-FACELIFT-01	5159	1890	1491	Edmunds 2016 Hyundai Equus specifications	https://www.edmunds.com/hyundai/equus/2016/features-specs/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6601-6700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.3-i-12v-gl-86hp-13696 "https://www.auto-data.net/en/hyundai-accent-hatchback-ii-1.3-i-12v-gl-86hp-13696"
[2]: https://www.auto-data.net/en/hyundai-elantra-iii-hatchback-generation-3007 "https://www.auto-data.net/en/hyundai-elantra-iii-hatchback-generation-3007"
[3]: https://www.auto-data.net/en/hyundai-equus-vi-generation-8562 "https://www.auto-data.net/en/hyundai-equus-vi-generation-8562"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3699 行）
- 累计尺寸组：dimension_groups_final.tsv（1013 行）

