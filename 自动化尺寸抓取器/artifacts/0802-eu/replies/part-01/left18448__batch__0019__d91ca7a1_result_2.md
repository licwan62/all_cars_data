# 任务：left18448 第 1801-1900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0019__d91ca7a1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1801-1900 行

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
left18448 第 1801-1900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1801-1900_ktype_dimension_mapping_final.tsv
- left18448_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-2-SERIES-F22-COUPE-01	4432	1774	1418
EU-BMW-2-SERIES-F23-CONVERTIBLE-01	4432	1774	1413
EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-SERIES-F45-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	4568	1800	1612
EU-BMW-2-SERIES-F46-MPV-PREFL-01	4556	1800	1612
EU-BMW-2-SERIES-F74-GRAN-COUPE-01	4546	1800	1445
EU-BMW-2-SERIES-G42-COUPE-01	4537	1838	1390
EU-BMW-2-SERIES-U06-MPV-01	4386	1824	1576

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	2	220 D	Coupe	Heckantrieb	Diesel	Nov 2014	Sep 2020	116639
BMW	2	220 D	Cabriolet	Heckantrieb	Diesel	Mar 2014	Sep 2020	116641
BMW	2	220 D	Coupe	Heckantrieb	Diesel	Mar 2014	Sep 2020	147600
BMW	2	220 D	Cabriolet	Heckantrieb	Diesel	Mar 2014	Sep 2020	147603
BMW	2	220 D	Coupe	Frontantrieb	Diesel/Elektro	Nov 2024	-	160039
BMW	2	220 D Mild Hybrid	Großraumlimousine	Frontantrieb	Diesel/Elektro	Jul 2024	-	159202
BMW	2	220 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	Aug 2021	-	144700
BMW	2	220 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2014	Oct 2021	107977
BMW	2	220 D Xdrive	Coupe	Allrad	Diesel	Jun 2014	Sep 2020	109516
BMW	2	220 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2015	-	111077
BMW	2	220 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2014	Oct 2021	116626
BMW	2	220 D Xdrive	Großraumlimousine	Allrad	Diesel	Mar 2015	-	116631
BMW	2	220 D Xdrive	Coupe	Allrad	Diesel	Mar 2015	Sep 2020	116640
BMW	2	220 D Xdrive	Coupe	Allrad	Diesel	Jun 2014	Sep 2020	147601
BMW	2	220 I	Coupe	Heckantrieb	Benzin	Oct 2013	Jun 2021	58291
BMW	2	220 I	Cabriolet	Heckantrieb	Benzin	Apr 2014	Jun 2021	107982
BMW	2	220 I	Großraumlimousine	Frontantrieb	Benzin	Mar 2014	Oct 2021	108182
BMW	2	220 I	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	-	111074
BMW	2	220 I	Großraumlimousine	Frontantrieb	Benzin	Mar 2014	Oct 2021	116627
BMW	2	220 I	Coupe	Heckantrieb	Benzin	Sep 2015	Jun 2021	120246
BMW	2	220 I	Cabriolet	Heckantrieb	Benzin	Sep 2015	Jun 2021	120250
BMW	2	220 I	Coupe	Heckantrieb	Benzin	Aug 2021	-	144697
BMW	2	220 I Xdrive	Coupe	Allrad	Benzin	Mar 2021	-	143451
BMW	2	220i Mild Hybrid	Großraumlimousine	Frontantrieb	Benzin/Elektro	Nov 2021	-	145856
BMW	2	223 D Mild Hybrid Xdrive	Großraumlimousine	Allrad	Diesel/Elektro	Jul 2022	-	148357
BMW	2	223 Xdrive	Coupe	Allrad	Benzin/Elektro	Mar 2025	-	160819
BMW	2	223i Mild Hybrid	Großraumlimousine	Frontantrieb	Benzin/Elektro	Nov 2021	-	145859
BMW	2	223i Mild Hybrid Xdrive	Großraumlimousine	Allrad	Benzin/Elektro	Mar 2022	-	147094
BMW	2	225 D	Coupe	Heckantrieb	Diesel	Jan 2014	Jun 2017	100824
BMW	2	225 D	Coupe	Heckantrieb	Diesel	Jul 2015	May 2019	113348
BMW	2	225 D	Cabriolet	Heckantrieb	Diesel	Jul 2015	May 2019	113397
BMW	2	225 I	Großraumlimousine	Frontantrieb	Benzin	Nov 2013	Dec 2019	105897
BMW	2	225 I Xdrive	Großraumlimousine	Allrad	Benzin	Mar 2014	Oct 2021	108188
BMW	2	225 XE Plug-in-hybrid	Großraumlimousine	Allrad	Benzin/Elektro	Nov 2014	Oct 2021	117573
BMW	2	225e Xdrive	Großraumlimousine	Allrad	Benzin/Elektro	Nov 2021	-	145850
BMW	2	228 I	Coupe	Heckantrieb	Benzin	Jul 2014	Jun 2016	105903
BMW	2	228 I	Cabriolet	Heckantrieb	Benzin	Nov 2014	Jun 2016	107983
BMW	2	228 Xdrive	Coupe	Allrad	Benzin	Nov 2024	-	160825
BMW	2	230 I	Coupe	Heckantrieb	Benzin	Jul 2016	Jun 2021	120247
BMW	2	230 I	Cabriolet	Heckantrieb	Benzin	Jul 2016	Jun 2021	120251
BMW	2	230 I	Coupe	Heckantrieb	Benzin	Apr 2022	-	147093
BMW	2	230e Xdrive	Großraumlimousine	Allrad	Benzin/Elektro	Nov 2021	-	145853
BMW	2	M 235 I	Coupe	Heckantrieb	Benzin	Oct 2013	Jun 2016	58294
BMW	2	M 235 I	Cabriolet	Heckantrieb	Benzin	Nov 2014	Jun 2016	108000
BMW	2	M 235 I Xdrive	Coupe	Allrad	Benzin	Jul 2014	Jun 2016	105902
BMW	2	M 235 I Xdrive	Cabriolet	Allrad	Benzin	Jul 2015	Jun 2016	113398
BMW	2	M 240 I	Coupe	Heckantrieb	Benzin	Sep 2015	Jun 2021	120248
BMW	2	M 240 I	Cabriolet	Heckantrieb	Benzin	Sep 2015	Jun 2021	120252
BMW	2	M 240 I Xdrive	Coupe	Allrad	Benzin	Sep 2015	Jun 2021	120249
BMW	2	M 240 I Xdrive	Cabriolet	Allrad	Benzin	Sep 2015	Jun 2021	120253
BMW	2	M2	Coupe	Heckantrieb	Benzin	Nov 2015	Jun 2018	117272
BMW	2	M2	Coupe	Heckantrieb	Benzin	Nov 2022	-	151467
BMW	2	M2	Coupe	Heckantrieb	Benzin	Aug 2024	-	800126
BMW	2	M2 CS	Coupe	Heckantrieb	Benzin	Aug 2025	-	802011
BMW	2	M235 Xdrive	Coupe	Allrad	Benzin	Nov 2024	-	160033
BMW	2	M240 I	Coupe	Heckantrieb	Benzin	Jul 2022	-	148346
BMW	2	M240 I Xdrive	Coupe	Allrad	Benzin	Aug 2021	-	144698
BMW	2	M240 I Xdrive	Coupe	Allrad	Benzin/Elektro	Sep 2025	-	802374
BMW	3	316 CI	Coupe	Heckantrieb	Benzin	Apr 2000	Jul 2006	15895
BMW	3	316 CI	Coupe	Heckantrieb	Benzin	Jun 2002	Jul 2006	18823
BMW	3	316 D	Kombi	Heckantrieb	Diesel	Sep 2009	Jun 2012	11145
BMW	3	316 D	Kombi	Heckantrieb	Diesel	Nov 2012	Jun 2019	55125
BMW	3	316 D	Stufenheck	Heckantrieb	Diesel	Nov 2020	-	142479
BMW	3	316 D	Kombi	Heckantrieb	Diesel	Nov 2020	-	142481
BMW	3	316 D	Kombi	Heckantrieb	Diesel	Nov 2020	-	142482
BMW	3	316 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Nov 2020	-	142480
BMW	3	316 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	Nov 2020	-	142483
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	Dec 1998	Feb 2002	11042
BMW	3	316 I	Schrägheck	Heckantrieb	Benzin	Jan 1999	Aug 2000	11369
BMW	3	316 I	Kombi	Heckantrieb	Benzin	Mar 1997	May 1999	13259
BMW	3	316 I	Kombi	Heckantrieb	Benzin	Sep 1991	Jun 1994	14403
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	Apr 2000	Feb 2005	15894
BMW	3	316 I	Kombi	Heckantrieb	Benzin	Mar 2002	Feb 2005	16741
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	Jun 2002	Feb 2005	18822
BMW	3	316 I	Coupe	Heckantrieb	Benzin	Sep 2007	Jun 2013	55565
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	Jul 2012	Aug 2016	57472
BMW	3	316 I	Kombi	Heckantrieb	Benzin	Mar 2013	Jun 2015	59407
BMW	3	316 I Baur TC	Cabriolet	Heckantrieb	Benzin	Sep 1987	Dec 1989	121337
BMW	3	316 TI	Schrägheck	Heckantrieb	Benzin	Jun 2001	Feb 2005	15924
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	Dec 1999	Aug 2001	11400
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	Dec 2000	May 2006	124771
BMW	3	318 CI	Cabriolet	Heckantrieb	Benzin	Dec 2000	Aug 2006	126010
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	Dec 1999	Aug 2001	126107
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	Sep 2007	Oct 2011	5768
BMW	3	318 D	Kombi	Heckantrieb	Diesel	Oct 2002	Mar 2003	16742
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	Mar 2003	Feb 2005	18465
BMW	3	318 D	Kombi	Heckantrieb	Diesel	Mar 2003	Feb 2005	18466
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	Mar 2005	Aug 2007	18967
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	Mar 2012	Oct 2018	53234
BMW	3	318 D	Kombi	Heckantrieb	Diesel	Nov 2012	Jun 2015	55126
BMW	3	318 D	Schrägheck	Heckantrieb	Diesel	Mar 2013	Jun 2015	58799
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	Jul 2015	Oct 2018	113430
BMW	3	318 D	Kombi	Heckantrieb	Diesel	Jul 2015	Jun 2019	113448
BMW	3	318 D	Schrägheck	Heckantrieb	Diesel	Jul 2015	-	113453
BMW	3	318 D	Kombi	Heckantrieb	Diesel	Nov 2012	Jun 2019	116646
BMW	3	318 D	Schrägheck	Heckantrieb	Diesel	Mar 2013	Mar 2018	116654
BMW	3	318 D	Kasten/Kombi	Heckantrieb	Diesel	Nov 2019	Jun 2022	154697
BMW	3	318 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2013	Jun 2015	59797
BMW	3	318 D Xdrive	Kombi	Allrad	Diesel	Jul 2013	Jun 2015	59799
BMW	3	318 D Xdrive	Stufenheck	Allrad	Diesel	Jul 2015	Feb 2018	113432


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批全部 58 个 BMW 2 系列输入 Ktype，形成 68 条 `READY` 映射；其中 10 个覆盖 F45/F46 改款前后两种外廓的 Ktype 已拆分为派生行。
* 复用跨批次已有的 9 个尺寸组，不重复输出其尺寸事实。
* 首次建立 8 个尺寸组，覆盖 F22/F23 M Performance、F44 Gran Coupe、G42 M240i 后驱与 xDrive、F87 M2、G87 M2 和 G87 M2 CS。
* BMW 官方规格确认 F22/F23 的 M235i、M240i 外廓不同于普通 F22/F23，因此未错误复用普通 4432 mm 组。
* G42 M240i 后驱和 xDrive 的车高分别为 1397 mm、1404 mm，已分别建组；F87、G87 与 G87 M2 CS 也按各自专属外廓分组。

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：58
* READY 映射：68
* 待处理输入 Ktype：42
* 当前已引用尺寸组：17

  * 复用既有尺寸组：9
  * 本轮新增尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116639	116639	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
116641	116641	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
147600	147600	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
147603	147603	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
160039	160039	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
159202	159202	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
144700	144700	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
107977_prefl	107977	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
107977_facelift	107977	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
109516	109516	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
111077_prefl	111077	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
111077_facelift	111077	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116626_prefl	116626	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
116626_facelift	116626	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
116631_prefl	116631	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
116631_facelift	116631	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116640	116640	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
147601	147601	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
58291	58291	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
107982	107982	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
108182_prefl	108182	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
108182_facelift	108182	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
111074_prefl	111074	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
111074_facelift	111074	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116627_prefl	116627	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
116627_facelift	116627	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
120246	120246	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
120250	120250	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
144697	144697	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
143451	143451	Coupe	2 Series F44 Gran Coupe	F44	4	EU-BMW-2-SERIES-F44-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
145856	145856	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
148357	148357	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
160819	160819	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
145859	145859	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
147094	147094	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
100824	100824	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
113348	113348	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
113397	113397	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
105897_prefl	105897	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
105897_facelift	105897	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
108188_prefl	108188	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
108188_facelift	108188	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
117573_prefl	117573	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
117573_facelift	117573	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
145850	145850	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
105903	105903	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
107983	107983	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
160825	160825	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
120247	120247	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
120251	120251	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
147093	147093	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
145853	145853	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
58294	58294	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
108000	108000	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
105902	105902	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
113398	113398	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120248	120248	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120252	120252	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120249	120249	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120253	120253	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
117272	117272	Coupe	M2 F87	F87	2	EU-BMW-M2-F87-COUPE-01	HIGH	M2 专属宽体外廓。	READY
151467	151467	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-COUPE-01	HIGH	G87 M2 外廓分支。	READY
800126	800126	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-COUPE-01	HIGH	G87 M2 外廓分支。	READY
802011	802011	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-CS-COUPE-01	HIGH	G87 M2 CS 专属外廓分支。	READY
160033	160033	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
148346	148346	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-RWD-COUPE-01	HIGH	M240i 后驱专属外廓分支。	READY
144698	144698	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	HIGH	M240i xDrive 专属外廓分支。	READY
802374	802374	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	HIGH	M240i xDrive 专属外廓分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	4454	1774	1408	BMW M235i Coupé official technical specifications; BMW M240i Coupé official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0165234EN/250291;https://www.press.bmwgroup.com/global/article/attachment/T0270425EN/401705
EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	4454	1774	1403	BMW M235i Convertible official technical specifications; BMW M240i Convertible official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0202265EN/293527;https://www.press.bmwgroup.com/global/article/attachment/T0327250EN/473317
EU-BMW-2-SERIES-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group PressClub first BMW 2 Series Gran Coupé press kit	https://www.press.bmwgroup.com/poland/article/detail/T0301802PL/pierwsze-w-historii-bmw-serii-2-gran-coupe?language=pl
EU-BMW-2-SERIES-G42-M240I-RWD-COUPE-01	4548	1838	1397	BMW M240i Coupé official technical specifications valid 05/2022	https://www.press.bmwgroup.com/global/article/attachment/T0393118EN/552858
EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	4548	1838	1404	BMW 2 Series Coupé M240i xDrive official technical specifications 06/2024	https://www.press.bmwgroup.com/asia/article/attachment/T0443240EN/618422
EU-BMW-M2-F87-COUPE-01	4468	1854	1410	BMW M2 Coupé official technical specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0238704EN/332758
EU-BMW-M2-G87-COUPE-01	4580	1887	1403	BMW Group PressClub Canada 2025 BMW M2 press kit	https://www.press.bmwgroup.com/canada/article/detail/T0443109EN/the-new-2025-bmw-m2?language=en
EU-BMW-M2-G87-CS-COUPE-01	4587	1887	1395	BMW M2 CS official technical specifications 05/2025	https://www.press.bmwgroup.com/global/article/attachment/T0450299EN/632433
```

## 下一步优先处理

1. 按 E30、E36、E46、E90/E91/E92、F30/F31/F34、G20/G21 聚类剩余 42 个 BMW 3 Ktype。
2. 优先批量复用同代际、同车身和同改款阶段的尺寸组。
3. 单独核对 Baur TC、Compact、Gran Turismo、`Kasten/Kombi` 以及改款前后存在外廓变化的分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1801-1900_ktype_dimension_mapping_final.tsv
- left18448_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 剩余 42 个 BMW 3 系列 Ktype 已全部闭合；涉及改款前后外廓变化的 Ktype 已拆分派生行。
* 新增并闭合 E30、E36、E46、E9x、F3x、G2x 相关尺寸组；F31 xDrive 改款前三维按 BMW 官方规格确认为 `4624 × 1811 × 1434 mm`。([BMW Group PressClub][1])
* 已完成轻量机械检查：固定表头、`id` 唯一、尺寸组唯一、映射引用闭合、三维及来源非空、无孤立尺寸组。
* 当前批次 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：121
* PENDING 映射：0
* 完整 DIMENSION_GROUP：43
* 映射引用闭合：通过
* 最终文件生成：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116639	116639	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
116641	116641	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
147600	147600	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
147603	147603	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
160039	160039	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
159202	159202	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
144700	144700	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
107977_prefl	107977	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
107977_facelift	107977	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
109516	109516	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
111077_prefl	111077	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
111077_facelift	111077	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116626_prefl	116626	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
116626_facelift	116626	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
116631_prefl	116631	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
116631_facelift	116631	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116640	116640	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
147601	147601	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
58291	58291	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
107982	107982	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
108182_prefl	108182	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
108182_facelift	108182	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
111074_prefl	111074	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-PREFL-01	HIGH	F46 Gran Tourer 改款前物理分支。	READY
111074_facelift	111074	MPV	2 Series F46 Gran Tourer	F46	5	EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	HIGH	F46 Gran Tourer 改款后物理分支。	READY
116627_prefl	116627	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
116627_facelift	116627	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
120246	120246	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
120250	120250	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
144697	144697	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
143451	143451	Coupe	2 Series F44 Gran Coupe	F44	4	EU-BMW-2-SERIES-F44-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
145856	145856	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
148357	148357	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
160819	160819	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
145859	145859	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
147094	147094	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
100824	100824	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
113348	113348	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
113397	113397	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
105897_prefl	105897	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
105897_facelift	105897	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
108188_prefl	108188	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
108188_facelift	108188	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
117573_prefl	117573	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-PREFL-01	HIGH	F45 Active Tourer 改款前物理分支。	READY
117573_facelift	117573	MPV	2 Series F45 Active Tourer	F45	5	EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	HIGH	F45 Active Tourer 改款后物理分支。	READY
145850	145850	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
105903	105903	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
107983	107983	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
160825	160825	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
120247	120247	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-COUPE-01	HIGH		READY
120251	120251	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-CONVERTIBLE-01	HIGH		READY
147093	147093	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-COUPE-01	HIGH		READY
145853	145853	MPV	2 Series U06 Active Tourer	U06	5	EU-BMW-2-SERIES-U06-MPV-01	HIGH		READY
58294	58294	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
108000	108000	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
105902	105902	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
113398	113398	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120248	120248	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120252	120252	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120249	120249	Coupe	2 Series F22	F22	2	EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
120253	120253	Convertible	2 Series F23	F23	2	EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	HIGH	M235i/M240i M Performance 外廓分支。	READY
117272	117272	Coupe	M2 F87	F87	2	EU-BMW-M2-F87-COUPE-01	HIGH	M2 专属宽体外廓。	READY
151467	151467	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-COUPE-01	HIGH	G87 M2 外廓分支。	READY
800126	800126	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-COUPE-01	HIGH	G87 M2 外廓分支。	READY
802011	802011	Coupe	M2 G87	G87	2	EU-BMW-M2-G87-CS-COUPE-01	HIGH	G87 M2 CS 专属外廓分支。	READY
160033	160033	Coupe	2 Series F74 Gran Coupe	F74	4	EU-BMW-2-SERIES-F74-GRAN-COUPE-01	HIGH	四门 Gran Coupe 车身。	READY
148346	148346	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-RWD-COUPE-01	HIGH	M240i 后驱专属外廓分支。	READY
144698	144698	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	HIGH	M240i xDrive 专属外廓分支。	READY
802374	802374	Coupe	2 Series G42	G42	2	EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	HIGH	M240i xDrive 专属外廓分支。	READY
15895	15895	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
18823	18823	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
11145	11145	Wagon	3 Series E91 Touring	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
55125_prefl	55125	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	F31 Touring 改款前物理分支。	READY
55125_facelift	55125	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	F31 Touring 改款后物理分支。	READY
142479_prefl	142479	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20 改款前物理分支。	READY
142479_facelift	142479	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	HIGH	G20 改款后物理分支。	READY
142481_prefl	142481	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-PREFL-01	HIGH	G21 Touring 改款前物理分支。	READY
142481_facelift	142481	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	HIGH	G21 Touring 改款后物理分支。	READY
142482_prefl	142482	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-PREFL-01	HIGH	G21 Touring 改款前物理分支。	READY
142482_facelift	142482	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	HIGH	G21 Touring 改款后物理分支。	READY
142480_prefl	142480	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20 改款前物理分支。	READY
142480_facelift	142480	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	HIGH	G20 改款后物理分支。	READY
142483_prefl	142483	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-PREFL-01	HIGH	G21 Touring 改款前物理分支。	READY
142483_facelift	142483	Wagon	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	HIGH	G21 Touring 改款后物理分支。	READY
11042	11042	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
11369	11369	Hatchback	3 Series E36 Compact	E36/5	3	EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	HIGH		READY
13259	13259	Wagon	3 Series E36 Touring	E36/3	5	EU-BMW-3-E36-TOURING-WAGON-01	HIGH		READY
14403	14403	Wagon	3 Series E30 Touring	E30/5	5	EU-BMW-3-E30-TOURING-WAGON-01	HIGH		READY
15894	15894	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
16741	16741	Wagon	3 Series E46 Touring	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18822	18822	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
55565_prefl	55565	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	E92 Coupé 改款前物理分支。	READY
55565_facelift	55565	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	E92 Coupé 改款后物理分支。	READY
57472_prefl	57472	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	F30 改款前物理分支。	READY
57472_facelift	57472	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	F30 改款后物理分支。	READY
59407	59407	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
121337	121337	Convertible	3 Series E30 Baur Topcabriolet	E30/2	2	EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	MEDIUM	Baur TC2 半敞篷车身分支。	READY
15924	15924	Hatchback	3 Series E46 Compact	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH		READY
11400	11400	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
124771	124771	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
126010	126010	Convertible	3 Series E46	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-01	HIGH		READY
126107	126107	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-01	HIGH		READY
5768_prefl	5768	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	E90 改款前物理分支。	READY
5768_facelift	5768	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	E90 改款后物理分支。	READY
16742	16742	Wagon	3 Series E46 Touring	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18465	18465	Sedan	3 Series E46	E46/4	4	EU-BMW-3-E46-SEDAN-01	HIGH		READY
18466	18466	Wagon	3 Series E46 Touring	E46/3	5	EU-BMW-3-E46-TOURING-WAGON-01	HIGH		READY
18967	18967	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH		READY
53234_prefl	53234	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-PREFL-01	HIGH	F30 改款前物理分支。	READY
53234_facelift	53234	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH	F30 改款后物理分支。	READY
55126	55126	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH		READY
58799	58799	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
113430	113430	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	HIGH		READY
113448	113448	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH		READY
113453	113453	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
116646_prefl	116646	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-PREFL-01	HIGH	F31 Touring 改款前物理分支。	READY
116646_facelift	116646	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	HIGH	F31 Touring 改款后物理分支。	READY
116654	116654	Hatchback	3 Series F34 Gran Turismo	F34	5	EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
154697	154697	Van	3 Series G21 Touring	G21	5	EU-BMW-3-G21-WAGON-RWD-PREFL-01	MEDIUM	G21 Touring 商用载货衍生，外部车身边界按 Touring。	READY
59797	59797	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	HIGH		READY
59799	59799	Wagon	3 Series F31 Touring	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH		READY
113432	113432	Sedan	3 Series F30	F30	4	EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1801-1900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-2-SERIES-F22-COUPE-01	4432	1774	1418	BMW 2 Series Coupé official technical specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0162084EN/242844
EU-BMW-2-SERIES-F23-CONVERTIBLE-01	4432	1774	1413	BMW 2 Series Convertible official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0192483EN/295142
EU-BMW-2-SERIES-F74-GRAN-COUPE-01	4546	1800	1445	BMW 2 Series Gran Coupé official press kit	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0445675EN_GB/the-new-bmw-2-series-gran-coup%C3%A9?language=en_GB
EU-BMW-2-SERIES-U06-MPV-01	4386	1824	1576	BMW 2 Series Active Tourer official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0442984EN/617681
EU-BMW-2-SERIES-G42-COUPE-01	4537	1838	1390	BMW 2 Series Coupé official technical specifications	https://www.press.bmwgroup.com/france/article/attachment/T0337274FR/484947
EU-BMW-2-SERIES-F45-MPV-PREFL-01	4342	1800	1555	BMW 2 Series Active Tourer official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0186826EN/325511
EU-BMW-2-SERIES-F45-MPV-FACELIFT-01	4354	1800	1555	BMW 2 Series Active Tourer facelift official technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286635CS/417963
EU-BMW-2-SERIES-F46-MPV-PREFL-01	4556	1800	1612	BMW 2 Series Gran Tourer official press kit	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0204180EN_GB/the-new-bmw-2-series-gran-tourer?language=en_GB
EU-BMW-2-SERIES-F46-MPV-FACELIFT-01	4568	1800	1612	BMW 2 Series Gran Tourer facelift official technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286637CS/417966
EU-BMW-2-SERIES-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group PressClub first BMW 2 Series Gran Coupé press kit	https://www.press.bmwgroup.com/poland/article/detail/T0301802PL/pierwsze-w-historii-bmw-serii-2-gran-coupe?language=pl
EU-BMW-2-SERIES-F22-MPERFORMANCE-COUPE-01	4454	1774	1408	BMW M235i Coupé official technical specifications; BMW M240i Coupé official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0165234EN/250291;https://www.press.bmwgroup.com/global/article/attachment/T0270425EN/401705
EU-BMW-2-SERIES-F23-MPERFORMANCE-CONVERTIBLE-01	4454	1774	1403	BMW M235i Convertible official technical specifications; BMW M240i Convertible official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0202265EN/293527;https://www.press.bmwgroup.com/global/article/attachment/T0327250EN/473317
EU-BMW-M2-F87-COUPE-01	4468	1854	1410	BMW M2 Coupé official technical specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0238704EN/332758
EU-BMW-M2-G87-COUPE-01	4580	1887	1403	BMW Group PressClub Canada 2025 BMW M2 press kit	https://www.press.bmwgroup.com/canada/article/detail/T0443109EN/the-new-2025-bmw-m2?language=en
EU-BMW-M2-G87-CS-COUPE-01	4587	1887	1395	BMW M2 CS official technical specifications 05/2025	https://www.press.bmwgroup.com/global/article/attachment/T0450299EN/632433
EU-BMW-2-SERIES-G42-M240I-RWD-COUPE-01	4548	1838	1397	BMW M240i Coupé official technical specifications valid 05/2022	https://www.press.bmwgroup.com/global/article/attachment/T0393118EN/552858
EU-BMW-2-SERIES-G42-M240I-XDRIVE-COUPE-01	4548	1838	1404	BMW 2 Series Coupé M240i xDrive official technical specifications 06/2024	https://www.press.bmwgroup.com/asia/article/attachment/T0443240EN/618422
EU-BMW-3-E46-COUPE-01	4488	1757	1369	BMW E46 Coupé official technical data	https://www.press.bmwgroup.com/italy/article/attachment/T0144010IT/220376
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418	BMW 3 Series Touring E91 facelift official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0039740EN/60981
EU-BMW-3-F31-WAGON-RWD-PREFL-01	4624	1811	1429	BMW 316d/318d Touring official specifications valid 11/2012	https://www.press.bmwgroup.com/global/article/attachment/T0132112EN/207744/Specifications_BMW_3_Series_Touring_316d_318d_11_2012.pdf
EU-BMW-3-F31-WAGON-RWD-FACELIFT-01	4633	1811	1429	BMW 3 Series Touring facelift official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan G20 official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354
EU-BMW-3-G20-SEDAN-RWD-FACELIFT-01	4713	1827	1440	BMW 318d Sedan official technical specifications 05/2024	https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620072
EU-BMW-3-G21-WAGON-RWD-PREFL-01	4709	1827	1440	BMW 3 Series Touring G21 official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0297109EN/432678/The_new_BMW_3_Series_Touring_Specifications.pdf
EU-BMW-3-G21-WAGON-RWD-FACELIFT-01	4713	1827	1440	BMW 3 Series Touring official technical specifications 05/2024	https://www.press.bmwgroup.com/global/article/attachment/T0442333EN/620073
EU-BMW-3-E46-SEDAN-01	4471	1739	1415	BMW E46 Sedan official technical data	https://www.press.bmwgroup.com/korea/article/detail/T0045096KO/bmw-325i-330i-%EC%B6%9C%EC%8B%9C-3%EC%8B%9C%EB%A6%AC%EC%A6%88-%EC%A0%84-%EB%AA%A8%EB%8D%B8-%EA%B5%AC%EC%B6%95?language=ko
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1698	1393	Automobile-Catalog BMW 316i Compact specifications	https://www.automobile-catalog.com/car/1994/269855/bmw_316i_compact.html
EU-BMW-3-E36-TOURING-WAGON-01	4433	1698	1391	Automobile-Catalog BMW 316i Touring specifications	https://www.automobile-catalog.com/car/1995/270695/bmw_316i_touring.html
EU-BMW-3-E30-TOURING-WAGON-01	4325	1645	1380	Automobile-Catalog BMW E30 Touring specifications	https://www.automobile-catalog.com/car/1991/266480/bmw_324td_touring.html
EU-BMW-3-E46-TOURING-WAGON-01	4478	1739	1409	BMW E46 Touring official technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	BMW 3 Series Coupé E92 official specifications	https://www.press.bmwgroup.com/south-africa/article/attachment/T0129163EN/195139
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	BMW 3 Series Coupé E92 facelift official specifications	https://www.press.bmwgroup.com/portugal/article/attachment/T0127866PT/193969
EU-BMW-3-F30-SEDAN-RWD-PREFL-01	4624	1811	1429	BMW 316i Sedan official specifications valid 11/2012	https://www.press.bmwgroup.com/global/article/attachment/T0131800EN/207748/Specifications_BMW_3_Series_Sedan_316i_11_2012.pdf
EU-BMW-3-F30-SEDAN-RWD-FACELIFT-01	4633	1811	1429	BMW 3 Series Sedan facelift official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380	BMW Group Classic E30 Baur Topcabriolet; BMWman E30 Baur dimensions	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-907-1.bmw-3-series-baur-topcabriolet-e30.html;https://www.bmwman.ru/blog/models/item/avtomobil-bmw-3-y-serii-e30-325i-baur-topcabriolet-1985-1991-gody
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408	BMW E46 Compact official technical data	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E46-CONVERTIBLE-01	4488	1757	1372	Automobile-Catalog BMW E46 Cabrio specifications	https://www.automobile-catalog.com/car/2001/276350/bmw_318ci_cabrio.html
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421	BMW 3 Series Sedan E90 official specifications	https://www.press.bmwgroup.com/south-africa/article/attachment/T0129152EN/195123
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421	BMW 3 Series Sedan E90 facelift official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0039673EN/60844
EU-BMW-3-F34-GRAN-TURISMO-HATCHBACK-01	4824	1828	1508	BMW 3 Series Gran Turismo official press kit; BMW 3 Series Gran Turismo facelift official press kit	https://www.press.bmwgroup.com/global/article/attachment/T0136657EN/256325/The_new_BMW_3_Series_Gran_Turismo.pdf;https://www.press.bmwgroup.com/slovak/article/attachment/T0260376SK/359995
EU-BMW-3-F30-SEDAN-XDRIVE-PREFL-01	4624	1811	1434	BMW 3 Series Sedan xDrive official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0127960EN/191798
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434	BMW 320d xDrive Touring official specifications valid 03/2013	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208688/Specifications_BMW_3_Series_Touring_320d_xDrive_03_2013.pdf
EU-BMW-3-F30-SEDAN-XDRIVE-FACELIFT-01	4633	1811	1434	BMW 3 Series Sedan xDrive facelift official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0234765EN/349813/The_new_BMW_3_Series_Sedan_The_new_BMW_3_Series_Touring_Specifications_EN.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1801-1900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208688/Specifications_BMW_3_Series_Touring_320d_xDrive_03_2013.pdf "https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208688/Specifications_BMW_3_Series_Touring_320d_xDrive_03_2013.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2213 行）
- 累计尺寸组：dimension_groups_final.tsv（674 行）

