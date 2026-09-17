# 任务：all 第 2101-2200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0022__6482e12a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2101-2200 行

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
all 第 2101-2200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-A4-B8-FACELIFT-SEDAN-01	4701	1826	1427
EU-AUDI-A4-B8-FACELIFT-WAGON-01	4699	1826	1436
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	4877	1849	1278
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	5258	1717	1702
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	5258	1717	1656
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	5258	1717	1618
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	5258	1717	1694
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	5258	1717	1648
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	5258	1717	1613
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	4887	1717	1694
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	4887	1717	1648
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	4887	1717	1613
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	5052	2013	1688
EU-CHRYSLER-SEBRING-I-COUPE-01	4760	1770	1296
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887
EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	4689	2019	1787
EU-FORD-USA-EXPEDITION-I-SUV-01	5197	1996	1890
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480
EU-MAZDA-626-V-GF-SEDAN-01	4575	1710	1430
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-NISSAN-350Z-Z33-CONVERTIBLE-PREFL-01	4310	1815	1328
EU-NISSAN-350Z-Z33-COUPE-01	4313	1815	1326
EU-NISSAN-350Z-Z33-ROADSTER-FACELIFT-01	4315	1815	1330
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-3D-02	3986	1719	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-02	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477
EU-RENAULT-CLIO-II-PHASE-III-VAN-01	3811	1639	1417
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	4228	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	4498	1777	1460
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Dodge	Ramcharger	5.2	SUV	Heckantrieb	Benzin	127	173	Oct 1988	Sep 1993	2024-03-01	24785
Dodge	Ramcharger	5.9	SUV	Heckantrieb	Benzin	142	193	Oct 1988	Dec 1996	2024-03-01	24786
Dodge	Viper	8.0 Rt10	Cabriolet	Heckantrieb	Benzin	282	383	Oct 1997	Sep 2002	2024-03-01	24787
Dodge	Viper	8.0 Rt10	Cabriolet	Heckantrieb	Benzin	299	407	Oct 1991	Sep 1997	2024-03-01	24788
Dodge	Viper	8.0 Rt10 ACR	Cabriolet	Heckantrieb	Benzin	335	455	Oct 1997	Sep 2002	2024-03-01	24789
Dodge	Viper	8.0 Rt10	Coupe	Heckantrieb	Benzin	282	383	Oct 1997	Sep 2002	2024-03-01	24790
Dodge	Viper	8.0 Rt10	Coupe	Heckantrieb	Benzin	290	394	Oct 1991	Sep 1997	2024-03-01	24791
Dodge	Viper	8.0 Rt10 ACR	Coupe	Heckantrieb	Benzin	335	455	Oct 1997	Sep 2002	2024-03-01	24792
Ford USA	Contour	2.5 SE	Stufenheck	Frontantrieb	Benzin	127	173	Sep 1993	Aug 1996	2024-03-01	24796
Ford USA	Contour	2.5	Stufenheck	Frontantrieb	Benzin	127	173	Sep 1997	Aug 2000	2024-03-01	24798
Ford USA	Crown	4.6	Stufenheck	Heckantrieb	Benzin	142	193	Sep 1991	Apr 1998	2024-03-01	24801
Ford USA	Crown	4.6	Stufenheck	Heckantrieb	Benzin	157	213	Sep 1991	Apr 1998	2024-03-01	24802
Ford USA	Explorer	4	SUV	Heckantrieb	Benzin	157	213	Sep 2001	-	2024-03-01	24832
Ford USA	Thunderbird	4.0 Premium	Cabriolet	Heckantrieb	Benzin	209	284	Oct 2002	Sep 2005	2024-03-01	24864
Hyundai	Equus / centennial	3.5	Stufenheck	Frontantrieb	Benzin	155	211	Oct 1999	Mar 2009	2024-03-01	24880
Hyundai	Equus / centennial	4.5	Stufenheck	Frontantrieb	Benzin	195	265	Oct 1999	Sep 2003	2024-03-01	24881
Lincoln	Continental	4.6	Stufenheck	Frontantrieb	Benzin	202	275	Jun 1998	Dec 2002	2024-03-01	24892
Lincoln	Continental	4.6 Signature	Stufenheck	Heckantrieb	Benzin	157	213	Jan 1994	Oct 1999	2024-03-01	24894
Lincoln	Continental	4.6	Stufenheck	Heckantrieb	Benzin	142	193	Jan 1993	Jan 1994	2024-03-01	24896
Lincoln	Navigator	5.4	SUV	Heckantrieb	Benzin	224	305	May 1997	Dec 2002	2024-03-01	24899
Lincoln	Navigator	5.4 Allrad	SUV	Allrad	Benzin	224	305	May 1997	Dec 2002	2024-03-01	24900
Nissan	Quest	3.5	Großraumlimousine	Frontantrieb	Benzin	176	239	May 2003	-	2024-03-01	24920
VW	Golf vi	2.0 TDI	Cabriolet	Frontantrieb	Diesel	110	150	Nov 2013	May 2016	2024-03-01	24942
Peugeot	206	1.6 16V	Schrägheck	Frontantrieb	Benzin	79	107	Jun 2001	Apr 2009	2024-03-01	24944
VW	Passat b3/b4 variant	2	Kombi	Frontantrieb	Benzin	85	116	Oct 1993	Oct 1996	2024-03-01	25056
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	82	111	Aug 1983	Dec 1992	2024-03-01	25058
Fiat	Marea	1.6	Kombi	Frontantrieb	Benzin	76	103	Sep 2000	Aug 2002	2024-03-01	25062
Peugeot	Partner	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	80	109	Sep 2000	Oct 2002	2024-03-01	25064
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	130	177	Oct 1981	Sep 1986	2024-03-01	25068
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	224	305	Oct 1991	Apr 1997	2024-03-01	25069
VW	Passat b5.5	2.8	Stufenheck	Frontantrieb	Benzin	142	193	May 2002	May 2003	2024-03-01	25083
Hummer	Hummer h2	6.0 AWD	Geländewagen geschlossen	Allrad	Benzin	232	315	Sep 2002	Sep 2004	2024-03-01	25089
Nissan	350z	3.5	Coupe	Heckantrieb	Benzin	230	313	Sep 2005	Dec 2008	2024-03-01	25093
Audi	A4 b7 avant	3	Kombi	Frontantrieb	Benzin	160	218	Nov 2004	May 2006	2024-03-01	25095
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	140	190	Nov 2002	Oct 2013	2025-12-01	25103
Mitsubishi	Lancer viii	2	Stufenheck	Frontantrieb	Benzin	110	150	Jan 2013	-	2024-03-01	25106
Renault	Clio ii	1.6	Kasten/Schrägheck	Frontantrieb	Benzin	79	107	Nov 2003	-	2026-05-01	25107
Renault	Megane ii	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Jun 2005	Feb 2008	2024-03-01	25108
Renault	Megane ii coupé-	1.6	Cabriolet	Frontantrieb	Benzin	77	105	Jun 2005	Mar 2009	2024-03-01	25109
Renault	Clio iii	1.2	Schrägheck	Frontantrieb	Benzin	57	78	Oct 2005	Dec 2012	2026-05-01	25110
VW	Golf ii	1.6	Schrägheck	Frontantrieb	Benzin	51	69	Aug 1986	Jul 1991	2024-03-01	25113
Honda	Odyssey	3.5	Großraumlimousine	Frontantrieb	Benzin	182	247	Sep 2005	-	2024-03-01	25123
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	182	247	May 1986	Sep 1989	2024-03-01	25133
Mini	Mini	S Works	Schrägheck	Frontantrieb	Benzin	149	203	Nov 2003	Jun 2005	2024-03-01	25139
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	236	321	Jun 1999	Sep 2003	2024-03-01	25148
Ford USA	Mustang convertible	4.6	Cabriolet	Heckantrieb	Benzin	236	321	Jun 1999	Sep 2003	2024-03-01	25149
Chrysler	Sebring	2.4 Turbo	Stufenheck	Frontantrieb	Benzin	164	223	Sep 2001	Jun 2007	2024-03-01	25152
Alfa Romeo	156	2.0 JTS	Stufenheck	Frontantrieb	Benzin	119	162	Mar 2001	Sep 2005	2024-03-01	25154
Honda	Civic vi hatchback	1.5	Schrägheck	Frontantrieb	Benzin	66	90	Nov 1995	Dec 1996	2024-03-01	25155
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	119	162	Oct 1983	Sep 1986	2024-03-01	25158
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	160	218	Oct 1986	Sep 1989	2024-03-01	25160
Ford USA	Expedition	5.4 4X4	SUV	Allrad	Benzin	194	264	Oct 2002	Feb 2006	2024-03-01	25163
Ford USA	Explorer	4.0 4WD	SUV	Allrad	Benzin	157	213	Sep 2001	-	2024-03-01	25164
Ford USA	Explorer	4.6 4WD	SUV	Allrad	Benzin	178	242	Sep 2001	Dec 2005	2024-03-01	25165
Toyota	Hilux vii	2.5 D 4WD	Pick-up	Allrad	Diesel	75	102	Mar 2005	May 2015	2024-03-01	25198
Chevrolet	Colorado	3.5 4X4	Pick-up	Allrad	Benzin	164	223	May 2005	Sep 2006	2024-03-01	25202
Chrysler	Pacifica	3.5 AWD	Großraumlimousine	Allrad	Benzin	186	253	Aug 2003	Dec 2006	2024-03-01	25216
Dodge	Durango	5.7 AWD	SUV	Allrad	Benzin	257	349	Nov 2003	Dec 2010	2024-03-01	25222
Dodge	Ramcharger	5.2 4WD	SUV	Allrad	Benzin	107	145	Oct 1983	Sep 1988	2024-03-01	25223
Dodge	Ramcharger	5.9 4WD	SUV	Allrad	Benzin	130	177	Jan 1983	Sep 1988	2024-03-01	25224
Dodge	Ramcharger	5.2 4WD	SUV	Allrad	Benzin	127	173	Oct 1988	Sep 1993	2024-03-01	25225
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	205	279	Oct 1993	Sep 1997	2024-03-01	25236
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	220	299	Jun 1992	Sep 1997	2024-03-01	25237
Nissan	Cefiro ii	2	Stufenheck	Frontantrieb	Benzin	103	140	Oct 1994	Dec 1999	2024-03-01	25254
Nissan	Cefiro iii	3	Stufenheck	Frontantrieb	Benzin	147	200	Jan 2000	Sep 2003	2024-03-01	25258
Nissan	Skyline	2	Coupe	Heckantrieb	Benzin	114	155	Mar 1989	Jun 1993	2024-03-01	25282
Nissan	Skyline	2.0 Turbo	Coupe	Heckantrieb	Benzin	158	215	Mar 1989	Jun 1993	2024-03-01	25286
Nissan	Skyline	2.5	Coupe	Heckantrieb	Benzin	147	200	Jun 1998	Jul 2000	2024-03-01	25288
Toyota	Fortuner	2.7	SUV	Heckantrieb	Benzin	118	160	Jun 2004	May 2015	2024-03-01	25326
Nissan	Skyline	2.5 4X4	Coupe	Allrad	Benzin	140	190	Jul 1993	May 1998	2024-03-01	25342
Nissan	Skyline	2.0 Turbo 4X4	Stufenheck	Allrad	Benzin	158	215	Mar 1989	Jun 1993	2024-03-01	25346
Land Rover	Discovery iii	4.0 V6 4X4	Geländewagen geschlossen	Allrad	Benzin	160	218	Oct 2004	Sep 2009	2024-03-01	25392
Ssangyong	Korando	2.0 E-xdi	SUV	Frontantrieb	Diesel	110	150	Feb 2012	-	2024-03-01	25402
Ssangyong	Korando	2.0 E-xdi 4WD	SUV	Allrad	Diesel	110	150	Feb 2012	-	2024-03-01	25403
Hummer	Hummer h3	3.7 4WD	Geländewagen geschlossen	Allrad	Benzin	180	245	Jan 2007	-	2024-03-01	25435
Mercedes-benz	R-Klasse	R 280	Großraumlimousine	Heckantrieb	Benzin	170	231	Jan 2007	Dec 2014	2024-03-01	25438
Mercedes-benz	R-Klasse	R 350	Großraumlimousine	Heckantrieb	Benzin	200	272	Jan 2007	Dec 2012	2024-03-01	25439
Mercedes-benz	R-Klasse	R 500 4-matic	Großraumlimousine	Allrad	Benzin	285	388	May 2007	Dec 2014	2024-03-01	25440
Mercedes-benz	R-Klasse	R 280 CDI	Großraumlimousine	Heckantrieb	Diesel	140	190	May 2006	Dec 2012	2024-03-01	25441
BMW	1	125 I	Coupe	Heckantrieb	Benzin	160	218	Mar 2008	Oct 2013	2024-03-01	25442
BMW	1	118 I	Cabriolet	Heckantrieb	Benzin	105	143	Mar 2008	Oct 2013	2024-03-01	25443
BMW	1	135 I	Cabriolet	Heckantrieb	Benzin	225	306	Mar 2008	Oct 2013	2024-03-01	25444
BMW	1	120 D	Cabriolet	Heckantrieb	Diesel	130	177	Mar 2008	Dec 2013	2024-03-01	25445
BMW	5	525 XD	Stufenheck	Allrad	Diesel	145	197	Sep 2007	Aug 2008	2024-03-01	25446
BMW	5	525 XD	Kombi	Allrad	Diesel	145	197	Sep 2007	Sep 2008	2024-03-01	25447
Hyundai	I30	1.6	Kombi	Frontantrieb	Benzin	90	122	Feb 2008	Jun 2012	2024-03-01	25448
Hyundai	I30	2	Kombi	Frontantrieb	Benzin	105	143	Feb 2008	Jun 2012	2024-03-01	25449
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	85	116	Feb 2008	Jun 2012	2024-03-01	25450
Toyota	Hilux vii	2.5 D-4d 4WD	Pick-up	Allrad	Diesel	88	120	Jun 2006	May 2015	2024-03-01	25451
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	88	120	Jun 2006	May 2015	2024-03-01	25452
Toyota	Hilux vii	3.0 D-4d 4WD	Pick-up	Allrad	Diesel	126	171	Aug 2005	Sep 2015	2024-03-01	25453
Audi	A4 b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	100	136	Nov 2007	Dec 2015	2024-03-01	25454
Audi	A4 b8	2.7 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Nov 2007	Mar 2012	2024-03-01	25455
Audi	A4 b8	1.8 Tfsi	Stufenheck	Frontantrieb	Benzin	88	120	Jan 2008	Dec 2015	2024-03-01	25456
Mazda	6	1.8 MZR	Stufenheck	Frontantrieb	Benzin	88	120	Aug 2007	Jul 2013	2024-03-01	25457
Mazda	6	2.0 MZR	Stufenheck	Frontantrieb	Benzin	108	147	Aug 2007	Dec 2012	2024-03-01	25458
Mazda	6	2.5 MZR	Stufenheck	Frontantrieb	Benzin	125	170	Aug 2007	Jul 2013	2024-03-01	25459
Mazda	6	2.0 Mzr-cd	Stufenheck	Frontantrieb	Diesel	103	140	Aug 2007	Oct 2010	2024-03-01	25460
Mazda	6	1.8 MZR	Schrägheck	Frontantrieb	Benzin	88	120	Aug 2007	Jul 2013	2024-03-01	25461
Mazda	6	2.0 MZR	Schrägheck	Frontantrieb	Benzin	108	147	Aug 2007	Jul 2013	2024-03-01	25462


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成 30 个输入 Ktype，共形成 37 条 READY 映射。
* 复用跨批次已有尺寸组 21 个；本轮首次闭合并新增尺寸组 8 个。
* 已处理跨改款或多车身分支：Partner 厢式/乘用版、Megane II 三门/五门、Clio III 改款前后及三门/五门、Audi A4 B8 改款前后。
* 新建尺寸组的三维已按不含后视镜宽度落盘([汽车数据网][1])([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：30
* 待处理 Ktype：70
* READY 映射行：37
* 本轮新增尺寸组：8
* 当前已闭合尺寸组：29，其中复用 21 个、新建 8 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24785	24785	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
24786	24786	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
24942	24942	Convertible	Golf VI Cabriolet	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	Golf VI双门敞篷车身。	READY
25056	25056	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-VARIANT-WAGON-5D-01	HIGH	B4 Variant五门旅行车。	READY
25058	25058	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-CABRIOLET-2D-01	HIGH	Golf I双门敞篷车身。	READY
25062	25062	Wagon	Marea Weekend	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-5D-01	HIGH	185型Weekend五门旅行车。	READY
25064_van	25064	Van	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	输入同时覆盖厢式版；与乘用版外廓三维相同。	READY
25064_mpv	25064	MPV	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	输入同时覆盖乘用版；与厢式版外廓三维相同。	READY
25069	25069	Convertible	Corvette C4	Y	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH	C4双门敞篷车身。	READY
25083	25083	Sedan	Passat B5.5	3B3	4	EU-VW-PASSAT-B5-5-SEDAN-4D-01	HIGH	B5.5四门轿车。	READY
25089	25089	SUV	H2	GMT840	5	EU-HUMMER-H2-GMT840-SUV-5D-01	HIGH	GMT840五门SUV外廓。	READY
25093	25093	Coupe	350Z	Z33	2	EU-NISSAN-350Z-Z33-COUPE-01	HIGH	Z33双门硬顶车身。	READY
25095	25095	Wagon	A4 B7 Avant	8ED	5	EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	HIGH	B7 Avant五门旅行车。	READY
25106	25106	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	CY0四门轿车。	READY
25107	25107	Van	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-VAN-01	HIGH	三门厢式车外廓。	READY
25108_3dr	25108	Hatchback	Megane II Phase II		3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门掀背分支。	READY
25108_5dr	25108	Hatchback	Megane II Phase II		5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门掀背分支。	READY
25109	25109	Convertible	Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	双门Coupe-Cabriolet外廓。	READY
25110_prefl_3dr	25110	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产区间覆盖Phase I三门分支。	READY
25110_prefl_5dr	25110	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产区间覆盖Phase I五门分支。	READY
25110_facelift_3dr	25110	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产区间覆盖Phase II三门分支。	READY
25110_facelift_5dr	25110	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产区间覆盖Phase II五门分支。	READY
25216	25216	MPV	Pacifica I	CS	5	EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	HIGH	CS五门MPV外廓。	READY
25222	25222	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	HB五门SUV外廓。	READY
25223	25223	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25224	25224	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25225	25225	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25236	25236	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代K-body四门轿车。	READY
25237	25237	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代K-body四门轿车。	READY
25392	25392	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-5D-01	HIGH	L319五门SUV外廓。	READY
25442	25442	Coupe	1 Series E82	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH	E82双门Coupe外廓。	READY
25446	25446	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60 LCI四门轿车。	READY
25447	25447	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61 LCI五门旅行车。	READY
25454_prefl	25454	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
25454_facelift	25454	Sedan	A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
25456_prefl	25456	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
25456_facelift	25456	Sedan	A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-1.2-tsi-105hp-20413
EU-VW-PASSAT-B4-VARIANT-WAGON-5D-01	4595	1720	1445	Auto-Data.net	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.0-115hp-8987
EU-VW-GOLF-I-CABRIOLET-2D-01	3815	1630	1410	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-i-cabrio-generation-1883
EU-FIAT-MAREA-185-WEEKEND-WAGON-5D-01	4485	1740	1510	Auto-Data.net	https://www.auto-data.net/en/fiat-marea-weekend-185-1.6-100-16v-103hp-7208
EU-VW-PASSAT-B5-5-SEDAN-4D-01	4703	1746	1462	Auto-Data.net	https://www.auto-data.net/en/volkswagen-passat-b5.5-2.8-30v-v6-193hp-4motion-43042
EU-HUMMER-H2-GMT840-SUV-5D-01	4820	2063	2080	Auto-Data.net	https://www.auto-data.net/en/hummer-h2-gmt-840-6.0i-v8-321hp-12494
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427	Auto-Data.net	https://www.auto-data.net/de/audi-a4-avant-b7-8e-3.0-tdi-v6-233hp-quattro-dpf-tiptronic-26721
EU-LAND-ROVER-DISCOVERY-III-L319-SUV-5D-01	4835	2009	1887	Auto-Data.net	https://www.auto-data.net/en/land-rover-discovery-iii-generation-1216
```

## 下一步优先处理

1. 批量闭合 Dodge Viper RT/10、GTS Coupe 及 ACR 的第一代、第二代车身边界。
2. 处理 Ford Contour、Crown Victoria、Explorer、Expedition、Thunderbird 和 Lincoln Navigator。
3. 集中解决 Toyota Hilux VII 与 Chevrolet Colorado 的驾驶室、驱动和悬架高度分支。
4. 处理 Mercedes-Benz R-Class 的 SWB/LWB，以及跨改款尺寸边界。
5. 随后处理 Nissan Skyline/Cefiro、Hyundai Equus、Mazda 6 GH 和其余日美车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.0-115hp-8987 "Volkswagen Passat Variant (B4) 2.0 (115 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 READY Ktype：40 个，新增 READY 映射：47 行。
* 本轮首次闭合 29 个尺寸组；Ktype `25202` 的 6 个 Colorado 分支及 Ktype `25455` 直接复用既有尺寸组，未重复输出尺寸事实。
* Ktype `24789`、`24791` 存在 ACR、RT/10 与输入车身形式冲突，本轮未强行映射；1999 年资料明确区分 RT/10 Roadster、GTS Coupe 与 Viper ACR。([汽车档案库][1])
* R-Class 相关 Ktype 暂未强行完成，资料确认该车型同时存在两种轴距，需要继续闭合 W251/V251 分支。([汽车档案库][2])

## 当前批次进度

* READY Ktype：70 / 100
* PENDING Ktype：30 / 100
* READY 映射：84 行
* 当前批次已引用并闭合尺寸组：64 个
* 本轮首次创建尺寸组：29 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24787	24787	Convertible	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-CONVERTIBLE-2D-01	HIGH	SR II RT/10双门敞篷外廓。	READY
24788	24788	Convertible	Viper SR I	SR I	2	EU-DODGE-VIPER-SR-I-CONVERTIBLE-2D-01	HIGH	SR I RT/10双门敞篷外廓。	READY
24790	24790	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	HIGH	SR II双门硬顶外廓。	READY
24792	24792	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	HIGH	SR II ACR双门硬顶外廓。	READY
24796	24796	Sedan	Contour I	CDW27	4	EU-FORD-USA-CONTOUR-I-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
24798	24798	Sedan	Contour I Facelift	CDW27	4	EU-FORD-USA-CONTOUR-I-SEDAN-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
24801	24801	Sedan	Crown Victoria I	EN53	4	EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
24802	24802	Sedan	Crown Victoria I	EN53	4	EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
24832	24832	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
24864	24864	Convertible	Thunderbird XI	DEW98	2	EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	HIGH	第十一代双门敞篷外廓。	READY
24880	24880	Sedan	Centennial / Equus I		4	EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	HIGH	第一代四门旗舰轿车外廓。	READY
24881	24881	Sedan	Centennial / Equus I		4	EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	HIGH	第一代四门旗舰轿车外廓。	READY
24892	24892	Sedan	Continental IX	FN74	4	EU-LINCOLN-CONTINENTAL-IX-SEDAN-4D-01	HIGH	第九代前驱四门轿车外廓。	READY
24920	24920	MPV	Quest III	V42	5	EU-NISSAN-QUEST-III-V42-MPV-5D-01	HIGH	V42五门MPV外廓。	READY
24944_prefl	24944	Hatchback	206 Phase I			EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	MEDIUM	生产区间覆盖改款前掀背外廓；门数未限定。	READY
24944_facelift	24944	Hatchback	206 Phase II			EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	MEDIUM	生产区间覆盖改款后掀背外廓；门数未限定。	READY
25068	25068	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25103	25103	Convertible	Elise Series 2	111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	HIGH	Series 2双门Roadster外廓。	READY
25123	25123	MPV	Odyssey III	RL3	5	EU-HONDA-ODYSSEY-III-RL3-MPV-5D-01	HIGH	北美第三代五门MPV外廓。	READY
25133	25133	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25139	25139	Hatchback	Mini R53	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	R53 John Cooper Works三门外廓。	READY
25148	25148	Coupe	Mustang IV Facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	SN95改款后双门Coupe外廓。	READY
25149	25149	Convertible	Mustang IV Facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	SN95改款后双门敞篷外廓。	READY
25152	25152	Sedan	Sebring Sedan JR	JR	4	EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	MEDIUM	JR四门轿车外廓。	READY
25154_prefl	25154	Sedan	156	932	4	EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前四门轿车外廓。	READY
25154_facelift	25154	Sedan	156 Facelift	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后四门轿车外廓。	READY
25155	25155	Hatchback	Civic VI	EK3	3	EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	HIGH	EK三门掀背外廓。	READY
25158	25158	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25160	25160	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25163	25163	SUV	Expedition II	U222	5	EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	HIGH	U222五门SUV外廓。	READY
25164	25164	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
25165	25165	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
25202_regcab_z71	25202	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Regular Cab Z71分支。	READY
25202_regcab_z85	25202	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Regular Cab Z85分支。	READY
25202_extcab_z71	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Extended Cab Z71分支。	READY
25202_extcab_z85	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Extended Cab Z85分支。	READY
25202_crewcab_z71	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Crew Cab Z71分支。	READY
25202_crewcab_z85	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Crew Cab Z85分支。	READY
25254	25254	Sedan	Cefiro II	A32	4	EU-NISSAN-CEFIRO-II-A32-SEDAN-4D-01	HIGH	A32四门轿车外廓。	READY
25258	25258	Sedan	Cefiro III	A33	4	EU-NISSAN-CEFIRO-III-A33-SEDAN-4D-01	HIGH	A33四门轿车外廓。	READY
25402	25402	SUV	Korando III	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	HIGH	C200五门SUV外廓。	READY
25403	25403	SUV	Korando III	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	HIGH	C200五门SUV外廓。	READY
25435	25435	SUV	H3	GMT345	5	EU-HUMMER-H3-GMT345-SUV-5D-01	HIGH	GMT345五门SUV外廓。	READY
25443	25443	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25444	25444	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25445	25445	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25455	25455	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2改款前四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-VIPER-SR-I-CONVERTIBLE-2D-01	4448	1924	1117	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-i-generation-7336
EU-DODGE-VIPER-SR-II-CONVERTIBLE-2D-01	4475	1924	1118	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-ii-convertible-generation-7337
EU-DODGE-VIPER-SR-II-COUPE-2D-01	4488	1923	1219	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-ii-coupe-generation-8225
EU-FORD-USA-CONTOUR-I-SEDAN-PREFL-01	4671	1755	1384	Edmunds	https://www.edmunds.com/ford/contour/1995/features-specs/
EU-FORD-USA-CONTOUR-I-SEDAN-FACELIFT-01	4707	1755	1384	Edmunds	https://www.edmunds.com/ford/contour/1998/features-specs/
EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	5385	1976	1443	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1997/1220075/ford_crown_victoria.html
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826	Edmunds	https://www.edmunds.com/ford/explorer/2002/suv/st-100002015/features-specs/
EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	4730	1829	1323	Auto-Data.net	https://www.auto-data.net/en/ford-thunderbird-retro-birds-4.0-i-v8-32v-283hp-8095
EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	5065	1870	1465	Auto-Data.net	https://www.auto-data.net/en/hyundai-centennial-3.5-v6-210hp-13797
EU-LINCOLN-CONTINENTAL-IX-SEDAN-4D-01	5260	1870	1420	Auto-Data.net	https://www.auto-data.net/en/lincoln-continental-ix-generation-1799
EU-NISSAN-QUEST-III-V42-MPV-5D-01	5184	1971	1778	Auto-Data.net	https://www.auto-data.net/en/nissan-quest-ff-l-3.5-i-v6-24v-233hp-772
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426	Auto-Data.net	https://www.auto-data.net/en/peugeot-206-1.6-16v-109hp-5250
EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	3822	1652	1425	Auto-Data.net	https://www.auto-data.net/en/peugeot-206-facelift-2003-1.6i-16v-109hp-17900
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278	Auto-Data.net	https://www.auto-data.net/en/chevrolet-camaro-iii-generation-9044
EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	3785	1719	1143	Auto-Data.net	https://www.auto-data.net/en/lotus-elise-series-2-1.8-i-16v-111r-192hp-8294
EU-HONDA-ODYSSEY-III-RL3-MPV-5D-01	5105	1958	1778	Edmunds	https://www.edmunds.com/honda/odyssey/2005/features-specs/
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r50-r53-cooper-s-1.6-i-16v-170hp-15332
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-iv-4.6-v8-32v-cobra-320hp-7792
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-iv-convertible-4.6-v8-32v-cobra-324hp-7782
EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	4843	1793	1394	Auto-Data.net	https://www.auto-data.net/en/chrysler-sebring-sedan-jr-2.4-i-16v-150hp-automatic-14810
EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	4430	1745	1415	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-156-932-2.0-jts-165hp-1487
EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	4435	1743	1430	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-156-932-facelift-2003-2.0-16v-jts-165hp-1469
EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	4190	1695	1375	Auto-Data.net	https://www.auto-data.net/en/honda-civic-vi-hatchback-generation-2630
EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	5228	2000	1971	Auto-Data.net	https://www.auto-data.net/en/ford-expedition-ii-generation-1709
EU-NISSAN-CEFIRO-II-A32-SEDAN-4D-01	4760	1770	1410	Auto-Data.net	https://www.auto-data.net/en/nissan-cefiro-32-2.0i-v6-24v-155hp-automatic-25039
EU-NISSAN-CEFIRO-III-A33-SEDAN-4D-01	4920	1780	1435	Auto-Data.net	https://www.auto-data.net/en/nissan-maxima-qx-v-a33-3.0-v6-24v-200hp-automatic-24982
EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	4410	1830	1675	Auto-Data.net	https://www.auto-data.net/en/ssangyong-korando-iii-c-generation-4641
EU-HUMMER-H3-GMT345-SUV-5D-01	4742	1897	1893	Auto-Data.net	https://www.auto-data.net/en/hummer-h3-generation-5530
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411	Auto-Data.net	https://www.auto-data.net/en/bmw-1-series-convertible-e88-118i-143hp-steptronic-9826
```

## 下一步优先处理

1. 闭合 Toyota Hilux VII 的 Single Cab、Extra Cab、Double Cab及改款分支。
2. 闭合 Nissan Skyline R32、R33、R34 的 Coupe、Sedan及四驱分支。
3. 解决 Viper、Lincoln后驱异常记录、Navigator年度高度和 Golf II 改款前后边界。
4. 按标准轴距与长轴分别闭合 Mercedes-Benz R-Class。
5. 最后处理 Fortuner、Hyundai i30 CW及 Mazda 6 GH Sedan/Hatchback。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2022/10/Dodge-Viper-1999-USA.pdf "https://autocatalogarchive.com/wp-content/uploads/2022/10/Dodge-Viper-1999-USA.pdf"
[2]: https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-R-2007-INT.pdf "https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-R-2007-INT.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增完成 9 个 Ktype，共新增 12 条 READY 映射。
* Golf II 按三门、五门拆分映射，但三维一致，复用同一个尺寸组。
* Hyundai i30 FD CW 三个动力版本统一关联同一旅行车尺寸组。
* Mazda 6 GH 按 Sedan、Hatchback及改款前后实际长度差异建组；相同三维直接复用。([汽车目录][1])

## 当前批次进度

* READY Ktype：79 / 100
* PENDING Ktype：21 / 100
* READY 映射：96 行
* 当前已引用并闭合尺寸组：70 个
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25113_3dr	25113	Hatchback	Golf II		3	EU-VW-GOLF-II-HATCHBACK-01	MEDIUM	Ktype未限定门数；三门分支。	READY
25113_5dr	25113	Hatchback	Golf II		5	EU-VW-GOLF-II-HATCHBACK-01	MEDIUM	Ktype未限定门数；五门分支。	READY
25448	25448	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25449	25449	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25450	25450	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25457	25457	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25458	25458	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25460	25460	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25461_prefl	25461	Hatchback	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-01	MEDIUM	改款前1.8五门掀背分支。	READY
25461_facelift	25461	Hatchback	Mazda 6 II Facelift	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	MEDIUM	改款后1.8五门掀背分支。	READY
25462_prefl	25462	Hatchback	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	MEDIUM	改款前2.0五门掀背分支。	READY
25462_facelift	25462	Hatchback	Mazda 6 II Facelift	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-03	MEDIUM	改款后2.0五门掀背分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-II-HATCHBACK-01	3985	1665	1415	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1987/30305/volkswagen_golf_1_6_gl.html
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565	Auto-Data.net	https://www.auto-data.net/en/hyundai-i30-i-cw-2.0-143hp-automatic-30922
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-sedan-gh-2.0-147hp-44555; https://www.auto-data.net/en/mazda-6-ii-sedan-gh-facelift-2010-2.0-155hp-16773
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-1.8-120hp-16780
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-2.0-147hp-16781; https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-1.8-120hp-44573
EU-MAZDA-6-II-GH-HATCHBACK-03	4765	1795	1440	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-2.0i-155hp-17509
```

## 下一步优先处理

1. 闭合 Toyota Hilux VII 的驾驶室、驱动形式和改款分支。
2. 闭合 Nissan Skyline R32、R33、R34 的 Coupe与Sedan外廓。
3. 处理 Mercedes-Benz R-Class W251/V251 标准轴距和长轴分支。
4. 处理 Lincoln异常车型记录、Navigator、Fortuner及Viper冲突记录。
5. 最后闭合 Mazda 6 2.5 Sedan剩余改款差异。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/30305/volkswagen_golf_1_6_gl.html?utm_source=chatgpt.com "1987 Volkswagen Golf 1.6 GL Specs Review (55 kW / 75 PS / 74 hp) (for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增完成 10 个 Ktype，新增 10 条 READY 映射。
* Dodge Viper 两条冲突记录按实际硬顶车身关联既有 Coupe 尺寸组，未重复输出尺寸组。
* Lincoln Navigator I 两个驱动版本共用同一物理外廓，新建 1 个尺寸组。([汽车数据网][1])
* Nissan Skyline R32、R33、R34 共闭合 5 个 Ktype，新建 4 个尺寸组。([日产汽车公司][2])
* Lincoln 两条记录的动力、驱动及 Signature 版本信息实际指向 Town Car，与输入 Model `Continental` 冲突，暂不强制落组。([汽车目录][3])
* Hilux VII 官方资料确认同时存在多种驾驶室和 4×2／4×4组合，当前 Ktype 未限定具体分支，继续保持 PENDING。([丰田欧洲新闻中心][4])

## 当前批次进度

* READY Ktype：89 / 100
* PENDING Ktype：11 / 100
* READY 映射：106 行
* PENDING 映射：11 行
* 当前已引用并闭合尺寸组：75 个
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24789	24789	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	MEDIUM	输入BodyStyle与ACR硬顶车型冲突；按ACR实际物理车身归入Coupe。	READY
24791	24791	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	MEDIUM	输入VariantName与硬顶车身冲突；按Coupe实际物理车身归类。	READY
24894	24894	Sedan	Town Car II		4		LOW	动力、驱动及Signature版本指向Town Car；输入Model仍为Continental。	PENDING: 输入车型名称冲突且完整尺寸组尚未闭合
24896	24896	Sedan	Town Car II		4		LOW	动力及后驱信息指向Town Car；输入Model仍为Continental。	PENDING: 输入车型名称冲突且完整尺寸组尚未闭合
24899	24899	SUV	Navigator I		5	EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
24900	24900	SUV	Navigator I		5	EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
25198	25198	Pickup	Hilux VII				LOW	候选包含Single Cab、Extra Cab和Double Cab，并覆盖改款区间。	PENDING: 驾驶室及跨改款物理外廓分支尚未闭合
25282	25282	Coupe	Skyline R32	HR32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	MEDIUM	R32自然吸气双门Coupe外廓。	READY
25286	25286	Coupe	Skyline R32	HCR32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	HIGH	R32涡轮双门Coupe外廓。	READY
25288	25288	Coupe	Skyline R34	ER34	2	EU-NISSAN-SKYLINE-R34-COUPE-2D-01	HIGH	ER34双门Coupe外廓。	READY
25326	25326	SUV	Fortuner I		5		LOW	生产区间覆盖第一代改款前后外廓。	PENDING: 跨改款尺寸边界尚未闭合
25342	25342	Coupe	Skyline R33	ENR33	2	EU-NISSAN-SKYLINE-R33-GTS4-COUPE-2D-01	HIGH	ENR33四驱双门Coupe外廓。	READY
25346	25346	Sedan	Skyline R32	HNR32	4	EU-NISSAN-SKYLINE-R32-SEDAN-4D-01	HIGH	HNR32四驱四门Sedan外廓。	READY
25438	25438	MPV	R-Class		5		LOW	候选包含W251标准轴距、V251长轴及跨改款外廓。	PENDING: 轴距及跨改款物理分支尚未闭合
25439	25439	MPV	R-Class		5		LOW	候选包含W251标准轴距、V251长轴及跨改款外廓。	PENDING: 轴距及跨改款物理分支尚未闭合
25440	25440	MPV	R-Class		5		LOW	候选包含V251长轴及跨改款外廓。	PENDING: 跨改款物理分支尚未闭合
25441	25441	MPV	R-Class		5		LOW	候选包含W251标准轴距、V251长轴及跨改款外廓。	PENDING: 轴距及跨改款物理分支尚未闭合
25451	25451	Pickup	Hilux VII				LOW	候选包含Single Cab、Extra Cab和Double Cab，并覆盖改款区间。	PENDING: 驾驶室及跨改款物理外廓分支尚未闭合
25452	25452	Pickup	Hilux VII				LOW	候选包含多种驾驶室及两驱外廓。	PENDING: 驾驶室及跨改款物理外廓分支尚未闭合
25453	25453	Pickup	Hilux VII				LOW	候选包含Single Cab、Extra Cab和Double Cab，并覆盖改款区间。	PENDING: 驾驶室及跨改款物理外廓分支尚未闭合
25459	25459	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	5202	2030	1948	Auto-Data.net	https://www.auto-data.net/en/lincoln-navigator-i-generation-1805
EU-NISSAN-SKYLINE-R32-COUPE-2D-01	4530	1695	1325	Nissan Heritage Collection	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/Skyline_GTS-t_TypeM.html
EU-NISSAN-SKYLINE-R34-COUPE-2D-01	4580	1725	1340	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1999/2137790/nissan_skyline_2door_sports_coupe_25gt_turbo.html
EU-NISSAN-SKYLINE-R33-GTS4-COUPE-2D-01	4640	1720	1355	Goo-net Exchange	https://www.goo-net-exchange.com/catalog/NISSAN__SKYLINE/1501399/
EU-NISSAN-SKYLINE-R32-SEDAN-4D-01	4580	1695	1360	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1992/2135255/nissan_skyline_4door_sports_sedan_gts-4.html
```

## 下一步优先处理

1. 一次性闭合 Hilux VII 的驾驶室、驱动和改款尺寸矩阵。
2. 拆分 R-Class W251标准轴距、V251长轴及改款后的实际尺寸分支。
3. 闭合 Fortuner I 改款前后外廓。
4. 完成两条 Lincoln Town Car异常记录的完整三维，并保留输入 Model 冲突说明。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lincoln-navigator-i-generation-1805?utm_source=chatgpt.com "Lincoln Navigator I | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/Skyline_GTS-t_TypeM.html?utm_source=chatgpt.com "Skyline GTS-t TypeM (1990 : HCR32)"
[3]: https://www.automobile-catalog.com/car/1994/1415525/lincoln_town_car_signature.html?utm_source=chatgpt.com "1994 Lincoln Town Car Signature Specs Review (156.5 kW / 213 PS / 210 hp) (since mid-year 1993 for North America U.S.)"
[4]: https://newsroom.toyota.eu/2005-toyota-hilux/ "2005 Toyota Hilux"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz R-Class 的 3 个 Ktype：`25438`、`25439`、`25441`。
* `25438`、`25439` 均拆分为 W251 标准轴距与 V251 长轴车身；对应车型代码资料同时覆盖两种车身。([AUTODOC][1])
* `25441` 同样拆分为 W251 与 V251；柴油版本高度与汽油版本不同，因此使用同系列独立尺寸组。([汽车数据网][2])
* `25440` 暂不修改，继续等待 R500 跨改款外廓边界闭合。

## 当前批次进度

* READY Ktype：92 / 100
* PENDING Ktype：8 / 100
* READY 映射：112 行
* PENDING 映射：8 行
* 当前已引用并闭合尺寸组：79 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
25438_swb	25438	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	HIGH	W251标准轴距分支。	READY
25438_lwb	25438	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	HIGH	V251长轴分支。	READY
25439_swb	25439	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	HIGH	W251标准轴距分支。	READY
25439_lwb	25439	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	HIGH	V251长轴分支。	READY
25441_swb	25441	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-02	HIGH	W251标准轴距柴油高度分支。	READY
25441_lwb	25441	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-02	HIGH	V251长轴柴油高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	4922	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-v6-231hp-g-tronic-37164
EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	5157	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-r-280-v6-231hp-g-tronic-37188
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-02	4922	1922	1659	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-cdi-v6-190hp-g-tronic-37168
EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-02	5157	1922	1659	Auto-Data.net	https://www.auto-data.net/es/mercedes-benz-r-class-long-v251-r-280-cdi-v6-190hp-g-tronic-37190
```

## 下一步优先处理

1. 闭合四个 Hilux VII Ktype 的驾驶室、两驱/四驱和改款尺寸矩阵。
2. 解决 R-Class R500 Ktype `25440` 的 W251/V251及跨改款分支。
3. 闭合 Fortuner I Ktype `25326` 的改款前后尺寸。
4. 最后处理 Lincoln Town Car 冲突记录 `24894`、`24896`。

推进信号：CONTINUE

[1]: https://www.autodoc.fi/autonosat/aanitorvi-10420/mercedes-benz/r-klasse/r-sarja-w251-v251/25438-r-280-251-054-251-154?utm_source=chatgpt.com "Mercedes W251 R 280 3.0 Äänitorvi (231 hv Bensiini M 272.945)"
[2]: https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-cdi-v6-190hp-g-tronic-37168 "Mercedes-Benz R-class (W251) R 280 CDI V6 (190 Hp) G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 4 个 Ktype：Lincoln `24894`、`24896`，Toyota Fortuner `25326`，Mercedes-Benz R-Class `25440`。
* Lincoln 记录实际对应 Town Car；`24894` 的生产区间跨越 1995 年改款和 1998 年换代，因此拆成 3 个物理外廓，`24896` 复用 1993–1994 尺寸组。([Edmunds][1])
* Fortuner 按 2011 年外廓更新前后拆分，车长分别为 4695 mm 和 4705 mm。([Scribd][2])
* R500 按改款前后及标准轴距／长轴拆成 4 个分支；改款后尺寸采用 Mercedes-Benz 官方 R-Class brochure，不含后视镜宽度为 1922 mm。([汽车数据网][3])

## 当前批次进度

* READY Ktype：96 / 100
* PENDING Ktype：4 / 100
* READY 映射：122 行
* PENDING 映射：4 行
* 当前已引用并闭合尺寸组：88 个
* 本轮首次创建尺寸组：9 个
* 剩余 PENDING 均为 Toyota Hilux VII：`25198`、`25451`、`25452`、`25453`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24894_prefl	24894	Sedan	Town Car II	FN36	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	MEDIUM	输入Model与动力及驱动信息冲突；1994车身分支。	READY
24894_facelift	24894	Sedan	Town Car II Facelift	FN116	4	EU-LINCOLN-TOWN-CAR-II-FACELIFT-SEDAN-01	MEDIUM	输入Model与动力及驱动信息冲突；1995-1997车身分支。	READY
24894_gen3	24894	Sedan	Town Car III	FN145	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-01	MEDIUM	输入Model与动力及驱动信息冲突；1998-1999车身分支。	READY
24896	24896	Sedan	Town Car II	FN36	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	MEDIUM	输入Model与动力及驱动信息冲突；1993车身。	READY
25326_pre2011	25326	SUV	Fortuner I	TGN61	5	EU-TOYOTA-FORTUNER-I-TGN61-SUV-PRE2011-01	MEDIUM	生产区间覆盖2011年外廓更新前分支。	READY
25326_2011facelift	25326	SUV	Fortuner I 2011 Facelift	TGN61	5	EU-TOYOTA-FORTUNER-I-TGN61-SUV-2011-FACELIFT-01	MEDIUM	生产区间覆盖2011年外廓更新后分支。	READY
25440_prefl_swb	25440	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-PREFL-01	MEDIUM	改款前标准轴距分支。	READY
25440_prefl_lwb	25440	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-PREFL-01	MEDIUM	改款前长轴分支。	READY
25440_facelift_swb	25440	MPV	R-Class W251 Facelift	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-FACELIFT-01	MEDIUM	改款后标准轴距分支。	READY
25440_facelift_lwb	25440	MPV	R-Class V251 Long Facelift	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-FACELIFT-01	MEDIUM	改款后长轴分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	5560	1953	1445	Edmunds 1993 Lincoln Town Car; Edmunds 1994 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1993/sedan/st-2837/features-specs/; https://www.edmunds.com/lincoln/town-car/1994/st-2834/features-specs/
EU-LINCOLN-TOWN-CAR-II-FACELIFT-SEDAN-01	5560	1948	1445	Edmunds 1995 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1995/sedan/st-2827/features-specs/
EU-LINCOLN-TOWN-CAR-III-SEDAN-01	5469	1986	1473	Edmunds 1998 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1998/sedan/st-14253/features-specs/
EU-TOYOTA-FORTUNER-I-TGN61-SUV-PRE2011-01	4695	1840	1850	Toyota Fortuner brochure	https://id.scribd.com/document/77881333/Toyota-Fortuner-Brochure
EU-TOYOTA-FORTUNER-I-TGN61-SUV-2011-FACELIFT-01	4705	1840	1850	Toyota Fortuner 2012 brochure	https://es.scribd.com/document/533338815/Toyota-Fortuner-Brochure-2012
EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-PREFL-01	4938	1922	1661	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-500-v8-388hp-4matic-7g-tronic-54142
EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-PREFL-01	5157	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-r-500-v8-388hp-4matic-g-tronic-37236
EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-FACELIFT-01	4922	1922	1674	Mercedes-Benz R-Class official brochure	https://ragtop.org/mbbrochures/2012/new-zealand/r251_Brochure.pdf
EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-FACELIFT-01	5157	1922	1674	Mercedes-Benz R-Class official brochure	https://ragtop.org/mbbrochures/2012/new-zealand/r251_Brochure.pdf
```

## 下一步优先处理

1. 将剩余 4 个 Hilux VII Ktype 作为一个尺寸矩阵处理，统一闭合 Single Cab、Extra Cab、Double Cab、两驱／四驱及改款分支。
2. 优先复用既有 `EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01`，仅对尚不存在的外廓首次建组。
3. Hilux 全部闭合后，立即执行一次机械检查并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.edmunds.com/lincoln/town-car/1993/sedan/st-2837/features-specs/ "Used 1993 Lincoln Town Car Sedan Executive Specs & Features | Edmunds"
[2]: https://fr.scribd.com/document/77881333/Toyota-Fortuner-Brochure?utm_source=chatgpt.com "Toyota Fortuner Brochure | PDF | Suspension (Vehicle)"
[3]: https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-r-500-v8-388hp-4matic-g-tronic-37236 "Mercedes-Benz R-class Long (V251) R 500 V8 (388 Hp) 4MATIC G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 剩余 4 个 Hilux VII Ktype 已全部闭合，新增 26 条 READY 映射。
* Hilux 按 Single Cab、Extra Cab、Double Cab、2WD／4WD、窄体／宽体及 2012 改款拆分；复用既有 Single Cab 2WD 尺寸组，其余首次建组。改款前尺寸采用 Toyota 官方技术资料，2012 改款尺寸采用对应市场 brochure。([丰田欧洲新闻中心][1])
* 已完成轻量机械检查：表头固定、`id` 和 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸与来源均非空。
* 当前批次不存在 PENDING。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY Ktype：100
* PENDING Ktype：0
* 最终 Ktype 映射：148 行
* 最终 DIMENSION_GROUP：99 行
* 所有映射均为 `READY`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24785	24785	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
24786	24786	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
24787	24787	Convertible	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-CONVERTIBLE-2D-01	HIGH	SR II RT/10双门敞篷外廓。	READY
24788	24788	Convertible	Viper SR I	SR I	2	EU-DODGE-VIPER-SR-I-CONVERTIBLE-2D-01	HIGH	SR I RT/10双门敞篷外廓。	READY
24789	24789	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	MEDIUM	输入BodyStyle与ACR硬顶车型冲突；按ACR实际物理车身归入Coupe。	READY
24790	24790	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	HIGH	SR II双门硬顶外廓。	READY
24791	24791	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	MEDIUM	输入VariantName与硬顶车身冲突；按Coupe实际物理车身归类。	READY
24792	24792	Coupe	Viper SR II	SR II	2	EU-DODGE-VIPER-SR-II-COUPE-2D-01	HIGH	SR II ACR双门硬顶外廓。	READY
24796	24796	Sedan	Contour I	CDW27	4	EU-FORD-USA-CONTOUR-I-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
24798	24798	Sedan	Contour I Facelift	CDW27	4	EU-FORD-USA-CONTOUR-I-SEDAN-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
24801	24801	Sedan	Crown Victoria I	EN53	4	EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
24802	24802	Sedan	Crown Victoria I	EN53	4	EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	HIGH	第一代四门轿车外廓。	READY
24832	24832	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
24864	24864	Convertible	Thunderbird XI	DEW98	2	EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	HIGH	第十一代双门敞篷外廓。	READY
24880	24880	Sedan	Centennial / Equus I		4	EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	HIGH	第一代四门旗舰轿车外廓。	READY
24881	24881	Sedan	Centennial / Equus I		4	EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	HIGH	第一代四门旗舰轿车外廓。	READY
24892	24892	Sedan	Continental IX	FN74	4	EU-LINCOLN-CONTINENTAL-IX-SEDAN-4D-01	HIGH	第九代前驱四门轿车外廓。	READY
24894_prefl	24894	Sedan	Town Car II	FN36	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	MEDIUM	输入Model与动力及驱动信息冲突；1994车身分支。	READY
24894_facelift	24894	Sedan	Town Car II Facelift	FN116	4	EU-LINCOLN-TOWN-CAR-II-FACELIFT-SEDAN-01	MEDIUM	输入Model与动力及驱动信息冲突；1995-1997车身分支。	READY
24894_gen3	24894	Sedan	Town Car III	FN145	4	EU-LINCOLN-TOWN-CAR-III-SEDAN-01	MEDIUM	输入Model与动力及驱动信息冲突；1998-1999车身分支。	READY
24896	24896	Sedan	Town Car II	FN36	4	EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	MEDIUM	输入Model与动力及驱动信息冲突；1993车身。	READY
24899	24899	SUV	Navigator I		5	EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
24900	24900	SUV	Navigator I		5	EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	HIGH	第一代五门SUV外廓。	READY
24920	24920	MPV	Quest III	V42	5	EU-NISSAN-QUEST-III-V42-MPV-5D-01	HIGH	V42五门MPV外廓。	READY
24942	24942	Convertible	Golf VI Cabriolet	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH	Golf VI双门敞篷车身。	READY
24944_prefl	24944	Hatchback	206 Phase I			EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	MEDIUM	生产区间覆盖改款前掀背外廓；门数未限定。	READY
24944_facelift	24944	Hatchback	206 Phase II			EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	MEDIUM	生产区间覆盖改款后掀背外廓；门数未限定。	READY
25056	25056	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-VARIANT-WAGON-5D-01	HIGH	B4 Variant五门旅行车。	READY
25058	25058	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-CABRIOLET-2D-01	HIGH	Golf I双门敞篷车身。	READY
25062	25062	Wagon	Marea Weekend	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-5D-01	HIGH	185型Weekend五门旅行车。	READY
25064_van	25064	Van	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	输入同时覆盖厢式版；与乘用版外廓三维相同。	READY
25064_mpv	25064	MPV	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	输入同时覆盖乘用版；与厢式版外廓三维相同。	READY
25068	25068	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25069	25069	Convertible	Corvette C4	Y	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH	C4双门敞篷车身。	READY
25083	25083	Sedan	Passat B5.5	3B3	4	EU-VW-PASSAT-B5-5-SEDAN-4D-01	HIGH	B5.5四门轿车。	READY
25089	25089	SUV	H2	GMT840	5	EU-HUMMER-H2-GMT840-SUV-5D-01	HIGH	GMT840五门SUV外廓。	READY
25093	25093	Coupe	350Z	Z33	2	EU-NISSAN-350Z-Z33-COUPE-01	HIGH	Z33双门硬顶车身。	READY
25095	25095	Wagon	A4 B7 Avant	8ED	5	EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	HIGH	B7 Avant五门旅行车。	READY
25103	25103	Convertible	Elise Series 2	111	2	EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	HIGH	Series 2双门Roadster外廓。	READY
25106	25106	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	CY0四门轿车。	READY
25107	25107	Van	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-VAN-01	HIGH	三门厢式车外廓。	READY
25108_3dr	25108	Hatchback	Megane II Phase II		3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门掀背分支。	READY
25108_5dr	25108	Hatchback	Megane II Phase II		5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门掀背分支。	READY
25109	25109	Convertible	Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	双门Coupe-Cabriolet外廓。	READY
25110_prefl_3dr	25110	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产区间覆盖Phase I三门分支。	READY
25110_prefl_5dr	25110	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产区间覆盖Phase I五门分支。	READY
25110_facelift_3dr	25110	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	生产区间覆盖Phase II三门分支。	READY
25110_facelift_5dr	25110	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	生产区间覆盖Phase II五门分支。	READY
25113_3dr	25113	Hatchback	Golf II		3	EU-VW-GOLF-II-HATCHBACK-01	MEDIUM	Ktype未限定门数；三门分支。	READY
25113_5dr	25113	Hatchback	Golf II		5	EU-VW-GOLF-II-HATCHBACK-01	MEDIUM	Ktype未限定门数；五门分支。	READY
25123	25123	MPV	Odyssey III	RL3	5	EU-HONDA-ODYSSEY-III-RL3-MPV-5D-01	HIGH	北美第三代五门MPV外廓。	READY
25133	25133	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25139	25139	Hatchback	Mini R53	R53	3	EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	HIGH	R53 John Cooper Works三门外廓。	READY
25148	25148	Coupe	Mustang IV Facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	SN95改款后双门Coupe外廓。	READY
25149	25149	Convertible	Mustang IV Facelift	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	SN95改款后双门敞篷外廓。	READY
25152	25152	Sedan	Sebring Sedan JR	JR	4	EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	MEDIUM	JR四门轿车外廓。	READY
25154_prefl	25154	Sedan	156	932	4	EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前四门轿车外廓。	READY
25154_facelift	25154	Sedan	156 Facelift	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后四门轿车外廓。	READY
25155	25155	Hatchback	Civic VI	EK3	3	EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	HIGH	EK三门掀背外廓。	READY
25158	25158	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25160	25160	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门掀背式Coupe外廓。	READY
25163	25163	SUV	Expedition II	U222	5	EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	HIGH	U222五门SUV外廓。	READY
25164	25164	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
25165	25165	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	HIGH	U152五门SUV外廓。	READY
25198_prefl_singlecab	25198	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	MEDIUM	生产区间覆盖改款前Single Cab 4WD分支。	READY
25198_prefl_extracab	25198	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	MEDIUM	生产区间覆盖改款前Extra Cab 4WD分支。	READY
25198_prefl_doublecab_narrow	25198	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	MEDIUM	生产区间覆盖改款前Double Cab 4WD窄体分支。	READY
25198_prefl_doublecab_wide	25198	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	MEDIUM	生产区间覆盖改款前Double Cab 4WD宽体分支。	READY
25198_facelift_singlecab	25198	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Single Cab分支。	READY
25198_facelift_extracab	25198	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Extra Cab分支。	READY
25198_facelift_doublecab_narrow	25198	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	生产区间覆盖2012改款Double Cab窄体分支。	READY
25198_facelift_doublecab_wide	25198	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	MEDIUM	生产区间覆盖2012改款Double Cab宽体分支。	READY
25202_regcab_z71	25202	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Regular Cab Z71分支。	READY
25202_regcab_z85	25202	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Regular Cab Z85分支。	READY
25202_extcab_z71	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Extended Cab Z71分支。	READY
25202_extcab_z85	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Extended Cab Z85分支。	READY
25202_crewcab_z71	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Crew Cab Z71分支。	READY
25202_crewcab_z85	25202	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	MEDIUM	Ktype未限定驾驶室/悬架；覆盖Crew Cab Z85分支。	READY
25216	25216	MPV	Pacifica I	CS	5	EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	HIGH	CS五门MPV外廓。	READY
25222	25222	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH	HB五门SUV外廓。	READY
25223	25223	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25224	25224	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25225	25225	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH	第二代三门SUV外廓。	READY
25236	25236	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代K-body四门轿车。	READY
25237	25237	Sedan	Seville IV	K	4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代K-body四门轿车。	READY
25254	25254	Sedan	Cefiro II	A32	4	EU-NISSAN-CEFIRO-II-A32-SEDAN-4D-01	HIGH	A32四门轿车外廓。	READY
25258	25258	Sedan	Cefiro III	A33	4	EU-NISSAN-CEFIRO-III-A33-SEDAN-4D-01	HIGH	A33四门轿车外廓。	READY
25282	25282	Coupe	Skyline R32	HR32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	MEDIUM	R32自然吸气双门Coupe外廓。	READY
25286	25286	Coupe	Skyline R32	HCR32	2	EU-NISSAN-SKYLINE-R32-COUPE-2D-01	HIGH	R32涡轮双门Coupe外廓。	READY
25288	25288	Coupe	Skyline R34	ER34	2	EU-NISSAN-SKYLINE-R34-COUPE-2D-01	HIGH	ER34双门Coupe外廓。	READY
25326_pre2011	25326	SUV	Fortuner I	TGN61	5	EU-TOYOTA-FORTUNER-I-TGN61-SUV-PRE2011-01	MEDIUM	生产区间覆盖2011年外廓更新前分支。	READY
25326_2011facelift	25326	SUV	Fortuner I 2011 Facelift	TGN61	5	EU-TOYOTA-FORTUNER-I-TGN61-SUV-2011-FACELIFT-01	MEDIUM	生产区间覆盖2011年外廓更新后分支。	READY
25342	25342	Coupe	Skyline R33	ENR33	2	EU-NISSAN-SKYLINE-R33-GTS4-COUPE-2D-01	HIGH	ENR33四驱双门Coupe外廓。	READY
25346	25346	Sedan	Skyline R32	HNR32	4	EU-NISSAN-SKYLINE-R32-SEDAN-4D-01	HIGH	HNR32四驱四门Sedan外廓。	READY
25392	25392	SUV	Discovery III	L319	5	EU-LAND-ROVER-DISCOVERY-III-L319-SUV-5D-01	HIGH	L319五门SUV外廓。	READY
25402	25402	SUV	Korando III	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	HIGH	C200五门SUV外廓。	READY
25403	25403	SUV	Korando III	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	HIGH	C200五门SUV外廓。	READY
25435	25435	SUV	H3	GMT345	5	EU-HUMMER-H3-GMT345-SUV-5D-01	HIGH	GMT345五门SUV外廓。	READY
25438_swb	25438	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	HIGH	W251标准轴距分支。	READY
25438_lwb	25438	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	HIGH	V251长轴分支。	READY
25439_swb	25439	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	HIGH	W251标准轴距分支。	READY
25439_lwb	25439	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	HIGH	V251长轴分支。	READY
25440_prefl_swb	25440	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-PREFL-01	MEDIUM	改款前标准轴距分支。	READY
25440_prefl_lwb	25440	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-PREFL-01	MEDIUM	改款前长轴分支。	READY
25440_facelift_swb	25440	MPV	R-Class W251 Facelift	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-FACELIFT-01	MEDIUM	改款后标准轴距分支。	READY
25440_facelift_lwb	25440	MPV	R-Class V251 Long Facelift	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-FACELIFT-01	MEDIUM	改款后长轴分支。	READY
25441_swb	25441	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-02	HIGH	W251标准轴距柴油高度分支。	READY
25441_lwb	25441	MPV	R-Class V251 Long	V251	5	EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-02	HIGH	V251长轴柴油高度分支。	READY
25442	25442	Coupe	1 Series E82	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH	E82双门Coupe外廓。	READY
25443	25443	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25444	25444	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25445	25445	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88双门敞篷外廓。	READY
25446	25446	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60 LCI四门轿车。	READY
25447	25447	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61 LCI五门旅行车。	READY
25448	25448	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25449	25449	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25450	25450	Wagon	i30 I CW	FD	5	EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	HIGH	FD五门旅行车外廓。	READY
25451_prefl_singlecab	25451	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	MEDIUM	生产区间覆盖改款前Single Cab 4WD分支。	READY
25451_prefl_extracab	25451	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	MEDIUM	生产区间覆盖改款前Extra Cab 4WD分支。	READY
25451_prefl_doublecab_narrow	25451	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	MEDIUM	生产区间覆盖改款前Double Cab 4WD窄体分支。	READY
25451_prefl_doublecab_wide	25451	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	MEDIUM	生产区间覆盖改款前Double Cab 4WD宽体分支。	READY
25451_facelift_singlecab	25451	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Single Cab分支。	READY
25451_facelift_extracab	25451	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Extra Cab分支。	READY
25451_facelift_doublecab_narrow	25451	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	生产区间覆盖2012改款Double Cab窄体分支。	READY
25451_facelift_doublecab_wide	25451	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	MEDIUM	生产区间覆盖2012改款Double Cab宽体分支。	READY
25452_prefl_singlecab	25452	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	生产区间覆盖改款前Single Cab 2WD分支。	READY
25452_prefl_extracab	25452	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	MEDIUM	生产区间覆盖改款前Extra Cab 2WD分支。	READY
25452_prefl_doublecab	25452	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	MEDIUM	生产区间覆盖改款前Double Cab 2WD分支。	READY
25452_facelift_singlecab	25452	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Single Cab分支。	READY
25452_facelift_extracab	25452	Pickup	Hilux VII 2012 Facelift		2	EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	MEDIUM	生产区间覆盖2012改款Extra Cab分支。	READY
25452_facelift_doublecab_narrow	25452	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	生产区间覆盖2012改款Double Cab窄体分支。	READY
25452_facelift_doublecab_wide	25452	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	MEDIUM	生产区间覆盖2012改款Double Cab宽体分支。	READY
25453_prefl_doublecab_wide	25453	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	HIGH	改款前3.0 D-4D Double Cab宽体分支。	READY
25453_facelift_doublecab_narrow	25453	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	MEDIUM	2012改款3.0 D-4D Double Cab窄体分支。	READY
25453_facelift_doublecab_wide	25453	Pickup	Hilux VII 2012 Facelift		4	EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	MEDIUM	2012改款3.0 D-4D Double Cab宽体分支。	READY
25454_prefl	25454	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
25454_facelift	25454	Sedan	A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
25455	25455	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2改款前四门轿车外廓。	READY
25456_prefl	25456	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖改款前车身。	READY
25456_facelift	25456	Sedan	A4 B8 Facelift	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖改款后车身。	READY
25457	25457	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25458	25458	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25459	25459	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25460	25460	Sedan	Mazda 6 II	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车外廓。	READY
25461_prefl	25461	Hatchback	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-01	MEDIUM	改款前1.8五门掀背分支。	READY
25461_facelift	25461	Hatchback	Mazda 6 II Facelift	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	MEDIUM	改款后1.8五门掀背分支。	READY
25462_prefl	25462	Hatchback	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	MEDIUM	改款前2.0五门掀背分支。	READY
25462_facelift	25462	Hatchback	Mazda 6 II Facelift	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-03	MEDIUM	改款后2.0五门掀背分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2101-2200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	4689	2019	1787	Auto-Data.net	https://www.auto-data.net/en/dodge-ramcharger-5.2-i-v8-172hp-2994
EU-DODGE-VIPER-SR-II-CONVERTIBLE-2D-01	4475	1924	1118	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-ii-convertible-generation-7337
EU-DODGE-VIPER-SR-I-CONVERTIBLE-2D-01	4448	1924	1117	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-i-generation-7336
EU-DODGE-VIPER-SR-II-COUPE-2D-01	4488	1923	1219	Auto-Data.net	https://www.auto-data.net/en/dodge-viper-sr-ii-coupe-generation-8225
EU-FORD-USA-CONTOUR-I-SEDAN-PREFL-01	4671	1755	1384	Edmunds	https://www.edmunds.com/ford/contour/1995/features-specs/
EU-FORD-USA-CONTOUR-I-SEDAN-FACELIFT-01	4707	1755	1384	Edmunds	https://www.edmunds.com/ford/contour/1998/features-specs/
EU-FORD-USA-CROWN-VICTORIA-I-SEDAN-4D-01	5385	1976	1443	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1997/1220075/ford_crown_victoria.html
EU-FORD-USA-EXPLORER-III-U152-SUV-5D-01	4813	1831	1826	Edmunds	https://www.edmunds.com/ford/explorer/2002/suv/st-100002015/features-specs/
EU-FORD-USA-THUNDERBIRD-XI-CONVERTIBLE-2D-01	4730	1829	1323	Auto-Data.net	https://www.auto-data.net/en/ford-thunderbird-retro-birds-4.0-i-v8-32v-283hp-8095
EU-HYUNDAI-EQUUS-I-SEDAN-4D-01	5065	1870	1465	Auto-Data.net	https://www.auto-data.net/en/hyundai-centennial-3.5-v6-210hp-13797
EU-LINCOLN-CONTINENTAL-IX-SEDAN-4D-01	5260	1870	1420	Auto-Data.net	https://www.auto-data.net/en/lincoln-continental-ix-generation-1799
EU-LINCOLN-TOWN-CAR-II-SEDAN-PREFL-01	5560	1953	1445	Edmunds 1993 Lincoln Town Car; Edmunds 1994 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1993/sedan/st-2837/features-specs/; https://www.edmunds.com/lincoln/town-car/1994/st-2834/features-specs/
EU-LINCOLN-TOWN-CAR-II-FACELIFT-SEDAN-01	5560	1948	1445	Edmunds 1995 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1995/sedan/st-2827/features-specs/
EU-LINCOLN-TOWN-CAR-III-SEDAN-01	5469	1986	1473	Edmunds 1998 Lincoln Town Car Signature	https://www.edmunds.com/lincoln/town-car/1998/sedan/st-14253/features-specs/
EU-LINCOLN-NAVIGATOR-I-SUV-5D-01	5202	2030	1948	Auto-Data.net	https://www.auto-data.net/en/lincoln-navigator-i-generation-1805
EU-NISSAN-QUEST-III-V42-MPV-5D-01	5184	1971	1778	Auto-Data.net	https://www.auto-data.net/en/nissan-quest-ff-l-3.5-i-v6-24v-233hp-772
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-1.2-tsi-105hp-20413
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426	Auto-Data.net	https://www.auto-data.net/en/peugeot-206-1.6-16v-109hp-5250
EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	3822	1652	1425	Auto-Data.net	https://www.auto-data.net/en/peugeot-206-facelift-2003-1.6i-16v-109hp-17900
EU-VW-PASSAT-B4-VARIANT-WAGON-5D-01	4595	1720	1445	Auto-Data.net	https://www.auto-data.net/en/volkswagen-passat-variant-b4-2.0-115hp-8987
EU-VW-GOLF-I-CABRIOLET-2D-01	3815	1630	1410	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-i-cabrio-generation-1883
EU-FIAT-MAREA-185-WEEKEND-WAGON-5D-01	4485	1740	1510	Auto-Data.net	https://www.auto-data.net/en/fiat-marea-weekend-185-1.6-100-16v-103hp-7208
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810	Auto-Data.net	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-generation-1275
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278	Auto-Data.net	https://www.auto-data.net/en/chevrolet-camaro-iii-generation-9044
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201	Edmunds 1992 Chevrolet Corvette Convertible	https://www.edmunds.com/chevrolet/corvette/1992/convertible/features-specs/
EU-VW-PASSAT-B5-5-SEDAN-4D-01	4703	1746	1462	Auto-Data.net	https://www.auto-data.net/en/volkswagen-passat-b5.5-2.8-30v-v6-193hp-4motion-43042
EU-HUMMER-H2-GMT840-SUV-5D-01	4820	2063	2080	Auto-Data.net	https://www.auto-data.net/en/hummer-h2-gmt-840-6.0i-v8-321hp-12494
EU-NISSAN-350Z-Z33-COUPE-01	4313	1815	1326	Automobile-Catalog.com	https://www.automobile-catalog.com/car/2008/2188925/nissan_350_z.html
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427	Auto-Data.net	https://www.auto-data.net/de/audi-a4-avant-b7-8e-3.0-tdi-v6-233hp-quattro-dpf-tiptronic-26721
EU-LOTUS-ELISE-S2-CONVERTIBLE-2D-01	3785	1719	1143	Auto-Data.net	https://www.auto-data.net/en/lotus-elise-series-2-1.8-i-16v-111r-192hp-8294
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog.com	https://www.automobile-catalog.com/car/2009/1996625/mitsubishi_lancer_de_cvt.html
EU-RENAULT-CLIO-II-PHASE-III-VAN-01	3811	1639	1417	Auto-Data.net	https://www.auto-data.net/en/renault-clio-ii-phase-iii-2003-3-door-generation-9002
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458	Auto-Data.net	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-generation-5607
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458	Auto-Data.net	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-generation-5607
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data.net	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-generation-5609
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495	Auto-Data.net	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-75hp-25673
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495	Auto-Data.net	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-generation-11029
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497	Auto-Data.net	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-1.6-16v-128hp-56146
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497	Auto-Data.net	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-5-door-generation-11031
EU-VW-GOLF-II-HATCHBACK-01	3985	1665	1415	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1987/30305/volkswagen_golf_1_6_gl.html
EU-HONDA-ODYSSEY-III-RL3-MPV-5D-01	5105	1958	1778	Edmunds	https://www.edmunds.com/honda/odyssey/2005/features-specs/
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r50-r53-cooper-s-1.6-i-16v-170hp-15332
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-iv-4.6-v8-32v-cobra-320hp-7792
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-iv-convertible-4.6-v8-32v-cobra-324hp-7782
EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	4843	1793	1394	Auto-Data.net	https://www.auto-data.net/en/chrysler-sebring-sedan-jr-2.4-i-16v-150hp-automatic-14810
EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	4430	1745	1415	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-156-932-2.0-jts-165hp-1487
EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	4435	1743	1430	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-156-932-facelift-2003-2.0-16v-jts-165hp-1469
EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	4190	1695	1375	Auto-Data.net	https://www.auto-data.net/en/honda-civic-vi-hatchback-generation-2630
EU-FORD-USA-EXPEDITION-II-U222-SUV-5D-01	5228	2000	1971	Auto-Data.net	https://www.auto-data.net/en/ford-expedition-ii-generation-1709
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-4WD-PREFL-01	5255	1760	1795	Toyota Hilux official technical specifications	https://media.toyota.co.uk/bigger-and-better-the-toyota-hilux-moves-one-size-up/
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-4WD-PREFL-01	5255	1835	1795	Toyota Hilux official technical specifications	https://media.toyota.co.uk/hilux-has-the-x-tra-factor/
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-NARROW-01	5130	1760	1810	Toyota Hilux official technical specifications	https://media.toyota.co.uk/bigger-and-better-the-toyota-hilux-moves-one-size-up/
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-4WD-PREFL-WIDE-01	5255	1835	1810	Toyota Hilux official technical specifications	https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2012-FACELIFT-01	5260	1760	1795	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK-.pdf
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2012-FACELIFT-01	5260	1760	1835	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK-.pdf
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-NARROW-01	5260	1760	1850	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK-.pdf
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2012-FACELIFT-WIDE-01	5260	1835	1850	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK-.pdf
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	4887	1717	1694	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	4887	1717	1648	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	5258	1717	1694	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	5258	1717	1648	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	5258	1717	1702	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	5258	1717	1656	Chevrolet Colorado 2006 brochure	https://xr793.com/wp-content/uploads/2017/07/2006-Chevrolet-Colorado-CN.pdf
EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	5052	2013	1688	Auto-Data.net	https://www.auto-data.net/en/chrysler-pacifica-3.5-v6-253hp-awd-14715
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887	Auto-Data.net	https://www.auto-data.net/en/dodge-durango-ii-hb-facelift-2006-generation-6906
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351	Carspecsguru	https://www.carspecsguru.com/cadillac/seville/494/745/modification-6341
EU-NISSAN-CEFIRO-II-A32-SEDAN-4D-01	4760	1770	1410	Auto-Data.net	https://www.auto-data.net/en/nissan-cefiro-32-2.0i-v6-24v-155hp-automatic-25039
EU-NISSAN-CEFIRO-III-A33-SEDAN-4D-01	4920	1780	1435	Auto-Data.net	https://www.auto-data.net/en/nissan-maxima-qx-v-a33-3.0-v6-24v-200hp-automatic-24982
EU-NISSAN-SKYLINE-R32-COUPE-2D-01	4530	1695	1325	Nissan Heritage Collection	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/Skyline_GTS-t_TypeM.html
EU-NISSAN-SKYLINE-R34-COUPE-2D-01	4580	1725	1340	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1999/2137790/nissan_skyline_2door_sports_coupe_25gt_turbo.html
EU-TOYOTA-FORTUNER-I-TGN61-SUV-PRE2011-01	4695	1840	1850	Toyota Fortuner brochure	https://id.scribd.com/document/77881333/Toyota-Fortuner-Brochure
EU-TOYOTA-FORTUNER-I-TGN61-SUV-2011-FACELIFT-01	4705	1840	1850	Toyota Fortuner 2012 brochure	https://es.scribd.com/document/533338815/Toyota-Fortuner-Brochure-2012
EU-NISSAN-SKYLINE-R33-GTS4-COUPE-2D-01	4640	1720	1355	Goo-net Exchange	https://www.goo-net-exchange.com/catalog/NISSAN__SKYLINE/1501399/
EU-NISSAN-SKYLINE-R32-SEDAN-4D-01	4580	1695	1360	Automobile-Catalog.com	https://www.automobile-catalog.com/car/1992/2135255/nissan_skyline_4door_sports_sedan_gts-4.html
EU-LAND-ROVER-DISCOVERY-III-L319-SUV-5D-01	4835	2009	1887	Auto-Data.net	https://www.auto-data.net/en/land-rover-discovery-iii-generation-1216
EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	4410	1830	1675	Auto-Data.net	https://www.auto-data.net/en/ssangyong-korando-iii-c-generation-4641
EU-HUMMER-H3-GMT345-SUV-5D-01	4742	1897	1893	Auto-Data.net	https://www.auto-data.net/en/hummer-h3-generation-5530
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-01	4922	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-v6-231hp-g-tronic-37164
EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-01	5157	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-r-280-v6-231hp-g-tronic-37188
EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-PREFL-01	4938	1922	1661	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-500-v8-388hp-4matic-7g-tronic-54142
EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-PREFL-01	5157	1922	1674	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-r-500-v8-388hp-4matic-g-tronic-37236
EU-MERCEDES-BENZ-R-CLASS-W251-R500-MPV-FACELIFT-01	4922	1922	1674	Mercedes-Benz R-Class official brochure	https://ragtop.org/mbbrochures/2012/new-zealand/r251_Brochure.pdf
EU-MERCEDES-BENZ-R-CLASS-V251-R500-LWB-MPV-FACELIFT-01	5157	1922	1674	Mercedes-Benz R-Class official brochure	https://ragtop.org/mbbrochures/2012/new-zealand/r251_Brochure.pdf
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-5D-02	4922	1922	1659	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-cdi-v6-190hp-g-tronic-37168
EU-MERCEDES-BENZ-R-CLASS-V251-LWB-MPV-5D-02	5157	1922	1659	Auto-Data.net	https://www.auto-data.net/es/mercedes-benz-r-class-long-v251-r-280-cdi-v6-190hp-g-tronic-37190
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423	Auto-Data.net	https://www.auto-data.net/en/bmw-1-series-coupe-e82-125i-218hp-9837
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411	Auto-Data.net	https://www.auto-data.net/en/bmw-1-series-convertible-e88-118i-143hp-steptronic-9826
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-525d-197hp-xdrive-28189
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-525xd-197hp-28203
EU-HYUNDAI-I30-FD-CW-WAGON-5D-01	4475	1775	1565	Auto-Data.net	https://www.auto-data.net/en/hyundai-i30-i-cw-2.0-143hp-automatic-30922
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680	Toyota Hilux official technical specifications	https://media.toyota.co.uk/bigger-and-better-the-toyota-hilux-moves-one-size-up/
EU-TOYOTA-HILUX-VII-PICKUP-EXTRA-CAB-2WD-PREFL-01	5255	1760	1680	Toyota Hilux official technical specifications	https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-PICKUP-DOUBLE-CAB-2WD-PREFL-01	5255	1760	1695	Toyota Hilux official technical specifications	https://newsroom.toyota.eu/2006-paris-motor-show/
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b8-8k-2.7-tdi-v6-190hp-4317
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b8-8k-facelift-2011-generation-4129
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-sedan-gh-2.0-147hp-44555; https://www.auto-data.net/en/mazda-6-ii-sedan-gh-facelift-2010-2.0-155hp-16773
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-1.8-120hp-16780
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-2.0-147hp-16781; https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-1.8-120hp-44573
EU-MAZDA-6-II-GH-HATCHBACK-03	4765	1795	1440	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-hatchback-gh-facelift-2010-2.0i-155hp-17509
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2101-2200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://newsroom.toyota.eu/2006-paris-motor-show/ "2006 Paris Motor Show"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2101-2200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2101-2200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3084 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1584 行）

