# 任务：left18448 第 3401-3500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0035__fe1ab626


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3401-3500 行

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
left18448 第 3401-3500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CHRYSLER-SEBRING-II-CONVERTIBLE-EU-01	4921	1792	1401
EU-CHRYSLER-SEBRING-III-CONVERTIBLE-01	4922	1816	1485
EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	4850	1843	1497
EU-CHRYSLER-SEBRING-II-SEDAN-01	4844	1792	1394

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Chrysler	Sebring	2.7	Stufenheck	Frontantrieb	Benzin	Jul 2007	Dec 2010	114797
Chrysler	Sebring	2.7 Flexfuel	Cabriolet	Frontantrieb	Benzin/Ethanol	May 2007	Sep 2010	124849
Chrysler	Sebring	2.7 V6 24V	Stufenheck	Frontantrieb	Benzin	Apr 2001	Jun 2007	15498
Chrysler	Sebring	2.7 V6 24V	Cabriolet	Frontantrieb	Benzin	Apr 2001	Jun 2007	15859
Chrysler	Sebring	2.7 VVT	Stufenheck	Frontantrieb	Benzin	Jul 2007	Sep 2010	59760
Chrysler	Stratus	2.4 16 V	Stufenheck	Frontantrieb	Benzin	Dec 1995	Apr 2001	14319
Chrysler	Viper	8	Coupe	Heckantrieb	Benzin	Jul 1998	Dec 1998	10225
Chrysler	Viper	8	Cabriolet	Heckantrieb	Benzin	Jul 1998	Dec 1998	10226
Chrysler	Viper	8	Coupe	Heckantrieb	Benzin	Aug 1992	Dec 1998	18659
Chrysler	Viper	8	Cabriolet	Heckantrieb	Benzin	Aug 1992	Dec 1998	18660
Chrysler	Viper	8	Coupe	Heckantrieb	Benzin	Aug 1992	Dec 1998	18661
Chrysler	Viper	8	Cabriolet	Heckantrieb	Benzin	Aug 1992	Dec 1998	18662
Chrysler	Viper	8	Coupe	Heckantrieb	Benzin	Aug 1992	Dec 1998	18663
Chrysler	Voyager / grand ii	3.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jan 1993	Sep 1995	142652
Chrysler	Voyager / grand ii	2.5 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 1992	Sep 1995	142651
Chrysler	Voyager / grand iii	3	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	14670
Chrysler	Voyager / grand iii	3.8	Großraumlimousine	Frontantrieb	Benzin	Oct 1997	Sep 2000	59949
Chrysler	Voyager / grand iii	2.4 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	5131
Chrysler	Voyager / grand iii	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	Jan 1995	Mar 2001	5134
Chrysler	Voyager / grand iii	3.3 I	Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	5132
Chrysler	Voyager / grand iii	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	5133
Chrysler	Voyager / grand iii	3.8 I AWD	Großraumlimousine	Allrad	Benzin	Jan 1995	Mar 2001	11028
Chrysler	Voyager ii	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	Jan 1992	Sep 1995	57287
Chrysler	Voyager iii van	2.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	143208
Chrysler	Voyager iii van	3.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jan 1995	Mar 2001	143209
Chrysler	Voyager iii van	2.5 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 1995	Mar 2001	143212
Chrysler	Voyager iii van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	Oct 1995	Sep 1997	143210
Chrysler	Voyager iii van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	Oct 1997	Mar 2001	143211
Chrysler	Voyager iv	2.4	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2008	14681
Chrysler	Voyager iv	2.4	Großraumlimousine	Frontantrieb	Benzin	Apr 2003	Dec 2007	59940
Chrysler	Voyager iv	3	Großraumlimousine	Frontantrieb	Benzin	Sep 1999	Dec 2000	38751
Chrysler	Voyager iv	3.3	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2008	14894
Chrysler	Voyager iv	3.8	Großraumlimousine	Frontantrieb	Benzin	Feb 2000	Dec 2008	16433
Chrysler	Voyager iv	2.5 CRD	Großraumlimousine	Frontantrieb	Diesel	Feb 2000	Dec 2008	14895
Chrysler	Voyager iv	2.8 CRD	Großraumlimousine	Frontantrieb	Diesel	Jun 2004	Dec 2008	18267
Chrysler	Voyager iv	3.3 AWD	Großraumlimousine	Allrad	Benzin	Feb 2000	Dec 2008	16435
Chrysler	Voyager iv	3.8 AWD	Großraumlimousine	Allrad	Benzin	Feb 2000	Dec 2008	16434
Chrysler	Voyager iv van	3.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2000	Jun 2007	143246
Chrysler	Voyager iv van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2000	Jun 2007	143247
Chrysler	Voyager iv van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	Oct 2000	Jun 2007	143248
Citroën	Acadiane	6	Kasten	Frontantrieb	Benzin	Aug 1978	Oct 1988	14136
Citroën	Acadiane	6	Kasten	Frontantrieb	Benzin	Aug 1978	Oct 1988	15360
Citroën	Ami	Electric	Schrägheck	Frontantrieb	Elektro	Apr 2020	-	143386
Citroën	Ami	Electric	Schrägheck	Frontantrieb	Elektro	Jun 2025	-	161168
Citroën	Ax	10	Schrägheck	Frontantrieb	Benzin	Sep 1986	Jun 1992	19005
Citroën	Ax	1.4 GTI	Schrägheck	Frontantrieb	Benzin	Aug 1991	Dec 1996	6022
Citroën	Ax	1.4 GTI	Schrägheck	Frontantrieb	Benzin	Jun 1991	Dec 1996	6023
Citroën	Ax	1.4 GTI	Schrägheck	Frontantrieb	Benzin	Jun 1991	Dec 1992	15048
Citroën	Ax	11 4X4	Schrägheck	Allrad	Benzin	Jun 1991	Jul 1992	18870
Citroën	Ax	11 CAT	Schrägheck	Frontantrieb	Benzin	Sep 1988	Dec 1989	6020
Citroën	Berlingo	1.1 I	Großraumlimousine	Frontantrieb	Benzin	Jul 1996	May 2008	5722
Citroën	Berlingo	1.4 Bivalent	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2002	Dec 2011	18614
Citroën	Berlingo	1.4 Bivalent	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2002	Dec 2011	18615
Citroën	Berlingo	1.4 I	Großraumlimousine	Frontantrieb	Benzin	Jul 1996	Dec 2011	5719
Citroën	Berlingo	1.4 I Bivalent	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Apr 2003	Oct 2005	17674
Citroën	Berlingo	1.4 I Bivalent	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	Apr 2003	Oct 2008	17675
Citroën	Berlingo	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Oct 2000	Dec 2011	16155
Citroën	Berlingo	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Dec 2014	Apr 2021	112390
Citroën	Berlingo	1.6 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2014	Apr 2021	112392
Citroën	Berlingo	1.6 Bluehdi 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2014	Apr 2021	118107
Citroën	Berlingo	1.6 Bluehdi 100 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Dec 2014	Dec 2018	122105
Citroën	Berlingo	1.6 Bluehdi 120	Großraumlimousine	Frontantrieb	Diesel	Dec 2014	Aug 2018	112391
Citroën	Berlingo	1.6 Bluehdi 120	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2014	Aug 2018	112393
Citroën	Berlingo	1.6 HDI / Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Apr 2020	113667
Citroën	Berlingo	1.6 HDI 110	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Dec 2018	11049
Citroën	Berlingo	1.6 HDI 115	Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Dec 2018	56261
Citroën	Berlingo	1.6 HDI 115	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Dec 2018	56262
Citroën	Berlingo	1.6 HDI 115 4X4	Großraumlimousine	Allrad	Diesel	Feb 2012	Dec 2018	122102
Citroën	Berlingo	1.6 HDI 115 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Feb 2012	Dec 2018	122106
Citroën	Berlingo	1.6 HDI 75	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	Dec 2011	19026
Citroën	Berlingo	1.6 HDI 75 / Bluehdi 75	Großraumlimousine	Frontantrieb	Diesel	Apr 2008	Apr 2020	113668
Citroën	Berlingo	1.6 HDI 75 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Feb 2012	Dec 2018	122103
Citroën	Berlingo	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Dec 2018	11048
Citroën	Berlingo	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	May 2008	19027
Citroën	Berlingo	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2010	Dec 2017	116222
Citroën	Berlingo	1.6 HDI 90 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 2008	Dec 2018	59312
Citroën	Berlingo	1.6 HDI 90 4X4	Großraumlimousine	Allrad	Diesel	Feb 2012	Dec 2014	122101
Citroën	Berlingo	1.6 HDI 90 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Feb 2012	Dec 2014	122104
Citroën	Berlingo	1.6 HDI 92	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2010	Dec 2017	118106
Citroën	Berlingo	1.6 HDI 92	Großraumlimousine	Frontantrieb	Diesel	Sep 2018	-	150197
Citroën	Berlingo	1.6 VTI 120	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2009	Dec 2018	11050
Citroën	Berlingo	1.8 D	Großraumlimousine	Frontantrieb	Diesel	Jul 1998	Oct 2002	15049
Citroën	Berlingo	1.8 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 1998	Oct 2002	18873
Citroën	Berlingo	1.8 I 4WD	Großraumlimousine	Allrad	Benzin	Apr 1997	Oct 2001	15050
Citroën	Berlingo	1.9 D	Großraumlimousine	Frontantrieb	Diesel	Jul 1996	Dec 2003	5720
Citroën	Berlingo	1.9 D	Großraumlimousine	Frontantrieb	Diesel	Jul 1998	Oct 2005	10227
Citroën	Berlingo	1.9 D 4WD	Großraumlimousine	Allrad	Diesel	Jul 1998	Oct 2005	15052
Citroën	Berlingo	1.9 D 70	Kasten/Großraumlimousine	Frontantrieb	Diesel	Apr 1999	Dec 2011	14443
Citroën	Berlingo	1.9 D 70 4WD	Kasten/Großraumlimousine	Allrad	Diesel	Jul 1998	Mar 2006	15051
Citroën	Berlingo	2.0 HDI 90	Großraumlimousine	Frontantrieb	Diesel	Dec 1999	Oct 2005	14491
Citroën	Berlingo	2.0 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 1999	Dec 2011	15755
Citroën	Berlingo	2.0 HDI 90 4WD	Kasten/Großraumlimousine	Allrad	Diesel	Nov 2000	Oct 2005	18877
Citroën	Berlingo	Ë-berlingo	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jul 2021	-	145276
Citroën	Berlingo	Ë-berlingo	Großraumlimousine	Frontantrieb	Elektro	Jul 2021	-	145516
Citroën	Berlingo	Ë-berlingo	Kasten/Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157796
Citroën	Berlingo	Ë-berlingo	Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	157797
Citroën	Berlingo	Ë-berlingo 4X4	Kasten/Großraumlimousine	Allrad	Elektro	Jan 2025	-	801456
Citroën	Berlingo	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jan 2010	Dec 2010	59304
Citroën	Berlingo	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jan 2013	Dec 2018	107936
Citroën	Berlingo	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jan 2013	-	108166


--- Round 1 / 首次发送 ---
## 更新点

* 已直接复用 4 个跨批次 Sebring 尺寸组，完成 5 个 Sebring Ktype 映射。
* 新闭合 Stratus JA、1998 Viper SR II Coupe/Convertible、Acadiane、两版 Ami 和 AX 尺寸组。Viper 1998 两种车身采用明确标注“不含后视镜宽度”的规格；2020 Ami 官方资料同样明确宽度不含后视镜。([汽车数据网][1])
* 2025 年 Ami 官方资料给出 `2460 × 1390 × 1525 mm`，与 2020 版 `2410 × 1390 × 1520 mm` 不同，因此单独建组，未覆盖旧组。([Stellantis Media][2])
* AX GTI 确认为三门；AX 10、11 CAT 和 4x4 存在三门/五门分支，按门数派生 id，但因三维一致共用一个尺寸组。([汽车目录][3])
* 5 个宽年份 Viper Ktype 暂未强行关联：其 TecDoc 日期覆盖或混合 SR I、SR II 边界，需要按功率/欧洲型号进一步聚类，避免把 1992 RT/10 与后期车身错误合并。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：18
* READY 映射行：21
* PENDING Ktype：82
* 已确认尺寸组：11

  * 跨批次复用：4
  * 本轮首次创建：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
114797	114797	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	HIGH	第三代四门轿车。	READY
124849	124849	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-CONVERTIBLE-01	HIGH	第三代双门敞篷车。	READY
15498	15498	Sedan	Sebring II	JR	4	EU-CHRYSLER-SEBRING-II-SEDAN-01	HIGH	第二代四门轿车。	READY
15859	15859	Convertible	Sebring II		2	EU-CHRYSLER-SEBRING-II-CONVERTIBLE-EU-01	HIGH	第二代双门敞篷车。	READY
59760	59760	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	HIGH	第三代四门轿车。	READY
14319	14319	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-I-SEDAN-01	HIGH	JA四门轿车。	READY
10225	10225	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	HIGH	1998年SR II GTS三门掀背式双门跑车。	READY
10226	10226	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	HIGH	1998年SR II RT/10双门敞篷车。	READY
18659	18659	Coupe	Viper first generation		3		LOW	需确认该功率Ktype对应SR II GTS的具体欧洲规格边界。	PENDING: TecDoc年份与正式Coupe投产边界冲突
18660	18660	Convertible	Viper first generation		2		LOW	候选为早期SR I RT/10，需排除后期SR II外廓。	PENDING: Ktype年份跨越SR I与SR II边界
18661	18661	Coupe	Viper first generation		3		LOW	需确认该功率Ktype对应SR II GTS的具体欧洲规格边界。	PENDING: TecDoc年份与正式Coupe投产边界冲突
18662	18662	Convertible	Viper first generation		2		LOW	需区分SR I与SR II RT/10物理外廓。	PENDING: Ktype年份跨越SR I与SR II边界
18663	18663	Coupe	Viper first generation		3		LOW	需确认该功率Ktype对应SR II GTS的具体欧洲规格边界。	PENDING: TecDoc年份与正式Coupe投产边界冲突
14136	14136	Van	Acadiane			EU-CITROEN-ACADIANE-VAN-01	HIGH	Acadiane厢式车外廓。	READY
15360	15360	Van	Acadiane			EU-CITROEN-ACADIANE-VAN-01	HIGH	Acadiane厢式车外廓。	READY
143386	143386	Hatchback	Ami I	Z2CA	2	EU-CITROEN-AMI-I-HATCHBACK-01	HIGH	2020版封闭式双门电动微型车。	READY
161168	161168	Hatchback	Ami I facelift	Z2CA	2	EU-CITROEN-AMI-I-FACELIFT-HATCHBACK-01	HIGH	2025改款官方三维与早期车型不同。	READY
19005_3dr	19005	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	Ktype覆盖AX 10三门分支。	READY
19005_5dr	19005	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	Ktype覆盖AX 10五门分支；三维与三门相同。	READY
6022	6022	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
6023	6023	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
15048	15048	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
18870_3dr	18870	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 4x4三门分支。	READY
18870_5dr	18870	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 4x4五门分支；三维与三门相同。	READY
6020_3dr	6020	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 11 CAT三门分支。	READY
6020_5dr	6020	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 11 CAT五门分支；三维与三门相同。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-STRATUS-I-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus (JA) specifications	https://www.auto-data.net/en/chrysler-stratus-ja-generation-3236
EU-CHRYSLER-VIPER-SR-II-COUPE-01	4488	1923	1194	Edmunds 1998 Dodge Viper GTS specifications	https://www.edmunds.com/dodge/viper/1998/st-13055/features-specs/
EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	4448	1923	1118	Edmunds 1998 Dodge Viper RT/10 specifications	https://www.edmunds.com/dodge/viper/1998/st-13057/features-specs/
EU-CITROEN-ACADIANE-VAN-01	4030	1500	1825	Auto-Data Citroen Acadiane specifications	https://www.auto-data.net/en/citroen-acadiane-generation-3299
EU-CITROEN-AMI-I-HATCHBACK-01	2410	1390	1520	Citroën Stellantis Media Ami official technical characteristics	https://www.media.stellantis.com/em-en/citroen/press/ami-100-electric-mobility-accessible-to-all
EU-CITROEN-AMI-I-FACELIFT-HATCHBACK-01	2460	1390	1525	Citroën official Ami technical characteristics July-November 2025	https://www.media.stellantis.com/uploads/fr/model-document/caracteristiques_techniques_ami_1125-69a99a625a11c.pdf
EU-CITROEN-AX-HATCHBACK-01	3495	1596	1355	Auto-Data Citroen AX specifications	https://www.auto-data.net/en/citroen-ax-generation-3321
```

## 下一步优先处理

1. 按 SWB/LWB 聚类处理 Voyager II、III、IV，并分别核对乘用 MPV 与 Van 是否共用外廓。
2. 闭合宽年份 Viper Ktype 的 SR I/SR II 边界。
3. 将 Berlingo 按第一代、第二代、第三代，再按 MPV、Van、底盘/Pickup、M/L 长度及 4x4 特殊高度批量建组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/chrysler-stratus-ja-generation-3236 "1995 Chrysler Stratus (JA) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.media.stellantis.com/uploads/fr/model-document/caracteristiques_techniques_ami_1125-69a99a625a11c.pdf?utm_source=chatgpt.com "Citroën ami"
[3]: https://www.automobile-catalog.com/car/1991/541010/citroen_ax_gti.html?utm_source=chatgpt.com "1991 Citroen AX GTI Specs Review (73.5 kW / 100 PS / 99 hp) (since September 1991 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Voyager II 的短轴、长轴外廓：短轴 `4525 × 1830 × 1707 mm`，长轴 `4896 × 1830 × 1707 mm`，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Voyager III 的 `GS-52` 短轴和 `GS-53` 长轴外廓；Chrysler 车身代码资料确认 `52=短轴`、`53=长轴`，对应三维分别为 `4733 × 1950 × 1740 mm` 和 `5070 × 1950 × 1740 mm`。([NHTSA][2])
* `Voyager III Van` 的现有 Ktype 均带 `GSH…52` 车身代码，本轮统一关联已闭合的 `GS-52` 短轴尺寸组，不重复建立相同尺寸事实。([archiwum.allegro.pl][3])
* 本轮新增完成 15 个 Ktype、24 条 READY 映射和 4 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：33
* PENDING Ktype：67
* READY 映射行：45
* 已确认尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142652_swb	142652	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴外廓。	READY
142652_lwb	142652	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-LWB-01	HIGH	ES长轴Grand外廓。	READY
142651_swb	142651	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴外廓。	READY
142651_lwb	142651	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-LWB-01	HIGH	ES长轴Grand外廓。	READY
14670_swb	14670	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
14670_lwb	14670	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
59949_swb	59949	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
59949_lwb	59949	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5131_swb	5131	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5131_lwb	5131	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5134_swb	5134	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5134_lwb	5134	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5132_swb	5132	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5132_lwb	5132	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5133_swb	5133	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5133_lwb	5133	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
11028_swb	11028	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
11028_lwb	11028	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
57287	57287	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴Voyager外廓。	READY
143208	143208	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143209	143209	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143212	143212	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143210	143210	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴AWD厢式外廓。	READY
143211	143211	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴AWD厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-VOYAGER-II-SWB-01	4525	1830	1707	Automobile-Catalog 1994 Chrysler Voyager 2.5 TD specifications	https://www.automobile-catalog.com/car/1994/518180/chrysler_voyager_2_5_td.html
EU-CHRYSLER-VOYAGER-II-LWB-01	4896	1830	1707	Automobile-Catalog 1993 Chrysler Grand Voyager 2.5 TD specifications	https://www.automobile-catalog.com/car/1993/518315/chrysler_grand_voyager_le_2_5_td.html
EU-CHRYSLER-VOYAGER-III-SWB-01	4733	1950	1740	Chrysler manufacturer body-code filing; Automobile-Catalog 1999 Chrysler Voyager specifications	https://www.nhtsa.gov/file-downloads/download?p=nhtsa%2Fdownloads%2FMfrMail%2F01-22-N11B-6012.pdf;https://www.automobile-catalog.com/car/1999/519860/chrysler_voyager_family_2_4.html
EU-CHRYSLER-VOYAGER-III-LWB-01	5070	1950	1740	Chrysler manufacturer body-code filing; Automobile-Catalog 1999 Chrysler Grand Voyager specifications	https://www.nhtsa.gov/file-downloads/download?p=nhtsa%2Fdownloads%2FMfrMail%2F01-22-N11B-6012.pdf;https://www.automobile-catalog.com/car/1999/519980/chrysler_grand_voyager_se_2_4.html
```

## 下一步优先处理

1. 集中闭合 Voyager IV 的短轴、长轴及 `Voyager IV Van` 车身代码边界。
2. 处理剩余 5 个宽年份 Viper Ktype 的 SR I、SR II 映射边界。
3. 将 Berlingo 按代际、乘用/厢式/底盘、M/XL 长度和特殊 4×4 高度分组处理。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1994/518180/chrysler_voyager_2_5_td.html?utm_source=chatgpt.com "1994 Chrysler Voyager 2.5 TD Specs Review (87 kW / 118 ..."
[2]: https://www.nhtsa.gov/file-downloads/download?p=nhtsa%2Fdownloads%2FMfrMail%2F01-22-N11B-6012.pdf&utm_source=chatgpt.com "chrysler corporation"
[3]: https://archiwum.allegro.pl/oferta/pompa-wody-chrysler-voyager-iii-3-3-3-8-1995-2001-i13928852459.html?utm_source=chatgpt.com "POMPA WODY CHRYSLER VOYAGER III 3.3 3.8 1995-2001 - 13928852459 - oficjalne archiwum Allegro"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Voyager IV 的前期与改款外廓：前期标准轴距为 `4803 × 1996 × 1750 mm`、长轴为 `5049 × 1997 × 1749 mm`；2005 年欧洲官方规格中的改款标准轴距和长轴分别为 `4810 × 1997 × 1749 mm`、`5096 × 1997 × 1749 mm`，因此建立 4 个独立尺寸组。宽度均采用不含后视镜口径。([汽车目录][1])
* 根据欧洲官方配置边界，将 2.4 和 2.5 CRD 关联标准轴距，将 3.3、3.8 与 AWD 版本关联长轴 Grand 外廓；2.8 CRD 同时覆盖标准轴距和长轴。([Amazon Web Services, Inc.][2])
* Voyager IV Van 的 3.3、3.8 和 3.8 AWD Ktype 均确认属于 `53` 长轴车身代码系列，因此只关联长轴前期与改款尺寸组。([普里梅克斯][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：44
* PENDING Ktype：56
* READY 映射行：67
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14681_swb_prefl	14681	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
14681_swb_facelift	14681	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
59940_swb_prefl	59940	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
59940_swb_facelift	59940	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
14894_lwb_prefl	14894	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	RG长轴Grand前期外廓。	READY
14894_lwb_facelift	14894	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	RG长轴Grand改款外廓。	READY
16433_lwb_prefl	16433	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	RG长轴Grand前期外廓。	READY
16433_lwb_facelift	16433	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	RG长轴Grand改款外廓。	READY
14895_swb_prefl	14895	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
14895_swb_facelift	14895	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
18267_swb	18267	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	改款标准轴距外廓。	READY
18267_lwb	18267	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	改款长轴Grand外廓。	READY
16435_lwb_prefl	16435	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	AWD长轴Grand前期外廓。	READY
16435_lwb_facelift	16435	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	AWD长轴Grand改款外廓。	READY
16434_lwb_prefl	16434	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	AWD长轴Grand前期外廓。	READY
16434_lwb_facelift	16434	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	AWD长轴Grand改款外廓。	READY
143246_lwb_prefl	143246	Van	Voyager IV	S-53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	53系列长轴厢式前期外廓。	READY
143246_lwb_facelift	143246	Van	Voyager IV	S-53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	53系列长轴厢式改款外廓。	READY
143247_lwb_prefl	143247	Van	Voyager IV	SYX53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	SYX53长轴厢式前期外廓。	READY
143247_lwb_facelift	143247	Van	Voyager IV	SYX53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	SYX53长轴厢式改款外廓。	READY
143248_lwb_prefl	143248	Van	Voyager IV	SCH53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	SCH53长轴AWD厢式前期外廓。	READY
143248_lwb_facelift	143248	Van	Voyager IV	SCH53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	SCH53长轴AWD厢式改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	4803	1996	1750	Automobile-Catalog 2001 Chrysler Voyager 2.4L specifications	https://www.automobile-catalog.com/car/2001/522350/chrysler_voyager_2_4l_automatic.html
EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	5049	1997	1749	Automobile-Catalog 2001 Chrysler Grand Voyager 2.5 CRD specifications	https://www.automobile-catalog.com/car/2001/522980/chrysler_grand_voyager_limited_2_5_crd.html
EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	4810	1997	1749	DaimlerChrysler 2005 Chrysler Voyager and Grand Voyager Europe press specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/attachments/ChryslerGrandVoyagerEnglish.pdf
EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	5096	1997	1749	DaimlerChrysler 2005 Chrysler Voyager and Grand Voyager Europe press specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/attachments/ChryslerGrandVoyagerEnglish.pdf
```

## 下一步优先处理

1. 闭合 Ktype `38751` 的早期 3.0 版本轴距分支。
2. 处理剩余 Viper SR I、SR II 边界。
3. 集中处理 Berlingo 第一代与第二代的乘用版、厢式版、底盘版和 4×4 特殊外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/522350/chrysler_voyager_2_4l_automatic.html?utm_source=chatgpt.com "2001 Chrysler Voyager 2.4L automatic (aut. 3)"
[2]: https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/attachments/ChryslerGrandVoyagerEnglish.pdf "Chrysler GrandVoyager iii.indd"
[3]: https://primex-bg.com/search-by-automobile.html?vehicle=143246&utm_source=chatgpt.com "Search by Automobile"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* `38751` 已按生产日期和 3.0 V6 车型边界关联第三代 Voyager `GS-52` 短轴组，不再新建重复尺寸组。2000 年对应外廓为 `4733 × 1950 × 1740 mm`。([汽车目录][1])
* 5 个宽年份 Viper Ktype 已消除 PENDING：Coupe 仅对应 SR II GTS；Convertible 拆分为 SR I 与 SR II。SR I 欧洲版 RT/10 为 `4448 × 1924 × 1117 mm`，SR II 继续复用已有尺寸组。([汽车目录][2])
* Berlingo I 非四驱车型按三套已确认外廓闭合：

  * M49 早期：`4108 × 1698 × 1802 mm`
  * M49 后期：`4108 × 1719 × 1802 mm`
  * M59 改款：`4137 × 1724 × 1810 mm`。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* PENDING Ktype：33
* READY 映射行：109
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18659	18659	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
18660_sr_i	18660	Convertible	Viper first generation	SR I	2	EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR I敞篷分支。	READY
18660_sr_ii	18660	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR II敞篷分支。	READY
18661	18661	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
18662_sr_i	18662	Convertible	Viper first generation	SR I	2	EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR I敞篷分支。	READY
18662_sr_ii	18662	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR II敞篷分支。	READY
18663	18663	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
38751	38751	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	MEDIUM	生产日期对应GS-52短轴第三代外廓；输入代次标记前移。	READY
5722_m49_early	5722	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5722_m49_late	5722	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5722_m59	5722	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
18614	18614	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
18615	18615	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
5719_m49_early	5719	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5719_m49_late	5719	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5719_m59	5719	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
17674	17674	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
17675	17675	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
16155_m49_late	16155	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
16155_m59	16155	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
19026	19026	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
19027	19027	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
15049_m49_early	15049	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
15049_m49_late	15049	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
18873_m49_early	18873	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
18873_m49_late	18873	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
5720_m49_early	5720	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5720_m49_late	5720	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5720_m59	5720	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
10227_m49_early	10227	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
10227_m49_late	10227	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
10227_m59	10227	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
14443_m49_early	14443	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
14443_m49_late	14443	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
14443_m59	14443	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
14491_m49_early	14491	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
14491_m49_late	14491	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
14491_m59	14491	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
15755_m49_early	15755	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
15755_m49_late	15755	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
15755_m59	15755	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
59304	59304	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59电动厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	4448	1924	1117	Automobile-Catalog 1995 Chrysler Viper RT/10 Europe specifications	https://www.automobile-catalog.com/car/1995/685385/chrysler_viper_rt10.html
EU-CITROEN-BERLINGO-I-M49-EARLY-01	4108	1698	1802	Automobile-Catalog 1998 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/1998/547775/citroen_berlingo_multispace_1_9_d.html
EU-CITROEN-BERLINGO-I-M49-LATE-01	4108	1719	1802	Automobile-Catalog 2001 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/2001/547850/citroen_berlingo_multispace_1_9_d.html
EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	4137	1724	1810	Automobile-Catalog 2005 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/2005/550205/citroen_berlingo_multispace_1_9_d.html
```

## 下一步优先处理

1. 闭合 Berlingo I 的 4×4 Dangel 特殊高度组。
2. 集中处理 Berlingo II `B9` 的标准长度、长车身、底盘版与 4×4 外廓。
3. 随后处理第三代 `K9`、ë-Berlingo 及 2023 改款分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/519770/chrysler_voyager_family_2_0.html?utm_source=chatgpt.com "2000 Chrysler Voyager 2.0 Specs Review (98 kW / 133 PS / 131 hp) (up to late-year 2000 for Europe )"
[2]: https://www.automobile-catalog.com/car/1995/685385/chrysler_viper_rt10.html?utm_source=chatgpt.com "1995 Chrysler Viper RT/10 Specs Review (290 kW / 394 PS / 389 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1998/547775/citroen_berlingo_multispace_1_9_d.html?utm_source=chatgpt.com "1998 Citroen Berlingo Multispace 1.9 D Specs Review (51.5 kW / 70 PS / 69 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Berlingo II `B9` 的乘用版、L1 标准载荷、L1 高载荷、L1 XTR、L2、平台底盘和 L1 Dangel 4×4 外廓。
* Citroën 官方规格确认：乘用版为 `4380 × 1810 × 1852 mm`；厢式车按配置分别为 L1 `4380 × 1810 × 1801/1828/1831 mm`、L2 `4628 × 1810 × 1828 mm`，平台底盘为 `4237 × 1810 × 1828 mm`。([汽车档案馆][1])
* B9 Electric 的 L1、L2 外廓直接复用对应厢式尺寸组；官方资料确认后期 Electric 增加 L2 车身。([Stellantis Media][2])
* B9 Dangel 4×4 L1 采用 `4380 × 1810 × 1865 mm` 独立尺寸组。([Ultimate Specs][3])
* 本轮新增完成 20 个 Ktype、29 条 READY 映射和 7 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* PENDING Ktype：13
* READY 映射行：138
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
112390	112390	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
112392_l1	112392	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	BlueHDi 100 L1标准载荷外廓。	READY
112392_l2	112392	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	BlueHDi 100 L2长车身外廓。	READY
118107	118107	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
122105	122105	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
112391	112391	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
112393	112393	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	BlueHDi 120 L1标准载荷外廓。	READY
113667	113667	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi或BlueHDi 75 L1标准载荷外廓。	READY
56261	56261	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
122102	122102	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1乘用版外廓。	READY
122106	122106	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
113668	113668	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
122103	122103	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
11048_l1_low	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 90 L1标准载荷外廓。	READY
11048_l1_high	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 90 L1高载荷外廓。	READY
11048_l1_xtr	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 90 L1 XTR升高悬架外廓。	READY
11048_l2	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 90 L2长车身外廓。	READY
116222_l1_low	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 90 L1标准载荷外廓。	READY
116222_l1_high	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 90 L1高载荷外廓。	READY
116222_l1_xtr	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 90 L1 XTR升高悬架外廓。	READY
116222_l2	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 90 L2长车身外廓。	READY
59312	59312	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
122101	122101	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1乘用版外廓。	READY
122104	122104	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
118106	118106	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
107936_l1	107936	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	Electric L1短车身外廓。	READY
107936_l2	107936	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	Electric L2长车身外廓。	READY
108166_l1	108166	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	Electric L1短车身外廓。	READY
108166_l2	108166	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	Electric L2长车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-II-B9-MPV-01	4380	1810	1852	Citroën Berlingo Multispace 2012 official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2022/08/Citroen-Berlingo-Multispace-2012-UK.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	4380	1810	1801	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	4380	1810	1828	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	4380	1810	1831	Citroën Berlingo 2010 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1828	Citroën Berlingo 2010 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf
EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	4380	1810	1865	UltimateSpecs Citroën Berlingo II Multispace HDi 90 4x4 Dangel specifications	https://www.ultimatespecs.com/car-specs/Citroen/64893/Citroen-Berlingo-II-Multispace-Tonic-HDi-90-4x4-Dangel.html
```

## 下一步优先处理

1. 闭合剩余 B9 Ktype `11049`、`56262`、`11050` 的发动机与 L1/L2/载荷外廓边界。
2. 闭合 Berlingo I 的 4 个 Dangel 4×4 Ktype。
3. 最后处理 Berlingo III `K9`、ë-Berlingo、2023 改款及 2025 4×4 分支。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2022/08/Citroen-Berlingo-Multispace-2012-UK.pdf?utm_source=chatgpt.com "Citroën Berlingo Multispace"
[2]: https://www.media.stellantis.com/uk-en/citroen/press/citroen-extends-berlingo-electric-van-range-with-new-l2-version?utm_source=chatgpt.com "CITROËN EXTENDS BERLINGO ELECTRIC VAN RANGE ..."
[3]: https://www.ultimatespecs.com/car-specs/Citroen/64893/Citroen-Berlingo-II-Multispace-Tonic-HDi-90-4x4-Dangel.html?utm_source=chatgpt.com "Citroen Berlingo II Multispace Tonic HDi 90 4x4 Dangel"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已完成 B9 剩余 `11049`、`56262`、`11050`：HDi 110/115 厢式版复用既有 L1/L2、载荷及 XTR 尺寸组；VTi 120 按其乘用版配置关联既有 B9 MPV 尺寸组，不重复建组。([汽车档案馆][1])
* 已闭合 Berlingo III K9 乘用版 M/XL，以及改款前后 Van 的 M/XL、低/高车身分支。官方资料确认不含后视镜宽度为 `1848 mm`；乘用版为 `4403/4753 × 1848 × 1844/1849 mm`，改款 Van 为 `4401/4751 × 1848 × 1796–1860 mm`。
* `801456` 已拆分 M/XL Dangel 4×4 分支，采用 `4403/4753 × 1848 × 1895 mm`；因直接尺寸记录对应同一 Dangel K9 四驱车身但动力配置不同，映射置信度标记为 `MEDIUM`。([Motoro][2])
* 第一代 Berlingo 的 4 个旧款 Dangel Ktype 仍保持 PENDING：目前仅完整确认 2004—2008 M59 Dangel 外廓为 `4137 × 1724 × 1950 mm`，尚缺早期 M49 Dangel 同一配置的完整三维来源，未使用普通前驱车身尺寸拼接。([AutoScout24][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* PENDING Ktype：4
* READY 映射行：163
* PENDING 映射行：4
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11049_l1_low	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 110 L1标准载荷外廓。	READY
11049_l1_high	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 110 L1高载荷外廓。	READY
11049_l1_xtr	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 110 L1 XTR升高悬架外廓。	READY
11049_l2	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 110 L2长车身外廓。	READY
56262_l1_low	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 115 L1标准载荷外廓。	READY
56262_l1_high	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 115 L1高载荷外廓。	READY
56262_l1_xtr	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 115 L1 XTR升高悬架外廓。	READY
56262_l2	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 115 L2长车身外廓。	READY
11050	11050	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	MEDIUM	VTi 120对应B9乘用版外廓。	READY
15050	15050	MPV	Berlingo I			LOW	候选包含早期M49 Dangel外廓。	PENDING: 缺少早期M49 Dangel同配置完整三维来源
15052	15052	MPV	Berlingo I			LOW	生产期跨M49与M59 Dangel外廓。	PENDING: M49与M59四驱分支尚未全部闭合
15051	15051	Van	Berlingo I			LOW	生产期跨M49与M59 Dangel厢式外廓。	PENDING: M49与M59四驱分支尚未全部闭合
18877	18877	Van	Berlingo I			LOW	候选包含M49后期与M59 Dangel外廓。	PENDING: 缺少M49后期Dangel同配置完整三维来源
150197_m	150197	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	K9 M标准长度乘用版外廓。	READY
150197_xl	150197	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	K9 XL长轴乘用版外廓。	READY
145276_m_low	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-LOW-01	HIGH	改款前M低车身厢式外廓。	READY
145276_m_high	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-HIGH-01	HIGH	改款前M高车身厢式外廓。	READY
145276_xl_low	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-LOW-01	HIGH	改款前XL低车身厢式外廓。	READY
145276_xl_high	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-HIGH-01	HIGH	改款前XL高车身厢式外廓。	READY
145516_m	145516	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	ë-Berlingo M乘用版外廓。	READY
145516_xl	145516	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	ë-Berlingo XL乘用版外廓。	READY
157796_m_low	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-LOW-01	HIGH	改款M低车身厢式外廓。	READY
157796_m_high	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-HIGH-01	HIGH	改款M高车身厢式外廓。	READY
157796_xl_low	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-LOW-01	HIGH	改款XL低车身厢式外廓。	READY
157796_xl_high	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-HIGH-01	HIGH	改款XL高车身厢式外廓。	READY
157797_m	157797	MPV	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	改款M乘用版三维未变化。	READY
157797_xl	157797	MPV	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	改款XL乘用版三维未变化。	READY
801456_m	801456	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-4X4-VAN-M-01	MEDIUM	Dangel 4×4 M升高车身外廓。	READY
801456_xl	801456	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-4X4-VAN-XL-01	MEDIUM	Dangel 4×4 XL升高车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën ë-Berlingo January 2023 official specifications; Auto-Data Citroen Berlingo III specifications	https://www.media.stellantis.com/uploads/uk/model-pricelist/citroeneberlingopricespecjan2023-63a9af48b0fcd.pdf;https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën ë-Berlingo January 2023 official specifications; Auto-Data Citroen Berlingo III specifications	https://www.media.stellantis.com/uploads/uk/model-pricelist/citroeneberlingopricespecjan2023-63a9af48b0fcd.pdf;https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-CITROEN-BERLINGO-III-K9-VAN-M-LOW-01	4403	1848	1796	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-M-HIGH-01	4403	1848	1860	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-LOW-01	4753	1848	1812	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-HIGH-01	4753	1848	1860	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-LOW-01	4401	1848	1796	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-HIGH-01	4401	1848	1860	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-LOW-01	4751	1848	1812	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-HIGH-01	4751	1848	1860	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-M-01	4403	1848	1895	Swiss FEDRO approved Citroen-Dangel Berlingo 4x4 specifications; Automobiles Dangel conversion price list	https://motoro.ch/en/fiche-technique/citroen-dangel/berlingo-4x4;https://www.dangel.com/sites/www.dangel.fr/files/Pricelist%20Dangel%20from%2001_08_2025.pdf
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-XL-01	4753	1848	1895	Swiss FEDRO approved Citroen-Dangel Berlingo 4x4 specifications; Automobiles Dangel conversion price list	https://motoro.ch/en/fiche-technique/citroen-dangel/berlingo-4x4;https://www.dangel.com/sites/www.dangel.fr/files/Pricelist%20Dangel%20from%2001_08_2025.pdf
```

## 下一步优先处理

1. 仅处理 `15050`、`15052`、`15051`、`18877` 的早期 M49 Dangel 4×4 完整三维与 M49/M59 分支边界。
2. 不再重新核对其余 96 个 READY Ktype 或已闭合的 42 个尺寸组。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2022/10/Citroen-Berlingo-Van-2010-UK.pdf?utm_source=chatgpt.com "CITROËN BERLINGO"
[2]: https://motoro.ch/en/fiche-technique/citroen-dangel/berlingo-4x4 "motoro.ch"
[3]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/dangel/berlingo/?srsltid=AfmBOorFuPYlSgFxQYKAONHxEBs00-xViuwfMav8gh23B4oPPTpxo2Iw "Dangel Berlingo - Spécifications techniques | AutoScout24"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3401-3500_ktype_dimension_mapping_final.tsv
- left18448_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合剩余 4 个旧款 Berlingo Dangel Ktype，并按 M49、M59 两种物理外廓拆分。M49 组为 `4123 × 1719 × 1912 mm`，M59 组为 `4137 × 1724 × 1950 mm`。([Motoro][1])
* 已补齐跨批次复用的 Sebring 尺寸组来源，其中第二代 Cabriolet 的 `4921 × 1792 × 1401 mm` 明确采用不含后视镜宽度。([汽车目录][2])
* 已完成唯一一次机械收尾：固定表头、唯一主键、100 个 Ktype 覆盖、映射引用闭合、尺寸与来源完整、无孤立尺寸组。
* 两份最终 TSV 已生成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：170
* PENDING：0
* DIMENSION_GROUP：44
* 机械校验：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
114797	114797	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	HIGH	第三代四门轿车。	READY
124849	124849	Convertible	Sebring III	JS	2	EU-CHRYSLER-SEBRING-III-CONVERTIBLE-01	HIGH	第三代双门敞篷车。	READY
15498	15498	Sedan	Sebring II	JR	4	EU-CHRYSLER-SEBRING-II-SEDAN-01	HIGH	第二代四门轿车。	READY
15859	15859	Convertible	Sebring II		2	EU-CHRYSLER-SEBRING-II-CONVERTIBLE-EU-01	HIGH	第二代双门敞篷车。	READY
59760	59760	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	HIGH	第三代四门轿车。	READY
14319	14319	Sedan	Stratus I	JA	4	EU-CHRYSLER-STRATUS-I-SEDAN-01	HIGH	JA四门轿车。	READY
10225	10225	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	HIGH	1998年SR II GTS三门掀背式双门跑车。	READY
10226	10226	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	HIGH	1998年SR II RT/10双门敞篷车。	READY
18659	18659	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
18660_sr_i	18660	Convertible	Viper first generation	SR I	2	EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR I敞篷分支。	READY
18660_sr_ii	18660	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR II敞篷分支。	READY
18661	18661	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
18662_sr_i	18662	Convertible	Viper first generation	SR I	2	EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR I敞篷分支。	READY
18662_sr_ii	18662	Convertible	Viper first generation	SR II	2	EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	MEDIUM	Ktype覆盖SR II敞篷分支。	READY
18663	18663	Coupe	Viper first generation	SR II	3	EU-CHRYSLER-VIPER-SR-II-COUPE-01	MEDIUM	Coupe仅对应SR II GTS外廓；输入起始日期早于Coupe投产。	READY
142652_swb	142652	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴外廓。	READY
142652_lwb	142652	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-LWB-01	HIGH	ES长轴Grand外廓。	READY
142651_swb	142651	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴外廓。	READY
142651_lwb	142651	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-LWB-01	HIGH	ES长轴Grand外廓。	READY
14670_swb	14670	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
14670_lwb	14670	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
59949_swb	59949	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
59949_lwb	59949	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5131_swb	5131	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5131_lwb	5131	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5134_swb	5134	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5134_lwb	5134	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5132_swb	5132	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5132_lwb	5132	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
5133_swb	5133	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
5133_lwb	5133	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
11028_swb	11028	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴外廓。	READY
11028_lwb	11028	MPV	Voyager III	GS-53		EU-CHRYSLER-VOYAGER-III-LWB-01	HIGH	GS-53长轴Grand外廓。	READY
57287	57287	MPV	Voyager II	ES		EU-CHRYSLER-VOYAGER-II-SWB-01	HIGH	ES短轴Voyager外廓。	READY
143208	143208	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143209	143209	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143212	143212	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴厢式外廓。	READY
143210	143210	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴AWD厢式外廓。	READY
143211	143211	Van	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	HIGH	GS-52短轴AWD厢式外廓。	READY
14681_swb_prefl	14681	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
14681_swb_facelift	14681	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
59940_swb_prefl	59940	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
59940_swb_facelift	59940	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
38751	38751	MPV	Voyager III	GS-52		EU-CHRYSLER-VOYAGER-III-SWB-01	MEDIUM	生产日期对应GS-52短轴第三代外廓；输入代次标记前移。	READY
14894_lwb_prefl	14894	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	RG长轴Grand前期外廓。	READY
14894_lwb_facelift	14894	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	RG长轴Grand改款外廓。	READY
16433_lwb_prefl	16433	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	RG长轴Grand前期外廓。	READY
16433_lwb_facelift	16433	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	RG长轴Grand改款外廓。	READY
14895_swb_prefl	14895	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	HIGH	RG标准轴距前期外廓。	READY
14895_swb_facelift	14895	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	RG标准轴距改款外廓。	READY
18267_swb	18267	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	HIGH	改款标准轴距外廓。	READY
18267_lwb	18267	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	改款长轴Grand外廓。	READY
16435_lwb_prefl	16435	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	AWD长轴Grand前期外廓。	READY
16435_lwb_facelift	16435	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	AWD长轴Grand改款外廓。	READY
16434_lwb_prefl	16434	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	AWD长轴Grand前期外廓。	READY
16434_lwb_facelift	16434	MPV	Voyager IV	RG		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	AWD长轴Grand改款外廓。	READY
143246_lwb_prefl	143246	Van	Voyager IV	S-53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	S-53长轴厢式前期外廓。	READY
143246_lwb_facelift	143246	Van	Voyager IV	S-53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	S-53长轴厢式改款外廓。	READY
143247_lwb_prefl	143247	Van	Voyager IV	SYX53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	SYX53长轴厢式前期外廓。	READY
143247_lwb_facelift	143247	Van	Voyager IV	SYX53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	SYX53长轴厢式改款外廓。	READY
143248_lwb_prefl	143248	Van	Voyager IV	SCH53		EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	HIGH	SCH53长轴AWD厢式前期外廓。	READY
143248_lwb_facelift	143248	Van	Voyager IV	SCH53		EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	HIGH	SCH53长轴AWD厢式改款外廓。	READY
14136	14136	Van	Acadiane			EU-CITROEN-ACADIANE-VAN-01	HIGH	Acadiane厢式车外廓。	READY
15360	15360	Van	Acadiane			EU-CITROEN-ACADIANE-VAN-01	HIGH	Acadiane厢式车外廓。	READY
143386	143386	Hatchback	Ami I	Z2CA	2	EU-CITROEN-AMI-I-HATCHBACK-01	HIGH	2020版封闭式双门电动微型车。	READY
161168	161168	Hatchback	Ami I facelift	Z2CA	2	EU-CITROEN-AMI-I-FACELIFT-HATCHBACK-01	HIGH	2025改款官方三维与早期车型不同。	READY
19005_3dr	19005	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	Ktype覆盖AX 10三门分支。	READY
19005_5dr	19005	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	Ktype覆盖AX 10五门分支；三维与三门相同。	READY
6022	6022	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
6023	6023	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
15048	15048	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	HIGH	AX GTI三门车身。	READY
18870_3dr	18870	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 4x4三门分支。	READY
18870_5dr	18870	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 4x4五门分支；三维与三门相同。	READY
6020_3dr	6020	Hatchback	AX	ZA	3	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 11 CAT三门分支。	READY
6020_5dr	6020	Hatchback	AX	ZA	5	EU-CITROEN-AX-HATCHBACK-01	MEDIUM	AX 11 CAT五门分支；三维与三门相同。	READY
5722_m49_early	5722	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5722_m49_late	5722	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5722_m59	5722	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
18614	18614	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
18615	18615	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
5719_m49_early	5719	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5719_m49_late	5719	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5719_m59	5719	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
17674	17674	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
17675	17675	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
16155_m49_late	16155	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
16155_m59	16155	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
112390	112390	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
112392_l1	112392	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	BlueHDi 100 L1标准载荷外廓。	READY
112392_l2	112392	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	BlueHDi 100 L2长车身外廓。	READY
118107	118107	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
122105	122105	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
112391	112391	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
112393	112393	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	BlueHDi 120 L1标准载荷外廓。	READY
113667	113667	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi或BlueHDi 75 L1标准载荷外廓。	READY
11049_l1_low	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 110 L1标准载荷外廓。	READY
11049_l1_high	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 110 L1高载荷外廓。	READY
11049_l1_xtr	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 110 L1 XTR升高悬架外廓。	READY
11049_l2	11049	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 110 L2长车身外廓。	READY
56261	56261	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
56262_l1_low	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 115 L1标准载荷外廓。	READY
56262_l1_high	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 115 L1高载荷外廓。	READY
56262_l1_xtr	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 115 L1 XTR升高悬架外廓。	READY
56262_l2	56262	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 115 L2长车身外廓。	READY
122102	122102	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1乘用版外廓。	READY
122106	122106	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
19026	19026	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
113668	113668	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	HIGH	B9标准长度乘用版外廓。	READY
122103	122103	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
11048_l1_low	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 90 L1标准载荷外廓。	READY
11048_l1_high	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 90 L1高载荷外廓。	READY
11048_l1_xtr	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 90 L1 XTR升高悬架外廓。	READY
11048_l2	11048	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 90 L2长车身外廓。	READY
19027	19027	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
116222_l1_low	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	HDi 90 L1标准载荷外廓。	READY
116222_l1_high	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	HIGH	HDi 90 L1高载荷外廓。	READY
116222_l1_xtr	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	HIGH	HDi 90 L1 XTR升高悬架外廓。	READY
116222_l2	116222	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	HDi 90 L2长车身外廓。	READY
59312	59312	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
122101	122101	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1乘用版外廓。	READY
122104	122104	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	MEDIUM	Dangel 4×4 L1厢式外廓。	READY
118106	118106	Pickup	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	HIGH	B9平台底盘外廓。	READY
150197_m	150197	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	K9 M标准长度乘用版外廓。	READY
150197_xl	150197	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	K9 XL长轴乘用版外廓。	READY
11050	11050	MPV	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-MPV-01	MEDIUM	VTi 120对应B9乘用版外廓。	READY
15049_m49_early	15049	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
15049_m49_late	15049	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
18873_m49_early	18873	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
18873_m49_late	18873	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
15050	15050	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	MEDIUM	M49 Dangel 4×4乘用版外廓。	READY
5720_m49_early	5720	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
5720_m49_late	5720	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
5720_m59	5720	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
10227_m49_early	10227	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
10227_m49_late	10227	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
10227_m59	10227	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
15052_m49	15052	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	MEDIUM	M49 Dangel 4×4乘用版外廓。	READY
15052_m59	15052	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-DANGEL-4X4-01	MEDIUM	M59 Dangel 4×4乘用版外廓。	READY
14443_m49_early	14443	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
14443_m49_late	14443	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
14443_m59	14443	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
15051_m49	15051	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	HIGH	M49 Dangel 4×4厢式外廓。	READY
15051_m59	15051	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-DANGEL-4X4-01	MEDIUM	M59 Dangel 4×4厢式外廓。	READY
14491_m49_early	14491	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期外廓。	READY
14491_m49_late	14491	MPV	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期外廓。	READY
14491_m59	14491	MPV	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款外廓。	READY
15755_m49_early	15755	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-EARLY-01	HIGH	M49早期厢式外廓。	READY
15755_m49_late	15755	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-LATE-01	HIGH	M49后期厢式外廓。	READY
15755_m59	15755	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59改款厢式外廓。	READY
18877_m49	18877	Van	Berlingo I	M49		EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	MEDIUM	M49后期Dangel 4×4厢式外廓。	READY
18877_m59	18877	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-DANGEL-4X4-01	MEDIUM	M59 Dangel 4×4厢式外廓。	READY
145276_m_low	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-LOW-01	HIGH	改款前M低车身厢式外廓。	READY
145276_m_high	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-HIGH-01	HIGH	改款前M高车身厢式外廓。	READY
145276_xl_low	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-LOW-01	HIGH	改款前XL低车身厢式外廓。	READY
145276_xl_high	145276	Van	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-VAN-XL-HIGH-01	HIGH	改款前XL高车身厢式外廓。	READY
145516_m	145516	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	ë-Berlingo M乘用版外廓。	READY
145516_xl	145516	MPV	Berlingo III	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	ë-Berlingo XL乘用版外廓。	READY
157796_m_low	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-LOW-01	HIGH	改款M低车身厢式外廓。	READY
157796_m_high	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-HIGH-01	HIGH	改款M高车身厢式外廓。	READY
157796_xl_low	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-LOW-01	HIGH	改款XL低车身厢式外廓。	READY
157796_xl_high	157796	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-HIGH-01	HIGH	改款XL高车身厢式外廓。	READY
157797_m	157797	MPV	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	改款M乘用版三维未变化。	READY
157797_xl	157797	MPV	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	改款XL乘用版三维未变化。	READY
801456_m	801456	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-4X4-VAN-M-01	MEDIUM	Dangel 4×4 M升高车身外廓。	READY
801456_xl	801456	Van	Berlingo III facelift	K9		EU-CITROEN-BERLINGO-III-K9-4X4-VAN-XL-01	MEDIUM	Dangel 4×4 XL升高车身外廓。	READY
59304	59304	Van	Berlingo I	M59		EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	HIGH	M59电动厢式外廓。	READY
107936_l1	107936	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	Electric L1短车身外廓。	READY
107936_l2	107936	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	Electric L2长车身外廓。	READY
108166_l1	108166	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	HIGH	Electric L1短车身外廓。	READY
108166_l2	108166	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	HIGH	Electric L2长车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_3401-3500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-SEBRING-III-SEDAN-EU-01	4850	1843	1497	Auto-Data Chrysler Sebring model specifications	https://www.auto-data.net/en/chrysler-sebring-model-1664
EU-CHRYSLER-SEBRING-III-CONVERTIBLE-01	4922	1816	1485	Chrysler 2009 Sebring Convertible official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2009_ChryslerSebringConvertibleSpecifications.pdf
EU-CHRYSLER-SEBRING-II-SEDAN-01	4844	1792	1394	Automobile-Catalog 2005 Chrysler Sebring Limited 2.7 V6 specifications	https://www.automobile-catalog.com/car/2005/522245/chrysler_sebring_limited_2_7_v6_automatic.html
EU-CHRYSLER-SEBRING-II-CONVERTIBLE-EU-01	4921	1792	1401	Automobile-Catalog 2005 Chrysler Sebring Cabrio Touring 2.7 V6 specifications	https://www.automobile-catalog.com/car/2005/522335/chrysler_sebring_cabrio_touring_2_7_v6_automatic.html
EU-CHRYSLER-STRATUS-I-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus (JA) specifications	https://www.auto-data.net/en/chrysler-stratus-ja-generation-3236
EU-CHRYSLER-VIPER-SR-II-COUPE-01	4488	1923	1194	Edmunds 1998 Dodge Viper GTS specifications	https://www.edmunds.com/dodge/viper/1998/st-13055/features-specs/
EU-CHRYSLER-VIPER-SR-II-CONVERTIBLE-01	4448	1923	1118	Edmunds 1998 Dodge Viper RT/10 specifications	https://www.edmunds.com/dodge/viper/1998/st-13057/features-specs/
EU-CHRYSLER-VIPER-SR-I-CONVERTIBLE-01	4448	1924	1117	Automobile-Catalog 1995 Chrysler Viper RT/10 Europe specifications	https://www.automobile-catalog.com/car/1995/685385/chrysler_viper_rt10.html
EU-CHRYSLER-VOYAGER-II-SWB-01	4525	1830	1707	Automobile-Catalog 1994 Chrysler Voyager 2.5 TD specifications	https://www.automobile-catalog.com/car/1994/518180/chrysler_voyager_2_5_td.html
EU-CHRYSLER-VOYAGER-II-LWB-01	4896	1830	1707	Automobile-Catalog 1993 Chrysler Grand Voyager 2.5 TD specifications	https://www.automobile-catalog.com/car/1993/518315/chrysler_grand_voyager_le_2_5_td.html
EU-CHRYSLER-VOYAGER-III-SWB-01	4733	1950	1740	Chrysler manufacturer body-code filing; Automobile-Catalog 1999 Chrysler Voyager specifications	https://www.nhtsa.gov/file-downloads/download?p=nhtsa%2Fdownloads%2FMfrMail%2F01-22-N11B-6012.pdf;https://www.automobile-catalog.com/car/1999/519860/chrysler_voyager_family_2_4.html
EU-CHRYSLER-VOYAGER-III-LWB-01	5070	1950	1740	Chrysler manufacturer body-code filing; Automobile-Catalog 1999 Chrysler Grand Voyager specifications	https://www.nhtsa.gov/file-downloads/download?p=nhtsa%2Fdownloads%2FMfrMail%2F01-22-N11B-6012.pdf;https://www.automobile-catalog.com/car/1999/519980/chrysler_grand_voyager_se_2_4.html
EU-CHRYSLER-VOYAGER-IV-SWB-PREFL-01	4803	1996	1750	Automobile-Catalog 2001 Chrysler Voyager 2.4L specifications	https://www.automobile-catalog.com/car/2001/522350/chrysler_voyager_2_4l_automatic.html
EU-CHRYSLER-VOYAGER-IV-SWB-FACELIFT-01	4810	1997	1749	DaimlerChrysler 2005 Chrysler Voyager and Grand Voyager Europe press specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/attachments/ChryslerGrandVoyagerEnglish.pdf
EU-CHRYSLER-VOYAGER-IV-LWB-PREFL-01	5049	1997	1749	Automobile-Catalog 2001 Chrysler Grand Voyager 2.5 CRD specifications	https://www.automobile-catalog.com/car/2001/522980/chrysler_grand_voyager_limited_2_5_crd.html
EU-CHRYSLER-VOYAGER-IV-LWB-FACELIFT-01	5096	1997	1749	DaimlerChrysler 2005 Chrysler Voyager and Grand Voyager Europe press specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/attachments/ChryslerGrandVoyagerEnglish.pdf
EU-CITROEN-ACADIANE-VAN-01	4030	1500	1825	Auto-Data Citroen Acadiane specifications	https://www.auto-data.net/en/citroen-acadiane-generation-3299
EU-CITROEN-AMI-I-HATCHBACK-01	2410	1390	1520	Citroën Stellantis Media Ami official technical characteristics	https://www.media.stellantis.com/em-en/citroen/press/ami-100-electric-mobility-accessible-to-all
EU-CITROEN-AMI-I-FACELIFT-HATCHBACK-01	2460	1390	1525	Citroën official Ami technical characteristics July-November 2025	https://www.media.stellantis.com/uploads/fr/model-document/caracteristiques_techniques_ami_1125-69a99a625a11c.pdf
EU-CITROEN-AX-HATCHBACK-01	3495	1596	1355	Auto-Data Citroen AX specifications	https://www.auto-data.net/en/citroen-ax-generation-3321
EU-CITROEN-BERLINGO-I-M49-EARLY-01	4108	1698	1802	Automobile-Catalog 1998 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/1998/547775/citroen_berlingo_multispace_1_9_d.html
EU-CITROEN-BERLINGO-I-M49-LATE-01	4108	1719	1802	Automobile-Catalog 2001 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/2001/547850/citroen_berlingo_multispace_1_9_d.html
EU-CITROEN-BERLINGO-I-M59-FACELIFT-01	4137	1724	1810	Automobile-Catalog 2005 Citroen Berlingo Multispace specifications	https://www.automobile-catalog.com/car/2005/550205/citroen_berlingo_multispace_1_9_d.html
EU-CITROEN-BERLINGO-II-B9-MPV-01	4380	1810	1852	Citroën Berlingo Multispace 2012 official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2022/08/Citroen-Berlingo-Multispace-2012-UK.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-LOW-01	4380	1810	1801	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1828	Citroën Berlingo 2010 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf
EU-CITROEN-BERLINGO-II-B9-4X4-L1-01	4380	1810	1865	UltimateSpecs Citroën Berlingo II Multispace HDi 90 4x4 Dangel specifications	https://www.ultimatespecs.com/car-specs/Citroen/64893/Citroen-Berlingo-II-Multispace-Tonic-HDi-90-4x4-Dangel.html
EU-CITROEN-BERLINGO-II-B9-VAN-L1-HIGH-01	4380	1810	1828	Citroën Berlingo 2010 and 2015 official UK brochures	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf;https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L1-XTR-01	4380	1810	1831	Citroën Berlingo 2010 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-Berlingo-UK.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën ë-Berlingo January 2023 official specifications; Auto-Data Citroen Berlingo III specifications	https://www.media.stellantis.com/uploads/uk/model-pricelist/citroeneberlingopricespecjan2023-63a9af48b0fcd.pdf;https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën ë-Berlingo January 2023 official specifications; Auto-Data Citroen Berlingo III specifications	https://www.media.stellantis.com/uploads/uk/model-pricelist/citroeneberlingopricespecjan2023-63a9af48b0fcd.pdf;https://www.auto-data.net/en/citroen-berlingo-model-1694
EU-CITROEN-BERLINGO-I-M49-DANGEL-4X4-01	4123	1719	1912	Swiss FEDRO type approval via Motoro	https://v2.motoro.ch/en/fiche-technique/citroen/berlingo-1-9d-4x4
EU-CITROEN-BERLINGO-I-M59-DANGEL-4X4-01	4137	1724	1950	ParuVendu Dangel Berlingo 4x4 2.0 HDi 2004 specifications	https://www.paruvendu.fr/fiches-techniques-auto/dangel-berlingo/4x4-2-0-hdi-bivouac-performance-6-cv-diesel/1089926/
EU-CITROEN-BERLINGO-III-K9-VAN-M-LOW-01	4403	1848	1796	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-M-HIGH-01	4403	1848	1860	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-LOW-01	4753	1848	1812	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-XL-HIGH-01	4753	1848	1860	Citroën ë-Berlingo and Berlingo Van official specifications	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/berlingo/Berlingo-price-and-specification-guide.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-LOW-01	4401	1848	1796	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-M-HIGH-01	4401	1848	1860	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-LOW-01	4751	1848	1812	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-FACELIFT-VAN-XL-HIGH-01	4751	1848	1860	Citroën ë-Berlingo and Berlingo Van MY24A official specifications	https://www.media.stellantis.com/uploads/uk/attachment/5204/citroenberlingoeberlingopricespecguide-65f8777a5c552.pdf
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-M-01	4403	1848	1895	Swiss FEDRO approved Citroen-Dangel Berlingo 4x4 specifications; Automobiles Dangel conversion price list	https://motoro.ch/en/fiche-technique/citroen-dangel/berlingo-4x4;https://www.dangel.com/sites/www.dangel.fr/files/Pricelist%20Dangel%20from%2001_08_2025.pdf
EU-CITROEN-BERLINGO-III-K9-4X4-VAN-XL-01	4753	1848	1895	Swiss FEDRO approved Citroen-Dangel Berlingo 4x4 specifications; Automobiles Dangel conversion price list	https://motoro.ch/en/fiche-technique/citroen-dangel/berlingo-4x4;https://www.dangel.com/sites/www.dangel.fr/files/Pricelist%20Dangel%20from%2001_08_2025.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_3401-3500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://v2.motoro.ch/en/fiche-technique/citroen/berlingo-1-9d-4x4 "v2.motoro.ch"
[2]: https://www.automobile-catalog.com/car/2005/522335/chrysler_sebring_cabrio_touring_2_7_v6_automatic.html "https://www.automobile-catalog.com/car/2005/522335/chrysler_sebring_cabrio_touring_2_7_v6_automatic.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4056 行）
- 累计尺寸组：dimension_groups_final.tsv（1194 行）

