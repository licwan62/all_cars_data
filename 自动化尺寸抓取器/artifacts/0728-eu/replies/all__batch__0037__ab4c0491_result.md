# 任务：all 第 3601-3700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0037__ab4c0491


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3601-3700 行

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
all 第 3601-3700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-164-164-SEDAN-FACELIFT-01	4555	1760	1390
EU-ALFA-ROMEO-164-164-SEDAN-PREFL-01	4565	1760	1390
EU-ALFA-ROMEO-164-164-SEDAN-QV24V-01	4555	1760	1390
EU-ALFA-ROMEO-164-164-SEDAN-SUPER-01	4665	1760	1390
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-7-E23-SEDAN-01	4860	1800	1430
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340
EU-FIAT-CINQUECENTO-HATCHBACK-01	3227	1487	1435
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	3864	1716	1721
EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	3959	1716	1721
EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	3957	1716	1721
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904
EU-FIAT-FIORINO-I-VAN-01	3635	1690	1810
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514
EU-FIAT-TEMPRA-SEDAN-01	4354	1695	1445
EU-FIAT-TEMPRA-WAGON-4X4-01	4472	1695	1540
EU-FIAT-TEMPRA-WAGON-FWD-01	4472	1695	1500
EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	3958	1700	1445
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450
EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	3958	1700	1445
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450
EU-PEUGEOT-106-I-HATCHBACK-3D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-5D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	3564	1607	1360
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	3995	1695	1365
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-3D-01	3995	1692	1367
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-5D-01	3995	1692	1367
EU-PEUGEOT-405-II-BREAK-01	4398	1704	1445
EU-PEUGEOT-405-II-SEDAN-MI16-01	4408	1716	1406
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406
EU-PEUGEOT-405-II-SEDAN-T16-01	4408	1716	1390
EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	4765	1799	1417
EU-PEUGEOT-605-I-FACELIFT-SEDAN-SV24-01	4765	1799	1411
EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	4765	1799	1415
EU-PEUGEOT-605-I-SEDAN-STANDARD-01	4723	1799	1417
EU-PEUGEOT-605-I-SEDAN-SV24-01	4723	1799	1411
EU-PEUGEOT-605-I-SEDAN-V6-01	4723	1799	1415
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693
EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	3982	1588	1803
EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	3982	1588	1790
EU-RENAULT-RAPID-PHASE23-VAN-01	4056	1566	1776
EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	4770	1820	1440
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	5182	1904	1958
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037
EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	4542	1905	2037
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	3	316 I	Coupe	Heckantrieb	Benzin	75	102	Sep 1993	Nov 1998	2024-03-01	3726
BMW	5	540 I	Kombi	Heckantrieb	Benzin	210	286	Sep 1993	Jul 1996	2024-03-01	3727
BMW	3	318 I	Cabriolet	Heckantrieb	Benzin	85	115	Mar 1994	Nov 1999	2024-03-01	3728
Peugeot	106 i	1.6	Schrägheck	Frontantrieb	Benzin	76	103	Nov 1994	Apr 1996	2024-03-01	3729
Peugeot	306	2.0 S16	Schrägheck	Frontantrieb	Benzin	110	150	Jun 1994	May 2001	2024-03-01	3730
Peugeot	306	1.8	Cabriolet	Frontantrieb	Benzin	74	101	Mar 1994	Apr 2002	2024-03-01	3731
Peugeot	306	2	Cabriolet	Frontantrieb	Benzin	89	121	Mar 1994	Apr 2002	2024-03-01	3732
Peugeot	Boxer	2.0 I	Bus	Frontantrieb	Benzin	80	109	Mar 1994	Apr 2002	2024-03-01	3733
Peugeot	Boxer	2.5 D	Bus	Frontantrieb	Diesel	63	86	Aug 1994	Apr 2002	2024-03-01	3734
Peugeot	Boxer	1.9 TD	Bus	Frontantrieb	Diesel	66	90	Aug 1994	Apr 2002	2024-03-01	3735
Peugeot	Boxer	1.9 TD	Bus	Frontantrieb	Diesel	68	92	Mar 1994	Apr 2002	2024-03-01	3736
Peugeot	Boxer	2.5 TD	Bus	Frontantrieb	Diesel	76	103	Jul 1994	Dec 1997	2024-03-01	3737
Peugeot	106 i	1.5 D	Schrägheck	Frontantrieb	Diesel	40	54	Jun 1994	Apr 1996	2024-03-01	3738
Peugeot	806	2.0 Turbo	Großraumlimousine	Frontantrieb	Benzin	108	147	Jun 1994	Aug 2002	2024-03-01	3739
Peugeot	806	2	Großraumlimousine	Frontantrieb	Benzin	89	121	Jun 1994	Aug 2002	2024-03-01	3740
Peugeot	306	1.9 D	Schrägheck	Frontantrieb	Diesel	50	68	Jun 1994	May 2001	2024-03-01	3741
Peugeot	306	1.1	Stufenheck	Frontantrieb	Benzin	44	60	Jun 1994	May 2001	2024-03-01	3742
Peugeot	306	1.4 SL	Stufenheck	Frontantrieb	Benzin	55	75	Jun 1994	May 2001	2024-03-01	3743
Peugeot	306	1.8 ST	Stufenheck	Frontantrieb	Benzin	74	101	Jun 1994	May 2001	2024-03-01	3744
Peugeot	306	1.6 SR	Stufenheck	Frontantrieb	Benzin	65	89	Jun 1994	Oct 2000	2024-03-01	3745
Peugeot	306	1.9 Srdt	Stufenheck	Frontantrieb	Diesel	66	90	Jun 1994	May 2001	2024-03-01	3746
Peugeot	306	1.9 SLD	Stufenheck	Frontantrieb	Diesel	47	64	Jun 1994	May 2001	2024-03-01	3747
Peugeot	306	2.0 ST	Stufenheck	Frontantrieb	Benzin	89	121	Jul 1994	May 2001	2024-03-01	3748
Peugeot	306	2.0 S16	Stufenheck	Frontantrieb	Benzin	112	152	Jun 1994	May 2001	2024-03-01	3749
Peugeot	306	2.0 S16	Stufenheck	Frontantrieb	Benzin	110	150	Jun 1994	May 2001	2024-03-01	3750
Peugeot	306	1.9 SLD	Stufenheck	Frontantrieb	Diesel	50	68	Jun 1994	May 2001	2024-03-01	3751
Peugeot	405 ii	1.9 D	Stufenheck	Frontantrieb	Diesel	50	68	Jun 1994	Oct 1995	2024-03-01	3752
Peugeot	405 ii	2.0 16V	Stufenheck	Frontantrieb	Benzin	110	150	Jun 1994	Oct 1995	2024-03-01	3753
Peugeot	405 ii break	1.9 D	Kombi	Frontantrieb	Diesel	50	68	Jun 1994	Oct 1996	2024-03-01	3754
Peugeot	605	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	108	147	Jul 1991	Sep 1999	2024-03-01	3755
Peugeot	605	2.0 16V	Stufenheck	Frontantrieb	Benzin	97	132	Jul 1994	Sep 1999	2024-03-01	3756
Peugeot	605	2.5 Turbo Diesel	Stufenheck	Frontantrieb	Diesel	95	129	Jul 1994	Sep 1999	2024-03-01	3757
Renault	19 ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1992	Dec 1995	2024-03-01	3758
Renault	19 ii chamade	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Nov 1993	Dec 1995	2024-03-01	3759
Renault	19 ii	1.8	Schrägheck	Frontantrieb	Benzin	79	107	May 1994	Dec 1995	2024-03-01	3760
Renault	19 ii chamade	1.8	Stufenheck	Frontantrieb	Benzin	79	107	May 1994	Dec 1995	2024-03-01	3761
Renault	Laguna i	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Nov 1993	Mar 2001	2024-03-01	3762
Renault	Laguna i	2.2 D	Schrägheck	Frontantrieb	Diesel	61	83	Nov 1993	Mar 2001	2024-03-01	3763
Renault	Laguna i	3	Schrägheck	Frontantrieb	Benzin	123	167	Nov 1993	Mar 2001	2024-03-01	3764
Renault	Laguna i	2	Schrägheck	Frontantrieb	Benzin	83	113	Nov 1993	Mar 2001	2024-03-01	3765
Renault	Safrane i	2.1 DT	Schrägheck	Frontantrieb	Diesel	65	88	Nov 1993	Jul 1996	2024-03-01	3766
Renault	Clio i	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1994	Apr 1996	2026-05-01	3767
Renault	Clio i	1.8 RSI	Schrägheck	Frontantrieb	Benzin	79	107	Aug 1995	Sep 1998	2026-05-01	3768
Renault	Trafic	2.1 D	Bus	Frontantrieb	Diesel	47	64	Jun 1994	Oct 1997	2024-03-01	3769
Renault	Trafic	2.2	Bus	Frontantrieb	Benzin	74	101	Jun 1994	Oct 1997	2024-03-01	3770
Renault	Rapid	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	40	54	Sep 1994	Mar 1998	2024-03-01	3771
Renault	Rapid	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	58	79	Jan 1994	Mar 1998	2024-03-01	3772
Renault	Espace ii	2	Großraumlimousine	Frontantrieb	Benzin	76	103	Jan 1991	Oct 1996	2024-03-01	3773
Mini	Mini	Cooper S JCW	Cabriolet	Frontantrieb	Benzin	147	200	Nov 2011	Apr 2015	2024-03-01	3775
Fiat	Ducato	1.9 TD Panorama/combinato	Bus	Frontantrieb	Diesel	60	82	Mar 1994	Apr 2002	2024-03-01	3776
Fiat	Ducato	2.5 TDI Panorama/combinato	Bus	Frontantrieb	Diesel	85	116	Mar 1994	Apr 2002	2024-03-01	3777
Fiat	Ducato	2.0 Panorama/combinato	Bus	Frontantrieb	Benzin	80	109	Mar 1994	Apr 2002	2024-03-01	3778
Fiat	Ducato	2.5 TDI Panorama/combinato	Bus	Frontantrieb	Diesel	80	109	Jul 1994	Apr 2002	2024-03-01	3779
Fiat	Cinquecento	0.7 I	Schrägheck	Frontantrieb	Benzin	22	30	Jul 1994	Jan 1998	2024-03-01	3780
Fiat	Ducato	2.5 D Combinato	Bus	Frontantrieb	Diesel	62	84	Aug 1994	Apr 2002	2024-03-01	3781
Fiat	Ducato	1.9 TD Combinato	Bus	Frontantrieb	Diesel	59	80	Aug 1994	Apr 2002	2024-03-01	3782
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	147	200	Feb 2010	Jun 2015	2024-03-01	3783
Hyundai	I30	1.4	Schrägheck	Frontantrieb	Benzin	73	99	Dec 2011	Dec 2015	2024-03-01	3784
Fiat	Ulysse	2.0 Turbo	Großraumlimousine	Frontantrieb	Benzin	108	147	Jun 1994	Aug 2002	2024-03-01	3785
Fiat	Ulysse	2	Großraumlimousine	Frontantrieb	Benzin	89	121	Jun 1994	Aug 2002	2024-03-01	3786
Fiat	Tempra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1994	Aug 1996	2024-03-01	3787
Fiat	Tempra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	76	103	Sep 1993	Aug 1996	2024-03-01	3788
Fiat	Tempra	1.8 I.e.	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1993	Aug 1996	2024-03-01	3789
Fiat	Tempra	1.6 I.e.	Stufenheck	Frontantrieb	Benzin	66	90	Jun 1994	Aug 1996	2024-03-01	3790
Fiat	Tempra	1.8 I.e.	Kombi	Frontantrieb	Benzin	74	101	Oct 1994	Aug 1996	2024-03-01	3791
Fiat	Tempra	1.8 I.e.	Kombi	Frontantrieb	Benzin	76	103	Sep 1993	Aug 1996	2024-03-01	3792
Fiat	Tempra	1.8 I.e.	Kombi	Frontantrieb	Benzin	66	90	Sep 1993	Aug 1996	2024-03-01	3793
Fiat	Tempra	1.6 I.e.	Kombi	Frontantrieb	Benzin	66	90	Jun 1994	Aug 1996	2024-03-01	3794
Fiat	Punto	55 1.1	Schrägheck	Frontantrieb	Benzin	40	54	Sep 1993	Sep 1999	2024-03-01	3795
Fiat	Punto	60 1.2	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1994	Sep 1999	2024-03-01	3796
Fiat	Punto	75 1.2	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1993	Sep 1999	2024-03-01	3797
Fiat	Punto	1.4 GT Turbo	Schrägheck	Frontantrieb	Benzin	98	133	Oct 1993	Mar 1997	2024-03-01	3798
Fiat	Punto	1.7 TD	Schrägheck	Frontantrieb	Diesel	52	71	Jan 1994	Sep 1999	2024-03-01	3799
Fiat	Punto	1.7 TD	Schrägheck	Frontantrieb	Diesel	51	69	Jan 1994	Sep 1999	2024-03-01	3800
Fiat	Punto	60 1.2	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1993	Sep 1999	2024-03-01	3801
Fiat	Punto	60 1.2	Cabriolet	Frontantrieb	Benzin	43	58	Apr 1994	Jun 2000	2024-03-01	3802
Fiat	Punto	90 1.6	Cabriolet	Frontantrieb	Benzin	65	88	Apr 1994	Apr 1997	2024-03-01	3803
Fiat	Coupe	2.0 16V	Coupe	Frontantrieb	Benzin	102	139	Nov 1993	Aug 1996	2024-03-01	3804
Fiat	Coupe	2.0 16V Turbo	Coupe	Frontantrieb	Benzin	140	190	Nov 1993	Aug 1996	2024-03-01	3805
Fiat	Punto	1.6	Schrägheck	Frontantrieb	Benzin	65	88	Jan 1994	Apr 1997	2024-03-01	3806
Fiat	Cinquecento	1.1 Sporting	Schrägheck	Frontantrieb	Benzin	40	54	Oct 1994	Jan 1998	2024-03-01	3807
Fiat	Tipo	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	74	101	Oct 1994	Oct 1995	2024-03-01	3808
Fiat	Tipo	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1993	Apr 1995	2024-03-01	3809
Fiat	Fiorino	75 I.e. 1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Oct 1993	May 2001	2024-03-01	3810
BMW	3	316 I	Schrägheck	Heckantrieb	Benzin	75	102	Jan 1994	Aug 2000	2024-03-01	3811
BMW	7	730 I, IL	Stufenheck	Heckantrieb	Benzin	155	211	Oct 1994	Nov 2001	2024-03-01	3812
BMW	7	730 I, IL	Stufenheck	Heckantrieb	Benzin	160	218	Mar 1994	Feb 1996	2024-03-01	3813
BMW	7	740 I, IL	Stufenheck	Heckantrieb	Benzin	210	286	Mar 1994	Feb 1996	2024-03-01	3814
BMW	7	750 I, IL	Stufenheck	Heckantrieb	Benzin	240	326	Nov 1994	Jul 2001	2024-03-01	3815
BMW	8	850 CI	Coupe	Heckantrieb	Benzin	240	326	Sep 1994	Dec 1999	2024-03-01	3816
BMW	5	518 G	Kombi	Heckantrieb	Benzin/Erdgas (CNG)	74	101	Feb 1996	Jul 1996	2024-03-01	3817
BMW	3	318 TDS	Stufenheck	Heckantrieb	Diesel	66	90	Jan 1995	Feb 1998	2024-03-01	3818
Alfa Romeo	164	3.0 24V Q4	Stufenheck	Allrad	Benzin	170	231	Feb 1994	Sep 1998	2024-03-01	3819
Alfa Romeo	145	1.7 I.e. 16V	Schrägheck	Frontantrieb	Benzin	95	129	Oct 1994	Dec 1996	2024-03-01	3820
Alfa Romeo	145	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	76	103	Oct 1994	Dec 1996	2024-03-01	3821
Alfa Romeo	145	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1994	Dec 1996	2024-03-01	3822
Alfa Romeo	145	1.9 TD	Schrägheck	Frontantrieb	Diesel	66	90	Oct 1994	Feb 1999	2024-03-01	3823
BMW	3	318 TDS	Schrägheck	Heckantrieb	Diesel	66	90	Jun 1995	Aug 2000	2024-03-01	3824
BMW	3	318 TI	Schrägheck	Heckantrieb	Benzin	103	140	Sep 1994	Dec 1995	2024-03-01	3825
Maserati	Quattroporte v	4.7 S	Stufenheck	Heckantrieb	Benzin	317	431	Jun 2008	-	2024-03-01	3826


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理外廓聚类完成 **39 个 Ktype、51 条映射行**，全部复用跨批次已有尺寸组，共命中 **30 个 DIMENSION_GROUP_ID**，未重复抓取或重建尺寸事实。
* Peugeot 106、Renault 19 II 和 Clio I 的对应资料存在 3 门、5 门车身边界，因此相关 Ktype 拆分派生行；Peugeot 306 1.9 D 的生产期跨越 Phase I 与 facelift，按门数及改款边界拆分。([汽车数据网][1])
* Fiat Tipo 1.8 101 hp 与 90 hp 分别关联累计表中 1445 mm、1450 mm 高度分支。([汽车目录][2])
* Alfa Romeo 164 Q4 当前来源分别给出 `4670×1760×1360` 与 `4665×1760×1356`，且均不等于已有尺寸组高度，因此本轮未错误复用或覆盖缓存，留待下一轮创建新组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：39
* READY 映射行：51
* PENDING Ktype：61
* 本轮复用尺寸组：30
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3726	3726	Coupe	3 Series E36	E36	2	EU-BMW-3-SERIES-E36-COUPE-01	HIGH	E36双门Coupe。	READY
3727	3727	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH	E34五门Touring。	READY
3728	3728	Convertible	3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH	E36双门Cabriolet。	READY
3729_3dr	3729	Hatchback	106 I	1A/C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3729_5dr	3729	Hatchback	106 I	1A/C	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3738_3dr	3738	Hatchback	106 I	1A/C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3738_5dr	3738	Hatchback	106 I	1A/C	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3741_3dr_prefl	3741	Hatchback	306 Phase I	7A/C	3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且资料列明3/5门。	READY
3741_5dr_prefl	3741	Hatchback	306 Phase I	7A/C	5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且资料列明3/5门。	READY
3741_3dr_facelift	3741	Hatchback	306 Phase II	7A/C	3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	MEDIUM	生产期跨改款且资料列明3/5门。	READY
3741_5dr_facelift	3741	Hatchback	306 Phase II	7A/C	5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	MEDIUM	生产期跨改款且资料列明3/5门。	READY
3752	3752	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH	405 II标准四门轿车。	READY
3753	3753	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-MI16-01	HIGH	2.0 16V对应Mi16外廓。	READY
3754	3754	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH	405 II Break五门旅行车。	READY
3755_prefl	3755	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-STANDARD-01	MEDIUM	生产期跨605改款边界。	READY
3755_facelift	3755	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	MEDIUM	生产期跨605改款边界。	READY
3756	3756	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	改款期标准四门轿车。	READY
3757	3757	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	改款期标准四门轿车。	READY
3758_3dr	3758	Hatchback	19 II	C53	3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3758_5dr	3758	Hatchback	19 II	B53	5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3759	3759	Sedan	19 II Chamade	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53四门Chamade。	READY
3760_3dr	3760	Hatchback	19 II	C53	3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3760_5dr	3760	Hatchback	19 II	B53	5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3761	3761	Sedan	19 II Chamade	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53四门Chamade。	READY
3767_3dr	3767	Hatchback	Clio I Phase I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3767_5dr	3767	Hatchback	Clio I Phase I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3768_3dr	3768	Hatchback	Clio I Phase I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3768_5dr	3768	Hatchback	Clio I Phase I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3769	3769	MPV	Trafic I Phase II			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	累计组限定SWB低顶Bus外廓。	READY
3770	3770	MPV	Trafic I Phase II			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	累计组限定SWB低顶Bus外廓。	READY
3771	3771	Van	Rapid Phase II/III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Kasten/乘用厢式共用该外廓。	READY
3772	3772	Van	Rapid Phase II/III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Kasten/乘用厢式共用该外廓。	READY
3773	3773	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63五门MPV。	READY
3780	3780	Hatchback	Cinquecento	170	3	EU-FIAT-CINQUECENTO-HATCHBACK-01	HIGH	Type 170三门Hatchback。	READY
3787	3787	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3788	3788	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3789	3789	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3790	3790	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3791	3791	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3792	3792	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3793	3793	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3794	3794	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3807	3807	Hatchback	Cinquecento	170	3	EU-FIAT-CINQUECENTO-HATCHBACK-01	HIGH	Sporting不改变Type 170外廓。	READY
3808_3dr	3808	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	MEDIUM	101 hp版本按1445 mm车高分支，门数需拆分。	READY
3808_5dr	3808	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	101 hp版本按1445 mm车高分支，门数需拆分。	READY
3809_3dr	3809	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	90 hp版本按1450 mm车高分支，门数需拆分。	READY
3809_5dr	3809	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	90 hp版本按1450 mm车高分支，门数需拆分。	READY
3810	3810	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Type 146厢式车外廓。	READY
3816	3816	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850-01	HIGH	E31双门850Ci。	READY
3817	3817	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH	CNG动力不改变E34 Touring外廓。	READY
3818	3818	Sedan	3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH	E36四门Sedan。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无（本轮仅复用跨批次已有尺寸组，未首次创建或修正尺寸事实）。

## 下一步优先处理

1. 优先闭合 Peugeot Boxer 与 Fiat Ducato 第二代 Bus/Combinato，确认轴距及车顶分支并批量建立尺寸组。
2. 处理 Peugeot 306 Cabriolet、Sedan，以及共平台的 Peugeot 806、Fiat Ulysse。
3. 处理 BMW E38、E36 Compact、Alfa Romeo 145/164 Q4、Mini R57、Hyundai i30 GD、Fiat Punto/Coupe 与 Maserati Quattroporte V。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-106-i-1a-c-1.5-d-55hp-5417 "Peugeot 106 I (1A/C) 1.5 D (55 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1994/718745/fiat_tipo_1_8_i_e__gt.html?utm_source=chatgpt.com "1994 Fiat Tipo 1.8 i.e. GT Specs Review (76 kW ..."
[3]: https://www.auto-data.net/en/alfa-romeo-164-164-3.0-24v-228hp-q4-1254?utm_source=chatgpt.com "Alfa Romeo 164 (164) 3.0 24V (228 Hp) Q4 /Sedan 1994"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增完成 **50 个 Ktype、75 条 READY 映射行**；另修正上一轮 8 条映射，将 `1A/C`、`7A/C` 这类组合代码清空，避免违反单行只能填写一个明确 `BodyCode` 的规则。
* Peugeot 306 S16 已拆分 3 门、5 门。当前直接资料给出 `3995×1692×1365 mm`，与累计表已有 3 门组的 `WidthMM=1695` 不同，因此未覆盖旧组，新建 3 门 `-02` 和独立 5 门组。306 Cabrio 同时按 1997 年改款前后拆为长度 4144 mm、4179 mm 两组。([汽车目录][1])
* 本轮同时闭合 Peugeot 806/306 Sedan、Renault Laguna/Safrane、MINI R57、Hyundai i30 GD、Fiat Ulysse/Punto/Coupé、BMW E36 Compact/E38、Alfa Romeo 145/164 Q4、Maserati Quattroporte V 等车身簇。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射行：126
* PENDING Ktype：11
* 已确认尺寸组：54
* 本轮首次创建尺寸组：24
* 剩余 PENDING：3733、3734、3735、3736、3737、3776、3777、3778、3779、3781、3782
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3729_3dr	3729	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3729_5dr	3729	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3730_3dr	3730	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	MEDIUM	输入Ktype覆盖3/5门S16分支。	READY
3730_5dr	3730	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门S16分支。	READY
3731_prefl	3731	Convertible	306 Cabrio Phase I	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3731_facelift	3731	Convertible	306 Cabrio Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3732_prefl	3732	Convertible	306 Cabrio Phase I	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3732_facelift	3732	Convertible	306 Cabrio Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3738_3dr	3738	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3738_5dr	3738	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3739	3739	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221五门MPV外廓。	READY
3740	3740	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221五门MPV外廓。	READY
3741_3dr_prefl	3741	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_5dr_prefl	3741	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_3dr_facelift	3741	Hatchback	306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_5dr_facelift	3741	Hatchback	306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3742_prefl	3742	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3742_facelift	3742	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3743_prefl	3743	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3743_facelift	3743	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3744_prefl	3744	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3744_facelift	3744	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3745_prefl	3745	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3745_facelift	3745	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3746_prefl	3746	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3746_facelift	3746	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3747_prefl	3747	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3747_facelift	3747	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3748_prefl	3748	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3748_facelift	3748	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3749_prefl	3749	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3749_facelift	3749	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3750_prefl	3750	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3750_facelift	3750	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3751_prefl	3751	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3751_facelift	3751	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3762	3762	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3763	3763	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3764	3764	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3765	3765	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3766	3766	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH	B54标准五门掀背外廓。	READY
3775	3775	Convertible	MINI R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	R57改款期双门敞篷外廓。	READY
3783_prefl	3783	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	MEDIUM	生产期跨2010年改款边界。	READY
3783_facelift	3783	Convertible	MINI R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	生产期跨2010年改款边界。	READY
3784	3784	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3785	3785	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH	220五门MPV外廓。	READY
3786	3786	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH	220五门MPV外廓。	READY
3795_3dr	3795	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3795_5dr	3795	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3796_3dr	3796	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3796_5dr	3796	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3797_3dr	3797	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3797_5dr	3797	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3798	3798	Hatchback	Punto I GT	176	3	EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	HIGH	GT三门外廓。	READY
3799_3dr	3799	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3799_5dr	3799	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3800_3dr	3800	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3800_5dr	3800	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3801_3dr	3801	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3801_5dr	3801	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3802	3802	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH	176C双门敞篷外廓。	READY
3803	3803	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH	176C双门敞篷外廓。	READY
3804	3804	Coupe	Fiat Coupé	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	Type 175双门Coupe外廓。	READY
3805	3805	Coupe	Fiat Coupé	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	Type 175双门Coupe外廓。	READY
3806_3dr	3806	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3806_5dr	3806	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3811	3811	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3812_swb	3812	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3812_lwb	3812	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3813_swb	3813	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3813_lwb	3813	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3814_swb	3814	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3814_lwb	3814	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3815_swb	3815	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3815_lwb	3815	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3819	3819	Sedan	164	164	4	EU-ALFA-ROMEO-164-164-SEDAN-Q4-01	MEDIUM	Q4专属四驱外廓。	READY
3820	3820	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3821	3821	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3822	3822	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3823	3823	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3824	3824	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3825	3825	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3826	3826	Sedan	Quattroporte V	M139	4	EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-S-01	HIGH	M139 Quattroporte S四门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	3995	1692	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2610545/peugeot_306_s16_3d.html
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	3995	1692	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/2610140/peugeot_306_s16_5d.html
EU-PEUGEOT-306-CABRIO-7D-PREFL-01	4144	1689	1356	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-cabrio-7d-1.8-101hp-5677
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-cabrio-facelift-1997-generation-6620
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Auto-Data.net	https://www.auto-data.net/en/peugeot-806-221-2.0-turbo-147hp-5479
EU-PEUGEOT-306-SEDAN-7B-PREFL-01	4232	1689	1386	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-sedan-7b-1.4-sl-75hp-5682
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-sedan-facelift-1997-generation-6619
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432	Auto-Data.net	https://www.auto-data.net/en/renault-laguna-1.8-90hp-10334
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443	Auto-Data.net	https://www.auto-data.net/en/renault-safrane-i-b54-2.1-td-b546-88hp-10742
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1755035/mini_cooper_s_convertible_john_cooper_works.html
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414	Auto-Data.net	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6-175hp-21563
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470	Auto-Data.net	https://www.auto-data.net/en/hyundai-i30-ii-1.4-100hp-18534
EU-FIAT-ULYSSE-I-220-MPV-01	4454	1834	1714	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-i-22-220-2.0-turbo-220.ad5-147hp-7160
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-60-1.2-58hp-6998
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-60-1.2-58hp-6998
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-gt-1.4-turbo-133hp-6993
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-cabrio-176c-1.6-88hp-6992
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340	Auto-Data.net	https://www.auto-data.net/en/fiat-coupe-fa-175-2.0-16v-139hp-7276
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-compact-e36-318ti-140hp-10024
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435	Auto-Data.net	https://www.auto-data.net/de/bmw-7-series-e38-730i-218hp-9734
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-long-e38-730il-218hp-9735
EU-ALFA-ROMEO-164-164-SEDAN-Q4-01	4665	1760	1356	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/217820/alfa_romeo_164_q4_cat.html
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-145-930-1.7-i.e.-16v-129hp-1236
EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-S-01	5097	1885	1438	Auto-Data.net	https://www.auto-data.net/en/maserati-quattroporte-s-4.7-430hp-17482
```

## 下一步优先处理

1. 集中处理剩余 11 个 Peugeot Boxer I、Fiat Ducato II Typ 230 Bus/Panorama/Combinato Ktype。
2. 先闭合该平台的 SWB/MWB/LWB 与低顶/高顶物理分支，再批量建立 Ktype 关联；现有资料确认该代同时存在多个轴距和车顶组合，不能将全部 Bus/Combinato 强行映射到单一尺寸。([Transit Center Ford Transit Spare Parts][3])

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/2610140/peugeot_306_s16_5d.html?utm_source=chatgpt.com "1995 Peugeot 306 S16 5d Specs Review (112 kW ..."
[2]: https://www.auto-data.net/en/peugeot-306-sedan-7b-1.4-sl-75hp-5682 "Peugeot 306 Sedan (7B) 1.4 SL (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.transitcenter.uk/peugeot-boxer-1-data-specification.php?srsltid=AfmBOoo5Jqp1G8XUm5NEY3O3c5IxVudZS9Ijf3WqyurlKNEW0zMSXTEn "https://www.transitcenter.uk/peugeot-boxer-1-data-specification.php?srsltid=AfmBOoo5Jqp1G8XUm5NEY3O3c5IxVudZS9Ijf3WqyurlKNEW0zMSXTEn"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 6 个 Ktype：`3733`、`3734`、`3735`、`3777`、`3778`、`3779`，新增 10 条 READY 映射。
* Peugeot Boxer 2.0 Bus 已确认短轴与中轴两种外廓；2.5 D Bus 已确认短轴、中轴和中轴高顶三种外廓；1.9 TD 66 kW 则命中独立的 `4665×1998×2130 mm` 分支。([引擎细节][1])
* Fiat Ducato 2.0 80 kW 已确认标准短轴和长轴高顶两种外廓；2.5 TDI 80/85 kW 对应标准短轴外廓。([Driveto][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：136
* PENDING Ktype：5
* 已确认尺寸组：62
* 本轮首次创建尺寸组：8
* 剩余 PENDING：`3736`、`3737`、`3776`、`3781`、`3782`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3733_swb	3733	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	短轴标准顶Bus外廓。	READY
3733_mwb	3733	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	中轴标准顶Bus外廓。	READY
3734_swb	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	短轴低顶Bus外廓。	READY
3734_mwb	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	MEDIUM	中轴低顶Bus外廓。	READY
3734_mwb_highroof	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶Bus外廓。	READY
3735	3735	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	HIGH	短轴1.9 TD乘用Bus外廓。	READY
3777	3777	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	短轴标准乘用Bus外廓。	READY
3778_swb	3778	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	短轴标准乘用Bus外廓。	READY
3778_mwb_highroof	3778	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用Bus外廓。	READY
3779	3779	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	短轴标准乘用Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150	Engine in Detail Peugeot Boxer 310 C 2.0 Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-310-c-2-0-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150	Engine in Detail Peugeot Boxer 320 M 2.0 Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-m-2-0-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	Engine in Detail Peugeot Boxer 310 C 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-310-c-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130	Engine in Detail Peugeot Boxer 320 M 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-m-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475	Engine in Detail Peugeot Boxer 320 MH 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-mh-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130	Engine in Detail Peugeot Boxer 270 C 1.9 DT Luxus	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-270-c-1-9-dt-luxus-1999
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150	Driveto Fiat Ducato 230 Kombi Seriova	https://www.driveto.cz/products/fiat-ducato-ducato-230-kombi-1994-1998-9533-2-0-80-kw-benzinovy-predni-manualni
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465	Driveto Fiat Ducato 230 Kombi zvysena verze long	https://www.driveto.cz/products/fiat-ducato-ducato-230-kombi-1994-1998-9534-2-0-80-kw-benzinovy-predni-manualni
```

## 下一步优先处理

1. 核对 `3736` 的早期 1.9 TD 68 kW Bus 是否与后期 66 kW 的 `4665 mm` 外廓共用，或存在独立短轴尺寸。
2. 核对 `3737` 的 1994–1997 年 2.5 TD 76 kW 早期 Bus 分支。
3. 批量闭合 Fiat `3776`、`3781`、`3782` 的 Panorama/Combinato 早期发动机版本，重点确认是否只包含短轴标准车身。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-270-c-1-9-dt-luxus-1999?utm_source=chatgpt.com "Peugeot Boxer Estate (Wagon) 270 C 1.9 DT Luxus 1999 - Specs, Review & Tests"
[2]: https://www.driveto.cz/products/fiat-ducato-ducato-230-kombi-1994-1998-9534-2-0-80-kw-benzinovy-predni-manualni?srsltid=AfmBOoqh0auVwvYjg45VGQBHVUeX1KUrGhiNodGsLR4OqfnNCQYRVuMm "Fiat - Ducato - zvýšená verze long | Driveto.cz"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 最后 5 个 PENDING Ktype 已闭合：`3736` 复用 Boxer 1.9 TD 短轴组；`3737` 拆分 310C 短轴与 320M 中轴；`3776`、`3781`、`3782` 复用 Ducato Typ 230 短轴标准 Bus 组。本轮未新建或修改尺寸组。([Peugeot Boxer Engines][1])
* 已完成机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源无空值、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* 最终映射行：142
* PENDING：0
* 最终 DIMENSION_GROUP：62
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3726	3726	Coupe	3 Series E36	E36	2	EU-BMW-3-SERIES-E36-COUPE-01	HIGH	E36双门Coupe。	READY
3727	3727	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH	E34五门Touring。	READY
3728	3728	Convertible	3 Series E36	E36	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH	E36双门Cabriolet。	READY
3729_3dr	3729	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3729_5dr	3729	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3730_3dr	3730	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	MEDIUM	输入Ktype覆盖3/5门S16分支。	READY
3730_5dr	3730	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门S16分支。	READY
3731_prefl	3731	Convertible	306 Cabrio Phase I	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3731_facelift	3731	Convertible	306 Cabrio Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3732_prefl	3732	Convertible	306 Cabrio Phase I	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3732_facelift	3732	Convertible	306 Cabrio Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3733_swb	3733	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	MEDIUM	短轴标准顶Bus外廓。	READY
3733_mwb	3733	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	中轴标准顶Bus外廓。	READY
3734_swb	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	短轴低顶Bus外廓。	READY
3734_mwb	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	MEDIUM	中轴低顶Bus外廓。	READY
3734_mwb_highroof	3734	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶Bus外廓。	READY
3735	3735	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	HIGH	短轴1.9 TD乘用Bus外廓。	READY
3736	3736	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	MEDIUM	短轴1.9 TD乘用Bus外廓。	READY
3737_swb	3737	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	MEDIUM	310C短轴乘用Bus外廓。	READY
3737_mwb	3737	MPV	Boxer I Typ 230	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	MEDIUM	320M中轴乘用Bus外廓。	READY
3738_3dr	3738	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3738_5dr	3738	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3739	3739	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221五门MPV外廓。	READY
3740	3740	MPV	806 I	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH	221五门MPV外廓。	READY
3741_3dr_prefl	3741	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_5dr_prefl	3741	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_3dr_facelift	3741	Hatchback	306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3741_5dr_facelift	3741	Hatchback	306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	MEDIUM	生产期跨改款且覆盖3/5门分支。	READY
3742_prefl	3742	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3742_facelift	3742	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3743_prefl	3743	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3743_facelift	3743	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3744_prefl	3744	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3744_facelift	3744	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3745_prefl	3745	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3745_facelift	3745	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3746_prefl	3746	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3746_facelift	3746	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3747_prefl	3747	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3747_facelift	3747	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3748_prefl	3748	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3748_facelift	3748	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3749_prefl	3749	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3749_facelift	3749	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3750_prefl	3750	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3750_facelift	3750	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3751_prefl	3751	Sedan	306 Sedan Phase I	7B	4	EU-PEUGEOT-306-SEDAN-7B-PREFL-01	MEDIUM	生产期跨1997年改款边界。	READY
3751_facelift	3751	Sedan	306 Sedan Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	MEDIUM	生产期跨1997年改款边界。	READY
3752	3752	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH	405 II标准四门轿车。	READY
3753	3753	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-MI16-01	HIGH	2.0 16V对应Mi16外廓。	READY
3754	3754	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH	405 II Break五门旅行车。	READY
3755_prefl	3755	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-STANDARD-01	MEDIUM	生产期跨605改款边界。	READY
3755_facelift	3755	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	MEDIUM	生产期跨605改款边界。	READY
3756	3756	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	改款期标准四门轿车。	READY
3757	3757	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	改款期标准四门轿车。	READY
3758_3dr	3758	Hatchback	19 II	C53	3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3758_5dr	3758	Hatchback	19 II	B53	5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3759	3759	Sedan	19 II Chamade	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53四门Chamade。	READY
3760_3dr	3760	Hatchback	19 II	C53	3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3760_5dr	3760	Hatchback	19 II	B53	5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	输入Ktype覆盖3/5门分支，外廓尺寸组共用。	READY
3761	3761	Sedan	19 II Chamade	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53四门Chamade。	READY
3762	3762	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3763	3763	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3764	3764	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3765	3765	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56五门掀背外廓。	READY
3766	3766	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	HIGH	B54标准五门掀背外廓。	READY
3767_3dr	3767	Hatchback	Clio I Phase I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3767_5dr	3767	Hatchback	Clio I Phase I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3768_3dr	3768	Hatchback	Clio I Phase I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3768_5dr	3768	Hatchback	Clio I Phase I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	资料列明3/5门，外廓尺寸组共用。	READY
3769	3769	MPV	Trafic I Phase II			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	累计组限定SWB低顶Bus外廓。	READY
3770	3770	MPV	Trafic I Phase II			EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	MEDIUM	累计组限定SWB低顶Bus外廓。	READY
3771	3771	Van	Rapid Phase II/III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Kasten/乘用厢式共用该外廓。	READY
3772	3772	Van	Rapid Phase II/III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Kasten/乘用厢式共用该外廓。	READY
3773	3773	MPV	Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63五门MPV。	READY
3775	3775	Convertible	MINI R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	R57改款期双门敞篷外廓。	READY
3776	3776	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	Panorama短轴标准乘用Bus外廓。	READY
3777	3777	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	短轴标准乘用Bus外廓。	READY
3778_swb	3778	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	短轴标准乘用Bus外廓。	READY
3778_mwb_highroof	3778	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	MEDIUM	中轴高顶乘用Bus外廓。	READY
3779	3779	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	短轴标准乘用Bus外廓。	READY
3780	3780	Hatchback	Cinquecento	170	3	EU-FIAT-CINQUECENTO-HATCHBACK-01	HIGH	Type 170三门Hatchback。	READY
3781	3781	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	Combinato短轴标准乘用Bus外廓。	READY
3782	3782	MPV	Ducato II Typ 230	230P	4	EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	Combinato短轴标准乘用Bus外廓。	READY
3783_prefl	3783	Convertible	MINI R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	MEDIUM	生产期跨2010年改款边界。	READY
3783_facelift	3783	Convertible	MINI R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	MEDIUM	生产期跨2010年改款边界。	READY
3784	3784	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD五门掀背外廓。	READY
3785	3785	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH	220五门MPV外廓。	READY
3786	3786	MPV	Ulysse I	220	5	EU-FIAT-ULYSSE-I-220-MPV-01	HIGH	220五门MPV外廓。	READY
3787	3787	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3788	3788	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3789	3789	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3790	3790	Sedan	Tempra	159	4	EU-FIAT-TEMPRA-SEDAN-01	HIGH	Type 159四门Sedan。	READY
3791	3791	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3792	3792	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3793	3793	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3794	3794	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-WAGON-FWD-01	HIGH	Type 159五门FWD Wagon。	READY
3795_3dr	3795	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3795_5dr	3795	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3796_3dr	3796	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3796_5dr	3796	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3797_3dr	3797	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3797_5dr	3797	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3798	3798	Hatchback	Punto I GT	176	3	EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	HIGH	GT三门外廓。	READY
3799_3dr	3799	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3799_5dr	3799	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3800_3dr	3800	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3800_5dr	3800	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3801_3dr	3801	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3801_5dr	3801	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3802	3802	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH	176C双门敞篷外廓。	READY
3803	3803	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH	176C双门敞篷外廓。	READY
3804	3804	Coupe	Fiat Coupé	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	Type 175双门Coupe外廓。	READY
3805	3805	Coupe	Fiat Coupé	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	Type 175双门Coupe外廓。	READY
3806_3dr	3806	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3806_5dr	3806	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖3/5门分支。	READY
3807	3807	Hatchback	Cinquecento	170	3	EU-FIAT-CINQUECENTO-HATCHBACK-01	HIGH	Sporting不改变Type 170外廓。	READY
3808_3dr	3808	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	MEDIUM	101 hp版本按1445 mm车高分支，门数需拆分。	READY
3808_5dr	3808	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	101 hp版本按1445 mm车高分支，门数需拆分。	READY
3809_3dr	3809	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	90 hp版本按1450 mm车高分支，门数需拆分。	READY
3809_5dr	3809	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	90 hp版本按1450 mm车高分支，门数需拆分。	READY
3810	3810	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Type 146厢式车外廓。	READY
3811	3811	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3812_swb	3812	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3812_lwb	3812	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3813_swb	3813	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3813_lwb	3813	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3814_swb	3814	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3814_lwb	3814	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3815_swb	3815	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3815_lwb	3815	Sedan	7 Series E38 Long	E38	4	EU-BMW-7-E38-SEDAN-LWB-01	MEDIUM	输入版本同时覆盖i与iL轴距分支。	READY
3816	3816	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850-01	HIGH	E31双门850Ci。	READY
3817	3817	Wagon	5 Series E34	E34	5	EU-BMW-5-E34-WAGON-01	HIGH	CNG动力不改变E34 Touring外廓。	READY
3818	3818	Sedan	3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH	E36四门Sedan。	READY
3819	3819	Sedan	164	164	4	EU-ALFA-ROMEO-164-164-SEDAN-Q4-01	MEDIUM	Q4专属四驱外廓。	READY
3820	3820	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3821	3821	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3822	3822	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3823	3823	Hatchback	145	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门掀背外廓。	READY
3824	3824	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3825	3825	Hatchback	3 Series E36 Compact	E36	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH	E36 Compact三门外廓。	READY
3826	3826	Sedan	Quattroporte V	M139	4	EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-S-01	HIGH	M139 Quattroporte S四门外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3601-3700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e36-generation-2043
EU-BMW-5-E34-WAGON-01	4720	1751	1417	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-touring-e34-540i-286hp-9664
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/271040/bmw_318i_convertible.html
EU-PEUGEOT-106-I-HATCHBACK-3D-01	3564	1590	1369	Auto-Data.net	https://www.auto-data.net/en/peugeot-106-i-1a-c-generation-1244
EU-PEUGEOT-106-I-HATCHBACK-5D-01	3564	1590	1369	Auto-Data.net	https://www.auto-data.net/en/peugeot-106-i-1a-c-generation-1244
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	3995	1692	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/2610545/peugeot_306_s16_3d.html
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	3995	1692	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/2610140/peugeot_306_s16_5d.html
EU-PEUGEOT-306-CABRIO-7D-PREFL-01	4144	1689	1356	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-cabrio-7d-1.8-101hp-5677
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-cabrio-facelift-1997-generation-6620
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150	Engine in Detail Peugeot Boxer 310 C 2.0 Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-310-c-2-0-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150	Engine in Detail Peugeot Boxer 320 M 2.0 Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-m-2-0-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	Engine in Detail Peugeot Boxer 310 C 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-310-c-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130	Engine in Detail Peugeot Boxer 320 M 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-m-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475	Engine in Detail Peugeot Boxer 320 MH 2.5 D Standard	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-320-mh-2-5-d-standard-1999
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130	Engine in Detail Peugeot Boxer 270 C 1.9 DT Luxus	https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-270-c-1-9-dt-luxus-1999
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Auto-Data.net	https://www.auto-data.net/en/peugeot-806-221-2.0-turbo-147hp-5479
EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	3995	1692	1380	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-1.9-d-68hp-5713
EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	3995	1692	1380	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-1.9-d-68hp-5713
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PEUGEOT-306-SEDAN-7B-PREFL-01	4232	1689	1386	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-sedan-7b-1.4-sl-75hp-5682
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386	Auto-Data.net	https://www.auto-data.net/en/peugeot-306-sedan-facelift-1997-generation-6619
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406	Auto-Data.net	https://www.auto-data.net/en/peugeot-405-i-15b-facelift-1992-1.9-d-68hp-5569
EU-PEUGEOT-405-II-SEDAN-MI16-01	4408	1716	1406	Auto-Data.net	https://www.auto-data.net/en/peugeot-405-i-15b-facelift-1992-2.0-mi-16-150hp-5573
EU-PEUGEOT-405-II-BREAK-01	4398	1704	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585510/peugeot_405_break_grd.html
EU-PEUGEOT-605-I-SEDAN-STANDARD-01	4723	1799	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2587475/peugeot_605_sri.html
EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	4765	1799	1417	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/2588135/peugeot_605_executive_2_0i_16_automatic.html
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417	Auto-Data.net	https://www.auto-data.net/en/renault-19-b-c53-facelift-1992-generation-2186
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417	Auto-Data.net	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-generation-2188
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432	Auto-Data.net	https://www.auto-data.net/en/renault-laguna-1.8-90hp-10334
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443	Auto-Data.net	https://www.auto-data.net/en/renault-safrane-i-b54-2.1-td-b546-88hp-10742
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Auto-Data.net	https://www.auto-data.net/en/renault-clio-model-1020
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037	Auto.ru	https://auto.ru/catalog/cars/renault/trafic/22956767/22957019/specifications/
EU-RENAULT-RAPID-PHASE23-VAN-01	4056	1566	1776	Renault Rapid technical data	https://de.wikipedia.org/wiki/Renault_Rapid
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2944910/renault_espace_2_0i.html
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1755035/mini_cooper_s_convertible_john_cooper_works.html
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150	Driveto Fiat Ducato 230 Kombi Seriova	https://www.driveto.cz/products/fiat-ducato-ducato-230-kombi-1994-1998-9533-2-0-80-kw-benzinovy-predni-manualni
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465	Driveto Fiat Ducato 230 Kombi zvysena verze long	https://www.driveto.cz/products/fiat-ducato-ducato-230-kombi-1994-1998-9534-2-0-80-kw-benzinovy-predni-manualni
EU-FIAT-CINQUECENTO-HATCHBACK-01	3227	1487	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-cinquecento-generation-1625
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414	Auto-Data.net	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6-175hp-21563
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470	Auto-Data.net	https://www.auto-data.net/en/hyundai-i30-ii-1.4-100hp-18534
EU-FIAT-ULYSSE-I-220-MPV-01	4454	1834	1714	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-i-22-220-2.0-turbo-220.ad5-147hp-7160
EU-FIAT-TEMPRA-SEDAN-01	4354	1695	1445	Auto-Data.net	https://www.auto-data.net/en/fiat-tempra-159-generation-1598
EU-FIAT-TEMPRA-WAGON-FWD-01	4472	1695	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/719810/fiat_tempra_s_w__1_8_i_e__sx.html
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-60-1.2-58hp-6998
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-60-1.2-58hp-6998
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-i-176-gt-1.4-turbo-133hp-6993
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447	Auto-Data.net	https://www.auto-data.net/en/fiat-punto-cabrio-176c-1.6-88hp-6992
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340	Auto-Data.net	https://www.auto-data.net/en/fiat-coupe-fa-175-2.0-16v-139hp-7276
EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	3958	1700	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/718745/fiat_tipo_1_8_i_e__gt.html
EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	3958	1700	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/718745/fiat_tipo_1_8_i_e__gt.html
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450	Auto-Data.net	https://www.auto-data.net/en/fiat-tipo-160-1.8-i.e.-90hp-7079
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450	Auto-Data.net	https://www.auto-data.net/en/fiat-tipo-160-1.8-i.e.-90hp-7079
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904	Auto-Data.net	https://www.auto-data.net/en/fiat-fiorino-147-1.6-ie-75hp-6960
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-compact-e36-318ti-140hp-10024
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435	Auto-Data.net	https://www.auto-data.net/de/bmw-7-series-e38-730i-218hp-9734
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-long-e38-730il-218hp-9735
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/269270/bmw_850_ci_automatic.html
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-sedan-e36-318tds-90hp-10038
EU-ALFA-ROMEO-164-164-SEDAN-Q4-01	4665	1760	1356	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/217820/alfa_romeo_164_q4_cat.html
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-145-930-1.7-i.e.-16v-129hp-1236
EU-MASERATI-QUATTROPORTE-V-M139-SEDAN-S-01	5097	1885	1438	Auto-Data.net	https://www.auto-data.net/en/maserati-quattroporte-s-4.7-430hp-17482
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3601-3700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.peugeotboxerengines.co.uk/peugeot-boxer-1.9-engines/amp?utm_source=chatgpt.com "Peugeot Boxer 1.9 Engines, Fully Warranted Engine Replacement, Supply & Fit"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3601-3700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3601-3700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4952 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1471 行）

