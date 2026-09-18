# 任务：left18448 第 401-500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0005__795b6f53


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 401-500 行

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
left18448 第 401-500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	5019	1929	1360

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Aston Martin	Rapide	6.0 S	Schrägheck	Heckantrieb	Benzin	Aug 2014	-	125126
Aston Martin	Rapide	6.0 S	Schrägheck	Heckantrieb	Benzin	Nov 2016	-	155243
Aston Martin	Tickford capri	2.8 T	Coupe	Heckantrieb	Benzin	Jan 1982	Dec 1985	8185
Aston Martin	V12 speedster	5.2	Cabriolet	Heckantrieb	Benzin	Jun 2021	-	147008
Aston Martin	V8	5.3	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1989	8186
Aston Martin	V8	5.3	Coupe	Heckantrieb	Benzin	Jan 1969	Dec 1989	8187
Aston Martin	V8	5.3	Cabriolet	Heckantrieb	Benzin	Jan 1978	Dec 1989	8188
Aston Martin	V8	5.3	Cabriolet	Heckantrieb	Benzin	Jan 1978	Dec 1989	8189
Aston Martin	V8	5.3 V8	Cabriolet	Heckantrieb	Benzin	Jan 1980	Jan 1986	108196
Aston Martin	Valhalla	4.0 Phev	Coupe	Allrad	Benzin/Elektro	Mar 2024	-	158642
Aston Martin	Valhalla	4.0 Phev	Coupe	Allrad	Benzin/Elektro	Mar 2026	-	803009
Aston Martin	Valiant	5.2	Coupe	Heckantrieb	Benzin	Jul 2024	-	159397
Aston Martin	Valkyrie	6.5	Coupe	Heckantrieb	Benzin/Elektro	May 2021	-	158351
Aston Martin	Valour	5.2	Coupe	Heckantrieb	Benzin	Feb 2024	-	158323
Aston Martin	Vanquish	5.2	Coupe	Heckantrieb	Benzin	Sep 2024	-	159764
Aston Martin	Vanquish	5.2	Coupe	Heckantrieb	Benzin	Nov 2024	-	160423
Aston Martin	Vanquish	5.2	Cabriolet	Heckantrieb	Benzin	Jun 2025	-	163944
Aston Martin	Vanquish	6	Coupe	Heckantrieb	Benzin	Oct 2012	-	56732
Aston Martin	Vanquish	6	Coupe	Heckantrieb	Benzin	May 2014	-	108025
Aston Martin	Vanquish	6	Cabriolet	Heckantrieb	Benzin	May 2014	-	126963
Aston Martin	Vanquish	6.0 V12	Coupe	Heckantrieb	Benzin	May 2001	Aug 2007	16061
Aston Martin	Vanquish	S 6.0	Coupe	Heckantrieb	Benzin	Nov 2016	-	128126
Aston Martin	Vanquish	S 6.0	Cabriolet	Heckantrieb	Benzin	Nov 2016	-	128127
Aston Martin	Vantage	4.3	Cabriolet	Heckantrieb	Benzin	Jan 2008	Dec 2010	127111
Aston Martin	Vantage	6	Cabriolet	Heckantrieb	Benzin	Jan 2012	-	51339
Aston Martin	Vantage	4.3 N400	Coupe	Heckantrieb	Benzin	Jan 2008	Dec 2010	121304
Aston Martin	Vantage	4.7 GT8	Coupe	Heckantrieb	Benzin	Jul 2013	-	125883
Aston Martin	Vantage	4.7 V8	Coupe	Heckantrieb	Benzin	Oct 2008	Jul 2018	34762
Aston Martin	Vantage	4.7 V8	Cabriolet	Heckantrieb	Benzin	Oct 2008	Jul 2018	34763
Aston Martin	Vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Sep 2009	Dec 2013	34759
Aston Martin	Vantage	6.0 V12s	Coupe	Heckantrieb	Benzin	Jan 2013	-	100249
Aston Martin	Vantage	6.0 V12s	Cabriolet	Heckantrieb	Benzin	Apr 2014	-	106902
Aston Martin	Vantage	V12	Coupe	Heckantrieb	Benzin	Jun 2021	-	151841
Aston Martin	Vantage	V12	Cabriolet	Heckantrieb	Benzin	Jun 2021	-	151842
Aston Martin	Vantage	V12 AMR	Coupe	Heckantrieb	Benzin	Nov 2017	-	155251
Aston Martin	Vantage	V8	Coupe	Heckantrieb	Benzin	Mar 2021	-	144783
Aston Martin	Vantage	V8	Cabriolet	Heckantrieb	Benzin	Mar 2021	-	144784
Aston Martin	Vantage	V8	Coupe	Heckantrieb	Benzin	Apr 2024	-	158122
Aston Martin	Vantage	V8	Cabriolet	Heckantrieb	Benzin	Jan 2025	-	801413
Aston Martin	Vantage	V8 S	Coupe	Heckantrieb	Benzin	Aug 2025	-	802804
Aston Martin	Vantage	V8 S	Cabriolet	Heckantrieb	Benzin	Aug 2025	-	802805
Aston Martin	Virage limited edition vantage	5.3	Coupe	Heckantrieb	Benzin	Jan 1995	Dec 1995	8200
Aston Martin	Virage saloon	5.3	Stufenheck	Heckantrieb	Benzin	Jan 1994	Dec 1995	8195
Aston Martin	Virage saloon	6.3	Stufenheck	Heckantrieb	Benzin	Jan 1995	Dec 1995	8196
Aston Martin	Virage shooting brake	5.3	Kombi	Heckantrieb	Benzin	Jan 1993	Dec 1995	8194
Aston Martin	Virage shooting brake	6.3	Kombi	Heckantrieb	Benzin	Jan 1994	Dec 1995	8197
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	Jan 1988	Dec 1992	8192
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	Oct 1992	Dec 2000	8199
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	Jan 1991	Dec 1992	127112
Aston Martin	Virage volante	5.3	Cabriolet	Heckantrieb	Benzin	Sep 1990	Dec 1995	8193
Aston Martin	Virage volante	6.3	Cabriolet	Heckantrieb	Benzin	Sep 1990	Dec 1995	8198
Aston Martin	Zagato vantage	5.3	Coupe	Heckantrieb	Benzin	Jan 1986	Dec 1989	8190
Aston Martin	Zagato volante	5.3	Cabriolet	Heckantrieb	Benzin	Jan 1986	Dec 1989	8191
Audi	60	1.5	Kombi	Frontantrieb	Benzin	Sep 1968	Aug 1972	14310
Audi	80	1.3	Stufenheck	Frontantrieb	Benzin	Sep 1978	Jul 1981	18203
Audi	80	1.4	Stufenheck	Frontantrieb	Benzin	Aug 1986	Jul 1988	17635
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	Aug 1978	Jul 1986	17980
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	Aug 1990	Oct 1991	18109
Audi	80	2	Stufenheck	Frontantrieb	Benzin	Oct 1983	Sep 1984	12965
Audi	80	2.8	Kombi	Frontantrieb	Benzin	Sep 1991	Jan 1996	5057
Audi	80	1.8 GTE	Stufenheck	Frontantrieb	Benzin	Aug 1985	Jul 1986	5763
Audi	80	1.9 TD	Kombi	Frontantrieb	Diesel	Sep 1991	Dec 1994	17421
Audi	80	2.0 E	Stufenheck	Frontantrieb	Benzin	Aug 1990	Oct 1991	148994
Audi	80	2.0 E 16V	Stufenheck	Frontantrieb	Benzin	Sep 1991	Jul 1992	59287
Audi	90	2	Stufenheck	Frontantrieb	Benzin	Mar 1986	Mar 1987	5992
Audi	90	1.6 TD	Stufenheck	Frontantrieb	Diesel	Apr 1987	Sep 1991	12969
Audi	90	2.0 20 V	Stufenheck	Frontantrieb	Benzin	Aug 1989	Jul 1991	14140
Audi	90	2.0 20 V Quattro	Stufenheck	Allrad	Benzin	Aug 1988	Sep 1991	15409
Audi	90	2.2 E	Stufenheck	Frontantrieb	Benzin	Apr 1987	Jul 1991	5059
Audi	90	2.2 E Quattro	Stufenheck	Allrad	Benzin	Aug 1985	Mar 1987	5061
Audi	90	2.2 E Quattro	Stufenheck	Allrad	Benzin	Apr 1987	Sep 1991	5064
Audi	90	2.3 E 20V	Stufenheck	Frontantrieb	Benzin	Aug 1988	Jul 1991	5065
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	Aug 1982	Dec 1987	1967
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	Aug 1983	Jul 1989	8055
Audi	100	1.9	Kombi	Frontantrieb	Benzin	Feb 1983	Jul 1984	5993
Audi	100	2	Stufenheck	Frontantrieb	Benzin	Aug 1984	Dec 1987	8158
Audi	100	2.2	Stufenheck	Frontantrieb	Benzin	Aug 1982	Jul 1984	17919
Audi	100	1.8 CAT	Kombi	Frontantrieb	Benzin	Mar 1985	Nov 1990	8758
Audi	100	1.8 CAT Quattro	Kombi	Allrad	Benzin	Aug 1985	Oct 1990	6000
Audi	100	1.8 Quattro	Kombi	Allrad	Benzin	Aug 1986	Jul 1990	5998
Audi	100	1.8 Quattro	Stufenheck	Allrad	Benzin	Oct 1984	Jul 1988	8056
Audi	100	1.8 Quattro	Kombi	Allrad	Benzin	Oct 1984	Jul 1988	8057
Audi	100	2.0 D	Stufenheck	Frontantrieb	Diesel	Aug 1978	Jul 1982	1966
Audi	100	2.0 E	Kombi	Frontantrieb	Benzin	Jan 1985	Dec 1987	8159
Audi	100	2.0 E 16V	Stufenheck	Frontantrieb	Benzin	Jan 1992	Jul 1994	12481
Audi	100	2.2 CAT	Kombi	Frontantrieb	Benzin	Jun 1989	Nov 1990	8161
Audi	100	2.2 CAT	Stufenheck	Frontantrieb	Benzin	Oct 1984	Dec 1987	8164
Audi	100	2.2 CAT Quattro	Stufenheck	Allrad	Benzin	Oct 1984	Dec 1987	8162
Audi	100	2.2 CAT Quattro	Kombi	Allrad	Benzin	Jun 1989	Nov 1990	8163
Audi	200 c2	2.1 5T	Stufenheck	Frontantrieb	Benzin	Oct 1979	Sep 1982	106901
Audi	200 c3	2.3	Stufenheck	Frontantrieb	Benzin	Nov 1986	Sep 1991	8166
Audi	200 c3 avant	2.3	Kombi	Frontantrieb	Benzin	Nov 1986	Sep 1991	8167
Audi	200 c3 avant	2.2 Turbo	Kombi	Frontantrieb	Benzin	Aug 1985	Sep 1991	8168
Audi	A1	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Mar 2015	Oct 2018	112018
Audi	A1	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Mar 2015	Oct 2018	112021
Audi	A1	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Jan 2016	Oct 2018	118024
Audi	A1	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	Jan 2016	Oct 2018	118026
Audi	A1	1.2 Tfsi	Schrägheck	Frontantrieb	Benzin	Jan 2012	Apr 2015	11782
Audi	A1	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2014	Oct 2018	108165
Audi	A1	1.4 TDI	Schrägheck	Frontantrieb	Diesel	Nov 2014	Oct 2018	108168


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **17 个 Ktype 映射**，其中 Rapide S 两个 Ktype 直接复用跨批次已有尺寸组，不重复输出尺寸组。
* 本轮首次建立 **12 个 DIMENSION_GROUP**，覆盖 V12 Speedster、三代 Vanquish 分支以及 Vantage 2018、V12 宽体和 2024 改款车身。相关页面均提供可用于不含后视镜宽度口径的三维数据。([汽车目录][1])
* 2024 年后新一代 Vanquish 暂未闭合：官方规格目前使用“后视镜折叠宽度”，且不同直接资料的车长存在 4855 mm 与 4890 mm 冲突，因此 Ktype 159764、160423、163944 本轮保持待处理。([阿斯顿·马丁][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：17
* PENDING Ktype：83
* 当前批次已确认尺寸组：13

  * 复用已有尺寸组：1
  * 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125126	125126	Hatchback	Rapide (2010)		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S 五门掀背物理外廓。	READY
155243	155243	Hatchback	Rapide (2010)		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S 五门掀背物理外廓。	READY
147008	147008	Convertible	V12 Speedster		2	EU-ASTON-MARTIN-V12-SPEEDSTER-CONVERTIBLE-01	HIGH	无风挡双座开放式 Speedster 车身。	READY
16061	16061	Coupe	Vanquish (2001)		2	EU-ASTON-MARTIN-VANQUISH-2001-COUPE-01	HIGH	第一代 V12 Vanquish 双门 Coupe。	READY
56732	56732	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	HIGH	第二代 Vanquish Coupe，S 版外廓更新前。	READY
108025	108025	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	HIGH	第二代 Vanquish Coupe，S 版外廓更新前。	READY
126963	126963	Convertible	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-CONVERTIBLE-01	HIGH	第二代 Vanquish Volante 车身。	READY
128126	128126	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-S-COUPE-01	HIGH	Vanquish S Coupe 采用 S 版专属外廓。	READY
128127	128127	Convertible	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-S-CONVERTIBLE-01	HIGH	Vanquish S Volante 采用 S 版专属外廓。	READY
144783	144783	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	HIGH	标准 V8 Coupe，2024 外观大改前。	READY
144784	144784	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	HIGH	标准 V8 Roadster，2024 外观大改前。	READY
151841	151841	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-V12-COUPE-01	MEDIUM	映射至 V12 宽体 Coupe；输入起始月早于公开量产发布。	READY
151842	151842	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-V12-CONVERTIBLE-01	MEDIUM	映射至 V12 宽体 Roadster；输入起始月早于公开量产发布。	READY
158122	158122	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	HIGH	2024 外观大改后的 Coupe。	READY
801413	801413	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	HIGH	2025 Roadster，采用 2024 外观大改车身。	READY
802804	802804	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	HIGH	Vantage S Coupe 官方外廓尺寸与当前 Coupe 相同。	READY
802805	802805	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	HIGH	Vantage S Roadster 官方外廓尺寸与当前 Roadster 相同。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-V12-SPEEDSTER-CONVERTIBLE-01	4525	1990	1195	Automobile-Catalog 2021 Aston Martin V12 Speedster specifications	https://www.automobile-catalog.com/car/2021/3313490/aston_martin_v12_speedster.html
EU-ASTON-MARTIN-VANQUISH-2001-COUPE-01	4665	1923	1318	Auto-Data Aston Martin V12 Vanquish specifications	https://www.auto-data.net/en/aston-martin-v12-vanquish-generation-4916
EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	4720	1912	1294	Automobile-Catalog 2013 Aston Martin Vanquish specifications	https://www.automobile-catalog.com/car/2013/1764185/aston_martin_vanquish.html
EU-ASTON-MARTIN-VANQUISH-2012-CONVERTIBLE-01	4728	1912	1294	Automobile-Catalog 2013 Aston Martin Vanquish Volante specifications	https://www.automobile-catalog.com/car/2013/1913090/aston_martin_vanquish_volante.html
EU-ASTON-MARTIN-VANQUISH-2012-S-COUPE-01	4745	1910	1295	Automobile-Catalog 2017 Aston Martin Vanquish S specifications	https://www.automobile-catalog.com/car/2017/2515070/aston_martin_vanquish_s.html
EU-ASTON-MARTIN-VANQUISH-2012-S-CONVERTIBLE-01	4745	1910	1295	Automobile-Catalog 2017 Aston Martin Vanquish S Volante specifications	https://www.automobile-catalog.com/car/2017/2607410/aston_martin_vanquish_s_volante.html
EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	4465	1942	1274	Automobile-Catalog 2021 Aston Martin Vantage Coupe specifications	https://www.automobile-catalog.com/car/2021/2616650/aston_martin_vantage.html
EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	4465	1942	1274	Automobile-Catalog 2021 Aston Martin Vantage Roadster specifications	https://www.automobile-catalog.com/car/2021/2920340/aston_martin_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2018-V12-COUPE-01	4514	1982	1274	Automobile-Catalog 2022 Aston Martin V12 Vantage Coupe specifications	https://www.automobile-catalog.com/car/2022/3086015/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2018-V12-CONVERTIBLE-01	4514	1982	1274	Automobile-Catalog 2022 Aston Martin V12 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2022/3172355/aston_martin_v12_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	4495	1980	1275	Aston Martin Vantage official specifications	https://www.astonmartin.com/en-gb/models/vantage-coupe
EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	4495	1980	1275	Aston Martin Vantage Roadster official specifications	https://www.astonmartin.com/en-gb/models/vantage-roadster
```

## 下一步优先处理

1. 闭合 Valhalla、Valiant、Valkyrie、Valour及新一代 Vanquish，并解决新 Vanquish 不含后视镜宽度和车长冲突。
2. 按共享外廓批量处理 Aston Martin V8、Virage、Zagato 与 Tickford Capri 历史车型。
3. Aston Martin 清零后，按 Audi 80/90、Audi 100/200 共平台关系建立缓存尺寸组，再批量关联发动机版本。
4. 最后处理 Audi A1 2012—2018 三门与 Sportback 门数边界，避免把不同外廓误并为同一尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2021/3313490/aston_martin_v12_speedster.html?utm_source=chatgpt.com "2021 Aston Martin V12 Speedster Specs Review (533 kW / 725 PS / 715 hp) (since Q1 2021 for Europe worldwide, special edition)"
[2]: https://www.astonmartin.com/en-gb/models/vanquish "Vanquish: Super GT V12 Sports Car | Aston Martin UK"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Valhalla、Valiant、Valkyrie、Valour及第三代 Vanquish，共新增 **8 个 READY 映射、6 个尺寸组**。
* Valhalla 两个 Ktype 复用同一量产车身；第三代 Vanquish 两个 Coupe Ktype 复用同一尺寸组，Volante 因高度不同独立建组。
* Valkyrie 采用明确标注不含后视镜的 1922 mm 宽度；第三代 Vanquish 的 2044 mm 车宽已由明确的 without-mirrors 规格交叉确认。([汽车目录][1])
* Valhalla 最终量产尺寸采用 4748 × 2014 × 1161 mm，未沿用早期概念车或预量产尺寸。([Motor1.com][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：25
* PENDING Ktype：75
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
158642	158642	Coupe	Valhalla		2	EU-ASTON-MARTIN-VALHALLA-COUPE-01	MEDIUM	映射至最终量产 Valhalla 车身；输入起始时间早于正式量产。	READY
803009	803009	Coupe	Valhalla		2	EU-ASTON-MARTIN-VALHALLA-COUPE-01	HIGH	最终量产 Valhalla 双门 Coupe。	READY
159397	159397	Coupe	Valiant		2	EU-ASTON-MARTIN-VALIANT-COUPE-01	HIGH	Valiant 专属宽体及空气动力学外廓。	READY
158351	158351	Coupe	Valkyrie		2	EU-ASTON-MARTIN-VALKYRIE-COUPE-01	HIGH	Valkyrie 量产双门 Coupe。	READY
158323	158323	Coupe	Valour		2	EU-ASTON-MARTIN-VALOUR-COUPE-01	HIGH	Valour 限量双门 Coupe。	READY
159764	159764	Coupe	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	HIGH	第三代 Vanquish Coupe。	READY
160423	160423	Coupe	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	HIGH	第三代 Vanquish Coupe，共用同一量产外廓。	READY
163944	163944	Convertible	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-CONVERTIBLE-01	HIGH	第三代 Vanquish Volante 开篷车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VALHALLA-COUPE-01	4748	2014	1161	Aston Martin Boston Valhalla production specifications; Motor1 Valhalla final production specifications	https://www.astonmartinboston.com/exploring-the-aston-martin-valhalla-the-future-of-hybrid-hypercars/;https://www.motor1.com/news/743877/aston-martin-valhalla-supercar-alonso/
EU-ASTON-MARTIN-VALIANT-COUPE-01	4600	2000	1250	Automobile-Catalog 2024 Aston Martin Valiant specifications	https://www.automobile-catalog.com/car/2024/3377975/aston_martin_valiant.html
EU-ASTON-MARTIN-VALKYRIE-COUPE-01	4500	1922	1070	Automobile-Catalog 2021 Aston Martin Valkyrie specifications	https://www.automobile-catalog.com/car/2021/3086090/aston_martin_valkyrie.html
EU-ASTON-MARTIN-VALOUR-COUPE-01	4599	1987	1274	Auto-Data Aston Martin Valour specifications	https://www.auto-data.net/en/aston-martin-valour-5.2-v12-715hp-52251
EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	4855	2044	1290	Aston Martin Vanquish official specifications; Car and Driver 2025 Vanquish specifications	https://www.astonmartin.com/en/models/vanquish;https://www.caranddriver.com/aston-martin/vanquish/specs/2025/aston-martin_vanquish_aston-martin-vanquish_2025
EU-ASTON-MARTIN-VANQUISH-2024-CONVERTIBLE-01	4855	2044	1295	Aston Martin Vanquish Volante official specifications; Automobile-Catalog Vanquish Volante specifications	https://www.astonmartin.com/en/models/vanquish-volante;https://www.automobile-catalog.com/car/2025/3429140/aston_martin_vanquish_volante.html
```

## 下一步优先处理

1. 按共享外廓批量闭合 Aston Martin V8 Coupe、V8 Volante及 Tickford Capri。
2. 处理 Virage Saloon、Shooting Brake、Vantage、Volante和 Zagato 各独立车身分支。
3. Aston Martin 清零后，按 Audi 80/90 和 Audi 100/200 共平台、代际及 Sedan/Wagon 外廓聚类建组。
4. 最后核对 Audi A1 三门 Hatchback 与五门 Sportback 的 Ktype 分支边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2024/3086090/aston_martin_valkyrie.html?utm_source=chatgpt.com "2024 Aston Martin Valkyrie (s-aut. 7) (model up to mid-year ..."
[2]: https://www.motor1.com/news/743877/aston-martin-valhalla-supercar-alonso/?utm_source=chatgpt.com "Aston Martin Valhalla production model final specs revealed"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 9 个 Aston Martin Vantage Ktype，覆盖标准 V8 Coupe/Roadster、N400、V12、V12 S、V12 Roadster及 GT8。
* 标准 V8 与 N400 按相同外廓复用尺寸组；V12、V12 S及敞篷分支因高度或外部版本边界不同分别建组。([汽车目录][1])
* GT8 的加长、加宽空气动力学外廓单独建组，不与普通 V8 Vantage Coupe 合并。([汽车目录][2])
* Ktype `155251` 的 V12 AMR 本轮未落盘，继续等待明确标注不含后视镜宽度的完整三维来源。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：34
* PENDING Ktype：66
* 已确认尺寸组：26

  * 跨批次复用：1
  * 前两轮创建：18
  * 本轮首次创建：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127111	127111	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	HIGH	V8 Vantage Roadster 标准车身。	READY
51339	51339	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-CONVERTIBLE-01	HIGH	V12 Vantage Roadster 车身。	READY
121304	121304	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	HIGH	N400 未改变标准 Coupe 外廓边界。	READY
125883	125883	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-GT8-COUPE-01	MEDIUM	GT8 专属宽体空气动力学外廓；输入起始时间早于公开车型年份。	READY
34762	34762	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	HIGH	标准 V8 Vantage Coupe 车身。	READY
34763	34763	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	HIGH	标准 V8 Vantage Roadster 车身。	READY
34759	34759	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-COUPE-01	HIGH	初代 V12 Vantage Coupe 车身。	READY
100249	100249	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12S-COUPE-01	HIGH	V12 Vantage S Coupe 外廓。	READY
106902	106902	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12S-CONVERTIBLE-01	HIGH	V12 Vantage S Roadster 外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	4380	1865	1265	Automobile-Catalog 2009 Aston Martin V8 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2009/229220/aston_martin_v8_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-CONVERTIBLE-01	4385	1865	1256	Automobile-Catalog 2012 Aston Martin V12 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2012/1764140/aston_martin_v12_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	4380	1865	1255	Aston Martin V8 Vantage N400 brochure; Automobile-Catalog 2014 Aston Martin V8 Vantage specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-Vantage-N400-2007.pdf;https://www.automobile-catalog.com/car/2014/1437905/aston_martin_v8_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-GT8-COUPE-01	4540	1915	1250	Automobile-Catalog 2016 Aston Martin V8 Vantage GT8 specifications	https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-COUPE-01	4385	1865	1241	Automobile-Catalog 2010 Aston Martin V12 Vantage specifications	https://www.automobile-catalog.com/car/2010/1186325/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-V12S-COUPE-01	4385	1865	1241	Automobile-Catalog 2013 Aston Martin V12 Vantage S Coupe specifications	https://www.automobile-catalog.com/car/2013/1912025/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-V12S-CONVERTIBLE-01	4385	1865	1260	Automobile-Catalog 2015 Aston Martin V12 Vantage S Roadster specifications	https://www.automobile-catalog.com/car/2015/2071070/aston_martin_v12_vantage_s_roadster.html
```

## 下一步优先处理

1. 闭合 V12 AMR，并完成 Virage Vantage、Volante和 Limited Edition 的明确车身分支。
2. 单独解决 Virage Saloon 与 Shooting Brake 的短轴三门、普通 Coupe和长轴 Lagonda 命名边界。
3. 处理 AMV8、V8 Volante、Zagato及 Tickford Capri 历史车型的改款和宽体拆分。
4. Aston Martin 清零后，按 Audi 80/90、Audi 100/200 平台和车身形式批量建组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/229145/aston_martin_v8_vantage_n400_sportshift.html?utm_source=chatgpt.com "2008 Aston Martin V8 Vantage N400 Sportshift Specs ..."
[2]: https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html?utm_source=chatgpt.com "2016 Aston Martin Vantage GT8 Sportshift (s-aut. 7)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增 **10 个 READY 映射、7 个尺寸组**。
* V8 Volante 的三个 Ktype 复用同一欧洲规格车身；未采用北美加长保险杠版本。标准欧洲外廓为 4667 × 1829 × 1370 mm。([汽车目录][1])
* V12 Vantage AMR 单独建组：AMR 高度为 1250 mm，宽度以明确标注 `without mirrors` 的规格核对。([汽车指南][2])
* Virage 标准 Coupe、Vantage 宽体、标准 Volante 与 6.3 宽体 Volante 已按外廓拆分；宽体版本不与标准车身合并。([汽车目录][3])
* V8 Vantage Zagato Coupe 已闭合；Zagato Volante 因直接资料存在车长、宽度冲突，本轮仍不落盘。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：44
* PENDING Ktype：56
* 已确认尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8188	8188	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格 V8 Volante 车身。	READY
8189	8189	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格 V8 Volante 车身。	READY
108196	108196	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格 V8 Volante 车身。	READY
155251	155251	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-AMR-COUPE-01	HIGH	V12 Vantage AMR 专属版本外廓。	READY
8192	8192	Coupe	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	MEDIUM	生产区间结束于宽体 Vantage 量产前，映射至标准 Virage Coupe。	READY
8199	8199	Coupe	Virage Vantage (1993)		2	EU-ASTON-MARTIN-VIRAGE-VANTAGE-1993-COUPE-01	MEDIUM	输入起始月跨越正式发布边界，映射至双机械增压宽体 Vantage。	READY
127112	127112	Coupe	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	MEDIUM	生产区间结束于宽体 Vantage 量产前，映射至标准 Virage Coupe。	READY
8193	8193	Convertible	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-01	MEDIUM	标准 5.3 Virage Volante 车身；输入起始月早于量产交付。	READY
8198	8198	Convertible	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-WIDEBODY-01	HIGH	6.3 Works 宽体 Virage Volante。	READY
8190	8190	Coupe	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-COUPE-01	HIGH	V8 Vantage Zagato 短车身双门 Coupe。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	4667	1829	1370	Automobile-Catalog 1988 Aston Martin V8 Volante specifications	https://www.automobile-catalog.com/car/1988/227195/aston_martin_v8_volante.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-AMR-COUPE-01	4385	1865	1250	CarsGuide 2017 Aston Martin V12 Vantage AMR dimensions; Car and Driver 2017 V12 Vantage S exterior dimensions	https://www.carsguide.com.au/aston-martin/v12/car-dimensions/2017;https://www.caranddriver.com/aston-martin/vantage/specs/2017/aston-martin_vantage_aston-martin-v12-vantage-coupe_2017
EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	4745	1856	1320	Automobile-Catalog 1993 Aston Martin Virage specifications	https://www.automobile-catalog.com/car/1993/227735/aston_martin_virage_automatic.html
EU-ASTON-MARTIN-VIRAGE-VANTAGE-1993-COUPE-01	4745	1924	1330	Automobile-Catalog 1993 Aston Martin Virage Vantage specifications	https://www.automobile-catalog.com/car/1993/228320/aston_martin_virage_vantage.html
EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-01	4745	1856	1320	Automobile-Catalog 1993 Aston Martin Virage Volante specifications	https://www.automobile-catalog.com/car/1993/227795/aston_martin_virage_volante.html
EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-WIDEBODY-01	4745	1905	1320	Automobile-Catalog 1993 Aston Martin Virage Volante 6.3 specifications	https://www.automobile-catalog.com/car/1993/228020/aston_martin_virage_volante_6_3.html
EU-ASTON-MARTIN-V8-ZAGATO-COUPE-01	4390	1860	1295	AstonMartins.com V8 Vantage Zagato specifications; Automobile-Catalog 1988 Vantage Zagato specifications	https://astonmartins.com/car/v8-vantage-zagato/;https://www.automobile-catalog.com/car/1988/53795/aston_martin_vantage_zagato.html
```

## 下一步优先处理

1. 闭合 Virage Shooting Brake 5.3 与 6.3 宽体分支。
2. 处理 Virage Saloon、Limited Edition Vantage及 Zagato Volante 的车身边界和冲突尺寸。
3. 拆分生产区间横跨 DBS V8、AM V8早期和后期外廓的 V8 Coupe Ktype。
4. Aston Martin 清零后，按 Audi 80/90、Audi 100/200 的代际和 Sedan/Wagon 外廓批量建组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/227195/aston_martin_v8_volante.html?utm_source=chatgpt.com "1988 Aston Martin V8 Volante Specs Review (227.5 kW / 309 PS / 305 hp) (for Europe Australia )"
[2]: https://www.carsguide.com.au/aston-martin/v12/car-dimensions/2017?utm_source=chatgpt.com "Aston Martin V12 Dimensions 2017 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[3]: https://www.automobile-catalog.com/car/1993/227735/aston_martin_virage_automatic.html?utm_source=chatgpt.com "1993 Aston Martin Virage automatic Specs Review (246 kW / 335 PS / 330 hp) (since mid-year 1992 for Europe North America )"
[4]: https://www.automobile-catalog.com/car/1988/53795/aston_martin_vantage_zagato.html?utm_source=chatgpt.com "1988 Aston Martin Vantage Zagato Specs Review (322 kW / 438 PS / 432 hp) (up to mid-year 1988 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 6 个 Ktype，覆盖 Tickford Capri、AM V8 Vantage 标准/宽体分支、Virage Limited Edition、Virage Shooting Brake 5.3 和 Zagato Volante。
* Ktype `8186` 为标准窄体 V8 Vantage；`8187` 的 376 kW 版本按宽体高性能外廓独立建组，不能仅因同为 5.3 升发动机而合并。([汽车零件商店][1])
* Tickford Capri 确认为 Capri III 三门车身；Virage Shooting Brake 5.3 确认为标准轴距三门 Wagon，不与长轴五门 Lagonda Shooting Brake 合并。([汽车目录][2])
* Zagato Volante 与此前 Zagato Coupe 长度及车顶结构不同，独立建立 Convertible 尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：50
* PENDING Ktype：50
* 已确认尺寸组：39

  * 本轮首次创建：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8185	8185	Coupe	Tickford Capri		3	EU-ASTON-MARTIN-TICKFORD-CAPRI-COUPE-01	HIGH	Capri III三门Tickford Turbo车身。	READY
8186	8186	Coupe	AM V8 Vantage		2	EU-ASTON-MARTIN-AM-V8-VANTAGE-COUPE-01	HIGH	标准窄体V8 Vantage Coupe。	READY
8187	8187	Coupe	AM V8 Vantage		2	EU-ASTON-MARTIN-AM-V8-VANTAGE-XPACK-COUPE-01	MEDIUM	宽体高性能V8 Vantage外廓。	READY
8200	8200	Coupe	Virage Limited Edition		2	EU-ASTON-MARTIN-VIRAGE-LIMITED-EDITION-COUPE-01	HIGH	Limited Edition专属宽体Coupe。	READY
8194	8194	Wagon	Virage (1989)		3	EU-ASTON-MARTIN-VIRAGE-1989-SHOOTING-BRAKE-01	HIGH	标准轴距三门Shooting Brake。	READY
8191	8191	Convertible	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-CONVERTIBLE-01	HIGH	Volante Zagato开放式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-TICKFORD-CAPRI-COUPE-01	4390	1698	1346	Automobile-Catalog 1984 Ford Capri Tickford Turbo specifications	https://www.automobile-catalog.com/car/1984/929360/ford_capri_tickford_turbo.html
EU-ASTON-MARTIN-AM-V8-VANTAGE-COUPE-01	4667	1829	1327	Automobile-Catalog 1978 Aston Martin V8 Vantage specifications	https://www.automobile-catalog.com/car/1978/164870/aston_martin_v8_vantage.html
EU-ASTON-MARTIN-AM-V8-VANTAGE-XPACK-COUPE-01	4667	1890	1327	Automobile-Catalog 1988 Aston Martin V8 Vantage X-Pack specifications	https://www.automobile-catalog.com/car/1988/227300/aston_martin_v8_vantage_x-pack.html
EU-ASTON-MARTIN-VIRAGE-LIMITED-EDITION-COUPE-01	4745	1920	1330	Automobile-Catalog 1994 Aston Martin Virage Limited Edition Coupe specifications	https://www.automobile-catalog.com/car/1994/228095/aston_martin_virage_limited_edition_coupe.html
EU-ASTON-MARTIN-VIRAGE-1989-SHOOTING-BRAKE-01	4745	1855	1320	Automobile-Catalog 1993 Aston Martin Virage Shooting Brake specifications; EncyCARpedia 1992 Virage Shooting Brake specifications	https://www.automobile-catalog.com/car/1993/227870/aston_martin_virage_shooting_brake.html;https://www.encycarpedia.com/aston-martin/92-virage-shooting-brake-estate
EU-ASTON-MARTIN-V8-ZAGATO-CONVERTIBLE-01	4480	1860	1300	Automobile-Catalog 1988 Aston Martin Volante Zagato specifications	https://www.automobile-catalog.com/car/1988/54935/aston_martin_volante_zagato.html
```

## 下一步优先处理

1. 解决 Virage Saloon 5.3/6.3 的 TecDoc 命名与真实双门车身边界。
2. 判定 Virage Shooting Brake 6.3 是标准轴距宽体三门还是长轴五门 Lagonda 分支。
3. Aston Martin 剩余冲突清零后，按 Audi 80/90 的 B1、B2、B3、B4 代际批量建组。
4. 随后处理 Audi 100/200 C2、C3、C4 的 Sedan与Avant共享关系。

推进信号：CONTINUE

[1]: https://www.buycarparts.co.uk/aston-martin/v8-vantage/8186/74863/performance-clutch?utm_source=chatgpt.com "Performance clutch V8 Vantage 5.3 340 hp Petrol 40HCA 1969"
[2]: https://www.automobile-catalog.com/car/1983/929360/ford_capri_tickford_turbo.html?utm_source=chatgpt.com "1983 Ford Capri Tickford Turbo Specs Review (153 kW / 208 PS / 205 hp) (since mid-year 1983 for Europe )"
[3]: https://www.automobile-catalog.com/car/1988/54935/aston_martin_volante_zagato.html?utm_source=chatgpt.com "1988 Aston Martin Volante Zagato Specs Review (227 kW / 309 PS / 304 hp) (for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 3 个 Aston Martin 历史车型：`8195`、`8196` 复用 Virage Lagonda 四门 Saloon 外廓；`8197` 对应长轴五门 Shooting Brake，不与此前标准轴距三门 `8194` 合并。([汽车目录][1])
* 已批量闭合全部 10 个 Audi 80 Ktype。
* `17980` 与 `12965` 的生产区间跨越 Audi 80 B2 外观阶段变化，分别拆为 `prefl` 和 `facelift`；标准车身长度由 4383 mm 变为 4406 mm。([汽车目录][2])
* Audi 80 GTE 的 1345 mm 运动化车高与普通 B2 facelift 的 1365 mm 不同，因此单独建组。([汽车目录][3])
* Audi 80 B3 Phase I、Phase II及 B4 Sedan/Avant 已按实际外廓变化分组，没有按发动机版本重复建组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：63
* READY 映射：65
* PENDING Ktype：37
* 已确认尺寸组：48
* 本轮新增尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8195	8195	Sedan	Virage Lagonda		4	EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	HIGH	5.3升长轴四门Lagonda Saloon。	READY
8196	8196	Sedan	Virage Lagonda		4	EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	HIGH	6.3升版本保持相同长轴四门外廓。	READY
8197	8197	Wagon	Virage Lagonda		5	EU-ASTON-MARTIN-VIRAGE-LAGONDA-WAGON-01	HIGH	6.3升长轴五门Lagonda Shooting Brake。	READY
18203	18203	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前四门Sedan。	READY
17635	17635	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE1-01	HIGH	B3 Phase I四门Sedan。	READY
17980_prefl	17980	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖B2改款前外廓。	READY
17980_facelift	17980	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖B2改款后外廓。	READY
18109	18109	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE2-01	HIGH	B3 Phase II四门Sedan。	READY
12965_prefl	12965	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	MEDIUM	生产区间跨越1984年外观更新，包含改款前外廓。	READY
12965_facelift	12965	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越1984年外观更新，包含改款后外廓。	READY
5057	5057	Wagon	Audi 80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4 Avant五门Wagon。	READY
5763	5763	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-GTE-SEDAN-01	HIGH	GTE运动化车高与普通B2 facelift不同。	READY
17421	17421	Wagon	Audi 80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4 Avant五门Wagon。	READY
148994	148994	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE2-01	HIGH	B3 Phase II四门Sedan。	READY
59287	59287	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH	B4 16V四门Sedan。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	5055	1895	1360	Automobile-Catalog 1993 Aston Martin Lagonda Saloon 5.3 specifications; Automobile-Catalog 1994 Aston Martin Lagonda Saloon 6.3 specifications	https://www.automobile-catalog.com/car/1993/228185/aston_martin_lagonda_saloon_automatic.html;https://www.automobile-catalog.com/car/1994/228230/aston_martin_lagonda_saloon_6_3_automatic.html
EU-ASTON-MARTIN-VIRAGE-LAGONDA-WAGON-01	5055	1905	1360	Automobile-Catalog 1994 Aston Martin Lagonda Shooting Brake 6.3 specifications	https://www.automobile-catalog.com/car/1994/228275/aston_martin_lagonda_shooting_brake_6_3.html
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365	Automobile-Catalog 1979 Audi 80 1.3 specifications	https://www.automobile-catalog.com/car/1979/34805/audi_80_1_3.html
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365	Automobile-Catalog 1984 Audi 80 1.6 CC specifications	https://www.automobile-catalog.com/car/1984/230975/audi_80_1_6_cc.html
EU-AUDI-80-B2-GTE-SEDAN-01	4406	1682	1345	Automobile-Catalog 1984 Audi 80 GTE specifications	https://www.automobile-catalog.com/car/1984/50645/audi_80_gte.html
EU-AUDI-80-B3-SEDAN-PHASE1-01	4393	1695	1397	Automobile-Catalog 1987 Audi 80 1.6 specifications	https://www.automobile-catalog.com/car/1987/234845/audi_80_1_6_automatic.html
EU-AUDI-80-B3-SEDAN-PHASE2-01	4403	1695	1397	Automobile-Catalog 1991 Audi 80 1.6 specifications	https://www.automobile-catalog.com/car/1991/235445/audi_80_1_6_cat.html
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406	Automobile-Catalog 1992 Audi 80 16V specifications	https://www.automobile-catalog.com/car/1992/236480/audi_80_16v.html
EU-AUDI-80-B4-WAGON-01	4482	1695	1408	Automobile-Catalog 1992 Audi 80 Avant 2.0 E specifications	https://www.automobile-catalog.com/car/1992/236720/audi_80_avant_2_0_e.html
```

## 下一步优先处理

1. 按 B2、B3及 Phase I/II 外廓批量闭合 Audi 90 的 8 个 Ktype，并单独处理 20V 低车高分支。
2. 按 C2、C3、C4 平台聚类 Audi 100 Sedan与Avant，避免逐发动机重复建组。
3. 处理 Audi 200 C2、C3 Sedan与Avant相对 Audi 100 的保险杠长度差异。
4. 最后依据 Ktype 资料拆分 Audi A1 8X 三门 Hatchback与五门 Sportback。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1993/228185/aston_martin_lagonda_saloon_automatic.html?utm_source=chatgpt.com "1993 Aston Martin Lagonda Saloon automatic Specs Review (228 kW / 310 PS / 306 hp) (since mid-year 1993 for Europe )"
[2]: https://www.automobile-catalog.com/car/1979/34805/audi_80_1_3.html?utm_source=chatgpt.com "Detailed specs review of 1979 Audi 80 1.3 model for Europe"
[3]: https://www.automobile-catalog.com/car/1984/50645/audi_80_gte.html?utm_source=chatgpt.com "1984 Audi 80 GTE Specs Review (82 kW / 112 PS / 110 hp) (since mid-year 1984 for Europe )"
[4]: https://www.automobile-catalog.com/car/1987/234845/audi_80_1_6_automatic.html?utm_source=chatgpt.com "1987 Audi 80 1.6 automatic Specs Review (55 kW / 75 PS / 74 hp) (for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已批量闭合全部 8 个 Audi 90 Ktype。
* Audi 90 B2 前驱与 Quattro 的车高分别为 1365 mm、1376 mm，按不同物理外廓建组。([汽车目录][1])
* Audi 90 B3 普通版本车高为 1397 mm；20V 前驱与 Quattro 分别为 1371 mm、1372 mm，未因长宽相同而错误合并。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* READY 映射：73
* PENDING Ktype：29
* 已确认尺寸组：53
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5992	5992	Sedan	Audi 90 B2	81	4	EU-AUDI-90-B2-SEDAN-2WD-01	HIGH	B2前驱四门Sedan。	READY
12969	12969	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高四门Sedan。	READY
14140	14140	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-2WD-01	HIGH	20V前驱低车高外廓。	READY
15409	15409	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-QUATTRO-01	HIGH	20V Quattro低车高外廓。	READY
5059	5059	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高四门Sedan。	READY
5061	5061	Sedan	Audi 90 B2	85	4	EU-AUDI-90-B2-SEDAN-QUATTRO-01	HIGH	B2 Quattro四门Sedan。	READY
5064	5064	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高Quattro Sedan。	READY
5065	5065	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-2WD-01	HIGH	20V前驱低车高外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-90-B2-SEDAN-2WD-01	4465	1682	1365	Automobile-Catalog 1986 Audi 90 2.0 E specifications	https://www.automobile-catalog.com/car/1986/51500/audi_90_2_0_e.html
EU-AUDI-90-B3-SEDAN-STANDARD-01	4393	1695	1397	Automobile-Catalog 1987 Audi 90 2.2 E specifications	https://www.automobile-catalog.com/car/1987/235670/audi_90_2_2_e.html
EU-AUDI-90-B3-20V-SEDAN-2WD-01	4393	1695	1371	Automobile-Catalog 1988 Audi 90 20V specifications	https://www.automobile-catalog.com/car/1988/235790/audi_90_20v.html
EU-AUDI-90-B3-20V-SEDAN-QUATTRO-01	4393	1695	1372	Automobile-Catalog 1988 Audi 90 Quattro 20V catalyst specifications	https://www.automobile-catalog.com/car/1988/235775/audi_90_quattro_20v_cat.html
EU-AUDI-90-B2-SEDAN-QUATTRO-01	4465	1682	1376	Automobile-Catalog 1986 Audi 90 Quattro specifications	https://www.automobile-catalog.com/car/1986/52850/audi_90_quattro.html
```

## 下一步优先处理

1. 按 Audi 100 C3 的 Sedan、Avant及驱动形式批量关联，单独核对普通车高与 Quattro 车高差异。
2. 闭合 Audi 100 C2 Sedan及 Audi 100 C4 Sedan。
3. 处理 Audi 200 C2、C3 Sedan与Avant相对 Audi 100 的保险杠长度差异。
4. 最后拆分 Audi A1 8X 三门 Hatchback和五门 Sportback。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/51500/audi_90_2_0_e.html?utm_source=chatgpt.com "1986 Audi 90 2.0 E Specs Review (84.5 kW / 115 PS / 113 hp) (up to mid-year 1986 for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/235670/audi_90_2_2_e.html?utm_source=chatgpt.com "1987 Audi 90 2.2 E Specs Review (100 kW / 136 PS / 134 hp) (since mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_401-500_ktype_dimension_mapping_final.tsv
- left18448_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 剩余 29 个 Ktype 已全部闭合；当前批次 100 个输入 Ktype 均已覆盖。
* Audi 100/200 C3 按改款前后外廓拆分：改款前通常为 1422 mm 高，改款后为 1421 mm；Audi 200 的保险杠变化还造成 4807 mm 与 4793 mm 的车长差异。([汽车目录][1])
* Audi A1 已根据 Ktype 对应的三门 `8XK`、五门 Sportback `8XF` 及 `11782` 跨改款边界完成拆分。改款后三门为 3973 × 1740 × 1416 mm，Sportback 为 3973 × 1746 × 1422 mm。([lakiauto.ee][2])
* 已完成固定表头、唯一主键、引用闭合、尺寸与来源非空及孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：112
* PENDING：0
* DIMENSION_GROUP：68
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125126	125126	Hatchback	Rapide (2010)		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S五门掀背物理外廓。	READY
155243	155243	Hatchback	Rapide (2010)		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	Rapide S五门掀背物理外廓。	READY
8185	8185	Coupe	Tickford Capri		3	EU-ASTON-MARTIN-TICKFORD-CAPRI-COUPE-01	HIGH	Capri III三门Tickford Turbo车身。	READY
147008	147008	Convertible	V12 Speedster		2	EU-ASTON-MARTIN-V12-SPEEDSTER-CONVERTIBLE-01	HIGH	无风挡双座开放式Speedster车身。	READY
8186	8186	Coupe	AM V8 Vantage		2	EU-ASTON-MARTIN-AM-V8-VANTAGE-COUPE-01	HIGH	标准窄体V8 Vantage Coupe。	READY
8187	8187	Coupe	AM V8 Vantage		2	EU-ASTON-MARTIN-AM-V8-VANTAGE-XPACK-COUPE-01	MEDIUM	宽体高性能V8 Vantage外廓。	READY
8188	8188	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格V8 Volante车身。	READY
8189	8189	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格V8 Volante车身。	READY
108196	108196	Convertible	AM V8		2	EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	HIGH	标准欧洲规格V8 Volante车身。	READY
158642	158642	Coupe	Valhalla		2	EU-ASTON-MARTIN-VALHALLA-COUPE-01	MEDIUM	映射至最终量产Valhalla车身。	READY
803009	803009	Coupe	Valhalla		2	EU-ASTON-MARTIN-VALHALLA-COUPE-01	HIGH	最终量产Valhalla双门Coupe。	READY
159397	159397	Coupe	Valiant		2	EU-ASTON-MARTIN-VALIANT-COUPE-01	HIGH	Valiant专属宽体及空气动力学外廓。	READY
158351	158351	Coupe	Valkyrie		2	EU-ASTON-MARTIN-VALKYRIE-COUPE-01	HIGH	Valkyrie量产双门Coupe。	READY
158323	158323	Coupe	Valour		2	EU-ASTON-MARTIN-VALOUR-COUPE-01	HIGH	Valour限量双门Coupe。	READY
159764	159764	Coupe	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	HIGH	第三代Vanquish Coupe。	READY
160423	160423	Coupe	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	HIGH	第三代Vanquish Coupe。	READY
163944	163944	Convertible	Vanquish (2024)		2	EU-ASTON-MARTIN-VANQUISH-2024-CONVERTIBLE-01	HIGH	第三代Vanquish Volante。	READY
56732	56732	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	HIGH	第二代Vanquish Coupe。	READY
108025	108025	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	HIGH	第二代Vanquish Coupe。	READY
126963	126963	Convertible	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-CONVERTIBLE-01	HIGH	第二代Vanquish Volante。	READY
16061	16061	Coupe	Vanquish (2001)		2	EU-ASTON-MARTIN-VANQUISH-2001-COUPE-01	HIGH	第一代V12 Vanquish Coupe。	READY
128126	128126	Coupe	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-S-COUPE-01	HIGH	Vanquish S Coupe专属外廓。	READY
128127	128127	Convertible	Vanquish (2012)		2	EU-ASTON-MARTIN-VANQUISH-2012-S-CONVERTIBLE-01	HIGH	Vanquish S Volante专属外廓。	READY
127111	127111	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	HIGH	V8 Vantage Roadster标准车身。	READY
51339	51339	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-CONVERTIBLE-01	HIGH	V12 Vantage Roadster车身。	READY
121304	121304	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	HIGH	N400保持标准Coupe外廓。	READY
125883	125883	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-GT8-COUPE-01	MEDIUM	GT8专属宽体空气动力学外廓。	READY
34762	34762	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	HIGH	标准V8 Vantage Coupe。	READY
34763	34763	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	HIGH	标准V8 Vantage Roadster。	READY
34759	34759	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-COUPE-01	HIGH	初代V12 Vantage Coupe。	READY
100249	100249	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12S-COUPE-01	HIGH	V12 Vantage S Coupe。	READY
106902	106902	Convertible	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12S-CONVERTIBLE-01	HIGH	V12 Vantage S Roadster。	READY
151841	151841	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-V12-COUPE-01	MEDIUM	V12宽体Coupe。	READY
151842	151842	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-V12-CONVERTIBLE-01	MEDIUM	V12宽体Roadster。	READY
155251	155251	Coupe	Vantage (2005)		2	EU-ASTON-MARTIN-VANTAGE-2005-V12-AMR-COUPE-01	HIGH	V12 Vantage AMR专属外廓。	READY
144783	144783	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	HIGH	标准V8 Coupe，2024改款前。	READY
144784	144784	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	HIGH	标准V8 Roadster，2024改款前。	READY
158122	158122	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	HIGH	2024外观大改Coupe。	READY
801413	801413	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	HIGH	2025 Roadster采用改款车身。	READY
802804	802804	Coupe	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	HIGH	Vantage S Coupe同外廓。	READY
802805	802805	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	HIGH	Vantage S Roadster同外廓。	READY
8200	8200	Coupe	Virage Limited Edition		2	EU-ASTON-MARTIN-VIRAGE-LIMITED-EDITION-COUPE-01	HIGH	Limited Edition专属宽体Coupe。	READY
8195	8195	Sedan	Virage Lagonda		4	EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	HIGH	5.3升长轴四门Lagonda Saloon。	READY
8196	8196	Sedan	Virage Lagonda		4	EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	HIGH	6.3升版本同一长轴四门外廓。	READY
8194	8194	Wagon	Virage (1989)		3	EU-ASTON-MARTIN-VIRAGE-1989-SHOOTING-BRAKE-01	HIGH	标准轴距三门Shooting Brake。	READY
8197	8197	Wagon	Virage Lagonda		5	EU-ASTON-MARTIN-VIRAGE-LAGONDA-WAGON-01	HIGH	6.3升长轴五门Lagonda Shooting Brake。	READY
8192	8192	Coupe	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	MEDIUM	标准Virage Coupe。	READY
8199	8199	Coupe	Virage Vantage (1993)		2	EU-ASTON-MARTIN-VIRAGE-VANTAGE-1993-COUPE-01	MEDIUM	双机械增压宽体Vantage。	READY
127112	127112	Coupe	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	MEDIUM	标准Virage Coupe。	READY
8193	8193	Convertible	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-01	MEDIUM	标准5.3 Virage Volante。	READY
8198	8198	Convertible	Virage (1989)		2	EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-WIDEBODY-01	HIGH	6.3 Works宽体Virage Volante。	READY
8190	8190	Coupe	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-COUPE-01	HIGH	V8 Vantage Zagato短车身Coupe。	READY
8191	8191	Convertible	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-CONVERTIBLE-01	HIGH	Volante Zagato开放式车身。	READY
14310	14310	Wagon	Audi F103	F103	3	EU-AUDI-60-F103-WAGON-01	HIGH	Audi 60 Variant三门Wagon。	READY
18203	18203	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前四门Sedan。	READY
17635	17635	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE1-01	HIGH	B3 Phase I四门Sedan。	READY
17980_prefl	17980	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	MEDIUM	生产区间覆盖B2改款前外廓。	READY
17980_facelift	17980	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖B2改款后外廓。	READY
18109	18109	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE2-01	HIGH	B3 Phase II四门Sedan。	READY
12965_prefl	12965	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	MEDIUM	生产区间包含改款前外廓。	READY
12965_facelift	12965	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	生产区间包含改款后外廓。	READY
5057	5057	Wagon	Audi 80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4 Avant五门Wagon。	READY
5763	5763	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-GTE-SEDAN-01	HIGH	GTE运动化车高外廓。	READY
17421	17421	Wagon	Audi 80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4 Avant五门Wagon。	READY
148994	148994	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-PHASE2-01	HIGH	B3 Phase II四门Sedan。	READY
59287	59287	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH	B4 16V四门Sedan。	READY
5992	5992	Sedan	Audi 90 B2	81	4	EU-AUDI-90-B2-SEDAN-2WD-01	HIGH	B2前驱四门Sedan。	READY
12969	12969	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高Sedan。	READY
14140	14140	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-2WD-01	HIGH	20V前驱低车高外廓。	READY
15409	15409	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-QUATTRO-01	HIGH	20V Quattro低车高外廓。	READY
5059	5059	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高Sedan。	READY
5061	5061	Sedan	Audi 90 B2	85	4	EU-AUDI-90-B2-SEDAN-QUATTRO-01	HIGH	B2 Quattro四门Sedan。	READY
5064	5064	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-SEDAN-STANDARD-01	HIGH	B3标准车高Quattro Sedan。	READY
5065	5065	Sedan	Audi 90 B3	89	4	EU-AUDI-90-B3-20V-SEDAN-2WD-01	HIGH	20V前驱低车高外廓。	READY
1967	1967	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	C3改款前四门Sedan。	READY
8055_prefl	8055	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	MEDIUM	生产区间覆盖C3改款前外廓。	READY
8055_facelift	8055	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后外廓。	READY
5993	5993	Wagon	Audi 100 C3	44	5	EU-AUDI-100-C3-WAGON-PREFL-01	HIGH	C3改款前Avant。	READY
8158	8158	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	C3改款前四门Sedan。	READY
17919	17919	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	C3改款前四门Sedan。	READY
8758_prefl	8758	Wagon	Audi 100 C3	44	5	EU-AUDI-100-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前Avant。	READY
8758_facelift	8758	Wagon	Audi 100 C3	44	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后Avant。	READY
6000_prefl	6000	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前Quattro Avant。	READY
6000_facelift	6000	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后Quattro Avant。	READY
5998_prefl	5998	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前Quattro Avant。	READY
5998_facelift	5998	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后Quattro Avant。	READY
8056_prefl	8056	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	MEDIUM	生产区间覆盖C3改款前Quattro Sedan。	READY
8056_facelift	8056	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后Quattro Sedan。	READY
8057_prefl	8057	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前Quattro Avant。	READY
8057_facelift	8057	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后Quattro Avant。	READY
1966	1966	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH	C2四门Diesel Sedan。	READY
8159	8159	Wagon	Audi 100 C3	44	5	EU-AUDI-100-C3-WAGON-PREFL-01	HIGH	C3改款前Avant。	READY
12481	12481	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-01	HIGH	C4四门Sedan。	READY
8161	8161	Wagon	Audi 100 C3	44	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	HIGH	C3改款后Avant。	READY
8164	8164	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	C3改款前Sedan。	READY
8162	8162	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	C3改款前Quattro Sedan。	READY
8163	8163	Wagon	Audi 100 C3	44Q	5	EU-AUDI-100-C3-WAGON-FACELIFT-01	HIGH	C3改款后Quattro Avant。	READY
106901	106901	Sedan	Audi 200 C2	43	4	EU-AUDI-200-C2-SEDAN-01	HIGH	C2四门200 5T Sedan。	READY
8166_prefl	8166	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	MEDIUM	生产区间覆盖C3改款前200 Sedan。	READY
8166_facelift	8166	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后200 Sedan。	READY
8167_prefl	8167	Wagon	Audi 200 C3	44	5	EU-AUDI-200-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前200 Avant。	READY
8167_facelift	8167	Wagon	Audi 200 C3	44	5	EU-AUDI-200-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后200 Avant。	READY
8168_prefl	8168	Wagon	Audi 200 C3	44	5	EU-AUDI-200-C3-WAGON-PREFL-01	MEDIUM	生产区间覆盖C3改款前200 Turbo Avant。	READY
8168_facelift	8168	Wagon	Audi 200 C3	44	5	EU-AUDI-200-C3-WAGON-FACELIFT-01	MEDIUM	生产区间覆盖C3改款后200 Turbo Avant。	READY
112018	112018	Hatchback	Audi A1 8X facelift	8XK	3	EU-AUDI-A1-8X-HATCHBACK-FACELIFT-01	HIGH	三门A1 facelift。	READY
112021	112021	Hatchback	Audi A1 8X facelift	8XF	5	EU-AUDI-A1-8X-SPORTBACK-FACELIFT-01	HIGH	五门A1 Sportback facelift。	READY
118024	118024	Hatchback	Audi A1 8X facelift	8XK	3	EU-AUDI-A1-8X-HATCHBACK-FACELIFT-01	HIGH	三门A1 facelift。	READY
118026	118026	Hatchback	Audi A1 8X facelift	8XF	5	EU-AUDI-A1-8X-SPORTBACK-FACELIFT-01	HIGH	五门A1 Sportback facelift。	READY
11782_prefl	11782	Hatchback	Audi A1 8X	8XA	5	EU-AUDI-A1-8X-SPORTBACK-PREFL-01	MEDIUM	生产区间覆盖改款前Sportback。	READY
11782_facelift	11782	Hatchback	Audi A1 8X facelift	8XF	5	EU-AUDI-A1-8X-SPORTBACK-FACELIFT-01	MEDIUM	生产区间覆盖改款后Sportback。	READY
108165	108165	Hatchback	Audi A1 8X facelift	8XK	3	EU-AUDI-A1-8X-HATCHBACK-FACELIFT-01	HIGH	三门A1 facelift。	READY
108168	108168	Hatchback	Audi A1 8X facelift	8XF	5	EU-AUDI-A1-8X-SPORTBACK-FACELIFT-01	HIGH	五门A1 Sportback facelift。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_401-500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	5019	1929	1360	Aston Martin Rapide S official brochure	https://astonmartins.com/wp-content/uploads/2013/03/Rapide-S-April-2013-2.pdf
EU-ASTON-MARTIN-TICKFORD-CAPRI-COUPE-01	4390	1698	1346	Automobile-Catalog 1984 Ford Capri Tickford Turbo specifications	https://www.automobile-catalog.com/car/1984/929360/ford_capri_tickford_turbo.html
EU-ASTON-MARTIN-V12-SPEEDSTER-CONVERTIBLE-01	4525	1990	1195	Automobile-Catalog 2021 Aston Martin V12 Speedster specifications	https://www.automobile-catalog.com/car/2021/3313490/aston_martin_v12_speedster.html
EU-ASTON-MARTIN-AM-V8-VANTAGE-COUPE-01	4667	1829	1327	Automobile-Catalog 1978 Aston Martin V8 Vantage specifications	https://www.automobile-catalog.com/car/1978/164870/aston_martin_v8_vantage.html
EU-ASTON-MARTIN-AM-V8-VANTAGE-XPACK-COUPE-01	4667	1890	1327	Automobile-Catalog 1988 Aston Martin V8 Vantage X-Pack specifications	https://www.automobile-catalog.com/car/1988/227300/aston_martin_v8_vantage_x-pack.html
EU-ASTON-MARTIN-V8-VOLANTE-CONVERTIBLE-01	4667	1829	1370	Automobile-Catalog 1988 Aston Martin V8 Volante specifications	https://www.automobile-catalog.com/car/1988/227195/aston_martin_v8_volante.html
EU-ASTON-MARTIN-VALHALLA-COUPE-01	4748	2014	1161	Aston Martin Boston Valhalla production specifications; Motor1 Valhalla final production specifications	https://www.astonmartinboston.com/exploring-the-aston-martin-valhalla-the-future-of-hybrid-hypercars/;https://www.motor1.com/news/743877/aston-martin-valhalla-supercar-alonso/
EU-ASTON-MARTIN-VALIANT-COUPE-01	4600	2000	1250	Automobile-Catalog 2024 Aston Martin Valiant specifications	https://www.automobile-catalog.com/car/2024/3377975/aston_martin_valiant.html
EU-ASTON-MARTIN-VALKYRIE-COUPE-01	4500	1922	1070	Automobile-Catalog 2021 Aston Martin Valkyrie specifications	https://www.automobile-catalog.com/car/2021/3086090/aston_martin_valkyrie.html
EU-ASTON-MARTIN-VALOUR-COUPE-01	4599	1987	1274	Auto-Data Aston Martin Valour specifications	https://www.auto-data.net/en/aston-martin-valour-5.2-v12-715hp-52251
EU-ASTON-MARTIN-VANQUISH-2024-COUPE-01	4855	2044	1290	Aston Martin Vanquish official specifications; Car and Driver 2025 Vanquish specifications	https://www.astonmartin.com/en/models/vanquish;https://www.caranddriver.com/aston-martin/vanquish/specs/2025/aston-martin_vanquish_aston-martin-vanquish_2025
EU-ASTON-MARTIN-VANQUISH-2024-CONVERTIBLE-01	4855	2044	1295	Aston Martin Vanquish Volante official specifications; Automobile-Catalog Vanquish Volante specifications	https://www.astonmartin.com/en/models/vanquish-volante;https://www.automobile-catalog.com/car/2025/3429140/aston_martin_vanquish_volante.html
EU-ASTON-MARTIN-VANQUISH-2012-COUPE-01	4720	1912	1294	Automobile-Catalog 2013 Aston Martin Vanquish specifications	https://www.automobile-catalog.com/car/2013/1764185/aston_martin_vanquish.html
EU-ASTON-MARTIN-VANQUISH-2012-CONVERTIBLE-01	4728	1912	1294	Automobile-Catalog 2013 Aston Martin Vanquish Volante specifications	https://www.automobile-catalog.com/car/2013/1913090/aston_martin_vanquish_volante.html
EU-ASTON-MARTIN-VANQUISH-2001-COUPE-01	4665	1923	1318	Auto-Data Aston Martin V12 Vanquish specifications	https://www.auto-data.net/en/aston-martin-v12-vanquish-generation-4916
EU-ASTON-MARTIN-VANQUISH-2012-S-COUPE-01	4745	1910	1295	Automobile-Catalog 2017 Aston Martin Vanquish S specifications	https://www.automobile-catalog.com/car/2017/2515070/aston_martin_vanquish_s.html
EU-ASTON-MARTIN-VANQUISH-2012-S-CONVERTIBLE-01	4745	1910	1295	Automobile-Catalog 2017 Aston Martin Vanquish S Volante specifications	https://www.automobile-catalog.com/car/2017/2607410/aston_martin_vanquish_s_volante.html
EU-ASTON-MARTIN-VANTAGE-2005-V8-CONVERTIBLE-01	4380	1865	1265	Automobile-Catalog 2009 Aston Martin V8 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2009/229220/aston_martin_v8_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-CONVERTIBLE-01	4385	1865	1256	Automobile-Catalog 2012 Aston Martin V12 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2012/1764140/aston_martin_v12_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2005-V8-COUPE-01	4380	1865	1255	Aston Martin V8 Vantage N400 brochure; Automobile-Catalog 2014 Aston Martin V8 Vantage specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-Vantage-N400-2007.pdf;https://www.automobile-catalog.com/car/2014/1437905/aston_martin_v8_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-GT8-COUPE-01	4540	1915	1250	Automobile-Catalog 2016 Aston Martin V8 Vantage GT8 specifications	https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-COUPE-01	4385	1865	1241	Automobile-Catalog 2010 Aston Martin V12 Vantage specifications	https://www.automobile-catalog.com/car/2010/1186325/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-V12S-COUPE-01	4385	1865	1241	Automobile-Catalog 2013 Aston Martin V12 Vantage S Coupe specifications	https://www.automobile-catalog.com/car/2013/1912025/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2005-V12S-CONVERTIBLE-01	4385	1865	1260	Automobile-Catalog 2015 Aston Martin V12 Vantage S Roadster specifications	https://www.automobile-catalog.com/car/2015/2071070/aston_martin_v12_vantage_s_roadster.html
EU-ASTON-MARTIN-VANTAGE-2018-V12-COUPE-01	4514	1982	1274	Automobile-Catalog 2022 Aston Martin V12 Vantage Coupe specifications	https://www.automobile-catalog.com/car/2022/3086015/aston_martin_v12_vantage.html
EU-ASTON-MARTIN-VANTAGE-2018-V12-CONVERTIBLE-01	4514	1982	1274	Automobile-Catalog 2022 Aston Martin V12 Vantage Roadster specifications	https://www.automobile-catalog.com/car/2022/3172355/aston_martin_v12_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2005-V12-AMR-COUPE-01	4385	1865	1250	CarsGuide 2017 Aston Martin V12 Vantage AMR dimensions; Car and Driver 2017 V12 Vantage S exterior dimensions	https://www.carsguide.com.au/aston-martin/v12/car-dimensions/2017;https://www.caranddriver.com/aston-martin/vantage/specs/2017/aston-martin_vantage_aston-martin-v12-vantage-coupe_2017
EU-ASTON-MARTIN-VANTAGE-2018-COUPE-01	4465	1942	1274	Automobile-Catalog 2021 Aston Martin Vantage Coupe specifications	https://www.automobile-catalog.com/car/2021/2616650/aston_martin_vantage.html
EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	4465	1942	1274	Automobile-Catalog 2021 Aston Martin Vantage Roadster specifications	https://www.automobile-catalog.com/car/2021/2920340/aston_martin_vantage_roadster.html
EU-ASTON-MARTIN-VANTAGE-2024-COUPE-01	4495	1980	1275	Aston Martin Vantage official specifications	https://www.astonmartin.com/en-gb/models/vantage-coupe
EU-ASTON-MARTIN-VANTAGE-2024-CONVERTIBLE-01	4495	1980	1275	Aston Martin Vantage Roadster official specifications	https://www.astonmartin.com/en-gb/models/vantage-roadster
EU-ASTON-MARTIN-VIRAGE-LIMITED-EDITION-COUPE-01	4745	1920	1330	Automobile-Catalog 1994 Aston Martin Virage Limited Edition Coupe specifications	https://www.automobile-catalog.com/car/1994/228095/aston_martin_virage_limited_edition_coupe.html
EU-ASTON-MARTIN-VIRAGE-LAGONDA-SEDAN-01	5055	1895	1360	Automobile-Catalog 1993 Aston Martin Lagonda Saloon 5.3 specifications; Automobile-Catalog 1994 Aston Martin Lagonda Saloon 6.3 specifications	https://www.automobile-catalog.com/car/1993/228185/aston_martin_lagonda_saloon_automatic.html;https://www.automobile-catalog.com/car/1994/228230/aston_martin_lagonda_saloon_6_3_automatic.html
EU-ASTON-MARTIN-VIRAGE-1989-SHOOTING-BRAKE-01	4745	1855	1320	Automobile-Catalog 1993 Aston Martin Virage Shooting Brake specifications; EncyCARpedia 1992 Virage Shooting Brake specifications	https://www.automobile-catalog.com/car/1993/227870/aston_martin_virage_shooting_brake.html;https://www.encycarpedia.com/aston-martin/92-virage-shooting-brake-estate
EU-ASTON-MARTIN-VIRAGE-LAGONDA-WAGON-01	5055	1905	1360	Automobile-Catalog 1994 Aston Martin Lagonda Shooting Brake 6.3 specifications	https://www.automobile-catalog.com/car/1994/228275/aston_martin_lagonda_shooting_brake_6_3.html
EU-ASTON-MARTIN-VIRAGE-1989-COUPE-01	4745	1856	1320	Automobile-Catalog 1993 Aston Martin Virage specifications	https://www.automobile-catalog.com/car/1993/227735/aston_martin_virage_automatic.html
EU-ASTON-MARTIN-VIRAGE-VANTAGE-1993-COUPE-01	4745	1924	1330	Automobile-Catalog 1993 Aston Martin Virage Vantage specifications	https://www.automobile-catalog.com/car/1993/228320/aston_martin_virage_vantage.html
EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-01	4745	1856	1320	Automobile-Catalog 1993 Aston Martin Virage Volante specifications	https://www.automobile-catalog.com/car/1993/227795/aston_martin_virage_volante.html
EU-ASTON-MARTIN-VIRAGE-1989-CONVERTIBLE-WIDEBODY-01	4745	1905	1320	Automobile-Catalog 1993 Aston Martin Virage Volante 6.3 specifications	https://www.automobile-catalog.com/car/1993/228020/aston_martin_virage_volante_6_3.html
EU-ASTON-MARTIN-V8-ZAGATO-COUPE-01	4390	1860	1295	AstonMartins.com V8 Vantage Zagato specifications; Automobile-Catalog 1988 Vantage Zagato specifications	https://astonmartins.com/car/v8-vantage-zagato/;https://www.automobile-catalog.com/car/1988/53795/aston_martin_vantage_zagato.html
EU-ASTON-MARTIN-V8-ZAGATO-CONVERTIBLE-01	4480	1860	1300	Automobile-Catalog 1988 Aston Martin Volante Zagato specifications	https://www.automobile-catalog.com/car/1988/54935/aston_martin_volante_zagato.html
EU-AUDI-60-F103-WAGON-01	4380	1626	1456	Automobile-Catalog 1969 Audi 60 Variant specifications	https://www.automobile-catalog.com/car/1969/74465/audi_60_variant.html
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365	Automobile-Catalog 1979 Audi 80 1.3 specifications	https://www.automobile-catalog.com/car/1979/34805/audi_80_1_3.html
EU-AUDI-80-B3-SEDAN-PHASE1-01	4393	1695	1397	Automobile-Catalog 1987 Audi 80 1.6 specifications	https://www.automobile-catalog.com/car/1987/234845/audi_80_1_6_automatic.html
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365	Automobile-Catalog 1984 Audi 80 1.6 CC specifications	https://www.automobile-catalog.com/car/1984/230975/audi_80_1_6_cc.html
EU-AUDI-80-B3-SEDAN-PHASE2-01	4403	1695	1397	Automobile-Catalog 1991 Audi 80 1.6 specifications	https://www.automobile-catalog.com/car/1991/235445/audi_80_1_6_cat.html
EU-AUDI-80-B4-WAGON-01	4482	1695	1408	Automobile-Catalog 1992 Audi 80 Avant 2.0 E specifications	https://www.automobile-catalog.com/car/1992/236720/audi_80_avant_2_0_e.html
EU-AUDI-80-B2-GTE-SEDAN-01	4406	1682	1345	Automobile-Catalog 1984 Audi 80 GTE specifications	https://www.automobile-catalog.com/car/1984/50645/audi_80_gte.html
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406	Automobile-Catalog 1992 Audi 80 16V specifications	https://www.automobile-catalog.com/car/1992/236480/audi_80_16v.html
EU-AUDI-90-B2-SEDAN-2WD-01	4465	1682	1365	Automobile-Catalog 1986 Audi 90 2.0 E specifications	https://www.automobile-catalog.com/car/1986/51500/audi_90_2_0_e.html
EU-AUDI-90-B3-SEDAN-STANDARD-01	4393	1695	1397	Automobile-Catalog 1987 Audi 90 2.2 E specifications	https://www.automobile-catalog.com/car/1987/235670/audi_90_2_2_e.html
EU-AUDI-90-B3-20V-SEDAN-2WD-01	4393	1695	1371	Automobile-Catalog 1988 Audi 90 20V specifications	https://www.automobile-catalog.com/car/1988/235790/audi_90_20v.html
EU-AUDI-90-B3-20V-SEDAN-QUATTRO-01	4393	1695	1372	Automobile-Catalog 1988 Audi 90 Quattro 20V catalyst specifications	https://www.automobile-catalog.com/car/1988/235775/audi_90_quattro_20v_cat.html
EU-AUDI-90-B2-SEDAN-QUATTRO-01	4465	1682	1376	Automobile-Catalog 1986 Audi 90 Quattro specifications	https://www.automobile-catalog.com/car/1986/52850/audi_90_quattro.html
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422	Automobile-Catalog 1987 Audi 100 1.8 specifications	https://www.automobile-catalog.com/car/1987/232610/audi_100_1_8_5-speed.html
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421	Automobile-Catalog 1989 Audi 100 1.8 specifications	https://www.automobile-catalog.com/car/1989/233045/audi_100_1_8.html
EU-AUDI-100-C3-WAGON-PREFL-01	4793	1814	1422	Automobile-Catalog 1987 Audi 100 Avant 2.2 E specifications	https://www.automobile-catalog.com/car/1987/232430/audi_100_avant_2_2_e_cc_automatic.html
EU-AUDI-100-C3-WAGON-FACELIFT-01	4793	1814	1421	Automobile-Catalog 1989 Audi 100 Avant 1.8 specifications	https://www.automobile-catalog.com/car/1989/233495/audi_100_avant_1_8.html
EU-AUDI-100-C2-SEDAN-01	4683	1768	1390	Automobile-Catalog 1981 Audi 100 C Diesel specifications	https://www.automobile-catalog.com/car/1981/167345/audi_100_c_diesel.html
EU-AUDI-100-C4-SEDAN-01	4790	1777	1431	Automobile-Catalog 1992 Audi 100 2.0 16V specifications	https://www.automobile-catalog.com/car/1992/238700/audi_100_2_0_16v.html
EU-AUDI-200-C2-SEDAN-01	4695	1768	1390	Automobile-Catalog 1980 Audi 200 5T specifications	https://www.automobile-catalog.com/car/1980/167870/audi_200_5t.html
EU-AUDI-200-C3-SEDAN-PREFL-01	4807	1814	1422	Automobile-Catalog 1983 Audi 200 specifications	https://www.automobile-catalog.com/car/1983/254780/audi_200.html
EU-AUDI-200-C3-SEDAN-FACELIFT-01	4793	1814	1421	Automobile-Catalog 1989 Audi 200 Turbo specifications	https://www.automobile-catalog.com/car/1989/234140/audi_200_turbo_automatic.html
EU-AUDI-200-C3-WAGON-PREFL-01	4807	1814	1422	Sauto Audi 200 Avant 2.3 specifications	https://www.sauto.cz/katalog-modelu/41-audi/500-200/1080-200-avant-c3-typ-4444q/4283-24
EU-AUDI-200-C3-WAGON-FACELIFT-01	4793	1814	1421	Automobile-Catalog 1990 Audi 200 Avant Turbo specifications	https://www.automobile-catalog.com/car/1990/234110/audi_200_avant_turbo_quattro_cat.html
EU-AUDI-A1-8X-HATCHBACK-FACELIFT-01	3973	1740	1416	Automobile-Catalog 2015 Audi A1 1.0 TFSI specifications	https://www.automobile-catalog.com/car/2015/2170865/audi_a1_1_0_tfsi_ultra_95.html
EU-AUDI-A1-8X-SPORTBACK-FACELIFT-01	3973	1746	1422	Automobile-Catalog 2015 Audi A1 Sportback 1.0 TFSI specifications	https://www.automobile-catalog.com/car/2015/2170910/audi_a1_sportback_1_0_tfsi_ultra_95_s-tronic.html
EU-AUDI-A1-8X-SPORTBACK-PREFL-01	3954	1746	1422	Audi UK A1 Sportback 1.2 TFSI technical data	https://press.audi.co.uk/assets/documents/original/9692-AudiUK00000044A1Sportback12TFSITechnical.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_401-500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1987/232610/audi_100_1_8_5-speed.html?utm_source=chatgpt.com "1987 Audi 100 1.8 5-speed Specs Review (55 kW ..."
[2]: https://www.lakiauto.ee/admin/upload/Dokumendid/pump_compressed.pdf?utm_source=chatgpt.com "TecDoc ktype Manufacturer Model Engine ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（601 行）
- 累计尺寸组：dimension_groups_final.tsv（309 行）

