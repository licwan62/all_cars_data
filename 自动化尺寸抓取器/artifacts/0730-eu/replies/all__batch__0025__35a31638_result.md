# 任务：all 第 2401-2500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0025__35a31638


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2401-2500 行

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
all 第 2401-2500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538
EU-BMW-X2-F39-SUV-01	4360	1824	1526
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480
EU-FORD-TRANSIT-TOURNEO-MK6-BUS-SWB-LOWROOF-01	4863	1974	1989
EU-FORD-TRANSIT-TOURNEO-MK7-BUS-SWB-LOWROOF-01	4863	1974	2089
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	4410	1820	1655
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-LANCIA-BETA-BC-COUPE-01	3995	1650	1285
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1350
EU-MAZDA-626-III-GD-SEDAN-FACELIFT-01	4535	1690	1410
EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	4275	1765	1535
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-SL-R107-FACELIFT-CONVERTIBLE-01	4580	1790	1300
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	4655	1695	1855
EU-OPEL-ASTRA-G-CLASSIC-II-HATCHBACK-5D-01	4110	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-SEDAN-01	4252	1709	1425
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457
EU-PEUGEOT-308-II-T9-WAGON-FACELIFT-01	4585	1804	1457
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-SSANGYONG-REXTON-II-SUV-01	4850	1960	1825
EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	4970	1964	1445
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	407	2.0 HDI	Stufenheck	Frontantrieb	Diesel	93	126	Nov 2004	Oct 2007	2024-03-01	131790
Mercedes-benz	B-Klasse sports tourer	B 220 D 4-matic	Schrägheck	Allrad	Diesel	125	170	Jun 2018	Dec 2018	2024-03-01	131792
Rolls-royce	Camargue	6.7	Coupe	Heckantrieb	Benzin	156	212	Jun 1974	Dec 1987	2024-03-01	131801
Rolls-royce	Corniche ii	6.75	Cabriolet	Heckantrieb	Benzin	158	215	Oct 1986	Sep 1989	2024-03-01	131802
Rolls-royce	Corniche	6.75	Cabriolet	Heckantrieb	Benzin	158	215	Jul 1984	Sep 1986	2024-03-01	131803
Rolls-royce	Corniche	6.75	Stufenheck	Heckantrieb	Benzin	191	260	Oct 1977	Jun 1984	2024-03-01	131804
Rolls-royce	Corniche	6.75	Cabriolet	Heckantrieb	Benzin	191	260	Mar 1971	Jun 1984	2024-03-01	131805
Rolls-royce	Silver shadow	6.7	Stufenheck	Heckantrieb	Benzin	144	196	Oct 1977	Dec 1980	2024-03-01	131808
Peugeot	308 ii	1.6 GTI Puretech 263	Schrägheck	Frontantrieb	Benzin	193	263	Jul 2018	Jun 2021	2024-03-01	131809
Mercedes-benz	G-Klasse	200 GE	Geländewagen offen	Allrad	Benzin	80	109	Jul 1982	Aug 1989	2024-03-01	131812
Mercedes-benz	G-Klasse	280 GE	Geländewagen offen	Allrad	Benzin	110	150	Jul 1982	May 1993	2024-03-01	131814
Mercedes-benz	G-Klasse	230 GE	Geländewagen offen	Allrad	Benzin	92	125	Jul 1982	May 1993	2024-03-01	131815
Mazda	6	2.5	Stufenheck	Frontantrieb	Benzin	143	194	Mar 2018	-	2024-03-01	131816
Mercedes-benz	G-Klasse	230 GE	Geländewagen offen	Allrad	Benzin	90	122	Aug 1986	May 1993	2024-03-01	131817
Mercedes-benz	G-Klasse	250 GD	Geländewagen offen	Allrad	Diesel	62	84	Oct 1987	Oct 1991	2024-03-01	131820
Mercedes-benz	G-Klasse	300 GD	Geländewagen offen	Allrad	Diesel	65	88	Nov 1979	Aug 1989	2024-03-01	131821
Mazda	6	2.5	Kombi	Frontantrieb	Benzin	143	194	Mar 2018	-	2024-03-01	131822
Citroën	C4 cactus	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	75	102	Jun 2018	-	2024-03-01	131826
Citroën	C-Elysee	1.5 Bluehdi 100	Stufenheck	Frontantrieb	Diesel	75	102	May 2018	-	2024-03-01	131827
BMW	X2	Sdrive 18 D	SUV	Frontantrieb	Diesel	100	136	Mar 2018	Oct 2023	2024-03-01	131828
Peugeot	301	1.5 Bluehdi 100	Stufenheck	Frontantrieb	Diesel	75	102	May 2018	-	2024-03-01	131829
BMW	X2	Xdrive 18 D	SUV	Allrad	Diesel	100	136	Mar 2018	Oct 2023	2024-03-01	131830
Hyundai	Accent v	1.4	Stufenheck	Frontantrieb	Benzin	73	99	Jul 2018	-	2024-03-01	131831
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	100	136	Jul 2018	Jun 2020	2024-03-01	131832
BMW	5	518 D	Stufenheck	Heckantrieb	Diesel	110	150	Jul 2018	Jun 2020	2024-03-01	131833
BMW	5	518 D	Kombi	Heckantrieb	Diesel	110	150	Jul 2018	Jun 2020	2024-03-01	131834
BMW	5	518 D	Kombi	Heckantrieb	Diesel	100	136	Jul 2018	Jun 2020	2024-03-01	131835
BMW	6	620 D	Schrägheck	Heckantrieb	Diesel	120	163	Jul 2018	Jun 2020	2024-03-01	131836
BMW	6	620 D Xdrive	Schrägheck	Allrad	Diesel	120	163	Jul 2018	Jun 2020	2024-03-01	131837
Ferrari	488 gtb	Pista 3.9	Coupe	Heckantrieb	Benzin	530	720	Mar 2018	-	2024-03-01	131838
Subaru	Forester	2.0 E-boxer Hybrid AWD	SUV	Allrad	Benzin/Elektro	107	145	Apr 2018	-	2024-03-01	131840
Subaru	Forester	2.5 AWD	SUV	Allrad	Benzin	136	185	Apr 2018	-	2024-03-01	131841
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	118	160	Aug 2018	-	2024-03-01	131842
Mercedes-benz	C-Klasse	C 300 D	Stufenheck	Heckantrieb	Diesel	180	245	Jun 2018	May 2021	2024-03-01	131843
Mercedes-benz	C-Klasse	C 300 D 4-matic	Stufenheck	Allrad	Diesel	180	245	Jun 2018	May 2021	2024-03-01	131844
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	140	190	Aug 2018	Oct 2022	2024-03-01	131845
Ford	Ka+ iii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	70	95	Feb 2018	Dec 2020	2026-04-01	131847
Ford	Ka+ iii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2018	Dec 2020	2026-04-01	131848
Alfa Romeo	Giulia	2.2 D Q4	Stufenheck	Allrad	Diesel	140	190	Aug 2018	Oct 2022	2024-03-01	131849
Volvo	Xc40	D3	SUV	Frontantrieb	Diesel	110	150	Sep 2018	Sep 2021	2024-03-01	131853
Mercedes-benz	C-Klasse	C 300 D	Kombi	Heckantrieb	Diesel	180	245	Jun 2018	Feb 2021	2024-03-01	131857
Mercedes-benz	C-Klasse	C 300 D 4-matic	Kombi	Allrad	Diesel	180	245	Jun 2018	Feb 2021	2024-03-01	131858
Renault	Koleos i	2.0 DCI	SUV	Frontantrieb	Diesel	127	173	Jul 2013	-	2026-04-01	131864
Lancia	Beta	2	Stufenheck	Frontantrieb	Benzin	90	122	Jun 1978	Oct 1982	2024-03-01	131879
Mitsubishi	Delica / space gear	2.5	Bus	Allrad	Diesel	73	99	May 1995	May 2000	2024-03-01	131881
Volvo	Xc40	D3 AWD	SUV	Allrad	Diesel	110	150	Sep 2018	Sep 2021	2024-03-01	131882
Rolls-royce	Silver spirit mk ii	6.75	Stufenheck	Heckantrieb	Benzin	166	226	Oct 1989	Sep 1997	2024-03-01	131886
Hyundai	Santa fe iv	2.2 Crdi	SUV	Frontantrieb	Diesel	147	200	Jul 2018	Nov 2020	2024-03-01	131897
Hyundai	Santa fe iv	2.2 Crdi AWD	SUV	Allrad	Diesel	147	200	Jul 2018	Nov 2020	2024-03-01	131898
Toyota	Celica	2.8 Supra	Coupe	Heckantrieb	Benzin	103	140	Dec 1981	Dec 1985	2024-03-01	131901
Hyundai	Santa fe iv	2.4 AWD	SUV	Allrad	Benzin	127	173	Jul 2018	Jul 2020	2024-03-01	131903
Bentley	Arnage	6.7 V8 T	Stufenheck	Heckantrieb	Benzin	336	457	Feb 2002	Aug 2005	2024-03-01	131906
Renault	Megane iv	1.3 TCE 115	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2018	-	2024-03-01	131930
Renault	Megane iv	1.3 TCE 140	Schrägheck	Frontantrieb	Benzin	103	140	Jan 2018	-	2024-03-01	131933
Renault	Megane iv	1.3 TCE 160	Schrägheck	Frontantrieb	Benzin	120	163	Jan 2018	-	2024-03-01	131934
Renault	Megane iv grandtour	1.3 TCE 115	Kombi	Frontantrieb	Benzin	85	116	Jan 2018	-	2024-03-01	131935
Renault	Megane iv grandtour	1.3 TCE 140	Kombi	Frontantrieb	Benzin	103	140	Jan 2018	-	2024-03-01	131936
Renault	Megane iv grandtour	1.3 TCE 160	Kombi	Frontantrieb	Benzin	120	163	Jan 2018	-	2024-03-01	131937
Mazda	Cx-3	2.0 Skyactiv-g	SUV	Frontantrieb	Benzin	89	121	Feb 2018	-	2024-03-01	131940
Nissan	Skyline	2	Coupe	Heckantrieb	Benzin	160	218	Jan 1990	Jan 1993	2024-03-01	131951
Ford	Fiesta vii van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	92	125	Sep 2018	-	2024-03-01	131963
Ford	Fiesta vii van	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	88	120	Sep 2018	-	2024-03-01	131964
Ssangyong	Rexton	2	SUV	Heckantrieb	Benzin	165	224	Jul 2018	-	2024-03-01	131965
Ssangyong	Rexton	2.0 Allrad	SUV	Allrad	Benzin	165	224	Jul 2018	-	2024-03-01	131966
Mazda	6	2.2 D	Stufenheck	Frontantrieb	Diesel	135	184	Mar 2018	Nov 2020	2024-07-01	131970
Mazda	6	2.2 D	Kombi	Frontantrieb	Diesel	135	184	Mar 2018	Dec 2020	2024-03-01	131971
Mazda	6	2.2 D AWD	Kombi	Allrad	Diesel	135	184	Mar 2018	Dec 2020	2024-03-01	131972
Tesla	Model s	75D AWD	Schrägheck	Allrad	Elektro	245	333	Jun 2016	Apr 2026	2026-06-01	131973
Honda	Civic x	1.0 Vtec	Schrägheck	Frontantrieb	Benzin	93	126	Jul 2018	Dec 2022	2024-03-01	131976
Mercedes-benz	C-Klasse	C 220 D 4-matic	Coupe	Allrad	Diesel	143	194	Jun 2018	Apr 2023	2024-03-01	131979
Mercedes-benz	C-Klasse	C 220 D 4-matic	Cabriolet	Allrad	Diesel	143	194	Jun 2018	Apr 2023	2024-03-01	131980
Mercedes-benz	A-Klasse	A 220 4-matic	Schrägheck	Allrad	Benzin	140	190	Jul 2018	Oct 2019	2024-03-01	131981
Mercedes-benz	A-Klasse	A 250 4-matic	Schrägheck	Allrad	Benzin	165	224	Jul 2018	-	2024-03-01	131982
Tesla	Model s	90D AWD	Schrägheck	Allrad	Elektro	386	525	Sep 2015	Apr 2026	2026-06-01	131983
Tesla	Model s	100d AWD	Schrägheck	Allrad	Elektro	386	525	Jun 2017	Apr 2026	2026-06-01	131984
Mercedes-benz	C-Klasse	C 200 D	Coupe	Heckantrieb	Diesel	118	160	Jul 2018	Nov 2019	2024-03-01	131985
Mercedes-benz	C-Klasse	C 200 D	Cabriolet	Heckantrieb	Diesel	118	160	Jul 2018	Nov 2019	2024-03-01	131986
Mercedes-benz	Slc	AMG SLC 43	Cabriolet	Heckantrieb	Benzin	287	390	Jun 2018	-	2024-03-01	131987
Mercedes-benz	Sl	63 AMG	Cabriolet	Heckantrieb	Benzin	420	571	Jul 2018	May 2019	2024-03-01	131988
Ford	Transit tourneo	2	Bus	Frontantrieb	Diesel	74	101	Jun 2000	Mar 2005	2024-03-01	131990
Chevrolet	Lanos	1.5	Stufenheck	Frontantrieb	Benzin	63	86	Nov 2005	Dec 2010	2024-03-01	131991
Mercedes-benz	C-Klasse	C 300 D	Coupe	Heckantrieb	Diesel	180	245	Jul 2018	Apr 2023	2024-03-01	131992
Mercedes-benz	C-Klasse	C 300 D 4-matic	Coupe	Allrad	Diesel	180	245	Jul 2018	Apr 2023	2024-03-01	131993
Mercedes-benz	C-Klasse	C 300 D	Cabriolet	Heckantrieb	Diesel	180	245	Jul 2018	Apr 2023	2024-03-01	131994
Mercedes-benz	Cla	CLA 220 D	Kombi	Frontantrieb	Diesel	125	170	Jul 2018	Mar 2019	2024-03-01	131995
Mercedes-benz	Cla	CLA 220 D 4-matic	Kombi	Allrad	Diesel	125	170	Jul 2018	Mar 2019	2024-03-01	131996
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	279	379	Oct 2014	Feb 2016	2024-03-01	131998
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	118	160	Aug 2018	-	2024-03-01	131999
Tesla	Model s	P100d AWD	Schrägheck	Allrad	Elektro	450	612	Oct 2016	Apr 2026	2026-06-01	132000
Opel	Astra g	1.7 Cdti	Kasten/Kombi	Frontantrieb	Diesel	59	80	Jul 2003	Nov 2004	2024-03-01	132001
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	140	190	Aug 2018	-	2024-03-01	132002
Tesla	Model s	P90d AWD	Schrägheck	Allrad	Elektro	568	772	Sep 2015	Apr 2026	2026-06-01	132003
Alfa Romeo	Stelvio	2.2 Jtdm Q4	SUV	Allrad	Diesel	140	190	Aug 2018	-	2024-03-01	132004
Land Rover	Freelander i soft top	2.5 V6 4X4	Geländewagen offen	Allrad	Benzin	130	177	Nov 2000	Oct 2006	2024-03-01	132008
Hyundai	Ix35	2	SUV	Frontantrieb	Benzin	113	154	Aug 2013	Dec 2015	2024-03-01	132021
Dodge	Durango	6.0 4WD	SUV	Allrad	Benzin	184	250	Dec 1997	Oct 2003	2024-03-01	132025
Mercedes-benz	Gl-Klasse	GL 500 4-matic	SUV	Allrad	Benzin	300	408	Jul 2014	Oct 2015	2024-03-01	132045
Jeep	Grand cherokee iii	4.7 V8	Geländewagen geschlossen	Heckantrieb	Benzin	167	227	Oct 2004	May 2010	2024-03-01	132056
Mini	Mini	1.6 Cooper	Coupe	Frontantrieb	Benzin	88	120	Oct 2014	May 2015	2024-03-01	132076
Mercedes-benz	E-Klasse	AMG E53 EQ Boost 4-matic+	Cabriolet	Allrad	Benzin/Elektro	320	435	May 2018	-	2024-03-01	132083


--- Round 1 / 首次发送 ---
## 更新点

* 按缓存优先完成首批复用：BMW F39/G30/G31/G32、Mercedes-Benz W205/S205/C205/A205/W177/X117、Volvo XC40、Hyundai Santa Fe TM 等现有尺寸组仅新增映射，不重复抓取或输出尺寸。BMW 官方技术资料确认了 F39、G30、G31、G32 的车型边界。([BMW Group PressClub][1])
* 2018 C4 Cactus 已按改款五门掀背关联已有尺寸组；Mercedes-Benz CLA Shooting Brake 确认为 X117，C-Class 轿跑/敞篷分别采用 C205/A205。([Stellantis Media][2])
* 本轮没有首次创建或纠正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：43
* READY 映射行：43
* PENDING Ktype：57
* 已引用并确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131809	131809	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背。	READY
131826	131826	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	2018改款五门掀背。	READY
131828	131828	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV。	READY
131830	131830	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV。	READY
131832	131832	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车。	READY
131833	131833	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车。	READY
131834	131834	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31五门旅行车；驱动形式不改变外廓。	READY
131835	131835	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31五门旅行车；驱动形式不改变外廓。	READY
131836	131836	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门掀背式Gran Turismo。	READY
131837	131837	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门掀背式Gran Turismo。	READY
131843	131843	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车。	READY
131844	131844	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车。	READY
131853	131853	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	第一代XC40五门SUV。	READY
131857	131857	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车。	READY
131858	131858	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车。	READY
131881	131881	MPV	Delica Space Gear	L400		EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	HIGH	L400标准车身MPV。	READY
131882	131882	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	第一代XC40五门SUV。	READY
131897	131897	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131898	131898	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131903	131903	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131940	131940	SUV	CX-3 I facelift	DK	5	EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	HIGH	DK改款五门SUV。	READY
131965	131965	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-SUV-01	HIGH	Y400五门SUV。	READY
131966	131966	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-SUV-01	HIGH	Y400五门SUV。	READY
131973	131973	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
131976	131976	Hatchback	Civic X		5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	第十代五门掀背。	READY
131979	131979	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131980	131980	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131981	131981	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177五门掀背。	READY
131982	131982	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177五门掀背。	READY
131984	131984	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
131985	131985	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131986	131986	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131990	131990	MPV	Transit/Tourneo Mk6			EU-FORD-TRANSIT-TOURNEO-MK6-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo客车。	READY
131992	131992	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131993	131993	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131994	131994	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131995	131995	Wagon	CLA I facelift	X117	5	EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	HIGH	X117改款五门Shooting Brake。	READY
131996	131996	Wagon	CLA I facelift	X117	5	EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	HIGH	X117改款五门Shooting Brake。	READY
131999	131999	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132000	132000	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
132002	132002	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132004	132004	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132021	132021	SUV	ix35 I facelift	LM	5	EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	HIGH	LM改款五门SUV。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Mazda 6 2018 改款轿车/旅行车、Alfa Romeo Giulia 952、Renault Megane IV 掀背/旅行车和 Ford Ka+ 的乘用车簇。
2. 单独处理 Tesla Model S 改款前、跨改款 Ktype 131983/132003 的派生边界。
3. 随后处理 Rolls-Royce Corniche/Camargue/Silver Shadow/Silver Spirit、Mercedes-Benz G-Class 开放式 W460 等历史车型簇。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0278876EN/technical-specifications-of-the-new-bmw-x2-valid-from-03/2018?utm_source=chatgpt.com "Technical Specifications of the new BMW X2, valid from 03/2018."
[2]: https://www.media.stellantis.com/em-en/citroen/press/new-c4-cactus-the-ultra-comfortable-hatchback-with-a-unique-personality?utm_source=chatgpt.com "NEW C4 CACTUS, THE ULTRA-COMFORTABLE HATCHBACK WITH A UNIQUE PERSONALITY | Citroën | Stellantis Media"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮按物理车身聚类首次闭合 **11 个尺寸组**，批量新增 **21 个 READY Ktype 映射**；既有22个缓存尺寸组未重复抓取或输出。
* Mazda6 改款轿车/旅行车、Alfa Romeo Giulia 后驱/Q4、Renault Megane IV 掀背/Grandtour 和 Ford Ka+ 改款的外廓及不含后视镜宽度已闭合。
* Mercedes-Benz B-Class W246、Ferrari 488 Pista、Subaru Forester SK 和 Peugeot 301 改款同步完成首次建组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射行：64
* PENDING Ktype：36
* 已确认尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131792	131792	Hatchback	B-Class II facelift	W246	5	EU-MERCEDES-BENZ-B-KLASSE-W246-HATCHBACK-FACELIFT-01	HIGH	W246改款五门掀背式Sports Tourer。	READY
131816	131816	Sedan	Mazda6 III facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车。	READY
131822	131822	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
131829	131829	Sedan	301 I facelift		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH	第一代改款四门轿车。	READY
131838	131838	Coupe	488		2	EU-FERRARI-488-PISTA-COUPE-01	HIGH	488 Pista双门硬顶车身。	READY
131840	131840	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK五门SUV。	READY
131841	131841	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK五门SUV。	READY
131842	131842	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH	952后驱四门轿车。	READY
131845	131845	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH	952后驱四门轿车。	READY
131847	131847	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH	第三代改款五门掀背。	READY
131848	131848	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH	第三代改款五门掀背。	READY
131849	131849	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	952 Q4四驱四门轿车；标准车高与后驱版不同。	READY
131930	131930	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131933	131933	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131934	131934	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131935	131935	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131936	131936	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131937	131937	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131970	131970	Sedan	Mazda6 III facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车。	READY
131971	131971	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
131972	131972	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-B-KLASSE-W246-HATCHBACK-FACELIFT-01	4393	1786	1557	Mercedes-Benz The B-Class brochure	https://i.i-sgcm.com/new_cars/cars/11195/brochures/brochure_20161005124035.pdf
EU-MAZDA-6-III-FACELIFT-SEDAN-01	4870	1840	1450	Mazda UK Mazda6 Price and Specification Guide	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy157/p2/sept-pricing/mazda6-price--specs.pdf?rnd=4a589b
EU-MAZDA-6-III-FACELIFT-WAGON-01	4805	1840	1475	Mazda UK Mazda6 Price and Specification Guide	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy157/p2/sept-pricing/mazda6-price--specs.pdf?rnd=4a589b
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466	Peugeot Ghana 301 official page; Auto-Data Peugeot 301 facelift 1.5 BlueHDi 102	https://www.peugeot.com.gh/our-models/301.html;https://www.auto-data.net/en/peugeot-301-facelift-2017-1.5-bluehdi-102hp-36346
EU-FERRARI-488-PISTA-COUPE-01	4605	1975	1206	Ferrari 488 Pista official specifications	https://www.ferrari.com/en-EN/auto/ferrari-488-pista
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730	Subaru Asia Forester 2019 specifications; Subaru Forester e-BOXER brochure	https://www.subaru.asia/brochures/forester19_specs_ph.pdf;https://www.carparisonleasing.co.uk/files/328/Subaru%20Forester%20e-Boxer%20Brochure.pdf
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436	Alfa Romeo Canada 2018 Giulia Specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2018-alfaromeo-giulia-specifications-en.pdf
EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	3941	1704	1524	Ford New KA+ official brochure; Automobile-Catalog 2018 Ford Ka+ 1.5 TDCi 95	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_KA%2B.pdf;https://www.automobile-catalog.com/car/2018/2740175/ford_ka_plus_1_5_tdci_95.html
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450	Alfa Romeo Canada 2018 Giulia Specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2018-alfaromeo-giulia-specifications-en.pdf
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Renault Egypt Megane Hatchback September 2018 flyer	https://renault.com.eg/CountriesData/Egypt/images/pdf/files1/Megane_HB_A4_folded_flyer_Sep-2018.pdf
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457	Renault UK Megane Sport Tourer Press Kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14255-RenaultMeganeSportTourerPressKitMay2018.pdf
```

## 下一步优先处理

1. 闭合 Rolls-Royce Camargue、Corniche、Silver Shadow、Silver Spirit 历史车型簇。
2. 处理 Mercedes-Benz G-Class 开放式 W460、SLC、SL、E53 Cabriolet 和 GL-Class。
3. 处理剩余单车型簇：Peugeot 407、C-Elysée、Accent V、Koleos I、Lancia Beta Sedan、Celica Supra、Skyline R32、Fiesta Van、Astra G Van、Freelander Soft Top、Durango、Grand Cherokee III 和 MINI Coupe。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 36 个 Ktype 已闭合；本批次共形成 **106 条 READY 映射**，覆盖全部 **100 个输入 Ktype**。
* 131815、131817、131820 按 W460/W463 拆分；131983、132003 按 Model S 改款前后拆分；132008 按 Freelander I 改款前后拆分。
* 共维护 **63 个被引用尺寸组**，不存在孤立组或缺失引用。
* Astra G Classic II Caravan 的既有 `4288 × 1709 × 1465 mm` 缓存组已补齐可追溯来源，没有改写既有尺寸事实。([Scribd][1])
* 已完成表头、主键唯一性、引用闭合、尺寸和来源非空以及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：106
* PENDING：0
* DIMENSION_GROUP：63
* 唯一 `id`：106
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131790	131790	Sedan	407 I	6D	4	EU-PEUGEOT-407-I-SEDAN-01	HIGH	6D四门轿车。	READY
131792	131792	Hatchback	B-Class II facelift	W246	5	EU-MERCEDES-BENZ-B-KLASSE-W246-HATCHBACK-FACELIFT-01	HIGH	W246改款五门Sports Tourer。	READY
131801	131801	Coupe	Camargue		2	EU-ROLLS-ROYCE-CAMARGUE-I-COUPE-01	HIGH	双门固定顶车身。	READY
131802	131802	Convertible	Corniche II		2	EU-ROLLS-ROYCE-CORNICHE-II-CONVERTIBLE-01	HIGH	Corniche II双门敞篷。	READY
131803	131803	Convertible	Corniche I facelift		2	EU-ROLLS-ROYCE-CORNICHE-I-CONVERTIBLE-FACELIFT-01	HIGH	Corniche I后期双门敞篷。	READY
131804	131804	Coupe	Corniche I		2	EU-ROLLS-ROYCE-CORNICHE-I-COUPE-01	HIGH	输入车身标签按固定顶双门外廓校正。	READY
131805	131805	Convertible	Corniche I		2	EU-ROLLS-ROYCE-CORNICHE-I-CONVERTIBLE-PREFL-01	HIGH	Corniche I前期双门敞篷。	READY
131808	131808	Sedan	Silver Shadow II		4	EU-ROLLS-ROYCE-SILVER-SHADOW-II-SEDAN-01	HIGH	Silver Shadow II四门轿车。	READY
131809	131809	Hatchback	308 II facelift	T9	5	EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	HIGH	T9改款五门掀背。	READY
131812	131812	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	W460短轴开放式车身。	READY
131814	131814	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	W460短轴开放式车身。	READY
131815_w460	131815	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W460短轴开放式分支。	READY
131815_w463	131815	SUV	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W463短轴开放式分支。	READY
131816	131816	Sedan	Mazda6 III facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车。	READY
131817_w460	131817	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W460短轴开放式分支。	READY
131817_w463	131817	SUV	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W463短轴开放式分支。	READY
131820_w460	131820	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W460短轴开放式分支。	READY
131820_w463	131820	SUV	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	HIGH	Ktype跨W460/W463；本行为W463短轴开放式分支。	READY
131821	131821	SUV	G-Class W460	W460	2	EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	HIGH	W460短轴开放式车身。	READY
131822	131822	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
131826	131826	Hatchback	C4 Cactus I facelift		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	2018改款五门掀背。	READY
131827	131827	Sedan	C-Elysee I facelift		4	EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	HIGH	第一代改款四门轿车。	READY
131828	131828	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV。	READY
131829	131829	Sedan	301 I facelift		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH	第一代改款四门轿车。	READY
131830	131830	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV。	READY
131831	131831	Sedan	Accent V	HC	4	EU-HYUNDAI-ACCENT-V-SEDAN-01	HIGH	HC四门轿车。	READY
131832	131832	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车。	READY
131833	131833	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH	G30四门轿车。	READY
131834	131834	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31五门旅行车。	READY
131835	131835	Wagon	5 Series VII	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31五门旅行车。	READY
131836	131836	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo。	READY
131837	131837	Hatchback	6 Series Gran Turismo I	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo。	READY
131838	131838	Coupe	488		2	EU-FERRARI-488-PISTA-COUPE-01	HIGH	488 Pista双门硬顶车身。	READY
131840	131840	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK五门SUV。	READY
131841	131841	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK五门SUV。	READY
131842	131842	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH	952后驱四门轿车。	READY
131843	131843	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车。	READY
131844	131844	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205改款四门轿车。	READY
131845	131845	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH	952后驱四门轿车。	READY
131847	131847	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH	第三代改款五门掀背。	READY
131848	131848	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH	第三代改款五门掀背。	READY
131849	131849	Sedan	Giulia I	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	952 Q4四驱四门轿车。	READY
131853	131853	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	第一代XC40五门SUV。	READY
131857	131857	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车。	READY
131858	131858	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款五门旅行车。	READY
131864	131864	SUV	Koleos I facelift	HY	5	EU-RENAULT-KOLEOS-I-FACELIFT-SUV-01	HIGH	第一代改款五门SUV。	READY
131879	131879	Sedan	Beta Berlina facelift	828	4	EU-LANCIA-BETA-828-SEDAN-FACELIFT-01	HIGH	828后期四门Berlina。	READY
131881	131881	MPV	Delica Space Gear	L400		EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	HIGH	L400标准车身MPV。	READY
131882	131882	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	第一代XC40五门SUV。	READY
131886	131886	Sedan	Silver Spirit II		4	EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	HIGH	Silver Spirit II四门轿车。	READY
131897	131897	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131898	131898	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131901	131901	Coupe	Celica Supra II	A60	3	EU-TOYOTA-CELICA-SUPRA-A60-COUPE-01	HIGH	A60三门掀背式轿跑。	READY
131903	131903	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH	TM五门SUV。	READY
131906	131906	Sedan	Arnage I		4	EU-BENTLEY-ARNAGE-I-T-SEDAN-01	HIGH	Arnage T四门轿车。	READY
131930	131930	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131933	131933	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131934	131934	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	第四代五门掀背。	READY
131935	131935	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131936	131936	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131937	131937	Wagon	Megane IV	KFB	5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH	KFB五门Grandtour旅行车。	READY
131940	131940	SUV	CX-3 I facelift	DK	5	EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	HIGH	DK改款五门SUV。	READY
131951	131951	Coupe	Skyline VIII	R32	2	EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	HIGH	R32后驱双门GTS外廓。	READY
131963	131963	Van	Fiesta VII Van	B479	3	EU-FORD-FIESTA-VII-VAN-SPORT-01	HIGH	三门Sport系列厢式车身。	READY
131964	131964	Van	Fiesta VII Van	B479	3	EU-FORD-FIESTA-VII-VAN-SPORT-01	HIGH	三门Sport系列厢式车身。	READY
131965	131965	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-SUV-01	HIGH	Y400五门SUV。	READY
131966	131966	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-SUV-01	HIGH	Y400五门SUV。	READY
131970	131970	Sedan	Mazda6 III facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH	第三代改款四门轿车。	READY
131971	131971	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
131972	131972	Wagon	Mazda6 III facelift		5	EU-MAZDA-6-III-FACELIFT-WAGON-01	HIGH	第三代改款五门旅行车。	READY
131973	131973	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
131976	131976	Hatchback	Civic X		5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	第十代五门掀背。	READY
131979	131979	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131980	131980	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131981	131981	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177五门掀背。	READY
131982	131982	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH	W177五门掀背。	READY
131983_prefl	131983	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	Ktype跨2016改款；本行为改款前分支。	READY
131983_facelift	131983	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	Ktype跨2016改款；本行为改款后分支。	READY
131984	131984	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
131985	131985	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131986	131986	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131987	131987	Convertible	SLC facelift	R172	2	EU-MERCEDES-BENZ-SLC-R172-AMG-SLC43-CONVERTIBLE-01	HIGH	R172 AMG SLC 43双门敞篷。	READY
131988	131988	Convertible	SL VI facelift	R231	2	EU-MERCEDES-BENZ-SL-R231-AMG-SL63-CONVERTIBLE-FACELIFT-01	HIGH	R231改款AMG SL 63双门敞篷。	READY
131990	131990	MPV	Transit/Tourneo Mk6			EU-FORD-TRANSIT-TOURNEO-MK6-BUS-SWB-LOWROOF-01	HIGH	短轴低顶Tourneo客车。	READY
131991	131991	Sedan	Lanos I	T150	4	EU-CHEVROLET-LANOS-I-SEDAN-01	HIGH	T150四门轿车。	READY
131992	131992	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131993	131993	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH	C205改款双门轿跑。	READY
131994	131994	Convertible	C-Class IV facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH	A205改款双门敞篷。	READY
131995	131995	Wagon	CLA I facelift	X117	5	EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	HIGH	X117改款五门Shooting Brake。	READY
131996	131996	Wagon	CLA I facelift	X117	5	EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	HIGH	X117改款五门Shooting Brake。	READY
131998	131998	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	改款前五门掀背。	READY
131999	131999	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132000	132000	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	2016改款后五门掀背。	READY
132001	132001	Van	Astra G	F35	5	EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	MEDIUM	F35旅行车衍生厢式外廓，复用相同车身尺寸组。	READY
132002	132002	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132003_prefl	132003	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	Ktype跨2016改款；本行为改款前分支。	READY
132003_facelift	132003	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	Ktype跨2016改款；本行为改款后分支。	READY
132004	132004	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949五门SUV。	READY
132008_prefl	132008	SUV	Freelander I pre-facelift	L314	3	EU-LAND-ROVER-FREELANDER-I-L314-SOFTBACK-PREFL-01	HIGH	Ktype跨2003外观改款；本行为改款前Softback分支。	READY
132008_facelift	132008	SUV	Freelander I facelift	L314	3	EU-LAND-ROVER-FREELANDER-I-L314-SOFTBACK-FACELIFT-01	HIGH	Ktype跨2003外观改款；本行为改款后Softback分支。	READY
132021	132021	SUV	ix35 I facelift	LM	5	EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	HIGH	LM改款五门SUV。	READY
132025	132025	SUV	Durango I	DN	5	EU-DODGE-DURANGO-I-SUV-01	HIGH	DN五门SUV。	READY
132045	132045	SUV	GL-Class II	X166	5	EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	HIGH	X166五门SUV。	READY
132056	132056	SUV	Grand Cherokee III	WK	5	EU-JEEP-GRAND-CHEROKEE-III-WK-SUV-01	HIGH	WK五门SUV。	READY
132076	132076	Coupe	MINI Coupe	R58	2	EU-MINI-MINI-R58-COUPE-COOPER-01	HIGH	R58双门Coupe。	READY
132083	132083	Convertible	E-Class V	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	HIGH	A238 AMG E53双门敞篷。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2401-2500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-407-I-SEDAN-01	4676	1811	1455	CarSized Peugeot 407 2004 sedan	https://www.carsized.com/en/cars/peugeot-407-2004-sedan/
EU-MERCEDES-BENZ-B-KLASSE-W246-HATCHBACK-FACELIFT-01	4393	1786	1557	Mercedes-Benz The B-Class brochure	https://i.i-sgcm.com/new_cars/cars/11195/brochures/brochure_20161005124035.pdf
EU-ROLLS-ROYCE-CAMARGUE-I-COUPE-01	5169	1918	1478	Automobile-Catalog 1975 Rolls-Royce Camargue	https://www.automobile-catalog.com/car/1975/29090/rolls-royce_camargue.html
EU-ROLLS-ROYCE-CORNICHE-II-CONVERTIBLE-01	5196	1836	1518	Automobile-Catalog 1988 Rolls-Royce Corniche II	https://www.automobile-catalog.com/car/1988/2993060/rolls-royce_corniche_ii.html
EU-ROLLS-ROYCE-CORNICHE-I-CONVERTIBLE-FACELIFT-01	5196	1836	1518	Automobile-Catalog 1986 Rolls-Royce Corniche	https://www.automobile-catalog.com/car/1986/2992985/rolls-royce_corniche.html
EU-ROLLS-ROYCE-CORNICHE-I-COUPE-01	5194	1829	1492	Automobile-Catalog 1978 Rolls-Royce Corniche	https://www.automobile-catalog.com/car/1978/44195/rolls-royce_corniche.html
EU-ROLLS-ROYCE-CORNICHE-I-CONVERTIBLE-PREFL-01	5194	1829	1518	Automobile-Catalog 1977 Rolls-Royce Corniche Convertible	https://www.automobile-catalog.com/car/1977/24380/rolls-royce_corniche_convertible.html
EU-ROLLS-ROYCE-SILVER-SHADOW-II-SEDAN-01	5194	1822	1518	Automobile-Catalog 1978 Rolls-Royce Silver Shadow II	https://www.automobile-catalog.com/car/1978/36380/rolls-royce_silver_shadow_ii.html
EU-PEUGEOT-308-II-T9-HATCHBACK-FACELIFT-01	4253	1804	1457	Auto-Data Peugeot 308 II Phase II	https://www.auto-data.net/en/peugeot-308-ii-phase-ii-2017-generation-5518
EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	4145	1700	2000	Auto-Data Mercedes-Benz G-Class Cabriolet W460 300 GD	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w460-300-gd-88hp-4wd-47944
EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	4185	1690	1967	Mercedes-Benz Public Archive W463 G Cabriolet; UltimateSpecs W463 250 GD SWB	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/picture/G-Cabriolet-Off-Roader---W-463.xhtml?oid=55838;https://www.ultimatespecs.com/car-specs/Mercedes-Benz/128939/Mercedes-Benz-G-Class-SWB-%28W463%29-250-GD.html
EU-MAZDA-6-III-FACELIFT-SEDAN-01	4870	1840	1450	Mazda UK Mazda6 Price and Specification Guide	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy157/p2/sept-pricing/mazda6-price--specs.pdf?rnd=4a589b
EU-MAZDA-6-III-FACELIFT-WAGON-01	4805	1840	1475	Mazda UK Mazda6 Price and Specification Guide	https://media-assets.mazda.eu/raw/upload//mazdauk/globalassets/uk/pdfs/fy157/p2/sept-pricing/mazda6-price--specs.pdf?rnd=4a589b
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480	Automobile-Catalog 2018 Citroen C4 Cactus PureTech 110	https://www.automobile-catalog.com/car/2018/2630870/citroen_c4_cactus_puretech_110.html
EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	4419	1748	1466	Automobile-Catalog 2018 Citroen C-Elysee	https://www.automobile-catalog.com/car/2018/2513420/citroen_c-elysee_puretech_82_live.html
EU-BMW-X2-F39-SUV-01	4360	1824	1526	BMW Group PressClub X2 technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0283649EN/technical-specifications-of-the-new-bmw-x2-valid-from-10/2017
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466	Peugeot Ghana 301 official page; Auto-Data Peugeot 301 facelift 1.5 BlueHDi 102	https://www.peugeot.com.gh/our-models/301.html;https://www.auto-data.net/en/peugeot-301-facelift-2017-1.5-bluehdi-102hp-36346
EU-HYUNDAI-ACCENT-V-SEDAN-01	4385	1729	1450	Hyundai Accent 2018 official specifications	https://www.hyundai.com/pacific/en/find-a-car/accent-2018/specification
EU-BMW-5-G30-SEDAN-01	4936	1868	1466	BMW Group PressClub 5 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/detail/T0286565EN/specifications-of-the-bmw-5-series-sedan-valid-from-09/2018
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498	BMW Group PressClub 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/detail/T0286567EN/specifications-of-the-bmw-5-series-touring-valid-from-09/2018?language=en
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	BMW UK 6 Series Gran Turismo technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0271717EN_GB/395434
EU-FERRARI-488-PISTA-COUPE-01	4605	1975	1206	Ferrari 488 Pista official specifications	https://www.ferrari.com/en-EN/auto/ferrari-488-pista
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730	Subaru Asia Forester 2019 specifications; Subaru Forester e-BOXER brochure	https://www.subaru.asia/brochures/forester19_specs_ph.pdf;https://www.carparisonleasing.co.uk/files/328/Subaru%20Forester%20e-Boxer%20Brochure.pdf
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436	Alfa Romeo Canada 2018 Giulia Specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2018-alfaromeo-giulia-specifications-en.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Automobile-Catalog 2019 Mercedes-Benz C 300 d	https://www.automobile-catalog.com/car/2019/2967365/mercedes-benz_c_300_d.html
EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	3941	1704	1524	Ford New KA+ official brochure; Automobile-Catalog 2018 Ford Ka+ 1.5 TDCi 95	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_KA%2B.pdf;https://www.automobile-catalog.com/car/2018/2740175/ford_ka_plus_1_5_tdci_95.html
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450	Alfa Romeo Canada 2018 Giulia Specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2018-alfaromeo-giulia-specifications-en.pdf
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo XC40 Support dimensions	https://www.volvocars.com/uk/support/car/xc40/17w46/article/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Mercedes-Benz C-Class Estate brochure	https://www.mb.zungfu.com/brochure/C-Class-S205.pdf
EU-RENAULT-KOLEOS-I-FACELIFT-SUV-01	4520	1855	1690	CarsGuide Renault Koleos 2013 dimensions	https://www.carsguide.com.au/renault/koleos/car-dimensions/2013
EU-LANCIA-BETA-828-SEDAN-FACELIFT-01	4295	1706	1400	Automobile-Catalog 1978 Lancia Beta 2000 Berlina	https://www.automobile-catalog.com/car/1978/1376675/lancia_beta_2000_2a_serie_fl.html
EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	4655	1695	1855	Cars Japan Mitsubishi Delica Space Gear body dimensions	https://cars-japan.net/body/mdl00400285.html
EU-ROLLS-ROYCE-SILVER-SPIRIT-II-SEDAN-01	5268	1887	1485	Automobile-Catalog 1990 Rolls-Royce Silver Spirit II	https://www.automobile-catalog.com/car/1990/2993510/rolls-royce_silver_spirit_ii.html
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai 2018 Santa Fe TM official history	https://www.hyundai.com/kr/ko/brand/brandstory/model/santafe-history/2018-santa-fe-tm
EU-TOYOTA-CELICA-SUPRA-A60-COUPE-01	4620	1720	1315	Automobile-Catalog 1984 Toyota Celica Supra 2.8i OHC	https://www.automobile-catalog.com/car/1984/3507965/toyota_celica_supra_2_8i_ohc.html
EU-BENTLEY-ARNAGE-I-T-SEDAN-01	5400	1932	1515	Automobile-Catalog 2002 Bentley Arnage T	https://www.automobile-catalog.com/car/2002/261095/bentley_arnage_t.html
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Renault Egypt Megane Hatchback September 2018 flyer	https://renault.com.eg/CountriesData/Egypt/images/pdf/files1/Megane_HB_A4_folded_flyer_Sep-2018.pdf
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457	Renault UK Megane Sport Tourer Press Kit May 2018	https://www.press.renault.co.uk/assets/documents/original/14255-RenaultMeganeSportTourerPressKitMay2018.pdf
EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	4275	1765	1535	Automobile-Catalog 2018 Mazda CX-3 2.0 SkyActiv-G 150 AWD	https://www.automobile-catalog.com/car/2018/2768900/mazda_cx-3_2_0_skyactiv-g_150_awd.html
EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	4530	1695	1325	Automobile-Catalog 1990 Nissan Skyline GTS 2-door	https://www.automobile-catalog.com/car/1990/2134955/nissan_skyline_2door_sports_coupe_gts.html
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466	Ford New Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-SSANGYONG-REXTON-II-SUV-01	4850	1960	1825	ADAC SsangYong Rexton 2018 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ssangyong/rexton/2generation/284957/
EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	4970	1964	1445	Tesla Model S Owner's Manual	https://www.tesla.com/ownersmanual/2012_2020_models/en_eu/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434	Honda News Europe 2018 Civic i-DTEC; Honest John Civic specifications	https://hondanews.eu/gb/en/cars/media/pressreleases/125516/2018-honda-civic-16-i-dtec;https://www.honestjohn.co.uk/honda/civic/2017/specs/
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Automobile-Catalog 2019 Mercedes-Benz C 220 d Coupe	https://www.automobile-catalog.com/car/2019/2727050/mercedes-benz_c_220_d_coupe.html
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Automobile-Catalog 2019 Mercedes-Benz C 220 d Cabriolet	https://www.automobile-catalog.com/car/2019/2727155/mercedes-benz_c_220_d_cabriolet.html
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440	Mercedes-Benz UK A-Class world premiere; Mercedes-Benz A-Class technical history	https://mercedes-benz-media.co.uk/releases/54;https://www.mercedesman.ru/en/A-Class
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4978	1963	1435	Edmunds 2015 Tesla Model S specifications	https://www.edmunds.com/tesla/model-s/2015/features-specs/
EU-MERCEDES-BENZ-SLC-R172-AMG-SLC43-CONVERTIBLE-01	4143	1817	1303	Automobile-Catalog 2018 Mercedes-AMG SLC 43	https://www.automobile-catalog.com/car/2018/2297705/mercedes-amg_slc_43.html
EU-MERCEDES-BENZ-SL-R231-AMG-SL63-CONVERTIBLE-FACELIFT-01	4641	1877	1300	Mercedes-Benz USA 2018 AMG SL63 specifications	https://media.mbusa.com/releases/release-f64df5efcf40bb28fb4d418ddc1fddb1-2018-mercedes-amg-sl63-roadster-specifications
EU-FORD-TRANSIT-TOURNEO-MK6-BUS-SWB-LOWROOF-01	4863	1974	1989	Drom Ford Tourneo dimensions 2000	https://www.drom.ru/catalog/ford/tourneo/specs/dimensions/
EU-CHEVROLET-LANOS-I-SEDAN-01	4237	1678	1432	Auto-Data Chevrolet Lanos 1.5i	https://www.auto-data.net/en/chevrolet-lanos-1.5-i-86hp-14455
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435	Mercedes-Benz CLA-Class C117/X117 brochure	https://www.australiancar.reviews/_pdfs/Mercedes-Benz_CLA-Class_C117-X117_Brochure_201501.pdf
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Alfa Romeo Stelvio Stellantis Media; Auto Motor und Sport Stelvio technical data	https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-alfa-romeo-stelvio;https://www.auto-motor-und-sport.de/test/alfa-romeo-stelvio-2-0-turbo/technische-daten/
EU-OPEL-ASTRA-G-CLASSIC-II-WAGON-01	4288	1709	1465	Opel Astra Classic II Features Guide	https://www.scribd.com/document/92727488/Astra-Classic-II
EU-LAND-ROVER-FREELANDER-I-L314-SOFTBACK-PREFL-01	4368	1809	1757	Automobile-Catalog 2001 Land Rover Freelander Softback	https://www.automobile-catalog.com/car/2001/1401800/land_rover_freelander_1_8_s_softback.html
EU-LAND-ROVER-FREELANDER-I-L314-SOFTBACK-FACELIFT-01	4423	1809	1717	Carfolio 2003 Land Rover Freelander 2.5 V6 Softback	https://www.carfolio.com/land-rover-freelander-2.5-v6-softback-137731
EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	4410	1820	1655	Auto-Data Hyundai ix35 facelift 2013	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-generation-4093
EU-DODGE-DURANGO-I-SUV-01	4910	1816	1852	Automobile-Catalog 1998 Dodge Durango SLT 4WD 5.9 V8	https://www.automobile-catalog.com/car/1998/687905/dodge_durango_slt_4wd_5_9l_v-8.html
EU-MERCEDES-BENZ-GL-KLASSE-X166-SUV-01	5120	1934	1850	Mercedes-Benz USA 2014 GL-Class specifications	https://media.mbusa.com/releases/release-5b86968c3f0340d9a2bfc1bac40da246-2014-gl-class-specifications
EU-JEEP-GRAND-CHEROKEE-III-WK-SUV-01	4740	1862	1720	Auto-Data Jeep Grand Cherokee III WK 4.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-4.7i-v8-238hp-automatic-31267
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378	BMW Group PressClub MINI Cooper Coupe technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425	Auto-Data Mercedes-Benz E-Class Cabrio A238 AMG E53	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-amg-e-53-435hp-eq-boost-4matic-amg-speedshift-tct-34008
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2401-2500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.scribd.com/document/92727488/Astra-Classic-II?utm_source=chatgpt.com "Opel Astra Classic II Features Guide | PDF"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1676 行）
- 累计尺寸组：dimension_groups_final.tsv（845 行）

