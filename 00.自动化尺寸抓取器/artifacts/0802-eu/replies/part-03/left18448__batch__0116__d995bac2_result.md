# 任务：left18448 第 11501-11600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0116__d995bac2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11501-11600 行

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
left18448 第 11501-11600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	4445	1640	1575
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	4445	1640	1580
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	4295	1640	1525
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	4600	1775	1690
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	4600	1775	1650

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mitsubishi	Space wagon	2.0 Glxi 4WD	Großraumlimousine	Allrad	Benzin	Jun 1988	Apr 1991	3379
Mitsubishi	Space wagon	2.4 GDI	Großraumlimousine	Frontantrieb	Benzin	Oct 1998	Dec 2004	10103
Mitsubishi	Space wagon	2.4 GDI	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Dec 2004	16166
Mitsubishi	Space wagon	2.4 GDI 4WD	Großraumlimousine	Allrad	Benzin	Oct 1998	Dec 2004	10359
Mitsubishi	Space wagon	2.4 GDI 4WD	Großraumlimousine	Allrad	Benzin	Sep 2000	Dec 2004	16167
Mitsubishi	Space wagon van	1.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 1986	Dec 1988	143202
Mitsubishi	Space wagon van	1.8 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 1983	Sep 1987	143203
Mitsubishi	Starion	2.0 Turbo ECI	Coupe	Heckantrieb	Benzin	Jun 1982	Dec 1985	3372
Mitsubishi	Starion	2.0 Turbo ECI	Coupe	Heckantrieb	Benzin	May 1985	Aug 1987	3373
Mitsubishi	Starion	2.6 Turbo ECI	Coupe	Heckantrieb	Benzin	Sep 1987	Jun 1990	3374
Mitsubishi	Tredia	1.4 GLX	Stufenheck	Frontantrieb	Benzin	Oct 1982	Aug 1985	3316
Mitsubishi	Tredia	1.6 GLS	Stufenheck	Frontantrieb	Benzin	Sep 1982	Oct 1987	3318
Mitsubishi	Tredia	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	Sep 1982	May 1985	3319
Mitsubishi	Tredia	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	Sep 1982	Jul 1984	3320
Mitsubishi	Tredia	1.8 GLS	Stufenheck	Frontantrieb	Benzin	Aug 1984	Jul 1986	3321
Mitsubishi	Tredia	1.8 GLS 4WD	Stufenheck	Allrad	Benzin	Apr 1985	Jul 1986	58729
Mitsubishi	Tredia	2.0 Glxi 4WD	Stufenheck	Allrad	Benzin	Oct 1986	Mar 1988	59323
Mitsuoka	Himiko	2	Cabriolet	Heckantrieb	Benzin	Sep 2009	-	34840
Mitsuoka	Himiko	2	Cabriolet	Heckantrieb	Benzin	Sep 2009	-	34841
Mitsuoka	Orochi	3.3 L V6	Coupe	Heckantrieb	Benzin	Sep 2006	-	34839
Mobilize	Bento pro	EV	Pritsche/Fahrgestell	Heckantrieb	Elektro	Oct 2024	-	160704
Mobilize	Duo	EV	Schrägheck	Heckantrieb	Elektro	Jan 2025	-	160810
Mobilize	Duo	EV	Schrägheck	Heckantrieb	Elektro	Jan 2025	-	160811
Morgan	3-Wheeler	2	Cabriolet	Heckantrieb	Benzin	May 2014	-	106391
Morgan	Aero	4.8 V8	Coupe	Heckantrieb	Benzin	Oct 2012	-	54920
Morgan	Aero 8	4.4	Cabriolet	Heckantrieb	Benzin	Oct 2000	-	14809
Morgan	Aero 8	4.4	Cabriolet	Heckantrieb	Benzin	Apr 2004	-	17932
Morgan	Aero 8	4.8	Cabriolet	Heckantrieb	Benzin	Oct 2008	-	11824
Morgan	Aero supersports	4.8 V8	Cabriolet	Heckantrieb	Benzin	Mar 2010	-	34847
Morgan	Four	1.6	Cabriolet	Heckantrieb	Benzin	Jan 1968	Aug 1982	13639
Morgan	Four	2	Cabriolet	Heckantrieb	Benzin	Jan 2010	-	126175
Morgan	Four	1.6 Cvh/ohv	Cabriolet	Heckantrieb	Benzin	Aug 1982	Sep 1991	13640
Morgan	Four	1.6 I	Cabriolet	Heckantrieb	Benzin	Jan 1985	Aug 1991	13643
Morgan	Four	1.6 I	Cabriolet	Heckantrieb	Benzin	Jan 2009	-	124209
Morgan	Four	1.6 I KAT	Cabriolet	Heckantrieb	Benzin	Aug 1991	Dec 1993	13642
Morgan	Four	1.8 I	Cabriolet	Heckantrieb	Benzin	Jan 1993	Jan 2005	13644
Morgan	Plus eight	3.5	Cabriolet	Heckantrieb	Benzin	Jan 1968	Dec 1986	13665
Morgan	Plus eight	3.9	Cabriolet	Heckantrieb	Benzin	Aug 1990	Apr 1995	13667
Morgan	Plus eight	4.6	Cabriolet	Heckantrieb	Benzin	Jan 1996	Oct 2001	13668
Morgan	Plus eight	3.5 EFI	Cabriolet	Heckantrieb	Benzin	Jan 1984	Aug 1990	13666
Morgan	Plus eight	4.8 V8	Cabriolet	Heckantrieb	Benzin	Mar 2010	-	54918
Morgan	Plus four	1.8 I	Cabriolet	Heckantrieb	Benzin	Jan 1993	Jun 1999	13658
Morgan	Plus four	2.0 I	Cabriolet	Heckantrieb	Benzin	Nov 1991	May 2000	13659
Morgan	Plus four	2.0 I	Cabriolet	Heckantrieb	Benzin	Jan 1985	Aug 1988	13661
Morgan	Plus four	2.0 I	Cabriolet	Heckantrieb	Benzin	Aug 1988	Dec 2000	13664
Morgan	Plus four	2.0 I	Cabriolet	Heckantrieb	Benzin	Jan 2004	Jun 2014	54919
Morgan	Plus four	2.0 I	Cabriolet	Heckantrieb	Benzin	Jun 2014	Feb 2020	108942
Morgan	Roadster	3.7	Cabriolet	Heckantrieb	Benzin	Nov 2011	-	108647
Morgan	Roadster	1.6 4/4	Cabriolet	Heckantrieb	Benzin	Jan 2004	-	34844
Morgan	Roadster	2.0 Plus4	Cabriolet	Heckantrieb	Benzin	Jan 2004	Dec 2009	34845
Morgan	Roadster	3.0 V6	Cabriolet	Heckantrieb	Benzin	Jan 2004	-	34846
Morgan	Supersport	3	Cabriolet	Heckantrieb	Benzin	Apr 2025	-	161344
Morris	Marina	1.3	Kombi	Heckantrieb	Benzin	Oct 1978	Oct 1980	13849
Morris	Marina	1.7	Kombi	Heckantrieb	Benzin	Nov 1978	Jun 1980	13257
Morris	Marina	1.8	Stufenheck	Heckantrieb	Benzin	Apr 1971	Dec 1979	6057
Morris	Marina	1300	Stufenheck	Heckantrieb	Benzin	Apr 1971	Jun 1975	6053
Morris	Marina	1300	Coupe	Heckantrieb	Benzin	Apr 1971	Jun 1980	6054
Morris	Marina	1300	Kombi	Heckantrieb	Benzin	Mar 1978	Oct 1980	14001
Morris	Marina	1300	Stufenheck	Heckantrieb	Benzin	Oct 1975	Sep 1978	14009
Morris	Marina	1750	Stufenheck	Heckantrieb	Benzin	Oct 1975	Sep 1978	13991
Morris	Marina	1800	Coupe	Heckantrieb	Benzin	Apr 1971	Dec 1975	6059
Morris	Marina	1800	Stufenheck	Heckantrieb	Benzin	Oct 1975	Sep 1978	13848
Morris	Marina	1800	Kombi	Heckantrieb	Benzin	Oct 1975	Oct 1978	14003
Morris	Marina	1800	Stufenheck	Heckantrieb	Benzin	Mar 1975	Oct 1978	14011
Morris	Marina	2600	Stufenheck	Heckantrieb	Benzin	Oct 1975	Sep 1978	13993
Morris	Marina	1,3	Stufenheck	Heckantrieb	Benzin	Oct 1978	Oct 1980	14000
Morris	Marina	1,5 Diesel	Stufenheck	Heckantrieb	Diesel	Oct 1978	Oct 1980	13996
Morris	Marina	1.8 TC	Stufenheck	Heckantrieb	Benzin	Apr 1971	Sep 1975	6058
Morris	Marina	1500 Diesel	Stufenheck	Heckantrieb	Diesel	Oct 1975	Sep 1978	13990
Morris	Marina	1500 Diesel	Stufenheck	Heckantrieb	Diesel	Apr 1971	Sep 1975	14010
Morris	Marina	1800 GT	Stufenheck	Heckantrieb	Benzin	Mar 1975	Oct 1978	14012
Morris	Marina	1800 HL	Stufenheck	Heckantrieb	Benzin	Mar 1975	Oct 1978	13992
Morris	Marina	1800 TC	Coupe	Heckantrieb	Benzin	Apr 1971	Dec 1975	6061
Moskvich	412	1.5	Stufenheck	Heckantrieb	Benzin	Sep 1981	Oct 1988	14032
Mosler	Mt900	7.0 GTR	Coupe	Heckantrieb	Benzin	Jul 2006	Oct 2011	801847
Navor	E5	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Jun 2025	-	161913
Nextem	Humpback	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2022	-	152872
Nextem	Minke	Electric	Kasten	Heckantrieb	Elektro	Jan 2022	-	152873
Nextem	Orca	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2022	-	152871
NIO	Ec6	EV	SUV	Allrad	Elektro	Sep 2023	-	156227
NIO	El6	EV Allrad	SUV	Allrad	Elektro	Oct 2023	-	154975
NIO	El7	EV Allrad	SUV	Allrad	Elektro	Jan 2023	-	147934
NIO	El7	EV Allrad	SUV	Allrad	Elektro	Jan 2023	-	150465
NIO	El8	EV	SUV	Allrad	Elektro	Jul 2024	-	159371
NIO	El8	EV Allrad	SUV	Allrad	Elektro	Jul 2024	-	151711
NIO	Es6	EV	SUV	Allrad	Elektro	May 2023	-	155115
NIO	Et5	EV Allrad	Stufenheck	Allrad	Elektro	Mar 2023	-	146217
NIO	Et5	EV Allrad	Kombi	Allrad	Elektro	Aug 2023	-	154974
NIO	Et7	EV Allrad	Stufenheck	Allrad	Elektro	Jan 2023	-	143290
Nissan	200sx	2.4	Coupe	Heckantrieb	Benzin	Sep 1988	Dec 1990	46220
Nissan	200sx	2.0 I 16V	Coupe	Heckantrieb	Benzin	Oct 1993	Dec 1999	12459
Nissan	240sx	2.4	Coupe	Heckantrieb	Benzin	Sep 1988	Dec 1990	109605
Nissan	240z	2.4	Coupe	Heckantrieb	Benzin	Oct 1970	May 1974	58681
Nissan	260z	2.6 2+2	Coupe	Heckantrieb	Benzin	May 1974	Dec 1979	58682
Nissan	350z	3.5	Coupe	Heckantrieb	Benzin	Oct 2003	Dec 2006	17435
Nissan	350z roadster	3.5	Cabriolet	Heckantrieb	Benzin	Mar 2005	Dec 2007	18277
Nissan	370z	3.7	Coupe	Heckantrieb	Benzin	Apr 2009	-	106194
Nissan	370z	Nismo 3.7	Coupe	Heckantrieb	Benzin	Jun 2013	-	58978
Nissan	370z roadster	3.7	Cabriolet	Heckantrieb	Benzin	Jan 2010	-	34552
Nissan	Almera i	2	Stufenheck	Frontantrieb	Benzin	Jul 1995	Jul 2000	58856


--- Round 1 / 首次发送 ---
## 更新点

* 已按尺寸组缓存优先完成 **20 个 Ktype**，新增/修改 **21 条映射**。
* Space Wagon III 的前驱低顶与四驱高顶分别复用已有尺寸组；Space Wagon I 4WD 的 Ktype `3379` 覆盖改款前后两种已缓存外廓，因此拆为两条派生映射。([汽车数据网][1])
* Starion 已确认 `A183A` 窄体与 `A187A` 宽体边界；两代外廓宽度不同，分别首次创建尺寸组。([Brembo Parts][2])
* NIO 本轮车型均使用官方发布页或官方用户手册闭合三维，其中 EL6 与 ES6 为同一第二代物理车身并复用同一尺寸组。([蔚来][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：20
* READY 映射：21
* PENDING Ktype：80
* 本轮首次创建尺寸组：10
* 本轮复用已有尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3379_prefl	3379	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	MEDIUM	Ktype覆盖改款前4WD外廓分支。	READY
3379_facelift	3379	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	MEDIUM	Ktype覆盖改款后4WD外廓分支。	READY
10103	10103	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	前驱低顶物理外廓。	READY
16166	16166	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	前驱低顶物理外廓。	READY
10359	10359	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	四驱高顶物理外廓。	READY
16167	16167	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	四驱高顶物理外廓。	READY
3372	3372	Coupe	Starion	A183A	3	EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	HIGH	A183A窄体外廓。	READY
3373	3373	Coupe	Starion	A183A	3	EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	HIGH	A183A中期改款仍使用相同窄体外廓。	READY
3374	3374	Coupe	Starion	A187A	3	EU-MITSUBISHI-STARION-A187A-COUPE-3D-WIDEBODY-01	HIGH	A187A宽体外廓。	READY
160810	160810	Hatchback	Duo		2	EU-MOBILIZE-DUO-HATCHBACK-2D-01	HIGH	Duo双座微型车外廓。	READY
160811	160811	Hatchback	Duo		2	EU-MOBILIZE-DUO-HATCHBACK-2D-01	HIGH	Duo动力版本不改变外廓。	READY
156227	156227	SUV	EC6 II		5	EU-NIO-EC6-II-SUV-5D-01	HIGH	第二代EC6轿跑SUV外廓。	READY
154975	154975	SUV	EL6 (ES6 II)		5	EU-NIO-ES6-II-SUV-5D-01	HIGH	欧洲EL6对应第二代ES6物理车身。	READY
147934	147934	SUV	EL7 (ES7)		5	EU-NIO-ES7-SUV-5D-01	HIGH	EL7标准物理外廓。	READY
150465	150465	SUV	EL7 (ES7)		5	EU-NIO-ES7-SUV-5D-01	HIGH	重复动力条目复用EL7外廓。	READY
159371	159371	SUV	EL8 (ES8 II)		5	EU-NIO-ES8-II-SUV-5D-01	HIGH	第二代EL8六座SUV外廓。	READY
151711	151711	SUV	EL8 (ES8 II)		5	EU-NIO-ES8-II-SUV-5D-01	HIGH	重复动力条目复用EL8外廓。	READY
155115	155115	SUV	ES6 II		5	EU-NIO-ES6-II-SUV-5D-01	HIGH	中国市场ES6与欧洲EL6为相同第二代车身。	READY
146217	146217	Sedan	ET5		4	EU-NIO-ET5-SEDAN-4D-01	HIGH	ET5四门轿车外廓。	READY
154974	154974	Wagon	ET5		5	EU-NIO-ET5-WAGON-5D-01	HIGH	ET5 Touring旅行车外廓。	READY
143290	143290	Sedan	ET7		4	EU-NIO-ET7-SEDAN-4D-01	HIGH	ET7四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	4430	1705	1315	Automobile-Catalog 1985 Mitsubishi Starion 2000 Turbo	https://www.automobile-catalog.com/car/1985/57185/mitsubishi_starion_turbo.html
EU-MITSUBISHI-STARION-A187A-COUPE-3D-WIDEBODY-01	4430	1745	1315	Automobile-Catalog 1988 Mitsubishi Starion 2600 Turbo catalyst	https://www.automobile-catalog.com/car/1988/1929155/mitsubishi_starion_2600_turbo_cat.html
EU-MOBILIZE-DUO-HATCHBACK-2D-01	2430	1300	1460	Automobile Dimension Mobilize Duo	https://www.automobiledimension.com/model/mobilize/duo
EU-NIO-EC6-II-SUV-5D-01	4849	1995	1697	NIO All-New EC6 official launch	https://www.nio.com/news/all-new-EC6-launch
EU-NIO-ES6-II-SUV-5D-01	4854	1995	1703	NIO All-New ES6 official launch	https://www.nio.com/news/All-New-ES6-Launch
EU-NIO-ES7-SUV-5D-01	4912	1987	1720	NIO EL7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/EL7/index.html
EU-NIO-ES8-II-SUV-5D-01	5099	1989	1750	NIO EL8 official user manual	https://www.nio.com/cdn-static/www/user-instructions/EL8/index.html
EU-NIO-ET5-SEDAN-4D-01	4790	1960	1499	NIO ET5 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET5/index.html
EU-NIO-ET5-WAGON-5D-01	4790	1960	1499	NIO ET5 Touring official user manual	https://www.nio.com/cdn-static/www/user-instructions/ET5-Touring/index.html
EU-NIO-ET7-SEDAN-4D-01	5101	1987	1509	NIO ET7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/ET7/index.html
```

## 下一步优先处理

1. 闭合 Mitsubishi Tredia 的前驱、四驱及年份高度差异。
2. 按共用传统车身平台批量处理 Morgan Four、Plus Four、Roadster 和 Plus Eight。
3. 按 Sedan、Coupe、Wagon 聚类处理 Morris Marina。
4. 批量闭合 Nissan S13/S14、S30、350Z 与 370Z 各车身组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-space-wagon-iii-2.4-gdi-150hp-15595?utm_source=chatgpt.com "Mitsubishi Space Wagon III 2.4 GDI (150 Hp) /Minivan 1998"
[2]: https://www.bremboparts.com/europe/en/catalogue/mitsubishi-starion-a18-a-2-0-turbo-eci-a183a/000003372-1?utm_source=chatgpt.com "Pads and Discs for MITSUBISHI STARION (A18_A) 2.0 Turbo ECi (A183A)"
[3]: https://www.nio.com/news/All-New-ES6-Launch?utm_source=chatgpt.com "NIO Launches the All-New ES6, a Smart Electric All-Round ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Space Wagon Van 两个 Ktype 已关联同代前驱缓存尺寸组，不重复输出该既有尺寸组。([汽车目录][1])
* Tredia 已按前驱标准高度与四驱增高车身拆分为两个尺寸组，完成 7 个 Ktype。([汽车目录][2])
* 新增闭合 Orochi、Mobilize Bento、350Z Coupe 与 350Z Roadster 尺寸组。([Carfolio][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：33
* READY 映射：34
* PENDING Ktype：67
* 已确认尺寸组：21
* 本轮新增映射：13
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143202	143202	Van	Space Wagon I		5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	MEDIUM	商用Van与同代前驱车身共用外廓。	READY
143203	143203	Van	Space Wagon I	D09V	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D09V商用柴油Van外廓。	READY
3316	3316	Sedan	Tredia	A211	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A211四门前驱外廓。	READY
3318	3318	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212四门前驱外廓。	READY
3319	3319	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212涡轮版本不改变外廓。	READY
3320	3320	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212涡轮版本不改变外廓。	READY
3321	3321	Sedan	Tredia	A215	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A215四门前驱外廓。	READY
58729	58729	Sedan	Tredia	A215G	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	HIGH	A215G四驱车身高度增加。	READY
59323	59323	Sedan	Tredia		4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	MEDIUM	四驱版本采用同一增高外廓。	READY
34839	34839	Coupe	Orochi	MSP1	2	EU-MITSUOKA-OROCHI-MSP1-COUPE-2D-01	HIGH	MSP1量产双门车身。	READY
160704	160704	Van	Bento		2	EU-MOBILIZE-BENTO-VAN-2D-01	MEDIUM	单座封闭货箱版物理外廓。	READY
17435	17435	Coupe	350Z	Z33	3	EU-NISSAN-350Z-Z33-COUPE-3D-01	HIGH	Z33三门Coupe外廓。	READY
18277	18277	Convertible	350Z Roadster	HZ33	2	EU-NISSAN-350Z-HZ33-CONVERTIBLE-2D-01	HIGH	HZ33双门敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	4280	1660	1370	Auto-Data Mitsubishi Tredia 1400 GLX; Automobile-Catalog Mitsubishi Tredia 1600 Turbo; Automobile-Catalog Mitsubishi Tredia 1800 GLS	https://www.auto-data.net/en/mitsubishi-tredia-a21-1400-glx-a211-70hp-15816; https://www.automobile-catalog.com/car/1982/1917125/mitsubishi_tredia_1600_turbo.html; https://www.automobile-catalog.com/car/1984/1917155/mitsubishi_tredia_1800_gls.html
EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	4280	1660	1415	Automobile-Catalog Mitsubishi Tredia 1800 4WD GLS; Automobile-Catalog Mitsubishi Tredia 2000 4WD catalyst	https://www.automobile-catalog.com/car/1984/1917200/mitsubishi_tredia_1800_4wd_gls.html; https://www.automobile-catalog.com/car/1987/1917275/mitsubishi_tredia_2000_4wd_cat.html
EU-MITSUOKA-OROCHI-MSP1-COUPE-2D-01	4560	2035	1180	TCV Mitsuoka Orochi specifications; Carfolio Mitsuoka Orochi	https://www.tc-v.com/specifications/mitsuoka/orochi/; https://www.carfolio.com/mitsuoka-orochi-293271
EU-MOBILIZE-BENTO-VAN-2D-01	2540	1300	1570	Mobilize official Bento product article; VanReviewer Mobilize Bento dimensions	https://www.mobilize.com/en/wearemobilizers/mobilize-bento-the-small-van-thats-changing-the-game/; https://vanreviewer.co.uk/renault/mobilize-bento/dimensions/5894/
EU-NISSAN-350Z-Z33-COUPE-3D-01	4310	1815	1315	Nissan Heritage Collection Fairlady Z Version ST	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/284_fairlady_z_version_st.html
EU-NISSAN-350Z-HZ33-CONVERTIBLE-2D-01	4310	1815	1325	Nissan Heritage Collection Fairlady Z Roadster	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/383_fairlady_z_roadster.html
```

## 下一步优先处理

1. 闭合 Mitsuoka Himiko 两个 Ktype 的变速箱或规格高度分支。
2. 按传统车架外廓批量处理 Morgan Four、Plus Four、Roadster 与 Plus Eight。
3. 按 Sedan、Coupe、Wagon 聚类处理 Morris Marina。
4. 继续处理 Nissan S13/S14、S30、370Z 及 Roadster 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/48920/mitsubishi_space_wagon_1_8_glx.html?utm_source=chatgpt.com "1988 Mitsubishi Space Wagon 1800 GLX Specs Review (66 kW / 90 PS / 89 hp) (up to mid-year 1988 for Europe )"
[2]: https://www.automobile-catalog.com/car/1984/1917155/mitsubishi_tredia_1800_gls.html?utm_source=chatgpt.com "1984 Mitsubishi Tredia 1800 GLS Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1984 for Europe )"
[3]: https://www.carfolio.com/mitsuoka-orochi-293271?utm_source=chatgpt.com "2012 Mitsuoka Orochi: detailed specifications, performance ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Nissan S13、S14 两个车身簇，Ktype `46220` 与 `109605` 关联 S13 2.4L 外廓，Ktype `12459` 关联 S14 外廓。([汽车数据网][1])
* 已闭合 240Z 双座车身与 260Z 2+2 长车身，两者分别建组。([日产汽车全球官网][2])
* 370Z 标准 Coupe 与 NISMO 因前后保险杠外廓变化分别拆为改款前后分支；Roadster 改款前后三维保持一致，仅建立一个尺寸组。
* 已通过 N15 维修手册闭合 Almera I 四门 Sedan 尺寸组。([Doksi][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：42
* READY 映射：45
* PENDING Ktype：58
* 已确认尺寸组：31
* 本轮新增映射：11
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
46220	46220	Coupe	S13	S13	2	EU-NISSAN-240SX-S13-COUPE-2D-01	MEDIUM	2.4L S13双门外廓。	READY
12459	12459	Coupe	S14	S14	2	EU-NISSAN-200SX-S14-COUPE-2D-01	HIGH	S14双门Coupe外廓。	READY
109605	109605	Coupe	S13	S13	2	EU-NISSAN-240SX-S13-COUPE-2D-01	HIGH	S13双门Coupe外廓。	READY
58681	58681	Coupe	S30	HLS30	3	EU-NISSAN-240Z-S30-COUPE-3D-01	HIGH	S30双座掀背外廓。	READY
58682	58682	Coupe	S30		3	EU-NISSAN-260Z-S30-COUPE-3D-2PLUS2-01	HIGH	S30长轴距2+2外廓。	READY
106194_prefl	106194	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-PREFL-01	HIGH	初期标准Coupe保险杠外廓。	READY
106194_facelift	106194	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-FACELIFT-01	HIGH	后期标准Coupe保险杠外廓。	READY
58978_prefl	58978	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-PREFL-01	HIGH	初期NISMO空气动力套件外廓。	READY
58978_facelift	58978	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-FACELIFT-01	HIGH	后期NISMO空气动力套件外廓。	READY
34552	34552	Convertible	370Z Z34	HZ34	2	EU-NISSAN-370Z-HZ34-CONVERTIBLE-2D-01	HIGH	HZ34双门敞篷外廓。	READY
58856	58856	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-01	MEDIUM	N15四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-240SX-S13-COUPE-2D-01	4520	1690	1290	Auto-Data Nissan 240SX Coupe S13 2.4	https://www.auto-data.net/en/nissan-240sx-coupe-s13-2.4-134hp-42566
EU-NISSAN-200SX-S14-COUPE-2D-01	4560	1730	1295	Auto-Data Nissan 200 SX S14 2.0 i 16V Turbo	https://www.auto-data.net/en/nissan-200-sx-s14-2.0-i-16v-turbo-200hp-380
EU-NISSAN-240Z-S30-COUPE-3D-01	4115	1630	1305	Nissan Heritage Collection Datsun 240Z	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/datsun_240z.html
EU-NISSAN-260Z-S30-COUPE-3D-2PLUS2-01	4445	1650	1290	Datsun 260Z 2+2 official UK brochure	https://xr793.com/wp-content/uploads/2022/10/1974-Datsun-260Z-22-UK.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-PREFL-01	4250	1845	1315	Nissan 370Z official European brochure	https://www.nissan-cdn.net/content/dam/Nissan/lv/brochures/brochureslv/ebrochure-370z.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-FACELIFT-01	4265	1845	1310	Nissan Europe FY17 370Z official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/pt/brochures/E-Catalago_370Z_PT.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-PREFL-01	4410	1870	1315	Nissan 370Z NISMO official European brochure	https://www.nissan-cdn.net/content/dam/Nissan/lv/brochures/brochureslv/ebrochure-370z.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-FACELIFT-01	4300	1870	1310	Nissan Europe FY17 370Z NISMO official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/pt/brochures/E-Catalago_370Z_PT.pdf
EU-NISSAN-370Z-HZ34-CONVERTIBLE-2D-01	4250	1845	1325	Nissan 370Z Roadster official UK brochure; Auto-Data Nissan 370Z Roadster; Auto-Data Nissan 370Z Roadster facelift 2012	https://xr793.com/wp-content/uploads/2022/10/2013-Nissan-370Z-Roadster-UK.pdf; https://www.auto-data.net/en/nissan-370z-roadster-generation-8044; https://www.auto-data.net/en/nissan-370z-roadster-facelift-2012-generation-4595
EU-NISSAN-ALMERA-I-N15-SEDAN-4D-01	4320	1690	1395	Nissan Almera N15 service manual	https://doksi.net/en/get.php?lid=39709
```

## 下一步优先处理

1. 按传统车架年代和外廓变化批量闭合 Morgan Four、Plus Four、Roadster 与 Plus Eight。
2. 按 Sedan、Coupe、Wagon 三种车身批量处理 Morris Marina。
3. 处理 Himiko、Morgan Aero 系列及 Morgan 3-Wheeler。
4. 闭合 Moskvich、Mosler、Navor 与 Nextem 车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/nissan-200-sx-s14-2.0-i-16v-turbo-200hp-380 "Nissan 200 SX (S14) 2.0 i 16V Turbo (200 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/datsun_240z.html "Nissan | Heritage Collection | Datsun 240Z"
[3]: https://doksi.net/en/get.php?lid=39709 "Nissan Almera N15 service manual"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已按 Marina I、II、III 的车身改款边界，闭合本批次中可确认的 Sedan、Coupe 与 Wagon 外廓；跨代 Ktype 已拆为稳定派生行。各代保险杠及车身长度变化对应不同尺寸组。([汽车目录][1])
* 新增闭合 Mosler MT900 GTR 和 Navor E5；Navor E5 使用与 DFSK E5 对应的量产外廓。([auto motor und sport][2])
* Morris Marina 的 1750 ZA、2600 ZA 和部分柴油分支暂未写入，本轮不创建猜测性映射。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：61
* READY 映射：74
* PENDING Ktype：39
* 已确认尺寸组：45
* 本轮新增映射：29
* 本轮首次创建尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13849	13849	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Marina III五门Wagon外廓。	READY
13257	13257	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Marina III五门Wagon外廓。	READY
6057_mk1	6057	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype覆盖Marina I标准四门外廓。	READY
6057_mk2	6057	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype覆盖Marina II四门外廓。	READY
6057_mk3	6057	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	MEDIUM	Ktype生产区间延伸至Marina III外廓。	READY
6053	6053	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	HIGH	Marina I标准四门外廓。	READY
6054_mk1	6054	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	HIGH	Marina I双门Coupe外廓。	READY
6054_mk2	6054	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1300-01	HIGH	Marina II 1300双门外廓。	READY
6054_mk3	6054	Coupe	Marina III	ADO28	2	EU-MORRIS-MARINA-III-COUPE-2D-01	HIGH	Marina III双门Coupe外廓。	READY
14001_mk2	14001	Wagon	Marina II	ADO28	5	EU-MORRIS-MARINA-II-WAGON-5D-01	HIGH	Ktype前期对应Marina II Wagon。	READY
14001_mk3	14001	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Ktype后期对应Marina III Wagon。	READY
14009	14009	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1300-01	HIGH	Marina II 1300四门外廓。	READY
6059_mk1	6059	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	MEDIUM	Marina I标准1800 Coupe外廓。	READY
6059_mk2	6059	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1800-01	MEDIUM	Ktype末期覆盖Marina II 1800 Coupe外廓。	READY
13848	13848	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	HIGH	Marina II 1800四门外廓。	READY
14003	14003	Wagon	Marina II	ADO28	5	EU-MORRIS-MARINA-II-WAGON-5D-01	HIGH	Marina II 1800五门Wagon外廓。	READY
14011_mk1	14011	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype前期对应Marina I四门外廓。	READY
14011_mk2	14011	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期对应Marina II四门外廓。	READY
14000	14000	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	HIGH	Marina III 1300四门外廓。	READY
13996	13996	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	HIGH	Marina III柴油版采用同一四门外廓。	READY
6058	6058	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	HIGH	Marina I 1.8 TC四门高度分支。	READY
14012_mk1	14012	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	MEDIUM	Ktype前期GT对应Marina I运动版外廓。	READY
14012_mk2	14012	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期GT对应Marina II四门外廓。	READY
13992_mk1	13992	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype前期覆盖Marina I四门外廓。	READY
13992_mk2	13992	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期HL对应Marina II四门外廓。	READY
6061_mk1	6061	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-TC-01	HIGH	Marina I 1800 TC Coupe外廓。	READY
6061_mk2	6061	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1800-01	MEDIUM	Ktype末期覆盖Marina II 1800 Coupe外廓。	READY
801847	801847	Coupe	MT900 GTR		2	EU-MOSLER-MT900-GTR-COUPE-2D-01	HIGH	MT900 GTR量产公路版外廓。	READY
161913	161913	SUV	E5		5	EU-NAVOR-E5-SUV-5D-01	HIGH	Navor E5五门PHEV SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORRIS-MARINA-III-WAGON-5D-01	4310	1640	1440	Automobile-Catalog 1979 Morris Marina 1300 Estate	https://www.automobile-catalog.com/car/1979/2035640/morris_marina_1300_l_estate.html
EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	4219	1646	1425	Automobile-Catalog 1975 Morris Marina 1.8 Super De Luxe Saloon	https://www.automobile-catalog.com/car/1975/2035055/morris_marina_1_8_super_de_luxe_saloon_automatic.html
EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	4318	1656	1424	Automobile-Catalog 1975 Morris Marina II 1.8 Special 4Door	https://www.automobile-catalog.com/car/1975/2035280/morris_marina_2_1_8_special_4door.html
EU-MORRIS-MARINA-III-SEDAN-4D-01	4280	1640	1420	Automobile-Catalog 1979 Morris Marina 1700 HL 4Door	https://www.automobile-catalog.com/car/1979/2035580/morris_marina_1700_hl_4door.html
EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	4143	1641	1406	Automobile-Catalog 1971 Morris Marina 1.3 Super De Luxe Coupe	https://www.automobile-catalog.com/car/1971/2035130/morris_marina_1_3_super_de_luxe_coupe.html
EU-MORRIS-MARINA-II-COUPE-2D-1300-01	4216	1652	1405	Automobile-Catalog 1976 Morris Marina II 1.3 Super 2Door	https://www.automobile-catalog.com/car/1976/2035340/morris_marina_2_1_3_super_2door.html
EU-MORRIS-MARINA-III-COUPE-2D-01	4200	1640	1410	Automobile-Catalog 1979 Morris Marina 1300 2Door	https://www.automobile-catalog.com/car/1979/2035610/morris_marina_1300_l_2door.html
EU-MORRIS-MARINA-II-WAGON-5D-01	4320	1655	1438	Automobile-Catalog 1976 Morris Marina II 1.8 Super Estate	https://www.automobile-catalog.com/car/1976/2035460/morris_marina_2_1_8_super_estate.html
EU-MORRIS-MARINA-II-SEDAN-4D-1300-01	4293	1656	1419	Automobile-Catalog 1975 Morris Marina II 1.3 Super 4Door	https://www.automobile-catalog.com/car/1975/2035250/morris_marina_2_1_3_super_4door.html
EU-MORRIS-MARINA-II-COUPE-2D-1800-01	4242	1652	1410	Automobile-Catalog 1976 Morris Marina II 1.8 Special 2Door	https://www.automobile-catalog.com/car/1976/2035400/morris_marina_2_1_8_special_2door.html
EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	4219	1646	1419	Automobile-Catalog 1975 Morris Marina 1.8 TC Saloon	https://www.automobile-catalog.com/car/1975/2035070/morris_marina_1_8_tc_saloon.html
EU-MORRIS-MARINA-I-COUPE-2D-TC-01	4143	1641	1400	Automobile-Catalog 1975 Morris Marina 1.8 TC Coupe	https://www.automobile-catalog.com/car/1975/39185/morris_marina_1800_tc_coupe.html
EU-MOSLER-MT900-GTR-COUPE-2D-01	4801	2006	1130	Auto Motor und Sport Mosler MT900 technical data	https://www.auto-motor-und-sport.de/marken-modelle/mosler/mt900/technische-daten/
EU-NAVOR-E5-SUV-5D-01	4760	1865	1710	DFSK official E5 specifications	https://dfsksweden.com/products/dfsk-e5/
```

## 下一步优先处理

1. 闭合 Morgan Four、Plus Four、Roadster 与 Plus Eight 的传统车架年代分支。
2. 处理 Morgan Aero 8、Aero、Aero Supersports、3-Wheeler 与新 Supersport。
3. 解决 Morris Marina 1750 ZA、2600 ZA 和柴油版未闭合分支。
4. 处理 Moskvich 412、Nextem 三车型及 Mitsuoka Himiko。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1971/2035130/morris_marina_1_3_super_de_luxe_coupe.html?utm_source=chatgpt.com "1971 Morris Marina 1.3 Super De Luxe Coupe Specs Review (42 kW / 57 PS / 56 hp) (since April 1971 for Europe )"
[2]: https://www.auto-motor-und-sport.de/marken-modelle/mosler/mt900/technische-daten/?utm_source=chatgpt.com "Mosler MT900 ► Technische Daten zu allen Motorisierungen"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Morgan 现代车型簇，包括 3 Wheeler、Aero Coupe、Aero 8、Aero Supersports、4/4、Plus 4、Roadster、复产 Plus 8 和 2025 Supersport。
* Aero 8 的 Ktype `17932` 覆盖 Series 2 与 Series 3 两种车身前脸外廓，拆分为两个派生映射；两者三维相同但物理车身边界不同。([维基百科][1])
* 4/4、Plus 4、Roadster 和复产 Plus 8 分别按 1630、1720、1720、1751 mm 的不含后视镜宽度独立建组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：77
* READY 映射：91
* PENDING Ktype：23
* 已确认尺寸组：57
* 本轮新增映射：17
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106391	106391	Convertible	3 Wheeler			EU-MORGAN-3-WHEELER-2011-CONVERTIBLE-01	HIGH	开放式三轮车身，无传统车门。	READY
54920	54920	Coupe	Aero Coupe		2	EU-MORGAN-AERO-COUPE-COUPE-2D-01	HIGH	Aero固定车顶Coupe外廓。	READY
14809	14809	Convertible	Aero 8 Series 1		2	EU-MORGAN-AERO-8-SERIES-1-CONVERTIBLE-2D-01	HIGH	Series 1初期车身外廓。	READY
17932_s2	17932	Convertible	Aero 8 Series 2		2	EU-MORGAN-AERO-8-SERIES-2-CONVERTIBLE-2D-01	MEDIUM	Ktype覆盖Series 2车身分支。	READY
17932_s3	17932	Convertible	Aero 8 Series 3		2	EU-MORGAN-AERO-8-SERIES-3-CONVERTIBLE-2D-01	MEDIUM	Ktype覆盖Series 3改款车身分支。	READY
11824	11824	Convertible	Aero 8 Series 4		2	EU-MORGAN-AERO-8-SERIES-4-CONVERTIBLE-2D-01	HIGH	Series 4 4.8升车身外廓。	READY
34847	34847	Convertible	Aero Supersports		2	EU-MORGAN-AERO-SUPERSPORTS-CONVERTIBLE-2D-01	HIGH	可拆卸车顶Supersports外廓。	READY
126175	126175	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	MEDIUM	2.0版本对应Plus 4双座外廓。	READY
124209	124209	Convertible	4/4		2	EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	HIGH	1.6 Sigma双座4/4外廓。	READY
54918	54918	Convertible	Plus 8 (2012)		2	EU-MORGAN-PLUS-8-2012-CONVERTIBLE-2D-01	MEDIUM	复产BMW 4.8 V8车身外廓。	READY
54919	54919	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	Plus 4双座传统车身外廓。	READY
108942	108942	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	2014至2020版本沿用相同双座外廓。	READY
108647	108647	Convertible	Roadster 3.7		2	EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	HIGH	3.7 V6双座Roadster外廓。	READY
34844	34844	Convertible	4/4		2	EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	MEDIUM	VariantName明确对应1.6升4/4车身。	READY
34845	34845	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	VariantName明确对应2.0升Plus 4车身。	READY
34846	34846	Convertible	Roadster 3.0		2	EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	HIGH	3.0 V6双座Roadster外廓。	READY
161344	161344	Convertible	Supersport		2	EU-MORGAN-SUPERSPORT-2025-CONVERTIBLE-2D-01	HIGH	2025 CXV平台Supersport外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORGAN-3-WHEELER-2011-CONVERTIBLE-01	3225	1720	1000	Automobile-Catalog 2014 Morgan 3 Wheeler	https://www.automobile-catalog.com/car/2014/2039615/morgan_3_wheeler.html
EU-MORGAN-AERO-COUPE-COUPE-2D-01	4147	1751	1248	CarsGuide Morgan Aero Coupe dimensions	https://www.carsguide.com.au/morgan/aero-coupe/car-dimensions
EU-MORGAN-AERO-8-SERIES-1-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2001 Morgan Aero 8	https://www.automobile-catalog.com/car/2001/2039120/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-2-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2004 Morgan Aero 8	https://www.automobile-catalog.com/car/2004/2039150/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-3-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2007 Morgan Aero 8	https://www.automobile-catalog.com/car/2007/2039255/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-4-CONVERTIBLE-2D-01	4145	1770	1200	Automobile-Catalog 2008 Morgan Aero 8	https://www.automobile-catalog.com/car/2008/2039270/morgan_aero_8.html
EU-MORGAN-AERO-SUPERSPORTS-CONVERTIBLE-2D-01	4147	1751	1248	Automobile-Catalog 2010 Morgan Aero Supersports	https://www.automobile-catalog.com/car/2010/2039390/morgan_aero_supersports_automatic.html
EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	4010	1630	1220	Automobile-Catalog 2009 Morgan 4/4 Sport	https://www.automobile-catalog.com/car/2009/2039345/morgan_44_sport.html
EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	4010	1720	1220	Automobile-Catalog 2009 Morgan Plus 4	https://www.automobile-catalog.com/car/2009/2039195/morgan_plus_4.html
EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	4010	1720	1220	Automobile-Catalog 2006 Morgan Roadster	https://www.automobile-catalog.com/car/2006/2039165/morgan_roadster.html
EU-MORGAN-PLUS-8-2012-CONVERTIBLE-2D-01	4010	1751	1220	Automobile-Catalog 2014 Morgan Plus 8	https://www.automobile-catalog.com/car/2014/2039525/morgan_plus_8.html
EU-MORGAN-SUPERSPORT-2025-CONVERTIBLE-2D-01	4110	1805	1290	Carfolio 2025 Morgan Supersport; Autocar Morgan Supersport review	https://www.carfolio.com/morgan-supersport-827101; https://www.autocar.co.uk/car-review/morgan/supersport
```

## 下一步优先处理

1. 闭合 Morgan 4/4、Plus 4 与 Plus 8 的 1968—2005 年传统车架年代分支。
2. 处理 Mitsuoka Himiko 两个 Ktype。
3. 解决 Morris Marina 1750、2600 和两个早期柴油分支。
4. 闭合 Moskvich 412 与 Nextem Humpback、Minke、Orca。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Morgan_Aero_8?utm_source=chatgpt.com "Morgan Aero 8"
[2]: https://www.automobile-catalog.com/car/2009/2039345/morgan_44_sport.html?utm_source=chatgpt.com "2009 Morgan 4/4 Sport Specs Review (82 kW / 112 PS ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合历史 Morgan 4/4 的窄体与宽体外廓：早期车身为 `3658×1422×1295 mm`，1987 年后车身为 `3886×1500×1290 mm`。([汽车目录][1])
* 已闭合历史 Morgan Plus 4 的窄体与宽体外廓：1992 年 11 月前为 `3886×1500×1270 mm`，之后为 `3962×1626×1290 mm`。([汽车目录][2])
* Moskvich 412 暂未落盘：现有资料出现 `4090 mm` 与 `4250 mm` 两种车长，且输入生产区间与生产厂边界尚未闭合。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：86
* READY 映射：104
* PENDING Ktype：14
* 已确认尺寸组：61
* 本轮新增映射：13
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13639	13639	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	HIGH	早期窄体双座外廓。	READY
13640_narrowbody	13640	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1987年前窄体分支。	READY
13640_widebody	13640	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1987年后宽体分支。	READY
13643_narrowbody	13643	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1987年前窄体分支。	READY
13643_widebody	13643	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1987年后宽体分支。	READY
13642	13642	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	HIGH	后期宽体双座外廓。	READY
13644	13644	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	HIGH	后期1.8升宽体外廓。	READY
13658	13658	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	HIGH	1992年11月后宽体外廓。	READY
13659_narrowbody	13659	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月前窄体分支。	READY
13659_widebody	13659	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月后宽体分支。	READY
13661	13661	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	HIGH	早期窄体双座外廓。	READY
13664_narrowbody	13664	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月前窄体分支。	READY
13664_widebody	13664	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月后宽体分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	3658	1422	1295	Automobile-Catalog 1968 Morgan 4/4 1600 2-seater; Automobile-Catalog 1982 Morgan 4/4 1600 2-seater	https://www.automobile-catalog.com/car/1968/2038355/morgan_44_1600_2_seater.html; https://www.automobile-catalog.com/car/1982/2038520/morgan_44_1600_2_seater.html
EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	3886	1500	1290	Automobile-Catalog 1987 Morgan 4/4 1600 two-seater; Automobile-Catalog 1995 Morgan 4/4 1800	https://www.automobile-catalog.com/car/1987/2038700/morgan_44_1600_two_seater.html; https://www.automobile-catalog.com/car/1995/2038955/morgan_44_1800.html
EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	3886	1500	1270	Automobile-Catalog 1988 Morgan Plus Four two-seater; Automobile-Catalog 1991 Morgan Plus Four two-seater	https://www.automobile-catalog.com/car/1988/2038730/morgan_plus_four_two_seater.html; https://www.automobile-catalog.com/car/1991/2038730/morgan_plus_four_two_seater.html
EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	3962	1626	1290	Automobile-Catalog 1992 Morgan Plus Four two-seater; Automobile-Catalog 1993 Morgan Plus Four two-seater	https://www.automobile-catalog.com/car/1992/2038925/morgan_plus_four_two_seater.html; https://www.automobile-catalog.com/car/1993/2038925/morgan_plus_four_two_seater.html
```

## 下一步优先处理

1. 闭合 Morgan Plus Eight 的早期窄体、3.9 升和后期宽体分支。
2. 确认 Mitsuoka Himiko 两个 Ktype 与软顶、硬顶高度分支的对应关系。
3. 解决 Morris Marina 1750 ZA、2600 ZA 和两个柴油 Ktype。
4. 解决 Moskvich 412 生产厂边界，以及 Nextem 三车型的不含后视镜宽度口径。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1968/2038355/morgan_44_1600_2_seater.html?utm_source=chatgpt.com "1968 Morgan 4/4 1600 2 Seater Specs Review (52 kW / 71 PS / 70 hp) (since February 1968 for Europe )"
[2]: https://www.automobile-catalog.com/car/1988/2038730/morgan_plus_four_two_seater.html?utm_source=chatgpt.com "1988 Morgan Plus Four Two Seater Specs Review (103 kW / 140 PS / 138 hp) (since early-year 1988 for Europe )"
[3]: https://www.automobile-catalog.com/car/1978/1293830/izh_412_ie.html?utm_source=chatgpt.com "1978 Izh-Moskvich 412 IE (man. 4) (model for Europe ) car ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 完成 Morgan Plus Eight 的 1984、1990 与 1996 宽体三个分支；三组宽度均明确为不含后视镜口径。([汽车目录][1])
* 完成 Mitsuoka Himiko 两个 Ktype：`34840` 为 125 kW 分支，`34841` 为 119 kW 分支；按对应车高拆为两个尺寸组。([Alkatrészek][2])
* 完成 Marina 2600 ZA、Marina I 1500 Diesel、Izh-Moskvich 412 IE 与 Nextem Minke；其中 Marina I 柴油版复用既有 Sedan 尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：95
* READY 映射：113
* PENDING Ktype：5
* 已确认尺寸组：69
* 本轮新增/修改映射：9
* 本轮首次创建尺寸组：8
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13666	13666	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1984-CONVERTIBLE-2D-01	HIGH	3.5 EFI后期传统车身外廓。	READY
13667	13667	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1990-CONVERTIBLE-2D-01	HIGH	3.9升传统车身外廓。	READY
13668	13668	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1996-CONVERTIBLE-2D-WIDEBODY-01	HIGH	4.6升宽体外廓。	READY
34840	34840	Convertible	Himiko I	NCEC	2	EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-MT-01	MEDIUM	125 kW手动挡低车高分支。	READY
34841	34841	Convertible	Himiko I	NCEC	2	EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-AT-01	MEDIUM	119 kW自动挡高车高分支。	READY
13993	13993	Sedan	Marina II		4	EU-MORRIS-MARINA-II-SEDAN-4D-2600-ZA-01	MEDIUM	南非2600六缸四门外廓。	READY
14010	14010	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Marina I四门柴油版不改变外廓。	READY
14032	14032	Sedan	412 IE (Izh)		4	EU-MOSKVICH-412-IE-SEDAN-4D-01	MEDIUM	生产区间跨1982年外观改款，三维不变。	READY
152873	152873	Van	Minke I			EU-NEXTEM-MINKE-I-VAN-01	HIGH	封闭厢式车单一外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORGAN-PLUS-8-1984-CONVERTIBLE-2D-01	3734	1575	1321	Automobile-Catalog 1984 Morgan Plus 8 PI	https://www.automobile-catalog.com/car/1984/2038685/morgan_plus_8_pi.html
EU-MORGAN-PLUS-8-1990-CONVERTIBLE-2D-01	3962	1600	1219	Automobile-Catalog 1990 Morgan Plus 8	https://www.automobile-catalog.com/car/1990/2038760/morgan_plus_8.html
EU-MORGAN-PLUS-8-1996-CONVERTIBLE-2D-WIDEBODY-01	3988	1753	1321	Automobile-Catalog 1996 Morgan Plus 8 4.6	https://www.automobile-catalog.com/car/1996/2039090/morgan_plus_8_4_6.html
EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-MT-01	4575	1725	1245	Goo-net Exchange Mitsuoka Himiko S Standard	https://www.goo-net-exchange.com/catalog/MITSUOKA__HIMIKO/10057841/
EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-AT-01	4575	1725	1255	Drive.Place Mitsuoka Himiko I 2.0 AT	https://mitsuoka.drive.place/himiko/i/group_roadster/413175
EU-MORRIS-MARINA-II-SEDAN-4D-2600-ZA-01	4220	1640	1390	Carfolio 1977 Leyland Marina 2600	https://www.carfolio.com/leyland-marina-2600-114455
EU-MOSKVICH-412-IE-SEDAN-4D-01	4120	1550	1480	Automobile-Catalog 1988 Izh-Moskvich 028-412 IE	https://www.automobile-catalog.com/car/1988/1293860/izh_412_ie.html
EU-NEXTEM-MINKE-I-VAN-01	4855	1730	1985	Nextem Minke e-drive Center	https://edrivecenter.de/e-fahrzeuge/e-cargo/nextem-minke
```

## 下一步优先处理

1. 拆分 Ktype `13665` 覆盖的早期窄体与后期加宽 Plus Eight 外廓。
2. 闭合 Marina `13991` 的 1750 ZA 分支，以及 `13990` 跨 Marina II／III 的柴油分支。
3. 确认 Nextem Humpback `152872` 与 Orca `152871` 的具体底盘长度和货箱配置；现有资料均显示多个物理外廓，暂不创建猜测性尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1984/2038685/morgan_plus_8_pi.html?utm_source=chatgpt.com "1984 Morgan Plus 8 PI Specs Review (142 kW ..."
[2]: https://alkatreszek.hu/termekek/auto_erzekelok_jeladok_kapcsolok_elektronika/viz_erzekelo/mitsuoka/himiko/himiko_kabrio_2008_09?utm_source=chatgpt.com "Vásároljon MITSUOKA HIMIKO Kabrió 2008/09 Víz érzékelő autóalkatrészeket - Kovács"
[3]: https://www.auto-data.net/en/morris-marina-ii-2600-za-110hp-16401?utm_source=chatgpt.com "Morris Marina II 2600 (ZA) (110 Hp) /Sedan 1975"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11501-11600_ktype_dimension_mapping_final.tsv
- left18448_11501-11600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 剩余 5 个 Ktype 已全部闭合。Morgan Plus Eight Ktype `13665` 按 1968—1972、1972—1976、1976 年后三种车宽外廓拆分。([汽车目录][1])
* Nextem Orca 按官方标准长度 `4000 mm` 与可选加长 `4300 mm` 拆分；Humpback 采用官方标准平台外廓。([Nextemev][2])
* 已完成固定表头、唯一主键、100 个输入 Ktype 覆盖、映射引用闭合、尺寸与来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：121
* PENDING：0
* DIMENSION_GROUP：74
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 孤立尺寸组：0
* 缺失引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3379_prefl	3379	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	MEDIUM	Ktype覆盖改款前4WD外廓分支。	READY
3379_facelift	3379	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	MEDIUM	Ktype覆盖改款后4WD外廓分支。	READY
10103	10103	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	前驱低顶物理外廓。	READY
16166	16166	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	前驱低顶物理外廓。	READY
10359	10359	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	四驱高顶物理外廓。	READY
16167	16167	MPV	Space Wagon III		5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	四驱高顶物理外廓。	READY
143202	143202	Van	Space Wagon I		5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	MEDIUM	商用Van与同代前驱车身共用外廓。	READY
143203	143203	Van	Space Wagon I	D09V	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D09V商用柴油Van外廓。	READY
3372	3372	Coupe	Starion	A183A	3	EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	HIGH	A183A窄体外廓。	READY
3373	3373	Coupe	Starion	A183A	3	EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	HIGH	A183A中期改款仍使用相同窄体外廓。	READY
3374	3374	Coupe	Starion	A187A	3	EU-MITSUBISHI-STARION-A187A-COUPE-3D-WIDEBODY-01	HIGH	A187A宽体外廓。	READY
3316	3316	Sedan	Tredia	A211	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A211四门前驱外廓。	READY
3318	3318	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212四门前驱外廓。	READY
3319	3319	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212涡轮版本不改变外廓。	READY
3320	3320	Sedan	Tredia	A212	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A212涡轮版本不改变外廓。	READY
3321	3321	Sedan	Tredia	A215	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	HIGH	A215四门前驱外廓。	READY
58729	58729	Sedan	Tredia	A215G	4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	HIGH	A215G四驱车身高度增加。	READY
59323	59323	Sedan	Tredia		4	EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	MEDIUM	四驱版本采用同一增高外廓。	READY
34840	34840	Convertible	Himiko I	NCEC	2	EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-MT-01	MEDIUM	125 kW手动挡低车高分支。	READY
34841	34841	Convertible	Himiko I	NCEC	2	EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-AT-01	MEDIUM	119 kW自动挡高车高分支。	READY
34839	34839	Coupe	Orochi	MSP1	2	EU-MITSUOKA-OROCHI-MSP1-COUPE-2D-01	HIGH	MSP1量产双门车身。	READY
160704	160704	Van	Bento		2	EU-MOBILIZE-BENTO-VAN-2D-01	MEDIUM	单座封闭货箱版物理外廓。	READY
160810	160810	Hatchback	Duo		2	EU-MOBILIZE-DUO-HATCHBACK-2D-01	HIGH	Duo双座微型车外廓。	READY
160811	160811	Hatchback	Duo		2	EU-MOBILIZE-DUO-HATCHBACK-2D-01	HIGH	Duo动力版本不改变外廓。	READY
106391	106391	Convertible	3 Wheeler			EU-MORGAN-3-WHEELER-2011-CONVERTIBLE-01	HIGH	开放式三轮车身，无传统车门。	READY
54920	54920	Coupe	Aero Coupe		2	EU-MORGAN-AERO-COUPE-COUPE-2D-01	HIGH	Aero固定车顶Coupe外廓。	READY
14809	14809	Convertible	Aero 8 Series 1		2	EU-MORGAN-AERO-8-SERIES-1-CONVERTIBLE-2D-01	HIGH	Series 1初期车身外廓。	READY
17932_s2	17932	Convertible	Aero 8 Series 2		2	EU-MORGAN-AERO-8-SERIES-2-CONVERTIBLE-2D-01	MEDIUM	Ktype覆盖Series 2车身分支。	READY
17932_s3	17932	Convertible	Aero 8 Series 3		2	EU-MORGAN-AERO-8-SERIES-3-CONVERTIBLE-2D-01	MEDIUM	Ktype覆盖Series 3改款车身分支。	READY
11824	11824	Convertible	Aero 8 Series 4		2	EU-MORGAN-AERO-8-SERIES-4-CONVERTIBLE-2D-01	HIGH	Series 4 4.8升车身外廓。	READY
34847	34847	Convertible	Aero Supersports		2	EU-MORGAN-AERO-SUPERSPORTS-CONVERTIBLE-2D-01	HIGH	可拆卸车顶Supersports外廓。	READY
13639	13639	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	HIGH	早期窄体双座外廓。	READY
126175	126175	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	MEDIUM	2.0版本对应Plus 4双座外廓。	READY
13640_narrowbody	13640	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1987年前窄体分支。	READY
13640_widebody	13640	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1987年后宽体分支。	READY
13643_narrowbody	13643	Convertible	4/4		2	EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1987年前窄体分支。	READY
13643_widebody	13643	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1987年后宽体分支。	READY
124209	124209	Convertible	4/4		2	EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	HIGH	1.6 Sigma双座4/4外廓。	READY
13642	13642	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	HIGH	后期宽体双座外廓。	READY
13644	13644	Convertible	4/4		2	EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	HIGH	后期1.8升宽体外廓。	READY
13665_narrowbody	13665	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1968-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype覆盖1968至1972年早期窄体分支。	READY
13665_midbody	13665	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1972-CONVERTIBLE-2D-MIDBODY-01	MEDIUM	Ktype覆盖1972至1976年中期加宽分支。	READY
13665_widebody	13665	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1984-CONVERTIBLE-2D-01	MEDIUM	Ktype覆盖1976年后宽体分支。	READY
13667	13667	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1990-CONVERTIBLE-2D-01	HIGH	3.9升传统车身外廓。	READY
13668	13668	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1996-CONVERTIBLE-2D-WIDEBODY-01	HIGH	4.6升宽体外廓。	READY
13666	13666	Convertible	Plus 8		2	EU-MORGAN-PLUS-8-1984-CONVERTIBLE-2D-01	HIGH	3.5 EFI后期传统车身外廓。	READY
54918	54918	Convertible	Plus 8 (2012)		2	EU-MORGAN-PLUS-8-2012-CONVERTIBLE-2D-01	MEDIUM	复产BMW 4.8 V8车身外廓。	READY
13658	13658	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	HIGH	1992年11月后宽体外廓。	READY
13659_narrowbody	13659	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月前窄体分支。	READY
13659_widebody	13659	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月后宽体分支。	READY
13661	13661	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	HIGH	早期窄体双座外廓。	READY
13664_narrowbody	13664	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月前窄体分支。	READY
13664_widebody	13664	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Ktype生产区间覆盖1992年11月后宽体分支。	READY
54919	54919	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	Plus 4双座传统车身外廓。	READY
108942	108942	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	2014至2020版本沿用相同双座外廓。	READY
108647	108647	Convertible	Roadster 3.7		2	EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	HIGH	3.7 V6双座Roadster外廓。	READY
34844	34844	Convertible	4/4		2	EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	MEDIUM	VariantName明确对应1.6升4/4车身。	READY
34845	34845	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	HIGH	VariantName明确对应2.0升Plus 4车身。	READY
34846	34846	Convertible	Roadster 3.0		2	EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	HIGH	3.0 V6双座Roadster外廓。	READY
161344	161344	Convertible	Supersport		2	EU-MORGAN-SUPERSPORT-2025-CONVERTIBLE-2D-01	HIGH	2025 CXV平台Supersport外廓。	READY
13849	13849	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Marina III五门Wagon外廓。	READY
13257	13257	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Marina III五门Wagon外廓。	READY
6057_mk1	6057	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype覆盖Marina I标准四门外廓。	READY
6057_mk2	6057	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype覆盖Marina II四门外廓。	READY
6057_mk3	6057	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	MEDIUM	Ktype生产区间延伸至Marina III外廓。	READY
6053	6053	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	HIGH	Marina I标准四门外廓。	READY
6054_mk1	6054	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	HIGH	Marina I双门Coupe外廓。	READY
6054_mk2	6054	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1300-01	HIGH	Marina II 1300双门外廓。	READY
6054_mk3	6054	Coupe	Marina III	ADO28	2	EU-MORRIS-MARINA-III-COUPE-2D-01	HIGH	Marina III双门Coupe外廓。	READY
14001_mk2	14001	Wagon	Marina II	ADO28	5	EU-MORRIS-MARINA-II-WAGON-5D-01	HIGH	Ktype前期对应Marina II Wagon。	READY
14001_mk3	14001	Wagon	Marina III	ADO28	5	EU-MORRIS-MARINA-III-WAGON-5D-01	HIGH	Ktype后期对应Marina III Wagon。	READY
14009	14009	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1300-01	HIGH	Marina II 1300四门外廓。	READY
13991	13991	Sedan	Marina II		4	EU-MORRIS-MARINA-II-SEDAN-4D-2600-ZA-01	MEDIUM	南非1750 ZA与同市场四门Marina外廓共用车身。	READY
6059_mk1	6059	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	MEDIUM	Marina I标准1800 Coupe外廓。	READY
6059_mk2	6059	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1800-01	MEDIUM	Ktype末期覆盖Marina II 1800 Coupe外廓。	READY
13848	13848	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	HIGH	Marina II 1800四门外廓。	READY
14003	14003	Wagon	Marina II	ADO28	5	EU-MORRIS-MARINA-II-WAGON-5D-01	HIGH	Marina II 1800五门Wagon外廓。	READY
14011_mk1	14011	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype前期对应Marina I四门外廓。	READY
14011_mk2	14011	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期对应Marina II四门外廓。	READY
13993	13993	Sedan	Marina II		4	EU-MORRIS-MARINA-II-SEDAN-4D-2600-ZA-01	MEDIUM	南非2600六缸四门外廓。	READY
14000	14000	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	HIGH	Marina III 1300四门外廓。	READY
13996	13996	Sedan	Marina III	ADO28	4	EU-MORRIS-MARINA-III-SEDAN-4D-01	HIGH	Marina III柴油版采用同一四门外廓。	READY
6058	6058	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	HIGH	Marina I 1.8 TC四门高度分支。	READY
13990	13990	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	柴油动力不改变Marina II四门外廓。	READY
14010	14010	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Marina I四门柴油版不改变外廓。	READY
14012_mk1	14012	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	MEDIUM	Ktype前期GT对应Marina I运动版外廓。	READY
14012_mk2	14012	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期GT对应Marina II四门外廓。	READY
13992_mk1	13992	Sedan	Marina I	ADO28	4	EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	MEDIUM	Ktype前期覆盖Marina I四门外廓。	READY
13992_mk2	13992	Sedan	Marina II	ADO28	4	EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	MEDIUM	Ktype后期HL对应Marina II四门外廓。	READY
6061_mk1	6061	Coupe	Marina I	ADO28	2	EU-MORRIS-MARINA-I-COUPE-2D-TC-01	HIGH	Marina I 1800 TC Coupe外廓。	READY
6061_mk2	6061	Coupe	Marina II	ADO28	2	EU-MORRIS-MARINA-II-COUPE-2D-1800-01	MEDIUM	Ktype末期覆盖Marina II 1800 Coupe外廓。	READY
14032	14032	Sedan	412 IE (Izh)		4	EU-MOSKVICH-412-IE-SEDAN-4D-01	MEDIUM	生产区间跨1982年外观改款，三维不变。	READY
801847	801847	Coupe	MT900 GTR		2	EU-MOSLER-MT900-GTR-COUPE-2D-01	HIGH	MT900 GTR量产公路版外廓。	READY
161913	161913	SUV	E5		5	EU-NAVOR-E5-SUV-5D-01	HIGH	Navor E5五门PHEV SUV外廓。	READY
152872	152872	Pickup	Humpback I		2	EU-NEXTEM-HUMPBACK-I-PLATFORM-2D-01	MEDIUM	标准Humpback平台/底盘外廓。	READY
152873	152873	Van	Minke I			EU-NEXTEM-MINKE-I-VAN-01	HIGH	封闭厢式车单一外廓。	READY
152871_std	152871	Pickup	Orca I		2	EU-NEXTEM-ORCA-I-PLATFORM-2D-STD-01	MEDIUM	Ktype覆盖标准长度平台分支。	READY
152871_lwb	152871	Pickup	Orca I		2	EU-NEXTEM-ORCA-I-PLATFORM-2D-LWB-01	MEDIUM	Ktype覆盖可选加长平台分支。	READY
156227	156227	SUV	EC6 II		5	EU-NIO-EC6-II-SUV-5D-01	HIGH	第二代EC6轿跑SUV外廓。	READY
154975	154975	SUV	EL6 (ES6 II)		5	EU-NIO-ES6-II-SUV-5D-01	HIGH	欧洲EL6对应第二代ES6物理车身。	READY
147934	147934	SUV	EL7 (ES7)		5	EU-NIO-ES7-SUV-5D-01	HIGH	EL7标准物理外廓。	READY
150465	150465	SUV	EL7 (ES7)		5	EU-NIO-ES7-SUV-5D-01	HIGH	重复动力条目复用EL7外廓。	READY
159371	159371	SUV	EL8 (ES8 II)		5	EU-NIO-ES8-II-SUV-5D-01	HIGH	第二代EL8六座SUV外廓。	READY
151711	151711	SUV	EL8 (ES8 II)		5	EU-NIO-ES8-II-SUV-5D-01	HIGH	重复动力条目复用EL8外廓。	READY
155115	155115	SUV	ES6 II		5	EU-NIO-ES6-II-SUV-5D-01	HIGH	中国市场ES6与欧洲EL6为相同第二代车身。	READY
146217	146217	Sedan	ET5		4	EU-NIO-ET5-SEDAN-4D-01	HIGH	ET5四门轿车外廓。	READY
154974	154974	Wagon	ET5		5	EU-NIO-ET5-WAGON-5D-01	HIGH	ET5 Touring旅行车外廓。	READY
143290	143290	Sedan	ET7		4	EU-NIO-ET7-SEDAN-4D-01	HIGH	ET7四门轿车外廓。	READY
46220	46220	Coupe	S13	S13	2	EU-NISSAN-240SX-S13-COUPE-2D-01	MEDIUM	2.4L S13双门外廓。	READY
12459	12459	Coupe	S14	S14	2	EU-NISSAN-200SX-S14-COUPE-2D-01	HIGH	S14双门Coupe外廓。	READY
109605	109605	Coupe	S13	S13	2	EU-NISSAN-240SX-S13-COUPE-2D-01	HIGH	S13双门Coupe外廓。	READY
58681	58681	Coupe	S30	HLS30	3	EU-NISSAN-240Z-S30-COUPE-3D-01	HIGH	S30双座掀背外廓。	READY
58682	58682	Coupe	S30		3	EU-NISSAN-260Z-S30-COUPE-3D-2PLUS2-01	HIGH	S30长轴距2+2外廓。	READY
17435	17435	Coupe	350Z	Z33	3	EU-NISSAN-350Z-Z33-COUPE-3D-01	HIGH	Z33三门Coupe外廓。	READY
18277	18277	Convertible	350Z Roadster	HZ33	2	EU-NISSAN-350Z-HZ33-CONVERTIBLE-2D-01	HIGH	HZ33双门敞篷外廓。	READY
106194_prefl	106194	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-PREFL-01	HIGH	初期标准Coupe保险杠外廓。	READY
106194_facelift	106194	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-FACELIFT-01	HIGH	后期标准Coupe保险杠外廓。	READY
58978_prefl	58978	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-PREFL-01	HIGH	初期NISMO空气动力套件外廓。	READY
58978_facelift	58978	Coupe	370Z Z34	Z34	3	EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-FACELIFT-01	HIGH	后期NISMO空气动力套件外廓。	READY
34552	34552	Convertible	370Z Z34	HZ34	2	EU-NISSAN-370Z-HZ34-CONVERTIBLE-2D-01	HIGH	HZ34双门敞篷外廓。	READY
58856	58856	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-01	MEDIUM	N15四门Sedan外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_11501-11600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	4445	1640	1580	Automobile-Catalog 1986 Mitsubishi Space Wagon 2000 GLX 4WD	https://www.automobile-catalog.com/car/1986/51665/mitsubishi_space_wagon_2_0_4wd.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	4445	1640	1575	Automobile-Catalog 1990 Mitsubishi Space Wagon 2000 GLXi 4WD	https://www.automobile-catalog.com/car/1990/1928825/mitsubishi_space_wagon_2000_glxi_4wd.html
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	4600	1775	1650	Auto-Data Mitsubishi Space Wagon III 2.4 GDI	https://www.auto-data.net/en/mitsubishi-space-wagon-iii-2.4-gdi-150hp-15595
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	4600	1775	1690	Automobile-Catalog 1999 Mitsubishi Space Wagon 2.4 GDI 4WD	https://www.automobile-catalog.com/car/1999/2005145/mitsubishi_space_wagon_2_4_gdi_4wd.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	4295	1640	1525	Automobile-Catalog 1986 Mitsubishi Space Wagon 1800 GLX	https://www.automobile-catalog.com/car/1986/1928300/mitsubishi_space_wagon_1800_glx_automatic.html
EU-MITSUBISHI-STARION-A183A-COUPE-3D-NARROWBODY-01	4430	1705	1315	Automobile-Catalog 1985 Mitsubishi Starion 2000 Turbo	https://www.automobile-catalog.com/car/1985/57185/mitsubishi_starion_turbo.html
EU-MITSUBISHI-STARION-A187A-COUPE-3D-WIDEBODY-01	4430	1745	1315	Automobile-Catalog 1988 Mitsubishi Starion 2600 Turbo catalyst	https://www.automobile-catalog.com/car/1988/1929155/mitsubishi_starion_2600_turbo_cat.html
EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-FWD-01	4280	1660	1370	Auto-Data Mitsubishi Tredia 1400 GLX; Automobile-Catalog Mitsubishi Tredia 1600 Turbo; Automobile-Catalog Mitsubishi Tredia 1800 GLS	https://www.auto-data.net/en/mitsubishi-tredia-a21-1400-glx-a211-70hp-15816; https://www.automobile-catalog.com/car/1982/1917125/mitsubishi_tredia_1600_turbo.html; https://www.automobile-catalog.com/car/1984/1917155/mitsubishi_tredia_1800_gls.html
EU-MITSUBISHI-TREDIA-A21-SEDAN-4D-4WD-01	4280	1660	1415	Automobile-Catalog Mitsubishi Tredia 1800 4WD GLS; Automobile-Catalog Mitsubishi Tredia 2000 4WD catalyst	https://www.automobile-catalog.com/car/1984/1917200/mitsubishi_tredia_1800_4wd_gls.html; https://www.automobile-catalog.com/car/1987/1917275/mitsubishi_tredia_2000_4wd_cat.html
EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-MT-01	4575	1725	1245	Goo-net Exchange Mitsuoka Himiko S Standard	https://www.goo-net-exchange.com/catalog/MITSUOKA__HIMIKO/10057841/
EU-MITSUOKA-HIMIKO-I-NCEC-CONVERTIBLE-2D-AT-01	4575	1725	1255	Drive.Place Mitsuoka Himiko I 2.0 AT	https://mitsuoka.drive.place/himiko/i/group_roadster/413175
EU-MITSUOKA-OROCHI-MSP1-COUPE-2D-01	4560	2035	1180	TCV Mitsuoka Orochi specifications; Carfolio Mitsuoka Orochi	https://www.tc-v.com/specifications/mitsuoka/orochi/; https://www.carfolio.com/mitsuoka-orochi-293271
EU-MOBILIZE-BENTO-VAN-2D-01	2540	1300	1570	Mobilize official Bento product article; VanReviewer Mobilize Bento dimensions	https://www.mobilize.com/en/wearemobilizers/mobilize-bento-the-small-van-thats-changing-the-game/; https://vanreviewer.co.uk/renault/mobilize-bento/dimensions/5894/
EU-MOBILIZE-DUO-HATCHBACK-2D-01	2430	1300	1460	Automobile Dimension Mobilize Duo	https://www.automobiledimension.com/model/mobilize/duo
EU-MORGAN-3-WHEELER-2011-CONVERTIBLE-01	3225	1720	1000	Automobile-Catalog 2014 Morgan 3 Wheeler	https://www.automobile-catalog.com/car/2014/2039615/morgan_3_wheeler.html
EU-MORGAN-AERO-COUPE-COUPE-2D-01	4147	1751	1248	CarsGuide Morgan Aero Coupe dimensions	https://www.carsguide.com.au/morgan/aero-coupe/car-dimensions
EU-MORGAN-AERO-8-SERIES-1-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2001 Morgan Aero 8	https://www.automobile-catalog.com/car/2001/2039120/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-2-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2004 Morgan Aero 8	https://www.automobile-catalog.com/car/2004/2039150/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-3-CONVERTIBLE-2D-01	4120	1770	1200	Automobile-Catalog 2007 Morgan Aero 8	https://www.automobile-catalog.com/car/2007/2039255/morgan_aero_8.html
EU-MORGAN-AERO-8-SERIES-4-CONVERTIBLE-2D-01	4145	1770	1200	Automobile-Catalog 2008 Morgan Aero 8	https://www.automobile-catalog.com/car/2008/2039270/morgan_aero_8.html
EU-MORGAN-AERO-SUPERSPORTS-CONVERTIBLE-2D-01	4147	1751	1248	Automobile-Catalog 2010 Morgan Aero Supersports	https://www.automobile-catalog.com/car/2010/2039390/morgan_aero_supersports_automatic.html
EU-MORGAN-4-4-1968-CONVERTIBLE-2D-NARROWBODY-01	3658	1422	1295	Automobile-Catalog 1968 Morgan 4/4 1600 2-seater; Automobile-Catalog 1982 Morgan 4/4 1600 2-seater	https://www.automobile-catalog.com/car/1968/2038355/morgan_44_1600_2_seater.html; https://www.automobile-catalog.com/car/1982/2038520/morgan_44_1600_2_seater.html
EU-MORGAN-PLUS-4-2004-CONVERTIBLE-2D-01	4010	1720	1220	Automobile-Catalog 2009 Morgan Plus 4	https://www.automobile-catalog.com/car/2009/2039195/morgan_plus_4.html
EU-MORGAN-4-4-1987-CONVERTIBLE-2D-WIDEBODY-01	3886	1500	1290	Automobile-Catalog 1987 Morgan 4/4 1600 two-seater; Automobile-Catalog 1995 Morgan 4/4 1800	https://www.automobile-catalog.com/car/1987/2038700/morgan_44_1600_two_seater.html; https://www.automobile-catalog.com/car/1995/2038955/morgan_44_1800.html
EU-MORGAN-4-4-2009-CONVERTIBLE-2D-01	4010	1630	1220	Automobile-Catalog 2009 Morgan 4/4 Sport	https://www.automobile-catalog.com/car/2009/2039345/morgan_44_sport.html
EU-MORGAN-PLUS-8-1968-CONVERTIBLE-2D-NARROWBODY-01	3708	1460	1321	Automobile-Catalog 1968 Morgan Plus 8	https://www.automobile-catalog.com/car/1968/2038400/morgan_plus_8.html
EU-MORGAN-PLUS-8-1972-CONVERTIBLE-2D-MIDBODY-01	3708	1499	1321	Automobile-Catalog 1972 Morgan Plus 8	https://www.automobile-catalog.com/car/1972/2038460/morgan_plus_8.html
EU-MORGAN-PLUS-8-1984-CONVERTIBLE-2D-01	3734	1575	1321	Automobile-Catalog 1984 Morgan Plus 8 PI	https://www.automobile-catalog.com/car/1984/2038685/morgan_plus_8_pi.html
EU-MORGAN-PLUS-8-1990-CONVERTIBLE-2D-01	3962	1600	1219	Automobile-Catalog 1990 Morgan Plus 8	https://www.automobile-catalog.com/car/1990/2038760/morgan_plus_8.html
EU-MORGAN-PLUS-8-1996-CONVERTIBLE-2D-WIDEBODY-01	3988	1753	1321	Automobile-Catalog 1996 Morgan Plus 8 4.6	https://www.automobile-catalog.com/car/1996/2039090/morgan_plus_8_4_6.html
EU-MORGAN-PLUS-8-2012-CONVERTIBLE-2D-01	4010	1751	1220	Automobile-Catalog 2014 Morgan Plus 8	https://www.automobile-catalog.com/car/2014/2039525/morgan_plus_8.html
EU-MORGAN-PLUS-4-1992-CONVERTIBLE-2D-WIDEBODY-01	3962	1626	1290	Automobile-Catalog 1992 Morgan Plus Four two-seater; Automobile-Catalog 1993 Morgan Plus Four two-seater	https://www.automobile-catalog.com/car/1992/2038925/morgan_plus_four_two_seater.html; https://www.automobile-catalog.com/car/1993/2038925/morgan_plus_four_two_seater.html
EU-MORGAN-PLUS-4-1985-CONVERTIBLE-2D-NARROWBODY-01	3886	1500	1270	Automobile-Catalog 1988 Morgan Plus Four two-seater; Automobile-Catalog 1991 Morgan Plus Four two-seater	https://www.automobile-catalog.com/car/1988/2038730/morgan_plus_four_two_seater.html; https://www.automobile-catalog.com/car/1991/2038730/morgan_plus_four_two_seater.html
EU-MORGAN-ROADSTER-2004-CONVERTIBLE-2D-01	4010	1720	1220	Automobile-Catalog 2006 Morgan Roadster	https://www.automobile-catalog.com/car/2006/2039165/morgan_roadster.html
EU-MORGAN-SUPERSPORT-2025-CONVERTIBLE-2D-01	4110	1805	1290	Carfolio 2025 Morgan Supersport; Autocar Morgan Supersport review	https://www.carfolio.com/morgan-supersport-827101; https://www.autocar.co.uk/car-review/morgan/supersport
EU-MORRIS-MARINA-III-WAGON-5D-01	4310	1640	1440	Automobile-Catalog 1979 Morris Marina 1300 Estate	https://www.automobile-catalog.com/car/1979/2035640/morris_marina_1300_l_estate.html
EU-MORRIS-MARINA-I-SEDAN-4D-STANDARD-01	4219	1646	1425	Automobile-Catalog 1975 Morris Marina 1.8 Super De Luxe Saloon	https://www.automobile-catalog.com/car/1975/2035055/morris_marina_1_8_super_de_luxe_saloon_automatic.html
EU-MORRIS-MARINA-II-SEDAN-4D-1800-01	4318	1656	1424	Automobile-Catalog 1975 Morris Marina II 1.8 Special 4Door	https://www.automobile-catalog.com/car/1975/2035280/morris_marina_2_1_8_special_4door.html
EU-MORRIS-MARINA-III-SEDAN-4D-01	4280	1640	1420	Automobile-Catalog 1979 Morris Marina 1700 HL 4Door	https://www.automobile-catalog.com/car/1979/2035580/morris_marina_1700_hl_4door.html
EU-MORRIS-MARINA-I-COUPE-2D-STANDARD-01	4143	1641	1406	Automobile-Catalog 1971 Morris Marina 1.3 Super De Luxe Coupe	https://www.automobile-catalog.com/car/1971/2035130/morris_marina_1_3_super_de_luxe_coupe.html
EU-MORRIS-MARINA-II-COUPE-2D-1300-01	4216	1652	1405	Automobile-Catalog 1976 Morris Marina II 1.3 Super 2Door	https://www.automobile-catalog.com/car/1976/2035340/morris_marina_2_1_3_super_2door.html
EU-MORRIS-MARINA-III-COUPE-2D-01	4200	1640	1410	Automobile-Catalog 1979 Morris Marina 1300 2Door	https://www.automobile-catalog.com/car/1979/2035610/morris_marina_1300_l_2door.html
EU-MORRIS-MARINA-II-WAGON-5D-01	4320	1655	1438	Automobile-Catalog 1976 Morris Marina II 1.8 Super Estate	https://www.automobile-catalog.com/car/1976/2035460/morris_marina_2_1_8_super_estate.html
EU-MORRIS-MARINA-II-SEDAN-4D-1300-01	4293	1656	1419	Automobile-Catalog 1975 Morris Marina II 1.3 Super 4Door	https://www.automobile-catalog.com/car/1975/2035250/morris_marina_2_1_3_super_4door.html
EU-MORRIS-MARINA-II-SEDAN-4D-2600-ZA-01	4220	1640	1390	Carfolio 1977 Leyland Marina 2600	https://www.carfolio.com/leyland-marina-2600-114455
EU-MORRIS-MARINA-II-COUPE-2D-1800-01	4242	1652	1410	Automobile-Catalog 1976 Morris Marina II 1.8 Special 2Door	https://www.automobile-catalog.com/car/1976/2035400/morris_marina_2_1_8_special_2door.html
EU-MORRIS-MARINA-I-SEDAN-4D-TC-01	4219	1646	1419	Automobile-Catalog 1975 Morris Marina 1.8 TC Saloon	https://www.automobile-catalog.com/car/1975/2035070/morris_marina_1_8_tc_saloon.html
EU-MORRIS-MARINA-I-COUPE-2D-TC-01	4143	1641	1400	Automobile-Catalog 1975 Morris Marina 1.8 TC Coupe	https://www.automobile-catalog.com/car/1975/39185/morris_marina_1800_tc_coupe.html
EU-MOSKVICH-412-IE-SEDAN-4D-01	4120	1550	1480	Automobile-Catalog 1988 Izh-Moskvich 028-412 IE	https://www.automobile-catalog.com/car/1988/1293860/izh_412_ie.html
EU-MOSLER-MT900-GTR-COUPE-2D-01	4801	2006	1130	Auto Motor und Sport Mosler MT900 technical data	https://www.auto-motor-und-sport.de/marken-modelle/mosler/mt900/technische-daten/
EU-NAVOR-E5-SUV-5D-01	4760	1865	1710	DFSK official E5 specifications	https://dfsksweden.com/products/dfsk-e5/
EU-NEXTEM-HUMPBACK-I-PLATFORM-2D-01	5510	1850	2485	Nextem official Humpback platform specifications	https://nextemev.com/h3/
EU-NEXTEM-MINKE-I-VAN-01	4855	1730	1985	Nextem Minke e-drive Center	https://edrivecenter.de/e-fahrzeuge/e-cargo/nextem-minke
EU-NEXTEM-ORCA-I-PLATFORM-2D-STD-01	4000	1600	1890	Nextem official Orca platform specifications	https://nextemev.com/h2/
EU-NEXTEM-ORCA-I-PLATFORM-2D-LWB-01	4300	1600	1890	Nextem official Orca optional-length platform specifications	https://nextemev.com/h2/
EU-NIO-EC6-II-SUV-5D-01	4849	1995	1697	NIO All-New EC6 official launch	https://www.nio.com/news/all-new-EC6-launch
EU-NIO-ES6-II-SUV-5D-01	4854	1995	1703	NIO All-New ES6 official launch	https://www.nio.com/news/All-New-ES6-Launch
EU-NIO-ES7-SUV-5D-01	4912	1987	1720	NIO EL7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/EL7/index.html
EU-NIO-ES8-II-SUV-5D-01	5099	1989	1750	NIO EL8 official user manual	https://www.nio.com/cdn-static/www/user-instructions/EL8/index.html
EU-NIO-ET5-SEDAN-4D-01	4790	1960	1499	NIO ET5 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET5/index.html
EU-NIO-ET5-WAGON-5D-01	4790	1960	1499	NIO ET5 Touring official user manual	https://www.nio.com/cdn-static/www/user-instructions/ET5-Touring/index.html
EU-NIO-ET7-SEDAN-4D-01	5101	1987	1509	NIO ET7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/ET7/index.html
EU-NISSAN-240SX-S13-COUPE-2D-01	4520	1690	1290	Auto-Data Nissan 240SX Coupe S13 2.4	https://www.auto-data.net/en/nissan-240sx-coupe-s13-2.4-134hp-42566
EU-NISSAN-200SX-S14-COUPE-2D-01	4560	1730	1295	Auto-Data Nissan 200 SX S14 2.0 i 16V Turbo	https://www.auto-data.net/en/nissan-200-sx-s14-2.0-i-16v-turbo-200hp-380
EU-NISSAN-240Z-S30-COUPE-3D-01	4115	1630	1305	Nissan Heritage Collection Datsun 240Z	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/datsun_240z.html
EU-NISSAN-260Z-S30-COUPE-3D-2PLUS2-01	4445	1650	1290	Datsun 260Z 2+2 official UK brochure	https://xr793.com/wp-content/uploads/2022/10/1974-Datsun-260Z-22-UK.pdf
EU-NISSAN-350Z-Z33-COUPE-3D-01	4310	1815	1315	Nissan Heritage Collection Fairlady Z Version ST	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/284_fairlady_z_version_st.html
EU-NISSAN-350Z-HZ33-CONVERTIBLE-2D-01	4310	1815	1325	Nissan Heritage Collection Fairlady Z Roadster	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/383_fairlady_z_roadster.html
EU-NISSAN-370Z-Z34-COUPE-3D-PREFL-01	4250	1845	1315	Nissan 370Z official European brochure	https://www.nissan-cdn.net/content/dam/Nissan/lv/brochures/brochureslv/ebrochure-370z.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-FACELIFT-01	4265	1845	1310	Nissan Europe FY17 370Z official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/pt/brochures/E-Catalago_370Z_PT.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-PREFL-01	4410	1870	1315	Nissan 370Z NISMO official European brochure	https://www.nissan-cdn.net/content/dam/Nissan/lv/brochures/brochureslv/ebrochure-370z.pdf
EU-NISSAN-370Z-Z34-COUPE-3D-NISMO-FACELIFT-01	4300	1870	1310	Nissan Europe FY17 370Z NISMO official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/pt/brochures/E-Catalago_370Z_PT.pdf
EU-NISSAN-370Z-HZ34-CONVERTIBLE-2D-01	4250	1845	1325	Nissan 370Z Roadster official UK brochure; Auto-Data Nissan 370Z Roadster; Auto-Data Nissan 370Z Roadster facelift 2012	https://xr793.com/wp-content/uploads/2022/10/2013-Nissan-370Z-Roadster-UK.pdf; https://www.auto-data.net/en/nissan-370z-roadster-generation-8044; https://www.auto-data.net/en/nissan-370z-roadster-facelift-2012-generation-4595
EU-NISSAN-ALMERA-I-N15-SEDAN-4D-01	4320	1690	1395	Nissan Almera N15 service manual	https://doksi.net/en/get.php?lid=39709
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_11501-11600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1968/2038400/morgan_plus_8.html "https://www.automobile-catalog.com/car/1968/2038400/morgan_plus_8.html"
[2]: https://nextemev.com/h2/ "https://nextemev.com/h2/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2594 行）
- 累计尺寸组：dimension_groups_final.tsv（791 行）

