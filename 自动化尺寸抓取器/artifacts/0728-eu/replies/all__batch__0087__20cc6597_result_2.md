# 任务：all 第 8601-8700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0087__20cc6597


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8601-8700 行

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
all 第 8601-8700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-1.8TD-01	4040	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	4015	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-FACELIFT-01	4015	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-PREFL-01	4015	1612	1325
EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340
EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	4015	1612	1303
EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345
EU-ALFA-ROMEO-33-905-WAGON-FWD-01	4142	1612	1345
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350
EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350
EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	4075	1614	1375
EU-ALFA-ROMEO-33-907-WAGON-4X4-01	4200	1614	1375
EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	3975	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	3995	1590	1370
EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	3995	1616	1370
EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	3995	1616	1370
EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	3935	1590	1370
EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	3890	1590	1370
EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	3926	1590	1370
EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305
EU-CADILLAC-STS-I-SEDAN-4D-01	4986	1844	1463
EU-CHRYSLER-300C-II-LD-SEDAN-4D-01	5066	1902	1488
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505
EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	4520	1797	1499
EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	4510	1797	1497
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510
EU-OPEL-ASTRA-G-HATCHBACK-3D-01	4110	1709	1425
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425
EU-OPEL-INSIGNIA-A-G09-HATCHBACK-5D-PREFL-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-G09-WAGON-5D-PREFL-01	4908	1858	1520
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490
EU-OPEL-ZAFIRA-B-A05-VAN-5D-01	4467	1801	1645
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492
EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	4635	1762	1434
EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	4635	1762	1466
EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	4654	1782	1507
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1440
EU-SAAB-9-3-I-YS3D-HATCHBACK-5D-01	4629	1711	1428
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675
EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	4340	1850	1850
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425
EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	4370	1660	1400
EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	4410	1660	1450
EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	4410	1660	1490
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	4100	1690	1380
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	4290	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	4270	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	4295	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	4340	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	4320	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	4320	1690	1445
EU-VOLVO-780-COUPE-2D-01	4794	1750	1400
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VI-R-HATCHBACK-3D-01	4212	1786	1469
EU-VW-GOLF-VI-R-HATCHBACK-5D-01	4212	1786	1461
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709
EU-VW-TOURAN-I-GP2-MPV-01	4397	1794	1634

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Chrysler	300c	2.7	Stufenheck	Heckantrieb	Benzin	130	177	Jan 2007	Nov 2012	2024-03-01	9593
Chrysler	300c	2.7	Kombi	Heckantrieb	Benzin	130	177	Jan 2007	Dec 2010	2024-03-01	9594
Chrysler	Sebring	2.4 VVT	Stufenheck	Frontantrieb	Benzin	125	170	Jul 2007	Dec 2010	2024-03-01	9595
Chrysler	Sebring	2.4 VVT	Cabriolet	Frontantrieb	Benzin	125	170	Jul 2007	Dec 2010	2024-03-01	9596
Mercedes-benz	S-Klasse	S 320	Stufenheck	Heckantrieb	Benzin	165	224	Oct 1998	Aug 2005	2024-03-01	9599
Mercedes-benz	S-Klasse	S 430, S 430 L	Stufenheck	Heckantrieb	Benzin	205	279	Oct 1998	Aug 2005	2025-02-03	9600
Mercedes-benz	S-Klasse	S 500, S 500 L	Stufenheck	Heckantrieb	Benzin	225	306	Oct 1998	Aug 2005	2025-02-03	9601
VW	Golf iv	1.8 4motion	Schrägheck	Allrad	Benzin	92	125	May 1998	Jun 2005	2024-03-01	9602
Fiat	Freemont	3.6 4X4	Großraumlimousine	Allrad	Benzin	206	280	Aug 2011	Dec 2015	2024-03-01	9608
Fiat	Freemont	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	103	140	Aug 2011	Dec 2015	2024-03-01	9609
Fiat	Freemont	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	125	170	Aug 2011	Dec 2015	2024-03-01	9610
Fiat	Freemont	2.0 JTD 4X4	Großraumlimousine	Allrad	Diesel	125	170	Aug 2011	Dec 2015	2024-03-01	9611
Opel	Insignia a	2.0 Turbo E85	Stufenheck	Frontantrieb	Benzin/Ethanol	162	220	Jul 2008	Mar 2017	2024-03-01	9612
VW	Touareg	4.2 V8 FSI	SUV	Allrad	Benzin	265	360	Jan 2011	Mar 2018	2024-03-01	9615
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	81	110	Nov 2010	May 2015	2024-03-01	9620
VW	Golf vi	1.2 TSI	Schrägheck	Frontantrieb	Benzin	63	86	May 2010	Nov 2012	2024-03-01	9621
VW	Golf vi	2.0 R 4motion	Schrägheck	Allrad	Benzin	195	265	Nov 2009	May 2011	2024-03-01	9623
VW	Jetta iv	1.4 TSI	Stufenheck	Frontantrieb	Benzin	118	160	Apr 2011	Dec 2017	2024-03-01	9629
VW	Jetta iv	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	147	200	Dec 2010	Jul 2014	2024-03-01	9630
Ford	Focus i	1.4 16V	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1998	Nov 2004	2024-03-01	9639
Ford	Focus i	1.6 16V	Schrägheck	Frontantrieb	Benzin	74	100	Oct 1998	Nov 2004	2024-03-01	9640
Ford	Focus i	1.8 16V	Schrägheck	Frontantrieb	Benzin	85	115	Oct 1998	Nov 2004	2024-03-01	9641
Ford	Focus i	1.4 16V	Stufenheck	Frontantrieb	Benzin	55	75	Feb 1999	Nov 2004	2024-03-01	9642
Ford	Focus i	1.6 16V	Stufenheck	Frontantrieb	Benzin	74	100	Feb 1999	Nov 2004	2024-03-01	9643
Ford	Focus i	1.8 16V	Stufenheck	Frontantrieb	Benzin	85	115	Feb 1999	Nov 2004	2024-03-01	9644
Ford	Focus i turnier	1.4 16V	Kombi	Frontantrieb	Benzin	55	75	Feb 1999	Nov 2004	2024-03-01	9645
Ford	Focus i turnier	1.6 16V	Kombi	Frontantrieb	Benzin	74	100	Feb 1999	Nov 2004	2024-03-01	9646
Ford	Focus i turnier	1.8 16V	Kombi	Frontantrieb	Benzin	85	115	Feb 1999	Nov 2004	2024-03-01	9647
Saab	9-5	2.0 T	Kombi	Frontantrieb	Benzin	110	150	Oct 1998	Dec 2009	2024-03-01	9648
Saab	9-5	2.3 T	Kombi	Frontantrieb	Benzin	125	170	Oct 1998	Dec 2009	2024-03-01	9649
Saab	9-5	3.0 V6T	Kombi	Frontantrieb	Benzin	147	200	Oct 1998	Aug 2005	2024-03-01	9650
Ford	Fiesta iii	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1989	Dec 1992	2024-03-01	9659
Saab	9-3	1.9 Ttid	Kombi	Frontantrieb	Diesel	96	130	Dec 2007	Feb 2015	2024-03-01	9683
Saab	9-3	1.9 Ttid	Kombi	Frontantrieb	Diesel	118	160	Dec 2007	Feb 2015	2024-03-01	9684
Saab	9-3	1.9 Ttid	Stufenheck	Frontantrieb	Diesel	96	130	Dec 2007	Feb 2015	2024-03-01	9685
Saab	9-3	1.9 Ttid	Cabriolet	Frontantrieb	Diesel	96	130	Dec 2007	Feb 2015	2024-03-01	9686
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	220	299	Sep 2003	Dec 2006	2024-03-01	9692
Opel	Astra g caravan	2.2 DTI	Kombi	Frontantrieb	Diesel	86	117	Sep 2002	Jul 2004	2024-03-01	9693
Opel	Astra g cc	2.2 DTI	Schrägheck	Frontantrieb	Diesel	86	117	Sep 2002	Jan 2005	2024-03-01	9694
Opel	Astra g	1.6 16V	Coupe	Frontantrieb	Benzin	74	101	Mar 2000	May 2005	2024-03-01	9695
Opel	Astra g	2.2 DTI	Stufenheck	Frontantrieb	Diesel	86	117	Sep 2002	Jan 2005	2024-03-01	9696
Opel	Astra j caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	74	101	Oct 2010	Oct 2015	2024-03-01	9697
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	74	101	Dec 2010	Dec 2015	2026-03-01	9698
Lotus	Elite	2	Coupe	Heckantrieb	Benzin	119	162	May 1974	May 1980	2024-03-01	9699
Lotus	Eclat	2	Coupe	Heckantrieb	Benzin	119	162	Oct 1975	May 1980	2024-03-01	9700
Lotus	Esprit s2	2	Coupe	Heckantrieb	Benzin	119	162	Oct 1975	May 1980	2024-03-01	9701
Lotus	Esprit s2	2.2 Turbo	Coupe	Heckantrieb	Benzin	157	214	Feb 1980	Aug 1988	2024-03-01	9702
Lotus	Elite	2.2	Coupe	Heckantrieb	Benzin	119	162	May 1980	Dec 1982	2024-03-01	9703
Lotus	Eclat	2.2	Coupe	Heckantrieb	Benzin	119	162	May 1980	Aug 1986	2024-03-01	9704
Lotus	Esprit s3	2.2	Coupe	Heckantrieb	Benzin	119	162	May 1980	Aug 1986	2024-03-01	9705
Lotus	Excel	2.2	Coupe	Heckantrieb	Benzin	119	162	Oct 1983	Aug 1986	2024-03-01	9706
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	92	125	Dec 2010	Dec 2015	2026-03-01	9707
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	107	146	Dec 2010	Dec 2021	2026-03-01	9708
Opel	Vectra b	2.2 DTI 16V	Stufenheck	Frontantrieb	Diesel	88	120	Sep 2000	Apr 2002	2024-03-01	9709
Opel	Vectra b caravan	2.2 DTI 16V	Kombi	Frontantrieb	Diesel	88	120	Sep 2000	Apr 2002	2024-03-01	9710
Opel	Vectra b cc	2.2 DTI 16V	Schrägheck	Frontantrieb	Diesel	88	120	Sep 2000	Apr 2002	2024-03-01	9711
Opel	Zafira	2.2 DTI 16V	Großraumlimousine	Frontantrieb	Diesel	86	117	Jan 2002	Jun 2005	2024-03-01	9712
Cadillac	Sts	4.6 AWD	Stufenheck	Allrad	Benzin	239	325	Sep 2004	Dec 2005	2024-03-01	9713
Volvo	S80 ii	D3 / D4	Stufenheck	Frontantrieb	Diesel	120	163	Jan 2010	Dec 2016	2024-03-01	9714
Volvo	Xc70 ii	3.2 AWD	Kombi	Allrad	Benzin	179	243	May 2010	Dec 2014	2024-03-01	9715
Lancia	Delta iii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	77	105	Apr 2011	Aug 2014	2024-03-01	9716
Volvo	Xc70 ii	T6 AWD	Kombi	Allrad	Benzin	224	304	Jan 2010	Apr 2015	2024-03-01	9717
Volvo	780	2.4 D	Coupe	Heckantrieb	Diesel	90	122	Apr 1986	Jul 1990	2024-03-01	9718
Lotus	Europa	1.5	Coupe	Heckantrieb	Benzin	57	78	Oct 1966	Oct 1970	2024-03-01	9719
Lotus	Europa	1.6	Coupe	Heckantrieb	Benzin	78	106	May 1970	Apr 1976	2024-03-01	9720
Lotus	Elise	1.8	Cabriolet	Heckantrieb	Benzin	88	120	Aug 1995	Nov 2000	2024-03-01	9721
Lotus	Elise	111 S	Cabriolet	Heckantrieb	Benzin	107	146	Mar 1999	Nov 2000	2024-03-01	9722
Lotus	Esprit s4	3.5 V8 32V Turbo	Coupe	Heckantrieb	Benzin	260	354	Feb 1996	Jun 2003	2024-03-01	9723
Lotus	Esprit s4	2.2 16V Turbo SE	Coupe	Heckantrieb	Benzin	197	268	May 1989	Sep 1996	2024-03-01	9724
Lotus	Elan	1.6 I 16V	Cabriolet	Frontantrieb	Benzin	97	132	Sep 1989	Nov 1995	2024-03-01	9725
Lotus	Elan	1.6 I 16V Turbo	Cabriolet	Frontantrieb	Benzin	123	167	Sep 1989	Nov 1995	2024-03-01	9727
Alfa Romeo	33	1.5 I.e.	Schrägheck	Frontantrieb	Benzin	74	101	Jul 1990	Aug 1991	2024-03-01	9728
Alfa Romeo	33	1.8 TD	Schrägheck	Frontantrieb	Diesel	62	84	Jul 1990	Sep 1994	2024-03-01	9730
Lotus	Excel	2.2 Se/sa	Coupe	Heckantrieb	Benzin	135	184	Oct 1984	Aug 1991	2024-03-01	9731
Toyota	Corolla	1.8 Vvtl-i TS	Schrägheck	Frontantrieb	Benzin	160	218	Oct 2005	Dec 2006	2024-03-01	9732
Volvo	V70 iii	T5	Kombi	Frontantrieb	Benzin	177	241	Jan 2010	Dec 2014	2024-03-01	9733
Volvo	S80 ii	3.2 AWD	Stufenheck	Allrad	Benzin	179	243	Jan 2010	Dec 2014	2024-05-01	9734
Volvo	S80 ii	3.2	Stufenheck	Frontantrieb	Benzin	179	243	Jan 2010	Dec 2014	2024-03-01	9735
Volvo	S60 ii	Drive / D2	Stufenheck	Frontantrieb	Diesel	84	114	Jan 2011	Dec 2015	2024-03-01	9737
Alfa Romeo	6	2	Stufenheck	Heckantrieb	Benzin	99	135	Jul 1981	Dec 1986	2024-03-01	9739
Alfa Romeo	6	2.5 TD	Stufenheck	Heckantrieb	Diesel	77	105	Jul 1981	May 1986	2024-03-01	9740
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	147	200	Jan 2011	Dec 2014	2024-03-01	9743
VW	Jetta iv	2.5	Stufenheck	Frontantrieb	Benzin	125	170	Apr 2010	Dec 2017	2024-03-01	9749
VW	Jetta iv	2.0 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Oct 2010	Dec 2017	2024-03-01	9752
VW	Jetta iv	2	Stufenheck	Frontantrieb	Benzin	85	115	Jun 2010	Dec 2017	2024-03-01	9753
Alfa Romeo	Alfasud	1.7	Coupe	Frontantrieb	Benzin	87	118	Mar 1987	Dec 1989	2024-03-01	9761
Alfa Romeo	Rz	3.0 V6 Zagato	Cabriolet	Heckantrieb	Benzin	152	207	Jan 1992	Dec 1994	2024-03-01	9762
Alfa Romeo	33	1.7	Kombi	Frontantrieb	Benzin	87	118	Mar 1988	Dec 1989	2024-03-01	9764
Subaru	Forester	2.0 AWD	SUV	Allrad	Benzin	110	150	Jan 2010	-	2024-03-01	9777
Subaru	Forester	2.5 AWD	SUV	Allrad	Benzin	126	171	Jan 2009	Sep 2013	2024-03-01	9778
Alfa Romeo	33	1.5 I.E	Kombi	Frontantrieb	Benzin	71	97	Jan 1990	Sep 1994	2024-03-01	9780
Subaru	Leone iii station wagon	1600 4WD	Kombi	Allrad	Benzin	55	75	Jan 1990	Dec 1994	2024-03-01	9784
Subaru	Leone iii station wagon	1600 4WD	Kombi	Allrad	Benzin	54	73	Jan 1987	Jan 1989	2024-03-01	9785
Subaru	Leone iii station wagon	1600	Kombi	Frontantrieb	Benzin	55	75	Jan 1990	Dec 1994	2024-03-01	9786
Subaru	Leone iii	1600 4WD	Stufenheck	Allrad	Benzin	55	74	Jan 1990	Dec 1994	2024-03-01	9787
Subaru	Leone iii	1600 4WD	Stufenheck	Allrad	Benzin	54	73	Jan 1990	Dec 1994	2024-03-01	9788
Subaru	Trezia	1.3	Schrägheck	Frontantrieb	Benzin	73	99	Mar 2011	-	2024-03-01	9792
Subaru	Trezia	1.4 D	Schrägheck	Frontantrieb	Diesel	66	90	Mar 2011	-	2024-03-01	9793
Ssangyong	Korando	2.3	Geländewagen geschlossen	Allrad	Benzin	110	150	Jan 2002	Jun 2006	2024-03-01	9798
Ssangyong	Korando	2.3	Geländewagen offen	Allrad	Benzin	110	150	Jan 2002	Jun 2006	2024-03-01	9799


--- Round 1 / 首次发送 ---
更新点

* 按缓存优先模式完成首轮关联，30 个 Ktype 已闭合，共形成 39 条 READY 映射。
* 本轮引用 31 个已有尺寸组，未重复抓取三维或来源。
* 已拆分门数、改款前后及 Griffin 外廓分支；未创建新尺寸组。

当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：30
* 待处理 Ktype：70
* READY 映射：39
* 本轮复用已有尺寸组：31
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9602_3dr	9602	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9602_5dr	9602	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9608	9608	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9609	9609	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9610	9610	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9611	9611	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9615_prefl	9615	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	MEDIUM	生产区间覆盖改款前后；本行为改款前分支。	READY
9615_facelift	9615	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	MEDIUM	生产区间覆盖改款前后；本行为改款后分支。	READY
9620	9620	MPV	Touran I GP2	1T3	5	EU-VW-TOURAN-I-GP2-MPV-01	HIGH		READY
9623_3dr	9623	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-R-HATCHBACK-3D-01	MEDIUM	Golf R三门物理分支。	READY
9623_5dr	9623	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-R-HATCHBACK-5D-01	MEDIUM	Golf R五门物理分支。	READY
9683_facelift	9683	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9683_griffin	9683	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9684_facelift	9684	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9684_griffin	9684	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9685_facelift	9685	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9685_griffin	9685	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9693	9693	Wagon	Astra G	T98	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9694_3dr	9694	Hatchback	Astra G	T98	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门CC车身；本行为三门分支。	READY
9694_5dr	9694	Hatchback	Astra G	T98	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门CC车身；本行为五门分支。	READY
9709	9709	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH		READY
9710	9710	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH		READY
9711	9711	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH		READY
9713	9713	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-4D-01	HIGH		READY
9716_prefl	9716	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	MEDIUM	生产区间与2011年改款交叠；本行为改款前分支。	READY
9716_facelift	9716	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	MEDIUM	生产区间与2011年改款交叠；本行为改款后分支。	READY
9718	9718	Coupe	780		2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
9728	9728	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH		READY
9730	9730	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH		READY
9733_prefl	9733	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	生产区间覆盖改款前后；本行为改款前分支。	READY
9733_facelift	9733	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖改款前后；本行为改款后分支。	READY
9761	9761	Coupe	Alfasud Sprint	902A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	HIGH		READY
9764	9764	Wagon	33 905	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
9780	9780	Wagon	33 907	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	HIGH		READY
9784	9784	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH		READY
9785	9785	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH		READY
9787	9787	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
9788	9788	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
9799	9799	Convertible	Korando II	KJ	2	EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 闭合 Chrysler 300C、Sebring 与 Mercedes-Benz S-Klasse W220 的车身、轴距及改款分支。
2. 集中建立 Ford Focus I、Saab 9-5 Wagon、Opel Astra G Coupe/Sedan 和 Zafira A 尺寸组。
3. 随后处理 Jetta IV、Volvo S80/XC70/S60/XC90、Subaru Forester/Trezia。
4. Movano B Bus 和经典 Lotus 车型最后按轴距、车顶及车身系列分别聚类。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 13 个 Ktype，共新增 17 条 READY 映射。
* 首次创建 10 个尺寸组；另有 6 条 Volvo S80 II 派生映射直接复用现有两个尺寸组。
* Chrysler 300C、Sebring Sedan、Opel Astra G/J、Volvo S60 II/XC90 I 与 Subaru Trezia 的尺寸组已按车身及改款边界闭合。([汽车目录][1])
* Volvo S60 II 改款前后长度分别为 4628 mm 与 4635 mm；Trezia 两种动力复用同一物理外廓。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：43
* 待处理 Ktype：57
* READY 映射：56
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9593	9593	Sedan	300C I	LX	4	EU-CHRYSLER-300C-I-LX-SEDAN-4D-01	HIGH	2.7动力对应第一代LX轿车外廓。	READY
9594	9594	Wagon	300C I	LX	5	EU-CHRYSLER-300C-I-LX-WAGON-5D-01	HIGH	300C Touring五门旅行车外廓。	READY
9595	9595	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
9695	9695	Coupe	Astra G		2	EU-OPEL-ASTRA-G-COUPE-2D-01	HIGH	Bertone双门Coupe外廓。	READY
9696	9696	Sedan	Astra G		4	EU-OPEL-ASTRA-G-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
9697	9697	Wagon	Astra J		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-5D-01	HIGH	Sports Tourer外廓；改款前后本组三维不变。	READY
9714_pre13	9714	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9714_facelift13	9714	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9734_pre13	9734	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9734_facelift13	9734	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9735_pre13	9735	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9735_facelift13	9735	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9737_prefl	9737	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2013年改款；本行为改款前分支。	READY
9737_facelift	9737	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2013年改款；本行为改款后分支。	READY
9743	9743	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	HIGH	2007年改款后的第一代XC90外廓。	READY
9792	9792	Hatchback	Trezia		5	EU-SUBARU-TREZIA-HATCHBACK-5D-01	HIGH		READY
9793	9793	Hatchback	Trezia		5	EU-SUBARU-TREZIA-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-300C-I-LX-SEDAN-4D-01	5015	1880	1475	Automobile-Catalog 2007 Chrysler 300C 2.7 specifications	https://www.automobile-catalog.com/car/2007/524225/chrysler_300c_2_7.html
EU-CHRYSLER-300C-I-LX-WAGON-5D-01	5015	1880	1481	Automobile-Catalog 2007 Chrysler 300C Touring 2.7 specifications	https://www.automobile-catalog.com/car/2007/524300/chrysler_300c_touring_2_7.html
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4850	1843	1497	Auto-Data Chrysler Sebring Sedan JS 2.4i 16V specifications	https://www.auto-data.net/en/chrysler-sebring-sedan-js-2.4i-16v-172hp-automatic-24868
EU-OPEL-ASTRA-G-COUPE-2D-01	4267	1709	1390	Automobile-Catalog Opel Astra G Bertone Coupe specifications	https://www.automobile-catalog.com/car/2000/2519465/opel_astra_coupe_2_2_16v.html
EU-OPEL-ASTRA-G-SEDAN-4D-01	4252	1709	1425	Automobile-Catalog 2003 Opel Astra 4d 2.2 DTI specifications	https://www.automobile-catalog.com/car/2003/2519000/opel_astra_4d_2_2_dti_16v.html
EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-5D-01	4698	1814	1535	Automobile-Catalog 2011 Opel Astra Sports Tourer 1.7 CDTI specifications	https://www.automobile-catalog.com/car/2011/2530730/opel_astra_sports_tourer_1_7_cdti_110.html
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484	Auto-Data Volvo S60 model dimensions	https://www.auto-data.net/en/volvo-s60-model-917
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data Volvo S60 II facelift 1.6 D2 specifications	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-1.6-d2-115hp-18415
EU-VOLVO-XC90-I-SUV-FACELIFT-01	4807	1936	1784	Auto-Data Volvo XC90 facelift D5 AWD specifications	https://www.auto-data.net/en/volvo-xc90-facelift-2007-2.4-d5-200hp-awd-automatic-18204
EU-SUBARU-TREZIA-HATCHBACK-5D-01	3995	1695	1595	Auto-Data Subaru Trezia generation specifications	https://www.auto-data.net/en/subaru-trezia-generation-3985
```

## 下一步优先处理

1. Mercedes-Benz S-Klasse W220 的短轴、长轴及改款前后分支。
2. Ford Focus I Hatchback、Sedan、Turnier 的改款边界和批量映射。
3. Saab 9-5 Wagon 的多次外廓更新，以及 Opel Insignia A Sedan。
4. Volvo XC70 II、VW Jetta VI、Subaru Forester SH 与剩余 SsangYong Korando KJ。
5. 最后处理 Movano B Bus 的轴距/车顶组合及经典 Lotus 多车型簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/524225/chrysler_300c_2_7.html?utm_source=chatgpt.com "2007 Chrysler 300C 2.7 Specs Review (142 kW / 193 PS / ..."
[2]: https://www.auto-data.net/en/volvo-s60-model-917?utm_source=chatgpt.com "Volvo S60 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增闭合 10 个 Ktype，共新增 19 条 READY 映射。
* 首次创建 6 个尺寸组：Jetta VI 改款前/后、Saab 9-5 I Wagon 三个外廓阶段，以及 Volvo XC70 II Wagon。
* Jetta VI 改款前为 4644 × 1778 × 1482 mm，改款后长度增至 4659 mm；Saab 9-5 Sport Combi 按 2001、2005 两次外廓更新拆分。([汽车数据][1])
* XC70 II 的当前两个 Ktype 在 2013 年改款前后三维一致，统一关联同一尺寸组。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：53
* PENDING Ktype：47
* READY 映射：75
* 已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9629_prefl	9629	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9629_facelift	9629	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9630	9630	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	HIGH	生产结束时间位于2014年改款切换前。	READY
9648_prefl	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为初期分支。	READY
9648_facelift01	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2001年改款分支。	READY
9648_facelift05	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2005年改款分支。	READY
9649_prefl	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为初期分支。	READY
9649_facelift01	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2001年改款分支。	READY
9649_facelift05	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2005年改款分支。	READY
9650_prefl	9650	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖初期与2001年改款外廓；本行为初期分支。	READY
9650_facelift01	9650	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖初期与2001年改款外廓；本行为2001年改款分支。	READY
9715	9715	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	2013年改款前后三维一致。	READY
9717	9717	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	2013年改款前后三维一致。	READY
9749_prefl	9749	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9749_facelift	9749	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9752_prefl	9752	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9752_facelift	9752	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9753_prefl	9753	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9753_facelift	9753	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-JETTA-VI-162-SEDAN-PREFL-01	4644	1778	1482	Auto-Data Volkswagen Jetta VI 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-jetta-vi-1.4-tsi-122hp-44516
EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	4659	1778	1482	Volkswagen UK Jetta brochure November 2017	https://www.vwpress.co.uk/assets/documents/original/17569-Jetta_brochure_11_17.pdf
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492	Auto-Data Saab 9-5 Sport Combi 2.0 T specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-2.0-t-150hp-automatic-11856
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501	Auto-Data Saab 9-5 Sport Combi facelift 2001 specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2001-2.3-t-185hp-11859
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459	Auto-Data Saab 9-5 Sport Combi facelift 2005 specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2005-1.9-tid-150hp-automatic-42748
EU-VOLVO-XC70-II-WAGON-01	4838	1870	1604	Auto-Data Volvo XC70 II 3.2 specifications; Auto-Data Volvo XC70 II facelift 2013 specifications	https://www.auto-data.net/en/volvo-xc70-ii-3.2-243hp-geartronic-24704;https://www.auto-data.net/en/volvo-xc70-ii-facelift-2013-2.0-d4-163hp-19789
```

## 下一步优先处理

1. 闭合 Ford Focus I Hatchback、Sedan、Turnier 的改款前后外廓及门数分支。
2. 处理 Mercedes-Benz W220 的短轴、长轴和改款边界。
3. 闭合 Saab 9-3 II Convertible、Opel Insignia A Sedan、Zafira A 与 Golf VI 标准 Hatchback。
4. 处理 Chevrolet Tahoe、Subaru Forester SH、Korando KJ closed 与 Leone III FWD Wagon。
5. 最后集中处理 Movano B Bus 的轴距/车顶组合及经典 Lotus 车型簇。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-jetta-vi-1.4-tsi-122hp-44516?utm_source=chatgpt.com "Volkswagen Jetta VI 1.4 TSI (122 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volvo-xc70-ii-3.2-243hp-geartronic-24704?utm_source=chatgpt.com "Volvo XC70 II 3.2 (243 Hp) Geartronic"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增闭合 10 个 Ktype，新增 19 条 READY 映射。
* Mercedes-Benz W220/V220 按短轴、长轴及改款前后闭合为四个尺寸组：改款前长度分别为 5038/5158 mm，改款后为 5043/5163 mm，车身宽度均为 1855 mm。([汽车数据][1])
* Golf VI 官方资料确认三门、五门车身宽度分别为 1779/1786 mm；本轮仅首次创建三门组，五门继续复用已有组。Insignia A 官方资料确认 Sedan 外廓为 4830 × 1856 × 1498 mm，宽度明确不含后视镜。([大众汽车英国][2])
* Forester III 的改款前 2.5 与改款后 2.0 复用 1780 mm 标准宽度组；改款后 2.5 使用 1795 mm 宽体组。Saab 9-3 敞篷、Zafira A 和 Alfa Romeo RZ 同步闭合。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：63
* PENDING Ktype：37
* READY 映射：94
* 已确认尺寸组：58
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9599	9599	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	HIGH		READY
9600_swb_prefl	9600	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款前分支。	READY
9600_swb_facelift	9600	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款后分支。	READY
9600_lwb_prefl	9600	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款前分支。	READY
9600_lwb_facelift	9600	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款后分支。	READY
9601_swb_prefl	9601	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款前分支。	READY
9601_swb_facelift	9601	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款后分支。	READY
9601_lwb_prefl	9601	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款前分支。	READY
9601_lwb_facelift	9601	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款后分支。	READY
9612	9612	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-G09-SEDAN-4D-PREFL-01	HIGH		READY
9621_3dr	9621	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9621_5dr	9621	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9686_facelift	9686	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-FACELIFT-CONVERTIBLE-2D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9686_griffin	9686	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9712	9712	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	MEDIUM	生产区间覆盖2003年改款，物理外廓不变。	READY
9762	9762	Convertible	RZ		2	EU-ALFA-ROMEO-RZ-CONVERTIBLE-2D-01	HIGH		READY
9777	9777	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	HIGH		READY
9778_prefl	9778	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	MEDIUM	生产区间覆盖2010年改款；本行为改款前标准宽度分支。	READY
9778_facelift	9778	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-WIDE-01	MEDIUM	生产区间覆盖2010年改款；本行为改款后宽体分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	5038	1855	1444	Auto-Data Mercedes-Benz S-Class W220 S 320 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-w220-s-320-v6-224hp-5g-tronic-13057
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	5043	1855	1444	Auto-Data Mercedes-Benz S-Class W220 facelift S 430 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-w220-facelift-2002-s-430-v8-279hp-5g-tronic-13064
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	5158	1855	1444	Auto-Data Mercedes-Benz S-Class Long V220 S 320 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-long-v220-s-320-v6-224hp-5g-tronic-13060
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444	Auto-Data Mercedes-Benz S-Class Long V220 facelift S 430 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-long-v220-facelift-2002-s-430-v8-279hp-7g-tronic-44472
EU-OPEL-INSIGNIA-A-G09-SEDAN-4D-PREFL-01	4830	1856	1498	Vauxhall New Insignia official brochure October 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/insignia-a/Insignia_October_2008.pdf
EU-VW-GOLF-VI-5K-HATCHBACK-3D-01	4199	1779	1480	Volkswagen UK Golf Mk6 official brochure February 2010	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_feb_2010.pdf
EU-SAAB-9-3-II-FACELIFT-CONVERTIBLE-2D-01	4647	1762	1437	Automobile-Catalog 2008 Saab 9-3 1.9 TiD Cabriolet specifications	https://www.automobile-catalog.com/car/2008/3037655/saab_9-3_1_9_tid_150_cabriolet.html
EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	4317	1742	1684	Auto-Data Opel Zafira A T3000 specifications;Auto-Data Opel Zafira A facelift 2003 specifications	https://www.auto-data.net/en/opel-zafira-a-t3000-generation-574;https://www.auto-data.net/en/opel-zafira-a-facelift-2003-generation-5178
EU-ALFA-ROMEO-RZ-CONVERTIBLE-2D-01	4060	1730	1300	Auto-Data Alfa Romeo RZ 3.0 V6 specifications	https://www.auto-data.net/en/alfa-romeo-rz-3.0-i-v6-210hp-1359
EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	4560	1780	1700	Auto-Data Subaru Forester III 2.5 XS specifications;Auto-Data Subaru Forester III facelift 2.0 i specifications	https://www.auto-data.net/en/subaru-forester-iii-2.5-xs-171hp-16210;https://www.auto-data.net/en/subaru-forester-iii-facelift-2010-2.0-i-150hp-17915
EU-SUBARU-FORESTER-III-SH-SUV-WIDE-01	4560	1795	1700	Auto-Data Subaru Forester III facelift 2.5 specifications	https://www.auto-data.net/en/subaru-forester-iii-facelift-2010-2.5-171hp-awd-e-4at-54229
```

## 下一步优先处理

1. 解决 Ford Focus I Hatchback、Sedan、Turnier 的来源尺寸差异并批量闭合 9 个 Ktype。
2. 处理 Chevrolet Tahoe、Sebring Convertible、Korando KJ closed 与 Leone III FWD Wagon。
3. 闭合剩余 Toyota Corolla T-Sport、Fiesta III 及 Alfa Romeo 6。
4. 最后集中处理 Movano B Bus 的轴距/车顶组合和经典 Lotus 车型簇。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-s-class-w220-s-320-v6-224hp-5g-tronic-13057 "Mercedes-Benz S-class (W220) S 320 V6 (224 Hp) 5G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_feb_2010.pdf "untitled"
[3]: https://www.auto-data.net/en/subaru-forester-iii-2.5-xs-171hp-16210 "Subaru Forester III 2.5 XS (171 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 本轮新增闭合 15 个 Ktype，共新增 18 条 READY 映射。
* Ford Focus I 的三门、五门 Hatchback、Sedan 与 Turnier 四类物理车身一次建组后批量关联 9 个 Ktype。([汽车数据][1])
* Sebring Convertible 使用独立敞篷外廓；Tahoe 按 Ktype 自 2003 年 9 月开始所对应的 2004–2006 外廓闭合。([汽车目录][2])
* Corolla T Sport Compressor 按其专属保险杠、降低车身外廓独立建组；Alfa Romeo 6 两种动力复用同一 119 Sedan 组。([Ultimate Specs][3])
* Subaru Leone III 前驱旅行车与已有四驱旅行车尺寸不同，首次创建 FWD 尺寸组。([汽车目录][4])

## 2. 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：78
* PENDING Ktype：22
* READY 映射：112
* 已确认尺寸组：67
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9596	9596	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	HIGH		READY
9639_3dr	9639	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9639_5dr	9639	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9640_3dr	9640	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9640_5dr	9640	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9641_3dr	9641	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9641_5dr	9641	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9642	9642	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9643	9643	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9644	9644	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9645	9645	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9646	9646	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9647	9647	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9692	9692	SUV	Tahoe II	GMT800	5	EU-CHEVROLET-TAHOE-II-GMT800-SUV-2004-06-01	MEDIUM	生产开始月份对应2004车型年度外廓。	READY
9732	9732	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	HIGH	T Sport Compressor专属降低车身及外部套件。	READY
9739	9739	Sedan	Alfa Romeo 6	119	4	EU-ALFA-ROMEO-6-119-SEDAN-4D-01	HIGH		READY
9740	9740	Sedan	Alfa Romeo 6	119	4	EU-ALFA-ROMEO-6-119-SEDAN-4D-01	HIGH		READY
9786	9786	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-FWD-01	HIGH	前驱旅行车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	4922	1816	1485	Automobile-Catalog 2008 Chrysler Sebring Convertible LX 2.4L specifications	https://www.automobile-catalog.com/car/2008/1211525/chrysler_sebring_convertible_lx_2_4l.html
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-hatchback-i-1.4-16v-75hp-7361
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-hatchback-i-1.4-16v-75hp-7361
EU-FORD-FOCUS-I-SEDAN-4D-01	4362	1698	1430	Auto-Data Ford Focus I Sedan 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-i-sedan-1.4-16v-75hp-7353
EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	4438	1698	1447	Auto-Data Ford Focus Turnier I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-turnier-i-1.4-16v-75hp-7372
EU-CHEVROLET-TAHOE-II-GMT800-SUV-2004-06-01	5050	2002	1900	Edmunds 2004 Chevrolet Tahoe RWD specifications	https://www.edmunds.com/chevrolet/tahoe/2004/features-specs/
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	4200	1710	1460	UltimateSpecs Toyota Corolla IX 1.8 TTE Compressor specifications	https://www.ultimatespecs.com/car-specs/Toyota/1567/Toyota-Corolla-IX-18-TTE-Compressor.html
EU-ALFA-ROMEO-6-119-SEDAN-4D-01	4679	1684	1395	Auto-Data Alfa Romeo 6 119 generation specifications	https://www.auto-data.net/en/alfa-romeo-6-119-generation-398
EU-SUBARU-LEONE-III-WAGON-5D-FWD-01	4410	1660	1420	Automobile-Catalog 1994 Subaru Leone Estate Van 1.6 LC specifications	https://www.automobile-catalog.com/car/1994/3213590/subaru_leone_estate_van_1_6_lc.html
```

## 5. 下一步优先处理

1. 集中闭合 Lotus Elite、Eclat、Excel、Europa、Elise、Elan 与 Esprit 各代车身。
2. 按轴距和车顶组合处理 Opel Movano B Bus 的 3 个 Ktype。
3. 核对 Fiesta III 三门/五门边界及 Korando KJ closed 的两个既有高度组。
4. 完成剩余车型后立即进行一次机械闭合检查并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-focus-i-sedan-1.4-16v-75hp-7353 "Ford Focus I Sedan 1.4 16V (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2008/1211525/chrysler_sebring_convertible_lx_2_4l.html?utm_source=chatgpt.com "2008 Chrysler Sebring Convertible LX 2.4L Specs Review (129 kW / 175 PS / 173 hp) (since mid-year 2007 for North America U.S.)"
[3]: https://www.ultimatespecs.com/car-specs/Toyota/1567/Toyota-Corolla-IX-18-TTE-Compressor.html?utm_source=chatgpt.com "Toyota Corolla IX 1.8 TTE Compressor Specs"
[4]: https://www.automobile-catalog.com/car/1994/3213590/subaru_leone_estate_van_1_6_lc.html?utm_source=chatgpt.com "1994 Subaru Leone Estate Van 1.6 LC (man. 4)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 19 个 Ktype，新增 24 条 READY 映射；另正式落盘 3 条 Movano B PENDING 映射。
* Fiesta III 和 Korando II 直接复用既有尺寸组，未重复输出尺寸组。
* Lotus Elite、Eclat、Esprit、Excel、Europa、Elise 与 Elan 共首次创建 18 个尺寸组；其中 Esprit S3 按 1984 年前后外廓变化拆分，Europa 1.5 按 Type 46/54 拆分。([汽车目录][1])
* 剩余 3 个 PENDING 均为 Movano B FWD Bus，尚需闭合轴距与车顶组合。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：97
* PENDING Ktype：3
* READY 映射：136
* PENDING 映射：3
* 已确认尺寸组：85
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9659_3dr	9659	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9659_5dr	9659	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9698	9698	MPV	Movano B	X62			LOW	FWD Bus的轴距与车顶组合尚未闭合。	PENDING: 尚未确认轴距与车顶组合
9699	9699	Coupe	Elite Type 75	75	3	EU-LOTUS-ELITE-TYPE75-COUPE-3D-01	HIGH		READY
9700	9700	Coupe	Eclat Type 76	76	2	EU-LOTUS-ECLAT-TYPE76-COUPE-2D-01	HIGH		READY
9701	9701	Coupe	Esprit S2	79	2	EU-LOTUS-ESPRIT-S2-COUPE-2D-01	MEDIUM	Ktype车型名称确定为S2；输入起始年月早于S2正式阶段。	READY
9702	9702	Coupe	Turbo Esprit	82	2	EU-LOTUS-ESPRIT-TYPE82-TURBO-COUPE-2D-01	HIGH		READY
9703	9703	Coupe	Elite Type 83	83	3	EU-LOTUS-ELITE-TYPE83-COUPE-3D-01	HIGH		READY
9704	9704	Coupe	Eclat Type 84	84	2	EU-LOTUS-ECLAT-TYPE84-COUPE-2D-01	MEDIUM	按Eclat 2.2车身边界映射。	READY
9705_pre84	9705	Coupe	Esprit S3	85	2	EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-EARLY-01	MEDIUM	生产区间覆盖1984年外廓更新；本行为早期分支。	READY
9705_late84	9705	Coupe	Esprit S3	85	2	EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-LATE-01	MEDIUM	生产区间覆盖1984年外廓更新；本行为后期分支。	READY
9706	9706	Coupe	Excel	89	2	EU-LOTUS-EXCEL-TYPE89-COUPE-STANDARD-01	HIGH	标准早期Excel外廓。	READY
9707	9707	MPV	Movano B	X62			LOW	FWD Bus的轴距与车顶组合尚未闭合。	PENDING: 尚未确认轴距与车顶组合
9708	9708	MPV	Movano B	X62			LOW	FWD Bus的轴距与车顶组合尚未闭合。	PENDING: 尚未确认轴距与车顶组合
9719_type46	9719	Coupe	Europa S1	46	2	EU-LOTUS-EUROPA-TYPE46-COUPE-2D-01	MEDIUM	生产区间覆盖Type 46与Type 54；本行为Type 46分支。	READY
9719_type54	9719	Coupe	Europa S2	54	2	EU-LOTUS-EUROPA-TYPE54-COUPE-2D-01	MEDIUM	生产区间覆盖Type 46与Type 54；本行为Type 54分支。	READY
9720	9720	Coupe	Europa Twin Cam	74	2	EU-LOTUS-EUROPA-TYPE74-COUPE-2D-01	HIGH		READY
9721	9721	Convertible	Elise Series 1	111	2	EU-LOTUS-ELISE-S1-111-ROADSTER-STANDARD-01	HIGH	标准Series 1外廓。	READY
9722	9722	Convertible	Elise Series 1	111	2	EU-LOTUS-ELISE-S1-111S-ROADSTER-01	HIGH	111S外部长度与标准版不同。	READY
9723	9723	Coupe	Esprit S4		2	EU-LOTUS-ESPRIT-S4-V8-COUPE-01	HIGH	V8外廓。	READY
9724	9724	Coupe	Esprit X180/S4		2	EU-LOTUS-ESPRIT-X180-TURBO-SE-COUPE-01	HIGH	Turbo SE外廓。	READY
9725	9725	Convertible	Elan II	M100	2	EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	HIGH		READY
9727	9727	Convertible	Elan II	M100	2	EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	HIGH	自然吸气与Turbo版本复用相同外廓。	READY
9731	9731	Coupe	Excel	89	2	EU-LOTUS-EXCEL-TYPE89-COUPE-SE-SA-01	HIGH	SE/SA外廓。	READY
9798_h1840	9798	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	MEDIUM	同一Ktype覆盖两个已确认车身高度；本行为1840 mm高度分支。	READY
9798_h1940	9798	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	MEDIUM	同一Ktype覆盖两个已确认车身高度；本行为1940 mm高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LOTUS-ELITE-TYPE75-COUPE-3D-01	4458	1816	1207	Encycarpedia Lotus Elite Type 75 specifications	https://www.encycarpedia.com/lotus/74-elite-s2-coupe
EU-LOTUS-ECLAT-TYPE76-COUPE-2D-01	4458	1816	1207	Auto-Data Lotus Eclat generation specifications	https://www.auto-data.net/en/lotus-eclat-generation-1828
EU-LOTUS-ESPRIT-S2-COUPE-2D-01	4191	1854	1111	Automobile-Catalog 1979 Lotus Esprit S2 specifications	https://www.automobile-catalog.com/car/1979/1434335/lotus_esprit_s2.html
EU-LOTUS-ESPRIT-TYPE82-TURBO-COUPE-2D-01	4330	1860	1150	Auto-Data Lotus Esprit 2.2 Turbo specifications	https://www.auto-data.net/en/lotus-esprit-2.2-turbo-218hp-8304
EU-LOTUS-ELITE-TYPE83-COUPE-3D-01	4458	1816	1207	Automobile-Catalog 1980 Lotus Elite S 2.2 specifications	https://www.automobile-catalog.com/car/1980/44060/lotus_elite_s_2_2.html
EU-LOTUS-ECLAT-TYPE84-COUPE-2D-01	4458	1816	1207	Auto-Data Lotus Eclat 2.2 specifications	https://www.auto-data.net/en/lotus-eclat-2.2-162hp-8291
EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-EARLY-01	4191	1854	1118	Automobile-Catalog 1981 Lotus Esprit S3 specifications	https://www.automobile-catalog.com/car/1981/1434635/lotus_esprit_s3.html
EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-LATE-01	4224	1854	1111	Automobile-Catalog 1986 Lotus Esprit S3 specifications	https://www.automobile-catalog.com/car/1986/23825/lotus_esprit_s3.html
EU-LOTUS-EXCEL-TYPE89-COUPE-STANDARD-01	4395	1815	1205	Auto-Data Lotus Excel 2.2 specifications	https://www.auto-data.net/en/lotus-excel-2.2-162hp-8317
EU-LOTUS-EUROPA-TYPE46-COUPE-2D-01	3960	1630	1070	Automobile-Catalog 1967 Lotus Europa Type 46 specifications	https://www.automobile-catalog.com/car/1967/1433000/lotus_europa_type_46.html
EU-LOTUS-EUROPA-TYPE54-COUPE-2D-01	3993	1638	1080	Automobile-Catalog 1969 Lotus Europa S2 Type 54 specifications	https://www.automobile-catalog.com/car/1969/1433075/lotus_europa_s2_type_54.html
EU-LOTUS-EUROPA-TYPE74-COUPE-2D-01	4000	1638	1079	Automobile-Catalog 1971 Lotus Europa Twin Cam specifications	https://www.automobile-catalog.com/car/1971/1433105/lotus_europa_twin_cam.html
EU-LOTUS-ELISE-S1-111-ROADSTER-STANDARD-01	3726	1701	1202	Auto-Data Lotus Elise Series 1 1.8 specifications	https://www.auto-data.net/en/lotus-elise-series-1-1.8-i-16v-120hp-8296
EU-LOTUS-ELISE-S1-111S-ROADSTER-01	3734	1701	1202	Auto-Data Lotus Elise Series 1 111S specifications	https://www.auto-data.net/en/lotus-elise-series-1-1.8-i-16v-111s-146hp-8297
EU-LOTUS-ESPRIT-S4-V8-COUPE-01	4370	1880	1150	Auto-Data Lotus Esprit 3.5 V8 Turbo specifications	https://www.auto-data.net/en/lotus-esprit-3.5-i-v8-32v-turbo-354hp-8305
EU-LOTUS-ESPRIT-X180-TURBO-SE-COUPE-01	4330	1860	1150	Auto-Data Lotus Esprit Turbo SE S4 specifications	https://www.auto-data.net/en/lotus-esprit-2.2-i-16v-turbo-se-s4-268hp-8299
EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	3900	1735	1230	Auto-Data Lotus Elan II M100 Turbo specifications	https://www.auto-data.net/en/lotus-elan-ii-m100-1.6-i-16v-turbo-167hp-8312
EU-LOTUS-EXCEL-TYPE89-COUPE-SE-SA-01	4395	1815	1205	Auto-Data Lotus Excel 2.2 SE/SA specifications	https://www.auto-data.net/en/lotus-excel-2.2-se-sa-184hp-8318
```

## 下一步优先处理

1. 仅处理 Movano B X62 FWD Bus 的可售轴距、车顶及车身长度组合。
2. 将 9698、9707、9708 批量关联至闭合后的相同尺寸组，不按功率重复建组。
3. PENDING 归零后立即进行一次机械检查并输出两张最终完整 TSV 与指定 sandbox 下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1967/1433000/lotus_europa_type_46.html?utm_source=chatgpt.com "1967 Lotus Europa (type 46) Specs Review (58 kW / 79 PS / 78 hp) (since mid-year 1967 for Europe France)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8601-8700_ktype_dimension_mapping_final.tsv
- all_8601-8700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* Movano B X62 FWD Bus 已闭合：9698 对应 L1H1 6-seat Combi；9707 拆为 L2H2 9-seat Combi 与 L3H2 17-seat Minibus；9708 对应 L2H2 9-seat Combi。官方乘用车型资料明确列出这些车身与动力组合。
* PENDING 已归零。
* 完成机械检查：映射表严格 10 列、尺寸组表严格 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；全部引用闭合；三维、来源和 URL 均非空。
* 复用的 38 个既有尺寸组保留任务提供的跨批次缓存值，未重新抓取或覆盖。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：139
* PENDING 映射：0
* DIMENSION_GROUP：95
* 孤立尺寸组：0
* 未闭合引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9593	9593	Sedan	300C I	LX	4	EU-CHRYSLER-300C-I-LX-SEDAN-4D-01	HIGH	2.7动力对应第一代LX轿车外廓。	READY
9594	9594	Wagon	300C I	LX	5	EU-CHRYSLER-300C-I-LX-WAGON-5D-01	HIGH	300C Touring五门旅行车外廓。	READY
9595	9595	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
9596	9596	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	HIGH		READY
9599	9599	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	HIGH		READY
9600_swb_prefl	9600	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款前分支。	READY
9600_swb_facelift	9600	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款后分支。	READY
9600_lwb_prefl	9600	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款前分支。	READY
9600_lwb_facelift	9600	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款后分支。	READY
9601_swb_prefl	9601	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款前分支。	READY
9601_swb_facelift	9601	Sedan	S-Klasse W220	W220	4	EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为短轴改款后分支。	READY
9601_lwb_prefl	9601	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款前分支。	READY
9601_lwb_facelift	9601	Sedan	S-Klasse W220	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	MEDIUM	同一Ktype覆盖短轴、长轴及改款前后；本行为长轴改款后分支。	READY
9602_3dr	9602	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9602_5dr	9602	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9608	9608	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9609	9609	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9610	9610	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9611	9611	MPV	Freemont	JC	5	EU-FIAT-FREEMONT-MPV-5D-01	HIGH		READY
9612	9612	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-G09-SEDAN-4D-PREFL-01	HIGH		READY
9615_prefl	9615	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	MEDIUM	生产区间覆盖改款前后；本行为改款前分支。	READY
9615_facelift	9615	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	MEDIUM	生产区间覆盖改款前后；本行为改款后分支。	READY
9620	9620	MPV	Touran I GP2	1T3	5	EU-VW-TOURAN-I-GP2-MPV-01	HIGH		READY
9621_3dr	9621	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9621_5dr	9621	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9623_3dr	9623	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-R-HATCHBACK-3D-01	MEDIUM	Golf R三门物理分支。	READY
9623_5dr	9623	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-R-HATCHBACK-5D-01	MEDIUM	Golf R五门物理分支。	READY
9629_prefl	9629	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9629_facelift	9629	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9630	9630	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	HIGH	生产结束时间位于2014年改款切换前。	READY
9639_3dr	9639	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9639_5dr	9639	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9640_3dr	9640	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9640_5dr	9640	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9641_3dr	9641	Hatchback	Focus I		3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9641_5dr	9641	Hatchback	Focus I		5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9642	9642	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9643	9643	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9644	9644	Sedan	Focus I		4	EU-FORD-FOCUS-I-SEDAN-4D-01	HIGH		READY
9645	9645	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9646	9646	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9647	9647	Wagon	Focus I		5	EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	HIGH		READY
9648_prefl	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为初期分支。	READY
9648_facelift01	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2001年改款分支。	READY
9648_facelift05	9648	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2005年改款分支。	READY
9649_prefl	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为初期分支。	READY
9649_facelift01	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2001年改款分支。	READY
9649_facelift05	9649	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	MEDIUM	生产区间覆盖三次外廓阶段；本行为2005年改款分支。	READY
9650_prefl	9650	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	MEDIUM	生产区间覆盖初期与2001年改款外廓；本行为初期分支。	READY
9650_facelift01	9650	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	MEDIUM	生产区间覆盖初期与2001年改款外廓；本行为2001年改款分支。	READY
9659_3dr	9659	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为三门分支。	READY
9659_5dr	9659	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	同一Ktype覆盖三门与五门车身；本行为五门分支。	READY
9683_facelift	9683	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9683_griffin	9683	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9684_facelift	9684	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9684_griffin	9684	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9685_facelift	9685	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9685_griffin	9685	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9686_facelift	9686	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-FACELIFT-CONVERTIBLE-2D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为标准改款分支。	READY
9686_griffin	9686	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	MEDIUM	生产区间覆盖标准改款与Griffin外廓；本行为Griffin分支。	READY
9692	9692	SUV	Tahoe II	GMT800	5	EU-CHEVROLET-TAHOE-II-GMT800-SUV-2004-06-01	MEDIUM	生产开始月份对应2004车型年度外廓。	READY
9693	9693	Wagon	Astra G	T98	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9694_3dr	9694	Hatchback	Astra G	T98	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门与五门CC车身；本行为三门分支。	READY
9694_5dr	9694	Hatchback	Astra G	T98	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖三门与五门CC车身；本行为五门分支。	READY
9695	9695	Coupe	Astra G		2	EU-OPEL-ASTRA-G-COUPE-2D-01	HIGH	Bertone双门Coupe外廓。	READY
9696	9696	Sedan	Astra G		4	EU-OPEL-ASTRA-G-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
9697	9697	Wagon	Astra J		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-5D-01	HIGH	Sports Tourer外廓；改款前后本组三维不变。	READY
9698	9698	MPV	Movano B	X62	5	EU-OPEL-MOVANO-B-X62-BUS-L1H1-FWD-01	HIGH	100PS FWD 6-seat Combi L1H1外廓。	READY
9699	9699	Coupe	Elite Type 75	75	3	EU-LOTUS-ELITE-TYPE75-COUPE-3D-01	HIGH		READY
9700	9700	Coupe	Eclat Type 76	76	2	EU-LOTUS-ECLAT-TYPE76-COUPE-2D-01	HIGH		READY
9701	9701	Coupe	Esprit S2	79	2	EU-LOTUS-ESPRIT-S2-COUPE-2D-01	MEDIUM	Ktype车型名称确定为S2；输入起始年月早于S2正式阶段。	READY
9702	9702	Coupe	Turbo Esprit	82	2	EU-LOTUS-ESPRIT-TYPE82-TURBO-COUPE-2D-01	HIGH		READY
9703	9703	Coupe	Elite Type 83	83	3	EU-LOTUS-ELITE-TYPE83-COUPE-3D-01	HIGH		READY
9704	9704	Coupe	Eclat Type 84	84	2	EU-LOTUS-ECLAT-TYPE84-COUPE-2D-01	MEDIUM	按Eclat 2.2车身边界映射。	READY
9705_pre84	9705	Coupe	Esprit S3	85	2	EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-EARLY-01	MEDIUM	生产区间覆盖1984年外廓更新；本行为早期分支。	READY
9705_late84	9705	Coupe	Esprit S3	85	2	EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-LATE-01	MEDIUM	生产区间覆盖1984年外廓更新；本行为后期分支。	READY
9706	9706	Coupe	Excel	89	2	EU-LOTUS-EXCEL-TYPE89-COUPE-STANDARD-01	HIGH	标准早期Excel外廓。	READY
9707_l2h2	9707	MPV	Movano B	X62	5	EU-OPEL-MOVANO-B-X62-BUS-L2H2-FWD-01	MEDIUM	125PS覆盖9-seat Combi L2H2；本行为L2H2分支。	READY
9707_l3h2	9707	MPV	Movano B	X62	5	EU-OPEL-MOVANO-B-X62-MINIBUS-L3H2-FWD-01	MEDIUM	125PS覆盖17-seat Minibus L3H2；本行为L3H2分支。	READY
9708	9708	MPV	Movano B	X62	5	EU-OPEL-MOVANO-B-X62-BUS-L2H2-FWD-01	HIGH	146PS FWD 9-seat Combi L2H2外廓。	READY
9709	9709	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH		READY
9710	9710	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH		READY
9711	9711	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH		READY
9712	9712	MPV	Zafira A	T98	5	EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	MEDIUM	生产区间覆盖2003年改款，物理外廓不变。	READY
9713	9713	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-4D-01	HIGH		READY
9714_pre13	9714	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9714_facelift13	9714	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9715	9715	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	2013年改款前后三维一致。	READY
9716_prefl	9716	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	MEDIUM	生产区间与2011年改款交叠；本行为改款前分支。	READY
9716_facelift	9716	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	MEDIUM	生产区间与2011年改款交叠；本行为改款后分支。	READY
9717	9717	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-01	HIGH	2013年改款前后三维一致。	READY
9718	9718	Coupe	780		2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
9719_type46	9719	Coupe	Europa S1	46	2	EU-LOTUS-EUROPA-TYPE46-COUPE-2D-01	MEDIUM	生产区间覆盖Type 46与Type 54；本行为Type 46分支。	READY
9719_type54	9719	Coupe	Europa S2	54	2	EU-LOTUS-EUROPA-TYPE54-COUPE-2D-01	MEDIUM	生产区间覆盖Type 46与Type 54；本行为Type 54分支。	READY
9720	9720	Coupe	Europa Twin Cam	74	2	EU-LOTUS-EUROPA-TYPE74-COUPE-2D-01	HIGH		READY
9721	9721	Convertible	Elise Series 1	111	2	EU-LOTUS-ELISE-S1-111-ROADSTER-STANDARD-01	HIGH	标准Series 1外廓。	READY
9722	9722	Convertible	Elise Series 1	111	2	EU-LOTUS-ELISE-S1-111S-ROADSTER-01	HIGH	111S外部长度与标准版不同。	READY
9723	9723	Coupe	Esprit S4		2	EU-LOTUS-ESPRIT-S4-V8-COUPE-01	HIGH	V8外廓。	READY
9724	9724	Coupe	Esprit X180/S4		2	EU-LOTUS-ESPRIT-X180-TURBO-SE-COUPE-01	HIGH	Turbo SE外廓。	READY
9725	9725	Convertible	Elan II	M100	2	EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	HIGH		READY
9727	9727	Convertible	Elan II	M100	2	EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	HIGH	自然吸气与Turbo版本复用相同外廓。	READY
9728	9728	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH		READY
9730	9730	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH		READY
9731	9731	Coupe	Excel	89	2	EU-LOTUS-EXCEL-TYPE89-COUPE-SE-SA-01	HIGH	SE/SA外廓。	READY
9732	9732	Hatchback	Corolla IX	E120	3	EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	HIGH	T Sport Compressor专属降低车身及外部套件。	READY
9733_prefl	9733	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	生产区间覆盖改款前后；本行为改款前分支。	READY
9733_facelift	9733	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖改款前后；本行为改款后分支。	READY
9734_pre13	9734	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9734_facelift13	9734	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9735_pre13	9735	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为更新前分支。	READY
9735_facelift13	9735	Sedan	S80 II	AS	4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	MEDIUM	生产区间覆盖2013年外廓更新；本行为2013年更新后分支。	READY
9737_prefl	9737	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2013年改款；本行为改款前分支。	READY
9737_facelift	9737	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2013年改款；本行为改款后分支。	READY
9739	9739	Sedan	Alfa Romeo 6	119	4	EU-ALFA-ROMEO-6-119-SEDAN-4D-01	HIGH		READY
9740	9740	Sedan	Alfa Romeo 6	119	4	EU-ALFA-ROMEO-6-119-SEDAN-4D-01	HIGH		READY
9743	9743	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	HIGH	2007年改款后的第一代XC90外廓。	READY
9749_prefl	9749	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9749_facelift	9749	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9752_prefl	9752	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9752_facelift	9752	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9753_prefl	9753	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-PREFL-01	MEDIUM	生产区间覆盖2014年改款；本行为改款前分支。	READY
9753_facelift	9753	Sedan	Jetta VI	162	4	EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖2014年改款；本行为改款后分支。	READY
9761	9761	Coupe	Alfasud Sprint	902A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	HIGH		READY
9762	9762	Convertible	RZ		2	EU-ALFA-ROMEO-RZ-CONVERTIBLE-2D-01	HIGH		READY
9764	9764	Wagon	33 905	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
9777	9777	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	HIGH		READY
9778_prefl	9778	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	MEDIUM	生产区间覆盖2010年改款；本行为改款前标准宽度分支。	READY
9778_facelift	9778	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-WIDE-01	MEDIUM	生产区间覆盖2010年改款；本行为改款后宽体分支。	READY
9780	9780	Wagon	33 907	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	HIGH		READY
9784	9784	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH		READY
9785	9785	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH		READY
9786	9786	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-FWD-01	HIGH	前驱旅行车外廓。	READY
9787	9787	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
9788	9788	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH		READY
9792	9792	Hatchback	Trezia		5	EU-SUBARU-TREZIA-HATCHBACK-5D-01	HIGH		READY
9793	9793	Hatchback	Trezia		5	EU-SUBARU-TREZIA-HATCHBACK-5D-01	HIGH		READY
9798_h1840	9798	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	MEDIUM	同一Ktype覆盖两个已确认车身高度；本行为1840 mm高度分支。	READY
9798_h1940	9798	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	MEDIUM	同一Ktype覆盖两个已确认车身高度；本行为1940 mm高度分支。	READY
9799	9799	Convertible	Korando II	KJ	2	EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8601-8700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-300C-I-LX-SEDAN-4D-01	5015	1880	1475	Automobile-Catalog 2007 Chrysler 300C 2.7 specifications	https://www.automobile-catalog.com/car/2007/524225/chrysler_300c_2_7.html
EU-CHRYSLER-300C-I-LX-WAGON-5D-01	5015	1880	1481	Automobile-Catalog 2007 Chrysler 300C Touring 2.7 specifications	https://www.automobile-catalog.com/car/2007/524300/chrysler_300c_touring_2_7.html
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4850	1843	1497	Auto-Data Chrysler Sebring Sedan JS 2.4i 16V specifications	https://www.auto-data.net/en/chrysler-sebring-sedan-js-2.4i-16v-172hp-automatic-24868
EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	4922	1816	1485	Automobile-Catalog 2008 Chrysler Sebring Convertible LX 2.4L specifications	https://www.automobile-catalog.com/car/2008/1211525/chrysler_sebring_convertible_lx_2_4l.html
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	5038	1855	1444	Auto-Data Mercedes-Benz S-Class W220 S 320 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-w220-s-320-v6-224hp-5g-tronic-13057
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	5043	1855	1444	Auto-Data Mercedes-Benz S-Class W220 facelift S 430 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-w220-facelift-2002-s-430-v8-279hp-5g-tronic-13064
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	5158	1855	1444	Auto-Data Mercedes-Benz S-Class Long V220 S 320 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-long-v220-s-320-v6-224hp-5g-tronic-13060
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444	Auto-Data Mercedes-Benz S-Class Long V220 facelift S 430 specifications	https://www.auto-data.net/en/mercedes-benz-s-class-long-v220-facelift-2002-s-430-v8-279hp-7g-tronic-44472
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-FIAT-FREEMONT-MPV-5D-01	4890	1880	1690	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-INSIGNIA-A-G09-SEDAN-4D-PREFL-01	4830	1856	1498	Vauxhall New Insignia official brochure October 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/insignia-a/Insignia_October_2008.pdf
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-TOURAN-I-GP2-MPV-01	4397	1794	1634	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-GOLF-VI-5K-HATCHBACK-3D-01	4199	1779	1480	Volkswagen UK Golf Mk6 official brochure February 2010	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_feb_2010.pdf
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-GOLF-VI-R-HATCHBACK-3D-01	4212	1786	1469	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-GOLF-VI-R-HATCHBACK-5D-01	4212	1786	1461	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VW-JETTA-VI-162-SEDAN-PREFL-01	4644	1778	1482	Auto-Data Volkswagen Jetta VI 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-jetta-vi-1.4-tsi-122hp-44516
EU-VW-JETTA-VI-162-SEDAN-FACELIFT-01	4659	1778	1482	Volkswagen UK Jetta brochure November 2017	https://www.vwpress.co.uk/assets/documents/original/17569-Jetta_brochure_11_17.pdf
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-hatchback-i-1.4-16v-75hp-7361
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1698	1430	Auto-Data Ford Focus Hatchback I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-hatchback-i-1.4-16v-75hp-7361
EU-FORD-FOCUS-I-SEDAN-4D-01	4362	1698	1430	Auto-Data Ford Focus I Sedan 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-i-sedan-1.4-16v-75hp-7353
EU-FORD-FOCUS-I-TURNIER-WAGON-5D-01	4438	1698	1447	Auto-Data Ford Focus Turnier I 1.4 16V specifications	https://www.auto-data.net/en/ford-focus-turnier-i-1.4-16v-75hp-7372
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492	Auto-Data Saab 9-5 Sport Combi 2.0 T specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-2.0-t-150hp-automatic-11856
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501	Auto-Data Saab 9-5 Sport Combi facelift 2001 specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2001-2.3-t-185hp-11859
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459	Auto-Data Saab 9-5 Sport Combi facelift 2005 specifications	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2005-1.9-tid-150hp-automatic-42748
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SAAB-9-3-II-FACELIFT-CONVERTIBLE-2D-01	4647	1762	1437	Automobile-Catalog 2008 Saab 9-3 1.9 TiD Cabriolet specifications	https://www.automobile-catalog.com/car/2008/3037655/saab_9-3_1_9_tid_150_cabriolet.html
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-CHEVROLET-TAHOE-II-GMT800-SUV-2004-06-01	5050	2002	1900	Edmunds 2004 Chevrolet Tahoe RWD specifications	https://www.edmunds.com/chevrolet/tahoe/2004/features-specs/
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-ASTRA-G-HATCHBACK-3D-01	4110	1709	1425	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-ASTRA-G-COUPE-2D-01	4267	1709	1390	Automobile-Catalog Opel Astra G Bertone Coupe specifications	https://www.automobile-catalog.com/car/2000/2519465/opel_astra_coupe_2_2_16v.html
EU-OPEL-ASTRA-G-SEDAN-4D-01	4252	1709	1425	Automobile-Catalog 2003 Opel Astra 4d 2.2 DTI specifications	https://www.automobile-catalog.com/car/2003/2519000/opel_astra_4d_2_2_dti_16v.html
EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-5D-01	4698	1814	1535	Automobile-Catalog 2011 Opel Astra Sports Tourer 1.7 CDTI specifications	https://www.automobile-catalog.com/car/2011/2530730/opel_astra_sports_tourer_1_7_cdti_110.html
EU-OPEL-MOVANO-B-X62-BUS-L1H1-FWD-01	5048	2070	2307	Vauxhall Movano Passenger Carriers official brochure 2013;Vauxhall Movano official brochure 2016	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Passenger_Carrier_Sept_2013_v2.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2016.pdf
EU-LOTUS-ELITE-TYPE75-COUPE-3D-01	4458	1816	1207	Encycarpedia Lotus Elite Type 75 specifications	https://www.encycarpedia.com/lotus/74-elite-s2-coupe
EU-LOTUS-ECLAT-TYPE76-COUPE-2D-01	4458	1816	1207	Auto-Data Lotus Eclat generation specifications	https://www.auto-data.net/en/lotus-eclat-generation-1828
EU-LOTUS-ESPRIT-S2-COUPE-2D-01	4191	1854	1111	Automobile-Catalog 1979 Lotus Esprit S2 specifications	https://www.automobile-catalog.com/car/1979/1434335/lotus_esprit_s2.html
EU-LOTUS-ESPRIT-TYPE82-TURBO-COUPE-2D-01	4330	1860	1150	Auto-Data Lotus Esprit 2.2 Turbo specifications	https://www.auto-data.net/en/lotus-esprit-2.2-turbo-218hp-8304
EU-LOTUS-ELITE-TYPE83-COUPE-3D-01	4458	1816	1207	Automobile-Catalog 1980 Lotus Elite S 2.2 specifications	https://www.automobile-catalog.com/car/1980/44060/lotus_elite_s_2_2.html
EU-LOTUS-ECLAT-TYPE84-COUPE-2D-01	4458	1816	1207	Auto-Data Lotus Eclat 2.2 specifications	https://www.auto-data.net/en/lotus-eclat-2.2-162hp-8291
EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-EARLY-01	4191	1854	1118	Automobile-Catalog 1981 Lotus Esprit S3 specifications	https://www.automobile-catalog.com/car/1981/1434635/lotus_esprit_s3.html
EU-LOTUS-ESPRIT-S3-TYPE85-COUPE-LATE-01	4224	1854	1111	Automobile-Catalog 1986 Lotus Esprit S3 specifications	https://www.automobile-catalog.com/car/1986/23825/lotus_esprit_s3.html
EU-LOTUS-EXCEL-TYPE89-COUPE-STANDARD-01	4395	1815	1205	Auto-Data Lotus Excel 2.2 specifications	https://www.auto-data.net/en/lotus-excel-2.2-162hp-8317
EU-OPEL-MOVANO-B-X62-BUS-L2H2-FWD-01	5548	2070	2500	Vauxhall Movano Passenger Carriers official brochure 2013;Vauxhall Movano official brochure 2016	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Passenger_Carrier_Sept_2013_v2.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2016.pdf
EU-OPEL-MOVANO-B-X62-MINIBUS-L3H2-FWD-01	6198	2070	2488	Vauxhall Movano Passenger Carriers official brochure 2013;Vauxhall Movano official brochure 2016	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Passenger_Carrier_Sept_2013_v2.pdf;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2016.pdf
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-OPEL-ZAFIRA-A-T98-MPV-5D-01	4317	1742	1684	Auto-Data Opel Zafira A T3000 specifications;Auto-Data Opel Zafira A facelift 2003 specifications	https://www.auto-data.net/en/opel-zafira-a-t3000-generation-574;https://www.auto-data.net/en/opel-zafira-a-facelift-2003-generation-5178
EU-CADILLAC-STS-I-SEDAN-4D-01	4986	1844	1463	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-XC70-II-WAGON-01	4838	1870	1604	Auto-Data Volvo XC70 II 3.2 specifications;Auto-Data Volvo XC70 II facelift 2013 specifications	https://www.auto-data.net/en/volvo-xc70-ii-3.2-243hp-geartronic-24704;https://www.auto-data.net/en/volvo-xc70-ii-facelift-2013-2.0-d4-163hp-19789
EU-LANCIA-DELTA-III-844-HATCHBACK-PREFL-01	4510	1797	1497	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-LANCIA-DELTA-III-844-HATCHBACK-FACELIFT-01	4520	1797	1499	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-780-COUPE-2D-01	4794	1750	1400	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-LOTUS-EUROPA-TYPE46-COUPE-2D-01	3960	1630	1070	Automobile-Catalog 1967 Lotus Europa Type 46 specifications	https://www.automobile-catalog.com/car/1967/1433000/lotus_europa_type_46.html
EU-LOTUS-EUROPA-TYPE54-COUPE-2D-01	3993	1638	1080	Automobile-Catalog 1969 Lotus Europa S2 Type 54 specifications	https://www.automobile-catalog.com/car/1969/1433075/lotus_europa_s2_type_54.html
EU-LOTUS-EUROPA-TYPE74-COUPE-2D-01	4000	1638	1079	Automobile-Catalog 1971 Lotus Europa Twin Cam specifications	https://www.automobile-catalog.com/car/1971/1433105/lotus_europa_twin_cam.html
EU-LOTUS-ELISE-S1-111-ROADSTER-STANDARD-01	3726	1701	1202	Auto-Data Lotus Elise Series 1 1.8 specifications	https://www.auto-data.net/en/lotus-elise-series-1-1.8-i-16v-120hp-8296
EU-LOTUS-ELISE-S1-111S-ROADSTER-01	3734	1701	1202	Auto-Data Lotus Elise Series 1 111S specifications	https://www.auto-data.net/en/lotus-elise-series-1-1.8-i-16v-111s-146hp-8297
EU-LOTUS-ESPRIT-S4-V8-COUPE-01	4370	1880	1150	Auto-Data Lotus Esprit 3.5 V8 Turbo specifications	https://www.auto-data.net/en/lotus-esprit-3.5-i-v8-32v-turbo-354hp-8305
EU-LOTUS-ESPRIT-X180-TURBO-SE-COUPE-01	4330	1860	1150	Auto-Data Lotus Esprit Turbo SE S4 specifications	https://www.auto-data.net/en/lotus-esprit-2.2-i-16v-turbo-se-s4-268hp-8299
EU-LOTUS-ELAN-II-M100-CONVERTIBLE-2D-01	3900	1735	1230	Auto-Data Lotus Elan II M100 Turbo specifications	https://www.auto-data.net/en/lotus-elan-ii-m100-1.6-i-16v-turbo-167hp-8312
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-LOTUS-EXCEL-TYPE89-COUPE-SE-SA-01	4395	1815	1205	Auto-Data Lotus Excel 2.2 SE/SA specifications	https://www.auto-data.net/en/lotus-excel-2.2-se-sa-184hp-8318
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	4200	1710	1460	UltimateSpecs Toyota Corolla IX 1.8 TTE Compressor specifications	https://www.ultimatespecs.com/car-specs/Toyota/1567/Toyota-Corolla-IX-18-TTE-Compressor.html
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484	Auto-Data Volvo S60 model dimensions	https://www.auto-data.net/en/volvo-s60-model-917
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data Volvo S60 II facelift 1.6 D2 specifications	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-1.6-d2-115hp-18415
EU-ALFA-ROMEO-6-119-SEDAN-4D-01	4679	1684	1395	Auto-Data Alfa Romeo 6 119 generation specifications	https://www.auto-data.net/en/alfa-romeo-6-119-generation-398
EU-VOLVO-XC90-I-SUV-FACELIFT-01	4807	1936	1784	Auto-Data Volvo XC90 facelift D5 AWD specifications	https://www.auto-data.net/en/volvo-xc90-facelift-2007-2.4-d5-200hp-awd-automatic-18204
EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-RZ-CONVERTIBLE-2D-01	4060	1730	1300	Auto-Data Alfa Romeo RZ 3.0 V6 specifications	https://www.auto-data.net/en/alfa-romeo-rz-3.0-i-v6-210hp-1359
EU-ALFA-ROMEO-33-905-WAGON-FWD-01	4142	1612	1345	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SUBARU-FORESTER-III-SH-SUV-STANDARD-01	4560	1780	1700	Auto-Data Subaru Forester III 2.5 XS specifications;Auto-Data Subaru Forester III facelift 2.0 i specifications	https://www.auto-data.net/en/subaru-forester-iii-2.5-xs-171hp-16210;https://www.auto-data.net/en/subaru-forester-iii-facelift-2010-2.0-i-150hp-17915
EU-SUBARU-FORESTER-III-SH-SUV-WIDE-01	4560	1795	1700	Auto-Data Subaru Forester III facelift 2.5 specifications	https://www.auto-data.net/en/subaru-forester-iii-facelift-2010-2.5-171hp-awd-e-4at-54229
EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	4410	1660	1450	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SUBARU-LEONE-III-WAGON-5D-FWD-01	4410	1660	1420	Automobile-Catalog 1994 Subaru Leone Estate Van 1.6 LC specifications	https://www.automobile-catalog.com/car/1994/3213590/subaru_leone_estate_van_1_6_lc.html
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SUBARU-TREZIA-HATCHBACK-5D-01	3995	1695	1595	Auto-Data Subaru Trezia generation specifications	https://www.auto-data.net/en/subaru-trezia-generation-3985
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	4340	1850	1850	Task-provided cross-batch existing dimension-group index	sandbox:/mnt/data/all_8601-8700_cross_batch_dimension_index_source.txt
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8601-8700_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8601-8700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8601-8700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10774 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3356 行）

