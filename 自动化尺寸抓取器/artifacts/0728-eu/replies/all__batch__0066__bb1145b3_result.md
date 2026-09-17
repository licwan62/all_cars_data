# 任务：all 第 6501-6600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0066__bb1145b3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6501-6600 行

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
all 第 6501-6600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6501-6600_ktype_dimension_mapping_final.tsv
- all_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-BMW-6-F13-COUPE-01	4894	1894	1369
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764
EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	4820	1884	1723
EU-FORD-MONDEO-IV-BA7-SEDAN-01	4844	1886	1500
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931
EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	4922	1922	1674
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296
EU-MERCEDES-BENZ-SL-W113-CONVERTIBLE-01	4285	1760	1320
EU-MERCEDES-BENZ-SL-W121-CONVERTIBLE-01	4290	1740	1320
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	4855	2000	2455
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	5235	2000	2525
EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	5885	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	5885	2000	2530
EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	5885	2000	2240
EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	3790	1480	1210
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435
EU-VW-PASSAT-B7-362-SEDAN-01	4769	1820	1470
EU-VW-PASSAT-B7-SEDAN-01	4769	1820	1470
EU-VW-PASSAT-B7-VARIANT-WAGON-01	4771	1820	1508
EU-VW-PASSAT-B7-WAGON-01	4771	1820	1508

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Volvo	740	2.3	Stufenheck	Heckantrieb	Benzin	111	151	Aug 1988	Aug 1992	2024-03-01	6924
Mercedes-benz	170	170 D	Stufenheck	Heckantrieb	Diesel	28	38	May 1949	May 1950	2024-03-01	6925
Mercedes-benz	170	170 V	Stufenheck	Heckantrieb	Benzin	28	38	Mar 1936	May 1950	2024-03-01	6926
Mercedes-benz	170	170 S	Stufenheck	Heckantrieb	Benzin	38	52	May 1949	Feb 1952	2024-03-01	6927
Mercedes-benz	170	170 S-D	Stufenheck	Heckantrieb	Diesel	29	40	Jul 1953	Sep 1955	2024-03-01	6928
Mercedes-benz	Gullwing	300 SL	Coupe	Heckantrieb	Benzin	158	215	Sep 1954	May 1957	2024-03-01	6929
Mercedes-benz	Sl	300 SL	Cabriolet	Heckantrieb	Benzin	158	215	May 1957	Feb 1963	2024-03-01	6930
Mercedes-benz	G-Klasse	250 GD	Geländewagen geschlossen	Allrad	Diesel	62	84	Oct 1987	Dec 1992	2024-03-01	6931
Ford	Galaxy ii	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	118	160	Nov 2010	Jun 2015	2024-03-01	6932
Mercedes-benz	T1	207 D 2.4	Kasten	Heckantrieb	Diesel	53	72	Jun 1982	Jan 1990	2024-03-01	6933
Mercedes-benz	T1	307 D 2.4	Kasten	Heckantrieb	Diesel	53	72	Oct 1982	Jan 1990	2024-03-01	6934
Mercedes-benz	T1	307 D 2.4	Pritsche/Fahrgestell	Heckantrieb	Diesel	48	65	Apr 1977	Jan 1983	2024-03-01	6935
Mercedes-benz	T1	309 D 3.0	Kasten	Heckantrieb	Diesel	65	88	Oct 1982	Jan 1990	2024-03-01	6936
Mercedes-benz	T1	308 D 2.3	Bus	Heckantrieb	Diesel	58	79	May 1990	Feb 1996	2024-03-01	6937
Ford	Mondeo iv	1.6 TI	Schrägheck	Frontantrieb	Benzin	88	120	Jul 2010	Jan 2015	2024-03-01	6938
Ford	Mondeo iv	1.6 Ecoboost	Schrägheck	Frontantrieb	Benzin	118	160	Feb 2011	Jan 2015	2024-03-01	6939
Triumph	Herald	13/60	Stufenheck	Heckantrieb	Benzin	46	62	Jan 1967	Dec 1971	2024-03-01	6941
Triumph	Herald	1200	Stufenheck	Heckantrieb	Benzin	35	48	Jan 1968	Dec 1969	2024-03-01	6942
Triumph	Herald	13/60	Kombi	Heckantrieb	Benzin	46	62	Jan 1967	Dec 1971	2024-03-01	6943
Triumph	Herald	13/60	Cabriolet	Heckantrieb	Benzin	46	62	Jan 1967	Dec 1971	2024-03-01	6944
Triumph	1300	1.3	Stufenheck	Heckantrieb	Benzin	46	62	Jan 1965	Dec 1970	2024-03-01	6945
Triumph	1300	1.3 TC	Stufenheck	Heckantrieb	Benzin	56	76	Jan 1967	Dec 1970	2024-03-01	6946
Triumph	Spitfire mk i	1.2 MK I	Cabriolet	Heckantrieb	Benzin	46	63	Oct 1962	Dec 1965	2024-03-01	6947
Triumph	Spitfire mk ii	1.2	Cabriolet	Heckantrieb	Benzin	49	67	Dec 1964	Jan 1967	2024-03-01	6948
Triumph	Spitfire mk iii	1.3	Cabriolet	Heckantrieb	Benzin	55	75	Feb 1967	Nov 1970	2024-03-01	6949
Triumph	Spitfire mk iv	1.3	Cabriolet	Heckantrieb	Benzin	51	69	Dec 1972	Nov 1974	2024-05-01	6950
Ford	Mondeo iv	2.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	176	240	Jul 2010	Jan 2015	2024-03-01	6951
Triumph	Gt6 i	MK I	Coupe	Heckantrieb	Benzin	70	95	Jan 1966	Dec 1968	2024-03-01	6952
Triumph	Gt6 i	MK II	Coupe	Heckantrieb	Benzin	77	105	Dec 1968	Dec 1970	2024-03-01	6953
Triumph	Gt6 i	MK III	Coupe	Heckantrieb	Benzin	77	105	Dec 1971	Dec 1972	2024-03-01	6954
Triumph	Gt6 i	MK III	Coupe	Heckantrieb	Benzin	71	96	Dec 1972	Dec 1973	2024-03-01	6955
Triumph	Vitesse i	2	Stufenheck	Heckantrieb	Benzin	70	95	Dec 1965	Dec 1971	2024-03-01	6957
Triumph	Vitesse i	2	Stufenheck	Heckantrieb	Benzin	77	105	Dec 1968	Dec 1971	2024-03-01	6958
Triumph	Vitesse	2	Cabriolet	Heckantrieb	Benzin	70	95	Jan 1967	Dec 1968	2024-03-01	6959
Triumph	Vitesse	2	Cabriolet	Heckantrieb	Benzin	77	105	Dec 1968	Dec 1971	2024-03-01	6960
Triumph	2000 mk i	2	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1968	Mar 1972	2024-03-01	6961
Triumph	2000 mkii	2	Stufenheck	Heckantrieb	Benzin	65	88	Mar 1972	Apr 1975	2024-03-01	6963
Triumph	2000 mkii	2.0 TC	Stufenheck	Heckantrieb	Benzin	68	93	Apr 1975	Dec 1977	2024-03-01	6964
Triumph	2000 mk i estate	2	Kombi	Heckantrieb	Benzin	66	90	Jan 1968	Dec 1975	2024-03-01	6965
Triumph	2000 mkii estate	2	Kombi	Heckantrieb	Benzin	66	91	Mar 1972	Dec 1975	2024-03-01	6966
Triumph	2000 mkii estate	2.0 TC	Kombi	Heckantrieb	Benzin	68	92	Mar 1972	Dec 1975	2024-03-01	6967
Triumph	Tr 2 i	2	Cabriolet	Heckantrieb	Benzin	66	90	Jan 1953	Dec 1955	2024-03-01	6968
Triumph	Tr 3 i	2	Cabriolet	Heckantrieb	Benzin	67	91	Dec 1955	Dec 1957	2025-06-01	6969
Triumph	Tr 3a i	2	Cabriolet	Heckantrieb	Benzin	70	95	Dec 1957	Dec 1961	2024-03-01	6970
Triumph	Tr 3a i	2.2	Cabriolet	Heckantrieb	Benzin	74	100	Jan 1959	Dec 1961	2024-03-01	6971
Triumph	Tr 4 i	2	Cabriolet	Heckantrieb	Benzin	75	100	Jan 1961	Dec 1965	2024-03-01	6972
Triumph	Tr 4a	2.2	Cabriolet	Heckantrieb	Benzin	76	104	Dec 1965	Dec 1967	2024-03-01	6973
Triumph	Tr 5	2.5 PI	Cabriolet	Heckantrieb	Benzin	105	143	Jan 1967	Dec 1968	2024-03-01	6974
Triumph	Tr 6 i	2.5 PI	Cabriolet	Heckantrieb	Benzin	105	143	Jan 1969	Dec 1976	2024-03-01	6976
Triumph	Stag	3	Cabriolet	Heckantrieb	Benzin	107	145	Jan 1970	Dec 1977	2024-03-01	6977
Honda	Cr-V iv	2	SUV	Frontantrieb	Benzin	110	150	Jan 2012	Dec 2018	2024-03-01	6978
Ford	Mondeo iv	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Feb 2011	Jan 2015	2024-03-01	6979
Ford	Mondeo iv	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	147	200	Jul 2010	Jan 2015	2024-03-01	6981
Triumph	Tr 8	3.5	Cabriolet	Heckantrieb	Benzin	99	135	Jan 1980	Dec 1981	2024-03-01	6982
Triumph	2.5 pi mk i	2.5	Stufenheck	Heckantrieb	Benzin	99	134	Jan 1968	Dec 1975	2024-03-01	6983
Triumph	2.5 pi mk i estate	2.5	Kombi	Heckantrieb	Benzin	99	134	Jan 1968	Dec 1975	2024-03-01	6984
Triumph	Toledo	1300	Stufenheck	Heckantrieb	Benzin	43	59	Oct 1970	Dec 1977	2024-03-01	6985
Triumph	Toledo	1500	Stufenheck	Heckantrieb	Benzin	46	62	Oct 1970	Dec 1977	2024-03-01	6986
Triumph	Toledo	1500	Stufenheck	Heckantrieb	Benzin	49	66	Jan 1972	Dec 1977	2024-03-01	6987
Triumph	Toledo	1500 TC	Stufenheck	Heckantrieb	Benzin	51	69	Jan 1971	Dec 1977	2024-03-01	6988
Triumph	1500 i	1.5	Stufenheck	Heckantrieb	Benzin	42	57	Oct 1970	Dec 1974	2024-03-01	6989
Triumph	1500 i	1.5	Stufenheck	Heckantrieb	Benzin	49	66	Jan 1972	Dec 1974	2024-03-01	6990
Triumph	1500 i	1.5 TC	Stufenheck	Heckantrieb	Benzin	53	72	Apr 1975	Dec 1977	2024-03-01	6991
Triumph	Dolomite	1850	Stufenheck	Heckantrieb	Benzin	68	92	Jan 1972	Dec 1977	2024-03-01	6992
Triumph	Dolomite	Sprint	Stufenheck	Heckantrieb	Benzin	95	129	Jun 1973	Dec 1981	2024-03-01	6994
Triumph	Dolomite	1300	Stufenheck	Heckantrieb	Benzin	43	59	Jan 1977	Dec 1981	2024-03-01	6995
Triumph	Dolomite	1500 HL	Stufenheck	Heckantrieb	Benzin	53	72	Jan 1977	Dec 1981	2024-03-01	6996
Triumph	Dolomite	1850 HL	Stufenheck	Heckantrieb	Benzin	68	92	Jan 1977	Dec 1981	2024-03-01	6997
Triumph	2500	TC	Stufenheck	Heckantrieb	Benzin	74	100	May 1974	Apr 1975	2024-03-01	6998
Triumph	2500	S	Stufenheck	Heckantrieb	Benzin	79	108	Apr 1975	Dec 1977	2024-03-01	6999
Triumph	2500	TC	Kombi	Heckantrieb	Benzin	74	100	May 1974	Apr 1975	2024-03-01	7000
Triumph	2500	S	Kombi	Heckantrieb	Benzin	79	108	Apr 1975	Dec 1977	2024-03-01	7001
Ford	Mondeo iv turnier	1.6 TI	Kombi	Frontantrieb	Benzin	88	120	Jul 2010	Jan 2015	2024-03-01	7002
Mercedes-benz	R-Klasse	R 350 CGI 4-matic	Großraumlimousine	Allrad	Benzin	225	306	Oct 2011	Dec 2014	2024-03-01	7003
Glas	4	S 1004	Cabriolet	Heckantrieb	Benzin	31	42	May 1962	Apr 1967	2024-03-01	7004
Glas	4	S 1004 TS	Cabriolet	Heckantrieb	Benzin	47	64	May 1962	Apr 1967	2024-03-01	7005
Glas	4	1004	Stufenheck	Heckantrieb	Benzin	29	39	Jul 1963	Apr 1967	2024-03-01	7006
Glas	4	1204	Stufenheck	Heckantrieb	Benzin	39	53	Nov 1962	Apr 1967	2024-03-01	7007
Glas	4	S 1204	Cabriolet	Heckantrieb	Benzin	39	53	Nov 1962	Apr 1967	2024-03-01	7008
Glas	4	1204 TS	Stufenheck	Heckantrieb	Benzin	51	69	Nov 1962	Apr 1967	2024-03-01	7009
Glas	4	S 1204 TS	Cabriolet	Heckantrieb	Benzin	51	69	Nov 1962	Apr 1967	2024-03-01	7010
Glas	Gt	1300	Cabriolet	Heckantrieb	Benzin	63	86	Feb 1964	Oct 1968	2024-03-01	7011
Glas	4	1304	Cabriolet	Heckantrieb	Benzin	44	60	Aug 1965	Dec 1968	2024-03-01	7012
Glas	4	1304	Stufenheck	Heckantrieb	Benzin	63	86	Feb 1965	Dec 1968	2024-03-01	7013
Glas	4	S 1304	Cabriolet	Heckantrieb	Benzin	55	75	Feb 1965	Apr 1967	2024-03-01	7014
Ford	Mondeo iv turnier	1.6 Ecoboost	Kombi	Frontantrieb	Benzin	118	160	Feb 2011	Jan 2015	2024-03-01	7015
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	141	192	Dec 1977	Apr 1989	2024-03-01	7016
Glas	1700	1.7	Stufenheck	Heckantrieb	Benzin	63	86	Aug 1964	Dec 1968	2024-03-01	7017
Glas	Gt	1700	Cabriolet	Heckantrieb	Benzin	74	101	Aug 1964	Dec 1968	2024-03-01	7018
Ford	Mondeo iv turnier	2.0 Ecoboost	Kombi	Frontantrieb	Benzin	176	240	Jul 2010	Jan 2015	2024-03-01	7019
Ford	Mondeo iv turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	85	115	Feb 2011	Jan 2015	2024-03-01	7020
Ford	Mondeo iv turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	147	200	Jul 2010	Jan 2015	2024-03-01	7021
Glas	V	2600	Stufenheck	Heckantrieb	Benzin	110	150	Aug 1966	Jan 1967	2026-04-01	7022
Glas	V	3000	Stufenheck	Heckantrieb	Benzin	118	160	Feb 1966	Aug 1967	2026-04-01	7024
Glas	Goggomobil	TA 300	Stufenheck	Heckantrieb	Benzin	11	15	Feb 1955	Mar 1958	2024-03-01	7025
Glas	Goggomobil	TS 250	Coupe	Heckantrieb	Benzin	10	14	Feb 1957	Apr 1961	2024-03-01	7026
VW	Passat b7	3.6 FSI 4motion	Stufenheck	Allrad	Benzin	220	300	Jan 2011	Dec 2014	2024-03-01	7027
BMW	6	M 635 CSI	Coupe	Heckantrieb	Benzin	191	260	Apr 1986	Feb 1989	2024-03-01	7028
Glas	Goggomobil	TS 300	Coupe	Heckantrieb	Benzin	11	15	Feb 1957	Apr 1961	2024-03-01	7029
Glas	Goggomobil	TS 400	Coupe	Heckantrieb	Benzin	14	19	May 1957	May 1960	2024-03-01	7030


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类处理全部 100 个输入 Ktype，形成 101 条映射；`7016` 因生产区间同时覆盖 BMW E24 早期短车身和后期长车身，拆分为 `7016_early`、`7016_late`。
* 已复用跨批次缓存中的 Volvo 740 Sedan、Ford Galaxy II facelift、Triumph Spitfire Mk IV、Mercedes-Benz R-Class W251 facelift、BMW E24、VW Passat B7 等 8 个既有尺寸组。
* 已闭合 Mercedes-Benz 300 SL Gullwing/Roadster，以及 Ford Mondeo IV facelift 掀背和旅行车尺寸组。([automobile-catalog.com][1])
* 已集中闭合 Triumph Herald、1300、Spitfire、GT6、Vitesse、TR 系列、Stag、Toledo、Dolomite及 2000/2500 Mk II Sedan 等高复用物理外廓。([tssc.org.uk][2])
* Mercedes-Benz 170/T1、G-Class、Honda CR-V IV、部分 Triumph Estate/1500，以及 Glas/Goggomobil 系列仍缺少可闭合的尺寸或物理分支证据，暂不创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：101
* READY 映射：60，覆盖 59 个输入 Ktype
* PENDING 映射：41，覆盖 41 个输入 Ktype
* 本轮首次创建尺寸组：31
* 本轮复用既有尺寸组：8
* 当前已引用尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6924	6924	Sedan	Volvo 740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
6925	6925	Sedan	Mercedes-Benz 170 D	W136	4		MEDIUM	W136 170 D 三维与不含镜宽度尚未闭合。	PENDING: 170 D 尺寸组与来源待闭合
6926	6926	Sedan	Mercedes-Benz 170 V	W136	4		MEDIUM	W136 170 V 三维与不含镜宽度尚未闭合。	PENDING: 170 V 尺寸组与来源待闭合
6927	6927	Sedan	Mercedes-Benz 170 S	W136	4		MEDIUM	170 S 加长车身三维与来源尚未闭合。	PENDING: 170 S 尺寸组与来源待闭合
6928	6928	Sedan	Mercedes-Benz 170 S-D	W191	4		MEDIUM	W191 170 S-D 三维与来源尚未闭合。	PENDING: 170 S-D 尺寸组与来源待闭合
6929	6929	Coupe	Mercedes-Benz 300 SL W198 I	W198	2	EU-MERCEDES-BENZ-300-SL-W198-GULLWING-COUPE-2D-01	HIGH	Gullwing 双门轿跑外廓。	READY
6930	6930	Convertible	Mercedes-Benz 300 SL W198 II	W198	2	EU-MERCEDES-BENZ-300-SL-W198-ROADSTER-2D-01	HIGH	Roadster 双门敞篷外廓。	READY
6931	6931	SUV	Mercedes-Benz G-Class W463	W463			LOW	250 GD 封闭车身可能涉及三门短轴与五门长轴，分支尚未确认。	PENDING: W463 门数与轴距分支待确认
6932	6932	MPV	Ford Galaxy II facelift	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6 改款五门 MPV 外廓。	READY
6933	6933	Van	Mercedes-Benz T1				LOW	207 D 厢式车可用长度/车顶组合尚未确认。	PENDING: T1 207 D 车长与车顶分支待确认
6934	6934	Van	Mercedes-Benz T1				LOW	307 D 厢式车可用长度/车顶组合尚未确认。	PENDING: T1 307 D 车长与车顶分支待确认
6935	6935	Pickup	Mercedes-Benz T1				LOW	307 D 平台/底盘的长度分支尚未确认。	PENDING: T1 307 D 平台长度分支待确认
6936	6936	Van	Mercedes-Benz T1				LOW	309 D 厢式车可用长度/车顶组合尚未确认。	PENDING: T1 309 D 车长与车顶分支待确认
6937	6937	MPV	Mercedes-Benz T1				LOW	308 D Bus 的车长与车顶组合尚未闭合。	PENDING: T1 308 D Bus 外廓分支待确认
6938	6938	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7 改款五门掀背外廓。	READY
6939	6939	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7 改款五门掀背外廓。	READY
6941	6941	Sedan	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-SEDAN-2D-01	HIGH	13/60 双门三厢外廓。	READY
6942	6942	Sedan	Triumph Herald 1200		2	EU-TRIUMPH-HERALD-1200-SEDAN-2D-01	HIGH	1200 双门三厢外廓。	READY
6943	6943	Wagon	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-WAGON-2D-01	HIGH	13/60 双门旅行车外廓。	READY
6944	6944	Convertible	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-CONVERTIBLE-2D-01	HIGH	13/60 双门敞篷外廓。	READY
6945	6945	Sedan	Triumph 1300		4	EU-TRIUMPH-1300-SEDAN-4D-01	HIGH	Triumph 1300 四门三厢外廓。	READY
6946	6946	Sedan	Triumph 1300		4	EU-TRIUMPH-1300-SEDAN-4D-01	HIGH	Triumph 1300 四门三厢外廓。	READY
6947	6947	Convertible	Triumph Spitfire Mk I		2	EU-TRIUMPH-SPITFIRE-MK-I-CONVERTIBLE-2D-01	HIGH	Mk I 双门敞篷外廓。	READY
6948	6948	Convertible	Triumph Spitfire Mk II		2	EU-TRIUMPH-SPITFIRE-MK-II-CONVERTIBLE-2D-01	HIGH	Mk II 双门敞篷外廓。	READY
6949	6949	Convertible	Triumph Spitfire Mk III		2	EU-TRIUMPH-SPITFIRE-MK-III-CONVERTIBLE-2D-01	HIGH	Mk III 双门敞篷外廓。	READY
6950	6950	Convertible	Triumph Spitfire Mk IV		2	EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	HIGH	复用既有 Mk IV 双门敞篷尺寸组。	READY
6951	6951	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7 改款五门掀背外廓。	READY
6952	6952	Coupe	Triumph GT6 Mk I		2	EU-TRIUMPH-GT6-MK-I-COUPE-2D-01	HIGH	Mk I 双门快背轿跑外廓。	READY
6953	6953	Coupe	Triumph GT6 Mk II		2	EU-TRIUMPH-GT6-MK-II-COUPE-2D-01	HIGH	Mk II 双门快背轿跑外廓。	READY
6954	6954	Coupe	Triumph GT6 Mk III		2	EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	HIGH	Mk III 双门快背轿跑外廓。	READY
6955	6955	Coupe	Triumph GT6 Mk III		2	EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	HIGH	Mk III 双门快背轿跑外廓。	READY
6957	6957	Sedan	Triumph Vitesse 2-Litre Mk I		2	EU-TRIUMPH-VITESSE-2L-MK-I-SEDAN-2D-01	HIGH	Mk I 双门三厢外廓。	READY
6958	6958	Sedan	Triumph Vitesse 2-Litre Mk II		2	EU-TRIUMPH-VITESSE-2L-MK-II-SEDAN-2D-01	HIGH	Mk II 双门三厢外廓。	READY
6959	6959	Convertible	Triumph Vitesse 2-Litre Mk I		2	EU-TRIUMPH-VITESSE-2L-MK-I-CONVERTIBLE-2D-01	HIGH	Mk I 双门敞篷外廓。	READY
6960	6960	Convertible	Triumph Vitesse 2-Litre Mk II		2	EU-TRIUMPH-VITESSE-2L-MK-II-CONVERTIBLE-2D-01	HIGH	Mk II 双门敞篷外廓。	READY
6961	6961	Sedan	Triumph 2000 Mk I		4		MEDIUM	Mk I 三厢尺寸需与 Mk II 4629 mm 车身分离核对。	PENDING: Triumph 2000 Mk I 尺寸组待闭合
6963	6963	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II 大型四门三厢共用外廓。	READY
6964	6964	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II 大型四门三厢共用外廓。	READY
6965	6965	Wagon	Triumph 2000 Mk I Estate		5		LOW	Mk I Estate 三维与来源尚未闭合。	PENDING: Triumph 2000 Mk I Estate 尺寸组待闭合
6966	6966	Wagon	Triumph 2000 Mk II Estate		5		LOW	Mk II Estate 三维与来源尚未闭合。	PENDING: Triumph 2000 Mk II Estate 尺寸组待闭合
6967	6967	Wagon	Triumph 2000 Mk II Estate		5		LOW	Mk II Estate 三维与来源尚未闭合。	PENDING: Triumph 2000 Mk II Estate 尺寸组待闭合
6968	6968	Convertible	Triumph TR2		2	EU-TRIUMPH-TR2-CONVERTIBLE-2D-01	HIGH	TR2 双门敞篷外廓。	READY
6969	6969	Convertible	Triumph TR3		2	EU-TRIUMPH-TR3-CONVERTIBLE-2D-01	HIGH	TR3 双门敞篷外廓。	READY
6970	6970	Convertible	Triumph TR3A		2	EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	HIGH	TR3A 双门敞篷外廓。	READY
6971	6971	Convertible	Triumph TR3A		2	EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	HIGH	TR3A 双门敞篷外廓。	READY
6972	6972	Convertible	Triumph TR4		2	EU-TRIUMPH-TR4-CONVERTIBLE-2D-01	HIGH	TR4 双门敞篷外廓。	READY
6973	6973	Convertible	Triumph TR4A		2	EU-TRIUMPH-TR4A-CONVERTIBLE-2D-01	HIGH	TR4A 双门敞篷外廓。	READY
6974	6974	Convertible	Triumph TR5		2	EU-TRIUMPH-TR5-CONVERTIBLE-2D-01	HIGH	TR5 双门敞篷外廓。	READY
6976	6976	Convertible	Triumph TR6		2	EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	HIGH	TR6 双门敞篷外廓。	READY
6977	6977	Convertible	Triumph Stag		2	EU-TRIUMPH-STAG-CONVERTIBLE-2D-01	HIGH	Stag 双门敞篷外廓。	READY
6978	6978	SUV	Honda CR-V IV	RM	5		LOW	生产区间跨中期改款，前后外廓分支与高度尚未闭合。	PENDING: CR-V IV 改款前后尺寸分支待确认
6979	6979	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7 改款五门掀背外廓。	READY
6981	6981	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7 改款五门掀背外廓。	READY
6982	6982	Convertible	Triumph TR8		2	EU-TRIUMPH-TR8-CONVERTIBLE-2D-01	HIGH	TR8 双门敞篷外廓。	READY
6983	6983	Sedan	Triumph 2.5 PI Mk I		4		LOW	输入年段跨 Mk I/Mk II 边界，物理分支尚未确认。	PENDING: 2.5 PI Mk I 年段与车身分支冲突
6984	6984	Wagon	Triumph 2.5 PI Mk I Estate		5		LOW	Estate 年段与 Mk I/Mk II 车身分支尚未闭合。	PENDING: 2.5 PI Estate 外廓分支待确认
6985	6985	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo 四门三厢外廓。	READY
6986	6986	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo 四门三厢外廓。	READY
6987	6987	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo 四门三厢外廓。	READY
6988	6988	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo 四门三厢外廓。	READY
6989	6989	Sedan	Triumph 1500		4		LOW	输入驱动形式与 1500 FWD 资料冲突，且年段跨 1500TC。	PENDING: Triumph 1500 驱动与代际边界冲突
6990	6990	Sedan	Triumph 1500		4		LOW	输入驱动形式与 1500 FWD 资料冲突，且年段跨 1500TC。	PENDING: Triumph 1500 驱动与代际边界冲突
6991	6991	Sedan	Triumph 1500 TC		4		LOW	1975-1977 记录需确认是否实际属于 1500TC/Toledo-Dolomite 外廓。	PENDING: Triumph 1500 TC 车型边界待确认
6992	6992	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite 四门三厢共用外廓。	READY
6994	6994	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite 四门三厢共用外廓。	READY
6995	6995	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite 四门三厢共用外廓。	READY
6996	6996	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite 四门三厢共用外廓。	READY
6997	6997	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite 四门三厢共用外廓。	READY
6998	6998	Sedan	Triumph 2500 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II 大型四门三厢共用外廓。	READY
6999	6999	Sedan	Triumph 2500 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II 大型四门三厢共用外廓。	READY
7000	7000	Wagon	Triumph 2500 Mk II Estate		5		LOW	2500 TC Estate 三维与来源尚未闭合。	PENDING: Triumph 2500 Estate 尺寸组待闭合
7001	7001	Wagon	Triumph 2500 Mk II Estate		5		LOW	2500 S Estate 三维与来源尚未闭合。	PENDING: Triumph 2500 Estate 尺寸组待闭合
7002	7002	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7 改款五门旅行车外廓。	READY
7003	7003	MPV	Mercedes-Benz R-Class W251 facelift	W251	5	EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	HIGH	W251 改款五门 MPV 外廓。	READY
7004	7004	Convertible	Glas 04 Series		2		LOW	S 1004 Cabriolet 三维与来源尚未闭合。	PENDING: Glas S 1004 Cabriolet 尺寸组待闭合
7005	7005	Convertible	Glas 04 Series		2		LOW	S 1004 TS Cabriolet 三维与来源尚未闭合。	PENDING: Glas S 1004 TS Cabriolet 尺寸组待闭合
7006	7006	Sedan	Glas 04 Series		2		LOW	1004 双门三厢三维与来源尚未闭合。	PENDING: Glas 1004 Sedan 尺寸组待闭合
7007	7007	Sedan	Glas 04 Series		2		LOW	1204 双门三厢三维与来源尚未闭合。	PENDING: Glas 1204 Sedan 尺寸组待闭合
7008	7008	Convertible	Glas 04 Series		2		LOW	S 1204 Cabriolet 三维与来源尚未闭合。	PENDING: Glas S 1204 Cabriolet 尺寸组待闭合
7009	7009	Sedan	Glas 04 Series		2		LOW	1204 TS 双门三厢三维与来源尚未闭合。	PENDING: Glas 1204 TS Sedan 尺寸组待闭合
7010	7010	Convertible	Glas 04 Series		2		LOW	S 1204 TS Cabriolet 三维与来源尚未闭合。	PENDING: Glas S 1204 TS Cabriolet 尺寸组待闭合
7011	7011	Convertible	Glas GT		2		LOW	1300 GT Cabriolet 三维与来源尚未闭合。	PENDING: Glas GT 1300 Cabriolet 尺寸组待闭合
7012	7012	Convertible	Glas 04 Series		2		LOW	1304 Cabriolet 三维与来源尚未闭合。	PENDING: Glas 1304 Cabriolet 尺寸组待闭合
7013	7013	Sedan	Glas 04 Series		2		LOW	1304 双门三厢三维与来源尚未闭合。	PENDING: Glas 1304 Sedan 尺寸组待闭合
7014	7014	Convertible	Glas 04 Series		2		LOW	S 1304 Cabriolet 三维与来源尚未闭合。	PENDING: Glas S 1304 Cabriolet 尺寸组待闭合
7015	7015	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7 改款五门旅行车外廓。	READY
7016_early	7016	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH	生产区间覆盖 E24 早期短车身。	READY
7016_late	7016	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-LATE-01	HIGH	生产区间覆盖 E24 后期长车身。	READY
7017	7017	Sedan	Glas 1700		4		LOW	Glas 1700 四门三厢三维与来源尚未闭合。	PENDING: Glas 1700 Sedan 尺寸组待闭合
7018	7018	Convertible	Glas GT		2		LOW	1700 GT Cabriolet 三维与来源尚未闭合。	PENDING: Glas GT 1700 Cabriolet 尺寸组待闭合
7019	7019	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7 改款五门旅行车外廓。	READY
7020	7020	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7 改款五门旅行车外廓。	READY
7021	7021	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7 改款五门旅行车外廓。	READY
7022	7022	Coupe	Glas V8		2		LOW	输入 BodyStyle 与 Glas V8 双门轿跑资料冲突，三维尚未闭合。	PENDING: Glas V8 2600 车身形式与尺寸待确认
7024	7024	Coupe	Glas V8		2		LOW	输入 BodyStyle 与 Glas V8 双门轿跑资料冲突，三维尚未闭合。	PENDING: Glas V8 3000 车身形式与尺寸待确认
7025	7025	Sedan	Glas Goggomobil TA		2		LOW	TA 300 三维与来源尚未闭合。	PENDING: Goggomobil TA 300 尺寸组待闭合
7026	7026	Coupe	Glas Goggomobil TS		2		LOW	TS 250 三维与来源尚未闭合。	PENDING: Goggomobil TS 250 尺寸组待闭合
7027	7027	Sedan	Volkswagen Passat B7	362	4	EU-VW-PASSAT-B7-362-SEDAN-01	HIGH	B7 362 四门三厢外廓。	READY
7028	7028	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-M635I-LATE-01	HIGH	M 635 CSi 后期双门轿跑外廓。	READY
7029	7029	Coupe	Glas Goggomobil TS		2		LOW	TS 300 三维与来源尚未闭合。	PENDING: Goggomobil TS 300 尺寸组待闭合
7030	7030	Coupe	Glas Goggomobil TS		2		LOW	TS 400 三维与来源尚未闭合。	PENDING: Goggomobil TS 400 尺寸组待闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-300-SL-W198-GULLWING-COUPE-2D-01	4520	1790	1300	Automobile-Catalog Mercedes-Benz 300 SL Gullwing profile	https://www.automobile-catalog.com/car/1954/1460990/mercedes-benz_300_sl_opt__3_25_axle.html
EU-MERCEDES-BENZ-300-SL-W198-ROADSTER-2D-01	4570	1790	1300	Automobile-Catalog Mercedes-Benz 300 SL Roadster profile	https://www.automobile-catalog.com/car/1958/1461020/mercedes-benz_300_sl_roadster.html
EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	4784	1886	1500	Automobile-Catalog Ford Mondeo 5-door 1.6 EcoBoost 160 profile	https://www.automobile-catalog.com/car/2011/1594655/ford_mondeo_5-dr_1_6_ecoboost_160_trend.html
EU-TRIUMPH-HERALD-13-60-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Saloon profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=42
EU-TRIUMPH-HERALD-1200-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 1200 Saloon profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=27
EU-TRIUMPH-HERALD-13-60-WAGON-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Estate profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=43
EU-TRIUMPH-HERALD-13-60-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Convertible profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=30
EU-TRIUMPH-1300-SEDAN-4D-01	3937	1568	1372	Triumph Sports Six Club Triumph 1300 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=34
EU-TRIUMPH-SPITFIRE-MK-I-CONVERTIBLE-2D-01	3683	1448	1207	Triumph Sports Six Club Spitfire Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=24
EU-TRIUMPH-SPITFIRE-MK-II-CONVERTIBLE-2D-01	3683	1448	1207	Triumph Sports Six Club Spitfire Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=24
EU-TRIUMPH-SPITFIRE-MK-III-CONVERTIBLE-2D-01	3734	1448	1207	Triumph Sports Six Club Spitfire Mk III profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=23
EU-TRIUMPH-GT6-MK-I-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=19
EU-TRIUMPH-GT6-MK-II-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=19
EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk III profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=20
EU-TRIUMPH-VITESSE-2L-MK-I-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk I profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=33
EU-TRIUMPH-VITESSE-2L-MK-II-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=11
EU-TRIUMPH-VITESSE-2L-MK-I-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk I profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=33
EU-TRIUMPH-VITESSE-2L-MK-II-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=11
EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	4629	1651	1422	Triumph Sports Six Club Triumph 2000 profile; Triumph Sports Six Club Triumph 2.5Pi/2500TC/2500S profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=38;https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=39
EU-TRIUMPH-TR2-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR2 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=15
EU-TRIUMPH-TR3-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR3/3A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=16
EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR3/3A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=16
EU-TRIUMPH-TR4-CONVERTIBLE-2D-01	3962	1473	1207	Triumph Sports Six Club TR4/4A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=17
EU-TRIUMPH-TR4A-CONVERTIBLE-2D-01	3962	1473	1207	Triumph Sports Six Club TR4/4A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=17
EU-TRIUMPH-TR5-CONVERTIBLE-2D-01	3900	1473	1270	Triumph Sports Six Club TR5 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=18
EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	3950	1550	1270	Triumph Sports Six Club TR6 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=6
EU-TRIUMPH-STAG-CONVERTIBLE-2D-01	4413	1613	1257	Triumph Sports Six Club Stag profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=35
EU-TRIUMPH-TR8-CONVERTIBLE-2D-01	4067	1681	1267	Triumph Sports Six Club TR7/8 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=22
EU-TRIUMPH-TOLEDO-SEDAN-4D-01	4125	1588	1372	Triumph Sports Six Club Toledo/1500TC profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=36
EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	4125	1588	1372	Triumph Sports Six Club Dolomite 1850 profile; Triumph Sports Six Club Dolomite Sprint profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=37;https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=8
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Automobile-Catalog Ford Mondeo Estate 1.6 EcoBoost 160 profile	https://www.automobile-catalog.com/car/2011/1595570/ford_mondeo_5-dr_1_6_ecoboost_160_trend.html
```

## 下一步优先处理

1. 按已有缓存组合核对 Mercedes-Benz T1 的车长、车顶及厢式车/平台/Bus 分支，争取批量消除 Ktype `6933–6937`。
2. 闭合 Triumph 2000/2500 Estate、2000 Mk I、2.5 PI 与 Triumph 1500/1500 TC 的代际边界。
3. 核对 Honda CR-V IV 改款前后，以及 G-Class W463 三门短轴/五门长轴分支。
4. 最后集中处理 Mercedes-Benz 170 与 Glas/Goggomobil 历史车型尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1954/1460990/mercedes-benz_300_sl_opt__3_25_axle.html?utm_source=chatgpt.com "1954 Mercedes-Benz 300 SL (opt. 3.25 axle) (man. 4)"
[2]: https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=42 "The Triumph Sports Six Club - Cars - Triumph Herald 13/60 Saloon"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6501-6600_ktype_dimension_mapping_final.tsv
- all_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz 170 系列 4 个 Ktype；其中 `6926` 的 170 V 跨越战前、战后两套不同外廓，拆分为 `prewar` 与 `postwar` 两行。([汽车目录][1])
* 闭合 Glas Typ 612、Glas GT、Glas 1700、Glas V8 和 Goggomobil T/TS 共 19 个 Ktype；`7022`、`7024` 根据车型资料将车身形式由输入的 Stufenheck 修正为 Coupe。([汽车目录][2])
* Goggomobil TS 250、TS 300、TS 400 复用同一双门轿跑尺寸组；TA 300 使用 T/TA 双门三厢外廓组。([汽车目录][3])
* `6991` 已关联既有 Triumph 1500 TC/Toledo 长车身尺寸组，不重复输出该尺寸组。([胜利运动六人俱乐部][4])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：102
* READY 映射：85，覆盖 83 个输入 Ktype
* PENDING 映射：17，覆盖 17 个输入 Ktype
* 当前已确认尺寸组：51
* 本轮新增/修改映射：25 行
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6925	6925	Sedan	Mercedes-Benz 170 D W136 I	W136	4	EU-MERCEDES-BENZ-170-D-W136-SEDAN-4D-01	HIGH	W136四门柴油三厢外廓。	READY
6926_prewar	6926	Sedan	Mercedes-Benz 170 V W136 I	W136	4	EU-MERCEDES-BENZ-170-V-W136-SEDAN-PREWAR-01	HIGH	战前四门三厢外廓分支。	READY
6926_postwar	6926	Sedan	Mercedes-Benz 170 V W136 I	W136	4	EU-MERCEDES-BENZ-170-V-W136-SEDAN-POSTWAR-01	HIGH	战后四门三厢外廓分支。	READY
6927	6927	Sedan	Mercedes-Benz 170 S W136 IV	W136	4	EU-MERCEDES-BENZ-170-S-W136-SEDAN-4D-01	HIGH	W136 IV四门三厢外廓。	READY
6928	6928	Sedan	Mercedes-Benz 170 S-D W136 VIII D	W136	4	EU-MERCEDES-BENZ-170-SD-W136-SEDAN-4D-01	HIGH	W136 VIII D四门柴油三厢外廓。	READY
6991	6991	Sedan	Triumph 1500 TC		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	MEDIUM	1500 TC长车身四门三厢外廓。	READY
7004	7004	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	MEDIUM	Typ 612双门敞篷外廓。	READY
7005	7005	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	MEDIUM	Typ 612双门敞篷外廓。	READY
7006	7006	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7007	7007	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7008	7008	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7009	7009	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7010	7010	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7011	7011	Convertible	Glas 1300-1700 GT		2	EU-GLAS-GT-CONVERTIBLE-2D-01	HIGH	Glas GT双门敞篷外廓。	READY
7012	7012	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7013	7013	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7014	7014	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7017	7017	Sedan	Glas 1700		4	EU-GLAS-1700-SEDAN-4D-01	HIGH	Glas 1700四门三厢外廓。	READY
7018	7018	Convertible	Glas 1300-1700 GT		2	EU-GLAS-GT-CONVERTIBLE-2D-01	HIGH	Glas GT双门敞篷外廓。	READY
7022	7022	Coupe	Glas 2600-3000 V8		2	EU-GLAS-V8-COUPE-2D-01	HIGH	输入车身形式修正为双门轿跑。	READY
7024	7024	Coupe	Glas 2600-3000 V8		2	EU-GLAS-V8-COUPE-2D-01	HIGH	输入车身形式修正为双门轿跑。	READY
7025	7025	Sedan	Goggomobil T/TA		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	MEDIUM	T/TA双门三厢外廓。	READY
7026	7026	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	MEDIUM	TS系列双门轿跑外廓。	READY
7029	7029	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	HIGH	TS系列双门轿跑外廓。	READY
7030	7030	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	MEDIUM	TS系列双门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-170-D-W136-SEDAN-4D-01	4285	1580	1610	Automobile-Catalog Mercedes-Benz 170 D W136 profile	https://www.automobile-catalog.com/car/1949/31565/mercedes-benz_170_d_w_136_i_d.html
EU-MERCEDES-BENZ-170-V-W136-SEDAN-PREWAR-01	4270	1570	1560	Automobile-Catalog Mercedes-Benz 170 V pre-war profile	https://www.automobile-catalog.com/car/1939/1459190/mercedes-benz_170_v.html
EU-MERCEDES-BENZ-170-V-W136-SEDAN-POSTWAR-01	4285	1580	1610	Automobile-Catalog Mercedes-Benz 170 V post-war profile	https://www.automobile-catalog.com/car/1950/1459205/mercedes-benz_170_v_w_136_i.html
EU-MERCEDES-BENZ-170-S-W136-SEDAN-4D-01	4455	1684	1610	Automobile-Catalog Mercedes-Benz 170 S W136 profile	https://www.automobile-catalog.com/car/1950/1459325/mercedes-benz_170_s_w_136_iv.html
EU-MERCEDES-BENZ-170-SD-W136-SEDAN-4D-01	4450	1685	1590	Automobile-Catalog Mercedes-Benz 170 S-D W136 profile	https://www.automobile-catalog.com/car/1954/1459385/mercedes-benz_170_s-d_w_136_viii_d.html
EU-GLAS-TYP-612-CONVERTIBLE-2D-01	3835	1500	1355	Automobile-Catalog Glas Typ 612 Cabriolet profiles	https://www.automobile-catalog.com/car/1965/1017410/glas_s_1204_cabriolet.html;https://www.automobile-catalog.com/car/1967/1017665/glas_1304_cabriolet.html
EU-GLAS-TYP-612-SEDAN-2D-01	3835	1500	1355	Automobile-Catalog Glas Typ 612 Limousine profiles	https://www.automobile-catalog.com/car/1963/1017455/glas_s_1004.html;https://www.automobile-catalog.com/make/glas/1004_1204_1304/1004_1204_1304_limousine/1966.html
EU-GLAS-GT-CONVERTIBLE-2D-01	4050	1550	1350	Automobile-Catalog Glas 1300-1700 GT Cabriolet profiles	https://www.automobile-catalog.com/car/1967/1017875/glas_1700_gt_cabriolet.html;https://www.automobile-catalog.com/make/glas/1300_1700_gt/1300_1700_gt_cabriolet/1964.html
EU-GLAS-1700-SEDAN-4D-01	4415	1610	1390	Automobile-Catalog Glas 1700 profile	https://www.automobile-catalog.com/car/1964/36980/glas_1700.html
EU-GLAS-V8-COUPE-2D-01	4600	1750	1380	Automobile-Catalog Glas 2600 and 3000 V8 profiles	https://www.automobile-catalog.com/car/1966/1017905/glas_2600_v8.html;https://www.automobile-catalog.com/car/1967/1017920/glas_3000_v8.html
EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	2900	1280	1310	Automobile-Catalog Goggomobil T 300 profile	https://www.automobile-catalog.com/car/1957/1017080/goggomobil_t_300.html
EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	3035	1370	1235	Automobile-Catalog Goggomobil TS profiles	https://www.automobile-catalog.com/car/1957/1017125/goggomobil_ts_300.html;https://www.automobile-catalog.com/make/goggomobil/ts_250_300_400/ts_250_300_400/1963.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz T1 `6933–6937` 的车长、车顶和厢式车/平台/Bus 分支。
2. 闭合 Triumph 2000/2500 Sedan、Estate、2.5 PI 与 1500 FWD 剩余边界。
3. 最后处理 Mercedes-Benz G-Class W463 `6931` 和 Honda CR-V IV `6978` 的多外廓分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1949/31565/mercedes-benz_170_d_w_136_i_d.html?utm_source=chatgpt.com "1949 Mercedes-Benz 170 D (W 136 I D) Specs Review (28 kW / 38 PS / 38 hp) (since May 1949 for Europe )"
[2]: https://www.automobile-catalog.com/car/1963/1017455/glas_s_1004.html?utm_source=chatgpt.com "1963 Glas S 1004 Specs Review (31 kW / 42 PS / 42 hp) (since mid-year 1963 for Europe )"
[3]: https://www.automobile-catalog.com/car/1957/1017080/goggomobil_t_300.html?utm_source=chatgpt.com "1957 Goggomobil T 300 Specs Review (10.9 kW / 14.8 PS / 15 hp) (for Europe )"
[4]: https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=36 "The Triumph Sports Six Club - Cars - Triumph Toledo/1500TC"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6501-6600_ktype_dimension_mapping_final.tsv
- all_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Triumph 2000/2500 系列的 Mk I、Mk II 早期、Mk II 后期 Sedan/Wagon 外廓；跨代际生产区间的 Ktype 已拆分为稳定派生行。([THE TRIUMPH 2000 / 2500 / 2·5 REGISTER][1])
* 已闭合 Triumph 1500 四门三厢尺寸组，`6989`、`6990` 的输入驱动字段冲突保留在映射备注中，不再阻塞尺寸关联。([carfolio.com][2])
* Honda CR-V IV `6978` 已拆分为改款前、改款后两套外廓，统一使用不含后视镜宽度。([hondanews.eu][3])
* 本轮消除 11 个输入 Ktype 的 PENDING；剩余 6 个均集中在 Mercedes-Benz T1 和 G-Klasse。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：111
* READY 映射：105，覆盖 94 个输入 Ktype
* PENDING 映射：6，覆盖 6 个输入 Ktype
* 当前已确认尺寸组：59
* 本轮新增/修改映射：20 行
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6961_mki	6961	Sedan	Triumph 2000 Mk I		4	EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk I短车身分支。	READY
6961_mkii	6961	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk II长车身分支。	READY
6965_mki	6965	Wagon	Triumph 2000 Mk I		5	EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	MEDIUM	生产区间覆盖Mk I旅行车分支。	READY
6965_mkii_pre74	6965	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	MEDIUM	生产区间覆盖Mk II早期旅行车分支。	READY
6965_mkii_post74	6965	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	MEDIUM	生产区间覆盖Mk II后期旅行车分支。	READY
6966_pre74	6966	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	HIGH	Mk II早期旅行车分支。	READY
6966_post74	6966	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车分支。	READY
6967_pre74	6967	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	HIGH	Mk II早期旅行车分支。	READY
6967_post74	6967	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车分支。	READY
6978_prefl	6978	SUV	Honda CR-V IV	RM1	5	EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	HIGH	改款前五门SUV外廓。	READY
6978_facelift	6978	SUV	Honda CR-V IV	RM1	5	EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
6983_mki	6983	Sedan	Triumph 2.5 PI Mk I		4	EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk I短车身分支。	READY
6983_mkii	6983	Sedan	Triumph 2.5 PI Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk II长车身分支。	READY
6984_mki	6984	Wagon	Triumph 2.5 PI Mk I		5	EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	MEDIUM	生产区间覆盖Mk I旅行车分支。	READY
6984_mkii_pre74	6984	Wagon	Triumph 2.5 PI Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	MEDIUM	生产区间覆盖Mk II早期旅行车分支。	READY
6984_mkii_post74	6984	Wagon	Triumph 2.5 PI Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	MEDIUM	生产区间覆盖Mk II后期旅行车分支。	READY
6989	6989	Sedan	Triumph 1500		4	EU-TRIUMPH-1500-SEDAN-4D-01	MEDIUM	输入驱动字段与车型资料不一致，按1500四门外廓处理。	READY
6990	6990	Sedan	Triumph 1500		4	EU-TRIUMPH-1500-SEDAN-4D-01	MEDIUM	输入驱动字段与车型资料不一致，按1500四门外廓处理。	READY
7000	7000	Wagon	Triumph 2500 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车外廓。	READY
7001	7001	Wagon	Triumph 2500 Mk II		5	EU-TRIUMPH-2500S-MK-II-WAGON-5D-01	HIGH	2500 S旅行车低车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	4410	1650	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	4410	1650	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	4500	1690	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	4530	1710	1440	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2500S-MK-II-WAGON-5D-01	4530	1710	1410	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-1500-SEDAN-4D-01	4115	1568	1372	Carfolio 1972 Triumph 1500;Carfolio 1973 Triumph 1500 TC	https://www.carfolio.com/triumph-1500-690910;https://www.carfolio.com/triumph-1500-tc-55880
EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	4570	1820	1685	Honda Europe 2012 CR-V press kit;Auto-Data Honda CR-V IV dimensions	https://hondanews.eu/eu/lv/cars/media/pressreleases/34671/cr-v;https://www.auto-data.net/en/honda-cr-v-model-1317
EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	4605	1820	1685	Honda Europe 2015 CR-V specifications;Drive.place Honda CR-V IV facelift technical data	https://hondanews.eu/be/fr/cars/media/pressreleases/41825/honda-cr-v-2015;https://honda.drive.place/cr_v/iv_res/group_offroad_5d/583136
```

## 下一步优先处理

1. 根据型号代码集中闭合 T1 `6933–6937` 的 L1/L2/L3、车顶高度及 Van/Platform/Bus 分支，并优先复用已有 T1 尺寸组。
2. 核对 `6931` 的 62 kW Mercedes-Benz 250 GD 所属 W460/W461 边界，以及 SWB/LWB、三门/五门物理外廓。
3. 上述 6 个 PENDING 消除后立即进入一次机械收尾并输出两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://triumph2000register.co.uk/the-cars/technical-specifications/?utm_source=chatgpt.com "Technical Specifications - THE TRIUMPH 2000 / 2500 / 2·5 ..."
[2]: https://www.carfolio.com/triumph-1500-690910?utm_source=chatgpt.com "1972 Triumph 1500: detailed specifications, performance ..."
[3]: https://hondanews.eu/eu/lv/cars/media/pressreleases/34671/cr-v?utm_source=chatgpt.com "CR-V"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6501-6600_ktype_dimension_mapping_final.tsv
- all_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* `6931` 已确认是 **62 kW / 84 hp 的 W460 250 GD**，并按官方资料拆分为短轴三门 Station Wagon、长轴五门 Station Wagon、长轴三门 Van；短轴为 `3955×1700×1925 mm`，长轴为 `4405×1700×1920 mm`。([marsClassic][1])
* `6933`、`6936` 已按已确认的 T1 厢式车车长和车顶组合拆分，全部复用既有 T1 尺寸组；相关 TecDoc/EPC 车型代码覆盖多个轴距与车身分支。([wahnsinnspreise.com][2])
* `6935` 已按早期 307 D 平台底盘的 `602.321`、`602.323` 两个物理长度分支拆分，并复用既有平台尺寸组。([catalogonuevo.icerbrakes.com][3])
* `6937` 已按 `602.371` 与 `602.373` 两个 Bus 车长分支拆分并复用既有 T1 外廓尺寸组。([winparts.ie][4])
* 当前仅剩 `6934` 的 307 D 厢式车完整代码集合与高顶分支边界尚未完全闭合。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：122
* READY 映射：121，覆盖 99 个输入 Ktype
* PENDING 映射：1，覆盖 1 个输入 Ktype
* 当前已确认尺寸组：61
* 本轮新增/修改映射：17 行
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6931_swb_3dr	6931	SUV	Mercedes-Benz G-Class W460	460.337	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	HIGH	短轴三门Station Wagon外廓。	READY
6931_lwb_5dr	6931	SUV	Mercedes-Benz G-Class W460	460.338	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	HIGH	长轴五门Station Wagon外廓。	READY
6931_lwb_van	6931	Van	Mercedes-Benz G-Class W460	460.328	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	HIGH	长轴三门封闭Van外廓。	READY
6933_l1h1	6933	Van	Mercedes-Benz T1	601.361		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1H1厢式车分支。	READY
6933_l1h2	6933	Van	Mercedes-Benz T1	601.366		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1H2厢式车分支。	READY
6933_l2h1	6933	Van	Mercedes-Benz T1	601.362		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2H1厢式车分支。	READY
6933_l2h2	6933	Van	Mercedes-Benz T1	601.367		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2H2厢式车分支。	READY
6934	6934	Van	Mercedes-Benz T1	602	6		LOW	307 D厢式车标准顶与高顶的完整车型代码集合尚未闭合。	PENDING: T1 307 D厢式车分支待最终确认
6935_l1	6935	Pickup	Mercedes-Benz T1	602.321		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	短轴平台或底盘分支。	READY
6935_l3	6935	Pickup	Mercedes-Benz T1	602.323		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	长轴平台或底盘分支。	READY
6936_l1h1	6936	Van	Mercedes-Benz T1	602.461		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1H1厢式车分支。	READY
6936_l1h2	6936	Van	Mercedes-Benz T1	602.476		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1H2厢式车分支。	READY
6936_l2h1	6936	Van	Mercedes-Benz T1	602.462		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2H1厢式车分支。	READY
6936_l2h2	6936	Van	Mercedes-Benz T1	602.477		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2H2厢式车分支。	READY
6936_l3h1	6936	Van	Mercedes-Benz T1	602.463		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3H1厢式车分支。	READY
6937_l1	6937	MPV	Mercedes-Benz T1	602.371		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	短轴Bus外廓。	READY
6937_l3	6937	MPV	Mercedes-Benz T1	602.373		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	长轴Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925	Mercedes-Benz Public Archive 250 GD short wheelbase 1987-1992	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-short-wheelbase-1987---1992.xhtml?oid=190007636
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920	Mercedes-Benz Public Archive 250 GD long wheelbase 1987-1992	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-long-wheelbase-1987---1992.xhtml?oid=190007637
```

## 下一步优先处理

1. 仅核对 `6934` 对应的完整 T1 307 D 厢式车代码集合。
2. 将已确认代码机械映射到既有 L1/L2/L3、H1/H2 尺寸组。
3. PENDING 消除后立即输出两张最终完整 TSV、两个指定 sandbox 下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-short-wheelbase-1987---1992.xhtml?oid=190007636 "250 GD (short wheelbase), 1987 - 1992"
[2]: https://www.wahnsinnspreise.com/ersatzteile-passend-zu/mercedes-benz/t1-kasten-601-611/207-d-2-4-601-361-601-367-601-366-601-362/6933/bordwandprofile-zubehoer-0-705817.html?utm_source=chatgpt.com "Bordwandprofile Zubehoer als Universal-Artikel für MERCEDES-BENZ T1 Kasten (601, 611) 207 D 2.4 (601.361, 601.367, 601.366, 601.362)"
[3]: https://catalogonuevo.icerbrakes.com/Producto/Details?idProducto=140405-113&utm_source=chatgpt.com "Product 140405-113 - Web Catalogo"
[4]: https://www.winparts.ie/drivetrain-suspension/shock-absorbers-coil-springs/coil-spring-leaf-springs/c470/spring-pack/p1190462.html?utm_source=chatgpt.com "Spring Pack | Winparts.ie - Coil spring & leaf springs"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6501-6600_ktype_dimension_mapping_final.tsv
- all_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后一个 PENDING Ktype `6934` 已拆分为 `602.361`、`602.366`、`602.362`、`602.367`、`602.363` 五个厢式车分支，并全部关联既有 T1 L1/L2/L3、H1/H2 尺寸组，不重复创建尺寸事实。相关目录资料支持这些车身代码及厢式车分支边界。([Partsouq][1])
* 已完成机械收尾检查：两个表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，尺寸和来源字段完整，无孤立尺寸组。
* 最终覆盖 100 个输入 Ktype，共 126 条 READY 映射、68 个被引用尺寸组，`PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：126
* PENDING 映射：0
* 完整 DIMENSION_GROUP：68
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6924	6924	Sedan	Volvo 740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
6925	6925	Sedan	Mercedes-Benz 170 D W136 I	W136	4	EU-MERCEDES-BENZ-170-D-W136-SEDAN-4D-01	HIGH	W136四门柴油三厢外廓。	READY
6926_prewar	6926	Sedan	Mercedes-Benz 170 V W136 I	W136	4	EU-MERCEDES-BENZ-170-V-W136-SEDAN-PREWAR-01	HIGH	战前四门三厢外廓分支。	READY
6926_postwar	6926	Sedan	Mercedes-Benz 170 V W136 I	W136	4	EU-MERCEDES-BENZ-170-V-W136-SEDAN-POSTWAR-01	HIGH	战后四门三厢外廓分支。	READY
6927	6927	Sedan	Mercedes-Benz 170 S W136 IV	W136	4	EU-MERCEDES-BENZ-170-S-W136-SEDAN-4D-01	HIGH	W136 IV四门三厢外廓。	READY
6928	6928	Sedan	Mercedes-Benz 170 S-D W136 VIII D	W136	4	EU-MERCEDES-BENZ-170-SD-W136-SEDAN-4D-01	HIGH	W136 VIII D四门柴油三厢外廓。	READY
6929	6929	Coupe	Mercedes-Benz 300 SL W198 I	W198	2	EU-MERCEDES-BENZ-300-SL-W198-GULLWING-COUPE-2D-01	HIGH	Gullwing双门轿跑外廓。	READY
6930	6930	Convertible	Mercedes-Benz 300 SL W198 II	W198	2	EU-MERCEDES-BENZ-300-SL-W198-ROADSTER-2D-01	HIGH	Roadster双门敞篷外廓。	READY
6931_swb_3dr	6931	SUV	Mercedes-Benz G-Class W460	460.337	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	HIGH	短轴三门Station Wagon外廓。	READY
6931_lwb_5dr	6931	SUV	Mercedes-Benz G-Class W460	460.338	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	HIGH	长轴五门Station Wagon外廓。	READY
6931_lwb_van	6931	Van	Mercedes-Benz G-Class W460	460.328	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	HIGH	长轴三门封闭Van外廓。	READY
6932	6932	MPV	Ford Galaxy II facelift	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6改款五门MPV外廓。	READY
6933_l1h1	6933	Van	Mercedes-Benz T1	601.361		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1H1厢式车分支。	READY
6933_l1h2	6933	Van	Mercedes-Benz T1	601.366		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1H2厢式车分支。	READY
6933_l2h1	6933	Van	Mercedes-Benz T1	601.362		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2H1厢式车分支。	READY
6933_l2h2	6933	Van	Mercedes-Benz T1	601.367		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2H2厢式车分支。	READY
6934_l1h1	6934	Van	Mercedes-Benz T1	602.361		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	HIGH	L1H1厢式车分支。	READY
6934_l1h2	6934	Van	Mercedes-Benz T1	602.366		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	HIGH	L1H2厢式车分支。	READY
6934_l2h1	6934	Van	Mercedes-Benz T1	602.362		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	HIGH	L2H1厢式车分支。	READY
6934_l2h2	6934	Van	Mercedes-Benz T1	602.367		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	HIGH	L2H2厢式车分支。	READY
6934_l3h1	6934	Van	Mercedes-Benz T1	602.363		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	HIGH	L3H1厢式车分支。	READY
6935_l1	6935	Pickup	Mercedes-Benz T1	602.321		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	短轴平台或底盘分支。	READY
6935_l3	6935	Pickup	Mercedes-Benz T1	602.323		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	长轴平台或底盘分支。	READY
6936_l1h1	6936	Van	Mercedes-Benz T1	602.461		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1H1厢式车分支。	READY
6936_l1h2	6936	Van	Mercedes-Benz T1	602.476		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1H2厢式车分支。	READY
6936_l2h1	6936	Van	Mercedes-Benz T1	602.462		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2H1厢式车分支。	READY
6936_l2h2	6936	Van	Mercedes-Benz T1	602.477		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2H2厢式车分支。	READY
6936_l3h1	6936	Van	Mercedes-Benz T1	602.463		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3H1厢式车分支。	READY
6937_l1	6937	MPV	Mercedes-Benz T1	602.371		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	短轴Bus外廓。	READY
6937_l3	6937	MPV	Mercedes-Benz T1	602.373		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	长轴Bus外廓。	READY
6938	6938	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7改款五门掀背外廓。	READY
6939	6939	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7改款五门掀背外廓。	READY
6941	6941	Sedan	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-SEDAN-2D-01	HIGH	13/60双门三厢外廓。	READY
6942	6942	Sedan	Triumph Herald 1200		2	EU-TRIUMPH-HERALD-1200-SEDAN-2D-01	HIGH	1200双门三厢外廓。	READY
6943	6943	Wagon	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-WAGON-2D-01	HIGH	13/60双门旅行车外廓。	READY
6944	6944	Convertible	Triumph Herald 13/60		2	EU-TRIUMPH-HERALD-13-60-CONVERTIBLE-2D-01	HIGH	13/60双门敞篷外廓。	READY
6945	6945	Sedan	Triumph 1300		4	EU-TRIUMPH-1300-SEDAN-4D-01	HIGH	Triumph 1300四门三厢外廓。	READY
6946	6946	Sedan	Triumph 1300		4	EU-TRIUMPH-1300-SEDAN-4D-01	HIGH	Triumph 1300四门三厢外廓。	READY
6947	6947	Convertible	Triumph Spitfire Mk I		2	EU-TRIUMPH-SPITFIRE-MK-I-CONVERTIBLE-2D-01	HIGH	Mk I双门敞篷外廓。	READY
6948	6948	Convertible	Triumph Spitfire Mk II		2	EU-TRIUMPH-SPITFIRE-MK-II-CONVERTIBLE-2D-01	HIGH	Mk II双门敞篷外廓。	READY
6949	6949	Convertible	Triumph Spitfire Mk III		2	EU-TRIUMPH-SPITFIRE-MK-III-CONVERTIBLE-2D-01	HIGH	Mk III双门敞篷外廓。	READY
6950	6950	Convertible	Triumph Spitfire Mk IV		2	EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	HIGH	Mk IV双门敞篷外廓。	READY
6951	6951	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7改款五门掀背外廓。	READY
6952	6952	Coupe	Triumph GT6 Mk I		2	EU-TRIUMPH-GT6-MK-I-COUPE-2D-01	HIGH	Mk I双门快背轿跑外廓。	READY
6953	6953	Coupe	Triumph GT6 Mk II		2	EU-TRIUMPH-GT6-MK-II-COUPE-2D-01	HIGH	Mk II双门快背轿跑外廓。	READY
6954	6954	Coupe	Triumph GT6 Mk III		2	EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	HIGH	Mk III双门快背轿跑外廓。	READY
6955	6955	Coupe	Triumph GT6 Mk III		2	EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	HIGH	Mk III双门快背轿跑外廓。	READY
6957	6957	Sedan	Triumph Vitesse 2-Litre Mk I		2	EU-TRIUMPH-VITESSE-2L-MK-I-SEDAN-2D-01	HIGH	Mk I双门三厢外廓。	READY
6958	6958	Sedan	Triumph Vitesse 2-Litre Mk II		2	EU-TRIUMPH-VITESSE-2L-MK-II-SEDAN-2D-01	HIGH	Mk II双门三厢外廓。	READY
6959	6959	Convertible	Triumph Vitesse 2-Litre Mk I		2	EU-TRIUMPH-VITESSE-2L-MK-I-CONVERTIBLE-2D-01	HIGH	Mk I双门敞篷外廓。	READY
6960	6960	Convertible	Triumph Vitesse 2-Litre Mk II		2	EU-TRIUMPH-VITESSE-2L-MK-II-CONVERTIBLE-2D-01	HIGH	Mk II双门敞篷外廓。	READY
6961_mki	6961	Sedan	Triumph 2000 Mk I		4	EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk I短车身分支。	READY
6961_mkii	6961	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk II长车身分支。	READY
6963	6963	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II大型四门三厢共用外廓。	READY
6964	6964	Sedan	Triumph 2000 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II大型四门三厢共用外廓。	READY
6965_mki	6965	Wagon	Triumph 2000 Mk I		5	EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	MEDIUM	生产区间覆盖Mk I旅行车分支。	READY
6965_mkii_pre74	6965	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	MEDIUM	生产区间覆盖Mk II早期旅行车分支。	READY
6965_mkii_post74	6965	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	MEDIUM	生产区间覆盖Mk II后期旅行车分支。	READY
6966_pre74	6966	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	HIGH	Mk II早期旅行车分支。	READY
6966_post74	6966	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车分支。	READY
6967_pre74	6967	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	HIGH	Mk II早期旅行车分支。	READY
6967_post74	6967	Wagon	Triumph 2000 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车分支。	READY
6968	6968	Convertible	Triumph TR2		2	EU-TRIUMPH-TR2-CONVERTIBLE-2D-01	HIGH	TR2双门敞篷外廓。	READY
6969	6969	Convertible	Triumph TR3		2	EU-TRIUMPH-TR3-CONVERTIBLE-2D-01	HIGH	TR3双门敞篷外廓。	READY
6970	6970	Convertible	Triumph TR3A		2	EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	HIGH	TR3A双门敞篷外廓。	READY
6971	6971	Convertible	Triumph TR3A		2	EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	HIGH	TR3A双门敞篷外廓。	READY
6972	6972	Convertible	Triumph TR4		2	EU-TRIUMPH-TR4-CONVERTIBLE-2D-01	HIGH	TR4双门敞篷外廓。	READY
6973	6973	Convertible	Triumph TR4A		2	EU-TRIUMPH-TR4A-CONVERTIBLE-2D-01	HIGH	TR4A双门敞篷外廓。	READY
6974	6974	Convertible	Triumph TR5		2	EU-TRIUMPH-TR5-CONVERTIBLE-2D-01	HIGH	TR5双门敞篷外廓。	READY
6976	6976	Convertible	Triumph TR6		2	EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	HIGH	TR6双门敞篷外廓。	READY
6977	6977	Convertible	Triumph Stag		2	EU-TRIUMPH-STAG-CONVERTIBLE-2D-01	HIGH	Stag双门敞篷外廓。	READY
6978_prefl	6978	SUV	Honda CR-V IV	RM1	5	EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	HIGH	改款前五门SUV外廓。	READY
6978_facelift	6978	SUV	Honda CR-V IV	RM1	5	EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
6979	6979	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7改款五门掀背外廓。	READY
6981	6981	Hatchback	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	HIGH	BA7改款五门掀背外廓。	READY
6982	6982	Convertible	Triumph TR8		2	EU-TRIUMPH-TR8-CONVERTIBLE-2D-01	HIGH	TR8双门敞篷外廓。	READY
6983_mki	6983	Sedan	Triumph 2.5 PI Mk I		4	EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk I短车身分支。	READY
6983_mkii	6983	Sedan	Triumph 2.5 PI Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	MEDIUM	生产区间覆盖Mk II长车身分支。	READY
6984_mki	6984	Wagon	Triumph 2.5 PI Mk I		5	EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	MEDIUM	生产区间覆盖Mk I旅行车分支。	READY
6984_mkii_pre74	6984	Wagon	Triumph 2.5 PI Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	MEDIUM	生产区间覆盖Mk II早期旅行车分支。	READY
6984_mkii_post74	6984	Wagon	Triumph 2.5 PI Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	MEDIUM	生产区间覆盖Mk II后期旅行车分支。	READY
6985	6985	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo四门三厢外廓。	READY
6986	6986	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo四门三厢外廓。	READY
6987	6987	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo四门三厢外廓。	READY
6988	6988	Sedan	Triumph Toledo		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	HIGH	Toledo四门三厢外廓。	READY
6989	6989	Sedan	Triumph 1500		4	EU-TRIUMPH-1500-SEDAN-4D-01	MEDIUM	输入驱动字段不一致，按1500四门外廓处理。	READY
6990	6990	Sedan	Triumph 1500		4	EU-TRIUMPH-1500-SEDAN-4D-01	MEDIUM	输入驱动字段不一致，按1500四门外廓处理。	READY
6991	6991	Sedan	Triumph 1500 TC		4	EU-TRIUMPH-TOLEDO-SEDAN-4D-01	MEDIUM	1500 TC长车身四门三厢外廓。	READY
6992	6992	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite四门三厢共用外廓。	READY
6994	6994	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite四门三厢共用外廓。	READY
6995	6995	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite四门三厢共用外廓。	READY
6996	6996	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite四门三厢共用外廓。	READY
6997	6997	Sedan	Triumph Dolomite		4	EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	HIGH	Dolomite四门三厢共用外廓。	READY
6998	6998	Sedan	Triumph 2500 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II大型四门三厢共用外廓。	READY
6999	6999	Sedan	Triumph 2500 Mk II		4	EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	HIGH	Mk II大型四门三厢共用外廓。	READY
7000	7000	Wagon	Triumph 2500 Mk II		5	EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	HIGH	Mk II后期旅行车外廓。	READY
7001	7001	Wagon	Triumph 2500 Mk II		5	EU-TRIUMPH-2500S-MK-II-WAGON-5D-01	HIGH	2500 S旅行车低车身分支。	READY
7002	7002	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7改款五门旅行车外廓。	READY
7003	7003	MPV	Mercedes-Benz R-Class W251 facelift	W251	5	EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	HIGH	W251改款五门MPV外廓。	READY
7004	7004	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	MEDIUM	Typ 612双门敞篷外廓。	READY
7005	7005	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	MEDIUM	Typ 612双门敞篷外廓。	READY
7006	7006	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7007	7007	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7008	7008	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7009	7009	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7010	7010	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7011	7011	Convertible	Glas 1300-1700 GT		2	EU-GLAS-GT-CONVERTIBLE-2D-01	HIGH	Glas GT双门敞篷外廓。	READY
7012	7012	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7013	7013	Sedan	Glas Typ 612	612	2	EU-GLAS-TYP-612-SEDAN-2D-01	HIGH	Typ 612双门三厢外廓。	READY
7014	7014	Convertible	Glas Typ 612	612	2	EU-GLAS-TYP-612-CONVERTIBLE-2D-01	HIGH	Typ 612双门敞篷外廓。	READY
7015	7015	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7改款五门旅行车外廓。	READY
7016_early	7016	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-EARLY-01	HIGH	生产区间覆盖E24早期短车身。	READY
7016_late	7016	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-LATE-01	HIGH	生产区间覆盖E24后期长车身。	READY
7017	7017	Sedan	Glas 1700		4	EU-GLAS-1700-SEDAN-4D-01	HIGH	Glas 1700四门三厢外廓。	READY
7018	7018	Convertible	Glas 1300-1700 GT		2	EU-GLAS-GT-CONVERTIBLE-2D-01	HIGH	Glas GT双门敞篷外廓。	READY
7019	7019	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7改款五门旅行车外廓。	READY
7020	7020	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7改款五门旅行车外廓。	READY
7021	7021	Wagon	Ford Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	BA7改款五门旅行车外廓。	READY
7022	7022	Coupe	Glas 2600-3000 V8		2	EU-GLAS-V8-COUPE-2D-01	HIGH	输入车身形式修正为双门轿跑。	READY
7024	7024	Coupe	Glas 2600-3000 V8		2	EU-GLAS-V8-COUPE-2D-01	HIGH	输入车身形式修正为双门轿跑。	READY
7025	7025	Sedan	Goggomobil T/TA		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	MEDIUM	T/TA双门三厢外廓。	READY
7026	7026	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	MEDIUM	TS系列双门轿跑外廓。	READY
7027	7027	Sedan	Volkswagen Passat B7	362	4	EU-VW-PASSAT-B7-362-SEDAN-01	HIGH	B7 362四门三厢外廓。	READY
7028	7028	Coupe	BMW 6 Series E24	E24	2	EU-BMW-6-E24-COUPE-M635I-LATE-01	HIGH	M 635 CSi后期双门轿跑外廓。	READY
7029	7029	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	HIGH	TS系列双门轿跑外廓。	READY
7030	7030	Coupe	Goggomobil TS		2	EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	MEDIUM	TS系列双门轿跑外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6501-6600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430	Auto-Data Volvo 740 (744) specifications	https://www.auto-data.net/en/volvo-740-model-930
EU-MERCEDES-BENZ-170-D-W136-SEDAN-4D-01	4285	1580	1610	Automobile-Catalog Mercedes-Benz 170 D W136 profile	https://www.automobile-catalog.com/car/1949/31565/mercedes-benz_170_d_w_136_i_d.html
EU-MERCEDES-BENZ-170-V-W136-SEDAN-PREWAR-01	4270	1570	1560	Automobile-Catalog Mercedes-Benz 170 V pre-war profile	https://www.automobile-catalog.com/car/1939/1459190/mercedes-benz_170_v.html
EU-MERCEDES-BENZ-170-V-W136-SEDAN-POSTWAR-01	4285	1580	1610	Automobile-Catalog Mercedes-Benz 170 V post-war profile	https://www.automobile-catalog.com/car/1950/1459205/mercedes-benz_170_v_w_136_i.html
EU-MERCEDES-BENZ-170-S-W136-SEDAN-4D-01	4455	1684	1610	Automobile-Catalog Mercedes-Benz 170 S W136 profile	https://www.automobile-catalog.com/car/1950/1459325/mercedes-benz_170_s_w_136_iv.html
EU-MERCEDES-BENZ-170-SD-W136-SEDAN-4D-01	4450	1685	1590	Automobile-Catalog Mercedes-Benz 170 S-D W136 profile	https://www.automobile-catalog.com/car/1954/1459385/mercedes-benz_170_s-d_w_136_viii_d.html
EU-MERCEDES-BENZ-300-SL-W198-GULLWING-COUPE-2D-01	4520	1790	1300	Automobile-Catalog Mercedes-Benz 300 SL Gullwing profile	https://www.automobile-catalog.com/car/1954/1460990/mercedes-benz_300_sl_opt__3_25_axle.html
EU-MERCEDES-BENZ-300-SL-W198-ROADSTER-2D-01	4570	1790	1300	Automobile-Catalog Mercedes-Benz 300 SL Roadster profile	https://www.automobile-catalog.com/car/1958/1461020/mercedes-benz_300_sl_roadster.html
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925	Mercedes-Benz Public Archive 250 GD short wheelbase 1987-1992	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-short-wheelbase-1987---1992.xhtml?oid=190007636
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920	Mercedes-Benz Public Archive 250 GD long wheelbase 1987-1992	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-long-wheelbase-1987---1992.xhtml?oid=190007637
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764	Ford Galaxy 2011 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2016/09/Ford-Galaxy-2011-UK.pdf
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	4855	2000	2455	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	5235	2000	2525	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	5885	2000	2240	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	4855	2000	2170	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	5885	2000	2240	Drom Mercedes-Benz T1 dimensions table	https://www.drom.ru/catalog/lcv/mercedes-benz/t1/specs/dimensions/
EU-FORD-MONDEO-IV-BA7-HATCHBACK-FACELIFT-01	4784	1886	1500	Automobile-Catalog Ford Mondeo 5-door 1.6 EcoBoost 160 profile	https://www.automobile-catalog.com/car/2011/1594655/ford_mondeo_5-dr_1_6_ecoboost_160_trend.html
EU-TRIUMPH-HERALD-13-60-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Saloon profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=42
EU-TRIUMPH-HERALD-1200-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 1200 Saloon profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=27
EU-TRIUMPH-HERALD-13-60-WAGON-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Estate profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=43
EU-TRIUMPH-HERALD-13-60-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Herald 13/60 Convertible profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=30
EU-TRIUMPH-1300-SEDAN-4D-01	3937	1568	1372	Triumph Sports Six Club Triumph 1300 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=34
EU-TRIUMPH-SPITFIRE-MK-I-CONVERTIBLE-2D-01	3683	1448	1207	Triumph Sports Six Club Spitfire Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=24
EU-TRIUMPH-SPITFIRE-MK-II-CONVERTIBLE-2D-01	3683	1448	1207	Triumph Sports Six Club Spitfire Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=24
EU-TRIUMPH-SPITFIRE-MK-III-CONVERTIBLE-2D-01	3734	1448	1207	Triumph Sports Six Club Spitfire Mk III profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=23
EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	3790	1480	1210	CyprusCar Triumph Spitfire Mk IV specifications	https://www.cypruscar.com/triumph-spitfire-mk-iv-year-1974-3-cpma133mo51675tr44375.html
EU-TRIUMPH-GT6-MK-I-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=19
EU-TRIUMPH-GT6-MK-II-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk I/II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=19
EU-TRIUMPH-GT6-MK-III-COUPE-2D-01	3785	1448	1194	Triumph Sports Six Club GT6 Mk III profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=20
EU-TRIUMPH-VITESSE-2L-MK-I-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk I profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=33
EU-TRIUMPH-VITESSE-2L-MK-II-SEDAN-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=11
EU-TRIUMPH-VITESSE-2L-MK-I-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk I profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=33
EU-TRIUMPH-VITESSE-2L-MK-II-CONVERTIBLE-2D-01	3886	1524	1321	Triumph Sports Six Club Vitesse 2-Litre Mk II profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=11
EU-TRIUMPH-2000-2500-MK-I-SEDAN-4D-01	4410	1650	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-II-SEDAN-4D-01	4629	1651	1422	Triumph Sports Six Club Triumph 2000 and 2500 profiles	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=38;https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=39
EU-TRIUMPH-2000-2500-MK-I-WAGON-5D-01	4410	1650	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-II-WAGON-PRE74-5D-01	4500	1690	1420	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-2000-2500-MK-II-WAGON-POST74-5D-01	4530	1710	1440	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-TRIUMPH-TR2-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR2 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=15
EU-TRIUMPH-TR3-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR3/3A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=16
EU-TRIUMPH-TR3A-CONVERTIBLE-2D-01	3835	1410	1270	Triumph Sports Six Club TR3/3A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=16
EU-TRIUMPH-TR4-CONVERTIBLE-2D-01	3962	1473	1207	Triumph Sports Six Club TR4/4A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=17
EU-TRIUMPH-TR4A-CONVERTIBLE-2D-01	3962	1473	1207	Triumph Sports Six Club TR4/4A profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=17
EU-TRIUMPH-TR5-CONVERTIBLE-2D-01	3900	1473	1270	Triumph Sports Six Club TR5 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=18
EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	3950	1550	1270	Triumph Sports Six Club TR6 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=6
EU-TRIUMPH-STAG-CONVERTIBLE-2D-01	4413	1613	1257	Triumph Sports Six Club Stag profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=35
EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	4570	1820	1685	Honda Europe 2012 CR-V press kit;Auto-Data Honda CR-V IV dimensions	https://hondanews.eu/eu/lv/cars/media/pressreleases/34671/cr-v;https://www.auto-data.net/en/honda-cr-v-model-1317
EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	4605	1820	1685	Honda Europe 2015 CR-V specifications;Drive.place Honda CR-V IV facelift technical data	https://hondanews.eu/be/fr/cars/media/pressreleases/41825/honda-cr-v-2015;https://honda.drive.place/cr_v/iv_res/group_offroad_5d/583136
EU-TRIUMPH-TR8-CONVERTIBLE-2D-01	4067	1681	1267	Triumph Sports Six Club TR7/8 profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=22
EU-TRIUMPH-TOLEDO-SEDAN-4D-01	4125	1588	1372	Triumph Sports Six Club Toledo/1500TC profile	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=36
EU-TRIUMPH-1500-SEDAN-4D-01	4115	1568	1372	Carfolio Triumph 1500 and 1500 TC profiles	https://www.carfolio.com/triumph-1500-690910;https://www.carfolio.com/triumph-1500-tc-55880
EU-TRIUMPH-DOLOMITE-SEDAN-4D-01	4125	1588	1372	Triumph Sports Six Club Dolomite profiles	https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=37;https://www.tssc.org.uk/tssc/cars_final.asp?model_ID=8
EU-TRIUMPH-2500S-MK-II-WAGON-5D-01	4530	1710	1410	Triumph 2000 Register technical specifications	https://triumph2000register.co.uk/the-cars/technical-specifications/
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Automobile-Catalog Ford Mondeo Estate 1.6 EcoBoost 160 profile	https://www.automobile-catalog.com/car/2011/1595570/ford_mondeo_5-dr_1_6_ecoboost_160_trend.html
EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	4922	1922	1674	Auto-Data Mercedes-Benz R-Class dimensions	https://www.auto-data.net/en/mercedes-benz-r-class-model-1389
EU-GLAS-TYP-612-CONVERTIBLE-2D-01	3835	1500	1355	Automobile-Catalog Glas Typ 612 Cabriolet profiles	https://www.automobile-catalog.com/car/1965/1017410/glas_s_1204_cabriolet.html;https://www.automobile-catalog.com/car/1967/1017665/glas_1304_cabriolet.html
EU-GLAS-TYP-612-SEDAN-2D-01	3835	1500	1355	Automobile-Catalog Glas Typ 612 Limousine profiles	https://www.automobile-catalog.com/car/1963/1017455/glas_s_1004.html;https://www.automobile-catalog.com/make/glas/1004_1204_1304/1004_1204_1304_limousine/1966.html
EU-GLAS-GT-CONVERTIBLE-2D-01	4050	1550	1350	Automobile-Catalog Glas 1300-1700 GT Cabriolet profiles	https://www.automobile-catalog.com/car/1967/1017875/glas_1700_gt_cabriolet.html;https://www.automobile-catalog.com/make/glas/1300_1700_gt/1300_1700_gt_cabriolet/1964.html
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365	NetCarShow BMW 635 CSi 1978 specifications	https://www.netcarshow.com/bmw/1978-635csi/
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365	Carfolio 1986 BMW 635 CSi specifications	https://www.carfolio.com/bmw-635-csi-31240
EU-GLAS-1700-SEDAN-4D-01	4415	1610	1390	Automobile-Catalog Glas 1700 profile	https://www.automobile-catalog.com/car/1964/36980/glas_1700.html
EU-GLAS-V8-COUPE-2D-01	4600	1750	1380	Automobile-Catalog Glas 2600 and 3000 V8 profiles	https://www.automobile-catalog.com/car/1966/1017905/glas_2600_v8.html;https://www.automobile-catalog.com/car/1967/1017920/glas_3000_v8.html
EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	2900	1280	1310	Automobile-Catalog Goggomobil T 300 profile	https://www.automobile-catalog.com/car/1957/1017080/goggomobil_t_300.html
EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	3035	1370	1235	Automobile-Catalog Goggomobil TS profiles	https://www.automobile-catalog.com/car/1957/1017125/goggomobil_ts_300.html;https://www.automobile-catalog.com/make/goggomobil/ts_250_300_400/ts_250_300_400/1963.html
EU-VW-PASSAT-B7-362-SEDAN-01	4769	1820	1470	Volkswagen Newsroom Passat B7 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355	Automobile-Catalog 1988 BMW M 635 CSi profile	https://www.automobile-catalog.com/car/1988/264245/bmw_m_635_csi.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6501-6600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=129628928&q=&srsltid=AfmBOoorrZp84vHsiYg72qhTpAYmyNCTdripNqIQZ3O8fwWAFX7YQt62&ssd=%24%2AKwGEsKGx0MGA__Pg9sG5qNzI6O_xgI-Cg5G-jcXD8P7z-s7tn5KL9vaAgIeChIfX1M-OydPxzZXEkNXDu_6VnJPblYqD3djLhJuS1pSNiIvd2YDIwdXZ9sySxM3bk8Pb3J2U2tOQ1cPLhoWDh4eVnJCcgt-MlZKdlNrbkNXDzJSbktLYlYqQ3dbElJuSx9WVipDcw4AAAAAA1YeCGA%3D%3D%24&vid=&utm_source=chatgpt.com "Mercedes-Benz 307 D/308 D Standard 602.361 Parts Catalogs"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6501-6600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6501-6600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8295 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2581 行）

- 尺寸冲突协调：
  - EU-TRIUMPH-TR6-CONVERTIBLE-2D-01 -> EU-TRIUMPH-TR6-CONVERTIBLE-2D-02：3937x1473x1270 与 3950x1550x1270，创建新尺寸组
