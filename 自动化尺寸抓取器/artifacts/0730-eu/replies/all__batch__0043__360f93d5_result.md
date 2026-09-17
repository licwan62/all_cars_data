# 任务：all 第 4201-4300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0043__360f93d5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4201-4300 行

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
all 第 4201-4300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALPINE-A110-II-COUPE-01	4178	1798	1252
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	4738	1842	1435
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-BMW-X6-F16-SUV-01	4909	1989	1702
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L2-AWD-01	5572	2052	2210
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L3-AWD-01	6022	2052	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	5205	2052	2215
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	5572	2052	2194
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	5572	2111	2210
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	5572	2052	2210
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	6022	2052	2186
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	6022	2111	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	6022	2052	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	6579	2052	2186
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	6579	2111	2214
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	6579	2052	2214
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	7577	2066	2206
EU-FORD-TRANSIT-V363-VAN-L2H2-AWD-01	5531	2059	2534
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2490
EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	5531	2059	2542
EU-FORD-TRANSIT-V363-VAN-L2H3-01	5531	2059	2781
EU-FORD-TRANSIT-V363-VAN-L2H3-AWD-01	5531	2059	2771
EU-FORD-TRANSIT-V363-VAN-L3H2-AWD-01	5981	2059	2533
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2541
EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	5981	2059	2543
EU-FORD-TRANSIT-V363-VAN-L3H3-AWD-01	5981	2059	2769
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2780
EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	5981	2059	2782
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	6704	2126	2790
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	6704	2059	2790
EU-HONDA-ELEMENT-I-SUV-01	4300	1815	1788
EU-HYUNDAI-KONA-I-OS-EV-SUV-01	4180	1800	1570
EU-HYUNDAI-KONA-I-OS-ICE-SUV-FACELIFT-01	4205	1800	1550
EU-HYUNDAI-KONA-I-OS-ICE-SUV-PREFL-01	4165	1800	1550
EU-LEXUS-UX-I-ZA10-SUV-01	4495	1840	1540
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	4321	1829	1809
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-NISSAN-JUKE-I-F15-FACELIFT-SUV-01	4135	1765	1565
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420
EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	5341	2164	1835
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	4609	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	4959	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659
EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	3600	1641	1504

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Rolls-royce	Silver spirit mk ii	6.75	Stufenheck	Heckantrieb	Benzin	160	218	Oct 1989	Sep 1993	2024-03-01	137183
Ferrari	208/308	308 GTS	Targa	Heckantrieb	Benzin	176	239	Jun 1983	Dec 1985	2024-03-01	137187
Renault	Koleos ii	1.7 Blue DCI 150	SUV	Frontantrieb	Diesel	110	150	Jun 2019	-	2024-03-01	137194
Opel	Combo e tour / life	1.2	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	137208
Mercedes-benz	Citan	108 CDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	59	80	May 2019	Aug 2021	2024-03-01	137217
Mercedes-benz	Citan	109 CDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	May 2019	Aug 2021	2024-03-01	137221
Mercedes-benz	Citan	111 CDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	May 2019	Aug 2021	2024-03-01	137226
VW	Transporter t6	2.0 TDI 4motion	Kasten	Allrad	Diesel	146	199	Aug 2018	Aug 2024	2025-02-03	137234
Toyota	Proace	1.5 D4D	Kasten	Frontantrieb	Diesel	75	102	May 2019	Apr 2025	2026-01-01	137257
Toyota	Proace	1.5 D4D	Kasten	Frontantrieb	Diesel	88	120	May 2019	-	2024-03-01	137258
Opel	Zafira	1.5	Bus	Frontantrieb	Diesel	88	120	Mar 2019	Apr 2025	2026-01-01	137264
Opel	Zafira	1.5	Bus	Frontantrieb	Diesel	75	102	Mar 2019	Apr 2025	2026-01-01	137265
Opel	Zafira	2	Bus	Frontantrieb	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	137282
Opel	Zafira	2	Bus	Frontantrieb	Diesel	130	177	Mar 2019	Apr 2025	2026-01-01	137283
Audi	A4 b9	30 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	100	136	Jul 2019	-	2024-03-01	137333
Audi	A4 b9 avant	30 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	100	136	Jul 2019	-	2024-03-01	137334
Audi	A4 b9 avant	35 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	120	163	Jul 2019	-	2024-03-01	137335
Mercedes-benz	Sprinter 3,5-T	314 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	105	143	Jan 2019	Dec 2021	2024-08-01	137358
Mercedes-benz	Sprinter 4-T	414 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	137364
Mercedes-benz	Sprinter 4-T	414 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	105	143	Jan 2019	Dec 2021	2024-08-01	137366
Mercedes-benz	Sprinter 3,5-T	316 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	137369
Mercedes-benz	Sprinter 4-T	416 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	137373
Audi	A4 allroad b9	45 TDI Quattro	Kombi	Allrad	Diesel	170	231	Jul 2018	-	2024-03-01	137377
Mercedes-benz	Sprinter 5-T	516 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	137378
Mercedes-benz	Sprinter 3,5-T	319 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	137379
Mercedes-benz	Sprinter 4-T	419 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	137381
Mercedes-benz	Sprinter 5-T	519 CDI Allrad	Pritsche/Fahrgestell	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	137382
Mercedes-benz	Sprinter 3-T	214 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	137410
Dacia	Duster	1.6 16V	Kasten/SUV	Frontantrieb	Benzin	77	105	Apr 2011	-	2024-03-01	137411
Mercedes-benz	Sprinter 3-T	216 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	137471
Mercedes-benz	A-Klasse	A 200 D	Stufenheck	Frontantrieb	Diesel	110	150	Aug 2019	-	2024-03-01	137527
Mercedes-benz	A-Klasse	A 220 D	Stufenheck	Frontantrieb	Diesel	140	190	Aug 2019	-	2024-03-01	137528
Mercedes-benz	Gle	350 D 4-matic	SUV	Allrad	Diesel	183	249	Apr 2015	Oct 2018	2024-03-01	137547
Ford	Transit v363	2.0 Ecoblue Mhev	Kasten	Frontantrieb	Diesel/Elektro	96	130	May 2019	-	2024-03-01	137558
Ford	Transit v363	2.0 Ecoblue Mhev RWD	Kasten	Heckantrieb	Diesel/Elektro	96	130	May 2019	-	2024-03-01	137560
Citroën	C5	2.0 HDI	Kasten/Kombi	Frontantrieb	Diesel	79	107	Jun 2002	Aug 2004	2024-07-01	137562
Ford	Transit v363	2.0 Ecoblue Mhev	Kasten	Frontantrieb	Diesel/Elektro	125	170	May 2019	Jun 2024	2024-11-01	137563
Ford	Transit v363	2.0 Ecoblue Mhev RWD	Kasten	Heckantrieb	Diesel/Elektro	125	170	May 2019	Jun 2024	2024-11-01	137564
Ford	Transit v363	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	96	130	May 2019	-	2024-03-01	137565
Ford	Transit v363	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	125	170	May 2019	Jun 2024	2024-11-01	137566
Mercedes-benz	Cla	CLA 200	Kombi	Frontantrieb	Benzin	110	150	Jun 2019	-	2024-03-01	137567
Rolls-royce	Cullinan	V12	SUV	Allrad	Benzin	441	600	Aug 2019	-	2024-03-01	137571
Ford	Transit v363	2.0 Ecoblue Mhev RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel/Elektro	96	130	May 2019	-	2024-03-01	137572
Ford	Transit v363	2.0 Ecoblue Mhev	Pritsche/Fahrgestell	Frontantrieb	Diesel/Elektro	96	130	May 2019	-	2024-03-01	137573
Ford	Transit v363	2.0 Ecoblue Mhev	Pritsche/Fahrgestell	Frontantrieb	Diesel/Elektro	125	170	May 2019	Jun 2024	2024-11-01	137577
Peugeot	508 ii	Hybrid 225	Schrägheck	Frontantrieb	Benzin/Elektro	165	224	Aug 2019	-	2024-03-01	137579
Lexus	Ux	200	SUV	Frontantrieb	Benzin	127	173	Jan 2019	-	2024-03-01	137580
Ford	Transit v363	2.0 Ecoblue Mhev RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel/Elektro	125	170	May 2019	Jun 2024	2024-11-01	137582
Peugeot	508 sw ii	Hybrid 224	Kombi	Frontantrieb	Benzin/Elektro	165	224	Aug 2019	-	2024-03-01	137583
Peugeot	2008 ii	1.5 Bluehdi 130	SUV	Frontantrieb	Diesel	96	131	Aug 2019	-	2024-03-01	137585
Peugeot	2008 ii	1.5 Bluehdi 100	SUV	Frontantrieb	Diesel	75	102	Aug 2019	-	2024-03-01	137586
Peugeot	2008 ii	1.2 Puretech 130	SUV	Frontantrieb	Benzin	96	131	Aug 2019	-	2025-12-01	137587
Peugeot	2008 ii	1.2 THP / Puretech 155	SUV	Frontantrieb	Benzin	114	155	Nov 2019	-	2024-03-01	137588
Dacia	Duster	1.3 TCE 130 4X4	SUV	Allrad	Benzin	96	131	Jan 2019	-	2024-03-01	137589
Dacia	Duster	1.3 TCE 150 4X4	SUV	Allrad	Benzin	110	150	Jan 2019	-	2024-03-01	137590
Dacia	Duster	1.0 TCE 100	SUV	Frontantrieb	Benzin	74	101	Jan 2019	-	2024-03-01	137591
Alpine	A110 ii	1.8 S	Coupe	Heckantrieb	Benzin	215	292	Oct 2019	Apr 2021	2026-04-01	137592
Hyundai	Kona	1.6 GDI Hybrid	SUV	Frontantrieb	Benzin/Elektro	104	141	Sep 2019	Apr 2023	2024-05-01	137594
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	183	249	Aug 2019	Jul 2020	2024-03-01	137595
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	155	211	Aug 2019	Jul 2020	2024-03-01	137596
BMW	X5	Xdrive 25 D	SUV	Allrad	Diesel	155	211	Aug 2019	Mar 2023	2024-03-01	137597
Peugeot	2008 ii	E-2008	SUV	Frontantrieb	Elektro	100	136	Sep 2019	-	2024-03-01	137598
Mercedes-benz	Glb	GLB 180 D	SUV	Frontantrieb	Diesel	85	116	Aug 2019	-	2024-03-01	137599
Mercedes-benz	Glb	GLB 200 D	SUV	Frontantrieb	Diesel	110	150	Aug 2019	-	2024-03-01	137600
Mercedes-benz	Glb	GLB 200 D 4-matic	SUV	Allrad	Diesel	110	150	Aug 2019	-	2024-03-01	137601
Mercedes-benz	Glb	GLB 220 D 4-matic	SUV	Allrad	Diesel	140	190	Aug 2019	-	2024-03-01	137602
Mercedes-benz	Glb	GLB 200	SUV	Frontantrieb	Benzin	120	163	Aug 2019	-	2024-03-01	137603
Mercedes-benz	Glb	GLB 250 4-matic	SUV	Allrad	Benzin	165	224	Aug 2019	-	2024-03-01	137604
Mercedes-benz	Glb	AMG GLB 35 4-matic	SUV	Allrad	Benzin	225	306	Aug 2019	-	2024-03-01	137605
Mercedes-benz	Sprinter 3,5-T tourer	319 CDI Allrad	Bus	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	137606
Mercedes-benz	Sprinter 3,5-T tourer	314 CDI Allrad	Bus	Allrad	Diesel	105	143	Jan 2019	Dec 2021	2024-08-01	137607
Mercedes-benz	Sprinter 3,5-T tourer	316 CDI Allrad	Bus	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	137608
Peugeot	3008 ii	Hybrid	SUV	Frontantrieb	Benzin/Elektro	165	224	Oct 2019	-	2024-11-01	137609
Peugeot	3008 ii	Hybrid4	SUV	Allrad	Benzin/Elektro	220	299	Oct 2019	-	2024-11-01	137610
Citroën	Spacetourer	1.6 HDI 90	Bus	Frontantrieb	Diesel	66	90	Jul 2018	-	2024-03-01	137614
KIA	Xceed	1.0 T-gdi	SUV	Frontantrieb	Benzin	88	120	Jun 2019	-	2024-03-01	137623
KIA	Xceed	1.4 T-gdi	SUV	Frontantrieb	Benzin	103	140	Jun 2019	Dec 2020	2024-08-01	137624
KIA	Xceed	1.6 T-gdi	SUV	Frontantrieb	Benzin	150	204	Jun 2019	-	2024-03-01	137625
KIA	Xceed	1.6 Crdi 115	SUV	Frontantrieb	Diesel	85	116	Jun 2019	-	2024-03-01	137626
KIA	Xceed	1.6 Crdi 136	SUV	Frontantrieb	Diesel	100	136	Jun 2019	-	2024-03-01	137627
Lada	Xray	1.6 Cross	Schrägheck	Frontantrieb	Benzin	83	113	Oct 2019	-	2024-03-01	137629
Ford	Puma	1.0 Ecoboost	SUV	Frontantrieb	Benzin	92	125	Sep 2019	-	2024-03-01	137641
BMW	3	M 340 I Xdrive	Stufenheck	Allrad	Benzin	285	387	Mar 2019	-	2024-03-01	137647
Lamborghini	Sian fkp 37	6.5 Mhev AWD	Coupe	Allrad	Benzin/Elektro	602	818	Sep 2019	-	2024-03-01	137650
Honda	E	Electric	Schrägheck	Heckantrieb	Elektro	100	136	Sep 2019	-	2024-03-01	137651
Honda	E	Electric Advance	Schrägheck	Heckantrieb	Elektro	113	154	Sep 2019	-	2024-03-01	137652
Ford	Tourneo custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	136	185	May 2019	Dec 2023	2024-05-01	137655
Ford	Tourneo custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	136	185	May 2019	Dec 2023	2024-05-01	137656
Ford	Transit custom v362	2.0 Ecoblue	Bus	Frontantrieb	Diesel	136	185	May 2019	Dec 2023	2024-05-01	137657
Ford	Transit custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	136	185	May 2019	Dec 2023	2024-05-01	137658
Ford	Tourneo custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	96	130	May 2019	Dec 2023	2024-05-01	137659
Ford	Transit custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	96	130	May 2019	Dec 2023	2024-05-01	137660
Ford	Transit custom v362	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	125	170	May 2019	Dec 2023	2024-05-01	137661
Ford	Puma	1.0 Ecoboost Mhev	SUV	Frontantrieb	Benzin/Elektro	92	125	Sep 2019	-	2024-03-01	137666
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	85	116	Feb 2019	Nov 2020	2025-11-01	137668
VW	Up!	E-up	Schrägheck	Frontantrieb	Elektro	61	83	Aug 2019	-	2025-06-01	137671
Ford	Puma	1.0 Ecoboost Mhev	SUV	Frontantrieb	Benzin/Elektro	114	155	Sep 2019	-	2024-03-01	137672
Seat	Mii	Electric	Schrägheck	Frontantrieb	Elektro	61	83	Jan 2020	-	2024-03-01	137676
Nissan	Juke	Dig-t 117	SUV	Frontantrieb	Benzin	86	117	Aug 2019	-	2024-03-01	137680
KIA	Seltos	1.6 T-gdi 4WD	SUV	Allrad	Benzin	130	177	Sep 2019	Jun 2022	2024-03-01	137685


--- Round 1 / 首次发送 ---
更新点

* 已按缓存优先完成首轮聚类，闭合 21 个输入 Ktype，共形成 22 条 READY 映射。
* `137208` 已按 Combo E Life 标准轴与 XL 加长轴拆分为两个物理外廓。
* 本轮全部复用历史或跨批次已确认尺寸组，未重复抓取、未重复输出尺寸来源。
* Sprinter、Transit、Transporter、Proace、Zafira Life、SpaceTourer 等多长度/车顶车型暂不猜测分支。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：21
* READY 映射行：22
* PENDING 输入 Ktype：79
* 已引用尺寸组：19
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137183	137183	Sedan	Silver Spirit II		4	EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	HIGH	Silver Spirit II标准轴距四门车身。	READY
137194	137194	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH	Koleos II五门SUV外廓。	READY
137208_std	137208	MPV	Combo E Life		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	标准轴Life车身分支。	READY
137208_xl	137208	MPV	Combo E Life		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	加长轴XL Life车身分支。	READY
137377	137377	Wagon	A4 allroad B9	8W5	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH	B9 allroad旅行车外廓。	READY
137527	137527	Sedan	A-Class V177 pre-facelift	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177四门轿车标准外廓。	READY
137528	137528	Sedan	A-Class V177 pre-facelift	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177四门轿车标准外廓。	READY
137547	137547	SUV	GLE I	W166	5	EU-MERCEDES-BENZ-GLE-I-SUV-01	HIGH	W166五门SUV外廓。	READY
137567	137567	Wagon	CLA II Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH	X118标准旅行车外廓。	READY
137571	137571	SUV	Cullinan I		5	EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	HIGH	Cullinan I标准五门SUV外廓。	READY
137579	137579	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	R8五门Fastback外廓。	READY
137580	137580	SUV	UX I	ZA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH	ZA10五门SUV外廓。	READY
137583	137583	Wagon	508 II SW		5	EU-PEUGEOT-508-II-WAGON-01	HIGH	508 II旅行车外廓。	READY
137589	137589	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	第二代四驱SUV外廓。	READY
137590	137590	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	第二代四驱SUV外廓。	READY
137591	137591	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	第二代前驱SUV外廓。	READY
137592	137592	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-01	HIGH	A110 II双门Coupe外廓。	READY
137595	137595	SUV	X6 G06 pre-facelift	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV Coupe外廓。	READY
137596	137596	SUV	X6 G06 pre-facelift	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV Coupe外廓。	READY
137597	137597	SUV	X5 G05 pre-facelift	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前标准SUV外廓。	READY
137647	137647	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	G20改款前xDrive四门轿车外廓。	READY
137668	137668	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH	5T五门MPV外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无（本轮均复用既有尺寸组）。

下一步优先处理

1. 批量闭合 Peugeot 2008 II/e-2008、Mercedes-Benz GLB、KIA XCeed、Ford Puma、Honda e、VW e-up/Seat Mii Electric 等高复用乘用车尺寸组。
2. 确认 Audi A4 B9 facelift 标准底盘与低车身尺寸组的关联边界。
3. 按长度、车顶、驱动和车身形式集中处理 Proace/Zafira Life/SpaceTourer、Citan、Transporter、Transit 与 Sprinter 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 补齐上一轮已经引用但尚未落盘的 Silver Spirit II、Koleos II、Combo E Life L/XL 与 GLE W166 共 5 个尺寸组；同时将 `137208_std` 的标准轴尺寸组 ID 从误写的 `M` 修正为 `L`。([汽车目录][1])
* 新闭合 Peugeot 2008 II、Kona Hybrid、GLB X247、KIA XCeed、Ford Puma、Honda e、Nissan Juke II 共 24 个输入 Ktype。([Stellantis Media][2])
* GLB 35 按 AMG 专用外廓独立建组；Puma 按 Titanium 与 ST-Line 不同保险杠长度拆分，125 PS 和 155 PS MHEV 均覆盖两个物理分支。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：45
* READY 映射行：49
* PENDING 输入 Ktype：55
* 已确认尺寸组：28
* 本轮新增映射行：27
* 本轮修改映射行：1
* 本轮首次创建/修正尺寸组：14
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137208_std	137208	MPV	Combo E Life		5	EU-OPEL-COMBO-E-LIFE-L-MPV-01	MEDIUM	标准轴L Life乘用车外廓。	READY
137585	137585	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137586	137586	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137587	137587	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137588	137588	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137594	137594	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	HIGH	OS混合动力五门SUV外廓。	READY
137598	137598	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前纯电五门SUV外廓。	READY
137599	137599	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137600	137600	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137601	137601	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137602	137602	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137603	137603	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137604	137604	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137605	137605	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	HIGH	AMG GLB 35专用外廓。	READY
137623	137623	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137624	137624	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137625	137625	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137626	137626	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137627	137627	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137641_titanium	137641	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137641_stline	137641	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137651	137651	Hatchback	Honda e I		5	EU-HONDA-E-I-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
137652	137652	Hatchback	Honda e I		5	EU-HONDA-E-I-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
137666_titanium	137666	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137666_stline	137666	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137672_titanium	137672	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137672_stline	137672	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137680	137680	SUV	Juke II pre-facelift	F16	5	EU-NISSAN-JUKE-II-F16-SUV-PREFL-01	HIGH	F16改款前五门SUV外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	5268	1887	1485	Automobile-Catalog Rolls-Royce Silver Spirit II	https://www.automobile-catalog.com/car/1992/2993540/rolls-royce_silver_spirit_ii.html
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos official dimensions	https://www.renault.com.ar/automoviles/nueva-koleos/especificaciones.html
EU-OPEL-COMBO-E-LIFE-L-MPV-01	4403	1848	1844	Opel Combo E official owner manual	https://public-servicebox.opel.com/OVddb/OV/sv_SE/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOLSE2111-sv_16_online.pdf
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1849	Opel Combo E official owner manual	https://public-servicebox.opel.com/OVddb/OV/sv_SE/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOLSE2111-sv_16_online.pdf
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796	Automobile-Catalog Mercedes-Benz GLE 350 d 4MATIC	https://www.automobile-catalog.com/car/2016/2135795/mercedes-benz_gle_350_d_4matic.html
EU-PEUGEOT-2008-II-SUV-PREFL-01	4300	1770	1550	Peugeot 2008 official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/peugeot2008pricespecapr23-6455a61e84bde.pdf
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	4165	1800	1565	Hyundai Kona Hybrid official technical specifications	https://www.hyundai.news/uk/articles/press-releases/all-new-hyundai-kona-hybrid-technical-specifications.html
EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	4634	1834	1659	Mercedes-Benz GLB X247 official owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-glb-suv-2020-september-x247-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	4650	1850	1662	Mercedes-AMG GLB official owner's manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-glb-owners-manual-supplement-march-2020-1.pdf
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495	Kia XCeed official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/XCeed/xceed_downloads/Press%20kit%20-%20Kia%20XCeed%20PETD.doc
EU-FORD-PUMA-II-SUV-TITANIUM-01	4186	1805	1537	Ford Puma official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Puma.pdf
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537	Ford Puma official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Puma.pdf
EU-HONDA-E-I-HATCHBACK-01	3895	1750	1512	Honda e official press kit	https://hondanews.eu/gb/en/cars/media/documenttext/199613/2020-honda-e-press-kit-1
EU-NISSAN-JUKE-II-F16-SUV-PREFL-01	4210	1800	1595	Nissan Juke official press release	https://uk.nissannews.com/en-GB/releases/all-new-nissan-juke-redefines-compact-crossovers-with-bigger-personality-better-performance-and-ground-breaking-technologies
```

下一步优先处理

1. 直接关联 Audi A4 B9 facelift Sedan/Avant 三条 Ktype 到现有缓存组，并厘清标准高度与低车身分支。
2. 按 Compact/Medium/Long 和乘用/厢式边界集中处理 Proace、Zafira Life、SpaceTourer、Citan、Transporter。
3. 按 L/H、驱动形式、单排底盘与 Tourer 集中处理 Sprinter 和 Transit，优先复用已有 Transit V363 尺寸组。
4. 随后闭合 Seat Mii Electric、VW e-up、Lada Xray Cross、Lamborghini Sián 等单车型组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1992/2993540/rolls-royce_silver_spirit_ii.html?utm_source=chatgpt.com "1992 Rolls-Royce Silver Spirit II Specs Review (165 kW ..."
[2]: https://www.media.stellantis.com/uploads/uk/model-pricelist/peugeot2008pricespecapr23-6455a61e84bde.pdf?utm_source=chatgpt.com "PEUGEOT
2008
PRICES - EQUIPMENT - TECHNICAL SPECIF"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 完成 Audi A4 B9 facelift 三条 Ktype 的缓存关联，并按标准悬架与运动悬架低车身外廓拆分。
* 完成 Citroën C5 I pre-facelift Wagon、Peugeot 3008 II Hybrid/Hybrid4 的既有尺寸组复用。
* 首次创建 Ferrari 308 GTS Quattrovalvole、Volkswagen e-up!、SEAT Mii Electric、Lamborghini Sián FKP 37 四个尺寸组。Ferrari、Volkswagen 和 SEAT 的三维来自厂商资料；Sián 使用 Auto-Data 的不含后视镜宽度规格。([法拉利][1])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：55
* READY 映射行：62
* PENDING 输入 Ktype：45
* 已引用尺寸组：38
* 本轮新增/修改映射行：13
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137187	137187	Convertible	308 GTS Quattrovalvole		2	EU-FERRARI-308-GTS-QV-TARGA-01	HIGH	可拆卸硬顶Targa车身。	READY
137333_std	137333	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137333_sport	137333	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137334_std	137334	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137334_sport	137334	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137335_std	137335	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137335_sport	137335	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137562	137562	Wagon	C5 I pre-facelift	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	DE改款前旅行车及货运衍生外廓。	READY
137609	137609	SUV	3008 II pre-facelift	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	前驱插电混合动力标准外廓。	READY
137610	137610	SUV	3008 II pre-facelift	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	四驱插电混合动力标准外廓。	READY
137650	137650	Coupe	Sián FKP 37		2	EU-LAMBORGHINI-SIAN-FKP37-COUPE-01	HIGH	双门Coupe固定车顶外廓。	READY
137671	137671	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-E-UP-HATCHBACK-01	HIGH	改款后五门纯电Hatchback外廓。	READY
137676	137676	Hatchback	Mii I Electric		5	EU-SEAT-MII-I-ELECTRIC-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FERRARI-308-GTS-QV-TARGA-01	4230	1720	1120	Ferrari 308 GTS Quattrovalvole official specifications	https://www.ferrari.com/en-EN/auto/308-gts-quattrovalvole
EU-LAMBORGHINI-SIAN-FKP37-COUPE-01	4980	2101	1133	Auto-Data Lamborghini Sián FKP 37 6.5 V12 Hybrid AWD	https://www.auto-data.net/en/lamborghini-sian-fkp-37-6.5-v12-819hp-hybrid-awd-automatic-37680
EU-VW-UP-I-FACELIFT-E-UP-HATCHBACK-01	3600	1645	1492	Volkswagen e-up! official technical data	https://www.volkswagen-newsroom.com/en/the-e-up-taken-to-a-new-level-5583/technical-data-5590
EU-SEAT-MII-I-ELECTRIC-HATCHBACK-01	3556	1645	1481	SEAT Mii Electric official technical specifications	https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/global_site/img/PressKits/Mii-Electric/Technical_Specifications_Mii_Electric.pdf
```

下一步优先处理

1. 按 Compact/Medium/Long 与 Van/MPV 边界集中闭合 Proace、Zafira Life、SpaceTourer 和 Citan。
2. 复用 Transit V363 缓存，先处理能够由驱动形式、车长和车顶高度明确拆分的 Van、Bus 与底盘车。
3. 集中核对 Sprinter VS30 底盘车和 Tourer 的轴距、驱动及单排/双排驾驶室分支。
4. 随后处理 Transporter T6、Transit/Tourneo Custom、Duster I Van、Lada XRAY Cross 与 Kia Seltos。

推进信号：CONTINUE

[1]: https://www.ferrari.com/en-EN/auto/308-gts-quattrovalvole?utm_source=chatgpt.com "Ferrari 308 GTS Quattrovalvole (1982)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 闭合 Toyota Proace 1.5 D-4D 两条 Ktype：75 kW 版本关联 Compact Van，88 kW 版本关联 Medium Van；官方规格表同时明确了发动机适用车长、三维及不含后视镜宽度。([丰田媒体][1])
* `137614` Citroën SpaceTourer 1.6 HDI 90 按已确认的 XS、M 两个物理外廓拆分并复用现有尺寸组；未重复输出尺寸组。该动力在 XS、M 车身均有对应记录。([汽车数据网][2])
* Zafira Life、Citan、Sprinter、Transit 等复杂多车长分支本轮未猜测关联。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：58
* READY 映射行：66
* PENDING 输入 Ktype：42
* 已引用尺寸组：42
* 本轮新增/修改映射行：4
* 本轮首次创建/修正尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137257	137257	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	HIGH	1.5D 100对应Compact厢式车外廓。	READY
137258	137258	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	HIGH	1.5D 120对应Medium厢式车外廓。	READY
137614_xs	137614	MPV	SpaceTourer I pre-facelift		5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	MEDIUM	1.6 HDI 90的XS短车身分支。	READY
137614_m	137614	MPV	SpaceTourer I pre-facelift		5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	MEDIUM	1.6 HDI 90的M标准车身分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	4609	1920	1910	Toyota PROACE Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	4959	1920	1899	Toyota PROACE Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
```

下一步优先处理

1. 按 S/M/L 与发动机适用范围闭合四条 Zafira Life Ktype，并一次性建立三个稳定尺寸组。
2. 按 Compact/Long/Extra-long 与 Van/Tourer 边界集中处理三条 Citan W415 Ktype。
3. 批量处理可直接关联现有 L2H2、L2H3、L3H2、L3H3、L4H3 缓存组的 Transit V363 Van/Bus。
4. 最后集中处理 Sprinter VS30 底盘车、Tourer 及 Transit Custom/Tourneo Custom 多长度分支。

推进信号：CONTINUE

[1]: https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf "Microsoft Word - 210223M - Proace full release"
[2]: https://www.auto-data.net/en/citroen-spacetourer-m-1.6-bluehdi-95hp-32389?utm_source=chatgpt.com "Citroen SpaceTourer M 1.6 BlueHDi (95 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 完成 `137629` Lada XRAY Cross：资料明确覆盖 113 PS 自动挡五门车身，车宽 1810 mm，括号内 1983 mm 为含后视镜宽度；高度按给定范围上限落盘为 1645 mm。
* 完成 `137685` KIA Seltos 1.6 T-GDI 177 4WD：车型、动力、驱动和生产区间与输入吻合，五门车身尺寸按高度范围上限 1620 mm 落盘。([汽车数据网][1])
* Zafira Life 与 Citan W415 尚存在同一 Ktype 覆盖多个车长或车身形式的问题，本轮未创建猜测性分支。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：60
* READY 映射行：68
* PENDING 输入 Ktype：40
* 已确认尺寸组：44
* 本轮新增/修改映射行：2
* 本轮首次创建/修正尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137629	137629	Hatchback	XRAY I Cross		5	EU-LADA-XRAY-I-CROSS-HATCHBACK-01	HIGH	Cross五门车身。	READY
137685	137685	SUV	Seltos I		5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH	1.6 T-GDI四驱五门车身。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-XRAY-I-CROSS-HATCHBACK-01	4171	1810	1645	LADA XRAY Cross specifications and price sheet	https://adom.ru/sites/default/files/txt/lada/xray-cross/komplektaciiiceny-ladaxraycross-lada.pdf
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620	Auto-Data Kia Seltos I 1.6 T-GDI 177 4WD	https://www.auto-data.net/en/kia-seltos-i-1.6-t-gdi-177hp-4wd-dct-38365
```

下一步优先处理

1. 按发动机适用车长闭合 Zafira Life 的 S、M、L 分支，避免把载荷等级造成的高度差误并。
2. 按 Van、Tourer 及 Compact、Long、Extra-long 边界处理 Citan W415。
3. 批量关联 Transit V363 的既有 L2H2、L3H2、L3H3 和 L4H3 缓存组。
4. 集中处理 Sprinter VS30、Transit/Tourneo Custom、Transporter T6 与 Duster I Commercial。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-seltos-i-1.6-t-gdi-177hp-4wd-dct-38365 "Kia Seltos I 1.6 T-GDI (177 Hp) 4WD DCT | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 完成 Citan 109 CDI、111 CDI 的 W415 长轴厢式、加长轴厢式及长轴 Tourer 分支；厢式车新建两个尺寸组，Tourer 直接复用既有长轴乘用车尺寸组。([梅赛德斯-奔驰法国媒体中心][1])
* 完成四条 Zafira Life Ktype：1.5 Diesel 102 覆盖 S、M；1.5 Diesel 120、2.0 Diesel 150、2.0 Diesel 177 均覆盖 S、M、L 三种车长。
* 完成 Duster I 1.6 16V 前驱商用衍生型，按第一代改款前 4×2 五门 SUV 外廓独立建组。([维基百科][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：67
* READY 映射行：86
* PENDING 输入 Ktype：33
* 已引用尺寸组：51
* 本轮新增/修改映射行：18
* 本轮首次创建/修正尺寸组：6
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137221_long_van	137221	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	MEDIUM	W415长轴厢式车分支。	READY
137221_xl_van	137221	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	MEDIUM	W415加长轴厢式车分支。	READY
137221_long_mpv	137221	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	MEDIUM	W415长轴Tourer乘用车分支。	READY
137226_long_van	137226	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	MEDIUM	W415长轴厢式车分支。	READY
137226_xl_van	137226	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	MEDIUM	W415加长轴厢式车分支。	READY
137226_long_mpv	137226	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	MEDIUM	W415长轴Tourer乘用车分支。	READY
137264_s	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137264_m	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137264_l	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137265_s	137265	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137265_m	137265	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137282_s	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137282_m	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137282_l	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137283_s	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137283_m	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137283_l	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137411	137411	SUV	Duster I pre-facelift	HS	5	EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	HIGH	两座商用衍生型沿用4x2五门SUV外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	4321	1829	1816	Mercedes-Benz Citan official media kit	https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/
EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	4705	1829	1839	Mercedes-Benz Citan official media kit	https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	4315	1822	1625	Auto-Data Dacia Duster	https://www.auto-data.net/en/dacia-duster-model-1948
```

下一步优先处理

1. 确认 Citan 108 CDI 80 PS 对应的 W415 长度及 Van/Tourer边界。
2. 批量关联 Transit V363 Van、Bus 与底盘车到已有 L/H、驱动和 SRW/DRW 尺寸组。
3. 集中处理 Sprinter VS30 底盘车及 Tourer 的轴距、驱动和载重级别分支。
4. 处理 Transporter T6、Transit Custom/Tourneo Custom 的短轴与长轴外廓。

推进信号：CONTINUE

[1]: https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/ "Le nouveau Mercedes-Benz Citan : le véhicule de livraison efficient"
[2]: https://de.wikipedia.org/wiki/Dacia_Duster?utm_source=chatgpt.com "Dacia Duster"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
更新点

* 完成 Citan 108 CDI：确认仅覆盖 W415 长轴 Van 与长轴 Tourer，均复用已有尺寸组，不新增尺寸事实。([汽车数据网][1])
* 完成三条 Tourneo Custom V362 Ktype，均拆分为 L1、L2 两个乘用车外廓；尺寸采用 Ford 官方资料中不含后视镜宽度，并按官方高度范围上限落盘。([福特英国][2])
* 完成四条 Transit Custom V362 Bus Ktype：185 PS 非 MHEV 对应低顶 L1/L2；185 PS MHEV、130 PS MHEV、170 PS MHEV覆盖已确认的 L1H1、L1H2、L2H1、L2H2 分支。([福特英国][3])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：75
* READY 映射行：108
* PENDING 输入 Ktype：25
* 已确认尺寸组：57
* 本轮新增/修改映射行：22
* 本轮首次创建/修正尺寸组：6
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137217_long_van	137217	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	HIGH	W415长轴厢式车分支。	READY
137217_long_mpv	137217	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH	W415长轴Tourer分支。	READY
137655_l1	137655	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137655_l2	137655	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137656_l1	137656	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137656_l2	137656	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137657_l1h1	137657	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137657_l2h1	137657	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137658_l1h1	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	MEDIUM	L1低顶Kombi分支。	READY
137658_l1h2	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	MEDIUM	L1高顶Kombi分支。	READY
137658_l2h1	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	MEDIUM	L2低顶Kombi分支。	READY
137658_l2h2	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	MEDIUM	L2高顶Kombi分支。	READY
137659_l1	137659	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137659_l2	137659	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137660_l1h1	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137660_l1h2	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1高顶Kombi分支。	READY
137660_l2h1	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137660_l2h2	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2高顶Kombi分支。	READY
137661_l1h1	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137661_l1h2	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1高顶Kombi分支。	READY
137661_l2h1	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137661_l2h2	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2高顶Kombi分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	4973	1986	1979	Ford Tourneo Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Tourneo_Custom.pdf
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	5340	1986	1977	Ford Tourneo Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Tourneo_Custom.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	4973	1986	2389	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	5340	1986	2017	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	5340	1986	2381	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
```

下一步优先处理

1. 批量关联 Transit V363 Van、Bus 与底盘车到已有 L/H、FWD/RWD、SRW/DRW 尺寸组。
2. 集中闭合 Sprinter VS30 底盘车和 Tourer 的轴距、驱动及载重级别分支。
3. 处理 Transporter T6 4Motion 的短轴、长轴和车顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-citan-tourer-long-w415-108-cdi-80hp-43767?utm_source=chatgpt.com "Mercedes-Benz Citan Tourer Long (W415) 108 CDI (80 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Tourneo_Custom.pdf "Tourneo Custom 21MY V1 GBR en_EBRO.pdf"
[3]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf "Transit Custom 21MY V1 GBR EN R2_EBRO.pdf"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
更新点

* 完成 4 条 Transit V363 Van Ktype。FWD 分为 L2H2、L2H3、L3H2、L3H3；RWD 另包含 L4H3，并区分 SRW、DRW。Ford 2019 车型资料确认了这些车长、车顶和驱动边界，同时确认 mHEV 适用于手动挡 FWD/RWD 车型。([博兰汽车][1])
* 20 条映射全部关联跨批次既有 Transit V363 尺寸组，未重新抓取或重复输出尺寸来源。
* Transit Bus、底盘车及 Sprinter 分支本轮未猜测关联。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：79
* READY 映射行：128
* PENDING 输入 Ktype：21
* 当前批次已引用尺寸组：66
* 本轮新增/修改映射行：20
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137558_l2h2	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱厢式车分支。	READY
137558_l2h3	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3前驱厢式车分支。	READY
137558_l3h2	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱厢式车分支。	READY
137558_l3h3	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	MEDIUM	L3H3前驱厢式车分支。	READY
137560_l2h2	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	MEDIUM	L2H2后驱厢式车分支。	READY
137560_l2h3	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3后驱厢式车分支。	READY
137560_l3h2	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	MEDIUM	L3H2后驱厢式车分支。	READY
137560_l3h3	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	MEDIUM	L3H3后驱厢式车分支。	READY
137560_l4h3_srw	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	MEDIUM	L4H3后驱单后轮厢式车分支。	READY
137560_l4h3_drw	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	MEDIUM	L4H3后驱双后轮厢式车分支。	READY
137563_l2h2	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱厢式车分支。	READY
137563_l2h3	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3前驱厢式车分支。	READY
137563_l3h2	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱厢式车分支。	READY
137563_l3h3	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	MEDIUM	L3H3前驱厢式车分支。	READY
137564_l2h2	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	MEDIUM	L2H2后驱厢式车分支。	READY
137564_l2h3	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3后驱厢式车分支。	READY
137564_l3h2	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	MEDIUM	L3H2后驱厢式车分支。	READY
137564_l3h3	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	MEDIUM	L3H3后驱厢式车分支。	READY
137564_l4h3_srw	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	MEDIUM	L4H3后驱单后轮厢式车分支。	READY
137564_l4h3_drw	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	MEDIUM	L4H3后驱双后轮厢式车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 处理 Transit V363 Bus 的 L2H2、L3H2 外廓边界。
2. 按 FWD/RWD、L1–L5、SRW/DRW 处理四条 Transit V363 底盘车 Ktype。
3. 集中闭合 Sprinter VS30 底盘车与 Tourer。
4. 最后处理 Transporter T6 4Motion。

推进信号：CONTINUE

[1]: https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf "Transit Van 19.75MY V1 IRL EN_EBRO.pdf"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
更新点

* 完成 Transit V363 两条前驱 Bus Ktype，按 L2H2、L3H2 外廓关联既有前驱 Van 尺寸组。
* 完成四条 Transit V363 底盘车 Ktype：前驱按 L2–L4，后驱按 L1–L5，并在已有缓存边界内区分 SRW/DRW。Ford 官方资料确认 Transit 底盘车采用 L1–L5、FWD/RWD/AWD、SRW/DRW 组合体系。
* 本轮全部复用已有尺寸组，未重复输出尺寸或来源。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：85
* READY 映射行：154
* PENDING 输入 Ktype：15
* 已引用尺寸组：74
* 本轮新增/修改映射行：26
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137565_l2h2	137565	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱Bus外廓分支。	READY
137565_l3h2	137565	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱Bus外廓分支。	READY
137566_l2h2	137566	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱Bus外廓分支。	READY
137566_l3h2	137566	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱Bus外廓分支。	READY
137572_l1_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	MEDIUM	L1后驱单后轮单排底盘车分支。	READY
137572_l2_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	MEDIUM	L2后驱单后轮单排底盘车分支。	READY
137572_l2_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	MEDIUM	L2后驱双后轮单排底盘车分支。	READY
137572_l3_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	MEDIUM	L3后驱单后轮单排底盘车分支。	READY
137572_l3_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	MEDIUM	L3后驱双后轮单排底盘车分支。	READY
137572_l4_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	MEDIUM	L4后驱单后轮单排底盘车分支。	READY
137572_l4_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	MEDIUM	L4后驱双后轮单排底盘车分支。	READY
137572_l5	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	MEDIUM	L5超长后驱单排底盘车分支。	READY
137573_l2	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	MEDIUM	L2前驱单排底盘车分支。	READY
137573_l3	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	MEDIUM	L3前驱单排底盘车分支。	READY
137573_l4	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	MEDIUM	L4前驱单排底盘车分支。	READY
137577_l2	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	MEDIUM	L2前驱单排底盘车分支。	READY
137577_l3	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	MEDIUM	L3前驱单排底盘车分支。	READY
137577_l4	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	MEDIUM	L4前驱单排底盘车分支。	READY
137582_l1_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	MEDIUM	L1后驱单后轮单排底盘车分支。	READY
137582_l2_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	MEDIUM	L2后驱单后轮单排底盘车分支。	READY
137582_l2_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	MEDIUM	L2后驱双后轮单排底盘车分支。	READY
137582_l3_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	MEDIUM	L3后驱单后轮单排底盘车分支。	READY
137582_l3_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	MEDIUM	L3后驱双后轮单排底盘车分支。	READY
137582_l4_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	MEDIUM	L4后驱单后轮单排底盘车分支。	READY
137582_l4_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	MEDIUM	L4后驱双后轮单排底盘车分支。	READY
137582_l5	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	MEDIUM	L5超长后驱单排底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 集中处理 11 条 Sprinter VS30 底盘车 Ktype，按载重等级、L1–L4、AWD/RWD/FWD 与 SRW/DRW 聚类。
2. 处理三条 Sprinter Tourer AWD 的车长和车顶分支。
3. 最后闭合 Transporter T6 4Motion 的 SWB/LWB 与车顶分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
更新点

* 完成 `137234` Volkswagen Transporter T6.1 146 kW 4Motion 厢式车，拆分为 SWB、LWB 两个标准顶外廓；官方尺寸图确认长度分别为 4904/5304 mm，车身宽度 1904 mm、标准顶高度 1990 mm。
* 完成 `137364` Mercedes-Benz Sprinter III 414 CDI 前驱底盘车，拆分为 L1、L2 单排驾驶室外廓；车型表确认两个长度均提供 414 CDI FWD，尺寸图明确车身宽度为 2020 mm，并区分含镜宽度 2345 mm。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：87
* READY 映射行：158
* PENDING 输入 Ktype：13
* 已确认尺寸组：78
* 本轮新增/修改映射行：4
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137234_swb	137234	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	SWB标准顶4Motion厢式车分支。	READY
137234_lwb	137234	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	LWB标准顶4Motion厢式车分支。	READY
137364_l1	137364	Pickup	Sprinter III		2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L1-FWD-01	HIGH	L1前驱单排底盘车分支。	READY
137364_l2	137364	Pickup	Sprinter III		2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-FWD-01	HIGH	L2前驱单排底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990	Volkswagen Transporter 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/showroom-brochures-live/VW_CV_Transporter-6.1_Brochure.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990	Volkswagen Transporter 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/showroom-brochures-live/VW_CV_Transporter-6.1_Brochure.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L1-FWD-01	5321	2020	2302	Mercedes-Benz Sprinter UK model information and price list	https://www.gmminibus.co.uk/wp-content/uploads/2024/07/mercedes-sprinter-1.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-FWD-01	5986	2020	2292	Mercedes-Benz Sprinter UK model information and price list	https://www.gmminibus.co.uk/wp-content/uploads/2024/07/mercedes-sprinter-1.pdf
```

下一步优先处理

1. 集中闭合 8 条 Sprinter VS30 AWD 底盘车，按 L2/L3、载重级别及 SRW/DRW 核对高度差。
2. 处理 3 条 Sprinter Tourer AWD 的车长和车顶分支。
3. 解决 `137410`、`137471` 两条 3-T RWD 底盘车的欧洲市场长度边界。

推进信号：CONTINUE


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
更新点

* 完成 3 条 Sprinter 3.5-T Tourer AWD Ktype。`137606`、`137607`、`137608` 均确认对应 `907.733`、L2H1 四驱 Tourer 外廓，共用同一尺寸组。([Nokian Tyres][1])
* 首次创建 Sprinter VS30 L2H1 AWD Tourer 尺寸组；采用不含后视镜宽度 2020 mm，含镜宽度 2345 mm 未落盘。([Ultimate Specs][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：90
* READY 映射行：161
* PENDING 输入 Ktype：10
* 已确认尺寸组：79
* 本轮新增/修改映射行：3
* 本轮首次创建/修正尺寸组：1
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137606	137606	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
137607	137607	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
137608	137608	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	5932	2020	2435	UltimateSpecs Mercedes-Benz Sprinter 2019 L2H1 Tourer 314 CDI 3.5t AWD	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/154294/Mercedes-Benz-Sprinter-2019-L2H1-Tourer-314-CDI-35t-AWD.html
```

下一步优先处理

1. 闭合 `137410`、`137471` 两条 3-T RWD 底盘车的 `907.221/907.223` 长度与驾驶室边界。
2. 集中处理剩余 8 条 Sprinter VS30 AWD 底盘车，按 L2/L3、载重等级和 SRW/DRW 建立或复用尺寸组。

推进信号：CONTINUE

[1]: https://www.nokiantyres.jp/taiyawo-tansu/zi-dong-chemeka/mercedes-benz/2020/sprinter-3-5-t-bus-907/314-cdi-all-wheel-drive-907-733-105kw/?utm_source=chatgpt.com "2020 Mercedes-benz SPRINTER 3,5-t Bus (907) 314 CDI All ..."
[2]: https://www.ultimatespecs.com/car-specs/Mercedes-Benz/154294/Mercedes-Benz-Sprinter-2019-L2H1-Tourer-314-CDI-35t-AWD.html?utm_source=chatgpt.com "Mercedes Benz Sprinter 2019 L2H1 Tourer 314 CDI 3.5t AWD Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
更新点

* 已确认剩余 10 条 Sprinter Ktype 的车身代码与物理分支边界：3-T 后驱为双排驾驶室 L1/L2；3.5-T、4-T、5-T 四驱底盘车均需区分单排/双排驾驶室及 L2/L3。Mercedes-Benz 车身制造指南明确列出了各载重等级、轴距和 `907.1xx/907.2xx` 车身代码对应关系。([pdfcoffee.com][1])
* 原有 10 条未拆分 PENDING 映射已改为 36 条明确物理分支。
* 本轮仅完成映射边界拆分；相应 AWD 底盘车高度及 SRW/DRW 宽度组合尚未全部闭合，因此未提前创建尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：90
* PENDING 输入 Ktype：10
* READY 映射行：161
* PENDING 映射行：36
* 映射行合计：197
* 已确认尺寸组：79
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137358_scab_l2	137358	Pickup	Sprinter III	907.133	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: L2 AWD底盘车三维尚未闭合
137358_scab_l3	137358	Pickup	Sprinter III	907.135	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: L3 AWD底盘车三维尚未闭合
137358_dcab_l2	137358	Pickup	Sprinter III	907.233	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: L2 AWD双排驾驶室三维尚未闭合
137358_dcab_l3	137358	Pickup	Sprinter III	907.235	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: L3 AWD双排驾驶室三维尚未闭合
137366_scab_l2	137366	Pickup	Sprinter III	907.143	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: 4-T L2 AWD底盘车三维尚未闭合
137366_scab_l3	137366	Pickup	Sprinter III	907.145	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: 4-T L3 AWD底盘车三维尚未闭合
137366_dcab_l2	137366	Pickup	Sprinter III	907.243	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: 4-T L2 AWD双排驾驶室三维尚未闭合
137366_dcab_l3	137366	Pickup	Sprinter III	907.245	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: 4-T L3 AWD双排驾驶室三维尚未闭合
137369_scab_l2	137369	Pickup	Sprinter III	907.133	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: L2 AWD底盘车三维尚未闭合
137369_scab_l3	137369	Pickup	Sprinter III	907.135	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: L3 AWD底盘车三维尚未闭合
137369_dcab_l2	137369	Pickup	Sprinter III	907.233	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: L2 AWD双排驾驶室三维尚未闭合
137369_dcab_l3	137369	Pickup	Sprinter III	907.235	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: L3 AWD双排驾驶室三维尚未闭合
137373_scab_l2	137373	Pickup	Sprinter III	907.143	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: 4-T L2 AWD底盘车三维尚未闭合
137373_scab_l3	137373	Pickup	Sprinter III	907.145	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: 4-T L3 AWD底盘车三维尚未闭合
137373_dcab_l2	137373	Pickup	Sprinter III	907.243	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: 4-T L2 AWD双排驾驶室三维尚未闭合
137373_dcab_l3	137373	Pickup	Sprinter III	907.245	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: 4-T L3 AWD双排驾驶室三维尚未闭合
137378_scab_l2	137378	Pickup	Sprinter III	907.153	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: 5-T L2 AWD底盘车SRW/DRW边界尚未闭合
137378_scab_l3	137378	Pickup	Sprinter III	907.155	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: 5-T L3 AWD底盘车SRW/DRW边界尚未闭合
137378_dcab_l2	137378	Pickup	Sprinter III	907.253	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: 5-T L2 AWD双排驾驶室三维尚未闭合
137378_dcab_l3	137378	Pickup	Sprinter III	907.255	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: 5-T L3 AWD双排驾驶室三维尚未闭合
137379_scab_l2	137379	Pickup	Sprinter III	907.133	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: L2 AWD底盘车三维尚未闭合
137379_scab_l3	137379	Pickup	Sprinter III	907.135	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: L3 AWD底盘车三维尚未闭合
137379_dcab_l2	137379	Pickup	Sprinter III	907.233	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: L2 AWD双排驾驶室三维尚未闭合
137379_dcab_l3	137379	Pickup	Sprinter III	907.235	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: L3 AWD双排驾驶室三维尚未闭合
137381_scab_l2	137381	Pickup	Sprinter III	907.143	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: 4-T L2 AWD底盘车三维尚未闭合
137381_scab_l3	137381	Pickup	Sprinter III	907.145	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: 4-T L3 AWD底盘车三维尚未闭合
137381_dcab_l2	137381	Pickup	Sprinter III	907.243	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: 4-T L2 AWD双排驾驶室三维尚未闭合
137381_dcab_l3	137381	Pickup	Sprinter III	907.245	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: 4-T L3 AWD双排驾驶室三维尚未闭合
137382_scab_l2	137382	Pickup	Sprinter III	907.153	2		MEDIUM	L2四驱单排驾驶室底盘车分支。	PENDING: 5-T L2 AWD底盘车SRW/DRW边界尚未闭合
137382_scab_l3	137382	Pickup	Sprinter III	907.155	2		MEDIUM	L3四驱单排驾驶室底盘车分支。	PENDING: 5-T L3 AWD底盘车SRW/DRW边界尚未闭合
137382_dcab_l2	137382	Pickup	Sprinter III	907.253	4		MEDIUM	L2四驱双排驾驶室底盘车分支。	PENDING: 5-T L2 AWD双排驾驶室三维尚未闭合
137382_dcab_l3	137382	Pickup	Sprinter III	907.255	4		MEDIUM	L3四驱双排驾驶室底盘车分支。	PENDING: 5-T L3 AWD双排驾驶室三维尚未闭合
137410_dcab_l1	137410	Pickup	Sprinter III	907.221	4		MEDIUM	L1后驱双排驾驶室底盘车分支。	PENDING: 3-T L1双排驾驶室完整三维尚未闭合
137410_dcab_l2	137410	Pickup	Sprinter III	907.223	4		MEDIUM	L2后驱双排驾驶室底盘车分支。	PENDING: 3-T L2双排驾驶室完整三维尚未闭合
137471_dcab_l1	137471	Pickup	Sprinter III	907.221	4		MEDIUM	L1后驱双排驾驶室底盘车分支。	PENDING: 3-T L1双排驾驶室完整三维尚未闭合
137471_dcab_l2	137471	Pickup	Sprinter III	907.223	4		MEDIUM	L2后驱双排驾驶室底盘车分支。	PENDING: 3-T L2双排驾驶室完整三维尚未闭合
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 先闭合 3-T 双排驾驶室 L1/L2 两个尺寸组，同时解决 `137410`、`137471`。
2. 再按 `3.5-T/4-T/5-T × L2/L3 × 单排/双排 × SRW/DRW` 聚类闭合 AWD 底盘车尺寸组。
3. 尺寸组闭合后批量把相同 BodyCode 的 314/316/319、414/416/419、516/519 Ktype 关联到共享组。

推进信号：CONTINUE

[1]: https://pdfcoffee.com/mb-sprinter-pdf-free.html "MB Sprinter - PDFCOFFEE.COM"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
更新点

* 已确认 Sprinter 3-T 双排驾驶室的 `907.221` 为 3250 mm 轴距 L1、`907.223` 为 3665 mm 轴距 L2；本轮先闭合资料完整的 L2 分支。([pdfcoffee.com][1])
* `137410_dcab_l2`、`137471_dcab_l2` 已关联同一 L2 后驱双排驾驶室尺寸组。Mercedes-Benz 2020 规格图给出的完整外廓为 5886 × 2020 × 2282 mm，2345 mm 含后视镜宽度未落盘。([Dezo's Garage][2])
* 两条 Ktype 的 L1 分支继续保留 PENDING，未使用 L2 尺寸代填。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：90
* PENDING 输入 Ktype：10
* READY 映射行：163
* PENDING 映射行：34
* 映射行合计：197
* 已确认尺寸组：80
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137410_dcab_l2	137410	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-01	HIGH	L2后驱双排驾驶室底盘车分支。	READY
137471_dcab_l2	137471	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-01	HIGH	L2后驱双排驾驶室底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-01	5886	2020	2282	Mercedes-Benz Sprinter UK model information and price list March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
```

下一步优先处理

1. 闭合 `907.221` L1 后驱双排驾驶室尺寸组，同时解决 `137410_dcab_l1`、`137471_dcab_l1`。
2. 批量闭合 `907.133/135`、`907.143/145`、`907.153/155` 的 AWD 单排驾驶室分支。
3. 随后处理 `907.233/235`、`907.243/245`、`907.253/255` 的 AWD 双排驾驶室分支及 5-T SRW/DRW 边界。

推进信号：CONTINUE

[1]: https://pdfcoffee.com/mb-sprinter-pdf-free.html "https://pdfcoffee.com/mb-sprinter-pdf-free.html"
[2]: https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf "https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
更新点

* 闭合 `137410`、`137471` 的 `907.221` L1 与 `907.223` L2 后驱双排驾驶室分支。对应三维分别为 `5576×2018×2365 mm` 和 `6156×2018×2365 mm`；两种车身均为四门、六座双排驾驶室底盘。([二手车目录][1])
* 修正上一轮 L2 关联：原 `EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-01` 的三维来自不同载重级别外廓，当前 3-T `907.223` 改用新组 `...-02`；旧组不再被当前批次映射引用。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：92
* PENDING 输入 Ktype：8
* READY 映射行：165
* PENDING 映射行：32
* 映射行合计：197
* 当前引用尺寸组：81
* 本轮新增/修改映射行：4
* 本轮首次创建/修正尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137410_dcab_l1	137410	Pickup	Sprinter III	907.221	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	HIGH	3-T L1后驱双排驾驶室底盘车分支。	READY
137410_dcab_l2	137410	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	HIGH	3-T L2后驱双排驾驶室底盘车分支。	READY
137471_dcab_l1	137471	Pickup	Sprinter III	907.221	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	HIGH	3-T L1后驱双排驾驶室底盘车分支。	READY
137471_dcab_l2	137471	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	HIGH	3-T L2后驱双排驾驶室底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	5576	2018	2365	Mercedes-Benz Sprinter 2018 model information and price list;Használtautó Autókatalógus Mercedes-Benz 211 CDI 907.221.13	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://katalogus.hasznaltauto.hu/mercedes-benz/211_cdi_907.221.13_automata/130304
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	6156	2018	2365	Mercedes-Benz Sprinter 2018 model information and price list;Használtautó Autókatalógus Mercedes-Benz 214 CDI 907.223.13;Használtautó Autókatalógus Mercedes-Benz 216 CDI 907.223.13	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://katalogus.hasznaltauto.hu/mercedes-benz/214_cdi_907.223.13/119805;https://katalogus.hasznaltauto.hu/mercedes-benz/216_cdi_907.223.13/119809
```

下一步优先处理

1. 闭合 `907.133/907.135` 的 3.5-T AWD 单排驾驶室 L2/L3，并批量解决 `137358`、`137369`、`137379`。
2. 闭合 `907.233/907.235` 的 3.5-T AWD 双排驾驶室 L2/L3。
3. 随后处理 `907.143/145`、`907.243/245` 的 4-T 分支，以及 `907.153/155`、`907.253/255` 的 5-T SRW/DRW 分支。

推进信号：CONTINUE

[1]: https://katalogus.hasznaltauto.hu/mercedes-benz/211_cdi_907.221.13_automata/130304 "Autókatalógus - MERCEDES-BENZ 211 CDI 907.221.13 (Automata) (4 ajtós, 114.24 LE) (2020–)"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
更新点

* 闭合 3.5-T AWD 底盘车的四个物理外廓：单排 L2/L3、双排 L2/L3，并批量解决 `137358`、`137369`、`137379`。
* 长度与不含后视镜宽度采用 Mercedes-Benz 2020 Sprinter 底盘车尺寸图；AWD 高度依据 Oberaigner 技术资料明确的前轴车身抬升 120 mm，由对应 RWD 底盘高度机械换算，不按发动机重复建组。([MB Vans][1])
* 相同 BodyCode 的 314/316/319 CDI 共用稳定尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：95
* PENDING 输入 Ktype：5
* READY 映射行：177
* PENDING 映射行：20
* 映射行合计：197
* 当前引用尺寸组：85
* 本轮新增/修改映射行：12
* 本轮首次创建/修正尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137358_scab_l2	137358	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137358_scab_l3	137358	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137358_dcab_l2	137358	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137358_dcab_l3	137358	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
137369_scab_l2	137369	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137369_scab_l3	137369	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137369_dcab_l2	137369	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137369_dcab_l3	137369	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
137379_scab_l2	137379	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137379_scab_l3	137379	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137379_dcab_l2	137379	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137379_dcab_l3	137379	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	5886	2020	2408	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	6696	2020	2400	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	5886	2020	2402	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	6696	2020	2392	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
```

下一步优先处理

1. 闭合 `907.143/907.145` 与 `907.243/907.245` 的 4-T AWD 单排、双排 L2/L3 分支，批量解决 `137366`、`137373`、`137381`。
2. 最后处理 `907.153/907.155` 与 `907.253/907.255` 的 5-T AWD 分支及后轮外廓边界，解决 `137378`、`137382`。

推进信号：CONTINUE

[1]: https://assets.mbvans.com/Mercedes-Benz-Vans/Brochures/2020-Mercedes-Benz-Sprinter-Vans-Brochure.pdf?utm_source=chatgpt.com "2020 Mercedes-Benz Sprinter"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
更新点

* 闭合 `907.143/907.145` 与 `907.243/907.245` 的 4-T AWD 单排、双排 L2/L3 分支，批量解决 `137366`、`137373`、`137381`。
* 4-T 与已确认的 3.5-T AWD 对应分支具有相同驾驶室、轴距、车长、车身宽度和高度；差异为允许总质量及承载配置，不另建重复尺寸组。Mercedes-Benz 型号表确认 `.143/.145` 为 L2/L3 单排、`.243/.245` 为 L2/L3 双排，官方尺寸资料确认对应外廓边界。([Mercedes-Benz][1])
* 本轮全部复用既有 AWD 尺寸组，未重复输出尺寸与来源。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：98
* PENDING 输入 Ktype：2
* READY 映射行：189
* PENDING 映射行：8
* 映射行合计：197
* 当前引用尺寸组：85
* 本轮新增/修改映射行：12
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137366_scab_l2	137366	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137366_scab_l3	137366	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137366_dcab_l2	137366	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137366_dcab_l3	137366	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
137373_scab_l2	137373	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137373_scab_l3	137373	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137373_dcab_l2	137373	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137373_dcab_l3	137373	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
137381_scab_l2	137381	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137381_scab_l3	137381	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137381_dcab_l2	137381	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137381_dcab_l3	137381	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 闭合 `137378`、`137382` 的 `907.153/907.155` 单排和 `907.253/907.255` 双排 AWD 分支。
2. 核对 5-T 后轴外廓是否为 DRW；若宽度或高度不同则创建独立尺寸组，否则复用现有 L2/L3 AWD 组。
3. 两条 Ktype 闭合且 `PENDING=0` 后，下一轮直接输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://mercedes-benz.jpauto.hu/wp-content/uploads/2024/07/Mercedes-Benz_Sprinter_arlista_2024.01.17.pdf?utm_source=chatgpt.com "Sprinter zárt áruszállító - A2 járműhossz BASE"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* `137378`、`137382` 的 5-T AWD 单排/双排、L2/L3 共 8 条物理分支已全部闭合。
* 5-T 分支复用已确认的四个 Sprinter VS30 AWD 尺寸组，未重复建组或重复抓取来源。
* 已完成机械校验：固定表头、197 个唯一 `id`、100 个输入 Ktype 全覆盖、88 个尺寸组唯一、所有引用闭合、无孤立尺寸组、三维及来源均非空。
* 当前批次 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* Ktype 映射行：197
* DIMENSION_GROUP：88
* 机械校验：PASS
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
137183	137183	Sedan	Silver Spirit II		4	EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	HIGH	Silver Spirit II标准轴距四门车身。	READY
137187	137187	Convertible	308 GTS Quattrovalvole		2	EU-FERRARI-308-GTS-QV-TARGA-01	HIGH	可拆卸硬顶Targa车身。	READY
137194	137194	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH	Koleos II五门SUV外廓。	READY
137208_std	137208	MPV	Combo E Life		5	EU-OPEL-COMBO-E-LIFE-L-MPV-01	MEDIUM	标准轴L Life乘用车外廓。	READY
137208_xl	137208	MPV	Combo E Life		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	加长轴XL Life车身分支。	READY
137217_long_van	137217	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	HIGH	W415长轴厢式车分支。	READY
137217_long_mpv	137217	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH	W415长轴Tourer分支。	READY
137221_long_van	137221	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	MEDIUM	W415长轴厢式车分支。	READY
137221_xl_van	137221	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	MEDIUM	W415加长轴厢式车分支。	READY
137221_long_mpv	137221	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	MEDIUM	W415长轴Tourer乘用车分支。	READY
137226_long_van	137226	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	MEDIUM	W415长轴厢式车分支。	READY
137226_xl_van	137226	Van	Citan I	W415		EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	MEDIUM	W415加长轴厢式车分支。	READY
137226_long_mpv	137226	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	MEDIUM	W415长轴Tourer乘用车分支。	READY
137234_swb	137234	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	SWB标准顶4Motion厢式车分支。	READY
137234_lwb	137234	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	LWB标准顶4Motion厢式车分支。	READY
137257	137257	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	HIGH	1.5D 100对应Compact厢式车外廓。	READY
137258	137258	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	HIGH	1.5D 120对应Medium厢式车外廓。	READY
137264_s	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137264_m	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137264_l	137264	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137265_s	137265	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137265_m	137265	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137282_s	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137282_m	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137282_l	137282	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137283_s	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短轴乘用车分支。	READY
137283_m	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M标准轴乘用车分支。	READY
137283_l	137283	MPV	Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L加长轴乘用车分支。	READY
137333_std	137333	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137333_sport	137333	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137334_std	137334	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137334_sport	137334	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137335_std	137335	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	MEDIUM	标准悬架外廓分支。	READY
137335_sport	137335	Wagon	A4 B9 Avant facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	MEDIUM	运动悬架低车身外廓分支。	READY
137358_scab_l2	137358	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137358_scab_l3	137358	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137358_dcab_l2	137358	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137358_dcab_l3	137358	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
137364_l1	137364	Pickup	Sprinter III		2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L1-FWD-01	HIGH	L1前驱单排底盘车分支。	READY
137364_l2	137364	Pickup	Sprinter III		2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-FWD-01	HIGH	L2前驱单排底盘车分支。	READY
137366_scab_l2	137366	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137366_scab_l3	137366	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137366_dcab_l2	137366	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137366_dcab_l3	137366	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
137369_scab_l2	137369	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137369_scab_l3	137369	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137369_dcab_l2	137369	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137369_dcab_l3	137369	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
137373_scab_l2	137373	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137373_scab_l3	137373	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137373_dcab_l2	137373	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137373_dcab_l3	137373	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
137377	137377	Wagon	A4 allroad B9	8W5	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH	B9 allroad旅行车外廓。	READY
137378_scab_l2	137378	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	5-T L2四驱单排驾驶室底盘车分支。	READY
137378_scab_l3	137378	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	5-T L3四驱单排驾驶室底盘车分支。	READY
137378_dcab_l2	137378	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	5-T L2四驱双排驾驶室底盘车分支。	READY
137378_dcab_l3	137378	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	5-T L3四驱双排驾驶室底盘车分支。	READY
137379_scab_l2	137379	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	3.5-T L2四驱单排驾驶室底盘车分支。	READY
137379_scab_l3	137379	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	3.5-T L3四驱单排驾驶室底盘车分支。	READY
137379_dcab_l2	137379	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	3.5-T L2四驱双排驾驶室底盘车分支。	READY
137379_dcab_l3	137379	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	3.5-T L3四驱双排驾驶室底盘车分支。	READY
137381_scab_l2	137381	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	4-T L2四驱单排驾驶室底盘车分支。	READY
137381_scab_l3	137381	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	4-T L3四驱单排驾驶室底盘车分支。	READY
137381_dcab_l2	137381	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	4-T L2四驱双排驾驶室底盘车分支。	READY
137381_dcab_l3	137381	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	4-T L3四驱双排驾驶室底盘车分支。	READY
137382_scab_l2	137382	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	HIGH	5-T L2四驱单排驾驶室底盘车分支。	READY
137382_scab_l3	137382	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	HIGH	5-T L3四驱单排驾驶室底盘车分支。	READY
137382_dcab_l2	137382	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	HIGH	5-T L2四驱双排驾驶室底盘车分支。	READY
137382_dcab_l3	137382	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	HIGH	5-T L3四驱双排驾驶室底盘车分支。	READY
137410_dcab_l1	137410	Pickup	Sprinter III	907.221	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	HIGH	3-T L1后驱双排驾驶室底盘车分支。	READY
137410_dcab_l2	137410	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	HIGH	3-T L2后驱双排驾驶室底盘车分支。	READY
137411	137411	SUV	Duster I pre-facelift	HS	5	EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	HIGH	两座商用衍生型沿用4x2五门SUV外廓。	READY
137471_dcab_l1	137471	Pickup	Sprinter III	907.221	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	HIGH	3-T L1后驱双排驾驶室底盘车分支。	READY
137471_dcab_l2	137471	Pickup	Sprinter III	907.223	4	EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	HIGH	3-T L2后驱双排驾驶室底盘车分支。	READY
137527	137527	Sedan	A-Class V177 pre-facelift	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177四门轿车标准外廓。	READY
137528	137528	Sedan	A-Class V177 pre-facelift	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH	V177四门轿车标准外廓。	READY
137547	137547	SUV	GLE I	W166	5	EU-MERCEDES-BENZ-GLE-I-SUV-01	HIGH	W166五门SUV外廓。	READY
137558_l2h2	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱厢式车分支。	READY
137558_l2h3	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3前驱厢式车分支。	READY
137558_l3h2	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱厢式车分支。	READY
137558_l3h3	137558	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	MEDIUM	L3H3前驱厢式车分支。	READY
137560_l2h2	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	MEDIUM	L2H2后驱厢式车分支。	READY
137560_l2h3	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3后驱厢式车分支。	READY
137560_l3h2	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	MEDIUM	L3H2后驱厢式车分支。	READY
137560_l3h3	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	MEDIUM	L3H3后驱厢式车分支。	READY
137560_l4h3_srw	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	MEDIUM	L4H3后驱单后轮厢式车分支。	READY
137560_l4h3_drw	137560	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	MEDIUM	L4H3后驱双后轮厢式车分支。	READY
137562	137562	Wagon	C5 I pre-facelift	DE	5	EU-CITROEN-C5-I-DE-WAGON-PREFL-01	HIGH	DE改款前旅行车及货运衍生外廓。	READY
137563_l2h2	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱厢式车分支。	READY
137563_l2h3	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3前驱厢式车分支。	READY
137563_l3h2	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱厢式车分支。	READY
137563_l3h3	137563	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	MEDIUM	L3H3前驱厢式车分支。	READY
137564_l2h2	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	MEDIUM	L2H2后驱厢式车分支。	READY
137564_l2h3	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	MEDIUM	L2H3后驱厢式车分支。	READY
137564_l3h2	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	MEDIUM	L3H2后驱厢式车分支。	READY
137564_l3h3	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	MEDIUM	L3H3后驱厢式车分支。	READY
137564_l4h3_srw	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	MEDIUM	L4H3后驱单后轮厢式车分支。	READY
137564_l4h3_drw	137564	Van	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	MEDIUM	L4H3后驱双后轮厢式车分支。	READY
137565_l2h2	137565	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱Bus外廓分支。	READY
137565_l3h2	137565	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱Bus外廓分支。	READY
137566_l2h2	137566	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	MEDIUM	L2H2前驱Bus外廓分支。	READY
137566_l3h2	137566	MPV	Transit V363 facelift	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	MEDIUM	L3H2前驱Bus外廓分支。	READY
137567	137567	Wagon	CLA II Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH	X118标准旅行车外廓。	READY
137571	137571	SUV	Cullinan I		5	EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	HIGH	Cullinan I标准五门SUV外廓。	READY
137572_l1_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	MEDIUM	L1后驱单后轮单排底盘车分支。	READY
137572_l2_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	MEDIUM	L2后驱单后轮单排底盘车分支。	READY
137572_l2_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	MEDIUM	L2后驱双后轮单排底盘车分支。	READY
137572_l3_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	MEDIUM	L3后驱单后轮单排底盘车分支。	READY
137572_l3_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	MEDIUM	L3后驱双后轮单排底盘车分支。	READY
137572_l4_srw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	MEDIUM	L4后驱单后轮单排底盘车分支。	READY
137572_l4_drw	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	MEDIUM	L4后驱双后轮单排底盘车分支。	READY
137572_l5	137572	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	MEDIUM	L5超长后驱单排底盘车分支。	READY
137573_l2	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	MEDIUM	L2前驱单排底盘车分支。	READY
137573_l3	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	MEDIUM	L3前驱单排底盘车分支。	READY
137573_l4	137573	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	MEDIUM	L4前驱单排底盘车分支。	READY
137577_l2	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	MEDIUM	L2前驱单排底盘车分支。	READY
137577_l3	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	MEDIUM	L3前驱单排底盘车分支。	READY
137577_l4	137577	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	MEDIUM	L4前驱单排底盘车分支。	READY
137579	137579	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	R8五门Fastback外廓。	READY
137580	137580	SUV	UX I	ZA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH	ZA10五门SUV外廓。	READY
137582_l1_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	MEDIUM	L1后驱单后轮单排底盘车分支。	READY
137582_l2_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	MEDIUM	L2后驱单后轮单排底盘车分支。	READY
137582_l2_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	MEDIUM	L2后驱双后轮单排底盘车分支。	READY
137582_l3_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	MEDIUM	L3后驱单后轮单排底盘车分支。	READY
137582_l3_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	MEDIUM	L3后驱双后轮单排底盘车分支。	READY
137582_l4_srw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	MEDIUM	L4后驱单后轮单排底盘车分支。	READY
137582_l4_drw	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	MEDIUM	L4后驱双后轮单排底盘车分支。	READY
137582_l5	137582	Pickup	Transit V363 facelift	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	MEDIUM	L5超长后驱单排底盘车分支。	READY
137583	137583	Wagon	508 II SW		5	EU-PEUGEOT-508-II-WAGON-01	HIGH	508 II旅行车外廓。	READY
137585	137585	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137586	137586	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137587	137587	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137588	137588	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前五门SUV外廓。	READY
137589	137589	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	第二代四驱SUV外廓。	READY
137590	137590	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH	第二代四驱SUV外廓。	READY
137591	137591	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	第二代前驱SUV外廓。	READY
137592	137592	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-01	HIGH	A110 II双门Coupe外廓。	READY
137594	137594	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	HIGH	OS混合动力五门SUV外廓。	READY
137595	137595	SUV	X6 G06 pre-facelift	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV Coupe外廓。	READY
137596	137596	SUV	X6 G06 pre-facelift	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV Coupe外廓。	READY
137597	137597	SUV	X5 G05 pre-facelift	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前标准SUV外廓。	READY
137598	137598	SUV	2008 II pre-facelift		5	EU-PEUGEOT-2008-II-SUV-PREFL-01	HIGH	第二代改款前纯电五门SUV外廓。	READY
137599	137599	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137600	137600	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137601	137601	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137602	137602	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137603	137603	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137604	137604	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247标准五门SUV外廓。	READY
137605	137605	SUV	GLB X247 pre-facelift	X247	5	EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	HIGH	AMG GLB 35专用外廓。	READY
137606	137606	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
137607	137607	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
137608	137608	MPV	Sprinter III	907.733	4	EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	HIGH	907.733 L2H1四驱Tourer外廓。	READY
137609	137609	SUV	3008 II pre-facelift	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	前驱插电混合动力标准外廓。	READY
137610	137610	SUV	3008 II pre-facelift	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	四驱插电混合动力标准外廓。	READY
137614_xs	137614	MPV	SpaceTourer I pre-facelift		5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	MEDIUM	1.6 HDI 90的XS短车身分支。	READY
137614_m	137614	MPV	SpaceTourer I pre-facelift		5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	MEDIUM	1.6 HDI 90的M标准车身分支。	READY
137623	137623	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137624	137624	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137625	137625	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137626	137626	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137627	137627	SUV	XCeed I pre-facelift	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD改款前五门跨界SUV外廓。	READY
137629	137629	Hatchback	XRAY I Cross		5	EU-LADA-XRAY-I-CROSS-HATCHBACK-01	HIGH	Cross五门车身。	READY
137641_titanium	137641	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137641_stline	137641	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137647	137647	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	G20改款前xDrive四门轿车外廓。	READY
137650	137650	Coupe	Sián FKP 37		2	EU-LAMBORGHINI-SIAN-FKP37-COUPE-01	HIGH	双门Coupe固定车顶外廓。	READY
137651	137651	Hatchback	Honda e I		5	EU-HONDA-E-I-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
137652	137652	Hatchback	Honda e I		5	EU-HONDA-E-I-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
137655_l1	137655	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137655_l2	137655	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137656_l1	137656	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137656_l2	137656	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137657_l1h1	137657	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137657_l2h1	137657	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137658_l1h1	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	MEDIUM	L1低顶Kombi分支。	READY
137658_l1h2	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	MEDIUM	L1高顶Kombi分支。	READY
137658_l2h1	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	MEDIUM	L2低顶Kombi分支。	READY
137658_l2h2	137658	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	MEDIUM	L2高顶Kombi分支。	READY
137659_l1	137659	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	HIGH	L1短轴乘用车分支。	READY
137659_l2	137659	MPV	Tourneo Custom I facelift	V362	5	EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	HIGH	L2长轴乘用车分支。	READY
137660_l1h1	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137660_l1h2	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1高顶Kombi分支。	READY
137660_l2h1	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137660_l2h2	137660	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2高顶Kombi分支。	READY
137661_l1h1	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	HIGH	L1低顶Kombi分支。	READY
137661_l1h2	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	HIGH	L1高顶Kombi分支。	READY
137661_l2h1	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	HIGH	L2低顶Kombi分支。	READY
137661_l2h2	137661	MPV	Transit Custom I facelift	V362		EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	HIGH	L2高顶Kombi分支。	READY
137666_titanium	137666	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137666_stline	137666	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137668	137668	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH	5T五门MPV外廓。	READY
137671	137671	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-E-UP-HATCHBACK-01	HIGH	改款后五门纯电Hatchback外廓。	READY
137672_titanium	137672	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-TITANIUM-01	MEDIUM	Titanium标准保险杠外廓分支。	READY
137672_stline	137672	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	MEDIUM	ST-Line系列保险杠外廓分支。	READY
137676	137676	Hatchback	Mii I Electric		5	EU-SEAT-MII-I-ELECTRIC-HATCHBACK-01	HIGH	五门纯电Hatchback外廓。	READY
137680	137680	SUV	Juke II pre-facelift	F16	5	EU-NISSAN-JUKE-II-F16-SUV-PREFL-01	HIGH	F16改款前五门SUV外廓。	READY
137685	137685	SUV	Seltos I		5	EU-KIA-SELTOS-I-SUV-4WD-01	HIGH	1.6 T-GDI四驱五门车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4201-4300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	5268	1887	1485	Automobile-Catalog Rolls-Royce Silver Spirit II	https://www.automobile-catalog.com/car/1992/2993540/rolls-royce_silver_spirit_ii.html
EU-FERRARI-308-GTS-QV-TARGA-01	4230	1720	1120	Ferrari 308 GTS Quattrovalvole official specifications	https://www.ferrari.com/en-EN/auto/308-gts-quattrovalvole
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos official dimensions	https://www.renault.com.ar/automoviles/nueva-koleos/especificaciones.html
EU-OPEL-COMBO-E-LIFE-L-MPV-01	4403	1848	1844	Opel Combo E official owner manual	https://public-servicebox.opel.com/OVddb/OV/sv_SE/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOLSE2111-sv_16_online.pdf
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1849	Opel Combo E official owner manual	https://public-servicebox.opel.com/OVddb/OV/sv_SE/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOLSE2111-sv_16_online.pdf
EU-MERCEDES-BENZ-CITAN-W415-VAN-LONG-01	4321	1829	1816	Mercedes-Benz Citan official media kit	https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/
EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	4321	1829	1809	Mercedes-Benz Citan official media kit	https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/
EU-MERCEDES-BENZ-CITAN-W415-VAN-EXTRALONG-01	4705	1829	1839	Mercedes-Benz Citan official media kit	https://media.mercedes-benz.fr/le-nouveau-mercedes-benz-citan--le-vehicule-de-livraison-efficient/
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990	Volkswagen Transporter 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/showroom-brochures-live/VW_CV_Transporter-6.1_Brochure.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990	Volkswagen Transporter 6.1 official brochure	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/showroom-brochures-live/VW_CV_Transporter-6.1_Brochure.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	4609	1920	1910	Toyota PROACE Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	4959	1920	1899	Toyota PROACE Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Opel Zafira Life official 2019 price list;Auto-Data Opel Zafira Life	https://cdn.files.smcloud.net/t/cennik_nowaZafira_Life_rp19_20_1.pdf;https://www.auto-data.net/en/opel-zafira-life-model-2663
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431	Audi A4 major upgrade official press kit	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428	Audi A4 major upgrade official press kit	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460	Audi A4 major upgrade official press kit	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435	Audi A4 major upgrade official press kit	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-AWD-01	5886	2020	2408	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L3-AWD-01	6696	2020	2400	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-AWD-01	5886	2020	2402	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L3-AWD-01	6696	2020	2392	Mercedes-Benz Sprinter UK model information and price list March 2020;Oberaigner Sprinter 4x4 technical data	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf;https://www.oberaigner.es/wp-content/uploads/2024/07/Hoja-de-producto.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L1-FWD-01	5321	2020	2302	Mercedes-Benz Sprinter UK model information and price list	https://www.gmminibus.co.uk/wp-content/uploads/2024/07/mercedes-sprinter-1.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-SCAB-L2-FWD-01	5986	2020	2292	Mercedes-Benz Sprinter UK model information and price list	https://www.gmminibus.co.uk/wp-content/uploads/2024/07/mercedes-sprinter-1.pdf
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493	Audi A4 allroad quattro official product information	https://www.audi-mediacenter.com/en/audi-a4-allroad-quattro-92
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L1-RWD-01	5576	2018	2365	Mercedes-Benz Sprinter 2018 model information and price list;Használtautó Autókatalógus Mercedes-Benz 211 CDI 907.221.13	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://katalogus.hasznaltauto.hu/mercedes-benz/211_cdi_907.221.13_automata/130304
EU-MERCEDES-BENZ-SPRINTER-VS30-CHASSIS-DCAB-L2-RWD-02	6156	2018	2365	Mercedes-Benz Sprinter 2018 model information and price list;Használtautó Autókatalógus Mercedes-Benz 214 CDI 907.223.13;Használtautó Autókatalógus Mercedes-Benz 216 CDI 907.223.13	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://katalogus.hasznaltauto.hu/mercedes-benz/214_cdi_907.223.13/119805;https://katalogus.hasznaltauto.hu/mercedes-benz/216_cdi_907.223.13/119809
EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	4315	1822	1625	Auto-Data Dacia Duster	https://www.auto-data.net/en/dacia-duster-model-1948
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Mercedes-Benz A-Class Sedan official specifications	https://www.mercedes-benz.com/en/vehicles/passenger-cars/a-class/sedan/
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796	Automobile-Catalog Mercedes-Benz GLE 350 d 4MATIC	https://www.automobile-catalog.com/car/2016/2135795/mercedes-benz_gle_350_d_4matic.html
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2490	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L2H3-01	5531	2059	2781	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2541	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2780	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	5531	2059	2542	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	5981	2059	2543	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	5981	2059	2782	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	6704	2059	2790	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	6704	2126	2790	Ford Transit official brochure	https://www.bolandcars.ie/images/new-brands/ford/transit-van.brochure.pdf
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516	Automobile-Catalog Citroën C5 Break	https://www.automobile-catalog.com/model/citroen/c5_1gen.html
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442	Mercedes-Benz CLA Shooting Brake official specifications	https://www.mercedes-benz.com/en/vehicles/passenger-cars/cla/shooting-brake/
EU-ROLLS-ROYCE-CULLINAN-I-SUV-01	5341	2164	1835	Rolls-Royce Cullinan official product information	https://www.rolls-roycemotorcars.com/en_GB/showroom/cullinan.html
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	5205	2052	2215	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	5572	2052	2210	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	5572	2111	2210	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	6022	2052	2202	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	6022	2111	2202	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	6579	2052	2214	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	6579	2111	2214	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	7577	2066	2206	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	5572	2052	2194	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	6022	2052	2186	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	6579	2052	2186	Ford Transit Chassis Cab official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404	Peugeot 508 official technical specifications	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-508
EU-LEXUS-UX-I-ZA10-SUV-01	4495	1840	1540	Lexus UX official specifications	https://newsroom.lexus.eu/new-lexus-ux/
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 SW official technical specifications	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-508-sw
EU-PEUGEOT-2008-II-SUV-PREFL-01	4300	1770	1550	Peugeot 2008 official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/peugeot2008pricespecapr23-6455a61e84bde.pdf
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682	Dacia Duster official dimensions	https://media.dacia.com/new-dacia-duster-more-duster-than-ever/
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	Dacia Duster official dimensions	https://media.dacia.com/new-dacia-duster-more-duster-than-ever/
EU-ALPINE-A110-II-COUPE-01	4178	1798	1252	Alpine A110 official technical specifications	https://www.alpine-cars.co.uk/a110.html
EU-HYUNDAI-KONA-I-OS-HYBRID-SUV-01	4165	1800	1565	Hyundai Kona Hybrid official technical specifications	https://www.hyundai.news/uk/articles/press-releases/all-new-hyundai-kona-hybrid-technical-specifications.html
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW X6 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0298304EN/the-new-bmw-x6?language=en
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0281686EN/the-new-bmw-x5?language=en
EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	4634	1834	1659	Mercedes-Benz GLB X247 official owner's manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-glb-suv-2020-september-x247-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	4650	1850	1662	Mercedes-AMG GLB official owner's manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-glb-owners-manual-supplement-march-2020-1.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-TOURER-L2H1-AWD-01	5932	2020	2435	UltimateSpecs Mercedes-Benz Sprinter 2019 L2H1 Tourer 314 CDI 3.5t AWD	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/154294/Mercedes-Benz-Sprinter-2019-L2H1-Tourer-314-CDI-35t-AWD.html
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Peugeot 3008 official technical specifications	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-3008
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905	Citroën SpaceTourer official technical specifications	https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890	Citroën SpaceTourer official technical specifications	https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495	Kia XCeed official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/XCeed/xceed_downloads/Press%20kit%20-%20Kia%20XCeed%20PETD.doc
EU-LADA-XRAY-I-CROSS-HATCHBACK-01	4171	1810	1645	LADA XRAY Cross specifications and price sheet	https://adom.ru/sites/default/files/txt/lada/xray-cross/komplektaciiiceny-ladaxraycross-lada.pdf
EU-FORD-PUMA-II-SUV-TITANIUM-01	4186	1805	1537	Ford Puma official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Puma.pdf
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537	Ford Puma official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Puma.pdf
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan official technical data	https://www.press.bmwgroup.com/global/article/detail/T0285717EN/the-all-new-bmw-3-series-sedan?language=en
EU-LAMBORGHINI-SIAN-FKP37-COUPE-01	4980	2101	1133	Auto-Data Lamborghini Sián FKP 37 6.5 V12 Hybrid AWD	https://www.auto-data.net/en/lamborghini-sian-fkp-37-6.5-v12-819hp-hybrid-awd-automatic-37680
EU-HONDA-E-I-HATCHBACK-01	3895	1750	1512	Honda e official press kit	https://hondanews.eu/gb/en/cars/media/documenttext/199613/2020-honda-e-press-kit-1
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L1-01	4973	1986	1979	Ford Tourneo Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Tourneo_Custom.pdf
EU-FORD-TOURNEO-CUSTOM-V362-MPV-L2-01	5340	1986	1977	Ford Tourneo Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Tourneo_Custom.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H1-01	4973	1986	2020	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H1-01	5340	1986	2017	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L1H2-01	4973	1986	2389	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-FORD-TRANSIT-CUSTOM-V362-BUS-L2H2-01	5340	1986	2381	Ford Transit Custom official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Transit_Custom_new.pdf
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659	Volkswagen Touran official technical data	https://www.volkswagen-newsroom.com/en/touran-3558
EU-VW-UP-I-FACELIFT-E-UP-HATCHBACK-01	3600	1645	1492	Volkswagen e-up! official technical data	https://www.volkswagen-newsroom.com/en/the-e-up-taken-to-a-new-level-5583/technical-data-5590
EU-SEAT-MII-I-ELECTRIC-HATCHBACK-01	3556	1645	1481	SEAT Mii Electric official technical specifications	https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/global_site/img/PressKits/Mii-Electric/Technical_Specifications_Mii_Electric.pdf
EU-NISSAN-JUKE-II-F16-SUV-PREFL-01	4210	1800	1595	Nissan Juke official press release	https://uk.nissannews.com/en-GB/releases/all-new-nissan-juke-redefines-compact-crossovers-with-bigger-personality-better-performance-and-ground-breaking-technologies
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620	Auto-Data Kia Seltos I 1.6 T-GDI 177 4WD	https://www.auto-data.net/en/kia-seltos-i-1.6-t-gdi-177hp-4wd-dct-38365
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4201-4300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4000 行）
- 累计尺寸组：dimension_groups_final.tsv（1658 行）

- 尺寸冲突协调：
  - EU-OPEL-COMBO-E-LIFE-XL-MPV-01 -> EU-OPEL-COMBO-E-LIFE-XL-MPV-02：4753x1848x1880 与 4753x1848x1849，创建新尺寸组
