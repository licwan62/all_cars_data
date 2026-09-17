# 任务：all 第 6001-6100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0061__a8db7f89


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6001-6100 行

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
all 第 6001-6100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6001-6100_ktype_dimension_mapping_final.tsv
- all_6001-6100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	4399	1660	1431
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	4230	1650	1358
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	4237	1682	1370
EU-CITROEN-DS4-I-HATCHBACK-01	4275	1810	1523
EU-CITROEN-DS-SERIES-2-SEDAN-01	4838	1790	1470
EU-CITROEN-DS-SERIES-3-SEDAN-01	4874	1803	1470
EU-CITROEN-DS-SERIES-3-WAGON-01	5026	1803	1530
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330
EU-FORD-CAPRI-II-COUPE-01	4286	1695	1295
EU-FORD-CAPRI-III-COUPE-01	4440	1700	1350
EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	4129	1640	1568
EU-FORD-ESCORT-III-CONVERTIBLE-01	4010	1640	1403
EU-FORD-ESCORT-III-HATCHBACK-3D-01	3966	1640	1337
EU-FORD-ESCORT-III-HATCHBACK-5D-01	3966	1640	1337
EU-FORD-ESCORT-III-HATCHBACK-EARLY-01	3970	1640	1400
EU-FORD-ESCORT-III-HATCHBACK-LATE-01	3970	1640	1384
EU-FORD-ESCORT-III-WAGON-01	4033	1640	1385
EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	4150	1590	1410
EU-FORD-ESCORT-II-SEDAN-01	3978	1596	1398
EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	3977	1570	1393
EU-FORD-ESCORT-I-SEDAN-PREFL-01	3978	1572	1402
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	4181	1640	1568
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	4181	1640	1594
EU-FORD-ESCORT-IV-CONVERTIBLE-01	4022	1640	1375
EU-FORD-ESCORT-IV-HATCHBACK-01	4022	1640	1385
EU-FORD-ESCORT-IV-HATCHBACK-RS-TURBO-01	4061	1650	1354
EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	4022	1640	1385
EU-FORD-ESCORT-IV-HATCHBACK-XR3I-01	4061	1640	1354
EU-FORD-ESCORT-IV-WAGON-01	4080	1640	1390
EU-FORD-TAUNUS-TC1-SEDAN-2D-01	4267	1701	1370
EU-FORD-TAUNUS-TC1-SEDAN-4D-01	4267	1701	1370
EU-FORD-TAUNUS-TC2-SEDAN-01	4267	1700	1370
EU-FORD-TAUNUS-TC2-SEDAN-2D-01	4380	1700	1362
EU-FORD-TAUNUS-TC2-SEDAN-4D-01	4380	1700	1362
EU-FORD-TAUNUS-TC2-WAGON-01	4440	1700	1366
EU-FORD-TAUNUS-TC3-SEDAN-2D-01	4340	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-2D-2P3-GHIA-01	4382	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-4D-01	4340	1706	1363
EU-FORD-TAUNUS-TC3-SEDAN-4D-2P3-GHIA-01	4382	1706	1363
EU-FORD-TAUNUS-TC3-WAGON-01	4440	1712	1355
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Capri	1500	Coupe	Heckantrieb	Benzin	44	60	Dec 1968	Feb 1974	2025-02-03	6416
Ford	Capri	1500	Coupe	Heckantrieb	Benzin	48	65	Dec 1968	Feb 1974	2025-02-03	6417
Ford	Capri	2000	Coupe	Heckantrieb	Benzin	63	86	Feb 1969	Jun 1971	2025-02-03	6418
Ford	Capri	2000	Coupe	Heckantrieb	Benzin	66	90	Feb 1969	Feb 1974	2025-02-03	6419
Ford	Capri	2300	Coupe	Heckantrieb	Benzin	79	108	Feb 1969	Feb 1974	2025-02-03	6420
Ford	Capri	2300	Coupe	Heckantrieb	Benzin	92	125	Aug 1969	Feb 1974	2025-02-03	6421
Ford	Capri	2600	Coupe	Heckantrieb	Benzin	92	125	Aug 1970	Feb 1974	2025-02-03	6422
Citroën	Bx	14	Schrägheck	Frontantrieb	Benzin	47	64	Jan 1989	Dec 1989	2024-03-01	6423
Citroën	Bx	19 GTI 16V	Schrägheck	Frontantrieb	Benzin	116	158	Sep 1987	Dec 1988	2024-03-01	6424
Ford	Escort i	1100	Stufenheck	Heckantrieb	Benzin	35	48	Jun 1970	Feb 1976	2024-03-01	6425
Ford	Escort i	1100	Stufenheck	Heckantrieb	Benzin	29	40	Jun 1968	Jun 1971	2024-03-01	6426
Ford	Escort i	1100	Stufenheck	Heckantrieb	Benzin	33	45	Jun 1968	Jun 1971	2024-03-01	6427
Ford	Escort i	1300	Stufenheck	Heckantrieb	Benzin	35	48	Jun 1968	Jun 1971	2024-03-01	6428
Ford	Escort i	1300	Stufenheck	Heckantrieb	Benzin	38	52	Jun 1968	Jun 1971	2024-03-01	6429
Ford	Escort i	1300	Stufenheck	Heckantrieb	Benzin	40	54	Sep 1973	Feb 1976	2024-03-01	6430
Ford	Escort i	1300	Stufenheck	Heckantrieb	Benzin	42	57	Jun 1970	Feb 1976	2024-03-01	6431
Ford	Escort i	1300 GT	Stufenheck	Heckantrieb	Benzin	47	64	Jun 1968	Jun 1971	2024-03-01	6432
Ford	Escort i	1300	Stufenheck	Heckantrieb	Benzin	53	72	Jun 1970	Feb 1976	2024-03-01	6433
Ford	Escort i turnier	1100	Kombi	Heckantrieb	Benzin	29	40	Jun 1968	Jun 1971	2024-03-01	6434
Ford	Escort i turnier	1100	Kombi	Heckantrieb	Benzin	35	48	Jun 1970	Feb 1976	2024-03-01	6435
Ford	Escort i turnier	1100	Kombi	Heckantrieb	Benzin	32	44	Jun 1970	Feb 1976	2024-03-01	6436
Ford	Escort i turnier	1300	Kombi	Heckantrieb	Benzin	42	57	Jun 1970	Feb 1976	2024-03-01	6437
Mercedes-benz	A-Klasse	E-cell	Schrägheck	Frontantrieb	Elektro	50	68	Dec 2010	Jun 2012	2024-03-01	6438
Citroën	C4 picasso i	1.6 THP 155	Großraumlimousine	Frontantrieb	Benzin	115	156	Sep 2010	Aug 2013	2024-03-01	6440
Audi	Tt	2.0 Tfsi	Coupe	Frontantrieb	Benzin	155	211	May 2010	Jun 2014	2024-03-01	6441
Citroën	C4 picasso i	1.6 HDI 110	Großraumlimousine	Frontantrieb	Diesel	82	112	Sep 2010	Aug 2013	2024-03-01	6442
Mini	Mini	Cooper SD All4	Kombi	Allrad	Diesel	100	136	Mar 2011	Oct 2016	2024-03-01	6443
Citroën	Bx	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Oct 1985	Sep 1993	2024-03-01	6444
Ford	Taunus	12M	Stufenheck	Heckantrieb	Benzin	25	34	Jan 1951	Aug 1953	2024-03-01	6445
Ford	Taunus	1.2	Stufenheck	Heckantrieb	Benzin	28	38	Dec 1951	Feb 1963	2024-03-01	6446
Ford	Taunus	1.2	Kombi	Heckantrieb	Benzin	28	38	May 1953	Feb 1963	2024-03-01	6447
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	40	54	Jul 1959	Feb 1963	2024-03-01	6448
Mini	Mini	Cooper SD	Schrägheck	Frontantrieb	Diesel	100	136	Feb 2011	Nov 2013	2024-03-01	6449
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	70	95	Dec 1987	Dec 1989	2024-03-01	6450
Ford	Taunus	1.2	Stufenheck	Frontantrieb	Benzin	29	39	Jul 1962	Apr 1967	2024-03-01	6451
Ford	Taunus	1.5	Stufenheck	Frontantrieb	Benzin	37	50	Jul 1962	Apr 1967	2024-03-01	6452
Ford	Taunus	1.5 TS	Stufenheck	Frontantrieb	Benzin	40	54	Dec 1962	Apr 1967	2024-03-01	6453
Ford	Taunus	1.5 TS	Stufenheck	Frontantrieb	Benzin	48	65	Dec 1962	Apr 1967	2024-03-01	6454
Ford	Taunus	1.5 TS	Coupe	Frontantrieb	Benzin	37	50	Dec 1962	Apr 1967	2024-03-01	6455
Ford	Taunus	1.5 TS	Coupe	Frontantrieb	Benzin	40	54	Dec 1962	Apr 1967	2024-03-01	6456
Ford	Taunus	1.5 TS	Coupe	Frontantrieb	Benzin	48	65	Dec 1962	Apr 1967	2024-03-01	6457
Ford	Taunus	1.2	Kombi	Frontantrieb	Benzin	29	39	Apr 1963	Apr 1967	2024-03-01	6458
Ford	Taunus	1.5	Kombi	Frontantrieb	Benzin	37	50	Apr 1963	Apr 1967	2024-03-01	6459
Ford	Taunus	1.2	Stufenheck	Frontantrieb	Benzin	33	45	Aug 1966	Jun 1971	2024-03-01	6460
Ford	Taunus	1.3	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1966	Jun 1971	2024-03-01	6461
Ford	Taunus	1.5	Stufenheck	Frontantrieb	Benzin	40	54	Aug 1966	Jun 1971	2024-03-01	6462
Ford	Taunus	1.3	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1966	Jun 1971	2024-03-01	6463
Ford	Taunus	1.3	Coupe	Frontantrieb	Benzin	37	50	Aug 1966	Jun 1971	2024-03-01	6464
Ford	Taunus	1.3	Kombi	Frontantrieb	Benzin	37	50	Sep 1966	Jun 1971	2024-03-01	6465
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	40	54	Dec 1954	Sep 1958	2024-03-01	6466
Ford	Taunus	1.5	Stufenheck	Frontantrieb	Benzin	40	54	Aug 1966	Jun 1971	2024-03-01	6467
Ford	Taunus	1.5	Stufenheck	Frontantrieb	Benzin	40	54	Aug 1966	Jun 1971	2024-03-01	6468
Ford	Taunus	1.5	Coupe	Frontantrieb	Benzin	40	54	Jan 1968	Jun 1971	2024-03-01	6469
Ford	Taunus	1.5	Coupe	Frontantrieb	Benzin	48	65	Aug 1966	Jun 1971	2024-03-01	6470
Ford	Taunus	1.7	Coupe	Frontantrieb	Benzin	51	69	Jan 1968	Jun 1971	2024-03-01	6471
Ford	Taunus	1.7	Coupe	Frontantrieb	Benzin	55	75	Jul 1968	Jun 1971	2024-03-01	6472
Ford	Taunus	1.5	Kombi	Frontantrieb	Benzin	40	54	Sep 1966	Jul 1971	2024-03-01	6473
Ford	Taunus	1.5 Xl/rs	Stufenheck	Frontantrieb	Benzin	40	54	Jan 1968	Jun 1971	2024-03-01	6474
Ford	Taunus	1.5 Xl/rs	Stufenheck	Frontantrieb	Benzin	48	65	Aug 1966	Jun 1971	2024-03-01	6475
Ford	Taunus	1.7 Xl/rs	Stufenheck	Frontantrieb	Benzin	51	69	Jan 1968	Jun 1971	2024-03-01	6476
Ford	Taunus	1.7 Xl/rs	Stufenheck	Frontantrieb	Benzin	55	75	Jul 1968	Jun 1971	2024-03-01	6477
Ford	Taunus	1.5 Xl/rs	Stufenheck	Frontantrieb	Benzin	40	54	Jan 1968	Jun 1971	2024-03-01	6478
Ford	Taunus	1.5 Xl/rs	Stufenheck	Frontantrieb	Benzin	48	65	Aug 1966	Jun 1971	2024-03-01	6479
Citroën	Id	19 P	Stufenheck	Frontantrieb	Benzin	51	69	Aug 1959	Sep 1964	2024-03-01	6480
Citroën	Id	19 P	Stufenheck	Frontantrieb	Benzin	54	73	Sep 1964	Sep 1969	2024-03-01	6481
Citroën	Id	19 B	Stufenheck	Frontantrieb	Benzin	57	78	Sep 1964	Aug 1975	2024-03-01	6482
Citroën	Id	19 F	Stufenheck	Frontantrieb	Benzin	59	80	Mar 1965	Oct 1972	2024-03-01	6483
Citroën	Id	19 B	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1971	Aug 1975	2024-03-01	6484
Citroën	Id	19 F Super	Stufenheck	Frontantrieb	Benzin	62	84	Jan 1966	Oct 1972	2024-03-01	6485
Citroën	Id	20	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1969	Aug 1975	2024-03-01	6486
Citroën	Id	20	Stufenheck	Frontantrieb	Benzin	72	98	Nov 1971	Aug 1975	2024-03-01	6487
Citroën	Id	21 F	Stufenheck	Frontantrieb	Benzin	74	101	Apr 1966	Nov 1972	2024-03-01	6488
Citroën	Id	21 F	Stufenheck	Frontantrieb	Benzin	76	103	Feb 1969	Nov 1972	2024-03-01	6489
Citroën	Id	19 F	Kombi	Frontantrieb	Benzin	62	84	Jan 1966	Oct 1972	2024-03-01	6490
Citroën	Id	20 F	Kombi	Frontantrieb	Benzin	66	90	Feb 1969	Oct 1972	2024-03-01	6491
Citroën	Id	20 F	Kombi	Frontantrieb	Benzin	72	98	Nov 1971	Aug 1975	2024-03-01	6493
Citroën	Id	21 F	Kombi	Frontantrieb	Benzin	74	101	Apr 1966	Nov 1972	2024-03-01	6494
Citroën	Id	21 F	Kombi	Frontantrieb	Benzin	76	103	Feb 1969	Nov 1972	2024-03-01	6495
Audi	Tt	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	155	211	May 2010	Jun 2014	2024-03-01	6496
Citroën	Ds	19	Stufenheck	Frontantrieb	Benzin	62	84	Apr 1966	Oct 1972	2024-03-01	6497
Citroën	Ds	19	Stufenheck	Frontantrieb	Benzin	59	80	May 1959	Apr 1966	2024-03-01	6498
Citroën	Ds	20	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1968	Oct 1972	2024-03-01	6500
Citroën	Ds	21	Stufenheck	Frontantrieb	Benzin	88	120	Dec 1969	Aug 1975	2024-03-01	6501
Citroën	Ami	6	Stufenheck	Frontantrieb	Benzin	24	33	May 1968	Jul 1969	2024-03-01	6502
Citroën	Ami	8	Stufenheck	Frontantrieb	Benzin	24	33	Jul 1969	Dec 1977	2024-03-01	6503
Citroën	Ami	6	Stufenheck	Frontantrieb	Benzin	18	24	Jan 1963	May 1968	2024-03-01	6504
Citroën	Ami	10 Super	Stufenheck	Frontantrieb	Benzin	40	54	Mar 1973	Dec 1977	2024-03-01	6505
Citroën	Ami	6	Kombi	Frontantrieb	Benzin	24	33	May 1968	Jul 1969	2024-03-01	6506
Citroën	Ami	10 Super	Kombi	Frontantrieb	Benzin	40	54	Mar 1973	Dec 1977	2024-03-01	6507
Citroën	Ami	8	Kombi	Frontantrieb	Benzin	24	33	Jul 1969	Dec 1977	2024-03-01	6508
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1957	Nov 1960	2024-03-01	6509
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	44	60	Aug 1957	Nov 1960	2024-03-01	6510
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	40	54	Sep 1960	Jan 1965	2024-03-01	6511
Ford	Taunus	1.7 S	Stufenheck	Heckantrieb	Benzin	48	65	Sep 1960	Jan 1965	2024-03-01	6512
Ford	Taunus	1.7 S	Coupe	Heckantrieb	Benzin	55	75	Nov 1961	Jan 1965	2024-03-01	6513
Ford	Taunus	1.5	Kombi	Heckantrieb	Benzin	40	54	Dec 1960	Jan 1965	2024-03-01	6514
Ford	Taunus	1.7 S	Kombi	Heckantrieb	Benzin	48	65	Dec 1960	Jan 1965	2024-03-01	6515
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1964	Oct 1968	2024-03-01	6516
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	48	65	Sep 1964	Oct 1968	2024-03-01	6517
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	51	69	Sep 1964	Oct 1968	2024-03-01	6518


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成 Capri I、BX 普通车身、BX Break、MINI R56，以及 DS/ID 已有尺寸组的批量关联。
* Ktype `6424` 的 BX 19 GTI 16V 为 `4237 × 1690 × 1350 mm`，与普通 BX Phase II 的 `4237 × 1682 × 1360 mm` 不同，已独立创建 16V 尺寸组。([汽车目录][1])
* 已首次闭合 Mercedes-Benz A-Class W169、Citroën C4 Picasso I facelift、Audi TT 8J facelift 三个尺寸组。A-Class 官方尺寸图明确给出 `3883 × 1764 × 1593 mm`。
* C4 Picasso facelift 已确认 `4468 × 1831 × 1610 mm`；TT 8J facelift Coupé 已确认 `4187 × 1842 × 1353 mm`，宽度均为不含后视镜口径。([汽车目录][2])
* DS Series II、Series III 的尺寸边界与已有缓存一致；跨系列的 Ktype `6497` 已拆成两个稳定派生映射。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：26
* READY 映射行：28
* PENDING 输入 Ktype：74
* 已引用尺寸组：12

  * 复用已有组：8
  * 本轮首次创建：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6416	6416	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6417	6417	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6418	6418	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6419	6419	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6420	6420	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6421	6421	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6422	6422	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6423	6423	Hatchback	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
6424	6424	Hatchback	BX I Phase II 16V	XB	5	EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	HIGH	16V宽体及低车高外廓。	READY
6438	6438	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-01	HIGH	E-CELL未改变W169五门车身外廓。	READY
6440	6440	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	HIGH		READY
6441	6441	Coupe	TT 8J facelift	8J3	3	EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	HIGH		READY
6442	6442	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	HIGH		READY
6444_phasei	6444	Hatchback	BX I Phase I	XB	5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越BX Phase I与Phase II外廓。	READY
6444_phaseii	6444	Hatchback	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越BX Phase I与Phase II外廓。	READY
6449	6449	Hatchback	MINI R56 facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
6450	6450	Wagon	BX I Phase II Break	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH		READY
6484	6484	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6486	6486	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6487	6487	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6491	6491	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6493	6493	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6495	6495	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6496	6496	Coupe	TT 8J facelift	8J3	3	EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	HIGH	Quattro未改变标准TT Coupé外廓。	READY
6497_series2	6497	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6497_series3	6497	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6500	6500	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
6501	6501	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	4237	1690	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/54755/citroen_bx_19_gti_16v.html
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-01	3883	1764	1593	Mercedes-Benz A-Class official brochure	https://ragtop.org/mbbrochures/2012/ireland/20111011A-Class_WC169_0611_021.pdf
EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	4468	1831	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1215515/citroen_c4_picasso_hdi_110_fap_exclusive_esg6.html
EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	4187	1842	1353	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1337060/audi_tt_coupe_2_0_tfsi_quattro_s-tronic.html
```

## 下一步优先处理

1. 按 P1、P2、P3、P4、P5、P6 聚类闭合 Ford Taunus 的 Sedan、Coupe、Wagon 尺寸组。
2. 核对 Escort I 德国规格与生产区间，避免将市场规格差异误判为单纯 facelift。
3. 闭合 Citroën Ami 6、Ami 8、Ami 10 的 Sedan 与 Wagon。
4. 补齐早期 ID/DS Series 1、Series 2 Wagon，以及跨系列 Ktype 的派生映射。
5. 核对 Ktype `6443` 实际对应的 MINI Countryman R60 Cooper SD ALL4，而非 MINI Clubman。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/54755/citroen_bx_19_gti_16v.html?utm_source=chatgpt.com "1988 Citroen BX 19 GTI 16V Specs Review (117.5 kW / 160 PS / 158 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2010/1215515/citroen_c4_picasso_hdi_110_fap_exclusive_esg6.html?utm_source=chatgpt.com "2010 Citroen C4 Picasso HDi 110 FAP Exclusive EGS6 ..."
[3]: https://www.auto-data.net/en/citroen-ds-model-1691?utm_source=chatgpt.com "Citroen DS | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6001-6100_ktype_dimension_mapping_final.tsv
- all_6001-6100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Ford Taunus P4 的标准 Sedan、TS 长车身 Sedan、Coupe 和 Wagon 四个尺寸组。P4 标准 Sedan 与 TS Sedan 长度不同，不能合并。([汽车目录][1])
* 闭合 Ford Taunus P6 的 Sedan、Coupe 和 Wagon 三个尺寸组；Coupe 与 Sedan 车高不同，Wagon 同时具有不同长度和车高。([汽车目录][2])
* 闭合 Ford Taunus P3 的 Sedan 与 Wagon 尺寸组。Ktype `6513` 所指稀有 Coupe 仍需独立核对，未直接套用 Sedan 尺寸。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：58
* READY 映射行：60
* PENDING 输入 Ktype：42
* 已确认并引用尺寸组：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6451	6451	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	HIGH		READY
6452	6452	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	HIGH		READY
6453	6453	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-TS-01	HIGH	TS长车身外廓。	READY
6454	6454	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-TS-01	HIGH	TS长车身外廓。	READY
6455	6455	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6456	6456	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6457	6457	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6458	6458	Wagon	Taunus P4	P4	3	EU-FORD-TAUNUS-P4-WAGON-3D-01	HIGH		READY
6459	6459	Wagon	Taunus P4	P4	3	EU-FORD-TAUNUS-P4-WAGON-3D-01	HIGH		READY
6460	6460	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6461	6461	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6462	6462	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6463	6463	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6464	6464	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6465	6465	Wagon	Taunus P6	P6	3	EU-FORD-TAUNUS-P6-WAGON-3D-01	HIGH		READY
6467	6467	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6468	6468	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6469	6469	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6470	6470	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6471	6471	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6472	6472	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6473	6473	Wagon	Taunus P6	P6	3	EU-FORD-TAUNUS-P6-WAGON-3D-01	HIGH		READY
6474	6474	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6475	6475	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6476	6476	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6477	6477	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6478	6478	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6479	6479	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6511	6511	Sedan	Taunus P3	P3		EU-FORD-TAUNUS-P3-SEDAN-01	HIGH		READY
6512	6512	Sedan	Taunus P3	P3		EU-FORD-TAUNUS-P3-SEDAN-01	HIGH		READY
6514	6514	Wagon	Taunus P3	P3	3	EU-FORD-TAUNUS-P3-WAGON-3D-01	HIGH		READY
6515	6515	Wagon	Taunus P3	P3	3	EU-FORD-TAUNUS-P3-WAGON-3D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	4248	1594	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/899945/ford_taunus_12m_1_2l.html
EU-FORD-TAUNUS-P4-SEDAN-TS-01	4322	1594	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/900020/ford_taunus_12m_ts.html
EU-FORD-TAUNUS-P4-COUPE-01	4322	1594	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/900050/ford_taunus_12m_ts_coupe.html
EU-FORD-TAUNUS-P4-WAGON-3D-01	4248	1594	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/899990/ford_taunus_12m_kombi_1_5l.html
EU-FORD-TAUNUS-P6-SEDAN-01	4389	1603	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/900080/ford_15m_ts_1700_s.html
EU-FORD-TAUNUS-P6-COUPE-2D-01	4389	1603	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/900530/ford_12m_coupe_1700_s.html
EU-FORD-TAUNUS-P6-WAGON-3D-01	4318	1603	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/900455/ford_15m_turnier_1700_s.html
EU-FORD-TAUNUS-P3-SEDAN-01	4452	1670	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899630/ford_taunus_17m_1_5l.html
EU-FORD-TAUNUS-P3-WAGON-3D-01	4452	1670	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899855/ford_taunus_17m_turnier_325_1_7l.html
```

## 下一步优先处理

1. 闭合 Taunus G13/G4、P2、P5，并单独处理 Ktype `6513` 的 P3 Coupe。
2. 完成 Escort I Sedan 跨前后期派生及 Turnier 尺寸组。
3. 批量关联剩余 ID/DS Series 2、Series 3 Sedan 与 Wagon。
4. 闭合 Citroën Ami 6、Ami 8、Ami 10，以及 MINI Countryman R60。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1965/899945/ford_taunus_12m_1_2l.html?utm_source=chatgpt.com "1965 Ford Taunus 12M Limousine 2 Turen 1.2L (man. 4)"
[2]: https://www.automobile-catalog.com/car/1966/900080/ford_15m_ts_1700_s.html?utm_source=chatgpt.com "1966 Ford 15M TS 1700 S Specs Review (51.5 kW ..."
[3]: https://www.automobile-catalog.com/car/1961/899630/ford_taunus_17m_1_5l.html?utm_source=chatgpt.com "1961 Ford Taunus 17M 1.5L Specs Review (40.5 kW ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6001-6100_ktype_dimension_mapping_final.tsv
- all_6001-6100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 MINI Countryman R60 Cooper SD ALL4：官方技术资料确认其为五门 SAV/SUV，并采用 Cooper S/SD 外观车身尺寸组。([BMW Group PressClub][1])
* 完成剩余 Citroën ID/DS 映射。首次补建 DS Series 1 Sedan 与 Series 2 Wagon；Series 2、Series 3 已有尺寸组直接复用。([汽车目录][2])
* 闭合 Ami 6、Ami 8 的 Sedan/Wagon 四个物理尺寸组；Ami Super 与 Ami 8 对应车身三维一致，直接复用 Ami 8 组。([汽车数据][3])
* Taunus P2 Sedan 按 1959 年车顶改型拆为 prefl 与 facelift；P2 Wagon 前后期三维不变，保持单一尺寸组。([汽车目录][4])
* Ktype `6516`—`6518` 的生产区间跨越 P5、P7A、P7B 三种不同外廓，已分别派生并链接三个尺寸组。([汽车目录][5])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：81
* READY 映射行：99
* PENDING 输入 Ktype：19
* 已确认并引用尺寸组：34
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6443	6443	SUV	MINI Countryman R60	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-S-BODY-01	HIGH	Cooper SD ALL4使用S外观车身。	READY
6480_series1	6480	Sedan	DS Series 1		4	EU-CITROEN-DS-SERIES-1-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6480_series2	6480	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6481_series2	6481	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6481_series3	6481	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6482_series2	6482	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6482_series3	6482	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6483_series2	6483	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6483_series3	6483	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6485_series2	6485	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6485_series3	6485	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6488_series2	6488	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6488_series3	6488	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6489	6489	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
6490_series2	6490	Wagon	DS Series 2		5	EU-CITROEN-DS-SERIES-2-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6490_series3	6490	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6494_series2	6494	Wagon	DS Series 2		5	EU-CITROEN-DS-SERIES-2-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6494_series3	6494	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6498_series1	6498	Sedan	DS Series 1		4	EU-CITROEN-DS-SERIES-1-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6498_series2	6498	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6502	6502	Sedan	Ami 6		4	EU-CITROEN-AMI-6-SEDAN-4D-01	HIGH		READY
6503	6503	Sedan	Ami 8		4	EU-CITROEN-AMI-8-SEDAN-4D-01	HIGH		READY
6504	6504	Sedan	Ami 6		4	EU-CITROEN-AMI-6-SEDAN-4D-01	HIGH		READY
6505	6505	Sedan	Ami Super		4	EU-CITROEN-AMI-8-SEDAN-4D-01	HIGH	Ami Super采用Ami 8四门车身外廓。	READY
6506	6506	Wagon	Ami 6		5	EU-CITROEN-AMI-6-WAGON-5D-01	HIGH		READY
6507	6507	Wagon	Ami Super		5	EU-CITROEN-AMI-8-WAGON-5D-01	HIGH	Ami Super Break采用Ami 8 Break车身外廓。	READY
6508	6508	Wagon	Ami 8		5	EU-CITROEN-AMI-8-WAGON-5D-01	HIGH		READY
6509_prefl	6509	Sedan	Taunus P2	P2		EU-FORD-TAUNUS-P2-SEDAN-PREFL-01	HIGH	Ktype跨越P2车顶改型前后两种外廓。	READY
6509_facelift	6509	Sedan	Taunus P2	P2		EU-FORD-TAUNUS-P2-SEDAN-FACELIFT-01	HIGH	Ktype跨越P2车顶改型前后两种外廓。	READY
6510	6510	Wagon	Taunus P2	P2	3	EU-FORD-TAUNUS-P2-WAGON-3D-01	HIGH		READY
6516_p5	6516	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6516_p7a	6516	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6516_p7b	6516	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p5	6517	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p7a	6517	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p7b	6517	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p5	6518	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p7a	6518	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p7b	6518	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-COUNTRYMAN-R60-SUV-5D-S-BODY-01	4110	1789	1561	BMW Group MINI Countryman official technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0097277EN_GB/144746
EU-CITROEN-DS-SERIES-1-SEDAN-01	4800	1790	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/126995/citroen_ds_19.html
EU-CITROEN-DS-SERIES-2-WAGON-01	4990	1790	1530	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/127670/citroen_break_19.html
EU-CITROEN-AMI-6-SEDAN-4D-01	3940	1520	1490	Auto-Data	https://www.auto-data.net/en/citroen-ami-6-generation-3308
EU-CITROEN-AMI-6-WAGON-5D-01	3960	1520	1490	Auto-Data	https://www.auto-data.net/en/citroen-ami-model-1684
EU-CITROEN-AMI-8-SEDAN-4D-01	3990	1520	1485	Auto-Data	https://www.auto-data.net/en/citroen-ami-8-generation-5264
EU-CITROEN-AMI-8-WAGON-5D-01	3990	1520	1520	Auto-Data	https://www.auto-data.net/en/citroen-ami-model-1684
EU-FORD-TAUNUS-P2-SEDAN-PREFL-01	4375	1670	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1957/899390/ford_taunus_17m.html
EU-FORD-TAUNUS-P2-SEDAN-FACELIFT-01	4375	1670	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/899510/ford_taunus_17m.html
EU-FORD-TAUNUS-P2-WAGON-3D-01	4375	1670	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/899615/ford_taunus_17m_kombi_de_luxe_4-speed.html
EU-FORD-TAUNUS-P5-SEDAN-01	4585	1715	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/900695/ford_taunus_17m_1_5l.html
EU-FORD-TAUNUS-P7A-17M-SEDAN-01	4663	1756	1494	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/901205/ford_17m_1700_s.html
EU-FORD-TAUNUS-P7B-17M-SEDAN-01	4721	1756	1478	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/901820/ford_17m_1500_4-speed.html
```

## 下一步优先处理

1. 闭合 Escort I Sedan 的早期/后期映射边界及 Escort I Turnier 尺寸组。
2. 处理 Taunus G13/G4B 的 Sedan、Wagon 及跨改型 Ktype。
3. 独立核对 Ktype `6466` 的 Taunus 15M G13/G4B 边界。
4. 闭合 Ktype `6513` 的稀有 Taunus P3 Karl Deutsch Coupé，避免误用普通 Sedan 尺寸组。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0097277EN_GB/144746?utm_source=chatgpt.com "Technical Data - MINI Countryman"
[2]: https://www.automobile-catalog.com/car/1959/126995/citroen_ds_19.html?utm_source=chatgpt.com "1959 Citroen DS 19 (man. 4) (model for Europe North ..."
[3]: https://www.auto-data.net/en/citroen-ami-model-1684?utm_source=chatgpt.com "Citroen AMI | Technical Specs, Fuel consumption ..."
[4]: https://www.automobile-catalog.com/car/1957/899390/ford_taunus_17m.html?utm_source=chatgpt.com "1957 Ford Taunus 17M Specs Review (44 kW / 60 PS ..."
[5]: https://www.automobile-catalog.com/car/1964/900695/ford_taunus_17m_1_5l.html?utm_source=chatgpt.com "1964 Ford Taunus 17M 1.5L Specs Review (44 kW ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6001-6100_ktype_dimension_mapping_final.tsv
- all_6001-6100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Escort I Sedan 与 Turnier：Sedan 复用累计缓存，Turnier 首次建立独立 Wagon 尺寸组。Turnier 外廓为 `4070 × 1565 × 1430 mm`。([汽车目录][1])
* 已闭合 Taunus G93A、G13、G13AL。G13AL 属于降低车顶的后期外廓；G13 Wagon 根据已确认的高度变化拆分早期和后期尺寸组。([taunus-fan-club.com][2])
* 已确认 Ktype `6513` 对应 P3 两门 Coupé 分支，但现有资料只确认车型存在，尚未找到直接支持该 Coupé 完整三维及不含后视镜宽度的可追溯规格来源，因此保持 PENDING，不套用 Sedan 尺寸。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* PENDING 输入 Ktype：1
* READY 映射行：120
* PENDING 映射行：1
* 已确认并引用尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6425	6425	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6426	6426	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6427	6427	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6428	6428	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6429	6429	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6430	6430	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6431	6431	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6432	6432	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6433	6433	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6434	6434	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6435	6435	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6436	6436	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6437	6437	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6445	6445	Sedan	Taunus G93A	G93A	2	EU-FORD-TAUNUS-G93A-SEDAN-2D-01	HIGH		READY
6446_g13	6446	Sedan	Taunus G13	G13	2	EU-FORD-TAUNUS-G13-SEDAN-2D-01	HIGH	Ktype跨越G13与G13AL两种外廓。	READY
6446_g13al	6446	Sedan	Taunus G13AL	G13AL	2	EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	HIGH	Ktype跨越G13与G13AL两种外廓。	READY
6447_g13_early	6447	Wagon	Taunus G13	G13	3	EU-FORD-TAUNUS-G13-WAGON-3D-EARLY-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6447_g13_late	6447	Wagon	Taunus G13	G13	3	EU-FORD-TAUNUS-G13-WAGON-3D-LATE-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6447_g13al	6447	Wagon	Taunus G13AL	G13AL	3	EU-FORD-TAUNUS-G13AL-WAGON-3D-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6448	6448	Sedan	Taunus G13AL	G13AL	2	EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	HIGH		READY
6466	6466	Sedan	Taunus G4B	G4B	2	EU-FORD-TAUNUS-G13-SEDAN-2D-01	HIGH	G4B与G13共用车身外廓。	READY
6513	6513	Coupe	Taunus P3	P3	2		LOW	Karl Deutsch两门Coupé物理分支；不可直接复用Sedan组。	PENDING: 缺少P3 Karl Deutsch Coupé直接三维来源
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	4070	1565	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/908690/ford_escort_turnier_1100.html
EU-FORD-TAUNUS-G93A-SEDAN-2D-01	4080	1485	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1951/898745/ford_taunus_de_luxe.html
EU-FORD-TAUNUS-G13-SEDAN-2D-01	4060	1580	1550	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/898790/ford_taunus_12m.html
EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	4060	1570	1520	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/899210/ford_taunus_12m_1_2l.html
EU-FORD-TAUNUS-G13-WAGON-3D-EARLY-01	4060	1580	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/898850/ford_taunus_12m_kombi.html
EU-FORD-TAUNUS-G13-WAGON-3D-LATE-01	4060	1580	1595	Automobile-Catalog	https://www.automobile-catalog.com/car/1958/898925/ford_taunus_12m_kombi_4-speed.html
EU-FORD-TAUNUS-G13AL-WAGON-3D-01	4060	1570	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899165/ford_taunus_12m_kombi_1_2l_4-speed.html
```

## 下一步优先处理

1. 仅处理 Ktype `6513`：查找 Ford/Karl Deutsch 历史规格、车身厂资料、type approval 或直接列出 Coupé 三维与不含后视镜宽度的可信数据库页面；闭合后立即执行一次机械收尾并输出完整两表及指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/ford_germany/escort_germany_1gen/escort_germany_1gen_turnier/1969.html?utm_source=chatgpt.com "1969 Ford (Germany) Escort Turnier full range specs"
[2]: https://www.taunus-fan-club.com/page-611030-1.html "Ford Taunus G13 / G4B"
[3]: https://en.wikipedia.org/wiki/Ford_Taunus_P3?utm_source=chatgpt.com "Ford Taunus P3"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6001-6100_ktype_dimension_mapping_final.tsv
- all_6001-6100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Ktype `6513` 已闭合。车型目录将其识别为 Taunus 17M Coupé (P3) 1.7 S、55 kW/75 PS；同代对应 17M TS 两门车身规格为 `4452 × 1670 × 1450 mm`，宽度不含后视镜。本映射采用 `MEDIUM` 置信度，并建立独立尺寸组。([AUTODOC][1])
* 已完成机械检查：映射表严格 10 列、尺寸组表严格 6 列；`id` 和 `DIMENSION_GROUP_ID` 唯一；所有映射引用闭合；尺寸及来源字段完整。
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* 最终映射行：121
* 最终尺寸组：43
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6416	6416	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6417	6417	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6418	6418	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6419	6419	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6420	6420	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6421	6421	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6422	6422	Coupe	Capri I		3	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
6423	6423	Hatchback	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
6424	6424	Hatchback	BX I Phase II 16V	XB	5	EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	HIGH	16V宽体及低车高外廓。	READY
6425	6425	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6426	6426	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6427	6427	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6428	6428	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6429	6429	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6430	6430	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6431	6431	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6432	6432	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6433	6433	Sedan	Escort I			EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH		READY
6434	6434	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6435	6435	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6436	6436	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6437	6437	Wagon	Escort I		3	EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	HIGH		READY
6438	6438	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-01	HIGH	E-CELL未改变W169五门车身外廓。	READY
6440	6440	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	HIGH		READY
6441	6441	Coupe	TT 8J facelift	8J3	3	EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	HIGH		READY
6442	6442	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	HIGH		READY
6443	6443	SUV	MINI Countryman R60	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-S-BODY-01	HIGH	Cooper SD ALL4使用S外观车身。	READY
6444_phasei	6444	Hatchback	BX I Phase I	XB	5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越BX Phase I与Phase II外廓。	READY
6444_phaseii	6444	Hatchback	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越BX Phase I与Phase II外廓。	READY
6445	6445	Sedan	Taunus G93A	G93A	2	EU-FORD-TAUNUS-G93A-SEDAN-2D-01	HIGH		READY
6446_g13	6446	Sedan	Taunus G13	G13	2	EU-FORD-TAUNUS-G13-SEDAN-2D-01	HIGH	Ktype跨越G13与G13AL两种外廓。	READY
6446_g13al	6446	Sedan	Taunus G13AL	G13AL	2	EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	HIGH	Ktype跨越G13与G13AL两种外廓。	READY
6447_g13_early	6447	Wagon	Taunus G13	G13	3	EU-FORD-TAUNUS-G13-WAGON-3D-EARLY-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6447_g13_late	6447	Wagon	Taunus G13	G13	3	EU-FORD-TAUNUS-G13-WAGON-3D-LATE-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6447_g13al	6447	Wagon	Taunus G13AL	G13AL	3	EU-FORD-TAUNUS-G13AL-WAGON-3D-01	HIGH	Ktype跨越G13早期、G13后期与G13AL三种外廓。	READY
6448	6448	Sedan	Taunus G13AL	G13AL	2	EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	HIGH		READY
6449	6449	Hatchback	MINI R56 facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
6450	6450	Wagon	BX I Phase II Break	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH		READY
6451	6451	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	HIGH		READY
6452	6452	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	HIGH		READY
6453	6453	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-TS-01	HIGH	TS长车身外廓。	READY
6454	6454	Sedan	Taunus P4	P4		EU-FORD-TAUNUS-P4-SEDAN-TS-01	HIGH	TS长车身外廓。	READY
6455	6455	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6456	6456	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6457	6457	Coupe	Taunus P4	P4	2	EU-FORD-TAUNUS-P4-COUPE-01	HIGH		READY
6458	6458	Wagon	Taunus P4	P4	3	EU-FORD-TAUNUS-P4-WAGON-3D-01	HIGH		READY
6459	6459	Wagon	Taunus P4	P4	3	EU-FORD-TAUNUS-P4-WAGON-3D-01	HIGH		READY
6460	6460	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6461	6461	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6462	6462	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6463	6463	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6464	6464	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6465	6465	Wagon	Taunus P6	P6	3	EU-FORD-TAUNUS-P6-WAGON-3D-01	HIGH		READY
6466	6466	Sedan	Taunus G4B	G4B	2	EU-FORD-TAUNUS-G13-SEDAN-2D-01	HIGH	G4B与G13共用车身外廓。	READY
6467	6467	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6468	6468	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6469	6469	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6470	6470	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6471	6471	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6472	6472	Coupe	Taunus P6	P6	2	EU-FORD-TAUNUS-P6-COUPE-2D-01	HIGH		READY
6473	6473	Wagon	Taunus P6	P6	3	EU-FORD-TAUNUS-P6-WAGON-3D-01	HIGH		READY
6474	6474	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6475	6475	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6476	6476	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6477	6477	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6478	6478	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6479	6479	Sedan	Taunus P6	P6		EU-FORD-TAUNUS-P6-SEDAN-01	HIGH		READY
6480_series1	6480	Sedan	DS Series 1		4	EU-CITROEN-DS-SERIES-1-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6480_series2	6480	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6481_series2	6481	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6481_series3	6481	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6482_series2	6482	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6482_series3	6482	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6483_series2	6483	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6483_series3	6483	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6484	6484	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6485_series2	6485	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6485_series3	6485	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6486	6486	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6487	6487	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	ID与DS共用Series 3标准车身外廓。	READY
6488_series2	6488	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6488_series3	6488	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6489	6489	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
6490_series2	6490	Wagon	DS Series 2		5	EU-CITROEN-DS-SERIES-2-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6490_series3	6490	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6491	6491	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6493	6493	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6494_series2	6494	Wagon	DS Series 2		5	EU-CITROEN-DS-SERIES-2-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6494_series3	6494	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	Ktype跨越DS Series 2与Series 3 Break外廓。	READY
6495	6495	Wagon	DS Series 3		5	EU-CITROEN-DS-SERIES-3-WAGON-01	HIGH	ID Break与DS Break共用Series 3外廓。	READY
6496	6496	Coupe	TT 8J facelift	8J3	3	EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	HIGH	Quattro未改变标准TT Coupé外廓。	READY
6497_series2	6497	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6497_series3	6497	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH	Ktype跨越DS Series 2与Series 3外廓。	READY
6498_series1	6498	Sedan	DS Series 1		4	EU-CITROEN-DS-SERIES-1-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6498_series2	6498	Sedan	DS Series 2		4	EU-CITROEN-DS-SERIES-2-SEDAN-01	HIGH	Ktype跨越DS Series 1与Series 2外廓。	READY
6500	6500	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
6501	6501	Sedan	DS Series 3		4	EU-CITROEN-DS-SERIES-3-SEDAN-01	HIGH		READY
6502	6502	Sedan	Ami 6		4	EU-CITROEN-AMI-6-SEDAN-4D-01	HIGH		READY
6503	6503	Sedan	Ami 8		4	EU-CITROEN-AMI-8-SEDAN-4D-01	HIGH		READY
6504	6504	Sedan	Ami 6		4	EU-CITROEN-AMI-6-SEDAN-4D-01	HIGH		READY
6505	6505	Sedan	Ami Super		4	EU-CITROEN-AMI-8-SEDAN-4D-01	HIGH	Ami Super采用Ami 8四门车身外廓。	READY
6506	6506	Wagon	Ami 6		5	EU-CITROEN-AMI-6-WAGON-5D-01	HIGH		READY
6507	6507	Wagon	Ami Super		5	EU-CITROEN-AMI-8-WAGON-5D-01	HIGH	Ami Super Break采用Ami 8 Break车身外廓。	READY
6508	6508	Wagon	Ami 8		5	EU-CITROEN-AMI-8-WAGON-5D-01	HIGH		READY
6509_prefl	6509	Sedan	Taunus P2	P2		EU-FORD-TAUNUS-P2-SEDAN-PREFL-01	HIGH	Ktype跨越P2车顶改型前后两种外廓。	READY
6509_facelift	6509	Sedan	Taunus P2	P2		EU-FORD-TAUNUS-P2-SEDAN-FACELIFT-01	HIGH	Ktype跨越P2车顶改型前后两种外廓。	READY
6510	6510	Wagon	Taunus P2	P2	3	EU-FORD-TAUNUS-P2-WAGON-3D-01	HIGH		READY
6511	6511	Sedan	Taunus P3	P3		EU-FORD-TAUNUS-P3-SEDAN-01	HIGH		READY
6512	6512	Sedan	Taunus P3	P3		EU-FORD-TAUNUS-P3-SEDAN-01	HIGH		READY
6513	6513	Coupe	Taunus P3	P3	2	EU-FORD-TAUNUS-P3-COUPE-2D-01	MEDIUM	TecDoc将该75PS两门分支列为Coupé；外廓采用同代17M TS两门车身规格。	READY
6514	6514	Wagon	Taunus P3	P3	3	EU-FORD-TAUNUS-P3-WAGON-3D-01	HIGH		READY
6515	6515	Wagon	Taunus P3	P3	3	EU-FORD-TAUNUS-P3-WAGON-3D-01	HIGH		READY
6516_p5	6516	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6516_p7a	6516	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6516_p7b	6516	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p5	6517	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p7a	6517	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6517_p7b	6517	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p5	6518	Sedan	Taunus P5	P5		EU-FORD-TAUNUS-P5-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p7a	6518	Sedan	Ford P7A	P7A		EU-FORD-TAUNUS-P7A-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
6518_p7b	6518	Sedan	Ford P7B	P7B		EU-FORD-TAUNUS-P7B-17M-SEDAN-01	HIGH	Ktype跨越P5、P7A与P7B三种外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6001-6100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330	Ford Capri Club Switzerland technical data	https://www.ford-capri.ch/technics/technical-data-I/1600gt-69-72-e.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/539330/citroen_bx_14_e_low_compr.html
EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	4237	1690	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/54755/citroen_bx_19_gti_16v.html
EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	3977	1570	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/908810/ford_escort_1100_s.html
EU-FORD-ESCORT-I-TURNIER-WAGON-3D-01	4070	1565	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/908690/ford_escort_turnier_1100.html
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-01	3883	1764	1593	Mercedes-Benz A-Class official brochure	https://ragtop.org/mbbrochures/2012/ireland/20111011A-Class_WC169_0611_021.pdf
EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	4468	1831	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1215515/citroen_c4_picasso_hdi_110_fap_exclusive_esg6.html
EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	4187	1842	1353	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1337060/audi_tt_coupe_2_0_tfsi_quattro_s-tronic.html
EU-MINI-COUNTRYMAN-R60-SUV-5D-S-BODY-01	4110	1789	1561	BMW Group MINI Countryman official technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0097277EN_GB/144746
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/2030045/citroen_bx_digit.html
EU-FORD-TAUNUS-G93A-SEDAN-2D-01	4080	1485	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1951/898745/ford_taunus_de_luxe.html
EU-FORD-TAUNUS-G13-SEDAN-2D-01	4060	1580	1550	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/898790/ford_taunus_12m.html
EU-FORD-TAUNUS-G13AL-SEDAN-2D-01	4060	1570	1520	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/899210/ford_taunus_12m_1_2l.html
EU-FORD-TAUNUS-G13-WAGON-3D-EARLY-01	4060	1580	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/898850/ford_taunus_12m_kombi.html
EU-FORD-TAUNUS-G13-WAGON-3D-LATE-01	4060	1580	1595	Automobile-Catalog	https://www.automobile-catalog.com/car/1958/898925/ford_taunus_12m_kombi_4-speed.html
EU-FORD-TAUNUS-G13AL-WAGON-3D-01	4060	1570	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899165/ford_taunus_12m_kombi_1_2l_4-speed.html
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	BMW Group MINI official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0076947EN/114936
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/539060/citroen_bx_break_19_trs.html
EU-FORD-TAUNUS-P4-SEDAN-STANDARD-01	4248	1594	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/899945/ford_taunus_12m_1_2l.html
EU-FORD-TAUNUS-P4-SEDAN-TS-01	4322	1594	1458	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/900020/ford_taunus_12m_ts.html
EU-FORD-TAUNUS-P4-COUPE-01	4322	1594	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/1965/900050/ford_taunus_12m_ts_coupe.html
EU-FORD-TAUNUS-P4-WAGON-3D-01	4248	1594	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/1963/899990/ford_taunus_12m_kombi_1_5l.html
EU-FORD-TAUNUS-P6-SEDAN-01	4389	1603	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/900080/ford_15m_ts_1700_s.html
EU-FORD-TAUNUS-P6-COUPE-2D-01	4389	1603	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/900530/ford_12m_coupe_1700_s.html
EU-FORD-TAUNUS-P6-WAGON-3D-01	4318	1603	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/900455/ford_15m_turnier_1700_s.html
EU-CITROEN-DS-SERIES-1-SEDAN-01	4800	1790	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/126995/citroen_ds_19.html
EU-CITROEN-DS-SERIES-2-SEDAN-01	4838	1790	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/55070/citroen_ds_19.html
EU-CITROEN-DS-SERIES-3-SEDAN-01	4874	1803	1470	ADAC Fahrzeugkatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/citroen/ds/1generation-facelift/350663/
EU-CITROEN-DS-SERIES-2-WAGON-01	4990	1790	1530	Automobile-Catalog	https://www.automobile-catalog.com/car/1966/127670/citroen_break_19.html
EU-CITROEN-DS-SERIES-3-WAGON-01	5026	1803	1530	Automobile-Catalog	https://www.automobile-catalog.com/car/1972/127745/citroen_ds_20_break.html
EU-CITROEN-AMI-6-SEDAN-4D-01	3940	1520	1490	Auto-Data	https://www.auto-data.net/en/citroen-ami-6-generation-3308
EU-CITROEN-AMI-8-SEDAN-4D-01	3990	1520	1485	Auto-Data	https://www.auto-data.net/en/citroen-ami-8-generation-5264
EU-CITROEN-AMI-6-WAGON-5D-01	3960	1520	1490	Auto-Data	https://www.auto-data.net/en/citroen-ami-model-1684
EU-CITROEN-AMI-8-WAGON-5D-01	3990	1520	1520	Auto-Data	https://www.auto-data.net/en/citroen-ami-model-1684
EU-FORD-TAUNUS-P2-SEDAN-PREFL-01	4375	1670	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1957/899390/ford_taunus_17m.html
EU-FORD-TAUNUS-P2-SEDAN-FACELIFT-01	4375	1670	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/899510/ford_taunus_17m.html
EU-FORD-TAUNUS-P2-WAGON-3D-01	4375	1670	1510	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/899615/ford_taunus_17m_kombi_de_luxe_4-speed.html
EU-FORD-TAUNUS-P3-SEDAN-01	4452	1670	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899630/ford_taunus_17m_1_5l.html
EU-FORD-TAUNUS-P3-COUPE-2D-01	4452	1670	1450	AUTODOC vehicle catalogue; Automobile-Catalog	https://www.autodoc.parts/spares/ford/taunus/taunus-17m-coupe-p3/6513-1-7-s;https://www.automobile-catalog.com/car/1964/899780/ford_taunus_17m_ts.html
EU-FORD-TAUNUS-P3-WAGON-3D-01	4452	1670	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/1961/899855/ford_taunus_17m_turnier_325_1_7l.html
EU-FORD-TAUNUS-P5-SEDAN-01	4585	1715	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/1964/900695/ford_taunus_17m_1_5l.html
EU-FORD-TAUNUS-P7A-17M-SEDAN-01	4663	1756	1494	Automobile-Catalog	https://www.automobile-catalog.com/car/1967/901205/ford_17m_1700_s.html
EU-FORD-TAUNUS-P7B-17M-SEDAN-01	4721	1756	1478	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/901820/ford_17m_1500_4-speed.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6001-6100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.parts/spares/ford/taunus/taunus-17m-coupe-p3/6513-1-7-s "Parts FORD Taunus 17M Coupe (P3) 1.7 S 75 hp Petrol 1961 - 1965 | TAUNUS P3 parts catalogue AUTODOC"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6001-6100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6001-6100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7791 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2398 行）

