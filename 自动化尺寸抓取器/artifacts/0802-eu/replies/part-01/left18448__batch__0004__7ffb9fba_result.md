# 任务：left18448 第 301-400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0004__7ffb9fba


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 301-400 行

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
left18448 第 301-400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALPINA-B6-E21-SEDAN-01	4355	1610	1360
EU-ALPINA-B6-E30-SEDAN-2D-01	4325	1645	1350
EU-ALPINA-B6-E30-SEDAN-2D-02	4325	1645	1355
EU-ALPINA-B6-E30-SEDAN-4D-01	4325	1645	1355
EU-ALPINA-B6-E36-SEDAN-01	4433	1698	1373
EU-ALPINA-B6-E63-COUPE-01	4820	1855	1371
EU-ALPINA-B6-E64-CONVERTIBLE-01	4820	1855	1371

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Alpina	B6	Biturbo	Coupe	Heckantrieb	Benzin	Sep 2011	Sep 2014	12515
Alpina	B6	Biturbo	Cabriolet	Heckantrieb	Benzin	Sep 2011	Sep 2014	12517
Alpina	B6	Biturbo	Coupe	Heckantrieb	Benzin	Jan 2015	Mar 2016	113469
Alpina	B6	Biturbo	Cabriolet	Heckantrieb	Benzin	Jan 2015	Mar 2016	113470
Alpina	B6	Biturbo Allrad	Coupe	Allrad	Benzin	Apr 2014	Dec 2014	100940
Alpina	B6	Biturbo Allrad	Coupe	Allrad	Benzin	Jan 2015	Mar 2016	113736
Alpina	B7	3	Stufenheck	Heckantrieb	Benzin	Dec 1978	Feb 1982	11737
Alpina	B7	3	Coupe	Heckantrieb	Benzin	Dec 1978	Feb 1982	11741
Alpina	B7	3.4	Coupe	Heckantrieb	Benzin	May 1982	Aug 1987	11742
Alpina	B7	3.4	Coupe	Heckantrieb	Benzin	Oct 1986	Jun 1988	11743
Alpina	B7	3.5	Stufenheck	Heckantrieb	Benzin	Nov 1981	May 1982	11738
Alpina	B7	3.5	Stufenheck	Heckantrieb	Benzin	Apr 1984	Jul 1987	11739
Alpina	B7	3.5	Stufenheck	Heckantrieb	Benzin	Aug 1986	Dec 1987	11740
Alpina	B7	4.4	Stufenheck	Heckantrieb	Benzin	Dec 2003	Jun 2008	18045
Alpina	B7	Biturbo	Stufenheck	Heckantrieb	Benzin	Jul 2012	Jul 2015	59393
Alpina	B7	Biturbo Allrad	Stufenheck	Allrad	Benzin	Jul 2012	Jul 2015	59394
Alpina	B7	Biturbo Heckantrieb	Stufenheck	Heckantrieb	Benzin	Mar 2017	Dec 2022	126181
Alpina	B8	4.6	Stufenheck	Heckantrieb	Benzin	Jan 1995	Mar 1998	11679
Alpina	B8	4.6	Kombi	Heckantrieb	Benzin	Jan 1995	Mar 1998	11680
Alpina	B8	4.6	Coupe	Heckantrieb	Benzin	Jan 1995	Mar 1998	11681
Alpina	B8	4.6	Cabriolet	Heckantrieb	Benzin	Jan 1995	Nov 1998	11682
Alpina	B8	Biturbo Allrad	Coupe	Allrad	Benzin	Mar 2021	Dec 2025	143575
Alpina	B8	GT Allrad	Coupe	Allrad	Benzin	Aug 2024	Dec 2025	801386
Alpina	B9	3.4	Stufenheck	Allrad	Benzin	Nov 1981	Dec 1985	11683
Alpina	B9	3.4	Coupe	Heckantrieb	Benzin	Jul 1982	Dec 1985	11684
Alpina	C1	2.3	Stufenheck	Heckantrieb	Benzin	Apr 1980	Jul 1983	11619
Alpina	C1	2.3	Stufenheck	Heckantrieb	Benzin	Aug 1983	Nov 1985	11620
Alpina	C1	2.5	Stufenheck	Heckantrieb	Benzin	Oct 1986	Jun 1988	11621
Alpina	C2	2.5	Stufenheck	Heckantrieb	Benzin	Jul 1985	Mar 1988	11622
Alpina	C2	2.7	Stufenheck	Heckantrieb	Benzin	Feb 1986	Jul 1987	11624
Alpina	C2	2.7	Stufenheck	Heckantrieb	Benzin	Mar 1987	Aug 1987	11625
Alpina	C2	2.7	Cabriolet	Heckantrieb	Benzin	Feb 1986	Jul 1987	11631
Alpina	C2	2.7 Allrad	Stufenheck	Allrad	Benzin	Feb 1986	Jul 1987	11630
Alpina	D10	3.0 D Biturbo	Stufenheck	Heckantrieb	Diesel	Apr 2000	Oct 2003	11879
Alpina	D10	3.0 D Biturbo	Kombi	Heckantrieb	Diesel	Apr 2000	Oct 2003	13997
Alpina	D3	2	Stufenheck	Heckantrieb	Diesel	Dec 2005	Apr 2008	50872
Alpina	D3	2	Kombi	Heckantrieb	Diesel	Dec 2005	Apr 2008	50878
Alpina	D3	Biturbo	Stufenheck	Heckantrieb	Diesel	Jul 2013	Jul 2018	100944
Alpina	D3	Biturbo	Kombi	Heckantrieb	Diesel	Jul 2013	Jul 2018	100945
Alpina	D3	Biturbo Allrad	Kombi	Allrad	Diesel	Jul 2013	Jul 2018	100946
Alpina	D4	Biturbo	Coupe	Heckantrieb	Diesel	Sep 2014	Jun 2020	108075
Alpina	D4	Biturbo	Cabriolet	Heckantrieb	Diesel	Sep 2014	Jun 2020	108076
Alpina	D4 gran	S	Coupe	Allrad	Diesel/Elektro	Jul 2022	Dec 2025	151538
Alpina	D5	Biturbo	Stufenheck	Heckantrieb	Diesel	Sep 2011	Dec 2016	10392
Alpina	D5	S Allrad	Stufenheck	Allrad	Diesel	Jul 2017	Jun 2020	128500
Alpina	D5	S Allrad	Kombi	Allrad	Diesel	Jul 2017	Jun 2020	128505
Alpina	D5	S Allrad	Stufenheck	Allrad	Diesel	Jul 2020	Feb 2024	142900
Alpina	D5	S Allrad	Kombi	Allrad	Diesel	Jul 2020	Feb 2024	142901
Alpina	D5	S Mild-hybrid Allrad	Stufenheck	Allrad	Diesel/Elektro	Nov 2020	Feb 2024	142904
Alpina	Rle roadster	2.7	Cabriolet	Heckantrieb	Benzin	Aug 1990	Sep 1991	11736
Alpina	Roadster	3.3	Cabriolet	Heckantrieb	Benzin	Jul 2003	Dec 2005	18046
Alpina	Roadster	4.8 V8	Cabriolet	Heckantrieb	Benzin	Jun 2002	Oct 2003	16701
Alpina	Xb7	Biturbo Mild-hybrid	SUV	Allrad	Benzin/Elektro	Oct 2022	Nov 2025	151347
Alpina	Xd3	Biturbo Allrad	SUV	Allrad	Diesel	Apr 2013	Jun 2018	100943
Alpina	Xd3	Biturbo Allrad	SUV	Allrad	Diesel	Apr 2022	Jun 2024	147248
Alpina	Xd3	Biturbo Mild-hybrid Allrad	SUV	Allrad	Diesel/Elektro	Nov 2020	Jun 2024	142929
Alpina	Xd4	Biturbo Allrad	SUV	Allrad	Diesel	Apr 2022	Jun 2024	147250
Alpine	A110 ii	1.8 GT	Coupe	Heckantrieb	Benzin	Nov 2021	Oct 2024	147428
Alpine	A110 ii	1.8 R Ultime	Coupe	Heckantrieb	Benzin	Dec 2025	-	802811
Alpine	A290	180	Schrägheck	Frontantrieb	Elektro	Jul 2024	-	159584
Alpine	A290	220	Schrägheck	Frontantrieb	Elektro	Jul 2024	-	159585
Alpine	A390	GT	SUV	Allrad	Elektro	Dec 2025	-	162475
Alpine	A390	GTS	SUV	Allrad	Elektro	Dec 2025	-	162476
ARO	10	1.4 AWD	Geländewagen offen	Allrad	Benzin	Jun 1984	Oct 1999	151161
ARO	240-244	2.5	Geländewagen geschlossen	Allrad	Benzin	Apr 1978	Dec 1998	11221
ARO	240-244	2.7 D	Geländewagen geschlossen	Allrad	Diesel	Sep 1989	Dec 1998	11219
ARO	240-244	2.7 D	Geländewagen geschlossen	Allrad	Diesel	Apr 1985	Dec 1998	11220
ARO	Spartana pick up	1,2 AWD	Geländewagen offen	Allrad	Benzin	Jan 1997	Dec 2003	127222
Artega	Gt	3.6	Coupe	Heckantrieb	Benzin	Jul 2009	Sep 2012	10194
Asia Motors	Hi-Topic	2.7 D Heckantrieb	Bus	Heckantrieb	Diesel	Jun 1993	Dec 1999	8038
Asia Motors	Rocsta	1.8 Allrad	Geländewagen geschlossen	Allrad	Benzin	Feb 1992	Dec 1998	57222
Aston Martin	Db12	4.0 V8	Coupe	Heckantrieb	Benzin	Sep 2023	-	154906
Aston Martin	Db12 volante	4.0 V8	Cabriolet	Heckantrieb	Benzin	Aug 2023	-	155939
Aston Martin	Db6 vantage	4	Coupe	Heckantrieb	Benzin	Oct 1964	Dec 1970	8179
Aston Martin	Db6 vantage	4	Coupe	Heckantrieb	Benzin	Oct 1964	Dec 1970	8180
Aston Martin	Db6 volante	4	Cabriolet	Heckantrieb	Benzin	Oct 1964	Dec 1970	8181
Aston Martin	Db7 vantage	5.9	Coupe	Heckantrieb	Benzin	Mar 1999	Oct 2003	12199
Aston Martin	Db7 volante	3.2	Cabriolet	Heckantrieb	Benzin	Jan 1996	Oct 2003	8202
Aston Martin	Db9 vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Jan 2004	Oct 2016	17825
Aston Martin	Db9 vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Jan 2008	Jul 2012	34741
Aston Martin	Db9 vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Jul 2012	Oct 2016	57111
Aston Martin	Db9 vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Apr 2015	Oct 2016	119776
Aston Martin	Db9 vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Apr 2004	Apr 2008	800914
Aston Martin	Db9 volante	6	Cabriolet	Heckantrieb	Benzin	Sep 2015	Oct 2016	116330
Aston Martin	Db9 volante	6.0 V12	Cabriolet	Heckantrieb	Benzin	Apr 2004	Jul 2012	17826
Aston Martin	Db9 volante	6.0 V12	Cabriolet	Heckantrieb	Benzin	Sep 2005	Jul 2012	34743
Aston Martin	Db9 volante	6.0 V12	Cabriolet	Heckantrieb	Benzin	Jul 2012	Oct 2016	57112
Aston Martin	Db9 volante	6.0 V12	Cabriolet	Heckantrieb	Benzin	Apr 2004	Apr 2008	800913
Aston Martin	Dbs	5.2 770 Ultimate	Coupe	Heckantrieb	Benzin	Jan 2023	-	153380
Aston Martin	Dbs vantage	4	Coupe	Heckantrieb	Benzin	Jan 1966	Dec 1972	8182
Aston Martin	Dbs vantage	5.3	Coupe	Heckantrieb	Benzin	Oct 1968	Aug 1972	123876
Aston Martin	Dbs vantage	6.0 V12	Coupe	Heckantrieb	Benzin	Sep 2007	-	34756
Aston Martin	Dbs volante	5.2 770 Ultimate	Cabriolet	Heckantrieb	Benzin	Apr 2023	-	153381
Aston Martin	Dbs volante	6.0 V12	Cabriolet	Heckantrieb	Benzin	Sep 2007	-	34766
Aston Martin	Dbx	4.0 Allrad	SUV	Allrad	Benzin	Mar 2022	-	147148
Aston Martin	Dbx	4.0 S Allrad	SUV	Allrad	Benzin	Apr 2025	-	802353
Aston Martin	Lagonda i	5.3	Stufenheck	Heckantrieb	Benzin	Jan 1976	Dec 1997	8183
Aston Martin	Lagonda i shooting brake	5.3	Kombi	Heckantrieb	Benzin	Jan 1976	Dec 1997	8184
Aston Martin	Lagonda i shooting brake	5.3	Kombi	Heckantrieb	Benzin	Nov 1985	Dec 1987	125881
Aston Martin	Rapide	6.0 S	Schrägheck	Heckantrieb	Benzin	Feb 2013	Feb 2014	58925


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合首个物理车身簇：Alpina B6 Bi-Turbo。
* 2011–2014 的 F13 Coupé、F12 Cabriolet，与 2015 起改款车型因高度变化分别建组。
* 两个“Allrad + Coupe”输入实际对应四门 F06 Gran Coupé；2014 年型与 2015–2016 改款后的高度不同，分别建组。B6 Coupé/Cabriolet 的前后期尺寸由同期 ALPINA 技术资料直接支持；F06 四驱车型边界由车型资料和四驱仅用于 Gran Coupé 的记录交叉确认。([乐帕纳斯博客][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：6
* PENDING／尚未闭合：94
* 已确认尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12515	12515	Coupe	B6 Bi-Turbo (F13)	F13	2	EU-ALPINA-B6-F13-COUPE-PREFL-01	HIGH	F13改款前双门车身。	READY
12517	12517	Convertible	B6 Bi-Turbo (F12)	F12	2	EU-ALPINA-B6-F12-CONVERTIBLE-PREFL-01	HIGH	F12改款前敞篷车身。	READY
113469	113469	Coupe	B6 Bi-Turbo (F13 LCI)	F13	2	EU-ALPINA-B6-F13-COUPE-FACELIFT-01	HIGH	F13改款后双门车身。	READY
113470	113470	Convertible	B6 Bi-Turbo (F12 LCI)	F12	2	EU-ALPINA-B6-F12-CONVERTIBLE-FACELIFT-01	HIGH	F12改款后敞篷车身。	READY
100940	100940	Coupe	B6 Bi-Turbo Gran Coupé (F06)	F06	4	EU-ALPINA-B6-F06-GRAN-COUPE-PREFL-01	HIGH	输入Coupe实际为四门四驱Gran Coupé改款前车身。	READY
113736	113736	Coupe	B6 Bi-Turbo Gran Coupé (F06 LCI)	F06	4	EU-ALPINA-B6-F06-GRAN-COUPE-FACELIFT-01	HIGH	输入Coupe实际为四门四驱Gran Coupé改款后车身。	READY
```

F12/F13 同期官方技术表分别给出 Coupé 与 Convertible 的车身高度；四驱 B6 对应 F06 四门 Gran Coupé，而非双门 F13。

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B6-F13-COUPE-PREFL-01	4894	1894	1377	BMW ALPINA B6 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b6_biturbo_coupe_convertible.pdf
EU-ALPINA-B6-F12-CONVERTIBLE-PREFL-01	4894	1894	1373	BMW ALPINA B6 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b6_biturbo_coupe_convertible.pdf
EU-ALPINA-B6-F13-COUPE-FACELIFT-01	4894	1894	1375	BMW ALPINA B6 Bi-Turbo official brochure, March 2017	https://i.i-sgcm.com/new_cars/cars/11863/brochures/brochure_20180129033803.pdf
EU-ALPINA-B6-F12-CONVERTIBLE-FACELIFT-01	4894	1894	1371	BMW ALPINA B6 Bi-Turbo official brochure, March 2017	https://i.i-sgcm.com/new_cars/cars/11863/brochures/brochure_20180129033803.pdf
EU-ALPINA-B6-F06-GRAN-COUPE-PREFL-01	5007	1894	1392	Car and Driver 2015 BMW Alpina B6 xDrive Gran Coupe test	https://www.caranddriver.com/reviews/a15107156/2015-bmw-alpina-b6-gran-coupe-test-review/
EU-ALPINA-B6-F06-GRAN-COUPE-FACELIFT-01	5007	1894	1398	BMW Group Canada ALPINA B6 2018MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0269584EN/391264
```

官方 B6 技术表明确列出不含后视镜的 1894 mm 车宽及两种双门车身的独立高度；F06 改款前后采用直接车型规格中的 5007 × 1894 × 1392/1398 mm。([乐帕纳斯博客][1])

## 下一步优先处理

优先闭合 Alpina B7 的 E12、E24、E28、E32、E65、F01/F02 与 G12 车身簇，并先区分早期输入中同名 B7 的 Sedan/Coupé 代际边界。

推进信号：CONTINUE

[1]: https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b6_biturbo_coupe_convertible.pdf "lay-ALPINA-B6-BiTurbo-2013_UK.indd"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Alpina B7 的 E12、E24、E24/1 与 E28 车身簇。
* E12 的 B7 Turbo 与 B7 S Turbo 共用四门车身尺寸组。
* 1982 年更新后的 E24/1 与早期 E24 分组；后期催化版仅发动机变化，复用 E24/1 尺寸组。
* E28 的普通版与后期催化版外廓一致，共用尺寸组。([阿尔皮娜档案馆][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：13
* PENDING 映射：87
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11737	11737	Sedan	B7 Turbo	E12	4	EU-ALPINA-B7-E12-SEDAN-01	HIGH	E12四门B7 Turbo车身。	READY
11741	11741	Coupe	B7 Turbo Coupé	E24	2	EU-ALPINA-B7-E24-COUPE-PREFL-01	HIGH	早期E24双门车身。	READY
11742	11742	Coupe	B7 Turbo Coupé/1	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	1982年更新后的E24/1双门车身。	READY
11743	11743	Coupe	B7 Turbo Coupé/1 B7/3	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	后期催化发动机版，外廓沿用E24/1。	READY
11738	11738	Sedan	B7 S Turbo	E12	4	EU-ALPINA-B7-E12-SEDAN-01	HIGH	E12四门B7 S Turbo车身。	READY
11739	11739	Sedan	B7 Turbo/1	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	E28四门B7 Turbo/1车身。	READY
11740	11740	Sedan	B7 Turbo/1 B7/3	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	后期催化发动机版，外廓沿用E28。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B7-E12-SEDAN-01	4620	1690	1405	EncyCARpedia Alpina B7 Turbo E12 specifications; UltimateSpecs Alpina B7 S Turbo E12 specifications	https://www.encycarpedia.com/alpina/78-b7-turbo-e12-saloon;https://www.ultimatespecs.com/car-specs/Alpina/119631/Alpina-E12-5-Series-B7-S-Turbo.html
EU-ALPINA-B7-E24-COUPE-PREFL-01	4755	1725	1345	UltimateSpecs Alpina E24 B7 Turbo Coupé specifications	https://www.ultimatespecs.com/car-specs/Alpina/123619/Alpina-E24-6-Series-B7-Turbo-Coupe.html
EU-ALPINA-B7-E24-COUPE-FACELIFT-01	4755	1725	1345	UltimateSpecs Alpina E24/1 B7 Turbo Coupé specifications	https://www.ultimatespecs.com/car-specs/Alpina/123622/Alpina-E24-1-6-Series-B7-Turbo-Coupe.html
EU-ALPINA-B7-E28-SEDAN-01	4620	1700	1395	UltimateSpecs Alpina E28 B7 Turbo/1 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119627/Alpina-E28-5-Series-B7-Turbo-1-300HP.html
```

## 下一步优先处理

优先闭合 Alpina B7 的 E65、F01/F02 与 G11/G12 三代四门车身，先确认标准轴距与长轴距边界，再批量关联对应 Ktype。

推进信号：CONTINUE

[1]: https://www.alpina-archive.com/?page_id=175&utm_source=chatgpt.com "B7 Turbo/1"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Alpina B7 的 E65、F01/F02 LCI 和 G12 车身簇。
* Ktype `59393`、`59394` 的车型边界均覆盖 F01 标准轴距和 F02 长轴距，因此分别拆为 `swb`、`lwb` 派生行；四驱 F01 因整车高度不同单独建组，F02 长轴距外廓共用一个尺寸组。([AUTODOC Danmark][1])
* Ktype `126181` 覆盖 G12 改款前后，前后保险杠造型使车长由 5250 mm 变为 5268 mm，已拆分为 `prefl` 与 `facelift`。([AUTODOC][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：17
* READY 映射行：20
* PENDING 输入 Ktype：83
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18045	18045	Sedan	B7 (E65)	E65	4	EU-ALPINA-B7-E65-SEDAN-01	HIGH	E65标准轴距四门车身。	READY
59393_swb	59393	Sedan	B7 Bi-Turbo LCI	F01	4	EU-ALPINA-B7-F01-SEDAN-RWD-01	HIGH	后驱标准轴距F01车身。	READY
59393_lwb	59393	Sedan	B7 Bi-Turbo LCI	F02	4	EU-ALPINA-B7-F02-SEDAN-LWB-01	HIGH	后驱长轴距F02车身。	READY
59394_swb	59394	Sedan	B7 Bi-Turbo LCI	F01	4	EU-ALPINA-B7-F01-SEDAN-AWD-01	HIGH	四驱标准轴距F01车身。	READY
59394_lwb	59394	Sedan	B7 Bi-Turbo LCI	F02	4	EU-ALPINA-B7-F02-SEDAN-LWB-01	HIGH	四驱长轴距F02车身。	READY
126181_prefl	126181	Sedan	B7 Bi-Turbo	G12	4	EU-ALPINA-B7-G12-SEDAN-PREFL-01	HIGH	G12改款前长轴距车身。	READY
126181_facelift	126181	Sedan	B7 Bi-Turbo LCI	G12	4	EU-ALPINA-B7-G12-SEDAN-FACELIFT-01	HIGH	G12改款后长轴距车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B7-E65-SEDAN-01	5029	1902	1477	UltimateSpecs Alpina E65 B7 specifications	https://www.ultimatespecs.com/car-specs/Alpina/M11388/E65-7-Series
EU-ALPINA-B7-F01-SEDAN-RWD-01	5092	1902	1485	BMW ALPINA B7 Bi-Turbo official brochure, April 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b7_biturbo_saloon.pdf
EU-ALPINA-B7-F02-SEDAN-LWB-01	5232	1902	1484	Automobile-Catalog 2014 Alpina B7 Bi-Turbo L specifications; Edmunds 2013 BMW ALPINA B7 LWB xDrive specifications	https://www.automobile-catalog.com/car/2014/1762190/alpina_b7_biturbo_l.html;https://www.edmunds.com/bmw/alpina-b7/2013/st-401657909/features-specs/
EU-ALPINA-B7-F01-SEDAN-AWD-01	5093	1902	1491	Edmunds 2014 BMW ALPINA B7 SWB xDrive specifications	https://www.edmunds.com/bmw/alpina-b7/2014/st-200491673/features-specs/
EU-ALPINA-B7-G12-SEDAN-PREFL-01	5250	1902	1491	BMW Group Canada 2018 ALPINA B7 Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0276855EN/399017
EU-ALPINA-B7-G12-SEDAN-FACELIFT-01	5268	1902	1491	Goo-net BMW ALPINA B7 Bi-Turbo Limousine Allrad catalogue	https://www.goo-net-exchange.com/catalog/BMW_ALPINA__B7/10142951/
```

## 下一步优先处理

优先闭合 Alpina B8 的 E36 Sedan、Touring、Coupé、Cabriolet 四种车身，以及 G16 B8 Gran Coupé与 B8 GT；其中 E36 车身应先查询已有跨批次尺寸组，避免重复建组。

推进信号：CONTINUE

[1]: https://www.autodoc.dk/reservedele/baerearm-og-rep-saet-10671/alpina/b7/b7-f01-f02/59393-biturbo?utm_source=chatgpt.com "Bærearm ALPINA B7 Sedan (F01, F02) BITURBO 540 HK ..."
[2]: https://www.autodoc.co.uk/car-parts/gasket-rocker-cover-10327/alpina/b7/b7-g12/126181-biturbo-rear-wheel-drive "Rocker cover gasket for ALPINA B7 Saloon (G12) 4.4 BiTurbo Heckantrieb 608 hp Petrol 2017 - 2026 N63 B44 C | AUTODOC"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Alpina B8 的 E36 Sedan、Touring、Coupé、Cabriolet 四种独立车身。
* Ktype `143575` 跨越 G16 改款节点：早期官方资料高度为 1423 mm，2022 年改款资料为 1428 mm，因此拆分为 `prefl` 与 `facelift`。
* B8 GT 虽与普通改款 B8 的三维相同，但具有专属外部空气动力组件，独立建组，不与普通 B8 合并。其官方技术资料明确给出 5092 × 1932 × 1428 mm，宽度另列含后视镜 2137 mm。([Alpina][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：23
* READY 映射行：27
* PENDING 输入 Ktype：77
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11679	11679	Sedan	B8 4.6	E36	4	EU-ALPINA-B8-E36-SEDAN-01	HIGH	E36四门车身。	READY
11680	11680	Wagon	B8 4.6 Touring	E36	5	EU-ALPINA-B8-E36-WAGON-01	HIGH	E36五门Touring车身。	READY
11681	11681	Coupe	B8 4.6 Coupé	E36	2	EU-ALPINA-B8-E36-COUPE-01	HIGH	E36双门Coupé车身。	READY
11682	11682	Convertible	B8 4.6 Cabriolet	E36	2	EU-ALPINA-B8-E36-CONVERTIBLE-01	HIGH	E36双门敞篷车身。	READY
143575_prefl	143575	Coupe	B8 Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-PREFL-01	HIGH	G16改款前四门Gran Coupé车身。	READY
143575_facelift	143575	Coupe	B8 Gran Coupé LCI	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-FACELIFT-01	HIGH	G16改款后四门Gran Coupé车身。	READY
801386	801386	Coupe	B8 GT Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-GT-01	HIGH	G16改款后GT专属外部套件车身。	READY
```

E36 各输入分别对应四门、五门 Touring、双门 Coupé 和双门 Cabriolet，不因发动机相同合并。([Auto Data][2])

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B8-E36-SEDAN-01	4433	1698	1373	Auto-Data Alpina B8 E36 4.6 Sedan specifications	https://www.auto-data.net/en/alpina-b8-e36-4.6-i-v8-32v-333hp-1643
EU-ALPINA-B8-E36-WAGON-01	4433	1698	1371	UltimateSpecs Alpina E36 Touring B8 4.6 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119039/Alpina-E36-3-Series-Touring-B8-46.html
EU-ALPINA-B8-E36-COUPE-01	4433	1710	1346	Auto-Data Alpina B8 E36 4.6 Coupe specifications	https://www.auto-data.net/en/alpina-b8-coupe-e36-4.6-i-v8-24v-333hp-1646
EU-ALPINA-B8-E36-CONVERTIBLE-01	4433	1710	1328	UltimateSpecs Alpina E36 Cabriolet B8 4.6 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119037/Alpina-E36-3-Series-Cabriolet-B8-46.html
EU-ALPINA-B8-G16-GRAN-COUPE-PREFL-01	5092	1932	1423	BMW Group Canada MY22 ALPINA B8 Gran Coupé Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0338596EN/486423
EU-ALPINA-B8-G16-GRAN-COUPE-FACELIFT-01	5092	1932	1428	ALPINA BMW ALPINA B8 official brochure February 2022	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2022_02_DE/B8/index.html
EU-ALPINA-B8-G16-GRAN-COUPE-GT-01	5092	1932	1428	ALPINA BMW ALPINA B8 GT official technical data	https://b8gt.alpina.de/wp-content/uploads/2025/01/BMW_ALPINA_B8_GT_Technical_Data.pdf
```

## 下一步优先处理

优先闭合 Alpina B9 与 C1/C2 的 E21、E30 车身簇，先查询已存在的 B6 E21、B6 E30 尺寸组；仅在物理外廓及三维完全一致时复用，否则创建 B9、C1 或 C2 独立尺寸组。

推进信号：CONTINUE

[1]: https://b8gt.alpina.de/wp-content/uploads/2025/01/BMW_ALPINA_B8_GT_Technical_Data.pdf?utm_source=chatgpt.com "TECHNICAL DATA"
[2]: https://www.auto-data.net/en/alpina-b8-e36-4.6-i-v8-32v-333hp-1643?utm_source=chatgpt.com "Alpina B8 (E36) 4.6 i V8 32V (333 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Alpina B9 的 E28 Sedan 与 E24/1 Coupé。两者三维分别与本批已建的 B7 E28、B7 E24/1 尺寸组完全一致，直接复用，不重复建组。([阿尔皮娜档案馆][1])
* 闭合 C1 2.3：Ktype `11619` 为 E21 双门 Sedan，`11620` 为 E30 双门 Sedan，均复用已有同外廓尺寸组。([primex-bg.com][2])
* Ktype `11621` 同时覆盖 E30 双门与四门 C1 2.5，已拆为两个派生映射；两者三维相同，但门数和侧围结构不同，分别建立尺寸组。([UltimateSpecs][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：28
* READY 映射行：33
* PENDING 输入 Ktype：72
* 当前映射引用的已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11683	11683	Sedan	B9 3.5	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	E28四门车身。	READY
11684	11684	Coupe	B9 3.5 Coupé/1	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	E24/1双门车身。	READY
11619	11619	Sedan	C1 2.3	E21	2	EU-ALPINA-B6-E21-SEDAN-01	HIGH	E21双门车身。	READY
11620	11620	Sedan	C1 2.3/1	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-01	HIGH	E30双门车身。	READY
11621_2dr	11621	Sedan	C1 2.5	E30	2	EU-ALPINA-C1-E30-SEDAN-2D-01	HIGH	Ktype覆盖双门车身。	READY
11621_4dr	11621	Sedan	C1 2.5	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖四门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-C1-E30-SEDAN-2D-01	4325	1645	1380	UltimateSpecs Alpina E30 C1 2.5 2-door specifications	https://www.ultimatespecs.com/car-specs/Alpina/123088/Alpina-E30-3-Series-C1-25-2-door.html
EU-ALPINA-C1-E30-SEDAN-4D-01	4325	1645	1380	UltimateSpecs Alpina E30 C1 2.5 4-door specifications	https://www.ultimatespecs.com/car-specs/Alpina/123089/Alpina-E30-3-Series-C1-25-4-door.html
```

## 下一步优先处理

优先闭合 Alpina C2 的 `11622`、`11624`、`11625`、`11631`、`11630`，按 E30 双门、四门、Cabriolet 与 Allrad 分支批量建立关联，并复用本轮已经闭合的 E30 外廓组。

推进信号：CONTINUE

[1]: https://www.alpina-archive.com/?page_id=174 "Alpina-Archive | B9 3.5"
[2]: https://primex-bg.com/search-by-automobile.html?vehicle=11619&utm_source=chatgpt.com "Tyres for ALPINA C1 (E21) 1980-1983 rim 7 x 16 engine ..."
[3]: https://www.ultimatespecs.com/car-specs/Alpina/123088/Alpina-E30-3-Series-C1-25-2-door.html "Alpina E30 3 Series C1 2.5 2-door Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Alpina C2 的 5 个 Ktype。C2 2.5、C2 2.7 以及催化版 C2 2.7 均存在 E30 双门和四门 Sedan，已按门数拆分。双门外廓复用现有 `EU-ALPINA-B6-E30-SEDAN-2D-02`，四门外廓复用现有 `EU-ALPINA-C1-E30-SEDAN-4D-01`。([UltimateSpecs][1])
* C2 2.7 Allrad 确认为 E30 双门 Sedan，因宽度和高度不同新建独立尺寸组。([UltimateSpecs][2])
* C2 2.7 Cabriolet 确认为双门敞篷车身，新建独立尺寸组。([UltimateSpecs][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：33
* READY 映射行：41
* PENDING 输入 Ktype：67
* 当前映射引用的已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11622_2dr	11622	Sedan	C2 2.5	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖E30双门车身。	READY
11622_4dr	11622	Sedan	C2 2.5	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖E30四门车身。	READY
11624_2dr	11624	Sedan	C2 2.7 C2/1	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖E30双门车身。	READY
11624_4dr	11624	Sedan	C2 2.7 C2/1	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖E30四门车身。	READY
11625_2dr	11625	Sedan	C2 2.7 C2/2	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖催化版E30双门车身。	READY
11625_4dr	11625	Sedan	C2 2.7 C2/2	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖催化版E30四门车身。	READY
11631	11631	Convertible	C2 2.7 Cabriolet	E30	2	EU-ALPINA-C2-E30-CONVERTIBLE-01	HIGH	E30双门敞篷车身。	READY
11630	11630	Sedan	C2 2.7 Allrad	E30	2	EU-ALPINA-C2-E30-SEDAN-2D-AWD-01	HIGH	E30双门四驱车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-C2-E30-CONVERTIBLE-01	4325	1645	1345	UltimateSpecs Alpina E30 Convertible C2 2.7 specifications	https://www.ultimatespecs.com/car-specs/Alpina/123092/Alpina-E30-3-Series-Convertible-C2-27-210HP.html
EU-ALPINA-C2-E30-SEDAN-2D-AWD-01	4325	1662	1380	UltimateSpecs Alpina E30 C2 2.7 2-door Allrad specifications	https://www.ultimatespecs.com/car-specs/Alpina/123406/Alpina-E30-3-Series-C2-27-2-door-Allrad.html
```

## 下一步优先处理

优先闭合 Alpina D10、D3 与 D4，按 E39 Sedan/Touring、E90/E91、F30/F31、F32/F33 和 G26 物理车身聚类，并优先批量复用同代已确认尺寸组。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Alpina/119041/Alpina-E30-3-Series-C2-25-2-door.html "Alpina E30 3 Series C2 2.5 2-door Specs, Performance, Comparisons"
[2]: https://www.ultimatespecs.com/car-specs/Alpina/123406/Alpina-E30-3-Series-C2-27-2-door-Allrad.html "Alpina E30 3 Series C2 2.7 2-door Allrad Specs, Performance, Comparisons"
[3]: https://www.ultimatespecs.com/car-specs/Alpina/123092/Alpina-E30-3-Series-Convertible-C2-27-210HP.html "Alpina E30 3 Series Convertible C2 2.7 210HP Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Alpina D10 的 E39 Sedan、Touring，以及第一代 Alpina D3 的 E90 Sedan、E91 Touring。
* 四个 Ktype 均唯一对应单一物理车身，无需派生拆分。所用宽度均明确为不含后视镜口径。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：37
* READY 映射行：45
* PENDING 输入 Ktype：63
* 当前映射引用的已确认尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11879	11879	Sedan	D10 Bi-Turbo	E39	4	EU-ALPINA-D10-E39-SEDAN-01	HIGH	E39四门Sedan车身。	READY
13997	13997	Wagon	D10 Bi-Turbo Touring	E39	5	EU-ALPINA-D10-E39-WAGON-01	HIGH	E39五门Touring车身。	READY
50872	50872	Sedan	D3	E90	4	EU-ALPINA-D3-E90-SEDAN-01	HIGH	E90改款前四门车身。	READY
50878	50878	Wagon	D3 Touring	E91	5	EU-ALPINA-D3-E91-WAGON-01	HIGH	E91改款前五门Touring车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-D10-E39-SEDAN-01	4775	1800	1415	Automobile-Catalog 2001 Alpina D10 Biturbo specifications	https://www.automobile-catalog.com/car/2001/287735/alpina_d10_biturbo.html
EU-ALPINA-D10-E39-WAGON-01	4805	1800	1420	Automobile-Catalog 2001 Alpina D10 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2001/287765/alpina_d10_biturbo_touring.html
EU-ALPINA-D3-E90-SEDAN-01	4520	1817	1413	Automobile-Catalog 2005 Alpina D3 specifications	https://www.automobile-catalog.com/car/2005/288515/alpina_d3.html
EU-ALPINA-D3-E91-WAGON-01	4520	1817	1418	Automobile-Catalog 2007 Alpina D3 Touring specifications	https://www.automobile-catalog.com/car/2007/288530/alpina_d3_touring.html
```

## 下一步优先处理

优先闭合 Ktype `100944`、`100945`、`100946` 的 F30/F31 D3 Bi-Turbo，按改款前后拆分，并判断 F31 后驱和四驱高度是否需要独立尺寸组；随后处理 F32/F33/G26 D4。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/287765/alpina_d10_biturbo_touring.html?utm_source=chatgpt.com "2001 Alpina D10 Biturbo Touring Specs Review (180 kW / 245 PS / 241 hp) (for Europe )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Ktype `100944`、`100945`、`100946` 的 F30/F31 D3 Bi-Turbo 车身簇。
* 三个 Ktype 均跨越 F30/F31 LCI 外廓变化节点：改款前车长为 4628 mm，改款后为 4632 mm，因此分别拆为 `prefl` 与 `facelift`。
* F31 后驱 Touring 高度为 1428 mm，Allrad Touring 高度为 1431 mm，分别建立尺寸组；其不含后视镜宽度均为 1811 mm。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：40
* READY 映射行：51
* PENDING 输入 Ktype：60
* 当前映射引用的已确认尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100944_prefl	100944	Sedan	D3 Bi-Turbo	F30	4	EU-ALPINA-D3-F30-SEDAN-PREFL-01	HIGH	F30改款前四门车身。	READY
100944_facelift	100944	Sedan	D3 Bi-Turbo LCI	F30	4	EU-ALPINA-D3-F30-SEDAN-FACELIFT-01	HIGH	F30改款后四门车身。	READY
100945_prefl	100945	Wagon	D3 Bi-Turbo Touring	F31	5	EU-ALPINA-D3-F31-WAGON-RWD-PREFL-01	HIGH	F31改款前后驱Touring车身。	READY
100945_facelift	100945	Wagon	D3 Bi-Turbo Touring LCI	F31	5	EU-ALPINA-D3-F31-WAGON-RWD-FACELIFT-01	HIGH	F31改款后后驱Touring车身。	READY
100946_prefl	100946	Wagon	D3 Bi-Turbo Touring Allrad	F31	5	EU-ALPINA-D3-F31-WAGON-AWD-PREFL-01	HIGH	F31改款前四驱Touring车身。	READY
100946_facelift	100946	Wagon	D3 Bi-Turbo Touring Allrad LCI	F31	5	EU-ALPINA-D3-F31-WAGON-AWD-FACELIFT-01	HIGH	F31改款后四驱Touring车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

下列改款前后尺寸均来自对应年份和驱动形式的直接车型规格页，页面明确将宽度标为不含后视镜。([汽车目录][1])

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-D3-F30-SEDAN-PREFL-01	4628	1811	1428	Automobile-Catalog 2014 Alpina D3 Biturbo Limousine specifications	https://www.automobile-catalog.com/car/2014/1953200/alpina_d3_biturbo_limousine.html
EU-ALPINA-D3-F30-SEDAN-FACELIFT-01	4632	1811	1428	Automobile-Catalog 2016 Alpina D3 Biturbo Limousine specifications	https://www.automobile-catalog.com/car/2016/2501780/alpina_d3_biturbo_limousine.html
EU-ALPINA-D3-F31-WAGON-RWD-PREFL-01	4628	1811	1428	Automobile-Catalog 2014 Alpina D3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2014/1953215/alpina_d3_biturbo_touring.html
EU-ALPINA-D3-F31-WAGON-RWD-FACELIFT-01	4632	1811	1428	Automobile-Catalog 2016 Alpina D3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2016/2501825/alpina_d3_biturbo_touring.html
EU-ALPINA-D3-F31-WAGON-AWD-PREFL-01	4628	1811	1431	Automobile-Catalog 2014 Alpina D3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2014/1953230/alpina_d3_biturbo_touring_allrad.html
EU-ALPINA-D3-F31-WAGON-AWD-FACELIFT-01	4632	1811	1431	Automobile-Catalog 2016 Alpina D3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2016/2501855/alpina_d3_biturbo_touring_allrad.html
```

## 下一步优先处理

优先闭合 Ktype `108075`、`108076`、`151538` 的 D4 车身簇，分别处理 F32 Coupé、F33 Cabriolet 和 G26 Gran Coupé，并按改款造成的实际三维变化拆分。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2014/1953200/alpina_d3_biturbo_limousine.html?utm_source=chatgpt.com "2014 Alpina D3 Biturbo Limousine Specs Review (257 kW / 350 PS / 345 hp) (for Europe )"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Alpina D4 的 F32 Coupé、F33 Cabriolet 和 G26 Gran Coupé 三个 Ktype。
* F32 改款前后三维均为 `4640 × 1825 × 1382 mm`，保持单一映射和尺寸组。([Auto Data][1])
* F33 改款后高度由 `1382 mm` 变为 `1378 mm`，Ktype `108076` 拆分为 `prefl`、`facelift`。([Auto Data][2])
* G26 2022–2025 改款前后三维保持 `4792 × 1850 × 1440 mm`，复用单一尺寸组。([阿尔皮纳汽车][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：43
* READY 映射行：55
* PENDING 输入 Ktype：57
* 当前映射引用的已确认尺寸组：43
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108075	108075	Coupe	D4 Bi-Turbo	F32	2	EU-ALPINA-D4-F32-COUPE-01	HIGH	F32双门Coupé，改款前后三维一致。	READY
108076_prefl	108076	Convertible	D4 Bi-Turbo Cabriolet	F33	2	EU-ALPINA-D4-F33-CONVERTIBLE-PREFL-01	HIGH	F33改款前双门敞篷车身。	READY
108076_facelift	108076	Convertible	D4 Bi-Turbo Cabriolet LCI	F33	2	EU-ALPINA-D4-F33-CONVERTIBLE-FACELIFT-01	HIGH	F33改款后双门敞篷车身。	READY
151538	151538	Coupe	D4 S Gran Coupé	G26	5	EU-ALPINA-D4-G26-GRAN-COUPE-01	HIGH	输入Coupe对应五门Gran Coupé，改款前后三维一致。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-D4-F32-COUPE-01	4640	1825	1382	Auto-Data Alpina D4 Coupe F32 specifications; Auto-Data Alpina D4 Coupe F32 facelift specifications	https://www.auto-data.net/en/alpina-d4-coupe-f32-3.0d-350hp-switch-tronic-24156;https://www.auto-data.net/en/alpina-d4-coupe-f32-facelift-2017-3.0d-350hp-switch-tronic-37428
EU-ALPINA-D4-F33-CONVERTIBLE-PREFL-01	4640	1825	1382	Auto-Data Alpina D4 Cabrio F33 specifications	https://www.auto-data.net/en/alpina-d4-cabrio-f33-3.0d-350hp-switch-tronic-24225
EU-ALPINA-D4-F33-CONVERTIBLE-FACELIFT-01	4640	1825	1378	Auto-Data Alpina D4 Cabrio F33 facelift specifications	https://www.auto-data.net/en/alpina-d4-cabrio-f33-facelift-2017-3.0d-350hp-switch-tronic-37429
EU-ALPINA-D4-G26-GRAN-COUPE-01	4792	1850	1440	BMW ALPINA D4 S Gran Coupé official brochure; Auto-Data Alpina D4 Gran Coupe G26 facelift specifications	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2022_06_INT/D4_S/epaper/ausgabe.pdf;https://www.auto-data.net/en/alpina-d4-gran-coupe-g26-facelift-2024-s-3.0-355hp-mild-hybrid-awd-switch-tronic-53137
```

## 下一步优先处理

优先闭合 Alpina D5 的 F10、G30 Sedan 与 G31 Touring，按驱动形式和 2020 年改款节点核对实际外廓变化并批量关联。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alpina-d4-coupe-f32-generation-4874?utm_source=chatgpt.com "Alpina D4 Coupe (F32) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alpina-d4-cabrio-f33-3.0d-350hp-switch-tronic-24225?utm_source=chatgpt.com "Alpina D4 Cabrio (F33) 3.0d (350 Hp) Switch-Tronic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2022_06_INT/D4_S/epaper/ausgabe.pdf?utm_source=chatgpt.com "ALPINA

MANUFACTURER OF
EXCLUSIVE AUTOMOBILESBMW A"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Alpina D5 Bi-Turbo 的 F10 Sedan。2011–2016 年覆盖期内外廓尺寸保持 `4905 × 1860 × 1469 mm`，无需按改款拆分。([乐帕纳斯博客][1])
* 闭合 D5 S 的 G30 Sedan、G31 Touring 改款前车身；2017 年官方资料分别确认两种车身均为 `4956 × 1868 × 1466 mm`。
* 闭合 G30/G31 改款后车身，车长变为 4978 mm。官方资料另列含后视镜宽度 2126 mm，因此落盘的 1868 mm 为不含后视镜宽度。
* Ktype `142900` 与 `142904` 共用 G30 改款后尺寸组；轻混动力未形成不同物理外廓。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：49
* READY 映射行：61
* PENDING 输入 Ktype：51
* 当前映射引用的已确认尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10392	10392	Sedan	D5 Bi-Turbo	F10	4	EU-ALPINA-D5-F10-SEDAN-01	HIGH	F10四门Sedan车身。	READY
128500	128500	Sedan	D5 S	G30	4	EU-ALPINA-D5-G30-SEDAN-PREFL-01	HIGH	G30改款前四门车身。	READY
128505	128505	Wagon	D5 S Touring	G31	5	EU-ALPINA-D5-G31-WAGON-PREFL-01	HIGH	G31改款前五门Touring车身。	READY
142900	142900	Sedan	D5 S LCI	G30	4	EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	HIGH	G30改款后四门车身。	READY
142901	142901	Wagon	D5 S Touring LCI	G31	5	EU-ALPINA-D5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门Touring车身。	READY
142904	142904	Sedan	D5 S Mild-Hybrid LCI	G30	4	EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	HIGH	轻混版本沿用G30改款后车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-D5-F10-SEDAN-01	4905	1860	1469	BMW ALPINA D5 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_biturbo_saloon_touring.pdf
EU-ALPINA-D5-G30-SEDAN-PREFL-01	4956	1868	1466	BMW ALPINA D5 S official brochure, July 2017	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_s201707_g.pdf
EU-ALPINA-D5-G31-WAGON-PREFL-01	4956	1868	1466	BMW ALPINA D5 S official brochure, July 2017	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_s201707_g.pdf
EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	4978	1868	1466	BMW ALPINA D5 S official brochure, June 2020	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2020_06_INT/D5_S/epaper/BMW_ALPINA_D5S.pdf
EU-ALPINA-D5-G31-WAGON-FACELIFT-01	4978	1868	1466	BMW ALPINA D5 S official brochure, June 2020	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2020_06_INT/D5_S/epaper/BMW_ALPINA_D5S.pdf
```

## 下一步优先处理

优先闭合 Alpina RLE Roadster、Roadster 3.3、Roadster 4.8 V8，以及 XB7、XD3、XD4；先按底盘、代际和改款节点聚类，再批量关联可复用尺寸组。

推进信号：CONTINUE

[1]: https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_biturbo_saloon_touring.pdf "lay-D5-BiTurbo-2013-UK.indd"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 RLE Roadster、Roadster S 和 Roadster V8 三种独立敞篷车身，分别对应 Z1、E85 与 E52。([UltimateSpecs][1])
* 闭合 XB7 G07 LCI、XD3 F25、XD3 G01 LCI 与 XD4 G02 LCI 四种 SUV 外廓；不同底盘之间不复用尺寸组。([Carsales][2])
* Ktype `142929` 暂未在本轮修改，留待单独解决其跨 G01 改款节点及不同市场三维口径的冲突。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：56
* READY 映射行：68
* PENDING 输入 Ktype：44
* 当前映射引用的已确认尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11736	11736	Convertible	RLE Roadster	Z1	2	EU-ALPINA-RLE-Z1-CONVERTIBLE-01	HIGH	Z1双门Roadster Limited Edition车身。	READY
18046	18046	Convertible	Roadster S	E85	2	EU-ALPINA-ROADSTER-S-E85-CONVERTIBLE-01	MEDIUM	输入排量标注3.3，物理车身对应E85 Roadster S。	READY
16701	16701	Convertible	Roadster V8	E52	2	EU-ALPINA-ROADSTER-V8-E52-CONVERTIBLE-01	HIGH	E52双门Roadster V8车身。	READY
151347	151347	SUV	XB7 LCI	G07	5	EU-ALPINA-XB7-G07-SUV-FACELIFT-01	HIGH	G07改款后五门SUV车身。	READY
100943	100943	SUV	XD3 Bi-Turbo	F25	5	EU-ALPINA-XD3-F25-SUV-01	HIGH	F25五门SUV车身。	READY
147248	147248	SUV	XD3 Bi-Turbo LCI	G01	5	EU-ALPINA-XD3-G01-SUV-FACELIFT-01	HIGH	G01改款后394马力五门SUV车身。	READY
147250	147250	SUV	XD4 Bi-Turbo LCI	G02	5	EU-ALPINA-XD4-G02-SUV-FACELIFT-01	HIGH	G02改款后五门SUV Coupe车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-RLE-Z1-CONVERTIBLE-01	3921	1690	1262	UltimateSpecs Alpina Z1 Roadster Limited Edition RLE specifications	https://www.ultimatespecs.com/car-specs/Alpina/123678/Alpina-Z1-Roadster-Limited-Edition-RLE.html
EU-ALPINA-ROADSTER-S-E85-CONVERTIBLE-01	4091	1781	1299	EncyCARpedia 2003 Alpina Roadster S E85 specifications	https://www.encycarpedia.com/alpina/03-z4-roadster-s-e85
EU-ALPINA-ROADSTER-V8-E52-CONVERTIBLE-01	4400	1830	1317	BMW Z8 Club Alpina Roadster V8 technical data	https://www.bmwz8club.com/en/alpina-roadster-v8/
EU-ALPINA-XB7-G07-SUV-FACELIFT-01	5178	2000	1797	Carsales 2023 Alpina XB7 specifications	https://www.carsales.com.au/research/alpina/xb7/2023/
EU-ALPINA-XD3-F25-SUV-01	4647	1901	1670	Auto-Data Alpina XD3 F25 Bi-Turbo specifications	https://www.auto-data.net/en/alpina-xd3-f25-3.0-350hp-biturbo-18316
EU-ALPINA-XD3-G01-SUV-FACELIFT-01	4715	1897	1665	ALPINA Automobiles Australia XD3 technical data	https://www.alpinaautomobiles.com.au/models/xd3/technical-data/
EU-ALPINA-XD4-G02-SUV-FACELIFT-01	4751	1927	1615	Auto-Data Alpina XD4 G02 LCI specifications	https://www.auto-data.net/en/alpina-xd4-model-2489
```

## 下一步优先处理

1. 单独闭合 Ktype `142929`，解决 G01 改款前后及 `4718 × 1897 × 1655`、`4732 × 1897 × 1665` 两种市场口径。
2. 随后处理 Alpine A110 II、A290、A390，并按普通版、R Ultime 和不同 SUV 版本的实际外廓建立关联。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Alpina/123678/Alpina-Z1-Roadster-Limited-Edition-RLE.html "Alpina Z1 Roadster Limited Edition RLE Specs, Performance, Comparisons"
[2]: https://www.carsales.com.au/research/alpina/xb7/2023/?utm_source=chatgpt.com "Alpina XB7 2023 Pricing & Specifications"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Ktype `142929`。其生产期跨越 G01 的 2021 年改款，已拆为改款前 `4718 × 1897 × 1655 mm` 与改款后 `4715 × 1897 × 1665 mm`；改款后分支复用已存在的 XD3 G01 LCI 尺寸组。
* 闭合 Alpine A110 II GT 与 A110 R Ultime。R Ultime 的专属空气动力外廓达到 `4258 × 1798 × 1234 mm`，不与普通 A110 GT 合并。([Alpine Cars][1])
* A290 的 180 和 220 两种功率版本外廓相同，共用尺寸组。A390 GT 与 GTS 同样共用量产车身尺寸组；A390 高度采用量产用户手册中的空载 `1530 mm`。([Alpine Media][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：63
* READY 映射行：76
* PENDING 输入 Ktype：37
* 当前映射引用的已确认尺寸组：60
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142929_prefl	142929	SUV	XD3	G01	5	EU-ALPINA-XD3-G01-SUV-PREFL-01	HIGH	Ktype跨越2021年改款，改款前车身。	READY
142929_facelift	142929	SUV	XD3 LCI	G01	5	EU-ALPINA-XD3-G01-SUV-FACELIFT-01	HIGH	Ktype跨越2021年改款，改款后车身。	READY
147428	147428	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-GT-01	HIGH	A110 II GT双门车身。	READY
802811	802811	Coupe	A110 II R Ultime		2	EU-ALPINE-A110-II-COUPE-R-ULTIME-01	HIGH	R Ultime专属空气动力外廓。	READY
159584	159584	Hatchback	A290		5	EU-ALPINE-A290-HATCHBACK-01	HIGH	180马力版本沿用A290五门车身。	READY
159585	159585	Hatchback	A290		5	EU-ALPINE-A290-HATCHBACK-01	HIGH	220马力版本沿用A290五门车身。	READY
162475	162475	SUV	A390		5	EU-ALPINE-A390-SUV-01	HIGH	GT版本沿用A390五门Sport Fastback车身。	READY
162476	162476	SUV	A390		5	EU-ALPINE-A390-SUV-01	HIGH	GTS版本沿用A390五门Sport Fastback车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-XD3-G01-SUV-PREFL-01	4718	1897	1655	BMW ALPINA XD3 official brochure, September 2019	https://i.i-sgcm.com/new_cars/cars/12797/brochures/brochure_20210320115459.pdf
EU-ALPINE-A110-II-COUPE-GT-01	4181	1798	1252	Alpine A110 official brochure, April 2022	https://www.alpinecars.com/assets/docs/PL-BrochureAlpineA110_04.2022.pdf
EU-ALPINE-A110-II-COUPE-R-ULTIME-01	4258	1798	1234	Alpine A110 R Ultime official user manual	https://www.user-manual.alpinecars.com/zh-hans/node/1594
EU-ALPINE-A290-HATCHBACK-01	3990	1820	1520	Alpine A290 official launch specifications	https://media.alpinecars.com/alpine-a290-orders-now-being-taken-and-prices-for-france/?lang=eng
EU-ALPINE-A390-SUV-01	4615	1885	1530	Alpine A390 official user manual	https://www.user-manual.alpinecars.com/en/information-about-the-vehicle/dimensions-metres-0
```

## 下一步优先处理

优先闭合 ARO 10、ARO 240–244、ARO Spartana、Artega GT、Asia Motors Hi-Topic 与 Rocsta，按开放式越野车、封闭式越野车、Pickup、Coupé、Bus 分别聚类。

推进信号：CONTINUE

[1]: https://www.alpinecars.com/assets/docs/PL-BrochureAlpineA110_04.2022.pdf?utm_source=chatgpt.com "PL-BrochureAlpineA110_04.2022.pdf"
[2]: https://media.alpinecars.com/alpine-a290-orders-now-being-taken-and-prices-for-france/?lang=eng "Alpine A290: orders now being taken and prices for France - Alpine global media website"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 Artega GT 单一双门 Coupé 外廓，三维为 `4015 × 1882 × 1180 mm`。([汽车目录][1])
* 闭合 Asia Motors Rocsta 1.8 四驱三门封闭式 SUV，采用明确标注不含后视镜宽度的 `3585 × 1688 × 1820 mm`。([Auto Data][2])
* 闭合 ARO Spartana Ktype `127222`。零件目录虽使用 `Pick Up` 标签，但车型边界实际为两门开放式越野 Cabrio；采用早期 1.2 AWD 外廓 `3680 × 1640 × 1660 mm`。([Kmotorshop][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：66
* READY 映射行：79
* PENDING 输入 Ktype：34
* 当前映射引用的已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127222	127222	Convertible	Spartana		2	EU-ARO-SPARTANA-CONVERTIBLE-01	MEDIUM	TecDoc模型标签为Pick Up，实际物理车身为两门开放式越野Cabrio。	READY
10194	10194	Coupe	GT		2	EU-ARTEGA-GT-COUPE-01	HIGH	双门中置发动机Coupé车身。	READY
57222	57222	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-01	HIGH	三门封闭式四驱越野车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ARO-SPARTANA-CONVERTIBLE-01	3680	1640	1660	Automobile-Catalog 1997 ARO Spartana specifications	https://www.automobile-catalog.com/car/1997/1763930/aro_spartana.html
EU-ARTEGA-GT-COUPE-01	4015	1882	1180	Automobile-Catalog 2012 Artega GT specifications	https://www.automobile-catalog.com/car/2012/1582280/artega_gt.html
EU-ASIA-MOTORS-ROCSTA-SUV-01	3585	1688	1820	Automobile-Catalog 1995 Asia Rocsta 1.8 specifications	https://www.automobile-catalog.com/car/1995/3158750/asia_rocsta_1_8_86.html
```

## 下一步优先处理

优先拆解 ARO 240–244 的三个 Ktype，确认每个 Ktype 是否同时覆盖三门 ARO 243 与五门 ARO 244，并处理生产期内 `4140 mm` 至 `4102 mm` 的车长变化；随后闭合 Asia Motors Hi-Topic。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/1582280/artega_gt.html?utm_source=chatgpt.com "2012 Artega GT Specs Review (220.5 kW / 300 PS / 296 hp ..."
[2]: https://www.auto-data.net/en/asia-rocsta-1.8-i-4x4-86hp-2878 "Asia Rocsta 1.8 i 4x4 (86 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.kmotorshop.com/en/article-list/list/car/127222?utm_source=chatgpt.com "Spare parts ARO SPARTANA Pick Up 1,2 AWD"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已闭合 ARO 240–244 的三个 Ktype。输入为封闭式越野车，因此按三门 ARO 243 与五门 ARO 244 拆分；开放式 ARO 240 不纳入映射。([维基百科][1])
* 早期 243/244 车长为 4140 mm，后期缩短为 4102 mm；宽度保持 1775 mm，243 高度为 1980 mm，244 高度为 1880 mm。([汽车目录][2])
* Ktype `11219` 从 1989 年 9 月开始，仅关联后期外廓；`11220` 和 `11221` 的生产期跨越外廓变更节点，分别保留早期和后期分支。([Denso AM][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：69
* READY 映射行：89
* PENDING 输入 Ktype：31
* 当前映射引用的已确认尺寸组：67
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11221_3dr_prefl	11221	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-PREFL-01	MEDIUM	封闭式三门243早期车身。	READY
11221_5dr_prefl	11221	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-PREFL-01	MEDIUM	封闭式五门244早期车身。	READY
11221_3dr_facelift	11221	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11221_5dr_facelift	11221	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
11219_3dr	11219	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11219_5dr	11219	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
11220_3dr_prefl	11220	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-PREFL-01	MEDIUM	封闭式三门243早期车身。	READY
11220_5dr_prefl	11220	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-PREFL-01	MEDIUM	封闭式五门244早期车身。	READY
11220_3dr_facelift	11220	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11220_5dr_facelift	11220	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ARO-24-243-SUV-PREFL-01	4140	1775	1980	Automobile-Catalog ARO 243 early body specifications	https://www.automobile-catalog.com/car/1986/51530/aro_243_d_2_7.html
EU-ARO-24-244-SUV-PREFL-01	4140	1775	1880	Automobile-Catalog 1986 ARO 244 D 2.7 specifications	https://www.automobile-catalog.com/car/1986/1762640/aro_244_d_2_7.html
EU-ARO-24-243-SUV-FACELIFT-01	4102	1775	1980	Automobile-Catalog 1991 ARO 243 D 2.5 specifications	https://www.automobile-catalog.com/car/1991/1763495/aro_243_d_2_5.html
EU-ARO-24-244-SUV-FACELIFT-01	4102	1775	1880	Automobile-Catalog 1991 ARO 244 D 2.5 specifications	https://www.automobile-catalog.com/car/1991/1763555/aro_244_d_2_5.html
```

## 下一步优先处理

优先闭合 ARO 10 Ktype `151161` 与 Asia Motors Hi-Topic Ktype `8038`。ARO 10 需先解决输入开放式车身与目录“Pick Up”标签的边界；Hi-Topic 需确认 AM715/AM725 底盘及可追溯的完整三维。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/ARO_24_Series?utm_source=chatgpt.com "ARO 24 Series"
[2]: https://www.automobile-catalog.com/car/1985/51530/aro_243_d_2_7.html?utm_source=chatgpt.com "1985 ARO 243 D 2.7 (man. 5) (model for Europe ) car ..."
[3]: https://www.denso-am.eu/catalog/pv/11219?utm_source=chatgpt.com "Car parts for ARO 240-244, 2.7 D, 50kW(68ps), L27DA | DENSO"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 闭合 ARO 10 Ktype `151161`，确认对应两门软顶 `ARO 10.1` 开放式越野车身，外廓为 `3835 × 1644 × 1655 mm`，宽度为不含后视镜口径。([汽车目录][1])
* Asia Motors Hi-Topic 已确认属于 `AM 725` 五门车身，但当前可追溯规格页未提供完整三维，本轮暂不创建尺寸组或映射。([Auto Data][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：70
* READY 映射行：90
* PENDING 输入 Ktype：30
* 当前映射引用的已确认尺寸组：68
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151161	151161	Convertible	ARO 10.1	10.1	2	EU-ARO-10-10-1-CONVERTIBLE-01	MEDIUM	两门软顶开放式越野车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ARO-10-10-1-CONVERTIBLE-01	3835	1644	1655	Automobile-Catalog 1989 ARO 10.1 1.4 specifications	https://www.automobile-catalog.com/car/1989/1763270/aro_10_1_1_4.html
```

## 下一步优先处理

优先继续补齐 Asia Motors Hi-Topic AM 725 的完整三维；随后批量处理 Aston Martin DB12、DB6 与 DB7 车身簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/1763270/aro_10_1_1_4.html?utm_source=chatgpt.com "1989 ARO 10.1 1.4 (man. 4) (model for Europe ) car ..."
[2]: https://www.auto-data.net/en/asia-hi-topic-am-725-2.7-d-75hp-2871 "Asia Hi-topic (AM 725) 2.7 D (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 闭合 Aston Martin DB12 Coupé 与 DB12 Volante。两者三维均为 `4725 × 1980 × 1295 mm`，但车顶结构不同，分别建组；`1980 mm` 为官方明确标注的不含后视镜最大后部车宽。([阿斯顿·马丁][1])
* 闭合 DB6 Vantage Coupé 与 DB6 Volante。Ktype `8179`、`8180` 复用同一 Coupé 尺寸组；Volante 独立建组。所用宽度均明确为不含后视镜口径。([汽车目录][2])
* 闭合 DB7 V12 Vantage Coupé 与 3.2 直六 DB7 Volante，二者属于不同动力时期和不同车身外廓。([汽车目录][3])
* Asia Motors Hi-Topic 尚缺可追溯的完整三维，本轮未创建猜测性映射或尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：77
* READY 映射行：97
* PENDING 输入 Ktype：23
* 当前映射引用的已确认尺寸组：74
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154906	154906	Coupe	DB12		2	EU-ASTON-MARTIN-DB12-COUPE-01	HIGH	DB12双门Coupé车身。	READY
155939	155939	Convertible	DB12 Volante		2	EU-ASTON-MARTIN-DB12-VOLANTE-01	HIGH	DB12双门Volante车身。	READY
8179	8179	Coupe	DB6 Vantage		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH	DB6 Vantage双门车身。	READY
8180	8180	Coupe	DB6 Vantage		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH	DB6 Vantage双门车身。	READY
8181	8181	Convertible	DB6 Volante		2	EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	HIGH	DB6双门Volante车身。	READY
12199	12199	Coupe	DB7 Vantage		2	EU-ASTON-MARTIN-DB7-VANTAGE-COUPE-01	HIGH	DB7 V12 Vantage双门车身。	READY
8202	8202	Convertible	DB7 Volante		2	EU-ASTON-MARTIN-DB7-I6-VOLANTE-CONVERTIBLE-01	HIGH	DB7 3.2直六双门Volante车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-DB12-COUPE-01	4725	1980	1295	Aston Martin DB12 official specifications	https://www.astonmartin.com/en/models/db12
EU-ASTON-MARTIN-DB12-VOLANTE-01	4725	1980	1295	Aston Martin DB12 Volante official specifications	https://www.astonmartin.com/en/models/db12-volante
EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	4623	1676	1384	Automobile-Catalog 1968 Aston Martin DB6 Vantage specifications	https://www.automobile-catalog.com/car/1968/34715/aston_martin_db6_vantage.html
EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	4623	1676	1359	Automobile-Catalog 1968 Aston Martin DB6 Volante specifications	https://www.automobile-catalog.com/car/1968/74060/aston_martin_db6_volante.html
EU-ASTON-MARTIN-DB7-VANTAGE-COUPE-01	4666	1830	1238	Automobile-Catalog 2001 Aston Martin DB7 Vantage specifications	https://www.automobile-catalog.com/car/2001/228650/aston_martin_db7_vantage.html
EU-ASTON-MARTIN-DB7-I6-VOLANTE-CONVERTIBLE-01	4646	1830	1265	Automobile-Catalog 1997 Aston Martin DB7 Volante specifications	https://www.automobile-catalog.com/car/1997/228620/aston_martin_db7_volante.html
```

## 下一步优先处理

优先闭合 Aston Martin DB9 Coupé 与 DB9 Volante 的多个 Ktype，按 2004–2012 初期外廓、2012 年改款外廓及 Coupé／Volante 车身批量聚类。

推进信号：CONTINUE

[1]: https://www.astonmartin.com/en-us/models/db12 "DB12 | Super GT | Aston Martin USA"
[2]: https://www.automobile-catalog.com/car/1968/34715/aston_martin_db6_vantage.html?utm_source=chatgpt.com "1968 Aston Martin DB6 Vantage Specs Review (242.5 kW / 330 PS / 325 hp) (for Europe North America )"
[3]: https://www.automobile-catalog.com/car/2001/228650/aston_martin_db7_vantage.html?utm_source=chatgpt.com "2001 Aston Martin DB7 Vantage Specs Review (309 kW / 420 PS / 414 hp) (for Europe North America Australia )"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 已闭合 10 个 Aston Martin DB9 Ktype。
* Ktype `17825` 横跨 2012 年外廓更新，拆分为改款前和 2013MY 后期车身；其余 Ktype 按生产区间直接关联对应车身组。
* DB9 Coupé 与 Volante 分别建组；2004–2012 外廓采用 `4710 × 1875 × 1270 mm`，2013MY 起采用 `4720 × 1905 × 1282 mm`。后期 DB9 的车长和高度由 Aston Martin 官方规格支持，1905 mm 采用不含后视镜车身宽度口径。([汽车目录档案][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：87
* READY 映射行：108
* PENDING 输入 Ktype：13
* 当前映射引用的已确认尺寸组：78
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17825_prefl	17825	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	Ktype覆盖2012年外廓更新前Coupé车身。	READY
17825_facelift	17825	Coupe	DB9 2013MY		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	Ktype覆盖2012年外廓更新后Coupé车身。	READY
34741	34741	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	2008至2012年Coupé车身。	READY
57111	57111	Coupe	DB9 2013MY		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	2012年外廓更新后Coupé车身。	READY
119776	119776	Coupe	DB9 GT		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	DB9 GT沿用后期Coupé外廓。	READY
800914	800914	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	早期DB9 Coupé车身。	READY
116330	116330	Convertible	DB9 Volante 2013MY		2	EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	HIGH	后期DB9 Volante车身。	READY
17826	17826	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	2012年外廓更新前Volante车身。	READY
34743	34743	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	2005至2012年Volante车身。	READY
57112	57112	Convertible	DB9 Volante 2013MY		2	EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	HIGH	2012年外廓更新后Volante车身。	READY
800913	800913	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	早期DB9 Volante车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	4710	1875	1270	Aston Martin DB9 official brochure 2009	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-DB9-2009.pdf
EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	4710	1875	1270	Aston Martin DB9 official brochure 2009; Aston Martins DB9 Volante 2009MY specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-DB9-2009.pdf;https://astonmartins.com/car/db9-volante-my2009/
EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	4720	1905	1282	Aston Martin DB9 13MY official specification; CarsGuide DB9 2014 dimensions	https://astonmartin.blob.core.windows.net/sitefinity/media-centre/Models/Press%20Releases/DB9.pdf;https://www.carsguide.com.au/aston-martin/db9/car-dimensions/2014
EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	4720	1905	1282	Aston Martin DB9 13MY official specification; The Car Guide DB9 Volante 2014 specifications	https://astonmartin.blob.core.windows.net/sitefinity/media-centre/Models/Press%20Releases/DB9.pdf;https://www.guideautoweb.com/en/makes/aston-martin/db9/2014/specifications/volante/
```

## 下一步优先处理

优先闭合 Aston Martin DBS 的经典 DBS Vantage、现代 V12 DBS Coupé／Volante及 770 Ultimate Coupé／Volante六个 Ktype；随后处理 DBX、Lagonda、Rapide和仍缺完整三维的 Hi-Topic。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-DB9-2009.pdf?utm_source=chatgpt.com "Aston-Martin-DB9-2009.pdf"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* 闭合经典 DBS 直六与 DBS V8。两者基础三维均为 `4585 × 1829 × 1327 mm`，宽度明确不含后视镜；DBS V8 具有不同前部外观处理，因此分别建组。([汽车目录][1])
* 闭合 2007–2012 DBS V12 Coupé 与 Volante。官方技术规格对两种车身统一列出 `4721 × 1905 × 1280 mm`，但固定顶与敞篷车身结构不同，分别建组。
* 闭合 DBS 770 Ultimate Coupé 与 Volante。两者具有 770 Ultimate 专属前分流器、马蹄形发动机盖等外部空气动力结构；Coupé 与 Volante 高度分别为 1285 mm 和 1295 mm。([阿斯顿·马丁][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：93
* READY 映射行：114
* PENDING 输入 Ktype：7
* 当前映射引用的已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
153380	153380	Coupe	DBS 770 Ultimate		2	EU-ASTON-MARTIN-DBS-770-ULTIMATE-COUPE-01	HIGH	770 Ultimate专属空气动力Coupé车身。	READY
8182	8182	Coupe	DBS		2	EU-ASTON-MARTIN-DBS-CLASSIC-I6-COUPE-01	HIGH	经典DBS直六双门车身。	READY
123876	123876	Coupe	DBS V8		2	EU-ASTON-MARTIN-DBS-CLASSIC-V8-COUPE-01	HIGH	经典DBS V8双门车身，具有V8前部外观处理。	READY
34756	34756	Coupe	DBS V12		2	EU-ASTON-MARTIN-DBS-V12-COUPE-01	HIGH	现代DBS V12双门Coupé车身。	READY
153381	153381	Convertible	DBS 770 Ultimate Volante		2	EU-ASTON-MARTIN-DBS-770-ULTIMATE-VOLANTE-01	HIGH	770 Ultimate专属空气动力Volante车身。	READY
34766	34766	Convertible	DBS V12 Volante		2	EU-ASTON-MARTIN-DBS-V12-VOLANTE-01	HIGH	现代DBS V12双门Volante车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-DBS-770-ULTIMATE-COUPE-01	4715	1970	1285	Aston Martin DBS 770 Ultimate official brochure; Automobile-Catalog 2023 Aston Martin DBS 770 Ultimate Coupe specifications	https://www.astonmartin.com/en/models/brochures/dbs-770-ultimate-brochure;https://www.automobile-catalog.com/car/2023/3172190/aston_martin_dbs_770_ultimate_coupe.html
EU-ASTON-MARTIN-DBS-CLASSIC-I6-COUPE-01	4585	1829	1327	Automobile-Catalog 1969 Aston Martin DBS specifications	https://www.automobile-catalog.com/car/1969/74165/aston_martin_dbs.html
EU-ASTON-MARTIN-DBS-CLASSIC-V8-COUPE-01	4585	1829	1327	Automobile-Catalog 1971 Aston Martin DBS V8 specifications	https://www.automobile-catalog.com/car/1971/74225/aston_martin_dbs_v8.html
EU-ASTON-MARTIN-DBS-V12-COUPE-01	4721	1905	1280	Aston Martin DBS official brochure	https://astonmartins.com/wp-content/uploads/2013/01/AstonMartin-DBS-Brochure.pdf
EU-ASTON-MARTIN-DBS-770-ULTIMATE-VOLANTE-01	4715	1970	1295	Aston Martin DBS 770 Ultimate official brochure; Automobile-Catalog 2023 Aston Martin DBS 770 Ultimate Volante specifications	https://www.astonmartin.com/en/models/brochures/dbs-770-ultimate-brochure;https://www.automobile-catalog.com/car/2023/3172205/aston_martin_dbs_770_ultimate_volante.html
EU-ASTON-MARTIN-DBS-V12-VOLANTE-01	4721	1905	1280	Aston Martin DBS official brochure	https://astonmartins.com/wp-content/uploads/2013/01/AstonMartin-DBS-Brochure.pdf
```

## 下一步优先处理

闭合剩余 7 个 Ktype：DBX `147148`、`802353`，Lagonda Sedan `8183`，Lagonda Shooting Brake `8184`、`125881`，Rapide `58925`，以及仍缺完整三维的 Asia Motors Hi-Topic `8038`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1969/74165/aston_martin_dbs.html?utm_source=chatgpt.com "1969 Aston Martin DBS Specs Review (210 kW / 286 PS / 282 hp) (for Europe North America Australia )"
[2]: https://www.astonmartin.com/en-us/models/brochures/dbs-770-ultimate-brochure "DBS 770 Ultimate Brochure | Aston Martin USA"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_301-400_ktype_dimension_mapping_final.tsv
- left18448_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 已闭合剩余 7 个 Ktype：`8038`、`147148`、`802353`、`8183`、`8184`、`125881`、`58925`。
* 完成一次轻量机械检查：表头固定、`id` 唯一、尺寸组唯一、全部引用闭合、三维及来源非空。
* 已生成两个指定文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：122
* PENDING：0
* DIMENSION_GROUP：92
* 孤立尺寸组：0
* 未闭合映射引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12515	12515	Coupe	B6 Bi-Turbo (F13)	F13	2	EU-ALPINA-B6-F13-COUPE-PREFL-01	HIGH	F13改款前双门车身。	READY
12517	12517	Convertible	B6 Bi-Turbo (F12)	F12	2	EU-ALPINA-B6-F12-CONVERTIBLE-PREFL-01	HIGH	F12改款前敞篷车身。	READY
113469	113469	Coupe	B6 Bi-Turbo (F13 LCI)	F13	2	EU-ALPINA-B6-F13-COUPE-FACELIFT-01	HIGH	F13改款后双门车身。	READY
113470	113470	Convertible	B6 Bi-Turbo (F12 LCI)	F12	2	EU-ALPINA-B6-F12-CONVERTIBLE-FACELIFT-01	HIGH	F12改款后敞篷车身。	READY
100940	100940	Coupe	B6 Bi-Turbo Gran Coupé (F06)	F06	4	EU-ALPINA-B6-F06-GRAN-COUPE-PREFL-01	HIGH	输入Coupe实际为四门四驱Gran Coupé改款前车身。	READY
113736	113736	Coupe	B6 Bi-Turbo Gran Coupé (F06 LCI)	F06	4	EU-ALPINA-B6-F06-GRAN-COUPE-FACELIFT-01	HIGH	输入Coupe实际为四门四驱Gran Coupé改款后车身。	READY
11737	11737	Sedan	B7 Turbo	E12	4	EU-ALPINA-B7-E12-SEDAN-01	HIGH	E12四门B7 Turbo车身。	READY
11741	11741	Coupe	B7 Turbo Coupé	E24	2	EU-ALPINA-B7-E24-COUPE-PREFL-01	HIGH	早期E24双门车身。	READY
11742	11742	Coupe	B7 Turbo Coupé/1	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	1982年更新后的E24/1双门车身。	READY
11743	11743	Coupe	B7 Turbo Coupé/1 B7/3	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	后期催化发动机版，外廓沿用E24/1。	READY
11738	11738	Sedan	B7 S Turbo	E12	4	EU-ALPINA-B7-E12-SEDAN-01	HIGH	E12四门B7 S Turbo车身。	READY
11739	11739	Sedan	B7 Turbo/1	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	E28四门B7 Turbo/1车身。	READY
11740	11740	Sedan	B7 Turbo/1 B7/3	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	后期催化发动机版，外廓沿用E28。	READY
18045	18045	Sedan	B7 (E65)	E65	4	EU-ALPINA-B7-E65-SEDAN-01	HIGH	E65标准轴距四门车身。	READY
59393_swb	59393	Sedan	B7 Bi-Turbo LCI	F01	4	EU-ALPINA-B7-F01-SEDAN-RWD-01	HIGH	后驱标准轴距F01车身。	READY
59393_lwb	59393	Sedan	B7 Bi-Turbo LCI	F02	4	EU-ALPINA-B7-F02-SEDAN-LWB-01	HIGH	后驱长轴距F02车身。	READY
59394_swb	59394	Sedan	B7 Bi-Turbo LCI	F01	4	EU-ALPINA-B7-F01-SEDAN-AWD-01	HIGH	四驱标准轴距F01车身。	READY
59394_lwb	59394	Sedan	B7 Bi-Turbo LCI	F02	4	EU-ALPINA-B7-F02-SEDAN-LWB-01	HIGH	四驱长轴距F02车身。	READY
126181_prefl	126181	Sedan	B7 Bi-Turbo	G12	4	EU-ALPINA-B7-G12-SEDAN-PREFL-01	HIGH	G12改款前长轴距车身。	READY
126181_facelift	126181	Sedan	B7 Bi-Turbo LCI	G12	4	EU-ALPINA-B7-G12-SEDAN-FACELIFT-01	HIGH	G12改款后长轴距车身。	READY
11679	11679	Sedan	B8 4.6	E36	4	EU-ALPINA-B8-E36-SEDAN-01	HIGH	E36四门车身。	READY
11680	11680	Wagon	B8 4.6 Touring	E36	5	EU-ALPINA-B8-E36-WAGON-01	HIGH	E36五门Touring车身。	READY
11681	11681	Coupe	B8 4.6 Coupé	E36	2	EU-ALPINA-B8-E36-COUPE-01	HIGH	E36双门Coupé车身。	READY
11682	11682	Convertible	B8 4.6 Cabriolet	E36	2	EU-ALPINA-B8-E36-CONVERTIBLE-01	HIGH	E36双门敞篷车身。	READY
143575_prefl	143575	Coupe	B8 Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-PREFL-01	HIGH	G16改款前四门Gran Coupé车身。	READY
143575_facelift	143575	Coupe	B8 Gran Coupé LCI	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-FACELIFT-01	HIGH	G16改款后四门Gran Coupé车身。	READY
801386	801386	Coupe	B8 GT Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-GT-01	HIGH	G16改款后GT专属外部套件车身。	READY
11683	11683	Sedan	B9 3.5	E28	4	EU-ALPINA-B7-E28-SEDAN-01	HIGH	E28四门车身。	READY
11684	11684	Coupe	B9 3.5 Coupé/1	E24/1	2	EU-ALPINA-B7-E24-COUPE-FACELIFT-01	HIGH	E24/1双门车身。	READY
11619	11619	Sedan	C1 2.3	E21	2	EU-ALPINA-B6-E21-SEDAN-01	HIGH	E21双门车身。	READY
11620	11620	Sedan	C1 2.3/1	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-01	HIGH	E30双门车身。	READY
11621_2dr	11621	Sedan	C1 2.5	E30	2	EU-ALPINA-C1-E30-SEDAN-2D-01	HIGH	Ktype覆盖双门车身。	READY
11621_4dr	11621	Sedan	C1 2.5	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖四门车身。	READY
11622_2dr	11622	Sedan	C2 2.5	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖E30双门车身。	READY
11622_4dr	11622	Sedan	C2 2.5	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖E30四门车身。	READY
11624_2dr	11624	Sedan	C2 2.7 C2/1	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖E30双门车身。	READY
11624_4dr	11624	Sedan	C2 2.7 C2/1	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖E30四门车身。	READY
11625_2dr	11625	Sedan	C2 2.7 C2/2	E30	2	EU-ALPINA-B6-E30-SEDAN-2D-02	HIGH	Ktype覆盖催化版E30双门车身。	READY
11625_4dr	11625	Sedan	C2 2.7 C2/2	E30	4	EU-ALPINA-C1-E30-SEDAN-4D-01	HIGH	Ktype覆盖催化版E30四门车身。	READY
11631	11631	Convertible	C2 2.7 Cabriolet	E30	2	EU-ALPINA-C2-E30-CONVERTIBLE-01	HIGH	E30双门敞篷车身。	READY
11630	11630	Sedan	C2 2.7 Allrad	E30	2	EU-ALPINA-C2-E30-SEDAN-2D-AWD-01	HIGH	E30双门四驱车身。	READY
11879	11879	Sedan	D10 Bi-Turbo	E39	4	EU-ALPINA-D10-E39-SEDAN-01	HIGH	E39四门Sedan车身。	READY
13997	13997	Wagon	D10 Bi-Turbo Touring	E39	5	EU-ALPINA-D10-E39-WAGON-01	HIGH	E39五门Touring车身。	READY
50872	50872	Sedan	D3	E90	4	EU-ALPINA-D3-E90-SEDAN-01	HIGH	E90改款前四门车身。	READY
50878	50878	Wagon	D3 Touring	E91	5	EU-ALPINA-D3-E91-WAGON-01	HIGH	E91改款前五门Touring车身。	READY
100944_prefl	100944	Sedan	D3 Bi-Turbo	F30	4	EU-ALPINA-D3-F30-SEDAN-PREFL-01	HIGH	F30改款前四门车身。	READY
100944_facelift	100944	Sedan	D3 Bi-Turbo LCI	F30	4	EU-ALPINA-D3-F30-SEDAN-FACELIFT-01	HIGH	F30改款后四门车身。	READY
100945_prefl	100945	Wagon	D3 Bi-Turbo Touring	F31	5	EU-ALPINA-D3-F31-WAGON-RWD-PREFL-01	HIGH	F31改款前后驱Touring车身。	READY
100945_facelift	100945	Wagon	D3 Bi-Turbo Touring LCI	F31	5	EU-ALPINA-D3-F31-WAGON-RWD-FACELIFT-01	HIGH	F31改款后后驱Touring车身。	READY
100946_prefl	100946	Wagon	D3 Bi-Turbo Touring Allrad	F31	5	EU-ALPINA-D3-F31-WAGON-AWD-PREFL-01	HIGH	F31改款前四驱Touring车身。	READY
100946_facelift	100946	Wagon	D3 Bi-Turbo Touring Allrad LCI	F31	5	EU-ALPINA-D3-F31-WAGON-AWD-FACELIFT-01	HIGH	F31改款后四驱Touring车身。	READY
108075	108075	Coupe	D4 Bi-Turbo	F32	2	EU-ALPINA-D4-F32-COUPE-01	HIGH	F32双门Coupé，改款前后三维一致。	READY
108076_prefl	108076	Convertible	D4 Bi-Turbo Cabriolet	F33	2	EU-ALPINA-D4-F33-CONVERTIBLE-PREFL-01	HIGH	F33改款前双门敞篷车身。	READY
108076_facelift	108076	Convertible	D4 Bi-Turbo Cabriolet LCI	F33	2	EU-ALPINA-D4-F33-CONVERTIBLE-FACELIFT-01	HIGH	F33改款后双门敞篷车身。	READY
151538	151538	Coupe	D4 S Gran Coupé	G26	5	EU-ALPINA-D4-G26-GRAN-COUPE-01	HIGH	输入Coupe对应五门Gran Coupé，改款前后三维一致。	READY
10392	10392	Sedan	D5 Bi-Turbo	F10	4	EU-ALPINA-D5-F10-SEDAN-01	HIGH	F10四门Sedan车身。	READY
128500	128500	Sedan	D5 S	G30	4	EU-ALPINA-D5-G30-SEDAN-PREFL-01	HIGH	G30改款前四门车身。	READY
128505	128505	Wagon	D5 S Touring	G31	5	EU-ALPINA-D5-G31-WAGON-PREFL-01	HIGH	G31改款前五门Touring车身。	READY
142900	142900	Sedan	D5 S LCI	G30	4	EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	HIGH	G30改款后四门车身。	READY
142901	142901	Wagon	D5 S Touring LCI	G31	5	EU-ALPINA-D5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门Touring车身。	READY
142904	142904	Sedan	D5 S Mild-Hybrid LCI	G30	4	EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	HIGH	轻混版本沿用G30改款后车身。	READY
11736	11736	Convertible	RLE Roadster	Z1	2	EU-ALPINA-RLE-Z1-CONVERTIBLE-01	HIGH	Z1双门Roadster Limited Edition车身。	READY
18046	18046	Convertible	Roadster S	E85	2	EU-ALPINA-ROADSTER-S-E85-CONVERTIBLE-01	MEDIUM	输入排量标注3.3，物理车身对应E85 Roadster S。	READY
16701	16701	Convertible	Roadster V8	E52	2	EU-ALPINA-ROADSTER-V8-E52-CONVERTIBLE-01	HIGH	E52双门Roadster V8车身。	READY
151347	151347	SUV	XB7 LCI	G07	5	EU-ALPINA-XB7-G07-SUV-FACELIFT-01	HIGH	G07改款后五门SUV车身。	READY
100943	100943	SUV	XD3 Bi-Turbo	F25	5	EU-ALPINA-XD3-F25-SUV-01	HIGH	F25五门SUV车身。	READY
147248	147248	SUV	XD3 Bi-Turbo LCI	G01	5	EU-ALPINA-XD3-G01-SUV-FACELIFT-01	HIGH	G01改款后394马力五门SUV车身。	READY
142929_prefl	142929	SUV	XD3	G01	5	EU-ALPINA-XD3-G01-SUV-PREFL-01	HIGH	Ktype跨越2021年改款，改款前车身。	READY
142929_facelift	142929	SUV	XD3 LCI	G01	5	EU-ALPINA-XD3-G01-SUV-FACELIFT-01	HIGH	Ktype跨越2021年改款，改款后车身。	READY
147250	147250	SUV	XD4 Bi-Turbo LCI	G02	5	EU-ALPINA-XD4-G02-SUV-FACELIFT-01	HIGH	G02改款后五门SUV Coupe车身。	READY
147428	147428	Coupe	A110 II		2	EU-ALPINE-A110-II-COUPE-GT-01	HIGH	A110 II GT双门车身。	READY
802811	802811	Coupe	A110 II R Ultime		2	EU-ALPINE-A110-II-COUPE-R-ULTIME-01	HIGH	R Ultime专属空气动力外廓。	READY
159584	159584	Hatchback	A290		5	EU-ALPINE-A290-HATCHBACK-01	HIGH	180马力版本沿用A290五门车身。	READY
159585	159585	Hatchback	A290		5	EU-ALPINE-A290-HATCHBACK-01	HIGH	220马力版本沿用A290五门车身。	READY
162475	162475	SUV	A390		5	EU-ALPINE-A390-SUV-01	HIGH	GT版本沿用A390五门Sport Fastback车身。	READY
162476	162476	SUV	A390		5	EU-ALPINE-A390-SUV-01	HIGH	GTS版本沿用A390五门Sport Fastback车身。	READY
151161	151161	Convertible	ARO 10.1	10.1	2	EU-ARO-10-10-1-CONVERTIBLE-01	MEDIUM	两门软顶开放式越野车身。	READY
11221_3dr_prefl	11221	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-PREFL-01	MEDIUM	封闭式三门243早期车身。	READY
11221_5dr_prefl	11221	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-PREFL-01	MEDIUM	封闭式五门244早期车身。	READY
11221_3dr_facelift	11221	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11221_5dr_facelift	11221	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
11219_3dr	11219	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11219_5dr	11219	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
11220_3dr_prefl	11220	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-PREFL-01	MEDIUM	封闭式三门243早期车身。	READY
11220_5dr_prefl	11220	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-PREFL-01	MEDIUM	封闭式五门244早期车身。	READY
11220_3dr_facelift	11220	SUV	ARO 24 Series	243	3	EU-ARO-24-243-SUV-FACELIFT-01	MEDIUM	封闭式三门243后期车身。	READY
11220_5dr_facelift	11220	SUV	ARO 24 Series	244	5	EU-ARO-24-244-SUV-FACELIFT-01	MEDIUM	封闭式五门244后期车身。	READY
127222	127222	Convertible	Spartana		2	EU-ARO-SPARTANA-CONVERTIBLE-01	MEDIUM	TecDoc模型标签为Pick Up，实际物理车身为两门开放式越野Cabrio。	READY
10194	10194	Coupe	GT		2	EU-ARTEGA-GT-COUPE-01	HIGH	双门中置发动机Coupé车身。	READY
8038	8038	MPV	Hi-Topic	AM725	5	EU-ASIA-MOTORS-HI-TOPIC-AM725-MPV-01	MEDIUM	AM725十五座Hi-Topic Bus车身。	READY
57222	57222	SUV	Rocsta		3	EU-ASIA-MOTORS-ROCSTA-SUV-01	HIGH	三门封闭式四驱越野车身。	READY
154906	154906	Coupe	DB12		2	EU-ASTON-MARTIN-DB12-COUPE-01	HIGH	DB12双门Coupé车身。	READY
155939	155939	Convertible	DB12 Volante		2	EU-ASTON-MARTIN-DB12-VOLANTE-01	HIGH	DB12双门Volante车身。	READY
8179	8179	Coupe	DB6 Vantage		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH	DB6 Vantage双门车身。	READY
8180	8180	Coupe	DB6 Vantage		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH	DB6 Vantage双门车身。	READY
8181	8181	Convertible	DB6 Volante		2	EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	HIGH	DB6双门Volante车身。	READY
12199	12199	Coupe	DB7 Vantage		2	EU-ASTON-MARTIN-DB7-VANTAGE-COUPE-01	HIGH	DB7 V12 Vantage双门车身。	READY
8202	8202	Convertible	DB7 Volante		2	EU-ASTON-MARTIN-DB7-I6-VOLANTE-CONVERTIBLE-01	HIGH	DB7 3.2直六双门Volante车身。	READY
17825_prefl	17825	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	Ktype覆盖2012年外廓更新前Coupé车身。	READY
17825_facelift	17825	Coupe	DB9 2013MY		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	Ktype覆盖2012年外廓更新后Coupé车身。	READY
34741	34741	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	2008至2012年Coupé车身。	READY
57111	57111	Coupe	DB9 2013MY		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	2012年外廓更新后Coupé车身。	READY
119776	119776	Coupe	DB9 GT		2	EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	HIGH	DB9 GT沿用后期Coupé外廓。	READY
800914	800914	Coupe	DB9		2	EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	HIGH	早期DB9 Coupé车身。	READY
116330	116330	Convertible	DB9 Volante 2013MY		2	EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	HIGH	后期DB9 Volante车身。	READY
17826	17826	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	2012年外廓更新前Volante车身。	READY
34743	34743	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	2005至2012年Volante车身。	READY
57112	57112	Convertible	DB9 Volante 2013MY		2	EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	HIGH	2012年外廓更新后Volante车身。	READY
800913	800913	Convertible	DB9 Volante		2	EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	HIGH	早期DB9 Volante车身。	READY
153380	153380	Coupe	DBS 770 Ultimate		2	EU-ASTON-MARTIN-DBS-770-ULTIMATE-COUPE-01	HIGH	770 Ultimate专属空气动力Coupé车身。	READY
8182	8182	Coupe	DBS		2	EU-ASTON-MARTIN-DBS-CLASSIC-I6-COUPE-01	HIGH	经典DBS直六双门车身。	READY
123876	123876	Coupe	DBS V8		2	EU-ASTON-MARTIN-DBS-CLASSIC-V8-COUPE-01	HIGH	经典DBS V8双门车身，具有V8前部外观处理。	READY
34756	34756	Coupe	DBS V12		2	EU-ASTON-MARTIN-DBS-V12-COUPE-01	HIGH	现代DBS V12双门Coupé车身。	READY
153381	153381	Convertible	DBS 770 Ultimate Volante		2	EU-ASTON-MARTIN-DBS-770-ULTIMATE-VOLANTE-01	HIGH	770 Ultimate专属空气动力Volante车身。	READY
34766	34766	Convertible	DBS V12 Volante		2	EU-ASTON-MARTIN-DBS-V12-VOLANTE-01	HIGH	现代DBS V12双门Volante车身。	READY
147148	147148	SUV	DBX		5	EU-ASTON-MARTIN-DBX-SUV-01	HIGH	标准DBX五门SUV车身。	READY
802353	802353	SUV	DBX S		5	EU-ASTON-MARTIN-DBX-S-SUV-01	HIGH	DBX S专属前分流器、侧裙、后扩散器及四出排气外廓。	READY
8183_prefl	8183	Sedan	Lagonda Series 2–3		4	EU-ASTON-MARTIN-LAGONDA-S2-S3-SEDAN-01	HIGH	Series 2–3楔形四门车身。	READY
8183_facelift	8183	Sedan	Lagonda Series 4		4	EU-ASTON-MARTIN-LAGONDA-S4-SEDAN-01	HIGH	1987年圆角化前后部改款车身。	READY
8184	8184	Wagon	Lagonda Series 3 Shooting Brake		5	EU-ASTON-MARTIN-LAGONDA-S3-SHOOTING-BRAKE-01	MEDIUM	目录宽泛生产期对应1987 Series 3一体式Shooting Brake外廓。	READY
125881	125881	Wagon	Lagonda Series 3 Shooting Brake		5	EU-ASTON-MARTIN-LAGONDA-S3-SHOOTING-BRAKE-01	HIGH	1987 Series 3五门Shooting Brake车身。	READY
58925	58925	Hatchback	Rapide S		5	EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	HIGH	五门Rapide S掀背车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B6-F13-COUPE-PREFL-01	4894	1894	1377	BMW ALPINA B6 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b6_biturbo_coupe_convertible.pdf
EU-ALPINA-B6-F12-CONVERTIBLE-PREFL-01	4894	1894	1373	BMW ALPINA B6 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b6_biturbo_coupe_convertible.pdf
EU-ALPINA-B6-F13-COUPE-FACELIFT-01	4894	1894	1375	BMW ALPINA B6 Bi-Turbo official brochure, March 2017	https://i.i-sgcm.com/new_cars/cars/11863/brochures/brochure_20180129033803.pdf
EU-ALPINA-B6-F12-CONVERTIBLE-FACELIFT-01	4894	1894	1371	BMW ALPINA B6 Bi-Turbo official brochure, March 2017	https://i.i-sgcm.com/new_cars/cars/11863/brochures/brochure_20180129033803.pdf
EU-ALPINA-B6-F06-GRAN-COUPE-PREFL-01	5007	1894	1392	Car and Driver 2015 BMW Alpina B6 xDrive Gran Coupe test	https://www.caranddriver.com/reviews/a15107156/2015-bmw-alpina-b6-gran-coupe-test-review/
EU-ALPINA-B6-F06-GRAN-COUPE-FACELIFT-01	5007	1894	1398	BMW Group Canada ALPINA B6 2018MY Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0269584EN/391264
EU-ALPINA-B7-E12-SEDAN-01	4620	1690	1405	EncyCARpedia Alpina B7 Turbo E12 specifications; UltimateSpecs Alpina B7 S Turbo E12 specifications	https://www.encycarpedia.com/alpina/78-b7-turbo-e12-saloon;https://www.ultimatespecs.com/car-specs/Alpina/119631/Alpina-E12-5-Series-B7-S-Turbo.html
EU-ALPINA-B7-E24-COUPE-PREFL-01	4755	1725	1345	UltimateSpecs Alpina E24 B7 Turbo Coupé specifications	https://www.ultimatespecs.com/car-specs/Alpina/123619/Alpina-E24-6-Series-B7-Turbo-Coupe.html
EU-ALPINA-B7-E24-COUPE-FACELIFT-01	4755	1725	1345	UltimateSpecs Alpina E24/1 B7 Turbo Coupé specifications	https://www.ultimatespecs.com/car-specs/Alpina/123622/Alpina-E24-1-6-Series-B7-Turbo-Coupe.html
EU-ALPINA-B7-E28-SEDAN-01	4620	1700	1395	UltimateSpecs Alpina E28 B7 Turbo/1 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119627/Alpina-E28-5-Series-B7-Turbo-1-300HP.html
EU-ALPINA-B7-E65-SEDAN-01	5029	1902	1477	UltimateSpecs Alpina E65 B7 specifications	https://www.ultimatespecs.com/car-specs/Alpina/M11388/E65-7-Series
EU-ALPINA-B7-F01-SEDAN-RWD-01	5092	1902	1485	BMW ALPINA B7 Bi-Turbo official brochure, April 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_b7_biturbo_saloon.pdf
EU-ALPINA-B7-F02-SEDAN-LWB-01	5232	1902	1484	Automobile-Catalog 2014 Alpina B7 Bi-Turbo L specifications; Edmunds 2013 BMW ALPINA B7 LWB xDrive specifications	https://www.automobile-catalog.com/car/2014/1762190/alpina_b7_biturbo_l.html;https://www.edmunds.com/bmw/alpina-b7/2013/st-401657909/features-specs/
EU-ALPINA-B7-F01-SEDAN-AWD-01	5093	1902	1491	Edmunds 2014 BMW ALPINA B7 SWB xDrive specifications	https://www.edmunds.com/bmw/alpina-b7/2014/st-200491673/features-specs/
EU-ALPINA-B7-G12-SEDAN-PREFL-01	5250	1902	1491	BMW Group Canada 2018 ALPINA B7 Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0276855EN/399017
EU-ALPINA-B7-G12-SEDAN-FACELIFT-01	5268	1902	1491	Goo-net BMW ALPINA B7 Bi-Turbo Limousine Allrad catalogue	https://www.goo-net-exchange.com/catalog/BMW_ALPINA__B7/10142951/
EU-ALPINA-B8-E36-SEDAN-01	4433	1698	1373	Auto-Data Alpina B8 E36 4.6 Sedan specifications	https://www.auto-data.net/en/alpina-b8-e36-4.6-i-v8-32v-333hp-1643
EU-ALPINA-B8-E36-WAGON-01	4433	1698	1371	UltimateSpecs Alpina E36 Touring B8 4.6 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119039/Alpina-E36-3-Series-Touring-B8-46.html
EU-ALPINA-B8-E36-COUPE-01	4433	1710	1346	Auto-Data Alpina B8 E36 4.6 Coupe specifications	https://www.auto-data.net/en/alpina-b8-coupe-e36-4.6-i-v8-24v-333hp-1646
EU-ALPINA-B8-E36-CONVERTIBLE-01	4433	1710	1328	UltimateSpecs Alpina E36 Cabriolet B8 4.6 specifications	https://www.ultimatespecs.com/car-specs/Alpina/119037/Alpina-E36-3-Series-Cabriolet-B8-46.html
EU-ALPINA-B8-G16-GRAN-COUPE-PREFL-01	5092	1932	1423	BMW Group Canada MY22 ALPINA B8 Gran Coupé Product Guide	https://www.press.bmwgroup.com/canada/article/attachment/T0338596EN/486423
EU-ALPINA-B8-G16-GRAN-COUPE-FACELIFT-01	5092	1932	1428	ALPINA BMW ALPINA B8 official brochure, February 2022	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2022_02_DE/B8/index.html
EU-ALPINA-B8-G16-GRAN-COUPE-GT-01	5092	1932	1428	ALPINA BMW ALPINA B8 GT official technical data	https://b8gt.alpina.de/wp-content/uploads/2025/01/BMW_ALPINA_B8_GT_Technical_Data.pdf
EU-ALPINA-B6-E21-SEDAN-01	4355	1610	1360	Automobile-Catalog 1982 Alpina B6 2.8 specifications	https://www.automobile-catalog.com/car/1982/170345/alpina_b6_2_8.html
EU-ALPINA-B6-E30-SEDAN-2D-01	4325	1645	1350	Automobile-Catalog 1984 Alpina B6 2.8 specifications	https://www.automobile-catalog.com/car/1984/286460/alpina_b6_2_8.html
EU-ALPINA-C1-E30-SEDAN-2D-01	4325	1645	1380	UltimateSpecs Alpina E30 C1 2.5 2-door specifications	https://www.ultimatespecs.com/car-specs/Alpina/123088/Alpina-E30-3-Series-C1-25-2-door.html
EU-ALPINA-C1-E30-SEDAN-4D-01	4325	1645	1380	UltimateSpecs Alpina E30 C1 2.5 4-door specifications	https://www.ultimatespecs.com/car-specs/Alpina/123089/Alpina-E30-3-Series-C1-25-4-door.html
EU-ALPINA-B6-E30-SEDAN-2D-02	4325	1645	1355	Automobile-Catalog 1988 Alpina B6 3.5 specifications	https://www.automobile-catalog.com/car/1988/1186190/alpina_b6_3_5.html
EU-ALPINA-C2-E30-CONVERTIBLE-01	4325	1645	1345	UltimateSpecs Alpina E30 Convertible C2 2.7 specifications	https://www.ultimatespecs.com/car-specs/Alpina/123092/Alpina-E30-3-Series-Convertible-C2-27-210HP.html
EU-ALPINA-C2-E30-SEDAN-2D-AWD-01	4325	1662	1380	UltimateSpecs Alpina E30 C2 2.7 2-door Allrad specifications	https://www.ultimatespecs.com/car-specs/Alpina/123406/Alpina-E30-3-Series-C2-27-2-door-Allrad.html
EU-ALPINA-D10-E39-SEDAN-01	4775	1800	1415	Automobile-Catalog 2001 Alpina D10 Biturbo specifications	https://www.automobile-catalog.com/car/2001/287735/alpina_d10_biturbo.html
EU-ALPINA-D10-E39-WAGON-01	4805	1800	1420	Automobile-Catalog 2001 Alpina D10 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2001/287765/alpina_d10_biturbo_touring.html
EU-ALPINA-D3-E90-SEDAN-01	4520	1817	1413	Automobile-Catalog 2005 Alpina D3 specifications	https://www.automobile-catalog.com/car/2005/288515/alpina_d3.html
EU-ALPINA-D3-E91-WAGON-01	4520	1817	1418	Automobile-Catalog 2007 Alpina D3 Touring specifications	https://www.automobile-catalog.com/car/2007/288530/alpina_d3_touring.html
EU-ALPINA-D3-F30-SEDAN-PREFL-01	4628	1811	1428	Automobile-Catalog 2014 Alpina D3 Biturbo Limousine specifications	https://www.automobile-catalog.com/car/2014/1953200/alpina_d3_biturbo_limousine.html
EU-ALPINA-D3-F30-SEDAN-FACELIFT-01	4632	1811	1428	Automobile-Catalog 2016 Alpina D3 Biturbo Limousine specifications	https://www.automobile-catalog.com/car/2016/2501780/alpina_d3_biturbo_limousine.html
EU-ALPINA-D3-F31-WAGON-RWD-PREFL-01	4628	1811	1428	Automobile-Catalog 2014 Alpina D3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2014/1953215/alpina_d3_biturbo_touring.html
EU-ALPINA-D3-F31-WAGON-RWD-FACELIFT-01	4632	1811	1428	Automobile-Catalog 2016 Alpina D3 Biturbo Touring specifications	https://www.automobile-catalog.com/car/2016/2501825/alpina_d3_biturbo_touring.html
EU-ALPINA-D3-F31-WAGON-AWD-PREFL-01	4628	1811	1431	Automobile-Catalog 2014 Alpina D3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2014/1953230/alpina_d3_biturbo_touring_allrad.html
EU-ALPINA-D3-F31-WAGON-AWD-FACELIFT-01	4632	1811	1431	Automobile-Catalog 2016 Alpina D3 Biturbo Touring Allrad specifications	https://www.automobile-catalog.com/car/2016/2501855/alpina_d3_biturbo_touring_allrad.html
EU-ALPINA-D4-F32-COUPE-01	4640	1825	1382	Auto-Data Alpina D4 Coupe F32 specifications; Auto-Data Alpina D4 Coupe F32 facelift specifications	https://www.auto-data.net/en/alpina-d4-coupe-f32-3.0d-350hp-switch-tronic-24156;https://www.auto-data.net/en/alpina-d4-coupe-f32-facelift-2017-3.0d-350hp-switch-tronic-37428
EU-ALPINA-D4-F33-CONVERTIBLE-PREFL-01	4640	1825	1382	Auto-Data Alpina D4 Cabrio F33 specifications	https://www.auto-data.net/en/alpina-d4-cabrio-f33-3.0d-350hp-switch-tronic-24225
EU-ALPINA-D4-F33-CONVERTIBLE-FACELIFT-01	4640	1825	1378	Auto-Data Alpina D4 Cabrio F33 facelift specifications	https://www.auto-data.net/en/alpina-d4-cabrio-f33-facelift-2017-3.0d-350hp-switch-tronic-37429
EU-ALPINA-D4-G26-GRAN-COUPE-01	4792	1850	1440	BMW ALPINA D4 S Gran Coupé official brochure; Auto-Data Alpina D4 Gran Coupe G26 facelift specifications	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2022_06_INT/D4_S/epaper/ausgabe.pdf;https://www.auto-data.net/en/alpina-d4-gran-coupe-g26-facelift-2024-s-3.0-355hp-mild-hybrid-awd-switch-tronic-53137
EU-ALPINA-D5-F10-SEDAN-01	4905	1860	1469	BMW ALPINA D5 Bi-Turbo official brochure, March 2013	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_biturbo_saloon_touring.pdf
EU-ALPINA-D5-G30-SEDAN-PREFL-01	4956	1868	1466	BMW ALPINA D5 S official brochure, July 2017	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_s201707_g.pdf
EU-ALPINA-D5-G31-WAGON-PREFL-01	4956	1868	1466	BMW ALPINA D5 S official brochure, July 2017	https://blog.le-parnass.com/catalogue_pdf/bmw_alpina_d5_s201707_g.pdf
EU-ALPINA-D5-G30-SEDAN-FACELIFT-01	4978	1868	1466	BMW ALPINA D5 S official brochure, June 2020	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2020_06_INT/D5_S/epaper/BMW_ALPINA_D5S.pdf
EU-ALPINA-D5-G31-WAGON-FACELIFT-01	4978	1868	1466	BMW ALPINA D5 S official brochure, June 2020	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2020_06_INT/D5_S/epaper/BMW_ALPINA_D5S.pdf
EU-ALPINA-RLE-Z1-CONVERTIBLE-01	3921	1690	1262	UltimateSpecs Alpina Z1 Roadster Limited Edition RLE specifications	https://www.ultimatespecs.com/car-specs/Alpina/123678/Alpina-Z1-Roadster-Limited-Edition-RLE.html
EU-ALPINA-ROADSTER-S-E85-CONVERTIBLE-01	4091	1781	1299	EncyCARpedia 2003 Alpina Roadster S E85 specifications	https://www.encycarpedia.com/alpina/03-z4-roadster-s-e85
EU-ALPINA-ROADSTER-V8-E52-CONVERTIBLE-01	4400	1830	1317	BMW Z8 Club Alpina Roadster V8 technical data	https://www.bmwz8club.com/en/alpina-roadster-v8/
EU-ALPINA-XB7-G07-SUV-FACELIFT-01	5178	2000	1797	Carsales 2023 Alpina XB7 specifications	https://www.carsales.com.au/research/alpina/xb7/2023/
EU-ALPINA-XD3-F25-SUV-01	4647	1901	1670	Auto-Data Alpina XD3 F25 Bi-Turbo specifications	https://www.auto-data.net/en/alpina-xd3-f25-3.0-350hp-biturbo-18316
EU-ALPINA-XD3-G01-SUV-FACELIFT-01	4715	1897	1665	ALPINA Automobiles Australia XD3 technical data	https://www.alpinaautomobiles.com.au/models/xd3/technical-data/
EU-ALPINA-XD3-G01-SUV-PREFL-01	4718	1897	1655	BMW ALPINA XD3 official brochure, September 2019	https://i.i-sgcm.com/new_cars/cars/12797/brochures/brochure_20210320115459.pdf
EU-ALPINA-XD4-G02-SUV-FACELIFT-01	4751	1927	1615	Auto-Data Alpina XD4 G02 LCI specifications	https://www.auto-data.net/en/alpina-xd4-model-2489
EU-ALPINE-A110-II-COUPE-GT-01	4181	1798	1252	Alpine A110 official brochure, April 2022	https://www.alpinecars.com/assets/docs/PL-BrochureAlpineA110_04.2022.pdf
EU-ALPINE-A110-II-COUPE-R-ULTIME-01	4258	1798	1234	Alpine A110 R Ultime official user manual	https://www.user-manual.alpinecars.com/zh-hans/node/1594
EU-ALPINE-A290-HATCHBACK-01	3990	1820	1520	Alpine A290 official launch specifications	https://media.alpinecars.com/alpine-a290-orders-now-being-taken-and-prices-for-france/?lang=eng
EU-ALPINE-A390-SUV-01	4615	1885	1530	Alpine A390 official user manual	https://www.user-manual.alpinecars.com/en/information-about-the-vehicle/dimensions-metres-0
EU-ARO-10-10-1-CONVERTIBLE-01	3835	1644	1655	Automobile-Catalog 1989 ARO 10.1 1.4 specifications	https://www.automobile-catalog.com/car/1989/1763270/aro_10_1_1_4.html
EU-ARO-24-243-SUV-PREFL-01	4140	1775	1980	Automobile-Catalog ARO 243 early body specifications	https://www.automobile-catalog.com/car/1986/51530/aro_243_d_2_7.html
EU-ARO-24-244-SUV-PREFL-01	4140	1775	1880	Automobile-Catalog 1986 ARO 244 D 2.7 specifications	https://www.automobile-catalog.com/car/1986/1762640/aro_244_d_2_7.html
EU-ARO-24-243-SUV-FACELIFT-01	4102	1775	1980	Automobile-Catalog 1991 ARO 243 D 2.5 specifications	https://www.automobile-catalog.com/car/1991/1763495/aro_243_d_2_5.html
EU-ARO-24-244-SUV-FACELIFT-01	4102	1775	1880	Automobile-Catalog 1991 ARO 244 D 2.5 specifications	https://www.automobile-catalog.com/car/1991/1763555/aro_244_d_2_5.html
EU-ARO-SPARTANA-CONVERTIBLE-01	3680	1640	1660	Automobile-Catalog 1997 ARO Spartana specifications	https://www.automobile-catalog.com/car/1997/1763930/aro_spartana.html
EU-ARTEGA-GT-COUPE-01	4015	1882	1180	Automobile-Catalog 2012 Artega GT specifications	https://www.automobile-catalog.com/car/2012/1582280/artega_gt.html
EU-ASIA-MOTORS-HI-TOPIC-AM725-MPV-01	5260	1690	2040	iCarros Asia Hi-Topic DLX 2.7 1993–1997 specifications	https://www.icarros.com.br/catalogo-zero-km/marcas/asia/hi-topic/dlx-2.7-1993-1997
EU-ASIA-MOTORS-ROCSTA-SUV-01	3585	1688	1820	Automobile-Catalog 1995 Asia Rocsta 1.8 specifications	https://www.automobile-catalog.com/car/1995/3158750/asia_rocsta_1_8_86.html
EU-ASTON-MARTIN-DB12-COUPE-01	4725	1980	1295	Aston Martin DB12 official specifications	https://www.astonmartin.com/en/models/db12
EU-ASTON-MARTIN-DB12-VOLANTE-01	4725	1980	1295	Aston Martin DB12 Volante official specifications	https://www.astonmartin.com/en/models/db12-volante
EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	4623	1676	1384	Automobile-Catalog 1968 Aston Martin DB6 Vantage specifications	https://www.automobile-catalog.com/car/1968/34715/aston_martin_db6_vantage.html
EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	4623	1676	1359	Automobile-Catalog 1968 Aston Martin DB6 Volante specifications	https://www.automobile-catalog.com/car/1968/74060/aston_martin_db6_volante.html
EU-ASTON-MARTIN-DB7-VANTAGE-COUPE-01	4666	1830	1238	Automobile-Catalog 2001 Aston Martin DB7 Vantage specifications	https://www.automobile-catalog.com/car/2001/228650/aston_martin_db7_vantage.html
EU-ASTON-MARTIN-DB7-I6-VOLANTE-CONVERTIBLE-01	4646	1830	1265	Automobile-Catalog 1997 Aston Martin DB7 Volante specifications	https://www.automobile-catalog.com/car/1997/228620/aston_martin_db7_volante.html
EU-ASTON-MARTIN-DB9-COUPE-PREFL-01	4710	1875	1270	Aston Martin DB9 official brochure 2009	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-DB9-2009.pdf
EU-ASTON-MARTIN-DB9-COUPE-FACELIFT-01	4720	1905	1282	Aston Martin DB9 13MY official specification; CarsGuide DB9 2014 dimensions	https://astonmartin.blob.core.windows.net/sitefinity/media-centre/Models/Press%20Releases/DB9.pdf;https://www.carsguide.com.au/aston-martin/db9/car-dimensions/2014
EU-ASTON-MARTIN-DB9-VOLANTE-FACELIFT-01	4720	1905	1282	Aston Martin DB9 13MY official specification; The Car Guide DB9 Volante 2014 specifications	https://astonmartin.blob.core.windows.net/sitefinity/media-centre/Models/Press%20Releases/DB9.pdf;https://www.guideautoweb.com/en/makes/aston-martin/db9/2014/specifications/volante/
EU-ASTON-MARTIN-DB9-VOLANTE-PREFL-01	4710	1875	1270	Aston Martin DB9 official brochure 2009; Aston Martins DB9 Volante 2009MY specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-DB9-2009.pdf;https://astonmartins.com/car/db9-volante-my2009/
EU-ASTON-MARTIN-DBS-770-ULTIMATE-COUPE-01	4715	1970	1285	Aston Martin DBS 770 Ultimate official brochure; Automobile-Catalog 2023 Aston Martin DBS 770 Ultimate Coupe specifications	https://www.astonmartin.com/en/models/brochures/dbs-770-ultimate-brochure;https://www.automobile-catalog.com/car/2023/3172190/aston_martin_dbs_770_ultimate_coupe.html
EU-ASTON-MARTIN-DBS-CLASSIC-I6-COUPE-01	4585	1829	1327	Automobile-Catalog 1969 Aston Martin DBS specifications	https://www.automobile-catalog.com/car/1969/74165/aston_martin_dbs.html
EU-ASTON-MARTIN-DBS-CLASSIC-V8-COUPE-01	4585	1829	1327	Automobile-Catalog 1971 Aston Martin DBS V8 specifications	https://www.automobile-catalog.com/car/1971/74225/aston_martin_dbs_v8.html
EU-ASTON-MARTIN-DBS-V12-COUPE-01	4721	1905	1280	Aston Martin DBS official brochure	https://astonmartins.com/wp-content/uploads/2013/01/AstonMartin-DBS-Brochure.pdf
EU-ASTON-MARTIN-DBS-770-ULTIMATE-VOLANTE-01	4715	1970	1295	Aston Martin DBS 770 Ultimate official brochure; Automobile-Catalog 2023 Aston Martin DBS 770 Ultimate Volante specifications	https://www.astonmartin.com/en/models/brochures/dbs-770-ultimate-brochure;https://www.automobile-catalog.com/car/2023/3172205/aston_martin_dbs_770_ultimate_volante.html
EU-ASTON-MARTIN-DBS-V12-VOLANTE-01	4721	1905	1280	Aston Martin DBS official brochure	https://astonmartins.com/wp-content/uploads/2013/01/AstonMartin-DBS-Brochure.pdf
EU-ASTON-MARTIN-DBX-SUV-01	5039	1998	1680	Auto-Data Aston Martin DBX specifications	https://www.auto-data.net/en/aston-martin-dbx-model-2759
EU-ASTON-MARTIN-DBX-S-SUV-01	5039	1998	1680	Aston Martin DBX S official specifications; Goo-net Aston Martin DBX S catalogue	https://www.astonmartin.com/en/models/dbx-s;https://www.goo-net-exchange.com/catalog/ASTON_MARTIN__DBX/10158026/
EU-ASTON-MARTIN-LAGONDA-S2-S3-SEDAN-01	5283	1816	1302	Aston Martin Lagonda official heritage specifications	https://www.astonmartin.com/en/models/past-models/lagonda
EU-ASTON-MARTIN-LAGONDA-S4-SEDAN-01	5283	1816	1302	Aston Martin Lagonda official heritage specifications; UltimateSpecs Lagonda Series 4 specifications	https://www.astonmartin.com/en/models/past-models/lagonda;https://www.ultimatespecs.com/car-specs/Aston-Martin/375/Aston-Martin-Lagonda-Series-4.html
EU-ASTON-MARTIN-LAGONDA-S3-SHOOTING-BRAKE-01	5283	1816	1302	Aston Martins Lagonda V8 Shooting Brake by Roos; Auta5P Aston Martin Lagonda Shooting Brake specifications	https://astonmartins.com/car/lagonda-v8-shooting-brake-by-roos/;https://auta5p.eu/lang/en/katalog/auto.php?idf=Aston-Martin-Lagonda-Shooting-Brake-19998
EU-ASTON-MARTIN-RAPIDE-S-HATCHBACK-01	5019	1929	1360	Aston Martin Rapide S official brochure 2013	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-Rapide-S-2013.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（489 行）
- 累计尺寸组：dimension_groups_final.tsv（242 行）

