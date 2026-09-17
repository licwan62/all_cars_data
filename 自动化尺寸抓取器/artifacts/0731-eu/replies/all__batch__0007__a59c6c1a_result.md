# 任务：all 第 601-700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0007__a59c6c1a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 601-700 行

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
all 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-3-G20-SEDAN-01	4709	1827	1442
EU-BMW-3-G21-WAGON-01	4709	1827	1440
EU-MERCEDES-BENZ-GLA-H247-SUV-01	4410	1834	1611
EU-MERCEDES-BENZ-GLB-X247-SUV-01	4634	1834	1658
EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	4655	1890	1644
EU-PORSCHE-911-9921-TURBO-S-CONVERTIBLE-01	4535	1900	1301
EU-PORSCHE-911-9921-TURBO-S-COUPE-01	4535	1900	1303
EU-PORSCHE-911-9971-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-9972-TARGA-4S-01	4435	1852	1300
EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	4918	1983	1696
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440
EU-SUZUKI-SWIFT-VI-A2L-HATCHBACK-SPORT-01	3890	1735	1495
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4408	1793	1858
EU-VW-CADDY-IV-ALLTRACK-VAN-SWB-01	4408	1794	1823

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Porsche	911	4	Targa	Allrad	Benzin	283	385	May 2020	Dec 2024	2026-03-01	140632
Porsche	911	4S	Targa	Allrad	Benzin	331	450	May 2020	Dec 2024	2026-03-01	140633
Skoda	E-Citigo	E IV	Schrägheck	Frontantrieb	Elektro	61	83	Sep 2019	Sep 2021	2024-03-01	140638
Maxus	Euniq 5	EV	Großraumlimousine	Frontantrieb	Elektro	130	177	May 2020	-	2026-04-01	140654
Maxus	Euniq 6	EV	SUV	Frontantrieb	Elektro	130	177	May 2020	-	2024-08-01	140660
VW	T-Cross	1.0 TSI	SUV	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	140667
Audi	90	1.8 E	Stufenheck	Frontantrieb	Benzin	82	111	Aug 1989	Aug 1991	2024-03-01	140669
Mercedes-benz	Gla	GLA 180 D	SUV	Frontantrieb	Diesel	85	116	Mar 2020	-	2024-03-01	140670
Nissan	Juke	1	SUV	Frontantrieb	Benzin	84	114	Aug 2019	-	2024-03-01	140681
Mercedes-benz	Glb	GLB 180	SUV	Frontantrieb	Benzin	100	136	Apr 2020	-	2024-03-01	140686
Mercedes-benz	Glc	300 DE 4-matic	SUV	Allrad	Diesel/Elektro	225	306	May 2020	Jun 2022	2024-03-01	140691
Mercedes-benz	Glc	300 DE 4-matic	SUV	Allrad	Diesel/Elektro	225	306	May 2020	Mar 2023	2024-03-01	140694
VW	Tiguan	1.5 TSI	SUV	Frontantrieb	Benzin	96	131	Jul 2018	Apr 2024	2025-06-01	140708
Mercedes-benz	Gle	GLE 350 DE 4-matic	SUV	Allrad	Diesel/Elektro	225	306	Nov 2019	Mar 2023	2024-03-01	140709
Mercedes-benz	Gle	GLE 350 DE 4-matic	SUV	Allrad	Diesel/Elektro	235	320	Mar 2020	Mar 2023	2024-03-01	140712
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	420	571	Mar 2020	Mar 2023	2024-03-01	140713
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Mar 2020	-	2024-03-01	140714
Casalini	M20	M20	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2018	-	2024-03-01	140718
Microcar	Due	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Dec 2019	-	2024-03-01	140721
Aixam	Roadline	0.4	Schrägheck	Frontantrieb	Diesel	4	5	Sep 2009	Jul 2012	2024-03-01	140722
Aixam	Crossover	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2018	-	2024-03-01	140723
Hyundai	I30	1.6 Crdi Hybrid 48V	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140729
Hyundai	I30	1.6 Crdi Hybrid 48V	Kombi	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140730
Hyundai	I30	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Mar 2020	-	2024-03-01	140731
Hyundai	I30	1.0 T-gdi Hybrid 48V	Kombi	Frontantrieb	Benzin/Elektro	88	120	Mar 2020	-	2024-03-01	140732
Mercedes-benz	A-Klasse	A 250 E	Stufenheck	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	-	2024-03-01	140736
Mercedes-benz	A-Klasse	A 250 E	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	-	2024-03-01	140737
Hyundai	I30	1.6 Crdi Hybrid 48V	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140738
Renault	Clio v	1.6 E-tech 140	Schrägheck	Frontantrieb	Benzin/Elektro	103	140	Mar 2020	-	2026-05-01	140751
Renault	Twizy	80	Schrägheck	Heckantrieb	Elektro	9	12	Jun 2020	-	2024-03-01	140752
Mercedes-benz	B-Klasse sports tourer	B 250 E	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Jun 2020	-	2024-03-01	140775
Mercedes-benz	Gla	AMG GLA 35 4-matic	SUV	Allrad	Benzin	225	306	Jun 2020	-	2024-03-01	140776
Mercedes-benz	Gla	AMG GLA 45 4-matic+	SUV	Allrad	Benzin	285	387	Jun 2020	-	2024-03-01	140777
Mercedes-benz	Gla	AMG GLA 45 S 4-matic+	SUV	Allrad	Benzin	310	421	Jun 2020	-	2024-03-01	140778
Mercedes-benz	E-Klasse	E 350 E	Stufenheck	Heckantrieb	Benzin/Elektro	235	320	Sep 2016	Jun 2019	2024-03-01	140787
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Stufenheck	Allrad	Diesel/Elektro	225	306	Jun 2020	Aug 2023	2024-03-01	140789
Maxus	V80	Ev80	Kasten	Frontantrieb	Elektro	92	125	Jan 2017	-	2024-03-01	140806
Maxus	V80	Ev80	Pritsche/Fahrgestell	Frontantrieb	Elektro	92	125	Jan 2017	-	2024-03-01	140807
KIA	Soul iii cargo	E-soul	Kasten/Schrägheck	Frontantrieb	Elektro	150	204	Jun 2020	-	2024-03-01	140808
Maxus	Deliver 9	2.0 D	Kasten	Heckantrieb	Diesel	120	163	Jul 2020	-	2024-03-01	140813
BMW	4	430 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	210	286	Mar 2021	-	2024-03-01	140850
Toyota	Hilux viii	2.8 D-4d 4WD	Pick-up	Allrad	Diesel	150	204	Jun 2020	-	2026-05-01	140855
BMW	4	M440 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	250	340	Mar 2021	-	2024-03-01	140856
Maxus	Edeliver 3	Electric	Kasten	Frontantrieb	Elektro	90	122	Jul 2020	-	2024-03-01	140865
Polestar	Polestar 1	Phev AWD	Coupe	Allrad	Benzin/Elektro	448	609	Mar 2018	-	2024-03-01	140883
Mini	Mini	Cooper SE	Kombi	Allrad	Benzin/Elektro	162	220	Jul 2020	-	2024-03-01	140885
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	131	178	Jul 2020	-	2024-03-01	140889
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	131	178	Jul 2020	-	2024-03-01	140890
Mercedes-benz	Glc	300 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Nov 2019	Jun 2022	2024-03-01	140891
VW	Caddy iv	ABT E-caddy	Großraumlimousine	Frontantrieb	Elektro	83	113	Apr 2020	Dec 2020	2025-06-01	140892
Mercedes-benz	Glc	F-cell	SUV	Heckantrieb	Wasserstoff	80	109	Oct 2018	Apr 2020	2024-07-01	140893
Mercedes-benz	Glc	F-cell	SUV	Heckantrieb	Wasserstoff	155	211	Oct 2018	Apr 2020	2024-03-01	140894
VW	Caddy iv	ABT E-caddy	Kasten/Großraumlimousine	Frontantrieb	Elektro	83	113	Apr 2020	Dec 2020	2025-06-01	140895
VW	Transporter t6	ABT E-transporter	Kasten	Frontantrieb	Elektro	83	113	Jan 2020	Aug 2024	2025-02-03	140896
VW	Transporter t6 / caravelle	ABT E-caravelle	Bus	Frontantrieb	Elektro	83	113	Jan 2020	Aug 2024	2025-02-03	140897
Porsche	Cayenne	4.0 GTS	SUV	Allrad	Benzin	338	460	May 2017	May 2023	2026-03-01	140905
Mclaren	720s	4	Coupe	Heckantrieb	Benzin	530	720	Feb 2019	-	2025-06-01	140906
BMW	6	630 I Mild-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	190	258	Jul 2020	-	2024-03-01	140916
BMW	6	640 I Mild-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140917
BMW	6	640 I Mild-hybrid Xdrive	Schrägheck	Allrad	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140918
BMW	6	620 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140919
BMW	6	630 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140920
BMW	6	630 D Mild-hybrid Xdrive	Schrägheck	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140921
BMW	6	640 D Mild-hybrid Xdrive	Schrägheck	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2024-03-01	140922
BMW	5	520 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	135	184	Jul 2020	Jun 2023	2024-03-01	140923
BMW	5	530 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	185	252	Jul 2020	Jun 2023	2024-03-01	140924
BMW	5	530 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	185	252	Jul 2020	Jun 2023	2024-03-01	140925
BMW	5	540 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	245	333	Jul 2020	May 2023	2024-03-01	140926
BMW	5	540 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	245	333	Jul 2020	Jun 2023	2024-03-01	140927
BMW	5	530 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	Jun 2023	2024-03-01	140928
BMW	5	530 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	210	286	Jul 2020	Jun 2023	2024-03-01	140929
BMW	5	540 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	250	340	Jul 2020	Jun 2023	2024-03-01	140930
BMW	5	520 I Mild-hybrid	Kombi	Heckantrieb	Benzin/Elektro	135	184	Jul 2020	-	2024-03-01	140931
BMW	5	530 I Mild-hybrid	Kombi	Heckantrieb	Benzin/Elektro	185	252	Jul 2020	-	2024-03-01	140932
BMW	5	530 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	185	252	Jul 2020	-	2024-03-01	140933
BMW	5	540 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140934
BMW	5	530 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140935
BMW	5	530 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140936
BMW	5	540 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2024-03-01	140937
Volvo	Xc40	T4 Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	155	211	Jun 2020	-	2024-03-01	140943
Volvo	V90 ii	T6 Plug-in-hybrid AWD	Kombi	Allrad	Benzin/Elektro	250	340	Jun 2020	Dec 2022	2024-05-01	140957
BMW	3	330 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	215	292	Jul 2019	-	2024-03-01	140967
Ford	Puma	1.0 Ecoboost	SUV	Frontantrieb	Benzin	70	95	Sep 2019	-	2024-03-01	140974
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	192	261	Mar 2019	Jan 2025	2026-03-01	140979
Tesla	Model y	EV Allrad	SUV	Allrad	Elektro	258	351	Mar 2019	Jan 2025	2026-03-01	140980
Tesla	Model y	EV Performance Allrad	SUV	Allrad	Elektro	340	462	Mar 2019	Jan 2025	2026-03-01	140981
Porsche	Taycan	Electric	Stufenheck	Heckantrieb	Elektro	300	408	Jun 2020	-	2024-03-01	140982
RAM	1500 crew cab pickup	3.6 Etorque Mild Hybrid 4X4	Pick-up	Allrad	Benzin/Elektro	227	309	Dec 2018	-	2024-03-01	140998
Opel	Mokka	Mokka-e	SUV	Frontantrieb	Elektro	100	136	Jun 2020	-	2024-03-01	141005
Suzuki	Swift v	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	61	83	Jun 2020	-	2024-03-01	141020
Suzuki	Swift v	1.2 Hybrid	Schrägheck	Allrad	Benzin/Elektro	61	83	Jun 2020	-	2024-03-01	141021
Volvo	S60 iii	B5 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	141022
Volvo	S60 iii	B5 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	141023
BMW	2	218 D	Coupe	Frontantrieb	Diesel	110	150	Jul 2020	-	2024-03-01	141032
BMW	2	218 D	Coupe	Frontantrieb	Diesel	100	136	Jul 2020	Oct 2024	2025-06-01	141033
BMW	2	220 D Xdrive	Coupe	Allrad	Diesel	140	190	Jul 2020	Oct 2024	2025-06-01	141036
Ford	Focus iv turnier	1.0 Ecoboost Mhev	Kombi	Frontantrieb	Benzin/Elektro	114	155	Jul 2020	Nov 2025	2026-02-01	141038
Ford	Focus iv turnier	1.0 Ecoboost Mhev	Kombi	Frontantrieb	Benzin/Elektro	92	125	Jul 2020	Nov 2025	2026-02-01	141039
Hyundai	I30	1.5 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	118	160	Mar 2020	-	2024-03-01	141040
BMW	X2	Xdrive 25 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	162	220	Mar 2020	Oct 2023	2024-03-01	141042


--- Round 1 / checkpoint 续跑 ---
更新点

* 复用 7 个跨批次既有尺寸组，闭合 GLA H247、GLB X247、GLC X253 改款、Clio V、V90 II、BMW 3 G20 和 BMW 2 F44 的相关映射。
* 根据 BMW 官方技术规格，首次建立 BMW 4 系 G22 两种外廓、5 系 G30/G31 改款、6 系 G32 改款和 X2 F39 插混尺寸组。430d 与 M440d 的车长、车高不同，未错误合并。
* 根据 Tesla 2020–2024 Model Y 官方车主手册，建立第一代改款前尺寸组，宽度采用明确的不含后视镜口径。([Tesla][1])

当前批次进度

* READY 映射：39
* PENDING 映射：61
* 当前已引用尺寸组：14
* 本轮首次创建尺寸组：7
* 本轮复用跨批次尺寸组：7
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140670	140670	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH	H247五门SUV。	READY
140686	140686	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-01	HIGH	X247五门SUV。	READY
140691	140691	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	HIGH	X253 2019改款五门SUV。	READY
140694	140694	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	HIGH	X253 2019改款五门SUV。	READY
140751	140751	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	Clio V五门掀背。	READY
140850	140850	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-01	HIGH	G22 430d xDrive双门轿跑外廓。	READY
140856	140856	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440D-COUPE-01	HIGH	M440d xDrive因车长和车高不同独立建组。	READY
140891	140891	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	HIGH	X253 2019改款五门SUV。	READY
140916	140916	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140917	140917	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140918	140918	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140919	140919	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140920	140920	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140921	140921	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140922	140922	Hatchback	6 Series Gran Turismo G32 LCI	G32	5	EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	HIGH	G32改款五门Gran Turismo外廓。	READY
140923	140923	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140924	140924	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140925	140925	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140926	140926	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140927	140927	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140928	140928	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140929	140929	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140930	140930	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-FACELIFT-SEDAN-01	HIGH	G30改款四门轿车外廓。	READY
140931	140931	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140932	140932	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140933	140933	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140934	140934	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140935	140935	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140936	140936	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140937	140937	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-FACELIFT-WAGON-01	HIGH	G31改款五门旅行车外廓。	READY
140957	140957	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II标准旅行车外廓。	READY
140967	140967	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH	G20四门轿车。	READY
140979	140979	SUV	Model Y first generation pre-facelift		5	EU-TESLA-MODEL-Y-GEN1-PREFACELIFT-SUV-01	HIGH	2020–2024款第一代改款前五门SUV外廓。	READY
140980	140980	SUV	Model Y first generation pre-facelift		5	EU-TESLA-MODEL-Y-GEN1-PREFACELIFT-SUV-01	HIGH	2020–2024款第一代改款前五门SUV外廓。	READY
140981	140981	SUV	Model Y first generation pre-facelift		5	EU-TESLA-MODEL-Y-GEN1-PREFACELIFT-SUV-01	HIGH	2020–2024款第一代改款前五门SUV外廓。	READY
141032	141032	Coupe	2 Series Gran Coupé F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe按前驱/四驱布局解析为F44四门Gran Coupé。	READY
141033	141033	Coupe	2 Series Gran Coupé F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe按前驱/四驱布局解析为F44四门Gran Coupé。	READY
141036	141036	Coupe	2 Series Gran Coupé F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe按前驱/四驱布局解析为F44四门Gran Coupé。	READY
141042	141042	SUV	X2 F39	F39	5	EU-BMW-X2-F39-PHEV-SUV-01	HIGH	F39 xDrive25e五门SUV外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-G22-COUPE-01	4768	1852	1390	BMW Group official technical specifications, BMW 430d xDrive Coupé (03/2021)	https://www.press.bmwgroup.com/global/article/attachment/T0326318EN/472221
EU-BMW-4-G22-M440D-COUPE-01	4770	1852	1393	BMW Group official technical specifications, BMW M440d xDrive Coupé (03/2021)	https://www.press.bmwgroup.com/global/article/attachment/T0326318EN/472221
EU-BMW-6-G32-FACELIFT-GRAN-TURISMO-01	5091	1902	1538	BMW Group official technical specifications, BMW 6 Series Gran Turismo (11/2020)	https://www.press.bmwgroup.com/global/article/attachment/T0308711EN/463959
EU-BMW-5-G30-FACELIFT-SEDAN-01	4963	1868	1479	BMW Group official technical specifications, BMW 5 Series Sedan (05/2020)	https://www.press.bmwgroup.com/global/article/attachment/T0314291EN/457886
EU-BMW-5-G31-FACELIFT-WAGON-01	4963	1868	1498	BMW Group official technical specifications, BMW 5 Series Touring (05/2020)	https://www.press.bmwgroup.com/global/article/attachment/T0314289EN/457890
EU-TESLA-MODEL-Y-GEN1-PREFACELIFT-SUV-01	4751	1921	1624	Tesla Model Y Owner's Manual, 2020–2024 exterior dimensions	https://www.tesla.com/ownersmanual/2020_2024_modely/de_de/GUID-E47C4A6D-528E-419C-8C57-FD3864644C34.html
EU-BMW-X2-F39-PHEV-SUV-01	4360	1824	1512	BMW Group official technical specifications, BMW X2 xDrive25e (05/2020)	https://www.press.bmwgroup.com/global/article/attachment/T0314293EN/457892
```

下一步优先处理

1. 集中闭合 Mercedes-Benz 车型簇：GLE V167、GLA AMG H247、E-Class W213、A-Class V177、B-Class W247 和 GLC F-Cell。
2. 批量处理 Hyundai i30 掀背与旅行车外廓，覆盖 6 个关联 Ktype。
3. 处理 Maxus、VW Caddy 和 Transporter 商用车，先确认 SWB/LWB、车顶高度及厢式车/底盘分支，避免错误合并。

推进信号：CONTINUE

[1]: https://www.tesla.com/ownersmanual/2020_2024_modely/de_de/GUID-E47C4A6D-528E-419C-8C57-FD3864644C34.html "Abmessungen"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
更新点

* 闭合 Hyundai i30 2020 改款车型簇：4 个掀背 Ktype 共用一个尺寸组，2 个旅行车 Ktype 共用另一个尺寸组。Hyundai 官方技术表明确区分 Hatchback 与 Wagon，并给出不含后视镜宽度。([现代汽车新闻][1])
* 闭合 Volvo XC40 T4 Plug-in Hybrid，采用 Volvo 官方 2020 XC40 Twin Engine 用户手册尺寸。([沃尔沃汽车][2])
* 闭合两个 Volvo S60 III B5 Ktype，前驱和四驱不改变本批次所需物理外廓，共用一个尺寸组。([沃尔沃汽车][3])

当前批次进度

* READY 映射：48
* PENDING 映射：52
* 已确认尺寸组：18
* 本轮新增尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140729	140729	Hatchback	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-HATCHBACK-01	HIGH	PD改款五门掀背外廓。	READY
140730	140730	Wagon	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-WAGON-01	HIGH	PD改款五门旅行车外廓。	READY
140731	140731	Hatchback	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-HATCHBACK-01	HIGH	PD改款五门掀背外廓。	READY
140732	140732	Wagon	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-WAGON-01	HIGH	PD改款五门旅行车外廓。	READY
140738	140738	Hatchback	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-HATCHBACK-01	HIGH	PD改款五门掀背外廓。	READY
140943	140943	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	2020 XC40 Twin Engine五门SUV外廓。	READY
141022	141022	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	第三代四门轿车外廓。	READY
141023	141023	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	第三代四门轿车外廓。	READY
141040	141040	Hatchback	i30 III facelift	PD	5	EU-HYUNDAI-I30-PD-FACELIFT-HATCHBACK-01	HIGH	PD改款五门掀背外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I30-PD-FACELIFT-HATCHBACK-01	4340	1795	1455	Hyundai Motor Europe i30 Technical Specifications, February 2020	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/20200226_i30_Technical_Data_preliminary_Update.pdf
EU-HYUNDAI-I30-PD-FACELIFT-WAGON-01	4585	1795	1465	Hyundai Motor Europe i30 Technical Specifications, February 2020	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/20200226_i30_Technical_Data_preliminary_Update.pdf
EU-VOLVO-XC40-I-SUV-01	4425	1873	1658	Volvo XC40 Twin Engine 2020 owner's manual – Dimensions	https://www.volvocars.com/en-bh/support/car/xc40-twin-engine/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1437	Volvo S60 Twin Engine 2020 owner's manual – Dimensions	https://www.volvocars.com/en-ca/support/car/s60-twin-engine/article/766ee075f0e03896c0a8015109ee0749/
```

下一步优先处理

1. Mercedes-Benz A-Class、B-Class、E-Class 和 GLE 车型簇，优先寻找欧洲市场官方规格，避免直接套用可能存在保险杠差异的美国市场尺寸。
2. 闭合 Porsche 911 Targa、Taycan、Cayenne GTS 和 McLaren 720S。
3. 集中处理 Skoda E-Citigo、VW T-Cross、Nissan Juke、Ford Puma、Opel Mokka-e 等单一外廓乘用车。

推进信号：CONTINUE

[1]: https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/20200226_i30_Technical_Data_preliminary_Update.pdf "20200226_i30 Technical Data_preliminary_Update"
[2]: https://www.volvocars.com/en-bh/support/car/xc40-twin-engine/article/766ee075f0e03896c0a8015109ee0749/?utm_source=chatgpt.com "XC40 Twin Engine Dimensions | Volvo Support EN-BH"
[3]: https://www.volvocars.com/en-ca/support/car/s60-twin-engine/article/766ee075f0e03896c0a8015109ee0749/?utm_source=chatgpt.com "S60 Twin Engine Dimensions | Volvo Support EN-CA"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
更新点

* 闭合 Mercedes-AMG GLA H247 车型簇。官方 AMG 手册确认全部 AMG GLA 的长宽为 4436×1849 mm；GLA 35 与非 S 的 GLA 45 高度均为 1588 mm，GLA 45 S 高度为 1585 mm，因此拆为两个尺寸组，未错误复用普通 GLA H247 的既有组。([Mercedes-Benz][1])
* 闭合 GLE V167 车型簇：两个 GLE 350 de 共用插混外廓组；GLE 63 与 GLE 63 S 共用 AMG 外廓组。Mercedes-AMG 官方手册给出的 AMG SUV 三维为 4954×2018×1782 mm。([汽车数据网][2])
* 闭合 A 250 e 两种车身、B 250 e、E 350 e 改款前及 E 300 de 改款后尺寸组；轿车、掀背和改款边界分别建组。([汽车数据网][3])

当前批次进度

* READY 映射：60
* PENDING 映射：40
* 已确认尺寸组：27
* 本轮新增尺寸组：9
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140709	140709	SUV	GLE V167	V167	5	EU-MERCEDES-BENZ-GLE-V167-PHEV-SUV-01	HIGH	V167插电混动五门SUV外廓。	READY
140712	140712	SUV	GLE V167	V167	5	EU-MERCEDES-BENZ-GLE-V167-PHEV-SUV-01	HIGH	V167插电混动五门SUV外廓。	READY
140713	140713	SUV	AMG GLE V167	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-63-SUV-01	HIGH	V167 AMG 63五门SUV外廓。	READY
140714	140714	SUV	AMG GLE V167	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-63-SUV-01	HIGH	V167 AMG 63 S五门SUV外廓。	READY
140736	140736	Sedan	A-Class Sedan V177	V177	4	EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-01	HIGH	V177四门插电混动轿车外廓。	READY
140737	140737	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	HIGH	W177五门插电混动掀背外廓。	READY
140775	140775	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-CLASS-W247-HATCHBACK-01	HIGH	W247五门插电混动车身外廓。	READY
140776	140776	SUV	AMG GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-01	HIGH	H247 AMG GLA 35外廓。	READY
140777	140777	SUV	AMG GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-01	HIGH	H247 AMG GLA 45非S外廓。	READY
140778	140778	SUV	AMG GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-45S-SUV-01	HIGH	H247 AMG GLA 45 S高度不同，独立建组。	READY
140787	140787	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213改款前四门插电混动轿车外廓。	READY
140789	140789	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-SEDAN-01	HIGH	W213 2020改款四门插电混动轿车外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-V167-PHEV-SUV-01	4924	1947	1795	Auto-Data Mercedes-Benz GLE SUV V167 GLE 350de technical specifications	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350de-320hp-plug-in-hybrid-4matic-9g-tronic-37678
EU-MERCEDES-BENZ-GLE-V167-AMG-63-SUV-01	4954	2018	1782	Mercedes-Benz Mercedes-AMG GLE Owner's Manual Supplement March 2021	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-bh/pdf/mercedes-amg-gle-owners-manual-supplement-march-2021-1.pdf
EU-MERCEDES-BENZ-A-CLASS-V177-SEDAN-01	4549	1796	1458	Auto-Data Mercedes-Benz A-Class Sedan V177 A 250e technical specifications	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-250e-218hp-plug-in-hybrid-8g-dct-37688
EU-MERCEDES-BENZ-A-CLASS-W177-HATCHBACK-01	4419	1796	1452	Auto-Data Mercedes-Benz A-Class W177 A 250e technical specifications	https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-250e-218hp-plug-in-hybrid-8g-dct-37687
EU-MERCEDES-BENZ-B-CLASS-W247-HATCHBACK-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247 B 250e technical specifications	https://www.auto-data.net/en/mercedes-benz-b-class-w247-b-250e-218hp-plug-in-hybrid-8g-dct-41799
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-01	4436	1849	1588	Mercedes-Benz Mercedes-AMG GLA and GLB Owner's Manual Supplement March 2021	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-om/pdf/mercedes-amg-gla-glb-owners-manual-supplement-march-2021-1.pdf
EU-MERCEDES-BENZ-GLA-H247-AMG-45S-SUV-01	4436	1849	1585	Mercedes-Benz Mercedes-AMG GLA and GLB Owner's Manual Supplement March 2021	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-om/pdf/mercedes-amg-gla-glb-owners-manual-supplement-march-2021-1.pdf
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 350e technical specifications	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-350e-286hp-plug-in-hybrid-9g-tronic-29701
EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-SEDAN-01	4935	1852	1481	Auto-Data Mercedes-Benz E-Class W213 facelift E 300de 4MATIC technical specifications	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300de-306hp-plug-in-hybrid-4matic-9g-tronic-40972
```

下一步优先处理

1. 闭合 Porsche 911 Targa 992、Taycan、Cayenne GTS 和 McLaren 720S。
2. 批量处理 Skoda E-Citigo、VW T-Cross、Nissan Juke、Ford Puma、Opel Mokka-e 和 Suzuki Swift。
3. 最后处理 Maxus、VW Transporter、RAM 1500、Toyota Hilux 等存在轴距、车顶、货斗或商用车分支的记录。

推进信号：CONTINUE

[1]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-om/pdf/mercedes-amg-gla-glb-owners-manual-supplement-march-2021-1.pdf "mercedes-amg-gla-glb-owners-manual-supplement-march-2021-1"
[2]: https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350de-320hp-plug-in-hybrid-4matic-9g-tronic-37678 "Mercedes-Benz GLE SUV (V167) GLE 350de (320 Hp) Plug-in Hybrid 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-250e-218hp-plug-in-hybrid-8g-dct-37687 "Mercedes-Benz A-class (W177) A 250e (218 Hp) Plug-in Hybrid 8G-DCT | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

