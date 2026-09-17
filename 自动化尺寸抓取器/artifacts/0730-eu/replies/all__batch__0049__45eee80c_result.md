# 任务：all 第 4801-4900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0049__45eee80c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4801-4900 行

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
all 第 4801-4900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450
EU-ALFA-ROMEO-GIULIA-952-SEDAN-QUADRIFOGLIO-01	4639	1874	1433
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436
EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	4490	1942	1274
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-2-F87-M2-CS-COUPE-01	4461	1871	1414
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
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-F95-M-COMPETITION-SUV-01	4953	2015	1749
EU-BMW-X5-F95-M-SUV-01	4953	2015	1751
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-BMW-X6-F16-SUV-01	4909	1989	1702
EU-BMW-X6-F96-M-COMPETITION-SUV-01	4953	2019	1692
EU-BMW-X6-F96-M-SUV-01	4953	2019	1693
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696
EU-CHEVROLET-CORVETTE-C3-COUPE-FACELIFT-01	4704	1753	1219
EU-CHEVROLET-CORVETTE-C5-Z06-COUPE-01	4564	1869	1212
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1840
EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	4753	1848	1849
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905
EU-FIAT-500-I-312-HATCHBACK-FACELIFT-01	3571	1627	1488
EU-FIAT-500-I-312-HATCHBACK-PREFL-01	3546	1627	1488
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L2-FWD-01	5572	2066	2214
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-FWD-01	6022	2066	2203
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-DRW-01	6022	2111	2218
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-SRW-01	6022	2066	2218
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
EU-HYUNDAI-H100-II-VAN-01	4790	1690	1965
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	4597	2069	1727
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	4597	1904	1727
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494
EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	4424	1804	1494
EU-MG-ZS-I-SUV-01	4314	1809	1611
EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	6199	2070	2263
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	5549	2070	2265
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	6199	2070	2258
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307
EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	5048	2070	2500
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499
EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	5548	2070	2749
EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	6198	2070	2488
EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	6198	2070	2744
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	5643	2070	2283
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	5643	2070	2284
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	6193	2070	2283
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	6293	2070	2276
EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	6198	2070	2549
EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	6198	2070	2527
EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	6198	2070	2815
EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	6198	2070	2786
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812
EU-OPEL-COMBO-E-LIFE-L-MPV-01	4403	1848	1844
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880
EU-OPEL-COMBO-E-LIFE-XL-MPV-02	4753	1848	1849
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-OPEL-VIVARO-C-K0-PLATFORM-CAB-M-01	4959	1920	1930
EU-OPEL-VIVARO-C-K0-VAN-L-01	5309	1920	1935
EU-OPEL-VIVARO-C-K0-VAN-M-01	4959	1920	1895
EU-OPEL-VIVARO-C-K0-VAN-S-01	4609	1920	1905
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	4467	1801	1635
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	5333	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	4983	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	5331	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	4981	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	4137	1724	1810
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	5333	1920	1890
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	4983	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468
EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	3890	1735	1495
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	Boxer	2.2 Bluehdi 165	Bus	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2024-05-01	139329
Chevrolet	Corvette	6.2	Coupe	Heckantrieb	Benzin	369	502	Jul 2019	-	2024-03-01	139330
BMW	X5	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	May 2020	-	2024-03-01	139332
BMW	X6	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	May 2020	Mar 2023	2024-03-01	139333
Citroën	Berlingo	1.5 Bluehdi 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Jun 2018	-	2024-03-01	139338
Citroën	Jumpy iii	2.0 Bluehdi 120 4X4	Kasten	Allrad	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	139339
Citroën	Jumpy iii	2.0 Bluehdi 150 4X4	Kasten	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139341
Citroën	Spacetourer	2.0 Bluehdi 150 4X4	Bus	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139344
Peugeot	Partner	1.5 Bluehdi 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Sep 2018	-	2024-03-01	139347
Peugeot	Expert	2.0 Bluehdi 120 4X4	Kasten	Allrad	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	139348
Peugeot	Expert	2.0 Bluehdi 150 4X4	Kasten	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2026-01-01	139354
Peugeot	Boxer	2.2 HDI 130 4X4	Kasten	Allrad	Diesel	96	131	Mar 2011	-	2024-03-01	139362
Peugeot	Boxer	2.2 HDI 150 4X4	Kasten	Allrad	Diesel	110	150	Mar 2011	-	2024-03-01	139364
Peugeot	Boxer	2.0 Bluehdi 130 4X4	Kasten	Allrad	Diesel	96	130	Mar 2016	Sep 2019	2025-02-03	139365
Peugeot	Boxer	2.0 Bluehdi 160 4X4	Kasten	Allrad	Diesel	120	163	Mar 2016	Sep 2019	2025-02-03	139366
Peugeot	Traveller	2.0 Bluehdi 150 / HDI 150 4X4	Bus	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139367
Opel	Zafira	2.0 4X4	Bus	Allrad	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	139376
Opel	Combo	1.5 D Allrad	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Aug 2018	-	2025-06-01	139377
Opel	Vivaro c	1.5 Allrad	Kasten	Allrad	Diesel	88	120	Mar 2019	-	2025-06-01	139378
Opel	Vivaro c	2.0 Allrad	Kasten	Allrad	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	139379
Mercedes-benz	Sprinter classic 3,5-T	313 CDI	Kasten	Heckantrieb	Diesel	100	136	Jan 2017	-	2024-03-01	139397
Mercedes-benz	Sprinter classic 4,6-T	413 CDI	Kasten	Heckantrieb	Diesel	100	136	Jan 2017	-	2024-03-01	139398
Nissan	Nv400	DCI 180	Kasten	Frontantrieb	Diesel	132	179	Jan 2020	Dec 2022	2026-03-01	139400
Nissan	Nv400	DCI 180	Pritsche/Fahrgestell	Frontantrieb	Diesel	132	179	Jan 2020	Dec 2022	2026-03-01	139401
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	90	122	Nov 2019	Dec 2022	2026-01-01	139431
Land Rover	Range rover sport ii	3.0 P360 Mhev 4X4	SUV	Allrad	Benzin/Elektro	265	360	Jun 2019	Mar 2022	2025-02-03	139460
BMW	3	330 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	215	292	Jul 2020	-	2024-03-01	139467
BMW	3	330 E Plug-in-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	215	292	Jul 2020	-	2024-03-01	139469
BMW	3	M340 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	250	340	Apr 2020	-	2024-03-01	139470
BMW	3	M 340 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	250	340	Apr 2020	-	2024-03-01	139471
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	66	90	Oct 2019	Aug 2024	2025-02-03	139473
BMW	3	320 I	Kasten/Kombi	Heckantrieb	Benzin	135	184	Nov 2019	-	2024-03-01	139481
BMW	3	330 I	Kasten/Kombi	Heckantrieb	Benzin	190	258	Jul 2019	-	2024-03-01	139482
BMW	3	M 340 I Xdrive	Kasten/Kombi	Allrad	Benzin	275	374	Nov 2019	-	2024-03-01	139483
BMW	3	320 D	Kasten/Kombi	Heckantrieb	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	139484
BMW	3	320 D Mild-hybrid	Kasten/Kombi	Heckantrieb	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139485
BMW	3	320 D Xdrive	Kasten/Kombi	Allrad	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	139486
BMW	3	320 D Mild-hybrid Xdrive	Kasten/Kombi	Allrad	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139487
BMW	3	330 D	Kasten/Kombi	Heckantrieb	Diesel	195	265	Nov 2019	-	2024-03-01	139488
BMW	3	330 D Xdrive	Kasten/Kombi	Allrad	Diesel	195	265	Nov 2019	-	2024-03-01	139489
BMW	X5	Xdrive 30 D	Kasten/SUV	Allrad	Diesel	195	265	Nov 2019	Mar 2023	2024-03-01	139490
BMW	X5	Xdrive 40 I	Kasten/SUV	Allrad	Benzin	250	340	Nov 2019	Mar 2023	2024-03-01	139491
Peugeot	Partner	1.6 HDI 92	Kasten/Großraumlimousine	Frontantrieb	Diesel	68	92	Sep 2018	-	2024-05-01	139492
Opel	Grandland	1.6 Turbo	SUV	Frontantrieb	Benzin	110	150	Dec 2019	Jul 2021	2025-02-03	139502
MG	Hs	1.5 T	SUV	Frontantrieb	Benzin	119	162	Sep 2018	-	2025-12-01	139504
Fiat	500	1.0 Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	51	69	Jan 2020	-	2024-03-01	139507
Santana	300	1.6 HDI 4X4	Geländewagen offen	Allrad	Diesel	66	90	Oct 2006	Feb 2011	2024-03-01	139533
Land Rover	Range rover evoque	1.5 P300e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	227	309	Feb 2020	-	2024-03-01	139607
MG	Zs	EV	SUV	Frontantrieb	Elektro	105	143	Mar 2019	-	2025-12-01	139640
Ford	Transit v363	2.0 Ecoblue RWD	Bus	Heckantrieb	Diesel	96	130	May 2019	-	2024-03-01	139643
Ford	Transit v363	2.0 Ecoblue RWD	Bus	Heckantrieb	Diesel	125	170	May 2019	Jun 2024	2024-11-01	139644
Audi	A4 allroad b9	40 TDI Quattro	Kombi	Allrad	Diesel	140	190	Jan 2020	-	2024-03-01	139648
BMW	X3	Xdrive M40 I	SUV	Allrad	Benzin	285	387	Sep 2019	-	2024-03-01	139649
BMW	X3	Xdrive M40 I	Kasten/SUV	Allrad	Benzin	285	387	Sep 2019	-	2024-03-01	139650
Alfa Romeo	Giulia	2.9 GTA	Stufenheck	Heckantrieb	Benzin	397	540	May 2020	-	2024-03-01	139651
Mercedes-benz	Gla	GLA 200	SUV	Frontantrieb	Benzin	120	163	Feb 2020	-	2024-03-01	139652
Mercedes-benz	Gla	GLA 250	SUV	Frontantrieb	Benzin	165	224	Feb 2020	-	2024-03-01	139653
Mercedes-benz	Gla	GLA 250 4-matic	SUV	Allrad	Benzin	165	224	Feb 2020	-	2024-03-01	139654
Mercedes-benz	Gla	GLA 200 D	SUV	Frontantrieb	Diesel	110	150	Feb 2020	-	2024-03-01	139655
Mercedes-benz	Gla	GLA 200 D 4-matic	SUV	Allrad	Diesel	110	150	Feb 2020	-	2024-03-01	139656
Lancia	Ypsilon	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	51	69	Mar 2020	-	2024-03-01	139657
Mercedes-benz	Gla	GLA 220 D 4-matic	SUV	Allrad	Diesel	140	190	Feb 2020	-	2024-03-01	139658
Mercedes-benz	Gla	GLA 220 D	SUV	Frontantrieb	Diesel	140	190	Feb 2020	-	2024-03-01	139659
Aston Martin	Dbx	4	SUV	Allrad	Benzin	405	551	Nov 2019	-	2024-03-01	139672
Land Rover	Discovery sport	1.5 P300e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	227	309	Feb 2020	-	2024-03-01	139678
Suzuki	Swift v	1.4 Sport Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	95	129	Mar 2020	-	2024-03-01	139679
BMW	2	216 D	Coupe	Frontantrieb	Diesel	85	116	Mar 2020	-	2024-03-01	139680
KIA	Ceed	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	101	Sep 2019	-	2024-03-01	139690
KIA	Ceed	1.6 Crdi 115 Eco-dynamics+	Schrägheck	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139693
KIA	Ceed	1.6 Crdi 136 Eco-dynamics+	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139694
KIA	Ceed	1.6 Crdi 115 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139695
KIA	Ceed	1.6 Crdi 136 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139696
KIA	Proceed	1.6 Crdi 136 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139697
KIA	Xceed	1.6 Crdi 115 Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139698
KIA	Xceed	1.6 Crdi 136 Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139699
Audi	A3	35 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2019	-	2024-03-01	139714
Audi	A3	30 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Nov 2019	-	2024-03-01	139715
Audi	A3	35 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	139716
Porsche	718 cayman	GTS 4.0	Coupe	Heckantrieb	Benzin	294	400	Jan 2019	-	2024-03-01	139717
Porsche	718 boxster	GTS 4.0	Cabriolet	Heckantrieb	Benzin	294	400	Jan 2019	-	2024-03-01	139725
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	131	Nov 2019	-	2024-03-01	139734
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2019	-	2024-03-01	139736
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Nov 2019	-	2024-03-01	139737
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	139738
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	96	131	Mar 2020	-	2024-03-01	139744
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Mar 2020	-	2024-03-01	139745
VW	Golf viii	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Dec 2019	-	2024-03-01	139749
Skoda	Octavia	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2020	-	2024-03-01	139764
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Mar 2020	-	2024-03-01	139765
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2020	-	2024-03-01	139766
Hyundai	H100	2.5 TCI	Pritsche/Fahrgestell	Heckantrieb	Diesel	74	100	Jan 2004	Dec 2012	2024-03-01	139767
Nissan	Cedric	2.8	Stufenheck	Heckantrieb	Benzin	108	147	Jan 1980	Feb 1983	2024-03-01	139779
Bestune	T77	PRO 280 TID	SUV	Frontantrieb	Benzin	124	169	Mar 2020	-	2024-03-01	139781
KIA	Sorento iv	2.2 Crdi	SUV	Frontantrieb	Diesel	148	201	Mar 2020	-	2024-03-01	139786
KIA	Sorento iv	2.2 Crdi 4WD	SUV	Allrad	Diesel	148	201	Mar 2020	-	2024-03-01	139787
Aston Martin	Vantage	V8	Cabriolet	Heckantrieb	Benzin	375	510	Feb 2020	-	2024-03-01	139788
Volvo	S90 ii	B4 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2024-03-01	139795
Volvo	S90 ii	B5 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	139796
Volvo	S90 ii	B6 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139797
Volvo	V90 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2024-03-01	139799


--- Round 1 / 首次发送 ---
更新点

* 按跨批次尺寸组索引完成首批缓存关联，共闭合 39 个 Ktype。
* 本轮复用 21 个既有尺寸组，未重复抓取或输出尺寸来源。
* BMW G21、Kia CD、Audi A3 8V、Volvo S90 等同外廓动力版本已批量关联。

当前批次进度

* 输入 Ktype：100
* READY 映射：39
* PENDING 映射：61
* 已引用尺寸组：21
* 本轮新建或修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139332	139332	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前标准SUV外廓。	READY
139333	139333	SUV	X6 III	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV外廓。	READY
139460	139460	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	L494改款后标准SUV外廓。	READY
139467	139467	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	G20改款前xDrive轿车外廓。	READY
139471	139471	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340d与既有G21 M Performance xDrive旅行车共用外廓。	READY
139481	139481	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139482	139482	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139483	139483	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340i xDrive使用G21 M Performance旅行车外廓。	READY
139484	139484	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139485	139485	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	轻混动力不改变G21后驱Touring外廓。	READY
139486	139486	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	Kasten/Kombi对应G21 xDrive Touring外廓。	READY
139487	139487	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	轻混动力不改变G21 xDrive Touring外廓。	READY
139488	139488	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139489	139489	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	Kasten/Kombi对应G21 xDrive Touring外廓。	READY
139490	139490	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	Kasten/SUV对应G05改款前标准SUV外廓。	READY
139491	139491	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	Kasten/SUV对应G05改款前标准SUV外廓。	READY
139502	139502	SUV	Grandland X I	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18标准SUV外廓。	READY
139607	139607	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	P300e使用L551五门SUV外廓。	READY
139648	139648	Wagon	A4 allroad B9	B9	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH	B9 allroad旅行车外廓。	READY
139649	139649	SUV	X3 III	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	G01 M40i专用外廓。	READY
139650	139650	SUV	X3 III	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	Kasten/SUV与同版本G01 M40i共用外廓。	READY
139678	139678	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	P300e对应L550改款后五门外廓。	READY
139679	139679	Hatchback	Swift VI	A2L	5	EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	HIGH	输入代次命名归并至A2L Swift Sport五门外廓。	READY
139680	139680	Coupe	2 Series Gran Coupe I	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱216d对应F44四门Gran Coupe外廓。	READY
139690	139690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	CD五门掀背标准外廓。	READY
139693	139693	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	轻混柴油动力不改变CD五门掀背外廓。	READY
139694	139694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	轻混柴油动力不改变CD五门掀背外廓。	READY
139695	139695	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon标准外廓。	READY
139696	139696	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon标准外廓。	READY
139697	139697	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD ProCeed shooting-brake外廓。	READY
139698	139698	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD XCeed改款前外廓。	READY
139699	139699	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD XCeed改款前外廓。	READY
139714	139714	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139715	139715	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139716	139716	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139749	139749	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背外廓。	READY
139795	139795	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B4轻混动力不改变S90 II轿车外廓。	READY
139796	139796	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B5轻混动力不改变S90 II轿车外廓。	READY
139797	139797	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B6 AWD轻混动力不改变S90 II轿车外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 集中核对 Citroën、Peugeot、Opel 的 Dangel/4X4 商用车簇，按 Van、MPV、长度和车顶分支一次性闭合。
2. 处理 Corvette C8、MG HS、Mercedes-Benz GLA H247、Seat Leon IV、Skoda Octavia IV 等待新建尺寸组的乘用车。
3. 最后处理 Boxer、Transit Bus、Sprinter Classic、H100 等多轴距或多车顶复杂商用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 首次闭合 BMW G20 M340d xDrive Sedan、Fiat 500C Hybrid 和 Škoda Octavia IV 掀背尺寸组；官方资料分别确认三维为 4713×1827×1440、3571×1627×1488、4689×1829×1470 mm。
* 新增 6 个 READY 映射；Volvo V90 B4 直接复用既有 V90 II Wagon 尺寸组。
* 本轮首次创建 3 个尺寸组，未修改已有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 映射：45
* PENDING 映射：55
* 当前已引用尺寸组：25
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139470	139470	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	HIGH	M340d xDrive专用M Performance轿车外廓。	READY
139507	139507	Convertible	500 I	312		EU-FIAT-500-I-312-CONVERTIBLE-FACELIFT-01	HIGH	500C改款后敞篷外廓。	READY
139764	139764	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139765	139765	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139766	139766	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139799	139799	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	B4轻混动力不改变V90 II旅行车外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440	BMW M340d xDrive Sedan official specifications 02/2020	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-FIAT-500-I-312-CONVERTIBLE-FACELIFT-01	3571	1627	1488	Fiat 500 and 500C official technical specifications January 2020	https://www.media.stellantis.com/uploads/fr/attachment/fiat500_fichetarifs_janvier2020-5e3965a67fbbc.pdf
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470	Škoda Octavia official petrol technical specifications July 2020	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-petrol-en.pdf
```

下一步优先处理

1. 批量闭合 SEAT Leon IV 五门与 Sportstourer，并处理标准悬架和 FR 低车身边界。
2. 处理 Mercedes-Benz GLA H247、Kia Sorento IV、MG HS、MG ZS EV 等乘用车新尺寸组。
3. 集中处理 PSA/Stellantis Dangel 4×4 商用车簇，按长度、车顶及 Van/MPV 分支一次建组并批量关联。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 新增 14 个 READY 映射：BMW 330e xDrive Touring 复用既有尺寸组；Mercedes-Benz GLA H247 的 7 个动力版本批量关联同一外廓。([宝马集团新闻][1])
* 首次闭合 MG HS、MG ZS EV、Lancia Ypsilon Hybrid、Aston Martin DBX，以及 Porsche 718 Cayman/Boxster GTS 4.0，共新建 7 个尺寸组。([Mail & Guardian][2])
* 未修改任何跨批次既有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 映射：59
* PENDING 映射：41
* 当前已引用尺寸组：33
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139469	139469	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	G21 330e Touring五门外廓。	READY
139504	139504	SUV	HS I		5	EU-MG-HS-I-SUV-01	HIGH	HS I五门SUV外廓。	READY
139640	139640	SUV	ZS I		5	EU-MG-ZS-I-EV-SUV-01	HIGH	ZS EV初期型五门SUV外廓。	READY
139652	139652	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139653	139653	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139654	139654	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139655	139655	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139656	139656	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139657	139657	Hatchback	Ypsilon III		5	EU-LANCIA-YPSILON-III-HATCHBACK-FACELIFT-01	MEDIUM	改款后五门车身；官方厘米尺寸已换算为毫米。	READY
139658	139658	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139659	139659	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139672	139672	SUV	DBX I		5	EU-ASTON-MARTIN-DBX-I-SUV-01	HIGH	初代DBX五门SUV外廓。	READY
139717	139717	Coupe	718	982	2	EU-PORSCHE-718-982-CAYMAN-GTS-4-0-COUPE-01	HIGH	982 GTS 4.0双门硬顶外廓。	READY
139725	139725	Convertible	718	982	2	EU-PORSCHE-718-982-BOXSTER-GTS-4-0-CONVERTIBLE-01	HIGH	982 GTS 4.0双门敞篷外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MG-HS-I-SUV-01	4574	1876	1685	MG HS Owner Manual	https://www.mg.co.uk/sites/default/files/2021-11/MG%20HS%20Owner%20Manual.pdf
EU-MG-ZS-I-EV-SUV-01	4314	1809	1644	MG Motor Europe MG ZS EV official technical specifications	https://news.mgmotor.eu/press/mg-zs-ev-the-first-truly-affordable-electric-b-segment-suv/
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	Mercedes-Benz GLA H247 official brochure	https://www.mercedes-benzcaribbean.com/assets/brochures/GLA_H247_ePaper_0420_02_ENG.pdf
EU-LANCIA-YPSILON-III-HATCHBACK-FACELIFT-01	3840	1680	1520	Lancia New Ypsilon official Frankfurt press material; Lancia Ypsilon Hybrid EcoChic official launch	https://www.media.stellantis.com/em-en/lancia/press/lancia-at-the-2015-frankfurt-international-motor-show;https://www.media.stellantis.com/em-en/lancia/press/lancia-ypsilon-celebrates-its-35th-anniversary-and-production-of-3-million-units-by-presenting-ypsilon-dreamers
EU-ASTON-MARTIN-DBX-I-SUV-01	5039	1998	1680	Aston Martin DBX official launch specification	https://media.astonmartin.com/aston-martin-unveils-dbx-an-suv-with-the-soul-of-a-sports-car-3
EU-PORSCHE-718-982-CAYMAN-GTS-4-0-COUPE-01	4405	1801	1276	Porsche 718 Boxster GTS 4.0 and 718 Cayman GTS 4.0 official technical data	https://newsroom.porsche.com/dam/jcr%3A5d1b4e09-a439-4c4f-880c-a0faae55c450/718%20Boxster%20GTS%204.0%20and%20718%20Cayman%20GTS%204.0%20US%20technical%20specifications_.pdf
EU-PORSCHE-718-982-BOXSTER-GTS-4-0-CONVERTIBLE-01	4391	1801	1262	Porsche 718 Boxster GTS 4.0 and 718 Cayman GTS 4.0 official technical data	https://newsroom.porsche.com/dam/jcr%3A5d1b4e09-a439-4c4f-880c-a0faae55c450/718%20Boxster%20GTS%204.0%20and%20718%20Cayman%20GTS%204.0%20US%20technical%20specifications_.pdf
```

下一步优先处理

1. 集中闭合 SEAT Leon IV 五门与 Sportstourer，并区分标准悬架和低车身版本。
2. 批量处理 Citroën、Peugeot、Opel 的 Dangel 4×4 Van/MPV 簇，优先复用现有长度和车顶尺寸组。
3. 处理 Boxer、Transit Bus、NV400、Sprinter Classic 等仍涉及多轴距或多车顶分支的商用车。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0325532EN/471539?utm_source=chatgpt.com "BMW
Media
Information
03/2021
Page 1
Technica"
[2]: https://www.mg.co.uk/sites/default/files/2021-11/MG%20HS%20Owner%20Manual.pdf?utm_source=chatgpt.com "MG HS Owner Manual.pdf"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 新增 4 个 READY 映射，首次创建 3 个尺寸组。
* Corvette C8 Stingray 官方技术资料确认三维为 4630×1934×1234 mm；Kia Sorento IV 两个驱动版本共用 MQ4 标准外廓；2020 Vantage Roadster 规格明确宽度为不含后视镜的 1942 mm。([通用汽车新闻中心][1])
* 未修改任何既有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 映射：63
* PENDING 映射：37
* 当前已引用尺寸组：36
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139330	139330	Coupe	Corvette VIII	C8	2	EU-CHEVROLET-CORVETTE-C8-STINGRAY-COUPE-01	HIGH	C8 Stingray双门硬顶外廓。	READY
139786	139786	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4前驱五门SUV外廓。	READY
139787	139787	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4四驱五门SUV外廓。	READY
139788	139788	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-ROADSTER-01	HIGH	2020款双门Roadster外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORVETTE-C8-STINGRAY-COUPE-01	4630	1934	1234	Chevrolet New Corvette Stingray official technical data	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/next-gen-corvette/Chevrolet-Corvette-Stingray-Technical-Data-EN-190731.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1695	Kia Europe New Sorento official press kit	https://press.kia.com/content/dam/kiapress/EU/Pressreleases/2020/kia_pressrelease_2020_sorento/Press%20kit%20-%20New%20Kia%20Sorento%20-%2018%20Mar%202020%20v3.doc
EU-ASTON-MARTIN-VANTAGE-2018-ROADSTER-01	4465	1942	1273	Aston Martin Vantage Roadster official launch; Aston Martin Vantage Roadster specification sheet	https://www.astonmartin.com/en-gb/our-world/news/2020/2/12/vantage-roadster-uncompromising-performance-meets-pure-emotion;https://www.autointernational.com.my/WebNews/Overseas/Year%202020/ASTON%20MARTIN_VANTAGE%20ROADSTER%20-%2022%20Feb%2020/VANTAGE%20ROADSTER%20SPECIFICATION.pdf
```

下一步优先处理

1. 闭合 SEAT Leon IV 六个 Ktype，按五门/旅行车及标准悬架/FR 低车身拆分。
2. 批量处理 Citroën、Peugeot、Opel 的 Dangel 4×4 Van/MPV 簇。
3. 处理 Boxer、Transit Bus、NV400、Sprinter Classic 等多轴距、多车顶商用车分支。

推进信号：CONTINUE

[1]: https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/next-gen-corvette/Chevrolet-Corvette-Stingray-Technical-Data-EN-190731.pdf "For Release: Wednesday, Nov"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 闭合 SEAT Leon IV 的 6 个 Ktype。由于输入不限定普通悬架或 FR 悬架，每个 Ktype 均按标准车身与 FR 低车身拆分；五门版为 4368×1799×1456/1442 mm，Sportstourer 为 4642×1799×1450/1437 mm。([SEAT][1])
* 首次闭合 Bestune T77 Pro 与 Hyundai H100 HR 标准驾驶室底盘组；官方资料分别给出 4525×1845×1615 mm 和 4850×1740×1970 mm。
* Toyota Proace Verso 2.0 D-4D 按 Compact、Medium、Long 三种既有外廓拆分并复用缓存尺寸组。
* 本轮新增 16 行 READY 映射，首次创建 6 个尺寸组，未修改已有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：72
* READY 映射行：80
* PENDING 输入 Ktype：28
* 当前已引用尺寸组：45
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139431_compact	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact短车身分支。	READY
139431_medium	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium中车身分支。	READY
139431_long	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	HIGH	Long长车身分支。	READY
139734_std	139734	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139734_fr	139734	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139736_std	139736	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139736_fr	139736	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139737_std	139737	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139737_fr	139737	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139738_std	139738	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139738_fr	139738	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139744_std	139744	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架Sportstourer外廓。	READY
139744_fr	139744	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低车身Sportstourer外廓。	READY
139745_std	139745	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架Sportstourer外廓。	READY
139745_fr	139745	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低车身Sportstourer外廓。	READY
139767	139767	Pickup	H100 / Porter II	HR	2	EU-HYUNDAI-H100-HR-CHASSIS-CAB-01	HIGH	HR标准驾驶室底盘外廓。	READY
139781	139781	SUV	T77 I		5	EU-BESTUNE-T77-I-SUV-01	HIGH	T77 Pro五门SUV外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1799	1442	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-HYUNDAI-H100-HR-CHASSIS-CAB-01	4850	1740	1970	Hyundai H-100 official brochure	https://www.hyundai.com/content/dam/hyundai/ph/en/data/marketing/brochure/product/h100/H-100_FLYERv2.pdf
EU-BESTUNE-T77-I-SUV-01	4525	1845	1615	Bestune T77 official brochure	https://www.bestune.bh/brochure/bestune-t77.pdf
```

下一步优先处理

1. 集中闭合 Citroën、Peugeot、Opel 的 Dangel 4×4 Van/MPV 簇，按长度、车身用途和升高外廓批量建组。
2. 处理 Nissan NV400、Peugeot Boxer、Ford Transit Bus 与 Mercedes-Benz Sprinter Classic 的轴距、车顶和驾驶室分支。
3. 最后处理 Giulia GTA、Santana 300、Nissan Cedric 430 与 VW Transporter T6 等剩余特殊边界。

推进信号：CONTINUE

[1]: https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf?utm_source=chatgpt.com "New Leon Technical Brochure"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 闭合 Ktype `139473`，按 Volkswagen Caravelle 6.1 的 SWB/LWB 两种物理外廓拆分；官方尺寸图明确车身宽度为 1904 mm、含后视镜宽度为 2297 mm。SWB 为 4904×1904×1970 mm，LWB 为 5304×1904×1990 mm。
* 闭合 Ktype `139533` 的 Santana 300 三门开放式车身；两项规格库一致支持 3660×1630×1665 mm，其中 Automobile-Catalog 明确宽度不含后视镜。([汽车目录][1])
* 本轮新增 3 行 READY 映射、首次创建 3 个尺寸组，未修改既有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* READY 映射行：83
* PENDING 输入 Ktype：26
* 当前已引用尺寸组：48
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139473_swb	139473	MPV	Transporter T6.1 / Caravelle			EU-VW-CARAVELLE-T6-1-MPV-SWB-01	MEDIUM	短轴距乘用型车身分支。	READY
139473_lwb	139473	MPV	Transporter T6.1 / Caravelle			EU-VW-CARAVELLE-T6-1-MPV-LWB-01	MEDIUM	长轴距乘用型车身分支。	READY
139533	139533	Convertible	Santana 300		3	EU-SANTANA-300-CONVERTIBLE-3D-01	MEDIUM	三门开放式越野车外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CARAVELLE-T6-1-MPV-SWB-01	4904	1904	1970	Volkswagen Commercial Vehicles Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-CARAVELLE-T6-1-MPV-LWB-01	5304	1904	1990	Volkswagen Commercial Vehicles Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-SANTANA-300-CONVERTIBLE-3D-01	3660	1630	1665	Automobile-Catalog Santana 300 specifications; Auto-Data Santana 300 1.6 HDi 4WD specifications	https://www.automobile-catalog.com/car/2006/3043100/santana_300_berline.html;https://www.auto-data.net/en/santana-300-1.6-hdi-90hp-4wd-55590
```

下一步优先处理

1. 集中闭合 Jumpy、Expert、SpaceTourer、Traveller、Vivaro C 与 Zafira Life 的 Dangel 4×4 簇，按 Compact/Standard/Long 和 Van/MPV 分支建组。
2. 处理 Berlingo、Partner、Combo 的短轴/长轴及 Van/MPV 4×4 分支。
3. 最后处理 Boxer、Transit Bus、NV400、Sprinter Classic、Giulia GTA 与 Cedric 的复杂或特殊外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/3043100/santana_300_berline.html?utm_source=chatgpt.com "2006 Santana 300 Berline (man. 5) (Cazador, JX, JLX)."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
更新点

* 新增 7 行 READY 映射，闭合 2 个 Ktype。
* Nissan NV400 FWD 厢式车按 6 个现有长度/车顶尺寸组完成关联，未重复输出尺寸组。
* Alfa Romeo Giulia GTA 首次建组；官方欧洲参考数据明确其全长 4654 mm、不含后视镜宽度 1923 mm、含天线最大高度 1445 mm。([阿尔法·罗密欧][1])
* 本轮首次创建 1 个尺寸组，未修改既有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：76
* READY 映射行：90
* PENDING 输入 Ktype：24
* 当前已引用尺寸组：55
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139400_l1h1	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	FWD L1H1厢式车分支。	READY
139400_l1h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	FWD L1H2厢式车分支。	READY
139400_l2h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	FWD L2H2厢式车分支。	READY
139400_l2h3	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	FWD L2H3厢式车分支。	READY
139400_l3h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	FWD L3H2厢式车分支。	READY
139400_l3h3	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	FWD L3H3厢式车分支。	READY
139651	139651	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-GTA-SEDAN-01	HIGH	GTA宽体四门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-GIULIA-952-GTA-SEDAN-01	4654	1923	1445	Alfa Romeo Japan Giulia GTA/GTAm official European reference specifications	https://alfaromeo-jp.com/giulia/limited/gta/spec/
```

下一步优先处理

1. 闭合 Nissan NV400 FWD 单排/双排底盘分支，优先关联现有 L2、L3 尺寸组。
2. 集中处理 Jumpy、Expert、SpaceTourer、Traveller、Vivaro C 与 Zafira Life 的 Dangel 4×4 分支。
3. 处理 Boxer、Transit Bus 与 Sprinter Classic 的多轴距、多车顶外廓。

推进信号：CONTINUE

[1]: https://alfaromeo-jp.com/giulia/limited/gta/spec/?utm_source=chatgpt.com "Alfa Romeo GIULIA GTA（アルファ ロメオ ジュリア ジーティーエー）参考データ（欧州参考値） | セダン | 限定車 | Alfa Romeo（アルファ ロメオ）"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
更新点

* 闭合 Citroën Jumpy III 两个 4×4 Ktype，按 XS/M/XL 及普通/升高车身关联 5 个现有尺寸组；Dangel 资料确认 4×4 转换存在悬架升高配置，因此保留对应物理高度分支。([Dangel Shop][1])
* Nissan NV400 FWD 底盘按单排 L2H1、单排 L3H1、双排 L3H1 三个现有尺寸组完成关联。
* Nissan Cedric 430 的生产区间跨越 1981 年改款，车长由 4825 mm 变为 4885 mm，宽度和高度保持 1715×1430 mm，因此拆分改款前、改款后两个尺寸组。([汽车目录][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：80
* READY 映射行：105
* PENDING 输入 Ktype：20
* 当前已引用尺寸组：65
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139339_xs_low	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS普通高度4×4厢式车分支。	READY
139339_xs_high	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS升高4×4厢式车分支。	READY
139339_m_low	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M普通高度4×4厢式车分支。	READY
139339_m_high	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M升高4×4厢式车分支。	READY
139339_xl	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL长车身4×4厢式车分支。	READY
139341_xs_low	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS普通高度4×4厢式车分支。	READY
139341_xs_high	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS升高4×4厢式车分支。	READY
139341_m_low	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M普通高度4×4厢式车分支。	READY
139341_m_high	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M升高4×4厢式车分支。	READY
139341_xl	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL长车身4×4厢式车分支。	READY
139401_single_l2h1	139401	Pickup	NV400 I	X62	2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	HIGH	FWD单排L2H1底盘分支。	READY
139401_single_l3h1	139401	Pickup	NV400 I	X62	2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	FWD单排L3H1底盘分支。	READY
139401_double_l3h1	139401	Pickup	NV400 I	X62	4	EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	HIGH	FWD双排L3H1底盘分支。	READY
139779_prefl	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-PREFL-01	HIGH	430改款前四门轿车外廓。	READY
139779_facelift	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-FACELIFT-01	HIGH	430改款后四门轿车外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-CEDRIC-430-SEDAN-PREFL-01	4825	1715	1430	Automobile-Catalog 1980 Nissan Cedric 280E Brougham specifications	https://www.automobile-catalog.com/car/1980/2145065/nissan_cedric_4door_sedan_280e_brougham.html
EU-NISSAN-CEDRIC-430-SEDAN-FACELIFT-01	4885	1715	1430	Automobile-Catalog 1981 Nissan Cedric 280E Brougham specifications	https://www.automobile-catalog.com/car/1981/2146025/nissan_cedric_4door_sedan_280e_brougham.html
```

下一步优先处理

1. 闭合 Expert、SpaceTourer、Traveller、Vivaro C 与 Zafira Life 的 4×4 普通高度和升高车身分支。
2. 处理 Berlingo、Partner、Combo K9 4×4 的 M/XL 与悬架升高外廓。
3. 最后处理 Boxer、Transit Bus、Sprinter Classic 和旧款 Partner 的多轴距、多车顶边界。

推进信号：CONTINUE

[1]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf?utm_source=chatgpt.com "DANGEL TREK & 4x4 CONVERSIONS"
[2]: https://www.automobile-catalog.com/car/1980/2145065/nissan_cedric_4door_sedan_280e_brougham.html?utm_source=chatgpt.com "1980 Nissan Cedric 4Door Sedan 280E Brougham Specs Review (106.5 kW / 145 PS / 143 hp) (for Japan )"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
更新点

* 闭合 Expert、Traveller、Vivaro C、Zafira Life 共 6 个 4×4 Ktype。
* Dangel 资料确认 Expert/Traveller 2.0 BlueHDi 120/150 覆盖 Compact、Standard、Long；Traveller 4×4 同样提供三种长度。([Dangel Shop][1])
* Vivaro 4×4 覆盖三种车长；1.5 柴油分支按 S、M 两种既有外廓关联，2.0 柴油按 S、M、L 三种既有外廓关联。([Stellantis Media][2])
* Dangel 的额外悬架升高属于独立选装，输入 Ktype 未指定该选项；本轮仅关联基础 4×4 外廓，不新增推测性升高分支。([Dangel Shop][3])
* 本轮全部复用既有尺寸组，未新建或修改尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：86
* READY 映射行：122
* PENDING 输入 Ktype：14
* 当前已引用尺寸组：77
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139348_compact	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact短车身4×4厢式车分支。	READY
139348_standard	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard中车身4×4厢式车分支。	READY
139348_long	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long长车身4×4厢式车分支。	READY
139354_compact	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact短车身4×4厢式车分支。	READY
139354_standard	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard中车身4×4厢式车分支。	READY
139354_long	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long长车身4×4厢式车分支。	READY
139367_compact	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact短车身4×4乘用分支。	READY
139367_standard	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard中车身4×4乘用分支。	READY
139367_long	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long长车身4×4乘用分支。	READY
139376_s	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短车身4×4乘用分支。	READY
139376_m	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M中车身4×4乘用分支。	READY
139376_l	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L长车身4×4乘用分支。	READY
139378_s	139378	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	1.5柴油S短车身4×4厢式车分支。	READY
139378_m	139378	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	1.5柴油M中车身4×4厢式车分支。	READY
139379_s	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	2.0柴油S短车身4×4厢式车分支。	READY
139379_m	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	2.0柴油M中车身4×4厢式车分支。	READY
139379_l	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	HIGH	2.0柴油L长车身4×4厢式车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 闭合 Berlingo、Partner、Combo K9 的 M/XL、Van/MPV 4×4 分支。
2. 处理 Peugeot Boxer Bus 与四个 Boxer 4×4 Ktype 的 L1H1—L4H3 分支。
3. 最后处理 Ford Transit Bus、Mercedes-Benz Sprinter Classic 及旧款 Partner 的多轴距、车顶边界。

推进信号：CONTINUE

[1]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf?utm_source=chatgpt.com "Peugeot Expert/Traveller"
[2]: https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb?utm_source=chatgpt.com "Geländewagen: Opel Combo Cargo und Opel Vivaro mit Allradantrieb | Opel | Stellantis Media"
[3]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/01%20P%20GEN%2000%20EN%202019%2002_Peugeot%20Price%20list.pdf?utm_source=chatgpt.com "PRICE LIST - Trek 2WD & 4X4 conversions"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
更新点

* 闭合 Opel Combo 1.5 D Allrad，按 K9 平台 M、XL 两种 Dangel 4×4 厢式车外廓拆分。官方规格列明 4×4 车型覆盖 L1/L2，车宽不含后视镜为 1848 mm，两种长度分别为 4403、4753 mm，4×4 对应外部高度取 1860 mm。
* 闭合 Peugeot Partner 1.6 HDi 92。该动力属于 Partner II B9，输入合并车身类型按 Van L1、Van L2、标准 MPV、Outdoor MPV 四个既有物理分支关联，不重复输出缓存尺寸组。([Stellantis Media][1])
* 本轮新增 6 行 READY 映射，首次创建 2 个尺寸组，未修改已有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：88
* READY 映射行：128
* PENDING 输入 Ktype：12
* 当前已引用尺寸组：83
* 本轮首次创建或修正尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139377_m	139377	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-4X4-01	HIGH	M短车身Dangel 4×4厢式车分支。	READY
139377_xl	139377	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-4X4-01	HIGH	XL长车身Dangel 4×4厢式车分支。	READY
139492_van_l1	139492	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1短车身厢式车分支。	READY
139492_van_l2	139492	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2长车身厢式车分支。	READY
139492_mpv_standard	139492	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度五门乘用分支。	READY
139492_mpv_outdoor	139492	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor升高五门乘用分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-COMBO-E-K9-VAN-M-4X4-01	4403	1848	1860	Vauxhall Combo Cargo Model Year 2021.5 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-OPEL-COMBO-E-K9-VAN-XL-4X4-01	4753	1848	1860	Vauxhall Combo Cargo Model Year 2021.5 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
```

下一步优先处理

1. 闭合 Peugeot Partner 与 Citroën Berlingo K9 Dangel 4×4，区分 M/XL、标准 4×4 与 Plus 升高外廓。
2. 闭合 Citroën SpaceTourer 4×4 的 XS/M/XL 高度分支。
3. 集中处理 Peugeot Boxer、Ford Transit Bus 与 Mercedes-Benz Sprinter Classic 的多轴距、多车顶分支。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/de-de/peugeot/press/peugeot-partner-ab-sofort-noch-sparsamer-und-umweltfreundlicher?utm_source=chatgpt.com "Peugeot Partner - Ab sofort noch sparsamer und ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
更新点

* 闭合 Citroën Berlingo 与 Peugeot Partner 的 K9 平台 4×4 Ktype。Dangel 资料将对应 1.5 BlueHDi 130 转换限定为 Van/Crew Cab，乘用车或 MPV 版本不适用，因此各自只拆分短、长厢式车分支。([Dangel Shop][1])
* K9 车身按短版 4403 mm、长版 4753 mm、不含后视镜宽度 1848 mm、4×4 外廓高度 1860 mm 首次建组；同平台官方尺寸图明确区分 1848 mm 不含后视镜与 2107 mm 含后视镜口径。
* Citroën SpaceTourer 4×4 按 XS、M、XL 三种车长关联已闭合的改款前 MPV 尺寸组，不重复输出缓存尺寸。官方资料确认该 4×4 车型覆盖三种车身长度。([Stellantis Media][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：91
* READY 映射行：135
* PENDING 输入 Ktype：9
* 当前已引用尺寸组：90
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139338_m	139338	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-4X4-01	MEDIUM	M短车身Dangel 4×4厢式车分支。	READY
139338_xl	139338	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-4X4-01	MEDIUM	XL长车身Dangel 4×4厢式车分支。	READY
139344_xs	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS短车身4×4乘用分支。	READY
139344_m	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中车身4×4乘用分支。	READY
139344_xl	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长车身4×4乘用分支。	READY
139347_l1	139347	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-4X4-01	MEDIUM	L1短车身Dangel 4×4厢式车分支。	READY
139347_l2	139347	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-4X4-01	MEDIUM	L2长车身Dangel 4×4厢式车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-III-K9-VAN-M-4X4-01	4403	1848	1860	Dangel Citroën Berlingo 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/L_V37C4_0119_01_Leaflet%20Berlingo%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-4X4-01	4753	1848	1860	Dangel Citroën Berlingo 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/L_V37C4_0119_01_Leaflet%20Berlingo%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-4X4-01	4403	1848	1860	Dangel Peugeot Partner 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/L_V37P4_0119_01_Leaflet%20Partner%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-4X4-01	4753	1848	1860	Dangel Peugeot Partner 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/L_V37P4_0119_01_Leaflet%20Partner%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
```

下一步优先处理

1. 集中闭合 Peugeot Boxer Bus 及四个 Boxer Dangel 4×4 Ktype，按 L1H1 至 L4H3 分支关联既有尺寸组。
2. 处理 Ford Transit V363 Bus 的长度、车顶和后驱分支。
3. 最后闭合 Mercedes-Benz Sprinter Classic 3.5-T 与 4.6-T 的厢式车外廓。

推进信号：CONTINUE

[1]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/01%20P%20GEN%2000%20EN%202019%2002_Peugeot%20Price%20list.pdf?utm_source=chatgpt.com "PRICE LIST - Trek 2WD & 4X4 conversions"
[2]: https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer-4x4-e-concept-living-the-adventure-with-style?utm_source=chatgpt.com "CITROËN SPACETOURER 4X4 Ë CONCEPT: LIVING THE ..."


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
更新点

* 闭合 Peugeot Boxer Bus 与四个 Boxer Dangel 4×4 Ktype。Bus 按 6 种乘用/窗口车外廓复用既有 Boxer 尺寸组；4×4 按相同 6 种车身规格首次创建独立升高尺寸组。生产版 Dangel 基础升高按 20 mm 落盘，未采用概念车的特殊升高参数。([Charters Peugeot][1])
* 闭合 Ford Transit V363 Bus 两个 Ktype，分别拆分 L2H2、L3H2、L3H3 和 L4H3 DRW 后驱 Minibus 外廓。
* 闭合 Mercedes-Benz Sprinter Classic 3.5-T、4.6-T；3.5-T 拆分 L1/L2，4.6-T 关联 L2 外廓。([Дром][2])
* 本轮新增 41 行 READY 映射，首次创建 12 个尺寸组；全部输入 Ktype 已完成数据闭合。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：176
* PENDING 输入 Ktype：0
* 当前已引用尺寸组：108
* 本轮首次创建尺寸组：12
* 数据处理阶段已完成；不再进行外部检索。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139329_l1h1	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	MEDIUM	L1H1乘用/窗口车外廓分支。	READY
139329_l2h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	MEDIUM	L2H2乘用/窗口车外廓分支。	READY
139329_l3h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	MEDIUM	L3H2乘用/窗口车外廓分支。	READY
139329_l3h3	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	MEDIUM	L3H3高顶乘用/窗口车外廓分支。	READY
139329_l4h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	MEDIUM	L4H2乘用/窗口车外廓分支。	READY
139329_l4h3	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	MEDIUM	L4H3高顶乘用/窗口车外廓分支。	READY
139362_l1h1	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139362_l2h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139362_l3h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139362_l3h3	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139362_l4h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139362_l4h3	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139364_l1h1	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139364_l2h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139364_l3h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139364_l3h3	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139364_l4h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139364_l4h3	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139365_l1h1	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139365_l2h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139365_l3h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139365_l3h3	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139365_l4h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139365_l4h3	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139366_l1h1	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139366_l2h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139366_l3h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139366_l3h3	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139366_l4h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139366_l4h3	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139397_l1	139397	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	MEDIUM	3.5-T L1厢式车外廓。	READY
139397_l2	139397	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	MEDIUM	3.5-T L2厢式车外廓。	READY
139398	139398	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	MEDIUM	4.6-T L2厢式车外廓。	READY
139643_l2h2	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	HIGH	L2H2后驱Minibus外廓。	READY
139643_l3h2	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	HIGH	L3H2后驱Minibus外廓。	READY
139643_l3h3	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	HIGH	L3H3后驱高顶Minibus外廓。	READY
139643_l4h3_drw	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	HIGH	L4H3后驱双后轮Minibus外廓。	READY
139644_l2h2	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	HIGH	L2H2后驱Minibus外廓。	READY
139644_l3h2	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	HIGH	L3H2后驱Minibus外廓。	READY
139644_l3h3	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	HIGH	L3H3后驱高顶Minibus外廓。	READY
139644_l4h3_drw	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	HIGH	L4H3后驱双后轮Minibus外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-III-4X4-L1H1-01	4963	2050	2274	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L2H2-01	5413	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L3H2-01	5998	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L3H3-01	5998	2050	2780	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L4H2-01	6363	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L4H3-01	6363	2050	2780	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	5640	1933	2595	Drom Mercedes-Benz Sprinter Classic dimensions catalogue	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	6590	1933	2610	Drom Mercedes-Benz Sprinter Classic dimensions catalogue	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/
EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	5531	2059	2484	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	5981	2059	2528	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	5981	2059	2764	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	6704	2126	2757	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
```

下一步优先处理

1. 仅执行一次轻量机械收尾：核对两张完整表的固定表头、唯一键、映射引用闭合、尺寸与来源非空。
2. 下一轮直接输出两张最终完整 TSV、两个指定 sandbox 下载链接和 `推进信号：COMPLETE`，不再检索车型或来源。

推进信号：CONTINUE

[1]: https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf "Boxer MYD0 July 19 v3.1"
[2]: https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/?utm_source=chatgpt.com "Размеры Мерседес Спринтер Классик и вес. Какие габариты Mercedes-Benz Sprinter Classic?"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4801-4900_ktype_dimension_mapping_final.tsv
- all_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已完成一次轻量机械收尾。
* Ktype 映射表严格为 10 列，覆盖 100 个输入 Ktype，共 176 个 READY 映射。
* DIMENSION_GROUP 表严格为 6 列，共 108 个唯一尺寸组。
* `id` 与 `DIMENSION_GROUP_ID` 均无重复；所有映射引用闭合，无孤立尺寸组。
* 长宽高均为正整数，尺寸来源和 URL 均非空。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：176
* PENDING：0
* DIMENSION_GROUP：108
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139329_l1h1	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	MEDIUM	L1H1乘用/窗口车外廓分支。	READY
139329_l2h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	MEDIUM	L2H2乘用/窗口车外廓分支。	READY
139329_l3h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	MEDIUM	L3H2乘用/窗口车外廓分支。	READY
139329_l3h3	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	MEDIUM	L3H3高顶乘用/窗口车外廓分支。	READY
139329_l4h2	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	MEDIUM	L4H2乘用/窗口车外廓分支。	READY
139329_l4h3	139329	MPV	Boxer III facelift			EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	MEDIUM	L4H3高顶乘用/窗口车外廓分支。	READY
139330	139330	Coupe	Corvette VIII	C8	2	EU-CHEVROLET-CORVETTE-C8-STINGRAY-COUPE-01	HIGH	C8 Stingray双门硬顶外廓。	READY
139332	139332	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前标准SUV外廓。	READY
139333	139333	SUV	X6 III	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前标准SUV外廓。	READY
139338_m	139338	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-4X4-01	MEDIUM	M短车身Dangel 4×4厢式车分支。	READY
139338_xl	139338	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-4X4-01	MEDIUM	XL长车身Dangel 4×4厢式车分支。	READY
139339_xs_low	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS普通高度4×4厢式车分支。	READY
139339_xs_high	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS升高4×4厢式车分支。	READY
139339_m_low	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M普通高度4×4厢式车分支。	READY
139339_m_high	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M升高4×4厢式车分支。	READY
139339_xl	139339	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL长车身4×4厢式车分支。	READY
139341_xs_low	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS普通高度4×4厢式车分支。	READY
139341_xs_high	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS升高4×4厢式车分支。	READY
139341_m_low	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M普通高度4×4厢式车分支。	READY
139341_m_high	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M升高4×4厢式车分支。	READY
139341_xl	139341	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL长车身4×4厢式车分支。	READY
139344_xs	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS短车身4×4乘用分支。	READY
139344_m	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中车身4×4乘用分支。	READY
139344_xl	139344	MPV	SpaceTourer I	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长车身4×4乘用分支。	READY
139347_l1	139347	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-4X4-01	MEDIUM	L1短车身Dangel 4×4厢式车分支。	READY
139347_l2	139347	Van	Partner III	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-4X4-01	MEDIUM	L2长车身Dangel 4×4厢式车分支。	READY
139348_compact	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact短车身4×4厢式车分支。	READY
139348_standard	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard中车身4×4厢式车分支。	READY
139348_long	139348	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long长车身4×4厢式车分支。	READY
139354_compact	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	HIGH	Compact短车身4×4厢式车分支。	READY
139354_standard	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	HIGH	Standard中车身4×4厢式车分支。	READY
139354_long	139354	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	HIGH	Long长车身4×4厢式车分支。	READY
139362_l1h1	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139362_l2h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139362_l3h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139362_l3h3	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139362_l4h2	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139362_l4h3	139362	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139364_l1h1	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139364_l2h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139364_l3h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139364_l3h3	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139364_l4h2	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139364_l4h3	139364	Van	Boxer III			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139365_l1h1	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139365_l2h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139365_l3h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139365_l3h3	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139365_l4h2	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139365_l4h3	139365	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139366_l1h1	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L1H1-01	MEDIUM	Dangel 4×4 L1H1外廓分支。	READY
139366_l2h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L2H2-01	MEDIUM	Dangel 4×4 L2H2外廓分支。	READY
139366_l3h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H2-01	MEDIUM	Dangel 4×4 L3H2外廓分支。	READY
139366_l3h3	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L3H3-01	MEDIUM	Dangel 4×4 L3H3高顶外廓分支。	READY
139366_l4h2	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H2-01	MEDIUM	Dangel 4×4 L4H2外廓分支。	READY
139366_l4h3	139366	Van	Boxer III facelift			EU-PEUGEOT-BOXER-III-4X4-L4H3-01	MEDIUM	Dangel 4×4 L4H3高顶外廓分支。	READY
139367_compact	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact短车身4×4乘用分支。	READY
139367_standard	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard中车身4×4乘用分支。	READY
139367_long	139367	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long长车身4×4乘用分支。	READY
139376_s	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	S短车身4×4乘用分支。	READY
139376_m	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	M中车身4×4乘用分支。	READY
139376_l	139376	MPV	Zafira Life I	K0	5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	L长车身4×4乘用分支。	READY
139377_m	139377	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-4X4-01	HIGH	M短车身Dangel 4×4厢式车分支。	READY
139377_xl	139377	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-4X4-01	HIGH	XL长车身Dangel 4×4厢式车分支。	READY
139378_s	139378	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	1.5柴油S短车身4×4厢式车分支。	READY
139378_m	139378	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	1.5柴油M中车身4×4厢式车分支。	READY
139379_s	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-S-01	HIGH	2.0柴油S短车身4×4厢式车分支。	READY
139379_m	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-01	HIGH	2.0柴油M中车身4×4厢式车分支。	READY
139379_l	139379	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-01	HIGH	2.0柴油L长车身4×4厢式车分支。	READY
139397_l1	139397	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	MEDIUM	3.5-T L1厢式车外廓。	READY
139397_l2	139397	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	MEDIUM	3.5-T L2厢式车外廓。	READY
139398	139398	Van	Sprinter Classic	W909		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	MEDIUM	4.6-T L2厢式车外廓。	READY
139400_l1h1	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	FWD L1H1厢式车分支。	READY
139400_l1h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	FWD L1H2厢式车分支。	READY
139400_l2h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	FWD L2H2厢式车分支。	READY
139400_l2h3	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	FWD L2H3厢式车分支。	READY
139400_l3h2	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	FWD L3H2厢式车分支。	READY
139400_l3h3	139400	Van	NV400 I	X62		EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	FWD L3H3厢式车分支。	READY
139401_single_l2h1	139401	Pickup	NV400 I	X62	2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	HIGH	FWD单排L2H1底盘分支。	READY
139401_single_l3h1	139401	Pickup	NV400 I	X62	2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	FWD单排L3H1底盘分支。	READY
139401_double_l3h1	139401	Pickup	NV400 I	X62	4	EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	HIGH	FWD双排L3H1底盘分支。	READY
139431_compact	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact短车身分支。	READY
139431_medium	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium中车身分支。	READY
139431_long	139431	MPV	Proace Verso II		5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	HIGH	Long长车身分支。	READY
139460	139460	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	L494改款后标准SUV外廓。	READY
139467	139467	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	G20改款前xDrive轿车外廓。	READY
139469	139469	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	G21 330e Touring五门外廓。	READY
139470	139470	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	HIGH	M340d xDrive专用M Performance轿车外廓。	READY
139471	139471	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340d与既有G21 M Performance xDrive旅行车共用外廓。	READY
139473_swb	139473	MPV	Transporter T6.1 / Caravelle			EU-VW-CARAVELLE-T6-1-MPV-SWB-01	MEDIUM	短轴距乘用型车身分支。	READY
139473_lwb	139473	MPV	Transporter T6.1 / Caravelle			EU-VW-CARAVELLE-T6-1-MPV-LWB-01	MEDIUM	长轴距乘用型车身分支。	READY
139481	139481	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139482	139482	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139483	139483	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340i xDrive使用G21 M Performance旅行车外廓。	READY
139484	139484	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139485	139485	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	轻混动力不改变G21后驱Touring外廓。	READY
139486	139486	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	Kasten/Kombi对应G21 xDrive Touring外廓。	READY
139487	139487	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	轻混动力不改变G21 xDrive Touring外廓。	READY
139488	139488	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH	Kasten/Kombi对应G21后驱Touring外廓。	READY
139489	139489	Wagon	3 Series VII Touring	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH	Kasten/Kombi对应G21 xDrive Touring外廓。	READY
139490	139490	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	Kasten/SUV对应G05改款前标准SUV外廓。	READY
139491	139491	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	Kasten/SUV对应G05改款前标准SUV外廓。	READY
139492_van_l1	139492	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1短车身厢式车分支。	READY
139492_van_l2	139492	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2长车身厢式车分支。	READY
139492_mpv_standard	139492	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度五门乘用分支。	READY
139492_mpv_outdoor	139492	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor升高五门乘用分支。	READY
139502	139502	SUV	Grandland X I	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	A18标准SUV外廓。	READY
139504	139504	SUV	HS I		5	EU-MG-HS-I-SUV-01	HIGH	HS I五门SUV外廓。	READY
139507	139507	Convertible	500 I	312		EU-FIAT-500-I-312-CONVERTIBLE-FACELIFT-01	HIGH	500C改款后敞篷外廓。	READY
139533	139533	Convertible	Santana 300		3	EU-SANTANA-300-CONVERTIBLE-3D-01	MEDIUM	三门开放式越野车外廓。	READY
139607	139607	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	P300e使用L551五门SUV外廓。	READY
139640	139640	SUV	ZS I		5	EU-MG-ZS-I-EV-SUV-01	HIGH	ZS EV初期型五门SUV外廓。	READY
139643_l2h2	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	HIGH	L2H2后驱Minibus外廓。	READY
139643_l3h2	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	HIGH	L3H2后驱Minibus外廓。	READY
139643_l3h3	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	HIGH	L3H3后驱高顶Minibus外廓。	READY
139643_l4h3_drw	139643	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	HIGH	L4H3后驱双后轮Minibus外廓。	READY
139644_l2h2	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	HIGH	L2H2后驱Minibus外廓。	READY
139644_l3h2	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	HIGH	L3H2后驱Minibus外廓。	READY
139644_l3h3	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	HIGH	L3H3后驱高顶Minibus外廓。	READY
139644_l4h3_drw	139644	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	HIGH	L4H3后驱双后轮Minibus外廓。	READY
139648	139648	Wagon	A4 allroad B9	B9	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH	B9 allroad旅行车外廓。	READY
139649	139649	SUV	X3 III	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	G01 M40i专用外廓。	READY
139650	139650	SUV	X3 III	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	Kasten/SUV与同版本G01 M40i共用外廓。	READY
139651	139651	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-GTA-SEDAN-01	HIGH	GTA宽体四门外廓。	READY
139652	139652	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139653	139653	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139654	139654	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139655	139655	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139656	139656	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139657	139657	Hatchback	Ypsilon III		5	EU-LANCIA-YPSILON-III-HATCHBACK-FACELIFT-01	MEDIUM	改款后五门车身；官方厘米尺寸已换算为毫米。	READY
139658	139658	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139659	139659	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247改款前五门SUV外廓。	READY
139672	139672	SUV	DBX I		5	EU-ASTON-MARTIN-DBX-I-SUV-01	HIGH	初代DBX五门SUV外廓。	READY
139678	139678	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	P300e对应L550改款后五门外廓。	READY
139679	139679	Hatchback	Swift VI	A2L	5	EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	HIGH	输入代次命名归并至A2L Swift Sport五门外廓。	READY
139680	139680	Coupe	2 Series Gran Coupe I	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱216d对应F44四门Gran Coupe外廓。	READY
139690	139690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	CD五门掀背标准外廓。	READY
139693	139693	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	轻混柴油动力不改变CD五门掀背外廓。	READY
139694	139694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	轻混柴油动力不改变CD五门掀背外廓。	READY
139695	139695	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon标准外廓。	READY
139696	139696	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	CD Sportswagon标准外廓。	READY
139697	139697	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD ProCeed shooting-brake外廓。	READY
139698	139698	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD XCeed改款前外廓。	READY
139699	139699	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-PREFL-01	HIGH	CD XCeed改款前外廓。	READY
139714	139714	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139715	139715	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139716	139716	Hatchback	A3 III	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH	生产起始时间对应8V改款后Sportback五门外廓。	READY
139717	139717	Coupe	718	982	2	EU-PORSCHE-718-982-CAYMAN-GTS-4-0-COUPE-01	HIGH	982 GTS 4.0双门硬顶外廓。	READY
139725	139725	Convertible	718	982	2	EU-PORSCHE-718-982-BOXSTER-GTS-4-0-CONVERTIBLE-01	HIGH	982 GTS 4.0双门敞篷外廓。	READY
139734_std	139734	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139734_fr	139734	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139736_std	139736	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139736_fr	139736	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139737_std	139737	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139737_fr	139737	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139738_std	139738	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	标准悬架五门外廓。	READY
139738_fr	139738	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低车身五门外廓。	READY
139744_std	139744	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架Sportstourer外廓。	READY
139744_fr	139744	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低车身Sportstourer外廓。	READY
139745_std	139745	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架Sportstourer外廓。	READY
139745_fr	139745	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低车身Sportstourer外廓。	READY
139749	139749	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背外廓。	READY
139764	139764	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139765	139765	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139766	139766	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX五门掀背标准外廓。	READY
139767	139767	Pickup	H100 / Porter II	HR	2	EU-HYUNDAI-H100-HR-CHASSIS-CAB-01	HIGH	HR标准驾驶室底盘外廓。	READY
139779_prefl	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-PREFL-01	HIGH	430改款前四门轿车外廓。	READY
139779_facelift	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-FACELIFT-01	HIGH	430改款后四门轿车外廓。	READY
139781	139781	SUV	T77 I		5	EU-BESTUNE-T77-I-SUV-01	HIGH	T77 Pro五门SUV外廓。	READY
139786	139786	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4前驱五门SUV外廓。	READY
139787	139787	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4四驱五门SUV外廓。	READY
139788	139788	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-ROADSTER-01	HIGH	2020款双门Roadster外廓。	READY
139795	139795	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B4轻混动力不改变S90 II轿车外廓。	READY
139796	139796	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B5轻混动力不改变S90 II轿车外廓。	READY
139797	139797	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	B6 AWD轻混动力不改变S90 II轿车外廓。	READY
139799	139799	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	B4轻混动力不改变V90 II旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4801-4900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760	Peugeot Boxer July 2019 official specification brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-CHEVROLET-CORVETTE-C8-STINGRAY-COUPE-01	4630	1934	1234	Chevrolet New Corvette Stingray official technical data	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/next-gen-corvette/Chevrolet-Corvette-Stingray-Technical-Data-EN-190731.pdf
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 G05 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0282949EN/the-new-bmw-x5
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW X6 G06 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0295947EN/the-new-bmw-x6
EU-CITROEN-BERLINGO-III-K9-VAN-M-4X4-01	4403	1848	1860	Dangel Citroën Berlingo 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/L_V37C4_0119_01_Leaflet%20Berlingo%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-4X4-01	4753	1848	1860	Dangel Citroën Berlingo 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/L_V37C4_0119_01_Leaflet%20Berlingo%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910	Citroën Jumpy official dimensions; Dangel Citroën 4x4 price list	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/jumpy.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950	Citroën Jumpy official dimensions; Dangel Citroën 4x4 price list	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/jumpy.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899	Citroën Jumpy official dimensions; Dangel Citroën 4x4 price list	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/jumpy.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935	Citroën Jumpy official dimensions; Dangel Citroën 4x4 price list	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/jumpy.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940	Citroën Jumpy official dimensions; Dangel Citroën 4x4 price list	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/jumpy.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Citroen/Dangel%20Pricelist%20Citro%C3%ABn%2015_06_2023_EngZ1.pdf
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905	Citroën SpaceTourer official dimensions; Citroën SpaceTourer 4x4 official press material	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/spacetourer.pdf;https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer-4x4-e-concept-living-the-adventure-with-style
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890	Citroën SpaceTourer official dimensions; Citroën SpaceTourer 4x4 official press material	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/spacetourer.pdf;https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer-4x4-e-concept-living-the-adventure-with-style
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890	Citroën SpaceTourer official dimensions; Citroën SpaceTourer 4x4 official press material	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/spacetourer.pdf;https://www.media.stellantis.com/em-en/citroen/press/citroen-spacetourer-4x4-e-concept-living-the-adventure-with-style
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-4X4-01	4403	1848	1860	Dangel Peugeot Partner 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/L_V37P4_0119_01_Leaflet%20Partner%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-4X4-01	4753	1848	1860	Dangel Peugeot Partner 4x4 official leaflet; Vauxhall Combo Cargo MY2021.5 official K9 dimension guide	https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/L_V37P4_0119_01_Leaflet%20Partner%204x4%20-%20ENG.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910	Peugeot Expert official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/expert.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904	Peugeot Expert official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/expert.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935	Peugeot Expert official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/expert.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-PEUGEOT-BOXER-III-4X4-L1H1-01	4963	2050	2274	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L2H2-01	5413	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L3H2-01	5998	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L3H3-01	5998	2050	2780	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L4H2-01	6363	2050	2542	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-BOXER-III-4X4-L4H3-01	6363	2050	2780	Peugeot Boxer July 2019 official specification brochure; Dangel Peugeot Boxer 4x4 official leaflet	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/Peugeot%20Boxer%204x4%20new%20leaflet%2015_06_2023%20English.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905	Peugeot Traveller official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/traveller.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890	Peugeot Traveller official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/traveller.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890	Peugeot Traveller official dimensions; Dangel Peugeot Expert/Traveller 4x4 official leaflet	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/traveller.pdf;https://www.dangel.com/sites/www.dangel.fr/files/pdf/FR/Peugeot/5244B_Leaflet%20Peugeot%20V61%20-%20FR.pdf
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Opel Zafira Life official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-zafira-life-technical-data-5e8f22abcf6e9.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Opel Zafira Life official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-zafira-life-technical-data-5e8f22abcf6e9.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Opel Zafira Life official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-zafira-life-technical-data-5e8f22abcf6e9.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-OPEL-COMBO-E-K9-VAN-M-4X4-01	4403	1848	1860	Vauxhall Combo Cargo Model Year 2021.5 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-OPEL-COMBO-E-K9-VAN-XL-4X4-01	4753	1848	1860	Vauxhall Combo Cargo Model Year 2021.5 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/combo-cargo/price-guides/Combo_Cargo_Spec_ePG_21_January_2021_Library-1611227052.pdf
EU-OPEL-VIVARO-C-K0-VAN-S-01	4609	1920	1905	Opel Vivaro C official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-vivaro-technical-data-5d0b721f45de2.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-OPEL-VIVARO-C-K0-VAN-M-01	4959	1920	1895	Opel Vivaro C official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-vivaro-technical-data-5d0b721f45de2.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-OPEL-VIVARO-C-K0-VAN-L-01	5309	1920	1935	Opel Vivaro C official technical data; Opel Dangel all-wheel-drive press material	https://www.media.stellantis.com/uploads/em/attachment/opel-vivaro-technical-data-5d0b721f45de2.pdf;https://www.media.stellantis.com/de-de/opel/press/gelandewagen-opel-combo-cargo-und-opel-vivaro-mit-allradantrieb
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	5640	1933	2595	Drom Mercedes-Benz Sprinter Classic dimensions catalogue	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	6590	1933	2610	Drom Mercedes-Benz Sprinter Classic dimensions catalogue	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	5048	2070	2500	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	5548	2070	2749	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	6198	2070	2488	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	6198	2070	2744	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	5549	2070	2265	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	6199	2070	2258	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	6199	2070	2263	Nissan NV400 official brochure and dimensions	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/nv400-brochure.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905	Toyota Proace Verso official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/10/Toyota-Proace-Verso-2019-UK.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890	Toyota Proace Verso official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/10/Toyota-Proace-Verso-2019-UK.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890	Toyota Proace Verso official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/10/Toyota-Proace-Verso-2019-UK.pdf
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Land Rover Range Rover Sport official technical specification	https://media.landrover.com/en-us/news/2017/10/new-range-rover-sport-technology-enhanced-performance-suv
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan official specifications 02/2020	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442	BMW 330e Touring official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0325532EN/471539
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440	BMW 3 Series Sedan official specifications 02/2020	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440	BMW 3 Series Touring official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-VW-CARAVELLE-T6-1-MPV-SWB-01	4904	1904	1970	Volkswagen Commercial Vehicles Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-VW-CARAVELLE-T6-1-MPV-LWB-01	5304	1904	1990	Volkswagen Commercial Vehicles Caravelle 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	BMW 3 Series Touring official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445	BMW 3 Series Touring official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0305706EN/609715
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828	Peugeot Partner B9 official specifications	https://www.media.stellantis.com/de-de/peugeot/press/peugeot-partner-ab-sofort-noch-sparsamer-und-umweltfreundlicher
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner B9 official specifications	https://www.media.stellantis.com/de-de/peugeot/press/peugeot-partner-ab-sofort-noch-sparsamer-und-umweltfreundlicher
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801	Peugeot Partner B9 official specifications	https://www.media.stellantis.com/de-de/peugeot/press/peugeot-partner-ab-sofort-noch-sparsamer-und-umweltfreundlicher
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862	Peugeot Partner B9 official specifications	https://www.media.stellantis.com/de-de/peugeot/press/peugeot-partner-ab-sofort-noch-sparsamer-und-umweltfreundlicher
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Opel Grandland X official technical data	https://www.media.stellantis.com/uploads/em/attachment/opel-grandland-x-technical-data-5c8a36786351f.pdf
EU-MG-HS-I-SUV-01	4574	1876	1685	MG HS Owner Manual	https://www.mg.co.uk/sites/default/files/2021-11/MG%20HS%20Owner%20Manual.pdf
EU-FIAT-500-I-312-CONVERTIBLE-FACELIFT-01	3571	1627	1488	Fiat 500 and 500C official technical specifications January 2020	https://www.media.stellantis.com/uploads/fr/attachment/fiat500_fichetarifs_janvier2020-5e3965a67fbbc.pdf
EU-SANTANA-300-CONVERTIBLE-3D-01	3660	1630	1665	Automobile-Catalog Santana 300 specifications; Auto-Data Santana 300 1.6 HDi 4WD specifications	https://www.automobile-catalog.com/car/2006/3043100/santana_300_berline.html;https://www.auto-data.net/en/santana-300-1.6-hdi-90hp-4wd-55590
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Land Rover Range Rover Evoque official technical specification	https://media.landrover.com/en-us/news/2018/11/new-range-rover-evoque-refined-evolution
EU-MG-ZS-I-EV-SUV-01	4314	1809	1644	MG Motor Europe MG ZS EV official technical specifications	https://news.mgmotor.eu/press/mg-zs-ev-the-first-truly-affordable-electric-b-segment-suv/
EU-FORD-TRANSIT-V363-MINIBUS-L2H2-RWD-01	5531	2059	2484	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L3H2-RWD-01	5981	2059	2528	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L3H3-RWD-01	5981	2059	2764	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-FORD-TRANSIT-V363-MINIBUS-L4H3-RWD-DRW-01	6704	2126	2757	Ford Transit Minibus 25.5MY official brochure; Ford New Transit Minibus 2020 brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://xr793.com/wp-content/uploads/2020/09/2020-Ford-New-Transit-Minibus-UK.pdf
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493	Audi A4 allroad quattro official technical data	https://www.audi-mediacenter.com/en/audi-a4-allroad-quattro-2019-12018/download
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676	BMW X3 M40i official technical data	https://www.press.bmwgroup.com/global/article/detail/T0274411EN/the-new-bmw-x3
EU-ALFA-ROMEO-GIULIA-952-GTA-SEDAN-01	4654	1923	1445	Alfa Romeo Japan Giulia GTA/GTAm official European reference specifications	https://alfaromeo-jp.com/giulia/limited/gta/spec/
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	Mercedes-Benz GLA H247 official brochure	https://www.mercedes-benzcaribbean.com/assets/brochures/GLA_H247_ePaper_0420_02_ENG.pdf
EU-LANCIA-YPSILON-III-HATCHBACK-FACELIFT-01	3840	1680	1520	Lancia New Ypsilon official Frankfurt press material; Lancia Ypsilon Hybrid EcoChic official launch	https://www.media.stellantis.com/em-en/lancia/press/lancia-at-the-2015-frankfurt-international-motor-show;https://www.media.stellantis.com/em-en/lancia/press/lancia-ypsilon-celebrates-its-35th-anniversary-and-production-of-3-million-units-by-presenting-ypsilon-dreamers
EU-ASTON-MARTIN-DBX-I-SUV-01	5039	1998	1680	Aston Martin DBX official launch specification	https://media.astonmartin.com/aston-martin-unveils-dbx-an-suv-with-the-soul-of-a-sports-car-3
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	4597	1904	1727	Land Rover Discovery Sport official technical specification	https://media.landrover.com/en-us/news/2019/05/new-discovery-sport-enhanced-versatility-and-intuitive-technology
EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	3890	1735	1495	Suzuki Swift Sport Hybrid official specifications	https://media.suzuki.co.uk/en-gb/releases/663
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW 2 Series Gran Coupe official technical data	https://www.press.bmwgroup.com/global/article/detail/T0300700EN/the-first-ever-bmw-2-series-gran-coupe
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Kia Europe Ceed family official specifications	https://press.kia.com/eu/en/home/media-resouces/press-kits/products/2018/the-new-kia-ceed.html
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Europe Ceed family official specifications	https://press.kia.com/eu/en/home/media-resouces/press-kits/products/2018/the-new-kia-ceed.html
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Kia Europe Ceed family official specifications	https://press.kia.com/eu/en/home/media-resouces/press-kits/products/2018/the-new-kia-ceed.html
EU-KIA-XCEED-I-CD-SUV-PREFL-01	4395	1826	1495	Kia Europe Ceed family official specifications	https://press.kia.com/eu/en/home/media-resouces/press-kits/products/2018/the-new-kia-ceed.html
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Audi A3 Sportback 8V facelift official technical data	https://www.audi-mediacenter.com/en/audi-a3-sportback-2016-6045/download
EU-PORSCHE-718-982-CAYMAN-GTS-4-0-COUPE-01	4405	1801	1276	Porsche 718 Boxster GTS 4.0 and 718 Cayman GTS 4.0 official technical data	https://newsroom.porsche.com/dam/jcr%3A5d1b4e09-a439-4c4f-880c-a0faae55c450/718%20Boxster%20GTS%204.0%20and%20718%20Cayman%20GTS%204.0%20US%20technical%20specifications_.pdf
EU-PORSCHE-718-982-BOXSTER-GTS-4-0-CONVERTIBLE-01	4391	1801	1262	Porsche 718 Boxster GTS 4.0 and 718 Cayman GTS 4.0 official technical data	https://newsroom.porsche.com/dam/jcr%3A5d1b4e09-a439-4c4f-880c-a0faae55c450/718%20Boxster%20GTS%204.0%20and%20718%20Cayman%20GTS%204.0%20US%20technical%20specifications_.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1799	1442	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	SEAT New Leon official technical brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/leon/ennewletsmy21w48.pdf
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456	Volkswagen Golf VIII official technical data	https://www.volkswagen-newsroom.com/en/the-new-golf-2019-5460/download
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470	Škoda Octavia official petrol technical specifications July 2020	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-petrol-en.pdf
EU-HYUNDAI-H100-HR-CHASSIS-CAB-01	4850	1740	1970	Hyundai H-100 official brochure	https://www.hyundai.com/content/dam/hyundai/ph/en/data/marketing/brochure/product/h100/H-100_FLYERv2.pdf
EU-NISSAN-CEDRIC-430-SEDAN-PREFL-01	4825	1715	1430	Automobile-Catalog 1980 Nissan Cedric 280E Brougham specifications	https://www.automobile-catalog.com/car/1980/2145065/nissan_cedric_4door_sedan_280e_brougham.html
EU-NISSAN-CEDRIC-430-SEDAN-FACELIFT-01	4885	1715	1430	Automobile-Catalog 1981 Nissan Cedric 280E Brougham specifications	https://www.automobile-catalog.com/car/1981/2146025/nissan_cedric_4door_sedan_280e_brougham.html
EU-BESTUNE-T77-I-SUV-01	4525	1845	1615	Bestune T77 official brochure	https://www.bestune.bh/brochure/bestune-t77.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1695	Kia Europe New Sorento official press kit	https://press.kia.com/content/dam/kiapress/EU/Pressreleases/2020/kia_pressrelease_2020_sorento/Press%20kit%20-%20New%20Kia%20Sorento%20-%2018%20Mar%202020%20v3.doc
EU-ASTON-MARTIN-VANTAGE-2018-ROADSTER-01	4465	1942	1273	Aston Martin Vantage Roadster official launch; Aston Martin Vantage Roadster specification sheet	https://www.astonmartin.com/en-gb/our-world/news/2020/2/12/vantage-roadster-uncompromising-performance-meets-pure-emotion;https://www.autointernational.com.my/WebNews/Overseas/Year%202020/ASTON%20MARTIN_VANTAGE%20ROADSTER%20-%2022%20Feb%2020/VANTAGE%20ROADSTER%20SPECIFICATION.pdf
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo S90 official specifications	https://www.media.volvocars.com/global/en-gb/models/s90/2020/specifications
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo V90 official specifications	https://www.media.volvocars.com/global/en-gb/models/v90/2020/specifications
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4801-4900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5036 行）
- 累计尺寸组：dimension_groups_final.tsv（1889 行）

