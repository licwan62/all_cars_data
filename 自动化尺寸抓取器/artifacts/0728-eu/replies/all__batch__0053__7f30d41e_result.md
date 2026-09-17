# 任务：all 第 5201-5300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0053__7f30d41e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5201-5300 行

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
all 第 5201-5300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-7-E23-SEDAN-01	4860	1800	1430
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276
EU-FORD-COURIER-I-KOMBI-01	4115	1650	1819
EU-FORD-COURIER-I-VAN-01	4115	1650	1835
EU-FORD-GALAXY-I-MPV-01	4634	1810	1730
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380
EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	4675	1780	1390
EU-HONDA-ACCORD-V-CE-WAGON-5D-01	4770	1780	1425
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	4103	1620	1394
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	4103	1620	1394
EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	4117	1620	1394
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	4750	1870	1740
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4821	1943	1760
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4821	1938	1763
EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	4500	1800	1690
EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	4489	1790	1708
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430
EU-LANCIA-DEDRA-I-SEDAN-PREFL-01	4340	1700	1430
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449
EU-LANCIA-DELTA-II-HATCHBACK-01	4011	1703	1430
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430
EU-MAZDA-626-III-GV-WAGON-5D-02	4660	1755	1440
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-HATCHBACK-5D-02	4680	1750	1400
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	4755	1795	1440
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-MITSUBISHI-ASX-I-SUV-01	4295	1770	1615
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400
EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	4239	1688	1400
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410
EU-OPEL-ASTRA-F-HATCHBACK-GSI-3D-01	4086	1688	1410
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410
EU-OPEL-ASTRA-F-WAGON-5D-01	4278	1688	1475
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	3870	1680	1395
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980
EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	3700	1590	1395
EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	3700	1590	1395
EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	3680	1525	1380
EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	3680	1525	1380
EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	3850	1525	1395
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	3720	1600	1380
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	3720	1600	1380
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Honda	Accord v	2.0 I LS	Stufenheck	Frontantrieb	Benzin	96	131	Feb 1996	Oct 1998	2024-03-01	5356
Honda	Accord v	2.2 I Vtec	Stufenheck	Frontantrieb	Benzin	110	150	Feb 1996	Oct 1998	2024-03-01	5357
Honda	Accord v	2.0 TDI	Stufenheck	Frontantrieb	Diesel	77	105	Apr 1996	Oct 1998	2024-03-01	5358
Honda	Civic vi fastback	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1995	Feb 2001	2024-03-01	5359
Jeep	Grand cherokee i	4.0 I 4X4	Geländewagen geschlossen	Allrad	Benzin	130	177	Oct 1995	Apr 1999	2024-03-01	5360
Jeep	Grand cherokee i	5.2 4X4	Geländewagen geschlossen	Allrad	Benzin	156	212	Oct 1995	Apr 1999	2024-03-01	5361
Jeep	Grand cherokee i	2.5 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	85	115	Oct 1995	Apr 1999	2024-03-01	5362
Chrysler	Stratus	2.0 LE	Stufenheck	Frontantrieb	Benzin	96	131	Dec 1995	Apr 2001	2024-03-01	5363
Chrysler	Stratus	2.5 LX V6	Stufenheck	Frontantrieb	Benzin	120	163	Dec 1995	Apr 2001	2024-03-01	5364
Hyundai	Accent i	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	73	99	Dec 1995	Jan 2000	2024-03-01	5365
Hyundai	Accent	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	73	99	Oct 1995	Jan 2000	2024-03-01	5366
Mazda	121 iii	1.3	Schrägheck	Frontantrieb	Benzin	37	50	Mar 1996	Apr 2003	2024-03-01	5367
Mazda	121 iii	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1996	Apr 2003	2024-03-01	5368
Mazda	121 iii	1.25	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1996	Apr 2003	2024-03-01	5369
Mazda	121 iii	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Mar 1996	Apr 2003	2024-03-01	5370
Mercedes-benz	E-Klasse	E 290 Turbo-d	Stufenheck	Heckantrieb	Diesel	95	129	Mar 1996	Jul 1999	2024-03-01	5371
Mercedes-benz	E-Klasse	E 280	Stufenheck	Heckantrieb	Benzin	142	193	Jan 1996	Jun 1997	2024-03-01	5372
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	85	115	Sep 2006	Nov 2013	2024-03-01	5373
Mercedes-benz	E-Klasse	E 420	Stufenheck	Heckantrieb	Benzin	205	279	Jan 1996	Jun 1997	2024-03-01	5374
Mercedes-benz	E-Klasse	E 50 AMG	Stufenheck	Heckantrieb	Benzin	255	347	Feb 1996	Aug 1997	2024-03-01	5375
Honda	Cr-V iii	2.4 I-vtec 4WD	SUV	Allrad	Benzin	122	166	Sep 2009	Dec 2012	2025-12-01	5376
Dacia	Duster	1.5 DCI	SUV	Frontantrieb	Diesel	66	90	Oct 2010	Jan 2018	2024-03-01	5377
Dacia	Duster	1.5 DCI 4X4	SUV	Allrad	Diesel	66	90	Oct 2010	Jan 2018	2024-03-01	5378
Proton	Persona 300	313i	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1996	Jan 2000	2024-03-01	5379
Proton	Persona 300	315 Gli/glsi	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1996	Jul 2000	2024-03-01	5380
Proton	Persona 300	316 Glxi	Schrägheck	Frontantrieb	Benzin	83	113	Mar 1996	Jul 2000	2024-03-01	5381
Rover	400	420 D	Schrägheck	Frontantrieb	Diesel	63	86	Nov 1995	Mar 2000	2024-03-01	5382
Rover	400	420 DI	Schrägheck	Frontantrieb	Diesel	77	105	May 1995	Mar 2000	2024-03-01	5383
Suzuki	Baleno	1.8 GTX	Schrägheck	Frontantrieb	Benzin	89	121	Mar 1996	May 2002	2024-03-01	5384
Suzuki	Baleno	1.8 GTX	Stufenheck	Frontantrieb	Benzin	89	121	Mar 1996	May 2002	2024-03-01	5385
Toyota	Hiace iv	2.4 D	Bus	Heckantrieb	Diesel	58	79	Aug 1995	Aug 2001	2024-03-01	5386
Toyota	Hiace iv	2.4 TD	Bus	Heckantrieb	Diesel	66	90	Aug 1995	Aug 2001	2024-03-01	5387
Toyota	Hiace iv	2.4	Bus	Heckantrieb	Benzin	85	115	Aug 1995	Apr 1998	2024-03-01	5388
Dacia	Duster	1.5 DCI 4X4	SUV	Allrad	Diesel	81	110	Oct 2010	Jan 2018	2024-03-01	5389
Volvo	850	2.5 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Aug 1995	Dec 1996	2024-03-01	5390
Volvo	850	2.5 TDI	Kombi	Frontantrieb	Diesel	103	140	Aug 1995	Dec 1996	2024-03-01	5392
Volvo	S40 i	1.8	Stufenheck	Frontantrieb	Benzin	85	115	Jul 1995	Aug 1999	2024-03-01	5393
Volvo	S40 i	2	Stufenheck	Frontantrieb	Benzin	100	136	Jul 1995	Dec 2003	2024-03-01	5394
Volvo	V40	1.8	Kombi	Frontantrieb	Benzin	85	115	Jul 1995	Aug 1999	2024-03-01	5395
Volvo	V40	2	Kombi	Frontantrieb	Benzin	100	136	Jul 1995	Jun 2004	2024-03-01	5396
Lancia	Y	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1996	Sep 2003	2024-03-01	5397
Lancia	Y	1.4 12V	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1996	Sep 2003	2024-03-01	5398
Toyota	Paseo	1.5	Coupe	Frontantrieb	Benzin	66	90	Aug 1995	Jun 1999	2024-03-01	5399
Toyota	Starlet	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1996	Jul 1999	2024-03-01	5400
BMW	7	725 TDS	Stufenheck	Heckantrieb	Diesel	105	143	Apr 1996	Nov 2001	2024-03-01	5403
BMW	5	540 I	Stufenheck	Heckantrieb	Benzin	210	286	Mar 1996	Jun 2003	2024-03-01	5404
Mercedes-benz	C-Klasse	C 180 T	Kombi	Heckantrieb	Benzin	90	122	Jun 1996	Sep 2000	2024-03-01	5405
Mercedes-benz	C-Klasse	C 200 T	Kombi	Heckantrieb	Benzin	100	136	Jun 1996	Mar 2001	2024-03-01	5406
Mercedes-benz	C-Klasse	C 220 T D	Kombi	Heckantrieb	Diesel	70	95	Jun 1996	Sep 1998	2024-03-01	5407
Mercedes-benz	C-Klasse	C 250 T Turbo-d	Kombi	Heckantrieb	Diesel	110	150	Jun 1996	Mar 2001	2024-03-01	5408
Audi	A8 d2	2.8	Stufenheck	Frontantrieb	Benzin	142	193	Apr 1996	Sep 2002	2024-03-01	5409
Audi	A8 d2	2.8 Quattro	Stufenheck	Allrad	Benzin	142	193	Apr 1996	Sep 2002	2024-03-01	5410
Audi	A4 b5	2.8	Stufenheck	Frontantrieb	Benzin	142	193	Oct 1996	Nov 2000	2024-03-01	5411
Audi	A4 b5 avant	2.8	Kombi	Frontantrieb	Benzin	142	193	Oct 1996	Sep 2001	2024-03-01	5412
Audi	A4 b5	2.8 Quattro	Stufenheck	Allrad	Benzin	142	193	Oct 1996	Aug 2001	2024-03-01	5413
Audi	A4 b5 avant	2.8 Quattro	Kombi	Allrad	Benzin	142	193	Oct 1996	Sep 2001	2024-03-01	5414
Chrysler	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	109	148	Apr 1996	Aug 1999	2024-03-01	5415
Ford	Courier	1.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Feb 1996	Aug 2003	2024-03-01	5416
Ford	Courier	1.8 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	44	60	Feb 1996	Apr 2002	2024-03-01	5417
Ssangyong	Musso	2.9 D	Pick-up	Heckantrieb	Diesel	88	120	Aug 2004	Sep 2007	2024-03-01	5418
Ford	Galaxy i	2.8 I V6 4X4	Großraumlimousine	Allrad	Benzin	128	174	Apr 1996	Apr 2000	2024-03-01	5419
VW	Golf vi	2.0 R 4motion	Schrägheck	Allrad	Benzin	188	256	Nov 2009	Nov 2013	2024-03-01	5420
Mercedes-benz	Sprinter 3,5-T	318 CDI	Bus	Heckantrieb	Diesel	135	184	Feb 2008	Dec 2009	2024-03-01	5421
Mitsubishi	Asx	2.0 Mivec	SUV	Frontantrieb	Benzin	110	150	Jun 2010	-	2024-03-01	5514
Mitsubishi	Asx	2.0 Mivec 4WD	SUV	Allrad	Benzin	110	150	Jun 2010	-	2024-03-01	5517
Opel	Meriva a	1.4 16V Twinport LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	66	90	Jul 2004	May 2010	2024-03-01	5519
Mercedes-benz	Sprinter 3,5-T	319 CDI / Bluetec	Bus	Heckantrieb	Diesel	140	190	Mar 2009	Dec 2018	2024-03-01	5521
Mazda	6	2.2 Mzr-cd	Kombi	Frontantrieb	Diesel	132	180	Jan 2010	Jul 2013	2024-03-01	5530
Opel	Astra f cc	1.4 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1996	Feb 1998	2024-03-01	5533
Opel	Astra f	1.4 I 16V	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1996	Sep 1998	2024-03-01	5534
Opel	Corsa b	1.7 D	Schrägheck	Frontantrieb	Diesel	44	60	Feb 1996	Sep 2000	2024-03-01	5535
Opel	Astra f caravan	1.4 I 16V	Kombi	Frontantrieb	Benzin	66	90	Feb 1996	Jan 1998	2024-03-01	5536
Opel	Astra f	1.4 I 16V	Cabriolet	Frontantrieb	Benzin	66	90	Jan 1996	Mar 2001	2024-03-01	5537
Opel	Astra f	1.6 I	Cabriolet	Frontantrieb	Benzin	55	75	Jan 1996	Mar 2001	2024-03-01	5538
Mercedes-benz	E-Klasse	E 200 T	Kombi	Heckantrieb	Benzin	100	136	Jun 1996	Aug 2000	2024-03-01	5540
Mercedes-benz	E-Klasse	E 230 T	Kombi	Heckantrieb	Benzin	110	150	Jun 1996	Jun 1997	2024-03-01	5541
Mercedes-benz	E-Klasse	E 420 T	Kombi	Heckantrieb	Benzin	205	279	Jun 1996	Jun 1997	2024-03-01	5542
Mercedes-benz	E-Klasse	E 290 T Turbo-d	Kombi	Heckantrieb	Diesel	95	129	Jun 1996	Jul 1999	2024-03-01	5543
Mercedes-benz	E-Klasse	E 250 T D	Kombi	Heckantrieb	Diesel	83	113	Jun 1996	Jul 1999	2024-03-01	5544
BMW	5	535 I	Stufenheck	Heckantrieb	Benzin	173	235	Jun 1996	Aug 1998	2024-03-01	5545
Citroën	Saxo	1.0 X	Schrägheck	Frontantrieb	Benzin	33	45	May 1996	Nov 1998	2024-03-01	5547
Citroën	Saxo	1.1 X, SX	Schrägheck	Frontantrieb	Benzin	40	54	May 1996	Sep 2003	2024-03-01	5548
Citroën	Saxo	1.4 VTS	Schrägheck	Frontantrieb	Benzin	55	75	May 1996	Jun 2003	2024-03-01	5549
Citroën	Saxo	1.6 Vtl, VTR	Schrägheck	Frontantrieb	Benzin	65	88	May 1996	Jun 2003	2024-03-01	5550
Citroën	Saxo	1.5 D	Schrägheck	Frontantrieb	Diesel	40	54	Sep 1996	Sep 2003	2024-03-01	5551
Citroën	Saxo	1.6 VTS	Schrägheck	Frontantrieb	Benzin	87	118	Jun 1996	Sep 2003	2024-03-01	5552
Citroën	Jumpy i	1.9 TD	Bus	Frontantrieb	Diesel	68	92	Apr 1996	Nov 2003	2024-03-01	5553
Citroën	Jumpy i	1.9 D	Bus	Frontantrieb	Diesel	51	69	Oct 1995	Aug 1998	2024-03-01	5554
Citroën	Jumpy i	1.6	Bus	Frontantrieb	Benzin	58	79	Oct 1995	Aug 2000	2024-03-01	5555
Citroën	Xantia	1.9 SD	Schrägheck	Frontantrieb	Diesel	55	75	Feb 1996	Apr 2003	2024-03-01	5556
Fiat	Scudo	1.9 TD	Bus	Frontantrieb	Diesel	68	92	Feb 1996	Dec 2006	2024-03-01	5557
Fiat	Scudo	1.9 D	Bus	Frontantrieb	Diesel	51	69	Feb 1996	Apr 1998	2024-03-01	5558
Fiat	Scudo	1.6	Bus	Frontantrieb	Benzin	58	79	Feb 1996	Dec 2006	2024-03-01	5559
Lancia	Delta ii	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1996	Aug 1999	2024-03-01	5560
Lancia	Delta ii	1.8 I.e. 16V	Schrägheck	Frontantrieb	Benzin	83	113	Mar 1996	Aug 1999	2024-03-01	5561
Lancia	Delta ii	1.8 I.e. 16V GT	Schrägheck	Frontantrieb	Benzin	96	131	Mar 1996	Aug 1999	2024-03-01	5562
Lancia	Dedra	1.8 16V LE	Stufenheck	Frontantrieb	Benzin	83	113	Mar 1996	Jul 1999	2024-03-01	5563
Lancia	Dedra	1.8 GT 16V	Stufenheck	Frontantrieb	Benzin	96	131	Mar 1996	Jul 1999	2024-03-01	5564
Lancia	Dedra	1.8 16V LE	Kombi	Frontantrieb	Benzin	83	113	Mar 1996	Jul 1999	2024-03-01	5565
Lancia	Dedra	1.8 GT 16V	Kombi	Frontantrieb	Benzin	96	131	Mar 1996	Jul 1999	2024-03-01	5566


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类处理 100 个输入 Ktype，共形成 114 条映射；门数、改款或车身用途不唯一的 Ktype 已拆成稳定派生 `id`。
* 本轮共引用 52 个尺寸组：复用跨批次已有组 33 个，首次创建 19 个。
* Mercedes-Benz W210 按普通汽油、E 290 柴油和 E 50 AMG 的实际高度拆组；S210 的 E 420 T 高度为 1506 mm，未与其他 1505 mm 旅行版合并。 ([汽车数据][1])
* S202 旅行版和 Audi A8 D2 已按改款前后拆分；BMW E39、Stratus、Mazda 121 III、Volvo S40/V40、Paseo、Starlet、Meriva A 等新尺寸组已经闭合。 ([汽车数据][2])
* CR-V、Duster、Musso Sports、Golf R 等存在尺寸或物理分支冲突，未创建猜测性尺寸组。Duster 资料中存在 1690/1695 mm 高度差异，Musso Sports 存在 1750/1760 mm 高度差异，Golf VI R 的三门和五门宽度也不同。 ([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：114
* READY 映射：90
* PENDING 映射：24
* 已引用尺寸组：52
* 本轮首次创建尺寸组：19
* 复用跨批次尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5356	5356	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5357	5357	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5358	5358	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5359	5359	Hatchback	Civic VI		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH		READY
5360	5360	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5361	5361	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5362	5362	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5363	5363	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
5364	5364	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
5365_3dr	5365	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5365_5dr	5365	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5366	5366	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
5367	5367	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5368	5368	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5369	5369	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5370	5370	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5371	5371	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
5372	5372	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	HIGH		READY
5373	5373	Hatchback	MINI Hatch		3		LOW	85 kW/115 hp与R56 Cooper常见功率不一致，且生产期跨改款，物理分支尚未闭合。	PENDING: 代际与改款分支未确认
5374	5374	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	HIGH		READY
5375	5375	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	HIGH		READY
5376	5376	SUV	CR-V III		5		LOW	候选为第三代后期车身；现有资料高度存在1675/1680 mm冲突。	PENDING: 高度冲突未闭合
5377	5377	SUV	Duster I		5		LOW	生产期跨Phase 1/Phase 2，且高度口径存在1690/1695 mm冲突。	PENDING: 改款分支与高度未闭合
5378	5378	SUV	Duster I		5		LOW	生产期跨Phase 1/Phase 2，且高度口径存在1690/1695 mm冲突。	PENDING: 改款分支与高度未闭合
5379	5379	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5380	5380	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5381	5381	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5382	5382	Hatchback	400 II	HHR	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5383	5383	Hatchback	400 II	HHR	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5384	5384	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	HIGH		READY
5385	5385	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
5386	5386	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5387	5387	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5388	5388	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5389	5389	SUV	Duster I		5		LOW	生产期跨Phase 1/Phase 2，且4×4高度口径尚未闭合。	PENDING: 改款分支与高度未闭合
5390	5390	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
5392	5392	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
5393	5393	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
5394	5394	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
5395	5395	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
5396	5396	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
5397	5397	Hatchback	Y	840	3		LOW	生产期跨中期更新，资料显示3723/3725 mm与1435/1440 mm两套外廓。	PENDING: 改款边界未闭合
5398	5398	Hatchback	Y	840	3		LOW	生产期跨中期更新，资料显示3723/3725 mm与1435/1440 mm两套外廓。	PENDING: 改款边界未闭合
5399	5399	Coupe	Paseo II	L5	2	EU-TOYOTA-PASEO-L5-COUPE-2D-01	HIGH		READY
5400_3dr	5400	Hatchback	Starlet V	P90	3	EU-TOYOTA-STARLET-V-P90-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5400_5dr	5400	Hatchback	Starlet V	P90	5	EU-TOYOTA-STARLET-V-P90-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5403	5403	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	HIGH		READY
5404	5404	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
5405_prefl	5405	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5405_facelift	5405	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5406_prefl	5406	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5406_facelift	5406	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5407_prefl	5407	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5407_facelift	5407	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5408_prefl	5408	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5408_facelift	5408	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5409_prefl	5409	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	生产期跨1998年改款，拆分改款前。	READY
5409_facelift	5409	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-FACELIFT-01	HIGH	生产期跨1998年改款，拆分改款后。	READY
5410_prefl	5410	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	生产期跨1998年改款，拆分改款前。	READY
5410_facelift	5410	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-FACELIFT-01	HIGH	生产期跨1998年改款，拆分改款后。	READY
5411	5411	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5412	5412	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5413	5413	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5414	5414	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5415	5415	Sedan	Neon I	PL	4		LOW	同代资料出现1712/1714 mm宽度及高度差异，尚未确认欧洲147/148 hp配置。	PENDING: 三维配置未闭合
5416_van	5416	Van	Courier I			EU-FORD-COURIER-I-VAN-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分厢式车。	READY
5416_kombi	5416	MPV	Courier I			EU-FORD-COURIER-I-KOMBI-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分乘用Kombi。	READY
5417_van	5417	Van	Courier I			EU-FORD-COURIER-I-VAN-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分厢式车。	READY
5417_kombi	5417	MPV	Courier I			EU-FORD-COURIER-I-KOMBI-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分乘用Kombi。	READY
5418	5418	Pickup	Musso Sports	P100	4		LOW	可靠资料高度存在1750/1760 mm冲突。	PENDING: 高度冲突未闭合
5419	5419	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
5420	5420	Hatchback	Golf VI	5K			LOW	Golf VI R存在3门与5门两套宽度，输入Ktype未明确门数且256 hp为特定市场功率。	PENDING: 门数与市场配置未闭合
5421	5421	MPV	Sprinter II	B906			LOW	3.5 t Bus覆盖多轴距与多车顶，输入未给出可唯一确定外廓的分支。	PENDING: 轴距和车顶分支未确认
5514	5514	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH		READY
5517	5517	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH		READY
5519_prefl	5519	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-PREFL-01	HIGH	生产期跨改款，拆分改款前。	READY
5519_facelift	5519	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后。	READY
5521	5521	MPV	Sprinter II	B906			LOW	3.5 t Bus覆盖多轴距与多车顶，输入未给出可唯一确定外廓的分支。	PENDING: 轴距和车顶分支未确认
5530	5530	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH		READY
5533_3dr	5533	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5533_5dr	5533	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5534	5534	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
5535_3dr	5535	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5535_5dr	5535	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5536	5536	Wagon	Astra F		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH		READY
5537	5537	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
5538	5538	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
5540	5540	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5541	5541	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5542	5542	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	HIGH		READY
5543	5543	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5544	5544	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5545	5545	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
5547	5547	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5548	5548	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5549	5549	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5550	5550	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5551	5551	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5552	5552	Hatchback	Saxo				LOW	生产期与版本可能覆盖3门/5门及Phase I/II，当前Ktype尚未闭合全部物理分支。	PENDING: 门数与改款分支未确认
5553	5553	MPV	Jumpy I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5554	5554	MPV	Jumpy I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5555	5555	MPV	Jumpy I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5556_x1	5556	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	生产期跨X1/X2，拆分X1。	READY
5556_x2	5556	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	生产期跨X1/X2，拆分X2。	READY
5557	5557	MPV	Scudo I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5558	5558	MPV	Scudo I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5559	5559	MPV	Scudo I				LOW	乘用Bus的长度、宽度与车顶口径尚未由同一配置来源闭合。	PENDING: 三维配置未闭合
5560	5560	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5561	5561	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5562	5562	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5563	5563	Sedan	Dedra I		4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
5564	5564	Sedan	Dedra I		4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
5565	5565	Wagon	Dedra I		5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
5566	5566	Wagon	Dedra I		5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-STRATUS-JA-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus model specification	https://www.auto-data.net/en/chrysler-stratus-model-1645
EU-MAZDA-121-III-HATCHBACK-5D-01	3828	1634	1330	Auto-Data Mazda 121 III specification	https://www.auto-data.net/en/mazda-121-model-1161
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438	Auto-Data Mercedes-Benz E-Class W210 E 290 Turbodiesel specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-290-turbodiesel-129hp-automatic-12944
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439	Auto-Data Mercedes-Benz E-Class W210 E 280 specification; Auto-Data Mercedes-Benz E-Class W210 E 420 specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-280-193hp-12957;https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-420-v8-279hp-automatic-12968
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411	Auto-Data Mercedes-Benz E-Class W210 AMG E 50 specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-amg-e-50-v8-347hp-automatic-12972
EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	3990	1698	1365	Auto-Data Proton Persona I Compact 313i specification	https://www.auto-data.net/en/proton-persona-i-compact-1.3-i-12v-313-i-75hp-8233
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Auto-Data Volvo S40 I model specification	https://www.auto-data.net/en/volvo-s40-model-941
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425	Auto-Data Volvo V40 I model specification	https://www.auto-data.net/en/volvo-v40-model-937
EU-TOYOTA-PASEO-L5-COUPE-2D-01	4160	1660	1290	Auto-Data Toyota Paseo L5 1.5 specification	https://www.auto-data.net/en/toyota-paseo-l5-1.5-16v-90hp-3188
EU-TOYOTA-STARLET-V-P90-HATCHBACK-3D-01	3740	1635	1400	Auto-Data Toyota Starlet V specification	https://www.auto-data.net/en/toyota-starlet-v-1.3i-16v-75hp-automatic-31885
EU-TOYOTA-STARLET-V-P90-HATCHBACK-5D-01	3740	1635	1400	Auto-Data Toyota Starlet V specification	https://www.auto-data.net/en/toyota-starlet-v-1.3i-16v-75hp-automatic-31885
EU-BMW-5-E39-SEDAN-01	4775	1800	1435	Auto-Data BMW 5 Series E39 540i specification; UltimateSpecs BMW E39 540i specification	https://www.auto-data.net/en/bmw-5-series-e39-540i-v8-286hp-9642;https://www.ultimatespecs.com/car-specs/BMW/180/BMW-E39-5-Series-540i.html
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 generation specification	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-generation-8522
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 facelift generation specification	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-facelift-1997-generation-2735
EU-AUDI-A8-D2-SEDAN-FACELIFT-01	5034	1880	1438	Auto-Data Audi A8 D2 facelift 2.8 specification	https://www.auto-data.net/en/audi-a8-d2-4d-facelift-1998-2.8-v6-30v-193hp-49432
EU-OPEL-MERIVA-A-MPV-PREFL-01	4042	1694	1624	Auto-Data Opel Meriva A 1.4i 16V specification	https://www.auto-data.net/en/opel-meriva-a-1.4i-16v-90hp-2516
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	UltimateSpecs Opel Meriva A 1.4 16V Twinport specification	https://www.ultimatespecs.com/car-specs/Opel/1154/Opel-Meriva-A-14-16v-Twinport-EcoFlex.html
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505	Auto-Data Mercedes-Benz E-Class T-modell S210 E 200 specification	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s210-e-200-136hp-12974
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506	Auto-Data Mercedes-Benz E-Class T-modell S210 E 420 V8 specification	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s210-e-420-v8-279hp-automatic-44086
```

## 下一步优先处理

1. 集中闭合 Saxo 的 Phase I/II 与 3门/5门分支，批量解决 Ktype 5547–5552。现有资料已经确认 Phase I 与 Phase II 外廓不同，不能作为单一尺寸组处理。 ([汽车数据][4])
2. 联合处理 Jumpy I 与 Scudo I 的乘用 Bus，共享同平台证据但分别确认同一配置的长度、无镜宽度和车顶高度。
3. 解析 Sprinter B906 3.5 t Bus 的轴距和车顶组合，处理 Ktype 5421、5521。
4. 处理 Duster I、CR-V III、Musso Sports、Neon I 的尺寸冲突。
5. 最后闭合 MINI 5373、Lancia Y 5397–5398 和 Golf R 5420 的代际、改款及门数边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-290-turbodiesel-129hp-automatic-12944?utm_source=chatgpt.com "Mercedes-Benz E-class (W210) E 290 Turbodiesel (129 ..."
[2]: https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-generation-8522?utm_source=chatgpt.com "Mercedes-Benz C-class T-modell (S202) /1995, 1996, 1997"
[3]: https://www.auto-data.net/en/renault-duster-i-1.5-dci-86hp-29557?utm_source=chatgpt.com "Renault Duster I 1.5 dCi (86 Hp) /SUV 2011 - 2015"
[4]: https://www.auto-data.net/en/citroen-saxo-model-1697?utm_source=chatgpt.com "Citroen Saxo | Technical Specs, Fuel consumption, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮将 MINI R56、Honda CR-V III、Dacia Duster I、Lancia Y 840、Chrysler Neon PL、SsangYong Musso Sports 和 Golf VI R 的映射闭合。([汽车数据][1])
* Saxo 已按 Phase I/Phase II 与三门/五门拆成四个稳定尺寸组，覆盖 Ktype 5547–5552 的全部已确认物理分支。([汽车数据][2])
* Jumpy I 乘用 Bus 与 Scudo I Combinato 已分别闭合并批量关联，不混用两者不同的车高。([汽车数据][3])
* 当前仅剩 Ktype 5421、5521 两条 Sprinter B906 记录待确认轴距与车顶分支。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：122
* PENDING 映射：2
* 已确认并被引用尺寸组：66
* 本轮首次创建尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5373	5373	Hatchback	MINI Hatch R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	MEDIUM	输入功率与目录常见120/122 hp不一致，但三门R56物理外廓明确。	READY
5376	5376	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
5377	5377	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5378	5378	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5389	5389	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5397	5397	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH		READY
5398	5398	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH		READY
5415	5415	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
5418	5418	Pickup	Musso Sports	P100	4	EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	MEDIUM	双排座皮卡外廓。	READY
5420_3dr	5420	Hatchback	Golf VI	5K	3	EU-VW-GOLF-VI-R-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分三门与五门。	READY
5420_5dr	5420	Hatchback	Golf VI	5K	5	EU-VW-GOLF-VI-R-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分三门与五门。	READY
5547	5547	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH		READY
5548_3dr_prefl	5548	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_5dr_prefl	5548	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_3dr_facelift	5548	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_5dr_facelift	5548	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5549_prefl	5549	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5549_facelift	5549	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5550_prefl	5550	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5550_facelift	5550	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5551_3dr_prefl	5551	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_5dr_prefl	5551	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_3dr_facelift	5551	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_5dr_facelift	5551	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5552_prefl	5552	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5552_facelift	5552	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5553	5553	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5554	5554	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5555	5555	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5557	5557	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
5558	5558	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
5559	5559	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	Auto-Data MINI Hatch R56 Cooper specification	https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327
EU-HONDA-CR-V-III-SUV-01	4519	1820	1679	Auto-Data Honda CR-V III 2.4 i-VTEC AWD specification	https://www.auto-data.net/en/honda-cr-v-iii-2.4-i-vtec-166hp-awd-automatic-12338
EU-DACIA-DUSTER-I-SUV-01	4315	1822	1625	Auto-Data Dacia Duster 1.5 dCi 90 4x2 specification; Auto-Data Dacia Duster 1.5 dCi 90 4x4 specification; Auto-Data Dacia Duster 1.5 dCi 110 4x4 specification	https://www.auto-data.net/en/dacia-duster-1.5-dci-90hp-fap-4x2-18001;https://www.auto-data.net/en/dacia-duster-1.5-dci-90hp-fap-4x4-18002;https://www.auto-data.net/en/dacia-duster-1.5-dci-110hp-fap-4x4-18003
EU-LANCIA-Y-840-HATCHBACK-3D-01	3725	1690	1440	Auto-Data Lancia Y 840 generation specification	https://www.auto-data.net/en/lancia-y-840-generation-1166
EU-CHRYSLER-NEON-PL-SEDAN-4D-01	4364	1714	1369	Auto-Data Chrysler Neon PL 2.0 i 16V specification	https://www.auto-data.net/en/chrysler-neon-pl-2.0-i-16v-147hp-14782
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	4935	1864	1760	CarExpert SsangYong Musso Sports specification; CarsGuide SsangYong Musso 2004 dimensions	https://www.carexpert.co.nz/kgm/musso/2004-sports-jjkmwmog20041019;https://www.carsguide.com.au/ssangyong/musso/car-dimensions/2004
EU-VW-GOLF-VI-R-HATCHBACK-3D-01	4212	1786	1469	Auto-Data Volkswagen Golf VI 3-door R 2.0 TSI 256 specification	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-r-2.0-tsi-256hp-4motion-52636
EU-VW-GOLF-VI-R-HATCHBACK-5D-01	4212	1786	1461	Auto-Data Volkswagen Golf VI 5-door R specification	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-r-2.0-tsi-270hp-4motion-dsg-41231
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	3718	1595	1390	Auto-Data Citroën Saxo Phase I 3-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-generation-3339
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Auto-Data Citroën Saxo Phase I 5-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-5-door-generation-8654
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1620	1370	Auto-Data Citroën Saxo Phase II 3-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-generation-8655
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data Citroën Saxo Phase II 5-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-5-door-generation-8656
EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	4440	1810	1927	Auto-Data Citroën Jumpy I Combi 1.9 TD 9-seat specification	https://www.auto-data.net/en/citroen-jumpy-i-combi-1.9td-92hp-9-seat-45742
EU-FIAT-SCUDO-I-COMBINATO-MPV-01	4440	1810	1940	Drive.Place Fiat Scudo I minivan specification; VinDecoderz Fiat Scudo 1996 minivan specification	https://fiat.drive.place/scudo/i/group_minivan/385660;https://www.vindecoderz.com/EN/Fiat/Scudo/1996/1.9d%20MT/specs-features/10609
```

## 下一步优先处理

1. 仅处理 Ktype 5421、5521，共享解析 Mercedes-Benz Sprinter B906 3.5-T Bus 的轴距与车顶组合。
2. 确认两条 Ktype 是否必须派生为多个 `swb/mwb/lwb` 与 `standardroof/highroof` 物理分支。
3. PENDING 清零后立即执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327?utm_source=chatgpt.com "Mini Hatch (R56) Cooper 1.6 i 16V (120 Hp) /Hatchback 2007"
[2]: https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-generation-3339?utm_source=chatgpt.com "Citroen Saxo (Phase I, 1996) 3-door"
[3]: https://www.auto-data.net/en/citroen-jumpy-i-combi-1.9td-92hp-9-seat-45742 "Citroen Jumpy I Dispatch 1.9TD (92 Hp) 9 Seat | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5201-5300_ktype_dimension_mapping_final.tsv
- all_5201-5300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已完成剩余 Sprinter B906 映射。Ktype `5421` 拆分为 5 个改款前轴距/车顶分支；Ktype `5521` 拆分为 5 个改款前分支和 5 个改款后分支。普通顶、高顶及不同轴距对应独立物理尺寸组。([YUMPU][1])
* 已完成一次机械收尾：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、尺寸及来源字段完整、下载文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：137
* PENDING 映射：0
* DIMENSION_GROUP：76
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5356	5356	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5357	5357	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5358	5358	Sedan	Accord V		4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	MEDIUM		READY
5359	5359	Hatchback	Civic VI		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH		READY
5360	5360	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5361	5361	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5362	5362	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH		READY
5363	5363	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
5364	5364	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-JA-SEDAN-01	HIGH		READY
5365_3dr	5365	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5365_5dr	5365	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5366	5366	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
5367	5367	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5368	5368	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5369	5369	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5370	5370	Hatchback	121 III		5	EU-MAZDA-121-III-HATCHBACK-5D-01	HIGH		READY
5371	5371	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
5372	5372	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	HIGH		READY
5373	5373	Hatchback	MINI Hatch R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	MEDIUM	输入功率与目录常见120/122 hp不一致，但三门R56物理外廓明确。	READY
5374	5374	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	HIGH		READY
5375	5375	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	HIGH		READY
5376	5376	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH		READY
5377	5377	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5378	5378	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5379	5379	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5380	5380	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5381	5381	Hatchback	Persona I		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	MEDIUM		READY
5382	5382	Hatchback	400 II	HHR	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5383	5383	Hatchback	400 II	HHR	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5384	5384	Hatchback	Baleno I	EG	3	EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	HIGH		READY
5385	5385	Sedan	Baleno I	EG	4	EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	HIGH		READY
5386	5386	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5387	5387	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5388	5388	MPV	Hiace IV	H100		EU-TOYOTA-HIACE-IV-H100-MPV-01	MEDIUM		READY
5389	5389	SUV	Duster I		5	EU-DACIA-DUSTER-I-SUV-01	HIGH		READY
5390	5390	Sedan	850		4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
5392	5392	Wagon	850		5	EU-VOLVO-850-WAGON-5D-01	HIGH		READY
5393	5393	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
5394	5394	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
5395	5395	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
5396	5396	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
5397	5397	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH		READY
5398	5398	Hatchback	Y	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH		READY
5399	5399	Coupe	Paseo II	L5	2	EU-TOYOTA-PASEO-L5-COUPE-2D-01	HIGH		READY
5400_3dr	5400	Hatchback	Starlet V	P90	3	EU-TOYOTA-STARLET-V-P90-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5400_5dr	5400	Hatchback	Starlet V	P90	5	EU-TOYOTA-STARLET-V-P90-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5403	5403	Sedan	7 Series E38	E38	4	EU-BMW-7-E38-SEDAN-SWB-01	HIGH		READY
5404	5404	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
5405_prefl	5405	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5405_facelift	5405	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5406_prefl	5406	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5406_facelift	5406	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5407_prefl	5407	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5407_facelift	5407	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5408_prefl	5408	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	生产期跨1997年改款，拆分改款前。	READY
5408_facelift	5408	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	生产期跨1997年改款，拆分改款后。	READY
5409_prefl	5409	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	生产期跨1998年改款，拆分改款前。	READY
5409_facelift	5409	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-FACELIFT-01	HIGH	生产期跨1998年改款，拆分改款后。	READY
5410_prefl	5410	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	生产期跨1998年改款，拆分改款前。	READY
5410_facelift	5410	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-SEDAN-FACELIFT-01	HIGH	生产期跨1998年改款，拆分改款后。	READY
5411	5411	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5412	5412	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5413	5413	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5414	5414	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5415	5415	Sedan	Neon I	PL	4	EU-CHRYSLER-NEON-PL-SEDAN-4D-01	HIGH		READY
5416_van	5416	Van	Courier I			EU-FORD-COURIER-I-VAN-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分厢式车。	READY
5416_kombi	5416	MPV	Courier I			EU-FORD-COURIER-I-KOMBI-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分乘用Kombi。	READY
5417_van	5417	Van	Courier I			EU-FORD-COURIER-I-VAN-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分厢式车。	READY
5417_kombi	5417	MPV	Courier I			EU-FORD-COURIER-I-KOMBI-01	MEDIUM	原BodyStyle同时包含Kasten与Großraumlimousine，拆分乘用Kombi。	READY
5418	5418	Pickup	Musso Sports	P100	4	EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	MEDIUM	双排座皮卡外廓。	READY
5419	5419	MPV	Galaxy I		5	EU-FORD-GALAXY-I-MPV-01	HIGH		READY
5420_3dr	5420	Hatchback	Golf VI	5K	3	EU-VW-GOLF-VI-R-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分三门与五门。	READY
5420_5dr	5420	Hatchback	Golf VI	5K	5	EU-VW-GOLF-VI-R-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分三门与五门。	READY
5421_compact_normalroof	5421	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-NORMALROOF-PREFL-01	HIGH	3.5-T Bus，紧凑轴距普通顶。	READY
5421_compact_highroof	5421	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-HIGHROOF-PREFL-01	HIGH	3.5-T Bus，紧凑轴距高顶。	READY
5421_standard_normalroof	5421	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-NORMALROOF-PREFL-01	HIGH	3.5-T Bus，标准轴距普通顶。	READY
5421_standard_highroof	5421	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-HIGHROOF-PREFL-01	HIGH	3.5-T Bus，标准轴距高顶。	READY
5421_long_highroof	5421	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-LONG-HIGHROOF-PREFL-01	HIGH	3.5-T Bus，长轴距高顶。	READY
5514	5514	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH		READY
5517	5517	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH		READY
5519_prefl	5519	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-PREFL-01	HIGH	生产期跨改款，拆分改款前。	READY
5519_facelift	5519	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	生产期跨改款，拆分改款后。	READY
5521_compact_normalroof_prefl	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-NORMALROOF-PREFL-01	HIGH	改款前3.5-T Bus，紧凑轴距普通顶。	READY
5521_compact_highroof_prefl	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-HIGHROOF-PREFL-01	HIGH	改款前3.5-T Bus，紧凑轴距高顶。	READY
5521_standard_normalroof_prefl	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-NORMALROOF-PREFL-01	HIGH	改款前3.5-T Bus，标准轴距普通顶。	READY
5521_standard_highroof_prefl	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-HIGHROOF-PREFL-01	HIGH	改款前3.5-T Bus，标准轴距高顶。	READY
5521_long_highroof_prefl	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-LONG-HIGHROOF-PREFL-01	HIGH	改款前3.5-T Bus，长轴距高顶。	READY
5521_compact_normalroof_facelift	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-NORMALROOF-FACELIFT-01	HIGH	改款后3.5-T Bus，紧凑轴距普通顶。	READY
5521_compact_highroof_facelift	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-HIGHROOF-FACELIFT-01	HIGH	改款后3.5-T Bus，紧凑轴距高顶。	READY
5521_standard_normalroof_facelift	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-NORMALROOF-FACELIFT-01	HIGH	改款后3.5-T Bus，标准轴距普通顶。	READY
5521_standard_highroof_facelift	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-HIGHROOF-FACELIFT-01	HIGH	改款后3.5-T Bus，标准轴距高顶。	READY
5521_long_highroof_facelift	5521	MPV	Sprinter II	B906		EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-LONG-HIGHROOF-FACELIFT-01	HIGH	改款后3.5-T Bus，长轴距高顶。	READY
5530	5530	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH		READY
5533_3dr	5533	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5533_5dr	5533	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5534	5534	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH		READY
5535_3dr	5535	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5535_5dr	5535	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	MEDIUM	输入Ktype未区分3门/5门。	READY
5536	5536	Wagon	Astra F		5	EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	HIGH		READY
5537	5537	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
5538	5538	Convertible	Astra F		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	HIGH		READY
5540	5540	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5541	5541	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5542	5542	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	HIGH		READY
5543	5543	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5544	5544	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
5545	5545	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
5547	5547	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH		READY
5548_3dr_prefl	5548	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_5dr_prefl	5548	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_3dr_facelift	5548	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5548_5dr_facelift	5548	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5549_prefl	5549	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5549_facelift	5549	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5550_prefl	5550	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5550_facelift	5550	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5551_3dr_prefl	5551	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_5dr_prefl	5551	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_3dr_facelift	5551	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5551_5dr_facelift	5551	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	输入Ktype覆盖门数与改款分支。	READY
5552_prefl	5552	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5552_facelift	5552	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	生产期覆盖Phase I与Phase II。	READY
5553	5553	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5554	5554	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5555	5555	MPV	Jumpy I Dispatch		5	EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5556_x1	5556	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	生产期跨X1/X2，拆分X1。	READY
5556_x2	5556	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	生产期跨X1/X2，拆分X2。	READY
5557	5557	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
5558	5558	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
5559	5559	MPV	Scudo I Combinato	222	5	EU-FIAT-SCUDO-I-COMBINATO-MPV-01	HIGH		READY
5560	5560	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5561	5561	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5562	5562	Hatchback	Delta II		5	EU-LANCIA-DELTA-II-HATCHBACK-01	HIGH		READY
5563	5563	Sedan	Dedra I		4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
5564	5564	Sedan	Dedra I		4	EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	HIGH		READY
5565	5565	Wagon	Dedra I		5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
5566	5566	Wagon	Dedra I		5	EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5201-5300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380	Auto-Data Honda Accord V CC7 facelift generation specification	https://www.auto-data.net/en/honda-accord-v-cc7-facelift-1996-generation-6863
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Auto-Data Honda Civic VI Fastback generation specification	https://www.auto-data.net/en/honda-civic-vi-fastback-generation-2628
EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	4500	1800	1690	Auto-Data Jeep Grand Cherokee I ZJ specification	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.9i-v8-241hp-4x4-automatic-1173
EU-CHRYSLER-STRATUS-JA-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus model specification	https://www.auto-data.net/en/chrysler-stratus-model-1645
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I generation specification	https://www.auto-data.net/en/hyundai-accent-hatchback-i-generation-2959
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I generation specification	https://www.auto-data.net/en/hyundai-accent-hatchback-i-generation-2959
EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	4117	1620	1394	Auto-Data Hyundai Accent model specification	https://www.auto-data.net/en/hyundai-accent-model-1472
EU-MAZDA-121-III-HATCHBACK-5D-01	3828	1634	1330	Auto-Data Mazda 121 III specification	https://www.auto-data.net/en/mazda-121-model-1161
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438	Auto-Data Mercedes-Benz E-Class W210 E 290 Turbodiesel specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-290-turbodiesel-129hp-automatic-12944
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439	Auto-Data Mercedes-Benz E-Class W210 E 280 specification; Auto-Data Mercedes-Benz E-Class W210 E 420 specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-280-193hp-12957;https://www.auto-data.net/en/mercedes-benz-e-class-w210-e-420-v8-279hp-automatic-12968
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	Auto-Data MINI Hatch R56 Cooper specification	https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411	Auto-Data Mercedes-Benz E-Class W210 AMG E 50 specification	https://www.auto-data.net/en/mercedes-benz-e-class-w210-amg-e-50-v8-347hp-automatic-12972
EU-HONDA-CR-V-III-SUV-01	4519	1820	1679	Auto-Data Honda CR-V III 2.4 i-VTEC AWD specification	https://www.auto-data.net/en/honda-cr-v-iii-2.4-i-vtec-166hp-awd-automatic-12338
EU-DACIA-DUSTER-I-SUV-01	4315	1822	1625	Auto-Data Dacia Duster 1.5 dCi 90 4x2 specification; Auto-Data Dacia Duster 1.5 dCi 90 4x4 specification; Auto-Data Dacia Duster 1.5 dCi 110 4x4 specification	https://www.auto-data.net/en/dacia-duster-1.5-dci-90hp-fap-4x2-18001;https://www.auto-data.net/en/dacia-duster-1.5-dci-90hp-fap-4x4-18002;https://www.auto-data.net/en/dacia-duster-1.5-dci-110hp-fap-4x4-18003
EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	3990	1698	1365	Auto-Data Proton Persona I Compact 313i specification	https://www.auto-data.net/en/proton-persona-i-compact-1.3-i-12v-313-i-75hp-8233
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390	Auto-Data Rover 400 RT 420 Di specification	https://www.auto-data.net/en/rover-400-rt-420-di-105hp-11620
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390	Auto-Data Suzuki Baleno Hatchback EG 1.8 GT specification	https://www.auto-data.net/en/suzuki-baleno-hatchback-eg-1995-1.8-gt-121hp-16483
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390	Auto-Data Suzuki Baleno EG 1.8 GT specification	https://www.auto-data.net/en/suzuki-baleno-eg-1995-1.8-gt-121hp-16473
EU-TOYOTA-HIACE-IV-H100-MPV-01	4615	1690	1980	Toyota HiAce H100 model reference	https://en.wikipedia.org/wiki/Toyota_HiAce
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415	Auto-Data Volvo 850 LS 2.5 TDI specification	https://www.auto-data.net/en/volvo-850-ls-2.5-tdi-140hp-9214
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Auto-Data Volvo 850 Combi LW generation specification	https://www.auto-data.net/en/volvo-850-combi-lw-generation-1927
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Auto-Data Volvo S40 I model specification	https://www.auto-data.net/en/volvo-s40-model-941
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425	Auto-Data Volvo V40 I model specification	https://www.auto-data.net/en/volvo-v40-model-937
EU-LANCIA-Y-840-HATCHBACK-3D-01	3725	1690	1440	Auto-Data Lancia Y 840 generation specification	https://www.auto-data.net/en/lancia-y-840-generation-1166
EU-TOYOTA-PASEO-L5-COUPE-2D-01	4160	1660	1290	Auto-Data Toyota Paseo L5 1.5 specification	https://www.auto-data.net/en/toyota-paseo-l5-1.5-16v-90hp-3188
EU-TOYOTA-STARLET-V-P90-HATCHBACK-3D-01	3740	1635	1400	Auto-Data Toyota Starlet V specification	https://www.auto-data.net/en/toyota-starlet-v-1.3i-16v-75hp-automatic-31885
EU-TOYOTA-STARLET-V-P90-HATCHBACK-5D-01	3740	1635	1400	Auto-Data Toyota Starlet V specification	https://www.auto-data.net/en/toyota-starlet-v-1.3i-16v-75hp-automatic-31885
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435	Auto-Data BMW 7 Series E38 725tds specification	https://www.auto-data.net/en/bmw-7-series-e38-725tds-143hp-9728
EU-BMW-5-E39-SEDAN-01	4775	1800	1435	Auto-Data BMW 5 Series E39 540i specification; UltimateSpecs BMW E39 540i specification	https://www.auto-data.net/en/bmw-5-series-e39-540i-v8-286hp-9642;https://www.ultimatespecs.com/car-specs/BMW/180/BMW-E39-5-Series-540i.html
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 generation specification	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-generation-8522
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 facelift generation specification	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-facelift-1997-generation-2735
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440	Auto-Data Audi A8 D2 2.8 V6 30V specification	https://www.auto-data.net/en/audi-a8-d2-4d-2.8-v6-30v-193hp-4836
EU-AUDI-A8-D2-SEDAN-FACELIFT-01	5034	1880	1438	Auto-Data Audi A8 D2 facelift 2.8 specification	https://www.auto-data.net/en/audi-a8-d2-4d-facelift-1998-2.8-v6-30v-193hp-49432
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415	Auto-Data Audi A4 B5 Typ 8D generation specification	https://www.auto-data.net/en/audi-a4-b5-typ-8d-generation-1088
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417	Auto-Data Audi A4 Avant B5 Typ 8D generation specification	https://www.auto-data.net/en/audi-a4-avant-b5-typ-8d-generation-1089
EU-CHRYSLER-NEON-PL-SEDAN-4D-01	4364	1714	1369	Auto-Data Chrysler Neon PL 2.0 i 16V specification	https://www.auto-data.net/en/chrysler-neon-pl-2.0-i-16v-14782
EU-FORD-COURIER-I-VAN-01	4115	1650	1835	Ford Courier van model specification	https://en.wikipedia.org/wiki/Ford_Courier
EU-FORD-COURIER-I-KOMBI-01	4115	1650	1819	Ford Courier Kombi model specification	https://en.wikipedia.org/wiki/Ford_Courier
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	4935	1864	1760	CarExpert SsangYong Musso Sports specification; CarsGuide SsangYong Musso 2004 dimensions	https://www.carexpert.co.nz/kgm/musso/2004-sports-jjkmwmog20041019;https://www.carsguide.com.au/ssangyong/musso/car-dimensions/2004
EU-FORD-GALAXY-I-MPV-01	4634	1810	1730	Auto-Data Ford Galaxy I 2.8i V6 4x4 specification	https://www.auto-data.net/en/ford-galaxy-i-2.8i-v6-4x4-174hp-7894
EU-VW-GOLF-VI-R-HATCHBACK-3D-01	4212	1786	1469	Auto-Data Volkswagen Golf VI 3-door R 2.0 TSI 256 specification	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-r-2.0-tsi-256hp-4motion-52636
EU-VW-GOLF-VI-R-HATCHBACK-5D-01	4212	1786	1461	Auto-Data Volkswagen Golf VI 5-door R specification	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-r-2.0-tsi-270hp-4motion-dsg-41231
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-NORMALROOF-PREFL-01	5245	1993	2415	Mercedes-Benz Sprinter Kombi official technical data sheet	https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-HIGHROOF-PREFL-01	5245	1993	2705	Mercedes-Benz Sprinter Kombi official technical data sheet	https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-NORMALROOF-PREFL-01	5910	1993	2435	Mercedes-Benz Sprinter Kombi official technical data sheet	https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-HIGHROOF-PREFL-01	5910	1993	2720	Mercedes-Benz Sprinter Kombi official technical data sheet	https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-LONG-HIGHROOF-PREFL-01	6945	1993	2715	Mercedes-Benz Sprinter Kombi official technical data sheet	https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-
EU-MITSUBISHI-ASX-I-SUV-01	4295	1770	1615	Auto-Data Mitsubishi ASX I model specification	https://www.auto-data.net/en/mitsubishi-asx-model-1940
EU-OPEL-MERIVA-A-MPV-PREFL-01	4042	1694	1624	Auto-Data Opel Meriva A 1.4i 16V specification	https://www.auto-data.net/en/opel-meriva-a-1.4i-16v-90hp-2516
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	UltimateSpecs Opel Meriva A 1.4 16V Twinport specification	https://www.ultimatespecs.com/car-specs/Opel/1154/Opel-Meriva-A-14-16v-Twinport-EcoFlex.html
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-NORMALROOF-FACELIFT-01	5261	1993	2357	Mercedes-Benz Sprinter Kombi official brochure 09/2015	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_kombi_201509_g.pdf
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-COMPACT-HIGHROOF-FACELIFT-01	5261	1993	2644	Mercedes-Benz Sprinter Kombi official brochure 09/2015	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_kombi_201509_g.pdf
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-NORMALROOF-FACELIFT-01	5926	1993	2457	Mercedes-Benz Sprinter Kombi official brochure 09/2015	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_kombi_201509_g.pdf
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-STANDARD-HIGHROOF-FACELIFT-01	5926	1993	2663	Mercedes-Benz Sprinter Kombi official brochure 09/2015	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_kombi_201509_g.pdf
EU-MERCEDES-BENZ-SPRINTER-II-B906-MPV-LONG-HIGHROOF-FACELIFT-01	6961	1993	2654	Mercedes-Benz Sprinter Kombi official brochure 09/2015	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_kombi_201509_g.pdf
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490	Auto-Data Mazda 6 II GH facelift wagon specification	https://www.auto-data.net/en/mazda-6-ii-combi-gh-facelift-2010-2.2-cd-180hp-16793
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410	Auto-Data Opel Astra F generation specification	https://www.auto-data.net/en/opel-astra-f-generation-559
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410	Auto-Data Opel Astra F generation specification	https://www.auto-data.net/en/opel-astra-f-generation-559
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410	Auto-Data Opel Astra F Classic facelift generation specification	https://www.auto-data.net/en/opel-astra-f-classic-facelift-1994-generation-6633
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420	Auto-Data Opel Corsa B facelift generation specification	https://www.auto-data.net/en/opel-corsa-b-facelift-1997-generation-5147
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420	Auto-Data Opel Corsa B facelift generation specification	https://www.auto-data.net/en/opel-corsa-b-facelift-1997-generation-5147
EU-OPEL-ASTRA-F-CARAVAN-FACELIFT-WAGON-01	4278	1696	1525	Auto-Data Opel Astra F Caravan facelift specification	https://www.auto-data.net/en/opel-astra-f-caravan-facelift-1994-1.7-td-68hp-2487
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400	Auto-Data Opel Astra model specification	https://www.auto-data.net/en/opel-astra-model-252
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505	Auto-Data Mercedes-Benz E-Class T-modell S210 E 200 specification	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s210-e-200-136hp-12974
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506	Auto-Data Mercedes-Benz E-Class T-modell S210 E 420 V8 specification	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s210-e-420-v8-279hp-automatic-44086
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	3718	1595	1390	Auto-Data Citroën Saxo Phase I 3-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-generation-3339
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Auto-Data Citroën Saxo Phase I 5-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-5-door-generation-8654
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1620	1370	Auto-Data Citroën Saxo Phase II 3-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-generation-8655
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data Citroën Saxo Phase II 5-door generation specification	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-5-door-generation-8656
EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	4440	1810	1927	Auto-Data Citroën Jumpy I Combi 1.9 TD 9-seat specification	https://www.auto-data.net/en/citroen-jumpy-i-combi-1.9td-92hp-9-seat-45742
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387	Auto-Data Citroën Xantia X1 specification	https://www.auto-data.net/en/citroen-xantia-x1-1.9-d-68hp-automatic-24795
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400	Auto-Data Citroën Xantia X2 specification	https://www.auto-data.net/en/citroen-xantia-x2-2.0-i-16v-132hp-14945
EU-FIAT-SCUDO-I-COMBINATO-MPV-01	4440	1810	1940	Drive.Place Fiat Scudo I minivan specification; VinDecoderz Fiat Scudo 1996 minivan specification	https://fiat.drive.place/scudo/i/group_minivan/385660;https://www.vindecoderz.com/EN/Fiat/Scudo/1996/1.9d%20MT/specs-features/10609
EU-LANCIA-DELTA-II-HATCHBACK-01	4011	1703	1430	Auto-Data Lancia Delta II 836 generation specification	https://www.auto-data.net/en/lancia-delta-ii-836-generation-1176
EU-LANCIA-DEDRA-I-SEDAN-FACELIFT-01	4343	1700	1430	Auto-Data Lancia Dedra 835 1.8 LE specification	https://www.auto-data.net/en/lancia-dedra-835-1.8-le-113hp-4996
EU-LANCIA-DEDRA-I-WAGON-FACELIFT-01	4343	1703	1449	Auto-Data Lancia Dedra Station Wagon 835 specification	https://www.auto-data.net/en/lancia-dedra-station-wagon-835-1.8-101hp-5003
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5201-5300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz- "https://www.yumpu.com/de/document/view/435572/sprinter-kombi-datenblatt-pdf-14534-kb-mercedes-benz-"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5201-5300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5201-5300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6855 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2120 行）

