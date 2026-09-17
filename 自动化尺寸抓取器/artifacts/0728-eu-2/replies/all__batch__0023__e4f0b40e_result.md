# 任务：all 第 2201-2300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0023__e4f0b40e


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
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391
EU-AUDI-A4-B7-CONVERTIBLE-02	4570	1780	1390
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453
EU-AUDI-A4-B7-WAGON-5D-02	4586	1772	1427
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-AUDI-A6-C7-AVANT-WAGON-01	4926	1874	1468
EU-AUDI-A6-C7-SEDAN-01	4915	1874	1468
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-BMW-X3-E83-SUV-5D-FACELIFT-01	4569	1853	1674
EU-BMW-X5-E70-SUV-01	4854	1933	1766
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	5258	1717	1702
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	5258	1717	1656
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	5258	1717	1618
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	5258	1717	1694
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	5258	1717	1648
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	5258	1717	1613
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	4887	1717	1694
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	4887	1717	1648
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	4887	1717	1613
EU-CHRYSLER-SEBRING-I-COUPE-01	4760	1770	1296
EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	4843	1793	1394
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407
EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	4730	1829	1323
EU-MAZDA-626-V-GF-SEDAN-01	4575	1710	1430
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-03	4765	1795	1440
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704
EU-OPEL-ANTARA-A-SUV-02	4575	1850	1704
EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	4839	1798	1500
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-B-MPV-OPC-01	4467	1801	1645
EU-OPEL-ZAFIRA-B-MPV-PREFL-01	4467	1801	1645
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mazda	6	2.5 MZR	Schrägheck	Frontantrieb	Benzin	125	170	Aug 2007	Mar 2013	2024-03-01	25463
Mazda	6	2.0 Mzr-cd	Schrägheck	Frontantrieb	Diesel	103	140	Aug 2007	Oct 2009	2024-03-01	25464
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	105	143	Sep 2007	Oct 2011	2024-03-01	25465
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	105	143	Feb 2007	Oct 2011	2024-03-01	25466
BMW	3	335 XI	Stufenheck	Allrad	Benzin	225	306	Mar 2007	Aug 2008	2024-03-01	25467
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	160	218	Mar 2007	Dec 2011	2024-03-01	25468
BMW	3	325 XI	Stufenheck	Allrad	Benzin	160	218	Sep 2007	Aug 2008	2024-03-01	25469
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	125	170	Sep 2007	Oct 2011	2024-03-01	25470
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	130	177	Sep 2007	Feb 2010	2024-03-01	25471
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	200	272	Sep 2007	Oct 2011	2024-03-01	25472
BMW	3	330 XI	Stufenheck	Allrad	Benzin	200	272	Sep 2007	Aug 2008	2024-03-01	25473
BMW	3	318 I	Kombi	Heckantrieb	Benzin	105	143	May 2007	May 2012	2024-03-01	25474
BMW	3	318 D	Kombi	Heckantrieb	Diesel	105	143	Sep 2007	Jun 2012	2024-03-01	25475
BMW	3	320 I	Kombi	Heckantrieb	Benzin	125	170	Feb 2007	Dec 2012	2024-03-01	25476
BMW	3	335 XI	Kombi	Allrad	Benzin	225	306	Mar 2007	Aug 2008	2024-03-01	25477
BMW	3	330 I	Kombi	Heckantrieb	Benzin	200	272	Sep 2007	Jun 2012	2024-03-01	25478
BMW	3	330 XI	Kombi	Allrad	Benzin	200	272	Sep 2007	Jun 2012	2024-03-01	25479
BMW	3	325 I	Kombi	Heckantrieb	Benzin	160	218	Sep 2007	Jun 2012	2024-03-01	25480
BMW	3	325 XI	Kombi	Allrad	Benzin	160	218	Sep 2007	Aug 2008	2024-03-01	25481
BMW	3	320 D	Kombi	Heckantrieb	Diesel	130	177	Feb 2007	Dec 2010	2024-03-01	25482
BMW	3	325 I	Coupe	Heckantrieb	Benzin	160	218	Sep 2007	Jun 2013	2024-03-01	25483
BMW	3	325 XI	Coupe	Allrad	Benzin	160	218	Sep 2007	Aug 2008	2024-03-01	25484
BMW	3	335 XI	Coupe	Allrad	Benzin	225	306	Mar 2007	Feb 2010	2024-03-01	25485
BMW	3	325 D	Cabriolet	Heckantrieb	Diesel	145	197	Mar 2007	Dec 2010	2024-03-01	25486
BMW	3	320 D	Cabriolet	Heckantrieb	Diesel	130	177	Mar 2008	Feb 2010	2024-03-01	25487
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	90	122	Mar 2007	Dec 2011	2024-03-01	25488
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	130	177	Sep 2007	Dec 2009	2024-03-01	25489
BMW	5	520 D	Kombi	Heckantrieb	Diesel	130	177	Sep 2007	May 2010	2024-03-01	25490
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	125	170	Sep 2007	Dec 2009	2024-03-01	25491
BMW	5	520 I	Kombi	Heckantrieb	Benzin	125	170	Sep 2007	Dec 2010	2024-03-01	25492
BMW	6	630 I	Coupe	Heckantrieb	Benzin	200	272	Sep 2007	Aug 2010	2024-03-01	25493
BMW	6	635 D	Coupe	Heckantrieb	Diesel	210	286	Jul 2007	Jul 2010	2024-03-01	25494
BMW	6	635 D	Cabriolet	Heckantrieb	Diesel	210	286	Jul 2007	Jul 2010	2024-03-01	25495
BMW	6	630 I	Cabriolet	Heckantrieb	Benzin	200	272	Sep 2007	Aug 2010	2024-03-01	25496
BMW	X3	2.0 SD	SUV	Allrad	Diesel	130	177	Sep 2007	Aug 2008	2024-03-01	25497
BMW	X5	3.0 SD	SUV	Allrad	Diesel	210	286	Oct 2007	Sep 2008	2024-03-01	25498
Opel	Vectra c caravan	1.6	Kombi	Frontantrieb	Benzin	77	105	Dec 2005	Aug 2008	2024-03-01	25499
Opel	Vectra c caravan	2.8 V6 Turbo	Kombi	Frontantrieb	Benzin	184	250	Aug 2005	Aug 2008	2024-03-01	25500
Opel	Zafira	1.6	Großraumlimousine	Frontantrieb	Benzin	85	115	Jan 2008	Apr 2015	2024-03-01	25501
Opel	Zafira	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	81	110	Jan 2008	Apr 2015	2024-03-01	25502
Opel	Zafira	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	92	125	Mar 2007	Apr 2015	2024-03-01	25503
Opel	Antara a	2.0 Cdti	SUV	Allrad	Diesel	93	127	Mar 2007	Dec 2011	2024-03-01	25504
Mercedes-benz	E-Klasse	E 230	Stufenheck	Heckantrieb	Benzin	150	204	Sep 2007	Dec 2008	2024-03-01	25505
Audi	A4 b8 avant	1.8 Tfsi	Kombi	Frontantrieb	Benzin	118	160	Nov 2007	Mar 2012	2024-03-01	25506
Audi	A4 b8 avant	3.2 FSI Quattro	Kombi	Allrad	Benzin	195	265	Apr 2008	Mar 2012	2024-03-01	25507
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	105	143	Apr 2008	Dec 2015	2024-03-01	25508
Audi	A4 b8 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	176	240	Apr 2008	Mar 2012	2024-03-01	25509
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	125	170	Apr 2008	Mar 2012	2024-03-01	25510
Suzuki	Samurai	1.9 D Allrad	Geländewagen geschlossen	Allrad	Diesel	47	64	Nov 1998	Dec 2004	2024-03-01	25511
Lancia	Zeta	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	80	109	Sep 1999	Sep 2002	2024-03-01	25512
Toyota	Celica	2.2	Coupe	Frontantrieb	Benzin	100	136	Oct 1989	Dec 1994	2024-03-01	25519
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	140	190	Sep 1998	Sep 2003	2024-03-01	25536
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	160	218	Jun 1999	Sep 2003	2024-03-01	25537
Nissan	Urvan	2	Kasten	Heckantrieb	Benzin	65	88	Jun 1986	Sep 1994	2024-03-01	25563
BMW	3	330 I	Cabriolet	Heckantrieb	Benzin	190	258	Mar 2010	Oct 2013	2024-03-01	25583
Nissan	X-Trail ii	2.0 FWD	SUV	Frontantrieb	Benzin	104	141	Mar 2007	Nov 2013	2024-03-01	25648
Audi	A6 c7	2.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	155	211	May 2012	Apr 2015	2024-03-01	25658
Renault	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	50	68	Apr 2007	-	2024-03-01	25659
Renault	Logan	1.6	Stufenheck	Frontantrieb	Benzin	77	105	Apr 2007	Oct 2013	2024-03-01	25660
Chevrolet	Avalanche	5.3	Pick-up	Heckantrieb	Benzin	220	299	Oct 2000	Sep 2006	2024-03-01	25661
Chevrolet	Avalanche	8.1	Pick-up	Heckantrieb	Benzin	253	344	Oct 2000	Sep 2006	2024-03-01	25663
Chevrolet	Colorado	2.9	Pick-up	Heckantrieb	Benzin	139	189	Oct 2006	-	2024-03-01	25665
Chevrolet	Colorado	3.7	Pick-up	Heckantrieb	Benzin	181	246	Oct 2006	-	2024-03-01	25667
Chevrolet	Colorado	3.7 4X4	Pick-up	Allrad	Benzin	181	246	Oct 2006	-	2024-03-01	25668
Ford USA	Explorer	4.6 4WD	SUV	Allrad	Benzin	218	296	May 2006	Dec 2010	2024-03-01	25673
Audi	A6 c7	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	162	220	May 2013	Sep 2018	2024-03-01	25690
Ford USA	Thunderbird	3.8	Coupe	Heckantrieb	Benzin	104	141	Jan 1993	Dec 1996	2024-03-01	25743
Fiat	Punto	1.4 Multi AIR	Schrägheck	Frontantrieb	Benzin	77	105	Mar 2012	-	2024-03-01	25762
Chrysler	Sebring	2.7 VVT	Cabriolet	Frontantrieb	Benzin	141	192	Jul 2007	Dec 2010	2024-03-01	25886
Chrysler	Sebring	2.7 VVT	Stufenheck	Frontantrieb	Benzin	141	192	Sep 2006	Dec 2010	2024-03-01	25887
Fiat	Punto	1.4	Schrägheck	Frontantrieb	Benzin	57	78	Mar 2012	-	2024-03-01	25909
Hyundai	Elantra v	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	94	128	Feb 2011	Dec 2015	2024-03-01	25918
Rolls-royce	Wraith	V12	Coupe	Heckantrieb	Benzin	465	632	Aug 2013	-	2024-03-01	25931
Toyota	Previa iii	2.4	Großraumlimousine	Frontantrieb	Benzin	125	170	Oct 2005	-	2024-03-01	25973
Fiat	Punto	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Mar 2012	-	2024-03-01	26003
Fiat	Punto	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Mar 2012	-	2024-03-01	26004
Mercedes-benz	Sprinter 3,5-T	313 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	95	129	Jun 2006	Dec 2016	2024-03-01	26018
Toyota	Scepter	2.2	Stufenheck	Frontantrieb	Benzin	100	136	Nov 1992	Sep 1996	2024-03-01	26082
Toyota	Isis	1.8 Vvti	Großraumlimousine	Frontantrieb	Benzin	97	132	Jul 2004	Aug 2014	2024-03-01	26145
Toyota	Highlander	3.3	SUV	Frontantrieb	Benzin	171	233	Aug 2003	May 2007	2024-03-01	26163
Alfa Romeo	Giulietta	1.8 TBI	Schrägheck	Frontantrieb	Benzin	177	241	Sep 2013	Oct 2018	2024-03-01	26235
Nissan	Cima	4.1	Stufenheck	Heckantrieb	Benzin	198	269	Jul 1996	Feb 2001	2024-03-01	26308
Fiat	Punto	0.9 Twinair Turbo	Schrägheck	Frontantrieb	Benzin	63	86	Mar 2012	-	2024-03-01	26324
Toyota	Sprinter	1.6 GTI	Coupe	Frontantrieb	Benzin	91	124	Oct 1984	Jul 1987	2024-03-01	26357
Nissan	Cima	4.1	Stufenheck	Heckantrieb	Benzin	198	269	Sep 1991	Jun 1996	2024-03-01	26400
Toyota	Sienna	3	Großraumlimousine	Frontantrieb	Benzin	143	194	Aug 1997	Dec 2002	2024-03-01	26427
Daihatsu	Rugger	2.0 4X4	Geländewagen geschlossen	Allrad	Benzin	65	88	Apr 1984	Oct 1988	2024-03-01	26478
Daihatsu	Rugger	2.8 D 4X4	Geländewagen geschlossen	Allrad	Diesel	54	73	Apr 1984	Apr 1993	2024-03-01	26479
Daihatsu	Rugger	2.8 Tdic 4X4	Geländewagen geschlossen	Allrad	Diesel	75	102	May 1993	Jun 1996	2024-03-01	26485
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	55	75	Mar 2012	-	2024-03-01	26491
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	62	84	Mar 2012	-	2024-03-01	26492
Fiat	Punto	1.4 Turbo Multi AIR	Schrägheck	Frontantrieb	Benzin	99	135	Mar 2012	-	2024-03-01	26495
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	70	95	Mar 2012	-	2024-03-01	26496
Renault	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	50	68	Apr 2007	-	2024-03-01	26543
Renault	Logan	1.6	Kombi	Frontantrieb	Benzin	64	87	Apr 2007	-	2024-03-01	26544
Renault	Logan	1.6	Kombi	Frontantrieb	Benzin	77	105	Apr 2007	-	2024-03-01	26545
Renault	Logan	1.4	Kombi	Frontantrieb	Benzin	55	75	Oct 2007	-	2024-03-01	26546
Audi	A4 b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	89	121	Sep 2005	Sep 2006	2024-03-01	26547
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	89	121	Sep 2005	Sep 2006	2024-03-01	26548
Audi	A6 c6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	89	121	Sep 2005	Jun 2006	2024-03-01	26549


--- Round 1 / 首次发送 ---
更新点

* 已优先完成可复用缓存组的批量关联，闭合 BMW E9x、BMW 5/X3/X5、Opel、Audi、Mustang、Explorer 等 49 个 Ktype。
* 对跨改款且外廓不同的 BMW E90/E91/E92、Audi A4 B8 生成稳定派生行，不保留无后缀基础行。
* Opel Antara 25504 的既有双组冲突已完成必要核对，并关联 `EU-OPEL-ANTARA-A-SUV-02`。([汽车目录][1])
* 本轮全部复用既有尺寸组，未重复输出尺寸来源，未新建尺寸组。

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：49
* READY 映射行：64
* PENDING Ktype：51
* 当前引用既有尺寸组：26
* 本轮新建或修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25465_prefl	25465	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25465_facelift	25465	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25466_prefl	25466	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25466_facelift	25466	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25467	25467	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25468_prefl	25468	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25468_facelift	25468	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25469	25469	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25470_prefl	25470	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25470_facelift	25470	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25471_prefl	25471	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25471_facelift	25471	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25472_prefl	25472	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25472_facelift	25472	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25473	25473	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25474_prefl	25474	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25474_facelift	25474	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25475_prefl	25475	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25475_facelift	25475	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25476_prefl	25476	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25476_facelift	25476	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25477	25477	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH		READY
25478_prefl	25478	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25478_facelift	25478	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25479_prefl	25479	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25479_facelift	25479	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25480_prefl	25480	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25480_facelift	25480	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25481	25481	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH		READY
25482_prefl	25482	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25482_facelift	25482	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25483_prefl	25483	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH	改款前外廓。	READY
25483_facelift	25483	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	改款后外廓。	READY
25484	25484	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH		READY
25485	25485	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH		READY
25486	25486	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
25487	25487	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
25489	25489	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
25490	25490	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH		READY
25491	25491	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
25492	25492	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH		READY
25497	25497	SUV	X3 E83 facelift	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
25498	25498	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH		READY
25499	25499	Wagon	Vectra C facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
25500	25500	Wagon	Vectra C facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
25501	25501	MPV	Zafira B facelift		5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25502	25502	MPV	Zafira B facelift		5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25504	25504	SUV	Antara A		5	EU-OPEL-ANTARA-A-SUV-02	HIGH		READY
25506	25506	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25507	25507	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25508_prefl	25508	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
25508_facelift	25508	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
25509	25509	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25510	25510	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25511	25511	SUV	Samurai SJ413	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	HIGH		READY
25536	25536	Coupe	Mustang IV facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH		READY
25537	25537	Convertible	Mustang IV facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH		READY
25583	25583	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH		READY
25658	25658	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-SEDAN-01	HIGH		READY
25673	25673	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH		READY
26235	26235	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
26547	26547	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26548	26548	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	HIGH		READY
26549	26549	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 闭合高复用新组：BMW 6 E63/E64、Fiat Punto 199、Renault Logan Sedan/MCV。
2. 核对 Mazda 6 GH 三个既有 Hatchback 组与 25463、25464 的改款边界。
3. 处理 Chevrolet Avalanche、Colorado 的 CAB、悬架高度和多外廓派生。
4. 处理 Mercedes Sprinter 26018 的轴距、驾驶室和底盘分支。
5. 批量闭合其余日系老款和进口车型尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/2541050/opel_antara_2_0_cdti_127_4x4.html?utm_source=chatgpt.com "2007 Opel Antara 2.0 CDTI (127) 4x4 Specs Review (93.5 kW / 127 PS / 125 hp) (since June 2007 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 本轮闭合 17 个 Ktype：Mazda 6 GH 2 个、BMW E81 1 个、BMW E63/E64 4 个、Opel Zafira B 1 个、Fiat Punto 2012 共 9 个。
* Mazda 6 GH 复用现有 Hatchback 尺寸组；BMW E81 与 Zafira B facelift 复用现有组，不重复输出尺寸组。
* 首次创建 BMW 6 Series E63 Coupé、E64 Convertible 和 Fiat Punto 2012 三个尺寸组。BMW 官方技术资料确认 E63/E64 三维均为 `4820 × 1855 × 1374 mm`；Fiat 官方资料确认 Punto 2012 三维为 `4065 × 1687 × 1490 mm`。

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：66
* READY 映射行：81
* PENDING Ktype：34
* 当前引用尺寸组：31
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25463	25463	Hatchback	Mazda6 II (GH)	GH5FS	5	EU-MAZDA-6-II-GH-HATCHBACK-01	HIGH		READY
25464	25464	Hatchback	Mazda6 II (GH)	GH14	5	EU-MAZDA-6-II-GH-HATCHBACK-01	HIGH		READY
25488	25488	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
25493	25493	Coupe	6 Series E63 LCI	E63	2	EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	HIGH		READY
25494	25494	Coupe	6 Series E63 LCI	E63	2	EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	HIGH		READY
25495	25495	Convertible	6 Series E64 LCI	E64	2	EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	HIGH		READY
25496	25496	Convertible	6 Series E64 LCI	E64	2	EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	HIGH		READY
25503	25503	MPV	Zafira B facelift	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25762	25762	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
25909	25909	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26003	26003	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26004	26004	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26324	26324	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26491	26491	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26492	26492	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26495	26495	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26496	26496	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	4820	1855	1374	BMW Group – The new BMW 6 Series Coupé and Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0037654EN/76891
EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	4820	1855	1374	BMW Group – The new BMW 6 Series Coupé and Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0037654EN/76891
EU-FIAT-PUNTO-2012-HATCHBACK-01	4065	1687	1490	Fiat Punto 2012 official press kit	https://www.media.stellantis.com/be-fr/fiat/press/fiat-punto-2012-l-evolution-d-un-best-seller
```

下一步优先处理

1. 批量闭合 Renault Logan Sedan 与 Logan MCV 的 6 个 Ktype。
2. 处理 Chevrolet Avalanche、Colorado 的驾驶室、悬架高度及多外廓派生。
3. 闭合 Chrysler Sebring Sedan/Convertible、Hyundai Elantra V、Nissan X-Trail T31。
4. 处理 Mercedes-Benz Sprinter 26018 的轴距及底盘驾驶室分支。
5. 最后集中处理老款日系车型和 Daihatsu Rugger 多轴距外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 复用既有 `EU-AUDI-A6-C7-SEDAN-01`，完成 Ktype `25690` 关联。
* 首次创建 Hyundai Elantra V MD 四门轿车尺寸组。Hyundai 官方 2011 Elantra 规格给出的车身三维为 `4530 × 1775 × 1435 mm`。([现代新闻][1])
* 首次创建 Rolls-Royce Wraith 双门轿跑尺寸组。Rolls-Royce 官方 Wraith press kit 给出的三维为 `5269 × 1947 × 1507 mm`。([BMW Group PressClub][2])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：69
* READY 映射行：84
* PENDING Ktype：31
* 当前引用尺寸组：33
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25690	25690	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-SEDAN-01	HIGH		READY
25918	25918	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-01	MEDIUM	第五代MD四门车身。	READY
25931	25931	Coupe	Wraith		2	EU-ROLLS-ROYCE-WRAITH-COUPE-2D-01	HIGH		READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-01	4530	1775	1435	Hyundai Motor America – 2011 Hyundai Elantra official specifications	https://www.hyundainews.com/releases/1597
EU-ROLLS-ROYCE-WRAITH-COUPE-2D-01	5269	1947	1507	Rolls-Royce Motor Cars – Wraith press kit	https://www.press.rolls-roycemotorcars.com/rolls-royce-motor-cars-pressclub/article/attachment/T0137422EN/283872
```

下一步优先处理

1. 闭合 Renault Logan Sedan 与 Logan MCV 的 6 个 Ktype。
2. 核对 Nissan X-Trail T31 改款前后外廓，并完成必要派生。
3. 批量处理 Chrysler Sebring Sedan/Convertible 与 Lancia Zeta。
4. 拆解 Chevrolet Avalanche、Colorado 的车身和悬架高度分支。
5. 处理 Sprinter 底盘驾驶室以及剩余老款日系、Daihatsu Rugger。

推进信号：CONTINUE

[1]: https://www.hyundainews.com/releases/1597?utm_source=chatgpt.com "THE 2011 HYUNDAI ELANTRA: THE NEW STANDARD FOR COMPACT SEDANS - Releases - Official Media Site NEWSROOM"
[2]: https://www.press.rolls-roycemotorcars.com/rolls-royce-motor-cars-pressclub/article/attachment/T0137422EN/283872?utm_source=chatgpt.com "https://www.press.rolls-roycemotorcars.com/rolls-r..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 完成 Mercedes-Benz E 230 W211 facelift、Lancia Zeta 2.0 JTD、Chrysler Sebring Sedan 与 Convertible 共 4 个 Ktype。
* 本轮首次建立 4 个尺寸组。Mercedes-Benz 官方档案确认 E 230 车身代码及三维；Chrysler 官方规格分别确认 Sedan 与 Convertible 三维。([梅赛德斯-奔驰档案馆][1])
* Lancia Zeta 采用对应 2.0 JTD 109 PS 直接规格页，宽度口径为不含后视镜。([汽车目录][2])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：73
* READY 映射行：88
* PENDING Ktype：27
* 当前引用尺寸组：37
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25505	25505	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	HIGH		READY
25512	25512	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-5D-01	HIGH		READY
25886	25886	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	HIGH		READY
25887	25887	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	4856	1822	1483	Mercedes-Benz Classic Archive – E 230 W 211 E 25	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/E-230.xhtml?oid=2461836
EU-LANCIA-ZETA-220-MPV-5D-01	4470	1834	1714	Automobile-Catalog – 1999 Lancia Zeta 2.0 JTD LX	https://www.automobile-catalog.com/car/1999/1383935/lancia_zeta_2_0_jtd_lx.html
EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	4922	1816	1485	Chrysler Media – 2009 Chrysler Sebring Convertible Specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2009_ChryslerSebringConvertibleSpecifications.pdf
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4842	1808	1498	Chrysler Media – 2007 Chrysler Sebring Specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2007ChryslerSebringFASpecifications.pdf
```

下一步优先处理

1. Nissan Cima Y32/Y33、Ford Thunderbird X、Toyota Celica T180 等单一老款车身。
2. Toyota Sienna、Highlander、Scepter 与 Sprinter 底盘驾驶室。
3. Renault Logan Sedan/MCV 的改款前后外廓拆分。
4. Chevrolet Avalanche 与 Colorado 多驾驶室、悬架高度分支。
5. 最后处理 Toyota Isis、Previa III 与 Daihatsu Rugger 的多外廓边界。

推进信号：CONTINUE

[1]: https://mercedes-benz-archive.com/marsClassic/en/instance/ko/E-230.xhtml?oid=2461836 "
            E 230

    "
[2]: https://www.automobile-catalog.com/car/1999/1383935/lancia_zeta_2_0_jtd_lx.html?utm_source=chatgpt.com "1999 Lancia Zeta 2.0 JTD LX Specs Review (80 kW / 109 PS / 107 hp) (since mid-year 1999 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 复用既有 Zafira B facelift 尺寸组，完成 Ktype `25502`。
* Nissan X-Trail T31 在该 Ktype 覆盖期内存在改款前后外廓差异，拆分为 `4630 × 1785 × 1685 mm` 与 `4635 × 1790 × 1700 mm` 两组。([汽车目录][1])
* 完成 Ford Thunderbird X（MN12）3.8 Coupé，三维为 `5088 × 1847 × 1334 mm`。([汽车目录][2])
* Toyota Sienna I（XL10）在 2001 年改款后长度由 `4915 mm` 增至 `4933 mm`，宽度和高度保持 `1864 × 1709 mm`，因此拆分两组。([Edmunds][3])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：77
* READY 映射行：94
* PENDING Ktype：23
* 当前引用尺寸组：42
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25502	25502	MPV	Zafira B facelift	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25648_prefl	25648	SUV	X-Trail II T31	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	HIGH	改款前外廓。	READY
25648_facelift	25648	SUV	X-Trail II T31	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
25743	25743	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	HIGH		READY
26427_prefl	26427	MPV	Sienna I	XL10	5	EU-TOYOTA-SIENNA-I-XL10-MPV-PREFL-01	HIGH	2001年改款前外廓。	READY
26427_facelift	26427	MPV	Sienna I	XL10	5	EU-TOYOTA-SIENNA-I-XL10-MPV-FACELIFT-01	HIGH	2001年改款后外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685	Automobile-Catalog – 2007 Nissan X-Trail T31 specifications	https://www.automobile-catalog.com/car/2007/2316080/nissan_x-trail_2_0_dci_150_se_automatic.html
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700	Automobile-Catalog – 2011 Nissan X-Trail T31 facelift specifications	https://www.automobile-catalog.com/car/2011/2316620/nissan_x-trail_2_0_dci_173_tekna.html
EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	5088	1847	1334	Automobile-Catalog – 1994 Ford Thunderbird LX 3.8L	https://www.automobile-catalog.com/car/1994/879350/ford_thunderbird_lx_3_8l_v-6_automatic.html
EU-TOYOTA-SIENNA-I-XL10-MPV-PREFL-01	4915	1864	1709	Edmunds – 1998 Toyota Sienna 3.0 specifications	https://www.edmunds.com/toyota/sienna/1998/features-specs/
EU-TOYOTA-SIENNA-I-XL10-MPV-FACELIFT-01	4933	1864	1709	Edmunds – 2001 Toyota Sienna 3.0 specifications	https://www.edmunds.com/toyota/sienna/2001/features-specs/
```

下一步优先处理

1. Nissan Cima Y32、Y33 与 Toyota Scepter、Isis 等单一日系车身。
2. Renault Logan Sedan 与 Logan MCV 的改款前后尺寸组。
3. Chevrolet Avalanche 与 Colorado 的车身、驾驶室和悬架分支。
4. Mercedes-Benz Sprinter 底盘驾驶室的轴距分支。
5. 最后集中处理 Nissan Urvan、Toyota Celica、Previa、Sprinter Trueno 与 Daihatsu Rugger 多外廓边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/2316080/nissan_x-trail_2_0_dci_150_se_automatic.html?utm_source=chatgpt.com "2007 Nissan X-Trail 2.0 dCi 150 SE automatic (aut. 6)"
[2]: https://www.automobile-catalog.com/car/1994/879350/ford_thunderbird_lx_3_8l_v-6_automatic.html?utm_source=chatgpt.com "1994 Ford Thunderbird LX 3.8L V-6 automatic (aut. 4)"
[3]: https://www.edmunds.com/toyota/sienna/1998/features-specs/ "Used 1998 Toyota Sienna Specs & Features | Edmunds"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 按唯一 `Ktype` 和 `id` 重新计数，修正上一轮将已完成的 `25502` 重复计入进度的问题。
* 完成 Nissan Cima FY32、FY33 两个独立车身。FY32 为 `4930 × 1780 × 1420 mm`，FY33 为 `4970 × 1820 × 1445 mm`。([日产汽车][1])
* 完成 Renault Logan MCV 的 4 个 Ktype，并按 2008 年改款拆分。改款前为 `4450 × 1740 × 1674 mm`，改款后为 `4473 × 1740 × 1640 mm`；来源分别列出含后视镜宽度，因此落盘宽度可确认是不含后视镜口径。([汽车数据网][2])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：82
* READY 映射行：103
* PENDING Ktype：18
* 当前引用尺寸组：46
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26308	26308	Sedan	Cima III	FGY33	4	EU-NISSAN-CIMA-III-FY33-SEDAN-4D-01	HIGH		READY
26400	26400	Sedan	Cima II	FGY32	4	EU-NISSAN-CIMA-II-FY32-SEDAN-4D-01	HIGH		READY
26543_prefl	26543	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26543_facelift	26543	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26544_prefl	26544	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26544_facelift	26544	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26545_prefl	26545	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26545_facelift	26545	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26546_prefl	26546	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26546_facelift	26546	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-CIMA-III-FY33-SEDAN-4D-01	4970	1820	1445	GAZOO Car Catalog – Nissan Cima 41L (E-FGY33)	https://gazoo.com/catalog/maker/NISSAN/CIMA/199606/1500485/
EU-NISSAN-CIMA-II-FY32-SEDAN-4D-01	4930	1780	1420	Nissan Heritage Collection – Cima Type III Limited L	https://www2.nissan.co.jp/HERITAGE/DETAIL/431.html
EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	4450	1740	1674	Auto-Data – Dacia Logan I MCV 1.5 dCi (68 Hp) 7 Seats	https://www.auto-data.net/en/dacia-logan-i-mcv-1.5-dci-68hp-7-seats-15884
EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data – Dacia Logan I MCV facelift 1.6 16V (105 Hp)	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-16v-105hp-46170
```

下一步优先处理

1. 解决 Renault Logan Sedan 在 Renault/Dacia 市场版本之间的长度与宽度冲突。
2. 批量处理 Toyota Scepter、Isis、Previa III、Highlander及 Sprinter Trueno。
3. 拆解 Chevrolet Avalanche 与 Colorado 的驾驶室、悬架和车身分支。
4. 处理 Mercedes-Benz Sprinter 底盘驾驶室及 Nissan Urvan 的轴距分支。
5. 最后处理 Daihatsu Rugger 的短轴、长轴及改款外廓。

推进信号：CONTINUE

[1]: https://www2.nissan.co.jp/HERITAGE/DETAIL/431.html "日産： NISSAN HERITAGE COLLECTION｜シーマ タイプIII リミテッドL"
[2]: https://www.auto-data.net/en/dacia-logan-i-mcv-1.5-dci-68hp-7-seats-15884 "Dacia Logan I MCV 1.5 dCi (68 Hp) 7 Seats | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
更新点

* 完成 Toyota Scepter XV10 轿车，并按 1994 年外廓变化拆分：改款前 `4780 × 1770 × 1410 mm`，改款后 `4790 × 1770 × 1410 mm`。([トヨタの中古車【トヨタ公式 GAZOO中古車サイト】][1])
* 完成 Toyota Isis 1.8，并按标准车身改款前、标准车身改款后及 Platana 外部套件拆分三个物理外廓。([トヨタの中古車【トヨタ公式 GAZOO中古車サイト】][2])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：84
* READY 映射行：108
* PENDING Ktype：16
* 当前引用尺寸组：51
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26082_prefl	26082	Sedan	Scepter XV10	SXV10	4	EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
26082_facelift	26082	Sedan	Scepter XV10	SXV10	4	EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-FACELIFT-01	HIGH	1994年改款后外廓。	READY
26145_standard_prefl	26145	MPV	Isis I	ZNM10G	5	EU-TOYOTA-ISIS-I-MPV-STANDARD-PREFL-01	HIGH	标准车身改款前外廓。	READY
26145_standard_facelift	26145	MPV	Isis I	ZGM10G	5	EU-TOYOTA-ISIS-I-MPV-STANDARD-FACELIFT-01	HIGH	标准车身改款后外廓。	READY
26145_platana	26145	MPV	Isis I	ZGM10W	5	EU-TOYOTA-ISIS-I-MPV-PLATANA-01	HIGH	Platana外部套件外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-PREFL-01	4780	1770	1410	Toyota GAZOO – Scepter Sedan 2.2G	https://gazoo.com/catalog/maker/TOYOTA/SCEPTER_SEDAN/199211/1006944/
EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-FACELIFT-01	4790	1770	1410	Toyota GAZOO – Scepter Sedan 2.2	https://gazoo.com/catalog/maker/TOYOTA/SCEPTER_SEDAN/199211/1001046/
EU-TOYOTA-ISIS-I-MPV-STANDARD-PREFL-01	4610	1695	1640	Toyota GAZOO – Isis L 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10030858/
EU-TOYOTA-ISIS-I-MPV-STANDARD-FACELIFT-01	4635	1695	1640	Toyota GAZOO – Isis L G Edition 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10057945/
EU-TOYOTA-ISIS-I-MPV-PLATANA-01	4640	1710	1640	Toyota GAZOO – Isis Platana Black Limited 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10065264/
```

下一步优先处理

1. 闭合 Renault Logan Sedan 的改款前后外廓。
2. 处理 Toyota Previa III 标准车身与 Aeras 外部套件分支。
3. 处理 Toyota Highlander、Celica及 Sprinter Trueno。
4. 集中拆解 Chevrolet Avalanche、Colorado 的驾驶室和悬架分支。
5. 最后处理 Mercedes-Benz Sprinter、Nissan Urvan 与 Daihatsu Rugger 多轴距外廓。

推进信号：CONTINUE

[1]: https://gazoo.com/catalog/maker/TOYOTA/SCEPTER_SEDAN/199211/1006944/ "セプターセダン(1992年11月～1993年8月) ２．２Ｇ| トヨタ自動車のクルマ情報サイト‐GAZOO"
[2]: https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10030858/?utm_source=chatgpt.com "アイシス(2005年11月～2007年5月) L| トヨタ自動車のクルマ情報 ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
更新点

* 完成 Renault Logan Sedan 两个 Ktype，并按 2008 年改款拆分：改款前 `4250 × 1742 × 1534 mm`，改款后 `4288 × 1740 × 1534 mm`；宽度均为不含后视镜口径。([汽车目录][1])
* 完成 Toyota Celica V ST184 2.2 Coupé，统一换算为 `4470 × 1704 × 1285 mm`。([Edmunds][2])
* 完成 Toyota Highlander I facelift 3.3 FWD，并按原厂车顶架拆分无车顶架、带车顶架两个高度分支。
* 本轮首次创建 5 个尺寸组，未重复输出既有尺寸组。

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：88
* READY 映射行：115
* PENDING Ktype：12
* 当前引用尺寸组：56
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25519	25519	Coupe	Celica V (T18)	ST184	2	EU-TOYOTA-CELICA-V-T18-COUPE-2D-01	HIGH		READY
25659_prefl	25659	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
25659_facelift	25659	Sedan	Logan I facelift	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	HIGH	2008年改款后外廓。	READY
25660_prefl	25660	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
25660_facelift	25660	Sedan	Logan I facelift	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26163_norack	26163	SUV	Highlander I (XU20) facelift		5	EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-NORACK-01	HIGH	无原厂车顶架外廓。	READY
26163_roofrack	26163	SUV	Highlander I (XU20) facelift		5	EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-ROOFRACK-01	HIGH	原厂车顶架高度分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CELICA-V-T18-COUPE-2D-01	4470	1704	1285	Edmunds – 1990 Toyota Celica Coupe GT specifications	https://www.edmunds.com/toyota/celica/1990/coupe/st-11821/features-specs/
EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	4250	1742	1534	Automobile-Catalog – 2008 Dacia Logan 1.5 dCi 68 Laureate pre-facelift	https://www.automobile-catalog.com/car/2008/554630/dacia_logan_1_5_dci_68_laureate.html
EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	4288	1740	1534	Automobile-Catalog – 2008 Dacia Logan 1.5 dCi 68 facelift	https://www.automobile-catalog.com/car/2008/1221920/dacia_logan_1_5_dci_68_ambiance.html
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-NORACK-01	4689	1826	1679	Toyota – 2004 Highlander specifications brochure	https://xr793.com/wp-content/uploads/2022/01/2004-Toyota-Highlander-Specs.pdf
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-ROOFRACK-01	4689	1826	1735	Toyota – 2004 Highlander specifications brochure	https://xr793.com/wp-content/uploads/2022/01/2004-Toyota-Highlander-Specs.pdf
```

下一步优先处理

1. 利用既有九个 Colorado 尺寸组，拆分并闭合 `25665`、`25667`、`25668` 的驾驶室和悬架分支。
2. 处理 Chevrolet Avalanche 1500 与 2500 两个外廓。
3. 闭合 Toyota Previa III 2.4 的标准车身、Aeras及改款分支。
4. 核清 Toyota Sprinter 26357 的前驱 E80 Coupé边界，避免误关联后驱 AE86。
5. 最后集中处理 Nissan Urvan、Mercedes-Benz Sprinter及 Daihatsu Rugger 多轴距分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/1221920/dacia_logan_1_5_dci_68_ambiance.html?utm_source=chatgpt.com "2008 Dacia Logan 1.5 dCi 68 Specs Review (50 kW / 68 PS / 67 hp) (since mid-year 2008 for Europe )"
[2]: https://www.edmunds.com/toyota/celica/1990/coupe/st-11821/features-specs/?utm_source=chatgpt.com "Used 1990 Toyota Celica Coupe GT Specs & Features"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
更新点

* 完成 Chevrolet Colorado 三个 Ktype。依照三种驾驶室、悬架套件和驱动形式拆分：`25665` 生成 6 个分支，`25667` 生成 9 个分支，`25668` 生成 6 个分支；全部复用跨批次已有的 9 个 Colorado 尺寸组，未重复建组。该代 Colorado 提供 Regular、Extended、Crew 三种驾驶室；Z71 可对应 2WD 或 4WD，而 ZQ8 不用于本批 4WD 分支。
* 完成 Chevrolet Avalanche 两个 Ktype。5.3L 1500 与 8.1L 2500 的标准外廓三维一致，因此共同引用一个新尺寸组 `5629 × 2027 × 1869 mm`。([Edmunds][1])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：93
* READY 映射行：138
* PENDING Ktype：7
* 当前引用尺寸组：66
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25661	25661	Pickup	Avalanche I	GMT800	4	EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	HIGH	1500车身外廓。	READY
25663	25663	Pickup	Avalanche I	GMT800	4	EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	HIGH	2500车身外廓与1500三维相同。	READY
25665_regcab_z85	25665	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab Z85外廓。	READY
25665_regcab_zq8	25665	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	HIGH	Regular Cab ZQ8外廓。	READY
25665_extcab_z85	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab Z85外廓。	READY
25665_extcab_zq8	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	HIGH	Extended Cab ZQ8外廓。	READY
25665_crewcab_z85	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab Z85外廓。	READY
25665_crewcab_zq8	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	HIGH	Crew Cab ZQ8外廓。	READY
25667_regcab_z85	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab Z85外廓。	READY
25667_regcab_z71	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	HIGH	Regular Cab Z71外廓。	READY
25667_regcab_zq8	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	HIGH	Regular Cab ZQ8外廓。	READY
25667_extcab_z85	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab Z85外廓。	READY
25667_extcab_z71	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	HIGH	Extended Cab Z71外廓。	READY
25667_extcab_zq8	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	HIGH	Extended Cab ZQ8外廓。	READY
25667_crewcab_z85	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab Z85外廓。	READY
25667_crewcab_z71	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	HIGH	Crew Cab Z71外廓。	READY
25667_crewcab_zq8	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	HIGH	Crew Cab ZQ8外廓。	READY
25668_regcab_z85	25668	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab 4WD Z85外廓。	READY
25668_regcab_z71	25668	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	HIGH	Regular Cab 4WD Z71外廓。	READY
25668_extcab_z85	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab 4WD Z85外廓。	READY
25668_extcab_z71	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	HIGH	Extended Cab 4WD Z71外廓。	READY
25668_crewcab_z85	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab 4WD Z85外廓。	READY
25668_crewcab_z71	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	HIGH	Crew Cab 4WD Z71外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	5629	2027	1869	Edmunds – 2006 Chevrolet Avalanche 1500 LS specifications;Edmunds – 2006 Chevrolet Avalanche 2500 LS specifications	https://www.edmunds.com/chevrolet/avalanche/2006/st-100580431/features-specs/;https://www.edmunds.com/chevrolet/avalanche/2006/st-100580433/features-specs/
```

下一步优先处理

1. Toyota Previa III 2.4 的标准车身、Aeras及改款外廓。
2. Nissan Urvan E24 的短轴、长轴和车顶高度分支。
3. Mercedes-Benz Sprinter W906 313 CDI 底盘驾驶室的轴距与驾驶室分支。
4. Daihatsu Rugger 的短轴、长轴及改款分支。
5. 核清 Toyota Sprinter `26357` 的车身代码与输入驱动形式冲突。

推进信号：CONTINUE

[1]: https://www.edmunds.com/chevrolet/avalanche/2006/st-100580431/features-specs/?utm_source=chatgpt.com "Used 2006 Chevrolet Avalanche 1500 LS Specs & Features"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
更新点

* 完成 Toyota Previa III 2.4。对应第三代 Estima/Previa 前驱 `ACR50` 车身，三维为 `4795 × 1800 × 1730 mm`。([丰田汽车官网][1])
* 完成 Toyota Sprinter V Coupé。上游 `Frontantrieb` 与部分目录中的 `AE86` 标识冲突，因此不强写 BodyCode；按确认的 E80 双门轿跑外廓关联 `4180 × 1625 × 1335 mm`。([车指南][2])
* 完成 Daihatsu Rugger 2.0，拆分短轴硬顶与长轴 Wagon；两个发动机版本共用的物理外廓未重复建组。([汽车目录][3])
* 完成 Daihatsu Rugger 2.8 TDIC，拆分 F73 短轴和 F78 长轴欧洲出口车身。F73/F78 边界由 Daihatsu 车型目录确认，三维采用明确标注不含后视镜宽度的欧洲出口规格。([ダイハツ認定中古車・軽自動車 公式情報サイト|U-CATCH][4])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：97
* READY 映射行：144
* PENDING Ktype：3
* 当前引用尺寸组：72
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25973	25973	MPV	Previa III (XR50)	ACR50	5	EU-TOYOTA-PREVIA-III-XR50-MPV-FWD-01	HIGH		READY
26357	26357	Coupe	Sprinter V (E80)		2	EU-TOYOTA-SPRINTER-V-E80-COUPE-2D-01	MEDIUM	上游驱动字段与AE86标识冲突；保留已确认的E80双门轿跑边界，BodyCode留空。	READY
26478_swb	26478	SUV	Rugger I	F80	3	EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	HIGH	短轴硬顶外廓。	READY
26478_lwb	26478	SUV	Rugger I	F85	3	EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	HIGH	长轴Wagon外廓。	READY
26485_swb	26485	SUV	Rugger I facelift	F73	3	EU-DAIHATSU-RUGGER-I-F73-SUV-SWB-01	HIGH	F73短轴硬顶外廓。	READY
26485_lwb	26485	SUV	Rugger I facelift	F78	3	EU-DAIHATSU-RUGGER-I-F78-SUV-LWB-01	HIGH	F78长轴Wagon外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PREVIA-III-XR50-MPV-FWD-01	4795	1800	1730	Toyota 75 Years – Third-generation Estima vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000619/index.html
EU-TOYOTA-SPRINTER-V-E80-COUPE-2D-01	4180	1625	1335	Auto-Data – Toyota Corolla Coupe V E80 1.6 GT 16V	https://www.auto-data.net/en/toyota-corolla-coupe-v-e80-1.6-gt-16v-124hp-automatic-28600
EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	3775	1580	1840	Automobile-Catalog – 1984 Daihatsu Rocky 2.0 Hard-top	https://www.automobile-catalog.com/car/1984/562805/daihatsu_rocky_2_0_hard-top.html
EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	4100	1580	1915	Automobile-Catalog – 1984 Daihatsu Rocky 2.0 Wagon	https://www.automobile-catalog.com/car/1984/562685/daihatsu_rocky_2_0_wagon.html
EU-DAIHATSU-RUGGER-I-F73-SUV-SWB-01	3840	1690	1850	Automobile-Catalog – 1993 Daihatsu Rocky 2.8 Turbo Diesel Hard-top	https://www.automobile-catalog.com/car/1993/570230/daihatsu_rocky_2_8_turbo_diesel_hard-top.html
EU-DAIHATSU-RUGGER-I-F78-SUV-LWB-01	4165	1780	1925	Automobile-Catalog – 1993 Daihatsu Rocky 2.8 Turbo Diesel Wagon	https://www.automobile-catalog.com/car/1993/570245/daihatsu_rocky_2_8_turbo_diesel_wagon.html
```

下一步优先处理

1. 核清 `26479` 的 2.8 D 自然吸气版本是否在 1990 年后的输入覆盖期继续对应改款车身，避免错误套用涡轮版本外廓。
2. 拆分 `25563` Nissan Urvan E24 的短轴、长轴及车顶高度分支。
3. 拆分 `26018` Mercedes-Benz Sprinter W906 313 CDI 底盘驾驶室的轴距与驾驶室外廓；闭合后立即执行最终机械检查并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000619/index.html?utm_source=chatgpt.com "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://www.carsguide.com.au/toyota/sprinter/car-dimensions/1984?utm_source=chatgpt.com "Toyota Sprinter Dimensions 1984 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[3]: https://www.automobile-catalog.com/car/1984/562805/daihatsu_rocky_2_0_hard-top.html?utm_source=chatgpt.com "1984 Daihatsu Rocky (Fourtrak) 2.0 Hard-top (man. 5)"
[4]: https://u-catch.daihatsu.co.jp/catalog/RUGGER/MODEL__198904/?utm_source=chatgpt.com "ラガー 1989年~1995年モデルのWEBカタログ〖ダイハツ公式〗U-CATCH"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
更新点

* 完成 `25563` Nissan Urvan E24 2.0 厢式车。精确 Ktype 对应 Z20S、65 kW、1986-06 至 1994-09；闭合为四门标准厢式车 `4690 × 1690 × 1965 mm`。([AutoDoc][1])
* 完成 `26479` Daihatsu Rugger 2.8 D，自然吸气柴油版本拆分为 F70 短轴硬顶和 F75 长轴 Wagon；三维与已缓存的对应 Rugger 组完全一致，直接复用，不重复建组。([汽车目录][2])
* `26018` Sprinter W906 仍未闭合：该 Ktype 同时覆盖多个单排、双排和轴距代码，且生产期跨越改款，现有改款前后资料的长度、宽度和高度存在实质差异，不能用一套旧三维覆盖全部分支。([Autodzeusas][3])

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：99
* READY 映射行：147
* PENDING Ktype：1
* 当前引用尺寸组：73
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25563	25563	Van	Urvan III (E24)	E24	4	EU-NISSAN-URVAN-III-E24-VAN-01	HIGH		READY
26018	26018	Pickup	Sprinter W906			LOW	候选包含906.131/133/135单排及906.231/233/235双排，且生产期跨越改款。	PENDING: 多驾驶室、轴距及改款前后外廓边界尚未闭合
26479_swb	26479	SUV	Rugger I	F70	3	EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	HIGH	F70短轴硬顶外廓。	READY
26479_lwb	26479	SUV	Rugger I	F75	3	EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	HIGH	F75长轴Wagon外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-URVAN-III-E24-VAN-01	4690	1690	1965	CarSpecsGuru – Nissan Urvan III E24 2.0 MT 88 HP;Auto.ru – Nissan Urvan III E24 Van specifications	https://www.carspecsguru.com/nissan/urvan/4601/9000/modification-60265;https://auto.ru/catalog/cars/nissan/urvan/20334821/21757034/specifications/21757034__22762593/
```

下一步优先处理

1. 只处理 `26018`：按单排/双排、3250/3665/4325 mm 轴距及改款前后外廓建立最终物理分支。
2. 优先取得能够同时明确长度、不含后视镜宽度和高度的 Mercedes-Benz W906 官方车身制造资料；不再复查其他 99 个 Ktype。
3. 该 Ktype 闭合后立即执行一次机械检查，并在下一轮输出两张完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/spares/nissan/urvan/urvan-box-e24/25563-2-0?utm_source=chatgpt.com "Parts Urvan Van (E24) 2.0 88 hp Petrol 1986 - 1994 Z20S"
[2]: https://www.automobile-catalog.com/car/1990/562835/daihatsu_rocky_2_8_diesel_hard-top.html?utm_source=chatgpt.com "1990 Daihatsu Rocky (Fourtrak) 2.8 Diesel Hard-top (man. 5)"
[3]: https://www.zeusauto.lt/en/catalog/tecdoc/personal/ds/sprinter-3-5-t-platform-chassis-b906/313-cdi-906-131-906-133-906-135-906-231-906-233/bellow/74/5591/26018/100074/?path=100074 "SPRINTER 3,5-t Platform/Chassis (B906) 313 CDI (906.131, 906.133, 906.135, 906.231, 906.233,..."


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
更新点

* 已确认 `26018` 覆盖六个 W906 底盘分支：`906.131/133/135` 为单排驾驶室的 3250/3665/4325 mm 三种轴距，`906.231/233/235` 为对应的双排驾驶室。2006 年车身制造资料与后期 3.55 t Cab Chassis 资料在车长及高度上存在配置差异，例如中轴单排分别出现 `5870 mm` 与 `5886 mm`，中轴双排出现 `5870 mm` 与 `6103 mm`，不能静默合并为同一尺寸组。([DIY Sprinter][1])
* 现有资料尚未同时闭合六个分支在 2006–2016 全生产期内的同市场、同驾驶室、同轴距三维，因此本轮不创建猜测性尺寸组。

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：99
* READY 映射行：147
* PENDING Ktype：1
* 已确认尺寸组：73
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26018	26018	Pickup	Sprinter W906			LOW	已确认906.131/133/135为单排三轴距，906.231/233/235为双排三轴距；不同年份资料的车长及高度存在配置差异。	PENDING: 2006-2016单排/双排三轴距的同市场同口径三维尚未全部闭合
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 仅补齐 `26018` 六个车身代码在改款前后对应的欧洲 3.5 t 底盘驾驶室图纸，锁定每个分支的不含后视镜宽度、车长和高度。
2. 若资料证明改款前后三维相同，则按六个驾驶室/轴距分支建组；若不同，则分别创建稳定的 `prefl` 与 `facelift` 尺寸组。
3. 闭合后立即执行最终机械检查并输出两张完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "Body/Equipment Mounting Directives for Sprinter Model ..."


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2201-2300_ktype_dimension_mapping_final.tsv
- all_2201-2300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* `26018` 已按 W906 单排驾驶室 `906.131/133/135` 和双排驾驶室 `906.231/233/235` 拆成六个物理分支，对应 3250、3665、4325 mm 三种轴距。Mercedes-Benz 车身制造指引确认了车身代码与轴距边界，规格页进一步区分了 1990 mm 不含后视镜车宽与 2426 mm 最大含镜宽度。([DIY Sprinter][1])
* 当前批次已达到 `PENDING=0`。
* 已完成固定表头、`id` 唯一、尺寸组唯一、映射引用闭合、尺寸及来源非空检查。
* 两个指定 TSV 文件均已生成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：153
* PENDING Ktype：0
* DIMENSION_GROUP：79
* 孤立尺寸组：0
* 未闭合映射引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25463	25463	Hatchback	Mazda6 II (GH)	GH5FS	5	EU-MAZDA-6-II-GH-HATCHBACK-01	HIGH		READY
25464	25464	Hatchback	Mazda6 II (GH)	GH14	5	EU-MAZDA-6-II-GH-HATCHBACK-01	HIGH		READY
25465_prefl	25465	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25465_facelift	25465	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25466_prefl	25466	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25466_facelift	25466	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25467	25467	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25468_prefl	25468	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25468_facelift	25468	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25469	25469	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25470_prefl	25470	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25470_facelift	25470	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25471_prefl	25471	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25471_facelift	25471	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25472_prefl	25472	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
25472_facelift	25472	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
25473	25473	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH		READY
25474_prefl	25474	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25474_facelift	25474	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25475_prefl	25475	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25475_facelift	25475	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25476_prefl	25476	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25476_facelift	25476	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25477	25477	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH		READY
25478_prefl	25478	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25478_facelift	25478	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25479_prefl	25479	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25479_facelift	25479	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25480_prefl	25480	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25480_facelift	25480	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25481	25481	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH		READY
25482_prefl	25482	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
25482_facelift	25482	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
25483_prefl	25483	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH	改款前外廓。	READY
25483_facelift	25483	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	改款后外廓。	READY
25484	25484	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH		READY
25485	25485	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH		READY
25486	25486	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
25487	25487	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
25488	25488	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
25489	25489	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
25490	25490	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH		READY
25491	25491	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
25492	25492	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH		READY
25493	25493	Coupe	6 Series E63 LCI	E63	2	EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	HIGH		READY
25494	25494	Coupe	6 Series E63 LCI	E63	2	EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	HIGH		READY
25495	25495	Convertible	6 Series E64 LCI	E64	2	EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	HIGH		READY
25496	25496	Convertible	6 Series E64 LCI	E64	2	EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	HIGH		READY
25497	25497	SUV	X3 E83 facelift	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
25498	25498	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH		READY
25499	25499	Wagon	Vectra C facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
25500	25500	Wagon	Vectra C facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
25501	25501	MPV	Zafira B facelift		5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25502	25502	MPV	Zafira B facelift		5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25503	25503	MPV	Zafira B facelift	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH		READY
25504	25504	SUV	Antara A		5	EU-OPEL-ANTARA-A-SUV-02	HIGH		READY
25505	25505	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	HIGH		READY
25506	25506	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25507	25507	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25508_prefl	25508	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
25508_facelift	25508	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
25509	25509	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25510	25510	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
25511	25511	SUV	Samurai SJ413	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	HIGH		READY
25512	25512	MPV	Zeta	220	5	EU-LANCIA-ZETA-220-MPV-5D-01	HIGH		READY
25519	25519	Coupe	Celica V (T18)	ST184	2	EU-TOYOTA-CELICA-V-T18-COUPE-2D-01	HIGH		READY
25536	25536	Coupe	Mustang IV facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH		READY
25537	25537	Convertible	Mustang IV facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH		READY
25563	25563	Van	Urvan III (E24)	E24	4	EU-NISSAN-URVAN-III-E24-VAN-01	HIGH		READY
25583	25583	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH		READY
25648_prefl	25648	SUV	X-Trail II T31	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	HIGH	改款前外廓。	READY
25648_facelift	25648	SUV	X-Trail II T31	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
25658	25658	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-SEDAN-01	HIGH		READY
25659_prefl	25659	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
25659_facelift	25659	Sedan	Logan I facelift	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	HIGH	2008年改款后外廓。	READY
25660_prefl	25660	Sedan	Logan I	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
25660_facelift	25660	Sedan	Logan I facelift	L90	4	EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	HIGH	2008年改款后外廓。	READY
25661	25661	Pickup	Avalanche I	GMT800	4	EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	HIGH	1500车身外廓。	READY
25663	25663	Pickup	Avalanche I	GMT800	4	EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	HIGH	2500车身外廓与1500三维相同。	READY
25665_regcab_z85	25665	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab Z85外廓。	READY
25665_regcab_zq8	25665	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	HIGH	Regular Cab ZQ8外廓。	READY
25665_extcab_z85	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab Z85外廓。	READY
25665_extcab_zq8	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	HIGH	Extended Cab ZQ8外廓。	READY
25665_crewcab_z85	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab Z85外廓。	READY
25665_crewcab_zq8	25665	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	HIGH	Crew Cab ZQ8外廓。	READY
25667_regcab_z85	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab Z85外廓。	READY
25667_regcab_z71	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	HIGH	Regular Cab Z71外廓。	READY
25667_regcab_zq8	25667	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	HIGH	Regular Cab ZQ8外廓。	READY
25667_extcab_z85	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab Z85外廓。	READY
25667_extcab_z71	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	HIGH	Extended Cab Z71外廓。	READY
25667_extcab_zq8	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	HIGH	Extended Cab ZQ8外廓。	READY
25667_crewcab_z85	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab Z85外廓。	READY
25667_crewcab_z71	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	HIGH	Crew Cab Z71外廓。	READY
25667_crewcab_zq8	25667	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	HIGH	Crew Cab ZQ8外廓。	READY
25668_regcab_z85	25668	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	HIGH	Regular Cab 4WD Z85外廓。	READY
25668_regcab_z71	25668	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	HIGH	Regular Cab 4WD Z71外廓。	READY
25668_extcab_z85	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	HIGH	Extended Cab 4WD Z85外廓。	READY
25668_extcab_z71	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	HIGH	Extended Cab 4WD Z71外廓。	READY
25668_crewcab_z85	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	HIGH	Crew Cab 4WD Z85外廓。	READY
25668_crewcab_z71	25668	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	HIGH	Crew Cab 4WD Z71外廓。	READY
25673	25673	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH		READY
25690	25690	Sedan	A6 C7	4G2	4	EU-AUDI-A6-C7-SEDAN-01	HIGH		READY
25743	25743	Coupe	Thunderbird X	MN12	2	EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	HIGH		READY
25762	25762	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
25886	25886	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	HIGH		READY
25887	25887	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
25909	25909	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
25918	25918	Sedan	Elantra V	MD	4	EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-01	MEDIUM	第五代MD四门车身。	READY
25931	25931	Coupe	Wraith		2	EU-ROLLS-ROYCE-WRAITH-COUPE-2D-01	HIGH		READY
25973	25973	MPV	Previa III (XR50)	ACR50	5	EU-TOYOTA-PREVIA-III-XR50-MPV-FWD-01	HIGH		READY
26003	26003	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26004	26004	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26018_single_swb	26018	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-SWB-01	HIGH	单排驾驶室，3250 mm轴距。	READY
26018_single_mwb	26018	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	HIGH	单排驾驶室，3665 mm轴距。	READY
26018_single_lwb	26018	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	HIGH	单排驾驶室，4325 mm轴距。	READY
26018_crew_swb	26018	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-SWB-01	HIGH	双排驾驶室，3250 mm轴距。	READY
26018_crew_mwb	26018	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-MWB-01	HIGH	双排驾驶室，3665 mm轴距。	READY
26018_crew_lwb	26018	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-LWB-01	HIGH	双排驾驶室，4325 mm轴距。	READY
26082_prefl	26082	Sedan	Scepter XV10	SXV10	4	EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
26082_facelift	26082	Sedan	Scepter XV10	SXV10	4	EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-FACELIFT-01	HIGH	1994年改款后外廓。	READY
26145_standard_prefl	26145	MPV	Isis I	ZNM10G	5	EU-TOYOTA-ISIS-I-MPV-STANDARD-PREFL-01	HIGH	标准车身改款前外廓。	READY
26145_standard_facelift	26145	MPV	Isis I	ZGM10G	5	EU-TOYOTA-ISIS-I-MPV-STANDARD-FACELIFT-01	HIGH	标准车身改款后外廓。	READY
26145_platana	26145	MPV	Isis I	ZGM10W	5	EU-TOYOTA-ISIS-I-MPV-PLATANA-01	HIGH	Platana外部套件外廓。	READY
26163_norack	26163	SUV	Highlander I (XU20) facelift		5	EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-NORACK-01	HIGH	无原厂车顶架外廓。	READY
26163_roofrack	26163	SUV	Highlander I (XU20) facelift		5	EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-ROOFRACK-01	HIGH	原厂车顶架高度分支。	READY
26235	26235	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
26308	26308	Sedan	Cima III	FGY33	4	EU-NISSAN-CIMA-III-FY33-SEDAN-4D-01	HIGH		READY
26324	26324	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26357	26357	Coupe	Sprinter V (E80)		2	EU-TOYOTA-SPRINTER-V-E80-COUPE-2D-01	MEDIUM	上游驱动字段与AE86标识冲突；保留已确认的E80双门轿跑边界，BodyCode留空。	READY
26400	26400	Sedan	Cima II	FGY32	4	EU-NISSAN-CIMA-II-FY32-SEDAN-4D-01	HIGH		READY
26427_prefl	26427	MPV	Sienna I	XL10	5	EU-TOYOTA-SIENNA-I-XL10-MPV-PREFL-01	HIGH	2001年改款前外廓。	READY
26427_facelift	26427	MPV	Sienna I	XL10	5	EU-TOYOTA-SIENNA-I-XL10-MPV-FACELIFT-01	HIGH	2001年改款后外廓。	READY
26478_swb	26478	SUV	Rugger I	F80	3	EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	HIGH	短轴硬顶外廓。	READY
26478_lwb	26478	SUV	Rugger I	F85	3	EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	HIGH	长轴Wagon外廓。	READY
26479_swb	26479	SUV	Rugger I	F70	3	EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	HIGH	F70短轴硬顶外廓。	READY
26479_lwb	26479	SUV	Rugger I	F75	3	EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	HIGH	F75长轴Wagon外廓。	READY
26485_swb	26485	SUV	Rugger I facelift	F73	3	EU-DAIHATSU-RUGGER-I-F73-SUV-SWB-01	HIGH	F73短轴硬顶外廓。	READY
26485_lwb	26485	SUV	Rugger I facelift	F78	3	EU-DAIHATSU-RUGGER-I-F78-SUV-LWB-01	HIGH	F78长轴Wagon外廓。	READY
26491	26491	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26492	26492	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26495	26495	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26496	26496	Hatchback	Punto 2012			EU-FIAT-PUNTO-2012-HATCHBACK-01	HIGH	3门及5门外廓三维相同，不拆分尺寸组。	READY
26543_prefl	26543	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26543_facelift	26543	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26544_prefl	26544	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26544_facelift	26544	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26545_prefl	26545	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26545_facelift	26545	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26546_prefl	26546	Wagon	Logan I MCV	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	HIGH	改款前外廓。	READY
26546_facelift	26546	Wagon	Logan I MCV facelift	K90	5	EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	HIGH	2008年改款后外廓。	READY
26547	26547	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
26548	26548	Wagon	A4 B7	8ED	5	EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	HIGH		READY
26549	26549	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2201-2300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440	Auto-Data – Mazda 6 II Hatchback (GH) 2.5	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-2.5-170hp-16783
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421	BMW AG TIS – E90 complete vehicle	https://workshop-manuals.com/bmw/3_series_e90/335i_n54_sal/6_si_techniques/0__maintenance_and_general_data/6_sbt__complete_vehicle_e90/page_3861/
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	BMW Group PressClub – Specifications BMW 3 Series Sedan	https://www.press.bmwgroup.com/global/article/detail/T0039673EN/specifications-bmw-3-series-sedan
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	BMW Group – BMW 3 Series Touring technical data	https://www.press.bmwgroup.com/global/article/detail/T0048254EN/the-new-bmw-3-series
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	BMW Group PressClub – 3 Series Touring technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0125277ES/185336
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395	BMW Group – BMW 3 Series Coupé technical data	https://f30.bimmerpost.com/forums/attachment.php?attachmentid=53127&d=1167364329
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375	BMW Group PressClub – BMW 3 Series Coupé technical data	https://www.press.bmwgroup.com/austria/article/attachment/T0036895DE/193404
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384	BMW Group PressClub – 2009 BMW 3 Series Convertible technical data	https://www.press.bmwgroup.com/usa/article/attachment/T0018124EN_US/42510
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	ADAC – BMW 120i 3-door E81 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/1er-reihe/e81-e87-e82-e88-facelift/209126/
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468	Auto-Data – BMW 5 Series E60 LCI technical data	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-525i-218hp-28136
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491	Auto-Data – BMW 5 Series Touring E61 LCI 520d	https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-520d-177hp-28230
EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	4820	1855	1374	BMW Group – The new BMW 6 Series Coupé and Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0037654EN/76891
EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	4820	1855	1374	BMW Group – The new BMW 6 Series Coupé and Convertible technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0037654EN/76891
EU-BMW-X3-E83-SUV-5D-FACELIFT-01	4569	1853	1674	Auto-Data – BMW X3 E83 facelift	https://www.auto-data.net/en/bmw-x3-e83-facelift-2006-generation-6389
EU-BMW-X5-E70-SUV-01	4854	1933	1766	BMW Technical Training – E70 Complete Vehicle	https://bmwtechinfo.bmwgroup.com/tech_training_manual/ST605%20E70%20Complete%20Vehicle.pdf
EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	4839	1798	1500	Automobile-Catalog – Opel Vectra Caravan 1.9 CDTI	https://www.automobile-catalog.com/car/2007/2523860/opel_vectra_caravan_1_9_cdti_150.html
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635	Opel Media Information – Zafira B press kit	https://dixi-car.pl/doc/zafira-b-presskit-en.pdf
EU-OPEL-ANTARA-A-SUV-02	4575	1850	1704	Automobile-Catalog – Opel Antara 2.0 CDTI 127 4x4	https://www.automobile-catalog.com/car/2007/2541050/opel_antara_2_0_cdti_127_4x4.html
EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	4856	1822	1483	Mercedes-Benz Classic Archive – E 230 W 211 E 25	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/E-230.xhtml?oid=2461836
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto Motor und Sport – Audi A4 Avant 1.8 TFSI technical data	https://www.auto-motor-und-sport.de/test/audi-a4-avant-1-8-tfsi-kombi/technische-daten/
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Automobile-Catalog – 2012 Audi A4 Avant 1.8 TFSI	https://www.automobile-catalog.com/car/2012/1586870/audi_a4_avant_1_8_tfsi_170_multitronic.html
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680	Auto-Data – Suzuki Samurai SJ413	https://www.auto-data.net/en/suzuki-samurai-sj-1.3-sj-413-64hp-16424
EU-LANCIA-ZETA-220-MPV-5D-01	4470	1834	1714	Automobile-Catalog – 1999 Lancia Zeta 2.0 JTD LX	https://www.automobile-catalog.com/car/1999/1383935/lancia_zeta_2_0_jtd_lx.html
EU-TOYOTA-CELICA-V-T18-COUPE-2D-01	4470	1704	1285	Edmunds – 1990 Toyota Celica Coupe GT specifications	https://www.edmunds.com/toyota/celica/1990/coupe/st-11821/features-specs/
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359	Ford – 1999 Mustang Owner’s Manual	https://www.mustangspecs.com/wp-content/uploads/2020/05/1999-Mustang-Owners-Manual.pdf
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350	Automobile-Catalog – 1999 Ford Mustang Convertible 3.8L V6	https://www.automobile-catalog.com/car/1999/885815/ford_mustang_convertible_3_8l_v-6.html
EU-NISSAN-URVAN-III-E24-VAN-01	4690	1690	1965	CarSpecsGuru – Nissan Urvan III E24 2.0 MT 88 HP;Auto.ru – Nissan Urvan III E24 Van specifications	https://www.carspecsguru.com/nissan/urvan/4601/9000/modification-60265;https://auto.ru/catalog/cars/nissan/urvan/20334821/21757034/specifications/21757034__22762593/
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	BMW Group PressClub – BMW 3 Series Convertible technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0084820ES/132013
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685	Automobile-Catalog – 2007 Nissan X-Trail T31	https://www.automobile-catalog.com/car/2007/2316080/nissan_x-trail_2_0_dci_150_se_automatic.html
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700	Automobile-Catalog – 2011 Nissan X-Trail T31 facelift	https://www.automobile-catalog.com/car/2011/2316620/nissan_x-trail_2_0_dci_173_tekna.html
EU-AUDI-A6-C7-SEDAN-01	4915	1874	1468	Audi – A6 Sedan dimensions	https://www.audi.com.tw/dam/nemo/tw/Model/A6/A6_Sedan/dimensions/0105-AudiA6.pdf
EU-RENAULT-LOGAN-I-L90-SEDAN-PREFL-01	4250	1742	1534	Automobile-Catalog – 2008 Dacia Logan pre-facelift	https://www.automobile-catalog.com/car/2008/554630/dacia_logan_1_5_dci_68_laureate.html
EU-RENAULT-LOGAN-I-L90-SEDAN-FACELIFT-01	4288	1740	1534	Automobile-Catalog – 2008 Dacia Logan facelift	https://www.automobile-catalog.com/car/2008/1221920/dacia_logan_1_5_dci_68_ambiance.html
EU-CHEVROLET-AVALANCHE-I-GMT800-PICKUP-4D-01	5629	2027	1869	Edmunds – 2006 Chevrolet Avalanche 1500 LS specifications;Edmunds – 2006 Chevrolet Avalanche 2500 LS specifications	https://www.edmunds.com/chevrolet/avalanche/2006/st-100580431/features-specs/;https://www.edmunds.com/chevrolet/avalanche/2006/st-100580433/features-specs/
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	4887	1717	1648	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	4887	1717	1613	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	5258	1717	1648	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	5258	1717	1613	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	5258	1717	1656	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	5258	1717	1618	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	4887	1717	1694	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	5258	1717	1694	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	5258	1717	1702	Chevrolet – 2008 Colorado official brochure	https://xr793.com/wp-content/uploads/2024/01/2008-Chevrolet-Colorado.pdf
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826	Edmunds – 2006 Ford Explorer specifications	https://www.edmunds.com/ford/explorer/2006/features-specs/
EU-FORD-USA-THUNDERBIRD-X-MN12-COUPE-2D-01	5088	1847	1334	Automobile-Catalog – 1994 Ford Thunderbird LX 3.8L	https://www.automobile-catalog.com/car/1994/879350/ford_thunderbird_lx_3_8l_v-6_automatic.html
EU-FIAT-PUNTO-2012-HATCHBACK-01	4065	1687	1490	Fiat Punto 2012 official press kit	https://www.media.stellantis.com/be-fr/fiat/press/fiat-punto-2012-l-evolution-d-un-best-seller
EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	4922	1816	1485	Chrysler Media – 2009 Chrysler Sebring Convertible Specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2009_ChryslerSebringConvertibleSpecifications.pdf
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4842	1808	1498	Chrysler Media – 2007 Chrysler Sebring Specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2007ChryslerSebringFASpecifications.pdf
EU-HYUNDAI-ELANTRA-V-MD-SEDAN-4D-01	4530	1775	1435	Hyundai Motor America – 2011 Hyundai Elantra official specifications	https://www.hyundainews.com/releases/1597
EU-ROLLS-ROYCE-WRAITH-COUPE-2D-01	5269	1947	1507	Rolls-Royce Motor Cars – Wraith press kit	https://www.press.rolls-roycemotorcars.com/rolls-royce-motor-cars-pressclub/article/attachment/T0137422EN/283872
EU-TOYOTA-PREVIA-III-XR50-MPV-FWD-01	4795	1800	1730	Toyota 75 Years – Third-generation Estima vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000619/index.html
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-SWB-01	5305	1990	2355	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 313 CDI 906.131	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/313-cdi-906.131-2006-2009-k62613
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	5870	1990	2350	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 316 CDI 906.133	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/316-cdi-906.133-2009-k79565
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	6680	1990	2345	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 313 CDI 906.135	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/313-cdi-906.135-2009-2013-k79551
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-SWB-01	5305	1990	2385	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 318 CDI 906.231	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/318-cdi-906.231-2006-2009-k62651
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-MWB-01	5870	1990	2385	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 319 CDI 906.233	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/319-cdi-906.233-2009-2013-k79583
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-LWB-01	6680	1990	2385	Mercedes-Benz Sprinter W906 Body/Equipment Mounting Directives;Autogidas – Mercedes-Benz Sprinter 313 CDI 906.235	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/313-cdi-906.235-2009-2013-k79554
EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-PREFL-01	4780	1770	1410	Toyota GAZOO – Scepter Sedan 2.2G	https://gazoo.com/catalog/maker/TOYOTA/SCEPTER_SEDAN/199211/1006944/
EU-TOYOTA-SCEPTER-XV10-SEDAN-4D-FACELIFT-01	4790	1770	1410	Toyota GAZOO – Scepter Sedan 2.2	https://gazoo.com/catalog/maker/TOYOTA/SCEPTER_SEDAN/199211/1001046/
EU-TOYOTA-ISIS-I-MPV-STANDARD-PREFL-01	4610	1695	1640	Toyota GAZOO – Isis L 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10030858/
EU-TOYOTA-ISIS-I-MPV-STANDARD-FACELIFT-01	4635	1695	1640	Toyota GAZOO – Isis L G Edition 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10057945/
EU-TOYOTA-ISIS-I-MPV-PLATANA-01	4640	1710	1640	Toyota GAZOO – Isis Platana Black Limited 1.8	https://gazoo.com/catalog/maker/TOYOTA/ISIS/200409/10065264/
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-NORACK-01	4689	1826	1679	Toyota – 2004 Highlander specifications brochure	https://xr793.com/wp-content/uploads/2022/01/2004-Toyota-Highlander-Specs.pdf
EU-TOYOTA-HIGHLANDER-I-XU20-FACELIFT-SUV-FWD-ROOFRACK-01	4689	1826	1735	Toyota – 2004 Highlander specifications brochure	https://xr793.com/wp-content/uploads/2022/01/2004-Toyota-Highlander-Specs.pdf
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Alfa Romeo – Giulietta S2 buyer’s guide	https://tools.alfaromeo.com.au/vehicles/Giulietta-Buyers-Guide_v7-NO-PRICE.pdf
EU-NISSAN-CIMA-III-FY33-SEDAN-4D-01	4970	1820	1445	GAZOO Car Catalog – Nissan Cima 41L (E-FGY33)	https://gazoo.com/catalog/maker/NISSAN/CIMA/199606/1500485/
EU-TOYOTA-SPRINTER-V-E80-COUPE-2D-01	4180	1625	1335	Auto-Data – Toyota Corolla Coupe V E80 1.6 GT 16V	https://www.auto-data.net/en/toyota-corolla-coupe-v-e80-1.6-gt-16v-124hp-automatic-28600
EU-NISSAN-CIMA-II-FY32-SEDAN-4D-01	4930	1780	1420	Nissan Heritage Collection – Cima Type III Limited L	https://www2.nissan.co.jp/HERITAGE/DETAIL/431.html
EU-TOYOTA-SIENNA-I-XL10-MPV-PREFL-01	4915	1864	1709	Edmunds – 1998 Toyota Sienna 3.0 specifications	https://www.edmunds.com/toyota/sienna/1998/features-specs/
EU-TOYOTA-SIENNA-I-XL10-MPV-FACELIFT-01	4933	1864	1709	Edmunds – 2001 Toyota Sienna 3.0 specifications	https://www.edmunds.com/toyota/sienna/2001/features-specs/
EU-DAIHATSU-RUGGER-I-SUV-SWB-PREFL-01	3775	1580	1840	Automobile-Catalog – 1984 Daihatsu Rocky 2.0 Hard-top	https://www.automobile-catalog.com/car/1984/562805/daihatsu_rocky_2_0_hard-top.html
EU-DAIHATSU-RUGGER-I-SUV-LWB-PREFL-01	4100	1580	1915	Automobile-Catalog – 1984 Daihatsu Rocky 2.0 Wagon	https://www.automobile-catalog.com/car/1984/562685/daihatsu_rocky_2_0_wagon.html
EU-DAIHATSU-RUGGER-I-F73-SUV-SWB-01	3840	1690	1850	Automobile-Catalog – 1993 Daihatsu Rocky 2.8 Turbo Diesel Hard-top	https://www.automobile-catalog.com/car/1993/570230/daihatsu_rocky_2_8_turbo_diesel_hard-top.html
EU-DAIHATSU-RUGGER-I-F78-SUV-LWB-01	4165	1780	1925	Automobile-Catalog – 1993 Daihatsu Rocky 2.8 Turbo Diesel Wagon	https://www.automobile-catalog.com/car/1993/570245/daihatsu_rocky_2_8_turbo_diesel_wagon.html
EU-RENAULT-LOGAN-I-K90-MCV-WAGON-PREFL-01	4450	1740	1674	Auto-Data – Dacia Logan I MCV 1.5 dCi 68 7 Seats	https://www.auto-data.net/en/dacia-logan-i-mcv-1.5-dci-68hp-7-seats-15884
EU-RENAULT-LOGAN-I-K90-MCV-WAGON-FACELIFT-01	4473	1740	1640	Auto-Data – Dacia Logan I MCV facelift 1.6 16V	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-16v-105hp-46170
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Audi – 2007 A4 technical specifications	https://www.audiworld.com/model/a4/07/A4_tech.pdf
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427	Auto-Data – Audi A4 Avant B7 2.0 TDI	https://www.auto-data.net/en/audi-a4-avant-b7-8e-2.0-tdi-140hp-4392
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459	ADAC – Audi A6 C6 2.0 TDI DPF technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a6/c6/205684/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2201-2300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "ABR.boo"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2201-2300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2201-2300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3237 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1626 行）

- 尺寸冲突协调：
  - EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01 -> EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-02：4856x1822x1484 与 4856x1822x1483，创建新尺寸组
