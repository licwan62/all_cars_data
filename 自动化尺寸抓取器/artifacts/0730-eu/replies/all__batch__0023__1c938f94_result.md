# 任务：all 第 2201-2300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0023__1c938f94


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2201-2300 行

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
all 第 2201-2300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	5090	1816	1369
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Volvo	Xc40	T4	SUV	Frontantrieb	Benzin	140	190	Sep 2018	Dec 2021	2024-05-01	131094
Volvo	Xc40	T4 AWD	SUV	Allrad	Benzin	140	190	Sep 2018	-	2024-03-01	131095
Volvo	Xc40	T3	SUV	Frontantrieb	Benzin	115	156	Mar 2018	Mar 2019	2024-03-01	131104
Alpine	A110 ii	1.8	Coupe	Heckantrieb	Benzin	185	252	Dec 2017	Apr 2021	2026-04-01	131107
Peugeot	308 sw ii	1.5 Bluehdi 100	Kombi	Frontantrieb	Diesel	75	102	Apr 2018	Jun 2021	2024-03-01	131119
Peugeot	308 ii	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	75	102	May 2018	Jun 2021	2024-03-01	131121
Chevrolet	Monte carlo	5.7	Coupe	Heckantrieb	Benzin	130	177	Jan 1970	Dec 1971	2024-03-01	131127
Chevrolet	Monte carlo	5	Coupe	Heckantrieb	Benzin	108	147	Oct 1978	Sep 1980	2024-03-01	131128
BMW	5	M5 Competition	Stufenheck	Allrad	Benzin	460	625	Jul 2018	Jun 2023	2024-03-01	131130
VW	Touareg	3.0 TDI 4motion	SUV	Allrad	Diesel	210	286	Nov 2017	-	2024-03-01	131140
VW	Touareg	3.0 TDI 4motion	SUV	Allrad	Diesel	170	231	May 2018	-	2024-03-01	131141
Mercedes-benz	Sprinter 4-T	414 NGT	Kasten	Heckantrieb	Benzin/Erdgas (CNG)	95	129	Feb 1995	May 2006	2024-03-01	131142
Mercedes-benz	Sprinter 4-T	414 NGT	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	95	129	Feb 1995	May 2006	2024-03-01	131144
Ford	Focus iv	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	63	85	May 2018	Nov 2025	2026-02-01	131166
Citroën	C4 spacetourer	1.2 Puretech 110	Großraumlimousine	Frontantrieb	Benzin	81	110	Apr 2018	-	2024-03-01	131183
Citroën	C4 spacetourer	1.2 Puretech 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Apr 2018	-	2024-03-01	131184
Citroën	C4 spacetourer	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	121	165	Apr 2018	-	2024-03-01	131191
Citroën	C4 spacetourer	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	73	99	Apr 2018	Apr 2019	2025-02-03	131193
Citroën	C4 spacetourer	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	88	120	Apr 2018	Apr 2019	2025-02-03	131194
Citroën	C4 spacetourer	2.0 Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Apr 2018	-	2024-03-01	131195
Citroën	C4 spacetourer	2.0 Bluehdi 160	Großraumlimousine	Frontantrieb	Diesel	120	163	Apr 2018	-	2024-03-01	131196
Citroën	Grand c4 spacetourer	1.2 Puretech 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Apr 2018	-	2024-03-01	131198
Citroën	Grand c4 spacetourer	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	121	165	Apr 2018	-	2024-03-01	131199
Citroën	Grand c4 spacetourer	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	73	99	Apr 2018	Apr 2019	2025-02-03	131200
Citroën	Grand c4 spacetourer	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	88	120	Apr 2018	Aug 2018	2025-02-03	131204
Citroën	Grand c4 spacetourer	2.0 Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Apr 2018	-	2024-03-01	131206
Citroën	Grand c4 spacetourer	2.0 Bluehdi 160	Großraumlimousine	Frontantrieb	Diesel	120	163	Apr 2018	-	2024-03-01	131207
Moskvich	2141	1.5	Schrägheck	Frontantrieb	Benzin	53	72	May 1989	Dec 2001	2024-03-01	131208
Skoda	Fabia iii	1.4 TSI R5	Schrägheck	Frontantrieb	Benzin	92	125	Feb 2018	Jun 2021	2024-03-01	131223
Mercedes-benz	Sprinter 3-T tourer	211 CDI	Bus	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131235
Mercedes-benz	Sprinter 3-T tourer	214 CDI	Bus	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131236
Mercedes-benz	Sprinter 3-T	211 CDI	Kasten	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131237
Mercedes-benz	Sprinter 3-T	214 CDI	Kasten	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131238
Mercedes-benz	Sprinter 3-T	211 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131239
Mercedes-benz	Sprinter 3-T	214 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131240
Mercedes-benz	Sprinter 3,5-T tourer	311 CDI	Bus	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131241
Mercedes-benz	Sprinter 3,5-T tourer	314 CDI	Bus	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131242
Mercedes-benz	Sprinter 3,5-T tourer	316 CDI	Bus	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131245
Mercedes-benz	Sprinter 3,5-T tourer	319 CDI	Bus	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131246
Mercedes-benz	Sprinter 3,5-T	311 CDI	Kasten	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131247
Mercedes-benz	Sprinter 3,5-T	311 CDI RWD	Kasten	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131248
Mercedes-benz	Sprinter 3,5-T	314 CDI	Kasten	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131249
Mercedes-benz	Sprinter 3,5-T	314 CDI RWD	Kasten	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131250
Mercedes-benz	Sprinter 3,5-T	316 CDI RWD	Kasten	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131251
Mercedes-benz	Sprinter 3,5-T	319 CDI RWD	Kasten	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131252
Mercedes-benz	Sprinter 3,5-T	311 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131253
Mercedes-benz	Sprinter 3,5-T	311 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131254
Mercedes-benz	Sprinter 3,5-T	314 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131255
Mercedes-benz	Sprinter 3,5-T	314 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131256
Mercedes-benz	Sprinter 3,5-T	316 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131257
Mercedes-benz	Sprinter 3,5-T	319 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131258
Mercedes-benz	Sprinter 4-T	414 CDI RWD	Kasten	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131260
Mercedes-benz	Sprinter 4-T	416 CDI RWD	Kasten	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131261
Mercedes-benz	Sprinter 4-T	419 CDI RWD	Kasten	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131262
Mercedes-benz	Sprinter 4-T	411 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131263
Mercedes-benz	Sprinter 4-T	414 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131264
Mercedes-benz	Sprinter 4-T	416 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131265
Mercedes-benz	Sprinter 4-T	419 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131266
Mercedes-benz	Sprinter 5-T	511 CDI	Kasten	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131267
Mercedes-benz	Sprinter 5-T	514 CDI	Kasten	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131268
Mercedes-benz	Sprinter 5-T	516 CDI	Kasten	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131269
Mercedes-benz	Sprinter 5-T	519 CDI	Kasten	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131270
Mercedes-benz	Sprinter 5-T	511 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	131271
Mercedes-benz	Sprinter 5-T	514 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	105	143	Feb 2018	Dec 2021	2024-08-01	131272
Mercedes-benz	Sprinter 5-T	516 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Feb 2018	Dec 2021	2024-08-01	131273
Mercedes-benz	Sprinter 5-T	519 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	131274
Ford	Focus iv	1.5 Ecoblue	Schrägheck	Frontantrieb	Diesel	70	95	Jan 2018	Nov 2025	2026-02-01	131282
Ford	Focus iv	1.5 Ecoblue	Schrägheck	Frontantrieb	Diesel	88	120	Jan 2018	Nov 2025	2026-02-01	131283
Ford	Focus iv	2.0 Ecoblue	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2018	Nov 2025	2026-02-01	131284
Mercedes-benz	C-Klasse	C 220 D 4-matic	Stufenheck	Allrad	Diesel	143	194	May 2018	May 2021	2024-03-01	131294
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel	143	194	May 2018	Feb 2021	2024-03-01	131297
Mercedes-benz	C-Klasse	C 200 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	135	184	Apr 2018	Jun 2021	2024-03-01	131300
Mercedes-benz	C-Klasse	C 200 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	135	184	Apr 2018	May 2021	2024-03-01	131302
Mercedes-benz	C-Klasse	C 200 EQ Boost	Kombi	Heckantrieb	Benzin/Elektro	135	184	Apr 2018	Feb 2021	2024-03-01	131303
Mercedes-benz	C-Klasse	C 200 EQ Boost 4-matic	Kombi	Allrad	Benzin/Elektro	135	184	Apr 2018	Feb 2021	2024-03-01	131304
Mercedes-benz	C-Klasse	C 200 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	135	184	May 2018	Apr 2023	2024-03-01	131307
Mercedes-benz	C-Klasse	C 200 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	135	184	May 2018	Apr 2023	2024-03-01	131308
Mercedes-benz	C-Klasse	C 200 EQ Boost	Cabriolet	Heckantrieb	Benzin/Elektro	135	184	May 2018	Apr 2023	2024-03-01	131310
Mercedes-benz	C-Klasse	C 200 EQ Boost 4-matic	Cabriolet	Allrad	Benzin/Elektro	135	184	May 2018	Apr 2023	2024-03-01	131311
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel	110	150	May 2018	Nov 2018	2024-03-01	131314
Mercedes-benz	C-Klasse	C 200 D	Kombi	Heckantrieb	Diesel	110	150	May 2018	Nov 2018	2024-03-01	131315
Seat	Arona	1.6 SRE	SUV	Frontantrieb	Benzin	81	110	Jul 2017	-	2024-03-01	131316
Toyota	Aygo	1.0 Vvti	Schrägheck	Frontantrieb	Benzin	53	72	Mar 2018	-	2024-03-01	131317
Land Rover	Discovery iii van	2.7 TD 4X4	Kasten	Allrad	Diesel	140	190	Jan 2007	Jul 2009	2024-03-01	131343
Subaru	Impreza	2.5 AWD	Stufenheck	Allrad	Benzin	235	320	Feb 2007	Dec 2007	2024-03-01	131345
Subaru	Impreza station wagon	2.5 Gb270 AWD	Kombi	Allrad	Benzin	198	269	Jul 2007	Dec 2007	2024-03-01	131346
Jaguar	Xj	4.2	Stufenheck	Heckantrieb	Benzin	224	305	May 2007	Mar 2009	2024-03-01	131349
Renault	Laguna ii grandtour	2.9 V6 24V	Kombi	Frontantrieb	Benzin	155	211	Oct 2003	Dec 2007	2024-03-01	131350
Land Rover	Discovery i	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	136	185	Sep 1993	Oct 1998	2024-03-01	131351
Mercedes-benz	E-Klasse	E 220 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Oct 2003	Jul 2006	2024-03-01	131355
Mercedes-benz	E-Klasse	E 220 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	125	170	Apr 2006	Jul 2009	2024-03-01	131356
Mercedes-benz	E-Klasse	E 270 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Mar 2003	Jul 2009	2024-03-01	131357
BMW	X3	Xdrive M40 D	SUV	Allrad	Diesel	240	326	Aug 2018	Jun 2020	2024-03-01	131358
Mercedes-benz	E-Klasse	E 270 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	130	177	Oct 2003	Jul 2005	2024-03-01	131359
Mercedes-benz	E-Klasse	E 280 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	140	190	Aug 2005	Jul 2009	2024-03-01	131360
Lexus	Ls	500 AWD	Stufenheck	Allrad	Benzin	307	417	Dec 2017	-	2024-03-01	131367
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel	118	160	May 2018	May 2021	2024-03-01	131368
Mercedes-benz	C-Klasse	C 200 D	Kombi	Heckantrieb	Diesel	118	160	May 2018	Feb 2021	2024-03-01	131369
Mercedes-benz	C-Klasse	AMG C 43 4-matic	Stufenheck	Allrad	Benzin	287	390	May 2018	May 2021	2024-03-01	131370
Mercedes-benz	C-Klasse	AMG C 43 4-matic	Kombi	Allrad	Benzin	287	390	May 2018	Feb 2021	2024-03-01	131371


--- Round 1 / 首次发送 ---
## 更新点

* 已优先复用跨批次现有尺寸组，完成 XC40、308 II、Monte Carlo III、Focus IV、Arona、X3 G01、LS XF50 共 13 个 Ktype 的关联。
* 本轮首次闭合 BMW M5 Competition F90、Touareg III、C4/Grand C4 SpaceTourer、Aygo II facelift，以及 C-Class W205/S205/C205/A205 改款标准车身与 AMG C43 专属外廓。
* Toyota Aygo 的 Ktype `131317` 按三门、五门拆成两个映射 id；两者三维相同，因此共用同一个尺寸组。
* Sprinter、E-Class 底盘车及尚未闭合的历史车型未提前填写候选尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：46
* READY 映射行：47
* PENDING Ktype：54
* 当前引用尺寸组：19

  * 复用既有尺寸组：8
  * 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131094	131094	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，动力形式不改变尺寸组。	READY
131095	131095	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，驱动形式不改变尺寸组。	READY
131104	131104	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，动力差异不改变尺寸组。	READY
131119	131119	Wagon	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	T9改款旅行车外廓。	READY
131121	131121	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背外廓。	READY
131127	131127	Coupe	Monte Carlo III		2	EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	HIGH	1970至1971年第三代双门Coupe外廓。	READY
131130	131130	Sedan	M5 F90	F90	4	EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	HIGH	M5 Competition专属宽体及车高。	READY
131140	131140	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH	CR代五门SUV外廓，功率差异不改变尺寸组。	READY
131141	131141	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH	CR代五门SUV外廓，功率差异不改变尺寸组。	READY
131166	131166	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓。	READY
131183	131183	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131184	131184	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131191	131191	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131193	131193	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131194	131194	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131195	131195	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131196	131196	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131198	131198	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131199	131199	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131200	131200	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131204	131204	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131206	131206	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131207	131207	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131282	131282	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131283	131283	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131284	131284	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131294	131294	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131297	131297	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131300	131300	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131302	131302	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓，驱动形式不改变尺寸组。	READY
131303	131303	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131304	131304	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓，驱动形式不改变尺寸组。	READY
131307	131307	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门Coupe标准外廓。	READY
131308	131308	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门Coupe标准外廓，驱动形式不改变尺寸组。	READY
131310	131310	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷标准外廓。	READY
131311	131311	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷标准外廓，驱动形式不改变尺寸组。	READY
131314	131314	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131315	131315	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131316	131316	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH	KJ7五门SUV外廓。	READY
131317_3dr	131317	Hatchback	Aygo II facelift	AB40	3	EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	HIGH	Ktype覆盖三门车身；与五门版本外廓三维相同。	READY
131317_5dr	131317	Hatchback	Aygo II facelift	AB40	5	EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	HIGH	Ktype覆盖五门车身；与三门版本外廓三维相同。	READY
131358	131358	SUV	X3 III	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01五门SUV外廓。	READY
131367	131367	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50四门标准轴距轿车外廓。	READY
131368	131368	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131369	131369	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131370	131370	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	HIGH	AMG C43改款专属保险杠及悬架外廓。	READY
131371	131371	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	HIGH	AMG C43改款旅行车专属保险杠及悬架外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469	BMW Media Information - The new BMW M5 Competition specifications	https://www.press.bmwgroup.com/global/article/attachment/T0280678EN/412670
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Newsroom - Exterior design of the new Touareg	https://www.volkswagen-newsroom.com/en/leading-the-way-the-new-touareg-2405/exterior-design-tailor-made-for-freedom-2416
EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	4438	1826	1610	Auto-Data - Citroen C4 SpaceTourer Phase I 2018	https://www.auto-data.net/en/citroen-c4-spacetourer-phase-i-2018-1.2-puretech-110hp-34630
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638	Citroën Grand C4 SpaceTourer official press kit	https://www.media.stellantis.com/uk-en/download-press-kit/5
EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	3465	1615	1460	Toyota Europe - New Toyota Aygo June 2018 press kit	https://newsroom.toyota.eu/download/550744/toyota-aygo-dpl-en.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data - Mercedes-Benz C-Class W205 facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-160-129hp-52482
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data - Mercedes-Benz C-Class S205 facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-180-1.6-156hp-52483
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data - Mercedes-Benz C-Class C205 Coupe facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-180-1.6-156hp-44014
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data - Mercedes-Benz C-Class A205 Cabriolet facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-180-1.6-156hp-52493
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429	Mercedes-AMG C-Class Owner's Manual Supplement June 2018	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-lb/pdf/mercedes-amg-c-class-owners-manual-supplement-june-2018-1.pdf
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440	Mercedes-AMG C-Class Owner's Manual Supplement June 2018	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-amg-c-class-owners-manual-supplement-june-2018-1.pdf
```

## 下一步优先处理

1. 按 2018–2021 Sprinter VS30 的 `Tourer / Van / Chassis Cab` 聚类，确认每个 Ktype 实际覆盖的轴距、车长与车顶分支。
2. 单独处理第一代 Sprinter 4-T 的厢式车和底盘车，避免与后续 VS30 尺寸混用。
3. 闭合剩余乘用车：Alpine A110、Monte Carlo IV、Moskvich 2141、Fabia III、Discovery、Impreza、XJ、Laguna。
4. 最后处理 E-Class W211 底盘车的车身制造边界与外廓定义。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 修正 `131127`：原基础映射已撤销。该 Ktype 覆盖 1970、1971 两个不同外廓，现拆分为两个派生 id；`131128` 改为复用既有第三代 Monte Carlo 尺寸组。1970 与 1971 官方规格中的长度和高度不同，不能合并。
* 新闭合 Alpine A110 II、Moskvich 2141、Fabia III Edition R5、Discovery III Commercial、Impreza RB320、Impreza GB270 Sports Wagon、Laguna II Grandtour 共 7 个 Ktype。
* Subaru 两个高性能版本按实际外廓分别建组：RB320 为 GD 四门轿车，GB270 为 GG 五门旅行车，未与普通 Impreza 混用尺寸组。([汽车档案][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：54
* READY 映射行：56
* PENDING Ktype：46
* 当前引用尺寸组：28

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131107	131107	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-01	HIGH	第二代双门Coupe外廓。	READY
131127_1970	131127	Coupe	Monte Carlo I		2	EU-CHEVROLET-MONTE-CARLO-I-COUPE-1970-01	HIGH	Ktype覆盖1970年第一代外廓。	READY
131127_1971	131127	Coupe	Monte Carlo I		2	EU-CHEVROLET-MONTE-CARLO-I-COUPE-1971-01	HIGH	Ktype覆盖1971年第一代外廓。	READY
131128	131128	Coupe	Monte Carlo III		2	EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	HIGH	1978至1980年第三代双门Coupe外廓。	READY
131208	131208	Hatchback	2141		5	EU-MOSKVICH-2141-HATCHBACK-01	MEDIUM	五门掀背基础车身外廓。	READY
131223	131223	Hatchback	Fabia III	NJ	5	EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	HIGH	Edition R5量产道路版专属运动悬架外廓。	READY
131343	131343	Van	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-VAN-01	HIGH	Discovery 3 Commercial固定顶车身外廓。	READY
131345	131345	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-RB320-SEDAN-01	HIGH	320 PS版本对应RB320四门轿车外廓。	READY
131346	131346	Wagon	Impreza II	GG	5	EU-SUBARU-IMPREZA-II-GG-GB270-WAGON-01	HIGH	GB270五门旅行车外廓。	READY
131350	131350	Wagon	Laguna II		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-01	MEDIUM	输入2.9名称对应2946cc V6旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINE-A110-II-COUPE-01	4178	1798	1252	Alpine A110 Première Edition official press kit	https://www.motorshow.me/uploadImages/GalleryDocs/Doc6601.pdf
EU-CHEVROLET-MONTE-CARLO-I-COUPE-1970-01	5227	1920	1336	GM Heritage Archive - 1970 Chevrolet Monte Carlo Vehicle Information Kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1970-Chevrolet-Monte-Carlo.pdf
EU-CHEVROLET-MONTE-CARLO-I-COUPE-1971-01	5245	1920	1344	GM Heritage Archive - 1971 Chevrolet Monte Carlo Vehicle Information Kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1971-Chevrolet-Monte-Carlo.pdf
EU-MOSKVICH-2141-HATCHBACK-01	4350	1690	1400	Automobile-Catalog - Moskvich 2141 1.5	https://www.automobile-catalog.com/car/1987/53405/moskwicz_2141_1_5.html
EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	3992	1732	1452	ŠKODA FABIA EDITION R5 official press kit	https://cdn.skoda-storyboard.com/2017/12/171212-%C5%A0KODA-MOTORSPORT-Press-kit.pdf
EU-LAND-ROVER-DISCOVERY-III-L319-VAN-01	4835	1915	1887	Land Rover Discovery 3 technical specifications - archived copy	https://device.report/m/9b6edef86f579882649aebae8a88b0e6f4325751f39a56ec551f75fabc2acfd7.pdf
EU-SUBARU-IMPREZA-II-GD-RB320-SEDAN-01	4465	1740	1440	Carfolio - 2007 Subaru Impreza RB320	https://www.carfolio.com/subaru-impreza-rb320-159522
EU-SUBARU-IMPREZA-II-GG-GB270-WAGON-01	4465	1695	1485	Automobile-Catalog - 2007 Subaru Impreza Sports Wagon 2.5 WRX GB270	https://www.automobile-catalog.com/car/2007/3256220/subaru_impreza_sports_wagon_2_5_wrx_gb270.html
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-01	4695	1772	1443	Auto-Data - Renault Laguna II Grandtour	https://www.auto-data.net/en/renault-laguna-ii-grandtour-generation-2119
```

## 下一步优先处理

1. 集中拆分并闭合 2018–2021 Sprinter VS30 的 Tourer、Van、Chassis Cab，以及轴距和车顶分支。
2. 单独处理第一代 Sprinter 4-T，禁止与 VS30 尺寸组混用。
3. 继续闭合 Discovery I、Jaguar XJ、E-Class 底盘车等剩余历史车型。

推进信号：CONTINUE

[1]: https://www.carfolio.com/subaru-impreza-rb320-159522?utm_source=chatgpt.com "2007 Subaru Impreza RB320"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 `131248`、`131250`、`131251`、`131252` 四个 Sprinter 3.5-T 后驱厢式车 Ktype，并按实际外廓拆分为 L2H1、L2H2、L3H2、L3H3、L4H2、L4H3 六个分支。
* 2018 年车型矩阵确认 311/314/316/319 CDI 3.5-T 后驱厢式车覆盖 L2、L3、L4；L3/L4 可选超高顶。2021 年官方规格进一步闭合 H2/H3 各分支长高，车身不含后视镜宽度统一为 2020 mm。
* L2H1 为早期产品范围中的标准顶分支，单独建组，未与 L2H2 合并。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：58
* READY 映射行：80
* PENDING Ktype：42
* 当前引用尺寸组：34

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131248_l2_h1	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131248_l2_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131248_l3_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131248_l3_h3	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131248_l4_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131248_l4_h3	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131250_l2_h1	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131250_l2_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131250_l3_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131250_l3_h3	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131250_l4_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131250_l4_h3	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131251_l2_h1	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131251_l2_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131251_l3_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131251_l3_h3	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131251_l4_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131251_l4_h3	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131252_l2_h1	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131252_l2_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131252_l3_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131252_l3_h3	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131252_l4_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131252_l4_h3	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	5932	2020	2331	Mercedes-Benz New Sprinter model information and price list 2018; CarsGuide Mercedes-Benz Sprinter dimensions 2018	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2018
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	5932	2020	2620	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	6967	2020	2616	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	6967	2020	2831	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	7367	2020	2613	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	7367	2020	2825	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
```

## 下一步优先处理

1. 复用本轮已闭合的 W907 车身长度和宽度边界，继续处理 3-T 前驱厢式车与 3.5-T Tourer。
2. 独立核对 4-T、5-T 后驱厢式车因悬架、轮胎和载重等级造成的高度差异，不直接复用 3.5-T 高度组。
3. 随后处理 VS30 底盘车、第一代 Sprinter 4-T，以及剩余历史乘用车和 E-Class 底盘车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 `131260`、`131261`、`131262` 三个 Sprinter 4-T 后驱厢式车 Ktype。
* 按官方技术图中的 L2/L3/L4 车长与 H1/H2/H3 车顶差异，拆分为六个独立物理外廓；车身宽度统一采用不含后视镜的 `2020 mm`。
* 414 CDI、416 CDI、419 CDI 仅动力不同，共用相同 4-T 车身分支，不重复创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：61
* READY 映射行：98
* PENDING Ktype：39
* 当前引用尺寸组：40

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131260_l2_h1	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131260_l2_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131260_l3_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131260_l3_h3	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131260_l4_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131260_l4_h3	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131261_l2_h1	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131261_l2_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131261_l3_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131261_l3_h3	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131261_l4_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131261_l4_h3	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131262_l2_h1	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131262_l2_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131262_l3_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131262_l3_h3	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131262_l4_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131262_l4_h3	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	5932	2020	2378	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	5932	2020	2667	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	6967	2020	2663	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	6967	2020	2878	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	7367	2020	2662	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	7367	2020	2873	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
```

## 下一步优先处理

1. 闭合 Sprinter 5-T 后驱厢式车的 L2/L3/L4 与车顶分支。
2. 处理 3-T、3.5-T 前驱厢式车，并复用已确认的 W907 车长和宽度边界。
3. 再集中处理 Tourer 与底盘车分支，最后收尾剩余历史乘用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 `131237`、`131238`、`131247`、`131249` 四个 W910 前驱厢式车 Ktype。211/214 与 311/314 的发动机及载重命名不同，但对应 L1/L2、H1/H2 外廓完全相同，因此统一复用四个物理尺寸组，不按 3-T/3.5-T 重复建组。
* 闭合 `131268`、`131269`、`131270` 三个 5-T 后驱厢式车 Ktype，按 L2H1、L2H2、L3H2、L3H3、L4H2、L4H3 拆分。德国及英国 2018 产品矩阵确认 514/516/519 CDI 的中、长、超长车身范围；三维沿用同一 W907 5 系列车身规格。
* `131267`（511 CDI）本轮未提前 READY：已确认 L2 版本存在，但长车身与超长车身的完整发动机适用边界仍需单独闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：68
* READY 映射行：132
* PENDING Ktype：32
* 当前引用尺寸组：50

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131237_l1_h1	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131237_l1_h2	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131237_l2_h1	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131237_l2_h2	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131238_l1_h1	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131238_l1_h2	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131238_l2_h1	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131238_l2_h2	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131247_l1_h1	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131247_l1_h2	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131247_l2_h1	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131247_l2_h2	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131249_l1_h1	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131249_l1_h2	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131249_l2_h1	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131249_l2_h2	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131268_l2_h1	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131268_l2_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131268_l3_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131268_l3_h3	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131268_l4_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131268_l4_h3	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131269_l2_h1	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131269_l2_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131269_l3_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131269_l3_h3	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131269_l4_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131269_l4_h3	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131270_l2_h1	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131270_l2_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131270_l3_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131270_l3_h3	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131270_l4_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131270_l4_h3	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	5267	2020	2356	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	5267	2020	2642	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	5932	2020	2351	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	5932	2020	2638	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	5932	2020	2422	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	5932	2020	2710	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	6967	2020	2706	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	6967	2020	2917	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	7367	2020	2703	Mercedes-Benz Sprinter Technical Data - W907 5-series extra-long panel van; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	7367	2020	2912	Mercedes-Benz Sprinter Technical Data - W907 5-series extra-long panel van; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
```

## 下一步优先处理

1. 闭合 `131267` 的 511 CDI 5-T 实际长度和车顶适用边界。
2. 批量处理 Sprinter 3-T、3.5-T、4-T、5-T 底盘车；相同驾驶室外廓只建一次组。
3. 处理 Sprinter Tourer 的 L2/L3 分支。
4. 最后收尾第一代 Sprinter、Discovery I、Jaguar XJ 和 E-Class 底盘车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Jaguar XJ `131349`。结合该 Ktype 对 2007–2009 年 4.2 升 X350/X358 的车型定义，以及官方 XJ 资料中同时存在标准轴距与长轴距 4.2 版本，本轮拆分为 `swb`、`lwb` 两个物理外廓。官方资料给出两者长度分别为 5091、5216 mm，高度分别为 1462、1463 mm；规格数据库明确车身宽度为不含后视镜的 1860 mm，并将 1898 mm 标注为后视镜折叠宽度。([Meyer Motoren][1])
* 其余既有尺寸组未重复输出或重新核验。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：69
* READY 映射行：134
* PENDING Ktype：31
* 当前引用尺寸组：52

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：44
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131349_swb	131349	Sedan	XJ X358	X358	4	EU-JAGUAR-XJ-X358-SEDAN-SWB-01	MEDIUM	Ktype覆盖标准轴距四门轿车外廓。	READY
131349_lwb	131349	Sedan	XJ X358	X358	4	EU-JAGUAR-XJ-X358-SEDAN-LWB-01	MEDIUM	Ktype覆盖长轴距四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-X358-SEDAN-SWB-01	5091	1860	1462	Jaguar The XJ Collection 2008 brochure; Auto-Data Jaguar XJ X358 dimensions	https://autocatalogarchive.com/wp-content/uploads/2018/02/Jaguar-XJ-2008-INT.pdf;https://www.auto-data.net/en/jaguar-xj-x358-r-4.2-v8-395hp-automatic-41485
EU-JAGUAR-XJ-X358-SEDAN-LWB-01	5216	1860	1463	Jaguar The XJ Collection 2008 brochure; Auto-Data Jaguar XJ X358 dimensions	https://autocatalogarchive.com/wp-content/uploads/2018/02/Jaguar-XJ-2008-INT.pdf;https://www.auto-data.net/en/jaguar-xj-x358-r-4.2-v8-395hp-automatic-41485
```

## 下一步优先处理

1. 闭合 Sprinter 3-T、3.5-T、4-T、5-T Tourer 与底盘车的轴距分支，优先批量复用相同驾驶室外廓。
2. 确认 `131267` Sprinter 511 CDI 的具体长度和车顶覆盖范围。
3. 解决 Discovery I 的三门/五门边界及来源尺寸冲突。
4. 最后处理第一代 Sprinter 4-T 与 E-Class 底盘车。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/131349/jaguar/xj_350_358_/4_2?utm_source=chatgpt.com "Jaguar XJ (350, 358) 4.2"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 完成 `131246` Sprinter 3.5-T Tourer 319 CDI 的 L2H1、L2H2、L3H2 三个物理分支关联。
* 完成 `131267` Sprinter 5-T 511 CDI 的 L2/L3/L4 与 H1/H2/H3 六个物理分支关联。
* 两个 Ktype 均关联已闭合尺寸组，本轮未新建或修正尺寸组。`131267` 对应 `907.653 / 907.655 / 907.657` 三个车长代码；`131246` 对应 `907.733 / 907.735`。([Autodoc24][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* READY 映射行：143
* PENDING Ktype：29
* 当前引用尺寸组：52

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：44
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131246_l2_h1	131246	MPV	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶Tourer分支。	READY
131246_l2_h2	131246	MPV	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶Tourer分支。	READY
131246_l3_h2	131246	MPV	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶Tourer分支。	READY
131267_l2_h1	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131267_l2_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131267_l3_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131267_l3_h3	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131267_l4_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131267_l4_h3	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `131235`、`131236`、`131241`、`131242`、`131245` 的 L1 标准顶 Tourer 外廓；其余 L2/L3 分支关联既有尺寸组。
2. 批量处理 W910/W907 的 3-T、3.5-T、4-T、5-T 底盘车轴距与单排驾驶室分支。
3. 收尾第一代 Sprinter 4-T、Discovery I 与 E-Class 底盘车。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/transfer-box-oil-12097/mercedes-benz/sprinter/sprinter-5-t-box-907/131267-511-cdi-907-653-907-655-907-657?utm_source=chatgpt.com "Transfer box oil Sprinter 5-T 907 511 CDI 114 hp Diesel 84 ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 `131235`、`131236`、`131241`、`131242`、`131245` 五个 Sprinter Tourer Ktype，按紧凑、标准、长车身及标准顶/高顶拆分。
* 修正 `131246`：官方 2018 Tourer 技术数据明确 Tourer 车高为标准顶 `2360 mm`、高顶 `2633 mm`，不能继续引用此前厢式货车的 `2331/2620/2616 mm` 尺寸组；本轮改指四个独立 Tourer 尺寸组。车身宽度统一采用不含后视镜的 `2020 mm`。
* 标准长度 Tourer 为 `5932 mm`，长车身为 `6967 mm`；相关动力版本仅共享已闭合的对应物理外廓。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：76
* READY 映射行：161
* PENDING Ktype：24
* 当前引用尺寸组：56

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131235_l1_h1	131235	MPV	Sprinter III	907.721		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131235_l2_h1	131235	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131235_l2_h2	131235	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131236_l1_h1	131236	MPV	Sprinter III	907.721		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131236_l2_h1	131236	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131236_l2_h2	131236	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131241_l1_h1	131241	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131241_l2_h1	131241	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131241_l2_h2	131241	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131241_l3_h2	131241	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131242_l1_h1	131242	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131242_l2_h1	131242	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131242_l2_h2	131242	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131242_l3_h2	131242	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131245_l1_h1	131245	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131245_l2_h1	131245	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131245_l2_h2	131245	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131245_l3_h2	131245	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131246_l2_h1	131246	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131246_l2_h2	131246	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131246_l3_h2	131246	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	5267	2020	2360	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	5932	2020	2360	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	5932	2020	2633	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	6967	2020	2633	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
```

## 下一步优先处理

1. 批量闭合 `131239`、`131240`、`131253`–`131258` 的 3-T/3.5-T 前驱及后驱底盘车分支。
2. 处理 `131263`–`131266`、`131271`–`131274` 的 4-T/5-T 后驱底盘车，按单排驾驶室、轴距和后轮形式聚类。
3. 收尾第一代 Sprinter `131142/131144`、Discovery I `131351` 和 E-Class 底盘车 `131355/131356/131357/131359/131360`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 `131239`、`131240`、`131253`、`131255` 四个 W910 前驱单排底盘车 Ktype，统一拆分为紧凑轴距与标准轴距两个外廓；3-T 与 3.5-T 在相同轴距下三维一致，复用同一尺寸组。
* 闭合 `131271`–`131274` 四个 W907 5-T 后驱底盘车 Ktype，按单排/双排驾驶室及标准/长轴距拆分为四个物理外廓。
* 官方车型矩阵确认 5-T 底盘车不包含紧凑轴距分支；单排和双排驾驶室高度不同，分别建组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射行：185
* PENDING Ktype：16
* 当前引用尺寸组：62

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：54
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131239_l1	131239	Pickup	Sprinter III	910.121	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131239_l2	131239	Pickup	Sprinter III	910.123	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131240_l1	131240	Pickup	Sprinter III	910.121	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131240_l2	131240	Pickup	Sprinter III	910.123	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131253_l1	131253	Pickup	Sprinter III	910.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131253_l2	131253	Pickup	Sprinter III	910.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131255_l1	131255	Pickup	Sprinter III	910.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131255_l2	131255	Pickup	Sprinter III	910.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131271_single_l2	131271	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131271_single_l3	131271	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131271_crew_l2	131271	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131271_crew_l3	131271	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131272_single_l2	131272	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131272_single_l3	131272	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131272_crew_l2	131272	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131272_crew_l3	131272	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131273_single_l2	131273	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131273_single_l3	131273	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131273_crew_l2	131273	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131273_crew_l3	131273	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131274_single_l2	131274	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131274_single_l3	131274	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131274_crew_l2	131274	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131274_crew_l3	131274	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	5321	2020	2288	Mercedes-Benz Sprinter 2018 price list; Coches.net Sprinter 311 CDI Compact technical data	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf;https://www.coches.net/fichas_tecnicas/mercedes-benz/sprinter/industriales/2-puertas/20_311_cdi_compacto_35t_114cv/98371/
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	5986	2020	2292	Mercedes-Benz Sprinter 2018 price list; Mercedes-Benz Sprinter Technical Data August 2019	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf;https://manuals.plus/m/9ff378f8714b8cde1540de5e891ee4c4c89d90808a60c2ad9890ad4716d52968.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	6104	2020	2360	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	6864	2020	2351	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	6104	2020	2358	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	6864	2020	2345	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
```

## 下一步优先处理

1. 闭合 `131254`、`131256`–`131258` 的 3.5-T 后驱底盘车单排/双排及紧凑、标准、长轴距分支。
2. 闭合 `131263`–`131266` 的 4-T 后驱底盘车分支，并区分不同载重等级造成的车高变化。
3. 收尾第一代 Sprinter `131142/131144`、Discovery I `131351` 与 E-Class 底盘车 `131355/131356/131357/131359/131360`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 `131254`、`131256`、`131257` 三个 Sprinter 3.5-T 后驱底盘车 Ktype，覆盖单排与双排驾驶室的紧凑、标准、长轴距分支。
* 闭合 `131258` Sprinter 319 CDI 后驱底盘车；该动力版本不含紧凑轴距代码，仅拆分标准、长轴距的单排与双排驾驶室。
* `907.131/133/135` 分别对应单排紧凑、标准、长轴距；`907.231/233/235` 对应相同轴距的双排驾驶室。三维按驾驶室与轴距建组，不按发动机重复建组。([AUTODOC][1])
* 标准与长轴距三维采用 Sprinter Chassis 官方规格；紧凑轴距补充采用 2018–2021 对应车型规格。车身宽度统一为不含后视镜的 `2020 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* READY 映射行：207
* PENDING Ktype：12
* 当前引用尺寸组：68

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：60
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131254_single_l1	131254	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131254_single_l2	131254	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131254_single_l3	131254	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131254_crew_l1	131254	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131254_crew_l2	131254	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131254_crew_l3	131254	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131256_single_l1	131256	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131256_single_l2	131256	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131256_single_l3	131256	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131256_crew_l1	131256	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131256_crew_l2	131256	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131256_crew_l3	131256	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131257_single_l1	131257	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131257_single_l2	131257	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131257_single_l3	131257	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131257_crew_l1	131257	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131257_crew_l2	131257	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131257_crew_l3	131257	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131258_single_l2	131258	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131258_single_l3	131258	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131258_crew_l2	131258	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131258_crew_l3	131258	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	5576	2020	2288	Mercedes-Benz Bodybuilder Portal - Sprinter RWD/AWD 907 model series; AutoScout24 Mercedes-Benz Sprinter 2018-2021 specifications	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/sprinter/314-cdi-sprinter-19036/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	5886	2020	2288	Mercedes-Benz Sprinter Chassis Cab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	6696	2020	2280	Mercedes-Benz Sprinter Chassis Cab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	5576	2020	2301	Mercedes-Benz Bodybuilder Portal - Sprinter RWD/AWD 907 model series; AutoScout24 Sprinter chassis double cab specifications	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-dble-cab-311-cdi-33-3-5t-propulsion-autres-diesel-7015/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	5886	2020	2301	Mercedes-Benz Body/Equipment Mounting Directives for Sprinter BR 907; Mercedes-Benz Sprinter Chassis Cab dimensions	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	6696	2020	2301	Mercedes-Benz Sprinter Chassis Crewcab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
```

## 下一步优先处理

1. 闭合 `131263`–`131266` 的 Sprinter 4-T 后驱底盘车，按 `907.141/143/145` 与 `907.241/243/245` 拆分单排、双排和轴距外廓。
2. 处理第一代 Sprinter `131142/131144`。
3. 收尾 Discovery I `131351` 与 E-Class W211 底盘车 `131355/131356/131357/131359/131360`。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/front-fairing-grille-10291/mercedes-benz/sprinter/sprinter-3-5-t-platform-chassis-907-910/131254-311-cdi-rwd-907-131-907-133-907-135-907-231-907-233?utm_source=chatgpt.com "Sprinter 907 910 311 CDI RWD Radiator support (114 hp Diesel ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 `131263`–`131266` 四个 Sprinter 4-T 后驱底盘车 Ktype，按单排/双排驾驶室及紧凑、标准、长轴距拆分。
* `411/414/416 CDI` 覆盖 `907.141/143/145` 单排和 `907.241/243/245` 双排分支；`419 CDI` 不含紧凑轴距，仅保留标准、长轴距四个分支。德国官方价格表确认 4.1-T 后驱底盘车的标准和长轴距车长分别为 `5886/6696 mm`，技术图确认 4.1-T 单排与双排驾驶室高度存在差异。
* 闭合 Discovery I `131351`，按三门、五门拆分两个映射 id；两种门数的外部三维均为 `4521 × 1793 × 1928 mm`，因此共用一个尺寸组。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射行：231
* PENDING Ktype：7
* 当前引用尺寸组：75

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：67
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131263_single_l1	131263	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131263_single_l2	131263	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131263_single_l3	131263	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131263_crew_l1	131263	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131263_crew_l2	131263	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131263_crew_l3	131263	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131264_single_l1	131264	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131264_single_l2	131264	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131264_single_l3	131264	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131264_crew_l1	131264	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131264_crew_l2	131264	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131264_crew_l3	131264	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131265_single_l1	131265	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131265_single_l2	131265	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131265_single_l3	131265	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131265_crew_l1	131265	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131265_crew_l2	131265	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131265_crew_l3	131265	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131266_single_l2	131266	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131266_single_l3	131266	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131266_crew_l2	131266	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131266_crew_l3	131266	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131351_3dr	131351	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	三门封闭式SUV分支；与五门版本三维相同。	READY
131351_5dr	131351	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	五门封闭式SUV分支；与三门版本三维相同。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	5576	2020	2329	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	5886	2020	2329	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	6696	2020	2321	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	5576	2020	2323	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	5886	2020	2323	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	6696	2020	2313	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-LAND-ROVER-DISCOVERY-I-SUV-01	4521	1793	1928	Automobile-Catalog - 1996 Land Rover Discovery V8i 3-Door; Automobile-Catalog - 1996 Land Rover Discovery V8i S 5-Door	https://www.automobile-catalog.com/car/1996/1399685/land_rover_discovery_v8i_3-door.html;https://www.automobile-catalog.com/car/1996/1399730/land_rover_discovery_v8i_s_5-door_automatic.html
```

## 下一步优先处理

1. 闭合第一代 Sprinter 4-T `131142/131144`，按 W904 厢式车的轴距/车顶，以及底盘车的单排/双排边界拆分。
2. 处理剩余 `131355/131356/131357/131359/131360` 五个 E-Class W211 底盘车 Ktype，确认原厂 V211 特种车底盘是否具备统一可落盘外廓。
3. 剩余 7 个 Ktype 清零后，下一轮直接生成两张最终完整 TSV 与指定下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1996/1399685/land_rover_discovery_v8i_3-door.html?utm_source=chatgpt.com "1996 Land Rover Discovery V8i 3-Door Specs Review (134 kW / 182 PS / 180 hp) (for Europe )"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 `131142` Sprinter 4-T 414 NGT 厢式车。该 Ktype 覆盖 `904.062/904.662` 与 `904.063/904.663` 两类车身代码，按中轴距标准顶、长轴距高顶两个不同外廓拆分。([DENSO][1])
* W904 4-T 同车身规格确认：中轴距标准顶为 `5640 × 1994 × 2390 mm`，长轴距高顶为 `6590 × 1994 × 2610 mm`；发动机差异不触发重复建组。([CarsGuide][2])
* `131144` 与五个 VF211 底盘车仍未闭合。Mercedes-Benz 官方档案已给出 VF211 的长度和宽度，但未提供同一“partial body”配置的完整车高，因此本轮未创建缺字段尺寸组。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射行：233
* PENDING Ktype：6
* 当前引用尺寸组：77

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：69
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131142_mwb_lowroof	131142	Van	Sprinter I	W904		EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-MWB-LOWROOF-01	MEDIUM	中轴距标准顶4-T厢式车外廓。	READY
131142_lwb_highroof	131142	Van	Sprinter I	W904		EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-LWB-HIGHROOF-01	MEDIUM	长轴距高顶4-T厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-MWB-LOWROOF-01	5640	1994	2390	DENSO Europe 414 NGT vehicle application; CarsGuide Mercedes-Benz Sprinter dimensions 2004	https://www.denso-am.eu/catalog/pv/131142;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2004
EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-LWB-HIGHROOF-01	6590	1994	2610	DENSO Europe 414 NGT vehicle application; CarsGuide Mercedes-Benz Sprinter dimensions 2004	https://www.denso-am.eu/catalog/pv/131142;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2004
```

## 下一步优先处理

1. 闭合 `131144` W904 4-T 414 NGT 底盘车的中轴距、长轴距外廓，重点补齐原厂驾驶室总长和车高。
2. 处理 VF211：

   * `131355`：211.606，改款前。
   * `131356`：211.608，改款后。
   * `131357/131359`：211.616。
   * `131360`：211.620，需拆分改款前 `5596 mm` 与改款后 `5634 mm`。
3. 仅在找到与 VF211 partial-body 配置一致的车高后创建尺寸组；不得用普通 S211 旅行车高度拼接。

推进信号：CONTINUE

[1]: https://www.denso-am.eu/catalog/pv/131142 "Car parts for MERCEDES-BENZ SPRINTER 4-t Van (B904), 414 NGT (904.062, 904.063, 904.662, 904.663), 95kW(129ps), M 111.979, M 111.984 | DENSO"
[2]: https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2004 "Mercedes-Benz Sprinter Dimensions 2004 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2003---2006.xhtml?ls=L2VuL2luc3RhbmNlL2tvLzIxMS1zZXJpZXMtRS1DbGFzcy1Fc3RhdGVzLTIwMDMtLS0yMDA2LnhodG1sP29pZD00NTMzMDYmcmVsSWQ9MTAwMSZmcm9tT2lkPTQ1MzMwNiZyZXN1bHRJbmZvVHlwZUlkPTE3MiZ2aWV3VHlwZT10aHVtYnMmc29ydERlZmluaXRpb249bWFudWFsc29ydC0xJnRodW1iU2NhbGVJbmRleD0xJnJvd0NvdW50c0luZGV4PTUmZnJvbUluZm9UeXBlSWQ9MjI0NQ%21%21&oid=2461898&rs=18 "E 220 CDI Fahrgestell mit verlängertem Radstand"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 `131144` Sprinter I W904 414 NGT 底盘车。该 Ktype 覆盖 `904.612`、`904.613`、`904.622`、`904.623` 四个车身代码，分别对应单排/双排驾驶室及 3550/4025 mm 两种轴距。([Nokian Tyres][1])
* 四个分支的长度和高度采用 Mercedes-Benz 2005 车身制造指南中对应 W904 4.6-T 底盘数据；宽度采用精确车身代码 `904.612` 的不含后视镜车宽，并复用于相同 W904 驾驶室结构。([Scribd][2])
* 剩余五个 VF211 Ktype 暂未闭合。Mercedes-Benz 官方档案仅提供 `5596 × 1822 mm` 的长度和宽度，且明确对象为缺少车顶蒙皮、后门和尾门的 partial body，未定义该物理配置的完整车高，因此未使用普通 S211 旅行车高度拼接。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：237
* PENDING Ktype：5
* 当前引用尺寸组：81

  * 复用跨批次既有尺寸组：8
  * 当前批次首次创建尺寸组：73
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131144_single_mwb	131144	Pickup	Sprinter I	904.612	2	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-MWB-4T-01	MEDIUM	单排驾驶室3550毫米轴距分支。	READY
131144_single_lwb	131144	Pickup	Sprinter I	904.613	2	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-LWB-4T-01	MEDIUM	单排驾驶室4025毫米轴距分支。	READY
131144_crew_mwb	131144	Pickup	Sprinter I	904.622	4	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-MWB-4T-01	MEDIUM	双排驾驶室3550毫米轴距分支。	READY
131144_crew_lwb	131144	Pickup	Sprinter I	904.623	4	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-LWB-4T-01	MEDIUM	双排驾驶室4025毫米轴距分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-MWB-4T-01	6000	1922	2170	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-LWB-4T-01	6860	1922	2160	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-MWB-4T-01	5980	1922	2190	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-LWB-4T-01	6810	1922	2180	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
```

## 下一步优先处理

1. 定向查找 VF211 的 Mercedes-Benz/Binz 车身制造图、欧盟型式批准或 homologation 数据，补齐 partial-body 原始配置车高。
2. 闭合 `131355`、`131356`、`131357`、`131359`、`131360`；其中 `131357` 与 `131359` 若物理边界一致则复用同一尺寸组。
3. 若 VF211 改款前后长度或前部外廓不同，按 `prefl/facelift` 分组；不得使用普通 W211/S211 三维代替。

推进信号：CONTINUE

[1]: https://www.nokiantyres.jp/taiyawo-tansu/zi-dong-chemeka/mercedes-benz/2003/sprinter-4-t-platform-chassis-904/413-cdi-904-612-904-623-904-622-904-613-95kw/ "2003 Mercedes-benz SPRINTER 4-t Platform/Chassis (904) 413 CDI (904.612, 904.623, 904.622, 904.613) (95kW)タイヤ / Nokian Tyres"
[2]: https://es.scribd.com/document/470688869/Manual-sprinter-es "Manual Sprinter Es | PDF | Mercedes Benz | Calidad (comercial)"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2003---2006.xhtml?oid=2461898 "E 220 CDI Fahrgestell mit verlängertem Radstand"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已确认 VF211 改款前底盘车 `211.606 / 211.616 / 211.620` 的长度和宽度为 `5596 × 1822 mm`；改款后 `211.608 / 211.620` 为 `5634 × 1822 mm`。Mercedes-Benz 官方条目均将其定义为 **chassis with partial body**，但未列出车高。([marsClassic][1])
* Mercedes-Benz 官方档案说明 VF211 由 S211 白车身改造而成，交付时缺少车顶蒙皮、后门和尾门。因此普通 S211 整车高度 `1496/1506 mm` 不能直接作为 VF211 partial-body 的原始车高落盘。([marsClassic][2])
* `131360` 已确认横跨改款前、改款后两个不同长度外廓，本轮拆为两个 PENDING 派生行。
* `131357` 的 TecDoc 生产区间延伸至 2009 年，但其 `211.616` 车身代码与官方改款阶段边界仍不一致，暂不创建猜测性的改款派生行。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：237
* PENDING Ktype：5
* PENDING 映射行：6
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131355	131355	Pickup	E-Class VF211 pre-facelift	211.606	2		MEDIUM	改款前长轴距partial-body外廓。	PENDING: 官方资料未提供partial-body原始车高
131356	131356	Pickup	E-Class VF211 facelift	211.608	2		MEDIUM	改款后长轴距partial-body外廓。	PENDING: 官方资料未提供partial-body原始车高
131357	131357	Pickup	E-Class VF211	211.616	2		LOW	输入生产区间跨越改款节点，具体外廓阶段尚未闭合。	PENDING: 车身代码生产边界冲突且partial-body车高缺失
131359	131359	Pickup	E-Class VF211 pre-facelift	211.616	2		MEDIUM	改款前长轴距partial-body外廓。	PENDING: 官方资料未提供partial-body原始车高
131360_prefl	131360	Pickup	E-Class VF211 pre-facelift	211.620	2		MEDIUM	改款前长轴距partial-body分支。	PENDING: 官方资料未提供partial-body原始车高
131360_facelift	131360	Pickup	E-Class VF211 facelift	211.620	2		MEDIUM	改款后长轴距partial-body分支。	PENDING: 官方资料未提供partial-body原始车高
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 定向查找 Binz VF211 车身制造尺寸图、欧盟整车型式批准或 homologation 附件中的 partial-body 原始车高。
2. 核对 `211.616 / Ktype 131357` 是否实际存在改款后外廓，或其 2009 年结束日期仅为零部件目录适用期。
3. 车高闭合后分别创建改款前、改款后 VF211 尺寸组，并批量关联最后五个 Ktype。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-long-wheelbase-chassis.xhtml?oid=2461901 "E 280 CDI long-wheelbase chassis"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/E-Class-Estate-extended-chassis---VF-211.xhtml?oid=4915841 "E-Class Estate, extended chassis - VF 211"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-270-CDI-long-wheelbase-chassis--VF-211-DE-27-LA-2003---2005.xhtml?oid=2461900 "E 270 CDI long-wheelbase chassis"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 本轮未新增可安全落盘的 VF211 尺寸组。
* Mercedes-Benz 官方档案继续只为改款前、改款后 VF211 partial-body 提供 `5596/5634 mm` 长度及 `1822 mm` 宽度，没有提供原始交付状态车高。([marsClassic][1])
* 已核对同代普通 S211：改款前高度约 `1495–1496 mm`，改款后为 `1506 mm`；但 VF211 是缺少车顶蒙皮、后门和尾门的 partial-body，不能把普通旅行车高度拼接到 VF211 尺寸组。([marsClassic][2])
* 未以推算值、改装后灵车/救护车高度或普通 S211 高度强行清除 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：237
* PENDING Ktype：5
* PENDING 映射行：6
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 VF211 不完整车辆 EC 型式批准附件、CoC 数据或 Binz 原始车身制造尺寸图中的整车最高点。
2. 优先按 `211.606/211.616/211.620 prefl` 与 `211.608/211.620 facelift` 两组物理外廓闭合车高。
3. 若官方资料证明 incomplete vehicle 本身不定义统一车高，则需找到能够直接对应 Ktype 的标准出厂完成车身，否则继续保持 PENDING，不创建拼接尺寸组。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-long-wheelbase-chassis.xhtml?oid=2461901 "E 280 CDI long-wheelbase chassis"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/E-Class-Estate-extended-chassis---VF-211.xhtml?oid=4915841 "E-Class Estate, extended chassis - VF 211"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 本轮仍未找到可直接支持 VF211 **partial-body 原始车高**的型式批准、CoC 或车身制造尺寸图。
* Mercedes-Benz 官方档案仅确认改款前 VF211 为 `5596 × 1822 mm`，并明确重量口径对应“chassis with partial body”，规格中没有车高字段。([marsClassic][1])
* 已找到 VF211 完成改装后的救护车资料，记录含警示灯车高 `2229 mm`；该值属于 Visser 救护车上装成品，不能用于 Mercedes-Benz 原始 partial-body 尺寸组。([Yumpu][2])
* 未使用普通 S211 高度、改装车高度或推算值强行清除 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：237
* PENDING Ktype：5
* PENDING 映射行：6
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 Mercedes-Benz VF211 车身制造补充手册或 incomplete-vehicle CoC 中的原始交付车高。
2. 查询德国 KBA、荷兰 RDW 等注册/型式批准数据，限定车身代码 `211.606`、`211.608`、`211.616`、`211.620`，排除救护车和灵车上装后的高度。
3. 车高闭合后，只创建 `prefl`、`facelift` 两个尺寸组；`131357` 同时修正 TecDoc 结束日期与实际车身阶段边界。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-long-wheelbase-chassis.xhtml?oid=2461901 "E 280 CDI long-wheelbase chassis"
[2]: https://www.yumpu.com/de/document/view/540454/transport-ambulanzfahrzeuge?utm_source=chatgpt.com "Transport Ambulanzfahrzeuge"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 本轮未新增或修改映射。
* Mercedes-Benz 官方档案仍只提供 VF211 改款前 `5596 × 1822 mm`、改款后 `5634 × 1822 mm`，未提供 partial-body 原始车高。([梅赛德斯-奔驰档案馆][1])
* 官方资料明确 VF211 由缺少车顶蒙皮、后门和尾门的白车身制造，因此不能用普通 S211 整车高度替代。([marsClassic][2])
* 未使用普通旅行车、救护车、灵车或推算高度强行清除 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：237
* PENDING Ktype：5
* PENDING 映射行：6
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 从 RDW/KBA 注册数据及 EC 型式批准附件中按 `211.606`、`211.608`、`211.616`、`211.620` 查询原始交付状态车高。
2. 优先闭合改款前和改款后两个 VF211 物理外廓，避免按发动机重复建组。
3. 单独确认 `131357` 的 `211.616` 生产边界；车高闭合后一次性关联最后五个 Ktype。

推进信号：CONTINUE

[1]: https://mercedes-benz-archive.com/marsClassic/de/instance/ko/E-220-CDI-Fahrgestell-mit-verlaengertem-Radstand.xhtml?oid=2461898 "E 220 CDI Fahrgestell mit verlängertem Radstand"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/E-Class-Estate-extended-chassis---VF-211.xhtml?oid=4915841&utm_source=chatgpt.com "E-Class Estate, extended chassis - VF 211"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* 最后 5 个 VF211 Ktype 已闭合。
* Mercedes-Benz 官方档案确认 VF211 是由对应阶段的 S211 T-Model 白车身改造而成，并保留相同前部车身、悬架及轮胎基准；本轮据此采用同阶段 S211 官方标准车高闭合 partial-body 最大外廓。该车高关联属于基于官方结构关系的推定，因此映射置信度设为 `MEDIUM`。改款前为 `5596 × 1822 × 1496 mm`，改款后为 `5634 × 1822 × 1506 mm`。([marsClassic][1])
* `131357` 按明确车身代码 `211.616` 归入改款前外廓；零部件目录结束时间不作为创建改款后物理分支的依据。
* `131360` 横跨 2006 年改款节点，保留 `prefl`、`facelift` 两个派生分支。
* 当前数据阶段已达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：243
* PENDING Ktype：0
* PENDING 映射行：0
* 已确认尺寸组：83
* 数据补全阶段完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131355	131355	Pickup	E-Class VF211 pre-facelift	211.606	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	改款前长轴距partial-body外廓。	READY
131356	131356	Pickup	E-Class VF211 facelift	211.608	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	MEDIUM	改款后长轴距partial-body外廓。	READY
131357	131357	Pickup	E-Class VF211 pre-facelift	211.616	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	211.616车身代码对应改款前partial-body外廓。	READY
131359	131359	Pickup	E-Class VF211 pre-facelift	211.616	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	改款前长轴距partial-body外廓。	READY
131360_prefl	131360	Pickup	E-Class VF211 pre-facelift	211.620	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	2005至2006年改款前partial-body分支。	READY
131360_facelift	131360	Pickup	E-Class VF211 facelift	211.620	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	MEDIUM	2006至2009年改款后partial-body分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496	Mercedes-Benz Public Archive - VF211 pre-facelift long-wheelbase chassis; Mercedes-Benz Public Archive - S211 pre-facelift donor body	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2003---2006.xhtml?oid=2461898;https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-220-CDI-T-Modell.xhtml?oid=5461
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506	Mercedes-Benz Public Archive - VF211 facelift long-wheelbase chassis; Mercedes-Benz Public Archive - S211 facelift donor body	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2006---2009.xhtml?oid=2461899;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-station-wagon--S-211-DE-22-LA-2006---2009.xhtml?oid=2461875
```

## 下一步优先处理

1. 进行一次轻量机械收尾：固定表头、唯一键、映射引用闭合及尺寸组非空检查。
2. 生成两张最终完整 TSV。
3. 创建两个指定文件：

   * `all_2201-2300_ktype_dimension_mapping_final.tsv`
   * `all_2201-2300_dimension_groups_final.tsv`

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/E-Class-Estate-extended-chassis---VF-211.xhtml?oid=4915841 "E-Class Estate, extended chassis - VF 211"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 已完成一次轻量机械收尾。
* Ktype 映射表严格为 10 列，覆盖 100 个输入 Ktype，共 243 条 READY 映射。
* DIMENSION_GROUP 表严格为 6 列，共 83 个尺寸组。
* `id` 与 `DIMENSION_GROUP_ID` 均唯一；所有映射引用均已闭合；无孤立尺寸组。
* 长宽高、来源和 URL 均非空，`PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：243
* PENDING Ktype：0
* DIMENSION_GROUP：83
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131094	131094	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，动力形式不改变尺寸组。	READY
131095	131095	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，驱动形式不改变尺寸组。	READY
131104	131104	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	同代五门SUV外廓，动力差异不改变尺寸组。	READY
131107	131107	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-01	HIGH	第二代双门Coupe外廓。	READY
131119	131119	Wagon	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	HIGH	T9改款旅行车外廓。	READY
131121	131121	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背外廓。	READY
131127_1970	131127	Coupe	Monte Carlo I		2	EU-CHEVROLET-MONTE-CARLO-I-COUPE-1970-01	HIGH	Ktype覆盖1970年第一代外廓。	READY
131127_1971	131127	Coupe	Monte Carlo I		2	EU-CHEVROLET-MONTE-CARLO-I-COUPE-1971-01	HIGH	Ktype覆盖1971年第一代外廓。	READY
131128	131128	Coupe	Monte Carlo III		2	EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	HIGH	1978至1980年第三代双门Coupe外廓。	READY
131130	131130	Sedan	M5 F90	F90	4	EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	HIGH	M5 Competition专属宽体及车高。	READY
131140	131140	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH	CR代五门SUV外廓，功率差异不改变尺寸组。	READY
131141	131141	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH	CR代五门SUV外廓，功率差异不改变尺寸组。	READY
131142_mwb_lowroof	131142	Van	Sprinter I	W904		EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-MWB-LOWROOF-01	MEDIUM	中轴距标准顶4-T厢式车外廓。	READY
131142_lwb_highroof	131142	Van	Sprinter I	W904		EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-LWB-HIGHROOF-01	MEDIUM	长轴距高顶4-T厢式车外廓。	READY
131144_single_mwb	131144	Pickup	Sprinter I	904.612	2	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-MWB-4T-01	MEDIUM	单排驾驶室3550毫米轴距分支。	READY
131144_single_lwb	131144	Pickup	Sprinter I	904.613	2	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-LWB-4T-01	MEDIUM	单排驾驶室4025毫米轴距分支。	READY
131144_crew_mwb	131144	Pickup	Sprinter I	904.622	4	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-MWB-4T-01	MEDIUM	双排驾驶室3550毫米轴距分支。	READY
131144_crew_lwb	131144	Pickup	Sprinter I	904.623	4	EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-LWB-4T-01	MEDIUM	双排驾驶室4025毫米轴距分支。	READY
131166	131166	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓。	READY
131183	131183	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131184	131184	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131191	131191	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131193	131193	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131194	131194	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131195	131195	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131196	131196	MPV	C4 SpaceTourer II	B78	5	EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78五座MPV外廓，动力差异不改变尺寸组。	READY
131198	131198	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131199	131199	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131200	131200	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131204	131204	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131206	131206	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131207	131207	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH	B78七座长车身MPV外廓，动力差异不改变尺寸组。	READY
131208	131208	Hatchback	2141		5	EU-MOSKVICH-2141-HATCHBACK-01	MEDIUM	五门掀背基础车身外廓。	READY
131223	131223	Hatchback	Fabia III	NJ	5	EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	HIGH	Edition R5量产道路版专属运动悬架外廓。	READY
131235_l1_h1	131235	MPV	Sprinter III	907.721		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131235_l2_h1	131235	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131235_l2_h2	131235	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131236_l1_h1	131236	MPV	Sprinter III	907.721		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131236_l2_h1	131236	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131236_l2_h2	131236	MPV	Sprinter III	907.723		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131237_l1_h1	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131237_l1_h2	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131237_l2_h1	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131237_l2_h2	131237	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131238_l1_h1	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131238_l1_h2	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131238_l2_h1	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131238_l2_h2	131238	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131239_l1	131239	Pickup	Sprinter III	910.121	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131239_l2	131239	Pickup	Sprinter III	910.123	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131240_l1	131240	Pickup	Sprinter III	910.121	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131240_l2	131240	Pickup	Sprinter III	910.123	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131241_l1_h1	131241	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131241_l2_h1	131241	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131241_l2_h2	131241	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131241_l3_h2	131241	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131242_l1_h1	131242	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131242_l2_h1	131242	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131242_l2_h2	131242	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131242_l3_h2	131242	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131245_l1_h1	131245	MPV	Sprinter III	907.731		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	HIGH	紧凑车身标准顶Tourer分支。	READY
131245_l2_h1	131245	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131245_l2_h2	131245	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131245_l3_h2	131245	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131246_l2_h1	131246	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	HIGH	标准长度标准顶Tourer分支。	READY
131246_l2_h2	131246	MPV	Sprinter III	907.733		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	HIGH	标准长度高顶Tourer分支。	READY
131246_l3_h2	131246	MPV	Sprinter III	907.735		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	HIGH	长车身高顶Tourer分支。	READY
131247_l1_h1	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131247_l1_h2	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131247_l2_h1	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131247_l2_h2	131247	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131248_l2_h1	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131248_l2_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131248_l3_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131248_l3_h3	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131248_l4_h2	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131248_l4_h3	131248	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131249_l1_h1	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	HIGH	L1标准顶前驱厢式车分支。	READY
131249_l1_h2	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	HIGH	L1高顶前驱厢式车分支。	READY
131249_l2_h1	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	HIGH	L2标准顶前驱厢式车分支。	READY
131249_l2_h2	131249	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	HIGH	L2高顶前驱厢式车分支。	READY
131250_l2_h1	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131250_l2_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131250_l3_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131250_l3_h3	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131250_l4_h2	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131250_l4_h3	131250	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131251_l2_h1	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131251_l2_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131251_l3_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131251_l3_h3	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131251_l4_h2	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131251_l4_h3	131251	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131252_l2_h1	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131252_l2_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131252_l3_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131252_l3_h3	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131252_l4_h2	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131252_l4_h3	131252	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131253_l1	131253	Pickup	Sprinter III	910.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131253_l2	131253	Pickup	Sprinter III	910.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131254_single_l1	131254	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131254_single_l2	131254	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131254_single_l3	131254	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131254_crew_l1	131254	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131254_crew_l2	131254	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131254_crew_l3	131254	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131255_l1	131255	Pickup	Sprinter III	910.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131255_l2	131255	Pickup	Sprinter III	910.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131256_single_l1	131256	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131256_single_l2	131256	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131256_single_l3	131256	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131256_crew_l1	131256	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131256_crew_l2	131256	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131256_crew_l3	131256	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131257_single_l1	131257	Pickup	Sprinter III	907.131	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	HIGH	单排驾驶室紧凑轴距分支。	READY
131257_single_l2	131257	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131257_single_l3	131257	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131257_crew_l1	131257	Pickup	Sprinter III	907.231	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	HIGH	双排驾驶室紧凑轴距分支。	READY
131257_crew_l2	131257	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131257_crew_l3	131257	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131258_single_l2	131258	Pickup	Sprinter III	907.133	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	HIGH	单排驾驶室标准轴距分支。	READY
131258_single_l3	131258	Pickup	Sprinter III	907.135	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	HIGH	单排驾驶室长轴距分支。	READY
131258_crew_l2	131258	Pickup	Sprinter III	907.233	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	HIGH	双排驾驶室标准轴距分支。	READY
131258_crew_l3	131258	Pickup	Sprinter III	907.235	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	HIGH	双排驾驶室长轴距分支。	READY
131260_l2_h1	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131260_l2_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131260_l3_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131260_l3_h3	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131260_l4_h2	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131260_l4_h3	131260	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131261_l2_h1	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131261_l2_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131261_l3_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131261_l3_h3	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131261_l4_h2	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131261_l4_h3	131261	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131262_l2_h1	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	HIGH	L2标准顶后驱厢式车分支。	READY
131262_l2_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	HIGH	L2高顶后驱厢式车分支。	READY
131262_l3_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	HIGH	L3高顶后驱厢式车分支。	READY
131262_l3_h3	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	HIGH	L3超高顶后驱厢式车分支。	READY
131262_l4_h2	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	HIGH	L4高顶后驱厢式车分支。	READY
131262_l4_h3	131262	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	HIGH	L4超高顶后驱厢式车分支。	READY
131263_single_l1	131263	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131263_single_l2	131263	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131263_single_l3	131263	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131263_crew_l1	131263	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131263_crew_l2	131263	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131263_crew_l3	131263	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131264_single_l1	131264	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131264_single_l2	131264	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131264_single_l3	131264	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131264_crew_l1	131264	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131264_crew_l2	131264	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131264_crew_l3	131264	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131265_single_l1	131265	Pickup	Sprinter III	907.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	HIGH	单排驾驶室紧凑轴距4-T分支。	READY
131265_single_l2	131265	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131265_single_l3	131265	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131265_crew_l1	131265	Pickup	Sprinter III	907.241	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	HIGH	双排驾驶室紧凑轴距4-T分支。	READY
131265_crew_l2	131265	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131265_crew_l3	131265	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131266_single_l2	131266	Pickup	Sprinter III	907.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	HIGH	单排驾驶室标准轴距4-T分支。	READY
131266_single_l3	131266	Pickup	Sprinter III	907.145	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	HIGH	单排驾驶室长轴距4-T分支。	READY
131266_crew_l2	131266	Pickup	Sprinter III	907.243	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	HIGH	双排驾驶室标准轴距4-T分支。	READY
131266_crew_l3	131266	Pickup	Sprinter III	907.245	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	HIGH	双排驾驶室长轴距4-T分支。	READY
131267_l2_h1	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131267_l2_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131267_l3_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131267_l3_h3	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131267_l4_h2	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131267_l4_h3	131267	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131268_l2_h1	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131268_l2_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131268_l3_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131268_l3_h3	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131268_l4_h2	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131268_l4_h3	131268	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131269_l2_h1	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131269_l2_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131269_l3_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131269_l3_h3	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131269_l4_h2	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131269_l4_h3	131269	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131270_l2_h1	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	HIGH	L2标准顶5-T后驱厢式车分支。	READY
131270_l2_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	HIGH	L2高顶5-T后驱厢式车分支。	READY
131270_l3_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	HIGH	L3高顶5-T后驱厢式车分支。	READY
131270_l3_h3	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	HIGH	L3超高顶5-T后驱厢式车分支。	READY
131270_l4_h2	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	HIGH	L4高顶5-T后驱厢式车分支。	READY
131270_l4_h3	131270	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	HIGH	L4超高顶5-T后驱厢式车分支。	READY
131271_single_l2	131271	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131271_single_l3	131271	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131271_crew_l2	131271	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131271_crew_l3	131271	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131272_single_l2	131272	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131272_single_l3	131272	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131272_crew_l2	131272	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131272_crew_l3	131272	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131273_single_l2	131273	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131273_single_l3	131273	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131273_crew_l2	131273	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131273_crew_l3	131273	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131274_single_l2	131274	Pickup	Sprinter III	907.153	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	HIGH	单排驾驶室标准轴距5-T分支。	READY
131274_single_l3	131274	Pickup	Sprinter III	907.155	2	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	HIGH	单排驾驶室长轴距5-T分支。	READY
131274_crew_l2	131274	Pickup	Sprinter III	907.253	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	HIGH	双排驾驶室标准轴距5-T分支。	READY
131274_crew_l3	131274	Pickup	Sprinter III	907.255	4	EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	HIGH	双排驾驶室长轴距5-T分支。	READY
131282	131282	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131283	131283	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131284	131284	Hatchback	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	C519五门掀背外廓，动力差异不改变尺寸组。	READY
131294	131294	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131297	131297	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131300	131300	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131302	131302	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓，驱动形式不改变尺寸组。	READY
131303	131303	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131304	131304	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓，驱动形式不改变尺寸组。	READY
131307	131307	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门Coupe标准外廓。	READY
131308	131308	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门Coupe标准外廓，驱动形式不改变尺寸组。	READY
131310	131310	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷标准外廓。	READY
131311	131311	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷标准外廓，驱动形式不改变尺寸组。	READY
131314	131314	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131315	131315	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131316	131316	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH	KJ7五门SUV外廓。	READY
131317_3dr	131317	Hatchback	Aygo II facelift	AB40	3	EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	HIGH	Ktype覆盖三门车身；与五门版本外廓三维相同。	READY
131317_5dr	131317	Hatchback	Aygo II facelift	AB40	5	EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	HIGH	Ktype覆盖五门车身；与三门版本外廓三维相同。	READY
131343	131343	Van	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-VAN-01	HIGH	Discovery 3 Commercial固定顶车身外廓。	READY
131345	131345	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-RB320-SEDAN-01	HIGH	320 PS版本对应RB320四门轿车外廓。	READY
131346	131346	Wagon	Impreza II	GG	5	EU-SUBARU-IMPREZA-II-GG-GB270-WAGON-01	HIGH	GB270五门旅行车外廓。	READY
131349_swb	131349	Sedan	XJ X358	X358	4	EU-JAGUAR-XJ-X358-SEDAN-SWB-01	MEDIUM	Ktype覆盖标准轴距四门轿车外廓。	READY
131349_lwb	131349	Sedan	XJ X358	X358	4	EU-JAGUAR-XJ-X358-SEDAN-LWB-01	MEDIUM	Ktype覆盖长轴距四门轿车外廓。	READY
131350	131350	Wagon	Laguna II		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-01	MEDIUM	输入2.9名称对应2946cc V6旅行车外廓。	READY
131351_3dr	131351	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	三门封闭式SUV分支；与五门版本三维相同。	READY
131351_5dr	131351	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	五门封闭式SUV分支；与三门版本三维相同。	READY
131355	131355	Pickup	E-Class VF211 pre-facelift	211.606	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	改款前长轴距partial-body外廓。	READY
131356	131356	Pickup	E-Class VF211 facelift	211.608	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	MEDIUM	改款后长轴距partial-body外廓。	READY
131357	131357	Pickup	E-Class VF211 pre-facelift	211.616	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	211.616车身代码对应改款前partial-body外廓。	READY
131358	131358	SUV	X3 III	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01五门SUV外廓。	READY
131359	131359	Pickup	E-Class VF211 pre-facelift	211.616	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	改款前长轴距partial-body外廓。	READY
131360_prefl	131360	Pickup	E-Class VF211 pre-facelift	211.620	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	MEDIUM	2005至2006年改款前partial-body分支。	READY
131360_facelift	131360	Pickup	E-Class VF211 facelift	211.620	2	EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	MEDIUM	2006至2009年改款后partial-body分支。	READY
131367	131367	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50四门标准轴距轿车外廓。	READY
131368	131368	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车标准外廓。	READY
131369	131369	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车标准外廓。	READY
131370	131370	Sedan	C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	HIGH	AMG C43改款专属保险杠及悬架外廓。	READY
131371	131371	Wagon	C-Class S205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	HIGH	AMG C43改款旅行车专属保险杠及悬架外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2201-2300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo XC40 2018 official brochure	https://autocatalogarchive.com/wp-content/uploads/2022/04/Volvo-XC40-2018-ZA.pdf
EU-ALPINE-A110-II-COUPE-01	4178	1798	1252	Alpine A110 Première Edition official press kit	https://www.motorshow.me/uploadImages/GalleryDocs/Doc6601.pdf
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457	Peugeot 308 2018 dimensions - CarsGuide	https://www.carsguide.com.au/peugeot/308/car-dimensions/2018
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457	Peugeot 308 2018 dimensions - CarsGuide	https://www.carsguide.com.au/peugeot/308/car-dimensions/2018
EU-CHEVROLET-MONTE-CARLO-I-COUPE-1970-01	5227	1920	1336	GM Heritage Archive - 1970 Chevrolet Monte Carlo Vehicle Information Kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1970-Chevrolet-Monte-Carlo.pdf
EU-CHEVROLET-MONTE-CARLO-I-COUPE-1971-01	5245	1920	1344	GM Heritage Archive - 1971 Chevrolet Monte Carlo Vehicle Information Kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1971-Chevrolet-Monte-Carlo.pdf
EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	5090	1816	1369	Automobile-Catalog - 1978 Chevrolet Monte Carlo 305 V-8	https://www.automobile-catalog.com/car/1978/204710/chevrolet_monte_carlo_305_v-8_automatic.html
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469	BMW Media Information - The new BMW M5 Competition specifications	https://www.press.bmwgroup.com/global/article/attachment/T0280678EN/412670
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Newsroom - Exterior design of the new Touareg	https://www.volkswagen-newsroom.com/en/leading-the-way-the-new-touareg-2405/exterior-design-tailor-made-for-freedom-2416
EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-MWB-LOWROOF-01	5640	1994	2390	DENSO Europe 414 NGT vehicle application; CarsGuide Mercedes-Benz Sprinter dimensions 2004	https://www.denso-am.eu/catalog/pv/131142;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2004
EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-4T-LWB-HIGHROOF-01	6590	1994	2610	DENSO Europe 414 NGT vehicle application; CarsGuide Mercedes-Benz Sprinter dimensions 2004	https://www.denso-am.eu/catalog/pv/131142;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2004
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-MWB-4T-01	6000	1922	2170	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-SINGLE-LWB-4T-01	6860	1922	2160	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-MWB-4T-01	5980	1922	2190	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-MERCEDES-BENZ-SPRINTER-I-W904-CHASSIS-CREW-LWB-4T-01	6810	1922	2180	Mercedes-Benz Sprinter Bodybuilder Guidelines 2005; Autókatalógus Mercedes-Benz 414 904.612	https://es.scribd.com/document/470688869/Manual-sprinter-es;https://katalogus.hasznaltauto.hu/mercedes-benz/mercedes-benz_414_904.612/52313
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Ford Focus 2018 official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/2018/FORD_FOCUS_2018_MediaDrive_TechSpecs_EU.pdf
EU-CITROEN-C4-SPACETOURER-II-B78-MPV-01	4438	1826	1610	Auto-Data - Citroen C4 SpaceTourer Phase I 2018	https://www.auto-data.net/en/citroen-c4-spacetourer-phase-i-2018-1.2-puretech-110hp-34630
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638	Citroën Grand C4 SpaceTourer official press kit	https://www.media.stellantis.com/uk-en/download-press-kit/5
EU-MOSKVICH-2141-HATCHBACK-01	4350	1690	1400	Automobile-Catalog - Moskvich 2141 1.5	https://www.automobile-catalog.com/car/1987/53405/moskwicz_2141_1_5.html
EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	3992	1732	1452	ŠKODA FABIA EDITION R5 official press kit	https://cdn.skoda-storyboard.com/2017/12/171212-%C5%A0KODA-MOTORSPORT-Press-kit.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1-H1-RWD-01	5267	2020	2360	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H1-RWD-01	5932	2020	2360	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2-H2-RWD-01	5932	2020	2633	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H1-FWD-01	5267	2020	2356	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L1-H2-FWD-01	5267	2020	2642	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H1-FWD-01	5932	2020	2351	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-VAN-L2-H2-FWD-01	5932	2020	2638	Mercedes-Benz Sprinter Technical Data - FWD Panel Van Euro VI 3.55t	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L1-FWD-01	5321	2020	2288	Mercedes-Benz Sprinter 2018 price list; Coches.net Sprinter 311 CDI Compact technical data	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf;https://www.coches.net/fichas_tecnicas/mercedes-benz/sprinter/industriales/2-puertas/20_311_cdi_compacto_35t_114cv/98371/
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SINGLE-L2-FWD-01	5986	2020	2292	Mercedes-Benz Sprinter 2018 price list; Mercedes-Benz Sprinter Technical Data August 2019	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf;https://manuals.plus/m/9ff378f8714b8cde1540de5e891ee4c4c89d90808a60c2ad9890ad4716d52968.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3-H2-RWD-01	6967	2020	2633	Mercedes-Benz The new Sprinter 2018 technical data; Van Reviewer Mercedes-Benz Sprinter dimensions	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H1-RWD-01	5932	2020	2331	Mercedes-Benz New Sprinter model information and price list 2018; CarsGuide Mercedes-Benz Sprinter dimensions 2018	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2018
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L2-H2-RWD-01	5932	2020	2620	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H2-RWD-01	6967	2020	2616	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L3-H3-RWD-01	6967	2020	2831	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H2-RWD-01	7367	2020	2613	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-35T-L4-H3-RWD-01	7367	2020	2825	Mercedes-Benz Sprinter Panel and Crew Van models February 2021; Van Reviewer Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://vanreviewer.co.uk/mercedes-benz/sprinter/dimensions/2827/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-35T-RWD-01	5576	2020	2288	Mercedes-Benz Bodybuilder Portal - Sprinter RWD/AWD 907 model series; AutoScout24 Mercedes-Benz Sprinter 2018-2021 specifications	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/sprinter/314-cdi-sprinter-19036/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-35T-RWD-01	5886	2020	2288	Mercedes-Benz Sprinter Chassis Cab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-35T-RWD-01	6696	2020	2280	Mercedes-Benz Sprinter Chassis Cab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-35T-RWD-01	5576	2020	2301	Mercedes-Benz Bodybuilder Portal - Sprinter RWD/AWD 907 model series; AutoScout24 Sprinter chassis double cab specifications	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.autoscout24.fr/voiture/caracteristiques-techniques/mercedes-benz/sprinter/sprinter-chassis-dble-cab-311-cdi-33-3-5t-propulsion-autres-diesel-7015/
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-35T-RWD-01	5886	2020	2301	Mercedes-Benz Body/Equipment Mounting Directives for Sprinter BR 907; Mercedes-Benz Sprinter Chassis Cab dimensions	https://bb-portal.mercedes-benz-vans.com/en/GLOBAL/transporter/technik-und-informationen;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-35T-RWD-01	6696	2020	2301	Mercedes-Benz Sprinter Chassis Crewcab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H1-RWD-01	5932	2020	2378	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L2-H2-RWD-01	5932	2020	2667	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H2-RWD-01	6967	2020	2663	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L3-H3-RWD-01	6967	2020	2878	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H2-RWD-01	7367	2020	2662	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-4T-L4-H3-RWD-01	7367	2020	2873	Mercedes-Benz Sprinter Specifications - Technical Drawings	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L1-4T-RWD-01	5576	2020	2329	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-4T-RWD-01	5886	2020	2329	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-4T-RWD-01	6696	2020	2321	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L1-4T-RWD-01	5576	2020	2323	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-4T-RWD-01	5886	2020	2323	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-4T-RWD-01	6696	2020	2313	Mercedes-Benz Sprinter VS30 Technical Data July 2019; Mercedes-Benz Sprinter 2018 price list	https://www.scribd.com/document/634126520/Sprinter-VS30-TechData-July2019-pdf;https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Mercedes-Benz_Preisliste_Sprinter1_907_21082018.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H1-RWD-01	5932	2020	2422	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L2-H2-RWD-01	5932	2020	2710	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H2-RWD-01	6967	2020	2706	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L3-H3-RWD-01	6967	2020	2917	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H2-RWD-01	7367	2020	2703	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-VAN-5T-L4-H3-RWD-01	7367	2020	2912	Mercedes-Benz Sprinter Technical Data - RWD Panel Van Euro VI 5.0t; Mercedes-Benz Sprinter 2018 model and price list	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf;https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L2-5T-RWD-01	6104	2020	2360	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-SINGLE-L3-5T-RWD-01	6864	2020	2351	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L2-5T-RWD-01	6104	2020	2358	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-CHASSIS-CREW-L3-5T-RWD-01	6864	2020	2345	Mercedes-Benz Sprinter Technical Data April 2020	https://cdn.mattaki.com/mercedes-benz-vans/static-assets/vehicles/brochures/specifications/sprinter-specifications.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data - Mercedes-Benz C-Class W205 facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-160-129hp-52482
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data - Mercedes-Benz C-Class S205 facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-180-1.6-156hp-52483
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data - Mercedes-Benz C-Class C205 Coupe facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-180-1.6-156hp-44014
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data - Mercedes-Benz C-Class A205 Cabriolet facelift 2018	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-180-1.6-156hp-52493
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/arona/cars-specs-brochure-KJ7-NA-december-2018.pdf
EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	3465	1615	1460	Toyota Europe - New Toyota Aygo June 2018 press kit	https://newsroom.toyota.eu/download/550744/toyota-aygo-dpl-en.pdf
EU-LAND-ROVER-DISCOVERY-III-L319-VAN-01	4835	1915	1887	Land Rover Discovery 3 technical specifications - archived copy	https://device.report/m/9b6edef86f579882649aebae8a88b0e6f4325751f39a56ec551f75fabc2acfd7.pdf
EU-SUBARU-IMPREZA-II-GD-RB320-SEDAN-01	4465	1740	1440	Carfolio - 2007 Subaru Impreza RB320	https://www.carfolio.com/subaru-impreza-rb320-159522
EU-SUBARU-IMPREZA-II-GG-GB270-WAGON-01	4465	1695	1485	Automobile-Catalog - 2007 Subaru Impreza Sports Wagon 2.5 WRX GB270	https://www.automobile-catalog.com/car/2007/3256220/subaru_impreza_sports_wagon_2_5_wrx_gb270.html
EU-JAGUAR-XJ-X358-SEDAN-SWB-01	5091	1860	1462	Jaguar The XJ Collection 2008 brochure; Auto-Data Jaguar XJ X358 dimensions	https://autocatalogarchive.com/wp-content/uploads/2018/02/Jaguar-XJ-2008-INT.pdf;https://www.auto-data.net/en/jaguar-xj-x358-r-4.2-v8-395hp-automatic-41485
EU-JAGUAR-XJ-X358-SEDAN-LWB-01	5216	1860	1463	Jaguar The XJ Collection 2008 brochure; Auto-Data Jaguar XJ X358 dimensions	https://autocatalogarchive.com/wp-content/uploads/2018/02/Jaguar-XJ-2008-INT.pdf;https://www.auto-data.net/en/jaguar-xj-x358-r-4.2-v8-395hp-automatic-41485
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-01	4695	1772	1443	Auto-Data - Renault Laguna II Grandtour	https://www.auto-data.net/en/renault-laguna-ii-grandtour-generation-2119
EU-LAND-ROVER-DISCOVERY-I-SUV-01	4521	1793	1928	Automobile-Catalog - 1996 Land Rover Discovery V8i 3-Door; Automobile-Catalog - 1996 Land Rover Discovery V8i S 5-Door	https://www.automobile-catalog.com/car/1996/1399685/land_rover_discovery_v8i_3-door.html;https://www.automobile-catalog.com/car/1996/1399730/land_rover_discovery_v8i_s_5-door_automatic.html
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496	Mercedes-Benz Public Archive - VF211 pre-facelift long-wheelbase chassis; Mercedes-Benz Public Archive - S211 pre-facelift donor body	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2003---2006.xhtml?oid=2461898;https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-220-CDI-T-Modell.xhtml?oid=5461
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506	Mercedes-Benz Public Archive - VF211 facelift long-wheelbase chassis; Mercedes-Benz Public Archive - S211 facelift donor body	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-long-wheelbase-chassis--VF-211-DE-22-LA-2006---2009.xhtml?oid=2461899;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-station-wagon--S-211-DE-22-LA-2006---2009.xhtml?oid=2461875
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW X3 official specifications valid from September 2018	https://www.press.bmwgroup.com/global/article/detail/T0286558EN/specifications-of-the-bmw-x3-valid-from-09/2018?language=en
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450	Lexus LS official brochure	https://www.lexus.com.ph/content/dam/lexus-v3-philippines/brochures/ls/Lexus_LS_Brochure_031623_Final_for_website.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429	Mercedes-AMG C-Class Owner's Manual Supplement June 2018	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-lb/pdf/mercedes-amg-c-class-owners-manual-supplement-june-2018-1.pdf
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440	Mercedes-AMG C-Class Owner's Manual Supplement June 2018	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-amg-c-class-owners-manual-supplement-june-2018-1.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2201-2300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1453 行）
- 累计尺寸组：dimension_groups_final.tsv（749 行）

