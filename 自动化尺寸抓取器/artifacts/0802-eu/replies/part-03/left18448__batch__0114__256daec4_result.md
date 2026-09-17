# 任务：left18448 第 11301-11400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0114__256daec4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11301-11400 行

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
left18448 第 11301-11400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MITSUBISHI-GRANDIS-2025-SUV-5D-01	4413	1797	1575

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mitsubishi	Grandis	1.8 HEV	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	162806
Mitsubishi	Grandis	2.0 Di-d	Großraumlimousine	Frontantrieb	Diesel	Sep 2005	Mar 2010	18778
Mitsubishi	Grandis	2.4 Mivec	Großraumlimousine	Frontantrieb	Benzin	Apr 2004	Dec 2011	18023
Mitsubishi	L 300 / delica ii	1.6	Bus	Heckantrieb	Benzin	Sep 1981	Oct 1986	3389
Mitsubishi	L 300 / delica ii	1.6	Bus	Heckantrieb	Benzin	Nov 1984	Feb 1987	3390
Mitsubishi	L 300 / delica ii	1.6	Kasten	Heckantrieb	Benzin	May 1980	Oct 1986	3397
Mitsubishi	L 300 / delica ii	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	Apr 1983	Apr 1994	10595
Mitsubishi	L 300 / delica ii	1.8 4WD	Bus	Allrad	Benzin	Aug 1984	Feb 1987	3391
Mitsubishi	L 300 / delica ii	2.0 4WD	Bus	Allrad	Benzin	Nov 1986	Feb 1987	3395
Mitsubishi	L 300 / delica ii	2.3 D	Bus	Heckantrieb	Diesel	Apr 1983	Oct 1986	3396
Mitsubishi	L 300 / delica ii	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 1986	Apr 1994	10597
Mitsubishi	L 300 iii	1.6	Kasten	Heckantrieb	Benzin	Nov 1986	May 1994	3398
Mitsubishi	L 300 iii	1.6	Bus	Heckantrieb	Benzin	Nov 1986	May 1994	3400
Mitsubishi	L 300 iii	2	Bus	Heckantrieb	Benzin	Nov 1986	May 2004	3405
Mitsubishi	L 300 iii	2	Bus	Heckantrieb	Benzin	Nov 1986	May 2004	3411
Mitsubishi	L 300 iii	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jul 1994	Apr 2000	10598
Mitsubishi	L 300 iii	2.4	Bus	Heckantrieb	Benzin	Nov 1990	May 2004	3412
Mitsubishi	L 300 iii	2.0 4WD	Bus	Allrad	Benzin	Dec 1986	May 2004	3402
Mitsubishi	L 300 iii	2.0 4WD	Bus	Allrad	Benzin	Nov 1986	May 2004	3406
Mitsubishi	L 300 iii	2.0 I	Bus	Heckantrieb	Benzin	Jun 1994	Oct 1998	5980
Mitsubishi	L 300 iii	2.4 4WD	Bus	Allrad	Benzin	Nov 1986	Dec 1990	3407
Mitsubishi	L 300 iii	2.4 4WD	Bus	Allrad	Benzin	Aug 1986	May 2004	3408
Mitsubishi	L 300 iii	2.5 D	Kasten	Heckantrieb	Diesel	Nov 1986	Feb 2006	3399
Mitsubishi	L 300 iii	2.5 D	Bus	Heckantrieb	Diesel	Nov 1986	May 2004	3409
Mitsubishi	L 300 iii	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Nov 1994	Apr 2000	10599
Mitsubishi	L 300 iii	2.5 TD 4WD	Bus	Allrad	Diesel	Dec 1987	May 2004	3410
Mitsubishi	L200	2	Pick-up	Heckantrieb	Benzin	Jun 1996	Dec 2007	8737
Mitsubishi	L200	2.0 4WD	Pick-up	Allrad	Benzin	Feb 1987	May 1994	59324
Mitsubishi	L200	2.4 4WD	Pick-up	Allrad	Benzin	Jun 1996	Dec 2007	8738
Mitsubishi	L200	2.4 Di-d 4WD	Pick-up	Allrad	Diesel	Sep 2015	-	111099
Mitsubishi	L200	2.4 Di-d 4WD	Pick-up	Allrad	Diesel	Sep 2015	-	116161
Mitsubishi	L200	2.5 D	Pick-up	Heckantrieb	Diesel	Jun 1996	Dec 2007	8739
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	Aug 2007	Dec 2015	10981
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	Jan 2010	Dec 2015	125748
Mitsubishi	L200	2.5 Di-d	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 2007	Dec 2015	126659
Mitsubishi	L200	2.5 Di-d 16V 4WD	Pick-up	Allrad	Diesel	Apr 2007	Dec 2015	116196
Mitsubishi	L200	2.5 Di-d 4WD	Pritsche/Fahrgestell	Allrad	Diesel	Sep 2009	Dec 2015	57471
Mitsubishi	L200	2.5 Di-d 4WD	Pick-up	Allrad	Diesel	Nov 2014	-	117261
Mitsubishi	L200	2.5 TD 4WD	Pick-up	Allrad	Diesel	Jun 1996	Dec 2007	8740
Mitsubishi	L200	2.5 TD 4WD	Pick-up	Allrad	Diesel	Sep 2001	Dec 2007	17459
Mitsubishi	L200	2.5 TD 4WD	Pick-up	Allrad	Diesel	Aug 2001	Dec 2007	17755
Mitsubishi	L400	2.4	Bus	Heckantrieb	Benzin	Sep 1996	Jun 2005	54969
Mitsubishi	L400	2.4 4WD	Bus	Allrad	Benzin	Sep 1996	Jun 2005	54970
Mitsubishi	L400	2500 TD	Bus	Heckantrieb	Diesel	May 1995	Jun 2005	14069
Mitsubishi	L400	2500 TD	Kasten	Heckantrieb	Diesel	Sep 1996	Jun 2005	14070
Mitsubishi	L400	2500 TD 4WD	Kasten	Allrad	Diesel	Sep 1996	Jun 2005	18401
Mitsubishi	Lancer celeste	1.6 ST	Coupe	Heckantrieb	Benzin	Jan 1977	Jun 1981	3322
Mitsubishi	Lancer celeste	2.0 GSR	Coupe	Heckantrieb	Benzin	Oct 1975	Jun 1981	3323
Mitsubishi	Lancer celeste	2.0 GSR	Coupe	Heckantrieb	Benzin	Jan 1977	Jun 1981	3324
Mitsubishi	Lancer celeste	2.0 GSR	Coupe	Heckantrieb	Benzin	Jan 1979	Jun 1981	3325
Mitsubishi	Lancer iv	1.5	Schrägheck	Frontantrieb	Benzin	Jun 1988	May 1992	18022
Mitsubishi	Lancer iv	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	Jun 1992	Dec 1993	3314
Mitsubishi	Lancer iv	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	Nov 1989	May 1992	3315
Mitsubishi	Lancer iv	EVO IV	Stufenheck	Allrad	Benzin	Aug 1996	Dec 1997	125528
Mitsubishi	Lancer v	1.8 16V	Stufenheck	Frontantrieb	Benzin	Jun 1992	Dec 1993	16887
Mitsubishi	Lancer v station wagon	1.6 16V 4WD	Kombi	Allrad	Benzin	Dec 1992	Oct 2003	5092
Mitsubishi	Lancer vi	1.5 12V	Stufenheck	Frontantrieb	Benzin	Jul 1996	Aug 2003	11307
Mitsubishi	Lancer vi	1.8 16V	Stufenheck	Frontantrieb	Benzin	Sep 1995	Aug 2003	18664
Mitsubishi	Lancer vi	EVO V	Stufenheck	Allrad	Benzin	Jan 1998	Dec 1998	14893
Mitsubishi	Lancer vii	1.3	Stufenheck	Frontantrieb	Benzin	Sep 2003	Dec 2013	17750
Mitsubishi	Lancer vii	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2003	Dec 2013	17751
Mitsubishi	Lancer vii	1.6	Kombi	Frontantrieb	Benzin	Sep 2003	Oct 2008	17752
Mitsubishi	Lancer vii	2	Kombi	Frontantrieb	Benzin	Sep 2003	Dec 2007	17753
Mitsubishi	Lancer vii	2	Stufenheck	Frontantrieb	Benzin	Dec 2003	Dec 2013	18212
Mitsubishi	Lancer vii	EVO IX - Fq-360	Stufenheck	Allrad	Benzin	Jul 2006	Dec 2007	125608
Mitsubishi	Lancer vii	EVO VII	Stufenheck	Allrad	Benzin	Jan 2001	Jan 2003	125584
Mitsubishi	Lancer vii	EVO Viii	Stufenheck	Allrad	Benzin	Apr 2003	Mar 2005	125592
Mitsubishi	Lancer vii	EVO Viii - 260	Stufenheck	Allrad	Benzin	Mar 2004	Jul 2005	17904
Mitsubishi	Lancer vii	EVO Viii - Fq-300	Stufenheck	Allrad	Benzin	Apr 2003	Apr 2004	125593
Mitsubishi	Lancer vii	EVO Viii - Fq-300	Stufenheck	Allrad	Benzin	Apr 2003	Apr 2004	125594
Mitsubishi	Lancer vii	EVO Viii - Fq-330	Stufenheck	Allrad	Benzin	Oct 2003	Aug 2006	125596
Mitsubishi	Lancer vii	EVO Viii - Fq-340	Stufenheck	Allrad	Benzin	Apr 2004	Mar 2005	125600
Mitsubishi	Lancer vii	EVO Viii - Fq-400	Stufenheck	Allrad	Benzin	Oct 2004	Aug 2006	125602
Mitsubishi	Lancer viii	1.8	Stufenheck	Frontantrieb	Benzin	May 2010	-	3394
Mitsubishi	Lancer viii	1.5 Bifuel	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2010	-	55456
Mitsubishi	Lancer viii	1.6 Mivec	Stufenheck	Frontantrieb	Benzin	May 2010	-	3393
Mitsubishi	Lancer viii	1.8 Bifuel	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2010	-	55453
Mitsubishi	Lancer viii	1.8 Di-d	Stufenheck	Frontantrieb	Diesel	Jun 2010	-	34985
Mitsubishi	Lancer viii	1.8 Flexfuel	Stufenheck	Frontantrieb	Benzin/Ethanol	Mar 2009	-	10452
Mitsubishi	Lancer viii	2.0 I	Stufenheck	Frontantrieb	Benzin	Apr 2007	-	12186
Mitsubishi	Lancer viii	2.0 I 4WD	Stufenheck	Allrad	Benzin	Mar 2007	-	56825
Mitsubishi	Lancer viii	EVO X	Stufenheck	Allrad	Benzin	Oct 2007	Oct 2008	124205
Mitsubishi	Lancer viii	EVO X - Fq330	Stufenheck	Allrad	Benzin	Mar 2008	Jun 2015	34932
Mitsubishi	Lancer viii	EVO X - Fq360	Stufenheck	Allrad	Benzin	Mar 2008	Jun 2015	34933
Mitsubishi	Lancer viii sportback	1.5 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Mar 2010	-	55455
Mitsubishi	Lancer viii sportback	1.8 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2010	-	55454
Mitsubishi	Lancer viii sportback	1.8 Di-d	Schrägheck	Frontantrieb	Diesel	Jun 2010	-	34984
Mitsubishi	Lancer viii sportback	1.8 Flex	Schrägheck	Frontantrieb	Benzin/Ethanol	Mar 2009	-	10449
Mitsubishi	Lancer viii sportback	2.0 Ralliart 4WD	Schrägheck	Allrad	Benzin	Oct 2008	-	34937
Mitsubishi	Outlander i	2	SUV	Frontantrieb	Benzin	May 2003	Oct 2006	18983
Mitsubishi	Outlander i	2.0 4WD	SUV	Allrad	Benzin	May 2003	Oct 2006	17284
Mitsubishi	Outlander i	2.0 Turbo 4WD	SUV	Allrad	Benzin	Apr 2004	Oct 2006	18617
Mitsubishi	Outlander i	2.0 Turbo-r 4WD	SUV	Allrad	Benzin	Jan 2002	Oct 2006	18736
Mitsubishi	Outlander i	2.4 4WD	SUV	Allrad	Benzin	Nov 2003	Sep 2007	17400
Mitsubishi	Outlander i	2.4 4WD	SUV	Allrad	Benzin	May 2003	Oct 2006	18738
Mitsubishi	Outlander i	2.4 4WD	SUV	Allrad	Benzin	May 2003	Sep 2007	18739
Mitsubishi	Outlander ii	2.0 4WD	SUV	Allrad	Benzin	Nov 2006	Nov 2012	12146
Mitsubishi	Outlander ii van	Di-d 4WD	Kasten/SUV	Allrad	Diesel	Dec 2006	Jun 2010	142850
Mitsubishi	Outlander ii van	Di-d 4WD	Kasten/SUV	Allrad	Diesel	Sep 2010	Dec 2012	142851
Mitsubishi	Outlander iii	2	SUV	Frontantrieb	Benzin	Oct 2012	Dec 2022	56332


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Grandis、Lancer VII、Lancer VIII/Sportback、Lancer Evolution VII–X、Outlander I、Outlander II** 的候选物理车身。
* `162806` 直接复用跨批次已有的 `EU-MITSUBISHI-GRANDIS-2025-SUV-5D-01`，未重复建立尺寸组。
* Lancer Evolution X 普通车身与 FQ 外部空气动力学版本外廓不同，分别建立 `4495 mm` 与 `4505 mm` 长度组。([汽车目录][1])
* Outlander I 的普通欧洲 SUV 外廓与 `Turbo-R/Airtrek Turbo R` 矮车身外廓分开建组。([汽车目录][2])
* `Ktype=12146` 的生产区间跨越 Outlander II 改款，已拆分为 `prefl` 与 `facelift` 两条物理映射；同期 4Work 商用衍生分别复用对应外廓。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**43**
* READY 映射：**44**，其中 `12146` 拆分为 2 条派生映射
* PENDING 输入 Ktype：**57**
* 当前已确认尺寸组：**15**

  * 跨批次复用：1
  * 本轮首次建立：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
162806	162806	SUV	Grandis (2025)		5	EU-MITSUBISHI-GRANDIS-2025-SUV-5D-01	HIGH	2025 年重新启用名称的 5 门 SUV。	READY
18778	18778	MPV	Grandis I	NA8W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
18023	18023	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
17750	17750	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
17751	17751	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
17752	17752	Wagon	Lancer VII		5	EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	HIGH		READY
17753	17753	Wagon	Lancer VII		5	EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	HIGH		READY
18212	18212	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
125608	125608	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	HIGH		READY
125584	125584	Sedan	Lancer Evolution VII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VII-SEDAN-4D-01	HIGH		READY
125592	125592	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
17904	17904	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125593	125593	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125594	125594	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125596	125596	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125600	125600	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125602	125602	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
3394	3394	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
55456	55456	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
3393	3393	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
55453	55453	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
34985	34985	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
10452	10452	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
12186	12186	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
56825	56825	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
124205	124205	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-01	HIGH		READY
34932	34932	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	HIGH	FQ 前部空气动力学套件形成独立外廓。	READY
34933	34933	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	HIGH	FQ 前部空气动力学套件形成独立外廓。	READY
55455	55455	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
55454	55454	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
34984	34984	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
10449	10449	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
34937	34937	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
18983	18983	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
17284	17284	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18617	18617	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18736	18736	SUV	Outlander I / Airtrek Turbo R		5	EU-MITSUBISHI-OUTLANDER-I-TURBO-R-SUV-5D-01	MEDIUM	Turbo-R 对应 Airtrek 矮车身外廓，独立建组。	READY
17400	17400	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18738	18738	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18739	18739	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
12146_prefl	12146	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	MEDIUM	同一 Ktype 覆盖改款前外廓。	READY
12146_facelift	12146	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	MEDIUM	同一 Ktype 覆盖改款后外廓。	READY
142850	142850	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	HIGH	4Work 商用衍生，外部车身按同期 Outlander II。	READY
142851	142851	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	HIGH	4Work 商用衍生，外部车身按同期 Outlander II。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2005910/mitsubishi_grandis_2_4_classic.html
EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	4480	1695	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1994990/mitsubishi_lancer_1_6.html
EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	4485	1695	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1995020/mitsubishi_lancer_wagon_1_6.html
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	4490	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/1998080/mitsubishi_lancer_evolution_ix.html
EU-MITSUBISHI-LANCER-EVOLUTION-VII-SEDAN-4D-01	4455	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/1997390/mitsubishi_lancer_gsr_evolution_vii.html
EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	4490	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1997870/mitsubishi_lancer_evo_viii_gsr.html
EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1996325/mitsubishi_lancer_1_8_di-d_cleartec_inform.html
EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-01	4495	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1997675/mitsubishi_lancer_gsr_evolution_x_5-speed.html
EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	4505	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1998200/mitsubishi_lancer_evolution_x_gsr_fq-360.html
EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	4585	1760	1515	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1996220/mitsubishi_lancer_sportback_1_8.html
EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	4545	1750	1670	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2010515/mitsubishi_outlander_2_0_invite_4wd.html
EU-MITSUBISHI-OUTLANDER-I-TURBO-R-SUV-5D-01	4465	1750	1540	Automobile-Catalog; Cars-Directory	https://www.automobile-catalog.com/car/2002/2010050/mitsubishi_airtek_turbo_r.html;https://www.cars-directory.net/specs/mitsubishi/airtrek/2002_10/15848/
EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	4640	1800	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2011595/mitsubishi_outlander_2_0_di-d_4wd_inform_invite.html
EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	4665	1800	1720	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2011745/mitsubishi_outlander_2_2_di-d_plus_4wd_intense_instyle.html
```

## 下一步优先处理

1. 按 **L 300 / Delica II、L 300 III** 的 Bus、Kasten、Pritsche、2WD/4WD 与不同车长/车顶聚类，优先确认是否需要 SWB/LWB 派生。
2. 集中核对 **L200** 各代的驾驶室、货斗和底盘车分支，避免仅按发动机版本建组。
3. 闭合 **L400、Lancer Celeste、Lancer IV–VI、Lancer V Station Wagon**。
4. 最后处理本批末行 `Outlander III 56332`，并执行引用闭合检查。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/1997675/mitsubishi_lancer_gsr_evolution_x_5-speed.html?utm_source=chatgpt.com "2008 Mitsubishi Lancer GSR Evolution X 5-speed (man. 5)"
[2]: https://www.automobile-catalog.com/car/2005/2010515/mitsubishi_outlander_2_0_invite_4wd.html?utm_source=chatgpt.com "2005 Mitsubishi Outlander 2.0 Invite 4WD (man. 5)"
[3]: https://www.automobile-catalog.com/car/2007/2011595/mitsubishi_outlander_2_0_di-d_4wd_inform_invite.html?utm_source=chatgpt.com "2007 Mitsubishi Outlander 2.0 DI-D 4WD Inform (Invite) (man. 6)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 **13 个输入 Ktype、15 条映射、10 个尺寸组**。
* L400 2.4 Bus 按 2WD 与 4WD 分组：两者均为 `4655 × 1695 mm`，但高度分别为 `1855 mm` 与 `1965 mm`。([汽车目录][1])
* Celeste 2.0 GSR 在 1978 年中发生高度变化，改款前为 `1330 mm`、改款后为 `1335 mm`；跨越该节点的 Ktype 已拆为 `prefl/facelift`。([汽车目录][2])
* Lancer IV Hatchback 后期 GTI 高度由前期 `1405 mm` 变为 `1410 mm`，单独建立后期尺寸组。([汽车目录][3])
* Lancer V 4WD Wagon 使用其明确的 `1515 mm` 高度，未误复用 2WD Wagon 的 `1470 mm` 组。([汽车目录][4])
* Lancer VI 普通三厢目前存在不同市场 `4290/4295 mm`、`1395/1405 mm` 的规格差异，本轮未建立猜测性映射；Evolution V 已独立闭合。([汽车数据网][5])
* Outlander III 的 Ktype `56332` 跨越改款前 `4655 × 1800 × 1680 mm` 与后期 `4695 × 1810 × 1710 mm` 外廓，本轮继续保留待拆分状态。([汽车目录][6])

## 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**56**
* READY 映射：**59**
* PENDING 输入 Ktype：**44**
* 已确认尺寸组：**25**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
54969	54969	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-01	HIGH		READY
54970	54970	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-4WD-01	HIGH		READY
3322	3322	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH		READY
3323_prefl	3323	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	MEDIUM	同一 Ktype 覆盖1978年中改款前外廓。	READY
3323_facelift	3323	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	MEDIUM	同一 Ktype 覆盖1978年中改款后外廓。	READY
3324_prefl	3324	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	HIGH	同一 Ktype 覆盖1978年中改款前外廓。	READY
3324_facelift	3324	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH	同一 Ktype 覆盖1978年中改款后外廓。	READY
3325	3325	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH	1978年中改款后外廓。	READY
18022	18022	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3314	3314	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-02	HIGH	后期GTI规格高度与前期组不同。	READY
3315	3315	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
125528	125528	Sedan	Lancer Evolution IV	CN9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IV-SEDAN-4D-01	HIGH		READY
16887	16887	Sedan	Lancer V	CB5A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
5092	5092	Wagon	Lancer V Station Wagon		5	EU-MITSUBISHI-LANCER-V-WAGON-5D-4WD-01	HIGH	4WD车身高度与2WD Wagon不同。	READY
14893	14893	Sedan	Lancer Evolution V	CP9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-V-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L400-MPV-5D-2WD-01	4655	1695	1855	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/2020085/mitsubishi_space_gear_2400_glx.html
EU-MITSUBISHI-L400-MPV-5D-4WD-01	4655	1695	1965	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/2020055/mitsubishi_space_gear_2400_glx_4wd.html
EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	4115	1610	1330	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/1906670/mitsubishi_celeste_2000_gsr.html
EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	4115	1610	1335	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/1906685/mitsubishi_celeste_2000_gsr.html
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	4235	1670	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1934000/mitsubishi_lancer_hatchback_1800_gti-16v_cat.html
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-02	4235	1670	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1934225/mitsubishi_lancer_hatchback_1800_gti_16v_cat.html
EU-MITSUBISHI-LANCER-EVOLUTION-IV-SEDAN-4D-01	4330	1690	1415	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-evolution-iv-2.0-280hp-4wd-42185
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1375	Carfolio	https://www.carfolio.com/mitsubishi-lancer-gti-1.8-16v-152625
EU-MITSUBISHI-LANCER-V-WAGON-5D-4WD-01	4275	1690	1515	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/1952600/mitsubishi_lancer_wagon_1600_glxi_16v_4wd.html
EU-MITSUBISHI-LANCER-EVOLUTION-V-SEDAN-4D-01	4350	1770	1415	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-evolution-v-2.0-280hp-4wd-15659
```

## 下一步优先处理

1. 集中闭合 L300 / Delica II、L300 III 的 Bus、Kasten、Pritsche，以及 SWB/LWB、2WD/4WD、普通顶/高顶分支。
2. 按代际、驾驶室与货斗结构批量处理 L200，避免按动力版本重复建组。
3. 处理 L400 2500 TD Bus、2WD/4WD Kasten 的商用车外廓。
4. 最后解决 Lancer VI 普通三厢和 Outlander III 跨改款拆分。

[1]: https://www.automobile-catalog.com/car/1996/2020085/mitsubishi_space_gear_2400_glx.html?utm_source=chatgpt.com "1996 Mitsubishi Space Gear 2400 GLX Specs Review (94 kW / 128 PS / 126 hp) (since September 1996 for Europe )"
[2]: https://www.automobile-catalog.com/car/1977/1906670/mitsubishi_celeste_2000_gsr.html?utm_source=chatgpt.com "1977 Mitsubishi Celeste 2000 GSR Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1977 for Europe )"
[3]: https://www.automobile-catalog.com/car/1990/1934000/mitsubishi_lancer_hatchback_1800_gti-16v_cat.html?utm_source=chatgpt.com "1990 Mitsubishi Lancer Hatchback 1800 GTi-16V catalyst ..."
[4]: https://www.automobile-catalog.com/car/1993/1952600/mitsubishi_lancer_wagon_1600_glxi_16v_4wd.html?utm_source=chatgpt.com "1993 Mitsubishi Lancer Wagon 1600 GLXi 16V 4WD Specs Review (83 kW / 113 PS / 111 hp) (since January 1993 for Europe )"
[5]: https://www.auto-data.net/en/mitsubishi-lancer-vi-1.5-110hp-15661?utm_source=chatgpt.com "Mitsubishi Lancer VI 1.5 (110 Hp) /Sedan 1996"
[6]: https://www.automobile-catalog.com/car/2014/2012405/mitsubishi_outlander_2_0_2wd_cleartec_inform.html?utm_source=chatgpt.com "2014 Mitsubishi Outlander 2.0 2WD ClearTec Inform Specs Review (110 kW / 150 PS / 148 hp) (up to June 2014 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 L300 III / Delica III 的 **11 个 Bus Ktype**，新增 **20 条 READY 映射**。
* 普通 2WD Bus 按前后期外廓拆分：前期 `4275 × 1690 × 1835 mm`，后期因前部外廓变化长度增至 `4285 mm`。([汽车目录][1])
* 4WD Bus 同样按前后期拆分：前期 `4365 × 1690 × 1975 mm`，后期长度增至 `4375 mm`。([汽车目录][2])
* 同一 Ktype 跨越前后期时完整输出 `prefl`、`facelift` 两个派生分支；未保留无后缀基础行。
* Kasten 与 Pritsche/Fahrgestell 可能包含不同轴距或车顶，本轮未猜测性复用 Bus 尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**67**
* READY 映射：**79**
* PENDING 输入 Ktype：**33**
* 已确认尺寸组：**29**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3400_prefl	3400	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3400_facelift	3400	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3405_prefl	3405	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3405_facelift	3405	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3411_prefl	3411	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3411_facelift	3411	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3412	3412	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	HIGH		READY
3402_prefl	3402	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3402_facelift	3402	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3406_prefl	3406	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3406_facelift	3406	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
5980	5980	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	HIGH		READY
3407_prefl	3407	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3407_facelift	3407	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3408_prefl	3408	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3408_facelift	3408	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3409_prefl	3409	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3409_facelift	3409	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3410_prefl	3410	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3410_facelift	3410	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	4275	1690	1835	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/60170/mitsubishi_l-300_bus_2_0_cat.html
EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	4285	1690	1835	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2020130/mitsubishi_l-300_bus_2_0_cat.html
EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	4365	1690	1975	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2020115/mitsubishi_l-300_allrad-bus_2_4_cat.html
EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	4375	1690	1975	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2020190/mitsubishi_l-300_allrad-bus_2_5_diesel_turbo.html
```

## 下一步优先处理

1. 闭合 L300 / Delica II 的 Bus、Kasten 与旧款 Pritsche/Fahrgestell。
2. 核对 L300 III Kasten 的 SWB/LWB、普通顶/高顶分支，以及新款 Pritsche/Fahrgestell。
3. 按代际和驾驶室结构集中处理 L200。
4. 处理 L400 柴油 Bus/Kasten、Lancer VI 普通三厢与 Outlander III 跨改款分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/60170/mitsubishi_l-300_bus_2_0_cat.html?utm_source=chatgpt.com "1987 Mitsubishi L-300 Bus 2.0 catalyst Specs Review (64 kW / 87 PS / 86 hp) (since mid-year 1987 for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/2020115/mitsubishi_l-300_allrad-bus_2_4_cat.html?utm_source=chatgpt.com "1987 Mitsubishi L-300 Allrad-Bus 2.4 catalyst Specs Review (80 kW / 109 PS / 107 hp) (since mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 已闭合 L300 / Delica II 的两个欧洲 4WD Bus Ktype，共用 `4135 × 1695 × 1925 mm` 外廓。([汽车目录][1])
* L400 2500 TD Bus 跨越前后期车长变化，拆分为 1995 年初期 `4595 mm` 组与后期既有 `4655 mm` 组；后期组直接复用，不重复输出。([汽车目录][2])
* Lancer VI 普通 1.5 三厢与 1.8 GSR 涡轮四驱分别闭合，未因同代名称相同而错误共组。([汽车数据网][3])
* Outlander III `56332` 已按 2015 年改款前后拆分，分别对应 `4655 × 1800 × 1680 mm` 与 `4695 × 1810 × 1680 mm`。([汽车目录][4])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**73**
* READY 映射：**87**
* PENDING 输入 Ktype：**27**
* 已确认尺寸组：**35**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3391	3391	MPV	L300 / Delica II	L035P	4	EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	MEDIUM	欧洲4WD Bus外廓。	READY
3395	3395	MPV	L300 / Delica II	L037P	4	EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	MEDIUM	欧洲4WD Bus外廓。	READY
14069_prefl	14069	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-PREFL-01	MEDIUM	1995年初期外廓。	READY
14069_facelift	14069	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-01	MEDIUM	1996年后期外廓。	READY
11307	11307	Sedan	Lancer VI	CK2A	4	EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	HIGH		READY
18664	18664	Sedan	Lancer VI GSR	CM5A	4	EU-MITSUBISHI-LANCER-VI-GSR-SEDAN-4D-01	HIGH	GSR涡轮四驱外廓。	READY
56332_prefl	56332	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	改款前外廓。	READY
56332_facelift	56332	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	2015年改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	4135	1695	1925	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/49040/mitsubishi_l-300_country_4x4.html
EU-MITSUBISHI-L400-MPV-5D-2WD-PREFL-01	4595	1695	1855	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/2019980/mitsubishi_space_gear_2500_td_glx.html
EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	4290	1690	1395	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.5-110hp-15661
EU-MITSUBISHI-LANCER-VI-GSR-SEDAN-4D-01	4250	1690	1405	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.8-gsr-205hp-15662
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	4655	1800	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2012420/mitsubishi_outlander_2_0_2wd_cleartec_invite.html
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	4695	1810	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2231735/mitsubishi_outlander_2_0_2wd_cleartec.html
```

## 5. 下一步优先处理

1. 闭合 L300 / Delica II 的 2WD Bus、Kasten、Pritsche/Fahrgestell 分支。
2. 闭合 L300 III 的 Kasten 与 Pritsche/Fahrgestell，区分轴距和车顶差异。
3. 按代际、驾驶室和货斗结构集中处理剩余 15 个 L200 Ktype。
4. 最后处理 L400 的两个柴油 Kasten Ktype，并完成引用闭合检查。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/49040/mitsubishi_l-300_country_4x4.html?utm_source=chatgpt.com "1983 Mitsubishi L-300 Country 4x4 Specs Review (60 kW / ..."
[2]: https://www.automobile-catalog.com/car/1995/2019980/mitsubishi_space_gear_2500_td_glx.html?utm_source=chatgpt.com "1995 Mitsubishi Space Gear 2500 TD GLX (man. 5)"
[3]: https://www.auto-data.net/en/mitsubishi-lancer-vi-1.5-110hp-15661?utm_source=chatgpt.com "Mitsubishi Lancer VI 1.5 (110 Hp) /Sedan 1996"
[4]: https://www.automobile-catalog.com/car/2014/2012420/mitsubishi_outlander_2_0_2wd_cleartec_invite.html?utm_source=chatgpt.com "2014 Mitsubishi Outlander 2.0 2WD ClearTec Invite (man. 5)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 已闭合 L300 / Delica II 后期 1.6 Bus。`3390` 从 1984 年 11 月开始，对应改款后的 `4035 × 1690 × 1800 mm` 标准顶 2WD 外廓。([CarsGuide][1])
* 已闭合 L300 / Delica II 独立驾驶室 Pritsche/Fahrgestell。1.6 与后续 2.5 D 继续使用同一 L0 系列皮卡车身，统一关联 `4690 × 1650 × 1535 mm` 尺寸组。([CarsGuide][2])
* 已确认 `K62T` 同时覆盖 L200 III 的 Single Cab 与 Double Cab，Ktype `8737` 拆成两个物理外廓分支，不保留基础行。([PartSouq][3])
* L300 II 跨 1984 年改款的 `3389`、`3396`、`3397` 暂未关联，等待将改款前后高度差异与欧洲市场车身边界一次性闭合。

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**77**
* READY 映射：**92**
* PENDING 输入 Ktype：**23**
* 已确认尺寸组：**39**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3390	3390	MPV	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-01	MEDIUM	1984年末改款后的标准顶2WD Bus外廓。	READY
10595	10595	Pickup	L300 / Delica II Pickup		2	EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	MEDIUM	L0系列独立驾驶室皮卡及底盘车外廓。	READY
10597	10597	Pickup	L300 / Delica II Pickup		2	EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	MEDIUM	L0系列后期柴油独立驾驶室皮卡及底盘车外廓。	READY
8737_singlecab	8737	Pickup	L200 III	K62T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	K62T单排驾驶室分支。	READY
8737_doublecab	8737	Pickup	L200 III	K62T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-01	MEDIUM	K62T双排驾驶室分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-01	4035	1690	1800	CarsGuide Mitsubishi Express 1984 dimensions	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1984
EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	4690	1650	1535	CarsGuide Mitsubishi Express 1983 dimensions	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983
EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-2WD-01	5009	1694	1585	Autoevolution Mitsubishi L200 Single Cab specifications	https://www.autoevolution.com/cars/mitsubishi-l200-single-cab-1995.html
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-01	4920	1694	1610	Autoevolution Mitsubishi L200 Double Cab specifications	https://www.autoevolution.com/cars/mitsubishi-l200-double-cab-1995.html
```

## 5. 下一步优先处理

1. 一次性闭合 `3389`、`3396`、`3397` 的 L300 II 改款前后标准顶外廓。
2. 处理 L300 III Kasten 与 Pritsche/Fahrgestell 的标准顶、轴距和 P13T/P15T 分支。
3. 根据 K64T、K74T、K75T 的 Single Cab、Club Cab、Double Cab 边界集中拆分 L200 III。
4. 处理 L200 IV/V、L400 两个 Kasten Ktype，并完成剩余引用闭合。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1984?utm_source=chatgpt.com "Mitsubishi Express Dimensions 1984"
[2]: https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983?utm_source=chatgpt.com "Mitsubishi Express Dimensions 1983 - CarsGuide"
[3]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MR432756&srsltid=AfmBOooZHoifmqPKe96ziroHbOsSf8gmzUOV7dxHm_KEVG6x0p7Y7ZX2&ssd=%24%2AKwF-SltwJHgAOn97J3x2TiYyEhULenV4eWttYiQNMWklb3AmYHdrYG8paXZvCXAlKEV8DHwPbmFoJTchJQd7eB9uYWgreTk9bgcPGQgIBn43ZgAAAADzH0sd%24&utm_source=chatgpt.com "Mitsubishi L200 General (EXPORT) K62T | Parts Catalogs"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 已闭合 L400 柴油 Kasten 的 2WD 与 4WD 两个 Ktype。
* Mitsubishi L400 维修资料明确区分 `PA5V` 标准轴距 2WD Panel Van 与 `PD5V` 标准轴距 4WD Panel Van；对应外廓分别与本批已建立的 L400 2WD、4WD 尺寸组完全一致，因此直接复用，不重复建组。([manualzz.com][1])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**79**
* READY 映射：**94**
* PENDING 输入 Ktype：**21**
* 已确认尺寸组：**39**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14070	14070	Van	L400	PA5V	4	EU-MITSUBISHI-L400-MPV-5D-2WD-01	HIGH	标准轴距2WD Kasten外廓。	READY
18401	18401	Van	L400	PD5V	4	EU-MITSUBISHI-L400-MPV-5D-4WD-01	HIGH	标准轴距4WD Kasten外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 闭合 L300 / Delica II 的 `3389`、`3396`、`3397`，解决改款前后高度口径冲突。
2. 拆分 L300 III Kasten 的标准轴距、长轴及高顶外廓，并处理 `3398`、`3399`。
3. 闭合 L300 III Pritsche/Fahrgestell 的 `10598`、`10599`。
4. 集中处理剩余 L200 Ktype，按 L200 II–V 代际以及 Single Cab、Club Cab、Double Cab、底盘车分支批量关联。

推进信号：CONTINUE

[1]: https://manualzz.com/doc/24296331/mitsubishi-l400-van-or-space-gear-van-or-wagon-user-manual "Mitsubishi L400+ AI Chat & PDF Download | Manualzz"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 已闭合 L300 III Kasten 的短轴标准顶与长轴高顶分支。`3398` 明确覆盖 `P02V/P12V`，`3399` 覆盖 `P05V/P15V`，均按物理外廓拆分，不再保留基础行。([KMotorShop][1])
* 短轴厢式车使用 `4275 × 1690 × 1835 mm`；长轴 `P15V` 的官方型式批准尺寸为 `4675 × 1690 × 1950 mm`。([汽车目录][2])
* 已闭合 L300 III `P13T/P15T` 长轴 Pritsche/Fahrgestell。两种动力共用同一驾驶室、轴距与平台外廓，发动机差异不重复建组。([PartSouq][3])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**83**
* READY 映射：**100**
* PENDING 输入 Ktype：**17**
* 已确认尺寸组：**42**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3398_swb	3398	Van	L300 III / Delica III	P02V	4	EU-MITSUBISHI-L300-III-VAN-SWB-01	MEDIUM	短轴标准顶厢式车分支。	READY
3398_lwb	3398	Van	L300 III / Delica III	P12V	4	EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车分支。	READY
3399_swb	3399	Van	L300 III / Delica III	P05V	4	EU-MITSUBISHI-L300-III-VAN-SWB-01	HIGH	短轴标准顶厢式车分支。	READY
3399_lwb	3399	Van	L300 III / Delica III	P15V	4	EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车分支。	READY
10598	10598	Pickup	L300 III / Delica III	P13T	2	EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	HIGH	长轴独立驾驶室平台车。	READY
10599	10599	Pickup	L300 III / Delica III	P15T	2	EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	HIGH	长轴独立驾驶室平台车。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-III-VAN-SWB-01	4275	1690	1835	Automobile-Catalog Mitsubishi L-300 Bus 2.5 Diesel; Mitsubishi L300 P05V/P15V vehicle catalog	https://www.automobile-catalog.com/car/1987/2020160/mitsubishi_l-300_bus_2_5_diesel.html;https://www.autodoc.parts/spares/mitsubishi/l-300/l-300-box-p0-w-p1-w/3399-2-5-d-p05v-p05w-p15v
EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	4675	1690	1950	Swiss Federal Roads Office type approval 3M7516; K MOTORSHOP L300 III vehicle listing	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3M7516_F.pdf;https://www.kmotorshop.com/en/device/car-list/1813
EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	4720	1720	1840	Swiss type approval 3M7535; Mitsubishi Parts Catalog L300 Truck P13T	https://www.dauto.ch/typenscheine/mitsubishi-l300-2-5-td-3m7535-jmbyzp150sa-x;https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&ssd=%24%2AKwEpHQxhYywwVl1weXgKFXFlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFEvKyowSxAZE1Bka3lzWmY9IW5qOzhfKisoXChyfBE5Nj0-djgnP2AcYShOPzA7OH5zYHZwOUNHUC04YAAAAAASwkvW%24&vid=0
```

## 5. 下一步优先处理

1. 闭合 L300 / Delica II 的 `3389`、`3396`、`3397`，按 1983、1984 与后期车头改款边界拆分。
2. 集中处理剩余 **14 个 L200 Ktype**，优先完成 L200 III 的 Single Cab、Club Cab、Double Cab 和底盘车分支。
3. 再处理 L200 IV 与 L200 V，并执行映射引用闭合检查。

推进信号：CONTINUE

[1]: https://www.kmotorshop.com/en/device/car-list/1813?utm_source=chatgpt.com "Cars MITSUBISHI L 300 III Van (P0_V, P1_V, P2_V) | K MOTORSHOP s.r.o."
[2]: https://www.automobile-catalog.com/car/1987/2020160/mitsubishi_l-300_bus_2_5_diesel.html?utm_source=chatgpt.com "1987 Mitsubishi L-300 Bus 2.5 Diesel Specs Review ..."
[3]: https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&ssd=%24%2AKwEpHQxhYywwVl1weXgKFXFlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFEvKyowSxAZE1Bka3lzWmY9IW5qOzhfKisoXChyfBE5Nj0-djgnP2AcYShOPzA7OH5zYHZwOUNHUC04YAAAAAASwkvW%24&vid=0&utm_source=chatgpt.com "Engine | Mitsubishi L300-TRUCK Europe (EUROPE) P13T Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 已闭合 `Ktype=3396`。该 Ktype 对应 L300 / Delica II 2.3 D Bus、车身代码 `L038P`。([www.valeoservice.com][1])
* 按 1984 年前后车头外廓拆分：1983 年标准车身为 `3990 × 1690 × 1800 mm`，1984 年后长度增至 `4035 mm`；改款后尺寸组直接复用，不重复输出。([CarsGuide][2])
* `3389`、`3397` 仍保留待处理：现有资料显示 1981 年车高为 `1815 mm`、1983 年为 `1800 mm`，需要先确定变化边界，未做猜测性合并。([CarsGuide][3])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**84**
* READY 映射：**102**
* PENDING 输入 Ktype：**16**
* 已确认尺寸组：**43**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3396_prefl	3396	MPV	L300 / Delica II	L038P	4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	MEDIUM	L038P短轴Bus，1984年改款前外廓。	READY
3396_facelift	3396	MPV	L300 / Delica II	L038P	4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-01	MEDIUM	L038P短轴Bus，1984年改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	3990	1690	1800	CarsGuide Mitsubishi Express 1983 dimensions; Valeo TechAssist Mitsubishi L300 2.3 D L038P vehicle application	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983;https://www.valeoservice.com/techassist/vehicle/P-3396?country=MA
```

## 5. 下一步优先处理

1. 确定 `3389`、`3397` 的早期 `1815 mm` 与后期 `1800 mm` 车高边界，闭合最后两个 L300 II Ktype。
2. 处理 L200 III 的 K62T、K64T、K74T、K75T，区分 Single Cab、Club Cab 与 Double Cab。
3. 处理 L200 IV 的 KA4T、KB4T Pickup 与 Platform/Chassis 分支。
4. 最后闭合 L200 V 的 KJ0T、KL1T 驾驶室分支，并执行完整引用检查。

推进信号：CONTINUE

[1]: https://www.valeoservice.com/techassist/vehicle/P-3396?country=MA&utm_source=chatgpt.com "Parts MITSUBISHI L 300 / DELICA II Bus (L03_P/G, L0_2P)"
[2]: https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983 "Mitsubishi Express Dimensions 1983 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[3]: https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1981 "Mitsubishi Express Dimensions 1981 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 修正 `8737`：`K62T` 在 Mitsubishi EPC 中明确为 2WD Double Cab，上一轮错误拆出的 `8737_singlecab`、`8737_doublecab` 由单行 `8737` 取代。由于新核对三维与旧尺寸组不同，未覆盖旧组，创建序号 `-02` 的新组。([PartSouq][1])
* 闭合 `17459`、`17755`。两者均对应 2001–2007 年后期 `K74T`；该代码覆盖 Single Cab、Club Cab、Double Cab，以及部分 Club/Double Cab 宽体分支，因此分别完整派生五种物理外廓。([Meyer Motoren][2])
* 后期 K74T 的五套三维已由 Mitsubishi L200 维修手册集中闭合：普通单排、普通/宽体 Club Cab、普通/宽体 Double Cab。([ManualsLib][3])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**86**
* READY 映射：**111**
* PENDING 输入 Ktype：**14**
* 当前有效尺寸组：**47**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8737	8737	Pickup	L200 III	K62T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	HIGH	K62T为2WD双排驾驶室；修正上一轮误拆分。	READY
17459_singlecab	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期单排驾驶室分支。	READY
17459_clubcab	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度Club Cab分支。	READY
17459_clubcab_wide	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱Club Cab分支。	READY
17459_doublecab	17459	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度双排驾驶室分支。	READY
17459_doublecab_wide	17459	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱双排驾驶室分支。	READY
17755_singlecab	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期单排驾驶室分支。	READY
17755_clubcab	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度Club Cab分支。	READY
17755_clubcab_wide	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱Club Cab分支。	READY
17755_doublecab	17755	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度双排驾驶室分支。	READY
17755_doublecab_wide	17755	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱双排驾驶室分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	4935	1695	1610	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=30
EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	5010	1695	1750	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	5125	1695	1775	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	5125	1775	1800	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	5010	1695	1780	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=95
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	5010	1775	1800	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=96
```

## 5. 下一步优先处理

1. 闭合 `3389`、`3397` 的 L300 II 早期 `1815 mm` 与后期 `1800 mm` 高度边界。
2. 使用已闭合的 L200 III 驾驶室规则处理 `8738`、`8739`、`8740`，并补齐跨改款前后分支。
3. 处理旧代 `59324`。
4. 最后批量闭合 L200 IV/V 的 `10981`、`125748`、`126659`、`116196`、`57471`、`117261`、`111099`、`116161`。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=MMC202501&number=MR491790&ssd=%24%2AKwEuGgsRJElRelJYa3FyGnZiQkVbKiUoKTsUJ29pWlRZUGRHNTghXFBILyUsLSF1NSF5dVpgPnQ4Iis-O3AxOHg-JzhbfXtkXi1bLVg_NjooaW0-ViwpSD82OiYndSY_UF5STl9UEmkqAAAAALreGow%3D%24&vid=0&utm_source=chatgpt.com "Power Train | Mitsubishi L200 General (EXPORT) K62T | Parts Catalogs | PartSouq"
[2]: https://www.meyermotoren.de/en/fahrzeuge/17755/mitsubishi/l200_iii_k7_k6_k5_/2_5_td_4wd_k74t_17755?utm_source=chatgpt.com "2.5 TD 4WD (K74T) | L200 III (K7, K6, K5) | MITSUBISHI | Manufacturers | Meyer Motoren"
[3]: https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94 "Mitsubishi MOTORS L200 1996 Workshop Manual (Page 94 of 1723) | ManualsLib"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 修正 L300 / Delica II 改款后 2WD Bus 的高度口径：1984 年规格为 `4035 × 1690 × 1815 mm`，不再沿用此前的 `1800 mm` 高度。按照冲突处理规则，未覆盖旧组，而是建立序号 `-02` 新组，并同步更新 `3390`、`3396_facelift` 的引用；旧组退出当前批次有效快照。([CarsGuide][1])
* 闭合 `Ktype=8739`。其 `K64T` 为 L200 III 2WD Double Cab，直接复用已经确认的双排驾驶室尺寸组，不重复建立或抓取尺寸。([PartSouq][2])
* `3389`、`3397` 涉及 `L032P/L062P` 等不同车身代码及早期高度变化，本轮未进行猜测性合并。([Meyer Motoren][3])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**87**
* READY 映射：**112**
* PENDING 输入 Ktype：**13**
* 当前有效尺寸组：**47**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3390	3390	MPV	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	1984年末改款后的标准顶2WD Bus外廓；修正高度口径。	READY
3396_facelift	3396	MPV	L300 / Delica II	L038P	4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	L038P短轴Bus，1984年改款后外廓；修正高度口径。	READY
8739	8739	Pickup	L200 III	K64T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	4035	1690	1815	CarsGuide Mitsubishi Express 1984 dimensions	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1984
```

## 5. 下一步优先处理

1. 拆分 `3389`、`3397` 的 `L032P/L062P` 车身及早期、改款后外廓。
2. 闭合 `8738`、`8740` 的 Single Cab、Club Cab、Double Cab、宽体及前后期分支。
3. 处理 L200 IV 的 `10981`、`125748`、`126659`、`116196`、`57471`、`117261`。
4. 处理旧代 `59324` 及 L200 V 的 `111099`、`116161`，随后执行完整引用闭合检查。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1984?utm_source=chatgpt.com "Mitsubishi Express Dimensions 1984 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[2]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD342664&srsltid=AfmBOoo3LBlZpsguudVgKVlMF6pkpMJyaKpzoMrhwgfDonovXPpVBTzf&ssd=%24%2AKwE9CRgOOFRlWmQ9PkoGbGVxUVZIOTY7OiguIWdOcipmLDNlIzQoIyxqKjUsSjNmawY_Tz9MLSIrZnRiZkQ4PVwtIitoOnp-LURMRlxCXikrAAAAAK2CZSQ%24&utm_source=chatgpt.com "Mitsubishi L200 General (EXPORT) K64T | Parts Catalogs"
[3]: https://www.meyermotoren.de/en/fahrzeuge/3389/mitsubishi/l300_delica_ii_bus_l03p_g_l02p_/1_6_l032p_l062p_3389?utm_source=chatgpt.com "1.6 (L032P, L062P) | L300/Delica II Bus (L03P/G, L02P) | MITSUBISHI | Manufacturers | Meyer Motoren"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 1. 更新点

* 已闭合 `8738`、`8740`。`K75T` 与 `K74T` 均覆盖单排、Club Cab、双排及宽体分支，且这些分支与已确认的 L200 III 尺寸组完全一致，因此本轮仅新增映射，不重复建立尺寸组。([PartSouq][1])
* 已闭合 `116196`。Mitsubishi EPC 显示 `KB4T` 包含 Single Cab、Club Cab、Double Cab 和宽体 Double Cab；官方 L200 尺寸图分别确认四套外廓。([PartSouq][2])
* 发动机和功率差异未单独建立尺寸组。

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**90**
* READY 映射：**126**
* PENDING 输入 Ktype：**10**
* 当前有效尺寸组：**51**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8738_singlecab	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K75T单排驾驶室分支。	READY
8738_clubcab	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K75T普通宽度Club Cab分支。	READY
8738_clubcab_wide	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K75T宽体Club Cab分支。	READY
8738_doublecab	8738	Pickup	L200 III	K75T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K75T普通宽度双排驾驶室分支。	READY
8738_doublecab_wide	8738	Pickup	L200 III	K75T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K75T宽体双排驾驶室分支。	READY
8740_singlecab	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T单排驾驶室分支。	READY
8740_clubcab	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T普通宽度Club Cab分支。	READY
8740_clubcab_wide	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T宽体Club Cab分支。	READY
8740_doublecab	8740	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T普通宽度双排驾驶室分支。	READY
8740_doublecab_wide	8740	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T宽体双排驾驶室分支。	READY
116196_singlecab	116196	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	HIGH	KB4T单排驾驶室分支。	READY
116196_clubcab	116196	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-CLUB-CAB-4WD-01	HIGH	KB4T Club Cab分支。	READY
116196_doublecab_longbed	116196	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-LONGBED-4WD-01	HIGH	KB4T普通宽度长货斗双排分支。	READY
116196_doublecab_wide	116196	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH	KB4T宽体短货斗双排分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	5040	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-CLUB-CAB-4WD-01	5120	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-LONGBED-4WD-01	5185	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-WIDE-4WD-01	5005	1815	1780	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
```

## 5. 下一步优先处理

1. 闭合 L300 II 的 `3389`、`3397`，确认 `L032P/L062P` 与 Bus/Kasten 的早期高度边界。
2. 处理 L200 II 的 `59324`。
3. 闭合 L200 IV 2WD 的 `10981`、`125748`，以及底盘车 `126659`、`57471`。
4. 最后处理 L200 IV/V 交界的 `117261` 与 L200 V 的 `111099`、`116161`。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=MMC202403&number=MR125917&ssd=%24%2AKwFsWEl8CxcRMRwKPyJkPTQgAAcZaGdqa3lWZS0rGBYbEiYFd3pjHhIKaGxqYWswd2M7NxgifDZ6YGl8eTJzejp8ZXoZPzkmHG8Zbxp9dHhqKy98FG9sCn10eGRlN2R9HRcaGhR4egAAAAAQ3MG9%24&vid=0&utm_source=chatgpt.com "Body | Mitsubishi L200 General (EXPORT) K75T | Parts Catalogs | PartSouq"
[2]: https://partsouq.com/en/catalog/genuine/unit?c=Mitsubishi&cid=3&q=&ssd=%24%2AKwEwBBUAT0o1ZERxXnEiGGh8XFtFNDs2NyU2CXkhcCc4IV4kd3cqIDk3eHx2RH15IWs4IV4nLiFnaHlva0E7NDZOMzQzH3dlIGBtJzgwKCQud3MgNzYoNjI0JHd3ICA5JjQ2MSs3b2cWNjI0QTIzNDVoAWt_fXJgakN_JDJ3c2x2aGkuIWckYXcKOjM3STIzMUJ5eWtvIT4nSUEwUnl5a2FvJj8gTUFIDg8ZUDsmeAAAAADwF7Lq%24&uid=142021&vid=0&utm_source=chatgpt.com "BODY - REAR END STRUCTURE | Mitsubishi L200,L200 SPORTERO General (EXPORT) KB4T | Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 1. 更新点

* 已闭合 L200 V 的 `111099`、`116161`、`117261`。
* `116161 / KJ0T` 同时覆盖 Club Cab 与 Double Cab，已拆成两个物理分支；两种驾驶室分别使用 `5195 × 1785 × 1775 mm` 和 `5205 × 1785 × 1775 mm` 外廓。
* `111099 / KL1T` 与 `117261 / KL3T` 均关联 L200 V 宽体 4WD Double Cab。发动机不同未重复建组，共用 `5205 × 1815 × 1780 mm` 尺寸组；KL3T 维修资料同时确认基础车长 `5200 mm`、牌照饰件状态 `5205 mm`。([AUTODOC France][1])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**93**
* READY 映射：**130**
* PENDING 输入 Ktype：**7**
* 当前有效尺寸组：**54**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
111099	111099	Pickup	L200 V	KL1T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH		READY
116161_clubcab	116161	Pickup	L200 V	KJ0T	2	EU-MITSUBISHI-L200-V-PICKUP-CLUB-CAB-4WD-01	MEDIUM	KJ0T Club Cab物理分支。	READY
116161_doublecab	116161	Pickup	L200 V	KJ0T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-4WD-01	MEDIUM	KJ0T Double Cab物理分支。	READY
117261	117261	Pickup	L200 V	KL3T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH	KL3T宽体双排驾驶室。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-V-PICKUP-CLUB-CAB-4WD-01	5195	1785	1775	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors Deutschland L200 KJ0T Club Cab rescue sheet	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://rettungskarten-service.de/wp-content/uploads/L200-Club-Cab-Typ-KJ0T-ab-Modelljahr-2016.pdf
EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-4WD-01	5205	1785	1775	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors España L200 KJ0T Double Cab rescue sheet	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://www.mitsubishi-motors.es/content/dam/mitsubishi-motors-es/es/rescate/Hoja_de_rescate_L200_KJ0T_Doble_cabina.pdf
EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	5205	1815	1780	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors L200 service bulletin MSB-19X00_31_51-001	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://mmc-manuals.ru/MSBv2/SATSU/MSB-19X00_31_51-001.pdf
```

## 5. 下一步优先处理

1. 闭合 L300 II 的 `3389`、`3397`，确定 `L032P/L062P`、Bus/Kasten 与早期高度边界。
2. 处理 L200 II 的 `59324`。
3. 闭合 L200 IV 2WD Pickup 的 `10981`、`125748`。
4. 闭合 L200 IV 底盘车 `126659`、`57471`，完成剩余引用检查。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/timing-chain-10511/mitsubishi/l-200/l200-kj/111099-2-4-di-d-4wd-kl1t?utm_source=chatgpt.com "Timing chain Mitsubishi L200 KJ 2.4 DI-D 4WD 181 hp Diesel ..."


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1. 更新点

* 已闭合 `Ktype=59324`。`K32T` 同时存在单排长货斗与双排车身，已拆成两个物理分支；1987 年对应外廓分别为单排 `5095 × 1655 × 1690 mm`、双排 `4920 × 1655 × 1740 mm`。([MitzyBitz][1])
* 剩余 L200 IV 不做猜测性合并：目录已明确 `10981` 为 KA4T 高功率双排，而 `126659` 的底盘车适配信息涉及 Single Cab、Club Cab 与 Double Cab，需要分别闭合对应外廓。([PartSouq][2])

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**94**
* READY 映射：**132**
* PENDING 输入 Ktype：**6**
* 当前有效尺寸组：**56**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59324_singlecab	59324	Pickup	L200 II	K32T	2	EU-MITSUBISHI-L200-II-PICKUP-SINGLE-CAB-4WD-01	MEDIUM	K32T单排长货斗分支。	READY
59324_doublecab	59324	Pickup	L200 II	K32T	4	EU-MITSUBISHI-L200-II-PICKUP-DOUBLE-CAB-4WD-01	MEDIUM	K32T双排驾驶室分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-II-PICKUP-SINGLE-CAB-4WD-01	5095	1655	1690	Mitsubishi General Export K32T parts catalog; CarsGuide Mitsubishi Triton 1987 dimensions	https://www.mitzybitz.com/mitsubishi-l200/l200/general-export-5/k0-k3-0/k32t-20004wdlong-truck-standard-cablong5fmt-rhd-1986-01-01-2001-03-31;https://www.carsguide.com.au/mitsubishi/triton/1987
EU-MITSUBISHI-L200-II-PICKUP-DOUBLE-CAB-4WD-01	4920	1655	1740	Car.info Mitsubishi L200 Double Cab 2nd Generation; CarsGuide Mitsubishi Triton 1987 dimensions	https://www.car.info/en-se/mitsubishi/l200/l200-double-cab-70588;https://www.carsguide.com.au/mitsubishi/triton/1987
```

## 5. 下一步优先处理

1. 闭合 `10981`、`125748` 的 L200 IV 2WD 高车身双排及前后期外廓。
2. 拆分 `126659`、`57471` 的 2WD/4WD 底盘车驾驶室分支。
3. 最后解决 `3389`、`3397` 的 `L032P/L062P` Bus/Kasten 与早期车高边界。

推进信号：CONTINUE

[1]: https://www.mitzybitz.com/mitsubishi-l200/l200/general-export-5/k0-k3-0/k32t-20004wdlong-truck-standard-cablong5fmt-rhd-1986-01-01-2001-03-31?utm_source=chatgpt.com "MITSUBISHI L200 / L200 General (EXPORT) K0-K3# K32T"
[2]: https://partsouq.com/en/catalog/genuine/unit?c=Mitsubishi&cid=1&q=&ssd=%24%2AKwFeant-AgYeDD0XAiBkcgYSMjUrWlVYWUtYZxdPHklWTzBKGRlETldbFhIYKhMXTwVWTzBJQE8JBhcBBS9VWlggXVpdcRkLTg4DSVZcRkpAGR1OXF5GXFxaShkZTk5XSFpdWUVZBA94XFxaL1xdX14CbwURExwOBC0RSlwZHQIYBgdATwlKDxlkVF1ZJ1xdXywXFwUBT1BJJyxePBcXBQ8BSFFOJSA6YGF3IE8XAAAAAHn6z1o%3D%24&uid=145528&vid=0&utm_source=chatgpt.com "COOLING - RADIATOR,HOSE & CONDENSER TANK | Mitsubishi L200,L200 SPORTERO General (EXPORT) KA4T | Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 1. 更新点

* 已闭合 L200 IV 的 4 个剩余 Ktype。
* `10981` 跨越 2010 年前后两种 2WD Double Cab 外廓，拆分为改款前 `4995 × 1750 × 1650 mm` 与改款后 `5185 × 1750 × 1645 mm`；`125748` 直接复用后期组。([Scribd][1])
* `126659` 已关联 2WD Single Cab 底盘车外廓 `5040 × 1750 × 1655 mm`；`57471` 复用已确认的 4WD Single Cab 组，不重复输出尺寸组。([encyCARpedia][2])
* 当前仅剩 L300 / Delica II 的 `3389`、`3397` 未闭合。

## 2. 当前批次进度

* 输入 Ktype：**100**
* 已闭合输入 Ktype：**98**
* READY 映射：**137**
* PENDING 输入 Ktype：**2**
* 当前有效尺寸组：**59**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10981_prefl	10981	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-PREFL-01	MEDIUM	同一Ktype覆盖2010年前2WD双排外廓。	READY
10981_facelift	10981	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖2010年后2WD双排外廓。	READY
125748	125748	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	MEDIUM		READY
126659	126659	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	2WD单排底盘车分支。	READY
57471	57471	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	MEDIUM	4WD单排底盘车分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-PREFL-01	4995	1750	1650	Mitsubishi Triton KA4/KB4 Factory Service Manual	https://www.scribd.com/doc/159429016/117-Mitsubishi-Triton-KA4-KB4-KB8-Factory-Service-Manual
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	5185	1750	1645	EncyCARpedia Mitsubishi L200 2.5 DI-D 2WD Double Cab specifications	https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-double-cab-128-pick-up
EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-2WD-01	5040	1750	1655	EncyCARpedia Mitsubishi L200 2.5 DI-D 2WD Single Cab specifications	https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-single-cab-128-pick-up
```

## 5. 下一步优先处理

1. 一次性确认 `3389`、`3397` 所覆盖的 `L032P/L062P` Bus、Kasten 分支及 1981–1984 年车高变化边界。
2. 两个 Ktype 闭合后立即执行一次机械收尾，并在下一轮输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.scribd.com/doc/159429016/117-Mitsubishi-Triton-KA4-KB4-KB8-Factory-Service-Manual "Mitsubishi Triton Workshop Manual | PDF | Airbag | Electrical Connector"
[2]: https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-single-cab-128-pick-up?utm_source=chatgpt.com "2010 Mitsubishi L200 2.5 DI-D 2WD Single Cab 128 ..."


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11301-11400_ktype_dimension_mapping_final.tsv
- left18448_11301-11400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 已闭合最后两个 Ktype：`3389` 与 `3397` 均覆盖 L300/Delica II 1.6 的 `L032P/L062P` 范围，按照 1984 年前后车身长度变化拆分为 `prefl` 与 `facelift` 分支。1983 年规格为 `3990 × 1690 × 1800 mm`，1984 年后外廓为 `4035 × 1690 × 1815 mm`。([AUTODOC][1])
* 已完成机械检查：表头固定、141 个 `id` 唯一、59 个尺寸组唯一、全部映射引用闭合、无孤立尺寸组、三维及来源均非空。
* 当前批次达到 `PENDING=0`，直接输出最终完整快照。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**141**
* PENDING 映射：**0**
* DIMENSION_GROUP：**59**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
162806	162806	SUV	Grandis (2025)		5	EU-MITSUBISHI-GRANDIS-2025-SUV-5D-01	HIGH	2025 年重新启用名称的 5 门 SUV。	READY
18778	18778	MPV	Grandis I	NA8W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
18023	18023	MPV	Grandis I	NA4W	5	EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	HIGH		READY
3389_prefl	3389	MPV	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	MEDIUM	1984年改款前标准顶2WD Bus外廓。	READY
3389_facelift	3389	MPV	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	1984年改款后标准顶2WD Bus外廓。	READY
3390	3390	MPV	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	1984年末改款后的标准顶2WD Bus外廓；修正高度口径。	READY
3397_prefl	3397	Van	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	MEDIUM	1984年改款前标准顶Kasten外廓。	READY
3397_facelift	3397	Van	L300 / Delica II		4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	1984年改款后标准顶Kasten外廓。	READY
10595	10595	Pickup	L300 / Delica II Pickup		2	EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	MEDIUM	L0系列独立驾驶室皮卡及底盘车外廓。	READY
3391	3391	MPV	L300 / Delica II	L035P	4	EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	MEDIUM	欧洲4WD Bus外廓。	READY
3395	3395	MPV	L300 / Delica II	L037P	4	EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	MEDIUM	欧洲4WD Bus外廓。	READY
3396_prefl	3396	MPV	L300 / Delica II	L038P	4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	MEDIUM	L038P短轴Bus，1984年改款前外廓。	READY
3396_facelift	3396	MPV	L300 / Delica II	L038P	4	EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	MEDIUM	L038P短轴Bus，1984年改款后外廓；修正高度口径。	READY
10597	10597	Pickup	L300 / Delica II Pickup		2	EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	MEDIUM	L0系列后期柴油独立驾驶室皮卡及底盘车外廓。	READY
3398_swb	3398	Van	L300 III / Delica III	P02V	4	EU-MITSUBISHI-L300-III-VAN-SWB-01	MEDIUM	短轴标准顶厢式车分支。	READY
3398_lwb	3398	Van	L300 III / Delica III	P12V	4	EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车分支。	READY
3400_prefl	3400	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3400_facelift	3400	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3405_prefl	3405	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3405_facelift	3405	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
3411_prefl	3411	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3411_facelift	3411	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
10598	10598	Pickup	L300 III / Delica III	P13T	2	EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	HIGH	长轴独立驾驶室平台车。	READY
3412	3412	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	HIGH		READY
3402_prefl	3402	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3402_facelift	3402	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3406_prefl	3406	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3406_facelift	3406	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
5980	5980	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	HIGH		READY
3407_prefl	3407	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3407_facelift	3407	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3408_prefl	3408	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3408_facelift	3408	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
3399_swb	3399	Van	L300 III / Delica III	P05V	4	EU-MITSUBISHI-L300-III-VAN-SWB-01	HIGH	短轴标准顶厢式车分支。	READY
3399_lwb	3399	Van	L300 III / Delica III	P15V	4	EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车分支。	READY
3409_prefl	3409	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	MEDIUM	同一Ktype覆盖前期2WD Bus外廓。	READY
3409_facelift	3409	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期2WD Bus外廓。	READY
10599	10599	Pickup	L300 III / Delica III	P15T	2	EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	HIGH	长轴独立驾驶室平台车。	READY
3410_prefl	3410	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	MEDIUM	同一Ktype覆盖前期4WD Bus外廓。	READY
3410_facelift	3410	MPV	L300 III / Delica III		5	EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	MEDIUM	同一Ktype覆盖后期4WD Bus外廓。	READY
8737	8737	Pickup	L200 III	K62T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	HIGH	K62T为2WD双排驾驶室；修正上一轮误拆分。	READY
59324_singlecab	59324	Pickup	L200 II	K32T	2	EU-MITSUBISHI-L200-II-PICKUP-SINGLE-CAB-4WD-01	MEDIUM	K32T单排长货斗分支。	READY
59324_doublecab	59324	Pickup	L200 II	K32T	4	EU-MITSUBISHI-L200-II-PICKUP-DOUBLE-CAB-4WD-01	MEDIUM	K32T双排驾驶室分支。	READY
8738_singlecab	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K75T单排驾驶室分支。	READY
8738_clubcab	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K75T普通宽度Club Cab分支。	READY
8738_clubcab_wide	8738	Pickup	L200 III	K75T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K75T宽体Club Cab分支。	READY
8738_doublecab	8738	Pickup	L200 III	K75T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K75T普通宽度双排驾驶室分支。	READY
8738_doublecab_wide	8738	Pickup	L200 III	K75T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K75T宽体双排驾驶室分支。	READY
111099	111099	Pickup	L200 V	KL1T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH		READY
116161_clubcab	116161	Pickup	L200 V	KJ0T	2	EU-MITSUBISHI-L200-V-PICKUP-CLUB-CAB-4WD-01	MEDIUM	KJ0T Club Cab物理分支。	READY
116161_doublecab	116161	Pickup	L200 V	KJ0T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-4WD-01	MEDIUM	KJ0T Double Cab物理分支。	READY
8739	8739	Pickup	L200 III	K64T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	HIGH		READY
10981_prefl	10981	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-PREFL-01	MEDIUM	同一Ktype覆盖2010年前2WD双排外廓。	READY
10981_facelift	10981	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	MEDIUM	同一Ktype覆盖2010年后2WD双排外廓。	READY
125748	125748	Pickup	L200 IV	KA4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	MEDIUM		READY
126659	126659	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-2WD-01	MEDIUM	2WD单排底盘车分支。	READY
116196_singlecab	116196	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	HIGH	KB4T单排驾驶室分支。	READY
116196_clubcab	116196	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-CLUB-CAB-4WD-01	HIGH	KB4T Club Cab分支。	READY
116196_doublecab_longbed	116196	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-LONGBED-4WD-01	HIGH	KB4T普通宽度长货斗双排分支。	READY
116196_doublecab_wide	116196	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH	KB4T宽体短货斗双排分支。	READY
57471	57471	Pickup	L200 IV	KB4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	MEDIUM	4WD单排底盘车分支。	READY
117261	117261	Pickup	L200 V	KL3T	4	EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	HIGH	KL3T宽体双排驾驶室。	READY
8740_singlecab	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T单排驾驶室分支。	READY
8740_clubcab	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T普通宽度Club Cab分支。	READY
8740_clubcab_wide	8740	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T宽体Club Cab分支。	READY
8740_doublecab	8740	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T普通宽度双排驾驶室分支。	READY
8740_doublecab_wide	8740	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T宽体双排驾驶室分支。	READY
17459_singlecab	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期单排驾驶室分支。	READY
17459_clubcab	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度Club Cab分支。	READY
17459_clubcab_wide	17459	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱Club Cab分支。	READY
17459_doublecab	17459	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度双排驾驶室分支。	READY
17459_doublecab_wide	17459	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱双排驾驶室分支。	READY
17755_singlecab	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期单排驾驶室分支。	READY
17755_clubcab	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度Club Cab分支。	READY
17755_clubcab_wide	17755	Pickup	L200 III	K74T	2	EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱Club Cab分支。	READY
17755_doublecab	17755	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	MEDIUM	K74T后期普通宽度双排驾驶室分支。	READY
17755_doublecab_wide	17755	Pickup	L200 III	K74T	4	EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	MEDIUM	K74T后期宽体轮拱双排驾驶室分支。	READY
54969	54969	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-01	HIGH		READY
54970	54970	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-4WD-01	HIGH		READY
14069_prefl	14069	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-PREFL-01	MEDIUM	1995年初期外廓。	READY
14069_facelift	14069	MPV	L400 / Space Gear		5	EU-MITSUBISHI-L400-MPV-5D-2WD-01	MEDIUM	1996年后期外廓。	READY
14070	14070	Van	L400	PA5V	4	EU-MITSUBISHI-L400-MPV-5D-2WD-01	HIGH	标准轴距2WD Kasten外廓。	READY
18401	18401	Van	L400	PD5V	4	EU-MITSUBISHI-L400-MPV-5D-4WD-01	HIGH	标准轴距4WD Kasten外廓。	READY
3322	3322	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH		READY
3323_prefl	3323	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	MEDIUM	同一 Ktype 覆盖1978年中改款前外廓。	READY
3323_facelift	3323	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	MEDIUM	同一 Ktype 覆盖1978年中改款后外廓。	READY
3324_prefl	3324	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	HIGH	同一 Ktype 覆盖1978年中改款前外廓。	READY
3324_facelift	3324	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH	同一 Ktype 覆盖1978年中改款后外廓。	READY
3325	3325	Coupe	Lancer Celeste		3	EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	HIGH	1978年中改款后外廓。	READY
18022	18022	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3314	3314	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-02	HIGH	后期GTI规格高度与前期组不同。	READY
3315	3315	Hatchback	Lancer IV		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
125528	125528	Sedan	Lancer Evolution IV	CN9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IV-SEDAN-4D-01	HIGH		READY
16887	16887	Sedan	Lancer V	CB5A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
5092	5092	Wagon	Lancer V Station Wagon		5	EU-MITSUBISHI-LANCER-V-WAGON-5D-4WD-01	HIGH	4WD车身高度与2WD Wagon不同。	READY
11307	11307	Sedan	Lancer VI	CK2A	4	EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	HIGH		READY
18664	18664	Sedan	Lancer VI GSR	CM5A	4	EU-MITSUBISHI-LANCER-VI-GSR-SEDAN-4D-01	HIGH	GSR涡轮四驱外廓。	READY
14893	14893	Sedan	Lancer Evolution V	CP9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-V-SEDAN-4D-01	HIGH		READY
17750	17750	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
17751	17751	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
17752	17752	Wagon	Lancer VII		5	EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	HIGH		READY
17753	17753	Wagon	Lancer VII		5	EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	HIGH		READY
18212	18212	Sedan	Lancer VII		4	EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	HIGH		READY
125608	125608	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	HIGH		READY
125584	125584	Sedan	Lancer Evolution VII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VII-SEDAN-4D-01	HIGH		READY
125592	125592	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
17904	17904	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125593	125593	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125594	125594	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125596	125596	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125600	125600	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
125602	125602	Sedan	Lancer Evolution VIII	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	HIGH		READY
3394	3394	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
55456	55456	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
3393	3393	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
55453	55453	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
34985	34985	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
10452	10452	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
12186	12186	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
56825	56825	Sedan	Lancer VIII	CY0A	4	EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	HIGH		READY
124205	124205	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-01	HIGH		READY
34932	34932	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	HIGH	FQ 前部空气动力学套件形成独立外廓。	READY
34933	34933	Sedan	Lancer Evolution X	CZ4A	4	EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	HIGH	FQ 前部空气动力学套件形成独立外廓。	READY
55455	55455	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
55454	55454	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
34984	34984	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
10449	10449	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
34937	34937	Hatchback	Lancer VIII Sportback	CX0A	5	EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	HIGH		READY
18983	18983	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
17284	17284	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18617	18617	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18736	18736	SUV	Outlander I / Airtrek Turbo R		5	EU-MITSUBISHI-OUTLANDER-I-TURBO-R-SUV-5D-01	MEDIUM	Turbo-R 对应 Airtrek 矮车身外廓，独立建组。	READY
17400	17400	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18738	18738	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
18739	18739	SUV	Outlander I		5	EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	HIGH		READY
12146_prefl	12146	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	MEDIUM	同一 Ktype 覆盖改款前外廓。	READY
12146_facelift	12146	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	MEDIUM	同一 Ktype 覆盖改款后外廓。	READY
142850	142850	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	HIGH	4Work 商用衍生，外部车身按同期 Outlander II。	READY
142851	142851	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	HIGH	4Work 商用衍生，外部车身按同期 Outlander II。	READY
56332_prefl	56332	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	改款前外廓。	READY
56332_facelift	56332	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	2015年改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_11301-11400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-GRANDIS-2025-SUV-5D-01	4413	1797	1575	Automobile-Catalog Mitsubishi Grandis 2025 specifications	https://www.automobile-catalog.com/car/2025/3572180/mitsubishi_grandis_mildhybrid_1_3_turbo_140.html
EU-MITSUBISHI-GRANDIS-I-MPV-5D-01	4765	1795	1655	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2005910/mitsubishi_grandis_2_4_classic.html
EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-PREFL-01	3990	1690	1800	CarsGuide Mitsubishi Express 1983 dimensions	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983
EU-MITSUBISHI-L300-DELICA-II-VAN-2WD-FACELIFT-02	4035	1690	1815	CarsGuide Mitsubishi Express 1984 model dimensions	https://www.carsguide.com.au/mitsubishi/express/1984
EU-MITSUBISHI-L300-DELICA-II-PICKUP-2D-01	4690	1650	1535	CarsGuide Mitsubishi Express 1983 dimensions	https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983
EU-MITSUBISHI-L300-DELICA-II-MPV-4WD-01	4135	1695	1925	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/49040/mitsubishi_l-300_country_4x4.html
EU-MITSUBISHI-L300-III-VAN-SWB-01	4275	1690	1835	Automobile-Catalog Mitsubishi L-300 Bus 2.5 Diesel; Mitsubishi L300 P05V/P15V vehicle catalog	https://www.automobile-catalog.com/car/1987/2020160/mitsubishi_l-300_bus_2_5_diesel.html;https://www.autodoc.parts/spares/mitsubishi/l-300/l-300-box-p0-w-p1-w/3399-2-5-d-p05v-p05w-p15v
EU-MITSUBISHI-L300-III-VAN-LWB-HIGHROOF-01	4675	1690	1950	Swiss Federal Roads Office type approval 3M7516; K MOTORSHOP L300 III vehicle listing	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3M7516_F.pdf;https://www.kmotorshop.com/en/device/car-list/1813
EU-MITSUBISHI-L300-III-MPV-5D-2WD-PREFL-01	4275	1690	1835	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/60170/mitsubishi_l-300_bus_2_0_cat.html
EU-MITSUBISHI-L300-III-MPV-5D-2WD-FACELIFT-01	4285	1690	1835	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2020130/mitsubishi_l-300_bus_2_0_cat.html
EU-MITSUBISHI-L300-III-PICKUP-LWB-2D-01	4720	1720	1840	Swiss type approval 3M7535; Mitsubishi Parts Catalog L300 Truck P13T	https://www.dauto.ch/typenscheine/mitsubishi-l300-2-5-td-3m7535-jmbyzp150sa-x;https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&ssd=%24%2AKwEpHQxhYywwVl1weXgKFXFlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFEvKyowSxAZE1Bka3lzWmY9IW5qOzhfKisoXChyfBE5Nj0-djgnP2AcYShOPzA7OH5zYHZwOUNHUC04YAAAAAASwkvW%24&vid=0
EU-MITSUBISHI-L300-III-MPV-5D-4WD-PREFL-01	4365	1690	1975	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2020115/mitsubishi_l-300_allrad-bus_2_4_cat.html
EU-MITSUBISHI-L300-III-MPV-5D-4WD-FACELIFT-01	4375	1690	1975	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2020190/mitsubishi_l-300_allrad-bus_2_5_diesel_turbo.html
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-2WD-02	4935	1695	1610	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=30
EU-MITSUBISHI-L200-II-PICKUP-SINGLE-CAB-4WD-01	5095	1655	1690	Mitsubishi General Export K32T parts catalog; CarsGuide Mitsubishi Triton 1987 dimensions	https://www.mitzybitz.com/mitsubishi-l200/l200/general-export-5/k0-k3-0/k32t-20004wdlong-truck-standard-cablong5fmt-rhd-1986-01-01-2001-03-31;https://www.carsguide.com.au/mitsubishi/triton/1987
EU-MITSUBISHI-L200-II-PICKUP-DOUBLE-CAB-4WD-01	4920	1655	1740	Car.info Mitsubishi L200 Double Cab 2nd Generation; CarsGuide Mitsubishi Triton 1987 dimensions	https://www.car.info/en-se/mitsubishi/l200/l200-double-cab-70588;https://www.carsguide.com.au/mitsubishi/triton/1987
EU-MITSUBISHI-L200-III-PICKUP-SINGLE-CAB-4WD-FACELIFT-01	5010	1695	1750	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-4WD-FACELIFT-01	5125	1695	1775	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-CLUB-CAB-WIDE-4WD-FACELIFT-01	5125	1775	1800	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=94
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-4WD-FACELIFT-01	5010	1695	1780	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=95
EU-MITSUBISHI-L200-III-PICKUP-DOUBLE-CAB-WIDE-4WD-FACELIFT-01	5010	1775	1800	Mitsubishi Motors L200 1996 Workshop Manual	https://www.manualslib.com/manual/1556080/Mitsubishi-Motors-L200-1996.html?page=96
EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-WIDE-4WD-01	5205	1815	1780	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors L200 service bulletin MSB-19X00_31_51-001	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://mmc-manuals.ru/MSBv2/SATSU/MSB-19X00_31_51-001.pdf
EU-MITSUBISHI-L200-V-PICKUP-CLUB-CAB-4WD-01	5195	1785	1775	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors Deutschland L200 KJ0T Club Cab rescue sheet	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://rettungskarten-service.de/wp-content/uploads/L200-Club-Cab-Typ-KJ0T-ab-Modelljahr-2016.pdf
EU-MITSUBISHI-L200-V-PICKUP-DOUBLE-CAB-4WD-01	5205	1785	1775	Mitsubishi Motors Portugal L200 official brochure; Mitsubishi Motors España L200 KJ0T Double Cab rescue sheet	https://www.mitsubishi-motors.pt/content/dam/mitsubishi-motors-pt/images/brochures/L200_Brochure.pdf;https://www.mitsubishi-motors.es/content/dam/mitsubishi-motors-es/es/rescate/Hoja_de_rescate_L200_KJ0T_Doble_cabina.pdf
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-PREFL-01	4995	1750	1650	Mitsubishi Triton KA4/KB4 Factory Service Manual	https://www.scribd.com/doc/159429016/117-Mitsubishi-Triton-KA4-KB4-KB8-Factory-Service-Manual
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-2WD-FACELIFT-01	5185	1750	1645	EncyCARpedia Mitsubishi L200 2.5 DI-D 2WD Double Cab specifications	https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-double-cab-128-pick-up
EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-2WD-01	5040	1750	1655	EncyCARpedia Mitsubishi L200 2.5 DI-D 2WD Single Cab specifications	https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-single-cab-128-pick-up
EU-MITSUBISHI-L200-IV-PICKUP-SINGLE-CAB-4WD-01	5040	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-CLUB-CAB-4WD-01	5120	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-LONGBED-4WD-01	5185	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLE-CAB-WIDE-4WD-01	5005	1815	1780	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-L400-MPV-5D-2WD-01	4655	1695	1855	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/2020085/mitsubishi_space_gear_2400_glx.html
EU-MITSUBISHI-L400-MPV-5D-4WD-01	4655	1695	1965	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/2020055/mitsubishi_space_gear_2400_glx_4wd.html
EU-MITSUBISHI-L400-MPV-5D-2WD-PREFL-01	4595	1695	1855	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/2019980/mitsubishi_space_gear_2500_td_glx.html
EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-02	4115	1610	1335	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/1906685/mitsubishi_celeste_2000_gsr.html
EU-MITSUBISHI-LANCER-CELESTE-COUPE-3D-01	4115	1610	1330	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/1906670/mitsubishi_celeste_2000_gsr.html
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	4235	1670	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1934000/mitsubishi_lancer_hatchback_1800_gti-16v_cat.html
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-02	4235	1670	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1934225/mitsubishi_lancer_hatchback_1800_gti_16v_cat.html
EU-MITSUBISHI-LANCER-EVOLUTION-IV-SEDAN-4D-01	4330	1690	1415	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-evolution-iv-2.0-280hp-4wd-42185
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1375	Carfolio	https://www.carfolio.com/mitsubishi-lancer-gti-1.8-16v-152625
EU-MITSUBISHI-LANCER-V-WAGON-5D-4WD-01	4275	1690	1515	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/1952600/mitsubishi_lancer_wagon_1600_glxi_16v_4wd.html
EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	4290	1690	1395	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.5-110hp-15661
EU-MITSUBISHI-LANCER-VI-GSR-SEDAN-4D-01	4250	1690	1405	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.8-gsr-205hp-15662
EU-MITSUBISHI-LANCER-EVOLUTION-V-SEDAN-4D-01	4350	1770	1415	Auto-Data	https://www.auto-data.net/en/mitsubishi-lancer-evolution-v-2.0-280hp-4wd-15659
EU-MITSUBISHI-LANCER-VII-SEDAN-4D-01	4480	1695	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1994990/mitsubishi_lancer_1_6.html
EU-MITSUBISHI-LANCER-VII-WAGON-5D-01	4485	1695	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/1995020/mitsubishi_lancer_wagon_1_6.html
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	4490	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/1998080/mitsubishi_lancer_evolution_ix.html
EU-MITSUBISHI-LANCER-EVOLUTION-VII-SEDAN-4D-01	4455	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/1997390/mitsubishi_lancer_gsr_evolution_vii.html
EU-MITSUBISHI-LANCER-EVOLUTION-VIII-SEDAN-4D-01	4490	1770	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/1997870/mitsubishi_lancer_evo_viii_gsr.html
EU-MITSUBISHI-LANCER-VIII-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1996325/mitsubishi_lancer_1_8_di-d_cleartec_inform.html
EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-01	4495	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1997675/mitsubishi_lancer_gsr_evolution_x_5-speed.html
EU-MITSUBISHI-LANCER-EVOLUTION-X-SEDAN-4D-02	4505	1810	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1998200/mitsubishi_lancer_evolution_x_gsr_fq-360.html
EU-MITSUBISHI-LANCER-VIII-HATCHBACK-5D-01	4585	1760	1515	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1996220/mitsubishi_lancer_sportback_1_8.html
EU-MITSUBISHI-OUTLANDER-I-SUV-5D-01	4545	1750	1670	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/2010515/mitsubishi_outlander_2_0_invite_4wd.html
EU-MITSUBISHI-OUTLANDER-I-TURBO-R-SUV-5D-01	4465	1750	1540	Automobile-Catalog; Cars-Directory	https://www.automobile-catalog.com/car/2002/2010050/mitsubishi_airtek_turbo_r.html;https://www.cars-directory.net/specs/mitsubishi/airtrek/2002_10/15848/
EU-MITSUBISHI-OUTLANDER-II-SUV-5D-01	4640	1800	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2011595/mitsubishi_outlander_2_0_di-d_4wd_inform_invite.html
EU-MITSUBISHI-OUTLANDER-II-SUV-5D-02	4665	1800	1720	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/2011745/mitsubishi_outlander_2_2_di-d_plus_4wd_intense_instyle.html
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	4655	1800	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2012420/mitsubishi_outlander_2_0_2wd_cleartec_invite.html
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	4695	1810	1680	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2231735/mitsubishi_outlander_2_0_2wd_cleartec.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_11301-11400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-doc.ie/car-parts/timing-belt-10504/mitsubishi/l-300/l-300-bus-lo3-p-g-l0-2p/3389-1-6-l032p-l062p?utm_source=chatgpt.com "MITSUBISHI L300 / Delica II Minibus (LO3_P/G, L0_2P) 1.6 Timing belt - 65 hp Petrol 48 kW 1981 - 1986 4G32 ▷ AUTODOC"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2268 行）
- 累计尺寸组：dimension_groups_final.tsv（661 行）

