# 任务：all 第 8301-8400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0084__b59f9f90


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8301-8400 行

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
all.tsv

【当前独立任务】
all 第 8301-8400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	4063	1720	1446
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2016-01	4063	1720	1446
EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	4063	1720	1446
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-CITROEN-C25-MINIBUS-4X4-SWB-LOWROOF-01	4759	1965	2096
EU-CITROEN-C25-MINIBUS-LWB-HIGHROOF-01	5489	1965	2420
EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	4759	1965	2096
EU-FIAT-500-110-SEDAN-01	2970	1320	1325
EU-FIAT-500-120-GIARDINIERA-WAGON-01	3185	1323	1354
EU-FIAT-500-312-CONVERTIBLE-01	3550	1650	1490
EU-FIAT-500-312-HATCHBACK-01	3546	1627	1488
EU-FIAT-500-A-TOPOLINO-SEDAN-01	3215	1275	1375
EU-FIAT-500-B-TOPOLINO-SEDAN-01	3210	1273	1375
EU-FIAT-500-C-TOPOLINO-SEDAN-01	3245	1273	1377
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1832
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-LOWROOF-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-LWB-LOWROOF-01	4633	1722	1817
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	4253	1722	2086
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	4253	1722	1831
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	4253	1722	2073
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	4253	1722	1818
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	4740	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	4390	1832	2100
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	4406	1832	1899
EU-FIAT-DOBLO-II-263-MPV-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-FACELIFT-01	4406	1832	2125
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-II-CARGO-MAXI-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-II-CARGO-MAXI-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-II-CARGO-SWB-FACELIFT-01	4406	1832	1845
EU-FIAT-DOBLO-II-CARGO-SWB-PREFL-01	4390	1832	1845
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468
EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	3408	1500	1485
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420
EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	3380	1460	1445
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540
EU-FIAT-PANDA-II-4X4-HATCHBACK-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-4X4-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	3538	1589	1614
EU-FIAT-PANDA-III-319-HATCHBACK-01	3653	1643	1551
EU-FIAT-PANDA-I-PREFL-4X4-01	3390	1485	1470
EU-FIAT-ULYSSE-I-220-MPV-01	4454	1834	1714
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	3689	1558	1405
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	3644	1555	1432
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	3644	1548	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	3644	1555	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	3644	1560	1370
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBODIESEL-01	3644	1560	1420
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	3644	1555	1432
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	3644	1548	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	3644	1555	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-TURBODIESEL-01	3644	1560	1420
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	4105	1690	1515
EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	3995	1615	1380
EU-ISUZU-GEMINI-II-JT-HATCHBACK-GTI-01	4010	1615	1365
EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	4040	1615	1380
EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	4035	1698	1660
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	3392	1537	1460
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	4829	1915	1887
EU-LAND-ROVER-DISCOVERY-IV-SUV-01	4829	1915	1887
EU-MAZDA-E-SERIES-III-SR1-MPV-01	4965	1690	1955
EU-MAZDA-E-SERIES-III-SR2-VAN-01	4690	1690	1960
EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	4390	1690	1960
EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	4690	1690	1960
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301
EU-MITSUBISHI-LANCER-V-CBW-WAGON-5D-01	4270	1690	1465
EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	4585	1760	1515
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	4295	1690	1395
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488
EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	4730	1772	1530
EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	4730	1772	1481
EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	4768	1760	1530
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	5182	1904	1958
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-DIESEL-01	4535	1996	2067
EU-RENAULT-TRAFIC-I-PHASE1-PLATFORM-PETROL-01	4535	1996	2070
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	4542	1905	2037
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	3687	1654	1470
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	3600	1654	1470
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-FACELIFT2012-01	4950	1970	1865
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	4750	1800	1845
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	4750	1800	1815
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-TURBODIESEL-01	4750	1800	1830
EU-TOYOTA-LAND-CRUISER-70-CONVERTIBLE-2D-SWB-HARDTOP-01	4040	1690	1890
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	4405	1790	1950
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	3975	1690	1870
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900
EU-TOYOTA-LAND-CRUISER-PRADO-70-SUV-5D-LWB-01	4585	1690	1890
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-3D-01	4485	1885	1875
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-01	4760	1885	1890
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	3950	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	3945	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	3885	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	3950	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	3945	1695	1510
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	3885	1695	1510
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford USA	Aerostar	3.0 I V6	Großraumlimousine	Heckantrieb	Benzin	108	147	Sep 1985	Dec 1997	2024-03-01	9188
Ford USA	Aerostar	4.0 I V6 4WD	Großraumlimousine	Allrad	Benzin	115	156	Sep 1989	Dec 1997	2024-03-01	9189
Honda	Civic iv	1.6 I 16V 4X4	Stufenheck	Allrad	Benzin	80	109	Oct 1989	Sep 1991	2024-03-01	9191
Isuzu	Gemini	1.5	Stufenheck	Frontantrieb	Benzin	52	71	Feb 1988	Dec 1989	2024-03-01	9193
Isuzu	Campo	2.0 4WD	Pick-up	Allrad	Benzin	58	79	Jun 1985	Dec 1988	2024-03-01	9194
Isuzu	Campo	2	Pick-up	Heckantrieb	Benzin	58	79	Jun 1985	Dec 1988	2024-03-01	9195
Isuzu	Campo	2.5 D	Pick-up	Heckantrieb	Diesel	55	75	Jan 1983	Dec 1990	2024-03-01	9196
Isuzu	Campo	2.5 D 4WD	Pick-up	Allrad	Diesel	55	75	Jan 1983	Dec 1990	2024-03-01	9197
Lancia	Y10	1.0 Fire Allrad	Schrägheck	Allrad	Benzin	33	45	Dec 1987	Feb 1992	2024-03-01	9198
Fiat	Croma	1900 Turbo D I.d.	Schrägheck	Frontantrieb	Diesel	69	94	Nov 1992	Dec 1996	2024-03-01	9199
Renault	Kangoo	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	43	58	Aug 1997	-	2024-03-01	9200
BMW	3	316 G	Schrägheck	Heckantrieb	Benzin/Erdgas (CNG)	75	102	Feb 1996	Aug 2000	2024-03-01	9201
Renault	Kangoo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Aug 1997	Jun 2008	2024-03-01	9202
Renault	Kangoo	D 55 1.9	Kasten/Großraumlimousine	Frontantrieb	Diesel	40	54	Aug 1997	-	2024-03-01	9203
Renault	Kangoo	D 65 1.9	Kasten/Großraumlimousine	Frontantrieb	Diesel	47	64	Aug 1997	-	2024-03-01	9204
Citroën	C25	2	Kasten	Frontantrieb	Benzin	62	84	Feb 1991	Mar 1994	2024-03-01	9205
Citroën	C25	2.0 E	Kasten	Frontantrieb	Benzin	58	79	Sep 1981	Mar 1994	2024-03-01	9206
Citroën	C25	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	62	84	Jan 1987	Mar 1994	2024-03-01	9207
NSU	Spider	56	Cabriolet	Heckantrieb	Benzin	37	50	Jan 1964	Dec 1968	2024-03-01	9208
Land Rover	110/127	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	98	133	Sep 1983	Jul 1990	2024-03-01	9209
Land Rover	90	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	62	84	Sep 1985	Aug 1990	2024-03-01	9210
Land Rover	110/127	2.5 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	63	86	Sep 1986	Jul 1990	2024-03-01	9211
Mazda	323 iii hatchback	1.6 GT Turbo 4WD	Schrägheck	Allrad	Benzin	110	150	Aug 1987	Oct 1989	2024-03-01	9212
Mazda	323 iii hatchback	1.6 GT Turbo	Schrägheck	Frontantrieb	Benzin	103	140	Oct 1985	Aug 1993	2024-03-01	9213
Mazda	E	E2000 4WD	Bus	Allrad	Benzin	60	82	Oct 1988	Sep 1989	2024-03-01	9218
Mitsubishi	Lancer v	1.6 16V 4WD	Stufenheck	Allrad	Benzin	83	113	Jun 1992	Dec 1996	2024-03-01	9219
Oldsmobile	Cutlass supreme	2.8 V6	Coupe	Frontantrieb	Benzin	97	132	Sep 1988	Dec 1997	2024-03-01	9222
Oldsmobile	Cutlass supreme	3.1 V6	Coupe	Frontantrieb	Benzin	101	137	Sep 1988	Dec 1997	2024-03-01	9223
Oldsmobile	Cutlass supreme	3.4 V6	Coupe	Frontantrieb	Benzin	149	203	Sep 1990	Dec 1997	2024-03-01	9224
Opel	Omega a caravan	3	Kombi	Heckantrieb	Benzin	115	156	Mar 1987	Mar 1994	2024-03-01	9225
Fiat	Freemont	2.0 JTD 4X4	Großraumlimousine	Allrad	Diesel	120	163	Aug 2011	Dec 2015	2024-03-01	9230
Peugeot	309 i	1.6 CAT	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1986	Dec 1989	2024-03-01	9231
Renault	Trafic	2.0 4X4	Bus	Allrad	Benzin	59	80	Jun 1986	Apr 1989	2024-03-01	9233
Renault	Trafic	2.1 D 4X4	Kasten	Allrad	Diesel	43	58	Nov 1986	Apr 1989	2024-03-01	9235
Opel	Astra h	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	74	101	Mar 2004	Oct 2010	2024-03-01	9243
Opel	Astra h	1.9 Cdti	Kasten/Kombi	Frontantrieb	Diesel	110	150	Sep 2004	Oct 2010	2024-03-01	9244
Renault	Fluence	Z.e.	Stufenheck	Frontantrieb	Elektro	70	95	Feb 2012	-	2024-03-01	9245
Opel	Astra h	1.9 Cdti 16V	Kasten/Kombi	Frontantrieb	Diesel	88	120	Aug 2004	Oct 2010	2024-03-01	9246
Opel	Astra h	1.9 Cdti	Kasten/Kombi	Frontantrieb	Diesel	88	120	Sep 2005	Oct 2010	2024-03-01	9247
Opel	Astra h	1.3 Cdti	Kasten/Kombi	Frontantrieb	Diesel	66	90	Aug 2005	Oct 2010	2024-03-01	9248
Opel	Astra h	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	81	110	Feb 2007	Oct 2014	2024-03-01	9249
Opel	Astra h	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	92	125	Feb 2007	Oct 2010	2024-03-01	9250
Opel	Zafira	1.7 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Jan 2008	Apr 2015	2024-03-01	9251
Opel	Zafira	1.6 CNG Turbo VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	110	150	Feb 2009	Apr 2015	2024-03-01	9252
Opel	Zafira	1.8 VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin	103	140	Jul 2005	Apr 2015	2024-03-01	9253
Renault	Wind	1.2 TCE 100	Cabriolet	Frontantrieb	Benzin	75	102	Feb 2011	Aug 2013	2025-12-01	9254
Renault	Twingo	1.2 TCE 100	Schrägheck	Frontantrieb	Benzin	75	102	Feb 2011	Aug 2013	2026-05-01	9255
Fiat	500	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	69	Dec 2010	-	2024-03-01	9256
Toyota	Yaris	1.33 Vvt-i	Schrägheck	Frontantrieb	Benzin	73	99	Jul 2010	May 2011	2024-03-01	9257
Lancia	Ypsilon	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	57	78	Nov 2010	Dec 2011	2024-03-01	9258
Toyota	Hiace iv	2.4	Kasten	Heckantrieb	Benzin	88	120	Aug 1989	Aug 1995	2024-03-01	9259
Lancia	Musa	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	57	78	Nov 2010	Sep 2012	2024-03-01	9260
Bentley	Continental	6.0 Flex	Coupe	Allrad	Benzin/Ethanol	423	575	Nov 2010	Dec 2013	2024-03-01	9261
Fiat	Bravo ii	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Dec 2008	Dec 2014	2024-03-01	9262
Fiat	Grande punto	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	57	78	Dec 2008	-	2024-03-01	9263
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	180	245	May 2011	Mar 2018	2024-03-01	9264
Opel	Corsa d	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Sep 2009	Aug 2014	2024-03-01	9265
Spyker	C12	Zagato	Coupe	Heckantrieb	Benzin	368	500	Dec 2007	-	2024-03-01	9266
Spyker	C8	4.2	Coupe	Heckantrieb	Benzin	298	405	Apr 2000	-	2024-03-01	9267
Spyker	C8	4.2	Cabriolet	Heckantrieb	Benzin	298	405	Apr 2000	-	2024-03-01	9268
Spyker	C8	4.2	Coupe	Heckantrieb	Benzin	298	405	Apr 2010	-	2024-03-01	9269
Fiat	Panda	1.4 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	57	78	Oct 2009	-	2024-03-01	9274
Toyota	Hiace iv	2.4 4WD	Bus	Allrad	Benzin	88	120	Aug 1989	Jul 1995	2024-03-01	9279
Toyota	Hiace iv	2.4 4WD	Kasten	Allrad	Benzin	88	120	Aug 1989	Aug 1995	2024-03-01	9280
Toyota	Land cruiser	4	Geländewagen geschlossen	Allrad	Benzin	115	156	Aug 1987	Dec 1992	2024-03-01	9281
Toyota	Land cruiser 80	4	Geländewagen geschlossen	Allrad	Benzin	115	156	Jan 1990	Oct 1992	2024-03-01	9282
Citroën	Ds3	1.6 Racing	Schrägheck	Frontantrieb	Benzin	152	207	Feb 2011	Jul 2015	2024-03-01	9284
Peugeot	206+	1.4 I	Schrägheck	Frontantrieb	Benzin	54	73	Sep 2010	Jun 2013	2024-03-01	9285
Renault	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	63	86	Feb 2008	Jun 2015	2024-03-01	9286
Renault	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	63	86	Feb 2008	Jun 2015	2024-03-01	9287
Mercedes-benz	Slk	200	Cabriolet	Heckantrieb	Benzin	135	184	Feb 2011	-	2024-03-01	9288
Mercedes-benz	Slk	350	Cabriolet	Heckantrieb	Benzin	225	306	Feb 2011	-	2024-03-01	9289
Renault	Thalia ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	62	85	Sep 2008	Dec 2012	2025-12-01	9290
Renault	Thalia ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	47	64	Sep 2008	Jun 2014	2025-12-01	9291
Renault	Thalia ii	1.2 16V	Stufenheck	Frontantrieb	Benzin	55	75	Sep 2008	Jun 2014	2024-03-01	9292
Renault	Thalia ii	1.6 16V	Stufenheck	Frontantrieb	Benzin	77	105	Sep 2008	Mar 2013	2025-12-01	9293
Opel	Corsa d	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	63	86	Jun 2010	Aug 2014	2024-03-01	9294
Opel	Insignia a	2.0 E85 Turbo	Schrägheck	Frontantrieb	Benzin/Ethanol	162	220	Oct 2010	Mar 2017	2024-03-01	9295
Opel	Insignia a sports tourer	2.0 E85 Turbo	Kombi	Frontantrieb	Benzin/Ethanol	162	220	Sep 2010	Nov 2011	2024-03-01	9296
Opel	Ampera	EV 150	Schrägheck	Frontantrieb	Benzin/Elektro	111	151	Nov 2011	Mar 2015	2024-03-01	9297
Fiat	Doblo	1.3 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Feb 2010	Dec 2023	2025-02-03	9298
Fiat	Uno	45 I.e. 1.0	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1984	Oct 1995	2024-03-01	9299
Fiat	Doblo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	77	105	Feb 2010	Dec 2023	2025-02-03	9300
Fiat	Doblo	2.0 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	99	135	Feb 2010	Dec 2023	2025-02-03	9301
Fiat	Doblo	1.4	Pritsche/Fahrgestell	Frontantrieb	Benzin	70	95	Apr 2010	Dec 2023	2025-02-03	9302
Alfa Romeo	Mito	1.3 Multijet	Schrägheck	Frontantrieb	Diesel	62	84	Jan 2011	Dec 2015	2024-03-01	9303
Audi	A1	1.4 Tfsi	Schrägheck	Frontantrieb	Benzin	136	185	Jan 2011	Apr 2015	2024-03-01	9304
Audi	A1	1.6 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Mar 2011	Apr 2015	2024-03-01	9305
Audi	A1	2.0 TDI	Schrägheck	Frontantrieb	Diesel	105	143	Sep 2011	Apr 2015	2024-03-01	9306
Audi	A5	RS5 Quattro	Coupe	Allrad	Benzin	331	450	Mar 2010	Jan 2017	2024-03-01	9307
Audi	A6 c7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Mar 2011	Sep 2018	2024-03-01	9308
Audi	A6 c7	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	132	180	May 2011	Sep 2018	2024-03-01	9309
Fiat	Idea	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	70	95	May 2008	Dec 2012	2024-03-01	9310
Fiat	Idea	1.6 D Multijet	Großraumlimousine	Frontantrieb	Diesel	88	120	May 2008	-	2024-03-01	9311
Land Rover	Discovery iv	3.0 4X4	Geländewagen geschlossen	Allrad	Benzin	250	340	Aug 2013	Dec 2018	2024-03-01	9312
Fiat	Idea	1.4 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	57	78	Mar 2009	-	2024-03-01	9313
Fiat	Ulysse	2.2 JTD	Großraumlimousine	Frontantrieb	Diesel	120	163	Mar 2008	Jun 2011	2024-03-01	9314
Fiat	Grande punto	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	85	116	Jun 2006	Dec 2009	2024-03-01	9315
Audi	A8 d4	6.3 W12 Quattro	Stufenheck	Allrad	Benzin	368	500	Jan 2011	Jan 2018	2024-03-01	9318
VW	Polo	1.9 SDI	Kombi	Frontantrieb	Diesel	47	64	Jun 1997	Sep 2001	2024-03-01	9319


--- Round 1 / 首次发送 ---
## 更新点

* 缓存优先完成 32 个既有尺寸组命中，并批量建立相关 Ktype 映射。
* 首次闭合 10 个尺寸组，覆盖 Fluence Z.E.、Zafira B VAN、Renault Wind、Yaris II、Peugeot 206+、Opel Ampera、Audi A1 8X 和 Fiat Idea。Fluence Z.E. 与 Wind 的来源分别明确列出车身宽度和含镜宽度，可确认本轮落盘宽度为不含后视镜口径。([汽车数据网][1])
* Yaris II、Peugeot 206+ 和 Ampera 的三维已闭合；206+ 与 Yaris II 均明确覆盖三门、五门车身，因此分别建立门数尺寸组。([汽车数据网][2])
* Audi A1 三个动力版本均确认采用改款前三门 8X1 外廓；Fiat Idea 三个动力版本复用同一五门 MPV 外廓。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：43
* READY 映射行：53
* PENDING Ktype：57
* 当前已引用尺寸组：42
* 本轮新建尺寸组：10
* 本轮命中既有尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9191	9191	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四门四驱版本共用该轿车外廓。	READY
9199	9199	Hatchback	Croma I	154		EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	1992年后改款外廓。	READY
9201	9201	Hatchback	3 Series E36 Compact	E36/5	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	316 G为E36 Compact三门车身。	READY
9218	9218	MPV	E-Series III	SR1		EU-MAZDA-E-SERIES-III-SR1-MPV-01	HIGH	E2000四驱客车外廓。	READY
9219	9219	Sedan	Lancer V		4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	四驱动力不改变四门轿车外廓。	READY
9225_prefl	9225	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	MEDIUM	生产区间跨越改款，拆分一期3.0 Caravan。	READY
9225_facelift	9225	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	MEDIUM	生产区间跨越改款，拆分二期Caravan。	READY
9231_3dr	9231	Hatchback	309 I		3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9231_5dr	9231	Hatchback	309 I		5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9233	9233	MPV	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	HIGH	一期四驱短轴低顶客车。	READY
9235	9235	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH	一期四驱短轴低顶厢式车。	READY
9245	9245	Sedan	Fluence Z.E.	L38	4	EU-RENAULT-FLUENCE-ZE-L38-SEDAN-01	HIGH	纯电四门轿车外廓。	READY
9251	9251	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9252	9252	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9253	9253	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9254	9254	Convertible	Wind	E33	2	EU-RENAULT-WIND-E33-CONVERTIBLE-2D-01	HIGH	双门敞篷车身。	READY
9255	9255	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	2011年改款后三门外廓。	READY
9256	9256	Hatchback	500 II	312	3	EU-FIAT-500-312-HATCHBACK-01	HIGH	LPG动力不改变三门车身外廓。	READY
9257_3dr	9257	Hatchback	Yaris II	XP90	3	EU-TOYOTA-YARIS-II-XP90-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9257_5dr	9257	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-XP90-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9258	9258	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH	843改款后三门外廓。	READY
9260	9260	MPV	Musa I		5	EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	HIGH	改款后五门MPV外廓。	READY
9262	9262	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	Bravo II五门车身。	READY
9263_3dr	9263	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9263_5dr	9263	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9264	9264	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	245PS版本对应改款前7P外廓。	READY
9265_3dr	9265	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留L08三门分支。	READY
9265_5dr	9265	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留L68五门分支。	READY
9274	9274	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power采用增高外廓。	READY
9279	9279	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH	四驱客车命中H100客运外廓。	READY
9281	9281	SUV	Land Cruiser 60	J60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	HIGH	4.0汽油五门J60外廓。	READY
9285_3dr	9285	Hatchback	206+		3	EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9285_5dr	9285	Hatchback	206+		5	EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9288	9288	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	R172双门硬顶敞篷外廓。	READY
9289	9289	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	R172双门硬顶敞篷外廓。	READY
9294	9294	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式认证沿用L08外廓。	READY
9297	9297	Hatchback	Ampera		5	EU-OPEL-AMPERA-HATCHBACK-5D-01	HIGH	五门增程式掀背车身。	READY
9299_3dr_prefl	9299	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	MEDIUM	生产区间跨改款，三门改款前标准外廓。	READY
9299_3dr_facelift	9299	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	MEDIUM	生产区间跨改款，三门1989改款外廓。	READY
9299_5dr_prefl	9299	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	MEDIUM	生产区间跨改款，五门改款前标准外廓。	READY
9299_5dr_facelift	9299	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	MEDIUM	生产区间跨改款，五门1989改款外廓。	READY
9304	9304	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9305	9305	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9306	9306	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9308	9308	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	该动力版本对应C7改款前四门轿车。	READY
9309	9309	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	该动力版本对应C7改款前四门轿车。	READY
9310	9310	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9311	9311	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9312	9312	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	HIGH	L319五门SUV外廓。	READY
9313	9313	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9315_3dr	9315	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9315_5dr	9315	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9319	9319	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-FLUENCE-ZE-L38-SEDAN-01	4748	1809	1458	Auto-Data Renault Fluence Z.E. 22 kWh (95 Hp)	https://www.auto-data.net/en/renault-fluence-z.e.-22-kwh-95hp-42342
EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	4467	1801	1645	Auto-Data Opel Zafira B 1.8i 16V (140 Hp)	https://www.auto-data.net/en/opel-zafira-b-1.8i-16v-140hp-2591
EU-RENAULT-WIND-E33-CONVERTIBLE-2D-01	3833	1689	1381	Auto-Data Renault Wind 1.2 TCe (101 Hp)	https://www.auto-data.net/en/renault-wind-1.2-tce-101hp-33940
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-3D-01	3785	1695	1530	Auto-Data Toyota Yaris II 1.33 VVT-i (101 Hp)	https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-5D-01	3785	1695	1530	Auto-Data Toyota Yaris II 1.33 VVT-i (101 Hp)	https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051
EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	3872	1655	1446	Auto-Data Peugeot 206+ 1.4i (75 Hp)	https://www.auto-data.net/en/peugeot-206-1.4i-75hp-34683
EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	3872	1655	1446	Auto-Data Peugeot 206+ 1.4i (75 Hp)	https://www.auto-data.net/en/peugeot-206-1.4i-75hp-34683
EU-OPEL-AMPERA-HATCHBACK-5D-01	4498	1787	1439	Auto-Data Opel Ampera 1.4 (150 Hp) Hybrid	https://www.auto-data.net/en/opel-ampera-1.4-150hp-hybrid-19559
EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	3954	1740	1416	Auto-Data Audi A1 (8X) 1.4 TFSI (185 Hp) S tronic	https://www.auto-data.net/en/audi-a1-8x-1.4-tfsi-185hp-s-tronic-18961
EU-FIAT-IDEA-350-MPV-5D-01	3930	1700	1660	Auto-Data Fiat Idea	https://www.auto-data.net/en/fiat-idea-generation-1603
```

## 下一步优先处理

1. 集中解决 Aerostar、Campo、Kangoo、C25、Hiace、Doblo底盘车等存在轴距、车顶、驾驶室或车长分支的车型。
2. 核对 Land Rover 90／110／127 与 Land Cruiser 80 的轴距、车身和动力高度边界。
3. 处理 Cutlass Supreme、Bentley Continental、Spyker、Audi RS5/A8、Insignia 等改款或低产车型。
4. 补齐 Astra H Caravan、Logan/Thalia、Fiat Ulysse II、Freemont及剩余单一尺寸车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-fluence-z.e.-22-kwh-95hp-42342 "https://www.auto-data.net/en/renault-fluence-z.e.-22-kwh-95hp-42342"
[2]: https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051 "https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051"
[3]: https://www.auto-data.net/en/audi-a1-8x-1.4-tfsi-185hp-s-tronic-18961 "Audi A1 (8X) 1.4 TFSI (185 Hp) S tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Fiat Doblò II 平台驾驶室与 Work Up 固定货斗的聚类：按改款前后、短轴/长轴拆分，共闭合 6 个尺寸组，并一次关联 4 个 Ktype。官方资料分别给出了 Work Up 与平台驾驶室各分支的完整外廓尺寸。([fiatcesaro.it][1])
* 完成 Fiat Freemont、Citroën DS3 Racing 和 Fiat Ulysse II 三个首次尺寸组。([Stellantis Media][2])
* Astra H Caravan/Kasten 按改款边界建立改款前尺寸组；改款后分支直接复用已有尺寸组。([汽车目录档案][3])
* Alfa Romeo MiTo 9303 按生产区间拆分为改款前和 2013 改款两个既有尺寸组，不新增重复尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：58
* READY 映射行：92
* PENDING Ktype：42
* 当前已引用尺寸组：55
* 本轮新增/修改映射行：39
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9230	9230	MPV	Freemont		5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH	五门MPV外廓。	READY
9243_prefl	9243	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9243_facelift	9243	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9244_prefl	9244	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9244_facelift	9244	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9246_prefl	9246	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9246_facelift	9246	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9247_prefl	9247	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9247_facelift	9247	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9248_prefl	9248	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9248_facelift	9248	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9249	9249	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	改款后五门Caravan/Kasten外廓。	READY
9250	9250	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	改款后五门Caravan/Kasten外廓。	READY
9284	9284	Hatchback	DS3		3	EU-CITROEN-DS3-RACING-HATCHBACK-3D-01	HIGH	Racing三门外廓。	READY
9298_workup_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9298_workup_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9298_chassis_swb_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9298_chassis_swb_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9298_chassis_lwb_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9298_chassis_lwb_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9300_workup_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9300_workup_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9300_chassis_swb_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9300_chassis_swb_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9300_chassis_lwb_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9300_chassis_lwb_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9301_workup_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9301_workup_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9301_chassis_swb_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9301_chassis_swb_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9301_chassis_lwb_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9301_chassis_lwb_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9302_chassis_swb_prefl	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9302_chassis_swb_facelift	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9302_chassis_lwb_prefl	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9302_chassis_lwb_facelift	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9303_prefl	9303	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	MEDIUM	生产区间跨越2013改款，改款前三门外廓。	READY
9303_facelift2013	9303	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	MEDIUM	生产区间跨越2013改款，2013改款三门外廓。	READY
9314	9314	MPV	Ulysse II		5	EU-FIAT-ULYSSE-II-MPV-5D-01	HIGH	第二代五门MPV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690	Fiat Freemont official press kit	https://www.media.stellantis.com/uploads/ch/CH/2011/FIAT/PRESS/20110620/Fiat_Freemont_FRA.pdf
EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	4515	1753	1500	Vauxhall Astra 2005 official brochure archive; Automobile-Catalog Opel Astra H Caravan 2005	https://autocatalogarchive.com/wp-content/uploads/2022/12/Vauxhall-Astra-2005-UK.pdf;https://www.automobile-catalog.com/make/opel/astra_h/astra_h_crv/2005.html
EU-CITROEN-DS3-RACING-HATCHBACK-3D-01	3962	1717	1443	Citroën DS3 Racing official technical specification	https://xr793.com/wp-content/uploads/2022/09/2012-Citroen-DS3-Racing-Black-Tech-Specs-UK.pdf
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049	Fiat Professional Doblò Work Up official brochure	https://www.fiatcesaro.it/editorcms/Doblo_WorkUp_Catalogo_ITA_2011.pdf
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	4211	1789	1845	Fiat Professional New Doblò Cargo Chassis Cab official technical specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	4227	1789	1845	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	4561	1789	1845	Fiat Professional New Doblò Cargo Chassis Cab official technical specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	4577	1789	1845	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-ULYSSE-II-MPV-5D-01	4719	1863	1752	Fiat New Ulysse official press kit	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-ulysse
```

## 下一步优先处理

1. 优先闭合 Kangoo I、C25、Hiace IV、Land Rover 90/110/127 等轴距、车顶或车身长度分支。
2. 批量处理 Aerostar、Campo、Mazda 323 III、Cutlass Supreme 等同车身多动力 Ktype。
3. 补齐 Logan/Thalia、Insignia、Bentley、Spyker及剩余 Audi 车型。

推进信号：CONTINUE

[1]: https://www.fiatcesaro.it/editorcms/Doblo_WorkUp_Catalogo_ITA_2011.pdf "https://www.fiatcesaro.it/editorcms/Doblo_WorkUp_Catalogo_ITA_2011.pdf"
[2]: https://www.media.stellantis.com/uploads/ch/CH/2011/FIAT/PRESS/20110620/Fiat_Freemont_FRA.pdf "https://www.media.stellantis.com/uploads/ch/CH/2011/FIAT/PRESS/20110620/Fiat_Freemont_FRA.pdf"
[3]: https://autocatalogarchive.com/wp-content/uploads/2022/12/Vauxhall-Astra-2005-UK.pdf "https://autocatalogarchive.com/wp-content/uploads/2022/12/Vauxhall-Astra-2005-UK.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Renault Logan／Logan MCV 聚类，按 2008 年改款前后拆分轿车与旅行车外廓，共闭合 4 个尺寸组。([汽车数据网][1])
* Renault Thalia II 的 4 个动力 Ktype 批量复用同一 L35 四门轿车尺寸组。([autokatalog.pl][2])
* 完成 Opel Insignia A 掀背、Sports Tourer，Audi RS5 8T Coupe 与 A8L D4 W12 的尺寸组闭合。([autodata1.com][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：68
* READY 映射行：104
* PENDING Ktype：32
* 当前已引用尺寸组：64
* 本轮新增/修改映射行：12
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9286_prefl	9286	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	MEDIUM	生产区间跨2008改款，改款前四门轿车外廓。	READY
9286_facelift	9286	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	MEDIUM	生产区间跨2008改款，改款后四门轿车外廓。	READY
9287_prefl	9287	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-WAGON-PREFL-01	MEDIUM	生产区间跨2008改款，改款前五门旅行车外廓。	READY
9287_facelift	9287	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-WAGON-FACELIFT-01	MEDIUM	生产区间跨2008改款，改款后五门旅行车外廓。	READY
9290	9290	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9291	9291	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9292	9292	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9293	9293	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9295	9295	Hatchback	Insignia A	G09	5	EU-OPEL-INSIGNIA-A-G09-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
9296	9296	Wagon	Insignia A Sports Tourer	G09	5	EU-OPEL-INSIGNIA-A-G09-WAGON-5D-PREFL-01	HIGH	改款前五门旅行车外廓。	READY
9307	9307	Coupe	RS5 8T	8T3	2	EU-AUDI-RS5-8T-COUPE-2D-01	HIGH	8T双门Coupe外廓。	READY
9318	9318	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-A8L-SEDAN-4D-PREFL-01	HIGH	W12版本对应长轴A8L外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.5 dCi (86 Hp)	https://www.auto-data.net/en/dacia-logan-i-1.5-dci-86hp-46154
EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	4290	1740	1534	Auto-Data Dacia Logan model overview	https://www.auto-data.net/en/dacia-logan-model-1791
EU-RENAULT-LOGAN-I-K90-WAGON-PREFL-01	4450	1740	1674	Auto-Data Dacia Logan I MCV 1.5 dCi (86 Hp) 7 Seats	https://www.auto-data.net/en/dacia-logan-i-mcv-1.5-dci-86hp-7-seats-17996
EU-RENAULT-LOGAN-I-K90-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.5 dCi (86 Hp)	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-86hp-46174
EU-RENAULT-THALIA-II-L35-SEDAN-01	4261	1639	1439	Autokatalog.pl Renault Thalia II	https://autokatalog.pl/renault/thalia/ii
EU-OPEL-INSIGNIA-A-G09-HATCHBACK-5D-PREFL-01	4830	1858	1498	Autodata1 Opel Insignia Hatchback 2.0 Turbo (220 Hp)	https://www.autodata1.com/en/car/opel/insignia/insignia-hatchback-20-turbo-220-hp
EU-OPEL-INSIGNIA-A-G09-WAGON-5D-PREFL-01	4908	1858	1520	Auto-Data Opel Insignia Sports Tourer 2.0 Turbo Ethanol	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-2.0-turbo-220hp-ethanol-26375
EU-AUDI-RS5-8T-COUPE-2D-01	4649	1860	1366	Automobile-Catalog Audi RS5 Coupe 2010	https://www.automobile-catalog.com/car/2010/1336520/audi_rs5_coupe.html
EU-AUDI-A8-D4-4H-A8L-SEDAN-4D-PREFL-01	5267	1949	1471	Auto-Data Audi A8L D4 6.3 FSI W12	https://www.auto-data.net/en/audi-a8l-d4-4h-6.3-fsi-w12-500hp-quattro-tiptronic-20343
```

## 下一步优先处理

1. 集中闭合 Aerostar、Campo、Kangoo I、C25、Land Rover 90/110/127 与 Hiace IV 的轴距、车顶和车身分支。
2. 批量处理 Gemini、Y10、Mazda 323 III 及 Cutlass Supreme 的同车身多动力映射。
3. 补齐 NSU Spider、Bentley Continental、Spyker C8/C12 与 Land Cruiser 80 等剩余车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/dacia-logan-i-1.5-dci-86hp-46154?utm_source=chatgpt.com "Specs of Dacia Logan I 1.5 dCi (86 Hp) /2007, 2008"
[2]: https://autokatalog.pl/renault/thalia/ii?utm_source=chatgpt.com "Renault Thalia II"
[3]: https://www.autodata1.com/en/car/opel/insignia/insignia-hatchback-20-turbo-220-hp?utm_source=chatgpt.com "Opel Insignia Hatchback 2.0 Turbo (220 Hp)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Gemini II 汽油轿车、NSU Wankel Spider，以及 Mazda 323 BF 前驱/四驱 Turbo 的物理外廓闭合；Y10 1.0 FIRE 4WD 直接复用既有第一系列四驱尺寸组。([汽车目录][1])
* 完成 Bentley Continental GT II W12、Spyker C12 Zagato、C8 Laviolette 与 C8 Aileron 的映射和首次建组。([汽车目录][2])
* Land Cruiser 80 4.0 汽油版确认与既有 4820×1900×1900 五门标准外廓一致，直接复用现有组。Spyker C8 Cabriolet 因可靠资料存在 4050 mm 与 4185 mm 两种车长，暂不强行落组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* READY 映射行：114
* PENDING Ktype：22
* 当前已引用尺寸组：74
* 本轮新增/修改映射行：10
* 本轮首次创建尺寸组：8
* 本轮复用既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9193	9193	Sedan	Gemini II	JT150	4	EU-ISUZU-GEMINI-II-JT150-SEDAN-PETROL-FACELIFT-01	HIGH	改款后JT150四门汽油轿车外廓。	READY
9198	9198	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	HIGH	第一系列三门四驱外廓。	READY
9208	9208	Convertible	Wankel Spider		2	EU-NSU-WANKEL-SPIDER-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
9212	9212	Hatchback	323 III BF	BF2	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-4WD-01	HIGH	BF2三门Turbo四驱外廓。	READY
9213	9213	Hatchback	323 III BF	BF1	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-FWD-01	HIGH	BF1三门Turbo前驱外廓。	READY
9261	9261	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-W12-COUPE-2D-01	HIGH	第二代W12双门Coupe外廓。	READY
9266	9266	Coupe	C12 Zagato		2	EU-SPYKER-C12-ZAGATO-COUPE-2D-01	HIGH	Zagato双门Coupe专属外廓。	READY
9267	9267	Coupe	C8 Laviolette		2	EU-SPYKER-C8-LAVIOLETTE-COUPE-2D-01	MEDIUM	固定顶Coupe对应Laviolette量产外廓。	READY
9269	9269	Coupe	C8 Aileron		2	EU-SPYKER-C8-AILERON-COUPE-2D-01	HIGH	第二代Aileron双门Coupe外廓。	READY
9282	9282	SUV	Land Cruiser 80	FJ80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH	汽油动力不改变五门标准外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-GEMINI-II-JT150-SEDAN-PETROL-FACELIFT-01	4070	1615	1370	Automobile-Catalog 1989 Isuzu Gemini 1.5 LJ Sedan catalyst	https://www.automobile-catalog.com/car/1989/1258985/isuzu_gemini_1_5_lj_sedan_cat.html
EU-NSU-WANKEL-SPIDER-CONVERTIBLE-2D-01	3580	1520	1260	Zwischengas NSU-Wankel Spider historical road test	https://www.zwischengas.com/en/articles/cars/NSU-Wankel-Spider-im-historischen-Fahrbericht.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-4WD-01	4000	1645	1355	Automobile-Catalog 1987 Mazda 323 4WD Turbo 16V GT	https://www.automobile-catalog.com/car/1987/58730/mazda_323_4wd_turbo_16v_gt.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-FWD-01	3990	1645	1390	Auto-Data Mazda 323 III BF 1.6 GT Turbo BF1; Automobile-Catalog 1985 Mazda 323 1.6i GTX	https://www.auto-data.net/en/mazda-323-iii-hatchback-bf-1.6-gt-turbo-bf1-140hp-11216;https://www.automobile-catalog.com/car/1985/51620/mazda_323_1_6i_gtx.html
EU-BENTLEY-CONTINENTAL-GT-II-W12-COUPE-2D-01	4806	1944	1404	Automobile-Catalog 2012 Bentley Continental GT 6.0 W12	https://www.automobile-catalog.com/car/2012/1373090/bentley_continental_gt.html
EU-SPYKER-C12-ZAGATO-COUPE-2D-01	4505	2031	1250	Automobile-Catalog 2007 Spyker C12 Zagato	https://www.automobile-catalog.com/car/2007/3156290/spyker_c12_zagato.html
EU-SPYKER-C8-LAVIOLETTE-COUPE-2D-01	4185	1880	1245	Automobile-Catalog Spyker C8 Laviolette	https://www.automobile-catalog.com/car/2004/3156200/spyker_c8_laviolette.html
EU-SPYKER-C8-AILERON-COUPE-2D-01	4620	1960	1270	Automobile-Catalog 2010 Spyker C8 Aileron Europe	https://www.automobile-catalog.com/car/2010/3156350/spyker_c8_aileron.html
```

## 下一步优先处理

1. 集中闭合 Kangoo I 与 C25 的厢式车、MPV、轴距及车顶分支。
2. 处理 Campo、Hiace IV 和 Land Rover 90／110／127 的驾驶室、轴距及车身长度边界。
3. 处理 Aerostar 与 Cutlass Supreme 的跨年份改款外廓，并解决 Spyker C8 Cabriolet 的车长冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/1258985/isuzu_gemini_1_5_lj_sedan_cat.html?utm_source=chatgpt.com "1989 Isuzu Gemini 1.5 LJ Sedan catalyst (man. 5)"
[2]: https://www.automobile-catalog.com/car/2012/1373090/bentley_continental_gt.html?utm_source=chatgpt.com "2012 Bentley Continental GT 6.0 Litre W12 (aut. 6)"
[3]: https://www.auto-data.net/en/toyota-land-cruiser-j80-4.0-155hp-4wd-3720?utm_source=chatgpt.com "Toyota Land Cruiser (J80) 4.0 (155 Hp) 4WD /SUV 1990"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 Ford Aerostar 两个动力版本：3.0 V6 对应标准车长后驱外廓，4.0 V6 4WD 对应 Long 四驱外廓。([汽车数据网][1])
* 完成 Oldsmobile Cutlass Supreme 三个 Coupe 动力版本；依据功率和实际供应年份分别关联 1988、1990 与 1993 对应外廓，不按输入中的宽泛结束年份猜测拆分。([汽车目录][2])
* 解决 Spyker C8 Cabriolet 车长冲突：输入的 298 kW／405 PS 早期版本确定为 C8 Spyder，采用 4050 mm 短轴外廓。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射行：120
* PENDING Ktype：16
* 当前已引用尺寸组：80
* 本轮新增/修改映射行：6
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9188	9188	MPV	Aerostar		4	EU-FORD-USA-AEROSTAR-MPV-4D-STD-01	HIGH	3.0 V6标准车长后驱外廓。	READY
9189	9189	MPV	Aerostar		4	EU-FORD-USA-AEROSTAR-MPV-4D-LONG-4WD-01	HIGH	4.0 V6 Long四驱外廓。	READY
9222	9222	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1988-01	HIGH	2.8 V6对应1988年双门外廓。	READY
9223	9223	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1990-01	HIGH	137 PS版本对应1990年双门外廓。	READY
9224	9224	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-FACELIFT-01	HIGH	203 PS版本对应1992年改款后双门外廓。	READY
9268	9268	Convertible	C8 Spyder		2	EU-SPYKER-C8-SPYDER-CONVERTIBLE-2D-01	HIGH	早期短轴C8 Spyder外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-AEROSTAR-MPV-4D-STD-01	4440	1820	1850	Auto-Data Ford Aerostar 3.0i V6 (147 Hp)	https://www.auto-data.net/en/ford-aerostar-3.0i-v6-147hp-7295
EU-FORD-USA-AEROSTAR-MPV-4D-LONG-4WD-01	4883	1821	1851	Auto-Data Ford Aerostar 4.0 V6 Long 4 WD XL (155 Hp)	https://www.auto-data.net/en/ford-aerostar-4.0-v6-long-4-wd-xl-155hp-7296
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1988-01	4879	1803	1341	Automobile-Catalog 1988 Oldsmobile Cutlass Supreme SL Coupe 2.8 V6	https://www.automobile-catalog.com/car/1988/2399420/oldsmobile_cutlass_supreme_sl_coupe_2_8_v6_5-speed.html
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1990-01	4884	1803	1354	Edmunds 1990 Oldsmobile Cutlass Supreme Coupe specifications	https://www.edmunds.com/oldsmobile/cutlass-supreme/1990/coupe/features-specs/
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-FACELIFT-01	4925	1803	1354	Automobile-Catalog 1993 Oldsmobile Cutlass Supreme S Coupe 3.4 Twin Dual Cam V6	https://www.automobile-catalog.com/car/1993/2403845/oldsmobile_cutlass_supreme_coupe_3_4_twin_dual_cam_v6.html
EU-SPYKER-C8-SPYDER-CONVERTIBLE-2D-01	4050	1880	1080	Auto-Data Spyker C8 Spyder 4.2 V8 40V (400 Hp)	https://www.auto-data.net/en/spyker-c8-spyder-4.2-v8-40v-400hp-15874
```

## 下一步优先处理

1. 闭合 Kangoo I 的改款前厢式车分支，并批量关联 9200、9202、9203、9204。
2. 处理 Hiace IV 两个 Kasten Ktype 的标准轴距、长轴与四驱边界。
3. 集中处理 C25 厢式车／底盘车、Campo Pickup 与 Land Rover 90／110／127。
4. 完成剩余 16 个 Ktype 后立即进行一次机械收尾并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-aerostar-3.0i-v6-147hp-7295 "Ford Aerostar 3.0i V6 (147 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1988/2399420/oldsmobile_cutlass_supreme_sl_coupe_2_8_v6_5-speed.html?utm_source=chatgpt.com "1988 Oldsmobile Cutlass Supreme SL Coupe 2.8 V6 5- ..."
[3]: https://www.auto-data.net/en/spyker-c8-spyder-generation-3524?utm_source=chatgpt.com "Spyker C8 Spyder | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Kangoo I 的 `Kasten/Großraumlimousine` 已按 KC 乘用版与 FC 厢式版拆分映射；KC 为 4 门、FC 为 3 门，两种车身外廓均为 3995×1663×1827 mm，因此统一复用既有尺寸组，不重复建组。([汽车数据网][1])
* Land Rover 110/127 的封闭式车身已限定为 One Ten County 五门 Station Wagon；标准 127 为 Crew Cab／高容量皮卡车身，不属于本批输入的封闭式 SUV 分支。3.5 V8 与 2.5 TD County 外廓相同，复用同一新尺寸组。([汽车目录][2])
* Land Rover 90 2.5 已闭合为 Ninety／LDV 两门短轴封闭式外廓。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：131
* PENDING Ktype：9
* 当前已引用尺寸组：83
* 本轮新增/修改映射行：11
* 本轮首次创建尺寸组：2
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9200_mpv	9200	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9200_van	9200	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9202_mpv	9202	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9202_van	9202	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9203_mpv	9203	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9203_van	9203	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9204_mpv	9204	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9204_van	9204	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9209	9209	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	MEDIUM	封闭式车身对应One Ten County；127标准分支为皮卡或底盘车。	READY
9210	9210	SUV	Land Rover Ninety	LDV	2	EU-LAND-ROVER-NINETY-LDV-SUV-2D-01	HIGH	LDV两门短轴封闭式外廓。	READY
9211	9211	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	MEDIUM	封闭式车身对应One Ten County；127标准分支为皮卡或底盘车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	4580	1790	1996	Automobile-Catalog 1986 Land-Rover 110 County V8; Automobile-Catalog 1987 Land-Rover 110 County 2.5 Turbo Diesel	https://www.automobile-catalog.com/car/1986/1394435/land-rover_110_county_v8.html;https://www.automobile-catalog.com/car/1987/1394420/land-rover_110_county_2_5_turbo_diesel.html
EU-LAND-ROVER-NINETY-LDV-SUV-2D-01	3722	1790	2000	Auto-Data Land Rover Defender 90 2.5 (83 Hp)	https://www.auto-data.net/en/land-rover-defender-90-2.5-83hp-5169
```

## 下一步优先处理

1. 闭合 Citroën C25 的厢式车与平台底盘轴距、车顶分支。
2. 处理 Isuzu Campo 的驾驶室、货斗长度及两驱／四驱外廓边界。
3. 闭合 Toyota Hiace IV 两个 Kasten Ktype 的车长、轴距及四驱分支。
4. 剩余 9 个 Ktype 全部 READY 后，下一轮直接进行机械收尾并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-kangoo-i-express-fc-1.2-58hp-10728 "Renault Kangoo I Express (FC) 1.2 (58 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1986/1394435/land-rover_110_county_v8.html?utm_source=chatgpt.com "1986 Land-Rover 110 County V8 Specs Review (98 kW / 133 PS / 131 hp) (since mid-year 1986 for Europe export)"
[3]: https://www.auto-data.net/en/land-rover-defender-90-2.5-83hp-5169 "Land Rover Defender 90 2.5 (83 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* Isuzu Campo 4 个 Ktype 已按底盘代码聚类为两种外廓：`KB28/KBD27` 为两驱长轴单排，`KB48/KBD47` 为四驱短轴单排。CarsGuide 的同代车型表分别给出两驱单排与四驱单排尺寸，Auto-Data 用于确认各 Ktype 对应的底盘代码。([CarsGuide][1])
* Toyota Hiace IV 两个 Kasten Ktype 已闭合：后驱低车身首次建组；四驱增高车身直接复用已有 H100 尺寸组，不重复输出尺寸事实。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射行：137
* PENDING Ktype：3
* 当前已引用尺寸组：86
* 本轮新增/修改映射行：6
* 本轮首次创建尺寸组：3
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9194	9194	Pickup	Campo KB	KB48	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	HIGH	KB48四驱短轴单排外廓。	READY
9195	9195	Pickup	Campo KB	KB28	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	HIGH	KB28两驱长轴单排外廓。	READY
9196	9196	Pickup	Campo KB	KBD27	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	HIGH	KBD27柴油两驱长轴单排外廓。	READY
9197	9197	Pickup	Campo KB	KBD47	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	HIGH	KBD47柴油四驱短轴单排外廓。	READY
9259	9259	Van	Hiace IV H100		4	EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	MEDIUM	后驱标准车长低车身厢式外廓。	READY
9280	9280	Van	Hiace IV H100		4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	四驱增高厢式外廓与既有H100四驱尺寸组一致。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	4425	1600	1592	CarsGuide 1985 Holden Rodeo single-cab 4x4 dimensions; Auto-Data Isuzu Campo KB48 and KBD47	https://www.carsguide.com.au/holden/rodeo/car-dimensions/1985;https://www.auto-data.net/en/isuzu-campo-2.0-4wd-kb48-79hp-15952;https://www.auto-data.net/en/isuzu-campo-2.5-d-4wd-kbd47-75hp-15956
EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	4860	1600	1550	CarsGuide 1985 Holden Rodeo single-cab 4x2 dimensions; Auto-Data Isuzu Campo KB28 and KBD27	https://www.carsguide.com.au/holden/rodeo/car-dimensions/1985;https://www.auto-data.net/en/isuzu-campo-2.0-kb28-79hp-15951;https://www.auto-data.net/en/isuzu-campo-2.5-d-kbd27-75hp-15955
EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	4615	1690	1935	Auto-Data Toyota HiAce IV H100 2.4i	https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186
```

## 下一步优先处理

1. 仅处理剩余 Citroën C25 Ktype `9205`、`9206`、`9207`。
2. 闭合厢式车的轴距／车顶分支以及平台驾驶室外廓。
3. 三个 Ktype 全部 READY 后立即执行一次机械检查，并输出两张最终完整 TSV、两个指定下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/holden/rodeo/car-dimensions/1985 "Holden Rodeo Dimensions 1985 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[2]: https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186 "Toyota HiAce IV (H100) 2.4 i (132 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8301-8400_ktype_dimension_mapping_final.tsv
- all_8301-8400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 剩余 Citroën C25 已按物理外廓闭合：厢式车拆分为 `L1H1`、`L1H2`、`L2H2`，平台驾驶室拆分为短轴和长轴，共新增 5 个([Transit Center Ford Transit Spare Parts][1])([transitcenter.uk][1])
* 当前批次所有 Ktype 均已完成映射。
* 已完成固定表头、主键唯一性、映射引用闭合、尺寸和来源完整性及文件名检查，机械校验通过。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：145
* PENDING 映射：0
* DIMENSION_GROUP：91
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合且无孤立尺寸组：通过
* 长宽高均为正整数，来源和 URL 非空：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9188	9188	MPV	Aerostar		4	EU-FORD-USA-AEROSTAR-MPV-4D-STD-01	HIGH	3.0 V6标准车长后驱外廓。	READY
9189	9189	MPV	Aerostar		4	EU-FORD-USA-AEROSTAR-MPV-4D-LONG-4WD-01	HIGH	4.0 V6 Long四驱外廓。	READY
9191	9191	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四门四驱版本共用该轿车外廓。	READY
9193	9193	Sedan	Gemini II	JT150	4	EU-ISUZU-GEMINI-II-JT150-SEDAN-PETROL-FACELIFT-01	HIGH	改款后JT150四门汽油轿车外廓。	READY
9194	9194	Pickup	Campo KB	KB48	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	HIGH	KB48四驱短轴单排外廓。	READY
9195	9195	Pickup	Campo KB	KB28	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	HIGH	KB28两驱长轴单排外廓。	READY
9196	9196	Pickup	Campo KB	KBD27	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	HIGH	KBD27柴油两驱长轴单排外廓。	READY
9197	9197	Pickup	Campo KB	KBD47	2	EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	HIGH	KBD47柴油四驱短轴单排外廓。	READY
9198	9198	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	HIGH	第一系列三门四驱外廓。	READY
9199	9199	Hatchback	Croma I	154		EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	1992年后改款外廓。	READY
9200_mpv	9200	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9200_van	9200	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9201	9201	Hatchback	3 Series E36 Compact	E36/5	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	316 G为E36 Compact三门车身。	READY
9202_mpv	9202	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9202_van	9202	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9203_mpv	9203	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9203_van	9203	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9204_mpv	9204	MPV	Kangoo I	KC	4	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	KC乘用版物理分支。	READY
9204_van	9204	Van	Kangoo I	FC	3	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH	FC厢式版物理分支。	READY
9205_l1h1	9205	Van	C25 Series 2	290	3	EU-CITROEN-C25-VAN-L1H1-01	HIGH	短轴低顶厢式车外廓。	READY
9205_l1h2	9205	Van	C25 Series 2	290	3	EU-CITROEN-C25-VAN-L1H2-01	HIGH	短轴高顶厢式车外廓。	READY
9205_l2h2	9205	Van	C25 Series 2	290	3	EU-CITROEN-C25-VAN-L2H2-01	HIGH	长轴高顶厢式车外廓。	READY
9206_l1h1	9206	Van	C25		3	EU-CITROEN-C25-VAN-L1H1-01	MEDIUM	生产区间覆盖Type 280/290；短轴低顶外廓尺寸不变。	READY
9206_l1h2	9206	Van	C25		3	EU-CITROEN-C25-VAN-L1H2-01	MEDIUM	生产区间覆盖Type 280/290；短轴高顶外廓尺寸不变。	READY
9206_l2h2	9206	Van	C25		3	EU-CITROEN-C25-VAN-L2H2-01	MEDIUM	生产区间覆盖Type 280/290；长轴高顶外廓尺寸不变。	READY
9207_swb	9207	Pickup	C25		2	EU-CITROEN-C25-CHASSIS-CAB-SWB-01	MEDIUM	平台驾驶室短轴物理分支。	READY
9207_lwb	9207	Pickup	C25		2	EU-CITROEN-C25-CHASSIS-CAB-LWB-01	MEDIUM	平台驾驶室长轴物理分支。	READY
9208	9208	Convertible	Wankel Spider		2	EU-NSU-WANKEL-SPIDER-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
9209	9209	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	MEDIUM	封闭式车身对应One Ten County；127标准分支为皮卡或底盘车。	READY
9210	9210	SUV	Land Rover Ninety	LDV	2	EU-LAND-ROVER-NINETY-LDV-SUV-2D-01	HIGH	LDV两门短轴封闭式外廓。	READY
9211	9211	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	MEDIUM	封闭式车身对应One Ten County；127标准分支为皮卡或底盘车。	READY
9212	9212	Hatchback	323 III BF	BF2	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-4WD-01	HIGH	BF2三门Turbo四驱外廓。	READY
9213	9213	Hatchback	323 III BF	BF1	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-FWD-01	HIGH	BF1三门Turbo前驱外廓。	READY
9218	9218	MPV	E-Series III	SR1		EU-MAZDA-E-SERIES-III-SR1-MPV-01	HIGH	E2000四驱客车外廓。	READY
9219	9219	Sedan	Lancer V		4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	四驱动力不改变四门轿车外廓。	READY
9222	9222	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1988-01	HIGH	2.8 V6对应1988年双门外廓。	READY
9223	9223	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1990-01	HIGH	137 PS版本对应1990年双门外廓。	READY
9224	9224	Coupe	Cutlass Supreme W-body		2	EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-FACELIFT-01	HIGH	203 PS版本对应1992年改款后双门外廓。	READY
9225_prefl	9225	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	MEDIUM	生产区间跨越改款，拆分一期3.0 Caravan。	READY
9225_facelift	9225	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	MEDIUM	生产区间跨越改款，拆分二期Caravan。	READY
9230	9230	MPV	Freemont		5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH	五门MPV外廓。	READY
9231_3dr	9231	Hatchback	309 I		3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9231_5dr	9231	Hatchback	309 I		5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9233	9233	MPV	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	HIGH	一期四驱短轴低顶客车。	READY
9235	9235	Van	Trafic I Phase 1			EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH	一期四驱短轴低顶厢式车。	READY
9243_prefl	9243	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9243_facelift	9243	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9244_prefl	9244	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9244_facelift	9244	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9245	9245	Sedan	Fluence Z.E.	L38	4	EU-RENAULT-FLUENCE-ZE-L38-SEDAN-01	HIGH	纯电四门轿车外廓。	READY
9246_prefl	9246	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9246_facelift	9246	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9247_prefl	9247	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9247_facelift	9247	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9248_prefl	9248	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	MEDIUM	生产区间跨改款，改款前五门Caravan/Kasten外廓。	READY
9248_facelift	9248	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	MEDIUM	生产区间跨改款，改款后五门Caravan/Kasten外廓。	READY
9249	9249	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	改款后五门Caravan/Kasten外廓。	READY
9250	9250	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	改款后五门Caravan/Kasten外廓。	READY
9251	9251	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9252	9252	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9253	9253	Van	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	HIGH	VAN认证版本沿用Zafira B五门外廓。	READY
9254	9254	Convertible	Wind	E33	2	EU-RENAULT-WIND-E33-CONVERTIBLE-2D-01	HIGH	双门敞篷车身。	READY
9255	9255	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	2011年改款后三门外廓。	READY
9256	9256	Hatchback	500 II	312	3	EU-FIAT-500-312-HATCHBACK-01	HIGH	LPG动力不改变三门车身外廓。	READY
9257_3dr	9257	Hatchback	Yaris II	XP90	3	EU-TOYOTA-YARIS-II-XP90-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9257_5dr	9257	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-XP90-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9258	9258	Hatchback	Ypsilon II	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH	843改款后三门外廓。	READY
9259	9259	Van	Hiace IV H100		4	EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	MEDIUM	后驱标准车长低车身厢式外廓。	READY
9260	9260	MPV	Musa I		5	EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	HIGH	改款后五门MPV外廓。	READY
9261	9261	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-W12-COUPE-2D-01	HIGH	第二代W12双门Coupe外廓。	READY
9262	9262	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	Bravo II五门车身。	READY
9263_3dr	9263	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9263_5dr	9263	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9264	9264	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	245PS版本对应改款前7P外廓。	READY
9265_3dr	9265	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留L08三门分支。	READY
9265_5dr	9265	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留L68五门分支。	READY
9266	9266	Coupe	C12 Zagato		2	EU-SPYKER-C12-ZAGATO-COUPE-2D-01	HIGH	Zagato双门Coupe专属外廓。	READY
9267	9267	Coupe	C8 Laviolette		2	EU-SPYKER-C8-LAVIOLETTE-COUPE-2D-01	MEDIUM	固定顶Coupe对应Laviolette量产外廓。	READY
9268	9268	Convertible	C8 Spyder		2	EU-SPYKER-C8-SPYDER-CONVERTIBLE-2D-01	HIGH	早期短轴C8 Spyder外廓。	READY
9269	9269	Coupe	C8 Aileron		2	EU-SPYKER-C8-AILERON-COUPE-2D-01	HIGH	第二代Aileron双门Coupe外廓。	READY
9274	9274	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power采用增高外廓。	READY
9279	9279	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	HIGH	四驱客车命中H100客运外廓。	READY
9280	9280	Van	Hiace IV H100		4	EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM	四驱增高厢式外廓与既有H100四驱尺寸组一致。	READY
9281	9281	SUV	Land Cruiser 60	J60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	HIGH	4.0汽油五门J60外廓。	READY
9282	9282	SUV	Land Cruiser 80	FJ80	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH	汽油动力不改变五门标准外廓。	READY
9284	9284	Hatchback	DS3		3	EU-CITROEN-DS3-RACING-HATCHBACK-3D-01	HIGH	Racing三门外廓。	READY
9285_3dr	9285	Hatchback	206+		3	EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9285_5dr	9285	Hatchback	206+		5	EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9286_prefl	9286	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	MEDIUM	生产区间跨2008改款，改款前四门轿车外廓。	READY
9286_facelift	9286	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	MEDIUM	生产区间跨2008改款，改款后四门轿车外廓。	READY
9287_prefl	9287	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-WAGON-PREFL-01	MEDIUM	生产区间跨2008改款，改款前五门旅行车外廓。	READY
9287_facelift	9287	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-WAGON-FACELIFT-01	MEDIUM	生产区间跨2008改款，改款后五门旅行车外廓。	READY
9288	9288	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	R172双门硬顶敞篷外廓。	READY
9289	9289	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	R172双门硬顶敞篷外廓。	READY
9290	9290	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9291	9291	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9292	9292	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9293	9293	Sedan	Thalia II	L35	4	EU-RENAULT-THALIA-II-L35-SEDAN-01	HIGH	L35四门轿车外廓。	READY
9294	9294	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式认证沿用L08外廓。	READY
9295	9295	Hatchback	Insignia A	G09	5	EU-OPEL-INSIGNIA-A-G09-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
9296	9296	Wagon	Insignia A Sports Tourer	G09	5	EU-OPEL-INSIGNIA-A-G09-WAGON-5D-PREFL-01	HIGH	改款前五门旅行车外廓。	READY
9297	9297	Hatchback	Ampera		5	EU-OPEL-AMPERA-HATCHBACK-5D-01	HIGH	五门增程式掀背车身。	READY
9298_workup_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9298_workup_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9298_chassis_swb_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9298_chassis_swb_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9298_chassis_lwb_prefl	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9298_chassis_lwb_facelift	9298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9299_3dr_prefl	9299	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	MEDIUM	生产区间跨改款，三门改款前标准外廓。	READY
9299_3dr_facelift	9299	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	MEDIUM	生产区间跨改款，三门1989改款外廓。	READY
9299_5dr_prefl	9299	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	MEDIUM	生产区间跨改款，五门改款前标准外廓。	READY
9299_5dr_facelift	9299	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	MEDIUM	生产区间跨改款，五门1989改款外廓。	READY
9300_workup_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9300_workup_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9300_chassis_swb_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9300_chassis_swb_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9300_chassis_lwb_prefl	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9300_chassis_lwb_facelift	9300	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9301_workup_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	MEDIUM	改款前Work Up固定货斗外廓。	READY
9301_workup_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	MEDIUM	改款后Work Up固定货斗外廓。	READY
9301_chassis_swb_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9301_chassis_swb_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9301_chassis_lwb_prefl	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9301_chassis_lwb_facelift	9301	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9302_chassis_swb_prefl	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	MEDIUM	改款前短轴平台驾驶室外廓。	READY
9302_chassis_swb_facelift	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	MEDIUM	改款后短轴平台驾驶室外廓。	READY
9302_chassis_lwb_prefl	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	MEDIUM	改款前长轴平台驾驶室外廓。	READY
9302_chassis_lwb_facelift	9302	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	MEDIUM	改款后长轴平台驾驶室外廓。	READY
9303_prefl	9303	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	MEDIUM	生产区间跨越2013改款，改款前三门外廓。	READY
9303_facelift2013	9303	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	MEDIUM	生产区间跨越2013改款，2013改款三门外廓。	READY
9304	9304	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9305	9305	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9306	9306	Hatchback	A1 8X	8X1	3	EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	HIGH	该动力版本对应改款前三门A1。	READY
9307	9307	Coupe	RS5 8T	8T3	2	EU-AUDI-RS5-8T-COUPE-2D-01	HIGH	8T双门Coupe外廓。	READY
9308	9308	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	该动力版本对应C7改款前四门轿车。	READY
9309	9309	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	HIGH	该动力版本对应C7改款前四门轿车。	READY
9310	9310	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9311	9311	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9312	9312	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	HIGH	L319五门SUV外廓。	READY
9313	9313	MPV	Idea	350	5	EU-FIAT-IDEA-350-MPV-5D-01	HIGH	动力差异不改变Idea五门外廓。	READY
9314	9314	MPV	Ulysse II		5	EU-FIAT-ULYSSE-II-MPV-5D-01	HIGH	第二代五门MPV外廓。	READY
9315_3dr	9315	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	输入未限定门数，保留三门物理分支。	READY
9315_5dr	9315	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	输入未限定门数，保留五门物理分支。	READY
9318	9318	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-A8L-SEDAN-4D-PREFL-01	HIGH	W12版本对应长轴A8L外廓。	READY
9319	9319	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8301-8400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-AEROSTAR-MPV-4D-STD-01	4440	1820	1850	Auto-Data Ford Aerostar 3.0i V6 (147 Hp)	https://www.auto-data.net/en/ford-aerostar-3.0i-v6-147hp-7295
EU-FORD-USA-AEROSTAR-MPV-4D-LONG-4WD-01	4883	1821	1851	Auto-Data Ford Aerostar 4.0 V6 Long 4 WD XL (155 Hp)	https://www.auto-data.net/en/ford-aerostar-4.0-v6-long-4-wd-xl-155hp-7296
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360	Auto-Data Honda Civic model specifications	https://www.auto-data.net/en/honda-civic-model-1307
EU-ISUZU-GEMINI-II-JT150-SEDAN-PETROL-FACELIFT-01	4070	1615	1370	Automobile-Catalog 1989 Isuzu Gemini 1.5 LJ Sedan catalyst	https://www.automobile-catalog.com/car/1989/1258985/isuzu_gemini_1_5_lj_sedan_cat.html
EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-SWB-4WD-01	4425	1600	1592	CarsGuide 1985 Holden Rodeo single-cab 4x4 dimensions; Auto-Data Isuzu Campo KB48 and KBD47	https://www.carsguide.com.au/holden/rodeo/car-dimensions/1985;https://www.auto-data.net/en/isuzu-campo-2.0-4wd-kb48-79hp-15952;https://www.auto-data.net/en/isuzu-campo-2.5-d-4wd-kbd47-75hp-15956
EU-ISUZU-CAMPO-KB-PICKUP-SINGLECAB-LWB-2WD-01	4860	1600	1550	CarsGuide 1985 Holden Rodeo single-cab 4x2 dimensions; Auto-Data Isuzu Campo KB28 and KBD27	https://www.carsguide.com.au/holden/rodeo/car-dimensions/1985;https://www.auto-data.net/en/isuzu-campo-2.0-kb28-79hp-15951;https://www.auto-data.net/en/isuzu-campo-2.5-d-kbd27-75hp-15955
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	3392	1537	1460	Automobile-Catalog 1987 Lancia Y10 4WD specifications	https://www.automobile-catalog.com/car/1987/1380740/lancia_y10_4wd.html
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433	Automobile-Catalog 1994 Fiat Croma specifications	https://www.automobile-catalog.com/car/1994/717860/fiat_croma_2_0_i_e__automatic.html
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827	Auto-Data Renault Kangoo I KC specifications	https://www.auto-data.net/en/renault-kangoo-i-kc-1.4i-75hp-automatic-33782
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390	Auto-Data BMW 3 Series Compact E36 specifications	https://www.auto-data.net/en/bmw-3-series-compact-e36-323ti-170hp-automatic-21171
EU-CITROEN-C25-VAN-L1H1-01	4759	1965	2108	Citroën C25 body-dimension reference; Fiat Ducato I shared-body specification	https://www.samochodyswiata.pl/viewtopic.php?f=21&t=36548;https://www.transitcenter.uk/fiat-ducato-1-data-specification.php
EU-CITROEN-C25-VAN-L1H2-01	4759	1965	2420	Citroën C25 body-dimension reference; Fiat Ducato I shared-body specification	https://www.samochodyswiata.pl/viewtopic.php?f=21&t=36548;https://www.transitcenter.uk/fiat-ducato-1-data-specification.php
EU-CITROEN-C25-VAN-L2H2-01	5489	1965	2420	Citroën C25 LWB high-roof shared-body specification	https://en.wheelsage.org/twins/group/120233/specifications
EU-CITROEN-C25-CHASSIS-CAB-SWB-01	4658	1965	2108	Auto Plus Citroën C25 chassis cab short-wheelbase specification	https://www.autoplus.fr/fiche-technique/citroen/c25-chassis-cab/citroen-c25-chassis-cab-c25-1400-tbo-d-656987
EU-CITROEN-C25-CHASSIS-CAB-LWB-01	5442	1965	2108	ParuVendu Citroën C25 1400 E LONG chassis-cab specification	https://www.paruvendu.fr/fiches-techniques-utilitaire/citroen-c25/1400-e-long-11-cv-essence/3056143/
EU-NSU-WANKEL-SPIDER-CONVERTIBLE-2D-01	3580	1520	1260	Zwischengas NSU-Wankel Spider historical road test	https://www.zwischengas.com/en/articles/cars/NSU-Wankel-Spider-im-historischen-Fahrbericht.html
EU-LAND-ROVER-ONE-TEN-LDH-SUV-5D-COUNTY-01	4580	1790	1996	Automobile-Catalog 1986 Land-Rover 110 County V8; Automobile-Catalog 1987 Land-Rover 110 County 2.5 Turbo Diesel	https://www.automobile-catalog.com/car/1986/1394435/land-rover_110_county_v8.html;https://www.automobile-catalog.com/car/1987/1394420/land-rover_110_county_2_5_turbo_diesel.html
EU-LAND-ROVER-NINETY-LDV-SUV-2D-01	3722	1790	2000	Auto-Data Land Rover Defender 90 2.5 (83 Hp)	https://www.auto-data.net/en/land-rover-defender-90-2.5-83hp-5169
EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-4WD-01	4000	1645	1355	Automobile-Catalog 1987 Mazda 323 4WD Turbo 16V GT	https://www.automobile-catalog.com/car/1987/58730/mazda_323_4wd_turbo_16v_gt.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-GT-TURBO-FWD-01	3990	1645	1390	Auto-Data Mazda 323 III BF 1.6 GT Turbo BF1; Automobile-Catalog 1985 Mazda 323 1.6i GTX	https://www.auto-data.net/en/mazda-323-iii-hatchback-bf-1.6-gt-turbo-bf1-140hp-11216;https://www.automobile-catalog.com/car/1985/51620/mazda_323_1_6i_gtx.html
EU-MAZDA-E-SERIES-III-SR1-MPV-01	4965	1690	1955	Truck1 Mazda E2000 Bus SR1 specifications	https://www.truck1.eu/blog/mazda-e2000-bus-sr1-2-0-82-hp-tech-specs-t28416
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data Mitsubishi Lancer V specifications	https://www.auto-data.net/en/mitsubishi-lancer-v-1.3-75hp-15664
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1988-01	4879	1803	1341	Automobile-Catalog 1988 Oldsmobile Cutlass Supreme SL Coupe 2.8 V6	https://www.automobile-catalog.com/car/1988/2399420/oldsmobile_cutlass_supreme_sl_coupe_2_8_v6_5-speed.html
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-1990-01	4884	1803	1354	Edmunds 1990 Oldsmobile Cutlass Supreme Coupe specifications	https://www.edmunds.com/oldsmobile/cutlass-supreme/1990/coupe/features-specs/
EU-OLDSMOBILE-CUTLASS-SUPREME-W-COUPE-2D-FACELIFT-01	4925	1803	1354	Automobile-Catalog 1993 Oldsmobile Cutlass Supreme S Coupe 3.4 Twin Dual Cam V6	https://www.automobile-catalog.com/car/1993/2403845/oldsmobile_cutlass_supreme_coupe_3_4_twin_dual_cam_v6.html
EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	4730	1772	1530	Swiss type-approval Opel Omega A 30i Caravan	https://www.dauto.ch/typenscheine/opel-omega-a-30i-cvan-1o5041-w0l000067l1-x
EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	4768	1760	1530	Automobile-Catalog 1992 Opel Omega Caravan specifications	https://www.automobile-catalog.com/car/1992/2469185/opel_omega_caravan_24v.html
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690	Fiat Freemont official press kit	https://www.media.stellantis.com/uploads/ch/CH/2011/FIAT/PRESS/20110620/Fiat_Freemont_FRA.pdf
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Automobile-Catalog 1989 Peugeot 309 specifications	https://www.automobile-catalog.com/car/1989/2579780/peugeot_309_look_1_3.html
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Automobile-Catalog 1989 Peugeot 309 specifications	https://www.automobile-catalog.com/car/1989/2579780/peugeot_309_look_1_3.html
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037	FastCarCheck Renault Trafic I 2.0 4WD specifications	https://fastcarcheck.uk/specs/make/renault/trafic/269730
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037	Drom Renault Trafic I L1H1 panel-van specifications	https://www.drom.ru/catalog/lcv/renault/trafic/272079/
EU-OPEL-ASTRA-H-CARAVAN-PREFL-01	4515	1753	1500	Vauxhall Astra 2005 official brochure archive; Automobile-Catalog Opel Astra H Caravan 2005	https://autocatalogarchive.com/wp-content/uploads/2022/12/Vauxhall-Astra-2005-UK.pdf;https://www.automobile-catalog.com/make/opel/astra_h/astra_h_crv/2005.html
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift specifications	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.7-cdti-ecoflex-110hp-16947
EU-RENAULT-FLUENCE-ZE-L38-SEDAN-01	4748	1809	1458	Auto-Data Renault Fluence Z.E. 22 kWh (95 Hp)	https://www.auto-data.net/en/renault-fluence-z.e.-22-kwh-95hp-42342
EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	4467	1801	1645	Auto-Data Opel Zafira B 1.8i 16V (140 Hp)	https://www.auto-data.net/en/opel-zafira-b-1.8i-16v-140hp-2591
EU-RENAULT-WIND-E33-CONVERTIBLE-2D-01	3833	1689	1381	Auto-Data Renault Wind 1.2 TCe (101 Hp)	https://www.auto-data.net/en/renault-wind-1.2-tce-101hp-33940
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	3687	1654	1470	Auto-Data Renault Twingo II facelift specifications	https://www.auto-data.net/en/renault-twingo-ii-facelift-2011-1.2-lev-16v-75hp-17447
EU-FIAT-500-312-HATCHBACK-01	3546	1627	1488	Auto-Data Fiat 500 312 specifications	https://www.auto-data.net/en/fiat-500-312-generation-3777
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-3D-01	3785	1695	1530	Auto-Data Toyota Yaris II 1.33 VVT-i (101 Hp)	https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051
EU-TOYOTA-YARIS-II-XP90-HATCHBACK-5D-01	3785	1695	1530	Auto-Data Toyota Yaris II 1.33 VVT-i (101 Hp)	https://www.auto-data.net/en/toyota-yaris-ii-1.33-vvt-i-101hp-4051
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Autodata1 Lancia Ypsilon 843 facelift specifications	https://www.autodata1.com/en/car/lancia/ypsilon/ypsilon-843-facelift-2006-14-8v-77-hp
EU-TOYOTA-HIACE-IV-H100-VAN-RWD-LOWROOF-01	4615	1690	1935	Auto-Data Toyota HiAce IV H100 2.4i	https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186
EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	4035	1698	1660	Auto-Data Lancia Musa facelift specifications	https://www.auto-data.net/en/lancia-musa-facelift-2007-1.4-77hp-30845
EU-BENTLEY-CONTINENTAL-GT-II-W12-COUPE-2D-01	4806	1944	1404	Automobile-Catalog 2012 Bentley Continental GT 6.0 W12	https://www.automobile-catalog.com/car/2012/1373090/bentley_continental_gt.html
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data Fiat Bravo II 198 specifications	https://www.auto-data.net/en/fiat-bravo-ii-198-1.4-90hp-7174
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Auto-Data Fiat Grande Punto 199 specifications	https://www.auto-data.net/en/fiat-grande-punto-199-generation-3779
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Auto-Data Fiat Grande Punto 199 specifications	https://www.auto-data.net/en/fiat-grande-punto-199-generation-3779
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	ADAC VW Touareg 2010-2018 vehicle data	https://assets.adac.de/Autodatenbank/GWInfo/gw0413-vw-touareg-2010-2018-diesel-bericht.pdf
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall Corsa D official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall Corsa D official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-SPYKER-C12-ZAGATO-COUPE-2D-01	4505	2031	1250	Automobile-Catalog 2007 Spyker C12 Zagato	https://www.automobile-catalog.com/car/2007/3156290/spyker_c12_zagato.html
EU-SPYKER-C8-LAVIOLETTE-COUPE-2D-01	4185	1880	1245	Automobile-Catalog Spyker C8 Laviolette	https://www.automobile-catalog.com/car/2004/3156200/spyker_c8_laviolette.html
EU-SPYKER-C8-SPYDER-CONVERTIBLE-2D-01	4050	1880	1080	Auto-Data Spyker C8 Spyder 4.2 V8 40V (400 Hp)	https://www.auto-data.net/en/spyker-c8-spyder-4.2-v8-40v-400hp-15874
EU-SPYKER-C8-AILERON-COUPE-2D-01	4620	1960	1270	Automobile-Catalog 2010 Spyker C8 Aileron Europe	https://www.automobile-catalog.com/car/2010/3156350/spyker_c8_aileron.html
EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	3538	1589	1614	Auto-Data Fiat Panda II Natural Power specifications	https://www.auto-data.net/en/fiat-panda-ii-169-1.4-8v-77-69hp-natural-power-54404
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980	Toyota 75 Years vehicle-lineage Hiace specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001935/index.html
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-PETROL-01	4750	1800	1815	Toyota 75 Years Land Cruiser 60 specifications	https://www.toyota.co.jp/jpn/company/history/75years/vehicle_lineage/car/id60013889/
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900	Auto-Data Toyota Land Cruiser J80 specifications	https://www.auto-data.net/en/toyota-land-cruiser-j80-4.0-155hp-4wd-3720
EU-CITROEN-DS3-RACING-HATCHBACK-3D-01	3962	1717	1443	Citroën DS3 Racing official technical specification	https://xr793.com/wp-content/uploads/2022/09/2012-Citroen-DS3-Racing-Black-Tech-Specs-UK.pdf
EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	3872	1655	1446	Auto-Data Peugeot 206+ 1.4i (75 Hp)	https://www.auto-data.net/en/peugeot-206-1.4i-75hp-34683
EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	3872	1655	1446	Auto-Data Peugeot 206+ 1.4i (75 Hp)	https://www.auto-data.net/en/peugeot-206-1.4i-75hp-34683
EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.5 dCi (86 Hp)	https://www.auto-data.net/en/dacia-logan-i-1.5-dci-86hp-46154
EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	4290	1740	1534	Auto-Data Dacia Logan model overview	https://www.auto-data.net/en/dacia-logan-model-1791
EU-RENAULT-LOGAN-I-K90-WAGON-PREFL-01	4450	1740	1674	Auto-Data Dacia Logan I MCV 1.5 dCi (86 Hp) 7 Seats	https://www.auto-data.net/en/dacia-logan-i-mcv-1.5-dci-86hp-7-seats-17996
EU-RENAULT-LOGAN-I-K90-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.5 dCi (86 Hp)	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-86hp-46174
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301	Autodata1 Mercedes-Benz SLK R172 specifications	https://www.autodata1.com/en/car/mercedes-benz/slk/slk-r172-slk-200-184-hp
EU-RENAULT-THALIA-II-L35-SEDAN-01	4261	1639	1439	Autokatalog.pl Renault Thalia II	https://autokatalog.pl/renault/thalia/ii
EU-OPEL-INSIGNIA-A-G09-HATCHBACK-5D-PREFL-01	4830	1858	1498	Autodata1 Opel Insignia Hatchback 2.0 Turbo (220 Hp)	https://www.autodata1.com/en/car/opel/insignia/insignia-hatchback-20-turbo-220-hp
EU-OPEL-INSIGNIA-A-G09-WAGON-5D-PREFL-01	4908	1858	1520	Auto-Data Opel Insignia Sports Tourer 2.0 Turbo Ethanol	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-2.0-turbo-220hp-ethanol-26375
EU-OPEL-AMPERA-HATCHBACK-5D-01	4498	1787	1439	Auto-Data Opel Ampera 1.4 (150 Hp) Hybrid	https://www.auto-data.net/en/opel-ampera-1.4-150hp-hybrid-19559
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049	Fiat Professional Doblò Work Up official brochure	https://www.fiatcesaro.it/editorcms/Doblo_WorkUp_Catalogo_ITA_2011.pdf
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	4211	1789	1845	Fiat Professional New Doblò Cargo Chassis Cab official technical specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	4227	1789	1845	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	4561	1789	1845	Fiat Professional New Doblò Cargo Chassis Cab official technical specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	4577	1789	1845	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	3644	1555	1425	Automobile-Catalog Fiat Uno Series I specifications	https://www.automobile-catalog.com/make/fiat/uno/uno_series_i/1988.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420	Automobile-Catalog 1989 Fiat Uno Series II specifications	https://www.automobile-catalog.com/car/1989/716135/fiat_uno_45_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	3644	1555	1425	Automobile-Catalog Fiat Uno Series I specifications	https://www.automobile-catalog.com/make/fiat/uno/uno_series_i/1988.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420	Automobile-Catalog 1989 Fiat Uno Series II specifications	https://www.automobile-catalog.com/car/1989/716135/fiat_uno_45_s.html
EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo specifications	https://www.auto-data.net/en/alfa-romeo-mito-generation-363
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2013 specifications	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2013-1.4-tp-170hp-tct-24669
EU-AUDI-A1-8X-HATCHBACK-3D-PREFL-01	3954	1740	1416	Auto-Data Audi A1 (8X) 1.4 TFSI (185 Hp) S tronic	https://www.auto-data.net/en/audi-a1-8x-1.4-tfsi-185hp-s-tronic-18961
EU-AUDI-RS5-8T-COUPE-2D-01	4649	1860	1366	Automobile-Catalog Audi RS5 Coupe 2010	https://www.automobile-catalog.com/car/2010/1336520/audi_rs5_coupe.html
EU-AUDI-A6-C7-4G2-SEDAN-PREFL-01	4915	1874	1455	Audi A6 Saloon official brochure	https://www.pac-solutions.co.uk/wp-content/uploads/2012/04/A6-SALOON-AVANT.pdf
EU-FIAT-IDEA-350-MPV-5D-01	3930	1700	1660	Auto-Data Fiat Idea	https://www.auto-data.net/en/fiat-idea-generation-1603
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	4829	1915	1887	Auto-Data Land Rover Discovery IV facelift specifications	https://www.auto-data.net/en/land-rover-discovery-iv-facelift-2013-3.0-v6-340hp-awd-automatic-23048
EU-FIAT-ULYSSE-II-MPV-5D-01	4719	1863	1752	Fiat New Ulysse official press kit	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-ulysse
EU-AUDI-A8-D4-4H-A8L-SEDAN-4D-PREFL-01	5267	1949	1471	Auto-Data Audi A8L D4 6.3 FSI W12	https://www.auto-data.net/en/audi-a8l-d4-4h-6.3-fsi-w12-500hp-quattro-tiptronic-20343
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433	Volkswagen Polo Variant brochure	https://www.autoweek.nl/autobrochures/download/1091/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8301-8400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.transitcenter.uk/fiat-ducato-1-data-specification.php?srsltid=AfmBOopMWkt5t9V-nuaCvoooeIfCdrtT0iQDoenNygBHZS_KpU-K4K4g "https://www.transitcenter.uk/fiat-ducato-1-data-specification.php?srsltid=AfmBOopMWkt5t9V-nuaCvoooeIfCdrtT0iQDoenNygBHZS_KpU-K4K4g"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8301-8400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8301-8400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10359 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3193 行）

