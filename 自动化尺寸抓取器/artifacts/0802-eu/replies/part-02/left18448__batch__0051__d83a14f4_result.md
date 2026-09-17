# 任务：left18448 第 5001-5100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0051__d83a14f4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5001-5100 行

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
left18448.tsv

【当前独立任务】
left18448 第 5001-5100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	4390	1741	1420
EU-FIAT-MAREA-185-SEDAN-PREFL-01	4378	1741	1420
EU-FIAT-MAREA-185-WAGON-FACELIFT-01	4487	1741	1500
EU-FIAT-MAREA-185-WAGON-PREFL-01	4484	1741	1500

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Fiat	Marea	1.9 JTD 110	Kombi	Frontantrieb	Diesel	Sep 2000	Aug 2002	15827
Fiat	Marea	1.9 TD 100	Stufenheck	Frontantrieb	Diesel	May 1996	Dec 2002	5765
Fiat	Marea	1.9 TD 75	Stufenheck	Frontantrieb	Diesel	Sep 1996	May 2002	5764
Fiat	Marea	2.0 150 20V	Stufenheck	Frontantrieb	Benzin	Sep 1996	Apr 1999	5761
Fiat	Marea	2.0 150 20V	Kombi	Frontantrieb	Benzin	Sep 1996	Apr 1999	5778
Fiat	Marea	2.0 150 20V	Stufenheck	Frontantrieb	Benzin	Jan 2001	May 2002	15824
Fiat	Marea	2.0 150 20V	Kombi	Frontantrieb	Benzin	Jan 2001	May 2002	15825
Fiat	Marea	2.0 155 20V	Stufenheck	Frontantrieb	Benzin	Apr 1999	Jan 2001	12041
Fiat	Marea	2.0 155 20V	Kombi	Frontantrieb	Benzin	Apr 1999	Feb 2003	12044
Fiat	Marea	2.4 JTD 130	Stufenheck	Frontantrieb	Diesel	Apr 1999	May 2002	12040
Fiat	Marea	2.4 JTD 130	Kombi	Frontantrieb	Diesel	Apr 1999	May 2002	12043
Fiat	Marea	2.4 TD 125	Stufenheck	Frontantrieb	Diesel	Sep 1996	Apr 1999	5774
Fiat	Multipla	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Jun 2010	143084
Fiat	Multipla	1.6 100 16V	Großraumlimousine	Frontantrieb	Benzin	Apr 1999	Aug 2000	10499
Fiat	Multipla	1.6 16V Bipower	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Apr 1999	Sep 2004	11759
Fiat	Multipla	1.6 16V Bipower	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Oct 2001	Aug 2005	16589
Fiat	Multipla	1.6 16V GPL	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	Oct 2001	Jun 2010	113442
Fiat	Multipla	1.6 Blupower	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Apr 1999	Sep 2004	11159
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 2000	Mar 2002	143080
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2004	Jun 2010	143081
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 2002	Jun 2010	143082
Fiat	Multipla	1.9 JTD 105	Großraumlimousine	Frontantrieb	Diesel	Apr 1999	Aug 2000	10500
Fiat	Multipla	1.9 JTD 110	Großraumlimousine	Frontantrieb	Diesel	Mar 2001	Jul 2002	15828
Fiat	Multipla	1.9 JTD 115	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	Jun 2010	16862
Fiat	Multipla	Bipower	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	Oct 2001	Jun 2010	143083
Fiat	Palio	1.2	Kombi	Frontantrieb	Benzin	Apr 1996	Feb 2004	8781
Fiat	Palio	1.2	Kombi	Frontantrieb	Benzin	Jul 1997	Oct 2004	16092
Fiat	Palio	1.6 16V	Kombi	Frontantrieb	Benzin	Jun 1996	Feb 2001	8782
Fiat	Palio	1.6 16V	Kombi	Frontantrieb	Benzin	Feb 2001	Jan 2012	16093
Fiat	Palio	1.7 TD	Kombi	Frontantrieb	Diesel	Apr 1996	Mar 2001	8783
Fiat	Palio	1.9 D	Kombi	Frontantrieb	Diesel	Mar 2001	-	16091
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	Feb 2012	-	14015
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	Feb 2012	-	54902
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100778
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100779
Fiat	Panda	0.9	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 2012	-	111896
Fiat	Panda	0.9	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 2012	-	111897
Fiat	Panda	0.9	Kasten/Schrägheck	Frontantrieb	Benzin	Nov 2013	-	118549
Fiat	Panda	1.1	Schrägheck	Frontantrieb	Benzin	Sep 2003	-	17627
Fiat	Panda	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	Sep 2004	-	59291
Fiat	Panda	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	Sep 2010	-	12192
Fiat	Panda	1.2	Schrägheck	Frontantrieb	Benzin	Feb 2012	-	14002
Fiat	Panda	1.2	Schrägheck	Frontantrieb	Benzin	Sep 2003	-	17628
Fiat	Panda	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 2012	-	111899
Fiat	Panda	950	Schrägheck	Frontantrieb	Benzin	Sep 1982	Aug 1983	16946
Fiat	Panda	0.9 4X4	Schrägheck	Allrad	Benzin	Sep 2012	-	56748
Fiat	Panda	0.9 4X4	Schrägheck	Allrad	Benzin	Jun 2014	-	108019
Fiat	Panda	0.9 4X4	Kasten/Schrägheck	Allrad	Benzin	Sep 2012	-	111898
Fiat	Panda	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jul 2012	-	56739
Fiat	Panda	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jan 2015	-	111089
Fiat	Panda	0.9 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jan 2015	-	118547
Fiat	Panda	0.9 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jul 2012	-	118550
Fiat	Panda	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2022	-	800120
Fiat	Panda	1.2 4X4	Kasten/Schrägheck	Allrad	Benzin	Sep 2010	-	12193
Fiat	Panda	1.2 4X4	Schrägheck	Allrad	Benzin	Oct 2004	-	18093
Fiat	Panda	1.2 LPG	Kasten/Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Sep 2010	-	12204
Fiat	Panda	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2012	-	56749
Fiat	Panda	1.2 LPG	Kasten/Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Apr 2009	-	110001
Fiat	Panda	1.2 LPG	Kasten/Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2012	-	111900
Fiat	Panda	1.2 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Jan 2007	Nov 2009	109999
Fiat	Panda	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Feb 2012	-	14008
Fiat	Panda	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2003	-	17640
Fiat	Panda	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	Feb 2012	-	111901
Fiat	Panda	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Apr 2015	-	114582
Fiat	Panda	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	Dec 2015	-	118551
Fiat	Panda	1.3 D Multijet 4X4	Kasten/Schrägheck	Allrad	Diesel	Jan 2006	-	12194
Fiat	Panda	1.3 D Multijet 4X4	Schrägheck	Allrad	Diesel	Oct 2004	-	18092
Fiat	Panda	1.3 D Multijet 4X4	Schrägheck	Allrad	Diesel	Jun 2012	-	56740
Fiat	Panda	1.3 D Multijet 4X4	Schrägheck	Allrad	Diesel	Jun 2014	-	108020
Fiat	Panda	1.3 D Multijet 4X4	Kasten/Schrägheck	Allrad	Diesel	Oct 2004	Dec 2006	110002
Fiat	Panda	1.3 D Multijet 4X4	Kasten/Schrägheck	Allrad	Diesel	Jun 2012	-	111902
Fiat	Panda	1.3 D Multijet 4X4	Schrägheck	Allrad	Diesel	Apr 2015	-	114583
Fiat	Panda	1.3 D Multijet 4X4	Kasten/Schrägheck	Allrad	Diesel	Jun 2014	-	118552
Fiat	Panda	1000 I.E	Kasten/Schrägheck	Frontantrieb	Benzin	Aug 1992	Feb 2004	14143
Fiat	Panda	1300 D	Schrägheck	Frontantrieb	Diesel	Apr 1986	Dec 1992	14481
Fiat	Pandina	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2024	-	163519
Fiat	Pandina	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2026	-	163523
Fiat	Punto	0.9	Schrägheck	Frontantrieb	Benzin	Jul 2013	-	52465
Fiat	Punto	0.9	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100770
Fiat	Punto	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	Apr 1996	Feb 2000	8908
Fiat	Punto	1.2	Schrägheck	Frontantrieb	Benzin	Feb 2014	-	100883
Fiat	Punto	1.4	Schrägheck	Frontantrieb	Benzin	Sep 2003	Mar 2012	17779
Fiat	Punto	0.9 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2012	-	13959
Fiat	Punto	1.2 16V 80	Schrägheck	Frontantrieb	Benzin	Sep 1999	Apr 2006	12752
Fiat	Punto	1.2 60	Schrägheck	Frontantrieb	Benzin	Sep 1999	Dec 2010	12751
Fiat	Punto	1.2 60	Kasten/Schrägheck	Frontantrieb	Benzin	Feb 2000	Oct 2009	15891
Fiat	Punto	1.2 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Aug 2007	Mar 2012	55446
Fiat	Punto	1.2 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Sep 2003	Mar 2012	17780
Fiat	Punto	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	Apr 2008	-	7864
Fiat	Punto	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 2009	-	12203
Fiat	Punto	1.3 D Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 2009	Feb 2012	58730
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Dec 2013	-	100780
Fiat	Punto	1.3 JTD 16V	Schrägheck	Frontantrieb	Diesel	Jun 2003	Mar 2012	17392
Fiat	Punto	1.3 JTD Multijet	Schrägheck	Frontantrieb	Diesel	May 2018	-	120770
Fiat	Punto	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2012	-	55441
Fiat	Punto	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2009	Feb 2012	12208
Fiat	Punto	1.4 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Mar 2009	-	12196
Fiat	Punto	1.7 D	Kasten/Schrägheck	Frontantrieb	Diesel	Apr 1996	Feb 2000	8909
Fiat	Punto	1.7 D	Schrägheck	Frontantrieb	Diesel	Apr 1994	Sep 1997	11799
Fiat	Punto	1.7 TD	Kasten/Schrägheck	Frontantrieb	Diesel	Apr 1996	Feb 2000	8910


--- Round 1 / 首次发送 ---
更新点

* 已闭合 Fiat Marea 的 12 个输入 Ktype，共生成 13 条 READY 映射。
* `5764` 的 1.9 TD 75 覆盖 Marea Series I 与 Series II，按改款前后拆分为两条物理外廓映射。
* `5765` 的 1.9 TD 100 仅命中改款前车型，不因输入结束日期延后而错误拆分。
* Marea 确认为 Type 185；Sedan 为 4 门，Weekend/Wagon 为 5 门。1999 年 Series II 车型已有独立外廓，TD 75 同时存在于 Series I 和 Series II，而 TD 100 属于改款前版本。([维基百科][1])
* 四个 Marea 尺寸组全部复用跨批次已有组，本轮未重复抓取或新建尺寸组。

当前批次进度

* 输入 Ktype：100
* 已处理输入 Ktype：12
* READY 映射：13 行
* 未处理输入 Ktype：88
* 当前批次引用尺寸组：4 个
* 本轮新建或修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15827	15827	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	Series II Weekend五门外廓。	READY
5765	5765	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	MEDIUM	TD 100仅对应改款前四门外廓；输入结束月晚于该版本实际供应期。	READY
5764_prefl	5764	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	TD 75覆盖Series I改款前四门外廓。	READY
5764_facelift	5764	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	TD 75覆盖Series II改款后四门外廓。	READY
5761	5761	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
5778	5778	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-PREFL-01	HIGH	改款前Weekend五门外廓。	READY
15824	15824	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	Series II四门外廓。	READY
15825	15825	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	Series II Weekend五门外廓。	READY
12041	12041	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	155 20V Series II四门外廓。	READY
12044	12044	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	155 20V Series II Weekend五门外廓。	READY
12040	12040	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	JTD 130 Series II四门外廓。	READY
12043	12043	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	JTD 130 Series II Weekend五门外廓。	READY
5774	5774	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	TD 125改款前四门外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 按第一代和 2004 年改款后的外廓边界集中处理 Fiat Multipla。
2. 一次性确认 Multipla 的 MPV 与 `Kasten/Großraumlimousine` 是否共享量产外廓，避免按发动机重复建组。
3. Multipla 闭合后批量关联其 13 个 Ktype，再处理 Palio Wagon 的代际和改款边界。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Fiat_Marea?utm_source=chatgpt.com "Fiat Marea"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 已闭合 Fiat Multipla 的 13 个输入 Ktype，新增 19 条 READY 映射。
* Multipla 186 改款前和改款后分别采用 `3994×1871×1695` 与 `4089×1871×1695`；官方规格图中的宽度标注不包含车外后视镜。([汽车目录][1])
* 改款后 Bipower/Natural Power 气体燃料车型高度为 `1721 mm`，不能错误复用普通改款车型的 `1695 mm` 高度，因此独立建组。([汽车目录][2])
* `Kasten/Großraumlimousine` 记录按相同五门 Type 186 外部车身归入 MPV；发动机、燃料和商用登记本身未触发重复建组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：25
* READY 映射：32 行
* 尚未处理输入 Ktype：75
* 已确认尺寸组：7 个
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143084_prefl	143084	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143084_facelift	143084	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
10499	10499	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
11759	11759	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Bipower五门外廓。	READY
16589_prefl	16589	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Bipower五门外廓。	READY
16589_facelift	16589	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	HIGH	改款后Bipower气体燃料五门外廓。	READY
113442_prefl	113442	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前GPL五门外廓。	READY
113442_facelift	113442	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后GPL五门外廓。	READY
11159	11159	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Blupower五门外廓。	READY
143080	143080	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143081	143081	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
143082_prefl	143082	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143082_facelift	143082	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
10500	10500	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
15828	15828	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
16862_prefl	16862	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
16862_facelift	16862	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后五门MPV外廓。	READY
143083_prefl	143083	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	上游能源标记异常；改款前Bipower五门外廓。	READY
143083_facelift	143083	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	MEDIUM	上游能源标记异常；改款后Bipower气体燃料五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695	Automobile-Catalog 2003 Fiat Multipla 100 16V SX	https://www.automobile-catalog.com/car/2003/1221245/fiat_multipla_100_16v_sx.html
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4089	1871	1695	Fiat Multipla UK brochure Ed. 02/09; Automobile-Catalog 2004 Fiat Multipla 1.9 JTD 115 Dynamic	https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf;https://www.automobile-catalog.com/car/2004/723650/fiat_multipla_1_9_jtd_115_dynamic.html
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	4089	1871	1721	Automobile-Catalog 2005 Fiat Multipla 1.6 16V Natural Power CNG	https://www.automobile-catalog.com/car/2005/723680/fiat_multipla_1_6_16v_natural_power_cng.html
```

下一步优先处理

1. 集中闭合 Fiat Palio Weekend 的 Series I、改款和后期生产边界。
2. 批量关联 6 个 Palio Ktype，避免把发动机更替误当成尺寸组差异。
3. 随后按 Panda 141、169、319 三个明确代际聚类处理。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2003/1221245/fiat_multipla_100_16v_sx.html?utm_source=chatgpt.com "2003 Fiat Multipla 100 16V SX (man. 5) (model for Europe ) ..."
[2]: https://www.automobile-catalog.com/car/2005/723680/fiat_multipla_1_6_16v_natural_power_cng.html?utm_source=chatgpt.com "2005 Fiat Multipla 1.6 16V Natural Power (CNG) (man. 5)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 已闭合 Fiat Panda 319 的 8 个边界明确 Ktype：4 个普通前驱外廓、4 个标准 4x4 外廓。
* 普通前驱统一为 `3653×1643×1551 mm`；标准 4x4 统一为 `3686×1672×1605 mm`。官方技术表明确宽度分别为不含后视镜的 `1643 mm` 和 `1672 mm`。([Stellantis Media][1])
* `Kasten/Schrägheck` 行保留 `NormalizedBodyStyle=Van`，但因未改变五门量产车身外廓，直接复用对应乘用版尺寸组。
* 2014 年后 90 PS/80 PS/95 PS 的 4x4、Cross 及其他尚可能涉及保险杠和车高差异的 Ktype，本轮未提前错误归组。

当前批次进度

* 输入 Ktype：100
* 已处理输入 Ktype：33
* READY 映射：40 行
* 尚未处理输入 Ktype：67
* 已确认尺寸组：9 个
* 本轮首次创建尺寸组：2 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14002	14002	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
111899	111899	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
56748	56748	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
111898	111898	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
56749	56749	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	EasyPower普通前驱五门外廓。	READY
111900	111900	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用EasyPower普通前驱五门外廓。	READY
56740	56740	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
111902	111902	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-319-HATCHBACK-4X2-01	3653	1643	1551	Fiat Panda official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
EU-FIAT-PANDA-319-HATCHBACK-4X4-01	3686	1672	1605	Fiat Panda 4x4 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
```

下一步优先处理

1. 闭合 Panda 319 普通 TwinAir、Natural Power 与前驱 Multijet，并区分普通车身和 Trekking 外廓。
2. 单独处理 2014 年后 Panda Cross、90 PS/80 PS/95 PS 4x4 Ktype，避免复用标准 4x4 尺寸。
3. 随后批量处理 Panda 169 的普通前驱、4x4 和 Natural Power 三类外廓。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf?utm_source=chatgpt.com "Technical specifications for the Fiat Panda 4x4 and ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 已闭合 Panda 319 的普通前驱、Trekking、Natural Power、Cross 及对应商用登记外廓，本轮新增 17 个 Ktype、22 条 READY 映射。
* Trekking 与标准 4x4 的外廓均为 `3686×1672×1605 mm`，直接复用既有 `EU-FIAT-PANDA-319-HATCHBACK-4X4-01`；Natural Power 普通车身为 `3653×1643×1605 mm`，宽度均为不含后视镜口径。
* Panda Cross 独立外廓为 `3705×1662×1657 mm`，新建一个尺寸组。([Stellantis Media][1])
* `114583` 的 95 PS 四驱版本覆盖普通 4x4 与 Cross 两种不同外廓，拆成两个派生映射；未将配置差异错误合并。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：50
* READY 映射：62 行
* 尚未处理输入 Ktype：50
* 已确认尺寸组：11 个
* 本轮首次创建尺寸组：2 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14015_standard	14015	Hatchback	Panda 319	312PXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
14015_trekking	14015	Hatchback	Panda 319	312PXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱外廓。	READY
54902	54902	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
100778	100778	Hatchback	Panda 319	312PXP1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
100779	100779	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
111896	111896	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
111897	111897	Van	Panda 319	312DXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
118549	118549	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
108019	108019	Hatchback	Panda 319	312PXR2B	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Cross四驱外廓。	READY
56739_standard	56739	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	MEDIUM	Natural Power普通五门外廓。	READY
56739_trekking	56739	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Natural Power Trekking前驱外廓。	READY
111089_standard	111089	Hatchback	Panda 319	312PXN1A	5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	MEDIUM	Natural Power普通五门外廓。	READY
111089_trekking	111089	Hatchback	Panda 319	312PXN1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Natural Power Trekking前驱外廓。	READY
118547	118547	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	HIGH	商用登记，沿用Natural Power普通五门外廓。	READY
118550	118550	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	HIGH	商用登记，沿用Natural Power普通五门外廓。	READY
14008_standard	14008	Hatchback	Panda 319	312PXL1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
14008_trekking	14008	Hatchback	Panda 319	312PXL1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱外廓。	READY
111901	111901	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
108020	108020	Hatchback	Panda 319	312PXS2A	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Cross四驱外廓。	READY
114583_4x4	114583	Hatchback	Panda 319	312PXU1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	普通4x4五门外廓。	READY
114583_cross	114583	Hatchback	Panda 319	312PXU1A	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	MEDIUM	Cross四驱外廓。	READY
118552	118552	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	3705	1662	1657	Fiat UK The New Fiat Panda Cross official press pack	https://www.media.stellantis.com/uk-en/fiat/press/the-new-fiat-panda-cross-a-car-like-no-other
EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	3653	1643	1605	Fiat Panda Natural Power official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
```

下一步优先处理

1. 闭合 Panda 169 的普通前驱、标准 4x4、Natural Power 与商用登记外廓。
2. 单独确认 Panda 319 的 2015 年后普通柴油、Mild Hybrid 与可能覆盖的 City Cross 分支。
3. 随后处理 Panda 141、Pandina，再回到尚未处理的 Palio Weekend。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/fiat/press/the-new-fiat-panda-cross-a-car-like-no-other?utm_source=chatgpt.com "THE NEW FIAT PANDA CROSS - A CAR LIKE NO OTHER"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 已闭合 Panda 169 的普通前驱、LPG、Natural Power、标准 4x4 与 Cross 外廓，本轮新增 13 个 Ktype、14 条 READY 映射。
* 标准 4x4 外廓为 `3574×1605×1632 mm`，Natural Power 为 `3538×1589×1576 mm`，Cross 为 `3581×1611×1643 mm`；所用宽度均为不含后视镜口径。([汽车目录][1])
* `18092` 覆盖普通 1.3 Multijet 4x4 与 Cross 两种外廓，拆分为两个派生映射；商用登记 Ktype 仅关联标准量产外廓。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：63
* READY 映射：76 行
* 尚未处理输入 Ktype：37
* 已确认尺寸组：15 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17627	17627	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
59291	59291	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
12192	12192	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
17628	17628	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
12193	12193	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
18093	18093	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
12204	12204	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	LPG商用登记，沿用普通前驱五门外廓。	READY
110001	110001	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	LPG商用登记，沿用普通前驱五门外廓。	READY
109999	109999	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power商用登记五门外廓。	READY
17640	17640	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
12194	12194	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
18092_4x4	18092	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	标准4x4五门分支。	READY
18092_cross	18092	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-CROSS-01	HIGH	Cross五门分支。	READY
110002	110002	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-169-HATCHBACK-4X2-01	3538	1578	1540	Auto-Data Fiat Panda II 169 1.2 MPI specifications	https://www.auto-data.net/en/fiat-panda-ii-169-1.2-mpi-60hp-6903
EU-FIAT-PANDA-169-HATCHBACK-4X4-01	3574	1605	1632	Automobile-Catalog 2008 Fiat Panda Climbing 4x4 1.2	https://www.automobile-catalog.com/car/2008/726815/fiat_panda_climbing_4x4_1_2.html
EU-FIAT-PANDA-169-HATCHBACK-NATURAL-POWER-01	3538	1589	1576	Automobile-Catalog 2008 Fiat Panda 1.2 Natural Power CNG	https://www.automobile-catalog.com/car/2008/726785/fiat_panda_1_2_natural_power_cng.html
EU-FIAT-PANDA-169-HATCHBACK-CROSS-01	3581	1611	1643	Automobile-Catalog 2006 Fiat Panda Cross 4x4 1.3 Multijet 16V	https://www.automobile-catalog.com/car/2006/726860/fiat_panda_cross_4x4_1_3_multijet_16v.html
```

下一步优先处理

1. 闭合 Panda 141 的初期、1986 年改款和 1991 年改款外廓。
2. 处理 Panda 319 后期柴油、Mild Hybrid 及 Pandina，并复用已确认的普通、City Cross 或 Cross 外廓。
3. 随后集中闭合 Palio Weekend，再处理剩余 Punto Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/726815/fiat_panda_climbing_4x4_1_2.html?utm_source=chatgpt.com "2008 Fiat Panda Climbing 4x4 1.2 Specs Review (44 kW / ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 已闭合 Panda 141 的早期 950 与 1986 年改款后 1300 D；对应外廓分别为 `3380×1460×1445` 和 `3408×1494×1420`，宽度均为不含后视镜口径。([dokumen.pub][1])
* 已闭合 Panda 319 Mild Hybrid 的普通车身与 City Cross 两种外廓；该动力同时用于 Urban 与 City Cross，不能只保留其中一个分支。([Stellantis Media][2])
* 已闭合 2024 年起的 Pandina Ktype `163519`。该版本基于 Cross 车身，直接复用已确认的 Panda 319 Cross 尺寸组。([Stellantis Media][3])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：67
* READY 映射：81 行
* 待闭合输入 Ktype：33
* 已确认尺寸组：18 个
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16946	16946	Hatchback	Panda 141 Series I	141	3	EU-FIAT-PANDA-141-HATCHBACK-SERIES-I-01	HIGH	早期三门前驱外廓。	READY
14481	14481	Hatchback	Panda 141A	141A	3	EU-FIAT-PANDA-141A-HATCHBACK-4X2-01	HIGH	1986年改款后三门前驱外廓。	READY
800120_standard	800120	Hatchback	Panda 319 facelift 2020	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
800120_citycross	800120	Hatchback	Panda 319 facelift 2020	319	5	EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	HIGH	City Cross前驱五门外廓。	READY
163519	163519	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Pandina五门Cross外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-141-HATCHBACK-SERIES-I-01	3380	1460	1445	Haynes Fiat Panda Owners Workshop Manual	https://dokumen.pub/haynes-fiat-panda-owners-workshop-manual-0856967939-9780856967931.html
EU-FIAT-PANDA-141A-HATCHBACK-4X2-01	3408	1494	1420	Automobile-Catalog 1986 Fiat Panda D	https://www.automobile-catalog.com/car/1986/58535/fiat_panda_d.html
EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	3705	1662	1635	Auto-Data Fiat Panda III City Cross 1.0 Mild Hybrid	https://www.auto-data.net/en/fiat-panda-iii-city-cross-1.0-70hp-mild-hybrid-39071
```

下一步优先处理

1. 单独闭合带尾部钢制加长结构的 Panda 141 Van `14143`，不得复用普通三门车身尺寸。
2. 解决 Pandina `163523` 的 POP/ICON 与 CROSS 外廓分支及官方长度口径冲突。
3. 随后集中处理 Palio Weekend 的改款边界，再推进剩余 Punto Ktype。

推进信号：CONTINUE

[1]: https://dokumen.pub/haynes-fiat-panda-owners-workshop-manual-0856967939-9780856967931.html?utm_source=chatgpt.com "Haynes Fiat Panda Owners Workshop Manual"
[2]: https://www.media.stellantis.com/em-en/fiat/press/fiat-panda-hybrid-the-most-democratic-mild-hybrid-on-the-market?utm_source=chatgpt.com "Fiat Panda Hybrid, the most democratic Mild ..."
[3]: https://www.media.stellantis.com/em-en/fiat/press/orders-open-for-the-most-technological-fiat-panda-ever?utm_source=chatgpt.com "Orders open for the most technological Fiat Panda ever"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Panda 319 后期柴油 Ktype `114582`、商用登记 Ktype `118551`，以及 MY2026 Pandina Ktype `163523`。
* `114582` 按普通车身、Trekking 和 City Cross 三种前驱外廓拆分；官方资料确认 1.3 MultiJet 95 HP 存在 Trekking 前驱版及 City Cross 前驱版。
* `163523` 按 POP/ICON 普通外廓与 CROSS 外廓拆分；MY2026 官方阵容明确包含 POP、ICON、CROSS 三种配置。([菲亚特][1])
* 本轮全部复用既有 Panda 319 尺寸组，未新建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：70
* PENDING 输入 Ktype：30
* READY 映射：87 行
* 已确认尺寸组：18 个
* 本轮新增尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
114582_standard	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
114582_trekking	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱五门外廓。	READY
114582_citycross	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	MEDIUM	City Cross前驱五门外廓。	READY
118551	118551	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
163523_standard	163523	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	POP与ICON普通五门外廓。	READY
163523_cross	163523	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	CROSS五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Panda 141 Van `14143` 的独立商用外廓。
2. 集中处理 6 个 Palio Weekend Ktype 的初期与改款后物理边界。
3. 随后按 Punto 176、188、199 三个代际批量消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.fiat.com/news/fiat-panda-family "FIAT Panda MY26: Nuova Gamma Grande Panda e Pandina | News & Updates"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
更新点

* 已闭合 4 个 Fiat Palio Weekend Ktype，新增 6 条 READY 映射。
* Palio Weekend Series I 外廓确认为 `4130×1614×1515 mm`，Series II 外廓确认为 `4142×1627×1488 mm`；两组宽度均为明确不含后视镜口径。([汽车目录][1])
* `8781`、`16092` 的生产区间覆盖两套不同外廓，拆分为 Series I 与 Series II 派生行。
* `8782`、`8783` 在 Series II 外廓启用前结束，仅关联 Series I 尺寸组。
* `16093`、`16091` 的较长生产区间还覆盖后续改款，本轮未强行套用两组已确认尺寸。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* PENDING 输入 Ktype：26
* READY 映射：93 行
* 已确认尺寸组：20 个
* 本轮首次创建尺寸组：2 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8781_prefl	8781	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	MEDIUM	Series I五门旅行车外廓。	READY
8781_facelift	8781	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
16092_prefl	16092	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	MEDIUM	Series I五门旅行车外廓。	READY
16092_facelift	16092	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
8782	8782	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	HIGH	Series I五门旅行车外廓。	READY
8783	8783	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	HIGH	Series I五门旅行车外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PALIO-178-WAGON-PREFL-01	4130	1614	1515	Automobile-Catalog 2000 Fiat Palio Weekend 75 EL	https://www.automobile-catalog.com/car/2000/723170/fiat_palio_weekend_75_el.html
EU-FIAT-PALIO-178-WAGON-FACELIFT-01	4142	1627	1488	Automobile-Catalog 2003 Fiat Palio Weekend 1.6 16V Active	https://www.automobile-catalog.com/car/2003/723305/fiat_palio_weekend_1_6_16v_active.html
```

下一步优先处理

1. 闭合 Palio `16093`、`16091` 覆盖的 2001、2004 及后续改款外廓。
2. 解决 Panda 141 Van `14143` 的尾部钢制扩展长度和宽度来源冲突。
3. 按 Punto 176、188、199 三个代际聚类处理剩余 Punto Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/723170/fiat_palio_weekend_75_el.html?utm_source=chatgpt.com "2000 Fiat Palio Weekend 75 EL Specs Review ..."


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 9 个 Punto Ktype，新增 15 条 READY 映射。
* Punto 199（2012 版）普通 TwinAir、1.2、Multijet 与 EasyPower 外廓均为 `4065×1687×1490 mm`；官方规格同时列出三门和五门整备质量，因此分别建立稳定的三门、五门物理尺寸组。
* Punto 176 官方历史资料确认提供三门和五门车身，外廓为 `3760×1620×1450 mm`；两种车门结构分别建组，但三维一致。([Stellantis Media][1])
* 三个 Punto 176 商用登记 Ktype 采用三门钢板侧窗车身，复用三门外廓尺寸组，不因载货舱内饰或发动机差异重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：83
* PENDING 输入 Ktype：17
* READY 映射：108 行
* 已确认尺寸组：24 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
52465_3dr	52465	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
52465_5dr	52465	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
100770_3dr	100770	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100770_5dr	100770	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
8908	8908	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
100883_3dr	100883	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100883_5dr	100883	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
100780_3dr	100780	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100780_5dr	100780	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
55441_3dr	55441	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	EasyPower三门外廓。	READY
55441_5dr	55441	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	EasyPower五门外廓。	READY
8909	8909	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
11799_3dr	11799	Hatchback	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	MEDIUM	第一代三门柴油外廓。	READY
11799_5dr	11799	Hatchback	Punto 176	176	5	EU-FIAT-PUNTO-176-HATCHBACK-5D-01	MEDIUM	第一代五门柴油外廓。	READY
8910	8910	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	4065	1687	1490	Fiat Punto 2012 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/SCHEDE_TECNICHE/120207_F_Punto2012_ST_ALL_GBR.PDF
EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	4065	1687	1490	Fiat Punto 2012 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/SCHEDE_TECNICHE/120207_F_Punto2012_ST_ALL_GBR.PDF
EU-FIAT-PUNTO-176-HATCHBACK-3D-01	3760	1620	1450	Stellantis Heritage 30th anniversary of Fiat Punto	https://www.media.stellantis.com/em-en/heritage-hub-italy/press/heritage-celebrates-the-30th-anniversary-of-the-legendary-fiat-punto
EU-FIAT-PUNTO-176-HATCHBACK-5D-01	3760	1620	1450	Stellantis Heritage 30th anniversary of Fiat Punto	https://www.media.stellantis.com/em-en/heritage-hub-italy/press/heritage-celebrates-the-30th-anniversary-of-the-legendary-fiat-punto
```

## 下一步优先处理

1. 闭合 Punto 188 改款前三门、五门以及 2003 改款后三门、五门外廓，并批量处理 `12751`、`12752`、`15891`、`17392`、`17779`、`17780`、`58730`。
2. 闭合 Grande Punto、Punto Evo 跨改款 Ktype：`55446`、`7864`、`12203`、`12208`、`12196`。
3. 最后解决 `13959`、`120770`、Palio `16093/16091` 与 Panda Van `14143`，消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/heritage-hub-italy/press/heritage-celebrates-the-30th-anniversary-of-the-legendary-fiat-punto "Heritage celebrates the 30th anniversary of the legendary Fiat Punto | Heritage HUB Italy | Stellantis Media"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
更新点

* 已闭合 Punto 188 的 7 个剩余 Ktype，新增 16 条 READY 映射。
* Punto 188 改款前三门、五门外廓分别为 `3800×1660×1480`、`3835×1660×1480`；2003 年改款后三门、五门分别为 `3840×1660×1480`、`3865×1660×1480`，宽度均为不含后视镜口径。([汽车目录][1])
* 官方 2003 年车型阵容确认 1.2 16V、1.3 Multijet 和 1.4 16V 均存在三门和五门配置；Natural Power 与后期 Bifuel 按已确认的五门车身关联。([Stellantis Media][2])
* 本轮创建四个 Punto 188 稳定尺寸组；发动机、燃料及商用登记未触发重复建组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：90
* PENDING 输入 Ktype：10
* READY 映射：124 行
* 已确认尺寸组：28 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12752_3dr_prefl	12752	Hatchback	Punto 188 Series I	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门外廓。	READY
12752_5dr_prefl	12752	Hatchback	Punto 188 Series I	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	Series I五门外廓。	READY
12752_3dr_facelift	12752	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门外廓。	READY
12752_5dr_facelift	12752	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	2003年改款后五门外廓。	READY
12751_3dr_prefl	12751	Hatchback	Punto 188 Series I	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门外廓。	READY
12751_5dr_prefl	12751	Hatchback	Punto 188 Series I	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	Series I五门外廓。	READY
12751_3dr_facelift	12751	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门外廓。	READY
12751_5dr_facelift	12751	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	2003年改款后五门外廓。	READY
15891_prefl	15891	Van	Punto 188 Van Series I	188AX	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门商用车身外廓。	READY
15891_facelift	15891	Van	Punto 188 Van facelift	188AX	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门商用车身外廓。	READY
17779_3dr	17779	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门外廓。	READY
17779_5dr	17779	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门外廓。	READY
17780	17780	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Natural Power五门外廓。	READY
55446	55446	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Bifuel五门外廓。	READY
17392_3dr	17392	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	Multijet三门外廓。	READY
17392_5dr	17392	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Multijet五门外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	3800	1660	1480	Automobile-Catalog 2001 Fiat Punto 3-Porte 1.2 S	https://www.automobile-catalog.com/car/2001/723755/fiat_punto_3-porte_1_2_s.html
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	3835	1660	1480	Automobile-Catalog 2001 Fiat Punto 5-Porte 1.2 ELX	https://www.automobile-catalog.com/car/2001/723830/fiat_punto_5-porte_1_2_elx.html
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	3840	1660	1480	Fiat New Punto official press release	https://www.media.stellantis.com/uk-en/fiat/press/new-punto-on-sale-in-britain
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	3865	1660	1480	Automobile-Catalog 2004 Fiat Punto 5-Porte 1.2 Active	https://www.automobile-catalog.com/car/2004/724190/fiat_punto_5-porte_1_2_active.html
```

下一步优先处理

1. 闭合 Punto 199 商用车 Ktype `7864`、`12203`、`58730`、`12196`，按 Grande Punto、Punto Evo 和 2012 Punto 外廓拆分。
2. 关联 Punto 199 乘用版 `13959`、`120770`、`12208`，优先复用已存在的 2012 三门、五门尺寸组。
3. 最后处理 Palio `16093/16091` 与 Panda Van `14143`，消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/723755/fiat_punto_3-porte_1_2_s.html?utm_source=chatgpt.com "2001 Fiat Punto 3-Porte 1.2 S Specs Review (44 kW / ..."
[2]: https://www.media.stellantis.com/uk-en/fiat/press/new-punto-on-sale-in-britain "NEW PUNTO ON SALE IN BRITAIN | FIAT | Stellantis Media"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5001-5100_ktype_dimension_mapping_final.tsv
- left18448_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 剩余 10 个 Ktype 已全部闭合；新增 Palio Weekend Series III/IV、Grande Punto 与 Punto Evo 尺寸组，并复用既有 Panda 141A 与 Punto 2012 尺寸组。([汽车目录][1])
* 已完成机械检查：映射表严格为 10 列，尺寸组表严格为 6 列；152 个映射 `id` 唯一，34 个 `DIMENSION_GROUP_ID` 唯一；全部引用闭合且无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射：152 行
* PENDING：0
* DIMENSION_GROUP：34 个
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15827	15827	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	Series II Weekend五门外廓。	READY
5765	5765	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	MEDIUM	TD 100仅对应改款前四门外廓；输入结束月晚于该版本实际供应期。	READY
5764_prefl	5764	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	TD 75覆盖Series I改款前四门外廓。	READY
5764_facelift	5764	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	TD 75覆盖Series II改款后四门外廓。	READY
5761	5761	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
5778	5778	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-PREFL-01	HIGH	改款前Weekend五门外廓。	READY
15824	15824	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	Series II四门外廓。	READY
15825	15825	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	Series II Weekend五门外廓。	READY
12041	12041	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	155 20V Series II四门外廓。	READY
12044	12044	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	155 20V Series II Weekend五门外廓。	READY
12040	12040	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	HIGH	JTD 130 Series II四门外廓。	READY
12043	12043	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WAGON-FACELIFT-01	HIGH	JTD 130 Series II Weekend五门外廓。	READY
5774	5774	Sedan	Marea 185	185	4	EU-FIAT-MAREA-185-SEDAN-PREFL-01	HIGH	TD 125改款前四门外廓。	READY
143084_prefl	143084	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143084_facelift	143084	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
10499	10499	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
11759	11759	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Bipower五门外廓。	READY
16589_prefl	16589	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Bipower五门外廓。	READY
16589_facelift	16589	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	HIGH	改款后Bipower气体燃料五门外廓。	READY
113442_prefl	113442	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前GPL五门外廓。	READY
113442_facelift	113442	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后GPL五门外廓。	READY
11159	11159	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前Blupower五门外廓。	READY
143080	143080	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143081	143081	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
143082_prefl	143082	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前商用登记五门MPV外廓。	READY
143082_facelift	143082	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后商用登记五门MPV外廓。	READY
10500	10500	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
15828	15828	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
16862_prefl	16862	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
16862_facelift	16862	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	HIGH	改款后五门MPV外廓。	READY
143083_prefl	143083	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	上游能源标记异常；改款前Bipower五门外廓。	READY
143083_facelift	143083	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	MEDIUM	上游能源标记异常；改款后Bipower气体燃料五门外廓。	READY
8781_prefl	8781	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	MEDIUM	Series I五门旅行车外廓。	READY
8781_facelift	8781	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
16092_prefl	16092	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	MEDIUM	Series I五门旅行车外廓。	READY
16092_facelift	16092	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
8782	8782	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	HIGH	Series I五门旅行车外廓。	READY
16093_series2	16093	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
16093_series3	16093	Wagon	Palio Weekend 178 Series III	178DX	5	EU-FIAT-PALIO-178-WAGON-SERIES-III-01	MEDIUM	2004年第二次改款五门旅行车外廓。	READY
16093_series4	16093	Wagon	Palio Weekend 178 Series IV	178DX	5	EU-FIAT-PALIO-178-WAGON-SERIES-IV-01	MEDIUM	2007年改款五门旅行车外廓。	READY
8783	8783	Wagon	Palio Weekend 178 Series I	178DX	5	EU-FIAT-PALIO-178-WAGON-PREFL-01	HIGH	Series I五门旅行车外廓。	READY
16091_series2	16091	Wagon	Palio Weekend 178 Series II	178DX	5	EU-FIAT-PALIO-178-WAGON-FACELIFT-01	MEDIUM	Series II五门旅行车外廓。	READY
16091_series3	16091	Wagon	Palio Weekend 178 Series III	178DX	5	EU-FIAT-PALIO-178-WAGON-SERIES-III-01	MEDIUM	2004年第二次改款五门旅行车外廓。	READY
16091_series4	16091	Wagon	Palio Weekend 178 Series IV	178DX	5	EU-FIAT-PALIO-178-WAGON-SERIES-IV-01	MEDIUM	2007年改款五门旅行车外廓。	READY
14015_standard	14015	Hatchback	Panda 319	312PXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
14015_trekking	14015	Hatchback	Panda 319	312PXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱外廓。	READY
54902	54902	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
100778	100778	Hatchback	Panda 319	312PXP1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
100779	100779	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
111896	111896	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
111897	111897	Van	Panda 319	312DXG1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
118549	118549	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
17627	17627	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
59291	59291	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
12192	12192	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
14002	14002	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
17628	17628	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
111899	111899	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
16946	16946	Hatchback	Panda 141 Series I	141	3	EU-FIAT-PANDA-141-HATCHBACK-SERIES-I-01	HIGH	早期三门前驱外廓。	READY
56748	56748	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
108019	108019	Hatchback	Panda 319	312PXR2B	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Cross四驱外廓。	READY
111898	111898	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
56739_standard	56739	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	MEDIUM	Natural Power普通五门外廓。	READY
56739_trekking	56739	Hatchback	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Natural Power Trekking前驱外廓。	READY
111089_standard	111089	Hatchback	Panda 319	312PXN1A	5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	MEDIUM	Natural Power普通五门外廓。	READY
111089_trekking	111089	Hatchback	Panda 319	312PXN1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Natural Power Trekking前驱外廓。	READY
118547	118547	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	HIGH	商用登记，沿用Natural Power普通五门外廓。	READY
118550	118550	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	HIGH	商用登记，沿用Natural Power普通五门外廓。	READY
800120_standard	800120	Hatchback	Panda 319 facelift 2020	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
800120_citycross	800120	Hatchback	Panda 319 facelift 2020	319	5	EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	HIGH	City Cross前驱五门外廓。	READY
12193	12193	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
18093	18093	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
12204	12204	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	LPG商用登记，沿用普通前驱五门外廓。	READY
56749	56749	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	EasyPower普通前驱五门外廓。	READY
110001	110001	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	LPG商用登记，沿用普通前驱五门外廓。	READY
111900	111900	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用EasyPower普通前驱五门外廓。	READY
109999	109999	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-NATURAL-POWER-01	HIGH	Natural Power商用登记五门外廓。	READY
14008_standard	14008	Hatchback	Panda 319	312PXL1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
14008_trekking	14008	Hatchback	Panda 319	312PXL1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱外廓。	READY
17640	17640	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X2-01	HIGH	普通前驱五门外廓。	READY
111901	111901	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
114582_standard	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	MEDIUM	普通前驱五门外廓。	READY
114582_trekking	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	Trekking前驱五门外廓。	READY
114582_citycross	114582	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	MEDIUM	City Cross前驱五门外廓。	READY
118551	118551	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	商用登记，沿用普通前驱五门外廓。	READY
12194	12194	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
18092_4x4	18092	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	标准4x4五门分支。	READY
18092_cross	18092	Hatchback	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-CROSS-01	HIGH	Cross五门分支。	READY
56740	56740	Hatchback	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	标准4x4五门外廓。	READY
108020	108020	Hatchback	Panda 319	312PXS2A	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Cross四驱外廓。	READY
110002	110002	Van	Panda 169	169	5	EU-FIAT-PANDA-169-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
111902	111902	Van	Panda 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
114583_4x4	114583	Hatchback	Panda 319	312PXU1A	5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	MEDIUM	普通4x4五门外廓。	READY
114583_cross	114583	Hatchback	Panda 319	312PXU1A	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	MEDIUM	Cross四驱外廓。	READY
118552	118552	Van	Panda 319		5	EU-FIAT-PANDA-319-HATCHBACK-4X4-01	HIGH	商用登记，沿用标准4x4五门外廓。	READY
14143	14143	Van	Panda 141A	141A	3	EU-FIAT-PANDA-141A-HATCHBACK-4X2-01	MEDIUM	商用登记，沿用三门量产车身外廓。	READY
14481	14481	Hatchback	Panda 141A	141A	3	EU-FIAT-PANDA-141A-HATCHBACK-4X2-01	HIGH	1986年改款后三门前驱外廓。	READY
163519	163519	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	Pandina五门Cross外廓。	READY
163523_standard	163523	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-4X2-01	HIGH	POP与ICON普通五门外廓。	READY
163523_cross	163523	Hatchback	Pandina 319	319	5	EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	HIGH	CROSS五门外廓。	READY
52465_3dr	52465	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
52465_5dr	52465	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
100770_3dr	100770	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100770_5dr	100770	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
8908	8908	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
100883_3dr	100883	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100883_5dr	100883	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
17779_3dr	17779	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门外廓。	READY
17779_5dr	17779	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门外廓。	READY
13959_3dr	13959	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	2012版Bifuel三门外廓。	READY
13959_5dr	13959	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	MEDIUM	2012版Bifuel五门外廓。	READY
12752_3dr_prefl	12752	Hatchback	Punto 188 Series I	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门外廓。	READY
12752_5dr_prefl	12752	Hatchback	Punto 188 Series I	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	Series I五门外廓。	READY
12752_3dr_facelift	12752	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门外廓。	READY
12752_5dr_facelift	12752	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	2003年改款后五门外廓。	READY
12751_3dr_prefl	12751	Hatchback	Punto 188 Series I	188	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门外廓。	READY
12751_5dr_prefl	12751	Hatchback	Punto 188 Series I	188	5	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	HIGH	Series I五门外廓。	READY
12751_3dr_facelift	12751	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门外廓。	READY
12751_5dr_facelift	12751	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	2003年改款后五门外廓。	READY
15891_prefl	15891	Van	Punto 188 Van Series I	188AX	3	EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	HIGH	Series I三门商用车身外廓。	READY
15891_facelift	15891	Van	Punto 188 Van facelift	188AX	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	2003年改款后三门商用车身外廓。	READY
55446	55446	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Bifuel五门外廓。	READY
17780	17780	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Natural Power五门外廓。	READY
7864_grande	7864	Van	Grande Punto 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	MEDIUM	Grande Punto 199三门商用车身外廓。	READY
7864_evo	7864	Van	Punto Evo 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	MEDIUM	Punto Evo 199三门商用车身外廓。	READY
7864_2012	7864	Van	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	Punto 199 2012三门商用车身外廓。	READY
12203_grande	12203	Van	Grande Punto 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	MEDIUM	Grande Punto 199三门商用车身外廓。	READY
12203_evo	12203	Van	Punto Evo 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	MEDIUM	Punto Evo 199三门商用车身外廓。	READY
12203_2012	12203	Van	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	Punto 199 2012三门商用车身外廓。	READY
58730_grande	58730	Van	Grande Punto 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	MEDIUM	Grande Punto 199三门商用车身外廓。	READY
58730_evo	58730	Van	Punto Evo 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	MEDIUM	Punto Evo 199三门商用车身外廓。	READY
58730_2012	58730	Van	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	Punto 199 2012三门商用车身外廓。	READY
100780_3dr	100780	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	2012版三门外廓。	READY
100780_5dr	100780	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2012版五门外廓。	READY
17392_3dr	17392	Hatchback	Punto 188 facelift	188	3	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	HIGH	Multijet三门外廓。	READY
17392_5dr	17392	Hatchback	Punto 188 facelift	188	5	EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	HIGH	Multijet五门外廓。	READY
120770	120770	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	2018年仅五门量产外廓。	READY
55441_3dr	55441	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	HIGH	EasyPower三门外廓。	READY
55441_5dr	55441	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	HIGH	EasyPower五门外廓。	READY
12208_3dr_grande	12208	Hatchback	Grande Punto 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	MEDIUM	Grande Punto 199 LPG三门外廓。	READY
12208_5dr_grande	12208	Hatchback	Grande Punto 199	199	5	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-5D-01	MEDIUM	Grande Punto 199 LPG五门外廓。	READY
12208_3dr_evo	12208	Hatchback	Punto Evo 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	MEDIUM	Punto Evo 199 LPG三门外廓。	READY
12208_5dr_evo	12208	Hatchback	Punto Evo 199	199	5	EU-FIAT-PUNTO-199-HATCHBACK-EVO-5D-01	MEDIUM	Punto Evo 199 LPG五门外廓。	READY
12208_3dr_2012	12208	Hatchback	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	Punto 199 2012 LPG三门外廓。	READY
12208_5dr_2012	12208	Hatchback	Punto 199 2012	199	5	EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	MEDIUM	Punto 199 2012 LPG五门外廓。	READY
12196_grande	12196	Van	Grande Punto 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	MEDIUM	Grande Punto 199 Natural Power三门商用车身外廓。	READY
12196_evo	12196	Van	Punto Evo 199	199	3	EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	MEDIUM	Punto Evo 199 Natural Power三门商用车身外廓。	READY
12196_2012	12196	Van	Punto 199 2012	199	3	EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	MEDIUM	Punto 199 2012 Natural Power三门商用车身外廓。	READY
8909	8909	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
11799_3dr	11799	Hatchback	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	MEDIUM	第一代三门柴油外廓。	READY
11799_5dr	11799	Hatchback	Punto 176	176	5	EU-FIAT-PUNTO-176-HATCHBACK-5D-01	MEDIUM	第一代五门柴油外廓。	READY
8910	8910	Van	Punto 176	176	3	EU-FIAT-PUNTO-176-HATCHBACK-3D-01	HIGH	三门商用钢板侧窗外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5001-5100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-MAREA-185-WAGON-FACELIFT-01	4487	1741	1500	Automobile-Catalog 2001 Fiat Marea Weekend 100 16V ELX	https://www.automobile-catalog.com/car/2001/722570/fiat_marea_weekend_100_16v_elx.html
EU-FIAT-MAREA-185-SEDAN-PREFL-01	4378	1741	1420	Automobile-Catalog 1998 Fiat Marea 1.8 16V ELX	https://www.automobile-catalog.com/car/1998/721850/fiat_marea_1_8_16v_elx.html
EU-FIAT-MAREA-185-SEDAN-FACELIFT-01	4390	1741	1420	Automobile-Catalog 2001 Fiat Marea 100 16V ELX	https://www.automobile-catalog.com/car/2001/722225/fiat_marea_100_16v_elx.html
EU-FIAT-MAREA-185-WAGON-PREFL-01	4484	1741	1500	Automobile-Catalog 1998 Fiat Marea Weekend 1.6 16V ELX automatic	https://www.automobile-catalog.com/car/1998/721970/fiat_marea_weekend_1_6_16v_elx_automatic.html
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695	Automobile-Catalog 2003 Fiat Multipla 100 16V SX	https://www.automobile-catalog.com/car/2003/1221245/fiat_multipla_100_16v_sx.html
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4089	1871	1695	Fiat Multipla UK brochure Ed. 02/09; Automobile-Catalog 2004 Fiat Multipla 1.9 JTD 115 Dynamic	https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf;https://www.automobile-catalog.com/car/2004/723650/fiat_multipla_1_9_jtd_115_dynamic.html
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-CNG-01	4089	1871	1721	Automobile-Catalog 2005 Fiat Multipla 1.6 16V Natural Power CNG	https://www.automobile-catalog.com/car/2005/723680/fiat_multipla_1_6_16v_natural_power_cng.html
EU-FIAT-PALIO-178-WAGON-PREFL-01	4130	1614	1515	Automobile-Catalog 2000 Fiat Palio Weekend 75 EL	https://www.automobile-catalog.com/car/2000/723170/fiat_palio_weekend_75_el.html
EU-FIAT-PALIO-178-WAGON-FACELIFT-01	4142	1627	1488	Automobile-Catalog 2004 Fiat Palio Weekend 1.6 16V Active	https://www.automobile-catalog.com/car/2004/723305/fiat_palio_weekend_1_6_16v_active.html
EU-FIAT-PALIO-178-WAGON-SERIES-III-01	4215	1634	1515	Automobile-Catalog 2006 Fiat Palio Weekend ELX 1.4	https://www.automobile-catalog.com/car/2006/734825/fiat_palio_weekend_elx_1_4.html
EU-FIAT-PALIO-178-WAGON-SERIES-IV-01	4237	1639	1515	Automobile-Catalog 2008 Fiat Palio Weekend ELX 1.4	https://www.automobile-catalog.com/car/2008/735605/fiat_palio_weekend_elx_1_4.html
EU-FIAT-PANDA-319-HATCHBACK-4X2-01	3653	1643	1551	Fiat Panda official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
EU-FIAT-PANDA-319-HATCHBACK-4X4-01	3686	1672	1605	Fiat Panda 4x4 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
EU-FIAT-PANDA-141-HATCHBACK-SERIES-I-01	3380	1460	1445	Haynes Fiat Panda Owners Workshop Manual	https://dokumen.pub/haynes-fiat-panda-owners-workshop-manual-0856967939-9780856967931.html
EU-FIAT-PANDA-319-HATCHBACK-CROSS-01	3705	1662	1657	Fiat UK The New Fiat Panda Cross official press pack	https://www.media.stellantis.com/uk-en/fiat/press/the-new-fiat-panda-cross-a-car-like-no-other
EU-FIAT-PANDA-319-HATCHBACK-NATURAL-POWER-01	3653	1643	1605	Fiat Panda Natural Power official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/FILES/121016_F_panda_techspecification.pdf
EU-FIAT-PANDA-319-HATCHBACK-CITY-CROSS-01	3705	1662	1635	Auto-Data Fiat Panda III City Cross 1.0 Mild Hybrid	https://www.auto-data.net/en/fiat-panda-iii-city-cross-1.0-70hp-mild-hybrid-39071
EU-FIAT-PANDA-169-HATCHBACK-4X2-01	3538	1578	1540	Auto-Data Fiat Panda II 169 1.2 MPI specifications	https://www.auto-data.net/en/fiat-panda-ii-169-1.2-mpi-60hp-6903
EU-FIAT-PANDA-169-HATCHBACK-4X4-01	3574	1605	1632	Automobile-Catalog 2008 Fiat Panda Climbing 4x4 1.2	https://www.automobile-catalog.com/car/2008/726815/fiat_panda_climbing_4x4_1_2.html
EU-FIAT-PANDA-169-HATCHBACK-NATURAL-POWER-01	3538	1589	1576	Automobile-Catalog 2008 Fiat Panda 1.2 Natural Power CNG	https://www.automobile-catalog.com/car/2008/726785/fiat_panda_1_2_natural_power_cng.html
EU-FIAT-PANDA-169-HATCHBACK-CROSS-01	3581	1611	1643	Automobile-Catalog 2006 Fiat Panda Cross 4x4 1.3 Multijet 16V	https://www.automobile-catalog.com/car/2006/726860/fiat_panda_cross_4x4_1_3_multijet_16v.html
EU-FIAT-PANDA-141A-HATCHBACK-4X2-01	3408	1494	1420	Automobile-Catalog 1986 Fiat Panda D	https://www.automobile-catalog.com/car/1986/58535/fiat_panda_d.html
EU-FIAT-PUNTO-199-HATCHBACK-2012-3D-01	4065	1687	1490	Fiat Punto 2012 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/SCHEDE_TECNICHE/120207_F_Punto2012_ST_ALL_GBR.PDF
EU-FIAT-PUNTO-199-HATCHBACK-2012-5D-01	4065	1687	1490	Fiat Punto 2012 official technical specifications	https://www.media.stellantis.com/uploads/em/2012/FIAT/SCHEDE_TECNICHE/120207_F_Punto2012_ST_ALL_GBR.PDF
EU-FIAT-PUNTO-176-HATCHBACK-3D-01	3760	1620	1450	Stellantis Heritage 30th anniversary of Fiat Punto	https://www.media.stellantis.com/em-en/heritage-hub-italy/press/heritage-celebrates-the-30th-anniversary-of-the-legendary-fiat-punto
EU-FIAT-PUNTO-176-HATCHBACK-5D-01	3760	1620	1450	Stellantis Heritage 30th anniversary of Fiat Punto	https://www.media.stellantis.com/em-en/heritage-hub-italy/press/heritage-celebrates-the-30th-anniversary-of-the-legendary-fiat-punto
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-3D-01	3800	1660	1480	Automobile-Catalog 2001 Fiat Punto 3-Porte 1.2 S	https://www.automobile-catalog.com/car/2001/723755/fiat_punto_3-porte_1_2_s.html
EU-FIAT-PUNTO-188-HATCHBACK-PREFL-5D-01	3835	1660	1480	Automobile-Catalog 2001 Fiat Punto 5-Porte 1.2 ELX	https://www.automobile-catalog.com/car/2001/723830/fiat_punto_5-porte_1_2_elx.html
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-3D-01	3840	1660	1480	Fiat New Punto official press release	https://www.media.stellantis.com/uk-en/fiat/press/new-punto-on-sale-in-britain
EU-FIAT-PUNTO-188-HATCHBACK-FACELIFT-5D-01	3865	1660	1480	Automobile-Catalog 2004 Fiat Punto 5-Porte 1.2 Active	https://www.automobile-catalog.com/car/2004/724190/fiat_punto_5-porte_1_2_active.html
EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-3D-01	4030	1687	1490	Automobile-Catalog 2008 Fiat Grande Punto 1.4 Active	https://www.automobile-catalog.com/car/2008/1229390/fiat_grande_punto_1_4_active.html
EU-FIAT-PUNTO-199-HATCHBACK-GRANDE-5D-01	4030	1687	1490	Automobile-Catalog 2008 Fiat Grande Punto 1.4 Active	https://www.automobile-catalog.com/car/2008/1229390/fiat_grande_punto_1_4_active.html
EU-FIAT-PUNTO-199-HATCHBACK-EVO-3D-01	4065	1687	1490	Automoli Fiat Punto Evo 199 vehicle specifications	https://www.automoli.com/en/vehicles/fiat/punto/punto-evo-199-3778/
EU-FIAT-PUNTO-199-HATCHBACK-EVO-5D-01	4065	1687	1490	Automoli Fiat Punto Evo 199 vehicle specifications	https://www.automoli.com/en/vehicles/fiat/punto/punto-evo-199-3778/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5001-5100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2006/734825/fiat_palio_weekend_elx_1_4.html?utm_source=chatgpt.com "2006 Fiat Palio Weekend ELX 1.4 Specs Review (60 kW ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（805 行）
- 累计尺寸组：dimension_groups_final.tsv（219 行）

