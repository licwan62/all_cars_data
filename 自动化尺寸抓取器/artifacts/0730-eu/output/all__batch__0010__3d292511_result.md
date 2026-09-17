# 任务：all 第 901-1000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0010__3d292511


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 901-1000 行

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
all 第 901-1000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F20-HATCHBACK-5D-01	4329	1765	1421
EU-BMW-1-F20-HATCHBACK-5D-M140-01	4324	1765	1411
EU-BMW-1-F21-HATCHBACK-3D-01	4329	1765	1421
EU-BMW-1-F21-HATCHBACK-3D-M140-01	4324	1765	1411
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448
EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	4267	1732	1445
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438
EU-RENAULT-TWINGO-III-HATCHBACK-01	3595	1647	1557
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Honda	Crossroad	2	SUV	Frontantrieb	Benzin	110	150	Feb 2007	Aug 2010	2024-03-01	124130
Dacia	1100	1.1	Stufenheck	Heckantrieb	Benzin	33	45	Sep 1967	Oct 1971	2024-03-01	124153
DE Tomaso	Deauville	5.8	Stufenheck	Heckantrieb	Benzin	198	269	Jan 1974	Dec 1978	2024-03-01	124160
Dacia	Logan	1.6 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	62	84	May 2010	-	2024-03-01	124173
Maserati	Quattroporte v	4.2	Stufenheck	Heckantrieb	Benzin	298	405	Sep 2004	Dec 2012	2024-03-01	124175
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	81	110	Oct 2016	-	2024-03-01	124178
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	105	143	Oct 2016	-	2024-03-01	124179
Mazda	626 i	2	Coupe	Heckantrieb	Benzin	66	90	Oct 1978	Dec 1982	2024-03-01	124181
Mitsubishi	Colt vi	1.5 Ralliart R	Schrägheck	Frontantrieb	Benzin	132	180	Feb 2010	Jun 2012	2024-03-01	124197
Land Rover	Discovery v	2.0 TD4 4X4	SUV	Allrad	Diesel	132	180	Sep 2016	-	2024-03-01	124200
Land Rover	Discovery v	2.0 SD4 4X4	SUV	Allrad	Diesel	177	241	Sep 2016	-	2024-03-01	124201
Mitsubishi	Lancer viii	EVO X	Stufenheck	Allrad	Benzin	206	280	Oct 2007	Oct 2008	2024-03-01	124205
Morgan	Four	1.6 I	Cabriolet	Heckantrieb	Benzin	82	112	Jan 2009	-	2024-03-01	124209
BMW	3	318 TI	Schrägheck	Heckantrieb	Benzin	100	136	Mar 2001	Dec 2004	2024-03-01	124212
VW	Golf sportsvan vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2020	2024-03-01	124225
Lexus	Lc	500	Coupe	Heckantrieb	Benzin	351	477	Nov 2016	-	2024-03-01	124231
Renault	Fluence	1.6 16V	Stufenheck	Frontantrieb	Benzin	78	106	Feb 2010	-	2024-03-01	124234
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	120	163	Nov 2014	-	2024-03-01	124237
Piaggio	Ape	0.2	Pritsche/Fahrgestell	Heckantrieb	Gemisch	8	11	Jan 2012	-	2024-03-01	124238
VW	Golf vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Nov 2016	Aug 2020	2024-03-01	124239
VW	Golf vii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2020	2024-03-01	124240
VW	Golf vii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Nov 2016	Aug 2020	2024-03-01	124242
VW	Golf vii variant	1.6 TDI	Kombi	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2020	2024-03-01	124243
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	100	136	Dec 2014	Jul 2019	2025-02-03	124246
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	120	163	Feb 2015	Jul 2019	2025-02-03	124249
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	120	163	Apr 2015	-	2024-03-01	124251
Mini	Mini	Cooper SD All4	Kombi	Allrad	Diesel	120	163	Apr 2015	Jul 2019	2025-02-03	124252
Subaru	Svx	3.3 AWD	Coupe	Allrad	Benzin	171	233	Sep 1993	Dec 1995	2024-03-01	124255
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	120	163	Sep 2013	-	2024-03-01	124256
Mini	Mini	Cooper SD	Schrägheck	Frontantrieb	Diesel	120	163	Sep 2013	-	2024-03-01	124257
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	120	163	Nov 2014	-	2024-03-01	124267
Mini	Mini	Cooper SD	Cabriolet	Frontantrieb	Diesel	120	163	May 2015	Jul 2019	2025-02-03	124270
Nissan	Skyline	370gt	Stufenheck	Heckantrieb	Benzin	243	330	Dec 2008	Dec 2014	2024-03-01	124286
Renault	Twingo	0.9 TCE 110	Schrägheck	Heckantrieb	Benzin	80	109	Nov 2016	Apr 2019	2026-05-01	124320
Caterham	Seven	2	Cabriolet	Heckantrieb	Benzin	177	240	May 2015	-	2024-03-01	124358
Subaru	Impreza	1.6 I	Schrägheck	Frontantrieb	Benzin	85	115	Oct 2016	-	2024-03-01	124364
Subaru	Impreza	1.6 I AWD	Schrägheck	Allrad	Benzin	85	115	Oct 2016	-	2024-03-01	124365
Mini	Mini	Cooper SD All4	Coupe	Allrad	Diesel	100	136	Apr 2012	Sep 2016	2024-03-01	124370
Mini	Mini	Cooper S All4	Coupe	Allrad	Benzin	120	163	Mar 2012	Sep 2016	2024-03-01	124371
Mercedes-benz	C-Klasse	C 220 D	Cabriolet	Heckantrieb	Diesel	120	163	Jun 2016	May 2018	2024-03-01	124381
Suzuki	Sx4 / classic	1.5 Vvti	Schrägheck	Frontantrieb	Benzin	81	110	Jul 2007	Dec 2015	2024-03-01	124432
Honda	Integra	1.8	Stufenheck	Frontantrieb	Benzin	147	200	Sep 1993	Aug 2001	2024-03-01	124452
Mazda	Az1	0.7	Coupe	Heckantrieb	Benzin	47	64	Oct 1992	Nov 1994	2024-03-01	124525
Nissan	Teana ii	2.5 Four Allrad	Stufenheck	Allrad	Benzin	123	167	Jun 2008	Dec 2012	2024-03-01	124551
Hyundai	Xg	250	Stufenheck	Frontantrieb	Benzin	123	167	Oct 2003	Sep 2005	2024-03-01	124554
Toyota	Tercel	1.3	Stufenheck	Frontantrieb	Benzin	55	75	May 1982	Apr 1986	2024-03-01	124646
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	48	65	Nov 2008	Dec 2012	2025-12-01	124722
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	100	136	Mar 2011	Oct 2016	2024-03-01	124730
Renault	Megane iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	84	115	Nov 2015	-	2024-03-01	124736
Renault	Dokker	1.5 DCI	Kasten	Frontantrieb	Diesel	66	90	Dec 2013	-	2024-03-01	124738
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	145	197	Mar 2007	Dec 2011	2024-03-01	124739
Wiesmann	Mf3 roadster	3.2	Cabriolet	Heckantrieb	Benzin	239	325	May 2001	Aug 2003	2024-03-01	124747
Tazzari	Zero	EM1	Stufenheck	Heckantrieb	Elektro	15	20	Jun 2012	Dec 2016	2024-03-01	124748
Bentley	Bentayga	4.0 D	SUV	Allrad	Diesel	320	435	Jan 2017	-	2024-03-01	124751
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	120	163	Oct 2007	Jun 2015	2024-03-01	124760
BMW	3	325 I	Kombi	Heckantrieb	Benzin	155	211	Dec 2004	Dec 2010	2024-03-01	124763
BMW	3	320 CI	Coupe	Heckantrieb	Benzin	120	163	Jan 2000	May 2006	2024-03-01	124765
Ford USA	Thunderbird	4.6	Coupe	Heckantrieb	Benzin	153	208	Jan 1994	Dec 1997	2024-03-01	124766
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	100	136	Dec 2000	May 2006	2024-03-01	124771
Ford	Mondeo v	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	92	125	Feb 2015	Mar 2022	2026-04-01	124773
BMW	3	330 D	Kombi	Heckantrieb	Diesel	155	211	Jun 2005	May 2012	2024-03-01	124776
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	155	211	Sep 2005	Dec 2011	2024-03-01	124777
Ford	Mondeo v	1.5 Ecoboost	Stufenheck	Frontantrieb	Benzin	118	160	Sep 2014	Mar 2022	2026-04-01	124779
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	110	150	Jun 2004	Feb 2007	2024-03-01	124781
Ford	Mondeo v	1.5 Tdci	Stufenheck	Frontantrieb	Diesel	88	120	Mar 2015	Mar 2022	2026-04-01	124783
Ford	Mondeo v	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	110	150	Sep 2014	Mar 2022	2026-04-01	124784
Ford	Mondeo v	2.0 Tdci 4X4	Stufenheck	Allrad	Diesel	110	150	Sep 2014	Mar 2022	2026-04-01	124786
Porsche	Panamera	3	Schrägheck	Heckantrieb	Benzin	243	330	May 2016	Dec 2020	2026-02-01	124806
Porsche	Panamera	3.0 4	Schrägheck	Allrad	Benzin	243	330	May 2016	Dec 2020	2026-02-01	124807
Fiat	Ducato	1.8	Kasten	Frontantrieb	Benzin	51	69	Jul 1982	Dec 1988	2024-03-01	124817
Mercedes-benz	E-Klasse	E 220 D	Coupe	Heckantrieb	Diesel	143	194	Dec 2016	-	2024-03-01	124818
Mercedes-benz	E-Klasse	E 200	Coupe	Heckantrieb	Benzin	135	184	Dec 2016	-	2024-03-01	124820
Mercedes-benz	E-Klasse	E 300	Coupe	Heckantrieb	Benzin	180	245	Dec 2016	-	2024-03-01	124821
Mercedes-benz	E-Klasse	E 400 4-matic	Coupe	Allrad	Benzin	245	333	Dec 2016	-	2024-03-01	124822
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	100	136	Nov 2016	-	2024-03-01	124833
Hyundai	I30	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	88	120	Nov 2016	-	2024-03-01	124834
Hyundai	I30	1.4 T-gdi	Schrägheck	Frontantrieb	Benzin	103	140	Nov 2016	Dec 2020	2024-07-01	124836
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	70	95	Nov 2016	-	2024-03-01	124837
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	81	110	Nov 2016	-	2024-03-01	124839
Chrysler	Sebring	2.7 Flexfuel	Cabriolet	Frontantrieb	Benzin/Ethanol	137	186	May 2007	Sep 2010	2024-03-01	124849
Audi	A4 allroad b9	2.0 TDI Quattro	Kombi	Allrad	Diesel	100	136	Nov 2016	Jul 2018	2024-03-01	124858
Audi	A4 allroad b9	2.0 TDI Quattro	Kombi	Allrad	Diesel	110	150	Nov 2016	Oct 2019	2024-03-01	124859
Seat	Leon	1.6 TDI	Coupe	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2018	2024-03-01	124860
Chrysler	Neon	2.0 16V R/T	Stufenheck	Frontantrieb	Benzin	112	152	Oct 2001	Dec 2004	2024-03-01	124862
Renault	Fluence	1.6 LPG 16V	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	81	110	Jan 2012	-	2024-03-01	124864
Renault	Megane ii grandtour	1.6 LPG 16V	Kombi	Frontantrieb	Benzin/Autogas (LPG)	82	112	Jan 2006	Aug 2009	2024-03-01	124865
Renault	Clio iv	0.9 TCE 90	Kasten/Schrägheck	Frontantrieb	Benzin	66	90	Jan 2014	Aug 2021	2026-05-01	124871
Renault	Clio iv	1.2 16V	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Jan 2014	Aug 2021	2026-05-01	124872
Renault	Clio iv	1.5 DCI 75	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Jan 2014	Aug 2021	2026-05-01	124874
Renault	Clio iv	1.5 DCI 90	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Jan 2014	Aug 2021	2026-05-01	124875
Renault	Latitude	2.0 DCI 130	Stufenheck	Frontantrieb	Diesel	96	131	Dec 2013	-	2024-03-01	124878
Dacia	Logan	1.6	Kombi	Frontantrieb	Benzin	62	84	Jun 2013	-	2024-03-01	124913
Dacia	Logan	TCE 90 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Sep 2015	-	2024-03-01	124914
Dacia	Sandero	1.6 Hi-flex	Schrägheck	Frontantrieb	Benzin/Ethanol	64	87	Jun 2008	Dec 2012	2024-03-01	124918
Audi	A5	1.4 Tfsi	Coupe	Frontantrieb	Benzin	110	150	Nov 2016	Feb 2020	2024-03-01	124925
Audi	A5	1.4 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2017	Feb 2020	2024-03-01	124926
Peugeot	5008	1.2 THP	Großraumlimousine	Frontantrieb	Benzin	96	131	Dec 2016	-	2024-08-01	124945
Peugeot	5008	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	73	99	Dec 2016	-	2024-03-01	124949
Peugeot	5008	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	88	120	Dec 2016	Nov 2019	2025-02-03	124950
Peugeot	5008	1.6 THP 165	Großraumlimousine	Frontantrieb	Benzin	121	165	Dec 2016	-	2024-03-01	124951


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 **34 个 Ktype 映射**：复用跨批次已有尺寸组 4 个，首次创建尺寸组 9 个。
* 新建的 Volkswagen、Renault、Ford、Mercedes-Benz、Hyundai 和 Peugeot 尺寸组均已取得明确长宽高；相关页面将车身宽度与含后视镜宽度分列时，采用前者。([汽车数据][1])
* Audi A5 Sportback 使用 Audi 官方技术资料，其中明确标注 `width excluding mirrors` 为 1843 mm。
* MINI F54/F56、Audi A5 Coupe F5 和 SEAT Leon SC 直接复用题目提供的既有尺寸组，不重复输出尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：34
* PENDING 映射：66
* 当前映射引用的已确认尺寸组：13
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124225	124225	MPV	Golf VII Sportsvan facelift	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	MEDIUM	85 kW柴油版本对应改款Sportsvan五门外廓。	READY
124237	124237	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	MEDIUM	Clubman F54旅行车外廓。	READY
124239	124239	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
124240	124240	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
124242	124242	Wagon	Golf VII Variant facelift	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
124243	124243	Wagon	Golf VII Variant facelift	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
124246	124246	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	Clubman F54旅行车外廓。	READY
124249	124249	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	MEDIUM	Clubman F54旅行车外廓。	READY
124251	124251	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	ALL4不改变F54车身外廓。	READY
124252	124252	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	ALL4不改变F54车身外廓。	READY
124256	124256	Hatchback	MINI Hatch III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	MEDIUM	F56三门运动外廓。	READY
124257	124257	Hatchback	MINI Hatch III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	MEDIUM	Cooper SD与F56 Cooper S共用该外廓。	READY
124736	124736	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	非GT标准五门外廓。	READY
124773	124773	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124779	124779	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124783	124783	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124784	124784	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124786	124786	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	四驱不改变CD391四门车身外廓。	READY
124818	124818	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124820	124820	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124821	124821	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124822	124822	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH	4MATIC不改变C238标准车身外廓。	READY
124833	124833	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124834	124834	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124836	124836	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124837	124837	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124839	124839	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124860	124860	Hatchback	Leon III facelift	5F5	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	HIGH	Leon SC三门外廓。	READY
124925	124925	Coupe	A5 II	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
124926	124926	Hatchback	A5 II Sportback	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback五门快背外廓。	READY
124945	124945	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124949	124949	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124950	124950	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124951	124951	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613	Auto-Data.net Volkswagen Golf VII Sportsvan facelift 1.6 TDI SCR	https://www.auto-data.net/en/volkswagen-golf-vii-sportsvan-facelift-2017-1.6-tdi-scr-116hp-dsg-36070
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Auto-Data.net Volkswagen Golf VII 5-door facelift 1.6 TDI	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.6-tdi-115hp-27633
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515	Auto-Data.net Volkswagen Golf VII Variant facelift 1.6 TDI	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.6-tdi-115hp-27735
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Auto-Data.net Renault Megane IV 1.6 SCe	https://www.auto-data.net/en/renault-megane-iv-1.6-sce-115hp-22552
EU-FORD-MONDEO-V-CD391-SEDAN-01	4871	1852	1482	Auto-Data.net Ford Mondeo IV Sedan 1.5 EcoBoost	https://www.auto-data.net/en/ford-mondeo-iv-sedan-1.5-ecoboost-160hp-20356
EU-MERCEDES-BENZ-E-C238-COUPE-01	4826	1860	1430	Auto-Data.net Mercedes-Benz E-Class Coupe C238 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-200-184hp-9g-tronic-27317
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455	Auto-Data.net Hyundai i30 III 1.4 T-GDi	https://www.auto-data.net/en/hyundai-i30-iii-1.4-t-gdi-140hp-25965
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi MediaInfo A5 Sportback official technical data	https://press.audi.co.uk/assets/documents/original/16287-AudiUK00017563AudiA5andS5Sportback.pdf
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646	Auto-Data.net Peugeot 5008 II Phase I 1.6 BlueHDi	https://www.auto-data.net/en/peugeot-5008-ii-phase-i-2017-1.6-bluehdi-100hp-27386
```

## 下一步优先处理

1. 批量闭合 BMW E46、E87、E90、E91 等重复车身簇，并核对改款前后边界。
2. 处理 Dacia Logan/Sandero、Renault Fluence/Clio/Dokker 等可批量复用车型。
3. 单独解决 MINI R55/R57/R61、Land Rover Discovery V、Seat Ateca 等存在高度口径、版本功率或车身边界歧义的记录。
4. 最后处理 De Tomaso、Morgan、Caterham、Wiesmann、Tazzari、Piaggio Ape 等低重复历史或小众车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-golf-vii-sportsvan-facelift-2017-1.6-tdi-scr-116hp-dsg-36070 "Volkswagen Golf VII Sportsvan (facelift 2017) 1.6 TDI SCR (116 Hp) DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **27 行映射**，覆盖 **20 个此前 PENDING 的 Ktype**。
* BMW E46 Coupe、BMW E90/E91 与 Renault Fluence 的生产区间跨越外廓发生变化的改款节点，已拆为 `prefl`、`facelift` 派生行。([汽车数据][1])
* 首次闭合 11 个尺寸组；BMW E90/E91、Renault Twingo III、Renault Clio IV 直接复用已有尺寸组，不重复输出。BMW E46 Compact、E87、Dacia Logan/Sandero/Dokker 与 Megane II Grandtour 的三维及车身边界已闭合。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：54
* PENDING Ktype：46
* READY 映射行：61
* 当前批次已引用尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124173	124173	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-01	HIGH		READY
124212	124212	Hatchback	3 Series Compact E46	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-01	HIGH		READY
124234_prefl	124234	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124234_facelift	124234	Sedan	Fluence I facelift	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124320	124320	Hatchback	Twingo III		5	EU-RENAULT-TWINGO-III-HATCHBACK-01	HIGH		READY
124722	124722	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
124738	124738	Van	Dokker I		5	EU-DACIA-DOKKER-I-VAN-01	HIGH		READY
124763_prefl	124763	Wagon	3 Series Touring E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124763_facelift	124763	Wagon	3 Series Touring E91 facelift	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124765_prefl	124765	Coupe	3 Series Coupe E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124765_facelift	124765	Coupe	3 Series Coupe E46 facelift	E46	2	EU-BMW-3-E46-COUPE-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124771_prefl	124771	Coupe	3 Series Coupe E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124771_facelift	124771	Coupe	3 Series Coupe E46 facelift	E46	2	EU-BMW-3-E46-COUPE-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124776_prefl	124776	Wagon	3 Series Touring E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124776_facelift	124776	Wagon	3 Series Touring E91 facelift	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124777_prefl	124777	Sedan	3 Series Sedan E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124777_facelift	124777	Sedan	3 Series Sedan E90 facelift	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124781	124781	Hatchback	1 Series E87	E87	5	EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	HIGH		READY
124864_prefl	124864	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124864_facelift	124864	Sedan	Fluence I facelift	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124865	124865	Wagon	Megane II Grandtour Phase II	KM	5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-01	HIGH		READY
124871	124871	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124872	124872	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124874	124874	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124875	124875	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124914	124914	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-PREFL-01	HIGH		READY
124918	124918	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-LOGAN-I-MCV-FACELIFT-01	4473	1740	1640	Auto-Data.net Dacia Logan I MCV facelift 1.6 MPI LPG	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-mpi-8v-84hp-lpg-46172
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408	Auto-Data.net BMW 3 Series Compact E46 318ti	https://www.auto-data.net/en/bmw-3-series-compact-e46-318ti-143hp-9972
EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	4620	1809	1479	Auto-Data.net Renault Fluence 1.6 16V	https://www.auto-data.net/en/renault-fluence-1.6-16v-110hp-10656
EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	4622	1809	1479	Auto-Data.net Renault Fluence facelift 1.6 16V	https://www.auto-data.net/en/renault-fluence-facelift-2012-1.6-16v-110hp-18014
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534	Auto-Data.net Dacia Sandero I 1.5 dCi	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-86hp-46138
EU-DACIA-DOKKER-I-VAN-01	4363	1751	1809	Auto-Data.net Dacia Dokker Van 1.5 dCi	https://www.auto-data.net/en/dacia-dokker-van-1.5-dci-90hp-fap-18346
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370	Auto-Data.net BMW 3 Series Coupe E46 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-318ci-143hp-9996
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369	Auto-Data.net BMW 3 Series Coupe E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-facelift-2003-318ci-143hp-46092
EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	Auto-Data.net BMW 1 Series E87 120d	https://www.auto-data.net/en/bmw-1-series-hatchback-e87-120d-163hp-steptronic-21117
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-01	4500	1777	1467	Auto-Data.net Renault Megane II Grandtour Phase II 1.6 16V	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-30357
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4346	1733	1517	Auto-Data.net Dacia Logan II 0.9 TCe LPG	https://www.auto-data.net/en/dacia-logan-ii-0.9-tce-90hp-lpg-start-stop-23651
```

## 下一步优先处理

1. 闭合 MINI R55、R57、R61 的 Clubman、Convertible、Paceman 外廓边界。
2. 批量处理 Seat Ateca、Land Rover Discovery V、Audi A4 Allroad B9 与 Porsche Panamera。
3. 处理 Honda、Subaru、Mitsubishi、Nissan、Hyundai 等日系和韩系重复车身簇。
4. 最后处理 De Tomaso、Morgan、Caterham、Wiesmann、Tazzari、Piaggio Ape 等低重复车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-3-series-coupe-e46-318ci-143hp-9996 "BMW 3 Series Coupe (E46) 318Ci (143 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-3-series-compact-e46-318ti-143hp-9972 "BMW 3 Series Compact (E46) 318ti (143 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **17 个 READY Ktype 映射**，首次创建 **11 个尺寸组**。
* MINI R55 Clubman 与 R61 Paceman 分别按独立物理外廓建组；同组发动机与驱动版本直接复用。([汽车数据][1])
* Seat Ateca、Audi A4 Allroad、Porsche Panamera、Mercedes-Benz C-Class Cabriolet、BMW E87 LCI、Lexus LC、Bentley Bentayga 与 Subaru Impreza V 已闭合三维和车身边界。([汽车数据][2])
* Discovery V 的 2000 mm 不含后视镜车身宽度由 2017 年车型规格补齐；2073 mm 折叠后视镜宽度未作为 `WidthMM` 使用。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* PENDING Ktype：29
* READY 映射行：78
* 当前批次已引用尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124178	124178	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	MEDIUM		READY
124179	124179	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	MEDIUM		READY
124200	124200	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
124201	124201	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
124231	124231	Coupe	LC I		2	EU-LEXUS-LC-I-COUPE-01	HIGH		READY
124364	124364	Hatchback	Impreza V		5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	MEDIUM	前驱版本与同代五门车身共用外廓。	READY
124365	124365	Hatchback	Impreza V		5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	HIGH		READY
124370	124370	Coupe	Paceman	R61	3	EU-MINI-MINI-R61-PACEMAN-COUPE-01	MEDIUM	R61三门Paceman外廓。	READY
124371	124371	Coupe	Paceman	R61	3	EU-MINI-MINI-R61-PACEMAN-COUPE-01	MEDIUM	R61三门Paceman外廓。	READY
124381	124381	Convertible	C-Class Cabriolet	A205	2	EU-MERCEDES-BENZ-C-A205-CABRIOLET-01	MEDIUM		READY
124730	124730	Wagon	MINI Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-01	MEDIUM	R55 Clubman旅行车外廓。	READY
124739	124739	Hatchback	1 Series E87 facelift	E87	5	EU-BMW-1-E87-HATCHBACK-5D-FACELIFT-01	MEDIUM		READY
124751	124751	SUV	Bentayga I	4V	5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
124806	124806	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH		READY
124807	124807	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH	四驱不改变标准轴距971车身外廓。	READY
124858	124858	Wagon	A4 Allroad B9	8W	5	EU-AUDI-A4-B9-ALLROAD-WAGON-01	MEDIUM		READY
124859	124859	Wagon	A4 Allroad B9	8W	5	EU-AUDI-A4-B9-ALLROAD-WAGON-01	MEDIUM		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601	Auto-Data.net Seat Ateca I 2.0 TDI	https://www.auto-data.net/en/seat-ateca-i-2.0-tdi-150hp-start-stop-23119
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1888	Auto-Data.net Land Rover Discovery V 2.0 SD4;CarExpert 2017 Land Rover Discovery exterior dimensions	https://www.auto-data.net/en/land-rover-discovery-v-2.0-sd4-240hp-4wd-automatic-39109;https://www.carexpert.com.au/land-rover/discovery/2017/exterior-and-dimensions
EU-LEXUS-LC-I-COUPE-01	4760	1920	1345	Auto-Data.net Lexus LC 500 V8	https://www.auto-data.net/en/lexus-lc-500-v8-477hp-automatic-29883
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480	Auto-Data.net Subaru Impreza V Hatchback 1.6i	https://www.auto-data.net/en/subaru-impreza-v-hatchback-1.6i-114hp-awd-lineartronic-32129
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518	Auto-Data.net MINI Paceman R61 Cooper S ALL4	https://www.auto-data.net/en/mini-paceman-r61-cooper-s-1.6-190hp-all4-21654
EU-MERCEDES-BENZ-C-A205-CABRIOLET-01	4686	1810	1409	Auto-Data.net Mercedes-Benz C-Class Cabriolet A205 C 220d	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-c-220d-170hp-24247
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426	Auto-Data.net MINI Clubman R55 Cooper SD	https://www.auto-data.net/en/mini-clubman-r55-cooper-sd-2.0-143hp-21507
EU-BMW-1-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421	Auto-Data.net BMW 1 Series E87 LCI 120d	https://www.auto-data.net/en/bmw-1-series-hatchback-5dr-e87-lci-facelift-2007-120d-177hp-9813
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1722	Auto-Data.net Bentley Bentayga 4.0 diesel V8	https://www.auto-data.net/en/bentley-bentayga-4.0-diesel-v8-435hp-awd-automatic-27234
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423	Auto-Data.net Porsche Panamera G2 3.0 V6	https://www.auto-data.net/en/porsche-panamera-g2-3.0-v6-330hp-pdk-26984
EU-AUDI-A4-B9-ALLROAD-WAGON-01	4750	1842	1493	Auto-Data.net Audi A4 Allroad B9 2.0 TDI	https://www.auto-data.net/en/audi-a4-allroad-b9-8w-2.0-tdi-150hp-quattro-ultra-36295
```

## 下一步优先处理

1. 处理 Honda Crossroad、Mitsubishi Colt Ralliart、Lancer Evolution X、Subaru SVX 和 Nissan Skyline/Teana。
2. 闭合 MINI R57/F57 Cabriolet 的代际边界，避免将跨代 Ktype 错误合并。
3. 处理 Dacia 1100、Mazda 626/Tercel、Hyundai XG、Chrysler Neon/Sebring 等历史标准乘用车。
4. 最后处理 De Tomaso、Morgan、Caterham、Wiesmann、Tazzari、Piaggio Ape 与多轴距/多车顶 Fiat Ducato。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mini-clubman-r55-cooper-sd-2.0-143hp-21507 "Mini Clubman (R55) Cooper SD 2.0 (143 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/seat-ateca-i-2.0-tdi-150hp-start-stop-23119 "Seat Ateca I 2.0 TDI (150 Hp) Start/Stop | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/land-rover-discovery-v-2.0-sd4-240hp-4wd-automatic-39109 "Land Rover Discovery V 2.0 SD4 (240 Hp) 4WD Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增 **12 个 READY Ktype 映射**，首次创建 **12 个 DIMENSION_GROUP**。
* 已闭合 Honda Crossroad RT3、Maserati Quattroporte V M139、Mitsubishi Lancer Evolution X CZ4A、Subaru SVX CXW、Nissan Skyline KV36、Nissan Teana TNJ32 等车型的物理外廓。([本田][1])
* Hyundai XG、Ford Thunderbird、Chrysler Sebring、Renault Latitude 与 Dacia Logan II MCV 已按各自代际车身建组。([汽车目录][2])
* Mitsubishi Ktype `124205` 的输入 Model 代际标签与 `EVO X` 版本信息不一致，按明确的 Evolution X `CZ4A` 外廓映射。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* PENDING Ktype：17
* READY 映射行：90
* 当前批次已引用尺寸组：53
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124130	124130	SUV	Crossroad II	RT3	5	EU-HONDA-CROSSROAD-II-RT3-SUV-01	HIGH	2.0前驱版本对应RT3车身。	READY
124175	124175	Sedan	Quattroporte V	M139	4	EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-01	HIGH		READY
124205	124205	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	MEDIUM	输入Model代际标签与EVO X版本不一致，按CZ4A物理外廓映射。	READY
124255	124255	Coupe	SVX	CXW	2	EU-SUBARU-SVX-CXW-COUPE-01	HIGH		READY
124286	124286	Sedan	Skyline XII	KV36	4	EU-NISSAN-SKYLINE-XII-KV36-SEDAN-01	HIGH	370GT后驱轿车对应KV36。	READY
124525	124525	Coupe	AZ-1	PG6SA	2	EU-MAZDA-AZ1-PG6SA-COUPE-01	HIGH		READY
124551	124551	Sedan	Teana II	TNJ32	4	EU-NISSAN-TEANA-II-TNJ32-SEDAN-01	HIGH	四驱版本对应TNJ32车身。	READY
124554	124554	Sedan	XG facelift	XG	4	EU-HYUNDAI-XG-FACELIFT-SEDAN-01	HIGH		READY
124766	124766	Coupe	Thunderbird X	MN12	2	EU-FORD-THUNDERBIRD-X-MN12-COUPE-01	HIGH		READY
124849	124849	Convertible	Sebring II	JS	2	EU-CHRYSLER-SEBRING-JS-CONVERTIBLE-01	HIGH		READY
124878	124878	Sedan	Latitude	X43	4	EU-RENAULT-LATITUDE-X43-SEDAN-01	HIGH		READY
124913	124913	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CROSSROAD-II-RT3-SUV-01	4285	1755	1670	Honda Crossroad official Fact Book	https://www.honda.co.jp/factbook/auto/CROSSROAD/200702/15.html
EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-01	5097	1885	1438	Auto-Data.net Maserati Quattroporte V 4.2 V8	https://www.auto-data.net/en/maserati-quattroporte-v-4.2-i-v8-32v-400hp-10899
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	4505	1810	1480	Auto-Data.net Mitsubishi Lancer Evolution X 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-lancer-evolution-x-2.0-mivec-295hp-s-awc-15647
EU-SUBARU-SVX-CXW-COUPE-01	4625	1777	1300	Auto-Data.net Subaru SVX CXW 3.3 AWD	https://www.auto-data.net/en/subaru-svx-cx-3.3-i-24v-4wd-cxw-230hp-16203
EU-NISSAN-SKYLINE-XII-KV36-SEDAN-01	4755	1770	1450	Automobile-Catalog Nissan Skyline 370GT Type S;Goo-net Exchange Nissan Skyline 370GT Type S	https://www.automobile-catalog.com/car/2008/2138870/nissan_skyline_370gt_type_s.html;https://www.goo-net-exchange.com/catalog/NISSAN__SKYLINE/10052348/
EU-MAZDA-AZ1-PG6SA-COUPE-01	3295	1395	1150	Auto-Data.net Mazda AZ-1	https://www.auto-data.net/en/mazda-az-1-generation-2423
EU-NISSAN-TEANA-II-TNJ32-SEDAN-01	4850	1795	1500	Automobile-Catalog Nissan Teana 250XL Four;Onteco Nissan Teana 250XL Four	https://www.automobile-catalog.com/car/2013/2282780/nissan_teana_250xl_four.html;https://ontecojp.com/catalog/nissan/teana/10057024
EU-HYUNDAI-XG-FACELIFT-SEDAN-01	4875	1825	1420	Auto-Data.net Hyundai Grandeur III XG facelift 2.5 V6	https://www.auto-data.net/en/hyundai-grandeur-iii-xg-facelift-2003-2.5i-v6-172hp-automatic-30676
EU-FORD-THUNDERBIRD-X-MN12-COUPE-01	5088	1847	1333	Auto-Data.net Ford Thunderbird 4.6 V8	https://www.auto-data.net/en/ford-thunderbird-super-birds-4.6i-v8-208hp-8098
EU-CHRYSLER-SEBRING-JS-CONVERTIBLE-01	4930	1843	1500	Auto-Data.net Chrysler Sebring Convertible JS	https://www.auto-data.net/en/chrysler-sebring-convertible-js-generation-3270
EU-RENAULT-LATITUDE-X43-SEDAN-01	4897	1832	1483	Auto-Data.net Renault Latitude	https://www.auto-data.net/en/renault-latitude-generation-3771
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1539	Auto-Data.net Dacia Logan II MCV	https://www.auto-data.net/en/dacia-logan-ii-mcv-0.9-tce-90hp-18337
```

## 下一步优先处理

1. 闭合 MINI R57 与 F57 Cabriolet 的代际边界，处理 `124267`、`124270`、`124760`。
2. 处理 Dacia 1100、Mazda 626 Coupe、Mitsubishi Colt Ralliart、Suzuki SX4、Honda Integra、Toyota Tercel 和 Chrysler Neon。
3. 处理 De Tomaso、Morgan、Caterham、Wiesmann、Tazzari 与 Piaggio Ape 等低重复车型。
4. 最后解决 Fiat Ducato 多轴距、多车顶物理分支。

推进信号：CONTINUE

[1]: https://www.honda.co.jp/factbook/auto/CROSSROAD/200702/15.html "CROSSROAD"
[2]: https://www.automobile-catalog.com/car/2005/1177265/hyundai_xg250.html?utm_source=chatgpt.com "2005 Hyundai XG250 (aut. 4) (model up to mid-year ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮新增 **12 个 READY Ktype、14 行映射**，首次创建 **13 个尺寸组**。
* MINI `124267`、`124270` 已关联 F57 敞篷外廓；`124760` 的时间范围覆盖 R57 改款前后，按长度变化拆为两条派生映射。([汽车数据][1])
* Honda Integra `124452` 的 147 kW 版本确认对应 DB8 四门 Type R，并按前后期高度 1355/1365 mm 拆组。([トヨタの中古車【トヨタ公式 GAZOO中古車サイト】][2])
* Toyota Tercel `124646` 使用 Toyota 官方 AL20 四门轿车规格闭合。([丰田官方网站][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* PENDING Ktype：5
* READY 映射行：104
* 当前批次已引用尺寸组：66
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124153	124153	Sedan	Dacia 1100		4	EU-DACIA-1100-SEDAN-01	MEDIUM	输入开始月份早于资料所载量产年份，物理外廓对应Dacia 1100四门轿车。	READY
124181	124181	Coupe	626 I	CB2	2	EU-MAZDA-626-I-CB2-COUPE-01	HIGH		READY
124197	124197	Hatchback	Colt VI	Z30	5	EU-MITSUBISHI-COLT-VI-Z30-RALLIART-HATCHBACK-01	MEDIUM	180 PS Ralliart版本对应Z30五门宽体外廓。	READY
124209	124209	Convertible	4/4 Sigma		2	EU-MORGAN-4-4-SIGMA-CONVERTIBLE-01	HIGH		READY
124267	124267	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-01	MEDIUM	输入功率与常见F57铭牌功率存在差异，Ktype车身边界对应F57。	READY
124270	124270	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-01	MEDIUM	输入功率与常见F57铭牌功率存在差异，Ktype车身边界对应F57。	READY
124452_prefl	124452	Sedan	Integra III	DB8	4	EU-HONDA-INTEGRA-III-DB8-SEDAN-PREFL-01	MEDIUM	147 kW版本对应DB8 Type R；生产区间覆盖前期外廓。	READY
124452_facelift	124452	Sedan	Integra III facelift	DB8	4	EU-HONDA-INTEGRA-III-DB8-SEDAN-FACELIFT-01	MEDIUM	147 kW版本对应DB8 Type R；生产区间覆盖后期外廓。	READY
124646	124646	Sedan	Tercel II	AL20	4	EU-TOYOTA-TERCEL-II-AL20-SEDAN-01	HIGH		READY
124747	124747	Convertible	MF3		2	EU-WIESMANN-MF3-ROADSTER-01	MEDIUM		READY
124748	124748	Hatchback	Zero		2	EU-TAZZARI-ZERO-HATCHBACK-01	MEDIUM	输入BodyStyle为Stufenheck，按资料确认的两门掀背外廓归类。	READY
124760_prefl	124760	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	HIGH	生产区间覆盖改款前Cooper S外廓。	READY
124760_facelift	124760	Convertible	MINI Convertible R57 facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH	生产区间覆盖改款后Cooper S外廓。	READY
124862	124862	Sedan	Neon II	PL	4	EU-CHRYSLER-NEON-II-PL-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-1100-SEDAN-01	3990	1490	1410	Auto-Data.net Dacia 1100 1.1	https://www.auto-data.net/en/dacia-1100-1.1-46hp-55751
EU-MAZDA-626-I-CB2-COUPE-01	4420	1690	1370	UltimateSpecs Mazda 626 I HardTop 2.0	https://www.ultimatespecs.com/car-specs/Mazda/7529/Mazda-626-I-HardTop-20.html
EU-MITSUBISHI-COLT-VI-Z30-RALLIART-HATCHBACK-01	3925	1695	1535	Onteco Mitsubishi Colt Ralliart Version R	https://ontecojp.com/catalog/mitsubishi/colt/10060047
EU-MORGAN-4-4-SIGMA-CONVERTIBLE-01	4010	1630	1220	Automobile-Catalog 2009 Morgan 4/4 Sport	https://www.automobile-catalog.com/car/2009/2039345/morgan_44_sport.html
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415	Auto-Data.net MINI Convertible F57 Cooper S	https://www.auto-data.net/en/mini-convertible-f57-cooper-s-2.0-192hp-22760
EU-HONDA-INTEGRA-III-DB8-SEDAN-PREFL-01	4525	1695	1355	GAZOO Honda Integra Type R E-DB8	https://gazoo.com/catalog/maker/HONDA/INTEGRA/199305/2001618/
EU-HONDA-INTEGRA-III-DB8-SEDAN-FACELIFT-01	4525	1695	1365	GAZOO Honda Integra Type R E-DB8	https://gazoo.com/catalog/maker/HONDA/INTEGRA/199305/2001346/
EU-TOYOTA-TERCEL-II-AL20-SEDAN-01	3910	1615	1385	Toyota 75 Years Vehicle Lineage Tercel and Corsa	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60010722B/index.html
EU-WIESMANN-MF3-ROADSTER-01	3860	1750	1160	UltimateSpecs Wiesmann Roadster MF3	https://www.ultimatespecs.com/car-specs/Wiesmann/30217/Wiesmann-Roadster-MF-3.html
EU-TAZZARI-ZERO-HATCHBACK-01	2880	1560	1425	Automobile Propre Tazzari Zero specifications	https://www.automobile-propre.com/voitures/tazzari-zero/
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414	Auto-Data.net MINI Convertible R57 Cooper S	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6-175hp-21563
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414	Auto-Data.net MINI Convertible R57 facelift Cooper S	https://www.auto-data.net/en/mini-convertible-r57-facelift-2011-cooper-s-1.6-184hp-automatic-21571
EU-CHRYSLER-NEON-II-PL-SEDAN-01	4390	1715	1421	Auto-Data.net Chrysler Neon II	https://www.auto-data.net/en/chrysler-neon-ii-generation-3260
```

## 下一步优先处理

1. `124160` De Tomaso Deauville：解决不同年份资料中车长 4851、4890、4925 mm 的冲突。
2. `124238` Piaggio Ape：确认 218 cc 汽油版平板车与底盘车是否属于同一完整外廓。
3. `124358` Caterham Seven：确认 177 kW 版本对应标准 485、宽体底盘还是 CSR 分支。
4. `124432` Suzuki SX4：确认过长生产区间是否覆盖前后期不同保险杠和车身尺寸。
5. `124817` Fiat Ducato：拆清第一代两种轴距、两种车顶高度中的实际 Ktype 覆盖范围。Fiat 官方历史资料确认该代确有两轴距和两种车顶，当前不能合并为单组。([Stellantis Media][4])

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mini-convertible-f57-cooper-s-2.0-192hp-22760?utm_source=chatgpt.com "Mini Convertible (F57) Cooper S 2.0 (192 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://gazoo.com/catalog/maker/HONDA/INTEGRA/199305/2001618/?utm_source=chatgpt.com "インテグラ(1995年10月～1996年9月) タイプＲ| トヨタ自動車のクルマ情報サイト‐GAZOO"
[3]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60010722B/index.html?utm_source=chatgpt.com "75 Years of TOYOTA | Vehicle Lineage"
[4]: https://www.media.stellantis.com/em-en/fiat-professional/press/the-legendary-ducato-was-born-on-october-23-1981?utm_source=chatgpt.com "The legendary Ducato was born on October 23, 1981 | FIAT Professional | Stellantis Media"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* De Tomaso Deauville 已按输入的 198 kW 德国市场版本闭合为 4886 × 1878 × 1368 mm，宽度明确不含后视镜。([汽车目录][1])
* Piaggio Ape TM 已依据官方手册拆分标准货台、长货台、汽油倾卸货台以及手把式/方向盘式裸底盘五种物理外廓；手册同时确认该汽油版本排量为 217.9 cm³。
* Caterham Seven 485 已确认同时覆盖 S3 标准车身和 SV 宽体车身；尺寸采用 Caterham 官方手册对应的标准 S3 与宽体 S5/SV 外廓。([caterham-sv.com][2])
* Suzuki SX4 1.5 前驱五门车身已按 2012 年 6 月外廓变化拆分为改款前 4135 mm 和改款后 4150 mm 两组，宽度均明确不含后视镜。([汽车目录][3])
* 当前仅剩 Fiat Ducato I Ktype `124817` 未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：114
* PENDING 映射行：1
* 当前批次已确认并引用尺寸组：76
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124160	124160	Sedan	Deauville		4	EU-DE-TOMASO-DEAUVILLE-SEDAN-01	HIGH		READY
124238_normaldeck	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-NORMAL-DECK-01	HIGH	标准货台外廓。	READY
124238_longdeck	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONG-DECK-01	HIGH	长货台外廓。	READY
124238_tipper	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-TIPPER-01	HIGH	汽油倾卸货台外廓。	READY
124238_chassis_handlebar	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-HANDLEBAR-01	MEDIUM	手把式裸底盘外廓。	READY
124238_chassis_steering	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-STEERING-01	MEDIUM	方向盘式裸底盘外廓。	READY
124358_s3	124358	Convertible	Seven 485	S3	2	EU-CATERHAM-SEVEN-485-CONVERTIBLE-S3-01	HIGH	S3标准车身。	READY
124358_sv	124358	Convertible	Seven 485	SV	2	EU-CATERHAM-SEVEN-485-CONVERTIBLE-SV-01	HIGH	SV宽体车身。	READY
124432_prefl	124432	Hatchback	SX4 I	YA11S	5	EU-SUZUKI-SX4-I-HATCHBACK-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124432_facelift	124432	Hatchback	SX4 I facelift	YA11S	5	EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124817	124817	Van	Ducato I	280			LOW	候选覆盖SWB/LWB及低顶/高顶；LWB低顶尚缺同一配置的直接三维来源。	PENDING: LWB低顶缺少可追溯的同配置三维来源
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DE-TOMASO-DEAUVILLE-SEDAN-01	4886	1878	1368	Automobile-Catalog 1974 De Tomaso Deauville	https://www.automobile-catalog.com/car/1974/58400/de_tomaso_deauville.html
EU-PIAGGIO-APE-TM-PICKUP-NORMAL-DECK-01	3175	1480	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-LONG-DECK-01	3390	1500	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-TIPPER-01	3225	1500	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-HANDLEBAR-01	3150	1455	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-STEERING-01	3210	1455	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-CATERHAM-SEVEN-485-CONVERTIBLE-S3-01	3100	1575	1115	Caterham Seven 485 price and specification list;Caterham Seven official owners handbook	https://www.caterham-sv.com/wp-content/uploads/2022/03/485-Price-Specification_RRP_A4_V3.3.pdf;https://caterhamcars.com/assets/Documents/Owner-Downloads/Owners-Handbook-All-Models_2023_ED1.2.pdf
EU-CATERHAM-SEVEN-485-CONVERTIBLE-SV-01	3300	1685	1140	Caterham Seven 485 price and specification list;Caterham Seven official owners handbook	https://www.caterham-sv.com/wp-content/uploads/2022/03/485-Price-Specification_RRP_A4_V3.3.pdf;https://caterhamcars.com/assets/Documents/Owner-Downloads/Owners-Handbook-All-Models_2023_ED1.2.pdf
EU-SUZUKI-SX4-I-HATCHBACK-PREFL-01	4135	1755	1605	Automobile-Catalog 2007 Suzuki SX4 1.5XG 2WD	https://www.automobile-catalog.com/car/2007/3408440/suzuki_sx4_1_5xg_2wd.html
EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	4150	1755	1605	Automobile-Catalog 2012 Suzuki SX4 1.5XG 2WD	https://www.automobile-catalog.com/car/2012/3408770/suzuki_sx4_1_5xg_2wd.html
```

## 下一步优先处理

1. 仅处理 Fiat Ducato I Typ 280 的 LWB 低顶直接规格来源。
2. 闭合 `124817` 的 SWB/LWB、低顶/高顶全部物理分支后，立即执行一次机械检查并输出最终两张完整 TSV 与指定下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1974/58400/de_tomaso_deauville.html?utm_source=chatgpt.com "1974 de Tomaso Deauville Specs Review (198.5 kW / 270 PS / 266 hp) (since mid-year 1974 for Europe Germany)"
[2]: https://www.caterham-sv.com/wp-content/uploads/2022/03/485-Price-Specification_RRP_A4_V3.3.pdf?utm_source=chatgpt.com "485 | RRP PRICE & SPECIFICATIONS LIST"
[3]: https://www.automobile-catalog.com/car/2007/3408440/suzuki_sx4_1_5xg_2wd.html?utm_source=chatgpt.com "2007 Suzuki SX4 1.5XG 2WD Specs Review (81 kW / 110 PS / 109 hp) (for Japan )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后一个 Ktype `124817` 已闭合：Fiat Ducato I Typ 280 的 1.8 汽油 Kasten 对应标准短轴低顶厢式车外廓，尺寸采用同平台 Peugeot J5 1.8 69 hp 的对应规格，并以发动机应用资料确认版本边界。([Truck1][1])
* 已完成一次机械收尾检查：表头及列数正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，全部映射引用闭合，尺寸及来源字段完整。
* 当前批次达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：115
* PENDING 映射：0
* DIMENSION_GROUP：77
* 孤立尺寸组：0
* 未闭合映射引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124130	124130	SUV	Crossroad II	RT3	5	EU-HONDA-CROSSROAD-II-RT3-SUV-01	HIGH	2.0前驱版本对应RT3车身。	READY
124153	124153	Sedan	Dacia 1100		4	EU-DACIA-1100-SEDAN-01	MEDIUM	输入开始月份早于资料所载量产年份，物理外廓对应Dacia 1100四门轿车。	READY
124160	124160	Sedan	Deauville		4	EU-DE-TOMASO-DEAUVILLE-SEDAN-01	HIGH		READY
124173	124173	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-01	HIGH		READY
124175	124175	Sedan	Quattroporte V	M139	4	EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-01	HIGH		READY
124178	124178	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	MEDIUM		READY
124179	124179	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	MEDIUM		READY
124181	124181	Coupe	626 I	CB2	2	EU-MAZDA-626-I-CB2-COUPE-01	HIGH		READY
124197	124197	Hatchback	Colt VI	Z30	5	EU-MITSUBISHI-COLT-VI-Z30-RALLIART-HATCHBACK-01	MEDIUM	180 PS Ralliart版本对应Z30五门宽体外廓。	READY
124200	124200	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
124201	124201	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
124205	124205	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	MEDIUM	输入Model代际标签与EVO X版本不一致，按CZ4A物理外廓映射。	READY
124209	124209	Convertible	4/4 Sigma		2	EU-MORGAN-4-4-SIGMA-CONVERTIBLE-01	HIGH		READY
124212	124212	Hatchback	3 Series Compact E46	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-01	HIGH		READY
124225	124225	MPV	Golf VII Sportsvan facelift	AM1	5	EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	MEDIUM	85 kW柴油版本对应改款Sportsvan五门外廓。	READY
124231	124231	Coupe	LC I		2	EU-LEXUS-LC-I-COUPE-01	HIGH		READY
124234_prefl	124234	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124234_facelift	124234	Sedan	Fluence I facelift	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124237	124237	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	MEDIUM	Clubman F54旅行车外廓。	READY
124238_normaldeck	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-NORMAL-DECK-01	HIGH	标准货台外廓。	READY
124238_longdeck	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-LONG-DECK-01	HIGH	长货台外廓。	READY
124238_tipper	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-PICKUP-TIPPER-01	HIGH	汽油倾卸货台外廓。	READY
124238_chassis_handlebar	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-HANDLEBAR-01	MEDIUM	手把式裸底盘外廓。	READY
124238_chassis_steering	124238	Pickup	Ape TM		2	EU-PIAGGIO-APE-TM-CHASSIS-STEERING-01	MEDIUM	方向盘式裸底盘外廓。	READY
124239	124239	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
124240	124240	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
124242	124242	Wagon	Golf VII Variant facelift	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
124243	124243	Wagon	Golf VII Variant facelift	BA5	5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
124246	124246	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	Clubman F54旅行车外廓。	READY
124249	124249	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	MEDIUM	Clubman F54旅行车外廓。	READY
124251	124251	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	ALL4不改变F54车身外廓。	READY
124252	124252	Wagon	MINI Clubman II	F54	5	EU-MINI-MINI-F54-WAGON-01	HIGH	ALL4不改变F54车身外廓。	READY
124255	124255	Coupe	SVX	CXW	2	EU-SUBARU-SVX-CXW-COUPE-01	HIGH		READY
124256	124256	Hatchback	MINI Hatch III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	MEDIUM	F56三门运动外廓。	READY
124257	124257	Hatchback	MINI Hatch III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	MEDIUM	Cooper SD与F56 Cooper S共用该外廓。	READY
124267	124267	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-01	MEDIUM	输入功率与常见F57铭牌功率存在差异，Ktype车身边界对应F57。	READY
124270	124270	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-01	MEDIUM	输入功率与常见F57铭牌功率存在差异，Ktype车身边界对应F57。	READY
124286	124286	Sedan	Skyline XII	KV36	4	EU-NISSAN-SKYLINE-XII-KV36-SEDAN-01	HIGH	370GT后驱轿车对应KV36。	READY
124320	124320	Hatchback	Twingo III		5	EU-RENAULT-TWINGO-III-HATCHBACK-01	HIGH		READY
124358_s3	124358	Convertible	Seven 485	S3	2	EU-CATERHAM-SEVEN-485-CONVERTIBLE-S3-01	HIGH	S3标准车身。	READY
124358_sv	124358	Convertible	Seven 485	SV	2	EU-CATERHAM-SEVEN-485-CONVERTIBLE-SV-01	HIGH	SV宽体车身。	READY
124364	124364	Hatchback	Impreza V		5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	MEDIUM	前驱版本与同代五门车身共用外廓。	READY
124365	124365	Hatchback	Impreza V		5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	HIGH		READY
124370	124370	Coupe	Paceman	R61	3	EU-MINI-MINI-R61-PACEMAN-COUPE-01	MEDIUM	R61三门Paceman外廓。	READY
124371	124371	Coupe	Paceman	R61	3	EU-MINI-MINI-R61-PACEMAN-COUPE-01	MEDIUM	R61三门Paceman外廓。	READY
124381	124381	Convertible	C-Class Cabriolet	A205	2	EU-MERCEDES-BENZ-C-A205-CABRIOLET-01	MEDIUM		READY
124432_prefl	124432	Hatchback	SX4 I	YA11S	5	EU-SUZUKI-SX4-I-HATCHBACK-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124432_facelift	124432	Hatchback	SX4 I facelift	YA11S	5	EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124452_prefl	124452	Sedan	Integra III	DB8	4	EU-HONDA-INTEGRA-III-DB8-SEDAN-PREFL-01	MEDIUM	147 kW版本对应DB8 Type R；生产区间覆盖前期外廓。	READY
124452_facelift	124452	Sedan	Integra III facelift	DB8	4	EU-HONDA-INTEGRA-III-DB8-SEDAN-FACELIFT-01	MEDIUM	147 kW版本对应DB8 Type R；生产区间覆盖后期外廓。	READY
124525	124525	Coupe	AZ-1	PG6SA	2	EU-MAZDA-AZ1-PG6SA-COUPE-01	HIGH		READY
124551	124551	Sedan	Teana II	TNJ32	4	EU-NISSAN-TEANA-II-TNJ32-SEDAN-01	HIGH	四驱版本对应TNJ32车身。	READY
124554	124554	Sedan	XG facelift	XG	4	EU-HYUNDAI-XG-FACELIFT-SEDAN-01	HIGH		READY
124646	124646	Sedan	Tercel II	AL20	4	EU-TOYOTA-TERCEL-II-AL20-SEDAN-01	HIGH		READY
124722	124722	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
124730	124730	Wagon	MINI Clubman	R55	5	EU-MINI-MINI-R55-CLUBMAN-WAGON-01	MEDIUM	R55 Clubman旅行车外廓。	READY
124736	124736	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	非GT标准五门外廓。	READY
124738	124738	Van	Dokker I		5	EU-DACIA-DOKKER-I-VAN-01	HIGH		READY
124739	124739	Hatchback	1 Series E87 facelift	E87	5	EU-BMW-1-E87-HATCHBACK-5D-FACELIFT-01	MEDIUM		READY
124747	124747	Convertible	MF3		2	EU-WIESMANN-MF3-ROADSTER-01	MEDIUM		READY
124748	124748	Hatchback	Zero		2	EU-TAZZARI-ZERO-HATCHBACK-01	MEDIUM	输入BodyStyle为Stufenheck，按资料确认的两门掀背外廓归类。	READY
124751	124751	SUV	Bentayga I	4V	5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
124760_prefl	124760	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	HIGH	生产区间覆盖改款前Cooper S外廓。	READY
124760_facelift	124760	Convertible	MINI Convertible R57 facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH	生产区间覆盖改款后Cooper S外廓。	READY
124763_prefl	124763	Wagon	3 Series Touring E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124763_facelift	124763	Wagon	3 Series Touring E91 facelift	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124765_prefl	124765	Coupe	3 Series Coupe E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124765_facelift	124765	Coupe	3 Series Coupe E46 facelift	E46	2	EU-BMW-3-E46-COUPE-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124766	124766	Coupe	Thunderbird X	MN12	2	EU-FORD-THUNDERBIRD-X-MN12-COUPE-01	HIGH		READY
124771_prefl	124771	Coupe	3 Series Coupe E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124771_facelift	124771	Coupe	3 Series Coupe E46 facelift	E46	2	EU-BMW-3-E46-COUPE-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124773	124773	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124776_prefl	124776	Wagon	3 Series Touring E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124776_facelift	124776	Wagon	3 Series Touring E91 facelift	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124777_prefl	124777	Sedan	3 Series Sedan E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	生产区间覆盖改款前外廓。	READY
124777_facelift	124777	Sedan	3 Series Sedan E90 facelift	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
124779	124779	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124781	124781	Hatchback	1 Series E87	E87	5	EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	HIGH		READY
124783	124783	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124784	124784	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	欧洲Mondeo V四门轿车外廓。	READY
124786	124786	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-01	HIGH	四驱不改变CD391四门车身外廓。	READY
124806	124806	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH		READY
124807	124807	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH	四驱不改变标准轴距971车身外廓。	READY
124817	124817	Van	Ducato I	280	4	EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	HIGH	1.8汽油Kasten对应标准短轴低顶厢式车外廓。	READY
124818	124818	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124820	124820	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124821	124821	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH		READY
124822	124822	Coupe	E-Class Coupe	C238	2	EU-MERCEDES-BENZ-E-C238-COUPE-01	HIGH	4MATIC不改变C238标准车身外廓。	READY
124833	124833	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124834	124834	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124836	124836	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124837	124837	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124839	124839	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
124849	124849	Convertible	Sebring II	JS	2	EU-CHRYSLER-SEBRING-JS-CONVERTIBLE-01	HIGH		READY
124858	124858	Wagon	A4 Allroad B9	8W	5	EU-AUDI-A4-B9-ALLROAD-WAGON-01	MEDIUM		READY
124859	124859	Wagon	A4 Allroad B9	8W	5	EU-AUDI-A4-B9-ALLROAD-WAGON-01	MEDIUM		READY
124860	124860	Hatchback	Leon III facelift	5F5	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	HIGH	Leon SC三门外廓。	READY
124862	124862	Sedan	Neon II	PL	4	EU-CHRYSLER-NEON-II-PL-SEDAN-01	HIGH		READY
124864_prefl	124864	Sedan	Fluence I	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前外廓。	READY
124864_facelift	124864	Sedan	Fluence I facelift	L30	4	EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后外廓。	READY
124865	124865	Wagon	Megane II Grandtour Phase II	KM	5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-01	HIGH		READY
124871	124871	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124872	124872	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124874	124874	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124875	124875	Van	Clio IV		5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	MEDIUM	货运改装保留五门掀背车外廓。	READY
124878	124878	Sedan	Latitude	X43	4	EU-RENAULT-LATITUDE-X43-SEDAN-01	HIGH		READY
124913	124913	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
124914	124914	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-PREFL-01	HIGH		READY
124918	124918	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-01	HIGH		READY
124925	124925	Coupe	A5 II	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
124926	124926	Hatchback	A5 II Sportback	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback五门快背外廓。	READY
124945	124945	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124949	124949	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124950	124950	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
124951	124951	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	第二代5008按SUV物理车身归类。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_901-1000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CROSSROAD-II-RT3-SUV-01	4285	1755	1670	Honda Crossroad official Fact Book	https://www.honda.co.jp/factbook/auto/CROSSROAD/200702/15.html
EU-DACIA-1100-SEDAN-01	3990	1490	1410	Auto-Data.net Dacia 1100 1.1	https://www.auto-data.net/en/dacia-1100-1.1-46hp-55751
EU-DE-TOMASO-DEAUVILLE-SEDAN-01	4886	1878	1368	Automobile-Catalog 1974 De Tomaso Deauville	https://www.automobile-catalog.com/car/1974/58400/de_tomaso_deauville.html
EU-DACIA-LOGAN-I-MCV-FACELIFT-01	4473	1740	1640	Auto-Data.net Dacia Logan I MCV facelift 1.6 MPI LPG	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.6-mpi-8v-84hp-lpg-46172
EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-01	5097	1885	1438	Auto-Data.net Maserati Quattroporte V 4.2 V8	https://www.auto-data.net/en/maserati-quattroporte-v-4.2-i-v8-32v-400hp-10899
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601	Auto-Data.net Seat Ateca I 2.0 TDI	https://www.auto-data.net/en/seat-ateca-i-2.0-tdi-150hp-start-stop-23119
EU-MAZDA-626-I-CB2-COUPE-01	4420	1690	1370	UltimateSpecs Mazda 626 I HardTop 2.0	https://www.ultimatespecs.com/car-specs/Mazda/7529/Mazda-626-I-HardTop-20.html
EU-MITSUBISHI-COLT-VI-Z30-RALLIART-HATCHBACK-01	3925	1695	1535	Onteco Mitsubishi Colt Ralliart Version R	https://ontecojp.com/catalog/mitsubishi/colt/10060047
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1888	Auto-Data.net Land Rover Discovery V 2.0 SD4;CarExpert 2017 Land Rover Discovery exterior dimensions	https://www.auto-data.net/en/land-rover-discovery-v-2.0-sd4-240hp-4wd-automatic-39109;https://www.carexpert.com.au/land-rover/discovery/2017/exterior-and-dimensions
EU-MITSUBISHI-LANCER-EVOLUTION-X-CZ4A-SEDAN-01	4505	1810	1480	Auto-Data.net Mitsubishi Lancer Evolution X 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-lancer-evolution-x-2.0-mivec-295hp-s-awc-15647
EU-MORGAN-4-4-SIGMA-CONVERTIBLE-01	4010	1630	1220	Automobile-Catalog 2009 Morgan 4/4 Sport	https://www.automobile-catalog.com/car/2009/2039345/morgan_44_sport.html
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408	Auto-Data.net BMW 3 Series Compact E46 318ti	https://www.auto-data.net/en/bmw-3-series-compact-e46-318ti-143hp-9972
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613	Auto-Data.net Volkswagen Golf VII Sportsvan facelift 1.6 TDI SCR	https://www.auto-data.net/en/volkswagen-golf-vii-sportsvan-facelift-2017-1.6-tdi-scr-116hp-dsg-36070
EU-LEXUS-LC-I-COUPE-01	4760	1920	1345	Auto-Data.net Lexus LC 500 V8	https://www.auto-data.net/en/lexus-lc-500-v8-477hp-automatic-29883
EU-RENAULT-FLUENCE-I-L30-SEDAN-PREFL-01	4620	1809	1479	Auto-Data.net Renault Fluence 1.6 16V	https://www.auto-data.net/en/renault-fluence-1.6-16v-110hp-10656
EU-RENAULT-FLUENCE-I-L30-SEDAN-FACELIFT-01	4622	1809	1479	Auto-Data.net Renault Fluence facelift 1.6 16V	https://www.auto-data.net/en/renault-fluence-facelift-2012-1.6-16v-110hp-18014
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441	Auto-Data.net MINI Clubman F54 Cooper S 2.0	https://www.auto-data.net/en/mini-clubman-f54-cooper-s-2.0-192hp-34092
EU-PIAGGIO-APE-TM-PICKUP-NORMAL-DECK-01	3175	1480	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-LONG-DECK-01	3390	1500	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-PICKUP-TIPPER-01	3225	1500	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-HANDLEBAR-01	3150	1455	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-CHASSIS-STEERING-01	3210	1455	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Auto-Data.net Volkswagen Golf VII 5-door facelift 1.6 TDI	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.6-tdi-115hp-27633
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515	Auto-Data.net Volkswagen Golf VII Variant facelift 1.6 TDI	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.6-tdi-115hp-27735
EU-SUBARU-SVX-CXW-COUPE-01	4625	1777	1300	Auto-Data.net Subaru SVX CXW 3.3 AWD	https://www.auto-data.net/en/subaru-svx-cx-3.3-i-24v-4wd-cxw-230hp-16203
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414	Auto-Data.net MINI Hatch F56 3-door Cooper S 2.0	https://www.auto-data.net/en/mini-hatch-f56-3-door-cooper-s-2.0-192hp-21555
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415	Auto-Data.net MINI Convertible F57 Cooper S	https://www.auto-data.net/en/mini-convertible-f57-cooper-s-2.0-192hp-22760
EU-NISSAN-SKYLINE-XII-KV36-SEDAN-01	4755	1770	1450	Automobile-Catalog Nissan Skyline 370GT Type S;Goo-net Exchange Nissan Skyline 370GT Type S	https://www.automobile-catalog.com/car/2008/2138870/nissan_skyline_370gt_type_s.html;https://www.goo-net-exchange.com/catalog/NISSAN__SKYLINE/10052348/
EU-RENAULT-TWINGO-III-HATCHBACK-01	3595	1647	1557	Auto-Data.net Renault Twingo III 0.9 TCe	https://www.auto-data.net/en/renault-twingo-iii-0.9-tce-90hp-20242
EU-CATERHAM-SEVEN-485-CONVERTIBLE-S3-01	3100	1575	1115	Caterham Seven 485 price and specification list;Caterham Seven official owners handbook	https://www.caterham-sv.com/wp-content/uploads/2022/03/485-Price-Specification_RRP_A4_V3.3.pdf;https://caterhamcars.com/assets/Documents/Owner-Downloads/Owners-Handbook-All-Models_2023_ED1.2.pdf
EU-CATERHAM-SEVEN-485-CONVERTIBLE-SV-01	3300	1685	1140	Caterham Seven 485 price and specification list;Caterham Seven official owners handbook	https://www.caterham-sv.com/wp-content/uploads/2022/03/485-Price-Specification_RRP_A4_V3.3.pdf;https://caterhamcars.com/assets/Documents/Owner-Downloads/Owners-Handbook-All-Models_2023_ED1.2.pdf
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480	Auto-Data.net Subaru Impreza V Hatchback 1.6i	https://www.auto-data.net/en/subaru-impreza-v-hatchback-1.6i-114hp-awd-lineartronic-32129
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518	Auto-Data.net MINI Paceman R61 Cooper S ALL4	https://www.auto-data.net/en/mini-paceman-r61-cooper-s-1.6-190hp-all4-21654
EU-MERCEDES-BENZ-C-A205-CABRIOLET-01	4686	1810	1409	Auto-Data.net Mercedes-Benz C-Class Cabriolet A205 C 220d	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-c-220d-170hp-24247
EU-SUZUKI-SX4-I-HATCHBACK-PREFL-01	4135	1755	1605	Automobile-Catalog 2007 Suzuki SX4 1.5XG 2WD	https://www.automobile-catalog.com/car/2007/3408440/suzuki_sx4_1_5xg_2wd.html
EU-SUZUKI-SX4-I-HATCHBACK-FACELIFT-01	4150	1755	1605	Automobile-Catalog 2012 Suzuki SX4 1.5XG 2WD	https://www.automobile-catalog.com/car/2012/3408770/suzuki_sx4_1_5xg_2wd.html
EU-HONDA-INTEGRA-III-DB8-SEDAN-PREFL-01	4525	1695	1355	GAZOO Honda Integra Type R E-DB8	https://gazoo.com/catalog/maker/HONDA/INTEGRA/199305/2001618/
EU-HONDA-INTEGRA-III-DB8-SEDAN-FACELIFT-01	4525	1695	1365	GAZOO Honda Integra Type R E-DB8	https://gazoo.com/catalog/maker/HONDA/INTEGRA/199305/2001346/
EU-MAZDA-AZ1-PG6SA-COUPE-01	3295	1395	1150	Auto-Data.net Mazda AZ-1	https://www.auto-data.net/en/mazda-az-1-generation-2423
EU-NISSAN-TEANA-II-TNJ32-SEDAN-01	4850	1795	1500	Automobile-Catalog Nissan Teana 250XL Four;Onteco Nissan Teana 250XL Four	https://www.automobile-catalog.com/car/2013/2282780/nissan_teana_250xl_four.html;https://ontecojp.com/catalog/nissan/teana/10057024
EU-HYUNDAI-XG-FACELIFT-SEDAN-01	4875	1825	1420	Auto-Data.net Hyundai Grandeur III XG facelift 2.5 V6	https://www.auto-data.net/en/hyundai-grandeur-iii-xg-facelift-2003-2.5i-v6-172hp-automatic-30676
EU-TOYOTA-TERCEL-II-AL20-SEDAN-01	3910	1615	1385	Toyota 75 Years Vehicle Lineage Tercel and Corsa	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60010722B/index.html
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534	Auto-Data.net Dacia Sandero I 1.5 dCi	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-86hp-46138
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426	Auto-Data.net MINI Clubman R55 Cooper SD	https://www.auto-data.net/en/mini-clubman-r55-cooper-sd-2.0-143hp-21507
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Auto-Data.net Renault Megane IV 1.6 SCe	https://www.auto-data.net/en/renault-megane-iv-1.6-sce-115hp-22552
EU-DACIA-DOKKER-I-VAN-01	4363	1751	1809	Auto-Data.net Dacia Dokker Van 1.5 dCi	https://www.auto-data.net/en/dacia-dokker-van-1.5-dci-90hp-fap-18346
EU-BMW-1-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421	Auto-Data.net BMW 1 Series E87 LCI 120d	https://www.auto-data.net/en/bmw-1-series-hatchback-5dr-e87-lci-facelift-2007-120d-177hp-9813
EU-WIESMANN-MF3-ROADSTER-01	3860	1750	1160	UltimateSpecs Wiesmann Roadster MF3	https://www.ultimatespecs.com/car-specs/Wiesmann/30217/Wiesmann-Roadster-MF-3.html
EU-TAZZARI-ZERO-HATCHBACK-01	2880	1560	1425	Automobile Propre Tazzari Zero specifications	https://www.automobile-propre.com/voitures/tazzari-zero/
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1722	Auto-Data.net Bentley Bentayga 4.0 diesel V8	https://www.auto-data.net/en/bentley-bentayga-4.0-diesel-v8-435hp-awd-automatic-27234
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414	Auto-Data.net MINI Convertible R57 Cooper S	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6-175hp-21563
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414	Auto-Data.net MINI Convertible R57 facelift Cooper S	https://www.auto-data.net/en/mini-convertible-r57-facelift-2011-cooper-s-1.6-184hp-automatic-21571
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418	Auto-Data.net BMW 3 Series Touring E91 320d	https://www.auto-data.net/en/bmw-3-series-touring-e91-320d-163hp-steptronic-20748
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418	Auto-Data.net BMW 3 Series Touring E91 LCI 318d	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-318d-143hp-27580
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370	Auto-Data.net BMW 3 Series Coupe E46 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-318ci-143hp-9996
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369	Auto-Data.net BMW 3 Series Coupe E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-facelift-2003-318ci-143hp-46092
EU-FORD-THUNDERBIRD-X-MN12-COUPE-01	5088	1847	1333	Auto-Data.net Ford Thunderbird 4.6 V8	https://www.auto-data.net/en/ford-thunderbird-super-birds-4.6i-v8-208hp-8098
EU-FORD-MONDEO-V-CD391-SEDAN-01	4871	1852	1482	Auto-Data.net Ford Mondeo IV Sedan 1.5 EcoBoost	https://www.auto-data.net/en/ford-mondeo-iv-sedan-1.5-ecoboost-160hp-20356
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421	Auto-Data.net BMW 3 Series Sedan E90 318d	https://www.auto-data.net/en/bmw-3-series-sedan-e90-318d-122hp-9926
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421	Auto-Data.net BMW 3 Series Sedan E90 LCI 318d	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-318d-143hp-steptronic-27844
EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	Auto-Data.net BMW 1 Series E87 120d	https://www.auto-data.net/en/bmw-1-series-hatchback-e87-120d-163hp-steptronic-21117
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423	Auto-Data.net Porsche Panamera G2 3.0 V6	https://www.auto-data.net/en/porsche-panamera-g2-3.0-v6-330hp-pdk-26984
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4765	1965	2100	Truck1 Peugeot J5 Van 1.8 technical specifications;Peugeot J5 1.8 engine application	https://www.truck1.eu/blog/peugeot-j5-van-1.8-69-hp-tech-specs-t30476;https://www.motorzentrale.de/peugeot/j5/
EU-MERCEDES-BENZ-E-C238-COUPE-01	4826	1860	1430	Auto-Data.net Mercedes-Benz E-Class Coupe C238 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-200-184hp-9g-tronic-27317
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455	Auto-Data.net Hyundai i30 III 1.4 T-GDi	https://www.auto-data.net/en/hyundai-i30-iii-1.4-t-gdi-140hp-25965
EU-CHRYSLER-SEBRING-JS-CONVERTIBLE-01	4930	1843	1500	Auto-Data.net Chrysler Sebring Convertible JS	https://www.auto-data.net/en/chrysler-sebring-convertible-js-generation-3270
EU-AUDI-A4-B9-ALLROAD-WAGON-01	4750	1842	1493	Auto-Data.net Audi A4 Allroad B9 2.0 TDI	https://www.auto-data.net/en/audi-a4-allroad-b9-8w-2.0-tdi-150hp-quattro-ultra-36295
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446	Auto-Data.net Seat Leon III SC facelift 1.6 TDI	https://www.auto-data.net/en/seat-leon-iii-sc-facelift-2016-1.6-tdi-115hp-27057
EU-CHRYSLER-NEON-II-PL-SEDAN-01	4390	1715	1421	Auto-Data.net Chrysler Neon II	https://www.auto-data.net/en/chrysler-neon-ii-generation-3260
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-01	4500	1777	1467	Auto-Data.net Renault Megane II Grandtour Phase II 1.6 16V	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-30357
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448	Auto-Data.net Renault Clio IV Phase II 1.5 dCi	https://www.auto-data.net/en/renault-clio-iv-phase-ii-2016-1.5-dci-75hp-35442
EU-RENAULT-LATITUDE-X43-SEDAN-01	4897	1832	1483	Auto-Data.net Renault Latitude	https://www.auto-data.net/en/renault-latitude-generation-3771
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1539	Auto-Data.net Dacia Logan II MCV	https://www.auto-data.net/en/dacia-logan-ii-mcv-0.9-tce-90hp-18337
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4346	1733	1517	Auto-Data.net Dacia Logan II 0.9 TCe LPG	https://www.auto-data.net/en/dacia-logan-ii-0.9-tce-90hp-lpg-start-stop-23651
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Auto-Data.net Audi A5 Coupe F5 2.0 TFSI	https://www.auto-data.net/en/audi-a5-coupe-f5-2.0-tfsi-252hp-s-tronic-30250
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi MediaInfo A5 Sportback official technical data	https://press.audi.co.uk/assets/documents/original/16287-AudiUK00017563AudiA5andS5Sportback.pdf
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646	Auto-Data.net Peugeot 5008 II Phase I 1.6 BlueHDi	https://www.auto-data.net/en/peugeot-5008-ii-phase-i-2017-1.6-bluehdi-100hp-27386
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_901-1000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.truck1.eu/blog/peugeot-j5-van-1-8-69-hp-tech-specs-t30476?srsltid=AfmBOoonPH61miWdKNK2WNlbxb1bKRfb6rvjZIDaVlmEMR-rQC87tRs7 "https://www.truck1.eu/blog/peugeot-j5-van-1-8-69-hp-tech-specs-t30476?srsltid=AfmBOoonPH61miWdKNK2WNlbxb1bKRfb6rvjZIDaVlmEMR-rQC87tRs7"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_901-1000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_901-1000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（915 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（479 行）

